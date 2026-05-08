# `utils.py`

## `pysnooper.utils._check_methods` · *function*

## Summary:
Checks whether a class's method names are present (and not explicitly disabled) somewhere in its method resolution order; returns True when all are present and usable, otherwise returns NotImplemented.

## Description:
This helper examines the class object C's __mro__ (method resolution order) and, for each method name provided, verifies that some class in the MRO defines that name in its class dictionary and that the class dictionary entry is not the sentinel value None. The function is suited for use by higher-level code that needs a quick, static check that a class (or one of its base classes) supplies particular named attributes/methods and that they are not intentionally disabled.

Known callers within the available snapshot:
- No direct callers were discovered in the provided code excerpt. Typical callers (in similar codebases) are factory functions, metaclass helpers, or compatibility utilities that must decide whether a class implements certain optional methods before enabling behavior (for example, conditional registration of adapters or enabling protocol-specific code paths).

Why this is a separate function:
- Encapsulates a focused, repeated check: scanning a class's MRO to determine presence/absence of named attributes while applying a specific "None means disabled" policy.
- Keeps higher-level logic free from low-level __mro__/__dict__ traversal details and makes the presence-check policy explicit and testable in one place.

## Args:
    C (type): A class object (or any object exposing a __mro__ attribute) whose MRO will be searched. This must be a class-like object with a tuple attribute named __mro__.
    *methods (str): One or more attribute names (typically method names) to check for presence. Each should be a hashable object usable as a dict key (commonly a str).

Notes on argument interdependencies:
- C.__mro__ is relied on directly; passing an object without __mro__ will raise an AttributeError.
- Method names are checked by membership in each class's __dict__ (exact key equality). They are not looked up via getattr or via dynamic attribute resolution.

## Returns:
    True if, for every provided method name:
        - there exists some class B in C.__mro__ such that method is a key in B.__dict__, and
        - the corresponding value B.__dict__[method] is not None.
    NotImplemented if any of these is true for at least one method name:
        - no class in C.__mro__ has the method name in its __dict__;
        - the first class in the MRO that contains the method name has its __dict__ value equal to None (interpreted as intentionally disabled).

Edge cases:
- If no method names are supplied, the function returns True (vacuous truth).
- The function returns the built-in object NotImplemented (not a boolean) to signal "not supported" for the requested set of methods.

## Raises:
    AttributeError: If C does not have a __mro__ attribute (e.g., a non-class object passed).
    TypeError: If an unhashable object is provided as a method name (because dict membership requires hashability).

## Constraints:
Preconditions:
    - Caller should pass a class-like object that exposes __mro__ (a tuple of classes).
    - Each method identifier should be an appropriate dict key (normally a str).

Postconditions:
    - No mutation of the inspected classes or their dictionaries occurs.
    - The return value is either True or the special singleton NotImplemented.

## Side Effects:
    - None. The function performs only read-only inspection of class __dict__ entries and returns a value. It does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start --> GetMRO["mro = C.__mro__"]
    GetMRO --> MethodsLoop{"for method in methods"}
    MethodsLoop --> |no methods| ReturnTrue1["return True"]
    MethodsLoop --> ForEachMethod["for B in mro"]
    ForEachMethod --> IfInDict{"if method in B.__dict__"}
    IfInDict --> IfValueNone{"if B.__dict__[method] is None"}
    IfValueNone --> ReturnNotImplemented1["return NotImplemented"]
    IfValueNone --> BreakToNextMethod["break (next method)"]
    IfInDict --> |not in dict| ContinueNextB["continue to next B in mro"]
    ContinueNextB --> ForEachMethod
    BreakToNextMethod --> MethodsLoop
    ForEachMethod --> ElseNoMatch["(else of for B): no class had method"]
    ElseNoMatch --> ReturnNotImplemented2["return NotImplemented"]
    MethodsLoop --> AfterAll["(after all methods checked)"]
    AfterAll --> ReturnTrue2["return True"]

## Examples:
- Typical positive case (descriptive): Given a class C whose MRO includes a base class that defines 'serialize' in its __dict__ with a callable value, calling this checker with that class and 'serialize' yields True, indicating the method is present and enabled.

- Typical negative cases (descriptive):
    - If no class in C.__mro__ defines 'deserialize' as a key in its __dict__, the function yields NotImplemented.
    - If some class in the MRO defines 'close' but sets that class __dict__ entry to None to signal "disabled", the function yields NotImplemented.

Usage guidance:
- Use this function when you need a conservative, static check that a class or one of its base classes declares specific names and that they are not explicitly disabled via a None sentinel.
- Do not use it when dynamic attribute resolution (e.g., __getattr__, descriptors installed on instances, or runtime monkey-patching) should count as providing the method; this function only inspects class __dict__ entries along the MRO.

## `pysnooper.utils.WritableStream` · *class*

## Summary:
An abstract stream interface that declares a single required operation, write(s), and enables structural subtyping for objects that provide that operation.

## Description:
WritableStream exists to define a minimal, language-level contract for writable sinks: any object that exposes a write method can be treated as a WritableStream. Typical scenarios for instantiation of concrete implementors include adapters that wrap terminal output, file-like sinks, in-memory buffers, or logging recipients. The abstraction separates the concept of "something that accepts written text/bytes" from any particular implementation (console, file, socket, etc.).

This class:
- Declares the required method write(self, s) as abstract; concrete implementors must provide it.
- Implements a custom subclass hook that delegates to a helper (_check_methods) to allow objects that only implement write to be recognized as virtual subclasses (structural/duck typing), even if they do not explicitly inherit from WritableStream.

Responsibility boundary:
- WritableStream's only responsibility is to declare the write operation contract and support structural subtyping. It does not prescribe buffering, encoding, thread-safety, newline handling, or closing semantics — those are responsibilities of concrete implementations.

## State:
Attributes:
- The base class defines no instance attributes. Concrete implementations will introduce state as needed (e.g., file descriptor, buffer, encoding). Nothing in WritableStream enforces or prescribes those attributes.

__init__ parameters:
- WritableStream provides no initializer in this fragment. Concrete implementors decide constructor parameters and invariants.

Method parameter(s) (from the abstract method):
- s: the single argument passed to write(self, s).
  - Type: not enforced by WritableStream itself (no type annotations in the base class).
  - Typical/expected usage: implementations commonly accept text (string) or binary data depending on the specific sink; callers should consult the concrete implementation for exact accepted types and encoding expectations.

Class invariants:
- Any concrete, instantiable subclass must provide a callable attribute named write that accepts one positional argument (besides self).
- If a concrete class does not implement write, it remains abstract and cannot be instantiated due to the abstractmethod declaration.

## Lifecycle:
Creation:
- WritableStream is abstract and cannot be instantiated directly because it declares an abstract write method.
- To obtain an instance, define a concrete type that provides a write method (and any other necessary methods/state), then instantiate that concrete type.
- The subclass hook (__subclasshook__) defers to _check_methods(C, 'write') when comparing types; therefore, an otherwise unrelated type that exposes a write attribute may be recognized as a virtual subclass.

Usage:
- Typical usage pattern:
  1. Acquire or create a concrete instance that implements write.
  2. Call instance.write(s) repeatedly to send data to the sink.
  3. Follow the concrete implementation's contract for flushing or closing if required (WritableStream itself does not provide flush/close semantics).

Destruction / cleanup:
- WritableStream provides no cleanup methods. Concrete implementations should expose and document cleanup APIs (for example, flush or close) if resource management is required. Users should call those concrete cleanup methods when necessary.

## Method Map:
flowchart TD
    A[Client code] -->|calls| B[Concrete write implementation]
    B -->|performed by| C[Concrete stream object state]
    Note[WritableStream] --- B
    Note2[__subclasshook__ delegates to _check_methods] --- WritableStream

(Interpretation: client code calls the concrete object's write method; the base WritableStream defines the abstract contract and __subclasshook__ allows structural recognition of objects with write.)

## Raises:
- Instantiation of WritableStream itself will raise a TypeError via the abstract base class mechanism if write is not implemented by the concrete type being instantiated. This is the standard behavior of abstractmethod declarations.
- The base class code does not explicitly raise other exceptions; concrete write implementations may raise exceptions based on their own constraints (I/O errors, type errors for unsupported input types, etc.).

## Example:
- Create a concrete type that provides a write method which accepts one argument and performs the sink-specific action (for example, append the string to an internal buffer or forward it to a file descriptor).
- Instantiate that concrete type.
- Use the instance by repeatedly invoking write(s) with the data to be written.
- When finished, perform any cleanup required by the concrete type (for example, call a close or flush operation if implemented).

Notes and implementation tips:
- Do not assume the base class enforces text encoding or newline conversion; handle encoding at the concrete-implementation boundary.
- Rely on the subclass hook to allow duck-typed objects (objects that only implement write) to be recognized as WritableStream-compatible in isinstance or issubclass checks, provided the codebase's _check_methods identifies the method correctly.
- Document the concrete type's accepted types for s (text vs binary) and any thread-safety or buffering guarantees.

### `pysnooper.utils.WritableStream.write` · *method*

## Summary:
Abstract contract for emitting a payload to a stream-like sink; concrete subclasses must implement this method to perform the actual emission.

## Description:
This method is declared abstract (annotated with abc.abstractmethod) and contains no implementation in the base class. The class implementation also provides a __subclasshook__ that recognizes objects exposing a write method as conforming to the WritableStream ABC; therefore, concrete subclasses or duck-typed objects must provide a compatible write method to be treated as writable by this ABC.

Why this is a separate method:
- It isolates the sink-specific I/O behavior so tracing/logging callers can write uniformly to different backends (files, buffers, sockets, adapters) without embedding backend-specific logic in the caller.
- Implementers provide the concrete emission, buffering, encoding, and error handling policies here.

Known/expected callers (guidance, not enforced by the base class):
- Higher-level tracing or logging components in the codebase are expected to call write repeatedly to emit trace lines or fragments. Because the base class has no implementation, callers treat write as an abstract sink operation.

## Args:
    s (any): The single positional argument passed by callers. The base class does not constrain the type.
    Recommendation: Implementations SHOULD accept native text (str / string_types) as the primary payload since tracing data is textual. If supporting bytes, implementations MUST document how bytes are handled (e.g., decoding).

## Returns:
    None or any:
    - The abstract base does not require or inspect a return value.
    - Recommendation: Implementations SHOULD either return None or an integer count of characters/bytes written, following common file-like conventions. Do not rely on callers to use the return value.

## Raises:
    - The base method does not raise any specific exceptions because it has no implementation.
    - Implementations MAY raise:
        - TypeError if an unsupported type for s is explicitly rejected.
        - OSError or subclass (e.g., IOError) for low-level I/O failures.
    - Implementations SHOULD document which exceptions they raise so callers can handle them.

## State Changes:
    Attributes READ:
        - None mandated by the abstract method. Concrete implementations will read whatever internal attributes they need (for example, a wrapped file-like object, internal buffer, or encoding attribute).
    Attributes WRITTEN:
        - None mandated. Concrete implementations may update internal buffers, counters, or metadata attributes (for example, last_write_time or bytes_written).

## Constraints:
    Preconditions:
        - The WritableStream instance must be properly initialized by its concrete subclass prior to calling write (for example, any wrapped stream or buffer must be open/available).
        - Callers should pass the expected payload type documented by the concrete implementation (commonly text strings).
    Postconditions:
        - The base class makes no guarantees. Implementations SHOULD ensure that after a successful call the payload has been emitted to their sink or enqueued for emission according to their buffering semantics.

## Side Effects:
    - The abstract method itself has no side effects. Concrete implementations will typically perform I/O (writing to files, buffers, sockets, etc.) and may block, trigger network activity, or modify external resources.
    - Implementations SHOULD avoid performing long-running or unrelated computation inside write to keep callers (e.g., tracers) responsive.

## Implementation guidance (for reimplementers):
    - Mark the method with @abc.abstractmethod (as in the base class) when declaring an abstract base.
    - When implementing:
        - Accept and document the expected type for s.
        - Decide and document buffering/flush policy.
        - Decide whether the method is thread-safe and document synchronization if required.
        - Prefer returning None unless callers in your context expect a numeric write count.
        - Allow low-level I/O exceptions to propagate unless you intentionally convert them to other exception types.

### `pysnooper.utils.WritableStream.__subclasshook__` · *method*

## Summary:
When Python's abstract-subclass machinery asks whether a candidate class should be treated as a WritableStream, perform a structural (duck-typed) check for a usable 'write' attribute and return that decision or defer.

## Description:
This classmethod is invoked by Python's abstract base class (ABC) machinery (for example, via issubclass(candidate, WritableStream) or indirectly via isinstance checks) to implement a virtual subclass check for the WritableStream protocol. In practice the method runs during runtime type checks when code asks whether a class should be considered a WritableStream without explicit inheritance.

Behavioral summary:
- If the class object being queried for virtual-subclass-ness (the class bound to cls when this method is executed) is exactly the WritableStream ABC, this method uses the helper _check_methods to determine whether the candidate class C (the possible subclass) supplies a usable 'write' name in its MRO; the result returned is whichever _check_methods returns (True or NotImplemented).
- If cls is any other class (for example, a subclass of WritableStream), the method returns NotImplemented immediately to defer to other subclasshook logic or normal inheritance checks.

Why separate:
- The logic encapsulates a small, explicit structural check ("has a non-None 'write' declared in the MRO") that is reused only for the WritableStream ABC. Keeping it as its own method integrates with the ABC protocol and keeps subclass-decision semantics isolated and testable.

Known callers and context:
- ABCMeta.__subclasscheck__ / issubclass(candidate, WritableStream): called during virtual-subclass checks.
- isinstance(obj, WritableStream) may cause this path to be consulted via type(obj) checks in the ABC machinery.
- It is not intended to be called directly in normal application code; it participates in Python's type-check lifecycle when determining virtual subclass relationships.

## Args:
    cls (type): The class on which __subclasshook__ is invoked. In normal usage this is the WritableStream ABC or one of its subclasses.
    C (type): The candidate class being tested for virtual subclass-ness. Must be a class-like object exposing a __mro__ attribute (a tuple of classes).

## Returns:
    bool or NotImplemented:
        - True: when cls is exactly WritableStream and _check_methods(C, 'write') returns True (i.e., some class in C.__mro__ has 'write' in its __dict__ and the entry is not None).
        - NotImplemented: when cls is not exactly WritableStream (this method defers), or when cls is WritableStream but _check_methods(C, 'write') yields NotImplemented (meaning the candidate does not satisfy the conservative structural check).
    Notes:
        - The function returns the literal NotImplemented singleton (not False) to signal "I don't make a definitive subclass decision" in the ABC protocol.

## Raises:
    AttributeError: If C does not expose a __mro__ attribute, the helper _check_methods (which directly reads C.__mro__) will raise AttributeError; this propagates out of __subclasshook__.
    TypeError: Extremely unlikely from this method itself because it calls _check_methods with a string literal 'write' (hashable). However, if the underlying _check_methods implementation changed to treat inputs differently, a TypeError could propagate. Current implementation: no TypeError is raised here.

## State Changes:
Attributes READ:
    - None of self.<attr> fields are read or mutated. The method compares the cls object identity to the global WritableStream name and calls _check_methods; it does not access or mutate instance/class attributes of cls.
Attributes WRITTEN:
    - None. The method performs no mutations on cls, C, or other objects.

## Constraints:
Preconditions:
    - cls is expected to be a class object; the method is defined as a classmethod and is invoked by the ABC machinery with a class as the first argument.
    - C must be a class-like object with a __mro__ attribute (tuple). If not, AttributeError will be raised by _check_methods.
Postconditions:
    - No side-effecting changes are made to cls, C, or the classes in C.__mro__.
    - The return value is either True or the NotImplemented singleton; callers (ABC machinery) will interpret NotImplemented as "defer to other checks."

## Side Effects:
    - None. The method performs only read-only inspection via the helper _check_methods and returns a decision. It does not perform I/O, logging, or mutate external state.

## `pysnooper.utils.shitcode` · *function*

## Summary:
Produce an ASCII/8-bit-safe string by replacing any character whose Unicode code point is not in the range 1..255 with a question mark.

## Description:
This helper iterates the characters of the input and preserves characters whose Unicode code point (ord) lies strictly between 0 and 256 (i.e., 1..255). Any character with code point 0 (NUL) or >= 256 is replaced with '?' in the output. The function is a small, focused sanitizer intended to convert potentially wide/unprintable Unicode characters into a conservative placeholder so downstream text-handling or logging code can assume an 8-bit-safe representation.

Known callers within the codebase:
- No direct callers were found in the scanned module-level graph for this repository. It is a small utility likely intended to be used by tracing/logging functions when building human-readable output.

Why this logic is extracted into its own function:
- Responsibility boundary: centralizes the one-step normalization rule (map out-of-range characters to '?') so callers do not duplicate the ord-checking, and so tests and any future changes (different replacement character or range) can be made in one place.
- Keeps higher-level formatting/printing code focused on layout rather than character-level sanitization.

## Args:
    s (str or iterable of single-character strings): The input sequence to sanitize.
        - Expected to be a text string (Python str) composed of characters, where each element yielded when iterating is a one-character string.
        - Not intended for bytes objects or iterables of non-character values; ord(...) is called on each element.
        - No default value.

Interdependencies:
    - The function assumes each iterated item can be passed to ord(). If items are not one-character strings, ord will raise TypeError.

## Returns:
    str: A new string with the same number of elements as the input iteration. For each input character:
        - If 0 < ord(character) < 256 then the original character is copied into the output.
        - Otherwise (ord == 0 or ord >= 256) a question mark character '?' is placed in the corresponding output position.

Edge-case returns:
    - If s is an empty iterable or empty string, returns ''.
    - The returned string length equals the number of iterated items from s.

## Raises:
    TypeError:
        - If s is not iterable, Python will raise a TypeError when attempting iteration.
        - If an iterated element is not a one-character string (for example an int, a multi-character string, or a bytes element yielded when iterating a bytes object), ord(element) will raise TypeError.
    Any TypeError originates from Python built-ins (iteration or ord); the function does not raise custom exceptions.

## Constraints:
Preconditions:
    - Caller should pass an iterable of one-character strings (commonly a str).
    - The function does not validate types beyond relying on ord; callers should ensure the input is appropriate if they wish to avoid TypeError.

Postconditions:
    - Returned string length equals the number of items iterated over from s.
    - Every character in the return is either the original character (when its code point is in 1..255) or '?'.
    - No mutation of the input occurs.

## Side Effects:
    - None. The function performs no I/O, writes no globals, makes no network calls, and does not modify external state.

## Control Flow:
flowchart TD
    Start --> Iterate[Begin iterating over input s]
    Iterate --> ForEach{For each character c in s}
    ForEach --> Compute[Compute cp = ord(c)]
    Compute --> Check{Is 0 < cp < 256 ?}
    Check -->|Yes| Keep[Append original c to buffer]
    Check -->|No| Replace[Append '?' to buffer]
    Keep --> Next{More characters?}
    Replace --> Next
    Next -->|Yes| ForEach
    Next -->|No| Join[Join buffer into result string]
    Join --> Return[Return result string]
    Return --> End

## Examples:
    - Basic ASCII preserved:
        Input: "Hello, World!"
        Output: "Hello, World!"  (all characters have ord in 1..255)

    - Non-8-bit character replaced:
        Input: "aΩb"  (Ω has ord 937)
        Output: "a?b"

    - Latin-1 character preserved:
        Input: "café"  (é has ord 233)
        Output: "café"

    - NUL character replaced:
        Input: "ab\x00cd"
        Output: "ab?cd"

    - Empty input:
        Input: ""
        Output: ""

    - Type error example (caller should catch if input might be bytes or mixed types):
        Passing bytes: b"hi" will iterate integers 104,105, and ord(integer) will raise TypeError.
        A safe pattern if input may be bytes:
            - Decode bytes to str first (with an appropriate encoding/fallback), then call this function.

## `pysnooper.utils.get_repr_function` · *function*

## Summary:
Selects and appropriate representation function for a value by scanning an ordered sequence of (condition, action) rules; returns the first matching action or Python's built-in repr if none match.

## Description:
Iterates the ordered iterable custom_repr of (condition, action) pairs. For each pair:
- If condition is a type object (isinstance(condition, type) is True), it is treated as a shorthand for an isinstance check by converting it to a bound lambda.
- Otherwise condition is treated as a callable and is invoked with the item.

The function returns the action associated with the first rule whose condition(item) evaluates truthy. If no rule matches, it returns the built-in repr.

Typical usage context:
- Used by higher-level code that needs to choose how to stringify or format a value based on its type or a predicate. This function only selects and returns the action callable (it does not invoke it).

Reason for extraction:
- Encapsulates the "first-match-wins" selection policy and the convenience of allowing type objects as conditions (converted to isinstance checks) in one reusable place.

## Args:
    item (Any): The value to match against the rules.
    custom_repr (Iterable[tuple[condition, action]]): Ordered iterable of 2-tuples where:
        - condition: either
            * a type object (e.g., int, str, MyClass) — treated as isinstance check, or
            * a callable accepting one argument (the item) and returning a truthy/falsey result.
        - action: the value to return when the condition matches; typically a callable that produces a string representation for the item.
    Interdependencies:
        - If condition is a type, it is converted internally to a callable using a default-argument lambda to bind the specific type value.

## Returns:
    callable: The action from the first matching rule. If no rule matches, returns Python's built-in repr function.
    Notes:
        - The function returns the action object itself and does not call it.
        - Returned actions may be any Python object; callers are expected to know how to use them.

## Raises:
    TypeError:
        - If custom_repr itself is not iterable, attempting to iterate it will raise a TypeError which propagates.
        - If an element of custom_repr is not an iterable (e.g., an int), the unpacking "for condition, action in custom_repr" will raise a TypeError indicating a non-iterable element.
        - If a condition that is not a type is not callable, calling condition(item) will raise a TypeError which propagates.
    ValueError:
        - If an element of custom_repr is iterable but does not contain exactly two items (e.g., a 1-tuple or a 3-tuple), the unpacking for condition, action will raise a ValueError which propagates.
    Any exception raised by evaluating a condition callable will propagate to the caller.

## Constraints:
    Preconditions:
        - custom_repr must be an iterable whose elements can be unpacked into exactly two items (condition, action).
        - Conditions should be either type objects or callables that accept one positional argument.
    Postconditions:
        - The function returns either the first matched action or the built-in repr.
        - No mutation of item or custom_repr occurs.

## Side Effects:
    - The function itself has no side effects (no I/O, no global state mutation).
    - It does call condition callables during evaluation; any side effects those callables perform (or exceptions they raise) will occur and propagate.

## Control Flow:
flowchart TD
    Start --> ForLoop[For each element in custom_repr: unpack to (condition, action)]
    ForLoop --> IsType{isinstance(condition, type)?}
    IsType -- Yes --> BindLambda[condition := lambda x, y=condition: isinstance(x, y)]
    IsType -- No --> KeepCondition[use condition as-is]
    BindLambda --> Eval[Evaluate condition(item)]
    KeepCondition --> Eval
    Eval --> Match{condition(item) truthy?}
    Match -- Yes --> ReturnAction[return action]
    Match -- No --> NextRule[continue to next rule]
    NextRule --> ForLoop
    ForLoop --> NoMoreRules{no more rules?}
    NoMoreRules -- Yes --> ReturnRepr[return built-in repr]
    NoMoreRules -- No --> ForLoop

## Examples:
1) Type-based selection
    custom_repr = [
        (int, lambda x: f"<int:{x}>"),
        (str, lambda x: f"'{x}'"),
    ]
    action = get_repr_function(42, custom_repr)
    # action is the int lambda; action(42) -> "<int:42>"

2) Predicate condition and fallback
    custom_repr = [
        (lambda x: x is None, lambda x: "NULL"),
        (list, lambda x: "[" + ",".join(map(repr, x)) + "]"),
    ]
    action_none = get_repr_function(None, custom_repr)
    # action_none(None) -> "NULL"
    action_list = get_repr_function([1,2], custom_repr)
    # action_list([1,2]) -> "[1,2]"
    action_other = get_repr_function(3.14, custom_repr)
    # action_other is repr since no rule matched

3) Error cases
    # Non-iterable custom_repr:
    get_repr_function(1, None)  # raises TypeError: 'NoneType' object is not iterable

    # Element that is not an iterable:
    get_repr_function(1, [42])  # raises TypeError when unpacking the int element

    # Element with wrong number of items:
    get_repr_function(1, [(int,)])  # raises ValueError due to unpacking

Implementation note:
    - The conversion from a type object to a callable uses a default argument in the lambda (lambda x, y=condition: isinstance(x, y)) to bind the specific type value at definition time and avoid late-binding issues in loops.

## `pysnooper.utils.normalize_repr` · *function*

## Summary:
Removes (replaces with an empty string) all substrings that match a module-level regex DEFAULT_REPR_RE from the provided textual representation and returns the cleaned string.

## Description:
This function performs a single, focused transformation: it returns the result of calling the module-level regex object's sub method with an empty-string replacement on the provided input. In other words, it strips out any parts of the input that match DEFAULT_REPR_RE.

Known callers within the codebase:
    - None located in the available repository search results. Likely callers (based on the function's purpose in a tracing/logging utility) are places that prepare or sanitize object repr strings prior to logging, comparing, or outputting them (for example, before writing a line to a tracer or simplifying long reprs for display). Because no concrete callers were found in the provided context, this function should be considered a small utility intended for use wherever normalized representations are required.

Why this logic is extracted:
    - Responsibility boundary: isolates the regex-based normalization step so the regex itself (DEFAULT_REPR_RE) can be defined and tuned separately from call sites. This keeps callers simpler and centralizes the behavior for all repr-normalization needs.

## Args:
    item_repr (str): The textual representation to be normalized. The implementation calls DEFAULT_REPR_RE.sub('', item_repr), so item_repr must be a string (or another object accepted by the regex engine); typical usage passes the output of builtin repr(object) or str(object).

    Notes on interdependencies:
        - The behavior depends entirely on the module-level object DEFAULT_REPR_RE being a regex-like object that exposes a sub(repl, string) method (as provided by re.Pattern in the standard library). The exact matching behavior depends on how DEFAULT_REPR_RE is compiled (pattern, flags).

## Returns:
    str: The normalized string produced by DEFAULT_REPR_RE.sub('', item_repr).
    - If item_repr is a str and DEFAULT_REPR_RE is a text (unicode) regex pattern, the return is a str with every substring matching the regex removed.
    - If item_repr is bytes and DEFAULT_REPR_RE is a bytes pattern, the return would be bytes (this depends on DEFAULT_REPR_RE's type).
    - No additional wrapping or trimming is performed by this function; it returns exactly what the underlying regex substitution produces.

## Raises:
    NameError: If DEFAULT_REPR_RE is not defined in the module at the time the function is executed (the global name lookup will fail).
    AttributeError: If DEFAULT_REPR_RE exists but does not provide a sub method (for example, if it is set to None or some non-regex object).
    TypeError: If item_repr is not a type accepted by the regex engine's sub method (for example, passing an integer will produce a TypeError from the underlying re implementation).

## Constraints:
    Preconditions:
        - DEFAULT_REPR_RE must be present in the module globals and must behave like a compiled regex object (provide sub).
        - item_repr should be a string-like object compatible with the regex (commonly a str produced by repr()).

    Postconditions:
        - On successful return, the output equals the result of DEFAULT_REPR_RE.sub('', item_repr).
        - No mutation of input arguments or module-level state is performed by this function.

## Side Effects:
    - None intrinsic to this function: it performs pure computation and returns a value.
    - No I/O, no global-state mutation, and no external service calls are made by the code shown.

## Control Flow:
flowchart TD
    Start --> Check_DEFAULT_REPR_RE
    Check_DEFAULT_REPR_RE -->|defined and has sub| Call_sub
    Check_DEFAULT_REPR_RE -->|missing| Raise_NameError
    Call_sub -->|input accepted by regex engine| Return_Result
    Call_sub -->|input rejected| Raise_TypeError_or_AttributeError

## Examples:
    Example 1 (typical):
        Input: a repr string containing timestamp fragments that DEFAULT_REPR_RE is designed to remove.
        Effect: returns the input string with those timestamp fragments removed.

    Example 2 (error scenario):
        If DEFAULT_REPR_RE is accidentally deleted or replaced with None:
            Calling the function will raise NameError (if name removed) or AttributeError (if set to an object without sub).

    Example 3 (type error):
        If item_repr is an integer:
            The underlying regex engine will raise TypeError; the function does not catch or change that behavior.

## `pysnooper.utils.get_shortish_repr` · *function*

## Summary:
Return a compact, single-line textual representation of an object by invoking a chosen repr function, stripping carriage-returns/newlines, optionally normalizing via a module regex, and optionally truncating to a maximum length.

## Description:
- Known callers:
    - No direct callers were found in the available repository search results. Conceptually this function is intended for use by tracing/formatting code that needs a short, safe string to display for arbitrary objects (for example, a tracer that prints variable values on a single line).
- Typical context:
    - Called when preparing values for human-readable trace lines, logs, or small display widgets where multiline reprs or very long representations are undesirable.
- Why this is a separate function:
    - Encapsulates the full pipeline of (1) selecting a representation function for an item (via get_repr_function and the optional custom_repr rules), (2) safely invoking that function and recovering from any exception, (3) normalizing the textual representation using a central regex (normalize_repr), and (4) applying a consistent truncation policy (truncate).
    - Keeping these steps together enforces a single, consistent policy for preparing compact repr strings and avoids duplicating error-handling, newline removal, normalization, and truncation logic across the codebase.

## Args:
    item (Any):
        The object whose textual representation is requested. This can be any Python object.
    custom_repr (iterable of (condition, action), default=()):
        Optional ordered iterable of (condition, action) pairs used by get_repr_function to select a custom representation action for the item.
        - If empty or no rule matches, the built-in repr is used.
        - See get_repr_function docs for the allowed shapes of condition (type objects or predicate callables) and action (callable or other object that can produce/represent the item).
    max_length (int or None, default=None):
        If truthy, a maximum output length to enforce via truncate. Note:
        - The code checks "if max_length:" (truthiness), so max_length == 0 is treated as falsy and will skip truncation.
        - When provided, truncate's behavior (including for negative or small max_length values) follows the truncate documentation.
    normalize (bool, default=False):
        If True, the textual output is passed through normalize_repr before truncation. normalize_repr uses the module-level DEFAULT_REPR_RE to remove matched substrings.

## Returns:
    str:
        A single-line textual representation of the item after processing. Specifically:
        1) repr_function(item) is invoked (repr_function obtained from get_repr_function). If that call raises any Exception, the literal string 'REPR FAILED' is used instead.
        2) All '\r' and '\n' characters are removed from the result.
        3) If normalize is True, the result is passed to normalize_repr(...).
        4) If max_length is truthy, the result is passed to truncate(...).
        Under normal operation (repr_function returns a str), the function returns a str with no CR or newline characters; optionally normalized and/or truncated.
    Notes on edge-case returns:
        - If repr_function returns a non-text object (e.g., bytes or an object without a replace method), subsequent calls to .replace, normalize_repr, or truncate may raise exceptions. In typical Python usage, repr returns a str, so the common-case return type is str.
        - If repr_function raised an exception, the returned value will be 'REPR FAILED' (possibly normalized/truncated as configured).

## Raises:
    - Exceptions from normalize_repr(...) (e.g., NameError if DEFAULT_REPR_RE missing, AttributeError, TypeError) will propagate if normalize is True.
    - Exceptions from truncate(...) (e.g., TypeError if provided object does not support len() or slicing, or if max_length has an invalid type) will propagate if truncation is applied.
    - If repr_function returns a value that does not support str.replace with str arguments (for example, bytes), calling r.replace('\r', '') will raise a TypeError or AttributeError which will propagate.
    - Only exceptions raised by repr_function(item) are caught by this function; those are handled by falling back to the literal 'REPR FAILED'. All other exceptions propagate.

## Constraints:
Preconditions:
    - custom_repr (if provided) must be an iterable acceptable to get_repr_function (see get_repr_function docs).
    - Expectation: the selected representation callable returns a text string (str). Passing a repr function that returns non-text may cause subsequent operations to raise.
    - If you require strict truncation to a specific numeric width, pass an integer >= 3 to max_length; note that get_shortish_repr only applies truncation when max_length is truthy.
Postconditions:
    - The returned value contains no carriage-return ('\r') or newline ('\n') characters.
    - If no exceptions occur and a text repr is returned by the selected repr function, the final result will be a str (possibly normalized and/or truncated).

## Side Effects:
    - None intrinsic to this function: it performs no I/O, does not mutate global state, and does not call external services.
    - It does call user-provided condition or action callables via get_repr_function and the selected repr_function(item). Those callables may have arbitrary side effects; any such side effects will occur.
    - Errors raised by user-provided callables (except those raised during repr_function(item) — which are caught and converted into 'REPR FAILED') may propagate depending on where they occur.

## Control Flow:
flowchart TD
    Start --> SelectRepr[get_repr_function(item, custom_repr) -> repr_function]
    SelectRepr --> TryCall[Try: r = repr_function(item)]
    TryCall --> ReprOK{repr_function raised?}
    ReprOK -- Yes --> UseFail[Set r = 'REPR FAILED']
    ReprOK -- No --> UseR[Use repr result]
    UseFail --> Strip[Remove '\r' and '\n' from r]
    UseR --> Strip
    Strip --> NormalizeCheck{normalize is True?}
    NormalizeCheck -- Yes --> NormalizeCall[r = normalize_repr(r)]
    NormalizeCheck -- No --> SkipNormalize
    NormalizeCall --> TruncateCheck
    SkipNormalize --> TruncateCheck
    TruncateCheck{max_length truthy?} -- Yes --> TruncateCall[r = truncate(r, max_length)]
    TruncateCheck -- No --> SkipTruncate
    TruncateCall --> Return[r]
    SkipTruncate --> Return

## Examples:
1) Basic usage — default behavior (no custom rules, no normalization/truncation)
    - Call: get_shortish_repr(obj)
    - Effect: returns repr(obj) with any '\r' or '\n' removed. If repr(obj) raises, returns 'REPR FAILED'.

2) Using a custom representation rule for integers and truncation
    - custom_repr = [(int, lambda x: "<int:" + str(x) + ">")]
    - Call: get_shortish_repr(1234567890, custom_repr=custom_repr, max_length=8)
    - Behavior:
        * get_repr_function selects the int lambda
        * repr_function(1234567890) -> "<int:1234567890>"
        * CR/newline removal: no-op
        * truncate with max_length=8 -> applies truncate on the string, producing a shortened result such as "<i...890" (exact text determined by truncate's left/right calculation)

3) Normalization then truncation
    - Suppose DEFAULT_REPR_RE removes memory-address-like fragments from reprs.
    - Call: get_shortish_repr(some_obj, normalize=True, max_length=30)
    - Behavior:
        * A single-line repr is produced, normalized by DEFAULT_REPR_RE.sub('', ...), then truncated to at most 30 characters (truncate only executes because max_length is truthy).

4) repr failure handling
    - If the selected repr_function raises any Exception when called, the function uses the literal 'REPR FAILED' and continues processing:
        * Example: get_shortish_repr(broken_obj, max_length=5) -> returns a truncated/processed form of 'REPR FAILED' (the truncation and normalization steps still apply).

5) Error propagation examples (what to avoid)
    - Passing a representation function that returns bytes:
        * The subsequent r.replace('\r', '') call expects a str; bytes will cause a TypeError/AttributeError to propagate.
    - Passing max_length=0:
        * Because the code uses "if max_length:", truncation is skipped for 0 (no truncation). To request truncation, provide a truthy integer (e.g., 3 or greater).

## `pysnooper.utils.truncate` · *function*

## Summary:
If the input exceeds a given maximum length, return a new text string that preserves the start and end of the input with the middle replaced by an ellipsis ("..."); otherwise return the original value unchanged.

## Description:
- Known callers within the codebase:
    - Used by formatting and tracing utilities that prepare string values for display (e.g., when printing variable values in a compact trace). Call sites call this function when they need to ensure displayed strings do not exceed a configured width.
- Why this is a separate function:
    - Encapsulates a consistent truncation policy (use of a three-character ellipsis and symmetric preservation of prefix and suffix), avoiding duplication and ensuring consistent visual output across different modules.

## Args:
    string (str-like; expected text string):
        The value to possibly shorten. The function uses len() and slicing with string slice semantics; callers should pass text strings (unicode/str). Passing non-sequence objects will raise the usual TypeError from len() or slicing.
    max_length (int or None):
        Maximum allowed length for the returned string.
        - None: indicates no truncation; the original value is returned unchanged.
        - int: truncation is applied only when len(string) > max_length.
        - The implementation requires an integer for predictable behavior; passing non-integers (e.g., float) will later raise TypeError when slice indices are used.
        - The function does not validate that max_length is >= 0; negative or very small values are permitted by the implementation but can produce non-intuitive results (see Examples and Constraints).

## Returns:
    str (text string):
    - If max_length is None or len(string) <= max_length: returns the original input value unchanged (same object/reference when the input is already a text string).
    - Otherwise: returns a newly constructed text string equal to:
        prefix + '...' + suffix
      where
        left = (max_length - 3) // 2
        right = max_length - 3 - left
        prefix = string[:left]
        suffix = string[-right:]
    - Guarantee about length:
        * If truncation occurs and max_length is an integer >= 3, the returned string's length will equal max_length.
        * For max_length values less than 3 (or negative), the arithmetic produces negative or zero slice indices and the returned length may not equal max_length; callers should avoid those values if a strict length guarantee is required.

## Raises:
    - The function contains no explicit raise statements.
    - It will propagate built-in exceptions:
        * TypeError: if the provided object does not support len() or slicing, or if max_length is a non-integer type that causes invalid slice indices.
        * Any other exceptions raised by len() or slicing on the provided object.

## Constraints:
- Preconditions:
    - Prefer passing a text string (unicode in Python 2, str in Python 3).
    - Prefer passing max_length as an integer (or None). If a strict guarantee that the result length equals max_length is required, ensure max_length is an integer >= 3 before calling.
- Postconditions:
    - No mutation of the input occurs.
    - If no truncation is performed, the original object is returned unchanged.
    - If truncation is performed, the result contains the literal '...' and preserves characters from both ends according to the left/right computation.

## Side Effects:
    - None. Pure function: no I/O, no global state mutation, no external calls.

## Control Flow:
flowchart TD
    Start[Start]
    Start --> Check{max_length is None OR len(string) <= max_length?}
    Check -- Yes --> ReturnOriginal[Return original input unchanged]
    Check -- No --> ComputeLeft[Compute left = (max_length - 3) // 2]
    ComputeLeft --> ComputeRight[Compute right = max_length - 3 - left]
    ComputeRight --> Build[Construct prefix = string[:left]; suffix = string[-right:]; result = prefix + "..." + suffix]
    Build --> ReturnTruncated[Return truncated text string]

## Examples:
- Typical truncation (max_length >= 3, result length equals max_length):
    Input: string = "abcdefghijklmnop", max_length = 10
    left = (10 - 3) // 2 = 3
    right = 10 - 3 - 3 = 4
    Output: "abc...mnop"  (length 10)

- No truncation (max_length is None):
    Input: string = "short", max_length = None
    Output: "short"  (original object returned unchanged)

- No truncation (already within limit):
    Input: string = "short", max_length = 10
    Output: "short"

- Edge case: exact minimal ellipsis-only output (max_length == 3):
    Input: string = "longtext", max_length = 3
    left = 0, right = 0
    Output: "..."  (length 3)

- Edge case: small or negative max_length (behavior is determined by Python slice semantics and may be non-intuitive):
    Input: string = "example", max_length = 2
    left = (2 - 3) // 2 = -1
    right = 2 - 3 - (-1) = 0
    prefix = string[:-1]  (all but last character)
    suffix = string[-0:]  (empty)
    Output: prefix + "..."  (length > 2) — not guaranteed to equal max_length.
    Note: To avoid surprising results, validate that max_length is an integer >= 3 when a strict maximum-width result is required.

- Invalid input types:
    If string is an object without len() or slicing (for example, an int), the call will raise TypeError.

## `pysnooper.utils.ensure_tuple` · *function*

## Summary:
Normalize any input into a tuple: if the input is an iterable (but not a text/string type), return a tuple of its elements; otherwise wrap the input as a single-element tuple.

## Description:
This small utility ensures callers receive a tuple regardless of whether they were given a single value or a sequence. It treats text-like inputs (as defined by pycompat.string_types) as scalar values, not sequences to be expanded into characters.

Known callers within this repository snapshot:
    - No explicit call-sites were found in the provided project snapshot. Typical use cases (not present here) include argument normalization for APIs that accept either a single item or multiple items, configuration parsing, or internal utility functions that want a uniform tuple input.

Why extracted into a helper:
    - Centralizes the Iterable vs. string-type decision and the wrapping behavior so callers do not duplicate the type-check logic and risk inconsistent handling (for example, accidentally splitting strings into characters). It also documents the intentional treatment of string-like types as scalars.

## Args:
    x (Any): The value to normalize.
        - If x is an instance of collections_abc.Iterable and NOT an instance of pycompat.string_types, the function will return tuple(x).
        - Otherwise (including when x is a string-like object), the function will return (x,).
        - No parameter defaults.

## Returns:
    tuple:
        - If x is an iterable (and not a pycompat.string_types instance) -> tuple(x). This may be an empty tuple when x is empty.
        - Otherwise -> a single-element tuple containing x: (x,).
    Type note:
        - The element types within the returned tuple reflect whatever the iterable yields; no type conversion is performed.
    Edge-case examples:
        - x is None -> (None,)
        - x is an empty list -> ()
        - x is a generator -> tuple of generated items (the generator is consumed)
        - x is a dict -> tuple of the dict's keys
        - x is a string -> ('the string',)

## Raises:
    - The function itself does not explicitly raise exceptions.
    - Any exception raised during evaluation/iteration of x (for example, if x.__iter__ or the iterator raises) will propagate to the caller unchanged.

## Constraints:
    Preconditions:
        - collections_abc.Iterable and pycompat.string_types must be available (they are imported at module-level or the function imports string_types locally).
        - Callers expecting to reuse iterator/generator inputs must be aware that passing such an object will consume it.
    Postconditions:
        - The function always returns a tuple object.
        - If x is an iterable and not string-like, the returned tuple is exactly tuple(x) (length may be 0).
        - If x is non-iterable or string-like, the returned tuple has length 1 and contains x as its sole element.

## Side Effects:
    - No I/O, no network, no stdout printing.
    - Observable effects:
        - If x is an iterator or generator, it will be consumed (exhausted) to build the tuple.
        - Memory is allocated for the returned tuple proportional to the number of elements in the iterable case.
    - No global state or external services are modified.

## Control Flow:
flowchart TD
    Start --> IsIterable{isinstance(x, Iterable)?}
    IsIterable -- No --> ReturnSingle((x,))
    IsIterable -- Yes --> IsString{isinstance(x, string_types)?}
    IsString -- Yes --> ReturnSingle((x,))
    IsString -- No --> ConvertTuple(tuple(x)) --> ReturnTuple
    ReturnSingle --> End
    ReturnTuple --> End

## Examples:
    - List input:
        ensure_tuple([1, 2, 3])  # returns (1, 2, 3)

    - String input (treated as scalar):
        ensure_tuple("abc")  # returns ("abc",)

    - Generator input (generator is consumed):
        gen = (i for i in range(3))
        ensure_tuple(gen)  # returns (0, 1, 2)
        # gen is now exhausted

    - Non-iterable input:
        ensure_tuple(42)  # returns (42,)

    - Empty iterable:
        ensure_tuple([])  # returns ()

    - Error propagation:
        # If iterator raises during iteration, the exception propagates
        try:
            ensure_tuple(broken_iterable)
        except Exception as e:
            handle(e)

