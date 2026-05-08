# `instrument.py`

## `mingus.containers.instrument.Instrument` · *class*

## Summary:
Represents a musical instrument's basic metadata and playable pitch range. Provides utilities to set and validate the instrument's playable bounds and to test whether single or multiple notes fall within that range.

## Description:
Instrument is a lightweight container-class used to describe an instrument's identity (name), clef, optional tuning, and the inclusive pitch range it can play. Typical call sites:
- Instrument instances are created by client code or instrument-configuration factories when describing available instrumentation for an arrangement, score, or playback engine.
- Consumers call set_range to initialize or modify the playable bounds, and call note_in_range / notes_in_range / can_play_notes to validate whether one or more pitches are playable.

Responsibility boundary:
- Instrument stores descriptive metadata (name, clef, tuning) and enforces/validates simple range semantics. It does not implement sound playback, tuning algorithms, or advanced range mapping — those belong to other modules (e.g., a StringTuning class if present).
- It centralizes input normalization for ranges and note arguments (accepting string note names or Note-like objects) and raises UnexpectedObjectError for invalid object shapes.

## State:
Attributes (class-level defaults, instance may override):
- name (str)
    - Default: "Instrument"
    - Expected: human-readable identifier for the instrument instance (e.g., "Guitar", "Violin").
- range (sequence of two Note-like objects)
    - Default: (Note("C", 0), Note("C", 8))
    - Semantic: inclusive lower and upper bounds for playable notes; accessed as range[0] (low) and range[1] (high).
    - Valid values: an indexable sequence (tuple, list, etc.) with at least two elements. Elements should be Note-like (expose .name and support comparisons with Note instances).
    - Note: set_range assigns self.range to the exact sequence object passed in. If strings are passed and converted, the method mutates the provided sequence in-place when conversion occurs (so prefer passing a mutable sequence such as a list when using string representations).
- clef (str)
    - Default: "bass and treble"
    - Semantic: descriptive clef(s) used for display or notation; purely informational.
- tuning (optional object)
    - Default: None
    - Semantic: optional reference to a tuning object (for multi-string instruments). Instrument does not operate on tuning; it merely stores a reference.

Class invariants:
- self.range must always be an indexable sequence with at least two elements when methods performing comparisons are called.
- self.range[0] is expected to be Note-like (the class enforces this in set_range for the converted branch; callers should ensure similar conditions if setting range directly).
- Comparison operators (>= and <=) must be supported between Note-like objects used as range endpoints and the Note-like objects passed to note_in_range.

## Lifecycle:
Creation:
- Instantiate with no arguments:
    inst = Instrument()
- The constructor does not set up additional invariants beyond the class-level defaults; callers commonly call set_range afterward if a custom range is required.

Usage (typical sequence):
1. Optionally configure the range:
    - inst.set_range(["E2", "E6"])  # converts strings to Notes (requires a mutable sequence)
    - or inst.set_range([Note("E", 2), Note("E", 6)])  # provide Note-like objects directly
2. Query single-note capability:
    - inst.note_in_range("E4")  # accepts string or Note-like object
3. Query multiple notes:
    - inst.can_play_notes(["E2", "F#3"]) or inst.notes_in_range(notes_object)
    - can_play_notes accepts: a single Note or string, a Python list of Notes/strings, or an object exposing a .notes attribute (its .notes value is used).
4. Use repr(inst) to obtain a human-readable description of name and bounds.

Destruction:
- No special cleanup required. Instrument exposes no context-manager protocol and implements no close() method.

Sequencing constraints:
- Methods that perform comparisons assume self.range is indexable and contains valid endpoints; callers should set a valid range before performing comparisons to avoid IndexError or TypeError.

## Method Map:
graph TD
    Create[Instrument()] --> SetRange[set_range(range)]
    SetRange --> QuerySingle[note_in_range(note)]
    SetRange --> QueryMulti[can_play_notes(notes)]
    QueryMulti --> QuerySingle
    notes_in_range --> can_play_notes
    __repr__ --> ReadState[reads name & range]

(Above graph shows typical method dependencies and invocation relationships:
- set_range establishes range used by note_in_range and can_play_notes.
- can_play_notes delegates per-item checks to note_in_range.
- notes_in_range is a thin alias for can_play_notes.
- __repr__ reads name and range to format a display string.)

## Methods (behavior summary and implementation notes):
- __init__(self)
    - Behavior: no parameters; performs no initialization beyond instance creation. Instances inherit class-level defaults unless overridden by caller attributes.
    - Raises: None specific to this method.

- set_range(self, range)
    - Args:
        - range: indexable sequence with at least two elements, accessed as range[0] (lower) and range[1] (upper).
          * If range[0] is a string (instance of six.string_types), the implementation will convert both endpoints using Note(range[0]) and Note(range[1]) and assign them back into the sequence at indices 0 and 1 (in-place mutation).
          * If range[0] is not a string, no conversion is attempted; the method then validates that range[0] exposes a "name" attribute (Note-like). No validation is performed for range[1] in this branch.
    - Postcondition:
        - self.range is set to reference the provided sequence (no copying).
        - If conversion branch ran, self.range[0] is guaranteed Note-like; range[1] will be Note-like if conversion ran or the caller supplied a Note-like object.
    - Raises:
        - UnexpectedObjectError if, after any conversion, range[0] does not expose a "name" attribute.
        - IndexError if the provided sequence has fewer than two elements (implicit).
        - TypeError if attempting in-place assignment into an immutable sequence (e.g., tuple) during conversion.
        - Propagates exceptions raised by Note(...) during conversion (e.g., parsing errors).

- note_in_range(self, note)
    - Args:
        - note: either a string (six.string_types) acceptable to Note(...) or a Note-like object exposing "name".
    - Behavior:
        - If note is a string, construct Note(note) and use that instance for comparisons.
        - Validate the object: if it is not a string and lacks a "name" attribute, raise UnexpectedObjectError.
        - Compare inclusively: return True if self.range[0] <= note <= self.range[1] using >= and <= comparisons as implemented on Note-like objects; otherwise return False.
    - Returns:
        - bool: True if inclusive bounds check passes; False otherwise.
    - Raises:
        - UnexpectedObjectError if the note is neither a string nor has a "name" attribute.
        - Any TypeError or other exceptions propagated from failed comparisons or Note(...).

- notes_in_range(self, notes)
    - Behavior: convenience alias; returns self.can_play_notes(notes).
    - Purpose: improves API readability; delegates normalization and checking to can_play_notes.

- can_play_notes(self, notes)
    - Args:
        - notes: one of:
            * a single Note-like object or string,
            * a Python list of Note-like objects and/or strings,
            * any object exposing a .notes attribute (the attribute value is used as the collection).
    - Normalization rules:
        - If the input has a .notes attribute, replace notes with notes.notes.
        - If the normalized value is not an instance of list, wrap it into a list: notes = [notes].
          (Note: only list instances are treated as multi-item containers; other iterables are wrapped as a single element.)
    - Behavior:
        - Iterate normalized list and return False immediately if any element fails note_in_range. If every element passes, return True.
        - An empty list yields True.
    - Returns:
        - bool: True if all items are in-range; False if any are out-of-range.
    - Raises:
        - UnexpectedObjectError and any exceptions that propagate from note_in_range or Note(...).

- __repr__(self)
    - Behavior:
        - Returns string formatted as "%s [%s - %s]" % (self.name, self.range[0], self.range[1]).
        - Uses the string conversion of the range endpoints (relies on Note.__str__/__repr__).
    - Raises:
        - IndexError / TypeError if self.range is not indexable with two elements.
        - AttributeError if self.name is missing or conversion to string on range endpoints triggers attribute access errors.
        - No explicit validation; relies on set_range and caller discipline to maintain valid state.

## Raises:
Summary of exceptions raised by Instrument methods (what triggers them):
- UnexpectedObjectError
    - Raised by set_range when the lower bound is not Note-like after attempted conversion.
    - Raised by note_in_range when the provided argument is not a string and lacks a "name" attribute.
- IndexError (implicit)
    - Possible when calling set_range or __repr__ with a sequence containing fewer than two elements.
- TypeError (implicit)
    - Possible when set_range attempts to assign into an immutable sequence, or when comparisons are invalid between objects.
- Exceptions raised by Note(...) constructor or its comparison operations are propagated directly (e.g., parsing errors, invalid note strings).

## Example:
- Create and inspect an instrument:
    inst = Instrument()
    repr(inst)  # "Instrument [C0 - C8]" (actual format depends on Note string representations)

- Set a range using strings (use a mutable sequence so in-place conversion succeeds):
    inst.set_range(["E2", "E6"])  # converts both endpoints to Note instances, mutates the list, and stores it

- Check single note:
    inst.note_in_range("E4")  # True if E4 is between E2 and E6 inclusive

- Check multiple notes:
    inst.can_play_notes(["E2", "F#3", Note("E",6)])  # returns True only if all notes are within range

- Use the alias:
    inst.notes_in_range(notes_collection)  # delegated to can_play_notes

Implementation hints for reimplementation:
- Rely on Note(...) to parse string representations and on Note comparison operators for range checks.
- Use six.string_types to detect string inputs.
- When converting strings in set_range, convert both endpoints and assign them back into the provided mutable sequence before assigning self.range to it.
- Be explicit about not treating non-list iterables as multi-item containers in can_play_notes (wrap them into a single-element list).

### `mingus.containers.instrument.Instrument.__init__` · *method*

## Summary:
Creates a new Instrument instance without performing any instance-specific initialization; the object inherits class-level default attributes and requires explicit configuration (e.g., set_range) before use.

## Description:
Known callers and contexts:
- Client code and instrument-configuration factories create Instrument instances during arrangement, score assembly, or playback engine setup. Typical usage is:
    - inst = Instrument() immediately followed (optionally) by inst.set_range(...) or other configuration calls.
- Lifecycle stage: invoked at object construction time when a new Instrument is required; this is the first step of the Instrument lifecycle.

Why this logic is a dedicated method:
- Having an explicit constructor (even if it is currently a no-op) centralizes instance creation and provides a stable place for future initialization logic and for subclasses to call super().__init__().
- It documents that there are intentionally no side-effects or attribute mutations at construction time — configuration is handled by separate methods (e.g., set_range).

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
Attributes READ:
    - None (does not access any self.<attr> attributes)

Attributes WRITTEN:
    - None (does not assign or mutate any self.<attr> attributes)
    - Note: the instance is created and bound to self by the Python object model, but no explicit attribute assignments occur within this method.

## Constraints:
Preconditions:
    - None. The method accepts no arguments and imposes no constraints on the object prior to invocation.

Postconditions:
    - The resulting instance remains with class-level default attributes (for example: name, range, clef, tuning) until explicitly modified by other methods or by direct attribute assignment.
    - No instance attributes are guaranteed to be initialized by this method beyond what Python provides for any new object.

## Side Effects:
    - None. The constructor performs no I/O, no calls to external services, and makes no mutations to objects outside the newly created instance.
    - Any exceptions that could occur during normal object allocation are standard Python allocation errors and not induced by this method's body.

## Implementation notes for reimplementation:
    - Implement as an empty constructor (no-argument __init__ that performs no attribute assignments).
    - Keep the method as a dedicated hook so subclasses can extend initialization via super().__init__().
    - Do not perform implicit configuration here; rely on explicit configuration methods (e.g., set_range) to establish invariants.

### `mingus.containers.instrument.Instrument.set_range` · *method*

## Summary:
Assigns the provided two-element, indexable sequence to the instance as the instrument's playable range, converting string note names to Note objects when the first element is a string.

## Description:
Normalizes and validates a two-element sequence representing the lower and upper bounds of an instrument's range and stores that sequence on the instance.

Known callers and context:
- Intended to be called by instrument configuration code or client code during instrument initialization or when updating an instrument's range. There are no direct callers within this file.

Why this is a separate method:
- Centralizes input normalization (string → Note) and minimal validation (presence of a "name" attribute on the lower bound). This avoids duplicating conversion/validation logic across the codebase and provides a single place to manage how ranges are accepted and stored.

## Args:
    range (indexable sequence): A sequence with at least two elements, accessed as range[0] (lower bound) and range[1] (upper bound).
        - Allowed element types:
            * A string type (any type in six.string_types). If range[0] is a string, the method will convert both range[0] and range[1] by calling Note(...) and assign the results back into the sequence at indices 0 and 1.
            * A Note-like object: any object that exposes a "name" attribute. If range[0] is already Note-like, no conversion is attempted.
        - Mutability: The method assigns into range[0] and range[1] when conversion occurs, so the sequence should be mutable (for example, a list). Passing an immutable sequence (for example, a tuple) containing strings will cause a TypeError at assignment time.

## Returns:
    None

## Raises:
    UnexpectedObjectError:
        - Raised explicitly if, after any conversions, the object at range[0] does not have a "name" attribute.
        - Exact message format produced by the method:
          "Unexpected object '%s'. Expecting a mingus.containers.Note object"
          where %s is formatted using Python's percent formatting; the string representation (str(range[0])) is substituted.
    IndexError (implicit):
        - If the provided sequence does not contain at least two elements, indexing range[0] or range[1] will raise IndexError.
    TypeError (implicit):
        - If the provided sequence is immutable and the method attempts to assign Note instances into range[0] or range[1], a TypeError will be raised.
        - If the Note(...) constructor raises a TypeError for invalid inputs, that exception will propagate.
    Other exceptions from Note(...):
        - Any exception raised by Note(...) during conversion will propagate to the caller.

## Behavior details and edge cases:
    - The method first checks only range[0] for string-ness using isinstance(range[0], six.string_types).
        * If range[0] is a string: both range[0] and range[1] are converted by executing Note(range[0]) and Note(range[1]) and the results are assigned back into the sequence at indices 0 and 1 respectively.
        * If range[0] is not a string: no conversion is attempted; the method then verifies that range[0] has a "name" attribute. No validation is performed on range[1] in this branch.
    - Consequence: range[1] may be one of:
        * a Note-like object provided by the caller,
        * a Note instance produced by conversion when the conversion branch ran,
        * or a non-Note value left unchanged if the conversion branch did not run and the caller supplied a non-Note for range[1].
      Callers that require both ends to be Note-like should either supply strings for range[0] (which triggers conversion for both elements) or supply Note-like objects for both elements.
    - The method mutates the input sequence when performing conversions (assigns Note instances into indices 0 and 1). It does not make a copy of the sequence.

## State Changes:
    Attributes READ:
        - None of the instance's attributes are read.
        - The method reads the provided sequence at indices 0 and 1.
    Attributes WRITTEN:
        - self.range is set to reference the exact sequence object passed in.
        - The provided sequence object may be mutated in-place (range[0] and range[1] may be replaced by Note instances).

## Constraints:
    Preconditions:
        - Caller must provide an indexable sequence with at least two elements.
        - Prefer a mutable sequence (list) if any element is a string to avoid assignment errors.
    Postconditions:
        - On successful return:
            * self.range references the same sequence object passed in.
            * self.range[0] is guaranteed to be Note-like (object exposing a "name" attribute).
            * self.range[1] will be Note-like if either the conversion branch ran (range[0] was a string) or the caller provided a Note-like object for range[1]; otherwise range[1] may remain an arbitrary value the caller supplied.

## Side Effects:
    - Mutates the passed-in sequence when converting string elements to Note instances.
    - No external I/O or service calls are performed.
    - Exceptions from invalid input or Note(...) are propagated to the caller.

### `mingus.containers.instrument.Instrument.note_in_range` · *method*

## Summary:
Check whether a given note falls within the instrument's playable range and return True or False; does not modify the instrument.

## Description:
This method is used to validate if a single musical pitch is playable on the instrument. Known internal callers:
- Instrument.can_play_notes: used while checking whether a collection of notes are playable; this method is invoked per-note.
- Instrument.notes_in_range: delegates to can_play_notes which calls this method.

Typical lifecycle/context:
- Called during input validation, playback preparation, or capability checks where the system needs to know whether an instrument can produce a particular pitch.
- Kept as a separate method because the same per-note range-check logic is reused by higher-level helpers (e.g., checks for single notes vs. lists of notes), and isolating it centralizes type conversion and error handling for note arguments.

## Args:
    note (str | object): A note to check.
        - If a string (any value matching six.string_types), the method constructs a new Note instance from it.
        - Otherwise the object must expose a "name" attribute (a Note-like object).
        - The object must be comparable with Note instances using the >= and <= operators (i.e., implement appropriate comparison methods).

## Returns:
    bool: True if the provided note is greater than or equal to self.range[0] and less than or equal to self.range[1] (inclusive); False otherwise.
    Edge cases:
    - If the note equals exactly the lower or upper bound, the method returns True (bounds are inclusive).
    - If comparisons are not supported between the provided note and the range endpoints, a TypeError (or other comparison-related exception) may propagate from the comparison operations.

## Raises:
    UnexpectedObjectError: Raised when the provided argument is not a string and does not have a "name" attribute (i.e., is not a Note-like object).
    Note: The method does not explicitly raise comparison errors; if comparisons between the note and range endpoints are invalid, those exceptions propagate from the underlying comparison operations (e.g., TypeError).

## State Changes:
    Attributes READ:
        - self.range: the method reads this attribute and its first two elements self.range[0] and self.range[1] to perform the comparison.
    Attributes WRITTEN:
        - None. The method does not modify self or its attributes.

## Constraints:
    Preconditions:
        - self.range must be an indexable sequence (or similar) with at least two elements where self.range[0] and self.range[1] are Note-like objects that support comparison with the argument.
        - If passing a non-string object, it must have a "name" attribute; otherwise the method raises UnexpectedObjectError.
    Postconditions:
        - The instrument's state (including self.range) remains unchanged.
        - Return value is a boolean indicating whether the note lies within [self.range[0], self.range[1]] inclusive.

## Side Effects:
    - If the input is a string, a new Note instance is constructed (temporary object allocation).
    - No I/O is performed.
    - No external services are called.
    - No mutation of objects outside self is performed by this method.

### `mingus.containers.instrument.Instrument.notes_in_range` · *method*

## Summary:
Delegates validation to the instrument's multi-note checker to determine whether the provided note(s) are playable within the instrument's configured range. Does not modify the instrument's state.

## Description:
This small wrapper forwards its argument to self.can_play_notes(notes) and returns that result unchanged. It exists to expose a more semantically named API (notes_in_range) for callers that need a simple, descriptive method to ask whether one or many notes fall inside the instrument's range.

Known callers and usage context:
- External code that needs a descriptive, public-facing check for playability will call this method during validation stages before assigning notes to instruments, arranging parts, or attempting playback.
- It is also used interchangeably with can_play_notes in higher-level code; can_play_notes contains the normalization and per-note checks while this method provides a convenience alias.

Why this logic is a separate method:
- Keeps a clear, intention-revealing API: callers can use notes_in_range for readability without needing to know about the normalization semantics implemented in can_play_notes.
- Prevents duplication by delegating to can_play_notes which centralizes handling of different input shapes (single Note, string, list, or an object with a .notes attribute).

## Args:
    notes (mingus.containers.note.Note | str | list | object with .notes):
        - A single Note instance or a string acceptable to the Note constructor (e.g., "C-4"),
        - OR a list of Note instances and/or note strings,
        - OR any object that exposes a .notes attribute (that attribute's value is treated as the collection).
        - If a single non-list item is provided, it will be treated as a single-element list by the delegated can_play_notes method.
        - Note: Only Python list instances are treated as multi-note containers by can_play_notes; other iterables (tuples, sets, generators) are treated as a single element unless converted to list first.

## Returns:
    bool:
        - True if all normalized notes are within the instrument's configured range (self.range).
        - False as soon as any normalized note is found out-of-range.
        - True for an empty list of notes (nothing to disqualify).

## Raises:
    UnexpectedObjectError:
        - Propagated when a provided element is neither a Note-like object (no .name attribute) nor a valid string for Note construction; raised by note_in_range and thus by can_play_notes.
    Note constructor errors (e.g., parsing/format errors from mingus.containers.note.Note):
        - If a string cannot be parsed into a Note instance, the Note constructor may raise an error which is propagated.

## State Changes:
    Attributes READ:
        - self.range (consulted indirectly via note_in_range during per-note comparisons)
        - self.note_in_range (method is called for each normalized note)
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - self must implement can_play_notes(notes) and note_in_range(note) as expected.
        - When passing strings, they must be valid representations accepted by mingus.containers.note.Note.
        - Callers should be aware that only list instances are treated as multi-item collections by the delegated logic; convert other iterables to list if intended.

    Postconditions:
        - No attributes of self are modified.
        - The returned boolean accurately reflects the result of self.can_play_notes(notes): True means every normalized note passed self.note_in_range; False means at least one did not.

## Side Effects:
    - No I/O, network, or filesystem interactions.
    - May cause temporary Note instances to be constructed if string representations are provided (inside Note constructor calls invoked by note_in_range).
    - No mutation of objects external to self is performed by this method itself; any side effects originate from called functions (e.g., Note constructor) and are propagated.

### `mingus.containers.instrument.Instrument.can_play_notes` · *method*

## Summary:
Checks whether every provided note is playable by this instrument (i.e., falls within the instrument's configured range). Does not modify the instrument's state.

## Description:
This helper method accepts a single note, a list of notes, or an object that exposes a .notes attribute and returns True only if every note is within the instrument's allowed range (determined by note_in_range). It is used wherever callers must validate that one or more notes can be produced by this instrument before further processing — for example, Instrument.notes_in_range delegates directly to this method.

Why this is a separate method:
- Centralizes the logic that accepts multiple input shapes (single Note, list of Note, or an object with .notes) and normalizes them into a list for per-note range checks.
- Keeps the per-note validation in a single place while delegating the actual comparison to note_in_range, avoiding code duplication for callers that need list or single-note support.

Known callers:
- Instrument.notes_in_range(notes) — simply returns this method's result.
- Intended for use by any higher-level code that must validate whether notes are playable on the instrument before assignment or playback.

## Args:
    notes (mingus.containers.note.Note | str | list | object with .notes):
        - A single Note instance or a string acceptable to Note (e.g. "C-4"), or
        - A list of Note instances / note strings, or
        - Any object exposing a .notes attribute (whose value is treated as the note collection).
        - If a single non-list item is passed, it is treated as a single-element list.
        - Only Python list instances are treated as "multiple" items; other iterables (tuples, sets, generators) are NOT treated as lists and will be wrapped as a single element.

## Returns:
    bool:
        - True if all notes (after normalization) are in-range according to self.note_in_range.
        - False as soon as any note is found out-of-range.
        - True for an empty list (no notes to disqualify).

## Raises:
    UnexpectedObjectError:
        - Raised (propagated) if an element is neither a Note-like object (no .name attribute) nor an acceptable string representation — this originates from self.note_in_range.
    NoteFormatError (or other Note constructor errors):
        - May be propagated if a string note cannot be parsed/constructed into a Note instance when note_in_range attempts Note(string). This originates from mingus.containers.note.Note.

## State Changes:
    Attributes READ:
        - self.range (indirectly, via self.note_in_range which compares notes to self.range)
        - self.note_in_range (method is invoked)
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - self must implement note_in_range(note) and it must reliably return a boolean or raise the documented exceptions.
        - When passing strings as notes, they must be valid note representations accepted by mingus.containers.note.Note.
        - Callers should be aware that only list instances are treated as a multi-note container. Passing a tuple or other iterable will be treated as a single item unless converted to a list first.

    Postconditions:
        - No attributes of self are modified.
        - Return value True guarantees each normalized element returned True from self.note_in_range.
        - Return value False guarantees at least one normalized element returned False from self.note_in_range (the method short-circuits on the first failure).

## Side Effects:
    - No I/O, network, or filesystem activity.
    - May allocate temporary Note objects if string representations are provided (inside note_in_range/Note constructor).
    - No mutation of objects outside self is performed by this method itself (it only reads). Any exceptions raised by Note construction or note_in_range are propagated.

### `mingus.containers.instrument.Instrument.__repr__` · *method*

## Summary:
Return a concise, human-readable string that identifies the instrument and its playable range (low and high boundary).

## Description:
This method produces the representation used by repr() and debugging/printing for an Instrument instance. It formats the instrument's name together with the textual representation of the low and high bounds of its range, producing a string of the form "Name [low - high]".

Known callers / invocation contexts:
- The built-in repr() and interactive REPL when an Instrument instance is inspected.
- Any logging, debugging, or UI display code that calls repr() (or implicitly converts objects to strings).
- It is typically invoked at presentation or debugging stages of an application's lifecycle, not during note-processing or range-validation logic.

Why this is a separate method:
- Provides a single, consistent textual representation used by Python's object inspection and logging facilities.
- Keeps formatting logic centralized instead of being duplicated wherever an Instrument's summary is needed.

## Args:
None.

## Returns:
str
- A string formatted as "%s [%s - %s]" where:
  - the first %s is self.name (expected to be a string-like identifier for the instrument),
  - the second %s is the string conversion of self.range[0] (the lower bound Note-like object),
  - the third %s is the string conversion of self.range[1] (the upper bound Note-like object).
- Example: "Guitar [E2 - E6]" (actual note formatting depends on the Note.__str__/__repr__ implementation).
- Edge-case return values: there is no special-case return; any exception raised while accessing attributes will propagate instead of returning a value.

## Raises:
- IndexError: if self.range is a sequence with fewer than two elements (attempting to access index 0 or 1).
- TypeError: if self.range is None or not subscriptable (e.g., an integer), indexing will raise a TypeError.
- AttributeError: if self.name is missing (e.g., someone replaced the instance attributes), or if converting range elements to string triggers attribute access errors.
Notes:
- The class's set_range method enforces that range elements are Note objects (or convertible from strings) and raises UnexpectedObjectError on invalid input; however, __repr__ itself does not perform validation and will simply propagate low-level exceptions if attributes are malformed.

## State Changes:
Attributes READ:
- self.name
- self.range (and, implicitly, self.range[0] and self.range[1])

Attributes WRITTEN:
- None. __repr__ does not modify the object's state.

## Constraints:
Preconditions:
- Preferably, self.name should be set to a string-like identifier.
- Preferably, self.range should be a sequence (tuple/list) with at least two elements where each element is a Note-like object (the class normally ensures this via set_range).

Postconditions:
- No mutation of the instrument instance.
- Returns a single str describing the instrument and its range if no exceptions occur.

## Side Effects:
- None: no I/O, no external service calls, and no modifications to objects outside self. The only effects are reading attributes and invoking their __str__/__repr__ methods (which are expected to be side-effect-free).

## `mingus.containers.instrument.Piano` · *class*

## Summary:
A concrete Instrument subclass representing a standard piano. Provides the canonical name ("Piano") and a default inclusive playable range spanning from F0 to B8 (as Note instances); all playable-note logic is inherited from Instrument.

## Description:
The Piano class is a minimal, declarative specialization of mingus.containers.instrument.Instrument that encodes the common metadata for a piano:
- Use cases: instantiate when you need a ready-to-use Instrument object representing a standard piano (e.g., in arrangement descriptions, score instrumentation, or simple playback setups).
- Known callers/factories: client code or instrument-configuration factories that create Instrument instances for scoring or playback. Because Piano does not implement additional behavior, callers typically use Instrument methods (set_range, note_in_range, can_play_notes) on Piano instances.
- Motivation / responsibility boundary: Piano exists to provide a canonical name and default range for a piano so callers do not need to call set_range manually for the most common piano bounds. It intentionally does not override Instrument behavior — it only supplies default metadata.

See: mingus.containers.instrument.Instrument documentation for full descriptions of inherited methods, state semantics, and validation behaviors. Piano relies on those semantics and does not reimplement them.

## State:
- name (str, class attribute)
    - Value: "Piano"
    - Purpose: human-readable instrument identifier used by __repr__ and by any code reading an instrument's name.
    - Constraints: expected to be a short, display-friendly string.

- range (tuple of two Note instances, class attribute)
    - Value: (Note("F", 0), Note("B", 8))
    - Type: tuple with exactly two elements by default (immutable at the class level).
    - Semantic: inclusive lower and upper bounds for playable notes (range[0] is low bound, range[1] is high bound).
    - Notes:
        - The Note(...) constructors for the endpoints are executed when the module/class is evaluated (import time), so any exceptions raised by Note(...) (parsing errors, etc.) will occur at import time.
        - Because the class-level default is a tuple (immutable), it will not be mutated by Instrument.set_range conversion logic that attempts in-place mutation; callers who want to override the range should call set_range on the instance with an appropriate sequence (list preferred for in-place conversion when passing strings).

- Inherited attributes (see Instrument docs):
    - clef (str): descriptive clef(s)
    - tuning (optional): tuning reference
    - Any other Instrument public attributes and invariants apply unchanged.

Class invariants (expected but not enforced here beyond Instrument behavior):
- self.range is indexable with at least two elements when used by Instrument methods.
- range endpoints are Note-like objects (supporting comparisons and string conversion); the lower bound should compare <= the upper bound for meaningful results.

## Lifecycle:
- Creation:
    - Instantiate with no arguments: p = Piano()
    - Implementation detail: Piano.__init__ delegates to Instrument.__init__ (i.e., calls Instrument.__init__(self)). No additional initialization parameters are required or supported.
    - Import-time note: range endpoints (Note("F",0), Note("B",8)) are constructed at module/class evaluation, so import may raise if Note fails to construct.

- Usage:
    - Query methods (inherited from Instrument):
        - p.note_in_range(note) — check whether a single note (string or Note-like) is within the piano's range.
        - p.can_play_notes(notes) / p.notes_in_range(notes) — check whether one or more notes are playable.
        - p.set_range(range) — override the instance's range (see Instrument.set_range semantics; pass a mutable sequence such as a list if supplying string endpoints to allow in-place conversion).
    - Typical sequencing:
        1. Instantiate: p = Piano()
        2. Optionally override range: p.set_range(["A0", "C8"])  (use a list to allow in-place conversion of strings)
        3. Validate notes: p.can_play_notes(["C4", "G4"])
    - No special ordering is required beyond the general Instrument expectation that a valid range be present before performing range checks.

- Destruction:
    - No cleanup responsibilities. Piano does not implement context-manager protocol or close().

## Method Map:
graph TD
    PianoClass[Piano class constants] --> Instantiate[Piano().__init__]
    Instantiate --> InstrumentInit[Instrument.__init__]
    InstrumentInit --> SetRange[set_range(range)]
    SetRange --> NoteInRange[note_in_range(note)]
    NoteInRange --> CanPlayNotes[can_play_notes(notes)]
    CanPlayNotes --> NotesInRange[notes_in_range(notes)]
    Repr[__repr__] --> ReadState[name & range]

(Notes: Piano does not add new methods; all runtime behavior is provided by Instrument. The graph shows how a Piano instance is created and how its inherited methods typically depend on range/state.)

## Raises:
- Import-time:
    - Any exception raised by Note("F", 0) or Note("B", 8) during module/class evaluation will surface at import time (e.g., parsing or validation exceptions raised by Note constructor). This is a notable difference from instances where range endpoints are created lazily.
- Instantiation:
    - Piano.__init__ itself does not introduce new exceptions beyond those Instrument.__init__ may raise. If Instrument.__init__ raises, instantiation propagates that exception.
- Runtime:
    - Methods inherited from Instrument may raise:
        - UnexpectedObjectError (see Instrument.note_in_range and Instrument.set_range behavior) if callers pass invalid objects.
        - IndexError/TypeError may result from invalid range state if callers overwrite self.range with an invalid sequence.

## Example:
- Create a Piano instance and check notes:
    p = Piano()
    p.note_in_range("C4")            # True if C4 falls between F0 and B8 inclusive
    p.can_play_notes(["A0", "C8"])   # True if both endpoints are within the piano range

- Override the instance range (use a list when supplying strings so Instrument.set_range can convert in-place):
    p = Piano()
    p.set_range(["A0", "C8"])        # converts strings to Note instances and assigns the list to p.range

- Important caveat:
    - Because the class default range is an immutable tuple, passing the default tuple into code that expects a mutable range (and attempts in-place mutation) will raise. If you need to mutate p.range in-place, replace it with a mutable sequence first or call set_range with a list.

### `mingus.containers.instrument.Piano.__init__` · *method*

## Summary:
Delegates construction to the base Instrument initializer without altering instance state; instantiates a Piano object that retains the class-level default name and range.

## Description:
Known callers and context:
- Client code and instrument-configuration factories that create instrument instances for arrangements, scores, or playback typically call this during normal object construction (e.g., p = Piano()).
- This method is invoked at the object construction/lifecycle stage: it runs as part of Piano() instantiation.

Why this logic is its own method:
- Explicitly defining Piano.__init__ and delegating to Instrument.__init__ documents the inheritance intent and provides a stable override point for future piano-specific initialization without changing call sites.
- Keeping the delegation as a separate method preserves normal Python subclassing semantics and makes the class declaration self-contained and clear to readers.

## Args:
- None

## Returns:
- None (constructor). The method returns implicitly after initializing via the base class; no value is returned.

## Raises:
- Propagates any exception raised by Instrument.__init__ (none expected in current implementation).
- Note: exceptions from creating Piano's class-level default range (Note("F", 0) and Note("B", 8)) occur at import/class evaluation time, not inside this __init__ method.

## State Changes:
Attributes READ:
- None explicitly read by this method. The instance will have access to class-level attributes (e.g., name, range) established at class definition time, but this method does not access them.

Attributes WRITTEN:
- None. This method does not set or mutate any self.<attr> fields itself; it simply delegates to the base initializer.

## Constraints:
Preconditions:
- The Piano class must have been defined successfully (class-level expressions, including Note(...) calls for the default range, must have completed without raising) before instantiation.
- No arguments are expected; callers must instantiate with zero parameters.

Postconditions:
- The returned object is a valid Piano instance whose attributes are the class-level defaults unless modified elsewhere (e.g., name remains "Piano", range remains the class default tuple of Note("F", 0) and Note("B", 8) unless the instance or Instrument.__init__ modifies them).
- No additional invariants beyond those guaranteed by Instrument.__init__ are introduced here.

## Side Effects:
- None local to this method: no I/O, no external service calls, and no mutation of objects outside self.
- Any side effects originate from Instrument.__init__ (currently none) or from earlier import-time evaluation of class-level defaults.

## `mingus.containers.instrument.Guitar` · *class*

## Summary:
Represents a Guitar instrument definition — a lightweight Instrument subclass that provides guitar-specific defaults (name, clef, inclusive playable range) and enforces a 6-note maximum when checking multi-note playability.

## Description:
Use this class to represent a guitar within arrangements, score metadata, or instrument-capacity checks. Guitar is a thin specialization of Instrument that:
- Supplies the canonical guitar name ("Guitar"), treble clef, and the default inclusive range from low E3 to high E7.
- Overrides the multi-note validation to immediately reject collections with more than six elements (models the practical limitation of six strings / six simultaneous notes).

Typical instantiation sites:
- Instrument configuration factories that build available instrument sets for a score or playback engine.
- Client code that needs a named instrument container to query whether notes or chords are playable.

Motivation and responsibility:
- Keep instrument metadata (name, clef, range) centralized while capturing a guitar-specific constraint (six-note maximum). Guitar delegates range-checking, object normalization, and actual Note parsing/comparison to its Instrument base and the Note type.

Note: Guitar depends on Instrument for most behavior — see the Instrument documentation for details about set_range, note_in_range, notes_in_range, and the semantics of passing strings vs Note-like objects.

## State:
Class and instance state relevant to reimplementation:

- name (str)
    - Default: "Guitar"
    - Purpose: human-readable instrument identifier
    - Valid values: any string; used in __repr__ and display.

- range (tuple[Note, Note])
    - Default: (Note("E", 3), Note("E", 7))
    - Type: pair (indexable sequence with two elements) of Note-like objects (lower bound, upper bound), inclusive.
    - Invariant: range[0] <= range[1] according to Note comparison semantics (the Instrument base relies on comparisons for checks). Endpoints must support comparison with Note instances.

- clef (str)
    - Default: "Treble"
    - Purpose: informational label used by notation/rendering layers.

- Instance attributes
    - Guitar.__init__ does not add new instance attributes beyond what Instrument.__init__ creates; Guitar primarily uses the class-level defaults above unless callers override them or call Instrument.set_range.

Class invariants:
- self.range is indexable and contains two Note-like endpoints before performing note comparisons.
- Note comparisons used by Instrument must be supported for endpoints and tested notes (>=, <=).
- can_play_notes maintains: if a caller passes an object to can_play_notes, Guitar will first attempt len(notes); callers must pass sized sequences or strings. This is a behavioral invariant introduced by Guitar.

## Lifecycle:
Creation:
- Instantiate with no arguments:
    g = Guitar()
- The constructor simply calls the Instrument base constructor. No additional arguments or factories are required.

Usage:
- Optionally adjust the playable range using Instrument.set_range if the default E3–E7 needs change. Example: g.set_range(["E", "C"]) or g.set_range([Note(...), Note(...)]). (See Instrument docs for set_range behavior and conversion rules.)
- Query single-note capability using Instrument.note_in_range or via g.can_play_notes for single-item containers, bearing in mind Guitar's len() pre-check (see caveats below).
- Query multi-note capability using g.can_play_notes(notes_collection).
- Typical call sequence:
    1. g = Guitar()
    2. (optional) g.set_range(...)  # if you need different bounds
    3. g.can_play_notes([...])     # check chord or collection playability

Destruction:
- No special cleanup; no context-manager support or close() required.

Sequencing and behavioral caveats:
- Guitar.can_play_notes performs a length check (len(notes) > 6) before delegating to Instrument.can_play_notes. Because this check uses len(notes) directly, callers should pass a sized object (list, tuple, string) or a type that implements __len__. Passing a single Note instance (which typically does not implement __len__) will raise TypeError at the len(...) call. This differs from Instrument.can_play_notes, which accepts a single Note-like object directly. To check a single Note on Guitar, wrap it in a list: g.can_play_notes([note]) or use g.note_in_range(note).

## Method Map:
graph TD
    A[Guitar.__init__] --> B[Instrument.__init__]
    C[can_play_notes(notes)] --> D{len(notes) > 6?}
    D -- yes --> E[return False]
    D -- no --> F[Instrument.can_play_notes(notes)]
    F --> G[note_in_range(note) per item]
    G --> H[Note comparisons and parsing via Note class]

(Explanation: can_play_notes first performs len() check; if the check passes it delegates to Instrument.can_play_notes which normalizes inputs and calls note_in_range on each item.)

## Raises:
Exceptions that can be raised by Guitar methods and when they occur:

- TypeError
    - Trigger: calling Guitar.can_play_notes with a value that does not implement __len__ (for example, a single Note instance, or an iterable without __len__) — the initial len(notes) call will raise TypeError. This is an important behavioral difference from Instrument.can_play_notes which accepts single Note-like values.

- UnexpectedObjectError (from mingus.containers.mt_exceptions)
    - Trigger: delegated from Instrument.note_in_range or Instrument.set_range when a provided object is neither a string nor Note-like (i.e., lacks a "name" attribute). Guitar itself does not raise this directly but will propagate it.

- Any exceptions from Note(...) construction or from comparison operators
    - Trigger: when Instrument or callers construct Note objects from strings or compare Note-like objects (parsing errors, invalid note names, or incompatibility in comparisons).

- No exceptions are raised by Guitar.__init__ itself beyond those the base Instrument.__init__ might raise.

## Example:
- Create a Guitar and check a chord represented as strings:
    g = Guitar()
    g.can_play_notes(["E4", "G4", "B4"])  # typical, returns True if all are within E3-E7 inclusive

- Large chord is immediately rejected:
    g.can_play_notes(["E4","G4","B4","D5","F#5","A5","C6"])  # returns False because > 6 items

- Single Note objects must be wrapped because Guitar uses len():
    from mingus.containers.note import Note
    n = Note("E", 4)
    g.can_play_notes(n)        # TypeError: len(n) if Note has no __len__
    g.can_play_notes([n])      # correct usage; delegates to Instrument.can_play_notes

- Changing the instrument range (delegates to Instrument.set_range):
    g.set_range(["E3", "E6"])  # see Instrument.set_range for conversion and mutation semantics

Notes for reimplementation:
- Subclass Instrument.
- Provide class attributes: name = "Guitar", clef = "Treble", range = (Note("E", 3), Note("E", 7)).
- Implement __init__ to call the base constructor.
- Implement can_play_notes to:
    1. Attempt len(notes); if len(notes) > 6 return False.
    2. Otherwise delegate to Instrument.can_play_notes(self, notes).
- Document and preserve the len-based early-return behavior (it intentionally limits to six items but introduces the requirement that notes be a sized object).
- Ensure the implementation propagates UnexpectedObjectError and Note-related exceptions exactly as Instrument does.

### `mingus.containers.instrument.Guitar.__init__` · *method*

## Summary:
Initializes a Guitar instance by invoking the Instrument base-class constructor so the instance inherits the instrument defaults (name, clef, range) defined on the class hierarchy without adding or mutating additional instance state.

## Description:
Known callers and context:
- Commonly called by client code and instrument-configuration factories when constructing a Guitar for use in scores, arrangements, or capability checks:
    - Example call sites: g = Guitar()
    - Typical lifecycle stage: object construction / initialization phase before any range configuration or capability checks.
- Also invoked indirectly whenever frameworks or factories instantiate instrument classes (e.g., when building an instrument set for a playback engine).

Why this logic is a separate method:
- It provides an explicit subclass constructor that calls the Instrument base constructor. This makes the subclass initialization intent explicit and preserves a clear location to add guitar-specific initialization later without changing call sites.
- It documents and enforces the inheritance of base Instrument semantics (defaults for name, clef, and range) rather than relying on implicit object creation semantics.

## Args:
- None

## Returns:
- None (constructors do not return a value). After the call, the Guitar instance is a usable object with class-level defaults from Guitar/Instrument; no return value is produced.

## Raises:
- None specific to Guitar.__init__.
- Behavior note: Guitar.__init__ simply delegates to Instrument.__init__. Instrument.__init__ is documented to perform no extra initialization and raise no exceptions; therefore Guitar.__init__ does not introduce new exceptions. If the base constructor is modified in future, any exceptions it raises will propagate through this call.

## State Changes:
Attributes READ:
- None explicitly read from the instance by this method. The constructor delegates to the base class which, per current implementation, does not read instance attributes during initialization.

Attributes WRITTEN:
- None by this method itself. The call to Instrument.__init__ performs no instance attribute writes beyond default Python object creation according to the base-class documentation; therefore Guitar.__init__ does not add or modify self.<attr> fields.

## Constraints:
Preconditions:
- Called on a newly-created Guitar instance (i.e., self is an instance of Guitar).
- No other preconditions; no arguments are required.

Postconditions:
- Guaranteed that the Instrument base constructor has been invoked.
- The Guitar instance will rely on the class-level defaults (Guitar.name, Guitar.clef, Guitar.range) unless the caller or later code mutates instance attributes or calls set_range.
- No additional instance attributes are created by this method.

## Side Effects:
- None: no I/O, no external service calls, and no mutations of objects outside self are performed by this method.

## Usage examples:
- Basic instantiation:
    g = Guitar()
    # g now refers to a Guitar instance that inherits the Instrument defaults (name, clef, range)

- Typical subsequent actions:
    g.set_range(["E3", "E6"])    # optional, delegates to Instrument.set_range
    g.can_play_notes(["E4","G4"])  # capability checks as provided by Instrument / Guitar

### `mingus.containers.instrument.Guitar.can_play_notes` · *method*

## Summary:
Checks whether a provided collection of notes can be played on this six-string guitar; returns False immediately if the collection contains more than six items, otherwise delegates to the base Instrument.can_play_notes for per-note range validation. Does not modify the Guitar instance.

## Description:
Known callers and context:
- Instrument.notes_in_range(notes) — when invoked on a Guitar instance this method will be called (Instrument.notes_in_range delegates to self.can_play_notes).
- Higher-level arrangement, voice-assignment, or playback validation code that must verify whether a set/chord of notes is playable by the instrument prior to assignment/playback.
Lifecycle stage:
- This method is used at the validation stage: before assigning notes to the instrument, rendering fingerings, or rejecting chords that exceed the instrument's polyphony.

Why this logic is a separate method:
- The Guitar class overrides the generic Instrument behavior to enforce a guitar-specific physical constraint: a standard guitar has six strings and therefore cannot play more than six simultaneous notes. Implementing the check in this override keeps the Instrument implementation general while allowing instrument-specific limits to be enforced in subclasses.

## Args:
    notes (collection):
        - Expected: a sized collection (e.g., a Python list) whose elements are Note-like objects or strings accepted by mingus.containers.note.Note.
        - Important: this method requires that len(notes) is meaningful and returns the number of notes. It does NOT accept a single Note or a bare string as a proper call unless wrapped in a sized collection (e.g., [note] or ["C#4"]).
        - Allowed values:
            * A Python list of Note instances and/or note strings (recommended).
            * Any object for which len(obj) returns the number of notes (and whose elements, when later validated, are note-like or strings).
        - Not recommended / will behave unexpectedly:
            * Passing a plain string (e.g., "C#4") — len() will measure characters, not notes.
            * Passing an object that is a single-note container without __len__ implemented — len(notes) will raise TypeError.

## Returns:
    bool:
        - False if len(notes) > 6 (checked immediately, without validating individual elements).
        - Otherwise returns the boolean result of Instrument.can_play_notes(self, notes):
            * True if every normalized element is within this instrument's configured range.
            * False if any element is out-of-range.
        - Edge cases:
            * An empty list returns True (delegation will treat an empty list as all notes in-range).
            * If len(notes) cannot be computed, the call raises TypeError (no boolean return).

## Raises:
    TypeError:
        - If notes does not support len() (e.g., an iterator or an object without __len__), Python's built-in len() will raise TypeError before any validation occurs.
    UnexpectedObjectError:
        - May be raised by the delegated Instrument.can_play_notes (and its note_in_range) if an element is neither a string nor a Note-like object exposing a "name" attribute.
    Note-parsing / Note-construction exceptions:
        - If a string element cannot be parsed by mingus.containers.note.Note during delegation, the Note constructor will raise its parsing exception; that exception is propagated.

## State Changes:
    Attributes READ:
        - self.range (indirectly, via Instrument.can_play_notes -> note_in_range comparisons)
        - self.note_in_range (method is invoked during delegation)
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - self.range must be a valid, indexable two-element sequence of Note-like endpoints (this is an invariant of Instrument; callers should ensure set_range was called if needed).
        - The notes argument must be a sized collection (supports len()) whose length represents the number of notes to validate.
        - If passing note strings or objects requiring parsing/validation, they must be acceptable to the Note constructor or note_in_range; otherwise parsing errors or UnexpectedObjectError may occur.

    Postconditions:
        - The Guitar instance is unchanged (no attributes are mutated).
        - A boolean is returned indicating playability with the short-circuit constraint: return False if the collection contains more than six entries; otherwise the result reflects per-note range checks performed by Instrument.can_play_notes.

## Side Effects:
    - No I/O, network, or filesystem interaction.
    - May allocate temporary Note objects during delegated validation (when string representations are converted).
    - No mutation of objects outside self is performed by this method itself; any exceptions from delegated code propagate outward.

## `mingus.containers.instrument.MidiInstrument` · *class*

## Summary:
Represents a MIDI-capable instrument descriptor — a lightweight subclass of Instrument that pre-populates a General-MIDI-style playable range and a canonical list of instrument names. It primarily stores metadata used by MIDI playback or mapping code (instrument number, human name, and the list of available program names) and inherits range/validation behavior from Instrument.

## Description:
MidiInstrument exists to provide a ready-to-use Instrument configured with sensible MIDI defaults:
- It sets a default inclusive pitch range spanning from C0 up through B8 and exposes a long list of instrument names typically used for mapping MIDI program numbers to human-readable names.
- Typical call sites: MIDI playback engines, program-selection UIs, arrangement configuration code, or any factory that needs a basic Instrument pre-configured for General MIDI usage.
- Motivation / Responsibility: keep MIDI-specific metadata and common defaults centralized (default range, instrument number, and canonical names). It does not implement playback or MIDI I/O; those responsibilities belong to other modules. It also does not enforce mapping rules (e.g., validating instrument_nr against names) — such enforcement is left to callers.

## State:
- range (tuple[Note, Note])
    - Default value (class attribute): (Note("C", 0), Note("B", 8))
    - Type: an indexable sequence of two Note-like objects (lower bound at index 0, upper bound at index 1).
    - Semantic: inclusive lower and upper playable bounds.
    - Notes: set at class definition time; callers may override the instance attribute or use Instrument.set_range (inherited) to change it. Because the class-level value is a tuple, in-place mutation via Instrument.set_range (which expects a mutable sequence when converting string endpoints) will raise if attempted on that tuple.

- instrument_nr (int)
    - Default value (class attribute): 1
    - Semantic: intended to represent the MIDI program number for the instrument (conventionally 1-based, matching common General MIDI lists).
    - Constraints: conventionally 1 <= instrument_nr <= len(names), but this class does not validate that invariant; callers should enforce it if required.

- name (str)
    - Default value (class attribute): "" (empty string)
    - Instance initialization: __init__(self, name="") assigns the provided name (string) to the instance. This acts as a human-readable identifier that can differ from the entry in names.

- names (list[str])
    - Default: a long list of instrument names (General MIDI-style) defined at class level.
    - Semantic: the nth element in this list conventionally corresponds to MIDI program number n+1 (because instrument_nr default is 1 and lists are 0-indexed).
    - Notes: The list is a class-level constant and is not modified by the class. The class does not provide lookup helpers, but callers commonly map instrument_nr to names by indexing names[instrument_nr - 1].

Class invariants (conventions, not enforced by the class):
- range should remain an indexable two-element sequence of Note-like objects when inherited methods that use it are invoked.
- instrument_nr conventionally maps to an index in names; the class does not automatically enforce or normalize instrument_nr.

## Lifecycle:
- Creation
    - Construction: instantiate with optional human name:
        - MidiInstrument()  # creates an instance with empty name and default instrument_nr and range
        - MidiInstrument("Lead synth")  # sets instance.name to "Lead synth"
    - There are no alternative factory methods on the class itself.

- Usage
    - Inspect metadata:
        - read instance.name, instance.instrument_nr, and instance.names to display or choose program numbers/names.
    - Map program name ↔ number (convention):
        - To get the human name for the current instrument_nr: instance.names[instance.instrument_nr - 1] (caller must ensure instrument_nr is within bounds).
        - To set instrument_nr by a name: find the index of the desired name in instance.names and set instrument_nr = index + 1.
    - Range and validation:
        - Use inherited Instrument methods to change or validate pitch range:
            - instance.set_range(...) to change playable bounds (follow Instrument rules regarding mutable sequences and string conversion to Note).
            - instance.note_in_range(...), instance.can_play_notes(...) for range checks.
    - There is no special required sequencing beyond ensuring that range is a valid two-element indexable sequence before invoking inherited comparison methods.

- Destruction / cleanup
    - No cleanup is required. The class does not implement context-manager protocol or close() semantics.

## Method Map:
graph TD
    A[MidiInstrument.__init__(name)] --> B[set attributes: name]
    A --> C[inherits Instrument.range & methods]
    C --> D[Instrument.set_range(range)]
    D --> E[Instrument.note_in_range(note)]
    E --> F[Instrument.can_play_notes(notes)]
    C --> G[Instrument.__repr__]
    B --> H[read/write instrument_nr & names]

(Interpretation: __init__ only assigns the instance name. All range handling and note validation are provided by Instrument methods. Typical usage flows from instantiation to optional configuration (instrument_nr/name), optional set_range, then note validation or representation.)

## Raises:
- __init__(self, name=""):
    - Does not explicitly raise any exceptions.
    - Possible import-time exceptions: the module-level evaluation of Note("C", 0) and Note("B", 8) occurs when the class is defined. If the Note constructor raises for those arguments, the import of this module (and thus class definition) will fail with whatever exception Note raises. This is not raised by __init__ itself but may occur earlier.
- Inherited methods (Instrument.*):
    - Any code that calls inherited methods (set_range, note_in_range, can_play_notes, __repr__) may raise UnexpectedObjectError, IndexError, TypeError, or exceptions propagated from Note(...) as documented in the Instrument component. Consult Instrument documentation for exact triggers and behaviors.

## Example:
- Create a MIDI instrument and assign a program number by name (illustrative, plain-text usage):
    inst = MidiInstrument("My Piano")
    # Map a name to a program number (caller must check bounds)
    desired_name = "Acoustic Grand Piano"
    if desired_name in inst.names:
        inst.instrument_nr = inst.names.index(desired_name) + 1
        inst.name = desired_name
    # Use inherited range/validation methods
    inst.note_in_range("C4")          # uses Instrument.note_in_range (accepts string or Note)
    inst.can_play_notes(["C3","G4"])  # True if all notes are within inst.range

- Change the playable range (remember Instrument.set_range mutates provided mutable sequences when converting strings):
    inst.set_range(["E2", "E6"])  # preferred: pass a mutable list so conversion to Note objects can occur in-place

Notes for implementers reimplementing this class:
- The class is a very small subclass of Instrument; reimplementation requires:
    - Subclassing Instrument
    - Setting the class attributes shown: range (constructed with two Note(...) calls), instrument_nr = 1, name = "", and the names list containing the MIDI instrument strings.
    - Implementing an __init__(self, name="") that assigns self.name = name and otherwise defers to the inherited behavior (no additional initialization).
- Do not add side-effects: the original class does not validate instrument_nr nor convert it to zero-based indexing. Any such behavior should be implemented by caller code or a separate helper if desired.

### `mingus.containers.instrument.MidiInstrument.__init__` · *method*

## Summary:
Initialize a MidiInstrument instance by storing the provided display name on the instance.

## Description:
This constructor is invoked during object instantiation to record an instance-specific readable name. No complex initialization is performed — it simply assigns the provided value to the instance attribute so callers and other code can read or display the instrument's name.

Known callers:
    - No direct call sites for MidiInstrument(...) were discovered in the repository during analysis. In normal usage this method is called whenever user code or factory code constructs a MidiInstrument (e.g., MidiInstrument("Acoustic Grand Piano")) as part of instrument setup or when building a collection of MIDI instruments.
Lifecycle stage:
    - Executed at object construction time (immediately after a new instance is created).
Why this is a separate method:
    - Keeps object construction explicit and minimal, allowing subclasses to override or extend initialization behavior while preserving a consistent place to set the instance name. Separating initialization also makes tests and subclassing simpler.

## Args:
    name (str, optional): A human-readable name for the instrument. Defaults to the empty string ("").
        - Expected type: str for typical usage.
        - The constructor does not enforce type-checking: any object passed is assigned to self.name as-is.

## Returns:
    None

## Raises:
    None — this method performs a simple assignment and does not raise any exceptions.

## State Changes:
    Attributes READ:
        - None (the implementation performs no reads from self or class attributes).
    Attributes WRITTEN:
        - self.name : set to the provided name argument (or to "" if the default is used).

## Constraints:
    Preconditions:
        - self should be an instance of MidiInstrument (or a subclass). No other preconditions are enforced.
        - It is recommended to pass a string for name to match typical consumers that expect readable names.
    Postconditions:
        - After the call, self.name equals the exact value provided as the name argument (including non-string values if supplied).
        - No other attributes or global state are modified.

## Side Effects:
    - Mutates only the instance attribute self.name.
    - No I/O, no network or file system operations, and no external service calls.
    - No mutation of objects outside self (the passed-in name object is stored by reference, not copied).

## `mingus.containers.instrument.MidiPercussionInstrument` · *class*

## Summary:
Represents the General MIDI percussion (drum) instrument as a lightweight Instrument subclass. Exposes a mapping from MIDI percussion key numbers (35–81) to human-readable percussion names and provides convenience accessor methods that return a Note instance for each named percussion sound.

## Description:
This class models the General MIDI percussion set as an Instrument. It is intended to be instantiated when a caller needs a named collection of standard percussion sounds and programmatic access to each percussion voice as a Note-like object.

Typical scenarios to instantiate:
- Building a score, arrangement, or instrument roster that must include a percussion instrument described by General MIDI percussion key numbers.
- A playback engine or sequencer that maps percussion names to Note objects for downstream processing (e.g., scheduling note events or converting percussion keys to target pitch representations).
- Any client code that uses Instrument utilities (set_range, note_in_range, can_play_notes) but wants a ready-made percussion mapping and convenience factory methods for common percussion voices.

Motivation and responsibility boundary:
- MidiPercussionInstrument is a thin container: it provides identity (name), a canonical mapping of MIDI percussion numbers to names, and convenience methods that create Note objects for each percussion key.
- It does not implement playback, MIDI I/O, or any pitch-to-sample mapping beyond returning Note(midi_number - 12). All sound-generation or platform-specific translation is the responsibility of other components.

## State:
- name (str)
    - Type: str
    - Default: "Midi Percussion"
    - Invariant: present and human-readable; used by __repr__ and external displays.

- mapping (dict[int, str])
    - Type: dict mapping integer MIDI keys to percussion names
    - Valid keys: integers in the inclusive range 35 through 81 (the entries present in this implementation)
    - Values: non-empty human-readable strings describing the percussion voice
    - Invariant: mapping keys correspond to the convenience methods on the class (each method implemented below targets one mapping key).
    - Full mapping (MIDI number: name):
        - 35: Acoustic Bass Drum
        - 36: Bass Drum 1
        - 37: Side Stick
        - 38: Acoustic Snare
        - 39: Hand Clap
        - 40: Electric Snare
        - 41: Low Floor Tom
        - 42: Closed Hi Hat
        - 43: High Floor Tom
        - 44: Pedal Hi-Hat
        - 45: Low Tom
        - 46: Open Hi-Hat
        - 47: Low-Mid Tom
        - 48: Hi Mid Tom
        - 49: Crash Cymbal 1
        - 50: High Tom
        - 51: Ride Cymbal 1
        - 52: Chinese Cymbal
        - 53: Ride Bell
        - 54: Tambourine
        - 55: Splash Cymbal
        - 56: Cowbell
        - 57: Crash Cymbal 2
        - 58: Vibraslap
        - 59: Ride Cymbal 2
        - 60: Hi Bongo
        - 61: Low Bongo
        - 62: Mute Hi Conga
        - 63: Open Hi Conga
        - 64: Low Conga
        - 65: High Timbale
        - 66: Low Timbale
        - 67: High Agogo
        - 68: Low Agogo
        - 69: Cabasa
        - 70: Maracas
        - 71: Short Whistle
        - 72: Long Whistle
        - 73: Short Guiro
        - 74: Long Guiro
        - 75: Claves
        - 76: Hi Wood Block
        - 77: Low Wood Block
        - 78: Mute Cuica
        - 79: Open Cuica
        - 80: Mute Triangle
        - 81: Open Triangle

Inherited/related state (from Instrument):
- range: inclusive low/high playable Note bounds (Instrument class handles set_range, note_in_range, can_play_notes).
- clef, tuning: informational fields defined by Instrument.

Behavior of method return values:
- Each convenience method returns an instance of Note constructed with the integer argument (midi_number - 12). For example, the method corresponding to MIDI key 42 constructs Note(30). The exact semantics of Note(...) (accepted argument types, string vs integer constructors, comparison behavior) are delegated to the Note implementation—MidiPercussionInstrument simply passes an integer.

Class invariants:
- name is a non-empty string.
- mapping contains the percussion keys and names listed above.
- Each convenience method must return a Note instance (or propagate exceptions raised by Note constructor).
- Uses Instrument facilities unchanged; callers should be aware that Instrument expects range to be set to Note-like objects if range-related checks are used.

## Lifecycle:
Creation:
- Instantiate with no constructor arguments:
    - Create an instance; __init__ calls the Instrument base constructor, sets name to "Midi Percussion" and populates mapping with the canonical MIDI percussion table (entries above).
    - No factory methods; direct instantiation is the intended usage.

Usage:
- Typical usage flow:
    1. Instantiate the object:
        inst = MidiPercussionInstrument()
    2. Optionally configure instrument range (inherited Instrument API) if you plan to use note_in_range/can_play_notes:
        inst.set_range([lower, upper])  # lower/upper are Note-like or string names (see Instrument docs)
    3. Obtain Note instances for specific percussion voices via convenience methods or inspect mapping:
        - Use named method to get a Note representing that percussion sound (e.g., inst.closed_hi_hat()).
        - Alternatively, iterate inst.mapping.items() to enumerate available keys and names.
    4. Use returned Note objects with downstream systems that accept Note-like objects (e.g., scheduling engines, range checks).
- Method sequencing:
    - There is no required order for calling convenience methods.
    - If using Instrument range checks, ensure set_range has established a valid range before invoking note_in_range/can_play_notes.

Destruction / cleanup:
- No special cleanup required. No context-manager protocol or close() method is defined.

## Method Map:
graph TD
    A[Create: __init__] --> B[name set to "Midi Percussion"]
    A --> C[mapping populated with MIDI->name entries]
    C --> D[acoustic_bass_drum() .. open_triangle() methods]
    D --> E[Note(midi_number - 12) constructed and returned]
    F[Instrument methods] --> G[set_range / note_in_range / can_play_notes] 
    E --> G[returned Note used with Instrument checks]

(The class initialization populates mapping; each named accessor method constructs and returns a Note using the corresponding MIDI key minus 12. Instrument methods operate independently but can accept the Notes returned by the percussion methods.)

## Core methods and their behavior (summary sufficient to reimplement):
- __init__(self)
    - Calls the parent Instrument.__init__.
    - Sets self.name = "Midi Percussion".
    - Initializes self.mapping to the dictionary of MIDI percussion key numbers to names (see full mapping above).
    - Raises:
        - Any exceptions propagated from Instrument.__init__ (none expected).
        - No explicit exceptions otherwise.

- For each percussion voice listed in mapping there is a zero-argument method with a snake_case name corresponding to the readable name (lowercased, spaces/hyphens replaced by underscores, punctuation removed where applicable). The method:
    - Constructs and returns Note(midi_number - 12) where midi_number is the integer key from mapping.
    - Example mapping -> method pairs (not exhaustive here, see mapping above):
        - acoustic_bass_drum() -> Note(35 - 12)
        - bass_drum_1() -> Note(36 - 12)
        - side_stick() -> Note(37 - 12)
        - ...
        - open_triangle() -> Note(81 - 12)
    - Exceptions:
        - Any exception raised by the Note constructor (e.g., invalid argument type or value) will be propagated to the caller.

Implementation notes for reimplementation:
- The convenience methods are trivial wrappers; implementing them as one-line methods that return Note(midi_key - 12) is sufficient.
- The mapping keys must match the midi_key used by the corresponding method.
- Use six.string_types only if the implementation later needs to accept string inputs; this class's methods accept no arguments and therefore do not require string detection.

## Raises:
- __init__:
    - Propagates exceptions from the Instrument base constructor, if any.
    - Does not explicitly raise UnexpectedObjectError itself.

- Each convenience method:
    - Propagates any exceptions raised by Note(...) (construction or validation errors).
    - No other exceptions are intentionally raised by these methods.

## Example:
- Instantiate the percussion instrument and get a Note for a closed hi-hat:
    - Create an instance: inst = MidiPercussionInstrument()
    - Get a Note representing closed hi-hat: hat_note = inst.closed_hi_hat()
      (Internally this constructs Note(42 - 12) and returns it.)
- Use Instrument APIs with returned Note:
    - Optionally set a playable range using Instrument.set_range and then check if the percussion Note is within range using Instrument.note_in_range(hat_note) or by passing the note to can_play_notes.

### `mingus.containers.instrument.MidiPercussionInstrument.__init__` · *method*

## Summary:
Initializes instance state for a MIDI percussion instrument by calling the parent constructor, setting a human-readable name, and assigning the complete MIDI percussion key-to-sound mapping to the instance.

## Description:
This initializer runs when a MidiPercussionInstrument object is instantiated (for example: instrument = MidiPercussionInstrument()). Typical callers are any factory, loader, or user code that constructs instrument objects as part of instrument collections, arrangement building, or playback setup. The method is separated as an initializer to centralize instance setup: it ensures the parent initialization runs and that every instance receives the same fixed mapping table and descriptive name. Implementers should preserve the call to the parent initializer (super(MidiPercussionInstrument, self).__init__()) so any initialization performed by base classes is retained.

## Args:
    None

## Returns:
    None

## Raises:
    None raised directly by this method.
    - Note: the parent class __init__ called via super(...) may raise errors according to the parent's contract; those are not introduced here.

## Mapping contents (exact entries to assign to self.mapping):
Assign a dictionary mapping integer MIDI percussion note numbers to their human-readable names exactly as below. Keys are integers; values are strings.

35: Acoustic Bass Drum
36: Bass Drum 1
37: Side Stick
38: Acoustic Snare
39: Hand Clap
40: Electric Snare
41: Low Floor Tom
42: Closed Hi Hat
43: High Floor Tom
44: Pedal Hi-Hat
45: Low Tom
46: Open Hi-Hat
47: Low-Mid Tom
48: Hi Mid Tom
49: Crash Cymbal 1
50: High Tom
51: Ride Cymbal 1
52: Chinese Cymbal
53: Ride Bell
54: Tambourine
55: Splash Cymbal
56: Cowbell
57: Crash Cymbal 2
58: Vibraslap
59: Ride Cymbal 2
60: Hi Bongo
61: Low Bongo
62: Mute Hi Conga
63: Open Hi Conga
64: Low Conga
65: High Timbale
66: Low Timbale
67: High Agogo
68: Low Agogo
69: Cabasa
70: Maracas
71: Short Whistle
72: Long Whistle
73: Short Guiro
74: Long Guiro
75: Claves
76: Hi Wood Block
77: Low Wood Block
78: Mute Cuica
79: Open Cuica
80: Mute Triangle
81: Open Triangle

## State Changes:
Attributes READ:
    - None explicitly referenced in this method body. (The super call may read or modify parent attributes according to the parent's implementation.)

Attributes WRITTEN:
    - self.name (str): set to "Midi Percussion".
    - self.mapping (dict[int, str]): set to the full mapping dictionary described above.

## Constraints:
Preconditions:
    - No caller-provided arguments exist; there are no parameter preconditions.
    - The call to super(MidiPercussionInstrument, self).__init__() assumes the class has a well-formed parent that accepts no required constructor parameters or that parent defaults are satisfied.

Postconditions:
    - After successful completion:
        * self.name exists and equals the string "Midi Percussion".
        * self.mapping exists and is a dictionary containing the exact integer→string pairs listed in the Mapping contents section (keys 35 through 81).
        * The method returns None.

## Side Effects:
    - Calls the parent constructor via super(MidiPercussionInstrument, self).__init__(). Any side effects from that call (mutations, registrations, resource allocation) will occur.
    - No file, network, or external I/O is performed by this method itself.
    - No global state is modified directly by this method beyond setting attributes on the instance.

### `mingus.containers.instrument.MidiPercussionInstrument.acoustic_bass_drum` · *method*

## Summary:
Returns a new Note instance representing the acoustic bass drum percussion sound by constructing a Note with the integer value 35 - 12 (23). Does not modify the instrument object.

## Description:
This method is a convenience/factory accessor on the MidiPercussionInstrument that produces a Note corresponding to the "Acoustic Bass Drum" entry in the instrument's internal mapping (mapping key 35). It encapsulates the numeric mapping offset (35 - 12) so callers need not compute the MIDI/Note value themselves.

Known callers:
- No internal callers were found in the provided repository snapshot. This method is intended for direct use by client code (callers outside the class) that needs a Note instance representing the acoustic bass drum.

Why this is a separate method:
- Provides a named, discoverable accessor for the specific percussion instrument (improves readability and API discoverability).
- Prevents duplication of the numeric constant (35 - 12) throughout client code and centralizes the mapping logic in the instrument class.

## Args:
    self (MidiPercussionInstrument): Instance on which the method is invoked.

## Returns:
    mingus.containers.note.Note:
        A newly constructed Note instance created by calling Note(35 - 12), i.e. Note(23).
        - Normal case: returns a Note object initialized with the integer 23.
        - Edge cases: if the Note constructor performs validation, any invalid-input errors will be raised by the Note constructor (see Raises).

## Raises:
    Any exception raised by the Note constructor when called with the integer 23.
    - The method itself contains no explicit raise statements; exceptions are propagated from the Note(...) call.
    - No repository-internal exceptions (e.g., UnexpectedObjectError) are raised directly by this method.

## State Changes:
Attributes READ:
    - None (the method does not read any attributes from self)

Attributes WRITTEN:
    - None (the method does not modify self or any of its attributes)

## Constraints:
Preconditions:
    - self must be a valid MidiPercussionInstrument instance (implicit by method binding).
    - No argument-specific preconditions.

Postconditions:
    - Returns a Note instance constructed with the integer value 23.
    - The state of self (the MidiPercussionInstrument) is unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutations to objects outside self, except for the creation and return of the Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.bass_drum_1` · *method*

## Summary:
Returns a new Note object representing the instrument pitch produced by computing 36 - 12 (i.e., 24). This call does not modify object state.

## Description:
This is a convenience accessor that constructs and returns a fresh Note instance initialized with the integer value 24 (the expression 36 - 12 is evaluated by the method). It is intended for callers that need a Note object corresponding to this specific percussion instrument value without manually instantiating Note with the numeric value.

Known callers and context:
- No callers are present in the provided source fragment. Typically this method is invoked by external code that needs a Note representing this percussion instrument (for example, when building MIDI percussion tracks or mapping instrument accessors to Note objects).
- Lifecycle: called at use-time when a client requires the Note value; it does not participate in object initialization or persistent state changes.

Why this is a separate method:
- Provides a named, self-documenting accessor for a specific percussion pitch so callers do not need to remember or repeat the literal numeric value.
- Encapsulates the numeric computation in one place for readability and potential future modification.

## Args:
- None

## Returns:
- Note: A newly constructed mingus.containers.note.Note instance created by calling Note(24).
  - Possible values: always a Note wrapping the integer value 24 (no other values are returned).
  - Edge-case return values: none — the method always returns a Note instance.

## Raises:
- None raised by this method directly.
  - If the Note constructor itself were to raise (for example, on invalid input), that exception would propagate; this method does not catch or transform exceptions.

## State Changes:
- Attributes READ: none (does not read any self.<attr>).
- Attributes WRITTEN: none (does not write any self.<attr>).

## Constraints:
- Preconditions: self may be any valid instance; the method does not depend on internal state. No arguments required.
- Postconditions: after the call, a new Note object with underlying numeric value 24 has been returned; self remains unchanged.

## Side Effects:
- None: no I/O, no external service calls, and no mutation of objects outside the returned Note instance. The only effect is allocation of a new Note object that the caller receives.

### `mingus.containers.instrument.MidiPercussionInstrument.side_stick` · *method*

## Summary:
Returns a Note instance created from the numeric literal (37 - 12), producing a Note constructed with the integer 25. This method does not modify the instrument's state; it provides a named accessor for the "side stick" percussion mapping.

## Description:
Known callers:
- No callers were discovered in the inspected codebase. This method is intended to be called by code that needs a Note representing the instrument's "side stick" percussion sound (for example, higher-level code mapping percussion instrument names to Note objects or when building percussion patterns).

Context / lifecycle:
- Used when a consumer needs a canonical Note instance for the side stick percussion; it serves as a small, self-contained accessor that consistently returns the same Note construction each time it is invoked.

Why this is a separate method:
- Encapsulates the mapping between the semantic percussion instrument name ("side stick") and the numeric value used to construct a Note. Placing this logic in a method provides a named, discoverable API for clients and centralizes the numeric literal in one place for maintainability and clarity.

## Args:
- None

## Returns:
- mingus.containers.note.Note
    - A Note object constructed by calling Note(37 - 12). Evaluated value passed to the constructor is the integer 25.
    - The exact semantic interpretation of the integer (e.g., MIDI percussion key number, MIDI note number, semitone offset, or other pitch representation) is determined by the Note class implementation; this method only passes the integer 25 through to Note's constructor.

## Raises:
- This method itself does not raise any explicit exceptions.
- Exceptions raised by the Note constructor (for example, type or value validation errors) will propagate to the caller. The exact exception types and conditions are defined by the Note implementation and are not inspected here.

## State Changes:
Attributes READ:
- None (this method does not read any self.<attr> attributes)

Attributes WRITTEN:
- None (this method does not modify the object's state)

## Constraints:
Preconditions:
- No preconditions on self are required by this method; it does not access instance attributes.
- Assumes the Note class is available and callable with a single integer argument.

Postconditions:
- After calling, the caller receives a newly constructed Note instance created with the integer 25.
- No mutation to the instrument object has occurred.

## Side Effects:
- None. The method performs no I/O, does not interact with external services, and does not mutate objects other than returning a new Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.acoustic_snare` · *method*

## Summary:
Returns a Note object representing the Acoustic Snare percussion voice by constructing a Note with the integer value 38 - 12 (i.e., 26). This call does not modify the instrument's state.

## Description:
Known callers:
    - None found in repository documentation memory. Typical usage: callers will invoke this method when they need a Note object corresponding to the General MIDI "Acoustic Snare" percussion key from a MidiPercussionInstrument instance (for example, composition or playback code that asks the instrument for specific percussion notes).

Context / lifecycle:
    - This method is part of the MidiPercussionInstrument API and is intended to be called at any time a consumer needs the Note representing the acoustic snare sound. It is a pure accessor-like factory that produces a new Note instance each time it is called.

Why this is a separate method:
    - The mapping between named percussion instruments and their numeric MIDI key is encapsulated here to provide a clear, discoverable, and self-documenting API (one method per named percussion sound). Keeping this logic in a dedicated method avoids repeating the numeric literal (38 - 12) at call sites and groups the percussion-to-note mapping with the instrument class.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A new Note object constructed with the single positional argument integer value 26 (computed as 38 - 12). The returned Note represents the Acoustic Snare percussion voice as encoded by the numeric value passed to the Note constructor.

    Notes on return value:
        - The method always returns a newly constructed Note instance (no caching).
        - The numeric argument passed to Note is exactly 26; any semantics about what that integer means (MIDI note number, pitch class, etc.) depend on the Note class implementation.

## Raises:
    None raised by this method itself.
    - If the Note constructor raises an exception for the given argument (e.g., due to validation inside Note), that exception may propagate to the caller; such exceptions are not raised by this method's own logic.

## State Changes:
    Attributes READ:
        - None (this method does not read or depend on instance attributes).

    Attributes WRITTEN:
        - None (this method does not modify self or any of its attributes).

## Constraints:
    Preconditions:
        - self must be a valid instance of MidiPercussionInstrument (implicit from method binding).
        - The Note class must accept a single integer positional argument; otherwise the Note constructor may raise an exception (propagated to the caller).

    Postconditions:
        - A Note instance has been returned to the caller.
        - The MidiPercussionInstrument object remains unchanged.

## Side Effects:
    - None within this module. The method performs no I/O and does not mutate external objects.
    - Any observable side effect would only result from behavior inside the Note constructor (e.g., logging, validation side-effects), which is outside the scope of this method.

### `mingus.containers.instrument.MidiPercussionInstrument.hand_clap` · *method*

## Summary:
Returns a Note object representing the MIDI percussion "Hand Clap" key (computed as 39 minus one octave), without modifying the instrument instance.

## Description:
This method constructs and returns a new Note instance with the numeric pitch computed from the General MIDI percussion mapping entry for "Hand Clap" (39) shifted down by 12 semitones (one octave). It does not consult or modify any attributes of the MidiPercussionInstrument instance; it exists as a dedicated, named accessor to provide a semantically meaningful way to obtain the Note for the "Hand Clap" percussion sound.

Known callers and context:
- There are no internal callers in this class file; the method is part of the public MidiPercussionInstrument API.
- Typical usage is by client code that builds percussion/drum patterns, sequences, or that maps instrument-named accessors to Note objects for playback or MIDI export. It is intended to be invoked at runtime when a user or higher-level component needs the Note corresponding to the "Hand Clap" percussion sound.
- The logic is a separate method for API clarity and consistency: each percussion sound has a dedicated method that returns its corresponding Note, making calling code more readable and discoverable (e.g., instrument.hand_clap()) rather than using numeric literals.

## Args:
    self (MidiPercussionInstrument): The instrument instance. No other arguments are accepted.

## Returns:
    mingus.containers.note.Note: A newly constructed Note instance created by calling Note(39 - 12). The numeric pitch passed to the Note constructor evaluates to 27 (39 minus 12). There are no special-case return values; the method always returns a Note.

## Raises:
    This method does not raise exceptions itself. Any exception raised would come from the Note constructor if provided (for example, if Note enforces constraints on its input and rejects the numeric value), but the method does not perform validation or raise errors directly.

## State Changes:
    Attributes READ:
        - None (the method does not read any self.<attr> fields)
    Attributes WRITTEN:
        - None (the method does not modify the object state)

## Constraints:
    Preconditions:
        - The method must be called on an instance of MidiPercussionInstrument (Python enforces this when called as an instance method).
        - No additional object state or parameters are required.
    Postconditions:
        - A Note instance has been created and returned. The returned Note was constructed with the integer 27 (computed as 39 - 12).
        - The MidiPercussionInstrument instance is unchanged.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - No mutation of objects outside the method scope occurs (only a new Note instance is created and returned).

### `mingus.containers.instrument.MidiPercussionInstrument.electric_snare` · *method*

## Summary:
Returns a new Note instance representing the "Electric Snare" percussion voice (MIDI key 40 shifted by -12). Does not modify the instrument object's state.

## Description:
This convenience method constructs and returns a Note corresponding to the class's mapping entry for the electric snare (mapping key 40). The method body performs a single deterministic computation (40 - 12) and passes the result to the Note constructor.

Known callers:
    - No internal callers were found in the scanned class listing. It is a public, named accessor on MidiPercussionInstrument intended for client code to obtain a Note representing the electric snare percussion sound (MIDI percussion key 40).

Why this is a separate method:
    - Each percussion instrument in MidiPercussionInstrument exposes a named method that returns the corresponding Note. Having a separate method improves discoverability and provides a stable, explicit API for callers who want a Note pre-configured for a particular percussion instrument rather than constructing Note values manually.

## Args:
    None

## Returns:
    Note
        A newly constructed Note instance produced by calling Note(28) (40 - 12 = 28). The method always returns a Note object; there are no conditional return paths.

## Raises:
    None declared in this method.
    (Note: if the Note constructor itself raises for invalid input, those exceptions would propagate; this method contains no checks or exception handling.)

## State Changes:
    Attributes READ:
        None (the method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        None (the method makes no assignments to self; it does not mutate object state)

## Constraints:
    Preconditions:
        - The MidiPercussionInstrument instance must be instantiated (self must be a valid object), but the method does not depend on any particular state of the instance.
        - The Note constructor must accept an integer argument (28). This requirement stems from how the method calls Note(40 - 12).

    Postconditions:
        - After the call, self is unchanged.
        - The method returns a Note instance constructed with the integer value 28.

## Side Effects:
    - No I/O, no external service calls.
    - No mutations of objects outside of returning the new Note instance.

## Implementation notes for reimplementation:
    - Implement as a zero-argument instance method that computes 40 - 12, and returns the result passed to the Note constructor (i.e., return Note(28)).
    - Do not read or modify any attributes on self.
    - Keep it deterministic and side-effect free.

### `mingus.containers.instrument.MidiPercussionInstrument.low_floor_tom` · *method*

## Summary:
Returns a new Note object representing the Low Floor Tom percussion MIDI pitch (constructed from integer 41 - 12) without modifying the instrument instance.

## Description:
This is a convenience accessor on MidiPercussionInstrument that produces a Note corresponding to the percussion instrument labeled "Low Floor Tom" in the class mapping (mapping key 41). The method constructs and returns a new Note instance with the numeric argument 41 - 12 (evaluates to 29).

Known callers:
- No internal call sites are present in the MidiPercussionInstrument class definition. It is intended to be called by external user code or higher-level composition code that requests a Note representing the Low Floor Tom sound during composition, sequencing, or MIDI output preparation.

Why this logic is a separate method:
- Provides a clear, discoverable API for requesting standard percussion notes by instrument name.
- Keeps usage uniform with other percussion-accessor methods on MidiPercussionInstrument (each method returns a Note built from the mapping key minus 12).
- Avoids requiring users to remember or compute the numeric value (41 - 12) themselves.

## Args:
- None

## Returns:
- mingus.containers.note.Note
    - A newly constructed Note instance created by calling Note(41 - 12). The integer argument passed is 29.
    - The method always returns a Note object and does not return None or other types.

## Raises:
- None declared or raised in this method itself.
    - Any exceptions raised would come from the Note constructor; this method does not catch or transform them.

## State Changes:
- Attributes READ:
    - None (this method does not access any self.<attr> attributes)
- Attributes WRITTEN:
    - None (this method does not modify self)

## Constraints:
- Preconditions:
    - The caller must have a valid MidiPercussionInstrument instance (i.e., call as an instance method).
    - The Note constructor must accept an integer argument; if Note's constructor enforces constraints, callers should ensure those are satisfied (this method always passes integer 29).
- Postconditions:
    - After the call, self is unchanged.
    - The return value is a Note constructed with the integer 29.

## Side Effects:
- None within the repository-visible code: no I/O, no mutation of external objects, no network or filesystem interactions.
- The only effect is the allocation and return of a new Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.closed_hi_hat` · *method*

## Summary:
Return a newly constructed Note representing the "Closed Hi Hat" percussion voice (the method constructs a Note with the integer 42 - 12 => 30) without modifying the instrument instance.

## Description:
This method is a one-line factory/accessor on MidiPercussionInstrument that creates and returns a Note for the "Closed Hi Hat" percussion sound. In the class mapping the General MIDI percussion key 42 maps to "Closed Hi Hat"; this method computes 42 - 12 and passes the resulting integer to the Note constructor.

Known callers and invocation context:
- No internal callers were present in the provided snapshot of the repository; the method is designed for external callers that need a Note corresponding to the closed hi-hat percussion voice (for example, when constructing drum patterns or translating percussion mapping values to Note objects).
- It is part of a family of similar methods on MidiPercussionInstrument (one per percussion mapping entry) that provide clear, named accessors to Notes for each percussion instrument.

Why this is a separate method:
- Provides a discoverable, named API for the closed hi-hat Note rather than forcing callers to use raw numeric constants.
- Keeps the numeric mapping centralized and explicit, matching the class design of one accessor per percussion sound.

## Args:
- None.

## Returns:
- mingus.containers.note.Note
  - The method returns a newly instantiated Note created by calling Note(42 - 12).
  - The computed integer passed to Note is 30 (42 - 12).
  - There are no alternate return values produced by this method itself.

## Raises:
- The method does not explicitly raise exceptions. Any exception raised by the Note constructor (for example if the Note implementation validates its input) will propagate unchanged to the caller.

## State Changes:
- Attributes READ:
  - None (the method body does not read any self.<attr> attributes).
- Attributes WRITTEN:
  - None (the method does not modify any attributes on self).

## Constraints:
- Preconditions:
  - The caller must invoke the method on a valid MidiPercussionInstrument instance.
  - The Note class must accept the integer argument passed here; if the Note constructor rejects the argument, that error will surface to the caller.
- Postconditions:
  - A new Note object has been allocated and returned with internal pitch/value equal to 30.
  - The MidiPercussionInstrument instance remains unchanged.

## Side Effects:
- None observable beyond allocating and returning a new Note object. No I/O, network, file operations, or mutations of objects other than creating the returned Note.

## Example usage (descriptive):
- A caller constructs or obtains a MidiPercussionInstrument instance and calls the accessor to get a Note representing the closed hi-hat; that Note can then be used where Note objects are consumed (for example, adding to a track or pattern). The method itself performs only the conversion and object construction.

### `mingus.containers.instrument.MidiPercussionInstrument.high_floor_tom` · *method*

## Summary:
Returns a new Note object representing the "High Floor Tom" percussion pitch (constructed from the integer result of 43 - 12) without modifying the instrument instance.

## Description:
This method is a convenience accessor on the MidiPercussionInstrument class that constructs and returns a Note corresponding to the MIDI percussion key labelled "High Floor Tom". It is one of many similarly-named methods on MidiPercussionInstrument (e.g., low_floor_tom, acoustic_snare) that provide direct, readable ways for callers to obtain Note objects for standard GM percussion mappings.

Known callers and context:
- Intended for use by external code that needs a Note instance representing the High Floor Tom (for example, when building patterns, sequences, or converting percussion mappings to Note objects).
- Not used inside the class body itself; the class also contains a mapping dictionary where the integer 43 maps to the string "High Floor Tom", and this method returns Note(43 - 12) for convenience.
- Typical lifecycle: invoked at runtime by user code or higher-level utilities that translate percussion instrument names to Note instances prior to sequencing or playback.

Why this is its own method:
- Provides a self-documenting, per-instrument accessor consistent with other percussion methods in the class.
- Keeps the integer-to-Note conversion localized and uniform across percussion instrument accessors rather than inlined in multiple call sites.

## Args:
    None

## Returns:
    Note: A newly constructed Note instance created by calling Note(43 - 12). Concretely, this passes the integer 31 to the Note constructor (the result of 43 - 12). The method always returns a Note object when the Note constructor succeeds.

## Raises:
    Any exceptions raised by the Note constructor will propagate to the caller.
    The method does not explicitly raise any exceptions itself.

## State Changes:
    Attributes READ:
        None (this method does not read any attributes on self)
    Attributes WRITTEN:
        None (this method does not modify self)

## Constraints:
    Preconditions:
        - self must be a valid instance of MidiPercussionInstrument (the method uses no attributes or internal state, so no additional invariants are required).
    Postconditions:
        - A Note instance initialized with the integer 31 has been returned.
        - The MidiPercussionInstrument instance remains unmodified.

## Side Effects:
    - Allocates and returns a new Note object.
    - No I/O, no external service calls, and no mutation of objects outside the returned Note and the current object.

### `mingus.containers.instrument.MidiPercussionInstrument.pedal_hi_hat` · *method*

## Summary:
Returns a new Note object representing the "Pedal Hi-Hat" percussion voice by constructing a Note from the integer value 44 - 12 (i.e., 32). This call does not modify the instrument object.

## Description:
This is a convenience accessor on the percussion instrument class that produces a Note instance corresponding to the MIDI percussion mapping entry for "Pedal Hi-Hat". Within the MidiPercussionInstrument class each percussion voice is exposed as a similarly-named zero-argument method; this method follows that pattern.

Known callers and lifecycle:
- No internal callers are present within the MidiPercussionInstrument class definition inspected. The method is intended to be called by external code (client code, applications, or tests) that require a Note object for the pedal hi-hat percussion sound.
- Typical usage is at the point in a music-processing pipeline where a client needs a Note instance to represent the pedal hi-hat event (e.g., when creating or scheduling percussion events for playback or composition).

Rationale for separate method:
- Each percussion sound is given its own named accessor to make client code clearer and to centralize the numeric mapping (44 mapped to "Pedal Hi-Hat"). This avoids scattering magic numbers and provides a discoverable API for percussion notes.

## Args:
    None

## Returns:
    mingus.containers.note.Note: A freshly constructed Note initialized with the integer value 44 - 12 (which evaluates to 32). No other return values are produced by this method.

## Raises:
    This method does not raise exceptions itself. Any exception would originate from the Note constructor if the Note implementation enforces input validation; the method does not catch or transform such exceptions.

## State Changes:
    Attributes READ:
        None — the method does not read any attributes on self.
    Attributes WRITTEN:
        None — the method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - self must be a valid, initialized instance of MidiPercussionInstrument (or a compatible object exposing this method).
        - No arguments are required.

    Postconditions:
        - A new Note instance has been created and returned with the internal value equal to 32 (44 - 12).
        - The MidiPercussionInstrument instance remains unchanged.

## Side Effects:
    - No I/O, external service calls, or mutations to objects outside of creating and returning the new Note object.
    - The only runtime effect is the construction of the Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.low_tom` · *method*

## Summary:
Returns a new Note instance representing the "Low Tom" percussion sound by constructing a Note for MIDI key 45 shifted down one octave (45 - 12 = 33). This does not modify the instrument object.

## Description:
This is a convenience accessor on MidiPercussionInstrument that produces a Note corresponding to the General MIDI percussion "Low Tom" entry (key 45) adjusted by subtracting 12 semitones. It exists so callers can request a Note object for this specific percussion sound by name (low_tom) rather than by numeric MIDI key.

Known callers and context:
- No direct internal callers were found in the inspected module snapshot. Typical usage is external/consumer code that wants a Note object representing this percussion instrument (for example, when composing or playing percussion patterns using mingus). Callers will invoke this method during composition or when converting named percussion sounds into Note objects for playback or further transformation.

Rationale for a separate method:
- Encapsulates the numeric mapping and octave adjustment in a readable, discoverable API. It groups a single, well-defined mapping (Low Tom) behind a descriptive method name rather than requiring callers to remember the numeric key and octave offset.

## Args:
- None.

## Returns:
- mingus.containers.note.Note: A newly constructed Note instance created by calling Note(45 - 12). Concretely, the integer passed to the Note constructor is 33.
- Edge cases: The method itself does not return None or other types. If the Note constructor raises (for example, due to invalid argument types or invalid pitch range enforced by Note), those exceptions propagate to the caller.

## Raises:
- No exceptions are raised explicitly by this method.
- Any exception raised by the Note constructor (e.g., TypeError, ValueError) will propagate; this method does not catch or convert such exceptions.

## State Changes:
- Attributes READ:
    - None (the method does not read any self.<attr> fields).
- Attributes WRITTEN:
    - None (the method does not modify any self.<attr> fields).

## Constraints:
- Preconditions:
    - self must be an instance of MidiPercussionInstrument (or at least provide the bound method). There are no other preconditions on instance state.
    - The Note constructor must accept an integer pitch value; the method passes the integer 33 to Note.
- Postconditions:
    - After the call, the MidiPercussionInstrument instance is unchanged.
    - The caller receives a Note instance constructed with the integer 33 (representing MIDI key 45 shifted down 12 semitones).

## Side Effects:
- No I/O is performed.
- No mutation of objects outside self is performed.
- The only side-effect is allocation of a new Note object and any behavior inside the Note constructor (which may include validation) — those effects (if any) are the responsibility of the Note implementation.

### `mingus.containers.instrument.MidiPercussionInstrument.open_hi_hat` · *method*

## Summary:
Returns a Note object representing the MIDI percussion voice "Open Hi-Hat" and does not modify the instrument's state.

## Description:
This instance method is a small factory/convenience that constructs and returns a Note corresponding to the MIDI percussion number for an open hi-hat. It directly instantiates a Note with the integer value computed in the method body.

Known callers:
    - No internal callers were discovered in the surrounding module; the method is intended to be called by downstream code that needs a Note representing the open hi-hat (for example, code that converts percussion names to Note objects when composing or sequencing percussion parts).

Lifecycle / context:
    - Typically invoked at composition or sequencing time when a caller needs a Note representing the open hi-hat sound. It is part of the set of percussive factory methods on MidiPercussionInstrument that each return the Note for a specific percussion voice.

Why this is a separate method:
    - Provides a clear, discoverable API on MidiPercussionInstrument matching the human-readable percussion mapping (e.g., open_hi_hat -> "Open Hi-Hat").
    - Keeps callers from needing to remember or recompute the raw MIDI/percussion integer value; ensures parity with other instrument-specific factory methods.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A Note instance constructed with the integer 34 (computed as 46 - 12 in the source). This Note represents the "Open Hi-Hat" percussion voice as provided by this convenience method.

## Raises:
    None explicitly raised by this method.
    Note: the method does not catch exceptions; any exception propagated will come from the Note constructor invoked here.

## State Changes:
    Attributes READ:
        None — this method does not access any self.<attr> attributes.

    Attributes WRITTEN:
        None — this method does not modify the object state.

## Constraints:
    Preconditions:
        - No preconditions on self or arguments; method takes no parameters.
        - The Note class must be constructible with a single integer argument as used here.

    Postconditions:
        - A new Note object is returned with the numeric value 34.
        - The MidiPercussionInstrument instance remains unchanged.

## Side Effects:
    - None: there is no I/O, no mutation of external objects, and no network or file system access initiated by this method.

### `mingus.containers.instrument.MidiPercussionInstrument.low_mid_tom` · *method*

## Summary:
Returns a new Note instance representing the "low mid tom" percussion key (MIDI number 35) without modifying the instrument object.

## Description:
- Known callers and context:
    - No callers were found in the scanned codebase for this method. It is intended as a convenience accessor on a MidiPercussionInstrument to obtain the standard Note used for the low mid tom percussion sound (commonly mapped to MIDI percussion key 35).
    - Typical lifecycle: called by client code that needs a Note object corresponding to the low-mid tom sound when building or playing percussion patterns.
- Rationale for being a separate method:
    - Encapsulates the fixed mapping from instrument semantic name ("low mid tom") to the concrete Note value in one place. This avoids repeating the literal numeric mapping throughout client code and makes intent explicit.

## Args:
    None (only implicit self).

## Returns:
    mingus.containers.note.Note
    - A newly constructed Note instance created by calling Note(47 - 12), which evaluates to Note(35).
    - The method always constructs and returns a fresh Note object; it does not return None or other sentinel values.

## Raises:
    - The method itself contains no raise statements and performs no validation. It does not explicitly raise exceptions.
    - If the Note constructor raises (for example, due to an invalid argument type or value), that exception will propagate to the caller.

## State Changes:
- Attributes READ:
    - None (this method does not read any self.<attr> fields).
- Attributes WRITTEN:
    - None (this method does not modify any self.<attr> fields).

## Constraints:
- Preconditions:
    - self must be a valid instance (the method uses only self as a receiver and does not access internal state).
    - The Note constructor must accept a single integer argument; otherwise the Note constructor may raise.
- Postconditions:
    - After the call, self is unchanged.
    - The caller receives a Note instance equivalent to Note(35).

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside the newly created Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.hi_mid_tom` · *method*

## Summary:
Returns a Note object representing the "high mid tom" percussion MIDI pitch (computed as 48 - 12), without modifying the instrument object.

## Description:
This accessor-style method constructs and returns a new Note set to the numeric value produced by the expression 48 - 12 (i.e., 36). It is intended to be used when mapping named percussion instruments on a MidiPercussionInstrument to their corresponding MIDI note values represented as Note objects.

Known callers and context:
- No callers are defined inside this file. In typical usage, callers are other code that translates percussion-instrument names into playable Note objects (for example, when rendering or sequencing percussion patterns). This method would be invoked wherever code needs the Note for the "high mid tom" sound during MIDI/percussion handling or instrument setup.

Why this is a separate method:
- Encapsulates the mapping from the instrument name to a concrete Note, making the mapping explicit and easy to override or mock in subclasses.
- Keeps percussion-to-note mappings isolated from higher-level sequencing or playback logic for readability and maintainability.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A newly constructed Note instance created with the integer value 36 (computed as 48 - 12). This is the sole return value and is always produced when the Note constructor succeeds.

## Raises:
    None raised directly by this method.
    Any exception thrown by the Note constructor (for example, if Note validates its input and rejects it) will propagate out of this method unchanged.

## State Changes:
    Attributes READ:
        None
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - No preconditions on self are required by this method; it does not read or depend on any instance attributes.
    Postconditions:
        - After the call, self remains unmodified.
        - A Note instance representing MIDI pitch 36 is returned (assuming the Note constructor accepts the provided integer).

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside of the newly created Note instance returned to the caller.

### `mingus.containers.instrument.MidiPercussionInstrument.crash_cymbal_1` · *method*

## Summary:
Returns a newly-constructed Note initialized with the integer value 37 (computed as 49 - 12) and does not modify the instrument instance.

## Description:
This small accessor/factory constructs and returns a Note using the literal calculation 49 - 12, producing the integer 37, and returns that Note to the caller. The method contains no logic other than creating the Note instance and therefore does not inspect or mutate the instrument's state.

Known callers and lifecycle:
- No callers are referenced inside this method body. It is intended to be called by client code or higher-level utilities that need a Note corresponding to the semantic label implied by the method name.
- Typical use occurs when a caller needs an immutable Note object representing the instrument/percussion mapping associated with "Crash Cymbal 1" as provided by this API (the method encodes the numeric mapping as 37).

Why a separate method:
- Encapsulates the numeric literal behind a semantically-named accessor so callers do not hardcode the integer value and so the mapping is centralized in one place.

## Args:
- None

## Returns:
- mingus.containers.note.Note
    - A newly-created Note instance constructed with the integer 37 (result of 49 - 12).
    - The method always returns a Note instance when construction succeeds.

## Raises:
- No exceptions are raised directly by this method.
- Any exception raised by the Note constructor (for example, due to invalid constructor arguments or internal Note validation) will propagate to the caller because this method does not catch exceptions.

## State Changes:
- Attributes READ:
    - None (the method does not access self.<attr>)
- Attributes WRITTEN:
    - None (the method does not modify self or any external state)

## Constraints:
- Preconditions:
    - The method must be invoked on a bound instance (normal method binding applies).
    - The Note constructor must accept an integer value; the method passes 37.
- Postconditions:
    - On successful return, a Note instance constructed with integer 37 has been returned.
    - No attributes on self or external objects have been changed by the call.

## Side Effects:
- Allocates and returns a new Note object.
- No I/O, no network or filesystem access, and no mutations outside the newly-created Note instance.

## Example:
- After calling inst.crash_cymbal_1(), the returned value is a Note constructed with the integer 37 (i.e., the call is equivalent to Note(37) in effect).

### `mingus.containers.instrument.MidiPercussionInstrument.high_tom` · *method*

## Summary:
Returns a new Note instance representing the "High Tom" percussion sound by constructing a Note with the integer 50 - 12 (i.e., 38). This updates no state on the instrument object.

## Description:
- Known callers:
    - No internal callers are present in the retrieved module data. This method is provided as a public convenience accessor for external client code (users of the MidiPercussionInstrument) that needs a Note representing the "High Tom" percussion instrument.
    - Typical lifecycle / pipeline stage: called at runtime when translating a named percussion instrument into a Note object to be played, sequenced, or further transformed.

- Rationale for being a separate method:
    - Encapsulates the mapping from the instrument name "High Tom" to the numeric MIDI percussion key (50) with the library's one-octave transposition convention (subtracting 12). Having a named method improves readability and discoverability (e.g., instrument.high_tom()) compared to clients constructing the Note themselves with a magic number.

## Args:
- None

## Returns:
- mingus.containers.note.Note
    - A newly constructed Note instance created with the integer argument 38 (computed as 50 - 12).
    - The method always returns a Note object when the Note constructor succeeds; it does not return None or mutate existing Note instances.

## Raises:
- No exceptions are raised explicitly by this method.
- The method may propagate any exception raised by the Note constructor (for example, validation errors from Note if an invalid argument is passed into its initializer). The exact exception types and conditions depend on the Note implementation and are not introduced by this method itself.

## State Changes:
- Attributes READ:
    - None of self's attributes are read.
- Attributes WRITTEN:
    - None of self's attributes are modified.

## Constraints:
- Preconditions:
    - None required from the caller beyond the usual invariants of the MidiPercussionInstrument instance being a valid object.
    - Assumes the Note constructor accepts an integer argument and can construct a Note from the integer 38.
- Postconditions:
    - After the call, the object state is unchanged.
    - The caller receives a newly allocated Note instance whose constructor argument was the integer 38.

## Side Effects:
- No I/O or external service interactions.
- Allocates and returns a new Note object (memory allocation). No mutation of objects outside the method occurs.

### `mingus.containers.instrument.MidiPercussionInstrument.ride_cymbal_1` · *method*

## Summary:
Returns a new Note instance corresponding to the MIDI percussion instrument "Ride Cymbal 1" (constructed with the integer 51 - 12 = 39). The call does not modify the instrument object's state.

## Description:
- Known callers and context:
    - No direct callers were discovered in the provided repository snapshot. This method is one of many small accessor/factory methods on MidiPercussionInstrument that provide a Note object for a named percussion instrument.
    - Typical usage: called during mapping/translation of percussion instrument names or MIDI percussion numbers into Note objects for sequence creation, rendering, or playback pipelines where a Note object is required.

- Why this is a separate method:
    - The class exposes a set of named methods (one per percussion sound) to consistently and readably provide the corresponding Note objects. Keeping this logic in a dedicated method makes the mapping explicit, simplifies code that requests a particular percussion Note, and groups all percussion-to-Note conversions in a single, discoverable API surface rather than inlined literals scattered across the codebase.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A newly constructed Note instance created by calling Note(51 - 12) (i.e., Note(39)). Each invocation constructs and returns a Note object; the method always returns a Note constructed with the same integer argument.

## Raises:
    None explicitly raised by this method.
    Any exception raised by the Note constructor (for example, TypeError or ValueError if the Note implementation rejects the provided argument) will propagate out of this method unchanged.

## State Changes:
- Attributes READ:
    - None (the method does not access any self.<attr> attributes)
- Attributes WRITTEN:
    - None (the method does not modify self or any of its attributes)

## Constraints:
- Preconditions:
    - No preconditions on self enforced by this method. The only implicit requirement is that the Note constructor accepts an integer argument; otherwise, the constructor may raise.
- Postconditions:
    - self remains unchanged.
    - The method returns a Note instance constructed with the integer value 39.

## Side Effects:
    - None. This method performs no I/O and does not modify objects outside of constructing and returning the new Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.chinese_cymbal` · *method*

## Summary:
Returns a Note object representing the "Chinese Cymbal" percussion MIDI key transposed down one octave (MIDI number 40), without modifying the instrument instance.

## Description:
This method is a zero-argument convenience factory that constructs and returns a Note for the percussion instrument labeled "Chinese Cymbal" in the MidiPercussionInstrument mapping. The method body instantiates a Note with the integer result of the expression 52 - 12 (i.e., 40). There are no callers defined in this file; it is intended to be invoked by client code or playback/sequence-building logic that requires a Note object for the Chinese cymbal percussion sound.

This logic is its own method rather than inlined to provide a readable, named accessor for a specific percussion mapping (avoiding magic numbers) and to match the class's collection of similarly named percussive factory methods (one per mapped instrument).

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A Note instance constructed with the integer value 40 (computed as 52 - 12). This represents the MIDI key for "Chinese Cymbal" transposed down one octave. No other return values are possible.

## Raises:
    None
        The method does not perform validation and does not raise exceptions itself. Any exceptions raised originate from the Note constructor; those are not raised explicitly here.

## State Changes:
    Attributes READ:
        None — the method does not access any self.<attr> fields.
    Attributes WRITTEN:
        None — the method does not modify self or any external state.

## Constraints:
    Preconditions:
        - self must be an instance of MidiPercussionInstrument (or any object where calling this bound method is valid).
        - The Note constructor must accept a single integer argument; otherwise an error will be raised by that constructor.

    Postconditions:
        - After the call, the returned value is a Note instance initialized with the integer 40.
        - The state of the called object (self) is unchanged.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - No mutations occur on objects outside self (only a new Note instance is created and returned).

### `mingus.containers.instrument.MidiPercussionInstrument.ride_bell` · *method*

## Summary:
Returns a new Note object representing the percussion "ride bell" pitch (constructed with the integer 41).

## Description:
This method is a simple accessor that constructs and returns a Note instance corresponding to the instrument's ride bell sound. It performs no mutation of the instrument object and does not consult any instance state.

Known callers and context:
- Intended to be called by code that translates percussion instrument parts into concrete Note objects for sequencing, playback, MIDI export, or consumption by other music-processing components.
- Typically used during the stage where a percussion instrument's named components (e.g., ride bell, bass drum, snare) are mapped to specific Note instances or MIDI output values.

Why this is a separate method:
- Encapsulates the mapping from the instrument's semantic element ("ride bell") to the concrete Note constructor argument in a single place, making it easy to override in subclasses or to change the mapping without touching callers.
- Keeps higher-level code free from hard-coded numeric literals and clarifies intent where the ride bell pitch is needed.

## Args:
    None

## Returns:
    Note: A newly constructed Note object created by calling Note(53 - 12), i.e., Note(41).
    - The returned object is independent of the instrument instance (no caching).
    - If the Note constructor performs validation, any constructor-specific return behaviors or exceptions will propagate unchanged.

## Raises:
    No exceptions are raised by this method itself.
    - Exceptions thrown by the Note constructor (if any) will propagate to the caller (e.g., invalid argument type or value), since this method does not catch them.

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> fields)
    Attributes WRITTEN:
        - None (this method does not modify the instrument instance)

## Constraints:
    Preconditions:
        - None enforced by this method. It assumes the Note class is importable and callable with a single integer argument.
    Postconditions:
        - Returns a new Note instance constructed with the integer 41 (result of 53 - 12).
        - The instrument instance remains unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects other than creating and returning a new Note instance.

## Implementation notes for reimplementation:
    - Implement exactly as: construct a Note by evaluating 53 - 12 and passing the resulting integer to the Note constructor; return that Note.
    - Do not perform any additional logic, caching, or state mutation.

### `mingus.containers.instrument.MidiPercussionInstrument.tambourine` · *method*

## Summary:
Returns a new Note instance representing the tambourine percussion pitch (MIDI note number 42) and does not modify the instrument object.

## Description:
This method is a simple accessor that constructs and returns a Note for the tambourine by computing 54 - 12 and passing that integer to the Note constructor (resulting value: 42). It performs no side effects and does not reference or change any attributes on self.

Known callers and context:
- No direct callers are present in the provided source snapshot. Conceptually, this method is used wherever a mapping from named percussion instruments to their MIDI note values is needed (for example, when generating or interpreting MIDI percussion events).
- Typical lifecycle usage: invoked at the point a caller needs a Note object representing the tambourine pitch (e.g., during MIDI message construction or when building score representations).

Why this logic is a separate method:
- Encapsulates the mapping from the instrument name to the MIDI pitch in one place for readability and reuse.
- Allows subclasses or higher-level instrument abstractions to override or extend individual instrument mappings without duplicating numeric literals.

## Args:
None.

## Returns:
Note
- A new mingus.containers.note.Note instance constructed with the integer value 42 (computed as 54 - 12).
- The returned object is a freshly created Note; callers should not assume it is cached or reused.

## Raises:
- This method does not raise exceptions itself, but any exception thrown by the Note constructor will propagate to the caller (for example, if Note.__init__ validates input and raises TypeError/ValueError or a library-specific error).

## State Changes:
Attributes READ:
- None. The method does not read any self.<attr> fields.

Attributes WRITTEN:
- None. The method does not modify any self.<attr> fields.

## Constraints:
Preconditions:
- self must be a valid instance (an instance of the enclosing MidiPercussionInstrument class). There are no other preconditions on self or arguments.

Postconditions:
- self remains unchanged.
- The caller receives a Note initialized with the numeric MIDI pitch 42.

## Side Effects:
- No I/O, no external service calls.
- Only side effect is allocation of a new Note object in memory; no persistent state is modified.

### `mingus.containers.instrument.MidiPercussionInstrument.splash_cymbal` · *method*

## Summary:
Returns a new Note instance corresponding to the splash cymbal percussion mapping (constructed from the integer 55 - 12, i.e., 43). This method does not modify the instrument object's state.

## Description:
- Known callers and context:
    - No direct callers are present in the provided source. This method is intended as a convenience accessor on a MidiPercussionInstrument to obtain the Note value representing a splash cymbal; it is typically used wherever code needs the Note object for that percussion instrument (for example, when assembling percussion tracks, mapping percussion names to Note objects, or generating MIDI events).
- Why this is a separate method:
    - Encapsulates the mapping from the semantic percussion instrument (splash cymbal) to the concrete Note value in one place, providing a clear, named accessor. This improves readability and allows subclasses or mocks to override the mapping easily without inlining numeric constants throughout client code.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A newly-constructed Note object created with the integer value 55 - 12 (evaluates to 43). This is the only return value; there are no alternate return cases.

## Raises:
    Any exceptions raised by the Note constructor (propagated)
        The method does not raise its own exceptions. If the Note(...) call raises (for example, due to invalid constructor arguments or internal Note validation), that exception will propagate to the caller.

## State Changes:
- Attributes READ:
    - None (the method does not access any self.<attr> attributes)
- Attributes WRITTEN:
    - None (the method does not modify the object's attributes)

## Constraints:
- Preconditions:
    - The Note class (mingus.containers.note.Note) must accept a single integer in its constructor; otherwise the Note constructor may raise an exception which will propagate.
    - No particular state is required on self; the method is stateless with respect to the instance.
- Postconditions:
    - After the call, the caller receives a Note instance equivalent to calling Note(43).
    - The instrument object's state is unchanged.

## Side Effects:
    - None. The method performs no I/O, no external service calls, and does not mutate objects outside of creating and returning the new Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.cowbell` · *method*

## Summary:
Returns a new Note object representing the cowbell percussion sound by constructing a Note with the fixed MIDI pitch value (56 - 12 = 44). This does not modify the instrument instance.

## Description:
This method is a simple factory accessor that produces a Note corresponding to the cowbell percussion voice on the General MIDI percussion map. It is intended to be called when code needs a Note instance that plays the cowbell sound (for example, by user code or higher-level MIDI/track builders). No internal callers are present in the MidiPercussionInstrument class beyond the other similar per-instrument accessor methods; external code typically calls this method during composition or MIDI event creation.

The logic is separated into its own method to provide a named, convenient, and discoverable accessor for a specific percussion instrument (consistent pattern across all percussion accessors in MidiPercussionInstrument). Keeping this as its own method improves readability and allows callers to request named percussion notes rather than remembering numeric MIDI codes.

## Args:
    None

## Returns:
    Note: A newly constructed instance of mingus.containers.note.Note created by calling Note(56 - 12). Concretely, the integer passed to the Note constructor is 44 (56 - 12). The returned object represents the cowbell percussion note. If the Note constructor validates its argument and raises, that exception will propagate to the caller.

## Raises:
    Any exception raised by mingus.containers.note.Note when constructed with the integer 44 may be propagated. This method itself performs no validation or exception handling.

## State Changes:
    Attributes READ:
        None (this method does not read any attributes on self)

    Attributes WRITTEN:
        None (this method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - Called on a valid instance of MidiPercussionInstrument (self must be an instantiated object).
        - No arguments; the method assumes the Note constructor accepts an integer pitch value.

    Postconditions:
        - A Note instance representing MIDI pitch number 44 is returned.
        - The instrument object's state is unchanged.

## Side Effects:
    - Allocates and returns a new Note object.
    - No I/O, no external service calls, and no mutation of objects outside the returned Note instance.

## Implementation notes / Mapping:
    - The MidiPercussionInstrument.mapping dictionary associates the key 56 with "Cowbell". The accessor subtracts 12 from that MIDI key (56) before creating the Note (resulting pitch 44) — consistent with other percussion accessors in this class.
    - If callers require the original General MIDI percussion key (56), they should refer to the mapping dictionary on the instrument instance rather than this returned Note pitch.

### `mingus.containers.instrument.MidiPercussionInstrument.crash_cymbal_2` · *method*

## Summary:
Returns a Note instance representing the instrument's "Crash Cymbal 2" by constructing a Note with the integer value 45 (computed as 57 - 12). This does not modify the instrument object's state.

## Description:
This accessor method provides a named, reusable way to obtain the Note used for "Crash Cymbal 2". It simply constructs and returns a new Note object with the numeric value 45.

Known callers and context:
- No specific callers are identified in this file. In typical usage within a percussion instrument mapping, this method would be invoked when code needs the Note object that corresponds to the "Crash Cymbal 2" percussion voice (for example, when converting a percussion name to a Note or when building instrument mappings).
- It is a convenience/naming wrapper so callers can request a percussion instrument's Note by semantic name rather than by numeric literal.

Reason for being a separate method:
- Encapsulates the numeric constant (57 - 12) behind a descriptive method name, improving readability and maintainability.
- Keeps percussion-note mappings centralized and discoverable as named methods instead of scattering numeric literals throughout the code.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A newly constructed Note instance created by calling Note(57 - 12), i.e., Note(45).
        The exact interpretation of the integer argument (45) and the internal state of the returned Note depend on the Note class implementation.

## Raises:
    Any exception raised by the Note constructor may propagate out of this method.
    This method itself does not raise exceptions directly.

## State Changes:
    Attributes READ:
        - None (the method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        - None (the method does not modify self or other stored attributes)

## Constraints:
    Preconditions:
        - self should be an instance of the enclosing class (MidiPercussionInstrument). The method does not validate type and will ignore self.
        - The Note constructor must accept a single integer argument; otherwise, the Note constructor may raise an exception.
    Postconditions:
        - Returns a Note instance constructed with the integer 45.
        - The instrument object (self) remains unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside the newly created Note (i.e., only the returned Note is newly created; no other global or object state is modified).

### `mingus.containers.instrument.MidiPercussionInstrument.vibraslap` · *method*

## Summary:
Returns a new Note object representing the "Vibraslap" percussion sound by constructing a Note with the MIDI percussion key 58 shifted down one octave (58 - 12 = 46). This call does not modify the instrument object's state.

## Description:
This method is one of many convenience factory methods on MidiPercussionInstrument that produce Note instances for specific General MIDI percussion sounds. Each factory method maps a named percussion instrument to its MIDI key number, then constructs a Note with that numeric value shifted down by 12 semitones (one octave).

Known callers and context:
- No internal callers are present within this module for this method; it is intended to be used by external client code (for example, music generation or sequencing code) that needs a Note representing the Vibraslap percussion instrument.
- Lifecycle / pipeline: invoked whenever a caller needs a concrete Note instance corresponding to the Vibraslap percussion sound (e.g., when building a percussion track or translating a percussion name to a Note).

Why this logic is a separate method:
- Keeps a clear, discoverable API: callers can request a Note by semantic name (vibraslap) rather than remembering numeric MIDI keys.
- Encapsulates the mapping convention (MIDI key minus 12) in a single location and keeps percussive mappings symmetrical with other percussion factory methods in the class.
- Improves readability and maintainability by providing a per-instrument factory method instead of inlining numeric literals at call sites.

## Args:
    This method takes no arguments.

## Returns:
    mingus.containers.note.Note
        A newly constructed Note instance created by calling Note(58 - 12). Concretely, the integer argument passed to the Note constructor is 46.
    Edge cases:
        - If the Note constructor performs validation on its input (e.g., numeric range checks), that validation may cause the constructor to raise an exception; such behavior is determined by the Note implementation and is not performed in this method.

## Raises:
    This method does not raise any exceptions itself.
    - Any exception that may propagate is raised by the Note constructor (for example, if Note validates its argument); this method does not catch or translate those exceptions.

## State Changes:
    Attributes READ:
        - None: the method does not read any self.<attr> attributes.
    Attributes WRITTEN:
        - None: the method does not modify any self.<attr> attributes.

## Constraints:
    Preconditions:
        - Must be called on an instance of MidiPercussionInstrument (bound method). No other object state is required.
        - Assumes the Note constructor accepts a single integer argument; the method passes 46.
    Postconditions:
        - A Note instance has been created and returned; self remains unchanged.

## Side Effects:
    - None within this method: no I/O, no global mutation, no external service calls.
    - The only observable effect is the allocation of a new Note object and returning it to the caller.

### `mingus.containers.instrument.MidiPercussionInstrument.ride_cymbal_2` · *method*

## Summary:
Returns a new Note corresponding to the MIDI percussion instrument "Ride Cymbal 2" mapped to a pitched note (MIDI number 47). Does not modify the instrument object.

## Description:
This accessor constructs and returns a Note representing the percussion instrument whose General MIDI percussion key is 59 ("Ride Cymbal 2"), shifted down by one octave (59 - 12 = 47). It is intended as a named convenience method so callers can obtain a Note object for this specific percussion sound without hard-coding numeric MIDI values.

Known callers and usage context:
- No internal callers are discovered inside this class definition; the method exists to be called by external code that needs a Note object representing "Ride Cymbal 2".
- Typical call site: code that converts MIDI percussion messages or builds percussion patterns into Note objects for composition, playback, or transformation pipelines.
- Lifecycle stage: called at the moment a client needs a Note representation of the "Ride Cymbal 2" percussion instrument (lookup / translation step), not during object initialization.

Why this is a separate method:
- Provides a clear, self-documenting named accessor for a specific percussion instrument.
- Keeps percussion-to-Note mapping centralized and consistent with other percussion accessors in the class.
- Avoids repeating numeric literals across client code and makes intent explicit.

## Args:
None

## Returns:
Note
- A newly constructed instance of mingus.containers.note.Note initialized with the integer value 47 (computed as 59 - 12).
- The returned Note always represents the same MIDI pitch (47) for this method; it is not None.

## Raises:
- This method does not raise any exceptions directly.
- Any exception raised by the Note constructor (for example, input validation inside Note) will propagate to the caller.

## State Changes:
Attributes READ:
- None (the method does not read any self.<attr> fields)

Attributes WRITTEN:
- None (the method does not modify the instrument's state)

## Constraints:
Preconditions:
- self must be a valid instance of MidiPercussionInstrument (implicit for instance methods).
- No other preconditions or input parameters are required.

Postconditions:
- A new Note instance representing MIDI pitch 47 has been returned.
- The MidiPercussionInstrument instance remains unmodified.

## Side Effects:
- None local to this method (no I/O, no network calls, no mutation of external objects).
- Only side effect possibility: if the Note constructor has side effects or raises, those will occur as part of Note(...) evaluation.

## Implementation note:
- The method is a one-liner that constructs a Note from a constant expression (59 - 12) to mirror the class-wide pattern of mapping General MIDI percussion numbers to pitched Note values lowered by an octave.

### `mingus.containers.instrument.MidiPercussionInstrument.hi_bongo` · *method*

## Summary:
Returns a new Note object representing the "Hi Bongo" percussion sound (MIDI key 48) without mutating the instrument instance.

## Description:
This method is a named accessor that produces the Note used to represent the Hi Bongo percussion instrument. There are no internal callers within the provided class definition; it is intended to be invoked by external code that needs a Note instance for playback, sequencing, or when resolving instrument names to concrete Note values (for example, code that maps instrument names to these accessor methods or a playback pipeline that requests notes by instrument name). Keeping the numeric-to-note construction in its own method provides a clear, discoverable API (one method per mapped percussion sound) and isolates the literal MIDI number used for Hi Bongo so callers do not need to hard-code numeric values.

## Args:
    None

## Returns:
    Note: A newly constructed Note instance initialized with the integer 48 (computed as 60 - 12).
    - Typical value: Note(48)
    - Each call returns a fresh Note object (no caching).

## Raises:
    Propagated exceptions from Note constructor (if any), e.g. TypeError or ValueError raised by Note() when given an invalid argument. The method itself performs no validation and does not raise exceptions directly.

## State Changes:
Attributes READ:
    - None (does not read any self.<attr> fields)

Attributes WRITTEN:
    - None (does not modify any self.<attr> fields)

## Constraints:
Preconditions:
    - self must be a valid instance of MidiPercussionInstrument (method should be called on an instance).
    - No other preconditions or required initialization steps are enforced by this method.

Postconditions:
    - A Note object equal to Note(48) is returned.
    - The instrument instance (self) remains unmodified.

## Side Effects:
    - None external: no I/O, no network access, no global state mutation.
    - Only effect is creation of a Note object returned to the caller.

### `mingus.containers.instrument.MidiPercussionInstrument.low_bongo` · *method*

## Summary:
Returns a new Note object representing the low bongo percussion pitch (MIDI note number 49). The method does not modify the instrument object's state.

## Description:
This is a tiny accessor factory method that produces a Note instance for the low bongo percussion sound. The method's body constructs and returns a Note using the constant expression (61 - 12), which evaluates to 49.

Known callers:
- No callers are referenced inside this method. Callers are expected to be external code (e.g., instrument-to-note mapping utilities, percussion rendering code, or higher-level instrument helpers) that need a Note instance for the low bongo sound.

Why this is a separate method:
- Encapsulates the specific MIDI note mapping for the low bongo in a single, named location so callers can request the appropriate Note without embedding numeric constants throughout the codebase.
- Improves readability and makes it straightforward to change the mapping in one place if needed.

## Args:
- None

## Returns:
- mingus.containers.note.Note: A newly constructed Note instance initialized with the integer 49 (computed from 61 - 12).
- Deterministic: every call returns a fresh Note(initial_value=49). There are no alternate or error return values.

## Raises:
- None explicitly raised by this method.
- Implicit assumption: if the Note constructor raises due to invalid arguments or environment, that exception will propagate to the caller (this method does not catch exceptions).

## State Changes:
- Attributes READ: none (this method does not read any self.<attr> values).
- Attributes WRITTEN: none (this method does not modify self or any of its attributes).

## Constraints:
- Preconditions:
    - None required by this method itself.
    - The runtime must have a Note constructor that accepts a single integer argument; the method calls Note(49).
- Postconditions:
    - After the call, the returned object is a Note instance that represents MIDI pitch 49. The internal state of self is unchanged.

## Side Effects:
- None: no I/O, no network or file operations, and no mutations of objects outside of the returned Note instance (the returned Note is newly created by the call).

### `mingus.containers.instrument.MidiPercussionInstrument.mute_hi_conga` · *method*

## Summary:
Returns a Note instance representing the "Mute Hi Conga" percussion sound (MIDI percussion key 62 mapped to a Note value of 50). Does not modify object state.

## Description:
This accessor method provides a named, self-documenting way to obtain the Note that corresponds to the MIDI percussion instrument "Mute Hi Conga". It constructs and returns a Note from the integer expression 62 - 12, which evaluates to 50.

Known callers:
- No internal call sites were found in the repository for this specific method. It is intended to be called by external user code or higher-level MIDI/score-generation logic when a Note for the "Mute Hi Conga" is required (for example, when building a percussion track or inserting a percussion hit into a sequence).

Why this is a separate method:
- Each percussion instrument is exposed via a dedicated, named method to provide a clear, discoverable API (e.g., instrument.mute_hi_conga()) rather than requiring users to remember numeric MIDI keys.
- Keeping the mapping in discrete methods makes it easy to reference the semantics (instrument name) in user code and documentation, and to keep the numeric-to-Note construction consistent across all percussion mappings.

## Args:
- None

## Returns:
- mingus.containers.note.Note
  - A Note object constructed from the integer 62 - 12 (i.e., Note(50)).
  - There are no alternative return values or error codes; the method always returns a Note instance.

## Raises:
- None documented or raised by this method. (It performs a straightforward constructor call; any exceptions would originate from the Note constructor itself if it validates inputs.)

## State Changes:
- Attributes READ:
  - None (the method does not reference any self.<attr> fields)
- Attributes WRITTEN:
  - None (the method does not modify the object's state)

## Constraints:
- Preconditions:
  - No preconditions on the MidiPercussionInstrument instance are required; the method does not depend on instance state.
  - The Note constructor must accept the integer 50 as a valid input (if the Note class performs validation, that validation must pass).
- Postconditions:
  - After the call, self is unchanged.
  - The caller receives a fresh Note instance representing the mute hi conga (value 50).

## Side Effects:
- None. The method does not perform I/O, external service calls, or mutate objects outside of returning the newly created Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.open_hi_conga` · *method*

*No documentation generated.*

### `mingus.containers.instrument.MidiPercussionInstrument.low_conga` · *method*

## Summary:
Returns a new Note instance representing the "Low Conga" percussion sound; does not modify the instrument object.

## Description:
This accessor constructs and returns a Note object initialized with the integer value computed as 64 - 12 (i.e., 52). Within this module the integer keys in the instrument mapping correspond to General MIDI percussion note numbers; this method produces the same numbered note shifted down one octave by subtracting 12 semitones.

Known callers:
- No callers were found in the immediate repository snapshot for this specific method. Conceptually, this method is intended to be used by caller code that needs a Note instance for the Low Conga percussion (for playback, sequencing, or mapping percussion names to Note objects).

Why this is its own method:
- Provides a clear, named accessor for the "Low Conga" percussion note that mirrors the other percussion accessors in MidiPercussionInstrument.
- Encapsulates the integer computation and creation of a Note in one place so consumers can request the instrument sound by name instead of hardcoding note numbers.

## Args:
- None (only implicit self)

## Returns:
- mingus.containers.note.Note: A newly constructed Note object created by calling Note(52). The numeric argument is computed as 64 - 12 in the source. No caching is performed; each call returns a fresh Note instance.

## Raises:
- This method does not explicitly raise any exceptions. Any exceptions raised by the Note constructor (if invalid input or runtime errors occur there) will propagate to the caller.

## State Changes:
- Attributes READ: None (this method does not access any self.<attr> attributes).
- Attributes WRITTEN: None (this method does not modify self or any external state).

## Constraints:
Preconditions:
- self must be a valid instance of MidiPercussionInstrument (or at least an object supporting bound method calls). No other preconditions; the method does not depend on instance state.

Postconditions:
- Returns a Note object initialized with the integer 52.
- The MidiPercussionInstrument instance remains unchanged.

## Side Effects:
- None. The method does not perform I/O, external calls, or mutate objects outside of returning the newly created Note.

### `mingus.containers.instrument.MidiPercussionInstrument.high_timbale` · *method*

## Summary:
Returns a Note object representing the "High Timbale" percussion sound by constructing a Note with the MIDI code 65 shifted down by one octave (65 - 12).

## Description:
This method provides a convenient, named accessor that produces a Note corresponding to the MIDI percussion mapping entry for "High Timbale". It exists to let callers request a Note object for this percussion instrument by name instead of remembering numeric MIDI codes.

Known callers and invocation context:
- No internal callers were found in the surrounding module; this method is intended to be called by external user code or higher-level sequencing/arrangement code that needs a Note instance for the high timbale percussion sound.
- Typical lifecycle stage: used when constructing percussion patterns, drum sequences, or when converting percussion mappings into Note objects for playback or further manipulation.

This logic is factored into its own method to:
- Provide a self-documenting, named API for each percussion instrument in the mapping.
- Avoid repeating numeric literals in client code and centralize the numeric-to-Note conversion for readability and maintainability.

## Args:
- None

## Returns:
- mingus.containers.note.Note
    - A newly constructed Note instance created with the integer value 65 - 12 (evaluates to 53).
    - The returned Note represents the instrument's mapped MIDI code shifted down one octave by the implementation convention used across this class.
    - The method always returns a Note instance; it never returns None or other types.

## Raises:
- This method does not raise exceptions itself.
- Any exception raised would come from the Note constructor (for example, if Note enforces argument types/values); such exceptions are not raised by this method directly but may propagate from Note(...) if the Note class enforces stricter invariants.

## State Changes:
- Attributes READ:
    - None (this method does not read any self.<attr> attributes)
- Attributes WRITTEN:
    - None (this method does not modify self or any external state)

## Constraints:
- Preconditions:
    - self should be an instance of MidiPercussionInstrument (or a compatible object exposing this method). No other preconditions are required.
    - No arguments are required.
- Postconditions:
    - A new Note instance has been created and returned with the integer parameter equal to 53 (65 - 12).
    - The MidiPercussionInstrument instance remains unmodified.

## Side Effects:
- No I/O is performed.
- No external services are called.
- No mutations of objects outside of the newly created Note instance occur.

### `mingus.containers.instrument.MidiPercussionInstrument.low_timbale` · *method*

## Summary:
Returns a Note instance representing the low timbale MIDI percussion pitch (one octave below the mapped MIDI number) without modifying the instrument object.

## Description:
Known callers and context:
- No direct callers are present within the provided class source. This method is intended as a convenience accessor used by client code that needs a Note representing the "Low Timbale" percussion sound defined in the instrument's MIDI mapping.
- Typical lifecycle: invoked at runtime when constructing or scheduling percussion notes for playback, sequencing, or analysis.

Why this is its own method:
- The class defines many small, named accessor methods (one per percussion instrument) that consistently return a Note for the instrument's MIDI key minus 12 (one octave down). Encapsulating the calculation in a named method (rather than inlining the integer) improves readability, provides a stable public API for callers, and groups the domain knowledge (which MIDI key corresponds to "Low Timbale") in one place.

## Args:
    self: MidiPercussionInstrument
        The instrument instance. No additional arguments.

## Returns:
    mingus.containers.note.Note
        A new Note instance constructed with the integer value 66 - 12 (i.e., 54). This represents the MIDI note number one octave below the mapping entry for Low Timbale.
        - Normal return: a Note object initialized with 54.
        - There are no alternative return values or sentinel values produced by this method.

## Raises:
    None raised directly by this method.
    - If the Note constructor enforces type/value constraints, that constructor may raise its own exceptions for invalid input; this method itself does not validate inputs or raise exceptions.

## State Changes:
    Attributes READ:
        None — the method does not access or depend on any self.<attr> attributes.
    Attributes WRITTEN:
        None — the method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - self must be an instance of MidiPercussionInstrument (or at least provide the same interface). No other preconditions.
    Postconditions:
        - A new Note object has been created and returned with the numeric value 54.
        - The instrument instance remains unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside of the newly created Note instance (i.e., no global state changes).

### `mingus.containers.instrument.MidiPercussionInstrument.high_agogo` · *method*

## Summary:
Returns a new Note object representing the "High Agogo" percussion key (MIDI number 67 mapped to Note(55)), without modifying the instrument instance.

## Description:
This is a convenience accessor that constructs and returns a Note corresponding to the MIDI percussion key labeled "High Agogo" in the MidiPercussionInstrument mapping. The method is a thin wrapper that instantiates a Note with the integer value 67 - 12 (evaluates to 55). There are no internal callers in the MidiPercussionInstrument class; it is intended to be called by client code or higher-level sequencing/score-building logic when a Note object for the high agogo percussion sound is required.

This logic is separated into its own method to provide a clear, discoverable, and consistent API: every percussion instrument in MidiPercussionInstrument supplies a similarly named method that returns the corresponding Note. Having individual methods keeps client code readable (e.g., instrument.high_agogo()) and avoids duplicating the numeric literal throughout the codebase.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A new Note instance constructed with the integer 55 (result of 67 - 12). This is the only return value produced by the method.

## Raises:
    Any exception raised by the Note constructor may propagate through this method.
    The method itself does not raise exceptions explicitly.

## State Changes:
    Attributes READ:
        None
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - No preconditions on self are required; the method does not inspect or depend on any instance attributes.
        - The Note class must accept an integer argument (55) in its constructor; otherwise the Note constructor may raise.

    Postconditions:
        - Returns a freshly constructed Note(55).
        - The MidiPercussionInstrument instance (self) remains unmodified.

## Side Effects:
    - No I/O operations are performed.
    - No mutations to objects outside of the newly created Note instance occur.
    - Any side effects depend solely on the Note constructor (e.g., if Note registers itself elsewhere), which are not performed by this method directly.

### `mingus.containers.instrument.MidiPercussionInstrument.low_agogo` · *method*

## Summary:
Returns a Note object representing the "Low Agogo" percussion sound (MIDI mapping 68) transposed down one octave, and does not modify the instrument's state.

## Description:
This instance method is a named convenience accessor on MidiPercussionInstrument that produces a Note corresponding to the Low Agogo percussion sound. It constructs and returns a new Note initialized with the numeric pitch value computed from the hard-coded MIDI mapping (68) minus 12 semitones (one octave), i.e., 56.

Known callers and usage context:
- There are no other methods in the provided class that call this method internally; it is intended to be invoked by user code or higher-level composition code when a Note for the Low Agogo sound is required.
- Typical lifecycle stage: called during composition or when building a track/measure to obtain a Note instance that represents the Low Agogo percussion sound for further processing (adding to a bar, converting to MIDI messages, etc.).

Why this is its own method:
- The class exposes one method per percussion sound as a clear, discoverable API (named accessors) so callers can request specific percussion notes by name rather than by numeric constants.
- Keeping this logic in its own method makes the mapping explicit and readable, and centralizes the small conversion (subtracting 12 semitones) used across all percussion accessors.

## Args:
None

## Returns:
- Note: A new Note instance constructed with the integer pitch value 56 (computed as 68 - 12).
- The returned Note represents the Low Agogo percussion sound transposed down one octave from the raw MIDI mapping value.

## Raises:
- This method does not raise any exceptions directly.
- Any exception raised would originate from the Note constructor if it validates inputs; such exceptions are not created by this method itself.

## State Changes:
- Attributes READ: None (the method does not access any self.<attr> attributes)
- Attributes WRITTEN: None (the method does not modify self or external state)

## Constraints:
- Preconditions: self must be a properly constructed MidiPercussionInstrument instance; no additional state or arguments are required.
- Postconditions: A Note object is returned with pitch value 56. No attributes on self are modified.

## Side Effects:
- None. The method performs no I/O, external calls, or mutations to objects outside the newly created Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.cabasa` · *method*

## Summary:
Returns a newly constructed Note representing the Cabasa percussion sound (GM key 69 shifted by -12). Does not modify the instrument object's state.

## Description:
This is a convenience accessor on MidiPercussionInstrument that produces a Note corresponding to the Cabasa percussion instrument. It constructs and returns a new Note initialized with the integer value 69 - 12 (which evaluates to 57).

Known callers and context:
- No direct internal callers were found in the repository. Typical call sites are application or library code that requests a percussion instrument's Note by calling the appropriately-named method on a MidiPercussionInstrument instance (for example, when converting a percussion mapping to Note objects, assembling patterns, or exposing human-friendly instrument accessors).
- It is intended to be used at runtime when code needs a Note object for the Cabasa sound (e.g., when assembling a percussion track).

Why this logic is a separate method:
- Provides a clear, discoverable accessor named after the instrument (consistent with the many other instrument-named methods on MidiPercussionInstrument).
- Keeps mapping-to-Note construction centralized and uniform across all percussion sounds, improving readability and enabling callers to obtain Note objects without duplicating the numeric translation.

## Args:
    None

## Returns:
    Note
    - A newly created Note instance initialized with the integer 57 (computed as 69 - 12).
    - The returned Note is independent of the instrument object (a fresh instance each call).
    - There are no special-case return values; on success a Note is always returned.

## Raises:
    - Propagates any exception raised by the Note constructor. For example, if the Note initializer rejects the provided value or receives an invalid type, that exception (TypeError, ValueError, or a library-specific exception) will propagate to the caller.
    - The method itself does not raise exceptions directly.

## State Changes:
    Attributes READ:
        - None (does not read any self.<attr> fields)
    Attributes WRITTEN:
        - None (does not modify self or any other object attributes)

## Constraints:
    Preconditions:
        - self must be a valid, initialized MidiPercussionInstrument instance (typical instance returned by MidiPercussionInstrument()).
        - No arguments are required.
    Postconditions:
        - A Note instance representing Cabasa (GM key 69 adjusted by -12) is returned.
        - The receiver object (self) remains unmodified.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside of the newly created Note instance returned by the method.

### `mingus.containers.instrument.MidiPercussionInstrument.maracas` · *method*

## Summary:
Returns a new Note object representing the MIDI percussion instrument "Maracas" by constructing a Note with the numeric pitch 70 - 12 (58), without mutating the instrument.

## Description:
This convenience accessor produces a Note instance that encodes the maracas percussion sound as used by the library's MIDI percussion mapping. It is intended to be called when client code or higher-level utilities need a Note object corresponding to the "Maracas" percussion entry defined in the MidiPercussionInstrument mapping.

Known callers:
- No direct callers were found inside the repository (no internal references to maracas were discovered). It is primarily intended for external or user code to request a maracas Note by name.
- Typical usage context: invoked during composition or MIDI event generation pipelines where a developer wants a Note representing the maracas percussion for scheduling or playback.

Why this is a separate method:
- Provides a named, self-documenting way to obtain the specific percussion Note (keeps user code readable).
- Matches the pattern used across MidiPercussionInstrument for each percussion sound (one method per mapped percussion ID) so callers can obtain instrument-specific notes by descriptive names rather than numeric constants.

## Args:
    self: (MidiPercussionInstrument) Bound instance on which the method is invoked. No additional arguments are accepted.

## Returns:
    mingus.containers.note.Note
        A newly constructed Note instance created by calling Note(70 - 12). The numeric argument evaluates to 58, so the returned Note is constructed with the integer 58.
        - The method always returns a Note object when the Note constructor succeeds.
        - If the Note constructor raises an exception for this argument, that exception will propagate to the caller.

## Raises:
    Any exception raised by the Note constructor will propagate unchanged (the method contains no internal try/except). There are no explicit raises in this method itself.

## State Changes:
    Attributes READ:
        - None (the method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        - None (the method does not modify self or any external state)

## Constraints:
    Preconditions:
        - The method must be called on a valid MidiPercussionInstrument instance (i.e., "self" must be bound).
        - The Note constructor must accept an integer argument; if it does not, the caller will receive the resulting exception.

    Postconditions:
        - On success, returns a new Note instance constructed with integer 58.
        - The internal state of the MidiPercussionInstrument instance is unchanged.

## Side Effects:
    - No I/O is performed.
    - No network or filesystem interactions.
    - Only effect is creation of a new Note Python object; no external objects are mutated.

### `mingus.containers.instrument.MidiPercussionInstrument.short_whistle` · *method*

## Summary:
Returns a new Note instance representing the MIDI percussion voice "Short Whistle" (constructed with the integer 71 - 12 → 59). Does not modify the instrument object's state.

## Description:
This method is a convenience accessor on MidiPercussionInstrument that constructs and returns a Note corresponding to the MIDI percussion mapping entry for "Short Whistle". No callers were found in the provided code memory for this specific method; typical usage is from user code or higher-level routines that request a Note for a specific percussion sound (for example, when assembling a MIDI event stream or when converting instrument names to Note objects).

This logic is implemented as its own method (rather than inlined) for consistency and discoverability: the MidiPercussionInstrument class exposes one method per named percussion sound, each returning the Note representing that sound. This provides a clear, self-documenting API for callers that want a Note object for a particular percussion instrument.

## Args:
This method takes no arguments other than self.

## Returns:
Note
    A freshly-constructed Note object created by calling Note(71 - 12). From the source this evaluates to Note(59). No mutation of the instrument occurs.
    - Normal return: a Note instance constructed with the integer 59.
    - Edge cases: the method itself does not handle or check errors from the Note constructor; if Note(...) raises, that exception will propagate to the caller.

## Raises:
This method does not raise any exceptions directly. However, any exception thrown by the Note constructor (for example, if Note disallows the provided value) will propagate to the caller.

## State Changes:
Attributes READ:
    - None (the method does not read any self.<attr> attributes)

Attributes WRITTEN:
    - None (the method does not modify self or any external state)

## Constraints:
Preconditions:
    - self must be a valid MidiPercussionInstrument instance (i.e., the object is initialized).
    - The Note constructor must accept the integer value 59; otherwise an exception from Note will propagate.

Postconditions:
    - On successful return, the caller receives a Note instance constructed with the integer 59.
    - The instrument instance is unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutations to objects outside self, aside from any side effects that may be caused by the Note constructor itself (not performed by this method).

## Implementation notes (for reimplementation):
    - Implement as a no-argument instance method that returns the result of calling Note(71 - 12).
    - Keep the arithmetic literal (71 - 12) or replace with its evaluated value 59; either yields the same Note constructor argument.

### `mingus.containers.instrument.MidiPercussionInstrument.long_whistle` · *method*

## Summary:
Returns a new Note instance representing the instrument's "long whistle" pitch (constructed with the integer value 72 - 12 = 60). The call does not modify the instrument object's state.

## Description:
This method provides the canonical "long whistle" pitch for a MidiPercussionInstrument as a Note object. In the provided implementation it simply constructs and returns Note(60) (the result of 72 - 12) and does not interact with or mutate the instrument instance.

Known callers and context:
- No specific callers are present in the extracted context provided. Conceptually, this method is intended to be called by code that maps percussion instrument roles to canonical Note values, for example when assembling an instrument-to-note mapping, generating MIDI events, or selecting default pitches for playback or notation.
- Typical lifecycle stage: invoked at mapping/lookup time (e.g., during MIDI generation, instrument initialization, or score rendering) whenever the "long whistle" pitch for this instrument is needed.

Why this is a separate method:
- Encapsulates the mapping of the semantic instrument role "long whistle" to a concrete Note construction in one place.
- Makes the mapping overrideable by subclasses or easier to patch in tests.
- Improves readability and documents the intended canonical pitch for this percussion role.

## Args:
- None

## Returns:
- Note: A newly constructed Note object produced by calling Note(72 - 12). The exact interpretation of the integer argument (60) is governed by the Note constructor; this method simply forwards that integer to Note and returns the resulting object.
- Edge-case return values: None. The method always attempts to construct and return a Note; if Note's constructor raises, that exception propagates to the caller.

## Raises:
- This method does not raise exceptions itself. Any exception raised by the Note constructor (for example, due to invalid constructor arguments inside Note) will propagate to the caller unchanged.

## State Changes:
- Attributes READ: None (this method does not read any self.<attr> attributes)
- Attributes WRITTEN: None (this method does not modify the instrument instance)

## Constraints:
- Preconditions:
    - self must be a valid MidiPercussionInstrument instance (no other preconditions checked by this method).
    - The Note constructor must accept the integer 60; otherwise Note will raise and that exception will propagate.
- Postconditions:
    - A Note instance constructed with the integer value 60 is returned.
    - The instrument instance (self) remains unchanged.

## Side Effects:
- None within the running process other than creating and returning a new Note object. There is no I/O, no mutation of external objects, and no calls to external services.

### `mingus.containers.instrument.MidiPercussionInstrument.short_guiro` · *method*

## Summary:
Creates and returns a new Note instance for the instrument's "short guiro" percussion pitch (the method does not modify the instrument).

## Description:
This instance method constructs and returns a Note by evaluating the literal expression Note(73 - 12) found in the implementation. The arithmetic expression 73 - 12 evaluates to 61, so the effect is identical to calling Note(61). The method is a small, named accessor that encapsulates this fixed pitch mapping so callers can obtain the corresponding Note without hardcoding numeric values.

Why this is a separate method:
- Centralizes the pitch mapping for the "short guiro" sound so the value can be changed in one place.
- Improves readability for code that requests percussion-specific Note objects.

Known callers / invocation context:
- The repository snapshot used to generate this documentation did not provide verified call sites; callers are not asserted here. Conceptually, callers will be code that translates percussion instrument kinds into Note objects for MIDI event creation, playback, or serialization.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A newly constructed Note instance created with the integer 61 (i.e., result of 73 - 12). This method returns a fresh Note object on each call.

## Raises:
    Any exception raised by mingus.containers.note.Note when constructing a Note with the integer 61 (for example, TypeError or ValueError). This method performs no exception handling and will propagate any exception raised by the Note constructor.

## State Changes:
    Attributes READ:
        None — the method does not access any self attributes.
    Attributes WRITTEN:
        None — the method does not modify the instrument instance.

## Constraints:
    Preconditions:
        - Called on a valid instance (self should be an instance of the instrument class).
        - The Note constructor must accept an integer pitch (61) as input; otherwise the Note constructor will raise an exception which this method will propagate.

    Postconditions:
        - Returns a Note instance representing pitch 61.
        - No mutation occurs on the instrument instance or external state.

## Side Effects:
    - No I/O, network, or external service calls.
    - Constructs and returns a new Note object; no other objects are mutated.

## Minimal usage example:
    instrument.short_guiro()   # returns a Note equivalent to Note(61)

## Implementation notes for reimplementation:
    - Implement as a zero-argument instance method that returns Note(73 - 12).
    - Do not catch or translate exceptions from the Note constructor; allow them to propagate to the caller.

### `mingus.containers.instrument.MidiPercussionInstrument.long_guiro` · *method*

## Summary:
Return a new Note object representing the MIDI percussion sound "Long Guiro" by constructing Note with the integer value 62 (computed from 74 - 12). The method does not modify the instrument instance.

## Description:
This accessor method returns the exact Note value the class uses for the "Long Guiro" percussion sound. The integer passed to Note is computed directly as 74 - 12 (result 62). The MidiPercussionInstrument.mapping dictionary contains the entry 74: "Long Guiro", which is the source of the numeric constant used here.

Known callers:
    - No callers are defined within this module or class in the provided source.

Why this is a separate method:
    - The class follows a one-method-per-sound pattern, where each named percussion sound has its own accessor that returns the corresponding Note.

## Args:
    None

## Returns:
    mingus.containers.note.Note
        A Note instance constructed with the integer value 62. Each invocation returns a newly created Note object produced by calling Note(62).

## Raises:
    Any exception raised by the Note constructor will propagate to the caller. This method performs no validation or error handling.

## State Changes:
    Attributes READ:
        None — the method does not reference self attributes.
    Attributes WRITTEN:
        None — the method does not modify self or external state.

## Constraints:
    Preconditions:
        - The Note name must be defined in the module imports; otherwise the call will fail at runtime.
        - No state is required on the MidiPercussionInstrument instance to call this method.
    Postconditions:
        - A new Note object initialized with integer 62 is returned.
        - The MidiPercussionInstrument instance remains unchanged.

## Side Effects:
    - No I/O or external service interactions.
    - No mutation of objects outside the method, aside from creating and returning the Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.claves` · *method*

## Summary:
Returns a new Note object constructed with the integer value 63 (computed as 75 - 12) without modifying the instrument instance.

## Description:
This method is a named accessor that produces a Note representing the MIDI pitch value 63 (the value produced by 75 - 12). It does not take any inputs nor mutate the state of the MidiPercussionInstrument instance.

Known callers:
- No explicit call sites were found in the provided repository snapshot for this method. Conceptually, it is intended to be called wherever a code path needs the Note corresponding to the "claves" percussion instrument (for example, when mapping percussion instrument names to MIDI notes or when generating a Note for playback).

Why this is a separate method:
- Encapsulates the mapping from the named percussion instrument "claves" to its numeric Note value in one place for clarity and potential overriding in subclasses. Keeping this logic in a dedicated accessor makes tests and overrides simpler than inlining the numeric constant at call sites.

## Args:
- None

## Returns:
- mingus.containers.note.Note: A newly constructed Note instance created by calling Note(63).
  - The integer value passed into the Note constructor is 63, computed as 75 - 12.
  - If the Note constructor interprets integers as MIDI pitch numbers, this returned Note will represent that pitch; exact semantics depend on the Note implementation.

## Raises:
- This method does not explicitly raise any exceptions itself.
- Any exception raised by the Note constructor (for example, invalid argument errors thrown by Note when given an unacceptable type or value) will propagate to the caller.

## State Changes:
- Attributes READ:
    - None (the method does not read or depend on any self.<attribute> fields)
- Attributes WRITTEN:
    - None (the method does not modify self or any external stored state)

## Constraints:
- Preconditions:
    - self must be a properly constructed MidiPercussionInstrument instance (no internal state is required by this method).
    - The Note constructor must accept a single integer argument; otherwise a constructor-level exception will be raised.
- Postconditions:
    - A new Note instance has been created and returned; self remains unchanged.
    - No caching or reuse of Note instances occurs within this method.

## Side Effects:
- None within this repository: no I/O, no external service calls, and no mutation of objects outside the returned Note instance.
- The only side effect observable to the caller is allocation of a new Note object (in memory).

### `mingus.containers.instrument.MidiPercussionInstrument.hi_wood_block` · *method*

## Summary:
Returns a new Note object representing the "Hi Wood Block" percussion sound (constructed from the constant numeric pitch 76 - 12) without modifying the instrument object.

## Description:
- Known callers: No direct callers are present within the local codebase snapshot. This method is an access convenience intended for external callers (user code, sequencers, or other library code) that need a Note object corresponding to the Hi Wood Block percussion mapping.
- Lifecycle / pipeline stage: Invoked when code needs to obtain a Note representing the Hi Wood Block percussion instrument (e.g., during pattern generation, playback preparation, or when building a percussion track).
- Rationale for separate method: The class exposes one method per percussion mapping for readability and convenience so callers can request semantic percussion names (hi_wood_block) instead of numeric MIDI values. Keeping this logic in its own small method centralizes the mapping and makes call sites clearer.

## Args:
This method takes no arguments.

## Returns:
- mingus.containers.note.Note: A newly constructed Note instance created by calling Note(76 - 12). Concretely, the integer passed to the Note constructor is 64 (result of 76 - 12).
- No additional return values or sentinel values are used.

## Raises:
- This method does not explicitly raise exceptions itself. Any exception raised will originate from the Note constructor; the documentation does not assume or enumerate specific exception types because those are defined by the Note implementation.

## State Changes:
- Attributes READ: none (the method does not access any self.<attr> fields).
- Attributes WRITTEN: none (the method does not modify self or any of its attributes).

## Constraints:
- Preconditions: None required by this method; it does not depend on instance state or input parameters.
- Postconditions: After the call, the returned value is a Note instance that was constructed with the integer 64. Self remains unchanged.

## Side Effects:
- Creates (allocates) a new Note object; no I/O, no network calls, and no mutations of objects outside the method.

### `mingus.containers.instrument.MidiPercussionInstrument.low_wood_block` · *method*

## Summary:
Returns a Note object representing the "Low Wood Block" percussion sound (MIDI key 77 shifted down one octave), without modifying the instrument instance.

## Description:
This method is a convenience accessor on the MidiPercussionInstrument that constructs and returns a Note corresponding to the MIDI percussion mapping entry for "Low Wood Block". It does not consult the instance mapping or mutate any state — it returns a new Note constructed from the constant numeric value 77 - 12 (i.e., 65).

Known callers and context:
- There are no internal callers within this class; the method is part of the public API of MidiPercussionInstrument and is intended to be called by client code (composition/sequencing code, MIDI event builders, or other higher-level routines) when a Note representing the low wood block percussion is required.
- Typical lifecycle step: invoked at composition or MIDI event generation time to obtain the Note object to place into a track or to convert into a MIDI event.

Why this logic is a separate method:
- Provides a clear, discoverable, and named accessor for a specific percussion instrument consistent with the rest of the class (each percussion sound has its own method).
- Keeps callers from needing to remember numeric MIDI codes and octave adjustments; centralizes the numeric constant in one place.

## Args:
This method takes no arguments.

## Returns:
Note
- A new instance of mingus.containers.note.Note constructed with the integer 77 - 12 (value: 65).
- The returned Note is a fresh object and is independent of the instrument instance.

## Raises:
- None raised by this method directly. (The method only constructs and returns a Note; any exceptions would originate from the Note constructor and are not handled here.)

## State Changes:
Attributes READ:
- None. The method does not read any self.<attr> fields.

Attributes WRITTEN:
- None. The method does not modify self or any external object.

## Constraints:
Preconditions:
- self should be an initialized MidiPercussionInstrument instance (method is an instance method).
- No other preconditions on attributes or arguments.

Postconditions:
- The instrument instance remains unchanged.
- The caller receives a Note object representing MIDI value 65 (77 - 12).

## Side Effects:
- None. The method performs no I/O, no external service calls, and does not mutate objects outside the freshly returned Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.mute_cuica` · *method*

## Summary:
Returns a new Note instance representing the MIDI pitch value computed for the muted cuica percussion sound; does not modify the instrument object.

## Description:
This method is a small, named accessor that encapsulates the mapping between this percussion instrument and the numeric pitch used for a "mute cuica" sound. It constructs and returns a fresh Note initialized with the integer expression 78 - 12 (i.e., 66).

Known callers:
- No callers are present in the provided code snapshot. In typical usage within a MIDI/percussion mapping context, callers would request named percussion note mappings from an instrument instance when building MIDI events or when translating percussion names to note values.

Why this is a separate method:
- Encapsulates a single, reusable mapping value behind a named method so callers can request the muted cuica pitch by name.
- Keeps the mapping centralized for clarity and makes it easy to override in subclasses or to change the mapping in one place.

## Args:
This method takes no arguments.

## Returns:
Note
- A newly constructed Note object created by calling Note(78 - 12).
- The numeric value passed to the Note constructor is 66 (computed as 78 - 12). The semantic interpretation of that integer (for example, whether it represents a MIDI note number) is determined by the Note class implementation.

## Raises:
- This method itself does not raise explicit exceptions.
- Any exceptions raised by the Note constructor (for example, input validation errors inside Note) are propagated to the caller.

## State Changes:
Attributes READ:
- None. The method does not access any attributes of self.

Attributes WRITTEN:
- None. The method does not modify self or any of its attributes.

## Constraints:
Preconditions:
- No preconditions on self are required by this method; it does not read or depend on instance state.

Postconditions:
- self remains unchanged.
- The caller receives a Note instance constructed with integer 66.

## Side Effects:
- Allocates and returns a new Note object.
- No I/O, no external service calls, and no mutation of objects outside of the newly created Note instance.

### `mingus.containers.instrument.MidiPercussionInstrument.open_cuica` · *method*

## Summary:
Returns a new Note instance representing the MIDI pitch for the "Open Cuica" percussion sound (computed as 79 - 12 = 67) and does not modify the instrument object's state.

## Description:
Known callers:
    - No internal call-sites were found in the repository memory for this method. It is intended to be called by client code or higher-level routines that need a Note corresponding to the "Open Cuica" percussion instrument (for example, when building percussion patterns or mapping instrument names to Note objects).

Lifecycle / context:
    - This method is part of MidiPercussionInstrument and is used when a caller needs a ready-to-use Note for the Open Cuica percussion voice. It represents a convenience accessor that encodes the standard mapping from General MIDI percussion numbers to the Note constructor input used across the class.

Why this is a separate method:
    - Provides a named, discoverable convenience accessor consistent with the other percussion methods in the class (e.g., mute_cuica). Keeps mapping logic localized and avoids repeating the numeric calculation at call sites; also improves readability and discoverability for library users.

## Args:
    None

## Returns:
    Note
        A newly-constructed mingus.containers.note.Note instance created by calling Note(79 - 12). Numerically this is Note(67). Each call produces a new Note object (the constructor is invoked on every call).

## Raises:
    - This method does not explicitly raise exceptions itself.
    - Any exception raised by the Note constructor (for example, due to invalid constructor arguments) is propagated to the caller.

## State Changes:
Attributes READ:
    - None (this method does not read any self.<attr> fields)

Attributes WRITTEN:
    - None (this method does not modify any self.<attr> fields)

## Constraints:
Preconditions:
    - self must be a valid MidiPercussionInstrument instance (method bound to an instance).
    - The Note constructor must accept the integer value 67 as a valid initializer argument (the method supplies that integer).

Postconditions:
    - On successful return, the caller receives a Note instance initialized with the integer value 67.
    - The MidiPercussionInstrument instance is unchanged (no attribute read or write side effects).

## Side Effects:
    - No I/O, no external service calls.
    - The only observable effect is allocation/construction of a new Note object; no global or object state is mutated.

### `mingus.containers.instrument.MidiPercussionInstrument.mute_triangle` · *method*

## Summary:
Returns a Note object representing the "mute triangle" percussion voice as the MIDI key 80 shifted down by one octave (80 - 12 = 68). This does not modify the instrument object.

## Description:
This method provides a named accessor for the MIDI percussion instrument "Mute Triangle" by returning a Note instance with the appropriate MIDI pitch number. It mirrors the pattern used by all other percussion accessor methods in the same class (each method returns a Note created from the mapped MIDI number minus 12), keeping the mapping and creation logic localized and easy to discover.

Known callers:
- No internal callers are defined in this file. Typical usage is external: client code or higher-level sequence-building code calls this method on a MidiPercussionInstrument instance when it needs a Note representing the mute triangle percussion sound (for example, when assembling a percussion pattern or converting a percussion mapping into Note objects).

Why this is a separate method:
- Encapsulates the mapping from a named percussion instrument to the specific Note representing its MIDI pitch.
- Keeps the public API consistent and discoverable: users can call instrument.mute_triangle() instead of constructing Note objects by hard-coded integers.

## Args:
    self (MidiPercussionInstrument): Instance on which the method is invoked. No other arguments.

## Returns:
    mingus.containers.note.Note: A Note instance created with the MIDI pitch number 68, computed as 80 - 12. There are no special sentinel or alternative return values; the method always returns a Note object unless an exception is raised during Note construction.

## Raises:
    Any exception raised by the Note constructor may propagate out of this method. The method itself performs no explicit checks or raises its own exceptions.

## State Changes:
    Attributes READ:
        - None (the method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        - None (the method does not modify the instance)

## Constraints:
    Preconditions:
        - The method must be called on a valid, initialized MidiPercussionInstrument instance.
        - The Note class must accept the numeric MIDI pitch used here; if the Note constructor enforces constraints, those must be satisfied (this method always supplies integer 68).
    Postconditions:
        - The MidiPercussionInstrument instance remains unchanged.
        - The caller receives a Note instance representing MIDI pitch 68.

## Side Effects:
    - None intrinsic to this method: no I/O, no external service calls, and no mutations to objects outside the returned Note instance (the Note object is newly constructed and returned to the caller).

### `mingus.containers.instrument.MidiPercussionInstrument.open_triangle` · *method*

## Summary:
Returns a Note instance representing the "open triangle" percussion sound by constructing a Note with the integer value 81 - 12 (resulting in 69). Does not modify the instrument object.

## Description:
This method is a named accessor on MidiPercussionInstrument that produces a Note corresponding to the Open Triangle percussion mapping. In the current implementation it simply returns Note(81 - 12), i.e., Note(69).

Known callers and context:
- No direct callers were found in the inspected code snippet. In practice, this method is intended to be called when client code or higher-level sequencing/event-building code needs a Note object for the "open triangle" percussion sound (for example, when translating MIDI-percussion mapping entries into Note objects for playback or processing).
- This method is part of a family of similarly-named accessor methods on MidiPercussionInstrument (e.g., mute_triangle, tambourine) each returning a Note constructed from a fixed integer calculated as (MIDI_map_number - 12).

Why this logic is a separate method:
- Provides a clear, discoverable, and self-documenting way to obtain a Note for this specific percussion instrument without requiring callers to remember or repeat the numeric MIDI mapping and octave adjustment.
- Keeps caller code concise and consistent by centralizing the mapping-to-Note construction in named methods instead of inlining numeric literals throughout the codebase.

## Args:
    self: MidiPercussionInstrument
        - The instance is required by Python method semantics but is not inspected or modified by this method.

## Returns:
    mingus.containers.note.Note
        - A Note instance constructed with the integer value 69 (computed from 81 - 12).
        - There are no alternative return paths; this method always returns the result of the Note(...) constructor call.
        - If the Note constructor raises an exception for the given input, that exception will propagate to the caller.

## Raises:
    (No raises are explicitly triggered by this method itself.)
    - Any exception raised by the Note constructor (e.g., due to invalid constructor arguments) will propagate unchanged.
    - This method does not raise UnexpectedObjectError or other exceptions directly.

## State Changes:
    Attributes READ:
        - None: this method does not read any attributes from self.
    Attributes WRITTEN:
        - None: this method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - The Note class must be importable and callable with a single integer positional argument (the current code invokes Note(69)).
        - The caller must handle any exceptions propagated from the Note constructor.

    Postconditions:
        - After the call, no state of the MidiPercussionInstrument instance has changed.
        - The caller receives a Note instance representing MIDI-percussion mapping number 81 adjusted by -12 (i.e., 69).

## Side Effects:
    - None within the repository: the method performs no I/O, network access, or global mutations.
    - The only observable effect is creation of a new Note object (allocation and any side effects that Note(...) itself may perform, which are outside the scope of this method).

