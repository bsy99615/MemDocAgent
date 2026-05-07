# `response_types.py`

## `imapclient.response_types.Envelope` · *class*

## Summary:
A passive container representing an IMAP ENVELOPE structure: typed fields for the envelope date, subject, address lists (from/sender/reply-to/to/cc/bcc), and message threading identifiers (In-Reply-To and Message-ID).

## Description:
Envelope models the parsed result of an IMAP ENVELOPE response item. It exists so the IMAP response parser can return a typed, attribute-accessible representation of the canonical envelope fields defined by the IMAP protocol (date, subject, from, sender, reply-to, to, cc, bcc, in-reply-to, message-id).

Typical instantiation and callers:
- An IMAP response parser or higher-level mailbox client constructs an Envelope instance and populates its attributes from parsed tokens. The parser is the canonical factory for Envelope objects.
- Consumers of the IMAP client (message listing, fetch handlers) read Envelope attributes to present message headers or to implement higher-level behaviour (address display, threading).

Motivation and responsibility boundary:
- Envelope is deliberately a lightweight, typed data holder — it does not perform parsing, validation beyond Python type annotation, or I/O. Its responsibility is to collect the standard envelope fields in a single object so callers can read them with predictable attribute names and types. Converting bytes to displayable text or formatting addresses is the caller's responsibility (or the caller may use the Address.__str__ helper).

## State:
Note: The class provides attribute type annotations but does not define a custom __init__ in the source shown. Therefore instances start with no guaranteed attribute values until a caller/parser assigns them. The following describes the attributes and their expected types (as declared).

- date: Optional[datetime.datetime]
  - Type: datetime.datetime or None
  - Meaning: the envelope "date" field interpreted as a datetime when the parser can produce one; absent or unparsable dates may be represented as None.
  - Invariant: when non-None, consumers may rely on datetime methods; do not assume timezone normalization unless the parser documents it.

- subject: bytes
  - Type: bytes
  - Meaning: raw subject bytes exactly as returned by the IMAP server (not decoded to text).
  - Invariant: callers should treat this as raw bytes and decode using util.to_unicode or other appropriate decoding before presenting as text.

- from_: Optional[Tuple["Address", ...]]
  - Type: tuple of Address instances, or None
  - Meaning: the envelope "FROM" address list; each Address holds raw parts (name, route, mailbox, host).
  - Invariant: when non-None, each element is an Address (see Address documentation). The tuple preserves the order returned by the server.

- sender: Optional[Tuple["Address", ...]]
  - Type and semantics: same shape and semantics as from_, representing the "SENDER" envelope field.

- reply_to: Optional[Tuple["Address", ...]]
  - Type and semantics: same shape and semantics as from_, representing the "REPLY-TO" envelope field.

- to: Optional[Tuple["Address", ...]]
  - Type and semantics: same shape and semantics as from_, representing the "TO" envelope field.

- cc: Optional[Tuple["Address", ...]]
  - Type and semantics: same shape and semantics as from_, representing the "CC" envelope field.

- bcc: Optional[Tuple["Address", ...]]
  - Type and semantics: same shape and semantics as from_, representing the "BCC" envelope field.

- in_reply_to: bytes
  - Type: bytes
  - Meaning: the raw In-Reply-To header value(s) as returned by the server.
  - Invariant: callers should decode or parse this value if they need a textual form or to extract Message-ID tokens.

- message_id: bytes
  - Type: bytes
  - Meaning: the raw Message-ID header value as returned by the server.
  - Invariant: treat as raw bytes until decoded.

Class invariants:
- Envelope instances are passive; attribute types should conform to the annotations above when populated by a parser.
- There are no automatic conversions: bytes fields remain bytes until callers decode them.
- Address-containing attributes (from_, sender, reply_to, to, cc, bcc) when present must contain Address instances (see Address component documentation for expected Address semantics).

## Lifecycle:
Creation:
- Instantiate with the default constructor (Envelope()). The source does not declare an explicit __init__, so attributes are not automatically initialized — a parser or caller must assign values to attributes before use.
- Preferred factory: the IMAP response parser that produced the tokens for the envelope. If constructing manually, callers must set each attribute with correct typed values.

Usage:
- Typical sequence:
  1. Create Envelope() (or obtain one from the parser).
  2. Populate attributes from parsed IMAP envelope tokens:
     - set date to a datetime or None,
     - set subject, in_reply_to, message_id to bytes,
     - set address lists (from_/sender/reply_to/to/cc/bcc) to tuples of Address or None.
  3. Consume attributes: decode subject/message_id/in_reply_to via util.to_unicode, and format addresses via str(address) or by manually converting Address parts.
- There are no methods to call on Envelope itself. Consumers are free to read attributes in any order after they have been populated.

Destruction:
- No special cleanup required. Envelope holds only simple objects and Address instances; normal garbage collection handles lifecycle.

## Method Map:
flowchart TD
    Create[Create Envelope()] --> Populate[Populate attributes from parser]
    Populate --> Use[Read attributes in consumer code]
    Use --> Decode[Decode bytes via util.to_unicode when needed]
    Use --> Format[Format Address objects via str(Address) or custom routines]
    Decode --> Present[Display or process textual headers]
    Format --> Present

(Note: Envelope defines no methods; the flow shows typical creation/population/consumption steps.)

## Raises:
- Envelope itself does not raise exceptions on creation or attribute access.
- Potential runtime errors for consumers:
  - Attribute access before assignment will raise AttributeError if the attribute has not been set on the instance.
  - Converting bytes attributes (subject, in_reply_to, message_id) using util.to_unicode or performing operations on a presumed datetime in date may raise exceptions from those conversion/operation functions if the underlying value is of an unexpected type. Consumers should validate types before operating.

## Example:
Typical usage pattern (described in steps, not executable code in this document):
1. A parser creates an Envelope instance for a single message envelope.
2. The parser assigns:
   - envelope.date = a datetime.datetime or None
   - envelope.subject = b'Raw subject bytes'
   - envelope.from_ = (Address instances, ...) or None
   - envelope.to = (Address instances, ...) or None
   - envelope.in_reply_to = b'<message-id@host>' (bytes)
   - envelope.message_id = b'<message-id@host>' (bytes)
3. A consumer receives the Envelope and prepares values for display:
   - subject_text = util.to_unicode(envelope.subject)
   - for addr in envelope.from_ (if not None): display_text = str(addr)  (Address.__str__ will convert Address parts to text and format)
4. No cleanup is required; the Envelope and contained Address instances are garbage-collected when no longer referenced.

## `imapclient.response_types.Address` · *class*

## Summary:
A lightweight container for the four raw parts of an IMAP/email address (name, route, mailbox, host) with a string formatter that converts stored bytes into a human-readable RFC-style address.

## Description:
Address holds the raw parsed components produced by an IMAP address parser: name (display name), route (obsolete/route field), mailbox (local-part), and host (domain). Its primary role is to keep the parsed byte fields together and provide a single, canonical textual representation via __str__. The __str__ implementation centralizes three responsibilities: (1) convert stored bytes/str fields to text using util.to_unicode, (2) construct the local@domain form only when both mailbox and host are present, and (3) produce the final RFC-2822-style formatted address using email.utils.formataddr. __str__ only reads these fields and does not mutate the Address instance.

Common instantiation patterns:
- An IMAP response parser populates Address instances from parsed tokens and returns them to callers.
- Callers that construct Address manually should populate its attributes with bytes before formatting.

## State:
Attributes (declared on the class; no __init__ sets defaults):
- name: bytes
  - Meaning: display name (e.g., b"John Doe").
  - Valid values: bytes or str values accepted by util.to_unicode; empty bytes (b'') represents no display name.
  - Invariant: convertible by util.to_unicode to a str for display.
- route: bytes
  - Meaning: route information from IMAP address parsing (rarely used in practice).
  - Valid values: bytes; may be b'' if absent.
  - Note: route is stored for completeness but is not referenced by the __str__ formatter.
- mailbox: bytes
  - Meaning: local-part (left of '@'), e.g., b'john'.
  - Valid values: bytes; may be b'' if missing.
  - Invariant: when both mailbox and host are non-empty, __str__ will combine them as local@domain.
- host: bytes
  - Meaning: domain-part (right of '@'), e.g., b'example.com'.
  - Valid values: bytes; may be b'' if missing.

Class invariants:
- Instances are passive data holders; __str__ reads attributes but does not change them.
- Consumers are responsible for populating attributes with appropriate byte/text values prior to formatting.

## Lifecycle:
Creation:
- Instantiate with the default constructor (Address()). There is no custom __init__, so attributes are not initialized by the class.
- Typical factory: an IMAP parser or higher-level helper will create an Address instance and assign name, route, mailbox, and host.

Usage:
- Assign the parsed byte values to the instance attributes (name, route, mailbox, host).
- Call str(address) when a displayable, RFC-style representation is required. __str__ converts fields to unicode and formats the address; it uses both mailbox and host to produce a local@domain form only when both are present, otherwise it uses whichever of mailbox or host is present for the address portion.
- There is no required call ordering beyond ensuring attributes are set before invoking __str__.

Destruction:
- No resources to release; normal garbage collection applies. The class does not implement context-manager or close semantics.

## Method Map:
flowchart TD
    Create[Create Address()] --> Populate[Populate attributes: name, route, mailbox, host]
    Populate --> Format[Call __str__()]
    Format --> Convert[util.to_unicode(name/mailbox/host)]
    Convert --> BuildAddr[If mailbox and host -> mailbox@host else mailbox or host]
    BuildAddr --> formataddr[formataddr((name_text, address_text))]
    formataddr --> Result[Return formatted string]

## Raises:
- The class itself does not raise custom exceptions. However, __str__ delegates to util.to_unicode and email.utils.formataddr; any exceptions raised by those functions (for example, TypeError for unsupported types) will propagate to the caller.
- Callers should ensure attributes are present and are bytes or strings that util.to_unicode can handle; otherwise conversion errors may occur.

## Example:
A typical usage scenario (described in prose):
- An IMAP parser creates an Address instance, assigns bytes for name, mailbox, and host (route may be b''), and returns the instance.
- The consumer calls str(address). Internally, __str__ converts the byte fields to text, constructs "mailbox@host" when both parts exist, and returns a formatted string such as "John Doe <john@example.com>".
- No explicit cleanup is required after use.

### `imapclient.response_types.Address.__str__` · *method*

## Summary:
Return a human-readable RFC-2822-style string for the Address by converting stored bytes/str fields to text and formatting the display name and address; does not modify the Address instance.

## Description:
Called whenever an Address instance is converted to text (for example via str(address) or when an Address is interpolated into a string). Typical call sites include logging, building message headers, or presenting parsed ENVELOPE/address-list data to users or other components.

This behavior is encapsulated in __str__ to centralize: (1) conversion of bytes fields to text using util.to_unicode, (2) construction of the local@domain form only when both mailbox and host are present, and (3) final RFC-style formatting via email.utils.formataddr. Centralizing ensures consistent decoding, error handling, and formatting across the codebase.

## Args:
    None

## Returns:
    str: A formatted address string produced by email.utils.formataddr((display_name, address)).
         - When both mailbox and host are truthy: the address portion is to_unicode(mailbox) + "@" + to_unicode(host), producing a result like:
             - Display Name <local@domain>
         - When only one of mailbox or host is truthy: the address portion is to_unicode(mailbox or host), producing:
             - Display Name <local>  (if only mailbox present)
             - Display Name <domain> (if only host present)
         - If display name is empty/blank, email.utils.formataddr will produce a representation that omits the name and returns the address portion according to its own rules.
         - The method always returns a Python str (because util.to_unicode returns str for bytes and passes through str).

## Raises:
    - The method itself does not deliberately raise exceptions for the documented, expected attribute types (bytes or str).
    - If self.name, self.mailbox, or self.host contain values that are neither bytes nor str, util.to_unicode will pass them through unchanged and email.utils.formataddr may raise a TypeError or otherwise behave unexpectedly. This is an undefined/invalid-input condition (see Preconditions).

## State Changes:
    Attributes READ:
        - self.mailbox
        - self.host
        - self.name
    Attributes WRITTEN:
        - None (no mutation of the Address instance)

## Constraints:
    Preconditions:
        - Per the Address class definition, name, mailbox, and host are expected to be bytes (or str). The method relies on that typing.
        - mailbox/host falsiness (e.g., empty bytes b'' or empty string '') is interpreted as "absent"; the code falls back to the available field.
    Postconditions:
        - The returned value is a str formatted via email.utils.formataddr from to_unicode(self.name) and the computed address string.
        - The Address object remains unchanged.

## Side Effects:
    - util.to_unicode will perform ASCII decoding for bytes; on UnicodeDecodeError it logs a warning and falls back to decoding with errors="ignore". That logging is the only side effect observable outside the process memory (no I/O or network calls).
    - No mutation of external objects occurs.

## Examples:
    - Given name=b"John Doe", mailbox=b"local", host=b"example.com" -> "John Doe <local@example.com>"
    - Given name=b"", mailbox=b"local", host=b"" -> "local" or a format consistent with email.utils.formataddr for an empty name and non-empty address portion
    - Given name=b"Alice", mailbox=b"", host=b"example.com" -> "Alice <example.com>"

## `imapclient.response_types.SearchIds` · *class*

## Summary:
A minimal list subclass that stores integer identifiers (as list elements) and carries one additional metadata attribute, modseq, initialized to None.

## Description:
SearchIds extends the built-in list type without altering list semantics. Its only purpose is to provide a list container (constructed with the same arguments as list) and to expose a single instance attribute, modseq, for optional integer metadata. The class itself performs no validation on list elements or on modseq; it simply provides the attribute and the usual list behavior.

## State:
- Inherited list storage:
  - Contents: the list elements stored by the instance (inherited behavior from list).
  - The class does not enforce element types; callers may place any objects in the list. Typical usage is to store integers, but this is a convention, not enforced in code.
- Attributes added by SearchIds:
  - modseq: Optional[int]
    - Default value: None (set unconditionally in __init__).
    - Valid values: None or an int. The class does not validate type or range on assignment.
- Class invariants:
  - Each instance has a modseq attribute present after construction.
  - The instance behaves identically to a built-in list for all list operations.

## Lifecycle:
- Creation:
  - Call with no arguments to create an empty SearchIds instance: SearchIds()
  - Call with a single iterable argument to initialize list contents: SearchIds(iterable)
  - Any positional arguments accepted follow list.__init__ semantics; invalid arguments will raise the same exceptions list.__init__ would raise.
  - On construction, the class forwards the provided args to list.__init__ and then sets self.modseq = None.
- Usage:
  - Use any standard list operations (append, extend, insert, pop, remove, indexing, slicing, iteration, sort, reverse, etc.).
  - Read or assign the metadata attribute directly: ids.modseq = 123 or current = ids.modseq.
  - There is no required order for mutations and modseq updates; callers may set modseq before or after modifying the list.
- Destruction:
  - No special cleanup is required. Instances are regular Python objects subject to normal garbage collection.

## Method Map:
graph TD
    A[Create SearchIds(...)] --> B[list.__init__ invoked]
    B --> C[SearchIds.__init__ sets modseq = None]
    C --> D[List API available (append/extend/...) ]
    D --> E[Caller reads/writes modseq attribute]
    E --> F[Instance used/passed/returned]

## Raises:
- TypeError (or other exceptions) propagated from list.__init__ if the provided constructor arguments are invalid for list.
- Runtime exceptions from list methods (e.g., IndexError from pop on empty list, ValueError from remove when item absent) are not intercepted and will propagate normally.

## Example:
1) Create an empty container and add elements:
   ids = SearchIds()
   ids.append(1)
   ids.extend([2, 3])
   ids.modseq = 10

2) Create from an iterable:
   ids = SearchIds([4, 5, 6])
   assert ids.modseq is None

3) Typical access patterns:
   first = ids[0]
   for uid in ids:
       process(uid)
   # modseq can be updated independently:
   ids.modseq = None  # or an integer value

### `imapclient.response_types.SearchIds.__init__` · *method*

## Summary:
Initializes the list storage via the list base class constructor and ensures the instance has a modseq metadata attribute set to None.

## Description:
This constructor forwards all positional arguments to the parent list.__init__ so the instance is initialized exactly like a built-in list (empty or populated from an iterable). After list initialization it attaches a single instance attribute, modseq, and sets it to None.

Known callers and context:
- Any code that constructs a SearchIds instance — typically response-parsing or result-collection code that needs a list-like container for message identifiers and an associated optional modseq metadata field. Construction can occur during protocol response handling, factory/helper functions that produce ID lists, or direct consumer code that needs the combined container+metadata object.
- Lifecycle stage: invoked at object creation time. After this method returns the instance is ready for normal list operations and for callers to read or assign the modseq metadata.

Why this logic is a separate method:
- The initialization needs two steps: (1) perform the normal list initialization semantics provided by list.__init__, and (2) ensure the additional attribute modseq exists and has a defined default (None). Placing this logic in __init__ keeps the attribute guarantee local to object construction and avoids repeating the assignment wherever SearchIds is instantiated.

## Args:
    *args (Any): Positional arguments forwarded unchanged to list.__init__.
        - Typical usage: no arguments to create an empty list, or a single iterable argument to populate the list contents (e.g., SearchIds([1,2,3])).
        - Allowed values: any arguments accepted by the built-in list constructor. Invalid argument combinations will produce the same exceptions that list.__init__ would raise.

## Returns:
    None: This initializer does not return a value. It mutates self by initializing the list contents and by setting the modseq attribute.

## Raises:
    TypeError (or other exceptions from list.__init__):
        - If the provided constructor arguments are invalid for list.__init__, the same exception (for example TypeError) is propagated.
    (No additional exceptions are raised by this method itself.)

## State Changes:
    Attributes READ:
        - None (this implementation does not read any existing instance attributes)

    Attributes WRITTEN:
        - list storage (inherited): the underlying list contents of self are initialized/populated by calling list.__init__(*args).
        - self.modseq: set to None unconditionally.

## Constraints:
    Preconditions:
        - self must be a freshly constructed instance of SearchIds (standard Python object state for __init__).
        - The provided *args must be valid for the built-in list constructor (e.g., either no args or a single iterable).

    Postconditions:
        - After return, self behaves as a fully-initialized list with contents equivalent to calling list.__init__(*args).
        - After return, the instance has an attribute modseq, and its value is None.
        - Callers can read or assign self.modseq to any value (the class does not enforce type or range checks).

## Side Effects:
    - Mutates only the instance (self): initializes its inherited list storage and sets self.modseq = None.
    - No I/O is performed and no external services are invoked.
    - If an iterable argument is passed, elements are copied into the new list as list.__init__ semantics dictate (any side effects of iterating that iterable are those of the iterable itself, not this constructor).

## `imapclient.response_types.BodyData` · *class*

## Summary:
Represents a parsed IMAP BODY or BODYSTRUCTURE response as an immutable, sequence-like container where the first element is either a list of part BodyData objects for multipart messages or the single-part descriptor; provides a factory that converts the raw parser tuples into this nested representation.

## Description:
BodyData exists to encapsulate the raw token tuple(s) returned by an IMAP server for BODY or BODYSTRUCTURE fetch responses and to provide a small, well-defined view onto multipart vs single-part messages.

Usage scenarios:
- A low-level IMAP response parser yields a tuple of tokens (bytes and/or nested tuples). Call BodyData.create(response) to transform that parser output into a BodyData instance that:
  - Recursively converts nested part tuples into BodyData instances for each part when the response represents a multipart body.
  - Leaves single-part responses wrapped unchanged (except for being stored in the BodyData container).
- Higher-level code inspects is_multipart to decide whether to iterate parts or to parse single-part mime attributes from the tuple fields.

Motivation and responsibility boundary:
- Motivation: The raw parser returns nested tuples and bytes which are inconvenient to work with directly. BodyData defines a small, immutable, sequence-like abstraction that:
  - Encodes multipart structure by replacing the first element with a Python list of BodyData parts for multipart responses.
  - Preserves the original ordering and remaining fields in the tuple tail (after the parts).
- Responsibility: BodyData is a thin wrapper over the parser output — it must not interpret or decode MIME fields (that responsibility belongs to higher-level helpers). It only converts nested tuple structures into nested BodyData objects and exposes an is_multipart discriminator.

## State:
Primary state and invariants an implementation must provide:
- Logical contents (sequence-like):
  - The BodyData instance shall behave like an immutable sequence/tuple of elements (indexable, iterable, supports len()).
  - The underlying stored sequence is a tuple whose first element is either:
    - For multipart responses: a Python list of BodyData instances (each representing one part).
    - For single-part responses: a tuple or atomic tokens describing the single-part body (as produced by the parser).
  - Any subsequent elements (index >= 1) represent additional BODY/STRUCTURE metadata fields (e.g., flags, sizes, envelope fields) exactly in the order produced by the IMAP parser.
- Attribute semantics (recommended names and types for implementers):
  - No mandatory public attributes are required; callers will index the instance (self[0]) and iterate it. If an implementation exposes attributes, they should not mutate underlying data.
- Invariants:
  - The instance is immutable once constructed (no mutation methods).
  - If is_multipart is True, then self[0] is a list and every element of that list is a BodyData instance.
  - If is_multipart is False, then self[0] is not a list (typically a tuple or other atomic token as produced by the parser).
  - The ordering of elements in the tuple-like container must be preserved relative to the original parser response.

## Lifecycle:
Creation:
- Primary creation API: BodyData.create(response: Tuple[_Atom, ...]) -> BodyData
  - response must be a non-empty tuple produced by the parser where each _Atom is either:
    - bytes (or text tokens treated as atomic tokens from the parser), or
    - tuple (a nested tuple that represents one part).
  - The create() factory inspects response[0]:
    - If response[0] is a tuple: treat the response as a multipart body. Collect the leading sequence of items that are tuple instances (these are the parts). Stop collecting when a bytes token is encountered (the first bytes token after parts marks the start of the tail fields) or when the response is exhausted.
      - Recursively call BodyData.create(part) for each collected part (each part is a tuple).
      - Construct a new container by replacing the leading parts with a single list object containing those BodyData part instances, then append the remaining tail tokens unchanged. Return cls(new_tuple) where cls is BodyData (or subclass).
    - Otherwise: return cls(response) — the factory wraps the original response tuple directly into a BodyData instance.
  - create() performs no decoding of bytes; it only restructures nested tuples into BodyData objects.
- Alternate creation (implementer note):
  - The class's constructor (cls(...)) must accept a tuple-like sequence representing the internal data and produce an immutable, indexable BodyData instance. The create() factory assumes that cls(consumed_tuple) will produce an instance whose self[0] and other indices behave as described.

Usage:
- Typical sequence:
  1. body = BodyData.create(response_tuple)
  2. if body.is_multipart:
         iterate over body[0] (a list of BodyData parts) to inspect/handle each part
     else:
         parse single-part description fields from body (e.g., mime type, encoding, size) by indexing into body tuple positions expected by higher-level parsers
- No ordering between methods is required beyond creating via create() (or constructor) before reading. is_multipart is a read-only discriminator and may be called at any time after construction.

Destruction:
- No special cleanup, close, or context-manager behavior is required. Instances are pure data and are cleaned up by normal garbage collection.

## Method Map:
flowchart TD
    create[BodyData.create(response)] --> inspect[Check response[0] type]
    inspect --> |tuple| collect[Collect leading tuple parts]
    collect --> recurse[Recursively call BodyData.create(part) for each part]
    recurse --> build[Replace leading parts with list of BodyData parts]
    build --> wrap[Call cls(new_tuple) -> BodyData instance]
    inspect --> |not tuple| wrap_orig[Call cls(response) -> BodyData instance]
    wrap_orig --> done[Return BodyData]
    build --> done

    is_multipart[body.is_multipart] --> check_first[Return isinstance(self[0], list)]

## Raises:
- BodyData.create may raise:
  - IndexError: if response is empty (response[0] access). Callers must ensure the parser provided a non-empty tuple.
  - TypeError: if the provided response is not indexable like a tuple (e.g., passing None or an atomic bytes value). Implementations should either validate input type and raise TypeError with a clear message, or allow natural exceptions (TypeError/AttributeError) to propagate.
  - RecursionError: if the nested structure is extremely deep, recursive calls to create may hit Python recursion limits.
- The class constructor (cls(response)) should raise:
  - TypeError: if response is not a tuple-like sequence suitable for indexing/iteration; implementations may validate and raise a clearer TypeError for misuse.
- No other exceptions are raised by BodyData itself; conversion/decoding exceptions are outside its responsibility.

## Example:
Scenario: parser returns a multipart BODYSTRUCTURE for a two-part message with an octet-size tail token after parts.
- Given parser output (schematic):
    response = (
        (b'text', b'plain', (b'charset', b'utf-8'), b'...', b'...', b'...'),   # part 1 tuple
        (b'text', b'html',  (b'charset', b'utf-8'), b'...', b'...', b'...'),   # part 2 tuple
        b'1234'  # first bytes token after parts — start of tail metadata
    )
- body = BodyData.create(response)
  - body.is_multipart -> True
  - body[0] is a list of two BodyData instances: [BodyData(part1_tuple), BodyData(part2_tuple)]
  - body[1] == b'1234' (tail token preserved)
- For a single-part message:
    response = (b'text', b'plain', (b'charset', b'utf-8'), b'...', b'...')
    body = BodyData.create(response)
    - body.is_multipart -> False
    - body[0] is the original single-part descriptor (not a list) and body acts like a tuple wrapper.

Implementation blueprint (what a reimplementation must provide):
- Provide a class BodyData that behaves like an immutable sequence of elements (indexable, iterable, supports len()).
- Implement create() exactly as described: inspect response[0], detect multipart by tuple-typed first element, collect consecutive tuple parts up to the first bytes token (or end), recursively wrap each part with create(), then replace the leading parts by a single list of the created BodyData parts and construct the instance via cls(new_tuple). For non-multipart, simply wrap the input tuple via cls(response).
- Implement is_multipart as a read-only property returning True iff the first element of the instance is a list.

Notes and constraints:
- BodyData does not decode bytes into strings; any decoding should be deferred to higher-level helpers or consumers.
- The create() method uses TYPE_CHECKING-only assertions in the reference source; those are optional and intended for static type checkers. Runtime implementations do not need to perform these assertions but must ensure correctness of input types where appropriate.

### `imapclient.response_types.BodyData.create` · *method*

## Summary:
Factory classmethod that constructs a BodyData instance from a raw IMAP BODYSTRUCTURE-like tuple, recursively converting leading nested tuple subparts into BodyData objects and placing them as a list in the returned instance's first element when the input represents a multipart entity.

## Description:
- Purpose: Convert a raw parsed IMAP body/bodystructure tuple into a BodyData instance suitable for use by higher-level code. The method encapsulates the recursive creation logic required for nested multipart structures.
- Core behavior:
  - If the first element of the provided response is a tuple, treat the response as indicating a multipart container. Collect the leading elements of the response that are not bytes (the code collects tuple elements until it encounters a bytes element), recursively create BodyData for each collected subpart, and return cls(...) where the first element is a list of those subpart BodyData objects followed by the remainder (tail) of the original response beginning at the index where the loop stopped.
  - If the first element is not a tuple, return cls(response) directly (single-part passthrough).
- Recursive behavior: The method calls cls.create(part) for each collected subpart tuple, so nested multipart structures are handled by repeated re-entry into this same method.
- Why a separate method: The logic performs non-trivial, recursive parsing/assembly of nested tuples into structured BodyData instances. Encapsulating it in a factory method avoids duplicating recursion and keeps construction semantics centralized.

Known callers / invocation context:
- This is the canonical constructor-like entrypoint for producing BodyData from a raw tuple. The source code shows recursive self-calls (cls.create), but specific external callsites are not present in this method's body and thus are not enumerated here.

## Args:
    cls (type[BodyData]): The class used for instantiation (supports subclassing).
    response (Tuple[_Atom, ...]): Raw, non-empty tuple representing an IMAP body or bodystructure.
        - Expected element types:
            * nested tuples for subparts when multipart is present
            * bytes objects that delimit the end of the initial subpart list
            * other _Atom-compatible tokens for remaining fields
        - The method only inspects response[0] and then iterates the tuple elements.

## Returns:
    BodyData: An instance of cls constructed from the provided response tuple.
        - Multipart case (response[0] is a tuple):
            * The returned instance equals cls((subparts_list, ) + tail)
            * subparts_list is a Python list of BodyData instances created by cls.create for each collected subpart tuple.
            * tail is the slice of the original response starting at the index where the loop encountered the first bytes element (response[i:]). If the loop completes without encountering a bytes element, tail is response[i:] where i is the last index from the loop (see edge cases).
        - Single-part case (response[0] is not a tuple):
            * The returned instance equals cls(response) (no recursion).
        - No special sentinel values are returned.

## Raises:
    IndexError:
        - If response is empty, access to response[0] raises IndexError.
    TypeError:
        - If response is not subscriptable or not tuple-like such that response[0] access is invalid, a TypeError (or a related exception) will be raised by the runtime before the method can proceed.
    Any exception raised by cls(...) constructor:
        - If cls(...) performs validation and raises ValueError/TypeError/etc., those exceptions propagate unchanged.

## State Changes:
    Attributes READ:
        - None on existing instances or class-level mutable state. The method reads only the provided response argument.
    Attributes WRITTEN:
        - None on existing objects. New BodyData instance(s) (and sub-instances) are created and returned; the method does not mutate external objects.

## Constraints:
    Preconditions:
        - response must be a tuple-like, non-empty sequence (the method immediately accesses response[0]).
        - When response indicates multipart (response[0] is a tuple), the code expects that subparts are represented as tuple elements and that at some point a bytes element will occur to mark the end of subparts in typical inputs. The implementation will still operate if no bytes element is present (see edge cases).
        - cls must accept the constructed tuple/list shape as a valid constructor argument (i.e., cls((...,), ...)).

    Postconditions:
        - The returned value is an instance of cls.
        - For multipart inputs, the returned instance's first element is a list of BodyData instances corresponding to the leading subpart tuples.
        - For non-multipart inputs, the returned instance encapsulates the original response tuple unchanged.

## Edge cases and exact runtime behavior:
    - Empty response: Raises IndexError due to response[0] access.
    - No bytes encountered while collecting subparts:
        * The loop appends every element to parts and, because no break occurs, the loop finishes normally; the variable i retains the last index value from enumerate. The method then returns cls(([...subparts...],) + response[i:]) where response[i:] is a one-element tail containing the last original element. This can cause the last subpart tuple to appear both inside the subparts list (after recursive conversion) and again as an unconverted tuple in the tail. This is an exact consequence of the control flow in the implementation.
    - TYPE_CHECKING guard:
        * The in-loop TYPE_CHECKING block contains an assert to indicate that collected parts are tuples, but that code is conditional on TYPE_CHECKING and does not execute at runtime; no runtime validation is performed there.

## Side Effects:
    - No I/O, network, or filesystem activity.
    - No mutation of the input tuple.
    - Allocates new BodyData instances (and possibly many recursively).

## Implementation notes (precise, for reimplementation):
    - Signature: create(cls, response: Tuple[_Atom, ...]) -> "BodyData" and defined as a classmethod.
    - Check multipart: use isinstance(response[0], tuple).
    - If multipart:
        * Initialize an empty list parts = [].
        * Iterate for i, part in enumerate(response):
            - If isinstance(part, bytes): break the loop (stop collecting subparts).
            - Append part to parts.
        * Build subparts_list = [cls.create(part) for part in parts]
        * Compute tail = response[i:] (i is the index at break or the last index if loop completed).
        * Return cls((subparts_list,) + tail)
    - If not multipart: return cls(response)
    - Do not rely on the TYPE_CHECKING assertion for runtime validation.

### `imapclient.response_types.BodyData.is_multipart` · *method*

## Summary:
Return a boolean indicating whether this BodyData instance represents a multipart entity by checking whether the first element is a list; exposed as a read-only property and does not mutate the object.

## Description:
Known callers and context:
- Typically consulted after parsing an IMAP BODYSTRUCTURE into a BodyData instance to decide whether to iterate sub-parts (multipart) or treat the value as a single body part.
- The BodyData.create classmethod constructs multipart BodyData values by placing a Python list at index 0 for multipart structures; this property relies on that construction convention.
- This logic is a dedicated @property because it captures a single structural predicate (is the first element a list?) that callers frequently need. Centralizing the check avoids repeating the index-and-isinstance pattern and documents the intended representation.

Usage (textual example):
- Access as instance.is_multipart (property access, do not call). For a multipart BodyData this returns True; for a regular part it returns False. Callers that are unsure whether the BodyData contains any elements should handle IndexError.

## Args:
- None.

## Returns:
- bool: True if and only if self[0] exists and is an instance of list (this includes subclasses of list). False if self[0] exists but is not a list (for example tuple, bytes, str, None, etc.).

Edge cases:
- The method does not return special sentinels; it returns a Python bool when it returns normally.

## Raises:
- IndexError: Raised when the BodyData has no element at index 0 (equivalently, len(self) == 0). This is the exact condition: attempting to evaluate self[0] on an empty sequence-like BodyData.
- Note: If self is not a sequence-like object (which would be a programming error in the module), accessing self[0] may raise TypeError; this is not part of the intended behavior for BodyData instances constructed by the module.

## State Changes:
Attributes READ:
- self[0] (reads the first element of the BodyData sequence)

Attributes WRITTEN:
- None (no modification of self)

## Constraints:
Preconditions:
- The caller should expect self to be a BodyData (sequence-like) object produced by the module's parsing routines (e.g., BodyData.create). If the caller cannot guarantee that self has at least one element, they should handle IndexError.

Postconditions:
- No side effects or mutations are performed on self.
- The returned boolean accurately reflects whether the first element was a list at the moment of the check.

## Side Effects:
- None. The property performs only an in-memory index and type check; it does not perform I/O, network access, or mutate external state.

