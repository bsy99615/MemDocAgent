# `parser.py`

## `sumy.parsers.parser.DocumentParser` · *class*

## Summary:
DocumentParser is a thin adapter around a tokenizer object that provides two simple, stable parsing operations: splitting paragraph text into non-empty sentences and delegating word tokenization for a single sentence.

## Description:
DocumentParser exists to encapsulate how the rest of the system asks for sentence- and word-level tokenization without coupling callers to a specific tokenizer implementation. It should be instantiated whenever code needs to break free-form paragraph text into sentences and then into words, but the concrete tokenization logic is provided by the injected tokenizer.

Typical callers / factories:
- Any summarizer, indexer, or NLP pipeline component that needs sentence and word tokens from raw paragraph text.
- Test code that injects a lightweight tokenizer stub implementing the required interface.

Motivation and responsibility boundary:
- The class does not implement tokenization algorithms itself; it delegates to the provided tokenizer.
- It enforces minimal post-processing: sentence results are filtered to remove empty/whitespace-only entries.
- It centralizes the place for any document-level tokenization constants (e.g., SIGNIFICANT_WORDS and STIGMA_WORDS) so other components may reference those lists consistently.

## State:
- SIGNIFICANT_WORDS (tuple[str, ...])
  - A tuple of Czech-language "positive" words provided as constants on the class. Immutable at runtime.
  - Valid values: sequence of strings. Never modified by class methods (class-level constant).
- STIGMA_WORDS (tuple[str, ...])
  - A tuple of Czech-language "negative" words provided as constants on the class. Immutable at runtime.
  - Valid values: sequence of strings. Never modified by class methods (class-level constant).
- _tokenizer (object)
  - Type: any object implementing the tokenizer protocol described below.
  - Invariant: after __init__, self._tokenizer is set and must remain a usable tokenizer instance for the lifetime of the DocumentParser instance.
  - There are no further constraints enforced by the class; invalid tokenizer implementations will cause errors only when methods are invoked.

Tokenizer protocol (requirements for objects passed to __init__):
- to_sentences(paragraph)
  - Accepts the paragraph argument passed from DocumentParser.tokenize_sentences.
  - Returns an iterable (commonly a list or generator) of strings representing sentence text.
- to_words(sentence)
  - Accepts the sentence argument passed from DocumentParser.tokenize_words.
  - Returns an iterable (commonly a list) of word/token strings.

Note: The class does not coerce or validate the tokenizer's return types; callers should use a tokenizer that returns string sequences.

## Lifecycle:
Creation:
- Instantiate by providing a tokenizer object implementing to_sentences and to_words. There are no other constructor arguments or defaults.
- Example constructor requirement: DocumentParser(tokenizer=<tokenizer-instance>)

Usage:
- Typical sequence:
  1. Call tokenize_sentences(paragraph) with a paragraph (string). The method returns a list of sentences (strings) with empty/whitespace-only entries removed.
  2. For each sentence you want to analyze further, call tokenize_words(sentence). The method directly returns the tokenizer's word-token iterable for that sentence.
- Methods may be used in any order (they are independent). There is no required setup beyond instantiation.
- Both methods simply delegate to the tokenizer and forward any exceptions raised by the tokenizer.

Destruction / cleanup:
- DocumentParser manages no external resources and requires no explicit cleanup.
- The class is not a context manager and has no close() method.

## Method Map:
Flowchart of method call relationships and typical invocation order:

graph TD
    A[__init__(tokenizer)] --> B[tokenize_sentences(paragraph)]
    B --> |calls| C[tokenizer.to_sentences(paragraph)]
    C --> D[filter out s where not s.strip()]
    A --> E[tokenize_words(sentence)]
    E --> |calls| F[tokenizer.to_words(sentence)]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style E fill:#bbf,stroke:#333,stroke-width:1px

(Interpretation: after creating DocumentParser, callers typically call tokenize_sentences to obtain non-empty sentences; they then call tokenize_words on sentences of interest. Both public methods delegate to similarly-named methods on the injected tokenizer.)

## Methods (behavioral details)
- __init__(tokenizer)
  - Inputs:
    - tokenizer: required. Any object implementing the tokenizer protocol (see State section).
  - Behavior:
    - Stores the tokenizer instance on self._tokenizer.
    - Performs no further validation.
  - Side effects:
    - None beyond storing the reference.
- tokenize_sentences(paragraph)
  - Inputs:
    - paragraph: the paragraph to split into sentences. The method passes this value directly to self._tokenizer.to_sentences(paragraph).
  - Output:
    - list[str]: a Python list containing each sentence string produced by the tokenizer, excluding any entries that are empty or contain only whitespace (i.e., s for s in to_sentences if s.strip()).
  - Behavior and edge cases:
    - If the tokenizer yields empty strings or strings containing only whitespace, those entries are filtered out.
    - The function will propagate any exception raised by tokenizer.to_sentences (e.g., AttributeError if to_sentences is missing, TypeError from tokenizer implementation).
    - If the tokenizer returns a generator, the generator is consumed to produce the returned list.
- tokenize_words(sentence)
  - Inputs:
    - sentence: a single sentence string. Passed directly to self._tokenizer.to_words(sentence).
  - Output:
    - Whatever the tokenizer returns for to_words. Typically an iterable/list of token strings (list[str]).
  - Behavior and edge cases:
    - No post-processing is applied; the result is returned verbatim.
    - Any exception from tokenizer.to_words is propagated to the caller.

## Raises:
- __init__:
  - Explicitly raises nothing. It will complete normally for any input object.
  - Implicit/propagated: none at construction time.
- tokenize_sentences / tokenize_words:
  - May raise AttributeError if the injected tokenizer lacks the expected method(s).
  - May raise any exceptions the tokenizer implementation raises (TypeError, ValueError, etc.). DocumentParser does not catch or translate these exceptions.

## Example (usage described in prose):
1. Prepare a tokenizer object that implements:
   - to_sentences(paragraph) -> returns an iterable of sentence strings
   - to_words(sentence) -> returns an iterable of token strings
2. Create a DocumentParser instance by passing the tokenizer to its constructor.
3. To obtain non-empty sentences from a paragraph, call tokenize_sentences(paragraph). The result is a list of sentence strings; blank or whitespace-only strings are removed.
4. To obtain word tokens for a sentence, call tokenize_words(sentence). The raw output from the tokenizer is returned (typically a list of words).
5. No cleanup is needed after use; discard the DocumentParser instance when finished.

Notes and best practices:
- Prefer passing a tokenizer that returns lists (not generators) if callers expect random-access indexing or repeated iteration.
- If downstream code requires strict types, validate/tokenize the tokenizer's outputs externally, because DocumentParser performs only minimal filtering for sentences and no normalization for words.
- Use the class-level SIGNIFICANT_WORDS and STIGMA_WORDS constants when performing simple sentiment/keyword checks; they are provided as ready-to-use tuples.

### `sumy.parsers.parser.DocumentParser.__init__` · *method*

## Summary:
Stores a tokenizer reference on the new DocumentParser instance so the parser delegates sentence and word tokenization to the injected tokenizer.

## Description:
- Known callers and context:
    - Summarizers, indexers, and other NLP pipeline components that need to convert paragraph text to sentences and sentences to word tokens create a DocumentParser by passing a tokenizer implementation. Typically invoked during component construction or pipeline setup before any tokenization operations occur.
    - Test code that supplies a tokenizer stub or mock to exercise DocumentParser.tokenize_sentences and tokenize_words.
    - Lifecycle stage: called at object creation; establishes the dependency injection that enables subsequent tokenize_sentences and tokenize_words calls.

- Why this logic is a distinct method:
    - Constructor-level assignment centralizes dependency injection (setting the tokenizer) and keeps tokenizer management separate from tokenization logic. This separation makes it trivial to substitute different tokenizer implementations for testing or different languages without inlining or repeating assignment logic elsewhere.

## Args:
    tokenizer (object): Required. Any object implementing the tokenizer protocol:
        - to_sentences(paragraph) -> iterable[str]
        - to_words(sentence) -> iterable[str]
    Allowed values: any object meeting the above protocol. There is no runtime validation performed by __init__, so passing an object that does not provide these methods will only fail later when those methods are invoked.

## Returns:
    None. The constructor initializes the instance and returns normally; no value is returned.

## Raises:
    Explicitly: none declared. Under normal conditions __init__ completes without raising.
    Implicit/propagated: assignment to self._tokenizer is a simple attribute set and will not raise for typical objects. If the instance uses a custom __setattr__ that raises, that exception would propagate. No tokenizer-method-related exceptions are raised here because the tokenizer is not called in __init__.

## State Changes:
- Attributes READ:
    - None (the constructor does not read any existing instance attributes).
- Attributes WRITTEN:
    - self._tokenizer is set to the tokenizer argument.

## Constraints:
- Preconditions:
    - The caller should supply an object that implements the tokenizer protocol (to_sentences and to_words). Although __init__ does not enforce this, consumers of DocumentParser expect these methods to exist.
    - The DocumentParser instance should be newly constructed or in a state where setting attributes is allowed (i.e., no restrictive metaclass or custom __setattr__ that blocks assignment).

- Postconditions:
    - After __init__ returns, self._tokenizer is bound to the provided tokenizer object.
    - The instance is ready for tokenize_sentences and tokenize_words calls; any errors from using an invalid tokenizer will occur when those methods are invoked.

## Side Effects:
    - Mutates the new instance by assigning the tokenizer to self._tokenizer.
    - No I/O, no external service calls, and no other global or external state is modified.

### `sumy.parsers.parser.DocumentParser.tokenize_sentences` · *method*

## Summary:
Splits a paragraph into sentences using the parser's tokenizer and returns only non-empty, non-whitespace sentence strings.

## Description:
This method delegates sentence segmentation to the DocumentParser's tokenizer (self._tokenizer.to_sentences) and filters out any results that are empty or contain only whitespace. It is intended to be used during the text parsing/tokenization stage of the pipeline when a paragraph must be broken into candidate sentences for downstream processing (e.g., sentence scoring, summarization, or further word-tokenization).

Known callers and context:
- No explicit internal call sites were present in the provided snapshot. Typically, this method is invoked by higher-level parsing or summarization components (or by subclasses of DocumentParser) as the step that converts a paragraph-level string into a list of sentence strings before further processing.
- Lifecycle stage: tokenization/sentence-splitting step within a document parsing pipeline.

Why this is a separate method:
- Encapsulates the tokenizer delegate call and the common filter for empty/whitespace-only results so callers don't need to repeat that logic.
- Keeps a single place to adjust sentence-level filtering behavior (for example, if additional normalization or validation is later required).
- Provides a small, well-defined public API on DocumentParser for sentence segmentation.

## Args:
    paragraph (str): A text paragraph to split into sentences. The method does not coerce or normalize the input; it is passed directly to self._tokenizer.to_sentences. Acceptable values depend on the tokenizer implementation (typically a str or Unicode text).

## Returns:
    list[str]: A list of sentence strings produced by self._tokenizer.to_sentences(paragraph), with all elements that are empty or contain only whitespace removed. The returned sentences are exactly the strings produced by the tokenizer (no additional stripping or normalization is performed here other than the emptiness test).

    Edge-case returns:
    - Returns an empty list if the tokenizer yields no sentences or yields only empty/whitespace-only strings.
    - Returns the original sentence strings (not trimmed) if the tokenizer returns strings that include surrounding whitespace.

## Raises:
    - No exceptions are raised directly by this method.
    - Any exception raised by self._tokenizer.to_sentences(paragraph) (for example TypeError if paragraph is of an unsupported type) will propagate to the caller unchanged.

## State Changes:
    Attributes READ:
    - self._tokenizer

    Attributes WRITTEN:
    - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
    - self._tokenizer must be set (typically provided at DocumentParser construction) and must expose a to_sentences(paragraph) method.
    - paragraph must be of a type accepted by the tokenizer; otherwise the tokenizer may raise an exception.

    Postconditions:
    - self remains unchanged.
    - The returned list contains only truthy sentence strings (s for which s.strip() is truthy), i.e., no empty or whitespace-only strings.

## Side Effects:
    - This method itself performs no I/O and makes no network calls.
    - Any side effects originate from the tokenizer implementation invoked via self._tokenizer.to_sentences(paragraph) (if that implementation has side effects, they will occur).

### `sumy.parsers.parser.DocumentParser.tokenize_words` · *method*

## Summary:
Delegates tokenization of a single sentence to the configured tokenizer and returns the tokenizer's result without modifying parser state.

## Description:
This method is a thin adapter that calls the parser's tokenizer to split a sentence into word tokens. It is intended to be used during the tokenization stage of document processing — after sentence segmentation and before downstream steps such as feature extraction, indexing, or summarization.

Known callers:
- No internal callers inside DocumentParser are present in this class. External code (higher-level parsing pipelines, summarizers, extractors, or any consumer that requires word tokens) typically calls this method when it needs a sentence broken into tokens.

Why this is a separate method:
- It isolates and documents the parser's dependency on a pluggable tokenizer object.
- It keeps tokenization concerns out of higher-level code, enabling different tokenizer implementations to be injected without changing the parser's public API.
- As a distinct method it makes testing and mocking tokenization behavior easier.

## Args:
    sentence (str): Input sentence to tokenize. The method forwards this value directly to the tokenizer's to_words method; therefore the allowed types/values are whatever the configured tokenizer accepts. There is no default value.

## Returns:
    Any: The exact return value produced by self._tokenizer.to_words(sentence). Implementations of tokenizer.to_words typically return a sequence (commonly a list) of string tokens, but callers should treat the return as opaque and rely on the concrete tokenizer's contract.

Edge cases:
- If the tokenizer accepts an empty string, the returned value will reflect that (commonly an empty list). If the tokenizer transforms or normalizes text, those effects appear in the returned tokens.

## Raises:
    Any exception raised by self._tokenizer.to_words(sentence) is propagated unchanged.
    - Example possibilities (dependent on tokenizer implementation): TypeError if the sentence type is unacceptable; AttributeError if self._tokenizer is missing or does not implement to_words.

## State Changes:
    Attributes READ:
        - self._tokenizer
    Attributes WRITTEN:
        - (none) — this method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self._tokenizer must be set (non-None) and expose a callable method named to_words.
        - The caller should provide a sentence value compatible with the tokenizer's expectations (usually a str).
    Postconditions:
        - self remains unchanged.
        - The return value equals the direct result of self._tokenizer.to_words(sentence).

## Side Effects:
    - None within this class: no I/O, no external service calls, and no mutation of objects other than the tokenizer result returned to the caller.
    - Side effects (if any) are only those caused by the tokenizer.to_words implementation (e.g., if a tokenizer logs to disk or modifies external state, those effects originate from the tokenizer, not from this method).

