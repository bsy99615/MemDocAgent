# `meter.py`

## `mingus.core.meter.valid_beat_duration` · *function*

## Summary:
Determines whether a numeric duration represents a valid beat length by returning True only for positive powers of two (1, 2, 4, 8, ...); returns False otherwise.

## Description:
This helper validates a single duration value according to the rule "valid if and only if it is an exact power of two and not zero." Typical uses:
- Called by meter/time-signature validation code to ensure a note/beat duration can be represented as (1 / 2^n) subdivisions.
- Used before constructing or normalizing beat subdivisions in scheduling or notation code.

Known callers in this repository: None provided in the task context.
Why this logic is extracted:
- It encapsulates the single responsibility of testing the "power-of-two" property in one place rather than duplicating the loop and checks wherever durations must be validated.
- Keeps higher-level meter parsing/validation code concise and focused on structure rather than numeric checks.

## Args:
    duration (int or numeric): The duration to validate.
        - Expected: a non-negative integer (0, 1, 2, 4, 8, ...). The function treats 0 specially (returns False).
        - If a non-integer numeric is passed, behavior is undefined and may lead to non-termination for some inputs (see Constraints).
        - There are no interdependent parameters.

## Returns:
    bool: 
        - True if duration is an exact power of two and not zero (1, 2, 4, 8, ...).
        - False otherwise (including duration == 0, odd integers > 1, or integers that are not powers of two).

All observed return paths in the code:
- Immediately returns False when duration == 0.
- Immediately returns True when duration == 1.
- For duration > 1, repeatedly divides by 2; if any step yields an odd value (r % 2 == 1), returns False; otherwise, if repeated division reaches 1, returns True.

## Raises:
    This function does not explicitly raise any exceptions in the provided implementation.
    - Note: Passing certain non-integer numeric values may lead to an infinite loop rather than a raised exception.

## Constraints:
Preconditions:
- Callers should pass a non-negative integer value (preferably Python int). The function is designed to operate on integer durations.
- duration should be finite (not NaN or infinite).

Postconditions:
- After returning True, the caller can rely that the input represents 2^k for some integer k >= 0 (with the function returning False for 0, so effectively k >= 0 and value >= 1).
- After returning False, the input is known not to be a positive integer power of two, or was 0.

Edge cases and behavior notes:
- duration == 0: returns False (explicit check).
- duration == 1: returns True (explicit check).
- Negative integers: behavior follows the same controls but is not a supported input; negative values will typically return False early or later in the loop; callers should avoid negatives.
- Non-integer numeric values: the algorithm may never reach r == 1 (for example values < 1 that are not 1) and thus can loop indefinitely. Do not pass fractional durations unless you have pre-normalized them to integers.

## Side Effects:
- None. The function performs purely local numeric computation and does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start --> CheckZero
    CheckZero{duration == 0?}
    CheckZero -- Yes --> ReturnFalseZero[return False]
    CheckZero -- No --> CheckOne{duration == 1?}
    CheckOne -- Yes --> ReturnTrueOne[return True]
    CheckOne -- No --> InitR[r = duration]
    InitR --> LoopStart{r != 1?}
    LoopStart -- No --> ReturnTrueLoop[return True]
    LoopStart -- Yes --> CheckOdd{r % 2 == 1?}
    CheckOdd -- Yes --> ReturnFalseOdd[return False]
    CheckOdd -- No --> Divide[r = r / 2]
    Divide --> LoopStart

## Examples:
1) Valid integer power of two:
    - Input: 4
    - Behavior: 4 -> 2 -> 1, reaches 1 and returns True.
    - Result: True

2) Non-power-of-two integer:
    - Input: 6
    - Behavior: 6 % 2 == 0 => r -> 3; 3 % 2 == 1 => returns False.
    - Result: False

3) Zero:
    - Input: 0
    - Behavior: immediate check returns False.
    - Result: False

4) Fractional input (unsupported):
    - Input: 1.5
    - Behavior: not equal to 0 or 1; loop divides producing values that will not reach 1 exactly → may loop indefinitely.
    - Recommendation: normalize durations to integers before calling or guard against non-integer inputs.

Usage pattern (caller-side):
- Validate or normalize the incoming duration to an integer >= 0 before calling.
- Example pseudo-flow:
    1. Parse duration value from input.
    2. If not isinstance(duration, int) or duration < 0: reject or normalize.
    3. Call valid_beat_duration(duration) and branch on the boolean result.

## `mingus.core.meter.is_valid` · *function*

## Summary:
Returns True when a meter tuple/sequence represents a positive beat count and a valid beat duration; otherwise returns False.

## Description:
This function evaluates a two-part meter representation and enforces two independent requirements:
1) The first element (beat count) must be greater than zero.
2) The second element (beat duration) must be a valid beat duration according to the power-of-two rule validated by valid_beat_duration.

Known callers within this repository:
- No direct callers were discovered in the provided context. Typical callers (expected use cases) include meter/time-signature parsing and validation code, notation formatting, and scheduling components that must ensure a time signature/meter is well-formed before use.

Why this logic is extracted:
- It encapsulates the structural validation of a two-part meter (count and duration) so higher-level code can rely on a single boolean check rather than reimplement the short-circuit and numeric-validity logic.
- It centralizes the short-circuit policy: if the beat count is not positive, the duration is not validated.

## Args:
    meter (sequence): A sequence-like object (e.g., tuple or list) with at least two elements:
        - meter[0]: numeric (int or other numeric type) representing the number of beats per bar; expected to be comparable with 0.
        - meter[1]: numeric representing the beat duration; expected to be a non-negative integer suitable for valid_beat_duration (powers of two: 1,2,4,8,...).
    Notes on interdependencies:
        - The function treats meter as an indexed sequence and uses only the first two elements; additional elements are ignored.
        - The second element is passed directly to valid_beat_duration; its preconditions apply (preferably a non-negative integer).

## Returns:
    bool:
        - True if and only if:
            * meter[0] > 0 evaluates True, AND
            * valid_beat_duration(meter[1]) returns True (i.e., meter[1] is an exact positive power of two).
        - False otherwise. Because of Python's short-circuit evaluation, if meter[0] > 0 is False, valid_beat_duration is not called and the function returns False immediately.

## Raises:
    IndexError:
        - If meter is a sequence with fewer than two elements, accessing meter[0] or meter[1] raises IndexError.
    TypeError:
        - If meter is not a sequence or its elements do not support the operations performed (comparison meter[0] > 0 or being passed to valid_beat_duration), a TypeError (or other built-in exception from those operations) may be raised.
    Other runtime issues:
        - valid_beat_duration itself does not raise in the provided implementation but may loop indefinitely on certain non-integer inputs. That can cause the call to is_valid to hang rather than raise.

## Constraints:
Preconditions:
    - Caller should provide a sequence-like meter with length >= 2.
    - meter[0] should be a numeric type that can be compared to 0 (preferably an int >= 0).
    - meter[1] should be a non-negative integer (preferably Python int) because valid_beat_duration is defined only for integer durations.

Postconditions:
    - The function returns a boolean summarizing the two checks:
        * True guarantees meter[0] > 0 and that meter[1] is an exact positive power of two (1,2,4,8,...).
        * False guarantees at least one of those conditions failed (or an exception was raised before a boolean result).

## Side Effects:
    - None. The function performs no I/O and does not mutate global state. It only evaluates the provided inputs and calls valid_beat_duration as needed.

## Control Flow:
flowchart TD
    Start --> EvalCount
    EvalCount[Evaluate meter[0] > 0] --> CountTrue{meter[0] > 0 ?}
    CountTrue -- No --> ReturnFalseShortCircuit[return False (do not call valid_beat_duration)]
    CountTrue -- Yes --> CallValidDur[Call valid_beat_duration(meter[1])]
    CallValidDur --> ValidTrue{valid_beat_duration returned True?}
    ValidTrue -- Yes --> ReturnTrue[return True]
    ValidTrue -- No --> ReturnFalse[return False]

Notes:
    - The function relies on Python's left-to-right short-circuiting of the 'and' operator; valid_beat_duration is invoked only when meter[0] > 0 is True.

## Examples:
1) Common valid meter:
    - Input: a two-element tuple (4, 4) representing 4/4
    - Rationale: 4 > 0 is True; valid_beat_duration(4) is True (4 is a power of two)
    - Result: True

2) Non-positive beat count:
    - Input: (0, 4)
    - Rationale: meter[0] > 0 is False; valid_beat_duration is not called
    - Result: False

3) Invalid beat duration:
    - Input: (3, 6)
    - Rationale: 3 > 0 is True, but valid_beat_duration(6) is False (6 is not a power of two)
    - Result: False

4) Defensive calling pattern (recommended):
    - Ensure the meter sequence is well-formed before calling; for example, check length and types and handle IndexError/TypeError:
        - If meter is malformed, handle the exception or sanitize input before calling is_valid to avoid runtime errors or hanging due to invalid duration types.

## `mingus.core.meter.is_compound` · *function*

## Summary:
Returns True when a meter represents a valid "compound" time signature: it is structurally valid, its beat count is a multiple of three, and the beat count is at least six.

## Description:
This function classifies a two-element meter (beat count and beat duration) as compound by performing three checks in order:
1) Structural and semantic validity via is_valid(meter).
2) The beat count (meter[0]) is divisible evenly by 3.
3) The beat count is greater than or equal to 6.

Known callers within the codebase:
- No direct callers were discovered in the provided repository snapshot. Typical call sites include meter/time-signature parsing, notation formatting, rhythmic analysis, and scheduling components that need to decide whether to treat a time signature as compound for grouping or rendering purposes.

Why this logic is extracted:
- The compound-meter test is a distinct, repeatedly useful classification: it composes a generic "is the meter valid" check with two numeric predicates on the beat count. Extracting it avoids duplicating the short-circuit semantics and makes the intent explicit (valid + divisible-by-3 + >=6) so higher-level code can ask a single question instead of reimplementing the conditions.

## Args:
    meter (sequence): A sequence-like object (tuple, list, etc.) with at least two elements:
        - meter[0] (numeric): Number of beats per bar (beat count). Expected to be comparable with 0 and suitable for modulo operations.
        - meter[1] (numeric): Beat duration (e.g., denominator of a time signature). Passed to is_valid (and ultimately to valid_beat_duration) for validation.
    Notes:
        - Only the first two elements are used; additional elements are ignored.
        - The function does not coerce or normalize types; callers should supply reasonable numeric types (preferably ints).

## Returns:
    bool: True if and only if all three of the following hold:
        - is_valid(meter) returns True (i.e., the meter is structurally valid),
        - meter[0] % 3 == 0 (the beat count is an exact multiple of 3),
        - 6 <= meter[0] (the beat count is at least six).
    Possible return values / edge cases:
        - False is returned when any of those checks fails.
        - Because Python uses left-to-right short-circuit evaluation for 'and', if is_valid(meter) is False the numeric checks are not evaluated.

## Raises:
    IndexError:
        - If meter is a sequence with fewer than two elements, is_valid(meter) or direct indexing may raise IndexError which propagates from this function.
    TypeError (or other builtin exceptions):
        - If meter is not indexable or its elements do not support the required operations (comparison with 0, modulo), those operations may raise TypeError or other exceptions which will propagate.
    Exceptions raised by is_valid / valid_beat_duration:
        - Any exception raised by is_valid (or by valid_beat_duration called from is_valid) will propagate. For example, malformed meter[1] values that cause valid_beat_duration to fail/hang are not caught here.

## Constraints:
Preconditions:
    - Caller should supply a sequence-like meter with length >= 2.
    - meter[0] should be a numeric type that supports comparison and modulo operations (ints are recommended).
    - meter[1] should be appropriate for the validation performed by is_valid (preferably a non-negative integer suitable for valid_beat_duration).

Postconditions:
    - On successful return, the function yields a boolean:
        * True guarantees meter was valid and meter[0] is a multiple of 3 and >= 6.
        * False guarantees at least one of those predicates failed (or is_valid returned False).

## Side Effects:
    - None. The function performs no I/O and does not mutate global state. It only reads the provided input and calls is_valid.

## Control Flow:
flowchart TD
    Start --> CallIsValid[Call is_valid(meter)]
    CallIsValid --> IsValidTrue{is_valid returned True?}
    IsValidTrue -- No --> ReturnFalseShort[return False]
    IsValidTrue -- Yes --> EvalDiv3[Evaluate meter[0] % 3 == 0]
    EvalDiv3 --> Div3True{Divisible by 3?}
    Div3True -- No --> ReturnFalseDiv[return False]
    Div3True -- Yes --> EvalMin6[Evaluate 6 <= meter[0]]
    EvalMin6 --> Min6True{meter[0] >= 6?}
    Min6True -- No --> ReturnFalseMin[return False]
    Min6True -- Yes --> ReturnTrue[return True]

## Examples:
1) Typical compound meter:
    - Input: (6, 4)  # 6/4 time
    - Behavior: is_valid((6,4)) -> True, 6 % 3 == 0 True, 6 <= 6 True
    - Result: True

2) Larger compound meter:
    - Input: (9, 8)  # 9/8 time
    - Result: True

3) Valid but not compound (too few beats):
    - Input: (3, 4)  # 3/4 time is not treated as "compound" by this function because 3 < 6
    - Result: False

4) Valid but not compound (not divisible by 3):
    - Input: (4, 4)  # 4/4
    - Result: False

5) Malformed input (example of defensive usage):
    - Example:
        try:
            is_compound((4,))  # missing beat duration
        except IndexError:
            # handle or sanitize meter before calling
            pass

6) Defensive pattern to avoid hangs or type errors:
    - Validate shape and element types before calling (e.g., check len(meter) >= 2 and isinstance(meter[0], int) and isinstance(meter[1], int)) to avoid propagated exceptions or unexpected behavior from valid_beat_duration.

## `mingus.core.meter.is_simple` · *function*

## Summary:
Returns a boolean indicating whether a two-element meter representation is considered valid/simple by delegating to the central meter validation routine.

## Description:
- Known callers within this repository:
    - None discovered in the provided context. Typical callers (expected use cases) include meter/time-signature parsing, notation formatting, scheduling, or any higher-level code that needs a quick boolean check that a meter/time-signature value is well-formed before it is used.
- Purpose and responsibility:
    - This function is a minimal, semantically named wrapper that forwards its argument to the canonical meter validator (is_valid). It exists to provide an alternative API name (readability, backward compatibility, or a clearer semantic choice) while centralizing the actual validation logic in a single place.
    - Responsibility boundary: do not implement validation here. Any change to validation rules must be made in the underlying validator (is_valid). This wrapper only delegates and returns that result.

## Args:
    meter (sequence): A sequence-like object (e.g., tuple or list) with at least two elements:
        - meter[0]: numeric (int or comparable numeric type) representing the number of beats per bar. Expected to be comparable with 0.
        - meter[1]: numeric representing the beat duration (passed unchanged to the validator).
    Notes:
        - Only the first two elements are used; extra elements are ignored.
        - The function does not coerce or sanitize inputs — callers should ensure the sequence shape and element types meet the validator's preconditions if they wish to avoid exceptions.

## Returns:
    bool:
        - Exactly the boolean result returned by the underlying validator (is_valid).
        - True indicates the meter meets the validation rules (typically: positive beat count and a valid beat duration such as a positive power-of-two value).
        - False indicates the meter failed validation.
        - No additional interpretation or transformation of the result is performed.

## Raises:
    - IndexError:
        - If meter has fewer than two elements, indexing (meter[0] or meter[1]) performed by the validator will raise IndexError.
    - TypeError (or other built-in exceptions):
        - If meter is not a sequence or the elements do not support necessary operations (e.g., comparison meter[0] > 0) the call may raise TypeError or another exception propagated from the validator.
    - Blocking/hang:
        - If the underlying validator expects certain numeric types and receives inappropriate input that leads to non-terminating behavior, the call may appear to hang. (This reflects behavior of the validator; the wrapper does not introduce new failure modes.)

## Constraints:
- Preconditions:
    - Caller should provide a sequence-like meter with length >= 2.
    - meter[0] should be a numeric type comparable to 0 (preferably a non-negative int).
    - meter[1] should be of a type appropriate for the underlying validator (typically a non-negative integer representing a beat duration).
- Postconditions:
    - The function returns a boolean that exactly reflects the underlying validator's assessment of the provided meter.
    - No input objects are mutated and no side effects occur.

## Side Effects:
- None. The function performs no I/O, does not mutate external state, and only returns the value produced by the underlying validator.

## Control Flow:
flowchart TD
    Start --> CallValidator[Call underlying validator (is_valid) with meter]
    CallValidator --> ReturnResult[Return the boolean result from validator]

## Examples:
1) Typical valid usage:
    - Input: (4, 4)
    - Behavior: Delegates to validator; validator checks 4 > 0 and that 4 is a valid beat duration (power of two) and returns True.
    - Result: True

2) Invalid beat count:
    - Input: (0, 4)
    - Behavior: Validator finds beat count not > 0, returns False (no duration check).
    - Result: False

3) Invalid duration:
    - Input: (3, 6)
    - Behavior: Validator checks beat count (3 > 0) then rejects duration 6 (not a power of two), returns False.
    - Result: False

4) Defensive usage with error handling:
    - Before calling, ensure meter is well-formed to avoid IndexError/TypeError:
        - Example pattern: verify len(meter) >= 2 and isinstance(meter[0], (int, float)) before calling.
    - If unexpected inputs are possible, call within try/except to handle IndexError or TypeError raised by the validator.

## `mingus.core.meter.is_asymmetrical` · *function*

## Summary:
Return True precisely when the meter passes structural validation and the expression meter[0] % 2 == 1 evaluates True; otherwise return False.

## Description:
This function implements a two-step boolean predicate:
1) Call is_valid(meter). If is_valid(meter) is False (or raises), the function short-circuits accordingly.
2) If is_valid(meter) returns True, evaluate meter[0] % 2 == 1 and return that boolean result.

Known callers:
- No direct callers were discovered in the provided context. Typical consumers include meter/time-signature parsing, notation formatting, rhythm scheduling, or other code that must distinguish meters whose first element yields a remainder of 1 when taken modulo 2.

Why this logic is extracted:
- The predicate "valid meter AND (meter[0] % 2 == 1)" is a frequently-needed check (i.e., an asymmetrical meter test). Encapsulating it avoids repeated composition of validation and oddness checks and preserves consistent short-circuit semantics.

## Args:
    meter (sequence-like):
        - Expected to be an indexable sequence (e.g., tuple or list) with at least two elements for is_valid to operate.
        - meter[0]: the beat-count value (used in the modulo expression).
        - meter[1]: the beat-duration value (used by is_valid).
    Notes:
        - The function itself does not inspect meter[1]; is_valid(meter) may inspect both elements.
        - The function uses Python's % operator on meter[0]; behavior depends on the runtime types of meter[0].

## Returns:
    bool:
        - True if and only if is_valid(meter) returns True AND the expression meter[0] % 2 == 1 evaluates to True.
        - False if is_valid(meter) returns False, or if is_valid(meter) returns True but meter[0] % 2 == 1 evaluates False.
        - Because of Python's short-circuit evaluation, meter[0] % 2 == 1 is evaluated only when is_valid(meter) returns True.

## Raises:
    IndexError:
        - May be raised by is_valid(meter) (for example if meter has fewer than two elements) or by attempting to index meter[0] in the second step. The function does not catch IndexError; it propagates.
    TypeError (or other builtin exceptions):
        - May be raised if meter is not indexable, if its elements are of types incompatible with is_valid, or if the modulo operator (%) is unsupported for the runtime type of meter[0]. Exceptions raised by is_valid or by the modulo operation propagate unchanged.
    Notes:
        - Any exception raised inside is_valid (including from functions it calls) will propagate through this function.

## Constraints:
Preconditions:
    - To avoid runtime exceptions, callers should pass a sequence-like meter with length >= 2 and elements of types suitable for is_valid and for the modulo operation on meter[0].
    - No additional checks are performed by this function beyond delegating to is_valid and computing the modulo.

Postconditions:
    - On successful return (no exception), the function yields a boolean that exactly reflects the conjunction of is_valid(meter) and the modulo test on meter[0].

## Side Effects:
    - None. The function performs no I/O and does not mutate external/global state. It only invokes is_valid and evaluates a pure expression on the provided input.

## Control Flow:
flowchart TD
    Start --> CallIsValid[Call is_valid(meter)]
    CallIsValid --> IsValidTrue{is_valid returned True?}
    IsValidTrue -- No --> ReturnFalse1[return False]
    IsValidTrue -- Yes --> EvalModulo[Evaluate meter[0] % 2 == 1]
    EvalModulo --> ModTrue{Result == True?}
    ModTrue -- Yes --> ReturnTrue[return True]
    ModTrue -- No --> ReturnFalse2[return False]

## Examples:
1) Asymmetrical and valid (expected True):
    - Input: (3, 4)
    - Behavior: is_valid((3,4)) returns True; 3 % 2 == 1 is True; function returns True.

2) Valid but modulo yields False (expected False):
    - Input: (4, 4)
    - Behavior: is_valid((4,4)) returns True; 4 % 2 == 1 is False; function returns False.

3) Invalid meter (expected False or exception depending on is_valid):
    - Input: (0, 4)
    - Behavior: is_valid((0,4)) returns False; function returns False (short-circuited).

4) Malformed input (may raise IndexError/TypeError):
    - Input: (3,) or 'not-a-sequence'
    - Behavior: is_valid may raise IndexError/TypeError or the modulo operation may raise; such exceptions propagate and should be handled by the caller if needed.

Usage tip:
    - If callers cannot guarantee well-formed meter sequences, validate shape and types before calling or wrap calls in try/except to handle propagated IndexError/TypeError.

