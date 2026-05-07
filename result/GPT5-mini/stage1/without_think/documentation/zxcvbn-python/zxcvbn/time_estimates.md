# `time_estimates.py`

## `zxcvbn.time_estimates.estimate_attack_times` · *function*

## Summary:
Compute estimated crack times (in seconds and as human-readable labels) for several attacker scenarios and convert the numeric guess estimate into a discrete 0–4 strength score.

## Description:
This function takes a numeric estimate of how many guesses an attacker would need to crack a secret and produces:
- crack_times_seconds: a mapping of four attacker scenarios to Decimal durations (seconds),
- crack_times_display: the same durations rendered as short human-readable English labels via the display_time helper,
- score: an integer 0..4 produced by guesses_to_score(guesses).

Known callers:
- No direct callers were discovered in the provided code snapshot. Typical call sites are higher-level password-strength or time-estimation pipelines that compute a numeric `guesses` estimate and then call this function to produce durations and a UI-facing score.

Why extracted:
- Encapsulates the mapping from raw guess-count estimates into multiple attacker-rate scenarios and their human-readable labels, plus bucketing into a 0–4 score. This keeps formatting and scenario definitions centralized so UI or feedback code can consume a single consistent structure instead of duplicating scenario rates and conversion logic.

## Args:
    guesses (int | float | Decimal | any numeric-like)
        - Required. A numeric estimate of the number of guesses an attacker would need.
        - Typical values: non-negative integers or Decimal objects produced by the guess-estimation logic. Floats are accepted but will be passed to Decimal() which may preserve floating imprecision unless callers pass Decimal explicitly.
        - Interdependencies:
            * guesses is converted via Decimal(guesses) for numeric arithmetic. If `guesses` is of a type that Decimal() cannot convert (or that causes Decimal() to signal an invalid operation), the underlying Decimal constructor will raise and that exception will propagate.
            * The value is also passed to guesses_to_score which performs numeric comparisons; that function will raise TypeError if `guesses` is not comparable to numeric thresholds.

## Returns:
    dict with keys:
        'crack_times_seconds' : dict[str, Decimal]
            - Mapping of scenario name -> Decimal number of seconds estimated to crack.
            - Scenarios (exact keys used):
                * 'online_throttling_100_per_hour'
                * 'online_no_throttling_10_per_second'
                * 'offline_slow_hashing_1e4_per_second'
                * 'offline_fast_hashing_1e10_per_second'
            - Each value is computed as Decimal(guesses) divided by a Decimal representation of the attacker's guesses-per-second rate (the denominators are produced with float_to_decimal(...) so the division uses Decimal arithmetic).

        'crack_times_display' : dict[str, str]
            - Same keys as crack_times_seconds. Each value is the result of calling display_time(seconds) where seconds is the Decimal value above. display_time returns a short English phrase (e.g., '45 seconds', '2 days', 'centuries').

        'score' : int
            - Integer in 0..4 returned from guesses_to_score(guesses). See guesses_to_score for exact bucket thresholds.

Edge-case return behaviors:
    - If the function returns successfully, all three keys above are always present and populated.
    - The numeric durations are Decimal objects; they may represent very large or very small values depending on `guesses`.
    - There is no special sentinel return for invalid input — invalid input will raise exceptions (see Raises).

## Raises:
    Exceptions raised by underlying conversions and helper functions are propagated; this function does not catch them:
    - TypeError
        * If `guesses` is a type that cannot be converted to Decimal (Decimal(guesses) raises TypeError) or cannot be compared inside guesses_to_score.
    - decimal.InvalidOperation (or similar Decimal construction error)
        * If Decimal(guesses) or Decimal constructions inside float_to_decimal fail due to invalid input.
    - ValueError
        * If a float passed internally to float_to_decimal were NaN, float.as_integer_ratio() would raise ValueError; note that this function uses only finite numeric constants for denominators, so that particular path arises only if callers change code to pass non-finite values into float_to_decimal.
    - Any exception raised by display_time or guesses_to_score (for example, TypeError if their inputs are not numeric-like) will propagate.

## Constraints:
Preconditions:
    - callers should pass a numeric-like `guesses` (int, Decimal, or float). Non-numeric inputs will likely cause exceptions from Decimal() or comparison operations.
    - The function assumes denominators (attack rates) are non-zero; current implementation uses fixed finite non-zero rates.

Postconditions:
    - If no exception is raised:
        * Returned mapping contains the three keys described in Returns.
        * crack_times_seconds values are Decimal instances representing seconds.
        * crack_times_display values are non-empty short English strings (per display_time contract).
        * score is an integer in [0, 4] (per guesses_to_score contract).
    - No global Decimal context or other global state is mutated by this function (float_to_decimal uses a local Decimal Context).

## Side Effects:
    - None. The function performs pure computation and calls pure or pure-like helpers. It performs no I/O, network calls, file access, or mutation of global variables.

## Control Flow:
flowchart TD
    Start --> ComputeSeconds[Compute crack_times_seconds mapping]
    ComputeSeconds --> ForEach[For each (scenario, seconds) in mapping]
    ForEach --> CallDisplay[Call display_time(seconds) -> label]
    CallDisplay --> StoreLabel[Store label in crack_times_display for scenario]
    StoreLabel --> NextItem{more scenarios?}
    NextItem -- yes --> ForEach
    NextItem -- no --> ComputeScore[Call guesses_to_score(guesses) -> score]
    ComputeScore --> Return[Return dict with crack_times_seconds, crack_times_display, score]
    Return --> End

## Examples:
Example 1 — typical successful call (integer guesses):
    - Input:  guesses = 1_000_000
    - Behavior:
        * crack_times_seconds['offline_fast_hashing_1e10_per_second'] = Decimal(1_000_000) / Decimal(1e10) -> Decimal small fraction (~1E-4 seconds)
        * crack_times_display entries will be short labels like 'less than a second' or 'N seconds' as determined by display_time.
        * score = guesses_to_score(1_000_000) -> integer bucket (see guesses_to_score docs).

Example 2 — Decimal input (recommended when upstream uses Decimal):
    - Input: guesses = Decimal('1E8')
    - Behavior:
        * All arithmetic is Decimal-based; crack_times_seconds values are Decimal results with predictable decimal behavior.
        * display_time accepts Decimal and will produce human-readable labels.

Example 3 — defensive usage with error handling:
    - If input might be non-numeric, validate or catch exceptions:
        try:
            result = estimate_attack_times(user_supplied_guesses)
        except (TypeError, ValueError, decimal.InvalidOperation) as exc:
            # handle invalid guess input (e.g., report error to caller, sanitize input)
            handle_invalid_input(exc)

Implementation notes for callers:
    - For maximum numeric precision and to avoid unintended Decimal-from-float artifacts, prefer passing an int or Decimal for `guesses` rather than a float.
    - The four attacker-rate scenario keys and their denominators are intentionally explicit and centralized here so UI code can present both precise (seconds) and human-friendly (display) estimates consistently.

## `zxcvbn.time_estimates.guesses_to_score` · *function*

## Summary:
Map a numeric guess-count estimate into a discrete 0–4 strength score by checking which predefined threshold bucket the guess count falls into.

## Description:
This function takes an estimated number of guesses required to crack a password and returns a small integer score (0 through 4) representing increasing strength. It is intended to be used by higher-level password-strength or feedback components that need a compact, user-facing score derived from a raw guess-count estimate (for example, a time/effort estimation pipeline that first computes `guesses` and then converts that into a discrete score for UI/display).

Why this is a separate function:
- It encapsulates the mapping logic from continuous guess counts to discrete score buckets so the same threshold behaviour is reused consistently across the codebase.
- Separating this mapping makes thresholds easy to inspect, test, and update without touching other time estimation or feedback code.

Known callers and typical context:
- Called by components that convert numeric cracking-estimates into user-facing scores (the time-estimation/strength-evaluation pipeline).
- Typically invoked after the code computes an estimated number of guesses; this function performs the final bucketing for presentation or deciding feedback tiers.

## Args:
    guesses (int | float | Decimal):
        A numeric estimate of how many guesses an attacker would need to crack the password.
        - Accepts integers, floats, or Decimal objects, i.e., any type that supports numeric ordering comparisons with Python floats.
        - No default value; callers must supply a numeric argument.
        - Typical values are non-negative, but negative numbers are accepted by the comparison semantics (they will be mapped to the lowest score).

## Returns:
    int
        An integer score in the range 0..4 inclusive:
        - 0 : guesses < 1_000 + 5
        - 1 : 1_000 + 5 <= guesses < 1_000_000 + 5
        - 2 : 1_000_000 + 5 <= guesses < 100_000_000 + 5
        - 3 : 100_000_000 + 5 <= guesses < 10_000_000_000 + 5
        - 4 : guesses >= 10_000_000_000 + 5

        Note: The function uses an additive delta of 5 in the comparisons; thresholds are implemented as strict "<" checks against (threshold + delta) as shown above.

## Raises:
    TypeError
        If `guesses` is a value that cannot be compared to floats (for example, passing a non-numeric object), Python will raise a TypeError when attempting the comparison operations. The function does not catch or translate such exceptions.

    (No other exceptions are explicitly raised by this function.)

## Constraints:
Preconditions:
- The caller should provide a numeric value for `guesses` (int, float, or Decimal) to avoid TypeError during comparisons.
- While negative values are accepted by the function, callers should normally pass non-negative estimates since negative guesses are semantically invalid for cracking estimates.

Postconditions:
- The return value is guaranteed to be an integer in [0, 4].
- No external state is modified.

## Side Effects:
- None. The function performs pure computation and has no I/O, no mutation of global state, and makes no external service calls.

## Control Flow:
flowchart TD
    Start([start])
    A{guesses < 1000 + 5?}
    B{guesses < 1_000_000 + 5?}
    C{guesses < 100_000_000 + 5?}
    D{guesses < 10_000_000_000 + 5?}
    E[/return 0/]
    F[/return 1/]
    G[/return 2/]
    H[/return 3/]
    I[/return 4/]

    Start --> A
    A -- yes --> E
    A -- no --> B
    B -- yes --> F
    B -- no --> C
    C -- yes --> G
    C -- no --> D
    D -- yes --> H
    D -- no --> I

## Examples:
- Typical numeric mapping:
    - If the estimate is 500, the function returns 0 (500 < 1005).
    - If the estimate is 50_000, the function returns 1 (50_000 < 1_000_005 but >= 1005).
    - If the estimate is 5_000_000_000, the function returns 3 (5e9 < 10_000_000_005).
    - If the estimate is 1e11, the function returns 4 (>= 10_000_000_005).

- Decimal usage:
    - A Decimal guess value is supported (provided it can be compared against floats in the environment). For instance, a Decimal('1E7') will be compared to the thresholds and bucketed accordingly.

- Error handling:
    - If a non-numeric value is passed (for example, a list or dict), the function will raise a TypeError at the comparison step. Callers should validate or convert input before calling if needed.

## `zxcvbn.time_estimates.display_time` · *function*

## Summary:
Return a concise, human-readable English phrase representing a duration given in seconds (e.g., "45 seconds", "2 days", "centuries").

## Description:
Converts a numeric duration in seconds into a single short English label by selecting the largest appropriate whole time unit (seconds, minutes, hours, days, months, years, centuries), rounding to the nearest whole unit, and pluralizing when needed.

Known callers within the provided context:
    - No direct callers were discovered in the provided preloaded context or source snippet. (A repository-wide caller search was unavailable while generating this doc.)
Typical usage contexts:
    - Formatting estimated durations for display in UIs, logs, reports, or diagnostic messages where a compact human-readable label is desired.
Responsibility boundary:
    - Encapsulates presentation/formatting logic for time durations so callers need only compute durations in seconds and delegate human-friendly rendering to this function. It does not compute durations or perform localization.

## Args:
    seconds (int | float | Decimal | any numeric-like): Duration in seconds to format.
        - Allowed values: any value that supports numeric comparison with integers and basic arithmetic (comparison, division).
        - Typical range: non-negative values are expected for meaningful results; negative values are accepted and treated as "less than a second" by the function logic.
        - Interdependencies: none.

## Returns:
    str: A short English phrase describing the duration. Possible outputs (exact strings returned by the implementation) and their triggering ranges are:
        - 'less than a second' when seconds < 1
        - 'N second' or 'N seconds' when 1 <= seconds < 60
        - 'N minute' or 'N minutes' when 60 <= seconds < 3,600
        - 'N hour' or 'N hours' when 3,600 <= seconds < 86,400
        - 'N day' or 'N days' when 86,400 <= seconds < 2,678,400 (month defined as 31 days)
        - 'N month' or 'N months' when 2,678,400 <= seconds < 32,140,800 (year defined as 12 * 31 days)
        - 'N year' or 'N years' when 32,140,800 <= seconds < 3,214,080,000 (century defined as 100 * year)
        - 'centuries' when seconds >= 3,214,080,000
    Notes:
        - Numeric N is computed by rounding to the nearest whole unit using Python's round().
        - For the 'centuries' case the function returns the literal 'centuries' (no numeric prefix).
        - The function pluralizes by appending 's' when the numeric value is present and not equal to 1.

## Raises:
    - The function performs comparisons and arithmetic directly on the input. If `seconds` does not support these operations (for example, a non-numeric type), Python will raise the corresponding exception (TypeError, ValueError, or other exceptions raised by that type). The function does not perform explicit type validation and will propagate such exceptions.

## Constraints:
    Preconditions:
        - Callers should pass a numeric-like value that can be compared to integers and divided.
    Postconditions:
        - The function returns a non-empty ASCII English string describing the duration.
        - No global state or external resources are modified.

## Side Effects:
    - None. The function is pure and performs no I/O, network calls, filesystem access, or mutation of external state.

## Control Flow:
flowchart TD
    A[Start] --> B{seconds < 1}
    B -- yes --> C[return 'less than a second']
    B -- no --> D{seconds < 60}
    D -- yes --> E[base = round(seconds); set '<base> second(s)'; return]
    D -- no --> F{seconds < 3600}
    F -- yes --> G[base = round(seconds/60); set '<base> minute(s)'; return]
    F -- no --> H{seconds < 86400}
    H -- yes --> I[base = round(seconds/3600); set '<base> hour(s)'; return]
    H -- no --> J{seconds < 2678400}
    J -- yes --> K[base = round(seconds/86400); set '<base> day(s)'; return]
    J -- no --> L{seconds < 32140800}
    L -- yes --> M[base = round(seconds/2678400); set '<base> month(s)'; return]
    L -- no --> N{seconds < 3214080000}
    N -- yes --> O[base = round(seconds/32140800); set '<base> year(s)'; return]
    N -- no --> P[return 'centuries']

## Examples:
Basic small durations:
    - display_time(0.3)   -> 'less than a second'
    - display_time(1)     -> '1 second'
    - display_time(45)    -> '45 seconds'

Minute/hour/day boundaries:
    - display_time(59.4)  -> '59 seconds'    (round(59.4) -> 59)
    - display_time(59.6)  -> '60 seconds'    (round(59.6) -> 60)
    - display_time(60)    -> '1 minute'
    - display_time(90)    -> '2 minutes'     (90 / 60 = 1.5 -> round -> 2)
    - display_time(3600)  -> '1 hour'
    - display_time(90000) -> '1 day'         (90000 / 86400 ~ 1.0417 -> round -> 1)

Month/year/century examples (using function's fixed unit definitions):
    - month = 31 days -> 2,678,400 seconds
    - year = 12 * month = 32,140,800 seconds
    - century = 100 * year = 3,214,080,000 seconds
    - display_time(60 * 60 * 24 * 40) -> '1 month'   (40 days ≈ 1.29 months -> round -> 1)
    - display_time(60 * 60 * 24 * 365) -> '12 months' (365 days maps to ~11.77 months -> round -> 12)
    - display_time(60 * 60 * 24 * 365 * 200) -> 'centuries' (>= century threshold)

Robust usage pattern:
    - If input may be non-numeric, guard the call:
        try:
            label = display_time(user_supplied_value)
        except Exception as e:
            handle_invalid_input(e)

Implementation notes for callers:
    - Unit definitions are approximate (month=31 days, year=12*31 days) and chosen for coarse, human-friendly estimates only.
    - Rounding means values close to unit boundaries can round up (e.g., 1.5 minutes -> '2 minutes').
    - The output is English-only and not localized.

## `zxcvbn.time_estimates.float_to_decimal` · *function*

## Summary:
Converts a Python float into an exact Decimal representation by computing its integer ratio and performing a high-precision rational division until the result is exact.

## Description:
This function turns the binary floating-point value into a Decimal that exactly represents the same rational value (the float's numerator/denominator ratio), avoiding the usual binary->decimal rounding surprises when printing or performing further decimal arithmetic.

Known callers within the repository:
    - No direct callers were found in the current codebase snapshot. Typical usage is inside time- or precision-sensitive code (for example, modules that compute time estimates or present numeric results to users) where a float must be represented as an exact Decimal for formatting, comparison, or further Decimal-based arithmetic.

Why this is extracted into a separate function:
    - Converting a float into an exact Decimal requires multiple steps (extracting the integer ratio, performing a controlled Decimal division with growing precision until exact). Extracting this logic enforces a clear responsibility boundary: reliably produce an exact Decimal from any finite float without changing global Decimal context or duplicating precision-handling logic across the codebase.

## Args:
    f (float): The input floating-point number to convert.
        - Expected to be a finite float (not NaN or infinite).
        - No default value; this parameter is required.
        - Interdependency: none beyond being a Python float-like object that implements as_integer_ratio() (standard float satisfies this).

## Returns:
    Decimal: A Decimal instance equal to the exact rational value n/d where (n, d) = f.as_integer_ratio().
    - The returned Decimal is computed in a local Decimal Context; it represents the float's exact value (not a decimal rounded representation).
    - Possible return behaviors:
        * For ordinary finite floats, returns an exact Decimal equal to the float's rational value.
        * For subnormal or very small/large finite floats, the function will increase precision until the division is exact and then return the exact Decimal.

## Raises:
    Propagated exceptions from underlying operations:
    - ValueError:
        * Raised by float.as_integer_ratio() if the float is NaN (not-a-number). This function does not catch it.
    - OverflowError:
        * Raised by float.as_integer_ratio() if the float is infinite. This function does not catch it.
    - (Very unlikely) Any exceptions raised while constructing Decimal from very large integers would propagate (e.g., MemoryError if system cannot allocate), but standard Decimal(int) calls do not typically raise for bounded Python ints.
    - DivisionByZero is not expected because as_integer_ratio() for a float yields a non-zero denominator for finite floats.

## Constraints:
Preconditions:
    - Caller should pass a float-like object that implements as_integer_ratio() and represents a finite numeric value.
    - No assumptions are made about the global Decimal context; the function uses (and mutates) a local Decimal Context object.

Postconditions:
    - The returned Decimal exactly equals Decimal(n) / Decimal(d) where (n, d) = f.as_integer_ratio().
    - The function does not change any global Decimal context or other global program state.

## Side Effects:
    - No I/O (no file, network, or stdout activity).
    - No mutation of global variables or the module state.
    - Local Decimal Context (ctx) flags and precision are mutated during computation, but ctx is a local object and does not affect the module-level or global Decimal context.

## Control Flow:
flowchart TD
    Start --> GetRatio
    GetRatio -->|n,d = f.as_integer_ratio()| MakeDecimals
    MakeDecimals --> CreateCtx
    CreateCtx --> Compute
    Compute --> CheckInexact
    CheckInexact -->|Inexact True| ClearFlag
    ClearFlag --> DoublePrec
    DoublePrec --> Recompute
    Recompute --> CheckInexact
    CheckInexact -->|Inexact False| ReturnResult
    ReturnResult --> End

(Descriptions:
- GetRatio: call f.as_integer_ratio()
- MakeDecimals: Decimal(n), Decimal(d)
- CreateCtx: Context(prec=60)
- Compute/Recompute: ctx.divide(numerator, denominator)
- CheckInexact: check ctx.flags[Inexact]
- ClearFlag: reset ctx.flags[Inexact] = False
- DoublePrec: ctx.prec *= 2
- ReturnResult: return the last result)

## Examples:
Example 1 — basic usage
    try:
        d = float_to_decimal(0.1)
        # d is a Decimal exactly equal to the binary float 0.1 (the long decimal expansion
        # that corresponds to the float bit-pattern), suitable for exact Decimal arithmetic
        # or formatting that exposes the float's exact value.
    except (ValueError, OverflowError) as exc:
        # Handle non-finite floats (NaN/inf) which cannot be converted to a rational
        # via as_integer_ratio()
        raise

Example 2 — guarding input
    import math
    x = float('nan')
    if math.isfinite(x):
        exact = float_to_decimal(x)
    else:
        # Decide how to handle NaN / infinity before conversion
        exact = None

Notes:
    - The function is deterministic for a given float on a given Python build.
    - It intentionally uses a fresh Context so it does not modify or rely on the global Decimal context.
    - The loop doubles precision until the Decimal division sets no Inexact flag; for standard IEEE-754 double floats this will terminate because the float's rational representation is finite (integers n and d).

