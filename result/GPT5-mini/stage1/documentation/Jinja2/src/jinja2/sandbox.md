# `sandbox.py`

## `src.jinja2.sandbox.inspect_format_method` · *function*

## Summary:
Detects whether a given callable is a bound string format method and, if so, returns the underlying string object; otherwise returns None.

## Description:
This helper inspects a Python callable to determine if it is a bound method named "format" or "format_map" whose bound receiver (the __self__ attribute) is a str. If both conditions hold, the function returns that string instance; otherwise it returns None.

Known callers within the provided repository snapshot:
    - No direct callers were present in the provided file snapshot. In typical use within a sandboxing or template-evaluation environment, this function is invoked when the sandbox needs to detect calls to a string's format methods so they can be handled or restricted specially before invocation.

Why this logic is extracted:
    - The check is a narrowly scoped predicate used to recognize the common case of the bound string formatting methods. Extracting it keeps the caller code concise and centralizes the exact checks (type of method, method name, and receiver type), making reasoning about and modifying the format-method detection easier and less error-prone.

## Args:
    callable (typing.Callable): Any Python callable to inspect. Expected to be an object that may be a bound method (types.MethodType or types.BuiltinMethodType). The function performs type checks and attribute access safely for method/builtin-method instances; other callables are permitted but will not match.

Notes on the parameter:
    - The function expects a callable argument but does not assume it is a function object; it explicitly tests for types.MethodType or types.BuiltinMethodType before accessing method-specific attributes.
    - The parameter name shadows the built-in name "callable"; callers may choose a different name to avoid confusion, but the behavior depends only on the runtime value passed.

## Returns:
    typing.Optional[str]:
    - If the supplied callable is a bound method (an instance of types.MethodType or types.BuiltinMethodType), its __name__ is either "format" or "format_map", and its bound receiver (callable.__self__) is an instance of str, the function returns that str object.
    - In all other cases the function returns None.

All possible return values:
    - A str instance: when a bound string method matching the name checks is detected (e.g., "hello {}".format).
    - None: when the callable is not a bound method of the accepted types, has a different __name__, or is bound to a non-str object.

## Raises:
    - The implementation raises no exceptions deliberately. Access to callable.__self__ is only performed after confirming the callable is a MethodType or BuiltinMethodType, which guarantees the attribute exists; therefore no AttributeError is expected from that access in correctly behaving Python implementations.

## Constraints:
Preconditions:
    - The runtime environment is a standard Python implementation where instances of types.MethodType and types.BuiltinMethodType expose a __name__ and __self__ attribute as usual.
    - The caller should expect and handle None return values when the callable does not represent a bound string-format method.

Postconditions:
    - The function performs no mutation and returns either a reference to the original string object bound to the method or None.
    - No side effects or changes to input objects or global state are made.

## Side Effects:
    - None. The function performs only type inspection and attribute access; it does not perform I/O, mutate globals, write to disk, or call external services.

## Control Flow:
flowchart TD
    Start([Start]) --> IsMethod{Is instance of MethodType or BuiltinMethodType?}
    IsMethod -- No --> ReturnNone1([return None])
    IsMethod -- Yes --> NameCheck{callable.__name__ in ("format","format_map")?}
    NameCheck -- No --> ReturnNone2([return None])
    NameCheck -- Yes --> GetSelf[ obj = callable.__self__ ]
    GetSelf --> IsStr{isinstance(obj, str)?}
    IsStr -- Yes --> ReturnStr([return obj])
    IsStr -- No --> ReturnNone3([return None])

## Examples:
Example 1 — bound string method (typical positive case):
    s = "Hello {name}"
    m = s.format         # bound method; builtin method or method type
    result = inspect_format_method(m)
    # result == "Hello {name}" (the original string object s)

Example 2 — format method bound to non-str receiver:
    class C:
        def format(self): ...
    c = C()
    result = inspect_format_method(c.format)
    # result is None because c is not an instance of str

Example 3 — function or unbound method:
    def format_map(x): ...
    result = inspect_format_method(format_map)
    # result is None because the callable is not a bound method instance

Usage note:
    - Callers should treat a truthy return (a str) as an indication that the callable is a formatting operation tied to that specific string and can make decisions (such as disallowing invocation or pre-inspecting the format string). A None return indicates no special-case formatting-string handling should be applied.

## `src.jinja2.sandbox.safe_range` · *function*

## Summary:
Creates and returns a Python range object from the supplied integer arguments, but enforces a sandbox limit by raising OverflowError when the produced range's length exceeds the module-level MAX_RANGE.

## Description:
This helper centralizes the sandbox policy that disallows excessively large ranges. It constructs a built-in range using the provided integer arguments and then rejects the range if its length exceeds MAX_RANGE.

Known callers:
- No callers were identified in the provided context. If used elsewhere in the codebase, typical callers are sandbox-aware template runtime functions that construct numeric ranges for iteration (for example, code that would otherwise call the built-in range in template execution).

Why this function exists:
- Responsibility boundary: it encapsulates the security/size-check for ranges so all sandboxed code can rely on a single policy point (check + error) rather than duplicating the check around ad-hoc range construction. This makes it straightforward to change the limit behavior or error handling in one place.

## Args:
- *args (int): One to three integer arguments forwarded directly to the built-in range constructor. They correspond to the same semantics as range(start, stop[, step]) or range(stop) when a single argument is provided.
    - Allowed values/types: integers (annotation indicates ints). Non-integer or otherwise invalid arguments will be propagated from the built-in range (see Raises).
    - Interdependencies: follows the same argument interdependencies as built-in range (1..3 positional integer args; step cannot be zero).

## Returns:
- range: The constructed range object equivalent to range(*args) provided that its length does not exceed MAX_RANGE.
    - Normal return: a range object covering the requested sequence.
    - Edge-case return: an empty range may be returned when the arguments produce an empty interval (this is the same behavior as built-in range).

## Raises:
- OverflowError: raised when len(range(*args)) > MAX_RANGE. The exact message raised by the implementation is:
  "Range too big. The sandbox blocks ranges larger than MAX_RANGE (<value>)."
  (The actual numeric value for MAX_RANGE is a module-level constant and is not specified here; the implementation references it directly.)
- Any exception raised by the built-in range constructor is propagated:
  - TypeError: if non-integer arguments are passed (or incompatible types).
  - ValueError: e.g., if step == 0.
  These are not caught by this function and will surface to the caller.

## Constraints:
- Preconditions:
  - A module-level integer constant named MAX_RANGE must exist and be accessible in the same module. It should be a non-negative integer representing the maximum allowed length for ranges in the sandbox.
  - Callers should pass at most three integers (start, stop, step) or a single stop integer, following built-in range semantics.
- Postconditions:
  - If the function returns normally, the returned range's length is guaranteed to be <= MAX_RANGE.
  - If the length would exceed MAX_RANGE, the function will raise OverflowError and will not return a range.

## Side Effects:
- None. The function performs no I/O and does not mutate external state or global variables beyond reading MAX_RANGE.
- It only constructs a range object and performs an in-memory length check.

## Control Flow:
flowchart TD
    Start --> CreateRange[Create range = range(*args)]
    CreateRange --> ComputeLen[Compute len(range)]
    ComputeLen --> CheckLimit{len(range) > MAX_RANGE?}
    CheckLimit -->|Yes| RaiseOverflow[Raise OverflowError]
    CheckLimit -->|No| ReturnRange[Return range]
    RaiseOverflow --> End
    ReturnRange --> End

## Examples:
- Successful construction (conceptual):
  - Given arguments that produce a sequence whose length is within the sandbox limit, the function returns the corresponding range object (equivalent to built-in range(*args)).
  - Example scenario described in prose: If MAX_RANGE is 1000 and a caller requests a range covering 0..100, the function returns the range(0, 100).

- Rejection due to sandbox limit (conceptual):
  - If MAX_RANGE is 1000 and a caller requests range(0, 2000), the function raises OverflowError indicating the range is too big; callers should catch OverflowError if they need to handle or report this condition.

- Propagated errors:
  - If a caller passes invalid arguments (for example, a non-integer or step == 0), the underlying built-in range will raise TypeError or ValueError respectively; safe_range does not swallow these exceptions.

Notes for implementers:
- Implementers reconstructing this function must ensure that the length check uses Python's len(range_object) and that MAX_RANGE is defined as an integer in the same module. Keep the exception semantics identical (propagate built-in range exceptions; raise OverflowError with an explanatory message when the length exceeds MAX_RANGE).

## `src.jinja2.sandbox.unsafe` · *function*

## Summary:
Marks an object (typically a user-defined callable) as unsafe for sandboxing by setting a boolean attribute on the object and returns the same object.

## Description:
This small decorator-style helper attaches an attribute named unsafe_callable with the boolean value True to the provided object and returns that same object. The intended purpose is to provide a simple, explicit flag that sandboxing or registration logic elsewhere can check to treat the object specially.

Known callers within the provided repository snapshot:
    - No direct callers were found in the scanned snapshot. The function is designed to be used by call sites that register or inspect user-provided callables (for example, prior to adding filters, tests, or globals to an environment that enforces sandbox policies).

Why this is a separate function:
    - Encapsulates a single, explicit intent: "this callable is considered unsafe." Centralizing the attribute-setting avoids repeated ad-hoc attribute assignments across the codebase, makes intent explicit in call sites, and separates the act of marking from sandbox policy logic that reads that mark.

## Args:
    f (F): The target object to mark. F is the generic type variable representing the input object's static type; the function preserves and returns the same type. In practice callers will pass Python functions, bound methods, or callable objects, but the implementation does not enforce callability.

    Notes:
    - No validation is performed that f is callable.
    - The function will overwrite any existing attribute named unsafe_callable on the object.

## Returns:
    F: The exact same object reference that was passed in, now bearing the attribute unsafe_callable set to True.

    Return scenarios:
    - Success: returns the original object instance with unsafe_callable == True.
    - Failure: if attribute assignment fails, an exception is raised and no value is returned.

## Raises:
    The function does not catch or translate exceptions from the attribute assignment; any such exception propagates to the caller. The most common exception in practice is:
    - AttributeError: raised when the object's type does not permit setting arbitrary attributes (for example, many built-in functions, types implemented in C, or instances constrained by __slots__ without the attribute).
    Other exceptions raised during attribute assignment by the object's type implementation will also propagate as-is.

## Constraints:
    Preconditions:
    - If the caller requires the marking to succeed, the object should accept attribute assignment (i.e., allow arbitrary attributes or include unsafe_callable in its layout).
    - No attempt is made to ensure f is callable; callers should enforce callability if that is required by their protocol.

    Postconditions:
    - On successful return, the object has an attribute named unsafe_callable whose value is True, and the returned reference is identical to the argument reference.

## Side Effects:
    - Mutates the provided object by adding or replacing the attribute unsafe_callable.
    - No I/O is performed and no global variables or external services are modified by this function.

## Control Flow:
flowchart TD
    A[Start: receive object f] --> B{Attempt f.unsafe_callable = True}
    B -- Assignment succeeds --> C[Return f (with unsafe_callable == True)]
    B -- Assignment fails (AttributeError or other) --> D[Exception propagates to caller]

## Examples (descriptive):
    - Typical successful use:
      A user-defined function or a callable object is passed to this helper immediately before registration with a sandboxing-aware registry. After marking, the registration or sandbox code can detect unsafe_callable == True and apply stricter restrictions.

    - Overwriting an existing marker:
      If the object already had an unsafe_callable attribute, the helper will replace its value with True.

    - Handling objects that forbid attribute assignment:
      When attempting to mark built-in functions or other objects that do not allow arbitrary attributes, attribute assignment will raise (commonly AttributeError). Callers that may pass such objects should wrap the call in a try/except block and implement fallback logic (for example, skip marking and log a warning, or wrap the built-in in a user-defined callable that can be marked).

    - Type-preserving behavior:
      Because the function returns the same object reference and is annotated with the generic type F, it can be used inline where the original callable value is expected by the surrounding code (for example, assignable back into registration tables or returned from factory functions).

## `src.jinja2.sandbox.is_internal_attribute` · *function*

## Summary:
Determines whether accessing a named attribute on an object should be treated as internal/unsafe by the sandbox policy; returns True when the access must be blocked.

## Description:
This function implements a deterministic, ordered policy to decide whether obj.attr is an internal/unsafe attribute. It examines the runtime type of obj and then applies one or more membership or equality checks against module-level unsafe-name collections. The checks are performed in the following order (first matching rule returns True):

1. If obj is an instance of types.FunctionType:
   - Return True if attr is a member of UNSAFE_FUNCTION_ATTRIBUTES.

2. Else if obj is an instance of types.MethodType:
   - Return True if attr is a member of UNSAFE_FUNCTION_ATTRIBUTES or UNSAFE_METHOD_ATTRIBUTES.

3. Else if obj is an instance of type (i.e., a class object):
   - Return True if attr == "mro".

4. Else if obj is an instance of any of (types.CodeType, types.TracebackType, types.FrameType):
   - Return True (all attribute access on these objects is considered internal/unsafe).

5. Else if obj is an instance of types.GeneratorType:
   - Return True if attr is a member of UNSAFE_GENERATOR_ATTRIBUTES.

6. Else if the types module exposes CoroutineType and obj is an instance of it:
   - Return True if attr is a member of UNSAFE_COROUTINE_ATTRIBUTES.

7. Else if the types module exposes AsyncGeneratorType and obj is an instance of it:
   - Return True if attr is a member of UNSAFE_ASYNC_GENERATOR_ATTRIBUTES.

8. Fallback:
   - Return True if attr.startswith("__") (attribute name begins with a double underscore).
   - Otherwise return False.

Known callers in provided context:
- No concrete callers were present in the supplied source excerpt. Typical callers in a sandboxed template engine include the internal safe_getattr / attribute-resolution path invoked during template rendering. Do not assume any additional callers beyond these typical contexts unless you locate them in the codebase.

Why this is a separate function:
- The decision depends on obj's runtime class and on centralized module-level unsafe-name collections (UNSAFE_*). Centralizing the rules prevents duplication and makes the policy easier to review and maintain.

Note about UNSAFE_* names:
- The function references the following module-level names: UNSAFE_FUNCTION_ATTRIBUTES, UNSAFE_METHOD_ATTRIBUTES, UNSAFE_GENERATOR_ATTRIBUTES, UNSAFE_COROUTINE_ATTRIBUTES, UNSAFE_ASYNC_GENERATOR_ATTRIBUTES.
- The source implementation performs membership tests (attr in SOME_COLLECTION) against these names. The collections must therefore be defined in the same module at runtime; otherwise a NameError will occur when the function is executed.
- The documentation does not assume a particular container type for these constants; they must be containers that support the "in" membership test (e.g., set, frozenset, list, tuple, etc.). If a collection requires its elements to be hashable (e.g., set, frozenset), passing an unhashable attr (like a list) can raise TypeError during membership tests.

## Args:
    obj (t.Any): The target object whose attribute is being accessed. Any Python object is permitted (functions, methods, classes, generator objects, coroutine objects, code objects, frames, tracebacks, etc.).
    attr (str): The attribute name being accessed. The function expects a string identifying the attribute; callers should coerce/validate attr accordingly.

## Returns:
    bool: True when the attribute access is classified as internal/unsafe (i.e., callers should block or deny the lookup); False otherwise.

- True is returned on the first matching rule described above.
- False is returned only if none of the type-specific rules match and attr does not start with "__".

## Raises:
- NameError: If any of the referenced UNSAFE_* module-level names are not defined when the function executes, Python will raise NameError at the point of the membership test. Ensure the sandbox module defines all referenced constants.
- TypeError (indirect): If attr is unhashable and a membership test is performed against a container that requires hashable elements (e.g., a set or frozenset), Python may raise TypeError during "attr in container".
- AttributeError (indirect): If attr does not provide a startswith method (for example, attr is None), the final attr.startswith("__") call may raise AttributeError.
- The function does not explicitly raise SecurityError — it only returns a boolean that a caller can use to raise or enforce SecurityError.

## Constraints:
Preconditions:
- Prefer callers to pass attr as a str (and hashable). The function assumes attr is a string-like identifier for best behavior.

Postconditions:
- No mutation: the function performs only inspection and membership checks; it does not modify obj or global state.
- Deterministic: given the same obj, attr, and the same definitions of the module-level UNSAFE_* collections, the function returns the same boolean answer.

## Side Effects:
- None. The function performs no I/O and does not mutate program state.

## Implementation recipe (sufficient to reimplement):
1. Accept parameters obj (any) and attr (string).
2. If isinstance(obj, types.FunctionType):
     - If attr in UNSAFE_FUNCTION_ATTRIBUTES: return True
3. Elif isinstance(obj, types.MethodType):
     - If attr in UNSAFE_FUNCTION_ATTRIBUTES or attr in UNSAFE_METHOD_ATTRIBUTES: return True
4. Elif isinstance(obj, type):
     - If attr == "mro": return True
5. Elif isinstance(obj, (types.CodeType, types.TracebackType, types.FrameType)):
     - return True
6. Elif isinstance(obj, types.GeneratorType):
     - If attr in UNSAFE_GENERATOR_ATTRIBUTES: return True
7. Elif hasattr(types, "CoroutineType") and isinstance(obj, types.CoroutineType):
     - If attr in UNSAFE_COROUTINE_ATTRIBUTES: return True
8. Elif hasattr(types, "AsyncGeneratorType") and isinstance(obj, types.AsyncGeneratorType):
     - If attr in UNSAFE_ASYNC_GENERATOR_ATTRIBUTES: return True
9. Return the boolean result of attr.startswith("__") as the final fallback.

Notes:
- Respect the exact order above; the function returns as soon as a check matches.
- Use membership tests exactly as shown to match the original policy semantics.
- Guard the CoroutineType and AsyncGeneratorType checks with hasattr(types, "...") to remain compatible with Python versions that do not expose those names.

## Control Flow:
flowchart TD
    Start([start])
    IsFunction{isinstance(obj, types.FunctionType)}
    IsMethod{isinstance(obj, types.MethodType)}
    IsType{isinstance(obj, type)}
    IsCodeLike{isinstance(obj, (types.CodeType, types.TracebackType, types.FrameType))}
    IsGenerator{isinstance(obj, types.GeneratorType)}
    HasCoroutineType{hasattr(types,"CoroutineType") and isinstance(obj, types.CoroutineType)}
    HasAsyncGenType{hasattr(types,"AsyncGeneratorType") and isinstance(obj, types.AsyncGeneratorType)}
    AttrInUnsafeFunc{attr in UNSAFE_FUNCTION_ATTRIBUTES}
    AttrInUnsafeMethod{(attr in UNSAFE_FUNCTION_ATTRIBUTES) or (attr in UNSAFE_METHOD_ATTRIBUTES)}
    AttrIsMro{attr == "mro"}
    AttrInUnsafeGen{attr in UNSAFE_GENERATOR_ATTRIBUTES}
    AttrInUnsafeCoro{attr in UNSAFE_COROUTINE_ATTRIBUTES}
    AttrInUnsafeAsyncGen{attr in UNSAFE_ASYNC_GENERATOR_ATTRIBUTES}
    AttrDunder{attr.startswith("__")}
    ReturnTrue([return True])
    ReturnFalse([return False])

    Start --> IsFunction
    IsFunction -- yes --> AttrInUnsafeFunc
    AttrInUnsafeFunc -- yes --> ReturnTrue
    AttrInUnsafeFunc -- no --> IsMethod
    IsFunction -- no --> IsMethod
    IsMethod -- yes --> AttrInUnsafeMethod
    AttrInUnsafeMethod -- yes --> ReturnTrue
    AttrInUnsafeMethod -- no --> IsType
    IsMethod -- no --> IsType
    IsType -- yes --> AttrIsMro
    AttrIsMro -- yes --> ReturnTrue
    AttrIsMro -- no --> IsCodeLike
    IsType -- no --> IsCodeLike
    IsCodeLike -- yes --> ReturnTrue
    IsCodeLike -- no --> IsGenerator
    IsGenerator -- yes --> AttrInUnsafeGen
    AttrInUnsafeGen -- yes --> ReturnTrue
    AttrInUnsafeGen -- no --> HasCoroutineType
    IsGenerator -- no --> HasCoroutineType
    HasCoroutineType -- yes --> AttrInUnsafeCoro
    AttrInUnsafeCoro -- yes --> ReturnTrue
    AttrInUnsafeCoro -- no --> HasAsyncGenType
    HasCoroutineType -- no --> HasAsyncGenType
    HasAsyncGenType -- yes --> AttrInUnsafeAsyncGen
    AttrInUnsafeAsyncGen -- yes --> ReturnTrue
    AttrInUnsafeAsyncGen -- no --> AttrDunder
    HasAsyncGenType -- no --> AttrDunder
    AttrDunder -- yes --> ReturnTrue
    AttrDunder -- no --> ReturnFalse

## Examples:
1) Basic defensive caller pattern:
    # Coerce attr to string and handle indirect exceptions
    try:
        attr_name = str(attr_name)
        if is_internal_attribute(obj, attr_name):
            # deny access (e.g., raise SecurityError or return an error)
            raise SecurityError("access to internal attribute blocked")
        # otherwise proceed to getattr(obj, attr_name)
    except (TypeError, AttributeError, NameError) as exc:
        # handle malformed attr or missing UNSAFE_* definitions
        raise

2) Dunder attribute example:
    is_internal_attribute(42, "__class__")  # -> True (dunder fallback)

3) Class mro example:
    class C: pass
    is_internal_attribute(C, "mro")  # -> True

4) Code object and frame:
    import types
    code_obj = (lambda: 0).__code__
    is_internal_attribute(code_obj, "co_argcount")  # -> True (code objects always blocked)

5) Function/generator example (depends on module-level UNSAFE_* contents):
    def f(): pass
    is_internal_attribute(f, "co_consts")  # -> True only if "co_consts" in UNSAFE_FUNCTION_ATTRIBUTES

    def gen(): yield 1
    g = gen()
    is_internal_attribute(g, "gi_frame")  # -> True only if "gi_frame" in UNSAFE_GENERATOR_ATTRIBUTES

## `src.jinja2.sandbox.modifies_known_mutable` · *function*

## Summary:
Determines whether a named attribute on a given object is classified in a global specification as a known mutable/unsafe attribute; returns True when the attribute is listed as unsafe for the first matching type specification, otherwise False.

## Description:
This utility consults a global ordered specification named _mutable_spec. The specification is an iterable of pairs (typespec, unsafe). For each entry, it tests isinstance(obj, typespec). On the first entry where that test is True, it checks membership of attr in unsafe and returns the boolean result immediately. If no typespec matches, the function returns False.

Known callers within the codebase:
- No direct references to this function were found in the scanned repository graph. Typical and intended callers are sandboxing or security checks that must decide whether an attribute access or assignment should be treated as potentially mutating and therefore restricted (for example: attribute-assignment guards, template sandbox enforcement, or attribute-access instrumentation).

Why this logic is factored out:
- Centralizes a first-match, typespec-driven policy determining which attributes are "unsafe" to mutate.
- Keeps callers simple by encapsulating matching logic and membership semantics in a single place.
- Makes the matching policy replaceable and testable without repeating membership logic across the codebase.

## Args:
    obj (t.Any):
        The object instance to test. The function uses isinstance(obj, typespec) for matching; obj may be any Python object.
    attr (str):
        The attribute name to check. The function performs a membership test (attr in unsafe), so attr can be any hashable or comparable value appropriate for the unsafe collection, but is semantically expected to be a string attribute name.

Interdependencies:
- The function relies on a global name _mutable_spec. Its correctness depends on that object having the expected structure (see Constraints).

## Returns:
    bool:
      - True: There exists an entry (typespec, unsafe) in _mutable_spec such that isinstance(obj, typespec) is True for the first matching entry and attr is a member of unsafe.
      - False: Either no typespec in _mutable_spec matches obj, or the first matching entry's unsafe collection does not contain attr.

Notes on return behavior:
- First-match semantics: once a typespec matches, the function returns the result of attr in unsafe for that entry and does not inspect later entries, even if later typespecs would also match.
- The membership semantics depend entirely on the unsafe object's implementation of the membership operator (e.g., set/list/tuple or a custom container).

## Raises:
    NameError:
        - If _mutable_spec is not defined in the global scope when this function is called, attempting to iterate it will raise NameError.
    TypeError:
        - If _mutable_spec is not iterable, iterating it will raise TypeError.
        - If an individual typespec in _mutable_spec is not a valid second argument to isinstance (for example, a non-type, non-tuple), isinstance(obj, typespec) may raise TypeError.
        - If unsafe does not support membership testing (the "in" operator) in a way that accepts attr, the membership test may raise TypeError.
    Any exception propagated from custom __contains__ or isinstance implementations of types used in _mutable_spec.

## Constraints:
Preconditions:
    - The global variable _mutable_spec must exist prior to calling this function.
    - _mutable_spec must be an iterable of two-item entries: (typespec, unsafe).
        * typespec: a type or a tuple of types (or any object acceptable as the second argument to isinstance).
        * unsafe: any container supporting membership testing (in). Typical choices: set[str], tuple[str], list[str].
    - The order of entries in _mutable_spec defines priority: entries earlier in the iterable are consulted before later ones.
    - attr is expected to be the attribute name (a string); non-string attr values are allowed but membership semantics will follow the unsafe container.

Postconditions:
    - No mutation of obj or _mutable_spec is performed by this function.
    - The function will have returned True or False according to the first-match membership semantics described above.

## Side Effects:
    - None: the function performs read-only checks and membership tests only.
    - No I/O, no network calls, and no global state mutation are performed by the function itself.

## Control Flow:
flowchart TD
    Start([start]) --> Iterate{iterate entries in _mutable_spec?}
    Iterate --> |entry: (typespec, unsafe)| CheckType{isinstance(obj, typespec)?}
    CheckType --> |yes| CheckMember{is attr in unsafe?}
    CheckMember --> |yes| ReturnTrue([return True])
    CheckMember --> |no| ReturnFalse([return False])
    CheckType --> |no| Next([continue to next entry])
    Next --> Iterate
    Iterate --> |no more entries| ReturnFalseEnd([return False])

Important: the function returns as soon as it finds the first typespec that matches obj; it does not continue to scan later entries to see if attr might be present for them.

## Examples (realistic usage and expected outcomes):
Example specification (conceptual description):
- _mutable_spec is an ordered sequence with entries such as:
    - typespec: list, unsafe: a set of mutating attribute names like {"append", "extend", "clear"}
    - typespec: dict, unsafe: {"clear", "update", "setdefault"}
    - typespec: collections.deque, unsafe: {"append", "appendleft", "pop", "popleft"}

Evaluation scenarios (described step-by-step):
1. Given _mutable_spec as above, obj = [] (an instance of list), attr = "append":
    - The first entry's typespec (list) matches obj via isinstance.
    - "append" is a member of the unsafe set for that entry.
    - Result: True — the attribute is classified as known-mutable.
2. Given the same _mutable_spec, obj = [] and attr = "nonexistent":
    - list matches, but "nonexistent" not in unsafe set.
    - Result: False — returns immediately after the first matching typespec yields False.
3. obj is an instance matching multiple typespecs (e.g., a subclass of both A and B) and the first-matching entry in _mutable_spec for that object does not include attr:
    - The function returns False as soon as it checks the first matching entry; later entries are not consulted.
4. If _mutable_spec is missing or malformed:
    - Calling this function will raise NameError or TypeError as described in Raises; callers should ensure the specification is initialized and valid before invoking this check.

Integration guidance:
- Populate and order _mutable_spec in initialization code for the sandbox/security module, prioritizing more specific types before more general ones to ensure correct first-match behavior.
- When using custom classes as typespec entries, ensure they are valid for isinstance checks; when using custom unsafe containers, implement __contains__ to support expected membership behavior.
- Callers should handle NameError/TypeError if _mutable_spec may be uninitialized at runtime, or ensure safe module initialization order so _mutable_spec always exists before being used.

## `src.jinja2.sandbox.SandboxedEnvironment` · *class*

*No documentation generated.*

### `src.jinja2.sandbox.SandboxedEnvironment.__init__` · *method*

## Summary:
Initializes a sandboxed environment instance by delegating to the base Environment initializer, exposing a sandbox-safe range function to template globals, and creating instance-local copies of the operator tables used for unary and binary operations.

## Description:
- Known callers and context:
    - Instantiated whenever code wants a SandboxedEnvironment for template parsing/compilation/execution in a restricted (sandboxed) context. Typical callers are application code or framework components that configure Jinja2 environments before loading or rendering templates. This constructor runs during the environment creation/lifecycle setup step.
- Why this is its own method:
    - The constructor centralizes sandbox-specific initialization (injecting a safe range implementation into globals and making instance-local copies of operator tables). Keeping this separate from the base Environment initialization allows the sandbox variant to reuse Environment.__init__ behavior while layering sandbox-specific policy (safe_range) and per-instance operator tables without inlining or duplicating Environment logic.

## Args:
    *args (typing.Any): Positional arguments forwarded directly to the base Environment constructor. No interpretation is done by this method.
    **kwargs (typing.Any): Keyword arguments forwarded directly to the base Environment constructor.

## Returns:
    None

## Raises:
    - No exceptions are raised explicitly by this method body.
    - Propagated exceptions:
        - Any exception raised by Environment.__init__ (called via super().__init__(*args, **kwargs)) will propagate to the caller.
        - Attribute or type-related exceptions may propagate if the inherited attributes are not of the expected shape (for example, if self.default_binop_table or self.default_unop_table do not exist or do not implement copy(), the attribute access or method call will raise AttributeError or TypeError).

## State Changes:
- Attributes READ:
    - self.default_binop_table — read to obtain the default binary-operator table used as the template for the instance copy.
    - self.default_unop_table — read to obtain the default unary-operator table used as the template for the instance copy.
    - self.globals — read (implicitly) and then mutated via item assignment; assumed to exist after Environment.__init__.
- Attributes WRITTEN:
    - self.globals["range"] — the mapping entry for the key "range" is set to the sandbox-safe safe_range callable (overwrites any previous value for that key).
    - self.binop_table — set to a shallow copy of self.default_binop_table (result of calling .copy()) on the instance.
    - self.unop_table — set to a shallow copy of self.default_unop_table (result of calling .copy()) on the instance.

## Constraints:
- Preconditions:
    - Environment.__init__ must accept the provided *args and **kwargs and must set up self.globals (or otherwise ensure self.globals exists and is a mapping that supports item assignment).
    - self.default_binop_table and self.default_unop_table must exist (typically as class-level attributes inherited from the base class or defined on this class) and must implement a .copy() method (i.e., be mapping-like or have a copy() that returns a shallow copy).
- Postconditions:
    - After successful return:
        - self.globals contains an item keyed by "range" whose value is the safe_range callable (the sandbox-safe wrapper around Python's range).
        - self.binop_table is an independent shallow copy of the default binary-operator table (mutating self.binop_table will not change the class-level default table object).
        - self.unop_table is an independent shallow copy of the default unary-operator table.

## Side Effects:
    - Calls Environment.__init__(*args, **kwargs) which may perform additional initialization and side effects defined by the base class.
    - Mutates the instance mapping self.globals by setting the "range" key.
    - Creates new objects (the results of .copy()) and assigns them to self.binop_table and self.unop_table; these are shallow copies — any mutable values inside those tables remain shared unless the underlying copy implementations perform deep copy (the code calls .copy(), so the copy semantics depend on that implementation).
    - References the safe_range function (no I/O or external calls are made by this method itself).

### `src.jinja2.sandbox.SandboxedEnvironment.is_safe_attribute` · *method*

## Summary:
Determines whether accessing a given attribute on an object is permitted by the sandbox policy; returns True when the attribute lookup is allowed and False when it must be blocked.

## Description:
This method encapsulates the sandbox's attribute-safety check used during template attribute resolution. It is invoked during rendering when the sandbox must decide whether to allow obj.attr to be accessed. The method implements a simple two-part policy:
1) Deny any attribute whose name starts with an underscore (leading underscore(s) are considered unsafe).
2) Defer to the module-level is_internal_attribute(obj, attr) predicate for type-specific and dunder checks; deny when that predicate indicates the attribute is internal/unsafe.

Known callers and lifecycle stage:
- SandboxedEnvironment.getattr: called when resolving direct attribute access (obj.attribute) during template rendering.
- SandboxedEnvironment.getitem: called when a string key lookup falls back to attribute access (e.g., obj["name"] falling back to obj.name) during template rendering.
- ImmutableSandboxedEnvironment and other sandbox variants may override or call this method to extend or refine safety rules.

Why this is a separate method:
- Centralizes the sandbox attribute policy in one overrideable place so different sandbox variants (e.g., immutable sandbox) can reuse or extend the base checks without duplicating logic. It also keeps attribute-safety semantics explicit and testable, and separates low-level type-specific checks (is_internal_attribute) from the general underscore-based rule.

## Args:
    obj (t.Any):
        The object whose attribute is being accessed. Any Python object is acceptable; the object is only inspected (no mutation).
    attr (str):
        The attribute name to check. Expected to be a string identifier. The implementation calls attr.startswith("_"), so callers should pass a string (or an object with an appropriate startswith method) to avoid exceptions.
    value (t.Any):
        The attribute's value as obtained by getattr(obj, attr) (or the candidate value). In this base implementation the parameter is not inspected; it is provided to allow overrides (subclasses) to make safety decisions based on the value.

## Returns:
    bool:
        - True: attribute access is allowed (attr does not start with "_" and is_internal_attribute(obj, attr) returns False).
        - False: attribute access is denied (either attr starts with "_" or is_internal_attribute(obj, attr) returns True).

Edge-case returns:
- The method returns a strict boolean; it does not return Undefined or raise SecurityError by itself. Callers use the boolean to either return the value or produce an unsafe/undefined sentinel or raise SecurityError.

## Raises:
    AttributeError:
        If attr does not provide a startswith method (for example, when attr is None or an object lacking startswith), attr.startswith("_") may raise AttributeError which will propagate.
    TypeError:
        If attr is of a type that causes a TypeError when used in is_internal_attribute's membership checks or when attr.startswith is invoked with incompatible arguments, that TypeError may propagate.
    NameError:
        If the module-level is_internal_attribute implementation expects certain UNSAFE_* constants that are not defined at runtime, the call to is_internal_attribute(obj, attr) may raise NameError which will propagate.

Note:
- This method itself does not raise SecurityError; instead, callers typically check the returned boolean and raise SecurityError or return an unsafe/undefined sentinel.

## State Changes:
Attributes READ:
    - None on self. The method does not read any self.<attr> fields.
Attributes WRITTEN:
    - None. The method does not modify attributes on self.

## Constraints:
Preconditions:
    - attr should normally be a str (or at least provide startswith("_")).
    - The sandbox module must provide the is_internal_attribute function and any module-level constants it uses; otherwise NameError may occur during the call.

Postconditions:
    - No mutation of obj, value, or self.
    - Deterministic decision: given the same obj, attr, and the same definitions of is_internal_attribute and module constants, the method returns the same boolean.

## Side Effects:
    - None: the method performs only pure inspection and boolean logic. It performs no I/O, network access, or mutation of external objects.

### `src.jinja2.sandbox.SandboxedEnvironment.is_safe_callable` · *method*

## Summary:
Performs the sandbox safety check for a potential callable: returns True if the object is allowed to be called under sandbox policy, without modifying the environment or the object.

## Description:
This method is invoked during template evaluation immediately before the environment attempts to call a value coming from template code. Known caller:
- SandboxedEnvironment.call — used in the call pipeline to decide whether an arbitrary object may be invoked from within a template.

Purpose and rationale for being a separate method:
- Centralizes the sandbox policy for callability in one place so the rule is easy to read, test, and override in subclasses.
- Allows different sandboxing policies to be implemented by subclassing or monkey-patching this single method instead of scattering checks across call sites.

## Args:
    obj (typing.Any): The object to be tested for safe invocation. Can be any Python object; attribute access is performed with getattr and therefore may run object-specific descriptor or property code.

## Returns:
    bool: 
        - True if the object is considered safe to call (neither attribute "unsafe_callable" nor "alters_data" exists with a truthy value).
        - False if either getattr(obj, "unsafe_callable", False) or getattr(obj, "alters_data", False) yields a truthy value.
        - Note: missing attributes evaluate to False because getattr uses the provided default (False).

## Raises:
    Any exception raised during attribute lookup on obj (for example, exceptions raised by a property, descriptor, or __getattr__ implementation) will propagate out of this method. The method itself does not raise SecurityError; callers (e.g., SandboxedEnvironment.call) may raise SecurityError based on the returned boolean.

## State Changes:
    Attributes READ:
        - None on self (this method does not read any self.<attr> attributes)
    Attributes WRITTEN:
        - None (this method does not modify self or obj)

## Constraints:
    Preconditions:
        - None required on self; obj may be any object. Be aware that attribute access (getattr) may execute arbitrary code on obj.
    Postconditions:
        - The method returns a boolean that reflects the truthiness of obj.unsafe_callable and obj.alters_data as described above.
        - No mutation of self or obj is performed by this method itself.

## Side Effects:
    - No I/O or external service calls are made by this method.
    - The only side effects that can occur are side effects produced by attribute access on obj (via getattr). If obj defines properties, descriptors, or __getattr__ with side effects, those will run when this method checks the attributes.

### `src.jinja2.sandbox.SandboxedEnvironment.call_binop` · *method*

## Summary:
Look up the callable for a binary operator in the environment's operator table and invoke it with the given left and right operands. This dispatch does not modify the environment's state.

## Description:
Performs a direct dispatch for binary expressions inside the sandbox: it retrieves a callable from self.binop_table using the operator string and calls that callable with (left, right). The method accepts the rendering Context for API symmetry but does not use it.

Known callers and context:
- No direct callers are present in the provided code snapshot. Conceptually, this method is called by the template expression evaluation stage (the runtime/AST evaluator) when a binary expression (for example, a + b) is evaluated during template rendering.
- Keeping this behavior in a dedicated method lets the sandbox control or replace operator semantics by changing self.binop_table without modifying the expression evaluator.

Why this is its own method:
- Centralizes binary operator dispatch into a single override point for sandboxing: the sandbox can customize allowed operators or their implementations by altering binop_table.
- Separates evaluation concerns (parsing/AST handling) from operator semantics, simplifying testing and customization.

## Args:
    context (Context):
        The current rendering context object. Type: runtime.Context.
        Note: not used by this implementation (accepted for API consistency and possible future hooks).
    operator (str):
        A string key naming the operator to perform (e.g., "+", "-", "*", "/", "//", "**", "%").
        Valid values depend on the keys present in self.binop_table. The class defines a default mapping (default_binop_table) containing the keys:
        "+", "-", "*", "/", "//", "**", "%"
    left (Any):
        Left operand passed to the operator callable.
    right (Any):
        Right operand passed to the operator callable.

## Returns:
    Any:
        The direct result of calling the callable found at self.binop_table[operator] with (left, right). The precise type and semantics are determined by that callable (for defaults, these are the behaviors of the corresponding Python operator functions).

## Raises:
    KeyError:
        If operator is not present as a key in self.binop_table. The dict lookup self.binop_table[operator] raises this error.
    Any exception raised by the operator callable:
        The callable is invoked directly; any exception it raises (for example, TypeError for unsupported operand types, ZeroDivisionError for division by zero, etc.) is propagated unchanged to the caller.

## State Changes:
Attributes READ:
    self.binop_table

Attributes WRITTEN:
    None — the method performs no writes to self or other attributes.

## Constraints:
Preconditions:
    - self.binop_table must be a mapping type that supports key lookup (e.g., dict).
    - operator must be a key in that mapping; otherwise a KeyError will occur.
    - The left and right operands must be valid inputs for the callable stored under that key (type and semantics are determined by that callable).

Postconditions:
    - No attributes of the SandboxedEnvironment instance are modified.
    - The returned value equals the returned value of the operator callable, or an exception is raised and propagated.

## Side Effects:
    - The method itself performs no I/O and does not alter global state.
    - If the callable stored in self.binop_table performs side effects (mutating objects, I/O, etc.), those side effects will occur because the callable executes in the caller's process.

## Examples:
    - Using the default table (conceptual, not actual runtime snippet):
        result = env.call_binop(context, "+", 2, 3)
        # result == 5

    - Installing a custom operator (shows how to customize semantics; be aware of security implications):
        def concat_as_str(a, b):
            return str(a) + str(b)
        env.binop_table["++"] = concat_as_str
        result = env.call_binop(context, "++", "a", 1)
        # result == "a1"

    - Handling missing operator:
        try:
            env.call_binop(context, "@", 1, 2)
        except KeyError:
            # operator not allowed/defined in this sandbox
            pass

Security note:
    Replacing or adding callables in self.binop_table changes what operations templates can perform. The sandbox does not automatically re-check safety of custom callables; if you install untrusted callables they may perform arbitrary actions or side effects.

### `src.jinja2.sandbox.SandboxedEnvironment.call_unop` · *method*

## Summary:
Lookup and execute a unary operator callable from the environment's unary operator table and return its result; the environment object is not modified.

## Description:
This method performs a direct dispatch: it looks up operator in self.unop_table and calls the retrieved callable with the single operand arg. The implementation is intentionally minimal so the environment controls operator semantics via the unop_table mapping.

Intended callers and invocation context:
- Template expression evaluation code that needs to apply unary operators during rendering (the evaluator itself is not present in this file).
- Test or extension code that wants to apply the environment's configured unary operators programmatically.

Why this is a separate method:
- Centralizes operator dispatch so different environments can replace or extend unary operator behavior by replacing or mutating self.unop_table or by overriding this method.
- Keeps the expression-evaluation logic independent of the mechanism used to resolve and invoke operators.

Notes from the class context:
- The class defines default_unop_table with the keys "+" and "-" mapped to operator.pos and operator.neg.
- In __init__, unop_table is initialized as a copy of default_unop_table.
- This method does not consult intercepted_unops or perform additional security checks; it performs only the lookup and call.

## Args:
    context (Context):
        The rendering evaluation context passed by callers. This parameter is accepted for API symmetry with other call_* methods but is not used by this implementation.
    operator (str):
        Operator key to look up in self.unop_table. Default environment keys include "+" and "-"; any string present in self.unop_table is valid.
    arg (t.Any):
        The operand to pass to the operator callable. No type coercion is performed here; the callable determines accepted types.

## Returns:
    t.Any:
        The direct return value from the operator callable invoked as self.unop_table[operator](arg). The result may be any Python object the callable chooses to return (numbers, Undefined sentinel, custom objects, etc).

    Edge-case returns:
    - If the operator callable returns a framework-specific sentinel (for example Undefined), that value is returned unchanged.

## Raises:
    KeyError:
        If operator is not present in self.unop_table, the dictionary lookup self.unop_table[operator] raises KeyError.
    Any exception raised by the operator callable:
        Exceptions raised by the callable (TypeError for unsupported operand types, user-defined exceptions, etc.) propagate unchanged.

## State Changes:
    Attributes READ:
        self.unop_table
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
    - self.unop_table must be a mapping from strings to single-argument callables (this is ensured in __init__ where unop_table is copied from default_unop_table).
    - operator should be a key in self.unop_table to avoid KeyError.
    - The caller must supply an arg acceptable to the operator callable.

    Postconditions:
    - self is not modified by this call.
    - The returned value equals the operator callable's return value for the given arg, or an exception is raised.

## Side Effects:
    - The method itself performs no I/O and does not call external services.
    - Any side effects originate from the operator callable (for example, mutating arg or other global state); such effects are not prevented or wrapped by this method.

## Usage (prose example):
- To add a custom unary operator, a caller can update env.unop_table with a new key mapping to a single-argument callable; subsequent calls to call_unop with that operator key will invoke the provided callable.

### `src.jinja2.sandbox.SandboxedEnvironment.getitem` · *method*

## Summary:
Resolve a subscript access (obj[argument]) inside the sandboxed environment: return the subscript result if available, otherwise try a string-to-attribute fallback and enforce sandbox safety, returning either the discovered value or an Undefined placeholder without mutating environment state.

## Description:
This method is the centralized implementation for evaluating a template-level subscript expression (the equivalent of Python's obj[argument]) when rendering in a SandboxedEnvironment. Typical runtime usage is during template expression evaluation at render time whenever a template contains a subscript access (for example, foo[bar]).

Behavior is split into three phases:
1. Try obj[argument] and return the result if the operation succeeds.
2. If the subscript access fails with TypeError or LookupError and the argument is a string, attempt an attribute lookup using str(argument) → getattr(obj, attr). If that attribute exists and is considered safe per the sandbox policy, return it; if it exists but is unsafe, return an Undefined produced by unsafe_undefined.
3. If none of the above succeed, return the environment's undefined(...) for the attempted access.

This logic is implemented as its own method to centralize sandbox-specific rules for subscript/attribute access, to provide the attribute-fallback behavior consistently across the sandboxed environment, and to keep security checks (is_safe_attribute, unsafe_undefined, undefined) in one location rather than inlining them at each call site.

## Known callers / invocation context:
- Template expression evaluator at render time when a template performs a subscript access (obj[key]). This method is the environment-level hook used to resolve that access in a sandbox-aware way.
- It is conceptually paired with SandboxedEnvironment.getattr which implements the complementary attribute-first lookup.

## Args:
    self: SandboxedEnvironment instance (implicit).
    obj (Any): The target object to subscript or inspect. Can be any Python object.
    argument (Union[str, Any]): The subscript key/index. If a string, the method may fall back to attribute lookup using str(argument).

## Returns:
    Union[Any, Undefined]:
    - If obj[argument] succeeds, returns the result of that operation (any Python value).
    - If obj[argument] fails with TypeError or LookupError and argument is a string and getattr(obj, str(argument)) finds a valid attribute that is allowed by is_safe_attribute, returns that attribute value.
    - If the attribute exists but is considered unsafe by is_safe_attribute, returns the value produced by unsafe_undefined(obj, argument) (an Undefined instance that indicates an unsafe access; unsafe_undefined delegates to undefined(...) with exc=SecurityError).
    - If no subscript or attribute is found, returns self.undefined(obj=obj, name=argument) (an Undefined instance representing a missing value).
    - Note: The return type is therefore either a concrete Python value or an Undefined object imported from runtime.Undefined.

## Raises:
    - This method does not explicitly raise for missing lookups because missing results are represented by Undefined.
    - Exceptions from the underlying operations may propagate:
        * Exceptions other than TypeError or LookupError raised by obj[argument] will propagate unchanged (they are not caught by the method).
        * Exceptions other than AttributeError raised during getattr(obj, attr) (for example, if a property getter raises ValueError) will propagate unchanged.
    - Attempting to subscript with an unhashable or otherwise invalid key may result in exceptions from the object's __getitem__, and those exceptions will propagate unless they are TypeError or LookupError (which are handled as lookup failures).

## State Changes:
    Attributes READ:
        - self.is_safe_attribute (method is called to decide attribute safety)
        - self.unsafe_undefined (method is called to produce an unsafe Undefined)
        - self.undefined (method is called to produce a default Undefined for missing access)
    Attributes WRITTEN:
        - None. The method does not modify attributes on self.

## Constraints:
    Preconditions:
        - No strict preconditions enforced by this method, but callers should expect that obj may be any Python object and argument may be any value. If callers expect no exceptions to escape, they must ensure obj[argument] and attribute access do not raise unexpected exceptions (only TypeError and LookupError are caught for subscript).
    Postconditions:
        - The method will either return a concrete value from the object or return an Undefined instance representing either "missing" or "unsafe" access.
        - The environment and the provided obj are not mutated by this method (aside from any side effects performed by executed attribute/property code inside getattr or __getitem__).

## Edge cases and notable details:
    - Only TypeError and LookupError raised by obj[argument] are interpreted as "lookup failed" and cause the attribute-fallback logic to run. Any other exception from obj[argument] is treated as a real error and will propagate.
    - When falling back to attribute access, the code first attempts str(argument). If str(argument) raises any exception, that conversion is suppressed and attribute lookup is skipped.
    - getattr(obj, attr) is caught only for AttributeError. If the attribute exists but retrieving it raises another exception (e.g., a property raises ValueError), that exception will propagate.
    - Attribute safety is determined by is_safe_attribute(obj, attribute, value). In this environment, is_safe_attribute returns False for names that start with "_" or for internal attributes (see is_internal_attribute), so such attributes result in unsafe_undefined(...) rather than returning the real value.
    - unsafe_undefined(...) calls undefined(...) with exc=SecurityError; the resulting Undefined typically encodes that the attempted access was disallowed for security reasons.
    - This method does not perform any I/O itself, but attribute access (via property getters or __getitem__) may execute arbitrary user code and therefore may have side effects or perform I/O indirectly.

## Side Effects:
    - No direct I/O or global mutations are performed by this method.
    - Indirect side effects: executing obj.__getitem__(argument) or evaluating a property during getattr(obj, attr) may run arbitrary user code, which can produce side effects (mutations, I/O, exceptions). These effects originate from the target object, not from the method itself.

### `src.jinja2.sandbox.SandboxedEnvironment.getattr` · *method*

## Summary:
Lookup an attribute on an object in a sandbox-aware way: return the attribute value when accessible and allowed, otherwise return an environment-provided undefined/unsafe marker without mutating the environment.

## Description:
This method encapsulates how attribute access is performed inside a sandboxed environment during template rendering. Typical callers are the template expression evaluator and runtime attribute/variable resolution code that evaluate expressions like obj.attr or the equivalent attribute lookup performed by the template engine when rendering templates. It runs at evaluation time (during template rendering) whenever the engine needs to resolve an attribute on an object.

It exists as a separate method to centralize sandbox-specific rules for attribute access:
- ensure a uniform fallback to mapping-style access (obj[attribute]) when normal attribute lookup fails with AttributeError,
- apply sandbox safety checks via is_safe_attribute, and
- delegate to environment-specific undefined/unsafe handlers (undefined and unsafe_undefined) for missing or disallowed attributes.

Keeping this logic in its own method ensures the checks and fallbacks are applied consistently across all attribute lookups and makes it easy to override or customize sandbox behavior in subclasses.

## Args:
    obj (typing.Any): The object on which to perform attribute lookup. Can be any Python value (object, mapping, sequence, etc.). There is no automatic type coercion.
    attribute (str): The attribute name to resolve. Must be a string.

## Returns:
    typing.Union[typing.Any, Undefined]:
    - If normal attribute access (built-in getattr) succeeds and the attribute is considered safe by is_safe_attribute, the raw attribute value is returned.
    - If normal attribute access succeeds but is_safe_attribute returns False, the method returns whatever self.unsafe_undefined(obj, attribute) returns (often an Undefined marker or raises, depending on the environment implementation).
    - If normal attribute access raises AttributeError and obj supports item access (obj[attribute]) that succeeds, the item value is returned.
    - If both attribute access and item access fail (AttributeError from getattr and either TypeError or LookupError from obj[attribute]), the method returns the result of self.undefined(obj=obj, name=attribute).

Edge returns:
- The returned value can be any Python value provided by the underlying object (including callables, descriptors, descriptors' results, or Undefined-like sentinel values returned by the environment methods).
- If the attribute getter or the obj[attribute] lookup raises exceptions other than AttributeError, TypeError, or LookupError, those exceptions propagate unchanged.

## Raises:
    Any exception raised by the attribute access or item lookup that is not explicitly handled:
    - Exceptions raised from property descriptors, custom __getattr__/__getattribute__ implementations, or from obj[attribute] other than TypeError or LookupError will propagate to the caller.
    - The method itself does not raise SecurityError directly, but delegated methods (unsafe_undefined/undefined) could raise based on environment implementation.

## State Changes:
Attributes READ:
    - self.is_safe_attribute (method): queried to decide whether a found attribute is permitted.
    - self.unsafe_undefined (method): called if an attribute is present but considered unsafe.
    - self.undefined (method): called when attribute and mapping access both fail.

Attributes WRITTEN:
    - None. This method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
    - attribute must be a string (the method signature and typical callers assume this).
    - obj may be any Python object; callers should expect that some objects may raise on attribute access or indexing.

Postconditions:
    - If attribute exists via getattr and is_safe_attribute returns True, the returned value is the object's attribute value.
    - If attribute exists but is_safe_attribute returns False, the returned value equals self.unsafe_undefined(obj, attribute).
    - If attribute does not exist but obj[attribute] succeeds, the returned value is that item value.
    - If neither lookup succeeds, the returned value equals self.undefined(obj=obj, name=attribute).
    - No attributes on self are modified.

## Side Effects:
    - The method may execute descriptor code, property getters, or __getattribute__/__getattr__ logic when performing getattr(obj, attribute), and those may have arbitrary side effects external to the environment (I/O, mutation of obj, database calls, etc.). Such side effects are not suppressed by this method.
    - Calling obj[attribute] may run __getitem__ and can also have side effects or raise exceptions.
    - The method calls instance methods on self (is_safe_attribute, unsafe_undefined, undefined); side effects depend on their implementations.

### `src.jinja2.sandbox.SandboxedEnvironment.unsafe_undefined` · *method*

## Summary:
Create and return an Undefined sentinel representing an unsafe attribute access, delegating to the environment's undefined factory and attaching SecurityError as the exception type.

## Description:
This helper encapsulates the logic used when the sandbox prevents access to an attribute on an object. It is invoked by attribute/item access paths in the sandboxed environment (notably SandboxedEnvironment.getattr and SandboxedEnvironment.getitem) when an attribute exists but the environment deems it unsafe to expose.

Callers and context:
- SandboxedEnvironment.getattr: called when getattr succeeds but is deemed unsafe by is_safe_attribute.
- SandboxedEnvironment.getitem: called when item access yields an attribute value but is deemed unsafe by is_safe_attribute.
These calls occur at runtime during template evaluation when resolving names or indexes in a sandboxed template execution pipeline.

Reason for being a separate method:
- Centralizes the creation of a consistent Undefined object and error message for unsafe attribute accesses.
- Makes subclassing or overriding the sandbox's behavior easier by providing a single extension point.
- Keeps getattr/getitem focused on lookup logic and safety checks rather than construction of the undefined sentinel.

## Args:
    obj (Any): The target object whose attribute access was attempted. Used only for diagnostic metadata forwarded to the undefined factory.
    attribute (str): The attribute name that was accessed and deemed unsafe. Must be a string (caller code in the sandbox guarantees this).

## Returns:
    Undefined: The object returned is the result of calling self.undefined(...). The call is made with:
        - a human-readable message: "access to attribute 'attribute' of 'TypeName' object is unsafe."
        - name set to the attribute value
        - obj set to the provided obj
        - exc set to the SecurityError class
    Edge cases:
        - If self.undefined itself raises or returns something unusual, that behavior is propagated to the caller (unsafe_undefined does not wrap or transform the result).

## Raises:
    Any exception raised by self.undefined: unsafe_undefined does not raise new exceptions on its own; it simply returns whatever self.undefined produces or propagates exceptions raised by that call.
    (Notably, SecurityError is not raised here — it is passed as the exc parameter to the undefined factory. Whether that results in an actual raise depends on the environment.undefined implementation.)

## State Changes:
    Attributes READ:
        - self.undefined (method/property) — invoked to produce the Undefined object.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - attribute must be a string (the method signature enforces typing; callers in SandboxedEnvironment pass strings).
        - self.undefined must be a callable/factory that accepts the provided keyword arguments (message, name, obj, exc).
    Postconditions:
        - On successful return, the caller receives the value returned by self.undefined configured with the provided message and metadata (name, obj, exc=SecurityError).
        - No mutation of the SandboxedEnvironment instance occurs as a result of this call.

## Side Effects:
    - Calls into self.undefined; any side effects of that factory call (logging, state mutation, raising an exception) are possible and will be observed by the caller.
    - No I/O or external service calls are made directly by unsafe_undefined itself.

### `src.jinja2.sandbox.SandboxedEnvironment.format_string` · *method*

## Summary:
Format a string-like object using a sandbox-aware Formatter and return a new string-like instance of the same type as the input.

## Description:
This method centralizes format-string rendering for the sandboxed environment. It chooses a formatter that enforces sandbox lookups (and, when given a Markup input, Markup-aware escaping) and then delegates to the Formatter.vformat implementation to perform actual field resolution and formatting.

Known callers and call context:
- SandboxedEnvironment.call: when an object with a format-like method is invoked from template code, call() inspects the object for a format method and forwards that method plus the call arguments to format_string. In that pipeline this method runs during template evaluation when a template attempts to format values (for example when calling "{:...}".format-like operations on objects exposed to templates).
- Template rendering code and other environment utilities that need to render/format strings while enforcing sandbox rules and preserving Markup safety.
- Rationale for being a separate method: it encapsulates the logic that (1) selects the correct Formatter class for sandboxed resolution and Markup-aware escaping, (2) adapts the special-case behavior for format_map, and (3) ensures the return value has the same concrete string-like type as the input. Keeping this logic in its own method avoids duplicating the Markup/format_map handling in multiple call sites and centralizes the place where sandboxed formatting semantics are applied.

## Args:
    self: SandboxedEnvironment
    s (str): The format string or Markup-like object to render. If s is an instance of markupsafe.Markup the method will choose a Markup-aware EscapeFormatter so that already-safe values are preserved and other strings are escaped.
    args (tuple[Any, ...]): Positional arguments to pass to the formatter, typically the arguments provided to a format() call.
    kwargs (dict[str, Any]): Keyword mapping passed to the formatter, typically the keyword arguments provided to a format() call.
    format_func (Optional[Callable]): Optional callable representing the format method being invoked (for example, the bound method object when called via an object's format method). If provided and its __name__ equals "format_map", method applies the special format_map semantics (see Raises and behavior below).

## Returns:
    str (or Markup-like): Returns a new instance of the same concrete type as s (constructed via type(s)(rv)) containing the rendered result. For plain str input this is a str; for markupsafe.Markup input this is a Markup preserving its type behavior.

    Edge cases:
    - If the Formatter produces a value that cannot be used to construct type(s), that constructor may raise; that exception propagates to the caller.
    - When s is a Markup instance the method returns type(s)(rv) where rv is the string produced by the underlying formatter; EscapeFormatter semantics apply during formatting (plain strings are escaped, Markup instances are preserved).

## Raises:
    TypeError: If format_func is provided and format_func.__name__ == "format_map" and the supplied args/kwargs do not match expected signature: specifically, if len(args) != 1 or kwargs is not empty, the method raises TypeError with message:
        "format_map() takes exactly one argument {N} given"
    where N is computed as len(args) + (kwargs is not None) in the implementation.

    SecurityError: Any security violations raised by the sandboxing Environment during field resolution (for example, if Environment.getattr or Environment.getitem disallow access) will propagate as SecurityError or as the Environment-chosen Undefined/exception types.

    AttributeError: Accessing format_func.__name__ will raise AttributeError if format_func is an object that does not have a __name__ attribute; that exception propagates.

    Other exceptions propagated from the underlying formatter.vformat call:
    - KeyError, IndexError, ValueError, LookupError, TypeError, or other exceptions that originate from the format string processing, get_value resolution, conversion and formatting steps, or the Environment methods used during lookup.

## State Changes:
    Attributes READ:
        - None of self's individual attributes are directly read or mutated by this method. The method passes self to the constructed formatter so that subsequent formatting operations (Formatter.vformat) may use the Environment through the formatter, but format_string itself does not access self.<attr>.

    Attributes WRITTEN:
        - None. The method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - s must be a string-like object (commonly a str or markupsafe.Markup). If s is Markup the method expects that s has an .escape attribute (as markupsafe.Markup does).
        - args should be a tuple of positional arguments (the code treats it as a sequence and uses len and indexing).
        - kwargs should be a mapping/dict (the code expects to test truthiness and pass it to vformat).
        - If format_func is used to denote a "format_map" call it must (by convention) have a __name__ attribute equal to "format_map". The caller is responsible for providing format_func correctly.

    Postconditions:
        - No mutation to the SandboxedEnvironment instance is performed.
        - The method returns a newly constructed instance of type(s) initialized with the formatted string content.
        - The formatted output has been produced by a SandboxedFormatter (or SandboxedEscapeFormatter when s is Markup), therefore all attribute/item lookups performed during formatting have been mediated by the Environment (and may have raised security exceptions).

## Side Effects:
    - Invokes the Formatter.vformat pipeline on the chosen formatter object. That pipeline will:
        - Parse the format string and attempt to resolve replacement fields.
        - For each attribute or item access encountered during field resolution, call into the provided Environment's getattr/getitem methods (via SandboxedFormatter/SandboxedEscapeFormatter). Those calls can have side effects defined by Environment (e.g., raising SecurityError, returning an Undefined sentinel, or performing allowed lookups).
        - When s is Markup, use EscapeFormatter semantics to escape values or preserve Markup instances; escaping may call conversion methods on inserted values (which can have further side effects if those objects define __str__/__format__ with side effects).
    - No I/O or external service calls originate from format_string itself; any side effects originate from objects and Environment methods invoked during formatting and from constructor/type(s)(rv) when building the returned object.

### `src.jinja2.sandbox.SandboxedEnvironment.call` · *method*

## Summary:
Performs a sandbox-aware invocation of a callable value: it special-cases bound string-format methods, enforces the environment's callable-safety policy for other callables, delegates execution to the rendering Context, and does not mutate the SandboxedEnvironment's state.

## Description:
This method is the centralized, sandbox-aware entry point for invoking callables encountered during template evaluation. It performs two concise responsibilities:
- Detects bound str.format/format_map methods and routes them through the environment's controlled formatting path.
- For non-format callables, enforces the sandbox safety policy before delegating the actual invocation to the rendering Context.

Typical callers and invocation context:
- Typically invoked by the template rendering/evaluation machinery when a template expression requires calling a callable (for example, calling a function, macro, or a callable object).
- This occurs during the rendering phase where a Context instance and the callable value are available.
- Note: those callers are typical usage contexts; they are not explicitly declared within this function's source body.

Why this is a separate method:
- Encapsulates sandbox-specific decision points (format-method detection and safety enforcement) so that call sites need not duplicate this logic.
- Keeps special handling for string formatting isolated and easily overridable by overriding format_string or is_safe_callable.

## Args:
    __self (SandboxedEnvironment): The sandboxed environment instance.
    __context (Context): Rendering context object; must provide a call(callable_obj, *args, **kwargs) method.
    __obj (t.Any): The object to be invoked. May be a bound string-format method, a function, a callable object, or any value that might be callable.
    *args (t.Any): Positional arguments forwarded to the callable.
    **kwargs (t.Any): Keyword arguments forwarded to the callable.

(Types mirror the function signature; varargs and kwargs are passed through unchanged.)

## Returns:
    t.Any:
    - If inspect_format_method(__obj) returns a string fmt, the return value is whatever self.format_string(fmt, args, kwargs, __obj) returns (commonly a string or Markup).
    - Otherwise, if the callable is allowed, returns whatever __context.call(__obj, *args, **kwargs) returns.
    - Any return value from the delegated methods is propagated as-is. If delegated calls return None, None is returned.

## Raises:
    SecurityError:
        - Raised with the exact message f"{__obj!r} is not safely callable" when:
            * inspect_format_method(__obj) is None (no special format handling), and
            * self.is_safe_callable(__obj) evaluates to false.
    Other exceptions:
        - Any exception raised by self.format_string(...) or __context.call(...) (including TypeError, ValueError, or exceptions thrown by the target callable) is not caught here and will propagate to the caller.

## State Changes:
Attributes READ (self):
    - self.format_string: invoked when a bound string-format method is detected.
    - self.is_safe_callable: consulted to decide whether to allow invocation of a non-format callable.

Module-level / external reads:
    - inspect_format_method (module-level helper): called with __obj to detect whether __obj is a bound str.format/format_map method.
    - __context.call: invoked to perform the actual callable execution when allowed.

Attributes WRITTEN:
    - None. This method performs no assignments to self.<attr> or other module-level state.

## Constraints:
Preconditions:
    - __context must implement a call(callable_obj, *args, **kwargs) method.
    - self must provide:
        * format_string(fmt: str, args: tuple, kwargs: dict, original_callable: Any) -> Any
        * is_safe_callable(callable_obj: Any) -> bool
    - inspect_format_method must be available and must return either a str (format template) or None.

Postconditions:
    - No mutation of self or module-level state is performed.
    - If the method returns normally, the value is the direct result from either self.format_string(...) or __context.call(...).
    - If a SecurityError is raised, the target callable is not invoked via __context.call.

## Side Effects:
    - Delegated invocation side effects: When __context.call(...) runs, that call may perform arbitrary side effects (I/O, state mutation, user code execution) depending on the target callable. Those effects are not controlled by this method beyond the safety gate.
    - Format path side effects: self.format_string(...) may produce Markup or perform escaping/transformations; any side effects from that method will propagate.
    - This method itself performs no I/O, network, or filesystem operations.

## Implementation notes / reimplementation hints:
    - Call inspect_format_method(__obj); if it returns a str fmt, return self.format_string(fmt, args, kwargs, __obj).
    - If inspect_format_method returns None, evaluate self.is_safe_callable(__obj). If falsey, raise SecurityError(f"{__obj!r} is not safely callable").
    - If allowed, return __context.call(__obj, *args, **kwargs).
    - Do not call __obj directly for non-format cases; routing through __context.call ensures the Context can mediate or wrap the invocation.

## `src.jinja2.sandbox.ImmutableSandboxedEnvironment` · *class*

## Summary:
ImmutableSandboxedEnvironment is a Sandbox environment subclass that strengthens attribute-safety checks by denying access to attributes identified as known mutating/unsafe; it only permits an attribute if the parent sandbox allows it and the attribute is not in the known-mutable specification.

## Description:
This class is a thin specialization of SandboxedEnvironment whose sole responsibility is to make attribute access stricter: when an attribute access is being validated, ImmutableSandboxedEnvironment defers first to the parent sandbox rule and then consults a central policy of "known mutable" attributes. Typical callers are template rendering code and sandbox initialization/factory functions that construct environment instances for rendering untrusted templates. Instantiate this class when you need the sandbox to disallow access to attributes that could mutate objects (for example, list.append, dict.update) even if the general sandbox policy would otherwise permit them.

Motivation and responsibility boundary:
- Motivation: prevent templates from obtaining attribute access that could be used to mutate objects or produce side effects, by combining the parent sandbox's generic safety policy with a centralized known-mutable attribute policy.
- Boundary: this class does not change any behavior other than attribute-safety checks. It does not add new state, alter rendering semantics, or change resolving/lookup strategies beyond the attribute-safety decision.

## State:
- New attributes: None. ImmutableSandboxedEnvironment defines no additional instance attributes.
- Inherited state: All instance attributes, configuration, and constructor parameters are inherited unchanged from SandboxedEnvironment (constructor signature and state are defined by the parent).
- Internal dependencies:
    - modifies_known_mutable (global utility): consulted to determine whether a given (obj, attr) pair is classified as a known-mutable/unsafe attribute. See its documentation for the matching and exception semantics.
    - super().is_safe_attribute(...) (SandboxedEnvironment implementation): consulted first; if it returns False, ImmutableSandboxedEnvironment immediately returns False.
- Important invariants:
    - For any call (obj, attr, value) to is_safe_attribute:
        * If the parent sandbox's is_safe_attribute returns False, ImmutableSandboxedEnvironment returns False.
        * Otherwise, if modifies_known_mutable(obj, attr) returns True, ImmutableSandboxedEnvironment returns False.
        * Otherwise, ImmutableSandboxedEnvironment returns True.
    - The class does not mutate obj or global mutable specification(s); its checks are read-only.

For __init__ parameters:
- There are no new __init__ parameters introduced by this class. Callers must use the same constructor arguments and conventions as SandboxedEnvironment. Any constraints on those parameters are those imposed by SandboxedEnvironment.

## Lifecycle:
- Creation:
    - Instantiate using the same constructor and factory mechanisms as SandboxedEnvironment (no additional required or optional parameters introduced).
    - No special initialization steps are required by this subclass.
- Typical usage:
    - The runtime/template engine calls is_safe_attribute(obj, attr, value) at attribute-access decision points.
    - Sequence for each attribute check:
        1. Call parent: parent_allowed = super().is_safe_attribute(obj, attr, value)
        2. If not parent_allowed: deny access (return False)
        3. Else consult modifies_known_mutable(obj, attr)
        4. If modifies_known_mutable returns True: deny access (return False)
        5. Otherwise: allow access (return True)
    - There is no required ordering of other API calls beyond the expectation that the environment is constructed before any attribute checks occur.
- Destruction / cleanup:
    - No special cleanup; follows parent environment lifecycle. There are no close() or context-manager hooks introduced by this class.

## Method Map:
flowchart LR
    A[is_safe_attribute(obj,attr,value)] --> B[super().is_safe_attribute(obj,attr,value)]
    B --> |False| C[return False]
    B --> |True| D[modifies_known_mutable(obj,attr)]
    D --> |True| C
    D --> |False| E[return True]

Notes:
- The only method defined/overridden by this class is is_safe_attribute(obj: t.Any, attr: str, value: t.Any) -> bool (signature taken exactly from source).
- All other method calls and internals are inherited from SandboxedEnvironment.

## Raises:
- This subclass does not raise new exception types by itself in its implementation. However callers should be aware that exceptions may be propagated from:
    - super().is_safe_attribute(obj, attr, value): any exceptions the parent implementation may raise.
    - modifies_known_mutable(obj, attr): per its specification, this utility can raise NameError if the global _mutable_spec is missing, TypeError if _mutable_spec is malformed or membership tests fail, or other exceptions propagated from custom __contains__ or isinstance behavior.
- There are no explicit exception-handling wrappers in this override; thus exceptions from the parent or the mutable-spec utility surface to the caller.

## Example (described usage scenarios):
1) Allowance scenario:
   - If the parent sandbox permits attribute access (parent returns True) and the attribute is not listed as known-mutable for the object's type (modifies_known_mutable returns False), then is_safe_attribute returns True and attribute access may proceed.

2) Denial scenarios:
   - If the parent sandbox denies access (parent returns False), ImmutableSandboxedEnvironment returns False (denies).
   - If the parent permits access but modifies_known_mutable identifies the attribute as known-mutable (returns True), ImmutableSandboxedEnvironment returns False (denies) to prevent mutation-capable attribute use.

Implementation note for reimplementers:
- Reimplement exactly as in source: define a subclass of SandboxedEnvironment and override is_safe_attribute to first call the parent's is_safe_attribute with the same arguments; if that call returns False, return False; otherwise return the boolean negation of modifies_known_mutable(obj, attr).

### `src.jinja2.sandbox.ImmutableSandboxedEnvironment.is_safe_attribute` · *method*

## Summary:
Checks whether accessing a specific attribute on an object is allowed under the immutable sandbox policy and returns True only if the parent sandbox rules allow access and the attribute is not classified as a known mutating/unsafe attribute.

## Description:
This method is called during template attribute resolution to determine whether an attribute access should be permitted under the immutable sandboxed environment. Known callers in this codebase:
- SandboxedEnvironment.getattr — invoked when resolving attribute access (obj.attribute) during template rendering.
- SandboxedEnvironment.getitem — invoked when a string key lookup falls back to attribute access and the attribute name is a string.
Invocation occurs during template evaluation whenever an attribute lookup is performed on a Python object exposed to the sandbox.

Why this is a separate method:
- It extends the parent sandbox attribute-safety check by applying an additional immutability rule: attributes known to mutate an object are disallowed. Factoring this check into its own override keeps the additional policy explicit and testable and allows the immutable sandbox variant to reuse the parent checks without duplicating logic.

## Args:
    obj (typing.Any):
        The target object instance whose attribute is being accessed. Any Python object is accepted; matching for known-mutable attributes is performed using isinstance checks against configured types.
    attr (str):
        The attribute name to check. Expected to be a string representing the attribute identifier. Non-string values are not typical; callers in this codebase pass strings. The parent implementation assumes attr supports startswith("_"), so callers should pass a string to avoid unexpected exceptions.
    value (typing.Any):
        The value that would be returned by getattr(obj, attr). This parameter is forwarded to the parent safety check; it is not otherwise inspected by this override. It can be any Python object or Undefined sentinel.

## Returns:
    bool:
        - True: the parent sandbox safety check permits the attribute and the attribute is not listed as a known mutating/unsafe attribute for the object's type.
        - False: either the parent sandbox safety check denies the attribute access, or the attribute is classified as a known mutating/unsafe attribute for obj's type (i.e., access would allow mutation and is therefore disallowed).

Edge returns and semantics:
- The method strictly returns a boolean and does not perform any fallback or conversion. When the parent denies access, it returns False immediately without consulting the mutability specification.

## Raises:
    Any exception raised by the parent is_safe_attribute implementation:
        - For example, if attr does not support operations expected by the parent (like startswith), that exception may propagate.
    NameError:
        - If the global mutable specification used by modifies_known_mutable (typically _mutable_spec) is not defined, modifies_known_mutable may raise NameError which this method will propagate.
    TypeError:
        - If the global mutable specification is malformed (non-iterable, invalid typespec entries, or unsafe containers that do not support membership checks), modifies_known_mutable may raise TypeError which this method will propagate.
    Any exception raised by custom __contains__ implementations or by isinstance checks invoked inside modifies_known_mutable.

Note: This override does not catch or convert exceptions raised by its callees; callers should expect exceptions to propagate if the global mutability specification or the parent check are invalid.

## State Changes:
Attributes READ:
    - None explicitly on self. The method calls the parent's is_safe_attribute, which may read attributes on self (not by this override directly).
Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
    - attr should normally be a string. The parent implementation (SandboxedEnvironment.is_safe_attribute) calls attr.startswith("_"); passing non-string may raise an exception.
    - The global mutable specification consulted by modifies_known_mutable (commonly named _mutable_spec) must be initialized and well-formed (an iterable of (typespec, unsafe) pairs) before this method is called to avoid NameError/TypeError.
    - The object obj should be a runtime object acceptable to isinstance checks used by the mutability specification.

Postconditions:
    - No mutation of obj, self, or global specification is performed by this method.
    - The returned boolean accurately reflects: parent safety check result AND the negation of the known-mutable classification for (obj, attr).

## Side Effects:
    - No I/O, no network calls.
    - Reads global configuration used by modifies_known_mutable (the mutability specification). Reading that global may raise exceptions if it is missing or malformed.
    - No mutation of objects outside self is performed by this method.

## `src.jinja2.sandbox.SandboxedFormatter` · *class*

## Summary:
A string.Formatter subclass that resolves formatting replacement fields by delegating all attribute and item lookups to a sandboxing Environment, ensuring each lookup is mediated by Environment.getattr and Environment.getitem.

## Description:
SandboxedFormatter is intended for templating or formatting contexts where attribute and item access must be controlled by sandboxing policies. It does not perform direct attribute or item access during field resolution; instead, it delegates those operations to the provided Environment so the Environment can enforce security (for example, by raising SecurityError).

Important integration detail:
- The standard string.Formatter machinery (for example, string.Formatter.vformat and related methods) iterates over replacement fields in a format string and invokes get_field on the Formatter instance to resolve each field. SandboxedFormatter implements the resolution logic (split the field name, resolve the root via get_value, then apply successive lookups via Environment.getattr/getitem), but it is invoked by the Formatter internals (e.g., vformat) — callers typically call Formatter APIs rather than get_field directly.

Typical callers:
- Template rendering code that configures a sandboxing Environment and then calls the Formatter API (vformat/format_map/etc.) to perform rendering with sandboxed lookups.
- Any code reusing string.Formatter functionality that needs to enforce sandboxing on attribute/item access.

Responsibility boundary:
- Responsibility: take a replacement field name and resolve it to a value while ensuring every attribute/item access is routed through the sandbox Environment.
- Not responsible for: implementing security rules (that is Environment's job), escaping/markup handling, or modifying Formatter's other semantics beyond field resolution.

## State:
- _env: Environment
  - Type: Environment
  - Description: The sandbox Environment passed at construction. All attribute/item lookup operations use _env.getattr(obj, name) and _env.getitem(obj, key).
  - Constraint: Must be a valid Environment instance implementing getattr and getitem. The instance stores this reference and uses it for the lifetime of the formatter.

Inherited state:
- Inherits string.Formatter internals such as get_value; these are used to resolve the root identifier of a field.

Class invariants:
- _env remains a valid Environment instance after construction.
- get_field returns a tuple (resolved_value, first) where first is the original root identifier string extracted from the field name.

## Lifecycle:
Creation
- Instantiate with:
    - env (Environment) — required.
    - **kwargs (typing.Any) — optional keyword arguments forwarded to string.Formatter.__init__.
- Example: fmt = SandboxedFormatter(env)

Usage (typical sequence)
1. Call a Formatter API (such as fmt.vformat(format_string, args, kwargs) or fmt.format_map(mapping)) to trigger formatting.
2. The Formatter implementation iterates replacement fields in the format string and calls this instance's get_field(field_name, args, kwargs) to resolve each field.
3. get_field implements the deterministic resolution sequence:
    a. Split field_name into (first, rest) using formatter_field_name_split.
    b. Resolve the root by invoking the inherited get_value(first, args, kwargs).
    c. For each (is_attr, name_or_key) in rest, in original order:
        - If is_attr is True: call _env.getattr(current_obj, name_or_key).
        - If is_attr is False: call _env.getitem(current_obj, name_or_key).
    d. Return (current_obj, first) to the Formatter machinery.
4. The Formatter uses the returned value to perform formatting for that replacement field.
5. Repeat for each replacement field found by the Formatter.

Destruction
- No explicit cleanup required. No context manager or close method provided. Normal garbage collection applies.

## Method Map:
flowchart LR
    INIT[__init__(env, **kwargs)] --> FORMATTER_APIS[Formatter APIs (vformat/format/format_map)]
    FORMATTER_APIS --> GETFIELD[get_field(field_name, args, kwargs)]
    GETFIELD --> SPLIT[formatter_field_name_split(field_name) -> (first, rest)]
    GETFIELD --> ROOT[get_value(first, args, kwargs) -> obj]
    REST[for each (is_attr, i) in rest] -->|is_attr True| ATTR[_env.getattr(obj, i)]
    REST -->|is_attr False| ITEM[_env.getitem(obj, i)]
    ATTR --> REST
    ITEM --> REST
    REST --> RETURN[return (obj, first)]

## Raises:
- __init__:
  - Propagates exceptions from string.Formatter.__init__ if invalid kwargs are supplied.
- get_field:
  - Propagates exceptions from formatter_field_name_split for malformed field names.
  - Propagates exceptions from inherited get_value (e.g., KeyError, IndexError) depending on args/kwargs.
  - Propagates exceptions raised by the Environment methods, notably SecurityError from the sandbox policy, as well as AttributeError, KeyError, or other errors depending on the object semantics.
- The class does not catch or translate these exceptions; they propagate to the caller (usually the template rendering code).

## Example:
- Concrete usage pattern (concise):
    1. Prepare a sandbox Environment instance `env` that implements getattr(obj, name) and getitem(obj, key) and enforces desired policies.
    2. Instantiate the formatter:
        fmt = SandboxedFormatter(env)
    3. Use a Formatter API to render a format string that contains replacement fields:
        result = fmt.vformat("Hello {user.name}, first item: {items[0]}", args, kwargs)
    4. If the Environment disallows an access, it may raise SecurityError during resolution; handle this at the call site:
        try:
            result = fmt.vformat(format_string, args, kwargs)
        except SecurityError:
            # handle security violation (abort rendering, log, or raise)
            pass

This example shows the typical call pattern: callers invoke Formatter APIs (vformat/format/format_map) and rely on SandboxedFormatter.get_field to mediate attribute/item accesses through the sandbox Environment.

### `src.jinja2.sandbox.SandboxedFormatter.__init__` · *method*

## Summary:
Initializes the formatter with a sandboxing Environment by storing the Environment reference on the instance and delegating remaining initialization details to the base Formatter initializer.

## Description:
This constructor is called when a SandboxedFormatter instance is created (the object construction / instantiation lifecycle). Typical callers are template rendering setup code and any code that needs a Formatter which mediates attribute and item access through a sandbox Environment (for example, template engine components that instantiate the formatter before calling vformat/format_map). It is invoked at the creation step before any formatting methods are used.

This logic exists as a dedicated constructor because the formatter must retain a reference to the sandbox-enforcing Environment for the lifetime of the formatter (used by get_field and other resolution methods), while also allowing the underlying string.Formatter base class to perform its own initialization with any optional configuration passed via kwargs. Separating this behavior into __init__ keeps environment wiring explicit and ensures proper superclass initialization.

## Args:
    env (Environment):
        The sandbox Environment instance to use for all attribute and item resolution.
        - Expected behavior: env implements getattr(obj, name) and getitem(obj, key) and enforces sandbox policies.
        - Note: The constructor does not validate the interface of env; callers must supply a compliant Environment.
    **kwargs (t.Any):
        Additional keyword arguments forwarded directly to the superclass (string.Formatter) __init__.
        - Type annotation follows the source signature (t.Any).
        - Typical values: none for standard Formatter usage; included to allow compatibility with any Formatter subclasses that accept kwargs.

## Returns:
    None
    - The method does not return a value; it initializes instance state and returns implicitly.

## Raises:
    Any exception raised by the superclass __init__ (string.Formatter.__init__) when processing the forwarded kwargs.
    - Common examples: TypeError for unexpected keyword arguments or other initialization errors raised by the base class.
    - No new exceptions are raised by this method itself; it does not perform validation of env and therefore will not raise on invalid env here (errors may surface later when env is used).

## State Changes:
Attributes READ:
    - None (this method does not read other self.<attr> fields before writing).
Attributes WRITTEN:
    - self._env is set to the provided env object.
    - Additionally, calling super().__init__(**kwargs) may modify other inherited attributes defined by the base class (write effects depend on the string.Formatter implementation and provided kwargs).

## Constraints:
Preconditions:
    - The caller should provide a valid Environment implementing getattr and getitem. Although not enforced here, missing or non-conforming env will cause failures later when formatting methods use _env.
    - kwargs must be acceptable to the string.Formatter.__init__ signature; otherwise the superclass __init__ will raise.

Postconditions:
    - self._env references exactly the env object passed in.
    - The base class initialization has completed (assuming no exception was raised), so any Formatter-internal state managed by string.Formatter.__init__ is set up.
    - The instance is ready to be used for formatting (e.g., vformat/format_map) subject to the usual Formatter semantics and the correctness of env.

## Side Effects:
    - No I/O or external service calls are performed by this method itself.
    - It calls the superclass __init__, which may perform internal setup; any side effects of that call (allocation of internal state, attribute writes on self) are possible.
    - No validation or enforcement of sandbox policies occurs here; those occur later when _env is used.

### `src.jinja2.sandbox.SandboxedFormatter.get_field` · *method*

## Summary:
Resolve a formatting replacement field to its final value by obtaining the root value and applying successive attribute or item lookups via the sandboxed Environment. The method reads the formatter's Environment but does not modify the formatter's state.

## Description:
This method is invoked during the formatting phase for a single replacement field expression (for example, when string.Formatter.vformat evaluates a replacement field). Typical callers:
- string.Formatter.vformat or other formatting machinery that iterates replacement fields and delegates resolution to get_field.
- Jinja2's template rendering code when it uses this SandboxedFormatter to safely evaluate field expressions.

Why this is a separate method:
- It overrides/extends the base Formatter logic for field resolution to centralize sandbox-enforced attribute/item access.
- Encapsulating the root-value lookup and the subsequent attribute/item resolution in one method makes it easy to enforce security checks via the Environment and to reuse the logic wherever the sandboxed Formatter is used.

Algorithm implemented:
1. Split the incoming field_name into a root token and a list of lookups using formatter_field_name_split(field_name). This yields (first, rest) where rest is an ordered sequence of (is_attr, i) pairs.
2. Obtain the root object by calling self.get_value(first, args, kwargs).
3. Iterate over rest; for each pair:
   - If is_attr is truthy, replace obj with self._env.getattr(obj, i) (attribute lookup under environment control).
   - Otherwise, replace obj with self._env.getitem(obj, i) (item/key/index lookup under environment control).
4. Return a tuple (obj, first) where obj is the fully resolved value and first is the root token.

## Args:
    field_name (str): The replacement-field expression to resolve (as accepted by string.Formatter). May include attribute and item lookup syntax (e.g. "user.name", "items[0]").
    args (typing.Sequence[typing.Any]): Positional arguments passed to the formatter (used by get_value to resolve numeric or positional roots).
    kwargs (typing.Mapping[str, typing.Any]): Keyword arguments passed to the formatter (used by get_value to resolve named roots).

## Returns:
    tuple[typing.Any, str]: A 2-tuple (resolved_value, first)
        - resolved_value: The final object/value obtained after applying all attribute/item lookups (may be any Python object).
        - first: The root token (string) returned by formatter_field_name_split for the original field_name.

Edge cases:
- If field_name represents a simple root (no attribute/item lookups), rest will be empty and the method returns (self.get_value(first, args, kwargs), first).
- The exact type and meaning of 'i' in each (is_attr, i) pair follow formatter_field_name_split's contract (attribute name strings or index/key tokens as produced by the splitter).

## Raises:
    Propagates any exception raised by the underlying operations. In particular:
    - Exceptions from self.get_value(first, args, kwargs) (for example, KeyError, IndexError, or other lookup-related exceptions), when the root cannot be resolved.
    - Exceptions from self._env.getattr(obj, i) or self._env.getitem(obj, i). These calls implement sandboxed attribute/item access and may raise errors (for example, AttributeError, KeyError, IndexError, TypeError) or sandbox-specific errors raised by the Environment implementation.
    - Any exception raised by user-defined properties, __getattr__/__getitem__ implementations, or other side-effecting accessors invoked during resolution.

This method does not catch or wrap these exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
    - self._env: used to perform sandboxed getattr/getitem operations.
Methods invoked (read semantics):
    - self.get_value(first, args, kwargs) — resolves the root token.
    - self._env.getattr(obj, i)
    - self._env.getitem(obj, i)

Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self._env must be set and must expose callable getattr and getitem methods that accept (obj, name_or_index).
    - field_name must be a string acceptable to formatter_field_name_split.
    - args must be a sequence and kwargs a mapping as expected by the base Formatter.get_value implementation.

Postconditions:
    - The returned tuple contains the fully resolved value and the original root token.
    - The SandboxedFormatter instance is unchanged (no attribute mutations).

## Side Effects:
    - No I/O or external service calls are made by this method itself.
    - The method will invoke attribute and item accessors on arbitrary objects (via self._env.getattr/getitem). Those accessors may execute arbitrary Python code (properties, descriptors, __getitem__, __getattr__), which can have side effects outside this method.
    - The Environment accessors may perform sandbox/security checks and raise sandbox-related exceptions; those checks are side-effect free with respect to the formatter but affect control flow by raising exceptions.

## `src.jinja2.sandbox.SandboxedEscapeFormatter` · *class*

## Summary:
A combined Formatter that enforces sandboxed attribute/item access for replacement field resolution and applies HTML-safe escaping to formatted string output by composing SandboxedFormatter and markupsafe.EscapeFormatter.

## Description:
SandboxedEscapeFormatter is used when template/format string rendering requires both: (1) strict sandboxing of attribute and item access (so each lookup is mediated by an Environment that can enforce security policies), and (2) automatic escaping of string results to produce HTML-safe output while preserving already-safe Markup values.

Typical callers
- Templating/rendering code that configures a sandboxing Environment and needs both controlled lookups and automatic escaping of output.
- Any code that uses the string.Formatter API (for example vformat/format/format_map) and wants sandboxing plus Markup-aware escaping.

Motivation and responsibilities
- Combines two orthogonal concerns by multiple inheritance:
  - SandboxedFormatter: handles field name resolution by delegating attribute/item access to a provided Environment.
  - EscapeFormatter (from markupsafe): handles escaping of formatted output, typically escaping regular strings and preserving Markup instances.
- Responsibility boundary:
  - This class mediates lookups and escaping only by inheriting behavior from its parents. It does not implement sandbox policies itself (that is Environment's responsibility), nor does it implement escaping logic beyond what EscapeFormatter provides.

## State:
- _env: Environment
  - Type: Environment
  - Origin: inherited from SandboxedFormatter (constructor argument forwarded to the base).
  - Valid values: any Environment instance that implements getattr(obj, name) and getitem(obj, key).
  - Invariant: _env must remain a usable Environment object for the lifetime of the formatter; all attribute/item access performed during field resolution must go through this instance.

- No additional instance attributes are introduced by SandboxedEscapeFormatter itself; it relies on inherited state from SandboxedFormatter and EscapeFormatter (which in practice do not require extra per-instance state beyond what standard string.Formatter needs).

Class invariants
- _env is set at construction and remains a valid Environment for all formatting operations.
- Field resolution uses SandboxedFormatter.get_field (i.e., attribute/item lookups are routed to _env).
- Value formatting/escaping uses EscapeFormatter.format_field semantics (i.e., escaping behavior is inherited).

## Lifecycle:
Creation
- Instantiate with the sandbox Environment:
  - Required arguments: env (Environment)
  - Additional keyword arguments are forwarded to string.Formatter.__init__ if relevant.
- Example instantiation: create an Environment instance configured for sandboxing, then instantiate SandboxedEscapeFormatter with that env.

Usage
- Typical usage is via the string.Formatter API methods provided by the base classes:
  - vformat(format_string, args, kwargs)
  - format(format_string, *args, **kwargs)
  - format_map(mapping)
- Typical call sequence per replacement field:
  1. The Formatter parsing machinery (inherited from string.Formatter) identifies a replacement field in the format string.
  2. It calls get_field on the formatter instance. By MRO, this resolves to SandboxedFormatter.get_field, which:
     - Splits the field name into a root and attribute/item steps.
     - Resolves the root via inherited get_value.
     - For each step, calls _env.getattr or _env.getitem to perform the access.
  3. After a value is resolved, the formatting step calls format_field. By MRO, this resolves to EscapeFormatter.format_field, which applies Markup-aware escaping to string results and preserves Markup objects (behavior described at a high level here, inherited from markupsafe).
  4. The final escaped/formatted value is inserted into the output.
- No special sequencing is required beyond normal Formatter usage. Consumers should invoke Formatter APIs rather than calling get_field/format_field directly in most cases.

Destruction / Cleanup
- No explicit cleanup API (no close or context manager). Instances are ordinary objects cleaned up by garbage collection.
- If the associated Environment requires cleanup, manage that externally.

## Method Map:
flowchart LR
    CREATE[Instantiate: SandboxedEscapeFormatter(env, **formatter_kwargs)] --> FORMAT_APIS[Formatter APIs: vformat / format / format_map]
    FORMAT_APIS --> PARSE[Parse format string -> identify replacement fields]
    PARSE --> GETFIELD[SandboxedFormatter.get_field(field_name, args, kwargs)]
    GETFIELD --> SPLIT[formatter_field_name_split -> (first, rest)]
    GETFIELD --> ROOT[get_value(first, args, kwargs) -> current_obj]
    REST[for each (is_attr, name) in rest] -->|is_attr True| ATTR[_env.getattr(current_obj, name)]
    REST -->|is_attr False| ITEM[_env.getitem(current_obj, name)]
    ATTR --> REST
    ITEM --> REST
    GETFIELD --> RETURN[return (resolved_value, first)]
    RETURN --> FORMATFIELD[EscapeFormatter.format_field(resolved_value, format_spec)]
    FORMATFIELD --> ESCAPED[escape strings, preserve Markup instances]
    ESCAPED --> INSERT[insert into output string]

Notes on MRO and method origin
- get_field: provided by SandboxedFormatter (ensures sandboxing).
- format_field: provided by EscapeFormatter (ensures escaping/Markup handling).
- Other Formatter behaviors (parsing, get_value, conversion) are from string.Formatter as usual.

## Raises:
- Construction (__init__):
  - Propagates exceptions from parent constructors (e.g., invalid kwargs forwarded to string.Formatter.__init__).
  - There is no class-specific validation beyond requiring a valid Environment; passing a non-Environment will cause attribute/item access to fail at runtime.

- During formatting:
  - Exceptions propagated from SandboxedFormatter:
    - SecurityError (from Environment.getattr/getitem) when the sandbox policy disallows an access.
    - AttributeError, KeyError, IndexError or other errors originating from get_value or the Environment's getitem/getattr implementations.
  - Exceptions propagated from EscapeFormatter/markupsafe:
    - Errors that occur while converting/escaping values (rare in typical use). Plain strings are escaped and Markup instances are preserved; unexpected object types may raise their own exceptions during conversion to string or during escape operations.
  - The class itself does not catch or translate these exceptions; they bubble to the caller for handling.

## Example:
- Setup and typical usage pattern (concise):
  1. Prepare a sandbox Environment instance env that enforces attribute/item access policies (implements getattr(obj, name) and getitem(obj, key)).
  2. Instantiate the formatter:
     - fmt = SandboxedEscapeFormatter(env)
  3. Render a format string using a Formatter API. For example, render a template-like string containing fields such as "{user.name}" or "{items[0]}":
     - result = fmt.vformat("Hello {user.name}, first item: {items[0]}", args, kwargs)
  4. Behavior during rendering:
     - Each attribute/item access during resolution is routed through env, which may raise SecurityError when access is disallowed.
     - Final string results are escaped according to EscapeFormatter semantics (plain strings are escaped for HTML safety; Markup values are preserved as safe).
  5. Handle exceptions (for example, catch SecurityError to abort or log a security violation).

Notes and implementation guidance
- Reimplementing this class from scratch requires only defining an empty subclass that inherits SandboxedFormatter first and EscapeFormatter second. The desired combined behavior arises from Python's method resolution order: SandboxedFormatter.get_field will be used for lookup resolution, and EscapeFormatter.format_field will be used for escaping formatted values.
- Ensure the Environment passed at construction implements getattr and getitem and enforces any sandbox policy; this class itself does not implement security checks.

