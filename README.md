# MemDocAgent

MemDocAgent is a framework for automatically generating high-quality documentation for software repositories. It uses a **Manager/Worker agent architecture** with a ReAct-based loop to produce documentation at three hierarchical levels: component (functions, methods, classes), module (packages/directories), and repository.

## Key Features

- **Multi-language support**: Python, JavaScript, TypeScript, Java, C++, C, C#, PHP, Kotlin (via tree-sitter)
- **Dependency-aware ordering**: documents dependencies before the components that depend on them (topological order)
- **Iterative verification**: each component is self-scored on Consistency, Completeness, and Helpfulness before being saved
- **Multiple LLM backends**: OpenAI, Claude (Anthropic), Gemini, vLLM-hosted local models, HuggingFace
- **Optional NLI conflict detection**: flags contradictions across related documentation entries

## Installation

```bash
pip install -r requirements.txt
```

Install only the LLM provider(s) you need — `anthropic`, `openai`, or `google-generativeai`. `transformers` and `torch` are only needed for the NLI conflict-detection feature or local model inference.

## Configuration

```bash
cp config/example_config.yaml config/agent_config.yaml
# Edit agent_config.yaml: set llm.type and llm.api_key
```

`config/example_config.yaml` shows all options. The active config (`agent_config.yaml`) is `.gitignore`d to prevent accidentally committing API keys.

### Supported LLM types

| `llm.type` | Notes |
|------------|-------|
| `openai`   | Also works with any OpenAI-compatible endpoint (e.g., vLLM) |
| `claude`   | Anthropic API |
| `gemini`   | Google Generative AI API |
| `huggingface` | HuggingFace Inference API or local endpoint |
| `local`    | Direct local model loading via transformers |

## Usage

### Single repository

```bash
./run.sh --repo-path /path/to/your/repo
```

Or call `main.py` directly for full control:

```bash
python main.py \
  --repo-path /path/to/your/repo \
  --config-path config/agent_config.yaml \
  --output-dir ./output \
  --mode default
```

### Batch processing (multiple repositories)

Edit the `REPOS` list in `main.sh`, set `SOURCE_ROOT`, then run:

```bash
SOURCE_ROOT=/path/to/repos OUTPUT_DIR=./output bash main.sh
```

For a different LLM backend:

```bash
MODEL_TAG=Llama-3.3-70B SOURCE_ROOT=/path/to/repos bash main.sh
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--repo-path` | (required) | Repository to document |
| `--config-path` | `config/agent_config.yaml` | YAML config file |
| `--output-dir` | `./output` | Root output directory |
| `--mode` | `default` | Ablation mode (see below) |
| `--no-conflict-check` | off | Skip NLI cross-dependency verification |
| `--log-level` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### `--mode` ablation settings

| Mode | Behavior |
|------|----------|
| `default` | Full pipeline |
| `only_self` | Self-consistency verification only (no NLI conflict check) |
| `without_memory` | Always re-reads source; skips RepoMemory retrieval |
| `without_think` | Hides Thought step in prompt but still generates it |
| `without_think2` | Removes Thought generation entirely |
| `ver2` | Strips docs to essential sections; simple code passthrough |

## Output

```
output/
├── documentation/<repo>/
│   ├── documentation.json      # Full structured documentation
│   ├── README.md               # Repository-level overview
│   └── <module>.md             # Module-level documentation
├── dependency_graphs/<repo>/
│   └── <repo>_dependency_graph.json
└── analytics/<repo>/
    ├── run_<timestamp>.json        # Per-component action stats
    ├── llm_stats_<timestamp>.json  # Token usage and cost
    └── trajectory_<timestamp>.json # Turn-by-turn ReAct trace
```

## Architecture Overview

```
DependencyParser          → parses source files into CodeComponent objects
    ↓                       (multi-language via tree-sitter)
TopologicalSorter         → orders components: dependencies first
    ↓                       (Tarjan's algorithm for cycle detection)
ManagerAgent              → dispatches WorkerTask objects in topo order
    ↓
WorkerAgent (ReAct loop)  → for each task:
    READ   fetch source, imports, dependency docs from RepoMemory
    WRITE  generate documentation via LLM
    VERIFY self-score (Consistency / Completeness / Helpfulness ≥ 0.90)
    FINISH commit to RepoMemory
    ↓
RepoMemory + MarkdownExporter → persist and export all documentation
```

### Hierarchical documentation

Each component's documentation is written first; modules are documented after all their components are done; the repository entry is written last. This ensures every level has full context from the level below.

## Local LLM (vLLM)

Scripts in `tool/` launch OpenAI-compatible vLLM servers for various models:

```bash
# Start server (GPU 0, port 8000)
bash tool/serve_local_llm.sh

# Then run the pipeline pointing at the local endpoint
python main.py --repo-path /path/to/repo --config-path config/agent_config.yaml
# (agent_config.yaml must set llm.type: "openai" with api_base: "http://localhost:8000/v1")
```

## Resuming interrupted runs

If a run is interrupted after components are done but before modules/repo:

```bash
# Resume from module level onward
python resume_module_repo.py --repo-path /path/to/repo --output-dir ./output

# Resume only the repository-level entry
python resume_repo.py --repo-path /path/to/repo --output-dir ./output
```

## Utilities

Remove existing docstrings from a repository (useful before benchmarking):

```bash
bash tool/remove_docstrings.sh /path/to/repo
bash tool/remove_docstrings.sh --dry-run /path/to/repo   # preview only
bash tool/remove_docstrings.sh --backup /path/to/repo    # create .bak files first
```
