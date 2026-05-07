# `sumy.nlp.stemmers`

## Tree:
stemmers/
├── __init__.py
├── czech.py
├── greek.py
└── ukrainian.py

## Role:
Provides language-aware word stemming functionality for multiple Slavic and Hellenic languages, with specialized implementations for Czech, Greek, and Ukrainian text processing.

## Description:
The stemmers module offers a unified interface for applying morphological stemming operations to words in various languages. It serves as a core text preprocessing component that reduces words to their base morphological forms, which is essential for tasks like text summarization, information retrieval, and natural language processing. The module handles both general-purpose stemming through NLTK integration and specialized language-specific algorithms for better accuracy in particular linguistic domains.

This module is primarily consumed by text processing pipelines in the sumy library, particularly in the preprocessing and tokenization stages of document analysis. The separation of language-specific stemmers into dedicated modules allows for clean architecture and enables easy extension with additional languages.

## Components:
- Stemmer (class): Main interface for language-aware stemming with fallback to NLTK stemmers
- null_stemmer (function): Identity function that returns input unchanged
- czech.stem_word (function): Czech-specific stemming with multi-stage morphological processing
- czech._palatalize (function): Helper for Czech palatalization transformations
- czech._remove_augmentative (function): Removes Czech augmentative suffixes
- czech._remove_case (function): Strips Czech case endings
- czech._remove_comparative (function): Removes comparative suffixes from Czech words
- czech._remove_derivational (function): Removes derivational suffixes from Czech words
- czech._remove_diminutive (function): Removes diminutive suffixes from Czech words
- czech._remove_possessives (function): Removes possessive endings from Czech words
- greek.stem_word (function): Greek stemming using greek-stemmer library
- ukrainian.stem_word (function): Ukrainian stemming with morphological suffix removal
- ukrainian._preprocess (function): Normalizes Ukrainian text for stemming
- ukrainian._update_suffix (function): Updates suffix strings via regex pattern replacement

## Public API:
- Stemmer(language): Constructor for creating language-specific stemmers
- stem_word(word, aggressive=False): Generic stemming function for Czech text
- null_stemmer(word): Identity function returning input unchanged
- greek.stem_word(word): Greek word stemming function
- ukrainian.stem_word(word): Ukrainian word stemming function

## Dependencies:
Internal:
- sumy.nlp.utils: Used for language normalization utilities
- sumy.utils: Provides general utility functions
- nltk.stem.snowball: Required for NLTK-based stemmer fallbacks
- greek-stemmer: External library for Greek stemming (optional dependency)

External:
- nltk: Natural Language Toolkit for general-purpose stemmers
- re: Regular expressions for pattern matching in Ukrainian stemming
- greek-stemmer: Third-party library for Greek linguistic processing

## Constraints:
- All language identifiers must be valid and supported by the underlying stemmer implementations
- Specialized stemmers require specific external dependencies (e.g., greek-stemmer for Greek)
- Thread safety: The stemmers are stateless and thus inherently thread-safe
- Initialization: Stemmer instances must be properly initialized with valid language identifiers
- Input validation: All stemmer functions expect string inputs and may raise exceptions for invalid inputs

---

## Files

- [`__init__.py`](stemmers/__init__.md)
- [`czech.py`](stemmers/czech.md)
- [`greek.py`](stemmers/greek.md)
- [`ukrainian.py`](stemmers/ukrainian.md)

