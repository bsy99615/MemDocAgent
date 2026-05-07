"""Text utilities for NLI-based conflict detection.

Provides rule-based sentence extraction from structured documentation,
replacing LLM-based claim decomposition with zero-cost string operations.
"""
from __future__ import annotations

import re
from typing import List

# ---------------------------------------------------------------------------
# Markdown noise patterns
# ---------------------------------------------------------------------------

# All levels of markdown headers (# through ######)
_HEADER_RE = re.compile(r"^\s*#{1,6}\s+.*$", re.MULTILINE)

# Mermaid / code-fence blocks
_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)

# Directory tree lines (├── └── │)
_TREE_LINE_RE = re.compile(r"^.*[├└│──]+.*$", re.MULTILINE)

# Markdown links [text](url)
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")

# Bold/italic markers
_MD_BOLD_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")

# Inline code backticks (preserve content, remove backticks)
_BACKTICK_RE = re.compile(r"`([^`]+)`")

# Horizontal rules (---, ***, ___)
_HR_RE = re.compile(r"^\s*[-*_]{3,}\s*$", re.MULTILINE)

# Markdown list prefix (e.g. "    - ", "  * ", "1. ")
_LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+", re.MULTILINE)

# Key-value structural lines (e.g., "**Directory Responsibilities:**")
_KV_HEADER_RE = re.compile(r"^\s*\*\*[^*]+:\*\*\s*$", re.MULTILINE)

# Sentence boundary: split after . ! ? followed by whitespace
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

_MIN_SENTENCE_LEN = 20  # skip fragments shorter than this (raised from 10)
_MIN_WORD_COUNT = 4  # skip sentences with fewer than 4 words


def strip_markdown_noise(doc: str) -> str:
    """Remove markdown formatting noise from documentation for NLI input.

    Strips headers, code blocks, directory trees, horizontal rules,
    and converts markdown links/bold to plain text.
    """
    text = _CODE_BLOCK_RE.sub("", doc)       # code blocks / mermaid
    text = _TREE_LINE_RE.sub("", text)       # directory tree lines
    text = _HEADER_RE.sub("", text)          # all header levels
    text = _HR_RE.sub("", text)              # horizontal rules
    text = _KV_HEADER_RE.sub("", text)       # **Key:** lines
    text = _MD_LINK_RE.sub(r"\1", text)      # [text](url) → text
    text = _MD_BOLD_RE.sub(r"\1", text)      # **bold** → bold
    text = _BACKTICK_RE.sub(r"\1", text)     # `code` → code
    return text


# Keep old name as alias for backward compatibility
strip_section_headers = strip_markdown_noise


def split_sentences(text: str) -> List[str]:
    """Split cleaned documentation into individual sentences.

    Splits on newlines first (each line = candidate sentence),
    then on sentence-ending punctuation within each line.
    Filters out very short fragments and structural noise.
    """
    if not text:
        return []

    # Stage 1: Split on newlines (each line is a candidate)
    lines = text.split("\n")

    sentences: List[str] = []
    for line in lines:
        line = re.sub(r"\s{2,}", " ", line).strip()
        if not line:
            continue

        # Stage 2: Split on sentence boundaries within the line
        parts = _SENT_SPLIT_RE.split(line)
        for s in parts:
            s = _LIST_PREFIX_RE.sub("", s).strip()
            if len(s) < _MIN_SENTENCE_LEN:
                continue
            if len(s.split()) < _MIN_WORD_COUNT:
                continue
            if re.match(r"^[\w./\\]+$", s):
                continue
            sentences.append(s)
    return sentences


def extract_backtick_names(sentence: str) -> set:
    """Return the set of backtick-quoted names in *sentence*."""
    return set(re.findall(r"`([^`]+)`", sentence))
