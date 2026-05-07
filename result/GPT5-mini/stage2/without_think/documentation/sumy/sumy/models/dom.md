# `sumy.models.dom`

## Tree:
dom/
├── _document.py
├── _paragraph.py
└── _sentence.py

## Role:
Provide an in-memory, language-agnostic document object model composed of sentences and paragraphs and supply stable, read-only views (flattened sentence/word/headings lists) that summarizers and other text-processing components can consume.

## Description:
- Where and when this module is used:
  - Serves as the canonical lightweight DOM for text in the summarization pipeline. It is constructed by DOM/building/parsing code and consumed by downstream components that operate at paragraph, sentence, or token granularity (for example: summarizers, ranking/scoring stages, token-based feature extractors).
  - Typical lifecycle: parsed text → Sentence objects (with a tokenizer) → Paragraph containers → ObjectDocumentModel wrapping paragraphs → summarizer/analyzer consumes document-level views.

- Why these components are grouped here:
  - Cohesion principle: the module groups small, orthogonal model classes that together represent document structure (sentence, paragraph, document). They share semantics (tokenization, heading flags, cached flattened views) and a consistent caching/immutability policy, so co-locating them keeps the model API compact and discoverable.
  - Layer boundary: this module is the domain model layer (pure in-memory structures). It does not depend on parsing or summarization algorithms; instead it provides the structured data those layers consume.

## Components:
- class ObjectDocumentModel(paragraphs)
  - Document-level container that stores paragraphs as an immutable sequence and exposes cached flattened views: paragraphs, headings, sentences, words.
- class Paragraph(sentences)
  - Container for Sentence objects; validates element types and exposes cached properties: headings (sentences where is_heading==True), sentences (non-heading sentences), and words (flattened tokens from contained sentences).
- class Sentence(text, tokenizer, is_heading=False)
  - Represents an individual sentence (or heading); stores normalized text, a tokenizer reference, and a heading flag; exposes cached tokenization via words and provides equality/hash semantics.

Mermaid dependency graph:
graph LR
    S[Sentence] -->|contained in| P[Paragraph]
    P -->|contained in| D[ObjectDocumentModel]
    P -->|reads .words| S
    D -->|flattens .sentences/.words/.headings| P
    S -->|delegates tokenization to| T[Tokenizer Interface: to_words(text)]

## Public API:
- ObjectDocumentModel(paragraphs)
  - Signature: ObjectDocumentModel(paragraphs: Iterable[Paragraph])
  - Description: Construct a document from an iterable of Paragraph instances. Stores paragraphs as an immutable tuple and exposes read-only, cached views:
    - .paragraphs -> tuple[Paragraph]: direct immutable sequence (no copy).
    - .headings -> tuple[Sentence]: flattened tuple of paragraph.headings in paragraph order.
    - .sentences -> tuple[Sentence]: flattened tuple of paragraph.sentences (non-heading) in paragraph order.
    - .words -> tuple: flattened tuple of tokens from all paragraphs in order.
  - Usage note: pass an iterable of Paragraph objects; the iterable is consumed once. Cached views may be materialized on first access and stored on the instance.

- Paragraph(sentences)
  - Signature: Paragraph(sentences: Iterable[Sentence])
  - Description: Create a paragraph container from an iterable of Sentence objects. Provides:
    - .sentences -> tuple[Sentence]: tuple of Sentence objects where is_heading is False (cached).
    - .headings -> tuple[Sentence]: tuple of Sentence objects where is_heading is True (cached).
    - .words -> tuple[str]: flattened tokens from every contained sentence (cached).
  - Usage note: constructor enforces that each item is an instance of Sentence and raises TypeError with message "Only instances of class 'Sentence' are allowed." on violation.

- Sentence(text, tokenizer, is_heading=False)
  - Signature: Sentence(text: Any, tokenizer: Any, is_heading: bool = False)
  - Description: Immutable-ish value object representing sentence text and heading status. Exposes:
    - .words -> sequence: result of tokenizer.to_words(normalized_text) (cached on first access).
    - .is_heading -> bool: read-only flag.
    - equality/hash: equality compares normalized text and heading flag; hash computed from (is_heading, text).
    - .__unicode__ / string representation returns the normalized text.
  - Usage note: tokenizer must implement to_words(text). The class normalizes text via the repo's compatibility helper (to_unicode(...).strip()) during construction. Do not mutate text/heading after insertion into hashed collections.

## Dependencies:
- Internal imports (from inside the repository):
  - cached_property (utils): used to lazily compute and cache derived views (e.g., .words/.sentences/.headings). Purpose: avoid recomputing expensive flattening/tokenization results.
  - to_unicode (compat/_compat): used by Sentence to normalize text to a text (unicode/str) value.
  - Classes reference each other across files: _sentence.Sentence → _paragraph.Paragraph → _document.ObjectDocumentModel.

- External / standard-library imports:
  - itertools.chain: used conceptually to flatten per-sentence or per-paragraph iterables into a single sequence for .words/.sentences/.headings.
  - No third-party dependencies are required at the model level; tokenization is delegated to a tokenizer object whose implementation may import third-party libraries.

## Constraints:
- Type contracts:
  - Paragraph constructor requires Sentence instances. Passing non-Sentence elements raises TypeError.
  - Sentence.words requires the tokenizer to implement a callable to_words(text) method; missing method or tokenizer errors will propagate on first access.
- Immutability and caching:
  - Paragraphs and document-level paragraph storage are stored as tuples (immutable sequences). The module returns these tuples directly (no defensive copy) — callers must treat returned sequences as read-only.
  - cached_property is used for materialized views: first access computes and caches the tuple on the instance. This can increase memory usage proportional to document size; large documents will realize all sentences/words into memory when their cached properties are accessed.
- Thread-safety:
  - Cached-property writes are typically not synchronized. Concurrent first-access races can result in multiple computations or unguarded writes; the module does not provide thread synchronization — callers requiring concurrent access must provide external synchronization.
- Equality/hash notes:
  - Sentence.__eq__ uses an assertion-based type check in its implementation; comparisons with non-Sentence objects may raise AssertionError in non-optimized runs or AttributeError in optimized runs. Callers should compare Sentence instances to Sentence instances to avoid assertion/attribute errors.
- Initialization ordering:
  - Construct Sentence with a valid tokenizer before calling .words.
  - Build Paragraphs from fully-formed Sentence objects before constructing a document, since Paragraph validates element types at construction.
- Performance:
  - Flattening properties (.sentences/.words/.headings on the document) iterate over all paragraphs/sentences and allocate a tuple containing all items. For streaming or extremely large inputs, callers should avoid these materializing properties and instead iterate paragraphs and sentences lazily.

---

## Files

- [`_document.py`](dom/_document.md)
- [`_paragraph.py`](dom/_paragraph.md)
- [`_sentence.py`](dom/_sentence.md)

