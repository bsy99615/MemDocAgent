#!/bin/bash
# MemDocAgent — batch documentation generation for multiple repositories
#
# Environment variables:
#   SOURCE_ROOT — directory containing the target repositories (required)
#   OUTPUT_DIR  — output directory (default: ./output)
#   MODE        — ablation mode (default: "default")
#   MODEL_TAG   — LLM backend tag (default: "Qwen3-Coder")
#                 Llama-3.3-70B  → serve_local_llm_llama.sh   + agent_config_llama.yaml
#                 Kimi-K2        → serve_local_llm_kimi.sh    + agent_config_kimi.yaml
#                 GPT-OSS-120B   → serve_local_llm_gpt_oss.sh + agent_config_gpt_oss.yaml
#                 Gemini         → no vLLM needed, uses Gemini API directly
set -e

MODEL_TAG="${MODEL_TAG:-Qwen3-Coder}"

case "$MODEL_TAG" in
  Llama-3.3-70B)
    NEED_VLLM=true
    SERVE_SCRIPT="tool/serve_local_llm_llama.sh"
    CONFIG_PATH="config/agent_config_llama.yaml"
    ;;
  Kimi-K2)
    NEED_VLLM=true
    SERVE_SCRIPT="tool/serve_local_llm_kimi.sh"
    CONFIG_PATH="config/agent_config_kimi.yaml"
    ;;
  GPT-OSS-120B)
    NEED_VLLM=true
    SERVE_SCRIPT="tool/serve_local_llm_gpt_oss.sh"
    CONFIG_PATH="config/agent_config_gpt_oss.yaml"
    ;;
  Gemini)
    NEED_VLLM=false
    CONFIG_PATH="config/agent_config_gemini.yaml"
    ;;
  *)
    NEED_VLLM=true
    SERVE_SCRIPT="tool/serve_local_llm.sh"
    CONFIG_PATH="config/agent_config.yaml"
    MODEL_TAG="Qwen3-Coder"
    ;;
esac

# ── vLLM server (only when NEED_VLLM=true) ──────────────────────────
SERVER_PID=""
if $NEED_VLLM; then
    echo "[1/3] Starting vLLM server (${MODEL_TAG} / port 8000)..."
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "  → vLLM server already running"
    else
        bash "$SERVE_SCRIPT" &
        SERVER_PID=$!

        echo "[2/3] Waiting for server to be ready..."
        MAX_WAIT=300
        WAITED=0
        until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
            if [ $WAITED -ge $MAX_WAIT ]; then
                echo "ERROR: vLLM server did not become ready within ${MAX_WAIT}s." >&2
                kill $SERVER_PID 2>/dev/null
                exit 1
            fi
            sleep 3
            WAITED=$((WAITED + 3))
        done
        echo "  → Server ready (${WAITED}s elapsed)"
    fi
else
    echo "[1/3] API mode — no vLLM server needed (${MODEL_TAG})"
fi

echo "[3/3] Running pipeline..."

# ── Target repositories ───────────────────────────────────────────────
if [ -z "$SOURCE_ROOT" ]; then
    echo "ERROR: SOURCE_ROOT environment variable is required." >&2
    echo "  Set it to the directory containing your target repositories." >&2
    echo "  Example: SOURCE_ROOT=/path/to/repos bash main.sh" >&2
    exit 1
fi

MODE="${MODE:-default}"
OUTPUT_DIR="${OUTPUT_DIR:-./output}"

REPOS=(
    "Communications/Wikipedia-API"
    "Database/bplustree"
    "Internet/Jinja2"
    "Multimedia/hypertools"
    "Scientific-Engineering/csvkit"
    "Security/zxcvbn-python"
    "Software-Development/PySnooper"
    "System/exodus-bundler"
    "Text-Processing/parsel"
    "Utilities/mackup"
)

TOTAL=${#REPOS[@]}
COUNT=0
FAILED=()

echo "=== Target repos: ${TOTAL} ==="
echo "  Source : ${SOURCE_ROOT}"
echo "  Output : ${OUTPUT_DIR}"
echo "  Mode   : ${MODE}"
echo "  Model  : ${MODEL_TAG}"
echo "  Config : ${CONFIG_PATH}"

for repo in "${REPOS[@]}"; do
    COUNT=$((COUNT + 1))
    REPO_PATH="${SOURCE_ROOT}/${repo}"
    REPO_NAME=$(basename "$REPO_PATH")
    echo "========== [$COUNT/$TOTAL] ${REPO_NAME} (${repo}) =========="

    if python main.py --repo-path "$REPO_PATH" --output-dir "$OUTPUT_DIR" --mode "$MODE" --config-path "$CONFIG_PATH"; then
        echo "  → $repo done"
    else
        echo "  → $repo failed" >&2
        FAILED+=("$repo")
    fi
    echo ""
done

echo "========== Summary =========="
echo "$((TOTAL - ${#FAILED[@]})) / $TOTAL succeeded"
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "Failed:"
    for f in "${FAILED[@]}"; do
        echo "  - $f"
    done
fi

# Cleanup: kill the entire process tree (vLLM spawns tensor-parallel workers)
if [ -n "$SERVER_PID" ]; then
    echo "Shutting down vLLM server..."
    pkill -TERM -P $SERVER_PID 2>/dev/null || true
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
fi
echo "Done."
