# `plaintext.py`

## `sumy.parsers.plaintext.PlaintextParser` · *class*

## Summary:
PlaintextParser parses raw plain-text into an in-memory document model (ObjectDocumentModel) composed of Paragraph and Sentence objects using an injected tokenizer. It provides cached access to the parsed document, a list of "significant" words (from headings), and configured "stigma" words.

## Description:
PlaintextParser is a concrete DocumentParser subclass that converts plain-text input (string or file) to a structured ObjectDocumentModel suitable for downstream NLP tasks (summarization, indexing, keyword extraction). It expects a tokenizer implementing the DocumentParser protocol (to_sentences(paragraph) and to_words(sentence)). The parser:
- Splits the raw text into lines;
- Classifies lines that are ALL UPPERCASE as heading sentences (created as Sentence(..., is_heading=True));
- Groups contiguous non-blank lines into paragraphs; paragraph boundaries are blank lines;
- Consolidates text-lines within a paragraph into contiguous blocks, splits those blocks into sentence strings via the tokenizer, and wraps each sentence string into a Sentence object;
- Builds Paragraph objects from ordered Sentence objects and returns an ObjectDocumentModel composed of those Paragraphs.

Typical construction:
- from_string(string, tokenizer) — factory for in-memory strings
- from_file(file_path, tokenizer) — factory that reads a UTF-8 file and constructs the parser
- direct __init__(text, tokenizer) — accepts already-read text

Motivation / Responsibility boundary:
- Responsibility: convert free-form text into the project's DOM (ObjectDocumentModel) representation with a simple, deterministic paragraph/heading policy.
- Not responsible for: implementing tokenization algorithms (delegated to tokenizer), persistent storage, or any I/O beyond reading the input file in from_file.

## State:
- _text (str)
  - Type: unicode/native str
  - Set in __init__ to to_unicode(text).strip()
  - Invariant: trimmed text representing the entire input; may be empty string.
- _tokenizer (object) [inherited from DocumentParser]
  - Type: object implementing to_sentences(paragraph) and to_words(sentence)
  - Invariant: must remain a usable tokenizer for the lifetime of the instance.
- Cached properties (each computed once on first access and cached via cached_property):
  - document -> ObjectDocumentModel
    - Type: ObjectDocumentModel constructed from a list of Paragraph instances.
    - Invariant: each Paragraph contains only Sentence instances. Headings have is_heading == True.
  - significant_words -> tuple[str, ...]
    - Type: tuple of token strings.
    - Semantics: concatenation (in document order) of heading.words across all paragraphs; if no heading tokens exist, returns class-level SIGNIFICANT_WORDS (fallback).
  - stigma_words -> the value of self.STIGMA_WORDS
    - Type: whatever value the class assigns to STIGMA_WORDS (commonly tuple[str, ...]).
- Class-level constants (inherited/available from DocumentParser):
  - SIGNIFICANT_WORDS (tuple[str, ...]) — fallback significant words constant
  - STIGMA_WORDS (tuple[str, ...]) — configured stigma words constant

Class invariants:
- _text is normalized and does not contain leading/trailing whitespace.
- document, significant_words, and stigma_words are deterministic and cached on first access; subsequent reads return the cached object/tuple.
- Sentence instances inside Paragraphs have been constructed with the same tokenizer instance as the parser (_tokenizer).

## Lifecycle:
Creation:
- from_string(string, tokenizer): classmethod; reads provided string and delegates to cls(string, tokenizer).
- from_file(file_path, tokenizer): classmethod; opens file_path with encoding="utf-8", reads entire contents into memory, then delegates to cls(file_contents, tokenizer). The file is closed before returning; entire file content is loaded into memory.
- __init__(text, tokenizer): instance initializer. Calls DocumentParser.__init__(tokenizer) then stores normalized text in self._text via to_unicode(text).strip().

Usage / typical method sequence:
1. Instantiate via from_string, from_file, or __init__.
2. Access parser.document to produce (and cache) the parsed ObjectDocumentModel.
   - Access pattern inside document:
     - Iterate lines: for each line:
       - If line.isupper(): create Sentence(line, tokenizer, is_heading=True) and treat as an inlined heading element within the current paragraph buffer.
       - If line is empty and there is an accumulated paragraph buffer: flush buffer to sentences with _to_sentences(...) and wrap in Paragraph.
       - Otherwise append non-empty, non-heading line to current paragraph buffer.
     - After loop flush any remaining buffer into final Paragraph.
     - Wrap paragraphs into ObjectDocumentModel(paragraphs).
3. Optionally access parser.significant_words to obtain cached tuple derived from heading tokens (falls back to SIGNIFICANT_WORDS if no heading tokens found).
4. Access parser.stigma_words to obtain cached STIGMA_WORDS.
5. No explicit cleanup required — parser holds no external resources and is garbage-collected normally.

Destruction:
- No special destruction or close() is required. There is no context-manager support.

## Method Map:
flowchart LR
    A[from_string(string, tokenizer)] --> B[__init__(text, tokenizer)]
    C[from_file(file_path, tokenizer)] --> D[open file UTF-8 -> read -> close] --> B
    B --> E[_text = to_unicode(text).strip()]
    B --> F[_tokenizer set (DocumentParser.__init__)]
    F --> G[document (cached_property)]
    G --> H[splitlines() -> iterate lines]
    H -->|line.isupper()| I[Sentence(line, tokenizer, is_heading=True)]
    H -->|blank line & buffer| J[_to_sentences(current_paragraph)] --> K[Paragraph(sentences)]
    H -->|non-blank, non-heading line| L[append line to buffer]
    K --> M[ObjectDocumentModel(paragraphs)]
    G --> M
    N[significant_words (cached_property)] -->|reads| G
    N -->|collect headings.words| O[tuple of tokens] --> N
    P[stigma_words (cached_property)] -->|returns| STIGMA_WORDS
    subgraph tokenizer
        S[tokenize_sentences(text)] --> T[tokenizer.to_sentences(text)]
        U[tokenize_words(sentence)] --> V[tokenizer.to_words(sentence)]
    end
    J --> S
    _to_sentence_objects --> |for each s| Sentence(s, tokenizer)

Notes:
- _to_sentences(lines) preserves existing Sentence objects and concatenates adjacent string lines using single-space separators, then tokenizes flushed text blocks into Sentence objects via _to_sentence_objects.
- _to_sentence_objects(text) calls self.tokenize_sentences(text) (DocumentParser method) and lazily yields Sentence instances for each string returned.

## Raises:
- from_file:
  - FileNotFoundError: if file_path does not exist.
  - OSError / PermissionError: on file open/read failures.
  - UnicodeDecodeError: if file contents are not valid UTF-8.
  - Any exception raised by cls(file_contents, tokenizer) during instance construction.
- __init__:
  - Propagates any exception raised by to_unicode(text) or by DocumentParser.__init__ (tokenizer handling). No explicit validation occurs; invalid tokenizer will only fail when used.
- document (when accessed):
  - May propagate exceptions from:
    - tokenizer via self.tokenize_sentences(text) (e.g., TypeError, ValueError, tokenizer-specific errors).
    - Paragraph.__init__ TypeError if non-Sentence objects are passed (should not occur with provided helpers).
    - Any attribute errors if the tokenizer or DOM classes are replaced with incompatible types.
- _to_sentences(lines):
  - TypeError if an element in lines is neither a Sentence instance nor a string (e.g., concatenation of non-string with " " raises TypeError).
  - Propagates exceptions from _to_sentence_objects and tokenizer calls.
- _to_sentence_objects(text):
  - Propagates exceptions from tokenize_sentences(text) and from Sentence(...) construction (e.g., encoding/conversion errors).

## Example:
- Creating from a string:
  1. Provide a tokenizer implementing to_sentences(paragraph) -> iterable[str] and to_words(sentence) -> iterable[str].
  2. parser = PlaintextParser.from_string(raw_text, tokenizer)
  3. dom = parser.document  # triggers parsing; cached for subsequent calls
  4. For each paragraph in dom.paragraphs:
       - iterate paragraph.headings to inspect heading Sentence objects (heading.is_heading == True)
       - iterate paragraph.sentences (non-heading Sentence objects) for content
       - paragraph.words yields flattened tokens for the paragraph (via Sentence.words and tokenizer)
  5. sig = parser.significant_words  # tuple of tokens from headings, or SIGNIFICANT_WORDS fallback
  6. stigma = parser.stigma_words    # cached STIGMA_WORDS value
- Creating from a file:
  1. parser = PlaintextParser.from_file("/path/to/doc.txt", tokenizer)
  2. Access parser.document and other properties as above.
- Notes on edge-case behavior:
  - If _text is empty or whitespace-only, document still returns an ObjectDocumentModel containing a single Paragraph whose sentences list is empty.
  - Headings are detected only by line.isupper() after stripping whitespace. Lines containing punctuation or digits may still qualify if .isupper() returns True.
  - The entire input is read into memory by from_file; large files may be memory-intensive.

### `sumy.parsers.plaintext.PlaintextParser.from_string` · *method*

## Summary:
Constructs and returns a new parser instance initialized from raw text and a tokenizer, producing an object whose internal _text is the given string converted to unicode and stripped of surrounding whitespace and whose tokenizer reference is stored for later tokenization.

## Description:
Known callers and context:
- Typical callers are summarizers, indexers, or other NLP pipeline components that need to create a PlaintextParser (or subclass) from an in-memory string. It is invoked during the pipeline stage where raw text content is turned into a document model for sentence- and word-level tokenization.
- Tests and factory code commonly call this method when they need a parser instance without reading from a file.
Why this logic is a separate method:
- Acts as a convenience factory that mirrors from_file, providing a clear, discoverable API for creating a parser from a string input.
- Keeps construction and any future input normalization centralized (so callers need not repeat the same conversion/validation logic).

## Args:
    cls (type): The class to instantiate (a PlaintextParser subclass). Must be callable with the signature cls(text, tokenizer).
    string (str or bytes-like): Raw text to parse. It will be coerced to unicode (text) and stripped of leading/trailing whitespace during instance initialization.
    tokenizer (object): An object implementing the tokenizer protocol required by DocumentParser:
        - to_sentences(paragraph) -> iterable of sentence strings
        - to_words(sentence) -> iterable of token strings
    Note: tokenizer is not validated by this method; it is stored on the instance by DocumentParser.__init__ and expected to be usable for subsequent tokenization calls.

## Returns:
    instance of cls:
    - A newly created instance of the provided class.
    - Guarantees on returned instance:
        * The instance's _text attribute will be set to the unicode conversion of the provided string with surrounding whitespace removed (equivalent to to_unicode(string).strip()).
        * The tokenizer will have been stored on the instance (via DocumentParser.__init__), typically at _tokenizer.

    Edge cases:
    - If the provided string is empty or only whitespace, _text will be set to an empty string.
    - If tokenizer is None, the instance will be created with _tokenizer set to None (no immediate validation); subsequent tokenization calls will fail.

## Raises:
    - Propagates any exception raised during instance construction (cls(string, tokenizer)). Typical examples:
        * TypeError if cls cannot be called with the given arguments (wrong signature).
        * Any exceptions raised by to_unicode when converting the input inside __init__ (e.g., if conversion of the provided object fails).
    - This method itself performs no additional checks; it does not catch or wrap exceptions.

## State Changes:
    Attributes READ:
        - None on the class or an existing instance (method is a classmethod and does not access instance state).
    Attributes WRITTEN (effects on the returned instance):
        - _tokenizer: set by DocumentParser.__init__ to the provided tokenizer reference.
        - _text: set by PlaintextParser.__init__ to to_unicode(string).strip().

## Constraints:
    Preconditions:
        - cls must be a class (callable) whose constructor accepts (text, tokenizer).
        - tokenizer should implement the tokenizer protocol described above if the returned instance will be used for tokenization.
    Postconditions:
        - The returned object is an instance of cls with _text normalized (unicode + stripped) and _tokenizer set.
        - No other side effects occur (no file I/O or global state changes).

## Side Effects:
    - No I/O or external service calls are performed by this method itself.
    - The only effect is creation of a new object and the initialization of its attributes (as described in State Changes).

### `sumy.parsers.plaintext.PlaintextParser.from_file` · *method*

## Summary:
Creates and returns a new parser instance initialized from the full contents of a UTF-8 encoded file; the returned instance's internal text and tokenizer state reflect the file contents and provided tokenizer.

## Description:
- Known callers and context:
    - Higher-level pipeline or application code that needs to construct a PlaintextParser from a file path (for example CLI tools, ETL steps, summarizers, indexers, or test fixtures that accept file input).
    - Typical lifecycle stage: invoked during pipeline setup or input-loading stage to convert a plain-text input file into a parser instance that can produce a document model and sentence/word tokens.
- Reason for being a separate method:
    - Encapsulates file I/O and a consistent encoding choice (UTF-8) so callers don't need to duplicate file-reading logic.
    - Provides a concise factory-style constructor that returns an instance of cls (supports subclasses) from file contents rather than from a raw string.
    - Keeps file-reading concerns separate from parsing logic and from the __init__ constructor which expects already-read text.

## Args:
    cls (type): The class to construct (implicitly provided because this is a classmethod). Typically PlaintextParser or a subclass.
    file_path (str or os.PathLike): Path to the input file. Must point to an existing, readable file. No default.
    tokenizer (object): Tokenizer instance to attach to the parser. Must implement the tokenizer protocol used by DocumentParser:
        - to_sentences(paragraph) -> iterable[str]
        - to_words(sentence) -> iterable[str]
      The tokenizer is stored on the created instance and not validated at call time.

## Returns:
    object: An instance of cls (PlaintextParser or subclass) constructed by calling cls(file_contents, tokenizer).
    - The instance's _text attribute will contain the file contents coerced to unicode and stripped of leading/trailing whitespace.
    - The instance's _tokenizer (inherited from DocumentParser) will be set to the provided tokenizer.
    - Edge-case: if the file is empty or contains only whitespace, _text will be the empty string and the parser.document will produce a single Paragraph with zero sentences (see PlaintextParser.document behavior).

## Raises:
    FileNotFoundError: If file_path does not exist.
    OSError (including PermissionError): For other I/O problems opening or reading the file.
    UnicodeDecodeError: If the file bytes cannot be decoded using UTF-8 (encoding="utf-8" is forced).
    Any exception raised by cls(file_contents, tokenizer): If the class constructor raises (e.g., unexpected constructor signature), that exception propagates.

## State Changes:
- Attributes READ:
    - None on any existing PlaintextParser instance (this is a classmethod and does not read instance attributes).
- Attributes WRITTEN:
    - None on any existing PlaintextParser instance or on the class object itself.
    - As a result of calling cls(...), a new instance is created; that new instance will have attributes set by __init__:
        - _text: set to the file contents after to_unicode(...).strip()
        - _tokenizer: set to the provided tokenizer (set by DocumentParser.__init__)

## Constraints:
- Preconditions:
    - file_path must be a valid path-like pointing to a readable file.
    - The file must be UTF-8 encoded (or decodable as UTF-8); otherwise a UnicodeDecodeError will be raised.
    - tokenizer should implement the tokenizer protocol (to_sentences, to_words) expected by DocumentParser for later parsing operations; no runtime validation is performed here.
- Postconditions:
    - No file descriptor remains open after the method returns (uses with-open context).
    - The returned object is an instance of cls whose _text is the stripped unicode contents of the file and whose _tokenizer is the provided tokenizer.
    - If the file is empty or whitespace-only, returned_instance._text == "" and returned_instance.document will contain one Paragraph with no sentences (per PlaintextParser.document logic).

## Side Effects:
    - Performs synchronous disk I/O: opens and reads the entire file into memory.
    - No writes to disk or network calls are performed.
    - Memory: the entire file content is loaded into memory as a single string (not streamed).
    - No global state or module-level variables are modified.

### `sumy.parsers.plaintext.PlaintextParser.__init__` · *method*

## Summary:
Initializes a PlaintextParser instance by storing the provided text (normalized to native string/unicode and stripped) and delegating tokenizer setup to the parent DocumentParser initializer.

## Description:
This initializer is called during object construction (directly via __init__ or indirectly via convenience factories such as from_string and from_file). Typical callers:
- PlaintextParser.from_string(string, tokenizer) — when constructing a parser from an in-memory string.
- PlaintextParser.from_file(file_path, tokenizer) — after the file contents have been read and passed as text.
- Direct instantiation PlaintextParser(text, tokenizer) — when the caller has already prepared the raw text.

It exists as a separate initializer to keep tokenizer wiring (handled by DocumentParser.__init__) and input normalization (handled here) clearly separated. Normalizing and trimming the raw text early ensures downstream cached parsing and tokenization operate on a predictable, whitespace-normalized string.

## Args:
    text (str or bytes or any object accepted by to_unicode):
        Raw input representing the document content. It will be converted to the native unicode/str type using to_unicode(text) and then trimmed with .strip().
        - Allowed values: any object that to_unicode can convert (commonly a str/unicode or bytes).
        - Typical values: the entire document as a single string read from memory or from a UTF-8 file.
    tokenizer (object):
        A tokenizer instance compliant with the DocumentParser protocol (expected to support methods used elsewhere, e.g., to_sentences(paragraph) and to_words(sentence)). No runtime validation is performed here; an incompatible tokenizer may only fail later when parsing is attempted.

## Returns:
    None

## Raises:
    TypeError:
        - If to_unicode(text) raises TypeError (e.g., text is of a type that cannot be converted to unicode by the project's to_unicode).
    ValueError or other exceptions from to_unicode:
        - If to_unicode(text) raises ValueError for malformed input.
    Any exception raised by DocumentParser.__init__(tokenizer):
        - For example, if the parent initializer validates the tokenizer and raises on invalid input; such exceptions are propagated.

Note: Exceptions are not raised explicitly in this method body; they are those that may be thrown by the called routines (to_unicode or the parent initializer).

## State Changes:
Attributes READ:
    - None (this method does not read any pre-existing self.* attributes).

Attributes WRITTEN:
    - self._text (str): Set to to_unicode(text).strip() — a normalized, trimmed native string.
    - Indirectly written by the parent initializer (DocumentParser.__init__):
        - self._tokenizer (object): the tokenizer reference stored on the instance (this is done by the superclass initializer invoked via super()).

## Constraints:
Preconditions:
    - The provided text must be convertible by to_unicode(text). If not, to_unicode will raise and initialization will fail.
    - The tokenizer should implement the expected interface used elsewhere in the class (to_sentences and to_words). There is no immediate validation in this initializer—missing methods will surface when parsing is attempted.

Postconditions:
    - self._text is a native str/unicode with leading and trailing whitespace removed (may be the empty string).
    - The instance has been initialized via DocumentParser.__init__(tokenizer), so the tokenizer reference is available on the object (commonly as self._tokenizer).
    - The object is ready for lazy parsing operations (e.g., accessing the cached document property) though actual parsing is performed on demand.

## Side Effects:
    - No I/O or external service calls occur in this method.
    - No mutation of objects outside the instance (only instance attributes are set).
    - Calls to to_unicode may perform encoding/decoding work and may raise encoding-related exceptions; these are local to the call and not persisted externally.

### `sumy.parsers.plaintext.PlaintextParser.significant_words` · *method*

## Summary:
Collects token strings from all heading sentences in the parsed document and returns them as an immutable tuple; if no heading tokens are found, returns the class-level SIGNIFICANT_WORDS fallback. The computed tuple is cached (method is used as a cached property).

## Description:
Known callers and usage context:
- Typical callers are downstream components (summarizers, indexers, keyword extractors, or any pipeline step) that query the parser for a list of "significant" words to bias or seed processing.
- It is invoked during the analysis stage after the PlaintextParser.document property has been computed (i.e., once the raw text has been parsed into Paragraph and Sentence objects).
- Because the method is decorated with cached_property on the class, callers access it as an attribute (parser.significant_words). The first access computes and caches the value; subsequent accesses return the cached tuple.

Why this logic is its own method:
- It encapsulates the policy "use heading tokens as significant words, otherwise fall back to a predefined constant" in one place, keeping calling code simple and consistent.
- Separating the logic allows caching the computed token tuple (avoiding repeated traversal and tokenizer calls) and centralizes the fallback behavior to the class-level constant SIGNIFICANT_WORDS.
- Keeping this behavior out of inline code reduces duplication and keeps parsing and heuristics decoupled.

## Args:
- None (no parameters). Accessed via self as a cached property.

## Returns:
- tuple[str]: An immutable tuple of token strings.
  - Primary case: a tuple created from concatenating heading.words for every heading in every paragraph, in document order (paragraph iteration order, then heading order within each paragraph, then the token order within each heading).
  - Fallback case: self.SIGNIFICANT_WORDS (a class-level tuple[str, ...]) when no heading tokens were found.
  - Edge cases:
    - If heading.words yields an empty sequence for every heading, the method treats that as "no words" and returns SIGNIFICANT_WORDS.
    - The returned tuple preserves original token order produced by Sentence.words and paragraph ordering.

## Raises:
- The method does not explicitly raise exceptions but will propagate exceptions raised during attribute access or iteration:
  - AttributeError: if self.document is missing or does not expose .paragraphs, or if a paragraph lacks .headings, or if a heading lacks .words.
  - TypeError: if paragraph.headings or heading.words are not iterable (e.g., None), or if .extend receives a non-iterable.
  - Any exceptions raised by evaluating Sentence.words (for example, if that property calls the tokenizer and the tokenizer raises) will propagate to the caller.

## State Changes:
- Attributes READ:
  - self.document (reads the parsed ObjectDocumentModel instance)
  - self.SIGNIFICANT_WORDS (reads class-level constant for fallback)
  - Additionally reads properties on objects reachable from self.document:
    - paragraph.headings for each paragraph in self.document.paragraphs
    - heading.words for each heading (Sentence) encountered
- Attributes WRITTEN:
  - None by this method itself.
  - Note: because the method is used with the cached_property decorator, the first access will cause the cached_property machinery to store the computed tuple on the instance under the caching attribute name; that storage is an implementation detail of cached_property (not a direct assignment in this method body).

## Constraints:
Preconditions:
- self.document must be a document-like object exposing an iterable attribute .paragraphs.
- Each element of self.document.paragraphs should be a Paragraph-like object exposing .headings (an iterable of heading Sentence objects).
- Each heading (Sentence) must expose .words, an iterable of token strings.
- If the above invariants are not met, attribute access/iteration errors may be raised.

Postconditions:
- No mutation of self or the document model is performed by this method (except caching via cached_property external wrapper).
- The method returns a tuple[str] that is either the concatenation of heading.token sequences (in document order) or the class-level SIGNIFICANT_WORDS tuple when no heading tokens were found.
- Subsequent accesses (via the cached_property) will return the same tuple without re-traversing the document.

## Side Effects:
- No I/O or external service calls are performed directly.
- Accessing heading.words may trigger evaluation of Sentence.words which typically delegates to the tokenizer (DocumentParser._tokenizer.to_words); thus, calling this property can cause the tokenizer to run and may propagate tokenizer-side effects or exceptions.
- The cached_property wrapper will store the computed value on the instance on first access (observable as an attribute being set by the cached property implementation).

### `sumy.parsers.plaintext.PlaintextParser.stigma_words` · *method*

## Summary:
Expose and cache the parser's configured STIGMA_WORDS value so callers obtain the class-defined collection of stigma words with a single, cached lookup.

## Description:
This cached property returns the value of self.STIGMA_WORDS and relies on the class-level cached_property decorator (declared on the PlaintextParser class) to store the result on the instance after the first access.

Known callers / usage context:
- There are no direct references to this property elsewhere in this file; it is intended for use by external components that need the parser's stigma-word configuration during parsing, filtering, or downstream processing in the text-to-document pipeline.
- Typical lifecycle: accessed during analysis or scoring phases after the parser is constructed, not during initialization.

Why it is a separate method/property:
- STIGMA_WORDS is configuration-like data defined on the class hierarchy. Central access via this property makes subclassing and overrides straightforward.
- The cached_property decorator ensures the value is read once and then cached on the instance, avoiding repeated attribute lookups if the underlying STIGMA_WORDS were expensive to compute in subclasses.

## Args:
    None

## Returns:
    The exact value of self.STIGMA_WORDS.
    - Type: the type assigned to STIGMA_WORDS by the class (commonly an iterable of strings such as tuple or list), but the documentation does not assume a specific concrete type.
    - Edge-case return: if STIGMA_WORDS is defined and set to None, None will be returned (i.e., the method returns whatever the attribute contains).

## Raises:
    AttributeError: If STIGMA_WORDS is not defined on the instance or anywhere in its class MRO, evaluating self.STIGMA_WORDS will raise AttributeError.

## State Changes:
    Attributes READ:
        - self.STIGMA_WORDS
    Attributes WRITTEN:
        - The cached_property decorator will store the returned value on the instance under the property name on first access (mutation performed by the decorator). The method body itself performs no assignments.

## Constraints:
    Preconditions:
        - The instance must be a PlaintextParser (or subclass) and its class hierarchy should define STIGMA_WORDS if callers expect a meaningful value.
    Postconditions:
        - The value returned equals self.STIGMA_WORDS at the time of first evaluation.
        - After the first access, the cached value is present on the instance; subsequent accesses return the cached object without re-reading self.STIGMA_WORDS.

## Side Effects:
    - No I/O or external service calls.
    - Instance mutation due to the cached_property caching behavior on first access.

### `sumy.parsers.plaintext.PlaintextParser.document` · *method*

## Summary:
Parses the parser's raw text into an ObjectDocumentModel containing Paragraphs of Sentence objects; the result is cached on the parser instance.

## Description:
This cached property builds a document DOM model from the parser's _text by:
- Splitting the normalized input into lines.
- Classifying lines that are all-uppercase (line.isupper()) as heading Sentence objects (is_heading=True).
- Grouping contiguous non-blank lines into paragraphs; on paragraph boundaries (blank lines) converting the accumulated lines and heading Sentence objects into Sentence objects and wrapping them in a Paragraph.
- Ensuring a final Paragraph is created from any remaining lines after the loop.
Known callers / usage contexts:
- PlaintextParser.significant_words accesses self.document.paragraphs to collect heading words (see the class's significant_words cached_property).
- External consumers call this property to obtain a parsed ObjectDocumentModel as the parser->tokenizer->DOM stage in a text processing pipeline.
Why this logic is its own (cached) property:
- Parsing raw text into a DOM model is an expensive, deterministic transformation that is reused (e.g., by significant_words and by downstream consumers). Making it a separate, cached property centralizes parsing, avoids duplicated work, and returns a stable ObjectDocumentModel instance for the parser's lifetime.

## Args:
- None (this is a zero-argument cached property/attribute).

## Returns:
- ObjectDocumentModel: an instance constructed from a list of Paragraph objects created from the input text.
  - Each Paragraph contains a tuple of Sentence objects (Paragraph enforces Sentence instances).
  - Each Sentence is either:
    - A heading Sentence constructed when the original line satisfied line.isupper(), created with is_heading=True; or
    - A Sentence produced by tokenizing concatenated non-heading lines with self.tokenize_sentences and wrapping each sentence-string with Sentence(..., self._tokenizer).
  - Edge-case returns:
    - If the parser's _text is empty (or contains only whitespace), the method still returns an ObjectDocumentModel containing one Paragraph whose sentences list is empty (i.e., Paragraph of length 0).
    - Headings are preserved as Sentence objects within the Paragraphs in the order encountered.

## Raises:
- The method does not explicitly raise exceptions itself.
- Indirect/propagated exceptions:
  - Paragraph.__init__ may raise TypeError if given non-Sentence elements; this should not occur when using the provided _to_sentences/_to_sentence_objects implementations because they produce Sentence instances, but a custom override of those helpers or of tokenize_sentences could cause this TypeError to propagate.
  - Exceptions may propagate from tokenizer-related calls invoked when tokenizing paragraph text (via self.tokenize_sentences), such as ValueError or tokenizer-specific errors if the tokenizer implementation raises them.

## State Changes:
Attributes READ:
- self._text: read and iterated as lines (self._text.splitlines()).
- self._tokenizer: passed into Sentence constructors and used indirectly when creating Sentence objects.
- self._to_sentences / self.tokenize_sentences: the method invokes these helpers to convert accumulated line text into Sentence objects.
Attributes WRITTEN:
- As implemented in the class, document is decorated with cached_property; fetching this property will cause the cached_property machinery to store/cache the returned ObjectDocumentModel on the instance (typically under a cached attribute name, e.g., "_cached_property_document"). The method body itself does not assign to other self.* attributes.

## Constraints:
Preconditions:
- self._text is expected to be a (Unicode) string. In PlaintextParser.__init__, _text is normalized with to_unicode(...).strip(), so callers should construct the parser normally rather than mutating _text after construction.
- The parser's tokenize_sentences method must return an iterable of strings (sentence texts) for internal conversion to Sentence objects to succeed.
Postconditions:
- The returned ObjectDocumentModel contains Paragraph instances in the original document order.
- Each Paragraph contains only Sentence instances; headings have is_heading==True and are in their original relative positions.
- The parser instance will hold a cached reference to the returned ObjectDocumentModel via the cached_property decorator (so subsequent accesses return the same object without reparsing).

## Side Effects:
- No file I/O or network I/O.
- May invoke tokenizer logic (via self.tokenize_sentences and via Sentence construction which stores tokenizer for later use); tokenizer methods may perform CPU work and may raise tokenizer-specific exceptions.
- The cached_property decorator causes the parsed ObjectDocumentModel to be cached on the parser instance (mutation of the instance to store the cached value).
- Allocates in-memory structures: lists of Paragraphs, lists of Sentence objects, and associated tuples inside Paragraph (via Paragraph constructor and its caching).

### `sumy.parsers.plaintext.PlaintextParser._to_sentences` · *method*

## Summary:
Convert an iterable of mixed text lines and Sentence objects into a flat list of Sentence objects, preserving existing Sentence instances and tokenizing accumulated text segments into Sentence objects.

## Description:
This method is called while building the Document model from plain text: PlaintextParser.document collects lines for a paragraph as either raw text lines (str) or already-created Sentence objects (e.g., headings) and then calls this method to produce the paragraph's ordered list of Sentence objects. It is separated into its own method because it implements the non-trivial logic of:
- preserving pre-constructed Sentence objects in their original form and position,
- concatenating adjacent text lines into larger text blocks,
- tokenizing those blocks into Sentence objects via _to_sentence_objects,
and returning a single flattened list. Keeping this logic separate keeps the document-building flow clear and allows reusing/testing the tokenization/merge behavior independently.

Known callers:
- PlaintextParser.document (parsing pipeline stage: paragraph -> sentences conversion)

## Args:
    lines (iterable[str|Sentence]): An iterable (typically a list) whose elements are either:
        - Sentence instances (models.dom.Sentence) that should be preserved as-is in the output, or
        - text lines (str) that will be concatenated and later tokenized into Sentence objects.
    There is no default value; the caller must supply an iterable. Elements that are neither str nor Sentence will cause a TypeError when concatenated.

## Returns:
    list[Sentence]:
        - A list containing Sentence instances in the same document order as the input.
        - Existing Sentence objects from the input are included by identity (appended unchanged).
        - Text segments are concatenated (with single-space separators), stripped, tokenized via self.tokenize_sentences, converted to Sentence instances by _to_sentence_objects, and their resulting Sentence objects are appended in order.
        - If input contains no sentences/text, returns an empty list.

## Raises:
    TypeError:
        - If an element of lines is neither a Sentence instance nor a string-like object, the expression " ' ' + line " will raise a TypeError.
    Any exceptions raised by:
        - self._to_sentence_objects(text) or the tokenizer invoked within it (for example, errors from self.tokenize_sentences) will propagate out of this method unchanged.

## State Changes:
    Attributes READ:
        - None read directly by attribute access in this method.
        - Indirectly depends on self._to_sentence_objects (which uses self._tokenizer and tokenize_sentences), so those internal resources are used when text is flushed to tokenization.
    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - lines must be an iterable of elements that are either models.dom.Sentence instances or strings (or string-like objects). Non-string, non-Sentence elements will cause a TypeError.
        - If the caller relies on trimming/normalizing line whitespace, note that this method prefixes concatenated fragments with a single space for each appended non-Sentence line but strips the final accumulated text before tokenization, so internal extra spaces are removed at flush time.
    Postconditions:
        - The returned value is a list of models.dom.Sentence objects representing the input lines in-order with text lines tokenized and Sentence instances preserved.
        - The method does not mutate the input iterable or any attributes on self.

## Side Effects:
    - No I/O, no network calls.
    - The only mutations are construction of new Sentence objects (via _to_sentence_objects) and building the returned list; nothing outside the returned list and local variables is mutated.
    - Exceptions from the tokenizer or _to_sentence_objects may be raised to the caller.

### `sumy.parsers.plaintext.PlaintextParser._to_sentence_objects` · *method*

## Summary:
Creates a lazy sequence of Sentence domain objects from raw text by splitting the text into sentence strings and wrapping each string with the parser's tokenizer. The method does not modify parser state; it returns a generator that yields Sentence instances linked to self._tokenizer.

## Description:
Known callers and context:
    - PlaintextParser._to_sentences: used while assembling a paragraph's list of sentence objects from lines of text.
    - PlaintextParser.document: indirectly used during document construction when converting paragraph text into Sentence objects.
    - Lifecycle: invoked during the parsing pipeline when PlaintextParser converts raw text into the Document object model (ObjectDocumentModel -> Paragraph -> Sentence).

Why this is a separate method:
    - Encapsulates the one responsibility of converting raw text into Sentence objects so other methods (_to_sentences, document) can focus on paragraph and document composition.
    - Centralizes construction of Sentence objects with a consistent tokenizer (self._tokenizer).
    - Returns a generator (lazy sequence) rather than a concrete list to avoid unnecessary memory allocation and to allow callers to iterate or extend lists directly.

## Args:
    text (str): The input text to split into sentence strings. Expected to be a native string/unicode type. No default value; must be provided by caller.

## Returns:
    generator[Sentence]: A generator expression that yields Sentence instances for each sentence string produced by self.tokenize_sentences(text).
    - If tokenize_sentences(text) yields no items, the generator yields nothing (equivalent to an empty sequence).
    - Note on evaluation timing:
        * The call to self.tokenize_sentences(text) is executed immediately when _to_sentence_objects is called (the iterable to be iterated is obtained).
        * Construction of each Sentence(...) is performed lazily as the generator is iterated by the caller.

## Raises:
    - This method does not raise exceptions itself, but it will propagate exceptions from:
        * self.tokenize_sentences(text) (e.g., TypeError if it is not callable or does not return an iterable).
        * Sentence(...) constructor (e.g., if Sentence raises for invalid inputs).
    - Any exceptions raised by tokenizer methods invoked later by Sentence.words will propagate when those properties are accessed (not from this method directly).

## State Changes:
    Attributes READ:
        - self._tokenizer: used to pass into each Sentence so that tokens/words can later be derived consistently.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self must implement a tokenize_sentences(text) method (or inherit one) that returns an iterable of sentence strings given the supplied text.
        - text should be a string (unicode/native str). If not, to_unicode conversion inside Sentence may raise.
        - self._tokenizer must be a valid tokenizer object expected by Sentence (it will be stored on each Sentence and used later by Sentence.words).
    Postconditions:
        - Returns a generator which, when iterated, yields Sentence instances whose internal text has been normalized by Sentence (to_unicode(...).strip()) and whose _tokenizer attribute is the same object referenced by self._tokenizer.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of external objects or of self.
    - The only object construction side effect is creation of Sentence instances when the returned generator is iterated; until iteration, only the iterable from tokenize_sentences(text) is obtained.

## Usage notes:
    - Callers that need a concrete list of Sentence objects should explicitly materialize the generator, e.g., list(self._to_sentence_objects(text)).
    - Because tokenize_sentences(text) is invoked at method call time, any heavy computation in tokenization will occur immediately; Sentence object creation remains lazy.

