# Copyright (c) Meta Platforms, Inc. and affiliates
import re
import logging
from typing import List, Dict, Any, Optional

from .base import BaseLLM

logger = logging.getLogger(__name__)


class LocalLLM(BaseLLM):
    """Local GPU model wrapper using HuggingFace transformers (direct loading)."""

    _THINK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)
    _THINK_OPEN_PATTERN = re.compile(r"<think>.*$", re.DOTALL)

    def __init__(
        self,
        model_name: str,
        torch_dtype: str = "bfloat16",
        device_map: str = "auto",
        enable_thinking: bool = False,
        max_input_tokens: int = 32000,
        max_output_tokens: int = 4096,
    ) -> None:
        """Initialize LocalLLM by loading the model directly onto GPU.

        Args:
            model_name: HuggingFace model name or local path
            torch_dtype: Torch dtype string for model weights (e.g. "bfloat16")
            device_map: Device map for model placement (e.g. "auto")
            enable_thinking: Whether to enable thinking mode (Qwen3 style)
            max_input_tokens: Maximum number of input tokens allowed
            max_output_tokens: Maximum number of output tokens to generate
        """
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self._torch = torch  # keep reference so generate() can use it without re-importing
        self.model_name = model_name
        self.torch_dtype = getattr(torch, torch_dtype, torch.bfloat16)
        self.device_map = device_map
        self.enable_thinking = enable_thinking
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens

        logger.info(f"Loading tokenizer: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        logger.info(f"Loading model: {model_name} (dtype={torch_dtype}, device_map={device_map})")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=self.torch_dtype,
                device_map="auto",
                trust_remote_code=True,
            )
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

        self.model.eval()

    def _count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens for a list of messages using the HuggingFace tokenizer.

        Args:
            messages: List of message dictionaries

        Returns:
            Token count
        """
        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback: sum per-message token counts + overhead
            total = sum(
                len(self.tokenizer.encode(m["content"])) for m in messages
            )
            total += 4 * len(messages)
            return total

    def _truncate_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Truncate messages to stay within max_input_tokens.

        System messages are always preserved. Non-system messages are added
        newest-first until the budget is exhausted.

        Args:
            messages: List of message dictionaries

        Returns:
            Truncated list of message dictionaries
        """
        if not messages:
            return []

        system_messages = [m for m in messages if m["role"].lower() == "system"]
        non_system_messages = [m for m in messages if m["role"].lower() != "system"]

        result = system_messages.copy()
        token_budget = self.max_input_tokens - self._count_messages_tokens(result)

        for message in reversed(non_system_messages):
            message_tokens = self._count_messages_tokens([message])

            if message_tokens <= token_budget:
                result.insert(len(system_messages), message)
                token_budget -= message_tokens
            elif message["role"].lower() == "user" and token_budget > 20:
                content = message["content"]
                keep_ratio = token_budget / message_tokens
                if keep_ratio < 0.5:
                    truncated_content = (
                        f"[...truncated...] "
                        f"{content[int(len(content) * (1 - keep_ratio + 0.1)):].strip()}"
                    )
                else:
                    truncated_content = content[int(len(content) * (1 - keep_ratio)):].strip()

                truncated_message = {"role": message["role"], "content": truncated_content}
                truncated_tokens = self._count_messages_tokens([truncated_message])
                if truncated_tokens <= token_budget:
                    result.insert(len(system_messages), truncated_message)
                    token_budget -= truncated_tokens

            if token_budget <= 20:
                break

        result.sort(key=lambda m: 0 if m["role"].lower() == "system" else 1)
        return result

    def _strip_thinking_tags(self, text: str) -> str:
        """Remove <think>...</think> blocks from generated text.

        Also removes incomplete opening <think> blocks that extend to end-of-string.

        Args:
            text: Raw model output

        Returns:
            Cleaned text
        """
        text = self._THINK_PATTERN.sub("", text)
        text = self._THINK_OPEN_PATTERN.sub("", text)
        return text.strip()

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response by running inference on the local GPU model.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0 = greedy)
            max_output_tokens: Maximum output tokens; falls back to self.max_output_tokens
            max_tokens: Alias for max_output_tokens (backward compat)

        Returns:
            Generated response text
        """
        effective_max_out = max_output_tokens or max_tokens or self.max_output_tokens

        if self._count_messages_tokens(messages) > self.max_input_tokens:
            messages = self._truncate_messages(messages)

        # Apply chat template
        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=self.enable_thinking,
            )
        except TypeError:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        input_len = model_inputs["input_ids"].shape[1]

        torch = self._torch
        generated_ids = None
        try:
            with torch.no_grad():
                if temperature == 0:
                    generated_ids = self.model.generate(
                        **model_inputs,
                        max_new_tokens=effective_max_out,
                        temperature=None,
                        do_sample=False,
                        pad_token_id=self.tokenizer.pad_token_id,
                    )
                else:
                    generated_ids = self.model.generate(
                        **model_inputs,
                        max_new_tokens=effective_max_out,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id,
                    )

            output_ids = generated_ids[0][input_len:]
            response_text = self.tokenizer.decode(output_ids, skip_special_tokens=True)

            if not self.enable_thinking:
                response_text = self._strip_thinking_tags(response_text)

            return response_text
        finally:
            del model_inputs
            if generated_ids is not None:
                del generated_ids
            torch.cuda.empty_cache()

    def format_message(self, role: str, content: str) -> Dict[str, str]:
        """Format a message dictionary.

        Args:
            role: Message role (system, user, assistant)
            content: Message content

        Returns:
            Formatted message dictionary
        """
        return {"role": role, "content": content}
