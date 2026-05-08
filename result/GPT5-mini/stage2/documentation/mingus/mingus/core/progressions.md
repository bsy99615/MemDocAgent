# `progressions.py`

## `mingus.core.progressions.to_chords` · *function*

## Summary:
Converts a Roman-numeral progression (single token or sequence of tokens) into concrete chords in the given key, returning a list where each element is a list of note-name strings for the corresponding chord.

## Description:
- Known callers:
    - No direct callers were discovered during repository scan. This function is a public utility intended for code that needs to translate Roman-numeral style progression tokens (for example "V", "bII7", "#IVmaj7") into concrete chord note lists in a specified key.

- Responsibility and rationale:
    - This routine centralizes the procedure of: lexically splitting a progression token (via parse_string), validating its Roman-numeral portion against the module-level numerals table, resolving a chord factory via the chords module, applying shorthand-quality transformations when needed, and finally applying net accidentals (sharps/flats) to the resulting chord tones.
    - Keeping this logic in a single function prevents duplication in callers that need Roman-numeral → chord translation and isolates error/edge-case handling (invalid numerals, accidental shifting, shorthand processing).

## Args:
    progression (str or iterable of str)
        - A single progression token (e.g., "V", "bII7", "#IVmaj7") or an iterable (e.g., list/tuple) of such tokens.
        - If a plain string is supplied, the function treats it as a single token and internally wraps it in a single-element list.
        - Each token is passed to parse_string, so tokens must be compatible with parse_string (recommended: use Python str; see parse_string documentation for exact lexical rules and its possible exceptions).
    key (str, optional)
        - Root key in which chords should be realized. Defaults to "C".
        - Expected to be a string acceptable to the chord factory functions in the chords module.

Interdependencies:
    - progression items must be strings (or sliceable/iterable types that parse_string accepts).
    - The function relies on a module-level numerals container: roman_numeral values returned by parse_string are checked against numerals; if not present the function returns an empty list immediately.
    - The function uses chord factory functions in the chords module (accessed via chords.__dict__[roman_numeral]) and a chords.chord_shorthand mapping for non-empty/non-"7" suffixes. The exact keys accepted by chords.__dict__ and chords.chord_shorthand are defined by the chords module and must match the roman_numeral and suffix values produced here.

## Returns:
    list[list[str]]
    - A list with one element per input token (unless the function returns early — see edge cases below). Each element is a list of note-name strings representing the chord obtained for that token, after shorthand application and accidental adjustments.
    - Edge/early returns:
        - If parse_string yields a roman_numeral that is not found in the module-level numerals container, the function returns [] immediately (an empty list), abandoning processing of any remaining tokens.
        - If progression was a single string, the returned list will contain a single chord list (or [] per the rule above).

## Raises:
- The function does not explicitly raise custom exceptions, but several built-in exceptions can be propagated from called operations:
    - TypeError / AttributeError
        - Can be raised by parse_string if progression items are not valid (see parse_string docs). For example, if progression is an iterable of non-string items, parse_string may attempt string operations and fail.
        - If progression is not iterable or its elements are not subscriptable/sliceable where required, TypeError can occur.
    - KeyError
        - May be raised when the function looks up a chord factory: chords.__dict__[roman_numeral] — if the constructed roman_numeral key does not exist in chords.__dict__.
        - May be raised when using chords.chord_shorthand[suffix] if the suffix returned by parse_string is not present in the chord_shorthand mapping.
    - IndexError
        - Can be raised by notes.augment or notes.diminish if they receive an empty-string note (these helper functions index the last character of each note string).
    - Any exceptions raised by the chord factory functions or shorthand functions themselves will propagate (for example, if those factories validate the key parameter and raise ValueError).

## Constraints:
Preconditions:
    - Prefer passing str tokens. The function expects to iterate and slice tokens; parse_string requires sliceable/iterable input (best practice: Python str).
    - The module-level numerals container must contain the Roman-numeral keys that will be produced by parse_string for valid tokens; otherwise the function returns [] for the first invalid token encountered.
    - The chords module must expose callable chord factories under chords.__dict__ with keys matching the (possibly suffixed) roman-numeral strings, and a chord_shorthand mapping for non-trivial suffix processing.

Postconditions:
    - Successful return is a list with the same number of elements as the input tokens (unless an early return happened because of an invalid roman numeral).
    - Each returned chord list contains strings (note names). Those strings have been post-processed by notes.diminish/notes.augment to reflect net accidentals computed from the token prefix.

## Side Effects:
    - No I/O, no global state mutation within this function.
    - Side-effects can occur indirectly if chord factory or shorthand callables mutate state or perform I/O — those behaviors depend on the chords module and are outside this function's implementation.
    - Uses only pure string/list transformations and calls into other modules; it does not write files, network, stdout, or alter module-level globals here.

## Control Flow:
flowchart TD
    Start --> NormalizeInput{Is progression a string?}
    NormalizeInput -- Yes --> Wrap[progression = [progression]] --> LoopStart
    NormalizeInput -- No --> LoopStart[For each chord token in progression]
    LoopStart --> Parse[(roman_numeral, acc, suffix) = parse_string(chord)]
    Parse --> CheckNumeral{roman_numeral in numerals?}
    CheckNumeral -- No --> ReturnEmpty[return []]
    CheckNumeral -- Yes --> SuffixCheck{suffix == "7" or suffix == ""?}
    SuffixCheck -- Yes --> AppendSuffix[roman_numeral += suffix] --> FactoryLookup1[r = chords.__dict__[roman_numeral](key)]
    SuffixCheck -- No --> FactoryLookup2[r = chords.__dict__[roman_numeral](key)] --> Shorthand[r = chords.chord_shorthand[suffix](r[0])]
    FactoryLookup1 --> AccApply
    Shorthand --> AccApply
    AccApply --> AccNeg{acc < 0?}
    AccNeg -- Yes --> DiminishLoop[r = [notes.diminish(x) for x in r]; acc += 1] --> AccNeg
    AccNeg -- No --> AccPos{acc > 0?}
    AccPos -- Yes --> AugmentLoop[r = [notes.augment(x) for x in r]; acc -= 1] --> AccPos
    AccPos -- No --> AppendResult[result.append(r)] --> NextToken
    NextToken --> LoopStart
    LoopStart --> End[return result]

## Examples:
Note: exact concrete chord note lists depend on the chord factory implementations in the chords module. The examples below show how to call the function and describe the expected structure of the result.

1) Single token (common case)
    - Call:
        to_chords("V", key="C")
    - Behavior:
        - parse_string("V") -> ("V", 0, "")
        - "V" is validated against numerals; chord factory chords.__dict__["V"] is invoked with key "C".
        - The returned value is wrapped in a list and returned, e.g. [[...note-name strings...]].
    - Typical (conventional) expectation:
        - In many chord libraries, "V" in key C yields a G-major triad, so a plausible return is [["G", "B", "D"]], but the exact spelling depends on the chords module conventions.

2) Token with accidentals and quality shorthand
    - Call:
        to_chords("bII7", key="F")
    - Behavior:
        - parse_string("bII7") -> ("II", -1, "7")
        - Since suffix == "7", roman_numeral becomes "II7" and the factory chords.__dict__["II7"](key) is called.
        - Each note name returned by the chord factory is diminished once (acc == -1), using notes.diminish.
        - Returns a list like [[...notes lowered by one semitone...]].

3) Multiple tokens
    - Call:
        to_chords(["I", "V", "#ivmaj7"], key="C")
    - Behavior:
        - Each token is parsed and resolved in order; the function returns a list with an element per token: [chord_for_I, chord_for_V, chord_for_#ivmaj7].
        - If any token produces a roman_numeral not in numerals, the function returns [] immediately.

4) Error propagation examples
    - If progression contains an element that parse_string cannot handle (e.g., non-string item), parse_string may raise TypeError or AttributeError which will propagate.
    - If a suffix is not present in chords.chord_shorthand, a KeyError will propagate.
    - If a note string supplied to notes.augment/diminish is empty, an IndexError may propagate.

## `mingus.core.progressions.determine` · *function*

## Summary:
Maps one or more chords to their scale-degree (Roman numeral) functions relative to a given key, returning either verbose names (e.g., "tonic", "dominant seventh") or compact shorthand (e.g., "I", "V7", "bii") depending on the shorthand flag.

## Description:
This function accepts a single chord (as a sequence of pitch identifier strings) or a list of chords and returns the scale-degree function(s) of those chords relative to the provided key.

Known callers within the codebase:
- No internal callers were discovered in the provided memory snapshot. Typical call sites are:
  - Progression-analysis utilities that convert chord lists into functional (Roman-numeral) representations.
  - Higher-level user code or tooling that analyzes chord progressions relative to a scale/key.
Typical trigger:
- Called when a caller has a chord (or list of chords) and a tonal key and wants to express each chord as a scale-degree function relative to that key (optionally in shorthand form). The function relies on chord analysis (chords.determine) to produce candidate chord names/types and on interval analysis (intervals.determine) to compute each chord's root interval from the key.

Why this logic is separated:
- Responsibility separation: it isolates the mapping from chord-name/type to scale-degree names (including verbose vs shorthand naming and accidentals) from the lower-level chord-recognition and interval-detection code.
- Reuse: callers can supply chords already produced by other code paths or a nested list of chords and always receive consistent functional names.
- Readability: this function centralizes the mapping rules (expected diatonic chord qualities, naming conventions, accidental prefixes) so the behavior is easier to reason about and test.

## Args:
    chord (sequence or list of sequences):
        - If a single chord: an ordered, indexable sequence of pitch identifier strings (for example ['C','E','G']).
        - If a list-of-chords: the function checks specifically if chord[0] is a Python list; when True the function treats the argument as a list of chords and returns a list of results (one per sub-chord).
        - Each chord candidate consumed inside the main loop is expected to be a string-like candidate returned by chords.determine (see behavior below). In practice that string begins with a root letter (A–G) optionally followed by accidentals ('b' or '#') and ends with a shorthand chord-type token (for example 'M', 'm', '7', 'm7b5').
        - Important: the function indexes chord[0] directly — passing an empty sequence will raise IndexError. Passing a nested chord must use list objects for the outer container to trigger the "list-of-chords" handling (tuples will not match).
    key (str):
        - A pitch identifier string used as the tonal reference (e.g., 'C', 'G#', 'F'). It is forwarded to intervals.determine(key, name). The function expects intervals.determine to return a two-word string like "major third" or "minor second".
    shorthand (bool, optional):
        - If True, produce compact (Roman-numeral) results with accidentals and appended shorthand qualifiers (for example: 'bii', '#IV7', 'V7').
        - If False, produce verbose English names (for example: 'minor supertonic', 'augmented subdominant', 'dominant seventh').
        - Default: False.
    Notes about interdependencies:
        - The function depends on chords.determine(chord, True, False, True) to produce candidate chord strings and on intervals.determine(key, name) to produce an interval description in the form "<interval_type> <interval>" (for example "minor third"). If those functions change their output format, this function will break.

## Returns:
    list[str] or list[list[str]]:
        - For a single chord input: returns a list of function name strings — one entry for each candidate returned by chords.determine. Each string is either a shorthand Roman-numeral token (when shorthand=True) possibly prefixed by an accidental shorthand ('b', '#', 'bb') or a verbose English phrase when shorthand=False (prefixed with 'minor ', 'augmented ', or 'diminished ' when the chord root interval type is non-major).
        - For a list-of-chords input (outer object is a list and chord[0] is list): returns a list whose elements are the return values for each sub-chord (i.e., a list of lists of strings).
        - Edge cases:
            * If chords.determine returns multiple candidate chord-strings, each candidate produces one result in the output list.
            * If chords.determine or intervals.determine return unexpected shapes or values, those propagate and affect the output (see Raises).
            * The function never returns a bare False or non-list unless one of the helper functions returns such a value and it propagates (this function always wraps computed names into Python lists before returning for the single-chord case).

## Raises:
    IndexError:
        - If the provided chord is an empty sequence (e.g., [] or ()), the function attempts to access chord[0] and will raise IndexError.
        - Note: a literal empty list ([]) will raise IndexError here because the function does not special-case empty sequences.
    TypeError / AttributeError:
        - If chord is None or a non-indexable object, attempts to index chord[0] will raise TypeError or AttributeError.
    Any exception propagated from called helpers:
        - chords.determine(...) exceptions (for example note-format validation errors) are not caught and propagate to the caller.
        - intervals.determine(key, name) exceptions are not caught and propagate to the caller.
        - KeyError may be raised when this function attempts to look up chords.chord_shorthand_meaning[chord_type] for an unexpected chord_type.
    Summary: this function does not wrap or convert exceptions from its dependencies; they surface unchanged.

## Constraints:
    Preconditions:
        - chord must be a non-empty, indexable sequence of valid note-name strings, or a list whose first element is itself a list of pitch identifier strings (for nested/multi-chord input).
        - key must be a valid pitch identifier accepted by intervals.determine.
        - chords.determine must produce candidate chord strings in the expected format (root letter, optional accidentals 'b'/'#', then a chord-type token).
    Postconditions:
        - The returned structure is either a flat list of function-name strings (single chord) or a list-of-lists of strings (nested input); the strings represent the function names derived for each candidate chord.
        - No global/module-level state is modified by this function.

## Side Effects:
    - None performed directly. The function performs no I/O and does not modify global variables.
    - Side effects can occur only by propagation from called functions (chords.determine, intervals.determine) if they have side effects or raise exceptions.

## Control Flow:
flowchart TD
    Start --> IsNested{is chord[0] a list?}
    IsNested -- Yes --> ForEachSub[for each sub-chord c in chord: append determine(c,key,shorthand)]
    ForEachSub --> ReturnNested[return list-of-results]
    IsNested -- No --> CallChords[call chords.determine(chord, True, False, True) -> type_of_chord]
    CallChords --> ForEachCandidate[for each candidate in type_of_chord]
    ForEachCandidate --> ParseRoot["extract name = candidate[0] and collect leading accidentals (b/#)"]
    ParseRoot --> ExtractType[chord_type = candidate[a:]]
    ExtractType --> IntervalCall[call intervals.determine(key, name) -> "<interval_type> <interval>"]
    IntervalCall --> MapDegree[map interval -> func (I, ii, iii, IV, V, vi, vii)]
    MapDegree --> MatchExpected[for each expected_chord entry matching func: compare chord_type]
    MatchExpected --> DetermineName[
        - if chord_type equals expected major/minor token -> keep base name (or verbose mapping)
        - elif chord_type equals expected 7-type -> append "7" (shorthand) or " seventh" (verbose)
        - else -> append chord_type (shorthand) or lookup verbose meaning via chords.chord_shorthand_meaning
    ]
    DetermineName --> AccidentalsPrefix[if shorthand: prefix 'b'/'#'/'bb' for minor/augmented/diminished; else prefix 'minor '/ 'augmented '/ 'diminished ']
    AccidentalsPrefix --> AppendResult[append final func string to result list]
    AppendResult --> LoopEnd{more candidates?}
    LoopEnd -- Yes --> ForEachCandidate
    LoopEnd -- No --> ReturnResult[return result list]
    ReturnResult --> End

## Examples:
    1) Single triad, verbose result
        try:
            result = determine(['C','E','G'], 'C', shorthand=False)
            # Typical result: ['tonic']
        except Exception as e:
            # handle invalid input or underlying helper errors
            raise

    2) Single triad, shorthand
        result = determine(['D','F#','A'], 'C', shorthand=True)
        # Typical result: ['V'] or ['V','...'] depending on chord recognition candidates returned by chords.determine

    3) Nested list (multiple chords)
        chords = [['C','E','G'], ['D','F','A']]
        result = determine(chords, 'C', shorthand=False)
        # Typical result: [['tonic'], ['supertonic']]  (one list per sub-chord)

    4) Empty-sequence error
        try:
            determine([], 'C')
        except IndexError:
            # caller must ensure non-empty chord sequences before calling
            pass

Notes:
- Exact returned strings depend on the outputs of chords.determine and intervals.determine; this function maps those outputs into Roman-numeral function names with a small set of rules (diatonic quality matching, seventh handling, and accidental prefixing). If either helper's return format changes, caller behavior will change accordingly.

## `mingus.core.progressions.parse_string` · *function*

## Summary:
Extracts a leading sequence of accidentals ('#' and lowercase 'b') and Roman-numeral letters ('I' and 'V') from the start of a progression string and returns a 3-tuple: (uppercase Roman-numeral prefix, net accidental count, remaining suffix).

## Description:
Scans the input left-to-right and, for each character, accepts and processes exactly three kinds of tokens until a non-matching character is encountered:
- '#' : increments the accidental counter,
- 'b' (lowercase only) : decrements the accidental counter,
- 'I' or 'V' (case-insensitive) : appended to the Roman-numeral prefix as uppercase.

The scanner does not require these tokens to appear in grouped segments; any ordering or interleaving of '#' , 'b', 'I', and 'V' at the start of the input will be consumed until a character outside those four accepted tokens appears. After stopping, the remainder of the input starting at that position is returned as the suffix.

Known callers:
- No direct callers were found during repository scan. The function is intended for use by higher-level progression or Roman-numeral parsing routines which need a lexical split between accidentals/roman prefix and the rest of the token (chord quality, extensions, bass, numerals, etc).

Responsibility boundary:
- Strictly a lexical/token extraction utility. It does not:
  - Validate or interpret Roman-numeral semantics beyond collecting 'I' and 'V';
  - Parse chord extension/quality syntax from the suffix;
  - Normalize or validate accidentals beyond counting '#' and 'b'.

## Args:
    progression (str or sequence of single-character strings)
        - The input to scan, typically a str, e.g. "#IVmaj7", "bII7", "V".
        - Required: the object must be iterable (for the for-loop) and support slicing (progression[i:]) — typical and intended type is str.
        - If the object is iterable but yields non-string items (for example, iterating a bytes object in Python 3 yields ints), the function will attempt to call .upper() on those items and that will raise AttributeError.

## Returns:
    tuple (roman_numeral: str, acc: int, suffix: str_or_sequence)
    - roman_numeral: uppercase string containing only 'I' and 'V' characters collected from the start of progression (may be empty).
    - acc: integer net accidental count = (# consumed) - (b consumed).
    - suffix: progression[i:], i being the index of the first non-accepted character; the remainder of the input (may be empty, or equal to progression if nothing was consumed).

All returns are always a 3-tuple. The exact type of suffix matches slicing behavior of the provided progression (for str input, suffix is a str).

## Raises:
    TypeError:
        - If progression is None or otherwise non-iterable: iterating in the for-loop will raise TypeError.
        - If progression is iterable but not subscriptable/sliceable (e.g., a generator): iteration may succeed but the final slicing progression[i:] will raise TypeError.
    AttributeError:
        - If elements yielded by progression do not support .upper() (for example, iterating a bytes object in Python 3 yields ints), the call to c.upper() will raise AttributeError.
    Note: The function itself does not explicitly raise these exceptions; they are the natural exceptions raised by operations used in the implementation.

## Constraints:
Preconditions:
    - Best practice: pass a str. The implementation expects to iterate characters and later slice by index.
    - Only the exact ASCII characters '#' and 'b' (lowercase) are treated as accidentals by this function. Uppercase 'B' is not treated as a flat.
    - Only letters 'I' and 'V' are recognized as Roman-numeral tokens; other Roman letters (e.g., 'X', 'L') are not recognized and will stop the scan.

Postconditions:
    - roman_numeral contains only 'I' and 'V' (uppercase) and corresponds to all such letters consumed at the start.
    - acc equals the count of '#' minus the count of 'b' among the consumed prefix.
    - suffix equals progression[i:] where i is the first index not consumed; if nothing consumed i == 0 and suffix == progression.

## Side Effects:
    - None. Pure string/sequence processing: no I/O, no global state mutation, no external calls.

## Control Flow:
flowchart TD
    Start --> Loop[For each character c in progression]
    Loop --> IsHash{c == '#'?}
    IsHash -- yes --> IncAcc[acc += 1; i += 1] --> Loop
    IsHash -- no --> IsFlat{c == 'b'?}
    IsFlat -- yes --> DecAcc[acc -= 1; i += 1] --> Loop
    IsFlat -- no --> IsRoman{c.upper() == 'I' or c.upper() == 'V'?}
    IsRoman -- yes --> Append[roman_numeral += c.upper(); i += 1] --> Loop
    IsRoman -- no --> ExitLoop[break]
    ExitLoop --> Suffix[suffix = progression[i:]] --> Return[return (roman_numeral, acc, suffix)]

## Examples:
- Input: "#IVmaj7"
  - Process: '#' -> acc=1; 'I','V' consumed -> roman_numeral="IV"; stops at 'm'.
  - Return: ("IV", 1, "maj7")

- Input: "bIV7"
  - Process: 'b' -> acc=-1; 'I','V' consumed -> roman_numeral="IV"; stops at '7'.
  - Return: ("IV", -1, "7")

- Input: "##i#Vdim"
  - Process (mixed order allowed): '#' -> acc=1; '#' -> acc=2; 'i' -> roman="I"; '#' -> acc=3; 'V' -> roman="IV"; stops at 'd'.
  - Return: ("IV", 3, "dim")

- Input: "7sus4"
  - Nothing consumed because '7' is not accepted.
  - Return: ("", 0, "7sus4")

- Input: "BIV"
  - Uppercase 'B' is not recognized as a flat; scanning stops immediately.
  - Return: ("", 0, "BIV")

- Input: "" (empty string)
  - Return: ("", 0, "")

- Error case: progression is a generator yielding characters of "#I"
  - The for-loop will consume characters, but suffix = progression[i:] will raise TypeError because generators do not support slicing.
  - Result: TypeError propagated.

Implementation note:
- To avoid AttributeError/TypeError, callers receiving arbitrary iterables should convert them to a str (e.g., ''.join(iterable)) before calling this function.

## `mingus.core.progressions.tuple_to_string` · *function*

## Summary:
Formats a progression element described as a (roman, acc, suff) tuple into a string by prefixing the roman core with the correct number of sharp ('#') or flat ('b') accidentals and appending the suffix.

## Description:
Converts a 3-tuple representation of a roman-numeral progression element into a human-readable string. The function expects:
- roman: the roman-numeral core (e.g., "I", "ii", "V"),
- acc: an integer representing the net accidental count (positive for sharps, negative for flats),
- suff: a trailing suffix string (e.g., "7", "maj7", or "").

Known callers:
- No direct internal callers were discovered in the available code scan. The function is a small formatting utility intended to be used wherever a progression element stored as (roman, acc, suff) must be rendered as text (presentation, export, debug output).

Why this is a separate function:
- Isolates presentation logic (normalization and accidental-prefixing) from progression construction/manipulation so callers need not repeat formatting rules. This improves reuse and testability.

## Args:
    prog_tuple (tuple): A 3-element iterable (roman, acc, suff)
        - roman (str): Base roman-numeral text.
        - acc (int): Net accidental count. Positive => sharps ('#'), negative => flats ('b').
        - suff (str): Suffix appended after the roman-numeral core.

Type/interaction notes:
- prog_tuple must be unpackable into exactly three values; otherwise Python raises TypeError.
- roman and suff are concatenated; they should be string-like. Passing non-string-like objects will raise TypeError upon concatenation.
- acc must support integer comparison and modulo operations; passing non-numeric types will raise TypeError.

## Returns:
    str: The formatted progression string composed as:
        [<accidentals>][roman][suff]
    where <accidentals> is:
        - For a positive effective acc: that many '#' characters
        - For a negative effective acc: that many 'b' characters (one per negative unit)
        - For zero effective acc: no accidental characters
    Normalization details:
        - If acc > 6, the function replaces acc with -(acc % 6).
        - If acc < -6, the function replaces acc with (acc % 6).
        - acc values between -6 and 6 (inclusive) are left unchanged.
        - After normalization the effective acc will be in the inclusive range [-6, 6].
        - If normalization yields 0, no accidentals are added.

## Raises:
    TypeError:
        - If prog_tuple cannot be unpacked into three values.
        - If acc does not support numeric comparisons or modulo operations.
        - If roman or suff cannot be concatenated with strings.
    Notes:
        - The function does not explicitly raise ValueError or custom exceptions. Any other runtime errors are Python's native exceptions triggered by invalid argument types.

## Constraints:
Preconditions:
    - prog_tuple is a 3-element iterable.
    - roman and suff should be strings (or types that concatenate with strings).
    - acc should be an integer (or numeric type behaving like an int for comparisons and modulo).

Postconditions:
    - Returns a str made of zero or more leading accidentals ('#' or 'b'), followed by roman, then suff.
    - Does not mutate prog_tuple or any external state.
    - The number of accidentals corresponds to the normalized accidental count (abs(acc) characters).

## Side Effects:
    - None. Pure formatting function: no I/O, no global state mutation, no external calls.

## Control Flow:
flowchart TD
    A[Start: receive prog_tuple] --> B[Unpack to (roman, acc, suff)]
    B --> C{acc > 6?}
    C -- Yes --> C1[acc = -(acc % 6)]
    C -- No --> D{acc < -6?}
    D -- Yes --> D1[acc = acc % 6]
    D -- No --> E[skip normalization]
    C1 --> E
    D1 --> E
    E --> F{acc < 0?}
    F -- Yes --> F1[roman = "b" + roman; acc = acc + 1] --> F
    F -- No --> G{acc > 0?}
    G -- Yes --> G1[roman = "#" + roman; acc = acc - 1] --> G
    G -- No --> H[Return roman + suff]

## Examples:
1) Two sharps with suffix:
    Input: ("V", 2, "7")
    Output: "##V7"

2) One flat, no suffix:
    Input: ("ii", -1, "")
    Output: "bii"

3) Preservation of -6 (no normalization applied for acc == -6):
    Input: ("IV", -6, "")
    Output: "bbbbbbIV"
    Explanation: acc == -6 is within [-6,6], so it is not normalized away.

4) Normalization of a large positive acc:
    Input: ("I", 7, "")
    Normalization: acc > 6 => acc = -(7 % 6) = -1
    Output: "bI"

5) Error case — invalid acc type:
    Input: ("I", "two", "")
    Behavior: TypeError raised when comparisons or modulo are attempted on acc.
    Suggested safe usage:
        try:
            formatted = tuple_to_string(("V", int(acc_value), suffix))
        except (TypeError, ValueError):
            handle_invalid_input()

## `mingus.core.progressions.substitute_harmonic` · *function*

## Summary:
Returns a list of Roman-numeral harmonic substitutions (as formatted strings) for a single element of a progression, preserving accidentals and optionally preserving or ignoring suffixes.

## Description:
This function inspects the progression element at the given index, lexically splits it into (roman, accidental count, suffix) using the project's parse_string utility, and — if the suffix condition is satisfied — produces alternative Roman-numeral roots according to a fixed set of simple harmonic substitution pairs. Each substitution is rendered as a string via tuple_to_string which prefixes accidentals and appends any preserved suffix.

Known callers:
- No direct callers were found in the repository scan. Typical use-case: invoked by progression transformation, generation, or analysis routines that generate alternate/harmonic substitutions for a single chord token (for example, when enumerating variant progressions or proposing reharmonizations).

Why this logic is extracted:
- Encapsulates the substitution rule set and the small decision logic about whether suffixes may be preserved. Keeps lexical parsing (parse_string), formatting (tuple_to_string), and the substitution rule-set separated for reuse and testability.

## Args:
    progression (sequence of str)
        - A sequence (list/tuple) or other indexable container of progression elements where each element is a string-like progression token (e.g., "I", "IV7", "#V", "bIImaj7").
        - Required: progression must support indexing (progression[substitute_index]) and the element at that index must be a string (or str-like) acceptable to parse_string.
    substitute_index (int)
        - Index into progression selecting the element to attempt substitutions for.
        - Must be a valid index for progression (otherwise IndexError will be raised).
    ignore_suffix (bool, optional) (default False)
        - When False (default), substitutions are only produced if the parsed suffix is empty or exactly "7".
        - When True, the function ignores any non-empty suffix and will attempt substitutions; in that case any preserved suffix will still only be "7" (non-"7" suffixes are not preserved — see Returns).

Interdependencies:
- The function depends on parse_string returning (roman, acc, suff). If parse_string raises, that error propagates.
- substitute_index must point to an element that parse_string can accept (typically a str). If it does not, parse_string or tuple_to_string may raise.

## Returns:
    list[str]
    - A list of formatted progression strings (the outputs of tuple_to_string) representing valid simple harmonic substitutions for the selected element.
    - Possible shapes:
        * Empty list: when no substitution applies (e.g., the element's Roman numeral is not present in the substitution pairs or the suffix is disallowed and ignore_suffix is False).
        * One or more strings: one per matching substitution (the current implementation yields at most two substitutions for numerals present in the mapping).
    - Suffix preservation behavior:
        * If the parsed suffix is exactly "7", substitutions preserve "7" on the result (e.g., "I7" -> "III7").
        * If the parsed suffix is empty, substitutions produce results without suffix.
        * If the parsed suffix is non-empty and not "7", and ignore_suffix is False, no substitutions are produced.
        * If ignore_suffix is True and the parsed suffix is non-"7", the produced substitutions use an empty suffix (non-"7" suffixes are discarded).

Examples of returned values (behavioral):
- progression = ["I", "IV", "V"], substitute_index = 0 -> ["III", "VI"]
- progression = ["I7"], substitute_index = 0 -> ["III7", "VI7"]
- progression = ["Imaj7"], substitute_index = 0, ignore_suffix=False -> []
- progression = ["Imaj7"], substitute_index = 0, ignore_suffix=True -> ["III", "VI"]
- progression = ["#I"], substitute_index = 0 -> ["#III", "#VI"] (accidental preserved via tuple_to_string)

## Raises:
    IndexError
        - If substitute_index is out of range for progression (raised by progression[substitute_index]).
    TypeError, AttributeError
        - If progression[substitute_index] is not a str-like object suitable for parse_string (parse_string may call .upper() and slice the value), those implementation-level exceptions propagate.
    TypeError (from tuple_to_string)
        - If tuple_to_string receives invalid types (e.g., non-string roman/suff or non-numeric acc) the resulting TypeError will propagate.
    Notes:
        - The function does not explicitly raise new custom exceptions; it allows natural exceptions from indexing, parse_string, or tuple_to_string to surface.

## Constraints:
Preconditions:
    - Callers should pass an indexable container and a valid integer index.
    - Best practice: ensure progression elements are Python str objects (or string-like) to avoid AttributeError from parse_string.

Postconditions:
    - The function does not mutate progression or any global state.
    - Returns a new list containing zero or more formatted substitution strings.

## Side Effects:
    - None. Pure computation and string construction. No I/O, no global state mutation, and no network access.

## Control Flow:
flowchart TD
    Start --> Index[Access progression[substitute_index]]
    Index --> Parse[parse_string(element) -> (roman, acc, suff)]
    Parse --> SuffixCheck{(suff == "" OR suff == "7" OR ignore_suffix == True)?}
    SuffixCheck -- No --> ReturnEmpty[return []]
    SuffixCheck -- Yes --> LoopStart[for each (a,b) in simple_substitutions]
    LoopStart --> Match1{roman == a?}
    Match1 -- Yes --> SetR[r = b]
    Match1 -- No --> Match2{roman == b?}
    Match2 -- Yes --> SetR[r = a]
    Match2 -- No --> Continue[continue loop]
    SetR --> NormalizeSuffix[suff = suff if suff == "7" else ""]
    NormalizeSuffix --> Format[tuple_to_string((r, acc, suff))]
    Format --> Append[append formatted result to res]
    Append --> Continue
    Continue --> LoopEnd[after loop]
    LoopEnd --> Return[return res]

## Examples:
1) Basic substitutions (no suffix)
    - Input:
        progression = ["I", "IV", "V"]
        substitute_index = 0
    - Behavior: "I" matches pairs ("I","III") and ("I","VI"); returns ["III", "VI"]

2) Preserve 7-type suffix
    - Input:
        progression = ["I7"]
        substitute_index = 0
    - Behavior: suff == "7" so preserved; returns ["III7", "VI7"]

3) Ignore non-7 suffix (default)
    - Input:
        progression = ["Imaj7"]
        substitute_index = 0
        ignore_suffix = False
    - Behavior: suff == "maj7" (not allowed) -> returns []

4) Force substitutions, dropping non-7 suffix
    - Input:
        progression = ["Imaj7"]
        substitute_index = 0
        ignore_suffix = True
    - Behavior: produces substitutions but discards the "maj7" suffix -> ["III", "VI"]

5) Error handling example
    - Example call:
        try:
            subs = substitute_harmonic(progression, idx)
        except IndexError:
            handle_invalid_index()
        except (TypeError, AttributeError):
            handle_invalid_element()

## `mingus.core.progressions.substitute_minor_for_major` · *function*

*No documentation generated.*

## `mingus.core.progressions.substitute_major_for_minor` · *function*

*No documentation generated.*

## `mingus.core.progressions.substitute_diminished_for_diminished` · *function*

## Summary:
Produces up to three diminished-chord substitutions for a single progression element by walking forward two scale steps three times, adjusting accidentals so each generated roman numeral is the required interval from the previous degree, and formatting each result as a progression string.

## Description:
- Known callers:
    - No direct callers were discovered in the scanned repository snapshot. This function is intended to be used by higher-level progression transformation code that wants to substitute or expand a diminished chord into the sequence of diminished chords that follow it by degree-skipping.
- Why this is a separate function:
    - Encapsulates the specific substitution rule "replace a diminished (or a VII with empty suffix) by the sequence of the next three diminished degrees computed by skipping two scale steps repeatedly". It isolates parsing, degree-advancement, semitone-adjustment, and string-formatting so callers can request this substitution without duplicating the loop, accidental accumulation, or suffix-handling logic.

## Args:
    progression (Sequence[str]):
        - An indexable sequence (e.g., list or tuple) of progression element strings.
        - Each element will be passed to parse_string; typical elements look like "#IVmaj7", "V7", "VII", "ii(dim)" but may be any string.
        - The function does NOT accept an un-sliceable generator for progression because the code uses progression[substitute_index].
    substitute_index (int):
        - Index into progression specifying the element to substitute.
        - Must be a valid index for progression; otherwise IndexError is raised.
    ignore_suffix (bool, optional):
        - Default False.
        - When True, the function will perform the substitution regardless of the parsed suffix on the target element (i.e., bypasses the usual requirement that suffix indicate a diminished quality or that the roman numeral be VII when suffix is empty).

Notes on interdependencies:
    - progression[substitute_index] is parsed by parse_string into (roman, acc, suff); the returned roman and acc are used as the starting state for generating substitutions.
    - The ignore_suffix flag affects whether the substitution is attempted, but it does not change the parsed suff value (except when suff == "" — see behavior).

## Returns:
    list[str]:
        - A list containing zero or three formatted progression strings (as produced by tuple_to_string).
        - If the target element does not meet the condition for substitution (see Conditions below), the function returns an empty list [].
        - When substitution occurs, the function returns exactly three items in order: each is the string form of a generated diminished-degree chord produced by advancing the roman numeral by two scale steps repeatedly and accumulating accidental adjustments.
        - Returned strings include any accidentals (sharp '#' or flat 'b') and the suffix (usually "dim" or "dim7") as produced by tuple_to_string.

## Raises:
    IndexError:
        - If substitute_index is out of range for progression (raised by progression[substitute_index]).
    TypeError, AttributeError:
        - May be raised by parse_string if progression elements are not valid string-like inputs (e.g., non-iterable, or elements that do not support .upper()).
    ValueError:
        - May be raised by skip if the parsed roman numeral is not found in the module-level numerals sequence.
        - May be raised by interval_diff if its inputs are not present in the expected module-level sequences (see its doc).
    TypeError:
        - May be raised by tuple_to_string if its tuple elements are of incompatible types (non-string roman/suffix or non-integer acc), or by other helper calls when invalid types are encountered.
    Notes:
        - The function itself does not explicitly raise custom exceptions; the above exceptions propagate from the helper functions and standard operations used internally.

## Constraints:
Preconditions:
    - progression must be indexable and contain string-like progression elements.
    - substitute_index must be a valid integer index into progression.
    - The module-level helper data structures that parse_string, skip, and interval_diff rely on (e.g., numerals and numeral_intervals) must be correctly defined and populated in the same module.
    - Typical caller expectation: the element at progression[substitute_index] represents a roman-numeral style token optionally prefixed by accidentals and followed by a suffix.

Postconditions:
    - The returned list is either empty (no substitution performed) or contains exactly three formatted progression strings.
    - The function does not mutate the input progression sequence or global state.

## Side Effects:
    - None intrinsic: no I/O, no global mutation, no network or external service calls.
    - Side-effects may occur indirectly if helper functions raise exceptions due to misconfigured module-level state; such exceptions propagate outward.

## Behavior / Conditions
- Parsing:
    - The function parses the target element: (roman, acc, suff) = parse_string(progression[substitute_index]).
- Substitution condition (boolean expression evaluated as in Python):
    - Substitution proceeds only if any of the following is True:
        1) suff == "dim7"
        2) suff == "dim"
        3) suff == "" and roman in ["VII"]
        4) ignore_suffix is True
    - Note on operator precedence: the code uses Python's normal precedence so the third clause is (suff == "" and roman in ["VII"]) — an empty suffix alone does not trigger substitution unless the roman numeral is "VII".
- If substitution proceeds:
    - If suff == "" it is set to "dim" before generation.
    - The algorithm sets last = roman and repeats the following three times:
        1) next = skip(last, 2)  # advance two scale steps (wraps modulo 7)
        2) delta = interval_diff(last, next, 3)  # semitone adjustment needed so that next is a minor third (3 semitones) above last
        3) acc += delta  # accumulate net accidental shift for the new degree
        4) res.append(tuple_to_string((next, acc, suff)))  # format and collect the new chord string
        5) last = next
    - The function returns the list res.

## Control Flow:
flowchart TD
    Start([start]) --> Parse[Parse target: (roman, acc, suff) = parse_string(progression[substitute_index])]
    Parse --> Cond{(suff == "dim7") OR (suff == "dim") OR (suff == "" AND roman == "VII") OR ignore_suffix?}
    Cond -- No --> EndEmpty[Return []]
    Cond -- Yes --> SetSuff{Is suff == ""?}
    SetSuff -- Yes --> AssignSuff[suff = "dim"]
    SetSuff -- No --> Continue
    AssignSuff --> LoopInit[Set last = roman; res = []]
    Continue --> LoopInit
    LoopInit --> For[for x in range(3):]
    For --> ComputeNext[next = skip(last, 2)]
    ComputeNext --> ComputeDelta[delta = interval_diff(last, next, 3)]
    ComputeDelta --> UpdateAcc[acc += delta]
    UpdateAcc --> Append[res.append(tuple_to_string((next, acc, suff)))]
    Append --> UpdateLast[last = next]
    UpdateLast --> For
    For --> ReturnRes[Return res (3 items)]
    EndEmpty --> ReturnResEmpty[Return []]

## Examples:
1) Typical substitution (conceptual):
    - Input: progression = ["I", "V", "VII"], substitute_index = 2
    - parse_string("VII") -> ("VII", 0, "")
    - Condition true because suff == "" and roman == "VII"
    - After substitution returns a list of three strings, e.g. ["<accidentals>II dim", "<accidentals>IV dim", "<accidentals>VI dim"]
    - Exact accidentals depend on the module's numeral-to-semitone mapping; tuple_to_string determines how many '#' or 'b' are prefixed.

2) Forcing substitution regardless of suffix:
    - If progression[substitute_index] has a non-diminished suffix but the caller still wants the diminished chain:
        result = substitute_diminished_for_diminished(prog, idx, ignore_suffix=True)
      This will attempt the substitution even if suff is not "dim"/"dim7" (the existing suffix is preserved unless it was empty).

3) Error handling example:
    try:
        replacements = substitute_diminished_for_diminished(prog, idx)
    except IndexError:
        # invalid substitute_index
        handle_bad_index()
    except ValueError:
        # could be raised by skip or interval_diff if roman not in numerals or numerals misconfigured
        handle_configuration_error()
    else:
        # replacements is either [] or a list of three formatted strings
        apply_replacements_if_nonempty(replacements)

Implementation notes for re-creation:
    - Use parse_string to split the progression token into roman, acc, suff.
    - Respect Python's boolean operator precedence when evaluating the combined conditions.
    - Use skip(last, 2) to advance degrees with wrap-around and interval_diff(last, next, 3) to compute semitone adjustments so the new degree is a minor third (3 semitones) above the previous.
    - Accidental accumulation is performed in-place (acc is updated each iteration) so each generated chord uses the cumulative accidental adjustments up to that point.

## `mingus.core.progressions.substitute_diminished_for_dominant` · *function*

## Summary:
Given a progression and an index into it, compute a list of dominant-seventh chord strings that serve as substitutes for a diminished/dim7 chord at that index; returns an empty list if substitution is not applicable.

## Description:
This utility inspects the progression element at progression[substitute_index], lexically parses it into (roman, acc, suff), and — when that element is a diminished chord (suffix "dim" or "dim7"), a bare VII (no suffix with roman == "VII"), or when ignore_suffix is True — generates a four-chord sequence of dominant-seventh substitutions. Each produced element is formatted as a progression string (using the tuple_to_string formatting rules) with suffix "dom7" and an accidental adjustment computed so the dominant is 8 semitones above the originating diminished root.

Known callers:
- Higher-level progression-transformation or reharmonization code which replaces diminished chords with their dominant7 substitutes prior to chord realization or voice-leading. (No direct callers were discovered in the provided scan; typical usage is in pipelines that rewrite a progression's elements.)

Why this is factored out:
- The logic isolates the specific rule "substitute a diminished (or VII) chord by the chain of four dom7s" into one place so callers need only decide where substitution is desired. It encapsulates:
  - lexical parsing of the progression element,
  - the eligibility test for substitution,
  - the four-step generation of relative degrees (using skip),
  - accidental computation (using interval_diff) and final string formatting (using tuple_to_string).
This keeps higher-level code simpler and avoids duplicating the domain-specific degree-navigation and accidental-calculation logic.

## Args:
    progression (sequence[indexable], required)
        - A sequence (typically list of str) of progression element strings.
        - Must support indexing (progression[substitute_index]) and must supply an element acceptable to parse_string (best provided as a str).
        - If a non-indexable iterable (e.g., generator) is passed, an IndexError/TypeError will be raised when attempting to index/slice.
    substitute_index (int, required)
        - Index into progression identifying the element to examine for substitution.
        - Negative indices are allowed per normal Python indexing semantics.
        - If the index is out of range, Python's IndexError will be raised.
    ignore_suffix (bool, optional; default False)
        - When False (default) the function only considers an element substitutable if its parsed suffix is "dim" or "dim7", or if the suffix is empty and the roman core equals "VII".
        - When True the function will perform substitution regardless of the element's suffix (useful for forcing substitutions in transformations).

Interdependencies:
- The function depends on module-level helpers parse_string, skip, interval_diff, and tuple_to_string. Callers and implementers must respect the documented preconditions of those helpers:
    * parse_string expects a string-like token and returns (roman, acc, suff).
    * skip assumes a module-level sequence numerals exists, that numerals contains the given roman token, and that numerals models the seven scale degrees (skip uses modulo 7 wrap-around). Note: the skip implementation's doc stated it had no direct callers in the scanned snapshot; substitute_diminished_for_dominant is one such caller in this codepath.
    * interval_diff requires that the module-level sequences numerals and numeral_intervals are defined and aligned (numerals.index(...) must be valid and the corresponding indices must exist within numeral_intervals) and that the requested interval argument is an integer.
    * tuple_to_string expects to receive a 3-tuple (roman, acc, suff) where roman and suff are string-like (concatenable) and acc is integer-like.
- Practical requirements for safe operation:
    * numerals should be a 7-element sequence of string-like roman tokens (e.g., ['I','II','III','IV','V','VI','VII']), because skip uses modulo 7 and expects to index into numerals.
    * numeral_intervals should be an index-aligned sequence of integer semitone values corresponding to numerals.
    * The dom values returned by skip should be string-like so tuple_to_string can concatenate them with suffix "dom7".
    * interval_diff must yield an integer-like adjustment; combined with parsed acc (an integer) produces an integer 'a' passed to tuple_to_string.

## Returns:
    list[str]
    - A list of zero or more progression strings produced by tuple_to_string. Typical successful result length is 4 (a four-element sequence of dominant-seventh substitutions).
    - If the input element is not eligible for substitution (see eligibility rules below), the function returns an empty list [].
    - Each returned string represents a dominant-seventh chord built from:
        * dom = skip(last, 5)  (the dominant relative to the current degree)
        * a = interval_diff(last, dom, 8) + acc  (accidental adjustment)
        * suffix "dom7"
      and then formatted through tuple_to_string((dom, a, "dom7")).
    - The order of returned chords follows successive steps where last advances with skip(last, 2) for four iterations (i.e., a length-4 chain starting from the parsed roman).

Eligibility rules (when the function generates substitutions):
    - ignore_suffix is True, OR
    - parsed suffix equals "dim7", OR
    - parsed suffix equals "dim", OR
    - parsed suffix is the empty string AND parsed roman equals "VII".

Note on empty-suffix handling:
- When the parsed suffix is empty and the roman is "VII", the function sets suff = "dim" internally before proceeding (this mainly documents the intent to treat bare VII as diminished); the suff variable is not otherwise used in construction of the returned dom7 strings.

## Raises:
    - IndexError:
        - If substitute_index is out of range when indexing progression.
    - TypeError:
        - If parse_string is given a non-string-like progression element, it may raise AttributeError/TypeError.
        - If numerals contains non-string elements, tuple_to_string may raise TypeError when it attempts to concatenate roman or suff with strings.
        - If acc ('a') is not integer-like, tuple_to_string may raise TypeError during numeric operations or normalization.
    - ValueError / IndexError:
        - Values propagated from skip or interval_diff if roman is not in numerals or if numeral_intervals is inconsistent.
    - The function does not raise new custom exceptions; instead it allows underlying helper exceptions to propagate so callers can detect and handle malformed inputs or misconfigured module state.

## Constraints:
Preconditions:
    - Module-level names and sequences used by helpers must be present and consistent:
        * numerals must be defined and should contain seven string-like roman tokens representing scale degrees.
        * numeral_intervals must be defined and contain integer semitone values aligned with numerals.
    - progression must be indexable and contain string-like tokens acceptable to parse_string.
    - substitute_index must be an integer (or an object coercible to a standard sequence index) referencing a valid element.

Postconditions:
    - The original progression sequence is not modified.
    - If substitution occurred, the function returns a list of four formatted dom7 strings computed from the parsed roman and accidental base; if not eligible, returns [].
    - No global state is changed by this function.

## Side Effects:
    - None intrinsic to this function: no I/O, no mutation of global state, no network or database calls.
    - Note: side effects of helper functions (if any) would also apply, but in normal implementation these helpers are pure and have no side effects.

## Control Flow:
flowchart TD
    Start --> Index[Read progression[substitute_index]]
    Index --> Parse[Call parse_string(element) -> (roman, acc, suff)]
    Parse --> Eligibility{ignore_suffix == True?}
    Eligibility -- yes --> Generate[Proceed to generate substitutions]
    Eligibility -- no --> CheckDim{ suff == "dim7" or suff == "dim" or (suff == "" and roman == "VII")? }
    CheckDim -- no --> ReturnEmpty[Return []]
    CheckDim -- yes --> IfEmptySetDim{ if suff == "" then suff = "dim" } --> Generate
    Generate --> LoopStart[Set last = roman; x = 0]
    LoopStart --> ForLoop{x in 0..3}
    ForLoop --> ComputeNext[next = skip(last,2)]
    ComputeNext --> ComputeDom[dom = skip(last,5)]
    ComputeDom --> ComputeAcc[a = interval_diff(last, dom, 8) + acc]
    ComputeAcc --> Format[s = tuple_to_string((dom, a, "dom7"))]
    Format --> Append[res.append(s)]
    Append --> UpdateLast[last = next]
    UpdateLast --> ForLoop{increment x}
    ForLoop -- done --> ReturnRes[return res]
    ReturnEmpty --> ReturnRes

## Examples:
1) Forced substitution (ignore suffix)
    - Given progression = ["I", "ii", "V", "VII"], substitute_index = 3, ignore_suffix = True
    - The function parses progression[3] -> ("VII", acc, suff)
    - It will compute four dom7 substitution strings (for the sequence of dom degrees derived from advancing "VII")
    - Return value example (structure only): ["<accidentals?>Vdom7", "<accidentals?>VII dom7", "<accidentals?>IIdom7", "<accidentals?>IVdom7"]
      (actual accidental prefixes depend on numeral_intervals and the computed a values; tuple_to_string produces the final formatted strings.)

2) Typical use where the element is explicitly diminished:
    - progression = ["I", "V", "#Vdim", "vi"], substitute_index = 2, ignore_suffix = False
    - parse_string("#Vdim") -> ("V", 1, "dim")
    - Condition holds because suff == "dim", so the function generates substitutions for a diminished V and returns a 4-element list of dom7 formatted strings for the derived dominants.

3) No substitution:
    - progression = ["I", "ii7", "V7"], substitute_index = 1, ignore_suffix = False
    - parse_string("ii7") -> ("II", acc, "7") -> suff is "7" which is not "dim"/"dim7" and roman is not "VII" with empty suffix -> function returns [].

4) Error handling example:
    - If progression[substitute_index] is not a string-like object (for example, None), parse_string will raise TypeError or AttributeError and that exception will propagate to the caller. Callers should validate progression contents before invoking if input provenance is uncertain.

Implementation notes for re-creation:
    - Preserve the precise logical condition used to decide eligibility:
        suff == "dim7" OR suff == "dim" OR (suff == "" AND roman == "VII") OR ignore_suffix
      (remember Python's operator precedence: 'and' binds tighter than 'or'.)
    - Use the helpers exactly as:
        (roman, acc, suff) = parse_string(progression[substitute_index])
        next = skip(last, 2)
        dom = skip(last, 5)
        a = interval_diff(last, dom, 8) + acc
        res.append(tuple_to_string((dom, a, "dom7")))
    - This function supplies a literal suffix "dom7" (a string) to tuple_to_string; ensure numerals provides string-like roman tokens and that interval_diff yields integer-like accidental values to avoid TypeError in formatting.
    - The function must not mutate the input progression and should return the list of formatted strings (possibly empty).

## `mingus.core.progressions.substitute` · *function*

## Summary:
Generates possible Roman-numeral chord substitutions for a single element of a progression and (optionally) expands those substitutions recursively to a specified depth.

## Description:
This routine inspects progression[substitute_index], parses it into (roman, acc, suff) and applies a set of deterministic substitution rules to produce alternative progression-element strings. Rules include a fixed table of simple degree swaps, suffix-dependent transformations for major/minor/seventh/diminished chords, and a diminished-chain expansion. If depth > 0 the function will recursively substitute into the progression for each generated alternative and return the concatenation of direct and recursive substitutions.

This function directly invokes module-local helper utilities: parse_string, tuple_to_string, skip, and interval_diff to parse input tokens, format output tokens, navigate Roman-numeral degrees, and compute semitone adjustments. Note: separate documentation summaries for those helper utilities in the repository snapshot stated that a code scan found "no direct callers" for them; that statement reflects the scan results in the snapshot and does not contradict the fact that substitute calls them — substitute is a direct caller.

Known callers:
- No direct internal callers of substitute were found in the provided repository snapshot. It is intended for use by higher-level reharmonization, transformation, or enumeration utilities that need to list alternative chords for a given Roman-numeral element.

Why this is a separate function:
- Encapsulates substitution logic (rule table, suffix-driven transforms, interval computations, and optional recursion) so callers do not have to reimplement parsing, interval lookups, formatting, or recursion mechanics.

## Args:
    progression (sequence of str)
        - A sequence (commonly a list) of progression element strings (e.g., "I", "bII7", "#V7", "vi").
        - Must be indexable (support progression[substitute_index]).
        - IMPORTANT: If depth > 0 the implementation assigns into the sequence (new_progr = progression; new_progr[substitute_index] = x) before recursing. Therefore progression must be mutable (support item assignment) if you intend to allow the recursion to run without error; otherwise a TypeError will occur. To avoid mutating the caller's original list, pass a shallow copy (e.g., progression.copy()) when calling with depth > 0.
        - Elements must be strings acceptable to parse_string and tuple_to_string.

    substitute_index (int)
        - The index (Python indexing semantics) of the element to substitute.
        - Negative indices are supported per standard Python behavior.
        - Accessing an out-of-range index will raise IndexError.

    depth (int, optional; default=0)
        - Controls recursive substitution expansion.
        - Behavior:
            * depth <= 0 : no recursion performed (depth == 0 is default).
            * depth > 0  : for each direct substitution x, the function assigns x into the progression at substitute_index and calls substitute(new_progr, substitute_index, depth - 1), concatenating results.
        - Non-integer or non-numeric depths may raise TypeError during comparisons/recursion.

Interdependencies / notes:
    - The function calls helper functions parse_string, tuple_to_string, skip, interval_diff. Exceptions and behaviors of those helpers (ValueError, TypeError, etc.) may propagate.
    - The implementation performs exact string equality checks on specific suffix tokens (see "Implementation details" below); it does not perform fuzzy or case-insensitive matching for these suffixes.

## Returns:
    list[str]
        - A list of progression-element strings produced by tuple_to_string applied to generated (roman, acc, suff) triples.
        - Order: the function appends results in the order rules are applied:
            1. Simple-substitution matches (for suff == "" or "7") — each match yields a "" variant and also a "7" or no-"7" counterpart depending on r[-1] == "7".
            2. If suff in ["", "M", "m"] a suff+"7" variant for the same roman is appended.
            3. For m/m7 → relative major variants (skip(roman, 2)) with "M" and "M7".
            4. For M/M7 → relative minor variants (skip(roman, 5)) with "m" and "m7".
            5. For dim/dim7 → several dom7 and chained-diminished variants appended in sequence.
            6. If depth > 0, recursive results for each item above are concatenated after the direct results.
        - The list may contain duplicates (the function does not deduplicate).
        - The list may be empty if no rules produce substitutes for the parsed suffix.

## Raises:
    IndexError:
        - If substitute_index is invalid when accessing progression[substitute_index].

    TypeError:
        - If progression is not subscriptable or its elements are not string-like for parse_string/tuple_to_string.
        - If progression is immutable (e.g., a tuple) and depth > 0, the assignment new_progr[substitute_index] = x will raise TypeError.

    ValueError / IndexError / TypeError from helpers:
        - skip may raise ValueError if the parsed roman is not present in numerals.
        - interval_diff may raise ValueError or IndexError if numeral mappings are inconsistent.
        - tuple_to_string may raise TypeError for invalid tuple contents.
        - parse_string may raise TypeError/AttributeError for non-string-like elements.
        - These are not raised explicitly by substitute but will propagate.

## Constraints:
Preconditions:
    - progression must be indexable.
    - Elements must be strings parseable by parse_string.
    - If depth > 0 and you do not want the original progression mutated, pass a shallow copy (e.g., progression.copy()).

Postconditions:
    - The original sequence may be mutated if depth > 0 because the implementation assigns into progression before recursive calls. The function returns a new list; it does not explicitly return the (possibly mutated) progression.

## Implementation details relevant to re-creation:
    - Exact suffix tokens checked in the source code (all comparisons are exact string equality):
        * ""  (empty string)
        * "7"
        * "M"
        * "m"
        * "m7"
        * "M7"
        * "dim"
        * "dim7"

    - simple_substitutions table used when suff == "" or "7":
        [("I","III"),("I","VI"),("IV","II"),("IV","VI"),
         ("V","VII"),("V","VIIdim7"),("V","IIdim7"),
         ("V","IVdim7"),("V","bVIIdim7")]

    - When building simple-substitution results:
        * If roman equals one side of a tuple, r is set to the other side.
        * The code appends tuple_to_string((r, acc, "")).
        * Then:
            - If r[-1] != "7": append tuple_to_string((r, acc, "7"))
            - Else: append tuple_to_string((r[:-1], acc, ""))  (removes trailing '7' from r and uses empty suffix)

    - For the dim/dim7 branch:
        * The local variable acc is mutated inside a loop:
            - last = roman
            - repeat 4 times:
                next = skip(last, 2)
                acc += interval_diff(last, next, 3)
                append tuple_to_string((next, acc, suff))
                last = next
        * This means the acc value used for each appended diminished-chain element is cumulative: each iteration modifies acc for subsequent iterations. Reimplementations must preserve this in-place accumulation to match outputs exactly.

    - Recursive expansion:
        * For depth > 0, the code iterates the direct results res, and for each x:
            new_progr = progression
            new_progr[substitute_index] = x
            res2 += substitute(new_progr, substitute_index, depth - 1)
        * Two critical implications:
            - new_progr is an alias to progression (not a copy); the assignment mutates progression in-place.
            - Recursive calls therefore see and operate on the mutated progression; this behavior must be preserved to reproduce results.

## Side Effects:
    - Potential in-place mutation of progression when depth > 0 (assignment to progression[substitute_index]).
    - No I/O, no network, and no global state modifications performed directly by this function.

## Control Flow:
flowchart TD
    Start --> ReadP[Read p = progression[substitute_index]]
    ReadP --> Parse[parse_string(p) -> (roman, acc, suff)]
    Parse --> CheckSimple{suff == "" or "7"?}
    CheckSimple -- yes --> ForEachSimple[iterate simple_substitutions]
    ForEachSimple --> Match{roman == subs[0] or subs[1]?}
    Match -- match --> SetR[r = counterpart]
    SetR --> Append1[append tuple_to_string((r, acc, ""))]
    Append1 --> IfR7{r[-1] != "7"?}
    IfR7 -- yes --> append (r, acc, "7")
    IfR7 -- no --> append (r[:-1], acc, "")
    Match -- no --> continue loop
    AfterSimple --> CheckAdd7{suff in ["", "M", "m"]?}
    CheckAdd7 -- yes --> append (roman, acc, suff+"7")
    Parse --> CheckMinor{ suff in ["m","m7"]? }
    CheckMinor -- yes --> n = skip(roman,2); a = interval_diff(roman,n,3)+acc; append (n,a,"M") append (n,a,"M7")
    Parse --> CheckMajor{ suff in ["M","M7"]? }
    CheckMajor -- yes --> n = skip(roman,5); a = interval_diff(roman,n,9)+acc; append (n,a,"m") append (n,a,"m7")
    Parse --> CheckDim{ suff in ["dim","dim7"]? }
    CheckDim -- yes --> append (skip(roman,5), acc, "dom7")
    CheckDim --> n = skip(roman,1); append (n, acc + interval_diff(roman,n,1), "dom7")
    CheckDim --> DimLoop[for x in 0..3: next = skip(last,2); acc += interval_diff(last,next,3); append (next, acc, suff); last = next]
    AfterAll --> DepthCheck{depth > 0?}
    DepthCheck -- no --> Return res
    DepthCheck -- yes --> ForEachRes[for each x in res: new_progr = progression; new_progr[substitute_index] = x; res2 += substitute(new_progr, substitute_index, depth-1)]
    ForEachRes --> Return res + res2

## Examples:
1) Basic (no recursion)
    progression = ["I", "IV", "V"]
    substitute_index = 2
    depth = 0
    - p = "V" -> roman="V", acc=0, suff=""
    - Produces simple-substitution outputs for "V" (see simple_substitutions table) formatted via tuple_to_string.
    - Example result (format depends on tuple_to_string): ["VII", "VII7", "VIIdim7", "IIdim7", "IIdim7", "IVdim7", "IVdim7", "bVIIdim7", ...]

2) Add seventh to basic chord
    progression = ["I", "IV", "V"]
    substitute_index = 0
    depth = 0
    - If p parses with suff == "" then a variant with suff+"7" (i.e., "I7") is appended.

3) Minor → relative major variants
    progression = ["m", "IV", "V"]
    substitute_index = 0
    depth = 0
    - If p parses as roman with suff "m" or "m7": skip(roman, 2) is used to find the relative major degree; interval_diff is used to compute accidentals; "M" and "M7" variants are appended.

4) Recursion and mutation warning
    progression = ["I", "V", "vi"]
    substitute_index = 1
    depth = 1
    - Because depth > 0 the function mutates progression in-place when assigning new_progr[substitute_index] = x before recursive calls.
    - To avoid mutating the caller's progression, invoke with a shallow copy:
        safe_results = substitute(progression.copy(), substitute_index, depth=1)

5) Negative or non-positive depth
    - If depth <= 0 the function performs no recursion (equivalent to depth == 0).

Error-handling example:
    try:
        substitutes = substitute(prog_list, idx, depth=1)
    except (IndexError, TypeError, ValueError) as e:
        # handle the condition (out-of-range index, bad input types, helper failures)
        handle_error(e)

## `mingus.core.progressions.interval_diff` · *function*

## Summary:
Computes the signed number of semitone adjustments needed to make the interval from progression1 to progression2 equal to a target interval.

## Description:
This function:
- Looks up numeric interval values for two progression numerals via two module-level sequences (used here as: numerals and numeral_intervals).
- Computes how many semitone steps to apply to the second progression's interval value so that the difference (progression2 - progression1) equals the desired interval.
- Returns a signed integer: positive when progression2 must be raised (in semitones) and negative when it must be lowered.

Known callers within the scanned component source:
- No direct callers were discovered within the provided snippet. The function is implemented as a small utility that other progression-manipulation routines would call when they need to normalize or adjust scale-degree intervals.

Why this logic is factored into its own function:
- Encapsulates the algorithm that turns two numeral identifiers and a target semitone-distance into a discrete adjustment count.
- Keeps numeral lookup and incremental adjustment logic localized so other code can request "how many semitones must progression B move to be X semitones above progression A" without duplicating loop/normalization logic.

## Args:
    progression1 (any hashable/indexable value): An element that appears in the module-level sequence `numerals`. The function calls numerals.index(progression1) so the argument must be present in that sequence; typical values are strings or symbols representing scale degrees (e.g., 'I', 'V'), but the implementation only requires indexability/membership.
    progression2 (same type as progression1): An element present in `numerals`; used to lookup its base semitone value in `numeral_intervals`.
    interval (int): The desired difference in semitones (an integer). The function treats this as an exact target value for the numeric difference j - i.

Notes on parameter interdependencies:
- progression1 and progression2 must both be found in the same `numerals` sequence; the function uses their indices into that sequence to index `numeral_intervals`.
- The elements of `numeral_intervals` are expected to be numeric (integers or values behaving like integers) representing semitone counts.

## Returns:
    int: A signed integer 'acc' representing how many semitone steps to apply to progression2's base interval value so that (progression2 + acc) - progression1 == interval.
    - Positive acc: raise progression2 by acc semitones.
    - Negative acc: lower progression2 by -acc semitones.
    - Zero: progression2 already yields the desired interval relative to progression1.

Edge cases:
- If the loop must cross octave boundaries, the routine first normalizes by adding 12 to j when j < i before adjusting; the returned acc therefore corresponds to adjustments that may move progression2 up or down across an octave boundary depending on the target.

## Raises:
    ValueError: If progression1 or progression2 is not present in the module-level `numerals` sequence (because numerals.index(...) will raise ValueError).
    IndexError: If the numerals.index(...) result is out of range for `numeral_intervals` (i.e., `numeral_intervals` is not at least as long as `numerals`) — arising from the j = numeral_intervals[...] or i = numeral_intervals[...] lookups.
    TypeError: If `interval` is not an integer-like value and comparisons/arithmetics in the function fail.

These exceptions are not raised explicitly in the function but can propagate from the underlying sequence operations and arithmetic.

## Constraints:
Preconditions:
- The module-level variables `numerals` and `numeral_intervals` must be defined and accessible in the same module namespace.
- `numerals` must be an indexable/iterable container supporting index(value) and containing both progression1 and progression2.
- `numeral_intervals` must be indexable and contain numeric (integer-like) semitone values at the indices produced by numerals.index(...).
- `interval` should be an integer (desired semitone difference).

Postconditions:
- After the function returns, the relation (numeral_intervals[index(progression2)] + acc) - numeral_intervals[index(progression1)] == interval holds, assuming no exceptions occur and that numeral_intervals contains the original base values (note: the function works with local variables and does not mutate module-level data).

## Side Effects:
- None. The function performs lookups and local arithmetic only. It does not mutate global variables, perform I/O, or call external services.

## Control Flow:
flowchart TD
    Start --> Lookup_i_j[Lookup i = numeral_intervals[numerals.index(progression1)] and j = numeral_intervals[numerals.index(progression2)]]
    Lookup_i_j --> NormalizeIfNeeded{Is j < i ?}
    NormalizeIfNeeded -- yes --> Add12[j = j + 12]
    NormalizeIfNeeded -- no --> Continue
    Add12 --> WhileGreater{j - i > interval ?}
    Continue --> WhileGreater
    WhileGreater -- yes --> DecrementJ[j = j - 1; acc = acc - 1] --> WhileGreater
    WhileGreater -- no --> WhileLess{j - i < interval ?}
    WhileLess -- yes --> IncrementJ[j = j + 1; acc = acc + 1] --> WhileLess
    WhileLess -- no --> Return[Return acc]

## Examples:
- Example usage scenario (conceptual, not code):
    - Suppose numerals maps 'I' and 'V' to indices 0 and 4 respectively, and numeral_intervals stores semitone values such that i = 0 and j = 7 (a perfect fifth).
    - Calling this function with progression1='I', progression2='V', interval=7 would return 0 because the current interval already equals 7.
    - If numeral_intervals['V'] were 8 instead (one semitone higher), calling with interval=7 would return -1 (lower V by one semitone).
    - If numeral_intervals['V'] were 2 and numeral_intervals['I'] were 10, the function will initially add 12 to j to handle octave wrap, then compute the required acc accordingly.

Implementation notes for re-creation:
- The function relies solely on two module-level sequences:
    - numerals: sequence of progression identifiers supporting index(value).
    - numeral_intervals: sequence of integer semitone values aligned by index with numerals.
- Reimplementation must preserve the normalization step (adding 12 when j < i) and the iterative adjustment loops to match the exact behavior.

## `mingus.core.progressions.skip` · *function*

## Summary:
Advance a Roman-numeral token by a specified number of scale steps within the module's seven-element numerals sequence, returning the resulting Roman-numeral with cyclic wrap-around.

## Description:
This small helper locates the position of the given roman_numeral in the module-level sequence numerals (expected to contain the seven scale-degree tokens in order), adds skip_count to that index, applies modulo 7 wrap-around, and returns the element at the resulting position.

Typical callers and usage context:
    - No direct call sites were found in the available code snapshot. It is designed as a low-level utility for progression-building or Roman-numeral navigation routines (for example, functions that compute the next degree in a chord progression or that transpose Roman-numeral progressions by degree offsets).
    - Callers typically invoke this during progression construction or when computing relative degrees (e.g., compute the Roman numeral two steps after 'IV').

Why this function is separate:
    - Encapsulates the common operation "find current degree → advance by N → wrap" so higher-level logic does not duplicate index lookups, modulo arithmetic, or wrap-around edge cases. Centralizing this behavior also makes future changes (e.g., changing the numerals ordering or wrapping logic) easier.

## Args:
    roman_numeral (str):
        An element that must be equal (==) to one of the entries in the module-level numerals sequence. Exact permitted tokens depend on that list (commonly Roman numerals like 'I','II','III', ...).
    skip_count (int, optional):
        Number of scale steps to advance. Defaults to 1.
        - Any integer is accepted: positive advances forward, zero returns the same element, negative values step backward.
        - Very large integers are permitted; final index is reduced by modulo 7.
        - Must be an integer (or an int-like value). Non-integer numeric types will lead to a TypeError at indexing time.

Interdependencies:
    - The function depends on a module-level variable numerals and the code uses a modulo base of 7 (i % 7). Therefore the function assumes numerals has seven elements and that the caller expects 7-degree cyclic behavior.

## Returns:
    str:
        The element from numerals that lies skip_count positions after roman_numeral when moving forward through numerals, with wrap-around (i % 7) applied.
        - Return is always one of the items of numerals when preconditions hold.
        - Example (assuming numerals == ['I','II','III','IV','V','VI','VII']):
            skip('I', 1) -> 'II'
            skip('VII', 1) -> 'I'
            skip('I', -1) -> 'VII'

## Raises:
    ValueError:
        Raised by numerals.index(roman_numeral) when roman_numeral is not found in numerals.
    TypeError:
        If skip_count is not an integer (for example a float or a string), the computed index expression may be a non-integer and indexing numerals[...] will raise TypeError.
    NameError:
        If the module-level name numerals is not defined, a NameError will occur when the function attempts numerals.index(...).

Notes on IndexError:
    - The implementation deliberately applies modulo 7 before indexing, so when numerals is a 7-item sequence and roman_numeral is a valid element, an IndexError will not occur. IndexError is only possible if numerals is not a 7-length sequence or if numerals changes between the index lookup and the final access (which should not happen in normal, single-threaded use).

## Constraints:
Preconditions:
    - A module-level sequence numerals must be defined and contain exactly seven elements ordered to represent scale degrees.
    - roman_numeral must be equal to one of the elements in numerals.
    - skip_count should be an integer (or explicitly converted to int) before calling.

Postconditions:
    - The returned value is an element of numerals and corresponds to the original roman_numeral advanced by skip_count positions modulo 7.
    - The function does not mutate numerals or any external state.

## Side Effects:
    - None. The function performs no I/O and does not change global state.

## Control Flow:
flowchart TD
    Start[Call skip(roman_numeral, skip_count)]
    CheckNumeralsDefined{Is module name "numerals" defined?}
    FindIndex[Call numerals.index(roman_numeral)]
    NotFound[ValueError: roman_numeral not in numerals]
    ComputeI[Compute i = index + skip_count]
    Modulo[Compute wrapped = i % 7]
    Return[Return numerals[wrapped]]
    TypeErr[TypeError if skip_count not int-like]
    NameErr[NameError if numerals is undefined]

    Start --> CheckNumeralsDefined
    CheckNumeralsDefined -->|No| NameErr
    CheckNumeralsDefined -->|Yes| FindIndex
    FindIndex -->|not found| NotFound
    FindIndex -->|found| ComputeI
    ComputeI -->|skip_count invalid| TypeErr
    ComputeI --> Modulo
    Modulo --> Return

## Examples:
Assuming numerals == ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']:

    # Advance one degree (default)
    result = skip('I')         # -> 'II'

    # Advance two degrees
    result = skip('IV', 2)     # -> 'VI'

    # Wrap-around forward
    result = skip('VII', 1)    # -> 'I'

    # Wrap-around backward
    result = skip('I', -1)     # -> 'VII'

    # Error handling: unknown numeral
    try:
        skip('N')
    except ValueError:
        # roman_numeral not in numerals
        handle_missing_numeral()

    # Defensive caller validation (recommended)
    if not isinstance(skip_count, int):
        raise TypeError("skip_count must be an integer")
    if roman_numeral not in numerals:
        raise ValueError("roman_numeral must be an element of numerals")

