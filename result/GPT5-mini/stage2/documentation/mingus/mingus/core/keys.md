# `keys.py`

## `mingus.core.keys.is_valid_key` · *function*

## Summary:
Returns True if the supplied musical key string exists in the module-level keys collection; otherwise returns False.

## Description:
This function performs a membership check of the provided key against the module-level keys collection (an iterable of "couples" or groups of equivalent key names, e.g., enharmonic equivalents). It centralizes the validation logic used anywhere the codebase needs to confirm that a user- or program-supplied key is recognized by the library.

Known callers within the codebase:
    - Typical callers are other functions in the same module that construct or operate on keys, scales or key signatures (for example: functions that build scales, return key signatures, or perform transposition/validation). The exact caller function names are not provided here; callers will usually invoke this function at the start of operations that require a validated key.

Why this is a separate function:
    - Encapsulates the membership test against the canonical keys collection in a single place so other modules don't duplicate the check.
    - Makes the validation logic easy to update if the shape of the keys collection changes (for example, from pairs to longer tuples or to a different container type).

## Args:
    key (str): A string representing a musical key name to validate.
        - Expected shape/values: common musical key names such as 'C', 'G', 'F#', 'Bb', 'A', 'D#m', etc. (The concrete accepted values depend on the contents of the module-level `keys` collection.)
        - Interdependencies: The valid set of values depends entirely on the module-level `keys` iterable; this function does not normalize or transform the input key (e.g., it does not convert 'c' to 'C').

## Returns:
    bool:
        - True if key is found in at least one element of the module-level `keys` iterable (i.e., the key is a recognized name).
        - False if the key is not found.
        - No other return values are produced.

## Raises:
    - This function raises no exceptions directly.
    - If the module-level `keys` name is missing or not iterable, a NameError or TypeError may occur at runtime (these exceptions are not explicitly raised by the function).

## Constraints:
    Preconditions:
        - The module-level variable `keys` must be defined and be an iterable of iterables (each "couple" should itself be an iterable supporting membership testing, e.g., tuple or list).
        - Caller should provide the key as the same type/format that the `keys` collection uses (typically a str).
    Postconditions:
        - No module-level state is changed.
        - The function returns a boolean describing membership; repeated calls with the same inputs yield the same result (purely functional with respect to inputs and the `keys` collection).

## Side Effects:
    - None. The function performs no I/O and mutates no external state.

## Control Flow:
flowchart TD
    Start --> ForEachCouple[Iterate over each 'couple' in keys]
    ForEachCouple --> CheckMembership[Is key in current couple?]
    CheckMembership -- Yes --> ReturnTrue[Return True and exit]
    CheckMembership -- No --> NextCouple[Continue to next couple]
    NextCouple --> ForEachCouple
    ForEachCouple --> AfterLoop[Finished iterating all couples]
    AfterLoop --> ReturnFalse[Return False and exit]

## Examples:
    Example 1 — simple validation
    try:
        if is_valid_key('C'):
            print("Valid key: C")
        else:
            print("Unknown key: C")
    except Exception as exc:
        # In normal use this shouldn't happen; catch unexpected runtime errors
        print("Validation failed:", exc)

    Example 2 — guard before constructing a scale (typical usage)
    def make_scale_for_key(key):
        if not is_valid_key(key):
            raise ValueError("Unsupported key: {}".format(key))
        # Proceed to build the scale for the validated key...

## `mingus.core.keys.get_key` · *function*

## Summary:
Return the module-defined key entry corresponding to the given number of accidentals (sharps/flats), enforcing the allowed range.

## Description:
This function maps an integer accidentals count in the inclusive range -7..+7 to the corresponding element of the module-level keys sequence by computing index = accidentals + 7 and returning keys[index].

Known callers:
- No call sites are identified in the provided fragment. Callers are typically higher-level functions or user-facing APIs that need to convert a numerical accidental count into a canonical key representation. To find callers in a codebase, search for references to get_key.

Reason for extraction:
- Encapsulates the mapping and range validation between an accidental count and the module-level keys table. Keeping this logic in a single function centralizes input validation and prevents duplication of the index arithmetic (accidentals + 7) and the range check across the codebase.

## Args:
    accidentals (int, optional): Number of accidentals (negative for flats, positive for sharps).
        - Allowed values: integers in the inclusive range -7 .. +7.
        - Default: 0
        - Notes: The function expects an integer. Non-integer types are not explicitly handled in the function and may raise a TypeError when evaluated in the range membership check.

## Returns:
    The element from the module-level sequence named keys at position (accidentals + 7).
    - Formally: return_value == keys[accidentals + 7]
    - The concrete type and meaning of the returned value depend on how the module-level keys sequence is defined; typically this will be a string or an object representing a musical key name.
    - Edge cases:
        - When accidentals == 0, the function returns keys[7].
        - If the keys sequence is missing or not indexable, a subsequent exception (e.g., NameError, TypeError, IndexError) may be raised by Python; the function itself does not catch those.

## Raises:
    RangeError: Raised when the provided accidentals value is not an integer within -7 .. +7 (the code checks membership using range(-7, 8)).
    Other exceptions (not raised by this function directly but possible at call time):
        - NameError: if the module-level name keys is not defined.
        - TypeError: if keys is not indexable or if accidentals is of an inappropriate type for the membership test.

## Constraints:
    Preconditions:
        - The caller must provide an integer-like accidentals value (or a value that supports membership testing in range).
        - The module-level variable keys must exist and be indexable with integer indices 0..14.
    Postconditions:
        - If no exception is raised, the returned value is keys[accidentals + 7] and accidentals was within the allowed range.

## Side Effects:
    - None within the function body: no I/O, no global mutation, no network access.
    - The function reads the module-level name keys; if that name is rebound externally before calling, the returned value will reflect that binding.

## Control Flow:
flowchart TD
    A[Start] --> B{accidentals in range(-7,8)?}
    B -- No --> C[Raise RangeError("integer not in range (-7)-(+7).")]
    B -- Yes --> D[Compute index = accidentals + 7]
    D --> E[Return keys[index]]
    C --> F[End]
    E --> F[End]

## Examples:
- Valid usage (happy path):
    try:
        key = get_key(2)  # request key for 2 sharps
    except RangeError as e:
        print("invalid accidentals:", e)
    else:
        print("key for 2 accidentals:", key)

- Error handling for out-of-range input:
    try:
        key = get_key(10)  # outside allowed range
    except RangeError as e:
        print("caught RangeError:", e)

Notes:
- To implement compatible behavior, ensure you provide a module-level sequence named keys with 15 elements indexed 0..14 such that index = accidentals + 7 maps -7..+7 into that sequence.
- Do not rely on this function to validate types beyond the range membership check; callers should ensure they pass integers when needed.

## `mingus.core.keys.get_key_signature` · *function*

## Summary:
Compute and return a numeric key-signature value for a validated musical key by locating the key in the module-level keys table and returning its index offset from 7.

## Description:
This function validates the input key using is_valid_key(key); if validation succeeds it searches the module-level iterable `keys` for the element ("couple") that contains the supplied key. It computes the signature as keys.index(couple) - 7 and returns that integer.

Typical callers (not present in the provided snapshot) are higher-level routines that require a numeric key signature for algorithmic processing or rendering (for example: functions that build scales, annotate notation, compute transpositions, or produce displayable key signatures). Extracting this logic into a separate function centralizes the membership check and the index-arithmetic mapping from textual key names to a small integer signature.

## Args:
    key (str, optional): Musical key name to look up. Defaults to "C".
        - Expected format: a string exactly matching one of the entries present in the module-level `keys` collection (the exact accepted strings depend on that collection).
        - The argument is validated by calling is_valid_key(key) before any lookup; this function does not perform case normalization or other transformations.

## Returns:
    int or None:
        - int: If the function finds a "couple" in `keys` that contains the supplied key, it returns keys.index(couple) - 7 (an integer computed directly from the module-level `keys` ordering).
        - None: If the loop completes without finding a matching couple (this is possible only if the module-level data is inconsistent with is_valid_key or if `keys` is modified), the function reaches its end without an explicit return and thus returns None.
        - No other return types are produced by the implementation.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Raised exactly when is_valid_key(key) evaluates to False.
        - The raised exception message is constructed as: "unrecognized format for key '%s'" % key (i.e., the literal message contains the provided key).
    NameError, TypeError, ValueError, or other runtime exceptions:
        - Possible if the module-level `keys` variable is missing, not iterable, or if keys.index(couple) fails for some reason. These are not explicitly raised by the function but are plausible in misconfigured environments.

## Constraints:
    Preconditions:
        - The module-level name `keys` must exist and be an iterable of iterables (each element must support membership testing and be findable via keys.index()).
        - is_valid_key must be available and reflect membership in the `keys` collection; otherwise the function's validation step may be inconsistent with the subsequent lookup.
        - Callers should provide key strings in the exact form present in `keys` (this function does no normalization).

    Postconditions:
        - If a matching couple is found, the function returns an integer equal to keys.index(couple) - 7.
        - The function does not perform I/O and does not mutate module-level state.

## Side Effects:
    - None. No I/O, no modification of global state, and no external calls other than is_valid_key and standard iterable operations.

## Control Flow:
flowchart TD
    Start --> Validate[Call is_valid_key(key)]
    Validate -- False --> RaiseError[Raise NoteFormatError("unrecognized format for key '%s'" % key) and exit]
    Validate -- True --> Loop[For each 'couple' in keys]
    Loop --> Check[If key in couple]
    Check -- Yes --> Compute[accidentals = keys.index(couple) - 7]
    Compute --> ReturnAccidentals[Return accidentals (int)]
    Check -- No --> Next[Continue to next couple]
    Next --> Loop
    Loop --> End[Finished iterating without finding match]
    End --> ReturnNone[Implicitly return None]

## Examples:
    Example 1 — default call:
    - Call: get_key_signature()
    - Behavior: equivalent to get_key_signature("C"); if the 'couple' containing "C" is at index 7 in `keys`, the function returns 0 (because 7 - 7 == 0). Whether "C" is at index 7 depends on the module-level `keys` data.

    Example 2 — invalid key string:
    try:
        get_key_signature("invalid-key")
    except NoteFormatError as e:
        # e.args[0] == "unrecognized format for key 'invalid-key'"
        handle_invalid_key()

    Example 3 — defensive handling for unexpected None (library-data inconsistency):
    sig = None
    try:
        sig = get_key_signature(user_key)
    except NoteFormatError:
        # reject or re-prompt for a valid key
        pass
    if sig is None:
        # This indicates a mismatch between validation and lookup or misconfiguration of `keys`.
        raise RuntimeError("get_key_signature returned None for a validated key; check module-level keys")

## `mingus.core.keys.get_key_signature_accidentals` · *function*

## Summary:
Return an ordered list of accidental strings (sharps "#" or flats "b") that constitute the key signature for the given musical key.

## Description:
This function asks for the numeric key signature (an integer count of accidentals) from the numeric lookup helper and expands that integer into the sequence of notes that are sharpened or flattened in the key signature.

Known callers within the codebase:
- No direct callers are present in the provided snapshot. Typical callers (in the rest of the library) are rendering or notation helpers, scale/scale-building utilities, and transposition or display routines that need the explicit accidentals for a key (for example: functions that draw or return the list of notes to mark on a staff, or that build a displayable key-signature).

Why this logic is separated:
- Responsibility boundary: get_key_signature_accidentals isolates the mapping from a numeric signature (an integer count returned by get_key_signature) to the concrete accidental tokens used in notation (e.g., "F#", "Bb"). Keeping this logic separate centralizes the formatting and ordering rules for accidentals and avoids duplicating the notes.fifths indexing logic across callers.

## Args:
    key (str, optional): Musical key name to look up. Defaults to "C".
        - The value is forwarded to get_key_signature(key) and must therefore be accepted by that function.
        - No case-normalization or additional parsing is performed here; invalid keys cause get_key_signature to raise NoteFormatError.

## Returns:
    list[str]: A list of strings, each representing an accidental in the order they appear in the key signature.
        - Sharps: When the numeric signature (accidentals) is > 0, the function returns the first N entries from notes.fifths (in order) with a trailing "#" (e.g., ["F#", "C#"] for two sharps).
        - Flats: When the numeric signature is < 0, the function returns the first N entries from reversed(notes.fifths) with a trailing "b" (e.g., ["Bb", "Eb"] for two flats).
        - No accidentals: When the numeric signature is 0, an empty list is returned.
        - Edge-case values: If get_key_signature returns a value outside the expected / typical range or returns None, see Raises / Constraints below.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Propagated directly from get_key_signature when the provided key string is not in the expected format or not recognized.
    TypeError:
        - If get_key_signature returns None (or a non-numeric type) the comparison accidentals < 0 will raise TypeError.
    IndexError:
        - If the absolute value of the numeric signature exceeds the length of notes.fifths, the indexing into notes.fifths or its reversed view will raise IndexError.
    Other runtime exceptions:
        - Any other exceptions thrown by get_key_signature or by notes.fifths access (e.g., if notes.fifths is missing or not indexable) will propagate.

## Constraints:
    Preconditions:
        - The module-level function get_key_signature must exist and accept the same key format.
        - notes.fifths must be a finite, indexable sequence of note names ordered by fifths (the function indexes into it and into its reversed view).
        - Callers should expect get_key_signature to return an integer (typically in the range -7..+7 for standard Western key signatures); providing keys that map outside that typical range risks IndexError.

    Postconditions:
        - The return value is a list (possibly empty) of formatted accidental tokens of the form "<Note><# or b>".
        - The order of items matches conventional key-signature order: sharps are ordered by ascending fifths (notes.fifths[0] first); flats are ordered by ascending fifths of the reversed sequence.

## Side Effects:
    - None. The function performs no I/O and does not modify global state; it only queries get_key_signature and reads notes.fifths.

## Control Flow:
flowchart TD
    Start --> CallGetSig[Call get_key_signature(key)]
    CallGetSig --> SigVal{accidentals is int?}
    SigVal -- False (None / non-int) --> TypeErrorOrPropagate[Comparison or other operation raises TypeError or propagates upstream]
    SigVal -- True --> IsNeg{accidentals < 0}
    IsNeg -- Yes --> ForNeg[Loop i in range(-accidentals)]
    ForNeg --> AppendFlat[Append reversed(notes.fifths)[i] + "b"]
    AppendFlat --> End[Return res list]
    IsNeg -- No --> IsPos{accidentals > 0}
    IsPos -- Yes --> ForPos[Loop i in range(accidentals)]
    ForPos --> AppendSharp[Append notes.fifths[i] + "#"]
    AppendSharp --> End
    IsPos -- No --> End

## Examples:
    Example 1 — no accidentals (C major):
    >>> get_key_signature_accidentals("C")
    []  # empty list: 0 accidentals

    Example 2 — one sharp (G major):
    >>> get_key_signature_accidentals("G")
    ["F#"]  # G has one sharp: F#

    Example 3 — one flat (F major):
    >>> get_key_signature_accidentals("F")
    ["Bb"]  # F has one flat: Bb

    Example 4 — invalid key handling:
    try:
        get_key_signature_accidentals("not-a-key")
    except NoteFormatError as e:
        # handle missing/invalid key string (propagated from get_key_signature)
        pass

    Example 5 — defensive caller code for unexpected None or out-of-range values:
    try:
        accidentals = get_key_signature_accidentals(user_key)
    except NoteFormatError:
        # invalid key input
        handle_bad_key()
    except (TypeError, IndexError):
        # library-data inconsistency (get_key_signature returned None or magnitude exceeds notes.fifths)
        handle_library_inconsistency()

## `mingus.core.keys.get_notes` · *function*

## Summary:
Return the seven note names for a given musical key (the diatonic notes of the major scale starting at the key's tonic), applying the key signature's accidentals and caching the result.

## Description:
- Known callers and typical context:
    - Higher-level functions that need the ordered list of scale degree note names for a key, for example scale construction, rendering/notation routines, transposition helpers, or any code that must display or operate on the seven diatonic notes of a major key.
    - Typical use: called early in a pipeline after a key string is supplied by the user or derived programmatically, to obtain the seven pitch-class names (letters optionally suffixed by '#' or 'b') that form the key's diatonic scale.

- Why this logic is extracted:
    - Encapsulates the assembly of a key's diatonic note names (taking into account the numeric key signature and the ordered base scale) and centralizes caching to avoid recomputing identical results.
    - Keeps responsibilities separate: validation, numeric signature lookup, accidental-to-note mapping, and final note-list construction are delegated to smaller helpers; get_notes composes these results into the final, displayable list.

## Args:
    key (str, optional): A musical key name string identifying the tonic and quality (defaults to "C").
        - Expected values: canonical key name strings recognized by the module-level keys collection (examples: "C", "G", "F", "D#", "Bb", "A", "D#m").
        - The function does not normalize or canonicalize the key; it uses the key string as-is for cache lookup and validation. Case affects validation only insofar as the module's validators expect certain case patterns; however the tonic letter is extracted using key.upper()[0] internally.
        - Interdependencies: `key` must be accepted by is_valid_key(key) and by get_key_signature(key) / get_key_signature_accidentals(key). If those helpers do not accept the value, NoteFormatError (or other exceptions from those functions) will propagate.

## Returns:
    list[str]: A list of seven strings, each representing a diatonic pitch-class name in order from the tonic up to the seventh degree (no octave numbers).
        - Elements are either a single uppercase letter from A through G (e.g., "C", "D") or a letter followed by a single accidental symbol '#' or 'b' (e.g., "F#", "Bb").
        - The order is the natural diatonic order starting at the tonic letter: it is produced by rotating the module-level base_scale (expected to be ["C", "D", "E", "F", "G", "A", "B"]) so the first element matches key.upper()[0], then taking seven consecutive letters.
        - When the key's numeric signature has nonzero accidentals, notes whose letter appears in the accidental list (derived from get_key_signature_accidentals) are suffixed with the symbol chosen for the signature (either '#' for sharps when get_key_signature(key) > 0, or 'b' for flats when get_key_signature(key) < 0).
        - Guaranteed length: Exactly 7 elements in the returned list in normal operation.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Raised explicitly if is_valid_key(key) returns False. The exact message constructed by the function is:
          "unrecognized format for key '%s'" % key
    TypeError:
        - May be raised if get_key_signature(key) returns None or a non-numeric type and the code attempts numeric comparisons (e.g., None < 0).
    IndexError or ValueError:
        - ValueError may be raised if base_scale does not contain key.upper()[0] (base_scale.index(...) fails). Normally is_valid_key should prevent this; if module-level data is inconsistent this can occur.
        - IndexError is possible indirectly if a helper (e.g., get_key_signature_accidentals) or notes.fifths indexing returns out-of-range values; these will propagate.
    Other runtime exceptions:
        - Any exceptions thrown by is_valid_key, get_key_signature, get_key_signature_accidentals, or by malformed module-level data (e.g., missing base_scale or _key_cache) will propagate.

## Constraints:
- Preconditions:
    - Module-level base_scale must exist and be an ordered iterable of the seven natural note letters in diatonic order: ["C", "D", "E", "F", "G", "A", "B"] (strings of length 1).
    - Module-level _key_cache must exist and be a mutable mapping (e.g., dict) used to cache results indexed by the original key string.
    - is_valid_key(key), get_key_signature(key), and get_key_signature_accidentals(key) must be available and behave as described:
        * is_valid_key returns True for recognized key strings.
        * get_key_signature returns an integer number of accidentals (typically in range -7..+7) or raises NoteFormatError for invalid keys.
        * get_key_signature_accidentals returns a list of accidental strings formatted as "<Letter><# or b>" (e.g., "F#", "Bb").
    - Caller should pass a canonical key string; caching uses the raw key string as the key.

- Postconditions:
    - If the function returns normally, it stores the computed list under _key_cache[key] (mutating _key_cache) before returning, so subsequent calls with the identical key string return the cached list object (or a reference to it).
    - The returned list contains exactly seven strings and does not contain duplicate accidental symbols beyond the single trailing '#' or 'b'.

## Side Effects:
    - Mutates module-level cache: sets _key_cache[key] = result (where result is the returned list).
    - Performs no I/O, network access, or other external state mutation.
    - Calls into helper functions (which may raise exceptions) but does not otherwise change their state.

## Control Flow:
flowchart TD
    Start --> CheckCache{Is key in _key_cache?}
    CheckCache -- Yes --> ReturnCached[Return _key_cache[key]]
    CheckCache -- No --> ValidateKey[Call is_valid_key(key)]
    ValidateKey -- False --> RaiseNoteFormat[Raise NoteFormatError("unrecognized format for key '%s'" % key)]
    ValidateKey -- True --> ComputeAltered[Call get_key_signature_accidentals(key) and build altered_notes = [x[0] for x in result]]
    ComputeAltered --> GetSig[Call get_key_signature(key)]
    GetSig --> IsNeg{sig < 0}
    IsNeg -- True --> symbol_b[Set symbol = "b"]
    IsNeg -- False --> IsPos{sig > 0}
    IsPos -- True --> symbol_sharp[Set symbol = "#"]
    IsPos -- False --> no_symbol[Leave symbol undefined (not used because altered_notes will be empty)]
    no_symbol --> FindTonic[raw_tonic_index = base_scale.index(key.upper()[0])]
    symbol_b --> FindTonic
    symbol_sharp --> FindTonic
    FindTonic --> BuildList[Iterate notes = islice(cycle(base_scale), raw_tonic_index, raw_tonic_index + 7)]
    BuildList --> ForEachNote{For each note in iteration}
    ForEachNote -- note in altered_notes --> AppendWithSymbol[Append note + symbol to result]
    ForEachNote -- note not in altered_notes --> AppendPlain[Append note to result]
    AppendWithSymbol --> NextNote
    AppendPlain --> NextNote
    NextNote --> ForEachNote
    ForEachNote --> CacheAndReturn[Set _key_cache[key] = result; return result]

## Examples:
- Typical successful usage:
    try:
        notes = get_notes("G")
        # Example result: ["G", "A", "B", "C", "D", "E", "F#"]
    except NoteFormatError:
        # Handle invalid user input
        raise ValueError("Invalid key supplied")

- Using cached result (no recomputation):
    # First call computes and caches
    major_C = get_notes("C")  # ["C", "D", "E", "F", "G", "A", "B"]
    # Second call returns cached list (fast)
    major_C_again = get_notes("C")  # same list object returned from _key_cache

- Defensive handling for library inconsistencies:
    try:
        notes = get_notes(user_key)
    except NoteFormatError:
        # invalid key supplied by user
        handle_bad_key()
    except (TypeError, IndexError, ValueError):
        # indicates module-level data inconsistency (e.g., get_key_signature returned None
        # or base_scale not shaped as expected); log and abort or fallback
        handle_library_error()

- Implementation notes for reimplementation:
    - Ensure base_scale = ["C","D","E","F","G","A","B"] and _key_cache = {} at module scope.
    - get_key_signature_accidentals(key) returns strings like "F#" or "Bb"; this function extracts the letter portion via accidental[0] to compare against base_scale items.
    - When key signature is 0, altered_notes will be empty and no accidental symbol will be appended.

## `mingus.core.keys.relative_major` · *function*

## Summary:
Look up and return the major key name that is the relative major of the given minor-key name; raises NoteFormatError if the provided name is not found as a minor key.

## Description:
This function performs a linear search over the module-level iterable named keys and returns the first element[0] for which element[1] equals the supplied key argument. It is a small utility that centralizes the minor->major resolution and standardized error reporting.

Known callers:
- No callers were discovered in the provided subset of the repository. In a full codebase, this function is typically used by key-conversion utilities, UI/key-parsing helpers, and transposition routines that need to compute a relative major from a minor key name.

Why this is a separate function:
- Encapsulates lookup logic and consistent error formatting in a single place.
- Avoids duplicating the iteration and comparison semantics across the codebase.
- Makes unit testing and mocking of the keys lookup straightforward.

## Args:
    key (str): The minor key name to look up.
        - Must be provided in the same canonical string format used by the module-level keys mapping (see Constraints).
        - Comparison is a simple equality check (==); no case-folding, whitespace trimming, or enharmonic equivalence normalization is performed.

## Returns:
    str: The corresponding major key name.
        - Specifically, returns element[0] for the first element in keys where element[1] == key.
        - If multiple entries in keys have the same element[1], the first matching entry (iteration order) determines the result.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        - Condition: No item in keys has item[1] equal to the provided key.
        - Message: "'%s' is not a minor key" % key

    NameError
        - Condition: The module-level name keys is not defined in the module namespace when the function is called.
        - Note: This is a native Python error surfaced if keys is missing.

    TypeError
        - Condition: An element yielded by keys does not support indexing (item[1]) or keys is not iterable; or comparison raises a TypeError.
        - Examples: element is an int, or keys is None.

    IndexError
        - Condition: An element yielded by keys is a sequence shorter than 2 elements so item[1] access fails.

## Constraints:
Preconditions:
    - The module must define a variable named keys that is iterable.
    - Each element of keys is expected to be a 2-tuple or 2-list of strings: (major_name: str, minor_name: str).
    - The caller must pass key as a string that matches the format used in keys (e.g., exact case and accidentals as stored).

Postconditions:
    - On success, the returned value equals some keys[i][0] where keys[i][1] == key.
    - On failure (no match), a NoteFormatError is raised and no state is modified.

## Side Effects:
    - None. The function performs no I/O and does not modify global variables or external state; it only reads the module-level keys iterable.

## Control Flow:
flowchart TD
    Start --> CheckKeys["Ensure 'keys' iterable exists"]
    CheckKeys --> ForEach["For each element in keys"]
    ForEach --> IndexAccess["Access candidate_minor = element[1]"]
    IndexAccess --> Compare["Compare candidate_minor == key"]
    Compare -->|True| ReturnVal["Return element[0] (major)"]
    Compare -->|False| Next["Continue to next element"]
    Next --> ForEach
    ForEach --> EndLoop["Finished iteration (no match)"]
    EndLoop --> RaiseErr["Raise NoteFormatError(\"'%s' is not a minor key\" % key)"]

## Examples:

Example 1 — Successful lookup (typical):
    # Example keys mapping (module-level)
    keys = [
        ('C', 'a'),  # 'a' minor has relative major 'C'
        ('G', 'e'),
        ('D', 'b')
    ]
    relative_major('a')  # -> 'C'
    relative_major('e')  # -> 'G'

Example 2 — Not found: handling NoteFormatError
    keys = [('C', 'a')]
    try:
        relative_major('f#')
    except NoteFormatError as e:
        # e.args[0] == "'f#' is not a minor key"
        # handle missing mapping (fallback, log, or re-raise)
        fallback_to_default_key()

Example 3 — Malformed keys mapping: defensive handling
    # If keys is missing or malformed, native errors can occur:
    try:
        relative_major('a')
    except NameError:
        # Module-level mapping 'keys' is absent
        initialize_keys_mapping()
    except (TypeError, IndexError):
        # An element in keys is not a (major, minor) 2-tuple
        repair_or_validate_keys()

## `mingus.core.keys.relative_minor` · *function*

## Summary:
Returns the relative minor for a given major key by looking up the first matching pair in the module-level keys sequence; raises an error if the provided key is not found.

## Description:
This function scans the module-level iterable named `keys` (expected to contain 2-tuples where the first element is a major key and the second element is its relative minor) and returns the second element of the first tuple whose first element equals the provided key.

Known callers within the codebase:
- No callers were discovered in the provided context. Callers may exist elsewhere in the project; this documentation does not assume or invent them.

Why extracted:
- Encapsulates the lookup logic for mapping a major key to its relative minor in a single place so other code can reuse a simple, well-named API rather than duplicating iteration and error handling.
- Enforces a clear responsibility boundary: given a single key, return its relative minor if present, otherwise raise a well-defined error.

## Args:
    key (str): The major key to look up. The function performs an equality comparison against the first element of each pair in the module-level sequence `keys`.
        - Allowed values: any object comparable by equality to elements used as "major keys" inside `keys`.
        - Typical usage: a string representing a musical major key in the same format used by the rest of the keys data structure (e.g., 'C', 'G', 'F#' depending on repository conventions).
        - No default value; argument is required.
        - Interdependencies: `key` must be comparable to the first elements of `keys`; if `keys` uses a normalized note format, callers should pass the key in that normalized form.

## Returns:
    str (or other type as stored in `keys` tuple second element): The relative minor corresponding to the matched major key.
    - If a tuple (major, minor) in `keys` has its first element equal to `key`, the function immediately returns that tuple's second element.
    - If multiple tuples in `keys` have the same first element, the function returns the second element of the first matching tuple (i.e., the earliest match).
    - Edge cases:
        - If `keys` is empty or contains no tuple whose first element equals `key`, the function does not return but raises NoteFormatError (see Raises).
        - The return type is whatever type is stored as the second element of the tuples in `keys` (commonly a string representing a note).

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Raised when the function finishes scanning `keys` without finding any tuple whose first element equals the input `key`.
        - Error message format exactly as in the implementation: "'%s' is not a major key" % key

## Constraints:
    Preconditions:
        - The module-level identifier `keys` must be an iterable of 2-element sequences (e.g., tuples or lists). Each element is expected to be indexable so that element[0] is the major key to compare and element[1] is the relative minor to return.
        - Elements in `keys` must be comparable with `==` to the provided `key`.
    Postconditions:
        - On successful return, the returned value equals the second item of some tuple in `keys` whose first item equals `key`.
        - No changes are made to `keys` or other global state by this function.

## Side Effects:
    - None. The function performs pure read-only operations on the module-level `keys` iterable and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    Start --> ForLoop[Iterate over each tuple in keys]
    ForLoop --> CheckMatch{Is tuple[0] == key?}
    CheckMatch -- Yes --> ReturnMinor[Return tuple[1]]
    CheckMatch -- No --> NextTuple[Continue loop]
    NextTuple --> ForLoop
    ForLoop --> EndNotFound{No more tuples?}
    EndNotFound -- Yes --> RaiseError[Raise NoteFormatError("'key' is not a major key")]
    RaiseError --> End

## Examples:
- Basic usage (conceptual; actual returned value depends on contents/format of module-level `keys`):
    - If keys contains the pair ('C', 'A'):
        - relative_minor('C') returns 'A'
    - If keys does not contain any pair whose first element equals 'Db':
        - calling relative_minor('Db') raises NoteFormatError("'Db' is not a major key")

- Example with error handling:
    - Callers that cannot guarantee the presence of the input key should catch NoteFormatError:
        try:
            minor = relative_minor(user_supplied_key)
        except NoteFormatError as e:
            # handle missing major key (e.g., inform user or fall back)
            handle_missing_key(e)

## `mingus.core.keys.Key` · *class*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Represents a musical key (tonic plus mode) and exposes derived display and analytic properties: a human-readable name, a diatonic mode ("major" or "minor"), and a numeric key signature computed from module-level key tables.

## Description:
This class is a lightweight value-object used to encapsulate a musical key identifier (for example "C", "c", "F#", "eb") together with derived metadata that other parts of the music library can use without repeating parsing logic.

Typical instantiation scenarios:
- When callers need a single object containing (1) the original key string, (2) a normalized notion of its mode (major/minor), (3) a display-friendly name, and (4) the numeric key signature produced by the module-level key table lookup.
- As a small adapter returned by factories or utilities that translate user-supplied key names into a consistent, re-usable structure for scale generation, transposition, or notation rendering.

Motivation and responsibility boundary:
- The Key class centralizes presentation (name) and analytic (signature) derivations for a textual key label. It intentionally does not perform broad normalization: the original key string is preserved and equality is exact-string based. It delegates key validation / signature calculation to the module-level get_key_signature function.

## State:
Public attributes set by __init__:
- key (str)
    - Description: The textual key token provided by the caller, preserved exactly as passed.
    - Type: str
    - Constraints: Must be a non-empty string that matches one of the key forms present in the module-level `keys` collection if callers expect signature computation to succeed.
    - Notes: The class does not normalize case or accidental notation; the exact string is used for equality and for signature lookup.

- mode (str)
    - Description: The diatonic mode inferred from the first character of `key`.
    - Type: str
    - Valid values: "major" or "minor"
    - Inference rule: If the first character of `key` is lowercase, mode == "minor"; otherwise mode == "major".
    - Invariant: mode is always one of {"major","minor"} after initialization provided `key` is indexable.

- name (str)
    - Description: A human-readable name constructed from `key`'s first character (uppercase), an optional accidental symbol expansion, and the mode.
    - Type: str
    - Construction rules:
        - The first character of `key` is uppercased and used as the tonic letter.
        - If `key` has a second character, it is inspected:
            - If second character == "#", the intermediate symbol string becomes "sharp ".
            - If second character exists and is not "#", the symbol string becomes "flat ".
        - If no second character is present, symbol string is empty.
        - Final form: "<Uppercase tonic> <symbol><mode>" (note the single space between tonic and the rest).
    - Examples: For key "C" => "C major"; "c" => "C minor"; "F#" => "F sharp major"; "eb" => "E flat minor".

- signature (int or None)
    - Description: Numeric key signature value obtained by calling get_key_signature(key).
    - Type: int or None
    - Meaning: The integer is an index-derived value (module-level convention: keys.index(couple) - 7). None may occur if the module-level `keys` data is inconsistent or mutated; invalid key inputs instead cause get_key_signature to raise NoteFormatError.
    - Invariant: After initialization, signature is either an int (expected) or None (indicates library data inconsistency).

Class invariants after successful __init__:
- key is a str and indexable (has at least one character).
- mode is either "major" or "minor".
- name is a non-empty str derived from key and mode.
- signature is either an int (typical) or None (anomalous but possible).
- Equality (__eq__) compares Key objects by the exact `key` attribute; objects with identical key strings are equal.

## Lifecycle:
Creation:
- Instantiate with the constructor, providing an optional key string:
    - Required/optional args: key (str) — defaults to "C".
    - Typical call: create a new Key by passing a textual key like "C", "c", "F#", or "eb".
- During initialization:
    - The constructor stores the provided key string on the instance.
    - It infers the mode from the case of the first character.
    - It attempts to read a second character (if present) to create a user-friendly accidental label ("sharp " or "flat ").
    - It composes the display `name`.
    - It calls the module-level get_key_signature(key) and stores the returned value on `signature`. NoteFormatError may be raised by get_key_signature for unrecognized formats.

Usage:
- After construction, callers read attributes directly: `key`, `mode`, `name`, `signature`.
- For comparisons, use equality semantics: two Key instances are equal if and only if their `key` attributes are exactly equal.
- There is no implicit normalization: callers that need canonicalization must perform it before constructing Key objects.

Destruction / Cleanup:
- Key holds only simple data (strings and integers); there is no external resource management or cleanup required.
- No context manager or close() method is provided or required.

## Method Map:
flowchart TD
    A[Instantiate Key(key)] --> B[set self.key = key]
    B --> C{first char lowercase?}
    C -- yes --> D[set mode = "minor"]
    C -- no --> E[set mode = "major"]
    D --> F[try to read second char and set symbol]
    E --> F
    F --> G[compose name from tonic + symbol + mode]
    G --> H[call get_key_signature(key)]
    H --> I[set signature = returned int or None]
    A --> J[__eq__(other): compare self.key == other.key]
    A --> K[__ne__(other): return not __eq__]

Typical invocation order:
1. Instantiate Key (constructor runs steps B → I).
2. Read attributes or call equality operators (J/K) as needed.
3. No cleanup step.

## Raises:
Exceptions that may propagate from __init__:
- mingus.core.mt_exceptions.NoteFormatError
    - Trigger: Raised by get_key_signature(key) when the provided key string fails module-level validation. The message will be: "unrecognized format for key '%s'" % key.
- IndexError
    - Trigger: If `key` is an empty string, accessing key[0] will raise IndexError before validation or signature lookup.
- TypeError
    - Trigger: If `key` is not a subscriptable/sequence type (for example None or a non-sequence), attempts to read key[0] will raise TypeError.
- AttributeError (possible when comparing instances)
    - Trigger: Calling __eq__ with an object that does not have a `.key` attribute will raise AttributeError.
- Other runtime errors from get_key_signature or the module-level environment
    - Trigger: If the module-level `keys` data structure is missing or malformed, get_key_signature may raise other exceptions (NameError, ValueError, etc.). These propagate unchanged.

Notes on exception handling:
- The class does not catch or translate exceptions raised by get_key_signature; callers should catch NoteFormatError when constructing Keys from user input.
- The __init__ uses a broad try/except only around reading the second character; it deliberately ignores failures reading the second char (treating them as "no accidental").

## Example:
1) Creation and attribute access (described steps)
- Provide a valid key string, e.g. "c" to indicate C minor:
    - After construction: key == "c"; mode == "minor"; name == "C minor"; signature == integer computed by get_key_signature("c").
- Provide an accidental, e.g. "F#":
    - After construction: key == "F#"; mode == "major"; name == "F sharp major"; signature == get_key_signature("F#").

2) Typical equality usage (behavioral description)
- Two Key instances constructed with exactly the same key string compare equal. If either instance uses a different case or notation (for example "C" vs "c"), they are not equal because the comparison is exact-string based.

3) Defensive creation pattern (recommended usage)
- When accepting arbitrary user input for keys, validate or catch NoteFormatError around Key construction:
    - Validate input with the module's validation utilities or construct inside a try/except block and handle NoteFormatError to notify users of invalid input.

### `mingus.core.keys.Key.__init__` · *method*

## Summary:
Initializes the Key object state from a short key string (e.g., "C", "c", "Bb", "f#"), setting the canonical key string, inferred mode ("major" or "minor"), a human-readable name, and the numeric key signature used by the rest of the library.

## Description:
This constructor accepts a textual key identifier and populates four instance attributes used by other Key methods and external routines:
- key: the raw key string supplied by the caller.
- mode: determined from the case of the first character ("minor" when the first character is lowercase; otherwise "major").
- name: a human-readable label built from the uppercase letter, an optional accidental word ("sharp " or "flat "), and the mode.
- signature: a numeric key-signature value produced by get_key_signature(key) (see get_key_signature documentation).

Known callers and lifecycle:
- Any code that constructs a Key object to represent tonal context — for example, callers that build scales, chords, transpositions, or render notation — will call this initializer at object creation time.
- This logic is part of object construction (invoked when Key() is instantiated) and centralizes parsing/normalization and the call to get_key_signature so downstream code can assume these attributes exist and are consistently formatted.

This logic is implemented in the initializer rather than being inlined elsewhere because:
- It must run exactly once at construction to produce a consistent set of derived attributes.
- Centralizing name-formatting and the signature lookup here prevents duplication and ensures every Key instance exposes the same derived state immediately after instantiation.

## Args:
    key (str, optional): Short textual key identifier. Defaults to "C".
        - Expected format: a non-empty string whose first character is the base note letter (case matters: lowercase => minor, uppercase => major). The second character, if present, is interpreted as an accidental: '#' is treated as a sharp and any other character is treated as a flat for naming purposes.
        - Examples: "C", "c", "Bb", "f#", "G#"
        - Note: The value is validated later by get_key_signature; the initializer does not itself normalize the string beyond reading characters for mode and name generation.

## Returns:
    None

## Raises:
    NoteFormatError:
        - May be raised by get_key_signature(self.key) if the provided key string fails validation. This exception originates in get_key_signature and is not caught inside the constructor.
    IndexError:
        - If `key` is an empty string, accessing self.key[0] will raise IndexError before name/signature logic proceeds.
    TypeError:
        - If `key` is not subscriptable (for example, None or an object that does not support indexing), accessing self.key[0] will raise TypeError.
    Other exceptions:
        - A bare except is used around the second-character inspection; any exception thrown during that small block (other than the earlier first-character access) will be swallowed and treated as "no accidental". Exceptions raised by get_key_signature (other than NoteFormatError) can also propagate.

## State Changes:
Attributes READ:
    - self.key[0] (reads first character to determine mode)
    - self.key[1] (attempted read to determine accidental; access is inside a try/except)
Attributes WRITTEN:
    - self.key: set to the provided argument
    - self.mode: set to "minor" if first character is lowercase, otherwise "major"
    - self.name: set to a formatted string "{UppercaseBase} {accidental-word}{mode}" where accidental-word is "sharp " for '#' or "flat " for any other second character; omitted when there is no second character or on exception
    - self.signature: set to the return value of get_key_signature(self.key) (an int in normal operation; may be None only in inconsistent module-data scenarios per get_key_signature's contract)

## Constraints:
Preconditions:
    - The `key` argument must be a non-empty, indexable string to avoid IndexError/TypeError when reading characters.
    - The string should be in a form that get_key_signature recognizes; otherwise get_key_signature will raise NoteFormatError.

Postconditions:
    - After successful return, the instance has:
        * self.key equal to the supplied key argument,
        * self.mode set to "minor" for lowercase first letters, "major" otherwise,
        * self.name set to a human-readable label built from the first character, optional accidental word, and the mode,
        * self.signature set to get_key_signature(self.key) (typically an int; may be None only if the module-level keys data is inconsistent with validation).
    - If get_key_signature raises NoteFormatError, the constructor does not complete and no Key instance is returned to the caller.

## Side Effects:
    - Calls get_key_signature(self.key), which validates the key and computes the numeric signature; that call may raise NoteFormatError which propagates out of the constructor.
    - No I/O is performed.
    - No global state is mutated by this constructor; mutations are limited to the new Key instance attributes.

### `mingus.core.keys.Key.__eq__` · *method*

## Summary:
Compares this Key with another object by checking whether their stored key identifiers (self.key and other.key) are exactly equal, returning a boolean without modifying either object.

## Description:
This method is the equality operator implementation used when two Key objects (or compatible objects) are compared with the == operator. Typical invocation contexts include:
- Direct comparisons in code (a == b) where a and b are Key instances.
- Membership or deduplication checks (e.g., checking if a Key is present in a list).
- Equality checks performed implicitly by containers or algorithms (e.g., when removing duplicates or asserting expected values in tests).

It is implemented as a dedicated method so Python's rich comparison protocol (operator overloading for ==) yields consistent, idiomatic behavior across the codebase and so that containers and language features that rely on __eq__ behave correctly. Keeping this logic in __eq__ centralizes equality semantics and prevents duplication across call sites.

## Args:
    other (object): The object to compare against. Expected to provide a .key attribute (typically another Key instance). No implicit conversion is performed.

## Returns:
    bool: True if other has a .key attribute and self.key == other.key (exact string equality); otherwise False.
    - Edge cases:
        * If other is not an object with a .key attribute, attribute access will raise AttributeError (see Raises).
        * Comparison is case-sensitive and exact: e.g., 'C' != 'c' unless the stored strings are identical.

## Raises:
    AttributeError: If other does not have a .key attribute (e.g., other is None or an unrelated object), attribute access other.key will raise AttributeError.
    Note: The method itself does not explicitly raise exceptions; the above is the direct consequence of trying to access other.key on incompatible objects.

## State Changes:
    Attributes READ:
        - self.key
        - other.key (reads attribute on the other object)
    Attributes WRITTEN:
        - None (the method is side-effect free with respect to both operands)

## Constraints:
    Preconditions:
        - self.key must be a comparable value (the implementation expects a string as set in Key.__init__).
        - other must be an object exposing a .key attribute (preferably another Key instance or a compatible duck-typed object).
    Postconditions:
        - No mutation of self or other.
        - A boolean result is returned indicating exact equality of the key identifiers.

## Side Effects:
    - None. The method performs no I/O and does not modify other objects or global state.

### `mingus.core.keys.Key.__ne__` · *method*

## Summary:
Returns the logical negation of the Key equality comparison — i.e., indicates whether this Key's identifier differs from another object's key identifier — without modifying either object.

## Description:
Implements the inequality operator used by the != operator for Key objects. It delegates to the Key equality method and returns its logical negation, ensuring that equality and inequality remain consistent and centralized.

Known callers and lifecycle:
- Direct inequality comparisons in application logic (e.g., excluding or selecting keys).
- Collection operations or algorithms that test inequality during filtering or partitioning.
- Test assertions that verify two keys are different.

Why this is a dedicated method:
- Delegating to __eq__ avoids duplicating comparison logic and guarantees that == and != are consistent across the codebase and Python language features.

Example usage:
- Comparing two Key instances: Key("C") != Key("D") evaluates to True.
- Comparing equal keys: Key("C") != Key("C") evaluates to False.
- If compared against an incompatible object (one without a .key attribute), the comparison will raise an exception (see Raises).

See also:
- Key.__eq__ (the equality implementation this method negates; consult its documentation for exact equality semantics and error conditions).

## Args:
    other (object): The object to compare against. Expected to expose a .key attribute (typically another Key instance or a duck-typed object). No conversion or coercion is performed.

## Returns:
    bool: True when the equality comparison with other is False; False when equality is True.
    - Notes:
        * The result is a Python bool produced by applying the not operator to self.__eq__(other).
        * If self.__eq__(other) returns a non-boolean truthy/falsy value, Python's boolean coercion rules are applied when computing not <value>.

## Raises:
    AttributeError: If other does not have a .key attribute and the underlying __eq__ attempts to access other.key, that AttributeError will propagate.
    Any exception raised by self.__eq__(other) (for example, if __eq__ is changed to perform additional validation) will propagate unchanged.

## State Changes:
Attributes READ:
    - self.key (indirectly via the delegated __eq__ call)
    - other.key (indirectly via the delegated __eq__ call)
Attributes WRITTEN:
    - None (the method is side-effect free with respect to both operands and global state)

## Constraints:
Preconditions:
    - self must be a valid Key instance with an initialized self.key attribute (ensured by Key.__init__ under normal construction).
    - other should be an object exposing a .key attribute (preferably a Key instance).

Postconditions:
    - No mutation of self or other.
    - A boolean value is produced reflecting the logical negation of the equality comparison, unless an exception is raised.

## Side Effects:
    - None. The method performs no I/O and does not call external services. It only invokes self.__eq__(other), which is currently side-effect free.

