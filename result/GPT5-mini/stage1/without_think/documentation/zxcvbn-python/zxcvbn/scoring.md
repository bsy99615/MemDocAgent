# `scoring.py`

## `zxcvbn.scoring.calc_average_degree` · *function*

## Summary:
Computes the average degree (number of neighbors) per node for an adjacency mapping and returns it as a floating-point value.

## Description:
This function accepts an adjacency mapping (graph) and calculates the mean number of neighbors across all nodes by:
- Iterating every (node, neighbors) pair in the mapping,
- Counting truthy entries in each neighbors iterable (falsy values like None, '', 0 are ignored),
- Summing those counts and dividing by the number of nodes.

Known callers within the repository:
- No direct callers are referenced inside this source snippet. Conceptually, it is intended for use by higher-level scoring or graph-analysis utilities that need a simple metric of graph connectivity (for example, computing properties of keyboard adjacency graphs used in password-strength heuristics).

Why this logic is extracted:
- Encapsulates the single responsibility of computing a graph's average degree so callers do not duplicate the counting and division logic.
- Keeps neighbor-traversal semantics (counting truthy entries) centralized and consistent across the codebase.

## Args:
    graph (mapping): A mapping-like object (commonly a dict) whose keys are node identifiers and whose values are iterables (e.g., lists, tuples, sets) of neighbor entries.
        - Allowed values: any mapping where len(graph.items()) yields the number of nodes and iterating graph.items() yields (key, neighbors) pairs.
        - Neighbor entries are not type-constrained; however, only truthy neighbor entries are counted (i.e., items for which bool(item) is True).
        - Interdependencies: neighbors must be iterable. If a value is None or not iterable, a runtime error (TypeError) may occur when iterating.

## Returns:
    float: The arithmetic mean of per-node neighbor counts computed as
        (sum of counts of truthy neighbor entries for each node) / (number of nodes).
    - For a graph with N nodes and total counted neighbor entries M, the return value is M / N as a float.
    - Example possibilities:
        - Non-empty graph: returns a finite float >= 0.
        - If every node has zero truthy neighbors, returns 0.0.
        - Empty graph: the function does not handle this and will raise ZeroDivisionError (see Raises).

## Raises:
    ZeroDivisionError: If the provided graph mapping is empty (no items), the code attempts to divide by zero when computing the average.
    TypeError: If a value in the mapping is not iterable (e.g., None) and the function attempts to iterate it, a TypeError may be raised by the iterator protocol.
    Note: The function does not explicitly raise these; they are implicit runtime exceptions that can occur given invalid inputs.

## Constraints:
    Preconditions:
        - graph must be a mapping with a well-defined length (len(graph.items()) should be valid).
        - Each graph value must be iterable (e.g., list, tuple, set) or at least safely iterable; otherwise iteration will raise an exception.
    Postconditions:
        - If the function returns successfully, the result is a float representing M / N where M is the sum of truthy neighbor counts and N is the number of nodes (N >= 1).
        - The input mapping is not modified.

## Side Effects:
    - None: the function performs pure computation and does not perform I/O, mutate external/global state, write files, or call external services.

## Control Flow:
flowchart TD
    Start["Start: calc_average_degree(graph)"]
    CheckEmpty{"Is graph empty (len(graph.items()) == 0)?"}
    Loop["For each (key, neighbors) in graph.items():"]
    Count["Count truthy entries in neighbors (len([n for n in neighbors if n]))"]
    Sum["Add count to running total (average accumulator)"]
    Divide["Divide accumulator by float(len(graph.items()))"]
    Return["Return resulting float"]
    Start --> CheckEmpty
    CheckEmpty -- Yes --> Error["Division by zero will be raised (ZeroDivisionError)"]
    CheckEmpty -- No --> Loop
    Loop --> Count --> Sum
    Sum --> Loop
    Loop --> Divide --> Return

## Examples:
- Typical usage with a small adjacency mapping:
    graph = {'a': ['b', 'c'], 'b': ['a'], 'c': []}
    Result explanation: counts are [2, 1, 0] => sum = 3, nodes = 3 => return value = 1.0

- Handling falsy neighbor entries:
    graph = {'x': ['y', None, ''], 'y': [0, 'x']}
    Behavior: falsy entries None, '' and 0 are ignored when counting.
    Counts: node 'x' -> 1 (only 'y' is truthy), node 'y' -> 1 (only 'x' is truthy) => average = 1.0

- Empty graph (error handling):
    graph = {}
    Behavior: calling the function will raise ZeroDivisionError since the code divides by len(graph.items()) which is zero. Callers should check for empty graph before calling or handle ZeroDivisionError.

- Non-iterable neighbor value (invalid input):
    graph = {'a': None}
    Behavior: iterating neighbors will raise TypeError; callers are responsible for validating neighbor types beforehand.

## `zxcvbn.scoring.nCk` · *function*

## Summary:
Computes the binomial coefficient "n choose k" (number of k-sized combinations from n items) using an iterative multiplicative algorithm; returns 0 when k > n and 1 when k == 0.

## Description:
This small utility computes the combinatorial count C(n, k) by multiplying numerator terms and dividing by the running denominator to avoid computing large factorials directly. It is extracted as a dedicated function to encapsulate the combination logic (a reusable primitive needed by higher-level scoring/analysis routines that require combinatorial counts) and to centralize edge-case handling (k > n, k == 0).

Known callers within the scanned repository:
- No direct callers were discovered in the immediate scan of this module. Typical usage contexts (outside the scan) are scoring or combinatorics calculations where the number of ways to choose k items from n is required.

Why this is a separate function:
- Keeps combinatorics logic in one place so other scoring components can call a well-defined primitive.
- Avoids repeated implementations and makes future improvements (e.g., switching to an integer-safe algorithm or Python's built-in comb) localized.

## Args:
    n (int): Number of items (must be a non-negative integer for meaningful results). Represents the pool size.
    k (int): Number of items to choose (must be a non-negative integer). Represents the selection size.
Notes on arguments:
    - The implementation expects integer semantics. Passing non-integer numeric values is not supported and may produce unexpected results.
    - Common valid range: 0 <= k <= n. If k > n, the function returns 0 per the implementation.
    - Negative values are not handled intentionally; negative inputs may produce incorrect or surprising results.

## Returns:
    float or int:
    - Returns 0 (int) if k > n.
    - Returns 1 (int) if k == 0.
    - For 0 < k <= n, returns the multiplicative result of the binomial coefficient computation. Due to the implementation using true division, typical integer inputs produce a numeric value that is mathematically an integer but usually represented as a float (for example, 10.0 for C(5,3)). The return type can therefore be a float even when the mathematical result is an integer.

## Raises:
    This function does not explicitly raise exceptions in normal branches.
    - Passing non-numeric or non-orderable types (e.g., objects that do not support comparisons or numeric operations) may raise TypeError or other built-in exceptions from Python during comparisons or arithmetic; these are not handled in the function.
    - Extremely large n and k may lead to floating-point precision issues; no exception is raised for overflow, but results may be imprecise.

## Constraints:
Preconditions:
    - Caller should ensure n and k are integers (or at least integral numeric types) and non-negative when meaningful.
    - For semantically correct combinatorics, ensure 0 <= k <= n. The function handles k > n by returning 0.

Postconditions:
    - If k > n, return value equals 0.
    - If k == 0, return value equals 1.
    - For valid integer inputs with 0 < k <= n, return value equals the binomial coefficient C(n, k) up to floating-point representation and rounding; no global state is changed.

## Side Effects:
    - None. The function performs pure computation and does not perform I/O or mutate external/global state.

## Control Flow:
flowchart TD
    Start --> Check_k_gt_n
    Check_k_gt_n{Is k > n?}
    Check_k_gt_n -- Yes --> Return0[Return 0]
    Check_k_gt_n -- No --> Check_k_eq_0
    Check_k_eq_0{Is k == 0?}
    Check_k_eq_0 -- Yes --> Return1[Return 1]
    Check_k_eq_0 -- No --> InitLoop[Set r = 1; d = 1]
    InitLoop --> LoopCond
    LoopCond{d <= k?}
    LoopCond -- Yes --> MultiplyDivide[ r = r * n; r = r / d; n = n - 1; d = d + 1 ]
    MultiplyDivide --> LoopCond
    LoopCond -- No --> ReturnR[Return r]
    ReturnR --> End

## Examples:
- Typical uses:
    - nCk(5, 3) -> 10.0
    - nCk(6, 0) -> 1
    - nCk(3, 5) -> 0

- Error/edge handling:
    - If inputs are not integers:
        - nCk(5.5, 2) may run but results are not meaningful as a combinatorial count.
    - If negative values are passed:
        - nCk(-1, 0) returns 1 because the loop is skipped (this is a side-effect of the loop style and not intended behavior); callers should guard against negatives.

Implementation note (for reimplementers):
    - The algorithm iteratively multiplies r by descending n and divides by the loop index d to compute the binomial coefficient while reducing intermediate growth. To preserve exact integer results for large inputs, consider using integer arithmetic (multiplying and integer-dividing when appropriate) or Python's math.comb where available.

## `zxcvbn.scoring.most_guessable_match_sequence` · *function*

*No documentation generated.*

## `zxcvbn.scoring.estimate_guesses` · *function*

## Summary:
Estimate and normalize the number of guesses required to brute-force a single matched substring by dispatching to a pattern-specific estimator, enforcing a per-submatch minimum threshold, recording the numeric result and its base-10 log into the match mapping, and returning the final guesses as a Decimal.

## Description:
- Known callers within the repository snapshot:
    - No direct call-sites were found in the provided snapshot. In a typical password-strength scoring pipeline, this function is invoked for each match produced by pattern detectors (dictionary, spatial, regex, date, etc.) during the scoring stage that converts matches into numeric guess estimates.
- Typical pipeline stage:
    - For each match dictionary describing a substring of the password, estimate_guesses produces and records a per-submatch numeric estimate used later when aggregating full-password guesses.
- Responsibility boundary:
    - This function handles cross-cutting normalization around pattern-specific estimators:
        * short-circuit return when a precomputed guess exists and is truthy,
        * selection of a per-submatch minimum depending on token length vs. password length,
        * dispatch to the pattern-specific estimator,
        * writing standardized fields back into the match ('guesses' and 'guesses_log10'),
        * returning a Decimal-typed value for downstream code.
    - Pattern-specific numeric heuristics (combinatorics, rank-based multipliers, etc.) are delegated to estimator functions: bruteforce_guesses, dictionary_guesses, spatial_guesses, repeat_guesses, sequence_guesses, regex_guesses, date_guesses.

## Args:
    match (mapping-like, recommended: dict)
        - Must be a standard mapping (e.g., built-in dict) so the function can read and write keys.
        - Required keys (always):
            * 'pattern' (str): Which estimator to call. Allowed values: 'bruteforce', 'dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date'.
            * 'token' (sequence, typically str): The matched substring. Its length is used to decide minimum thresholds.
        - Optional/conditional keys:
            * 'guesses' (numeric-like): If present and truthy, function returns Decimal(match['guesses']) immediately (no mutation occurs). Note: a value of 0 is falsy and will NOT trigger the early-return; only truthy values short-circuit.
        - Pattern-specific required keys (the estimator invoked requires these; callers must supply them):
            * 'bruteforce' estimator: requires 'token' (length only).
            * 'dictionary' estimator: requires 'rank' (numeric). Common additional keys used by that estimator: 'token' (str), 'l33t' (bool), 'sub' (dict), 'reversed' (bool).
            * 'spatial' estimator: requires 'graph' (str), 'token' (str), 'turns' (int), 'shifted_count' (int).
            * 'repeat' estimator: requires 'base_guesses' (numeric) and 'repeat_count' (int or numeric-convertible).
            * 'sequence' estimator: requires 'token' (str) and 'ascending' (bool).
            * 'regex' estimator: requires 'regex_name' (str), 'token' (str), and for some regexes 'regex_match' (object with .group(0)).
            * 'date' estimator: requires 'year' (int); optional 'separator' (str) flags presence of separators.
        - Notes:
            * The function will mutate match by writing 'guesses' and 'guesses_log10' on success.
            * Estimators themselves may read and write additional keys on match (see their component docs).

    password (sequence, typically str)
        - The full password string; used only to compare len(match['token']) to len(password) when selecting minimum thresholds.

## Returns:
    Decimal
        - Always returns a Decimal constructed from the numeric value stored in match['guesses'] after applying the per-submatch minimum.
        - Behavior summary:
            1) If match.get('guesses', False) is truthy, return Decimal(match['guesses']) immediately (no mutation).
            2) Otherwise compute min_guesses:
                - Default min_guesses = 1
                - If len(match['token']) < len(password):
                    - If len(token) == 1 -> min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR
                    - Else -> min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR
            3) Call the estimator corresponding to match['pattern'] with the match mapping; let estimator_value be its return.
            4) Set match['guesses'] = max(estimator_value, min_guesses)
            5) Compute match['guesses_log10'] = log(match['guesses'], 10)  (math.log with base=10) — see "Type interactions" for exact conversion notes.
            6) Return Decimal(match['guesses'])
        - Possible numeric forms of estimator_value:
            * int, float, Decimal — the code accepts any numeric type, but care is needed when computing math.log and when constructing Decimal objects (see below).

## Raises:
    - KeyError:
        * If 'pattern' or 'token' are missing, subscripting raises KeyError.
        * If match['pattern'] is not one of the supported keys, the internal estimator lookup raises KeyError.
        * Estimators may raise KeyError if their own required keys are missing; those exceptions propagate.
    - TypeError / ValueError:
        * If len(match['token']) is invalid (e.g., match['token'] has no length), len() raises TypeError.
        * math.log(match['guesses'], 10) requires match['guesses'] to be a real-number type compatible with math.log (int or float). Passing a Decimal directly to math.log will typically raise TypeError. If a conversion to float is performed and the value is out of float range, math.log may raise OverflowError or ValueError.
        * Decimal(match['guesses']) will raise decimal.InvalidOperation if match['guesses'] is not convertible to Decimal.
        * If the estimator returns None or a non-numeric value, max(guesses, min_guesses) or log(...) will raise TypeError.
    - NameError:
        * If module-level constants MIN_SUBMATCH_GUESSES_SINGLE_CHAR or MIN_SUBMATCH_GUESSES_MULTI_CHAR are undefined, NameError occurs.
    - Any exception raised by the invoked estimator will propagate unchanged.

## Constraints:
- Preconditions:
    - match must be a mapping-like object (recommended: dict) and include at minimum 'pattern' and 'token'.
    - password must be sequence-like so len(password) is valid.
    - The estimator corresponding to match['pattern'] must be present in the local estimator mapping and must accept the match mapping.
    - Module-level constants MIN_SUBMATCH_GUESSES_SINGLE_CHAR and MIN_SUBMATCH_GUESSES_MULTI_CHAR must be defined.
- Postconditions:
    - On successful return:
        * match['guesses'] exists and equals the numeric max(estimator_value, min_guesses).
        * match['guesses_log10'] exists and equals math.log(match['guesses'], 10) (a float if math.log is used with float input).
        * The function returns Decimal(match['guesses']).
    - No other module-level globals or external state are mutated by this function.

## Type interactions and implementation notes:
- Early-return truthiness:
    - The function tests match.get('guesses', False). Only truthy values short-circuit. A zero (0) value is falsy and will NOT trigger the early-return; the estimator dispatch and min-threshold logic will proceed.
- math.log and Decimal:
    - math.log from the math module accepts floats (and ints). Passing a Decimal into math.log typically raises TypeError. To compute the log safely:
        * Option A (recommended): compute a float log: val = float(match['guesses']); match['guesses_log10'] = math.log(val, 10)
        * Option B: use Decimal-aware log if your environment provides it (Decimal.quantize + context-based log functions), but be aware decimal contexts and rounding behavior differ from math.log.
    - After computing match['guesses_log10'], the function returns Decimal(match['guesses']). Converting from float to Decimal can lose precision; prefer that estimators return integers or Decimals convertible to Decimal without intermediate float rounding, and perform the float conversion only for the log computation.
- Safe implementation pattern (pseudo-steps):
    1) estimator_value = estimator(match)
    2) chosen = max(estimator_value, min_guesses)
    3) match['guesses'] = chosen
    4) log_input = float(chosen)  # safe when chosen is int or float; Decimal -> float converts
    5) match['guesses_log10'] = math.log(log_input, 10)
    6) return Decimal(chosen)

## Side Effects:
- Mutates the provided match mapping by setting:
    * match['guesses'] (numeric)
    * match['guesses_log10'] (float)
- No I/O, no network calls, no database or file writes.
- Pattern estimators called by this function may also mutate match; that is part of their documented behavior.

## Control Flow:
flowchart TD
    Start([start]) --> HasGuesses{match.get('guesses', False)?}
    HasGuesses -- yes --> ReturnExisting[return Decimal(match['guesses'])]
    HasGuesses -- no --> InitMin[min_guesses = 1]
    InitMin --> TokenShort{len(match['token']) < len(password)?}
    TokenShort -- yes --> TokenLenIs1{len(match['token']) == 1?}
    TokenLenIs1 -- yes --> MinSingle[min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR]
    TokenLenIs1 -- no --> MinMulti[min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR]
    TokenShort -- no --> KeepMin[keep min_guesses = 1]
    MinSingle --> Dispatch
    MinMulti --> Dispatch
    KeepMin --> Dispatch
    Dispatch[Call estimator = estimation_functions[match['pattern']]] --> EstVal[guesses = estimator(match)]
    EstVal --> ApplyMin[match['guesses'] = max(guesses, min_guesses)]
    ApplyMin --> ComputeLog[match['guesses_log10'] = log(match['guesses'], 10)]
    ComputeLog --> ReturnDecimal[return Decimal(match['guesses'])]
    ReturnDecimal --> End([end])

## Examples:
1) Early-return when precomputed guesses exist (truthy):
    - match = {'pattern': 'any', 'token': 'x', 'guesses': 42}
    - password = 'x'
    - Behavior: function returns Decimal(42) immediately; no mutation occurs.

2) Note about zero guesses:
    - match = {'pattern': 'any', 'token': 'x', 'guesses': 0}
    - password = 'x'
    - Behavior: match.get('guesses', False) returns 0 (falsy), so the function will NOT short-circuit. It will proceed to compute min_guesses and call the estimator.

3) Dictionary pattern flow with safe log conversion:
    - match = {'pattern': 'dictionary', 'token': 'pass', 'rank': 50}
    - password = 'pass123'
    - Steps:
        * min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR (because 4 < 7)
        * calls dictionary_guesses(match) which returns a numeric estimate and typically writes additional keys
        * match['guesses'] = max(estimator_value, min_guesses)
        * match['guesses_log10'] = math.log(float(match['guesses']), 10)
        * return Decimal(match['guesses'])

4) Unknown pattern error:
    - match = {'pattern': 'unknown', 'token': 'a'}
    - Accessing the estimator mapping raises KeyError; callers must validate pattern or handle KeyError.

## `zxcvbn.scoring.bruteforce_guesses` · *function*

## Summary:
Estimate the number of pure brute-force guesses required for the given token by returning the greater of BRUTEFORCE_CARDINALITY ** token_length and a small, token-length-dependent minimum threshold.

## Description:
- Known callers (in provided repository snapshot):
    - No direct callers were found in the provided snapshot.
- Typical callers / usage context:
    - Used in password-strength scoring pipelines when a substring (match) cannot be categorized by a more specific matcher (dictionary, spatial, sequence, etc.) and the estimator must fall back to a brute-force guess count for that token.
    - Typical trigger: match objects classified with a "bruteforce" or "fallback" pattern are passed here to obtain a per-submatch guess estimate which will later be combined into a total guesses estimate for the full password.
- Why this logic is separated:
    - Centralizes the brute-force guess formula and the minimum-threshold policy in one place so tuning, testing, and consistent usage across the scoring pipeline are straightforward.

## Args:
    match (mapping): Required. A mapping-like object containing at least the key 'token'.
        - Required key:
            - 'token': a sequence (commonly a str) whose length (len(match['token'])) is used as the token length n.
        - Behavior on invalid input:
            - Missing 'token' raises KeyError.
            - If match['token'] does not support len(), a TypeError will be raised by len().
        - Interdependencies:
            - Only the length of match['token'] is used; token content is not inspected.

## Returns:
    int or Decimal or float: The computed guesses estimate. The exact numeric type depends on the numeric types of the module-level constants:
        - If BRUTEFORCE_CARDINALITY is an int and the minimum constants are ints, the result will be an int (Python int has arbitrary precision).
        - If BRUTEFORCE_CARDINALITY or either minimum constant is a Decimal, the result will be a Decimal (Decimal arithmetic preserves Decimal type).
        - If BRUTEFORCE_CARDINALITY is a float, the result may be a float (and subject to floating-point semantics).
    Concrete computation:
        - Let n = len(match['token']).
        - guesses = BRUTEFORCE_CARDINALITY ** n
        - min_guesses = (MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1) if n == 1 else (MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1)
        - Return max(guesses, min_guesses)
    Edge-case returns:
        - If n == 0, guesses == BRUTEFORCE_CARDINALITY ** 0 == 1 (for numeric BRUTEFORCE_CARDINALITY); min_guesses uses the multi-character branch, so the return will be max(1, MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1).
        - If BRUTEFORCE_CARDINALITY == 0: for n > 0, guesses == 0; for n == 0, guesses == 1 (0 ** 0 == 1 in Python integer arithmetic). The function will still return max(guesses, min_guesses).

## Raises:
    - KeyError: if 'token' is not present in the match mapping.
    - TypeError: if match['token'] does not support len() or the arithmetic operators used (e.g., BRUTEFORCE_CARDINALITY ** n) are not supported for the given types.
    - NameError: if any of BRUTEFORCE_CARDINALITY, MIN_SUBMATCH_GUESSES_SINGLE_CHAR, MIN_SUBMATCH_GUESSES_MULTI_CHAR are not defined at runtime in the module namespace.
    - ArithmeticError / OverflowError: may be raised by underlying numeric operations in non-integer numeric contexts (e.g., float overflow, Decimal invalid operations) depending on the runtime types and values of the constants. (These are not directly raised by this function's code but can propagate from Python numeric operations.)

## Constraints:
- Preconditions:
    - match must be mapping-like and contain 'token'.
    - len(match['token']) must be a non-negative integer (Python's len() returns a non-negative int for built-in sequences).
    - Module-level constants must be defined before calling:
        - BRUTEFORCE_CARDINALITY: numeric (preferably integer >= 1 for meaningful brute-force semantics; values <= 0 produce mathematically odd but well-defined numeric results).
        - MIN_SUBMATCH_GUESSES_SINGLE_CHAR: numeric (commonly integer >= 0).
        - MIN_SUBMATCH_GUESSES_MULTI_CHAR: numeric (commonly integer >= 0).
- Postconditions:
    - The returned value is >= min_guesses (the chosen threshold).
    - The returned value equals BRUTEFORCE_CARDINALITY ** n when that value is >= min_guesses; otherwise equals min_guesses.
    - No mutation of input match or any external state occurs.

## Side Effects:
- None observable: the function performs no I/O, writes, or external calls and does not mutate inputs.
- It does read module-level constants; if those are mutated elsewhere between calls, results will reflect the updated values.

## Control Flow:
flowchart TD
    Start([start]) --> GetLen[len = len(match['token'])]
    GetLen --> IsOne{len == 1?}
    IsOne -->|yes| MinSingle[ min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1 ]
    IsOne -->|no| MinMulti[ min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1 ]
    MinSingle --> Compute[ guesses = BRUTEFORCE_CARDINALITY ** len ]
    MinMulti --> Compute
    Compute --> Compare{guesses >= min_guesses?}
    Compare -->|yes| ReturnGuesses[return guesses]
    Compare -->|no| ReturnMin[return min_guesses]
    ReturnGuesses --> End([end])
    ReturnMin --> End

## Examples:
- Example 1 — integer constants (realistic, exact numeric result):
    - Suppose module constants are set as:
        - BRUTEFORCE_CARDINALITY = 10
        - MIN_SUBMATCH_GUESSES_SINGLE_CHAR = 1
        - MIN_SUBMATCH_GUESSES_MULTI_CHAR = 100
    - Call: bruteforce_guesses({'token': 'abc'})  # len == 3
        - guesses = 10 ** 3 = 1000
        - min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1 = 101
        - return value = max(1000, 101) = 1000
- Example 2 — single-character token:
    - With same constants, call: bruteforce_guesses({'token': 'x'})  # len == 1
        - guesses = 10 ** 1 = 10
        - min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1 = 2
        - return value = max(10, 2) = 10
- Error handling example:
    - Calling bruteforce_guesses({}) will raise KeyError because 'token' is missing; callers should validate matches or catch KeyError and handle it as an invalid/malformed match.
- Integration tip:
    - Ensure constants are defined (and of intended numeric types) early in module initialization. For consistent integer semantics prefer integer constants; if Decimal precision is desired, set BRUTEFORCE_CARDINALITY and minimums as Decimal instances and be aware the function will return Decimal results.

## `zxcvbn.scoring.dictionary_guesses` · *function*

## Summary:
Compute an estimated number of guesses for a dictionary-style match by combining the match's base rank with capitalization, l33t (substitution), and reversed-token variation multipliers.

## Description:
This function is part of the scoring stage that converts a detected dictionary match into a numeric guess-count estimate. It is intended to be called by password-scoring/ranking code when evaluating a match object produced by the matching/parsing stage. No direct callers were discovered in the scanned repository; conceptually it is invoked whenever a match represents a dictionary word (including reversed matches) and the scoreer needs a combined guess estimate.

The function delegates capitalization-variation and l33t-substitution counting to the helper functions uppercase_variations(match) and l33t_variations(match) respectively; these are extracted to keep combinatorial logic separate and testable. This function's responsibility is to combine those multiplicative factors with the base rank and the reversed-token multiplier into a single guess estimate, and to record the computed factors back into the match object for later use or inspection.

## Args:
    match (dict-like):
        - Required keys accessed directly by this function:
            * 'rank' (int or numeric-like): the base rank/guess-count for the matched dictionary word (must be present).
        - Implicit/indirect requirements (required by delegated helpers):
            * 'token' (str): required by uppercase_variations (and often by l33t_variations when 'l33t' is True).
            * 'l33t' (bool) and 'sub' (dict): required by l33t_variations when substitutions are present.
            * 'reversed' (bool, optional): indicates whether the match was found in reversed order; a truthy value doubles the variation multiplier.
        - Notes:
            * The function treats match as a mutable mapping and writes computed fields into it.
            * Types: caller should pass a standard mapping (e.g., dict). Numeric arithmetic will use the numeric types returned by helpers; helpers may return ints or floats.

## Returns:
    numeric (int or float):
        - The product: match['rank'] * uppercase_variations(match) * l33t_variations(match) * reversed_variations
        - reversed_variations is 2 when match.get('reversed', False) is truthy, otherwise 1.
        - Possible outcomes and edge cases:
            * Typical positive integer-like values when inputs are valid.
            * The numeric type may be float if helper functions (notably nCk used by the helpers) return float values for combinatorial counts (e.g., 10.0).
            * If any factor is zero (rare — e.g., uppercase_variations may return 0 in an unusual token case), the product will be zero.
        - The function does not round or coerce the result; it returns the raw numeric product.

## Raises:
    - KeyError:
        * If match does not contain the 'rank' key, a KeyError is raised when the function tries to read match['rank'].
        * Helper functions may raise KeyError if required keys (for example 'token' or 'sub') are missing when those helpers are invoked; those exceptions propagate.
    - TypeError / AttributeError:
        * If match is not mapping-like or helper functions are called with malformed values (e.g., match['token'] not a string), underlying operations may raise TypeError or AttributeError; these propagate.
    - Any exception raised by uppercase_variations or l33t_variations will propagate unchanged.

## Constraints:
Preconditions:
    - match must be a mutable mapping containing at least the 'rank' key with a numeric value.
    - If the match describes capitalization or l33t details, it must include the keys expected by uppercase_variations and l33t_variations (see those functions' documentation): typically 'token' (str), and when l33t is present, 'l33t' (truthy) and 'sub' (mapping).
    - No external I/O is required; all computation is in-memory.

Postconditions:
    - The match mapping is mutated to include the following keys with the computed values:
        * 'base_guesses' (numeric) — copied from match['rank']
        * 'uppercase_variations' (numeric) — value returned by uppercase_variations(match)
        * 'l33t_variations' (numeric) — value returned by l33t_variations(match)
    - The return value is equal to the product of these three computed values with the reversed multiplier (2 or 1).
    - No other global state or external resources are modified.

## Side Effects:
    - Mutation of the input match mapping: writes 'base_guesses', 'uppercase_variations', and 'l33t_variations'.
    - No file, network, stdout/stderr I/O, or external service calls are made.

## Control Flow:
flowchart TD
    Start --> ReadRank[Read base rank = match['rank']]
    ReadRank --> SetBase[Set match['base_guesses'] = rank]
    SetBase --> Upper[Call uppercase_variations(match)]
    Upper --> SetUpper[Set match['uppercase_variations'] = <result>]
    SetUpper --> L33T[Call l33t_variations(match)]
    L33T --> SetL33T[Set match['l33t_variations'] = <result>]
    SetL33T --> CheckReversed{match.get('reversed', False) ?}
    CheckReversed -- True --> Rev2[reversed_variations = 2]
    CheckReversed -- False --> Rev1[reversed_variations = 1]
    Rev2 --> ComputeProduct
    Rev1 --> ComputeProduct[Compute product = base_guesses * uppercase_variations * l33t_variations * reversed_variations]
    ComputeProduct --> Return[Return product]
    Return --> End

## Examples:
1) Basic dictionary match without l33t or reversal:
    Input:
        match = {'token': 'pAsS', 'rank': 10, 'l33t': False}
    Behaviour:
        uppercase_variations(match) -> 10 (example from uppercase_variations logic)
        l33t_variations(match) -> 1
        reversed_variations -> 1
        match is mutated with base_guesses=10, uppercase_variations=10, l33t_variations=1
    Return:
        10 * 10 * 1 * 1 = 100

2) Dictionary match with l33t substitutions and reversed token:
    Input:
        match = {'token': 'p@ss', 'rank': 50, 'l33t': True, 'sub': {'@': 'a'}, 'reversed': True}
    Behaviour (illustrative):
        uppercase_variations(match) -> 1
        l33t_variations(match) -> 2   (for example, if '@' -> 'a' yields 2 possibilities)
        reversed_variations -> 2
        match is mutated with computed fields
    Return:
        50 * 1 * 2 * 2 = 200

3) Error case — missing rank:
    Input:
        match = {'token': 'password'}
    Behaviour:
        Attempting to read match['rank'] raises KeyError immediately. No mutations occur.

Usage note:
    - Callers should treat the returned numeric as an estimate of the search-space size (a multiplicative guess-count). If an integer type is required downstream, convert/round explicitly; helper combinatorics may return float representations of integer counts.
    - Because this function mutates the match object, callers that must preserve the original match dict should pass a copy.

## `zxcvbn.scoring.repeat_guesses` · *function*

## Summary:
Computes the estimated number of guesses for a repeated match by multiplying the base guess estimate by the repeat count and returning the result as a Decimal.

## Description:
This function accepts a match descriptor (a mapping) that must include an estimate for the non-repeated pattern ('base_guesses') and the number of repetitions ('repeat_count'). It returns the product base_guesses * repeat_count expressed as a Decimal.

Known callers within the provided code context:
- No explicit call sites were available in the provided context. In typical usage within a password-strength scoring pipeline, this function is called during the scoring stage that converts a parsed "repeat" match (a substring repeated multiple times) into a guess-count estimate. It is intentionally extracted to encapsulate the logic for scaling an individual match's base guess estimate by its repetition count so that the higher-level scoring pipeline can remain agnostic about the arithmetic details.

Reason for separation:
- Encapsulates the single responsibility of converting a repeat-match descriptor into a numeric guess estimate, keeping conversion and multiplication logic in one place and enabling reuse, testing, and clearer call sites in the scoring pipeline.

## Args:
    match (dict): Required. A mapping containing at least the following keys:
        - 'base_guesses' (Decimal | int | other numeric-like): An estimate of how many guesses would be required for a single occurrence of the matched pattern (the "base" pattern). Preferably a Decimal or integer; using a float or other non-Decimal numeric may raise type errors at multiplication time.
        - 'repeat_count' (int | str | Decimal): The number of times the base pattern repeats. Can be an integer, a numeric string, or a Decimal-like value that Decimal(...) can accept.

    Notes on interdependencies:
        - Both keys must be present. The function multiplies match['base_guesses'] by Decimal(match['repeat_count']). The result's behavior depends on the types/properties of both values:
            * When 'base_guesses' is a Decimal or an int, multiplication with Decimal(...) yields a Decimal result.
            * If 'base_guesses' is a float or other unsupported type, multiplication may raise TypeError.
            * If 'repeat_count' is not convertible to Decimal (e.g., a non-numeric string), Decimal(...) will raise a decimal.InvalidOperation or related conversion error.

## Returns:
    Decimal: The computed guess estimate for the repeated match, equal to match['base_guesses'] * Decimal(match['repeat_count']).

    Possible return-value scenarios:
        - A Decimal strictly representing the mathematical product when inputs are valid (e.g., Decimal('1000') * Decimal(3) => Decimal('3000')).
        - If 'base_guesses' is zero or 'repeat_count' is zero (and convertible), the function returns Decimal('0') (or equivalent Decimal zero) because standard numeric multiplication rules apply.

## Raises:
    - KeyError: If the 'base_guesses' or 'repeat_count' key is missing from the match mapping. The code directly indexes the mapping and does not perform a presence check.
    - decimal.InvalidOperation (or a Decimal conversion error): If Decimal(match['repeat_count']) cannot convert the provided repeat_count value (for example, a non-numeric string). This exception originates from the Decimal constructor in the decimal module.
    - TypeError: If match['base_guesses'] is of a type that cannot be multiplied with a Decimal (for example, certain floats or custom types that do not cooperate with Decimal math). Multiplication of incompatible operand types may raise TypeError.

## Constraints:
    Preconditions:
        - The caller must pass a mapping object with the keys 'base_guesses' and 'repeat_count'.
        - 'repeat_count' must be a value convertible to Decimal (int, numeric string, Decimal, etc.) to avoid conversion errors.
        - Prefer passing 'base_guesses' as a Decimal or integer to ensure predictable Decimal arithmetic (avoid floats where possible).

    Postconditions:
        - On successful return, a Decimal representing the scaled guess estimate is produced.
        - No mutation of the input mapping occurs; the function has no side effects on the provided match mapping.

## Side Effects:
    - None. The function performs pure arithmetic and dictionary reads only. There are no I/O operations, no global state changes, no network calls, and no file or database access.

## Control Flow:
flowchart TD
    A([Start]) --> B{match has 'base_guesses' and 'repeat_count'?}
    B -- No --> C[Raise KeyError]
    B -- Yes --> D[Compute Decimal(match['repeat_count'])]
    D --> E{Decimal conversion succeeded?}
    E -- No --> F[Raise decimal.InvalidOperation / conversion error]
    E -- Yes --> G[Compute product = match['base_guesses'] * Decimal(repeat_count)]
    G --> H{Multiplication succeeded?}
    H -- No --> I[Raise TypeError or other arithmetic error]
    H -- Yes --> J[Return product (Decimal)]

## Examples:
- Typical successful usage (described):
    A match for a repeated substring might include base_guesses = Decimal('1200') and repeat_count = 3. The function returns Decimal('3600') as the estimated number of guesses required to cover the repeated pattern.

- When base_guesses is an integer:
    If base_guesses = 1200 (int) and repeat_count = '3' (string), Decimal('3') will convert and the function returns Decimal('3600').

- Error handling guidance:
    Callers that may receive untrusted or malformed match dictionaries should guard calls with try/except blocks catching KeyError and decimal.InvalidOperation (or a general Exception if broader handling is desired). Also validating or normalizing input types before calling (e.g., ensuring base_guesses is Decimal or int, and repeat_count is an int or numeric string) will make outcomes predictable.

## `zxcvbn.scoring.sequence_guesses` · *function*

## Summary:
Estimate the number of guesses for a detected sequential substring by returning a small integer proportional to the sequence character-space and the token length.

## Description:
This function computes a simple guess-count estimate for a "sequence" match (e.g., 'abcd', '4321', 'mnop'). It derives a per-character base guess count from the sequence's first character, optionally doubles that base for descending sequences, and multiplies by the token length.

Known callers:
- No callers were present in the provided source snapshot. In typical password-strength pipelines, this function is used by a sequence matcher component that detects sequential runs and needs an estimated guess count for scoring.

Reason for extraction:
- The logic is a small, self-contained heuristic that maps a match dictionary to a numeric guess estimate. Extracting it isolates sequence-specific heuristics (character-space selection, ascending/descending handling, and length-scaling) from higher-level scoring code so those details are easy to test and adjust without changing match-detection or score-aggregation code.

## Args:
    match (dict): A mapping describing a detected sequence. Required keys:
        - token (str): The matched substring. Must be a string (or other object supporting slicing and len()).
        - ascending (bool): True if the characters in token are in ascending order, False otherwise.

    Notes on argument behavior:
        - The function reads only match['token'] and match['ascending']; missing either key will raise KeyError.
        - match['token'] may be an empty string; slicing is handled and the function will return 0 in that case.
        - The function does not mutate the provided dict.

## Returns:
    int: A non-negative integer representing the estimated number of guesses for the matched sequence.

    Possible return values and edge cases:
        - If token is empty (''), the function returns 0.
        - For non-empty tokens, the return is base_guesses * len(token) where base_guesses is one of:
            * 4  — when the first character is one of ['a','A','z','Z','0','1','9']
            * 10 — when the first character is a digit (0–9) and not in the special list above
            * 26 — when the first character is a non-digit and not in the special list above
          If ascending is False, base_guesses is doubled before multiplication.
        - The returned value is an integer (Python int).

## Raises:
    KeyError: If match does not contain the 'token' or 'ascending' keys (e.g., match['token'] or match['ascending'] access fails).
    TypeError: If match['token'] is None or an object that does not support slicing or len() operations in the expected way (e.g., non-subscriptable types).
    (No other exceptions are raised by the function itself in normal operation.)

## Constraints:
    Preconditions:
        - match must be a dict-like object containing the keys 'token' and 'ascending'.
        - match['token'] should be a string (or string-like) so slicing and len() behave as expected.
        - match['ascending'] should be a boolean (truthy/falsy values work, but non-boolean values may change semantics).

    Postconditions:
        - The function returns an integer equal to (adjusted_base_guesses * token_length).
        - The function has no side effects — it does not modify match or any external state.

## Side Effects:
    - None. The function performs no I/O and does not modify any global state or external systems.

## Control Flow:
flowchart TD
    Start --> Read_first_char[Get first_chr = match['token'][:1]]
    Read_first_char --> Is_special?[first_chr in ['a','A','z','Z','0','1','9']?]
    Is_special? -- Yes --> base4[base_guesses = 4]
    Is_special? -- No --> Is_digit?[re.compile(r'\d').match(first_chr)?]
    Is_digit? -- Yes --> base10[base_guesses = 10]
    Is_digit? -- No --> base26[base_guesses = 26]
    base4 --> Ascending?[match['ascending'] is True?]
    base10 --> Ascending?
    base26 --> Ascending?
    Ascending? -- No --> double[base_guesses *= 2]
    Ascending? -- Yes --> skip_double[no change]
    double --> Multiply[return base_guesses * len(match['token'])]
    skip_double --> Multiply

## Examples:
Example 1 — ascending alphabetical sequence:
    Input: match = {'token': 'abcd', 'ascending': True}
    Calculation steps:
        first_chr = 'a' -> special branch -> base_guesses = 4
        ascending True -> base_guesses remains 4
        result = 4 * len('abcd') = 16
    Return: 16

Example 2 — descending numeric sequence:
    Input: match = {'token': '4321', 'ascending': False}
    Calculation steps:
        first_chr = '4' -> digit branch -> base_guesses = 10
        ascending False -> base_guesses = 10 * 2 = 20
        result = 20 * len('4321') = 80
    Return: 80

Example 3 — edge cases:
    - Empty token:
        Input: {'token': '', 'ascending': True}
        Behavior: first_chr == '' -> not special, not digit -> base_guesses = 26
                  result = 26 * 0 = 0
        Return: 0

    - Missing keys:
        Input: {'token': 'abc'}  (no 'ascending')
        Behavior: Accessing match['ascending'] raises KeyError.
        Recommended usage: Validate presence of required keys before calling or catch KeyError.

    - Defensive call pattern:
        try:
            g = sequence_guesses(match)
        except KeyError as e:
            # handle malformed match dict
            pass

## `zxcvbn.scoring.regex_guesses` · *function*

## Summary:
Compute an estimated guess-count for a password token that matched a regex rule by mapping character-class and recent-year matches to an attack-space size (integer guesses).

## Description:
This function converts a regex-based match object (as produced by the password-matching stage) into an integer estimate of how many guesses an attacker would need to brute-force that token.

Known callers:
- No explicit call sites were provided with the source snippet. In the expected codebase layout, this function is called by the regex-match scoring stage (the part of the scoring pipeline that iterates through regex matches and converts each match into a guess estimate). If you search the repository, look for code that handles regex-match dictionaries or a regex-based matching pipeline; that code should call this function for each regex match.

Why this is a separate function:
- Responsibility separation: it encapsulates the logic that maps regex match types (character classes and recent-year matches) to numeric guess estimates. Keeping it separate makes the regex-to-guesses mapping testable, reusable, and easy to update independently from the higher-level matching and scoring pipeline.

## Args:
    match (dict): A dictionary describing a regex match. Required keys:
        - 'regex_name' (str): The semantic name of the regex that matched (e.g., 'digits', 'alpha_lower', 'recent_year'). Controls which calculation branch is used.
        - 'token' (str): The substring from the password that matched the regex. Used for length-based exponentiation for character-class regexes.
        - 'regex_match' (re.Match or similar): The underlying regex match object (only used for some regex_name values like 'recent_year'); its .group(0) must return the matched text for numeric parsing.

    Types and constraints:
        - match must be a mapping-like object (typically dict). Missing keys raise KeyError.
        - 'regex_name' must be a string.
        - 'token' must be a string (can be empty; behavior described below).
        - 'regex_match' must provide .group(0) when required (AttributeError otherwise).

## Returns:
    int or None:
        - For character-class regexes (one of 'alpha_lower', 'alpha_upper', 'alpha', 'alphanumeric', 'digits', 'symbols'):
            returns base ** length where:
              base = { 'alpha_lower':26, 'alpha_upper':26, 'alpha':52, 'alphanumeric':62, 'digits':10, 'symbols':33 }
              length = len(match['token'])
            This is an integer >= 1 for token lengths >= 1; for empty token returns 1 (base ** 0 == 1).
        - For 'recent_year':
            returns an integer year_space computed as:
              year_space = abs(int(match['regex_match'].group(0)) - REFERENCE_YEAR)
              year_space = max(year_space, MIN_YEAR_SPACE)
            This returns at least MIN_YEAR_SPACE (an integer) and is otherwise the absolute difference between matched year and REFERENCE_YEAR.
        - For any other 'regex_name' value:
            returns None (no mapping defined for that regex name).

    Notes on types:
        - Return values are Python ints (arbitrary precision).
        - The function does not return floats or Decimals.

## Raises:
    The function does not explicitly raise custom exceptions, but the following built-in exceptions can occur:
        - KeyError: if 'regex_name' or 'token' (or 'regex_match' when used) are not present in the match dict.
        - AttributeError: if 'regex_match' is provided but does not have a .group method (or .group(0) is invalid).
        - ValueError: when converting match['regex_match'].group(0) to int fails in the 'recent_year' branch (e.g., matched text is non-numeric).
        - TypeError: if match is None or not subscriptable like a dict.

    Implementations should either ensure valid input or catch/handle these exceptions upstream.

## Constraints:
Preconditions:
    - Module-level integer constants REFERENCE_YEAR and MIN_YEAR_SPACE must be defined in the same module (or imported) before calling this function:
        - REFERENCE_YEAR (int): the baseline year used to compute year distance.
        - MIN_YEAR_SPACE (int): the minimum year-space to use when the difference is very small or zero.
    - match must contain the required keys and types (see Args).
    - For 'recent_year', match['regex_match'].group(0) must yield a string representing an integer year (e.g., '1999').

Postconditions:
    - Function returns an integer estimate for known regex_name cases, or None for unknown regex_name.
    - No global state is modified by this function.

## Side Effects:
    - None. The function performs pure computation based only on the provided match dict and module-level constants.
    - No I/O, no network calls, no mutation of global variables, and no external service interactions.

## Control Flow:
flowchart TD
    Start --> CheckRegexName
    CheckRegexName -->|regex_name in char_class_bases| CharClassBranch
    CheckRegexName -->|regex_name == recent_year| RecentYearBranch
    CheckRegexName -->|other| ReturnNone
    CharClassBranch --> ComputeBaseAndLen
    ComputeBaseAndLen --> ComputeExponentiation
    ComputeExponentiation --> ReturnInt
    RecentYearBranch --> ParseGroup0ToInt
    ParseGroup0ToInt --> ComputeAbsDiff
    ComputeAbsDiff --> MaxWithMinYearSpace
    MaxWithMinYearSpace --> ReturnInt

## Examples:
Example 1 — character-class match (digits):
    # Prerequisite: define constants in the module
    REFERENCE_YEAR = 2023
    MIN_YEAR_SPACE = 50

    match = {
        'regex_name': 'digits',
        'token': '1234',
        'regex_match': None  # not used for this regex_name
    }
    # Result: base for 'digits' is 10, length is 4 => 10**4 == 10000
    guesses = regex_guesses(match)  # returns 10000

Example 2 — recent-year match with small difference:
    REFERENCE_YEAR = 2023
    MIN_YEAR_SPACE = 50

    # Use a real re.Match object (or any object with .group(0))
    import re
    m = re.match(r'\d{4}', '2018')
    match = {
        'regex_name': 'recent_year',
        'token': '2018',
        'regex_match': m
    }
    # year_space = abs(2018 - 2023) = 5 -> max(5, 50) => 50
    guesses = regex_guesses(match)  # returns 50

Example 3 — error handling when year is non-numeric:
    REFERENCE_YEAR = 2023
    MIN_YEAR_SPACE = 50

    import re
    m = re.match(r'.+', 'abcd')  # group(0) is 'abcd'
    match = {
        'regex_name': 'recent_year',
        'token': 'abcd',
        'regex_match': m
    }
    try:
        guesses = regex_guesses(match)
    except ValueError:
        # Handle invalid year string
        guesses = MIN_YEAR_SPACE

Implementation notes for reimplementers:
    - Use integer arithmetic for the exponentiation; Python's ints are arbitrary-precision.
    - Ensure REFERENCE_YEAR and MIN_YEAR_SPACE are integers and set to reasonable values for your application domain.
    - Be explicit that unknown regex names return None so the caller can decide to ignore or handle them.

## `zxcvbn.scoring.date_guesses` · *function*

## Summary:
Estimates the number of brute-force guesses required to enumerate a date token by converting the year distance to days and scaling for optional separators.

## Description:
This function consumes a normalized date-match dictionary (typically produced by the date matcher) and converts that match into a numeric guess count used by the scoring pipeline. It computes a year-based search "space" (distance from a reference year, floored by a minimum span), converts that span to days, and multiplies by an extra factor when the matched token contained a separator character (e.g., '/', '-', '.'). 

Known callers:
- No direct callers were discovered in the scanned snapshot. Intended usage: called by the scoring component of the password-strength pipeline when computing guess estimates for matches produced by the date matcher (for example, a match returned by matching.date_match).

Why this is a separate function:
- Translating a normalized date match into an estimated guess count is a concise, well-defined responsibility that depends on module-level constants (REFERENCE_YEAR, MIN_YEAR_SPACE) and the normalized match shape. Extracting it isolates the numeric estimation logic from pattern-detection code and makes it easier to test or adjust the estimation heuristic independently.

## Args:
    match (dict):
        - Required keys:
            - 'year' (int): canonical, normalized year (expected as a four-digit integer after normalization).
        - Optional keys:
            - 'separator' (str): either '' (empty string) for contiguous-digit matches or the single separator character captured by the matcher (e.g., '/', '-', '.', ' ', etc.). The function treats any truthy separator value as indicating a separator was present.
        - Other keys in the dict are ignored by this function.
        - Interdependencies: 'year' must be numeric (supporting subtraction with REFERENCE_YEAR). The meaning of 'year' should follow the normalization rules applied by the date matcher (e.g., two-digit → four-digit normalization).

## Returns:
    int
        - The estimated number of guesses for the date token.
        - Computation summary:
            1) year_space = max(abs(match['year'] - REFERENCE_YEAR), MIN_YEAR_SPACE)
            2) guesses = year_space * 365
            3) if match.get('separator', False) is truthy: guesses *= 4
        - Possible/edge-case return values:
            - If match['year'] equals REFERENCE_YEAR and MIN_YEAR_SPACE is 0, year_space could be 0 and guesses 0 — in practice MIN_YEAR_SPACE should be a positive integer to avoid zero guesses.
            - Minimum returned value is MIN_YEAR_SPACE * 365 (or that times 4 if separator is present).
            - Return is an integer (product of integer operands when module constants are integers); if module constants are non-integer numerics, the returned value will be numeric consistent with Python multiplication (but callers expect an integral guess count).

## Raises:
    KeyError:
        - If the provided match dict does not contain the 'year' key, a KeyError will be raised when accessing match['year'].
    NameError:
        - If the module-level constants REFERENCE_YEAR or MIN_YEAR_SPACE are not defined in the scoring module namespace, a NameError will be raised at runtime.
    TypeError:
        - If match['year'] or REFERENCE_YEAR are not types that support numeric subtraction (for example, None or a non-numeric string), a TypeError may be raised during arithmetic.
    Any exception raised by evaluating match.get('separator', False) or by arithmetic operations will propagate.

## Constraints:
Preconditions:
    - Module-level constants must exist and be numeric:
        - REFERENCE_YEAR must be defined (int-like) and represent the anchor year used to measure temporal distance.
        - MIN_YEAR_SPACE must be defined (non-negative int-like) and represent the minimum number of years to consider when estimating guesses.
    - match must be a mapping (dict-like) and contain a numeric 'year' value (normalized to canonical form).
    - The caller should ensure normalization of 'year' (e.g., two-digit years converted to four-digit) before calling.

Postconditions:
    - Returns a numeric guess estimate computed as described in Returns.
    - The function does not mutate the input match dict.

## Side Effects:
    - None. The function performs pure computation and has no I/O, network activity, global state mutation, or caching. Side effects from external or missing module-level names (e.g., raising NameError) are not performed intentionally by this function.

## Control Flow:
flowchart TD
    Start --> CheckYearKey{match contains 'year'?}
    CheckYearKey -- no --> RaiseKeyError[Raise KeyError]
    CheckYearKey -- yes --> ComputeDiff[diff = abs(match['year'] - REFERENCE_YEAR)]
    ComputeDiff --> ApplyMin[max(diff, MIN_YEAR_SPACE) -> year_space]
    ApplyMin --> MultiplyDays[guesses = year_space * 365]
    MultiplyDays --> CheckSeparator{match.get('separator', False) truthy?}
    CheckSeparator -- yes --> MultiplyBy4[guesses = guesses * 4]
    CheckSeparator -- no --> NoSeparator[do not adjust]
    MultiplyBy4 --> Return[return guesses]
    NoSeparator --> Return

## Examples (illustrative):
Note: the numeric examples below assume illustrative module-constant values. Replace these with the actual values defined in the scoring module when reproducing results.

Example A — contiguous-digit date:
    - Assumed constants: REFERENCE_YEAR = 2016, MIN_YEAR_SPACE = 10
    - Input match: {'year': 2000, 'separator': ''}
    - Computation:
        year_space = max(abs(2000 - 2016) = 16, 10) -> 16
        guesses = 16 * 365 -> 5840
        separator is falsy (''), so final guesses = 5840
    - Return: 5840

Example B — separator date:
    - Assumed constants: REFERENCE_YEAR = 2016, MIN_YEAR_SPACE = 10
    - Input match: {'year': 1985, 'separator': '/'}
    - Computation:
        year_space = max(abs(1985 - 2016) = 31, 10) -> 31
        guesses = 31 * 365 -> 11315
        separator is truthy ('/'), so guesses *= 4 -> 45260
    - Return: 45260

Example C — edge case when year equals reference and MIN_YEAR_SPACE enforces floor:
    - Assumed constants: REFERENCE_YEAR = 2016, MIN_YEAR_SPACE = 20
    - Input match: {'year': 2016, 'separator': ''}
    - Computation:
        year_space = max(0, 20) -> 20
        guesses = 20 * 365 -> 7300
    - Return: 7300

## `zxcvbn.scoring.spatial_guesses` · *function*

## Summary:
Estimates the number of guesses required to brute-force a spatial adjacency match (keyboard or keypad) by summing combinatorial possibilities over start positions, turn counts, branching degree, and shift-placement variations; returns the numeric search-space size for that match.

## Description:
This function quantifies the brute-force search space for a spatial pattern detected by the spatial matcher (a contiguous walk on an adjacency graph such as QWERTY or a keypad). It enumerates all substrings lengths, feasible numbers of turns for each length, starting-key choices, and average branching at turns, then adjusts for character shift-placement permutations when applicable.

Known callers within the codebase:
- Typically invoked by the scoring/entropy stage immediately after the spatial matcher produces a match dictionary (match dictionaries with keys 'graph', 'token', 'turns', and 'shifted_count'). There were no direct call-sites discovered in the scanned metadata, but this function is intended to be used as part of the overall password scoring pipeline.

Why this is a separate function:
- Encapsulates the domain-specific combinatoric estimation for spatial patterns so higher-level scoring code can remain agnostic to adjacency-graph details and shift-handling logic. Centralizing the logic simplifies testing and future updates (for example, changing constants or using an exact combinatorics implementation).

## Args:
    match (dict): Required keys and expected types:
        - 'graph' (str): Name of adjacency graph ('qwerty', 'dvorak', or other graph names). Determines whether keyboard or keypad constants are used.
        - 'token' (str): The matched character sequence. len(token) is denoted L.
        - 'turns' (int): Number of turns observed in the walk (non-negative integer). Denoted t.
        - 'shifted_count' (int): Number of shifted characters in token (0 <= shifted_count <= L). When zero, shift-handling logic is skipped.
    Interdependencies:
        - shifted_count must be <= len(token) for meaningful results; otherwise U (unshifted count) becomes negative and combinatorics are invalid.
        - The function relies on module-level constants and helper nCk (binomial) function described elsewhere.

## Returns:
    int or float:
    - A numeric estimate of the number of guesses (>= 0). The implementation may produce a float because the combinatorics helper nCk can return float in the existing implementation; the mathematical value is an integer but the runtime type may be float.
    - Possible outcomes:
        * 0 if L < 2 or if combinatorics sum yields zero (no feasible patterns).
        * Positive numeric estimate otherwise.
    - The function never returns negative values.

## Raises:
    - KeyError: if any required key ('graph', 'token', 'turns', 'shifted_count') is missing from match.
    - TypeError / ValueError: may be raised implicitly if values have incorrect types (e.g., token without length, non-integer turns/shifted_count, negative shifted_count making combinations invalid).
    - Exceptions raised by referenced helpers/constants (for example, nCk) propagate upward.

## Constraints:
Preconditions:
    - match must be a dict-like object containing the required keys with these types:
        * 'graph': str
        * 'token': a sized sequence (typically str)
        * 'turns': int >= 0
        * 'shifted_count': int, 0 <= shifted_count <= len(token)
    - Module-level constants must be defined:
        * KEYBOARD_STARTING_POSITIONS (int)
        * KEYBOARD_AVERAGE_DEGREE (number)
        * KEYPAD_STARTING_POSITIONS (int)
        * KEYPAD_AVERAGE_DEGREE (number)
    - Helper function nCk(n, k) available and defined to return 0 when k > n and the binomial coefficient otherwise.

Postconditions:
    - Returns a non-negative numeric estimate.
    - Does not mutate the input match or module-level globals.

## Side Effects:
    - None. Pure computation; no I/O or external state mutations.

## Control Flow:
flowchart TD
    Start --> DetermineGraphType
    DetermineGraphType{graph in ['qwerty','dvorak']?}
    DetermineGraphType -- Yes --> UseKeyboardConstants[Set s=KEYBOARD_STARTING_POSITIONS; d=KEYBOARD_AVERAGE_DEGREE]
    DetermineGraphType -- No --> UseKeypadConstants[Set s=KEYPAD_STARTING_POSITIONS; d=KEYPAD_AVERAGE_DEGREE]
    UseKeyboardConstants --> Init[guesses = 0; L=len(token); t=turns]
    UseKeypadConstants --> Init
    Init --> For_i[for i in 2 .. L (inclusive)]
    For_i --> Compute_possible_turns[possible_turns = min(t, i - 1) + 1]
    Compute_possible_turns --> For_j[for j in 1 .. possible_turns-1]
    For_j --> Add_term[guesses += nCk(i - 1, j - 1) * s * d**j]
    Add_term --> For_j
    For_j --> For_i_end
    For_i_end --> Shift_check{shifted_count > 0?}
    Shift_check -- No --> Return[return guesses]
    Shift_check -- Yes --> Compute_S_U[S=shifted_count; U=L - S]
    Compute_S_U --> All_same{U == 0?}
    All_same -- Yes --> Multiply2[guesses *= 2] --> Return
    All_same -- No --> Sum_shifted[shifted_variations = sum_{k=1..min(S,U)} nCk(S+U, k)]
    Sum_shifted --> MultiplyShift[guesses *= shifted_variations] --> Return

## Detailed logic and notes for reimplementation:
1. Constant selection:
    - If match['graph'] equals 'qwerty' or 'dvorak', set:
        s = KEYBOARD_STARTING_POSITIONS
        d = KEYBOARD_AVERAGE_DEGREE
      Else:
        s = KEYPAD_STARTING_POSITIONS
        d = KEYPAD_AVERAGE_DEGREE
2. Base combinatorics:
    - Initialize guesses = 0.
    - Let L = len(match['token']); let t = match['turns'].
    - For i in range(2, L + 1):  # i enumerates substring lengths from 2 up to L inclusive
        * possible_turns = min(t, i - 1) + 1
          (possible_turns is an upper bound for the loop variable j; code iterates j from 1 up to possible_turns-1 inclusive)
        * For j in range(1, possible_turns):  # j is the number of turns considered (>=1)
            - Add term: nCk(i - 1, j - 1) * s * (d ** j)
              Explanation:
                - Choose j-1 gap positions among i-1 inter-key gaps to place turns (nCk(i-1, j-1))
                - Multiply by s (possible starting keys)
                - Multiply by d**j (average branching factor applied at each of j turns)
3. Shift handling:
    - Only if match['shifted_count'] is truthy (i.e., > 0) does the function adjust guesses for shift-placement permutations.
    - Let S = match['shifted_count']; let U = L - S (unshifted count).
    - If U == 0 (i.e., all characters are shifted; note S > 0 is already true here), then multiply guesses by 2. This encodes the two possibilities: all shifted using Shift vs. all unshifted (the code treats all-shifted as doubling the pattern possibilities).
    - Otherwise (S > 0 and U > 0):
        * Compute shifted_variations = sum_{k=1..min(S, U)} nCk(S + U, k)
          (This sums combinations for mixed-shift placements up to the smaller side; it matches the original implementation's behavior.)
        * Multiply guesses by shifted_variations.
    - Note: If shifted_count == 0, this entire step is skipped (no multiplier).
4. Return the final guesses value.

## Examples:
Example constants used for illustration:
    KEYBOARD_STARTING_POSITIONS = 94
    KEYBOARD_AVERAGE_DEGREE = 4
    KEYPAD_STARTING_POSITIONS = 10
    KEYPAD_AVERAGE_DEGREE = 2

1) Too-short token:
    - match = {'graph': 'qwerty', 'token': 'a', 'turns': 0, 'shifted_count': 0}
    - L = 1 -> loop over i from 2..1 is skipped -> guesses remains 0 -> return 0

2) Small keyboard pattern (no shifts):
    - match = {'graph': 'qwerty', 'token': 'rtyf', 'turns': 1, 'shifted_count': 0}
    - L = 4, t = 1
    - Iterate i = 2, 3, 4; for each i compute possible_turns = min(1, i-1) + 1 and sum terms nCk(i-1, j-1)*s*d**j for j = 1..possible_turns-1
    - shifted_count == 0 -> no final multiplier

3) Token with mixed shifts:
    - match = {'graph': 'qwerty', 'token': 'Aa1!', 'turns': 1, 'shifted_count': 2}
    - L = 4, S = 2, U = 2 -> min(S, U) = 2
    - shifted_variations = C(4,1) + C(4,2) = 4 + 6 = 10
    - Final guesses = base_guesses * 10

Implementation hints:
    - Use math.comb (Python 3.8+) for exact integer binomial coefficients to avoid floating inaccuracies of a multiplicative nCk implementation.
    - Validate that shifted_count is between 0 and L before calling the function to avoid invalid combinatorics.
    - If integer results are required, cast the final value to int after computing with exact combinatorics.

## `zxcvbn.scoring.uppercase_variations` · *function*

## Summary:
Estimate how many distinct capitalization variants a matched token can produce by checking simple capitalization patterns and, for mixed-case words, summing combinatorial choices of case flips.

## Description:
This function analyzes the 'token' string from a match object and returns a numeric count that estimates the number of different upper/lowercase variations of that token.

Known callers:
- No direct callers were discovered in the scanned repository. Conceptually, this function is intended to be invoked by password-matching or scoring routines that evaluate how many capitalization variants a detected token (e.g., a word matched against a dictionary) would produce during strength estimation.

Why this is a separate function:
- It encapsulates the capitalization-variation logic (simple-pattern detection and combinatorial counting) so scoring code can treat capitalization as a separate factor when converting a matched token into an estimate of guess-space size. Separating this logic reduces duplication and keeps combinatorial reasoning (nCk) and regex-based pattern detection localized.

## Args:
    match (dict-like): An object with a string value accessible at key 'token'.
        - Expected type: mapping (e.g., dict) where match['token'] is a str.
        - Required key: 'token'
        - Interdependency: The function only uses match['token']; other keys on match are ignored.

## Returns:
    int or float:
    - 1: returned when the token is effectively all-lowercase (no capitalization variants beyond itself).
    - 2: returned when the token matches any of the simple capitalization patterns START_UPPER, END_UPPER, or ALL_UPPER (representing the token and its lowercase form).
    - Sum of combinations (numeric): for other mixed-case words, returns the sum over i = 1..min(U, L) of nCk(U + L, i), where U is the count of uppercase characters in the token and L is the count of lowercase characters. This represents the total number of ways to choose 1..min(U,L) positions from the token letters to flip case; note that the underlying nCk implementation may return a float for integer combinatorial values (e.g., 10.0).
    - Edge-case returns:
        * If the token contains no letter characters (so .lower() == token), the function returns 1.
        * If U or L equals 0 and none of the simple-pattern regex tests matched, the combinatorial loop contributes 0 and the function may return 0 only if earlier checks did not return 1 or 2 (this is a rare situation depending on the regex definitions). Typical tokens return >=1.

## Raises:
    - KeyError: if match does not contain the 'token' key.
    - AttributeError or TypeError: if match['token'] is not a str (for example, calling .lower() or .isupper() on a non-string will raise).
    - Any exceptions raised by referenced helpers (e.g., nCk) if they are called with invalid arguments will propagate.

## Constraints:
Preconditions:
    - Caller must pass a mapping-like object with a 'token' key whose value is a Python string.
    - The function relies on the following module-level symbols to exist and be regex or callable objects:
        * ALL_LOWER, START_UPPER, END_UPPER, ALL_UPPER: regex-like objects providing a .match(str) method.
        * nCk(n, k): a function that returns the binomial coefficient C(n, k) (the implementation used in this code may return numeric values as floats).
    - The token string may contain non-letter characters; only characters where str.isupper() or str.islower() return True are counted toward U and L.

Postconditions:
    - No external state is modified.
    - Return value is a numeric estimate (int or float) representing capitalization variations as described above.

## Side Effects:
    - None. No I/O, no global state mutation, and no external service calls occur inside this function.

## Control Flow:
flowchart TD
    Start --> GetToken[Get word = match['token']]
    GetToken --> CheckAllLower{ALL_LOWER.match(word) OR word.lower() == word}
    CheckAllLower -- True --> Return1[Return 1]
    CheckAllLower -- False --> CheckSimpleCaps[Check START_UPPER, END_UPPER, ALL_UPPER]
    CheckSimpleCaps -- Any Match --> Return2[Return 2]
    CheckSimpleCaps -- No Match --> CountCases[Compute U = count(isupper), L = count(islower)]
    CountCases --> ComputeVariations{min(U,L) >= 1?}
    ComputeVariations -- No --> ReturnVariations0[variations stays 0 -> Return 0 or previous value]
    ComputeVariations -- Yes --> LoopI[For i from 1 to min(U,L): variations += nCk(U+L, i)]
    LoopI --> ReturnVariations[Return variations]
    ReturnVariations --> End

## Examples:
- Basic usage (token is all-lowercase):
    - match = {'token': 'password'}
    - uppercase_variations(match) -> 1

- Simple capitalization (first letter uppercase):
    - match = {'token': 'Password'}
    - uppercase_variations(match) -> 2

- All-uppercase token:
    - match = {'token': 'PASSWORD'}
    - uppercase_variations(match) -> 2

- Mixed-case token (combinatorial count):
    - match = {'token': 'pAsS'}
      * U = 2 (A,S), L = 2 (p,s), U+L = 4, min(U,L) = 2
      * variations = C(4,1) + C(4,2) = 4 + 6 = 10 (may be returned as 10.0 depending on nCk)
      * uppercase_variations(match) -> 10

- Error handling example:
    - match = {} -> uppercase_variations(match) raises KeyError because 'token' is missing.
    - match = {'token': None} -> calling .lower() or .isupper() will raise AttributeError.

Notes and implementation details for reimplementers:
    - The function uses regex-based short-circuits for the common patterns (all-lowercase, first/last/entirely uppercase) to return small constants (1 or 2) quickly.
    - For other mixed-case words it computes a combinatorial total by summing nCk(U + L, i) for i = 1..min(U, L). The nCk helper should compute binomial coefficients; if exact integer results are required, implement nCk to return integers (e.g., using math.comb on supported Python versions).
    - Be careful with tokens that contain non-alphabetic characters: only characters where c.isupper() or c.islower() are counted toward U and L.

## `zxcvbn.scoring.l33t_variations` · *function*

## Summary:
Computes the number of distinct "l33t" (leet) substitution variations implied by a single matched token: returns how many different original/plain tokens could correspond to the observed token given the reported substitutions.

## Description:
This function is called with a match object describing a substring (token) of a password that may contain l33t substitutions. It examines each substitution mapping in match['sub'] and multiplies independent counts of possible ways the mapping could have been applied, producing a total number of possible original (unsubstituted) variants for that token.

Known callers within the codebase:
    - No direct callers were discovered in the immediate scan of this module. Typical usage (outside the scan) is from scoring or ranking routines that evaluate a match object produced by the matcher/parser stage when estimating how many candidate originals a matched token could represent; i.e., it's used during scoring to inflate guessed-counts when l33t substitutions are present.

Why this logic is a separate function:
    - It isolates the combinatorics required to count substitution-based variants from the rest of the scoring logic.
    - That separation keeps combinatorial calculations (including calls to the nCk utility) centralized and testable, and prevents duplicating the logic across different scoring heuristics.

## Args:
    match (dict):
        - Description: A mapping describing a single match (token) found in the input password and metadata about detected substitutions.
        - Required keys when match['l33t'] is truthy:
            * 'token' (str): the matched substring from the password (will be lower-cased by the function for analysis).
            * 'sub' (dict): mapping of substituted character -> original character. Iterated via sub.items().
        - Optional:
            * 'l33t' (bool): flag indicating whether this match contains l33t substitutions. If missing or False, the function returns 1 immediately.
        - Expected types/values:
            * 'token' must be a string (or at least support .lower() and iteration).
            * 'sub' should be a mapping whose keys and values are single-character strings describing the substitution (e.g., '@' -> 'a'). The code compares characters from token to the mapping entries; multi-character mappings will behave according to Python equality semantics but are not the intended use.
        - Interdependencies:
            * If 'l33t' is truthy, the function assumes 'token' and 'sub' exist and are correctly formed; these are accessed without additional guards.

## Returns:
    int or float:
        - Represents the number of distinct original tokens that the observed token could map to under the provided substitution mappings.
        - Typical values:
            * 1 when no l33t substitutions are present (match.get('l33t', False) is False) or when no substitution mappings lead to alternative originals.
            * >= 1 when l33t is True. For each substitution mapping, the function multiplies a factor representing the number of distinct ways that substitution could have been applied; the product is returned.
        - Implementation note: the function uses the nCk utility which, per its implementation, may return numeric values as floats even when mathematically integers; therefore the returned value may be an int or a float that is an integer-valued number (e.g., 6.0). Semantically the return is a count (non-negative integer).

## Raises:
    - KeyError:
        * If match.get('l33t', False) is True (or truthy) but 'sub' or 'token' keys are missing, a KeyError will be raised when attempting to access match['sub'] or match['token'].
    - AttributeError / TypeError:
        * If match['sub'] is not an iterable of (key, value) pairs (i.e., missing .items()) an AttributeError or TypeError may occur.
        * If match['token'] does not support .lower() or iteration, AttributeError/TypeError may occur.
    - Indirect numeric issues:
        * Because the function relies on nCk, extremely large counts may expose floating-point precision issues; these do not raise exceptions but can produce imprecise numeric results.

## Constraints:
Preconditions:
    - Prefer to call with match as produced by the matching stage: a dict that sets 'l33t' to True only when 'sub' and 'token' are present and well-formed.
    - 'sub' mappings are intended to be single-character substitutions (single-character keys and values); mismatched types or multi-character strings may lead to unexpected counts.

Postconditions:
    - The return value is >= 1.
    - The function does not modify the input match argument or any global state.

## Side Effects:
    - None. The function performs pure computation and reads only the provided match argument and the nCk utility. No I/O or external state mutations are performed.

## Control Flow:
flowchart TD
    Start --> CheckL33T{match.get('l33t', False)?}
    CheckL33T -- No --> Return1[Return 1]
    CheckL33T -- Yes --> InitVariations[variations = 1]
    InitVariations --> LoopSubs{For each (subbed,unsubbed) in match['sub'].items()}
    LoopSubs --> ComputeChars[chrs = list(match['token'].lower())]
    ComputeChars --> CountS[Compute S = count of subbed in chrs]
    CountS --> CountU[Compute U = count of unsubbed in chrs]
    CountU --> EitherZero{Is S == 0 or U == 0?}
    EitherZero -- Yes --> Double[variations *= 2]
    EitherZero -- No --> ComputeP[p = min(U, S)]
    ComputeP --> SumPossibilities[possibilities = sum_{i=1..p} nCk(U + S, i)]
    SumPossibilities --> Multiply[variations *= possibilities]
    Multiply --> NextSub{More substitutions?}
    NextSub -- Yes --> LoopSubs
    NextSub -- No --> ReturnVariations[Return variations]
    ReturnVariations --> End

## Implementation details and rationale summary:
    - For each substitution mapping (subbed -> unsubbed):
        * If only one of the characters (either the substituted character or the unsubstituted/original character) appears in the token (S == 0 or U == 0), there are exactly two possibilities for that mapping at the token level: either the character(s) observed are actually the substituted character(s) (the token uses substitution) or they are the unsubstituted/original character(s) (the token does not use the substitution). The code multiplies variations by 2 in this case.
        * If both characters appear (S > 0 and U > 0), the function counts combinations where at least one of the positions is treated as substituted. Let U be the count of original chars and S be the count of substituted chars; the number of distinct ways to choose i positions (1 <= i <= min(U,S)) among the (U+S) total positions in which the substitution could be considered applied is summed over i. This sum of binomial coefficients is computed with nCk and multiplied into the running total.
    - The algorithm multiplies independent counts for different substitution mappings under the assumption that different mappings (different subbed characters) are independent choices; this matches typical combinatorial modeling of independent substitutions across distinct character classes.

## Examples:
Example 1 — No l33t:
    Input:
        match = {'token': 'password', 'l33t': False}
    Call:
        l33t_variations(match)
    Result:
        1
    Explanation:
        When l33t is False the function short-circuits and returns 1 (no alternate l33t originals).

Example 2 — Substitution present but original character absent:
    Input:
        match = {'token': 'p@ssw0rd', 'l33t': True, 'sub': {'@':'a', '0':'o'}}
    Call:
        l33t_variations(match)
    Result:
        4
    Explanation:
        For '@'->'a': token contains '@' (S=1) but not 'a' (U=0) => factor *= 2
        For '0'->'o': token contains '0' (S=1) but not 'o' (U=0) => factor *= 2
        Total = 1 * 2 * 2 = 4

Example 3 — Both substituted and original characters present:
    Input:
        match = {'token': 'pa44a', 'l33t': True, 'sub': {'4':'a'}}
    Call:
        l33t_variations(match)
    Explanation:
        chrs = ['p','a','4','4','a'] -> S = 2 (two '4'), U = 2 (two 'a')
        p = min(U, S) = 2
        possibilities = nCk(4,1) + nCk(4,2) = 4 + 6 = 10
        Total = 10
    Result:
        10

Usage note:
    - Callers that rely on this count to adjust guess-ranks should treat the returned value as a combinatorial multiplier (multiply guessed-counts by this factor). If integer-typed outputs are required, callers should convert or round the result, keeping in mind nCk may return floats for mathematically integer results.

