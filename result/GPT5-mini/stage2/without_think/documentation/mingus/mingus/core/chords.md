# `chords.py`

## `mingus.core.chords.triad` · *function*

## Summary:
Constructs and returns the three pitch names that form a triad (root, third, fifth) based on the supplied root note and key context.

## Description:
This function delegates the computation of the third and fifth scale degrees to the interval helpers and returns a 3-element list containing:
- the root (exactly as passed in),
- the third computed within the given key context,
- the fifth computed within the given key context.

Why this is a separate function:
- Encapsulates the single responsibility of producing a standard triad so callers do not need to call interval helpers directly or remember the specific interval offsets for a triad.
- Keeps higher-level code focused on chord progression logic while centralizing triad construction.

## Args:
    note (str):
        - Root note (pitch name) for the triad.
        - Must be in a format accepted by mingus.core.notes.is_valid_note.
        - This value is returned verbatim as the first element of the result list (no normalization performed here).
    key (str):
        - Key context used to determine scale ordering when computing intervals (passed to mingus.core.keys.get_notes internally).
        - Must be in a format accepted by mingus.core.keys.get_notes.

Interdependencies:
    - Both parameters are forwarded to intervals.third and intervals.fifth (via their call into intervals.interval). The correctness of results depends on both notes.is_valid_note(note) and keys.get_notes(key).

## Returns:
    list[str]:
        - A list of three strings: [root, third, fifth].
        - The root is the same object/string passed in as note.
        - The third and fifth are values returned by the interval helpers and will be elements from the scale ordering provided by keys.get_notes(key).
        - Guaranteed length is 3 on successful return.

## Raises:
    KeyError:
        - Raised if the root note is considered invalid by the notes module. The underlying intervals.interval raises:
          "The start note '%s' is not a valid note" % start_note
        - This exact KeyError message may propagate up through triad.
    Any exception from keys.get_notes(key) or other underlying helpers:
        - If the provided key is not recognized or those helpers raise, those exceptions propagate unchanged.
    UnboundLocalError (implementation-dependent):
        - The underlying intervals.interval searches for a scale element whose first character matches the start note's first character; if no such element is found, interval's implementation may leave a local variable uninitialized and raise UnboundLocalError. This is not raised by triad directly but can propagate.

## Constraints:
Preconditions:
    - notes.is_valid_note(note) should return True.
    - keys.get_notes(key) must accept and return a valid sequence for the provided key.
Postconditions:
    - If no exception is raised, the return value is a list of three pitch-name strings representing the triad tones in the key's note ordering.

## Side Effects:
    - None in triad itself. It performs pure computation and returns a new list. Any side effects would come from the helper modules (which are not expected to produce side effects).

## Control Flow:
flowchart TD
    Start([Start]) --> CallThird([Call intervals.third(note, key)])
    CallThird --> ThirdOK{Third computed?}
    ThirdOK -->|No (exception)| Propagate1([Propagate exception (e.g., KeyError)])
    ThirdOK -->|Yes| CallFifth([Call intervals.fifth(note, key)])
    CallFifth --> FifthOK{Fifth computed?}
    FifthOK -->|No (exception)| Propagate2([Propagate exception])
    FifthOK -->|Yes| Return([Return [note, third, fifth]])
    Propagate1 --> End([End])
    Propagate2 --> End

## Examples:
Note: returned values for third/fifth depend on the behavior of mingus.core.keys.get_notes for the supplied key. The following examples are illustrative.

Example — successful usage (illustrative):
    try:
        c_triad = triad('C', 'C')
        # Typical expected result with a conventional C major key implementation:
        # c_triad -> ['C', 'E', 'G']
        print("Triad:", c_triad)
    except KeyError as e:
        print("Invalid note:", e)
    except Exception as e:
        print("Failed to build triad:", e)

Example — handling invalid root:
    try:
        triad('H', 'C')  # 'H' is not a valid note in the common notation used by mingus
    except KeyError as e:
        # e.args[0] is likely: "The start note 'H' is not a valid note"
        print("Caught invalid note error:", e)
    except Exception as e:
        print("Other failure:", e)

## `mingus.core.chords.triads` · *function*

## Summary:
Returns the list of triads built on each degree of the given key's scale; results are cached per key to avoid recomputation.

## Description:
This function constructs a collection of triads for every scale degree in the specified key by:
- Obtaining the ordered scale notes for the key via keys.get_notes(key).
- Building a triad for each scale note by calling the triad(root_note, key) helper.
- Caching the resulting list of triads in the module-level mapping _triads_cache under the given key.

Known callers within the provided context:
- No direct callers were provided in the supplied context. Typical callers (not discovered in the provided files) include higher-level chord/progression builders, analysis utilities, or any code that needs the set of triads for a tonal key.

Why this is extracted into its own function:
- Encapsulates the pattern "for every scale degree produce its triad" and centralizes caching logic so callers do not need to repeat scale traversal, triad construction, or cache management.

## Args:
    key (str):
        - The key/tonic name or representation accepted by mingus.core.keys.get_notes.
        - Examples: "C", "G", "F#", "Bb" depending on the project's key format rules.
        - No default value; this parameter is required.
        - Interdependency: the returned list length and the specific note spellings depend entirely on keys.get_notes(key). The function assumes keys.get_notes returns an ordered iterable of pitch-name strings.

## Returns:
    list[list[str]]:
        - A list where each element is a triad produced by triad(root_note, key).
        - Each inner triad is a list of three pitch-name strings: [root, third, fifth].
        - The number of triads equals the number of scale notes returned by keys.get_notes(key) (typically 7 for diatonic keys).
        - On success the exact same list object stored in _triads_cache[key] is returned (the cached value).

## Raises:
    NoteFormatError:
        - Raised when keys.get_notes(key) deems the provided key invalid (see keys.get_notes implementation).
        - Example trigger: keys.get_notes raises NoteFormatError("unrecognized format for key '%s'" % key).

    Any exception raised by triad(root_note, key):
        - triad may raise KeyError for invalid root notes or other exceptions propagated from its interval helpers; those exceptions propagate through triads unchanged.

    Any other exception from keys.get_notes or underlying helpers:
        - Propagated unchanged.

## Constraints:
Preconditions:
    - The global cache variable _triads_cache must exist and be indexable by keys (behaves like a dict); the implementation assumes storing results by key is allowed.
    - key must be a format accepted by keys.get_notes.

Postconditions:
    - If no exception is raised, _triads_cache[key] will contain the returned list of triads.
    - Subsequent calls with the same key will return the cached value without recomputing triads.

## Side Effects:
    - Mutates module-global mapping _triads_cache by storing the computed list under _triads_cache[key].
    - No I/O, network access, or external persistent storage is performed by triads itself. Any side effects arise only from called helpers, which in normal usage do not produce side effects.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckCache{key in _triads_cache?}
    CheckCache -->|Yes| ReturnCached([return _triads_cache[key]])
    CheckCache -->|No| GetScale([notes = keys.get_notes(key)])
    GetScale --> GetScaleError{keys.get_notes raised?}
    GetScaleError -->|Yes| PropagateKeyError([propagate NoteFormatError or other])
    GetScaleError -->|No| MapTriads([res = [triad(n, key) for n in notes]])
    MapTriads --> TriadError{triad(n,key) raised for any n?}
    TriadError -->|Yes| PropagateTriadError([propagate triad exception])
    TriadError -->|No| Cache([_triads_cache[key] = res])
    Cache --> Return([return res])

## Examples:
Example — typical usage and success handling:
    try:
        all_triads = triads("C")
        # Typical expected result in a conventional diatonic implementation:
        # [
        #   ['C', 'E', 'G'],
        #   ['D', 'F', 'A'],
        #   ['E', 'G', 'B'],
        #   ['F', 'A', 'C'],
        #   ['G', 'B', 'D'],
        #   ['A', 'C', 'E'],
        #   ['B', 'D', 'F']
        # ]
        print("Triads for C:", all_triads)
    except Exception as exc:
        print("Failed to compute triads:", exc)

Example — invalid key handling:
    try:
        triads("InvalidKey")
    except NoteFormatError as e:
        # keys.get_notes will raise NoteFormatError for an unrecognized key format
        print("Bad key:", e)

Example — invalid internal note handling (propagated from triad):
    try:
        triads("C")  # if triad() or its helpers cannot handle some scale note, that exception will bubble up
    except KeyError as e:
        print("Invalid note encountered while building a triad:", e)

## `mingus.core.chords.major_triad` · *function*

## Summary:
Returns the three notes of a major triad built on the given root note: the root, its major third, and its perfect fifth.

## Description:
This function constructs a major triad by delegating interval calculation to the intervals module:
- It returns the root note unchanged and computes the major third and perfect fifth relative to the root using intervals.major_third and intervals.perfect_fifth.
- Known callers: No explicit call sites were discovered in the repository scan available to this task. Typical call contexts are chord-generation utilities, higher-level harmony routines, or user code that needs a spelled major triad from a single root note (for example, constructing chord progressions or rendering chord voicings).
- Why this is a separate function: It captures the single responsibility of producing a conventional major triad (root, 3rd, 5th) in the correct spelled form (respecting accidentals relative to the root). Extracting this logic keeps chord-construction code concise and centralizes the use of interval utilities so spelling and accidental adjustments are handled consistently.

## Args:
    note (str): The root note in string form. Must be non-empty; the first character is the note letter (A–G) and any subsequent characters are accidentals using '#' for sharp and 'b' for flat (for example, 'C', 'C#', 'Db', 'F##', 'Ebb').
    - Allowed characters: first character must be one of the natural note letters (A,B,C,D,E,F,G). Subsequent characters, if present, must be only '#' or 'b'.
    - Interdependencies: The correctness of the returned triad depends on the input being a single note string; passing already-spelled chord lists or non-string types is not supported.

## Returns:
    list[str]: A 3-element list of strings [root, major_third, perfect_fifth].
    - root: the exact value passed in the note parameter (no normalization is performed by this function).
    - major_third: the spelled major third above the root (accidentals adjusted so the interval between root and this note is a major third).
    - perfect_fifth: the spelled perfect fifth above the root (accidentals adjusted similarly).
    - Examples:
        - major_triad("C") -> ["C", "E", "G"]
        - major_triad("C#") -> ["C#", "E#", "G#"] (E# is the correctly spelled major third above C#)
    - Edge returns: If underlying interval utilities attempt to produce accidentals beyond typical enharmonic ranges, they normalize accidentals via augment/diminish logic; the function will still return strings but the exact accidental spelling follows the intervals module's rules.

## Raises:
    NoteFormatError: Raised when the provided note string is not a valid single-note format. This arises from lower-level validation/translation routines used by the interval functions (for example, when a utility attempts to inspect or convert the note and finds an unknown format).
    Other exceptions from lower layers: Errors raised inside the intervals or notes modules (for example, format or range errors in helper functions) may propagate; this function does not catch them. These are not raised directly here but may occur when inputs violate assumptions (non-string types, empty strings, or characters outside the allowed set).

## Constraints:
    Preconditions:
    - Caller must supply a single-note string as described above (first character in A–G; further characters only '#' or 'b').
    - The environment must have the intervals and notes utilities available (this is true inside the same package).
    Postconditions:
    - The returned list has exactly three string elements representing spelled notes.
    - The second and third elements are adjusted so their spelled interval distances from the root correspond to a major third and perfect fifth respectively.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not call external services. All work is pure computation using helper utilities; any side effects would come from those utilities (none are expected for standard note computations).

## Control Flow:
flowchart TD
    A[call major_triad(note)] --> B{note is given}
    B --> C[call intervals.major_third(note)]
    C --> D{intervals logic may loop}
    D --> D1[augment/diminish until interval matches] --> E
    C --> E[receive spelled_major_third]
    B --> F[call intervals.perfect_fifth(note)]
    F --> G{intervals logic may loop}
    G --> G1[augment/diminish until interval matches] --> H
    F --> H[receive spelled_perfect_fifth]
    E --> I[return [note, spelled_major_third, spelled_perfect_fifth]]
    H --> I

Notes:
- The loops mentioned occur inside the augment_or_diminish_until_the_interval_is_right helper used by the interval functions: that helper repeatedly augments or diminishes the candidate interval note until the measured semitone distance matches the target interval.

## Examples:
- Successful usage:
    - Input: "C"
      - major_triad("C") returns ["C", "E", "G"]
    - Input: "F#"
      - major_triad("F#") returns ["F#", "A#", "C#"] (A# is the major third above F#)
- Error handling example:
    - If input is malformed:
        - Example input: "H" (invalid natural note)
        - Typical handling by a caller:
            try:
                triad = major_triad("H")
            except NoteFormatError as e:
                # handle invalid input (notify user, log, raise further, etc.)
                pass
    - The exact exception instance and message are produced by the lower-level validation routines (NoteFormatError).

## `mingus.core.chords.minor_triad` · *function*

## Summary:
Constructs and returns the three pitch names that form a minor triad built on the provided root pitch: root, minor third above the root, and perfect fifth above the root.

## Description:
Known callers:
- None found in the supplied context. This function is intended as a small, reusable building block for chord-creation utilities elsewhere (for example: functions that enumerate chord tones, assemble chord objects for display, or generate harmonic analysis).

Why this logic is extracted:
- Building a minor triad is a common, self-contained musical operation that combines two interval computations. Encapsulating it prevents duplication, centralizes error propagation from interval parsing/computation, and provides a single clear entrypoint for requesting minor triads.

## Args:
    note (str):
        The root pitch/name for the triad. This function forwards the value unchanged to the interval helpers intervals.minor_third and intervals.perfect_fifth, so the allowed formats are those accepted by those helpers (commonly a note name string such as "C", "C#", "Bb"; octave qualifiers may be supported depending on the intervals/notes module).
        - Required.
        - No local validation is performed here; malformed input will be handled (or rejected) by the interval helpers.

## Returns:
    list[str]:
        A list of three strings in this exact order:
          1. The original root note argument (returned verbatim).
          2. The string returned by intervals.minor_third(note) — the minor third above the root.
          3. The string returned by intervals.perfect_fifth(note) — the perfect (major) fifth above the root.
        - On successful completion the list length is always 3.
        - Exact spelling/accidental choices (e.g., "D#" vs "Eb") and inclusion of octave numbers depend on the behavior of the intervals helpers.

## Raises:
    - Any exception raised by intervals.minor_third or intervals.perfect_fifth will propagate through this function.
    - Typical exceptions coming from note parsing/formatting in the lower-level modules include:
        * mingus.core.mt_exceptions.NoteFormatError
        * mingus.core.mt_exceptions.FormatError
      (These exception classes are imported into the module and are commonly used by note/interval parsing utilities; callers should be prepared to catch them if input may be malformed.)

## Constraints:
Preconditions:
    - The caller must supply a non-empty string representing a pitch in a format the intervals helpers accept.
    - The intervals module (and its minor_third / perfect_fifth implementations) must be available in the runtime environment.

Postconditions:
    - If no exception is raised, the function returns a length-3 list as described in Returns.
    - No external state is modified.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state; it only calls pure interval helper functions.

## Control Flow:
flowchart TD
    Start --> CallMinorThird
    CallMinorThird --> MinorThirdOK{minor_third succeeded?}
    MinorThirdOK -- yes --> CallPerfectFifth
    MinorThirdOK -- no --> PropagateError1[Propagate exception to caller]
    CallPerfectFifth --> PerfectFifthOK{perfect_fifth succeeded?}
    PerfectFifthOK -- yes --> BuildList[Build [root, minor_third, perfect_fifth]]
    BuildList --> ReturnList[Return result]
    PerfectFifthOK -- no --> PropagateError2[Propagate exception to caller]

## Examples:
Example 1 — typical usage:
    from mingus.core.chords import minor_triad

    triad = minor_triad("C")
    # Typical expected result (given standard interval spellings):
    # ["C", "Eb", "G"]

Example 2 — handling invalid input:
    from mingus.core.chords import minor_triad
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        triad = minor_triad("H#")  # malformed or unsupported note name
    except (NoteFormatError, FormatError) as e:
        # Handle or report invalid note format
        print("Invalid note format:", e)

Notes and implementation hints:
    - This function intentionally defers note-format validation and accidental/octave spelling rules to the intervals and notes modules; callers that need normalized spellings or specific octave handling should call the appropriate normalization utilities prior to invoking this function.
    - The returned list preserves the original root argument as its first element; if you need a normalized root spelling, normalize the input before calling.

## `mingus.core.chords.diminished_triad` · *function*

## Summary:
Constructs and returns the three pitch names that form a diminished triad built on the supplied root (root, minor third, diminished fifth).

## Description:
This function composes lower-level interval computations from the intervals module to produce a diminished triad. It returns a 3-element list: the supplied root note unchanged, the minor third above it (computed via intervals.minor_third), and the minor (diminished) fifth above it (computed via intervals.minor_fifth).

Known callers within the codebase:
    - No direct callers were found in the provided graph. It is intended for use by chord-building utilities, music-theory helpers, or any code that needs an explicit enumeration of the three pitch names for a diminished triad.

Rationale for extracting this logic:
    - Separation of concerns: interval calculation and chord construction are distinct responsibilities. This function keeps chord definitions declarative and reuses the interval computations, avoiding duplicated interval logic across the codebase.

## Args:
    note (sequence-like): The root pitch. Expected to be in a format accepted by the intervals module (commonly a string such as 'C', 'C#', 'Eb', or including octave like 'C4').
        - Practical requirement: the intervals.* helpers access note[0] (they index the argument), so `note` must be indexable and non-empty.
        - No normalization or validation is performed here; the function forwards the value directly to the intervals functions.

## Returns:
    list: A three-element list [root, minor_third, minor_fifth].
        - root: exactly the same object/value provided as the `note` argument (no copy or normalization).
        - minor_third: the return value of intervals.minor_third(note).
        - minor_fifth: the return value of intervals.minor_fifth(note).
        - Typical concrete types: these returned elements are typically strings representing pitches (e.g., 'Eb'), but the exact type/format is determined by the intervals module.

## Raises:
    - This function performs no local validation and does not explicitly raise exceptions.
    - Exceptions produced by the delegated calls (intervals.minor_third or intervals.minor_fifth) will propagate to the caller. In this file's context, FormatError and NoteFormatError are imported and are plausible propagated exception types if the underlying utilities raise them; callers should handle or translate propagated exceptions as appropriate.

## Constraints:
    Preconditions:
        - `note` must be indexable and non-empty because the intervals helper functions access note[0].
        - The value must be valid in the intervals module's expected notation (e.g., valid pitch names); otherwise the intervals functions will raise errors.

    Postconditions:
        - On successful return, the output is a list of length 3 whose second and third elements are computed by the intervals module.
        - No global state is modified and no I/O is performed.

## Side Effects:
    - None local to this function: no file, network, stdout operations, and no mutation of external/global state.
    - Any side effects originate from the intervals module (if any), and will be observable as propagated behavior.

## Control Flow:
flowchart TD
    Start --> Validate_indexable
    Validate_indexable -->|not indexable or empty| PropagateError_InvalidInput
    Validate_indexable -->|indexable| Call_minor_third
    Call_minor_third -->|exception| PropagateError_from_minor_third
    Call_minor_third -->|success| Call_minor_fifth
    Call_minor_fifth -->|exception| PropagateError_from_minor_fifth
    Call_minor_fifth -->|success| Return_list
    PropagateError_InvalidInput --> End
    PropagateError_from_minor_third --> End
    PropagateError_from_minor_fifth --> End
    Return_list --> End

## Examples:
    Example 1 — typical usage (happy path):
        Input: 'C'
        Expected (typical) return: ['C', 'Eb', 'Gb']
        Note: exact enharmonic spelling (e.g., 'Gb' vs 'F#') and octave notation depend on the intervals module's formatting rules.

    Example 2 — handling invalid input:
        from mingus.core.mt_exceptions import FormatError, NoteFormatError
        try:
            triad = diminished_triad(bad_note)
        except (FormatError, NoteFormatError) as e:
            # Translate or surface a user-friendly error message
            handle_invalid_note(e)
        except Exception:
            # Generic fallback for unexpected exceptions
            raise

    Real integration scenario:
        - A chord API receives ("dim", "A") and calls diminished_triad('A') to get ['A', 'C', 'Eb'] (subject to the intervals module's naming conventions), then formats and returns that list to the caller.

## `mingus.core.chords.augmented_triad` · *function*

## Summary:
Produces the three-note augmented triad built on the given root note: [root, major third, raised fifth].

## Description:
This function constructs an augmented triad from a single pitch name by (1) computing the major third above the root, (2) computing the (perfect) fifth above the root and then augmenting that fifth (raising it by a semitone).

Known callers within the codebase:
    - No direct callers were discovered during analysis of this component. It is intended to be used by higher-level chord-building utilities or by user code that needs an augmented triad representation.

Why this logic is separate:
    - Encapsulates the small, well-defined responsibility of producing an augmented triad so callers do not need to duplicate the sequence of interval computations and accidental manipulation. It keeps chord-construction semantics (major third + augmented fifth) expressed in one place.

## Args:
    note (str): The root pitch name. Expected to be a single note name in the project's note format (examples: "C", "C#", "Db", "Bb", "F#"). Must be non-empty and acceptable to the project's interval and note helper functions.

    - No default value.
    - There are no multiple-parameter interdependencies; the single parameter is passed to helper functions that validate and format the note.

## Returns:
    list[str]: A 3-element list of pitch names:
        [root, major_third, augmented_fifth]

    - root: exactly the input string (no normalization performed by this function).
    - major_third: the result of intervals.major_third(note) — the pitch a major third above the root (string).
    - augmented_fifth: produced by calling intervals.major_fifth(note) and then notes.augment(...) on that result; i.e. the fifth raised by one semitone (string).

    Edge / special return cases:
        - If intervals.major_fifth(note) returns a note ending with "b" (a flat), notes.augment will remove that trailing "b" (turning a flat into its natural), otherwise notes.augment appends "#" (sharp). Thus augmenting a flat produces a natural, augmenting a natural produces a sharp.

## Raises:
    - Any exception raised by intervals.major_third(note) or intervals.major_fifth(note) will propagate. In this codebase those helpers may raise:
        - mingus.core.mt_exceptions.NoteFormatError: when the input note string is not a valid/recognizable note.
        - mingus.core.mt_exceptions.FormatError: for other format-related errors in interval computation.
    - Any other runtime exceptions raised by the helper functions (e.g., IndexError on malformed inputs) will also propagate because this function does not catch exceptions.

## Constraints:
    Preconditions:
        - The input must be a non-empty string representing a pitch in the project's expected note format.
        - The intervals.* helpers must accept the given note and be able to compute intervals from it.

    Postconditions:
        - On successful return, a list of three pitch-name strings is returned as described in Returns.
        - The input value is not mutated (it is returned unchanged as the first element).

## Side Effects:
    - This function has no I/O, no network calls, and does not mutate global state.
    - It purely composes other pure helper functions; side effects (if any) would come from those helpers, but none are expected.

## Control Flow:
flowchart TD
    Start --> ComputeMajorThird
    ComputeMajorThird --> ComputeMajorFifth
    ComputeMajorFifth --> AugmentFifth
    AugmentFifth --> ReturnTriad
    ComputeMajorThird[Compute intervals.major_third(note)]
    ComputeMajorFifth[Compute intervals.major_fifth(note)]
    AugmentFifth[Call notes.augment(...) on the fifth]
    ReturnTriad[Return [note, major_third, augmented_fifth]]

## Examples:
    Basic usage:
        try:
            triad = augmented_triad("C")
            # triad is ["C", "E", "G#"]
        except (NoteFormatError, FormatError) as e:
            # handle invalid input or format problems
            raise

    Handling malformed input:
        try:
            augmented_triad("")  # likely to raise NoteFormatError or FormatError
        except Exception as e:
            # validate or report user-provided note string
            pass

Notes:
    - The exact accidentals returned for thirds/fifths depend on the interval helper implementation and its accidental-resolution rules; this function does not perform any additional normalization beyond calling those helpers and augmenting the fifth.

## `mingus.core.chords.seventh` · *function*

## Summary:
Returns the four pitch names that make up a seventh chord (root, third, fifth, seventh) constructed in the supplied key context.

## Description:
Known callers within the codebase:
    - None present in the provided module-level snapshots. This function is part of the public chord helpers in mingus.core.chords and intended for use by higher-level chord/analysis code or user-level code that needs a standard seventh chord.

Why this logic is a separate function:
    - Encapsulates the assembly of a seventh chord by delegating third/fifth computation to triad and the seventh to intervals.seventh, so callers can obtain a fully-assembled seventh chord with a single call.
    - Responsibility boundary: this function performs list assembly only. It does not normalize or alter the input note string — the root is returned verbatim because triad returns the root exactly as passed in.

## Args:
    note (str):
        - Root note (pitch name) for the chord.
        - Must be in a format accepted by mingus.core.notes.is_valid_note (examples: "C", "G#", "Bb" depending on project conventions).
        - This string is returned verbatim as the first element of the result list (no normalization performed by this function).
    key (str):
        - Key context used when computing scale degrees for the third, fifth and seventh (forwarded to the underlying interval helpers and keys.get_notes).
        - Must be in a format accepted by mingus.core.keys.get_notes.

Interdependencies:
    - triad(note, key) produces [root, third, fifth] and returns the root exactly as provided.
    - intervals.seventh(note, key) computes the seventh degree relative to the root in the given key.
    - The correctness depends on notes.is_valid_note(note) and keys.get_notes(key) as used by these helpers.

## Returns:
    list[str]:
        - A list of four pitch-name strings: [root, third, fifth, seventh].
        - The first element is exactly the input note string.
        - The remaining three elements are produced by triad and intervals.seventh and will be pitch names derived from the scale ordering provided by keys.get_notes(key).
        - On success the returned list has length 4.

## Raises:
    KeyError:
        - Propagated if the underlying interval or note validation helpers determine the root note is invalid. The original KeyError message from the helper will be propagated unchanged.
    Any exception raised by keys.get_notes(key) or other underlying helpers:
        - Propagated unchanged.
    UnboundLocalError (possible):
        - If an internal search in the interval helpers fails to initialize a local variable, an UnboundLocalError could propagate. This originates in helper implementations, not in this function.

## Constraints:
Preconditions:
    - notes.is_valid_note(note) is expected to be True.
    - keys.get_notes(key) must accept the provided key and return a valid note ordering.

Postconditions:
    - If no exception is raised, the returned list contains four pitch-name strings representing the seventh chord anchored at the supplied root, with the root preserved verbatim.

## Side Effects:
    - None. This function performs pure computation and returns a new list. Any side effects would come from underlying modules (not expected for these helpers).

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriad([Call triad(note, key)])
    CallTriad --> TriadOK{Triad computed?}
    TriadOK -->|No (exception)| Propagate1([Propagate exception and return])
    TriadOK -->|Yes| CallSeventh([Call intervals.seventh(note, key)])
    CallSeventh --> SeventhOK{Seventh computed?}
    SeventhOK -->|No (exception)| Propagate2([Propagate exception and return])
    SeventhOK -->|Yes| Concat([Concatenate triad + [seventh]])
    Concat --> Return([Return 4-element list])
    Propagate1 --> End([End])
    Propagate2 --> End

## Examples:
Example — typical successful usage:
    try:
        chord = seventh('C', 'C')
        # With a conventional C major key implementation, a typical result would be:
        # chord -> ['C', 'E', 'G', 'B']
        print("C7 chord tones:", chord)
    except Exception as e:
        print("Failed to build chord:", e)

Example — root string preserved (no normalization):
    # If the codebase accepts both 'C' and 'c' but triad returns the root verbatim,
    # this function will preserve the exact input form:
    chord = seventh('c', 'C')  # first element will be 'c' if triad returns it unchanged

Example — handling an invalid root note:
    try:
        seventh('H', 'C')  # 'H' is not valid in common notation used by mingus
    except KeyError as e:
        # Underlying helper likely raised: "The start note 'H' is not a valid note"
        print("Invalid note error:", e)
    except Exception as e:
        print("Other failure:", e)

## `mingus.core.chords.sevenths` · *function*

## Summary:
Computes and returns the diatonic seventh chords for every scale degree of the supplied key, caching the result for subsequent calls.

## Description:
Known callers within the codebase:
    - No internal direct callers were found in the provided snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for use by higher-level chord/analysis code or by user code that needs all seventh chords in a given key.

Why this logic is extracted:
    - Responsibility boundary: this function orchestrates three responsibilities — obtaining the scale notes for the key, assembling a seventh chord for each scale degree (by calling the helper seventh which itself delegates to triad and intervals helpers), and caching the result. Extracting it keeps cache management and bulk chord assembly separate from the single-chord helpers and avoids recomputing the same set of seventh chords repeatedly.

## Args:
    key (str):
        - The key context (e.g., "C", "G", "F#", "Bb") used to compute the scale degrees.
        - Must be a key format accepted by mingus.core.keys.get_notes.
        - No default value: this parameter is required.
        - Interdependencies: validity and semantics depend on the keys module (keys.get_notes may raise NoteFormatError on invalid formats).

## Returns:
    list[list[str]]:
        - A list whose length equals the number of notes returned by keys.get_notes(key) (typically 7 for diatonic keys).
        - Each element is a list of four pitch-name strings representing a seventh chord built on that scale degree: [root, third, fifth, seventh].
        - The function returns the exact cached list object when a cached entry exists; when computed, the newly created list is stored in the module-level cache and returned.
        - Example (conventional C major output): 
            [
                ['C','E','G','B'],
                ['D','F','A','C'],
                ['E','G','B','D'],
                ['F','A','C','E'],
                ['G','B','D','F'],
                ['A','C','E','G'],
                ['B','D','F','A']
            ]

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Raised when keys.get_notes(key) rejects the provided key format. This originates in keys.get_notes and is propagated unchanged.
    Any exception raised by the underlying seventh/triad/intervals helpers:
        - If the helper that constructs a single seventh chord raises (for example due to an invalid note), that exception propagates unchanged.
    (No exceptions are raised directly by this function beyond those propagated from callees.)

## Constraints:
Preconditions:
    - key must be a string in a format accepted by keys.get_notes.
    - The module-level cache object (_sevenths_cache) must be available in the module namespace (expected in the containing module).
Postconditions:
    - On successful return, _sevenths_cache[key] will contain the returned list.
    - The returned value is the same object stored in the cache; subsequent calls with the same key will return the cached object (identity equality).

## Side Effects:
    - Mutates module-level state: writes to the global cache mapping _sevenths_cache[key] when a cache miss occurs.
    - Important: the function returns the cached list object. If a caller mutates the returned list or its nested chord lists, those mutations will affect the cached value and therefore future callers of this function for the same key.
    - No I/O (files, network) is performed by this function itself.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckCache{key in _sevenths_cache?}
    CheckCache -->|Yes| ReturnCached([Return _sevenths_cache[key]])
    CheckCache -->|No| GetScale([Call keys.get_notes(key)])
    GetScale -->|raises exception| Propagate1([Propagate exception])
    GetScale --> BuildList([For each scale note x: call seventh(x, key)])
    BuildList -->|any call raises| Propagate2([Propagate exception])
    BuildList --> Store([Store result in _sevenths_cache[key]])
    Store --> ReturnNew([Return computed list])
    ReturnCached --> End([End])
    ReturnNew --> End

## Examples:
Typical successful usage (C major):
    try:
        diatonic_sevenths = sevenths('C')
        # diatonic_sevenths is typically:
        # [
        #   ['C','E','G','B'],
        #   ['D','F','A','C'],
        #   ['E','G','B','D'],
        #   ['F','A','C','E'],
        #   ['G','B','D','F'],
        #   ['A','C','E','G'],
        #   ['B','D','F','A']
        # ]
    except Exception as e:
        # Handle invalid key or other underlying errors
        print("Failed to compute sevenths:", e)

Example — cache behavior and mutation caveat:
    chords1 = sevenths('C')
    chords2 = sevenths('C')
    assert chords1 is chords2  # same object (cached)
    chords1[0][0] = 'C_mod'    # mutates cached data visible to all callers

Example — invalid key:
    try:
        sevenths('InvalidKeyName')  # keys.get_notes will raise NoteFormatError
    except NoteFormatError as e:
        print("Invalid key:", e)

## `mingus.core.chords.major_seventh` · *function*

## Summary:
Constructs a spelled major-seventh chord from a single root note, returning the root plus its major third, perfect fifth, and major seventh as four spelled note strings.

## Description:
This function composes two responsibilities handled elsewhere: it reuses major_triad to produce the root, major third and perfect fifth, and calls the intervals module to compute the spelled major seventh. The result is a four-note list representing a conventional major-seventh chord (e.g., ["C","E","G","B"]).
- Known callers: none discovered in the scanned repository; typical use cases are chord-generation utilities, harmony rendering, MIDI/notation exporters, or user code that builds chord voicings from a single note.
- Why separate: It centralizes the common pattern "triad + seventh" so callers need not recompute triads or individually request the major seventh. This keeps chord construction concise and ensures consistent accidental/spelling rules by delegating to the intervals utilities.

## Args:
    note (str): Root note string.
        - Required format: a single-note string whose first character is a natural note letter (A–G) and whose optional subsequent characters are accidentals using '#' (sharp) or 'b' (flat). Examples: "C", "C#", "Db", "F##", "Ebb".
        - The function does not normalize or change the root string; the exact root string provided is returned as the first element.
        - Interdependencies: The function assumes the input is a valid, non-empty single-note string; supplying other types or an empty string will raise exceptions propagated from the lower-level utilities or Python itself.

## Returns:
    list[str]: A 4-element list [root, major_third, perfect_fifth, major_seventh]
    - root: the original note string passed in.
    - major_third and perfect_fifth: produced by major_triad and spelled to represent a major third (4 semitones) and perfect fifth (7 semitones) above the root.
    - major_seventh: produced by intervals.major_seventh and spelled so that its distance from root is 11 semitones (the major seventh).
    - Examples:
        - major_seventh("C") -> ["C", "E", "G", "B"]
        - major_seventh("C#") -> ["C#", "E#", "G#", "B#"]
    - Edge-case behavior: The exact accidental spellings depend on the intervals module's augment/diminish logic; the function will always return four strings when called with a valid input.

## Raises:
    NoteFormatError:
        - Condition: The provided note string is malformed (invalid note letter or invalid accidental characters) or lower-level validation routines fail to parse the note.
        - Origin: Raised by major_triad or the intervals/notes utilities during parsing/validation.
    FormatError:
        - Condition: The intervals utilities encounter a formatting or internal interval construction error.
        - Origin: Raised by intervals.major_seventh or related helpers.
    IndexError:
        - Condition: The provided note is an empty string ("").
        - Reason: intervals.major_seventh inspects note[0] (the first character) and will raise IndexError on empty input.
    TypeError:
        - Condition: The provided note is not a string (e.g., None, list, int) or otherwise not subscriptable/compatible with the downstream utilities.
        - Reason: major_triad and intervals functions expect string inputs; passing incompatible types will raise TypeError or other built-in exceptions from string operations.

## Constraints:
    Preconditions:
    - The caller must pass a non-empty single-note string following the expected format (first char A–G, subsequent chars only '#' or 'b').
    - The intervals and notes utilities must be present and correctly implemented in the same package.
    Postconditions:
    - Returns exactly four strings where the 2nd, 3rd, and 4th elements are spelled to correspond to 4, 7, and 11 semitone intervals above the root respectively (subject to the intervals module's spelling rules).

## Side Effects:
    - None local to this function. It performs no I/O, does not modify global state, and calls only pure computation helpers. Any side effects would originate from lower-level utilities (not expected for normal note/interval computations).

## Control Flow:
flowchart TD
    A[Call major_seventh(note)] --> B{Is note a non-empty string?}
    B -- No (empty string) --> C[intervals.major_seventh reads note[0] -> IndexError raised]
    B -- No (non-string) --> D[major_triad/intervals operations -> TypeError or other]
    B -- Yes --> E[Call major_triad(note) -> [root, major_third, perfect_fifth]]
    E --> F[Call intervals.major_seventh(note) -> spelled_major_seventh]
    F --> G{intervals may augment/diminish to match 11 semitones}
    G --> H[Receive spelled_major_seventh]
    H --> I[Return [root, major_third, perfect_fifth, spelled_major_seventh]]
    E --> J[Downstream parsing/format errors? -> raise NoteFormatError or FormatError]

## Examples:
- Happy path:
    try:
        chord = major_seventh("C")
        # chord == ["C", "E", "G", "B"]
    except (NoteFormatError, FormatError, IndexError, TypeError) as e:
        # handle or report unexpected failure
        raise

- Handling malformed root:
    try:
        chord = major_seventh("H")  # invalid natural note
    except NoteFormatError as e:
        # notify user or log the invalid input
        log_invalid_input(e)

- Empty string danger:
    try:
        chord = major_seventh("")  # will raise IndexError inside intervals.major_seventh
    except IndexError:
        # validate input before calling or surface a clearer message to callers
        raise ValueError("root note must be a non-empty single-note string")

## `mingus.core.chords.minor_seventh` · *function*

## Summary:
Returns the four pitch names that form a minor seventh chord built on the provided root: the root, the minor third, the perfect fifth, and the minor seventh.

## Description:
Known callers:
- None found in the supplied context. This function is a small, reusable chord-construction utility intended for use by higher-level chord enumeration, rendering, or analysis routines.

Why this logic is extracted:
- Building a minor seventh chord is a common, self-contained musical operation that composes two interval computations (a minor triad and a minor seventh above the root). Extracting it avoids duplication, centralizes error propagation from the underlying interval helpers, and provides a single, easy-to-use helper for callers that need the four chord tones.

## Args:
    note (str):
        The root pitch/name for the chord.
        - Required.
        - The value is forwarded unchanged to the underlying helpers:
            * minor_triad(note) — produces the root, minor third, and perfect fifth.
            * intervals.minor_seventh(note) — produces the pitch that is a minor seventh above the root.
        - Accepted formats and validation rules are those enforced by the intervals/notes helpers (commonly note names like "C", "C#", "Bb"; octave qualifiers may be supported). This function does not perform additional validation.

## Returns:
    list[str]:
        A list of four strings in this exact order:
          1. The original root note argument (returned verbatim).
          2. The string returned by intervals.minor_third(note) — the minor third above the root.
          3. The string returned by intervals.perfect_fifth(note) — the perfect fifth above the root.
          4. The string returned by intervals.minor_seventh(note) — the minor seventh above the root.
        - On successful completion the list length is always 4.
        - Exact spelling/accidental choices (e.g., "D#" vs "Eb") and inclusion of octave numbers depend on the behavior of the intervals helpers.

## Raises:
    - Any exception raised by minor_triad or intervals.minor_seventh will propagate unchanged to the caller.
    - Typical exceptions coming from lower-level note/interval parsing utilities include:
        * mingus.core.mt_exceptions.NoteFormatError
        * mingus.core.mt_exceptions.FormatError

## Constraints:
Preconditions:
    - The caller must supply a non-empty string representing a pitch in a format accepted by the intervals/notes helpers.
    - The intervals and chords utilities must be available in the runtime environment.

Postconditions:
    - If no exception is raised, the function returns a list[str] of length 4 as described in Returns.
    - No external state is modified by this function.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state; it only calls pure helper functions.

## Control Flow:
flowchart TD
    Start --> CallMinorTriad
    CallMinorTriad --> MinorTriadOK{minor_triad succeeded?}
    MinorTriadOK -- no --> PropagateError1[Propagate exception to caller]
    MinorTriadOK -- yes --> CallMinorSeventh
    CallMinorSeventh --> MinorSeventhOK{intervals.minor_seventh succeeded?}
    MinorSeventhOK -- no --> PropagateError2[Propagate exception to caller]
    MinorSeventhOK -- yes --> AppendSeventh[Append minor seventh to triad list]
    AppendSeventh --> ReturnList[Return list of 4 pitches]
    ReturnList --> End

## Examples:
Example 1 — typical usage:
    from mingus.core.chords import minor_seventh

    chord = minor_seventh("C")
    # Typical expected result (given standard interval spellings from the intervals helpers):
    # ["C", "Eb", "G", "Bb"]

Example 2 — handling invalid input:
    from mingus.core.chords import minor_seventh
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        chord = minor_seventh("H#")  # malformed or unsupported note name
    except (NoteFormatError, FormatError) as e:
        # Handle or report invalid note format
        print("Invalid note format:", e)

Notes and implementation hints:
    - This function delegates all note-format validation and interval spelling choices to the minor_triad and intervals.minor_seventh helpers; callers that require normalized spellings or specific octave handling should normalize the input before calling.
    - Reimplementation: produce the minor triad list for the root, call the intervals helper to compute the minor seventh above the root, append that single pitch string to the triad list, and return the resulting 4-element list. Ensure exceptions from helpers propagate unchanged.

## `mingus.core.chords.dominant_seventh` · *function*

## Summary:
Builds a dominant seventh chord from a single root note and returns its four spelled notes (major triad + minor seventh).

## Description:
This function composes a dominant seventh chord by combining the spelled notes of a major triad built on the given root with the spelled minor seventh above the same root. It delegates triad construction to the chord utility that returns [root, major third, perfect fifth] and uses the intervals module to compute the spelled minor seventh.

Known callers:
- No explicit call sites were discovered in the available repository scan. Typical use cases include chord-generation utilities, harmony routines, MIDI/notation rendering code, or user-facing APIs that produce spelled chord notes from a single root note.

Why this is separate:
- The function captures a small, well-defined responsibility (constructing a dominant seventh chord) and centralizes the combination logic and interval calls. Keeping this as a single function avoids duplicating the pattern of "major triad + minor seventh" throughout the codebase and ensures consistent spelled-interval behavior by reusing existing interval utilities.

## Args:
    note (str): The root note as a single-note string.
        - Required format: non-empty string where the first character is a natural note letter A–G and any subsequent characters (if present) are accidentals '#' for sharps or 'b' for flats (examples: "C", "C#", "Db", "F##", "Ebb").
        - The function does not perform normalization of the root; the exact string passed is returned as the first element of the output list.
        - The function expects an indexable string (the intervals.minor_seventh implementation accesses note[0]), so passing an empty string or a non-string type will violate preconditions.

## Returns:
    list[str]: A 4-element list of spelled note strings in the following order:
        - index 0: root (exact string passed in)
        - index 1: spelled major third above root
        - index 2: spelled perfect fifth above root
        - index 3: spelled minor seventh above root
    - The second and third elements come from the major_triad helper. The fourth element is produced by intervals.minor_seventh.
    - Spelling and accidentals follow the rules implemented by the intervals utilities; e.g., major_triad("C") -> ["C","E","G"], minor seventh above "C" -> "Bb", so dominant_seventh("C") -> ["C","E","G","Bb"].
    - Edge cases: If the underlying interval utilities return unusual augmentations/diminutions (rare accidentals beyond simple sharps/flats), those spelled forms are returned unchanged.

## Raises:
    NoteFormatError:
        - Raised when the provided note string is not a valid single-note format (for example, invalid first character, invalid accidental characters, or empty string). This arises from validation/translation routines used by the interval functions called (major_triad and intervals.minor_seventh).
    Other exceptions from lower layers:
        - Errors raised inside the intervals or notes modules (for example, FormatError or other propagation from augment/diminish helpers) may propagate. The function does not catch these exceptions; callers should handle them if inputs may be invalid.

## Constraints:
    Preconditions:
        - `note` must be a non-empty string whose first character is one of 'A'..'G'.
        - Any accidentals after the letter must be only '#' or 'b' characters.
        - The package environment must provide the intervals and chord utilities (true inside the same library).
    Postconditions:
        - The function returns a list of exactly four strings.
        - The returned notes represent a spelled major triad built on the root followed by the spelled minor seventh above the root (interval distances correspond to major third, perfect fifth, and minor seventh respectively, as enforced by the intervals utilities).

## Side Effects:
    - None. The function performs pure computation and delegates to helper utilities; it does not perform I/O, mutate global state, or call external services. Any side effects would come from lower-level utilities (none are expected for standard note computations).

## Control Flow:
flowchart TD
    A[call dominant_seventh(note)] --> B{note provided? (non-empty string expected)}
    B --> C[call major_triad(note)]
    C --> D{major_triad validates note}
    D --> D1[if invalid -> raise NoteFormatError/propagate lower-layer exception]
    D --> E[receive triad_list (3 notes)]
    B --> F[call intervals.minor_seventh(note)]
    F --> G{intervals.validate_and_compute}
    G --> G1[if invalid -> raise NoteFormatError/propagate lower-layer exception]
    G --> H[receive minor_seventh_note (1 note)]
    E --> I[append minor_seventh_note to triad_list]
    H --> I[return 4-element list: [root, major_third, perfect_fifth, minor_seventh]]

## Examples:
- Typical usage:
    - Input: "C"
      - dominant_seventh("C") -> ["C", "E", "G", "Bb"]
    - Input: "F#"
      - dominant_seventh("F#") -> ["F#", "A#", "C#", "E"]
- Error handling:
    - Invalid input (empty string or invalid letter):
        try:
            dominant_seventh("")
        except NoteFormatError as e:
            # handle invalid input (notify user, log, or re-raise)
            pass
    - If callers need to protect against any lower-layer errors from the intervals or notes modules, catch FormatError (or a broader Exception) as appropriate for the calling context.

## `mingus.core.chords.half_diminished_seventh` · *function*

## Summary:
Constructs the four pitch names of a half-diminished seventh chord built on the given root and returns them as a 4-element list (root, minor third, diminished fifth, minor seventh).

## Description:
This function composes two smaller utilities — the diminished triad constructor and the minor-seventh interval helper — to produce the four chord tones of a half-diminished seventh chord. Known callers within the provided codebase: none were located; it is intended for use by higher-level chord-building, rendering, or analysis routines when an explicit list of chord tones is required.

Typical trigger/context:
- Invoked when a caller needs the explicit pitch names that constitute a half-diminished seventh chord for display, MIDI/event generation, analysis, or further harmonization steps.

Why this logic is a separate function:
- Responsibility separation: it centralizes the musical definition of a half-diminished seventh chord by composing the diminished triad (root, minor third, diminished fifth) with the minor seventh above the root. This avoids duplicating interval computations and ensures consistent error propagation and spelling choices determined by the intervals helpers.

## Args:
    note (str or indexable sequence-like):
        - The root pitch/name on which to build the chord.
        - Must be indexable and non-empty because the delegated interval helpers read note[0].
        - Common acceptable formats: simple note names like 'C', 'Bb', 'F#' or names including octave like 'C4' depending on the intervals/notes helper conventions.
        - The value is forwarded unchanged to diminished_triad and intervals.minor_seventh; no normalization is performed here.

## Returns:
    list:
        - A list of four pitch-name values in this exact order:
            1. The original root argument (returned verbatim).
            2. The pitch returned by intervals.minor_third(note) — the minor third above the root (this element is produced inside diminished_triad).
            3. The pitch returned by intervals.minor_fifth(note) — the diminished fifth above the root (this element is produced inside diminished_triad).
            4. The pitch returned by intervals.minor_seventh(note) — the minor seventh above the root.
        - Typical concrete type: list of strings representing note names (e.g., ['C', 'Eb', 'Gb', 'Bb']), but exact spellings and octave annotations are determined by the intervals module.
        - On success the list length is always 4.

## Raises:
    - This function does not raise errors directly. Any exception raised by the delegated calls will propagate unchanged to the caller. In practice these include, but may not be limited to:
        * mingus.core.mt_exceptions.NoteFormatError — when the input note string is malformed or cannot be parsed by the intervals/notes utilities.
        * mingus.core.mt_exceptions.FormatError — for other format-related validation errors from lower-level helpers.
    - If the underlying helpers perform other validations or raise other exceptions, those will also be propagated.

## Constraints:
    Preconditions:
        - `note` must be indexable and non-empty (e.g., a non-empty string).
        - `note` must represent a pitch in a format accepted by the intervals/notes helpers used by diminished_triad and intervals.minor_seventh.
        - The diminished_triad function must return a 3-element list [root, minor_third, diminished_fifth]; intervals.minor_seventh must return a single pitch value for the minor seventh.

    Postconditions:
        - If no exception is raised, the function returns a list of exactly 4 pitch values as described in Returns.
        - No global state is modified and no I/O is performed by this function.

## Side Effects:
    - None local to this function: it performs no file, network, or stdout I/O and does not mutate global variables.
    - Any side effects would come from the delegated interval/chord utilities (none are expected for pure interval computations).

## Control Flow:
flowchart TD
    Start --> Call_Diminished_Triad
    Call_Diminished_Triad --> DiminishedTriad_OK{diminished_triad succeeded?}
    DiminishedTriad_OK -- no --> PropagateError1[Propagate exception to caller]
    DiminishedTriad_OK -- yes --> Call_Minor_Seventh
    Call_Minor_Seventh --> MinorSeventh_OK{intervals.minor_seventh succeeded?}
    MinorSeventh_OK -- no --> PropagateError2[Propagate exception to caller]
    MinorSeventh_OK -- yes --> Concatenate[Concatenate triad + [minor seventh]]
    Concatenate --> ReturnList[Return 4-element list]
    PropagateError1 --> End
    PropagateError2 --> End
    ReturnList --> End

## Implementation Notes (sufficient to reimplement):
    - Obtain the diminished triad for the root by calling diminished_triad(note). Expect a 3-element list: [root, minor_third, diminished_fifth].
    - Compute the minor seventh above the same root by calling intervals.minor_seventh(note). Expect a single pitch-name value.
    - Return the concatenation of the triad list and a single-item list containing the minor seventh: i.e., result_list = triad_list + [minor_seventh_value].
    - Do not attempt to normalize or mutate the returned pitch strings — return them exactly as received from the helpers.
    - Allow any exceptions from diminished_triad or intervals.minor_seventh to propagate; do not catch them here.

## Examples:
Example — typical (happy path):
    from mingus.core.chords import half_diminished_seventh
    chord = half_diminished_seventh("C")
    # Typical expected result (intervals spelling dependent):
    # ["C", "Eb", "Gb", "Bb"]

Example — error handling for malformed input:
    from mingus.core.chords import half_diminished_seventh
    from mingus.core.mt_exceptions import NoteFormatError, FormatError
    try:
        chord = half_diminished_seventh("InvalidNoteName")
    except (NoteFormatError, FormatError) as e:
        # Report or handle invalid input to the caller
        handle_invalid_note(e)
    except Exception:
        # Unexpected exceptions propagate or can be handled globally
        raise

## `mingus.core.chords.minor_seventh_flat_five` · *function*

## Summary:
Delegates to the half-diminished seventh chord builder to produce the four pitch names of a minor-seventh, flat-fifth chord (m7b5 / half-diminished) built on the given root.

## Description:
Known callers:
- No direct callers were found in the inspected codebase; this function exists as a convenience/alias for callers that refer to this chord by the name "minor seventh flat five" or "m7b5".
Typical trigger/context:
- Invoked when a caller needs the explicit pitch names that constitute a minor-seventh flat-fifth (half-diminished seventh) chord for display, MIDI/event generation, analysis, harmonization, or other music-processing steps.

Why this logic is extracted into its own function:
- This function is a thin semantic alias that maps the alternate name "minor_seventh_flat_five" to the canonical implementation half_diminished_seventh. Keeping this alias as a separate function preserves naming compatibility and API ergonomics for users who expect the "minor seventh flat five" terminology, without duplicating the chord-construction logic.

## Args:
    note (str or indexable sequence-like):
        - The root pitch/name on which to build the chord.
        - Must be indexable and non-empty because the delegated helpers read note[0].
        - Common acceptable formats: simple note names like 'C', 'Bb', 'F#' or names including octave like 'C4' depending on the intervals/notes helper conventions.
        - This argument is forwarded unchanged to half_diminished_seventh (and ultimately to diminished_triad and intervals.minor_seventh).

## Returns:
    list:
        - A 4-element list of pitch-name values representing the chord tones in this exact order:
            1. Root (the original note argument, returned verbatim),
            2. Minor third above the root,
            3. Diminished fifth (flat five) above the root,
            4. Minor seventh above the root.
        - Typical concrete type: list of strings representing note names (e.g., ['C', 'Eb', 'Gb', 'Bb']), but exact spellings and octave annotations are determined by the intervals/notes helpers.
        - On success the list length is always 4.

## Raises:
    - This function does not raise errors itself; any exception raised by half_diminished_seventh (or its delegated helpers) will propagate unchanged to the caller. In practice these include:
        * mingus.core.mt_exceptions.NoteFormatError — if the input note string is malformed or cannot be parsed.
        * mingus.core.mt_exceptions.FormatError — for other format-related validation errors from lower-level helpers.
    - Any other exceptions thrown by the lower-level utilities (intervals, notes, or diminished_triad) will also propagate.

## Constraints:
    Preconditions:
        - `note` must be indexable and non-empty (e.g., a non-empty string).
        - `note` must be in a format accepted by the intervals/notes helpers used downstream.
    Postconditions:
        - If no exception is raised, the function returns a list of exactly 4 pitch values as described above.
        - No global state is modified and no I/O is performed by this function.

## Side Effects:
    - None local to this function: it performs no file, network, or stdout I/O and does not mutate global variables.
    - Any side effects would come from the delegated helpers (none expected for pure interval computations).

## Control Flow:
flowchart TD
    Start --> Call_HalfDiminished[Call half_diminished_seventh(note)]
    Call_HalfDiminished --> Succeeded{half_diminished_seventh succeeded?}
    Succeeded -- Yes --> ReturnList[Return 4-element chord list]
    Succeeded -- No --> PropagateError[Propagate exception to caller]
    ReturnList --> End
    PropagateError --> End

## Examples:
Example — typical (happy path):
    from mingus.core.chords import minor_seventh_flat_five
    chord = minor_seventh_flat_five("C")
    # Typical expected result (intervals spelling dependent):
    # ["C", "Eb", "Gb", "Bb"]

Example — error handling for malformed input:
    from mingus.core.chords import minor_seventh_flat_five
    from mingus.core.mt_exceptions import NoteFormatError, FormatError
    try:
        chord = minor_seventh_flat_five("InvalidNoteName")
    except (NoteFormatError, FormatError) as e:
        # Handle or report invalid input
        handle_invalid_note(e)
    except Exception:
        # Unexpected exceptions propagate or can be handled at a higher level
        raise

## `mingus.core.chords.diminished_seventh` · *function*

## Summary:
Constructs the four pitch names comprising a diminished seventh chord built on the supplied root and returns them as a list.

## Description:
This function composes lower-level chord and interval utilities to produce a diminished seventh chord: it takes the three pitches of a diminished triad built on the root and appends the diminished seventh above the root.

Known callers within the codebase:
    - Higher-level chord-building utilities and APIs that enumerate chord tones given a chord type and root (no direct callers were present in the provided graph). Typical usage is in a chord factory or formatter that needs the explicit list of chord tone names for presentation, playback, or further harmonic processing.

Why this logic is extracted into its own function:
    - Responsibility separation: chord construction (enumerating chord tones) is separated from interval arithmetic and single-note accidentals. This keeps chord definitions declarative and reuses interval and note-quality helpers (intervals.minor_seventh and notes.diminish) rather than duplicating that logic inline.

## Args:
    note (sequence-like, required):
        - The root pitch on which to build the diminished seventh chord.
        - Expected format: any value accepted by the intervals and notes helpers (commonly a string pitch name such as 'C', 'C#', 'Eb', or including octave like 'C4').
        - Constraints:
            * Must be indexable and non-empty because the underlying interval helpers access note[0] and notes.diminish inspects the last character (note[-1]).
            * The string contents must represent a valid pitch according to the intervals module; otherwise the delegated interval functions will raise.

## Returns:
    list:
        - A 4-element list of pitch representations (typically strings) in the form:
            [ root, minor_third, diminished_fifth, diminished_seventh ]
        - The first three elements are exactly the list returned by diminished_triad(note).
        - The fourth element is computed as notes.diminish(intervals.minor_seventh(note)).
        - Edge / variant cases:
            * Exact enharmonic spellings (for example 'Gb' vs 'F#') and octave suffixes are determined by the intervals.* helpers; this function preserves their returned formats except for the final step where notes.diminish adjusts the minor seventh's accidental as described below.

## Raises:
    - This function does not explicitly raise exceptions itself.
    - Exceptions raised by the delegated helpers will propagate to the caller. Examples of propagated exceptions that callers should anticipate (depending on inputs and the implementation of underlying modules):
        * FormatError — if the supplied `note` is syntactically invalid for the intervals/notes utilities.
        * NoteFormatError — for other invalid note representations.
        * IndexError or TypeError — if `note` is not indexable or is empty (because underlying helpers index note[0] or notes.diminish checks note[-1]).
    - Callers should catch and handle these propagated exceptions when working with untrusted or user-provided input.

## Constraints:
    Preconditions:
        - `note` must be indexable (support __getitem__) and non-empty.
        - `note` must be a valid pitch representation per the intervals module.

    Postconditions:
        - On successful return, a list of length 4 is returned as described above.
        - No global state is modified and the function performs no I/O.

## Side Effects:
    - None local to this function: no filesystem, network, stdout/stderr I/O, nor mutation of global state.
    - Any side effects would originate from calls to the underlying modules (intervals, notes), but those helpers are pure in the provided snapshots.

## Control Flow:
flowchart TD
    Start --> Call_diminished_triad
    Call_diminished_triad -->|exception| Propagate_error_from_triad
    Call_diminished_triad -->|success| Call_minor_seventh
    Call_minor_seventh -->|exception| Propagate_error_from_minor_seventh
    Call_minor_seventh -->|success| Call_notes_diminish
    Call_notes_diminish -->|exception| Propagate_error_from_notes_diminish
    Call_notes_diminish -->|success| Combine_and_Return
    Propagate_error_from_triad --> End
    Propagate_error_from_minor_seventh --> End
    Propagate_error_from_notes_diminish --> End
    Combine_and_Return --> End

## Examples:
    Example 1 — typical usage (happy path):
        Input: 'C'
        Flow:
            - diminished_triad('C') typically returns ['C', 'Eb', 'Gb'] (minor third and diminished fifth).
            - intervals.minor_seventh('C') typically yields 'Bb' (minor seventh above C).
            - notes.diminish('Bb') appends another flat producing 'Bbb' (because last char != '#').
        Result: ['C', 'Eb', 'Gb', 'Bbb']
        Note: exact spellings (e.g., 'Gb' vs 'F#') and interval naming are determined by the intervals module; this example shows the common theoretical spelling for a diminished seventh chord.

    Example 2 — handling invalid input:
        from mingus.core.mt_exceptions import FormatError, NoteFormatError
        try:
            chord = diminished_seventh(bad_input)
        except (FormatError, NoteFormatError, IndexError, TypeError) as e:
            # Validate or normalize input before retrying, or surface a user-friendly message
            handle_invalid_input(e)

## `mingus.core.chords.minor_major_seventh` · *function*

## Summary:
Builds a four-note minor-major seventh chord on the given root pitch and returns the chord tones in order (root, minor third, perfect fifth, major seventh).

## Description:
Known callers:
- None found in the supplied context. This is a small utility intended to be used by higher-level chord construction, rendering, or analysis code that needs the specific minor-major seventh chord type.

Context and typical usage:
- Called when a caller needs the spelled pitch names constituting a minor triad with a raised (major) seventh above the same root (commonly notated m(maj7) or mM7).
- Typical pipeline stage: chord generation / chord-listing utilities that assemble chord tones for display, MIDI generation, or harmonic analysis.

Why this logic is a separate function:
- Assembling this chord is a common, well-defined musical operation that composes two sub-operations: producing a minor triad and appending the major seventh. Encapsulating the composition prevents duplication, centralizes error propagation from the interval helpers, and provides a single, descriptive API for requesting a minor-major seventh chord.

## Args (if present):
    note (str):
        The root pitch/name for the chord.
        - Required.
        - Format: any note string accepted by the intervals/notes subsystem used by the module (examples: "C", "C#", "Db", optionally with octave qualifiers depending on the intervals/notes implementation).
        - The function does not validate or normalize the string itself; it forwards the value to minor_triad and intervals.major_seventh, so allowed values and parsing rules are those of those helpers.
        - There are no other parameters or interdependencies.

## Returns:
    list[str]:
        A list of four pitch-name strings in this exact order:
          1. The original root argument (returned verbatim).
          2. The minor third above the root (as returned by minor_triad / intervals.minor_third).
          3. The perfect fifth above the root (as returned by minor_triad / intervals.perfect_fifth).
          4. The major seventh above the root (as returned by intervals.major_seventh).
        - On success the returned list length is always 4.
        - Exact accidentals (e.g., "D#" vs "Eb"), enharmonic choices, and octave numbers depend on the behavior of the intervals helpers and any normalization they perform.

## Raises:
    - Any exception raised by minor_triad or intervals.major_seventh will propagate unchanged.
    - Common exceptions coming from the lower-level note/interval parsing utilities include:
        * mingus.core.mt_exceptions.NoteFormatError — if the supplied note string cannot be parsed as a valid pitch.
        * mingus.core.mt_exceptions.FormatError — for other formatting/interval-expression errors.
    - No exceptions are raised directly by this function beyond propagation.

## Constraints:
Preconditions:
    - The caller must provide a note string in a format acceptable to the library's intervals/notes utilities.
    - The intervals and chords helper functions must be available in the runtime environment.

Postconditions:
    - If the function returns normally, it guarantees a list of four strings representing the chord tones in the order root → minor-third → perfect-fifth → major-seventh.
    - No global state is modified by this function.

## Side Effects:
    - None. The function performs no I/O and does not mutate global or external state; it only calls pure interval/chord helper functions.

## Control Flow:
flowchart TD
    Start --> CallMinorTriad[Call minor_triad(note)]
    CallMinorTriad --> MinorTriadOK{minor_triad succeeded?}
    MinorTriadOK -- no --> PropagateError1[Propagate exception to caller]
    MinorTriadOK -- yes --> CallMajor7[Call intervals.major_seventh(note)]
    CallMajor7 --> Major7OK{major_seventh succeeded?}
    Major7OK -- no --> PropagateError2[Propagate exception to caller]
    Major7OK -- yes --> Combine[Combine minor_triad result + [major_seventh]]
    Combine --> Return[Return 4-note list]
    PropagateError1 --> End[End]
    PropagateError2 --> End

## Examples (if public and non-trivial):
Example 1 — typical usage (happy path):
    from mingus.core.chords import minor_major_seventh

    chord = minor_major_seventh("C")
    # Typical expected result (dependent on interval-spelling rules):
    # ["C", "Eb", "G", "B"]

Example 2 — another root demonstrating accidentals:
    from mingus.core.chords import minor_major_seventh

    chord = minor_major_seventh("A")
    # Typical expected result:
    # ["A", "C", "E", "G#"]

Example 3 — error handling for malformed input:
    from mingus.core.chords import minor_major_seventh
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        chord = minor_major_seventh("H#")  # invalid note name in most systems
    except (NoteFormatError, FormatError) as e:
        # Handle or report invalid note format
        print("Invalid note:", e)

Implementation notes for reimplementation:
    - This function composes two existing helpers: minor_triad(note) which returns [root, minor_third, perfect_fifth], and intervals.major_seventh(note) which returns the major seventh above the root.
    - A correct reimplementation simply concatenates the triad list with a single-element list containing the major seventh and propagates any exceptions from the helpers unchanged.
    - If callers require normalized or specific enharmonic spellings, normalize the input note before calling this function.

## `mingus.core.chords.minor_sixth` · *function*

## Summary:
Returns the four spelled pitch names forming a minor sixth chord built on the given root: the root, its minor third, its perfect fifth, and the major sixth above the root.

## Description:
Known callers within the codebase:
- None discovered in the supplied context. This function is a building block for higher-level chord-generation utilities, notation export, or user-facing chord rendering routines that require spelled chord tones.

Why this logic is extracted:
- Producing a minor sixth chord is a single, well-defined musical operation (minor triad plus an added major sixth). Extracting it into its own function centralizes the composition of the triad and the additional interval, reuses existing interval- and triad-building helpers, and keeps accidental/interval-spelling logic consistent across callers. The function's responsibility is orchestration (compose triad and sixth), not low-level note parsing or interval arithmetic — those are delegated to minor_triad and intervals.major_sixth.

## Args:
    note (str):
        - A single-note name representing the chord root.
        - Required format: an indexable string whose first character is a natural note letter A–G; subsequent characters (if any) are accidentals (commonly '#' for sharp, 'b' for flat) or other notation accepted by the intervals/notes utilities in this package.
        - Examples: "C", "C#", "Db", "F##", "Ebb".
        - The function forwards this argument unchanged to minor_triad and intervals.major_sixth; it does not normalize or validate the string itself.

## Returns:
    list[str]:
        - A list of four spelled note strings in this exact order:
            1. root (identical to the provided note argument)
            2. minor third above the root (value returned by intervals.minor_third via minor_triad)
            3. perfect fifth above the root (value returned by intervals.perfect_fifth via minor_triad)
            4. major sixth above the root (value returned by intervals.major_sixth)
        - On success the returned list length is always 4.
        - The precise accidental spellings and inclusion/exclusion of octave numbers depend on the interval helpers' behavior.

## Raises:
    - mingus.core.mt_exceptions.NoteFormatError
        * Propagates from the interval or triad helpers when the provided note string fails lower-level note-format validation.
    - mingus.core.mt_exceptions.FormatError
        * May propagate from lower-level parsing/formatting utilities used by the helpers.
    - IndexError
        * Can occur if note is an empty string and a helper attempts to access note[0] (propagated from intervals.major_sixth or other helpers).
    - TypeError
        * Can occur if note is not a string or not indexable (e.g., None, numeric types) when lower-level utilities operate on it.
    - Any other exception raised by minor_triad or intervals.major_sixth will propagate unchanged; this function performs no exception handling.

## Constraints:
Preconditions:
    - The caller must supply a non-empty, indexable string whose first character is one of the letters A–G (case rules follow the intervals/notes module).
    - The runtime must have the package's intervals and notes utilities available and working correctly.
Postconditions:
    - If the function returns normally, it guarantees a new list object of length 4 containing spelled notes as described in Returns.
    - No global state or external resources are modified by this function.

## Side Effects:
    - None local to this function: no I/O, no network, no global state mutation.
    - Any side effects are only those (if any) caused by the delegated helpers; typical interval/name computations are pure and side-effect free.

## Control Flow:
flowchart TD
    Start --> CallMinorTriad[Call minor_triad(note)]
    CallMinorTriad --> TriadOK{minor_triad succeeded?}
    TriadOK -- No --> PropagateTriadError[Propagate exception to caller]
    TriadOK -- Yes --> CallMajorSixth[Call intervals.major_sixth(note)]
    CallMajorSixth --> SixthOK{intervals.major_sixth succeeded?}
    SixthOK -- No --> PropagateSixthError[Propagate exception to caller]
    SixthOK -- Yes --> Concat[Concatenate triad list + [major_sixth]]
    Concat --> Return[Return 4-element list]
    PropagateTriadError --> End
    PropagateSixthError --> End

## Examples:
Example 1 — typical usage (happy path):
    from mingus.core.chords import minor_sixth

    chord = minor_sixth("C")
    # Expected (typical) result:
    # ["C", "Eb", "G", "A"]

    chord = minor_sixth("C#")
    # Expected (typical) result:
    # ["C#", "E", "G#", "A#"]

Example 2 — handling malformed input:
    from mingus.core.chords import minor_sixth
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        chord = minor_sixth("H#")  # invalid natural note letter
    except (NoteFormatError, FormatError) as e:
        # Validate or report the malformed note before retrying
        print("Invalid note format:", e)

Example 3 — handling empty or non-string input:
    try:
        minor_sixth("")   # may raise IndexError from lower-level helpers
    except IndexError:
        print("Empty note string is not allowed")

    try:
        minor_sixth(None) # will raise TypeError in helpers that expect a string
    except TypeError:
        print("Note must be a string")

## `mingus.core.chords.major_sixth` · *function*

## Summary:
Constructs a spelled major sixth chord from a single root note by returning the major triad (root, major third, perfect fifth) with the added major sixth above the root.

## Description:
This function composes a four-note chord by delegating to two helpers:
- It calls the chord-construction helper that returns the major triad built on the given root (root, major third, perfect fifth).
- It appends the spelled major sixth computed by the intervals utility.

Known callers within the codebase:
- No explicit call sites were discovered in the available repository scan. Typical callers are:
  - Chord-generation utilities and higher-level harmony/rhythm code that need spelled chord tones.
  - User-facing routines that render or manipulate chord symbols and voicings.
  - Any orchestration or MIDI/notation export code that constructs a chord tone list from a single root note.

Why this is a separate function:
- It captures the single responsibility of producing a conventional "major sixth" chord (root + major third + perfect fifth + major sixth) with correctly spelled accidentals.
- Keeping this logic as a small composed function centralizes interval spelling behavior and avoids repeating the pattern (triad + extra interval) across the codebase. This ensures consistent use of the intervals utilities for accidental augmentation/diminishment.

## Args:
    note (str): The root note spelled as a single-note string.
        - Required format: first character is a natural note letter A–G; remaining characters (if any) are accidentals, using '#' for sharp and 'b' for flat (examples: "C", "C#", "Db", "F##", "Ebb").
        - Must be a non-empty, indexable string (the underlying intervals helper accesses the first character).
        - Interdependencies: correctness depends on providing a single-note string — passing a list, pre-spelled chord, or non-string may cause exceptions from lower-level utilities.

## Returns:
    list[str]: A 4-element list of spelled note strings in this order:
        [root, major_third, perfect_fifth, major_sixth]
    - root: the same string value passed in (no normalization performed here).
    - major_third and perfect_fifth: spelled so the intervals from the root are a major third and a perfect fifth respectively (determined by intervals.major_third and intervals.perfect_fifth used by the triad helper).
    - major_sixth: spelled so it is a major sixth above the root (determined by intervals.major_sixth).
    - Edge cases:
        - If the interval utilities produce unusual augmentations/diminishments to reach the exact semitone distance, the returned spellings will reflect those decisions (the precise accidental spelling follows the intervals module's rules).

## Raises:
    NoteFormatError:
        - Raised when the provided note string is not a valid single-note format; this originates from validation or parsing performed by the triad or intervals utilities.
    IndexError:
        - Can occur if note is an empty string and an underlying routine attempts to access note[0] (propagates from intervals.major_sixth implementation).
    TypeError:
        - Can occur if note is not a string or otherwise not indexable (e.g., None or a numeric value) when lower-level utilities operate on the value.
    Other exceptions:
        - Any exception raised by the called helpers (major_triad or intervals.major_sixth) will propagate; this function does not catch or wrap those exceptions.

## Constraints:
    Preconditions:
    - Caller must pass a non-empty, single-note string whose first character is one of A,B,C,D,E,F,G and whose subsequent characters (if any) are accidentals using '#' or 'b'.
    - The package's intervals and notes utilities must be present (true inside the same package).
    Postconditions:
    - The function returns a 4-element list of strings representing spelled chord tones where the 2nd, 3rd, and 4th elements are respectively a major third, perfect fifth, and major sixth above the root according to the intervals utilities.

## Side Effects:
    - None within this function itself. It performs pure computation and returns a new list.
    - No I/O, no mutation of global state, no network or external service calls.
    - Any side effects would come from the helper functions (none are expected for standard note computations).

## Control Flow:
flowchart TD
    A[call major_sixth(note)] --> B{validate input implicitly}
    B --> C[call major_triad(note)]
    C --> D[major_triad calls intervals.major_third and intervals.perfect_fifth]
    D --> D1{interval helpers may loop to adjust spelling}
    D1 --> D2[augment/diminish until semitone distance matches]
    D --> E[receive triad_list (3 notes)]
    B --> F[call intervals.major_sixth(note)]
    F --> F1{interval helper may loop to adjust spelling}
    F1 --> F2[augment/diminish until semitone distance matches (target = major sixth)]
    F --> G[receive major_sixth_note]
    E --> H[concatenate triad_list + [major_sixth_note]]
    G --> H
    H --> I[return 4-element chord list]

Notes:
- The "loop" boxes reflect behavior inside the intervals utilities, which attempt augmentation/diminishment until the spelled note achieves the target semitone distance.

## Examples:
- Typical usage (happy path):
    - Input: "C"
      - major_sixth("C") -> ["C", "E", "G", "A"]
    - Input: "C#"
      - major_sixth("C#") -> ["C#", "E#", "G#", "A#"] (accidentals spelled to preserve interval names)
- Error handling example:
    - Malformed input:
        try:
            major_sixth("H")   # invalid natural note letter
        except NoteFormatError as e:
            # handle invalid-note-format (log, notify user, re-raise, etc.)
            raise
    - Non-string or empty input:
        try:
            major_sixth("")    # empty string may raise IndexError inside intervals
        except IndexError:
            # handle empty-note error
            pass
        try:
            major_sixth(None)  # None will cause TypeError in lower-level routines
        except TypeError:
            # handle invalid type
            pass

## `mingus.core.chords.dominant_sixth` · *function*

## Summary:
Constructs a spelled "dominant sixth" chord by producing the major-sixth chord built on the given root and appending the minor seventh above the same root, returning the five spelled chord tones.

## Description:
This function composes two smaller primitives to produce its result:
- It calls the chord helper major_sixth(note) to obtain the four-note major-sixth chord (root, major third, perfect fifth, major sixth).
- It calls intervals.minor_seventh(note) to compute the spelled minor seventh above the root and appends that single note to the major-sixth list.

Known callers within the codebase:
- None explicitly discovered in the repository scan. Typical callers include:
  - Higher-level chord-generation utilities that produce spelled chord tone lists from a root.
  - Notation/MIDI export or voicing routines that require fully spelled chord tones.
  - User-facing APIs that accept a root note string and request a specific chord quality.

Why this is a separate function:
- Encapsulates the specific chord shape “major triad + major sixth + minor seventh” so callers need not reconstruct it manually.
- Centralizes spelling behavior by reusing interval and chord helpers, ensuring consistent accidental handling across the codebase.

## Args:
    note (str): Root note as a single-note string.
        - Format: first character is a natural A–G; optional subsequent characters are accidentals (e.g., "#", "b", "##", "bb"). Examples: "C", "F#", "Ebb".
        - Constraint: must be a non-empty, indexable string (the underlying interval helpers access note[0]).
        - Interdependencies: correctness of behavior depends on passing a single-note string; non-string or malformed strings will cause lower-level utilities to raise errors.

## Returns:
    list[str]: A 5-element list of spelled note strings in this exact order:
        [root, major_third, perfect_fifth, major_sixth, minor_seventh]
    - Each element is a note name string spelled by the intervals/chord helpers to reflect correct interval names (may include accidentals).
    - Examples:
        - Input "C" -> ["C", "E", "G", "A", "Bb"]
        - Input "C#" -> ["C#", "E#", "G#", "A#", "B"] (spellings depend on intervals helper rules)
    - Edge cases:
        - If the underlying helpers choose augmentations/diminishments to satisfy semitone distances, the accidentals in returned note strings will reflect those adjustments.
        - The function always returns a new list (no mutation of inputs).

## Raises:
    NoteFormatError:
        - Propagated from underlying interval/chord utilities when the input note string is not a valid single-note format.
    IndexError:
        - May be raised if note is an empty string and a helper attempts to access note[0].
    TypeError:
        - May be raised if note is not indexable (e.g., None or a non-string type) when lower-level utilities operate on it.
    Other exceptions:
        - Any other exception raised by major_sixth or intervals.minor_seventh (e.g., internal assertion or formatting errors) will propagate unchanged; this function does not catch or wrap exceptions.

## Constraints:
    Preconditions:
    - Caller must supply a non-empty single-note string with a natural letter A–G as the first character; optional accidentals follow.
    - The intervals and chord helper utilities must be present and functional in the environment.
    Postconditions:
    - On successful return, the function yields a 5-element list of spelled chord tones where elements 2..5 are respectively a major third, perfect fifth, major sixth, and minor seventh above the root per the intervals utilities.

## Side Effects:
    - None local to this function. It performs pure, in-memory computation and returns a new list.
    - No I/O, no global state mutation, no external network or service calls.
    - Any side effects would only come from the called helpers (which, for the typical intervals and chord helpers, do not perform I/O or mutate global state).

## Control Flow:
flowchart TD
    A[Start: dominant_sixth(note)] --> B[Call major_sixth(note)]
    B --> C{major_sixth may internally adjust spelling}
    C --> D[Return triad_plus_six (4-note list)]
    A --> E[Call intervals.minor_seventh(note)]
    E --> F{minor_seventh may internally adjust spelling}
    F --> G[Return minor_seventh_note (single note string)]
    D --> H[Concatenate triad_plus_six + [minor_seventh_note]]
    G --> H
    H --> I[Return 5-element chord list]
    I --> J[End]

Notes:
- The internal "adjust spelling" decision boxes reflect behavior inside the intervals helpers (they may augment/diminish accidentals until the intended semitone distance is achieved).

## Examples:
- Typical (happy path):
    from mingus.core.chords import dominant_sixth
    chord = dominant_sixth("C")
    # chord is typically ["C", "E", "G", "A", "Bb"]

- With accidentals:
    dominant_sixth("C#")
    # may return something like ["C#", "E#", "G#", "A#", "B"] depending on the intervals helper's spelling choices

- Error handling:
    try:
        dominant_sixth("H")   # invalid natural note letter
    except NoteFormatError:
        # handle invalid note format (log, notify user, re-raise, etc.)
        raise

    try:
        dominant_sixth("")    # may raise IndexError in helpers
    except IndexError:
        # handle empty-string error
        pass

    try:
        dominant_sixth(None)  # may raise TypeError in helpers
    except TypeError:
        # handle invalid type
        pass

## `mingus.core.chords.sixth_ninth` · *function*

## Summary:
Constructs a spelled sixth-ninth chord from a single root note by producing the major-sixth four-note chord and appending the spelled major second (the "ninth") above the root.

## Description:
- Known callers within the codebase:
    - Higher-level chord-generation utilities and user-facing routines that produce spelled chord tone lists for rendering, MIDI output, notation, or analysis. (No direct call sites were discovered in the scanned repository snapshot; typical invocation is when a caller needs the spelled tones for a 6/9 chord from a single root note.)
- Why this logic is a separate function:
    - It encapsulates the single responsibility of assembling a conventional "sixth-ninth" chord (root, major third, perfect fifth, major sixth, major ninth) using the package's interval-spelling utilities. Separating this composition reduces duplication, ensures consistent spelling decisions (delegated to intervals.* helpers), and makes intent explicit where used.

## Args:
    note (str):
        - A single-note string representing the chord root.
        - Required format: first character a letter A–G (case-sensitive convention of the codebase), optional accidentals after the letter using '#' for sharp and 'b' for flat (examples: "C", "C#", "Db", "F##", "Ebb").
        - Must be non-empty and indexable (the underlying helpers access note[0]).
        - Interdependencies: correctness of the returned spellings depends on valid input for the underlying helpers major_sixth and intervals.major_second; passing non-string or malformed strings will cause lower-level exceptions.

## Returns:
    list[str]:
        - A list of five spelled note strings in this exact order:
            [root, major_third, perfect_fifth, major_sixth, major_second (ninth)]
        - Explanation:
            - The first four elements are produced by major_sixth(note): root, major third, perfect fifth, and major sixth (spelled according to interval utilities).
            - The final element is intervals.major_second(note): the spelled major second above the root (serving as the chord's ninth).
        - Edge cases:
            - If the interval helpers choose augmented/diminished spellings to match the required semitone distances, the accidentals in returned notes will reflect those decisions.
            - The function does not normalize octave numbers — all returned notes are spelled pitch names without explicit octave indices.

## Raises:
    NoteFormatError:
        - Propagated from major_sixth or intervals.major_second when the input note string does not conform to the expected note format.
    FormatError:
        - May be raised by lower-level utilities that validate or parse note input and are imported into this module.
    IndexError:
        - Can occur if note is an empty string and a called helper attempts to access note[0].
    TypeError:
        - Can occur if note is not indexable (e.g., None or a numeric type) when lower-level helpers operate on the value.
    Any other exceptions raised by the called helpers will propagate unchanged.

## Constraints:
- Preconditions:
    - Caller must supply a non-empty single-note string in the expected note-spelling format (A–G plus accidentals).
    - The intervals and chord-construction utilities (major_sixth and intervals.major_second) must be available and working as expected.
- Postconditions:
    - The function returns a newly allocated list of five spelled note strings representing the sixth-ninth chord tones as described above.
    - No mutation of the input argument is performed.

## Side Effects:
- None intrinsic to this function: it performs pure computation and returns a new list.
- No I/O, no global state mutation, and no network or external service calls.
- Any side effects would come from the invoked helpers (none are expected for standard note computations).

## Control Flow:
flowchart TD
    A[Call sixth_ninth(note)] --> B[Call major_sixth(note)]
    B --> C{major_sixth may validate/parse note}
    C --> D[major_sixth returns triad + major sixth (list of 4 notes)]
    A --> E[Call intervals.major_second(note)]
    E --> F{interval helper may validate/parse note}
    F --> G[intervals.major_second returns spelled second (single note)]
    D --> H[Concatenate the 4-note list with [second_note]]
    G --> H
    H --> I[Return 5-element chord list]

Notes:
- The "validation/parse" and any augmentation/diminishment loops occur inside the called helpers (major_sixth and intervals.major_second); this function only composes their outputs.

## Examples:
- Happy path:
    - Input: "C"
      - Result: ["C", "E", "G", "A", "D"]  # root, major third, perfect fifth, major sixth, major ninth
    - Input: "C#"
      - Result: ["C#", "E#", "G#", "A#", "D#"]  # accidentals chosen to preserve interval letter names
- Error handling:
    - Malformed input:
        try:
            sixth_ninth("H")   # invalid note letter
        except NoteFormatError:
            # handle invalid-note-format
            raise
    - Empty or non-string input:
        try:
            sixth_ninth("")    # may raise IndexError in lower-level helpers
        except IndexError:
            # handle empty-note error
            pass
        try:
            sixth_ninth(None)  # will raise TypeError in lower-level helpers
        except TypeError:
            # handle invalid type
            pass

## `mingus.core.chords.minor_ninth` · *function*

## Summary:
Constructs a minor ninth chord by taking the four tones of a minor seventh on the given root and appending the major ninth (a major second above the root), returning the five pitch names.

## Description:
Known callers:
- None found in the supplied context. This function is a small, reusable chord-construction utility intended for use by higher-level chord enumeration, rendering, or analysis routines.

Why this logic is extracted:
- Building a minor ninth chord is a common musical operation composed of two sub-operations: producing the four-tone minor seventh chord and computing the major second (the ninth) above the root. Extracting this into a dedicated helper centralizes the behavior, avoids duplicating the "build 7th then append 9th" pattern, and ensures consistent ordering and error propagation for callers.

## Args:
    note (str):
        The root pitch/name for the chord.
        - Required.
        - Forwarded verbatim to the underlying helpers:
            * minor_seventh(note) — returns the four-tone minor seventh chord: the root, the minor third, the perfect fifth, and the minor seventh (in that exact order).
            * intervals.major_second(note) — returns the pitch a major second above the root (the ninth).
        - Accepted formats and validation rules are those enforced by the intervals/notes helpers (examples: "C", "C#", "Db", "Bb"). Octave qualifiers, if supported by underlying helpers, are preserved.

## Returns:
    list[str]:
        A list of five pitch name strings in this exact order:
          1. The original root note (as returned/forwarded by minor_seventh).
          2. The minor third above the root.
          3. The perfect fifth above the root.
          4. The minor seventh above the root.
          5. The major second above the root (the ninth).
        - On success the returned list length is the concatenation of the four-tone list returned by minor_seventh and the single-string returned by intervals.major_second (typically length 5).
        - Exact accidental spellings (e.g., "D#" vs "Eb") and octave numbers depend entirely on the behavior of the underlying intervals/notes helpers.

## Raises:
    - Any exception raised by minor_seventh or intervals.major_second will propagate unchanged to the caller.
    - Typical exception types raised by the underlying helpers include:
        * mingus.core.mt_exceptions.NoteFormatError — when the input cannot be parsed as a valid pitch.
        * mingus.core.mt_exceptions.FormatError — when the input format violates expected patterns.
    - This function does not raise new exception types or perform additional validation.

## Constraints:
Preconditions:
    - The caller must supply a non-empty string representing a pitch in a format accepted by the underlying intervals/notes helpers.
    - The intervals and chords utilities must be available in the runtime environment.

Postconditions:
    - If no exception is raised, the function returns the concatenation of minor_seventh(note) and [intervals.major_second(note)] (commonly a list of five pitch strings in the order described under Returns).
    - No global state is modified and no I/O is performed.

## Side Effects:
    - None. The function calls pure helper functions and does not perform I/O or mutate external/global state.

## Control Flow:
flowchart TD
    Start --> CallMinorSeventh[Call minor_seventh(note) -> [root, m3, P5, m7]]
    CallMinorSeventh --> MinorSeventhOK{minor_seventh succeeded?}
    MinorSeventhOK -- no --> PropagateError1[Propagate exception to caller]
    MinorSeventhOK -- yes --> CallMajorSecond[Call intervals.major_second(note) -> 9th]
    CallMajorSecond --> MajorSecondOK{major_second succeeded?}
    MajorSecondOK -- no --> PropagateError2[Propagate exception to caller]
    MajorSecondOK -- yes --> Concat[Return minor_seventh_list + [major_second]]
    Concat --> End

## Examples:
Example 1 — typical usage:
    from mingus.core.chords import minor_ninth

    chord = minor_ninth("C")
    # Typical expected result (dependent on intervals helpers):
    # ["C", "Eb", "G", "Bb", "D"]

Example 2 — handling invalid input:
    from mingus.core.chords import minor_ninth
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        chord = minor_ninth("H#")  # malformed or unsupported note name
    except (NoteFormatError, FormatError) as e:
        # Handle or report invalid note format
        print("Invalid note format:", e)

Implementation note:
    - Reimplementation (aligns with dependency documentation): call minor_seventh(note) to obtain the four-tone list [root, minor third, perfect fifth, minor seventh], call intervals.major_second(note) to obtain the ninth (a single pitch string), append that ninth to the four-tone list, and return the concatenated list. Allow exceptions from the helper functions to propagate unchanged.

## `mingus.core.chords.major_ninth` · *function*

## Summary:
Constructs a spelled five-note major-ninth chord from a single root note by appending the spelled major second to the result produced by the major_seventh helper.

## Description:
This function builds a major-ninth chord by delegating responsibilities to two helpers:
- It reuses mingus.core.chords.major_seventh(note) — see that function's documentation for the exact four-note spelled major-seventh content.
- It appends the spelled major second produced by mingus.core.intervals.major_second(note) to represent the ninth degree.

- Known callers: None discovered in the scanned repository. Typical use cases include chord-generation utilities, harmony/voicing builders, MIDI/notation exporters, or user code that needs a spelled major-ninth chord from a single root.
- Why separate: Centralizes the pattern "major-seventh + major ninth" so callers need not recompose the four-note major-seventh or separately request a spelled second. Delegating spelling to the intervals utilities ensures consistent accidental choices across chord-building helpers.

## Args:
    note (str): Root note string.
        - Required format: a non-empty single-note string whose first character is a natural note letter (A–G) and whose optional subsequent characters are accidentals using '#' or 'b'. Examples: "C", "C#", "Db", "F##", "Ebb".
        - The function forwards the same string to the helper functions; it does not normalize or mutate the input.
        - Interdependencies: The argument must be acceptable to the package's notes/intervals utilities; malformed or non-string inputs will produce exceptions from downstream utilities.

## Returns:
    list[str]: A five-element list equal to the list returned by major_seventh(note) with the single-element list [ intervals.major_second(note) ] appended.
    - See mingus.core.chords.major_seventh for the meaning and spelling of the initial four elements.
    - The appended element is a spelled note string produced by intervals.major_second(note) and represents the ninth degree (musically a major second above the root). It is a spelled pitch without explicit octave information.

## Raises:
    NoteFormatError:
        - Condition: The provided note string is malformed or cannot be parsed by downstream utilities.
        - Origin: Propagated from major_seventh or intervals.major_second.
    FormatError:
        - Condition: Internal formatting or interval-construction errors in the intervals utilities.
        - Origin: Propagated from the intervals module or helpers used by major_seventh.
    IndexError:
        - Condition: The provided note is an empty string ("").
        - Reason: Downstream utilities access note[0] and will raise IndexError on empty input.
    TypeError:
        - Condition: The provided note is not a string or otherwise incompatible with string operations expected by helpers.
        - Reason: major_seventh and intervals.major_second expect string inputs and will raise built-ins for incompatible types.

## Constraints:
    Preconditions:
        - The caller must pass a non-empty single-note string with a natural letter A–G as the first character and optional accidentals '#' or 'b' thereafter.
        - The package's intervals and notes utilities must be available and functioning.
    Postconditions:
        - On success, returns exactly five spelled note strings (the 4-element major_seventh result plus one appended spelled major second). The exact accidental spellings follow the intervals module's augment/diminish and spelling rules.

## Side Effects:
    - None local to this function: no I/O, no global state mutation, and no external service calls. Any side effects would originate from lower-level utilities (not expected in normal use).

## Control Flow:
flowchart TD
    A[Call major_ninth(note)] --> B{Is note a non-empty string?}
    B -- No (empty string) --> C[Downstream access note[0] -> IndexError raised]
    B -- No (non-string) --> D[Downstream string ops -> TypeError or other built-ins raised]
    B -- Yes --> E[Call major_seventh(note) -> 4-element list (see its docs)]
    E --> F[Call intervals.major_second(note) -> spelled_second]
    F --> G{Intervals may augment/diminish to match semitone target}
    G --> H[Receive spelled_second]
    H --> I[Return major_seventh_list + [spelled_second]]
    E --> J[Parsing/format errors -> NoteFormatError or FormatError propagated]

## Examples:
- Typical usage:
    try:
        chord = major_ninth("C")
        # chord is major_seventh("C") with intervals.major_second("C") appended
    except (NoteFormatError, FormatError, IndexError, TypeError) as e:
        # validate or report input error
        raise

- Defensive validation before calling:
    if not isinstance(root, str) or root == "" or root[0].upper() not in "ABCDEFG":
        raise ValueError("root must be a non-empty single-note string starting with A-G")
    chord = major_ninth(root)

## `mingus.core.chords.dominant_ninth` · *function*

## Summary:
Builds a spelled dominant ninth chord by taking the dominant seventh (major triad + minor seventh) for the given root and appending the major ninth (major second) above that root.

## Description:
- Known callers:
    - No explicit call sites were discovered in the available repository scan. Typical callers include chord-generation utilities, harmony-processing routines, MIDI/notation exporters, and user APIs that need spelled chord note lists.
    - Typical trigger: when a consumer requests the spelled notes for a dominant ninth chord from a single root note string.
- Why this logic is its own function:
    - Encapsulates the composition rule "dominant seventh + major ninth" so callers do not need to assemble the chord from interval primitives. It delegates lower-level responsibilities to the dominant_seventh function (defined alongside this function) and to intervals.major_second, ensuring consistent spelling behavior and avoiding duplication.

## Args:
    note (str):
        - The root note as a non-empty single-note string.
        - Required format: first character must be a natural note letter 'A'..'G'. Subsequent characters (if present) should be accidentals using '#' for sharps or 'b' for flats (examples: "C", "C#", "Db", "F##", "Ebb").
        - Implementation expectation: the underlying utilities access note[0]; therefore the argument must be indexable and non-empty. Passing None, an integer, or an empty string will violate preconditions (may raise TypeError or NoteFormatError).
        - No normalization is performed: the exact input string is returned as the first element of the output list.

## Returns:
    list[str]:
        - A list of exactly five spelled note strings in this order:
            0. root (the exact string passed in)
            1. major third above the root (provided indirectly by dominant_seventh via the chord utility)
            2. perfect fifth above the root (provided indirectly by dominant_seventh via the chord utility)
            3. minor seventh above the root (computed by dominant_seventh via intervals.minor_seventh)
            4. major ninth above the root (computed by intervals.major_second and appended by this function)
        - Example: dominant_ninth("C") -> ["C", "E", "G", "Bb", "D"]
        - The spelled forms (including any augmentations/diminutions) are those produced by the underlying intervals and chord utilities and are returned unchanged.

## Raises:
    NoteFormatError:
        - Raised when the provided note string violates expected note formatting (for example empty string, invalid first character, or invalid accidental characters). This originates from validation performed by dominant_seventh or intervals.major_second and is propagated.
    TypeError:
        - May be raised if `note` is not indexable (e.g., None or an int) because dependent utilities access note[0]. This is not explicitly raised by this function but can arise from underlying calls.
    Other lower-level exceptions:
        - FormatError or other exceptions raised inside the intervals, notes, or chord utilities may propagate. The function does not catch these exceptions.

## Constraints:
- Preconditions:
    - `note` must be a non-empty, indexable string with first character in 'A'..'G'.
    - Accidentals (if any) should use '#' or 'b' characters only.
    - The function relies on the sibling function dominant_seventh (which itself delegates triad construction to the chord utility and uses intervals.minor_seventh) and on intervals.major_second to compute the ninth.
- Postconditions:
    - On success, returns a 5-element list of spelled note strings representing a dominant ninth chord as described above.
    - No global state is modified by this function.

## Side Effects:
    - None. The function performs pure computation and delegates to other pure utilities. It does not perform any I/O or mutate external state. Any side effects would originate from lower-level utilities (none expected).

## Control Flow:
flowchart TD
    A[call dominant_ninth(note)] --> B{note provided? (non-empty string expected)}
    B --> C[call dominant_seventh(note)]
    C --> C1[dominant_seventh delegates triad construction to chord utility (root, major_third, perfect_fifth)]
    C --> C2[dominant_seventh calls intervals.minor_seventh(note) to compute minor seventh]
    C1 --> C3[assemble triad_list (3 notes)]
    C2 --> C3[append minor_seventh -> 4-element list]
    C3 --> D[return 4-element list to dominant_ninth]
    B --> E[call intervals.major_second(note)]
    E --> E1[intervals.major_second validates note (uses note[0]) and returns a single-note string for the major ninth]
    D --> F[append major_ninth to 4-element list]
    F --> G[return 5-element list: [root, major_third, perfect_fifth, minor_seventh, major_ninth]]

## Examples:
- Typical usage:
    - dominant_ninth("C")  -> ["C", "E", "G", "Bb", "D"]
    - dominant_ninth("F#") -> ["F#", "A#", "C#", "E", "G#"]
- Error handling:
    - Invalid string input (empty or malformed):
        try:
            dominant_ninth("")
        except NoteFormatError as e:
            # handle invalid input
            pass
    - Non-indexable input:
        try:
            dominant_ninth(None)
        except TypeError:
            # handle unexpected input type
            pass
    - To guard broadly against lower-level format issues:
        try:
            chord = dominant_ninth(user_input)
        except (NoteFormatError, FormatError) as e:
            # handle or recover
            pass

## `mingus.core.chords.dominant_flat_ninth` · *function*

## Summary:
Constructs a spelled dominant-flat-ninth chord by obtaining a standard dominant ninth and replacing its ninth with the minor second (flattened ninth) above the root.

## Description:
- Known callers:
    - No explicit call sites were discovered in the repository scan. Typical callers include chord-generation utilities, harmony-processing routines, MIDI/notation exporters, and user APIs that need spelled chord note lists.
    - Typical trigger: when a consumer requests the spelled notes for a dominant-flat-ninth (e.g., "C7b9") given a single root note string.

- Why this logic is a separate function:
    - dominant_ninth(note) builds a spelled dominant ninth by taking the dominant seventh (root, major third, perfect fifth, minor seventh) and appending the major ninth (major second) above the root.
    - This function composes that result with intervals.minor_second(note) to produce the flat ninth variant: it reuses dominant_ninth for the base chord construction and then overwrites the ninth position with the spelled minor second. Encapsulating this small variant avoids duplicating chord-assembly logic and centralizes the flat‑ninth spelling behavior.

## Args:
    note (str):
        - The root note as a non-empty, indexable string.
        - Expected format: first character is a natural note letter 'A'..'G'; subsequent characters (if present) are accidentals using '#' for sharps or 'b' for flats (examples: "C", "C#", "Db", "F##", "Ebb").
        - The function delegates spelling and validation to dominant_ninth and intervals.minor_second; those utilities inspect note[0], so the argument must be indexable and non-empty.

## Returns:
    list[str]:
        - The function returns the list produced by dominant_ninth(note) after assigning element index 4 to intervals.minor_second(note). The intended result is a five-element list:
            0. root (the exact string passed as note)
            1. major third above the root
            2. perfect fifth above the root
            3. minor seventh above the root
            4. flattened ninth (minor second above the root)
        - If dominant_ninth returns a standard five-element dominant-ninth list, the returned list will have length 5 with the ninth replaced by the flattened ninth. Any spelled forms returned by the underlying utilities are preserved.

## Raises:
    NoteFormatError:
        - Propagated when the provided `note` violates note-format expectations. This commonly arises from the interval/notes utilities invoked here (for example intervals.minor_second) and is not handled by this function.

    TypeError:
        - May be raised if `note` is not indexable (e.g., None or an int) because underlying utilities access note[0].

    IndexError:
        - If dominant_ninth unexpectedly returns a list shorter than 5 elements, assigning to res[4] will raise IndexError. Under correct operation dominant_ninth returns five elements.

    FormatError or other lower-level exceptions:
        - Any FormatError or other exceptions raised by dominant_ninth, intervals.minor_second, or other underlying utilities may propagate unchanged.

## Constraints:
- Preconditions:
    - `note` must be a non-empty, indexable string whose first character is a letter in 'A'..'G'.
- Postconditions:
    - On success, returns a 5-element list of spelled note strings representing the dominant-flat-ninth chord: [root, major3, perfect5, minor7, flat9].
    - No global state is modified.

## Side Effects:
- None intrinsic: the function performs pure computation and returns a list. No I/O, no global mutation, and no external service calls occur here. Any side effects would originate from lower-level utilities (none expected).

## Control Flow:
flowchart TD
    A[Call dominant_flat_ninth(note)] --> B[Call dominant_ninth(note) which builds dominant7 + append major9]
    B --> |raises exception (e.g., FormatError, TypeError)| E[Propagate exception to caller]
    B --> |returns res (expected list)| C[Call intervals.minor_second(note)]
    C --> |raises exception (e.g., NoteFormatError, TypeError)| E
    C --> |returns minor_ninth_str| D[Set res[4] = minor_ninth_str]
    D --> F[Return res]
    B --> |returns list shorter than 5 elements| G[Assignment res[4] raises IndexError -> propagate IndexError]

## Examples:
- Normal usage:
    try:
        chord = dominant_flat_ninth("C")
        # expected: ["C", "E", "G", "Bb", "Db"]
    except (NoteFormatError, FormatError, TypeError, IndexError) as exc:
        # handle invalid input or unexpected internal error
        raise

- Defensive caller:
    def safe_build(root):
        try:
            return dominant_flat_ninth(root)
        except NoteFormatError:
            return None  # or translate to a user-friendly error

## `mingus.core.chords.dominant_sharp_ninth` · *function*

## Summary:
Constructs a spelled dominant ninth chord for the given root but with the ninth augmented (sharped), i.e., a dominant seventh plus an augmented ninth.

## Description:
- Known callers:
    - No explicit call sites were discovered in the available repository scan. Typical callers include chord-generation utilities, harmony-processing routines, MIDI/notation exporters, and user APIs that need spelled chord note lists.
    - Typical trigger: when a consumer requests the spelled notes for a dominant chord that includes a raised (sharp) ninth from a single root note string.

- Why this is a separate function:
    - Encapsulates the chord-construction rule "dominant ninth with a sharp ninth" so callers do not need to assemble intervals manually.
    - Delegates construction of the base dominant ninth to dominant_ninth(note) and applies a single deterministic transformation (augment the major second) to produce the sharp ninth. This keeps responsibilities small and ensures consistent spelling rules are reused.

## Args:
    note (str):
        - The root note for the chord.
        - Required format: a non-empty, indexable string whose first character is a natural note letter 'A'..'G'. Accidentals (if present) should use '#' for sharps and 'b' for flats (examples: "C", "C#", "Db", "F##", "Ebb").
        - Interdependencies:
            - The function relies on underlying utilities accessing note[0]; therefore the argument must be indexable and non-empty.
            - The exact input string is preserved as the chord root in the returned list (dominant_ninth returns the root as given).

## Returns:
    list[str]:
        - The result is the list produced by dominant_ninth(note) with its fifth element (index 4, the ninth) replaced by the augmented major second computed from the root.
        - Expected structure (5 elements):
            0. root (the exact string passed in)
            1. major third above the root
            2. perfect fifth above the root
            3. minor seventh above the root
            4. augmented major ninth above the root (computed by intervals.major_second(note) then transformed with notes.augment)
        - Examples:
            - dominant_sharp_ninth("C")  -> ["C", "E", "G", "Bb", "D#"]
            - dominant_sharp_ninth("F#") -> ["F#", "A#", "C#", "E", "G##"]

## Raises:
    - NoteFormatError:
        - Propagated from dominant_ninth or intervals.major_second when the provided note string violates expected formatting (for example empty string or invalid accidental characters).
    - TypeError:
        - May be raised if `note` is not indexable (e.g., None or an int) because dependent utilities access note[0].
    - FormatError:
        - May be propagated from lower-level utilities involved in interval spelling.
    - IndexError:
        - If dominant_ninth(note) returns a list with fewer than five elements, the assignment to res[4] will raise IndexError. This reflects an unexpected/inconsistent behavior from the dominant_ninth implementation.

    Note: This function does not catch exceptions raised by the underlying utilities; such exceptions propagate to the caller.

## Constraints:
    - Preconditions:
        - `note` must be a non-empty, indexable string whose first character is a letter in 'A'..'G'.
        - Accidentals, if present, should use '#' or 'b' characters only, following the expectations of the intervals and notes utilities.
        - The environment must provide dominant_ninth(note), intervals.major_second(note), and notes.augment(note_str) with their standard behaviors.
    - Postconditions:
        - On success, returns a five-element list representing a dominant seventh chord with an augmented ninth. The returned list is the same list object returned by dominant_ninth after its index 4 has been replaced.
        - No global state is modified by this function.

## Side Effects:
    - The function mutates the list object returned by dominant_ninth by replacing its element at index 4 before returning it.
    - No I/O, no network or file access, and no other global state mutations are performed here.

## Control Flow:
flowchart TD
    Start[Start: dominant_sharp_ninth(note)] --> CallDominantNinth[Call dominant_ninth(note)]
    CallDominantNinth --> ReceiveBase[Receive list (expected 4 or 5 elements)]
    ReceiveBase --> CallMajorSecond[Call intervals.major_second(note)]
    CallMajorSecond --> ReceiveSecond[Receive major second spelling (single-note string)]
    ReceiveSecond --> Augment[Call notes.augment(major_second)]
    Augment --> ReplaceNinth[Assign augmented value to res[4]]
    ReplaceNinth --> Return[Return modified list]
    Start -->|invalid note (non-indexable)| TypeErrorNode[TypeError raised by underlying call]
    Start -->|malformed note string| NoteFormatErrorNode[NoteFormatError propagated]
    CallMajorSecond -->|may raise FormatError| FormatErrorNode[FormatError propagated]
    ReplaceNinth -->|if list too short| IndexErrorNode[IndexError raised]
    TypeErrorNode --> EndErr[End with exception]
    NoteFormatErrorNode --> EndErr
    FormatErrorNode --> EndErr
    IndexErrorNode --> EndErr
    Return --> EndSuccess[End successfully]

## Examples:
- Typical successful use:
    - dominant_sharp_ninth("C")  -> ["C", "E", "G", "Bb", "D#"]
    - dominant_sharp_ninth("F#") -> ["F#", "A#", "C#", "E", "G##"]

- Error handling pattern:
    - Wrap calls in try/except to handle malformed input or unexpected lower-level failures:
        - try:
            chord = dominant_sharp_ninth(user_input)
          except (NoteFormatError, FormatError, TypeError, IndexError) as e:
            # handle or report error
            pass

- Notes about augmentation behavior:
    - notes.augment appends '#' to the supplied note string unless that string ends with 'b', in which case it removes the trailing 'b'. Therefore the final spelled ninth may be a single sharp, a double sharp, or a natural depending on how intervals.major_second spelled the interval.

## `mingus.core.chords.eleventh` · *function*

## Summary:
Returns the four pitch classes that form an eleventh chord voicing anchored on the given root note (root, perfect fifth, minor seventh, perfect fourth).

## Description:
This function constructs a simple eleventh-chord voicing by computing the chord tones relative to a supplied root note and returning them as a list of note name strings in the order: root, perfect fifth, minor seventh, perfect fourth.

Known callers within the codebase:
    - No internal callers were found in the provided repository snapshot. This function is a public utility intended for use by higher-level chord construction, analysis, or rendering code elsewhere in applications that use the mingus.core library.

Why this logic is extracted:
    - The responsibility of eleventh is narrowly scoped: compute a specific collection of chord tones (an eleventh voicing) from a single root. Extracting it keeps chord-construction logic modular and reusable for different parts of the system (display, playback, harmony analysis) without duplicating interval calculations.

## Args:
    note (str): The root note name, expressed in the same string format used throughout mingus (examples: "C", "C#", "Db", "Bb", "E-"). The function forwards this value to interval helper functions; it does not validate note semantics itself.
    - Allowed values: any note string accepted by the underlying interval routines.
    - Interdependencies: the validity of 'note' is determined by intervals.perfect_fifth, intervals.minor_seventh, and intervals.perfect_fourth; malformed input will propagate errors from those helpers.

## Returns:
    list[str]: A list of four note name strings in this order:
        1. root (the same object/value passed in)
        2. perfect fifth above the root
        3. minor seventh above the root
        4. perfect fourth above the root

    - Always returns a list of length 4 (barring exceptions).
    - Notes may be enharmonically equivalent (e.g., "E#" vs "F") depending on the interval helpers' conventions.
    - Duplicate pitch names are possible if the interval computations yield identical names under certain inputs or enharmonic conditions.

## Raises:
    - NoteFormatError: Propagated from the underlying interval functions if the supplied note string is malformed or cannot be parsed.
    - FormatError (or other interval-related exceptions): May be raised by the interval helper functions used (perfect_fifth, minor_seventh, perfect_fourth) if they encounter unexpected input or internal errors. This function does not catch these exceptions.

## Constraints:
    Preconditions:
        - The caller must provide a note string in the format expected by mingus interval functions.
        - No None or non-string types unless the interval helpers accept them (not validated here).

    Postconditions:
        - If no exception is raised, the returned value is a list of four note name strings representing the specified eleventh voicing.

## Side Effects:
    - None. The function is pure with respect to program state: it performs no I/O, does not mutate global state, and only returns a newly created list built from the interval helper results.

## Control Flow:
flowchart TD
    Start --> Call_perfect_fifth
    Call_perfect_fifth --> [Success] Call_minor_seventh
    Call_perfect_fifth --> [Error] Raise_Exception
    Call_minor_seventh --> [Success] Call_perfect_fourth
    Call_minor_seventh --> [Error] Raise_Exception
    Call_perfect_fourth --> [Success] Build_list_and_Return
    Call_perfect_fourth --> [Error] Raise_Exception
    Raise_Exception --> End
    Build_list_and_Return --> End

## Examples:
    Example (happy path):
        Input: "C"
        Result: ["C", "G", "Bb", "F"]
        Explanation: perfect fifth of C is G; minor seventh is Bb; perfect fourth is F.

    Example with error handling:
        If a caller cannot guarantee the input format, they should catch NoteFormatError:
        - Attempt to call eleventh(note)
        - If NoteFormatError is raised, handle the invalid note (log, sanitize, or re-raise with more context)

## `mingus.core.chords.minor_eleventh` · *function*

## Summary:
Constructs a five-note minor-eleventh chord built on the provided root and returns the chord tones as a list of pitch name strings.

## Description:
Known callers:
- None found in the supplied context. This function is a small, reusable chord-construction utility intended for use by higher-level chord enumeration, rendering, or analysis routines (the same role as other chord helpers in the chords module).

Why this logic is extracted:
- Building a minor-eleventh chord is a common, self-contained musical operation combining a minor-seventh chord with an added eleventh (a perfect fourth above the root). Extracting it into a separate function centralizes the composition of these two interval computations, avoids duplication, and provides a single helper callers can use when they need all five chord tones.

## Args:
    note (str):
        The root pitch/name for the chord.
        - Required.
        - Format and validation are delegated to the underlying interval helpers (minor_seventh and intervals.perfect_fourth). Typical accepted formats are note names like "C", "C#", "Bb"; octave qualifiers depend on the intervals/notes utilities.
        - There are no other parameters; no interdependencies beyond forwarding this single argument to the helper functions.

## Returns:
    list[str]:
        A list of five pitch-name strings in this exact order:
          1. The original root note argument (returned verbatim).
          2. The minor third above the root (as returned by the minor_triad/minor_seventh helper chain).
          3. The perfect fifth above the root.
          4. The minor seventh above the root.
          5. The perfect fourth above the root (the added "eleventh" tone, computed via intervals.perfect_fourth).
        - On successful completion the list length is always 5.
        - Exact spellings (e.g., "D#" vs "Eb") and octave qualifiers depend on the behavior of the underlying intervals helpers.

## Raises:
    - Any exception raised by minor_seventh(note) or intervals.perfect_fourth(note) is propagated unchanged.
    - Typical exceptions coming from lower-level note/interval parsing utilities include:
        * mingus.core.mt_exceptions.NoteFormatError
        * mingus.core.mt_exceptions.FormatError

## Constraints:
Preconditions:
    - Caller must supply a valid, non-empty string representable as a pitch name by the intervals/notes utilities.
    - The intervals and chords utilities (minor_seventh and intervals.perfect_fourth) must be available at runtime.

Postconditions:
    - If no exception is raised, the function returns a list[str] of length 5 as described in Returns.
    - The function does not modify external or global state.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state; it simply calls pure helper functions.

## Control Flow:
flowchart TD
    Start --> CallMinorSeventh
    CallMinorSeventh --> MinorSeventhOK{minor_seventh succeeded?}
    MinorSeventhOK -- no --> PropagateError1[Propagate exception to caller]
    MinorSeventhOK -- yes --> CallPerfectFourth
    CallPerfectFourth --> PerfectFourthOK{intervals.perfect_fourth succeeded?}
    PerfectFourthOK -- no --> PropagateError2[Propagate exception to caller]
    PerfectFourthOK -- yes --> Concat[Concatenate minor_seventh list + [perfect fourth]]
    Concat --> ReturnList[Return 5-note list]
    ReturnList --> End

## Examples:
Example 1 — typical usage:
    from mingus.core.chords import minor_eleventh

    chord = minor_eleventh("C")
    # Given standard spellings from the intervals helpers, a typical result is:
    # ["C", "Eb", "G", "Bb", "F"]

Example 2 — handling invalid input:
    from mingus.core.chords import minor_eleventh
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        chord = minor_eleventh("H#")  # malformed or unsupported note name
    except (NoteFormatError, FormatError) as e:
        # Handle or report invalid note format
        print("Invalid note format:", e)

## `mingus.core.chords.minor_thirteenth` · *function*

## Summary:
Constructs and returns the spelled pitch names comprising a minor thirteenth chord built on the given root note by composing a minor ninth and the spelled major sixth.

## Description:
Known callers:
- None discovered in the scanned repository. Typical callers are higher-level chord-generation utilities, harmony analysis or rendering routines, and user-facing code that needs spelled chord tone lists (e.g., MIDI export, notation rendering, or chord voicing tools).

Context and responsibility:
- This function composes two existing operations:
  1. minor_ninth(note) — constructs the five-tone minor ninth chord by taking the four tones of a minor seventh on the given root and appending the major ninth (a major second above the root). That helper returns the five pitch names [root, minor third, perfect fifth, minor seventh, major second].
  2. intervals.major_sixth(note) — computes the spelled major sixth (the thirteenth) above the root.
- The function appends the spelled major sixth returned by intervals.major_sixth to the five-tone list returned by minor_ninth, producing the conventional six-tone "minor thirteenth" spelling. Extracting this composition centralizes the combination rule so callers do not duplicate the compose/append pattern.

## Args:
    note (str):
        The root pitch/name for the chord.
        - Required.
        - Expected format: a one-note string whose first character is a natural letter A–G; optional accidentals may follow (e.g., "C", "C#", "Db", "F##", "Ebb"). The exact accepted formats and validation are those enforced by the underlying intervals and notes helpers.
        - The value is passed to minor_ninth(note) and to intervals.major_sixth(note); callers must satisfy constraints those helpers expect (non-empty, indexable string, valid note spelling, etc.).

## Returns:
    list[str]:
        A list of spelled pitch name strings representing the minor thirteenth chord in this exact order:
          1. Root
          2. Minor third above the root
          3. Perfect fifth above the root
          4. Minor seventh above the root
          5. Major second above the root (the ninth) — supplied by minor_ninth
          6. Major sixth above the root (the thirteenth) — appended by this function using intervals.major_sixth
        - Typical return length is 6 (five from minor_ninth plus the appended major sixth).
        - Exact accidental spellings and any octave qualifiers are determined entirely by the underlying intervals/notes helpers.

## Raises:
    - Exceptions raised by minor_ninth(note) or intervals.major_sixth(note) propagate unchanged to the caller.
    - Typical exception types that may originate from those helpers include:
        * mingus.core.mt_exceptions.NoteFormatError — when the input cannot be parsed as a valid pitch string.
        * mingus.core.mt_exceptions.FormatError — when the input format violates expected patterns.
        * IndexError — if the input is an empty string and a helper indexes into it.
        * TypeError — if the input is not indexable (e.g., None or a non-string).
    - This function does not perform additional validation or raise new exception types itself.

## Constraints:
Preconditions:
    - The caller must provide a note value acceptable to the intervals/notes utilities (generally a non-empty string whose first character is A–G; accidentals optional).
    - The minor_ninth helper and intervals.major_sixth must be available in the runtime environment.

Postconditions:
    - On successful return (no exception), the function returns minor_ninth(note) concatenated with [intervals.major_sixth(note)], yielding a six-element list of spelled chord tones in the order described under Returns.
    - No global state is modified; no I/O is performed.

## Side Effects:
    - None localized to this function. It calls pure helper functions and does not perform file, network, or stdout/stderr I/O, nor does it mutate global variables.
    - Any side effects would be the result of side effects in the called helpers (none expected for standard interval/chord computations).

## Control Flow:
flowchart TD
    Start --> CallMinorNinth[Call minor_ninth(note) -> five_tone_list]
    CallMinorNinth --> MinorNinthOK{minor_ninth succeeded?}
    MinorNinthOK -- no --> PropagateError1[Propagate exception to caller]
    MinorNinthOK -- yes --> CallMajorSixth[Call intervals.major_sixth(note) -> major_sixth_note]
    CallMajorSixth --> MajorSixthOK{intervals.major_sixth succeeded?}
    MajorSixthOK -- no --> PropagateError2[Propagate exception to caller]
    MajorSixthOK -- yes --> Concat[Return five_tone_list + [major_sixth_note]]
    Concat --> End

## Examples:
Example 1 — typical usage:
    from mingus.core.chords import minor_thirteenth

    chord = minor_thirteenth("C")
    # Typical expected result (dependent on intervals helpers):
    # ["C", "Eb", "G", "Bb", "D", "A"]

Example 2 — handling invalid input:
    from mingus.core.chords import minor_thirteenth
    from mingus.core.mt_exceptions import NoteFormatError, FormatError

    try:
        chord = minor_thirteenth("H#")  # malformed or unsupported note name
    except (NoteFormatError, FormatError, IndexError, TypeError) as e:
        # Handle invalid note format or type issues
        print("Invalid note:", e)

Implementation note:
    - Reimplementation recipe: call minor_ninth(note) (which itself returns minor_seventh(note) + [intervals.major_second(note)]) to obtain the five-tone list, call intervals.major_sixth(note) to obtain the spelled major sixth (a single string), append that string to the five-tone list, and return the resulting six-element list. Allow exceptions from the helpers to propagate.

## `mingus.core.chords.major_thirteenth` · *function*

## Summary:
Returns a spelled major-thirteenth chord (six notes) built from a single root note by extending the spelled major-ninth chord with the spelled major sixth (the thirteenth degree).

## Description:
- Known callers: None discovered in the scanned repository. Typical use cases include chord-generation utilities, harmony/voicing builders, MIDI/notation exporters, or user code that needs a fully spelled major-thirteenth chord from a root note.
- Context: This function composes two smaller responsibilities into one high-level helper:
    * It reuses the spelled five-note major-ninth chord produced by the major_ninth helper.
    * It appends the spelled major sixth (which represents the thirteenth degree) produced by the intervals module.
- Reason for being a separate function: Encapsulates the common pattern "major-ninth + major thirteenth" so callers can request a complete spelled major-thirteenth chord with a single call. Delegating interval spelling to the intervals utilities ensures consistent accidental choices and reduces repeated composition logic across callers.

## Args:
    note (str): Root note string.
        - Required format: a non-empty single-note string whose first character is a natural note letter (A–G) and whose optional subsequent characters are accidentals using '#' or 'b'. Examples: "C", "C#", "Db", "F##", "Ebb".
        - This function forwards the argument unchanged to major_ninth and intervals.major_sixth; it does not normalize or alter the input.
        - Interdependencies: The argument must be acceptable to the package's notes/intervals utilities; malformed or non-string inputs will raise exceptions from downstream utilities.

## Returns:
    list[str]: A six-element list of spelled note strings representing the major-thirteenth chord built on the given root.
        - Composition: The returned list is equal to major_ninth(note) (a five-element list) with one additional element appended: intervals.major_sixth(note).
        - Each element is a spelled note string (no explicit octave) following the intervals module's spelling/accidental conventions.
        - Edge cases:
            * If major_ninth or intervals.major_sixth returns unexpectedly malformed results (which would indicate deeper errors), those values are propagated; the function itself performs no additional validation.

## Raises:
    NoteFormatError:
        - Condition: Propagated if the provided note string is malformed or cannot be parsed by major_ninth or intervals.major_sixth.
    FormatError:
        - Condition: Propagated if the intervals utilities encounter internal formatting or construction errors while building the interval.
    IndexError:
        - Condition: If an empty string ("") is passed, downstream code that accesses note[0] will raise IndexError.
    TypeError:
        - Condition: If the provided note is not a string (or otherwise incompatible with string operations expected by downstream helpers), built-in errors from the helpers will be propagated.

## Constraints:
    Preconditions:
        - Caller must pass a non-empty single-note string starting with A–G, optionally followed by accidentals ('#' or 'b').
        - The intervals and notes utilities used by major_ninth and intervals.major_sixth must be available and correct.
    Postconditions:
        - On success, returns exactly six spelled note strings: the 5-element major_ninth output followed by the spelled major sixth (thirteenth degree).
        - The accidental spellings reflect the intervals module's augmentation/diminution logic to match semitone targets.

## Side Effects:
    - None local to this function: no I/O, no global state mutation, and no external service calls.
    - Any side effects would originate from lower-level utilities (not expected in normal use).

## Control Flow:
flowchart TD
    A[Call major_thirteenth(note)] --> B{Is note a non-empty string?}
    B -- No (empty string) --> C[Downstream access note[0] -> IndexError raised]
    B -- No (non-string) --> D[Downstream string ops -> TypeError or other built-ins raised]
    B -- Yes --> E[Call major_ninth(note) -> 5-element list]
    E --> F[Call intervals.major_sixth(note) -> spelled_sixth]
    F --> G{Intervals may augment/diminish to match semitone target}
    G --> H[Receive spelled_sixth]
    H --> I[Return major_ninth_list + [spelled_sixth]] 
    E --> J[Parsing/format errors -> NoteFormatError or FormatError propagated]
    F --> J

## Examples:
- Basic usage:
    try:
        chord = major_thirteenth("C")
        # chord is a list of 6 spelled notes: major_ninth("C") extended with intervals.major_sixth("C")
    except (NoteFormatError, FormatError, IndexError, TypeError) as e:
        # Input was malformed or a downstream error occurred
        raise

- Defensive validation before calling:
    if not isinstance(root, str) or root == "" or root[0].upper() not in "ABCDEFG":
        raise ValueError("root must be a non-empty single-note string starting with A-G")
    chord = major_thirteenth(root)

## `mingus.core.chords.dominant_thirteenth` · *function*

## Summary:
Returns the spelled notes of a dominant thirteenth chord by taking the spelled dominant ninth for the given root and appending the major sixth (the thirteenth) above that root.

## Description:
- Known callers:
    - No explicit call sites were discovered in the available repository scan. Typical callers include chord-generation utilities, harmony-processing routines, MIDI/notation exporters, and user APIs that request spelled chord tone lists.
    - Typical trigger: when a consumer requests the spelled notes for a dominant thirteenth chord from a single root note string.
- Relationship to dependencies:
    - This function delegates the first five chord tones to dominant_ninth(note). As documented for dominant_ninth, that function composes "dominant seventh + major ninth" and returns a five-note list: [root, major 3rd, perfect 5th, minor 7th, major 9th].
    - It then appends the result of intervals.major_sixth(note) to form the thirteenth (sixth) chord tone. This keeps construction rules localized in the respective utilities.

## Args:
    note (str):
        - The root note as a non-empty, indexable note string.
        - Required format: first character must be a natural note letter 'A'..'G'. Subsequent characters (if present) should be accidentals using '#' for sharps or 'b' for flats (examples: "C", "C#", "Db", "F##", "Ebb").
        - The function relies on the same formatting and validation semantics as dominant_ninth and intervals.major_sixth; passing None, an integer, or an empty string may raise TypeError or NoteFormatError from those delegated calls.
        - No normalization is performed: the exact input string is returned as the first element of the output list.

## Returns:
    list[str]:
        - A list of six spelled note strings in this order:
            0. root (the exact string passed in)
            1. major third above the root
            2. perfect fifth above the root
            3. minor seventh above the root
            4. major ninth above the root (the ninth supplied by dominant_ninth)
            5. major sixth above the root (the thirteenth supplied by intervals.major_sixth)
        - Example results (spellings depend on the underlying interval utilities):
            - dominant_thirteenth("C") -> ["C", "E", "G", "Bb", "D", "A"]
            - dominant_thirteenth("F#") -> ["F#", "A#", "C#", "E", "G#", "D#"]

## Raises:
    NoteFormatError:
        - Validation and formatting errors originate in the delegated utilities (dominant_ninth and intervals.major_sixth) and are propagated by this function when the provided note string violates expected formatting (for example empty string, invalid first character, or invalid accidental characters).
    TypeError:
        - May be raised if `note` is not indexable (e.g., None or an int) because delegated utilities access note[0]. This arises in the underlying calls rather than in this function itself.
    Other lower-level exceptions:
        - FormatError or other exceptions raised inside intervals, notes, or chord utilities may propagate since this function does not catch exceptions.

## Constraints:
- Preconditions:
    - `note` must be a non-empty, indexable string whose first character is a letter in 'A'..'G'.
    - Accidentals (if any) should use '#' or 'b'.
    - dominant_ninth and intervals.major_sixth must be available and behave according to their documented contracts (dominant_ninth returns the five base chord tones; intervals.major_sixth returns a single spelled note string).
- Postconditions:
    - On success, returns a 6-element list of spelled note strings representing a dominant thirteenth chord.
    - No global state is modified.

## Side Effects:
    - None. The function performs pure computation and delegates to other utilities. It performs no I/O and does not mutate external state. Any side effects would originate from lower-level utilities (none expected).

## Control Flow:
flowchart TD
    A[call dominant_thirteenth(note)] --> B[call dominant_ninth(note) -> 5-note list: root,3,5,b7,9]
    B --> C[call intervals.major_sixth(note) -> single-note string (13th)]
    C --> D[append 13th to 5-note list]
    D --> E[return 6-note list: [root,3,5,b7,9,13]]

## Examples:
- Typical usage:
    try:
        chord = dominant_thirteenth("C")
        # chord == ["C", "E", "G", "Bb", "D", "A"]
    except (NoteFormatError, FormatError) as e:
        # handle invalid input or formatting issues
        pass

- Handling malformed input:
    try:
        chord = dominant_thirteenth("")  # invalid: empty string
    except NoteFormatError as e:
        # recover: prompt user, log error, or provide default
        pass

- Protecting against unexpected types:
    try:
        chord = dominant_thirteenth(None)
    except TypeError:
        # guard against non-indexable inputs
        pass

## `mingus.core.chords.suspended_triad` · *function*

## Summary:
Acts as an alias for constructing a suspended-fourth triad from a single root note, returning the triad's three pitch names.

## Description:
This function is a thin delegator that returns the result of building a suspended-fourth triad for the provided root note. It calls suspended_fourth_triad(note) and returns its value unchanged.

Known callers within the provided codebase snapshot:
    - No direct callers were identified in the provided snapshot. Typically this function is exposed so callers can request a "suspended triad" using the common musical name (sus triad) while the implementation uses the sus4 interval convention.

Why this is a separate function:
    - It exists as a stable, named alias that encodes the musical convention that a "suspended triad" means a suspended-fourth triad in this codebase. Extracting the alias keeps naming consistent and allows external users to call suspended_triad without depending on the explicitly named suspended_fourth_triad implementation.

## Args:
    note (str): Root note identifier in the notation accepted by the library's interval utilities (examples: 'C', 'D#', 'Bb', 'G#4').
        - This value is forwarded verbatim to suspended_fourth_triad and therefore must satisfy the same format requirements as intervals.perfect_fourth and intervals.perfect_fifth.
        - No default value; this argument is required.

## Returns:
    list[str]: A list of three note strings representing the triad constituents:
        - index 0: the original root note (same value passed in)
        - index 1: the perfect fourth above the root (as produced by the underlying interval routine)
        - index 2: the perfect fifth above the root (as produced by the underlying interval routine)

    Edge cases and notes:
        - The function always returns the list produced by suspended_fourth_triad. If the underlying implementation returns a three-element list, this function will also return a three-element list.
        - The exact spelling and octaves of returned notes are determined by the interval functions used by suspended_fourth_triad.

## Raises:
    - Propagates any exception raised by suspended_fourth_triad (and transitively by the interval utilities it calls).
    - Common exceptions callers may encounter (from the codebase imports and typical behavior):
        - mingus.core.mt_exceptions.NoteFormatError: if the supplied note string is not in an accepted format.
        - mingus.core.mt_exceptions.FormatError: for other format-related issues.
    - This function performs no additional validation and does not raise its own new exception types.

## Constraints:
    Preconditions:
        - The caller must provide a non-empty string in a format accepted by the library's interval utilities.
        - No other preconditions are enforced.

    Postconditions:
        - If no exception is raised, the function returns the triad as a list of three strings representing the root, its perfect fourth, and its perfect fifth (in that order).

## Side Effects:
    - None. The function performs no I/O and does not mutate global state. It only calls pure functions and returns their result.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> Call_SuspendedFourth[/"Call suspended_fourth_triad(note)"/]
    Call_SuspendedFourth --> Return_Result[/"Return the list returned by suspended_fourth_triad"/]
    Call_SuspendedFourth -.-> Propagate_Exception((Exception - propagated))

## Examples:
    Example 1 - basic:
        Input: 'C'
        Typical output: ['C', 'F', 'G']
        Explanation: The perfect fourth above C is F; the perfect fifth above C is G.

    Example 2 - accidentals:
        Input: 'G#'
        Typical output: ['G#', 'C#', 'D#']
        Explanation: The perfect fourth above G# is C#; the perfect fifth above G# is D#.

    Example 3 - error handling (conceptual):
        If the input is malformed (for example an empty string or an unrecognized token), the call will raise a NoteFormatError or FormatError coming from the interval utilities; callers wanting robustness should catch these exceptions and handle or sanitize input before calling.

## `mingus.core.chords.suspended_second_triad` · *function*

## Summary:
Return a suspended-second triad (root, major second, perfect fifth) by delegating interval calculations to the intervals utilities.

## Description:
Constructs a three-note suspended-second (sus2) triad using the supplied root value:
- element 0: the supplied root (returned verbatim),
- element 1: the result of intervals.major_second(root),
- element 2: the result of intervals.perfect_fifth(root).

This function is a small, focused utility that centralizes the sus2 construction so callers do not need to call interval helpers directly and to keep chord construction consistent across the codebase.

Known callers:
- No direct callers were found in the provided repository memory snapshot. It is intended for use by higher-level chord-generation, analysis, or rendering code elsewhere in the project.

Why it's separate:
- Encapsulates a common chord shape (root + 2nd + 5th) for reuse.
- Delegates parsing and interval logic to the intervals module, keeping responsibilities separated.

## Args:
    note: A note representation accepted by the project's intervals utilities (commonly a note-name string such as "C", "C#", "Bb", or a project-specific note token).
    - The value is forwarded unchanged to intervals.major_second and intervals.perfect_fifth.
    - The function makes no assumptions about the concrete type beyond it being acceptable to the intervals utilities.

## Returns:
    list: A length-3 list [root, major_second, perfect_fifth].
    - The first element is the exact object/value passed as `note` (no copy performed by this function).
    - The second and third elements are the exact return values from intervals.major_second(note) and intervals.perfect_fifth(note), respectively.
    - The function does not perform any normalization or further validation of the returned interval values.

## Raises:
    - This function does not introduce new exception types. It propagates any exceptions raised by intervals.major_second or intervals.perfect_fifth (for example, parsing/formatting errors originating in the intervals module). Callers should handle exceptions coming from those utilities if needed.

## Constraints:
Preconditions:
    - `note` must be valid according to the intervals utilities used (i.e., intervals.major_second and intervals.perfect_fifth must accept it).
    - The intervals module must be available and correctly implemented.

Postconditions:
    - On success: returns a list of length 3 as described.
    - No global state is modified by this function.

Performance:
    - Time complexity: O(1) aside from the complexity of the delegated interval functions.
    - Memory: allocates a small list of three elements.

## Side Effects:
    - The function itself has no side effects (no I/O, no global state mutation).
    - Any side effects would originate from the called interval utilities.

## Control Flow:
flowchart TD
    A[Start: receive note] --> B[Call intervals.major_second(note)]
    B -->|returns| C[major_second_result]
    B -->|raises| H[Propagate exception]
    A --> D[Call intervals.perfect_fifth(note)]
    D -->|returns| E[perfect_fifth_result]
    D -->|raises| H
    C --> F[Assemble [note, major_second_result, perfect_fifth_result]]
    E --> F --> G[Return assembled triad]

## Examples:
Typical usage (common case):
    >>> suspended_second_triad("C")
    # Expected (typical) result: ["C", "D", "G"]
    # Exact spelling/format depends on the intervals module's formatting rules.

Error handling pattern:
    >>> try:
    ...     triad = suspended_second_triad("InvalidNote")
    ... except Exception as exc:
    ...     # Handle parsing/format errors raised by the intervals utilities
    ...     triad = None

When to use:
    - When you need a sus2 chord representation for analysis, display, or to assemble chord voicings for MIDI playback.
    - Prefer this helper over manually calling intervals.major_second and intervals.perfect_fifth to ensure consistent ordering and to document intent.

## `mingus.core.chords.suspended_fourth_triad` · *function*

## Summary:
Builds a suspended-fourth triad from a single root note by returning the root together with its perfect fourth and perfect fifth.

## Description:
This small utility constructs the note sequence that defines a suspended-fourth triad: [root, perfect fourth above root, perfect fifth above root]. It delegates interval calculation to the core interval functions and therefore only composes those results.

Known callers within the provided code context:
    - No other functions in the provided code snapshot were identified as direct callers of this function. Typical usage is from higher-level chord factories, analysis or rendering code that needs the pitch constituents of an sus4 triad.

Why this is a separate function:
    - The responsibility is a single, well-defined musical transformation (produce an sus4 triad given a root). Extracting this logic keeps chord construction declarative and centralizes the exact ordering and choice of intervals (perfect fourth and perfect fifth), so callers do not need to remember or duplicate the interval sequence.

## Args:
    note (str): A note identifier in the format accepted by mingus' intervals utilities (for example 'C', 'D#', 'Bb', or 'G#4'). This function does not parse or validate the note itself; it forwards the value to intervals.perfect_fourth and intervals.perfect_fifth, so the accepted formats are whatever those functions accept.

## Returns:
    list[str]: A length-3 list of note identifiers:
        - index 0: the original root note (the same object/value passed in)
        - index 1: the perfect fourth above the root (as returned by intervals.perfect_fourth)
        - index 2: the perfect fifth above the root (as returned by intervals.perfect_fifth)

    Possible return shapes/values and edge cases:
        - Always returns a list with exactly three elements when the underlying interval functions succeed.
        - The exact string formatting of the returned notes (enharmonic spellings, octave suffixes) is determined by intervals.perfect_fourth and intervals.perfect_fifth and will be preserved in the returned list.
        - If the underlying interval functions perform transposition that changes octave notation, that change will appear in the returned values.

## Raises:
    - This function does not raise exceptions itself, but it may propagate any exception raised by intervals.perfect_fourth or intervals.perfect_fifth.
      Examples of exceptions commonly used in this module that callers should be prepared to handle include mingus.core.mt_exceptions.NoteFormatError or FormatError when the provided note is not in an accepted format.

## Constraints:
    Preconditions:
        - The provided note must be in a format accepted by the intervals functions called (see Args). No other preconditions are enforced by this function.
    Postconditions:
        - If no exception is raised, the function returns a list of three elements: [root, root + perfect fourth, root + perfect fifth].

## Side Effects:
    - None. This function performs no I/O and does not mutate external state. It only calls pure interval functions and returns their results.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> Call_PerfectFourth[/"Call intervals.perfect_fourth(note)"/]
    Call_PerfectFourth --> Call_PerfectFifth[/"Call intervals.perfect_fifth(note)"/]
    Call_PerfectFifth --> Assemble[/"Assemble list: [note, fourth, fifth]"/]
    Assemble --> Return([Return list])
    Call_PerfectFourth -.-> Exception1((Exception - propagated))
    Call_PerfectFifth -.-> Exception2((Exception - propagated))

## Examples:
    Example 1 - basic:
        Input: 'C'
        Typical output: ['C', 'F', 'G']
        Explanation: perfect fourth above C is F; perfect fifth above C is G.

    Example 2 - accidental:
        Input: 'G#'
        Typical output: ['G#', 'C#', 'D#']
        Explanation: perfect fourth above G# is C#; perfect fifth above G# is D#.

    Example 3 - error handling (pseudo-code):
        - If the input note is not valid for the intervals module, intervals.perfect_fourth or intervals.perfect_fifth may raise a note-format exception. Callers that accept arbitrary input should catch and handle those exceptions.

## `mingus.core.chords.suspended_seventh` · *function*

## Summary:
Constructs an "suspended seventh" chord by combining a suspended-fourth triad built on the given root with the minor seventh above that root, returning the four chord tones as a list of pitch strings.

## Description:
This function composes two focused helpers to produce the chord tones:
- It calls suspended_fourth_triad(note) to obtain the three-note suspended-fourth triad [root, perfect fourth, perfect fifth]. suspended_fourth_triad is a thin pure helper that delegates interval computation to intervals.perfect_fourth and intervals.perfect_fifth.
- It calls intervals.minor_seventh(note) to compute the minor seventh above the root.
- It concatenates the triad list with the single-note list [minor_seventh] and returns the result.

Known callers within the provided code context:
- No direct callers were identified in the provided snapshot. Typical callers are higher-level chord factories, notation renderers, analysis routines, or any component that needs the constituent pitches of a "sus7" chord.

Why this logic is a separate function:
- The musical transformation "sus4 triad plus minor seventh" is a distinct, reusable operation. Centralizing it prevents duplication, ensures a consistent ordering of chord members, and keeps higher-level code declarative.

## Args:
    note (str): Root note string accepted by the intervals utilities (examples: 'C', 'D#', 'Bb', 'G#4').
    Notes on allowed values:
        - The exact accepted formats and parsing rules are determined by the interval helpers (intervals.perfect_fourth, intervals.perfect_fifth, intervals.minor_seventh); this function forwards the input unchanged.
        - There are no additional parameters or interdependencies beyond forwarding the same note to both called helpers.

## Returns:
    list[str]: A 4-element list of note strings in this order:
        - index 0: the original root note (the same value passed in)
        - index 1: the perfect fourth above the root (from suspended_fourth_triad)
        - index 2: the perfect fifth above the root (from suspended_fourth_triad)
        - index 3: the minor seventh above the root (from intervals.minor_seventh)
    Additional notes:
        - The exact string forms (enharmonic spelling, octave annotation) are produced by the underlying interval utilities and are preserved in the returned list.
        - On success, the list always contains exactly four elements.

## Raises:
    - This function does not raise exceptions itself. However, it will propagate exceptions raised by the interval computation helpers that it uses (either directly or indirectly). In particular:
        - Exceptions raised by intervals.perfect_fourth or intervals.perfect_fifth (called inside suspended_fourth_triad) will propagate.
        - Exceptions raised by intervals.minor_seventh will propagate.
      Examples of exception types commonly originating from those utilities include:
        - mingus.core.mt_exceptions.NoteFormatError: when the input note string is malformed or unrecognized.
        - mingus.core.mt_exceptions.FormatError: other formatting/semantic issues.
      The exact exceptions and triggering conditions are defined by the interval helper implementations.

## Constraints:
    Preconditions:
        - The input note must be in a format accepted by the interval helper functions.
    Postconditions:
        - If no exception is raised, the function returns a list of four note strings representing the chord tones in the order: root, perfect fourth, perfect fifth, minor seventh.
        - No global state or external resources are modified.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state. It is a pure composition of interval/chord helper calls.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> Call_Sus4["Call suspended_fourth_triad(note)"]
    Call_Sus4 --> Call_Min7["Call intervals.minor_seventh(note)"]
    Call_Min7 --> Concat["Concatenate: triad + [minor_seventh]"]
    Concat --> Return([Return 4-element list])
    Call_Sus4 -.-> PropagateEx1((Exception - propagated from intervals.perfect_fourth or intervals.perfect_fifth))
    Call_Min7 -.-> PropagateEx2((Exception - propagated from intervals.minor_seventh))

## Examples:
    Example 1 - basic:
        Input: 'C'
        Typical output: ['C', 'F', 'G', 'Bb']
        Explanation: suspended-fourth triad on C is ['C','F','G']; minor seventh above C is 'Bb'.

    Example 2 - accidental:
        Input: 'G#'
        Typical output: ['G#', 'C#', 'D#', 'F#']
        Explanation: suspended-fourth triad on G# is ['G#','C#','D#']; minor seventh above G# is 'F#'.

    Example 3 - error handling (pseudo-code):
        try:
            chord = suspended_seventh(user_input_note)
        except NoteFormatError:
            handle_invalid_note()
        except FormatError:
            handle_other_format_issues()
        else:
            render_chord(chord)

## `mingus.core.chords.suspended_fourth_ninth` · *function*

## Summary:
Constructs a suspended-fourth chord with an added minor-second above the root and returns its constituent notes as a list.

## Description:
Builds the four-note pitch set by taking a suspended-fourth triad (root, perfect fourth, perfect fifth) and appending the minor second above the same root note. This function delegates interval calculation to lower-level interval utilities and a small chord helper, composing their results into a single list.

Known callers within the codebase:
    - None identified in the provided code snapshot. Typical usage is from higher-level chord factories, rendering/voicing code, analysis routines, or any caller that needs the raw pitch constituents of a sus4 chord with a minor second (e.g., for notation, MIDI output, or harmonic analysis).

Why this is a separate function:
    - Encapsulates the specific musical transformation "sus4 + minor second" in one place so callers can request this particular chord shape without duplicating the two-step composition (build sus4 triad, then append minor second). It enforces the ordering of chord tones and isolates dependency on the intervals implementation.

## Args:
    note (str):
        - A note identifier accepted by the project's interval utilities (examples of acceptable forms in the codebase: 'C', 'D#', 'Bb', 'G#4').
        - This value is forwarded unchanged to suspended_fourth_triad and intervals.minor_second, so the exact accepted formats are those accepted by those functions.
        - There are no other parameters and no interdependencies beyond the single note argument.

## Returns:
    list[str]:
        - A list of four note identifier strings representing the chord tones, in this order:
            0: the original root note (the same object/value passed in)
            1: the perfect fourth above the root (as returned by suspended_fourth_triad)
            2: the perfect fifth above the root (as returned by suspended_fourth_triad)
            3: the minor second above the root (as returned by intervals.minor_second)
        - Shape and length:
            - When successful, always returns a list with exactly four elements.
            - Exact enharmonic spelling and any octave suffixes are determined by the called interval functions and are preserved in the returned list.

## Raises:
    - Propagates any exception raised by suspended_fourth_triad or intervals.minor_second.
    - In this codebase common exceptions to be prepared for include:
        - mingus.core.mt_exceptions.NoteFormatError: if the provided note has an invalid format for interval computation.
        - mingus.core.mt_exceptions.FormatError: if an underlying interval helper detects an invalid/unsupported format.
    - No new exception types are raised by this function itself.

## Constraints:
    Preconditions:
        - Caller must provide a note string in a format accepted by the project's interval utilities (see Args).
        - No mutation or preparation of the note is performed by this function.

    Postconditions:
        - If no exception is raised, the returned value is a list of four strings as described in Returns.
        - The returned list preserves the ordering: [root, perfect fourth, perfect fifth, minor second].

## Side Effects:
    - None. This function performs no I/O and does not mutate global state. It is a pure composition of other pure utilities.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> Build_Sus4[/Call suspended_fourth_triad(note)/]
    Build_Sus4 --> Get_Min2[/Call intervals.minor_second(note)/]
    Get_Min2 --> Assemble[/"Assemble result: sus4_list + [min2]"/]
    Assemble --> Return([Return list of 4 notes])
    Build_Sus4 -.-> PropagateEx1((Exception - propagated))
    Get_Min2 -.-> PropagateEx2((Exception - propagated))

## Examples:
    Example 1 - basic composition:
        Input: 'C'
        Behavior: Calls suspended_fourth_triad('C') to obtain ['C', <perfect fourth>, <perfect fifth>], then appends intervals.minor_second('C').
        Output (conceptual): ['C', <result of perfect fourth>, <result of perfect fifth>, <result of minor second>]
        Note: Exact spellings (e.g., 'C#' vs 'Db') depend on the underlying intervals implementation.

    Example 2 - usage with error handling:
        try:
            notes = suspended_fourth_ninth(user_input_note)
            # proceed to render or analyze `notes`
        except (NoteFormatError, FormatError) as e:
            # handle invalid input format coming from interval utilities

    Example 3 - accidental root:
        Input: 'G#'
        Output (conceptual): ['G#', <perfect fourth above G#>, <perfect fifth above G#>, <minor second above G#>]
        Explanation: All interval results are produced by the intervals helpers and preserved without further transformation.

## `mingus.core.chords.augmented_major_seventh` · *function*

## Summary:
Returns the four-note augmented major seventh chord built on the provided root pitch: an augmented triad (root, major third, raised/augmented fifth) followed by the major seventh above the root.

## Description:
This function builds an augmented major-seventh chord in two conceptual steps:
1. Constructs the three-note augmented triad for the given root: root, the major third above the root, and the fifth above the root raised by a semitone (augmented fifth). These steps mirror the exact triad-construction semantics documented for the project's augmented-triad utility (compute major third, compute fifth, then augment the fifth).
2. Appends the pitch a major seventh above the root by calling intervals.major_seventh(note).

Known callers within the codebase:
    - No direct callers were discovered during static analysis. It is intended for higher-level chord-building utilities, music-theory helpers, or user code that needs a textual representation of an augmented major-seventh chord.

Why this logic is extracted:
    - Encapsulates the well-defined responsibility of producing an augmented major-seventh chord so callers do not duplicate interval sequencing and accidental manipulation. Centralizing this logic ensures consistent accidental/interval handling across the codebase.

## Args:
    note (str):
        - The root pitch name on which to build the chord.
        - Accepted formats: any pitch string accepted by the project's note/interval helpers (examples: "C", "C#", "Db", "Bb", "F#").
        - Must be a non-empty string; there is no default value.
        - No additional parameters or interdependencies.

## Returns:
    list[str]:
        - A 4-element list of pitch-name strings in order:
            [root, major_third, augmented_fifth, major_seventh]
        - The first element is the input string (the root).
        - The second and third elements are the major third and the fifth raised by a semitone, produced using the project's interval and note helper rules (i.e., compute major third, compute fifth, then augment the fifth).
        - The fourth element is the pitch a major seventh above the root as returned by intervals.major_seventh(note).
        - Edge cases:
            - Accidentals and enharmonic spellings follow the project's interval/notes helper implementations; this function does not perform additional normalization or enharmonic conversion.

## Raises:
    - Any exception raised by the underlying interval/notes helpers will propagate unchanged. In this codebase those helpers may raise:
        - mingus.core.mt_exceptions.NoteFormatError: when the input note string is not a valid/recognizable note.
        - mingus.core.mt_exceptions.FormatError: for other format-related errors during interval computation.
    - Any other runtime exceptions from helper calls (IndexError, TypeError, etc.) will also propagate because this function does not catch exceptions.

## Constraints:
    Preconditions:
        - The input must be a non-empty string representing a pitch in the project's expected note format.
        - The project's intervals and notes helpers must accept the given note and be able to compute intervals from it.

    Postconditions:
        - On success, returns a list of four pitch-name strings as documented in Returns.
        - The input string is not mutated by this function; it is returned verbatim as the first element.

## Side Effects:
    - None local to this function: no file or network I/O and no global-state mutations.
    - Any side effects would originate from the invoked helper functions; the function itself is a pure composition of helpers.

## Control Flow:
flowchart TD
    Start --> ComputeTriadParts
    ComputeTriadParts --> CallMajorSeventh
    CallMajorSeventh --> ConcatenateResults
    ConcatenateResults --> ReturnChord
    ComputeTriadParts[Compute major third and compute fifth then augment the fifth (augmented triad semantics)]
    CallMajorSeventh[Call intervals.major_seventh(note) -> major_seventh]
    ConcatenateResults[Form [root, major_third, augmented_fifth] + [major_seventh]]
    ReturnChord[Return the 4-element list]

## Examples:
    Typical usage:
        try:
            chord = augmented_major_seventh("C")
            # chord is likely ["C", "E", "G#", "B"] given the project's interval/accidental rules
        except (NoteFormatError, FormatError) as e:
            # handle invalid input or interval computation problems
            raise

    Handling invalid input:
        try:
            augmented_major_seventh("")  # likely to raise NoteFormatError or FormatError
        except Exception as e:
            # validate or report the malformed note string to the caller
            pass

## `mingus.core.chords.augmented_minor_seventh` · *function*

## Summary:
Constructs the four-note chord formed by an augmented triad on the given root plus the minor seventh above that root (returns the augmented triad extended with a minor seventh).

## Description:
This function composes two smaller responsibilities: producing an augmented triad built on the provided root, and computing the minor seventh above that root. It returns a 4-element list representing the chord: [root, major_third, augmented_fifth, minor_seventh].

Known callers within the codebase:
    - No direct callers were discovered during analysis of the repository. The function is intended for use by higher-level chord-building utilities or by user code that needs an augmented triad extended with a minor seventh.

Why this logic is extracted:
    - The operation is a simple, well-defined chord construction composed from two primitives (augmented_triad and intervals.minor_seventh). Extracting it:
        * Avoids duplication where multiple callers need the same chord form.
        * Keeps chord-building semantics (augmented triad + minor seventh) in one place.
        * Allows the implementation to rely on shared interval and note utilities for accidental handling and validation.

## Args:
    note (str): Root pitch name in the project's note format.
        - Examples: "C", "C#", "Db", "Bb", "F#".
        - No default value; this parameter is required.
        - The string must be non-empty and acceptable to the project's interval/note helper functions (intervals.* and notes.*).
        - There are no other parameters or interdependencies.

## Returns:
    list[str]: A 4-element list of pitch-name strings in this order:
        [root, major_third, augmented_fifth, minor_seventh]

    Details:
        - root: exactly the input string (this function does not normalize or rewrite the root).
        - major_third: the note returned by intervals.major_third(note) (a pitch a major third above the root).
        - augmented_fifth: produced by the augmented_triad helper; conceptually intervals.major_fifth(note) raised by one semitone (notes.augment behaviour governs accidentals).
        - minor_seventh: the note returned by intervals.minor_seventh(note) (the pitch a minor seventh above the root).

    Edge / special return cases:
        - Accidentals and enharmonic choices (e.g., "A#" vs "Bb") depend entirely on the helper implementations (intervals.* and notes.*); this function does not perform further normalization.
        - Duplicate pitch names may occur if the interval helpers produce enharmonic duplicates for certain roots; the function returns them as provided by helpers.
        - On success the returned list will always have length 4.

## Raises:
    - Propagates exceptions raised by its helpers. In particular:
        - mingus.core.mt_exceptions.NoteFormatError: if the input note string is not a valid note format according to helper functions.
        - mingus.core.mt_exceptions.FormatError: for other format-related errors reported by interval/note helpers.
    - Any other runtime exceptions raised by augmented_triad or intervals.minor_seventh (e.g., IndexError on malformed internal state) will also propagate because this function does not catch exceptions.

## Constraints:
    Preconditions:
        - The caller must provide a non-empty string representing a pitch in the project's accepted format.
        - The global helper modules (intervals and notes) must be available and behave according to their contracts (able to compute major third, major fifth, and minor seventh).

    Postconditions:
        - If no exception is raised, the function returns a 4-element list as described above.
        - The input string is not modified by the function (it is returned as the first element).

## Side Effects:
    - None within this function:
        - No I/O, no network access, no stdout/stderr output.
        - No mutation of global state or cached data by this function itself.
    - Any side effects would only come from the helpers if those helpers perform side effects (not expected in normal implementations of interval/note utilities).

## Control Flow:
flowchart TD
    Start --> CallAugmentedTriad
    CallAugmentedTriad --> CheckAugmentedTriadSuccess
    CheckAugmentedTriadSuccess --> CallMinorSeventh
    CallMinorSeventh --> CheckMinorSeventhSuccess
    CheckMinorSeventhSuccess --> ReturnChord
    CallAugmentedTriad[Call augmented_triad(note) -> [root, major_third, augmented_fifth]]
    CallMinorSeventh[Call intervals.minor_seventh(note) -> minor_seventh]
    ReturnChord[Return [root, major_third, augmented_fifth, minor_seventh]]
    CheckAugmentedTriadSuccessX[augmented_triad raises exception] --> Exception
    CheckMinorSeventhSuccessX[intervals.minor_seventh raises exception] --> Exception
    Exception[Propagate exception to caller]

## Examples:
    Typical usage (happy path):
        try:
            chord = augmented_minor_seventh("C")
            # Expected chord (depending on helpers' accidental choices): ["C", "E", "G#", "Bb"]
        except (NoteFormatError, FormatError) as e:
            # Handle invalid input or format-related errors
            raise

    Handling invalid input:
        try:
            augmented_minor_seventh("")  # likely to raise NoteFormatError or FormatError
        except Exception as e:
            # Validate or report the user-provided note string
            handle_error(e)

Notes:
    - The exact names of the resulting pitches depend on the intervals/notes helper implementations; treat this function as a thin composer of those utilities rather than a normalizer of note names.

## `mingus.core.chords.dominant_flat_five` · *function*

## Summary:
Constructs a spelled dominant seventh chord on the given root and lowers (flattens) the chord's fifth by one semitone, returning the four spelled notes with the fifth altered to a diminished/five-flat.

## Description:
- Known callers:
    - No explicit internal callers were discovered in the available repository scan. Typical call sites include chord-generation utilities, harmony analyzers, MIDI/notation rendering code, or user-facing APIs that produce spelled chord notes from a single root.
- Context and trigger:
    - Used when a caller needs a dominant-seventh chord variant whose fifth is lowered by a semitone (commonly notated "7(b5)" or "7♭5").
- Why this logic is a separate function:
    - The function composes two small, focused responsibilities: building a standard dominant seventh (delegated to dominant_seventh) and altering the fifth by one semitone (delegated to notes.diminish). Extracting this behavior centralizes the "dominant with flat five" construction so callers do not duplicate the pattern of "build dominant seventh then flatten the fifth", and it keeps accidental-spelling logic confined to the existing notes utility.

## Args:
    note (str): Root note name.
        - Required format: non-empty string whose first character is a natural note letter 'A'..'G' and any subsequent characters (if present) are accidentals (e.g., "#", "b"). Examples: "C", "C#", "Db", "F##", "Ebb".
        - The function passes this string unchanged to dominant_seventh; the exact first element of the returned list will be this same string.
        - If a non-string or empty string is provided, lower-level code (dominant_seventh or notes.diminish) may raise an exception (see Raises).

## Returns:
    list[str]: A list of four spelled note strings in this order:
        - index 0: root (same string passed as `note`)
        - index 1: the major third above the root (from the major triad)
        - index 2: the diminished (flat) fifth — the perfect fifth produced by dominant_seventh lowered by one semitone via notes.diminish
        - index 3: the minor seventh above the root
    - Example outcomes:
        - Input "C" -> dominant_seventh("C") yields ["C", "E", "G", "Bb"]; after flattening the fifth the function returns ["C", "E", "Gb", "Bb"].
        - Input "F#" -> dominant_seventh("F#") yields ["F#", "A#", "C#", "E"]; after flattening the fifth -> ["F#", "A#", "C", "E"] (since notes.diminish("C#") -> "C").

## Raises:
    - NoteFormatError: Propagated from dominant_seventh (or deeper interval/note utilities) when the provided `note` string is not a valid single-note format (e.g., invalid first character, invalid accidentals, or other format validation failures).
    - IndexError: Can occur in these situations:
        - If `note` is an empty string, notes.diminish (which checks note[-1]) may raise IndexError.
        - If dominant_seventh returns an unexpected structure (not a list with at least three elements), attempting to assign res[2] may raise IndexError. This is an implementation-level precondition violation; under normal operation dominant_seventh returns a 4-element list.
    - Other exceptions: Any exceptions raised by dominant_seventh, intervals, or notes utilities (for example FormatError) are propagated; this function does not catch them.

## Constraints:
- Preconditions:
    - `note` must be a non-empty string representing a single musical pitch name whose initial character is A..G and whose accidentals (if any) follow expected notation ("#" or "b"). Callers should validate inputs or be prepared to handle NoteFormatError/IndexError.
    - The environment must provide working implementations of dominant_seventh (returns a 4-element spelled chord list) and notes.diminish (accepts a note string and returns a single note string).
- Postconditions:
    - The returned value is a list of exactly four strings representing a spelled dominant seventh chord whose fifth has been diminished by one semitone.
    - The other chord members (root, major third, minor seventh) are unchanged from the dominant_seventh result.

## Side Effects:
- None. The function performs pure computation and delegates to helper utilities; it does not perform I/O, modify global state, or call external services. Any side effects would originate from lower-level utilities (none expected for standard note computations).

## Control Flow:
flowchart TD
    A[call dominant_seventh(note)] --> B{dominant_seventh succeeds?}
    B -- yes --> C[res := dominant_seventh(note)  (list of 4 notes)]
    B -- no --> D[exception propagated to caller]
    C --> E[call notes.diminish(res[2])  (flatten the 3rd index / fifth)]
    E --> F{notes.diminish succeeds?}
    F -- yes --> G[set res[2] = diminished_fifth]
    F -- no --> H[exception propagated to caller (e.g., IndexError)]
    G --> I[return res (4-element list with flattened fifth)]

## Examples:
- Typical usage (happy path):
    - Input: "C"
      - dominant_seventh("C") -> ["C", "E", "G", "Bb"]
      - notes.diminish("G") -> "Gb"
      - dominant_flat_five("C") -> ["C", "E", "Gb", "Bb"]
- Example showing accidental removal behavior:
    - Input: "F#"
      - dominant_seventh("F#") -> ["F#", "A#", "C#", "E"]
      - notes.diminish("C#") -> "C"
      - dominant_flat_five("F#") -> ["F#", "A#", "C", "E"]
- Error handling:
    - Invalid input:
        try:
            dominant_flat_five("")
        except NoteFormatError:
            # handle invalid note format coming from dominant_seventh
            pass
        except IndexError:
            # handle unexpected empty-string edge in notes.diminish or malformed dominant_seventh output
            pass

## `mingus.core.chords.lydian_dominant_seventh` · *function*

## Summary:
Constructs a Lydian dominant seventh chord spelled as a list of notes by taking a dominant seventh built on the given root and appending the spelled augmented fourth above that root.

## Description:
This small utility composes the Lydian dominant seventh (a dominant seventh with a raised fourth) by:
- Calling the library's dominant_seventh helper to obtain the four-note dominant seventh spelled chord (root, major third, perfect fifth, minor seventh).
- Computing the perfect fourth above the root using the intervals utilities and then augmenting that spelled fourth (e.g., F -> F#) via notes.augment.
- Appending the augmented fourth to the dominant seventh list and returning the resulting list.

Known callers:
- No explicit callers were discovered in the scanned repository. Typical use cases include chord-generation utilities, harmony analysis/arrangement code, MIDI/notation rendering, or user APIs that need a spelled Lydian-dominant chord from a single root note.

Why this is its own function:
- The operation is a concise composition of two well-defined responsibilities (construct a dominant seventh, then compute and augment the fourth). Extracting it avoids repeating "[dominant seventh] + augmented fourth" logic across the codebase and centralizes the spelled-note ordering convention used for this chord type.

## Args:
    note (str): Root note string.
        - Required format: non-empty string whose first character is a natural note letter A–G and any subsequent characters are accidentals using '#' (sharp) or 'b' (flat). Examples: "C", "C#", "Db", "F##", "Ebb".
        - The function does not normalize spellings; the root string is returned verbatim as the first element of the result list.
        - Interdependencies: The argument must satisfy the input constraints of dominant_seventh and the intervals functions; invalid note formats will cause lower-level validation to raise exceptions.

## Returns:
    list[str]: A 5-element list of spelled note strings in this exact order:
        - index 0: root (the original string passed in)
        - index 1: major third above the root (from dominant_seventh)
        - index 2: perfect fifth above the root (from dominant_seventh)
        - index 3: minor seventh above the root (from dominant_seventh)
        - index 4: augmented fourth above the root (computed as notes.augment(intervals.perfect_fourth(root)))
    - Example: lydian_dominant_seventh("C") -> ["C", "E", "G", "Bb", "F#"]
    - Edge values: If underlying utilities produce uncommon enharmonic spellings or multiple accidentals, those spelled note strings are returned unchanged.

## Raises:
    NoteFormatError:
        - Thrown by the underlying intervals/chord utilities (dominant_seventh or intervals.perfect_fourth) when `note` is not a valid single-note string (invalid letter, invalid accidental characters, empty string, etc.). This function does not catch or translate those exceptions.
    IndexError:
        - Can occur when notes.augment attempts to index the last character of its input (it uses note[-1]). If intervals.perfect_fourth(root) were to return an empty string (or if an empty string is passed through), notes.augment will raise IndexError. In practice, interval utilities typically raise NoteFormatError for invalid inputs before this happens, but IndexError is a possible low-level exception given the augment implementation.
    Other exceptions:
        - Any other exceptions raised by the lower-level utilities (FormatError or library-specific errors) may propagate through; callers should handle or document these if they expect potentially invalid inputs.

## Constraints:
    Preconditions:
        - The runtime must provide the intervals and chord helper functions used (dominant_seventh and intervals.perfect_fourth) and the notes.augment function (true for normal use inside this library).
        - `note` must be a non-empty string with a valid note-letter and optional accidentals as described above.
    Postconditions:
        - On successful return, the function yields a list of exactly five spelled note strings representing the Lydian dominant seventh chord: [root, M3, P5, m7, #4].

## Side Effects:
    - None. The function performs pure computation and returns a new list. It does not perform I/O, mutate global state, or call external services. Any side effects would originate from lower-level functions (none of which perform I/O in their visible implementations).

## Control Flow:
flowchart TD
    A[Call lydian_dominant_seventh(note)] --> B{Is `note` provided as a non-empty string?}
    B -->|No| C[lower-level interval/chord functions likely raise NoteFormatError or other exceptions]
    B -->|Yes| D[Call dominant_seventh(note)]
    D --> E{dominant_seventh validates and computes triad + m7}
    E -->|Error| C
    E -->|OK| F[triad_and_m7_list (4 notes) returned]
    F --> G[Call intervals.perfect_fourth(note)]
    G --> H{perfect_fourth validates and computes spelled fourth}
    H -->|Error| C
    H -->|OK| I[receive spelled_fourth string]
    I --> J[Call notes.augment(spelled_fourth)]
    J --> K{augment logic: if last char != 'b' -> append '#', else drop trailing 'b'}
    K -->|OK| L[augmented_fourth string returned]
    L --> M[Append augmented_fourth to triad_and_m7_list]
    M --> N[Return 5-element list: [root, M3, P5, m7, #4]]

## Examples:
- Typical use:
    from mingus.core.chords import lydian_dominant_seventh
    lydian_dominant_seventh("C")
    # Returns: ["C", "E", "G", "Bb", "F#"]

    lydian_dominant_seventh("F#")
    # dominant_seventh("F#") -> ["F#", "A#", "C#", "E"]
    # intervals.perfect_fourth("F#") -> "B", notes.augment("B") -> "B#"
    # Returns: ["F#", "A#", "C#", "E", "B#"]

- Error handling:
    try:
        lydian_dominant_seventh("")   # empty string invalid
    except NoteFormatError:
        # Handle invalid note format (notify user, log, or re-raise)
        pass
    except IndexError:
        # Defensive: in case an empty string propagates to notes.augment, handle or normalize input
        pass

Notes:
- The final (fifth) element is the spelled augmented fourth (the raised 4th scale degree) appended after the four notes of the dominant seventh; this ordering reflects the function's implementation and should be relied upon by callers that depend on a consistent spelled-note ordering.

## `mingus.core.chords.hendrix_chord` · *function*

## Summary:
Returns a five-note spelled chord formed by taking the dominant seventh built on the given root and appending the spelled minor third above the same root.

## Description:
- Known callers in this repository:
    - No explicit call sites were discovered in the available repository scan. Typical usage is from chord-generation utilities, harmony-processing routines, MIDI/notation exporters, or user-facing APIs that produce spelled chord note lists.
- Context / when to call:
    - Use this function when you need a spelled representation of the Hendrix-style chord (a dominant seventh with an added minor third / #9) for rendering, analysis, or MIDI/notation generation.
- Why this logic is a separate function:
    - The function composes two small, reusable operations already provided by the library: obtaining a dominant seventh and computing a minor third above the root. Extracting this composition avoids duplicating the pattern and centralizes the intent ("dominant seventh plus minor third") in one place.

## Args:
    note (str):
        - The root note to build the chord on.
        - Required format: a non-empty string whose first character is a natural note letter A–G and any subsequent characters (if present) are accidentals (commonly '#' or 'b'; repeated accidentals such as 'F##' or 'Ebb' may be accepted depending on the library's interval/notes utilities).
        - The function uses the string as given (it does not perform normalization of the root spelling).
        - The underlying interval utilities expect an indexable string; passing an empty string or a non-string will likely cause a NoteFormatError or another lower-level exception.

## Returns:
    list[str]:
        - A list of five spelled note strings in this order:
            0: root (the exact input string)
            1: major third above the root
            2: perfect fifth above the root
            3: minor seventh above the root
            4: minor third above the root (the appended interval)
        - Provenance:
            - The first four elements are the result returned by dominant_seventh(note) (documented to be the major triad plus minor seventh).
            - The fifth element is the result of intervals.minor_third(note) called directly by hendrix_chord.
        - All spelled forms are produced by the underlying utilities and returned unchanged.
        - Example outputs:
            - hendrix_chord("E") -> ["E", "G#", "B", "D", "G"]
            - hendrix_chord("C") -> ["C", "E", "G", "Bb", "Eb"]

## Raises:
    NoteFormatError:
        - Raised when the provided `note` does not meet the expected single-note format (for example, invalid first character, invalid accidental characters, or empty string). This originates from validation performed by the lower-level interval/notes utilities.
    FormatError and other exceptions from lower layers:
        - Any exceptions raised by the intervals or notes modules will propagate; hendrix_chord does not catch them.

## Constraints:
- Preconditions:
    - `note` must be a non-empty string whose first character is 'A'..'G'.
    - Accidentals (if present) must be accepted by the library's intervals/notes utilities.
    - The environment must provide dominant_seventh and intervals.minor_third.
- Postconditions:
    - The function returns a list of exactly five strings as described in Returns.
    - The returned list's first four elements correspond to the spelled dominant seventh returned by dominant_seventh(note); the fifth is the spelled minor third produced by intervals.minor_third(note).

## Side Effects:
    - None. The function performs pure computation in memory and delegates to helper utilities. It does not perform I/O or mutate global state. Any side effects would originate from lower-level utilities (not expected for standard interval computations).

## Control Flow:
flowchart TD
    Start[Start: call hendrix_chord(note)]
    Start --> Check{Is note a non-empty, valid single-note string?}
    Check -- no --> Err[Lower-level validation raises NoteFormatError / other exception -> propagated]
    Check -- yes --> CallDom[Call dominant_seventh(note) -> 4-note list]
    CallDom --> CallMin3[Call intervals.minor_third(note) -> single note]
    CallMin3 --> Return[Return concatenated list: dominant_seventh_result + [minor_third_note]]
    Err --> EndErr[Exception propagated]

## Examples:
- Typical usage:
    - hendrix_chord("E") returns ["E", "G#", "B", "D", "G"].
    - hendrix_chord("C") returns ["C", "E", "G", "Bb", "Eb"].
- Error handling:
    - If input is invalid (for example, an empty string or an invalid note spelling), callers should catch NoteFormatError:
        - try:
            result = hendrix_chord(user_input)
          except NoteFormatError:
            # validate / report error or re-prompt user
            pass

## `mingus.core.chords.tonic` · *function*

## Summary:
Returns the tonic triad (the triad built on the first degree of the given key's scale).

## Description:
This is a small convenience accessor that obtains the collection of triads for the provided key and returns the first triad (the I chord / tonic). It delegates all scale construction, validation, and caching to the triads(key) function.

Known callers within this codebase:
- None were found in the provided context. Typical callers include:
  - High-level chord or progression builders that need the I (tonic) chord for functional harmony or analysis.
  - User-facing utilities or CLI commands that display or play the tonic chord.
  - Tests or examples that assert the tonic triad for a given key.

Why this logic is a separate function:
- Encapsulates the common operation "get the tonic triad" so callers do not need to call triads(key) and index the result themselves.
- Keeps call sites concise and expressive and centralizes any future change to how the tonic triad is derived (for example, if the library later chooses a different scale-ordering convention).

## Args:
    key (str):
        - The musical key or tonic identifier accepted by the library's keys.get_notes implementation (examples: "C", "G", "F#", "Bb").
        - Required. No default value.
        - Interdependency: the result depends entirely on triads(key), which itself depends on keys.get_notes(key) for the ordered scale notes.

## Returns:
    list[str]:
        - A triad represented as a list of three pitch-name strings: [root, third, fifth].
        - This is the first element (index 0) of the list returned by triads(key).
        - Typical successful example: for key "C", returns ['C', 'E', 'G'].
        - If triads(key) returns a list-like container, the function returns its element at index 0; the exact concrete container type and element shapes follow triads' contract.

## Raises:
    IndexError:
        - If triads(key) returns an empty sequence (no triads), attempting to access index 0 raises IndexError.
    NoteFormatError:
        - Any NoteFormatError raised by triads(key) (commonly propagated from keys.get_notes when the provided key string is invalid).
    Any exception raised by triads(key):
        - Any other exception (KeyError, ValueError, etc.) that triads(key) or underlying helpers raise is propagated unchanged.

## Constraints:
Preconditions:
    - The caller must supply a key string in the format accepted by the keys module.
    - The environment must have the triads function available and working as specified (returns a sequence of triads or raises on invalid input).

Postconditions:
    - On success, returns the first triad from triads(key) and does not mutate any module-level state itself.
    - If an exception is raised by triads(key) or the result is empty, no value is returned and the exception propagates.

## Side Effects:
    - The function itself performs no I/O and mutates no global state.
    - Indirect side effects may occur because triads(key) may cache results or perform other module-level updates; those are effects of triads, not of this accessor.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads[Call triads(key)]
    CallTriads --> TriadsError{triads raised an exception?}
    TriadsError -->|Yes| PropagateErr([Propagate that exception])
    TriadsError -->|No| CheckEmpty{result has element at index 0?}
    CheckEmpty -->|Yes| ReturnFirst([return triads(key)[0]])
    CheckEmpty -->|No| RaiseIndex([raise IndexError])

## Examples:
- Typical successful retrieval:
  - Given a conventional diatonic implementation, tonic("C") returns ['C', 'E', 'G'] (the I triad in C major).

- Handling an invalid key:
  - If the key string is malformed or not recognized by keys.get_notes, triads(key) will raise NoteFormatError which propagates through tonic(key). Callers should catch NoteFormatError to handle invalid input.

- Handling an unexpected empty triad list:
  - If triads(key) unexpectedly returns an empty list, tonic(key) will raise IndexError when attempting to access index 0; callers that cannot assume non-empty results should catch IndexError.

## `mingus.core.chords.tonic7` · *function*

## Summary:
Returns the tonic (first scale-degree) seventh chord for the given key — a four-note chord [root, third, fifth, seventh].

## Description:
Known callers:
    - No internal direct callers were found in inspected snapshots. This function is part of the public mingus.core.chords helper API and is intended for use by higher-level chord/analysis code or by user code that needs the tonic seventh chord quickly.

Purpose and responsibility:
    - This is a convenience wrapper that extracts and returns the first element of the diatonic seventh chords computed by the sevenths helper. It keeps the single-purpose access (get tonic seventh) separate from the bulk computation and caching logic implemented in sevenths.

## Args:
    key (str):
        - A key name or identifier (for example: "C", "G", "F#", "Bb").
        - Must be in a format accepted by mingus.core.keys.get_notes (validation and parsing are delegated to that function).
        - No default; this argument is required.

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the tonic seventh chord in the supplied key, ordered as [root, third, fifth, seventh].
        - Typical example for key "C": ['C', 'E', 'G', 'B'].
        - The returned list is the exact nested list value produced (and possibly cached) by sevenths(key). Mutating the returned list will mutate the cached data structure inside the chords module if sevenths uses caching.

## Raises:
    - mingus.core.mt_exceptions.NoteFormatError:
        - Propagated from keys.get_notes (via the sevenths helper) when the supplied key string is not a valid key format.
    - IndexError:
        - Raised when sevenths(key) returns an empty sequence (so attempting to access element [0] fails). This can occur only if the underlying sevenths helper produces an empty list for the provided key.
    - Any exception raised by sevenths (or the helpers it calls, e.g., seventh/triad/intervals helpers) is propagated unchanged.

## Constraints:
Preconditions:
    - The caller must pass a key string acceptable to the keys module.
    - The module-level helpers (sevenths and the keys/intervals helpers) must be available and functioning.

Postconditions:
    - On successful return, the caller receives a live reference to the tonic seventh chord list produced by sevenths(key). If sevenths uses caching, the returned object may be (directly or indirectly) part of that cache.

## Side Effects:
    - This function itself performs no I/O.
    - Side effects originate from sevenths(key): if sevenths populates or updates a module-level cache, the returned object may be shared; mutating that object impacts future callers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|raises exception| Propagate1[Propagate exception to caller]
    CallSevenths --> ReturnedList[sevenths returns list_of_chords]
    ReturnedList --> CheckEmpty{Is list_of_chords non-empty?}
    CheckEmpty -->|Yes| ReturnFirst[Return list_of_chords[0]]
    CheckEmpty -->|No| RaiseIndexError[Attempt to access [0] -> IndexError]
    ReturnFirst --> End([End])
    RaiseIndexError --> End

## Examples:
Typical successful usage:
    try:
        tonic = tonic7('C')  # returns ['C', 'E', 'G', 'B']
    except Exception as e:
        # Could be NoteFormatError (invalid key) or other underlying errors
        print("Failed to get tonic seventh:", e)

Handling invalid key:
    try:
        tonic = tonic7('InvalidKeyName')
    except NoteFormatError:
        print("The supplied key string is invalid.")

Handling possible empty-result IndexError (defensive):
    try:
        tonic = tonic7('C')
    except IndexError:
        # Defensive fallback if the underlying helper returns no chords
        tonic = None
    except Exception as e:
        # Other failures (propagated from underlying helpers)
        raise

## `mingus.core.chords.supertonic` · *function*

## Summary:
Return the triad built on the second (supertonic) degree of the given key's scale.

## Description:
Known callers within the codebase:
    - No direct callers were provided in the supplied context. Typical callers (not discovered here) include chord/progression builders, analysis utilities, or user-facing helpers that need the chord built on the supertonic scale degree.

Context and rationale:
    - This function is a small convenience wrapper that extracts a single triad from the full set produced by the triads(key) helper. Extracting this logic into its own function centralizes the intent ("give me the supertonic triad") and hides the indexing detail (index 1) from callers. It also preserves the single-responsibility pattern: callers request a specific chord instead of retrieving and indexing the entire triads list themselves.

## Args:
    key (str):
        - The musical key / tonic name accepted by mingus.core.keys.get_notes.
        - Examples: "C", "G", "F#", "Bb".
        - Required. No default.
        - Interdependency: Validity and the semantic content of the returned triad depend entirely on keys.get_notes and the triad construction logic used by triads(key).

## Returns:
    list[str]:
        - A triad represented as a list of three pitch-name strings: [root, third, fifth].
        - The returned object is the actual inner triad list from the list returned by triads(key). In other words, this returns a reference to the cached triad element when triads uses its internal cache.
        - Typical successful example for key "C":
            ['D', 'F', 'A']
        - If triads(key) returns fewer than two elements, an IndexError will occur (see Raises).

## Raises:
    IndexError:
        - Raised when triads(key) returns a list with fewer than two elements (so index 1 is out of range). This is unlikely for standard diatonic key implementations (which return 7 scale degrees) but is possible if keys.get_notes or triads behave atypically.

    NoteFormatError (propagated):
        - If keys.get_notes(key) rejects the key format, triads(key) will propagate NoteFormatError; supertonic will likewise propagate it unchanged.

    Any exception raised by triads(key):
        - Any other exception (KeyError, FormatError, or unexpected errors thrown by triad construction or keys.get_notes) will propagate through supertonic.

## Constraints:
Preconditions:
    - The global/fetch helpers used by triads must accept the provided key; in practice, key must be in the format handled by mingus.core.keys.get_notes.
    - triads must return an ordered list of triads where its second element corresponds to the supertonic triad.

Postconditions:
    - On successful return, the caller receives the triad for the supertonic degree as a list of three pitch-name strings.
    - No mutation is performed by supertonic itself, but because the returned list is typically a reference into triads' cached data, its contents may reflect and affect cached state if the caller mutates the list.

## Side Effects:
    - No I/O, network, or external persistent state changes are performed by supertonic itself.
    - Indirect side effect: because triads(key) typically returns a cached list and supertonic returns a reference to one of its inner lists, mutating the returned triad (e.g., triad[0] = 'X') will mutate the cached data held by triads' module-level cache. If callers must avoid modifying shared cache, they should copy the returned list before mutating it.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads[Call triads(key)]
    CallTriads --> TriadsError{triads(key) raised?}
    TriadsError -->|Yes| PropagateError([Propagate exception from triads()])
    TriadsError -->|No| HasSecond{len(result) > 1?}
    HasSecond -->|No| RaiseIndexError([IndexError raised])
    HasSecond -->|Yes| ReturnTriad([return result[1]])

## Examples:
Example — typical usage:
    try:
        st = supertonic("C")
        # Expected: ['D', 'F', 'A'] for a conventional diatonic implementation
        print("Supertonic triad of C:", st)
    except Exception as e:
        print("Failed to get supertonic triad:", e)

Example — guarding against mutation of cached data:
    tri = supertonic("C")
    tri_copy = list(tri)  # or tri.copy()
    tri_copy[0] = "Db"    # safe mutation that does not affect cache

Example — handling invalid key:
    try:
        supertonic("InvalidKey")
    except NoteFormatError as e:
        # keys.get_notes (via triads) will raise NoteFormatError for an unrecognized key format
        print("Bad key:", e)
    except IndexError:
        # Defensive: triads returned too few scale degrees
        print("Scale did not contain a supertonic degree")

## `mingus.core.chords.supertonic7` · *function*

## Summary:
Returns the diatonic seventh chord built on the supertonic (second scale degree) of the supplied key as a list of four pitch-name strings.

## Description:
- Known callers:
    - No internal direct callers were found in the provided code snapshots. This function is provided as a small convenience helper in the public chord API for client code or higher-level analysis code that needs the supertonic seventh chord directly.
- Why this is a separate function:
    - This function encapsulates the common one-liner operation of obtaining all diatonic seventh chords for a key and selecting the second element. It hides the cache/collection semantics of the underlying helper and provides a clear, intention-revealing API for callers who only need the supertonic seventh chord.

## Args:
    key (str):
        - The key context used to determine scale degrees (examples: "C", "G", "F#", "Bb").
        - Must be in a format accepted by mingus.core.keys.get_notes. No default — the argument is required.
        - Note: the exact validation of the key string is performed by the underlying sevenths(keys) and keys.get_notes implementations.

## Returns:
    list[str]:
        - A 4-element list of pitch-name strings representing the supertonic seventh chord in the form [root, third, fifth, seventh].
        - Example (typical for C major): ['D', 'F', 'A', 'C'].
        - The returned list is the same object stored inside the module-level cache managed by sevenths(). Therefore, callers receive a direct reference to cached data (mutating the list or its elements mutates the cached value).

## Raises:
    - Propagated exceptions from sevenths(key):
        - mingus.core.mt_exceptions.NoteFormatError (or other exceptions raised by keys.get_notes) if the provided key is invalid.
        - Any exception raised by the lower-level helpers that construct seventh chords (for example, exceptions raised when constructing a chord for an invalid note) will propagate unchanged.
    - IndexError:
        - Raised when the list returned by sevenths(key) has fewer than two elements (i.e., there is no second scale degree in the returned sequence).
        - This is the direct result of performing [1] indexing on the returned sequence.
    - (Note: TypeError may occur if sevenths(key) returns a non-subscriptable value; such behavior would indicate a deeper invariant violation in the helper.)

## Constraints:
- Preconditions:
    - key must be a valid key string accepted by the keys module (keys.get_notes).
    - The module-level cache used by sevenths() is expected to be present and correctly typed (an indexable mapping whose values are sequences of chord lists).
- Postconditions:
    - On successful return, the caller receives a list of exactly four pitch-name strings corresponding to the supertonic seventh chord.
    - The returned object is (usually) an element of the cached list produced by sevenths(key); its identity equals the cached nested list object.

## Side Effects:
- Mutates module-level state indirectly:
    - If sevenths(key) computes the diatonic seventh chords for the key (cache miss), it will populate the module-level cache. This function then returns an element of that cached result.
    - Because the returned chord list is a direct reference to cached data, any in-place mutation by the caller (changing items, appending/removing elements) will modify the cached value and be visible to subsequent callers.
- No file, network, stdout I/O is performed by this function itself.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|raises exception| Propagate1[Propagate exception to caller]
    CallSevenths --> IndexSecond[Attempt to access index 1 of returned sequence]
    IndexSecond -->|success| ReturnChord[Return that chord list]
    IndexSecond -->|IndexError or TypeError| Propagate2[Propagate indexing exception to caller]
    ReturnChord --> End([End])

## Examples:
- Typical successful use (conceptual):
    - Input: key = "C"
    - Underlying sevenths("C") typically returns the seven diatonic seventh chords:
        [
          ['C','E','G','B'],
          ['D','F','A','C'],
          ['E','G','B','D'],
          ...
        ]
    - Output (supertonic seventh): ['D','F','A','C']

- Error scenario (invalid key):
    - If the provided key is not recognized by keys.get_notes, the underlying call to sevenths(key) will raise a NoteFormatError which propagates to the caller.

- Cache/mutation caveat:
    - Because the returned list is a direct reference to the cached chord list, in-place modification by the caller will affect future results returned by this function for the same key.

## `mingus.core.chords.mediant` · *function*

## Summary:
Returns the triad built on the mediant (third) degree of the given key's scale as produced by the triads generator.

## Description:
- Known callers within the provided codebase/context:
    - No callers were discovered in the supplied repository context. This helper is typically used by higher-level chord/progression builders, analysis tools, or any code that needs a single triad from a key (specifically the mediant triad).
- Rationale for extracting this logic:
    - Encapsulates the simple but common operation "take the list of triads for a key and return the third-degree triad". This keeps callers concise and centralizes the index choice (0-based index 2) so callers do not need to depend on the internal ordering of triads or repeatedly index into the triads list.
    - Delegates scale and triad construction, caching, and validation to triads(key) so mediant remains a single-purpose accessor.

## Args:
    key (str):
        - The musical key / tonic identifier accepted by mingus.core.keys.get_notes and by triads(key).
        - Examples: "C", "G", "F#", "Bb" depending on project conventions.
        - Required: no default. The exact accepted formats and accidentals are governed by keys.get_notes.

## Returns:
    list[str]:
        - The triad built on the mediant degree: a list of three pitch-name strings in the order [root, third, fifth].
        - Typical example: mediant("C") -> ['E', 'G', 'B'] (assuming a conventional diatonic triads implementation).
        - The returned list is the same list object taken from the list returned by triads(key). If triads uses a cache, the returned list is a direct reference into that cached structure.

## Raises:
    NoteFormatError
        - Propagated from keys.get_notes (via triads) when the provided key is not a recognized/valid key representation.
    IndexError
        - Raised if triads(key) returns a list with fewer than 3 elements (i.e., no mediant triad is available). This function does not guard against that and will propagate the IndexError from the list indexing operation.
    Any exception raised by triads(key) or its helpers
        - Any other exception (for example KeyError or custom exceptions) thrown during triad construction in triads(key) or its callees will propagate unchanged.

## Constraints:
Preconditions:
    - The provided key must be in a format accepted by keys.get_notes (as used by triads).
    - The triads(key) implementation must return an ordered iterable with at least three elements for a mediant to exist.

Postconditions:
    - If no exception is raised, the function returns a list of three pitch-name strings representing the mediant triad for the given key.
    - No new module-level state is directly modified by mediant; however, triads(key) may mutate or populate its module cache (so calling mediant may indirectly cause caching).

## Side Effects:
    - No direct I/O or external service calls.
    - Indirect: calls triads(key), which may populate or update triads' module-level cache. The returned triad is a reference into triads(key)'s returned list (and thus into any cache). Mutating the returned list will mutate the cached entry in triads' storage.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads([call triads(key)])
    CallTriads --> TriadsError{triads(key) raised?}
    TriadsError -->|Yes| PropagateTriadsError([propagate exception])
    TriadsError -->|No| IndexAccess([access index 2 of returned list])
    IndexAccess --> IndexErrorCheck{index 2 exists?}
    IndexErrorCheck -->|No| PropagateIndexError([propagate IndexError])
    IndexErrorCheck -->|Yes| ReturnTriad([return triads(key)[2]])

## Examples:
Example — typical successful usage:
    try:
        m = mediant("C")
        # Expected (conventional diatonic result): ['E', 'G', 'B']
        print("Mediant triad for C:", m)
    except Exception as exc:
        print("Could not obtain mediant triad:", exc)

Example — handling invalid key:
    try:
        mediant("InvalidKey")
    except NoteFormatError as e:
        # keys.get_notes (via triads) reported an invalid key format
        print("Bad key provided:", e)

Example — guarding against missing mediant (defensive):
    try:
        m = mediant("SomeNonstandardScale")
    except IndexError:
        # triads returned too few elements; no mediant degree present
        print("Mediant degree not available for this key/scale")
    except Exception as e:
        # Other propagated errors from triads/intervals/notes
        raise

## `mingus.core.chords.mediant7` · *function*

## Summary:
Returns the diatonic seventh chord built on the mediant (third) scale degree of the supplied key.

## Description:
Known callers:
    - No internal direct callers were found in the provided repository snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for use by library consumers or higher-level analysis code that needs the mediant seventh chord for a given key.

Typical trigger / pipeline stage:
    - Called when code needs a single seventh chord corresponding to the mediant (3rd) degree of a key's diatonic scale (for example, when generating chord progressions, performing harmonic analysis, or rendering chord labels).

Why this logic is extracted into its own function:
    - Responsibility boundary: it provides a clear, self-documenting accessor for the mediant seventh chord. Centralizing the intent ("give me the mediant seventh") avoids duplicating indexing logic against the multi-chord result returned by sevenths(...), and it reuses sevenths(...) caching and construction behavior.

## Args:
    key (str):
        - The musical key context (examples: "C", "G", "F#", "Bb"). Must be a format accepted by mingus.core.keys.get_notes.
        - Required positional argument; no default.
        - Interdependencies: correctness and validity of the key string depend on the keys module. If keys.get_notes rejects the key, that error propagates via the called helpers.

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the seventh chord built on the mediant scale degree: [root, third, fifth, seventh].
        - Example for "C" (conventional C major): ['E', 'G', 'B', 'D'] (the mediant seventh chord for C major).
        - On success, the returned list object is the same nested chord list element returned from sevenths(key)[2]. Because sevenths(...) uses module-level caching, callers receive a reference into that cached structure.
        - Edge-case returns:
            - If the underlying sevenths(key) returns a list with fewer than 3 elements, an IndexError will be raised (see Raises).

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Propagated from keys.get_notes when the provided key string is invalid or not understood by the keys module.
    IndexError:
        - Raised when sevenths(key) returns a list with length <= 2 such that index 2 is out of range (e.g., non-standard or malformed scale data).
    Any exception raised by sevenths or lower-level helpers:
        - Any other exception raised during the construction of the seventh-chord list (for example errors from interval computations or invalid note names) is propagated unchanged.

## Constraints:
Preconditions:
    - key must be a str acceptable to mingus.core.keys.get_notes.
    - The module-level cache and the sevenths helper must exist in the same module namespace.
Postconditions:
    - If successful, returns the element at index 2 (the third element) from the list returned by sevenths(key). No mutation is performed by this function itself.
    - The returned list reference may be identical to an element inside a cache maintained by sevenths(...); subsequent external mutation of that list will affect the cached state.

## Side Effects:
    - No I/O (no file, network, or stdout activity) is performed by this function.
    - Returns a reference into the cached structure produced by sevenths(key). If a caller mutates the returned list or its contents, that mutation alters the module-level cached data and will be visible to other callers of sevenths(key) or mediant7(key).
    - The function does not itself modify global state; any cache mutation is performed inside sevenths(...) on a cache miss.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|raises NoteFormatError or other| PropagateErr[Propagate exception to caller]
    CallSevenths --> GotList{Is result a list with len > 2?}
    GotList -->|No| RaiseIndex[Raise IndexError (index 2 out of range)]
    GotList -->|Yes| ReturnChord[Return result[2] (the mediant seventh)]
    ReturnChord --> End([End])

## Examples:
Typical successful usage:
    # Request the mediant seventh chord for C major:
    try:
        chord = mediant7('C')
        # chord is typically: ['E', 'G', 'B', 'D']
    except Exception as e:
        # Handle unexpected error
        print("Failed to get mediant7:", e)

Handling invalid key names:
    try:
        mediant7('InvalidKeyName')  # keys.get_notes inside sevenths will raise NoteFormatError
    except NoteFormatError as e:
        print("Invalid key provided:", e)

Handling unexpected scale shapes (safe access):
    try:
        chord = mediant7(some_key)
    except IndexError:
        # sevenths(some_key) did not contain a mediant degree
        print("Mediant chord not available for key:", some_key)
    except NoteFormatError as e:
        print("Bad key format:", e)

Mutation caveat (cache identity):
    chords = mediant7('C')
    # chords is a reference to a cached nested list. Mutating it will affect the cached data:
    chords[0] = 'E_mod'  # modifies the cached chord data globally

## `mingus.core.chords.subdominant` · *function*

## Summary:
Returns the triad built on the subdominant scale degree (the IV chord) for the given key.

## Description:
Known callers:
    - No direct callers were found in the supplied context. Typical callers include chord progression builders, analysis utilities, or any code that needs the IV (subdominant) triad for harmonic processing.

Why this is a separate function:
    - Encapsulates the common convenience operation "get the IV triad for a key" so callers do not need to call triads(key) and index it manually. It isolates the indexing logic (degree selection) from triad construction and keeps call sites concise and expressive.

## Args:
    key (str):
        - The musical key / tonic name as accepted by mingus.core.keys.get_notes and passed through to triads(key).
        - Examples: "C", "G", "F#", "Bb".
        - This parameter is required. There is no default.
        - Interdependency: the returned triad depends entirely on triads(key) which itself depends on keys.get_notes(key).

## Returns:
    list[str]:
        - A triad represented as a list of three pitch-name strings: [root, third, fifth].
        - Specifically, returns the triad at index 3 of the list produced by triads(key), which corresponds to the subdominant (IV) degree in conventional scale order.
        - Typical successful example for a diatonic major key:
            - subdominant("C") -> ['F', 'A', 'C']
        - Edge cases:
            - If triads(key) returns fewer than 4 elements, an IndexError will be raised (see Raises).
            - The exact spelling and accidentals of the returned notes follow the underlying keys.get_notes and triad implementations.

## Raises:
    IndexError:
        - Raised when the list returned by triads(key) has fewer than 4 elements (so index 3 is out of range).
        - This is a direct Python indexing error produced by attempting triads(key)[3].

    NoteFormatError:
        - Propagated from triads(key) (via keys.get_notes) when the provided key has an invalid format or is unrecognized by keys.get_notes.
        - Example trigger: keys.get_notes raises NoteFormatError("unrecognized format for key '%s'" % key).

    Any exception raised by triads(key):
        - Any exception that triads(key) raises (KeyError, FormatError, or other exceptions raised by underlying helpers) will propagate unchanged through this function.

## Constraints:
Preconditions:
    - triads must be available in the module namespace and accept the given key.
    - key must be in a format accepted by keys.get_notes (as used by triads).

Postconditions:
    - On successful return, a triad list[str] (the IV chord for the key) is returned.
    - No module-level state is modified by subdominant itself; any caching performed by triads (e.g., _triads_cache) may be updated by triads(key).

## Side Effects:
    - subdominant does not perform I/O or mutate external state by itself.
    - Side effects originate only from triads(key): e.g., triads may populate a module-level cache when computing triads for the key. Those effects are not performed by subdominant directly but will occur as a result of calling triads(key).

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads[Call triads(key)]
    CallTriads --> TriadsError{triads(key) raised exception?}
    TriadsError -->|Yes| PropagateTriadsErr([Propagate underlying exception (NoteFormatError, KeyError, etc.)])
    TriadsError -->|No| IndexAccess[Access index 3: tris = triads(key)[3]]
    IndexAccess --> IndexErrorCheck{Is index 3 in list?}
    IndexErrorCheck -->|No| RaiseIndex([Raise IndexError])
    IndexErrorCheck -->|Yes| ReturnTriad([Return the triad list[str]])

## Examples:
Example — successful usage:
    try:
        iv = subdominant("C")
        # Expected iv (typical diatonic spelling): ['F', 'A', 'C']
        print("IV triad in C:", iv)
    except Exception as e:
        print("Failed to get subdominant:", e)

Example — invalid key (propagated NoteFormatError):
    try:
        subdominant("NotAKey")
    except NoteFormatError as e:
        print("Invalid key format:", e)

Example — insufficient triads length (IndexError):
    # If triads(key) returns a list smaller than 4 elements, indexing fails:
    try:
        subdominant("SomeKeyWithShortScale")
    except IndexError as e:
        print("Scale too short to have a subdominant triad:", e)

## `mingus.core.chords.subdominant7` · *function*

## Summary:
Returns the diatonic seventh chord built on the subdominant (fourth) degree of the supplied key.

## Description:
Known callers within the codebase:
    - No internal direct callers were found in the provided snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for use by higher-level chord/analysis code or by user code that needs the IV7 chord for a given key.

Typical usage context:
    - Called when a consumer needs the single seventh chord whose root is the subdominant (the 4th scale degree) of a given key, e.g., to analyze or render the IV7 chord.

Why this logic is extracted:
    - Responsibility boundary: this function is a small convenience wrapper that isolates the logic of selecting the fourth element from the diatonic seventh-chords list produced by the broader sevenths(key) helper. Extracting it keeps callers simple (they request a specific chord by musical name/intent) and centralizes the indexing semantics (which scale degree corresponds to the subdominant seventh) in one place rather than repeating sevenths(key)[3] throughout the codebase.

## Args:
    key (str):
        - A key name/identifier used as context for building diatonic seventh chords (examples: "C", "G", "F#", "Bb").
        - Must be in a format accepted by mingus.core.keys.get_notes (see keys module); invalid formats will cause downstream errors.
        - No default; this parameter is required.

## Returns:
    list[str]:
        - A list of pitch-name strings representing the subdominant seventh chord for the given key.
        - Typical length and contents: four strings [root, third, fifth, seventh], for example subdominant7('C') -> ['F', 'A', 'C', 'E'].
        - The returned object is the same list object contained at index 3 of the list returned by sevenths(key). Because sevenths(key) uses a module-level cache, the returned list may be a cached object; mutating it will affect the cached data and future callers.

## Raises:
    IndexError:
        - Raised if the list returned by sevenths(key) contains fewer than four elements (i.e., no element at index 3). This can occur for non-standard scales or if an upstream helper returns an unexpectedly short sequence.
    mingus.core.mt_exceptions.NoteFormatError:
        - Propagated when keys.get_notes(key) (called within sevenths) rejects the provided key format.
    Any exception raised by sevenths(key) or its callees:
        - Other exceptions raised while computing the diatonic seventh chords (e.g., errors constructing individual chords) are propagated unchanged.

## Constraints:
Preconditions:
    - The caller must provide a key string in a format accepted by the keys module.
    - The sevenths helper and its module-level cache are available in the module namespace.
Postconditions:
    - On successful return, the caller receives a reference to the fourth entry (index 3) of the list returned by sevenths(key). No additional module-level state is modified by this function itself.
    - If the returned list is mutated by the caller, that mutation may be visible to other callers that receive the cached object.

## Side Effects:
    - No I/O (files, network) is performed.
    - No direct modification of global state is performed by this function. However, because it returns a reference into the (possibly cached) list produced by sevenths(key), callers who mutate the returned list or its nested elements will effectively mutate module-level cached state maintained by sevenths.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|raises exception| Propagate1[Propagate exception to caller]
    CallSevenths --> GetList[Receive list_of_sevenths]
    GetList --> IndexAccess{len(list_of_sevenths) > 3?}
    IndexAccess -->|No| RaiseIndex[Raise IndexError]
    IndexAccess -->|Yes| ReturnChord[Return list_of_sevenths[3]]
    ReturnChord --> End([End])

## Examples:
Typical successful usage:
    try:
        iv7 = subdominant7('C')
        # iv7 is typically ['F', 'A', 'C', 'E']
    except Exception as e:
        # Handle invalid key or other underlying errors
        print("Failed to obtain subdominant seventh:", e)

Example — identity and cache mutation caveat:
    # sevenths('C') returns a cached list L where L[3] is the IV7 chord.
    iv7_a = subdominant7('C')
    # Another call that reads the same cached object:
    iv7_b = sevenths('C')[3]
    assert iv7_a is iv7_b  # same object reference
    # Mutating the returned chord mutates cached data visible to all callers:
    iv7_a[0] = 'F_mod'  # alters cached chord for key 'C'

Example — handling invalid key and short scale:
    try:
        chord = subdominant7('InvalidKeyName')
    except NoteFormatError:
        print("Provided key name has invalid format.")
    except IndexError:
        print("Computed diatonic seventh list is too short to contain a subdominant (index 3).")

## `mingus.core.chords.dominant` · *function*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Returns the triad built on the dominant scale degree (the fifth degree) of the specified key.

## Description:
Known callers within the codebase:
- No direct callers were found in the provided context. Typical callers (not present in the supplied files) are higher-level utilities that need the V chord of a key such as Roman-numeral analyzers, chord-progression generators, accompaniment/harmonic accompaniment functions, or music-theory helpers that ask for a single, conventional functional chord.

Why this logic is extracted into its own function:
- Provides a concise, self-documenting helper to obtain the dominant (V) triad without requiring callers to fetch the full collection of triads and remember the correct index. It encapsulates the semantic intent ("give me the dominant triad") and centralizes error/edge-case behavior (propagated from triads and the indexing operation) so callers remain simpler and less error-prone.

## Args:
    key (str):
        - A key/tonic name or representation accepted by mingus.core.keys.get_notes.
        - Examples: "C", "G", "F#", "Bb" following the project's key format rules.
        - No default — this parameter is required.
        - Interdependency: the result depends on keys.get_notes(key) and the triads helper; if those functions return altered spellings or a different number of scale degrees, the returned triad and its availability will reflect that behavior.

## Returns:
    list[str]:
        - A single triad representing the dominant (fifth-degree) chord of the specified key.
        - The triad is a list of three pitch-name strings: [root_of_V, third_of_V, fifth_of_V].
        - Example expected result for a conventional diatonic key "C": ['G', 'B', 'D'].
        - Edge-case returns:
            * If triads(key) returns a sequence shorter than five elements, this function does not return a value but instead raises IndexError from the indexing operation.
            * No special sentinel values are returned by this function itself — all error conditions raise exceptions.

## Raises:
    IndexError:
        - If the list returned by triads(key) has fewer than 5 elements (so index 4 is out of range).
        - This can occur for non-standard or non-heptatonic scale definitions returned by keys.get_notes or if triads raises a different-shaped result.

    NoteFormatError (or other exceptions raised by triads or keys.get_notes):
        - Propagated unchanged when triads(key) or keys.get_notes(key) raises NoteFormatError for invalid key formats or other validation failures.
        - Any exception raised by triad-building helpers (e.g., KeyError, ValueError) will propagate through this function.

## Constraints:
Preconditions:
    - The provided key must be in a format accepted by mingus.core.keys.get_notes.
    - The underlying triads(key) call is expected to return an indexable sequence (e.g., list-like) of triads.

Postconditions:
    - On successful return, the caller receives the dominant triad as a list of three pitch-name strings.
    - No additional guarantees are made beyond what triads(key) provides about note spellings or caching behavior.

## Side Effects:
    - This function itself performs no I/O and does not mutate external state directly.
    - Any side effects are inherited from triads(key): triads may populate or update a module-level cache when computing the triads for the key.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads[Call triads(key)]
    CallTriads --> TriadsError{triads(key) raised exception?}
    TriadsError -->|Yes| PropagateTriadsError([Propagate exception (e.g., NoteFormatError)])
    TriadsError -->|No| HasIndex{triads list has index 4?}
    HasIndex -->|No| RaiseIndex([Raise IndexError])
    HasIndex -->|Yes| ReturnTriad([Return triads(key)[4]])

## Examples:
Typical usage (happy path):
    - Input: a conventional diatonic key name such as "C".
    - Expected outcome: the dominant triad is returned, for example ['G', 'B', 'D'].

Example — handling invalid key formats:
    - If the caller passes an unrecognized key string, keys.get_notes (via triads) will raise NoteFormatError; this function does not catch it and lets it propagate so the caller can handle/notify.

Example — handling non-heptatonic or unexpected scale shapes:
    - If triads(key) produces fewer than five triads (e.g., a scale with fewer degrees), attempting to access the fifth element raises IndexError; callers that may encounter non-standard scales should catch IndexError and handle it appropriately (e.g., fallback logic or user-facing error).

## `mingus.core.chords.dominant7` · *function*

## Summary:
Returns the dominant seventh chord (the seventh chord built on the 5th scale degree) for the given key as a list of four pitch-name strings.

## Description:
- Known callers within the codebase:
    - No internal direct callers were found in the provided snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for use by higher-level chord/analysis code or by user code that needs the dominant (V7) chord for a given key.
- Typical usage context:
    - Called when a caller needs the V7 chord in a diatonic key context (e.g., for harmonic analysis, chord progression generation, or rendering chord symbols).
- Why this logic is extracted:
    - Responsibility boundary: dominant7 is a small, descriptive helper that isolates the simple semantic operation "give me the dominant seventh of a key". It delegates the heavy lifting (scale retrieval, building all diatonic seventh chords, and caching) to sevenths(key) and merely selects the correct scale degree. Extracting this into a named helper improves readability of caller code and centralizes the index that selects the V7 chord (index 4) rather than having scattered indexing logic.

## Args:
    key (str):
        - The musical key context used to compute the dominant seventh (examples: "C", "G", "F#", "Bb").
        - Must be accepted by mingus.core.keys.get_notes (i.e., follow the note/key formatting rules used by the keys module).
        - No default; this parameter is required.
        - Interdependencies: validity depends on the keys module; if keys.get_notes rejects the key format it will raise NoteFormatError (propagated).

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the dominant seventh chord: [root, third, fifth, seventh].
        - The chord returned is the seventh chord built on the 5th scale degree of the provided key (zero-based index 4 of the list returned by sevenths(key)).
        - Example (C major): ['G', 'B', 'D', 'F'].
        - The returned list is the exact nested chord object taken from the data structure returned (and cached) by sevenths(key). It is not a defensive copy; callers receive a direct reference to the cached chord list.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        - If keys.get_notes(key) (called within sevenths) rejects the provided key format. This originates in the keys module and propagates unchanged.
    IndexError
        - If sevenths(key) returns a list with fewer than 5 elements (i.e., index 4 is out of range). Typical diatonic keys return 7 degrees; IndexError is only expected for malformed or nonstandard results from the underlying helpers.
    Any exception raised by underlying helpers (seventh/triad/intervals)
        - If construction of the seventh chords fails for some note, those exceptions propagate unchanged.

## Constraints:
- Preconditions:
    - key must be a string format accepted by keys.get_notes.
    - The module-level sevenths cache used by sevenths(key) must be present and functioning in the containing module (this is an implementation-level precondition satisfied by the module itself).
- Postconditions:
    - On successful return, the returned object is the nested list representing the dominant seventh chord (the 5th element) from the list returned by sevenths(key).
    - If a cache miss occurred inside sevenths, the module-level cache will be populated with the newly computed list before this function returns.
    - No external I/O or global state is created by this function beyond what sevenths(key) may already perform (i.e., writing into the module-level cache).

## Side Effects:
- No direct I/O (files, network, stdout).
- No direct mutation of external state by this function itself; however:
    - The returned list is a reference to an element of the list returned (and possibly cached) by sevenths(key). If a caller mutates the returned list or its nested items, those mutations will affect the cached data visible to other callers.
    - Exceptions from underlying helpers may be propagated; this function does not catch them.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|raises exception| Propagate1[Propagate exception to caller]
    CallSevenths --> GetList[Receive list_of_sevenths]
    GetList -->|len < 5| IndexError[Raise IndexError (index 4 out of range)]
    GetList -->|len >= 5| SelectChord[Select chord = list_of_sevenths[4]]
    SelectChord --> ReturnChord([Return chord])
    ReturnChord --> End([End])

## Examples:
- Basic: get the dominant seventh for C major
    try:
        v7 = dominant7('C')
        # v7 == ['G', 'B', 'D', 'F']
    except Exception as e:
        # Handle invalid key or other underlying errors
        print("Failed to get dominant seventh:", e)

- Handling an invalid key:
    try:
        v7 = dominant7('InvalidKeyName')  # keys.get_notes inside sevenths will raise NoteFormatError
    except NoteFormatError:
        print("Invalid key provided")

- Mutation caveat (cache visible):
    chords1 = sevenths('C')         # returns cached list of all diatonic sevenths
    v7a = dominant7('C')            # v7a is chords1[4]
    v7b = sevenths('C')[4]          # v7b is the same object as v7a
    assert v7a is v7b
    v7a[0] = 'G_mod'                # mutates the cached chord list
    # Subsequent calls will see the mutation since the cached object was modified

## `mingus.core.chords.submediant` · *function*

## Summary:
Returns the submediant triad (the triad built on the 6th degree of the key's scale) for the specified key.

## Description:
Known callers:
- No direct callers were discovered in the provided context. Typical callers include chord/progression builders, harmonic analysis utilities, or any code that needs the vi (submediant) chord of a key (for example, functions that assemble common progressions like I–vi–ii–V).
- This function is a small convenience accessor that encapsulates the indexing logic for "the 6th scale degree triad" and delegates triad construction, validation, and caching to triads(key). Keeping this logic in its own function avoids repeating the index-of-degree constant (5) and centralizes the semantic meaning "submediant" in one place.

## Args:
    key (str):
        - The key or tonic name accepted by mingus.core.keys.get_notes and triads.
        - Examples: "C", "G", "F#", "Bb" depending on the project's key format rules.
        - Required parameter; no default value.
        - Interdependencies: the result depends on triads(key), which in turn depends on keys.get_notes(key) and triad(root_note, key).

## Returns:
    list[str]:
        - The triad corresponding to the submediant scale degree for the given key.
        - Represented as a list of three pitch-name strings (typically [root, third, fifth], e.g., ['A', 'C', 'E'] for C major).
        - This value is the element at index 5 of the list returned by triads(key).
        - If triads(key) returns a cached list object, the returned triad is that list's element (no defensive copy is made here).

## Raises:
    IndexError:
        - If triads(key) returns a sequence with length <= 5 (for example, if keys.get_notes returns a shorter-than-expected scale), attempting to access index 5 will raise IndexError.

    NoteFormatError:
        - Propagated from triads(key) (or keys.get_notes) when the provided key is in an invalid format.

    Any exception raised by triads(key):
        - Any other exception (KeyError, FormatError, or others) that triads or its helpers raise will propagate unchanged.

## Constraints:
Preconditions:
    - key must be valid for keys.get_notes and triads to produce a conventional scale (typically a 7-note diatonic scale).
    - The module-level state triads depends on (e.g., any caches used by triads) must be intact; this function does not initialize cache state itself.

Postconditions:
    - On successful return, the caller receives the triad at scale degree 6 as produced by triads(key).
    - No additional mutation is performed by this function itself; any caching or mutation is done by triads(key).

## Side Effects:
    - This function itself performs no I/O.
    - It may trigger side effects performed by triads(key), such as populating the triads cache (module-level) if triads computes and caches results for the key.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads([call triads(key)])
    CallTriads --> TriadsError{triads raised?}
    TriadsError -->|Yes| Propagate([propagate exception to caller])
    TriadsError -->|No| HasSixth{len(result) > 5?}
    HasSixth -->|No| IndexError([raise IndexError])
    HasSixth -->|Yes| Extract([return result[5]])
    Extract --> End([End])

## Examples:
Example — typical successful usage:
    try:
        sub = submediant("C")
        # Expected typical result for C major: ['A', 'C', 'E']
        print("Submediant of C:", sub)
    except Exception as e:
        print("Could not get submediant:", e)

Example — handling invalid key:
    try:
        submediant("InvalidKey")
    except NoteFormatError as e:
        # keys.get_notes or triads will raise NoteFormatError for bad key formats
        print("Bad key format:", e)

Example — handling unexpectedly short scale:
    try:
        submediant("SomeNonstandardScale")
    except IndexError:
        # triads returned too few scale-degree triads to contain a 6th degree
        print("Scale does not contain a 6th degree triad.")

## `mingus.core.chords.submediant7` · *function*

## Summary:
Returns the diatonic seventh chord built on the submediant (6th) scale degree of the supplied key as a list of pitch-name strings.

## Description:
- Known callers within the codebase:
    - No internal direct callers were found in the provided snapshots. This is a small public helper in the chords API intended for use by higher-level chord/analysis functions or by user code that wants the submediant seventh chord for a given key.
- Why this logic is extracted:
    - Responsibility boundary: this function provides a focused, readable accessor for the 6th-degree seventh chord without requiring callers to request all seventh chords and index them themselves. It keeps client code concise and documents the musical intent (submediant seventh) at the call site.
    - Delegation: it delegates all scale computation, chord assembly, caching, and validation to the shared helper sevenths(key), so it remains trivial and predictable.

## Args:
    key (str):
        - The musical key context (e.g., "C", "G", "F#", "Bb") used to compute diatonic chords.
        - Must be a key format accepted by mingus.core.keys.get_notes (see keys module).
        - No default — this parameter is required.
        - Interdependencies: correctness depends on the behavior of sevenths(key) / keys.get_notes; invalid or malformed key strings will cause underlying helpers to raise a NoteFormatError or similar.

## Returns:
    list[str]:
        - A list of pitch-name strings representing the submediant seventh chord in the given key.
        - Conventionally this is a four-element list [root, third, fifth, seventh] for the 6th scale degree. Example for key "C": ['A', 'C', 'E', 'G'] (A minor seventh).
        - The returned list is a direct reference into the data returned/cached by sevenths(key). Mutating the returned list or its elements modifies the shared cached data for that key.

## Raises:
    - IndexError:
        - If sevenths(key) returns a sequence with fewer than 6 elements (i.e., no 6th degree available), the indexing [5] raises IndexError. This can occur for non-standard or truncated scale definitions.
    - mingus.core.mt_exceptions.NoteFormatError (propagated):
        - If the provided key is invalid and keys.get_notes(key) (used by sevenths) raises NoteFormatError, the exception propagates unchanged.
    - Any exception raised by underlying helpers:
        - Any other exception raised by sevenths(key) or its callees (e.g., invalid note formatting raised when building the chords) will propagate unchanged.

## Constraints:
- Preconditions:
    - key must be a str in a format accepted by the keys/sevenths helpers.
    - The chords module-level cache used by sevenths (if any) is expected to exist; this function assumes sevenths handles caching and validity.
- Postconditions:
    - On success, a list of pitch-name strings representing the submediant seventh chord is returned.
    - No new module-level state is directly modified by submediant7 itself (it may observe side effects performed by sevenths such as cache population).

## Side Effects:
- No I/O or external service calls.
- Indirect side effect: it returns a direct reference into a cached data structure produced by sevenths(key). If a caller mutates the returned list or its nested lists, that mutation affects the cached value and will be visible to other callers of sevenths(key) and this function for the same key.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|sevenths raises NoteFormatError or other| PropagateEx[Propagate exception to caller]
    CallSevenths -->|sevenths returns sequence| IndexAccess[Attempt to access element index 5]
    IndexAccess -->|index in range| ReturnChord[Return seventh chord list (element 5)]
    IndexAccess -->|index out of range| RaiseIndex[Raise IndexError to caller]
    ReturnChord --> End([End])
    PropagateEx --> End
    RaiseIndex --> End

## Examples:
- Typical successful usage:
    try:
        chord = submediant7('C')  # returns ['A', 'C', 'E', 'G'] (A minor seventh)
        print("Submediant seventh in C:", chord)
    except Exception as e:
        print("Failed to get submediant seventh:", e)

- Handling invalid key format:
    try:
        chord = submediant7('InvalidKey')
    except NoteFormatError:
        print("Provided key was invalid")

- Guarding against missing 6th degree (defensive):
    try:
        chord = submediant7('SomeNonstandardKey')
    except IndexError:
        # sevenths() did not return at least 6 items for this key
        print("Submediant (6th degree) not available for this key")
    except Exception as e:
        print("Other error:", e)

- Mutation caveat (shared cache):
    chords = submediant7('C')
    chords[0] = 'A_mod'  # mutates the cached chord for 'C'; future calls see this change

## `mingus.core.chords.subtonic` · *function*

## Summary:
Returns the triad built on the seventh scale degree (the subtonic) for the given key, i.e., the triad at index 6 of the key's triads.

## Description:
This is a small convenience accessor that delegates to the module-level triads(key) function and returns its element at index 6. Known callers within the supplied context: none discovered in the provided files. Typical callers (not present in the supplied context) include chord lookup utilities, chord-symbol resolvers, progression builders, and analysis routines that need the subtonic chord for a given key.

This logic is extracted into its own function to provide a clear, self-documenting API for retrieving the subtonic (seventh-degree) triad without callers having to know the triads list indexing or to reimplement the index access. It keeps the responsibility narrow: fetch the triads for a key and return the 7th one.

## Args:
    key (str):
        - The key/tonic identifier accepted by mingus.core.keys.get_notes and by triads.
        - Examples: "C", "G", "F#", "Bb" depending on the project's key format rules.
        - No default; required.
        - Interdependencies: The validity and exact note spellings depend on keys.get_notes(key) and triad construction used by triads(key).

## Returns:
    list[str]:
        - A 3-element list of pitch-name strings representing the subtonic triad: [root, third, fifth].
        - Typical (diatonic) case: the triad built on the seventh scale degree of the key (for "C" -> ['B', 'D', 'F'] in a conventional diatonic implementation).
        - The function returns whatever triads(key)[6] yields; there is no defensive copying.

## Raises:
    IndexError:
        - If triads(key) returns a list with fewer than 7 elements (so index 6 is out of range), IndexError will be raised by the indexing operation.

    NoteFormatError:
        - Propagated from triads(key) / keys.get_notes(key) when the provided key string is not recognized or malformatted.

    Any exception raised by triads(key) or its helpers:
        - Exceptions from triad building or lower-level helpers (e.g., KeyError, FormatError, other runtime errors) are propagated unchanged.

## Constraints:
Preconditions:
    - The module-level triads function and the key-parsing utilities must be available and accept the provided key value.
    - The typical expectation is that triads(key) returns an ordered list of triads corresponding to each scale degree; in conventional diatonic systems this list has length >= 7.

Postconditions:
    - On successful return, the returned value is the exact list object at triads(key)[6] and represents the subtonic triad for the requested key.
    - No additional invariants are modified by this wrapper itself; any caching or side effects are performed by triads(key).

## Side Effects:
    - Indirect: triads(key) may populate or mutate a module-level cache (e.g., _triads_cache). Calling this function may therefore cause the cache to be written on first computation.
    - No I/O, network access, or global state mutation is performed directly by this function beyond what triads(key) does.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTriads[Call triads(key)]
    CallTriads --> TriadsError{triads raised an exception?}
    TriadsError -->|Yes| PropagateErr[Propagate exception (NoteFormatError or other)]
    TriadsError -->|No| HasIndex{len(triads) > 6?}
    HasIndex -->|Yes| ReturnTriad[Return triads[key][6]]
    HasIndex -->|No| RaiseIndex[Raise IndexError (index out of range)]

## Examples:
Example — successful retrieval:
    try:
        sub = subtonic("C")
        # Typical expected (diatonic) result: ['B', 'D', 'F']
        print("Subtonic triad for C:", sub)
    except Exception as exc:
        print("Failed to get subtonic:", exc)

Example — invalid key format:
    try:
        subtonic("InvalidKey")
    except NoteFormatError as e:
        # keys.get_notes (via triads) will raise NoteFormatError for unrecognized key strings
        print("Bad key:", e)

Example — index error (non-standard scale with fewer degrees):
    try:
        subtonic("NonStandardKeyWithFewScaleNotes")
    except IndexError:
        # triads(key) returned fewer than 7 triads; the 7th triad does not exist
        print("Subtonic not available for this key (insufficient scale degrees).")

## `mingus.core.chords.subtonic7` · *function*

## Summary:
Returns the diatonic seventh chord built on the subtonic (the 7th scale degree) for the supplied key.

## Description:
Known callers:
- No internal direct callers were found in the available snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for use by higher-level chord/analysis code or by user code that needs the seventh chord on the subtonic.

Why this logic is extracted:
- Provides a concise, self-documenting convenience helper that encapsulates the common operation "get all diatonic sevenths for a key and select the 7th (subtonic)". Extracting this avoids duplicating the indexing pattern ([6]) throughout the codebase and centralizes the semantic meaning (subtonic seventh) of that access.

## Args:
    key (str)
        - The key context used to compute diatonic seventh chords (examples: "C", "G", "F#", "Bb").
        - Must be in a format accepted by mingus.core.keys.get_notes (see keys.get_notes for allowed forms).
        - No default; this parameter is required.
        - Interdependencies: validity depends on the keys module and on the underlying chord-building helpers used by sevenths().

## Returns:
    list[str]
        - A list of pitch-name strings representing the seventh chord built on the subtonic (7th scale degree).
        - Typical shape: a list of four pitch names [root, third, fifth, seventh], e.g. for key "C" the expected return is ['B', 'D', 'F', 'A'].
        - The returned object is the exact nested chord list produced (and possibly cached) by sevenths(key). No defensive copy is performed by this function.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        - Propagated when the provided key is malformed or not recognized by keys.get_notes (raised by the underlying keys/seventh helpers).

    mingus.core.mt_exceptions.FormatError
        - May be propagated if an underlying helper validates or formats notes/keys and raises this exception.

    IndexError
        - Raised if sevenths(key) returns a list with fewer than 7 elements (i.e., there is no 7th scale degree to index). This is a direct consequence of the indexing operation [6].

    Any exception raised by the underlying chord-building helpers (e.g., errors from seventh/triad/intervals)
        - These exceptions are propagated unchanged; this function performs no additional error handling.

## Constraints:
Preconditions:
    - key must be a string accepted by the keys subsystem (keys.get_notes).
    - The module-level environment must provide the sevenths() helper (i.e., this symbol must be resolvable at call time).

Postconditions:
    - On successful return, the returned list is the same object held within the nested list returned (and possibly cached) by sevenths(key). No mutation is performed by this function itself.

## Side Effects:
    - This function itself performs no I/O and does not mutate global state.
    - Indirectly, because it returns a reference into the sevenths() result (which may be cached at module level), mutating the returned list or its nested elements will mutate the cached data and affect subsequent callers that observe the same cached object.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSevenths[Call sevenths(key)]
    CallSevenths -->|raises exception| Propagate1[Propagate exception to caller]
    CallSevenths --> AccessIndex[Access result[6]]
    AccessIndex -->|IndexError| Propagate2[Propagate IndexError to caller]
    AccessIndex --> ReturnChord[Return the 7th-seventh-chord list]
    ReturnChord --> End([End])

## Examples:
Example — normal usage (conceptual):
    Input: subtonic7("C")
    Output: ['B', 'D', 'F', 'A']

Example — invalid key:
    Behavior: subtonic7("InvalidKey")
    Outcome: keys.get_notes (via sevenths) raises NoteFormatError which is propagated to the caller.

Example — short/irregular scale:
    Behavior: if sevenths(key) returns fewer than 7 chords, subtonic7(key) raises IndexError (no 7th element available).

Notes on mutation/caching:
    - Because the returned list is taken directly from the data produced by sevenths(key) (which caches and reuses its result), callers should treat the returned list as shared/aliasable and avoid in-place mutation unless that effect is intentional.

## `mingus.core.chords.I` · *function*

## Summary:
Returns the tonic (I) triad for the given musical key by delegating to the tonic accessor.

## Description:
This is a tiny convenience wrapper that returns the same result as the tonic(key) function. It exists to provide a musically idiomatic name (I) for the tonic triad, making code that constructs or reads chord progressions more expressive.

Known callers within the codebase:
- No callers were found directly in the provided context. Typical callers include:
  - Progression builders or harmony utilities that need the I chord.
  - User-facing code or examples that want a concise way to request the tonic triad.
  - Tests and demonstrations asserting the tonic chord for a key.

Why this is a separate function:
- Provides a concise, semantically clear alias for tonic(key) so callers can write I(key) when they want the first-degree triad.
- Encapsulates the intent "give me the I chord" and centralizes any future changes to how the tonic triad is resolved.

## Args:
    key (str):
        - The musical key identifier (examples: "C", "G", "F#", "Bb").
        - Required. No default.
        - Must be in the same format accepted by the library's keys.get_notes / triads implementations.
        - The function does not validate the string itself — validation is performed by the called tonic/triads pipeline.

## Returns:
    list[str]:
        - A triad represented as a list of three pitch-name strings [root, third, fifth], as produced by tonic(key).
        - On success, typically for "C" returns ['C', 'E', 'G'].
        - If tonic(key) returns a different sequence/container type, this function returns whatever tonic(key) returns unchanged.

## Raises:
    IndexError:
        - Propagated if tonic(key) (and therefore triads(key)) returns an empty sequence and the underlying code attempts to access the first element.
    NoteFormatError:
        - Propagated if the provided key string is malformed or not recognized by the underlying keys/triads code.
    Any exception raised by tonic(key):
        - This function does not catch exceptions; any exception raised by tonic(key) is propagated unchanged.

## Constraints:
Preconditions:
    - The caller must supply a key string accepted by the library's key/notes utilities.
    - The tonic (and triads) implementation must be available in the module namespace.

Postconditions:
    - On success, returns the tonic triad for the given key and does not modify module-level state.
    - On failure, raises the same exception thrown by tonic(key) (no translation or wrapping).

## Side Effects:
    - The function itself has no I/O and does not mutate global state.
    - Any side effects (caching, logging, etc.) are those of tonic(key) or functions it calls, not of this wrapper.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTonic[Call tonic(key)]
    CallTonic --> TonicError{tonic raised an exception?}
    TonicError -->|Yes| PropagateErr([Propagate that exception])
    TonicError -->|No| ReturnVal([Return tonic(key) result])

## Examples:
- Typical successful retrieval:
  - I("C") -> ['C', 'E', 'G']  (the I triad in C major)

- Handling an invalid key:
  - Callers that accept user input should handle NoteFormatError:
    - Attempt to call I(user_key); if NoteFormatError is raised, inform the user and request a corrected key.

- Handling unexpected empty results:
  - If the underlying triad construction returns an empty container, an IndexError may be raised by the underlying implementation; callers that cannot assume valid triads should catch IndexError.

## `mingus.core.chords.I7` · *function*

## Summary:
Returns the tonic (I) seventh chord for a given musical key by delegating to the tonic7 helper; yields a four-note chord [root, third, fifth, seventh].

## Description:
Known callers:
    - No internal direct callers were found in inspected repository snapshots. This function is provided as part of the public mingus.core.chords API for library users and higher-level chord/analysis utilities that prefer Roman-numeral naming (I7) over the tonic7 identifier.

Why this is a separate function:
    - Acts as a small, readable alias that maps a common Roman-numeral chord name (I7) to the existing tonic7 implementation. This keeps naming consistent for callers who expect Roman-numeral chord helpers and avoids duplicating the chord-construction logic implemented in tonic7/sevenths.

Responsibility boundary:
    - I7 has a single responsibility: forward the provided key to tonic7 and return its result unchanged. All input validation, computation, caching, and error semantics are the responsibility of tonic7 and the helpers it calls (e.g., keys, intervals).

## Args:
    key (str):
        - A key name or identifier like "C", "G", "F#", "Bb".
        - Must be in a format accepted by the keys module (validation is delegated to tonic7 / keys.get_notes).
        - No default; this parameter is required.

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the tonic seventh chord in the supplied key, ordered as [root, third, fifth, seventh].
        - Example: for key "C" the typical return is ['C', 'E', 'G', 'B'].
        - The return value is the exact object returned by tonic7(key). If tonic7 returns a reference into a module-level cache, callers will receive that same reference.

## Raises:
    - mingus.core.mt_exceptions.NoteFormatError:
        - Propagated from tonic7 (via keys.get_notes) when the supplied key string is not a recognized key format.
    - IndexError:
        - Can occur if the underlying tonic7/sevenths helpers return an empty sequence and the wrapper attempts to access the tonic element (this is an edge case originating from tonic7).
    - Any other exception raised by tonic7 or the helpers it calls is propagated unchanged.

## Constraints:
Preconditions:
    - The caller must supply a non-empty string representing a musical key in a form understood by the keys module.
    - The tonic7 helper and its dependencies must be importable and functioning.

Postconditions:
    - On success, a list[str] with four pitch names is returned.
    - No mutation is performed by I7 itself; callers should assume they may receive a shared reference (mutating the list may affect other users if the underlying helper returns a cached object).

## Side Effects:
    - I7 itself performs no I/O and does not mutate global state.
    - Any side effects originate from tonic7/sevenths (for example, populating or updating a module-level cache). Mutating the returned list may alter shared cached data if the underlying helpers use caching.

## Control Flow:
flowchart TD
    Start([Start]) --> CallTonic7[Call tonic7(key)]
    CallTonic7 -->|raises exception| Propagate[Propagate exception to caller]
    CallTonic7 -->|returns list| ReturnValue[Return tonic7(key) result]
    ReturnValue --> End([End])

## Examples:
Typical successful usage:
    try:
        chord = I7('C')  # Expected: ['C', 'E', 'G', 'B']
    except Exception as e:
        # Could be NoteFormatError (invalid key) or other underlying errors
        print("Failed to get I7 chord:", e)

Defensive usage handling invalid key:
    try:
        chord = I7('InvalidKeyName')
    except NoteFormatError:
        print("The supplied key string is invalid.")
    except IndexError:
        # Defensive: underlying helper returned no chords
        chord = None

## `mingus.core.chords.ii` · *function*

## Summary:
A thin, descriptive wrapper that returns the triad built on the supertonic (scale degree II) of the specified key.

## Description:
Known callers within the codebase:
    - No direct callers were discovered in the supplied context. Typical callers include chord/progression builders, harmonic-analysis utilities, and user-facing helpers that request the diatonic II chord by Roman numeral.

Why this function exists:
    - It provides a clear, semantic alias for obtaining the scale-degree II triad. Extracting this one-line wrapper preserves intention at call sites (the caller asks for "ii" rather than "supertonic"), keeps client code readable, and centralizes delegation to the canonical implementation (supertonic). It enforces a single-responsibility boundary: ii maps Roman-numeral semantics to the supertonic construction without re-implementing triad logic.

## Args:
    key (str): The musical key/tonic name used to build the scale from which the supertonic triad is derived.
        - Accepted formats are those supported by the underlying key/notes helpers (examples: "C", "G", "F#", "Bb").
        - Required; no default.
        - The semantic correctness of the result depends on keys.get_notes and triad construction used by the underlying implementation.

## Returns:
    list[str]: The supertonic triad as a list of three pitch-name strings in order [root, third, fifth].
        - The returned list is produced by the supertonic implementation and typically references an inner list returned from the triads helper (i.e., may be a reference into a cached structure).
        - Example (typical diatonic output): for key "C" the returned value is ['D', 'F', 'A'].

## Raises:
    IndexError:
        - If the underlying triads or scale-producing helper returns fewer than two triads, indexing the supertonic element may raise IndexError.

    NoteFormatError:
        - If the provided key string is invalid according to the key/notes helpers, the underlying call will raise NoteFormatError which propagates unchanged.

    Any exception raised by the delegated implementation (supertonic / triads / keys.get_notes):
        - Other errors (FormatError, KeyError, or unexpected exceptions thrown by the underlying helpers) propagate through ii unchanged.

## Constraints:
Preconditions:
    - The provided key must be in a format accepted by the project's key/notes helpers.
    - The underlying triad-producing helper must return an ordered list of triads where the second element corresponds to the supertonic triad.

Postconditions:
    - On successful completion, the function yields the supertonic triad as a list of three pitch-name strings.
    - The function itself performs no mutations, but because the return value is commonly a reference into cached data, the caller must not assume the returned list is a fresh copy.

## Side Effects:
    - No I/O, networking, or persistent state changes are performed by ii itself.
    - Indirect side effect risk: the returned list is often a reference into a shared/cached structure. Mutating the returned list will mutate that shared cache and affect subsequent callers. Callers that must mutate should copy the list first.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSupertonic[Call supertonic(key)]
    CallSupertonic --> SuperError{supertonic raised an exception?}
    SuperError -->|Yes| Propagate([Propagate underlying exception])
    SuperError -->|No| ReturnValue([Return triad list from supertonic])

## Examples:
Example — basic usage and expected result:
    Calling ii with a conventional diatonic key returns the II triad. For example, ii("C") typically yields ['D', 'F', 'A'].

Example — defensive handling of an invalid key:
    If a caller provides an invalid key string, the operation will raise NoteFormatError (propagated from the key/notes helpers). Callers should catch NoteFormatError to handle user input validation failures.

Example — avoiding shared-cache mutation:
    Because the returned list may reference shared cached data, copy it before mutating:
    - Obtain the triad via ii("C"), make a shallow copy (for example via list(triad) or triad.copy()), and mutate the copy to avoid affecting global cache consumers.

## `mingus.core.chords.II` · *function*

## Summary:
A convenience alias that returns the triad built on the second (supertonic) degree of the given key's scale.

## Description:
Known callers within the codebase:
    - No direct callers are provided in the supplied context. Typical callers include chord/progression builders, harmonic analysis utilities, and user-facing helpers that request named scale-degree chords using Roman numeral notation.

Context and rationale:
    - This function exists as a short, semantically clear alias for the supertonic function so callers can request the "II" chord using Roman-numeral naming without importing or calling supertonic directly. It enforces a single responsibility: map the Roman-numeral label II to the corresponding chord-construction helper.

## Args:
    key (str):
        - The musical key or tonic name accepted by the underlying key/scale helpers (e.g., keys.get_notes).
        - Examples: "C", "G", "F#", "Bb".
        - Required. No default.
        - Interdependency: The validity and interpretation of this string are delegated to supertonic(key) and the functions it calls (typically keys.get_notes and triads).

## Returns:
    list[str]:
        - A triad represented as a list of three pitch-name strings [root, third, fifth] for the supertonic (second) scale degree in the specified key.
        - This is the exact object returned by supertonic(key) — typically a reference into triads(key)'s result (possibly a cached inner list). Do not assume the list is a defensive copy.

## Raises:
    IndexError:
        - If the underlying triads(key) result contains fewer than two elements (so accessing the second element fails). This is unlikely for standard diatonic implementations but possible if the key/triads helper behaves atypically.

    NoteFormatError:
        - Propagated when the underlying key parsing logic (e.g., keys.get_notes invoked by triads) rejects the provided key format.

    Any exception raised by supertonic(key):
        - Any other exceptions (for example FormatError, KeyError, or unexpected runtime errors) raised by the underlying helpers are propagated unchanged.

## Constraints:
Preconditions:
    - The provided key must be a string in a format accepted by the project's key/scale utilities (keys.get_notes).
    - The triads generator used by supertonic must return an ordered list of triads where the second element corresponds to the supertonic chord.

Postconditions:
    - On success, a list of three pitch-name strings representing the supertonic triad is returned.
    - No mutations are performed by II itself; callers that mutate the returned list may affect shared cached data if the underlying implementation shares references.

## Side Effects:
    - No I/O, network, or persistent external state changes are performed by II.
    - Indirect effect: because the returned list is typically a direct reference into triads' cached data, mutating the returned list will mutate any shared cache that triads maintains. If callers must avoid modifying shared state, they should copy the returned list before making changes.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSupertonic[Call supertonic(key)]
    CallSupertonic --> SuperError{supertonic raised an exception?}
    SuperError -->|Yes| Propagate([Propagate same exception to caller])
    SuperError -->|No| ReturnTriad([Return the triad list returned by supertonic])
    ReturnTriad --> End([End])

## Examples:
Example — typical usage:
    try:
        ii = II("C")
        # Typical expected result for a conventional diatonic implementation: ['D', 'F', 'A']
        print("II chord of C:", ii)
    except NoteFormatError:
        print("Invalid key format provided")
    except IndexError:
        print("Triads did not contain a supertonic degree")

Example — avoid mutating shared cached data:
    triad = II("C")
    safe_copy = list(triad)  # or triad.copy()
    safe_copy[0] = "Db"      # modifies only the local copy, not the shared cache

## `mingus.core.chords.ii7` · *function*

## Summary:
Returns the diatonic seventh chord built on the second scale degree (the supertonic) for the given key by delegating to the shared supertonic7 helper.

## Description:
- Known callers:
    - No internal direct callers were found in the available code snapshots. This function exists as part of the public chord API for client code and higher-level analysis code that may request the supertonic seventh chord by name.
- Why this is a separate function:
    - Acts as a concise, intention-revealing alias. It hides implementation details of how the supertonic seventh is obtained (for example, retrieving a cached list of seventh chords and selecting the second element) and provides a small, well-named API surface for callers that only need this specific chord.

## Args:
    key (str):
        - The musical key used to determine scale degrees (examples: "C", "G", "F#", "Bb").
        - Required positional argument; there is no default.
        - The key string must be valid per the keys module (validation is performed by the underlying helpers such as keys.get_notes and sevenths()).
        - Interdependencies: the accepted formats and normalization rules for key are determined entirely by the underlying keys/sevenths implementations; this function does not alter or validate the key beyond passing it through.

## Returns:
    list[str]:
        - A 4-element list of pitch-name strings representing the supertonic seventh chord in order [root, third, fifth, seventh].
        - Example (typical for C major): ['D', 'F', 'A', 'C'].
        - Implementation detail to be aware of: the returned list is typically the same object stored in the module-level cache used by the underlying sevenths(key) function. Callers receive a reference to that cached list; in-place modifications will affect the cached value and be visible to subsequent callers.

## Raises:
    - Propagated exceptions from the underlying supertonic7/sevenths/key helpers:
        - mingus.core.mt_exceptions.NoteFormatError (or other exceptions raised by keys.get_notes) when the provided key string is invalid or cannot be parsed.
        - Any error raised while constructing the diatonic seventh chords in sevenths(key) will propagate unchanged.
    - IndexError:
        - If the underlying sevenths(key) returns a sequence with fewer than two elements, attempting to select the second element will raise IndexError; this will propagate.
    - TypeError:
        - If the underlying sevenths(key) returns a non-indexable or otherwise unexpected type, TypeError may occur during the attempt to index/return the chord; this indicates a deeper invariant violation and will propagate.

## Constraints:
- Preconditions:
    - The caller must provide a non-empty key string in a format accepted by the keys module.
    - The module-level helper sevenths() (or equivalent that supertonic7 uses) is expected to return an indexable sequence of seventh-chord lists for the key.
- Postconditions:
    - On successful return, the function yields a 4-element list of pitch-name strings representing the supertonic seventh chord for the supplied key.
    - No local mutation is performed by this function itself; however, the returned object may be a cached object shared across calls.

## Side Effects:
    - No I/O (file, network, stdout) is performed by this function.
    - Indirect mutation of module-level cache/state:
        - If the underlying sevenths(key) populates a cache on first request, that cache may become populated as a side effect of the call.
        - Because the returned chord list is usually a direct reference to cached data, any in-place modification performed by the caller will mutate the cache and be visible to future callers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSupertonic7[Call supertonic7(key)]
    CallSupertonic7 -->|raises exception| Propagate1[Propagate exception to caller]
    CallSupertonic7 -->|returns chord list| ReturnChord[Return that chord list]
    ReturnChord --> End([End])

## Examples:
- Typical successful use:
    - Input: key = "C"
    - Behavior: Delegates to supertonic7("C") which typically produces ['D', 'F', 'A', 'C'] for the supertonic seventh.
    - Output: ['D', 'F', 'A', 'C']

- Error scenario (invalid key):
    - If key = "H#" (or another invalid format per keys.get_notes), the underlying helper will raise a NoteFormatError (or similar); this exception will propagate to the caller.

- Mutation/caching caveat:
    - Because the returned list is often a cached reference, callers should avoid in-place mutation unless they intend to modify the cached chord for future callers. If an independent copy is required, callers should explicitly copy the returned list before mutating it.

## `mingus.core.chords.II7` · *function*

## Summary:
Returns the diatonic seventh chord built on the supertonic (second scale degree) of the supplied key by delegating to the canonical helper; effectively an alias for that helper.

## Description:
- Known callers:
    - No internal callers were found in the scanned code snapshots. This function is provided as a public API convenience so client code can request the II7 chord form using Roman-numeral-style naming.
- Why this logic is a separate function:
    - It exists as a small, intention-revealing alias. Rather than duplicating chord-construction logic, it delegates to the single implementation (supertonic7) and provides a clearer, musically-named entry point for callers who prefer Roman-numeral notation (II7). This keeps responsibilities narrow: II7 maps naming/semantics to the canonical implementation.

## Args:
    key (str):
        - The musical key used to determine scale degrees (examples: "C", "G", "F#", "Bb").
        - Required positional argument. Must be in a format accepted by the keys module (keys.get_notes).
        - No other parameters or configuration are accepted.

## Returns:
    list[str]:
        - A 4-element list of pitch-name strings representing the supertonic seventh chord in the form [root, third, fifth, seventh].
        - Example (for key="C"): ['D', 'F', 'A', 'C'].
        - The returned list is the same object returned (and usually cached) by the delegated helper; callers receive a direct reference to that list (mutating it in-place will affect the cached object).

## Raises:
    - Propagated exceptions from the delegated implementation (supertonic7), for example:
        - mingus.core.mt_exceptions.NoteFormatError: if the provided key string is invalid according to the keys module.
        - IndexError: if the delegated helper returns a sequence shorter than expected and an index operation inside that helper fails.
        - TypeError or other exceptions that the delegated helper may raise; II7 does not catch or convert exceptions — it forwards them unchanged.

## Constraints:
- Preconditions:
    - The provided key must be a valid key string accepted by the keys module (keys.get_notes).
    - The underlying sevenths/sextonic helper and any module-level caches it uses must be present and functioning as expected.
- Postconditions:
    - On success, returns a list of exactly four pitch-name strings representing the II7 chord for the given key.
    - No additional state is modified by II7 itself beyond what the delegated helper may do (e.g., populating a cache).

## Side Effects:
    - II7 itself performs no I/O and makes no direct external calls beyond calling the delegated helper.
    - Indirect side effect: if the delegated supertonic7 or its helpers populate a module-level cache on first computation, that cache may be filled. Because the returned list is often a direct reference to cached data, in-place mutation by callers will change the cached chord list and affect subsequent callers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSupertonic7[Call supertonic7(key)]
    CallSupertonic7 -->|raises exception| Propagate[Propagate exception to caller]
    CallSupertonic7 -->|returns list| Return[Return the list object to caller]
    Return --> End([End])

## Examples:
- Typical usage:
    - Input: key = "C"
    - Call: II7("C")
    - Result: ['D', 'F', 'A', 'C']

- Example with error handling:
    - If the key might be invalid, handle the propagated exception:
        try:
            chord = II7("InvalidKey")
        except mingus.core.mt_exceptions.NoteFormatError:
            # handle invalid key
            pass

- Mutation caveat:
    - Because the returned list is typically a cached object, avoid mutating it in-place if caller-side changes must be isolated. If you must modify the chord, work on a copy:
        chord = list(II7("C"))  # shallow copy before mutating

## `mingus.core.chords.iii` · *function*

## Summary:
Returns the mediant (iii) triad for the given key — a convenience alias that forwards to the mediant triad accessor.

## Description:
- Known callers within the codebase and context:
    - No direct callers were discovered in the supplied repository context. This function is typically used by external code that prefers Roman-numeral naming (e.g., building chord progressions, analysis tools, or user-facing APIs that expose scale degrees as roman numerals).
- Why this logic is a separate function:
    - It exists as a tiny, semantic alias: it enforces a clear, caller-friendly naming convention ("iii" for the mediant degree) instead of requiring callers to know or import the mediant function. The function delegates all construction and validation to mediant(key) so the alias remains a single-responsibility adapter.

## Args:
    key (str):
        - The musical key / tonic identifier accepted by the project's key/scale utilities (e.g., "C", "G", "F#", "Bb").
        - No default; required.
        - Accepted formats and accidentals follow the same rules as mediant(key) and its underlying keys.get_notes caller.

## Returns:
    list[str]:
        - A list of three pitch-name strings representing the mediant triad in the order [root, third, fifth].
        - Typical example: for a conventional diatonic triads implementation, iii("C") -> ['E', 'G', 'B'].
        - The value returned is the exact value returned by mediant(key) and therefore subject to the same identity/caching semantics (it may be a reference into a cached list).

## Raises:
    - Any exception raised by mediant(key) will propagate unchanged. In practice this commonly includes:
        - mingus.core.mt_exceptions.NoteFormatError: if the supplied key is not a valid/recognized key representation (propagated from keys.get_notes / triads).
        - IndexError: if the underlying triads list contains fewer than three elements (no mediant degree available); this function performs no additional bounds-checking.
        - Any other exception thrown by mediant/triads/keys/notes (e.g., other format or lookup errors) will propagate.

## Constraints:
- Preconditions:
    - The caller must pass a key string in a format accepted by the project's key/scale utilities (same preconditions as mediant).
    - The underlying triads(key) implementation must return an ordered iterable with at least three elements for a valid mediant to exist.
- Postconditions:
    - If no exception is raised, the function returns a list of three pitch-name strings representing the mediant triad.
    - No additional guarantees are added beyond what mediant(key) provides.

## Side Effects:
    - No direct I/O or external service calls.
    - Indirect side effects: calling iii(key) calls mediant(key), which may in turn call triads(key) and populate or update any module-level cache in that implementation. The returned list may be a direct reference into such a cache; mutating it will mutate the cached structure.

## Control Flow:
flowchart TD
    Start([Start]) --> CallMediant([call mediant(key)])
    CallMediant --> MediantError{mediant(key) raised?}
    MediantError -->|Yes| Propagate([propagate exception])
    MediantError -->|No| Return([return mediant(key)])

## Examples:
Example — typical successful usage:
    try:
        triad = iii("C")
        # Expect a conventional diatonic mediant triad, e.g. ['E', 'G', 'B']
        print("iii triad for C:", triad)
    except Exception as exc:
        print("Could not obtain iii triad:", exc)

Example — handling invalid key:
    try:
        iii("NotAKey")
    except NoteFormatError as e:
        # keys.get_notes (via mediant/triads) reported an invalid key format
        print("Bad key provided:", e)

Example — guarding against missing mediant (defensive):
    try:
        iii("SomeNonstandardScale")
    except IndexError:
        # triads returned too few elements; no mediant degree present
        print("Mediant degree not available for this key/scale")

## `mingus.core.chords.III` · *function*

## Summary:
Return the triad built on the mediant (III, the third scale degree) of the specified key by delegating to the mediant accessor.

## Description:
- Known callers within the provided codebase/context:
    - No direct callers were discovered in the supplied repository context. This function is a public convenience alias intended for use by higher-level chord/progression builders, analysis utilities, or user code that prefers roman-numeral named accessors (e.g., I, II, III, etc.).
- Why this logic is a separate function:
    - This function exists as a small, self-documenting wrapper that maps the roman-numeral name "III" to the mediant accessor. It keeps caller code readable (calling III("C") is clearer in some musical contexts than calling mediant("C")) and centralizes a stable API surface, while delegating actual triad construction and validation to the underlying mediant/triads implementation.

## Args:
    key (str):
        - The musical key or tonic identifier accepted by the project's key/scale utilities.
        - Examples: "C", "G", "F#", "Bb".
        - Required; no default. The exact accepted formats (accidentals, case rules) are governed by keys.get_notes/triads as used by mediant.

## Returns:
    list[str]:
        - A list of three pitch-name strings representing the mediant triad in the order [root, third, fifth].
        - The return value is the same object returned by mediant(key); if the underlying triads implementation returns or caches lists, this function returns that same list reference.
        - Example conventional result: III("C") -> ['E', 'G', 'B'].

## Raises:
    NoteFormatError
        - Propagated when the provided key is not a valid key representation (originates from keys.get_notes via triads/mediant).
    IndexError
        - Propagated if the underlying triads(key) result contains fewer than three triads (no mediant available) or triads' internal structure does not include the third-degree triad.
    Any exception raised by mediant(key) or its callees
        - Other errors (e.g., KeyError, custom exceptions) raised during scale/triad construction are propagated unchanged.

## Constraints:
Preconditions:
    - The caller must pass a key in a format accepted by the project's keys/triads utilities.
    - The underlying triads(key) implementation must be able to produce at least three triads for the requested key/scale for a successful result.

Postconditions:
    - If no exception is raised, the function returns a list of exactly three pitch-name strings representing the mediant triad.
    - No direct module-level state is modified by this function, though mediant/triads may populate or update their caches as a side effect.

## Side Effects:
    - No direct I/O (no file, network, or stdout operations).
    - Indirect side effects come from calling mediant(key) / triads(key): those functions may populate or update module-level caches. Because the returned list can be a reference to cached data, mutating the returned list may mutate shared cached state.

## Control Flow:
flowchart TD
    Start([Start]) --> CallMediant([call mediant(key)])
    CallMediant --> MediantError{mediant(key) raised?}
    MediantError -->|Yes| PropagateError([propagate exception])
    MediantError -->|No| ReturnResult([return mediant(key) result])
    ReturnResult --> End([End])

## Examples:
Example — successful usage:
    try:
        triad = III("C")
        # Expected conventional output: ['E', 'G', 'B']
        print("Mediant triad for C:", triad)
    except Exception as exc:
        print("Error obtaining mediant triad:", exc)

Example — handling an invalid key:
    try:
        III("InvalidKey")
    except NoteFormatError as e:
        print("Invalid key format:", e)

Example — defensive handling for missing mediant:
    try:
        triad = III("UnusualScale")
    except IndexError:
        print("Mediant degree not available for this key/scale")
    except Exception:
        raise

## `mingus.core.chords.iii7` · *function*

## Summary:
Returns the diatonic seventh chord built on the mediant (third) degree of the supplied key by delegating to the mediant7 helper.

## Description:
Known callers:
    - No direct internal callers were found in the provided repository snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for library consumers or higher-level code that requests the "iii7" (mediant seventh) chord by conventional Roman-numeral name.

Typical trigger / pipeline stage:
    - Called when code or a user needs the 7th chord built on the third scale degree of a key (for example, when generating chord progressions, performing harmonic analysis, or formatting chord labels).

Why this logic is extracted into its own function:
    - Convenience and readability: it acts as a semantic alias (iii7) for mediant7 so callers can use standard Roman-numeral naming without worrying about the underlying helper name.
    - Responsibility boundary: it enforces a clear, single-purpose API surface (request the iii7 chord) while reusing the logic, caching, and validation implemented by mediant7/sevenths. Implementation details and error handling remain centralized in mediant7.

See also:
    - mingus.core.chords.mediant7 for the implementation, exact construction rules, caching behavior, and complete list of propagated exceptions.

## Args:
    key (str):
        - The musical key context (examples: "C", "G", "F#", "Bb").
        - Required positional argument; no default.
        - Must be a string format accepted by the keys module (see mediant7 / keys.get_notes). Invalid or unrecognized key strings will cause the delegated call to raise a NoteFormatError.

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the mediant seventh chord in the supplied key: [root, third, fifth, seventh].
        - The returned object is the exact value returned by mediant7(key). Typically, for a diatonic major key "C", the result is ['E', 'G', 'B', 'D'].
        - Edge-case returns:
            - If the underlying chord builder returns a cached reference, the caller receives that same reference (mutating it will affect the cached state).

## Raises:
    - Any exception raised by mediant7(key), propagated unchanged. In practice this includes:
        - mingus.core.mt_exceptions.NoteFormatError: if the provided key string is invalid or not understood by the keys module.
        - IndexError: if the underlying chord-generation routine returns a list lacking a mediant entry (index out of range).
        - Any other exception raised inside mediant7 or lower-level helpers (interval computations, invalid note names) will propagate to the caller.

## Constraints:
Preconditions:
    - key must be a valid string acceptable to the keys.get_notes helper used by mediant7.
    - The chords module must expose mediant7 in the same namespace (this function delegates directly to mediant7).

Postconditions:
    - On success, returns the mediant seventh chord list produced by mediant7(key). No additional mutation is performed by this wrapper.
    - On failure, an exception raised by mediant7 is propagated; iii7 does not convert or wrap exceptions.

## Side Effects:
    - This function does not perform I/O (no file, network, or stdout activity).
    - It does not directly mutate global state. However, because it returns the direct result of mediant7(key), which may be a reference into an internal cache, subsequent mutation of the returned list by the caller may alter cached module state.
    - No external services are invoked by this wrapper beyond what mediant7 uses.

## Control Flow:
flowchart TD
    Start([Start]) --> CallMediant7[Call mediant7(key)]
    CallMediant7 -->|raises exception| PropagateErr[Propagate exception to caller]
    CallMediant7 -->|returns list| ReturnValue[Return mediant7(key) result]
    ReturnValue --> End([End])

## Examples:
Typical successful usage:
    try:
        chord = iii7('C')
        # chord is typically: ['E', 'G', 'B', 'D']
    except Exception as e:
        # Handle unexpected error
        print("Failed to get iii7:", e)

Handling invalid key names:
    try:
        iii7('InvalidKeyName')  # underlying mediant7 / keys.get_notes will raise NoteFormatError
    except NoteFormatError as e:
        print("Invalid key provided:", e)

Safe handling for missing mediant degree:
    try:
        chord = iii7(some_key)
    except IndexError:
        # The underlying chord list did not include a mediant degree
        print("Mediant chord not available for key:", some_key)
    except NoteFormatError as e:
        print("Bad key format:", e)

Mutation caveat (cache identity):
    chords = iii7('C')
    # chords may be a reference to cached data. Mutating it affects the module cache:
    chords[0] = 'E_mod'  # modifies cached chord data globally

## `mingus.core.chords.III7` · *function*

## Summary:
A thin public alias that returns the diatonic seventh chord built on the mediant (third) degree for the supplied key.

## Description:
Known callers:
    - No internal direct callers were found in the provided repository snapshots. This function exists as part of the public chord helper API for library consumers and higher-level code that prefers Roman-numeral accessors (III7) over named helpers (mediant7).
Typical trigger / pipeline stage:
    - Called when code or a user requests the mediant (III) seventh chord for a given key (for example, when generating chord progressions, performing harmonic analysis, or rendering chord names).
Why this logic is extracted into its own function:
    - Responsibility boundary: III7 acts as a stable, self-documenting alias that maps Roman-numeral notation to the underlying implementation (mediant7). Keeping this alias separate improves API discoverability and allows consistent naming styles (Roman numerals vs. function names) without duplicating chord construction logic.

## Args:
    key (str):
        - The musical key context (examples: "C", "G", "F#", "Bb").
        - Must be a string format accepted by mingus.core.keys.get_notes and the underlying chord-construction helpers.
        - Required positional parameter; no default.
        - Interdependencies: correctness of the key depends on the keys module. Validation errors from keys.get_notes or downstream helpers will propagate to the caller.

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the mediant seventh chord in the given key: [root, third, fifth, seventh].
        - Example: for a major "C" key the typical result is ['E', 'G', 'B', 'D'].
        - Implementation note: III7 simply returns the value produced by mediant7(key). That value is typically the element at index 2 of the list returned by sevenths(key). On a cache hit, the returned list may be a direct reference into an internal cached nested structure (i.e., callers may receive a reference to cached data).

## Raises:
    mingus.core.mt_exceptions.NoteFormatError:
        - Propagated when the supplied key string is invalid or cannot be parsed by the keys module or lower-level note helpers.
    IndexError:
        - Raised when the underlying chord-builder (mediant7 or sevenths) returns a list too short to contain the mediant seventh (e.g., the expected index does not exist).
    Any exception raised by mediant7 or its callees:
        - Other exceptions thrown by mediant7, sevenths, intervals, or notes (such as unexpected value or format errors) propagate unchanged.

## Constraints:
Preconditions:
    - Caller must supply a key string acceptable to the keys module.
    - The module containing mediant7 (and its dependencies) must be importable and functioning; III7 does not perform its own validation beyond delegating to mediant7.
Postconditions:
    - If successful, returns the mediant seventh chord as a list of four pitch-name strings.
    - III7 itself performs no mutation; however, because it may return a reference into a cache, external mutation of the returned list will affect cached state.

## Side Effects:
    - No I/O (files, network, stdout) is performed by this function.
    - No direct global state mutation is performed by III7 itself.
    - Indirect side effect risk: the returned list may be an alias to cached data maintained by the underlying helpers. Mutating the returned list will mutate the shared cache and affect subsequent callers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallMediant[Call mediant7(key)]
    CallMediant -->|mediant7 raises NoteFormatError or other| PropagateErr[Propagate exception to caller]
    CallMediant --> MediReturns{mediant7 returned a value}
    MediReturns -->|value is list with len >= 3| ReturnChord[Return mediant chord list]
    MediReturns -->|value missing or too short| RaiseIndex[IndexError raised]
    ReturnChord --> End([End])
    RaiseIndex --> End

## Examples:
Typical successful usage:
    try:
        chord = III7('C')
        # chord typically -> ['E', 'G', 'B', 'D']
    except Exception as e:
        # Handle unexpected error (e.g., invalid key or malformed scale)
        print("Error obtaining III7:", e)

Using Roman-numeral alias interchangeably with named helper:
    # Both calls should yield the same result:
    chord_alias = III7('G')
    chord_named = mediant7('G')

Handling invalid key names:
    try:
        III7('NotAKey')  # underlying validation will raise NoteFormatError
    except NoteFormatError as e:
        print("Invalid key provided:", e)

Defensive usage to avoid cache-mutation surprises:
    chord = III7('C')
    chord_copy = list(chord)  # work with a shallow copy if you will mutate it

## `mingus.core.chords.IV` · *function*

## Summary:
Return the triad built on the subdominant (IV) scale degree for the provided key by delegating to the subdominant implementation.

## Description:
Known callers:
    - No direct callers were found in the supplied context. Typical callers include chord progression builders, analysis utilities, or any code that needs the IV (subdominant) triad for harmonic processing.
    - IV is provided as a semantic/API convenience so callers can request chords by Roman numeral name rather than calling subdominant() or indexing triads() directly.

Why this is a separate function:
    - Acts as a concise alias mapping the Roman-numeral-style API (IV) to the subdominant implementation. This improves readability at call sites and centralizes the Roman-numeral-to-function mapping.

## Args:
    key (str):
        - The musical key or tonic name accepted by the underlying key/triad utilities (e.g., "C", "G", "F#", "Bb").
        - Required parameter; there is no default.
        - The exact allowed formats are those accepted by keys.get_notes and by triads(key). Invalid formats will cause the underlying utilities to raise NoteFormatError or other related exceptions.

## Returns:
    list[str]:
        - The subdominant triad as returned by subdominant(key). According to the subdominant implementation, this is typically the element at index 3 of the list produced by triads(key) (i.e., triads(key)[3]) and is a list of three pitch-name strings [root, third, fifth].
        - Example (typical diatonic major spelling): calling with "C" will return ['F', 'A', 'C'].
        - If the underlying triad provider returns fewer than four triads, accessing index 3 will raise an IndexError (see Raises).

## Raises:
    IndexError:
        - Raised when the list returned by triads(key) has fewer than four elements and triads(key)[3] is accessed by the underlying subdominant implementation.

    NoteFormatError:
        - Propagated from the underlying key/triad utilities when the provided key has an invalid or unrecognized format.

    Any other exception raised by subdominant(key) or the underlying triads/keys implementation:
        - Other exceptions (e.g., KeyError, FormatError, or custom exceptions from deeper helpers) are propagated unchanged.

## Constraints:
Preconditions:
    - The triads/key utilities required by subdominant must be available and correctly imported in the module namespace.
    - The provided key must conform to the format accepted by keys.get_notes/triads.

Postconditions:
    - On success, a list of three pitch-name strings (the IV triad) is returned.
    - No additional guarantees are made about note spelling beyond those provided by the underlying implementation.

## Side Effects:
    - The function itself performs no I/O and does not mutate module-level state directly.
    - Any side effects come from calls to subdominant(key) / triads(key) (for example, those functions may populate or update internal caches). Those side effects are implemented by the underlying functions, not by this wrapper.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubdominant[Call subdominant(key)]
    CallSubdominant --> SubdominantError{Did subdominant raise an exception?}
    SubdominantError -->|Yes| PropagateErr([Propagate underlying exception])
    SubdominantError -->|No| ReturnValue([Return the triad list[str]])

## Examples:
Successful usage:
    iv = IV("C")
    # Typical result: ['F', 'A', 'C']

Handling invalid key format:
    try:
        IV("NotAKey")
    except NoteFormatError as e:
        # Handle invalid key formats reported by the underlying utilities
        print("Invalid key:", e)

Handling missing triad (scale too short):
    try:
        IV("SomeKeyWithShortScale")
    except IndexError as e:
        # triads(key) did not provide a subdominant triad (triads(key)[3] out of range)
        print("No subdominant triad available:", e)

## `mingus.core.chords.IV7` · *function*

## Summary:
Returns the diatonic seventh chord built on the subdominant (the fourth scale degree) for the given key by delegating to the shared subdominant7 helper.

## Description:
Known callers within the codebase:
    - No direct internal callers were found in the provided snapshots. This function is part of the public chord helper API in mingus.core.chords and intended for use by higher-level chord/analysis code or by external user code that requests the IV7 (Roman-numeral) chord for a key.

Typical usage context:
    - Called when a consumer needs the IV7 chord of a given key (for analysis, rendering, harmonization, or MIDI generation).

Why this logic is extracted into its own function:
    - Responsibility boundary: IV7 exists as a small, named convenience wrapper to provide a clear, semantically meaningful API (Roman-numeral naming) rather than requiring callers to directly call subdominant7. It centralizes the intent "give me the IV7 chord" and avoids duplicating indexing or lookup logic across the codebase.

## Args:
    key (str):
        - The musical key used as context for building diatonic seventh chords (examples: "C", "G", "F#", "Bb").
        - Must be in a format accepted by the keys module (keys.get_notes). Invalid formats will cause downstream exceptions from the underlying helpers.
        - Required positional argument; no default value.

## Returns:
    list[str]:
        - A list of pitch-name strings representing the subdominant seventh chord for the given key, typically four elements: [root, third, fifth, seventh].
        - Example: calling with key "C" typically returns ['F', 'A', 'C', 'E'].
        - This function returns whatever object subdominant7(key) returns; in the typical implementation this is a reference to the element at index 3 of the list returned by sevenths(key). Because that list may be cached, the returned list may be the same shared (cached) object used elsewhere — mutating it will mutate the cached data.

## Raises:
    IndexError:
        - If the underlying sevenths(key) returns a list with fewer than four entries (no element at index 3), an IndexError will propagate/occur.
    mingus.core.mt_exceptions.NoteFormatError:
        - Propagated when the underlying keys.get_notes(key) or related helpers reject the provided key format.
    Any other exception raised by subdominant7 or its callees:
        - All other exceptions from the call chain are propagated unchanged.

## Constraints:
Preconditions:
    - Caller must supply a key string formatted as accepted by the keys module.
    - The module-level helper subdominant7 (and any helpers it depends on, e.g., sevenths) must be available in the module namespace.

Postconditions:
    - On success, the function returns a list of pitch-name strings representing the subdominant seventh chord for the input key.
    - The function itself does not modify global state; however, because it typically returns a reference into a cached structure, mutations to the returned list may affect shared cached state.

## Side Effects:
    - No I/O (files, network, stdout) is performed by this function.
    - No direct mutation of global state is performed by this function itself.
    - Indirect effect: returning a reference to cached data means callers that mutate the returned list will modify module-level cached state visible to other callers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubdominant7[Call subdominant7(key)]
    CallSubdominant7 -->|raises exception| Propagate[Propagate exception to caller]
    CallSubdominant7 --> ReturnValue[Return whatever subdominant7(key) returns]
    ReturnValue --> End([End])

## Examples:
Typical successful usage:
    try:
        iv7 = IV7('C')
        # iv7 is typically ['F', 'A', 'C', 'E']
    except Exception as e:
        # Handle invalid key or other underlying errors
        print("Failed to obtain IV7 chord:", e)

Example — cache/reference caveat:
    # If subdominant7('C') returns a cached chord object:
    iv7_a = IV7('C')
    iv7_b = subdominant7('C')  # likely the same object or equivalent
    assert iv7_a is iv7_b or iv7_a == iv7_b
    # Mutating iv7_a may change the cached representation visible to other callers:
    iv7_a[0] = 'F_mod'  # alters shared data if the object is cached

Example — handling invalid key and short scale:
    try:
        chord = IV7('InvalidKeyName')
    except NoteFormatError:
        print("Provided key name has invalid format.")
    except IndexError:
        print("Computed diatonic seventh list is too short to contain a subdominant (index 3).")

## `mingus.core.chords.V` · *function*

## Summary:
Delegates to the dominant-chord helper to obtain the dominant (V) chord for the given key.

## Description:
- Behavior: This function is a thin wrapper that immediately calls and returns the result of dominant(key). It does not implement chord logic itself.
- Known callers within the provided context: None found in the supplied code. It is intended as a convenience API for callers that prefer the Roman-numeral name "V" when requesting the dominant chord.
- Why this is a separate function: Provides a concise, self-documenting alias that improves API discoverability and reads naturally in higher-level code that refers to Roman-numeral chord degrees (e.g., "I", "IV", "V") instead of function names like dominant.

## Args:
    key (any):
        - The key/tonic identifier passed through to dominant(key).
        - Accepted formats and constraints for this argument are defined by dominant and any lower-level helpers it calls; this function performs no validation itself.

## Returns:
    Any:
        - Returns exactly whatever dominant(key) returns.
        - No additional post-processing or wrapping is performed.

## Raises:
    Any exception raised by dominant(key):
        - This function does not catch or translate exceptions. Any exception thrown by dominant will propagate unchanged to the caller.

## Constraints:
Preconditions:
    - The caller must provide a key value valid for dominant(key) (format and semantics depend on the dominant implementation).

Postconditions:
    - If dominant(key) returns successfully, V(key) returns the same value.
    - If dominant raises, the exception propagates and V does not return.

## Side Effects:
    - V itself has no side effects beyond those caused by calling dominant(key). Any I/O, caching, or global/state changes are the responsibility of the dominant implementation.

## Control Flow:
flowchart TD
    Start([Start]) --> CallDominant[Call dominant(key)]
    CallDominant --> DominantError{dominant raised exception?}
    DominantError -->|Yes| Propagate([Propagate exception to caller])
    DominantError -->|No| ReturnResult([Return result of dominant(key)])

## Examples:
Basic delegation:
    result = V("C")
    # Equivalent to calling: result = dominant("C")

Example with error handling (propagated from dominant):
    try:
        v_chord = V("invalid-key")
    except Exception as e:
        # Handle or report the same exception that dominant would raise
        handle_error(e)

## `mingus.core.chords.V7` · *function*

## Summary:
Returns the dominant seventh chord for the given key by delegating to the dominant7 helper; this is a short, named alias that yields the V7 chord (root, third, fifth, seventh) as four pitch-name strings.

## Description:
- Known callers within the codebase:
    - No direct internal callers in the provided snapshots. This function is a public-facing helper in the chords API intended for use by higher-level chord/analysis code or user code that needs the V7 chord.
- Typical usage context:
    - Used when a caller needs the dominant (V7) seventh chord in the context of a diatonic key (e.g., harmonic analysis, chord progression generation, rendering or labeling chords).
- Why this logic is extracted into its own function:
    - This function exists as a concise, readable alias for dominant7(key). It clarifies intent when callers request "V7" (Roman-numeral notation) rather than "dominant7". It centralizes the naming choice and keeps client code expressive without duplicating logic.

## Args:
    key (str):
        - The musical key context used to compute the dominant seventh (examples: "C", "G", "F#", "Bb").
        - Must be accepted by mingus.core.keys.get_notes (i.e., conform to the keys/notes formatting rules used by the keys module).
        - Required positional parameter; no default.
        - Interdependencies: validity and parsing are delegated to the underlying dominant7/sevenths implementation; invalid formats will cause those helpers to raise NoteFormatError.

## Returns:
    list[str]:
        - A list of four pitch-name strings representing the dominant seventh chord built on the 5th scale degree of the provided key: [root, third, fifth, seventh].
        - Example (C major): ['G', 'B', 'D', 'F'].
        - The returned object is the same list object produced (and possibly cached) by dominant7 / sevenths(key); it is not a defensive copy. Mutating it will mutate cached state visible to other callers.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        - Propagated if the underlying keys.get_notes or other parsing helpers reject the provided key format.
    IndexError
        - Propagated if the underlying sevenths(key) returns fewer than five scale-degree seventh-chords and index 4 is out of range.
    Any other exception raised by underlying helpers
        - Any exception thrown inside dominant7 / sevenths (for example from intervals, notes processing, or cache construction) will propagate unchanged.

## Constraints:
- Preconditions:
    - key must be a string in a format accepted by the keys module.
    - The module-level state and helpers (dominant7 and sevenths) must be available and functioning.
- Postconditions:
    - On success, the function returns the dominant seventh chord (the 5th element of the list returned by sevenths(key)).
    - If sevenths populated a module-level cache, that cache will be populated before this function returns (this function itself does not manage the cache; it only returns the value selected by dominant7).

## Side Effects:
- No direct I/O (files, network, stdout) or external service calls.
- No direct global mutations by V7 itself; however:
    - Because the returned list is a direct reference into the underlying data (often a cached structure), in-place mutation by the caller will alter the cached chord data seen by other callers.
    - Exceptions from underlying helpers may be raised to the caller.

## Control Flow:
flowchart TD
    Start([Start]) --> CallDominant7[Call dominant7(key)]
    CallDominant7 -->|raises exception| Propagate[Propagate exception to caller]
    CallDominant7 -->|returns| ReturnValue[Return dominant7 result]
    ReturnValue --> End([End])

## Examples:
- Basic usage:
    try:
        v7 = V7('C')
        # v7 == ['G', 'B', 'D', 'F']
    except Exception as e:
        # Handle invalid key or other underlying errors
        print("Failed to get V7 chord:", e)

- Handling an invalid key:
    try:
        v7 = V7('InvalidKeyName')  # underlying parsing will raise NoteFormatError
    except NoteFormatError:
        print("Invalid key provided")

- Mutation caveat (shared cached object):
    chords_all = dominant7.__module__ and None  # (illustrative: this function returns the same object as dominant7('C'))
    v7a = V7('C')
    v7a[0] = 'G_mod'  # mutates the cached chord list; subsequent callers will see the change
    # Note: do not rely on immutability of returned chord lists if you need isolation

## `mingus.core.chords.vi` · *function*

## Summary:
Returns the submediant (the triad built on the 6th scale degree) for the given key — a thin alias that maps the Roman numeral VI to the submediant triad.

## Description:
Known callers:
- No direct callers were discovered in the provided context. Typical callers include chord/progression builders, harmonic-analysis utilities, or any code that needs the VI chord of a key (for example, functions assembling common progressions like I–vi–ii–V).
- This function exists as a semantic convenience and public API alias: it exposes the conventional Roman-numeral name "vi" while delegating the actual triad construction and validation to submediant(key). Keeping this alias separate improves readability when constructing or referring to progressions using Roman numerals and centralizes the naming convention without duplicating logic.

## Args:
    key (str):
        - The key or tonic name accepted by the underlying key/triad utilities (e.g., "C", "G", "F#", "Bb").
        - Required parameter; no default value.
        - Interdependencies: the correctness of the result depends entirely on submediant(key) (which in turn depends on keys.get_notes and triads functions).

## Returns:
    list[str]:
        - A triad represented as a list of three pitch-name strings [root, third, fifth], corresponding to the submediant (6th scale degree) of the supplied key (for example, ['A', 'C', 'E'] for C major).
        - The returned object is the value returned by submediant(key). No defensive copy is made by this function; if submediant returns a reference into a cached list, the caller receives that reference.

## Raises:
    - IndexError:
        - If the underlying triads(key) result (used by submediant) does not contain a 6th-degree element (i.e., its length <= 5), attempting to index the sixth element will raise IndexError which propagates through vi.
    - NoteFormatError:
        - Propagated from submediant(key) / keys.get_notes when the provided key string is in an invalid format.
    - Any exception raised by submediant(key):
        - Any other exceptions (FormatError, KeyError, etc.) thrown by the underlying functions propagate unchanged.

## Constraints:
Preconditions:
    - The supplied key must be valid for the project's key-parsing utilities (keys.get_notes and triads) and typically corresponds to a conventional diatonic key (a 7-note scale) so that a 6th-degree triad exists.
    - Module-level caches or state used by triads/submediant must be initialized/available; vi does not initialize such state itself.

Postconditions:
    - On successful return, the caller receives the triad for the 6th scale degree as produced by submediant(key).
    - vi does not perform additional mutations; any caching or state changes are performed by submediant/triads.

## Side Effects:
    - This function performs no I/O and has no direct side effects.
    - It may trigger side effects performed by submediant/triads, such as populating a module-level cache if those helpers compute and cache results for the key.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSub([call submediant(key)])
    CallSub --> SubError{did submediant raise an exception?}
    SubError -->|Yes| Propagate([propagate exception to caller])
    SubError -->|No| HasSixth{does submediant return a triad?}
    HasSixth -->|No (unexpected)| IndexError([propagate IndexError or other error])
    HasSixth -->|Yes| Return([return triad list])
    Return --> End([End])

## Examples:
Example — typical successful usage:
    try:
        vi_chord = vi("C")
        # Expected typical result for C major: ['A', 'C', 'E']
        print("VI (submediant) of C:", vi_chord)
    except Exception as e:
        print("Could not get VI chord:", e)

Example — handling invalid key format:
    try:
        vi("NotAKey")
    except NoteFormatError as e:
        # keys.get_notes or triads will raise NoteFormatError for bad key formats
        print("Bad key format:", e)

Example — handling unexpectedly short scale:
    try:
        vi("SomeNonstandardScale")
    except IndexError:
        # submediant/triads returned too few scale-degree triads to contain a 6th degree
        print("Scale does not contain a 6th-degree triad.")

## `mingus.core.chords.VI` · *function*

## Summary:
Returns the submediant (the triad built on the 6th scale degree) for the given key; a concise Roman-numeral alias that delegates to the canonical submediant accessor.

## Description:
Known callers:
- No direct callers were discovered in the inspected codebase. Typical callers are chord/progression builders, harmonic-analysis utilities, Roman-numeral based APIs, or any code that needs the VI chord as part of a progression (e.g., building I–vi–ii–V progressions).

Context and responsibility:
- This function is a minimal, semantic alias whose sole purpose is to expose the musically-labeled Roman-numeral "VI" for convenience and readability. It delegates all work to submediant(key), which performs triad construction, validation, and any caching. Keeping this alias separate improves API discoverability for users working with Roman-numeral chord names and centralizes the mapping from the Roman numeral VI to the musical concept "submediant."

## Args:
    key (str):
        - The key or tonic name accepted by the library's key/scale utilities (examples: "C", "G", "F#", "Bb").
        - Required; no default.
        - Interdependencies: The returned value depends entirely on submediant(key) (and therefore on triads(key) and keys.get_notes(key)). The semantics and accepted formats for key follow those utilities' rules.

## Returns:
    list[str]:
        - A list of pitch-name strings representing the triad built on the 6th scale degree for the supplied key (conventionally [root, third, fifth]).
        - Example expected return for a major C key: ['A', 'C', 'E'].
        - Notes:
            * The exact pitch-name formatting (e.g., 'Bb' vs 'A#') follows the underlying key/triad utilities.
            * The function returns whatever submediant(key) returns; no defensive copy is made here.

## Raises:
    IndexError:
        - If the underlying triads(key) (called by submediant) returns a sequence shorter than six elements, attempting to access the 6th-degree triad will raise IndexError. This manifests when the scale/triads produced do not contain a 6th-degree triad.

    NoteFormatError:
        - Propagated from the underlying key/scale or triad construction utilities when the supplied key string is invalid or cannot be parsed.

    Any exception raised by submediant(key):
        - Any other exception (FormatError, KeyError, or other exceptions raised by triads/key helpers) will propagate unchanged.

## Constraints:
Preconditions:
    - The key parameter must be valid according to the project's key/scale parsing (keys.get_notes).
    - The environment/module-level caches or state that triads/submediant rely upon must be initialized as required by those utilities.

Postconditions:
    - On success, the function returns the list of pitch-name strings that represent the submediant triad for the given key.
    - The function itself introduces no additional mutations; any caching or side effects come from submediant/triads.

## Side Effects:
    - The function itself performs no I/O and does not mutate global state directly.
    - Calling this function may trigger side effects of submediant(key) or triads(key), such as populating an internal triads cache. Those side effects are performed by the delegated utilities, not by this alias.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubmediant([call submediant(key)])
    CallSubmediant --> SubError{did submediant raise?}
    SubError -->|Yes| Propagate([propagate exception to caller])
    SubError -->|No| ReturnTriad([return triad list from submediant])
    ReturnTriad --> End([End])

## Examples:
- Typical usage:
    Calling VI("C") typically yields ['A', 'C', 'E'] (the submediant triad in C major).

- Handling an invalid key:
    If the provided key is malformed, callers should be prepared to catch NoteFormatError (or the specific parsing exception raised by the underlying utilities).

- Handling an unexpectedly short scale/triad list:
    If triads(key) produces too few scale-degree triads, an IndexError will be raised; callers can catch IndexError to detect nonstandard scales that lack a 6th-degree triad.

## `mingus.core.chords.vi7` · *function*

## Summary:
Returns the diatonic seventh chord built on the submediant (6th) degree of the supplied key — a concise Roman-numeral-style alias that delegates to the submediant7 helper.

## Description:
- Known callers within the codebase:
    - No internal direct callers were found in the provided snapshots. This function is a small, public convenience intended for higher-level chord/analysis functions or user code that prefers Roman-numeral naming (vi7).
- Why this logic is extracted into its own function:
    - Responsibility boundary: vi7 exists solely as an expressive alias mapping the Roman numeral "vi7" to the semantic operation "submediant seventh chord", making client code more readable.
    - Delegation chain: vi7 directly calls submediant7(key) and returns its result. submediant7, in turn, delegates scale computation, chord assembly, validation, and any caching to a lower-level helper (sevenths). Therefore, computation and error handling are implemented by submediant7/sevenths; vi7 does not implement or intercept them and simply propagates their results and exceptions.

## Args:
    key (str):
        - The musical key context used to compute diatonic chords (examples: "C", "G", "F#", "Bb").
        - Required. Must be in a format accepted by the underlying keys/sevenths helpers (see submediant7 / keys.get_notes).
        - vi7 performs no validation itself; all parsing/validation is performed by the delegated helpers.

## Returns:
    list[str]:
        - A list of pitch-name strings representing the submediant (6th degree) seventh chord in the given key.
        - Convention: typically a four-element list [root, third, fifth, seventh] for the 6th scale degree (e.g., for "C": ['A', 'C', 'E', 'G']).
        - The returned list is the same object returned by submediant7(key). Mutating the returned list or its elements may modify a shared cached structure maintained by the delegated helpers.

## Raises:
    - mingus.core.mt_exceptions.NoteFormatError (propagated):
        - If the provided key string is malformed or cannot be parsed by keys.get_notes (via sevenths), the exception propagates through submediant7 to vi7.
    - IndexError (propagated):
        - If the delegated sevenths(key) sequence lacks a 6th-degree element, attempts by submediant7 to index the 6th element will raise IndexError; vi7 does not catch this.
    - Any other exception raised by submediant7 or its callees will propagate unchanged through vi7.

## Constraints:
- Preconditions:
    - key must be a string acceptable to the keys/sevenths helpers used by submediant7.
    - vi7 assumes submediant7 and the underlying sevenths helper exist and implement their documented behaviors.
- Postconditions:
    - On success, the exact list returned by submediant7(key) is returned to the caller.
    - vi7 itself performs no additional state mutation; any cache population or mutation is done by the delegated helpers.

## Side Effects:
    - No direct I/O (no file, network, or stdout operations).
    - Indirect: returns a reference to data produced by submediant7/sevenths. Mutating that returned list will affect any shared cached data used by those helpers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubmediant7[Call submediant7(key)]
    CallSubmediant7 -->|submediant7 raises NoteFormatError or other| PropagateEx[Propagate exception to caller]
    CallSubmediant7 -->|submediant7 returns chord list| ReturnChord[Return chord list to caller]
    ReturnChord --> End([End])
    PropagateEx --> End

## Examples:
- Typical successful usage:
    try:
        chord = vi7('C')  # returns ['A', 'C', 'E', 'G'] (A minor seventh)
        print("vi7 in C:", chord)
    except Exception as e:
        print("Failed to get vi7:", e)

- Handling invalid key format:
    try:
        chord = vi7('InvalidKey')
    except NoteFormatError:
        print("Provided key was invalid")

- Defensive handling for missing 6th degree:
    try:
        chord = vi7('SomeNonstandardKey')
    except IndexError:
        # Underlying helper did not provide a 6th-degree chord
        print("Submediant (6th degree) not available for this key")
    except Exception as e:
        print("Other error:", e)

- Mutation caveat (shared cache):
    chords = vi7('C')
    chords[0] = 'A_mod'  # mutates the cached chord for 'C'; future calls see this change

## `mingus.core.chords.VI7` · *function*

## Summary:
Returns the diatonic seventh chord built on the submediant (6th) scale degree for the supplied key by delegating to the underlying submediant7 helper.

## Description:
- Known callers within the codebase:
    - No internal direct callers were found in the provided snapshots. This function is a small public API convenience offered to library users and higher-level chord/analysis code that prefer Roman-numeral naming (VI7) instead of the descriptive name (submediant7).
- Why this logic is extracted into its own function:
    - Responsibility boundary: VI7 exists as a concise, semantic alias that maps the Roman-numeral chord name to the underlying implementation that computes the 6th-degree seventh chord. Extracting this alias keeps the public API readable (users can call VI7 or submediant7 interchangeably) and avoids inlining or duplicating the chord-construction logic across multiple places. All computation, validation, caching, and error handling are delegated to submediant7 (and ultimately to the shared sevenths/key helpers).

## Args:
    key (str):
        - The musical key context used to compute the diatonic chord (examples: "C", "G", "F#", "Bb").
        - Must be in a format accepted by the library's key/notes helpers (see the keys module).
        - No default value; this parameter is required.
        - Interdependencies: correctness depends on the behavior of submediant7 and the chain of helpers it calls (sevenths, keys.get_notes, intervals, etc.). Invalid or malformed key strings will cause underlying helpers to raise an exception (e.g., NoteFormatError).

## Returns:
    list[str]:
        - A list of pitch-name strings representing the submediant seventh chord in the given key.
        - Conventionally this is a four-element list [root, third, fifth, seventh] for the 6th scale degree (for example, VI7('C') -> ['A', 'C', 'E', 'G']).
        - The returned list is the exact object returned by submediant7 (which may be a direct reference into a shared cache). Mutating the returned list will mutate that cached structure.

## Raises:
    - IndexError:
        - If the underlying helper returns fewer than six diatonic chords (so the 6th-degree entry is absent) an IndexError from the list access will propagate.
    - mingus.core.mt_exceptions.NoteFormatError (propagated):
        - If the provided key string is invalid and the underlying key/notes helpers raise NoteFormatError, that exception propagates unchanged.
    - Any exception raised by submediant7 or deeper helpers:
        - Other exceptions raised by the computation chain (e.g., unexpected type errors or other validation errors) are not caught and will propagate to the caller.

## Constraints:
- Preconditions:
    - The caller must pass a key string accepted by the keys/notes helpers.
    - The runtime environment must have the underlying chord-building helpers (submediant7 / sevenths) available and functioning; VI7 solely forwards to them.
- Postconditions:
    - On success, the function returns a list of pitch-name strings representing the submediant seventh chord for the given key.
    - No module-level state is modified by VI7 itself; any caching or stateful behavior is performed by the delegated helpers.

## Side Effects:
    - No I/O (files, network) or direct external service calls.
    - Possible indirect side-effect: because the returned object may be a reference into a shared cache, mutating elements of the returned list will mutate shared cached data visible to other callers.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubmediant7[Call submediant7(key)]
    CallSubmediant7 -->|submediant7 raises NoteFormatError or other| PropagateEx[Propagate exception to caller]
    CallSubmediant7 -->|submediant7 returns chord list| ReturnChord[Return the chord list to caller]
    ReturnChord --> End([End])
    PropagateEx --> End

## Examples:
- Typical successful usage:
    try:
        chord = VI7('C')  # delegates to submediant7('C'); expected ['A', 'C', 'E', 'G']
        print("VI7 in C:", chord)
    except Exception as e:
        print("Failed to obtain VI7:", e)

- Handling invalid key format:
    try:
        chord = VI7('InvalidKey')
    except NoteFormatError:
        print("Provided key format was invalid")

- Defensive handling for missing 6th degree (defensive, uncommon):
    try:
        chord = VI7('SomeNonstandardKey')
    except IndexError:
        # Underlying helper did not provide a 6th-degree chord
        print("Submediant (6th degree) not available for this key")
    except Exception as e:
        print("Other error when computing VI7:", e)

- Mutation caveat (shared cache):
    chords = VI7('C')
    chords[0] = 'A_modified'  # mutates the cached chord for 'C'; future calls may observe this change

## `mingus.core.chords.vii` · *function*

## Summary:
Returns the subtonic (triad built on the seventh scale degree) for the given key by delegating to the subtonic helper.

## Description:
- Known callers within the supplied codebase: none discovered.
- Typical callers: chord lookup utilities, roman-numeral symbol resolvers, progression builders, analysis routines, or any code that prefers a Roman-numeral-style API (vii) rather than the descriptive name (subtonic).
- Why this function exists: it provides a small, self-documenting alias following Roman-numeral naming conventions (vii) so callers can request the seventh-degree triad using conventional harmonic notation. Extracting this alias into its own function keeps the API consistent and discoverable (callers can import vii directly), without duplicating triad lookup logic.

## Args:
    key (str):
        - The key or tonic identifier accepted by the underlying key/triad utilities (for example: "C", "G", "F#", "Bb").
        - Required; no default.
        - The exact validation and accepted spellings follow the rules of keys.get_notes and triads; invalid formats will be rejected by those helpers.

## Returns:
    list[str]:
        - The triad (3-element list of pitch-name strings) representing the seventh scale-degree chord for the specified key.
        - The return value is exactly the value produced by subtonic(key), i.e., triads(key)[6] from the module-level triads implementation.
        - Examples of typical returns (dependent on triads implementation): for key "C" a diatonic implementation might return ['B', 'D', 'F'].

## Raises:
    - Any exception raised by subtonic(key) is propagated unchanged.
    - Common propagated exceptions include:
        - NoteFormatError: when the provided key string is not recognized or malformatted (raised by key parsing helpers).
        - IndexError: if the underlying triads list has fewer than 7 elements and index 6 is out of range.
        - Other runtime errors raised by triads(key) or its helpers may also propagate.

## Constraints:
- Preconditions:
    - The module-level triads and key parsing utilities must be available and accept the provided key value.
    - The caller should provide a syntactically valid key string per project conventions.
- Postconditions:
    - On success, the returned list is the subtonic triad for the requested key.
    - No additional side-effects are caused by this wrapper beyond whatever subtonic(key) performs.

## Side Effects:
- This function itself performs no I/O, network calls, or direct global state mutation.
- Indirect side effects depend entirely on subtonic(key) and the triads implementation (for example, triads(key) may populate an internal cache).

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubtonic[Call subtonic(key)]
    CallSubtonic --> SubtonicError{subtonic raised an exception?}
    SubtonicError -->|Yes| PropagateErr[Propagate exception]
    SubtonicError -->|No| ReturnValue[Return subtonic(key) result]
    ReturnValue --> End([End])

## Examples:
Example — successful retrieval:
    try:
        chord = vii("C")
        # Expected (diatonic example): ['B', 'D', 'F']
        print("vii triad for C:", chord)
    except Exception as exc:
        print("Error obtaining vii triad:", exc)

Example — handling bad key format:
    try:
        vii("NotAKey")
    except NoteFormatError as e:
        print("Invalid key:", e)

Example — handling missing seventh degree:
    try:
        vii("SomeNonStandardKey")
    except IndexError:
        print("The subtonic triad is not available for this key (insufficient scale degrees).")

## `mingus.core.chords.VII` · *function*

## Summary:
Returns the subtonic (triad built on the seventh scale degree) for the given key by delegating to the shared subtonic accessor.

## Description:
- Known callers within the provided codebase: none discovered.
- Typical callers: chord lookup utilities, Roman-numeral resolvers, progression builders, harmonic-analysis routines, or any consumer that expects a convenience function named for the Roman numeral "VII".
- Why this exists: This function is a tiny, self-documenting alias that maps the Roman-numeral label "VII" to the implementation that retrieves the subtonic triad. Keeping this alias separate improves API discoverability (users scanning for Roman-numeral helpers will find VII) and keeps naming/semantic responsibilities distinct from lower-level triad construction logic. It enforces the single responsibility of being a semantic alias rather than reimplementing triad lookup or scale handling.

## Args:
    key (str):
        - The key/tonic identifier accepted by the library's key/triad utilities (for example: "C", "G", "F#", "Bb").
        - Required: no default value.
        - Interdependencies: The exact accepted formats and spellings are determined by the keys.get_notes and triads implementations. Passing an invalid key string will cause the underlying routines to raise format-related exceptions.

## Returns:
    list[str]:
        - A 3-element list of pitch-name strings representing the subtonic triad for the supplied key: [root, third, fifth].
        - The returned list is the exact object produced by the underlying subtonic/triads routine (no copying is performed by this wrapper).
        - Examples (typical diatonic behavior):
            * For key "C": ['B', 'D', 'F']
            * For key "G": ['F#', 'A', 'C']
        - If the underlying triad provider returns a different structure, this function returns that same object unchanged.

## Raises:
    IndexError:
        - If the underlying triads list does not contain a seventh element (i.e., fewer than 7 triads), the attempt to access index 6 will raise IndexError.

    NoteFormatError:
        - If the provided key string is not recognized or malformatted, this exception (or other format-related exceptions thrown by keys.get_notes / triads) will propagate.

    Any exception raised by subtonic/triads or their helpers:
        - All exceptions raised by the delegated implementation (e.g., TypeError, ValueError, KeyError, FormatError) are propagated unchanged.

## Constraints:
Preconditions:
    - The triad-building machinery (triads/subtonic or keys.get_notes) must be available and able to accept the provided key argument.
    - Caller should provide a key in the accepted format for the host library.

Postconditions:
    - On success, the function returns the subtonic triad list corresponding to the provided key.
    - The function performs no additional mutation beyond what the delegated routines perform (e.g., caching done by triads may be affected).

## Side Effects:
    - No direct I/O, network calls, or global state mutations are performed by this wrapper itself.
    - Indirect side effects depend on subtonic/triads (for example, those functions may populate an internal cache on first invocation).

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubtonic[Call subtonic(key)]
    CallSubtonic --> SubtonicError{subtonic raised an exception?}
    SubtonicError -->|Yes| PropagateErr[Propagate exception to caller]
    SubtonicError -->|No| ReturnValue[Return subtonic(key) result]
    ReturnValue --> End([End])

## Examples:
Example — successful retrieval:
    try:
        vii = VII("C")
        # Expected (diatonic) result: ['B', 'D', 'F']
        print("VII (subtonic) for C:", vii)
    except Exception as exc:
        print("Failed to get VII:", exc)

Example — invalid key:
    try:
        VII("NotAKey")
    except NoteFormatError as e:
        # The keys/triads logic will raise NoteFormatError for unrecognized key formats
        print("Bad key format:", e)

Example — insufficient scale degrees:
    try:
        VII("NonStandardKey")
    except IndexError:
        # Underlying triad list had fewer than 7 elements
        print("VII (subtonic) is not available for this key")

## `mingus.core.chords.vii7` · *function*

## Summary:
Returns the subtonic (the triad built on the seventh scale degree) for the given key by delegating to the subtonic accessor.

## Description:
This is a tiny convenience wrapper that delegates directly to the module-level subtonic(key) function and returns its result. It exists to provide an alternative, musically-oriented name (vii7) for retrieving the seventh-degree chord without duplicating logic.

Known callers within the provided codebase: none discovered.
Typical callers (not present in the supplied context): chord lookup utilities, chord-symbol resolvers, progression builders, analysis routines or any code that prefers a "vii7" naming convention.

Responsibility boundary: do not perform any chord construction itself — simply forwards the key argument to subtonic and returns whatever that function returns (including any exceptions).

## Args:
    key (str):
        - The key / tonic identifier accepted by the project's key utilities and by subtonic / triads.
        - Examples: "C", "G", "F#", "Bb" (format follows mingus.core.keys.get_notes conventions).
        - Required (no default). The correctness of the value is validated by subtonic/triads.

## Returns:
    list[str]:
        - The triad (3-element list of pitch-name strings) representing the chord built on the seventh scale degree for the supplied key.
        - The exact value is the object returned by subtonic(key) (no copying or transformation is performed here).
        - Edge cases: if subtonic(key) returns an unexpected structure, that structure is returned unchanged.

## Raises:
    - Any exception raised by subtonic(key) is propagated unchanged. Common propagated exceptions include:
        - NoteFormatError: if the provided key string is malformed or not recognized by the key/triad utilities.
        - IndexError: if subtonic (via triads) attempts to index into a list with fewer than 7 elements.
        - Any other runtime errors raised by lower-level helpers called by subtonic.

## Constraints:
Preconditions:
    - The module-level subtonic and underlying triads/key utilities must be available and accept the provided key.
    - Caller should pass a key in the format expected by the mingus key utilities.

Postconditions:
    - On success, the returned value equals subtonic(key) and represents the seventh-degree triad for the requested key.
    - No additional state changes are performed by this function beyond any side effects produced by subtonic(key).

## Side Effects:
    - This function itself has no direct I/O or network side effects.
    - Indirect side effects depend solely on subtonic(key) and its helpers (for example, populating a cache inside triads on first computation).

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubtonic[Call subtonic(key)]
    CallSubtonic --> SubtonicError{subtonic raised an exception?}
    SubtonicError -->|Yes| PropagateErr[Propagate exception to caller]
    SubtonicError -->|No| ReturnValue[Return subtonic(key) result]

## Examples:
Example — successful retrieval:
    try:
        chord = vii7("C")
        # Expected typical diatonic result from subtonic: ['B', 'D', 'F']
        print("vii7 (subtonic) for C:", chord)
    except Exception as exc:
        print("Failed to get vii7:", exc)

Example — handling bad key format:
    try:
        vii7("InvalidKey")
    except NoteFormatError as e:
        # Error originates from subtonic/keys utilities
        print("Bad key:", e)

## `mingus.core.chords.VII7` · *function*

## Summary:
Returns the diatonic seventh chord built on the subtonic (the 7th scale degree) for the supplied key by delegating to the shared subtonic7 helper.

## Description:
Known callers:
- No internal direct callers were found in the available snapshots. This function is part of the public chord helper API in mingus.core.chords and is intended for use by higher-level chord/analysis code or by user code that needs the seventh chord on the subtonic.
- Typical usage: a caller requests the seventh chord whose root is the 7th degree of the specified key (for example, to analyze or display scale-degree-based harmony).

Why this logic is extracted:
- Serves as a concise, semantically named public alias for the subtonic7 implementation. It provides a musical-name convenience to callers (VII7) while keeping the core logic centralized in subtonic7. This avoids duplicating the delegated indexing/access pattern and makes API intent clearer to consumers.

Behavior summary:
- Delegates directly to subtonic7(key) and returns whatever that helper returns. No additional validation, transformation, or defensive copying is performed.

## Args:
    key (str)
        - The key context used to compute diatonic seventh chords (examples: "C", "G", "F#", "Bb").
        - Must be in a format accepted by mingus.core.keys.get_notes (see keys.get_notes for allowed forms).
        - No default; this parameter is required.
        - Interdependencies: validity depends on the keys module and on the underlying chord-building helpers used by subtonic7.

## Returns:
    list[str]
        - A list of pitch-name strings representing the seventh chord built on the subtonic (7th scale degree).
        - Typical shape: a list of four pitch names [root, third, fifth, seventh], e.g. for key "C" the expected return is ['B', 'D', 'F', 'A'].
        - The returned object is exactly the object returned (or referenced) by subtonic7 (and by extension sevenths(key)); no defensive copy is made.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        - Propagated when the provided key is malformed or not recognized by the keys subsystem (raised by underlying helpers such as keys.get_notes).

    mingus.core.mt_exceptions.FormatError
        - May be propagated if an underlying helper validates or formats notes/keys and raises this exception.

    IndexError
        - Raised if the underlying sevenths(key) (accessed by subtonic7) returns fewer than 7 elements so that the 7th element cannot be indexed. This is a direct consequence of the indexing operation performed by subtonic7.

    Any other exception raised by the underlying chord-building helpers
        - Propagated unchanged; this function performs no extra error handling.

## Constraints:
Preconditions:
    - key must be a string accepted by the keys subsystem (keys.get_notes).
    - subtonic7 must be available in the module namespace at call time.

Postconditions:
    - On successful return, the returned list represents the subtonic (7th-scale-degree) seventh chord for the given key.
    - The function does not mutate its inputs or any global state.

## Side Effects:
    - The function itself performs no I/O and does not mutate global state.
    - Indirect side effect: because it returns a reference into data produced by the underlying helpers (which may be cached), in-place mutation of the returned list by the caller will mutate shared state and may affect future callers that observe the same cached object.

## Control Flow:
flowchart TD
    Start([Start]) --> CallSubtonic7[Call subtonic7(key)]
    CallSubtonic7 -->|raises NoteFormatError or FormatError or other| Propagate1[Propagate exception to caller]
    CallSubtonic7 --> ReturnChord[Return the chord list from subtonic7]
    ReturnChord --> End([End])

## Examples:
Example — normal usage:
    Input: VII7("C")
    Output: ['B', 'D', 'F', 'A']

Example — error handling (conceptual):
    Try:
        chord = VII7("InvalidKey")
    Except mingus.core.mt_exceptions.NoteFormatError:
        handle_invalid_key()

Notes:
- This function is intentionally minimal; consult the documentation for subtonic7 and sevenths(key) for full details about caching, exact chord construction rules, and edge cases.

## `mingus.core.chords.invert` · *function*

## Summary:
Performs a single rotation (first-element-to-end) of a chord sequence and returns the rotated sequence.

## Description:
This function takes a sequence representing a chord (ordered notes) and produces its first inversion by moving the first element to the end of the sequence. It is a small, focused utility used to compute a single step of chord inversion without modifying the input in-place.

Known callers within the provided code graph:
- No callers of this function were discovered in the supplied graph snapshot. (There exists a separate function mingus.core.intervals.invert that is unrelated and operates on interval lists.)

Why this logic is extracted:
- The operation is a single, well-defined transformation (rotate a chord by one degree). Extracting it keeps higher-level chord-processing code simpler and enables reuse when generating successive chord inversions or when composing inversion-aware algorithms.

## Args:
    chord (sequence): A non-empty ordered sequence of chord members (commonly a list of note representations such as strings "C", "E", "G" or integers representing pitch classes). The implementation expects a sequence that supports slicing and indexing. Best and intended usage: pass a list of notes (list[str] or list[int]).

Notes on allowed values and interdependencies:
- The sequence must be non-empty.
- The function does not enforce element types — elements may be any Python objects representing notes.
- Input should be a list for predictable behavior (see "Raises" and "Constraints" for details about other sequence types).

## Returns:
    list: A new list representing the chord rotated left by one position (the original first element appears as the last element). For a typical list input, the returned value is a list containing the same elements in rotated order.

Edge-case / variant return details:
- If a list is passed, the operation returns a newly constructed list and does not mutate the input list.
- If a non-list sequence type is provided, behavior depends on that type's slice result and the ability to concatenate with a list; this can raise TypeError (see Raises). For safe and consistent results, convert the input to a list before calling.

## Raises:
    IndexError: If the input sequence is empty (attempting to access chord[0] raises IndexError).
    TypeError: If the input does not support the slice/index operations or if the types of the slice result and the single-element list cannot be concatenated (for example, tuple + list raises TypeError). Any TypeError arises from Python-level sequence/concatenation semantics — the function performs no additional type checks.

## Constraints:
Preconditions:
- chord must be a sequence supporting slicing and indexing (preferably a list).
- chord must contain at least one element.

Postconditions:
- The returned sequence has the same length as the input.
- The multiset of elements in the returned sequence equals that of the input.
- The returned sequence order is a single left rotation of the input: returned[i] == input[i+1] for i in 0..n-2 and returned[n-1] == input[0].

## Side Effects:
- None related to I/O or external state. The function does not mutate the input when passed a list (it builds and returns a new list).
- No global state is read or written.

## Control Flow:
flowchart TD
    Start([Start])
    CheckEmpty{Is chord empty?}
    Start --> CheckEmpty
    CheckEmpty -- Yes --> RaiseIndexError[/IndexError raised/]
    CheckEmpty -- No --> Compute["Compute chord[1:] + [chord[0]]"]
    Compute --> Return[Return rotated sequence]

## Examples:
1) Typical usage with a list of note names:
    Input: ["C", "E", "G"]
    Result: ["E", "G", "C"]

2) Using numeric pitch classes:
    Input: [0, 4, 7]  # C major triad as pitch classes
    Result: [4, 7, 0]

3) Defensive usage to avoid TypeError with non-list sequences:
    If you start with a tuple, convert to list first:
    Input: tuple_chord = ("C", "E", "G")
    Safe call: invert(list(tuple_chord))  # returns ["E", "G", "C"]

4) Error handling example:
    Empty input: []
    Behavior: IndexError is raised (attempt to access chord[0]).
    Defensive check before calling:
        if not chord:
            handle_empty_case()
        else:
            inverted = invert(chord)

Implementation note for reimplementers:
- The minimal correct implementation performs a left rotation by returning chord[1:] + [chord[0]]; ensure callers either pass non-empty lists or guard for empty inputs to avoid IndexError.

## `mingus.core.chords.first_inversion` · *function*

## Summary:
Returns the first inversion of a chord by delegating to the chord rotation utility; the returned sequence is the input rotated left by one position (the original root moved to the end).

## Description:
Known callers:
- No callers were discovered in the supplied code graph snapshot. This function is part of the public chord utilities and is intended to be called by higher-level code that requests the "first inversion" of a chord when building or transforming chord voicings.

Purpose and responsibility:
- This function is a small, explicit API for producing the first inversion of a chord. It exists as a named convenience/semantic alias that delegates the work to the module's invert implementation rather than inlining the rotation logic at every call site. Naming a function first_inversion makes client code clearer and allows the underlying rotation implementation to be changed or optimized in one place (the invert function) without changing call sites.

## Args:
    chord (sequence): A non-empty ordered sequence of chord members representing the chord to invert.
        - Typical element types: strings like "C", "E", "G" or integers representing pitch classes.
        - The sequence must support slicing and indexing (e.g., list). For predictable results pass a list.
        - No default value; the argument is required.
        - Interdependencies: None beyond the expectation that chord is non-empty and sliceable/indexable.

## Returns:
    list: A new sequence (list) representing the chord rotated left by one position:
        - For an input [a0, a1, a2, ..., aN], the returned value is [a1, a2, ..., aN, a0].
        - The returned sequence has the same length and same elements (multiset) as the input, just reordered.
        - If callers want a specific sequence type (e.g., tuple), they should convert the returned list explicitly.

## Raises:
    IndexError: If the input sequence is empty and the underlying rotation attempts to access the first element.
    TypeError: If the input does not support the required slice/index operations or if concatenation between slice results and a single-element list is invalid for the input's sequence types (this arises from Python sequence operations performed by the underlying rotation implementation).

## Constraints:
Preconditions:
- chord must be non-empty.
- chord must be sliceable and indexable (e.g., list-like). Passing arbitrary objects that do not implement these operations is invalid.

Postconditions:
- The returned list length equals the input length.
- The returned order is a single left rotation of the input (element at index i in the return equals element at index i+1 in the input, modulo wrap-around).
- The input is not mutated when a list is passed (the module's invert implementation returns a new list).

## Side Effects:
- None. This function performs no I/O and does not mutate external/global state. It simply delegates to the module-level rotation utility and returns its result.

## Control Flow:
flowchart TD
    Start([Start])
    CallInvert[/"Call module invert(chord)"/]
    Start --> CallInvert
    CallInvert --> Success{invert returns value}
    Success -- Yes --> Return[Return rotated list]
    Success -- No --> Propagate[Propagate IndexError or TypeError raised by invert]

## Examples:
1) Typical usage with note names:
    Input: ["C", "E", "G"]
    Result: ["E", "G", "C"]

2) Numeric pitch classes:
    Input: [0, 4, 7]  # C major triad as pitch classes
    Result: [4, 7, 0]

3) Defensive pattern to avoid empty input errors:
    if not chord:
        handle_empty_case()
    else:
        inverted = first_inversion(chord)

4) Ensuring type consistency (avoid TypeError with non-list sequences):
    tuple_chord = ("C", "E", "G")
    inverted = first_inversion(list(tuple_chord))  # returns ["E", "G", "C"]

Implementation note for reimplementers:
- The minimal implementation re-creates the left-rotation behavior: produce chord[1:] + [chord[0]] and return that new sequence. Ensure you validate or document that an empty input will raise IndexError (or perform an explicit check if you prefer to raise a different error).

## `mingus.core.chords.second_inversion` · *function*

## Summary:
Performs a second inversion of a chord by applying two successive single-step left rotations and returning the resulting ordered chord.

## Description:
This function composes the single-step rotation utility (invert) twice to produce the second inversion of an ordered chord sequence. Calling it is equivalent to rotating the chord left by two positions (or by 2 mod n, where n is the chord length).

Known callers within the provided code snapshot:
- No callers were discovered in the supplied repository snapshot. The function exists as a small, composable utility for chord transformations and is intended for use wherever a semantic "second inversion" transformation is required.

Why this logic is a separate function:
- It captures the musical concept of the "second inversion" as a self-contained operation, providing a clear, readable API. Implementing it by composing invert twice keeps the code DRY and leverages the tested single-rotation behavior rather than duplicating logic for multi-step rotations.

## Args:
    chord (sequence): An ordered sequence of chord members (commonly a list of note names like ["C", "E", "G"] or pitch-class integers like [0, 4, 7]).
        - Required properties: supports indexing and slicing (chord[0], chord[1:]).
        - Recommended: pass a non-empty list (list[str] or list[int]) for consistent and predictable behavior.
        - Interdependencies: behavior depends on how the underlying sequence type handles slicing and concatenation; for non-list sequence types, callers should convert to list first.

## Returns:
    list: A new list representing the chord rotated left by two positions.
        - For an input of length n >= 1, the returned list has length n and contains the same elements in rotated order.
        - Mathematical relation: returned[i] == input[(i + 2) % n] for all valid indices i.
        - For typical list input, the return value is a fresh list (no in-place mutation of the input).

## Raises:
    IndexError:
        - Trigger: If the input sequence is empty. The first call to invert will attempt to access chord[0] and raise IndexError, which propagates out of second_inversion.
    TypeError:
        - Trigger: If the sequence type does not support the slice/index operations or cannot be concatenated with the list used by invert (for example, tuple[1:] + [tuple[0]] raises TypeError). Any TypeError raised by the underlying invert calls will propagate.

## Constraints:
    Preconditions:
        - The caller should ensure chord is a sequence that supports indexing and slicing; ideally a non-empty list.
        - If chord may be empty, the caller must guard against empty input before calling to avoid IndexError.

    Postconditions:
        - On successful return, a list is returned whose length equals len(chord) and whose elements are the original elements rotated left by two positions.
        - The input sequence is not mutated when it is a list (the function composes operations that return new lists).

## Side Effects:
    - None. There is no I/O, no mutation of global state, and no external service calls. Any exception raised is propagated; the function does not catch or transform exceptions from invert.

## Control Flow:
flowchart TD
    Start([Start])
    CallInvert1[/Call invert(chord)/]
    CallInvert2[/Call invert(result_of_invert1)/]
    ReturnResult([Return result_of_invert2])
    Start --> CallInvert1
    CallInvert1 -->|IndexError or TypeError| PropagateError[/Propagate exception/]
    CallInvert1 -->|Success| CallInvert2
    CallInvert2 -->|IndexError or TypeError| PropagateError
    CallInvert2 -->|Success| ReturnResult
    PropagateError --> End([End with exception])
    ReturnResult --> End([End successfully])

## Examples:
1) Typical use with note names:
    Input: ["C", "E", "G"]  # root position C major triad
    Behavior: first invert -> ["E", "G", "C"]; second invert -> ["G", "C", "E"]
    Result: ["G", "C", "E"]

2) Numeric pitch-class example:
    Input: [0, 4, 7]
    Result: [7, 0, 4]  # rotated left twice

3) Short sequences:
    - Single-element: ["C"] -> ["C"] (rotation by 2 mod 1 is identity)
    - Two-elements: ["C", "E"] -> ["C", "E"] (rotation by 2 mod 2 is identity)

4) Defensive use with non-list sequences:
    If you have a tuple: ("C", "E", "G")
    Safe call: convert to list first (list(("C","E","G"))) before passing; otherwise a TypeError may occur when the underlying invert attempts to concatenate slice results with a list.

5) Error handling example:
    Empty input: []
    Behavior: IndexError is raised. Defensive caller pattern:
        if not chord:
            handle_empty()
        else:
            second = second_inversion(list(chord))

Implementation note for reimplementers:
- The simplest correct implementation composes two single-step left-rotations. For list inputs this is equivalently implemented by returning chord[2:] + chord[:2] but composing invert twice (invert(invert(chord))) preserves the same behavior and delegates single-rotation semantics to a single utility.
- Time complexity: O(n). Space complexity: O(n) (returns a new list).

## `mingus.core.chords.third_inversion` · *function*

## Summary:
Returns a new chord sequence rotated left by three positions (the result of applying a single-step inversion three times).

## Description:
This function computes the "third inversion" of an ordered chord sequence by applying the single-step rotate-left inversion operation three times in succession. In practice this means the returned list is the input chord rotated left by three positions (equivalently rotated by (3 mod len(chord)) positions).

Known callers:
- No callers were discovered in the provided codegraph snapshot. This function is a small, public utility intended for use wherever a clearly-named "third inversion" transformation is needed in chord-processing pipelines.

Why this logic is a separate function:
- It encodes a clear musical concept (third inversion) as a single semantic operation instead of requiring callers to call the lower-level invert function multiple times or to reimplement rotation logic. This improves readability and ensures consistent behavior across callers.

## Args:
    chord (sequence): Ordered sequence of chord members (commonly list[str] of note names like "C", "E", "G" or list[int] of pitch classes).
        - Required: must be non-empty.
        - Must support indexing and slicing (best practice: pass a list).
        - Elements can be any Python objects representing notes; the function does not inspect element values.

Interdependencies:
    - The input must satisfy the precondition (non-empty, sliceable). Errors from the underlying invert function (IndexError, TypeError) propagate to the caller.

## Returns:
    list: A new list containing the elements of the input chord rotated left by three positions.
        - If len(chord) == n, the returned list equals input rotated left by (3 mod n) positions.
        - For typical inputs (lists), the returned value is a newly constructed list and the original input is not mutated.

Examples of outcomes:
    - chord length 4: third inversion rotates left by 3 positions (equivalently right by 1).
    - chord length 3: third inversion returns a list identical in order to the input (rotation by 3 mod 3 == 0).
    - chord length 1: returns a new list equal to the input.
    - chord length 0: no valid rotation; see Raises.

## Raises:
    IndexError: If the input sequence is empty. The underlying single-step invert attempts to access chord[0] and will raise IndexError for empty sequences.
    TypeError: If the input does not support the slicing/indexing/concatenation operations used by the underlying invert function (for example, incompatible concatenation between slice result types). Any TypeError originates from Python-level sequence operations inside invert and is propagated.

## Constraints:
Preconditions:
    - chord must be a non-empty sequence supporting indexing and slicing (preferably a list).
Postconditions:
    - The returned object is a list of the same length as the input.
    - The returned list contains exactly the same elements as the input (same multiplicity).
    - Element order is rotated left by 3 positions (equivalently by 3 mod n where n is input length).

## Side Effects:
    - None. The function performs no I/O, does not mutate external/global state, and does not mutate a properly passed list input (a new list is produced by the underlying invert operations).

## Control Flow:
flowchart TD
    Start([Start: call third_inversion(chord)])
    Empty?{Is chord empty?}
    Start --> Empty?
    Empty? -- Yes --> IndexError[/IndexError raised by underlying invert/]
    Empty? -- No --> Inv1["Call invert(chord) -> rotated once"]
    Inv1 --> Inv2["Call invert(result_of_Inv1) -> rotated twice"]
    Inv2 --> Inv3["Call invert(result_of_Inv2) -> rotated three times"]
    Inv3 --> Return[Return final rotated list]
    Return --> End([End])

## Examples:
1) Typical tetrad (4-note chord)
    Input: ["C", "E", "G", "B"]
    Execution: third_inversion(["C","E","G","B"])  # rotates left by 3
    Result: ["B", "C", "E", "G"]

2) Triad (3-note chord) — rotation wraps to original order
    Input: ["C", "E", "G"]
    Execution: third_inversion(["C","E","G"])  # rotation by 3 mod 3 == 0
    Result: ["C", "E", "G"]  # identical order

3) Single-note chord
    Input: ["C"]
    Execution: third_inversion(["C"])
    Result: ["C"]

4) Defensive call for non-list sequences
    # If you have a tuple, convert to list to avoid potential TypeError from concatenation semantics
    Input: ("C", "E", "G", "B")
    Safe call: third_inversion(list(("C", "E", "G", "B")))  # returns ["B","C","E","G"]

5) Error handling example
    Input: []
    Behavior: third_inversion([]) will raise IndexError (propagated from invert).
    Defensive pattern:
        if not chord:
            handle_empty_case()
        else:
            result = third_inversion(chord)

Implementation note for reimplementers:
    - The minimal correct behavior can be implemented by applying a left-rotation operation three times (or by computing rotation offset k = 3 % len(chord) and returning chord[k:] + chord[:k]). Ensure you propagate the same exception behavior for empty and non-sliceable inputs to match callers' expectations.

## `mingus.core.chords.from_shorthand` · *function*

## Summary:
Parses a chord shorthand (or list of shorthands) into explicit chord note lists, supporting root accidentals, normalized chord-type synonyms, slash (bass) notation, and composite chords separated by "|"; returns lists of note-name strings or raises for malformed input.

## Description:
This function converts compact musician chord notations (for example "C", "C#m", "C7/G", "C|G7", or a list like ["C","Dm"]) into the explicit sequence(s) of pitch name tokens that form each chord. It performs small shorthand normalizations, validates the root token, separates root+accidentals from the chord suffix, interprets "|" as a composite-chord operator (recursing with the right side parsed as a slash/bass argument), and interprets "/" as a bass separator in most cases. The function delegates actual chord construction to a module-level mapping named chord_shorthand (keys are suffix strings; values are callables that accept the root name and return list[str]).

Known callers:
- No direct callers were provided in the supplied context. Typical usage:
  - Parsers converting textual chord progressions into playable/processable data structures.
  - Input-handling utilities that accept chord text from users or files.
  - Higher-level APIs that need explicit chord note lists for playback, transposition, or display.

Why this function exists separately:
- Parsing shorthand involves normalization, validation, recursive splitting, and delegation to chord builders. Keeping this logic in one function centralizes parsing rules, reduces duplication, and isolates error handling for malformed chord strings.

## Args:
    shorthand_string (str or list):
        - If str:
            * Expected to begin with a root note character (A-G or a-g) optionally followed by accidentals "#" or "b".
            * After the root+accidentals comes the chord-type suffix (examples: "", "m", "M7", "7", "6/9").
            * Before parsing, the function normalizes these substrings:
                - "min", "mi", "-" -> "m"
                - "maj", "ma" -> "M"
            * If the normalized string is empty, accessing shorthand_string[0] raises IndexError (propagated).
            * The first character (root base letter) is validated via notes.is_valid_note(shorthand_string[0]); if invalid a NoteFormatError is raised.
        - If list:
            * Each element is passed recursively to from_shorthand and the function returns a list of those results (i.e., possibly a list of lists).
            * Nested lists are not flattened; the structure corresponds to input structure.
    slash (None, str, or list; optional):
        - Default None: no explicit bass override.
        - If a str: treated as a bass note token; validated with notes.is_valid_note(slash). If valid, the returned chord list will be [slash] + chord_notes. If invalid, a NoteFormatError is raised.
        - If a list: treated as a mutable bass/voicing list. The function mutates this list in-place by appending elements from the computed chord notes with an append rule described in Returns / Side Effects below, and returns the same list object.
        - If slash is of any other type (e.g., int, dict, object), the function does not handle it specially — it will fall through and the computed chord notes (res) are returned unchanged.

Interdependencies:
    - chord_shorthand must be a module-level mapping of normalized suffix strings to callables that accept root-name strings and return list[str].
    - notes.is_valid_note(...) is used to validate the root character and any string-type slash.

## Returns:
    list[str] or list or []:
    - If shorthand_string is a str and the suffix is recognized:
        * Returns the list produced by chord_shorthand[short_chord](root_name), unless a slash argument modifies the result.
        * If slash is a valid string note, returns a newly created list with the slash note prepended: [slash] + chord_notes.
        * If slash is a list, returns the same list object after mutating it in-place: for each note n in chord_notes, if n != r[-1] (where r is the evolving list), append n; finally return r. This means:
            - The function compares each chord note to the current last element of the passed-in list at each append step and only appends if different from that last element.
            - The original list is modified and returned (callers expecting immutability should pass a copy).
    - If shorthand_string is "NC" or "N.C.": returns an empty list [] (special "no chord" token).
    - If shorthand_string is a list: returns a list whose elements are the results of from_shorthand on each element (structure mirrors input).
    - If an unknown suffix is encountered (not a key in chord_shorthand): the function does not return normally; see Raises.

## Raises:
    NoteFormatError:
        - If the first character of the normalized shorthand is not a valid note:
            "Unrecognised note '%s' in chord '%s'" % (shorthand_string[0], shorthand_string)
        - If slash is provided as a string and is not a valid note:
            "Unrecognised note '%s' in slash chord'%s'" % (slash, slash + shorthand_string)
    FormatError:
        - If the chord suffix is not found in chord_shorthand:
            "Unknown shorthand: %s" % shorthand_string
    IndexError / TypeError:
        - If shorthand_string is an empty string, attempting shorthand_string[0] raises IndexError (propagated).
        - If shorthand_string is None or not indexable/iterable, TypeError/IndexError may be raised while indexing or iterating; these are not caught.
    Propagated exceptions:
        - Any exception raised by the callable returned from chord_shorthand[...] will propagate to the caller.

## Constraints:
Preconditions:
    - chord_shorthand mapping must exist and provide callables that return lists of note-name strings for recognized suffix keys.
    - notes.is_valid_note must accept single-character bases (and accidentals when validating slash strings).
    - Callers should ensure shorthand_string is non-empty when passing strings to avoid IndexError.

Postconditions:
    - On successful return (and when slash is not a list), the returned list is a new list of note-name strings; global state is not mutated by this function.
    - If slash is a list, that list object is mutated and returned.
    - No file or network I/O is performed.

## Side Effects:
    - Mutates the list passed as slash if slash is a list (in-place append behavior described above).
    - Calls into chord_shorthand[...] callables and notes.is_valid_note(...). Any side effects from those callables will occur (this function itself does not perform I/O).

## Control Flow:
flowchart TD
    Start --> IsList{shorthand_string is a list?}
    IsList -- Yes --> ForEach[for x in shorthand_string: result.append(from_shorthand(x))] --> ReturnResults --> End
    IsList -- No --> IsNoChord{shorthand_string == "NC" or "N.C." ?}
    IsNoChord -- Yes --> ReturnEmpty[] --> End
    IsNoChord -- No --> Normalize[Replace "min","mi","-" -> "m" ; "maj","ma" -> "M"]
    Normalize --> ValidateRoot{notes.is_valid_note(shorthand_string[0])?}
    ValidateRoot -- No --> RaiseNoteFormatError --> End
    ValidateRoot -- Yes --> BuildRoot[Collect root name: first char + following '#' or 'b' chars]
    BuildRoot --> rest_of_string := shorthand_string[len(name):]
    BuildRoot --> Scan[Scan rest_of_string for positions of "/" and "|"]
    Scan --> FoundPipe{Found "|" at position s?}
    FoundPipe -- Yes --> Left := shorthand_string[:len(name)+s] ; Right := shorthand_string[len(name)+s+1:]
    FoundPipe -- Yes --> Return from_shorthand(Left, from_shorthand(Right)) --> End
    FoundPipe -- No --> FoundSlash{slash_index != -1 and rest_of_string not in ["m/M7","6/9","6/7"]?}
    FoundSlash -- Yes --> left := shorthand_string[:len(name)+slash_index] ; right := shorthand_string[len(name)+slash_index+1:]
    FoundSlash -- Yes --> Return from_shorthand(left, right) --> End
    FoundSlash -- No --> short_chord := rest_of_string
    short_chord --> InMapping{short_chord in chord_shorthand?}
    InMapping -- No --> RaiseFormatError --> End
    InMapping -- Yes --> res := chord_shorthand[short_chord](name)
    res --> SlashProvided{slash is not None?}
    SlashProvided -- No --> Return res --> End
    SlashProvided -- Yes --> SlashIsString{isinstance(slash, string)?}
    SlashIsString -- Yes --> If notes.is_valid_note(slash): Return [slash] + res  else RaiseNoteFormatError
    SlashProvided -- Yes --> SlashIsList{isinstance(slash, list)?}
    SlashIsList -- Yes --> r := slash ; for n in res: if n != r[-1]: r.append(n) ; Return r
    SlashIsList -- Yes --> End
    SlashProvided -- Yes --> SlashOther{slash neither string nor list?}
    SlashOther -- Yes --> Return res --> End

## Examples (realistic usage and edge cases):
- Basic triad (depends on chord_shorthand mapping):
    result = from_shorthand("C")
    # -> chord_shorthand[""]( "C" ) e.g. ["C","E","G"]

- Normalized minor forms:
    result = from_shorthand("Cmin")  # "min" -> "m"
    # -> chord_shorthand["m"]("C")

    result = from_shorthand("C-")    # "-" -> "m"
    # -> chord_shorthand["m"]("C")

- Slash/bass as string:
    result = from_shorthand("C7", "E")
    # If "E" is valid: returns ["E", ...notes of C7...]

    result = from_shorthand("C7", "NotANote")
    # Raises NoteFormatError("Unrecognised note 'NotANote' in slash chord'NotANoteC7'")

- Slash/bass as list (in-place mutation):
    bass = ["G"]
    result = from_shorthand("C", bass)
    # Suppose chord_shorthand[""]("C") == ["C","E","G"]
    # Loop behavior:
    #   compare "C" to bass[-1] ("G") -> not equal -> append "C" => bass becomes ["G","C"]
    #   compare "E" to bass[-1] ("C") -> append "E" => ["G","C","E"]
    #   compare "G" to bass[-1] ("E") -> append "G" => ["G","C","E","G"]
    # Returns the same 'bass' list object (now mutated).

- Composite using "|":
    # "C|G7" is parsed as:
    #   left = "C" ; right = "G7"
    #   calls from_shorthand("C", from_shorthand("G7"))
    # The inner call from_shorthand("G7") returns a list (e.g. ["G","B","D","F"])
    # That list is passed as the 'slash' argument to the outer call, so the outer call will mutate that list according to slash-list rules and return it.

- Special no-chord tokens:
    from_shorthand("NC")  -> []
    from_shorthand("N.C.") -> []

- Error / edge cases:
    from_shorthand("")           # raises IndexError while trying to access [0]
    from_shorthand("Xmaj")       # raises NoteFormatError if "X" is not valid root
    from_shorthand("Cunknown")   # raises FormatError if "unknown" not in chord_shorthand
    from_shorthand(["C",""])     # second element raises IndexError; the outer call will not catch it

Implementation notes for reimplementation:
    - Implement the normalization replacements exactly as shown before root validation.
    - Build the root name by taking the first character then appending subsequent '#' or 'b' characters until a non-accidental is encountered.
    - When scanning the suffix, record the first "/" position and if a "|" is found return from_shorthand(left, from_shorthand(right)) immediately.
    - Be careful: a "/" is treated as a bass separator unless the entire rest_of_string equals one of the blacklist entries ["m/M7", "6/9", "6/7"]; in those blacklisted cases the slash is considered part of the chord-type and not a bass separator.
    - The function only specially handles slash when it is a string or list; other types are ignored and the base chord list is returned unchanged.

## `mingus.core.chords.determine` · *function*

## Summary:
Routes an ordered sequence of pitch identifiers to the appropriate chord/interval detector based on the exact number of items and returns that detector's identification results.

## Description:
This small dispatcher centralizes length-based routing of chord analysis requests so callers can pass any sequence of pitch identifiers and obtain an appropriate analysis without choosing the detector manually.

Behavior by input length (exact implementation behavior):
- If chord is exactly the empty list object (chord == []): returns [] immediately.
  - Important: this is an equality check against the empty list literal. Other zero-length sequences (for example, an empty tuple ()) do not match this branch.
- Else if len(chord) == 1: returns the same single-element sequence passed in.
- Else if len(chord) == 2: returns a one-element list containing intervals.determine(chord[0], chord[1]) (intervals.determine is called with its default parameters, producing the long descriptive interval string like "major third").
- Else if len(chord) == 3..7: forwards the call to the respective helper:
    - 3 -> determine_triad(chord, shorthand, no_inversions, no_polychords)
    - 4 -> determine_seventh(chord, shorthand, no_inversions, no_polychords)
    - 5 -> determine_extended_chord5(chord, shorthand, no_inversions, no_polychords)
    - 6 -> determine_extended_chord6(chord, shorthand, no_inversions, no_polychords)
    - 7 -> determine_extended_chord7(chord, shorthand, no_inversions, no_polychords)
  Note: determine_extended_chord7 internally ignores its no_inversions parameter (the dispatcher still forwards the flag unchanged).
  Each helper is responsible for its own formatting rules (shorthand vs verbose), inversion exhaustion, and polychord concatenation. The dispatcher does not reformat helper results — it returns them verbatim.
- Else (any other length, including empty sequences that are not the empty list): returns determine_polychords(chord, shorthand).

Why this is a separate function:
- Keeps callers simple: they provide a note list and flags; routing logic (which detector to use) is centralized here.
- Allows individual detectors to focus on their specialized analysis (triads, sevenths, extended chords, polychords) and to manage inversion/polychord logic consistently.

Known callers and typical pipeline stage:
- Public chord-analysis entry points that accept variable-length note lists and want candidate chord names or decompositions without selecting the correct helper.
- Typical usage: normalize/clean a note list, then call determine(...) to obtain a list of candidate chord tokens or polychord decompositions.

## Args:
    chord (sequence):
        - An ordered, indexable sequence of pitch identifier strings (e.g., 'C', 'C#', 'Db').
        - The function performs an exact equality check for the empty list: if chord == [] returns [].
        - The function assumes chord supports len() and indexing. Passing None or a non-sequence will raise TypeError/AttributeError from the interpreter.
    shorthand (bool, optional):
        - Forwarded to helper detectors. If True, helpers produce compact notation (e.g., "Cm9"); if False, they produce verbose names (e.g., "C minor ninth") where supported.
        - Default: False.
    no_inversions (bool, optional):
        - Forwarded to helpers; instructs detectors to skip inversion checks when supported. Default: False.
        - Note: determine_extended_chord7 ignores this flag internally even though it is forwarded.
    no_polychords (bool, optional):
        - Forwarded to helpers; instructs detectors to skip polychord decomposition when supported. Default: False.

## Returns:
    - [] if and only if chord is exactly the empty list object (chord == []).
    - The original single-element sequence when len(chord) == 1.
    - A list containing a single interval-description string when len(chord) == 2: [intervals.determine(chord[0], chord[1])].
    - For len(chord) in 3..7: returns whatever the corresponding helper returns (usually a list of chord name strings; helpers may return False to indicate invalid-length input to that helper).
      * For len == 7: note that determine_extended_chord7 returns a formatted list of names and appends any polychord strings discovered on its first pass; the dispatcher returns that list unchanged.
    - For any other length (including empty sequences that are not the empty list): returns determine_polychords(chord, shorthand).
    - In general, successful results are lists of strings (possibly empty); helpers' False return values (when used) are preserved.

All notable edge returns:
- Passing an empty tuple () will not match the chord == [] test and will be routed to determine_polychords(() , shorthand).
- Helpers may return False for invalid lengths — these False values are returned directly by this dispatcher for len 3..7 cases.
- An empty list ([]) is the only input that yields an immediate [] return without calling helpers.

## Raises:
    - TypeError / AttributeError: If chord is None or a non-indexable object, Python will raise when calling len() or indexing.
    - Any exception raised by intervals.determine or helper functions is propagated unchanged. Examples include:
        * NoteFormatError or FormatError from intervals.determine when invalid note strings are passed.
        * KeyError or TypeError raised by helper detectors when verbose mappings (e.g., chord_shorthand_meaning) are missing or int_desc returns None for some inversion indices.
    - The dispatcher intentionally does not catch or wrap helper exceptions.

## Constraints:
Preconditions:
    - chord must be an ordered sequence of valid note-name strings for meaningful results.
    - If verbose output is desired (shorthand == False), the helper detectors may require module-level mappings (e.g., chord_shorthand_meaning) to contain expected keys; missing keys can cause KeyError to propagate.
Postconditions:
    - The returned object is the exact return value from the chosen branch or helper, with no further transformation by the dispatcher.

## Side Effects:
    - The dispatcher performs no I/O and does not mutate module-level state.
    - Any side effects are due to invoked helpers (which may themselves have side effects or raise exceptions); those are not caused by the dispatcher.

## Control Flow:
flowchart TD
    Start --> IsEmptyList{chord == []?}
    IsEmptyList -- Yes --> ReturnEmpty[return []]
    IsEmptyList -- No --> Len1{len(chord) == 1?}
    Len1 -- Yes --> ReturnSingle[return chord]
    Len1 -- No --> Len2{len(chord) == 2?}
    Len2 -- Yes --> IntervalCall[return [intervals.determine(chord[0], chord[1])]]
    Len2 -- No --> Len3{len(chord) == 3?}
    Len3 -- Yes --> CallTriad[return determine_triad(chord, shorthand, no_inversions, no_polychords)]
    Len3 -- No --> Len4{len(chord) == 4?}
    Len4 -- Yes --> CallSeventh[return determine_seventh(chord, shorthand, no_inversions, no_polychords)]
    Len4 -- No --> Len5{len(chord) == 5?}
    Len5 -- Yes --> CallExt5[return determine_extended_chord5(chord, shorthand, no_inversions, no_polychords)]
    Len5 -- No --> Len6{len(chord) == 6?}
    Len6 -- Yes --> CallExt6[return determine_extended_chord6(chord, shorthand, no_inversions, no_polychords)]
    Len6 -- No --> Len7{len(chord) == 7?}
    Len7 -- Yes --> CallExt7[return determine_extended_chord7(chord, shorthand, no_inversions, no_polychords)  (helper formats results and appends polychords on first pass)]
    Len7 -- No --> CallPolychords[return determine_polychords(chord, shorthand)]

## Examples:
1) Exact empty list
    input: chord = []
    return: []

2) Empty tuple (demonstrates the equality nuance)
    input: chord = ()
    behavior: does not match chord == []; flows to the final else and returns determine_polychords((), shorthand).

3) Two-note interval
    input: chord = ['C', 'E']
    return: ['major third']  (result of intervals.determine('C','E'))

4) Delegate to triad detector
    input: chord = ['C','E','G'], shorthand=True
    behavior: returns determine_triad(['C','E','G'], True, no_inversions=False, no_polychords=False)

5) Seven-note detection note
    input: chord = ['C','E','G','B','D','F','A'], shorthand=False
    behavior: returns determine_extended_chord7(...). That helper will produce formatted names and append any polychord strings discovered on its first pass; the dispatcher returns that list unchanged.

## `mingus.core.chords.determine_triad` · *function*

*No documentation generated.*

## `mingus.core.chords.determine_seventh` · *function*

## Summary:
Identify the possible seventh-chord names (and optional polychords) represented by four pitch identifiers and return them as formatted chord name strings (either shorthand or verbose).

## Description:
This function examines an ordered list/sequence of four pitch labels (the pitch at index 0 is treated as the current root for the first pass) and determines which seventh chords those four pitches can form, including all inversions (unless disabled) and optional polychord decompositions.

Known callers within the provided source context:
- determine_polychords: determine_seventh is included in determine_polychords' function list and will be invoked when polychord decompositions are being built.
- Other higher-level chord-analysis functions in this module typically call determine_seventh when they need to identify or format seventh chords from a list of notes.

Why this logic is factored into its own function:
- It isolates the non-trivial mapping from a four-note pitch set (and its inversions) to chord name candidates, including handling of inversions and optional polychord discovery. This encapsulation keeps triad/extended-chord detection code focused and reusable, and centralizes the mapping rules between triad quality, root-to-seventh interval, and the shorthand/full-name outputs.

## Args:
    seventh (list[str] or tuple[str]): An ordered sequence of exactly four note identifiers (e.g., ['C', 'E', 'G', 'Bb']). Each element is a pitch label in the same format used across the chords module (note names such as 'C', 'C#', 'Db', 'Bb', etc.). The function treats the element at index 0 as the current root for the first inversion pass.
    shorthand (bool, optional): If True, produce compact shorthand names (e.g., "Cm7"). If False, produce verbose names using a mapping (see "Returns" and "Side Effects" for mapping usage). Default False.
    no_inversion (bool, optional): If True, do not attempt chord inversions — only evaluate the chord using the given ordering of notes. If False, the function will rotate the notes to exhaust up to four inversion positions. Default False.
    no_polychords (bool, optional): If True, skip polychord decomposition calls. If False, when analyzing the chord from the original ordering (first pass) the function will call determine_polychords to add polychord names. Default False.

Notes on parameter interdependencies:
- If shorthand is False, the function will use the module-level mapping chord_shorthand_meaning to expand shorthand tokens into verbose strings. That mapping must contain entries for every shorthand the function may produce (for example: "m7", "M7", "7", "m7b5", etc.) or a KeyError may be raised.
- If no_inversion is True, the function returns results for the single ordering provided and will not rotate the sequence to discover names for other inversions.

## Returns:
    list[str] or bool:
    - If the provided seventh sequence does not have length 4, the function immediately returns False.
    - Otherwise, the function returns a list of string chord names. The list contains:
        * Chord names found for each inversion examined (unless no_inversion prevents inversion checking). Each name is constructed as:
            - If shorthand is True: root + shorthand_token (e.g., "C" + "m7" -> "Cm7").
            - If shorthand is False: root + chord_shorthand_meaning[shorthand_token] + int_desc(inversion_index), where:
                - chord_shorthand_meaning is a mapping (dictionary) from shorthand token (e.g., "m7") to a verbose fragment (e.g., " minor seventh" or similar).
                - int_desc(inversion_index) returns a textual inversion suffix for inversion indices 1..4 (for example: "", ", first inversion", ", second inversion", ", third inversion").
              Example verbose construction: "C" + " minor seventh" + ", first inversion".
        * Any polychord strings returned by determine_polychords(seventh, shorthand) when polychords are enabled. determine_polychords produces strings like "<chord1>|<chord2>" and may append " polychord" when shorthand=True depending on its behavior.

Possible values produced:
- Typical shorthand tokens that may appear (based on the mapping logic in this function): "m7", "m/M7", "m6", "M7", "7", "M6", "m7b5", "dim7", "m7+", "M7+", "sus47", "sus4b9", "11", "7b5". The precise final strings depend on chord_shorthand_meaning and the root name.
- If no matching triad/interval combination is found for any inversion, this function will return a list that may be empty or contain only polychord entries (if polychords exist for the input).

## Raises:
    - KeyError: May be raised if shorthand is False and chord_shorthand_meaning does not contain an entry for a shorthand token produced by the internal logic.
    - Any exception raised by helper functions called (for example, determine_triad, determine_polychords, or intervals.determine) will propagate up unchanged. For example:
        * If intervals.determine raises a NoteFormatError for invalid note names, it will propagate.
        * If determine_triad expects a particular note format and raises FormatError, it will propagate.

## Constraints:
Preconditions:
    - The caller must provide exactly four pitch labels in the seventh parameter. Anything else yields an immediate False.
    - The module-level helpers used by this function must follow these interfaces:
        * determine_triad(three_note_sequence, True, True) -> iterable[str]
            - Each returned string must begin with the root note string used in the call (i.e., the same format as seventh[0]). The remainder of each string is a triad-quality token such as "m", "M", "dim", "aug", "sus4", "m7", "7b5", etc.
        * intervals.determine(note_a, note_b) -> str
            - Returns a descriptive interval string such as "minor seventh", "major seventh", "major sixth", "diminished seventh", "minor second", "perfect fourth", etc.
        * determine_polychords(four_note_sequence, shorthand) -> list[str]
            - Returns zero or more polychord string(s) to append to the result list.
        * chord_shorthand_meaning: a dict mapping the shorthand tokens produced by this function (e.g., "m7", "M7") to verbose descriptions. Required only when shorthand is False.
        * int_desc(n) -> str or None: returns a textual inversion suffix for n == 1..4 (otherwise None). The function calls int_desc with values 1..4 only.
Postconditions:
    - If a list is returned, each element is a string representing either a single chord name (constructed as described) or a polychord decomposition string as returned by determine_polychords.
    - The order of returned chord names reflects the order of discovery across inversions (first pass corresponds to the original ordering, subsequent elements correspond to discovered inversions), followed by any polychord strings discovered during the first pass.

## Side Effects:
    - No I/O is performed.
    - No global state is intentionally mutated by this function. However:
        * It calls determine_polychords and determine_triad which may themselves have side effects (but are expected to be pure analytic functions).
        * If chord_shorthand_meaning is mutated elsewhere concurrently, the verbose output may vary; this function itself does not mutate that mapping.

## Control Flow:
flowchart TD
    Start --> CheckLength{len(seventh) == 4?}
    CheckLength -- no --> ReturnFalse[return False]
    CheckLength -- yes --> CallInversionExhauster[inversion_exhauster(seventh, shorthand, tries=1, result=[], polychords=[])]
    CallInversionExhauster --> Triads[triads = determine_triad(seventh[:3], True, True)]
    Triads --> Int[interval = intervals.determine(seventh[0], seventh[3])]
    Int --> MaybeAddPolychords{tries == 1 and not no_polychords?}
    MaybeAddPolychords -- true --> polychords += determine_polychords(seventh, shorthand)
    MaybeAddPolychords -- false --> continue
    TriadLoop[for each triad in triads] --> NormalizeTriad[triad_suffix = triad[len(seventh[0]):]]
    NormalizeTriad --> MatchQuality[match triad_suffix and interval to decide shorthand token]
    MatchQuality --> add_result[append (shorthand_token, tries, root, poly_flag) to result]
    MatchQuality --> EndLoop
    EndLoop --> MoreInversions{tries != 4 and not no_inversion?}
    MoreInversions -- true --> Recurse[rotate notes: new = [last] + rest; call inversion_exhauster(new, shorthand, tries+1, result, polychords)]
    MoreInversions -- false --> BuildOutput[construct final result list using root + token (or verbose mapping + inversion desc) and append polychords]
    BuildOutput --> ReturnList[return result_list + polychords]
    ReturnList --> End

## Examples:
Assume helper functions behave in the usual way for common note names.

1) Basic shorthand example (expected happy path)
    input:
        seventh = ['C', 'E', 'G', 'Bb']
        shorthand = True
        no_inversion = False
        no_polychords = False
    typical behavior:
        - determine_triad(['C','E','G'], True, True) yields strings that encode root + triad token (e.g., "C" + "m" for C minor triad, or "C" + "M" for major).
        - intervals.determine('C', 'Bb') -> "minor seventh"
        - mapping yields shorthand token "m7" for a minor triad with a minor seventh interval
    return (example):
        ['Cm7', ...] plus any polychord strings returned by determine_polychords for the original ordering.

2) Verbose (non-shorthand) example with inversion suffix
    input:
        seventh = ['C', 'E', 'G', 'B']
        shorthand = False
        no_inversion = False
    typical behavior:
        - intervals.determine('C', 'B') -> "major seventh"
        - triad quality -> major triad -> token "M7"
        - int_desc(1) -> "" (root position)
    return (example):
        ['C' + chord_shorthand_meaning['M7'] + int_desc(1), ...]
    where chord_shorthand_meaning['M7'] should expand into a human-readable fragment like " major seventh" (mapping must be provided by the module).

3) Invalid input length
    input:
        seventh = ['C', 'E', 'G']
    return:
        False

Error-handling example:
    If chord_shorthand_meaning lacks a required key and shorthand is False:
        - A KeyError will propagate when the function attempts chord_shorthand_meaning[shorthand_token].
        - Catching code should validate or supply chord_shorthand_meaning entries before calling if verbose output is desired.

Implementation notes for reimplementation:
    - Ensure determine_triad returns strings that begin with the triad root (the same string format used in seventh[0]) so that slicing by len(seventh[0]) yields the triad-quality suffix.
    - intervals.determine must return interval description strings that match those checked in this function (examples used here: "minor seventh", "major seventh", "major sixth", "diminished seventh", "minor second", "perfect fourth").
    - Maintain the same rotation order: the recursive inversion step builds a new list by moving the last element to the front: new = [seventh[-1]] + seventh[:-1], and increments tries from 1..4. The final presentation of the chord names uses the canonical root ordering seventh = [original[3]] + original[0:3] before combining root + token/description.

## `mingus.core.chords.determine_extended_chord5` · *function*

## Summary:
Determine possible extended-chord names (9th/11th/13th variants and related forms) that a sequence of five pitch identifiers can represent; returns a list of chord name strings (shorthand or verbose) or False for invalid input length.

## Description:
This function analyzes an ordered sequence of five pitch labels (strings) and attempts to identify extended-chord names (for example: 9, m9, 11, #11, 13, 6/9, 6/7, 7b9, 7#9, etc.) by combining triad and seventh-quality information with the interval between the sequence's first and fifth notes. The function explores inversions by rotating the note order (unless disabled) and collects matching chord tokens discovered for each inversion. On the first pass it can also include polychord decompositions returned by determine_polychords (unless disabled).

Known callers (within the chords module and common usage):
- Higher-level chord-analysis routines in the same module that want to identify a five-note extended chord from an ordered note list.
- Typical pipeline stage: after a caller has normalized or supplied a 5-note collection, it invokes this function to obtain user-displayable chord name suggestions (either in compact shorthand or verbose form).

Why this logic is extracted:
- The mapping from (triad-quality, seventh-quality, and root-to-fifth interval) to extended-chord tokens is a non-trivial rule-set that depends on inversion position and optional polychord decomposition. Encapsulating it keeps the higher-level chord-detection code focused and makes inversion/polychord handling reusable and testable.

## Args:
    chord (list[str] or tuple[str]):
        - Exactly 5 pitch identifiers (ordered). Example formats: 'C', 'C#', 'Db', 'Bb', etc.
        - The element at index 0 is treated as the "current root" for that pass; inversions are explored by rotating elements.
    shorthand (bool, optional):
        - If True, produce compact chord names like "Cm9" or "C13".
        - If False, produce verbose strings by expanding shorthand tokens using the module mapping chord_shorthand_meaning and appending an inversion suffix from int_desc.
        - Default: False
    no_inversions (bool, optional):
        - If True, do not attempt inversions; only the supplied ordering is evaluated.
        - If False, the function will rotate the sequence up to 5 times (tries = 1..5) to examine each inversion position.
        - Default: False
    no_polychords (bool, optional):
        - If True, skip querying determine_polychords and therefore do not include polychord decompositions in returned results.
        - If False, determine_polychords(chord, shorthand) is called only on the first pass (tries == 1) and any returned strings are appended to the final result list.
        - Default: False

Notes on interdependencies:
- When shorthand is False the function indexes chord_shorthand_meaning with tokens discovered internally (e.g., "m9", "M9", "13"). That mapping must include entries for any token the internal logic can produce or a KeyError will result.
- The function relies on determine_triad and determine_seventh producing strings that begin with the root pitch label passed in; the function slices off that root prefix to extract the triad/seventh-quality token.

## Returns:
    list[str] or bool
    - If chord is not length 5: returns False immediately.
    - Otherwise returns a list of strings representing identified chord names and any polychord strings (if polychords were collected).
        * When shorthand == True: each chord name is root + shorthand_token (e.g., "C" + "m9" -> "Cm9").
        * When shorthand == False: each chord name is root + chord_shorthand_meaning[shorthand_token] + int_desc(tries), where tries is the 1-based inversion pass when that token was discovered.
        * Polychord strings (returned from determine_polychords) are appended to the returned list as-is.
    - The returned list may be empty (no matches) or contain only polychord entries if triangular/seventh matches are absent but polychords were found.

All notable return-edge cases:
- False for wrong-length input (len != 5).
- Empty list when no extended-chord matches and no polychords were found.
- List with only polychord strings when polychord decompositions exist but no extended-chord tokens were matched.

## Raises:
    - KeyError:
        * May be raised when shorthand == False if chord_shorthand_meaning lacks an entry for a discovered shorthand token (the code looks up chord_shorthand_meaning[r[0]]).
    - Exceptions propagated from helper functions:
        * Any exception thrown by determine_triad, determine_seventh, determine_polychords, or intervals.determine will propagate unchanged. Examples from module imports include NoteFormatError or FormatError if invalid note names are supplied.
    - No exceptions are explicitly raised by this function for normal control flow (other than those described).

## Constraints:
Preconditions:
    - chord must be an ordered sequence of exactly 5 valid pitch labels recognizable by intervals.determine and the helper analyzers.
    - chord_shorthand_meaning must be populated with verbose expansions for any shorthand tokens required if shorthand is False.
    - int_desc must be available and return a string or None for tries values (the function calls int_desc with values 1..5 via the tries counter; typical valid returns are for 1..4).

Postconditions:
    - If a list is returned, each element is a string representing either an extended-chord name (shorthand or verbose with inversion suffix) or a polychord decomposition string.
    - The order of chord-name entries reflects discovery order across inversion passes; polychord entries (if any) are appended at the end (they are only gathered on the first pass).

## Side Effects:
    - No direct I/O (no files, network, or stdout).
    - The function does not intentionally mutate module-level state. However it calls helper functions (determine_triad, determine_seventh, determine_polychords) which may have their own side effects; callers should assume analysis helpers are pure.
    - The function reads module-level mappings (e.g., chord_shorthand_meaning) when verbose output is requested.

## Control Flow:
flowchart TD
    Start --> LenCheck{len(chord) == 5?}
    LenCheck -- No --> ReturnFalse[return False]
    LenCheck -- Yes --> CallExhauster[inversion_exhauster(chord, shorthand, tries=1, result=[], polychords=[])]
    CallExhauster --> ComputeTriads[triads = determine_triad(chord[:3], True, True)]
    CallExhauster --> ComputeSevenths[sevenths = determine_seventh(chord[:4], True, True, True)]
    FirstPassCheck{tries == 1 and not no_polychords?}
    ComputeSevenths --> FirstPassCheck
    FirstPassCheck -- Yes --> Polychords[polychords += determine_polychords(chord, shorthand)]
    FirstPassCheck -- No --> Continue
    IntervalCalc[intval4 = intervals.determine(chord[0], chord[4])] --> ForEachSeventh[for seventh in sevenths]
    ForEachSeventh --> NormalizeSeventh[seventh_suffix = seventh[len(chord[0]):]]
    NormalizeSeventh --> MatchRules[match suffix + intval4 to tokens (M9,m9,m11,9,7b9,7#9,7b12,7#11,13,6/9,6/7,...)]
    MatchRules --> add_result[append (token, tries, root) to result]
    AfterRules --> InversionCheck{tries != 5 and not no_inversions?}
    InversionCheck -- Yes --> RotateAndRecurse[call inversion_exhauster([last] + rest, shorthand, tries+1, result, polychords)]
    InversionCheck -- No --> BuildResults[construct final names: root+token (shorthand) or root+mapping+int_desc(tries) (verbose); append polychords]
    BuildResults --> ReturnList[return result_list + polychords]
    ReturnList --> End

## Examples:
1) Typical shorthand usage (happy path)
    input:
        chord = ['C', 'E', 'G', 'Bb', 'D']
        shorthand = True
        no_inversions = False
        no_polychords = False
    behavior:
        - determine_triad(['C','E','G'], True, True) and determine_seventh(['C','E','G','Bb'], True, True, True) are consulted.
        - intervals.determine('C', 'D') -> "major second" leads to detection of a 9th variant.
    example return:
        ['C9', 'Cm9', ...]  (actual tokens depend on triad/seventh outputs and mapping rules)

2) Verbose output with inversion suffix
    input:
        chord = ['C', 'E', 'G', 'B', 'D']
        shorthand = False
    behavior:
        - If token "M9" is discovered while tries == 1, the function returns strings like:
            "C" + chord_shorthand_meaning['M9'] + int_desc(1)
        - If chord_shorthand_meaning['M9'] == " major ninth", and int_desc(1) == "", result contains "C major ninth".

3) Invalid length
    input:
        chord = ['C', 'E', 'G', 'B']
    return:
        False

4) Error handling for missing verbose mapping
    - If shorthand == False and chord_shorthand_meaning does not contain the required token, a KeyError will propagate. Callers desiring robust behavior should either call with shorthand == True or ensure chord_shorthand_meaning contains necessary keys before calling.

Implementation notes for reimplementation:
    - Mirror the rotation order exactly: the recursive inversion call constructs the next pass as [chord[-1]] + chord[:-1] and increments tries (starting at 1).
    - The loop limit is governed by tries != 5; the function tries up to 5 passes (tries values 1..5) unless no_inversions is True.
    - The function uses intervals.determine(root, fifth) where root is chord[0] and fifth is chord[4] to decide which extended token to add for a given seventh-quality token (the code slices off the root prefix from determine_seventh output to obtain the token to match).

## `mingus.core.chords.determine_extended_chord6` · *function*

## Summary:
Classifies a six-note pitch collection into possible extended-chord name strings (including inversion variants), and optionally includes polychord decompositions; returns False for inputs that are not exactly six notes.

## Description:
This function is responsible for recognizing extended chords that require six pitches (extensions beyond the seventh such as 11/13 variants) by leveraging the five-note extended-chord detector and the interval between the candidate root (chord[0]) and the sixth pitch (chord[5]). It performs these steps in a loop over cyclic inversions (unless disabled) and on the first pass optionally appends polychord decompositions.

Known callers within the codebase:
- determine_polychords: may call determine_extended_chord6 (through polychord generation) when attempting all possible stacked-chord decompositions for longer pitch lists.
Typical pipeline stage:
- Invoked during chord recognition when the analyser has exactly six pitch entries and needs human-readable chord names or shorthand tokens.

Why extracted:
- Encapsulates inversion-exhaustion, combination of five-note detection with interval analysis to produce sixth-based extensions, and optional polychord inclusion. Separating this logic prevents duplication and centralizes six-note-specific rules.

## Args:
    chord (Sequence[str]):
        - An indexable sequence (list/tuple) of exactly 6 note strings in the codebase's note-format (what intervals.determine and the 5-note detector expect).
        - The function immediately returns False if len(chord) != 6.
    shorthand (bool, optional):
        - Default: False
        - If True, produced names use the short token form (root + short token). Example form: "C11" where "11" is the short token.
        - If False, results are expanded using a human-friendly meaning mapping plus an inversion description.
    no_inversions (bool, optional):
        - Default: False
        - If True, only the given ordering is analysed; do not rotate through cyclic inversions.
        - If False, the function will rotate the chord up to 6 times (one per inversion) to discover names for each inversion.
    no_polychords (bool, optional):
        - Default: False
        - If True, skip polychord decomposition attempts.
        - If False, on the first (unrotated) pass the function calls determine_polychords(chord, shorthand) and appends its results to the final list.

Interdependencies and parameter details:
- Calls determine_extended_chord5(chord[:5], True, True, True) — i.e., it requests five-note chord detection in shorthand mode with inversions and polychords disabled for that five-note detection call.
- Calls intervals.determine(chord[0], chord[5]) to inspect the musical interval between the candidate root and the sixth pitch.
- When shorthand is False, it looks up a long-form meaning in a module-level mapping chord_shorthand_meaning keyed by the short token (see Returns / Constraints).

## Returns:
    list[str] or False
    - False: returned immediately when the input sequence length is not 6.
    - list[str]: otherwise. The returned list is the concatenation of:
        1. All extended-chord names discovered while scanning inversions. For each discovered shorthand token r[0] found in inversion number r[1] with root r[2], the output element is:
           - if shorthand == True: r[2] + r[0] (root + short token).
           - if shorthand == False: r[2] + chord_shorthand_meaning[r[0]] + int_desc(r[1]) (root + long-form meaning + inversion suffix).
        2. Any polychord strings returned by determine_polychords on the first pass (unless no_polychords True). These are appended at the end and are not transformed by chord_shorthand_meaning/int_desc.
    - The function can return an empty list if nothing is detected and no polychords are found.

Exact mapping rules (how five-note results map to six-note extensions):
- The function calls determine_extended_chord5(chord[:5], True, True, True), which returns a list of short tokens prefixed with the root name (for example "C9", "Cm9", "CM9", or other tokens returned by the 5-note detector).
- For each returned five-note token string s, the code strips the root prefix using the length of chord[0]:
    suffix = s[len(chord[0]):]
  Then it compares suffix to these exact strings and applies the following mapping based on intval5 = intervals.determine(chord[0], chord[5]):

  - If suffix == "9":
    - intval5 == "perfect fourth"  -> add short token "11"
    - intval5 == "augmented fourth" -> add short token "7#11"
    - intval5 == "major sixth" -> add short token "13"

  - If suffix == "m9":
    - intval5 == "perfect fourth" -> add short token "m11"
    - intval5 == "major sixth" -> add short token "m13"

  - If suffix == "M9":
    - intval5 == "perfect fourth" -> add short token "M11"
    - intval5 == "major sixth" -> add short token "M13"

Notes on mapping behavior:
- Only those suffixes and interval comparisons shown above produce added results; any other suffix value or interval combination is ignored for that five-note candidate.
- The function accumulates results as tuples (short_token, tries, root) where:
    - short_token: the short token string added above (e.g., "11", "7#11", "m13", etc.)
    - tries: 1-based inversion index (1 for original ordering, 2 after one rotation, ..., up to 6)
    - root: chord[0] at the time the short token was identified (the candidate root for that inversion)

## Raises:
    - No exceptions are raised explicitly by this function.
    - Possible propagated exceptions:
        * KeyError when shorthand is False if chord_shorthand_meaning does not contain the generated short_token keys (expected keys include "11","7#11","13","m11","m13","M11","M13").
        * Any exception raised by determine_extended_chord5, determine_polychords, intervals.determine, or int_desc will propagate unchanged.
        * If determine_extended_chord5 unexpectedly returns False (it normally returns a list for a 5-note input), iterating over its result will raise a TypeError; this will propagate.

## Constraints:
Preconditions:
    - chord must be indexable and contain exactly 6 elements.
    - chord[0] must be a string used as the "root prefix" in determine_extended_chord5's return format so that s[len(chord[0]):] correctly extracts the suffix token.
    - chord_shorthand_meaning should contain long-form strings for the short tokens used when shorthand=False.
Postconditions:
    - When a list is returned, all inversion-detected chord names will be present as described and any polychords appended after them.

## Side Effects:
    - No direct I/O.
    - No mutation of global state performed by this function.
    - Delegated calls (determine_polychords, determine_extended_chord5, intervals.determine) may have their own side effects; those are not performed by this function itself but they may propagate.

## Control Flow:
flowchart TD
    Start --> LenCheck{len(chord) == 6?}
    LenCheck -- no --> ReturnFalse["return False"]
    LenCheck -- yes --> CallInvert["call inversion_exhauster(chord, shorthand, 1, [], [])"]
    CallInvert --> InversionBegin{"tries == 1 ?"}
    InversionBegin -- true & not no_polychords --> AddPolychords["polychords += determine_polychords(chord, shorthand)"]
    InversionBegin -- true & no_polychords --> SkipPolychords
    SkipPolychords --> Get5["ch = determine_extended_chord5(chord[:5], True, True, True)"]
    AddPolychords --> Get5
    Get5 --> GetInterval["intval5 = intervals.determine(chord[0], chord[5])"]
    GetInterval --> ForEachCh["for each c in ch:"]
    ForEachCh --> StripSuffix["suffix = c[len(chord[0]):]"]
    StripSuffix --> Check9{"suffix == '9'?"}
    Check9 -- true --> Map9["if intval5 == 'perfect fourth' -> add '11'; elif 'augmented fourth' -> add '7#11'; elif 'major sixth' -> add '13'"]
    Check9 -- false --> Checkm9{"suffix == 'm9'?"}
    Checkm9 -- true --> Mapm9["if intval5 == 'perfect fourth' -> add 'm11'; elif 'major sixth' -> add 'm13'"]
    Checkm9 -- false --> CheckM9{"suffix == 'M9'?"}
    CheckM9 -- true --> MapM9["if intval5 == 'perfect fourth' -> add 'M11'; elif 'major sixth' -> add 'M13'"]
    CheckM9 -- false --> NextC
    NextC --> AfterLoop
    AfterLoop --> InversionNext{"tries != 6 and not no_inversions?"}
    InversionNext -- true --> Rotate["chord = [chord[-1]] + chord[:-1]; tries += 1; repeat inversion_exhauster"]
    InversionNext -- false --> Format["format results into strings (shorthand or expanded)"]
    Format --> ReturnAll["return formatted_results + polychords"]
    ReturnAll --> End

## Examples:
    # Example: success path (note: exact output depends on chord_shorthand_meaning and interval naming)
    chord = ["C", "E", "G", "B", "D", "F"]  # root, 3rd, 5th, 7th, 9th, possible 11th
    names = determine_extended_chord6(chord, shorthand=True)
    # names might include "C11" if determine_extended_chord5 returns a "C9" entry and intervals.determine("C","F") == "perfect fourth".

    # Example: expanded names with inversion text
    names = determine_extended_chord6(chord, shorthand=False)
    # elements will be of the form root + chord_shorthand_meaning[short_token] + int_desc(tries),
    # e.g., "C (eleventh)" or "E (7#11), first inversion" depending on mappings and detection.

    # Example: skip polychords and skip inversions (only current ordering)
    names = determine_extended_chord6(chord, no_polychords=True, no_inversions=True)

    # Example: wrong length returns False
    determine_extended_chord6(["C","E","G"])  # returns False

Notes:
- This documentation documents the exact string comparisons and the interval-to-token mapping so a developer can reimplement the six-note mapping logic precisely.
- Expected short_token keys produced by this function (and therefore expected in chord_shorthand_meaning when shorthand=False) include: "11", "7#11", "13", "m11", "m13", "M11", "M13".

## `mingus.core.chords.determine_extended_chord7` · *function*

## Summary:
Classifies a 7-note pitch collection into possible seven-note extended-chord name strings (including inversion variants) or returns False when the input length is not exactly seven.

## Description:
This function analyzes a sequence of exactly seven note strings and attempts to produce human-readable chord names or shorthand tokens representing 13-type extensions derived from six-note detections plus the seventh pitch. It follows these steps:

- On the first (unrotated) pass, optionally requests polychord decompositions via determine_polychords(chord, shorthand) (unless no_polychords is True) and appends any returned polychord strings to the final output.
- Delegates six-note recognition to determine_extended_chord6(chord[:6], True, True, True) and inspects the musical interval between chord[0] (candidate root) and chord[6] (the 7th pitch) using intervals.determine.
- For each short token returned by the six-note detector (which are strings prefixed by the root name), it strips the root prefix using len(chord[0]) and compares the suffix to "11", "m11", and "M11". If the suffix matches and the interval from root to the 7th pitch equals "major sixth", it records a corresponding 13-type short token ("13", "m13", or "M13").
- It exhausts cyclic inversions by rotating the chord list and repeating the analysis for tries = 1..6 (tries is 1-based). For each detected token it records a tuple (short_token, tries, root_at_detection).
- After processing all inversions, it formats the recorded tuples:
    - If shorthand == True: each tuple becomes root + short_token (e.g., "C13").
    - If shorthand == False: each tuple becomes root + chord_shorthand_meaning[short_token] + int_desc(tries).
- Finally, it returns the formatted list concatenated with any polychord strings discovered on the first pass.

Known callers:
- determine_polychords includes determine_extended_chord7 in its polychord-generation loop when building decompositions for longer pitch collections.

Why this is factored out:
- Seven-note detection requires combining six-note detection results, interval analysis of the 7th note, inversion exhaustion, and optional polychord inclusion. Centralizing this logic avoids duplication and keeps higher-level chord-recognition code concise.

Important implementation note:
- The no_inversions parameter is present in the signature but not used; the function always cycles through up to 6 inversions. A correct reimplementation should preserve this behavior (unused parameter) unless intentionally changing the API.

## Args:
    chord (Sequence[str]):
        - Required. Indexable sequence (list/tuple) of exactly 7 note strings.
        - Immediate behavior: returns False if len(chord) != 7.
        - Expectation: chord[0] is the root-string prefix present at the start of strings produced by determine_extended_chord6 so that slicing by len(chord[0]) yields the suffix token.
    shorthand (bool, optional):
        - Default: False.
        - True -> format results as short tokens (root + short_token).
        - False -> format results expanded via chord_shorthand_meaning[short_token] + int_desc(tries).
    no_inversions (bool, optional):
        - Default: False.
        - Present but unused in the implementation. The function still rotates the chord through tries = 1..6.
    no_polychords (bool, optional):
        - Default: False.
        - If False, determine_polychords(chord, shorthand) is called on the first pass (tries == 1) and its returned list is appended to the final results. If True, polychord generation is skipped.

## Returns:
    list[str] or False
    - False: returned immediately when len(chord) != 7.
    - list[str]: otherwise. The returned list is the concatenation of:
        1. Formatted detected chord names (possibly empty).
        2. Polychord strings (if any were returned on the first pass and polychords not suppressed).
    - The function may return an empty list if nothing is detected and no polychords exist.

## Raises:
    - The function does not explicitly raise exceptions, but the following exceptions can propagate from implementation details and should be handled by callers or guarded against in a reimplementation:
        * TypeError:
            - If determine_extended_chord6(chord[:6], True, True, True) returns False (unexpected), iterating "for c in ch" will raise TypeError.
            - If shorthand == False and int_desc(tries) returns None (happens for tries values that do not compare equal to 1..4, namely tries == 5 or 6), concatenating chord_shorthand_meaning[short] (a str) with None will raise TypeError.
        * KeyError:
            - When shorthand == False, lookup chord_shorthand_meaning[short_token] will raise KeyError if the short_token (e.g., "13","m13","M13") is not present in the mapping.
        * Any exception raised by determine_polychords, determine_extended_chord6, intervals.determine, or int_desc will propagate unchanged.

## Constraints:
Preconditions:
    - chord must be indexable and len(chord) == 7.
    - determine_extended_chord6 must return an iterable of strings whose elements begin with the same root prefix used as chord[0], otherwise suffix extraction will be invalid.
    - chord_shorthand_meaning should contain entries for any short_tokens produced when shorthand == False to avoid KeyError.
Postconditions:
    - When returning a list, all detected tokens (converted according to shorthand) and any polychords found on the first pass are present; recorded tries values are integers in the range 1..6.

## Side Effects:
    - No I/O or mutation of module-level state is performed by this function itself.
    - It calls other functions which may have side effects; those effects are not caused by this function directly but may propagate.

## Control Flow:
flowchart TD
    Start --> LenCheck{len(chord) == 7?}
    LenCheck -- no --> ReturnFalse["return False"]
    LenCheck -- yes --> CallInvert["call inversion_exhauster(chord, shorthand, 1, [], [])"]
    CallInvert --> FirstPassCheck{"tries == 1 ?"}
    FirstPassCheck -- true & not no_polychords --> AddPolychords["polychords += determine_polychords(chord, shorthand)"]
    FirstPassCheck -- true & no_polychords --> SkipPolychords
    SkipPolychords --> Call6["ch = determine_extended_chord6(chord[:6], True, True, True)"]
    AddPolychords --> Call6
    Call6 --> GetInterval["intval6 = intervals.determine(chord[0], chord[6])"]
    GetInterval --> ForEachC["for each c in ch (strings expected):"]
    ForEachC --> StripSuffix["suffix = c[len(chord[0]):]"]
    StripSuffix --> Check11{"suffix == '11'?"}
    Check11 -- true --> IfMaj6_11["if intval6 == 'major sixth' -> add_result('13')"]
    Check11 -- false --> Checkm11{"suffix == 'm11'?"}
    Checkm11 -- true --> IfMaj6_m11["if intval6 == 'major sixth' -> add_result('m13')"]
    Checkm11 -- false --> CheckM11{"suffix == 'M11'?"}
    CheckM11 -- true --> IfMaj6_M11["if intval6 == 'major sixth' -> add_result('M13')"]
    CheckM11 -- false --> NextC
    NextC --> AfterLoop
    AfterLoop --> TryRotate{"tries != 6 ?"}
    TryRotate -- true --> Rotate["rotate: chord = [chord[-1]] + chord[:-1]; tries += 1; repeat inversion_exhauster"]
    TryRotate -- false --> Format["format tuples into strings (shorthand: root+short; expanded: root+chord_shorthand_meaning[short]+int_desc(tries))"]
    Format --> ReturnAll["return formatted_results + polychords"]
    ReturnAll --> End

## Examples:
    # 1) Basic shorthand usage
    chord = ["C", "E", "G", "B", "D", "F", "A"]
    names = determine_extended_chord7(chord, shorthand=True)
    # Example possible output: ["C13", "E13"]  (depends on six-note detector and interval naming)

    # 2) Expanded format (may raise TypeError for inversion indices 5 or 6)
    try:
        names = determine_extended_chord7(chord, shorthand=False)
    except TypeError:
        # This can happen if int_desc(tries) returned None for tries == 5 or 6
        # or if chord_shorthand_meaning lacks a needed key.
        # A robust caller can recover by normalizing int_desc to "" before concatenation:
        raise

    # 3) Suppress polychord discovery
    names = determine_extended_chord7(chord, no_polychords=True)

    # 4) Wrong length input
    determine_extended_chord7(["C", "E", "G"])  # returns False

Notes for reimplementers:
- The function calls determine_extended_chord6 with explicit flags: determine_extended_chord6(chord[:6], True, True, True). Preserve that call semantics (the six-note detector is requested in shorthand mode with its inversion and polychord flags set True) to match detection behavior.
- Because int_desc returns None for tries values outside 1..4, concatenation when shorthand == False can fail for tries == 5 or 6; a safe reimplementation should either guard int_desc output (use int_desc(tries) or "" ) or extend int_desc to return a string for all expected tries.

## `mingus.core.chords.int_desc` · *function*

## Summary:
Return a small textual suffix describing a chord inversion for values that compare equal to the integers 1 through 4.

## Description:
Maps a 1-based inversion index to a human-readable inversion description fragment intended for appending to a chord name (for example: "Cmaj" + ", first inversion").

Known callers within the provided source context:
- No direct callers were provided in the preloaded source for this task. In typical usage inside chord-formatting code paths, this function is invoked when converting a numeric inversion index into a displayable suffix while assembling a chord name.

Why this logic is factored into its own function:
- It encapsulates the mapping from numeric index to textual suffix so formatting code elsewhere can remain focused on chord construction. Separating this small mapping improves testability and ensures consistent inversion wording across the codebase.

## Args:
    tries (any):
        - Description: Value to be compared against the integers 1..4 to select an inversion description.
        - Expected usage: callers normally pass an integer (1, 2, 3, 4).
        - Matching semantics: the function uses Python's equality operator (==) to compare tries to 1, 2, 3, and 4 in that order. Therefore any value that compares equal to one of those integers (for example, 1.0 or True compare equal to 1) will produce the corresponding output.
        - There is no type checking or coercion performed beyond Python's standard equality comparisons.

## Returns:
    str or None:
        - If tries compares equal to:
            * 1 -> returns "" (empty string; represents root position — no suffix)
            * 2 -> returns ", first inversion"
            * 3 -> returns ", second inversion"
            * 4 -> returns ", third inversion"
        - For any other value (including integers outside 1..4 or objects that do not compare equal to 1..4), the function reaches no return statement and thus returns None.
        - Note: callers that require a stable string should normalize None to "" (for example: suffix = int_desc(x) or "").

## Raises:
    - The function itself does not explicitly raise exceptions.
    - However, if the provided tries value implements a custom __eq__ that raises an exception during comparison, that exception will propagate out of this function unchanged.

## Constraints:
    Preconditions:
        - Prefer passing an integer 1..4 for clear, predictable results.
    Postconditions:
        - If tries equals 1..4 under Python equality, a str is returned as specified above.
        - Otherwise, the function returns None.

## Side Effects:
    - None. No I/O or mutations of external state occur.

## Control Flow:
flowchart TD
    Start --> Compare1{tries == 1}
    Compare1 -- true --> ReturnEmpty["return \"\""]
    Compare1 -- false --> Compare2{tries == 2}
    Compare2 -- true --> ReturnFirst["return \", first inversion\""]
    Compare2 -- false --> Compare3{tries == 3}
    Compare3 -- true --> ReturnSecond["return \", second inversion\""]
    Compare3 -- false --> Compare4{tries == 4}
    Compare4 -- true --> ReturnThird["return \", third inversion\""]
    Compare4 -- false --> ReturnNone["fall through -> return None"]
    ReturnEmpty --> End
    ReturnFirst --> End
    ReturnSecond --> End
    ReturnThird --> End
    ReturnNone --> End

## Examples:
    # Exact integer inputs
    >>> int_desc(1)
    ""
    >>> int_desc(2)
    ", first inversion"

    # Values that compare equal to integers (due to Python equality semantics)
    >>> int_desc(1.0)
    ""
    >>> int_desc(True)
    ""   # because True == 1

    # Out-of-range integers or values that do not compare equal produce None
    >>> int_desc(0) is None
    True
    >>> int_desc(5) is None
    True
    >>> int_desc("2") is None
    True

    # Normalizing the result when appending to a chord name
    chord = "Cmaj"
    suffix = int_desc(2) or ""
    full_name = chord + suffix  # "Cmaj, first inversion"

## `mingus.core.chords.determine_polychords` · *function*

*No documentation generated.*

