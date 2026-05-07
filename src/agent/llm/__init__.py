# Copyright (c) Meta Platforms, Inc. and affiliates
from .base import BaseLLM
from .openai_llm import OpenAILLM
from .claude_llm import ClaudeLLM
from .huggingface_llm import HuggingFaceLLM
from .gemini_llm import GeminiLLM
from .factory import LLMFactory

# LocalLLM imports torch/transformers on instantiation — not at module level.
# Import lazily to avoid errors in environments without GPU dependencies.
def __getattr__(name):
    if name == "LocalLLM":
        from .local_llm import LocalLLM
        return LocalLLM
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'BaseLLM',
    'OpenAILLM',
    'ClaudeLLM',
    'HuggingFaceLLM',
    'GeminiLLM',
    'LocalLLM',
    'LLMFactory'
] 