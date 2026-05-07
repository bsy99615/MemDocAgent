# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MemDocAgent is a repository-level documentation framework that automatically generates documentation for multi-language codebases using a Manager/Worker agent architecture with LLMs. It operates at three hierarchical levels: component (functions/classes), module (packages/directories), and repository.

## Commands

### Run documentation generation
```bash
python main.py --repo-path <PATH_TO_REPO> [--config-path config/agent_config.yaml] [--output-dir ./output] [--mode default]
```

Key flags:
- `--no-conflict-check`: Skip cross-dependency NLI conflict verification (faster)
- `--mode`: Ablation mode — `default`, `only_self`, `without_memory`, `without_think`, `without_think2`, `ver2`
- `--log-level`: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Batch processing (DevEval repos)
```bash
MODE=default MODEL_TAG="claude-3-5-haiku" bash main.sh
```

### Resume interrupted runs
```bash
python resume_repo.py        # Resume repo-level processing
python resume_module_repo.py # Resume module-level processing
```

### Remove existing docstrings from a repo (for clean benchmarking)
```bash
python tool/remove_docstrings.py --repo-path <PATH>
```

### Start a local vLLM server
```bash
bash tool/serve_local_llm.sh
```

### Install dependencies
```bash
pip install -r requirements.txt
```

There is no test suite or linter configured in this repo.

## Configuration

Copy and edit `config/example_config.yaml` to `config/agent_config.yaml`. Key sections:

- `llm.type`: `claude`, `openai`, `gemini`, `huggingface`, or `local`
- `rate_limits.<provider>`: RPM, input/output token limits, per-million token prices
- `flow_control.max_verifier_rejections`: How many VERIFY failures before accepting anyway
- `docstring_options.overwrite_docstrings`: Whether to replace existing docstrings

## Architecture

### Five-layer pipeline

1. **DependencyParser** (`src/dependency_analyzer/`) — Scans repo files, builds `CodeComponent` objects using tree-sitter language analyzers, and extracts cross-component dependency edges.

2. **Topological Sorter** (`src/dependency_analyzer/topo_sort.py`) — Runs Tarjan's algorithm to detect/break cycles, then produces a processing order where dependencies are documented before their dependents.

3. **ManagerAgent** (`src/agent/manager_agent.py`) — Orchestrates the full pipeline. Iterates over topo-sorted components, then aggregates into modules, then into a repo-level entry. Dispatches `WorkerTask` objects and writes results to `RepoMemory`. Also drives analytics logging.

4. **WorkerAgent + WorkerExecutor** (`src/agent/worker_agent.py`) — Implements a ReAct loop (Thought → Action → Observation) for each task. Four actions:
   - **READ**: Fetches source code, imports, dependency docs from `RepoMemory`, or runs a web search via Perplexity API
   - **WRITE**: Generates documentation (Google docstring format, no markdown fences) via the configured LLM
   - **VERIFY**: Self-scores on Consistency / Completeness / Helpfulness (threshold 0.90); optionally runs NLI conflict detection against related component docs
   - **FINISH**: Commits result to `RepoMemory` and ends the loop

5. **RepoMemory** (`src/memory/repo_memory.py`) — Shared in-memory store across all workers. Holds `ComponentEntry`, `ModuleEntry`, and `RepoEntry` objects. Also caches web search results. Exports final output as JSON + hierarchical Markdown.

### LLM layer

`src/agent/llm/factory.py` uses a factory pattern to instantiate provider-specific LLM classes (all subclass `BaseLLM`). `RateLimiter` (`rate_limiter.py`) enforces per-minute RPM and token quotas with sliding-window tracking.

### Key data structures

- **`CodeComponent`** — One documented unit: `id` (dot-path like `src.agent.ManagerAgent.run`), `source_code`, `depends_on: Set[str]`, `language`, `component_type`
- **`WorkerTask`** — Task dispatched to a worker: `type` (COMPONENT / MODULE / REPO), `target`, source paths, constituent component IDs
- **`ComponentEntry`** — Memory store record: `documentation`, `confidence` (verification score), `claims` (atomic facts extracted from docs)
- **`VerifyResult`** — Output of VERIFY action: `passed`, `confidence`, per-criterion `scores`, optional `conflict_score`

### Output structure

```
output/
├── documentation/<repo>/   # documentation.json + per-module .md files
├── dependency_graphs/<repo>/  # <repo>_dependency_graph.json
└── analytics/<repo>/       # run_*.json, llm_stats_*.json, trajectory_*.json
```

### Multi-language support

Supported via tree-sitter: Python, JavaScript, TypeScript, Java, C++, C, C#, PHP, Kotlin. Each language has a dedicated analyzer in `src/dependency_analyzer/analyzers/` that returns normalized `Node` and `CallRelationship` objects.

### Ablation modes (`--mode`)

| Mode | Effect |
|------|--------|
| `default` | Full pipeline |
| `only_self` | Self-consistency verification only (no NLI conflict check) |
| `without_memory` | Always re-reads source; skips RepoMemory retrieval |
| `without_think` | Hides Thought from prompt but still generates it |
| `without_think2` | Disables Thought generation entirely (NOTHINK prompt) |
| `ver2` | Strips docs to essential sections; uses simple code passthrough |
