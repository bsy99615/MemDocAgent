#!/bin/bash
# vLLM OpenAI-compatible API server for meta-llama/Llama-3.3-70B-Instruct
# Prerequisites: conda activate codedoc
# Uses GPU 6,7 (tensor-parallel-size 2), port 8000

CUDA_VISIBLE_DEVICES=6,7 python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.3-70B-Instruct \
  --tensor-parallel-size 2 \
  --dtype float16 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 65536 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8000
