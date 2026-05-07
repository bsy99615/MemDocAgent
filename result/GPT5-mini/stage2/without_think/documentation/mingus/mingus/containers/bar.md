# `bar.py`

## `mingus.containers.bar.Bar` · *class*

*No documentation generated.*

### `mingus.containers.bar.Bar.__init__` · *method*

## Summary:
Initializes a Bar instance by setting its musical key and meter and resetting internal state so the bar starts empty and ready to accept notes.

## Description:
This constructor is called whenever a new Bar object is created (e.g., Bar(), or when other container/creator code instantiates a bar to represent a measure). Typical lifecycle usage: invoked at the moment a measure is constructed or when code explicitly reconstructs a bar. The method centralizes three related initialization steps:
- Normalizing the provided key to a keys.Key object when a string is given.
- Delegating meter validation and length computation to set_meter.
- Resetting the internal note storage and beat cursor via empty.

Separating these steps into set_meter and empty keeps validation and state-reset logic reusable (set_meter can be called later to change meter, empty can be called to clear the bar) and keeps the constructor focused on composition of those behaviors instead of duplicating logic.

## Args:
    key (str | keys.Key, optional): The musical key for the bar. If a string (e.g., "C", "Am"), it is converted to a keys.Key instance using keys.Key(key). If a keys.Key instance is provided it is used as-is. Defaults to "C".
    meter (tuple[int, int], optional): A 2-tuple representing the time signature (number_of_beats, beat_unit), e.g., (4, 4). The second element (beat unit) must be a valid beat duration recognized by the meter utilities, or the special tuple (0, 0) to represent an open/undefined-length bar. Defaults to (4, 4).

## Returns:
    None: Constructors do not return a value. The method initializes instance state.

## Raises:
    MeterFormatError: Propagated from set_meter if the provided meter tuple is not an accepted format (i.e., the beat duration is invalid and meter is not exactly (0, 0)). The exact condition is raised inside set_meter when meter[1] is not a valid beat duration.

## State Changes:
Attributes READ:
    None of self's attributes are read prior to assignment within __init__.

Attributes WRITTEN:
    self.key
        - Set to a keys.Key instance if a string was supplied, otherwise set to the provided value.
    self.meter (written by set_meter)
        - Set to the validated meter tuple (e.g., (4, 4)) or (0, 0) for an open bar.
    self.length (written by set_meter)
        - Set to the bar length in whole-note units (meter[0] * (1.0 / meter[1])) or 0.0 for (0, 0).
    self.bar (written by empty)
        - Initialized to an empty list representing no contained notes/entries.
    self.current_beat (written by empty)
        - Initialized to 0.0 representing the insertion cursor at the start of the bar.

Note: set_meter and empty perform the actual assignments for meter/length and bar/current_beat respectively; __init__ composes those operations.

## Constraints:
Preconditions:
    - key must be either a string (one of six.string_types) or an object acceptable as a keys.Key argument / a keys.Key instance.
    - meter must be a 2-tuple with integers (number_of_beats, beat_unit). The beat_unit (meter[1]) must be recognized as a valid beat duration by the meter module, unless meter == (0, 0).

Postconditions:
    - self.key is set: if key was a string it's converted to keys.Key(key); otherwise the provided object is assigned.
    - self.meter and self.length reflect the validated meter after calling set_meter.
    - self.bar is an empty list and self.current_beat == 0.0 after calling empty.
    - No notes are present in the bar and the bar is ready to accept new note placements.

## Side Effects:
    - May instantiate a keys.Key object when a string key is passed (object creation).
    - May raise MeterFormatError via set_meter if meter validation fails.
    - No I/O, network, or external system calls are performed.
    - Mutates only the instance (self) by setting the attributes listed above; no global state is modified.

### `mingus.containers.bar.Bar.empty` · *method*

## Summary:
Resets the Bar to an initial, empty state by clearing its internal note list and resetting the beat counter; returns the new (empty) internal list.

## Description:
This method clears the bar's contents and resets its current beat to the start of a measure. It is intended to be called whenever the Bar must be reinitialized between measures, when discarding existing contents, or prior to reusing a Bar object for new input. No external resources are accessed.

Known callers and context:
- The source code provided does not include any explicit internal callers of this method. It is intended for use by higher-level code that manages measure lifecycle (e.g., when beginning a new bar, undoing input, or resetting state during parsing or generation).
- Typical lifecycle stage: invoked at the start of a new measure or when the existing contents of the Bar should be discarded and the beat/time position reset.

Why this is a separate method:
- Encapsulates the reset logic (clearing stored notes and resetting beat position) in one place so callers do not need to manipulate internal attributes directly.
- Keeps state-reset semantics explicit and consistent across the codebase and makes it easy to extend reset behavior later (e.g., to trigger events) without changing call sites.

## Args:
    None

## Returns:
    list: The list object now assigned to self.bar. After the call this list is empty ([]). The method returns the actual list stored on the instance (not a copy).

## Raises:
    None

## State Changes:
    Attributes READ:
        - None (the method does not read any existing attribute values)

    Attributes WRITTEN:
        - self.bar (assigned to a new empty list [])
        - self.current_beat (assigned the float value 0.0)

## Constraints:
    Preconditions:
        - The caller must have a valid Bar instance (self must be a correctly initialized object). No other preconditions are required.
        - Any external references to the previous self.bar list will continue to reference the old list object; callers expecting the bar contents to be cleared in-place should not rely on previous references.

    Postconditions:
        - self.bar is an empty list (equal to []).
        - self.current_beat equals 0.0.
        - The returned value is the same object referenced by self.bar after assignment.

## Side Effects:
    - Mutates the Bar instance by overwriting its bar attribute and current_beat attribute.
    - Does not perform any I/O, logging, or external service calls.
    - Does not raise exceptions.

### `mingus.containers.bar.Bar.set_meter` · *method*

## Summary:
Validates a two-element time-signature tuple and updates the Bar instance's meter and length fields; sets a zero-length sentinel for (0, 0) or raises MeterFormatError for invalid denominators.

## Description:
This method enforces that the provided meter argument is a two-element tuple-like object (numerator, denominator), verifies the denominator using a module-level validator, and updates the Bar instance state when validation succeeds.

- Exact call performed by the implementation: calls _meter.valid_beat_duration(meter[1]) to validate the denominator.
- On valid denominator: sets self.meter to (numerator, denominator) and computes self.length as numerator * (1.0 / denominator).
- Special-case: if the argument equals the tuple (0, 0), the method treats this as a zero-length meter, sets self.meter to (0, 0) and self.length to 0.0.
- On any other invalid denominator value, raises MeterFormatError with a descriptive message.

Known callers and context:
- No specific callers provided in the snapshot. Typical usage is during Bar initialization or when a higher-level API updates a Bar's meter before scheduling or rendering notes.
- Lifecycle stage: invoked at the point a Bar's time signature must be validated and made consistent across the object's state.

Why this is a separate method:
- Centralizes the validation and the arithmetic for computing a bar's floating length.
- Keeps callers from repeating the power-of-two denominator check and ensures atomic updates to both meter and length.

## Args:
    meter (sequence or tuple of length >= 2)
        - Expected form: (numerator, denominator)
        - numerator (int): number of beats per bar (typical positive integers). Not further validated by this method beyond being stored and used arithmetically.
        - denominator (int): beat unit; MUST be a positive power of two (1, 2, 4, 8, ...), as validated by _meter.valid_beat_duration.
        - The method expects to be able to index meter at positions 0 and 1 (i.e., meter[0], meter[1]).
        - The method message and behavior imply callers should provide a tuple, though any sequence-like object with indexing will work.

## Returns:
    None
    - The method performs in-place updates to the Bar instance and does not return a value.

## Raises:
    MeterFormatError
        - Condition: _meter.valid_beat_duration(meter[1]) is False AND the provided meter is not exactly equal to the tuple (0, 0).
        - Exact message raised by the implementation:
          "The meter argument '%s' is not an understood representation of a meter. Expecting a tuple." % meter

    TypeError or IndexError (propagated built-ins)
        - Condition: the provided meter is not subscriptable (meter[1] access raises TypeError) or does not provide two elements (meter[1] raises IndexError).
        - These errors are not caught by the method and will propagate to the caller.

    Note on numeric denominators:
        - If denominator is a non-integer numeric type, the used validator (_meter.valid_beat_duration) expects integer-like inputs. Passing floats or other numerics may lead to undefined behavior in the validator (including the potential for long-running or non-terminating checks). Prefer integer denominators.

## State Changes:
    Attributes READ:
        - None of the Bar instance attributes are read prior to modification by this method.

    Attributes WRITTEN:
        - self.meter: set to (numerator, denominator) when validation succeeds, or to (0, 0) for the zero-length sentinel.
        - self.length: set to numerator * (1.0 / denominator) when validation succeeds, or to 0.0 when meter == (0, 0).

## Constraints:
    Preconditions:
        - meter must be indexable at positions 0 and 1.
        - meter[1] (denominator) should be a non-negative integer that is a power of two when not using the sentinel (0, 0).
        - Callers should avoid passing fractional denominators or unsupported numeric types to avoid undefined validator behavior.

    Postconditions:
        - On normal return (no exception):
            - self.meter equals the two-tuple (numerator, denominator) or (0, 0).
            - self.length equals float(numerator * (1.0 / denominator)) or 0.0 for (0, 0).
        - On exception, no partial update occurs because assignment to self.meter and self.length happens only after successful validation in the first branch or after the explicit (0, 0) match.

## Side Effects:
    - Mutates only the Bar instance (self.meter and self.length).
    - Calls the module-level validator _meter.valid_beat_duration on the denominator; the validator is expected to be pure and side-effect-free.
    - No I/O, network, or external service interactions.

## Implementation details (precise control flow to reimplement):
    1. Attempt to read denominator = meter[1]. If this fails, allow the resulting TypeError/IndexError to propagate.
    2. Call _meter.valid_beat_duration(denominator).
        - If True:
            a. Set self.meter = (meter[0], meter[1])
            b. Compute self.length = meter[0] * (1.0 / meter[1]) ensuring floating-point division.
            c. Return None.
        - If False:
            a. Check if meter == (0, 0). If so:
                i. Set self.meter = (0, 0)
                ii. Set self.length = 0.0
                iii. Return None.
            b. Otherwise raise MeterFormatError with the exact message:
                "The meter argument '%s' is not an understood representation of a meter. Expecting a tuple." % meter

## Examples (textual):
    - Valid standard meter:
        Input: meter = (4, 4)
        Effect: self.meter becomes (4, 4); self.length becomes 4 * (1.0 / 4) == 1.0

    - Special zero-length meter:
        Input: meter = (0, 0)
        Effect: self.meter becomes (0, 0); self.length becomes 0.0

    - Invalid denominator:
        Input: meter = (3, 3)
        Effect: _meter.valid_beat_duration(3) returns False; meter != (0, 0); MeterFormatError is raised with the exact string shown above.

    - Malformed argument:
        Input: meter = 4  (an int)
        Effect: accessing meter[1] raises TypeError; this exception propagates to the caller.

### `mingus.containers.bar.Bar.place_notes` · *method*

## Summary:
Attempts to append a note (or rest) entry to the bar at the current beat, converting the input to a NoteContainer when appropriate, and advances the bar's current beat if the entry fits within the bar's remaining length.

## Description:
Known callers and context:
    - Bar.place_rest(duration): calls place_notes(None, duration) to add a rest.
    - Bar.__add__(note_container): calls place_notes(note_container, self.meter[1]) when adding via the + operator.
    - External code that builds a Bar by sequentially adding notes or rests will call this method to place an element at the next available beat.
Lifecycle stage:
    - Invoked while constructing or editing a Bar to add a single musical event (note(s) or rest) at the bar's next unoccupied beat.
Why this is a separate method:
    - Encapsulates three responsibilities used in multiple places: normalizing the incoming notes argument into a NoteContainer when applicable, checking available space against the bar length, and performing the atomic update (append entry and advance current_beat). Centralizing these behaviors avoids duplication and ensures consistent bookkeeping for all code paths that add entries to the bar.

## Args:
    notes (NoteContainer | object | str | list | None):
        - Allowed values:
            * An object that already exposes a .notes attribute (treated as a ready NoteContainer and used as-is).
            * An object with a .name attribute (converted by calling NoteContainer(notes)).
            * A string (converted by calling NoteContainer(notes)).
            * A list (converted by calling NoteContainer(notes)).
            * None to represent a rest (no conversion attempted; None is stored as the entry's payload).
        - Semantics: The third element of the stored bar entry will be either the passed NoteContainer-like object, a newly constructed NoteContainer, or None.
    duration (int | float):
        - A numeric, non-zero beat denominator used to compute the beat length increment as 1.0 / duration.
        - Typical values are positive integers (e.g., 4 for a quarter-note when meter denominator is 4).
        - Not validated by this method beyond being used in the division; callers must pass a valid, non-zero numeric duration.

## Returns:
    bool:
        - True if the entry was appended and current_beat advanced.
        - False if there was insufficient remaining space in the bar (and no state change was performed).
        - Note: when the bar's length is 0.0 (unmetered bar), the method will allow appending entries and return True (subject to division by duration as described in Raises).

## Raises:
    ZeroDivisionError:
        - If duration == 0, evaluating 1.0 / duration raises ZeroDivisionError. This can occur even when the bar has length 0.0 because the division is evaluated before the 'or self.length == 0.0' short-circuit check.
    TypeError:
        - If duration is not a numeric type, evaluating 1.0 / duration may raise TypeError.
    Any exception raised by NoteContainer(notes):
        - If conversion is attempted (when notes has .name, is a string, or is a list) the NoteContainer constructor may raise its own exceptions for invalid inputs; these propagate up to the caller.

## State Changes:
    Attributes READ:
        - self.current_beat (reads current beat to compute start and available space)
        - self.length (reads bar length to check if there is space or if unmetered)
    Attributes WRITTEN:
        - self.bar (appends a new entry: [start_beat, duration, notes_or_NoteContainer_or_None])
        - self.current_beat (incremented by 1.0 / duration when append succeeds)

## Constraints:
    Preconditions:
        - duration must be a non-zero numeric value (preferably a positive number representing the denominator of the beat).
        - notes should be either:
            * a NoteContainer-like object (has .notes), or
            * a note-like object (has .name), or
            * a string or list that NoteContainer can accept, or
            * None to represent a rest.
        - The Bar object's set_meter(...) should have been used to set a meaningful self.length if meter semantics are required; if self.length == 0.0 the bar is treated as unmetered and entries are always allowed (subject to successful division).
    Postconditions:
        - If the method returns True:
            * A new entry [start_beat, duration, notes_or_converted] has been appended to self.bar, where start_beat is the value of self.current_beat prior to this call.
            * self.current_beat has been increased by exactly 1.0 / duration.
        - If the method returns False:
            * No modification to self.bar or self.current_beat is performed.
        - If an exception is raised during conversion or division:
            * No guarantee of state changes — exceptions occur before the append (the division is evaluated before the append and the conversion happens before the division), so the bar remains unchanged unless the exception originates from NoteContainer and it mutates external state (NoteContainer constructors typically do not mutate the Bar).

## Side Effects:
    - Mutates the Bar instance by appending to self.bar and updating self.current_beat when successful.
    - No I/O or external service calls.
    - May construct a new NoteContainer instance (side effect: allocation of an object and any exceptions it may raise).
    - When notes is None, the stored entry's payload is None (a rest). Other Bar methods that iterate over entries often expect a NoteContainer; storing None may lead to exceptions if callers do not guard against rests.

## Implementation notes (for reimplementation):
    - Conversion order must match the original: if notes has .notes attribute, do nothing; elif has .name, create NoteContainer(notes); elif is string, create NoteContainer(notes); elif is list, create NoteContainer(notes); otherwise leave notes unchanged.
    - Compute increment = 1.0 / duration. Use this value both for the space check (current_beat + increment <= length) and to advance current_beat when appended.
    - Use the predicate (current_beat + increment <= length) OR (length == 0.0) to decide whether to append; remember that the division is evaluated before the OR short-circuiting.
    - Append entry as a 3-element list: [start_beat, duration, notes_or_converted].
    - Return True on successful append; False otherwise.

### `mingus.containers.bar.Bar.place_notes_at` · *method*

## Summary:
Adds the given notes into the bar's internal slot(s) whose position equals the provided 'at' key, mutating the bar in-place.

## Description:
This method iterates the bar's internal sequence of slots and, for any slot whose position/descriptor equals the provided at value, appends/combines the supplied notes into that slot's note collection using the in-place += operator.

Known callers and typical context:
- Usually invoked when building or editing a Bar to place notes at a particular beat/position; for example, higher-level assembly routines that construct a Bar from note lists or when programmatically adding notes to an existing Bar before rendering or exporting.
- It is part of the Bar's mutation API and is expected to be called during composition or editing stages (not during read-only analysis or rendering).

Why this is a separate method:
- Encapsulates the logic for locating the target slot(s) and performing the in-place combination of notes into the slot. Keeping it separate centralizes the mutation behavior and avoids duplicating indexing/combination logic across callers.

## Args:
    notes (object): A value that can be combined into the slot's existing note collection using the in-place += operator. Commonly a list/tuple of note identifiers or a NoteContainer-like object that supports +=. No implicit copying is performed — the object is added to the existing collection.
    at (object): The position/descriptor to match against each slot's position field (the same type as the slot position). The method compares this value for equality with each slot's position field (x[0]).

## Returns:
    None: The method performs in-place mutation and does not return a value. If no slot matches the provided at value, no mutation occurs.

## Raises:
    No exceptions are explicitly raised by this method.
    - Runtime exceptions may occur if the bar's internal structure is not as expected. For example:
        * TypeError or AttributeError: if a slot's position (x[0]) is not indexable or if x[0][2] does not support the += operation with the provided notes.
        * IndexError: if a slot's position (x[0]) does not have at least three elements (so x[0][2] is out of range).
    These are not raised by the method itself but are natural Python errors that will propagate if the internal data shape is invalid.

## State Changes:
    Attributes READ:
        - self.bar (reads the iterable of slots to find matches)
    Attributes WRITTEN:
        - self.bar (the contents of matching slot entries are mutated because x[0][2] is modified via +=)

## Constraints:
    Preconditions:
        - self.bar must be an iterable of slot-like sequences where each slot variable x provides a position element at x[0].
        - Each position element x[0] must itself be an indexable sequence with at least three elements such that x[0][2] refers to a mutable collection (or an object) that supports in-place addition (+=) with the provided notes argument.
        - The 'at' argument must be comparable (==) to the position elements stored in x[0].
    Postconditions:
        - For every slot in self.bar where slot[0] == at, slot[0][2] has been modified by applying slot[0][2] += notes.
        - No return value (implicitly returns None).
        - If no slot matches, self.bar remains unchanged.

## Side Effects:
    - In-place mutation of internal data: modifies slot[0][2] for matching slots inside self.bar.
    - No I/O, no external service calls, and no global state modification outside of the mutated contents of self.bar.

### `mingus.containers.bar.Bar.place_rest` · *method*

## Summary:
Place a rest of the given duration into the bar by delegating to the bar's note-placement logic; this mutates the bar contents and advances the current beat when placement succeeds.

## Description:
This method is a thin convenience wrapper that calls the bar's generic placement routine with no notes (notes == None). It exists so callers can explicitly request a rest without constructing a NoteContainer.

Known callers:
    - No direct callers were discovered in the available code snapshot. This method is intended to be used by higher-level composition or sequencing code (user code, track builders, or other containers) when inserting rests between or instead of notes.

Typical lifecycle / context:
    - Called during bar construction or editing when a rest (silence) of a particular rhythmic duration needs to be placed at the next available beat within the bar.

Why this is its own method:
    - Improves API clarity and ergonomics: placing a rest is a common, distinct operation from placing notes, so the wrapper makes intent explicit.
    - Keeps insertion semantics centralized in place_notes while exposing a readable public method for rests.

## Args:
    duration (int or float):
        - The rhythmic denominator used to compute the beat increment as 1.0 / duration.
        - Expected to be a positive, non-zero numeric value (commonly integers like 1, 2, 4, 8, 16 representing whole, half, quarter, eighth, sixteenth notes).
        - No default value; caller must provide it.

## Returns:
    bool:
        - True: the rest was placed successfully. Side effects (described below) have been applied.
        - False: the rest would exceed the bar's configured length (self.length != 0.0) and therefore was not placed; no mutation to self.bar or self.current_beat occurs.

## Raises:
    ZeroDivisionError:
        - If duration == 0, the method triggers a division by zero when computing 1.0 / duration.
    TypeError:
        - If duration is not a numeric type that supports division by a float (e.g., passing a non-numeric object), the 1.0 / duration expression will raise a TypeError.
    (No additional exceptions are raised by this wrapper itself; any other exceptions would come from misuse of duration or underlying Python arithmetic.)

## State Changes:
    Attributes READ:
        - self.current_beat: read to determine the placement time for the rest and to compute whether there is space left.
        - self.length: read to determine whether the rest can be placed (or whether the bar is unbounded when length == 0.0).
    Attributes WRITTEN:
        - self.bar: when placement succeeds, appends the entry [old_current_beat, duration, None] where None denotes a rest.
        - self.current_beat: when placement succeeds, incremented by 1.0 / duration.

## Constraints:
    Preconditions:
        - The Bar object must have a valid numeric self.length (set by set_meter) or be in the unbounded state self.length == 0.0.
        - duration must be non-zero and numeric; positive values are expected for meaningful rhythmic placement.
    Postconditions (when return value is True):
        - self.bar has a new trailing element: [previous_current_beat, duration, None].
        - self.current_beat has increased by exactly 1.0 / duration.
    Postconditions (when return value is False):
        - self.bar and self.current_beat are unchanged.

## Side Effects:
    - No I/O, no network or external service calls.
    - Mutates only the Bar instance (self.bar and self.current_beat) when placement succeeds.
    - No mutation to external objects or global state is performed by this wrapper itself.

### `mingus.containers.bar.Bar.remove_last_entry` · *method*

## Summary:
Remove the last entry from the bar and decrement the current beat by that entry's beat value, returning the updated current beat.

## Description:
This method performs the "undo last placement" operation on the Bar: it subtracts the duration (as beats) of the last entry from self.current_beat, removes the last entry from the internal self.bar list, and returns the new current beat value.

Known callers and context:
- There are no internal callers of this method within the Bar class itself. It is intended to be used by external code or higher-level editors/workflows that need to undo or retract the most recently placed notes/rest in a bar (for example, a UI "undo" action, an editor script, or a higher-level Score/Track management routine).
- Typical lifecycle stage: invoked after one or more place_notes/place_rest calls when the caller decides to remove the most recently added entry.

Why this is a separate method:
- It encapsulates the two-step, stateful operation (adjusting the running beat counter and removing the list element) so callers do not need to duplicate the logic that keeps self.current_beat consistent with the contents of self.bar.
- Centralizing this behavior reduces the risk of inconsistencies between current_beat and bar contents when removing entries.

## Args:
    None.

## Returns:
    float: The updated self.current_beat after removal.
    - Normal return is a float representing the new beat position within the bar.
    - If the method raises an exception (see Raises), no value is returned.

## Raises:
    IndexError:
        - Condition: self.bar is empty (no entries). Attempting to access self.bar[-1] raises IndexError.
        - Effect: No mutation occurs to self.bar or self.current_beat when this exception is raised.
    ZeroDivisionError:
        - Condition: the last entry's duration (self.bar[-1][1]) is zero, causing division by zero when computing 1.0 / duration.
        - Effect: No mutation occurs to self.bar or self.current_beat when this exception is raised.
    TypeError (possible):
        - Condition: the last entry's duration is not a numeric type suitable for division (e.g., None or a non-numeric object). The underlying division will raise a TypeError.
        - Effect: No mutation occurs when this exception is raised.

## State Changes:
Attributes READ:
    - self.bar (reads the last entry: self.bar[-1] and its duration element at index 1)
    - self.current_beat (reads current value to compute new value)

Attributes WRITTEN:
    - self.current_beat (decrements by 1.0 / duration of the removed entry and stores the new float)
    - self.bar (reassigned to a new list omitting the last element: self.bar = self.bar[:-1])

## Constraints:
Preconditions:
    - self.bar must contain at least one entry (non-empty list).
    - The last entry in self.bar should be a sequence with an index 1 element representing duration (numeric and non-zero).
    - For correct musical semantics, the duration should be a valid beat-duration value as expected elsewhere in the Bar class (positive integer like 1, 2, 4, 8, ...), though this method does not itself validate that.

Postconditions:
    - If the call returns normally:
        * self.bar has one fewer entry than before (the last element removed).
        * self.current_beat has been decreased by exactly 1.0 / (duration of removed entry).
        * The returned value equals the new self.current_beat (a float).
    - If the call raises an exception (IndexError, ZeroDivisionError, TypeError), self.bar and self.current_beat remain unchanged.

## Side Effects:
    - No I/O or external service calls.
    - Only mutates the Bar instance (self): specifically self.bar and self.current_beat.
    - Does not touch or mutate objects outside self (e.g., NoteContainer objects inside other entries are not modified by this method).

### `mingus.containers.bar.Bar.is_full` · *method*

## Summary:
Returns whether the bar has reached (or effectively reached) its configured duration, without modifying the bar's state.

## Description:
This method determines if the Bar is "full" by checking three conditions in order:
1. If the bar's configured length is 0.0 (special/no-meter case), it is never considered full.
2. If the bar currently contains no entries, it is not full.
3. Otherwise, if the current beat position is within a small tolerance of or beyond the configured length, the bar is full.

Known callers:
- No direct internal callers are present in this class snapshot. Typical callers are external composition or sequencing code that add notes to a Bar (e.g., code that repeatedly calls place_notes or __add__) and needs to stop adding when the bar is complete.

Why this is a separate method:
- Encapsulates the fullness check (including the float-tolerance) in one place for reuse wherever calling code needs to know if the bar has reached its meter.
- Keeps decision logic out of note-placement and higher-level code for clarity and maintainability.

## Args:
    None

## Returns:
    bool: True if and only if
        - self.length is not 0.0,
        - the bar contains at least one entry, and
        - self.current_beat >= self.length - 0.001
    Otherwise returns False.

    Notes:
    - The method uses a tolerance of 0.001 to account for floating-point rounding when comparing current_beat to length.
    - When self.length == 0.0 (e.g., meter set to (0, 0)), the method always returns False even if the bar contains entries and current_beat > 0.0.

## Raises:
    None

## State Changes:
    Attributes READ:
        - self.length (float): the configured duration of the bar in beats (computed from the meter)
        - self.bar (list): the list of entries currently placed in the bar
        - self.current_beat (float): the cumulative beat position after placed entries
    Attributes WRITTEN:
        - None (the method does not mutate any attributes)

## Constraints:
    Preconditions:
        - self.length must be a numeric value (float or int); typically set via set_meter.
        - self.bar must be an iterable/list representing placed entries.
        - self.current_beat must represent the cumulative beat position and be numeric.

    Postconditions:
        - No mutation of self or external state occurs.
        - The return value accurately reflects the above boolean logic using a 0.001 tolerance.

## Side Effects:
    - None. This method performs read-only checks and does not perform I/O or modify objects outside self.

### `mingus.containers.bar.Bar.change_note_duration` · *method*

## Summary:
Adjusts the beat-duration of the bar entry identified by a matching "at" key and shifts the start times of all subsequent entries so the bar's event timeline remains continuous.

## Description:
This method searches the bar's entries and, when it finds an entry whose first-slot equals the provided at identifier, replaces that entry's stored duration with the new duration "to" and then updates following entries' start offsets by subtracting the change in beat-length. It encapsulates the non-trivial bookkeeping required when changing the duration of an already-placed note so that later notes keep the same relative spacing.

Known callers and context:
- There are no explicit callers shown in the local class listing; this method is intended to be invoked by editing routines or UI/utility code that let a user or process change a note's duration after it has been placed in a bar (a post-placement edit step in the note-editing lifecycle).
- It is implemented as a separate method because changing a single note's duration requires adjusting all later start times — logic that is non-trivial and cross-cutting for bar state consistency, so it is kept separate rather than inlined in simple placement/removal helpers.

## Args:
    at (mutable sequence-like): The identifier matched against the first-slot of each bar entry. The method expects that for every entry x in self.bar, x[0] is an indexable two-element mutable sequence where:
        - x[0][0] is the start time (float) and
        - x[0][1] is the duration (numeric denominator style used by the meter).
    to (int or numeric): The new beat-duration value to assign to the matched entry. Must be accepted by _meter.valid_beat_duration(to) (i.e., a valid beat duration according to the module-level meter validator).

## Returns:
    None

## Raises:
    ZeroDivisionError: If the matched entry's current duration (cur) is zero, the computation 1/cur will raise a ZeroDivisionError.
    (No other exceptions are explicitly raised by this method; if _meter.valid_beat_duration(to) returns False the method performs no changes.)

## State Changes:
Attributes READ:
    - self.bar: iterates over the list of bar entries.
    - For a matched entry x: the method reads x[0][1] (the current duration) to compute diff.

Attributes WRITTEN:
    - For the matched entry x: x[0][1] is set to to (the new duration).
    - For each entry that follows the matched entry in iteration order: x[0][0] (the start time) is decremented by diff (diff = 1/cur - 1/to) to keep later entries aligned.
    - Note: self.current_beat is not modified by this method (so callers may need to reconcile current_beat after calling this method if that value must remain accurate).

## Constraints:
Preconditions:
    - _meter.valid_beat_duration(to) must be True for any change to occur. If it is False, the method is a no-op.
    - The bar's entries must follow the shape expected by this method: for each element x in self.bar, x[0] must be a mutable, indexable sequence of at least two elements where positions 0 and 1 correspond to start time and duration respectively.
    - The matched entry's current duration (cur) should not be zero (otherwise a ZeroDivisionError will occur).

Postconditions:
    - If a matching entry was found and to was valid:
        * That entry's duration (x[0][1]) equals to.
        * Every entry encountered after the matched entry has its start time (x[0][0]) decreased by diff, where diff = 1/cur - 1/to.
    - If no matching entry is found, or to is not valid, the bar is left unchanged.

## Side Effects:
    - Mutates objects inside self.bar in place (modifies start times and durations of existing entries).
    - No I/O or external service calls are performed.
    - Because this method does not update self.current_beat, callers that rely on current_beat remaining consistent with the bar contents may need to update it separately after calling this method.

## Implementation notes and caveats:
    - The method uses a variable diff initialized to 0 and begins subtracting diff from subsequent entries only after the target entry is found and diff is set. This ensures entries earlier than the changed one are not affected.
    - The arithmetic uses reciprocals (1/cur - 1/to) which indicates durations are represented as denominators (e.g., meter values). Ensure consistent duration semantics across the Bar implementation when integrating or refactoring.
    - There is an apparent representation mismatch in the class: other methods (e.g., place_notes) append [start, duration, notes] (flat list), while this method expects x[0] to be a two-element indexable sequence. When reimplementing or using this method, confirm the canonical shape of bar entries in the running version of the class; otherwise adapt this method to match the project's canonical representation.

### `mingus.containers.bar.Bar.get_range` · *method*

## Summary:
Returns the lowest and highest note values present in the bar as a pair of the original note elements (not converted ints). The method does not modify the Bar; it computes a numeric range over all notes contained in each entry.

## Description:
This method scans the bar's entries (self.bar), examines each NoteContainer (the third item in each entry list), and determines the minimum and maximum note values by numeric comparison (using int() conversion for comparisons). It is intended for use during analysis or rendering steps that need the melodic/harmonic numeric range contained in the bar.

Known callers:
- No callers are present inside the Bar class source. It is a utility likely invoked by external analysis, rendering, or export code that needs the numeric range of notes in a bar.

Why this is a separate method:
- The operation is a cohesive piece of logic (scan all notes, determine numeric min/max) used for analysis and so is factored out to avoid duplication and to clearly express the intent of range computation. Keeping it separate makes it easy to reuse and test independently of other bar manipulations.

## Args:
    None

## Returns:
    tuple:
        A 2-tuple (min_note, max_note)
        - min_note: the element from the bar's notes that had the smallest numeric value when compared with int(). This is the original element (e.g., string or int) as stored in the NoteContainer.
        - max_note: the element from the bar's notes that had the largest numeric value when compared with int().
    Edge / special return values:
        - If no notes are encountered (e.g., bar is empty or no iterable notes were found), the method returns the sentinel tuple (100000, -1) (these are the initial values used by the method).
        - If a single note exists, min_note and max_note will both be that note element.

## Raises:
    TypeError:
        - If an entry's notes value (cont[2]) is None or otherwise not iterable, attempting "for note in cont[2]" will raise a TypeError.
    ValueError:
        - If a note element cannot be converted to int (int(note) fails), a ValueError will be raised during the numeric comparison.
    Notes:
        - The method does not catch these exceptions; callers must ensure the bar's entries contain iterable note containers whose elements are convertible to int, or handle exceptions externally.

## State Changes:
    Attributes READ:
        - self.bar (iterates over the list of entries)
    Attributes WRITTEN:
        - None (the method does not modify self or its entries)

## Constraints:
    Preconditions:
        - self.bar must be an iterable of entries where each entry is a sequence with the third element at index 2 representing the notes container (as created by place_notes: [beat, duration, notes]).
        - Each notes container (cont[2]) must be iterable. Typical values are instances of NoteContainer or similar objects that yield note elements.
        - Each yielded note element must be convertible to int (int(note) must succeed) for comparisons to work.
    Postconditions:
        - The method returns a tuple (min_note, max_note) where both values are either sentinel defaults (100000, -1) if no notes were processed, or are elements taken directly from the notes containers representing the numeric minimum and maximum by int() comparison.
        - The Bar instance is unchanged.

## Side Effects:
    - None: there is no I/O, no external service calls, and no mutation of objects outside of local temporaries. However, if cont[2] is not iterable or note values are not int()-convertible, exceptions propagate to the caller.

### `mingus.containers.bar.Bar.space_left` · *method*

## Summary:
Returns the number of beats remaining in the bar (length minus the amount already filled) without modifying the Bar.

## Description:
Known callers and usage context:
- Bar.value_left calls this method to compute a beat-based denominator (1.0 / space_left()) when interpreting remaining rhythmic value.
- Other callers (external code building or inspecting a Bar) may call this to decide whether there is room to place additional notes or rests.
- It is typically invoked during composition/assembly of a bar — i.e., while placing notes, removing entries, or when presenting the bar's remaining capacity to the caller.

Why this is a separate method:
- Centralizes the simple but frequently used computation of remaining beat-space so callers do not repeat the subtraction logic.
- Encapsulates the semantics of "space left" (length minus current occupancy) so future changes to how length/current_beat are represented only need one update point.

## Args:
None

## Returns:
float
- The return value is computed as self.length - self.current_beat.
- Typical values:
    - Positive float: that many beats remain free in the bar.
    - Zero: bar is exactly full (within floating-point precision).
    - Negative float: more beats have been placed than the declared length (this can happen when the bar's meter is set to (0, 0) which leaves length == 0.0 while current_beat can increase, or due to manual manipulation of current_beat).
- Note: callers that treat the return value as a divisor (for example, value_left uses 1.0 / space_left()) must guard against zero (ZeroDivisionError) and may need to handle negative values explicitly.

## Raises:
None directly.
- This method does not raise exceptions itself.
- However, code that immediately uses the returned value as a divisor will raise ZeroDivisionError if the return value is 0.0.

## State Changes:
Attributes READ:
- self.length
- self.current_beat

Attributes WRITTEN:
- None (this method does not modify self)

## Constraints:
Preconditions:
- self.length and self.current_beat must be numeric (float or int). The Bar class ensures length is set by set_meter() and current_beat is tracked by placement/removal methods.

Postconditions:
- self is unchanged after the call.
- The returned float equals the current numeric difference between length and current_beat at the time of the call (subject to floating-point precision).

## Side Effects:
- None. No I/O, no external service calls, and no mutation of objects outside self.

## Implementation notes and safety recommendations:
- When meter is (0, 0), set_meter stores length as 0.0 but place_notes allows adding entries regardless of length; in that scenario space_left() will return -current_beat (a negative number). Callers expecting "infinite remaining space" should check meter == (0, 0) or length == 0.0 rather than relying on this method returning a large positive value.
- Because of floating-point rounding, comparisons against zero or length in other methods use a small tolerance (e.g., is_full checks current_beat >= length - 0.001). Callers that need to test for "full" should follow similar tolerance-aware patterns.
- If the return value will be used as a divisor, explicitly check for value == 0.0 (or abs(value) < epsilon) and handle the unlimited-length case or raise a controlled error instead of allowing a raw ZeroDivisionError.

### `mingus.containers.bar.Bar.value_left` · *method*

## Summary:
Return the reciprocal of the remaining space in the bar (1.0 divided by the number of beats remaining).

## Description:
This method computes a numeric "value per unit" for the remaining space by returning 1.0 divided by the result of space_left(). It is a thin convenience helper that centralizes the reciprocal calculation so callers can obtain the inverse of remaining bar space without duplicating the division logic.

Known callers:
- No direct callers were found inside this module's listing. It is intended for use wherever callers need the reciprocal of the remaining space in a Bar (for example, weight/importance calculations or converting remaining time into a unit value). It may be invoked during composition or placement logic when a single scalar representing the inverse of remaining duration is required.

Why this is a separate method:
- Encapsulates the arithmetic 1.0 / space_left() in one place so callers do not have to repeat the division or reason about the underlying space calculation.
- Keeps semantic intent explicit (value of remaining space) rather than forcing callers to call space_left() and invert it.

## Args:
- None

## Returns:
- float: The reciprocal (1.0 / remaining_space) where remaining_space is self.space_left() (equal to self.length - self.current_beat).
  - If remaining_space > 0.0: returns a positive float (larger when remaining_space is small).
  - If remaining_space < 0.0: returns a negative float (possible if current_beat exceeds length, which can occur when length == 0.0 and notes are placed).
  - If remaining_space == 0.0: division by zero occurs (see Raises).

## Raises:
- ZeroDivisionError: Raised when self.space_left() evaluates to exactly 0.0 (or -0.0), i.e., there is no remaining space to invert. This commonly happens when the bar's length is zero (meter was set to (0, 0) or equivalent) or when current_beat equals length.

## State Changes:
- Attributes READ:
    - self.length (float) — total length of the bar in beats (derived from meter).
    - self.current_beat (float) — accumulated beats already placed in the bar.
- Attributes WRITTEN:
    - None (this method does not modify the Bar instance).

## Constraints:
- Preconditions:
    - The instance must be a valid Bar with numeric self.length and self.current_beat set.
    - Preferably call only when self.space_left() is non-zero to avoid a ZeroDivisionError.
- Postconditions:
    - No mutation of the Bar object occurs.
    - The return value equals 1.0 / (self.length - self.current_beat) when no exception is raised.

## Side Effects:
- None. This method performs a pure computation based on in-memory attributes and does not perform I/O or modify external objects.

### `mingus.containers.bar.Bar.augment` · *method*

## Summary:
Applies augmentation to every note-holding entry in the bar by calling each entry's note container augment() method; mutates the contained NoteContainer objects in-place and does not alter the Bar's structure.

## Description:
This method scans the Bar's internal entries list and delegates augmentation to each entry's note container (the third element of each entry). It is a convenience operation used to apply the same augmentation transformation to all note containers in a measure.

Known callers and typical usage context:
- Typical callers are composition, arrangement, or processing code that: (1) builds or loads a Bar by calling place_notes / __add__, (2) wants to apply a global augmentation transformation to all notes in the measure, then (3) continues with rendering, exporting, or further processing.
- Lifecycle stage: called after populating the bar (after place_notes / __add__) and before downstream processing that expects augmented note containers.
- The logic is a separate method because it centralizes the iteration and delegation to NoteContainer.augment(), avoiding duplicated iteration logic across multiple call sites and hiding the internal entry layout.

Entry structure (internal convention):
- Each entry in self.bar is a 3-element list: [start_beat, duration, notes]
  - start_beat (float): the beat offset within the bar
  - duration (int): the beat-duration denominator (e.g., 4 for quarter notes)
  - notes (NoteContainer or None): a NoteContainer instance for notes, or None for a rest
- place_notes appends entries in this format; place_rest calls place_notes(None, duration), therefore rests are represented with None in the notes slot.

## Args:
    None

## Returns:
    None

## Raises:
    AttributeError:
        - If an entry's notes slot (entry[2]) is None (a rest) or does not implement augment(), calling cont[2].augment() will raise AttributeError.
    IndexError:
        - If an entry is not indexable or does not have at least three elements, accessing cont[2] will raise IndexError.
    TypeError:
        - If self.bar is not iterable, iterating over it will raise TypeError.

    Notes:
    - These exceptions are not explicitly raised by augment; they are the Python exceptions that will propagate when the method attempts to call augment() on incompatible entries. For robust usage, callers should ensure entries follow the [start, duration, notes] convention and replace rests or other non-conforming entries before calling augment().

## State Changes:
    Attributes READ:
        self.bar — iterated to access each entry and its note container

    Attributes WRITTEN:
        None on the Bar instance itself (this method does not assign to any Bar attributes)
        However, the method causes in-place mutations on each contained NoteContainer via their augment() method (the exact mutation depends on NoteContainer.augment()).

## Constraints:
    Preconditions:
        - self.bar must be an iterable of indexable entries following the convention [start_beat, duration, notes].
        - For entries that should be augmented, entry[2] must be a NoteContainer-like object implementing augment().
        - If the bar contains rests (entry[2] is None), callers should either avoid calling augment() or handle/convert rests to NoteContainer placeholders first.

    Postconditions:
        - Every entry in self.bar with a valid note container at index 2 will have had its augment() method invoked exactly once.
        - The Bar's structural attributes (bar list object identity, current_beat, length, meter, key) remain unchanged.

## Side Effects:
    - No I/O or external service calls.
    - In-place mutation of contained NoteContainer objects (behavior defined by NoteContainer.augment()).
    - If entries are malformed or contain rests, Python exceptions (AttributeError/IndexError/TypeError) will propagate unless callers handle them.

## Implementation notes for reimplementation:
    - Minimal correct behavior:
        - for entry in self.bar:
            - container = entry[2]
            - container.augment()
    - Defensive alternatives (recommended for robust APIs but not present in the original implementation):
        - Skip entries where entry[2] is None (treat as rests) instead of raising.
        - Validate entry length and types with clearer custom exceptions.
        - Optionally return a summary (e.g., count of augmented containers and list of skipped entries).

## Example usage:
    - After populating a Bar with place_notes / __add__, simply call augment() to apply augmentation to all NoteContainer objects in the bar.
    - If rests are present and should be skipped:
        - Either convert rests to NoteContainer placeholders before calling augment(), or iterate externally and call augment() only on entries whose entry[2] is not None.

### `mingus.containers.bar.Bar.diminish` · *method*

## Summary:
Lower every pitch in the bar by one semitone by delegating to each entry's NoteContainer diminish operation (mutates contained NoteContainer/Note objects in-place; does not replace Bar data structures).

## Description:
- Known callers and context:
    - No internal callers are recorded in the repository for this method. It is intended to be invoked by application code or higher-level utilities that need to apply a uniform semitone-lowering to every set of notes placed in a Bar (for example, when transforming chords or adjusting an entire measure).
    - Typical lifecycle stage: called after a Bar has been constructed and populated with note entries (via place_notes, place_rest, or direct assignment) when the caller wants to diminish every contained note in the measure.

- Rationale for being a separate method:
    - Provides a concise, intention-revealing operation at the Bar level that mirrors similar container-level batch operations (Bar.augment, Bar.transpose). Encapsulating the iteration and delegation keeps callers from repeating the loop logic and preserves symmetry with other mutation methods.

## Args:
None.

## Returns:
None. The method performs in-place mutations on contained NoteContainer/Note objects and returns implicitly.

## Raises:
- AttributeError: If a bar entry's third element (cont[2]) is None (e.g., a rest placed via place_rest) or does not expose a diminish() method, attempting cont[2].diminish() will raise AttributeError which propagates to the caller.
- Any exception raised by NoteContainer.diminish (for example, IndexError or other exceptions coming from contained Note.diminish implementations) will propagate immediately; this method does not catch or translate such exceptions.

## State Changes:
Attributes READ:
- self.bar (iterated over; each element expected to be a sequence whose third element is the NoteContainer or note-like object)

Attributes WRITTEN:
- No Bar-level attributes are reassigned or modified by this method (e.g., self.current_beat, self.length, self.meter remain unchanged).
- Mutations occur on objects stored in self.bar: for each entry cont, cont[2] (the NoteContainer) is mutated in-place by its diminish() method, which in turn mutates each contained Note.

## Constraints:
Preconditions:
- self.bar must be an iterable of entries where each entry is index-accessible and contains at least three elements, with the third element (index 2) either:
    - a NoteContainer (or other object) that implements diminish(), or
    - an object explicitly known to the caller to handle diminish() calls.
- Callers should be aware that place_rest inserts entries with a None in the third position; calling diminish() without first filtering or replacing rests will raise AttributeError.

Postconditions:
- For each bar entry whose cont[2].diminish() call completes successfully, all contained Note objects will have been lowered by one semitone according to the Note/NoteContainer contract.
- The Bar object's structural attributes (self.bar list object and ordering, self.current_beat, self.length, self.meter) remain unchanged.
- The method returns None after processing all entries (or propagates the first exception encountered).

## Side Effects:
- In-place mutation of NoteContainer and Note objects referenced from self.bar: the pitch/accidental of each contained Note is changed.
- No I/O operations or external service calls are performed.
- No new NoteContainer objects are created by this method; existing containers are modified in-place.

### `mingus.containers.bar.Bar.transpose` · *method*

## Summary:
Applies a transposition to every note-containing entry in this bar, mutating the contained NoteContainer/Note objects in-place; does not return a value.

## Description:
Iterates the bar's internal entry list and forwards the provided interval and direction flag to the transpose method of the object stored in each entry's note slot (index 2). This method is used when a caller needs to transpose all notes within a Bar at once — for example, when changing the key of a bar before analysis, rendering, or playback.

Known callers and context:
- There are no internal calls to this method found within the Bar implementation; it is intended for client code and higher-level operations (for example, when transposing an entire track, pattern, or song). Typical use occurs after notes have been placed into the bar and before further processing (e.g., chord determination, progression analysis, or playback).
- Common pipeline stage: composition/arrangement transformation (key change) where a Bar is transposed as part of a larger structure (track or composition).

Why this is a separate method:
- Encapsulates the repeated action "apply transpose to every note container in the bar" so callers do not need to iterate the bar and access cont[2] themselves.
- Keeps code that manipulates Bars concise and centralizes any future changes to how bar entries are transposed.

## Args:
    interval (any): Forwarded directly to the contained object's transpose method. Accepted types/semantics are determined by the underlying Note or NoteContainer.transpose implementation (commonly a string like 'm3' or an integer semitone count).
    up (bool, optional): Direction flag forwarded to the contained object's transpose method. True to transpose upward, False to transpose downward. Defaults to True.

## Returns:
    None

## Raises:
    AttributeError: If an entry's note slot (cont[2]) is None or otherwise lacks a callable transpose method, attempting to call cont[2].transpose(...) will raise AttributeError.
    Propagated exceptions from the contained transpose implementation: Any exception raised by Note.transpose or NoteContainer.transpose (for example due to an invalid interval) will propagate unchanged.

## State Changes:
Attributes READ:
    self.bar — iterated to access each bar entry (each entry is expected to be an indexable sequence where index 2 is the notes object).

Attributes WRITTEN:
    None of Bar's attributes are reassigned or rebound by this method.
    However, the method invokes transpose on objects stored in cont[2], which typically mutates the contained Note or NoteContainer instances in-place.

## Constraints:
Preconditions:
    - self.bar must be an iterable of entries where each entry is indexable and has an element at index 2 (the notes slot).
    - Each entry's notes slot (cont[2]) must be either None or an object that implements transpose(interval, up). If it is None or missing transpose, an AttributeError will occur.
    - The provided interval and up parameters must be valid for the underlying transpose implementation (validation is delegated to the contained objects).

Postconditions:
    - If no exception is raised, for every entry cont present at call-time, cont[2].transpose(interval, up) has been invoked exactly once.
    - The membership and ordering of self.bar are unchanged.
    - Contained Note/NoteContainer objects will reflect the transposition (in-place mutation).

## Side Effects:
    - In-place mutation of the Note or NoteContainer objects stored in each entry's note slot (cont[2]). Any external references to those same Note objects will observe the updated (transposed) state.
    - No I/O or external service calls are performed.

### `mingus.containers.bar.Bar.determine_chords` · *method*

## Summary:
Returns a list mapping each entry's beat position to the chord-identification result produced by the entry's note container; does not modify the Bar instance.

## Description:
Iterates over the bar's stored entries and, for each entry, takes the stored beat/position (the first element of the entry) and asks the entry's note container (the third element) to determine chord identity using the provided shorthand flag. The method exists to encapsulate the common operation of converting the bar's internal entry representation into a sequence of (position, chord-identification) pairs and to centralize handling of the shorthand flag when delegating to NoteContainer.determine / the central chord dispatcher.

Known callers and typical pipeline stage:
- Commonly invoked by analysis or reporting utilities after the Bar has been populated with notes (for example, when building a chord chart or exporting per-beat chord analysis).
- It is used in the chord-analysis stage of a music-processing pipeline after notes have been placed in the Bar and normalized.
- The method is separated from other logic so callers don't need to know the internal entry layout of the Bar or repeatedly call NoteContainer.determine on each entry.

Why this is a separate method:
- Keeps higher-level code simple: callers receive a ready-to-use list of (position, chord-result) pairs rather than iterating and delegating themselves.
- Centralizes delegation to NoteContainer.determine and keeps Bar-level code focused on its role as a container.

## Args:
    shorthand (bool, optional): If True, request compact chord notation from the chord detectors (for example "Cm9"); if False, request verbose names where supported.
        - Default: False

## Returns:
    list[list]: A list of 2-element lists. Each element has the form:
        [ position, chord_result ]
    where:
        - position: the exact object stored in the bar entry at index 0 (typically a numeric beat/time value, e.g., float).
        - chord_result: the exact return value from calling the entry's note container .determine(shorthand).
    Notes about returned values:
        - If self.bar is empty, returns an empty list [].
        - chord_result values are whatever NoteContainer.determine (and the chord dispatcher) returns: this commonly includes lists of chord name strings, [] for an explicit empty-list input, a single-element sequence for single-note inputs, or False in some helper-specific cases. The method does not transform these results.
        - The list preserves iteration order of self.bar.

## Raises:
    - AttributeError: If an entry's third element (notes container) is None or does not implement .determine, attempting x[2].determine(...) will raise AttributeError.
    - IndexError: If an entry in self.bar is not a sequence with at least three elements (index 0 and index 2 are accessed), an IndexError will be raised.
    - Any exception raised by the note container's determine implementation or by the chord-detection helpers (for example, note-formatting errors originating in the chord dispatcher) is propagated unchanged.

## State Changes:
    Attributes READ:
        - self.bar (iterated): the method reads each entry in self.bar.
        - self.bar[i][0] (position): read for each entry to include in the result.
        - self.bar[i][2] (notes container): read and invoked with .determine(shorthand).
    Attributes WRITTEN:
        - None. This method does not modify self or its entries.

## Constraints:
    Preconditions:
        - self.bar must be an iterable of entry sequences where each entry is expected to be an indexable 3-element sequence of the form [position, duration, notes].
            * position (index 0) is typically a numeric beat (float or int).
            * notes (index 2) must normally be a NoteContainer-like object exposing determine(shorthand).
        - If any entry is a rest represented by None in the notes slot, callers should not call determine_chords (or must convert rests to a NoteContainer-like placeholder) because calling .determine on None will raise AttributeError.
    Postconditions:
        - The Bar instance is unchanged.
        - The return value is a list of [position, chord_result] pairs corresponding to the bar entries in iteration order.

## Side Effects:
    - No I/O or external service calls are performed by this method.
    - The only side effects are those produced by the invoked note container's determine method (and any helper functions it calls); any exceptions or side effects from those calls are not caused or masked by this method.

### `mingus.containers.bar.Bar.determine_progression` · *method*

## Summary:
Produces an ordered list mapping each entry's start beat to the progression result computed from that entry's pitch names without modifying the Bar.

## Description:
Iterates self.bar (where each entry is expected to be a three-element sequence [beat, duration, notes]) and, for each entry, calls the core progressions.determine routine with the entry's pitch names and the Bar's key string (self.key.key). The method returns a new list of [beat, progression_result] pairs in the same order as entries in self.bar.

This logic is encapsulated as its own method to provide a single, reusable facility to produce bar-level progression summaries: it centralizes iteration, note-name extraction, and the call into mingus.core.progressions.determine so callers don't duplicate that sequence.

## Args:
    shorthand (bool): If True, request shorthand notation from progressions.determine. Default: False.

## Returns:
    list[list]: A list where each element is a two-element list:
        - element[0] (numeric): the start beat read directly from the bar entry (entry[0]).
        - element[1] (any): the value returned by progressions.determine(note_names, key_string, shorthand) for that entry.
    Notes on element[1]:
        - Normally this is a list of one or more strings (e.g., ['I'], ['V7']) describing chord function(s).
        - progressions.determine may also return nested lists in cases where the input chord representation is nested; this method preserves whatever structure progressions.determine returns.
    Edge cases:
        - If self.bar is empty, returns [].

## Raises:
    AttributeError:
        - If an entry's notes element is None (a rest) or does not provide get_note_names(), calling x[2].get_note_names() will raise AttributeError.
        - If self.key does not expose a .key attribute, accessing self.key.key raises AttributeError.
    IndexError:
        - If an entry in self.bar does not have at least three elements (expected indexes 0 and 2), indexing may raise IndexError.
    Any exception raised by progressions.determine is propagated to the caller (this method does not catch exceptions).

## State Changes:
    Attributes READ:
        - self.bar (iterated; reads each entry's indexes 0 and 2)
        - self.key (reads self.key.key)
    Attributes WRITTEN:
        - None (the method does not modify self or the objects in self.bar)

## Constraints:
    Preconditions:
        - self.bar should be an iterable of indexable entries where:
            * entry[0] is a numeric beat value (float or int).
            * entry[2] is normally a NoteContainer or similar object exposing get_note_names().
        - self.key must expose a .key attribute containing a key string acceptable to progressions.determine.
    Postconditions:
        - self is unchanged.
        - The returned list has exactly len(self.bar) entries (one per bar entry) and preserves ordering.

## Side Effects:
    - No I/O or network activity.
    - Calls progressions.determine; any side effects or exceptions from that function will occur and propagate.

## Implementation notes (reimplementation recipe):
    1. Import or reference the progressions module (the original code does `from mingus.core import progressions` inside the method; a top-level import is also acceptable).
    2. Create an empty list result = [].
    3. For each entry in self.bar:
        a. Read beat = entry[0].
        b. Read notes_container = entry[2].
        c. Call note_names = notes_container.get_note_names() (expects a list of name strings).
        d. Read key_string = self.key.key.
        e. Call progression = progressions.determine(note_names, key_string, shorthand).
        f. Append [beat, progression] to result.
    4. Return result.
    - Do not suppress exceptions from steps (c) or (e); allow them to propagate as in the original implementation.

## Example (illustrative):
    - For a bar with entries [[0.0, 4, NoteContainer(['C','E','G'])], [1.0, 4, None]]:
        * The first entry will produce [0.0, progression_for_C_major] where progression_for_C_major is progressions.determine(['C','E','G'], self.key.key, shorthand).
        * The second entry will raise AttributeError when trying to call get_note_names() on None (this mirrors how place_rest stores rests).

### `mingus.containers.bar.Bar.get_note_names` · *method*

## Summary:
Return a de-duplicated list of note-name strings present in the bar, preserving the order in which each name is first observed.

## Description:
Iterates over each entry in self.bar (each entry is expected to be a three-element sequence created by place_notes: [beat, duration, notes]) and calls the third element's get_note_names() method to obtain note-name strings. It accumulates those names into a result list while ensuring each name appears only once; the order of names is the order of first appearance when iterating the bar and each entry's returned names.

Known callers and usage context:
- No direct callers of Bar.get_note_names were found in the provided snapshot of the repository.
- Typical callers would be analysis, UI, or export routines that need the set of pitch/note names used in a bar (for example, for displaying which pitches occur in the bar or for feeding into algorithms that accept a list of note names).
- This method centralizes iteration and de-duplication so callers do not repeat that logic.

Why this is a standalone method:
- Aggregating and de-duplicating note names is a reusable operation used in higher-level analysis or display code; placing it on Bar keeps callers simple and enforces the assumption about the bar-entry shape (beat, duration, notes).

## Args:
    None

## Returns:
    list[str]: A list of note-name strings.
    - Contains no duplicates: each distinct note name appears once.
    - Order is deterministic: names appear in the order they are first encountered while iterating self.bar and then in the order returned by each entry's get_note_names().
    - If self.bar is empty, returns [].

## Raises:
    AttributeError:
        - Trigger: when an entry's third element (notes) is None or does not have a callable get_note_names attribute.
        - Example: a rest is represented by notes == None (via place_rest), so calling this method will raise AttributeError for that entry.
    IndexError:
        - Trigger: when an entry in self.bar is shorter than three elements (no index 2).
    TypeError:
        - Trigger: when an entry's get_note_names() returns a non-iterable (e.g., None or a scalar) and the method attempts to iterate over it.
    Note: These exceptions are not raised intentionally by this method but are the natural propagation when bar entries or their note containers are malformed.

## State Changes:
    Attributes READ:
        - self.bar (iterated)
        - for each entry: the entry[2] object is read (its get_note_names method is invoked)
    Attributes WRITTEN:
        - None (this method does not modify the Bar instance or its entries)

## Constraints:
    Preconditions:
        - self.bar must be an iterable of entries shaped as [beat, duration, notes] (place_notes produces this shape).
        - For every entry for which the caller expects names to be included, entry[2] must be an object exposing a callable get_note_names() method.
        - get_note_names() should return an iterable of strings; otherwise, TypeError or unexpected results may occur.
    Postconditions:
        - The Bar instance is unchanged.
        - The returned list contains each distinct note-name string from the bar exactly once and preserves the observed order of first occurrence.

## Complexity:
    - Let E = number of entries in self.bar, K = average number of names returned per entry, and U = number of unique note names in the bar.
    - The method performs approximately E * K iterations and, because membership checks use a list (if x not in res), each membership check is O(U). Worst-case time complexity is O(E * K * U) — effectively quadratic in the number of unique names in the typical case. Memory usage is O(U) for the result list.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self by this method itself.
    - Exceptions from entry objects (AttributeError, IndexError, TypeError or others) will propagate to the caller.

## Example usage (conceptual):
    - Given a bar with entries created via place_notes where each notes element is a NoteContainer whose get_note_names returns ['C', 'E']:
        - get_note_names() -> ['C', 'E']
    - Given multiple entries with overlapping names, e.g. ['C', 'E'] then ['E', 'G']:
        - get_note_names() -> ['C', 'E', 'G'] (G appears once and in first-seen order)

### `mingus.containers.bar.Bar.__add__` · *method*

## Summary:
Adds a note or note-like object into this Bar by delegating to the placement routine using the bar's beat-duration; updates bar contents and current beat when placement succeeds.

## Description:
This method implements the behavior of the binary + operator for Bar: when a Bar instance is on the left side of + and a note container (or a note-like object) on the right, this method is invoked to place the given notes into the bar.

Known callers and invocation context:
- Implicitly invoked by Python when code performs bar + note_container. Typical use is in composition or sequencing code that builds a Bar by successively adding notes or note containers.
- User code or higher-level utilities in the composition pipeline that construct or populate Bar instances will use this through the + operator.

Why this is a separate method:
- It centralizes the logic for operator semantics (mapping the bar's meter to a placement duration) and delegates actual placement to place_notes. Keeping the operator implementation small makes the behavior predictable and reuses the place_notes logic for the actual insertion and validation.

## Args:
    note_container (mingus.containers.note_container.NoteContainer | object | str | list):
        The thing to add to the bar. Accepted types (as handled by place_notes):
         - an instance that already exposes a .notes attribute (treated as a NoteContainer-like object),
         - an object that has a .name attribute (converted to a NoteContainer),
         - a string of note names (converted to a NoteContainer),
         - a list of note representations (converted to a NoteContainer).
        There is no default value; the caller must supply the right-hand operand of the + operator.

## Returns:
    bool:
        True if the notes were placed into the bar (i.e., there was sufficient space and place_notes appended the entry),
        False if placement failed (insufficient remaining space in the bar when a finite meter length is in effect).

## Raises:
    This method does not itself raise exceptions. It delegates to place_notes, which in the current implementation does not raise for normal inputs. Meter parsing/setting elsewhere (e.g., set_meter) may raise MeterFormatError, but that is not raised by this method during normal addition.

## State Changes:
    Attributes READ:
        self.meter (tuple): reads self.meter[1] (the beat-duration denominator) to choose the duration argument passed to place_notes.

    Attributes WRITTEN (indirectly, via place_notes):
        self.bar (list): may be appended with a new entry [start_beat, duration, notes].
        self.current_beat (float): may be incremented by 1.0 / duration when placement succeeds.

## Constraints:
    Preconditions:
        - self must be an initialized Bar with a meter attribute set (tuple-like). The __init__ of Bar calls set_meter, so typical Bars satisfy this.
        - note_container must be one of the input forms that place_notes accepts (NoteContainer-like object, object with .name, string, or list).

    Postconditions:
        - If the method returns True: a new entry has been appended to self.bar representing the placed notes at the prior current_beat, and self.current_beat has been advanced by 1.0 / duration.
        - If the method returns False: self.bar and self.current_beat are unchanged.
        - The duration passed to place_notes is self.meter[1] when that value is non-zero, otherwise the fallback duration 4 is used.

## Side Effects:
    - No I/O or external service calls.
    - May construct a new NoteContainer (conversion from string/list/other) as part of place_notes.
    - Mutates the Bar instance via place_notes (see Attributes WRITTEN).

### `mingus.containers.bar.Bar.__getitem__` · *method*

## Summary:
Provides list-like access to a bar entry by delegating indexing to the internal storage; returns the stored entry (or a list of entries for a slice) and does not itself modify Bar attributes.

## Description:
This method implements Python's sequence access for the Bar container by forwarding the provided index to the underlying list stored in self.bar. Typical callers:
- External code that inspects or processes individual bar entries (for example rendering, analysis, chord/progression determination, or sequencing) will use bar[index] to obtain the entry at that beat.
- Client code that needs a contiguous range of entries will use slicing (bar[start:stop]) to obtain a list of entries.
- Because it is part of the Bar sequence API, it enables idiomatic interactions such as iteration, membership checks, and unpacking when combined with other container methods.

This functionality is implemented as its own method (instead of direct external access to self.bar) to:
- Provide a clear, documented public interface for accessing entries.
- Allow the Bar object to behave like a Python sequence (supporting negative indices and slices) while encapsulating underlying storage.
- Reserve the opportunity to change internal representation later without changing external callers.

## Args:
    index (int or slice):
        - int: zero-based index of the requested entry. Negative indices follow Python list semantics (-1 returns the last entry).
        - slice: a slice object (e.g., start:stop:step); the method returns a list of entries corresponding to the slice.
        - Invalid types (anything other than int or slice) will cause the underlying list to raise TypeError.

## Returns:
    If index is an int:
        list[object]: A single entry from the bar with the structure [beat, duration, notes]:
            - beat (float): beat offset inside the bar (e.g., 0.0, 0.5).
            - duration (int): denominator of the note (e.g., 4 for quarter notes) as stored when the entry was placed.
            - notes (NoteContainer or None): the NoteContainer for the entry, or None for a rest.
    If index is a slice:
        list[list[object]]: A new Python list containing zero or more entries (each as described above).
    Edge cases:
        - If the Bar is empty or the integer index is out of range, IndexError is raised by the underlying list.
        - For a slice that selects no elements, an empty list is returned.

## Raises:
    IndexError:
        - When an integer index is out of bounds for the underlying list (e.g., requesting index 0 from an empty bar).
    TypeError:
        - When the provided index object is not a valid list index type (e.g., a dict); the underlying list will raise TypeError in that case.

## State Changes:
    Attributes READ:
        - self.bar (list): the method reads the list object that stores bar entries.
    Attributes WRITTEN:
        - None. The method itself does not assign to any attributes.

## Constraints:
    Preconditions:
        - self.bar must be a list-like sequence of entries where each entry is expected to be [beat: float, duration: int, notes: NoteContainer|None].
        - The caller should expect Python list indexing semantics (0-based, negative indices allowed).
    Postconditions:
        - The Bar instance's attributes are unchanged by this call.
        - The returned value is a direct reference to the underlying entry (for integer indexing) or a new list containing references to the underlying entries (for slicing).

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutability caveat: when an integer index is used, the method returns a reference to the internal entry (a list). Mutating the returned list (for example, replacing its elements or mutating the contained NoteContainer) will mutate the Bar's internal state. Similarly, mutating a NoteContainer returned within an entry will affect the Bar.

### `mingus.containers.bar.Bar.__setitem__` · *method*

*No documentation generated.*

### `mingus.containers.bar.Bar.__repr__` · *method*

## Summary:
Returns a string representation of the Bar's internal list storage (self.bar) without modifying the object.

## Description:
Implements the object's canonical textual representation by returning the result of calling Python's str() on the internal attribute self.bar. This provides a direct, textual snapshot of the bar's contents at the time of the call.

## Known callers / invocation context:
- repr(bar) will use this method's return value as the object's representation.
- Any code that explicitly calls str(bar) will also obtain the same string.
(These usages are standard Python semantics; the method itself only performs the conversion.)

## Why this is a dedicated method:
Providing a focused dunder-representation isolates the conversion logic (stringifying the internal storage) from other behavior and makes the textual form available to Python's inspection and debugging mechanisms.

## Args:
    None

## Returns:
    str: The string produced by str(self.bar).
    - For an empty bar this will be "[]".
    - For a populated bar it will be the Python-list textual form of the entries in self.bar, where each entry is produced by the contained objects' string representations.

## Structure of self.bar (relevant for interpreting the return value):
    - self.bar is a Python list (initialized in __init__ via empty()).
    - Entries are appended by place_notes as lists of the form [beat, duration, notes], where:
        * beat: float (self.current_beat)
        * duration: int (beat subdivision, e.g., meter denominator)
        * notes: NoteContainer instance or None
    - Therefore the returned string typically represents a list of these inner lists, using each element's own string form.

## Raises:
    - Any exception raised by converting self.bar or its elements to strings (i.e., from an element's __str__ or __repr__) is propagated.
    - The method itself contains no explicit raise statements.

## State Changes:
    Attributes READ:
        - self.bar
    Attributes WRITTEN:
        - None

## Preconditions:
    - self.bar exists (the class initializes it in __init__ and empty()). If client code reassigns self.bar to an arbitrary object, str() will still be called on that object (no type enforcement here).

## Postconditions:
    - The Bar instance is unchanged.
    - The return value is a string representation of the bar's contents at call time.

## Side Effects:
    - No I/O or external service calls.
    - May indirectly invoke __str__/__repr__ on objects contained within self.bar; any side effects in those methods (if present) will occur.

### `mingus.containers.bar.Bar.__len__` · *method*

## Summary:
Returns the number of entries currently stored in the bar's internal container without modifying the object's state.

## Description:
This method implements the container-length protocol for Bar so that calling the built-in len(bar_instance) yields the number of placed entries. It is invoked whenever client code (including tests, serializers, or any external logic) calls len() on a Bar instance. The method is a distinct dunder method so Python's container protocol is satisfied and callers do not need to access the internal attribute self.bar directly.

Known callers / contexts:
- Any call site that performs len(bar_instance) (user code, utilities, or libraries).
- Typical usage contexts include: measuring how many note/rest entries are present before adding more, producing summaries/diagnostics, or tests that assert the number of entries.
Note: some internal methods in the class access the underlying list self.bar directly rather than calling len(self) (for example, class methods that reference self.bar), so not all internal checks invoke this dunder method.

This is a small, single-purpose method to provide a stable, public API for obtaining the bar's size and to encapsulate the internal representation (self.bar) behind Python's standard protocol.

## Args:
None

## Returns:
int: The length of the internal entries container (the value returned by len(self.bar)).
Possible values:
- Any integer >= 0 representing the number of placed entries.
Edge cases:
- If self.bar is an empty list, returns 0.
- If self.bar is replaced with an object that supports __len__, the returned value is whatever that object's __len__ provides.

## Raises:
- AttributeError: If the Bar instance does not have the attribute self.bar (this would indicate improper initialization or external mutation).
- TypeError: If self.bar exists but is an object that does not support len() (i.e., calling len(self.bar) raises TypeError).
These exceptions are not raised by the method itself intentionally but are the direct result of delegating to Python's built-in len() on self.bar.

## State Changes:
Attributes READ:
- self.bar

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- The Bar instance must be initialized so that self.bar exists and is intended to represent the entries container (by default __init__ calls empty() to set self.bar = []).
- Preferably, self.bar should be a sequence or another object that implements __len__.

Postconditions:
- No mutation of the Bar object occurs; self and its attributes remain unchanged.
- The return value accurately reflects the current length of the bar's entries container at the time of the call.

## Side Effects:
- None. The method performs no I/O, network calls, or mutations of external objects. It only queries the length of the internal container.

### `mingus.containers.bar.Bar.__eq__` · *method*

## Summary:
Compares the entries of this Bar with another Bar-like object by iterating the stored entries and returning True only if every compared entry is equal; does not modify object state.

## Description:
This method implements equality semantics used when Python's equality operator (==) is applied to Bar instances or other objects that expose a compatible bar attribute (i.e., a sequence supporting len() and indexing). It is invoked whenever two Bar objects are compared in application code, unit tests, or any pipeline step that compares measures for equivalence.

The method is separate to centralize the notion of equality for Bar objects (operator overloading) so callers can use the natural '==' syntax rather than calling a helper function. Keeping equality logic in a dedicated dunder method also allows other language features (containers, assertions) to rely on consistent semantics.

## Args:
None (operates on self and expects a second operand available as other when called by the Python interpreter).

Although not an explicit parameter, the method expects:
- other: an object with an attribute named bar that is indexable and has a length (supports len(other.bar) and other.bar[i]).

## Returns:
bool
- True if every compared entry self.bar[b] equals other.bar[b] for b in the iteration range (see Constraints for iteration details).
- False as soon as a mismatching pair is found.
- If the loop does not execute (e.g., when len(self.bar) <= 1), the method returns True (empty or single-entry self.bar is considered equal under this method unless an exception occurs).

## Raises:
- AttributeError: if other does not have a .bar attribute.
- IndexError: if other.bar is shorter than the indices accessed (possible when other.bar has fewer elements than self.bar - 1).
- Any exception raised by equality checks of contained elements (from calling self.bar[b] != other.bar[b]) may propagate (e.g., TypeError from unsupported comparisons).

Exact trigger conditions:
- AttributeError: accessing other.bar when other has no such attribute.
- IndexError: when the method attempts to access other.bar[b] for some b that is out of bounds (this can happen because the loop uses len(self.bar) - 1).
- Propagated exceptions: if elementwise comparison invokes user code or comparators that raise.

## State Changes:
Attributes READ:
- self.bar (length via len(self.bar] and elements via indexing)
- other.bar (length and elements via indexing, implicitly)
Attributes WRITTEN:
- None (the method does not mutate self or other)

## Constraints:
Preconditions:
- self.bar must be a sequence supporting len() and indexing.
- other must expose a .bar attribute that is a sequence supporting indexing and len().
- The intended semantics assume comparable element types inside the bar entries (their __eq__ is meaningful).

Postconditions:
- No attributes of self or other are changed.
- The method returns a boolean indicating the comparison result or raises an exception if a precondition is violated or an indexed access fails.
- Note: equality as implemented is not guaranteed to be symmetric. Because the function iterates up to len(self.bar) - 1, if self and other have different lengths the comparison may raise IndexError or yield a result that differs from other == self.

Important behavioral detail:
- The loop iterates for b in range(0, len(self.bar) - 1). This means the final element at index len(self.bar) - 1 is not compared. For len(self.bar) <= 1 the loop body does not execute and the method returns True. This is an off-by-one behavior to be aware of when relying on equality.

## Side Effects:
- None: the method performs no I/O, network access, or persistent side effects.
- It may raise exceptions that propagate to callers, which callers should handle if comparing Bars of differing shapes or non-Bar objects.

