# `note.py`

## `mingus.containers.note.Note` · *class*

## Summary:
Represents a musical note with name, octave, MIDI channel, and velocity properties.

## Description:
The Note class encapsulates musical note information including pitch (name and octave), MIDI channel, and velocity. It provides methods for manipulating note properties such as transposition, octave changes, and conversion between different representations. This class serves as a fundamental building block for musical notation and MIDI operations in the mingus library.

## State:
- name (str): The note name (e.g., "C", "D#", "Eb"). 
- octave (int): The octave number (typically 0-10).
- channel (int): MIDI channel number (0-15).
- velocity (int): MIDI velocity value (0-127).

## Lifecycle:
- Creation: Instantiate with note name, octave, and optional dynamics (channel, velocity)
- Usage: Call various manipulation methods like transpose(), octave_up(), augment(), etc.
- Destruction: No special cleanup required; uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[Note.__init__] --> B[set_note|from_int]
    B --> C[transpose]
    B --> D[octave_up|octave_down]
    B --> E[augment|diminish]
    B --> F[change_octave]
    C --> G[to_hertz|from_hertz]
    D --> H[to_shorthand|from_shorthand]
    E --> I[remove_redundant_accidentals]
    F --> J[measure]
    G --> K[__int__]
    H --> L[__int__]
    I --> M[__int__]
    J --> N[__int__]
    A --> O[__lt__|__eq__|__gt__|__le__|__ge__|__ne__|__repr__]
    C --> P[__repr__]
```

## Raises:
- NoteFormatError: When invalid note representations are provided to set_note() or from_shorthand()
- ValueError: When invalid MIDI channel (0-15) or velocity (0-127) values are set via set_channel() or set_velocity()

## Example:
```python
# Create a note
note = Note("C", 4)  # Middle C
print(note)  # 'C-4'

# Change octave
note.octave_up()
print(note)  # 'C-5'

# Transpose up by a major third
note.transpose("M3")
print(note)  # 'E-5'

# Convert to frequency
frequency = note.to_hertz()  # ~660 Hz
```

### `mingus.containers.note.Note.__init__` · *method*

## Summary:
Initializes a Note object with a musical note name, octave, and optional dynamics properties.

## Description:
The Note.__init__ method serves as the primary constructor for Note objects, supporting multiple input formats for specifying musical notes. It processes various parameter combinations to properly initialize a note's musical properties and dynamics settings. This method acts as a factory that routes initialization to appropriate internal methods based on the type of the name parameter.

## Args:
    name (str, int, or Note-like object): Musical note specification. Can be a string (e.g., "C", "D#"), an integer representing MIDI note number, or an object with name, octave, and dynamics attributes. Defaults to "C".
    octave (int): Octave number for the note. Defaults to 4.
    dynamics (dict): Dictionary containing dynamic properties like velocity and channel. Defaults to None.
    velocity (int): MIDI velocity value (0-127). Defaults to None.
    channel (int): MIDI channel number (0-15). Defaults to None.

## Returns:
    None: This method initializes the object in-place and does not return a value.

## Raises:
    NoteFormatError: When the name parameter cannot be processed due to invalid format or unsupported type.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave, self.channel, self.velocity

## Constraints:
    Preconditions: 
    - If name is a string, it must be a valid musical note name
    - If name is an integer, it represents a valid MIDI note number
    - If name is an object with name attribute, it must have valid name, octave, and dynamics attributes
    - Velocity must be between 0-127 if provided
    - Channel must be between 0-15 if provided
    
    Postconditions:
    - The Note object is properly initialized with name, octave, and dynamics
    - Dynamics dictionary contains velocity and channel if provided via dedicated parameters
    - Object state reflects the musical note specification provided

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only modifies the internal state of the Note object.

### `mingus.containers.note.Note.dynamics` · *method*

## Summary:
Returns a dictionary containing the MIDI channel and velocity dynamics of the note.

## Description:
Provides access to the MIDI dynamics attributes (channel and velocity) of the note as a dictionary. This property allows convenient retrieval of both dynamics parameters together without having to access them separately.

## Args:
    None

## Returns:
    dict[str, int]: A dictionary with keys "channel" and "velocity" mapping to their respective integer values. Channel is typically 0-15 and velocity is typically 0-127.

## Raises:
    None

## State Changes:
    Attributes READ: self.channel, self.velocity
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must be properly initialized with channel and velocity attributes.
    Postconditions: The returned dictionary contains the current channel and velocity values of the note.

## Side Effects:
    None

### `mingus.containers.note.Note.set_channel` · *method*

## Summary:
Sets the MIDI channel for this note with validation that the channel is within the valid range of 0-15.

## Description:
This method assigns a MIDI channel value to the note object, ensuring it falls within the standard MIDI channel range of 0-15. It is used to configure the MIDI channel that will be associated with this note during MIDI playback or processing. The method is typically called when setting up note properties programmatically or when updating existing note configurations.

## Args:
    channel (int): MIDI channel number, must be an integer between 0 and 15 inclusive.

## Returns:
    None: This method does not return any value.

## Raises:
    ValueError: Raised when the channel parameter is not within the valid range of 0-15.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.channel

## Constraints:
    Preconditions: The channel parameter must be an integer within the range [0, 15].
    Postconditions: After execution, self.channel will contain the validated channel value.

## Side Effects:
    None: This method only modifies the internal state of the Note object and has no external side effects.

### `mingus.containers.note.Note.set_velocity` · *method*

## Summary:
Sets the MIDI velocity value for the note, validating that it falls within the valid MIDI range of 0-127.

## Description:
This method assigns a velocity value to the note's velocity attribute after validating that it conforms to MIDI standards. The velocity represents the intensity or loudness of the note playback, with valid values ranging from 0 (silent) to 127 (maximum velocity). This method is called during note initialization when velocity is provided via the dynamics parameter, and can also be called independently to modify an existing note's velocity.

## Args:
    velocity (int): MIDI velocity value, must be an integer between 0 and 127 inclusive

## Returns:
    None: This method does not return any value

## Raises:
    ValueError: When velocity is outside the valid MIDI range of 0-127

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.velocity

## Constraints:
    Preconditions: The velocity argument must be an integer within the range [0, 127)
    Postconditions: The self.velocity attribute is updated to the provided velocity value

## Side Effects:
    None: This method only modifies the object's internal state and has no external side effects

### `mingus.containers.note.Note.set_note` · *method*

## Summary:
Sets the note name and octave while configuring dynamic properties like velocity and channel.

## Description:
Configures a Note object with a specified musical note name and octave, while also setting optional dynamic properties such as velocity and MIDI channel. This method supports two formats for note names: either a single note name (like "C") or a note name with octave separated by a hyphen (like "C-4"). The method validates note names and properly handles dynamic properties passed via explicit arguments or a dynamics dictionary.

## Args:
    name (str): Musical note name, either standalone (e.g., "C") or with octave (e.g., "C-4"). Defaults to "C".
    octave (int): Octave number for the note. Defaults to 4.
    dynamics (dict, optional): Dictionary containing dynamic properties like "velocity" and "channel". Defaults to None.
    velocity (int, optional): MIDI velocity value (0-127). Defaults to None.
    channel (int, optional): MIDI channel number (0-15). Defaults to None.

## Returns:
    Note: Returns self to allow method chaining.

## Raises:
    NoteFormatError: When the note name format is invalid or the note name is not valid according to musical conventions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave, self.velocity, self.channel

## Constraints:
    Preconditions: 
    - Note name must be valid according to musical conventions (validated by notes.is_valid_note())
    - Velocity must be between 0 and 127 inclusive
    - Channel must be between 0 and 15 inclusive
    - Note name format must be either a single note name or note-octave combination separated by a hyphen
    
    Postconditions:
    - self.name is set to the validated note name
    - self.octave is set to the provided octave value
    - self.velocity is set according to velocity argument or dynamics dictionary
    - self.channel is set according to channel argument or dynamics dictionary

## Side Effects:
    None

### `mingus.containers.note.Note.empty` · *method*

## Summary:
Resets the Note object to its default empty state by clearing the note name, setting octave to zero, and restoring default channel and velocity values.

## Description:
The `empty` method clears the current note information and resets the Note object to a default uninitialized state. This method is useful for reusing Note instances or preparing them for new note assignments. It sets the note name to an empty string, octave to zero, and restores the channel and velocity to their default values.

This method was implemented as a separate function to provide a clean, reusable way to reset a Note instance to its initial state without having to manually set each attribute, improving code readability and maintainability.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.name: Set to empty string ""
    - self.octave: Set to 0
    - self.channel: Set to default channel value (_DEFAULT_CHANNEL)
    - self.velocity: Set to default velocity value (_DEFAULT_VELOCITY)

## Constraints:
    Preconditions: None
    Postconditions: The Note object will have name="", octave=0, and channel/velocity set to their respective default values

## Side Effects:
    None

### `mingus.containers.note.Note.augment` · *method*

## Summary:
Applies a sharp accidental to the note name, converting flat notes to their sharp equivalents or adding sharps to natural notes.

## Description:
Modifies the note's name attribute by applying an augmentation operation. This method follows the musical convention where natural notes are sharpened (e.g., "C" becomes "C#") and flat notes are converted to sharps (e.g., "Db" becomes "D"). This is part of a pair of complementary methods alongside `diminish()`.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.name
    Attributes WRITTEN: self.name

## Constraints:
    Preconditions: The note name must be a valid musical note string that can be processed by the underlying `notes.augment` function.
    Postconditions: The note's name attribute will be modified to reflect the augmented version of the original note name.

## Side Effects:
    None

### `mingus.containers.note.Note.diminish` · *method*

## Summary:
Reduces the pitch of a musical note by one semitone by applying a flat accidental.

## Description:
This method modifies the note's name attribute to flatten the note by one semitone. It applies the diminishing operation to the current note name, which either adds a flat accidental ("b") to a natural note or removes a sharp accidental ("#") from a sharp note. This method is part of the musical accidentals manipulation suite alongside augment().

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.name
    Attributes WRITTEN: self.name

## Constraints:
    Preconditions: The note name must be a valid musical note string that can be processed by the notes.diminish function
    Postconditions: The note name will be modified to represent the same pitch one semitone lower

## Side Effects:
    None

### `mingus.containers.note.Note.change_octave` · *method*

## Summary:
Adjusts the octave of a musical note by a specified difference, ensuring octaves never drop below zero.

## Description:
Modifies the octave attribute of a musical note by adding the provided difference value. This method serves as a core building block for octave manipulation operations, with safeguards to prevent negative octave values. It is primarily used internally by the `octave_up()` and `octave_down()` convenience methods, which provide more semantic ways to adjust octaves by single steps.

## Args:
    diff (int): The amount to change the octave by (positive or negative integer)

## Returns:
    None: This method modifies the object in-place and does not return a value

## Raises:
    None: This method does not explicitly raise any exceptions

## State Changes:
    Attributes READ: self.octave
    Attributes WRITTEN: self.octave

## Constraints:
    Preconditions: The note object must have an octave attribute that can be incremented
    Postconditions: The octave attribute will be updated to (original_octave + diff), but will never be less than 0

## Side Effects:
    None: This method only modifies the internal state of the Note object

### `mingus.containers.note.Note.octave_up` · *method*

## Summary:
Increases the octave of the note by one position.

## Description:
This method increments the note's octave by exactly one octave. It serves as a convenient interface for raising a note's pitch by one octave without manually calculating the octave offset.

## Args:
    None

## Returns:
    None

## Raises:
    NoteFormatError: If the note cannot be properly formatted after the octave change.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: The octave attribute of the note object is modified.

## Constraints:
    Preconditions: The note object must be properly initialized with a valid octave value.
    Postconditions: The note's octave will be increased by exactly one octave.

## Side Effects:
    None

### `mingus.containers.note.Note.octave_down` · *method*

## Summary:
Decreases the note's octave by one semitone, ensuring the octave never goes below zero.

## Description:
This method reduces the octave of the musical note by one position. It is a convenience method that delegates to the underlying `change_octave` method with a decrement of 1. This allows for easy lowering of note octaves in musical compositions or calculations.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: self.octave

## Constraints:
    Preconditions: The Note object must be properly initialized with valid note data
    Postconditions: The octave value will be decremented by 1, but will never be less than 0

## Side Effects:
    None

### `mingus.containers.note.Note.remove_redundant_accidentals` · *method*

*No documentation generated.*

### `mingus.containers.note.Note.transpose` · *method*

## Summary:
Transposes the note by the specified interval, adjusting the octave when necessary to maintain proper musical pitch relationships.

## Description:
This method modifies the note's musical pitch by moving it up or down by a specified interval. When transposing up, if the resulting note is musically lower than the original (due to octave wrapping), the octave is incremented. When transposing down, if the resulting note is musically higher than the original, the octave is decremented. This ensures that the transposed note maintains correct musical relationships.

## Args:
    interval (str): The interval by which to transpose (e.g., 'm3', 'P5', 'M2')
    up (bool): Direction of transposition. True for upward transposition, False for downward. Defaults to True.

## Returns:
    None: This method modifies the instance in-place and does not return a value.

## Raises:
    None explicitly raised, but may raise exceptions from underlying functions if invalid interval or note data is encountered.

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: The note must be a valid musical note, and the interval must be a valid shorthand interval representation.
    Postconditions: After calling, the note's name and octave will reflect the transposed pitch, with octave adjustments made when necessary to preserve musical correctness.

## Side Effects:
    None: This method only modifies the instance's attributes and doesn't perform I/O or external service calls.

### `mingus.containers.note.Note.from_int` · *method*

## Summary:
Initializes a Note object from an integer MIDI note number where 0-11 correspond to C-B notes in octave 0, and higher values represent notes in higher octaves.

## Description:
Converts an integer MIDI note number into a musical note by mapping the remainder to a note name and quotient to an octave number. This method serves as a factory method for creating Note objects from integer representations, enabling seamless conversion between integer MIDI note numbers and note name/octave pairs. It is called internally by the Note constructor when an integer is passed as the first argument.

## Args:
    integer (int): Integer MIDI note number where 0 represents C in octave 0, 12 represents C in octave 1, etc.

## Returns:
    Note: Returns self to enable method chaining.

## Raises:
    None explicitly raised by this method, though underlying note conversion functions may raise exceptions for invalid inputs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: The integer parameter should be a valid integer that can be converted to a note name (the modulo 12 operation will always produce a valid index 0-11)
    Postconditions: The Note object's name and octave attributes are set according to the integer representation, where integer = octave * 12 + note_index

## Side Effects:
    None

### `mingus.containers.note.Note.measure` · *method*

## Summary:
Computes the interval distance between this note and another note as the difference of their integer pitch representations.

## Description:
This method calculates the interval between two musical notes by converting both notes to their integer pitch representations and returning the difference (other - self). The result represents the number of semitones between the notes, with positive values indicating the other note is higher and negative values indicating it's lower.

## Args:
    other: A musical note object or value that can be converted to an integer representing a note pitch

## Returns:
    int: The interval distance between the notes in semitone units (other - self)

## Raises:
    TypeError: If either note cannot be converted to an integer representation

## State Changes:
    Attributes READ: None - this method only accesses the integer representations of notes
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: Both self and other must support conversion to integers representing musical note pitches
    Postconditions: The returned integer represents the interval in semitone units between the notes

## Side Effects:
    None - this method performs no I/O operations or external service calls

### `mingus.containers.note.Note.to_hertz` · *method*

## Summary:
Converts a musical note to its frequency in Hertz using the standard equal temperament tuning formula.

## Description:
Transforms the note's MIDI note number representation into a frequency value in Hertz. This method implements the standard formula for calculating musical note frequencies where A4 (MIDI note 69) is defined as 440 Hz by default.

## Args:
    standard_pitch (float): Reference pitch in Hertz for A4 (middle A). Defaults to 440.0.

## Returns:
    float: Frequency of the note in Hertz.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The note must be properly initialized with valid note name and octave values.
    Postconditions: Returns a positive floating-point frequency value.

## Side Effects:
    None.

### `mingus.containers.note.Note.from_hertz` · *method*

## Summary:
Converts a frequency in Hertz to a musical note representation by setting the note name and octave attributes.

## Description:
This method transforms a frequency value in Hertz into a musical note by applying a logarithmic conversion formula. It's designed to work with standard musical pitch reference (default 440 Hz for A4) and maps the frequency to the appropriate note name and octave. The method is typically used when working with audio frequencies that need to be represented as musical notes.

## Args:
    hertz (float): The frequency in Hertz to convert to a musical note. Must be positive.
    standard_pitch (float): The standard pitch reference frequency in Hertz. Defaults to 440.0. Must be positive.

## Returns:
    Note: Returns self to enable method chaining.

## Raises:
    None explicitly raised by this method, but may propagate exceptions from underlying functions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: 
    - hertz must be a positive number
    - standard_pitch must be a positive number
    
    Postconditions:
    - self.name will be set to a valid note name (C, C#, D, etc.)
    - self.octave will be set to an integer representing the octave number

## Side Effects:
    None

### `mingus.containers.note.Note.to_shorthand` · *method*

## Summary:
Converts a musical note to its shorthand notation format with proper case and octave indicators.

## Description:
Transforms a Note object into a string representation using musical shorthand notation. This method follows standard conventions where:
- Notes in octaves below 3 use uppercase note names (e.g., "C", "D#")
- Notes in octave 3 and above use lowercase note names (e.g., "c", "d#")
- Octave adjustments are indicated by commas (for lower octaves) and apostrophes (for higher octaves)
- The method handles all octave ranges correctly, including negative octaves and high octaves

This logic is encapsulated in its own method rather than being inlined because shorthand notation is a standardized musical representation that needs consistent formatting across the application.

## Args:
    None

## Returns:
    str: A shorthand notation string representing the note, such as:
         - "C" for C note in octave 2 (or below)
         - "c" for C note in octave 3 or above  
         - "C," for C note in octave 2 (one octave below standard)
         - "c'" for C note in octave 4 (one octave above standard)
         - "D#'" for D# note in octave 4

## Raises:
    None

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must have valid name and octave attributes
    Postconditions: Returns a properly formatted shorthand notation string with correct case and octave indicators

## Side Effects:
    None

### `mingus.containers.note.Note.from_shorthand` · *method*

## Summary:
Parses a shorthand musical note representation and configures the note object with the corresponding note name and octave.

## Description:
Converts a shorthand string notation (like "c'", "B,", "f#", etc.) into a proper note object by parsing the note name and octave information. This method handles standard musical notation conventions where lowercase letters represent notes in octave 3, uppercase letters in octave 2, and comma/apostrophe characters modify the octave.

## Args:
    shorthand (str): A string representing a musical note in shorthand format containing note names (a-g, A-G), accidentals (#, b), and octave modifiers (, ')

## Returns:
    Note: The current note instance with updated name and octave properties

## Raises:
    NoteFormatError: When the note name is invalid after parsing

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: name, octave

## Constraints:
    Preconditions: The shorthand string must follow valid musical notation conventions
    Postconditions: The note object's name and octave attributes are set according to the shorthand representation

## Side Effects:
    None

### `mingus.containers.note.Note.__int__` · *method*

## Summary:
Converts a musical note to its integer representation for comparison and arithmetic operations.

## Description:
This method transforms a Note object into an integer value that represents the note's position in the chromatic scale. The integer value is calculated as (octave × 12) + (base note value) + (accidental adjustments), making it suitable for comparing notes and calculating intervals between them. This method is automatically invoked when using built-in functions like `int()` on Note objects or when comparing notes with relational operators.

## Args:
    self: The Note instance to convert to an integer.

## Returns:
    int: The integer representation of the note, where:
        - Notes in octave 0 start at 0 (C0 = 0, C#0 = 1, D0 = 2, etc.)
        - Each octave increases by 12 semitones
        - Sharps add 1 to the base note value
        - Flats subtract 1 from the base note value

## Raises:
    NoteFormatError: If the note name is invalid (when called indirectly via notes.note_to_int).

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.name must be a valid note name string (e.g., "C", "C#", "Db", "Bb")
    - self.octave must be a non-negative integer
    Postconditions:
    - Returns an integer representing the note's position in the chromatic scale
    - The returned value is unique for each note across all octaves

## Side Effects:
    None

### `mingus.containers.note.Note.__lt__` · *method*

## Summary:
Implements the less-than comparison operator for Note objects by converting them to integer representations.

## Description:
This method defines the behavior of the `<` operator when comparing Note objects. It converts both the current Note instance and the comparison object to their integer representations using the `__int__` method, then performs numerical comparison. This allows Notes to be sorted and compared in a meaningful way based on their musical pitch.

## Args:
    other: Another Note object or None to compare against

## Returns:
    bool: True if self's integer representation is less than other's integer representation, False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The other object must be either a Note instance or None
    Postconditions: Returns a boolean value representing the comparison result

## Side Effects:
    None

### `mingus.containers.note.Note.__eq__` · *method*

## Summary:
Compares two Note objects for equality based on their integer representations.

## Description:
Implements the equality comparison operator (`==`) for Note objects by converting both operands to integer MIDI note numbers and comparing those values. This method ensures that two Note objects representing the same musical pitch are considered equal regardless of their internal representation.

## Args:
    other (Note or None): Another Note object to compare with this instance, or None

## Returns:
    bool: True if both Note objects represent the same pitch (have identical integer values), False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self must be a valid Note object
    - other can be a Note object or None
    Postconditions:
    - Returns a boolean value indicating equality of the two Note objects' pitches

## Side Effects:
    None

### `mingus.containers.note.Note.__ne__` · *method*

## Summary:
Returns True if this note is not equal to another note, based on integer value comparison.

## Description:
Implements the "not equal" comparison operation for Note objects. This method delegates to the equality comparison (`__eq__`) and returns the logical negation of that result. It enables the use of the `!=` operator between Note instances.

## Args:
    other (Note or int): Another note object or integer to compare against

## Returns:
    bool: True if the notes are not equal, False otherwise

## Raises:
    None explicitly raised, but may propagate exceptions from `__eq__` or `int()` conversion

## State Changes:
    Attributes READ: None - this method only reads the object's integer representation
    Attributes WRITTEN: None - this method does not modify any attributes

## Constraints:
    Preconditions: The other object must be compatible with the `__eq__` method (either a Note instance or integer)
    Postconditions: Returns a boolean value indicating inequality

## Side Effects:
    None - this method is pure and has no side effects

### `mingus.containers.note.Note.__gt__` · *method*

## Summary:
Implements the greater-than comparison operator for Note objects by negating the less-than-or-equal-to condition.

## Description:
This method enables the use of the '>' operator between Note instances. It determines whether the current note is greater than another note by checking that it is not less than or equal to the other note. This implementation leverages the existing `__lt__` and `__eq__` methods to maintain consistency in comparison logic.

## Args:
    other (Note or None): Another Note instance to compare against, or None

## Returns:
    bool: True if the current note is greater than the other note, False otherwise

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Both notes must be valid Note objects or None
    Postconditions: Returns a boolean value indicating the comparison result

## Side Effects:
    None: This method performs no I/O, external service calls, or mutations to objects outside self

### `mingus.containers.note.Note.__le__` · *method*

## Summary:
Implements the less-than-or-equal-to comparison operator for musical notes.

## Description:
Compares two Note objects to determine if the current note is less than or equal to another note in musical pitch order. This method is part of Python's rich comparison protocol and enables note objects to be used in ordered collections and comparisons. The implementation delegates to the `__lt__` and `__eq__` methods to determine the result.

## Args:
    other (Note, int, or None): Another note object, integer, or None to compare against. When comparing with None, the method returns False (consistent with `__lt__` and `__eq__` behavior).

## Returns:
    bool: True if the current note is less than or equal to the other note, False otherwise.

## Raises:
    None explicitly raised, but may propagate exceptions from underlying comparison operations when comparing with incompatible types.

## State Changes:
    Attributes READ: None - this method only reads the note's internal representation via conversion to integer
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: The other object must be compatible with note comparison operations (Note instances, integers, or None)
    Postconditions: Returns a boolean value indicating the comparison result

## Side Effects:
    None - this method is purely functional and has no side effects

### `mingus.containers.note.Note.__ge__` · *method*

## Summary:
Implements the greater than or equal comparison operator for musical notes.

## Description:
This method determines whether the current note is greater than or equal to another note by negating the result of the less than comparison. It enables comparison operations between Note objects using the >= operator.

## Args:
    other (Note or None): Another Note object to compare against, or None

## Returns:
    bool: True if the current note is greater than or equal to the other note, False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The other object must be a Note instance or None
    Postconditions: Returns a boolean value representing the comparison result

## Side Effects:
    None

### `mingus.containers.note.Note.__repr__` · *method*

## Summary:
Returns a string representation of the note in the format "'note-octave'" (e.g., 'C-4') for debugging and display purposes.

## Description:
This is the Python magic method `__repr__` that defines the official string representation of a Note object. It is automatically invoked by Python's built-in `repr()` function and when the object is displayed in interactive environments such as the Python interpreter. The method formats the note name and octave into a standardized string representation that clearly identifies the musical note.

## Args:
    None

## Returns:
    str: A formatted string in the pattern "'name-octave'" where name is the note letter (e.g., 'C', 'D#') and octave is an integer representing the MIDI octave number.

## Raises:
    None

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must have valid `name` and `octave` attributes that are properly initialized. The name attribute should contain a valid note name string and the octave should be an integer.
    Postconditions: The returned string follows the exact format "'name-octave'" where name is the note name and octave is the octave number.

## Side Effects:
    None

