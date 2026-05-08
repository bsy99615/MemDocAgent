# `response_lexer.py`

## `imapclient.response_lexer.TokenSource` · *class*

## Summary:
A thin iterable adapter that constructs a Lexer from input bytes and exposes the lexer's token stream along with a convenience property to read the lexer's current source literal.

## Description:
TokenSource is a minimal wrapper whose purpose is to:
- Instantiate a Lexer for a provided List[bytes] input.
- Expose the lexer's iterator as the TokenSource iterator (so callers can iterate TokenSource to receive bytes tokens).
- Provide a property, current_literal, which forwards to the lexer's current_source.literal.

When to instantiate:
- When you have IMAP response data already split into a List[bytes] (for example, lines or chunks) and you want a simple iterator of lexed token bytes with occasional access to the underlying source literal.

Known callers / typical usage:
- Higher-level response-parsing code that needs a token stream to feed parsers will create TokenSource(text) and iterate it to process bytes tokens. When the caller needs the textual form of the token's source (for diagnostics, reassembly, or context), it may read TokenSource.current_literal.

Motivation and responsibility boundary:
- TokenSource does not implement lexing itself; it delegates tokenization to a Lexer and acts only as an adapter that ties lexer's lifecycle to an iterable object and exposes the lexer's current source literal.

## State:
Public instance attributes (set in __init__):

- lex: Lexer
  - Type: an instance of a Lexer-like class.
  - Required interface (TokenSource expects lex to provide):
    - __init__(text: List[bytes]) — accept the same 'text' passed to TokenSource.
    - __iter__(self) -> Iterator[bytes] — TokenSource stores iter(lex) as src and returns it from __iter__.
    - Attribute current_source — either None or an object with attribute literal (of type bytes).
      - Note: TokenSource assumes this attribute exists; it does not validate it at runtime.

- src: Iterator[bytes]
  - Type: iterator returned by iter(self.lex). Tokens yielded are bytes.

Property:

- current_literal -> Optional[bytes] (annotated)
  - Static typing: annotated Optional[bytes] to indicate that the lexer's current_source may be absent.
  - Runtime behavior: TokenSource returns self.lex.current_source.literal without a runtime None-check. Because the code only asserts non-None under the TYPE_CHECKING (static analysis) branch, at runtime accessing current_literal will raise AttributeError if lex.current_source is None.
  - Practical implication: Treat current_literal as potentially unsafe to access unless you ensure the lexer's current_source exists; either check lex.current_source is not None first or handle AttributeError.

Class invariants:
- After __init__, lex and src are non-None and src is an iterator over the lexer's token stream.
- TokenSource does not modify or cache lex.current_source or its literal; current_literal reflects the lexer's current state at access time.

## Lifecycle:
Creation:
- Call TokenSource(text: List[bytes]).
  - TokenSource will call Lexer(text) and then set src = iter(self.lex).
  - Any exceptions raised by the Lexer constructor or by obtaining its iterator are propagated.

Usage:
- Typical sequence:
    ts = TokenSource(text)
    for token in ts:
        # token is bytes, produced by the lexer's iterator
        try:
            lit = ts.current_literal
        except AttributeError:
            # safe fallback: lex.current_source was None
            lit = None
        # process token and optional lit
- Safety notes:
  - Because current_literal dereferences lex.current_source.literal at runtime, either:
    - Ensure the Lexer sets lex.current_source before you access the property; or
    - Access the underlying lex.current_source with a None-check:
        if ts.lex.current_source is not None:
            lit = ts.current_literal
        else:
            lit = None
    - Or catch AttributeError around ts.current_literal access.

Destruction / Cleanup:
- TokenSource itself has no explicit cleanup API. If the underlying Lexer requires cleanup, callers must manage that separately.

## Method Map:
flowchart TD
    A[TokenSource.__init__(text: List[bytes])] --> B[create Lexer(text)]
    B --> C[src = iter(lex)]
    C --> D[TokenSource.__iter__ returns src]
    E[Client iteration: for token in TokenSource] --> F[iter(src) yields bytes tokens]
    F --> G[Lexer updates lex.current_source and its .literal]
    G --> H[Client reads TokenSource.current_literal -> attempts to return bytes]
    H --> I{lex.current_source is None?}
    I -- yes --> J[AttributeError raised by property access]
    I -- no  --> K[returns bytes literal]

## Raises:
- Exceptions propagated from Lexer:
  - Any exception (TypeError, ValueError, custom parsing exceptions) raised by Lexer(text) or by iter(self.lex) will propagate out of TokenSource.__init__.
- AttributeError from current_literal:
  - If lex.current_source is None at runtime, accessing current_literal will raise AttributeError because the code accesses .literal without a runtime None-check.
  - Implementers/callers should guard or catch AttributeError when reading current_literal if the lexer's current_source may be absent.

## Example:
- Safe usage pattern demonstrating iteration and guarded access to current_literal:

    text = [b'* 1 FETCH (BODY[] {12}', b'Hello world\n)']  # List[bytes]
    ts = TokenSource(text)
    for token in ts:
        # token: bytes
        # Safe read of literal:
        lit = None
        # Option A: explicit check on lex.current_source
        if getattr(ts.lex, 'current_source', None) is not None:
            lit = ts.current_literal
        # Option B: exception-safe access
        # try:
        #     lit = ts.current_literal
        # except AttributeError:
        #     lit = None
        # Process token and lit...

Implementation note for reimplementers:
- To reproduce TokenSource behavior precisely:
  - Provide a Lexer with:
    - __init__(self, text: List[bytes])
    - __iter__(self) -> Iterator[bytes]
    - attribute current_source which may be None or an object with attribute literal: bytes
  - Implement TokenSource exactly as:
    - self.lex = Lexer(text)
    - self.src = iter(self.lex)
    - current_literal property returns self.lex.current_source.literal (no runtime None-check)
    - __iter__ returns self.src
- Because TokenSource omits a runtime check for current_source, the implementer may choose to intentionally keep that behavior for parity or add a safe guard if desired, noting that changing it alters runtime semantics relative to the original implementation.

### `imapclient.response_lexer.TokenSource.__init__` · *method*

## Summary:
Initializes the TokenSource by constructing a Lexer from the provided list of bytes and storing the lexer's iterator on the instance.

## Description:
- Known callers and context:
  - Instantiated by higher-level IMAP response-parsing code that has already split raw IMAP response data into a List[bytes] and needs a token stream for parsing. Typical lifecycle: parser code creates TokenSource(text) at the start of a parse operation, then iterates over the TokenSource to receive token bytes and, occasionally, reads the lexer's current source literal for context or diagnostics.
- Why this is a separate method:
  - The constructor centralizes the minimal, necessary setup for TokenSource: creating the underlying Lexer and obtaining its iterator. Keeping this logic in __init__ ensures TokenSource instances always have a consistent internal state (lex and src) immediately after creation and avoids duplicating lexer-instantiation logic elsewhere. The method deliberately delegates all lexing responsibilities to the Lexer implementation.

## Args:
    text (List[bytes]):
        A sequence (list) of bytes objects representing the input to be lexed (for example, lines or chunks from an IMAP response).
        - Type constraint: the function expects a list-like object whose elements are bytes; passing other types may cause errors from the Lexer.
        - No default value.

## Returns:
    None
    - Effect: initializes instance attributes; no explicit return value.

## Raises:
    Any exception raised by the Lexer constructor or by obtaining an iterator over the Lexer.
    - Common propagation points:
        - Exceptions raised during Lexer(text) (e.g., TypeError, ValueError, or lexer-specific parsing errors) will propagate out of TokenSource.__init__.
        - Exceptions raised when calling iter(self.lex) (if the Lexer implements __iter__ in a way that can raise) will also propagate.
    - TokenSource.__init__ itself does not raise AttributeError or similar for its own attributes; however, subsequent accessors (e.g., a current_literal property) may raise if the lexer's state is absent — those are not raised by __init__.

## State Changes:
- Attributes READ:
    - None (the method does not read any pre-existing self.<attr> fields).
- Attributes WRITTEN:
    - self.lex: set to the newly constructed Lexer(text).
    - self.src: set to iter(self.lex) — an iterator that yields the lexer's tokens (bytes).

## Constraints:
- Preconditions:
    - Caller must supply text as a List[bytes] (or equivalent sequence of bytes). If elements are not bytes, the Lexer implementation may raise.
    - The TokenSource instance should not be relied upon until __init__ completes successfully; on exception, no guarantees about instance attributes are provided.
- Postconditions:
    - On successful return:
        - self.lex is an instance of the Lexer class (or whatever lexing implementation is used) constructed with the same text argument.
        - self.src is a valid iterator obtained from iter(self.lex) and is expected to yield bytes tokens when iterated.
    - Any exceptions raised by constructing the Lexer or obtaining its iterator are propagated and prevent the object from being used as intended.

## Side Effects:
- Direct I/O: None performed by TokenSource.__init__ itself.
- Indirect side effects: any side effects performed by the Lexer constructor (text processing, validation, memory allocation, logging, etc.) occur during this call and will be visible to callers.
- External calls: delegates to the Lexer implementation; TokenSource does not call external services directly.

## Implementation notes for reimplementers:
- Implement exactly these two operations in order:
    1. Construct the lexer with the provided text and assign to self.lex.
    2. Obtain an iterator from the lexer and assign to self.src.
- Do not add runtime checks or different error handling if you want parity with the original behavior — exceptions from the Lexer should be allowed to propagate.

### `imapclient.response_lexer.TokenSource.current_literal` · *method*

## Summary:
Read-only @property that returns the lexer's current token literal (Optional[bytes]) without mutating TokenSource state.

## Description:
This property exposes the value of self.lex.current_source.literal at the moment it is accessed. It is implemented as a simple, in-place accessor (decorated with @property) and does not perform any runtime validation.

Access pattern:
- The property evaluates and returns the nested attribute expression self.lex.current_source.literal.
- There is a TYPE_CHECKING-only assertion in the implementation that helps static type checkers assume current_source is not None; that assertion is not executed at runtime.

Known callers:
- No direct call sites were discovered during repository analysis. Callers in client code that need the literal payload of the token currently tracked by the Lexer may access this property.

Why this is separated as a property:
- Encapsulates the nested access path so callers do not need to reference Lexer internals directly.
- Centralizes the documented return type and behavior in one place.
- Provides a single, stable accessor for the current token literal.

## Args:
    None

## Returns:
    Optional[bytes]
        - bytes: the literal payload for the current token when present.
        - None: indicates the current token exists but its literal payload is absent (the lexer represents the absence of a literal with None).

    Notes:
        - The returned value is exactly self.lex.current_source.literal at call time.
        - If current_source exists but its literal attribute is None, this property returns None.

## Raises:
    AttributeError:
        - Raised if self.lex.current_source is None at runtime (accessing .literal on None yields 'NoneType' object has no attribute 'literal').
        - As TokenSource.__init__ sets self.lex, a missing self.lex would also manifest as an AttributeError, but normal construction of TokenSource ensures self.lex exists.

## State Changes:
    Attributes READ:
        - self.lex
        - self.lex.current_source
        - self.lex.current_source.literal

    Attributes WRITTEN:
        - None (the property performs no mutation of TokenSource or Lexer state)

## Constraints:
    Preconditions:
        - TokenSource must have been constructed normally (TokenSource.__init__ assigns self.lex).
        - If the caller expects a non-exceptional return, the caller must ensure self.lex.current_source is not None before accessing this property.

    Postconditions:
        - No mutation occurs to TokenSource or the Lexer.
        - The return value (if any) reflects the literal attribute of the lexer's current_source at the exact time of access.

## Side Effects:
    - None. The property does not perform I/O, network access, or side-effecting mutations.

## Implementation notes:
    - The code contains a guard within "if TYPE_CHECKING: assert self.lex.current_source is not None" which aids static type analysis only; it does not prevent runtime AttributeError when current_source is None.
    - Because this is a direct accessor, callers that cannot guarantee current_source is present should check self.lex.current_source is not None before reading this property to avoid runtime exceptions.

### `imapclient.response_lexer.TokenSource.__iter__` · *method*

## Summary:
Returns the underlying iterator over token bytes maintained by the TokenSource instance; does not create a new iterator and does not modify object state.

## Description:
This method implements the Python iteration protocol for TokenSource so the object can be used in iteration contexts (for-loops, any call to iter(...)). Internally TokenSource.__init__ sets self.src = iter(self.lex) where self.lex is a Lexer that produces token values as bytes; this method simply returns that iterator.

Known callers and contexts:
- Any code that iterates over a TokenSource instance, for example:
  - for token in token_source: ...
  - list(token_source) or iter(token_source)
- The method is used during the lexical/tokenization stage of parsing IMAP responses to provide a stream of token bytes to higher-level consumers (parsers, response handlers).

Why this is a separate method:
- It formalizes the iteration interface so TokenSource instances behave like standard Python iterables.
- Returning the stored iterator (rather than re-wrapping or creating a new iterator) preserves the lexical stream position and avoids duplicating iterator construction logic in multiple call sites.

## Args:
This method takes no parameters beyond self.

## Returns:
Iterator[bytes]: the exact iterator object stored in self.src. Values yielded by this iterator are bytes objects representing lexical tokens produced by the underlying Lexer.
- Normal behavior: yields successive token bytes until the iterator is exhausted.
- Edge-case returns: when exhausted the iterator raises StopIteration to signal completion.

## Raises:
- AttributeError: if self.src does not exist (for example, if __init__ has not been successfully run or self.src was deleted). This is not raised by the method itself but will occur when attempting to access the missing attribute.
- No other exceptions are raised by this method directly.

## State Changes:
Attributes READ:
    - self.src

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - The TokenSource instance must have been initialized such that self.src exists and is an Iterator[bytes] (TokenSource.__init__ sets this).
    - The underlying Lexer must be functional and able to produce bytes tokens if iteration is to yield values.

Postconditions:
    - The TokenSource object is unchanged by this call.
    - The returned object is the same iterator stored on the instance; subsequent iteration proceeds from the iterator's current position.

Important behavioral note:
    - Multiple calls to iter(token_source) (or repeated use in for-loops) return the same iterator object (self.src). This means a second iteration will continue from the current iterator position rather than restarting from the beginning.

## Side Effects:
    - None. The method performs no I/O and does not mutate external objects.

## `imapclient.response_lexer.Lexer` · *class*

*No documentation generated.*

### `imapclient.response_lexer.Lexer.__init__` · *method*

## Summary:
Initializes the lexer with a lazy sequence of response sources and sets the tracker for the currently-active source to None, preparing the instance for tokenization without performing any lexical work.

## Description:
This constructor prepares the Lexer to tokenize a sequence of response records by creating a generator that will produce LiteralHandlingIter instances for each element of the provided text list. It does not instantiate those LiteralHandlingIter objects immediately — instantiation is deferred until the generator is iterated (lazy construction). During subsequent iteration over the Lexer, the generator is consumed and the Lexer updates current_source to the LiteralHandlingIter being processed.

Known callers and lifecycle context:
- The Lexer is typically constructed at the start of a response-lexing/parsing stage where a higher-level reader/collector has produced a sequence of response records (the `text` argument). After construction, the parser/consumer iterates over the Lexer (or calls its __iter__), which triggers creation of the LiteralHandlingIter instances and begins token streaming.
- This method is invoked during the initialization phase of the lexing pipeline — before any tokenization or reading methods (e.g., read_token_stream or __iter__) are called.

Why this is a separate method:
- The constructor's purpose is solely to establish the lexer's initial state (the lazy source generator and the current-source slot). Separating this setup from tokenization logic keeps initialization fast and side-effect free and ensures that validation or protocol errors produced by LiteralHandlingIter are deferred until the actual iteration phase.

## Args:
    text (List[bytes]):
        A list-like sequence whose elements will be forwarded to LiteralHandlingIter via a generator expression.
        - Annotated type matches the source signature (List[bytes]).
        - Runtime note: elements may be either bytes (a single response text) or a (bytes, bytes) tuple (src_text, literal). Each generator element is passed directly to LiteralHandlingIter, which enforces protocol checks for tuple forms.

## Returns:
    None

## Raises:
    None raised directly by this constructor.
    - Note: Because sources are produced by a generator expression, any exceptions from LiteralHandlingIter construction or validation (for example, ProtocolError when a tuple element lacks the expected literal marker) will occur later when the generator is iterated, not during this __init__ call.

## State Changes:
    Attributes READ:
        - None (the constructor does not read other instance attributes)

    Attributes WRITTEN:
        - self.sources: set to a generator expression that yields LiteralHandlingIter(chunk) for each chunk in the provided text
        - self.current_source: set to None (type: Optional[LiteralHandlingIter])

    Attribute types after call:
        - self.sources: generator[LiteralHandlingIter] (lazy; no LiteralHandlingIter instances created yet)
        - self.current_source: None

## Constraints:
    Preconditions:
        - The caller must supply a sequence compatible with iteration (the parameter is annotated as List[bytes]).
        - Practical runtime expectation: elements should be bytes or (bytes, bytes) tuples so that LiteralHandlingIter can accept them when the generator is consumed.

    Postconditions:
        - self.sources is a lazily-evaluated generator; iterating it will yield LiteralHandlingIter instances constructed from the original sequence elements.
        - self.current_source is guaranteed to be None until the lexer begins iterating over self.sources, at which point the attribute will be updated by the lexer's iteration logic.

## Side Effects:
    - No I/O, network, or file operations are performed by this constructor.
    - No exceptions are raised during construction from LiteralHandlingIter because creation of those objects is deferred; however, consuming self.sources may raise exceptions originating from LiteralHandlingIter or its validations.
    - No mutation to objects outside self occurs in this method.

### `imapclient.response_lexer.Lexer.read_until` · *method*

## Summary:
Consume bytes from an iterator until an unescaped terminal byte is seen, assemble and return a bytearray of the consumed bytes with one final terminal byte appended. This advances the provided iterator past the terminal byte.

## Description:
Iterate over stream_i (an iterator yielding integer byte values) and accumulate bytes into a bytearray token. The loop ends when an unescaped end_char is encountered; on successful completion the method appends one final end_char to the returned token. When escape is enabled, a BACKSLASH byte acts as an escape introducer and controls how the next byte is treated (see detailed rules below).

Known callers and context:
- This method is intended for use by lexer/tokenizer routines that parse delimited IMAP response elements (e.g., quoted strings or other delimited tokens). Callers request the lexer to read until a delimiter and rely on this method to consume the delimiter and any intervening escapes.
Why separate:
- The logic mixes iterator consumption, explicit next() calls, and non-trivial escape semantics; extracting it avoids duplication and centralizes error handling for unterminated sequences.

## Args:
    stream_i (PushableIterator):
        An iterator-like object yielding integer byte values (0..255). It must support iteration (for ... in stream_i) and direct next(stream_i) calls. When exhausted it must raise StopIteration.
    end_char (int):
        Integer byte value that terminates the read when encountered unescaped.
    escape (bool, default True):
        If True, treat BACKSLASH as an escape introducer with the semantics described below. If False, BACKSLASH is treated as an ordinary byte.

## Returns:
    bytearray:
        A bytearray containing:
          - All bytes read from stream_i up to the point of termination (these bytes may include bytes that were read after an escape introducer and therefore represent escaped content), and
          - A single appended end_char byte at the end of the returned bytearray (this appended terminal byte is always present on successful return).
        Notes:
          - If an end_char appears in the stream as the immediate byte following an escape introducer, that end_char is treated as content and will appear inside the returned bytearray (not as the final appended terminator); the method will continue until it later encounters an unescaped end_char which becomes the appended terminator.
          - The method does not return when the stream ends without encountering an unescaped end_char; in that case it raises ValueError.

## Raises:
    ValueError:
        Raised with message "No closing '<char>'" (chr(end_char) substituted) when the iterator is exhausted before an unescaped end_char is found. This happens in two situations:
          1. The for-loop finishes normally because the iterator yielded no more items (no break occurred).
          2. During escape processing: BACKSLASH was read as the last item and the subsequent next(stream_i) call raises StopIteration.
    Any exceptions raised by stream_i (e.g., TypeError if yielded items are not integers) propagate unchanged.

## State Changes:
    Attributes READ:
        - None of self.<attr> attributes are accessed by this method.
    Attributes WRITTEN:
        - None of self.<attr> attributes are modified by this method.

## Constraints:
    Preconditions:
      - stream_i must be an iterator yielding integer byte values and support next().
      - end_char must be an integer byte value.
      - The module-level constant BACKSLASH must be defined and hold the integer byte value used as the escape introducer if escape=True.
      - Caller should be prepared to handle ValueError for unterminated input.
    Postconditions:
      - On success, stream_i has been advanced past the terminating (unescaped) end_char.
      - The returned bytearray ends with a single end_char byte appended by this method.
      - If a ValueError is raised, the iterator was consumed until exhaustion or until StopIteration occurred while attempting to read after an escape.

## Escape semantics (precise rules):
    When escape is True and the method reads a BACKSLASH byte:
      - The method immediately reads the next byte via next(stream_i).
      - If next byte equals BACKSLASH or equals end_char:
          * The escaper (BACKSLASH) is NOT appended.
          * The next byte (either BACKSLASH or end_char) is appended to the token as content.
          * The read does NOT terminate even if the appended byte equals end_char (escaped end_char is considered content).
      - If next byte is any other value:
          * The escaper (BACKSLASH) is appended to the token (treating the escape as invalid for that following byte).
          * Then the next byte is appended as normal content.
    When escape is False:
      - BACKSLASH bytes are appended like any other byte; no special handling occurs.

## Side Effects:
    - Consumes items from stream_i (calls next() and iterates).
    - Does not perform file, network, or external I/O.
    - Does not mutate objects outside of consuming the provided iterator and returning a new bytearray.

## Examples (illustrative descriptions):
    - Given end_char = ord('"') and BACKSLASH as the escape introducer:
        * Stream: b'a' b'\\' b'"' b'c' b'"' ...
          Behavior: 'a' appended, BACKSLASH + '"' treated as escaped quote -> '"' appended to token, 'c' appended, then an unescaped '"' later terminates and the method appends the final '"' terminator to the returned bytearray. Returned content thus contains the inner escaped '"' plus the final appended '"'.
        * Stream: b'a' b'\\' b'x' b'"' ...
          Behavior: BACKSLASH followed by 'x' is invalid escaping -> BACKSLASH appended then 'x' appended; the later unescaped '"' terminates and is appended once at return.
        * If the stream ends before an unescaped end_char (including when BACKSLASH is final and next(stream_i) would raise StopIteration), ValueError("No closing '\"'") is raised.

### `imapclient.response_lexer.Lexer.read_token_stream` · *method*

## Summary:
Produce a stream of lexical tokens (as bytearray objects) from a byte-oriented pushable iterator, advancing the iterator and yielding complete tokens while preserving token boundaries for quoted strings, bracketed sequences, words, and single-character special tokens. This method does not modify Lexer instance attributes other than calling its helper read_until.

## Description:
This method implements the core tokenization loop used by the Lexer's iteration pipeline. Known callers:
- Lexer.__iter__: passes an iterator over a source (the method's stream_i) and consumes the bytearray tokens produced here, converting them to bytes for downstream use. Typical lifecycle stage: called during lexing of a single source chunk to break the raw byte stream into IMAP tokens.

Why a separate method:
- The logic for skipping whitespace, recognizing word characters, handling quoted strings and bracketed sequences, and yielding tokens is non-trivial and reused for each source; separating it keeps __iter__ concise and isolates tokenization concerns (including use of the helper read_until which handles nested/terminated sequences).

## Args:
    stream_i (PushableIterator or iterator-like):
        - Type: an iterator that yields integer byte values (ints, typically 0–255) and supports a push(value) operation to "un-read" a byte so it will be returned again on the next iteration.
        - Required behavior: pushing a previously-read integer must cause it to be returned before further items from the underlying iterator.
        - Note: The implementation expects int tokens (byte values). Passing an iterator that yields other types may break consumers.

## Returns:
    Iterator[bytearray]:
        - Yields successive tokens as bytearray objects (not bytes).
        - Token shapes:
            * Word token: a sequence of bytes where every byte is in NON_SPECIALS (the module constant). Returned as a single bytearray of those bytes.
            * Bracketed sequence: when encountering an OPEN_SQUARE byte, yields a bytearray beginning with OPEN_SQUARE, containing everything up to and including the matching CLOSE_SQUARE as produced by read_until(..., CLOSE_SQUARE, escape=False). The returned bracket token includes both bracket bytes.
            * Quoted string: when encountering DOUBLE_QUOTE as the first byte of a token, the method asserts (via assert_imap_protocol) that no bytes have been accumulated for the current token, then uses read_until(..., DOUBLE_QUOTE) to read through the closing DOUBLE_QUOTE (honoring escape semantics). The yielded token includes both surrounding DOUBLE_QUOTE bytes and inner contents.
            * Single-character special token: any non-word, non-whitespace, non-open-square, non-double-quote byte encountered after (or between) tokens is yielded as a one-byte bytearray containing that byte.
        - End-of-stream behavior: when the underlying iterator ends, if a token has been partially accumulated the method yields that token before returning; otherwise it returns without yielding further items.

## Raises:
    ValueError:
        - Propagated when read_until detects an unterminated sequence (e.g., a quoted string or bracketed sequence with no closing delimiter). read_until raises ValueError("No closing '%s'" % chr(end_char)) if the matching end_char is not found before the stream is exhausted or StopIteration occurs.
    Exception from assert_imap_protocol:
        - When a DOUBLE_QUOTE is encountered but a token is already being accumulated (i.e., a quoted string immediately following non-empty token bytes), the method calls assert_imap_protocol(not token). If that condition fails, assert_imap_protocol will raise (typically indicating a protocol violation). The exact exception type depends on the assert_imap_protocol implementation; this method propagates whatever it raises.

## State Changes:
    Attributes READ:
        - self.read_until (method): the helper is retrieved and invoked to read until matching delimiters (used for bracketed sequences and quoted strings).
    Attributes WRITTEN:
        - None. This method does not assign or mutate any self.<attr> fields on the Lexer instance.

## Constraints:
    Preconditions:
        - stream_i must be an iterator yielding integer byte values and must implement push(value) to allow a single byte to be pushed back onto the stream.
        - The module-level constants (WHITESPACE, NON_SPECIALS, OPEN_SQUARE, CLOSE_SQUARE, DOUBLE_QUOTE) define classification of bytes and must be correct for IMAP tokenization semantics.
    Postconditions:
        - The stream_i will be advanced to the position after the last character consumed for the yielded tokens; if a non-whitespace byte was read while skipping whitespace at the start of a loop iteration it is pushed back immediately so that token recognition begins at that byte.
        - Every yielded bytearray is a complete token as defined above: word token, bracketed token (including both brackets), quoted token (including both quotes), or single-byte special token.
        - If an unterminated bracket or quoted sequence was encountered, a ValueError is raised and no further tokens are yielded from this invocation.

## Side Effects:
    - Uses stream_i.push(nextchar) to push back a byte after skipping leading whitespace; this mutates the provided iterator's push buffer.
    - Calls self.read_until to consume bytes until a closing delimiter; read_until itself may consume further items from stream_i and raise ValueError on unterminated constructs.
    - No I/O, no network or file operations, and no mutation of objects outside of the provided iterator's push state and the use of local variables.

### `imapclient.response_lexer.Lexer.__iter__` · *method*

## Summary:
Produces a generator of immutable token byte-strings for all configured input sources, updating the lexer's current_source to reflect the source being processed.

## Description:
This generator method orchestrates token emission for the Lexer. For each source produced by self.sources it:
- sets self.current_source to that source object, and
- passes iter(source) into read_token_stream, yielding every token produced by that lower-level tokenizer as an immutable bytes object (bytes(tok)).

Known callers / invocation contexts:
- Any consumer that iterates the Lexer (for tok in lexer:) to obtain the stream of tokens for parsing IMAP responses or for higher-level response processing.
- Executed during the tokenization stage immediately after a Lexer has been constructed with input text chunks.

Why this logic is separate:
- It separates source-management (multiple input chunks and maintaining current_source for diagnostics) from the byte-level parsing done by read_token_stream. This separation keeps the orchestration simple and allows read_token_stream to focus on parsing a single iterator.

## Args:
This method takes no explicit arguments (self only).

## Returns:
Iterator[bytes]
- Each yield is an immutable bytes object converted from the bytearray token emitted by read_token_stream.
- Possible values:
  - Typical token bytes (e.g., atom, quoted string including quotes, single-character special tokens).
  - Empty bytes (b'') if read_token_stream yields an empty bytearray token.
- Edge cases:
  - If self.sources is empty, the iterator finishes immediately (no yields).
  - If read_token_stream yields large tokens (e.g., literal content), they are returned as a bytes copy of the underlying bytearray.

## Raises:
This method does not raise exceptions itself but propagates exceptions from its callees:
- ValueError: propagated from read_until (called by read_token_stream) for unterminated constructs (e.g., missing closing quote or bracket).
- AssertionError: propagated from assert_imap_protocol inside read_token_stream when protocol assumptions are violated.
- TypeError, StopIteration, or other exceptions raised by iter(source) or by read_token_stream will also propagate to the caller.

## State Changes:
Attributes READ:
- self.sources — consumed (iterated) as the method walks each source.
Attributes WRITTEN:
- self.current_source — assigned to each source object immediately before tokenizing that source. If no sources are processed, current_source remains as previously set (typically None after __init__).

## Constraints:
Preconditions:
- Lexer must be initialized such that:
  - self.sources is an iterable of source objects compatible with read_token_stream. In this implementation, __init__ constructs self.sources as a generator of LiteralHandlingIter objects (one per input chunk), so each source must produce an iterator acceptable to read_token_stream.
  - self.read_token_stream expects a PushableIterator-like iterator; therefore iter(source) must provide the interface and behavior that read_token_stream relies on.
- Consumers should be aware that self.sources is created as a generator expression in __init__ (one-time iterator); attempting to iterate the same Lexer multiple times will likely yield nothing on subsequent iterations because the generator is exhausted.

Postconditions:
- After exhaustion, self.current_source will reference the last source processed (or remain unchanged if none were processed).
- self.sources will have been advanced to exhaustion; no tokens remain to be produced from this Lexer instance unless the caller reinitializes sources.

## Side Effects:
- Mutates self.current_source as described above.
- Consumes (exhausts) self.sources (the generator of sources), making iteration single-use for the provided source generator.
- No direct I/O, network calls, or modifications to external objects are performed by this method itself; any side effects from read_token_stream or iter(source) (including exceptions) are propagated to the caller.

## Example usage (illustrative):
- A typical consumer iterates the Lexer once to obtain tokens for parsing: for each token yielded by iter(lexer) the consumer decodes/inspects the bytes returned and advances the parsing pipeline.

## `imapclient.response_lexer.LiteralHandlingIter` · *class*

## Summary:
Represents an IMAP response record that may include an inline literal and provides an iterator factory that returns a fresh PushableIterator over the response source bytes.

## Description:
LiteralHandlingIter encapsulates a single response record produced by the IMAP client server-reader, where a response record is either:
- a bytes object containing the response text (no attached literal), or
- a (bytes, bytes) tuple where the first element is the response text ending with the bytes character b"}" (the protocol marker) and the second element is the associated literal data.

This class is instantiated by the response-lexing/parsing pipeline when a higher-level reader has collected a response record and wants:
- to preserve the parsed literal data separately, and
- to obtain independent iterators over the source bytes for lexical analysis (the iterators support push/unread semantics via PushableIterator).

Known callers / typical scenarios:
- Created from responses yielded by the network-level IMAP reader/collector that returns either raw bytes or (src_text, literal) pairs.
- __iter__ is called by lexers/parsers that need to iterate over the response bytes and sometimes push tokens back.

Motivation and responsibility boundary:
- Responsibility: hold the paired source-text and optional literal, validate the expected protocol marker for tuple records, and provide fresh pushable iterators over the source text.
- Boundary: does not parse tokens itself, does not consume literal data, and does not manage networking or I/O.

## State:
- src_text (bytes-like expected)
  - Type: typically bytes (iterable of ints); the implementation sets this unconditionally in __init__.
  - Valid values: any object for which endswith(b"}") (when tuple form) is valid and which is iterable for constructing a PushableIterator.
  - Invariant: always present after __init__; represents the textual portion of the response record.
  - Note: the class does not enforce that src_text is bytes; callers should pass bytes to match downstream expectations.

- literal (Optional[bytes])
  - Type: bytes when present, otherwise None.
  - When set: assigned from the second element of a tuple resp_record; represents appended literal data that accompanies the src_text.
  - When absent: None indicates no literal data for this record.

Class invariants:
- After construction, src_text is defined and literal is either bytes or None.
- Calling __iter__ must always produce a new PushableIterator that wraps src_text and does not mutate LiteralHandlingIter's attributes.

## Lifecycle:
Creation:
- Constructor signature: LiteralHandlingIter(resp_record: Union[Tuple[bytes, bytes], bytes])
- Required argument:
  - resp_record: either a bytes object, or a tuple (src_text, literal) where both are expected to be bytes.
- Behavior on creation:
  - If resp_record is a tuple, src_text is set to resp_record[0] and literal to resp_record[1].
  - In tuple case, the implementation asserts that src_text.endswith(b"}"); if this is false, a ProtocolError is raised (see Raises).
  - If resp_record is bytes, src_text is set to that value and literal is set to None.
- Caller constraints: pass bytes (or tuple of bytes) to avoid attribute or type errors. Passing incompatible types may raise AttributeError/TypeError from underlying operations.

Usage:
- Obtain an iterator by calling iter(instance) or using the instance in an iterator context (for ... in ...).
- Each call to iter(instance) returns a fresh PushableIterator with its own push buffer. Multiple iterators may be active simultaneously without interfering with one another.
- Typical order: construct instance → call iter() to get an iterator → use the PushableIterator for lexical scanning (calls to next() and push()) → discard iterator when finished. The LiteralHandlingIter itself is immutable for iteration purposes.

Destruction / cleanup:
- No external resources to release. There is no close() or context-manager protocol on this class. Python's garbage collection handles cleanup.

## Method Map:
graph LR
    Init[__init__(resp_record)] --> SetSrcText[src_text set]
    Init --> SetLiteral[literal set or None]
    SetSrcText --> IterCall[__iter__()]
    IterCall --> NewPushable[PushableIterator(self.src_text) (fresh)]
    NewPushable --> Consumer[caller uses returned iterator (next/push)]
    Note[Multiple iter() calls produce independent PushableIterator instances]

(Explanation: __init__ sets src_text and literal. __iter__ constructs and returns a new PushableIterator over src_text. Consumers then operate on that iterator.)

## Raises:
- ProtocolError (from util.assert_imap_protocol) raised by __init__ when resp_record is a tuple and src_text.endswith(b"}") is False.
  - Trigger condition: resp_record is a tuple and the first element does not end with the literal-end marker b"}".
  - Practical effect: indicates a server response that violates the expected IMAP protocol format for literal markers.

- AttributeError or TypeError during __init__ if resp_record is an unexpected type:
  - Example: if resp_record is a tuple but resp_record[0] lacks endswith (not bytes-like), attribute access will raise AttributeError. The implementation does not explicitly validate element types beyond using them.
  - Caller responsibility: ensure resp_record follows the expected shapes (bytes or (bytes, bytes)).

- TypeError during __iter__:
  - When PushableIterator is constructed, it calls iter(self.src_text). If src_text is not iterable, iter() will raise TypeError. This will propagate from __iter__.
  - Caller responsibility: ensure src_text is iterable (typically bytes).

## Example:
- Typical creation with no literal:
  - Create with a bytes response record; literal will be None and src_text holds the bytes. Obtain an iterator by calling iter(instance) which yields integer byte values (0–255) when consumed.

- Typical creation with literal:
  - Create with (src_text, literal) where src_text ends with b"}"; the instance stores literal as bytes. If src_text does not end with b"}", construction raises ProtocolError.

- Typical usage sequence (described):
  1. Instantiate: provide either bytes or (bytes, bytes).
  2. Call iter(instance) to get a PushableIterator over src_text.
  3. Use next() / for-loop on the returned PushableIterator; the lexer/parser may call push(value) on the PushableIterator to unread tokens.
  4. Access instance.literal if the caller needs the literal data attached to the response record.

Notes:
- This class purposefully separates the literal payload from the textual source so lexers can operate on src_text (via pushable iterators) while the literal bytes are available for later processing. The class does not parse tokens or interact with network layers.

### `imapclient.response_lexer.LiteralHandlingIter.__init__` · *method*

## Summary:
Store the response text and optional inline literal from resp_record on the instance, validating the expected literal-end marker when a literal is present; after return self.src_text and self.literal are initialized.

## Description:
- Known callers and context:
    - Constructed by the IMAP response-lexing/parsing pipeline after a network-level reader/collector yields a response record. The reader provides either:
        - a bytes object containing only the response text, or
        - a (src_text, literal) tuple where src_text is the textual portion and literal is the following literal payload bytes.
    - Typical lifecycle: the higher-level reader collects a response record → LiteralHandlingIter(resp_record) is created to preserve any literal payload separately and establish an invariant src_text/literal pair for downstream lexers/parsers that will request iterators over src_text.
- Rationale for a separate initializer:
    - Centralizes construction-time validation and invariant establishment (guarantee that src_text is set and literal is either bytes or None) so downstream code can rely on those attributes without repeating checks.

## Args:
    resp_record (Union[Tuple[bytes, bytes], bytes]):
        - If a bytes object: treated as the response text; no literal is attached and self.literal will be set to None.
        - If a tuple: treated as (src_text, literal).
            - src_text is taken from resp_record[0] and must end with the bytes marker b"}" (this is checked).
            - literal is taken from resp_record[1] and assigned to self.literal.
        - Caller responsibility: provide either a bytes or a two-element tuple whose elements are bytes-like. Passing other shapes/types may raise standard Python exceptions described below.

## Returns:
    None — standard initializer; sets instance attributes and returns no value.

## Raises:
    Exception (as raised by util.assert_imap_protocol):
        - Condition: resp_record is a tuple and the check self.src_text.endswith(b"}") evaluates to False.
        - Note: this method calls util.assert_imap_protocol(check, value); the specific exception type and message depend on that helper's implementation.
    AttributeError:
        - Condition: resp_record is a tuple but resp_record[0] does not provide an endswith attribute (e.g., not bytes-like), causing the call to resp_record[0].endswith(b"}") to fail.
    IndexError:
        - Condition: resp_record is a tuple with fewer than two elements; accessing resp_record[1] will raise IndexError.
    TypeError:
        - Condition: resp_record is neither bytes nor a tuple-like object supporting indexing; attempting to index or call methods on it can raise TypeError.
    - These are direct consequences of the operations performed; this initializer does not catch or wrap these exceptions.

## State Changes:
- Attributes READ:
    - The constructor reads the resp_record parameter (no pre-existing self attributes are read).
- Attributes WRITTEN:
    - self.src_text: set to resp_record if resp_record is bytes, otherwise set to resp_record[0].
    - self.literal: set to resp_record[1] when resp_record is a tuple; set to None when resp_record is bytes.
    - The implementation annotates self.literal as Optional[bytes].

## Constraints:
- Preconditions:
    - Caller should supply resp_record as either:
        - bytes, or
        - a tuple-like with at least two elements where the first element supports endswith(b"}").
    - In tuple form, callers should ensure that src_text ends with b"}" to avoid the assertion failure.
- Postconditions:
    - On successful return, self.src_text is defined and holds the textual response portion.
    - On successful return, self.literal is either the provided literal bytes (tuple case) or None (bytes case).
    - No other instance attributes are modified.

## Side Effects:
    - No I/O, no network calls, and no mutation of objects beyond assigning to the instance's attributes.
    - May raise the exceptions listed above depending on the shape and types of resp_record and the result of the assert_imap_protocol check.

### `imapclient.response_lexer.LiteralHandlingIter.__iter__` · *method*

## Summary:
Return a fresh PushableIterator that will iterate over the object's source bytes without mutating the LiteralHandlingIter instance.

## Description:
Known callers and context:
- Called by the response-lexing / parsing pipeline when code needs to iterate the bytes that make up an IMAP response segment (the "source text" previously stored on this object).
- Typical lifecycle stage: invoked after a LiteralHandlingIter has been constructed from a response record and a consumer (lexer/parser) needs an iterator with the ability to push/unread tokens during lexical analysis.
- Why this is a separate method: the method provides a small, explicit factory for a PushableIterator so callers receive an independent iterator with its own push buffer. Keeping iterator construction in a dedicated __iter__ method follows Python iterator protocol and keeps push/unread semantics encapsulated in PushableIterator rather than spreading that logic into the lexer or into LiteralHandlingIter.

## Args:
- None

## Returns:
- PushableIterator
  - A newly-created PushableIterator instance constructed with self.src_text as the underlying iterable.
  - The returned iterator yields integer token values (typically 0–255 when the underlying source is a bytes object).
  - The PushableIterator is independent of any previous iterator returned from earlier calls to this method (i.e., each call returns a fresh wrapper with its own pushed buffer).

## Raises:
- TypeError:
  - Triggered if self.src_text is not iterable. This occurs during PushableIterator construction (iter(self.src_text) will raise TypeError).
- No other exceptions are raised directly by this method. It does not itself iterate or consume the source and therefore does not raise StopIteration here.

## State Changes:
- Attributes READ:
  - self.src_text
- Attributes WRITTEN:
  - None (the method does not modify the LiteralHandlingIter instance)

## Constraints:
- Preconditions:
  - The LiteralHandlingIter instance must have been initialized so that self.src_text is set (the class __init__ always sets src_text).
  - self.src_text must be an iterable (commonly a bytes object). If it is not iterable, constructing the PushableIterator will raise TypeError.
- Postconditions:
  - A PushableIterator wrapping self.src_text is returned.
  - The LiteralHandlingIter object's attributes (including self.src_text and self.literal) are unchanged by the call.

## Side Effects:
- None external: no I/O, no network or file access.
- Creates a new PushableIterator object (heap allocation) but does not consume or advance self.src_text itself; any iteration/consumption happens later when the caller uses the returned iterator.

## `imapclient.response_lexer.PushableIterator` · *class*

## Summary:
A small iterator wrapper that allows previously-consumed items to be "pushed" back and returned again on subsequent iteration. It behaves as a forward iterator over an underlying iterable of byte-values (ints) and provides a LIFO push buffer.

## Description:
PushableIterator is used when an iteration consumer sometimes needs to "un-read" one or more items and have them returned again on the next calls to next()/__next__(). Typical callers are lexical analyzers or parsers that read a stream of bytes (or other integer tokens) and occasionally need to backtrack one token. In this codebase it is instantiated with a bytes object (or any iterable of ints) and used where a small lookahead/unread facility is required.

Motivation and responsibility boundary:
- Responsibility: Provide a minimal, efficient mechanism to interleave items from an underlying iterator with items explicitly pushed back by the consumer.
- Boundary: It does not perform buffering beyond the pushed list and does not alter the underlying iterator except by consuming from it. It does not validate pushed items beyond appending them to the internal buffer.

## State:
- NO_MORE (class attribute)
  - Type: object
  - Purpose: sentinel constant available to callers; defined but not used internally by this class.
  - Valid values: singleton object

- self.it
  - Type: Iterator[int]
  - Set in __init__ as iter(it) where the initializer parameter is expected to be a bytes-like iterable (each element an int 0–255) or any iterable producing ints.
  - Invariant: always an iterator object; may raise StopIteration when exhausted.

- self.pushed
  - Type: List[int]
  - Initialized as an empty list in __init__.
  - Semantic invariant: acts as a LIFO stack of ints that will be returned before any further values are read from self.it.
  - Valid values: list of integer tokens that the user pushed back; no enforced range but typical values are 0–255 when underlying source is bytes.

Notes on __init__ parameter:
- __init__(self, it: bytes)
  - Expected: a bytes object is typical (iterating over bytes yields ints 0–255).
  - Constraint: the argument must be iterable; otherwise constructing iter(it) will raise TypeError.
  - The class does not enforce the element type at runtime, so passing non-int iterables will not be type-checked but will likely break consumers that expect ints.

Class invariants:
- self.pushed is always a list (possibly empty).
- Items returned by __next__ are drawn from pushed (LIFO) until empty, then from self.it.
- When both pushed is empty and self.it is exhausted, __next__ raises StopIteration.

## Lifecycle:
- Creation:
  - Instantiate by calling PushableIterator(it) where it is typically a bytes object or any iterable of ints.
  - Example creation form: PushableIterator(b"abc")

- Usage:
  - The instance is an iterator: use in for-loops, pass to next(), or iterate manually.
  - Typical sequence:
    1. Call next(instance) (or iterate) to obtain the next int token.
    2. If the consumer decides the token should be re-consumed later, call instance.push(token).
    3. Subsequent calls to next() will return the most recently pushed token first (LIFO).
  - push(item) may be called at any time between next() calls. There is no explicit ordering requirement beyond LIFO semantics for pushed items.

- Destruction / Cleanup:
  - No explicit cleanup is required. The object has no external resources or file handles.
  - It does not implement context manager protocol or a close() method.

## Method Map:
graph LR
    Init[__init__(it)] --> Iterator[__iter__ returns self]
    Iterator --> NextCall[__next__ / next()]
    Push[push(item)] --> PushedList[self.pushed (LIFO)]
    NextCall -->|if pushed non-empty| PoppedItem[self.pushed.pop() -> returned]
    NextCall -->|else| UnderlyingNext[next(self.it) -> returned / StopIteration]
    PushedList --> NextCall

(Explanation: __next__ first checks the pushed list. If there are elements, it pops and returns the last pushed item. Otherwise it delegates to the underlying iterator's next(). __iter__ simply returns the instance. push(item) appends to the pushed list.)

## Raises:
- __init__:
  - TypeError: if the provided `it` argument is not iterable (iter(it) will raise TypeError).
  - No other explicit validation or exceptions are raised by __init__.

- __next__ / next:
  - StopIteration: when the pushed buffer is empty and the underlying iterator is exhausted (i.e., next(self.it) raises StopIteration). This is the standard iterator termination signal.

- push:
  - No exceptions are raised by push itself. If callers push objects that are not ints, no immediate error occurs in PushableIterator, but downstream consumers may expect ints.

## Example:
- Creation:
  - Create an iterator over a bytes source: instance = PushableIterator(b"ABC")
- Typical method sequence:
  1. Call next(instance) -> returns 65 (ord('A')).
  2. Suppose the consumer wants to unread that token: instance.push(65).
  3. next(instance) -> returns 65 again (the pushed value).
  4. Continue consuming; when pushed is empty, values come from the original bytes iterator.
- End of iteration:
  - Once both the pushed buffer is empty and the bytes iterator is exhausted, calling next(instance) raises StopIteration and iteration terminates.

### `imapclient.response_lexer.PushableIterator.__init__` · *method*

## Summary:
Initializes the iterator wrapper by storing an iterator over the provided bytes-like source and creating an empty LIFO push buffer on the instance.

## Description:
Known callers and context:
- Instantiated by lexical analyzers/parsers that consume a stream of byte-valued tokens and occasionally need to "un-read" tokens (small lookahead/unread facility). In this codebase it is typically created with a bytes object (e.g., PushableIterator(b"...")) by the response lexer or other tokenizing code before iteration begins.
- Lifecycle stage: called at object construction time to prepare the PushableIterator for subsequent iteration, pushing, and reading operations.

Why this is a separate method:
- Encapsulates the minimal initialization logic for the iterator wrapper (creating the underlying iterator and initializing the push buffer). Keeping this logic in __init__ centralizes the invariant setup (self.it is an iterator; self.pushed is a list) and avoids repeating initialization logic wherever a PushableIterator is created. It also makes the class safe to use immediately after construction without requiring additional setup calls.

## Args:
    it (bytes): The iterable source used to drive iteration. The signature uses bytes as the typical/expected type (iterating over bytes yields ints 0–255), but any iterable is accepted; elements should be integer token values for downstream consumers. There is no default value.

Allowed values / constraints:
- Must be an iterable (e.g., bytes, bytearray, or any object implementing __iter__).
- Elements are expected to be integers (commonly 0–255 when using bytes), but this is not enforced at runtime.

## Returns:
    None: The constructor returns None implicitly. After return, the instance is ready for iteration and push operations.

## Raises:
    TypeError: Raised if the provided `it` argument is not iterable; this comes directly from calling iter(it).
    (No other exceptions are raised by __init__ itself.)

## State Changes:
Attributes READ:
- None. __init__ does not read pre-existing instance attributes.

Attributes WRITTEN:
- self.it: set to iter(it), an iterator object obtained from the provided iterable.
- self.pushed: set to a new empty list (List[int]) that will be used as a LIFO buffer for pushed-back tokens.

## Constraints:
Preconditions:
- The caller must provide an iterable object as `it`. If `it` is not iterable, construction will fail with TypeError.
- If downstream code expects integer tokens, the iterable should produce integers; supplying a different element type will not be detected here and may break consumers later.

Postconditions:
- self.it is guaranteed to be an iterator (i.e., calling next(self.it) is valid until the underlying iterable is exhausted).
- self.pushed is guaranteed to be an empty list ready to accept pushed tokens.
- The instance is immediately usable as an iterator: __iter__ should return self and __next__ will draw from self.pushed (initially empty) then from self.it.

## Side Effects:
- No I/O, no network or filesystem access.
- No mutation of objects outside self (the initializer calls iter(it) but does not consume items from the underlying iterable at construction time).
- No other global state is mutated.

### `imapclient.response_lexer.PushableIterator.__iter__` · *method*

## Summary:
Returns the iterator object itself so the instance can be used as an iterable/iterator (e.g., in for-loops or any builtins that call iter()) without creating a new iterator or copying state.

## Description:
This implements the Python iterator protocol for PushableIterator by returning the object itself. Typical callers and contexts:
- The built-in iter(obj) call, which is implicitly invoked by a for-loop (for x in obj) at the start of iteration.
- Any standard library or user code that accepts an Iterable and calls iter() or consumes it (e.g., list(obj), tuple(obj), sum(obj), any(), all()).
- Places in the response-lexing pipeline where a PushableIterator instance is passed into consumer code that expects an Iterable[int] or Iterator[int].

This logic is implemented as its own method because Python's iterator protocol requires an __iter__ method that returns an Iterator. Returning self makes the object both the iterable and the iterator (common pattern for stateful iterators that maintain internal position/state), and keeps iteration logic centralized in __next__ rather than constructing a separate iterator wrapper.

## Args:
    None

## Returns:
    PushableIterator
    - Always returns self.
    - The returned object is the same instance (identity equality), and it will be used as the iterator that produces ints via __next__.

## Raises:
    None

## State Changes:
    Attributes READ:
        - None (the method does not access or read any self.<attr> fields)
    Attributes WRITTEN:
        - None (the method does not modify any attributes)

## Constraints:
    Preconditions:
        - The instance must be a properly-initialized PushableIterator (i.e., __init__ must have been called so self.it is an iterator and self.pushed is a list). __iter__ does not validate initialization.
    Postconditions:
        - No state or attributes are modified.
        - The caller receives the same object back and may immediately call __next__ (or let Python call it) to obtain iteration items.

## Side Effects:
    - None. The method performs no I/O, external calls, or mutations of objects outside self.

### `imapclient.response_lexer.PushableIterator.__next__` · *method*

## Summary:
Return the next integer token from the iterator, preferring any items previously pushed back; when returning a pushed value the push buffer is mutated.

## Description:
This implements the iterator protocol's next-step for PushableIterator. Callers obtain items by calling next(instance) or iterating (for/while) over the instance; typical callers are the response-lexer/tokenizer routines that consume a byte stream one value at a time and sometimes need to push a value back for reprocessing. The method centralizes the semantics of reading from the primary iterator versus reading from the push-back buffer so push/pop behavior is implemented in one place instead of duplicated across the lexer.

Why this is a separate method:
- It implements the standard iterator protocol and is the natural place to implement push-back handling.
- Keeping this logic here ensures consistent LIFO semantics for pushed values and correct interaction with the underlying iterator.

## Args:
    None (implicit self)

## Returns:
    int: The next integer from the sequence. This is either:
        - the last value previously pushed via push (LIFO), or
        - the next value yielded by the underlying iterator created from the original bytes input.
    The integers are expected to represent bytes (0..255) when the underlying iterator comes from a bytes object.

## Raises:
    StopIteration: Raised when the push buffer is empty and the underlying iterator is exhausted. The exception is raised by next(self.it) and is propagated unchanged.

## State Changes:
    Attributes READ:
        - self.pushed: checked for truthiness to decide whether to pop or read underlying iterator
        - self.it: advanced by one when no pushed value is available
    Attributes WRITTEN:
        - self.pushed: mutated by pop() when a pushed value is returned (the list shrinks by one)

## Constraints:
    Preconditions:
        - self.it must be a valid iterator (typically over integers) — constructed in __init__ as iter(it) where it is a bytes-like object.
        - self.pushed must be a list (as established in __init__) and may contain integers previously pushed by push().
    Postconditions:
        - If a pushed value is returned, it is the most-recently pushed item and that item is removed from self.pushed.
        - If no pushed value exists, the underlying iterator is advanced by exactly one element.
        - If neither a pushed value nor an iterator element exists, StopIteration is raised and nothing in self is modified further.

## Side Effects:
    - Mutates self.pushed when returning a pushed value.
    - No I/O or external service calls are performed.
    - The method may allow StopIteration to propagate to the caller; callers should handle this when iterating.

## Implementation notes and edge cases:
    - Pushed values are returned LIFO (last pushed, first returned) because pop() is used.
    - The method does not validate types of values in self.pushed; pushing non-integer values will cause __next__ to return those values as-is.
    - The underlying iterator (self.it) may yield values outside 0..255 if it was constructed from a non-bytes iterator; the caller is responsible for ensuring the iterator's element domain matches expectations.

### `imapclient.response_lexer.PushableIterator.push` · *method*

## Summary:
Append a single integer value to the iterator's internal push-back buffer so the value will be returned by subsequent iteration before any further values are consumed from the underlying iterator; this mutates the object's pushed buffer.

## Description:
This method implements the push-back (unread) operation for the PushableIterator, allowing callers that consume an underlying sequence of bytes to return a value back onto the iterator for immediate re-consumption. There are no callers declared in this snippet; semantically it is intended for lexer/parser code (for example, when peeking one byte ahead and needing to unread it). The operation is factored into its own method to centralize and encapsulate the buffer mutation (append) and to keep push/pop semantics local to the iterator implementation rather than duplicating list manipulation across parsing code.

## Args:
    item (int): Value to push onto the buffer. In the typical usage within this module this is a byte value produced by iterating over a bytes object (conventionally 0..255). The method accepts any Python object at runtime because list.append is used, but downstream code expects an int.

## Returns:
    None: No return value.

## Raises:
    AttributeError: If the instance was not properly constructed and does not have a self.pushed attribute, an AttributeError will be raised when attempting to call append. This indicates incorrect initialization of the object rather than normal usage.
    (No other exceptions are raised by this method itself; it does not raise StopIteration — StopIteration behavior is produced by __next__ when both the pushed buffer and the underlying iterator are exhausted.)

## State Changes:
    Attributes READ:
        self.pushed (the list reference is accessed in order to call append)
    Attributes WRITTEN:
        self.pushed (mutated in-place by appending the provided item)

## Constraints:
    Preconditions:
        - The PushableIterator must have been initialized (self.pushed exists and is a list).
        - Callers should pass an int representing a byte to match downstream expectations; passing other types is permitted syntactically but may cause consumer code to fail.
        - This method is not thread-safe; concurrent calls or concurrent iteration without external synchronization can lead to race conditions.
    Postconditions:
        - len(self.pushed) increases by 1.
        - The pushed item will be returned by the next call(s) to __next__ before any additional values are read from the underlying iterator.
        - Multiple pushes form a LIFO buffer: the most recently pushed item is returned first because __next__ pops items from the end of self.pushed.
        - Once all pushed items have been consumed, __next__ will resume reading from the underlying iterator and will raise StopIteration if that iterator is exhausted.

## Side Effects:
    - Mutates the in-memory list self.pushed on this PushableIterator instance.
    - No I/O, no network calls, and no mutation of objects outside this instance.

