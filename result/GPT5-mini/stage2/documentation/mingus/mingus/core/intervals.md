# `intervals.py`

## `mingus.core.intervals.interval` · *function*

## Summary:
Return the note located a diatonic interval (a number of scale steps) away from a given starting note within the specified key's diatonic scale.

## Description:
This function looks up the diatonic scale for the given key (via keys.get_notes) finds the scale degree that matches the base letter of start_note, moves by the specified integer number of diatonic steps (wrapping within the 7-note scale), and returns the spelled note for the resulting degree as given by the key.

Known callers:
- No explicit callers were provided by the inspected context. Typical uses include higher-level music utilities that compute scale relationships, build chords from scale degrees, transpose notes diatonically, or implement interval-based melodic steps.

Why this is a separate function:
- It isolates diatonic interval arithmetic (respecting the key's accidentals and scale ordering) as a reusable operation. This prevents duplicating the logic for locating a note in a key's scale and advancing by a scale-degree interval across the codebase.

## Args:
    key (str)
        - Musical key name passed to keys.get_notes (e.g., "C", "G", "F#", "Bb").
        - If key is unrecognized, keys.get_notes will raise NoteFormatError; that propagates to the caller.
    start_note (str)
        - A note name string validated by notes.is_valid_note.
        - Validation rules (from notes.is_valid_note): the first character must be a recognized base note letter (present in the library's base note dictionary), and any subsequent characters, if present, must be accidentals either 'b' or '#'.
        - Examples: "C", "E", "F#", "Bb".
        - Important: start_note must be a non-empty string (start_note[0] is accessed). The function matches only on the first character (the base letter) and ignores accidentals in start_note for matching; the returned note uses the key's preferred accidentals.
    interval (int)
        - Number of diatonic steps to move from the starting note. Expected to be an integer.
        - Can be zero, positive, or negative. The computation performs modulo 7 arithmetic so any integer reduces into the 0..6 range.
        - If interval is not an integer or not a type that supports addition with an int and modulo operations, a TypeError will occur at runtime.

Interdependencies:
- start_note must be valid per notes.is_valid_note.
- The base letter start_note[0] must appear among the base letters of the list returned by keys.get_notes(key); otherwise index will remain undefined and a runtime error will occur.

## Returns:
    str
    - One of the seven note strings returned by keys.get_notes(key). This string is spelled according to the key's signature (may include '#' or 'b').
    - Always returns a single string from the key's diatonic scale; no enharmonic conversion is performed beyond what get_notes supplies.

Examples:
    - interval("C", "E", 2) -> "G"
    - interval("G", "F#", 1) -> "G"
    - interval("C", "E", -2) -> "C"

## Raises:
    KeyError
        - Raised when notes.is_valid_note(start_note) returns False.
        - Exact condition: start_note is malformed (first character not a known note or contains non-accidental characters after the first). The message is: "The start note '%s' is not a valid note" % start_note
    NoteFormatError
        - May be raised by keys.get_notes(key) if the provided key string is not a recognized key; this exception is not caught and will propagate.
    IndexError
        - Will be raised if start_note is an empty string because the function accesses start_note[0].
    TypeError
        - Will be raised if interval is not an integer (or not compatible with int in the expression (index + interval) % 7), e.g., passing a string or None.
    UnboundLocalError
        - If no note in keys.get_notes(key) has a first character equal to start_note[0], the local variable index is never assigned and accessing it later causes UnboundLocalError.
        - This is a likely runtime error when the base letter of start_note is not present in the key's scale; callers should ensure the start_note base letter exists in the key.

## Constraints:
Preconditions:
    - key must be a valid key string accepted by keys.get_notes.
    - start_note must be a non-empty string and valid according to notes.is_valid_note.
    - The base letter of start_note must appear among the base letters of the notes returned by keys.get_notes(key).
    - interval should be an integer (or integer-like) to avoid TypeError.
Postconditions:
    - The returned note is guaranteed to be one of the 7 strings in keys.get_notes(key).
    - No local or global state is modified by this function itself; however keys.get_notes may update its own internal cache.

## Side Effects:
    - The function itself does not perform I/O or mutate global state.
    - It calls keys.get_notes(key), which may populate or update an internal key cache (_key_cache) as a side effect of that function.

## Control Flow:
flowchart TD
    A[Start] --> B{Is start_note a non-empty string?}
    B -- No --> C[Raise IndexError (start_note[0] access)]
    B -- Yes --> D{notes.is_valid_note(start_note)?}
    D -- No --> E[Raise KeyError("The start note '%s' is not a valid note")]
    D -- Yes --> F[notes_in_key = keys.get_notes(key)]
    F --> G{keys.get_notes raises NoteFormatError?}
    G -- Yes --> H[NoteFormatError propagates]
    G -- No --> I[Loop over notes_in_key]
    I --> J{Does any n have n[0] == start_note[0]?}
    J -- No --> K[No index assigned -> UnboundLocalError when used]
    J -- Yes --> L[index assigned to last matching note's index]
    L --> M{Is interval an integer-compatible type?}
    M -- No --> N[TypeError at (index + interval) % 7]
    M -- Yes --> O[result_index = (index + interval) % 7]
    O --> P[return notes_in_key[result_index]]

Notes on matching:
    - The function compares only the first character of each note in the scale to start_note[0]. If, contrary to typical scale construction, the scale contains multiple notes whose first character equals start_note[0], the implementation sets index to the index of the last matching note encountered in the loop (because it does not break on first match). In standard diatonic scales produced by keys.get_notes, base letters are unique, so this behavior is not expected to change results in normal use.

## Examples (end-to-end including error handling):
1) Normal usage:
    try:
        result = interval("C", "E", 2)
        # result == "G"
    except Exception as exc:
        # handle unexpected error
        raise

2) Handling invalid start_note:
    try:
        interval("C", "H", 1)
    except KeyError as e:
        # H is not a valid note name; handle or propagate
        print("Invalid note:", e)

3) Handling invalid key:
    try:
        interval("NotAKey", "C", 1)
    except Exception as e:
        # keys.get_notes will raise NoteFormatError which propagates here
        print("Invalid key:", e)

Recommendations:
    - Validate inputs before calling to avoid UnboundLocalError and TypeError: ensure start_note is non-empty, notes.is_valid_note(start_note) is True, and start_note[0] appears in keys.get_notes(key).
    - If you require enharmonic-aware matching (matching "Eb" to a "D#" in the scale), replace the simple first-character matching with a more robust enharmonic comparison.

## `mingus.core.intervals.unison` · *function*

## Summary:
Returns the diatonic unison for a given note by delegating to the interval routine; in the current implementation the provided key parameter is ignored and the single note argument is used as both the musical key and the starting note.

## Description:
Known callers:
- No explicit callers discovered in the inspected codebase. Typical callers would be higher-level utilities that request a diatonic "unison" (interval of zero scale steps) for a note as part of scale, chord, or melodic computations.

Why this logic is a separate function:
- Conceptually this is a convenience wrapper that should express the intent "give me the unison of a note within a key" and hide the interval-call details from callers.
- Important implementation note: the function delegates to interval(...) but passes the same value for both the key and start_note arguments (interval(note, note, 0)), therefore the optional key parameter in unison(note, key=None) is not used by the current code. This behavior is factual (reflects the source) and not an intended feature: callers relying on passing a different key via the key parameter will not see that key used.

## Args:
    note (str):
        - A string supplied to both the key and the start_note parameters of interval().
        - Expected to be a valid note name (e.g., "C", "F#", "Bb") when used as a start_note and also to be a valid key name when used as the key argument to keys.get_notes.
        - If the string is empty, an IndexError may occur (access to start_note[0] in interval()).
    key (optional, ignored) (any):
        - Present in the signature but not forwarded to interval; the function ignores this parameter entirely.
        - Passing a value here does not affect behavior; it remains supported for API-compatibility but has no effect.

## Returns:
    str
    - The value returned by interval(note, note, 0).
    - Practically this is one of the seven note strings returned by keys.get_notes(note): the note in the scale whose base letter matches the base letter of the provided note, at the same diatonic degree (interval 0).
    - Possible return characteristics:
        * For typical inputs where the note both names a key and appears in that key's scale, the returned string will usually match the input note's base letter, but accidentals (sharps/flats) may be normalized to the key's spelling.
        * The exact returned spelling is whatever keys.get_notes(note) produces for that scale degree.

## Raises:
    Any exception raised by the delegated interval(...) call; common propagated exceptions include:
    - KeyError:
        - Raised by interval when notes.is_valid_note(start_note) is False. Because unison passes the same string as start_note, an invalid note string will trigger this KeyError with message: "The start note '%s' is not a valid note".
    - NoteFormatError (from keys.get_notes):
        - Raised when the note string is not a valid key name for keys.get_notes(note). This exception is raised by keys.get_notes and is not caught.
    - IndexError:
        - If the supplied note is an empty string, interval accesses start_note[0] and IndexError will be raised.
    - TypeError:
        - If interval's arithmetic attempts fail because non-integer-like types are supplied (e.g., unexpected types that do not support modulo), a TypeError can occur.
    - UnboundLocalError:
        - If keys.get_notes(note) returns a scale that does not contain any note whose first character equals start_note[0], interval may leave its local index unassigned and an UnboundLocalError will occur when the code later uses that variable.

## Constraints:
Preconditions:
    - The single note argument must be a non-empty string and valid according to notes.is_valid_note if you expect the KeyError to be avoided.
    - The same string must also be a recognized key name for keys.get_notes(note) to avoid NoteFormatError; because unison uses the same value for both roles, callers must ensure the string is appropriate as both a key and a start note.
Postconditions:
    - The function returns a single string belonging to the 7-note diatonic scale produced by keys.get_notes(note) (or raises an exception as described above).
    - No local or global state is modified by unison itself; any side effects come from keys.get_notes called within interval (e.g., cache population).

## Side Effects:
    - No I/O or direct state mutation performed by unison.
    - Delegates to interval(), which calls keys.get_notes(note). keys.get_notes may update an internal key cache; those effects propagate.

## Control Flow:
flowchart TD
    A[Start: call unison(note, key)] --> B[Call interval(note, note, 0)]
    B --> C{interval succeeds?}
    C -- Yes --> D[Return resulting note string]
    C -- No --> E[Exception propagates to caller]
    E --> F[Possible exceptions: KeyError, NoteFormatError, IndexError, TypeError, UnboundLocalError]

Notes:
    - unison does not inspect or validate its arguments itself; it relies entirely on interval's behavior and therefore all control decisions occur inside interval.

## Examples:
1) Typical usage (happy path):
    try:
        result = unison("C")
        # result is a string from keys.get_notes("C"), typically "C"
    except Exception as exc:
        # handle or propagate
        raise

2) Demonstrating ignored key parameter:
    # Even though a second argument is supplied, it is ignored by the current implementation.
    unison("C", key="G")  # Equivalent to unison("C") because key is not used
    # This calls interval("C", "C", 0) — the "G" value is not forwarded.

3) Handling invalid note / key:
    try:
        unison("H")  # "H" is not a valid note name in this library
    except KeyError:
        print("Invalid note supplied")
    except Exception as e:
        # Could be NoteFormatError or other propagated error
        print("Other error:", e)

Implementation note for maintainers:
    - If the intended API was unison(note, key=None) -> interval(key, note, 0) (i.e., use the optional key parameter as the musical key), update the call accordingly. As written, the function uses the first argument for both key and start note. This documentation reflects the current, exact behavior.

## `mingus.core.intervals.second` · *function*

## Summary:
Returns the diatonic second (one scale step above) of the given note within the specified key by delegating to the shared diatonic interval routine.

## Description:
This function is a tiny convenience wrapper that calls the central diatonic interval routine with an interval value of 1 so callers can request a "second" using a natural name instead of supplying the numeric step.

Known callers:
- No direct callers were found in the inspected codebase. Typical callers are higher-level utilities that build scale-aware melodic steps, construct chords by scale degree, or otherwise need the note one diatonic step above a given note within a key.

Why this is a separate function:
- Encapsulates the common operation "get the diatonic second" as a named, self-documenting operation rather than repeating interval(..., 1) across the codebase. It improves readability and provides a stable API for the common musical concept of a second.

## Args:
    note (str):
        - A note name string representing the starting note (e.g., "C", "E", "F#", "Bb").
        - This is passed through to the underlying interval routine as the start note argument and must satisfy the same validation rules (non-empty; first character a valid base note letter; any accidentals must be '#' or 'b').
    key (str):
        - A musical key name (e.g., "C", "G", "F#", "Bb") accepted by keys.get_notes.
        - The key determines the diatonic scale used to compute the result.

Notes on parameter relationship:
- The function does not reorder, validate, or normalize its arguments; it simply forwards them into interval(key, note, 1). Any interdependency checks (valid note, valid key, base-letter presence in the scale) are performed by that underlying routine.

## Returns:
    str:
    - The note string that lies one diatonic scale step above the provided starting note within the specified key.
    - The returned string is one of the seven scale degrees returned by keys.get_notes(key) and uses the key's conventional spelling (accidentals chosen according to the key).
    - Examples:
        - second("E", "C") -> "F"   (E in C major -> F)
        - second("C", "G") -> "D"   (C in G major -> D)

## Raises:
    - Any exception raised by the underlying interval routine may propagate unchanged. Common propagated exceptions include:
        KeyError:
            - If the provided starting note is not a valid note string according to notes.is_valid_note (the underlying routine raises KeyError with message "The start note '%s' is not a valid note").
        NoteFormatError:
            - If keys.get_notes(key) rejects the key string as invalid; this exception originates in keys.get_notes and is not caught here.
        IndexError:
            - If an empty string is passed as note (the interval code accesses note[0]).
        TypeError:
            - If the underlying arithmetic in interval expects an integer step and a non-integer (or incompatible type) is provided such that (index + 1) % 7 fails.
        UnboundLocalError:
            - If the base letter of the provided note does not appear among the first characters of the notes in the specified key's scale, the underlying routine may leave its internal index variable unset and raise UnboundLocalError when attempting to compute the result.

## Constraints:
Preconditions:
    - note must be a non-empty, valid note string per notes.is_valid_note.
    - key must be a valid key string accepted by keys.get_notes.
    - The base letter of note (note[0]) should appear among the base letters of keys.get_notes(key) to avoid an UnboundLocalError.
Postconditions:
    - On successful return, the result is guaranteed to be one of the strings in keys.get_notes(key) (the diatonic scale for key).
    - No mutation of external state is performed by second itself; stateful effects (such as key cache population) may occur inside keys.get_notes called by the underlying routine.

## Side Effects:
    - The function performs no I/O and mutates no globals itself.
    - It calls the shared interval routine which calls keys.get_notes(key); that call may update an internal key cache or other internal state inside the keys module.

## Control Flow:
flowchart TD
    A[Start: second(note, key) called] --> B[Call interval(key, note, 1)]
    B --> C{interval validates note via notes.is_valid_note?}
    C -- No --> D[KeyError propagates]
    C -- Yes --> E[keys.get_notes(key) called]
    E --> F{keys.get_notes raises NoteFormatError?}
    F -- Yes --> G[NoteFormatError propagates]
    F -- No --> H[interval computes index of note[0] in scale]
    H --> I{matching base letter found?}
    I -- No --> J[UnboundLocalError when interval uses unassigned index]
    I -- Yes --> K[Compute (index + 1) % 7 and return scale[result_index]]
    K --> L[Return to caller]
    D --> L
    G --> L
    J --> L

## Examples:
1) Normal usage (get the diatonic second):
    try:
        s = second("E", "C")   # Returns "F" (E -> F in C major)
    except Exception as exc:
        # Handle unexpected errors (invalid note or key)
        raise

2) Handling an invalid start note:
    try:
        second("H", "C")
    except KeyError as e:
        # "H" is not a valid note name; handle or propagate
        print("Invalid note:", e)

3) Handling an invalid key:
    try:
        second("C", "NotAKey")
    except Exception as e:
        # keys.get_notes will raise NoteFormatError which propagates here
        print("Invalid key:", e)

Implementation note:
- This function is intentionally minimal: it does no validation itself and relies entirely on the robust behavior and error reporting of the underlying interval(key, start_note, interval) routine.

## `mingus.core.intervals.third` · *function*

## Summary:
Return the note that lies a diatonic third (two diatonic scale steps) above the given starting note within the specified key's diatonic scale.

## Description:
This is a small, intention-revealing wrapper that delegates to the general diatonic interval routine, invoking it with a fixed interval of 2 (two scale steps). It therefore inherits the full validation, matching rules, and error semantics of that underlying routine.

Known callers:
- No explicit callers were discovered in the inspected codebase.
- Typical caller contexts where this helper is useful:
  - Chord construction (e.g., obtaining the 3rd of a chord tone when building triads).
  - Melody/harmony generation that moves voices by a diatonic third within a key.
  - Music-analysis utilities that query intervallic relationships inside a key.

Why this logic is a separate function:
- Makes call sites self-documenting (calling "third" expresses musical intent).
- Avoids repeating the numeric literal 2 in many places, reducing errors.
- Reuses the robust diatonic interval implementation rather than duplicating logic.

## Args:
    note (str)
        - The starting note name (examples: "C", "E", "F#", "Bb").
        - Must be a non-empty string; the implementation accesses note[0] to identify the base letter.
        - Must be valid according to the library's note validation (notes.is_valid_note). If invalid, the underlying routine raises KeyError.
    key (str)
        - The musical key name whose diatonic scale will be used (examples: "C", "G", "F#", "Bb").
        - Passed through to keys.get_notes(key) which returns the seven-note diatonic scale spelled for that key. If the key is unrecognized, keys.get_notes raises NoteFormatError which propagates.

Notes on argument ordering and interdependency:
- third(note, key) calls interval(key, note, 2) — i.e., the key is forwarded as the first argument to the underlying interval routine.
- The base letter (first character) of note must appear among the first characters of the seven notes returned by keys.get_notes(key). If it does not, the underlying routine fails at runtime (see Raises).

## Returns:
    str
    - A single note string that is the diatonic third above the provided note within the specified key.
    - The returned string is chosen from the seven-note scale returned by keys.get_notes(key) and uses that scale's preferred spelling (sharps or flats).
    - Example successful return values: "G" for third("E", "C"), "Bb" for third("G", "F").

## Raises:
All exceptions below are propagated from the delegated diatonic interval routine; third does not catch them.

    KeyError
        - Trigger: The provided note is not a valid note per notes.is_valid_note.
        - Exact message produced by the underlying routine: "The start note '%s' is not a valid note" % note
    NoteFormatError
        - Trigger: keys.get_notes(key) is called with an unrecognized key; keys.get_notes raises NoteFormatError which propagates.
    IndexError
        - Trigger: note is an empty string (attempting to access note[0] causes IndexError).
    UnboundLocalError
        - Trigger: The base letter note[0] is not found among the first characters of any notes in the scale returned by keys.get_notes(key). The underlying implementation assigns the index variable only when matches occur; without any matches, later access produces UnboundLocalError.
    TypeError (or other runtime errors)
        - Trigger: If the interval arithmetic (performed as (index + 2) % 7) encounters incompatible types (unlikely here because 2 is an int), or other unexpected runtime conditions in the delegated routine.

## Constraints:
Preconditions:
    - note: non-empty string and valid according to notes.is_valid_note.
    - key: recognized key string accepted by keys.get_notes.
    - The first character of note must match the base letter of some note in the key's diatonic scale (usually true for normal diatonic scales and valid notes).

Postconditions:
    - On success, the return value is one of the seven note names from keys.get_notes(key) and is the note two diatonic steps above the supplied note within that key.
    - No mutation of global variables or I/O is performed by third itself. keys.get_notes(key) may update its internal cache as a side effect.

Behavioral edge notes:
    - Matching logic: only the first character of each note is compared to note[0]. If the scale contains multiple notes whose first character equals note[0], the underlying implementation uses the index of the last match found. In canonical diatonic scales the base letters are unique, so this is normally irrelevant.
    - This function computes a diatonic third (i.e., two steps in the diatonic scale). Whether that third is major or minor depends on the key and the scale returned by keys.get_notes.

## Side Effects:
    - No direct I/O or global state modification performed by this function.
    - Indirect side effect: calling keys.get_notes(key) may populate or update an internal cache inside the keys module.

## Control Flow:
flowchart TD
    Start[Call third(note, key)] --> CallInterval[Call interval(key, note, 2)]
    CallInterval --> ValidNote{notes.is_valid_note(note)?}
    ValidNote -- No --> RaiseKeyError[KeyError: "The start note '...'' is not a valid note"] --> End
    ValidNote -- Yes --> GetScale[Call keys.get_notes(key)]
    GetScale --> KeyErrorChk{keys.get_notes raises NoteFormatError?}
    KeyErrorChk -- Yes --> PropagateNoteFormatError[NoteFormatError propagates] --> End
    KeyErrorChk -- No --> FindIndex[Loop notes_in_key; match n[0] == note[0]]
    FindIndex --> MatchFound{Any match?}
    MatchFound -- No --> UnboundLocal[UnboundLocalError when index used] --> End
    MatchFound -- Yes --> Compute[(index + 2) % 7] --> Return[Return notes_in_key[result_index]] --> End

## Examples:
Successful example:
    Input: note = "E", key = "C"
    Result: "G"  (the diatonic third above E in C major)

Successful example (key with flats):
    Input: note = "G", key = "F"
    Result: "Bb" (the diatonic third above G in F major, spelled using F major's preferred accidentals)

Failure example — invalid note:
    Call: third("H", "C")
    Outcome: KeyError raised with message "The start note 'H' is not a valid note"

Failure example — invalid key:
    Call: third("C", "NotAKey")
    Outcome: keys.get_notes raises NoteFormatError and that exception propagates

Usage recommendations:
    - Validate note with notes.is_valid_note and ensure the key is recognized by keys.get_notes before calling to avoid the common runtime errors.
    - Use third when you specifically want the diatonic third within a key; use the generic interval routine for arbitrary diatonic distances.

## `mingus.core.intervals.fourth` · *function*

## Summary:
Return the note a diatonic fourth (three scale steps) above a given note within the specified key's diatonic scale.

## Description:
This function is a thin convenience wrapper around the general diatonic interval operation: it computes the diatonic interval of 3 scale steps (a fourth) from the given note inside the provided key.

Known callers:
- No explicit callers were found in the inspected context. Typical uses include:
  - Building chords or voicings that use fourths (e.g., quartal harmony generators).
  - Diatonic melodic/transposition utilities that step a melody by scale degrees.
  - Any higher-level routine that needs the diatonic fourth relative to a note in a given key.

Why this is extracted:
- Encapsulates the common, semantically-named operation "take a fourth" so callers need not pass the numeric interval value repeatedly. It enforces a clear responsibility boundary (compute a diatonic fourth) and keeps call sites expressive.

## Args:
    note (str)
        - The starting note name. Must be a non-empty note string valid according to notes.is_valid_note.
        - Valid examples: "C", "E", "F#", "Bb".
        - Implementation detail: only the first character (the base letter) is used to locate the starting degree in the key's scale; accidentals in this argument are ignored for the matching step but will affect validation.
    key (str)
        - The musical key name passed to keys.get_notes (e.g., "C", "G", "F#", "Bb").
        - Must be a recognized key; otherwise keys.get_notes will raise an error.

Interdependencies:
- note must be valid per notes.is_valid_note.
- The base letter note[0] must appear among the base letters of the list returned by keys.get_notes(key). The function relies on keys.get_notes(key) to provide the spelled scale notes that determine returned accidentals.

## Returns:
    str
    - One of the seven note strings returned by keys.get_notes(key). The returned value is the note that lies three diatonic steps (a fourth) above the supplied note within the supplied key.
    - The returned string uses the spelling (accidentals) preferred by keys.get_notes for that key; no enharmonic conversion is performed beyond that.
    - Examples:
        - fourth("C", "C") -> "F"    (in C major scale, a diatonic fourth above C is F)
        - fourth("D", "C") -> "G"    (a fourth above D in C major is G)

## Raises:
    IndexError
        - If note is an empty string (note[0] access is performed).
    KeyError
        - If notes.is_valid_note(note) returns False. The interval implementation raises KeyError with message: "The start note '%s' is not a valid note" % note.
    NoteFormatError (from keys)
        - Propagated from keys.get_notes(key) when the provided key string is not a recognized key.
    UnboundLocalError
        - If no note in keys.get_notes(key) has a first character equal to note[0], the internal index variable is never assigned; using it later triggers UnboundLocalError. This occurs when the base letter of note is not present in the key's diatonic scale.

Notes on TypeError:
    - The generic interval implementation can raise TypeError if its numeric interval argument is not integer-compatible. fourth always supplies the integer 3, so that particular TypeError is not expected from fourth itself.

## Constraints:
Preconditions:
    - key must be a valid key string accepted by keys.get_notes.
    - note must be a non-empty string and valid according to notes.is_valid_note.
    - The base letter of note (note[0]) must exist among the first characters of notes returned by keys.get_notes(key).
Postconditions:
    - The return value is guaranteed to equal one of the strings returned by keys.get_notes(key).
    - No global state is modified by fourth itself; any side effects come from keys.get_notes (e.g., internal key cache updates).

## Side Effects:
    - No I/O or external network calls.
    - May indirectly trigger keys.get_notes(key) which can populate or update keys' internal caches.

## Control Flow:
flowchart TD
    A[Start] --> B{Is note a non-empty string?}
    B -- No --> C[Raise IndexError (note[0] access)]
    B -- Yes --> D{notes.is_valid_note(note)?}
    D -- No --> E[Raise KeyError("The start note '%s' is not a valid note")]
    D -- Yes --> F[notes_in_key = keys.get_notes(key)]
    F --> G{keys.get_notes raises NoteFormatError?}
    G -- Yes --> H[NoteFormatError propagates]
    G -- No --> I[Find index of scale degree whose first char == note[0]]
    I --> J{Found matching base letter?}
    J -- No --> K[UnboundLocalError when index is later used]
    J -- Yes --> L[result_index = (index + 3) % 7]
    L --> M[return notes_in_key[result_index]]

Notes:
    - Matching uses only the first character of scale notes and of the provided note; in correct diatonic scales base letters are unique so the last-match behavior in a loop is not relevant in normal use.

## Examples:

1) Normal use (C major):
    try:
        result = fourth("C", "C")
        # result == "F"
    except Exception:
        raise

2) Quartal harmony helper:
    # Build a stack of fourths starting from "C" in G major
    try:
        g_major = "G"
        root = "C"
        second = fourth(root, g_major)   # diatonic fourth above C in G major
        third = fourth(second, g_major)
    except Exception as exc:
        # Handle unexpected invalid input or key errors
        print("Error computing fourths:", exc)

3) Error handling — invalid note:
    try:
        fourth("H", "C")   # "H" is not a valid note name
    except KeyError as e:
        print("Invalid start note:", e)

4) Error handling — invalid key:
    try:
        fourth("C", "NotAKey")
    except Exception as e:
        # keys.get_notes will raise a NoteFormatError which is propagated
        print("Invalid key:", e)

## `mingus.core.intervals.fifth` · *function*

## Summary:
Compute the diatonic fifth of a given note within the context of a specified key and return the note name as spelled by that key.

## Description:
This function is a thin wrapper that delegates to the diatonic-interval computation (interval) using an interval of 4 scale steps (a fifth). It returns the note from the key's diatonic scale that lies a fifth above the provided note (as spelled by the key).

Known callers within the codebase:
- No direct internal callers were found in the inspected repository context. Typical external/consumer uses include:
    - Chord-building utilities that need the fifth of a chord tone spelled correctly for a given key.
    - Harmony or voice-leading routines that compute scale-aware intervallic relationships.
    - User-facing API calls where callers request common intervals by name (e.g., fifth) rather than calling the generic interval function.

Why this logic is a separate function:
- It provides a convenient, readable API for a common musical interval (the fifth) without requiring callers to remember numeric interval values or the argument order of the generic interval function. It encapsulates the specific numeric interval (4 diatonic steps) and preserves intention at call sites.

## Args:
    note (str):
        - A note name string (e.g., "C", "E", "F#", "Bb").
        - Must be non-empty; the implementation accesses note[0].
        - Must be valid according to notes.is_valid_note (first character a recognized base letter, subsequent characters only accidentals 'b' or '#').
        - The function uses only the first character of note for matching a scale degree in the key; accidentals in note do not influence which scale degree is selected.
    key (str):
        - A musical key name accepted by keys.get_notes (e.g., "C", "G", "F#", "Bb").
        - keys.get_notes returns the 7-note diatonic spelling for this key and determines accidentals in the returned note.

Interdependencies:
    - The base letter note[0] must appear among the base letters of the sequence returned by keys.get_notes(key). If it does not, the underlying interval function will fail at runtime (see Raises).

## Returns:
    str
    - One of the seven note strings from keys.get_notes(key), representing the diatonic fifth above the supplied note within that key.
    - Example outcomes:
        - fifth("E", "C") -> "B"  (E in the C major scale -> its fifth is B)
        - fifth("C", "F") -> "G"  (C in F major -> its fifth is G)

Edge-case return behavior:
    - The returned note is always chosen directly from the key's diatonic list; no enharmonic conversion beyond the key's spelled notes is performed.
    - If multiple notes in the key share the same starting letter (not typical for properly spelled diatonic scales), the underlying interval implementation selects the last matching index encountered in the key's note list; this function returns the corresponding result.

## Raises:
This function forwards exceptions raised by the underlying interval logic. Caller-visible exceptions include:
    IndexError
        - If note is an empty string (the code accesses note[0] in the underlying logic).
    KeyError
        - If notes.is_valid_note(note) returns False. The underlying code raises:
          "The start note '%s' is not a valid note" % note
    NoteFormatError (or a similar key-related exception from the keys module)
        - If key is not a recognized key name and keys.get_notes(key) raises an error; this propagates unchanged.
    TypeError
        - If the numeric interval arithmetic in the underlying function fails because the interval argument is not integer-compatible (not applicable here since fifth passes a literal integer 4, but can occur indirectly if the underlying code uses types of note/key that break assumptions).
    UnboundLocalError / IndexError-like runtime failure
        - If the base letter note[0] does not appear in the sequence returned by keys.get_notes(key), the underlying implementation may leave the index unset and produce an UnboundLocalError when computing the target degree. This is a runtime error caused by mismatched inputs.

## Constraints:
Preconditions:
    - note must be a non-empty, valid note string per notes.is_valid_note.
    - key must be a valid key string acceptable to keys.get_notes.
    - The base letter of note must appear in the diatonic note list returned by keys.get_notes(key).
Postconditions:
    - On successful return, the value is one of the 7 diatonic notes for the provided key, spelled according to that key's accidentals.
    - No global state is modified by this function itself.

## Side Effects:
    - No I/O or direct global mutation is performed by this function.
    - It calls keys.get_notes(key) (indirectly via interval), which may update or populate an internal key cache in the keys module.

## Control Flow:
flowchart TD
    Start --> CallInterval[Call interval(key, note, 4)]
    CallInterval --> ValidateNote{notes.is_valid_note(note)?}
    ValidateNote -- No --> RaiseKeyError[Raise KeyError: "The start note '%s' is not a valid note"]
    ValidateNote -- Yes --> GetKeyNotes[keys.get_notes(key)]
    GetKeyNotes --> KeyNotesError{keys.get_notes raises NoteFormatError?}
    KeyNotesError -- Yes --> PropagateNoteFormatError[Propagate NoteFormatError]
    KeyNotesError -- No --> FindBaseLetter[Find index where n[0] == note[0] in key notes]
    FindBaseLetter --> NoMatch[No matching base letter found]
    NoMatch --> RuntimeError[UnboundLocalError or IndexError at result computation]
    FindBaseLetter --> Match[Index found]
    Match --> ComputeIndex[result_index = (index + 4) % 7]
    ComputeIndex --> ReturnNote[Return key_notes[result_index]]

## Examples:
1) Typical usage (happy path):
    try:
        fifth_note = fifth("E", "C")
        # fifth_note == "B"
    except Exception as exc:
        # handle or propagate unexpected errors
        raise

2) Invalid start note:
    try:
        fifth("H", "C")   # "H" is not a valid note name
    except KeyError as e:
        print("Invalid note:", e)

3) Invalid key:
    try:
        fifth("C", "NotAKey")
    except Exception as e:
        # keys.get_notes will raise a key/format error which propagates here
        print("Invalid key:", e)

Implementation note for re-implementers:
    - This function performs no computation itself other than calling interval with the arguments reordered and the constant 4. Reimplementing it requires implementing the diatonic interval logic (interval) that:
        * Retrieves a 7-note diatonic spelling for the key (keys.get_notes).
        * Validates the input note (notes.is_valid_note).
        * Finds a scale degree matching the base letter of the input note.
        * Advances that degree by the given number of diatonic steps modulo 7 and returns the spelled note at the resulting degree.

## `mingus.core.intervals.sixth` · *function*

## Summary:
Return the diatonic sixth (five scale steps away) from a given note within the specified key.

## Description:
This function is a thin, semantic wrapper around the general diatonic interval routine: it always requests an interval of 5 (a sixth) from the underlying diatonic interval implementation.

Known callers:
- No direct callers were discovered in the inspected code snapshot. Typical call sites are higher-level music utilities that compute interval relationships, build chords (e.g., adding sixths to triads), create melodic lines by diatonic steps, or provide user-facing helpers in music theory APIs.

Why this logic is extracted:
- It provides a readable, intention-revealing helper for a common music-theory operation (getting a diatonic sixth). Extracting this as its own function avoids repeatedly specifying the numeric interval (5) at call sites and centralizes the intent (sixth) in a single place, improving clarity and discoverability.

## Args:
    note (str)
        - The starting note name (e.g., "C", "E", "F#", "Bb").
        - Must be a non-empty string and valid per notes.is_valid_note. The implementation matches only the first character (the base letter) when locating the start note in the key's diatonic scale.
    key (str)
        - The musical key name used to determine the diatonic scale (e.g., "C", "G", "F#", "Bb").
        - Passed directly to keys.get_notes(key); the key must be recognized by that function.

Interdependencies:
    - The base letter of note (note[0]) must appear among the first characters of the seven notes returned by keys.get_notes(key); otherwise the underlying routine will fail to locate the scale degree.
    - Because this function delegates to the general interval routine with a fixed integer (5), callers do not supply the numeric interval.

## Returns:
    str
    - A single note string taken from the seven-note diatonic scale for the supplied key (one of the strings returned by keys.get_notes(key)).
    - The returned note is spelled according to the key's preferred accidentals (e.g., may contain '#' or 'b').
    - Example: sixth("E", "C") -> "C" (in C major, E up a diatonic sixth becomes C).

## Raises:
    KeyError
        - If notes.is_valid_note(note) returns False. The underlying interval routine raises KeyError with the message "The start note '%s' is not a valid note" % note.
    NoteFormatError (from keys)
        - Propagated from keys.get_notes(key) when the provided key string is not a recognized key (the function does not catch this).
    IndexError
        - If note is an empty string (the underlying code accesses note[0]); this raises IndexError.
    UnboundLocalError
        - If no note in the key's diatonic scale has a first character equal to note[0], the underlying code never assigns an index and later attempts to use it, producing UnboundLocalError.

## Constraints:
Preconditions:
    - note must be a non-empty, valid note string according to notes.is_valid_note.
    - key must be a valid key name accepted by keys.get_notes.
    - The base letter note[0] must exist among the base letters of keys.get_notes(key)'s output.
Postconditions:
    - On success, the returned string is one of the seven correctly spelled notes from keys.get_notes(key).
    - No global state is modified by this function itself; any state changes are limited to side effects within keys.get_notes (e.g., internal caching).

## Side Effects:
    - No direct I/O, network, or stdout output.
    - May trigger internal side effects of keys.get_notes(key) such as populating or updating an internal key cache.

## Control Flow:
flowchart TD
    A[Start: sixth(note, key) called] --> B[Call interval(key, note, 5)]
    B --> C{notes.is_valid_note(note)?}
    C -- No --> D[Raise KeyError("The start note '%s' is not a valid note")]
    C -- Yes --> E[notes_in_key = keys.get_notes(key)]
    E --> F{keys.get_notes raises NoteFormatError?}
    F -- Yes --> G[NoteFormatError propagates to caller]
    F -- No --> H{Find index where n[0] == note[0] in notes_in_key}
    H -- No match --> I[UnboundLocalError when index is later used]
    H -- Match --> J[index assigned]
    J --> K[result_index = (index + 5) % 7]
    K --> L[return notes_in_key[result_index]]
    B --> M[IndexError if note is empty (note[0] access)]

## Examples:
1) Typical usage (happy path):
    try:
        n = sixth("E", "C")
        # n == "C"  (E -> C is a diatonic sixth in C major)
    except Exception as e:
        # handle or propagate error
        raise

2) Handling invalid starting note:
    try:
        sixth("H", "C")
    except KeyError as e:
        # "H" is not a valid note name; handle the invalid input
        print("Invalid note:", e)

3) Handling invalid key:
    try:
        sixth("C", "NotAKey")
    except Exception as e:
        # keys.get_notes will raise NoteFormatError which propagates
        print("Invalid key:", e)

Implementation note:
    - This function is intentionally minimal: it only reorders arguments to call the general interval routine with a fixed interval=5. Input validation and scale lookup are performed by the delegated interval implementation.

## `mingus.core.intervals.seventh` · *function*

## Summary:
Returns the diatonic seventh (the note six scale-steps above) of a given pitch within the context of a supplied key.

## Description:
Known callers:
- mingus.core.chords.seventh — uses this helper to compute the seventh degree when assembling a four-note seventh chord.
- Typical external uses: music-analysis or chord-building utilities that need the seventh scale degree relative to a given root within a specific key.

Why this is a separate function:
- Encapsulates the common operation "find the diatonic seventh above a note in a key" as a reusable helper. It delegates the diatonic interval arithmetic and key-aware spelling to the lower-level interval(...) helper so callers or higher-level chord builders do not duplicate that logic.

Behavior summary:
- This function delegates to interval(key, note, 6) and therefore inherits interval(...)'s semantics: it computes the note that lies 6 diatonic steps forward from the supplied note within the diatonic scale for the given key (wrapping modulo the 7-note scale). The returned note string is one of the seven note spellings produced by keys.get_notes(key).

## Args:
    note (str)
        - The starting pitch name (the note whose diatonic seventh is requested).
        - Must be a non-empty string accepted by mingus.core.notes.is_valid_note (examples: "C", "G#", "Bb").
        - Only the first character (base letter) of this string is used by the underlying implementation to locate the scale degree in the key; accidentals in this string are ignored for matching but do affect validation.
    key (str)
        - The musical key name used as the diatonic context (passed directly to keys.get_notes).
        - Examples: "C", "G", "F#", "Bb".
        - Must be a key string accepted by keys.get_notes; otherwise keys.get_notes will raise a NoteFormatError which propagates.

Interdependencies:
- note must satisfy notes.is_valid_note(note) (otherwise a KeyError is raised by interval).
- The base letter note[0] must appear among the base letters of the list returned by keys.get_notes(key); otherwise the underlying search may fail (UnboundLocalError).
- There is no default value for either parameter; both are required.

## Returns:
    str
    - A single note-name string representing the diatonic seventh of the input note within the specified key.
    - The value is exactly one of the seven strings returned by keys.get_notes(key) (spelled according to the key's signature, possibly containing '#' or 'b').
    - Example (typical): seventh("C", "C") -> "B" (in a conventional C major scale implementation).

## Raises:
    KeyError
        - If notes.is_valid_note(note) returns False. The underlying interval(...) raises this with the message: "The start note '%s' is not a valid note" % note.
    NoteFormatError
        - If keys.get_notes(key) rejects the supplied key string; this exception is raised by keys.get_notes and propagates unchanged.
    IndexError
        - If note is an empty string because the implementation accesses note[0].
    TypeError
        - If an unexpected non-integer-compatible type is used in the arithmetic inside interval(...) (not applicable for normal usage since interval(...) is called with a constant integer 6).
    UnboundLocalError
        - If the base letter of note does not appear in the list returned by keys.get_notes(key), the underlying implementation may leave an internal index variable unassigned and raise UnboundLocalError when trying to use it.

## Constraints:
Preconditions:
    - note must be a non-empty string and valid per notes.is_valid_note.
    - key must be a valid key name accepted by keys.get_notes.
    - The base letter note[0] should be present among the base letters of keys.get_notes(key).

Postconditions:
    - When no exception is raised, the returned string is one of the seven scale-degree note spellings provided by keys.get_notes(key).
    - No local or global state is modified by this function itself; only the underlying calls (keys.get_notes) may alter internal caches.

## Side Effects:
    - The function performs no I/O and does not mutate global variables directly.
    - It calls keys.get_notes(key), which may update or populate an internal key cache as a side effect of that function.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckNoteEmpty{Is note non-empty?}
    CheckNoteEmpty -- No --> RaiseIndexError[Raise IndexError]
    CheckNoteEmpty -- Yes --> ValidateNote{notes.is_valid_note(note)?}
    ValidateNote -- No --> RaiseKeyError[Raise KeyError("The start note '%s' is not a valid note")]
    ValidateNote -- Yes --> CallInterval[Call interval(key, note, 6)]
    CallInterval --> KeysError{keys.get_notes(key) valid?}
    KeysError -- No --> PropagateNoteFormatError[NoteFormatError propagates]
    KeysError -- Yes --> IntervalComputes[interval computes the 6-step diatonic advance]
    IntervalComputes --> PossibleTypeError{Type issues with arithmetic?}
    PossibleTypeError -- Yes --> PropagateTypeError[TypeError raised]
    PossibleTypeError -- No --> ReturnValue[Return the computed note string]

## Examples:
1) Typical usage in a diatonic context:
    - Input: note = "C", key = "C"
    - Expected output: "B"  (the major seventh degree in C major)

2) Used when building a seventh chord (as mingus.core.chords.seventh does):
    - triad = triad("C", "C")       # returns ['C', 'E', 'G']
    - seventh_note = seventh("C", "C")  # returns 'B'
    - result chord = ['C', 'E', 'G', 'B']

3) Handling invalid inputs:
    - If note is malformed (e.g., "H"), a KeyError is raised with the message "The start note 'H' is not a valid note".
    - If key is invalid (e.g., "NotAKey"), keys.get_notes will raise NoteFormatError which propagates.

Recommendations:
    - Validate note with notes.is_valid_note(note) and ensure note[0] is present in keys.get_notes(key) before calling to avoid UnboundLocalError.
    - For enharmonic-aware matching (if you need "D#" to match an "Eb" in the scale), perform explicit enharmonic comparison rather than relying on the simple base-letter match used by the underlying helper.

## `mingus.core.intervals.minor_unison` · *function*

## Summary:
Returns the diminished form of a pitch name by delegating to the notes handling utility; specifically, removes a trailing sharp or appends a flat.

## Description:
This thin helper produces the pitch name representing a "minor unison" relative to the input pitch by calling the shared note-transformation utility. It is a semantic wrapper that names the operation according to musical interval terminology while relying on the central notes module for string-level manipulation.

Known callers within the codebase:
- No internal callers were found in the scanned code graph. This function exists as a public helper in the intervals module and may be used by external code or higher-level interval logic.

Why this is a separate function:
- The function provides a clear, self-documenting API for the musical concept "minor unison" while centralizing actual string manipulation in notes.diminish. This separation keeps interval-level semantics separate from note-string operations and allows future changes to interval naming or behavior without modifying the notes module.

## Args:
    note (str): A non-empty pitch name string. Typical values include:
        - Natural notes: "C", "D", "E"
        - Sharps: "C#", "F#"
        - Flats: "Bb", "Eb"
    Notes on allowed values and interdependencies:
        - The function accepts any non-empty string; semantics are defined by the last character:
            * If the last character is '#', the sharp is removed.
            * Otherwise, a lowercase 'b' character is appended (which may create double or triple flats if repeated).
        - The function does not validate musical correctness beyond this string-level rule.

## Returns:
    str: The diminished pitch name.
    - If input ends with '#': returns the input with the final '#' removed (e.g., "C#" -> "C").
    - If input does not end with '#': returns the input with 'b' appended (e.g., "C" -> "Cb", "Bb" -> "Bbb").
    - The return is always a new string; no in-place mutation occurs.

## Raises:
    IndexError: If note is an empty string (note == ""), because the implementation accesses note[-1].
    TypeError: If note is not subscriptable (e.g., None or an integer), the underlying code will raise a TypeError or other subtype when attempting note[-1]. The function does not explicitly raise these; they come from the called utility.

## Constraints:
    Preconditions:
        - note must be a non-empty str-like (subscriptable) object.
    Postconditions:
        - The returned string equals notes.diminish(note), i.e.:
            * If note[-1] == '#', return == note[:-1]
            * Else return == note + 'b'

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and makes no external calls other than to the notes module.

## Control Flow:
flowchart TD
    Start --> CheckEmpty
    CheckEmpty{note is non-empty?}
    CheckEmpty -- No --> ErrorEmpty[Raise IndexError]
    CheckEmpty -- Yes --> EndsWithSharp{note[-1] == '#'?}
    EndsWithSharp -- Yes --> RemoveSharp[return note without final '#']
    EndsWithSharp -- No --> AppendFlat[return note + 'b']
    RemoveSharp --> End
    AppendFlat --> End
    ErrorEmpty --> End

## Examples:
    # Typical uses
    minor_unison("C")   -> "Cb"
    minor_unison("C#")  -> "C"
    minor_unison("Bb")  -> "Bbb"   # repeated flat characters are produced by design

    # Error handling
    try:
        minor_unison("")   # empty string
    except IndexError:
        # caller should ensure note is non-empty before calling
        pass

    # Defensive usage
    def safe_minor_unison(note):
        if not isinstance(note, str) or note == "":
            raise ValueError("note must be a non-empty string")
        return minor_unison(note)

## `mingus.core.intervals.major_unison` · *function*

## Summary:
Returns its input unchanged to represent applying a major unison interval (an interval of zero semitones) to a note.

## Description:
This function implements the semantic operation "major unison" by returning the supplied note unchanged. It exists as a named, separate operation so interval-processing code can call a clearly named function for the major unison case instead of special-casing or inlining an identity operation.

Known callers within the provided repository snapshot:
- No direct internal callers were found in the scanned code snapshot for this function. In typical usage within an interval/scale library, it would be invoked by interval-dispatch or mapping code when the requested interval is "major unison".

Why this logic is extracted:
- It enforces a clear responsibility boundary: each musical interval (including those that do nothing) is provided as a named function. This aids readability, discoverability, and consistency of the public API for interval transforms and makes it trivial to pass interval operations as first-class callables.

## Args:
    note (any): A representation of a musical note. Common representations in this codebase are:
        - str: note names such as 'C', 'C#', 'Db', 'G4', etc.
        - int: numeric pitch or MIDI-like integers, if the rest of the system uses numeric notes.
    Notes:
        - The function does not validate or coerce the input; it accepts any value and returns it unchanged.
        - There are no interdependencies with other parameters.

## Returns:
    any: The exact same object/value provided as the note argument.
    - If a string was passed, a string is returned with identical contents.
    - If an integer (or other object) was passed, the same integer/object is returned (identity/equivalence).
    - If None is passed, None is returned.

## Raises:
    This function does not raise exceptions on its own. Any exceptions will come from callers that assume specific types or further processing steps.

## Constraints:
    Preconditions:
        - Caller should provide a valid note representation expected by downstream code. Although this function will accept any value, subsequent consumers may require specific formats.
    Postconditions:
        - The output equals the input (value equality). No mutation or transformation is performed by this function.

## Side Effects:
    - None. The function performs no I/O and mutates no state or external resources.

## Control Flow:
flowchart TD
    Start --> CheckInput[Receive note argument]
    CheckInput --> ReturnSame[Return the input unchanged]
    ReturnSame --> End

## Examples:
- Semantic example: In an interval mapping that applies a callable for each interval, selecting the major-unison callable will leave notes unchanged — e.g., providing "C" as the input results in "C" as output.
- Defensive example: Passing None through the major-unison callable yields None; ensure callers validate note formats if required by later processing.

## `mingus.core.intervals.augmented_unison` · *function*

## Summary:
Returns the augmented form of a single note by delegating to the notes.augment helper; typically this raises the pitch by a semitone (adds a sharp) or removes a trailing flat.

## Description:
This function is a thin wrapper that forwards its input to the notes.augment implementation. It exists to provide a clear, musically-named API for producing an "augmented unison" (the interval that raises a unison by one semitone) within the intervals module.

Known callers within the codebase:
    - No other functions or modules reference this function in the currently available code graph. It is provided as a public helper for callers that want a semantic name for augmenting a unison.

Why this logic is extracted into its own function:
    - It gives a semantic, interval-oriented name (augmented_unison) to the operation of augmenting a single pitch.
    - It separates the interval-level API (intervals.*) from the note-level implementation (notes.*), allowing callers to use interval terminology without depending on notes.augment directly.

## Args:
    note (str): A note name string to be augmented.
        - Expected forms (common): "C", "D#", "Eb", "G", "A#", "Bb", etc.
        - The function does not parse or validate octave annotations; if the note includes octave digits or other trailing characters (e.g., "C-4"), those characters are considered part of the note and will affect behavior.
        - Empty string is not a valid input and will raise an IndexError (see Raises).

## Returns:
    str: The augmented note string produced by notes.augment.
    - If the last character of the input is "b" (flat), the function returns the input with that trailing "b" removed (e.g., "Db" -> "D").
    - Otherwise, the function appends a "#" (sharp) to the input (e.g., "C" -> "C#", "E#" -> "E##").
    - No normalization is performed beyond this text-based transformation; the function does not map double-sharps, adjust enharmonic equivalents, or modify octave numbers.

## Raises:
    IndexError: If note is an empty string, the underlying code accesses note[-1] and will raise IndexError.
    (No other exceptions are raised by this function itself.)

## Constraints:
    Preconditions:
        - Caller must provide a non-empty string for note.
        - The function assumes the last character of the string is meaningful for deciding whether the note is flat ("b") — inputs should follow the note-name conventions used by the rest of the project for expected results.
    Postconditions:
        - The returned string will be exactly either input + "#" or input with trailing "b" removed.
        - No other state is modified.

## Side Effects:
    - None. This function performs no I/O and mutates no external state. It simply returns a new string.

## Control Flow:
flowchart TD
    Start([Start])
    Input[/Receive note (string)/]
    CheckLastChar{Is last character == "b"?}
    CheckLastChar -- Yes --> Remove["Return note without trailing 'b' (note[:-1])"]
    CheckLastChar -- No --> Append["Return note with appended '#'(note + '#')"]
    Start --> Input --> CheckLastChar

## Examples:
- Augment a natural note:
    Input: "C"
    Output: "C#"

- Remove a flat:
    Input: "Db"
    Output: "D"

- Handle an already sharped note (textual append):
    Input: "E#"
    Output: "E##"

- Notes with octave annotations are treated literally:
    Input: "C-4"
    Output: "C-4#"

- Error case:
    Input: ""
    Behavior: Raises IndexError due to access of note[-1]; callers should validate non-empty input before calling or handle IndexError.

Use-case example with error handling:
    try:
        result = augmented_unison(note)
    except IndexError:
        # handle invalid empty input
        raise ValueError("note must be a non-empty string") from None

## `mingus.core.intervals.minor_second` · *function*

## Summary:
Return the spelled minor second (one semitone above) of a given pitch, expressed as a base letter plus accidentals.

## Description:
- Known callers:
    - No direct callers were identified in the inspected snapshot. Conceptually this function is used by higher-level interval, transposition, chord-construction, or spelling routines that need the minor-second above a given pitch as a correctly spelled note name.
- Purpose and rationale:
    - This routine encapsulates the common musical operation "find the minor second above a given pitch" while preserving diatonic letter relationships. It first selects the diatonic second (the next letter name) relative to the pitch's base letter (using the helper second with key "C" to obtain the next letter), then delegates to augment_or_diminish_until_the_interval_is_right to adjust accidentals so that the ascending semitone distance from the original pitch equals 1. Factoring this into a dedicated function keeps callers concise and ensures consistent spelled output (letter + accidentals) for the one-semitone interval.

## Args:
    note (str):
        - A pitch string representing the reference (lower) pitch.
        - Required format: non-empty string whose first character is a letter A-G (the function uses note[0] as the base letter). The remainder may include accidentals ('#' or 'b') and optionally octave digits — only the base letter and accidentals are meaningfully used by the underlying helpers.
        - Example valid values: "C", "C#", "Db", "G3", "F##".
        - Interdependency: the base letter (note[0]) is passed to the helper that computes the diatonic second; the full original note string is used as the reference when adjusting the target spelling.

## Returns:
    str:
        - A spelled pitch (base letter followed by zero or more '#' or 'b' accidentals) representing the pitch that is one ascending semitone above the supplied note.
        - The returned string does not include octave digits — it is a pitch-class spelling (e.g., "Db", "C", "F").
        - Possible results include naturals or accidentaled spellings depending on the input (examples below).
        - The return value is normalized by the called helper: accidentals are expressed as repeated '#' or 'b' characters and excessive accumulations are normalized according to the helper's rules.

## Raises:
    - IndexError:
        - If note is an empty string (the function accesses note[0]).
    - Any exception raised by the helper functions may propagate unchanged, including:
        - KeyError or NoteFormatError originating from validation in the underlying interval/notes utilities when an invalid note format or unknown key is encountered.
        - TypeError or ValueError if underlying helpers receive unexpected types or values.
    - Note: minor_second itself performs no validation and relies on the called helpers for error reporting.

## Constraints:
- Preconditions:
    - note must be a non-empty string whose first character is a letter A-G.
    - The full note string should be acceptable to the notes/measure utilities used by augment_or_diminish_until_the_interval_is_right (valid accidentals and overall note format).
- Postconditions:
    - On successful return, measure(original_note, returned_spelling) == 1 (i.e., the ascending semitone distance from the original note to the returned pitch-class is exactly one semitone).
    - The returned value is a canonical spelled pitch-class (letter + accidentals) suitable for use in interval naming and notation routines.

## Side Effects:
    - None performed directly by this function. It only calls pure helpers; any side effects would originate from those helpers (for example, if keys.get_notes populates an internal cache).

## Control Flow:
flowchart TD
    Start[Start: minor_second(note) called] --> CheckEmpty{note is non-empty?}
    CheckEmpty -- No --> RaiseIndexError[IndexError raised]
    CheckEmpty -- Yes --> ComputeBase[base_letter = note[0]]
    ComputeBase --> CallSecond[sec = second(base_letter, "C")]
    CallSecond --> CallAdjust[return augment_or_diminish_until_the_interval_is_right(note, sec, 1)]
    CallAdjust --> Result[Return spelled minor second]
    CallSecond -->|second may raise| Propagate1[Propagate exceptions from second]
    CallAdjust -->|augment_or_diminish... may raise| Propagate2[Propagate exceptions from augment_or_diminish_until_the_interval_is_right]

## Examples:
1) Basic usage:
    - Input: "C"
    - Behavior: second('C', 'C') -> "D"; adjust "D" down one semitone -> "Db"
    - Returned: "Db"

2) Natural-to-natural minor second (single semitone already):
    - Input: "E"
    - Behavior: second('E', 'C') -> "F"; measure("E","F") == 1, no adjustment
    - Returned: "F"

3) Wrapping diatonic letter (B -> C):
    - Input: "B"
    - Behavior: second('B', 'C') -> "C"; measure("B","C") == 1, no adjustment
    - Returned: "C"

4) Input with accidental:
    - Input: "C#"
    - Behavior: second('C', 'C') -> "D"; measure("C#","D") == 1
    - Returned: "D"

5) Error handling (empty input):
    - Calling minor_second("") raises IndexError because the function accesses note[0].

Implementation note:
- This function intentionally performs minimal logic and delegates:
    1) Choosing the target diatonic letter (by calling second with the base letter and key "C").
    2) Adjusting the chosen letter's accidentals to reach an exact one-semitone distance (by calling augment_or_diminish_until_the_interval_is_right).
- Callers that need an octave-aware result should combine this spelled pitch-class with octave information separately.

## `mingus.core.intervals.major_second` · *function*

## Summary:
Returns a spelled pitch name that is a major second (ascending two semitones) above the given note, choosing accidentals so the spelled note preserves the diatonic letter relationship implied by the input.

## Description:
This function computes the spelled pitch class one major second above the provided starting note by composing two smaller routines:
1. It first determines the diatonic "second" letter for the base letter of the input note by calling the diatonic helper with the key of C. Concretely it calls second(note[0], "C") to obtain the target base-letter (e.g., for input "E" this yields "F").
2. It then calls augment_or_diminish_until_the_interval_is_right(original_note, target_letter, 2) which adjusts the accidentals on the target letter until its ascending semitone distance from the original note equals 2.

Known callers:
- No direct callers were found in the inspected snapshot. Typical call sites conceptually include interval construction utilities, chord/voice-leading routines, or melodic step generators that need a correctly spelled major-second above a pitch.

Why this is a standalone function:
- Major seconds are a common musical interval. This function encapsulates the policy "use the diatonic second's letter, then adjust accidentals to obtain exactly two semitones" so callers need not replicate the two-step pattern (determine diatonic letter + normalize accidentals to match a semitone distance). It keeps higher-level code concise and prevents duplicated spelling logic.

## Args:
    note (str):
        - A pitch name string used as the reference start pitch.
        - Format: first character must be a letter A-G (the base note); it may optionally include accidentals ('#' or 'b') and/or trailing octave digits or other trailing tokens depending on callers, but this function only relies on the first character and the full string is forwarded where needed.
        - Required: non-empty string. If empty, an IndexError will occur because the function accesses note[0].
        - Note interdependency: the function extracts note[0] (the base letter) and passes that single-character string to second(...). Therefore the correctness of second(...) depends on that single-character being a valid note-letter.

## Returns:
    str:
        - A normalized spelled pitch class (base letter plus zero or more accidentals) representing a pitch whose ascending semitone distance from the input note equals 2.
        - The returned string contains only the base-letter and accidentals (no octave digits).
        - Examples:
            * major_second("C") -> "D"
            * major_second("E") -> "F#"
            * major_second("Bb") -> "C"
            * major_second("B") -> "C#"

## Raises:
    - IndexError:
        - If note is an empty string (note[0] access).
    - Any exception propagated from second(note[0], "C") or augment_or_diminish_until_the_interval_is_right(note, sec, 2). Examples include:
        - KeyError: if the single-character base letter passed to second is not a recognized note letter.
        - NoteFormatError / ValueError: if underlying note parsing routines reject inputs.
        - TypeError: if incorrect types are passed.
    - Note: augment_or_diminish_until_the_interval_is_right expects an integer interval in the 0..11 range to guarantee termination; this function always passes 2 so the non-termination risk for arbitrary intervals does not apply here.

## Constraints:
Preconditions:
    - note must be a non-empty string whose first character is a valid base note letter (A-G).
    - Because the function forwards note[0] to second(...), callers should ensure note[0] is a valid note letter; otherwise underlying routines will raise.
Postconditions:
    - On successful return, measure(original_note, returned_string) == 2 (the returned spelled pitch class is exactly two semitones above the input, measured ascending within one octave).
    - The returned value is normalized to a base letter with accidentals only (no octave information).

## Side Effects:
    - The function performs no I/O and mutates no global state itself.
    - Side effects may occur inside the helper routines it calls (e.g., keys.get_notes may populate a cache). Any such side effects originate from those helpers, not from this function.

## Control Flow:
flowchart TD
    A[Start: major_second(note) called] --> B{note is non-empty?}
    B -- No --> C[IndexError from note[0] access]
    B -- Yes --> D[sec = second(note[0], "C")]
    D --> E{second(...) raises?}
    E -- Yes --> F[Propagate exception to caller]
    E -- No --> G[result = augment_or_diminish_until_the_interval_is_right(note, sec, 2)]
    G --> H{augment... raises?}
    H -- Yes --> I[Propagate exception to caller]
    H -- No --> J[Return result]

## Examples:
1) Basic usage:
    try:
        print(major_second("C"))   # -> "D"
    except Exception as exc:
        # Handle malformed input or upstream errors
        raise

2) When accidentals are required:
    # E to a major second -> F#
    try:
        print(major_second("E"))   # -> "F#"
    except Exception:
        raise

3) Input with accidental preserved in interpretation:
    # Bb to major second -> C (Bb -> C is two semitones)
    try:
        print(major_second("Bb"))  # -> "C"
    except Exception:
        raise

4) Error handling for empty input:
    try:
        major_second("")           # raises IndexError
    except IndexError:
        # validate inputs before calling
        handle_empty_input()

## `mingus.core.intervals.minor_third` · *function*

## Summary:
Return the spelled pitch (letter plus accidentals) that lies a minor third (three semitones) above the given input note.

## Description:
This function computes a musically-correct, spelled minor third above the provided note by:
1) determining the diatonic third (two diatonic scale steps) above the input note's base letter within C major (using only the input note's first character), and
2) altering that spelled third by augmenting or diminishing its accidentals until its ascending semitone distance from the original note equals 3.

Known callers:
- No direct callers were discovered in the inspected codebase snapshot.
- Typical caller contexts (where this helper is useful):
    - Chord construction (finding the 3rd of a chord spelled as a minor third).
    - Melody/harmony generation and voice-leading utilities that need a correctly spelled minor third above a given pitch.
    - Music-analysis routines that query interval names or examine intervallic relationships.

Why this is a separate function:
- Encapsulates the specific musical operation "minor third above a given spelled pitch" so callers need not combine diatonic-interval lookup and accidentals-adjustment themselves.
- Keeps higher-level code (chord builders, interval name utilities) concise and declarative.
- Reuses the library's canonical diatonic and accidentals-normalization logic to ensure consistent spelling rules.

## Args:
    note (str)
        - A pitch name string whose first character is used as the reference base letter (examples: "C", "E", "F#", "Bb", "C4").
        - Requirements:
            * Must be a non-empty string (the implementation reads note[0]; empty string causes IndexError).
            * The first character should be a valid note letter accepted by the library (A-G). If it is not, the underlying diatonic routine will raise KeyError.
        - Interdependencies:
            * Only the first character is passed to the diatonic third helper; any accidentals or octave digits in the input are used by the subsequent measurement step (augment/diminish routines) but do not affect which diatonic base letter is selected.

## Returns:
    str
    - A spelled pitch consisting of a base letter (A-G) followed by zero or more accidentals ('#' or 'b') representing the note that is an ascending minor third (3 semitones) above the input.
    - Characteristics of the return value:
        * Uses the library's normalized accidentals representation (letter + accidentals only; no octave digits).
        * The returned note is selected and spelled so that measure(input_note, returned_note) == 3.
        * Examples:
            - minor_third("C") -> "Eb"
            - minor_third("E") -> "G"
            - minor_third("C#") -> "E"  (C# to E is 3 semitones)
            - minor_third("G") -> "Bb"

## Raises:
    IndexError
        - If the provided note is an empty string (accessing note[0] triggers IndexError).
    KeyError
        - If the first character of note is not a recognized note letter according to the library's validation; this originates from the diatonic-third helper and is propagated.
    NoteFormatError or ValueError (propagated)
        - If the augment/diminish measurement routines or notes converters reject the input format; these originate from lower-level notes/measuring functions and are propagated.
    TypeError
        - If incorrect types are passed (non-string) and lower-level routines fail; propagated.

    Implementation note:
        - The function itself does not introduce new exception types; it propagates exceptions raised by third(...) and augment_or_diminish_until_the_interval_is_right(...).

## Constraints:
Preconditions:
    - note must be a non-empty string whose first character is a valid note letter (A-G).
    - For robust behavior, pass typical note strings recognized by the library (optionally with accidentals and/or octave digits).

Postconditions:
    - On success, the returned string is a letter-plus-accidentals pitch whose ascending semitone distance from the input equals 3.
    - No global state is mutated by this function.

## Side Effects:
    - None local to this function: no file, network, or stdout I/O.
    - Any side effects originate from the called helpers (for example, keys.get_notes used by the diatonic helper may update an internal cache); this function itself performs pure string operations and library calls and returns the resulting spelled note.

## Control Flow:
flowchart TD
    Start[Start: minor_third(note)] --> CheckNonEmpty{note non-empty?}
    CheckNonEmpty -- No --> RaiseIndex[Raise IndexError] --> End
    CheckNonEmpty -- Yes --> ExtractBase[base = note[0]]
    ExtractBase --> CallThird[Call third(base, "C") -> trd]
    CallThird --> ThirdErrors{third raised KeyError/NoteFormatError?}
    ThirdErrors -- Yes --> PropagateThirdError[Propagate error] --> End
    ThirdErrors -- No --> CallAdjust[Call augment_or_diminish_until_the_interval_is_right(note, trd, 3)]
    CallAdjust --> AdjustErrors{augment_or_diminish... raised?}
    AdjustErrors -- Yes --> PropagateAdjustError[Propagate error] --> End
    AdjustErrors -- No --> ReturnResult[Return adjusted spelled note] --> End

## Examples:
1) Standard usage — lowering a major third to a minor third:
    Input: "C"
    Flow:
        - base = 'C'
        - third('C', 'C') -> "E"
        - adjust "E" against "C" until semitone distance is 3 -> "Eb"
    Output: "Eb"

2) Input already a minor third above:
    Input: "E"
    Flow:
        - base = 'E'
        - third('E', 'C') -> "G"
        - measure("E","G") == 3 so no adjustment required
    Output: "G"

3) Input with accidental:
    Input: "C#"
    Flow:
        - base = 'C'
        - third('C', 'C') -> "E"
        - measure("C#","E") == 3 -> no adjustment required
    Output: "E"

4) Error handling — empty input:
    Input: ""
    Outcome: IndexError is raised due to accessing note[0]; caller should validate input before calling.

Usage recommendations:
    - Validate the input string is non-empty and starts with a legal note letter (A-G) to avoid common runtime errors.
    - The function is intended to return spelled pitch classes only (no octave). If you need octave information preserved, combine this result with octave-handling logic at the call site.

## `mingus.core.intervals.major_third` · *function*

## Summary:
Return the spelled pitch name that is a major third (4 semitones) above the given pitch, using the diatonic letter-step relationship derived from the C major scale and then adjusting accidentals until the ascending semitone distance equals four.

## Description:
- What it does and why it exists:
    - This function computes a musically sensible "major third" above an input pitch by:
        1) choosing the diatonic third (two scale steps) above the input pitch's letter within the C major scale (via a call to the diatonic helper),
        2) then augmenting or diminishing that spelled pitch's accidentals until the ascending semitone distance from the original pitch equals 4 semitones (a major third).
    - Responsibility boundary: it only decides the diatonic letter relationship using the C major key and then enforces the 4-semitone distance by adjusting accidentals. It does not attempt to select an alternate diatonic letter (e.g., it will not choose a different letter to get the same semitone distance); that decision is fixed by the diatonic third in C major.

- Known callers in the codebase / typical call contexts:
    - No explicit callers were found in the inspected snapshot.
    - Typical usage contexts:
        - Chord construction and spelling (to compute the 3rd of a chord tone with a major quality).
        - Melody/harmony generation when a major-third relationship is required relative to a spelled pitch.
        - Music-analysis tools that need to express intervals as spelled note names rather than raw semitone offsets.

- Why this logic is factored out:
    - Encapsulates the two-step intent (select diatonic third by letter, then adjust accidentals to match the semitone distance) so callers can request a "major third spelled correctly" without reimplementing the diatonic/accidental loop.

## Args:
    note (str)
        - The reference pitch (e.g., "C", "E", "Bb", "G#", "Fb", "C#4"). The function uses:
            * note[0] (the first character) to determine the base letter passed to the diatonic third helper,
            * the full string as the reference pitch for semitone measurement.
        - Requirements:
            * Must be a non-empty string (otherwise accessing note[0] raises IndexError).
            * Must be a valid pitch format for the underlying notes.measure / notes.note_to_int routines (invalid formats can cause ValueError/NoteFormatError to propagate).
        - Interdependencies:
            * note[0] must be a letter A-G that the diatonic helper can interpret; otherwise the diatonic helper may raise KeyError or UnboundLocalError.

## Returns:
    str
    - A spelled pitch (base letter plus zero or more accidentals, e.g., "E", "G#", "Eb") representing the pitch class that is a major third (4 semitones ascending) above the provided reference pitch.
    - Characteristics of the return value:
        * Uses the base letter chosen by computing the diatonic third in C major (third(note[0], "C")).
        * Accidentals are adjusted (augmented/diminished) so that measure(original_note, returned_note) == 4.
        * The returned string contains only the base letter and accidentals (no octave digits are guaranteed).
    - Example returns:
        * major_third("C") -> "E"
        * major_third("E") -> "G#"
        * major_third("Eb") -> "G"
        * major_third("Bb") -> "D"

## Raises:
- IndexError
    - Condition: note is an empty string (accessing note[0] causes IndexError) or the underlying helpers access empty strings.
- KeyError
    - Condition: The diatonic helper third() rejects the base letter passed (third validates notes and may raise KeyError if the start note is not considered valid).
- NoteFormatError (or other value/format exceptions from keys/notes)
    - Condition: keys.get_notes or notes.note_to_int (called by the helpers) encounter an unrecognized key or malformed note string; these exceptions propagate.
- UnboundLocalError
    - Condition: If the diatonic helper fails to find a matching base letter within the key's scale (rare for canonical notes), the underlying code path may leave an index variable unassigned and raise UnboundLocalError.
- Other propagated exceptions
    - TypeError, ValueError, or other exceptions raised by lower-level measure/notes utilities will propagate unchanged.

## Constraints:
- Preconditions:
    - note must be non-empty.
    - note must be a string in a format accepted by the library's notes utilities (so measure and note parsing succeed).
    - note[0] must be a letter A-G suitable for computing the diatonic third within the C major scale.
- Postconditions:
    - On normal return, the returned string is a base-letter-with-accidentals pitch class whose ascending semitone distance from the input note equals 4 (measure(note, returned) == 4).
    - The function does not modify global state or perform I/O.

## Side Effects:
- None performed directly by this function.
- Indirect side effects may occur via called helpers:
    - keys.get_notes (invoked inside third) may update an internal cache.
    - All other operations are pure transformations and will not produce I/O or mutate global variables.

## Control Flow:
flowchart TD
    Start[Start: receive note]
    Start --> CheckEmpty{note is non-empty?}
    CheckEmpty -- No --> RaiseIndexError[IndexError raised] --> End
    CheckEmpty -- Yes --> ComputeBase[Compute base = note[0]]
    ComputeBase --> CallThird[Call third(base, "C") => trd]
    CallThird --> ThirdError{third raised exception?}
    ThirdError -- Yes --> Propagate[Propagate exception (KeyError/NoteFormatError/UnboundLocalError/...)] --> End
    ThirdError -- No --> CallAugDim[Call augment_or_diminish_until_the_interval_is_right(note, trd, 4)]
    CallAugDim --> AugDimError{augment_or_diminish raised exception?}
    AugDimError -- Yes --> Propagate2[Propagate exception (IndexError/TypeError/ValueError/...)] --> End
    AugDimError -- No --> ReturnResult[Return spelled_major_third] --> End

## Examples:
- Basic usage (happy path):
    - Input: note = "C"
    - Behavior: base letter 'C' -> diatonic third in C major is "E"; measure("C","E")==4 so no alteration -> returns "E"
    - Result: "E"

- Example with augmentation:
    - Input: note = "E"
    - Behavior: base letter 'E' -> diatonic third in C major is "G"; measure("E","G") == 3 (minor third) so "G" is augmented to "G#" to reach 4 semitones -> returns "G#"
    - Result: "G#"

- Example with flats preserved:
    - Input: note = "Eb"
    - Behavior: base letter 'E' -> diatonic third is "G"; measure("Eb","G") == 4 already -> returns "G"
    - Result: "G"

- Error handling example:
    - Calling major_third("") will raise IndexError; callers should validate non-empty input strings or handle the exception.

## `mingus.core.intervals.minor_fourth` · *function*

## Summary:
Return a spelled pitch-class (base letter plus accidentals) that is a diminished fourth above the given note — i.e., the diatonic fourth letter adjusted so the ascending semitone distance from the input equals 4.

## Description:
This function first determines the diatonic fourth letter above the input note's base letter using the C major diatonic spelling, then calls a helper to augment or diminish that spelled letter by accidentals until its ascending semitone distance from the original input equals 4 semitones. The result preserves the diatonic letter (from the fourth) and uses accidentals to meet the exact chromatic distance.

Known callers:
- No direct callers were detected in the inspected snapshot. Typical usages include:
  - Interval-naming or interval-construction routines that must produce a spelled diminished fourth (distinct from its enharmonic equivalent).
  - Chord- and voicing-construction helpers that keep diatonic letter relationships while achieving a specific semitone offset.
  - Transposition utilities that require spelled target notes at a specified chromatic distance.

Why this logic is factored out:
- Computing a spelled diminished fourth is a two-step operation: select the diatonic fourth letter, then iterate accidentals until the chromatic interval matches. Encapsulating this prevents duplication and ensures consistent spelled output across callers.

## Args:
    note (str)
        - The input pitch name. Must be a non-empty string whose first character is a letter A-G.
        - Common formats: "C", "G#", "Bb", "F##". Octave digits or other trailing characters may be present in caller code but are ignored by this function except for the first character and any accidentals used by downstream helpers.
        - Preconditions:
            * note must be at least one character long (the function accesses note[0]).
            * note should be parseable by the project's note/measure utilities to avoid propagated parsing errors.

## Returns:
    str
        - A normalized spelled pitch-class composed of a base letter (A-G) followed by zero or more accidentals ('#' or 'b').
        - The returned pitch is the diatonic fourth letter (computed with respect to C) adjusted by accidentals so that measuring the ascending semitone distance from the original note to the returned string yields exactly 4.
        - The result contains no octave digits.
        - Examples:
            * minor_fourth("C") -> "Fb"    (fourth of C is "F"; lowered to Fb gives an ascending distance of 4 semitones)
            * minor_fourth("E") -> "Ab"    (fourth of E is "A"; lowered to Ab -> 4 semitones)
            * minor_fourth("F#") -> "Bb"   (fourth of F is "B"; lowered to Bb -> 4 semitones)

## Raises:
    IndexError
        - If note is an empty string (accessing note[0] triggers IndexError).
    KeyError, ValueError, NoteFormatError
        - Any parsing/validation error originating from the underlying note/keys utilities (propagated).
    UnboundLocalError
        - Possible if fourth(note[0], "C") cannot find the base letter in the C major scale (indicates an unexpected base character).
    Any exception raised by augment_or_diminish_until_the_interval_is_right
        - The helper may raise IndexError, TypeError, ValueError, or other exceptions for invalid inputs; these propagate.

## Constraints:
Preconditions:
    - note must be non-empty and begin with a letter A-G.
    - The input should be parseable by the library's note/measure utilities to avoid downstream exceptions.
Postconditions:
    - The returned string is a base-letter-with-accidentals representation whose ascending semitone distance from the input equals 4.
    - The function itself does not perform I/O or mutate global state.

## Side Effects:
    - None local to this function. Any side effects would come from the called helpers; in typical implementations those are pure.

## Control Flow:
flowchart TD
    Start[Start: minor_fourth(note)]
    Start --> CheckEmpty{Is note non-empty?}
    CheckEmpty -- No --> RaiseIndexError[Raise IndexError (note[0] access)]
    CheckEmpty -- Yes --> ComputeFourth[frt = fourth(note[0], "C")]
    ComputeFourth --> FourthError{Did fourth raise?}
    FourthError -- Yes --> PropagateFourthErr[Propagate exception (KeyError/NoteFormatError/UnboundLocalError)]
    FourthError -- No --> CallAdjust[Call augment_or_diminish_until_the_interval_is_right(note, frt, 4)]
    CallAdjust --> AdjustError{Did adjust helper raise?}
    AdjustError -- Yes --> PropagateAdjustErr[Propagate helper exception (IndexError/TypeError/etc.)]
    AdjustError -- No --> ReturnResult[Return adjusted spelled note (base letter + accidentals)]
    ReturnResult --> End[End]

## Examples:
1) Standard use — diminished fourth above C
    try:
        result = minor_fourth("C")
        # result == "Fb"
    except Exception as exc:
        # Handle invalid input or lower-level parsing errors
        handle_error(exc)

2) With accidental input
    try:
        result = minor_fourth("F#")
        # result == "Bb"
    except Exception as exc:
        handle_error(exc)

3) Error example — empty input
    try:
        minor_fourth("")
    except IndexError:
        # Input validation required
        recover_from_empty_input()

## `mingus.core.intervals.major_fourth` · *function*

## Summary:
Return the correctly-spelled pitch name that is a perfect fourth (an ascending distance of 5 semitones) above the given note, choosing the letter name by stepping a diatonic fourth in the C major mapping and then adjusting accidentals until the semitone distance is exactly 5.

## Description:
Computes a spelled perfect fourth above the supplied pitch by:
1. Determining the diatonic fourth letter using the base letter of the input note inside the C major scale (calls the helper that computes a diatonic fourth from a single base letter in key "C").
2. Adjusting that letter's accidentals (augmenting or diminishing) until the ascending semitone distance from the original input note equals 5 semitones (perfect fourth), and returning a normalized letter+accidentals string.

Known callers:
- No direct callers were found in the inspected repository snapshot. Typical calling contexts include:
  - Interval-creation utilities that need a spelled fourth above a given pitch.
  - Chord- or voicing-building routines that construct quartal structures or compute interval spellings.
  - Transposition or music-theory utilities that must preserve diatonic letter relationships while fixing semitone distances.

Why this is factored out:
- The operation is small but conceptually two-step: pick the correct diatonic letter for a fourth, then tune accidentals so the pitch is exactly 5 semitones above the reference. Extracting it keeps callers concise and avoids repeating the pattern of selecting a diatonic target then iteratively augmenting/diminishing accidentals.

## Args:
    note (str):
        - A pitch string representing the reference note.
        - Format: first character is a letter A-G, optionally followed by accidentals ('#' or 'b') and possibly octave digits or other trailing characters. Only the letter and accidentals are relevant.
        - Examples: "C", "D#", "Bb", "F##", "G3" (octave ignored by this function).
        - Constraints:
            * Must be non-empty (the function accesses note[0]).
            * Should be a valid note according to the notes/measure utilities used by the underlying helpers; otherwise lower-level helpers will raise errors.

Interdependencies:
    - The function uses only the first character of note to choose the diatonic fourth letter (via fourth(note[0], "C")); the full note (including accidentals) is used when measuring semitone distance and when deciding which accidentals to apply to the target letter.

## Returns:
    str:
        - A normalized spelled pitch representing the perfect fourth above the input note.
        - The string contains the base letter followed by zero or more accidentals ('#' or 'b') and does not include octave numbers.
        - Examples:
            * major_fourth("C") -> "F"
            * major_fourth("C#") -> "F#"
            * major_fourth("E") -> "A"
            * major_fourth("Bb") -> "Eb"  (if Eb is the correct pitch class 5 semitones above Bb)
        - The returned spelling preserves the diatonic-letter relationship (the returned letter is a diatonic fourth above the input's base letter) and has accidentals chosen so the semitone distance equals 5.

## Raises:
    - IndexError:
        * If note is an empty string (note[0] access).
    - KeyError:
        * Propagated from the underlying fourth helper if the provided note is not recognized as a valid note (notes.is_valid_note check fails).
    - Any exceptions raised by the underlying helpers:
        * NoteFormatError, ValueError, TypeError, or other errors thrown by keys.get_notes, notes.note_to_int, measure, or the augment/diminish helpers will propagate unchanged.
    - UnboundLocalError:
        * In practice unlikely for valid A–G first characters because the C major scale contains all base letters; it can occur if the base character used to find the diatonic degree is not present in the scale returned by keys.get_notes("C").

## Constraints:
Preconditions:
    - note must be a non-empty string whose first character is a letter A–G.
    - note should be a format accepted by the notes/measure utilities (valid accidentals or naturals).
Postconditions:
    - The returned string is a letter + accidentals whose ascending semitone distance from the input note equals exactly 5 (a perfect fourth) as measured by the measure utility.
    - No global state or I/O is modified by this function itself; all work is delegated to pure helpers.

## Side Effects:
    - None performed directly. The function calls pure helpers (fourth and augment_or_diminish_until_the_interval_is_right) and does not perform I/O or mutate global state. Any side effects would originate from those helpers (which in typical implementations are side-effect free).

## Control Flow:
flowchart TD
    Start[Start: major_fourth(note)] --> CheckNoteNonEmpty{note non-empty?}
    CheckNoteNonEmpty -- No --> RaiseIndexError[Raise IndexError]
    CheckNoteNonEmpty -- Yes --> ComputeBase[base = note[0]]
    ComputeBase --> CallFourth[frt = fourth(base, "C")]
    CallFourth --> CallAdjust[res = augment_or_diminish_until_the_interval_is_right(note, frt, 5)]
    CallAdjust --> ReturnRes[Return res]

Notes:
    - The heavy-lifting loop that augments/diminishes accidentals until the semitone distance is 5 is inside augment_or_diminish_until_the_interval_is_right; major_fourth simply sequences the two helpers.

## Examples:
1) Basic usage:
    try:
        result = major_fourth("C")
        # result == "F"
    except Exception as e:
        # Handle invalid input or unexpected errors from helpers
        print("Error computing fourth:", e)

2) With accidental on the source:
    # Perfect fourth above C# is F#
    assert major_fourth("C#") == "F#"

3) With a flat on the source:
    # Perfect fourth above Bb is typically Eb (spelled as a fourth above B)
    result = major_fourth("Bb")
    # result == "Eb"

4) Error example — empty input:
    try:
        major_fourth("")
    except IndexError:
        # Input validation failed (empty string)
        handle_input_error()

## `mingus.core.intervals.perfect_fourth` · *function*

## Summary:
Returns the spelled pitch that is a perfect fourth above the provided note by delegating to the routine that computes a diatonically-correct major fourth and adjusts accidentals until the semitone distance equals five.

## Description:
- This function is a thin wrapper that forwards its single argument to the major_fourth helper and returns that result unchanged.
- Known callers:
    - No direct callers were found in the inspected repository snapshot.
    - Typical calling contexts include interval-construction utilities, chord/voicing builders that need a spelled fourth above a reference pitch, transposition helpers that must preserve diatonic letter relationships, and user-facing APIs that accept human-readable interval names (where callers may request a "perfect fourth" specifically).
- Why this logic is a separate function:
    - Provides a clear, semantically-named API entry for the musical interval "perfect fourth" while reusing the existing major_fourth implementation.
    - Keeps naming consistent and discoverable for API users who expect a perfect_fourth function, and centralizes documentation for the interval name without duplicating the implementation logic.

## Args:
    note (str):
        - Reference pitch as a string.
        - Expected format: a base letter A–G followed optionally by accidentals ('#' or 'b') and possibly trailing octave digits or other characters; only the base letter and accidentals are relevant.
        - Examples: "C", "D#", "Bb", "F##", "G3".
        - Constraints:
            * Must be a non-empty string (the implementation accesses note[0]).
            * The base letter should be A–G; otherwise underlying helpers may raise errors.
            * The string should be in a format acceptable to the shared notes/measure utilities used by major_fourth.

## Returns:
    str:
        - A spelled pitch (letter plus accidentals, no octave) representing the perfect fourth (ascending distance of 5 semitones) above the input note.
        - Possible return examples:
            * perfect_fourth("C") -> "F"
            * perfect_fourth("C#") -> "F#"
            * perfect_fourth("Bb") -> "Eb"
        - The returned string preserves the diatonic letter relationship (a fourth up) and contains accidentals chosen so the measured semitone distance is exactly 5.

## Raises:
    - IndexError:
        * If note is an empty string (attempt to access note[0]).
    - Any exception raised by major_fourth:
        * major_fourth performs the real computation; errors it raises (KeyError, ValueError, TypeError, NoteFormatError, etc.) are propagated unchanged.
    - In other rare malformed cases, errors from internal helpers used by major_fourth may propagate.

## Constraints:
- Preconditions:
    - Caller must supply a non-empty string whose first character is a letter A–G.
    - The note string should be valid according to the project's notes/measure utilities (valid accidentals/naturals).
- Postconditions:
    - On successful return, the output is a letter+accidentals string whose ascending semitone distance from the input equals exactly 5.
    - No global state is modified by this function itself; any side effects would come from the helpers it calls.

## Side Effects:
- This function performs no I/O and does not mutate global state directly. It simply delegates to major_fourth; any side effects would originate from that helper (which in typical implementations is pure).

## Control Flow:
flowchart TD
    Start[Start: perfect_fourth(note)] --> CheckNonEmpty{note non-empty?}
    CheckNonEmpty -- No --> RaiseIndexError[Raise IndexError]
    CheckNonEmpty -- Yes --> CallMajor[Call major_fourth(note)]
    CallMajor --> MajorReturns{major_fourth returns or raises}
    MajorReturns -- Raises --> PropagateError[Propagate exception to caller]
    MajorReturns -- Returns --> ReturnRes[Return spelled perfect fourth]

## Examples:
1) Basic usage:
    try:
        res = perfect_fourth("C")
        # res == "F"
    except Exception as e:
        # Handle invalid input or propagated helper errors
        print("Failed to compute perfect fourth:", e)

2) With accidentals:
    # Perfect fourth above C# is F#
    assert perfect_fourth("C#") == "F#"

3) Error example — empty input:
    try:
        perfect_fourth("")
    except IndexError:
        # Caller must provide a non-empty note string
        handle_input_error()

## `mingus.core.intervals.minor_fifth` · *function*

## Summary:
Return a spelled pitch (base letter plus accidentals) that is an ascending 6-semitone interval (tritone) above the provided note by selecting a diatonic fifth candidate and adjusting its accidentals until the semitone distance equals six.

## Description:
- Known callers within the inspected repository snapshot:
    - None found. This helper is intended for consumer code that needs a correctly spelled tritone relative to a given note (for chord construction, interval naming, or voice-leading).
- Typical external use cases:
    - Constructing a diminished fifth or tritone spelled relative to a root when building chords or analyzing harmony.
    - Producing a spelled pitch-class that is a fixed semitone distance from a reference while preserving diatonic letter relationships.
- Why this is a separate function:
    - It wraps two concerns into a single, reusable operation:
        1) Pick a diatonic candidate using only the input note's base letter (via fifth(note[0], "C")), and
        2) Repeatedly adjust that candidate's accidentals until the ascending semitone distance from the original input equals 6 (using augment_or_diminish_until_the_interval_is_right).
    - Factoring this out prevents callers from reimplementing the diatonic selection and the iterative augment/diminish search and centralizes expectation about the returned spelling.

## Args:
    note (str):
        - Description: The reference pitch name (root) used to compute the target minor fifth.
        - Requirements:
            * Must be a non-empty string; the implementation reads note[0].
            * First character must be a letter A-G.
            * May include accidentals following the letter ('#' or 'b'); octave digits or other suffixes are ignored by this function except as handled by called helpers.
        - Examples: "C", "E", "F#", "Bb", "G##".
        - Interdependencies: Only the base letter (note[0]) is used for choosing the diatonic fifth; accidentals on the input affect the semitone distance computation performed by the augmentation helper.

## Returns:
    str:
        - A normalized spelled pitch name (base letter A-G followed by zero or more '#' or 'b') representing a pitch-class whose ascending semitone distance from the input note equals 6.
        - The returned string contains no octave information.
        - Examples:
            * minor_fifth("C") -> "Gb"
            * minor_fifth("E") -> "Bb"
            * minor_fifth("C#") -> "G"
        - If the underlying helpers produce excessive accidentals, the returned form is subject to the normalization rules implemented by augment_or_diminish_until_the_interval_is_right.

## Raises:
- IndexError:
    - If note is an empty string (access to note[0]) or if called helpers index into empty strings.
- KeyError:
    - If the input note is not recognized as a valid note by the notes validation used by the underlying interval logic; this propagates from the lower-level validation.
- TypeError:
    - If arguments are of unsupported types for the called helpers (for example, passing non-string types) — augment_or_diminish_until_the_interval_is_right or the measure/notes functions it calls will raise TypeError which is propagated.
- NoteFormatError / ValueError (or similar) from keys/notes:
    - If keys.get_notes("C") or notes.note_to_int detect invalid formats, those exceptions propagate.
- Other exceptions:
    - Any exception raised by fifth(...) or augment_or_diminish_until_the_interval_is_right will propagate unchanged.

## Constraints:
- Preconditions:
    - note must be a non-empty string whose first character is A-G and whose format is acceptable to notes.note_to_int / measure used by the called helpers.
    - Because augment_or_diminish_until_the_interval_is_right expects a valid integer interval, this function always passes 6 (in-range), so non-termination due to an invalid interval does not apply here.
- Postconditions:
    - On success, the result is a base-letter-plus-accidentals string such that measure(note, result) == 6 (ascending semitone distance equals six).
    - No global state is modified by this function itself (aside from any caching done inside keys.get_notes).

## Side Effects:
- Direct: None (no I/O, network, or explicit global mutation).
- Indirect:
    - Calls to keys.get_notes (via fifth) may populate or update caches inside the keys module.
    - Any side effects from the notes/keys helpers (typically none) will be visible to callers.

## Control Flow:
flowchart TD
    Start --> ComputeBaseLetter[Compute base = note[0]]
    ComputeBaseLetter --> CallFifth[Call fifth(base, "C") -> fif_candidate]
    CallFifth --> CallAdjust[Call augment_or_diminish_until_the_interval_is_right(note, fif_candidate, 6)]
    CallAdjust --> ReturnResult[Return adjusted_note]
    CallFifth -->|fifth raises (invalid note/key)| PropagateError1[Propagate underlying exception]
    CallAdjust -->|augment_or_diminish raises (TypeError/ValueError/IndexError)| PropagateError2[Propagate underlying exception]

## Examples:
1) Typical usage:
    try:
        result = minor_fifth("C")
        # result == "Gb"
    except Exception as exc:
        # Handle or propagate; possible exceptions include IndexError, KeyError, TypeError, ValueError
        raise

2) With accidental on the input:
    try:
        result = minor_fifth("C#")
        # result == "G" because C# -> G is 6 semitones
    except Exception:
        raise

3) Invalid input example:
    try:
        result = minor_fifth("")   # empty string
    except IndexError:
        # Caller must ensure non-empty note strings
        handle_input_error()

## `mingus.core.intervals.major_fifth` · *function*

## Summary:
Return the spelled note (letter plus accidentals) that is a perfect fifth (7 semitones) above the given pitch, choosing an initial diatonic fifth from C major and then adjusting accidentals until the semitone distance equals a perfect fifth.

## Description:
- Known callers within the codebase:
    - No internal callers were found in the inspected snapshot. Typical external uses include:
        * Chord construction or analysis routines that need the perfect fifth spelled relative to a given pitch.
        * Interval/transposition helpers used by higher-level harmony or notation utilities.
        * User-facing API functions where callers request the common named interval "major fifth" above a pitch.
    - Typical usage context: called when a client needs the named, spelled perfect fifth above an input pitch (for display, chord spelling, or interval calculations) rather than just its enharmonic pitch-class.

- Why this is a separate function:
    - It encapsulates the two-step concern of: (1) choosing the diatonic fifth by letter (here using the C-major diatonic mapping) and (2) adjusting accidentals until the semitone distance equals a perfect fifth. This separation keeps callers from duplicating the pattern of picking a diatonic target and then iteratively augmenting/diminishing it to match a semitone interval.

## Args:
    note (str):
        - A non-empty pitch name string (examples: "C", "E", "F#", "Bb", "G##").
        - Format rules:
            * First character must be a letter A–G (this base letter is used to pick the diatonic fifth).
            * Subsequent characters may be accidentals ('#' or 'b'). Octave digits or extra suffixes are not used by this function and may be ignored by downstream helpers.
        - Precondition: note must be a valid note string accepted by the notes module (otherwise underlying helpers will raise).
        - The implementation reads note[0] (the base letter) to compute the initial diatonic fifth; passing an empty string will raise IndexError.

## Returns:
    str
    - A normalized spelled pitch representing the perfect fifth above the input pitch.
    - The returned string consists of the base note letter and zero or more accidentals ('#' or 'b'), e.g. "G", "C#", "Bb".
    - The return does NOT include octave numbers.
    - The returned spelling is chosen so that the ascending semitone distance from the input pitch to the returned pitch is exactly 7 (a perfect fifth), as measured by the measure() semantics used by the augment/diminish routine.
    - Examples:
        * major_fifth("C") -> "G"
        * major_fifth("E") -> "B"
        * major_fifth("F#") -> "C#"
        * major_fifth("Bb") -> "F"

## Raises:
    - IndexError:
        * If note is an empty string (the function accesses note[0]).
    - Any exceptions propagated from fifth(...) or augment_or_diminish_until_the_interval_is_right(...), e.g.:
        * KeyError when the start note is not a valid note according to the notes module.
        * Note/Key format errors raised by keys.get_notes when fifth(...) attempts to look up a key's diatonic notes.
        * TypeError or ValueError if underlying functions receive unsupported types or malformed inputs.
    - Note on failure modes: If the base letter note[0] is not present in the diatonic sequence that fifth(...) inspects (unexpected input), the underlying interval logic may raise an IndexError or an UnboundLocalError; these propagate unchanged.

## Constraints:
- Preconditions:
    - note must be non-empty and parseable as a pitch by the notes module (so notes.note_to_int / measure can process it when augmenting/diminishing).
    - The function assumes the base letter of note is one of A–G; otherwise the underlying fifth computation will fail.
- Postconditions:
    - On successful return, the returned string is a note letter plus accidentals whose ascending semitone distance from the input pitch is exactly 7 semitones.
    - No global state is modified by this function itself.

## Side Effects:
    - The function performs no I/O and does not mutate global state directly.
    - It calls into keys/notes helper functions which may read or populate internal caches in those modules; any such side effects originate from those modules.

## Control Flow:
flowchart TD
    Start[Start: major_fifth(note)]
    Start --> CheckEmpty{note non-empty?}
    CheckEmpty -- No --> RaiseIndexError[IndexError: note[0] access]
    CheckEmpty -- Yes --> ExtractBase[base = note[0]]
    ExtractBase --> CallFifth[call fifth(base, "C") -> initial_fif]
    CallFifth --> FifthError{fifth raises?}
    FifthError -- Yes --> PropagateError[Propagate exception]
    FifthError -- No --> CallAdjust[call augment_or_diminish_until_the_interval_is_right(note, initial_fif, 7)]
    CallAdjust --> AdjustError{adjust raises?}
    AdjustError -- Yes --> PropagateError
    AdjustError -- No --> ReturnResult[Return adjusted spelled note]
    ReturnResult --> End[End]

## Examples:
1) Typical usage (happy path):
    try:
        result = major_fifth("C")
        # result == "G"
    except Exception as exc:
        # handle errors from invalid input or underlying helpers
        raise

2) Example showing accidentals:
    try:
        result = major_fifth("F#")
        # result == "C#"
    except Exception:
        raise

3) Invalid input handling:
    try:
        major_fifth("")  # empty string
    except IndexError:
        # expected: input must be non-empty
        handle_input_error()

    try:
        major_fifth("H")  # invalid base letter
    except Exception as e:
        # underlying helpers will raise (KeyError/format error) for invalid note name
        handle_input_error()

## `mingus.core.intervals.perfect_fifth` · *function*

## Summary:
Returns the spelled note that is a perfect fifth above the given pitch by delegating directly to the underlying major_fifth implementation.

## Description:
- Role and behavior:
    - This function is a thin alias that immediately calls major_fifth(note) and returns its result. It performs no validation or transformation itself.
- Known callers within the codebase:
    - No internal callers were found in the inspected snapshot.
    - Typical external uses include chord construction, interval/transposition utilities, and user-facing API code that requests a "perfect fifth" by name.
- Why this is a separate, tiny function:
    - Provides an alternative/public-facing name for the same operation implemented by major_fifth and centralizes the call so callers can use either name without duplicating logic.

## Args:
    note (str):
        - A non-empty pitch name string (examples: "C", "E", "F#", "Bb", "G##").
        - Format expectations:
            * First character: A–G (used by the underlying interval logic).
            * Optional subsequent accidentals: '#' or 'b'.
        - Interdependency: This wrapper does not parse or validate the string — it relies on major_fifth and the notes/keys helpers to accept the value.

## Returns:
    str
    - The spelled pitch (letter plus zero or more accidentals) representing the perfect fifth above the input.
    - The returned value is exactly the value returned by major_fifth(note); this function does not alter or post-process that result.
    - Returned strings do not include octave information (e.g., "G", "C#", "Bb").

## Raises:
    - This function does not raise new exception types itself; any exception raised by major_fifth(note) is propagated to the caller.
    - Concrete examples of propagated exceptions (originating from major_fifth and its callees) include:
        * IndexError: if note is an empty string and major_fifth accesses note[0].
        * KeyError/ValueError/TypeError: if the note string is malformed or not recognized by the notes/keys helpers.

## Constraints:
- Preconditions:
    - Callers should supply a non-empty, parseable note string whose first character is a musical letter (A–G); otherwise underlying helpers may raise.
- Postconditions:
    - On success, the returned spelled note is at an ascending semitone distance of a perfect fifth (7 semitones) from the input, as determined by major_fifth.
    - No global state is modified by this wrapper itself.

## Side Effects:
    - The function performs no direct I/O and does not mutate global state.
    - Any side effects originate from major_fifth and the notes/keys modules it calls (e.g., internal caching within those modules).

## Control Flow:
flowchart TD
    Start[Start: perfect_fifth(note)]
    Start --> CallMajorFifth[Call major_fifth(note)]
    CallMajorFifth --> MajorFifthError{major_fifth raises?}
    MajorFifthError -- Yes --> PropagateError[Propagate exception to caller]
    MajorFifthError -- No --> ReturnResult[Return result from major_fifth]
    ReturnResult --> End[End]

## Examples:
1) Happy path:
    try:
        result = perfect_fifth("C")
        # result == "G"
    except Exception as exc:
        # Exceptions are from major_fifth / notes / keys; handle or re-raise
        raise

2) With accidentals:
    try:
        result = perfect_fifth("F#")
        # result == "C#"
    except Exception:
        raise

3) Invalid input handling (propagated):
    try:
        perfect_fifth("")  # empty string
    except IndexError:
        # Raised by underlying implementation; input must be non-empty
        handle_input_error()

## `mingus.core.intervals.minor_sixth` · *function*

## Summary:
Returns the spelled pitch name that is a minor sixth (8 semitones ascending) above the given note.

## Description:
Computes the diatonic sixth letter for the input note (using the C major diatonic context) and then adjusts that spelled pitch by adding or removing accidentals until its ascending semitone distance from the original note equals 8 (the semitone size of a minor sixth). The function is a thin composition of two lower-level helpers:
- It calls the diatonic helper to get the sixth letter (sixth) using the first character of the provided note and the fixed key "C".
- It then calls augment_or_diminish_until_the_interval_is_right to mutate that letter's accidentals until the interval equals 8 semitones and returns the normalized spelled pitch.

Known callers:
- No direct callers were discovered in the inspected snapshot. Typical callers would be higher-level music utilities that need a spelled minor sixth (for chord construction, interval labels, or melodic generation).

Why this logic is factored out:
- This function expresses the semantic operation "minor sixth above X" in a single, intention-revealing helper. It hides two implementation details from callers: (1) deriving the target diatonic letter (a sixth in C) and (2) iteratively augmenting/diminishing accidentals to reach exactly 8 semitones. Callers can therefore request a minor sixth without implementing diatonic-step lookup or accidental adjustment.

## Args:
    note (str):
        - The starting pitch name. Expected format: a non-empty string whose first character is a letter A-G.
        - Examples: "C", "E", "F#", "Bb", "G4", "E3" — octave digits are allowed but not required.
        - The function will use note[0] (the base letter) when computing the diatonic sixth and will pass the original note string as the reference pitch to the adjustment routine.
        - Interdependencies:
            * note must be non-empty (the function accesses note[0]).
            * The first character (note[0]) must be a valid base note letter recognized by the underlying sixth routine (A-G).
            * For predictable behavior, the entire note string should be acceptable to the notes/measure utilities (e.g., valid accidental characters); otherwise lower-level callers will raise.

## Returns:
    str:
        - A normalized spelled pitch name (base letter plus accidentals) representing the minor sixth above the input note.
        - The returned string contains only the letter A-G and accidentals ('#' or 'b'); it does not include octave digits.
        - Examples:
            * minor_sixth("C") -> "Ab"   (A diminished to Ab, producing 8 semitones above C)
            * minor_sixth("E") -> "C"    (E up to C is already 8 semitones)
            * minor_sixth("G#4") -> a spelled pitch like "E" or "E#" / "Eb" depending on spelling rules after adjustment

## Raises:
    IndexError:
        - If note is an empty string (accessing note[0] triggers IndexError).

    KeyError:
        - Propagated from sixth if the base letter or supplied arguments are not considered valid by the notes validation routines (for example, if note[0] is not an accepted note letter).

    NoteFormatError (or other errors from keys/notes utilities):
        - The underlying sixth and augment_or_diminish... functions call keys.get_notes and notes.note_to_int (via measure). If the provided note or internal lookups are malformed or specify an unknown key format, those functions may raise format-related errors which propagate through this function.

    Any other exceptions raised by the called helpers (e.g., TypeError, ValueError) are propagated unchanged.

## Constraints:
Preconditions:
    - note must be a non-empty string whose first character is a letter A-G.
    - The base letter (note[0]) should be recognized by the library's note/key utilities.
    - The internal interval value is fixed to 8, which lies within 0..11, ensuring the adjustment routine terminates under normal conditions.

Postconditions:
    - On success, the result is a spelled pitch (letter + accidentals) whose ascending semitone distance from the original note equals 8.
    - No global state or I/O is performed by this function itself.

## Side Effects:
    - None directly. The function calls keys.get_notes and notes-measure helpers which are pure in typical implementations; any side effects would originate from those functions (e.g., internal caching in keys.get_notes), not from minor_sixth.

## Control Flow:
flowchart TD
    Start[Start: minor_sixth(note) called]
    Start --> CheckEmpty{note non-empty?}
    CheckEmpty -- No --> RaiseIndexError[IndexError raised (note[0] access)]
    CheckEmpty -- Yes --> GetBase[base_letter = note[0]]
    GetBase --> CallSixth[sth = sixth(base_letter, "C")]
    CallSixth --> CallAdjust[res = augment_or_diminish_until_the_interval_is_right(note, sth, 8)]
    CallAdjust --> ReturnRes[Return res]
    CallSixth --> SixErr{sixth raised?}
    SixErr -- Yes --> PropagateSixErr[Propagate exception]
    CallAdjust --> AdjErr{augment/diminish raised?}
    AdjErr -- Yes --> PropagateAdjErr[Propagate exception]

## Examples:
1) Typical successful use:
    try:
        minor = minor_sixth("C")
        # minor == "Ab"
    except Exception as e:
        # handle or propagate
        raise

2) When the diatonic sixth already matches 8 semitones:
    # E up to C is an 8-semitone (minor sixth) interval
    minor_sixth("E")  # -> "C"

3) Invalid input (empty string):
    try:
        minor_sixth("")
    except IndexError:
        # caller must validate input before calling

4) Notes on invalid/odd spellings:
    - If the input contains an unexpected format or the library's note/key parsers reject the value, errors from those lower-level utilities will propagate. Validate inputs (e.g., using notes.is_valid_note or library key utilities) if you need to convert user input to a canonical form prior to calling minor_sixth.

## `mingus.core.intervals.major_sixth` · *function*

## Summary:
Return the spelled pitch class that is a major sixth above the given note (preserving diatonic letter relationship and choosing accidentals so the ascending semitone distance equals 9).

## Description:
Known callers:
    - No direct callers were discovered in the inspected code snapshot.
    - Typical call sites are higher-level music-theory utilities that compute named intervals, build chord extensions (adding major sixths), or produce spelled interval outputs for notation/transposition utilities.

Why this logic is extracted:
    - This function composes two distinct responsibilities — obtaining the diatonic sixth letter relationship and adjusting accidentals until the semitone distance equals that of a major sixth — into a single, intention-revealing helper. Extracting this keeps callers concise (they request a "major sixth" without reimplementing the diatonic lookup + accidental-adjustment loop) and centralizes the interval-defining constant (9 semitones) in one place.

## Args:
    note (str):
        - The reference pitch name (examples: "C", "E", "F#", "Bb", "Eb4").
        - Required. Must be a non-empty string whose first character is a letter A-G. The function uses:
            * note[0] (the base letter) when computing the diatonic sixth via sixth(...)
            * the full note string as the reference pitch1 passed to augment_or_diminish_until_the_interval_is_right(...)
        - Interdependencies:
            * note[0] must be acceptable to the diatonic lookup used by sixth (passing a single-letter like 'C','D', etc.).
            * note must be parseable by the lower-level measure/notes conversions used by augment_or_diminish_until_the_interval_is_right; otherwise those callees will raise.

## Returns:
    str:
        - A spelled pitch class string representing the major sixth above the input note.
        - Format: base letter (A-G) followed by zero or more accidentals ('#' or 'b'). No octave digits are returned.
        - The returned pitch class is chosen so that the ascending semitone distance from the input note to the returned pitch class equals 9 (the semitone span of a major sixth).
        - Examples:
            * major_sixth("C") -> "A"  (C up a major sixth -> A)
            * major_sixth("E") -> "C#" (E up a major sixth -> C#)
            * major_sixth("Bb") -> "G" (Bb up a major sixth -> G)

## Raises:
    IndexError:
        - If note is an empty string (code accesses note[0]).
    Any exception raised by sixth(...) or augment_or_diminish_until_the_interval_is_right(...):
        - sixth may raise KeyError or other exceptions if the base letter is not a valid note or if keys.get_notes rejects the provided key.
        - augment_or_diminish_until_the_interval_is_right can raise IndexError, TypeError, ValueError, or NoteFormatError originating from the lower-level notes/measure conversion functions.
    Notes:
        - Exceptions from the underlying helpers are propagated; this function performs no additional validation or exception translation.

## Constraints:
Preconditions:
    - note is a non-empty string and its first character is a letter A-G.
    - note must be parseable by the notes/measure utilities used by the downstream adjustment routine.
Postconditions:
    - On success, the returned string is a base-letter-plus-accidentals representation whose ascending semitone distance from the input note equals 9.
    - No global state or I/O side effects are performed by this function itself.

## Side Effects:
    - None intrinsic to this function (no I/O, no global mutations). Any side effects would come from the called helpers (for example, internal caching in keys.get_notes); those are not caused directly here.

## Control Flow:
flowchart TD
    Start[Start: major_sixth(note) called]
    Start --> CheckEmpty{note non-empty?}
    CheckEmpty -- No --> RaiseIndex[Raise IndexError (note[0] access)]
    CheckEmpty -- Yes --> ComputeBase[Compute base = note[0]]
    ComputeBase --> CallSixth[Call sixth(base, "C") => sth]
    CallSixth --> CallAdjust[Call augment_or_diminish_until_the_interval_is_right(note, sth, 9)]
    CallAdjust --> ReturnResult[Return adjusted spelled pitch class]
    CallSixth --> PropagateErrors1[Propagate exceptions from sixth]
    CallAdjust --> PropagateErrors2[Propagate exceptions from adjust routine]

## Examples:
1) Happy path:
    try:
        r = major_sixth("C")
        # r == "A"
    except Exception as e:
        # Handle unexpected input/format errors
        raise

2) Example showing accidental adjustment:
    try:
        r = major_sixth("E")
        # r == "C#"  (sixth('E','C') -> 'C' then adjusted up to 'C#' so measure("E","C#")==9)
    except Exception as e:
        raise

3) Error case — empty input:
    try:
        major_sixth("")
    except IndexError:
        # Caller should validate input before calling
        handle_input_error()

Implementation notes for callers:
    - This function hard-codes the diatonic step (sixth relative to a C diatonic lookup) and the semitone target (9). If you need other interval qualities (minor sixth = 8 semitones, augmented/diminished variants), use the appropriate lower-level helpers directly or adapt the interval constant.
    - If you must preserve octave numbers, reconstruct them separately; this function returns only the spelled pitch class (letter + accidentals).

## `mingus.core.intervals.minor_seventh` · *function*

## Summary:
Returns a spelled pitch name representing the minor seventh above the supplied note (i.e., the pitch class 10 semitones ascending from the input), with accidentals chosen so the result preserves the diatonic letter relationship implied by the input note.

## Description:
Known callers:
    - No direct callers were found in the provided snapshot. Typical callers include chord-building utilities, interval-naming or transposition routines, and music-analysis code that needs a correctly spelled minor seventh (for example, constructing a dominant seventh chord where the seventh is a minor seventh above the root).

Context and responsibility:
    - This small helper encapsulates the two-step process required to produce a properly spelled minor seventh:
        1) determine the diatonic seventh letter that corresponds to the input note's base letter (the function delegates that to a diatonic seventh helper),
        2) adjust that spelled letter by adding or removing accidentals until the ascending semitone distance from the original input to the spelled target equals 10 semitones (the numeric size of a minor seventh).
    - It is extracted as its own function because constructing a minor-seventh spelling is a distinct, frequently reused operation: callers should not need to know the details of diatonic-letter selection or the iterative augment/diminish adjustment loop.

## Args:
    note (str)
        - The reference pitch (root) from which the minor seventh is measured.
        - Required format: a non-empty string whose first character is a letter A-G. It may include accidentals (e.g., 'C', 'G#', 'Bb', 'F##'), but only the first character is used when selecting the diatonic seventh letter.
        - The function will access note[0]; passing an empty string will raise IndexError.
        - The string should be acceptable to lower-level note-parsing utilities (notes.note_to_int / measure) to avoid propagated parsing exceptions.

## Returns:
    str
        - A normalized pitch-class string representing the minor seventh above the input note.
        - Format: base letter (A-G) followed by zero or more accidentals ('#' or 'b'). The returned string does not include octave numbers or any other trailing tokens.
        - The returned pitch-class is computed such that measure(note, returned_value) == 10 (i.e., an ascending distance of 10 semitones).
        - Example results:
            * minor_seventh("C") -> "Bb"
            * minor_seventh("D") -> "C"
            * minor_seventh("F#") -> "E"

## Raises:
    IndexError
        - If note is an empty string (the implementation accesses note[0]).
    Any exception raised by the underlying helpers (propagated unchanged), including but not limited to:
        - KeyError: If lower-level validation considers the input invalid (e.g., notes.is_valid_note rejects the input).
        - NoteFormatError or ValueError: If keys.get_notes or notes parsing rejects a supplied key or note format during the helper calls.
        - TypeError: If passed unexpected non-string types or if numeric operations in the helpers receive incorrect types.
        - UnboundLocalError: Possible if the diatonic-letter lookup fails in the underlying helper (see the seventh helper notes).
    Implementation note: the function itself relies on the helper functions to perform validations and conversions; most domain-specific exceptions originate there and are intentionally propagated.

## Constraints:
Preconditions:
    - note must be a non-empty string whose first character is a letter A-G.
    - For robust behavior, note should be a format accepted by the project's notes utilities (avoid malformed characters).
    - No other parameters are accepted; the function uses a fixed numeric interval (10 semitones) internally.

Postconditions:
    - On successful return, the returned string is a pitch-class whose ascending semitone distance from the input note equals 10 (measure(input, result) == 10).
    - No global state or I/O is introduced by this function; any side effects originate from the helpers it calls (e.g., potential internal key-cache population in keys.get_notes).

## Side Effects:
    - None performed directly by this function (no file, network, or stdout I/O and no global mutation). 
    - The function calls helpers which may perform small internal cache updates (for example keys.get_notes) — those side effects are external to this function and are not part of its contract.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckEmpty{Is note non-empty?}
    CheckEmpty -- No --> RaiseIndexError[Raise IndexError]
    CheckEmpty -- Yes --> ComputeDiatonicSeventh[Call seventh(note[0], "C")]
    ComputeDiatonicSeventh --> SeventhOK{seventh succeeded?}
    SeventhOK -- No --> PropagateException[Propagate exception and return]
    SeventhOK -- Yes --> CallAdjust[Call augment_or_diminish_until_the_interval_is_right(note, sth, 10)]
    CallAdjust --> AdjustOK{adjustment succeeded?}
    AdjustOK -- No --> PropagateException2[Propagate exception and return]
    AdjustOK -- Yes --> ReturnResult[Return normalized spelled note string]
    ReturnResult --> End([End])

## Examples:
1) Typical: root C
    - Input: note = "C"
    - Explanation: seventh('C', 'C') -> "B" (diatonic seventh letter), then adjust "B" down to "Bb" so measure("C","Bb") == 10
    - Output: "Bb"

2) Natural result when no accidental change is required:
    - Input: note = "D"
    - Explanation: seventh('D', 'C') -> "C" and measure("D","C") already equals 10
    - Output: "C"

3) Input with accidental:
    - Input: note = "F#"
    - Explanation: base letter 'F' -> seventh('F','C') -> "E"; measure("F#","E") == 10 already
    - Output: "E"

4) Error handling example (empty input):
    try:
        minor_seventh("")
    except IndexError:
        # Caller should validate or surface the error appropriately
        handle_input_error()

Implementation hint for re-implementation:
    - Compute the diatonic seventh letter by calling the existing diatonic-seventh helper with the base letter of the input and an arbitrary consistent key context (the original implementation uses key "C" to obtain a canonical letter-based mapping).
    - Use an adjustment loop that calls low-level augment/diminish helpers until the ascending semitone distance (measured by measure) between the original input note and the candidate equals 10; then normalize accidentals and return the spelled pitch-class.

## `mingus.core.intervals.major_seventh` · *function*

## Summary:
Compute the spelled major seventh above a given root by selecting the diatonic seventh letter and then adjusting its accidentals until the ascending semitone distance from the root equals 11.

## Description:
Produces a normalized pitched-class string (base letter plus accidentals) representing the major seventh interval (11 semitones ascending) from the supplied root.

Known callers within the codebase:
    - mingus.core.chords.major_seventh — uses this helper when assembling a four-note major-seventh chord.
    - External callers are typical chord builders, harmony analysis tools, notation exporters, or any code that requires a correctly-spelled major-seventh above a root.

Reason for extraction:
    - Encapsulates two responsibilities:
        1) determine the diatonic seventh letter for the root's base letter (via seventh), and
        2) rely on augment_or_diminish_until_the_interval_is_right to mutate the spelled target until the ascending semitone distance equals 11.
    - Centralizing these steps avoids duplication and ensures consistent accidental-normalization behavior.

## Args:
    note (str)
        - The reference/root pitch name.
        - Requirements:
            * Non-empty string (the function reads note[0]).
            * First character must be a natural letter A–G; this base letter is passed to seventh to obtain a diatonic seventh letter.
            * The remainder may include accidentals ('#' or 'b') and optional octave digits; underlying helpers parse as needed.
        - Interdependencies:
            * The diatonic seventh (sth) returned by seventh(note[0], "C") is a pitch name string (a base letter possibly with accidentals) and is suitable as the second argument to augment_or_diminish_until_the_interval_is_right, which expects a pitch-name string in the same accepted format as note1.

## Returns:
    str
        - A normalized pitched-class string (base letter with zero or more '#' or 'b') representing the major seventh above the input note.
        - The returned string omits octave digits.
        - Examples:
            * major_seventh("C") -> "B"
            * major_seventh("C#") -> "B#"

## Raises:
    IndexError
        - If note is an empty string (accessing note[0]) or if an underlying helper reads an empty string.
        - augment_or_diminish_until_the_interval_is_right documents that it may raise IndexError for empty inputs; that exception will propagate here if triggered.

    TypeError
        - If inputs are of unsupported or unexpected types for the notes/measure utilities used by the helpers (propagated from called functions).

    ValueError or NoteFormatError
        - Propagated from notes parsing functions (for example, notes.note_to_int) used by the underlying helpers when a supplied string is not a recognized note format.

    KeyError
        - May be raised by seventh(note[0], "C") if the base letter is not recognized as a valid note letter by the validation routines used by seventh.

    UnboundLocalError (possible)
        - May propagate if an underlying helper's internal search fails to initialize an internal variable (documented as a possible failure mode in seventh).

Notes on propagation:
    - This function does not catch exceptions from the helpers; exceptions raised by seventh(...) and augment_or_diminish_until_the_interval_is_right(...) propagate unchanged to the caller.

## Constraints:
Preconditions:
    - note must be a non-empty string whose first character is in A–G.
    - note and the diatonic seventh produced by seventh(...) must be parseable by the notes/measure utilities used by augment_or_diminish_until_the_interval_is_right.

Postconditions:
    - On success, the returned string is a normalized pitched-class whose ascending semitone distance from the original note equals 11.
    - The function performs no I/O and does not mutate global state itself.

Termination and correctness notes:
    - augment_or_diminish_until_the_interval_is_right expects its interval argument to be an integer in 0..11 inclusive to guarantee termination; this function passes the integer 11, which lies within that range. Provided the augment/diminish helper's preconditions are satisfied (non-empty, parseable pitch-name strings), the adjustment loop will terminate with a pitched-class whose measure from the root equals 11.
    - If an invalid interval (outside 0..11 or non-integer) were passed to the augment/diminish helper, that helper documents a risk of non-termination. That risk does not apply here because 11 is used.

## Side Effects:
    - No direct I/O, network calls, or global mutations.
    - Indirect effects may occur in called helpers (for example, keys.get_notes may populate an internal cache).

## Control Flow:
flowchart TD
    Start([Start]) --> CheckEmpty{Is note non-empty?}
    CheckEmpty -- No --> RaiseIndexError[Raise IndexError]
    CheckEmpty -- Yes --> CallSeventh[Call seventh(note[0], "C") -> sth (a pitch-name string)]
    CallSeventh --> SeventhError{Seventh raised error?}
    SeventhError -- Yes --> PropagateSeventhError[Propagate error]
    SeventhError -- No --> CallAdjust[Call augment_or_diminish_until_the_interval_is_right(note, sth, 11)]
    CallAdjust --> AdjustError{Adjust helper raised error?}
    AdjustError -- Yes --> PropagateAdjustError[Propagate error]
    AdjustError -- No --> ReturnResult[Return spelled major seventh]
    ReturnResult --> End([End])

## Examples:
1) Typical usage:
    try:
        mj7 = major_seventh("C")
        # mj7 == "B"
    except Exception as e:
        # handle parsing/format errors or invalid input
        raise

2) With accidentals:
    try:
        mj7 = major_seventh("C#")
        # mj7 == "B#"
    except Exception:
        raise

3) Error cases:
    # Empty input -> IndexError
    try:
        major_seventh("")
    except IndexError:
        # validate input before calling
        pass

    # Invalid base letter -> KeyError or NoteFormatError
    try:
        major_seventh("H")
    except (KeyError, ValueError):
        # report invalid note format
        pass

Implementation notes:
    - Implementation steps for reimplementation:
        1) base = note[0]
        2) sth = seventh(base, "C")          # returns a pitch-name string appropriate as note2
        3) return augment_or_diminish_until_the_interval_is_right(note, sth, 11)
    - Delegate accidental adjustments and normalization to augment_or_diminish_until_the_interval_is_right to preserve consistent behavior and avoid duplicating the augmentation/diminution loop.

## `mingus.core.intervals.get_interval` · *function*

## Summary:
Return the note name that is a given number of semitones above an input note, choosing a spelling consistent with the specified major key when possible and producing a flat (diminished) enharmonic spelling when the chromatic result is not diatonic in that key.

## Description:
This function computes a pitch-class result by adding an integer number of semitones (interval) to the diatonic scale degree that corresponds to the input note's base letter within a given major key, and then selects an appropriate spelled note name:
- It constructs the seven diatonic pitch classes for the major key (intervals from the tonic: 0, 2, 4, 5, 7, 9, 11) shifted by the key tonic's pitch class.
- It asks keys.get_notes(key) for the seven spelled degree names in the given key (e.g., ['C','D','E','F','G','A','B'] for C major, with accidentals if the key has sharps/flats).
- It finds the key degree whose first character (letter A–G) matches the first character of the input note and uses that degree's diatonic pitch-class as the starting point.
- It adds the requested semitone offset modulo 12 to obtain the result pitch class.
- If that result pitch-class equals one of the key's diatonic pitch-classes, it returns the corresponding key degree name (preserving the input note's trailing substring note[1:] verbatim).
- If the result is not diatonic, it selects the key degree whose pitch-class equals (result + 1) mod 12 and returns the diminished (flat) form of that degree (via notes.diminish), again appending the original note[1:].

Typical callers:
- Higher-level scale, chord, or melody utilities that need a musically spelled note a specific number of semitones away while remaining consistent with a major key's diatonic notation.
- User code performing harmonic analysis or voice-leading transformations.

Why separated:
- This logic mixes pitch-class arithmetic, key-aware diatonic spelling, and enharmonic choice; extracting it makes other code simpler and centralizes spelling rules and edge-case handling.

## Args:
    note (str)
        - A note string where the first character is an uppercase letter A–G, e.g., 'C', 'F#', 'Eb4', 'G3'.
        - The function uses only note[0] to determine the starting key degree and preserves note[1:] (the remainder of the string) by appending it unchanged to the returned spelled note.
        - There is no validation of note[1:]; callers should ensure it contains only intended accidentals/octave markers if they expect well-formed output.
    interval (int)
        - Number of semitones to add to the starting degree's pitch-class. Any integer is allowed; arithmetic is performed modulo 12 (negative values wrap).
    key (str, optional, default "C")
        - The major key used for diatonic spelling. It is forwarded to keys.get_notes(key) which will validate the key and may raise a NoteFormatError for invalid keys.

## Returns:
    str
        - A spelled note name (string) representing the pitch-class (start_degree_pc + interval) % 12.
        - If the computed pitch-class matches a diatonic pitch-class of the key, the returned value is the corresponding key degree name with note[1:] appended.
        - If not diatonic, the returned value is the diminished (flat) form of the key degree whose pitch-class equals (result + 1) % 12, with note[1:] appended. The diminishing operation behaves as follows: if the chosen key degree ends with '#', the trailing '#' is removed; otherwise, a 'b' is appended (producing a one-semitone-lower spelling).
        - The function does not attempt to normalize or merge accidentals between the chosen degree and note[1:]; the trailing substring is appended verbatim.

## Raises:
    - NoteFormatError: propagated from keys.get_notes(key) when key has an unrecognized format.
    - UnboundLocalError: raised by the implementation if no key degree is found whose first character equals note[0]. This occurs when the input note's first character is not one of the letters returned by keys.get_notes(key) (typically A–G). Callers should ensure note[0] is a letter A–G that appears in the key's degree names.
    - Any exceptions propagated from the underlying utilities (e.g., if those utilities are changed to raise additional errors).

## Constraints:
    Preconditions:
        - key must be a valid major key string accepted by keys.get_notes.
        - note must be a non-empty string whose first character is one of A..G that appears as the first character of a degree name returned by keys.get_notes(key).
    Postconditions:
        - The returned string begins with a letter A..G (optionally followed by '#' or 'b'), and includes the original note[1:] appended verbatim.
        - The returned note's pitch-class (interpreted by notes.note_to_int on its base) equals (tonic_pc + one_of [0,2,4,5,7,9,11] + interval) % 12 as produced by the function's arithmetic.

## Side Effects:
    - No I/O (no files, network, or stdout).
    - No modification of global state by this function. It only calls keys.get_notes and notes.diminish/note_to_int helpers.
    - Exceptions from helper functions are propagated to the caller.

## Control Flow:
flowchart TD
    A[Start: receive note, interval, key] --> B[Compute key tonic pitch-class via notes.note_to_int(key)]
    B --> C[Compute diatonic pitch-classes = (tonic + [0,2,4,5,7,9,11]) % 12]
    C --> D[Get spelled key notes: key_notes = keys.get_notes(key)]
    D --> E{Find degree in key_notes where degree[0] == note[0]}
    E -->|found| F[Let start_pc = corresponding diatonic pitch-class]
    E -->|not found| X[No matching degree -> UnboundLocalError when result is referenced]
    F --> G[Compute result = (start_pc + interval) % 12]
    G --> H{Is result one of diatonic pitch-classes?}
    H -->|yes| I[Return key_notes[index_of_result] + note[1:]]
    H -->|no| J[Let candidate_idx = index_of((result + 1) % 12)]
    J --> K[Return notes.diminish(key_notes[candidate_idx]) + note[1:] ]

## Examples:
    1) Diatonic result (preserves spelling from key)
       Input: note='C', interval=2, key='C'
       - key_notes for C: ['C','D','E','F','G','A','B']
       - C degree pitch-class = 0; result = (0+2)%12 = 2 -> diatonic (D)
       Return: 'D'

    2) Non-diatonic result (produces diminished/flat enharmonic)
       Input: note='C', interval=1, key='C'
       - start_pc = 0; result = 1 -> not diatonic
       - (result + 1) % 12 = 2 -> diatonic degree at index-of-2 is 'D'
       - notes.diminish('D') -> 'Db'
       Return: 'Db'

    3) Preserving trailing accidentals and octaves (appended verbatim)
       Input: note='E#4', interval=1, key='C'
       - key_notes['E'] -> 'E' (start_pc = 4); result = (4 + 1) % 12 = 5 -> diatonic degree 'F'
       - Returned string = 'F' + '#4' => 'F#4'
       Note: The function simply appends note[1:] ('#4') to the chosen degree name without reconciling accidentals; in this example the result is a sensible musical name, but callers must avoid embedding accidental semantics in note[1:] unless intended.

    4) Invalid key
       Input: note='C', interval=2, key='H#' (invalid)
       - keys.get_notes raises NoteFormatError; this function propagates that exception.

Notes and implementation caveats:
    - keys.get_notes returns seven degree names whose first characters correspond to the seven letter names A–G in order; therefore, for a valid input note[0] in A–G that matches the intended scale degree, exactly one degree should match. The UnboundLocalError only arises when note[0] is not a letter present in the key_notes (e.g., malformed input).
    - The function uses modulo-12 arithmetic for semitone offsets; interval values outside 0–11 are wrapped accordingly.
    - The diminished spelling is chosen deterministically by taking the next key degree (result + 1) mod 12 and applying notes.diminish to it; notes.diminish appends 'b' when the degree does not end with '#', otherwise it removes a trailing '#'.

## `mingus.core.intervals.measure` · *function*

## Summary:
Compute the ascending interval in semitones from note1 up to note2 within a single octave, returning an integer in the range 0..11.

## Description:
This small utility converts two pitch names to their integer pitch encodings (using the notes.note_to_int helper) and returns the upward distance in semitones from the first pitch to the second, wrapped to a single octave. If the second pitch is lower in pitch-class value than the first, the function returns the number of semitones required to reach the next occurrence of note2 above note1 (i.e., uses modulo-12 arithmetic to always produce an ascending interval).

Known callers within the codebase:
    - No direct call sites were found in the provided memory snapshot. Conceptually, this function is intended for use by higher-level interval, transposition, or analysis code that needs the ascending semitone distance between two pitch names (for example, to compute interval names, interval qualities, or to decide octave adjustments during transposition).

Why this logic is extracted:
    - Encapsulates the common operation "ascending semitone distance modulo an octave" in a single place to avoid duplicating the note-to-int conversion and modulo arithmetic at multiple call sites.
    - Keeps caller code focused on musical logic (interval naming, interval comparison, transposition) rather than integer arithmetic details.

## Args:
    note1 (str): A pitch name accepted by notes.note_to_int (e.g., "C", "D#", "Bb").
        - Must be in the format recognized by the notes module: a note letter (A-G) optionally followed by accidentals (one or more '#' or 'b').
        - Passing an invalid string will cause notes.note_to_int to raise an error (see Raises).
    note2 (str): A pitch name accepted by notes.note_to_int (same format rules as note1).

    Notes on types and interdependencies:
        - Both arguments are independently validated by notes.note_to_int; there is no dependency between note1 and note2 beyond computing their difference.
        - The function does not accept pitch objects directly; any object accepted by notes.note_to_int (typically strings) is valid. If you pass other types, behavior depends on how notes.note_to_int handles them.

## Returns:
    int: The ascending semitone distance from note1 to note2, in the range 0..11 inclusive.
        - 0 indicates the same pitch class (e.g., measure("C", "C") -> 0).
        - Values 1..11 indicate the number of semitones you must ascend from note1 to reach note2 within the next octave.
        - Examples:
            - measure("C", "E") -> 4
            - measure("E", "C") -> 8  (ascending from E up to the next C)

## Raises:
    - Any exception raised by notes.note_to_int will propagate unchanged. Common possibilities include:
        - NoteFormatError (from the notes module): when a passed string is not a recognized note format (for example, "H").
        - IndexError: if an empty string is passed (notes.note_to_int accesses note[0]).
        - TypeError: if the argument type does not support indexing or is otherwise incompatible with notes.note_to_int.
    - No exceptions are raised by measure itself; it simply forwards errors from the underlying conversion.

## Constraints:
    Preconditions:
        - Caller must provide two pitch identifiers acceptable to notes.note_to_int (principal constraint).
        - Inputs should represent pitch classes (note names with optional accidentals); octave numbers are not considered by this function.
    Postconditions:
        - The return value is an integer between 0 and 11 inclusive.
        - The function does not modify either input object.

## Side Effects:
    - None performed by this function: no I/O, no global state mutation, no network or filesystem access.
    - Any side effects originate only from side effects in notes.note_to_int (which, in the typical implementation, performs pure computation and also has no side effects).

## Control Flow:
flowchart TD
    A[Start: receive note1, note2] --> B[Compute n1 = notes.note_to_int(note1)]
    B --> C[Compute n2 = notes.note_to_int(note2)]
    C --> D[res = n2 - n1]
    D --> E{res < 0?}
    E -- Yes --> F[compute out = 12 - (-res)] --> G[Return out]
    E -- No --> H[Return res]

## Examples:
    Example — normal usage:
        measure("C", "E")
        # Returns: 4

    Example — ascending wrap-around:
        measure("E", "C")
        # Returns: 8  (ascending from E up to the next C)

    Example — same pitch class:
        measure("G#", "G#")
        # Returns: 0

    Example — error handling for invalid note:
        try:
            measure("H", "C")
        except Exception as exc:
            # notes.note_to_int will raise an exception (e.g., NoteFormatError)
            handle_error(exc)

    Notes:
        - Because this function delegates parsing/validation to notes.note_to_int, prefer validating inputs earlier if you need custom error messages or recovery logic.

## `mingus.core.intervals.augment_or_diminish_until_the_interval_is_right` · *function*

## Summary:
Adjust the spelling of a target pitch (note2) by adding or removing accidentals until the ascending semitone distance from a reference pitch (note1) equals the requested interval, then return a normalized note name (letter plus accidentals) representing that spelled pitch class.

## Description:
This function repeatedly augments or diminishes the second pitch name until measure(note1, note2) equals the numeric interval requested, then converts the spelled result into a canonical note-letter plus accidentals form.

Known callers within the codebase:
    - No direct callers were found in the provided snapshot. Conceptually this helper is intended for higher-level interval, transposition, or name-normalization routines that need a specific spelled pitch class at a given semitone distance from a reference pitch (for example, when constructing interval names, chord spellings, or transpositions that preserve diatonic letter relationships).

Why this logic is factored out:
    - It encapsulates the responsibility "mutate a spelled pitch by accidentals until a target ascending semitone distance is reached" so that callers do not need to implement the iterative augment/diminish loop, accidentals counting, normalization of excessive accidentals, or conversion to a base-letter-with-accidentals form themselves. This keeps higher-level interval and spelling logic concise and correct.

## Args:
    note1 (str):
        - A pitch name accepted by the notes module (examples: "C", "D#", "Bb", "G##").
        - Format: a letter A-G as the first character, optionally followed by one or more accidentals ('#' or 'b'). Octave digits or other trailing tokens are allowed by the caller but only the first character and subsequent '#'/'b' tokens are used by this function.
        - Precondition: must be parsable by measure (which delegates to notes.note_to_int). Passing an invalid format will raise from lower-level converters.

    note2 (str):
        - A pitch name (same accepted format as note1). This argument is mutated locally (a new string is assigned) as the function augments/diminishes it while searching for the target interval.
        - The function inspects note2[1:] to count accidentals; therefore note2 must be at least one character long (non-empty).

    interval (int):
        - The desired ascending semitone distance from note1 to note2 after adjustment.
        - Expected range: 0..11 inclusive (the function compares against measure which returns values modulo an octave).
        - Must be an integer; non-integer values will not compare meaningfully and can lead to non-termination.

## Returns:
    str: A normalized note name representing the spelled pitch class of the adjusted note2.
        - The return value is composed of:
            * The base letter taken from the first character of the final adjusted note2.
            * Followed by a number of '#' characters (for positive accidentals) or 'b' characters (for negative accidentals) such that the returned string reflects the same pitch class as the adjusted note2 within the single-octave encoding.
        - The returned string does NOT include octave numbers or any characters other than the base letter and accidentals.
        - Examples:
            * If adjustment leaves note2 as "Eb" -> returns "Eb"
            * If adjustment leaves note2 as "E" -> returns "E"
            * If a note accumulates many accidentals this function normalizes them into a representation with at most 6 accidentals in magnitude (see normalization rules below).

## Raises:
    Any exception raised by measure or by notes.note_to_int will propagate; common possibilities include:
        - IndexError: If note1 or note2 is an empty string (the function reads note2[0] and note2[1:]).
        - TypeError: If arguments are of unsupported types for measure/notes functions.
        - ValueError or NoteFormatError (from notes.note_to_int): When a passed string is not a recognized note format.
    Notes on infinite-loop risk:
        - The function does not validate interval. If interval is outside the 0..11 range or is not an int, the while loop searching for cur == interval may never terminate. Callers must ensure interval is a single-octave semitone distance (0..11).

## Constraints:
    Preconditions:
        - note1 and note2 must be valid pitch name strings accepted by notes.note_to_int / measure.
        - note2 must be non-empty.
        - interval must be an integer in 0..11 inclusive (to guarantee termination).
    Postconditions:
        - The returned string represents a pitch-class whose ascending semitone distance from note1 (as measured by measure) equals the requested interval.
        - The result contains only the base note letter and accidentals and does not include octave digits.

## Side Effects:
    - No I/O, no network, no global state mutation.
    - The function performs only pure string operations and calls to measure and notes.augment/diminish; any side effects would originate from those called functions (in typical implementations those are pure and side-effect free).

## Control Flow:
flowchart TD
    Start[Start: receive note1, note2, interval]
    Start --> ComputeCur[Compute cur = measure(note1, note2)]
    ComputeCur --> CheckCur{cur == interval?}
    CheckCur -- No and cur > interval --> DiminishNote[call notes.diminish(note2) -> note2']
    CheckCur -- No and cur < interval --> AugmentNote[call notes.augment(note2) -> note2']
    DiminishNote --> RecomputeCur[recompute cur = measure(note1, note2')]
    AugmentNote --> RecomputeCur
    RecomputeCur --> CheckCur
    CheckCur -- Yes --> CountAccidentals[Count accidentals in note2[1:] -> val]
    CountAccidentals --> NormalizeVal{val > 6? or val < -6?}
    NormalizeVal -- val > 6 --> WrapHigh[reduce val by val%12 then val = -12 + (val%12)]
    NormalizeVal -- val < -6 --> WrapLow[reduce val by val% -12 then val = 12 + (val% -12)]
    NormalizeVal -- otherwise --> ComputeResultBase[set result = note2[0]]
    WrapHigh --> ComputeResultBase
    WrapLow --> ComputeResultBase
    ComputeResultBase --> ApplyAccidentalsLoop{val > 0? val < 0?}
    ApplyAccidentalsLoop -- val > 0 --> AugLoop[apply notes.augment(result) decrement val]
    ApplyAccidentalsLoop -- val < 0 --> DimLoop[apply notes.diminish(result) increment val]
    AugLoop --> ApplyAccidentalsLoop
    DimLoop --> ApplyAccidentalsLoop
    ApplyAccidentalsLoop -- val == 0 --> ReturnResult[Return result]

## Examples:
    1) Standard case — no change required:
        note1 = "C"
        note2 = "E"
        interval = 4
        # measure("C","E") == 4 so function returns "E"

    2) Lower the spelled pitch to obtain a minor third:
        note1 = "C"
        note2 = "E"
        interval = 3
        # measure("C","E") == 4 > 3 so note2 is diminished to "Eb"; function returns "Eb"

    3) Raise a flat to a natural/sharp as needed:
        note1 = "C"
        note2 = "Fb"   # spelling with two characters; 'Fb' is valid as a note name
        interval = 5
        # function will augment/diminish note2 until measure("C", note2) == 5, then return the base letter with normalized accidentals.

    4) Error example — empty input:
        try:
            augment_or_diminish_until_the_interval_is_right("", "E", 4)
        except IndexError:
            # note1 or note2 was empty; calling code should validate inputs first
            handle_input_error()

    Implementation notes for callers:
        - Ensure interval is within 0..11 to avoid non-termination.
        - If you need to preserve octave information, do not rely on the returned string; instead track octave separately or reconstruct the octave after you obtain the spelled pitch class.

## `mingus.core.intervals.invert` · *function*

## Summary:
Returns a new list containing the elements of the provided interval sequence in reverse order while restoring the original sequence to its original ordering before returning.

## Description:
Known callers within the provided code snapshot:
- No callers of this function were discovered in the supplied repository snapshot.

Typical usage context:
- Used when a reversed representation of an interval sequence is needed but the caller must preserve the original sequence object. The function is a small utility to produce a reversed copy while leaving the original sequence unchanged once the call completes.

Why this logic is extracted:
- The function encapsulates the pattern "temporarily reverse the input, capture a reversed copy, then restore the input." Extracting this logic avoids duplicating the two reverse calls and the list-copy idiom across the codebase and makes the intent explicit (produce a reversed copy without a lasting mutation of the input object).

## Args:
    interval (mutable sequence-like): A sequence-like object that:
        - supports an in-place reverse() method (e.g., a list) and
        - is iterable (so list(interval) succeeds).
    Notes:
        - The implementation expects a mutable sequence with a reverse method. Passing an immutable sequence (e.g., tuple) or an object without reverse() will raise an exception.
        - The function does not accept keyword-only parameters; it has a single positional parameter.

## Returns:
    list: A new Python list containing the elements of the input sequence in reverse order.
    - If the input is empty, returns an empty list.
    - The returned list is independent of the input object (mutating the returned list does not affect the input).
    - The original input object is restored to its original ordering before the function returns.

## Raises:
    AttributeError:
        - If the provided object does not have a reverse() method (e.g., passing a tuple).
    TypeError:
        - If the provided object is not iterable (list(interval) will raise TypeError).
        - If reverse() exists but list(interval) fails for that object type.
    Any exceptions raised are the raw Python exceptions produced by calling interval.reverse() or list(interval); the function performs no additional validation or wrapping.

## Constraints:
Preconditions:
    - The caller must pass an object that implements an in-place reverse() method and is iterable (preferably a list).
    - If callers cannot guarantee that, they should convert the input to a list before calling (e.g., interval = list(interval)).

Postconditions:
    - The input sequence will have the same ordering and contents it had before the call (assuming no concurrent mutation).
    - The returned value is a list whose element order is the element-wise reverse of the input as it was at call start.
    - The length and multiset of elements of the returned list match those of the input.

## Side Effects:
    - The function performs a transient in-place mutation of the provided object by calling interval.reverse(), then interval.reverse() again to restore it.
    - There is no persistent mutation: when the function returns the original object has been restored to its original order (unless an exception is raised before the second reverse()).
    - Important concurrency note: because the input is mutated temporarily, other threads or observers that access the same object while this function runs may observe the reversed ordering; the function is not thread-safe with respect to external concurrent observers.
    - No I/O, network access, global state mutation, or external service calls occur.

## Control Flow:
flowchart TD
    Start([Start])
    CallReverse1["Call interval.reverse() (in-place)"]
    BuildList["Create res = list(interval)"]
    CallReverse2["Call interval.reverse() to restore original"]
    ReturnRes["Return res (reversed copy)"]
    Start --> CallReverse1 --> BuildList --> CallReverse2 --> ReturnRes

    %% Exception branches
    CallReverse1 -- AttributeError/TypeError --> PropagateError[/Propagate exception/]
    BuildList -- TypeError --> PropagateError
    CallReverse2 -- AttributeError/TypeError --> PropagateError

## Examples:
1) Typical usage with a list of intervals (original preserved):
    input_intervals = [2, 1, 2]
    result = invert(input_intervals)
    # result == [2, 1, 2]  # elements in reverse order
    # input_intervals remains [2, 1, 2] (restored to original order)

2) Empty input:
    input_intervals = []
    result = invert(input_intervals)
    # result == []
    # input_intervals == [] (unchanged)

3) Defensive conversion for non-list inputs:
    input_tuple = (2, 1, 2)
    # Calling invert(input_tuple) will raise AttributeError because tuples lack reverse().
    result = invert(list(input_tuple))  # returns [2, 1, 2]

4) Error handling (example pattern):
    try:
        inverted = invert(maybe_not_list)
    except AttributeError:
        # convert and retry or handle the incompatible type
        inverted = invert(list(maybe_not_list))
    except TypeError:
        # handle non-iterable or other type errors
        handle_invalid_input()

Implementation note for reimplementers:
- An alternative implementation that avoids in-place mutation is simply: return list(interval)[::-1] after ensuring interval is iterable; however, for certain custom sequence types where list(interval) preserves order but reverse() isn't available, the current code requires conversion to a list first. The provided implementation optimizes for the common case where interval is already a list and wants to avoid creating two intermediate lists (it creates only one list for the result).

## `mingus.core.intervals.determine` · *function*

*No documentation generated.*

## `mingus.core.intervals.from_shorthand` · *function*

## Summary:
Converts a compact interval shorthand (e.g., "3", "#4", "b7") into the concrete note name at that interval above or below a given root note; returns the resulting note string on success or False on invalid input.

## Description:
Resolves a shorthand interval string into an explicit note by:
- validating the root note,
- mapping the interval degree (final character in the shorthand) to a base interval constructor (major_/minor_ helpers),
- applying accidentals ('#' to augment, 'b' to diminish) in left-to-right order,
- returning the computed note string.

This function is used whenever callers need to turn human-friendly interval shorthand into a concrete note (for chords, scale computations, or other interval arithmetic). It exists to centralize:
- validation of the root note,
- the mapping between degree digits and the appropriate interval constructors depending on direction (up/down),
- and the application of accidentals via the notes utility functions.

Known callers:
- Modules or functions that parse chord/scale descriptions or accept interval shorthand from users. (Specific call sites are not enumerated here; callers typically call this when a shorthand string is parsed.)

Responsibility boundary:
- This function composes interval constructor helpers and notes.augment/diminish to produce a final note string. It does not parse named interval words beyond recognizing leading '#' and 'b' accidentals and a final degree digit, nor does it normalize or validate the interval syntax beyond relying on the final character for mapping.

## Args:
    note (str)
        - Root note string. Must satisfy notes.is_valid_note(note) or the function returns False.
        - Examples: "C", "D#", "Bb" depending on the notes module's conventions.

    interval (str)
        - Interval shorthand string. Must be non-empty.
        - The last character must be a digit '1'..'7' identifying the degree used to select a base interval function.
        - Zero or more leading accidental characters may appear before the degree: '#' to augment, 'b' to diminish.
        - Examples: "1", "3", "#4", "b7", "##5", "bbb2".
        - If the string is empty, the function will raise IndexError when attempting to access interval[-1].

    up (bool, optional)
        - Direction flag. True (default) computes the interval above the root; False computes the corresponding interval below the root using the module's inverse mappings.

Interdependencies:
- Delegates degree-to-note computation to interval functions (major_unison, major_second, ..., minor_second) and applies accidentals using notes.augment and notes.diminish. Correct behavior depends on those helpers accepting and returning note strings compatible with notes.* utilities.

## Returns:
    str or bool
    - On success: returns a note string representing the computed interval relative to the input note (format depends on helper implementations, e.g. "E", "E#", "Fb").
    - On failure: returns False in these cases:
        * notes.is_valid_note(note) returns False (invalid root note).
        * The final character of interval is not one of '1'..'7' (no shorthand mapping found).
    - Note: the function uses False as a sentinel for error/invalid input; it does not return None.

## Raises:
    IndexError
        - If interval is an empty string, interval[-1] will raise IndexError.
    Any exception raised by delegated helpers
        - If any of the called helper functions (major_*/minor_* functions, notes.augment, notes.diminish, or notes.is_valid_note) raise an exception, that exception will propagate; the function does not catch these.

## Constraints:
Preconditions:
    - note must be a valid note according to notes.is_valid_note.
    - interval must be a non-empty string with the degree digit as its last character.
    - Accidentals (if present) should precede the degree digit.

Postconditions:
    - If a non-False value is returned, it is the result of:
        1) calling the chosen base interval constructor with the root note,
        2) applying augment/diminish once per accidental character in left-to-right order until a non-accidental character is encountered,
        3) returning the modified note string.
    - If False is returned, no external state is modified by this function.

## Side Effects:
    - No direct I/O.
    - No mutation of global state performed by this function.
    - Calls to notes.* and interval constructor helpers may have side effects; this function itself performs no state mutations.

## Control Flow:
flowchart TD
    Start --> CheckNoteValid
    CheckNoteValid{notes.is_valid_note(note)?}
    CheckNoteValid -- no --> ReturnFalseInvalidNote[Return False]
    CheckNoteValid -- yes --> CheckIntervalNotEmpty{interval != ""?}
    CheckIntervalNotEmpty -- no --> RaiseIndexError[IndexError]
    CheckIntervalNotEmpty -- yes --> DetermineDegree[degree = interval[-1]]
    DetermineDegree --> LookupShorthand[Find shorthand entry with shorthand[0] == degree]
    LookupShorthand --> Found{found?}
    Found -- no --> ReturnFalseNoMatch[Return False]
    Found -- yes --> ComputeBase{up?}
    ComputeBase -- yes --> val = shorthand[1](note)
    ComputeBase -- no --> val = shorthand[2](note)
    ComputeBase --> IterateChars[Loop x in interval left-to-right]
    IterateChars --> IsSharp{x == "#"?}
    IsSharp -- yes --> Direction2{up?}
    Direction2 -- yes --> val = notes.augment(val)
    Direction2 -- no --> val = notes.diminish(val)
    IsSharp -- no --> IsFlat{x == "b"?}
    IsFlat -- yes --> Direction3{up?}
    Direction3 -- yes --> val = notes.diminish(val)
    Direction3 -- no --> val = notes.augment(val)
    IsFlat -- no --> ReturnVal[Return val]
    ReturnVal --> End

Notes on iteration behaviour:
    - The function processes interval characters left-to-right.
    - For each '#' or 'b' it adjusts val accordingly.
    - On encountering the first character that is neither '#' nor 'b' (typically the degree digit), the function returns the current val immediately.
    - Therefore, accidentals must precede the degree digit to be applied. Any characters following the first non-accidental character are not inspected.

## Examples:
- Basic (above the root):
    result = from_shorthand("C", "3")
    # returns the major third above C (dependent on major_third implementation, e.g. "E")

- With accidentals:
    result = from_shorthand("C", "#3")
    # computes major_third("C"), then notes.augment(...) once

    result = from_shorthand("C", "##3")
    # applies augment twice (left-to-right) to the base interval

- Downwards:
    result = from_shorthand("C", "3", up=False)
    # uses the inverse mapping for degree "3" (e.g. minor sixth below C)

- Invalid root:
    result = from_shorthand("NotANote", "3")
    # returns False

- Invalid/missing degree:
    result = from_shorthand("C", "x")
    # returns False because 'x' does not match '1'..'7'

- Empty interval (caller must guard against this or handle IndexError):
    result = from_shorthand("C", "")
    # raises IndexError due to interval[-1]

Usage guidance:
    - Validate inputs before calling if you prefer exceptions over False sentinels (e.g., ensure notes.is_valid_note(note) and non-empty interval with degree digit).
    - Treat a False return as an invalid input indicator rather than an exception for standard validation checks.

## `mingus.core.intervals.is_consonant` · *function*

## Summary:
Return whether the interval from the first pitch to the second is a consonance (either perfect or imperfect), with an option to treat perfect fourths as consonant.

## Description:
This predicate evaluates whether the ascending interval from note1 to note2 (wrapped within a single octave) is considered musically consonant. It does so by delegating to two helper predicates: it first tests perfect-consonance rules (unison/octave, perfect fifth, and optionally perfect fourth) and, if that fails, tests imperfect-consonance rules (minor/major third or minor/major sixth). The function returns a boolean combining these two results.

Known callers:
    - No direct callers were found in the provided repository snapshot.
    - Typical callers (conceptual): harmony analysis routines, voice-leading validators, chord/scale utilities, or any higher-level code that needs a simple boolean test for consonance.

Why this logic is a separate function:
    - Encapsulates the common musical question "is this interval consonant?" into a single, readable predicate so callers do not need to repeat numeric interval lists or combine multiple helper checks.
    - Keeps higher-level code concise and focused on musical decisions instead of low-level semitone comparisons.

## Args:
    note1 (object):
        - The lower/starting pitch. Accepted values are any type that the module's measure() helper (via notes.note_to_int) accepts — commonly a pitch name string like "C", "G#", "Bb".
        - No normalization is performed here; invalid inputs will cause underlying parsing to raise.
    note2 (object):
        - The upper/target pitch; same accepted types and constraints as note1. The check is for the ascending interval from note1 up to note2 within a single octave (0..11 semitones).
    include_fourths (bool, optional):
        - Defaults to True.
        - Controls whether an ascending perfect fourth (5 semitones) is considered a perfect consonance. This flag is forwarded only to the perfect-consonant check; imperfect-consonant behavior is unaffected.

Interdependencies:
    - include_fourths affects only the perfect-consonant branch; the imperfect-consonant branch always uses its fixed set of intervals.
    - Validity of note1/note2 depends on the behavior of measure() / notes.note_to_int.

## Returns:
    bool:
        - True if the ascending interval (measure(note1, note2)) is classified as either:
            * a perfect consonance — unison/octave (0 semitones) or perfect fifth (7 semitones), and also perfect fourth (5 semitones) when include_fourths is True; OR
            * an imperfect consonance — minor/major third (3 or 4 semitones) or minor/major sixth (8 or 9 semitones).
        - False otherwise (any interval not listed above).

    Possible return values:
        - True: interval ∈ {0,7} ∪ ({5} if include_fourths) ∪ {3,4,8,9}
        - False: all other ascending intervals in 0..11 not in the sets above

## Raises:
    - This function does not raise its own exceptions but will propagate any exception raised by the underlying interval-measurement utilities (measure() and notes.note_to_int). Typical propagated exceptions include:
        - ValueError or a module-specific NoteFormatError for unrecognized pitch strings.
        - TypeError if an argument type cannot be processed.
        - IndexError if an invalid string is indexed by the parser.

## Constraints:
    Preconditions:
        - note1 and note2 must be acceptable inputs to the module's note parsing helper (notes.note_to_int).
        - include_fourths should be a boolean; truthy/falsy values follow Python boolean conversion.

    Postconditions:
        - No mutation of note1, note2, or global state.
        - The return value is a boolean that accurately reflects the union of perfect and imperfect consonance predicates, with include_fourths applied to the perfect-consonance test.

## Side Effects:
    - None intrinsic: no I/O, no filesystem/network operations, no global-state changes.
    - Any side effects originate only from side effects (if any) of measure() or notes.note_to_int.

## Control Flow:
flowchart TD
    Start[Start: receive note1, note2, include_fourths] --> CheckPerfect[Call is_perfect_consonant(note1, note2, include_fourths)]
    CheckPerfect -->|True| ReturnTrue1[Return True]
    CheckPerfect -->|False| CheckImperfect[Call is_imperfect_consonant(note1, note2)]
    CheckImperfect -->|True| ReturnTrue2[Return True]
    CheckImperfect -->|False| ReturnFalse[Return False]

## Examples:
    Typical — perfect fifth:
        is_consonant("C", "G")
        # Returns: True  (perfect fifth -> perfect consonance)

    Typical — major third (imperfect consonance):
        is_consonant("C", "E")
        # Returns: True  (major third -> imperfect consonance)

    Fourth behavior controlled by flag:
        is_consonant("C", "F")                      # include_fourths defaults to True
        # Returns: True  (perfect fourth counted as consonant by default)

        is_consonant("C", "F", include_fourths=False)
        # Returns: False  (perfect fourth excluded; neither perfect nor imperfect consonance)

    Dissonant interval:
        is_consonant("C", "C#")
        # Returns: False  (minor second -> dissonant)

    Invalid input handling:
        try:
            is_consonant("H", "C")
        except Exception as exc:
            # Underlying parsing/measurement will raise (e.g., ValueError); handle or propagate
            handle_error(exc)

## `mingus.core.intervals.is_perfect_consonant` · *function*

## Summary:
Determine whether the interval from one pitch to another is a perfect consonance (unison/octave or perfect fifth), optionally treating perfect fourth as consonant.

## Description:
This function computes the ascending semitone interval from note1 up to note2 (within a single octave) using the shared measure utility, and returns True when that interval is considered a perfect consonant. By default perfect consonances are: unison/octave-equivalent (0 semitones) and perfect fifth (7 semitones). If include_fourths is True (the default), perfect fourth (5 semitones) is also treated as consonant.

Known callers:
    - No direct callers were found in the provided repository snapshot. Conceptually, this helper is intended for use by higher-level analysis, harmony-checking, voice-leading, or interval-classification code that needs a boolean test for perfect consonance.

Why this logic is extracted:
    - Encapsulates the musical rule "is this interval a perfect consonance?" in a single, readable place so callers can use a clear boolean predicate instead of repeating numeric interval checks.
    - Keeps callers focused on musical logic rather than low-level semitone comparisons and the include_fourths toggle.

## Args:
    note1 (object):
        - A pitch identifier accepted by the module's measure() helper (typically a pitch name string such as "C", "D#", "Bb" in the format recognized by notes.note_to_int).
        - measure() will convert this argument via notes.note_to_int, so any type valid for that conversion is acceptable.
    note2 (object):
        - Same requirements as note1; the interval is computed from note1 up to note2 within a single octave.
    include_fourths (bool, optional):
        - Defaults to True.
        - When True, a perfect fourth (ascending distance of 5 semitones) will be treated as a perfect consonance in addition to unison (0) and perfect fifth (7).
        - When False, only 0 and 7 semitone intervals are considered perfect consonances.

Notes on interdependencies:
    - The function relies wholly on measure(note1, note2) to compute the ascending semitone distance. Validity of note1/note2 depends on what measure() (and thus notes.note_to_int) accepts.

## Returns:
    bool:
        - True if the ascending interval (measure(note1, note2)) is in {0, 7} or, when include_fourths is True, equals 5.
        - False otherwise.

    Possible outcomes:
        - True: unison/octave-equivalent (0 semitones), perfect fifth (7 semitones), or (if include_fourths) perfect fourth (5 semitones).
        - False: any other ascending semitone distance (1..4,6,8..11), or when include_fourths=False and distance==5.

## Raises:
    - Any exception raised by measure(note1, note2) will propagate unchanged. Typical examples include:
        - ValueError or NoteFormatError: when a supplied pitch string is not in a recognized format for notes.note_to_int.
        - TypeError: if an argument type is incompatible with notes.note_to_int.
        - IndexError: if an empty string or otherwise indexing-invalid input reaches notes.note_to_int.
    - The function itself performs no additional validation and does not raise custom exceptions.

## Constraints:
    Preconditions:
        - note1 and note2 must be acceptable inputs to measure() / notes.note_to_int (commonly: valid note name strings, e.g., "C", "G#", "Bb").
        - include_fourths must be a boolean (truthy/falsy values will behave as Python booleans).

    Postconditions:
        - No mutation: the function does not modify note1, note2, or any global state.
        - The return value correctly reflects the membership test described above based on the ascending semitone result returned by measure().

## Side Effects:
    - None intrinsic to the function: no I/O, no network or filesystem access, no global state mutation.
    - Any side effects originate only from side effects in measure() or notes.note_to_int (which in typical implementations are pure).

## Control Flow:
flowchart TD
    Start[Start: receive note1, note2, include_fourths] --> Calc[Call measure(note1, note2) -> dhalf]
    Calc --> CheckUnisonFifth{dhalf in [0,7]?}
    CheckUnisonFifth -- Yes --> ReturnTrue1[Return True]
    CheckUnisonFifth -- No --> CheckFourth{include_fourths AND dhalf == 5?}
    CheckFourth -- Yes --> ReturnTrue2[Return True]
    CheckFourth -- No --> ReturnFalse[Return False]

## Examples:
    Example — unison (same pitch class):
        is_perfect_consonant("C", "C")  # measure -> 0
        # Returns: True

    Example — perfect fifth:
        is_perfect_consonant("C", "G")  # measure -> 7
        # Returns: True

    Example — perfect fourth default behavior:
        is_perfect_consonant("C", "F")  # measure -> 5
        # Returns: True  (because include_fourths defaults to True)

    Example — perfect fourth when excluded:
        is_perfect_consonant("C", "F", include_fourths=False)
        # Returns: False

    Example — enharmonic / wrap-around:
        is_perfect_consonant("G#", "F#")  # measure computes ascending semitones modulo octave
        # Returns depends on measure("G#", "F#") which yields an ascending distance in 0..11

    Example — invalid input handling:
        try:
            is_perfect_consonant("H", "C")
        except Exception as exc:
            # notes.note_to_int (via measure) will raise; handle or propagate as appropriate
            handle_error(exc)

## `mingus.core.intervals.is_imperfect_consonant` · *function*

## Summary:
Return True when the ascending interval from the first pitch to the second is an imperfect consonance (minor/major third or minor/major sixth); otherwise return False.

## Description:
This predicate computes the ascending semitone distance from note1 to note2 (via the shared measure helper) and checks whether that distance is one of the four imperfect-consonant interval sizes: 3, 4, 8, or 9 semitones.

Known callers within the provided snapshot:
    - No direct call sites were found in the provided memory snapshot. Conceptually, this function is intended for use by interval analysis, voice-leading checks, or compositional/educational utilities that need a quick boolean test for imperfect consonance (for example: counterpoint validators, harmony analyzers, or heuristics in chord/voice-leading generators).

Why this logic is a separate function:
    - Encapsulates the musical concept "imperfect consonance" in one place so callers can ask the question at a high level without repeating the numeric interval comparison.
    - Keeps higher-level analysis code readable and avoids embedding the specific semitone list [3, 4, 8, 9] throughout the codebase.

## Args:
    note1 (str | object accepted by notes.note_to_int):
        - The starting pitch (lower note) expressed in a format accepted by the notes module (e.g., "C", "D#", "Bb"). Any parameter accepted by measure/notes.note_to_int is valid.
    note2 (str | object accepted by notes.note_to_int):
        - The destination pitch; the function checks the ascending interval from note1 up to note2 within a single octave.

Notes on interdependencies:
    - There is no semantic dependency between note1 and note2 beyond computing their ascending semitone difference. Both arguments are validated/parsed by the underlying measure call.

## Returns:
    bool:
        - True if measure(note1, note2) is one of [3, 4, 8, 9], i.e. the ascending interval is:
            * 3 semitones — minor third
            * 4 semitones — major third
            * 8 semitones — minor sixth (ascending)
            * 9 semitones — major sixth (ascending)
        - False otherwise (including unison, perfect consonances, seconds, fourths, fifths, sevenths, or any other interval not in the list).

## Raises:
    - Propagates any exceptions raised by measure() or notes.note_to_int. Typical propagated exceptions include:
        - NoteFormatError (or module-specific parsing exceptions) when an input string is not a recognized note.
        - IndexError for empty strings if notes.note_to_int indexes into the string.
        - TypeError if an argument type is incompatible with notes.note_to_int.
        - Any other exception thrown by underlying parsing/conversion logic.

## Constraints:
    Preconditions:
        - Both note1 and note2 must be acceptable inputs to the notes.note_to_int helper (the same preconditions as measure()).
        - The function assumes callers want the ascending interval within a single octave (measure() performs modulo-12 wrapping).

    Postconditions:
        - The function performs no mutation and returns a boolean reflecting whether the ascending semitone distance is an imperfect consonance.
        - No side effects guaranteed (see Side Effects).

## Side Effects:
    - None intrinsic to this function: no I/O, no global state mutation, no network calls.
    - Any side effects would come only from side effects of notes.note_to_int or other code invoked by measure(), which in typical implementations are pure computations without side effects.

## Control Flow:
flowchart TD
    A[Start: receive note1, note2] --> B[Call measure(note1, note2) -> m]
    B --> C{m in [3,4,8,9]?}
    C -- Yes --> D[Return True]
    C -- No --> E[Return False]

## Examples:
    Example — typical usage:
        is_imperfect_consonant("C", "E")
        # Returns: True  (C up to E is 4 semitones -> major third)

        is_imperfect_consonant("E", "C")
        # Returns: True  (ascending from E up to the next C is 8 semitones -> minor sixth)

    Example — non-imperfect consonance:
        is_imperfect_consonant("C", "G")
        # Returns: False  (C up to G is 7 semitones -> perfect fifth)

    Example — handling invalid input:
        try:
            is_imperfect_consonant("H", "C")
        except Exception as exc:
            # notes.note_to_int (via measure) will raise; handle or report error here
            handle_error(exc)

## `mingus.core.intervals.is_dissonant` · *function*

## Summary:
Return whether the ascending interval from note1 to note2 is musically dissonant (the logical negation of the consonance test), with a flag to control how perfect fourths are classified.

## Description:
This predicate is a small wrapper that returns the boolean negation of the consonance test applied to the ascending interval from note1 to note2. Consonance classification is delegated to the core is_consonant function; this function simply inverts that result while inverting the fourths flag when forwarding it.

Known callers:
    - mingus.containers.note_container.NoteContainer.is_dissonant
        - The container method performs the same logical negation on its instance-level is_consonant; it forwards the include_fourths parameter with identical inversion semantics.
    - Typical (conceptual) callers: harmony analysis routines, voice-leading validators, chord/scale utilities, or higher-level code that needs a simple boolean dissonance predicate.

Why this logic is a separate function:
    - Provides a clear, named predicate for "is this interval dissonant?" so calling code can express intent directly without writing not is_consonant(...) expressions.
    - Encapsulates the inversion of the fourths flag so callers don't have to remember the exact boolean logic used when treating perfect fourths.

## Args:
    note1 (any):
        - The lower/starting pitch of the interval.
        - Accepted formats are those supported by the library's note parsing utilities (commonly pitch name strings like "C", "G#", "Bb", or objects accepted by notes.note_to_int).
        - No normalization is performed here; invalid inputs will cause underlying parsing/measurement functions to raise.

    note2 (any):
        - The upper/target pitch. Same accepted formats and constraints as note1.
        - The interval is measured as the ascending interval from note1 to note2 wrapped into a single octave (0..11 semitones).

    include_fourths (bool, optional; default=False):
        - Controls how perfect fourths are treated, but note the inverted semantics relative to is_consonant:
            * If include_fourths is False (the default), this function calls is_consonant(note1, note2, True). In other words, by default perfect fourths are treated as consonant for the underlying consonance check, and thus will generally be considered non-dissonant here.
            * If include_fourths is True, this function calls is_consonant(note1, note2, False). In that case perfect fourths are excluded from consonance (treated as dissonant by the consonance test), so this wrapper will report perfect fourths as dissonant.
        - In short: include_fourths True => fourths counted as dissonant; include_fourths False => fourths counted as consonant (because the flag is inverted before calling is_consonant).

Interdependencies:
    - The value of include_fourths is inverted when forwarded to is_consonant; callers must be aware that the parameter name's meaning is "include fourths among dissonances" for this function (opposite of is_consonant's parameter).

## Returns:
    bool:
        - True if the ascending interval from note1 to note2 is considered dissonant according to is_consonant(...) negation with the inverted fourths flag.
        - False if the interval is considered consonant by the underlying is_consonant call.

    All possible return values:
        - True: the interval is not one of the consonant intervals recognized by is_consonant when called with (note1, note2, not include_fourths).
        - False: the interval is recognized as consonant by is_consonant(...).

## Raises:
    - This function does not raise its own exceptions but will propagate any exception raised by is_consonant or the utilities it uses (such as notes.note_to_int or the interval measurement helper).
    - Typical propagated exceptions:
        - ValueError (for unrecognized pitch strings)
        - TypeError (for invalid argument types)
        - Any module-specific parsing errors thrown by underlying utilities

## Constraints:
    Preconditions:
        - note1 and note2 must be acceptable inputs to the library's note parsing/measuring utilities.
        - include_fourths should be a boolean (Python truthy/falsy values are accepted but may be confusing).

    Postconditions:
        - No mutation of note1, note2, or global state occurs in this function.
        - A boolean is returned that is the logical negation of is_consonant(note1, note2, not include_fourths).

## Side Effects:
    - None intrinsic. No file, network, stdout, or global-state side effects are performed.
    - Any side effects would be a result of side effects in the underlying parsing/measurement utilities (which this function does not introduce).

## Control Flow:
flowchart TD
    Start[Start: receive note1, note2, include_fourths] --> InvertFlag[Compute forwarded_flag = not include_fourths]
    InvertFlag --> CallConsonant[Call is_consonant(note1, note2, forwarded_flag)]
    CallConsonant --> Negate[Return not (result of is_consonant)]
    Negate --> End[End: boolean dissonance result]

## Examples:
    Typical — perfect fifth (non-dissonant):
        is_dissonant("C", "G")
        # Returns: False  (perfect fifth is consonant → dissonant == False)

    Perfect fourth treated as consonant (default behavior):
        is_dissonant("C", "F")               # include_fourths defaults to False
        # Returns: False  (forwarded_flag = not False -> True -> is_consonant considers fourth consonant)

    Perfect fourth treated as dissonant:
        is_dissonant("C", "F", include_fourths=True)
        # Returns: True   (forwarded_flag = not True -> False -> is_consonant excludes fourth -> dissonant)

    Dissonant interval:
        is_dissonant("C", "C#")
        # Returns: True  (minor second -> not a consonance)

    Error handling example:
        try:
            result = is_dissonant("H", "C")   # "H" is not a valid pitch in many parsers
        except Exception as exc:
            # Underlying parsing/measurement will raise (e.g., ValueError); handle or propagate
            handle_error(exc)

