#!/bin/bash
# vLLM OpenAI-compatible API server for openai/gpt-oss-120b
# Prerequisites: conda activate codedoc
# MoE: 117B total / 5.1B active — fits in a single 80GB GPU
# Uses GPU 6 (tensor-parallel-size 1), GPU 7 free for NLI, port 8000

CUDA_VISIBLE_DEVICES=6 python -m vllm.entrypoints.openai.api_server \
  --model openai/gpt-oss-120b \
  --tensor-parallel-size 1 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 65536 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8000
