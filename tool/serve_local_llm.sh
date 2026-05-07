#!/bin/bash
# vLLM OpenAI-compatible API server for Qwen3-Coder-30B-A3B-Instruct
# Prerequisites: conda activate codedoc
# Uses GPUs 6,7 (matching project .envrc)

CUDA_VISIBLE_DEVICES=6 python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-Coder-30B-A3B-Instruct \
  --tensor-parallel-size 1 \
  --dtype float16 \
  --gpu-memory-utilization 0.9 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8000
