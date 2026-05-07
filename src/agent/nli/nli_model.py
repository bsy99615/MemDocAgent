"""NLI model wrapper for 3-label sentence-pair classification.

Provides a singleton ``NLIModel`` that loads a HuggingFace
sequence-classification model once and exposes batch prediction.

Labels returned: ``"entailment"``, ``"contradiction"``, ``"neutral"``.
"""
from __future__ import annotations

import logging
from typing import Any, ClassVar, Dict, List, Optional

logger = logging.getLogger(__name__)


class NLIModel:
    """Singleton wrapper around a HuggingFace NLI model.

    Usage::

        nli = NLIModel.get_instance("tals/albert-xlarge-vitaminc-mnli", "cuda:0")
        labels = nli.predict(
            premises=["The function returns an int."],
            hypotheses=["The function returns a string."],
        )
        # labels == ["contradiction"]
    """

    _instance: ClassVar[Optional["NLIModel"]] = None

    def __init__(
        self,
        model_name: str,
        device: str = "cuda:0",
        batch_size: int = 64,
    ) -> None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        logger.info("Loading NLI model: %s (device=%s)", model_name, device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(device).eval()
        self.device = device
        self.batch_size = batch_size
        self._torch = torch

        # Build normalised label map: model_id → lowercase label string
        raw_id2label: Dict[int, str] = self.model.config.id2label
        self._id2label: Dict[int, str] = {
            k: v.lower() for k, v in raw_id2label.items()
        }
        logger.info("NLI model loaded. id2label=%s", self._id2label)

    @classmethod
    def get_instance(
        cls,
        model_name: str,
        device: str = "cuda:0",
        batch_size: int = 64,
    ) -> "NLIModel":
        """Return (and cache) a singleton instance."""
        if cls._instance is None:
            cls._instance = cls(model_name, device, batch_size)
        return cls._instance

    def predict(
        self,
        premises: List[str],
        hypotheses: List[str],
    ) -> List[str]:
        """Classify each (premise, hypothesis) pair.

        Args:
            premises: Ground-truth sentences (dependency docs).
            hypotheses: Sentences to verify (current draft).

        Returns:
            List of labels, one per pair: ``"entailment"``,
            ``"contradiction"``, or ``"neutral"``.
        """
        assert len(premises) == len(hypotheses), (
            f"premises ({len(premises)}) and hypotheses ({len(hypotheses)}) must match"
        )
        if not premises:
            return []

        all_labels: List[str] = []
        for start in range(0, len(premises), self.batch_size):
            end = start + self.batch_size
            batch_p = premises[start:end]
            batch_h = hypotheses[start:end]

            inputs = self.tokenizer(
                batch_p,
                batch_h,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            ).to(self.device)

            with self._torch.no_grad():
                logits = self.model(**inputs).logits
                preds = logits.argmax(dim=-1).cpu().tolist()

            all_labels.extend(self._id2label[p] for p in preds)

        return all_labels
