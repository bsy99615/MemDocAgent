# `track.py`

## `mingus.containers.track.Track` · *class*

*No documentation generated.*

### `mingus.containers.track.Track.__init__` · *method*

## Summary:
Initializes a Track instance by creating an empty per-instance list of bars and storing an optional instrument reference, preparing the object to accept bars and notes.

## Description:
This constructor is invoked when a new Track object is created (typically by client code or higher-level assembly code when building a musical arrangement). It establishes the track's initial, empty state so subsequent operations (adding bars or notes, transposition, tuning) operate on an instance-specific container.

This logic is implemented as the constructor because it must create instance-scoped state (a new, empty list of bars) and record the optional instrument at object creation time; inlining this logic elsewhere would risk sharing mutable defaults between instances or delaying essential initialization.

Known callers and invocation context:
- No direct callers are defined in this module. Typical usage is direct instantiation by user code or by other containers that assemble musical data; the constructor is used during the object creation/lifecycle initialization step.

## Args:
    instrument (object | None): Optional instrument descriptor or object. Allowed values:
        - None (default): no instrument is associated with the Track.
        - An object that provides the minimal interface expected by other Track methods:
            * can_play_notes(note) -> bool  (used by add_notes to validate pitch range)
            * tuning attribute (readable/writable) (used by get_tuning and set_tuning)
        The implementation does not validate the instrument's type or raise on an invalid object; if provided, the instrument is stored as-is.

## Returns:
    None: As a constructor, it does not return a value; it initializes the instance in-place.

## Raises:
    None: The constructor does not raise any exceptions. Any errors related to instrument capabilities or other operations occur in other methods (e.g., add_notes may raise InstrumentRangeError when validating notes against instrument.can_play_notes).

## State Changes:
    Attributes READ:
        - None (the constructor does not read existing instance attributes)
    Attributes WRITTEN:
        - self.bars: set to a new empty list[] (instance-level list used to hold Bar objects)
        - self.instrument: set to the provided instrument argument (or None)

## Constraints:
    Preconditions:
        - No preconditions enforced by the constructor. If an instrument is provided, callers should ensure it implements the minimal interface (can_play_notes and tuning) before invoking methods that rely on those members.
    Postconditions:
        - After return, self.bars is a fresh, empty list distinct from the class-level default.
        - After return, self.instrument is exactly the value passed as the instrument argument (which may be None).
        - The Track instance is ready to accept bars/notes via add_bar, add_notes, and related methods.

## Side Effects:
    - No I/O, no external service calls.
    - Mutates only the newly created Track instance (does not touch global state).
    - By creating a new list for self.bars, prevents accidental sharing of a mutable list across Track instances.

### `mingus.containers.track.Track.add_bar` · *method*

## Summary:
Appends a bar object to this Track's bars list, mutating the Track, and returns the same Track instance to allow fluent chaining.

## Description:
Known callers and context:
- Track.__add__: when a value with a 'bar' attribute is added to a Track via the + operator, __add__ delegates to this method.
- User code / API consumers: typically called when constructing or modifying a Track by adding a completed Bar object.
Lifecycle stage:
- Invoked during track construction or modification when entire bars (not individual notes) are appended.
Why this is a separate method:
- Centralizes the append operation so callers can use a simple, documented API and so future validation, normalization, or event hooks can be added in one place without changing all call sites.
- Provides fluent API support by returning self.

## Args:
    bar (mingus.containers.bar.Bar or any object): The object to append to the track's bars list. Intended usage is to pass a mingus.containers.bar.Bar instance (or a Bar-like object). The method does not enforce type checks.

## Returns:
    Track: The same Track instance (self) after appending the bar. This enables call chaining (e.g., track.add_bar(bar).add_bar(another_bar)).

## Raises:
    AttributeError: If self.bars is not a list-like object with an append method (for example, if Track was not properly constructed and self.bars is None or replaced with a non-list object), calling append will raise AttributeError.
    Note: The method itself performs no explicit validation and therefore does not raise type-specific errors for invalid bar objects; downstream code may raise errors if appended objects do not meet expected Bar semantics.

## State Changes:
    Attributes READ:
        - self.bars (the list is accessed to call its append method)
    Attributes WRITTEN:
        - self.bars (mutated in-place: an element is appended)

## Constraints:
    Preconditions:
        - self must be a properly constructed Track where self.bars is a list-like container that supports append (Track.__init__ initializes self.bars to an empty list).
        - Preferably, the caller supplies a valid mingus.containers.bar.Bar instance (or compatible object) to avoid later errors when other Track APIs iterate or index into bars.
    Postconditions:
        - The length of self.bars increases by 1.
        - The final element of self.bars is the exact object passed as bar.
        - The method returns self.

## Side Effects:
    - Mutates the Track instance by appending to its bars list.
    - No I/O, no external service calls.
    - No validation or normalization performed; appending invalid objects may cause errors later when other Track methods assume Bar semantics.

## Notes and edge cases:
    - If bar is None or of an unexpected type, it will still be appended; callers should validate inputs if necessary.
    - There is no concurrency protection; concurrent appends from multiple threads may cause race conditions.
    - Track.__setitem__ performs a type-like check (hasattr(value, "bar")) when assigning by index, but add_bar does not perform this check.

### `mingus.containers.track.Track.add_notes` · *method*

## Summary:
Adds one or more notes (or a rest) into the track by placing them into the last Bar (creating new Bar(s) as needed), and returns whether placement into the bar succeeded; the call may mutate the track's bars list.

## Description:
Known callers and context:
    - Track.from_chords: invoked while expanding chord sequences into the track; used during composition to place chord NoteContainers or rests one event at a time.
    - Track.__add__: invoked when the Track is used with the + operator for convenience (adding notes or named note-like objects).
    - External composition code or interactive construction of a Track: called when building up a track by appending notes/rests sequentially.

Lifecycle stage:
    - Called while constructing or editing a Track to append the next musical event. It performs instrument-range validation, ensures there is a bar available, and delegates the actual placement to the Bar.place_notes method.

Why this logic is a separate method:
    - Centralizes the higher-level orchestration needed before placing notes into a Bar:
        * instrument-range validation,
        * setting a default duration,
        * ensuring an appropriate Bar exists (creating one when the track is empty or when the last bar is full),
        * delegating conversion/placement to Bar.place_notes.
    - Keeps Track-level concerns (bar management and instrument checks) separate from low-level Bar insertion logic.

## Args:
    note (NoteContainer | object | str | list | None):
        - Allowed values and behavior:
            * Any value that Bar.place_notes accepts (e.g., a NoteContainer, an object with a .notes attribute, an object with a .name attribute, a string, a list, or None to represent a rest).
            * Conversion and validation of note values are performed by Bar.place_notes; callers should follow the same input rules expected by NoteContainer/Bar.place_notes.
    duration (int | float | None, optional):
        - Denominator used by Bar.place_notes to compute the time increment as 1.0 / duration.
        - If None (the default), duration is set to 4 before placement.
        - Expected to be a non-zero numeric value. Passing 0 or a non-numeric value will cause Bar.place_notes to raise (e.g., ZeroDivisionError or TypeError).

## Returns:
    bool:
        - Returns the exact boolean value returned by Bar.place_notes:
            * True if the musical event was appended to the target Bar and the bar's current beat advanced.
            * False if there was insufficient remaining space in the target Bar (no append was performed by Bar.place_notes).
        - Note: add_notes itself may have already appended one or more Bar instances to self.bars before calling Bar.place_notes (see State Changes). Thus a False return does not imply that no Bar was appended to the Track — only that the final Bar.place_notes call did not append the event.

## Raises:
    InstrumentRangeError:
        - Raised when self.instrument is not None and self.instrument.can_play_notes(note) returns False.
        - Exact trigger: when an instrument is attached to the Track and that instrument declares the given note (or note container) out of playable range.
    Any exception raised by Bar.place_notes:
        - Bar.place_notes may raise ZeroDivisionError (if duration == 0), TypeError (if duration is not numeric), or propagate exceptions from NoteContainer conversion. These propagate through add_notes unchanged.

## State Changes:
    Attributes READ:
        - self.instrument (to call can_play_notes when present)
        - self.bars (to check length and to obtain the last bar)
        - last_bar.key and last_bar.meter (read when creating a new Bar to copy meter/key)
        - last_bar.is_full() (call on last bar to decide whether to create a new Bar)
    Attributes WRITTEN:
        - self.bars: may be modified by appending a new Bar() when the track is empty, and may append another Bar(last_bar.key, last_bar.meter) when the last bar is full. At most these appends occur before delegating to place_notes.
        - The Bar instance on which place_notes is invoked may be mutated by Bar.place_notes (appending an entry and advancing its current_beat) if placement succeeds.

## Constraints:
    Preconditions:
        - self must be a properly-initialized Track (self.bars should be a list or list-like).
        - If self.instrument is set, it must implement can_play_notes(note) and return a boolean.
        - note must be acceptable to Bar.place_notes / NoteContainer (conversion/validation is deferred to Bar.place_notes).
        - duration should preferably be a positive non-zero numeric; passing 0 or a non-numeric value will cause Bar.place_notes to raise.
    Postconditions:
        - If the method returns True:
            * The targeted Bar (the last element of self.bars at the time of the Bar.place_notes call) has had an entry appended and its current beat advanced (per Bar.place_notes semantics).
            * One or zero new Bars may have been appended to self.bars before placement (see State Changes).
        - If the method returns False:
            * Bar.place_notes did not append an entry to the final Bar; however, add_notes may still have appended Bar instances beforehand (for example, when the track was empty).
        - If an exception is raised (InstrumentRangeError or any exception from Bar.place_notes):
            * No guarantee about bar placement; however, any Bar(s) appended before the point of exception remain appended (add_notes does not roll back appended Bar objects).

## Side Effects:
    - Mutates the Track object's self.bars list by appending Bar instances when necessary.
    - Delegates to Bar.place_notes which may mutate that Bar (appending entries and advancing current beat).
    - No I/O or external network/service calls are performed.
    - Exceptions from Bar.place_notes or NoteContainer construction may be propagated to the caller.

### `mingus.containers.track.Track.get_notes` · *method*

## Summary:
Yields every beat tuple from each bar in the track as produced by the Bar iterator, without modifying track state.

## Description:
Provides a lazy iterator across all bars contained in the track. For each Bar in self.bars it iterates that Bar and yields each item the Bar produces. No transformation is applied; the method simply relays the triples emitted by the bars.

Known callers:
    - No direct callers are defined within the Track class source. This method is an API intended for callers that need to traverse all beats/notes of a Track (for example: rendering, exporting, or playback code), but specific call sites are external to this file.

Why this is a separate method:
    - Iterating the notes across all bars is a common, reusable operation. Encapsulating it as a generator method avoids duplicating iteration logic and allows callers to consume notes lazily.

## Args:
    None

## Returns:
    generator -> yields tuples (beat, duration, notes)
    - Each yielded value is exactly the value produced by iterating an individual Bar.
    - The method does not alter or wrap these tuples; it relays them unchanged.
    - If the track contains no bars, the generator yields nothing.

## Raises:
    None raised directly by this method.
    - If elements of self.bars are not iterable or their iterator does not yield 3-tuples, iteration will raise whatever exception occurs (e.g., TypeError, ValueError) originating from that iteration. This method does not catch or convert such exceptions.

## State Changes:
    Attributes READ:
        - self.bars
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self.bars must be an iterable (typically a list) of objects that themselves are iterable.
        - Each Bar element must provide an iterator that yields 3-tuples (beat, duration, notes). The method does not validate tuple shape before yielding.
    Postconditions:
        - No change to self or to contained Bar objects is performed by this method.
        - The returned generator will, as it is consumed, yield the same items that would be produced by iterating each Bar in self.bars in order.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside of transient iteration state.
    - Exceptions arising from iterating malformed Bar objects will propagate to the caller.

### `mingus.containers.track.Track.from_chords` · *method*

## Summary:
Populate the Track by expanding a sequence of chord descriptors into NoteContainer objects (or rests) and placing them sequentially into the Track's bars; returns self to allow chaining and mutates the track's bars and their contents.

## Description:
Known callers and context:
- Intended to be called by user code or higher-level composition utilities that convert a chord progression (an iterable of chord descriptors) into an actual Track of placed chord events.
- Typical lifecycle stage: invoked during Track construction or when converting a chord-based representation into concrete bar/beat placements prior to rendering, exporting, or further transformation (transpose/augment/etc.).

Why this is its own method:
- Encapsulates the non-trivial expansion logic that maps chord shorthand / chord descriptors to NoteContainer objects, applies optional instrument tuning fingering, and coordinates placement into bars (including splitting a chord event across a bar boundary).
- Keeps Track-level orchestration (bar management, integration with tuning/instrument) separate from lower-level concerns like parsing chord shorthand (NoteContainer.from_chord) and placing notes into a Bar (add_notes / Bar.place_notes).

## Args:
    chords (iterable):
        - An iterable (e.g., list or tuple) where each element is:
            * A chord descriptor acceptable to NoteContainer.from_chord (commonly a chord shorthand string like "Cmaj7"), or
            * A nested list of chord descriptors (lists are treated specially — see behavior below), or
            * None to indicate a rest of the given duration.
        - Elements may be heterogeneous (strings, objects convertible by from_chord). The method does not validate element types beyond attempting conversion via NoteContainer.from_chord and passing values to add_notes.
    duration (int | float, optional):
        - The base duration value passed to add_notes for each top-level chord element. Defaults to 1.
        - Expected to be a numeric, non-zero value acceptable to add_notes / Bar.place_notes. (If an invalid duration is supplied, underlying placement logic may raise exceptions.)

## Returns:
    Track (self)
        - Returns the same Track instance after attempting to place all chord events. This enables fluent chaining.

## Raises:
    InstrumentRangeError:
        - Propagated from add_notes if an instrument is attached to the Track and that instrument's can_play_notes(...) rejects a chord / note container as out of range.
        - Exact trigger: add_notes raises InstrumentRangeError when the instrument cannot play the provided NoteContainer (or note-like input).
    ZeroDivisionError:
        - May be raised indirectly by Bar.value_left() when the remaining space in the last bar equals zero (value_left performs 1.0 / space_left()).
        - This occurs in the split-across-bar logic when add_notes returned False and the code attempts to compute dur = self.bars[-1].value_left().
    Any exceptions raised by NoteContainer.from_chord:
        - E.g., parsing errors from the chord parser or UnexpectedObjectError if the resulting notes are not Note-like. These exceptions propagate unchanged.
    Any exceptions raised by tuning.find_chord_fingering or mingus.core.value.subtract:
        - If a tuning is present, find_chord_fingering is invoked and may raise or return values that cause later errors; value.subtract is used to compute the remainder duration and may raise if given incompatible inputs. These exceptions propagate.

## State Changes:
Attributes READ:
    - self.instrument (checked indirectly via add_notes when instrument is present)
    - self.tuning and self.instrument.tuning via get_tuning() (to determine whether to apply fingering)
    - self.bars (inspected to obtain the last bar when computing remaining space)
    - The last Bar's internal state when calling value_left() (reads space_left/current_beat/length)

Attributes WRITTEN:
    - self.bars: mutated via calls to add_notes which may append Bar instances when the track is empty or when a new bar is needed.
    - The Bar instance(s) inside self.bars: mutated by add_notes / Bar.place_notes (appending placed events and advancing bar state).
    - Local NoteContainer instances created during conversion may be mutated (populated) but those are not persisted as Track attributes unless placed into bars.

## Behavior and edge cases (detailed):
- Top-level iteration:
    - For every element c in chords:
        * If c is None: calls self.add_notes(None, duration) to insert a rest of the given duration.
        * Otherwise: calls the nested helper add_chord(c, duration).

- add_chord behavior:
    - If the argument chord is a list instance:
        * The code interprets this as a grouped or arpeggiated chord sequence and iterates over its elements.
        * For each element c in that list, add_chord(c, duration * 2) is called — i.e., nested-list elements are placed with twice the current duration. (Note: this doubling is recursive; nested lists multiply duration by 2 for each nesting level.)
    - If the argument chord is not a list:
        * A fresh NoteContainer is created and populated by calling NoteContainer().from_chord(chord). This converts the chord descriptor to a NoteContainer (or raises an exception if conversion fails).
        * If a tuning (tun) is present (truthy), the code calls tun.find_chord_fingering(chord, return_best_as_NoteContainer=True). The returned value replaces chord and is expected to be a NoteContainer suitable for placement.
        * The method attempts to place the chord NoteContainer into the track via self.add_notes(chord, duration).
            - If add_notes returns True: placement succeeded and processing continues.
            - If add_notes returns False: the chord did not fit into the current last bar and must be split across the boundary:
                1. Compute dur = self.bars[-1].value_left() — the duration that fits into the current last bar.
                   - This may raise ZeroDivisionError if the bar reports zero remaining space.
                2. Call self.add_notes(chord, dur) to place the portion that fits.
                3. Call self.add_notes(chord, value.subtract(duration, dur)) to place the remainder in one or more subsequent bars (value.subtract computes the remaining duration value). Exceptions from value.subtract or the subsequent add_notes propagate.

- Duration arithmetic and types:
    - The method operates on duration values exactly as provided and as returned by Bar.value_left and value.subtract. It does not coerce types beyond multiplication by 2 for nested-list handling. Passing incompatible types will surface exceptions from underlying calls.

## Constraints:
Preconditions:
    - self must be a valid Track instance with add_notes and get_tuning available (normal Track object).
    - chords must be an iterable. Non-iterable input will raise (TypeError) when iterating.
    - duration should be a numeric value acceptable to add_notes / Bar.place_notes. Passing 0 or non-numeric values may produce exceptions downstream.
    - If a tuning is present (via instrument.tuning or self.tuning), it must implement find_chord_fingering(...) with the accepted keyword argument return_best_as_NoteContainer.

Postconditions:
    - The track (self) has been mutated so that each non-None chord descriptor in chords has been converted to a NoteContainer and an attempt has been made to place it into the bars in sequence, splitting across bar boundaries if needed.
    - For None elements in chords, rests of the given duration have been placed.
    - The method returns self.

## Side Effects:
    - Mutates the Track (self.bars) and the contained Bar(s) by placing notes/rests.
    - Creates temporary NoteContainer instances and may call a tuning object's find_chord_fingering which could allocate or mutate tuning-related state (behavior depends on tuning implementation).
    - No I/O (file, network) is performed by this method itself.
    - Exceptions from helper methods (add_notes, NoteContainer.from_chord, Bar.value_left, tuning.find_chord_fingering, mingus.core.value.subtract) are not caught and will propagate to the caller.

## Implementation notes / tips for re-implementation:
    - Preserve the nested-list semantics: lists in the input sequence represent grouped chord elements whose durations are doubled per nesting level.
    - Use NoteContainer().from_chord(...) to convert chord descriptors; if a tuning is present, call tuning.find_chord_fingering(..., return_best_as_NoteContainer=True) and use its result for placement.
    - Rely on add_notes to append bars as needed and to report whether the chord event fitted into the current bar; when a split is necessary, compute how much fits (last_bar.value_left()), place that portion, and then place the remainder using a duration difference function (value.subtract).
    - Always return self to enable fluent chaining.

### `mingus.containers.track.Track.get_tuning` · *method*

## Summary:
Return the effective tuning for the track, preferring the instrument's tuning when present and truthy; does not modify object state.

## Description:
Known callers and context:
- Track.from_chords — called during chord-to-note conversion to obtain a tuning object used to find chord fingerings for tablature or multi-string instruments.
- set_tuning (indirectly) — callers set tuning via Track.set_tuning; get_tuning centralizes retrieval logic.
Typical lifecycle stage:
- Invoked when generating tablature, chord fingerings, or any operation that needs the track's tuning configuration prior to arranging or placing notes.

Why this is a separate method:
- Encapsulates the priority rule (instrument-level tuning overrides track-level tuning when present and truthy) so callers do not duplicate the conditional logic wherever tuning is needed. This centralization prevents inconsistencies between callers and makes it easy to change the selection policy in one place.

## Args:
- None

## Returns:
- type: object or None
- values:
    - If self.instrument is truthy (not None/False) and self.instrument.tuning is truthy, returns self.instrument.tuning.
    - Otherwise returns self.tuning (which may be a tuning object or None).
- Edge-case returns:
    - Returns None when neither an instrument tuning nor a track tuning is set (both are None or otherwise falsy).
    - If instrument exists but instrument.tuning is an empty/falsy value (e.g., empty list, False), the method falls back to returning self.tuning.

## Raises:
- None: this method performs simple attribute access and does not raise intentionally. AttributeError may propagate only if instrument object exists but lacks a tuning attribute (not expected given Instrument semantics).

## State Changes:
- Attributes READ:
    - self.instrument
    - self.instrument.tuning (if self.instrument is truthy)
    - self.tuning
- Attributes WRITTEN:
    - None (no modifications to self or external objects)

## Constraints:
- Preconditions:
    - No strict preconditions enforced by the method. Caller responsibility:
        - If the returned tuning will be used for tuning-specific operations (e.g., calling find_chord_fingering), the caller must handle a None return or ensure a tuning is configured beforehand.
- Postconditions:
    - The method does not alter any Track or Instrument state.
    - Return value accurately reflects the priority rule: instrument.tuning (when instrument exists and instrument.tuning is truthy) otherwise track.tuning.

## Side Effects:
- None: no I/O, no external service calls, and no mutation of objects outside self.

### `mingus.containers.track.Track.set_tuning` · *method*

## Summary:
Sets the track's tuning value (and mirrors it to an attached instrument, if present), updating the Track's state and returning the Track for chaining.

## Description:
This method centralizes the action of assigning a tuning value to the Track object. When called, it:
- Assigns the provided tuning value to the Track instance (self.tuning).
- If the Track has an associated instrument (self.instrument is truthy), assigns the same value to that instrument's tuning attribute (self.instrument.tuning).

Known callers and context:
- There are no callers visible in this method's body. In typical usage, this method is invoked by user code or by higher-level setup/configuration routines when initialising or changing a Track's tuning before adding notes or bars. It is also useful immediately after attaching or swapping an instrument on the Track to keep instrument and track tunings consistent.
- It is intended as a convenience API to keep Track and its instrument in sync and to support fluent/chained calls because it returns self.

Why this logic is a separate method:
- Encapsulates the common need to update both the Track and its instrument in a single, atomic operation.
- Avoids duplication of the same two assignments throughout user code and encourages a consistent way to set tuning across the codebase.
- Returning self enables method chaining (fluent interface) for setup code.

## Args:
    tuning (any): Value to be assigned as the tuning. The method performs a direct assignment; no validation or type coercion is performed here. The acceptable shape/type of tuning is determined by callers and by any instrument implementation that consumes instrument.tuning (e.g., string, int, list, tuple, or a domain-specific object).

## Returns:
    Track: Returns the same Track instance (self) after applying the tuning. This enables call chaining. There are no alternate or sentinel return values.

## Raises:
    None: The method does not explicitly raise exceptions. However, an AttributeError or other exception may be raised by Python if:
    - self is not a proper Track instance, or
    - self.instrument exists but does not accept assignment to attribute 'tuning' (for example, if instrument has a property with restricted setter behavior).
    These are not raised by this method itself; they are natural Python attribute assignment errors.

## State Changes:
    Attributes READ:
        self.instrument

    Attributes WRITTEN:
        self.tuning
        self.instrument.tuning (only when self.instrument is truthy)

## Constraints:
    Preconditions:
        - The caller should expect that no validation is performed on tuning; provide a value appropriate for the Track and any associated instrument.
        - If self.instrument is present, it must accept assignment to its 'tuning' attribute (i.e., instrument.tuning must be writable).

    Postconditions:
        - After the call, self.tuning == tuning.
        - If self.instrument was truthy at call time, then self.instrument.tuning == tuning.
        - The method returns self.

## Side Effects:
    - Mutates the Track instance (self.tuning).
    - May mutate an external object referenced by self.instrument by setting its tuning attribute.
    - No I/O, network calls, or other external service interactions occur within this method.

### `mingus.containers.track.Track.transpose` · *method*

## Summary:
Transposes every bar in the track by the given interval and direction, mutating the notes contained in those bars in-place and returning the same Track instance.

## Description:
Known callers and context:
- No internal callers of this method are present within the Track implementation. This method is intended to be used by client code or higher-level transformation steps (for example: applying a key change to an entire track prior to rendering, analysis, or playback).
- Typical pipeline stage: composition/arrangement transformation where an entire Track must be transposed as part of a larger operation (e.g., when changing key, preparing material for an instrument with a different range, or shifting harmony).

Why this is a separate method:
- Encapsulates the operation "transpose every Bar in this Track" so callers do not need to iterate over self.bars and call Bar.transpose themselves.
- Centralizes the semantics of transposing a Track (delegation to contained Bar objects) and preserves a fluent API by returning self.

## Args:
    interval (any): The transposition interval to apply to each Bar. The exact accepted types and semantics (for example a string like 'm3' or an integer number of semitones) are delegated to the Bar and ultimately to the Note/NoteContainer.transpose implementations.
    up (bool, optional): Direction flag. True to transpose upward, False to transpose downward. Defaults to True.

## Returns:
    Track: Returns self (the same Track instance), enabling call chaining.
    Edge cases:
    - If the track contains no bars (self.bars is empty), the method returns self immediately with no modifications.

## Raises:
    AttributeError: If any element of self.bars does not have a callable transpose method (i.e., calling bar.transpose(...) fails), Python will raise AttributeError.
    Propagated exceptions from Bar.transpose or the underlying Note/NoteContainer.transpose implementations: Any exception raised while transposing an individual Bar or its contained notes (for example due to an invalid interval) will propagate unchanged.

## State Changes:
Attributes READ:
    self.bars — iterated to access each Bar (the reference to the list is read).

Attributes WRITTEN:
    None of Track's attributes are rebound (self.bars reference is not reassigned). However, the method causes in-place mutation of objects reachable via self.bars: each Bar.transpose(...) may mutate the Bar's internal entries and the Note/NoteContainer objects contained therein.

## Constraints:
Preconditions:
    - self.bars must be an iterable (typically a list) of objects that implement a transpose(interval, up) method (commonly instances of mingus.containers.Bar).
    - The provided interval and up values must be valid for the underlying Bar/Note/NoteContainer.transpose implementations. Validation and error reporting for interval validity are delegated to those implementations.

Postconditions:
    - If the call returns normally (no exception), bar.transpose(interval, up) has been invoked for every bar that was present in self.bars at call time.
    - Contained Note and NoteContainer instances reachable from each Bar will reflect the transposition (mutated in-place).
    - The Track instance is returned (self), allowing further chained calls.

## Side Effects:
    - In-place mutation of the contents of each Bar in self.bars (and therefore any external references to those Note/NoteContainer objects will observe the updated, transposed state).
    - No I/O, no access to external services, and no mutation of global state performed by this method itself (mutations are confined to objects stored in the track's bars).

### `mingus.containers.track.Track.augment` · *method*

## Summary:
Invokes augmentation on every Bar in the track, causing each bar (and its contained NoteContainer objects) to perform their augmentation transformations; returns the same Track instance for chaining.

## Description:
This method iterates over the track's bars list and calls augment() on each Bar. It centralizes the iteration so callers can request "augment everything in this track" without iterating bars themselves.

Known callers and usage context:
- Typically invoked by composition or processing code after populating a Track with bars/notes (after place_notes, add_bar, or from_chords) and before downstream operations such as rendering, exporting (MIDI), further transformations, or analysis.
- Lifecycle stage: called in the post-construction / pre-processing stage when a global augmentation transform must be applied to all measures in the track.
- Rationale for being a separate method: it encapsulates the iteration and delegation to Bar.augment(), avoiding repeated loop logic at call sites and making intent explicit at the Track API level.

## Args:
    None

## Returns:
    Track: Returns self (the same Track instance) to allow method chaining.

## Raises:
    Any exception raised by Bar.augment() will propagate unchanged. Common exceptions that can surface (these are not explicitly raised by this method, but are likely based on Bar.augment() behavior):
    - AttributeError: if a bar's internal entries contain a notes object that is None or does not implement augment().
    - IndexError: if a bar's entries are malformed and indexing entry[2] fails inside Bar.augment().
    - TypeError: if self.bars is not iterable or a bar is not a valid object with augment().
    Notes:
    - This method does not perform defensive validation; it assumes each element in self.bars is a Bar-like object implementing augment().

## State Changes:
    Attributes READ:
        self.bars — iterated to access each Bar instance in the track
    Attributes WRITTEN:
        None on the Track instance itself (no assignment to Track attributes)
    Indirect mutations:
        - Each Bar.augment() call may perform in-place mutations on the Bar and on contained NoteContainer objects (e.g., modifying note values or internal structures). Those mutations are side effects of this method.

## Constraints:
    Preconditions:
        - self.bars must be an iterable (typically a list) containing Bar instances or objects that implement augment().
        - Each bar's augment() must be safe to call in the current context (i.e., bars should be populated according to the Bar/NoteContainer conventions if augment() expects certain structure).
    Postconditions:
        - For every element b in self.bars, b.augment() has been invoked exactly once (in order).
        - The method returns the original Track instance (self), enabling chaining like track.augment().transpose(...).

## Side Effects:
    - No I/O or network calls are performed by this method itself.
    - In-place mutation of each Bar and their contained NoteContainer objects occurs as a consequence of calling Bar.augment().
    - Exceptions originating inside Bar.augment() will propagate to the caller; this method does not catch or translate them.

### `mingus.containers.track.Track.diminish` · *method*

## Summary:
Lower every pitch in each Bar of the Track by one semitone (delegates to each Bar.diminish) and return the Track to allow method chaining; mutates the contents of contained Bar objects in-place.

## Description:
- Known callers and context:
    - No internal callers are recorded in the repository for this method. It is typically invoked by application code or higher-level utilities after a Track has been constructed and populated with Bars and notes (for example, during a global transformation step prior to playback, export, or further processing).
    - Typical lifecycle stage: called after notes/chords are added to the Track (via add_notes, from_chords, direct Bar manipulation) when the caller wants to uniformly lower every contained note by a semitone across the whole Track.
    - This method is analogous to Track.augment and Track.transpose which apply a similar per-Bar operation across the Track.

- Rationale for being a separate method:
    - Encapsulates the common operation "diminish every bar" so callers do not need to repeat iteration and delegation logic.
    - Provides a clear, intention-revealing API at the Track level consistent with other batch-transform methods (augment/transpose), enabling fluent chaining and easier maintenance.

## Args:
None.

## Returns:
    Track: Returns self (the same Track instance) after applying the in-place diminishment to each Bar. If the Track contains no bars, the method is a no-op and still returns self.

## Raises:
    - Propagates any exception raised by Bar.diminish called for each bar. In practice, callers should expect:
        - AttributeError: commonly raised if a Bar contains an entry with a None (a rest) or an entry whose note container does not implement diminish(); Bar.diminish will attempt to call cont[2].diminish() and this will fail if cont[2] is None or lacks the method.
        - Any other exception thrown by Bar.diminish or deeper NoteContainer/Note diminish implementations will propagate unchanged.
    - This method does not catch or wrap exceptions from the per-Bar operations.

## State Changes:
Attributes READ:
    - self.bars (the iterable/list of Bar objects is iterated)

Attributes WRITTEN:
    - No Track-level attributes are reassigned by this method.
    - Mutation occurs inside each Bar in self.bars: Bar.diminish performs in-place changes to the Bar's stored entries (specifically the NoteContainer/Note objects inside each Bar). Therefore, the pitch/accidental state of Notes reachable from self.bars will be changed.

## Constraints:
Preconditions:
    - self.bars should be an iterable of Bar instances (or objects exposing a diminish() method).
    - Each Bar must implement a diminish() method that knows how to lower contained notes; entries inside each Bar are expected to contain note containers (not plain None) unless the caller intentionally handled rests prior to calling diminish.

Postconditions:
    - For every Bar in self.bars for which Bar.diminish completes successfully, all contained Note/NoteContainer objects will have been lowered by one semitone according to the Note/NoteContainer contract.
    - The Track object itself keeps the same identity and Track-level attributes (instrument, name, tuning, bars list object) remain in place; the method returns self.

## Side Effects:
    - In-place mutation of the NoteContainer and Note objects held within each Bar (pitches are lowered).
    - No I/O operations, logging, or external service calls are performed.
    - No new Bar or NoteContainer objects are created by this method; existing contained objects are mutated.

### `mingus.containers.track.Track.__add__` · *method*

## Summary:
Dispatches the right-hand operand of a + expression to the appropriate Track mutator: appends a Bar-like object, or places notes when given a NoteContainer-like object, a name-bearing object, or a string. The method mutates the track by delegating to add_bar or add_notes.

## Description:
This method implements operator overloading for Track so user code can write track + item. It performs a small runtime dispatch based on the shape of value:
- If value has a "bar" attribute, it is treated as a Bar-like object and forwarded to add_bar(value).
- Else if value has a "notes" attribute, it is treated as a NoteContainer-like object and forwarded to add_notes(value).
- Else if value has a "name" attribute or is a string (six.string_types), it is forwarded to add_notes(value).

Dispatch ordering and ambiguity:
- The checks are evaluated in the above order. An object exposing multiple of these attributes will be classified by the first matching condition (e.g., an object with both "bar" and "notes" will be treated as a bar because the "bar" check runs first).

Known callers and context:
- Intended for client code building or modifying a Track using operator syntax (e.g., composition scripts, REPL interaction, or higher-level assembly code). There are no internal calls to __add__ in this file; add_bar and add_notes are used elsewhere directly as well.

Why a separate method:
- Centralizes syntactic convenience (operator +) while delegating validation and mutation logic to add_bar and add_notes. This keeps the operator thin and ensures all invariants and side effects are handled by the specialized methods.

## Args:
    value (any): The right-hand operand to add. Accepted shapes (in order tested):
        - Bar-like: any object with a "bar" attribute (forwarded to add_bar).
        - NoteContainer-like: any object with a "notes" attribute (forwarded to add_notes).
        - Name-bearing or string: any object with a "name" attribute, or any string (six.string_types) (forwarded to add_notes).
    No default. If value matches none of these shapes, the method performs no action and returns None.

## Returns:
    Track | bool | None
    - Track: returned when add_bar(value) is called; add_bar appends the bar and returns the Track instance (self).
    - bool: returned when add_notes(...) is called; add_notes delegates to Bar.place_notes which returns True when the note/rest was placed and False when there was insufficient bar space, so add_notes returns that boolean.
    - None: returned when value does not match any dispatch rule (no action performed).

## Raises:
    The method itself performs only attribute checks and delegation, but exceptions raised by the delegated calls may propagate:
    - InstrumentRangeError:
        - Propagated from add_notes when self.instrument is not None and self.instrument.can_play_notes(note) returns False.
    - ZeroDivisionError:
        - May be propagated from Bar.place_notes (called by add_notes) if duration == 0 or if internals compute 1.0 / duration and duration is zero.
    - TypeError:
        - May be propagated from Bar.place_notes if a non-numeric duration is used (1.0 / duration) or other type mismatches during placement.
    - Any exception raised by NoteContainer(...) conversion:
        - When add_notes or Bar.place_notes attempts to construct a NoteContainer from a string/list/name object, NoteContainer's constructor exceptions propagate up.
    Note: __add__ does not itself raise UnexpectedObjectError; that exception appears in other Track methods (e.g., __setitem__).

## State Changes:
    Note: __add__ delegates the work; it does not directly read or write Track attributes beyond calling methods.
    Attributes READ (via delegated methods):
        - self.instrument (read by add_notes to check instrument range)
        - self.bars (read by add_notes to find or create the last bar)
    Attributes WRITTEN (via delegated methods):
        - self.bars (may be appended to):
            * add_bar appends the provided Bar object to self.bars.
            * add_notes ensures at least one Bar exists and may append a new Bar if the last bar is full; then it places notes into the last bar.

## Constraints:
    Preconditions:
        - Caller should supply a value matching one of the recognized shapes (Bar-like, NoteContainer-like, name-bearing, or string) if they expect a mutation to occur.
        - When adding notes and the Track has an instrument set: the instrument must be able to play the note(s) or add_notes will raise InstrumentRangeError.
        - When adding notes with an explicit duration, duration must be a non-zero numeric value to avoid ZeroDivisionError in Bar.place_notes.

    Postconditions:
        - If add_bar routed: the provided Bar-like object has been appended to self.bars and the Track instance is returned.
        - If add_notes routed: one of:
            * True is returned and the notes/rest were appended to the last Bar (self.bars updated as necessary).
            * False is returned and no changes were made to the targeted Bar because there was insufficient space (but add_notes may have appended a new Bar prior to attempting placement).
        - If value unrecognized: self.bars is unchanged and None is returned.

## Side Effects:
    - Mutates in-memory Track state (self.bars) via the delegated add_bar or add_notes calls.
    - add_notes may create and append a new Bar() when the track has no bars or the last bar is full.
    - May construct NoteContainer instances (via Bar.place_notes) when converting strings, lists, or name-bearing objects.
    - No I/O or external network/service calls are made by __add__ itself.

## Examples (plain usage scenarios):
    - Appending a bar:
        track + some_bar_object  -> appends the bar to track.bars and returns the Track instance.
    - Adding a single note by name:
        track + "C-4"            -> forwards to add_notes; returns True if the note fit in the current bar, False if it did not.
    - Adding a NoteContainer:
        track + note_container   -> forwards to add_notes; behaves like the example above.

These examples illustrate typical outcomes, but the exact boolean returned when adding notes depends on Bar.place_notes semantics (True on successful placement, False on insufficient space).

### `mingus.containers.track.Track.test_integrity` · *method*

## Summary:
Checks whether every bar in the track except the final bar is completely filled; returns a boolean and does not modify the track.

## Description:
This method verifies the "integrity" of the track by confirming that each bar up to (but not including) the last one reports itself as full. It performs a defensive check typically used by calling code before treating a track as complete (for example: finalizing, exporting, rendering, or appending a new bar that assumes previous bars are complete).

Known callers and lifecycle stage:
- No specific callers were present in the provided source snippet. Conceptually, this will be called during validation or finalization steps where a track must be confirmed as internally consistent before further processing (e.g., before playback, export, or committing changes).
- It is implemented as a separate method to encapsulate the integrity check in one place so callers can use a simple boolean check rather than repeating the loop logic each time integrity must be validated.

Why this is a separate method:
- The check is a clear, repeated validation need (check all bars except the last). Extracting it into its own method keeps calling code concise, centralizes the definition of "integrity", and makes unit testing and future changes easier.

## Args:
    None

## Returns:
    bool
        - True if every bar in self.bars except the last one returns True for is_full()
        - False if any such bar returns False
        - Edge cases:
            * If self.bars is empty or contains exactly one bar, the method iterates over an empty slice and returns True (there are no preceding bars that can be incomplete).

## Raises:
    - AttributeError
        * If self.bars is not an iterable or if an element in self.bars does not have an is_full() method, the AttributeError (or another exception like TypeError) raised by the attribute access or call will propagate. The method does not explicitly catch or wrap such exceptions.
    - Any exception raised by Bar.is_full() will propagate unchanged.

## State Changes:
    Attributes READ:
        - self.bars (the list/sequence of bar objects)
        - For each item b in self.bars[:-1], b.is_full() is called (reads bar state)
    Attributes WRITTEN:
        - None (the method does not modify self or any bar)

## Constraints:
    Preconditions:
        - self must have an attribute bars that is an iterable (typically a list) of objects.
        - Each object in self.bars should implement an is_full() method that returns a boolean.
    Postconditions:
        - The method returns True or False as described above.
        - No modification is made to self or the bar objects.

## Side Effects:
    - No I/O performed.
    - No external services called.
    - No mutation of external objects (bars are only queried via is_full()).

## Implementation notes / equivalent behavior:
    - The method loops over self.bars[:-1] (all bars except the last); this slice intentionally excludes the current/last bar because the last bar is often used as a work-in-progress bar that may be partially filled.
    - Equivalent behavior: returns all(b.is_full() for b in self.bars[:-1])

### `mingus.containers.track.Track.__eq__` · *method*

## Summary:
Compares this Track to another object by checking equality of each Bar in self.bars except the final bar; returns True if all compared bars are equal, otherwise False.

## Description:
- Known callers and context:
    - There are no internal callers of this method within the Track class itself. It is invoked by client code when two Track instances (or Track-like objects) are compared using the equality operator (==). Typical contexts include unit tests, track-diffing or equality checks during composition/manipulation workflows.
- Why this logic is a separate method:
    - Implements Python's equality operator for Track objects so that Track instances can be compared with `==`. Centralizing the logic in __eq__ enables consistent behavior wherever equality checks are needed and allows operator overloading instead of repeating comparison code inline.

## Args:
- self: Track
    - The left-hand Track instance whose bars will be compared.
- other: object
    - Any object. The method expects an object with a sequence-like attribute named `bars` (indexable, length-accessible) where elements are comparable to this Track's bars (typically Bar instances).
    - No default value.

## Returns:
- bool
    - True if, for every index x in range(0, len(self.bars) - 1), self.bars[x] == other.bars[x]; otherwise False.
    - Special/edge-case returns:
        - If len(self.bars) <= 1, the method's loop body does not execute and the method returns True (i.e., tracks with 0 or 1 bar are considered equal to any other object that does not raise during access).
        - If all compared bars are equal but the final bar(s) differ, this implementation still returns True because it intentionally (or inadvertently) omits comparing the last bar.

## Raises:
- AttributeError
    - If `other` does not have a `bars` attribute, the attempt to access other.bars will raise AttributeError.
- IndexError
    - If other.bars is shorter than the number of indices iterated (i.e., len(other.bars) < max(0, len(self.bars) - 1)), attempting to access other.bars[x] will raise IndexError.
- Any exception raised by bar comparison
    - Comparing elements via `!=` delegates to the elements' comparison logic (e.g., Bar.__eq__). If that comparison raises, the exception will propagate.

## State Changes:
- Attributes READ:
    - self.bars (sequence of bars)
    - other.bars (sequence of bars on the other object)
- Attributes WRITTEN:
    - None — this method does not modify self or other.

## Constraints:
- Preconditions:
    - self.bars must be a sequence supporting len(...) and indexing.
    - other must provide a `bars` attribute that is indexable for indices 0 .. len(self.bars) - 2 (if len(self.bars) >= 2). In other words, other.bars must have length >= max(0, len(self.bars)-1) to avoid IndexError.
    - Elements of self.bars and other.bars should be comparable with != (typically Bar instances implementing equality).
- Postconditions:
    - No mutation of self or other; only a boolean result is produced.
    - The return value truthfully reflects equality of the compared prefix of bars (all except the last bar of self), per the method's logic.

## Side Effects:
- None. The method performs only in-memory reads and comparisons; it does not perform I/O, call external services, or mutate objects outside of transient local variables.

## Implementation notes and caveats (important for reimplementation):
- The loop iterates x over range(0, len(self.bars) - 1). That means:
    - If len(self.bars) == 0 or 1, the loop is skipped and the method returns True.
    - The final bar of self.bars (index len(self.bars)-1) is never compared against other.bars; this can yield surprising equality results when tracks differ only in their last bar.
- The method relies on the equality semantics of the bar objects (Bar.__eq__). A faithful reimplementation must use the same element-wise comparison operator to preserve behavior.
- Defensive improvements (not present in the current implementation) could include:
    - Verifying that other is a Track (or Track-like) and that its bars length matches self.bars length before comparing to avoid IndexError and to ensure symmetric equality semantics.

### `mingus.containers.track.Track.__getitem__` · *method*

## Summary:
Provides sequence-style access to the track's stored bars by delegating indexing and slicing to the internal bars list; does not modify the Track's state.

## Description:
This method is the Track object's implementation of Python's indexing protocol and is used whenever client code treats a Track as a sequence (explicit indexing, slicing, or iteration via the sequence protocol). Typical call sites include code that needs to retrieve a specific Bar for inspection or mutation (for example to read or modify beats/notes), code that slices a Track to obtain a contiguous list of Bar objects, or iteration constructs that rely on __getitem__ together with __len__ to traverse bars.

This logic is implemented as its own method (rather than inlined at call sites) so that Track presents a standard, list-like interface backed by its internal bars list. By delegating directly to self.bars[index], Track preserves Python list semantics (negative indices, slices, IndexError for out-of-range access) and avoids duplicating list indexing behavior.

## Args:
    index (int or slice): 
        - If an integer, selects a single bar using Python list indexing rules (supports negative indices).
        - If a slice, returns a new list containing the requested contiguous subset of bars.
        - Other index types are unsupported and will propagate a TypeError from the underlying list.

## Returns:
    mingus.containers.bar.Bar or list[mingus.containers.bar.Bar]:
        - When index is an int: returns the Bar instance stored at that position in self.bars.
        - When index is a slice: returns a plain Python list of Bar instances corresponding to the slice.
        - Edge cases:
            * Negative integers behave as with standard lists (e.g., -1 returns the last bar).
            * An empty slice returns an empty list.

## Raises:
    IndexError: If index is an integer and its value is out of the valid range for self.bars (propagated from list.__getitem__).
    TypeError: If index is of a type not supported by list indexing (propagated from list.__getitem__).

## State Changes:
    Attributes READ:
        - self.bars
    Attributes WRITTEN:
        - None (this method does not modify any Track attributes or the bars list)

## Constraints:
    Preconditions:
        - self.bars must be a sequence (the Track initializer ensures self.bars is a list).
        - Callers should pass an integer or slice appropriate for Python list indexing to avoid TypeError.
    Postconditions:
        - The Track instance remains unchanged.
        - The returned value is a direct reference to the Bar stored in self.bars (for integer indexing) or a new list containing references to those Bar objects (for slicing).

## Side Effects:
    - None: there is no I/O, no mutation of external objects by this method itself.
    - Note: although the method does not mutate state, callers that receive a Bar object may mutate that Bar; such mutations will be visible through the Track because the returned Bar is the same object stored in self.bars.

### `mingus.containers.track.Track.__setitem__` · *method*

## Summary:
Assigns a Bar-like object into the track's bars list at the given index, replacing the existing bar and mutating the track's internal bars collection.

## Description:
Known callers and context:
- Called by external code using item-assignment syntax on a Track instance (e.g., track[0] = some_bar) during composition or editing workflows where an existing bar is being replaced.
- There are no internal call sites within the Track class in this repository; usage is expected from higher-level code that builds or modifies a Track's contents (e.g., composition editors, MIDI import/export utilities, or tests).

Why this is a separate method:
- Implements Python item-assignment protocol for Track (supporting track[index] = value) and centralizes validation of the assigned object.
- Ensures only objects that conform to the Bar interface (identified here by having a "bar" attribute) are placed into the track, providing a single validation point and clearer error reporting instead of spreading checks across call sites.

## Args:
    index (int or slice or any object supported by Python list.__setitem__):
        Index or slice passed through to the underlying list assignment semantics.
        - Typical use: integer index (including negative indices) to replace a single bar.
        - Slice assignment is forwarded to list.__setitem__, but this method's validation expects a single Bar-like object (see Constraints), so slice assignments with iterables of bars are not supported by this implementation.
    value (mingus.containers.bar.Bar or any object exposing a "bar" attribute):
        Object to assign into self.bars at the specified index. The method accepts any object that has an attribute named "bar" (duck-typing check) — typically an instance of mingus.containers.bar.Bar or a compatible Bar-like object.

## Returns:
    None
    - As with Python assignment, the method does not return a value.

## Raises:
    UnexpectedObjectError:
        - Raised when the provided value does not have a "bar" attribute.
        - The exact error message is: "Unexpected object '%s', expecting a mingus.containers.Barobject" % value (note: this message reflects the implementation's literal text).
    IndexError:
        - Propagated from the underlying list assignment when the passed index is out of range for self.bars (same behavior as list.__setitem__).
    TypeError:
        - May be raised by the underlying list assignment if index or value types are incompatible with list.__setitem__ semantics (e.g., invalid index type or attempting to assign an incompatible object during slice assignment). This method does not explicitly catch such errors.

## State Changes:
Attributes READ:
    - self.bars (read to perform the index assignment)
Attributes WRITTEN:
    - self.bars (mutated: the element(s) at the specified index are replaced by value)

## Constraints:
Preconditions:
    - self.bars must be an initialized list-like container (Track.__init__ sets self.bars = []).
    - value must expose a "bar" attribute (duck-typed check). In practice, pass an instance of mingus.containers.bar.Bar or another object implementing the same interface.
    - index must be a valid index or slice according to Python list assignment semantics if you expect no IndexError/TypeError to occur.

Postconditions:
    - If no exception is raised, self.bars[index] references the provided value (replacing the previous element at that position).
    - No other elements of self.bars are modified.
    - The method returns None.

## Side Effects:
    - Mutates the Track instance by replacing entries in its internal self.bars list.
    - No I/O, no external service calls, and no global state modifications occur.
    - Does not validate bar contents beyond the presence of a "bar" attribute; it does not check bar completeness, meter, key consistency, or instrument compatibility.

### `mingus.containers.track.Track.__repr__` · *method*

## Summary:
Return a short, read-only string that represents the track as a two-element list [instrument, bars] for debugging and inspection; this does not modify the Track.

## Description:
Known callers and contexts:
- repr(track): explicitly requests the developer-oriented representation.
- str(track) and print(track): because Track does not implement __str__, Python falls back to __repr__, so these will produce the same output in typical usage.
- Logging, debugging, REPL inspection, or error messages where a compact snapshot of the Track is useful.
Lifecycle/context:
- Used during introspection or diagnostic steps. It is not used by the Track's musical-processing methods (add_notes, transpose, saving routines, etc.) and should not be relied on for machine-readable serialization.
Why this logic is its own method:
- Separates presentation/inspection concerns from mutation and processing logic. Having a dedicated __repr__ provides a consistent textual snapshot without affecting object state.

## Args:
- None

## Returns:
- str: The string produced by converting the Python list [self.instrument, self.bars] to a string (i.e., the result of str([self.instrument, self.bars])).
  - Behavior details:
    - The list conversion uses each element's own repr/str representation; for instrument the Instrument object's __repr__ (or __str__) is used, and for bars the list-of-Bar objects is converted using the Bars' representations.
    - Example possible return values (literal strings as produced by Python's list/element representations):
        - "[None, []]" — when instrument is None and there are no bars.
        - "[Instrument(...), [<Bar ...>, <Bar ...>]]" — when instrument and Bar objects provide their own reprs.
  - Edge cases:
    - If instrument or any bar element raises an exception during their conversion to string, that exception will propagate; this method itself performs no exception handling.

## Raises:
- No exceptions are explicitly raised by this method.
- Propagated exceptions:
  - Any exception raised by instrument.__repr__/__str__ or bar.__repr__/__str__ during list-to-string conversion will propagate out of this method.

## State Changes:
- Attributes READ:
    - self.instrument
    - self.bars
- Attributes WRITTEN:
    - None — the method does not mutate the Track instance.

## Constraints:
- Preconditions:
    - The object must be a properly constructed Track instance (instrument and bars attributes present). The Track class initializer creates these attributes, so normal instances meet this requirement.
- Postconditions:
    - The Track object remains unchanged after the call.
    - Caller obtains a str describing [instrument, bars].

## Side Effects:
- No direct I/O, external service calls, or mutations of objects external to self.
- Indirect side effects only if instrument.__repr__/__str__ or Bar.__repr__/__str__ perform side effects (those side effects are not caused by this method and would indicate non-idiomatic implementations of those objects).

### `mingus.containers.track.Track.__len__` · *method*

## Summary:
Return the number of bars contained in this track as a non-negative integer, without modifying the track.

## Description:
This method provides the length of the track by delegating to the container that holds the bars. It is invoked implicitly when Python's built-in len() is called with a Track instance (len(track)). There are no internal callers inside the Track implementation that use __len__ directly; the class's methods access self.bars directly. Typical external call sites include:
- Consumer code that needs the number of bars for iteration, rendering, or exporting (e.g., MIDI export, printing, UI/CLI status).
- Conditional checks for emptiness or sizing logic (e.g., if len(track) == 0).
It is implemented as its own method to provide the standard Python container protocol (support for len(track)) and to encapsulate the bar-counting operation in a single, discoverable location rather than relying on direct attribute access throughout client code.

## Args:
    None

## Returns:
    int: The number of bar objects currently stored in the track's bars container.
         - Always a non-negative integer.
         - Returns 0 when the track contains no bars.
         - If the underlying bars container implements a custom __len__, that result is returned.

## Raises:
    AttributeError: If the Track instance does not have a bars attribute (this should not occur for properly initialized Track objects).
    Any exception raised by calling len(self.bars) (for example, if self.bars is a proxy object whose __len__ raises) will propagate unchanged.

## State Changes:
    Attributes READ:
        self.bars
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - The Track instance should be properly initialized so that self.bars exists and is a sequence-like object (the class sets self.bars = [] in __init__).
    Postconditions:
        - The Track object is not mutated by this call.
        - The return value accurately reflects the current length of the bars container at call time.

## Side Effects:
    - None. This method performs no I/O, external calls, or mutations of objects outside of reading self.bars.

