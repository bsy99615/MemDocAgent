#!/bin/bash
# vLLM server for ChatLLM pipeline (separate from main pipeline)
# Uses GPU 7, port 8001 to avoid conflict with main server on port 8000

CUDA_VISIBLE_DEVICES=7 python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-Coder-30B-A3B-Instruct \
  --tensor-parallel-size 1 \
  --dtype float16 \
  --gpu-memory-utilization 0.9 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8001
