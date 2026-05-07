"""Worker Agent — ReAct-based single-LLM documentation agent.

Receives a WorkerTask from ManagerAgent and runs a multi-turn
Thought / Action / Observation loop until a Finish action is reached.
"""
from __future__ import annotations

import ast
import difflib
import json
import os
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import BaseAgent
from .llm.factory import LLMFactory
try:
    from ..memory.repo_memory import RepoMemory
    from ..agent.tool.perplexity_api import PerplexityAPI
    from ..dependency_analyzer.ast_parser import ImportCollector
    from ..dependency_analyzer.language_extensions import CODE_EXTENSIONS
except ImportError:
    from memory.repo_memory import RepoMemory
    from agent.tool.perplexity_api import PerplexityAPI
    from dependency_analyzer.ast_parser import ImportCollector
    from dependency_analyzer.language_extensions import CODE_EXTENSIONS
    
from print_color import print

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------


class TaskType(Enum):
    COMPONENT = "COMPONENT"
    MODULE    = "MODULE"
    REPO      = "REPO"


# ---------------------------------------------------------------------------
# Verify constants
# ---------------------------------------------------------------------------

VERIFY_WEIGHTS: Dict[str, float] = {
    "INTERNAL": 1.00, # consistency and completeness based on internal codebase information
    "CROSS" : 1.00 # cross conflict
}
VERIFY_THRESHOLD: float = 0.90  # minimum weighted score to pass


@dataclass
class VerifyResult:
    """Structured result returned by WorkerExecutor.verify_tool()."""
    passed:     bool
    confidence: float          # weighted score (0-1)
    observation: str           # human-readable summary for the ReAct loop
    scores: Optional[Dict[str, float]] = None       # {CONSISTENCY, COMPLETENESS, HELPFULNESS}
    weighted_avg: Optional[float] = None             # weighted average of the 3 scores
    conflict_score: Optional[float] = None           # 1.0 = no conflict, 0.0 = all conflict


@dataclass
class WorkerTask:
    """Describes a single documentation unit for WorkerAgent.

    Attributes:
        type: One of COMPONENT, MODULE, or REPO.
        target: component_id for COMPONENT tasks, module_path for MODULE,
                repo_path for REPO.
        file_path: Repo-relative path to the source file (COMPONENT only),
                   e.g. ``"src/agent/reader.py"``.
        file_paths: Repo-relative paths of all source files belonging to this
                    module (MODULE only). Used to build the module tree without
                    re-scanning the filesystem.
        component_ids: Authoritative list of component IDs belonging to this
                       module (MODULE only). Passed from ManagerAgent so
                       WorkerAgent does not need to recompute membership.
        module_paths: Root module paths in the repo (REPO only).
        child_module_paths: Direct child module paths of this module (MODULE only).
    """
    type: TaskType
    target: str
    file_path: str = ""
    file_paths: List[str] = field(default_factory=list)
    component_ids: List[str] = field(default_factory=list)
    module_paths: List[str] = field(default_factory=list)
    child_module_paths: List[str] = field(default_factory=list)
    # Pre-populated by ManagerAgent for COMPONENT tasks
    source_code: Optional[str] = None
    imports: Optional[str] = None


# ---------------------------------------------------------------------------
# System prompt template (COMPONENT task)
# ---------------------------------------------------------------------------

# task : component
# type : function, method, class


WORKER_AGENT_SYSTEM_PROMPT_NOTHINK = """\
<ROLE>
You are an expert code documentation worker agent operating on a software repository. Your goal is to generate a high-quality documentation that are both complete and helpful for developers. 
</ROLE>

<OBJECTIVES>
Generate documentation sufficient for a developer to reconstruct a functional implementation from scratch using only this documentation.
Each level must answer the following questions:
- Repository-level : "What does this system do, and how are its parts organized?"                                                                                        
- Module-level : "What does this module do, and how do its components interact?"                                                                                     
- Component-level: "How do I implement this function/class/method correctly?"
</OBJECTIVES>

<DOCUMENTATION_STRUCTURE>
Generate documentation following this structure depending on the target level:
1. REPO : Repository-level Documentation:
    - Brief introduction and purpose of the overall system
    - Architecture overview with diagrams
    - High-level functionality of each sub-module including references to its documentation file
    - Link to other module documentation instead of duplicating information
    - Do not duplicate content covered in MODULE or COMPONENT docs. Focus on the big picture, not implementation details

2. MODULE: Module-level Documentation:
    - Explanation of the module's role within the system and its internal design, so a developer can understand *how* its components fit together before reading individual component details
    - Responsibility and boundaries of the module
    - List of core components with a one-line description each
    - Component interaction diagram or call flow (if non-trivial)
    - Key data structures and state shared across components
    - Links to component-level documentation for each component
   
3. COMPONENT: Component-level Documentation:
    - Providing enough detail to *reimplement* the function, method, or class correctly — covering inputs, outputs, behavior, edge cases, and constraints
    - Summary of what the component does and why it exists (not how it works)
</DOCUMENTATION_STRUCTURE>

<WORKFLOW>
1. You will first receive a sub-task, which includes the type of task (COMPONENT, MODULE, or REPO), the target component/module/repo to document, and other relevant information.
2. Analyze the provided code components or module structure, explore the not given dependencies between the components if needed.
3. For COMPONENT tasks, generate the documentation for the specific component, and save the documentation in memory with the name of `component_id`.
4. For MODULE tasks, synthesize the documentations of sub-components and generate the module-level documentation, and save the documentation in memory with the name of `module_id`.
5. For REPO tasks, synthesize the documentations of all modules and generate the repository-level documentation, and save the documentation in memory with the name of `repo_id`.
6. For each task, you perform action-observation loops to iteratively improve the documentation until it passes verification, then save the final documentation to memory and return.
    - At every turn, you MUST follow this structure:
        Action: Choose exactly one action from the list below and provide the necessary input.
        (Observation will be provided after each action to inform your next step. Do NOT generate this yourself.)
    - Repeat until all target component is fully documented and verified, then call Finish to save and exit.
    - The required sequence of actions is typically: Read → Write → Verify → (optional Read or Write) → Finish
</WORKFLOW>

<AVAILABLE_TOOLS>
For each turn, take exactly one of the four actions below:
- `READ`: Request specific information about the code component or module structure.
- `WRITE`: Generate documentation for the target component/module/repo based on the provided information and context.
- `VERIFY`: Evaluate the quality of the generated documentation using an external evaluation tool. Use the feedback to iteratively improve the documentation if needed.
- `FINISH`: Save the final documentation to memory and end the task. Only call this after VERIFY passes.
</AVAILABLE_TOOLS> 

<DETAILED_TOOL_USAGE>
1. READ: If you think more information is needed to generate high-quality documentation of the target component, use this action to request relevant information.

- You should analyze the current code and context, and explain what additional information might be needed (if any)
- You have access to three types of information sources:
    1) Sub-components or sub-modules (from memory):
        - If the target is a MODULE or REPO, you can request the documentation of its sub-components or sub-modules that have already been documented from memory.
        - This is the primary source of information for MODULE and REPO tasks, since the module/repo-level documentation should be synthesized based on the already generated sub-component/sub-module documentations.
        - If you think you need the information of sub-components or sub-modules from memory, use <RETRIEVE>YES</RETRIEVE> tag to request the specific documentations from memory.
        - If the target is a REPO, you should first read the documentation of all top-level modules and components using READ<RETRIEVE>YES</RETRIEVE>, then decide if you need to read the documentation of lower-level sub-modules based on the gaps you observe in the module-level documentations.
    
    2) Internal Codebase Information (from local code repository):
        For Functions:
        - Code components called within the function body
        - Places where this function is called
        For Methods:
        - Code components called within the method body
        - Places where this method is called
        - The class this method belongs to
        For Classes:
        - Code components called in the __init__ method
        - Places where this class is instantiated
        - Complete class implementation beyond __init__

    3) External Open Internet retrieval Information:
        - External Retrieval is extremely expensive. Only request it when understanding an external third-party API or library is essential for accurate documentation, and that information cannot be found within the target codebase.
        - Use the import statements in <IMPORT_INFORMATION_IN_THE_FILE> to identify candidates for retrieval. If the component relies on a third-party API (e.g. `from openai import OpenAI`, `import torch`, `from stripe import Webhook`), you may request retrieval to understand the external API's expected behavior, parameters, or return types.
        - Also request retrieval for novel, state-of-the-art algorithms or techniques not self-explanatory from the code alone (e.g. NDCG Loss, Cohen's Kappa, specialized metrics).
        - Each query should be a clear, natural language question targeting specific API behavior or concept.

- If more information is needed, end your response with a structured request in XML format:
<RETRIEVE>YES or NO</RETRIEVE>
<REQUEST>
    <INTERNAL>
        <CLASS>class1,class2</CLASS>
        <FUNCTION>func1,func2</FUNCTION>
        <METHOD>self.method1,instance.method2,class.method3</METHOD>
    </INTERNAL>
    <RETRIEVAL>
        <QUERY>query1</QUERY>
    </RETRIEVAL>
</REQUEST>

- Important rules for structured request:
    - If no items exist for a category, use empty tags (e.g., <CLASS></CLASS>)
    - Each external QUERY should be a concise, clear, natural language search query.
    - Use comma-separated values without spaces for multiple items.
    - For METHODS, keep dot notation in the same format as the input.
    - Only first-level calls of the focal code component are accessible. Do not request information on code components that are not directly called by the focal component.
    - External Retrieval is extremely expensive. Only request external open internet retrieval information if the entity involves a novel, state of the art, recently-proposed algorithms or techniques.
            (e.g. computing a novel loss function (NDCG Loss, Alignment and Uniformity Loss, etc), certain novel metrics (Cohen's Kappa, etc), specialized novel ideas that can not be searched within the target codebase)
    - Each query should be a clear, natural language question
    - Only request internal codebase information that you think is necessary for docstring generation task. For some components that is simple and obvious, you do not need any other information for docstring generation.
    - For module and repository-level documentation, you MUST request <RETRIEVE>YES</RETRIEVE> first before any other information source. The memory-stored summaries are the primary basis for module and repository-level documentation and should always be retrieved at the start.
    - For module and repository-level documentation, Sources 2) and 3) are supplementary. Since sub-components or sub-modules have already been individually documented in prior steps, their internal or external information has already been gathered. Only request additional internal codebase or external retrieval information if there is a specific gap that cannot be addressed by the memory-stored summaries.


- Example response
Action: READ
<RETRIEVE>NO</RETRIEVE>
<REQUEST>
    <INTERNAL>
        <CLASS></CLASS>
        <FUNCTION>execute_query,connect_db</FUNCTION>
        <METHOD>self.process_data,data_processor._internal_process</METHOD>
    </INTERNAL>
    <RETRIEVAL>
        <QUERY></QUERY>
    </RETRIEVAL>
</REQUEST>

2. WRITE : If you think you have collected sufficient context, use this action and generate the documentation for the target task type.

- General guidelines for high-quality documentation:
    - Make documentations actionable and specific: Focus on practical usage.
    - Use clear, concise language: Avoid jargon unless necessary, use active voice, and be direct and specific.
    - Type Information: Include precise type hints, note any type constraints, and document generic type parameters.
    - Context and Integration: Explain component relationships, note any dependencies, and describe side effects.
    - Follow Google docstring format: Use consistent indentation, maintain clear section separation.
- You MUST include the documentation in a <DOCUMENTATION>...</DOCUMENTATION> block including required contents.
- The <DOCUMENTATION> block must contain ONLY the documentation text — section headers and their content.
- NEVER include any of the following inside <DOCUMENTATION>:
    - Python source code (def, class, return, import statements)
    - Triple-quoted docstrings (triple double-quotes or triple single-quotes)
    - Code fences (```)
    - The original function/class definition
    - Any comment syntax (# or //)

- CORRECT example:
Action: WRITE
<DOCUMENTATION>
## Summary:
Reads a file and returns its content as a list of lines.

## Description:
Opens the specified file in read mode using the given encoding.

## Args:
    path (str): Absolute or relative path to the target file.
    encoding (str): Character encoding. Defaults to 'utf-8'.

## Returns:
    list[str]: A list of strings, one per line, with trailing newlines removed.

## Raises:
    FileNotFoundError: If the file does not exist.
</DOCUMENTATION>

- WRONG example (do NOT do this):
<DOCUMENTATION>
def read_lines(path, encoding='utf-8'):
    \"\"\"Reads a file and returns its content as a list of lines.\"\"\"
    return open(path, encoding=encoding).readlines()
</DOCUMENTATION>

3. VERIFY: After generating a documentation, use this action to self-evaluate the documentation quality along three criteria, each scored from 0.00 to 1.00 (two decimal places).

- Verification Process:
    - First read the target task information (source code and related information) as if you're seeing it for the first time.
    - Read the generated documentation and evaluate each of the following criteria.
    - Be a harsh, skeptical reviewer. Assume the documentation is flawed until proven otherwise.
    - A perfect 1.00 is reserved for documentation that cannot be improved in any way.

- Scoring discipline:
    - Start each criterion at 0.50 and adjust up or down based on concrete evidence found during review.
    - Deduct at least 0.05 for each distinct minor flaw (e.g. imprecise wording, missing edge case).
    - Deduct at least 0.10 for each distinct major flaw (e.g. wrong type, fabricated parameter, missing parameter entirely).
    - A score above 0.85 requires an explicit justification in your Thought — list what the documentation does well.
    - Never round up. If you are unsure whether a claim is correct, treat it as incorrect.
    - Avoid anchoring to your own prior output — evaluate the text as if someone else wrote it.

- Evaluation criteria:
    1) Consistency:
        - Line-by-line cross-check: for every factual statement in the documentation, locate the corresponding evidence in the source code. If you cannot point to a specific line that supports the claim, deduct points.
        - Every parameter name, type, and description must exactly match the actual function signature; no parameter is mislabeled, mistyped, or given a fabricated default value.
        - Described behavior (preconditions, side effects, return values, raised exceptions) must be directly verifiable from the source code — nothing is fabricated or assumed.
        - No statement in the documentation may contradict what the code actually does (e.g., wrong return type, incorrect exception condition, swapped parameter roles).
        - Code examples, if present, must be syntactically valid Python and produce the stated output when executed against the implementation.
        - Deduct points for: vague hedge words ("typically", "usually", "may") used instead of precise statements; claims that go beyond what the source code shows; any detail copied from a different component; invented functionality not present in the code.

    2) Completeness:
        - Walk through the source code top-to-bottom and verify that every visible element is documented:
            * Every parameter: name, type, and purpose. Is any parameter silently omitted?
            * Return value: type and meaning. Is it documented?
            * Every exception explicitly raised: type and trigger condition. Is any missing?
        - Significant edge cases, constraints, and preconditions visible in the source code (e.g. if-guards, assertions, boundary checks) must be reflected in the documentation.
        - For classes: are all public attributes and `__init__` parameters documented? For modules/repos: are all public components listed with one-line role descriptions?
        - Deduct points for: any parameter, return value, or raised exception present in the source but absent from the documentation; missing edge-case that is visible in the code; undocumented class attributes or module-level exports.

    3) Helpfulness:
        - Read the Summary line in isolation. Does it immediately convey *what* the component does and *why* it exists — or does it merely restate the function/class name in slightly longer words?
        - Imagine you are a developer who has never seen this codebase. Can you understand how and when to use this component from the documentation alone, without reading the source code?
        - Descriptions must explain purpose and typical use cases (WHY / WHEN), not just restate the code logic line-by-line (HOW).
        - For non-trivial interfaces: are usage examples included? Do they demonstrate realistic, end-to-end scenarios, or are they trivially obvious (e.g. just calling the function with no context)?
        - Deduct points for: summary that paraphrases the function name without adding insight; descriptions that merely narrate the implementation step-by-step; missing examples for complex interfaces; examples that show only the happy path without edge cases.

- You MUST include a <SCORE> block immediately after the action line with a structured request in XML format:
<SCORE>
    <CONSISTENCY>score1</CONSISTENCY>
    <COMPLETENESS>score2</COMPLETENESS>
    <HELPFULNESS>score3</HELPFULNESS>
</SCORE>

- The three scores are combined into a final score to determine whether the documentation meets the verification.
- If the observation of the VERIFY action is PASS, proceed to Finish. If the verdict is REVISE, consider whether more context is needed (READ) or whether you can directly rewrite based on the feedback (WRITE). 
- If the documentation does not pass verification, it may be revised and re-verified up to {max_revisions} times.

- Example response
Action: VERIFY
<SCORE>
    <CONSISTENCY>0.90</CONSISTENCY>
    <COMPLETENESS>0.85</COMPLETENESS>
    <HELPFULNESS>0.80</HELPFULNESS>
</SCORE>

4. FINISH : If you think the documentation is complete and of high quality, and has passed verification, use this action to save the documentation to memory and end the task. Only call this after VERIFY passes.

- Example response
Action: FINISH
</DETAILED_TOOL_USAGE>
"""


# WORKER_AGENT_SYSTEM_PROMPT 는  Worker agent 가 작업을 시작할 때 맨 처음 입력받은 명령어이다.
# WORKER_AGENT USER PROMPT 는 Manager agent 가  Worker agent 에게 sub-goal (document 할 component, module, or repo) 을 전달할 때 사용하는 프롬프트이다.
WORKER_AGENT_SYSTEM_PROMPT = """\
<ROLE>
You are an expert code documentation worker agent operating on a software repository. Your goal is to generate a high-quality documentation that are both complete and helpful for developers. 
</ROLE>

<OBJECTIVES>
Generate documentation sufficient for a developer to reconstruct a functional implementation from scratch using only this documentation.
Each level must answer the following questions:
- Repository-level : "What does this system do, and how are its parts organized?"                                                                                        
- Module-level : "What does this module do, and how do its components interact?"                                                                                     
- Component-level: "How do I implement this function/class/method correctly?"
</OBJECTIVES>

<DOCUMENTATION_STRUCTURE>
Generate documentation following this structure depending on the target level:
1. REPO : Repository-level Documentation:
    - Brief introduction and purpose of the overall system
    - Architecture overview with diagrams
    - High-level functionality of each sub-module including references to its documentation file
    - Link to other module documentation instead of duplicating information
    - Do not duplicate content covered in MODULE or COMPONENT docs. Focus on the big picture, not implementation details

2. MODULE: Module-level Documentation:
    - Explanation of the module's role within the system and its internal design, so a developer can understand *how* its components fit together before reading individual component details
    - Responsibility and boundaries of the module
    - List of core components with a one-line description each
    - Component interaction diagram or call flow (if non-trivial)
    - Key data structures and state shared across components
    - Links to component-level documentation for each component
   
3. COMPONENT: Component-level Documentation:
    - Providing enough detail to *reimplement* the function, method, or class correctly — covering inputs, outputs, behavior, edge cases, and constraints
    - Summary of what the component does and why it exists (not how it works)
</DOCUMENTATION_STRUCTURE>

<WORKFLOW>
1. You will first receive a sub-task, which includes the type of task (COMPONENT, MODULE, or REPO), the target component/module/repo to document, and other relevant information.
2. Analyze the provided code components or module structure, explore the not given dependencies between the components if needed.
3. For COMPONENT tasks, generate the documentation for the specific component, and save the documentation in memory with the name of `component_id`.
4. For MODULE tasks, synthesize the documentations of sub-components and generate the module-level documentation, and save the documentation in memory with the name of `module_id`.
5. For REPO tasks, synthesize the documentations of all modules and generate the repository-level documentation, and save the documentation in memory with the name of `repo_id`.
6. For each task, you perform thought-action-observation loops to iteratively improve the documentation until it passes verification, then save the final documentation to memory and return.
    - At every turn, you MUST follow this structure:
        Thought: <your reasoning about what to do next, what information you need>
        Action: Choose exactly one action from the list below and provide the necessary input.
        (Observation will be provided after each action to inform your next step. Do NOT generate this yourself.)
    - Repeat until all target component is fully documented and verified, then call Finish to save and exit.
    - The required sequence of actions is typically: Read → Write → Verify → (optional Read or Write) → Finish
</WORKFLOW>

<AVAILABLE_TOOLS>
For each turn, first think about what you should do, then take exactly one of the four actions below:
- `READ`: Request specific information about the code component or module structure.
- `WRITE`: Generate documentation for the target component/module/repo based on the provided information and context.
- `VERIFY`: Evaluate the quality of the generated documentation using an external evaluation tool. Use the feedback to iteratively improve the documentation if needed.
- `FINISH`: Save the final documentation to memory and end the task. Only call this after VERIFY passes.
</AVAILABLE_TOOLS> 

<DETAILED_TOOL_USAGE>
1. READ: If you think more information is needed to generate high-quality documentation of the target component, use this action to request relevant information.

- During think step, you should analyze the current code and context, and explain what additional information might be needed (if any)
- You have access to three types of information sources:
    1) Sub-components or sub-modules (from memory):
        - If the target is a MODULE or REPO, you can request the documentation of its sub-components or sub-modules that have already been documented from memory.
        - This is the primary source of information for MODULE and REPO tasks, since the module/repo-level documentation should be synthesized based on the already generated sub-component/sub-module documentations.
        - If you think you need the information of sub-components or sub-modules from memory, use <RETRIEVE>YES</RETRIEVE> tag to request the specific documentations from memory.
        - If the target is a REPO, you should first read the documentation of all top-level modules and components using READ<RETRIEVE>YES</RETRIEVE>, then decide if you need to read the documentation of lower-level sub-modules based on the gaps you observe in the module-level documentations.
    
    2) Internal Codebase Information (from local code repository):
        For Functions:
        - Code components called within the function body
        - Places where this function is called
        For Methods:
        - Code components called within the method body
        - Places where this method is called
        - The class this method belongs to
        For Classes:
        - Code components called in the __init__ method
        - Places where this class is instantiated
        - Complete class implementation beyond __init__

    3) External Open Internet retrieval Information:
        - External Retrieval is extremely expensive. Only request it when understanding an external third-party API or library is essential for accurate documentation, and that information cannot be found within the target codebase.
        - Use the import statements in <IMPORT_INFORMATION_IN_THE_FILE> to identify candidates for retrieval. If the component relies on a third-party API (e.g. `from openai import OpenAI`, `import torch`, `from stripe import Webhook`), you may request retrieval to understand the external API's expected behavior, parameters, or return types.
        - Also request retrieval for novel, state-of-the-art algorithms or techniques not self-explanatory from the code alone (e.g. NDCG Loss, Cohen's Kappa, specialized metrics).
        - Each query should be a clear, natural language question targeting specific API behavior or concept.

- If more information is needed, end your response with a structured request in XML format:
<RETRIEVE>YES or NO</RETRIEVE>
<REQUEST>
    <INTERNAL>
        <CLASS>class1,class2</CLASS>
        <FUNCTION>func1,func2</FUNCTION>
        <METHOD>self.method1,instance.method2,class.method3</METHOD>
    </INTERNAL>
    <RETRIEVAL>
        <QUERY>query1</QUERY>
    </RETRIEVAL>
</REQUEST>

- Important rules for structured request:
    - If no items exist for a category, use empty tags (e.g., <CLASS></CLASS>)
    - Each external QUERY should be a concise, clear, natural language search query.
    - Use comma-separated values without spaces for multiple items.
    - For METHODS, keep dot notation in the same format as the input.
    - Only first-level calls of the focal code component are accessible. Do not request information on code components that are not directly called by the focal component.
    - External Retrieval is extremely expensive. Only request external open internet retrieval information if the entity involves a novel, state of the art, recently-proposed algorithms or techniques.
            (e.g. computing a novel loss function (NDCG Loss, Alignment and Uniformity Loss, etc), certain novel metrics (Cohen's Kappa, etc), specialized novel ideas that can not be searched within the target codebase)
    - Each query should be a clear, natural language question
    - Only request internal codebase information that you think is necessary for docstring generation task. For some components that is simple and obvious, you do not need any other information for docstring generation.
    - For module and repository-level documentation, you MUST request <RETRIEVE>YES</RETRIEVE> first before any other information source. The memory-stored summaries are the primary basis for module and repository-level documentation and should always be retrieved at the start.
    - For module and repository-level documentation, Sources 2) and 3) are supplementary. Since sub-components or sub-modules have already been individually documented in prior steps, their internal or external information has already been gathered. Only request additional internal codebase or external retrieval information if there is a specific gap that cannot be addressed by the memory-stored summaries.


- Example response
Thought : put your thought here.
Action: READ
<RETRIEVE>NO</RETRIEVE>
<REQUEST>
    <INTERNAL>
        <CLASS></CLASS>
        <FUNCTION>execute_query,connect_db</FUNCTION>
        <METHOD>self.process_data,data_processor._internal_process</METHOD>
    </INTERNAL>
    <RETRIEVAL>
        <QUERY></QUERY>
    </RETRIEVAL>
</REQUEST>

2. WRITE : If you think you have collected sufficient context, use this action and generate the documentation for the target task type.

- General guidelines for high-quality documentation:
    - Make documentations actionable and specific: Focus on practical usage.
    - Use clear, concise language: Avoid jargon unless necessary, use active voice, and be direct and specific.
    - Type Information: Include precise type hints, note any type constraints, and document generic type parameters.
    - Context and Integration: Explain component relationships, note any dependencies, and describe side effects.
    - Follow Google docstring format: Use consistent indentation, maintain clear section separation.
- You MUST include the documentation in a <DOCUMENTATION>...</DOCUMENTATION> block including required contents.
- The <DOCUMENTATION> block must contain ONLY the documentation text — section headers and their content.
- NEVER include any of the following inside <DOCUMENTATION>:
    - Python source code (def, class, return, import statements)
    - Triple-quoted docstrings (triple double-quotes or triple single-quotes)
    - Code fences (```)
    - The original function/class definition
    - Any comment syntax (# or //)

- CORRECT example:
Thought: put your thought here.
Action: WRITE
<DOCUMENTATION>
## Summary:
Reads a file and returns its content as a list of lines.

## Description:
Opens the specified file in read mode using the given encoding.

## Args:
    path (str): Absolute or relative path to the target file.
    encoding (str): Character encoding. Defaults to 'utf-8'.

## Returns:
    list[str]: A list of strings, one per line, with trailing newlines removed.

## Raises:
    FileNotFoundError: If the file does not exist.
</DOCUMENTATION>

- WRONG example (do NOT do this):
<DOCUMENTATION>
def read_lines(path, encoding='utf-8'):
    \"\"\"Reads a file and returns its content as a list of lines.\"\"\"
    return open(path, encoding=encoding).readlines()
</DOCUMENTATION>

3. VERIFY: After generating a documentation, use this action to self-evaluate the documentation quality along three criteria, each scored from 0.00 to 1.00 (two decimal places).

- Verification Process:
    - First read the target task information (source code and related information) as if you're seeing it for the first time.
    - Read the generated documentation and evaluate each of the following criteria.
    - Be a harsh, skeptical reviewer. Assume the documentation is flawed until proven otherwise.
    - A perfect 1.00 is reserved for documentation that cannot be improved in any way.

- Scoring discipline:
    - Start each criterion at 0.50 and adjust up or down based on concrete evidence found during review.
    - Deduct at least 0.05 for each distinct minor flaw (e.g. imprecise wording, missing edge case).
    - Deduct at least 0.10 for each distinct major flaw (e.g. wrong type, fabricated parameter, missing parameter entirely).
    - A score above 0.85 requires an explicit justification in your Thought — list what the documentation does well.
    - Never round up. If you are unsure whether a claim is correct, treat it as incorrect.
    - Avoid anchoring to your own prior output — evaluate the text as if someone else wrote it.

- Evaluation criteria:
    1) Consistency:
        - Line-by-line cross-check: for every factual statement in the documentation, locate the corresponding evidence in the source code. If you cannot point to a specific line that supports the claim, deduct points.
        - Every parameter name, type, and description must exactly match the actual function signature; no parameter is mislabeled, mistyped, or given a fabricated default value.
        - Described behavior (preconditions, side effects, return values, raised exceptions) must be directly verifiable from the source code — nothing is fabricated or assumed.
        - No statement in the documentation may contradict what the code actually does (e.g., wrong return type, incorrect exception condition, swapped parameter roles).
        - Code examples, if present, must be syntactically valid Python and produce the stated output when executed against the implementation.
        - Deduct points for: vague hedge words ("typically", "usually", "may") used instead of precise statements; claims that go beyond what the source code shows; any detail copied from a different component; invented functionality not present in the code.

    2) Completeness:
        - Walk through the source code top-to-bottom and verify that every visible element is documented:
            * Every parameter: name, type, and purpose. Is any parameter silently omitted?
            * Return value: type and meaning. Is it documented?
            * Every exception explicitly raised: type and trigger condition. Is any missing?
        - Significant edge cases, constraints, and preconditions visible in the source code (e.g. if-guards, assertions, boundary checks) must be reflected in the documentation.
        - For classes: are all public attributes and `__init__` parameters documented? For modules/repos: are all public components listed with one-line role descriptions?
        - Deduct points for: any parameter, return value, or raised exception present in the source but absent from the documentation; missing edge-case that is visible in the code; undocumented class attributes or module-level exports.

    3) Helpfulness:
        - Read the Summary line in isolation. Does it immediately convey *what* the component does and *why* it exists — or does it merely restate the function/class name in slightly longer words?
        - Imagine you are a developer who has never seen this codebase. Can you understand how and when to use this component from the documentation alone, without reading the source code?
        - Descriptions must explain purpose and typical use cases (WHY / WHEN), not just restate the code logic line-by-line (HOW).
        - For non-trivial interfaces: are usage examples included? Do they demonstrate realistic, end-to-end scenarios, or are they trivially obvious (e.g. just calling the function with no context)?
        - Deduct points for: summary that paraphrases the function name without adding insight; descriptions that merely narrate the implementation step-by-step; missing examples for complex interfaces; examples that show only the happy path without edge cases.

- You MUST include a <SCORE> block immediately after the action line with a structured request in XML format:
<SCORE>
    <CONSISTENCY>score1</CONSISTENCY>
    <COMPLETENESS>score2</COMPLETENESS>
    <HELPFULNESS>score3</HELPFULNESS>
</SCORE>

- The three scores are combined into a final score to determine whether the documentation meets the verification.
- If the observation of the VERIFY action is PASS, proceed to Finish. If the verdict is REVISE, consider whether more context is needed (READ) or whether you can directly rewrite based on the feedback (WRITE). 
- If the documentation does not pass verification, it may be revised and re-verified up to {max_revisions} times.

- Example response
Thought : put your thought here.
Action: VERIFY
<SCORE>
    <CONSISTENCY>0.90</CONSISTENCY>
    <COMPLETENESS>0.85</COMPLETENESS>
    <HELPFULNESS>0.80</HELPFULNESS>
</SCORE>

4. FINISH : If you think the documentation is complete and of high quality, and has passed verification, use this action to save the documentation to memory and end the task. Only call this after VERIFY passes.

- Example response
Thought : put your thought here.
Action: FINISH
</DETAILED_TOOL_USAGE>
"""

COMPONENT_USER_PROMPT = """\
Now, generate comprehensive documentation for the {type} component named {component_name} using the provided source code and file path.

The generated {type} typed component-level documentation should be included following contents:
{format}

<FILE_PATH>
{file_path}
</FILE_PATH>

<IMPORT_INFORMATION_IN_THE_FILE>
{imports}
</IMPORT_INFORMATION_IN_THE_FILE>

<SOURCE_CODE>
{source_code}
</SOURCE_CODE>
"""

MODULE_USER_PROMPT = """\
Now, generate comprehensive documentation for the {module_name} module using the provided module tree.

The generated module-level documentation should be included following contents:
{format}

<MODULE_TREE>
{module_tree}
</MODULE_TREE>
"""

REPO_USER_PROMPT = """\
Now, generate comprehensive documentation for the {repo_name} repository using the provided repository tree.

The generated repository-level documentation should be included following contents:
{format}

<REPO_TREE>
{repo_tree}
</REPO_TREE>
"""

REPO_PROMPT = """
## Tree:
    - Full top-level directory hierarchy (2-3 levels deep, indented tree format)
    - Annotate each major directory with its responsibility
 
## Purpose:
    - What problem this repository solves and why it matters
    - Target users and the scenarios they use it in
    - Position in the broader ecosystem (standalone tool, library, service)

## Architecture:
    - End-to-end data flow diagram using Mermaid (flowchart TD or sequence diagram)
    - Key abstractions and architectural patterns (pipeline, agent loop, plugin, etc.)

## Entry Points:
    - CLI commands, importable APIs, or service endpoints
    - For each: what it exposes, required arguments, and target audience

## Core Features:
    - List the key capabilities the repo provides
    - For each feature: one-line description + the implementing module(s)/component(s)

## Dependencies:
    - Key external dependencies and the role each plays
    - Version constraints or compatibility requirements that affect architecture

Conditional sections:
## Configuration:
    - Config files, environment variables, runtime parameters
    - Include only if configuration meaningfully affects system behavior

## Extension Points:
    - How to extend the system (plugins, hooks, subclassing, config-driven behavior)
    - Include only if extensibility is a first-class concern
"""

MODULE_PROMPT = """
## Tree:
    - Directory/file hierarchy of this module (indented tree format)

## Role:
    - Single-responsibility description: the one thing this module owns
    - Avoid repeating the module name

## Description:
    - Describe where and when this module is used within the repo : List the primary consumers (other modules or entry points that import it)
    - Explain why these components are grouped into a separate module : Describe the cohesion principle (shared concept, layer boundary, etc.)

## Components:
    - List all public classes, functions, and constants with their signatures
    - For each: *one-line* role description
    - Mermaid dependency graph showing relationships among internal components

## Public API:
    - The interfaces this module exposes to the rest of the repository
    - For each public symbol: signature, brief description, usage note

## Dependencies:
    - Internal imports (other repo modules) and their purpose
    - External imports (third-party libraries) and why they are needed

## Constraints:
    - Constraints callers must respect when using this module
    - Thread-safety, ordering requirements, initialization prerequisites
"""

FUNCTION_PROMPT = """
## Summary:
    - One-line description focusing on WHAT the function does
    - Avoid repeating the function name
    - Emphasize the outcome or effect

## Description:
    - List known callers within the codebase and the context in which they call this function : Describe the typical trigger condition or pipeline stage
    - Explain why this logic is extracted into its own function rather than inlined : Describe the responsibility boundary it enforces

## Args (if present):
    - name, type, allowed range/values, default value
    - Note any interdependencies between parameters

## Returns:
    - Explain what the return value represents
    - Include all possible return values and edge-case return values

## Raises:
    - exception type and exact condition in the code that triggers it

## Constraints:
    - Preconditions: what must be true before calling this function
    - Postconditions: what is guaranteed to be true after it returns

## Side Effects:
    - Any I/O (files, network, stdout)
    - External state mutations (global variables, database writes, cache updates)
    - External service calls

## Control Flow:
    - Mermaid flowchart (flowchart TD) illustrating the main decision branches and loops

## Examples (if public and non-trivial):
    - Show realistic end-to-end usage including error handling
"""

METHOD_PROMPT = """
## Summary:
    - One-line description focusing on WHAT the method does
    - Avoid repeating the method name
    - Emphasize the effect on the object's state

## Description:
    - List known callers and the context in which they call this method : Describe the lifecycle stage or pipeline step where this method is invoked
    - Explain why this logic is its own method rather than inlined or placed elsewhere

## Args (if present):
    - name, type, allowed range/values, default value

## Returns:
    - type, possible values, and edge-case return values

## Raises:
    - exception type and exact condition that triggers it

## State Changes:
    - Attributes READ : list self.<attr> fields this method reads
    - Attributes WRITTEN : list self.<attr> fields this method modifies

## Constraints:
    - Preconditions: what must be true about the object/args before calling
    - Postconditions: what is guaranteed on self or the return value after the call

## Side Effects:
    - I/O, external service calls, or mutations to objects outside self
"""

CLASS_PROMPT = """
## Summary:
    - One-line description focusing on WHAT the class represents
    - Focus on the core purpose or responsibility

## Description:
    - Scenarios where this class should be instantiated; known callers/factories that create instances
    - Motivation for this class as a distinct abstraction; the responsibility boundary it enforces

## State:
    - Each attribute: name, type, valid range/values, invariant it participates in
    - For __init__ parameters: note default value and any constraints for the caller
    - Class invariants: conditions that must always hold between method calls

## Lifecycle:
    - Creation: how to instantiate (required args, factory methods)
    - Usage: which methods are called in what order; any required sequencing
    - Destruction: cleanup responsibilities (context manager, close(), etc.)

## Method Map:
    - Mermaid diagram (flowchart or graph) showing method call dependencies
      and typical invocation order

## Raises:
    - Exceptions raised by __init__ and their trigger conditions

## Example:
    - Demonstrate creation, typical method sequence, and cleanup
"""

# ---------------------------------------------------------------------------
# MarkdownExporter
# ---------------------------------------------------------------------------


class MarkdownExporter:
    """Converts a completed RepoMemory into a structured markdown file tree.

    Output layout (all under *output_dir*)::

        {repo_name}.md                        # repo root — repo doc + module index
        {module_path}.md                      # module doc + file index
        {file_path_stem}.md                   # all components that live in that file

    All inter-file links are relative so the tree is self-contained.

    Args:
        repo_memory: Fully-populated RepoMemory after the pipeline finishes.
        repo_name: Base name of the repository (e.g. ``"my_project"``).
        output_dir: Absolute path to the directory where markdown files are written.
    """

    def __init__(
        self,
        repo_memory: "RepoMemory",
        repo_name: str,
        output_dir: str,
        components: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.memory = repo_memory
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.components = components or {}

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def export(self) -> str:
        """Write all markdown files and return the path to the repo root .md.

        Steps:
            1. Group components by ``file_path``.
            2. Write one ``{file_stem}.md`` per source file.
            3. Write one ``{module_path}.md`` per module.
            4. Write ``{repo_name}.md`` at *output_dir* root.

        Returns:
            Absolute path to ``{repo_name}.md``.
        """
        os.makedirs(self.output_dir, exist_ok=True)

        # Step 1 — group components by source file
        file_to_comps: Dict[str, List[str]] = {}
        for cid, entry in self.memory.get_all_component_summaries().items():
            fp = entry.file_path or ""
            file_to_comps.setdefault(fp, []).append(cid)

        # Step 2 — file-level docs
        for file_path, comp_ids in file_to_comps.items():
            if file_path:
                self._write_file_doc(file_path, comp_ids)

        # Step 3 — module-level docs
        for module_path, module_entry in self.memory.get_all_module_summaries().items():
            self._write_module_doc(module_path, module_entry, file_to_comps)

        # Step 4 — repo root doc
        return self._write_repo_doc()

    # ------------------------------------------------------------------
    # Private writers
    # ------------------------------------------------------------------

    def _write_file_doc(self, file_path: str, comp_ids: List[str]) -> str:
        """Write ``{file_path_stem}.md`` containing all components in *file_path*.

        Components are sorted by ``start_line`` so methods appear directly after
        their parent class, matching the actual source order. Heading levels encode
        type: ``class`` and ``function`` use h2; ``method`` uses h3 to visually
        nest under the preceding class heading.

        Args:
            file_path: Repo-relative source file path, e.g. ``"src/agent/reader.py"``.
            comp_ids: Component IDs whose source lives in *file_path*.

        Returns:
            Absolute path to the written markdown file.
        """
        stem = os.path.splitext(file_path)[0]   # "src/agent/reader"
        abs_path = os.path.join(self.output_dir, stem + ".md")
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # Sort by start_line (source order); fall back to alphabetical
        def _sort_key(cid: str) -> tuple:
            comp = self.components.get(cid)
            line = comp.start_line if comp and hasattr(comp, "start_line") else 0
            return (line, cid)

        # heading level and type label per component type
        _TYPE_H = {
            "class":    ("##",  "class"),
            "function": ("##",  "function"),
            "method":   ("###", "method"),
        }

        file_name = os.path.basename(file_path)
        lines: List[str] = [f"# `{file_name}`\n\n"]

        for cid in sorted(comp_ids, key=_sort_key):
            entry = self.memory.get_component_summary(cid)
            if not entry:
                continue

            # Short display name: strip file-stem prefix
            # e.g. "src/agent/reader.Reader.process" → "Reader.process"
            short_name = (
                cid[len(stem) + 1:]
                if cid.startswith(stem + ".")
                else cid.split("/")[-1]
            )

            # Prefer CodeComponent for type (always populated);
            # fall back to RepoMemory entry for non-Python components
            comp = self.components.get(cid)
            ct = (comp.component_type if comp and hasattr(comp, "component_type")
                  else entry.component_type or "")
            h_level, label = _TYPE_H.get(ct, ("##", ct))
            type_tag = f" · *{label}*" if label else ""
            lines.append(f"{h_level} `{short_name}`{type_tag}\n\n")

            if entry.documentation:
                lines.append(entry.documentation.strip() + "\n\n")
            else:
                lines.append("*No documentation generated.*\n\n")

        with open(abs_path, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
        logger.debug("MarkdownExporter: wrote %s", abs_path)
        return abs_path

    def _write_module_doc(
        self,
        module_path: str,
        module_entry: Any,
        file_to_comps: Dict[str, List[str]],
    ) -> str:
        """Write ``{module_path}.md`` containing the module doc and file index.

        Args:
            module_path: Repo-relative module directory, e.g. ``"src/agent"``.
            module_entry: :class:`ModuleEntry` from RepoMemory.
            file_to_comps: Mapping of file_path → component IDs (for link generation).

        Returns:
            Absolute path to the written markdown file.
        """
        abs_path = os.path.join(self.output_dir, module_path + ".md")
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        module_label = module_path.replace("/", ".")
        lines: List[str] = [f"# `{module_label}`\n\n"]

        if module_entry.documentation:
            lines.append(module_entry.documentation.strip() + "\n\n")

        # Files whose directory is exactly module_path (immediate children only)
        files_in_module = sorted(
            fp for fp in file_to_comps
            if fp and os.path.dirname(fp) == module_path
        )

        if files_in_module:
            lines.append("---\n\n## Files\n\n")
            for fp in files_in_module:
                stem = os.path.splitext(fp)[0]
                file_md_abs = os.path.join(self.output_dir, stem + ".md")
                rel_link = os.path.relpath(file_md_abs, os.path.dirname(abs_path))
                lines.append(f"- [`{os.path.basename(fp)}`]({rel_link})\n")
            lines.append("\n")

        with open(abs_path, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
        logger.debug("MarkdownExporter: wrote %s", abs_path)
        return abs_path

    def _write_repo_doc(self) -> str:
        """Write ``{repo_name}.md`` containing the repo doc and module index.

        Returns:
            Absolute path to the written markdown file.
        """
        abs_path = os.path.join(self.output_dir, f"{self.repo_name}.md")

        repo_entry = self.memory.get_repo_summary(self.repo_name)
        lines: List[str] = [f"# `{self.repo_name}`\n\n"]

        if repo_entry and repo_entry.documentation:
            lines.append(repo_entry.documentation.strip() + "\n\n")

        module_paths = sorted(self.memory.list_module_paths())
        if module_paths:
            lines.append("---\n\n## Modules\n\n")
            for mp in module_paths:
                module_md_abs = os.path.join(self.output_dir, mp + ".md")
                rel_link = os.path.relpath(module_md_abs, self.output_dir)
                lines.append(f"- [`{mp}`]({rel_link})\n")
            lines.append("\n")

        with open(abs_path, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
        logger.debug("MarkdownExporter: wrote %s", abs_path)
        return abs_path


# ---------------------------------------------------------------------------
# WorkerExecutor
# ---------------------------------------------------------------------------

class WorkerExecutor:
    """Executes individual ReAct actions on behalf of WorkerAgent.

    Keeps a ``draft`` buffer that is populated by Write and consumed by Finish.
    """

    def __init__(
        self,
        repo_path: str,
        repo_memory: RepoMemory,
        dep_graph: Dict[str, List[str]],
        task: WorkerTask,
        components: Optional[Dict[str, Any]] = None,
        analytics: Optional[Any] = None,
        llm: Optional[Any] = None,
        llm_params: Optional[Dict[str, Any]] = None,
        nli_config: Optional[Dict[str, Any]] = None,
        skip_conflict_check: bool = False,
        without_memory: bool = False,
        ver2_mode: bool = False,
    ) -> None:
        self.repo_path = repo_path
        self.repo_memory = repo_memory
        self.dep_graph = dep_graph
        self.task = task
        self.components: Dict[str, Any] = components or {}
        self._draft: Optional[str] = None
        self._analytics = analytics
        self._llm = llm
        self._llm_params: Dict[str, Any] = llm_params or {"temperature": 0.0, "max_output_tokens": 512}
        self._nli_config: Dict[str, Any] = nli_config or {}
        self.skip_conflict_check = skip_conflict_check
        self.without_memory = without_memory
        self.ver2_mode = ver2_mode

    # ------------------------------------------------------------------
    # ver2: filtered memory retrieval helpers
    # ------------------------------------------------------------------

    _REQUIRED_SECTIONS: Dict[str, set] = {
        "function": {"summary", "description", "returns"},
        "method":   {"summary", "description", "returns"},
        "class":    {"summary", "description", "state", "lifecycle", "method map"},
        "module":   {"tree", "role", "description", "components", "public api", "dependencies", "constraints"},
    }

    _SIMPLE_MAX_LINES = 15

    def _filter_doc_sections(self, documentation: str, component_type: str) -> str:
        """Extract only essential sections from documentation based on component type."""
        if not documentation:
            return ""
        required = self._REQUIRED_SECTIONS.get(component_type or "function", {"summary", "description", "returns"})

        # Parse ## Section: headers
        import re
        section_re = re.compile(r'^#{2,3}\s+([A-Za-z][A-Za-z /\-]*?)(?:\s*:)?\s*$', re.MULTILINE)
        matches = list(section_re.finditer(documentation))

        if not matches:
            return documentation  # no sections found, return as-is

        blocks = []
        for i, m in enumerate(matches):
            name = m.group(1).strip().lower()
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(documentation)
            if name in required:
                blocks.append(documentation[start:end].rstrip())

        return "\n\n".join(blocks) if blocks else documentation

    def _is_simple_component(self, comp_id: str) -> bool:
        """Check if a component is simple (no dependencies + short source code)."""
        comp = self.components.get(comp_id)
        if comp is None:
            return False
        has_deps = bool(getattr(comp, "depends_on", set()))
        # Check source code length from graph (CodeComponent has source_code or start/end lines)
        source = getattr(comp, "source_code", None) or ""
        if not source:
            # Try to get from memory
            entry = self.repo_memory.get_component_summary(comp_id)
            if entry is not None:
                source = entry.source_code or ""
        return not has_deps and len(source.splitlines()) <= self._SIMPLE_MAX_LINES

    def _get_source_for_component(self, comp_id: str) -> str:
        """Get raw source code for a component from memory or graph."""
        # Try memory first
        entry = self.repo_memory.get_component_summary(comp_id)
        if entry is not None and entry.source_code:
            return entry.source_code
        # Fall back to graph
        comp = self.components.get(comp_id)
        if comp is not None:
            src = self._extract_source_by_lines(comp)
            if src:
                return src
        return ""

    @property
    def draft(self) -> Optional[str]:
        return self._draft

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_target(self, cid: str) -> bool:
        """Return True if *cid* refers to the current task's target."""
        return self.task.target == cid or self.task.target.endswith("." + cid)

    def _get_imported_repo_files(self, relative_path: str) -> List[str]:
        """Return repo-relative paths of files imported by *relative_path* that exist in the repo."""
        from pathlib import Path
        ext = Path(relative_path).suffix.lower()
        # Only Python files support AST-based import collection.
        # For other languages the dependency graph already captures cross-file relationships.
        if ext != ".py":
            return []

        full_path = os.path.join(self.repo_path, relative_path)
        result: List[str] = []
        try:
            with open(full_path, "r", encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError):
            return result

        collector = ImportCollector()
        collector.visit(tree)

        for module_name in set(collector.imports) | set(collector.from_imports.keys()):
            # dot-notation → file path
            candidate = os.path.join(self.repo_path, module_name.replace(".", os.sep) + ".py")
            if os.path.isfile(candidate):
                norm = os.path.relpath(candidate, self.repo_path)
                if norm != relative_path:
                    result.append(norm)
                continue
            # package __init__.py fallback
            pkg = os.path.join(self.repo_path, module_name.replace(".", os.sep), "__init__.py")
            if os.path.isfile(pkg):
                norm = os.path.relpath(pkg, self.repo_path)
                if norm != relative_path:
                    result.append(norm)

        return result

    def _extract_source_by_lines(self, file_path: str, start_line: int, end_line: int) -> Optional[str]:
        """Read *file_path* and return lines [start_line, end_line] (1-indexed, inclusive)."""
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                all_lines = fh.readlines()
            return "".join(all_lines[start_line - 1 : end_line])
        except OSError:
            return None

    # ------------------------------------------------------------------
    # cid classification helpers
    # ------------------------------------------------------------------

    def _get_known_module_ids(self) -> set:
        """Return the set of module IDs (dot notation) known from self.components.

        Each unique ``relative_path`` in the dependency graph corresponds to one
        module.  E.g. ``src/agent/reader.py`` → ``src.agent.reader``.
        Already-documented modules in RepoMemory are included as well.
        Result is cached on first call.
        """
        if not hasattr(self, "_module_ids_cache"):
            from pathlib import Path as _Path
            modules: set = set()
            for comp in self.components.values():
                if comp.relative_path:
                    p = comp.relative_path.replace("\\", "/")
                    # Strip any known source extension
                    stem = p
                    for ext in CODE_EXTENSIONS:
                        if p.endswith(ext):
                            stem = p[: -len(ext)]
                            break
                    mod_id = stem.replace("/", ".")
                    modules.add(mod_id)
            modules.update(self.repo_memory.list_module_paths())
            self._module_ids_cache = modules
        return self._module_ids_cache

    def _classify_cid(self, cid: str) -> Tuple[str, str]:
        """Normalize *cid* to dot notation and classify it.

        Handles two input formats:
          * File-path notation  ``src/agent/reader.py``  →  ``src.agent.reader``
          * Dot notation        ``src.agent.reader``      (already normalized)

        Returns:
            (normalized_id, kind) where kind is one of:
              ``"target"``    — refers to the current task's target
              ``"module"``    — a Python module / package
              ``"component"`` — a function, class, or method
              ``"external"``  — a Perplexity search query (ends with ``?``)
              ``"unknown"``   — cannot be resolved
        """
        # External query — must be checked before normalization
        if cid.endswith("?"):
            return cid[:-1].strip(), "external"

        # Normalize file-path notation → dot notation
        _has_known_ext = any(cid.endswith(ext) for ext in CODE_EXTENSIONS)
        if "/" in cid or _has_known_ext:
            p = cid.lstrip("./").replace("\\", "/")
            # Strip any known source extension
            for ext in CODE_EXTENSIONS:
                if p.endswith(ext):
                    p = p[: -len(ext)]
                    break
            normalized = p.replace("/", ".")
        else:
            normalized = cid

        # Target check (after normalization so "src/agent/reader.py" also matches)
        if self._is_target(normalized):
            return normalized, "target"

        # Module: present in the known module set derived from dep graph
        if normalized in self._get_known_module_ids():
            return normalized, "module"

        # Component: exact match in dep graph or memory
        if normalized in self.components or normalized in self.repo_memory.list_component_ids():
            return normalized, "component"

        # Package prefix: e.g. "src" when components are "src.agent.reader.Reader"
        prefix = normalized + "."
        if any(comp_id.startswith(prefix) for comp_id in self.components):
            return normalized, "module"

        return normalized, "unknown"

    # ------------------------------------------------------------------
    # read_tool — target-first, memory-second, graph fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_read_xml(action_input: str) -> List[str]:
        """Parse a ``<REQUEST>...</REQUEST>`` XML block into a flat list of IDs.

        Extracts comma-separated values from ``<CLASS>``, ``<FUNCTION>``,
        ``<METHOD>`` tags (INTERNAL section) and ``<QUERY>`` tags (RETRIEVAL
        section).  Values are passed as-is so that ``_classify_cid`` can
        perform normalization and lookup.

        Returns an empty list when *action_input* contains no non-empty values.
        """
        tag_pattern = re.compile(r"<(CLASS|FUNCTION|METHOD|QUERY)>(.*?)</\1>", re.DOTALL | re.IGNORECASE)
        ids: List[str] = []
        for tag_match in tag_pattern.finditer(action_input):
            raw = tag_match.group(2).strip()
            if not raw:
                continue
            for item in raw.split(","):
                item = item.strip()
                if not item:
                    continue
                ids.append(item)
        return ids

    @staticmethod
    def _parse_read_request_dict(action_input: str) -> Dict[str, Any]:
        """Parse a READ action input (RETRIEVE + REQUEST XML) into a structured dict.

        Returns:
            {
                "RETRIEVE": "YES" or "NO",
                "CLASS": list of class names (empty list if none),
                "FUNCTION": list of function names (empty list if none),
                "METHOD": list of method names (empty list if none),
                "RETRIEVAL": list of queries (empty list if none),
            }
        """
        result: Dict[str, Any] = {
            "RETRIEVE": "NO",
            "CLASS": [],
            "FUNCTION": [],
            "METHOD": [],
            "RETRIEVAL": [],
        }

        retrieve_m = re.search(r"<RETRIEVE>(.*?)</RETRIEVE>", action_input, re.IGNORECASE | re.DOTALL)
        if retrieve_m:
            result["RETRIEVE"] = retrieve_m.group(1).strip().upper()

        for tag, key in [("CLASS", "CLASS"), ("FUNCTION", "FUNCTION"), ("METHOD", "METHOD"), ("QUERY", "RETRIEVAL")]:
            tag_m = re.search(rf"<{tag}>(.*?)</{tag}>", action_input, re.IGNORECASE | re.DOTALL)
            if tag_m:
                raw = tag_m.group(1).strip()
                if raw:
                    result[key] = [item.strip() for item in raw.split(",") if item.strip()]

        return result

    def read_tool(self, action_input: str) -> str:
        """Retrieve context using memory-first, graph-fallback strategy.

        Dispatches to a task-type-specific handler:
          - COMPONENT: source code + dependency docs
          - MODULE: component docs within the module from RepoMemory
          - REPO: module summaries from RepoMemory

        Args:
            action_input: Either a ``<REQUEST>...</REQUEST>`` XML block (new
                format) or a legacy comma-separated ID string.

        Returns:
            Formatted retrieval results as a string observation.
        """
        parsed_dict = self._parse_read_request_dict(action_input)
        print(f"Parsed READ request: {parsed_dict}", color="yellow")

        return self._read_component(parsed_dict)

    # ------------------------------------------------------------------
    # _read_component — unified retrieval handler
    # ------------------------------------------------------------------

    def _read_component(self, parsed_dict: Dict[str, Any]) -> str:

        lines: List[str] = []
        _graph_count = 0
        _memory_count = 0
        _fetched_names: List[str] = []
        _seen: set = set()  # 중복 fetch 방지

        # ------------------------------------------------------------------
        # 1. RETRIEVE: fetch sub-component/sub-module docs from memory
        #    (without_memory: fetch source code from graph instead)
        # ------------------------------------------------------------------
        if parsed_dict.get("RETRIEVE") == "YES" and self.without_memory:
            # Ablation: skip memory, graph-search all components whose
            # relative_path lives under the task's module/repo scope.
            target_ids: List[str] = []
            if self.task.type == TaskType.MODULE:
                # Walk the graph for every component physically located under
                # <module_path>/ (recursive, not just direct children).
                module_path = (self.task.target or "").replace("\\", "/").rstrip("/")
                prefix = module_path + "/"
                for cid, comp in self.components.items():
                    rel = (getattr(comp, "relative_path", "") or "").replace("\\", "/")
                    if not rel:
                        continue
                    if rel == module_path or rel.startswith(prefix) or os.path.dirname(rel) == module_path:
                        target_ids.append(cid)
            elif self.task.type == TaskType.REPO:
                # Every component in the repo is in scope.
                target_ids = list(self.components.keys())
            else:  # COMPONENT — depends_on fan-in stays the same
                comp = self.components.get(self.task.target)
                if comp is not None:
                    target_ids = sorted(comp.depends_on)

            for cid in sorted(set(target_ids)):
                if cid in _seen:
                    continue
                comp = self.components.get(cid)
                if comp is None:
                    continue
                src = self._extract_source_by_lines(
                    comp.file_path, comp.start_line, comp.end_line
                )
                if src:
                    lines.append(f"[GRAPH] {cid}:\n{src}")
                    _graph_count += 1
                    _fetched_names.append(cid)
                    _seen.add(cid)
            if not _fetched_names and self.task.type in (TaskType.MODULE, TaskType.REPO):
                lines.append(
                    f"[MISS] {self.task.target} — no components found under this scope"
                )

        elif parsed_dict.get("RETRIEVE") == "YES":
            if self.task.type == TaskType.MODULE:
                # 1) Read child module summaries (already documented)
                for child_mp in sorted(self.task.child_module_paths):
                    if child_mp in _seen:
                        continue
                    entry = self.repo_memory.get_module_summary(child_mp)
                    if entry is not None:
                        doc = entry.documentation
                        if self.ver2_mode and doc:
                            doc = self._filter_doc_sections(doc, "module")
                        lines.append(f"[MEMORY] {child_mp}\n{doc}")
                        _memory_count += 1
                        _fetched_names.append(child_mp)
                        _seen.add(child_mp)
                # 2) Read direct component summaries only
                for cid in sorted(self.task.component_ids):
                    if cid in _seen:
                        continue
                    if self.ver2_mode and self._is_simple_component(cid):
                        src = self._get_source_for_component(cid)
                        if src:
                            lines.append(f"[SOURCE] {cid}:\n{src}")
                            _memory_count += 1
                            _fetched_names.append(cid)
                            _seen.add(cid)
                            continue
                    entry = self.repo_memory.get_component_summary(cid)
                    if entry is not None:
                        doc = entry.documentation
                        if self.ver2_mode and doc:
                            doc = self._filter_doc_sections(doc, entry.component_type or "function")
                        lines.append(f"[MEMORY] {cid}\n{doc}")
                        _memory_count += 1
                        _fetched_names.append(cid)
                        _seen.add(cid)
                if not self.task.child_module_paths and not self.task.component_ids:
                    lines.append(
                        f"[MISS] {self.task.target} — no child modules or components found"
                    )

            elif self.task.type == TaskType.REPO:
                # 1) Read root module summaries only
                for mod_path in sorted(self.task.module_paths):
                    if mod_path in _seen:
                        continue
                    entry = self.repo_memory.get_module_summary(mod_path)
                    if entry is not None:
                        doc = entry.documentation
                        if self.ver2_mode and doc:
                            doc = self._filter_doc_sections(doc, "module")
                        lines.append(f"[MEMORY] {mod_path}\n{doc}")
                        _memory_count += 1
                        _fetched_names.append(mod_path)
                        _seen.add(mod_path)
                # 2) Read top-level component summaries (files not in any module)
                for cid in sorted(self.task.component_ids):
                    if cid in _seen:
                        continue
                    if self.ver2_mode and self._is_simple_component(cid):
                        src = self._get_source_for_component(cid)
                        if src:
                            lines.append(f"[SOURCE] {cid}:\n{src}")
                            _memory_count += 1
                            _fetched_names.append(cid)
                            _seen.add(cid)
                            continue
                    entry = self.repo_memory.get_component_summary(cid)
                    if entry is not None:
                        doc = entry.documentation
                        if self.ver2_mode and doc:
                            doc = self._filter_doc_sections(doc, entry.component_type or "function")
                        lines.append(f"[MEMORY] {cid}\n{doc}")
                        _memory_count += 1
                        _fetched_names.append(cid)
                        _seen.add(cid)
                if not self.task.module_paths and not self.task.component_ids:
                    lines.append(
                        f"[MISS] {self.task.target} — no module summaries found"
                    )

            else:  # COMPONENT: retrieve depends_on docs
                comp = self.components.get(self.task.target)
                depends_on: set = comp.depends_on if comp is not None else set()
                for dep_id in sorted(depends_on):
                    if dep_id in _seen:
                        continue
                    entry = self.repo_memory.get_component_summary(dep_id)
                    if entry is not None:
                        if self.ver2_mode and self._is_simple_component(dep_id):
                            # ver2: simple component → provide raw source
                            src = self._get_source_for_component(dep_id)
                            if src:
                                lines.append(f"[SOURCE] {dep_id}:\n{src}")
                        elif entry.documentation:
                            if self.ver2_mode:
                                # ver2: filter to essential sections only
                                filtered = self._filter_doc_sections(
                                    entry.documentation, entry.component_type or "function"
                                )
                                lines.append(f"[MEMORY] {dep_id}:\n{filtered}")
                            else:
                                lines.append(
                                    f"[MEMORY] {dep_id}:\n{entry.documentation}"
                                )
                        else:
                            lines.append(f"[MEMORY] {dep_id}:\n{entry.source_code}")
                        _memory_count += 1
                        _fetched_names.append(dep_id)
                        _seen.add(dep_id)

        # ------------------------------------------------------------------
        # 2. CLASS / FUNCTION / METHOD: suffix-match search
        # ------------------------------------------------------------------
        name_requests: List[str] = (
            parsed_dict.get("CLASS", [])
            + parsed_dict.get("FUNCTION", [])
            + parsed_dict.get("METHOD", [])
        )
        for name in name_requests:
            if not name:
                continue
            suffix = "." + name

            # Memory-first: find all component IDs ending with '.<name>'
            # (skipped in without_memory mode)
            if not self.without_memory:
                matched_ids = [
                    cid for cid in self.repo_memory.list_component_ids()
                    if cid == name or cid.endswith(suffix)
                ]
                if matched_ids:
                    for cid in matched_ids:
                        if cid in _seen:
                            continue
                        entry = self.repo_memory.get_component_summary(cid)
                        if entry is not None:
                            if entry.documentation:
                                lines.append(
                                    f"[MEMORY] {cid}:\n{entry.documentation}"
                                )
                            else:
                                lines.append(f"[MEMORY] {cid}:\n{entry.source_code}")
                            _memory_count += 1
                            _fetched_names.append(cid)
                            _seen.add(cid)
                    continue

            # Graph fallback: search self.components for suffix match
            graph_matches = [
                cid for cid in self.components
                if cid == name or cid.endswith(suffix)
            ]
            
            if not graph_matches:
                lines.append(f"[MISS] {name} — not found in memory or graph")
                continue

            for cid in graph_matches:
                if cid in _seen:
                    continue
                comp = self.components[cid]
                source = self._extract_source_by_lines(
                    comp.file_path, comp.start_line, comp.end_line
                )
                if source:
                    # Don't clobber a completed documentation (e.g. saved by a
                    # previous Finish): only cache the source when the entry is
                    # missing or still has no documentation.
                    existing = self.repo_memory.get_component_summary(cid)
                    if existing is None or not existing.documentation:
                        self.repo_memory.set_component_summary(
                            cid,
                            file_path=getattr(comp, "relative_path", ""),
                            source_code=source,
                            documentation="",
                            confidence=0.0,
                            component_type=getattr(comp, "component_type", None),
                        )
                    lines.append(f"[GRAPH] {cid}\n{source}")
                    _graph_count += 1
                    _fetched_names.append(cid)
                    _seen.add(cid)
                else:
                    lines.append(f"[MISS] {name} — source not found in graph")

        # ------------------------------------------------------------------
        # 3. RETRIEVAL: memory cache → Perplexity API fallback
        # ------------------------------------------------------------------
        queries = [q for q in parsed_dict.get("RETRIEVAL", []) if q]
        if queries:
            cache_miss = []
            for query in queries:
                cached = self.repo_memory.get_external_knowledge(query)
                if cached is not None:
                    lines.append(f"[MEMORY] {query}\n{cached}")
                else:
                    cache_miss.append(query)

            if cache_miss:
                results = self._gather_external_info(cache_miss)
                for query, answer in results.items():
                    self.repo_memory.set_external_knowledge(query, answer)
                    lines.append(f"[SEARCH] {query}\n{answer}")

        if self._analytics is not None:
            self._analytics.log_read_access(
                self.task.target, _graph_count, _memory_count, _fetched_names
            )

        return "\n\n".join(lines) if lines else "No information retrieved."


    # ------------------------------------------------------------------
    # verify_tool — self-evaluation scoring
    # ------------------------------------------------------------------

    def verify_tool(self, draft: str, llm_output: str = "", attempt: int = 1) -> VerifyResult:
        """Parse self-evaluation scores from the agent's Verify output and return a verdict.

        Scoring pipeline:
          1. Parse <score> block (3 criteria, each 0–1) from *llm_output*.
          2. Compute weighted average using ``VERIFY_WEIGHTS``.
          3. If the task has dependencies, run cross-dependency conflict check and
             average its consistency score with the weighted self-eval score.
          4. Return a :class:`VerifyResult` with verdict PASS / REVISE.

        Falls back to a PASS stub when no <score> block is present.

        Args:
            draft: The current documentation draft (used for conflict checking).
            llm_output: The full LLM output for the Verify turn, expected to
                contain a ``<score>…</score>`` block.

        Returns:
            :class:`VerifyResult` with ``passed``, ``confidence``, and
            ``observation`` fields.
        """
        # Step 1: Parse LLM self-evaluation scores.
        scores = self._parse_verify_scores(llm_output) # CONSISTENCY, COMPLETENESS, HELPFULNESS
        print(f"Parsed verify scores: {scores}", color="yellow")

        if scores is None:
            if attempt >= 2:
                return VerifyResult(
                    passed=True,
                    confidence=VERIFY_THRESHOLD,
                    observation=(
                        "Verification passed (no <score> block found on 2nd attempt — stub fallback). "
                        "Proceed to Finish."
                    ),
                )
            return VerifyResult(
                passed=False,
                confidence=0.0,
                observation=(
                    "No <SCORE> block found in your response. "
                    "You MUST include a <SCORE> block with CONSISTENCY, COMPLETENESS, and HELPFULNESS scores. "
                    "Please try Verify again with the correct format."
                ),
            )


        # parsing이 잘 되었다면! => 평균값 0~1 사이
        score_average = sum(scores.values()) / len(scores)

        # Step 2: Cross-dependency conflict check.
        # Skipped entirely when --no-conflict-check is active.
        if self.skip_conflict_check:
            has_deps = False
            conflict_score, conflict_report = 1.0, None
            print("[Verify] conflict check SKIPPED (--no-conflict-check)", color="yellow")
        else:
            # COMPONENT: has deps if comp.depends_on is non-empty
            # MODULE: has deps if child_module_paths or component_ids exist
            # REPO: has deps if module_paths or component_ids exist
            if self.task.type == TaskType.COMPONENT:
                comp = self.components.get(self.task.target)
                has_deps = comp is not None and bool(comp.depends_on)
            elif self.task.type == TaskType.MODULE:
                has_deps = bool(self.task.child_module_paths) or bool(self.task.component_ids)
            else:  # REPO
                has_deps = bool(self.task.module_paths) or bool(self.task.component_ids)

            print(f"[Verify] task_type={self.task.type}, target={self.task.target}, has_deps={has_deps}", color="red")
            if has_deps:
                conflict_score, conflict_report = self._check_dependency_conflicts(draft)
            else:
                conflict_score, conflict_report = 0.0, None
            print(f"[Verify] conflict_score={conflict_score:.4f}", color="red")

            conflict_score = 1.0 - conflict_score  # invert so that higher is better, consistent with self-eval scores

        # Step 3: Combine self-eval score and cross-dep conflict score.
        final_score = (score_average*VERIFY_WEIGHTS['INTERNAL'] + conflict_score*VERIFY_WEIGHTS['CROSS']) / 2 if has_deps else score_average*VERIFY_WEIGHTS['INTERNAL']
        print(f"Final score: {final_score:.4f}", color="yellow")

        passed = final_score >= VERIFY_THRESHOLD
        verdict = "PASS" if passed else "REVISE"

        lines = [
            f"Verification {verdict}  (final={final_score:.2f}, threshold={VERIFY_THRESHOLD:.2f})",
            f"  CONSISTENCY  : {scores['CONSISTENCY']:.2f})",
            f"  COMPLETENESS : {scores['COMPLETENESS']:.2f})",
            f"  HELPFULNESS  : {scores['HELPFULNESS']:.2f})"
        ]
        if has_deps:
            lines.append(f"  Dependency Information No-Conflict : {conflict_score:.2f}")
        if conflict_report is not None:
            lines.append("")
            lines.append(conflict_report)
            lines.append("")
            lines.append(
                "Fix the above conflicts by aligning your documentation "
                "with the dependency's documented behavior."
            )

        if passed:
            lines.append("Proceed to FINISH action.")
        else:
            lines.append(
                f"Score {final_score:.2f} is below threshold {VERIFY_THRESHOLD:.2f}. "
                "Revise the documentation."
            )

        return VerifyResult(
            passed=passed,
            confidence=round(final_score, 4),
            observation="\n".join(lines),
            scores=scores,
            weighted_avg=round(score_average, 4),
            conflict_score=round(conflict_score, 4),
        )

    def _parse_verify_scores(self, llm_output: str) -> Optional[Dict[str, float]]:

        score_block = re.search(r"<SCORE>(.*?)</SCORE>", llm_output, re.DOTALL | re.IGNORECASE)
        if not score_block:
            return None
        block = score_block.group(1)

        patterns = {
            "CONSISTENCY": r"<CONSISTENCY>\s*([\d.]+)\s*</CONSISTENCY>",
            "COMPLETENESS": r"<COMPLETENESS>\s*([\d.]+)\s*</COMPLETENESS>",
            "HELPFULNESS": r"<HELPFULNESS>\s*([\d.]+)\s*</HELPFULNESS>",
        }
        scores: Dict[str, float] = {}
        for key, pat in patterns.items():
            m = re.search(pat, block, re.IGNORECASE)
            if m:
                try:
                    scores[key] = max(0.0, min(1.0, float(m.group(1))))
                except ValueError:
                    scores[key] = 0.0

        return scores if len(scores) == 3 else None

    def _check_dependency_conflicts(self, draft: str) -> Tuple[float, Optional[str]]:
        """Compare draft against dependency docs for factual contradictions.

        Uses bidirectional NLI scoring: for each dependency, checks whether
        cross-dep sentences in the draft are supported by the dep doc and
        vice versa. Asymmetric support indicates a conflict.

        Returns: (score, report) where score 0.0 = no conflict, 1.0 = all conflict.
        """
        if not draft:
            return 0.0, None

        # ── Collect source documentation to compare against ───────────
        dep_docs: Dict[str, str] = {}

        if self.task.type == TaskType.COMPONENT:
            comp = self.components.get(self.task.target)
            depends_on: set = comp.depends_on if comp is not None else set()
            for dep_id in sorted(depends_on):
                entry = self.repo_memory.get_component_summary(dep_id)
                if entry is not None and entry.documentation:
                    dep_docs[dep_id] = entry.documentation

        elif self.task.type == TaskType.MODULE:
            for child_mp in sorted(self.task.child_module_paths):
                entry = self.repo_memory.get_module_summary(child_mp)
                if entry is not None and entry.documentation:
                    dep_docs[child_mp] = entry.documentation
            for cid in sorted(self.task.component_ids):
                entry = self.repo_memory.get_component_summary(cid)
                if entry is not None and entry.documentation:
                    dep_docs[cid] = entry.documentation

        else:  # REPO
            for mod_path in sorted(self.task.module_paths):
                entry = self.repo_memory.get_module_summary(mod_path)
                if entry is not None and entry.documentation:
                    dep_docs[mod_path] = entry.documentation
            for cid in sorted(self.task.component_ids):
                entry = self.repo_memory.get_component_summary(cid)
                if entry is not None and entry.documentation:
                    dep_docs[cid] = entry.documentation

        if not dep_docs:
            return 0.0, None

        # ── Bidirectional conflict detection ──────────────────────────
        target_sentences = self._split_doc_sentences(draft)
        print(target_sentences, color="yellow")

        conflict_score, reasons, label_counts = self._evaluate_claim_conflicts(
            target_sentences, dep_docs,
        )
        logger.info("[ConflictCheck] score=%.4f, labels=%s", conflict_score, label_counts)

        if self._analytics is not None:
            self._analytics.log_conflict_stats(
                component_id=self.task.target,
                total_candidate_pairs=sum(label_counts.values()),
                entailment_count=label_counts.get("entailment", 0),
                contradiction_count=label_counts.get("contradiction", 0),
                neutral_count=label_counts.get("neutral", 0),
                conflict_score=conflict_score,
                dep_ids_checked=list(dep_docs.keys()),
            )

        if not reasons:
            return conflict_score, None

        report = (
            f"[CONFLICT] score={conflict_score:.2f}\n"
            + "\n".join(f"  - {r}" for r in reasons)
        )
        return conflict_score, report


    # ------------------------------------------------------------------
    # Sentence extraction (NLI-based conflict detection)
    # ------------------------------------------------------------------

    def _split_doc_sentences(self, doc: str) -> List[str]:
        """Rule-based sentence extraction from documentation (no LLM call).

        Strips section headers and code blocks, then splits on sentence
        boundaries.
        """
        from .nli.text_utils import strip_section_headers, split_sentences
        cleaned = strip_section_headers(doc)
        return split_sentences(cleaned)

    # ------------------------------------------------------------------
    # Cross-dependency conflict evaluation (bidirectional NLI scoring)
    # ------------------------------------------------------------------

    _GENERIC_DEP_SEGMENTS = frozenset({
        "src", "lib", "test", "tests", "spec", "docs", "bin",
        "main", "index", "init", "utils", "helpers", "common",
        "internal", "pkg", "cmd", "app", "unit", "testing",
    })

    @staticmethod
    def _extract_dep_names(dep_id: str) -> Set[str]:
        """Extract the most specific name token from a dependency ID.

        Uses only the last meaningful segment to avoid false matches
        from broad parent names (e.g. 'chatette' matching everything).

        Example: "chatette.tests.unit-testing.parsing" → {"parsing"}
                 "src.agent.worker_agent" → {"worker_agent"}
        """
        parts = dep_id.replace("/", ".").split(".")
        # Walk from the end to find the last non-generic segment
        for p in reversed(parts):
            p = p.strip()
            if p and len(p) > 2 and p.lower() not in WorkerExecutor._GENERIC_DEP_SEGMENTS:
                return {p, p.lower()}
        return set()

    @staticmethod
    def _map_sentences_to_deps(
        target_sentences: List[str],
        dep_ids: List[str],
    ) -> Dict[int, List[str]]:
        """Map each target sentence index to the dep_ids it references.

        Returns:
            {sentence_idx: [dep_id, ...]}. Empty list = no cross-dep reference.
        """
        dep_patterns: List[Tuple[str, re.Pattern]] = []
        for dep_id in dep_ids:
            names = WorkerExecutor._extract_dep_names(dep_id)
            if names:
                alternatives = "|".join(re.escape(n) for n in sorted(names))
                pattern = re.compile(
                    rf"(?:\b(?:{alternatives})\b|(?:{alternatives})[/:])",
                    re.IGNORECASE,
                )
                dep_patterns.append((dep_id, pattern))

        mapping: Dict[int, List[str]] = {}
        for idx, sent in enumerate(target_sentences):
            matched: List[str] = []
            for dep_id, pattern in dep_patterns:
                if pattern.search(sent):
                    matched.append(dep_id)
            mapping[idx] = matched
        return mapping

    def _nli_score(
        self,
        docs: List[str],
        claims: List[str],
    ) -> Tuple[List[str], List[float]]:
        """Score each claim against its corresponding doc using the NLI model.

        Uses the NLI model as a factual-consistency checker:
        premise=doc (full text), hypothesis=claim (single sentence).

        Returns:
            (labels, scores) where labels are NLI label strings and
            scores are the softmax probability of the predicted label.
        """
        from .nli.nli_model import NLIModel

        nli = NLIModel.get_instance(
            model_name=self._nli_config["model"],
            device=self._nli_config.get("device", "cuda:0"),
            batch_size=self._nli_config.get("batch_size", 64),
        )
        labels = nli.predict(premises=docs, hypotheses=claims)
        # Convert labels to binary scores: entailment=1.0, else=0.0
        scores = [1.0 if l == "entailment" else 0.0 for l in labels]
        return labels, scores

    def _evaluate_claim_conflicts(
        self,
        target_sentences: List[str],
        dep_raw_docs: Dict[str, str],
    ) -> Tuple[float, List[str], Dict[str, int]]:
        """Bidirectional NLI conflict evaluation per dependency.

        For each dep, collects cross-dep target sentences and the dep doc,
        then scores in both directions:
          - Direction A: dep_doc supports each target claim?
          - Direction B: target claims support each dep sentence?

        Classification per dep:
          - Both directions supported → relevant (no conflict)
          - Neither direction supported → irrelevant (skip)
          - Asymmetric → conflict candidate

        Returns:
            (score, reasons, label_counts) where score 0.0 = no conflict.
        """
        label_counts: Dict[str, int] = {"entailment": 0, "contradiction": 0, "neutral": 0}

        if not target_sentences or not dep_raw_docs:
            return 0.0, [], label_counts

        sent_to_deps = self._map_sentences_to_deps(
            target_sentences, list(dep_raw_docs.keys()),
        )
        n_specific = sum(1 for v in sent_to_deps.values() if v)
        logger.debug(
            "[ConflictCheck] %d cross-dep sentences, %d general (skipped) / %d total",
            n_specific, len(target_sentences) - n_specific, len(target_sentences),
        )

        all_reasons: List[str] = []
        per_dep_scores: List[float] = []
        threshold = 0.5

        for dep_id, dep_doc in dep_raw_docs.items():
            if not dep_doc:
                continue

            # Collect target sentences that reference this dep
            cross_dep_sents = [
                target_sentences[i]
                for i in range(len(target_sentences))
                if dep_id in sent_to_deps.get(i, [])
            ]
            if not cross_dep_sents:
                continue

            from .nli.text_utils import strip_markdown_noise

            dep_sentences = self._split_doc_sentences(dep_doc)
            if not dep_sentences:
                per_dep_scores.append(0.0)
                continue

            # Use cleaned full text (headers, code blocks, trees removed)
            # as premise for NLI scoring
            dep_full_text = strip_markdown_noise(dep_doc)
            target_cross_text = strip_markdown_noise(" ".join(cross_dep_sents))

            try:
                # Direction A: dep_doc supports each target cross-dep claim?
                labels_a, scores_a = self._nli_score(
                    docs=[dep_full_text] * len(cross_dep_sents),
                    claims=cross_dep_sents,
                )
                # Direction B: target cross-dep text supports each dep sentence?
                labels_b, scores_b = self._nli_score(
                    docs=[target_cross_text] * len(dep_sentences),
                    claims=dep_sentences,
                )

                # Count labels
                for l in labels_a:
                    if l in label_counts:
                        label_counts[l] += 1
                for l in labels_b:
                    if l in label_counts:
                        label_counts[l] += 1

                support_a = sum(scores_a) / len(scores_a)  # target supported by dep
                support_b = sum(scores_b) / len(scores_b)  # dep supported by target

                logger.debug(
                    "[ConflictCheck] dep=%s, support_A=%.2f, support_B=%.2f",
                    dep_id, support_a, support_b,
                )

                if support_a >= threshold and support_b >= threshold:
                    # Both directions supported → relevant, no conflict
                    per_dep_scores.append(0.0)
                elif support_a < threshold and support_b < threshold:
                    # Neither direction → irrelevant, skip
                    per_dep_scores.append(0.0)
                else:
                    # Asymmetric → conflict candidate
                    # Find unsupported target claims that are still related
                    conflict_sents = [
                        (cross_dep_sents[i], scores_a[i])
                        for i in range(len(cross_dep_sents))
                        if scores_a[i] == 0.0
                    ]
                    dep_score = len(conflict_sents) / max(len(cross_dep_sents), 1)
                    per_dep_scores.append(dep_score)

                    # Find the most contradicting dep sentence for each conflict
                    for sent, score in conflict_sents:
                        # Find dep sentence with highest contradiction signal
                        best_dep_sent = ""
                        if dep_sentences:
                            # Re-score this single target claim against each dep sentence
                            try:
                                pair_labels, pair_scores = self._nli_score(
                                    docs=[sent] * len(dep_sentences),
                                    claims=dep_sentences,
                                )
                                # Pick the dep sentence classified as contradiction, or lowest support
                                contra_indices = [j for j, l in enumerate(pair_labels) if l == "contradiction"]
                                if contra_indices:
                                    best_idx = contra_indices[0]
                                else:
                                    best_idx = min(range(len(pair_scores)), key=lambda j: pair_scores[j])
                                best_dep_sent = dep_sentences[best_idx]
                            except Exception:
                                best_dep_sent = dep_sentences[0] if dep_sentences else ""

                        reason = (
                            f"Conflict with [{dep_id}] (support={score:.2f}):\n"
                            f"  YOUR claim : {sent}\n"
                            f"  DEP states : {best_dep_sent}"
                        )
                        all_reasons.append(reason)

            except Exception as exc:
                logger.warning("NLI scoring failed for dep=%s: %s", dep_id, exc)
                per_dep_scores.append(0.0)

        if not per_dep_scores:
            return 0.0, [], label_counts

        avg_score = sum(per_dep_scores) / len(per_dep_scores)
        return max(0.0, avg_score), all_reasons, label_counts

    def _gather_external_info(self, queries: List[str]) -> Dict[str, str]:
        """Gather external information using Perplexity API.

        Args:
            queries: List of search queries.

        Returns:
            Dictionary mapping queries to their responses.
        """
        if not queries:
            return {}
        try:
            perplexity = PerplexityAPI()
            responses = perplexity.batch_query(
                questions=queries,
                system_prompt=(
                    "You are a helpful assistant providing concise and accurate information "
                    "about programming concepts and code. Focus on technical accuracy and clarity."
                ),
                temperature=0.1,
            )
            results: Dict[str, str] = {}
            for query, response in zip(queries, responses):
                results[query] = (
                    response.content
                    if response is not None
                    else "Error: Failed to get response from Perplexity API"
                )
            return results
        except Exception as exc:
            logger.warning("Perplexity API error: %s", exc)
            return {q: f"Error: {exc}" for q in queries}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def execute_write(self, llm_output: str) -> str:
        """Extract ``<DOCUMENTATION>`` block from *llm_output* and store as draft.

        Applies post-processing to strip source code artifacts that the LLM
        may have erroneously included (e.g. ``def …``, triple-quoted
        docstrings, ``return`` statements).
        """
        match = re.search(
            r"<DOCUMENTATION>(.*?)</DOCUMENTATION>", llm_output, re.DOTALL
        )
        if not match:
            return "Write failed: no <DOCUMENTATION>...</DOCUMENTATION> block found."
        raw = match.group(1).strip()
        self._draft = self._clean_draft(raw)
        return "Draft stored. Proceed to Verify."

    @staticmethod
    def _clean_draft(raw: str) -> str:
        """Remove source-code artifacts from a raw documentation draft.

        Handles two common LLM failure modes:
          1. The entire function/class definition is wrapped around the
             docstring (``def … \"\"\"…\"\"\" … return …``).
          2. The docstring is included verbatim with triple quotes but
             without the surrounding code.
        """
        text = raw.strip()

        # Case 1: wrapped in function/class def → extract triple-quoted body
        if re.match(r"^\s*(def |class |async def )", text):
            docstring = re.search(r'(\"\"\"|\'\'\')(.*?)\1', text, re.DOTALL)
            if docstring:
                text = docstring.group(2).strip()
            else:
                # No docstring found inside code block — strip code lines
                lines = text.splitlines()
                text = "\n".join(
                    ln for ln in lines
                    if not re.match(
                        r"^\s*(def |class |async def |return |import |from |pass$|\.\.\.)", ln
                    )
                ).strip()

        # Case 2: bare triple-quoted docstring (no def wrapper)
        bare_docstring = re.match(
            r'^(\"\"\"|\'\'\')(.*?)\1\s*$', text, re.DOTALL
        )
        if bare_docstring:
            text = bare_docstring.group(2).strip()

        # Strip code-fence wrappers (```python ... ```)
        fenced = re.match(r'^```\w*\n(.*?)```\s*$', text, re.DOTALL)
        if fenced:
            text = fenced.group(1).strip()

        return text

    # ------------------------------------------------------------------
    # Finish
    # ------------------------------------------------------------------

    def execute_finish(self, task: WorkerTask, confidence: float) -> str:
        """Persist draft to RepoMemory and return it.

        If no draft has been written, an empty-string documentation is saved
        so that the task still gets an entry in RepoMemory instead of being
        silently dropped.
        """
        if self._draft is None:
            logger.warning(
                "execute_finish called without a draft for '%s' — saving empty doc.",
                task.target,
            )
            self._draft = ""

        if task.type == TaskType.COMPONENT:
            claims = self._split_doc_sentences(self._draft)
            comp = self.components.get(task.target)
            self.repo_memory.set_component_summary(
                component_id=task.target,
                file_path=task.file_path,
                confidence=confidence,
                documentation=self._draft,
                claims=claims,
                component_type=getattr(comp, "component_type", None) if comp else None,
            )
            logger.info("Saved component: %s (confidence=%.2f)", task.target, confidence)
            logger.info("Memory now has %d components: %s", len(self.repo_memory.list_component_ids()), self.repo_memory.list_component_ids())

        elif task.type == TaskType.MODULE:
            claims = self._split_doc_sentences(self._draft)
            self.repo_memory.set_module_summary(
                module_path=task.target,
                documentation=self._draft,
                component_ids=task.component_ids,
                child_module_paths=task.child_module_paths,
                claims=claims,
            )
            logger.info("Saved module: %s (%d components, %d children, %d claims)", task.target, len(task.component_ids), len(task.child_module_paths), len(claims))
            logger.info("Memory now has %d modules: %s", len(self.repo_memory.list_module_paths()), self.repo_memory.list_module_paths())

        elif task.type == TaskType.REPO:
            claims = self._split_doc_sentences(self._draft)
            self.repo_memory.set_repo_summary(
                repo_path=task.target,
                documentation=self._draft,
                module_paths=self.repo_memory.list_module_paths(),
                claims=claims,
            )
            logger.info("Saved repo summary: %s (%d claims)", task.target, len(claims))
            logger.info("Memory now has %d repo summaries: %s", len(self.repo_memory.list_repo_paths()), self.repo_memory.list_repo_paths())
            
        return self._draft



def _build_module_tree(
    module_path: str,
    file_paths: List[str],
    child_module_paths: Optional[List[str]] = None,
) -> str:
    """Return an ASCII tree showing direct files and child module directories.

    Args:
        module_path: Repo-relative directory of the module.
        file_paths:  Repo-relative paths of direct source files in this module.
        child_module_paths: Repo-relative paths of direct child modules.
    """
    module_name = os.path.basename(module_path.rstrip("/\\")) or module_path
    prefix_strip = module_path.replace("\\", "/").rstrip("/") + "/"

    # Build nested dict: dir segments → { ... } ; leaf files → None
    tree: Dict[str, Any] = {}

    # Insert child module directories
    for child_mp in sorted(child_module_paths or []):
        rel = child_mp.replace("\\", "/")
        if rel.startswith(prefix_strip):
            rel = rel[len(prefix_strip):]
        # Ensure the child directory name appears as a dict (directory node)
        tree.setdefault(rel.split("/")[0], {})

    # Insert direct files
    for path in sorted(file_paths):
        rel = path.replace("\\", "/")
        if rel.startswith(prefix_strip):
            rel = rel[len(prefix_strip):]
        parts = rel.split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None  # leaf file

    lines: list[str] = [module_name + "/"]

    def _render(node: Dict[str, Any], prefix: str) -> None:
        dirs  = sorted(k for k, v in node.items() if v is not None)
        files = sorted(k for k, v in node.items() if v is None)
        entries = [(name, True) for name in dirs] + [(name, False) for name in files]
        for index, (name, is_dir) in enumerate(entries):
            connector = "└── " if index == len(entries) - 1 else "├── "
            if is_dir:
                lines.append(f"{prefix}{connector}{name}/")
                extension = "    " if index == len(entries) - 1 else "│   "
                _render(node[name], prefix + extension)
            else:
                lines.append(f"{prefix}{connector}{name}")

    _render(tree, "")
    return "\n".join(lines)


def _build_repo_module_tree(
    repo_name: str,
    module_paths: List[str],
    root_file_paths: Optional[List[str]] = None,
) -> str:
    """Return an ASCII tree showing root modules and top-level files.

    Args:
        repo_name: Repository name (used as tree root label).
        module_paths: Root module directory paths.
        root_file_paths: Repo-relative paths of top-level files not in any module.
    """
    # Build a nested dict: directories → { ... }, files → None
    tree: Dict[str, Any] = {}
    for path in sorted(module_paths):
        node = tree
        for part in path.replace("\\", "/").split("/"):
            node = node.setdefault(part, {})

    # Add top-level files as leaf nodes
    for fp in sorted(root_file_paths or []):
        basename = os.path.basename(fp)
        tree[basename] = None

    lines: list[str] = [repo_name + "/"]

    def _render(node: Dict[str, Any], prefix: str) -> None:
        dirs  = sorted(k for k, v in node.items() if v is not None)
        files = sorted(k for k, v in node.items() if v is None)
        entries = [(name, True) for name in dirs] + [(name, False) for name in files]
        for index, (name, is_dir) in enumerate(entries):
            connector = "└── " if index == len(entries) - 1 else "├── "
            if is_dir:
                lines.append(f"{prefix}{connector}{name}/")
                extension = "    " if index == len(entries) - 1 else "│   "
                _render(node[name], prefix + extension)
            else:
                lines.append(f"{prefix}{connector}{name}")

    _render(tree, "")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# WorkerAgent
# ---------------------------------------------------------------------------

class WorkerAgent(BaseAgent):
    """Single-LLM ReAct agent that documents one WorkerTask at a time.

    Extends BaseAgent (which owns the LLM and conversation memory).
    Shares a RepoMemory instance with ManagerAgent so that completed
    component entries are visible to later workers.
    """

    def __init__(
        self,
        repo_path: str,
        repo_memory: RepoMemory,
        dep_graph: Dict[str, List[str]],
        components: Optional[Dict[str, Any]] = None,
        config_path: Optional[str] = None,
        analytics: Optional[Any] = None,
        skip_conflict_check: bool = False,
        without_memory: bool = False,
        without_think: bool = False,
        without_think2: bool = False,
        ver2_mode: bool = False,
    ) -> None:
        super().__init__("Worker", config_path=config_path)
        self.repo_path = repo_path
        self.repo_memory = repo_memory
        self.dep_graph = dep_graph
        self.components: Dict[str, Any] = components or {}
        self._analytics = analytics
        self.skip_conflict_check = skip_conflict_check
        self.without_memory = without_memory
        self.without_think = without_think
        self.without_think2 = without_think2
        self.ver2_mode = ver2_mode

        cfg = LLMFactory.load_config(config_path or "config/agent_config.yaml")
        worker_cfg = cfg.get("worker", {})
        self.confidence_threshold: float = worker_cfg.get("confidence_threshold", 0.85)
        self.max_turns: int               = worker_cfg.get("max_turns", 10)
        self.max_revisions: int           = worker_cfg.get("max_revisions", 2)
        self._nli_config: Dict[str, Any]  = cfg.get("nli", {})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, task: WorkerTask) -> str:
        """Run the ReAct loop for *task* and return the final documentation.

        Args:
            task: WorkerTask describing the component/module/repo to document.

        Returns:
            Final documentation string persisted to RepoMemory.

        Raises:
            RuntimeError: If the loop exceeds ``max_turns`` without finishing.
        """

        # 현재 component task에 대한 WorkerAgent의 메모리 초기화.
        self.clear_memory()
        executor = WorkerExecutor(
            self.repo_path, self.repo_memory, self.dep_graph, task, self.components,
            analytics=self._analytics,
            llm=self.llm,
            llm_params=self.llm_params,
            nli_config=self._nli_config,
            skip_conflict_check=self.skip_conflict_check,
            without_memory=self.without_memory,
            ver2_mode=self.ver2_mode,
        )

        # 시스템 프롬프트에 task 정보와 의도된 행동 양식 포함. 의존성 정보도 포함하여 LLM이 필요한 컨텍스트를 이해할 수 있도록 함.
        self.add_to_memory("system", self._build_system_prompt(task))

        # Inject pre-loaded source code and imports as the first user turn (COMPONENT tasks only)
        initial_context = self._build_initial_context(task)
        if initial_context:
            self.add_to_memory("user", initial_context)

        confidence: float = 0.0
        revisions:  int   = 0

        # Analytics: start component tracking + LLM snapshot
        if self._analytics is not None:
            self._analytics.start_component(task.target)
            self._analytics.start_task_trajectory(task.type.value, task.target, task.file_path)
        _llm_snapshot: Optional[Dict[str, Any]] = None
        if self._analytics is not None and hasattr(self.llm, "rate_limiter"):
            rl = self.llm.rate_limiter
            _llm_snapshot = {
                "requests": rl.total_requests,
                "input_tokens": rl.total_input_tokens,
                "output_tokens": rl.total_output_tokens,
                "cost": rl.total_cost,
            }

        def _finish_with_analytics(result: str, action_name: str = "Finish") -> str:
            """Wrap execute_finish: record Finish action and end_component."""
            if self._analytics is not None:
                self._analytics.log_agent_call(task.target, action_name, 0.0)
                llm_deltas: Optional[Dict[str, Any]] = None
                if _llm_snapshot is not None and hasattr(self.llm, "rate_limiter"):
                    rl = self.llm.rate_limiter
                    llm_deltas = {
                        "requests": rl.total_requests - _llm_snapshot["requests"],
                        "input_tokens": rl.total_input_tokens - _llm_snapshot["input_tokens"],
                        "output_tokens": rl.total_output_tokens - _llm_snapshot["output_tokens"],
                        "cost": rl.total_cost - _llm_snapshot["cost"],
                    }
                self._analytics.end_component(task.target, llm_deltas)
            return result

        import time as _time
        _verify_attempt: int = 0

        def _get_llm_tokens():
            """Snapshot current total tokens from rate_limiter."""
            rl = getattr(self.llm, "rate_limiter", None)
            if rl:
                return rl.total_input_tokens, rl.total_output_tokens
            return 0, 0

        def _save_current_draft(reason: str, action_name: str = "Finish") -> str:
            """Persist whatever draft exists (or empty) so the task is not dropped."""
            if executor._draft is not None:
                logger.warning(
                    "%s for '%s'. Saving current draft as final documentation.",
                    reason, task.target,
                )
            else:
                logger.warning(
                    "%s for '%s'. No draft was written — saving empty documentation.",
                    reason, task.target,
                )
            return _finish_with_analytics(
                executor.execute_finish(task, confidence), action_name=action_name
            )

        # Wrap the ReAct loop in try/except so any mid-turn exception still
        # falls through to _save_current_draft instead of losing the draft.
        try:
         for turn in range(self.max_turns):
            _t0 = _time.perf_counter()
            _tok_before = _get_llm_tokens()
            llm_output = self.generate_response()

            # without_think2: strip Thought text before storing in memory
            # so the LLM never sees prior Thought in its context window
            if self.without_think2:
                import re as _re
                action_match = _re.search(r'\bAction\s*:', llm_output, _re.IGNORECASE)
                cleaned_output = llm_output[action_match.start():] if action_match else llm_output
                self.add_to_memory("assistant", cleaned_output)
                thought = ""
            elif self.without_think:
                # Legacy partial ablation: store full output but skip thought parsing
                self.add_to_memory("assistant", llm_output)
                thought = ""
            else:
                self.add_to_memory("assistant", llm_output)
                thought = self._parse_thought(llm_output)

            logger.info("[Turn %d/%d] %s", turn + 1, self.max_turns, llm_output)

            action, action_input = self._parse_action(llm_output)

            if action == "Read":
                obs = executor.read_tool(action_input)
                _elapsed = _time.perf_counter() - _t0
                _tok_after = _get_llm_tokens()
                if self._analytics is not None:
                    self._analytics.log_agent_call(
                        task.target, "Read", _elapsed,
                        input_tokens=_tok_after[0] - _tok_before[0],
                        output_tokens=_tok_after[1] - _tok_before[1],
                    )
                    self._analytics.log_trajectory_turn(task.target, turn + 1, thought, action, action_input, obs)
                print(obs, tag="observation", color="yellow", tag_color="blue")

            elif action == "Write":
                obs = executor.execute_write(llm_output)
                _elapsed = _time.perf_counter() - _t0
                _tok_after = _get_llm_tokens()
                if self._analytics is not None:
                    self._analytics.log_agent_call(
                        task.target, "Write", _elapsed,
                        input_tokens=_tok_after[0] - _tok_before[0],
                        output_tokens=_tok_after[1] - _tok_before[1],
                    )
                    self._analytics.log_trajectory_turn(task.target, turn + 1, thought, action, action_input, obs)
                print(obs, tag="observation", color="yellow", tag_color="blue")

            elif action == "Verify":
                _verify_attempt += 1
                vr = executor.verify_tool(executor.draft or "", llm_output, attempt=_verify_attempt)
                _elapsed = _time.perf_counter() - _t0
                _tok_after = _get_llm_tokens()
                if self._analytics is not None:
                    self._analytics.log_agent_call(
                        task.target, "Verify", _elapsed,
                        input_tokens=_tok_after[0] - _tok_before[0],
                        output_tokens=_tok_after[1] - _tok_before[1],
                    )
                    self._analytics.log_verify_scores(
                        component_id=task.target,
                        attempt=_verify_attempt,
                        scores=vr.scores,
                        weighted_avg=vr.weighted_avg,
                        conflict_score=vr.conflict_score,
                        final_score=vr.confidence,
                        passed=vr.passed,
                    )
                passed     = vr.passed
                confidence = vr.confidence
                obs        = vr.observation
                # Store parsed scores in action_input for trajectory logging
                action_input = json.dumps({
                    "scores": vr.scores,
                    "weighted_avg": vr.weighted_avg,
                    "conflict_score": vr.conflict_score,
                    "final_score": vr.confidence,
                    "passed": vr.passed,
                }, ensure_ascii=False) if vr.scores else action_input

                if not passed:
                    if revisions >= self.max_revisions:
                        logger.warning(
                            "Max revisions (%d) reached for '%s'. Forcing finish.",
                            self.max_revisions, task.target,
                        )
                        if self._analytics is not None:
                            self._analytics.log_trajectory_turn(task.target, turn + 1, thought, action, action_input, obs)
                        self.add_to_memory(
                            "user",
                            f"Observation:\n{obs}\n\n"
                            f"[Step {turn+1}/{self.max_turns} | Revisions: {revisions}/{self.max_revisions}]",
                        )
                        self.add_to_memory(
                            "user",
                            "Observation:\nMax revisions reached. Proceed directly to Finish.",
                        )
                        return _finish_with_analytics(executor.execute_finish(task, confidence))
                    else:
                        revisions += 1
                        obs += f"\nRevise the draft (revision {revisions}/{self.max_revisions})."

                if self._analytics is not None:
                    self._analytics.log_trajectory_turn(task.target, turn + 1, thought, action, action_input, obs)
                print(obs, tag="observation", color="cyan", tag_color="blue")

            elif action == "Finish":
                if self._analytics is not None:
                    self._analytics.log_trajectory_turn(task.target, turn + 1, thought, action, action_input, "")
                return _finish_with_analytics(executor.execute_finish(task, confidence))

            else:
                obs = (
                    f"Unknown action '{action}'. "
                    "Valid actions: Read[...], Write, Verify, Finish."
                )
                if self._analytics is not None:
                    self._analytics.log_trajectory_turn(task.target, turn + 1, thought, action, action_input, obs)

            self.add_to_memory(
                "user",
                f"Observation:\n{obs}\n\n"
                f"[Step {turn+1}/{self.max_turns} | Revisions: {revisions}/{self.max_revisions}]",
            )
        except Exception as exc:
            logger.error(
                "ReAct loop raised for '%s': %s — falling back to save-draft.",
                task.target, exc, exc_info=True,
            )
            return _save_current_draft(f"Exception in ReAct loop ({exc})",
                                       action_name="Finish(exception)")

        # Max turns exhausted — always save whatever draft exists (or empty
        # documentation) so the task gets an entry in RepoMemory.
        return _save_current_draft(
            f"Max turns ({self.max_turns}) reached",
            action_name="Finish(max_turns)",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_component_type(self, target: str, file_path: str) -> tuple[str, str]:
        """Return (type_label, format_prompt) for a COMPONENT task target.

        Checks the component registry first (language-agnostic), then falls back
        to Python AST inspection for .py files.
        """
        # Registry-first: works for all languages
        if target in self.components:
            comp_type = self.components[target].component_type
            if comp_type == "class":
                return "class", CLASS_PROMPT
            elif comp_type == "method":
                return "method", METHOD_PROMPT
            else:
                return "function", FUNCTION_PROMPT

        # Python AST fallback
        parts = target.split(".", 1)
        if len(parts) == 2:
            return "method", METHOD_PROMPT
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                source = fh.read()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == parts[0]:
                    return "class", CLASS_PROMPT
                if (
                    isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == parts[0]
                ):
                    return "function", FUNCTION_PROMPT
        except (OSError, SyntaxError):
            pass
        return "function", FUNCTION_PROMPT

    def _build_system_prompt(self, task: WorkerTask) -> str:
        if self.without_think2:
            # Full ablation: use NOTHINK prompt (no Thought instructions at all)
            system_prompt = WORKER_AGENT_SYSTEM_PROMPT_NOTHINK.format(
                max_revisions=self.max_revisions
            )
        else:
            system_prompt = WORKER_AGENT_SYSTEM_PROMPT.format(
                max_revisions=self.max_revisions
            )
        # Legacy partial ablation: just remove Thought line from default prompt
        if self.without_think and not self.without_think2:
            system_prompt = system_prompt.replace(
                "Thought: <your reasoning about what to do next, what information you need>\n        ", ""
            ).replace(
                "For each turn, first think about what you should do, then take exactly one of the four actions below:",
                "For each turn, take exactly one of the four actions below:"
            )
        
        if task.type == TaskType.COMPONENT:
            type_label, format_prompt = self._resolve_component_type(
                task.target, task.file_path
            )
            user_prompt =  COMPONENT_USER_PROMPT.format(
                type=type_label,
                component_name=task.target,
                file_path=task.file_path,
                imports = task.imports,
                source_code = task.source_code,
                format=format_prompt,
            )
            
            system_prompt += user_prompt
            
            logger.info(user_prompt)
            return system_prompt
        
        elif task.type == TaskType.MODULE:
            user_prompt =  MODULE_USER_PROMPT.format(
                module_name=task.target,
                module_tree=_build_module_tree(task.file_path, task.file_paths, task.child_module_paths),
                format=MODULE_PROMPT
            )            
            system_prompt += user_prompt
            logger.info(user_prompt)
            return system_prompt

        else:  # REPO
            user_prompt =  REPO_USER_PROMPT.format(
                repo_name=task.target,
                format=REPO_PROMPT,
                repo_tree=_build_repo_module_tree(
                    task.target,
                    task.module_paths,
                    root_file_paths=sorted({
                        self.components[cid].relative_path
                        for cid in task.component_ids
                        if cid in self.components and self.components[cid].relative_path
                    }) if task.component_ids else None,
                ),
            )
            
            system_prompt += user_prompt

            logger.info(user_prompt)
            return system_prompt

    def _build_initial_context(self, task: WorkerTask) -> Optional[str]:
        """Build a pre-loaded context user-turn for COMPONENT tasks.

        Injects source code and imports pre-populated by ManagerAgent so the
        worker does not need to Read the target component itself.
        Returns None for MODULE/REPO tasks or when neither field is available.
        """
        if task.type != TaskType.COMPONENT:
            return None

        parts: List[str] = ["## Pre-loaded context for this task\n"]

        if task.imports:
            parts.append(
                f"### File-level imports ({task.file_path})\n"
                f"```python\n{task.imports}\n```\n"
            )

        if task.source_code:
            parts.append(
                f"### Target component source code ({task.target})\n"
                f"```python\n{task.source_code}\n```\n"
            )

        if len(parts) == 1:
            return None

        parts.append(
            "The source code and imports above are pre-loaded. "
            "You do not need to Read the target component — focus Read actions on its dependencies."
        )
        return "\n".join(parts)

    def _parse_action(self, llm_output: str) -> Tuple[str, str]:
        """Extract ``(action_name, action_input)`` from *llm_output*.

        Matches (in priority order):
          1. ``Action: READ`` followed by ``<RETRIEVE>…</RETRIEVE><REQUEST>…</REQUEST>``
             (primary format defined in WORKER_AGENT_SYSTEM_PROMPT)
          2. ``Action: READ`` with only ``<RETRIEVE>…</RETRIEVE>`` and no ``<REQUEST>``
             (LLM deviation — treated as READ with empty request)
          3. ``Action: Name[input]`` bracket form (legacy fallback)
          4. Bare ``Action: Name`` for Write / Verify / Finish

        Returns ``('Unknown', '')`` when no pattern matches.
        """
        # 1. READ: full XML block <RETRIEVE>…<REQUEST>…</REQUEST>
        xml_match = re.search(
            r"Action\s*:\s*READ\b(.*?</REQUEST>)",
            llm_output,
            re.IGNORECASE | re.DOTALL,
        )
        if xml_match:
            return "Read", xml_match.group(1).strip()

        # 2. READ: only <RETRIEVE> tag present (no <REQUEST> block)
        retrieve_only = re.search(
            r"Action\s*:\s*READ\b.*?(<RETRIEVE>.*?</RETRIEVE>)",
            llm_output,
            re.IGNORECASE | re.DOTALL,
        )
        if retrieve_only:
            return "Read", retrieve_only.group(1).strip()

        # 3. Legacy bracket form — normalize action name to Title-case
        bracket = re.search(
            r"Action\s*:\s*(\w+)\s*\[([^\]]*)\]", llm_output, re.IGNORECASE
        )
        if bracket:
            return bracket.group(1).strip().capitalize(), bracket.group(2).strip()

        # 4. Write / Verify / Finish / Read (bare, no body)
        no_bracket = re.search(
            r"Action\s*:\s*(Read|Write|Verify|Finish)\b", llm_output, re.IGNORECASE
        )
        if no_bracket:
            return no_bracket.group(1).strip().capitalize(), ""

        # 5. Fallback: LLM omitted "Action:" but produced known output tags
        if re.search(r"<DOCUMENTATION>.*?</DOCUMENTATION>", llm_output, re.DOTALL):
            return "Write", ""
        if re.search(r"<SCORE>.*?</SCORE>", llm_output, re.DOTALL | re.IGNORECASE):
            return "Verify", ""

        return "Unknown", ""

    def _parse_thought(self, llm_output: str) -> str:
        """Extract the Thought portion from *llm_output* (text before Action:).

        Handles both ``\\n`` and ``\\r\\n`` line endings.
        """
        match = re.search(
            r"Thought\s*:\s*(.*?)(?=\r?\nAction\s*:|\Z)", llm_output, re.DOTALL | re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
        return ""
