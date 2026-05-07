# `__init__.py`

## `zxcvbn.__init__.zxcvbn` · *function*

## Summary:
Analyze a candidate password (optionally with contextual user inputs) and return a comprehensive strength report including guess estimates, attack time approximations, feedback, and timing information.

## Description:
This function is the primary high-level entry point that orchestrates password-strength analysis:
- It normalizes and incorporates optional user-specific inputs (e.g., username, email fragments) into the dictionary lookup data used by matchers.
- It collects pattern matches for the password, selects the most guessable match sequence, computes guess counts and log10 guesses, estimates attack times under several attacker models, and produces human-oriented feedback.

Known callers within the repository:
- No internal call sites were discovered during an automated search. The function is implemented as a public API entry point intended to be called by application code (UI, CLI, web handlers, or tests) that needs a password-strength evaluation.

Why this logic is extracted into its own function:
- Responsibility boundary: it composes lower-level components (matching, scoring, time estimates, feedback) into a single, stable API which returns a complete result dictionary. This separation keeps matching and scoring pure and focused while providing a convenient, consistent top-level interface for consumers.
- Reuse: callers need one consolidated result structure (including timing and feedback) rather than wiring multiple subsystem calls themselves.
- Side-effect management: it centralizes treatment of user-provided inputs and the integration of their ranked dictionary into the matching pipeline.

## Args:
    password (str or bytes):
        The password to analyze. Must be the exact string/bytes value to evaluate.
        - The function does not coerce non-string inputs; callers should pass a text/byte string. Passing other types may cause errors propagated from downstream matchers.
    user_inputs (iterable of values, optional):
        Additional user-specific values (for example: username, email, birthdate fragments, or other context).
        - Allowed values: any objects convertible to string. Each element will be cast to str when not a string/bytes and then lower-cased.
        - Default: None (treated as empty list).
        - Interdependencies: user_inputs are sanitized and converted into a ranked dictionary that is inserted under the 'user_inputs' key of the matching dictionaries used by the matcher pipeline.

## Returns:
A dictionary containing the consolidated password analysis. Keys produced by this function include (at minimum):

    'password' (str or bytes)
        The original password value passed through from the scoring component.

    'guesses' (numeric, typically Decimal or int-like)
        Estimated number of guesses required by the computed most-guessable attack sequence.

    'guesses_log10' (float)
        Base-10 logarithm of the guesses value for compact magnitude representation.

    'sequence' (list[dict])
        Optimal sequence of match dictionaries produced by the scoring algorithm. Each match dict describes a matched token (pattern type, i, j, token, and pattern-specific data).

    'calc_time' (datetime.timedelta)
        Time elapsed while performing this evaluation (from start to just after scoring).

    'crack_times_seconds' (dict)
        Numeric estimated times (in seconds) for attacker models; keys mirror the time_estimates component (e.g., 'online_throttling_100_per_hour', 'online_no_throttling_10_per_second', 'offline_slow_hashing_1e4_per_second', 'offline_fast_hashing_1e10_per_second').

    'crack_times_display' (dict)
        Human-readable display strings for the same attack scenarios (returned by time_estimates.display_time).

    'score' (int)
        Coarse-grained score computed from guesses (returned by time_estimates.guesses_to_score). Lower values mean weaker passwords.

    'feedback' (dict)
        Guidance for the user, with keys:
            'warning' (str): short warning text (may be empty string).
            'suggestions' (list[str]): actionable suggestions.

Possible edge-case return values:
- For an empty password (zero-length), the underlying scoring logic sets guesses to 1; other returned fields are present according to the same processing pipeline.
- If underlying dependencies return different types for guesses (e.g., Decimal), those are passed through.

## Raises:
- This function does not raise exceptions explicitly. However, exceptions raised by called subsystems (matching, scoring, time_estimates, feedback) will propagate. Examples (not exhaustively listed):
    - TypeError or KeyError from matcher/scoring code if passed malformed inputs (e.g., a password of an unexpected type or matches list with unexpected structure).
    - Any other runtime exceptions thrown by the dependency modules.

## Constraints:
Preconditions:
    - The caller should pass a string or bytes-like password. Non-string types are not converted by this function (and may cause errors downstream).
    - If user_inputs is provided it should be an iterable; elements will be coerced to strings if they are not instances of the supported string types.

Postconditions (guarantees after return):
    - The returned dict contains at least the keys documented in "Returns" and is enriched with the outputs from time_estimates and feedback.
    - The measured calculation time (calc_time) reflects the wall-clock time between the start of evaluation and completion of scoring.

## Side Effects:
- Mutation: The function assigns to ranked_dictionaries['user_inputs'] where ranked_dictionaries is taken from matching.RANKED_DICTIONARIES. If matching.RANKED_DICTIONARIES is a mutable global dictionary (as implemented), this call mutates that global mapping by adding or replacing the 'user_inputs' key. Callers that rely on matching.RANKED_DICTIONARIES being immutable should be aware of this mutation.
- No file I/O, no network I/O, and no other external state (database, cache) are performed directly by this function.
- The function will call external modules (matching, scoring, time_estimates, feedback) which may themselves have side effects; those effects are not introduced here except for the ranked_dictionaries mutation described above.

## Control Flow:
flowchart TD
    A[Start] --> B{user_inputs is None?}
    B -- yes --> C[set user_inputs = []]
    B -- no --> C
    C --> D[sanitize user_inputs: str() if needed, .lower()]
    D --> E[ranked_dictionaries = matching.RANKED_DICTIONARIES]
    E --> F[ranked_dictionaries['user_inputs'] = build_ranked_dict(sanitized_inputs)]
    F --> G[matches = matching.omnimatch(password, ranked_dictionaries)]
    G --> H[result = scoring.most_guessable_match_sequence(password, matches)]
    H --> I[result['calc_time'] = now - start]
    I --> J[attack_times = time_estimates.estimate_attack_times(result['guesses'])]
    J --> K[for each prop,val in attack_times: result[prop] = val]
    K --> L[result['feedback'] = feedback.get_feedback(result['score'], result['sequence'])]
    L --> M[return result]

## Examples:
Basic usage:
    try:
        report = zxcvbn("Tr0ub4dour&3", ["username", "firstname", "company.com"])
        # Access overall score and advice
        score = report['score']
        suggestions = report['feedback']['suggestions']
        # Time estimates
        offline_fast_seconds = report['crack_times_seconds']['offline_fast_hashing_1e10_per_second']
    except Exception as e:
        # Handle unexpected dependency errors (e.g., malformed inputs)
        handle_error(e)

Edge cases:
    - Empty password:
        report = zxcvbn("", [])
        # report['guesses'] will be 1 and feedback will be provided accordingly.

Notes and best practices:
    - Convert non-textual password inputs to str before calling to avoid type-related exceptions arising from matchers.
    - If you call this function repeatedly in a long-lived process and provide user_inputs each time, be aware that it mutates matching.RANKED_DICTIONARIES['user_inputs']; if you need to preserve the original global mapping, copy it or restore it afterward.
    - Because 'guesses' is often a Decimal-like numeric type, prefer numeric-safe consumption (e.g., using Decimal-aware formatting or converting to float for plotting, while being mindful of precision).

