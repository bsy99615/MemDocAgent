#!/bin/bash
# MemDocAgent — generate documentation for a single repository
#
# Usage:
#   ./run.sh --repo-path <PATH> [options]
#
# Prerequisites:
#   1. pip install -r requirements.txt
#   2. cp config/example_config.yaml config/agent_config.yaml
#      (then edit agent_config.yaml to add your API key)
#
# Examples:
#   ./run.sh --repo-path /path/to/your/repo
#   ./run.sh --repo-path /path/to/your/repo --output-dir ./output
#   ./run.sh --repo-path /path/to/your/repo --mode default --no-conflict-check
#
# Options (passed directly to main.py):
#   --repo-path PATH        Path to the repository to document (required)
#   --config-path PATH      Config file path (default: config/agent_config.yaml)
#   --output-dir DIR        Output directory (default: ./output)
#   --mode MODE             Ablation mode: default | only_self | without_memory |
#                           without_think | without_think2 | ver2 (default: default)
#   --no-conflict-check     Skip cross-dependency NLI conflict verification (faster)
#   --log-level LEVEL       DEBUG | INFO | WARNING | ERROR (default: INFO)

set -e

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 --repo-path <PATH> [options]"
    echo "Run '$0 --help' or see main.py for full option list."
    exit 1
fi

python main.py "$@"
