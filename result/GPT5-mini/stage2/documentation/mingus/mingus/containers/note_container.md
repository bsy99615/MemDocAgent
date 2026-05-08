# `note_container.py`

## `mingus.containers.note_container.NoteContainer` · *class*

*No documentation generated.*

### `mingus.containers.note_container.NoteContainer.__init__` · *method*

## Summary:
Initializes the NoteContainer to an empty, well-formed state and populates it with any provided notes, leaving the instance with a sorted, duplicate-free list of Note objects.

## Description:
This constructor is invoked when a new NoteContainer instance is created (i.e., during object instantiation). Typical callers are user code or internal factory code that creates a NoteContainer to hold a collection of notes before further operations (for example, building chords, transposing, or determining consonance). It is executed as the first lifecycle step for a NoteContainer and prepares the internal notes list for all subsequent method calls.

The logic is implemented by delegating to two single-responsibility methods:
- empty(): centralizes how the container is reset to an empty state.
- add_notes(notes): centralizes the logic for normalizing and adding incoming notes (accepting strings, Note objects, iterables, and objects exposing a notes attribute).

Keeping this logic in the constructor (but implemented via empty() and add_notes()) avoids duplicating initialization and normalization code across the class and ensures consistent handling of note inputs.

## Args:
    notes (optional): One of the following (defaults to None):
        - None: produce an empty container.
        - mingus.containers.Note instance: a single Note to add.
        - str: a note name (e.g., "C", "F#") — will be converted to a Note by add_notes/add_note rules.
        - iterable: a sequence of elements as accepted by add_notes:
            * Note instances
            * strings (note names)
            * lists/tuples like [name] or [name, octave] or [name, octave, dynamics]
            * objects exposing a .name attribute (treated as a single Note-like object)
        - object exposing a .notes attribute: treated as another container; its .notes elements are added.
    Notes about defaults and mutability:
        - If notes is None, a new empty list is used internally (avoids shared mutable default).
        - The constructor passes the provided notes through add_notes; it does not deep-copy arbitrary inputs beyond what add_notes/add_note do when constructing Note instances.

## Returns:
    None (constructor). After return, the instance's internal notes collection (self.notes) has been initialized and populated according to add_notes rules.

## Raises:
    UnexpectedObjectError:
        - Propagated from add_note/add_notes when an element without a .name attribute (and not otherwise recognizable as a Note) is encountered.
        - This can occur if the caller passes a plain object that is not a string, not a Note, and does not expose .name (or an iterable containing such items).
    Other exceptions:
        - Any exception raised by Note constructor or methods invoked during add_notes/add_note (e.g., invalid octave or dynamics handling) will propagate.

## State Changes:
    Attributes READ:
        - None directly by __init__ itself. (Note: the called methods empty() and add_notes() may read self.notes as part of their logic.)
    Attributes WRITTEN:
        - self.notes: reset to an empty list by empty(), then populated (appended and sorted) by add_notes()/add_note().

## Constraints:
    Preconditions:
        - None required of the (just-created) object prior to calling __init__ — this is the constructor and should be called on a newly allocated instance only.
        - The notes argument, if present, must be composed of types acceptable to add_notes/add_note (see Args). Passing arbitrary objects may raise UnexpectedObjectError.
    Postconditions:
        - self.notes exists and is a list.
        - If add_notes completed successfully, self.notes contains Note objects (constructed or passed through), with duplicates avoided by add_note and the list sorted.
        - If add_notes raises an exception partway through, self.notes may contain a prefix of successfully added notes (partial initialization) depending on where the error occurred.

## Side Effects:
    - Mutates the new instance's self.notes attribute.
    - May call the Note constructor to create Note objects from strings or shorthand inputs.
    - May call Note instance methods (e.g., transpose) indirectly via add_notes/add_note when normalizing octaves; those calls can further mutate Note instances passed in.
    - No I/O or external service calls are performed by __init__ itself; side effects are limited to object construction/mutation and exception propagation.

### `mingus.containers.note_container.NoteContainer.empty` · *method*

## Summary:
Clears the container by resetting its internal notes storage to a new empty list, leaving the object in an empty state.

## Description:
Known callers and contexts:
- __init__: called during object construction to ensure a fresh, empty notes list before adding any initial notes.
- from_chord_shorthand: invoked at the start of loading notes derived from a chord shorthand to reset prior contents.
- from_interval_shorthand: invoked when creating a pair of notes from an interval to start from an empty container.
- from_progression_shorthand: invoked when building a chord/progression to clear previous notes before populating new ones.
- Typical external usage: callers may call this method to reuse a NoteContainer instance by clearing its contents before repopulating.

Why this is a separate method:
- Centralizes the "clear" behavior so all constructors and factory methods reset the container consistently.
- Intentionally assigns a new list object to self.notes (rather than mutating an existing list), preventing accidental reuse of previously shared list objects and avoiding duplicated clearing logic across methods.

## Args:
- None

## Returns:
- None (implicit). The method performs an in-place mutation of the NoteContainer instance and does not return a value.

## Raises:
- None. This method contains no conditional logic or checks that raise exceptions.

## State Changes:
- Attributes READ:
    - None
- Attributes WRITTEN:
    - self.notes (assigned to a new empty list [])

## Constraints:
- Preconditions:
    - self must be a valid NoteContainer instance (usually true when called as an instance method).
    - No other preconditions on self.notes' prior contents.
- Postconditions:
    - After the call, self.notes is a list() with length 0.
    - The type of self.notes is list; code that expects iterable/list semantics can safely operate on it.
    - Any previous list object formerly bound to self.notes is not modified by this call; references held elsewhere will continue to see the old list contents.

## Side Effects:
- Mutates only the NoteContainer instance by reassigning self.notes.
- No I/O, no network or filesystem access, and no calls to external services.
- Important note about aliasing: because the method assigns a new list object, external references to the previous list (if any code captured self.notes before calling empty) will not observe the cleared state — they will still reference the original list with its prior elements.

### `mingus.containers.note_container.NoteContainer.add_note` · *method*

## Summary:
Adds a single pitch to the container, normalizing string inputs into Note objects, ensuring no duplicates, and keeping the container sorted — mutates the container's notes list.

## Description:
Known callers and contexts:
- NoteContainer.add_notes — processes single or multiple inputs and delegates single-note insertion to this method.
- NoteContainer.__init__ — initializes the container by calling add_notes; therefore add_note is used during construction when initial notes are provided.
- NoteContainer.from_chord_shorthand, from_interval_shorthand, from_progression_shorthand — higher-level factories that build lists of notes (via add_notes) which eventually call add_note for each element.
- Operators and helpers that call add_notes (for example, __add__) will indirectly invoke add_note for each element added.
- External callers may call add_note directly when adding a single note to an existing container.

Why this is a separate method:
- Centralizes input normalization (accepting either a string or a Note-like object), validation (rejecting unexpected object shapes), deduplication, and ordering logic in one place so all callers get consistent behavior without duplicating code.

## Args:
    note (str | object): Either:
        - a string representing the note name (e.g., "C#", "G"), in which case a new Note instance will be constructed; or
        - an object expected to be a Note-like instance exposing at least a .name attribute and comparable behavior (used for equality and ordering checks).
        Allowed values: any six.string_types value or any object with a .name attribute.
    octave (int | None): Optional octave index to use when constructing a Note from a string. If provided and `note` is a string, it is passed verbatim to the Note constructor. If omitted and `note` is a string, the method selects an octave as described in Description edge cases. No explicit range is enforced by this method.
    dynamics (dict | None): Optional mapping used to initialize Note dynamics when constructing a Note from a string. If None, an empty dict is created per-call (dynamics = {}). If supplied, the same object is forwarded to the Note constructor.

## Returns:
    list: The container's internal notes list (self.notes) after the operation.
    - If the note was new (not already present according to membership/equality), the returned list includes the inserted Note and is sorted.
    - If the note was already present, the list is returned unchanged.
    - Always returns the live list object stored on self.notes.

## Raises:
    UnexpectedObjectError: Raised when `note` is neither a string nor a Note-like object with a .name attribute after normalization.
    - Trigger condition: after possible conversion from string to Note, the final `note` value does not have attribute "name" (checked with hasattr(note, "name")).

## State Changes:
    Attributes READ:
        - self.notes: read to determine current length (len(self.notes)) and to inspect the last element's octave (self.notes[-1].octave) when inferring octave for string inputs.
    Attributes WRITTEN:
        - self.notes: may be modified by appending a Note (self.notes.append(note)) and then sorted in-place (self.notes.sort()).
    Notes about mutation:
        - When `note` is a string, a new Note instance is created; existing external objects passed in are not modified by this method.
        - The method mutates the container's notes list in place.

## Constraints:
    Preconditions:
        - self.notes must exist and be a sequence supporting indexing, append(), and sort() (the class initializes it to a list).
        - If passing a non-string `note`, the object must expose a .name attribute; otherwise the method will raise UnexpectedObjectError.
    Postconditions:
        - If the supplied (or constructed) Note was not already present in self.notes (by membership test), it will be added and the list will be sorted.
        - If the supplied Note was already present, the container's notes list remains unchanged.
        - The method returns the container's notes list (self.notes) in either case.

## Behavior details and edge cases:
    - dynamics default: when caller passes None, dynamics is set to a fresh empty dict inside the method (avoids shared-mutable-default pitfalls).
    - String input handling:
        * If note is a string and octave is provided: constructs Note(note, octave, dynamics).
        * If note is a string and octave is None and the container is empty: constructs Note(note, 4, dynamics) — default octave 4.
        * If note is a string and octave is None and the container is non-empty:
            - Constructs a temporary Note(note, last_note.octave) and compares it with the last Note in self.notes using the Note class ordering (the '<' operator).
            - If the temporary Note is strictly less than the last note, the new note will be constructed with octave = last_note.octave + 1 (i.e., the next octave up); otherwise octave = last_note.octave.
            - This logic attempts to keep inserted notes in non-decreasing pitch order relative to the container's last note.
    - Deduplication: a membership test (if note not in self.notes) prevents inserting duplicates. Membership and equality rely on Note.__eq__.

## Side Effects:
    - No I/O, network, or filesystem operations are performed.
    - No external services are called.
    - The only side effect is mutation of the container's internal notes list (self.notes) and creation of a Note instance when the input is a string.

### `mingus.containers.note_container.NoteContainer.add_notes` · *method*

## Summary:
Adds one or many notes to the container by normalizing several input shapes into calls to the single-note insertion routine, mutating the container's internal notes list and returning it.

## Description:
This method accepts multiple input shapes and delegates actual insertion/normalization work to the container's add_note method. It is commonly invoked from:
- __init__ to populate a newly constructed container,
- from_chord_shorthand, from_interval_shorthand, from_progression_shorthand when building a container from chord/interval/progression helpers,
- __add__ when using the + operator to merge notes into the container.

Centralizing the normalization and iteration logic in add_notes avoids duplicating the code that handles the various acceptable input shapes (container-like objects, single Note-like objects, strings, or iterables of parameters).

## Args:
    notes (various):
        Allowed formats and how they are handled:
        - An object with a .notes attribute (e.g., another NoteContainer or similar): the method iterates over notes.notes and calls add_note(x) for each element.
        - An object with a .name attribute (e.g., a single Note instance): treated as a single note; add_note(notes) is called.
        - A string (six.string_types): treated as a single note name; add_note(notes) is called.
        - Any iterable (other than the above): iterated element-by-element. For each element x:
            * If x is a list and len(x) != 1:
                - If len(x) == 2: call add_note(x[0], x[1])  (interpreted as note, octave)
                - If len(x) >= 3: call add_note(x[0], x[1], x[2])  (interpreted as note, octave, dynamics). Any elements beyond the first three are ignored.
            * Otherwise: call add_note(x)
        Notes:
            - The code specifically checks isinstance(x, list) for the "tuple-like" unpacking behavior; other sequence types (tuple, deque, etc.) are not unpacked and are passed directly to add_note.
            - A list of length 1 will not be unpacked; it will be passed as-is to add_note and will typically cause an error (see Raises).

## Returns:
    list: The container's internal self.notes list after processing. This is the actual internal list object (not a defensive copy). If no insertions occur, the same list is returned (may be empty).

## Raises:
    UnexpectedObjectError:
        - Raised indirectly by add_note when an argument cannot be resolved to a Note object (i.e., the value passed to add_note is neither a string nor has a .name attribute).
        - Typical triggering examples:
            * Passing an element that is a list of length 1 (e.g., ['C']) inside an iterable: add_notes will call add_note(['C']) which lacks .name and is not a string, so add_note raises UnexpectedObjectError.
            * Passing any element type that add_note cannot coerce into a Note (e.g., arbitrary dicts, plain lists not matching the unpacking rules).

## State Changes:
    Attributes READ:
        - self.notes (read indirectly by add_note when add_note needs the previous note to determine a default octave for string inputs)
    Attributes WRITTEN:
        - self.notes (new Note objects may be appended by add_note; add_note also sorts and prevents duplicates)

## Constraints:
    Preconditions:
        - self must expose a mutable self.notes list and implement add_note(note, octave=None, dynamics=None).
        - The caller should not pass raw, single-character iterables intended to be single notes (strings are handled specially; arbitrary iterables will be iterated).
    Postconditions:
        - Every element successfully processed by add_note will be present in self.notes.
        - self.notes will be sorted after insertions (sorting is performed by add_note).
        - Duplicate Notes (by equality) are not duplicated: add_note only appends if the note is not already present.
        - The method returns the (possibly updated) self.notes list.

## Side Effects:
    - Mutates the container's self.notes by appending new Note objects and potentially sorting the list.
    - May construct new Note objects via add_note when given string inputs or when add_note determines a default octave.
    - No I/O or external network calls are performed.
    - UnexpectedObjectError may propagate from add_note to the caller if an input element cannot be converted to a Note.

### `mingus.containers.note_container.NoteContainer.from_chord` · *method*

## Summary:
Populate this NoteContainer by delegating to the chord-shorthand parser: clear the container and add the notes produced from the provided chord shorthand, then return self.

## Description:
This method is a thin public alias that forwards to from_chord_shorthand(shorthand). It exists to provide a concise, backward-compatible API entry point for populating a NoteContainer from a chord shorthand (for example, a typical shorthand string like "Cmaj7").

Behavioral role:
- Delegates the actual work to from_chord_shorthand, which clears the container (calls self.empty()), obtains a sequence of notes from mingus.core.chords.from_shorthand(shorthand), and then repopulates the container via self.add_notes(...).
- The method itself performs no parsing, validation, or mutation beyond delegation and return of the delegated result.

Known callers / invocation context:
- User code or higher-level utilities that need to initialize or replace a NoteContainer's contents from a chord text representation.
- No other internal callers are required; it is primarily an ergonomic alias for from_chord_shorthand.
- Typical lifecycle: invoked when a container should reflect the notes of a chord described by a shorthand string prior to operations like transposition, analysis, or rendering.

Why this is a separate method:
- Provides a stable, short API name while centralizing the implementation in from_chord_shorthand to avoid duplication and simplify maintenance.

## Args:
    shorthand (str or any accepted by mingus.core.chords.from_shorthand):
        The chord-shorthand identifier (commonly a string such as "C", "Dm7", "G7sus4", "Cmaj7") that the chords module can parse.
        The method does not validate the value; it is passed verbatim to mingus.core.chords.from_shorthand.

## Returns:
    NoteContainer (self):
        Returns the same NoteContainer instance after it has been emptied and (if parsing produced notes) populated with Note-like objects.
        If the chord parser returns an empty sequence, the container will be left empty and self is still returned.

## Raises:
    UnexpectedObjectError:
        May be raised indirectly by add_note/add_notes if the sequence returned by chords.from_shorthand contains objects that do not expose a 'name' attribute (i.e., are not Note-like).
    Any exceptions from mingus.core.chords.from_shorthand:
        Errors raised during parsing (invalid shorthand, unexpected input types) propagate through this method unchanged.

## State Changes:
    Attributes READ:
        - None read directly by this method. (The delegated implementation reads/writes self.notes.)
    Attributes WRITTEN:
        - self.notes is modified (cleared via self.empty() and then repopulated via self.add_notes(...)) as a result of calling the delegated implementation.

## Constraints:
    Preconditions:
        - self must be a valid NoteContainer instance.
        - shorthand must be acceptable input for mingus.core.chords.from_shorthand; calling with None or an unsupported type may raise from the chords module.
    Postconditions:
        - After the call, self.notes contains the notes corresponding to shorthand as returned by chords.from_shorthand, or is empty if that parser returned an empty sequence.
        - The method returns self to allow fluent method chaining.

## Side Effects:
    - Mutates this NoteContainer's notes collection.
    - Calls mingus.core.chords.from_shorthand(shorthand) (no external I/O in this method itself).
    - May indirectly trigger sorting and validation behavior in add_note/add_notes (including raising UnexpectedObjectError).

## Example usage (illustrative):
    Create a NoteContainer and call from_chord with a typical chord shorthand — after the call the container will hold the notes corresponding to that chord (or be empty if parsing produced no notes).

### `mingus.containers.note_container.NoteContainer.from_chord_shorthand` · *method*

## Summary:
Populate the container with Note objects derived from a chord shorthand (or list of shorthands), replacing any existing contents, and return the container for chaining.

## Description:
Known callers and contexts:
- NoteContainer.from_chord: a thin alias that forwards to this method when creating a container from chord shorthand.
- Typical usage: called when a NoteContainer instance needs to be initialized or re-used to represent the pitch content of a chord described by a shorthand string (e.g., "Cmaj7", "Am", "G/B") or a list of such shorthands.
- Lifecycle stage: acts as a factory-style initializer or reinitializer — it is invoked at the start of a pipeline step that converts chord shorthand notation into concrete Note instances stored in the container.

Why this is a separate method:
- Encapsulates the two-step flow required to build the container from shorthand: clearing prior state and delegating parsing to the chords helper, then normalizing and inserting results via add_notes.
- Keeps parsing concerns (chords.from_shorthand) separate from container mutation and normalization (add_notes), improving reuse and testability.

## Args:
    shorthand (str or list):
        - A chord shorthand string (for example "C", "Cm", "Cmaj7", "D/F#") or a list of shorthand strings.
        - The argument is passed directly to mingus.core.chords.from_shorthand, which accepts either a single shorthand string or a list and will return a list (or nested lists for some slash/compound forms).
        - No default value; must be provided.

## Returns:
    NoteContainer:
        - Returns the same NoteContainer instance (self) after mutation to allow call-chaining.
        - After successful return, self.notes contains the Note objects (or remains empty) corresponding to the chord shorthand parsed.

## Raises:
    - Any exception raised by mingus.core.chords.from_shorthand:
        * NoteFormatError: when the shorthand contains an unrecognised/invalid note token.
        * FormatError: when the shorthand is not a known/parseable chord form.
        (These exception types are raised by the chords parser and will propagate through this method.)
    - UnexpectedObjectError:
        * May be raised indirectly by self.add_notes when chords.from_shorthand returns items that cannot be coerced to Note objects (for example, malformed nested sequences that add_notes cannot normalize). This occurs when add_note receives an object that is neither a string nor has a .name attribute.

## State Changes:
    Attributes READ:
        - self.notes (read by add_notes / add_note when determining octave defaults for string inputs)
    Attributes WRITTEN:
        - self.notes (assigned to a new empty list by self.empty(), then appended/modified by self.add_notes)

## Constraints:
    Preconditions:
        - self must be a valid NoteContainer instance with working empty() and add_notes(...) methods.
        - shorthand must be acceptable to mingus.core.chords.from_shorthand (a valid chord shorthand string or list); otherwise the chords parser will raise an error.
    Postconditions:
        - On success, self.notes is populated with Note objects representing the chord described by shorthand, sorted and deduplicated according to add_note/add_notes semantics.
        - If the chord shorthand denotes "no chord" (for example "NC" / "N.C." handled by chords.from_shorthand), chords.from_shorthand returns an empty list and self.notes remains empty.
        - If parsing fails, an exception from chords.from_shorthand or add_notes propagates and self.notes will already have been reset to an empty list due to the initial call to self.empty().

## Side Effects:
    - Mutates only the NoteContainer instance by clearing and then populating self.notes.
    - No I/O, network, or filesystem activity.
    - May construct new Note objects (via add_notes / add_note) when chord parser returns note names.
    - Exceptions from the chord parser or normalization step propagate to the caller; the container will be left cleared if an exception is raised because empty() is called before parsing/insertion.

### `mingus.containers.note_container.NoteContainer.from_interval` · *method*

## Summary:
Delegate that resets the container and populates it with a two-note interval: the provided start note and a second note produced by transposing the start note by the given interval shorthand, returning the same container instance.

## Description:
Known callers and context:
- Public API used by client code that needs a NoteContainer representing a simple interval (two notes). Typical usage is when constructing intervals for analysis, playback, or for building chords/progressions in a higher-level pipeline step.
- This method is invoked at the point in a workflow where a consumer has a single start note (string or Note) and an interval shorthand (e.g., "m3", "M3", "P5") and wants a NoteContainer containing the start note and the transposed note.
- It is a convenience alias that forwards to the implementation in from_interval_shorthand, matching the class' other pairings (from_chord → from_chord_shorthand, from_progression → from_progression_shorthand), providing a stable, discoverable API name.

Why this logic is a separate method:
- Keeps a concise public API name (from_interval) while centralizing the actual behavior, parsing, and normalization in from_interval_shorthand.
- Encourages consistency with similar factory methods in the class and avoids duplicating initialization/normalization code.

## Args:
    startnote (str | mingus.containers.note.Note):
        - If a string: a note name like "C", "F#", "Bb" — will be converted to a Note instance using the Note constructor.
        - If a Note instance: the Note to use as the interval's root.
        - If another object is passed, it must expose the attributes required by from_interval_shorthand (see Preconditions) or errors will occur.
    shorthand (str):
        - An interval shorthand accepted by Note.transpose (examples: "m3", "M3", "P5", "P1").
        - The literal expected format and accepted values are those supported by the project's interval/transpose machinery.
    up (bool, optional):
        - If True (default), transpose upward by the interval.
        - If False, transpose downward.

## Returns:
    mingus.containers.note_container.NoteContainer
    - Returns self (the same NoteContainer instance) after clearing and populating it.
    - On successful return, self.notes will contain the start note and the transposed note (subject to duplicate-elimination rules in add_note).
    - There is no boolean/None special-case return; the method always returns the container instance on the successful execution path.

## Raises:
    AttributeError:
        - Triggered if startnote is not a string and does not provide required attributes (name, octave, dynamics) that from_interval_shorthand attempts to access when cloning and transposing the note. For example, accessing startnote.name will raise AttributeError if that attribute is missing.
    UnexpectedObjectError:
        - Raised by the add_note/add_notes pathway if an object being added does not expose a .name attribute and therefore cannot be treated as a Note-like object. This occurs when add_note is called with an object that is neither a string nor a Note and lacks .name. The exact message originates from add_note and follows the class' UnexpectedObjectError usage.

## State Changes:
Attributes READ:
    - None directly on self by this delegator; the implementation it forwards to will read properties of the provided startnote (name, octave, dynamics) when constructing the transposed note.
Attributes WRITTEN:
    - self.notes: the container is cleared (empty()) and then repopulated via add_notes; after the call self.notes will reflect the newly built interval (usually two Note objects, unless duplicate-removal rules reduce it).

## Constraints:
Preconditions:
    - The caller should provide either:
        * a string representing a note name, or
        * a Note instance from the project's Note class.
    - If passing a custom object as startnote (not a string or Note), it must expose at least the attributes name, octave, and dynamics, because the underlying implementation clones those fields to create a transposed Note. Failing to meet this will cause AttributeError.
    - shorthand must be a valid interval shorthand recognized by the project's Note.transpose implementation.

Postconditions:
    - self.notes is non-null and has been replaced with the interval's notes.
    - The container contains the start note (converted to a Note if a string was passed) and a second Note equal to the start note transposed by shorthand in the requested direction.
    - If the transposed note compares equal to the start note under the container's equality semantics, only one entry may remain due to the add_note duplicate-avoidance check.

## Side Effects:
    - No I/O, network, or filesystem operations.
    - Mutates the container's internal state (self.notes).
    - May construct new Note objects via the Note constructor and call Note.transpose on the cloned note.
    - May raise exceptions originating from Note construction or transposition (e.g., invalid octave or invalid interval shorthand) which propagate to the caller.

### `mingus.containers.note_container.NoteContainer.from_interval_shorthand` · *method*

## Summary:
Constructs a two-note interval inside the container by clearing the container, ensuring the start note is a Note, creating a copy transposed by the given interval shorthand, adding both notes to the container, and returning the container instance.

## Description:
- Known callers:
    - No direct callers were discovered in the provided code snapshot. This method is a public helper on the NoteContainer intended for creating a simple two-note interval (a dyad) from a starting note and an interval shorthand.
- Typical lifecycle / when called:
    - Invoked when a caller wants to produce a two-note interval inside an existing NoteContainer, replacing any previous contents. It is used at the step where a container should be populated with a start note and its interval companion.
- Reason this logic is its own method:
    - It encapsulates the common sequence: clear the container, normalize the start note (string → Note), create a transposed copy, and add both notes. Grouping these steps into a method keeps calling code concise and reuses container manipulation helpers (empty, add_notes).

## Args:
    startnote (mingus.containers.note.Note or str):
        - If a string, the method constructs a Note from it (Note(startnote)).
        - If a Note instance, it is used directly (the method does not mutate this Note).
        - If another type, behavior depends on the Note constructor and may raise an error from that constructor.
    shorthand (any):
        - Passed directly to Note.transpose on a newly-created Note copy. The allowed values are whatever the Note.transpose implementation accepts (commonly interval shorthand or a representation understood by transpose).
    up (bool, default True):
        - Direction passed to Note.transpose; True generally indicates transposition upwards, False downwards.

## Returns:
    self (NoteContainer):
        - Returns the same NoteContainer instance after replacing its contents with two notes.
        - After return, the container contains exactly two notes in order: the normalized start note and the transposed copy.

## Raises:
    - This method does not raise exceptions explicitly.
    - It may propagate exceptions raised by:
        * Note constructor (when converting a string or given an invalid startnote)
        * Note.transpose (if the shorthand or up value is invalid for transpose)
        These propagated exceptions depend on the underlying Note implementation.

## State Changes:
    Attributes READ:
        - None directly read from self via attribute access in this method (the method calls container helpers instead).
    Attributes WRITTEN:
        - The container's internal note collection is modified:
            * Cleared via self.empty()
            * Populated with two Note instances via self.add_notes([startnote, n])
        - Post-call, the container's contents are exactly the two notes added.

## Constraints:
    Preconditions:
        - The caller must provide a startnote that is either a Note instance or a string that the Note constructor can accept.
        - The shorthand must be a value accepted by Note.transpose; otherwise, transpose may raise.
        - The container must be in a usable state where self.empty() and self.add_notes(...) succeed (no external invariants are required by this method).
    Postconditions:
        - self contains two Note instances:
            1. The first is the normalized start note (a Note object; if a string was passed, it has been converted to a Note instance).
            2. The second is a newly-created Note copied from the start note and transposed by (shorthand, up).
        - The original startnote object is not modified by this method (the transposition is applied to a copy).

## Side Effects:
    - Mutates the container by clearing and then setting its contents to the two notes described above.
    - Creates a new Note instance (the transposed copy) and calls its transpose method.
    - No I/O, logging, or network activity is performed by this method.

### `mingus.containers.note_container.NoteContainer.from_progression` · *method*

## Summary:
Forwards the provided progression shorthand and key to the container's from_progression_shorthand implementation and returns its result; does not itself alter any attributes.

## Description:
This method exists as a lightweight alias/wrapper that delegates to the instance method from_progression_shorthand(shorthand, key). It centralizes a stable public API entry point that forwards progression parsing/creation work to the more specific from_progression_shorthand implementation.

Known callers:
- No direct callers were discovered within the inspected source during documentation generation. Typically this method is called by client code or higher-level utilities that want to populate or build a NoteContainer from a progression shorthand (the callsite is the stage where a progression string/representation is converted into notes/chords within a container).

Why this method is separate:
- It provides a simple, stable public API surface (a concise method name) while allowing the real parsing/creation logic to live in from_progression_shorthand. This separation helps keep API compatibility and isolates parsing details.

## Args:
    shorthand (any): A progression shorthand representation. The exact accepted types and structure are determined by from_progression_shorthand; this method forwards the value unchanged.
    key (str): Root key to use when interpreting the progression. Defaults to "C". Must be a string representing the tonic (e.g., "C", "G#", "Fm" etc.), but validation and accepted formats are handled by from_progression_shorthand.

## Returns:
    any: Returns whatever from_progression_shorthand returns. This wrapper does not transform the return value. Callers should consult from_progression_shorthand documentation for the precise return type and meaning.

## Raises:
    Any exception raised by from_progression_shorthand will be propagated unchanged by this method. This wrapper itself does not raise new exception types.

## State Changes:
    Attributes READ:
        - None directly read by this method (it merely calls another method on self).
    Attributes WRITTEN:
        - None directly written by this method. Any modifications to self are performed by from_progression_shorthand, not by this wrapper.

## Constraints:
    Preconditions:
        - self must be a properly-initialized NoteContainer instance with a valid from_progression_shorthand method.
        - shorthand must be in a format accepted by from_progression_shorthand.
        - key should be a string; invalid key formats will be handled (or rejected) by from_progression_shorthand.

    Postconditions:
        - This method guarantees that it returns the exact result of calling from_progression_shorthand(shorthand, key).
        - No additional side-effect or attribute change is performed by this wrapper itself. Any side-effects (mutations to self or other objects) are solely the responsibility of from_progression_shorthand.

## Side Effects:
    - No I/O or external service calls are performed by this wrapper itself.
    - It may cause side effects indirectly because it invokes from_progression_shorthand; those side effects (mutating self, creating Note objects, etc.) are delegated and not described here.

### `mingus.containers.note_container.NoteContainer.from_progression_shorthand` · *method*

## Summary:
Populate the container with Note objects representing the first chord realized from a Roman-numeral progression shorthand in the specified key. The container is cleared first; on success the method returns the container, and if the shorthand cannot be resolved to any chords it returns False.

## Description:
- Known callers and context:
    - NoteContainer.from_progression is a direct alias that calls this method. Callers use it when converting Roman-numeral progression shorthand (e.g., "V", "bII7", ["I","V","vi"]) into concrete chord tones and loading those tones into a NoteContainer as an initialization/population step.
    - Typical pipeline stage: translation/realization of symbolic progression notation into concrete pitch content prior to further processing (transposition, rendering, harmony analysis).

- Why this is a separate method:
    - Responsibility is limited to mutating the container from a progression shorthand; parsing and resolution of progression tokens is delegated to mingus.core.progressions.to_chords. Separating these concerns keeps progression parsing, error handling, and container population modular and reusable.

## Args:
    shorthand (str or iterable of str)
        - A Roman-numeral progression token (e.g., "V", "bII7", "#ivmaj7") or an iterable of such tokens.
        - Must be acceptable to mingus.core.progressions.to_chords (prefer Python str for single-token usage).
    key (str, optional)
        - The key in which to realize the progression (default "C").
        - Must be a valid key string for the chord factories used by progressions.to_chords (typical values: "C", "G#", "F", etc.).

## Returns:
    - NoteContainer (self): when progressions.to_chords(shorthand, key) returns a non-empty list. The container will contain Note objects created/added from the first chord in the returned list (chords[0]). Even if chords[0] is an empty chord list, the method returns self (with an empty container).
    - False: if progressions.to_chords(shorthand, key) returns an empty list (indicating the shorthand could not be resolved at all). In this case the container has been cleared and remains empty.
    - Note: the method therefore returns either the mutated NoteContainer instance or boolean False; callers should check truthiness or explicitly compare to False if distinguishing failure is required.

## Raises:
    - Propagated exceptions from mingus.core.progressions.to_chords:
        - TypeError / AttributeError: if shorthand is not a string/iterable acceptable to parsing functions.
        - KeyError: if a parsed roman-numeral or suffix lookup fails in the chords mappings.
        - IndexError: may propagate from augment/diminish operations inside to_chords on malformed note strings.
        - Any other exceptions raised by the chord factory or shorthand callables.
    - UnexpectedObjectError:
        - Raised by self.add_notes / self.add_note if an element returned by progressions.to_chords is not an acceptable Note-like object (add_note expects either a string or an object with a .name attribute).
    - Note: because the container is emptied before calling to_chords, any exception raised by to_chords or subsequent add_notes will leave the container in the cleared/partially-updated state and will propagate to the caller.

## State Changes:
- Attributes READ:
    - self.notes (read indirectly by add_note when inferring octave for string inputs). Because self.empty() is called first, the read will observe an empty list in the common case where no prior notes existed.
- Attributes WRITTEN:
    - self.notes — set to [] by self.empty(), then potentially appended to by self.add_notes(notes) according to the first chord produced.

## Constraints:
- Preconditions:
    - shorthand must be compatible with mingus.core.progressions.to_chords (prefer str or list/tuple of str).
    - key must be a valid key string for the chord factories in the chords module.
    - Callers should expect that only the first chord produced by to_chords is used; if multiple chords are returned, later chords are ignored by this method.
- Postconditions:
    - If to_chords returns []:
        - self.notes is empty and the method returns False.
    - If to_chords returns a non-empty list:
        - self.notes contains Note objects corresponding to the first chord (chords[0]), which may be an empty list (in that case self.notes remains empty) and the method returns self.
    - If an exception is raised during progression resolution or addition, the exception propagates and the container will be either empty (if the exception occurred before adding) or partially populated (if the exception occurred during add_notes).

## Side Effects:
- Mutates the NoteContainer instance (self.notes).
- May allocate Note objects via add_note.
- No file I/O, network, or global state changes are performed directly by this method.
- Exceptions and side-effects from the chord factory or shorthand functions called inside progressions.to_chords (if any) may occur and propagate.

## Example:
- Successful population:
    - Call: from_progression_shorthand("V", key="C")
    - Behavior: clears the container, resolves "V" in C to [["G","B","D"]], adds "G","B","D" as Note objects, returns self with these notes.
- Unresolvable shorthand:
    - Call: from_progression_shorthand("INVALID", key="C")
    - Behavior: clears the container, progressions.to_chords returns [], method returns False and container remains empty.

### `mingus.containers.note_container.NoteContainer._consonance_test` · *method*

## Summary:
Evaluates every unordered distinct pair of notes in the container with a provided test function and returns True if every pair passes; returns False on the first failing pair. Performs the checks on a snapshot of the container and does not modify the container or its Note objects.

## Description:
- Known callers:
    - is_consonant(include_fourths=True)
    - is_perfect_consonant(include_fourths=True)
    - is_imperfect_consonant()
  These public methods delegate their pairwise checks to this helper when determining whether the NoteContainer's current note set is consonant under different definitions.
- Invocation context:
    - Used during note-set analysis steps whenever the caller needs a boolean verdict about pairwise interval relationships among all notes currently held by the NoteContainer (for example, after constructing, adding, removing, or transposing notes).
- Reason for separate method:
    - Consolidates the common O(n^2) traversal and short-circuiting behavior so multiple public predicate methods can reuse the same logic. It also centralizes the conditional behavior of forwarding an extra parameter to the test function.

## Args:
    testfunc (callable): A function that evaluates a pair of note names. It must accept either:
        - two positional arguments (name1: str, name2: str) and return a truthy value for a passing pair, or
        - three positional arguments (name1: str, name2: str, param) if a non-None param is supplied.
      Note: testfunc is invoked with the .name attribute of Note instances (plain strings like "C", "G#", "Bb"), not with Note objects.
    param (optional, any): If non-None, forwarded as the third positional argument to testfunc. Commonly a boolean flag (e.g., include_fourths) but may be any value the testfunc expects. Default: None

## Returns:
    bool: 
    - True if testfunc returns a truthy value for every unordered distinct pair of notes.
    - False immediately when any single pair returns a falsy value.
    - For 0 or 1 notes in the container, returns True (vacuous truth).
    - The check is short-circuited: the method stops and returns False on the first failing pair.

## Raises:
    - Any exception raised by testfunc is propagated unchanged.
    - Typical failure modes:
        * TypeError if testfunc does not accept the number of arguments provided (e.g., param is passed when testfunc only accepts two args).
        * Any other exception raised from within testfunc (e.g., ValueError) will bubble up to the caller.
    - This method itself does not raise new, custom exceptions for normal operation.

## State Changes:
    Attributes READ:
        - self.notes: read once to create a local snapshot list of Note objects for pairwise iteration.
    Attributes WRITTEN:
        - None. The method does not mutate self.notes or any Note objects.

## Constraints:
    Preconditions:
        - self.notes must be an iterable of objects that expose a .name attribute containing a pitch name string.
        - testfunc must be callable and accept either two or three positional parameters depending on whether param is None.
    Postconditions:
        - self.notes remains unchanged.
        - The return value accurately reflects whether all unordered distinct pairs passed testfunc under the described calling convention.

## Behavior details:
    - Pairing semantics: each unordered distinct pair of notes (A,B) is tested exactly once. The implementation iterates using a sliding-window approach (testing note 0 with each subsequent note, then note 1 with each subsequent note, etc.) to avoid duplicate checks.
    - Snapshot semantics: the method constructs a local list from self.notes at the start; subsequent mutations to self.notes by other threads or callbacks will not affect the current evaluation.
    - Performance: O(n^2) time, O(n) extra space for the local snapshot where n is the number of notes.

## Examples (prose):
    - Typical usage: called with an interval-testing function and an optional boolean flag, e.g., a caller may pass an intervals.is_consonant function along with include_fourths=True so the internal invocation will be equivalent to calling intervals.is_consonant(name1, name2, True) for each pair of note names.
    - Edge-case behavior: when the container has a single note, callers receive True; when testfunc raises (for example, because an unexpected param type is supplied), that exception propagates to the caller.

## Side Effects:
    - None performed directly by this method: no I/O or external service calls.
    - Any side effects originate from testfunc itself if it mutates global state or performs I/O; since testfunc is called with plain strings, typical interval-test functions do not mutate Note objects.

### `mingus.containers.note_container.NoteContainer.is_consonant` · *method*

## Summary:
Returns whether every pairwise interval between notes in the container is musically consonant, using the intervals.is_consonant predicate and the supplied include_fourths flag.

## Description:
Known callers and calling context:
- Internal: NoteContainer.is_dissonant calls this method (negating its result) to decide whether a container is dissonant.
- Internal siblings: Other container-level consonance checks (is_perfect_consonant, is_imperfect_consonant) use the shared _consonance_test helper rather than calling this method directly.
- External: Typically invoked by any higher-level harmony or voice-leading analysis that needs to know if all voices/notes in a NoteContainer form consonant intervals (for example, chord validation, harmonic analysis pipelines, or user code inspecting a chord/progression).

Lifecycle / pipeline stage:
- Used during static analysis of a set of notes (a chord, a two-voice interval, or an extracted set from a progression/chord). It is a pure predicate used when deciding whether a set of notes is harmonically consonant.

Why this is a separate method:
- Encapsulates the container-level question "are these notes pairwise consonant?" so callers do not need to manually iterate and combine the low-level intervals.is_consonant predicate.
- Delegates pairwise iteration to a shared helper (_consonance_test), keeping the high-level intent readable and enabling reuse for other consonance variants.

## Args:
    include_fourths (bool, optional): Controls whether perfect fourths are counted as consonant by the underlying intervals.is_consonant predicate.
        - Default: True
        - Accepts any value coercible to boolean; truthy values enable inclusion of perfect fourths.

## Returns:
    bool:
        - True if every unordered pair of distinct notes in the container yields True from intervals.is_consonant(first.name, second.name, include_fourths).
        - False if any pair yields False.
        - Edge cases:
            * Empty container (no notes): returns True (vacuously consonant).
            * Single-note container: returns True (no distinct pairs to violate consonance).
        - Behavior with duplicates: duplicate entries are treated as separate voices and are checked; identical note names will typically produce a unison (consonant).

## Raises:
    - This method does not raise its own exceptions but may propagate exceptions from:
        * AttributeError: if elements of self.notes lack a .name attribute.
        * ValueError, TypeError, or other exceptions produced by intervals.is_consonant (which in turn delegates to note-parsing/measurement utilities). These occur when note name strings are malformed or of unacceptable types.

## State Changes:
    Attributes READ:
        - self.notes (the method reads each element and accesses .name on each Note)
    Attributes WRITTEN:
        - None (never mutates self.notes or any Note objects)

## Constraints:
    Preconditions:
        - Each element in self.notes must be an object exposing .name (a pitch name string acceptable to the core interval utilities).
        - include_fourths is expected to be used as a boolean flag (truthy/falsy values are accepted).
    Postconditions:
        - self and its Note objects are unchanged.
        - The return boolean correctly reflects the pairwise consonance status per intervals.is_consonant with include_fourths applied.

## Side Effects:
    - None intrinsic: no I/O, no external service calls.
    - Any side effects originate only from side effects (if any) of the underlying intervals.is_consonant call or note-name parsing utilities (typically there are none).

## Additional notes:
    - Complexity: Performs an O(n^2) pairwise check across the notes list (checks all unordered distinct pairs).
    - Implementation detail relevant to callers: comparison uses the note.name strings (not full Note objects or octave information), so octave distinctions are not part of the arguments passed to intervals.is_consonant here — the underlying intervals.is_consonant interprets the two name strings according to its own rules (which measure ascending interval within a single octave).

### `mingus.containers.note_container.NoteContainer.is_perfect_consonant` · *method*

## Summary:
Returns True when every pair of notes in this container forms a perfect consonance (unison/octave, perfect fifth, and optionally perfect fourth); otherwise returns False. Does not modify the container.

## Description:
This method tests pairwise consonance for all notes stored in the container by delegating to the shared helper _consonance_test and the musical predicate intervals.is_perfect_consonant. It forwards the include_fourths flag to the interval predicate.

Known callers and typical usage context:
- No direct callers were discovered in the provided code snapshot. Conceptually, this method is used during harmonic analysis or validation steps where a developer needs to know whether a set of pitches is entirely composed of perfect consonant intervals (for example, when validating doubled perfects or checking voice-leading constraints).
- Typical lifecycle stage: invoked on a populated NoteContainer after notes have been added/constructed (e.g., after from_chord_shorthand, add_notes, or manual construction) to classify the harmonic quality of that set.

Why this is a separate method:
- Encapsulates a common predicate (are all pairs perfect consonances?) behind a descriptive name, improving readability at call sites.
- Reuses the generic pairwise testing machinery in _consonance_test and the interval-specific logic in intervals.is_perfect_consonant, avoiding duplicated pairwise loops and interval comparisons across the codebase.
- Matches the public family of related predicates (is_consonant, is_imperfect_consonant, is_dissonant) for a consistent API on NoteContainer.

## Args:
    include_fourths (bool, optional): Whether to treat the perfect fourth (ascending interval of 5 semitones) as a perfect consonance.
        - Default: True.
        - Accepted values: any object coercible to a Python boolean; typical use passes True or False.

## Returns:
    bool:
        - True if every unordered pair of notes in the container (every combination of two distinct notes) satisfies intervals.is_perfect_consonant when called with the forwarded include_fourths flag.
        - False if any pair fails the perfect-consonance test.
        - Edge cases:
            * Empty container (no notes): returns True.
            * Single-note container: returns True (no distinct pairs violate the predicate).

## Raises:
    - Propagates any exception raised by intervals.is_perfect_consonant or its dependencies (for example, errors originating from measure() / notes.note_to_int when interval computation receives an invalid pitch representation). Typical propagated exceptions include ValueError, TypeError, or other format-related errors from lower-level utilities.
    - AttributeError will occur if any element in self.notes lacks the expected .name attribute (for example, if the container was mutated directly with non-Note objects). Normally add_note prevents this by raising UnexpectedObjectError on insertion, but direct mutation of self.notes can still trigger AttributeError here.

## State Changes:
    Attributes READ:
        - self.notes (iterates over its items and accesses each item's .name)
    Attributes WRITTEN:
        - None (this method does not modify any attribute of self)

## Constraints:
    Preconditions:
        - self.notes should contain objects exposing a .name attribute (typically mingus.containers.Note instances).
        - The note name strings returned by .name must be acceptable inputs to intervals.is_perfect_consonant (which ultimately relies on measure() / notes.note_to_int).
        - include_fourths should be used as a boolean flag.

    Postconditions:
        - No mutation of self or its contained Note objects is performed.
        - The return value accurately indicates whether all unordered note-pairs are perfect consonances under the include_fourths rule.

## Side Effects:
    - None intrinsic: no I/O, no network/filesystem access, and no mutation of external state.
    - Any side effect arises only from side effects in intervals.is_perfect_consonant (or the utilities it calls) — in typical implementations those utilities are pure and thus no side effects occur.

## Complexity:
    - Time: O(n^2) pairwise checks where n is len(self.notes), because every distinct pair is tested.
    - Space: O(n) for a shallow list copy used by _consonance_test.

## Implementation notes / pitfalls:
    - Because the method relies on .name of each note, calling it on a container that was directly assigned arbitrary objects to self.notes may raise AttributeError.
    - The include_fourths flag is forwarded directly to the interval predicate; to exclude the perfect fourth from the definition of "perfect consonance" pass include_fourths=False.

### `mingus.containers.note_container.NoteContainer.is_imperfect_consonant` · *method*

## Summary:
Determine whether every unordered distinct pair of notes in the container forms an imperfect consonance (a minor/major third or minor/major sixth); returns True only if all pairs satisfy that condition.

## Description:
- What this method does:
    - Delegates the pairwise checking work to the internal helper _consonance_test, supplying intervals.is_imperfect_consonant as the predicate. No additional parameters are passed.
    - The predicate is invoked with the .name attribute of each Note (plain pitch names like "C", "G#", "Bb"); octave information is not forwarded and therefore does not affect the test.

- Known callers and invocation context:
    - This is a public predicate on NoteContainer intended for client code that needs to validate the harmonic relationship among notes (for example: harmony analysis, counterpoint checks, or test assertions after constructing/transposing a container).
    - There are no internal callers in the same module that further wrap or change this behavior; other container predicates (is_consonant, is_perfect_consonant) use the same shared helper but different interval predicates.

- Why this logic is a separate method:
    - Provides a small, descriptive public API surface for asking the specific musical question "are these notes pairwise imperfect consonances?" while reusing the generic O(n^2) pairwise traversal implemented in _consonance_test. This keeps client code expressive and avoids repeating traversal logic.

## Args:
    None

## Returns:
    bool
        - True if intervals.is_imperfect_consonant(name1, name2) returns True for every unordered distinct pair of notes in self.notes.
        - False if any pair returns False (short-circuits on the first failing pair).
        - For containers with 0 or 1 notes the method returns True (vacuous truth).

## Raises:
    - Propagates any exception raised by _consonance_test or the predicate intervals.is_imperfect_consonant, including but not limited to:
        * Parsing/format errors coming from the underlying note parsing used by the intervals module (e.g., invalid note name strings).
        * TypeError if intervals.is_imperfect_consonant rejects the argument types supplied.
    - The method itself does not raise new exceptions beyond what the delegated calls may raise.

## State Changes:
    Attributes READ:
        - self.notes (a snapshot is taken by the helper and each Note object's .name is read)
    Attributes WRITTEN:
        - None. The method does not mutate self or Note objects.

## Constraints:
    Preconditions:
        - Each element in self.notes must expose a .name attribute that yields a pitch name string acceptable to the intervals.is_imperfect_consonant helper.
    Postconditions:
        - self.notes remains unchanged.
        - The returned boolean correctly reflects whether all unordered distinct pairs of note names satisfy the imperfect-consonance predicate.

## Side Effects:
    - None performed directly by this method. Any side effects would originate from exceptions or side effects in intervals.is_imperfect_consonant or lower-level parsing helpers (typically there are no side effects).

## Behavior and edge cases:
    - Octave information is ignored because only Note.name is passed to the predicate; therefore the check tests pitch class relationships (ascending interval measured modulo the octave).
    - Duplicate pitch names in the container are compared as distinct elements: a pair of identical names yields an interval of unison and will cause the predicate to return False (unison is not an imperfect consonance). Thus the presence of duplicate notes with the same .name will generally make the method return False.
    - The method short-circuits at the first failing pair for performance.
    - Containers with 0 or 1 notes return True.

## Examples (usage):
    - Typical usage:
        Create or populate a NoteContainer, then call the predicate to validate pairwise imperfect consonances:
            nc = NoteContainer(["C", "E", "A"])   # example container construction
            result = nc.is_imperfect_consonant()
            # result is True only if every unordered pair among C, E, A is a minor/major 3rd or 6th

    - Edge case:
            nc = NoteContainer(["C", "C"])   # duplicate pitch names
            nc.is_imperfect_consonant()      # returns False (unison is not an imperfect consonance)

## Implementation notes (for reimplementation):
    - Minimal correct implementation:
        - Return the result of calling the container's pairwise helper with the intervals predicate and no extra parameter:
            return self._consonance_test(intervals.is_imperfect_consonant)
    - Ensure that the helper passes only Note.name strings to the predicate so octave information is ignored and that it short-circuits on the first failing pair.

### `mingus.containers.note_container.NoteContainer.is_dissonant` · *method*

## Summary:
Determines whether the container contains any dissonant pair of notes by returning the logical negation of the container-level consonance check, with an adjustable fourths policy.

## Description:
Known callers and calling context:
- No other methods in this module call this method. It is provided as the complementary predicate to is_consonant for callers that need to know whether any pair of notes is dissonant.
Lifecycle / pipeline stage:
- Invoked when a caller needs a boolean answer about the presence of dissonant intervals among the notes currently held in the container (after construction or any modification).
Why this logic is its own method:
- Encapsulates the semantic question "are these notes dissonant?" and centralizes the inversion of the underlying consonance predicate so callers do not invert the result themselves.

Implementation note (equivalent expression):
- This method is implemented exactly as:
  not self.is_consonant(not include_fourths)
  Use that expression when reimplementing.

## Args:
    include_fourths (bool, optional): Controls how perfect fourths are treated with respect to dissonance.
        - Default: False
        - Semantics:
            * If include_fourths is False (the default), perfect fourths are treated as consonant for the purpose of this dissonance check.
            * If include_fourths is True, perfect fourths are treated as dissonant (stricter detection).
        - Note: The flag is inverted before delegating to is_consonant because is_consonant's include_fourths parameter means "treat fourths as consonant".

## Returns:
    bool:
        - True if there exists at least one unordered pair of distinct notes in the container that is considered dissonant under intervals.is_consonant using the fourths-policy described above.
        - False if every unordered pair of distinct notes is considered consonant under the same policy.
        - Edge cases:
            * Empty container: returns False (no pairs exist to be dissonant).
            * Single-note container: returns False (no distinct pairs exist).
            * Duplicate notes: duplicates are checked as separate entries; identical names typically yield unison (consonant).

## Raises:
    - This method does not raise exceptions itself.
    - It may propagate exceptions raised by is_consonant or underlying utilities, for example:
        * AttributeError if elements of self.notes lack a .name attribute.
        * Any exception thrown by intervals.is_consonant due to malformed input types/values.

## State Changes:
    Attributes READ:
        - self.notes (iterates entries and relies on their .name via the delegated is_consonant)
    Attributes WRITTEN:
        - None (does not modify self.notes or contained Note objects)

## Constraints:
    Preconditions:
        - Each element in self.notes must expose a .name attribute acceptable to the core interval utilities.
        - include_fourths should be a boolean (truthy/falsy values are accepted and coerced).
    Postconditions:
        - No mutation occurs to self or its Note objects.
        - The return value equals not self.is_consonant(not include_fourths).

## Side Effects:
    - None intrinsic: no I/O or external service calls.
    - Any side effects would be from the delegated calls (is_consonant / intervals.is_consonant), which are typically side-effect-free.

## Complexity:
    - Time: O(n^2) in the number of notes (delegates to is_consonant which checks all unordered pairs).
    - Space: O(1) additional.

### `mingus.containers.note_container.NoteContainer.remove_note` · *method*

## Summary:
Removes one or more notes from the container by name or by Note-object equality, updating the container's notes list in-place and returning the resulting list of notes.

## Description:
This method iterates the container's current notes and builds a new list that excludes notes matching the removal criteria. It is called from within the class by remove_notes (which handles multi-item removals) and indirectly via the subtraction operator implementation (__sub__) which delegates to remove_notes. Typical usage is when a caller needs to delete a specific pitch (by name) or a specific Note instance from the container without mutating the original list in-place (the container's notes attribute is replaced with a new list).

Why a separate method:
- Centralizes the logic for removing a single note so that remove_notes and other callers do not duplicate name-vs-object and octave-filtering behavior.
- Keeps a single responsibility: compute and set the new notes list after exclusion of the specified note.

## Args:
    note (str or Note): If a string, interpreted as a note name (e.g., "C", "G#") and removal is name-based (optionally filtered by octave). If a Note (or Note-like) object, removal uses object equality (x != note).
    octave (int, optional): Default -1. When note is a string, this narrows removal to notes with the same octave when set to any integer != -1. When -1 (the default) octave is ignored and all notes that match the given name are removed.

## Returns:
    list[Note]: The new list of Note objects assigned to self.notes after removal. This is a freshly constructed list (not the original list mutated), and it may be empty if all notes were removed. The same list object is also assigned back to self.notes.

## Raises:
    No explicit exceptions are raised by this method. 
    Preconditions must hold to avoid runtime errors:
    - Each element in self.notes must be a Note-like object exposing .name and .octave attributes (otherwise attribute access will raise AttributeError).
    - If note is neither a string nor a comparable Note-like object, the removal will fall back to equality comparison which may simply not match any items.

## State Changes:
    Attributes READ:
        - self.notes (iterated)
        - For each element x in self.notes: x.name, x.octave
    Attributes WRITTEN:
        - self.notes is replaced with a new list containing the retained Note objects

## Constraints:
    Preconditions:
        - self.notes should be an iterable (typically a list) of Note objects.
        - Note objects in self.notes must provide .name and .octave attributes and meaningful __eq__ semantics for object-equality removal.
    Postconditions:
        - After the call, self.notes contains every original element x for which the method's test returned True (i.e., items not matching the removal criteria).
        - If note is a string and octave == -1: all notes with x.name equal to note are removed.
        - If note is a string and octave != -1: only notes with x.name equal to note and x.octave equal to octave are removed; notes with the same name but different octaves are retained.
        - If note is not a string: items equal (==) to note are removed; all other items are retained.
        - The returned list is the exact new value of self.notes (same object identity).

## Side Effects:
    - Mutates the container by replacing self.notes with a newly constructed list (this changes the identity of self.notes; any external references to the previous list will not see subsequent changes).
    - No I/O, no network calls, and no external state modified beyond self.notes.

## Implementation notes (algorithm description):
    1. Create an empty result list.
    2. For each element x in self.notes:
        a. If the provided note argument is a string:
            i. If x.name != note: keep x (append to result).
            ii. Else (names match):
                - If octave != -1 and x.octave != octave: keep x.
                - Otherwise (octave == -1, or x.octave == octave): do not keep x (it is removed).
        b. If the provided note argument is not a string:
            i. If x != note: keep x.
            ii. Else: do not keep x.
    3. Assign the built result list to self.notes.
    4. Return the result list.

## Examples (illustrative, not executable here):
    - remove_note("C") removes every Note in the container whose .name == "C" (all octaves).
    - remove_note("C", octave=4) removes only Note objects with .name == "C" and .octave == 4.
    - remove_note(some_note_obj) removes note(s) equal to some_note_obj according to Note.__eq__.

### `mingus.containers.note_container.NoteContainer.remove_notes` · *method*

## Summary:
Removes one or more Note objects from the container's internal notes list, updating self.notes to exclude matching entries.

## Description:
This method accepts three broad forms of input and normalizes their handling:
- A single string note name (e.g., "C", "F#"): delegates to the single-item remover which removes all notes matching that name (unless an octave is specified when calling remove_note directly).
- A single Note-like object (any object with a .name attribute): delegates to the single-item remover which treats the argument as a concrete Note and removes matching Note objects by equality.
- An iterable of items (list, tuple, another NoteContainer, etc.): iterates over the iterable and calls the single-item removal for each element in turn; the method returns the container's notes list after all removals.

Known callers and contexts:
- NoteContainer.__sub__ (enables the subtraction operator container - other to remove notes).
- Typical use: invoked when a client needs to remove notes from a chord/voice/scale representation during editing or transformation pipelines.

Why this is a separate method:
- Consolidates type dispatch (string vs Note-like vs iterable) and iteration behavior so callers do not duplicate logic. It keeps operator overloads and external code simple by centralizing removal semantics.

## Args:
    notes (str | Note-like | iterable): The note(s) to remove.
        - str: a note name; remove_note will remove all Note objects whose .name equals this string (octave can be specified only when calling remove_note directly).
        - Note-like: any object exposing a .name attribute (commonly a mingus.containers.Note instance); matching uses equality comparison (x != note) inside remove_note.
        - iterable: an iterable whose elements are strings or Note-like objects; each element is removed by calling remove_note(element).
    Notes:
        - The method does not accept a separate octave parameter. To remove by octave, call remove_note(note, octave) directly with a string and octave or pass a Note instance with the desired octave.

## Returns:
    list[Note]: The container's notes list after removals.
        - For single-string and single Note-like inputs: returns the list returned by remove_note (the filtered list).
        - For iterable inputs: returns self.notes (the container's current notes list) after processing all elements.
        - Edge cases:
            * Passing an empty iterable returns the unchanged self.notes list.
            * Removing items that do not exist leaves self.notes unchanged and returns the current list.

## Raises:
    TypeError:
        - If 'notes' is not a string, does not have a .name attribute, and is not iterable, Python will raise a TypeError when the method attempts to iterate over it.
    (No UnexpectedObjectError is raised by this method; remove_note uses equality checks and string tests but does not validate object types in a way that raises UnexpectedObjectError.)

## State Changes:
    Attributes READ:
        - self.notes (read indirectly by remove_note to examine current notes)
    Attributes WRITTEN:
        - self.notes (assigned to the filtered list produced by remove_note; for iterable inputs, repeated calls reassign self.notes as each element is processed)

## Constraints:
    Preconditions:
        - The NoteContainer instance must be initialized and have a list-like self.notes attribute.
        - Each element passed (when passing an iterable) should be either a string or a Note-like object; passing nested structures such as tuples/lists encoding (name, octave) is not interpreted (they will be treated as non-matching objects).
    Postconditions:
        - All Note objects matching the provided removal criteria are absent from self.notes.
        - The method preserves ordering relative to how remove_note reconstructs the list (notes are not re-sorted by remove_notes itself).

## Side Effects:
    - Mutates this NoteContainer's self.notes attribute by replacing it with a filtered list.
    - No I/O or external services are invoked.
    - Does not mutate Note objects themselves; only the container's membership is changed.

### `mingus.containers.note_container.NoteContainer.remove_duplicate_notes` · *method*

## Summary:
Removes duplicate Note objects from the container's notes list in-place, preserving the first occurrence order and updating the container's notes attribute.

## Description:
This method iterates the current notes list and constructs a new list containing only the first occurrence of each element (determined using Python's membership/equality checks). It replaces self.notes with that deduplicated list and returns it.

Known callers and context:
    - No callers of this method are present inside the NoteContainer class implementation provided. It is intended as a utility for callers external to the class or for library users to invoke when duplicates may have been introduced by external manipulation, direct assignment to the notes attribute, list concatenation, deserialization, or other operations that bypass add_note/add_notes.
    - Typical lifecycle placement: call this after performing bulk operations that may create duplicate Note objects (for example, merging multiple NoteContainer instances, loading data from an external source, or applying transformations that can produce identical Note objects).

Why this is a separate method:
    - Centralizes the deduplication logic so callers do not need to reimplement it.
    - Keeps operations that modify the container's notes (filtering/deduplication) explicit and discoverable.
    - Preserves the first-seen ordering semantics, different from sort(), so it is useful when order matters and a stable dedupe is required.

## Args:
    None

## Returns:
    list[Note]: The new deduplicated list of Note objects which has been assigned to self.notes.
    - The returned list is newly created inside the method (not the original list object).
    - May be an empty list if self.notes was empty.
    - The return value always references the current value of self.notes after deduplication.

## Raises:
    None declared.
    - The method does not explicitly raise exceptions. However, if elements in self.notes do not support equality comparison and that raises an exception, that exception will propagate.

## State Changes:
    Attributes READ:
        - self.notes: iterated over to detect duplicates.
    Attributes WRITTEN:
        - self.notes: replaced with the deduplicated list (res).

## Constraints:
    Preconditions:
        - self.notes must be an iterable (typically a list) of objects for which Python membership testing (the "in" operator) and equality comparison are meaningful.
        - The caller should expect equality-based deduplication. If Note.__eq__ is not implemented to reflect desired identity (for example, comparing pitch+octave), duplicates may not be recognized as intended.
    Postconditions:
        - After the call, self.notes contains no two elements a and b such that a == b and a appears before b in the original list.
        - The order of the first occurrences of unique elements is preserved (stable deduplication).
        - len(self.notes) is less than or equal to its value prior to the call.

## Side Effects:
    - Mutates the container by assigning a new list to self.notes.
    - No I/O, no external service calls, and no mutation of objects other than replacing the notes list reference.
    - Because the method performs membership checks using "in" on a growing list, it has O(n^2) time complexity in the number of notes; for large lists this may be a performance consideration.

## Implementation notes for reimplementation:
    - Use a temporary list (res) and append elements from self.notes only if they are not already present in res (use "if x not in res").
    - After building res, assign it to self.notes and return res.
    - Do not call sort() inside this method — this method's goal is deduplication while preserving first occurrence order.

### `mingus.containers.note_container.NoteContainer.sort` · *method*

## Summary:
Sorts the container's notes list in-place so that the sequence of notes is ordered according to Python's default object ordering (the comparison behavior implemented by the Note objects).

## Description:
This method performs an in-place sort of the NoteContainer's internal notes sequence. It is a small, focused helper used when callers require the notes to be in a deterministic, ordered sequence (for example: preparing notes for output/serialization, normalizing before comparisons, or before generating chords/progressions).

Known callers and context:
- There are no explicit internal callers inside this module referenced here. Typical call sites are:
  - Consumer code that manipulates a NoteContainer and needs a canonical ordering prior to display or equality checks.
  - Higher-level operations that expect notes in ascending order before constructing chords, progressions, or exporting.
- This logic is factored into its own method because sorting is a distinct, frequently-needed mutation of the container's internal state; providing a dedicated method improves readability and reusability and centralizes any future changes to ordering behavior.

## Args:
    None

## Returns:
    None
    - The method returns None and always mutates the self.notes sequence in-place.

## Raises:
    AttributeError
        - If self.notes does not exist or does not provide a sort() method (for example if self.notes is None or replaced by an object without sort).
    TypeError
        - If the items in self.notes are not mutually comparable (comparison operations between some elements raise TypeError), the underlying list sort will raise TypeError.
    Any exception raised by the underlying list.sort implementation may propagate.

## State Changes:
Attributes READ:
    - self.notes

Attributes WRITTEN:
    - self.notes (the list object is mutated; element order may change; the list object identity is not replaced)

## Constraints:
Preconditions:
    - self.notes must be a mutable sequence that implements a sort() method (for example, a Python list).
    - Elements stored in self.notes must be mutually comparable by the comparison methods the Note class exposes (typically __lt__ or other ordering methods) so that sort can determine an ordering.

Postconditions:
    - After the call, the sequence self.notes is sorted in non-decreasing order according to the elements' comparison semantics.
    - Sorting is stable: elements considered equal according to comparisons preserve their relative order (Python's list.sort stability guarantee).

## Side Effects:
    - No I/O operations or external service calls are performed.
    - Only in-memory mutation of the self.notes sequence occurs.

### `mingus.containers.note_container.NoteContainer.augment` · *method*

## Summary:
Calls the augment operation on every Note stored in the container, mutating each contained Note in-place.

## Description:
This method iterates the container's notes list and invokes the augment method on each element. It is implemented as a small, focused helper so callers can apply the same single-note augmentation operation across the entire NoteContainer atomically from the caller perspective.

Known callers / contexts:
- No internal callers within the NoteContainer class are present in the provided module besides the complementary diminish() method. Typically invoked by client code or higher-level utilities when a user or algorithm needs to apply augmentation to all notes of a chord/collection at once (for example, to raise accidentals on every note).
- It is a convenience/batch operation placed here to keep note-level logic encapsulated in Note and collection-level orchestration in NoteContainer, rather than duplicating loops wherever an all-notes augmentation is required.

Why this is its own method:
- Provides a single, discoverable API to mutate every contained Note consistently.
- Keeps repetition out of external code and makes calling code simpler and clearer (one call vs. manual looping).
- Maintains separation of concerns: Note handles how a single augmentation is performed; NoteContainer handles applying that to the entire collection.

## Args:
    None

## Returns:
    None
    - The method performs in-place mutations on contained Note objects and does not return a value.

## Raises:
    AttributeError
        - If any element in self.notes does not have an augment attribute (e.g., it is not a Note-like object), an AttributeError will be raised when trying to call n.augment().
    Any exception raised by Note.augment
        - Any exception that the underlying Note.augment implementation raises will propagate unchanged (for example ValueError or custom exceptions thrown from Note.augment).
    TypeError
        - If self.notes is not iterable (for example, accidentally set to None or a non-iterable), iteration will raise a TypeError.

## State Changes:
Attributes READ:
    - self.notes: the container's list of note objects is iterated.

Attributes WRITTEN / Mutated:
    - The method does not reassign self.notes itself, but it mutates each element in-place by calling its augment() method:
        - self.notes[i] objects are modified according to their augment implementation.
    - No other attributes on self are written by this method.

## Constraints:
Preconditions:
    - self.notes must be an iterable (typically a list) of objects that implement an augment() method; normally these are mingus.containers.Note instances added via add_note/add_notes.
    - The container must be initialized (self.notes exists). Calling augment on an uninitialized container (if self.notes were removed or set to None externally) will raise an exception.

Postconditions:
    - For every element n present in self.notes at call-time, n.augment() has been invoked exactly once (unless an exception aborts the loop early).
    - The ordering and membership of self.notes (the list object and which objects it contains) are unchanged by this method; only the internal state of each Note object may change.

## Side Effects:
    - In-place mutation of each Note object in self.notes via the Note.augment() call.
    - No I/O, no external service calls, no creation or deletion of files.
    - Any side effects that occur are limited to what Note.augment itself performs (those effects will also occur and propagate).

### `mingus.containers.note_container.NoteContainer.diminish` · *method*

## Summary:
Lower the accidental of every Note held by the container by one semitone (mutates each contained Note in-place). The container's list structure and ordering are preserved.

## Description:
- Known callers and context:
    - No internal callers are recorded in the module. This method is intended to be invoked by application code or utilities that need to lower every pitch in a collection (for example, when diminishing a chord, applying an in-place modification to a progression, or performing batch note editing).
    - Typical lifecycle stage: used when a NoteContainer has been constructed/filled (via add_note(s), from_chord, from_interval, etc.) and the caller wants to apply a uniform semitone-lowering operation to all contained notes.

- Rationale for being a separate method:
    - Provides a container-level convenience that mirrors per-note mutation methods (e.g., augment, transpose) so callers can operate on the whole collection without iterating externally.
    - Encapsulates the batch operation and keeps higher-level code concise and intention-revealing (e.g., chord.diminish()).

## Args:
None.

## Returns:
None (implicitly returns None). The observable effect is that each contained Note instance is mutated.

## Raises:
- AttributeError: If an element of self.notes does not implement a diminish() method, the call n.diminish() will raise AttributeError and propagate.
- Any exception raised by a contained Note's diminish() implementation will propagate. In particular (based on the Note.diminish behavior):
    - IndexError: If a contained Note has an empty name string, the underlying Note.diminish may raise IndexError.
- Behavior on exceptions: iteration stops at the first exception; no internal catching or rollback is performed. Any exception is propagated to the caller.

## State Changes:
Attributes READ:
- self.notes (the list of note objects is iterated)

Attributes WRITTEN:
- None of the NoteContainer's own attributes are reassigned or replaced.
- Mutations occur on the contained Note objects: for each element n in self.notes, n.name is modified by the Note.diminish() call (i.e., self.notes[i].name is written).

## Constraints:
Preconditions:
- self.notes should be an iterable (typically a list) of objects that expose a diminish() method. In normal usage these are mingus.containers.Note instances.
- Calling code should avoid placing Note-like objects with empty name strings into the container if IndexError from Note.diminish is undesired.

Postconditions:
- For every object n in the container that successfully executes n.diminish(), n.name will be transformed according to the Note.diminish contract (i.e., accidental lowered by one semitone).
- The container's list (self.notes) remains the same object and the ordering of elements is preserved.
- The method returns None after all notes have been processed successfully.

## Side Effects:
- Mutates the name attribute of each contained Note (in-place changes to objects referenced by self.notes).
- No I/O is performed and no external services are called.
- No changes to other attributes of contained Note objects (e.g., octave, channel, velocity) are performed by this method itself — any such invariants depend on the contained Note.diminish implementation.

### `mingus.containers.note_container.NoteContainer.determine` · *method*

## Summary:
Delegates chord-identification for the notes contained in this NoteContainer to the central chord detector and returns that detector's result; does not mutate the container.

## Description:
This method collects the contained notes' pitch identifiers by calling self.get_note_names() and forwards them, together with the shorthand flag, to mingus.core.chords.determine for analysis. It is typically invoked when a caller has populated a NoteContainer and wants to obtain candidate chord names, interval descriptions, or polychord decompositions derived from the container's notes.

Known callers / typical pipeline stage:
- User code or higher-level convenience APIs that operate on NoteContainer instances and need to perform chord analysis on the container's contents.
- Used in the chord-analysis stage of a music-processing pipeline after notes have been added to the container and normalized.

Why this is a separate method:
- Encapsulates the common operation of converting a NoteContainer into the sequence form expected by the chord-detection utilities and delegating to the central chord dispatcher. Keeps the container API small and expressive (container -> chord names) and avoids duplicating argument-passing logic elsewhere.

## Args:
    shorthand (bool, optional): If True, request compact chord notation from the chord detectors (e.g., "Cm9"). If False, request verbose names where supported (e.g., "C minor ninth").
        - Default: False

## Returns:
    The exact return value of mingus.core.chords.determine(self.get_note_names(), shorthand).

    Common return shapes (see mingus.core.chords.determine for exhaustive behavior):
    - [] if and only if get_note_names() returns an empty list (a zero-length list will match the dispatcher’s empty-list equality test).
    - The original single-element sequence returned by get_note_names() when that sequence has length 1.
    - A one-element list containing an interval-description string when the note-name sequence has length 2 (e.g., ['major third']).
    - For sequences of length 3..7: whatever the respective helper detectors return (typically a list of chord-name strings; helpers may return False to indicate invalid helper-specific conditions).
    - For other lengths (including empty sequences that are not empty lists, e.g., empty tuples): the result of the polychord detector (determine_polychords), as returned by the dispatcher.

    Edge-case returns and nuances:
    - An empty tuple or other zero-length non-list sequence will not be treated the same as an empty list and will be routed differently by the chord dispatcher.
    - Any False values or helper-specific return values produced by the helpers are returned unchanged.

## Raises:
    - Any exception raised by self.get_note_names() is propagated (e.g., AttributeError if the method is missing or raises).
    - Any exception raised by mingus.core.chords.determine (or its helpers) is propagated unchanged. Typical exceptions that may surface include:
        - TypeError or AttributeError if get_note_names() does not return an indexable/sequence object.
        - Note/format-related errors from interval/chord detectors (e.g., format or note-parsing errors).
        - KeyError or other mapping errors from helper detectors if expected module-level mappings are missing.
    - This method performs no exception handling of its own.

## State Changes:
    Attributes READ:
        - None directly. The method calls self.get_note_names(); any attributes that method reads are not accessed here directly.
    Attributes WRITTEN:
        - None. This method does not modify self or any external state.

## Constraints:
    Preconditions:
        - The NoteContainer must implement get_note_names(), and that method must return an ordered, indexable sequence of pitch identifier strings (e.g., ['C', 'C#', 'Db']).
        - The returned sequence should contain valid note-name strings for meaningful chord-detection results.
    Postconditions:
        - No mutation to the NoteContainer occurs.
        - The return value equals the value returned by mingus.core.chords.determine when called with the sequence returned by get_note_names() and the provided shorthand flag.

## Side Effects:
    - None performed directly by this method (no I/O, no external service calls). Any side effects are solely those produced by self.get_note_names() or by mingus.core.chords.determine and its helper functions.

### `mingus.containers.note_container.NoteContainer.transpose` · *method*

## Summary:
Applies a transposition to every Note object stored in the container, mutating each Note in-place and returning the container (self).

## Description:
Iterates over self.notes and forwards the provided interval and direction flag to each element's transpose method (calls n.transpose(interval, up) for each n in self.notes). The method is a public convenience for applying the same transposition to every contained Note without reassigning the container or its notes list.

Known callers and context:
- There are no internal calls to this method elsewhere in the NoteContainer implementation. It is intended to be used by client code that operates on an entire collection of notes (for example, when transposing a chord or a set of notes as a unit).
- The acceptable forms and semantics of the interval argument are determined by the Note.transpose implementation; this method does not interpret or validate the interval itself.

Why this is a separate method:
- Encapsulates the repeated pattern "apply transpose to every contained note" so callers do not need to loop externally.
- Keeps call sites concise and supports fluent usage by returning self.

## Args:
    interval: Forwarded to Note.transpose. The exact allowed types/values are defined by the Note.transpose API (commonly a shorthand string or numeric semitone count); this method performs no validation.
    up (bool, optional): Direction flag forwarded to Note.transpose. True to transpose upward, False to transpose downward. Defaults to True.

## Returns:
    NoteContainer: The same container instance (self), after the contained Note objects have been mutated. If self.notes is empty, the method performs no mutations and still returns self.

## Raises:
    AttributeError: If any element n in self.notes does not implement a transpose method (i.e., lacks callable n.transpose), the attempted call n.transpose(...) raises AttributeError.
    Any exception raised by Note.transpose: Exceptions from the underlying Note.transpose implementation (for example, invalid interval values) propagate unchanged.

## State Changes:
Attributes READ:
    self.notes — iterated to obtain the Note objects.

Attributes WRITTEN:
    None of the container's attributes are rebound; self.notes remains the same list object.
    However, each Note object contained in self.notes is mutated by its transpose method.

## Constraints:
Preconditions:
    - self.notes must be an iterable (typically a list) of objects that implement transpose(interval, up).
    - The provided interval and up must be acceptable to Note.transpose.

Postconditions:
    - For every element n that was present in self.notes at call time, n.transpose(interval, up) has been invoked exactly once.
    - The membership and ordering of self.notes are unchanged by this method (no additions, removals, or reordering are performed).
    - The container instance is returned (self).

## Side Effects:
    - In-place mutation of the contained Note objects (no I/O, external service calls, or mutation of objects outside the elements of self.notes).
    - Any external references to the same Note objects will observe their updated state after this call.

### `mingus.containers.note_container.NoteContainer.get_note_names` · *method*

## Summary:
Returns a list of unique pitch names present in the container in their first-occurrence order, without modifying the container.

## Description:
This helper method extracts the pitch/name string from each Note object stored in self.notes and builds a list containing each distinct name exactly once, preserving the order of first appearance. Known callers:
- NoteContainer.determine — used when the container's pitches must be given to the chord-determination routine (chords.determine).
- Any external code that needs a deduplicated list of pitch names (for analysis, display, or interfacing with core functions).

This logic is factored into its own method to centralize the operation of converting a container of Note objects into the simple canonical representation (a list of names). That keeps other methods (e.g., determine, external utilities) simple and avoids duplicating the deduplication and ordering logic across the class.

## Args:
    None

## Returns:
    list[str]: A list of note name strings (for example 'C', 'C#', 'Eb', etc.).
    - Order: names appear in the result in the same order as the first Note with that name appears in self.notes.
    - Uniqueness: each name appears at most once (duplicates are removed).
    - Edge cases:
        * If self.notes is empty, returns an empty list [].
        * If multiple Note objects differ only by octave (e.g., C4 and C5), only the name ('C') appears once.

## Raises:
    AttributeError: If any element in self.notes does not expose a .name attribute, an AttributeError will be raised when the method attempts to access n.name.
    (The class invariant expects elements of self.notes to be Note objects with a .name attribute; add_note enforces this in normal usage.)

## State Changes:
    Attributes READ:
        - self.notes (the list object is iterated; each element's .name is read)
    Attributes WRITTEN:
        - None (the method does not modify self or any external object)

## Constraints:
    Preconditions:
        - self.notes must be an iterable of objects exposing a .name attribute (normally mingus.containers.note.Note instances).
    Postconditions:
        - self remains unchanged.
        - The returned list contains each distinct name present in the pre-call self.notes exactly once, preserving first-occurrence order.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside of read operations on self.notes and its elements.

## Implementation notes and performance:
    - The method uses a simple linear scan and membership testing with "if n.name not in res", yielding O(n^2) worst-case behavior for n distinct names due to repeated list membership checks. For very large containers, a set-based approach could be used to improve performance at the cost of losing stable first-occurrence ordering (or by tracking seen names in a set while preserving order).
    - Typical usage assumes small to moderate-size containers (chords, intervals), where the current implementation is simple and efficient enough.

## Example (illustrative):
    - If self.notes contains Note('C', 4), Note('C', 5), Note('E', 4) then the method returns ['C', 'E'].

### `mingus.containers.note_container.NoteContainer.__repr__` · *method*

## Summary:
Return a string representation of the container's notes collection by applying Python's built-in str() to the notes attribute; does not mutate the object.

## Description:
This method implements the object's official textual representation by returning the result of str(self.notes). Typical call sites and contexts:
- The built-in repr(obj) function calls this method directly (since this is the object's __repr__ implementation).
- Code that explicitly calls obj.__repr__ or otherwise requests the object's representation for debugging, logging, or serialization.
- Indirect call contexts that invoke repr(obj) (debug printers, debuggers, and some logging facilities). Note: print(obj) calls str(obj) (which prefers __str__); print will use this method only if __str__ is absent or falls back to __repr__.

Why this is a dedicated method:
- Centralizes the logic for producing the container's textual representation so all callers see a consistent view of the contained notes.
- Keeps conversion logic localized (useful for debugging and introspection) instead of duplicating str(self.notes) at multiple call sites.

## Args:
    None

## Returns:
    str: The exact string returned by calling built-in str() on self.notes.
    - Typical outputs: Python's collection representations such as "[]" for an empty list, or "['C-4', 'E-4']" if the notes collection contains strings or objects whose str()/repr() yield those forms.
    - Deterministic snapshot: the returned string reflects the current contents of self.notes at the time of the call.

## Raises:
    AttributeError: If the instance lacks a notes attribute (attempting to access self.notes raises AttributeError).
    Any exception raised while converting self.notes to a string: if str(self.notes) triggers an exception (for example, because an element's __str__/__repr__ raises), that exception propagates unchanged from this method.

## State Changes:
    Attributes READ:
        - self.notes
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The instance must have an attribute named notes. There is no type enforcement in this method; however, useful output assumes notes is a Python object with a meaningful str() (commonly a list/tuple of Note instances or strings).
    Postconditions:
        - The object (self) and its attributes are unchanged by this call.
        - A string representing the then-current value of self.notes is returned.

## Side Effects:
    - No I/O, no network or filesystem access.
    - No mutation of self or of objects reachable from self is performed by this method.
    - The only observable effect is returning a str object; any side effect must originate from custom __str__/__repr__ implementations of objects contained within self.notes (and will propagate).

### `mingus.containers.note_container.NoteContainer.__getitem__` · *method*

## Summary:
Provides indexed or sliced access into the container's internal note sequence by delegating to the underlying list; does not modify container state.

## Description:
This method implements item access for the NoteContainer sequence interface by returning self.notes[item], forwarding all semantics to the built-in list.__getitem__ implementation. It is invoked whenever client code or Python's sequence protocol requests an element or a slice from a NoteContainer instance (for example: container[0], container[-1], container[1:3], or when iterating with "for n in container" since iteration uses __len__ and __getitem__). Within this class, iteration in __eq__ (the "for x in self" loop) will call this method.

Keeping this logic in a dedicated __getitem__ method:
- Exposes standard Python sequence semantics for indexing and slicing.
- Centralizes access to the underlying notes list so any future changes to storage can be confined to this method.
- Allows Python to treat NoteContainer as a sequence (iteration, membership tests via iteration, etc.) without inlining list access throughout the class.

## Args:
    item (int or slice or any object accepted by list.__getitem__):
        - If an integer: a zero-based index; negative indices are supported per Python list semantics.
        - If a slice: a slice object producing a sub-list of notes.
        - Other index-like objects that the list implementation supports (e.g., objects implementing __index__).

## Returns:
    Note or list[Note] or arbitrary element:
        - If item is an integer: returns the single element stored at that index (typically a mingus.containers.Note instance).
        - If item is a slice: returns a new list containing the selected elements (list of Note).
        - If the underlying self.notes list contains non-Note objects (due to external mutation), those exact objects are returned unchanged.

## Raises:
    IndexError:
        - Raised when an integer index is out of range (delegated from list.__getitem__).
    TypeError:
        - Raised when item is an inappropriate type for list indexing (delegated from list.__getitem__).

## State Changes:
    Attributes READ:
        - self.notes
    Attributes WRITTEN:
        - None (this method does not modify any attributes)

## Constraints:
    Preconditions:
        - self.notes must be a sequence object (normally a Python list) accessible on the NoteContainer instance.
        - The caller should expect Python list indexing/slicing semantics (0-based, negative indices allowed).
    Postconditions:
        - The NoteContainer instance is unchanged.
        - The returned object is a direct element from the underlying list (for integer index) or a new list containing references to the same element objects (for slice).

## Side Effects:
    - No I/O or external service calls.
    - No mutation of external objects by this method itself.
    - Note objects returned are the same object instances stored in self.notes; mutating a returned Note (e.g., changing its octave) will affect the NoteContainer because the Note is mutable and shared by reference.

### `mingus.containers.note_container.NoteContainer.__setitem__` · *method*

## Summary:
Assigns a value into the container's internal notes list at the given index/slice, converting a string note name into a Note object; returns the updated internal notes list.

## Description:
This method is invoked whenever Python assignment syntax is used on a NoteContainer instance (e.g., container[index] = value). Typical callers are user or client code replacing or inserting notes by index or slice during composition or editing workflows. It exists as a dedicated method to centralize the logic of accepting either plain note-name strings or note-like objects and ensuring that string inputs are converted to a Note instance before being stored. This keeps callers simple and consistent while preventing scattered conversion logic across the codebase.

Known callers / invocation contexts:
- Direct assignment by consumers of NoteContainer: container[i] = "C#-4" or container[0] = Note("C", 4)
- Slice assignment by consumers: container[1:3] = [Note("D",4), "E"] (see Constraints for slice-specific notes)
- Not explicitly invoked by other methods inside this module; used as the container protocol for assignment.

Why this is a separate method:
- Centralizes conversion from string input to Note objects.
- Provides the standard Python assignment interface for the container (supporting index/slice semantics of lists).
- Keeps add_note/add_notes semantics separate (which handle more complex normalization and duplicate handling).

## Args:
    item (int or slice): The index or slice specifying where to assign in self.notes. Must be a valid index or slice acceptable by Python list assignment semantics for the current self.notes list.
    value (str or object): If a string (any six.string_types), it is interpreted as a note name and converted to a mingus.containers.note.Note via Note(value) before assignment. Otherwise the value is assigned directly (commonly a Note instance or an iterable for slice assignment).

## Returns:
    list: The container's internal notes list (self.notes) after assignment. This is the same list object stored on self.notes, now updated with the assigned value(s).

## Raises:
    - No exceptions are explicitly raised by this method.
    - The Note constructor may raise errors if the provided string is not a valid note representation; those exceptions propagate out of this method.
    - Assigning a single Note object to a slice (e.g., container[1:3] = "C") can raise a TypeError from underlying list assignment if the right-hand value is not an iterable of appropriate length — this is standard Python list behavior and not handled here.

## State Changes:
    Attributes READ:
        - self.notes (reads to perform index/slice assignment semantics and to return the list)
    Attributes WRITTEN:
        - self.notes (the underlying list is mutated: elements replaced or slice-assigned)

## Constraints:
    Preconditions:
        - self.notes must be a list (the class initializes it as a list and methods expect list semantics).
        - item must be a valid index or slice for list assignment; invalid indices or incompatible slice assignment shapes will raise Python exceptions.
        - If value is a string, it must be a valid note string acceptable by Note(value) (or Note will raise).

    Postconditions:
        - After the call, the internal list self.notes reflects the assignment (element(s) replaced according to item and value).
        - The method returns the same list object referenced by self.notes.

## Side Effects:
    - Mutates self.notes (the container's internal list).
    - If value is a mutable object, callers retain references to that object (no defensive copy is performed).
    - No I/O, network, or external service interactions occur.
    - No validation (beyond string-to-Note conversion) is performed: non-Note objects can be stored and may cause issues elsewhere if they lack expected attributes.

### `mingus.containers.note_container.NoteContainer.__add__` · *method*

## Summary:
Adds the given note(s) to this NoteContainer (in-place) and returns the same container to support chaining and the + operator.

## Description:
This method is the implementation of the Python + operator for NoteContainer objects. It is invoked whenever user code or other modules use the infix addition operator (container + notes) with a NoteContainer instance on the left-hand side. Typical call sites are:
- User code that combines existing NoteContainer(s) with additional notes or note-like objects using the + operator.
- Any code that expects operator chaining, e.g. container = container + "C" or container += "C" (in-place behavior is provided by returning self).

This method is a small, dedicated wrapper that delegates all input validation and insertion work to add_notes and then returns self. Keeping this logic as a thin operator overload method preserves a single authoritative implementation of adding notes (add_notes) while providing the ergonomic + operator for callers.

## Args:
    notes (various): One of the following accepted forms (all are forwarded to add_notes):
        - Another NoteContainer-like object (has attribute 'notes'): its contained notes are added.
        - A single Note-like object (has attribute 'name').
        - A string with a note name (e.g., "C", "F#").
        - An iterable of items where each item is one of:
            * a Note-like object
            * a string note name
            * a list/tuple describing a note: [name, octave] or [name, octave, dynamics]
    There is no default; caller must supply a value. Passing None or a non-iterable that does not expose a 'name' attribute will result in an exception (see Raises).

## Returns:
    NoteContainer: Returns the same NoteContainer instance (self) after attempting to add the provided notes. This enables chaining and matches typical in-place operator semantics. If no notes were added (e.g., empty iterable), the returned object is still the same instance and its notes list is unchanged.

## Raises:
    UnexpectedObjectError: Raised if an element being added is neither a string nor a Note-like object (i.e., it does not have a 'name' attribute) and thus cannot be interpreted as a Note. This originates from add_note when validating individual objects.
    TypeError: May be raised if the provided notes argument is not iterable and also does not present a 'name' attribute (for example, passing an integer). Iteration over a non-iterable value at the final fallback path in add_notes will raise this exception.

## State Changes:
    Attributes READ:
        - self.notes (inspected by add_notes/add_note for determining default octave and membership checks)
    Attributes WRITTEN:
        - self.notes (may be appended to, sorted, and updated by add_notes/add_note)

## Constraints:
    Preconditions:
        - self must be a properly initialized NoteContainer (its self.notes should be a list).
        - The notes argument must be one of the accepted forms described in Args. If an element cannot be resolved to a Note or a valid string representation, an UnexpectedObjectError will be raised.

    Postconditions:
        - The container's self.notes will include the newly added notes (if any) after the call.
        - Added notes are appended only if not already present (add_note prevents duplicates).
        - The stored notes list is sorted after insertions.
        - The method returns the same NoteContainer instance (self).

## Side Effects:
    - Mutates the NoteContainer in-place by changing self.notes (append, sort).
    - No I/O, no network calls, and no modification of external objects other than the passed-in note objects when they are stored (the Note objects themselves are referenced or constructed by add_note).
    - If a plain string note is added, add_note may construct new Note instances (which are then stored in self.notes).

## Notes / Implementation rationale:
    - This method exists solely to expose operator-friendly semantics while delegating the detailed insertion logic (type handling, Note construction, octave inference, duplicate prevention, and sorting) to add_notes/add_note. This avoids duplication of validation and normalization logic across the class.
    - Because it returns self, use of this operator is in-place from the caller's perspective; code that expects a fresh copy should explicitly construct one before adding.

### `mingus.containers.note_container.NoteContainer.__sub__` · *method*

## Summary:
Performs removal of one or more notes from this container and returns the same container (in-place mutation).

## Description:
This operator overload implements subtraction semantics for a NoteContainer instance: when a developer writes container - notes, this method delegates to remove_notes(notes) to remove matching entries from the container's internal notes list and then returns self. It is meant to be used by client code that wants a succinct, chainable way to remove notes (for example, in transformation pipelines or interactive manipulations). No internal callers are required by the library; it is invoked whenever the binary subtraction operator is used with a NoteContainer on the left-hand side.

This behavior is separated into its own method because it implements the Python operator protocol (special method for '-') and provides a thin, self-contained wrapper around the removal logic (remove_notes). Keeping operator semantics here keeps higher-level code concise and delegates the real removal logic to a dedicated method.

## Args:
    notes (str | mingus.containers.note.Note | Iterable): One of:
        - a string note name (e.g., 'C#') to remove all matching named notes,
        - a Note-like object (has attribute 'name'), which will be compared by equality,
        - or an iterable of such items (strings or Note objects). 
    Notes:
        - Unlike add_notes, passing nested list forms like ['C', 4] is not specially interpreted by remove_notes; such compound list elements will be treated as arbitrary objects and compared for equality against container elements. (add_notes supports list forms for adding, but removal only treats strings and Note-like objects specially.)

## Returns:
    NoteContainer: Returns self (the same NoteContainer instance) after performing removals. The returned object reflects the updated internal state (self.notes) with the requested elements removed.

## Raises:
    This method itself does not raise exceptions directly. However, exceptions may arise elsewhere if the caller passes pathological objects that other code expects to have certain attributes. In typical use with strings or Note objects no exceptions are raised by this method.

## State Changes:
    Attributes READ:
        - self.notes (read by the called remove_notes/remove_note methods to identify items to keep/remove)
    Attributes WRITTEN:
        - self.notes (assigned a new list of remaining notes by remove_note/remove_notes)

## Constraints:
    Preconditions:
        - self must be a properly-initialized NoteContainer instance (self.notes should be a list of Note objects).
        - notes must be one of the accepted forms listed above (string, Note-like object, or iterable of such). Passing nested compound descriptors (e.g., lists used by add_notes to specify octave/dynamics) will not be interpreted as such by removal and will be compared directly for equality.
    Postconditions:
        - The container (self) is returned.
        - self.notes will no longer contain elements that matched the removal criteria passed in notes.
        - The remaining ordering of notes is determined by remove_note (it rebuilds the list of non-matching items in original iteration order but does not re-sort automatically).

## Side Effects:
    - Mutates the NoteContainer in-place by replacing self.notes with a new list that excludes removed elements.
    - No I/O or external service calls occur.
    - No other global state is modified.

### `mingus.containers.note_container.NoteContainer.__len__` · *method*

## Summary:
Return the number of Note objects currently stored in the container as a non-negative integer.

## Description:
This method exposes the container's size to Python's sequence protocol so callers can use the built-in len() function on a NoteContainer instance. Typical callers include:
- External code that checks whether the container is empty or to size-controlled loops (e.g., "if len(container) == 0: ...").
- Any code that uses the built-in len() to make decisions about iteration, validation, or formatting.
- Test code asserting expected note counts.

The logic is a dedicated method to implement the sequence protocol (__len__) for this container type and to centralize the definition of length in a single place rather than duplicating len(self.notes) at call sites. It simply delegates to the underlying storage (self.notes) so the container behaves like a standard Python sequence.

## Args:
This method takes no arguments other than self.

## Returns:
int: The count of elements in self.notes. Always a Python int >= 0.
- If self.notes is a standard sequence (the normal case), this is equivalent to the list length.
- If self.notes does not support length, calling len() will raise the usual TypeError coming from the built-in len().

## Raises:
TypeError: If self.notes is not an object that supports the built-in len() operation (this is not raised by this method explicitly but by Python's len() when it attempts to measure the underlying object).

## State Changes:
Attributes READ:
    - self.notes

Attributes WRITTEN:
    - None (this method does not modify any attributes)

## Constraints:
Preconditions:
    - The instance must have a self.notes attribute that is or behaves like a sequence (supports __len__). The class constructor calls empty() to ensure self.notes is a list in normal usage.

Postconditions:
    - No change to the object's state.
    - The returned integer equals len(self.notes) at the moment the method is called.

## Side Effects:
    - None. No I/O, no external calls, and no mutation of self or other objects.

### `mingus.containers.note_container.NoteContainer.__eq__` · *method*

## Summary:
Performs a subset-style equality check: returns True if every element held by this container is present in the other operand (using Python's membership test), otherwise False.

## Description:
This method is executed when Python evaluates equality with a NoteContainer as the left-hand operand (the == operator dispatches to this method). It implements equality as a one-way containment test (self ⊆ other), not as strict sequence or multiset equality.

The logic is encapsulated in its own method to provide consistent, container-specific semantics for equality comparisons across the codebase and to centralize behavior when comparing NoteContainer instances to other iterables (lists, tuples, other NoteContainer-like objects). It avoids duplicating membership-handling logic at call sites and ensures the equality operator behaves predictably for this container type.

## Args:
    other (object supporting membership testing): Any object for which the expression 'x in other' is meaningful for the element objects stored in this container. Typical examples are another NoteContainer, a list or tuple of Note-like objects, or any object implementing __contains__ or iterable protocol. No default value.

## Returns:
    bool
        - True if for every element x in this container, the membership test 'x in other' evaluates to True.
        - False immediately when any element x in this container is not found in other.
      Special cases:
        - Returns True for an empty container (vacuous truth).
        - Does not verify that other contains only the same elements (other may contain additional elements).

## Raises:
    TypeError or any exception propagated from the membership check:
        - If other is None or otherwise not suitable for the membership operation, executing 'x in other' will raise (commonly TypeError for non-iterable NoneType), and that exception will propagate.
        - If other.__contains__ or iteration over other raises an exception, that exception will propagate unchanged.
        - If element comparison during membership testing invokes element equality methods that raise, those exceptions propagate.

## State Changes:
    Attributes READ:
        - self.notes (accessed indirectly by iteration; iteration uses __len__ and __getitem__ implemented on this class)
    Attributes WRITTEN:
        - None. The method does not modify self or other.

## Constraints:
    Preconditions:
        - self must be a valid NoteContainer instance exposing its elements via iteration (this class provides __len__ and __getitem__).
        - Elements contained in self should be comparable to elements of other (their equality implementation must not raise unexpectedly) for reliable membership checks.
        - other must support membership testing (implement __contains__ or be iterable); otherwise a TypeError or similar will occur during the first membership check.

    Postconditions:
        - Returns a boolean value.
        - Neither self nor other are modified by the call.

## Side Effects:
    - None local to this method: no I/O, network, or persistent state mutation.
    - Any side effects originate from methods called during membership testing (for example, other.__contains__ or element __eq__), and these will propagate.

## Implementation details (for reimplementation):
    - Iterate over each element x in self using Python's iteration protocol. In this class, iteration falls back to sequence access (it uses __len__ and __getitem__ because the class does not define __iter__).
    - For each x, evaluate membership with 'x in other'. If the membership test returns False for any x, return False immediately.
    - If the loop completes without finding a missing element, return True.
    - Complexity: O(n * m) in the worst case where n is the number of elements in self and m is the cost of a single membership test on other (for example, scanning other if it is a list).
    - Note: This equality is asymmetric. If callers need strict equality (same elements and same multiplicities), they must additionally check that other does not contain elements not present in self or compare lengths/multisets as appropriate.

