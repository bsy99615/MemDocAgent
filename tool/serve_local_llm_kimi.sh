#!/bin/bash
# vLLM OpenAI-compatible API server for moonshotai/Kimi-K2-Instruct
# Prerequisites: conda activate codedoc
# Uses GPU 6, port 8000 (same as serve_local_llm.sh — 동시에 실행 불가)

CUDA_VISIBLE_DEVICES=6 python -m vllm.entrypoints.openai.api_server \
  --model moonshotai/Kimi-K2-Instruct \
  --tensor-parallel-size 1 \
  --dtype float16 \
  --gpu-memory-utilization 0.9 \
  --enforce-eager \
  --host 0.0.0.0 \
  --port 8000
