# `response_parser.py`

## `imapclient.response_parser.parse_response` · *function*

## Summary:
Return an eagerly-evaluated tuple of parsed IMAP atoms for the given raw response fragments, treating the special sentinel [None] as an empty response.

## Description:
This small adapter converts a sequence of raw IMAP response fragments (a List of bytes) into a concrete tuple of parsed atom values by delegating parsing to the streaming parser generator.

Known callers and typical context:
- Higher-level IMAP response handling code that receives raw bytes lines from the network, assembles them into a List[bytes], and needs a concrete, fully-parsed tuple of atom values for immediate inspection, dispatch, or return from a public API.
- Callers typically run in a response-dispatch or fetch/command-result path where the entire parsed result is required at once rather than incrementally.

Why this logic is factored into its own function:
- Encapsulates the sentinel handling ([None] → empty tuple) and the conversion from a streaming generator (gen_parsed_response) into an eagerly-realized tuple in one place.
- Keeps callers simpler: they do not need to remember the [None] sentinel or to explicitly convert the generator to a tuple.
- Centralizes exception propagation semantics (exceptions from the generator propagate unchanged).

## Args:
    data (List[bytes]):
        - A list of bytes fragments representing one or more IMAP responses or chunks.
        - Special sentinel: if data is exactly [None] (a single-element list whose only element is None), the function returns an empty tuple without invoking the parser.
        - Typical values: e.g. [b'* 1 FETCH (FLAGS (\\Seen)) ...'], [], or [None].
        - Passing elements that are not bytes (other than the allowed sentinel [None]) may cause the lexer/parser (gen_parsed_response) to raise TypeError/ValueError/ProtocolError.

## Returns:
    Tuple[_Atom, ...]:
        - A tuple containing the parsed atom values produced by consuming the generator gen_parsed_response(data).
        - If data == [None], returns an empty tuple ().
        - If data is empty (e.g., []), the parser generator yields nothing and an empty tuple is returned.
        - The returned tuple is an eagerly-realized collection (the entire response is parsed and held in memory).

## Raises:
    ProtocolError:
        - Propagated unchanged if raised by the underlying parser/generator.
        - gen_parsed_response normalizes some ValueError cases into ProtocolError with token annotation; such ProtocolErrors will be raised here unchanged.
    Any exception raised by gen_parsed_response (or by its callees, e.g., TokenSource construction): those exceptions propagate unchanged (e.g., TypeError, ValueError, RuntimeError).

## Constraints:
Preconditions:
    - data must be a sequence (typically list or tuple) whose elements are bytes, except for the special-case [None].
    - TokenSource and the atom parsing routines (used by gen_parsed_response) must accept the supplied data shape.
Postconditions:
    - On success, the returned tuple contains one parsed _Atom for each token the underlying TokenSource/atom parser produced.
    - No tokens remain unconsumed from the generator when the function returns normally.

## Side Effects:
    - Instantiates and drives the parser generator (via gen_parsed_response), which in turn constructs a TokenSource and calls parsing routines. Any side effects those components have (memory allocation, temporary buffers) occur.
    - No I/O, global state mutation, or network activity is performed by this function itself; side effects are limited to what the parser/generator may do.

## Control Flow:
flowchart TD
    Start([call parse_response(data)]) --> IsSentinel{data == [None]?}
    IsSentinel -- Yes --> ReturnEmpty([return ()])
    IsSentinel -- No --> CallGen[call gen_parsed_response(data)]
    CallGen --> Consume[consume generator and build tuple from yields]
    Consume --> ReturnTuple([return tuple_of_parsed_atoms])
    CallGen -->|raises ProtocolError| PropagateProto([ProtocolError propagates])
    CallGen -->|raises other Exception| PropagateOther([Exception propagates unchanged])

## Examples:
- Normal usage (conceptual):
    - Assemble raw response fragments into a list, then obtain a fully-parsed tuple:
      data = [b'* 1 FETCH (BODY[] {12}\r\nHello World!\r\n)'] 
      parsed = parse_response(data)  # parsed is a tuple of parsed atom values

- Handling the sentinel (no response):
    - Some higher-level code supplies [None] to mean "no response":
      parsed = parse_response([None])  # returns ()

- Error handling:
    - Because parsing exceptions propagate, callers should catch ProtocolError when dealing with possibly-malformed server responses:
      try:
          parsed = parse_response(data)
      except ProtocolError as e:
          # handle protocol-level parse error; e may include offending token info
          raise

Implementation notes for reimplementers:
    - Implement exactly the sentinel check (data == [None]) returning an empty tuple.
    - Otherwise call the streaming parser generator and convert its yields to a tuple (fully realize the generator).
    - Do not try to swallow or alter exceptions from the generator; let ProtocolError and other exceptions propagate unchanged.

## `imapclient.response_parser.parse_message_list` · *function*

## Summary:
Convert a single IMAP message-list fragment (one bytes/str element) into a SearchIds object containing parsed numeric message IDs, appending any extra integers returned by the trailing-atom parser and capturing a MODSEQ value if present.

## Description:
This function parses the payload of an IMAP SEARCH/ESEARCH-style fragment supplied as a single-element list. It performs three steps: validate the single-element input, decode bytes to ASCII if needed, and use a module-level regular expression to extract the leading space-separated message-id sequence (group 1). It constructs a SearchIds from those ids. If any characters remain after the matched id-sequence, the function re-encodes that trailing text to ASCII bytes and calls parse_response to interpret trailing atoms; integers returned by that parser are appended to the SearchIds, and a two-element tuple whose first element (case-insensitive) equals b"modseq" sets ids.modseq to the second element.

Why this logic is factored out:
- Keeps message-id extraction, validation, and post-id atom handling centralized, so higher-level response handlers can work with a typed SearchIds result instead of raw text and parser call sites.

## Args:
    data (List[Union[bytes, str]]):
        - Must be a list with exactly one element; otherwise the function raises ValueError("unexpected message list data").
        - The single element may be:
            * bytes: will be decoded using ASCII (message_data.decode("ascii")). Non-ASCII bytes will raise UnicodeDecodeError at decode time.
            * str: used directly.
        - Typical valid examples:
            * [b'1 2 3']
            * ['1 2 3 (MODSEQ 42)']
            * [b''] (an empty fragment produces an empty SearchIds)
        - Interdependencies:
            * If trailing text exists after the matched id-list, it will be encoded with extra.encode("ascii") before passing to parse_response; encoding may raise UnicodeEncodeError for non-ASCII characters.

## Returns:
    SearchIds
        - A SearchIds instance (subclass of list[int]) initialized with the integers parsed from the leading matched group (m.group(1)). Integers are produced by int(n) for each whitespace-separated token from the capture.
        - After initial construction:
            * If parse_response yields integers, each integer is appended to the SearchIds (in the order produced by parse_response).
            * If parse_response yields a two-element tuple whose first element (lowercased) equals b"modseq", the second element is assigned to ids.modseq. The code includes a TYPE_CHECKING-only assertion that the second element is int; this assertion does not run at runtime, so non-int values would be assigned as-is.
            * Other items returned by parse_response (tuples of different shapes, non-integers) are ignored.
        - Edge returns:
            * For falsy message_data (e.g., b'' or ''), the function returns an empty SearchIds() with modseq == None.

## Raises:
    ValueError:
        - "unexpected message list data" when len(data) != 1.
        - "unexpected message list format" when the module-level regex (_msg_id_pattern) does not match the start of the (decoded) fragment.
    UnicodeDecodeError:
        - If the single-element was bytes containing non-ASCII bytes and .decode("ascii") fails.
    UnicodeEncodeError:
        - If trailing text is non-ASCII and extra.encode("ascii") is called.
    Any exception raised by parse_response:
        - parse_response may raise ProtocolError, ValueError, TypeError, or other exceptions; these propagate unchanged to the caller.

## Constraints:
Preconditions:
    - Caller must pass a list of length exactly one.
    - If passing bytes, they must be ASCII-encodable for decode to succeed.
    - The leading portion of the fragment must conform to the module's _msg_id_pattern (matched at the start); otherwise a ValueError is raised.
Postconditions:
    - Returned SearchIds contains integer elements for each parsed id (initial capture and any appended ints from parse_response) and may have modseq set to the value returned by parse_response for a MODSEQ atom.
    - No modification of global state or external I/O occurs within this function.

## Side Effects:
    - Calls parse_response on trailing ASCII-encoded bytes when extra characters follow the initially matched id-list; any side effects or exceptions from parse_response propagate.
    - Decoding and encoding operations may raise Unicode-related exceptions as noted above.

## Control Flow:
flowchart TD
    Start([parse_message_list(data)]) --> LenCheck{len(data)==1?}
    LenCheck -- No --> RaiseLenError[raise ValueError("unexpected message list data")]
    LenCheck -- Yes --> GetElem[message_data = data[0]]
    GetElem --> FalsyCheck{not message_data?}
    FalsyCheck -- Yes --> ReturnEmpty([return SearchIds()])
    FalsyCheck -- No --> BytesCheck{isinstance(message_data, bytes)?}
    BytesCheck -- Yes --> Decode[message_data = message_data.decode("ascii")]
    BytesCheck -- No --> NoDecode
    Decode --> RegexMatch[m = _msg_id_pattern.match(message_data)]
    NoDecode --> RegexMatch
    RegexMatch --> MatchCheck{m is not None?}
    MatchCheck -- No --> RaiseFormat[raise ValueError("unexpected message list format")]
    MatchCheck -- Yes --> BuildIds[ids = SearchIds(int(n) for n in m.group(1).split())]
    BuildIds --> SliceExtra[extra = message_data[m.end(1):]]
    SliceExtra --> ExtraCheck{extra non-empty?}
    ExtraCheck -- No --> ReturnIds([return ids])
    ExtraCheck -- Yes --> EncodeExtra[for item in parse_response([extra.encode("ascii")]):]
    EncodeExtra --> ItemIsModseq{is tuple of len 2 and item[0].lower()==b"modseq"?}
    ItemIsModseq -- Yes --> SetModseq[ids.modseq = item[1]]
    ItemIsModseq -- No --> ItemIsInt{isinstance(item,int)?}
    ItemIsInt -- Yes --> AppendInt[ids.append(item)]
    ItemIsInt -- No --> IgnoreItem[ignore]
    AppendInt --> ContinueLoop --> ReturnIds
    SetModseq --> ContinueLoop --> ReturnIds
    IgnoreItem --> ContinueLoop --> ReturnIds

## Examples:
- Successful parse, bytes input:
    - Input: [b'10 20 30']
    - Result: SearchIds([10, 20, 30]) with modseq == None

- Empty fragment:
    - Input: [b'']
    - Result: SearchIds([]) with modseq == None

- Trailing MODSEQ and appended ints:
    - Suppose parse_response on b' (MODSEQ 100) 40' yields [(b'MODSEQ', 100), 40]
      Input: [b'1 2 3 (MODSEQ 100) 40']
      Result: SearchIds([1,2,3,40]) with modseq == 100

- Error cases to handle:
    - Input: [] -> raises ValueError("unexpected message list data")
    - Input: [b'\xff'] -> decode step raises UnicodeDecodeError
    - Input: [b'abc'] -> module regex does not match -> raises ValueError("unexpected message list format")
    - If trailing text has non-ASCII characters, extra.encode("ascii") raises UnicodeEncodeError before parse_response is called.

Implementation notes for reimplementers:
    - Enforce the single-element input check and raise the exact ValueError messages used above.
    - Decode bytes with ASCII; do not perform alternative encodings.
    - Use the module-level regex _msg_id_pattern to match starting ids and use group(1).split() to obtain tokens converted to int().
    - Re-encode trailing text with ASCII and call parse_response([trailing_bytes]) — inspect each yielded item:
        * If item is a two-element tuple and its first element lowercased equals b"modseq", assign ids.modseq = item[1].
        * If item is an int, append it to ids.
        * Otherwise ignore the item.
    - Do not rely on TYPE_CHECKING assertions at runtime; they do not enforce types during normal execution.

## `imapclient.response_parser.gen_parsed_response` · *function*

## Summary:
Return a generator that tokenizes raw IMAP response bytes and yields parsed atom values; iteration produces zero or more parsed _Atom items and normalizes token-parsing ValueError into ProtocolError with the offending token annotated.

## Description:
This function orchestrates streaming parsing of IMAP server responses. It accepts a list of raw response fragments (List[bytes]), constructs a TokenSource for lexing, then iterates the token stream and delegates each token to the atom parser. Responsibilities:
- Create the token stream (TokenSource).
- Iterate the token stream and call atom(src, token) for each token.
- Yield each parsed result from atom.
- Convert ValueError raised during iteration/parsing into ProtocolError that includes the original ValueError message and the token that caused it.
- Re-raise ProtocolError unchanged.

Why this logic is a separate function:
- Centralizes iteration and error-normalization so callers receive a consistent, streaming parsed output and consistent error semantics without duplicating token-looping logic.

Known callers and typical context:
- Higher-level IMAP response processing code that needs a stream of parsed atoms (for example: a response dispatcher or an envelope/body parser). Callers typically obtain network-received bytes lines, assemble them into a List[bytes], then call this function and iterate the returned generator to consume parsed atoms as they arrive.

## Args:
    text (List[bytes]):
        - A list (or other sequence) of bytes fragments representing one or more IMAP responses or chunks.
        - Allowed values: any sequence whose elements are bytes objects.
        - If text is empty or otherwise falsy, iteration over the returned generator will immediately finish (no yields).

## Returns:
    Iterator[_Atom]:
        - A generator object that, when iterated, yields parsed atom values (type alias _Atom).
        - Important detail: because this function contains yield expressions, calling it always returns a generator object immediately; the body is executed only when the generator is iterated.
        - If the provided text is empty, the generator will immediately raise StopIteration on the first next() call (i.e., yields nothing).
        - For non-empty input, each token yielded by TokenSource(text) is passed to atom(src, token) and the atom(...) return value is yielded to the caller.

## Raises:
    ProtocolError:
        - Re-raised unchanged when a ProtocolError is raised by TokenSource, atom(...), or other called routines during iteration.
        - Raised when a ValueError is raised during the for-loop or inside atom(...): that ValueError is caught and converted into a ProtocolError whose message is "%s: %r" % (str(err), token), where err is the original ValueError and token is the token in scope at the time of error (see below for token semantics).
    Any other exception:
        - Exceptions other than ProtocolError and ValueError (e.g., TypeError, RuntimeError) that occur during TokenSource construction, iteration, or inside atom(...) will propagate unchanged to the caller.

Notes on token used in error message:
    - The function sets token = None before entering the try/for loop. Therefore, if a ValueError is raised before any token is produced (for example, in TokenSource.__iter__ or during the first atom call), the token used in the generated ProtocolError message will be None. If the error occurs while processing a token, the token's repr() will be included.

## Constraints:
Preconditions:
    - text must be a sequence of bytes objects. Passing elements that are not bytes may cause TokenSource or atom to raise TypeError or ValueError.
    - TokenSource and atom must be available and conform to their expected interfaces:
        - TokenSource(text) must be constructible with List[bytes] and its iterator must yield tokens (bytes).
        - atom(src, token) must accept (TokenSource, bytes) and return a parsed _Atom or raise an exception.

Postconditions:
    - On normal completion (no exceptions), all tokens produced by TokenSource have been consumed and a corresponding parsed _Atom was yielded for each.
    - If a ProtocolError is raised, either it originated upstream (propagated) or it was created by wrapping a ValueError and annotating the offending token.

## Side Effects:
    - Instantiates TokenSource(text). Any side effects from TokenSource (such as allocating parser state) occur.
    - Delegates to atom(src, token), which may have side effects not visible here; gen_parsed_response itself performs no I/O and does not mutate global state.
    - Exceptions from TokenSource construction occur before the try block and propagate unchanged.

## Control Flow:
flowchart TD
    Start([call gen_parsed_response(text)]) --> CreateGen[returns generator object]
    CreateGen --> IterateStart([on first next()/iteration])
    IterateStart --> CheckEmpty{text falsy/empty?}
    CheckEmpty -- Yes --> StopImmediate([raise StopIteration])
    CheckEmpty -- No --> ConstructTS[instantiate TokenSource(text)]
    ConstructTS -->|raises any exception| Propagate([exception propagates to caller])
    ConstructTS --> LoopStart[enter try: for token in src]
    LoopStart --> NextToken[yield next token from src -> token]
    NextToken --> CallAtom[call atom(src, token)]
    CallAtom --> YieldAtom[yield atom(...) result]
    YieldAtom --> LoopStart
    CallAtom -->|raises ProtocolError| ReRaiseProto[re-raise ProtocolError]
    CallAtom -->|raises ValueError| WrapAndRaise[wrap ValueError into ProtocolError("%s: %r", err, token) and raise]
    CallAtom -->|raises other Exception| PropagateOther[exception propagates unchanged]
    LoopStart --> EndStream([no more tokens -> StopIteration])

## Examples (conceptual):
- Typical iteration pattern:
    1) Client code receives IMAP response fragments and assembles them as a list of bytes.
    2) Call gen_parsed_response(text) to obtain a generator.
    3) Iterate the generator to consume parsed atoms; handle ProtocolError to detect malformed protocol responses.

- Error handling pattern:
    - Surround iteration with try/except ProtocolError to detect protocol-level parsing errors. If a ProtocolError is caught, its message may include the representation of the token that caused a ValueError, or token may be None if the error occurred before the first token was produced.

## Implementation notes for reimplementers:
    - Ensure the function is a generator function (it must contain yield) so that calling it returns a generator object; the top-level empty-input check should be left in place so the generator yields nothing for empty input.
    - Preserve the pattern of catching ValueError and converting it to ProtocolError with the original ValueError message and the repr(token).
    - Maintain the behavior of re-raising ProtocolError unchanged.
    - Do not catch exceptions raised during TokenSource construction if you want parity with the original: those exceptions occur before the try/for loop and will propagate directly.

## `imapclient.response_parser.parse_fetch_response` · *function*

## Summary:
Parse a list of raw IMAP response fragments representing one or more FETCH responses into a defaultdict that maps message identifiers (sequence number or UID) to dictionaries of parsed attributes, converting INTERNALDATE and ENVELOPE to higher-level Python types and producing BodyData for BODY/BODYSTRUCTURE.

## Description:
- Known callers (in provided snapshot):
    - No direct callers were discovered in the provided code snapshot. Typically this function is called by higher-level IMAP-response dispatchers or FETCH-handling code immediately after assembling the server response fragments (List[bytes]) so the client can work with a typed, convenient representation of FETCH results.

- Responsibility boundary:
    - This function is responsible for:
        * Driving the token stream returned by gen_parsed_response(text).
        * Interpreting the token stream as repeated pairs of (message-id, attribute-tuple) items.
        * Validating basic structural invariants (msg_response must be a tuple; attribute/value items must appear in pairs).
        * Converting particular attributes to richer Python types:
            - UID and sequence numbers -> int (via _int_or_error)
            - INTERNALDATE -> datetime or None (via _convert_INTERNALDATE)
            - ENVELOPE -> Envelope object (via _convert_ENVELOPE)
            - BODY and BODYSTRUCTURE -> BodyData (via BodyData.create)
        * Assembling and merging per-message attribute dictionaries and returning a mapping keyed by message id (or UID when uid_is_key is True).
    - It intentionally does not:
        * Decode bytes to text for scalar fields (subject, message-id, etc.) — raw bytes are preserved.
        * Implement higher-level semantics such as deduplication beyond update-merging, or client-specific normalization beyond date/envelope/body conversions.

## Args:
    text (List[bytes]):
        - A list of bytes fragments representing server response lines/chunks to be parsed.
        - Special-case: when text == [None] the function returns immediately with an empty defaultdict (see Returns).
        - Preconditions: elements should be bytes (or the type expected by the lexer). Supplying non-bytes may raise exceptions from the lexer/parsers.

    normalise_times (bool, default True):
        - Controls whether date/time conversion performed by the INTERNALDATE and ENVELOPE converters normalises timezones (see _convert_INTERNALDATE/_convert_ENVELOPE documentation).

    uid_is_key (bool, default True):
        - If True and a UID attribute is present for a message, that UID integer becomes the key in the returned mapping for that message.
        - If False, the mapping key remains the message sequence number and the UID is stored inside the inner dict under the b"UID" key.

## Returns:
    collections.defaultdict[int, dict]
    - A mapping from integers to per-message dicts. Types and semantics:
        * Mapping keys:
            - Normally the message sequence number (int) parsed as the first atom for each message.
            - If a UID attribute appears and uid_is_key is True, the UID (int) becomes the mapping key for that message.
        * Inner dict keys: attribute names as uppercase bytes (e.g., b"SEQ", b"UID", b"INTERNALDATE", b"ENVELOPE", b"BODY").
        * Inner dict values:
            - b"SEQ": int (sequence number)
            - b"UID": int (only present if uid_is_key is False, or when uid_is_key True the UID is used as the outer key and not duplicated inside the inner dict)
            - b"INTERNALDATE": datetime.datetime | None (via _convert_INTERNALDATE)
            - b"ENVELOPE": Envelope (via _convert_ENVELOPE)
            - b"BODY" / b"BODYSTRUCTURE": BodyData (via BodyData.create)
            - Any other attribute: raw token value as produced by the parser (bytes, tuples, etc.)
    - Special-return detail (important):
        * If the function returns early because text == [None], it returns collections.defaultdict() constructed with no default factory (i.e., defaultdict(None)). In the normal parsing path it returns collections.defaultdict(dict) whose default factory is dict. This differs in missing-key behavior:
            - defaultdict(dict): accessing parsed_response[some_missing_key] will create and return a new dict.
            - defaultdict(None): accessing a missing key raises KeyError (behaves like a plain dict when a key is missing).
        * The difference only matters to callers that access missing keys rather than using .get() or iterating existing keys. The early-return path is used solely for the specific sentinel input [None] and returns an empty mapping.

    - Merge semantics:
        * When multiple FETCH fragments or repeated attribute tuples target the same mapping key, the parser uses parsed_response[msg_id].update(msg_data) to merge the new msg_data into the existing inner dict. This means:
            - Keys in later msg_data overwrite previous values for the same attribute name.
            - Attributes not present in later fragments remain as previously parsed.
        * Therefore callers should be aware that the final per-message dict reflects the last-seen value for any duplicated attribute keys.

## Raises:
    ProtocolError (imapclient.exceptions.ProtocolError):
        - Raised exactly in these code-checked situations:
            * ProtocolError("unexpected EOF") — when a message ID was read but the following msg_response tuple is missing because the token stream ended.
            * ProtocolError("bad response type: %r" % msg_response) — when the item following a message-id is not a tuple.
            * ProtocolError("uneven number of response items: %r" % msg_response) — when the msg_response tuple contains an odd number of elements (attribute/value pairs must be even).
            * ProtocolError from _int_or_error when the message-id or UID cannot be converted to int — the error messages used at call sites are "invalid message ID" and "invalid UID".
        - ProtocolError raised by gen_parsed_response propagates unchanged.
    Other exceptions:
        - Exceptions from helper converters (e.g., IndexError/TypeError from _convert_ENVELOPE for malformed envelope tuples, AttributeError from _convert_INTERNALDATE if non-bytes are passed) propagate to the caller. These are not wrapped by this function.

## Constraints:
- Preconditions:
    - text must represent a valid input for gen_parsed_response (a sequence of bytes fragments).
    - The token stream must present items in the pattern: <message-id atom>, <tuple-of-attribute-value-pairs>, <message-id>, <tuple>, ...
    - Each attribute tuple must contain attribute/value pairs (even length), and attributes are expected to be bytes (the function .upper()s them).
- Postconditions:
    - If no exception is raised, the returned mapping contains one entry per parsed message id (or UID if uid_is_key True) and each per-message dict includes at least b"SEQ" plus any other attributes present in the response, with conversions applied for INTERNALDATE, ENVELOPE, and BODY/BODYSTRUCTURE.

## Side Effects:
- No direct I/O or network access.
- Allocates and returns a collections.defaultdict and constructs Envelope/BodyData objects by calling helper routines.
- Any side effects of the helper routines (gen_parsed_response, _convert_*, BodyData.create) are their own responsibilities and not performed by parse_fetch_response directly.

## Control Flow:
flowchart TD
    Start([call parse_fetch_response(text, normalise_times, uid_is_key)]) --> CheckNone{text == [None]?}
    CheckNone -- Yes --> ReturnEmpty[return empty defaultdict(None)]
    CheckNone -- No --> CreateGen[response = gen_parsed_response(text)]
    CreateGen --> InitParsed[parsed_response = defaultdict(dict)]
    InitParsed --> LoopStart[while True:]
    LoopStart --> GetSeq[try: seq = _int_or_error(next(response), "invalid message ID")]
    GetSeq --> SeqStop{StopIteration?}
    SeqStop -- Yes --> BreakLoop[break -> return parsed_response]
    SeqStop -- No --> GetMsg[try: msg_response = next(response)]
    GetMsg --> MsgEOF{StopIteration?}
    MsgEOF -- Yes --> RaiseEOF[raise ProtocolError("unexpected EOF")]
    MsgEOF -- No --> TypeCheck{isinstance(msg_response, tuple)?}
    TypeCheck -- No --> RaiseBadType[raise ProtocolError("bad response type: ...")]
    TypeCheck -- Yes --> EvenCheck{len(msg_response) % 2 == 0?}
    EvenCheck -- No --> RaiseUneven[raise ProtocolError("uneven number of response items: ...")]
    EvenCheck -- Yes --> BuildMsgData[start with msg_data = {b"SEQ": seq}]
    BuildMsgData --> ForEachPair[for i in range(0,len(msg_response),2): process attribute/value]
    ForEachPair --> UpperKey[word = attribute.upper()]
    UpperKey --> UIDCheck{word == b"UID"?}
    UIDCheck -- Yes --> uid = _int_or_error(value,"invalid UID") --> KeyPolicy{uid_is_key?}
    KeyPolicy -- True --> SetKey[msg_id = uid]
    KeyPolicy -- False --> msg_data[b"UID"] = uid
    UIDCheck -- No --> INTERNALDATE?{word == b"INTERNALDATE"}
    INTERNALDATE? -- Yes --> msg_data[word] = _convert_INTERNALDATE(value, normalise_times)
    INTERNALDATE? -- No --> ENVELOPE?{word == b"ENVELOPE"}
    ENVELOPE? -- Yes --> msg_data[word] = _convert_ENVELOPE(value, normalise_times)
    ENVELOPE? -- No --> BODY?{word in (b"BODY", b"BODYSTRUCTURE")}
    BODY? -- Yes --> msg_data[word] = BodyData.create(value)
    BODY? -- No --> msg_data[word] = value
    ForEachPair --> AfterPairs[parsed_response[msg_id].update(msg_data)]
    AfterPairs --> LoopStart

## Examples:
- Minimal conceptual example (explicit mapping of what is produced).
    - Suppose the token stream (as parsed by gen_parsed_response) yields these logical items in order:
        1) message-id atom -> 1
        2) msg_response tuple -> (b'UID', b'100', b'INTERNALDATE', b'21-Feb-2021 09:05:03 +0000', b'SUBJECT', b'Hi')
    - With default normalise_times=True and uid_is_key=True, the returned mapping will have key 100 (UID) and a value something like:
        {100: {b'SEQ': 1, b'INTERNALDATE': <datetime object or None>, b'SUBJECT': b'Hi'}}
      Notes:
        * b'INTERNALDATE' is the result of _convert_INTERNALDATE(value, True) and may be a datetime or None if unparsable.
        * b'SUBJECT' remains raw bytes.
    - With uid_is_key=False the same input yields:
        {1: {b'SEQ': 1, b'UID': 100, b'INTERNALDATE': <datetime or None>, b'SUBJECT': b'Hi'}}

- Merge/overwrite example:
    - If the token stream yields two items for the same message (same seq or same UID key depending on uid_is_key):
        * First item produces msg_data {b"SEQ": 1, b"SUBJECT": b"Hello", b"FLAG": b"\\Seen"}
        * Second item produces msg_data {b"SEQ": 1, b"SUBJECT": b"Updated", b"INTERNALDATE": <...>}
      After both are processed the inner dict is updated by the second: SUBJECT is "Updated", FLAG remains from first, INTERNALDATE is present from second. In other words, later values overwrite earlier ones for the same attribute key.

- Error example:
    - If the parser sees a message-id but the stream ends before the attribute tuple can be read, the function raises ProtocolError("unexpected EOF") and returns nothing. Callers should catch ProtocolError to handle malformed or truncated server responses.

Notes for implementers:
- This function depends on gen_parsed_response for tokenization and on the helper converters referenced; it assumes gen_parsed_response yields items in the expected pattern (msg-id followed by a tuple for that message). The exact representation of the raw input (text) is determined by the lexer/tokeniser; this function operates on the parsed atoms produced by that generator.

## `imapclient.response_parser._int_or_error` · *function*

## Summary:
Attempt to convert a parser token to a Python int; if conversion fails, raise ProtocolError with a diagnostic message.

## Description:
A small helper used by the IMAP response parser to coerce a token-like value into an integer and ensure parsing code raises a consistent ProtocolError when the token is not an integer.

Known callers:
    - No callers were discovered in the provided code snapshot. Intended callers are response-parsing routines that need numeric values (e.g., sequence numbers, UIDs, message sizes). Call sites should handle ProtocolError as a parsing failure.

Why this is a separate function:
    - Encapsulates the conversion plus standardized error-wrapping (same exception type and message format) so integer parsing sites do not duplicate try/except logic or error-message formatting.

## Args:
    value (typing_imapclient._Atom):
        - The token to convert to int.
        - Type information: use the function with the same token types produced by the response lexer; the code treats the input opaquely and passes it to Python's built-in int() for conversion.
        - Note: _Atom is an internal typing alias used in this module; do not assume a narrower type beyond "something passed by the lexer/parser".
    error_text (str):
        - Short descriptive text that identifies what integer was expected (e.g., "expected message number", "invalid size").
        - This text is prepended to the ProtocolError message.

## Returns:
    int
        - The integer produced by int(value).
        - There are no alternate return paths; on failure the function raises ProtocolError.

## Raises:
    ProtocolError (from imapclient.exceptions)
        - Raised when the conversion int(value) raises either TypeError or ValueError.
        - The exact exception message is constructed as "%s: %s" % (error_text, repr(value)).
        - Examples of inputs that trigger ProtocolError:
            * None (int(None) raises TypeError)
            * Non-numeric strings like "abc" (int("abc") raises ValueError)
            * Strings with non-decimal content such as "0x10" (without base specified) raise ValueError

## Constraints:
    Preconditions:
        - The caller should provide an error_text that meaningfully describes the expected integer for diagnostic purposes.
        - No range or semantic checks are performed here; callers must validate ranges if needed.
    Postconditions:
        - If the function returns, the caller receives a built-in Python int corresponding to value.
        - If conversion failed, a ProtocolError is raised and no integer is returned.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    Start --> TryConvert
    TryConvert -->|int(value) succeeds| ReturnInt
    TryConvert -->|TypeError or ValueError| RaiseProtocolError
    ReturnInt --> End
    RaiseProtocolError --> End

## Notes on conversion behavior and edge cases:
    - Numeric strings: "42", " 42 ", "+7", "-3" convert successfully.
    - Bytes that represent decimal digits (e.g., b"123") are accepted by int() and convert to 123.
    - Booleans convert because bool is a subclass of int: True -> 1, False -> 0.
    - Floating-point inputs are converted by truncation toward zero: int(3.9) -> 3, int(-1.2) -> -1. This function does not reject floats; callers that require rejection of non-integer numeric tokens must check before calling.
    - Strings with non-decimal formats (e.g., "0x10") raise ValueError unless parsed with an explicit base; this function does not supply a base and therefore will raise ProtocolError for such strings.
    - None and other non-numeric objects will raise TypeError and be wrapped as ProtocolError.

## Examples:
    # Successful conversions
    _int_or_error("42", "expected integer")   # returns 42
    _int_or_error(7, "expected integer")      # returns 7
    _int_or_error(b"123", "expected integer") # returns 123
    _int_or_error(True, "expected count")     # returns 1

    # Float is accepted and truncated (callers that require integers should guard first)
    _int_or_error(3.9, "expected integer")    # returns 3

    # Failure: non-numeric string -> ProtocolError (message uses repr(value))
    try:
        _int_or_error("abc", "invalid size")
    except ProtocolError as e:
        # e.args[0] == "invalid size: 'abc'"
        handle_protocol_error(e)

    # Failure: None -> ProtocolError
    try:
        _int_or_error(None, "expected id")
    except ProtocolError as e:
        # e.args[0] == "expected id: None"
        handle_protocol_error(e)

## `imapclient.response_parser._convert_INTERNALDATE` · *function*

## Summary:
Convert an IMAP INTERNALDATE token (an _Atom) into a Python datetime, returning None for absent or unparsable values.

## Description:
This helper normalises and parses a server-provided INTERNALDATE token by delegating to the shared parse_to_datetime routine. Typical callers are response-parsing code paths that consume IMAP FETCH/ENVELOPE responses and need to convert an INTERNALDATE token into a datetime for storing, comparing, or presenting message timestamps.

Known callers within the provided snapshot:
- No explicit call sites for this function are present in the provided repository excerpt. In typical IMAP client implementations it is invoked from response_parser functions that handle INTERNALDATE tokens returned by FETCH or ENVELOPE responses.

Why this is extracted into a separate function:
- Converting an INTERNALDATE involves consistent handling of None (absent tokens), parse failures, and the normalisation option. Extracting this logic centralises the policy of "return None for absent/unparsable date strings" and keeps the higher-level response parsing code simpler and less error-prone. The function acts as a thin, well-documented adaptor around parse_to_datetime with a stable return policy.

## Args:
    date_string (_Atom)
        - Type: typing_imapclient._Atom (at runtime expected to be bytes or None)
        - Semantics: The raw token value representing an INTERNALDATE as returned by the server. Typical examples are bytes like b'21-Feb-2021 09:05:03 +0000' or b'21-Feb-2021 09.05.03 +0000'.
        - Allowed values: bytes containing a server timestamp, or None to indicate missing/absent token.
        - Interdependencies: If date_string is None, the function returns None immediately and normalise_times is ignored.

    normalise_times (bool, optional)
        - Type: bool
        - Default: True
        - Semantics: Passed through to parse_to_datetime. When True, and when the parsed timestamp includes a timezone offset, parse_to_datetime will convert the resulting aware datetime to the system local time and return a tz-naive datetime representing the same instant. When False, parse_to_datetime can return an aware datetime with a FixedOffset tzinfo when the input contains a timezone offset.

## Returns:
    Optional[datetime.datetime]
    - None:
        * If date_string is None.
        * If date_string is present but parse_to_datetime fails to parse it (parse_to_datetime raises ValueError). In both cases the function returns None rather than propagating ValueError.
    - datetime.datetime:
        * If parse_to_datetime successfully parses the byte string, the returned value is whatever parse_to_datetime returns: either a tz-aware datetime (when normalise_times is False and a timezone offset was present) or a tz-naive datetime (when normalise_times is True after conversion, or if the original timestamp had no timezone offset).
    - Notes:
        * The function does not convert types; it simply forwards the byte token to parse_to_datetime and returns that result (unless the token is None or parse_to_datetime raised ValueError).

## Raises:
    AttributeError
        - Condition: If date_string is not a bytes object, parse_to_datetime (via its internal _munge helper) may attempt to call .decode('latin-1') on it; that will raise AttributeError. This exception is not caught here and will propagate to the caller.

    TypeError or other exceptions (propagated)
        - Condition: parse_to_datetime may raise other exceptions (for example, TypeError if the parsed time tuple does not contain sufficient fields for datetime construction, or exceptions originating from FixedOffset or datetime_to_native). These exceptions are not caught by this function and will propagate.

    ValueError
        - Note: parse_to_datetime can raise ValueError on parse failure, but this function catches ValueError and returns None instead of raising. Therefore callers will not observe ValueError from this wrapper.

## Constraints:
Preconditions:
    - The caller should treat date_string as either None or a bytes object containing an IMAP timestamp token. Passing other types may lead to AttributeError in parse_to_datetime.
    - The module-level dependency parse_to_datetime must be available and behave as documented (it accepts bytes and supports the `normalise` boolean flag).

Postconditions:
    - If the function returns a datetime, that datetime represents the instant described by the server token (subject to parse_to_datetime's handling of timezones and normalisation).
    - If the function returns None, either the input was None or the input could not be parsed as a valid timestamp.

## Side Effects:
    - None observable. The function performs no I/O and does not mutate global state. It delegates to parse_to_datetime which similarly has no persistent side effects (it may consult system timezone info when normalising, but does not mutate state).

## Control Flow:
flowchart TD
    Start[Start]
    Start --> CheckNone{date_string is None?}
    CheckNone -- Yes --> ReturnNone1[return None]
    CheckNone -- No --> TryParse[try: call parse_to_datetime(date_string, normalise=normalise_times)]
    TryParse --> ParseSuccess{parse_to_datetime returns datetime?}
    ParseSuccess -- Yes --> ReturnDT[return datetime]
    TryParse -- ValueError --> ReturnNone2[return None]
    TryParse -- OtherException --> Propagate[exception propagates to caller]

## Examples:
1) Successful parse (typical happy path)
    - Input: a bytes token representing an INTERNALDATE, using default normalisation.
    - Example usage:
        dt = _convert_INTERNALDATE(b'21-Feb-2021 09:05:03 +0000')
        if dt is not None:
            # dt is a datetime representing the same instant (converted to local time if parse_to_datetime normalised)
            pass

2) Missing token
    - Input: None (absent INTERNALDATE)
    - Example usage:
        dt = _convert_INTERNALDATE(None)
        # dt is None; caller can treat this as "no INTERNALDATE present"

3) Unparsable token
    - Input: bytes that are not a valid timestamp
    - Example usage with handling:
        dt = _convert_INTERNALDATE(b'not a date')
        if dt is None:
            # handle missing or unparsable INTERNALDATE
            pass

4) Non-bytes input (error case that propagates)
    - If caller accidentally passes a str instead of bytes, parse_to_datetime may raise AttributeError while attempting to decode; this function does not catch that error. Caller example:
        try:
            dt = _convert_INTERNALDATE("21-Feb-2021 09:05:03 +0000")  # incorrect: str not bytes
        except AttributeError:
            # handle programming error: ensure tokens are bytes before calling
            pass

## `imapclient.response_parser._convert_ENVELOPE` · *function*

## Summary:
Convert a raw IMAP ENVELOPE response (positional tuple) into an Envelope object: parse the date (optionally normalising it), copy scalar fields, and convert each address list into a tuple of Address objects or None.

## Description:
- Known callers within the codebase:
  - Other functions in response_parser that build higher-level FETCH/ENVELOPE results for client APIs. Callers pass the parsed token structure produced by the response lexer/parser when processing an IMAP server ENVELOPE response.
  - Typical trigger: invoked during handling of FETCH/ENVELOPE responses when the library must present a typed Envelope to the caller.

- Why this logic is extracted:
  - Encapsulates the positional-to-named mapping of the IMAP ENVELOPE structure so higher-level parsing remains concise and consistent.
  - Centralises parsing rules (date normalisation, address conversion rules) to avoid duplication across various response-processing code paths.

## Args:
    envelope_response (_Atom)
        - Runtime expectation: a sequence-like object (normally a tuple) with at least 10 positional elements indexed 0..9:
            0: date (bytes or None)
            1: subject (bytes or None)
            2: from (None or a sequence/tuple of address tuples)
            3: sender (None or a sequence/tuple of address tuples)
            4: reply-to (None or a sequence/tuple of address tuples)
            5: to (None or a sequence/tuple of address tuples)
            6: cc (None or a sequence/tuple of address tuples)
            7: bcc (None or a sequence/tuple of address tuples)
            8: in-reply-to (bytes or None)
            9: message-id (bytes or None)
        - Address list items (positions 2..7) when present are expected to be iterable sequences (commonly tuples) of address tuples; each address tuple is expected to contain the 4 elements required by the Address constructor (commonly bytes).
        - The function uses duck-typing: TYPE_CHECKING assertions exist for static analysis but are not enforced at runtime.
    normalise_times (bool, default True)
        - Passed through to parse_to_datetime to control date/time normalisation behavior.

## Returns:
    Envelope
    - Field mapping and semantics:
      - date: datetime.datetime | None — result of parse_to_datetime(envelope_response[0], normalise=normalise_times) if envelope_response[0] is truthy and parse succeeds; None if the date slot is falsey or parse_to_datetime raises ValueError.
      - subject: bytes | None — copied verbatim from envelope_response[1].
      - from_: Optional[Tuple[Address, ...]] — converted from envelope_response[2]: None if that slot is falsey (e.g., None or an empty tuple); otherwise a tuple of Address instances built from each truthy address tuple found.
      - sender, reply_to, to, cc, bcc: follow the same conversion rules as from_ for positions 3..7 respectively.
      - in_reply_to: bytes | None — copied from envelope_response[8].
      - message_id: bytes | None — copied from envelope_response[9].
    - Important edge-case behaviors:
      - If an address list slot (2..7) is falsey (for example None or an empty tuple), the corresponding Envelope field will be None.
      - If an address list is truthy (non-empty) but all contained address tuples are falsey or skipped, the corresponding Envelope field becomes an empty tuple (zero-length tuple).
      - Any falsey address tuple elements inside a non-empty address list are skipped (not converted).
      - Raw bytes are preserved for subject, in_reply_to, message_id, and address tuple components; no automatic decoding to text occurs here.

## Raises:
- IndexError
    - If envelope_response does not contain at least ten elements, indexing envelope_response[0]..[9] will raise IndexError.
- TypeError
    - If an address tuple does not have the expected number of items required by Address(...), the Address constructor call Address(*addr_tuple) may raise TypeError.
- Other exceptions may propagate:
    - parse_to_datetime ValueError is caught and handled (date set to None), so ValueError from parsing will not propagate.
    - Any other exception raised by parse_to_datetime (e.g., TypeError for an unexpected argument type) or by Address(...) (validation errors) will propagate to the caller.

## Constraints:
- Preconditions:
    - envelope_response must be indexable and iterable for the slices used (particularly length >= 10).
    - Address expects address tuples in the format required by its constructor; callers should ensure address tuple elements follow the expected IMAP envelope address shape.
- Postconditions:
    - The returned Envelope will have date either as a datetime or None.
    - Each address-related field will be either None (if the original slot was falsey) or a tuple of Address instances (possibly empty).
    - The function does not mutate envelope_response.

## Side Effects:
- None. No I/O, no global state mutation, and no external network or filesystem interaction.

## Control Flow:
flowchart TD
    Start[Start: receive envelope_response] --> CheckDate{envelope_response[0] truthy?}
    CheckDate -- Yes --> TryParse[Try parse_to_datetime(envelope_response[0])]
    TryParse --> ParseOK{parse_to_datetime raised ValueError?}
    ParseOK -- No --> SetDate[dt = parsed datetime]
    ParseOK -- Yes --> SetDateNone[dt = None (ValueError caught)]
    CheckDate -- No --> SetDateNone
    SetDate --> LoadScalars[subject,in_reply_to,message_id <- envelope_response[1], [8], [9]]
    LoadScalars --> ForAddrLists[for addr_list in envelope_response[2:8]]
    ForAddrLists --> AddrListCheck{addr_list truthy?}
    AddrListCheck -- No --> AppendNone[append None to addresses]
    AddrListCheck -- Yes --> IterateAddrTuples[for addr_tuple in addr_list]
    IterateAddrTuples --> AddrTupleCheck{addr_tuple truthy?}
    AddrTupleCheck -- No --> SkipTuple[skip]
    AddrTupleCheck -- Yes --> BuildAddress[addr = Address(*addr_tuple); append to addrs]
    BuildAddress --> IterateAddrTuples
    SkipTuple --> IterateAddrTuples
    IterateAddrTuples --> AppendTuple[append tuple(addrs) to addresses]
    AppendTuple --> ForAddrLists
    AppendNone --> ForAddrLists
    ForAddrLists --> BuildEnvelope[Construct Envelope(...) from dt, subject, addresses[0..5], in_reply_to, message_id]
    BuildEnvelope --> ReturnEnvelope[Return Envelope]

## Examples:
- Typical conversion
    envelope_response = (
        b"Mon, 7 Feb 2022 12:34:56 +0000",            # date
        b"Hello",                                     # subject
        ((b"Alice", b"", b"alice", b"example.com"),), # from (non-empty)
        None,                                         # sender (falsey -> None)
        None,                                         # reply-to
        ((b"Bob", b"", b"bob", b"example.net"),),     # to
        (),                                           # cc (empty tuple -> treated as falsey -> None)
        None,                                         # bcc
        b"<inreply@example.org>",                     # in-reply-to
        b"<msgid@example.org>",                       # message-id
    )
    envelope = _convert_ENVELOPE(envelope_response)
    # envelope.date -> datetime parsed from the date bytes (or None if parsing fails)
    # envelope.subject -> b"Hello"
    # envelope.from_ -> tuple(Address(...),)
    # envelope.sender -> None
    # envelope.cc -> None  (empty tuple in original response becomes None)

- Non-empty address list where contained tuples are falsey
    envelope_response = (
        None, b"Subj",
        ((),),   # from is truthy (tuple containing a falsey empty tuple) -> processed
        None, None, None, None, None, None, None
    )
    envelope = _convert_ENVELOPE(envelope_response)
    # envelope.from_ -> tuple()  (empty tuple, because addr_list was truthy but contained only falsey tuples)

- Defensive usage pattern
    try:
        envelope = _convert_ENVELOPE(raw_envelope)
    except IndexError:
        # Unexpected structure: not enough positional elements
        handle_protocol_error()
    except TypeError:
        # Address tuple shape mismatch or Address constructor rejected values
        handle_protocol_error()

## `imapclient.response_parser.atom` · *function*

*No documentation generated.*

## `imapclient.response_parser.parse_tuple` · *function*

## Summary:
Parse and consume an IMAP-style parenthesized tuple from the token stream and return it as a Python tuple of atoms.

## Description:
This function reads tokens from the provided TokenSource iterator and builds a tuple by repeatedly parsing each inner atom until it encounters the closing token b")". Typical callers:
- imapclient.response_parser.atom: invoked when the lexer yields a b"(" token; atom(src, b"(") calls this function to parse the tuple's contents.
- Higher-level IMAP response parsing routines that need to interpret parenthesized lists of atoms produced by the response lexer.

Why it is a separate function:
- Parsing a parenthesized sequence is a self-contained, recursive grammar operation (tuples may nest). Extracting it centralizes loop/termination logic, provides clear recursion boundaries (parse_tuple calls atom which may call parse_tuple for nested tuples), and keeps the top-level token-dispatch logic in atom small and readable.

## Args:
    src (TokenSource): An iterable lexer adapter that yields bytes tokens. Must be positioned such that the opening parenthesis that triggered this call has already been consumed (i.e., parse_tuple begins reading the first token after the "("). The TokenSource also exposes .current_literal, which may be required by nested atom() calls when parsing literals.

## Returns:
    tuple: A Python tuple whose elements are atoms (typing_imapclient._Atom). Each element is the result of atom(src, token) for a token inside the parentheses. Possible element types include:
    - None (for the IMAP NIL token)
    - int (for numeric tokens)
    - bytes (for raw or literal tokens)
    - str (for quoted-string tokens)
    - nested tuple (for nested parenthesized lists)
    If the tuple is empty (i.e., immediate closing token b")"), returns the empty tuple ().

## Raises:
    ProtocolError: Raised when the token stream ends before a matching closing b")" is found. The exception message includes a stringified partial tuple of already-parsed atoms, e.g. 'Tuple incomplete before "(...)"'.
    Any exception raised by atom(src, token) or by the TokenSource iterator/lexer (for example, ProtocolError from literal handling, AttributeError from missing current_literal, ValueError, etc.) will propagate without being caught.

## Constraints:
Preconditions:
- The caller must have just observed the opening parenthesis b"(" and then call parse_tuple(src). parse_tuple does not itself verify or consume an opening "("; it starts by consuming the next token from src.
- src must be a valid TokenSource whose iterator yields bytes tokens and whose lex may provide current_literal when atom() expects a literal. If atom() attempts to use current_literal and it is unavailable, atom() (not parse_tuple) may raise ProtocolError or AttributeError.

Postconditions:
- On success, the TokenSource iterator has advanced past and consumed the closing b")" token; the returned tuple represents all parsed inner atoms.
- On error (ProtocolError due to EOF or any propagated exception), the iterator position reflects the point of failure (it may be exhausted).

## Side Effects:
- Mutates the state of src by consuming tokens from its iterator (advances the lexer's position).
- Indirectly may trigger exceptions from atom() which can be raised to callers.
- No file, network, stdout I/O or global state mutation is performed by parse_tuple itself.

## Control Flow:
flowchart TD
    Start[Start: called after '(' consumed] --> Loop[for token in src]
    Loop --> CheckClose{token == b")"?}
    CheckClose -- yes --> ReturnTuple[return tuple(out) -- success]
    CheckClose -- no --> ParseAtom[call atom(src, token)]
    ParseAtom --> Append[append atom result to out]
    Append --> Loop
    Loop --> EOF[iterator exhausted?]
    EOF -- yes --> RaiseError[raise ProtocolError('Tuple incomplete before "(%s"' % _fmt_tuple(out))]
    EOF -- no --> (handled in loop)

## Examples:
- Typical successful parse:
    Given a token stream representing "(1 NIL \"abc\")", when atom() sees the initial b"(" it calls parse_tuple(src). parse_tuple will consume tokens for 1, NIL, and "abc", returning (1, None, b'abc') (types depend on atom's decoding rules).

- Handling nested tuples:
    If the token stream is "((1 2) 3)", parse_tuple will produce ((1, 2), 3) by recursively calling atom/parse_tuple for the inner "(".

- Error handling:
    If the response is truncated and b")" never appears, parse_tuple raises ProtocolError. Example usage:
        try:
            result = parse_tuple(src)
        except ProtocolError as exc:
            # handle incomplete or malformed tuple response
            raise

Notes:
- Because parse_tuple depends on atom(src, token) for interpreting individual tokens, many semantic edge conditions (literal size mismatches, missing literal text, invalid quoted strings) are surfaced via exceptions raised by atom and will propagate through parse_tuple unchanged.
- The returned tuple preserves the order of tokens as yielded by the TokenSource.

## `imapclient.response_parser._fmt_tuple` · *function*

## Summary:
Convert a list of atoms into a single space-separated string by stringifying each element.

## Description:
This is a small internal helper that takes a sequence of atoms (or atom-like values) and produces a single string representation suitable for inclusion in formatted response text. No callers are enumerated in the provided file scope; the function is intended for use anywhere in the response parsing/formatting code that needs to render a tuple of atoms as a single token-separated string.

This logic is extracted into a dedicated function to centralize the simple but repeated operation of:
- converting each element to its string form, and
- joining them with single spaces,
so callers need not repeat the join-and-stringify pattern and the intent is clearer at call sites.

## Args:
    t (List[_Atom]): A list of atoms (typing_imapclient._Atom). Each element will be passed to Python's str() before joining. There is no additional validation; elements should be amenable to str() (i.e., their __str__ should not raise). The function accepts an empty list.

## Returns:
    str: A single string consisting of each element from `t` converted via str() and concatenated with a single space character separating elements.
    - If `t` is empty, returns the empty string ''.
    - All returned values are standard Python str objects.

## Raises:
    Any exception raised by the conversion of an element to string or by iteration will propagate to the caller.
    - For example, if an item's __str__ implementation raises an Exception, that exception is not caught and will bubble up.
    - There are no explicit raises in the function body (no ProtocolError or similar are raised here).

## Constraints:
    Preconditions:
    - `t` must be an iterable (specifically a List) of items expected to be converted to strings.
    - The function does not accept None in place of the list argument; passing None will raise a TypeError when iterating.

    Postconditions:
    - The return value is a str whose tokens equal the stringified elements of `t`, separated by single spaces.
    - The function does not mutate the input list or any external state.

## Side Effects:
    - None. The function performs no I/O, network activity, global state mutation, or external service calls.
    - It only iterates over the input and constructs a new string.

## Control Flow:
flowchart TD
    Start --> CheckEmpty
    CheckEmpty -->|t is empty| ReturnEmpty
    CheckEmpty -->|t non-empty| Iterate
    Iterate --> ConvertEach["Call str(item) for each item"]
    ConvertEach --> Join["Join converted strings with ' '"]
    Join --> ReturnJoined
    ReturnEmpty["Return ''"] --> End
    ReturnJoined["Return joined string"] --> End
    End

## Examples:
- Typical usage with string atoms:
    - Input: ['INBOX', 'FLAGS', '\\Seen']
    - Output: "INBOX FLAGS \\Seen"

- Usage with mixed types (ints, custom objects with __str__):
    - Input: [1, 'BODY', custom_atom]
    - Output: "1 BODY <string from custom_atom.__str__()>"
    - If custom_atom.__str__ raises an exception, that exception will propagate and the caller must handle it.

- Empty list:
    - Input: []
    - Output: ""

