# `sumy.evaluation`

## Tree:
evaluation/
├── __main__.py
├── content_based.py
├── coselection.py
└── rouge.py

## Role:
Provides evaluation metrics and tools for assessing the quality of automatic text summarization systems.

## Description:
The evaluation module serves as a comprehensive toolkit for measuring the effectiveness of text summarization algorithms. It offers multiple evaluation approaches including content-based similarity metrics, coselection-based precision/recall measures, and ROUGE (Recall-Oriented Understudy for Gisting Evaluation) metrics. This module enables developers and researchers to quantitatively assess how well their summarization systems perform against reference summaries or original documents.

The module is organized around three primary evaluation paradigms:
1. Content-based similarity (cosine similarity, unit overlap)
2. Coselection metrics (precision, recall, F-score)
3. ROUGE metrics (ROUGE-1, ROUGE-2, ROUGE-L)

These evaluation methods are commonly used in computational linguistics and natural language processing research to benchmark summarization systems.

## Components:
*   **build_edmundson**: Creates and configures an Edmundson summarizer with language-specific settings
*   **build_kl**: Creates and configures a Kullback-Leibler divergence-based summarizer
*   **build_lex_rank**: Creates and configures a LexRank summarizer with language-specific settings
*   **build_lsa**: Creates and configures a Latent Semantic Analysis summarizer
*   **build_luhn**: Creates and configures a Luhn summarizer with language-specific settings
*   **build_random**: Creates and configures a random summarizer without language-specific settings
*   **build_sum_basic**: Creates and configures a SumBasic summarizer with language-specific settings
*   **build_text_rank**: Creates and configures a TextRank summarizer with language-specific settings
*   **evaluate_cosine_similarity**: Computes cosine similarity between document models
*   **evaluate_unit_overlap**: Computes unit overlap similarity between document models
*   **handle_arguments**: Processes command-line arguments to configure evaluation pipeline
*   **main**: Main entry point for running text summarization evaluations
*   **cosine_similarity**: Computes cosine similarity between document models
*   **unit_overlap**: Calculates unit overlap similarity between document models
*   **_divide_evaluation**: Calculates ratio of common sentences between collections
*   **f_score**: Computes F-score for sentence selection evaluation
*   **precision**: Computes precision metric for sentence selection
*   **recall**: Computes recall metric for sentence selection
*   **_f_lcs**: Helper function for LCS-based scoring
*   **_get_index_of_lcs**: Returns lengths of input sequences (placeholder implementation)
*   **_get_ngrams**: Generates n-grams from a text sequence
*   **_get_word_ngrams**: Generates word n-grams from sentence collections
*   **_lcs**: Computes dynamic programming table for longest common subsequence
*   **_len_lcs**: Computes length of longest common subsequence
*   **_recon_lcs**: Reconstructs longest common subsequence from DP table
*   **_split_into_words**: Converts sentence collections to flat word lists
*   **_union_lcs**: Computes union-based LCS ratio between sentences
*   **rouge_1**: Computes ROUGE-1 metric (unigram overlap)
*   **rouge_2**: Computes ROUGE-2 metric (bigram overlap)
*   **rouge_l_sentence_level**: Computes ROUGE-L sentence-level metric
*   **rouge_l_summary_level**: Computes ROUGE-L summary-level metric
*   **rouge_n**: Computes general ROUGE-N metric (n-gram overlap)

## Public API:
*   **build_edmundson(parser, language)**: Creates an EdmundsonSummarizer with language-specific configuration
*   **build_kl(parser, language)**: Creates a KLSummarizer with language-specific configuration
*   **build_lex_rank(parser, language)**: Creates a LexRankSummarizer with language-specific configuration
*   **build_lsa(parser, language)**: Creates an LSASummarizer with language-specific configuration
*   **build_luhn(parser, language)**: Creates a LuhnSummarizer with language-specific configuration
*   **build_random(parser, language)**: Creates a RandomSummarizer with default configuration
*   **build_sum_basic(parser, language)**: Creates a SumBasicSummarizer with language-specific configuration
*   **build_text_rank(parser, language)**: Creates a TextRankSummarizer with language-specific configuration
*   **evaluate_cosine_similarity(evaluated_sentences, reference_sentences)**: Computes cosine similarity between document models
*   **evaluate_unit_overlap(evaluated_sentences, reference_sentences)**: Computes unit overlap similarity between document models
*   **handle_arguments(args)**: Processes command-line arguments to configure evaluation pipeline
*   **main(args=None)**: Main entry point for running text summarization evaluations
*   **cosine_similarity(evaluated_model, reference_model)**: Computes cosine similarity between document models
*   **unit_overlap(evaluated_model, reference_model)**: Calculates unit overlap similarity between document models
*   **f_score(evaluated_sentences, reference_sentences, weight=1.0)**: Computes F-score for sentence selection evaluation
*   **precision(evaluated_sentences, reference_sentences)**: Computes precision metric for sentence selection
*   **recall(evaluated_sentences, reference_sentences)**: Computes recall metric for sentence selection
*   **rouge_1(evaluated_sentences, reference_sentences)**: Computes ROUGE-1 metric (unigram overlap)
*   **rouge_2(evaluated_sentences, reference_sentences)**: Computes ROUGE-2 metric (bigram overlap)
*   **rouge_l_sentence_level(evaluated_sentences, reference_sentences)**: Computes ROUGE-L sentence-level metric
*   **rouge_l_summary_level(evaluated_sentences, reference_sentences)**: Computes ROUGE-L summary-level metric
*   **rouge_n(evaluated_sentences, reference_sentences, n=2)**: Computes general ROUGE-N metric (n-gram overlap)

## Dependencies:
*   **Internal imports**:
    *   `sumy.parsers` - For document parsing capabilities
    *   `sumy.summarizers` - For various summarization algorithms
    *   `sumy.models.dom` - For sentence and document model representations
    *   `sumy.nlp.stemmers` - For language-specific stemming functionality
    *   `sumy.nlp.tokenizers` - For text tokenization
    *   `sumy.utils` - For utility functions and helpers
*   **External imports**:
    *   `collections.Counter` - For counting word frequencies
    *   `math` - For mathematical operations
    *   `numpy` - For numerical computations (used in some implementations)
    *   `docopt` - For command-line argument parsing
    *   `requests` - For HTTP requests (used in fetching URLs)

## Constraints:
*   All evaluation functions require valid sentence objects with appropriate attributes (e.g., `.words`)
*   Language parameters must correspond to supported languages in the system
*   Input collections for evaluation functions must not be empty
*   Document models must be properly initialized with term frequency data
*   ROUGE functions expect sentence collections with valid word attributes
*   Thread safety: Most functions are stateless and thus thread-safe
*   Initialization: Language-specific resources must be available for proper summarizer creation

---

## Files

- [`__main__.py`](evaluation/__main__.md)
- [`content_based.py`](evaluation/content_based.md)
- [`coselection.py`](evaluation/coselection.md)
- [`rouge.py`](evaluation/rouge.md)

