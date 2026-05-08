# `tests.py`

## `src.jinja2.tests.test_odd` · *function*

## Summary:
Returns True when the provided numeric value is an odd integer (remainder 1 when divided by 2); otherwise returns False.

## Description:
- Known callers within the codebase:
    - No direct callers were discovered in the repository scan for this function.
    - Intended usage context: defined in a module named for template tests (src/jinja2/tests.py). It is typically used as a small predicate / test that template engines or higher-level code can call to check oddness of integers.
- Reason for extraction:
    - Encapsulates a single, well-defined predicate (oddness) so that template code or other consumers can reuse the exact same logic consistently.
    - Keeps template-test registration and template logic concise by delegating the predicate to a single pure function rather than inlining modulo checks repeatedly.

## Args:
    value (int):
        - Expected to be an integer value to test for oddness.
        - The annotated type is int; the function performs value % 2.
        - Accepts any object that implements the modulo operation (%) with an integer 2. If the object supports the operation in a meaningful way (e.g., some Number subclasses or ints), the function will perform that operation — otherwise a TypeError will be raised.

## Returns:
    bool:
        - True if value % 2 == 1 (i.e., the remainder after dividing value by 2 equals 1).
        - False otherwise.
        - Examples of possible outcomes:
            * value = 3  -> True
            * value = -1 -> True (Python's modulo yields 1 for -1 % 2)
            * value = 2  -> False
            * value = 0  -> False

## Raises:
    TypeError:
        - If the argument does not support the modulo operator with an integer (e.g., passing a plain string that does not define an appropriate __mod__ semantics).
        - The exception is raised by the underlying modulo operation; this function does not catch it.

## Constraints:
- Preconditions:
    - Caller should supply an integer-like value or another object that meaningfully implements value % 2.
    - Calling with None or objects that lack modulo semantics will raise TypeError.
- Postconditions:
    - The function returns a boolean value (True or False).
    - It does not modify its input.

## Side Effects:
- None. The function is pure: it performs no I/O, does not mutate global state, and makes no external service calls.

## Control Flow:
flowchart TD
    A[Start: call test_odd(value)] --> B[Compute r = value % 2]
    B --> C{Is r == 1?}
    C -- Yes --> D[Return True]
    C -- No  --> E[Return False]
    B --> F[If value lacks % operator -> propagate TypeError]

## Examples:
- Typical successful calls:
    - test_odd(3)    # -> True
    - test_odd(-1)   # -> True
    - test_odd(2)    # -> False
- Non-integer / error example (illustrative):
    - Passing a string that doesn't support modulo with an integer:
        - test_odd("3")  # raises TypeError (unsupported operand types for %)
- Note:
    - Some numeric non-int types (e.g., floats) will execute the modulo; behavior depends on Python semantics (for example, test_odd(3.0) evaluates 3.0 % 2 == 1.0 which compares equal to 1 and therefore returns True). If strict integer-only semantics are required, callers should validate or coerce the input before calling.

## `src.jinja2.tests.test_even` · *function*

## Summary:
Return True if the provided value is evenly divisible by 2 (has zero remainder), otherwise return False.

## Description:
A minimal predicate that computes value % 2 and compares the result to 0 to determine parity.

Known callers within the repository:
    - None discovered by static analysis of the codebase. The function is defined in a tests module and may be imported or registered elsewhere, but no direct references were found.

Why this logic is extracted into its own function:
    - Encapsulation: centralizes the parity check so callers do not need to repeat the modulo-and-compare logic.
    - Testability: provides a single, easily testable point for parity logic.
    - Reuse: can be imported wherever a simple evenness predicate is required.

## Args:
    value (int):
        The parameter is annotated as an integer in the function signature.
        - The annotation indicates the expected type but is not enforced at runtime.
        - Other numeric types (e.g., float, Decimal, Fraction) or objects that implement the modulo operator with int may work; their behavior depends on their __mod__ implementation.

## Returns:
    bool:
        - True when (value % 2) == 0.
        - False otherwise.

        Edge-case return behavior:
            - Zero: test_even(0) -> True.
            - Negative integers: test_even(-4) -> True (Python's % yields 0 for -4 % 2).
            - Floating-point values: test_even(4.0) -> True; test_even(3.5) -> False because 3.5 % 2 == 1.5.
            - Values yielding a non-numeric remainder (if an object's __mod__ returns a non-zero-like result) will be compared with 0 using Python's equality rules; the boolean result follows that comparison.

## Raises:
    TypeError:
        - Occurs if the operand type does not support the modulo operation with an integer (for example, an object that does not implement __mod__ for int).
    Any exception raised by the operand's __mod__ implementation:
        - If value.__mod__(2) raises a different exception, that exception will propagate unchanged.

## Constraints:
    Preconditions:
        - The caller should expect an integer-like input; the signature is annotated with int.
        - Callers relying on type guarantees must perform type checks prior to calling, as the function does not coerce or validate types.

    Postconditions:
        - The function returns a Python bool.
        - No mutation of the input or external state occurs.

## Side Effects:
    - None. The function performs no I/O and does not change external state.

## Control Flow:
flowchart TD
    Start([Start]) --> Compute[Compute remainder = value % 2]
    Compute --> Compare{Is remainder == 0?}
    Compare -- Yes --> ReturnTrue([return True])
    Compare -- No --> ReturnFalse([return False])
    Compute -- Exception --> Propagate[Propagate exception raised by __mod__]

## Examples:
    - Typical integer usage:
        test_even(4)  -> True
        test_even(3)  -> False
        test_even(0)  -> True
        test_even(-2) -> True

    - Floating-point example:
        test_even(4.0) -> True
        test_even(3.5) -> False

    - Handling unsupported types safely:
        try:
            result = test_even("abc")
        except TypeError:
            # handle non-numeric input
            result = False  # or other application-specific fallback

## Implementation notes for reimplementation:
    - Implement as: return value % 2 == 0
    - Do not perform implicit type coercion; allow Python's operator behavior to determine outcomes and exceptions.
    - Keep the function pure and side-effect free so it is safe for use in many contexts.

## `src.jinja2.tests.test_divisibleby` · *function*

## Summary:
Checks whether one integer is evenly divisible by another and returns True when the remainder is zero.

## Description:
Performs an integer modulo operation and compares the remainder to zero to determine divisibility.

Known callers:
- No direct callers were identified in the scanned code excerpt. This function is implemented as a small utility-style predicate intended for use wherever a template test or other code path needs to know whether one number divides another without remainder.

Why this logic is extracted:
- Encapsulates the simple but commonly-needed "is divisible by" check into a named, reusable predicate. Keeping it separate clarifies intent at call sites (readability in templates or test suites) and centralizes handling of the modulo semantics and associated edge cases (e.g., division by zero).

## Args:
    value (int): The dividend — the number being divided. Intended to be an integer per the type annotation.
    num (int): The divisor — the number to divide by. Intended to be an integer per the type annotation.
        - Interdependency: If num is 0, the underlying modulo operation will raise a ZeroDivisionError.

Notes on types:
- The implementation uses the % operator directly. While the type hints specify int, any objects supporting the % operator may be accepted at runtime; such usage is subject to Python's % semantics and may raise TypeError if unsupported.

## Returns:
    bool: True if value % num == 0 (i.e., value is evenly divisible by num), otherwise False.

All possible outcomes:
- True: The modulo operation returns 0.
- False: The modulo operation returns a non-zero remainder.
- Exception: No boolean is returned if an exception is raised (see Raises).

## Raises:
    ZeroDivisionError: Raised when num == 0 because the modulo operation attempts division by zero.
    TypeError: May be raised when either operand does not support the % operator (e.g., passing incompatible types).

## Constraints:
Preconditions:
- The caller should ensure num is not zero if they wish to avoid a ZeroDivisionError.
- The function is annotated for integers; callers should preferably pass integers to match the intended semantics.

Postconditions:
- The function returns a boolean value representing whether the dividend is evenly divisible by the divisor.
- No global state or inputs are modified by this function.

## Side Effects:
- None. The function performs pure computation and does not perform I/O, mutate external state, or call external services.

## Control Flow:
flowchart TD
    Start --> CheckZero{is num == 0?}
    CheckZero -- Yes --> RaiseZero[raise ZeroDivisionError]
    CheckZero -- No --> Compute[compute remainder = value % num]
    Compute --> CheckRem{remainder == 0?}
    CheckRem -- Yes --> ReturnTrue[return True]
    CheckRem -- No --> ReturnFalse[return False]

## Examples:
- Basic usage:
    try:
        result = test_divisibleby(10, 2)
        # result == True
    except ZeroDivisionError:
        # handle divisor == 0

- Negative values:
    # Python's modulo semantics mean negative dividends are handled consistently:
    assert test_divisibleby(-10, 2) is True

- Handling zero divisor explicitly:
    if divisor == 0:
        # avoid calling the function or handle as special case
        handle_divisor_zero()
    else:
        is_divisible = test_divisibleby(value, divisor)

## `src.jinja2.tests.test_defined` · *function*

## Summary:
Return True when the provided value is not the template runtime's Undefined sentinel; otherwise return False.

## Description:
This function implements the semantics of the template "defined" test by checking whether the supplied value is the runtime Undefined sentinel and returning the negation of that check.

Known callers within the provided scan:
- No explicit internal call sites were discovered in the scanned view of the codebase. In typical usage the template evaluation/runtime calls this when evaluating the test expression "variable is defined". It is also intended to be registered or referenced from a tests registry used by the templating engine.

Why this is a separate function:
- Centralizes the Undefined-sentinel detection so template-evaluation code can call a single, well-named routine instead of repeating isinstance checks. This supports registration as a named test, easier unit testing, and future changes to the Undefined sentinel behavior in one place.

## Args:
    value (t.Any):
        - The value to test for being defined.
        - The annotation in the source is exactly "t.Any". The function accepts any Python object and only inspects whether it is an instance of the runtime Undefined sentinel.
        - No default value.

## Returns:
    bool:
        - True if and only if the supplied value is not an instance of runtime.Undefined.
        - False if the supplied value is an instance of runtime.Undefined.
        - Edge-case behavior:
            * If value is an instance of a subclass of Undefined, isinstance returns True and the function returns False.
            * Falsy values that are nevertheless defined (e.g., None, 0, False, empty collections) will return True because they are not the Undefined sentinel.

## Raises:
    TypeError:
        - May be raised by Python's isinstance if the runtime symbol Undefined is not a type or tuple of types (for example, if Undefined has been rebound to an invalid value). This function does not explicitly raise errors; any TypeError is propagated from isinstance and indicates a misconfiguration of the runtime imports.

## Constraints:
    Preconditions:
        - The name Undefined (imported from runtime in the module) should be a valid type or tuple of types appropriate for use as the second argument to isinstance.
        - Caller must provide a value object; the function accepts any Python object.

    Postconditions:
        - The function returns a boolean value with no side effects.
        - No global or caller-provided objects are modified.

## Side Effects:
    - None. The function performs a pure type-test and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> IsUndefined{isinstance(value, Undefined)?}
    IsUndefined -- True --> ReturnFalse[/return False/]
    IsUndefined -- False --> ReturnTrue[/return True/]

## Examples:
- Conceptual usage in template evaluation:
    - When evaluating "foo is defined", the template runtime passes the runtime value bound to foo into this function. If that runtime value is the Undefined sentinel, the test yields False; otherwise it yields True.

- Example outcomes (descriptive):
    - value is an instance of Undefined -> returns False.
    - value is None -> returns True.
    - value is 0 or False -> returns True.
    - value is a user object or collection -> returns True unless it is specifically an instance of Undefined.

## `src.jinja2.tests.test_undefined` · *function*

## Summary:
Returns whether the provided value is an instance of the repository's Undefined sentinel/type, yielding True for undefined sentinel objects and False otherwise.

## Description:
A tiny predicate used to test whether a given value represents the runtime's Undefined sentinel/type (imported from runtime). Typical uses are in template testing and conditional logic where code needs to distinguish between genuinely provided values and the templating system's "undefined" sentinel.

Known callers within the codebase:
- No callers were discovered by repository search during documentation generation (search failed). Despite that, this function is intended to be used anywhere a boolean test for the Undefined sentinel is needed (for example, in template filters, assertions in tests, or guard clauses in runtime code).

Why this logic is a separate function:
- Encapsulates the isinstance check behind a named predicate so call sites read clearly (test_undefined(value) vs isinstance(value, Undefined)).
- Centralizes the dependency on the runtime.Undefined symbol so future changes to how "undefined" is represented (class, tuple of classes, or sentinel object) only need a single-site update.
- Improves readability and can be mocked/stubbed in tests.

## Args:
    value (Any):
        The object to be tested. Any Python object is accepted; there are no intrinsic constraints on its type.
        Note: The annotation in source is a generic Any (t.Any). The function treats the value opaquely and only checks its runtime type.

## Returns:
    bool:
        True if and only if `value` is an instance of the runtime's Undefined type (the symbol imported as Undefined).
        Possible return values:
        - True: value is an instance of Undefined (or one of the classes in the tuple if Undefined is a tuple of classes).
        - False: value is not an instance of Undefined.

## Raises:
    TypeError:
        If the imported Undefined symbol is not a class or a tuple of classes but rather an invalid second argument for isinstance, Python's builtin isinstance will raise TypeError. This is a configuration/implementation error of the runtime.Undefined symbol, not of this predicate.
    NameError / ImportError:
        Not raised by this function directly at call time, but if the module-level import `from runtime import Undefined` failed when the module was loaded, the module would not have been imported successfully; thus callers would not reach this function. Documented here for completeness.

## Constraints:
Preconditions:
    - The module must have been imported successfully so that the name Undefined is bound in the module scope.
    - The runtime.Undefined symbol should be either a class or a tuple of classes (valid second argument for isinstance). If it is not, callers should expect TypeError.

Postconditions:
    - No mutation of inputs or global state occurs.
    - The function returns a boolean value; no other side effects are produced.

## Side Effects:
    - None. The function performs a pure type check and does not perform I/O, mutate global variables, or call external services.

## Control Flow:
flowchart TD
    A[Start: call test_undefined(value)] --> B{Is Undefined a valid isinstance target?}
    B -->|No (not class/tuple)| C[isinstance raises TypeError -> propagates to caller]
    B -->|Yes| D{isinstance(value, Undefined)}
    D -->|True| E[Return True]
    D -->|False| F[Return False]

## Examples:
    Example 1 — Typical usage
    - Context: checking if a value returned from template evaluation is the templating system's undefined sentinel.
    - Behavior: returns True for Undefined instances, False otherwise.

    Example 2 — Defensive use
    - If your runtime may replace Undefined with a non-class sentinel type, guard the call:
        try:
            is_undef = test_undefined(value)
        except TypeError:
            # Fallback logic if Undefined is misconfigured
            is_undef = False

    Note: The function's only responsibility is the boolean check; handling misconfiguration of the Undefined symbol is a caller concern.

## `src.jinja2.tests.test_filter` · *function*

## Summary:
Return True if the given filter name is present in the provided template environment's filters collection; otherwise return False.

## Description:
A minimal predicate that tests membership of a filter name in an Environment-like object's filters collection by evaluating "value in env.filters" and returning the resulting boolean.

Callers within the codebase:
    - No direct callers were discovered in the available repository snapshot. In a template engine, this kind of predicate is typically used by template-evaluation logic or diagnostic utilities that need to verify whether a named filter exists before attempting to apply it.

Why this is a separate function:
    - The operation is a single-responsibility predicate (existence test). Extracting it centralizes the membership check and its error semantics so callers do not duplicate the membership expression or handle the same edge cases in multiple places.

## Args:
    env (Environment): An Environment-like object (type-hinted as Environment). The object must provide a public attribute or property named filters. That attribute should support Python membership testing via the "in" operator (for example, a dict, set, list, or any container implementing __contains__). The function performs no validation beyond attribute access; passing None or an object without filters will raise attribute access errors.
    value (str): The name of the filter to test for. The function's signature indicates a string; passing other types may work depending on the semantics of env.filters (e.g., lists accept unhashable items, dicts require hashable keys).

## Returns:
    bool: True when the membership test "value in env.filters" evaluates to True; False when it evaluates to False.
    - The function never returns None.
    - If the membership test cannot be evaluated because of an exception (see Raises), that exception propagates instead of producing a boolean.

## Raises:
    AttributeError: If env has no attribute named filters (attempting to access env.filters raises AttributeError).
    TypeError: If the membership operation is invalid for the provided value and container (for example, env.filters is a dict and value is unhashable), or if env.filters is None and "in" is not supported.
    Any exception raised by evaluating env.filters (for example, if filters is a property whose getter raises) will propagate unchanged.

## Constraints:
    Preconditions:
        - The caller should pass an Environment-like object that exposes filters; there is no defensive check in the function.
        - The typical expected type for value is str (hashable). Behavior for other types depends on env.filters implementation.
    Postconditions:
        - No mutation of env or env.filters is performed by this call.
        - Either a boolean is returned or an exception originating from attribute access or membership testing is raised.

## Side Effects:
    - The function itself has no intrinsic side effects (no I/O, no global state mutation).
    - Accessing env.filters may trigger side effects if filters is implemented as a property or performs lazy initialization; such side effects are external and will occur when the attribute is accessed.

## Control Flow:
flowchart TD
    Start --> AccessFilters[Access env.filters]
    AccessFilters --> HasFilters{Did access succeed?}
    HasFilters -- No --> RaiseAttributeError[AttributeError raised]
    HasFilters -- Yes --> MembershipCheck[Evaluate "value in env.filters"]
    MembershipCheck -- True --> ReturnTrue[Return True]
    MembershipCheck -- False --> ReturnFalse[Return False]
    MembershipCheck -- Error --> PropagateError[Propagate TypeError/Other]

## Examples:
    (Assumes test_filter is imported from src.jinja2.tests)

    1) Basic usage with a dict-like filters:
        class DummyEnv:
            filters = {"upper": lambda s: s.upper()}

        env = DummyEnv()
        print(test_filter(env, "upper"))      # -> True
        print(test_filter(env, "nonexistent"))# -> False

    2) Handling missing filters attribute:
        try:
            # object() has no .filters attribute
            test_filter(object(), "x")
        except AttributeError:
            print("No filters attribute on env")  # Expected for objects without filters

    3) Handling unhashable value when filters is a dict:
        class EnvWithDict:
            filters = {}

        env = EnvWithDict()
        try:
            # lists are unhashable as dict keys -> membership on dict raises TypeError
            test_filter(env, [])
        except TypeError:
            print("Value unhashable for dict-backed filters")  # Handle accordingly

    4) Note on computed filters:
        If env.filters is implemented as a property that constructs the mapping on access, any exceptions or side effects produced by that property will surface to callers of this predicate. Wrap the call in try/except if such behavior must be contained.

## `src.jinja2.tests.test_test` · *function*

## Summary:
Checks whether the given value is present in the environment's tests collection and returns True if found, False otherwise.

## Description:
This function performs a single, direct membership check against the env.tests attribute and returns the boolean result.

Known callers:
- No callers were identified in the provided source context. The function is written as a small predicate intended to be used wherever a lookup of a test name/identifier in an Environment instance's tests collection is needed.

Why this logic is extracted:
- Encapsulates the membership-check logic for env.tests into a single, reusable predicate. This keeps callers concise and centralizes the single responsibility of querying the environment's tests collection for membership.

## Args:
    env (Environment): An Environment-like object that exposes an attribute named `tests`.
        - Requirement: env must have an attribute named `tests` at call time.
        - No further structural assumption is required by the function itself, except that `env.tests` supports Python membership testing (the `in` operator).
    value (str): The value to test for membership in env.tests.
        - Type annotation is str in the signature, but at runtime any object is allowed as long as membership semantics between that object and env.tests are valid.

## Returns:
    bool: True if `value in env.tests` evaluates to True, False if it evaluates to False.
    - The expression returns a Python boolean when the membership operation succeeds.
    - If the membership operation is supported but returns a truthy/falsey non-bool (rare for builtin containers), the returned value will be that truthy/falsey value coerced to Python's boolean context (effectively a bool in normal usage).

## Raises:
    AttributeError: If `env` does not have a `tests` attribute (raised by attribute access).
    TypeError: If `env.tests` exists but does not support the membership operation with the given `value` (for example, if `env.tests` is None or an object that doesn't implement __contains__ and whose membership check is invalid).

## Constraints:
Preconditions:
    - `env` must be an object with an attribute named `tests`.
    - The `tests` attribute must support membership testing against the provided `value` (i.e., the expression `value in env.tests` must be a valid operation).

Postconditions:
    - If no exception is raised, the function returns a boolean that accurately reflects the result of the membership test `value in env.tests`.
    - The function does not modify `env` or `env.tests`.

## Side Effects:
    - None. The function performs no I/O, does not mutate external state, and makes no network or file system calls.
    - It only reads the attribute `env.tests` and evaluates a membership expression.

## Control Flow:
flowchart TD
    Start --> CheckAttr["Does env have attribute 'tests'?"]
    CheckAttr -- No --> RaiseAttr["Raise AttributeError"]
    CheckAttr -- Yes --> Membership["Evaluate: value in env.tests"]
    Membership --> Success["Return result (True or False)"]
    Membership -- TypeError --> RaiseType["Raise TypeError"]

## Examples:
- Typical usage scenario (descriptive):
    If an Environment-like object has a tests collection that lists registered test names, calling this function with a candidate name returns True when that name is present and False otherwise.

- Example (behavioral, not implementation code):
    Given env.tests is a set containing "is_odd" and "is_even":
    - Calling the predicate with value="is_odd" returns True.
    - Calling the predicate with value="is_prime" returns False.

- Error case (behavioral):
    - If env lacks the attribute `tests`, the call raises AttributeError.
    - If env.tests is None, calling the function typically raises TypeError because membership cannot be evaluated.

## `src.jinja2.tests.test_none` · *function*

## Summary:
Performs an identity check and returns True only if the provided value is exactly the singleton None; otherwise returns False.

## Description:
This is a small, deterministic predicate extracted to centralize the "is None" check used by the template test infrastructure. No direct callers were found in the scanned repository index for this exact symbol; it is intended to be used wherever the template engine or related utilities need to evaluate whether a runtime value is the Python None singleton.

Responsibility boundary:
- Encapsulates a single, well-defined semantic: identity comparison against None using the Python "is" operator.
- Keeps the None-test logic separate from calling sites so callers do not need to repeat the identity-check semantics (important because "is None" is intentionally different from equality comparisons).

## Args:
    value (t.Any): Any Python value. The function accepts any object; there are no restrictions or required attributes on the value.

## Returns:
    bool: True if and only if value is the Python None singleton (value is None). Returns False for every other input, including but not limited to:
        - False, 0, empty containers
        - Objects that implement custom __eq__ or __bool__ behavior
        - Instances of runtime.Undefined or other sentinel objects (unless they are literally None)

## Raises:
    This function does not raise exceptions in normal operation. It performs a pure identity check and will not raise for any input value.

## Constraints:
    Preconditions:
        - Caller may pass any Python object; there are no type or attribute preconditions.
    Postconditions:
        - The function returns a boolean value.
        - No mutation of the input or external state occurs.

## Side Effects:
    - None. The function has no I/O, does not mutate global state, and makes no external calls.

## Control Flow:
flowchart TD
    Start[Start] --> Check{Is value is None?}
    Check -- Yes --> ReturnTrue[Return True]
    Check -- No --> ReturnFalse[Return False]
    ReturnTrue --> End[End]
    ReturnFalse --> End

## Implementation notes and important semantic details:
    - Uses Python's identity operator ("is") rather than equality ("=="), so the result is strictly based on object identity and is unaffected by any __eq__ or __bool__ implementations on the value.
    - Because it checks identity, it will only be True for the single None object present in the interpreter.
    - The function is suitable wherever an unambiguous check for None is needed (for example, in template test evaluation to distinguish missing/undefined values from falsy-but-present values).

## Examples:
    - Calling the predicate with None yields True.
    - Calling the predicate with other falsy values (0, False, "", [], {}) yields False.
    - Calling the predicate with an object that overrides equality still yields False unless it is exactly the None object.

## `src.jinja2.tests.test_boolean` · *function*

## Summary:
Returns True only when the supplied argument is the boolean singleton True or False (identity check); otherwise returns False.

## Description:
This function implements the low-level boolean test used by the templating runtime to determine whether a value is the actual boolean singleton True or False (not merely truthy or falsy). Typical callers:
- The templating engine when evaluating a template expression using the "is boolean" test (e.g., in Jinja2 templates when a template contains "variable is boolean").
- Any internal code or unit tests that need an explicit check that a value is the bool singleton rather than a truthy/falsy object.

Responsibility boundary:
- It enforces a strict identity-based boolean check: it answers the narrow question "is this object exactly True or exactly False?" This prevents conflating integer 1 or other truthy values with the True singleton, and similarly for falsy values. The function is intentionally small and isolated so the templating runtime can reuse a consistent, unambiguous test implementation rather than duplicating identity checks at call sites.

## Args:
    value (t.Any): The value to test. Any Python object may be passed; there are no special allowed ranges or additional constraints.

Note: There are no interdependencies between parameters because there is only a single parameter.

## Returns:
    bool: True if and only if value is the boolean singleton True or the boolean singleton False (i.e., value is True or value is False). For all other inputs (including truthy integers like 1, non-empty containers, None, custom truthy/falsy objects), the function returns False.

Possible return examples:
- test_boolean(True) -> True
- test_boolean(False) -> True
- test_boolean(1) -> False
- test_boolean(0) -> False
- test_boolean([]) -> False
- test_boolean(None) -> False

## Raises:
    This function does not raise any exceptions for normal inputs. It performs no operations that intentionally raise; any exception would be from unusual interpreter-level errors (not from the function logic itself).

## Constraints:
Preconditions:
- Caller must provide exactly one positional argument corresponding to value when invoking; typical Python call semantics apply.
- No type conversion or coercion is performed; the caller should not rely on truthiness semantics.

Postconditions:
- The return value is always a Python bool object (True or False).
- The call has no side effects and leaves the input value unchanged.

## Side Effects:
- None. The function performs a pure read-only identity check and does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> CheckTrue{value is True?}
    CheckTrue -- yes --> ReturnTrue[Return True]
    CheckTrue -- no --> CheckFalse{value is False?}
    CheckFalse -- yes --> ReturnTrue2[Return True]
    CheckFalse -- no --> ReturnFalse[Return False]
    ReturnTrue --> End([End])
    ReturnTrue2 --> End
    ReturnFalse --> End

## Examples:
Example 1 — direct calls
    result = test_boolean(True)   # returns True
    result = test_boolean(False)  # returns True
    result = test_boolean(1)      # returns False (1 is truthy but not the True singleton)
    result = test_boolean(0)      # returns False

Example 2 — usage in a templating context (conceptual)
    # When a template contains: {% if myvar is boolean %} ...
    # The template engine will call this function (or a wrapper) to determine
    # whether `myvar` is exactly True or False and branch accordingly.

## `src.jinja2.tests.test_false` · *function*

## Summary:
Return True only when the provided value is the Python boolean singleton False (identity check); returns False for all other values, including other falsy values.

## Description:
This predicate checks whether a value is the exact boolean False rather than merely "falsy". It is suitable wherever code must distinguish the literal False from other values that evaluate to False in boolean contexts (0, "", None, empty containers, or objects with a custom __bool__).

Known callers within the repository:
    - No direct callers were found in the scanned codebase for this function. It is commonly used as a building block for template tests or validation logic that needs to detect the literal False value.

Why this logic is extracted:
    - Centralizes the semantic distinction between the boolean False singleton and other falsy values.
    - Keeps callers succinct and avoids repeated identity-vs-truthiness checks.
    - Makes intent explicit (checking for "is False") rather than relying on implicit boolean coercion.

## Args:
    value (t.Any): Any Python object. The function performs an identity comparison against the built-in False singleton.
    - Allowed values: any Python object or value.
    - There are no interdependencies between parameters (single-argument function).

## Returns:
    bool: True if and only if value is the boolean singleton False (i.e., value is False). Returns False for any other value, including:
    - Numeric zero (0), empty strings (""), empty containers ([], {}, set()), None
    - Objects whose __bool__ or __len__ methods make them falsy
    - Instances of runtime.Undefined or other sentinel/placeholder types

## Raises:
    - This function does not raise exceptions under normal operation.

## Constraints:
    Preconditions:
        - None. Any Python object may be passed as the value argument.
    Postconditions:
        - The function always returns a Python bool (True or False).
        - No mutation of the input occurs.

## Side Effects:
    - None. The function performs a pure identity comparison and has no I/O, global state changes, or external service interactions.

## Control Flow:
flowchart TD
    Start[Start] --> Check{value is False?}
    Check -- yes --> RetTrue[return True]
    Check -- no --> RetFalse[return False]

## Examples:
    - Typical usage scenarios (described without embedding source lines):
        * When the caller needs to accept False as a distinct sentinel value but treat 0 or None differently:
            - Passing the boolean False returns True.
            - Passing 0, None, "", or an empty list returns False.
        * In template-test contexts where the template language supports a "false" test, this predicate enforces that only the literal boolean False matches.

    - Concrete results (informal):
        - test_false(False) -> True
        - test_false(0) -> False
        - test_false(None) -> False
        - test_false(runtime.Undefined()) -> False

## `src.jinja2.tests.test_true` · *function*

## Summary:
Return whether the given value is exactly the Python singleton True (identity check), producing a strict boolean result.

## Description:
This function performs a strict identity check to determine if the provided value is the built-in True object. It does not perform truthiness testing (so truthy values such as 1, "non-empty", or custom objects that evaluate to True will return False).

Known callers within the provided code snapshot:
- None identified in the provided source file context. The function is designed to be used wherever a template engine or other dispatching code needs to test whether a value is the literal True singleton (for example, when implementing template "tests" that distinguish True from other truthy values).

Why this logic is a separate function:
- It encapsulates a single, hard-to-misinterpret responsibility: distinguish the Python True singleton from all other values. Extracting this as its own function centralizes the identity-based test, avoids accidental substitution with truthiness checks, and makes the intent explicit to callers (they want "is True", not "truthy").

## Args:
    value (t.Any): Any Python object to test for identity with the True singleton.
        - Allowed values: any Python object.
        - Default: none (positional/required).
        - Notes: There are no interdependencies with other parameters.

## Returns:
    bool: True if and only if the argument is the exact built-in True object (value is True).
    - Possible return values:
        * True — when the argument is the True singleton.
        * False — for every other input, including:
            - False
            - None
            - 1 or 0 (integers)
            - "True" (string)
            - objects that evaluate truthily via __bool__ or __len__
            - custom objects equal to True via __eq__ but not the same object

## Raises:
    This function does not raise any exceptions for any input; it performs a simple identity comparison and always returns a bool.

## Constraints:
    Preconditions:
        - No preconditions. Any Python object may be passed as value.
    Postconditions:
        - The function returns a native bool (True or False).
        - The input value is not mutated.

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and makes no external calls.

## Control Flow:
flowchart TD
    A[Start: call test_true(value)] --> B{value is True?}
    B -- yes --> C[return True]
    B -- no --> D[return False]

## Examples:
    # Basic usage
    result = test_true(True)      # -> True
    result = test_true(False)     # -> False
    result = test_true(1)         # -> False (1 is truthy but not the True singleton)
    result = test_true("True")    # -> False

    # Defensive usage in code expecting a strict True:
    value_from_user = some_lookup()
    if test_true(value_from_user):
        perform_true_only_behavior()
    else:
        handle_non_true()

## `src.jinja2.tests.test_integer` · *function*

## Summary:
Determines whether a value is an integer type while explicitly excluding the boolean singletons True and False.

## Description:
This predicate returns True for Python int values (including int subclasses) but returns False for the boolean singletons True and False, which are a subclass of int in Python. It is intended to implement the runtime semantics of the "is integer" test used by the templating system: when a template or runtime asks whether a value "is integer" this function encodes that decision logic.

Known callers and typical context:
- The templating engine's test-dispatch mechanism uses this function to evaluate the "is integer" test during template rendering or expression evaluation. It is called when the template contains constructs such as `if value is integer` or when runtime code explicitly invokes the registered "integer" test.
- No file- or module-level callers are required to be listed here; the common usage is via the test registry / dispatch path within the template evaluation pipeline (i.e., it is a small, reusable predicate intended to be registered and invoked by the environment).

Reason for extraction:
- Separates the domain-specific decision "is an integer (but not a boolean)" from the rest of the templating evaluation logic so the test can be reused, registered, and unit-tested independently. It enforces a single responsibility: determine integer-ness with the explicit boolean exclusion.

## Args:
    value (typing.Any): The value to inspect. Any Python object is accepted. There are no other parameters.

## Returns:
    bool: True if and only if:
        - value is an instance of Python's built-in int type (isinstance(value, int) is True), and
        - value is not the boolean singleton True (identity check), and
        - value is not the boolean singleton False (identity check).
    Possible outcomes:
        - True: For ordinary integers (e.g., 0, 1, -5) and instances of subclasses of int (e.g., a custom class deriving from int), provided the object is not the True or False singleton.
        - False: For booleans True and False, for non-int numeric types (float, Decimal), for non-numeric types (str, list, None), and for numeric types that are not instances of built-in int (e.g., numpy.int64 instances are typically not instances of int).

## Raises:
    This function does not raise any exceptions by itself. It only performs type checks and identity comparisons on the provided value.

## Constraints:
    Preconditions:
        - None required; the function accepts any object.
    Postconditions:
        - The return value is always a boolean.
        - No mutation or side effects occur.

## Side Effects:
    - None. The function performs pure, read-only checks and does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start["Start: receive value"]
    IsInstance["isinstance(value, int)?"]
    IsTrueSingleton["value is True?"]
    IsFalseSingleton["value is False?"]
    ReturnTrue["return True"]
    ReturnFalse["return False"]

    Start --> IsInstance
    IsInstance -- No --> ReturnFalse
    IsInstance -- Yes --> IsTrueSingleton
    IsTrueSingleton -- Yes --> ReturnFalse
    IsTrueSingleton -- No --> IsFalseSingleton
    IsFalseSingleton -- Yes --> ReturnFalse
    IsFalseSingleton -- No --> ReturnTrue

## Examples:
- Common usage from a templating/test-dispatch perspective:
    - test_integer(42) -> True
    - test_integer(0) -> True
    - test_integer(-7) -> True

- Boolean singletons are excluded even though bool is a subclass of int:
    - test_integer(True) -> False
    - test_integer(False) -> False

- Subclass of int behaves like an int (unless it is the True/False singletons):
    - class MyInt(int): pass
    - test_integer(MyInt(1)) -> True

- Non-int numeric types and other values:
    - test_integer(3.0) -> False
    - test_integer(None) -> False
    - test_integer("1") -> False

Notes and edge-case considerations:
- The function uses identity checks (value is True / value is False) to exclude the True and False singletons specifically. Objects that are equal to True or False but are not the same singleton object (rare) will not be excluded by these identity checks.
- Some third-party numeric types (for example, numpy scalar types such as numpy.int64) are not instances of built-in int; behavior for such types depends on their class hierarchy and is not altered by this function beyond standard Python isinstance semantics.

## `src.jinja2.tests.test_float` · *function*

## Summary:
Determines whether the provided value is a Python float and returns True if so, otherwise False.

## Description:
This predicate performs a strict runtime type check: it returns True when the value is an instance of float (which includes instances of float subclasses) and False for all other types.

Known callers and usage context:
- The module-level context suggests this is intended as a Jinja2 "is" test predicate (used when a template expression uses "is float"); the function itself is a simple predicate suitable for registration with an environment's tests registry.
- There are no direct callers visible in this file. It can also be invoked directly by application code or unit tests that need a simple float-type check.

Why this is a separate function:
- Encapsulation: naming and extracting the check makes it easy to register, reuse, and test as the canonical "float" test used by the templating runtime.
- Single responsibility: keeps the templating wiring separate from the precise semantics of the float test (i.e., isinstance semantics).

## Args:
    value (t.Any): The object to test. Accepts any Python object.

## Returns:
    bool: True if and only if value is an instance of float (including instances of float subclasses); otherwise False.
    - True examples: 1.0, float('nan'), float('inf'), and instances of custom classes that inherit from float.
    - False examples: 1, Decimal('1.0'), fractions.Fraction(1, 2), None, "1.0", [], {}.

## Raises:
    This function does not raise exceptions under normal operation. The built-in isinstance call with a valid type argument will not produce an exception for any input value.

## Constraints:
    Preconditions:
    - None. The function accepts any value.

    Postconditions:
    - Always returns a Python bool.
    - Does not modify its input or any external state.

## Side Effects:
    - None. This function performs a pure, side-effect-free type check (no I/O, no globals mutated, no external calls beyond the safe builtin isinstance).

## Control Flow:
flowchart TD
    Start --> Check{isinstance(value, float)?}
    Check -- Yes --> ReturnTrue[return True]
    Check -- No  --> ReturnFalse[return False]
    ReturnTrue --> End
    ReturnFalse --> End

## Examples:
    # Basic usage
    result = test_float(3.14)         # True
    result = test_float(1)            # False

    # Special float values
    result = test_float(float('nan')) # True
    result = test_float(float('inf')) # True

    # Subclass of float
    class MyFloat(float):
        pass
    result = test_float(MyFloat(2.5)) # True

    # Non-float types
    result = test_float(None)         # False
    result = test_float("1.0")        # False

    # Typical templating scenario (conceptual)
    # When registered as the "float" test in the environment, the template runtime will call this predicate to evaluate "value is float".

## `src.jinja2.tests.test_lower` · *function*

## Summary:
Returns whether the string form of the provided value is lowercase, using Python's str.islower() semantics.

## Description:
A small, reusable predicate that coerces its input to a string and tests whether that string's cased characters (if any) are all lowercase. The function centralizes the conversion-to-string and lowercase-check so callers can perform this check via a single, well-named utility.

This documentation is based solely on the function implementation: it calls str(value) and then invokes the resulting string's islower() method.

## Args:
    value (str):
        - Typed as str in the function signature.
        - The implementation nevertheless calls the built-in str() on the argument, so any object that can be converted to a string is accepted.
        - No default value. Passing None will be converted to "None" and evaluated accordingly.

## Returns:
    bool:
        - The boolean result of str(value).islower().
        - According to Python's str.islower() rules: True only if the string contains at least one cased character and all cased characters are lowercase.
        - Returns False for empty strings and for strings containing no cased characters (for example, "123" or "!!!").

## Raises:
    - No exceptions are raised explicitly by this function.
    - Exceptions raised by str(value) (for example, if a user-defined __str__ raises) or by any unusual behavior of the object's __str__ will propagate to the caller.

## Constraints:
    Preconditions:
        - None required by the function; callers may pass any object.
        - For meaningful results, the value should be convertible to a string via str().
    Postconditions:
        - The function returns a boolean value.
        - The function does not modify its input or any external state.

## Side Effects:
    - The function itself has no side effects (no I/O, no global state mutation).
    - If the input object's __str__ implementation has side effects, those occur as part of the conversion and are not caused by this function.

## Control Flow:
flowchart TD
    Start --> Coerce[str(value)]
    Coerce --> CallIsLower[str(value).islower()]
    CallIsLower --> Return[return boolean result]
    Return --> End

## Examples:
- Typical cases:
    - test_lower("hello") -> True
    - test_lower("Hello") -> False
    - test_lower("") -> False  (empty string)
    - test_lower("123") -> False  (no cased characters)
    - test_lower(123) -> False  (str(123) == "123")

- Error propagation example:
    - If an object implements __str__ that raises ValueError, calling test_lower(obj) will propagate that ValueError to the caller.

## `src.jinja2.tests.test_upper` · *function*

## Summary:
Return True if the string representation of the provided value contains at least one cased character and every cased character is uppercase; otherwise return False.

## Description:
This predicate converts the input to a string using the built-in str() and returns the result of that string's isupper() method.

Known callers within the provided snapshot:
- No callers of this function are present in the provided repository fragment.

Why this logic is a separate function:
- Encapsulates the conversion-to-string and uppercase check in a single reusable predicate so callers do not duplicate this pattern.
- Facilitates unit testing and registration as a reusable predicate (for example, as a template test) by keeping the behavior in one place.

## Args:
    value (str):
        - The function signature is annotated with str, but the implementation accepts any object.
        - The function calls str(value) before applying isupper(), therefore any object convertible to a string is acceptable.
        - If the object's __str__ implementation raises an exception, that exception will propagate.

## Returns:
    bool:
        - True if str(value).isupper() returns True.
        - Per Python's str.isupper() semantics:
            * True when the string contains at least one cased character and every cased character is uppercase.
            * False for empty strings, strings with no cased characters (e.g., "123", "!?"), or strings that contain any lowercase cased character.
        - Examples:
            * "ABC" -> True
            * "AB1!" -> True
            * "abc" -> False
            * "" -> False
            * 123 -> False (str(123) == "123")
            * None -> False (str(None) == "None")

## Raises:
    Any exception raised by str(value):
        - The function does not raise exceptions itself.
        - If calling str(value) triggers an exception (for example, a custom __str__ that raises), that exception propagates to the caller.

## Constraints:
    Preconditions:
        - No special preconditions beyond providing a value that can be converted to a string; the caller may supply any object.
    Postconditions:
        - The function returns a boolean.
        - The input value is not mutated.

## Side Effects:
    - The function has no side effects: it performs no I/O, no network access, and does not modify external state.
    - Exceptions triggered by user-defined __str__ implementations are propagated but are not caused by this function's own side effects.

## Control Flow:
flowchart TD
    A[Start: call test_upper(value)] --> B[Compute s = str(value)]
    B --> C[Compute result = s.isupper()]
    C --> D{result is True?}
    D -->|Yes| E[Return True]
    D -->|No| F[Return False]

## Examples:
- Direct use:
    - test_upper("HELLO") -> True
    - test_upper("Hello") -> False
    - test_upper("") -> False
    - test_upper(123) -> False

- Exception propagation:
    - class Bad:
          def __str__(self):
              raise RuntimeError("bad")
      Calling test_upper(Bad()) will raise RuntimeError("bad"), propagated from Bad.__str__.

- Conceptual template usage (requires registering the function as a template test; registration is outside this function):
    - In a templating system where this predicate is registered as "upper", a template could use:
        {% if username is upper %} ... {% endif %}

## `src.jinja2.tests.test_string` · *function*

## Summary:
Returns True if the provided value is a Python string, otherwise False.

## Description:
This is a minimal predicate used to determine whether a value is a native Python text string (str). It performs a simple type check and is intended to be used wherever the codebase needs a canonical "is string" test — for example, by the template test dispatch when evaluating template expressions like `variable is string`. The function is deliberately small and focused so it can be registered or referenced by a central test/validation registry without duplicating logic.

Known callers within the provided snapshot:
- No direct internal callers are present in the single-function snapshot. Typical usage is through a test registry or template engine layer that dispatches named tests (e.g., the template evaluation stage when resolving `is string`).

Reason for extraction:
- Encapsulates the single-responsibility predicate for "is a string" so it can be reused, referenced by name in a registry, and unit-tested independently from template evaluation logic.

## Args:
    value (t.Any):
        The value to check. Any Python object is accepted; the function returns True only when the value is an instance of built-in str.
        - Allowed values: any Python object (None, numbers, sequences, mapping, custom objects, etc.)
        - There are no interdependencies with other parameters.

## Returns:
    bool:
        True if and only if value is an instance of the built-in Python str type; otherwise False.
        - Example outcomes:
            * value == "hello"  -> True
            * value == b"bytes" -> False
            * value == 123      -> False
            * value == None     -> False

## Raises:
    This function does not raise any exceptions for normal inputs.
    - If an unusual object implements a custom __instancecheck__ that raises, that exception would propagate (this is a property of isinstance mechanics, not of this function).

## Constraints:
    Preconditions:
        - No preconditions. Any Python object may be passed as `value`.
    Postconditions:
        - The function returns a boolean and does not mutate the input.
        - No external state is modified.

## Side Effects:
    - None. The function performs no I/O and does not modify global or external state.

## Control Flow:
flowchart TD
    Start["Start: call test_string(value)"]
    Check["isinstance(value, str)?"]
    True["Return True"]
    False["Return False"]
    Start --> Check
    Check -- yes --> True
    Check -- no --> False

## Examples:
    - Basic usage:
        result = test_string("hello")   # result is True
        result = test_string(42)        # result is False

    - Typical template-engine usage (conceptual):
        # Template expression "var is string" -> test dispatch invokes this predicate
        if test_string(resolved_variable):
            # treat as text
            ...
        else:
            # treat as non-text
            ...

## `src.jinja2.tests.test_mapping` · *function*

## Summary:
Return True if the given value is a Mapping (implements the collections.abc.Mapping interface); otherwise return False.

## Description:
This is a small predicate function that centralizes the "is a mapping" check performed using the Python abstract base class collections.abc.Mapping.

Known callers:
    - No direct internal callers were found in the provided repository graph for this function.
    - Intended usage: exported as a generic "mapping" test predicate (for example, to back template tests like "is mapping" or other runtime type checks). It is extracted into a named function so the mapping check is implemented consistently in one place and can be referenced or registered where predicate callables are required.

Responsibility and rationale for extraction:
    - Encapsulates the isinstance(value, abc.Mapping) check so callers do not duplicate the concrete ABC reference.
    - Provides a stable, single point to change mapping-detection logic if needed (for example to accept additional mapping-like types) without touching all call sites.

## Args:
    value (t.Any): Any Python object to be tested for the Mapping interface. No restrictions on the type of the input; can be None, primitives, containers, objects, etc.

## Returns:
    bool: True when value is an instance of collections.abc.Mapping (including subclasses); False otherwise.
    - Examples of True: dict(), dict subclass instances, instances of classes that register with or inherit from collections.abc.Mapping.
    - Examples of False: list, tuple, set, numbers, None, and objects that do not implement the Mapping interface.

## Raises:
    - This function itself does not raise exceptions for normal inputs because abc.Mapping is a valid class. The underlying isinstance call will only raise a TypeError if the second argument is not a class or tuple of classes; that is not applicable here because abc.Mapping is a class from the standard library. Therefore, no exceptions are raised by this implementation.

## Constraints:
    Preconditions:
        - The collections.abc.Mapping ABC is available (standard in Python's collections.abc).
        - The caller must provide a value argument (positional or keyword) matching the function signature.
    Postconditions:
        - The function always returns a boolean value (True/False).
        - No mutation of the argument or global state is performed.

## Side Effects:
    - None. The function performs a pure type-check and does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    A[Start] --> B{isinstance(value, abc.Mapping)?}
    B -- Yes --> C[Return True]
    B -- No --> D[Return False]

## Examples:
    - Typical usage:
        result = test_mapping({'a': 1})
        # result == True

    - Non-mapping:
        result = test_mapping([1, 2, 3])
        # result == False

    - Custom mapping-like object that inherits or registers with collections.abc.Mapping:
        from collections.abc import Mapping
        class MyMap(dict, Mapping):
            pass
        result = test_mapping(MyMap())
        # result == True

    - Defensive use inside calling code:
        if test_mapping(obj):
            # treat obj as a mapping (e.g., iterate .items())
            for k, v in obj.items():
                ...
        else:
            # handle non-mapping case
            ...

## `src.jinja2.tests.test_number` · *function*

## Summary:
Checks whether the given value is a numeric value according to Python's numbers.Number abstract base class and returns a boolean result.

## Description:
Known callers within the codebase:
- No direct call sites were discovered in the provided context. This function is declared in a module that provides predicate "tests" (likely for template expressions), so typical callers are template evaluation internals or code that needs to determine whether a value should be treated as numeric.

Typical trigger / pipeline stage:
- Invoked when code needs a simple predicate to decide if an object is a numeric type (e.g., validation, conditional template tests, or type-based formatting).

Why this logic is extracted into its own function:
- Single responsibility: encapsulates the numeric-type check in one place so other code (including template test dispatchers) can call it without duplicating isinstance checks.
- Reusability and testability: isolating the check makes it straightforward to register as a reusable "is number" predicate and to verify its behavior independently.

## Args:
    value (t.Any):
        Any Python object to be tested. The annotation is written as t.Any in the function signature; this matches the source-level type annotation. Note: the module must ensure the name t is defined (commonly via "import typing as t") for the annotation to be resolvable at definition time in some Python versions. The runtime behavior of the function does not depend on this annotation.

## Returns:
    bool:
        True if value is an instance of numbers.Number (the abstract base class imported as Number); otherwise False.

        Possible return values and notable cases:
        - True: for built-in numeric types such as int, float, complex, fractions.Fraction, decimal.Decimal where those types register as subclasses of numbers.Number.
        - True for booleans: bool is a subclass of int in Python, so True and False will evaluate as True for this test.
        - False for non-numeric types such as str, list, dict, None, and for custom objects that do not inherit from or register as numbers.Number.

## Raises:
    This function does not raise exceptions in normal operation.
    - Indirect possible import/definition errors:
        * If the module-level name Number (from numbers import Number) is missing or overwritten, calling the function could raise a NameError at function definition or runtime. In the provided source, Number is imported; therefore under normal circumstances no exception is raised.
        * If the annotation uses t.Any but t is not defined at module import time and annotations are evaluated immediately (depends on Python version and use of from __future__ import annotations), a NameError could occur during function definition. This is an annotation-level issue, not caused by the function body.

## Constraints:
Preconditions:
- No preconditions on the value argument — any Python object may be passed in.

Postconditions:
- The function returns a bool value.
- No mutation of the input object or external state is performed.

## Side Effects:
- None. The function performs a pure type check using isinstance and does not perform I/O, modify global variables, or call external services.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckIsInstance{isinstance(value, Number)?}
    CheckIsInstance -- Yes --> ReturnTrue[/return True/]
    CheckIsInstance -- No --> ReturnFalse[/return False/]

## Examples:
- Example 1 — typical outcomes:
    - Passing an integer (e.g., 3) yields True.
    - Passing a float (e.g., 3.14) yields True.
    - Passing a boolean (True) yields True because bool subclasses int.
    - Passing a string ("42") yields False.
    - Passing None yields False.

- Example 2 — usage context (textual):
    - A template engine's "is number" test can call this predicate during template evaluation to decide whether to apply numeric formatting or numeric-specific filters. Error handling is typically unnecessary because the function returns False for non-numeric inputs rather than raising.

## `src.jinja2.tests.test_sequence` · *function*

## Summary:
Performs a duck-typing check to determine whether a value behaves like a sequence by successfully supporting len() and exposing a __getitem__ attribute; returns True when both checks succeed, otherwise False.

## Description:
This helper performs a minimal, conservative sequence-like test using two operations:
1. Calls len(value) to verify the object reports a length without raising an exception.
2. Accesses value.__getitem__ to verify the object exposes an index-access attribute.

Both operations are performed inside a single try/except that catches any Exception; if either operation raises, the function returns False.

Known callers in the provided snapshot:
- No direct callers were found in the supplied code snapshot. The function is intended for use wherever a simple duck-typed "is sequence-like" predicate is required (for example, template test dispatchers or validation code), which is why the logic is kept as a small, focused function rather than repeated inline.

Why this logic is extracted:
- Encapsulates the duck-typing rules for "sequence-like" objects in one place so callers can rely on a single, well-documented predicate.
- Keeps caller code concise and avoids duplicating the try/except logic everywhere sequence-ness must be checked.

## Args:
    value (t.Any): The object to test. Annotated in the source as t.Any (accepts any Python object). There are no other parameters or interdependencies.

## Returns:
    bool: 
    - True if both of the following succeed without raising an exception:
        * len(value) completes (i.e., __len__ exists and does not raise)
        * value.__getitem__ attribute can be accessed
    - False if either operation raises any Exception.

    Edge cases:
    - Objects with __len__ implemented but whose __len__ raises an exception will yield False.
    - Objects with a lazily-evaluated __getitem__ attribute that raises on access will yield False.
    - Built-in sequence types (list, tuple, str, range, bytes) and mapping types (dict) will generally return True because they implement both operations; note that mapping types are considered "sequence-like" by this predicate because they expose __len__ and __getitem__.

## Raises:
    None. The function catches all Exceptions raised by the checks and converts them into a False result. It does not re-raise exceptions.

## Constraints:
Preconditions:
    - None required. The function accepts any object; callers need not validate the input type beforehand.

Postconditions:
    - The function returns True only if the object supports len() and exposes __getitem__ without raising during those checks.
    - No exceptions escape the function; failures in the checks result in False.

## Side Effects:
    - None. The function does not perform I/O, mutate global state, call external services, or modify the tested object. It only performs inspected operations (len and attribute access).

## Control Flow:
flowchart TD
    Start --> TryOperations
    TryOperations --> LenCall[len(value)]
    LenCall --> GetItemAccess[value.__getitem__]
    GetItemAccess --> Success[no exception -> return True]
    LenCall -->|Exception raised| Fail[return False]
    GetItemAccess -->|Exception raised| Fail
    Success --> End
    Fail --> End

## Examples:
- Basic usage:
    - test_sequence([1, 2, 3]) -> True
    - test_sequence("hello") -> True
    - test_sequence({"a": 1}) -> True  (dicts expose __getitem__ and len)
    - test_sequence(42) -> False
    - test_sequence(None) -> False

- Typical pattern in calling code:
    - Use the predicate when you need to branch logic depending on whether a value behaves like a sequence (duck-typed) without wanting to rely on concrete types or ABC checks.

- Example with error-tolerant caller:
    - result = test_sequence(maybe_value)
      if result:
          # safe to use len(maybe_value) and index access (e.g., maybe_value[0])
      else:
          # handle non-sequence case

Notes:
- This function purposely uses a broad except Exception clause to ensure that any unexpected behavior during the two checks (including TypeError, AttributeError, or user-defined exceptions raised from descriptors) results in a conservative False. If callers require finer-grained behavior, they should implement or wrap a stricter check.

## `src.jinja2.tests.test_sameas` · *function*

## Summary:
Performs a strict identity comparison and returns True only when both arguments reference the exact same Python object.

## Description:
A minimal utility that evaluates object identity using the Python `is` operator. It is implemented as a separate test function in the template-tests module and is intended to serve as the implementation of the Jinja2 "sameas" test (i.e., the semantics used when a template evaluates `a is sameas b`).

Known callers within the provided repository snapshot:
- No direct call sites were present in the provided snapshot. Semantically this function is intended to be invoked by the template runtime when evaluating "sameas" tests in templates or by other code that requires identity comparison rather than equality.

Why this logic is extracted into its own function:
- Encapsulates identity semantics (object identity vs. equality) in a single, named place so callers do not confuse `is` with `==`.
- Keeps template-engine test implementations small and easily registerable/unregisterable.
- Avoids inlining `is` checks throughout the codebase, improving clarity and reducing duplication.

## Args:
    value (t.Any): First object to compare. The source annotation uses `t.Any`.
    other (t.Any): Second object to compare. The source annotation uses `t.Any`.
Notes:
- The documentation intentionally reflects the function signature as written in source (parameters annotated with `t.Any`). No further assumptions about module-level aliases are made.
- There are no interdependencies between parameters; each may be any Python object.

## Returns:
    bool: True if and only if `value is other` (both names refer to the identical Python object). False otherwise.
Possible return scenarios:
- True: When both parameters are the same object (for example, the same list instance, the same object reference returned from a factory, or the singleton None).
- False: When parameters are distinct objects, even if `value == other` evaluates True (e.g., two separate but equal lists).

## Raises:
    This function does not raise exceptions for normal inputs. It performs a direct identity check and accepts any Python object, including None, user-defined objects, and builtin types.

## Constraints:
Preconditions:
- None. The function accepts any Python object for either parameter.

Postconditions:
- A boolean value is returned indicating identity.
- No state is mutated and no external side effects occur.

## Side Effects:
- None. The function is pure: no I/O, no global mutation, no network or database access.

## Control Flow:
flowchart TD
    Start --> EvaluateIdentity
    EvaluateIdentity -->|value is other is True| ReturnTrue
    EvaluateIdentity -->|value is other is False| ReturnFalse
    ReturnTrue --> End
    ReturnFalse --> End

## Examples:
- Identity of the same mutable object:
    lst = []
    test_sameas(lst, lst)  -> True

- Two distinct but equal objects:
    a = [1, 2]
    b = [1, 2]
    test_sameas(a, b)  -> False  # equal by value (a == b) but not the same object

- Singletons and interned values:
    test_sameas(None, None)  -> True  # None is a singleton
    test_sameas(1, 1)  -> True or False depending on Python's small-integer interning (commonly True for small ints)
    test_sameas("hello", "hello")  -> True or False depending on string interning

- Distinct numeric objects with same value:
    x = 1.0
    y = 1.0
    test_sameas(x, y)  -> False  # floats are often distinct objects even if equal in value

- Practical template-level usage (conceptual):
    In a template that supports this test as "sameas":
    {{ a is sameas b }}
    This evaluates to True only when `a` and `b` are the same Python object.

## `src.jinja2.tests.test_iterable` · *function*

## Summary:
Checks whether a value is iterable by attempting to obtain an iterator and returns a boolean indicating the result.

## Description:
This small utility attempts to call the built-in iter() on the provided value and returns True if iter(value) succeeds, or False if iter(value) raises a TypeError. It is a concise predicate used to guard code paths that require iteration (for example, template logic that only iterates over values confirmed to be iterable).

Known callers within the codebase:
- No direct call sites were found in the provided repository snapshot. Typical usage in similar codebases: used by template tests, filters, or helper utilities to decide whether to iterate over a value or treat it as a single value.

Why this logic is extracted:
- The check is a simple, well-scoped utility: it encapsulates the canonical Python way to test iterability (calling iter() and catching TypeError). Extracting it avoids repeated try/except blocks throughout the codebase and centralizes the policy of "only treat as iterable when iter() does not raise TypeError." It deliberately does not try to coerce or convert values; it only observes whether they are iterable.

## Args:
    value (t.Any): Any Python object to test for iterability. There are no additional constraints on the input; any object may be passed. The function does not mutate the input.

Notes:
- The type annotation uses t.Any in the function signature. This mirrors the source signature; it is expected that t refers to the typing module alias in the source context.

## Returns:
    bool: True if calling iter(value) does not raise a TypeError (i.e., the value is iterable in Python terms), False if iter(value) raises a TypeError.

Possible return behaviors / edge cases:
- For standard built-in iterability: lists, tuples, dicts, sets, strings, range, generators, and objects implementing __iter__/__getitem__ will return True.
- If value is None or a plain Number (without iteration support), iter(value) will raise TypeError and the function returns False.
- If value.__iter__ or the object’s iterator raises an exception other than TypeError when invoked, that exception is not caught by this function and will propagate to the caller (see Raises).

## Raises:
- No exceptions are raised directly by the function under normal circumstances.
- Any exception raised by iter(value) other than TypeError will propagate unchanged to the caller. In particular, if a custom object's __iter__ implementation raises ValueError, RuntimeError, AttributeError, or any other exception, that exception will not be caught here.

Exact conditions:
- TypeError from the built-in iter() call is caught and handled by returning False.
- Any other exception type raised by iter(value) is not caught and will surface.

## Constraints:
Preconditions:
- Caller must provide a value argument (no explicit None-check required by this function; None is a valid input and will return False).
- No other preconditions (no authentication, no environment state required).

Postconditions:
- The function returns a boolean that accurately reflects whether iter(value) succeeded without raising a TypeError.
- No mutations to the input or global state are performed.

## Side Effects:
- None: the function performs no I/O, does not modify global variables, and does not call external services. It only invokes the built-in iter() on the provided object.

## Control Flow:
flowchart TD
    A[Start: call test_iterable(value)] --> B[Call iter(value)]
    B -->|iter raises TypeError| C[Return False]
    B -->|iter succeeds| D[Return True]
    B -->|iter raises other Exception| E[Propagate exception to caller]

## Examples (usage described, not raw code):
- Typical positive example: pass a list or generator object; iter(value) succeeds and the function returns True. Use this result to decide whether to loop over the value in template rendering code.
- Typical negative example: pass None or an int; iter(value) raises TypeError, the function returns False, and the caller can handle the non-iterable case (e.g., render a fallback).
- Exception propagation example: if a custom object's __iter__ method raises ValueError when called, test_iterable will not catch the ValueError; the caller should wrap the call to test_iterable in a try/except if it must handle such custom iterator errors explicitly.
- Defensive usage pattern (described):
    1. Optionally call test_iterable(value).
    2. If True, safely iterate over value.
    3. If False, treat value as a single item or use a fallback rendering.
    4. If there is concern that custom iterator implementations may raise non-TypeError exceptions, surround the call with a try/except to handle those cases.

## `src.jinja2.tests.test_escaped` · *function*

## Summary:
Return True if the supplied object exposes an __html__ attribute or method (indicating it can render safe HTML); otherwise return False.

## Description:
A minimal predicate that checks whether a value provides an __html__ attribute or method by delegating to Python's attribute lookup machinery. This single-purpose function centralizes the __html__ presence check so callers (for example, template evaluation or test registries) can consistently decide whether a value should be treated as already HTML-safe.

Known callers within this repository are not enumerated here. Typical usage is within template-evaluation paths or tests where the runtime must decide whether to escape a value before rendering; extracting this logic ensures a single, testable definition of "escaped-like" objects.

Why this is factored out:
- The check is a small, well-scoped responsibility (presence of __html__). Extracting it prevents duplicated attribute-checking logic and makes behavior easier to test and to replace if the criteria change.

## Args:
    value (t.Any): The object to inspect. Any Python value is accepted (None, primitives, objects, callables, etc.). This parameter is required.

## Returns:
    bool: True if hasattr(value, "__html__") evaluates to True; otherwise False.
    - True: the attribute lookup succeeded (the object exposes an attribute or callable named "__html__").
    - False: the attribute lookup completed and reported the attribute as absent (hasattr returned False).

## Raises:
    - Any exception that arises from attribute lookup other than AttributeError will propagate out of the function.
      * Rationale: hasattr uses getattr internally and returns False only when getattr raises AttributeError. If getattr (or an object's __getattr__/descriptor) raises another exception type (for example TypeError, ValueError, or a custom exception), that exception is not converted to False by hasattr and will therefore propagate from this function.

## Constraints:
Preconditions:
    - The caller must supply a valid Python object for value. No other preconditions are required.

Postconditions:
    - On normal completion (no propagated exception), a boolean value is returned.
    - The function does not modify the supplied object or any global state.

## Side Effects:
    - The function performs attribute lookup which may trigger user-defined attribute access logic (such as __getattr__, properties, or descriptors). Any side effects caused by those user-defined accessors are a property of the inspected object, not of this function itself.
    - No I/O, network calls, stdout writes, or persistent state changes are performed by this function.

## Control Flow:
flowchart TD
    Start --> Call_hasattr
    Call_hasattr -->|hasattr returns True| ReturnTrue
    Call_hasattr -->|hasattr returns False| ReturnFalse
    Call_hasattr -->|hasattr triggers non-AttributeError exception| PropagateException
    ReturnTrue --> End
    ReturnFalse --> End
    PropagateException --> End

## Examples:
- Positive example (object defines __html__):
    - A wrapper object that implements an __html__ method will cause the predicate to return True. Template code using this predicate can skip escaping such objects.

- Negative example (no __html__):
    - Built-in types (e.g., plain str, int, list) that do not define __html__ will yield False.

- Example of propagated exception (defensive usage):
    - If an inspected object's attribute access raises TypeError or another non-AttributeError exception, the caller may want to guard the test:
      - Use try/except around this predicate when you expect objects with buggy or side-effecting attribute accessors and need to recover cleanly.

## `src.jinja2.tests.test_in` · *function*

## Summary:
Evaluate whether a value is a member of a sequence-like container and return True if it is, False otherwise.

## Description:
This small predicate performs a Python membership test using the built-in membership semantics (the in operator) and returns the boolean result. Known callers in the repository scan: none discovered (no direct call sites were found in the available code snapshot). Typical usage is as a predicate used by the templating/test subsystem to implement an "in" test that templates can use to check membership — it is separated as a distinct function to provide a single, testable implementation of the membership check which can be registered, mocked, or extended independently of template rendering logic.

The logic is extracted into its own function to:
- Encapsulate the membership check behind a stable callable interface used by the test registry.
- Make the operation easily replaceable or instrumentable (e.g., for custom behavior or testing).
- Keep template evaluation code free of raw operator expressions, improving clarity and testability.

## Args:
    value (t.Any): The item to search for. May be any Python object.
    seq (t.Container): The container to search in. Expected to support the Python membership protocol (e.g., implement __contains__ or be iterable). The annotation reflects the type hint in the function signature; at runtime any object is accepted but behavior depends on whether membership is supported.

Interdependencies:
    - None required between value and seq beyond the standard membership semantics. If seq does not support membership testing, the operation may raise an exception (see Raises).

## Returns:
    bool: True if value is considered a member of seq according to Python's membership protocol, False otherwise.
    - Possible return values:
        * True: value is found in seq via seq.__contains__(value) or by iteration-based membership.
        * False: value is not found.
    - Edge-case return behavior:
        * If seq is a container whose __contains__ returns a non-boolean truthy/falsy value, Python truthiness rules will govern the result (the expression coerces to bool for the return).

## Raises:
    TypeError: If the seq argument does not support membership testing (for example, if it is None and its type does not implement containment) or if the underlying membership operation implementation raises TypeError.
    Any exception raised by seq.__contains__(value) or by iteration used for membership will propagate unchanged. For example, a custom container that raises ValueError from its __contains__ will cause this function call to raise that ValueError.

## Constraints:
Preconditions:
    - Caller should pass an object for seq that implements the membership protocol (ideally a collections.abc.Container or other iterable).
    - value may be any object; no coercion is performed by this function.

Postconditions:
    - No mutations are performed on value or seq by this function.
    - The function returns a boolean reflecting membership, or it propagates exceptions from the underlying membership check.

## Side Effects:
    - None intrinsic to this function: it does not perform I/O, mutate global state, or call external services.
    - Side effects can occur if seq.__contains__ or iteration have user-defined side effects; such side effects are external to this function and will be performed as part of the membership evaluation.

## Control Flow:
flowchart TD
    Start --> CheckMembership[Perform "value in seq"]
    CheckMembership -->|membership True| ReturnTrue[Return True]
    CheckMembership -->|membership False| ReturnFalse[Return False]
    CheckMembership -->|membership raises exception| Propagate[Propagate the exception]

## Examples:
- Successful membership:
    - Given value = 'a' and seq = ['a', 'b'], the function yields True because 'a' is present in the list.

- Not a member:
    - Given value = 5 and seq = (1, 2, 3), the function yields False because 5 is not present.

- Error propagation:
    - If seq is None or an object whose membership operation does not exist or raises, the function will raise the same exception. Example scenario: seq is an object whose __contains__ implementation raises ValueError; calling this function will propagate that ValueError to the caller. Callers that must tolerate such cases should catch the appropriate exceptions around the call.

