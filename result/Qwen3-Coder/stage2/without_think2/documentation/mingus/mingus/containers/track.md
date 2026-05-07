# `track.py`

## `mingus.containers.track.Track` · *class*

## Summary:
Represents a musical track composed of sequential bars, supporting note addition, chord conversion, and musical transformations.

## Description:
The Track class serves as a container for musical compositions, organizing musical content into sequential bars. It provides methods for adding notes and chords, managing instrument constraints, and performing musical transformations such as transposition, augmentation, and diminishment. Tracks can be associated with instruments to enforce range constraints and support tablature tuning. The class supports flexible musical content creation through various addition methods and provides utility functions for musical analysis and modification.

## State:
- bars (list): Collection of Bar objects representing the musical content of the track
  - Type: list of mingus.containers.bar.Bar objects
  - Valid range: Empty list or list containing Bar objects
  - Invariant: Bars are maintained in sequential order
- instrument (Instrument or None): Associated instrument for range checking and musical context
  - Type: mingus.containers.instrument.Instrument or None
  - Valid range: None or valid Instrument instance
  - Invariant: When set, must support can_play_notes() method
- name (str): Name identifier for the track, used when saving MIDI files
  - Type: str
  - Valid range: String value, defaults to "Untitled"
  - Invariant: Should remain consistent during track lifecycle
- tuning (Tuning or None): Tuning configuration for tablature support
  - Type: mingus.containers.tuning.Tuning or None
  - Valid range: None or valid Tuning instance
  - Invariant: When set, must support find_chord_fingering() method

## Lifecycle:
- Creation: Instantiate with optional instrument parameter using `Track(instrument=None)`
- Usage: Add musical content using `add_bar()`, `add_notes()`, or `from_chords()` methods. Apply transformations with `transpose()`, `augment()`, or `diminish()`. Access content via indexing or iteration.
- Destruction: Standard Python garbage collection handles cleanup

## Method Map:
```mermaid
graph TD
    A[Track.__init__] --> B[Track.bars = []]
    B --> C[Track.instrument = instrument]
    A --> D[Track.name = "Untitled"]
    A --> E[Track.tuning = None]
    
    F[Track.add_bar] --> G[Track.bars.append(bar)]
    G --> H[Track.return self]
    
    I[Track.add_notes] --> J[Instrument validation if instrument set]
    J --> K[Track.bars[-1].place_notes(note, duration)]
    K --> L[Track.return self]
    
    M[Track.from_chords] --> N[Track.get_tuning()]
    N --> O[add_chord helper function]
    O --> P[Track.add_notes(chord, duration)]
    P --> Q[Track.add_notes(chord, value.subtract(duration, dur))]
    
    R[Track.transpose] --> S[Track.bars[i].transpose(interval, up)]
    S --> T[Track.return self]
    
    U[Track.augment] --> V[Track.bars[i].augment()]
    V --> W[Track.return self]
    
    X[Track.diminish] --> Y[Track.bars[i].diminish()]
    Y --> Z[Track.return self]
    
    AA[Track.__add__] --> AB[Track.add_bar(value) or Track.add_notes(value)]
    
    AC[Track.__eq__] --> AD[Compare bars]
    
    AE[Track.__getitem__] --> AF[Return self.bars[index]]
    
    AG[Track.__setitem__] --> AH[Validate bar object]
    AH --> AI[Set self.bars[index] = value]
    
    AJ[Track.__len__] --> AK[Return len(self.bars)]
```

## Raises:
- InstrumentRangeError: Raised in `add_notes()` when a note is outside the instrument's playable range
- UnexpectedObjectError: Raised in `__setitem__()` when attempting to assign an invalid object to a track bar

## Example:
```python
# Create a track with an instrument
instrument = Instrument()
track = Track(instrument)

# Add musical content
track.add_notes("C-E-G", 4)  # Add a chord
track.add_notes("D-F-A", 4)  # Add another chord

# Convert chords to notes
chords = ["C", "G", "Am"]
track.from_chords(chords, duration=2)

# Transform the track
track.transpose("P5")  # Transpose up a perfect fifth
track.augment()        # Double note durations

# Access track content
for i in range(len(track)):
    bar = track[i]
    print(f"Bar {i}: {bar}")
```

### `mingus.containers.track.Track.__init__` · *method*

## Summary:
Initializes a Track object with an optional instrument and empty bar list.

## Description:
The `__init__` method sets up the basic structure of a Track instance by initializing an empty list of bars and assigning an optional instrument. This method serves as the constructor for the Track class, establishing the fundamental state that defines a musical track.

## Args:
    instrument (Instrument, optional): An optional instrument object to associate with the track. Defaults to None.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.bars: Initialized to an empty list
        - self.instrument: Set to the provided instrument parameter or None

## Constraints:
    Preconditions: None
    Postconditions: 
        - self.bars will be an empty list
        - self.instrument will be set to the provided value or None

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `mingus.containers.track.Track.add_bar` · *method*

## Summary:
Adds a musical bar to the track's collection of bars, extending the track's musical content.

## Description:
This method appends a Bar object to the internal list of bars maintained by the Track instance. It enables the construction of musical compositions by sequentially adding measures to a track. The method is typically called during the process of building a musical piece, where individual bars are created and added to form a complete composition. This method follows the fluent interface pattern by returning the Track instance itself, allowing for method chaining.

## Args:
    bar (Bar): A Bar object representing a musical measure to be added to the track.

## Returns:
    Track: Returns the Track instance itself, enabling method chaining.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.bars (appends the bar to the list)

## Constraints:
    Preconditions: The bar argument must be an instance of the Bar class.
    Postconditions: The bar is appended to the self.bars list, increasing its length by one.

## Side Effects:
    None

### `mingus.containers.track.Track.add_notes` · *method*

## Summary:
Adds musical notes to the track's bar structure, creating new bars as needed and handling instrument validation.

## Description:
This method appends musical notes to the track's collection of bars, automatically managing bar creation when necessary. It validates that notes fall within the instrument's playable range when an instrument is assigned to the track. The method integrates with the bar management system to ensure proper musical structure organization. This logic is encapsulated in its own method to separate concerns between track-level bar management and note placement logic.

## Args:
    note (str or list): Musical note(s) to add to the track. Can be a single note string or list of notes.
    duration (float, optional): Duration value for the note(s). Defaults to 4 (quarter note).

## Returns:
    NoteContainer: A container holding the added notes, returned from the underlying bar's place_notes method.

## Raises:
    InstrumentRangeError: When an instrument is assigned to the track and the note(s) fall outside the instrument's playable range.

## State Changes:
    Attributes READ: self.instrument, self.bars
    Attributes WRITTEN: self.bars (appends new Bar instances when needed)

## Constraints:
    Preconditions: The track object must be properly initialized with a valid bar structure.
    Postconditions: The note(s) are added to the most recent bar, or a new bar is created if the current one is full.

## Side Effects:
    None

### `mingus.containers.track.Track.get_notes` · *method*

## Summary:
Returns a generator that iterates through all notes in the track, yielding structured note information from each bar.

## Description:
This method provides a convenient way to access all musical notes contained within the track's bars. It iterates through each bar in the track's bar collection and yields tuples containing beat position, note duration, and note information for each note.

The method is implemented as a generator to enable efficient processing of large tracks without loading all notes into memory simultaneously. This approach is particularly useful when working with long musical compositions.

## Args:
    None

## Returns:
    generator: A generator yielding tuples of (beat, duration, notes) where:
        - beat (float): The beat position within the bar (typically 0.0 to 1.0)
        - duration (float): The duration of the note(s) in beats
        - notes (NoteContainer): Container holding the actual notes for this beat/duration

## Raises:
    None explicitly raised

## State Changes:
    - Attributes READ: self.bars
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: The track must have a valid self.bars attribute containing iterable bar objects
    - Postconditions: The returned generator can only be consumed once and cannot be reset

## Side Effects:
    None

### `mingus.containers.track.Track.from_chords` · *method*

## Summary:
Populates a track with musical chords and handles complex chord structures, including nested lists and null values.

## Description:
This method transforms a sequence of chord specifications into musical notes within the track's bar structure. It supports various input formats including chord shorthand strings, nested lists of chords, and null values for rests. The method intelligently handles chord fingering when a tuning is applied and manages note placement across multiple bars when necessary. It's designed to be a high-level interface for building musical tracks from chord progressions.

## Args:
    chords (list): A sequence of chord specifications, which can be:
        - Chord shorthand strings (e.g., "C", "G7", "Am")
        - Lists of chords that will be recursively processed
        - None values representing rests
    duration (float, optional): Base duration for each chord. Defaults to 1.0.

## Returns:
    Track: The current track instance, enabling method chaining.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.bars, self.tuning
    Attributes WRITTEN: self.bars (modifies existing bars or creates new ones)

## Constraints:
    Preconditions:
        - The track must be properly initialized with a valid bar structure
        - The chords parameter must be iterable
        - Each chord in the sequence must be a valid chord shorthand string, list, or None
    Postconditions:
        - The track's bars contain the specified chords with appropriate durations
        - The method returns the same track instance for chaining

## Side Effects:
    None

### `mingus.containers.track.Track.get_tuning` · *method*

## Summary:
Returns the tuning configuration for the track, prioritizing instrument-specific tuning over track-level tuning.

## Description:
This method retrieves the appropriate tuning configuration for the track by checking if an instrument is assigned and has a defined tuning. If so, it returns the instrument's tuning; otherwise, it falls back to the track's own tuning setting. This design allows for flexible tuning assignment where individual instruments can override the track-wide default.

## Args:
    None

## Returns:
    The tuning configuration, which could be either the instrument's tuning (if available) or the track's tuning setting.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.instrument, self.instrument.tuning, self.tuning
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method assumes self.instrument and self.tuning are properly initialized, though they may be None.
    Postconditions: The returned value is either the instrument's tuning or the track's tuning, with no modification to the object's state.

## Side Effects:
    None

### `mingus.containers.track.Track.set_tuning` · *method*

## Summary:
Sets the tuning for a track's instrument and the track itself, updating both the instrument's tuning and the track's tuning attribute.

## Description:
This method configures the tuning of a musical track, either for an instrument if one is assigned or for the track itself. It serves as a centralized way to manage tuning settings for tracks in the mingus music composition framework. The method is typically called during track initialization or when changing the tuning of an existing track. When an instrument is assigned to the track, both the instrument's tuning and the track's tuning attribute are updated to the provided tuning value.

## Args:
    tuning: The tuning configuration to apply. This can be any valid tuning specification compatible with the instrument's tuning requirements, typically a list of note names or frequency values representing the pitch of each string.

## Returns:
    Track: Returns self to enable method chaining, allowing for fluent interface patterns.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.instrument
    Attributes WRITTEN: self.instrument.tuning, self.tuning

## Constraints:
    Preconditions: The tuning parameter should be compatible with the expected tuning format for the instrument. The method assumes that if an instrument exists, it can accept the provided tuning value.
    Postconditions: Both the instrument's tuning (if present) and the track's tuning attribute are updated to the provided tuning value. If no instrument is present, only the track's tuning attribute is updated.

## Side Effects:
    None

### `mingus.containers.track.Track.transpose` · *method*

## Summary:
Transposes all musical notes in the track by a specified interval either up or down.

## Description:
This method applies a transposition operation to all bars within the track, effectively shifting the pitch of all musical notes by a specified number of semitones. It iterates through each bar in the track and delegates the transposition task to each bar's transpose method. This allows for bulk transposition of entire musical pieces with a single method call.

The method is designed as a separate function to provide a clean interface for transposing entire tracks while maintaining consistency with the existing bar-level transposition logic. This promotes code reuse and ensures uniform musical transposition behavior across different levels of the musical hierarchy.

## Args:
    interval (int): The number of semitones to transpose by. Positive values transpose up, negative values transpose down.
    up (bool): Direction of transposition. True for upward transposition, False for downward. Defaults to True.

## Returns:
    Track: Returns self to enable method chaining.

## Raises:
    AttributeError: If any bar in self.bars does not support the transpose method.
    TypeError: If the interval parameter is not an integer or compatible numeric type.

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.bars must be iterable
    - Each element in self.bars must support a transpose(interval, up) method
    - The interval parameter must be a numeric type
    Postconditions: 
    - All notes contained in all bars within self.bars will be transposed by the specified interval in the specified direction

## Side Effects:
    Mutates the individual Note objects contained within the NoteContainer objects accessed via the bars in self.bars by calling their transpose method.

### `mingus.containers.track.Track.augment` · *method*

## Summary:
Applies the augment() method to all bars in the track, raising the pitch of notes by a semitone throughout the entire track.

## Description:
This method iterates through all bars contained in the track and applies the augment() method to each one. It is designed to uniformly raise the pitch of all musical notes within the track by one semitone, making it useful for transposing musical compositions. The method follows the standard pattern of returning self to enable method chaining. This approach ensures consistent pitch modification across the entire musical piece.

## Args:
    None

## Returns:
    Track: Returns the track instance itself, enabling method chaining.

## Raises:
    AttributeError: If any bar in self.bars does not have an augment() method.

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.bars must be iterable
    - Each item in self.bars must have an augment() method
    Postconditions: 
    - The augment() method will be called on each bar in self.bars, modifying the pitch of contained notes by raising them one semitone

## Side Effects:
    None

### `mingus.containers.track.Track.diminish` · *method*

## Summary:
Reduces the dynamic level of all musical elements within the track by diminishing each bar's contents.

## Description:
This method applies the diminish operation to every bar in the track, effectively reducing the volume/intensity of all musical elements contained within. It is designed to be part of a musical composition pipeline where dynamic control is needed across an entire track rather than individual bars. The method iterates through all bars in the track and calls the diminish method on each one.

## Args:
    None

## Returns:
    Track: Returns self to enable method chaining for fluent interface patterns.

## Raises:
    None

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.bars must be iterable
    - Each item in self.bars must have a diminish method
    Postconditions:
    - All bars in self.bars will have their dynamic levels reduced

## Side Effects:
    None

### `mingus.containers.track.Track.__add__` · *method*

## Summary:
Adds musical content to a track by appending bars or notes, supporting multiple input types through dynamic dispatch.

## Description:
This method enables flexible addition of musical content to a Track object by dynamically determining the appropriate action based on the type of object being added. It serves as a unified interface for incorporating musical elements into a track, allowing users to add complete bars, note collections, or note names without needing to know the specific underlying method. The method acts as a dispatcher that routes the operation to either `add_bar()` or `add_notes()` based on object attributes.

The method checks for specific attributes to determine the appropriate action:
- If the value has a "bar" attribute, it calls `add_bar()` to append the bar
- If the value has a "notes" attribute, it calls `add_notes()` to add notes to the last bar
- If the value has a "name" attribute or is a string, it calls `add_notes()` to add note names to the last bar

## Args:
    value: The musical content to add, which can be:
        - A Bar object (with a "bar" attribute)
        - A NoteContainer object (with a "notes" attribute)  
        - A string representing note names (has "name" attribute or is string type)

## Returns:
    Track: Returns self to enable method chaining, allowing multiple additions to be performed consecutively.

## Raises:
    InstrumentRangeError: When adding notes to a track with an instrument that cannot play those notes.
    UnexpectedObjectError: When setting a bar using __setitem__ with an object that doesn't have a "bar" attribute.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.bars (modified by delegation to add_bar or add_notes methods)

## Constraints:
    Preconditions: The Track object must be properly initialized with a bars list.
    Postconditions: The track's bars list will contain the newly added musical content, with proper handling of bar boundaries.

## Side Effects:
    None

### `mingus.containers.track.Track.test_integrity` · *method*

## Summary:
Checks that all bars in the track (except the last one) are completely filled with notes.

## Description:
This method validates the structural integrity of a Track object by ensuring that all bars except the final bar are completely full. It's typically called during track construction or modification to verify proper bar filling. The method is designed to be lightweight and efficient, iterating through all but the last bar to check their completeness. This validation ensures that musical pieces maintain proper rhythmic structure where intermediate bars are fully populated before proceeding to the next section.

## Args:
    None

## Returns:
    bool: True if all bars except the last one are full, False otherwise.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Track object must have a bars attribute containing Bar objects, and each Bar object must have a working is_full() method.
    Postconditions: The method returns a boolean value indicating whether the track integrity check passes.

## Side Effects:
    None

### `mingus.containers.track.Track.__eq__` · *method*

## Summary:
Compares two Track objects for equality by checking if their bar collections are identical, excluding the last bar.

## Description:
This method implements the equality comparison operator (`==`) for Track objects. It iterates through the bars of both tracks and compares them sequentially, stopping at the second-to-last bar. Due to the implementation, only bars at indices 0 through len(self.bars) - 2 are compared, effectively excluding the final bar from the comparison.

## Args:
    other (Track): Another Track object to compare against this instance.

## Returns:
    bool: True if all bars except the last one in both tracks are equal, False otherwise.

## Raises:
    None explicitly raised, but may raise exceptions from underlying bar comparisons.

## State Changes:
    Attributes READ: self.bars

## Constraints:
    Preconditions: 
    - The 'other' parameter must be a Track object
    - Both tracks must have at least one bar (len(self.bars) > 0)
    - The length of self.bars and other.bars should be comparable
    Postconditions:
    - Returns a boolean value indicating equality of the tracks' bar sequences (excluding last bar)

## Side Effects:
    None

### `mingus.containers.track.Track.__getitem__` · *method*

## Summary:
Retrieves a bar from the track by its index position.

## Description:
Provides indexed access to the bars contained within the track. This method enables iteration over the track's bars and direct access to specific bars using standard Python indexing conventions. The method delegates to the underlying bars collection's indexing mechanism.

## Args:
    index (int): The zero-based index of the bar to retrieve from the track's internal bars collection.

## Returns:
    Bar: The bar object located at the specified index position within the track.

## Raises:
    IndexError: When the provided index is out of bounds for the track's bars collection. This occurs when index is negative and its absolute value exceeds the number of bars, or when index is greater than or equal to the number of bars in the track.

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The track must contain at least one bar, and the index must be a valid integer within the range [-len(self.bars), len(self.bars)).
    Postconditions: The returned Bar object maintains its original state and is not modified by this operation.

## Side Effects:
    None

### `mingus.containers.track.Track.__setitem__` · *method*

## Summary:
Sets a bar at the specified index in the track's bars collection, validating that the assigned value is a Bar object.

## Description:
This method provides indexed assignment functionality for the Track class's bars collection. It ensures type safety by verifying that the value being assigned is a Bar object before performing the assignment. This validation prevents accidental assignment of incompatible objects to the bars collection.

## Args:
    index (int): The position in the bars collection where the bar should be placed
    value (object): The object to assign at the specified index

## Returns:
    None: This method does not return a value

## Raises:
    UnexpectedObjectError: When the provided value does not have a 'bar' attribute, indicating it is not a valid Bar object

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: self.bars

## Constraints:
    Preconditions: 
    - The index must be a valid integer index for the bars collection
    - The value must have a 'bar' attribute to be considered a valid Bar object
    - The bars collection must be initialized and accessible
    
    Postconditions:
    - The bar at the specified index is replaced with the provided value
    - The value is validated to be a Bar object before assignment

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `mingus.containers.track.Track.__repr__` · *method*

## Summary:
Returns a string representation of the track showing its instrument and bars.

## Description:
This method provides a string representation of the Track object by converting its instrument and bars attributes into a list format. It is primarily used for debugging and development purposes to quickly visualize the track's contents. The method is automatically called when the built-in `repr()` function is applied to a Track instance.

## Args:
    None

## Returns:
    str: A string representation of the track containing a list with the instrument and bars.

## Raises:
    None

## State Changes:
    Attributes READ: self.instrument, self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Track object must be initialized with valid instrument and bars attributes.
    Postconditions: The returned string accurately represents the current state of the track's instrument and bars.

## Side Effects:
    None

### `mingus.containers.track.Track.__len__` · *method*

## Summary:
Returns the number of bars contained in the track.

## Description:
This method provides a standard interface for determining the length of a Track object by returning the count of bars it contains. It is typically called during serialization, iteration, or length-based comparisons of musical tracks.

## Args:
    None

## Returns:
    int: The number of bars in the track. Returns 0 if the track contains no bars.

## Raises:
    None

## State Changes:
    Attributes READ: self.bars
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The track object must be properly initialized with a bars attribute that supports the len() function.
    Postconditions: The method returns an integer representing the count of bars in the track without modifying the track's state.

## Side Effects:
    None

