# `tunings.py`

## `mingus.extra.tunings.StringTuning` · *class*

*No documentation generated.*

### `mingus.extra.tunings.StringTuning.__init__` · *method*

## Summary:
Initializes the instance by storing the instrument and description and normalizing the provided tuning specification into a list of mingus.containers.note.Note objects (or lists of Note objects) assigned to self.tuning.

## Description:
This method runs during object construction when StringTuning(...) is called. Its sole responsibility is to normalize and store the incoming tuning representation so other methods can rely on a consistent internal format: self.tuning will be a list whose elements are either Note instances or lists of Note instances.

Why this is a separate initializer:
- Centralizes parsing/normalization of the tuning input at construction time so that other instance methods can assume a normalized structure (no repeated parsing elsewhere).
- Keeps object setup atomic and explicit: instrument, tuning, and description are all set in one place.

Known callers / lifecycle:
- Invoked whenever a StringTuning instance is created. No other callers are determined from this method body.

Example invocation:
- StringTuning('guitar', 'standard', ['E', 'A', 'D', 'G', 'B', 'E'])

## Args:
    instrument (any):
        The instrument identifier or object to associate with this tuning. Stored verbatim on self.instrument; no validation or coercion is applied here.
    description (any):
        Human-readable description stored verbatim on self.description (typically a string).
    tuning (iterable):
        An iterable (e.g., list) describing the strings/courses. For each element x in tuning:
        - If isinstance(x, list) is True (i.e., x is a Python list), x is treated as a multi-note course: each sub-element n in x is passed to Note(n) and the resulting list of Note objects is appended to self.tuning.
        - Otherwise x is treated as a single-note course: x is passed to Note(x) and the resulting Note object is appended to self.tuning.
        Important: only actual Python list objects trigger multi-note handling. Tuples or other sequence types are treated as single values and forwarded to the Note constructor.

## Returns:
    None
    (This is an initializer; it does not return a value. The observable effect is the mutation of the instance attributes described below.)

## Raises:
    TypeError:
        If tuning is not iterable, the "for x in tuning" will raise TypeError (propagated).
    Any exception raised by mingus.containers.note.Note:
        If constructing Note(n) for any element or sub-element raises an exception (for example due to invalid note text), that exception is propagated through this initializer. The method does not catch or translate exceptions from Note.

## State Changes:
    Attributes READ:
        None of the instance attributes are read by this method.
    Attributes WRITTEN:
        self.instrument   -- set to the provided instrument argument
        self.tuning       -- set to a newly created list; each entry corresponds to an entry in the provided tuning iterable and is either:
                              * a Note instance (for non-list elements), or
                              * a list of Note instances (for elements that were Python lists)
        self.description  -- set to the provided description argument

## Constraints:
    Preconditions:
        - tuning must be an iterable. If it is not, iteration will fail with TypeError.
        - Values passed (either elements or sub-elements) must be acceptable inputs to mingus.containers.note.Note; otherwise Note(...) will raise and that exception will propagate.
    Postconditions:
        - self.instrument equals the provided instrument argument.
        - self.description equals the provided description argument.
        - self.tuning is a list with the same length and ordering as the provided tuning iterable and with elements normalized to Note instances or lists of Note instances as described above.

## Side Effects:
    - Constructs mingus.containers.note.Note objects while populating self.tuning.
    - Mutates the instance by assigning to self.instrument, self.tuning, and self.description.
    - Performs no I/O and makes no external service calls.

### `mingus.extra.tunings.StringTuning.count_strings` · *method*

## Summary:
Return the number of top-level string entries (courses) recorded in the tuning; does not modify the object's state.

## Description:
This method provides a single, central place to query how many top-level entries are in self.tuning. Known callers within this class include:
- get_Note: uses count_strings() to validate that a requested string index is within bounds before constructing a Note for that string and fret.

This logic is a dedicated method (rather than inlined) to encapsulate the notion of "how many strings/courses the instrument exposes" and to make boundary checks and other callers clearer and less error-prone. It also isolates the representation detail that self.tuning is a list whose elements may be Note instances or lists of Note instances.

## Args:
    None

## Returns:
    int: The number of top-level entries in self.tuning.
    - If self.tuning is an empty sequence, returns 0.
    - This counts top-level list elements (courses). It does not count individual notes inside a multi-note course; use count_courses() to obtain the per-course average/total information.

## Raises:
    TypeError: If self.tuning is not a sequence type that supports len(), calling len(self.tuning) will raise TypeError. (In normal construction, the class initializes self.tuning as a list, so this should not occur.)

## State Changes:
    Attributes READ:
        - self.tuning

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self.tuning must be a sequence (supports len()). The class constructor ensures this under normal usage.
    Postconditions:
        - No changes are made to self.tuning or any other attribute.
        - The returned integer equals len(self.tuning) at the time of the call.

## Side Effects:
    - None. The method performs no I/O, network activity, or mutation of external objects.

### `mingus.extra.tunings.StringTuning.count_courses` · *method*

## Summary:
Returns the average number of physical strings per course for this tuning by counting individual strings across all courses and dividing by the number of courses; does not modify object state.

## Description:
Known callers and usage context:
- No internal callers were found inside mingus.extra.tunings.Source-level inspection shows this method is a utility on the StringTuning object and is intended to be called by external client code that needs instrument statistics (for example, display/validation logic or algorithms that must know how many physical strings a tuning has on average).
- Typical lifecycle stage: called after a StringTuning instance has been constructed (self.tuning populated) when a caller needs to reason about course sizes or total physical string counts (e.g., to adapt fingering algorithms or to report instrument characteristics).

Rationale for keeping this logic as a separate method:
- Encapsulates a single, well-defined query about the tuning (average strings per course). This keeps callers from repeating the counting logic and centralizes the handling of multi-string courses (lists) versus single-string courses, improving clarity and reuse.

## Args:
This method takes no arguments.

## Returns:
float
- The returned value is computed as (total number of individual strings across all entries in self.tuning) divided by (number of entries in self.tuning).
- Typical values:
  - 1.0 when every course is a single string.
  - > 1.0 for instruments with multi-string courses (e.g., a 12-string with six courses of two strings yields 2.0).
- Edge-case return: none — if self.tuning is empty, the method does not return; it triggers an exception (see Raises).

## Raises:
ZeroDivisionError
- Trigger condition: self.tuning is an empty sequence (len(self.tuning) == 0). The code divides by len(self.tuning), causing a ZeroDivisionError.

Note: The implementation does not raise other explicit exceptions. It treats any element that is an instance of builtin list as a multi-string course (counted by len(x)) and treats any non-list element as a single string (counts as 1). Thus, non-list sequence types (tuples, other sequence objects) are counted as a single string rather than by their length.

## State Changes:
Attributes READ:
- self.tuning (iterated to compute counts)

Attributes WRITTEN:
- None (this method does not modify any attributes on self)

## Constraints:
Preconditions:
- The caller should ensure self.tuning is non-empty (len(self.tuning) > 0) if they want a valid numeric result; otherwise expect a ZeroDivisionError.
- The method expects that multi-string courses are represented as builtin lists. Only instances where isinstance(element, list) is True will be treated as multi-string courses and counted using len(element). Other iterable/sequence types will be treated as single-string courses.

Postconditions:
- The method returns a float value representing average strings per course and leaves self.tuning and other object state unchanged.

## Side Effects:
- None. The method performs no I/O, makes no external service calls, and mutates no objects outside of reading self.tuning.

### `mingus.extra.tunings.StringTuning.find_frets` · *method*

## Summary:
Compute, for each string/course of the tuning, the fret number (semitone offset) required to produce the target pitch; returns a list of frets or None for strings that cannot produce the pitch within the allowed fret range. This does not modify the object state.

## Description:
Known callers and contexts:
- StringTuning.find_fingering calls this method early in its recursive fingering search to locate candidate fret positions for the first note in a phrase; it is used during the "generate candidate positions" stage of fingering generation.
- It is also useful as a small utility for callers that need to know, for a single pitch, which strings can play it and at which fret (for example: UI string maps, heuristics, or external code performing per-note analysis).

Why this logic is its own method:
- The operation (convert an input to a Note, compute semitone distance from each string's base pitch, clamp by maxfret) is a concise, reusable primitive used by higher-level fingering and chord-finding algorithms. Factoring it out keeps fingering logic focused on combinatorics while centralizing conversion and per-string measurement in one place.

## Args:
    note (str | Note):
        - A target pitch to locate on the instrument.
        - If a string is supplied, it will be converted to a Note by calling Note(note).
        - Accepted string formats and validation are those supported by the Note constructor; invalid strings will propagate constructor errors.
    maxfret (int, optional): default 24
        - Maximum allowed fret number considered valid.
        - Typical values are non-negative integers. If negative, no frets will satisfy 0 <= diff <= maxfret, and the method will return None for every string.

## Returns:
    list[int | None]:
        - A list whose length equals the number of strings/courses in self.tuning (the same order as self.tuning).
        - Each element is either:
            * an integer >= 0 and <= maxfret: the fret (number of semitone steps above the string's base pitch) that produces the target pitch on that string's primary course note; or
            * None: if the required fret is negative or exceeds maxfret (i.e., the pitch is not reachable on that string within the allowed fret range).
        - The integer values are the semitone difference computed as int(target_note) - int(string_base_note).

## Raises:
    Any exception raised by Note(note) when converting a string to a Note, for example:
        - ValueError: invalid pitch string format (depends on Note implementation)
    Any exception raised by Note.measure when it attempts to convert operands to integer pitch values, for example:
        - TypeError or ValueError from int() conversion
        - IndexError if a Note instance is malformed and its __int__/internal logic indexes invalid data
    (These exceptions are not raised explicitly by this method but propagate from the Note constructor or Note.measure.)

## State Changes:
    Attributes READ:
        - self.tuning: iterated to obtain each string/course base pitch
        - elements of self.tuning (each element is either a Note or a list of Notes); the method reads the first Note in a course when the entry is a list
    Attributes WRITTEN:
        - None (this method does not mutate self or contained Note objects)

## Constraints:
    Preconditions:
        - self.tuning must be initialized and contain either Note instances or lists whose first element is a Note (this is ensured by StringTuning.__init__ which constructs Note objects).
        - maxfret should be an integer (or at least a value comparable with integers); non-integer inputs will be compared with integers in the numeric comparisons and may behave unexpectedly.
        - If note is a string, it must be a valid input for Note(note).
    Postconditions:
        - The returned list has length == len(self.tuning).
        - For each index i:
            * If returned value is an integer f, then 0 <= f <= maxfret and int(target_note) - int(string_base_note) == f.
            * If returned value is None, then either int(target_note) - int(string_base_note) < 0 or > maxfret.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self.
    - The only observable side effects are exceptions propagated from Note(...) or Note.measure(...) if the input is invalid.

## Implementation notes (for reimplementation):
    - Convert string input to a Note using Note(note) when necessary.
    - For each element x in self.tuning:
        * If x is a list (a course), use x[0] as the base Note for that string/course.
        * Otherwise treat x directly as the base Note.
    - Compute diff = base.measure(note) which returns int(note) - int(base).
    - If 0 <= diff <= maxfret append diff to the result; otherwise append None.
    - Return the accumulated result list.

### `mingus.extra.tunings.StringTuning.find_fingering` · *method*

## Summary:
Finds all valid fingerings that map a sequence of notes to distinct instrument strings using candidate frets from the tuning, filters them by fret-span, and returns the candidate fingerings sorted primarily by ascending total fret sum. This method performs a pure computation and does not modify the tuning object.

## Description:
This recursive helper constructs all combinations of (string_index, fret) assignments for a given ordered sequence of notes under these rules:
- Each input note is assigned to a different string (strings are not reused).
- For each note the only allowed fret values are those returned by self.find_frets(note); positions where find_frets returns None are skipped.
- After assembling a full assignment for all notes, the fingering is accepted only if the span between the highest fret and the lowest non-zero fret is >= 0 and strictly less than max_distance, or if the fingering contains no non-zero frets (e.g., all open strings). The method returns accepted fingerings sorted by the sum of their frets (smallest sum first). For equal sums, the built-in tuple/list ordering of Python is used as a tiebreaker.

Known or typical callers and context:
- Called by higher-level routines that translate chords or note sets into playable positions for this tuning (e.g., chord-finding utilities, fretboard layout generators).
- Invoked at the moment a user requests playable fingerings for a set of notes; it is a dedicated search/selection step.
- It is a separate method because it encapsulates a recursive combinatorial search with pruning and sorting logic that is reusable and easier to test than inlining this logic where fingerings are requested.

## Args:
    notes (sequence[Note|str] or None):
        Sequence of notes to assign to strings, in the order they should be assigned. Each element is passed through to self.find_frets to obtain candidate frets. If None or an empty sequence, the method returns [].
    max_distance (int, optional):
        Non-negative integer. The exclusive upper bound on allowed fret-span: accepted fingerings must satisfy (max_nonzero_fret - min_nonzero_fret) < max_distance. Defaults to 4.
    not_strings (list[int] or None, optional):
        Internal recursion parameter: indices of strings that must not be used in this call. Public callers should omit this argument (pass None). When None, the method initializes it to [].

Notes on argument types and ranges:
- Elements of notes must be valid inputs for self.find_frets (for example Note instances or note name strings accepted by that method).
- max_distance should be >= 0; negative values are not meaningful and will typically yield no results.
- not_strings entries must be valid string indices for this tuning.

## Returns:
    list[list[tuple[int, int]]]:
        Each returned candidate is a list of (string_index, fret) tuples in the same order as the input notes. The outer list contains all accepted candidates sorted by ascending total fret sum. If no candidate is found or notes is None/empty, returns an empty list.

Sorting/tie-break behavior:
- Primary sort key is the sum of frets across the fingering (lower sums appear first).
- When sums are equal, Python's default sorting order on the (frets_sum, fingering) tuple determines tie-breakers (i.e., lexicographic order of the fingering lists).

Special/edge returns:
- [] for notes is None or notes is an empty sequence.
- Fingerings with only open strings (all frets == 0) are accepted regardless of max_distance per the method's acceptance check.

## Raises:
    The method itself does not explicitly raise exceptions. Exceptions from self.find_frets (for example due to invalid note inputs) will propagate to the caller.

## State Changes:
Attributes READ:
    - Calls self.find_frets(note) for each note processed; this is the only interaction with the tuning object.

Attributes WRITTEN:
    - None. The method does not modify self or external state.

## Constraints:
Preconditions:
    - self must implement find_frets(note) that returns a sequence (indexable/iterable) with one entry per string; each entry should be either:
        * an integer fret number >= 0, or
        * None to indicate that string cannot play the note.
    - For any non-empty successful result, the number of notes must not exceed the number of playable strings (because every note is assigned to a different string).
    - The caller should not supply a pre-populated not_strings unless intentionally resuming a partial assignment.

Postconditions:
    - Every returned fingering:
        * Uses distinct string indices (no repeats).
        * Uses fret values that came from self.find_frets for the corresponding note.
        * Satisfies (max_nonzero_fret - min_nonzero_fret) < max_distance, or contains no non-zero frets (the method accepts all-open-string fingerings).
    - The returned list is sorted by total fret sum ascending (with Python's tie-breaker behavior for equal sums).

## Side Effects:
    - No I/O, network, or filesystem operations.
    - Does not mutate input sequences, the tuning object, or global state.
    - Any exception from self.find_frets propagates outward.

## Implementation notes and precise edge-case behaviors:
    - Recursion and not_strings:
        * The algorithm takes the first note, enumerates candidate frets across strings from self.find_frets(first_note), and for each playable string (fret is not None and string not in not_strings) either:
            - Recurse on the remaining notes with that string added to not_strings (if more notes remain), or
            - Emit a single-element fingering [(string, fret)] when no notes remain.
        * This ensures strings are not reused across the assignment.
    - Acceptance test details (literal translation of the code):
        * For each candidate fingering r, the code computes:
            - min_fret initialized to 1000 and updated only with frets != 0 when smaller.
            - max_fret initialized to -1 and updated with any fret greater than current max_fret.
            - frets_sum as the sum of all fret values in r.
        * The fingering is accepted if any of these are true:
            - 0 <= (max_fret - min_fret) < max_distance
            - min_fret == 1000 (indicates the fingering had no non-zero frets; e.g., all frets were 0)
            - max_fret == -1 (practically unreachable given how candidates are built, because every appended candidate includes at least one (string, fret) with fret >= 0)
        * Note: max_fret == -1 is included verbatim in the original code but is effectively unreachable because result entries are only created from iterations where at least one valid fret exists (fret >= 0). Implementations reproducing this logic may keep the condition for fidelity or omit it if intentionally simplifying.
    - Variable naming:
        * The code reuses the name frets for both the initial candidate list from find_frets and later as an integer accumulator; when reimplementing, prefer distinct names like candidate_frets and frets_sum to avoid confusion.
    - Performance:
        * The search is combinatorial; the number of explored assignments grows rapidly with the number of notes and the number of candidate strings per note. Apply practical limits on input size or prune candidate sets when integrating into interactive tools.

### `mingus.extra.tunings.StringTuning.find_chord_fingering` · *method*

*No documentation generated.*

### `mingus.extra.tunings.StringTuning.frets_to_NoteContainer` · *method*

## Summary:
Convert a per-string fingering (sequence of frets or None) into a NoteContainer of Note objects representing only the played strings.

## Description:
This method iterates the provided fingering sequence and for each entry that is not None calls the instance's get_Note(string_index, fret) to construct a Note for that string/fret. It collects those Note objects in a new NoteContainer and returns it.

Known callers and context:
- StringTuning.find_chord_fingering: used when the best fingering must be converted into a NoteContainer for downstream processing or return (used when return_best_as_NoteContainer=True).
- It may also be called by external code using a StringTuning instance to convert a fingering representation (list/tuple) into notes.
Why this is a separate method:
- Encapsulates the mapping from a simple fingering representation to Note objects (including the per-Note .string and .fret assignment performed by get_Note).
- Keeps conversion logic localized so other algorithms in the class can reuse it without duplicating index/None handling or NoteContainer construction.

## Args:
    fingering (iterable of (int or None)):
        Sequence (typically a list or tuple) indexed by string number where each element is:
        - an integer fret number (0..24 by default), or
        - None to indicate the string is not played.
        The length of the sequence is commonly equal to the number of strings (self.count_strings()), but it may be shorter or longer; only entries present will be processed and their index is used as the string number.

## Returns:
    mingus.containers.note_container.NoteContainer:
        A NoteContainer holding Note objects for every non-None entry in fingering.
        - Each Note has its .string attribute set to the string index (the enumerate index).
        - Each Note has its .fret attribute set to the fret value passed to get_Note.
        - Order: Notes appear in ascending string index order for entries that were not None.
        - If fingering is empty or all entries are None, returns an empty NoteContainer.

## Raises:
    mingus.core.mt_exceptions.RangeError:
        - If any computed string index is out of range for this tuning (triggered by get_Note).
        - If any fret value is outside the allowed fret range enforced by get_Note (default maxfret is 24).
    TypeError / ValueError:
        - If fingering is not iterable (enumerate will raise TypeError).
        - If a non-None fret value is not an integer or a comparable numeric type, get_Note or its numeric comparisons may raise TypeError or ValueError.

## State Changes:
    Attributes READ:
        - self.tuning (read indirectly by get_Note to compute the base note)
        - any state accessed by get_Note (e.g., count_strings()) — effectively reads the tuning/length information
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.
        - It constructs new Note objects and returns them inside a new NoteContainer.

## Constraints:
    Preconditions:
        - self must be a properly initialized StringTuning instance (self.tuning populated).
        - fingering must be an iterable; its elements must be either None or integer-like fret numbers.
    Postconditions:
        - No attributes on self are modified.
        - The returned NoteContainer contains Note objects whose .string and .fret reflect the enumerated indices and fret values for non-None entries.
        - Any invalid string index or fret value will raise RangeError (propagated from get_Note) before a NoteContainer is returned.

## Side Effects:
    - No I/O or network calls.
    - Allocates Python objects (Note instances and a NoteContainer).
    - May raise exceptions coming from get_Note, which validates string and fret ranges.
    - Does not mutate objects outside the newly created Note instances and the returned NoteContainer.

### `mingus.extra.tunings.StringTuning.find_note_names` · *method*

## Summary:
Returns all fret numbers (0..maxfret) on a single string whose pitch class matches any note in the provided list, as (fret, note_name) pairs; does not modify the object.

## Description:
- Known callers and context:
    - No explicit callers were provided. Conceptually, this method is intended for use by higher-level fretboard or fingering utilities that compute or display possible positions for given target notes on a single instrument string.
    - Typical use: invoked once per string to gather candidate fret positions for a set of target notes when assembling full multi-string fingerings or rendering a fretboard diagram.
- Why a separate method:
    - It isolates the logic that (a) normalizes input notes into a names list, (b) converts those names to integer pitch classes, and (c) scans a single open-string tuning across a fret range to find matches. Separating this simplifies testing and prevents duplication when processing multiple strings.

## Args:
    notelist (sequence):
        - Required shape: a sequence type supporting indexing and iteration (must allow notelist[0] access). Examples: list of strings ['C', 'D#'], NoteContainer, list of Note-like objects.
        - Two primary accepted forms:
            * Sequence of note name strings (e.g., ['C', 'D#', 'F']). If notelist is non-empty and its first element is a string type (six.string_types), the method will create a NoteContainer from the sequence via NoteContainer(notelist).
            * NoteContainer or sequence of objects exposing a .name attribute (the method uses x.name for each element).
        - An empty sequence ([]) is allowed; the method will return an empty list.
        - Important: the method only inspects the first element to decide whether to wrap with NoteContainer. Heterogeneous sequences (first element string, later elements not) may yield unexpected results depending on NoteContainer behavior.
    string (int, optional):
        - Index of the string in self.tuning whose frets to examine. Defaults to 0.
        - Must be a valid index into self.tuning. The tuning value at that index must be convertible to an integer via int(self.tuning[string]).
    maxfret (int, optional):
        - Maximum fret number to examine (inclusive). Defaults to 24.
        - Should be an integer. If maxfret < 0 the method iterates no frets and returns [].
        - Passing a non-integer will raise TypeError when used in range(0, maxfret + 1).

## Returns:
    list[tuple[int, str]]:
        - A list of (fret, note_name) pairs sorted by increasing fret number.
        - fret: integer in [0, maxfret].
        - note_name: the name string taken from the names list built from the input (derived from element.name or from NoteContainer conversion).
    Additional behavior:
        - Pitch class matching is done modulo 12. The string open pitch is converted to an integer and reduced modulo 12; each fret’s pitch class is (open_pitch + fret) % 12 and compared to the target pitch classes.
        - If multiple input names map to the same pitch class, the returned note_name is the first occurrence in the input-derived names list. Implementation uses names[int_notes.index(pitch_class)] to select that name.
        - If there are no matches (including when notelist is empty or maxfret < 0), returns an empty list.

## Raises:
    - IndexError: If string is out of range for self.tuning (triggered by accessing self.tuning[string]).
    - TypeError: If maxfret is not an integer (used in range) or if int(self.tuning[string]) is called on an incompatible type.
    - ValueError/TypeError: May be raised by int(self.tuning[string]) depending on the tuning value type.
    - AttributeError: If notelist is non-empty and elements do not expose a .name attribute (the comprehension [x.name for x in n] will fail).
    - Exceptions from notes.note_to_int(name): If a note name is invalid, the underlying conversion will raise and that exception will propagate.
    - The method does not catch these exceptions; they propagate to callers.

## State Changes:
    Attributes READ:
        - self.tuning (reads the element at index string)
    Attributes WRITTEN:
        - None (no assignment to self attributes; all variables are local)

## Constraints:
    Preconditions:
        - self.tuning is indexable and contains a value at index string convertible to int(...).
        - notelist is indexable (supports notelist[0]), and either:
            * notelist is empty, or
            * notelist[0] is a string type (so NoteContainer(notelist) makes sense), or
            * every element of notelist exposes a .name attribute.
        - maxfret is an integer (or at least can be used in range()).
    Postconditions:
        - Returns all matching (fret, note_name) pairs for frets 0..maxfret inclusive where the string’s pitch class equals any provided note’s pitch class.
        - Self and input sequence(s) are not mutated by this method.

## Side Effects:
    - No I/O or external service calls.
    - May instantiate a NoteContainer locally when the first element of notelist is a string; the original notelist object is not modified by this method.
    - Calls notes.note_to_int(name) for each name (any side effects of that function will occur).

## Implementation notes (mapping to the source):
    - If notelist != [] and isinstance(notelist[0], six.string_types): n = NoteContainer(notelist) else n = notelist.
    - names = [x.name for x in n]
    - int_notes = [notes.note_to_int(x) for x in names]  # pitch-class integers used for modulo-12 comparison
    - s = int(self.tuning[string]) % 12
    - For each fret x in range(0, maxfret + 1): if (s + x) % 12 in int_notes:
          append (x, names[int_notes.index((s + x) % 12)]) to the result list.
    - Returns the result list (ordered by ascending fret).

## Short usage note:
- Usage intent: call once per string to collect candidate frets for a given set of target notes; combine results across strings in higher-level code to form full fingerings.

### `mingus.extra.tunings.StringTuning.get_Note` · *method*

## Summary:
Constructs and returns a Note object representing the pitch at the given string index and fret without modifying the StringTuning instance.

## Description:
This method converts a (string, fret) pair into a mingus.containers.note.Note instance using the tuning stored on the StringTuning object. Known callers and contexts:
- frets_to_NoteContainer: converts a list of fret numbers (one per string) into a NoteContainer by calling get_Note for each string/fret pair while building fingerings.
- Higher-level fingering and chord routines (e.g., find_chord_fingering) typically call frets_to_NoteContainer and therefore indirectly obtain Note objects from get_Note during fingering construction and conversion steps.

This logic is factored out into its own method to centralize:
- validation of string and fret ranges,
- selection of the base pitch for a string (handling single-note strings vs. multi-note courses),
- creation and annotation of the resulting Note with string and fret metadata.
Having this behavior in one place prevents duplication and keeps callers focused on fingering logic rather than on low-level Note creation and validation.

## Args:
    string (int): Index of the top-level tuning entry (0-based). Must satisfy 0 <= string < self.count_strings(). Default: 0.
    fret (int): Fret number on the specified string. Must satisfy 0 <= fret <= maxfret. Default: 0.
    maxfret (int): Inclusive upper bound for allowed fret values used for validation. Default: 24.

## Returns:
    mingus.containers.note.Note: A new Note instance created from the base pitch of the specified string plus the fret offset (constructed via Note(int(s) + fret)). The returned Note will have two attributes set before return:
        - note.string == string
        - note.fret == fret
    Edge cases:
        - If the tuning entry at the requested string is a list (a multi-note course), the first element of that list is used as the base pitch.
        - No further normalization or range-check is performed on the computed numeric pitch beyond constructing the Note.

## Raises:
    RangeError: If the string index is out of range:
        "String '%d' out of range" % string
    RangeError: If the fret is outside [0, maxfret]:
        "Fret '%d' on string '%d' is out of range" % (string, fret)
    (Implicit) TypeError or ValueError: If the selected base value s (an element of self.tuning or its first element when a course) cannot be converted to int(s). This is an unchecked error originating from the int(s) call.

## State Changes:
    Attributes READ:
        - self.tuning (used to select the base pitch for the specified string)
        - self.count_strings() is called to validate the string index (count_strings reads self.tuning)
    Attributes WRITTEN:
        - None on self (the StringTuning instance is not modified)

    Note-object mutations (not on self):
        - The newly-created Note instance has attributes written:
            - note.string is set to the requested string index
            - note.fret is set to the requested fret value

## Constraints:
    Preconditions:
        - self.tuning must be a sequence with at least count_strings() elements (this is how count_strings() is implemented).
        - Each element of self.tuning must be either a Note-like object or a list whose first element is Note-like; the code expects int(s) to succeed on the selected element.
        - Caller must provide integer-like values for string, fret, and maxfret (or values coercible to int); the method uses integer comparisons and the int() conversion.

    Postconditions:
        - If no exception is raised, the method returns a Note instance whose integer pitch equals int(base) + fret and whose .string and .fret attributes equal the provided string and fret arguments.
        - The StringTuning object remains unchanged.

## Side Effects:
    - No I/O, network calls, or interaction with external services.
    - Mutates only the newly-created Note object (setting its .string and .fret attributes) before returning it.

## `mingus.extra.tunings.fingers_needed` · *function*

## Summary:
Compute how many distinct finger placements are required to execute a fingering shape, accounting for open strings and a single index-finger barre across contiguous fretted strings.

## Description:
This function inspects a sequence of per-string finger numbers and returns the minimal count of finger placements required given these rules:
- 0 denotes an open (unfretted) string and splits a potential barre.
- The smallest non-zero finger number present is treated as the "index finger" and may form a single barre across multiple adjacent fretted strings (counted once) unless an open string separates them.
- All other fretted strings (non-zero values that either occur after an open string in the scan order or use a finger number different from the minimum) each require separate finger placements.

Known callers:
- Chord or fingering utilities that validate or analyze fingering shapes (e.g., chord-layout validators, fingering simplifiers, or UI renderers). These callers typically invoke this routine after computing per-string finger assignments to determine whether the shape fits within a player's available fingers or to display a finger-count hint.

Reason for extraction:
- Encapsulates the barre/open-string semantics and the reversed-scan logic into a single reusable function so chord and tuning modules don't replicate this subtle logic (reversed iteration, split behavior, single-index accounting).

## Args:
    fingering (sequence[int]):
        - Sequence (e.g., list or tuple) of integers, one element per string, in the instrument's canonical string order used by the surrounding code.
        - Semantics of values:
            * 0  => open string (not fretted)
            * 1  => index finger
            * 2  => middle finger
            * 3  => ring finger
            * 4+ => higher finger numbers
        - Requirements:
            * The object must support reversed(fingering) (i.e., be a sequence or implement __reversed__).
            * Elements should be integers (non-negative). Passing other types may lead to TypeError or undefined behavior.
            * At least one element must be > 0 (at least one fretted string); otherwise the function cannot determine the index finger.

## Returns:
    int:
        - The total number of finger placements required by the fingering under the barre rules.
        - Always a non-negative integer; with valid input (at least one fretted string) the return is >= 1.
        - Meaning:
            * 1 — All fretted strings can be covered by a single index-finger barre (or there is only one fretted note).
            * n > 1 — n separate finger placements are required (index finger counted at most once).

## Raises:
    ValueError:
        - Raised when there are no fretted strings (no elements > 0). This arises from the expression min(finger for finger in fingering if finger) evaluating an empty sequence.
    TypeError:
        - May be raised if `fingering` is not reversible (reversed(fingering) is invalid), for example when passing a plain iterator/generator that does not implement __reversed__.
        - May also occur if sequence elements are of types that cannot be compared by min() (e.g., mixing incomparable types).

## Constraints:
    Preconditions:
        - fingering is finite and reversible (supports reversed()).
        - At least one element in fingering is a positive integer.
        - Elements are integers and use 0 for open strings.

    Postconditions:
        - The returned integer equals the minimal number of finger placements required under these guarantees:
            * The smallest non-zero finger value is identified once as the index-finger candidate.
            * When scanning the sequence from the last element to the first (reversed order), encountering a 0 sets a split flag that prevents an index-finger barre from covering earlier (in original order) fretted strings.
            * The index finger (minimum value) contributes +1 to the result at its first eligible occurrence in the reversed scan; subsequent occurrences of the same minimal value (while indexfinger is already accounted for and before any split) do not increment the count.
            * Every fretted string not covered by the single index-barre (due to being after a split or using a different finger number) increments the result by 1.

## Side Effects:
    - None. Pure computation: no I/O, no mutation of the input sequence, and no external state changes.

## Control Flow:
flowchart TD
    Start((start)) --> ComputeMin[Compute minimum non-zero finger with min(... if finger)]
    ComputeMin --> InitVars[set split=False; indexfinger=False; result=0]
    InitVars --> ForLoop[For each finger in reversed(fingering)]
    ForLoop --> IsOpen{finger == 0 ?}
    IsOpen -- Yes --> SetSplit[set split = True] --> NextIter[continue]
    IsOpen -- No --> IsIndexCandidate{not split AND finger == minimum ?}
    IsIndexCandidate -- Yes --> IndexAccounted{indexfinger ?}
    IndexAccounted -- No --> IncAndMark[result += 1; indexfinger = True] --> NextIter
    IndexAccounted -- Yes --> NextIter
    IsIndexCandidate -- No --> IncOther[result += 1] --> NextIter
    NextIter --> ForLoop
    ForLoop --> ReturnResult((return result))

## Examples:
    - Example 1: all fretted, same index finger (barre)
        Input: [1, 1, 1, 1]
        Return: 1
        Rationale: minimum non-zero = 1; no open strings split the shape; index finger can barre all strings.

    - Example 2: open string breaks barre
        Input: [1, 1, 0, 1]
        Return: 2
        Rationale: Scanning from the end: last 1 contributes 1 (index finger accounted), then 0 sets split=True, so the earlier fretted 1 cannot be covered by the same barre and contributes +1.

    - Example 3: mixed fingers, index counted once
        Input: [2, 1, 1, 3]
        Return: 3
        Rationale:
            * minimum non-zero = 1 (index finger).
            * Scan reversed: 3 -> +1 (different finger),
                            next 1 -> +1 (first index occurrence; indexfinger becomes True),
                            next 1 -> +0 (index already accounted),
                            next 2 -> +1 (different finger).
            * Total = 1 + 1 + 0 + 1 = 3.

    - Example 4: all open (invalid)
        Input: [0, 0, 0]
        Behavior: Raises ValueError (no fretted strings to determine an index finger).

## `mingus.extra.tunings.add_tuning` · *function*

## Summary:
Registers a new string tuning object for a named instrument by creating a StringTuning and storing it in the module-level registry.

## Description:
Creates a StringTuning instance from the provided instrument name, description and tuning definition, then records it in the module registry (_known) under the uppercase instrument name and uppercase description.

Known callers within the available codebase:
    - No specific callers were found in the provided memory snapshot. This function is a public registration helper intended to be called by module initialization code or user code that wants to add custom tunings to the library registry.

Why this logic is extracted:
    - Adds a single, well-defined responsibility: construct the StringTuning object and update the shared registry. Extracting this avoids repeated registry-manipulation logic elsewhere, centralizes normalization (uppercase keys), and keeps StringTuning construction separated from storage mechanics.

## Args:
    instrument (str):
        Name/type of the instrument (e.g., 'Guitar', 'Bass'). Must be a Python str object because the function calls str.upper(instrument). The original (case-preserved) instrument value is stored in the registry tuple as provided.
    description (str):
        A short textual description/label for the tuning (e.g., 'Standard', 'Drop D'). Must be a Python str because the function calls str.upper(description) to normalize the key used in the registry.
    tuning (any):
        Opaque tuning definition passed through to the StringTuning constructor. The accepted shape and allowed types for this argument are determined by the StringTuning class; this function does not validate or transform it.

## Returns:
    None
    - This function does not return a value. Its effect is to mutate the module-level registry (_known).

## Raises:
    TypeError:
        If instrument or description are not Python str objects, the call to str.upper(instrument) or str.upper(description) will raise a TypeError (descriptor 'upper' requires a 'str' object).
    Any exception raised by the StringTuning constructor:
        If StringTuning(instrument, description, tuning) raises an exception (for example for invalid tuning shapes or out-of-range values), that exception propagates out of add_tuning unchanged.

## Constraints:
    Preconditions:
        - The caller must pass instrument and description as Python str objects (so str.upper(...) works).
        - The caller should supply a tuning value compatible with the StringTuning constructor (see StringTuning documentation).
    Postconditions:
        - After successful return, the module-level registry _known contains an entry keyed by str.upper(instrument).
        - The value for that key is a tuple: (instrument, mapping) where mapping[str.upper(description)] references the newly-created StringTuning instance.
        - If an entry for the instrument already existed, only its mapping is updated (the original stored instrument value in the tuple is left as it was when the key was first created).

## Side Effects:
    - Mutates the module-level registry _known (in-memory global state).
    - No file, network, or stdout/stderr I/O is performed by this function itself.
    - Any side effects from invoking the StringTuning constructor (if it performs them) will also occur and propagate.

## Control Flow:
flowchart TD
    A[Call add_tuning(instrument, description, tuning)]
    B[StringTuning(instrument, description, tuning) -> t]
    C{str.upper(instrument) in _known?}
    D[Update existing mapping: _known[UPPER_INST][1][UPPER_DESC] = t]
    E[Create new entry: _known[UPPER_INST] = (instrument, {UPPER_DESC: t})]
    A --> B --> C
    C -->|yes| D
    C -->|no| E
    D --> F[Return None]
    E --> F[Return None]

## Examples:
    Example: register a standard guitar tuning (happy-path)
    try:
        add_tuning('Guitar', 'Standard', ['E', 'A', 'D', 'G', 'B', 'E'])
    except TypeError:
        # instrument/description were not str
        raise
    except Exception as e:
        # StringTuning constructor rejected the tuning
        raise

    Example: retrieve the registered tuning from the registry (illustrative)
    # The internal registry structure after registration:
    # _known[str.upper('Guitar')] == ('Guitar', {str.upper('Standard'): <StringTuning instance>})
    inst_key = str.upper('Guitar')
    desc_key = str.upper('Standard')
    string_tuning = _known[inst_key][1][desc_key]
    # string_tuning is the same object created during add_tuning

## `mingus.extra.tunings.get_tuning` · *function*

## Summary:
Returns the first registered tuning object that matches a provided instrument name and description prefix, optionally constrained to exact numbers of strings and/or courses.

## Description:
Known callers and context:
- No direct callers were discovered in the provided code graph/memory snapshot. Typical callers (elsewhere in the codebase) are tablature generators, instrument factories, UI lookup handlers, or any code that needs to convert a human-readable instrument name and tuning description into a concrete tuning object for fingering, pitch calculations, or rendering.
- Typical pipeline stage: invoked when user input, instrument metadata, or configuration needs to be resolved to a canonical tuning object from the module-level registry (_known).

Why this is a separate function:
- Centralizes the registry lookup, matching policy, and optional numeric filtering. Exporting this as a single function prevents duplication of the instrument/description matching rules and numeric-filter logic across the codebase and ensures consistent behavior.

## Args:
- instrument (str)
    - Description: Instrument name or prefix to search for (e.g., "guitar", "GUI"). The function computes searchi = str.upper(instrument).
    - Requirement: Must be a string or string-like value acceptable to str.upper.
- description (str)
    - Description: Tuning description or prefix to search for (e.g., "standard", "DROP D"). The function computes searchd = str.upper(description).
    - Requirement: Must be a string or string-like value acceptable to str.upper.
- nr_of_strings (int or None, optional)
    - Description: If provided, the candidate tuning's tuning.count_strings() must equal this value.
    - Default: None (no filter by strings).
- nr_of_courses (int or None, optional)
    - Description: If provided, the candidate tuning's tuning.count_courses() must equal this value.
    - Default: None (no filter by courses).

Parameter interactions:
- If both nr_of_strings and nr_of_courses are None, the function returns the first tuning matching instrument and description prefix.
- If one or both numeric filters are provided, the tuning must match all provided filters to be returned.

## Returns:
- A tuning object (implementation-defined) that matched the search criteria, or None if no match was found.
- The tuning object is expected to provide:
    - count_strings() -> int
    - count_courses() -> int

## Raises:
- NameError: if the module-level registry variable _known is not defined.
- TypeError:
    - If instrument or description are not acceptable to str.upper (e.g., passing None).
    - If six.iteritems is invoked on a non-mapping (e.g., _known[x][1] is not mapping-like).
- IndexError:
    - If a registry value _known[x] exists but is not indexable at index 1 (the code uses _known[x][1]).
- AttributeError:
    - If a matched tuning object lacks count_strings() or count_courses() and those methods are called during filtering.
- Notes:
    - These exceptions are not explicitly raised by the function; they are the likely runtime errors produced when the registry or inputs violate the function's expectations.

## Constraints:
Preconditions:
- Module-level registry `_known` must exist and be a mapping where:
    - Each key is an instrument name (string).
    - Each value is indexable with [1] to produce a mapping/dictionary-like object of description -> tuning_object.
    - Conceptual example:
        - _known = { "GUITAR": (meta, {"STANDARD": tuning_obj, "DROP D": tuning_obj2}), ... }
- The registry's instrument keys (x) and description keys (desc) are compared as-is (the function uppercases the search inputs but does not uppercase x or desc internally). Therefore, to achieve case-insensitive behavior, keys in _known should themselves be stored uppercase.
- Tuning objects must implement count_strings() and count_courses() returning integers.
- instrument and description must be string-like (not None) such that str.upper succeeds.

Postconditions:
- No mutation of _known or the returned tuning object.
- Either returns a matching tuning object (first match following the exact matching algorithm) or None.

## Matching semantics and exact code behavior:
- Inputs normalization:
    - searchi = str.upper(instrument)
    - searchd = str.upper(description)
- Instrument matching:
    - keys = list(_known.keys())
    - Iterates each key x in keys (x is used as stored; the function does not uppercase x).
    - The conditional tested is exactly:
        (searchi not in keys and x.find(searchi) == 0) or (searchi in keys and x == searchi)
    - Behavior explained:
        - If searchi is an exact key in the registry keys, the function restricts matches to keys where x == searchi (exact match).
        - Otherwise (searchi not present as a key), the function accepts keys where x.find(searchi) == 0 (prefix match). Note: x.find(searchi) == 0 is equivalent to x.startswith(searchi) when both are strings, but the code uses find(...) == 0.
    - Important: because the code uppercases the search terms but does not transform x, effective matching is case-insensitive only when registry keys are stored in the same uppercase form (i.e., keys should be uppercase to get true case-insensitivity).
    - Operator precedence: The boolean grouping is important; the conditional groups the two alternatives with an OR; it is equivalent to:
        if ((searchi not in keys and x.find(searchi) == 0) or (searchi in keys and x == searchi)):
- Description matching:
    - For a matched instrument key x, the function iterates six.iteritems(_known[x][1]) yielding (desc, tun).
    - It tests if desc.find(searchd) == 0. Note: desc is not uppercased before comparison; therefore, to match robustly you should store description keys in the registry in uppercase to align with searchd.
- Numeric filtering:
    - If no numeric filters: return the first tun when description prefix matches.
    - If nr_of_strings is provided (and nr_of_courses is None): return tun if tun.count_strings() == nr_of_strings.
    - If nr_of_courses is provided (and nr_of_strings is None): return tun if tun.count_courses() == nr_of_courses.
    - If both provided: require both tun.count_courses() == nr_of_courses and tun.count_strings() == nr_of_strings.
- First-match policy:
    - The function returns the first tuning object that satisfies instrument matching, description prefix match, and any numeric filters. Iteration order is determined by list(_known.keys()) and the iteration order of the descriptions mapping returned by _known[x][1].

## Performance:
- Worst-case time complexity O(I * D) where I is number of instrument keys and D is average descriptions per instrument, plus cost of count_* calls when filters are used.

## Side Effects:
- None. No I/O, no network access, no modification of global/module state.

## Control Flow:
flowchart TD
    Start --> NormalizeInputs
    NormalizeInputs[searchi=str.upper(instrument); searchd=str.upper(description)]
    NormalizeInputs --> GetKeys[keys=list(_known.keys())]
    GetKeys --> ForEachKey
    ForEachKey{for x in keys}
    ForEachKey --> InstrumentCond
    InstrumentCond{(searchi not in keys and x.find(searchi)==0) OR (searchi in keys and x==searchi)}
    InstrumentCond -- no --> NextKey
    InstrumentCond -- yes --> ForEachDesc
    ForEachDesc[for (desc,tun) in six.iteritems(_known[x][1])]
    ForEachDesc --> DescCond
    DescCond{desc.find(searchd)==0?}
    DescCond -- no --> NextDesc
    DescCond -- yes --> Filters
    Filters{nr_of_strings/nr_of_courses provided?}
    Filters -- none --> ReturnTun
    Filters -- only strings --> CheckStrings
    Filters -- only courses --> CheckCourses
    Filters -- both --> CheckBoth
    CheckStrings{tun.count_strings()==nr_of_strings?} -- yes --> ReturnTun
    CheckStrings -- no --> NextDesc
    CheckCourses{tun.count_courses()==nr_of_courses?} -- yes --> ReturnTun
    CheckCourses -- no --> NextDesc
    CheckBoth{both equal?} -- yes --> ReturnTun
    CheckBoth -- no --> NextDesc
    ReturnTun[Return tuning object]
    NextDesc --> ForEachDesc
    NextKey --> ForEachKey
    ForEachKey --> End[Return None if no match found]

## Examples and recommended usage patterns:
- Simple lookup:
    - Goal: obtain a guitar "standard" tuning.
    - Call: get_tuning("guitar", "standard")
    - Important: ensure _known keys and description keys are stored uppercase (e.g., "GUITAR", "STANDARD") to guarantee matches because this function uppercases inputs but does not uppercase registry keys or descriptions.
- Lookup with string-count filter:
    - Goal: get a 7-string standard guitar tuning.
    - Call: get_tuning("guitar", "standard", nr_of_strings=7)
    - Behavior: each candidate tun will have tun.count_strings() compared to 7; first match returned, otherwise None.
- Defensive caller pattern:
    - Because malformed _known structures or unexpected types can raise NameError/IndexError/TypeError/AttributeError, a caller that must be resilient should wrap the call:
      - try:
          tun = get_tuning(inst, desc, nr_of_strings, nr_of_courses)
        except (NameError, TypeError, IndexError, AttributeError) as e:
          handle_registry_error(e)
      - If get_tuning returns None, handle the "no match found" case separately (e.g., use a fallback tuning or inform the user).

## Implementation checklist (for reimplementation):
- Uppercase input arguments with str.upper.
- Collect keys using list(_known.keys()).
- For each x in keys, evaluate the exact conditional:
    - if (searchi not in keys and x.find(searchi) == 0) or (searchi in keys and x == searchi)
- Iterate (desc, tun) over six.iteritems(_known[x][1]) and test desc.find(searchd) == 0.
- Apply numeric filters using tun.count_strings() and tun.count_courses() exactly as in the control flow.
- Return the first matching tuning or None.
- Document and handle the runtime exceptions listed above in callers as needed.

## `mingus.extra.tunings.get_tunings` · *function*

## Summary:
Return a list of tuning descriptor objects from the module's registry, filtered by instrument name (exact or prefix match) and/or by the number of strings and/or courses.

## Description:
Searches the module-level _known registry and collects tuning descriptors that match the supplied criteria:
- If instrument is None, tunings from all registered instruments are considered.
- If instrument is provided, it is converted to uppercase using str.upper(instrument) and matched against registry keys:
  - If the uppercase search exactly equals a registry key, only that instrument's tunings are considered (exact match).
  - Otherwise, registry keys that begin with the uppercase search string are considered (prefix match via str.find(search) == 0).
- For each selected registry entry _known[key], the function expects index 1 to be a mapping (dict-like) whose values are tuning descriptor objects; it collects those values.
- Optional numeric filters:
  - nr_of_strings: include only descriptors where descriptor.count_strings() == nr_of_strings.
  - nr_of_courses: include only descriptors where descriptor.count_courses() == nr_of_courses.
  - If both numeric filters are provided, a descriptor must satisfy both (logical AND).
- Returned list preserves the order produced by iterating the registry keys and the per-instrument tuning mapping values.

Known callers in the provided repository snapshot:
- None found in the provided memory/graph. (If other modules invoke this function, list them here for traceability.)

Why this is a separate function:
- Encapsulates lookup and filtering logic for tunings in one place. Callers can request tunings with simple arguments without knowing registry internals, and future changes to matching/filter semantics or registry layout are localized here.

## Args:
    instrument (str|None):
        - Instrument name to search for. Must be an instance of str (the function calls str.upper(instrument)); passing a non-str will raise TypeError.
        - If None: no instrument-based filtering (all instruments included).
        - If a string: the uppercase form is used for exact or prefix matching against registry keys.
    nr_of_strings (int|None):
        - If provided, only tunings whose descriptor.count_strings() equals this integer are included.
        - Expected to be an int; non-int values that compare equal using == may match but using non-integers is not guaranteed.
    nr_of_courses (int|None):
        - If provided, only tunings whose descriptor.count_courses() equals this integer are included.
        - Expected to be an int; non-int values that compare equal using == may match but using non-integers is not guaranteed.

Interdependencies:
- Both nr_of_strings and nr_of_courses may be set; a tuning must satisfy both to be included.
- When instrument is provided and matches a registry key exactly, only that key is searched; prefix matching is used only when no exact match exists.

## Returns:
    list: A list (possibly empty) of tuning descriptor objects taken from the registry values (the values of _known[<instrument>][1] for matched instruments).
    - Typical descriptor type: instances that implement count_strings() and count_courses(), e.g., NoteContainer-like objects.
    - If no registry entries or no descriptors match the filters, returns an empty list.
    - The function never returns None.

## Raises:
    TypeError:
        - Raised if instrument is not None and is not a str, because the function calls str.upper(instrument) which requires a str object.
    NameError:
        - Raised if the module-level variable _known is not defined (list(_known.keys()) will raise NameError).
    AttributeError:
        - May be raised if a descriptor selected for filtering does not implement the required methods (count_strings or count_courses) and the corresponding numeric filter is used.
    IndexError:
        - May be raised if an entry in _known does not have an index 1 (the code accesses _known[x][1]); this indicates the registry structure is not as expected.
    Any exception raised by descriptor.count_strings() or descriptor.count_courses():
        - If these methods themselves raise exceptions, those will propagate.

## Constraints:
Preconditions:
- The module-level _known variable must exist and be a mapping where each value at index 1 is a dict-like mapping of tuning names to tuning descriptor objects.
- If numeric filters are used, descriptors must implement the corresponding count_* methods and those methods should be side-effect-free and return integers.
- instrument, if provided, must be a str.

Postconditions:
- The returned list contains only descriptor objects sourced from the registry and satisfying all given filters.
- The function does not mutate the registry or the descriptor objects (it only reads and calls count_* methods).

## Side Effects:
- No I/O, network calls, or global state mutations are performed by this function itself.
- It reads the module-level _known mapping and calls methods on descriptor objects; any side effects would originate from those descriptor methods (not from get_tunings).

## Control Flow:
flowchart TD
    Start --> SetSearch[Set search = '' or str.upper(instrument)]
    SetSearch --> GetKeys[List keys = list(_known.keys())]
    GetKeys --> ComputeInkeys[inkeys = search in keys]
    ComputeInkeys --> ForEachKey[For each key x in keys]
    ForEachKey --> CheckInstrument{instrument is None?\nOR (inkeys is False and x starts with search?)\nOR (inkeys is True and search == x?)}
    CheckInstrument -- False --> NextKey[continue]
    CheckInstrument -- True --> FilterDecision{nr_of_strings is None?\nnr_of_courses is None?}
    FilterDecision -- both None --> AddAll[add all values from _known[x][1]]
    FilterDecision -- only nr_of_strings --> FilterStrings[add values where count_strings() == nr_of_strings]
    FilterDecision -- only nr_of_courses --> FilterCourses[add values where count_courses() == nr_of_courses]
    FilterDecision -- both set --> FilterBoth[add values where both counts match]
    AddAll --> NextKey
    FilterStrings --> NextKey
    FilterCourses --> NextKey
    FilterBoth --> NextKey
    NextKey --> ForEachKey
    ForEachKey --> End[return result list]

## Examples:
1) List all tunings:
    all_tunings = get_tunings()
    # all_tunings is a list of all tuning descriptor objects in the registry

2) Tunings for the exact "GUITAR" instrument key (case-insensitive input):
    guitar_tunings = get_tunings("guitar")
    # If "GUITAR" exists as a registry key, only its tunings are returned.

3) Tunings for instruments whose key starts with "GUITAR":
    partial = get_tunings("GUIT")
    # If "GUIT" is not an exact key but some keys begin with "GUIT", those keys' tunings are included.

4) 6-string tunings for guitars:
    six_string = get_tunings("guitar", nr_of_strings=6)
    if not six_string:
        # handle empty result (no matching tunings)
        pass

5) Handling common errors:
    try:
        t = get_tunings(123)  # incorrect type for instrument
    except TypeError:
        # instrument must be a str; handle the error
        pass

    try:
        t = get_tunings("guitar", nr_of_strings=6)
    except NameError:
        # registry (_known) is not initialized
        pass

Notes:
- Prefer checking for an empty list (no matches) rather than relying on exceptions for "not found" cases.
- If you need stricter behavior (e.g., raising a custom exception when no tunings match), wrap this function or add validation before calling it.

## `mingus.extra.tunings.get_instruments` · *function*

## Summary:
Returns a sorted list of instrument names discovered in the module-level registry, producing a lexicographically ordered list of the first element of each registry entry.

## Description:
This function reads a module-level mapping named _known and extracts the element at index 0 from each entry in that mapping, returning those elements as a sorted list.

Known callers within the provided context:
    - No callers were found in the supplied source snippet. In typical usage within a tunings/extra module, this helper is intended for use by UI, listing, or discovery utilities that need an alphabetized list of instrument names available in the tunings registry.

Why this logic is extracted:
    - It centralizes the small but repeated task of enumerating instrument display names from the internal registry and ensures a consistent lexicographic ordering for callers. Extracting this avoids duplicating the comprehension + sort logic and isolates the single responsibility: "produce a sorted list of the primary name for each registered instrument."

## Args:
    None

## Returns:
    list
        A list containing the first element (index 0) of each value in the module-level mapping _known, sorted in ascending (lexicographic) order.
        - If _known is empty, returns an empty list [].
        - The list elements are exactly whatever type _known[upname][0] yields (commonly strings representing instrument names).

## Raises:
    NameError
        If the module-level name _known is not defined at call time, a NameError will occur when the function attempts to iterate over it.
    IndexError
        If any value in _known is an indexable container with length 0 (so accessing [0] is invalid), an IndexError will be raised when that entry is accessed.
    TypeError
        If the extracted items are of types that cannot be compared to each other during sorting (e.g., mixture of incompatible types), Python's sort will raise a TypeError.
    Any exception raised by iterating the _known mapping itself (e.g., if _known implements __iter__ but its iterator raises) will propagate unchanged.

## Constraints:
Preconditions:
    - A module-level variable named _known must exist and be iterable (supporting iteration over keys).
    - For each key in _known, _known[key] must be an indexable sequence/collection with at least one element so that _known[key][0] is valid.
Postconditions:
    - Returns a new list (does not mutate _known) containing the primary element (index 0) of each entry from _known, sorted ascending.
    - No module-level state is altered by the function.

## Side Effects:
    - None intrinsic: the function performs no I/O and does not mutate any global state.
    - Side effects may occur indirectly if iterating _known or accessing its values triggers user-defined behavior (e.g., properties or computed items that have side effects); such side effects are not introduced by this function itself but will propagate.

## Control Flow:
flowchart TD
    Start --> CheckKnownExists
    CheckKnownExists -->|_known defined and iterable| IterateKeys
    CheckKnownExists -->|_known undefined| RaiseNameError
    IterateKeys --> AccessValue0
    AccessValue0 -->|value has index 0| AppendToList
    AccessValue0 -->|value missing index 0| RaiseIndexError
    AppendToList --> AfterCollect
    AfterCollect --> SortList
    SortList -->|items sortable| ReturnList
    SortList -->|items not sortable| RaiseTypeError

## Examples:
Example 1 — normal usage
    - Precondition: _known is a dict-like mapping such that:
        _known = {
            'ACOUSTIC_GUITAR': ('Acoustic Guitar', other_data),
            'PIANO': ('Piano', other_data),
            'VIOLIN': ('Violin', other_data)
        }
    - Call: get_instruments()
    - Result: ['Acoustic Guitar', 'Piano', 'Violin']

Example 2 — empty registry
    - Precondition: _known = {}
    - Call: get_instruments()
    - Result: []

Example 3 — error handling
    - If a registry entry is malformed: _known['X'] = ()
      Then calling get_instruments() will raise IndexError when attempting to access [0] for that entry.
    - Caller should guard if registry may contain malformed entries:
        try:
            instruments = get_instruments()
        except IndexError:
            # handle or log malformed registry entry
            raise

