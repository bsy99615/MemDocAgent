# `sumy.models`

## Tree:
models/
├── dom/
│   ├── _document.py
│   ├── _paragraph.py
│   └── _sentence.py
└── tf.py

## Role:
Provide in-memory document-level model primitives and a compact term-frequency document representation used by summarization and ranking components.

## Description:
- Where and when this module is used:
  - Acts as the canonical model layer for text data inside the summarization pipeline. Consumers include summarizers, ranking/scoring modules, feature extractors, and any component that needs stable document-, paragraph-, sentence-, or token-level views.
  - Typical flow: parsing/tokenization code produces Sentence objects (or raw tokens) → Paragraph containers hold sentences → ObjectDocumentModel exposes flattened views to consumers; TfDocumentModel provides a compact term-frequency view for algorithms that need frequency-based features.

- Why these components are grouped here:
  - Cohesion: groups pure in-memory data structures that represent the document domain (structure and simple statistical representation). These classes share responsibilities around immutability, cached derived views, and token-normalization conventions, so co-locating them creates a discoverable domain-model layer separated from parsing, tokenization implementations, and algorithmic code.

- Where to find detailed behavior:
  - Document structure (Sentence, Paragraph, ObjectDocumentModel): see sumy/models/dom documentation.
  - Term-frequency model (TfDocumentModel) and methods: see sumy/models/tf documentation (TfDocumentModel and its methods such as magnitude, most_frequent_terms, term_frequency, normalized_term_frequency, terms, __repr__, __init__ are documented there).

## Components:
- module sumy/models/dom
  - public classes (defined across _sentence.py, _paragraph.py, _document.py)
    - Sentence(text, tokenizer, is_heading=False)
      - Represents an individual sentence/heading; provides cached tokenization and equality/hash semantics.
    - Paragraph(sentences)
      - Container of Sentence objects; exposes cached flattened views for headings, sentences, and words.
    - ObjectDocumentModel(paragraphs)
      - Document-level container that stores paragraphs as an immutable sequence and exposes cached flattened views: headings, sentences, words.
  - See: sumy/models/dom for full component-level docs and implementation notes.

- module sumy/models/tf (tf.py)
  - class TfDocumentModel(words, tokenizer=None)
    - Encapsulates a document as a term-frequency model (internal Counter), exposes magnitude, vocabulary, ranked terms, raw and normalized term frequencies, and a repr for debugging.
  - See: sumy/models/tf for full method-level details and examples.

Mermaid dependency graph (high-level relationships):
graph LR
    subgraph DOM
      S[Sentence] -->|contained in| P[Paragraph]
      P -->|contained in| D[ObjectDocumentModel]
      S -->|tokenized by| T[Tokenizer Interface]
    end
    TF[TfDocumentModel] -->|built from tokens| D
    TF -->|reads tokens or Sentence.words| S
    D -->|provides flattened .words/.sentences/.headings| Consumers[Summarizers/Rankers/Features]

## Public API:
- sumy.models.dom (module)
  - Sentence(text, tokenizer, is_heading=False)
    - Signature: Sentence(text: Any, tokenizer: Any, is_heading: bool = False)
    - Note: Tokenizer must implement to_words(text). See sumy/models/dom for construction rules, cached properties, and equality/hash behavior.
  - Paragraph(sentences)
    - Signature: Paragraph(sentences: Iterable[Sentence])
    - Note: Constructor validates element types; returns cached .sentences/.headings/.words as tuples.
  - ObjectDocumentModel(paragraphs)
    - Signature: ObjectDocumentModel(paragraphs: Iterable[Paragraph])
    - Note: Stores paragraphs as an immutable tuple and exposes cached flattened views: .paragraphs, .headings, .sentences, .words.

- sumy.models.tf (module)
  - TfDocumentModel(words, tokenizer=None)
    - Signature: TfDocumentModel(words: Sequence[str] | str, tokenizer: Optional[object] = None)
    - Brief: Build a normalized term-frequency view for a document. If words is a raw string, tokenizer is required and its to_words(to_unicode(words)) will be used. Exposes:
      - magnitude -> float (L2 norm)
      - terms -> iterable of vocabulary terms
      - most_frequent_terms(count=0) -> tuple[str,..]
      - term_frequency(term) -> int
      - normalized_term_frequency(term, smooth=0.0) -> float
      - __repr__() -> str
    - Note: Stored term keys are lowercased unicode strings (constructor lowercases tokens). See sumy/models/tf for usage examples and edge-case handling.

Usage note:
- Prefer constructing TfDocumentModel from token sequences when tokenization is already available (e.g., Sentence.words). If only raw text is available, pass a tokenizer object implementing to_words.

## Dependencies:
- Internal (repository) dependencies:
  - sumy._compat (to_unicode, string_types): used for consistent unicode normalization and string/sequence detection.
  - sumy.utils.cached_property (or an equivalent cached_property helper): used by DOM classes to lazily materialize derived views (.words, .sentences, .headings).
  - Tokenizer interface (not implemented here): components expect an object with to_words(unicode_text) -> Sequence[str].

- External / standard-library dependencies:
  - collections.Counter: used by TfDocumentModel to count token frequencies.
  - itertools.chain: conceptually used to flatten nested iterables for .words/.sentences/.headings.
  - math (sqrt): used to compute magnitude (Euclidean norm).
  - pprint (pprint.pformat): used by TfDocumentModel.__repr__ to create readable representations.
  - No heavy third-party libraries are required by this module itself; tokenizers or higher-layer components may depend on third-party NLP libraries.

## Constraints:
- Type and initialization constraints:
  - Paragraph constructor requires Sentence instances — passing other types raises TypeError.
  - Sentence expects a tokenizer with to_words; accessing .words without a valid tokenizer will raise when first invoked.
  - TfDocumentModel: if words is a string, tokenizer must be provided; otherwise a ValueError is raised. If words is neither a string nor a Sequence, constructor raises ValueError.

- Immutability and caching:
  - Paragraphs and document-level paragraph storage are stored as tuples and returned directly (no defensive copy). Callers must treat returned sequences as read-only.
  - cached_property writes are not synchronized; the module does not provide thread-safety for first-access races. If multiple threads may access cached properties concurrently, callers must provide external synchronization.

- Normalization and lookup semantics:
  - TfDocumentModel lowercases tokens at construction; term_frequency lookup is exact (no implicit lowercasing). Callers should pass the canonical form (lowercased) when querying.
  - Sentence equality/hash is based on normalized text and heading flag; comparing non-Sentence objects to Sentence instances is unsupported and may raise.

- Performance considerations:
  - Flattening views (.sentences/.words/.headings on the document) materialize tuples containing all items; for very large documents this can use substantial memory. Consumers that need streaming behavior should iterate paragraphs and sentences directly rather than using materialized views.

- Ordering and determinism:
  - most_frequent_terms sorts by frequency; ties are resolved by Python's sort stability combined with the iteration order of the underlying mapping (thus deterministic for a given runtime and insertion order but not guaranteed by the API beyond "descending frequency").

For implementation details and per-method contracts, see:
- sumy/models/dom (Sentence, Paragraph, ObjectDocumentModel)
- sumy/models/tf (TfDocumentModel and its methods)

---

## Files

- [`tf.py`](models/tf.md)

