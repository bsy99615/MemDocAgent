# `docs.tutorials`

## Tree:
tutorials/
└── tools/
    └── nb_to_doc.py

## Role:
Provide a single, reusable utility that converts a Jupyter notebook basename into documentation artifacts by running a fixed sequence of nbconvert CLI commands.

## Description:
Where and when this module is used
- Primary consumers:
  - Documentation build scripts and tutorial conversion tooling (CI jobs or local doc generation) that convert .ipynb tutorial notebooks into reStructuredText and normalize notebook outputs for repository consistency.
  - Ad-hoc maintenance or developer scripts used by maintainers to batch-convert notebooks before publishing docs.
- Typical usage scenario:
  - A docs-generation script iterates notebook basenames and calls convert_nb for each to: 1) execute the notebook in-place, 2) export the executed notebook to reStructuredText (.rst), and 3) clear outputs so the repository stores cleaned notebooks.

Why these components are grouped here
- Cohesion principle: encapsulates the exact nbconvert command sequence and options (execute → export → clear) so callers do not duplicate command construction or ordering.
- Layer boundary: belongs to documentation tooling/utilities. It delegates process execution to a provided process-runner callable rather than implementing low-level process management itself.

## Components:
- convert_nb(nbname: str) -> None
  - Orchestrates three sequential jupyter nbconvert invocations for the given notebook basename: execute in-place, export to reStructuredText, then clear outputs in-place. See component-level documentation: docs.tutorials.tools.nb_to_doc.convert_nb

Mermaid dependency graph:
flowchart TD
    convert_nb["convert_nb(nbname)"]
    sh_helper["sh (callable injected into module/global scope)"]
    jupyter["jupyter nbconvert (external CLI)"]
    notebook["<nbname>.ipynb (filesystem)"]
    rstfile["<nbname>.rst (filesystem)"]

    convert_nb --> sh_helper
    sh_helper --> jupyter
    convert_nb --> notebook
    convert_nb --> rstfile

## Public API:
- convert_nb(nbname: str) -> None
  - Description: Execute nbname + ".ipynb" in-place, export it to nbname + ".rst" using jupyter nbconvert, then clear outputs in-place. Each step is performed by invoking the external jupyter CLI through a process-runner callable named sh that must be present at runtime.
  - Usage notes:
    - nbname must be the notebook basename without the ".ipynb" extension (e.g., "intro", not "intro.ipynb").
    - A callable named sh must be present in the module/global scope before calling convert_nb (see Dependencies). convert_nb propagates any exceptions raised by sh.
    - Returns None on success; exceptions indicate failure (e.g., subprocess.CalledProcessError, FileNotFoundError).
  - Link to component docs: docs.tutorials.tools.nb_to_doc.convert_nb

## Dependencies:
- Internal (repository) dependencies:
  - The module does not import other repository modules. Instead, it requires a runtime-injected callable named sh (a process-runner) to execute CLI commands. Callers should inject this helper into the module namespace (for example: import tutorials.tools.nb_to_doc as t; t.sh = my_sh_callable).
- External (system / third-party) dependencies:
  - jupyter nbconvert (part of the Jupyter toolchain) must be installed and available on the process PATH. The module constructs nbconvert CLI invocations; the sh callable executes them.

Expected contract for the sh callable:
- Signature: sh(cmd_tokens)
  - cmd_tokens: sequence (list or tuple) of command tokens, e.g. ["jupyter", "nbconvert", "--to", "rst", "file.ipynb"]
- Behavior:
  - Runs the command synchronously.
  - Returns on success or raises an exception on failure (e.g., subprocess.CalledProcessError, OSError).
- convert_nb does not inspect or modify stdout/stderr; any logging or output handling should be implemented by the injected sh helper.

## Constraints:
- Caller responsibilities:
  - Provide nbname without the ".ipynb" suffix. Passing a name that already ends with ".ipynb" will create an incorrect filename like "file.ipynb.ipynb".
  - Ensure the sh callable is assigned into the module/global scope before calling convert_nb (for example: import tutorials.tools.nb_to_doc as t; t.sh = my_sh_fn).
  - Ensure the working directory or resolved paths contain nbname + ".ipynb".
  - Ensure jupyter nbconvert is installed and reachable on PATH; otherwise the process-runner will fail.
- Concurrency and ordering:
  - The function mutates files on disk in a three-step sequence (execute → export .rst → clear outputs). Do not run simultaneous convert_nb calls against the same notebook basename without external coordination — this can cause race conditions and inconsistent files.
  - Running convert_nb concurrently for different notebook basenames is acceptable provided the process-runner and filesystem permit parallel processes.
- Error handling:
  - convert_nb does not catch or wrap exceptions from sh. Callers must handle exceptions to implement retries, logging, or abort behavior.
- Postconditions on success:
  - A file named nbname + ".rst" is created or overwritten.
  - The source notebook nbname + ".ipynb" is executed and then cleared of outputs.
  - The function returns None.

