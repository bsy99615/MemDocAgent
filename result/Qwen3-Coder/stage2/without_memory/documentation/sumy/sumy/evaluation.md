# `sumy.evaluation`

## Tree:
evaluation/
├── __main__.py
├── content_based.py
├── coselection.py
└── rouge.py

## Role:
Provides evaluation metrics and tools for assessing text summarization quality.

## Description:
This module implements various evaluation techniques for measuring the effectiveness of automatic text summarization algorithms. It offers multiple approaches to compare generated summaries against reference summaries, including content-based similarity measures, coselection-based metrics, and ROUGE metrics. The module serves as a comprehensive toolkit for researchers and developers working with text summarization systems.

The primary consumers of this module are the command-line interface for running automated evaluations and potentially other analysis tools within the sumy library. These components are grouped together because they all serve the common purpose of quantitatively evaluating summarization quality through different algorithmic approaches.

## Components:
*   `build_luhn(parser, language)` - Creates a Luhn summarizer instance for evaluation
*   `build_lex_rank(parser, language)` - Creates a LexRank summarizer instance for evaluation
*   `build_lsa(parser, language)` - Creates an LSA summarizer instance for evaluation
*   `build_kl(parser, language)` - Creates a KL summarizer instance for evaluation
*   `build_edmundson(parser, language)` - Creates an Edmundson summarizer instance for evaluation
*   `build_random(parser, language)` - Creates a random summarizer instance for evaluation
*   `build_sum_basic(parser, language)` - Creates a SumBasic summarizer instance for evaluation
*   `build_text_rank(parser, language)` - Creates a TextRank summarizer instance for evaluation
*   `evaluate_cosine_similarity(evaluated_sentences, reference_sentences)` - Computes cosine similarity between evaluated and reference sentences
*   `evaluate_unit_overlap(evaluated_sentences, reference_sentences)` - Computes unit overlap between evaluated and reference sentences
*   `handle_arguments(args)` - Processes command-line arguments for evaluation setup
*   `main(args)` - Main entry point for running evaluation tests
*   `cosine_similarity(evaluated_model, reference_model)` - Calculates cosine similarity between term frequency models
*   `unit_overlap(evaluated_model, reference_model)` - Calculates unit overlap between term frequency models
*   `f_score(evaluated_sentences, reference_sentences, weight=1.0)` - Computes F-score for evaluation metrics
*   `precision(evaluated_sentences, reference_sentences)` - Computes precision for evaluation metrics
*   `recall(evaluated_sentences, reference_sentences)` - Computes recall for evaluation metrics
*   `rouge_1(evaluated_sentences, reference_sentences)` - Computes ROUGE-1 metric for evaluation
*   `rouge_2(evaluated_sentences, reference_sentences)` - Computes ROUGE-2 metric for evaluation
*   `rouge_l_sentence_level(evaluated_sentences, reference_sentences)` - Computes ROUGE-L at sentence level for evaluation
*   `rouge_l_summary_level(evaluated_sentences, reference_sentences)` - Computes ROUGE-L at summary level for evaluation
*   `rouge_n(evaluated_sentences, reference_sentences, n=2)` - Computes general ROUGE-N metric for evaluation

## Public API:
*   `main(args)` - Main entry point for running evaluation tests
*   `handle_arguments(args)` - Processes command-line arguments for evaluation setup
*   `build_luhn(parser, language)` - Creates a Luhn summarizer instance for evaluation
*   `build_lex_rank(parser, language)` - Creates a LexRank summarizer instance for evaluation
*   `build_lsa(parser, language)` - Creates an LSA summarizer instance for evaluation
*   `build_kl(parser, language)` - Creates a KL summarizer instance for evaluation
*   `build_edmundson(parser, language)` - Creates an Edmundson summarizer instance for evaluation
*   `build_random(parser, language)` - Creates a random summarizer instance for evaluation
*   `build_sum_basic(parser, language)` - Creates a SumBasic summarizer instance for evaluation
*   `build_text_rank(parser, language)` - Creates a TextRank summarizer instance for evaluation
*   `evaluate_cosine_similarity(evaluated_sentences, reference_sentences)` - Computes cosine similarity between evaluated and reference sentences
*   `evaluate_unit_overlap(evaluated_sentences, reference_sentences)` - Computes unit overlap between evaluated and reference sentences
*   `cosine_similarity(evaluated_model, reference_model)` - Calculates cosine similarity between term frequency models
*   `unit_overlap(evaluated_model, reference_model)` - Calculates unit overlap between term frequency models
*   `f_score(evaluated_sentences, reference_sentences, weight=1.0)` - Computes F-score for evaluation metrics
*   `precision(evaluated_sentences, reference_sentences)` - Computes precision for evaluation metrics
*   `recall(evaluated_sentences, reference_sentences)` - Computes recall for evaluation metrics
*   `rouge_1(evaluated_sentences, reference_sentences)` - Computes ROUGE-1 metric for evaluation
*   `rouge_2(evaluated_sentences, reference_sentences)` - Computes ROUGE-2 metric for evaluation
*   `rouge_l_sentence_level(evaluated_sentences, reference_sentences)` - Computes ROUGE-L at sentence level for evaluation
*   `rouge_l_summary_level(evaluated_sentences, reference_sentences)` - Computes ROUGE-L at summary level for evaluation
*   `rouge_n(evaluated_sentences, reference_sentences, n=2)` - Computes general ROUGE-N metric for evaluation

## Dependencies:
*   Internal imports from sumy.models, sumy.parsers, sumy.summarizers, sumy.utils
*   External imports: itertools.chain, math, sys, docopt, collections.Counter

## Constraints:
*   All evaluation functions require valid sentence collections with proper sentence objects
*   Cosine similarity and unit overlap functions require TfModel instances
*   ROUGE metrics require proper sentence splitting and n-gram extraction
*   Evaluation functions expect consistent language handling across all inputs
*   Thread safety is not guaranteed for evaluation functions

---

## Files

- [`__main__.py`](evaluation/__main__.md)
- [`content_based.py`](evaluation/content_based.md)
- [`coselection.py`](evaluation/coselection.md)
- [`rouge.py`](evaluation/rouge.md)

