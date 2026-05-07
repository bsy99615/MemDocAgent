# `sumy`

## Tree:
sumy/                       - Top-level Python package (library + CLI entrypoint)
    ├── evaluation/         - Metrics and helpers for evaluating generated summaries
    ├── models/             - In-memory document models and term-frequency model
    │   ├── dom/            - DOM-like objects (Sentence, Paragraph, ObjectDocumentModel)
    │   └── tf.py           - Compact term-frequency document model (TfDocumentModel)
    ├── nlp/                - Tokenization and language-specific stemmer adapters
    │   ├── stemmers/       - Language stemmer adapters / wrappers
    │   └── tokenizers.py   - Tokenizer façade (sentence/word tokenizers)
    ├── parsers/            - Parsers converting raw input (text/HTML/URLs) into models
    │   ├── html.py         - HTML parsing & article extraction adapter
    │   └── plaintext.py    - Plaintext parser and paragraph heuristics
    ├── summarizers/        - Summarization algorithms (LexRank, Luhn, Edmundson, etc.)
    ├── __main__.py        - CLI orchestration and helpers (handle_arguments, main)
    ├── _compat.py         - Python-version compatibility helpers (text/bytes)
    └── utils.py           - Shared utilities (ItemsCount, cached_property, fetch_url, stop-words)
tasks.py                    - Invoke-style task helpers (clean, bump, release, docker, install, test)

## Purpose:
- Problem solved:
  - Provide a reusable, language-aware text summarization library and CLI tool that converts raw text/HTML into concise extractive summaries using multiple algorithms and evaluation helpers.
- Why it matters:
  - Enables quick experimentation with summarization algorithms and assembly of pipelines that include parsing, tokenization, stemming, summarization, and evaluation.
  - Useful for developers, researchers, and automation pipelines that need lightweight extractive summarization or to compare summarization algorithms.
- Target users & scenarios:
  - Developers embedding summarization into applications (import sumy.*).
  - CLI users who want to summarize local files or URLs via python -m sumy.
  - Researchers evaluating summarizers or comparing extractive techniques on documents.
- Position in the ecosystem:
  - Library + CLI tool: primarily a Python library with a CLI entrypoint (module __main__). Integrates with common NLP/tokenization libraries (nltk, optional language-specific tokenizers) and content extraction tools (breadability/readability).

## Architecture:
- High-level architectural pattern:
  - Pipeline pattern: input -> parser -> tokenizer/stemmer -> document model -> summarizer -> output/evaluation.
  - Modular, adapter-based design: tokenizers and stemmers are pluggable adapters; parsers produce standard document model objects consumed by summarizers.
  - Lazy optional dependencies: language-specific tokenizers/stemmers and HTML extraction libraries are imported only when needed by adapters.
- End-to-end data flow (Mermaid flowchart):
flowchart TD
    Input[Raw input (file / url / html / plain text)]
    Parser[sumy.parsers (PlaintextParser / HtmlParser)]
    Tokenizer[sumy.nlp.Tokenizer]
    Stemmer[sumy.nlp.stemmers (adapters)]
    Model[sumy.models (dom / tf)]
    Summarizer[sumy.summarizers (LexRank, Luhn, Edmundson, ...)]
    Evaluation[sumy.evaluation]
    Utils[sumy.utils]
    CLI[python -m sumy (__main__)]
    Compat[sumy._compat]

    Input -->|read/fetch (fetch_url)| Parser
    Parser -->|calls Tokenizer.to_sentences/to_words| Tokenizer
    Tokenizer -->|optionally uses language libs| Stemmer
    Parser -->|produces| Model
    Model -->|consumed by| Summarizer
    Summarizer -->|selects/ranks sentences| Output[Summary sentences]
    Output -->|optional| Evaluation
    Utils -->|used by| Parser & CLI & Summarizer
    Compat -->|text/bytes helpers| Utils & Parser & CLI

## Entry Points:
- CLI:
  - Command: python -m sumy
  - Exposes: CLI orchestration implemented in sumy.__main__.main
  - Responsibilities: parse CLI args, construct tokenizer/parser/stemmer/stop-words, build summarizer, run summarizer, print sentences to stdout. Typical audience: end users and shell scripts.
  - Key helper: sumy.__main__.handle_arguments(args, default_input_stream=None) returns (summarizer, parser, items_count).
- Programmatic API (importable):
  - sumy.parsers
    - PlaintextParser.from_string(text, tokenizer) -> Document model
    - HtmlParser.from_string(html, url=None, tokenizer) -> Document model
    - Use-case: transform raw input into ObjectDocumentModel for summarizers or evaluation.
  - sumy.nlp.Tokenizer(language)
    - Methods: to_sentences(paragraph) and to_words(sentence)
    - Use-case: inject into parsers and models to get language-aware tokenization.
  - sumy.models
    - dom.Sentence, dom.Paragraph, dom.ObjectDocumentModel
    - tf.TfDocumentModel for term-frequency based algorithms
    - Use-case: canonical in-memory representations consumed by summarizers.
  - sumy.summarizers
    - Summarizer classes accept a Stemmer and expose summarizer(document, items_count) -> iterable of Sentence
    - Use-case: implement algorithmic summarization; instantiate and call from application code.
  - sumy.utils
    - Utilities: ItemsCount, cached_property, fetch_url, get_stop_words, normalize_language
    - Use-case: common helpers for pipeline assembly and resource loading.

## Core Features:
- Input parsing
  - Convert plaintext and HTML into structured ObjectDocumentModel (sumy.parsers: plaintext.py, html.py).
- Language-aware tokenization
  - Sentence and word tokenization with pluggable language adapters (sumy.nlp.tokenizers, stemmers).
- Flexible document models
  - DOM-like Sentence/Paragraph/Document objects plus TfDocumentModel for TF-based algorithms (sumy.models.dom, sumy.models.tf).
- Multiple summarization algorithms
  - Implementations for LexRank, Luhn, Edmundson, etc., with a common summarizer interface (sumy.summarizers).
- Stop-words and stemming integration
  - Load packaged stop-words and attach language stemmers to summarizers (sumy.utils, sumy.nlp.stemmers).
- Evaluation helpers
  - Tools to compare generated summaries with references and compute metrics (sumy.evaluation).
- CLI orchestration
  - Build and run summarizer pipelines from command line with argument parsing and runtime wiring (sumy.__main__).
- Utilities for I/O & resources
  - fetch_url wrapper, resource resolution, cached_property, ItemsCount parsing for summary length control (sumy.utils).

## Dependencies:
- Core third-party libraries and role:
  - requests — HTTP fetching helper used by utils.fetch_url.
  - nltk — default sentence/word tokenization and required punkt resources for many languages.
  - breadability.readable (or readability) — HTML article extraction used by HtmlParser.
  - pycountry — optional, used by normalize_language to map language codes to canonical names.
- Optional language/tokenization libraries (imported lazily in adapters):
  - jieba, tinysegmenter, konlpy, hebrew_tokenizer, pyarabic, etc. — used by language-specific Tokenizer adapters.
- Packaging & utilities:
  - pkgutil / importlib.resources — for loading packaged stop-word data.
- Standard library:
  - os, sys, math, collections, itertools, pkgutil, contextlib, typing, etc.
- Version constraints & notes:
  - Optional libraries are not required for core functionality — missing optional libs raise informative errors when that language adapter is requested.
  - NLTK requires punkt resource files to be installed in nltk_data for sentence tokenization to function; otherwise Tokenizer construction may raise LookupError.
  - No strict pinned versions are included here; consult setup.py or requirements files in the repository (not included in this tree) for exact constraints.

## Configuration:
- Resource files:
  - Packaged stop-words under sumy/data/stopwords (loaded via get_stop_words). Missing resources raise LookupError.
- Runtime parameters:
  - CLI flags control parser selection, summarizer algorithm, language, number/percentage of sentences (ItemsCount), stop-words lookup.
- Environment/installation:
  - NLTK punkt data must be present for default Tokenizer.
  - Optional language tokenizers require installation of their specific packages.
- Where configuration affects behavior:
  - Tokenizer behavior and availability of language-specific features depend on installed optional packages and presence of language resources.
  - fetch_url behavior can be adjusted by modifying utility-level headers/constants (found in utils).

## Extension Points:
- Add a new summarizer
  - Implement a class in sumy.summarizers following the existing Summarizer API: initializer accepts a Stemmer (and optional stop_words), and callable semantics summarizer(document, items_count) that yields Sentence objects. Register or reference the new class via CLI mapping in sumy.__main__ if CLI exposure is desired.
- Add a new tokenizer or stemmer
  - Implement a Tokenizer with methods to_sentences(paragraph) and to_words(sentence) and register/use it via Tokenizer(language) factory or instantiate directly and pass into parsers.
  - Implement a stemmer adapter under nlp/stemmers that exposes the minimal interface expected by summarizers (stem(word) or similar).
- Add parser for additional input formats
  - Create a new parser under sumy.parsers that converts the new input type into ObjectDocumentModel and exposes .from_string / .from_file factory methods.
- Stop-words & language data
  - Add packaged stop-word files under sumy/data/stopwords and ensure get_stop_words can locate them; parse_stop_words will interpret the files into frozenset.
- Hooks & utilities
  - Many utilities are designed as small pure functions or adapters, making it straightforward to substitute custom implementations (e.g., replace fetch_url wrapper or ItemsCount parser with project-specific variants).

## Constraints & Operational Notes:
- Thread-safety: Some lazy initialization and cached_property patterns are not synchronized; the package is not guaranteed thread-safe for concurrent first-access. Use per-thread instances or external synchronization.
- Memory & performance: Parsers build materialized tuples (sentences/words). For very large documents, prefer streaming workflows or implement a streaming parser variant.
- Error handling: CLI main and handle_arguments intentionally propagate exceptions; callers and automation should catch exceptions as needed.
- Reproducibility: Summarizer behavior may depend on stemmer, stop-word sets, tokenizer behavior, and optional libraries — ensure deterministic environment for reproducible results.

## Where to look next:
- Module-level documentation (not duplicated here): consult individual module docs for
  - sumy.parsers (plaintext, html, parser)
  - sumy.nlp (tokenizers, stemmers)
  - sumy.models (dom, tf)
  - sumy.summarizers (individual algorithm implementations)
  - sumy.evaluation
  - sumy.__main__ (CLI wiring)
  - sumy.utils and sumy._compat
- Task automation:
  - tasks.py contains Invoke-style tasks for repository maintenance (clean, bump, release, docker, install, test). These are useful for packaging, release, and CI workflows.

---

## Modules

- [`sumy`](sumy.md)
- [`sumy/evaluation`](sumy/evaluation.md)
- [`sumy/models`](sumy/models.md)
- [`sumy/models/dom`](sumy/models/dom.md)
- [`sumy/nlp`](sumy/nlp.md)
- [`sumy/nlp/stemmers`](sumy/nlp/stemmers.md)
- [`sumy/parsers`](sumy/parsers.md)
- [`sumy/summarizers`](sumy/summarizers.md)

