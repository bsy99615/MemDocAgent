# `_compat.py`

## `sumy._compat.unicode_compatible` · *function*

## Summary:
A class decorator that makes a class providing a __unicode__ method behave consistently for str() and bytes() across Python 2 vs Python 3 by wiring __str__ and (on Python 3) __bytes__ to the __unicode__ implementation, using UTF-8 for byte conversion.

## Description:
This decorator mutates the given class by attaching or replacing its text/bytes conversion methods so that the class's human-readable text representation comes from a single __unicode__ implementation, and bytes representations are produced by UTF-8 encoding of that text where supported.

Known callers within the provided source context:
- No direct call sites were provided with the function source. In typical usage this decorator is applied to classes across the codebase that implement a __unicode__ method to ensure consistent behavior for str() and bytes() across Python versions.

Why this logic is extracted:
- Responsibility boundary: centralizes cross-Python compatibility plumbing in one reusable decorator rather than duplicating per-class wiring code.
- It enforces the convention that __unicode__ is the canonical text-producing method and encapsulates the version-specific differences (Python 2 vs Python 3) in one place.

## Args:
    cls (type): The class object to mutate and return.
        - Expected to be a new-style class object (i.e., something that supports attribute assignment).
        - Must implement a callable attribute named __unicode__ that returns a (text) string when called on instances.
        - No other arguments.

## Returns:
    type: The same class object passed in (cls), after being mutated:
        - If the PY3 flag is truthy: cls now has
            * __str__ bound to the same callable as cls.__unicode__ (so str(instance) returns the text)
            * __bytes__ set to a function that returns the UTF-8 encoding of str(instance)
        - If the PY3 flag is falsy: cls now has
            * __str__ set to a function that returns the UTF-8-encoded bytes produced by calling __unicode__ (this matches Python 2 str semantics)

Edge-case returns:
- The function always returns the input object reference (no None or alternative return values).

## Raises:
    AttributeError:
        - If the class does not define a __unicode__ attribute, the attempted access (cls.__unicode__) will raise AttributeError when the decorator executes.
    Exception (from __unicode__ call at runtime):
        - If __unicode__ exists but raises errors (TypeError, ValueError, etc.) when invoked at runtime, those exceptions will propagate to the caller of str() or bytes().

Note: The decorator itself does not explicitly raise these exceptions but they can arise from attribute access or underlying __unicode__ execution.

## Constraints:
Preconditions:
    - The caller should pass a class object (not None or a primitive). The class must allow attribute assignment (typical Python classes do).
    - The class must expose a callable __unicode__ method that returns a text string when invoked.

Postconditions:
    - The returned cls will have __str__ defined (either referencing __unicode__ or a wrapper around it).
    - Under PY3 truthy, cls will also have __bytes__ defined which encodes the result of __str__() with UTF-8.
    - No other attributes are modified.

## Side Effects:
    - Mutates the class object in-place by setting/replacing:
        * __str__ (always)
        * __bytes__ (only when PY3 is truthy)
    - No I/O, network activity, or external state updates beyond the class mutation.
    - No global variables are modified by this function.

## Control Flow:
flowchart TD
    Start --> Check_PY3
    Check_PY3{PY3 truthy?}
    Check_PY3 -- Yes --> Assign__str_to___unicode__
    Assign__str_to___unicode__ --> Assign__bytes_wrapper
    Assign__bytes_wrapper --> Return_cls
    Check_PY3 -- No --> Assign__str_to_encoded_wrapper
    Assign__str_to_encoded_wrapper --> Return_cls
    Return_cls --> End

(Interpretation: if PY3 is truthy the decorator wires __str__ to the class's __unicode__ and sets __bytes__ to a UTF-8 encoding wrapper; otherwise it sets __str__ to a wrapper that returns UTF-8-encoded bytes produced from __unicode__.)

## Examples (usage and behavior described in prose):
1) Typical application
    - Define a class that implements a method named __unicode__ which returns a text string for an instance.
    - Apply this decorator to the class (as a decorator or by assignment).
    - After decoration:
        * On Python 3 (PY3 truthy): calling str(instance) yields the text returned by __unicode__; calling bytes(instance) yields the UTF-8 encoded bytes of that text.
        * On Python 2 (PY3 falsy): calling str(instance) yields the UTF-8 encoded bytes of the text returned by __unicode__ (Python 2's str is a byte string).

2) Error handling scenario
    - If the class lacks __unicode__, applying the decorator at import time raises AttributeError. Catch or ensure presence of __unicode__ to avoid this.
    - If __unicode__ raises at runtime, that exception will propagate to callers of str() or bytes().

Implementation notes for re-implementation:
    - Do not attempt to call __unicode__ inside the decorator aside from obtaining the attribute; the decorator should only attach wrappers or references that will call __unicode__ at instance-call time.
    - The UTF-8 encoding used must be explicit and constant ("utf-8").
    - The decorator should return the class object after mutation so it can be used with the @decorator syntax.
    - Treat PY3 as a module-level boolean flag that determines which wiring to apply; do not assume its precise definition (it typically reflects whether running under Python 3).

## `sumy._compat.to_string` · *function*

## Summary:
Dispatches a value to the module's canonical text-or-bytes converter based on the runtime Python major-version flag, returning a text string on Python 3 and a bytes object on Python 2 compatibility mode.

## Description:
Known callers and typical contexts:
- Any code in the library that needs a single-call conversion which adapts to the library's compatibility mode (text-first on Python 3, bytes-first on Python 2). Typical callers include text-processing, tokenization, serialization, logging, and any helper that must produce the "native" string type for the active Python runtime.
- Callers normally invoke this function when they have an arbitrary object (text, bytes, or other) and want the library's canonical string representation without writing explicit PY2/PY3 branching themselves.

Why this logic is a separate helper:
- Encapsulates the simple but repeated policy decision "on PY3, produce text; otherwise produce bytes" in one place. This prevents duplication of the PY3 conditional across the codebase and centralizes the dependency on the module-level conversion helpers (to_unicode and to_bytes).
- Keeps callers simple — they do not need to know whether the library is running in text-first or bytes-first mode; they simply request "to_string" and receive the appropriate canonical representation.

## Args:
    object (Any):
        - The single positional parameter to convert.
        - Accepted inputs: text values (module's text type), bytes instances, or arbitrary Python objects.
        - No default value. The name shadows the built-in but reflects the original signature.
        - There are no interdependent parameters.

## Returns:
    Either the module's canonical text type or a bytes object, depending on the module-level PY3 flag:
    - If PY3 is truthy: returns the result of to_unicode(object). Typically this is the module text type (e.g., str on Python 3).
    - If PY3 is falsy: returns the result of to_bytes(object). Typically this is a bytes object (e.g., str/bytes on Python 2 compatibility mode).
    - All return values and error behavior are determined by the selected conversion function (to_unicode or to_bytes). The returned value therefore:
        * On PY3: will be text (unicode).
        * On non-PY3: will be bytes.

## Raises:
    - Any exception raised by to_unicode(object) when PY3 is truthy (for example, UnicodeDecodeError, or any exception propagated by instance conversion helpers).
    - Any exception raised by to_bytes(object) when PY3 is falsy (for example, TypeError from object conversion helpers).
    - This function itself does not introduce new exception types; it only propagates exceptions from the delegated conversion functions.

## Constraints:
    Preconditions:
        - The module-level boolean PY3 must be defined and correctly reflect whether the runtime compatibility mode expects text (True) or bytes (False).
        - The module must provide the functions to_unicode and to_bytes in the same namespace, and they must conform to their contracts:
            * to_unicode(object) returns the module text type for valid inputs.
            * to_bytes(object) returns a bytes object for valid inputs.
    Postconditions:
        - After a successful return, the caller receives a canonical representation appropriate for the active compatibility mode: text on PY3, bytes otherwise.
        - No global or external state is modified by this function.

## Side Effects:
    - The function performs no I/O, networking, or direct mutation of external state.
    - Indirect side effects may occur only if the delegated conversion functions (to_unicode / to_bytes) or the object's own conversion methods produce side effects; those are not caused by this dispatcher itself but may be observed by callers.

## Control Flow:
flowchart TD
    Start[Start: to_string(object)] --> CheckPY3{PY3 is truthy?}
    CheckPY3 -->|Yes| CallUnicode[to_unicode(object)]
    CallUnicode --> ReturnUnicode[Return result of to_unicode(object) or propagate its exception]
    CheckPY3 -->|No| CallBytes[to_bytes(object)]
    CallBytes --> ReturnBytes[Return result of to_bytes(object) or propagate its exception]

## Examples:
- On a Python-3 (PY3=True) runtime where to_unicode decodes/normalizes inputs:
    - Input: a text value "café"
      Outcome: returns the same or equivalent text value (module text type).
    - Input: bytes representing valid UTF-8 b'caf\xc3\xa9'
      Outcome: to_unicode decodes and returns "café".
    - Input: an arbitrary object obj
      Outcome: returns to_unicode(obj) (may produce a textual representation or raise if conversion fails).

- On a Python-2 compatibility mode runtime (PY3=False) where to_bytes encodes/normalizes inputs:
    - Input: a text value "café"
      Outcome: returns to_bytes("café") — typically the UTF-8 encoded bytes b'caf\xc3\xa9'.
    - Input: a bytes value b'caf\xc3\xa9'
      Outcome: returns the same bytes object unchanged.
    - Input: an arbitrary object obj
      Outcome: returns to_bytes(obj) (may produce a bytes representation or raise if conversion fails).

Usage note:
- Treat to_string as a thin, version-aware wrapper: if you specifically need bytes or specifically need text regardless of compatibility mode, call to_bytes or to_unicode directly. Use to_string when callers should follow the library's configured/native representation.

## `sumy._compat.to_bytes` · *function*

## Summary:
Converts its input into a bytes object: returns bytes unchanged, encodes text (module-level unicode) as UTF-8, and delegates all other conversions to the instance_to_bytes helper.

## Description:
Known callers within the codebase:
- sumy._compat.instance_to_bytes — calls this function as the final fallback when it needs to convert a repr(...) string of an object into bytes; that helper invokes to_bytes(repr(instance)).

Context / typical usage:
- Used anywhere the library needs a canonical bytes representation of a value that may already be bytes, may be a text string, or may be an arbitrary object. It is a small, well-scoped helper that enforces the policy: preserve bytes, encode text as UTF-8, and centralize complex instance-to-bytes logic in instance_to_bytes.

Why this logic is extracted:
- Keeps the simple, common conversion branches (already-bytes and text-to-bytes) compact and consistent across the codebase.
- Delegates complex, runtime-dependent instance conversion rules to instance_to_bytes so the decision boundary and priorities are centralized and easier to test and maintain.

## Args:
    object (Any): The value to convert to bytes.
        - If it is an instance of the module-level bytes type, it is returned unchanged.
        - If it is an instance of the module-level unicode type (a text type; typically aliased to str on Python 3), it is encoded with UTF-8.
        - Otherwise the value is forwarded to instance_to_bytes(object).
    Notes:
        - The name object shadows the built-in name but is used here as the single positional parameter.
        - The function relies on the module-level names unicode and instance_to_bytes being defined.

## Returns:
    bytes: A bytes object produced as follows:
        - If the input is already bytes, the same object is returned (identity preserved).
        - If the input is an instance of the module-level unicode type, returns the result of object.encode("utf-8").
        - Otherwise returns the value returned by instance_to_bytes(object). By design instance_to_bytes returns bytes for all successful paths.
    Edge cases:
        - If instance_to_bytes returns a non-bytes value (violating its contract), that value is returned unchanged — callers should rely on the documented contract that instance_to_bytes yields bytes.

## Raises:
    NameError: If the module-level name unicode is not defined when the isinstance check is executed.
    Any exception raised by instance_to_bytes: propagated unchanged (for example, TypeError if instance_to_bytes calls bytes(instance) and the instance's methods raise or return an invalid type).
    Any exception raised by object.encode("utf-8") if the object's type is not the expected text type — though in normal operation this path is only taken when isinstance(object, unicode) is True, so encode should be available.

## Constraints:
Preconditions:
    - The module must define:
        - unicode: a text type or alias (commonly str on Python 3, unicode on Python 2 compatibility layers).
        - instance_to_bytes: the fallback converter that accepts any object and returns bytes.
    - Callers should pass well-formed objects; magic method implementations on objects (e.g., __bytes__, __str__, __unicode__) may raise and those exceptions will propagate.

Postconditions:
    - On successful return, a bytes object is returned (per the documented contract and assuming instance_to_bytes adheres to its bytes-returning contract).
    - No module-level or global state is modified by this function.

## Side Effects:
    - None intrinsic: no I/O, no mutation of global variables, no network or filesystem access.
    - Side effects may occur indirectly if the object's own conversion methods perform side effects; those are not suppressed by this function.

## Control Flow:
flowchart TD
    Start[Start: to_bytes(object)] --> IsBytes{isinstance(object, bytes)?}
    IsBytes -->|Yes| ReturnBytes[Return object (bytes unchanged)]
    IsBytes -->|No| IsUnicode{isinstance(object, unicode)?}
    IsUnicode -->|Yes| Encode[Return object.encode("utf-8")]
    IsUnicode -->|No| Fallback[Return instance_to_bytes(object)]

## Examples:
- Input already bytes:
    - Input: b"utf8-bytes"  
      Result: b"utf8-bytes" (same object returned)

- Input is text (module-level unicode):
    - Input: "café" (if unicode is aliased to str)  
      Result: b"caf\xc3\xa9" (UTF-8 encoded bytes)

- Input is an arbitrary object (fallback path):
    - Input: an instance of a custom class without bytes/text protocol methods  
      Result: instance_to_bytes(instance) is invoked and its bytes result is returned. Wrap calls in try/except if the instance may raise in its magic methods:
        try:
            b = to_bytes(some_obj)
        except Exception as e:
            # handle conversion error (TypeError, ValueError, or custom exception from object's methods)
            ...

Usage note:
- Because the function relies on a module-level unicode alias and on instance_to_bytes, ensure those names are present in the module before calling to_bytes from external code.

## `sumy._compat.to_unicode` · *function*

## Summary:
Ensure a value is returned as the module's text type: return text unchanged, decode bytes using UTF-8, or delegate conversion of other objects to the instance conversion helper.

## Description:
Known callers within the codebase and typical contexts:
    - instance_to_unicode: may call this function as a fallback when it needs to convert repr(instance) into a text string; this creates a mutual delegation where to_unicode delegates complex instances to instance_to_unicode and instance_to_unicode may call to_unicode on reprs.
    - Other modules (text processing, tokenization, logging) typically call this function when they need a guaranteed text (unicode) string from inputs that may be already-text, raw bytes, or arbitrary Python objects.

Why this is a separate helper:
    - Centralizes the simplest and most common compatibility logic: "if already text -> return; if bytes -> decode; otherwise -> handle object-specific conversion".
    - Keeps bytes/str branching concise and readable while delegating the more nuanced instance-handling policies (which are Python-version-aware) to instance_to_unicode.
    - Provides a single place callers can use to obtain a normalized text value without duplicating UTF-8 decoding or isinstance checks.

## Args:
    object (any):
        - The value to convert to the module's canonical text type (named `unicode` in this module).
        - Allowed/expected inputs:
            * A text value of the module text type (module `unicode`) — returned unchanged.
            * A bytes value (`bytes`) — decoded as UTF-8 and returned as text.
            * Any other Python object — passed to instance_to_unicode(object) for conversion.
        - No other interdependencies between parameters.

## Returns:
    unicode (module text type):
        - If `object` is already the module text type: returns the same object unchanged.
        - If `object` is a bytes instance: returns object.decode("utf-8").
        - Otherwise: returns the result of instance_to_unicode(object), which itself returns the module text type (or propagates errors).
        - Edge cases:
            * If bytes cannot be decoded as UTF-8, a UnicodeDecodeError is propagated.
            * If instance_to_unicode raises (for example, due to an object's conversion method raising), that exception is propagated.

## Raises:
    - UnicodeDecodeError: when `object` is bytes and decoding with UTF-8 fails.
    - Any exception raised by instance_to_unicode(object), including exceptions raised by user-defined conversion special methods on the object (TypeError, ValueError, arbitrary exceptions).
    - No exceptions are raised by this function purely as a result of internal checks; all raised exceptions originate from decoding or delegated conversion.

## Constraints:
    Preconditions:
        - The module-level names `unicode`, `bytes`, and `instance_to_unicode` must exist and behave as expected in the module namespace.
        - Callers should expect that bytes data is UTF-8 encoded; non-UTF-8 bytes will raise UnicodeDecodeError.
    Postconditions:
        - On successful return, the caller receives a value of the module's canonical text type (named `unicode`).
        - No global state or module-level variables are modified by this function.

## Side Effects:
    - The function performs no direct I/O, network access, or modifications of external state.
    - Side effects can occur indirectly if:
        * Decoding triggers codec hooks (rare) or
        * instance_to_unicode calls user-defined methods on objects that have side effects; those side effects are not caused by this function itself but by the object's conversion methods.

## Control Flow:
flowchart TD
    A[Start: to_unicode(object)] --> B{isinstance(object, unicode)?}
    B -->|Yes| C[Return object unchanged]
    B -->|No| D{isinstance(object, bytes)?}
    D -->|Yes| E[Return object.decode("utf-8") or raise UnicodeDecodeError]
    D -->|No| F[Return instance_to_unicode(object) or propagate its exception]

## Examples:
- Happy path: text value already:
    text = to_unicode(u"café")
    # returns the same text value "café" (module text type)

- Bytes decoding:
    text = to_unicode(b'caf\xc3\xa9')  # b'caf\xc3\xa9' is UTF-8 for "café"
    # returns "café"

- Arbitrary object:
    text = to_unicode(123)
    # returns instance_to_unicode(123) which typically yields "123" as text

- Error handling (bytes decoding may fail):
    try:
        text = to_unicode(b'\xff')  # invalid UTF-8
    except UnicodeDecodeError:
        # handle decoding failure, e.g., log and use fallback
        text = "<invalid-bytes>"

- Handling conversion errors from instance conversion:
    try:
        text = to_unicode(maybe_problematic_object)
    except Exception as exc:
        # instance_to_unicode or the object's __str__/__bytes__ hook raised
        text = "<unrepresentable>"

## `sumy._compat.instance_to_bytes` · *function*

## Summary:
Convert an arbitrary Python object instance into a bytes object, using the instance's available byte/string protocol methods and falling back to a bytes-encoded repr when necessary.

## Description:
This helper centralizes the rules for converting an object instance to bytes while handling differences between Python 2 and Python 3 runtime conventions.

Known callers within the codebase:
- sumy._compat.to_bytes — calls instance_to_bytes(object) as the fallback conversion when the object is neither bytes nor the module's unicode type. This occurs inside to_bytes as part of a general-purpose conversion pipeline for arbitrary objects.

Why this logic is extracted:
- The conversion rules depend on runtime (Python 2 vs Python 3) and on the presence of several possible instance protocols (__bytes__, __str__, __unicode__). Extracting this logic keeps the conversion strategy in one place so to_bytes and other potential callers can rely on a consistent, well-tested policy for turning objects into bytes.

## Args:
    instance (Any): The object to convert to bytes. No specific type is required; the function inspects the instance for protocol methods (__bytes__, __str__, __unicode__) and uses repr(...) as a last resort.

## Returns:
    bytes: A bytes object produced by one of the following code paths (in priority order per branch):
    - If running under a module-level PY3 truthy flag and the instance implements __bytes__, returns bytes(instance).
    - If under PY3 and the instance lacks __bytes__ but has __str__, returns unicode(instance).encode("utf-8").
    - If not PY3 and the instance has __str__, returns bytes(instance).
    - If not PY3 and the instance has __unicode__, returns unicode(instance).encode("utf-8").
    - Otherwise, returns to_bytes(repr(instance)) — i.e., the repr string of the instance passed into the module-level to_bytes helper, which will itself ensure a bytes result.

All return paths guarantee the result is a bytes object (assuming the module-level helpers and aliases are defined and behave as expected).

## Raises:
The function does not explicitly raise exceptions; however, callers must be aware that built-in conversions invoked here can raise:
    - TypeError: If bytes(instance) is called but the instance's __bytes__ / __str__ implementation returns a value that cannot be converted to bytes by the built-in bytes() function.
    - NameError: If the module-level name unicode is not defined (this function uses unicode(...) in some branches).
    - Any exception propagated from instance-provided methods: if an instance's __bytes__, __str__, or __unicode__ method raises an exception, that exception will propagate through instance_to_bytes unchanged.

## Constraints:
Preconditions:
    - The module must define (or import) the names referenced here:
        - PY3: a module-level boolean-like flag that selects the Python-3 code path when truthy.
        - unicode: a type or callable used to obtain a text string representation in branches that call unicode(instance). (Typical _compat patterns alias unicode to str on Python 3 and to built-in unicode on Python 2.)
        - to_bytes: a module-level helper used as the final fallback for converting repr(instance) to bytes.
    - The instance may implement any of the inspected methods; none are required.

Postconditions:
    - On successful return, the value is a bytes object (subject to the behaviors/constraints of the invoked helpers and methods).
    - No global state is mutated by this function.

## Side Effects:
    - None intrinsic to this function: it performs no I/O, does not mutate global state, and makes no external network or file calls.
    - Side effects can occur indirectly if the instance's __bytes__, __str__, or __unicode__ methods perform side effects; those will occur during conversion and are not suppressed.

## Control Flow:
flowchart TD
    A[Start: instance_to_bytes(instance)] --> B{PY3 truthy?}
    B -->|Yes| C{has __bytes__?}
    C -->|Yes| D[return bytes(instance)]
    C -->|No| E{has __str__?}
    E -->|Yes| F[return unicode(instance).encode("utf-8")]
    E -->|No| G[Fallback -> to_bytes(repr(instance))]
    B -->|No| H{has __str__?}
    H -->|Yes| I[return bytes(instance)]
    H -->|No| J{has __unicode__?}
    J -->|Yes| K[return unicode(instance).encode("utf-8")]
    J -->|No| G

## Examples:
- Converting an object that already provides __bytes__ (Python 3):
    - If instance.__bytes__ exists and returns a bytes object, the function returns bytes(instance) unchanged.

- Converting a text-representable object on Python 3:
    - If the object lacks __bytes__ but implements __str__, the function calls unicode(instance).encode("utf-8") to obtain UTF-8-encoded bytes.

- Fallback for unusual objects:
    - If neither bytes nor text protocols are available, the function returns to_bytes(repr(instance)) — i.e., the UTF-8-encoded repr string of the object as computed by the module's to_bytes helper.

Usage note (error handling):
- To safely call instance_to_bytes on untrusted objects that may raise in their magic methods, wrap the call in try/except and handle TypeError and other exceptions raised by instance implementations.

## `sumy._compat.instance_to_unicode` · *function*

## Summary:
Convert an arbitrary Python object into a text (unicode) string using instance-specific hooks where available and falling back to a safe representation.

## Description:
This function normalizes an instance to the module's text type (named `unicode` in this module) by checking and using the instance's text/bytes conversion special methods in a Python-version-aware order, then falling back to `to_unicode(repr(instance))` if no direct conversion is found.

Known callers within the codebase:
    - sumy._compat.to_unicode: used when `to_unicode` receives an object that is neither the `unicode` type nor `bytes`; `to_unicode` delegates to this function to obtain a text representation.
    - Other modules may call this function indirectly via `to_unicode` when they need a guaranteed text string for logging, tokenization, or other text-processing steps.

Why this is extracted into its own function:
    - Centralizes cross-Python-version logic for converting arbitrary instances to the module's canonical text type.
    - Encapsulates the decision order (use __str__/__bytes__/__unicode__ appropriately per Python major version) so callers can simply request a unicode representation without duplicating compatibility checks.
    - Keeps `to_unicode` concise by separating the "instance-handling" responsibility from the direct-type branches for bytes/unicode.

## Args:
    instance (any): The object to convert to the module's text type.
        - No type restrictions; can be any Python object.
        - The function tests for presence of special methods on the object:
            * On Python 3 path: "__str__" then "__bytes__"
            * On Python 2 path: "__unicode__" then "__str__"
        - If none of the above are present, the function will use repr(instance) and pass that string through `to_unicode`.

## Returns:
    unicode (module text type): A text (unicode) string representation of `instance`.
    Possible return values/paths:
        - If running under the Python-3 branch (when `PY3` is true):
            * If `instance` has __str__: returns unicode(instance)
            * Else if it has __bytes__: returns bytes(instance).decode('utf-8')
        - If running under the Python-2 branch (when `PY3` is false):
            * If `instance` has __unicode__: returns unicode(instance)
            * Else if it has __str__: returns bytes(instance).decode('utf-8')
        - If none of the above apply: returns the result of to_unicode(repr(instance))
    Notes:
        - "unicode" is the module's canonical text type name (as used in this file); callers can expect a text-type result appropriate for the runtime.

## Raises:
    - The function does not explicitly raise its own exceptions, but it propagates exceptions raised by the called conversions:
        * Any exception raised by unicode(instance) (e.g., if the instance's special method raises).
        * Any exception raised by bytes(instance) or its .decode('utf-8') call (e.g., TypeError from bytes(...) or UnicodeDecodeError during decode).
        * Any exception raised by repr(instance) or by the downstream to_unicode call invoked on the repr.
    - No additional exception translation is performed; callers should catch relevant exceptions if required.

## Constraints:
    Preconditions:
        - The module-level names `PY3`, `unicode`, `bytes`, and `to_unicode` must be defined in the module namespace (this function assumes they exist).
        - The instance's special methods (if present) must behave according to the runtime's expectations (i.e., __bytes__ should return a bytes object).
    Postconditions:
        - On successful return, the result is the module's text type representing the instance; callers can use it where text strings are expected.
        - No global state or module-level variables are modified by this function.

## Side Effects:
    - None visible: the function performs no I/O, does not mutate external/global state, and does not call external services.
    - Side effects are only those caused by calling the instance's own conversion methods (which could be user-defined and may have side effects).

## Control Flow:
flowchart TD
    A[Start: instance_to_unicode(instance)] --> B{PY3?}
    B -->|Yes| C{has __str__?}
    B -->|Yes and no __str__| D{has __bytes__?}
    B -->|No| E{has __unicode__?}
    B -->|No and no __unicode__| F{has __str__?}
    C -->|Yes| G[Return unicode(instance)]
    C -->|No| D
    D -->|Yes| H[Return bytes(instance).decode('utf-8')]
    D -->|No| I[Return to_unicode(repr(instance))]
    E -->|Yes| J[Return unicode(instance)]
    E -->|No| F
    F -->|Yes| H
    F -->|No| I

## Examples:
1) Object with a readable text representation via __str__:
    class Person:
        def __str__(self):
            return "Alice"
    # instance_to_unicode(Person()) -> module text "Alice"
    # Typical use: converting objects to text for tokenization or logging.

2) Object exposing a raw bytes representation via __bytes__ (Python 3 path):
    class RawBytes:
        def __bytes__(self):
            return b'\xc3\xa9'  # UTF-8 for 'é'
    # instance_to_unicode(RawBytes()) -> "é"
    # decode uses UTF-8 per implementation.

3) Fallback to repr if no conversion hooks:
    class Marker: pass
    # instance_to_unicode(Marker()) -> to_unicode(repr(Marker()))
    # This ensures a stable, printable text result even for unfamiliar objects.

4) Error handling pattern:
    try:
        text = instance_to_unicode(maybe_broken_object)
    except (TypeError, UnicodeDecodeError, Exception) as exc:
        # Handle or log the failure of instance-specific conversion
        fallback = "<unrepresentable instance>"
        text = fallback
    # Use `text` safely after handling

