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
Provides a collection of text summarization algorithms for automatically generating concise summaries from documents.

## Description:
The summarizers module implements various classical and modern text summarization algorithms that transform documents into concise, informative summaries. This module serves as the core text summarization engine for the sumy library, offering multiple approaches to extract key information from text while preserving document structure and meaning.

The module is organized around different algorithmic approaches:
- Statistical methods (KL, LSA, SumBasic)
- Graph-based methods (LexRank, TextRank)
- Rule-based methods (Luhn, Reduction)
- Simple heuristics (Edmundson variants, Random)

Primary consumers include the main sumy library components that handle document parsing, tokenization, and result formatting. The module is designed to be easily extensible with new summarization algorithms while maintaining consistent interfaces.

## Components:
- AbstractSummarizer: Base class defining the interface for all summarizers
- EdmundsonSummarizer: Implements Edmundson's rule-based approach to summarization
- EdmundsonCueSummarizer: Edmundson variant focusing on cue words
- EdmundsonKeySummarizer: Edmundson variant emphasizing key phrases
- EdmundsonLocationSummarizer: Edmundson variant considering sentence position
- EdmundsonTitleSummarizer: Edmundson variant incorporating title information
- KLSummarizer: Implements KL divergence-based summarization
- LexRankSummarizer: Implements LexRank graph-based summarization
- LsaSummarizer: Implements Latent Semantic Analysis summarization
- LuhnSummarizer: Implements Luhn's statistical summarization approach
- RandomSummarizer: Provides random sentence selection for baseline comparison
- ReductionSummarizer: Implements reduction-based sentence ranking
- SumBasicSummarizer: Implements SumBasic statistical summarization
- TextRankSummarizer: Implements TextRank graph-based summarization

## Public API:
- AbstractSummarizer: Base class for all summarizers with common interface
- EdmundsonSummarizer: Rule-based summarization using Edmundson's framework
- EdmundsonCueSummarizer: Cue-word focused summarization variant
- EdmundsonKeySummarizer: Key phrase focused summarization variant
- EdmundsonLocationSummarizer: Position-aware summarization variant
- EdmundsonTitleSummarizer: Title-informed summarization variant
- KLSummarizer: KL divergence-based statistical summarization
- LexRankSummarizer: LexRank graph-based sentence ranking
- LsaSummarizer: Latent Semantic Analysis summarization
- LuhnSummarizer: Luhn's statistical approach to summarization
- RandomSummarizer: Random sentence selection for baseline comparison
- ReductionSummarizer: Reduction-based sentence similarity ranking
- SumBasicSummarizer: SumBasic statistical summarization algorithm
- TextRankSummarizer: TextRank graph-based summarization

## Dependencies:
- Internal: sumy._summarizer (AbstractSummarizer base class)
- External: numpy (required for LexRank, LSA, and TextRank algorithms)
- External: nltk (required for some stemmers and tokenizers)

## Constraints:
- All summarizers must inherit from AbstractSummarizer
- NumPy dependency is required for graph-based algorithms (LexRank, LSA, TextRank)
- Summarizers must handle empty documents gracefully
- Sentence selection algorithms must preserve original sentence order in results
- All algorithms must accept the same interface: (document, sentences_count)

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

