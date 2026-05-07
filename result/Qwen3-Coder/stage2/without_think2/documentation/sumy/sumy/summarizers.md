# `sumy.summarizers`

## Tree:
summarizers/
├── _summarizer.py
├── edmundson.py
├── edmundson_cue.py
├── edmundson_key.py
├── edmundson_location.py
├── edmundson_title.py
├── kl.py
├── lex_rank.py
├── lsa.py
├── luhn.py
├── random.py
├── reduction.py
├── sum_basic.py
└── text_rank.py

## Role:
Provides implementations of various text summarization algorithms for automatically extracting key information from documents.

## Description:
The summarizers module contains concrete implementations of multiple text summarization algorithms, each designed to extract the most important sentences from a document based on different computational approaches. These algorithms range from statistical methods like Luhn and SumBasic to graph-based approaches like LexRank and TextRank, and domain-specific methods like Edmundson variants.

This module serves as the core engine for automatic text summarization within the sumy library, offering users a variety of techniques to choose from based on their specific needs. Each summarizer implements the AbstractSummarizer interface, ensuring consistent usage patterns across different algorithms.

## Components:
- AbstractSummarizer: Base class defining the interface for all summarizers
- EdmundsonSummarizer: Implements Edmundson's approach using multiple criteria (cue, key, location, title)
- EdmundsonCueMethod: Evaluates sentences based on cue words
- EdmundsonKeyMethod: Identifies key terms in sentences
- EdmundsonLocationMethod: Ranks sentences based on their position in the document
- EdmundsonTitleMethod: Uses document headings to identify important content
- KLSummarizer: Implements KL divergence-based summarization
- LexRankSummarizer: Uses graph-based ranking with eigenvector centrality
- LsaSummarizer: Applies Latent Semantic Analysis through SVD
- LuhnSummarizer: Ranks sentences based on significant word frequency
- RandomSummarizer: Selects sentences randomly for baseline comparison
- ReductionSummarizer: Ranks sentences by similarity to others in the document
- SumBasicSummarizer: Uses word frequency to iteratively select sentences
- TextRankSummarizer: Implements graph-based ranking with power iteration

## Public API:
- AbstractSummarizer: Base class for all summarizers
- EdmundsonSummarizer: Main interface for Edmundson-based summarization
- KLSummarizer: KL divergence-based summarization
- LexRankSummarizer: LexRank algorithm implementation
- LsaSummarizer: Latent Semantic Analysis summarization
- LuhnSummarizer: Luhn algorithm implementation
- RandomSummarizer: Random sentence selection
- ReductionSummarizer: Reduction-based sentence ranking
- SumBasicSummarizer: SumBasic algorithm implementation
- TextRankSummarizer: TextRank algorithm implementation

## Dependencies:
- Internal: sumy._summarizer (AbstractSummarizer base class, which provides _stemmer: Callable object used for word stemming operations)
- External: numpy (required for LexRank, LSA, and TextRank algorithms)

## Constraints:
- All summarizers must inherit from AbstractSummarizer
- Algorithms requiring numerical computation depend on NumPy
- Stop words must be normalized using the inherited normalize_word method
- Sentence selection respects original document ordering

---

## Files

- [`_summarizer.py`](summarizers/_summarizer.md)
- [`edmundson.py`](summarizers/edmundson.md)
- [`edmundson_cue.py`](summarizers/edmundson_cue.md)
- [`edmundson_key.py`](summarizers/edmundson_key.md)
- [`edmundson_location.py`](summarizers/edmundson_location.md)
- [`edmundson_title.py`](summarizers/edmundson_title.md)
- [`kl.py`](summarizers/kl.md)
- [`lex_rank.py`](summarizers/lex_rank.md)
- [`lsa.py`](summarizers/lsa.md)
- [`luhn.py`](summarizers/luhn.md)
- [`random.py`](summarizers/random.md)
- [`reduction.py`](summarizers/reduction.md)
- [`sum_basic.py`](summarizers/sum_basic.md)
- [`text_rank.py`](summarizers/text_rank.md)

