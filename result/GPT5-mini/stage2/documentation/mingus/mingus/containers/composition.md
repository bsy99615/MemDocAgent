# `composition.py`

## `mingus.containers.composition.Composition` · *class*

## Summary:
Represents a musical composition containing an ordered list of tracks and metadata (title, subtitle, author, email, description). Provides operations to add tracks, add notes to selected tracks, and query or replace tracks by index.

## Description:
The Composition class is an in-memory container for a collection of Track-like objects (objects exposing a "bars" attribute) and composition-level metadata. Instantiate Composition when you need to build or manipulate a multi-track musical piece programmatically (for example in a composition editor, music-processing pipeline, or when serializing a set of Track objects).

Common usage scenarios:
- Create empty composition, set metadata, add Track instances, and then add Note objects to the currently selected track(s).
- Tools that construct a composition programmatically: create Composition(), add_track(track), then repeatedly call add_note(note) to append notes to the selected track(s).
- Simple read-only iteration and rendering of contained tracks via indexing, len(), and repr().

Callers/factories:
- Any client code that constructs compositions by hand (Composition()).
- Higher-level utilities that create Track objects and append them to a Composition using add_track or the addition operator.

Motivation and responsibility boundary:
- Composition centralizes track collection and metadata. It intentionally enforces only a lightweight validation on added tracks (checks for a "bars" attribute) and delegates per-track note-handling to the Track object itself. It is not responsible for validating Note objects or enforcing musical constraints — that responsibility belongs to the Track and Note implementations.

## State:
Attributes (instance-visible; defaults shown are initial class-level values but instance values are established by __init__/methods):

- title (str)
  - Default: "Untitled"
  - Description: Primary title of the composition.
  - Valid values: any string.

- subtitle (str)
  - Default: "" (empty string)
  - Description: Secondary title or subtitle for the composition.

- author (str)
  - Default: "" (empty string)
  - Description: Name of the author/creator.

- email (str)
  - Default: "" (empty string)
  - Description: Contact email for the author.

- description (str)
  - Default: "" (empty string at class level)
  - Description: Free-form description of the composition.

- tracks (list[Track])
  - Default at instantiation: [] (empty list)
  - Description: Ordered list of Track-like objects. Each track is expected to expose a "bars" attribute; no further structural checks are performed by Composition.
  - Invariant: tracks is always a list object (may be empty). Each item is intended to be a Track-like object.

- selected_tracks (list[int])
  - Default at class-level: [] — not explicitly set in __init__; after the first add_track call it is set to a new list on the instance.
  - Description: List of integer indices indicating which tracks are "selected" for subsequent add_note calls.
  - Invariant: If non-empty, every index must be a valid index into tracks (0 <= index < len(tracks)). The code does not proactively enforce this invariant on assignment; it will surface IndexError when used if invalid.

Class invariants:
- tracks is a list and selected_tracks (when used) contains integer indices pointing into tracks.
- title, subtitle, author, email, and description are strings.

Note on class-level mutable defaults:
- The source file declares tracks and selected_tracks at class scope. __init__ calls empty() to create an instance tracks list, and add_track creates an instance selected_tracks list. Consumers should not rely on class-level lists being shared; instance-level lists will be created on first use.

## Lifecycle:
Creation:
- Instantiate with no parameters:
    comp = Composition()
  - This creates an instance and calls empty() to set self.tracks = [].

Usage (typical call sequence):
1. Optionally set metadata:
     comp.set_title("My Song", "Subtitle")
     comp.set_author("Author Name", "author@example.com")
2. Add one or more tracks:
     comp.add_track(track_obj)
   - add_track validates that the provided object has a "bars" attribute; if not, it raises UnexpectedObjectError.
   - After adding, the new track becomes the only selected track (selected_tracks set to [index_of_new_track]).
3. Add notes to selected tracks:
     comp.add_note(note_obj)
   - add_note iterates selected_tracks and performs track + note for each selected track; actual note-handling is performed by the Track implementation via its __add__ or equivalent.
   - You may change selected_tracks (assign a list of indices) before calling add_note to direct notes to different tracks.
4. Query or modify tracks:
     t = comp[0]           # __getitem__
     comp[0] = another     # __setitem__
     n_tracks = len(comp)  # __len__
5. Inspect whole composition:
     str(comp) or repr(comp) returns the concatenation of str(track) for each track.

Ordering and sequencing notes:
- add_track sets selected_tracks to the newly-added track; therefore subsequent add_note calls will target the most recently added track by default.
- There is no explicit destroy/close method; no cleanup is required.

Destruction:
- Managed by Python garbage collection; Composition has no context manager or explicit resource cleanup.

Important operator caution:
- The class implements __add__(self, value) which dispatches to add_track when value has a "bars" attribute, otherwise to add_note. Both add_track and add_note mutate the composition and return None. Therefore, using the + operator and reassigning the result is dangerous:
    comp = comp + track_obj  # comp becomes None because __add__ returns None
  Prefer calling add_track/add_note methods to avoid accidental reassignments.

## Method Map:
graph TD
    init[Composition.__init__] --> empty[empty()]
    empty --> tracks_set[tracks = []]
    add_track[add_track(track)] --> validate[hasattr(track,"bars")?]
    validate -- yes --> append[tracks.append(track)] --> set_selected[selected_tracks=[len(tracks)-1]]
    validate -- no --> raise[raise UnexpectedObjectError]
    add_note[add_note(note)] --> loop[selected_tracks loop] --> per_track_call[tracks[n] + note]
    set_title[set_title(title, subtitle)] --> set_attrs[title/subtitle set]
    set_author[set_author(author, email)] --> set_attrs2[author/email set]
    getitem[__getitem__(index)] --> return_track
    setitem[__setitem__(index,value)] --> tracks[index] = value
    len[__len__()] --> return len(tracks)
    repr[__repr__()] --> concatenate str(track) for track in tracks

(Flow shows validation and how add_track sets selected_tracks; add_note delegates addition to Track objects.)

## Raises:
- UnexpectedObjectError
  - Raised by add_track(track) (and therefore implicitly by composition + track) if the provided track object does not have a "bars" attribute.
  - Message format: "Unexpected object '%s', expecting a mingus.containers.Track object" with the stringified provided object.

- IndexError
  - May be raised by __getitem__, __setitem__, or add_note if an index in selected_tracks is out of range for tracks.
  - Example: setting selected_tracks = [10] when tracks has length 1; calling add_note will raise IndexError when accessing tracks[10].

- Any exceptions raised by Track.__add__ or Track methods
  - add_note relies on track + note; errors thrown by that expression (TypeError, AttributeError, custom exceptions) will propagate unchanged.

- TypeError / AttributeError
  - If consumers misuse Composition (e.g., calling add_note with an object that Track.__add__ cannot handle), underlying TypeError or AttributeError can occur and will propagate.

## Example:
# Create a composition
comp = Composition()
comp.set_title("Sunrise", "Dawn Theme")
comp.set_author("Jane Doe", "jane@example.com")

# Minimal pseudo-Track object for illustration (must expose 'bars' and support '+ note')
class FakeTrack(object):
    def __init__(self): self.bars = []
    def __add__(self, note): self.bars.append(note); return self

track = FakeTrack()

# Add a track (validates presence of 'bars')
comp.add_track(track)
# Now selected_tracks == [0]

# Add a note to the selected track(s)
comp.add_note("C4_quarter")   # actual Note object expected by real Track implementations

# Inspect composition
first_track = comp[0]
count = len(comp)
print(str(comp))  # concatenation of str(track) for all tracks

# Replace a track by index
comp[0] = FakeTrack()

# Dangerous: do NOT reassign the result of the + operator (it returns None)
comp.add_track(track)          # safe
result = comp + track         # returns None but still mutates comp; avoid comp = comp + track

### `mingus.containers.composition.Composition.__init__` · *method*

## Summary:
Initializes a new Composition instance by resetting its tracks to a fresh, empty list (delegates initialization to the empty() helper).

## Description:
- Known callers:
    - The Python object constructor when code instantiates Composition() (i.e., any place that creates a new Composition object).
    - Indirectly complements the reset() lifecycle method which also calls empty() (reset() calls empty() itself; __init__ calls empty() at instantiation).
- Lifecycle/context:
    - Executed exactly once as part of instance construction; establishes the initial internal container state for tracks so subsequent operations (add_track, add_note, iteration, length) operate on an instance-specific list.
- Why this is a separate call to empty():
    - The actual work of clearing/initializing the track container lives in empty() so that other methods (for example reset()) can reuse the same initialization logic without duplicating code. This isolates the mutation of the tracks attribute into a single helper, making intent explicit and avoiding repetition.

## Args:
    None.

## Returns:
    None.

## Raises:
    None. The constructor performs no validation and does not raise exceptions.

## State Changes:
- Attributes READ:
    - None explicitly (the method calls self.empty(), but __init__ itself does not read attribute values).
- Attributes WRITTEN:
    - self.tracks is set to a new empty list (via empty()).

## Constraints:
- Preconditions:
    - None required. The method is safe to call on a fresh, partially-initialized, or previously-used instance; it does not depend on other attributes being set.
- Postconditions:
    - After __init__ returns, the instance will have an instance attribute self.tracks referencing a new empty list.
    - Other class-level defaults declared on Composition (title, subtitle, author, email, description, selected_tracks) are not changed by __init__; they remain the class-level defaults until/ unless instance code assigns to them later.

## Side Effects:
- Mutations:
    - Creates and assigns an empty list to self.tracks on the instance (this breaks sharing of the class-level tracks list).
- I/O / external calls:
    - None. No file, network, or external service interactions occur.
- Important implementation note (pitfall to avoid):
    - The Composition class declares mutable defaults at class scope (tracks = [] and selected_tracks = []). __init__ explicitly replaces tracks with a new list for the instance, preventing accidental sharing of the tracks list between instances. However, selected_tracks remains the class-level list until some instance code assigns to self.selected_tracks (for example add_track assigns a new list to self.selected_tracks). Callers should be aware of this subtlety when reading or mutating selected_tracks on a newly created instance.

### `mingus.containers.composition.Composition.empty` · *method*

## Summary:
Replaces the composition's track list with a fresh, empty list, clearing all tracks stored on the instance.

## Description:
Known callers and context:
- Composition.__init__: Called during object construction to ensure each instance gets its own empty tracks list instead of sharing the class-level default.
- Composition.reset: Called when reinitializing a composition; reset delegates the clearing of tracks to this method.
- External callers: Intended for use wherever an explicit clear of all tracks is required before reusing or rebuilding a Composition.

Why this is a separate method:
- Centralizes the "clear tracks" operation so both the constructor and reset (and any other callers) use the same logic.
- Ensures instances do not share the mutable class-level default list (tracks = []) by assigning a new list on the instance.
- Keeps callers simple (single line to clear tracks) and documents the intent semantically.

## Args:
This method takes no arguments.

## Returns:
None

## Raises:
This method does not explicitly raise exceptions.
Note: subsequent operations that index into self.tracks (for example __getitem__ or methods that assume at least one track exists) may raise IndexError if called after empty() without adding tracks first.

## State Changes:
Attributes READ:
- None (the method does not read any instance attributes prior to assignment).

Attributes WRITTEN:
- self.tracks: assigned to a new empty list instance ([]).

## Constraints:
Preconditions:
- None required by the method itself; the Composition instance must be a normal object that allows attribute assignment (as implemented in the class).

Postconditions:
- self.tracks is a brand-new empty list (len(self.tracks) == 0).
- Other attributes (for example self.selected_tracks) are not modified by this method; they may therefore contain indices that are no longer valid after clearing tracks.

## Side Effects:
- Mutates only the Composition instance by replacing its tracks attribute with a new list.
- If external code held a reference to the previous list object formerly assigned to self.tracks, that external reference remains valid but is no longer used by the Composition instance (the old list is effectively orphaned from the instance).
- No I/O or external service calls are performed.

### `mingus.containers.composition.Composition.reset` · *method*

## Summary:
Clear all tracks and restore the composition's title/author metadata to their default values, returning the object to the standard newly-created state.

## Description:
Performs a grouped reinitialization of the Composition instance by invoking three helper methods:
- empty(): clears the track list.
- set_title(): sets title/subtitle to their default values.
- set_author(): sets author/email to their default values.

Known callers:
- No direct callers were discovered in the provided repository snapshot. This method is intended for client code that needs to discard current content and reuse a Composition instance (for example, when creating a new composition in an editor, cancelling changes, or resetting state between tests).

Lifecycle context and rationale:
- __init__ calls empty() to ensure a newly-constructed Composition starts with no tracks. reset() consolidates the additional metadata reset steps so callers do not need to call empty(), set_title(), and set_author() individually.
- Keeping this logic in a dedicated method centralizes the reinitialization behavior and makes code that needs a full reset clearer and less error-prone.

## Args:
    None

## Returns:
    None

## Raises:
    None. The helper methods invoked by reset() (empty, set_title, set_author) do not raise exceptions under normal conditions.

## State Changes:
Attributes READ:
    - None. reset() does not inspect or rely on current instance attribute values before overwriting them.

Attributes WRITTEN (modified by this call):
    - self.tracks: assigned a new empty list (via empty()).
    - self.title: set to "Untitled" (via set_title()).
    - self.subtitle: set to "" (via set_title()).
    - self.author: set to "" (via set_author()).
    - self.email: set to "" (via set_author()).

Note: These assignments create or overwrite instance-level attributes; they do not modify the class-level defaults declared on the Composition class.

## Constraints:
Preconditions:
    - self must be a valid Composition instance (i.e., an instance of the Composition class). No other conditions or arguments are required.

Postconditions:
    - self.tracks is an empty list ([]).
    - self.title == "Untitled"
    - self.subtitle == ""
    - self.author == ""
    - self.email == ""
    - The method returns None.

Important caveat:
    - reset() does NOT modify self.selected_tracks. If selected_tracks currently contains indices, those indices will not be reconciled with the now-empty self.tracks list and therefore may be stale or invalid after reset. Callers that rely on selected_tracks should explicitly update or clear it after reset if necessary.

## Side Effects:
    - In-memory mutation only: modifies the instance attributes listed above.
    - No I/O, no network or filesystem access, and no mutation of objects outside the Composition instance.
    - Because the class defines certain default values at the class level (title, subtitle, author, email, tracks, selected_tracks), calling reset assigns instance-level attributes that shadow those class-level defaults for this instance.

### `mingus.containers.composition.Composition.add_track` · *method*

## Summary:
Adds a track object to the composition by appending it to the internal tracks list and making that newly added track the single selected track.

## Description:
This method is the single, canonical operation for adding a new track to a Composition instance. It performs a minimal validation (checks that the supplied object exposes a "bars" attribute) and then updates composition state so the newly added track becomes the only selected track.

Known callers and context:
- No internal callers are required or referenced by this method; it is intended to be invoked by client code, UI event handlers, or higher-level composition-building utilities at the point where a new Track should become part of a Composition.
- Typical lifecycle usage: called when constructing or modifying a Composition (for example, when a user chooses "add track" in an editor or when programmatically assembling a composition before rendering or exporting).

Why this is a separate method:
- Encapsulates the validation and state-update semantics for adding a track (append + update selection) in one place so callers need not duplicate logic or risk inconsistent selection state across the codebase.

## Args:
    track (object): An object expected to represent a track. The method does not require a specific class type but requires that the object have an attribute named "bars" (checked with hasattr). In the Mingus library this is typically an instance of mingus.containers.Track.

## Returns:
    None

    - There is no return value. The effect is purely the mutation of the composition object's state (see State Changes).

## Raises:
    mingus.containers.mt_exceptions.UnexpectedObjectError
        - Raised when the provided track object does not have a "bars" attribute (i.e., hasattr(track, "bars") is False).
        - The exception message is formatted to include the string representation of the passed-in track.

    Additionally, if the Composition instance does not expose the expected attributes (for example, if self.tracks does not exist or is not a mutable sequence), a built-in exception such as AttributeError or TypeError may be thrown by the underlying operations (these are not explicitly raised by this method but can surface if the Composition object is malformed).

## State Changes:
Attributes READ:
    - self.tracks (read to compute the index of the newly added track via len(self.tracks))
Attributes WRITTEN / MUTATED:
    - self.tracks: the provided track object is appended to this list (the list is mutated; the track reference is stored as-is).
    - self.selected_tracks: replaced with a new single-element list containing the integer index of the newly appended track (value is len(self.tracks) - 1 after append).

## Constraints:
Preconditions:
    - The caller must supply an object with a "bars" attribute (otherwise UnexpectedObjectError is raised).
    - The Composition instance must have a mutable sequence assigned to self.tracks (e.g., list) and an attribute self.selected_tracks that can be assigned; otherwise, attribute or type errors may occur.

Postconditions:
    - After successful return, the supplied track is present as the last element of self.tracks.
    - self.selected_tracks is set to a list with exactly one integer equal to the index of that new last element (0-based).
    - No other tracks are selected (previous contents of self.selected_tracks are discarded).

## Side Effects:
    - Mutates the composition instance in memory: appends to self.tracks and overwrites self.selected_tracks.
    - Does not perform any I/O, external service calls, or deep-copying of the provided track; the original track object is stored by reference.

### `mingus.containers.composition.Composition.add_note` · *method*

## Summary:
Adds a note-like object to every track referenced by the composition's selected_tracks, mutating those Track objects (their bars).

## Description:
Known callers and usage contexts:
- Composition.__add__: the Composition class overloads +; when a non-Track value is added to a Composition instance, Composition.__add__ delegates to this method. This allows expressions like composition + "C-4" to add notes to the currently selected tracks.
- Typical usage: after creating a composition and adding one or more Track objects (via add_track or __add__), callers add notes to the composition to place them into the currently selected track(s). selected_tracks is updated when tracks are added (add_track selects the newly added track).

Why this is a separate method:
- The method centralizes the logic for adding a note to every selected track (loop and delegation to the track-level addition). This keeps track-selection handling separated from Track.add_notes logic and enables Composition.__add__ to dispatch uniformly for non-Track values.

## Args:
note (object): The object describing what to add to each selected track. Allowed / commonly-accepted forms (delegated to Track.__add__/add_notes):
- A string (e.g., "C-4") or other string-like note/chord representation — Track will treat string-like values as notes/chords to be placed.
- An object exposing a `notes` attribute (e.g., a NoteContainer) — Track will treat this as a collection of notes to add.
- An object exposing a `bar` attribute (e.g., a Bar) — Track.__add__ will interpret this as a whole bar to append.
The method does not validate the note type itself; it simply forwards the value to each selected Track for handling.

## Returns:
None. The method performs side-effecting updates on Track instances and does not return a value.

## Raises:
This method does not raise exceptions explicitly, but several exceptions may propagate from underlying operations:
- IndexError: If any entry in self.selected_tracks is an out-of-range index for self.tracks, the attempt to index self.tracks[n] will raise IndexError.
- TypeError: If elements of self.selected_tracks are of an invalid type for list indexing (e.g., a non-integer object), indexing may raise TypeError.
- InstrumentRangeError (propagated from Track.add_notes): If a Track has an associated instrument and that instrument cannot play the requested note(s), Track.add_notes may raise InstrumentRangeError.
- Any other exceptions raised by Track.__add__/add_notes or Bar.place_notes may also propagate unchanged.

## State Changes:
Attributes READ:
- self.selected_tracks: iterated to determine which tracks receive the note(s).
- self.tracks: indexed to obtain each target Track instance.

Attributes WRITTEN / Mutated:
- self.tracks[n] (for each n in self.selected_tracks): the method delegates to the Track's addition logic which mutates the Track (for example, appending bars or placing notes inside existing bars). The Composition object's top-level attributes (self.tracks list reference and self.selected_tracks) are not reassigned by this method.

## Constraints:
Preconditions:
- self.selected_tracks should be a sequence of indices intended to reference entries in self.tracks (typically integers). Each such index must correspond to an existing Track in self.tracks to avoid IndexError.
- Each targeted element self.tracks[n] must be a Track-like object that supports addition of the provided note-like value (i.e., implements the behaviors handled by Track.__add__/add_notes).

Postconditions:
- For every valid index n present in self.selected_tracks, the corresponding Track instance at self.tracks[n] has been updated to include the provided note-like value (e.g., notes placed into bars or a bar appended).
- self.selected_tracks and the self.tracks list object remain the same objects (their references are unchanged); only the internal state of the Track instances is modified.

## Side Effects:
- In-place mutation of Track instances (their bars/notes). No I/O or external service calls are performed.
- If selected_tracks contains duplicate indices, the note-like value will be added once per occurrence (potentially duplicating the addition on a single track).
- If selected_tracks is empty, the method performs no operations.

## Examples:
- Adding a string note to the currently selected tracks:
    composition.add_note("C-4")
  or using operator dispatch:
    composition + "C-4"
- Adding a NoteContainer or a full Bar object will be forwarded to Track and handled according to Track's addition semantics.

### `mingus.containers.composition.Composition.set_title` · *method*

## Summary:
Sets the composition's title and subtitle on the object, replacing any previous values and affecting the composition's persisted metadata state.

## Description:
Known callers:
- Composition.reset(): calls set_title() with no arguments to restore title/subtitle defaults during a reset of the composition.
- External code (client/user code) may call this method to update the composition metadata before serialization, display, or export; such callers are not present in this module but are typical usage contexts.

Lifecycle / context:
- Invoked when the composition's metadata must be initialized or updated (e.g., during a reset operation or when a user supplies new metadata prior to saving or rendering).
- This logic is provided as a dedicated method so both internal operations (reset) and external callers can update title and subtitle in a single, consistent operation rather than duplicating assignments in multiple places.

## Args:
    title (str, optional): New title to assign to the composition. Defaults to "Untitled".
    subtitle (str, optional): New subtitle to assign to the composition. Defaults to "" (empty string).

Notes on types and values:
- The implementation performs no type checking; while strings are intended, any value may be assigned and will be stored as-is.
- There is no restriction on string contents (length, characters); callers are responsible for validation if required.

## Returns:
    None

The method does not return a value; it performs an in-place update of the object's attributes.

## Raises:
    None raised by this method.

There is no exception handling or explicit error raising in this method. If assignment were to fail due to unusual environment constraints (very unlikely in normal Python objects), Python's normal exceptions (e.g., AttributeError) would propagate.

## State Changes:
Attributes READ:
- None explicitly read by the method (it does not consult existing attribute values).

Attributes WRITTEN:
- self.title: set to the provided title argument
- self.subtitle: set to the provided subtitle argument

## Constraints:
Preconditions:
- self must be a Composition instance (or an object with writable attributes title and subtitle). The class defines class-level defaults for title and subtitle, so these attributes normally exist.
- No other preconditions are enforced by the method.

Postconditions:
- After the call, self.title is exactly the passed title value.
- After the call, self.subtitle is exactly the passed subtitle value.
- No other attributes of self are modified by this method.

## Side Effects:
- Mutates only the composition object (self) by assigning to its title and subtitle attributes.
- No I/O, no network calls, and no modification of objects outside self (unless the passed arguments themselves are mutable objects and shared elsewhere, in which case those objects are not copied).

### `mingus.containers.composition.Composition.set_author` · *method*

## Summary:
Assigns author metadata to the Composition instance by updating the instance attributes that store author name and email.

## Description:
Known callers and context:
    - No direct callers were identified in the provided source fragment. Typically this method is invoked during composition creation, metadata update flows, or when loading/parsing metadata from external sources into a Composition object.
Why this is a separate method:
    - Centralizes the assignment of author-related metadata in one place to improve API clarity and to provide a single extension point if future validation, normalization, or side-effects (e.g., change events) are added. Keeping the operation as a method makes higher-level code more readable (composition.set_author(...)) compared to setting attributes directly.

## Args:
    author (str, optional): The display name of the author. Defaults to the empty string "". The method does not enforce type checking; any value will be assigned as-is.
    email (str, optional): The author's email address. Defaults to the empty string "". The method does not validate email format.

## Returns:
    None

## Raises:
    None
    - Although UnexpectedObjectError is imported in the module, this method does not raise it or any other exception.

## State Changes:
    Attributes READ :
        - None (the method does not read any existing instance attributes)
    Attributes WRITTEN :
        - self.author: set to the value of the author argument
        - self.email: set to the value of the email argument

## Constraints:
    Preconditions:
        - The caller should expect that the object is a Composition instance or similar object that permits assignment to attributes named author and email.
        - No guarantee that arguments are strings; if non-string values are passed they will be stored without conversion or validation.
    Postconditions:
        - After invocation, self.author is equal to the provided author argument, and self.email is equal to the provided email argument (including when those arguments are the default empty strings or other non-string values).

## Side Effects:
    - Mutates only the caller object (self) by assigning to its author and email attributes.
    - Does not perform any I/O, network calls, logging, or interactions with external services.
    - No validation, normalization, or triggering of events is performed by this method.

### `mingus.containers.composition.Composition.__add__` · *method*

## Summary:
Dispatches the addition operator for a Composition: if given a Track-like object (has attribute "bars") it appends it as a new track; otherwise it forwards the value to the currently selected track(s) as a note. The call updates the composition's tracks and selection when a track is added and mutates contained Track objects when a note is added.

## Description:
This method implements operator-based convenience for building or editing a Composition using the + operator. Typical callers are user code or higher-level composition-building routines that do either:
- composition + track_object  (to add a whole Track to the composition during composition creation or editing)
- composition + note_object   (to append a note to whichever track(s) are currently selected)

Lifecycle / pipeline context:
- Used during composition construction and interactive editing where shorthand syntax (composition + ...) is desirable.
- It is the entry point for two distinct behaviors (add a Track vs add a Note) and centralizes the dispatch logic.

Why a separate method:
- Overloading __add__ keeps the Pythonic operator syntax while delegating concrete behavior to add_track and add_note. This separation keeps type/behavior checks and side-effect logic localized in those helper methods rather than in multiple call sites.

## Args:
    value (object): Either
        - a Track-like object: any object with a "bars" attribute. When such an object is provided, it will be treated as a Track and appended to self.tracks; or
        - a Note-like object: any value acceptable to Track.__add__ (the Track class' addition semantics). When provided, it will be forwarded to selected track(s).

    There is no default; callers must pass a value.

## Returns:
    None
    - Both add_track and add_note do not return a value (implicitly return None). __add__ returns the same (None) in both branches.
    - No meaningful return value is produced; the effect is performed by mutating the composition or its tracks.

## Raises:
    UnexpectedObjectError:
        - Raised by add_track if the object passed as a track does not actually provide the required "bars" attribute.
        - Under normal execution via __add__, this is unlikely because __add__ first checks hasattr(value, "bars") before calling add_track. However, if the object loses or proxies that attribute between the hasattr check and add_track's guard, add_track may raise UnexpectedObjectError.

    IndexError:
        - May be raised when adding a note if self.selected_tracks contains an index that is out of range for self.tracks. The add_note implementation performs self.tracks[n] + note for each n in self.selected_tracks; invalid indices propagate IndexError from list indexing.

    Any exception raised by Track.__add__:
        - When forwarding a note to tracks (self.tracks[n] + note), any exception that Track.__add__ raises (for example, on invalid note types or values) will propagate through __add__.

## State Changes:
Attributes READ:
    - self.selected_tracks (read by add_note to determine target track indices)
    - self.tracks (read by add_note to access target tracks)

Attributes WRITTEN:
    - self.tracks (append a Track object when adding a track)
    - self.selected_tracks (set to the index of the newly appended track when adding a track)

Other mutations:
    - When adding a note, the method invokes Track.__add__ on one or more Track objects stored in self.tracks; those Track instances are likely to be mutated (notes appended) even though the composition's tracks list object itself is not reassigned.

## Constraints:
Preconditions:
    - The Composition instance must be initialized (self.tracks and self.selected_tracks should exist). The class constructor ensures self.tracks is a list via empty().
    - If adding a track: the value should be a Track-like object exposing a "bars" attribute; otherwise add_track will raise UnexpectedObjectError.
    - If adding a note: self.selected_tracks should contain valid indices into self.tracks; otherwise an IndexError may be raised.

Postconditions:
    - If a Track-like object was added:
        - len(self.tracks) increases by 1.
        - self.selected_tracks is set to a single-item list containing the index of the newly added track (len(self.tracks) - 1).
    - If a note-like object was added:
        - self.tracks retains the same length.
        - One or more Track instances (those at indices in self.selected_tracks) have been updated by their own addition logic (Track.__add__), which may append the note or otherwise mutate the track's internal state.

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutates composition state (self.tracks and self.selected_tracks) when adding a Track.
    - Mutates Track objects contained in self.tracks when adding a note (via Track.__add__).
    - Exceptions raised by underlying operations (UnexpectedObjectError, IndexError, or Track.__add__ exceptions) propagate to the caller.

### `mingus.containers.composition.Composition.__getitem__` · *method*

## Summary:
Return item(s) from the composition's internal track list at the given index or slice; this is a non-mutating accessor that exposes stored Track-like objects.

## Description:
This method implements Python sequence-style access for a Composition by delegating to its internal list (self.tracks). It exists so external code can use idiomatic bracket notation (composition[i] or composition[i:j]) and so other code can treat Composition like a sequence without directly accessing the tracks attribute.

Known callers / usage contexts:
- External code that reads or inspects tracks for editing, rendering, playback preparation, or testing.
- Any code that expects standard sequence behavior (indexing, slicing, iteration) when interacting with a Composition instance.

This logic is provided as a dedicated method to centralize and standardize access semantics (including slices and negative indices) rather than requiring direct list manipulation in multiple places.

## Args:
    index (int, slice, or index-like object):
        - Integer: zero-based index of the track to return. Negative indices follow standard Python semantics (e.g., -1 returns the last track).
        - Slice: returns a new list of tracks corresponding to the slice.
        - Index-like objects that implement __index__ are accepted (e.g., numpy.int64), following Python list indexing rules.
        - No default; argument is required.

## Returns:
    Track-like object or list[Track-like]:
        - Integer index: returns the single stored item at that index (typically a Track instance — objects added via add_track are expected to have a 'bars' attribute).
        - Slice: returns a new Python list containing the selected items (not a Composition).
        - Returned objects are direct references to the items in self.tracks (mutating the returned object will mutate the stored object).

## Raises:
    IndexError:
        - If an integer index is out of bounds for self.tracks (this is the behavior of list.__getitem__).
    TypeError:
        - If index is of an unsupported type for list indexing (for example, a float or other non-indexable object).
    Notes:
        - This method does not raise UnexpectedObjectError; add_track performs type checks when tracks are inserted.

## State Changes:
    Attributes READ:
        - self.tracks
    Attributes WRITTEN:
        - None (no writes to self or its attributes)

## Constraints:
    Preconditions:
        - self.tracks must be a Python list (Composition.empty() initializes it to []).
        - Items in self.tracks are expected to be Track-like (add_track enforces presence of a 'bars' attribute), but __getitem__ does not validate the contents.
    Postconditions:
        - No mutation of self or self.tracks by this call.
        - Caller obtains either a reference to an existing stored object (integer index) or a new list of references (slice).

## Side Effects:
    - None. No I/O, network activity, or mutation of external objects is performed by this method itself (aside from the caller possibly mutating the returned object).

## Examples:
    - Retrieve the first track: composition[0]  (raises IndexError if there are no tracks)
    - Get the last track using a negative index: composition[-1]
    - Get tracks 1 through 3 (exclusive upper bound): composition[1:3]  (returns a list)
    - Using an index-like object: idx = some_index_like; composition[idx]  (works if idx implements __index__)

### `mingus.containers.composition.Composition.__setitem__` · *method*

## Summary:
Assigns a value into the composition's internal track container at the given index or slice, mutating the stored tracks (replaces one or more elements of self.tracks).

## Description:
- Known callers and contexts:
    - External client code using Python assignment syntax: composition[i] = value or composition[i:j] = iterable. This is the canonical usage when replacing an existing track or replacing a range of tracks during editing, import/deserialization, or programmatic modifications of a Composition.
    - Internal code that needs direct indexed replacement of tracks (for example patches, undo/redo, or transformations that operate by replacing elements).
    - Note: add_track uses append and performs runtime type checking; that code path does not call __setitem__.
- Lifecycle/context:
    - Invoked at any time after a Composition instance has been initialized (Composition.__init__ sets up self.tracks). Typically used during edit/modify phases of composition construction or manipulation.
- Why this is a separate method:
    - Implements the Python sequence assignment protocol so Composition behaves like a mutable sequence (supports bracket assignment). Centralizing this logic lets external code use idiomatic sequence operations without touching the internal tracks attribute directly and makes the behavior consistent with list assignment semantics.

## Args:
    index (int, slice, or index-like):
        - Integer: zero-based index specifying the single element to replace. Negative indices follow Python semantics (e.g., -1 refers to the last element).
        - Slice: a slice object specifying a range to replace. Right-hand value must be an iterable appropriate for slice assignment.
        - Index-like objects that implement __index__ are accepted.
    value (object or iterable):
        - For integer index: any object may be assigned; by convention and for correct downstream behavior this should be a Track-like object (an object with a 'bars' attribute).
        - For slice assignment: an iterable containing objects to insert in place of the slice; items should typically be Track-like objects.

## Returns:
    None
    - Assignment operations in Python do not return a value; this method performs the mutation and returns None implicitly.

## Raises:
    IndexError:
        - If an integer index is out of range for the current self.tracks (delegated from Python list behavior).
    TypeError:
        - If index is of an unsupported type for list indexing (e.g., a float), or if a non-iterable is provided for slice assignment.
    Any exception raised by underlying list assignment semantics (propagated unchanged), for example when the right-hand value is invalid for the requested slice assignment.

    Notes:
    - This method does not perform type validation of the assigned value(s). It does not raise UnexpectedObjectError; code that requires validation should call add_track or perform checks before assignment.

## State Changes:
- Attributes READ:
    - self.tracks (used to locate and perform the assignment)
- Attributes WRITTEN:
    - The contents of self.tracks are modified:
        - For integer index: the element at the given index is replaced with value (self.tracks[index] becomes value).
        - For slice assignment: the sequence of elements covered by the slice is replaced by the contents of the provided iterable; this may change the length of self.tracks.
    - The self.tracks attribute reference itself is not replaced by this method (the same list object is mutated).

## Constraints:
- Preconditions:
    - self.tracks must be present and be a mutable sequence that supports item assignment (Composition.__init__ sets self.tracks to a list; callers should ensure the instance has been initialized).
    - For meaningful composition semantics, values assigned should be Track-like objects (i.e., objects with a 'bars' attribute). However, this method does not enforce that.
    - For slice assignment: the provided value must be iterable.
- Postconditions:
    - After successful return:
        - For integer index: self.tracks[index] refers to the assigned value.
        - For slice assignment: the slice range is replaced by the provided iterable's elements and len(self.tracks) is updated accordingly.
    - No other Composition attributes are modified (e.g., selected_tracks remains unchanged).

## Side Effects:
- Mutations:
    - Mutates the internal list self.tracks (replaces elements or ranges inside it).
    - If value or elements of the assigned iterable are references to external objects, those references are stored — no defensive copy is made.
- I/O / external service calls:
    - None. The method performs only in-memory mutations and delegates to Python list semantics.
- Warnings:
    - Because __setitem__ does not validate that assigned objects are Track-like, assigning incompatible objects can break assumptions elsewhere in the codebase (for example, code that expects each track to have a 'bars' attribute). Use add_track when you want the class to enforce Track-like validation.

### `mingus.containers.composition.Composition.__len__` · *method*

## Summary:
Return the number of tracks contained in this composition as an integer; does not modify the composition.

## Description:
This method is the length protocol implementation used by Python's built-in len() when called with a Composition instance (i.e., len(composition)). It provides a single, authoritative way to obtain the current count of tracks stored on the instance.

Known callers and contexts:
- The Python built-in len(composition) invokes this method whenever code needs the composition's size (for example: loops, UI displays, validations, or conditional logic that depends on the number of tracks).
- Any internal or external code that queries how many tracks the composition contains will call this implicitly via len() or explicitly via composition.__len__().

Why this is a separate method:
- Implements the Python sequence/collection protocol so Composition integrates with len() and other language features.
- Encapsulates the representation detail (that track objects are stored in self.tracks) behind a stable API; callers need not access self.tracks directly.

## Args:
    None

## Returns:
    int: The number of track objects in the composition.
    - Always a non-negative integer.
    - Returns 0 when the composition contains no tracks (self.tracks is an empty sequence).

## Raises:
    TypeError: If self.tracks does not support the built-in len() operation (for example, if it is None or an object without __len__). This exception is raised by Python's len() and propagated unchanged.

## State Changes:
    Attributes READ:
        - self.tracks

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Composition instance should be properly initialized (typically by calling Composition()), which sets self.tracks to a list.
        - self.tracks must be an object that supports len() (sequence or other object implementing __len__).

    Postconditions:
        - The composition object is unchanged by this call.
        - The return value equals the length of the current self.tracks sequence at the time of the call.

## Side Effects:
    - None. This method performs no I/O, no external calls, and does not mutate the Composition or any external object.

### `mingus.containers.composition.Composition.__repr__` · *method*

## Summary:
Returns a flat string representation of the composition by concatenating the string representations of each track in iteration order. The method does not modify the Composition object.

## Description:
- Known callers and context:
    - There are no explicit internal callers of this method in the Composition class source. This method is invoked implicitly by Python when repr(composition_instance) is called and, because Composition does not define __str__, also when str(composition_instance) is used in printing or logging contexts. It will therefore be used during debugging, logging, or any place the textual representation of a Composition object is requested.
- Why this logic is its own method:
    - Implements the Python object representation protocol (repr) in a single place so callers (built-in repr, logging, interactive REPL, etc.) receive a consistent textual representation of the composition. Centralizing the formatting here avoids duplicating track-concatenation logic across the codebase and lets subclasses or future changes override only this display behavior.

## Args:
    None

## Returns:
    str: A string formed by appending str(x) for each track x in self.tracks, in the order provided by iteration.
    - If self.tracks is empty, returns an empty string "".
    - The exact contents depend on each track's __str__ implementation.

## Raises:
    - No exceptions are raised explicitly by this method.
    - Runtime errors that may propagate:
        * TypeError: If self.tracks is not iterable, iteration will raise a TypeError.
        * Any exception raised inside a track's __str__ implementation will propagate to the caller.

## State Changes:
    - Attributes READ:
        * self.tracks — iterated to collect track string representations.
    - Attributes WRITTEN:
        * None — the method does not modify any attributes of self.

## Constraints:
    - Preconditions:
        * self.tracks must be an iterable of objects (the Composition class initializes this as a list).
        * Each element in self.tracks should be suitable for conversion to str() (i.e., its __str__ should not raise unless that propagation is acceptable).
    - Postconditions:
        * The Composition instance remains unchanged (no attributes modified).
        * A string reflecting the current sequence of tracks is returned.

## Side Effects:
    - This method performs no I/O and does not call external services.
    - Note: calling str(x) on each track may execute code inside track.__str__ that has its own side effects; those side effects are not caused by this method itself but will occur during its execution if present.

