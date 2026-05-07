# `testable_imapclient.py`

## `imapclient.testable_imapclient.TestableIMAPClient` · *class*

## Summary:
A small test-focused subclass of IMAPClient that constructs with a fixed host ("somehost") and overrides the IMAP4 factory method to return the in-memory MockIMAP4 test double.

## Description:
TestableIMAPClient exists to provide a minimal, test-friendly IMAP client subclass that (1) is instantiated without parameters and (2) produces MockIMAP4 connection objects when its IMAP4-creation hook is invoked. This class is intended for unit tests that need an IMAPClient instance whose underlying connection object is a predictable, in-process mock (see the MockIMAP4 component for the mock's behavior and state).

Known call sites / scenarios:
- Unit tests that need an IMAPClient instance but must avoid real network I/O.
- Test helpers that instantiate an IMAPClient and rely on the underlying connection object being a MockIMAP4 instance.

Responsibility boundary:
- TestableIMAPClient does not implement IMAP protocol logic itself; it only configures construction (host) and the IMAP4 factory hook. All other behavior and state are inherited from the IMAPClient base class.

## State:
- Instance attributes introduced by this class: none.
  - The class body defines no new attributes on instances; it relies on IMAPClient for runtime state and behavior.
- Initialization effect:
  - On construction, the parent class IMAPClient is initialized with the literal string "somehost" (super().__init__("somehost")).
  - This means the instance's host-related state (whatever IMAPClient stores) will be initialized using that value.
- Factory override invariant:
  - The method _create_IMAP4 always returns a fresh MockIMAP4 instance as implemented here. Any caller that invokes this method on a TestableIMAPClient will receive a MockIMAP4 object (see MockIMAP4 docs for its attributes and behavior).

Notes about inherited state:
- Public/internal attributes defined by IMAPClient are not redefined here; callers should consult IMAPClient documentation for connection/session attributes, lifecycle flags, and supported operations.

## Lifecycle:
Creation:
- Instantiate without arguments:
  - client = TestableIMAPClient()
  - This calls IMAPClient.__init__ with the single argument "somehost".

Usage:
- The TestableIMAPClient class provides the same public API as its IMAPClient base class (no public methods are added or overridden except the IMAP4 factory hook).
- When the IMAP client implementation needs to create an IMAP4-style connection object, calling the instance method _create_IMAP4() on this subclass will return a MockIMAP4 instance (a test double suitable for in-memory testing; see MockIMAP4 docs).
- Typical test usage patterns:
  - Instantiate TestableIMAPClient().
  - Allow the client or test harness to call _create_IMAP4() (either directly in tests or indirectly via IMAPClient connection setup).
  - Interact with the returned MockIMAP4 according to test needs (inspect conn.sent, set conn.tagged_commands, etc.).

Destruction / cleanup:
- TestableIMAPClient defines no additional cleanup behavior. Any resource management responsibilities are inherited from IMAPClient (if any).
- The mock connection objects returned by _create_IMAP4 are pure in-memory mocks (see MockIMAP4); they require no network teardown.

## Method Map:
flowchart LR
    A[TestableIMAPClient.__init__] --> B[IMAPClient.__init__ called with "somehost"]
    C[TestableIMAPClient._create_IMAP4()] --> D[returns MockIMAP4 instance]
    style A fill:#EFEFEF,stroke:#333,stroke-width:1px
    style B fill:#FFF8DC,stroke:#333,stroke-width:1px
    style C fill:#FFF8DC,stroke:#333,stroke-width:1px
    style D fill:#E6FFE6,stroke:#333,stroke-width:1px

(Interpretation: construction delegates to IMAPClient.__init__ with a fixed host string. The _create_IMAP4 method is an override that returns a MockIMAP4 object.)

## Raises:
- __init__:
  - The TestableIMAPClient.__init__ implementation does not raise exceptions itself.
  - Exceptions may propagate from IMAPClient.__init__ (for example, if the base class validates arguments or performs operations that raise); callers should consult IMAPClient for exact exception behavior.
- _create_IMAP4:
  - As implemented, this method returns a MockIMAP4 instance and does not raise.

## Example:
- Basic instantiation and use in a test:

1) Create the testable client:
    client = TestableIMAPClient()

2) Obtain the mock IMAP4 connection via the factory method:
    mock_conn = client._create_IMAP4()
    # mock_conn is an instance of MockIMAP4 (see MockIMAP4 docs for its API).

3) Use the MockIMAP4 in assertions:
    mock_conn.send(b'A001 NOOP\r\n')
    assert mock_conn.sent.endswith(b'NOOP\r\n')

4) Cleanup: no special cleanup is required for TestableIMAPClient beyond any IMAPClient cleanup routines (if present). Discard the instance when finished.

See also:
- imapclient.testable_imapclient.MockIMAP4 — in-memory MockIMAP4 implementation used by this class as the IMAP4 connection object.

### `imapclient.testable_imapclient.TestableIMAPClient.__init__` · *method*

## Summary:
Initializes the instance by delegating to the IMAPClient base class constructor with the fixed host string "somehost", producing an object whose base-class state is initialized as if constructed for that host.

## Description:
This constructor is invoked when creating a TestableIMAPClient instance (e.g., client = TestableIMAPClient()) during test setup or other code that needs a ready-to-use IMAPClient substitute. Typical callers are unit tests and test helpers that require an IMAPClient instance but must avoid real network I/O.

The implementation intentionally keeps initialization logic minimal and delegated: the method exists so the test-focused subclass can (1) be constructed without parameters and (2) provide a consistent, deterministic host value to the base class. Placing this logic in the constructor (rather than in test helpers or factories) ensures instances of TestableIMAPClient are always created with the same base initialization semantics and so any inherited behavior that depends on the host is predictable in tests.

Implementation contract: the method must call the IMAPClient constructor with the literal string "somehost" and must not perform additional initialization that the base class does not expect.

## Args:
    None

## Returns:
    None

## Raises:
    Any exception raised by IMAPClient.__init__ may propagate unchanged.
    - Example triggers (depend on IMAPClient implementation): argument validation failures, resource-allocation errors, or other initialization-time exceptions raised by the base class.

## State Changes:
Attributes READ:
    - None within this method body (it does not inspect or use any self.<attr> before delegating).

Attributes WRITTEN:
    - Any instance attributes that IMAPClient.__init__ sets as part of normal construction. The exact attributes are defined by the IMAPClient implementation; at minimum the base-class host-related state will be initialized using the literal "somehost".

## Constraints:
Preconditions:
    - No requirements on caller-supplied arguments (constructor takes no parameters).
    - The IMAPClient base class must be callable via super().__init__ and accept a single positional host argument.

Postconditions:
    - After return, self has been initialized as if IMAPClient.__init__(self, "somehost") had been executed:
        * Base-class initialization completed successfully, or an exception was raised and propagated.
        * Any connection/session/host-related attributes that IMAPClient normally establishes for a given host value are set using the value "somehost".

## Side Effects:
    - This method performs no direct I/O itself; however, side effects are those caused by IMAPClient.__init__:
        * possible validations, resource allocation, or other setup performed by the base class.
        * any exceptions raised by base-class initialization will propagate.
    - The method does not modify objects outside of self except indirectly through whatever IMAPClient.__init__ performs.

### `imapclient.testable_imapclient.TestableIMAPClient._create_IMAP4` · *method*

## Summary:
Returns a new in-memory MockIMAP4 instance used in place of a real IMAP4 connection; does not modify the TestableIMAPClient instance.

## Description:
This method constructs and returns a fresh MockIMAP4 object — a unittest-friendly stand-in for a real IMAP connection. It is intended to be invoked at connection-creation time by the IMAP client infrastructure (for example when the client establishes or re-establishes its underlying IMAP4 connection). Typical callers are the connection-establishment code in the IMAPClient base class and test code that relies on TestableIMAPClient to provide a mockable connection object instead of performing real network I/O.

This logic is factored into its own method so subclasses (especially test subclasses) can override how an IMAP4-like connection is created without changing the higher-level connection lifecycle code. It enables dependency injection of mock or alternate connection implementations during tests.

## Args:
    None

## Returns:
    MockIMAP4
    - A newly-constructed MockIMAP4 instance on every call.
    - Never returns None.
    - The returned object is independent of any previous calls (i.e., not a cached/singleton instance).

## Raises:
    - The method itself does not raise. 
    - If MockIMAP4.__init__ or its superclass (unittest.mock.Mock.__init__) were to raise an exception during construction, that exception will propagate to the caller.

## State Changes:
Attributes READ:
    - None (the method does not read any attributes on self)

Attributes WRITTEN:
    - None (the method does not modify self or any of its attributes)

## Constraints:
Preconditions:
    - No preconditions on self or arguments; it can be called at any time.
    - The test environment must have the MockIMAP4 class available (it is defined in the same test-support module).

Postconditions:
    - After the call, the caller receives a ready-to-use MockIMAP4 instance whose initial state matches MockIMAP4's documented defaults (e.g., empty sent buffer, default flags). The TestableIMAPClient instance remains unchanged.

## Side Effects:
    - Allocates a new MockIMAP4 Python object (in-memory).
    - No network I/O, file I/O, or external service calls are performed by this method.
    - Any side effects are limited to whatever MockIMAP4.__init__ performs (which, in this context, does not open sockets or perform I/O).

## `imapclient.testable_imapclient.MockIMAP4` · *class*

## Summary:
A lightweight unittest.mock-based stand-in for an IMAP4 connection used in tests; it records data written via send(), exposes a deterministic _new_tag(), and stores simple command bookkeeping.

## Description:
MockIMAP4 is intended for unit tests that need a controllable, in-process replacement for an IMAP connection object (for example, tests of imapclient.IMAPClient or other code that interacts with an IMAP connection). It inherits from unittest.mock.Mock so it also provides all the usual mocking capabilities (assert_has_calls, call history, attribute injection, etc.). Use this class when you want:
- A fake IMAP object that does not perform network I/O.
- To capture bytes sent by the client under test.
- A deterministic tag generator (_new_tag) and simple storage for tagged commands.

Known callers/factories:
- Tests that construct an IMAP client and inject a connection-like object (e.g., replacing an IMAP4 instance).
- Any test helper that needs a mock implementing basic IMAP-like methods (send and tag generation).

Responsibility boundary:
- This class only simulates a tiny subset of an IMAP connection: it records sent bytes, returns a fixed tag string, and holds a dict for tagged commands. It does not implement protocol parsing, network I/O, authentication, or real STARTTLS behavior.

## State:
Attributes (public and internal):
- use_uid (bool)
  - Type: bool
  - Initial value: True
  - Purpose: indicates whether UID-based operations are expected; provided as a convenience flag for test code that checks this attribute on the connection.
  - Invariant: always a boolean.

- sent (bytes)
  - Type: bytes
  - Initial value: b""
  - Purpose: accumulates every bytes object passed to send(); represents the raw outgoing stream produced by the code under test.
  - Invariant: always a bytes instance. Concatenation behavior implies data passed to send() must be bytes-like; passing non-bytes will raise an error at runtime.

- tagged_commands (Dict[Any, Any])
  - Type: dict
  - Initial value: {}
  - Purpose: a simple map to record commands keyed by their tags (tests or callers may populate this to emulate server behavior or to assert that commands were created).
  - Invariant: always a dict mapping tags to command payloads as chosen by the test.

- _starttls_done (bool)
  - Type: bool
  - Initial value: False
  - Purpose: a minimal flag to indicate whether STARTTLS has been performed; present for tests that toggle or assert TLS state.
  - Invariant: always a boolean. Treated as an internal attribute (leading underscore).

Inheritance note:
- The class subclasses unittest.mock.Mock. All Mock behavior (dynamic attribute creation, call tracking, etc.) is available.

## Lifecycle:
Creation:
- Instantiate with no required arguments: MockIMAP4().
- Optional args/kwargs are forwarded to unittest.mock.Mock.__init__, allowing the usual Mock configuration (e.g., spec, name). There are no additional required parameters.

Usage (typical sequence):
1. Create instance: conn = MockIMAP4()
2. Optionally configure tagged_commands or other attributes directly on the instance (e.g., conn.tagged_commands['tag'] = expected_command).
3. Call send(data: bytes) as the code under test would. Each call appends to conn.sent.
4. Call _new_tag() to obtain the deterministic tag string "tag" if the client under test requests a new tag.
5. Inspect conn.sent, conn.tagged_commands, or use Mock assertions (conn.assert_called*, conn.method_calls) to assert behavior.

Sequencing constraints:
- No strict ordering is enforced by the class. Methods may be called in any order. Tests may depend on send() being called before inspecting sent.

Destruction / cleanup:
- No special destruction is required. Because this is a pure in-memory mock, there are no network sockets or resources to close.
- If test frameworks require cleanup, simply drop references to the instance; Mock provides no close() by default and this class does not implement one.

## Method Map:
flowchart LR
    A[__init__] --> B[send(data: bytes)]
    A --> C[_new_tag() -> "tag"]
    B --> D[updates sent (bytes)]
    C --> E[returns constant "tag"]
    style A fill:#EFEFEF,stroke:#333,stroke-width:1px
    style B fill:#FFF8DC,stroke:#333,stroke-width:1px
    style C fill:#FFF8DC,stroke:#333,stroke-width:1px

(Interpretation: __init__ establishes initial state. send appends bytes to the sent buffer. _new_tag returns the fixed tag string "tag". There are no cross-calls between send and _new_tag.)

## Raises:
- __init__: does not raise explicit exceptions in its body. Any exception would originate from unittest.mock.Mock.__init__ if invalid arguments are passed to that constructor.
- send(data: bytes):
  - If data is not a bytes-like object (for example, a str), Python will raise a TypeError during bytes concatenation (since sent is bytes and += expects bytes). Tests should pass bytes to send().
- _new_tag(): does not raise; returns the literal string "tag".

## Example:
- Create and use the mock to capture outgoing data and obtain a tag.

1) Instantiation:
    conn = MockIMAP4()

2) Record sending data:
    conn.send(b'A001 LOGIN "user" "pass"\r\n')
    conn.send(b'A002 NOOP\r\n')
    # After these calls:
    assert conn.sent == b'A001 LOGIN "user" "pass"\r\nA002 NOOP\r\n'

3) Deterministic tag:
    tag = conn._new_tag()
    assert tag == "tag"

4) Using Mock features:
    # Because MockIMAP4 subclasses unittest.mock.Mock, you can inspect or assert calls
    conn.some_method(1, 2)
    conn.assert_has_calls([('some_method', (1, 2), {})])  # illustrative; use Mock.call helpers in real tests

Notes and edge-cases:
- Always pass bytes to send(); passing str will raise TypeError when concatenating.
- _new_tag returns a constant string "tag" — it does not generate unique tags. Tests relying on unique tags must override this method or simulate tag allocation through other means.
- tagged_commands is provided as a convenience storage only; the class does not automatically populate it.

### `imapclient.testable_imapclient.MockIMAP4.__init__` · *method*

## Summary:
Initializes a Mock-based IMAP4-like object and establishes its testing state by setting default flags and storage used by other mock methods.

## Description:
This constructor prepares a MockIMAP4 instance for use as a drop-in mock of an IMAP4 connection in unit tests. It delegates base initialization to the parent Mock, then creates the attributes used by other MockIMAP4 methods (for example, to accumulate data sent to the connection, track whether STARTTLS was performed, and store tagged commands). 

Known callers and context:
- Instantiated directly in test setups or by helper factories when a test needs a fake IMAP4 connection object. It is invoked during the test setup/lifecycle when building mock connections that stand in for a real IMAP server.
- Typical lifecycle: construct MockIMAP4 in test setup -> call test methods that exercise send(), _new_tag(), or inspect tagged_commands/sent/_starttls_done.

Rationale for being a dedicated method:
- Centralizes all test-specific initial state in one place so other mock methods can rely on consistent attributes.
- Keeps initialization separate from method implementations to make it easy to create fresh, predictable mock instances for each test.

## Args:
    *args (Any): Positional arguments forwarded to the parent unittest.mock.Mock initializer. No interpretation is performed by this constructor.
    **kwargs (Any): Keyword arguments forwarded to unittest.mock.Mock.__init__ (e.g., name, spec, side_effect). Types and allowed values are those accepted by unittest.mock.Mock.

## Returns:
    None

## Raises:
    Any exception raised by unittest.mock.Mock.__init__ if invalid arguments are provided — this constructor does not raise explicitly.

## State Changes:
Attributes READ:
    - None (the constructor does not read any pre-existing self attributes)

Attributes WRITTEN:
    - self.use_uid (bool): Set to True. Indicates that UID-based operations are expected by higher-level code.
    - self.sent (bytes): Initialized to b""; used to accumulate byte data passed into send().
    - self.tagged_commands (Dict[Any, Any]): Initialized to an empty dict; intended to map tags to command state/results used by mock command implementations.
    - self._starttls_done (bool): Set to False; records whether a mock STARTTLS handshake has been performed.

Additionally, the constructor calls super().__init__(*args, **kwargs) which initializes the underlying Mock object's internal state (attributes managed by unittest.mock).

## Constraints:
Preconditions:
    - There are no required preconditions on the caller beyond providing arguments compatible with unittest.mock.Mock.__init__ if any are supplied.

Postconditions:
    - The instance is a functioning unittest.mock.Mock with the four attributes above initialized to their defaults.
    - Other MockIMAP4 methods (e.g., send, _new_tag) can rely on these attributes existing and having the documented types/initial values.

## Side Effects:
    - Calls unittest.mock.Mock.__init__ (may register mock metadata and internal state).
    - No I/O is performed.
    - No network or external service calls are made.
    - No mutation is performed on objects outside of self (only self attributes are set).

### `imapclient.testable_imapclient.MockIMAP4.send` · *method*

## Summary:
Append the provided bytes to the mock object's internal bytes buffer so all data that would have been sent over a real IMAP4 connection is accumulated on the instance for inspection.

## Description:
This method implements the minimal behavior required of an IMAP4-like send routine in a testing mock: it accepts raw bytes and appends them to an in-memory buffer. The class MockIMAP4 initializes that buffer as self.sent = b"" (see MockIMAP4.__init__), and this method extends that buffer with each call.

Known callers:
    - No explicit call sites are present in this file. The method is part of a test-oriented mock (module name testable_imapclient and class inheritance from unittest.mock.Mock indicate test usage). Typical usage is from test code or test fixtures that instantiate MockIMAP4 and exercise code paths that would write protocol bytes; at the moment the repository does not define concrete call sites inside this module.

Why this is a separate method:
    - Centralizes the mock's "send" behavior so tests and other mocks assert against a single observable attribute (self.sent).
    - Mirrors the real object's API surface minimally without performing I/O, keeping tests deterministic and side-effect free.

## Args:
    data (bytes): Required. Raw bytes to append to the instance buffer. Must be a bytes instance; other types are not accepted by the implementation.

## Returns:
    None: The method returns None. The effect is observable via the mutated attribute self.sent.

## Raises:
    TypeError: If data is not a bytes instance, Python will raise a TypeError during the concatenation operation (bytes + non-bytes is not supported).
    AttributeError: If the instance does not have the self.sent attribute (for example, if MockIMAP4.__init__ was not called or the attribute was deleted), attempting to read or assign will raise an AttributeError.
    Note: These exceptions are not explicitly raised by the method; they are the direct consequences of the single concatenation statement in the implementation.

## State Changes:
    Attributes READ:
        self.sent (bytes) — the previous buffer value is read to compute the new value.
    Attributes WRITTEN:
        self.sent (bytes) — set to the result of previous self.sent concatenated with data.

## Constraints:
    Preconditions:
        - The instance must have been initialized such that self.sent exists and is a bytes object. (MockIMAP4.__init__ sets self.sent = b"".)
        - The caller must pass a bytes object for data.
    Postconditions:
        - After the call, self.sent equals the previous value of self.sent concatenated with data.
        - If data is an empty bytes object (b""), self.sent is unchanged (same bytes value).
        - No network I/O occurs; the method is purely in-memory.

## Side Effects:
    - Mutates only the MockIMAP4 instance by updating its self.sent attribute.
    - No I/O, network, or external resource interactions are performed.
    - Repeated use accumulates bytes in memory; very large or many concatenations may increase memory usage.

### `imapclient.testable_imapclient.MockIMAP4._new_tag` · *method*

## Summary:
Returns a fixed string used as a command tag for the mock IMAP4 connection; does not modify object state.

## Description:
Known callers and context:
- Test code or test helpers that simulate issuing IMAP commands against a MockIMAP4 instance. Tests may call this method directly when they need a tag string, or other mock methods (in the same test suite) may call it to create or label tagged commands. The MockIMAP4.__init__ documentation indicates this method is part of the typical test lifecycle: construct MockIMAP4 in test setup -> call test methods that exercise send(), _new_tag(), or inspect tagged_commands/sent/_starttls_done.
- It is invoked during unit-test runtime when a stable, deterministic tag value is required for building mock IMAP command lines, inserting entries into tagged_commands, or asserting expected bytes were sent.

Rationale for being a dedicated method:
- Encapsulates tag generation so tests and other mock methods can call or override a single point to change tag behavior (for example, to return unique tags in more advanced mocks or to instrument tag generation in specific tests).
- Keeps tag logic separate from send/command-building logic to make tests easier to read and to allow targeted overriding or patching.

## Args:
    None

## Returns:
    str: The tag string. For this implementation it always returns the literal "tag".

## Raises:
    None

## State Changes:
Attributes READ:
    - None

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - No preconditions on self or external state; the instance need not have any particular attributes set beyond being a MockIMAP4 object.

Postconditions:
    - Returns the constant string "tag".
    - Leaves the MockIMAP4 instance and any external objects unmodified.

## Side Effects:
    - None. This method performs no I/O, does not call external services, and does not mutate self or any other object.

