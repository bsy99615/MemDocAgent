# `util.py`

## `imapclient.util.to_unicode` · *function*

## Summary:
Convert an input that may be raw bytes or an already-decoded string into a Unicode string using strict ASCII first, falling back to an ASCII decode that ignores invalid bytes while emitting a warning.

## Description:
This utility normalizes text values received from lower-level code (for example, IMAP server responses or protocol parsers) into Python str values. Callers typically pass raw byte payloads that are expected to be ASCII; the function attempts a strict ASCII decode and only strips problematic bytes if strict decoding fails.

Known callers within the repository were not provided with this task. Typical usage sites are response-parsing and header-decoding code paths where bytes read from network sockets or message streams must be worked with as Python strings.

This logic is extracted into a single function to centralize the ASCII-decoding policy and its fallback behavior (including the warning side effect). That prevents duplicated try/except+fallback logic across the codebase and ensures consistent handling of problematic byte sequences.

## Args:
    s (bytes | str)
        - bytes: raw byte sequence that should be interpreted as ASCII text
        - str: already-decoded Unicode string (returned unchanged)
        - Note: the signature declares bytes or str. If a caller passes a value of any other type, the function will return that value unchanged (no conversion is attempted).

## Returns:
    str
        - If a bytes object is passed and decoding in strict ASCII succeeds, returns the decoded str.
        - If a bytes object is passed and strict ASCII decoding raises UnicodeDecodeError, returns the result of decoding with errors="ignore" (a str where non-decodable bytes have been removed). In this fallback case a warning is emitted via the module logger.
        - If a str is passed, the same object (or an equal str) is returned unchanged.
        - If a non-bytes, non-str value is passed (contrary to the annotated signature), the original value is returned unchanged (this may violate callers' expectations — callers should ensure they pass bytes or str).

## Raises:
    - The function catches UnicodeDecodeError from the first ASCII decode and therefore never propagates UnicodeDecodeError.
    - Other exceptions are not explicitly raised by the function itself. If the module-level logger is misconfigured to raise on logging, logging calls could propagate exceptions (this is an external concern).

## Constraints:
    Preconditions:
        - Intended callers must pass either bytes or str. The type annotation reflects this expectation.
        - When passing bytes, the content is expected to be ASCII-compatible. Non-ASCII bytes will be silently dropped on fallback.
    Postconditions:
        - On normal code paths the function returns a str. In practice, if a non-str/bytes value is supplied it will be returned unchanged (so callers cannot strictly rely on return type unless they enforce input typing).

## Side Effects:
    - Emits a warning via the module-level logger (logger.warning) when strict ASCII decoding fails and the fallback "ignore" decode is used. The warning message includes the original input value.
    - No I/O, filesystem, network, or global-state mutation (aside from the logging call) occurs.

## Control Flow:
flowchart TD
    A[Start: call to_unicode(s)] --> B{isinstance(s, bytes)?}
    B -- No --> C[Return s (assumed str)]
    B -- Yes --> D[Try s.decode("ascii")]
    D -->|success| E[Return decoded str]
    D -->|UnicodeDecodeError| F[logger.warning(...)]
    F --> G[Return s.decode("ascii", "ignore")]

## Examples:
Example 1 — ASCII bytes
>>> to_unicode(b'Hello')
'Hello'

Example 2 — Non-ASCII bytes (fallback strips invalid bytes and logs a warning)
>>> to_unicode(b'Ol\xc3\xa1')  # bytes representing 'Olá' in UTF-8; not valid ASCII
# WARNING emitted via logger: "An error occurred while decoding b'Ol\xc3\xa1'... Fallback to 'ignore'..."
'Ol'  # non-ASCII bytes dropped by the 'ignore' fallback

Example 3 — Already a str (no-op)
>>> to_unicode('Hello')
'Hello'

Example 4 — Unexpected input type (returns value unchanged)
>>> to_unicode(123)  # not bytes or str
123  # returned as-is; callers should avoid passing other types

## `imapclient.util.to_bytes` · *function*

## Summary:
Normalize a str-or-bytes input to a bytes object by encoding strings with a specified charset; if the input is already bytes it is returned unchanged.

## Description:
A minimal utility that ensures callers obtain a bytes representation when they provide either text (str) or already-encoded bytes. It encapsulates the encoding decision in one place so callers need not duplicate str→bytes conversion logic.

Known callers within the provided source context:
- No call-sites were available in the provided code snippet for this task. Callers should be sought in other modules of the repository if needed.

Typical calling contexts (descriptive, not exhaustive):
- Preparing protocol messages, network frames, or binary I/O where the API requires bytes.
- Utility layers that accept either str or bytes and want to normalize inputs before downstream processing.

Why this is a standalone function:
- Centralizes encoding behavior and charset choice to avoid inconsistent encoding across code paths.
- Makes intent explicit (normalize to bytes) and reduces duplication and accidental double-encoding.

## Args:
    s (bytes | str):
        - If str: will be encoded using the `charset` parameter and a new bytes object is returned.
        - If bytes: returned unchanged (the same object, not a copy).
        - If any other type is passed: returned unchanged (this deviates from the annotated return type; callers should avoid passing other types).
    charset (str, optional): Default "ascii".
        - Encoding name passed to str.encode(). Accepts any encoding name recognized by Python (for example "utf-8", "latin-1", "ascii").

Interdependencies:
- Relies on Python's built-in str.encode behavior and codec lookup; no other internal dependencies.

## Returns:
bytes
    - If `s` is a str and encoding succeeds: a bytes object containing the encoded data.
    - If `s` is already bytes: the identical bytes object passed in (no copy).
    - If `s` is neither str nor bytes: the original value is returned unchanged (callers should not rely on this behavior; it's an implicit runtime outcome).

## Raises:
    UnicodeEncodeError:
        - Raised when `s` is a str and contains characters that cannot be represented in the specified `charset`. This comes directly from str.encode(charset) and is not caught here.
    LookupError:
        - Raised when the specified `charset` is not a known/registered codec name. This originates from the codec lookup performed by Python's encoding machinery (e.g., codecs.lookup) invoked by str.encode.
    (No other exceptions are explicitly raised by this function; it does not catch the above errors.)

## Constraints:
Preconditions:
    - Preferably pass only str or bytes to match the annotated types.
    - Provide a `charset` value supported by Python encodings if `s` is a str containing non-ASCII characters.

Postconditions:
    - On success when given a str: return value is bytes encoded with `charset`.
    - On success when given bytes: return is the same bytes object.
    - No global state modified.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or external resources.

## Control Flow:
flowchart TD
    A[Start: receive s, charset] --> B{isinstance(s, str)?}
    B -- Yes --> C[Attempt s.encode(charset)]
    C --> D{encoding success?}
    D -- Yes --> E[Return encoded bytes]
    D -- No --> F[Raise UnicodeEncodeError or LookupError]
    B -- No --> G[Return s unchanged]
    E --> H[End]
    F --> H
    G --> H

## Examples:
1) Encode a Unicode string to UTF-8 bytes (successful):
    s = "café"
    b = to_bytes(s, charset="utf-8")
    # b == b"caf\xc3\xa9"

2) Default ascii encoding — catch UnicodeEncodeError and fallback:
    try:
        b = to_bytes("é")  # default charset is "ascii"
    except UnicodeEncodeError:
        b = to_bytes("é", charset="utf-8")

3) Handle unknown charset name — catch LookupError:
    try:
        b = to_bytes("hello", charset="unknown-encoding")
    except LookupError:
        # handle invalid encoding name (e.g., log and fallback)
        b = to_bytes("hello", charset="utf-8")

4) Passing already-encoded bytes:
    s = b"OK"
    b = to_bytes(s)
    # b is s (identical object)

5) Unexpected non-str/bytes input (not recommended):
    s = 12345
    b = to_bytes(s)
    # b == 12345 (returned unchanged) — callers should validate input types to avoid this

Notes:
- Because the function returns non-bytes values unchanged if given unexpected types, callers that depend on a bytes result should validate inputs or perform an explicit check/cast prior to calling.
- Catch both UnicodeEncodeError and LookupError where appropriate when encoding user-supplied strings or charset names.

## `imapclient.util.assert_imap_protocol` · *function*

## Summary:
Raises a ProtocolError when a provided boolean condition is false, signalling that an IMAP server response violated the IMAP protocol; otherwise returns None.

## Description:
This helper centralizes the runtime assertion used when validating IMAP server replies. It is intended to be called at validation checkpoints after parsing or receiving server responses to ensure the response shape or content conforms to protocol expectations.

Known callers in the provided code context:
- No direct callers were available in the provided repository snapshot. Typical call sites (not listed in the local snapshot) are response-parsing code paths, command/response handlers, or any place that must assert server replies conform to the IMAP protocol before continuing.

Why this is a separate function:
- Encapsulates the assertion logic and the standardized error message construction in a single place so callers do not duplicate the error text/decoding behavior.
- Keeps higher-level code concise by providing a single, well-named guard that throws the standardized protocol-level exception when validations fail.

## Args:
    condition (bool): The boolean result of a validation check. If False, the function raises an exception.
    message (Optional[bytes]): Optional raw bytes from the server (e.g., the unmatched response or offending line). When provided, these bytes are decoded with ASCII and errors are ignored to be appended to the error message. Default is None.

Notes on parameter interdependency:
- The function only uses message when condition is False; supplying message when condition is True has no effect.

## Returns:
    None

Behavior summary:
- If condition is True: returns None (no side effects).
- If condition is False: never returns; instead raises exceptions.ProtocolError with a textual message (see Raises).

## Raises:
    exceptions.ProtocolError: Raised exactly when condition is False. The raised exception's message is constructed as:
        "Server replied with a response that violates the IMAP protocol"
    If message is provided, the function appends an additional substring produced by decoding message using ASCII with errors ignored. Note: the implementation appends the original base message twice when message is present due to the string formatting pattern used; the final msg when message is present will look like:
        "<base_msg><base_msg>: <decoded_message>"
    where <base_msg> is the initial static text. The code raises exceptions.ProtocolError(msg) from the local imapclient.exceptions module.

## Constraints:
Preconditions:
- condition should be a boolean. Passing non-boolean truthy/falsy values will behave according to Python truthiness rules (the function tests `if not condition`).
- message, if provided, must be bytes or a type compatible with .decode('ascii', errors='ignore'); passing other types may raise an AttributeError when .decode is called.

Postconditions:
- On success (condition True): no exception is raised and no state is mutated.
- On failure (condition False): an exceptions.ProtocolError is raised; the function never returns normally.

## Side Effects:
- None. The function performs no I/O, does not mutate global state, and does not call external services. It only constructs a string and raises an exception when appropriate.

## Control Flow:
flowchart TD
    Start --> CheckCondition
    CheckCondition{condition is True?}
    CheckCondition -->|Yes| ReturnNone[(return None)]
    CheckCondition -->|No| BuildBaseMsg[/"msg = base message"/]
    BuildBaseMsg --> HasMessage{message provided?}
    HasMessage -->|No| RaiseNoMessage[/"raise ProtocolError(msg)"/]
    HasMessage -->|Yes| Decode[/"decoded = message.decode('ascii', errors='ignore')"/]
    Decode --> AppendMsg[/"msg += \"{}: {}\".format(msg, decoded)"/]
    AppendMsg --> RaiseWithMessage[/"raise ProtocolError(msg)"/]

## Examples (usage described in prose):
- Typical successful path: A parser validates a server reply (e.g., checks that an IMAP STATUS response contains the expected tokens). If the check passes, call this function with condition True; it returns None and processing continues.
- Typical failure path and handling: After parsing a server line, a validation fails (condition False). Call this function with the offending raw bytes as message. The function decodes the bytes with ASCII (ignoring decode errors), appends them to the error message (note the duplicated base message behavior), and raises exceptions.ProtocolError. Higher-level code should catch exceptions.ProtocolError to log the violation, close the connection, or surface an error to callers.
- Defensive usage: Wrap calls in a try/except that catches exceptions.ProtocolError, logs the full exception message (which will include the decoded server bytes when provided), and performs cleanup or retry logic as appropriate.

## `imapclient.util.chunk` · *function*

## Summary:
Returns a generator that yields consecutive, non-overlapping contiguous slices of the provided sequence, each slice having length at most the specified size.

## Description:
- Known callers within the provided context:
    - No call sites were provided in the supplied observation; callers were not discovered from the available input.
- Typical usage context:
    - Employed when a sequence must be processed or transmitted in fixed-size batches (for example, breaking a long list of IDs into request-sized groups).
- Reason for extraction:
    - Encapsulates the common "split a sequence into chunks" pattern as a small, reusable generator to avoid repeating indexing and slicing logic and to make batch-processing intentions explicit.

## Args:
    lst (_TupleAtom):
        - A sequence-like object supporting len(lst) and slicing via lst[start:stop].
        - Typical concrete types: tuple, list, or any custom sequence implementing __len__ and __getitem__ that accepts slice objects.
        - No default; required.
    size (int):
        - Maximum length of each yielded chunk; used as the step/stride when advancing through lst.
        - Must be an integer (or an object acceptable to range() as a step, e.g., implementing the integer protocol).
        - No default; required.
        - Interdependencies:
            * Correct partitioning behavior requires size > 0.
            * size == 0 is invalid and will cause range() to raise when the generator is iterated.
            * size < 0 results in an iterator that yields no chunks (see Returns).

## Returns:
    Iterator[_TupleAtom]:
        - A generator object is returned immediately when the function is called.
        - When iterated, it yields successive slices lst[i : i + size] for i = 0, size, 2*size, ... until i >= len(lst).
        - For size > 0:
            * Each yielded slice has length between 1 and size (the final slice may be shorter).
            * The sequence of yielded slices, concatenated in order, reproduces the original sequence.
        - For size < 0:
            * The generator is returned; iterating it will produce no yields because the computed range is empty.
        - For size == 0:
            * The generator is returned, but attempting to iterate it will raise ValueError when range(0, len(lst), size) is evaluated (step must not be zero).

## Raises:
    ValueError:
        - Raised when size == 0. This occurs at the time the generator is first iterated (not at function call time) because range() is invoked with a step of zero and raises ValueError.
    TypeError:
        - May be raised when the generator is iterated if:
            * lst does not support len() or slicing (for example, lst is None), or
            * size is not an integer-like value acceptable to range().
        - Note: slicing an indexable sequence normally does not raise IndexError for out-of-range indices; it returns a shorter slice. However, user-defined sequence types may raise other exceptions from their __len__ or __getitem__ implementations; such exceptions will propagate.

## Constraints:
- Preconditions:
    - lst must be a sliceable, indexable sequence (supporting len() and __getitem__ with slice objects) for meaningful behavior.
    - size should be a positive integer for typical chunking semantics.
- Postconditions:
    - The original lst is not modified.
    - If size > 0, iterating the returned generator yields a sequence of contiguous slices that partition lst.
    - No hidden global state is changed by this function.

## Side Effects:
- None: the function performs pure in-memory operations (len and slicing). It does not perform I/O, mutate external state, or call external services.
- Any exceptions raised are those from built-in operations (range, len, slicing) or from user-defined sequence implementations.

## Control Flow:
flowchart TD
    Call([Call chunk(lst, size)])
    ReturnGen([Returns generator object])
    Iterate{First iteration (next(gen))?}
    EvalRange[Evaluate range(0, len(lst), size)]
    SizeZero{size == 0?}
    SizeNeg{size < 0?}
    RangeEmpty[range yields no indices -> end iteration]
    Loop[for i in range(...):]
    Yield[yield lst[i : i + size]]
    End([Iteration complete])

    Call --> ReturnGen
    ReturnGen --> Iterate
    Iterate --> EvalRange
    EvalRange --> SizeZero
    SizeZero -- Yes --> RaiseValueError[ValueError raised by range(step=0)]
    SizeZero -- No --> SizeNeg
    SizeNeg -- Yes --> RangeEmpty
    SizeNeg -- No --> Loop
    Loop --> Yield
    Yield --> Loop
    Loop --> End
    RangeEmpty --> End

## Examples:
- Normal usage (size > 0):
    - Given lst = (1, 2, 3, 4, 5, 6, 7) and size = 3:
      - Calling the function returns a generator; iterating it yields (1,2,3), (4,5,6), (7,)
      - Concatenating the yielded chunks in order reconstructs the original sequence.

- size < 0:
    - Given lst = [1,2,3] and size = -1:
      - Calling the function returns a generator; iterating it yields nothing (empty iterator).

- size == 0 (error occurs on iteration):
    - Given lst = [1,2,3] and size = 0:
      - Calling the function returns a generator object.
      - Attempting to iterate (for example, calling next() on the generator) raises ValueError due to range() being called with step == 0.

- Incompatible lst:
    - Given lst = None and size = 2:
      - Calling the function returns a generator object.
      - Attempting to iterate raises TypeError when len(None) or slicing is attempted.

