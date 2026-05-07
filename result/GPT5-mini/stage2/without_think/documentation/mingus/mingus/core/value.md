# `value.py`

## `mingus.core.value.add` · *function*

## Summary:
Compute the reciprocal of the sum of two reciprocals: returns 1 / (1.0 / value1 + 1.0 / value2), the standard "parallel" combination of two scalar quantities.

## Description:
This function evaluates the expression 1 / (1.0 / value1 + 1.0 / value2). Algebraically, when ordinary finite Python numbers are used and arithmetic is well-defined, the result equals (value1 * value2) / (value1 + value2).

Known callers within the provided repository snapshot:
    - No callers were found in the provided snapshot. Typical usage (when present) is in numeric utilities or domain code combining two scalar quantities in parallel (e.g., combining resistances, conductances, rates).

Why this is a separate function:
    - Encapsulates the concise numeric pattern 1/(1/a + 1/b) to avoid repetitive reimplementation and to provide a single point to document and reason about numeric edge cases such as division-by-zero and type incompatibilities.

## Args:
    value1 (number-like): First operand. Must support the operation 1.0 / value1.
    value2 (number-like): Second operand. Must support the operation 1.0 / value2.

Notes on accepted types and interdependencies:
    - For built-in Python numeric types (int, float), operations 1.0 / valueX perform floating-point division and the function returns a Python float.
    - If either input is a type that does not support division by a Python float (for example Decimal when mixed with float), the arithmetic will raise a TypeError (or a type-specific error) coming from Python's operator machinery.
    - If inputs are NumPy scalars or arrays, the returned type and behavior follow NumPy's operator rules (the function may return NumPy scalar/array types or raise NumPy-specific errors); such behavior is governed by those libraries, not by this function.

## Returns:
    float (for ordinary Python int/float inputs) or a numeric value produced by the operands' division implementations:
        return_value = 1 / (1.0 / value1 + 1.0 / value2)

Additional notes on return values:
    - When value1 and value2 are ordinary finite Python numbers and arithmetic is valid, the returned value equals (value1 * value2) / (value1 + value2) and will be a Python float.
    - If inputs include infinities or NaNs, the returned value may be inf or nan per IEEE rules propagated by Python or underlying numeric libraries.
    - If inputs are non-standard numeric-like types (e.g., NumPy types), the concrete return type/value depends on those types' operator implementations.

## Raises:
    ZeroDivisionError:
        - Raised when computing 1.0 / value1 or 1.0 / value2 if value1 == 0 or value2 == 0.
        - Raised when (1.0 / value1 + 1.0 / value2) evaluates to 0.0 (for example when value1 and value2 are non-zero and 1/value1 + 1/value2 == 0.0), causing the final 1 / denom to attempt division by zero.

    TypeError (or type-specific exceptions):
        - Raised if an operand does not support division by a Python float (for example mixing Decimal with float without conversion), or if the operand's implementation raises another arithmetic-related exception.

All exceptions originate from the direct arithmetic operations in the single-line implementation; no exceptions are caught or transformed by this function.

## Constraints:
    Preconditions:
        - Caller is responsible for ensuring inputs are of types that support division with floats, or for handling exceptions raised by incompatible types.
        - To avoid ZeroDivisionError, do not pass value1 == 0, value2 == 0, or pairs where 1.0/value1 + 1.0/value2 == 0.0 (e.g., value2 == -value1 for ordinary finite numbers).

    Postconditions:
        - If the function returns normally, it has not mutated external state and has produced the numeric result defined above.
        - No I/O or global state changes occur.

## Side Effects:
    - None. The function performs pure arithmetic and has no I/O, no global mutations, and no external service interactions.

## Control Flow:
flowchart TD
    Start([Start: receive value1, value2])
    R1[Compute r1 = 1.0 / value1]
    R2[Compute r2 = 1.0 / value2]
    Sum[Compute denom = r1 + r2]
    Check{denom == 0.0?}
    ZD[Raise ZeroDivisionError]
    Res[Compute result = 1 / denom]
    Return[Return result]

    Start --> R1 --> R2 --> Sum --> Check
    Check -- yes --> ZD
    Check -- no --> Res --> Return

## Examples:
    Typical outcomes (ordinary Python numbers):
        - value1 = 4, value2 = 4
          returns 2.0
          (because 1/(1/4 + 1/4) == (4*4)/(4+4) == 2.0)

        - value1 = 1, value2 = 2
          returns approximately 0.6666666666666666  (2/3)

        - value1 = -3, value2 = 1.5
          returns 3.0

    Error examples and guidance:
        - value1 = 0 or value2 = 0
          computing 1.0 / valueX raises ZeroDivisionError; validate inputs or catch ZeroDivisionError in the caller.

        - value1 = 5, value2 = -5
          1.0/5 + 1.0/-5 == 0.0, so final 1/0.0 raises ZeroDivisionError.

        - Mixing Decimal with float (e.g., value1 = Decimal('1.0'), value2 = 2.0)
          attempting 1.0 / Decimal(...) will raise TypeError; convert Decimals to floats or use Decimal arithmetic consistently before calling this function.

    Integration guidance:
        - For user-provided or untrusted inputs, either validate and coerce types to int/float before calling or wrap calls in try/except to handle ZeroDivisionError and TypeError.

## `mingus.core.value.subtract` · *function*

## Summary:
Computes the harmonic-style difference of two numeric values and returns the value 1 / (1/value1 - 1/value2), equivalent to (value1 * value2) / (value2 - value1).

## Description:
This function evaluates the expression 1 / (1.0 / value1 - 1.0 / value2) and returns the numeric result.

Known callers within the codebase:
- No direct callers were found in the provided repository snapshot. This function may be intended as a small numeric utility used where pairwise "harmonic" subtraction (analogous to combining/isolating parallel quantities such as electrical resistances or harmonic means) is required.

Why this is a separate function:
- The expression 1/(1/v1 - 1/v2) is a concise numeric formula but easy to mistype or mis-express when used repeatedly. Extracting it:
  - Documents intent (a harmonic-style subtraction)
  - Centralizes handling of edge cases and errors (division-by-zero conditions)
  - Makes call sites more readable by naming the operation (subtracting in harmonic domain)

## Args:
    value1 (number): First operand. Expected to be a numeric type (int or float for built-ins). Not allowed to be zero.
    value2 (number): Second operand. Expected to be a numeric type (int or float for built-ins). Not allowed to be zero.
Notes on types and interdependencies:
- For Python built-in numeric inputs (int or float), the computations use floating-point division (the function uses 1.0 as the numerator), so the returned value will be a float.
- If value1 or value2 are non-scalar numeric containers (e.g., numpy arrays), behavior follows the rules of those types for division and subtraction and the result will be that container type (subject to those libraries' broadcasting rules).
- Both values must not be zero and must not be equal (see Raises).

## Returns:
    float or numeric-type: The computed value of 1 / (1.0 / value1 - 1.0 / value2), equivalently (value1 * value2) / (value2 - value1).
Possible return behaviors:
- For standard numeric inputs (int/float) the function returns a Python float.
- For array-like numeric types (e.g., numpy.ndarray), the function returns the array-type result as defined by those libraries.
- The result can be positive or negative depending on the inputs.
- No special sentinel values are returned; error conditions raise exceptions.

## Raises:
    ZeroDivisionError:
        - If value1 == 0 or value2 == 0: the sub-expression 1.0 / valueX triggers a division-by-zero.
        - If 1.0 / value1 - 1.0 / value2 == 0 (which occurs when value1 == value2 for finite non-zero values), the final division 1 / denom triggers a division-by-zero.
    TypeError:
        - If provided inputs do not support the required numeric operations (1.0 / value and subtraction), Python will raise TypeError or a similar exception from the underlying numeric type.

## Constraints:
Preconditions:
- value1 and value2 must be numeric and non-zero.
- value1 and value2 must not be equal (to avoid denominator zero).

Postconditions:
- On successful return, result * (1.0 / value1 - 1.0 / value2) ≈ 1, within floating-point precision limits.
- No global state or external I/O is modified by this function.

## Side Effects:
- None. The function performs pure computation and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    A[Start] --> B{Is value1 == 0 or value2 == 0?}
    B -- Yes --> C[Raise ZeroDivisionError during 1.0/value calculation]
    B -- No --> D[Compute denom = 1.0/value1 - 1.0/value2]
    D --> E{Is denom == 0? (value1 == value2)}
    E -- Yes --> F[Raise ZeroDivisionError during final division]
    E -- No --> G[Compute result = 1 / denom]
    G --> H[Return result]

## Examples:
- Basic numeric usage:
  - Input: value1 = 4, value2 = 6
  - Computation: 1 / (0.25 - 0.1666666667) = 1 / 0.0833333333 = 12.0
  - Result: 12.0

- Algebraic equivalence:
  - The function returns (value1 * value2) / (value2 - value1). For value1=2, value2=5, this gives (2*5)/(5-2)=10/3 ≈ 3.3333333333.

- Error handling guidance:
  - If the caller cannot guarantee non-zero and non-equal inputs, guard the call and handle ZeroDivisionError:
    - If value1 or value2 may be zero, validate before calling or catch ZeroDivisionError to avoid a runtime crash.
    - If value1 may equal value2 (within intended tolerance), consider checking equality (or near-equality for floats) before calling and define the desired behavior (e.g., return None or raise a custom error).

Notes:
- Because the function uses 1.0 in computations, standard int inputs will be coerced into floating-point arithmetic and the result will be a float. For numeric types that define their own division semantics, the result type follows those semantics.

## `mingus.core.value.dots` · *function*

## Summary:
Returns the numeric result of the expression value * 0.5 / (1.0 - 0.5**(nr + 1)), computed as a Python float.

## Description:
Computes the value multiplied by the factor 0.5 / (1.0 - 0.5**(nr + 1)). The function performs a pure numeric calculation with no side effects.

Known callers within the codebase:
    - None discovered in the provided scan. It may be used by external code that requires this specific mathematical factor or normalization.

Why this logic is extracted:
    - Encapsulating the expression in a single function centralizes the formula, avoiding repetition and making intent explicit where this exact factor is required. It separates the numeric factor computation from higher-level logic that consumes the result.

## Args:
    value (int | float):
        The base numeric magnitude to scale. Any numeric type supporting multiplication and division is accepted.
    nr (int | float, optional, default=1):
        The parameter used in the exponent part of the denominator: 0.5 ** (nr + 1). Typically expected to be a non-negative integer in conventional use, but the implementation accepts any numeric value. Default value is 1.

    Interdependencies:
        - The denominator uses 0.5 ** (nr + 1). If nr == -1 the denominator is zero and a ZeroDivisionError will occur.
        - Passing non-integer or negative nr values is allowed by the arithmetic operators but changes the numeric interpretation and range of results.

## Returns:
    float:
        The computed floating-point result of (0.5 * value) / (1.0 - 0.5 ** (nr + 1)).

        Notable cases:
            - nr == 0: returns value (because 0.5 / (1 - 0.5**1) == 1.0).
            - nr > 0 and large: the value approaches 0.5 * value as nr → +∞ (because 0.5**(nr+1) → 0).
            - nr == -1: denominator is zero → ZeroDivisionError.
            - nr < -1: denominator may be negative or large in magnitude, producing negative or large-magnitude results.

## Raises:
    ZeroDivisionError:
        Raised when the denominator evaluates to zero, which occurs exactly when nr == -1 (because 0.5 ** (nr + 1) == 1.0).
    TypeError:
        May be raised by Python if inputs are non-numeric or do not support the required arithmetic operations (multiplication, exponentiation, division).

## Constraints:
    Preconditions:
        - value must be numeric (supports multiplication and division).
        - nr must be chosen so that (1.0 - 0.5 ** (nr + 1)) != 0 (i.e., avoid nr == -1) unless the caller intends to handle ZeroDivisionError.
        - For conventional integer-based interpretations, use integer nr.

    Postconditions:
        - The function returns a finite Python float when inputs are numeric and denominator is non-zero.
        - No global state is modified.

## Side Effects:
    - None. The function performs only pure numeric computation and does not perform I/O, mutate external state, or call external services.

## Control Flow:
flowchart TD
    A[Start] --> B{Are inputs numeric?}
    B -->|No| C[Python raises TypeError during operations]
    B -->|Yes| D[Compute denom = 1.0 - 0.5 ** (nr + 1)]
    D --> E{denom == 0.0?}
    E -->|Yes| F[ZeroDivisionError raised]
    E -->|No| G[Compute result = (0.5 * value) / denom]
    G --> H[Return result]

## Examples:
    Example 1 — nr = 0 (identity):
        Inputs: value = 2.0, nr = 0
        Computation: denom = 1.0 - 0.5**1 = 0.5
                     result = (0.5 * 2.0) / 0.5 = 1.0 / 0.5 = 2.0
        Return: 2.0

    Example 2 — small positive nr:
        Inputs: value = 1.0, nr = 1
        Computation: result = (0.5 * 1.0) / (1.0 - 0.5**2) = 0.5 / 0.75 = 0.6666666666666666

    Example 3 — nr → large positive:
        Inputs: value = 1.0, nr = 50
        Behavior: 0.5 ** (nr + 1) is effectively 0, denom ≈ 1.0, result ≈ 0.5

    Example 4 — error handling:
        Inputs: value = 1.0, nr = -1
        Behavior: denom = 1.0 - 0.5**0 = 0.0 → ZeroDivisionError
        Suggested usage:
            - Validate nr != -1 before calling, or
            - Call inside try/except to catch ZeroDivisionError

    Example 5 — non-integer nr (supported but atypical):
        Inputs: value = 1.0, nr = 0.5
        Behavior: computes using 0.5 ** (1.5) and returns a float; interpret results accordingly.

## `mingus.core.value.triplet` · *function*

## Summary:
Returns the value scaled by the 3:2 tuplet ratio — effectively computes (3 * value) / 2 and returns that result.

## Description:
This is a convenience wrapper that delegates to the general-purpose ratio-scaling helper, invoking it with numerator 3 and denominator 2. It exists to make callers' intent explicit when they want the "triplet" scaling (three units in the time normally occupied by two).

Known callers:
    - No direct callers were found in the provided repository snapshot. If present, typical callers would be code that needs to convert or scale a quantity by the musical triplet ratio (3/2), for example when converting durations or quantities from a duple subdivision into a triplet subdivision.

Why this is a separate function:
    - Encapsulates a common, semantically-named operation (triplet scaling) so callers can express intent clearly instead of repeatedly calling the more general tuplet with literal constants.
    - Centralizes the 3:2 ratio choice in one place to avoid duplication and ease maintenance/testing.

## Args:
    value (numeric or numeric-like)
        - The quantity to be scaled.
        - Acceptable inputs: ints, floats, or array-like numeric containers (e.g., NumPy arrays) that support elementwise multiplication and division.
        - Interdependencies: the value must support multiplication by the integer 3 and division by the float 2.0 (i.e., value * 3 and (value * 3) / 2.0 must be valid operations for the provided type). For exact-decimal arithmetic (decimal.Decimal), mixing Decimal and float may raise TypeError; see Examples and Constraints.

## Returns:
    The result of computing (3 * value) / 2.0 using Python's numeric semantics (delegated to tuplet).

    Possible return shapes/types:
    - For scalar numeric inputs (int/float): returns a Python float (because of division by 2.0).
    - For array-like numeric inputs (NumPy arrays, etc.): returns whatever the underlying library produces for elementwise (3 * value) / 2.0 (typically an array-like).
    - For non-standard numeric types, the return type follows the host type semantics; if those semantics do not support division by a float, a TypeError may be raised.

    Edge-case numeric outcomes:
    - Since the denominator is a fixed literal 2, conversion and zero-division issues from the denominator do not occur.
    - NaN/Infinity behavior follows IEEE rules when present in value or intermediate results.

## Raises:
    TypeError
        - If the provided value's type does not support multiplication by 3 or division by 2.0 (for example, Decimal objects divided by a float).
        - These exceptions originate from the underlying arithmetic operations (not explicitly raised by this wrapper).

    (Not raised by this wrapper)
        - ZeroDivisionError and ValueError related to converting the denominator do not apply here because the denominator is the literal 2 (float(2) is always 2.0 and not zero).

## Constraints:
    Preconditions:
        - The caller must ensure value supports the operations value * 3 and (value * 3) / 2.0.
        - If exact rational or Decimal arithmetic is required, callers should avoid this function or ensure all operands are Decimal-aware (do not mix Decimal with floats).

    Postconditions:
        - No mutation of the input value.
        - If the function returns normally, the returned result equals (3 * value) / 2.0 according to the numeric semantics of the operands.

## Side Effects:
    - None. Pure computation with no I/O, no global state mutation, and no external service calls.

## Control Flow:
flowchart TD
    Start --> CallTuplet["Call tuplet(value, 3, 2)"]
    CallTuplet --> PropagateErrors{"tuplet raises TypeError?"}
    PropagateErrors -- Yes --> RaiseTypeError["Propagate TypeError"] --> End
    PropagateErrors -- No --> ReturnResult["Return result of tuplet"] --> End

## Examples:
    - Integer input:
        value = 4
        # result == (3 * 4) / 2.0  -> 6.0

    - Float input:
        value = 1.5
        # result == (3 * 1.5) / 2.0  -> 2.25

    - NumPy array input (elementwise):
        import numpy as np
        value = np.array([1.0, 2.0])
        # result == array([1.5, 3.0])

    - Decimal caution (may raise TypeError due to mixing Decimal and float):
        from decimal import Decimal
        value = Decimal('1.5')
        try:
            # (3 * Decimal('1.5')) / 2.0 attempts Decimal / float and may raise TypeError
            result = triplet(value)
        except TypeError:
            # For exact Decimal arithmetic, do:
            result = (Decimal('3') * value) / Decimal('2')

## `mingus.core.value.quintuplet` · *function*

## Summary:
Returns the value scaled by the ratio 5:4 — equivalently computes (5 * value) / 4.0 — by delegating to the generic ratio-scaling utility.

## Description:
This function is a thin convenience wrapper that calls the common ratio-scaling utility with numerator 5 and denominator 4. It centralizes the semantic meaning "apply a quintuplet (5:4) scaling" so call sites can express the musical/temporal ratio intent without repeating numeric literals.

Known callers within the provided codebase:
    - None found in the provided repository snapshot. It is a small public utility exported to make higher-level code readably express a 5:4 tuplet conversion when needed.

Why this logic is extracted:
    - The tuple/tuplet logic (multiply-then-divide by a rational ratio) is implemented in a general helper (tuplet). quintuplet encodes the common, named ratio (5:4) so callers use an expressive helper instead of inlining numeric constants and the multiply/divide expression. This enforces a clear responsibility boundary: tuple/tuplet performs arithmetic; quintuplet encodes a specific ratio.

## Args:
    value (numeric or numeric-like)
        - The quantity to scale by 5/4.
        - Typical values: int, float, or numeric arrays (e.g., NumPy ndarray). Also may be other numeric-like types (Decimal, fractions.Fraction) but see Constraints for caveats.
        - There is no default; the single positional argument is required.
    Interdependencies:
        - This function always uses denominator 4 (converted internally to float by tuplet). Therefore, mixing value with high-precision types (Decimal) can lead to TypeError because division will be performed with a float denominator.

## Returns:
    - The result of (5 * value) / 4.0, computed under Python's numeric semantics.
    - Return value details:
        * If value is an int or float: returns a Python float (e.g., quintuplet(3) -> 3.75).
        * If value is an array-like with elementwise arithmetic (NumPy arrays): returns an array-like result of elementwise (5 * value) / 4.0.
        * If value is a non-standard numeric type, the return follows those types' operator semantics; mixing with a float denominator may raise TypeError.
    - Edge-case outcomes:
        * If value contains NaN or the arithmetic yields NaN/inf, the function will return NaN/inf per IEEE arithmetic rules (no special handling).

## Raises:
    - TypeError
        * When the multiplication or subsequent division is not supported between the provided value's type and the numeric operands used by the helper. Example: dividing a Decimal by a float raises TypeError in many implementations.
        * When value's __mul__ or __truediv__ raises TypeError for the given operand types.
    - Any exceptions raised by evaluating value * 5 (e.g., ValueError from custom types) will propagate.
    - Note: ZeroDivisionError and ValueError related to converting the denominator are not possible here because the denominator is the literal 4 (float(4) == 4.0), which is valid and non-zero. Any conversion errors documented for the generic tuplet are therefore not applicable to this wrapper.

## Constraints:
    Preconditions:
        - value must be a type that supports multiplication by 5 and division by a float (4.0), or be an array-like type providing compatible elementwise semantics.
        - Avoid passing Decimal instances (or other exact types) unless you intend to accept TypeError or perform an explicit conversion to a compatible type first.
    Postconditions:
        - No mutation of the input value is performed by this function.
        - On successful return, the result equals (5 * value) / 4.0 under the host numeric semantics.

## Side Effects:
    - None. Pure computation: no I/O, no global state mutation, no network or external resource access.

## Control Flow:
flowchart TD
    Start --> CallTuplet["Call tuplet(value, 5, 4)"]
    CallTuplet --> TupletMultiply["tuplet: compute numerator = 5 * value"]
    TupletMultiply --> TupletConvert["tuplet: denom = float(4) -> 4.0"]
    TupletConvert --> TupletDivide{"denom == 0.0?"}
    TupletDivide -- No --> TupletCompute["tuplet: result = numerator / denom"]
    TupletCompute --> Return["Return result to caller"]
    TupletDivide -- Yes --> (ImpossibleDenomZero)["Denom is 4.0, not zero; ZeroDivisionError cannot occur here"]

## Examples:
    - Basic scalar usage:
        # result = (5 * 3) / 4.0 -> 3.75
        result = quintuplet(3)

    - Floating-point input:
        # result = (5 * 2.0) / 4.0 -> 2.5
        result = quintuplet(2.0)

    - Array-like input (NumPy):
        # elementwise scaling
        import numpy as np
        arr = np.array([1.0, 2.0, 3.0])
        result = quintuplet(arr)  # -> array([1.25, 2.5 , 3.75])

    - Decimal caution (error handling):
        from decimal import Decimal
        try:
            # Decimal * int -> Decimal, but Decimal / float may raise TypeError
            result = quintuplet(Decimal('1.0'))
        except TypeError:
            # convert to float first or perform Decimal-safe arithmetic explicitly
            result = (Decimal('5') * Decimal('1.0')) / Decimal('4')

    - Defensive wrapper example:
        # ensure Decimal-safe result by converting operands to Decimal before applying 5/4
        from decimal import Decimal
        def quintuplet_decimal(value):
            d5 = Decimal(5)
            d4 = Decimal(4)
            return (d5 * Decimal(value)) / d4

## `mingus.core.value.septuplet` · *function*

## Summary:
Scales a numeric or numeric-like value by the septuplet ratio (either 7/4 or 7/8) and returns the scaled result.

## Description:
Selects one of two fixed septuplet ratios and delegates the numeric scaling to the tuplet utility:
- If in_fourths is True, applies the 7:4 ratio (compute 7 * value, then divide by 4).
- If in_fourths is False, applies the 7:8 ratio (compute 7 * value, then divide by 8).

Known callers:
- No direct callers were found in the provided repository snapshot. Typically used where musical time-values or other quantities need to be scaled by a septuplet factor relative to quarter-note (4ths) or eighth-note (8ths) subdivisions.

Why this logic is extracted:
- Encapsulates the specific septuplet constants (7/4 and 7/8) and the choice between them, keeping callers simple and avoiding repeated numeric literals. Delegating arithmetic to tuplet centralizes the multiply-then-divide pattern and its numeric semantics.

## Args:
    value (numeric or numeric-like)
        The value to scale. Typical scalar types: int, float. May also be an array-like (e.g., a NumPy ndarray) that supports elementwise multiplication and division.
    in_fourths (bool, optional)
        If True (default), use the 7:4 ratio. If False, use the 7:8 ratio.
        Any truthy/falsy value is accepted by Python coercion, but callers should pass a bool for clarity.

## Returns:
    The scaled result:
    - When in_fourths is True: the result equals (7 * value) / 4.0 (computed via tuplet(value, 7, 4)).
    - When in_fourths is False: the result equals (7 * value) / 8.0 (computed via tuplet(value, 7, 8)).

    Return type details:
    - For scalar numeric inputs (int/float): typically a Python float.
    - For array-like numeric inputs: the returned type and shape follow the array library's elementwise semantics (for example, a NumPy array with the same shape).
    - For other numeric-like types, the return type follows the underlying arithmetic semantics.

## Raises:
    TypeError
        - If the provided value's type does not support multiplication by the integer 7 or subsequent division by a float (e.g., incompatible custom object). This error originates from the arithmetic operations delegated to tuplet.
    Note about tuplet-related exceptions:
        - The tuplet helper generally converts its denominator argument with float(rat2) and may raise ValueError or TypeError for non-convertible denominators, or ZeroDivisionError if the denominator converts to 0.0. However, septuplet always passes literal integer denominators 4 or 8, so those conversion-related exceptions (ValueError, TypeError during float(rat2)) and ZeroDivisionError from denom == 0.0 cannot occur in this function's calls to tuplet.

## Constraints:
    Preconditions:
        - value must support multiplication by an integer and division by a float (or be an array-like supporting elementwise operations).
        - in_fourths should be a boolean (or truthy/falsy) indicating which ratio to apply.

    Postconditions:
        - The function returns a new value equal to (7 * value) / 4.0 if in_fourths is True, otherwise (7 * value) / 8.0.
        - No input arguments are mutated.

## Side Effects:
    - None. Pure computation with no I/O, no global state mutation, and no external service calls.

## Control Flow:
flowchart TD
    Start --> Check["Evaluate in_fourths (truthy?)"]
    Check -- True --> Call4["Call tuplet(value, 7, 4)"]
    Call4 --> Return4["Return result (7*value/4.0)"]
    Check -- False --> Call8["Call tuplet(value, 7, 8)"]
    Call8 --> Return8["Return result (7*value/8.0)"]
    Return4 --> End["End"]
    Return8 --> End

## Examples:
    - Scalar (quarter-note based septuplet):
        Given value = 1.0 and in_fourths = True, the result is (7 * 1.0) / 4.0 == 1.75.

    - Scalar (eighth-note based septuplet):
        Given value = 0.5 and in_fourths = False, the result is (7 * 0.5) / 8.0 == 0.4375.

    - Array-like (NumPy or similar library):
        If values is a NumPy array [0.25, 0.5, 1.0], calling septuplet(values, True) yields an array where each element is (7 * element) / 4.0, following the array library's elementwise semantics.

    - Error handling (incompatible type):
        If value is None or another type that cannot be multiplied by 7, a TypeError raised by the underlying arithmetic will propagate; callers should validate inputs when necessary.

## `mingus.core.value.tuplet` · *function*

## Summary:
Scales a numeric or numeric-like value by a rational factor by computing (rat1 * value) / float(rat2).

## Description:
Performs the arithmetic expression (rat1 * value) divided by rat2 after converting rat2 to a Python float via float(rat2). The function centralizes this multiply-then-divide pattern and makes the denominator conversion explicit.

Known callers:
    - No direct callers were found in the provided repository snapshot. The function appears to be a small utility intended for ratio-based scaling (for example, scaling durations or quantities by a tuplet ratio), but specific usages are not present in the provided code.

Purpose / Why extracted:
    - Encapsulates a concise numeric transformation so callers don't duplicate the multiplication and division expression and so the denominator conversion to float is handled in one place. This simplifies testing and clarifies intentions where used.

## Args:
    value (numeric or array-like)
        - The base quantity to scale. Typical scalar types: int, float. May also be a numeric-like container (e.g., NumPy ndarray), in which case elementwise arithmetic is governed by the container's numeric semantics.
    rat1 (numeric)
        - Numerator of the ratio. Expected to support multiplication with value (e.g., int, float).
    rat2 (numeric)
        - Denominator of the ratio. Will be converted with float(rat2) before the division.

    Interdependencies:
    - rat2 must be convertible to float and must not be zero after conversion (float(rat2) != 0.0) unless caller expects a ZeroDivisionError.
    - Mixing high-precision numeric types (e.g., decimal.Decimal) with float conversion is not safe: the conversion or the mixed arithmetic may raise TypeError. See Raises and Examples.

## Returns:
    The result of the expression (rat1 * value) / float(rat2).

    Return types by input patterns:
    - For scalar numeric inputs (int/float): a Python float is produced.
    - For array-like numeric inputs (NumPy arrays, etc.): the return value will be whatever the underlying numeric library yields (typically an array-like with elementwise division).
    - For non-standard numeric types, return type follows the host environment and operand behavior.

    Special numeric outcomes:
    - If float(rat2) is NaN, the result will be a NaN per IEEE rules (not an exception).
    - If float(rat2) is positive or negative infinity, the result will be zero (or signed zero) per IEEE rules.
    - If float(rat2) is 0.0, a ZeroDivisionError is raised.

## Raises:
    ZeroDivisionError
        - Raised when float(rat2) == 0.0 (division by zero is attempted).
    ValueError
        - Raised when float(rat2) cannot convert the provided value (e.g., float("abc")).
    TypeError
        - Raised when:
            * float(rat2) is called on a type that cannot be converted to float (e.g., a complex number), or
            * arithmetic operations between value/rat1 and the coerced denominator are not supported by the operand types, or
            * mixing types such as decimal.Decimal with float operands leads to unsupported operations.
    Note:
        - The function itself does not explicitly check types; these exceptions originate from the built-in float conversion and Python arithmetic.

## Constraints:
    Preconditions:
        - rat2 should be a scalar convertible to float (non-complex) and not equal to 0.0 after conversion, unless the caller intends to handle ZeroDivisionError.
        - value and rat1 should be types that support multiplication and division with the resulting float denominator (or be array-like types that define elementwise operations).
        - If exact Decimal arithmetic is required, do not use this function with Decimal operands without converting rat2 to Decimal and performing Decimal-aware operations separately.

    Postconditions:
        - No mutation of input arguments.
        - If the function returns normally, the returned result equals (rat1 * value) / float(rat2) under Python's numeric semantics.

## Side Effects:
    - None. Pure computation with no I/O, no global state mutation, and no external calls.

## Control Flow:
flowchart TD
    Start --> Multiply["Compute numerator = rat1 * value"]
    Multiply --> Convert["Attempt denom = float(rat2)"]
    Convert --> ConversionError{"float(rat2) raises ValueError/TypeError?"}
    ConversionError -- Yes --> RaiseConversionError["Propagate ValueError/TypeError"] --> End
    ConversionError -- No --> CheckZero{"Is denom == 0.0?"}
    CheckZero -- Yes --> RaiseZero["Raise ZeroDivisionError"] --> End
    CheckZero -- No --> Compute["Compute numerator / denom"]
    Compute --> Return["Return computed result"] --> End

## Examples:
    - Scalar usage:
        value = 3
        rat1 = 2
        rat2 = 4
        result = (2 * 3) / 4.0  # -> 1.5

    - Denominator zero handling:
        try:
            result = tuplet(1, 1, 0)
        except ZeroDivisionError:
            # handle invalid denominator
            pass

    - NaN and infinity denominators:
        import math
        tuplet(1, 1, float('nan'))   # -> nan (no exception)
        tuplet(1, 1, float('inf'))   # -> 0.0

    - Complex or non-convertible denominator:
        # float(complex(1,2)) raises TypeError
        try:
            tuplet(1, 1, complex(1, 2))
        except TypeError:
            # handle invalid denominator type
            pass

    - Decimal caution:
        from decimal import Decimal
        value = Decimal('1.0')
        rat1 = Decimal('3')
        rat2 = Decimal('2')
        # This function converts rat2 to float, and mixing Decimal with float may raise TypeError or produce unexpected results.
        # For Decimal-accurate arithmetic, perform Decimal-aware operations instead:
        result = (rat1 * value) / Decimal('2')  # use Decimal for denominator as well

## `mingus.core.value.determine` · *function*

*No documentation generated.*

