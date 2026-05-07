# `imap_utf7.py`

## `imapclient.imap_utf7.encode` · *function*

## Summary:
Encodes a Python string to the IMAP "modified UTF-7" bytes used for mailbox names; ASCII printable characters are passed through (with special handling for '&'), and runs of non-ASCII characters are emitted as IMAP-modified Base64 shifted blocks.

## Description:
This function converts its input into the IMAP modified UTF-7 representation:
- If the input is a str, the function iterates characters and:
  - emits ASCII-printable characters (U+0020 to U+007E) directly as single-byte ASCII,
  - encodes runs of non-ASCII characters as shifted blocks delimited by b'&' and b'-' where the contents are produced by base64_utf7_encode (which UTF-16BE-encodes the run and applies the IMAP modified base64 transformations).
  - the literal '&' (U+0026) is encoded as the two-byte sequence b"&-" (an empty shifted block) to avoid ambiguity with the shift marker.
- If the input is not an instance of str, it is returned unchanged immediately.

Known callers in this repository:
- No direct callers were discovered in the provided source listing.
Typical usage/context:
- This function is intended for encoding mailbox/folder names before sending them to an IMAP server or storing them in IMAP protocol exchanges. Higher-level utilities that prepare IMAP commands or present mailbox names will call it.

Why this is extracted:
- The function separates streaming/buffering/shift-delimiter logic (this function) from the exact byte-level base64+UTF-16BE transformation (base64_utf7_encode). This keeps responsibility clear: encode handles when to shift and how to assemble bytes; base64_utf7_encode handles the precise modified base64 encoding of buffered runs.

## Args:
    s (Union[str, bytes]):
        - The value to encode.
        - If s is a str: it will be converted to modified UTF-7 bytes and returned.
        - If s is not a str (for example bytes or bytearray), the function returns s unchanged.
        - Note: the type annotation indicates bytes is an accepted input type, but any non-str input is returned as-is (no conversion).

## Returns:
    bytes or original input:
        - If s is a str: returns a bytes object containing the modified UTF-7 encoding suitable for IMAP (ASCII-only bytes; ASCII characters preserved, non-ASCII runs encoded between b'&' and b'-', '&' encoded as b"&-").
        - If s is not a str: returns s unchanged (so the runtime return type may be bytes, bytearray, or whatever type was passed in).
        - Examples of possible return values:
            * encode("") -> b""
            * encode("ABC") -> b"ABC"
            * encode("&") -> b"&-"
            * encode(b"ABC") -> b"ABC" (returned unchanged)
            * encode("AäB") -> b'A' + b'&' + modified-base64-bytes + b'-' + b'B'

## Raises:
    - Indirect exceptions propagated from base64_utf7_encode when a buffered run is flushed:
        * TypeError: if base64_utf7_encode receives a buffer containing non-str elements (should not occur for well-formed str input because each appended element is a single-character str).
        * UnicodeEncodeError: if encoding the buffered characters to 'utf-16be' fails (very unlikely for standard Python str).
    - No explicit exceptions are raised by this function itself for normal str inputs.

## Constraints:
Preconditions:
    - If you expect the function to return a bytes object, pass s as a Python str. Passing other object types will short-circuit and return the original object.
    - The runtime must support the 'utf-16be' codec (present in standard Python).

Postconditions:
    - For str input: returned value is an ASCII-only bytes object conforming to IMAP modified UTF-7 byte layout (printable-ascii preserved, non-ASCII runs encoded as &...- blocks).
    - The function does not mutate the input string.

## Side Effects:
    - None. The function performs only in-memory computation; it does not perform I/O nor mutate global state.

## Control Flow:
flowchart TD
    Start([Start]) --> IsStr{Is s an instance of str?}
    IsStr -- No --> ReturnInput[Return s unchanged]
    IsStr -- Yes --> Init[Initialize res bytearray and empty b64_buffer]
    Init --> ForLoop[For each character c in s]
    ForLoop --> Ord[Compute o = ord(c)]
    Ord --> IsAsciiPrintable{0x20 <= o <= 0x7E?}
    IsAsciiPrintable -- Yes --> Consume[Call consume_b64_buffer on b64_buffer]
    Consume --> IsAmp{Is o == 0x26 ('&')?}
    IsAmp -- Yes --> AppendAmp[res.extend(b"&-")] --> LoopNext
    IsAmp -- No --> AppendAscii[res.append(o)] --> LoopNext
    IsAsciiPrintable -- No --> BufferChar[b64_buffer.append(c)] --> LoopNext
    LoopNext --> ForLoop
    ForLoop --> AfterLoop[After loop, call consume_b64_buffer]
    AfterLoop --> ReturnBytes[Return bytes(res)]
    ReturnBytes --> End([End])

## Examples:
1) ASCII-only input
    - Input: "INBOX"
    - Behavior: each character is emitted as ASCII byte.
    - Result: b"INBOX"

2) Literal ampersand
    - Input: "A&B"
    - Behavior: 'A' -> b'A'; '&' -> b"&-"; 'B' -> b'B'
    - Result: b"A&-B"

3) Mixed ASCII and non-ASCII (conceptual)
    - Input: "FooäöBar"
    - Behavior: "Foo" emitted as ASCII bytes, "äö" buffered then flushed as b'&' + base64_utf7_encode(["ä","ö"]) + b'-', then "Bar" emitted.
    - Result: b"Foo" + b'&' + (modified-base64-bytes for "äö") + b'-' + b"Bar"
    - Note: the exact bytes for the shifted block are produced by base64_utf7_encode and depend on the UTF-16BE -> base64 transformation (with '/' replaced by ',' and '=' padding stripped).

4) Non-str passed through
    - Input: b"raw-bytes"
    - Behavior: function returns the input unchanged.
    - Result: b"raw-bytes"

Error handling example:
    - If an unexpected exception arises while flushing a buffered run (e.g., UnicodeEncodeError from base64_utf7_encode), callers should catch and handle it:
    try:
        out = encode(some_name)
    except UnicodeEncodeError:
        # handle or log encoding failure for this mailbox name
        raise

## `imapclient.imap_utf7.decode` · *function*

## Summary:
Convert an IMAP "modified UTF-7" encoded byte sequence into a Python Unicode string; if a non-bytes object (commonly a str) is supplied, return it unchanged.

## Description:
This function decodes mailbox/name tokens encoded in IMAP's "modified UTF-7" (the variant used by IMAP for mailbox names) when given a bytes object. It scans the input bytes for framing markers (an ampersand region beginning with '&' and terminated by '-') and delegates the decoding of the region payload to base64_utf7_decode. The two-character escape "&-" decodes to a literal '&'. If the input is already a Python str (or any non-bytes object), the function returns it unchanged.

Known callers and typical usage:
- No direct callers were supplied in the provided snippet. In typical IMAP client code, this function is invoked when converting mailbox names returned by the IMAP server (which are encoded in modified UTF-7) into Python-native strings for display, storage, or further processing.

Why this is a distinct function:
- Responsibility separation: it handles framing and marker logic (detection of '&...-' regions and the special "&-" escape) while delegating the actual modified base64 → Unicode conversion to base64_utf7_decode. This keeps concerns separated and makes modified-base64 decoding reusable and testable independently.

## Args:
    s (bytes | str): The input to decode.
        - If s is bytes: it is interpreted as an IMAP modified UTF-7 encoded stream and will be decoded to produce the returned str.
        - If s is not bytes (commonly a str): the value is returned unchanged. Callers should therefore normally pass either bytes (for decoding) or str (already decoded).
        - The implementation performs a single isinstance check for bytes; any non-bytes object will be returned as-is.

## Returns:
    str: The decoded Unicode string.
        - For str (or other non-bytes) input: the same object/value is returned unchanged.
        - For bytes input: returns the concatenation of decoded segments:
            * Bytes outside any '&...-' region are converted byte-by-byte into Unicode characters via chr(byte).
            * The two-byte sequence "&-" (ampersand followed immediately by dash) is converted to the literal "&".
            * Any framed region beginning with '&' and ending with '-' and containing one or more payload bytes is decoded by calling base64_utf7_decode(payload_bytes) where payload_bytes excludes the leading '&' and trailing '-'. The resulting str is inserted into the output.
            * If the input ends while a framing buffer is open (i.e., a trailing '&' region without a terminating '-'), the remaining payload (which may be empty) is passed to base64_utf7_decode(b'...') and the returned string is appended. In particular, a trailing single '&' results in base64_utf7_decode being called with an empty payload (b'').

## Raises:
    - The function itself does not explicitly raise exceptions. Any exception raised by base64_utf7_decode (or any other called code) will propagate to the caller. Callers should be prepared to handle decoding errors originating from the helper.

## Constraints:
    Preconditions:
        - AMPERSAND_ORD and DASH_ORD must be integer constants representing the byte ordinals for the '&' and '-' marker bytes respectively; the function compares iterated byte values to these constants.
        - base64_utf7_decode(payload: bytes) must accept a bytes-like payload and return a str. Its behavior for an empty payload determines the outcome for a trailing '&' with no terminating '-'.
    Postconditions:
        - The return value is always a Python str.
        - No global state is modified by this function.

## Side Effects:
    - None within this function's code: there is no I/O, no network access, and no mutation of global state.
    - Any side effects would be due to the behavior of base64_utf7_decode if that helper performs side effects (not expected for a pure decoder).

## Control Flow:
flowchart TD
    Start[Start: call decode(s)] --> IsBytes{isinstance(s, bytes)?}
    IsBytes -- No --> ReturnStr[Return s unchanged (non-bytes input)]
    IsBytes -- Yes --> Init[res = [] ; b64_buffer = bytearray()]
    Init --> Loop[for each byte c in s]
    Loop --> CheckAmp{c == AMPERSAND_ORD and b64_buffer empty?}
    CheckAmp -- True --> AppendAmpToBuf[b64_buffer.append(c)]
    CheckAmp -- False --> CheckDash{b64_buffer non-empty and c == DASH_ORD?}
    CheckDash -- True --> ShortBuf{len(b64_buffer) == 1?}
    ShortBuf -- True --> AppendLiteralAmp[res.append("&") ; b64_buffer = bytearray()]
    ShortBuf -- False --> DecodeBuf[res.append(base64_utf7_decode(b64_buffer[1:])) ; b64_buffer = bytearray()]
    CheckDash -- False --> BufOpen{b64_buffer non-empty?}
    BufOpen -- True --> AppendToBuf[b64_buffer.append(c)]
    BufOpen -- False --> AppendAscii[res.append(chr(c))]
    Loop --> AfterLoop[after loop]
    AfterLoop --> TrailingBuf{b64_buffer non-empty?}
    TrailingBuf -- True --> DecodeTrailing[res.append(base64_utf7_decode(b64_buffer[1:]))]
    TrailingBuf -- False --> NoTrailing[no-op]
    DecodeTrailing --> Join[return "".join(res)]
    NoTrailing --> Join

## Examples:
Example — pass-through for str input:
    s = "INBOX"
    result = decode(s)
    # result == "INBOX"  (returned unchanged)

Example — ASCII bytes without framing:
    s = b"INBOX"
    result = decode(s)
    # result == "INBOX"

Example — literal ampersand escape:
    s = b"Foo &- Bar"
    result = decode(s)
    # result == "Foo & Bar"
    # Explanation: "&-" is recognized and converted to "&" (no base64 decoding).

Example — trailing '&' without terminating '-':
    s = b"Foo &"
    result = decode(s)
    # Behavior: the trailing '&' opens a buffer; after the loop the code calls
    # base64_utf7_decode(b'') and appends its result. The final returned value
    # therefore depends on how base64_utf7_decode handles an empty payload.
    # Callers should be aware that an unterminated '&' will trigger that call.

Example — framed payload (high level):
    s = b"Foo &<payload>- Baz"
    try:
        result = decode(s)
    except Exception:
        # Any decoding exception raised by base64_utf7_decode will propagate.
        raise

    # If base64_utf7_decode(<payload>) returns the Unicode string U,
    # result == "Foo " + U + " Baz"

## `imapclient.imap_utf7.base64_utf7_encode` · *function*

## Summary:
Encodes a list of Unicode string fragments into the IMAP "modified Base64" bytes used inside shifted UTF-7 segments.

## Description:
Concatenates the provided List[str], encodes the combined string using UTF-16 big-endian, converts that byte sequence to Base64 using binascii.b2a_base64, then adapts the output for IMAP's modified UTF-7 by:
- removing the trailing newline and any '=' padding characters produced by the base64 routine, and
- replacing '/' with ',' to match the IMAP-modified base64 alphabet.

Known callers:
- No direct callers were discovered in the provided source listing. In typical IMAP UTF-7 encoders, this function is called when the encoder has buffered a contiguous run of non-ASCII characters and needs the bytes for a single shifted block.

Why extracted:
- The function centralizes the exact encoding steps and the IMAP-specific base64 adjustments, keeping higher-level encoder code focused on buffering and shift-delimiter handling.

## Args:
    buffer (List[str]):
        - The function is annotated to accept a List[str] containing the Unicode fragments to encode together.
        - Each element is expected to be a str. If any element is not a str, a TypeError will be raised by the join operation.
        - The list may be empty (see Returns).

## Returns:
    bytes:
        - The IMAP-modified Base64 bytes representing the UTF-16BE encoding of the concatenated input strings.
        - The returned bytes:
            * contain only ASCII characters from the base64 alphabet with ',' substituted for '/' and '+' preserved,
            * do not include '=' padding characters (they are stripped),
            * do not include a trailing newline (it is removed).
        - For an empty input list (buffer == []), the function returns an empty bytes object (b'').

## Raises:
    TypeError:
        - If any element of buffer is not a str, the "".join(buffer) call will raise TypeError.
    UnicodeEncodeError:
        - If encoding the concatenated string to 'utf-16be' fails, .encode('utf-16be') will raise UnicodeEncodeError.

## Constraints:
Preconditions:
    - Callers should provide a List[str] (per the function signature). Passing other iterable types of str elements will typically work because str.join accepts any iterable of str, but the signature and documented contract specify List[str].
    - The Python runtime must include the 'utf-16be' codec (standard in CPython).

Postconditions:
    - The returned value is an ASCII-only bytes object formatted per IMAP modified Base64 rules (no '=' padding, no trailing newline, '/' replaced with ',').
    - No input objects are mutated and no global state is changed.

## Side Effects:
    - None. The function performs pure computation and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    Start([Start]) --> Join[Concatenate buffer with "".join(buffer)]
    Join --> Encode[Encode concatenated string with 'utf-16be' -> bytes]
    Encode --> Base64[binascii.b2a_base64(bytes) -> base64-with-newline-and-padding]
    Base64 --> Strip[Strip trailing b"\n" and b"=" via rstrip(b"\n=")]
    Strip --> Replace[Replace b"/" with b"," via replace(b"/", b",")]
    Replace --> Return([Return resulting bytes])
    Return --> End([End])

## Examples (behavioral, descriptive):
1) Typical non-ASCII run:
    - Input: buffer contains contiguous non-ASCII fragments that were buffered by an IMAP UTF-7 encoder.
    - Behavior: fragments are joined, encoded to UTF-16BE, base64-encoded, newline and padding removed, and '/' replaced with ','.
    - Output: a bytes object suitable for insertion into the encoder's shifted block (the encoder is responsible for surrounding '+' and '-' delimiters).

2) Empty input:
    - Input: buffer = []
    - Output: b''

3) Invalid element type:
    - Input: buffer contains a non-str element (e.g., ['a', 123])
    - Result: TypeError raised by the join operation; callers should validate or coerce elements to str if such inputs are possible.

Notes:
    - The function returns bytes. If callers need a textual form, they can decode the result with ASCII since the output is ASCII-only.
    - This function implements only the modified-base64 transformation for a buffered run; higher-level code must handle adding shift delimiters and assembling the full mailbox-encoded name.

## `imapclient.imap_utf7.base64_utf7_decode` · *function*

*No documentation generated.*

