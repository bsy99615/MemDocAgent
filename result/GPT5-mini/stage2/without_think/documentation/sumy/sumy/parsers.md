# `sumy.parsers`

## Tree:
parsers/
├── html.py
├── parser.py
└── plaintext.py

## Role:
Provide source-specific parsers and a tokenizer adapter that convert raw inputs (plain text, local files, HTML, or fetched URLs) into the repository's in-memory document model and token streams. This module owns input normalization, paragraph/heading policies for plain text, HTML extraction/annotation handling, and a stable delegation layer to a pluggable tokenizer.

## Description:
- Where/when this module is used:
  - It is the parsing stage of the pipeline. Consumers (summarizers, indexers, CLI tools, and tests) import parser classes here to obtain parsed ObjectDocumentModel instances or token lists.
  - Primary consumers:
    - Summarization and extraction modules that require Sentence/Paragraph/ObjectDocumentModel inputs.
    - Any code that requires sentence splitting and word tokenization while keeping tokenizer implementation pluggable.
    - Tests and utilities that instantiate parsers from strings, files, or URLs.

- Why these components are grouped together:
  - Cohesion: all files implement the single responsibility of transforming different input sources to the same DOM-style representation and of unifying tokenizer usage. DocumentParser defines the tokenizer contract and shared constants; PlaintextParser and HtmlParser implement source-specific assembly rules and expose consistent factory methods and cached properties.

## Components:
- DocumentParser
  - Signature: class DocumentParser(tokenizer)
  - One-line role: Adapter around a pluggable tokenizer that exposes sentence- and word-level tokenization and supplies fallback word lists (SIGNIFICANT_WORDS, STIGMA_WORDS).
  - See: sumy.parsers.parser.DocumentParser

- DocumentParser.tokenize_sentences
  - Signature: tokenize_sentences(self, paragraph) -> list[str]
  - One-line role: Delegate to tokenizer.to_sentences(paragraph) and return a list with empty/whitespace-only results removed.
  - See: sumy.parsers.parser.DocumentParser.tokenize_sentences

- DocumentParser.tokenize_words
  - Signature: tokenize_words(self, sentence) -> Any
  - One-line role: Delegate to tokenizer.to_words(sentence) and return the tokenizer's result unchanged.
  - See: sumy.parsers.parser.DocumentParser.tokenize_words

- DocumentParser.SIGNIFICANT_WORDS
  - Signature: tuple[str, ...] (class-level constant)
  - One-line role: Fallback tuple used when no significant tokens are discovered.

- DocumentParser.STIGMA_WORDS
  - Signature: tuple[str, ...] (class-level constant)
  - One-line role: Fallback tuple used when no stigmatized tokens are discovered.

- PlaintextParser
  - Signature: class PlaintextParser(text, tokenizer)
  - One-line role: Convert normalized plain text into an ObjectDocumentModel using line-based paragraphing and an uppercase-line heading heuristic.
  - See: sumy.parsers.plaintext.PlaintextParser

- PlaintextParser.from_string
  - Signature: classmethod from_string(cls, string, tokenizer)
  - One-line role: Factory to construct a PlaintextParser from an in-memory string.
  - See: sumy.parsers.plaintext.PlaintextParser.from_string

- PlaintextParser.from_file
  - Signature: classmethod from_file(cls, file_path, tokenizer)
  - One-line role: Factory to construct a PlaintextParser from a UTF-8 encoded file (reads full file).
  - See: sumy.parsers.plaintext.PlaintextParser.from_file

- PlaintextParser.document
  - Signature: cached property document(self) -> ObjectDocumentModel
  - One-line role: Lazily build and cache the parsed ObjectDocumentModel (Paragraph and Sentence objects).
  - See: sumy.parsers.plaintext.PlaintextParser.document

- PlaintextParser.significant_words
  - Signature: cached property significant_words(self) -> tuple[str, ...]
  - One-line role: Tokens collected from heading Sentence objects (in document order); if no heading tokens are found, returns SIGNIFICANT_WORDS fallback.
  - See: sumy.parsers.plaintext.PlaintextParser.significant_words

- PlaintextParser.stigma_words
  - Signature: cached property stigma_words(self) -> Any
  - One-line role: Returns the instance/class STIGMA_WORDS value (cached); used as configured stigma-word set.
  - See: sumy.parsers.plaintext.PlaintextParser.stigma_words

- HtmlParser
  - Signature: class HtmlParser(html_content, tokenizer, url=None)
  - One-line role: Use breadability.readable.Article to extract annotated main_text from HTML, then convert annotated fragments into the ObjectDocumentModel and token tuples.
  - See: sumy.parsers.html.HtmlParser

- HtmlParser.from_string
  - Signature: classmethod from_string(cls, string, url, tokenizer)
  - One-line role: Factory to construct an HtmlParser from in-memory HTML. Note: the factory's positional parameter order is (string, url, tokenizer) and it forwards to the constructor as (html_content, tokenizer, url).
  - See: sumy.parsers.html.HtmlParser.from_string

- HtmlParser.from_file
  - Signature: classmethod from_file(cls, file_path, url=None, tokenizer)
  - One-line role: Read a local file in binary mode and construct an HtmlParser with the raw bytes.
  - See: sumy.parsers.html.HtmlParser.from_file

- HtmlParser.from_url
  - Signature: classmethod from_url(cls, url, tokenizer)
  - One-line role: Fetch content via fetch_url(url), then construct an HtmlParser with the fetched data; network exceptions propagate.
  - See: sumy.parsers.html.HtmlParser.from_url

- HtmlParser.document
  - Signature: cached property document(self) -> ObjectDocumentModel
  - One-line role: Convert breadability's annotated main_text into Paragraphs/Sentences; preserve headings and skip preformatted segments.
  - See: sumy.parsers.html.HtmlParser.document

- HtmlParser.significant_words
  - Signature: cached property significant_words(self) -> tuple[str, ...]
  - One-line role: Tokens collected from annotated HTML fragments matching SIGNIFICANT_TAGS; if none are found, returns SIGNIFICANT_WORDS fallback.
  - See: sumy.parsers.html.HtmlParser.significant_words

- HtmlParser.stigma_words
  - Signature: cached property stigma_words(self) -> tuple[str, ...]
  - One-line role: Tokens collected from annotated HTML fragments matching stigmatized tags (e.g., "a", "strike", "s"); if none are found, returns STIGMA_WORDS fallback.
  - See: sumy.parsers.html.HtmlParser.stigma_words

Mermaid dependency graph (internal relationships):
graph TD
    DP[DocumentParser]
    PP[PlaintextParser]
    HP[HtmlParser]
    DOM[models.dom: Sentence/Paragraph/ObjectDocumentModel]
    TOKEN[tokenizer (to_sentences,to_words)]
    BREAD[breadability.readable.Article]
    NET[utils.net.fetch_url]
    DP -->|injects| TOKEN
    PP -->|extends| DP
    PP -->|produces| DOM
    PP -->|uses| TOKEN
    HP -->|extends| DP
    HP -->|wraps HTML ->| BREAD
    HP -->|produces| DOM
    HP -->|uses| TOKEN
    HP -->|from_url calls| NET
    DP -->|defines| SIGNIFICANT_WORDS
    DP -->|defines| STIGMA_WORDS

## Public API:
- DocumentParser(tokenizer)
  - Purpose: Provide tokenize_sentences(paragraph) -> list[str] and tokenize_words(sentence) -> Any to callers while delegating actual tokenization to the injected tokenizer.
  - Usage note: Supply a tokenizer implementing to_sentences(paragraph) and to_words(sentence). DocumentParser filters out empty sentences only; it does not validate tokenizer return types.

- PlaintextParser.from_string(string, tokenizer)
  - Purpose: Create a PlaintextParser with normalized text; use parser.document to obtain parsed DOM.
  - Usage note: The returned parser caches document and significant/stigma properties on first access.

- PlaintextParser.from_file(file_path, tokenizer)
  - Purpose: Read a UTF-8 file and construct a PlaintextParser; returns an instance ready to produce document and token outputs.
  - Usage note: Reads entire file into memory; raises FileNotFoundError/UnicodeDecodeError on problems.

- HtmlParser.from_string(string, url, tokenizer)
  - Purpose: Create an HtmlParser from raw HTML content. Be careful with positional ordering—prefer keyword args.
  - Usage note: The factory forwards tokenizer as the second constructor argument; to avoid mistakes use explicit keywords.

- HtmlParser.from_file(file_path, url=None, tokenizer)
  - Purpose: Read a file (binary) and construct an HtmlParser using the raw bytes.

- HtmlParser.from_url(url, tokenizer)
  - Purpose: Fetch and parse a remote document; network errors propagate.

- parser.document (PlaintextParser and HtmlParser)
  - Purpose: Access the parsed ObjectDocumentModel. This is computed lazily and cached.
  - Usage note: Accessing this property may invoke tokenizer code once (on first access) and allocate DOM structures.

- parser.significant_words and parser.stigma_words
  - Purpose: Retrieve cached heuristics used by downstream components. significant_words returns input-derived tokens (headings for plain text; annotated fragments for HTML) or a class-level fallback. stigma_words returns stigmatized tokens or STIGMA_WORDS fallback.
  - Usage note: Both are cached per-instance via cached_property; they are not guaranteed to be thread-safe.

## Dependencies:
- Internal:
  - models.dom: Sentence, Paragraph, ObjectDocumentModel — target DOM classes constructed by the parsers.
  - utils.encoding.to_unicode: used by PlaintextParser to normalize input text.
  - utils.net.fetch_url: used by HtmlParser.from_url to fetch remote content.
  - cached_property utility: used to cache document and token-list properties.
  - Tokenizer implementations: injected by callers; the module relies on the tokenizer protocol, not a concrete tokenizer.

- External:
  - breadability.readable.Article: used by HtmlParser to extract readable/annotated main_text from raw HTML.
  - Any third-party tokenizer library supplied by consumers (e.g., language-specific implementations).

## Constraints:
- Tokenizer protocol required by all parsers:
  - to_sentences(paragraph) -> iterable[str]
  - to_words(sentence) -> iterable[str]
  - Passing a tokenizer without these methods will raise AttributeError/TypeError at call time.

- Memory & I/O:
  - PlaintextParser.from_file reads entire file as UTF-8 into memory.
  - HtmlParser.from_file reads entire file in binary into memory and forwards to breadability; both factories are not streaming.

- Parameter ordering caveat:
  - HtmlParser.from_string signature uses (string, url, tokenizer) as positional args but forwards to the constructor as (html_content, tokenizer, url). Prefer keyword args to avoid misplacement.

- Thread-safety:
  - cached_property-based caching is per-instance and not guaranteed thread-safe. If a parser instance is accessed concurrently, property computation may race; callers should externally synchronize if needed.

- Initialization prerequisites:
  - Callers must supply a working tokenizer and the DOM model classes referenced by tests/consumers.
  - For HtmlParser, breadability.readable.Article must be available in the runtime environment.

For implementation specifics, error cases, and detailed behavior (including spacing rules, heading heuristics, and how HTML annotations map to headings or preformatted segments), consult the component-level documentation:
- sumy.parsers.parser.DocumentParser
- sumy.parsers.plaintext.PlaintextParser
- sumy.parsers.html.HtmlParser

---

## Files

- [`html.py`](parsers/html.md)
- [`parser.py`](parsers/parser.md)
- [`plaintext.py`](parsers/plaintext.md)

