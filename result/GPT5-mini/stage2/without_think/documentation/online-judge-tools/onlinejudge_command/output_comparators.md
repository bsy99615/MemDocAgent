# `output_comparators.py`

## `onlinejudge_command.output_comparators.OutputComparator` · *class*

## Summary:
Abstract base class that defines the interface for comparing two byte sequences (actual and expected) and returning a boolean result.

## Description:
OutputComparator is an interface (abstract base) that declares a single operation: calling an instance with (actual: bytes, expected: bytes) to determine whether the two byte sequences should be considered matching. Subclasses must implement the __call__ method to provide a concrete comparison policy (for example: strict byte-wise equality, normalized numeric comparison, tolerance-aware floating-point comparison after text decoding, or whitespace-insensitive comparison).

Use this class when you want to provide interchangeable comparator implementations that can be invoked via a common callable interface: comparator(actual_bytes, expected_bytes) -> bool.

## State:
- This class itself has no instance attributes defined in the base implementation.
- There are no required __init__ parameters in the base class.
- Valid inputs:
  - actual: bytes — raw output produced by the program under test.
  - expected: bytes — reference output to compare against.
- Return:
  - bool — True when the comparator considers the two byte sequences to match, False otherwise.
- Invariants:
  - Implementations must accept two bytes objects as positional arguments.
  - Implementations must return a bool and should not mutate the provided byte arguments.

## Lifecycle:
- Creation:
  - The base class inherits from abc.ABC and declares an abstract method; it cannot be instantiated directly unless a concrete subclass overrides __call__.
  - To instantiate, create a subclass that provides a concrete implementation of __call__.
- Usage:
  - Typical usage is: comparator_instance(actual_bytes, expected_bytes)
  - There is no required call ordering beyond instantiation followed by invocation(s) of __call__.
  - Implementations are expected to be reentrant and side-effect free (pure functions are preferred), but this is a guideline for implementers rather than an enforced constraint in the base class.
- Destruction:
  - No special cleanup or resource management is required by the base class (no context-manager protocol or close method provided). If a concrete subclass acquires external resources, that subclass must manage cleanup itself.

## Method Map:
graph LR
    A[Instantiate concrete subclass] --> B[__call__(actual: bytes, expected: bytes) -> bool]
    B --> C{Return True/False}
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style C fill:#bfb,stroke:#333,stroke-width:1px

## Raises:
- Instantiation:
  - TypeError will be raised by abc machinery if you attempt to instantiate OutputComparator directly (because it has an abstract __call__).
- __call__:
  - The base-class __call__ implementation raises NotImplementedError; calling OutputComparator.__call__ (i.e., not overridden) will raise NotImplementedError.
  - Concrete implementations may raise other exceptions depending on their decoding/parsing strategy (e.g., UnicodeDecodeError, ValueError) — these are implementation-specific and not raised by the base class itself.

## Example:
- Implementer intent (textual example, no class definition shown):
    1. Provide a subclass that implements __call__ to return True when actual == expected (simple byte-wise equality).
    2. Instantiate that subclass: comparator_instance = <your-concrete-comparator>()
    3. Invoke comparison: result = comparator_instance(b'1 2 3\n', b'1 2 3\n')  # expected True for equal bytes
    4. For a tolerant comparator, implement __call__ to decode bytes to text, normalize whitespace and numeric formats, then return True/False accordingly.

Notes:
- The base class only enforces the callable interface and result type; it does not prescribe how comparison is performed — that responsibility is left to subclasses.

### `onlinejudge_command.output_comparators.OutputComparator.__call__` · *method*

## Summary:
A callable comparator that decides whether two byte sequences (actual and expected program outputs) should be considered equivalent. The base implementation is abstract and raises NotImplementedError; concrete subclasses implement the comparison policy. This method is intended to be a pure, deterministic predicate and does not modify the comparator object by default.

## Description:
This abstract method defines the interface for comparing process output to an expected output artifact. The method is declared on an abstract base class, so concrete OutputComparator subclasses implement the comparison logic (for example: exact binary equality, text-normalized equality, numeric-tolerant comparison, token-based comparison, etc.).

Known callers:
- No direct call sites are present in the provided source excerpt. Typical callers (in a judge/run pipeline) are the piece of code that receives the program's captured stdout/stderr as bytes and the test's expected output bytes, and needs to decide whether the submission's output passes the test. Because this is an abstract method, actual invocations occur via subclass instances referenced polymorphically.

Why this is a separate method:
- Encapsulates comparison policy behind a small, well-defined interface to allow multiple interchangeable comparator implementations.
- Keeps the evaluation pipeline decoupled from comparison details (normalization rules, numeric tolerance, whitespace handling, binary vs text modes).
- Enables testing and reuse of comparison logic independently of the rest of the judge.

## Args:
    actual (bytes):
        - The output produced by the program under test.
        - Must be a bytes object (binary sequence). Implementations may interpret it as text using a chosen encoding, but the method contract requires callers to pass bytes.
    expected (bytes):
        - The canonical expected output for the test case.
        - Must be a bytes object. Implementations may decode or parse it as needed.

## Returns:
    bool:
        - True if the comparator considers the two byte sequences equivalent according to its policy; False otherwise.
        - There is no partial or probabilistic return: callers should treat True as "pass" and False as "fail".
        - Edge cases:
            * If both actual and expected are empty bytes (b''), a reasonable comparator implementation should return True unless a subclass documents otherwise.
            * Implementations may treat different encodings, trailing newlines, or line-ending differences as equivalent if that behavior is documented by the subclass.

## Raises:
    NotImplementedError:
        - Always raised by the base abstract implementation to indicate that subclasses must override this method.
    (Subclass-specific):
        - Concrete implementations may raise other exceptions (e.g., UnicodeDecodeError if they decode bytes without handling invalid sequences, ValueError for malformed numeric tokens, MemoryError for extremely large inputs). Any such exceptions are implementation-specific and must be documented on the subclass.

## State Changes:
    Attributes READ:
        - None known from the provided base-class excerpt. Concrete subclasses may read their own configuration attributes (for example, self.tolerance, self.normalize_whitespace) — document those on the subclass.
    Attributes WRITTEN:
        - The base implementation does not write to any self.* attributes. Implementations SHOULD avoid mutating instance state during comparison; if a subclass records diagnostics or statistics then those mutations must be documented.

## Constraints:
    Preconditions:
        - The caller must pass two bytes objects. Calling with non-bytes values violates the documented signature and may cause subclass implementations to fail.
        - Comparators should assume inputs can be arbitrarily large; implementations should consider memory/time complexity.
    Postconditions:
        - The method returns a boolean and does not intentionally modify the provided byte objects.
        - The comparator should be deterministic: given the same inputs and comparator configuration, it must return the same boolean result.

## Side Effects:
    - The base method has no I/O or external effects and should not perform logging, network calls, or file writes. Subclasses should avoid side effects during comparison; if logging or diagnostics are produced, they must be explicitly documented on the subclass implementation.

## Implementation guidance for subclasses (recommended contract):
    - Treat the method as a pure function: avoid mutating self or the arguments.
    - Validate argument types immediately and raise TypeError if either argument is not bytes (optional but recommended).
    - Decide and document the comparison policy clearly (exact binary, normalized text, numeric tolerance, etc.).
    - If decoding bytes to text, document the encoding used and how decoding errors are handled (e.g., 'utf-8' with 'replace' or strict).
    - For floating-point tolerant comparisons, document numeric tolerance semantics (absolute vs relative, how NaNs/Inf are handled).
    - Be explicit about how trailing whitespace and line-ending differences are treated.
    - Keep performance in mind: avoid unnecessary copies for large byte sequences; consider streaming comparisons for very large outputs.

## `onlinejudge_command.output_comparators.ExactComparator` · *class*

## Summary:
ExactComparator is a concrete OutputComparator that implements strict, byte-wise equality comparison between the actual and expected outputs.

## Description:
ExactComparator is used when the correct behavior is defined as exact binary equivalence of program output and reference output — no decoding, normalization, tolerance, or whitespace normalization is performed. Instantiate this comparator when the test evaluation requires that the produced output bytes match the expected bytes exactly (for example, when outputs include binary data, exact spacing/newlines are significant, or when any change should be treated as a mismatch).

Typical usage:
- Test runners or evaluation harnesses that accept interchangeable comparator implementations will create an ExactComparator instance and call it with (actual_bytes, expected_bytes) to determine pass/fail.
- Use this comparator when you do not want any interpretation or transformation of bytes (no text decoding, no numeric tolerance).

Responsibility boundary:
- ExactComparator's only responsibility is to decide if two bytes objects are identical using Python's equality operator. It does not perform type coercion, decoding, or normalization. Any preprocessing must be done by the caller before invoking this comparator.

## State:
- This class has no instance attributes; it is stateless.
- __init__:
  - No parameters (inherits default constructor from object / OutputComparator).
  - No side effects.
- Valid inputs:
  - actual (bytes): Raw bytes produced by the tested program.
  - expected (bytes): Reference bytes to compare against.
- Return:
  - bool — True if actual == expected (byte-wise equality), False otherwise.
- Invariants:
  - Instances are pure/value-like: repeated calls with the same inputs must return the same result.
  - ExactComparator does not modify the provided actual or expected objects.

## Lifecycle:
- Creation:
  - Instantiate with no arguments: comparator = ExactComparator()
  - No factory methods are required.
- Usage:
  - Single-step usage: call the instance with two positional arguments (actual, expected).
  - The comparator is reentrant and can be reused for multiple comparisons in any order.
  - There is no required sequencing beyond instantiation then calls.
- Destruction:
  - No cleanup required. The class does not manage external resources and does not implement context-management methods.

## Method Map:
graph LR
    A[Instantiate ExactComparator] --> B[__call__(actual: bytes, expected: bytes) -> bool]
    B --> C{actual == expected?}
    C -->|True| D[Return True]
    C -->|False| E[Return False]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style C fill:#ffd,stroke:#333,stroke-width:1px
    style D fill:#bfb,stroke:#333,stroke-width:1px
    style E fill:#fbb,stroke:#333,stroke-width:1px

## Raises:
- ExactComparator itself does not explicitly raise exceptions.
- Notes on runtime behavior:
  - The implementation performs a Python equality comparison. If callers pass non-bytes objects, Python's equality semantics apply:
    - Comparing bytes to a non-bytes object normally returns False, not an exception.
    - If a non-bytes object implements an __eq__ that raises an exception, that exception will propagate; such behavior is outside the responsibility of ExactComparator.
  - No decoding, parsing, or numeric conversions are attempted, so decoding-related exceptions (UnicodeDecodeError) do not originate from this comparator.

## Example:
- Create and use the comparator (illustrative, not source code):
    1. Instantiate: comparator = ExactComparator()
    2. Compare equal byte sequences: result = comparator(b'output\n', b'output\n')  # returns True
    3. Compare differing byte sequences: result = comparator(b'output\n', b'output \n')  # returns False
    4. Reuse: comparator(b'', b'')  # returns True for two empty byte sequences

### `onlinejudge_command.output_comparators.ExactComparator.__call__` · *method*

## Summary:
Performs a strict byte-for-byte equality comparison between two byte sequences and returns True if they are identical; the method is pure and does not alter the comparator's state.

## Description:
This method implements the exact-match strategy for an OutputComparator by applying Python's equality operator to the provided byte sequences. It is separated into its own callable to allow swapping different comparison strategies (e.g., whitespace-insensitive, token-based) through the OutputComparator interface without modifying caller code.

Known callers / invocation context:
- Intended to be invoked wherever an OutputComparator instance is used as a callable, e.g., comparator(actual, expected) during a test runner, judge verification step, or any output-checking pipeline.

Why separate:
- Encapsulates the "exact match" semantics so that different comparator implementations can be substituted and individually unit-tested.

## Args:
    actual (bytes): The actual output produced by the program under test. Must be a bytes object (encode textual output, e.g., using UTF-8, before calling).
    expected (bytes): The expected output to compare against. Must be a bytes object.

## Returns:
    bool: True if and only if actual == expected under Python's equality semantics; otherwise False.

    Edge cases:
    - Empty sequences: b'' == b'' -> True.
    - Different lengths: always False.
    - Cross-type equality: bytes == str evaluates to False; bytes == bytearray may evaluate to True if the byte contents are identical.

## Raises:
    None. The method itself does not raise exceptions. Passing values that are not bytes will result in Python's normal equality behavior (no guarantees beyond that); callers should provide bytes to get predictable exact-match semantics.

## State Changes:
    Attributes READ: none
    Attributes WRITTEN: none

## Constraints:
    Preconditions:
    - Both arguments should be bytes. The comparator performs no normalization (trimming, newline canonicalization, decoding) before comparison.
    - If the test output is textual, callers must encode both actual and expected using the same encoding.

    Postconditions:
    - Returns True exactly when the two arguments compare equal under Python's equality operator.
    - The comparator instance remains unchanged.

## Side Effects:
    - None. The method performs an in-memory comparison and produces no I/O, logging, or external calls.

## `onlinejudge_command.output_comparators.FloatingPointNumberComparator` · *class*

## Summary:
A callable comparator that attempts to treat inputs as floating-point values and compare them using configurable relative and absolute tolerances; when either input cannot be converted to a float, it falls back to strict bytes equality.

## Description:
This class is intended for use in output-comparison workflows where outputs are typically numeric but may differ by small floating-point rounding errors. Instantiate it with desired tolerances and use the instance as a function-like comparator (via its __call__ method) to compare an "actual" and an "expected" output.

Typical callers:
- Test harnesses, judge runners, or frameworks that support pluggable output comparators.
- Higher-level adapters that decode program output into text and then invoke comparators.

Why this abstraction:
- Encapsulates the decision: "If both sides are numeric, compare numerically with tolerances; otherwise compare bytes exactly."
- Keeps numeric-tolerance logic isolated from tokenization, whitespace handling, or multi-value comparison, which should be handled elsewhere.

Relationship to other classes:
- Inherits from OutputComparator (a callable comparator interface). It implements the callable comparison behavior expected by that interface.

## State:
Attributes (public, set once at construction):
- rel_tol (float)
  - Meaning: relative tolerance forwarded to math.isclose.
  - Constraints: should be a non-negative float for normal operation. If rel_tol < 0, math.isclose may raise ValueError when used.
  - Default: none; rel_tol is required as a keyword argument to __init__.
  - Invariant: stored exactly as provided; not modified by the class.

- abs_tol (float)
  - Meaning: absolute tolerance forwarded to math.isclose.
  - Constraints: should be a non-negative float for normal operation. If abs_tol < 0, math.isclose may raise ValueError when used.
  - Default: none; abs_tol is required as a keyword argument to __init__.
  - Invariant: stored exactly as provided; not modified by the class.

Constructor-side behavior:
- If max(rel_tol, abs_tol) > 1, the constructor emits a warning through the module logger to indicate unusually large tolerances. This is a warning only; no exception is raised.

Class invariants:
- After construction, rel_tol and abs_tol remain constant for the instance lifetime.
- __call__ will always use the stored rel_tol and abs_tol for numeric comparisons.

## Lifecycle:
Creation:
- Call FloatingPointNumberComparator(rel_tol=<float>, abs_tol=<float>) using keyword arguments.
- Both rel_tol and abs_tol are required; the __init__ signature enforces keyword-only parameters.

Usage (typical sequence):
1. Instantiate comparator = FloatingPointNumberComparator(rel_tol=..., abs_tol=...).
2. For each comparison, call comparator(actual, expected) where actual and expected are the values to compare.
   - The implementation annotates actual and expected as bytes in its signature, but see the "Important type note" below.
3. Each call is independent and side-effect free (except logging at construction). Instances are reusable and stateless between calls.

Destruction:
- No resources to free. No context-manager or close() API is provided or required.

Important type note (critical for correctness):
- The source code calls float(actual) and float(expected). In Python 3, passing a bytes object to float() raises TypeError (float() expects a string or a number, not 'bytes'). Although the method signature is annotated as taking bytes, typical correct usage is to pass decodable str objects (e.g., decoded text) or numeric types (int/float) rather than raw bytes — or to decode bytes to str before calling the comparator.
- If you must pass bytes, ensure the caller decodes them to str (e.g., actual.decode('utf-8')) before invoking the comparator, otherwise a TypeError will likely be raised.

## Method Map:
flowchart LR
    A[Instantiate] --> B[__init__(rel_tol, abs_tol)]
    B -->|stores rel_tol & abs_tol| C{rel_tol, abs_tol}
    C --> D[Call comparator(actual, expected)]
    D --> E[__call__]
    E --> F[Attempt x = float(actual)]
    F -- ValueError --> H[mark x=None]
    F -- TypeError --> R[TypeError propagates -> caller sees exception]
    H --> G[Attempt y = float(expected)]
    G -- ValueError --> I[mark y=None]
    G -- TypeError --> R
    I --> J{both x and y are not None?}
    J -- yes --> K[return math.isclose(x, y, rel_tol, abs_tol)]
    J -- no --> L[return actual == expected]

(Readable summary: instantiate -> store tolerances -> on call: try converting each side with float(); if both succeed: use math.isclose with stored tolerances; if either conversion failed with ValueError: fall back to strict equality; if conversion raised TypeError it will propagate.)

## Raises:
- __init__:
  - Does not raise for numeric rel_tol/abs_tol values; it only logs a warning when tolerances exceed 1.
  - If the caller passes values whose evaluation raises TypeError/ValueError before calling __init__, those originate from the caller (not the class).

- __call__(actual, expected) may raise:
  - TypeError: If actual or expected is a bytes object (or another type not accepted by float()), float(...) raises TypeError; since the implementation only catches ValueError, that TypeError will propagate. Therefore, passing raw bytes (the annotation) will typically result in TypeError unless the bytes are decoded first.
  - ValueError: If both actual and expected successfully convert to float but rel_tol or abs_tol are negative, math.isclose will raise ValueError (math.isclose requires non-negative tolerances). In that case, __call__ will propagate the ValueError.
  - Other exceptions from float(...) (rare): float() may raise other exceptions for very unusual inputs; such exceptions are not explicitly caught by __call__ and will propagate.

Notes about handled vs. unhandled conversion failures:
- The implementation catches ValueError from float(...) and treats the corresponding side as "non-numeric" (x or y set to None). That leads to the fallback strict equality branch when either side is non-numeric (ValueError path).
- TypeError from float(...) is not caught and will propagate to the caller; callers should avoid passing bytes.

## Behavior details and edge cases:
- Numeric comparison:
  - When both actual and expected successfully convert to floats, the comparator returns math.isclose(x, y, rel_tol=self.rel_tol, abs_tol=self.abs_tol).
  - math.isclose implements float closeness semantics: NaNs are not considered equal (isclose returns False when either value is NaN), infinities are compared according to IEEE semantics, and tolerances are applied as documented by Python's math.isclose.
- Fallback equality:
  - If either conversion raises ValueError (non-numeric strings), the comparator returns actual == expected (strict bytes/sequence equality). No whitespace normalization or tokenization occurs.
- Examples of pitfalls:
  - Passing raw bytes (e.g., b"1.0") directly to the comparator will typically raise TypeError; decode to "1.0" first.
  - Supplying negative tolerances will likely cause __call__ to raise ValueError at comparison time via math.isclose.
  - Large tolerances (> 1) trigger a constructor warning but are allowed.

## Example (usage pattern described in prose):
- Correct usage pattern:
  - Decode raw output to strings before comparing:
    - actual_text = actual_bytes.decode('utf-8')
    - expected_text = expected_bytes.decode('utf-8')
    - comparator = FloatingPointNumberComparator(rel_tol=1e-9, abs_tol=1e-12)
    - result = comparator(actual_text, expected_text)  # returns bool
- Numeric comparison example:
  - comparator("3.1415926535", "3.1415926536") -> True if difference within tolerances.
- Non-numeric fallback example:
  - comparator("hello\n", "hello\n") -> True (exact equality).
  - comparator("1.0", "one") -> False (one is non-numeric; fallback to exact equality).

Summary guidance:
- Instantiate with keyword-only float tolerances (non-negative).
- Pass str or numeric types (not raw bytes) to avoid TypeError.
- Expect math.isclose semantics for numeric comparisons and strict equality otherwise.

### `onlinejudge_command.output_comparators.FloatingPointNumberComparator.__init__` · *method*

## Summary:
Initializes the comparator by storing the provided relative and absolute tolerances on the instance and emitting a warning if either tolerance is unusually large.

## Description:
This constructor is called when a FloatingPointNumberComparator instance is created (e.g., in test harness or judge setup code) and runs during the comparator's creation phase. Typical callers create the comparator with keyword arguments, for example:
- FloatingPointNumberComparator(rel_tol=1e-9, abs_tol=1e-12)

This logic is isolated in __init__ to:
- Centralize validation/notification about tolerance values at object construction time.
- Ensure the instance holds immutable configuration (rel_tol and abs_tol) that subsequent comparison calls (__call__) will read.

## Args:
    rel_tol (float):
        Relative tolerance to be used for numeric comparisons (forwarded to math.isclose at comparison time).
        - Required: must be provided as a keyword argument.
        - Expected type: float (or numeric type convertible to float).
        - Allowed range: intended to be non-negative. The constructor does not enforce non-negativity; negative values may cause math.isclose to raise ValueError later during comparisons.
        - Special behavior: if rel_tol is not a numeric type comparable with the literal 1, a TypeError may occur when the constructor evaluates max(rel_tol, abs_tol) > 1.

    abs_tol (float):
        Absolute tolerance to be used for numeric comparisons (forwarded to math.isclose at comparison time).
        - Required: must be provided as a keyword argument.
        - Expected type: float (or numeric type convertible to float).
        - Allowed range: intended to be non-negative. The constructor does not enforce non-negativity; negative values may cause math.isclose to raise ValueError later during comparisons.
        - Special behavior: if abs_tol is not a numeric type comparable with the literal 1, a TypeError may occur when the constructor evaluates max(rel_tol, abs_tol) > 1.

## Returns:
    None

## Raises:
    TypeError:
        - If evaluating max(rel_tol, abs_tol) or the subsequent comparison to the literal 1 attempts an invalid comparison between the provided tolerance values and integers (for example, passing objects that do not support ordering with int), Python will raise a TypeError during construction.
        - This is not explicitly raised by the constructor code, but is a direct consequence of executing max(rel_tol, abs_tol) > 1 with incompatible types.

    Any exception raised by the evaluation of rel_tol or abs_tol before calling __init__ (e.g., from user code) will originate from the caller and is not generated by this constructor.

## State Changes:
    Attributes READ:
        - None (the constructor does not read any pre-existing self attributes).

    Attributes WRITTEN:
        - self.rel_tol: set to the provided rel_tol argument (stored exactly as given).
        - self.abs_tol: set to the provided abs_tol argument (stored exactly as given).

## Constraints:
    Preconditions:
        - Callers must supply rel_tol and abs_tol as keyword-only arguments.
        - For correct behavior of later comparisons, tolerances should be numeric and preferably non-negative floats. The constructor does not validate non-negativity.
    Postconditions:
        - After __init__ returns, the instance has attributes rel_tol and abs_tol equal to the provided arguments.
        - If max(rel_tol, abs_tol) > 1 evaluated to True, a warning has been emitted via the module logger; no exception is raised and construction completes normally (assuming no TypeError occurred during the comparison).

## Side Effects:
    - Emits a logging warning through the module logger when either provided tolerance is greater than 1:
        logger.warning('the tolerance is too large: relative = %s, absolute = %s', rel_tol, abs_tol)
    - No I/O, network calls, or mutations of objects outside self are performed by this constructor.

### `onlinejudge_command.output_comparators.FloatingPointNumberComparator.__call__` · *method*

## Summary:
Compare two byte sequences by parsing them as floating-point numbers when both parse successfully; return math.isclose on the parsed floats using the instance tolerances, otherwise fall back to exact byte-for-byte equality. The call does not modify the comparator's state.

## Description:
This callable implements the comparison policy for floating-point-aware output comparison used during the output-verification stage of a judging or test-run pipeline. Typical callers are components that implement an OutputComparator interface and invoke comparator(actual, expected) for each (actual, expected) pair produced by running a submission or test case.

Why this is a separate method:
- The parsing-and-tolerance logic is reused for many comparisons and benefits from being centralized so tolerances (rel_tol, abs_tol) are provided once on the comparator instance.
- Keeping numeric comparison separate from other comparators (e.g., exact string comparator) makes testing and substitution of comparator strategies straightforward.

Behavior summary:
1. Attempt to convert actual and expected (bytes) to floats using float(actual) and float(expected). Only ValueError raised by float(...) is caught by this method; other exceptions from float(...) (e.g., TypeError when passing unsupported types) will propagate.
2. If both conversions succeed, return math.isclose(x, y, rel_tol=self.rel_tol, abs_tol=self.abs_tol).
   - If either tolerance attribute is negative, math.isclose will raise ValueError; this exception is not caught here and will propagate to the caller.
   - Note: comparisons involving NaN always yield False (math.isclose(float('nan'), float('nan')) is False). Comparisons of infinities behave per IEEE rules (e.g., both +inf compare equal).
3. If either conversion fails (ValueError), do not attempt numeric comparison; instead, return exact byte equality (actual == expected).

Examples (illustrative, not executable code blocks):
- Both numeric and within tolerance: actual=b"1.0000", expected=b"1.0" => parses to floats; returns True if isclose per tolerances.
- Both numeric but outside tolerance: actual=b"1.1", expected=b"1.0" => parses to floats; returns False if not close.
- Non-numeric but identical bytes: actual=b"hello\n", expected=b"hello\n" => float() raises ValueError for both; returns True because bytes are equal.
- One numeric, one non-numeric: actual=b"1.0", expected=b"1" (both numeric) — numeric path used; but actual=b"1.0", expected=b"one" => fallback to exact bytes, returns False.
- NaN: actual=b"nan", expected=b"nan" => both parse, but isclose returns False.

## Args:
    actual (bytes): Observed output bytes. Must be of type bytes per the method signature; float(actual) accepts bytes representing a Python float literal (optionally with surrounding whitespace). Passing other types may raise TypeError.
    expected (bytes): Expected output bytes. Same rules as actual.

## Returns:
    bool:
        - True if both values parse to floats and math.isclose(x, y, rel_tol=self.rel_tol, abs_tol=self.abs_tol) is True.
        - True if at least one value fails to parse as float (ValueError) and raw bytes are exactly equal (actual == expected).
        - False otherwise.

Edge cases and notes:
    - NaN values: math.isclose never treats NaNs as close; comparisons involving NaN return False.
    - Infinities: +inf equals +inf under math.isclose; +inf vs -inf returns False.
    - String/format differences that still parse to the same float (e.g., b"1.0" vs b"1.00") are handled by the numeric path.
    - Whitespace differences: if both parse as floats (e.g., b" 1.0\n"), parsing succeeds; but if one fails to parse due to invalid bytes, exact equality requires byte-for-byte match including whitespace.

## Raises:
    ValueError:
        - From float(...) during parsing only when float(...) raises ValueError; these are caught by the method and cause fallback to byte-equality, so they do not propagate.
        - From math.isclose(...) if self.rel_tol < 0 or self.abs_tol < 0; this is not caught and will propagate to the caller when both operands parse to floats.
    TypeError:
        - May be raised by float(...) or by equality comparison if callers pass objects that violate the expected types (non-bytes). The method signature expects bytes; passing other types can cause TypeError and will propagate.

## State Changes:
    Attributes READ:
        - self.rel_tol
        - self.abs_tol
    Attributes WRITTEN:
        - None. The method does not mutate any attributes on self.

## Constraints:
    Preconditions:
        - The instance must have numeric attributes self.rel_tol and self.abs_tol (set by __init__).
        - Prefer non-negative tolerances to avoid math.isclose raising ValueError.
        - Callers should pass bytes for actual and expected, per the annotated signature.
    Postconditions:
        - The comparator instance remains unchanged.
        - The returned boolean correctly reflects numeric closeness when both values are numeric, or exact byte equality otherwise.

## Side Effects:
    - No I/O, logging, or external service calls occur.
    - No mutation of external objects or global state is performed.

## `onlinejudge_command.output_comparators.SplitComparator` · *class*

## Summary:
SplitComparator is an OutputComparator that compares two byte sequences token-by-token: it splits both byte sequences on whitespace into words and uses an inner word_comparator to compare each corresponding word. It returns True only when both sequences contain the same number of words and every corresponding word pair matches according to the inner comparator.

## Description:
Instantiate SplitComparator when you want comparison semantics that operate at the token/word level rather than on the entire byte sequence. Typical scenarios:
- Comparing program outputs where tokens (numbers, identifiers, words) should be compared individually while treating any run of whitespace as a separator.
- Composing a tolerant per-word comparator (for example, a numeric-tolerant comparator) so that each token is compared with specialized rules.

Motivation and responsibility boundary:
- SplitComparator delegates the actual comparison of individual tokens to the provided word_comparator and only enforces tokenization and pairing semantics: equal token count and per-token invocation of the inner comparator.
- It does not perform decoding, normalization, or numeric tolerant comparison itself; those responsibilities belong to the word_comparator passed into it.

Known callers/factories:
- Any test harness or comparison pipeline that implements OutputComparator-style objects can instantiate SplitComparator to achieve whitespace-insensitive tokenized comparisons.
- There are no internal runtime checks enforcing word_comparator's type beyond runtime callability; callers are expected to supply an OutputComparator-compatible object.

## State:
- word_comparator (OutputComparator)
    - Type: OutputComparator (callable with signature (actual: bytes, expected: bytes) -> bool)
    - Valid values: any object that is callable and implements the same callable contract as OutputComparator (accepts two bytes arguments and returns a bool).
    - Invariants:
        - word_comparator must be callable.
        - word_comparator must accept two positional bytes arguments and return a boolean result when called with token bytes returned by splitting.
- No other instance attributes are defined.

## Lifecycle:
- Creation:
    - Required argument:
        - word_comparator (OutputComparator): a comparator used to compare individual word tokens. No default.
    - Example of construction pattern: provide an instance of a concrete OutputComparator (for example, an ExactComparator or NumericToleranceComparator) as the word_comparator.
    - The constructor does not validate the inner comparator beyond assignment; invalid or non-callable objects will cause failures later when __call__ is invoked.
- Usage:
    - Primary operation: call the instance as a callable: comparator(actual: bytes, expected: bytes) -> bool.
    - Typical sequence:
        1. Instantiate with a word_comparator.
        2. Invoke comparator multiple times as needed — the object is stateless beyond storing the inner comparator.
    - Behavior details during usage:
        - Tokenization: both actual and expected are tokenized with bytes.split() (no separator argument). This splits on runs of ASCII whitespace bytes and discards leading/trailing whitespace. The result of split() is a sequence of bytes tokens.
        - Early-exit checks:
            - If the number of tokens differs, __call__ immediately returns False.
            - Otherwise, for each corresponding token pair (in order), __call__ invokes word_comparator(token_actual, token_expected). If any invocation returns False, __call__ immediately returns False. Only if all token comparisons return True does __call__ return True.
- Destruction / cleanup:
    - There are no resources to release. The class does not implement context-manager protocols or close methods. If word_comparator holds resources requiring cleanup, that responsibility belongs to the provider of word_comparator.

## Method Map:
graph LR
    A[Instantiate SplitComparator(word_comparator)] --> B[__call__(actual: bytes, expected: bytes)]
    B --> C[actual.split() -> actual_words]
    B --> D[expected.split() -> expected_words]
    C --> E{len(actual_words) == len(expected_words)?}
    E -- No --> F[return False]
    E -- Yes --> G[for each (x,y) in zip(actual_words, expected_words):]
    G --> H[word_comparator(x, y)]
    H --> I{word_comparator returned True?}
    I -- No --> F
    I -- Yes --> G
    G --> J[after loop -> return True]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style E fill:#ffd,stroke:#333,stroke-width:1px
    style H fill:#cfc,stroke:#333,stroke-width:1px

## Raises:
- __init__:
    - The constructor itself does not raise explicit exceptions. It assigns the provided word_comparator to an instance attribute without validation.
- __call__:
    - Caller preconditions:
        - actual and expected should be bytes (or bytes-like objects that support .split() with the same semantics). The method signature expects bytes; passing other types may raise exceptions:
            - AttributeError if the provided object does not implement split().
            - TypeError or other exceptions may arise if downstream word_comparator expects specific formats (e.g., decodable text) and cannot handle the provided token bytes.
    - If word_comparator is not callable, attempting to invoke it will raise TypeError.
    - Any exception raised by the inner word_comparator during token comparison (for example, UnicodeDecodeError, ValueError, or custom exceptions) will propagate through SplitComparator.__call__ unchanged.

## Example:
- Construction:
    - Provide a concrete word comparator that implements OutputComparator (for instance, a comparator that compares bytes exactly or one that decodes tokens and compares numbers with tolerance).
    - Example instantiation pattern: instantiate SplitComparator with that concrete comparator as word_comparator.
- Typical invocation:
    - Call comparator(actual_bytes, expected_bytes).
    - The call returns True only when both sequences tokenize to the same number of tokens and each corresponding token pair returns True when passed to the inner word comparator.
- Edge cases demonstrated conceptually:
    - If actual = b" 1\t2  3\n" and expected = b"1 2 3", both split() to three tokens [b"1", b"2", b"3"]; the inner comparator determines the final result.
    - If actual = b"1 2" and expected = b"1 2 3", __call__ returns False immediately due to differing token counts.

### `onlinejudge_command.output_comparators.SplitComparator.__init__` · *method*

## Summary:
Stores the provided word-level comparator on the instance so SplitComparator can use it for per-word comparisons.

## Description:
Called when a SplitComparator instance is constructed. The constructor performs a single action: it assigns the provided word_comparator to an instance attribute. This assignment is relied upon by SplitComparator.__call__ to compare corresponding whitespace-separated words of actual and expected byte sequences.

This logic is in the constructor to accept (inject) any concrete OutputComparator implementation for word-level comparison rather than hard-coding a specific comparator inside the SplitComparator class.

## Args:
    word_comparator (OutputComparator):
        Required. A concrete comparator object that conforms to the OutputComparator interface
        (i.e., a callable that accepts two bytes arguments and returns a bool). No validation
        or type checking is performed by this constructor.

## Returns:
    None

## Raises:
    None (the constructor does not raise). 
    Note: If a non-callable or incorrectly-behaved object is supplied, errors (for example,
    TypeError) may occur later when SplitComparator.__call__ attempts to invoke self.word_comparator.

## State Changes:
    Attributes READ:
        - None. The constructor does not read any pre-existing instance attributes.

    Attributes WRITTEN:
        - self.word_comparator (OutputComparator): set to the provided word_comparator argument.

## Constraints:
    Preconditions:
        - No preconditions enforced by the constructor. The caller should provide an object
          intended to be usable as an OutputComparator if comparisons are to succeed at runtime.

    Postconditions:
        - After return, self.word_comparator is defined on the instance and references the
          exact object passed as word_comparator.

## Side Effects:
    - Mutates the newly-constructed SplitComparator instance by assigning an attribute.
    - No I/O, no external service interaction, and no mutation of objects outside of self
      are performed by this method.

### `onlinejudge_command.output_comparators.SplitComparator.__call__` · *method*

## Summary:
Compare two byte-sequence outputs by splitting each on whitespace into words and returning True only if they have the same number of words and every corresponding word pair is accepted by the configured word-level comparator. This does not mutate the comparator object.

## Description:
This callable method is intended to be used during the output-comparison stage of a judging pipeline where whole outputs are compared at word granularity. Typical usage is that a higher-level comparator or the judge harness invokes this comparator to decide whether two outputs are equivalent under a given word-level policy.

This behavior is factored into its own method so the comparator instance can be used polymorphically (callable objects), to encapsulate the split-and-compare logic separately from word-level comparison policy, and to allow composing different word-level comparators without duplicating splitting logic.

Known callers and context:
- Any code that holds or composes OutputComparator instances and expects a callable that compares two outputs (e.g., a composite comparator or the result comparison step of a judge). (The method itself does not discover or instantiate callers.)

Why separate:
- Keeps splitting/iteration logic centralized so different word-level comparator strategies can be injected via self.word_comparator.
- Allows this comparator to be passed around and invoked like any other comparator object.

## Args:
    actual (bytes): Raw output produced (bytes). Must be a bytes object. The split semantics follow Python's bytes.split() with no separator: splits on runs of ASCII whitespace bytes, and strips leading/trailing whitespace.
    expected (bytes): Expected raw output (bytes). Same constraints and semantics as actual.

## Returns:
    bool: True if and only if:
        - actual.split() and expected.split() produce the same number of words, and
        - for every index i, self.word_comparator(actual_words[i], expected_words[i]) returns a truthy value that is interpreted as acceptance.
    Returns False otherwise.
    Edge cases:
        - Both empty or whitespace-only byte strings (e.g., b'' or b'   \\n\\t') produce zero words; this method will return True if both produce zero words.
        - Word-order matters: the comparator compares corresponding positions; permutations of words will not be considered equal unless the word_comparator accepts reordered pairs.

## Raises:
    No exceptions are explicitly raised by this method. However, the following may propagate:
        - TypeError or AttributeError if self.word_comparator is not callable.
        - Any exception raised by self.word_comparator when it is invoked for a word pair.
    The method contains no try/except and therefore will not swallow exceptions from the injected comparator.

## State Changes:
    Attributes READ:
        - self.word_comparator
    Attributes WRITTEN:
        - None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - self.word_comparator must have been initialized (typically in __init__) and should be a callable that accepts two bytes arguments and returns a boolean-like value.
        - actual and expected must be bytes (passing other types will likely raise at runtime).
    Postconditions:
        - The comparator object (self) remains unchanged.
        - The return value is a boolean indicating word-by-word acceptance as described above.

## Side Effects:
    - No I/O or external service calls are performed by this method itself.
    - Calling self.word_comparator may have side effects (if that comparator performs I/O or mutates external state); any such side effects will occur and are not suppressed by this method.

## `onlinejudge_command.output_comparators.SplitLinesComparator` · *class*

## Summary:
Compares two byte-sequence outputs line-by-line by splitting on newline bytes and delegating each line comparison to a provided per-line OutputComparator.

## Description:
SplitLinesComparator implements the OutputComparator callable interface (i.e., instances are invoked as comparator(actual: bytes, expected: bytes) -> bool). It is suitable for use wherever an OutputComparator is required; for example, it can be composed into the result-checking pipeline of a judge or test harness that needs per-line comparison policies.

This class enforces a clear responsibility boundary: it handles splitting the raw byte outputs into lines and aligning them (including normalizing trailing newlines), and it delegates the actual equality/tolerance logic for each line to the injected line_comparator. It does not perform any decoding or normalization beyond stripping trailing newline bytes and splitting on b'\n'.

## State:
- line_comparator: OutputComparator
  - Type: any object implementing the OutputComparator callable interface (i.e., callable with signature (actual: bytes, expected: bytes) -> bool). The constructor does not enforce the type at runtime, but correct usage requires a concrete OutputComparator instance.
  - Invariant: line_comparator is stored and will not be modified by this class; it must accept two bytes objects and return a bool.
- No other instance attributes are used.

Notes about data representations:
- Inputs to __call__ are raw bytes. The comparator does not decode text; all operations are byte-oriented.
- Splitting behavior:
  - Trailing newline bytes are removed using rstrip(b'\n') before splitting. Therefore inputs that differ only by trailing newline characters can be considered equivalent.
  - Splitting uses split(b'\n'), so internal empty lines are preserved as b'' entries.
  - Example: b'foo\nbar\n' -> rstrip -> b'foo\nbar' -> split -> [b'foo', b'bar'].

## Lifecycle:
- Creation:
  - Instantiate with a single required argument: line_comparator, an OutputComparator instance (or any callable matching the interface).
  - Example: comparator = SplitLinesComparator(line_comparator)
- Usage:
  - Invoke as a callable: result = comparator(actual_bytes, expected_bytes)
  - Typical sequence: construct once, call __call__ zero or more times with different actual/expected pairs. No required ordering beyond instantiation then invocation.
- Destruction:
  - No special cleanup required. This class does not manage external resources and does not implement context-manager or close semantics.

## Method Map:
graph LR
    A[Instantiate SplitLinesComparator(line_comparator)] --> B[__call__(actual: bytes, expected: bytes)]
    B --> C{Strip trailing b'\\n' and split on b'\\n' -> actual_lines, expected_lines}
    C --> D{If lengths differ -> return False}
    C --> E[For each pair (x,y) in zip(actual_lines, expected_lines)]
    E --> F[line_comparator(x, y) -> bool]
    F --> G{If any False -> return False}
    G --> H[All True -> return True]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style C fill:#ffb,stroke:#333,stroke-width:1px
    style D fill:#f66,stroke:#333,stroke-width:1px
    style H fill:#bfb,stroke:#333,stroke-width:1px

## Raises:
- TypeError or AttributeError if actual or expected are not bytes:
  - The implementation calls rstrip(b'\n') and split(b'\n') on the provided objects. If they are not bytes (for example, str or None), Python will raise an AttributeError or a TypeError when these methods are invoked. This class does not perform explicit type checking.
- Exceptions raised by the injected line_comparator:
  - Any exception raised by line_comparator when comparing two lines (e.g., UnicodeDecodeError if that comparator decodes bytes, ValueError for malformed numeric parsing, etc.) will propagate to the caller.
- No exceptions are raised for mismatches; mismatches are signaled by returning False.

## Raises in __init__:
- __init__ performs no validation; it does not raise exceptions in normal operation. If a non-callable or non-conforming object is passed, errors (TypeError, AttributeError) will surface later when __call__ delegates to line_comparator.

## Example:
- Constructing with a hypothetical per-line comparator (must implement OutputComparator interface):
    1. line_cmp = SomeLineComparator()  # SomeLineComparator: OutputComparator
    2. cmp = SplitLinesComparator(line_cmp)
    3. actual = b'1 2 3\n4 5 6\n'
    4. expected = b'1 2 3\n4 5 6\n'
    5. result = cmp(actual, expected)  # True if line_cmp returns True on both lines
- Behavior notes illustrated:
    - Different trailing newline styles:
        - cmp(b'foo\n', b'foo') -> True if line_cmp(b'foo', b'foo') -> True (trailing newline is normalized away)
    - Empty outputs:
        - cmp(b'', b'') -> delegates comparison for a single empty line: line_cmp(b'', b'')
    - Different number of lines:
        - cmp(b'a\nb\n', b'a\n') -> False (different line counts)

## Implementation constraints / edge cases:
- The component expects byte-level line boundaries only at b'\\n' and does not treat b'\\r\\n' specially; callers should ensure inputs use the expected newline convention or provide a line_comparator that tolerates CR bytes.
- Because trailing newline bytes are stripped (all trailing b'\\n' bytes), multiple trailing newlines are ignored for the purpose of counting lines.
- The equality semantics depend entirely on the supplied line_comparator; SplitLinesComparator only enforces per-line alignment and length equality prior to delegation.

### `onlinejudge_command.output_comparators.SplitLinesComparator.__init__` · *method*

## Summary:
Stores the provided per-line OutputComparator on the instance, establishing the comparator used when comparing outputs line-by-line.

## Description:
This constructor initializes a SplitLinesComparator by recording the injected line_comparator dependency. Known callers are the creation sites in result-checking or judge/test-harness pipelines that assemble comparators before invoking them on program outputs; typical usage is at the "construction" stage of the comparator lifecycle (create comparator once, then call it multiple times to compare actual/expected outputs). This logic is isolated in its own method to support dependency injection (allowing different per-line comparison policies), clearer separation of responsibilities, and easier unit testing of comparison policies.

## Args:
    line_comparator (OutputComparator):
        - A callable object implementing the OutputComparator interface: it must accept two bytes arguments (actual: bytes, expected: bytes) and return a bool indicating whether the two lines match.
        - No runtime type enforcement is performed by this constructor; passing a non-conforming object will not raise here but will likely cause errors later when the comparator is invoked.

## Returns:
    None

## Raises:
    - None raised by this method itself during normal operation.
    - Note: If a non-callable or otherwise invalid object is passed, this constructor does not validate it; subsequent invocation of the comparator (i.e., calling the instance) may raise TypeError, AttributeError, or whatever exceptions the invalid object produces.

## State Changes:
    Attributes READ:
        - None (this constructor does not read existing instance attributes)
    Attributes WRITTEN:
        - self.line_comparator: set to the provided line_comparator argument

## Constraints:
    Preconditions:
        - The caller should provide an object conforming to the OutputComparator contract:
            * Callable with signature (actual: bytes, expected: bytes) -> bool.
            * Should not mutate the provided byte arguments.
        - The object may be any callable or instance implementing the interface; it may be a function, a callable class instance, or a subclass of OutputComparator.
    Postconditions:
        - After return, self.line_comparator is exactly the object passed as line_comparator (no copy or wrapping).
        - No validation guarantees are made about the callable beyond being stored; any interface violations will manifest later when the comparator is used.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside of self: only self.line_comparator is assigned.
    - No logging or other global state changes.

### `onlinejudge_command.output_comparators.SplitLinesComparator.__call__` · *method*

## Summary:
Compare two byte-string outputs line-by-line (after removing trailing newlines) and return True iff they have the same number of lines and every corresponding line pair is considered equal by the instance's line comparator. This method does not modify the object's state.

## Description:
This method implements the callable behavior of a line-oriented output comparator: it splits both actual and expected byte outputs into lines, normalizes trailing newline characters, and delegates the per-line equality check to self.line_comparator.

Known callers / invocation context:
- The file does not declare explicit callers. The method is intended to be invoked by code that treats comparator objects as callables to decide whether two outputs match (for example, a judging or testing pipeline that compares program output against expected output).

Why this is a separate method:
- The splitting and per-line delegation is a reusable, clearly scoped operation that separates line-level comparison logic (self.line_comparator) from multi-line orchestration. Keeping this logic here avoids duplicating line-splitting and length checks wherever a comparator object is used.

## Args:
    actual (bytes): The raw bytes produced by the program under test. Must be a bytes object. The method treats b'\n' as the line separator.
    expected (bytes): The expected output as raw bytes. Must be a bytes object.

## Returns:
    bool: True if and only if:
        - After removing trailing newline bytes (b'\n') from both inputs and splitting on b'\n', actual and expected produce the same number of lines, and
        - For every pair of corresponding lines (actual_line, expected_line), self.line_comparator(actual_line, expected_line) returns a truthy value.
      Returns False as soon as a line count mismatch or any line_comparator call indicates inequality.

## Raises:
    Any exception raised by self.line_comparator is propagated (not caught) by this method.
    Type errors or attribute errors may occur if actual or expected are not bytes (e.g., if they lack rstrip or split methods). The method itself does not raise custom exceptions.

## Behavior details and edge cases:
    - Trailing newlines: Both actual and expected are passed through rstrip(b'\n') which removes all trailing newline bytes before splitting. Therefore, differing numbers of trailing newline characters do not by themselves cause a mismatch.
    - Empty input: If actual or expected is b'' (empty bytes), rstrip(b'\n') yields b'' and split(b'\n') yields [b''] (a single empty-line entry). Comparing b'' vs b'' therefore produces a single-line comparison using the line comparator.
    - Internal empty lines: Consecutive newline bytes (e.g., b'a\n\nb') produce empty-line entries when split (e.g., [b'a', b'', b'b']), and those empty lines are compared normally.
    - Line count check: The method first compares the lengths of the produced line lists; if they differ it returns False immediately. Because of this explicit length check, using zip to iterate is safe (it will always iterate over all paired lines).
    - Short-circuiting: The method returns False on the first failing line_comparator result; it returns True only after all pairs pass.

## State Changes:
    Attributes READ:
        - self.line_comparator: called for each corresponding line pair. The method expects this attribute to be a callable that accepts two bytes arguments and returns a truthy/falsey value indicating whether the lines match.
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - actual and expected should be bytes objects. Passing other types may raise exceptions.
        - self.line_comparator must be defined and callable; it must accept (bytes, bytes) and return a boolean-like value.
    Postconditions:
        - No mutation of self is performed.
        - The return value accurately reflects the line-by-line comparison semantics described above.

## Side Effects:
    - The method itself performs no I/O and does not call external services.
    - Side effects may occur if self.line_comparator has side effects; those are neither created nor suppressed by this method.
    - Exceptions from the line comparator are propagated to the caller.

## `onlinejudge_command.output_comparators.CRLFInsensitiveComparator` · *class*

## Summary:
A wrapper OutputComparator that normalizes Windows CRLF line endings (b'\r\n') to Unix LF (b'\n') in both actual and expected byte sequences before delegating the comparison to an inner comparator.

## Description:
Instantiate this class when you want to ignore differences between CRLF and LF line endings when comparing program output to expected output. This comparator performs a simple, byte-level normalization: it replaces every occurrence of the byte sequence b'\r\n' with b'\n' in both the actual and expected inputs, then forwards the normalized bytes to a contained OutputComparator (the file_comparator) for the real comparison.

Typical scenarios:
- Comparing outputs produced on Windows (CRLF) with expected outputs written for Unix (LF).
- Composing comparator behaviors: use this wrapper around any comparator that implements the OutputComparator interface to add CRLF-insensitivity without changing the comparator's core logic.

Known callers/factories:
- Any code that constructs comparator pipelines to compare program outputs across platforms.
- Tests or harnesses that want to reuse an existing comparator but relax line-ending differences.

Motivation and responsibility boundary:
- Responsibility: normalize CRLF -> LF and delegate comparison.
- Boundary: it does not alter any other aspect of the comparator's behavior (it does not trim whitespace, decode bytes to text, ignore trailing newlines, nor perform numeric tolerance). Those responsibilities remain with the wrapped file_comparator.

## State:
- file_comparator (OutputComparator)
    - Type: OutputComparator (callable signature: (bytes, bytes) -> bool)
    - Valid values: any callable object that accepts two bytes arguments and returns a bool. The implementation does not enforce type checks at construction time.
    - Invariant: file_comparator must be callable at the time __call__ is invoked; otherwise a TypeError (object not callable) will be raised by Python when attempting to call it.
- No other instance attributes are stored.

Class invariants:
- After instantiation, self.file_comparator refers to the comparator used for the actual comparison and must remain callable for the wrapper to operate correctly.
- The wrapper does not mutate provided byte arguments; it creates and passes normalized copies to file_comparator.

## Lifecycle:
Creation:
- Instantiate with one required positional argument:
    - file_comparator: an OutputComparator instance (or any callable) that implements comparison logic for two bytes objects.
- Example instantiation:
    - comparator = CRLFInsensitiveComparator(file_comparator)

Usage:
- Call the instance like a function: result = comparator(actual_bytes, expected_bytes)
- Ordering/sequence:
    1. Construct the wrapper with a concrete comparator.
    2. Invoke the wrapper any number of times with actual and expected bytes.
    3. The wrapper normalizes line endings and forwards to file_comparator each invocation.
- Concurrency: the wrapper itself is stateless beyond the reference to file_comparator; thread-safety depends on the thread-safety of the wrapped comparator.

Destruction:
- No special cleanup is required. The class does not implement context-manager or close/cleanup methods. If the wrapped comparator requires cleanup, that responsibility remains with the wrapped comparator.

## Method Map:
graph LR
    A[CRLFInsensitiveComparator.__init__(file_comparator)] --> B[instance.file_comparator set]
    B --> C[__call__(actual: bytes, expected: bytes)]
    C --> D[actual_norm = actual.replace(b'\r\n', b'\n')]
    C --> E[expected_norm = expected.replace(b'\r\n', b'\n')]
    C --> F[file_comparator(actual_norm, expected_norm) -> bool]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style C fill:#bbf,stroke:#333,stroke-width:1px
    style F fill:#bfb,stroke:#333,stroke-width:1px

## Raises:
- __init__:
    - The constructor does not perform type checking and therefore does not raise on incorrect file_comparator types itself.
- __call__:
    - TypeError: if self.file_comparator is not callable, Python will raise TypeError when attempting to call it.
    - Any exception raised by file_comparator is propagated unchanged (for example, ValueError, UnicodeDecodeError, or custom exceptions from the wrapped comparator).
    - AttributeError or TypeError may occur if actual or expected are not bytes and thus do not support bytes.replace; callers must pass bytes-like objects (the intended contract is bytes).

## Example:
- Create a CRLF-insensitive comparator around a simple byte-wise equality comparator and use it:
    comparator = CRLFInsensitiveComparator(lambda actual, expected: actual == expected)
    result1 = comparator(b"line1\r\nline2\r\n", b"line1\nline2\n")  # True (CRLF normalized to LF before comparing)
    result2 = comparator(b"line\n", b"other\n")                     # False

Notes and edge cases:
- Only the byte sequence b'\r\n' is normalized; lone b'\r' bytes (not followed by b'\n') are left unchanged.
- No other normalization is performed: differences such as extra spaces, differing numeric formats, or different encodings are not handled by this class.
- The wrapper operates purely at the byte level and never decodes bytes to text; it is therefore safe to use with arbitrary byte content as long as the wrapped comparator can handle those bytes.

### `onlinejudge_command.output_comparators.CRLFInsensitiveComparator.__init__` · *method*

## Summary:
Initializes the comparator by storing a delegated OutputComparator that will be invoked after CRLF normalization.

## Description:
This constructor accepts an existing OutputComparator instance and stores it on the new CRLF-insensitive comparator object so subsequent comparisons delegate to that comparator after normalizing CRLF sequences to LF. Typical usage is in a comparison pipeline where you want to reuse an existing comparator implementation (for example, a strict byte comparator or a tolerant text comparator) but make it insensitive to CRLF differences first.

Known callers and context:
- There are no explicit callers inside this module; client code or factories that build comparator stacks instantiate this class when they need CRLF-insensitive behavior.
- The constructor is called during comparator composition/initialization, before any comparisons (__call__) are invoked.

Rationale for separate method:
- The constructor is kept small and focused on dependency injection: it records the comparator to delegate to. Separating initialization from comparison logic keeps responsibilities clear and allows swapping or decorating different comparator implementations without duplicating normalization logic.

## Args:
    file_comparator (OutputComparator): Required. An instance of OutputComparator (or a compatible callable object) that implements the comparison policy. The object is expected to be callable as file_comparator(actual: bytes, expected: bytes) -> bool.

## Returns:
    None: Constructors in Python return None; no value is returned.

## Raises:
    None explicitly. The constructor does not validate the argument. Misuse (for example passing None or an object that lacks a callable __call__(actual, expected)) will not raise here but may cause AttributeError or TypeError later when __call__ is invoked.

## State Changes:
    Attributes READ:
        - (none) This initializer does not read any existing instance attributes.
    Attributes WRITTEN:
        - self.file_comparator: set to the provided file_comparator argument.

## Constraints:
    Preconditions:
        - The caller should provide a file_comparator that adheres to the OutputComparator contract: callable with two bytes arguments and returns bool. This is a behavioral precondition (not enforced by the constructor).
    Postconditions:
        - After return, self.file_comparator references the passed-in object exactly (no copying or validation performed).

## Side Effects:
    - No I/O, no external service calls.
    - No mutations to objects outside of assigning the file_comparator reference to self.file_comparator.

### `onlinejudge_command.output_comparators.CRLFInsensitiveComparator.__call__` · *method*

## Summary:
Delegates a bytes-level comparison to the wrapped comparator after normalizing CRLF pairs (b'\r\n') to LF (b'\n') in both actual and expected inputs, returning the wrapped comparator's boolean result.

## Description:
This method is invoked when an OutputComparator-like callable is used to compare two byte sequences representing program output and expected output. It exists to centralize and isolate CRLF-to-LF normalization so that downstream file-level comparison logic does not need to handle platform-specific CRLF differences.

Known callers and context:
- Any code that receives or stores an instance of this comparator and calls it as a callable with two bytes arguments (actual, expected). The class constructor stores the delegate comparator on self.file_comparator, and this method is the callable entrypoint used in comparison pipelines.
- Typical lifecycle stage: the comparator is called at the time of comparing the produced output of a program (actual) against the stored expected output (expected). This method performs normalization immediately before delegating the comparison.

Why this logic is a separate method:
- Normalization is a distinct concern from file/content comparison. Keeping CRLF insensitivity in this callable allows composition: different file comparison strategies can be wrapped by CRLFInsensitiveComparator without modifying them.

## Args:
    actual (bytes): The observed output bytes to compare. Must be a bytes object.
    expected (bytes): The expected output bytes to compare against. Must be a bytes object.

## Returns:
    bool: The boolean result returned by self.file_comparator after being called with normalized bytes.
    - True indicates the wrapped comparator considers the normalized actual and expected equal according to its logic.
    - False indicates the wrapped comparator considers them not equal.
    - If the wrapped comparator raises an exception, that exception propagates (see Raises).

## Raises:
    Any exception raised by self.file_comparator when it is invoked with the normalized byte arguments.
    - This method does not catch or translate exceptions from the delegate; they propagate to the caller.

## State Changes:
    Attributes READ:
        - self.file_comparator: read to obtain the delegate callable used for the actual comparison.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.file_comparator must be a callable that accepts two bytes arguments and returns a bool.
        - actual and expected must be of type bytes. Passing non-bytes values will likely cause attribute/type errors (e.g., if they do not implement replace(byte_sub, byte_sub)).
    Postconditions:
        - This method returns exactly what self.file_comparator returns when given actual.replace(b'\r\n', b'\n') and expected.replace(b'\r\n', b'\n').
        - No attributes on self are modified.

## Behavior details and edge cases:
    - Normalization performed: every occurrence of the two-byte sequence b'\r\n' is replaced with b'\n' in both inputs before delegation. This is a global replacement (all CRLF pairs are converted).
    - The method does not normalize lone b'\r' characters or other newline variants; b'\r' not immediately followed by b'\n' remains unchanged.
    - The method operates at the raw bytes level — it does not decode bytes to text and thus does not depend on or change character encodings.
    - The method allocates new bytes objects as the result of replace; callers should be aware that large inputs will incur the cost of copying.
    - Any semantics about how equality is determined (e.g., trimming trailing whitespace, ignoring extra blank lines) are entirely determined by the delegate comparator; this method only normalizes CRLF pairs.

## Side Effects:
    - No I/O or external service calls.
    - No mutations to objects outside self, except that exceptions raised by the delegate may have effects outside (propagated).

## `onlinejudge_command.output_comparators.CompareMode` · *class*

## Summary:
An enumeration that defines the allowed output comparison modes as distinct, immutable symbols with associated string values.

## Description:
CompareMode enumerates the canonical comparison-mode identifiers used to represent how two outputs should be compared. The class itself only provides the symbolic constants and their string values; it does not implement comparison logic. Typical usage is to pass one of these members to other components (for example, comparators, graders, or configuration handlers) so those components can interpret the selected comparison strategy.

Motivation and responsibility boundary:
- Centralizes the set of permitted comparison-mode identifiers.
- Provides a type-safe, IDE-friendly alternative to free-form strings.
- Does not perform comparison or normalization itself; it is a descriptive token only.

## State:
This enum is immutable and has no mutable instance attributes. Each member is a singleton with a name and a string value.

Members (name -> value):
- EXACT_MATCH -> "exact-match"
- CRLF_INSENSITIVE_EXACT_MATCH -> "crlf-insensitive-exact-match"
- IGNORE_SPACES -> "ignore-spaces"
- IGNORE_SPACES_AND_NEWLINES -> "ignore-spaces-and-newlines"

For each member:
- name (str): the member identifier, e.g., EXACT_MATCH.
- value (str): the string assigned to the member (see the list above).

Class invariants:
- The set of members is fixed at definition and cannot be changed at runtime.
- Each member's .value is unique among members.

## Lifecycle:
Creation:
- Obtain a member by attribute access (for example, using the member identifier) or by value lookup using the enum's standard value-conversion mechanism (providing one of the string values defined above).
- No constructor arguments are required beyond the standard enum semantics.

Usage:
- Read-only usage: callers inspect the chosen CompareMode and branch behavior elsewhere.
- There is no required invocation order; enum members are passive descriptors.

Destruction / Cleanup:
- No cleanup is required. Enum members are regular Python objects managed by the interpreter.

## Method Map:
A simple flow describing how a CompareMode value is typically obtained and forwarded.

graph TD
    A[Source: config / CLI / code] --> B[Obtain string value]
    B --> C[Convert string to CompareMode via enum value lookup]
    A --> D[Direct attribute access to CompareMode.<MEMBER>]
    C --> E[Comparator/consumer receives CompareMode]
    D --> E
    E --> F[Comparator/consumer interprets the mode]

(Interpretation: a CompareMode is either accessed directly by attribute or reconstructed from a stored string; it is then read by a consumer component that implements the comparison behavior.)

## Raises:
- ValueError:
  - If an attempt is made to create a CompareMode from a string that does not match any member's value, the standard enum value-lookup mechanism will raise ValueError. The class itself defines no custom exceptions.

## Example (descriptive, non-code):
- A configuration contains the string "ignore-spaces". A consumer program reads this string and attempts to convert it to a CompareMode by performing a value lookup. If the string matches one of the defined member values, the corresponding CompareMode member is obtained; otherwise, a ValueError is raised and the program should handle the invalid configuration.
- Alternatively, code can directly reference CompareMode.EXACT_MATCH to indicate that an exact match behavior should be used. The obtained CompareMode is then passed to the component responsible for performing the actual comparison, which interprets the meaning of the selected mode.

## `onlinejudge_command.output_comparators.check_lines_match` · *function*

## Summary:
Compare two text strings using a selected comparison strategy by encoding them to bytes and delegating to the appropriate OutputComparator; returns True when the chosen comparator considers them matching.

## Description:
This function centralizes the logic that maps a CompareMode token to a concrete comparator pipeline, encodes the two provided str values into bytes (using the default string encoding), and invokes the comparator to perform the actual match test.

Known callers:
- No specific function names are required in this module; the function is intended to be called by higher-level comparison/grading code paths (for example, CLI commands or test harness components) that must decide whether two outputs match according to a chosen CompareMode. It acts as a convenience/adapter that hides comparator construction and encoding details from callers.

When it is called:
- Typical callers call this during result evaluation after obtaining two text outputs (actual program output and expected output) and after selecting a CompareMode (from CLI flags, configuration, or other program logic). The function is usually invoked in the line-by-line or whole-output comparison stage of an evaluation pipeline.

Why this logic is extracted:
- Responsibility separation: it keeps mode→comparator selection and byte-encoding in one place so callers do not need to remember which comparator composition corresponds to which CompareMode.
- Reuse: different call sites that need the same mapping and encoding can reuse this single function rather than reimplement comparator construction and encoding repeatedly.
- Safety: consolidates the guard for disallowed modes (raises a clear RuntimeError for IGNORE_SPACES_AND_NEWLINES) so that callers get a consistent error when they attempt an unsupported operation.

## Args:
    a (str): First string to compare (typically the actual output). Must be a Python str instance. It will be encoded to bytes using the default str.encode() behavior (UTF-8 by default).
    b (str): Second string to compare (typically the expected output). Must be a Python str instance and will be encoded like `a`.
    compare_mode (CompareMode) (keyword-only): The comparison mode selecting how the two inputs should be compared. This parameter is keyword-only (the function signature enforces passing it as a keyword). Allowed values and their effect:
        - CompareMode.EXACT_MATCH: compares encoded bytes with an ExactComparator (byte-wise equality).
        - CompareMode.CRLF_INSENSITIVE_EXACT_MATCH: normalizes CRLF (b'\r\n' -> b'\n') on both sides, then does byte-wise equality via ExactComparator.
        - CompareMode.IGNORE_SPACES: splits both byte sequences on whitespace into tokens and compares corresponding tokens using ExactComparator (token-wise exact match).
        - CompareMode.IGNORE_SPACES_AND_NEWLINES: not supported by this function (see Raises).

Interdependencies:
- a and b must be str; the comparator pipeline expects bytes, so this function encodes them before invoking the comparator.
- The chosen CompareMode determines which comparator is constructed; some modes wrap or compose other comparators.

## Returns:
    bool: True if the selected comparator determines the encoded versions of `a` and `b` match, False otherwise.

Possible return behaviors:
- True: comparator returns True under the chosen semantics (exact bytes equal, CRLF-normalized equality, or token-wise equality depending on mode).
- False: comparator returns False (mismatch according to chosen semantics).

## Raises:
    RuntimeError: If compare_mode is CompareMode.IGNORE_SPACES_AND_NEWLINES. The function explicitly disallows this mode and raises RuntimeError('CompareMode.IGNORE_SPACES_AND_NEWLINES is not allowed for this function').
    AssertionError: If compare_mode does not match any of the handled enum members in the if/elif chain (the final `else: assert False`), an AssertionError will be raised. In normal usage with a valid CompareMode value this branch should not be reached.
    UnicodeEncodeError: If either input str contains code points that cannot be encoded by the default encoding used by str.encode(), encoding a or b may raise UnicodeEncodeError. (In typical Python builds using UTF-8 this is unlikely for normal Unicode text; lone surrogate code points can trigger this.)
    Any exception raised by the constructed comparator: the function delegates comparison to the comparator instance; exceptions from the comparator (for example, TypeError if comparator receives unexpected types, or other implementation-specific exceptions) propagate unchanged.

## Constraints:
Preconditions:
- `a` and `b` must be Python str objects (not bytes). The function will call .encode() on them.
- `compare_mode` must be a valid CompareMode member. Passing arbitrary values risks an AssertionError or incorrect behavior.
- Callers expecting IGNORE_SPACES_AND_NEWLINES semantics must not call this function; instead they should use a different comparator pipeline that supports that mode.

Postconditions:
- No global state is modified.
- The function returns True/False reflecting the chosen comparator's result.
- If the function returns normally, no exceptions were raised by the mapping/encoding/comparison steps (unless the comparator itself intentionally raises for certain inputs).

## Side Effects:
- No I/O (no file, network, or stdout/stderr writes) is performed by this function.
- No mutation of global variables or external state is performed.
- The only observable effect is encoding `a` and `b` to bytes and invoking comparator callables; any side effects of the underlying comparator (if it has them) will propagate.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckMode{compare_mode}
    CheckMode --> |EXACT_MATCH| ExactComp[ExactComparator()]
    CheckMode --> |CRLF_INSENSITIVE_EXACT_MATCH| CRLFComp[CRLFInsensitiveComparator(ExactComparator())]
    CheckMode --> |IGNORE_SPACES| SplitComp[SplitComparator(ExactComparator())]
    CheckMode --> |IGNORE_SPACES_AND_NEWLINES| ErrorR[Raise RuntimeError]
    CheckMode --> |Other| AssertFail[assert False -> AssertionError]
    ExactComp --> EncodeInputs[a.encode(), b.encode()]
    CRLFComp --> EncodeInputs
    SplitComp --> EncodeInputs
    EncodeInputs --> CallComp[comparator(encoded_a, encoded_b) -> bool]
    CallComp --> Return([Return bool])
    ErrorR --> EndError([Raises RuntimeError])
    AssertFail --> EndAssert([Raises AssertionError])

## Examples:
- Exact match:
    - Caller has actual_text and expected_text (both str) and wants a byte-wise exact comparison. Call:
      result = check_lines_match(actual_text, expected_text, compare_mode=CompareMode.EXACT_MATCH)
      If result is True, the encoded byte sequences are exactly equal.

- CRLF-insensitive exact match:
    - To treat CRLF and LF as equivalent line endings:
      result = check_lines_match(actual_text, expected_text, compare_mode=CompareMode.CRLF_INSENSITIVE_EXACT_MATCH)
      This constructs a CRLFInsensitiveComparator wrapping ExactComparator and returns True when CRLF differences are normalized to LF and the normalized bytes are equal.

- Ignore spaces (token-wise exact match):
    - To compare token-by-token (splitting on whitespace) while requiring tokens to match exactly:
      result = check_lines_match(actual_text, expected_text, compare_mode=CompareMode.IGNORE_SPACES)

- Handling the unsupported mode:
    - If caller mistakenly passes CompareMode.IGNORE_SPACES_AND_NEWLINES, the function raises RuntimeError. Example handling:
      try:
          ok = check_lines_match(a, b, compare_mode=CompareMode.IGNORE_SPACES_AND_NEWLINES)
      except RuntimeError as e:
          # handle or report that this use-case is unsupported by this function
          raise

Notes:
- This function uses the default str.encode() call (UTF-8 in standard Python builds) to convert inputs to bytes. If you need a different encoding or need to avoid encoding entirely (e.g., inputs are already bytes), perform that conversion or call an appropriate comparator directly.
- For fine-grained control (for example, applying numeric tolerance per-token), construct and invoke the desired comparator objects directly instead of using this helper.

