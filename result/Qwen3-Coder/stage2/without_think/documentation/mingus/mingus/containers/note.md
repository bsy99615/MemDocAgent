# `note.py`

## `mingus.containers.note.Note` · *class*

## Summary:
Represents a musical note with name, octave, MIDI channel, and velocity properties, supporting various manipulations and conversions.

## Description:
The Note class encapsulates musical note information including pitch (name and octave), MIDI channel, and velocity. It provides methods for modifying note properties, transposing notes, converting between different note representations, and performing musical operations like augmentation and diminishment. This abstraction allows for consistent handling of musical notes throughout the mingus music processing framework.

## State:
- name (str): Musical note name (e.g., "C", "D#", "Eb"). Valid values are standard musical note names that pass the notes.is_valid_note() check.
- octave (int): Octave number (typically 0-9). Must be non-negative.
- channel (int): MIDI channel number (0-15). Default is likely 0 based on typical MIDI conventions.
- velocity (int): MIDI velocity value (0-127). Default is likely 64 based on typical MIDI conventions.

## Lifecycle:
- Creation: Instantiate with note name, octave, and optional dynamics (channel, velocity). Supports multiple initialization formats including string ("C4"), Note objects, or integers.
- Usage: Call methods like transpose(), change_octave(), augment(), diminish() to modify note properties. Comparison operators enable ordering of notes.
- Destruction: No special cleanup required; uses standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[Note.__init__] --> B{Input Type}
    B -->|String| C[set_note]
    B -->|Note Object| D[set_note]
    B -->|Integer| E[from_int]
    C --> F[set_velocity|set_channel]
    F --> G[notes.is_valid_note]
    G --> H[Note.__int__]
    H --> I[transpose]
    I --> J[change_octave]
    J --> K[augment|diminish]
    K --> L[to_hertz|from_hertz]
    L --> M[to_shorthand|from_shorthand]
    M --> N[__int__|__repr__]
```

## Raises:
- NoteFormatError: When invalid note representations are provided to __init__ or set_note methods.
- ValueError: When attempting to set invalid channel (0-15) or velocity (0-127) values.

## Example:
```python
# Create a note
note = Note("C", 4)  # Middle C
print(note)  # 'C-4'

# Modify the note
note.octave_up()  # Raise octave
note.augment()    # Add sharp

# Convert between representations
midi_value = int(note)  # Convert to MIDI note number
frequency = note.to_hertz()  # Convert to frequency in Hz

# Transpose the note
note.transpose("P5")  # Perfect fifth up
```

### `mingus.containers.note.Note.__init__` · *method*

## Summary:
Initializes a Note object with various input formats, supporting string note names, note objects, or integer representations.

## Description:
Constructs a Note instance by processing the input name parameter in multiple formats and configuring associated dynamics properties. This method serves as the primary constructor that normalizes different input representations into a consistent Note object state. The initialization process handles string note names (like "C", "D#"), existing Note objects, and integer representations, while also managing dynamic properties like velocity and channel through the dynamics dictionary.

## Args:
    name (str, Note, int): The note representation, which can be a string name like "C", a Note object with name/octave/dynamics attributes, or an integer representing MIDI note number. Defaults to "C".
    octave (int): The octave number for the note when name is a string. Defaults to 4.
    dynamics (dict, optional): Dictionary containing dynamic properties like "velocity" and "channel". Defaults to None.
    velocity (int, optional): MIDI velocity value (0-127) for the note. Defaults to None.
    channel (int, optional): MIDI channel number (0-15) for the note. Defaults to None.

## Returns:
    None: This method initializes the object in-place and does not return a value.

## Raises:
    NoteFormatError: When the name parameter is not a recognized type (string, Note object, or integer) and cannot be processed.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave, and potentially self.velocity and self.channel if dynamics are configured

## Constraints:
    Preconditions:
    - If name is a string, it must be a valid note name
    - If velocity is provided, it must be between 0 and 127
    - If channel is provided, it must be between 0 and 15
    - octave must be a valid integer
    
    Postconditions:
    - The Note object is properly initialized with name and octave
    - Dynamics properties (velocity, channel) are configured in the dynamics dictionary
    - If name is an integer, self.name and self.octave are set via from_int conversion

## Side Effects:
    - May modify self.velocity and self.channel through dynamics dictionary updates
    - Calls set_note() or from_int() methods which may update other internal state
    - May raise NoteFormatError if name parameter is invalid

### `mingus.containers.note.Note.dynamics` · *method*

## Summary:
Returns a dictionary containing the MIDI channel and velocity dynamics of the note.

## Description:
This property provides access to the MIDI dynamics information associated with the note, specifically the channel and velocity values. It serves as a convenient way to retrieve both dynamics parameters together as a single dictionary structure.

## Args:
    None

## Returns:
    dict[str, int]: A dictionary with two keys:
        - "channel" (int): The MIDI channel number (0-15)
        - "velocity" (int): The MIDI velocity value (0-127)

## Raises:
    None

## State Changes:
    Attributes READ: self.channel, self.velocity
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must be properly initialized with valid channel and velocity values
    Postconditions: The returned dictionary contains the current channel and velocity values from the note object

## Side Effects:
    None

### `mingus.containers.note.Note.set_channel` · *method*

## Summary:
Sets the MIDI channel for this note, validating that the channel is within the valid range of 0-15.

## Description:
This method assigns a MIDI channel number to the note object. MIDI channels are numbered from 0 to 15, inclusive. This validation ensures that the channel value conforms to standard MIDI specifications. The method is typically called internally by other methods like `set_note()` when a channel parameter is provided, or directly by users who want to modify a note's channel assignment.

## Args:
    channel (int): The MIDI channel number to assign to this note. Must be an integer between 0 and 15 (inclusive).

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: Raised when the channel parameter is outside the valid range of 0-15.

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
Sets the MIDI velocity value for this note, validating that it falls within the standard MIDI range of 0-127.

## Description:
This method assigns a MIDI velocity value to the note object, ensuring it complies with standard MIDI specifications where velocity values range from 0 (silent) to 127 (maximum velocity). The method is typically called internally by `set_note()` when velocity information is provided, but can also be invoked directly by users who wish to modify a note's velocity independently.

## Args:
    velocity (int): The MIDI velocity value to assign to this note. Must be an integer between 0 and 127 (inclusive). Values outside this range will raise a ValueError.

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: Raised when the velocity parameter is less than 0 or greater than or equal to 128, as MIDI velocity values must be in the range [0, 127].

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.velocity

## Constraints:
    Preconditions: The velocity parameter must be an integer within the range [0, 127].
    Postconditions: After execution, self.velocity will contain the validated velocity value.

## Side Effects:
    None: This method only modifies the internal state of the Note object and has no external side effects.

### `mingus.containers.note.Note.set_note` · *method*

## Summary:
Sets the note name and octave for this Note object, with optional velocity and channel configuration from parameters or dynamics dictionary.

## Description:
Configures the musical note properties of this Note instance by setting the note name and octave, while also handling dynamic properties like velocity and channel either from direct parameters or from a dynamics dictionary. This method supports two note naming conventions: simple note names (like "C", "D#") and compound note-octave combinations (like "C-4", "A#-5").

## Args:
    name (str): The note name, either a simple note like "C" or a note-octave combination like "C-4". Defaults to "C".
    octave (int): The octave number for the note. Defaults to 4.
    dynamics (dict, optional): Dictionary containing dynamic properties like "velocity" and "channel". Defaults to None.
    velocity (int, optional): MIDI velocity value (0-127) for the note. Defaults to None.
    channel (int, optional): MIDI channel number (0-15) for the note. Defaults to None.

## Returns:
    Note: Returns self to allow for method chaining.

## Raises:
    NoteFormatError: When the note name is invalid or when the note name format contains more than one dash.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: 
    - The note name must be valid according to notes.is_valid_note() function
    - Velocity must be between 0 and 127 if provided
    - Channel must be between 0 and 15 if provided
    - Octave must be a valid integer
    
    Postconditions:
    - self.name is set to the validated note name
    - self.octave is set to the provided octave value
    - If velocity is provided, self.velocity is updated via set_velocity()
    - If channel is provided, self.channel is updated via set_channel()

## Side Effects:
    - Calls self.set_velocity() if velocity is provided or found in dynamics dict
    - Calls self.set_channel() if channel is provided or found in dynamics dict
    - May raise ValueError if velocity or channel values are out of valid ranges

### `mingus.containers.note.Note.empty` · *method*

## Summary:
Resets the note to its default empty state by clearing the note name, setting octave to 0, and restoring default channel and velocity values.

## Description:
The empty() method clears the note's musical content while preserving the object structure. It sets the note name to an empty string, octave to 0, and restores default MIDI channel and velocity values. This method is typically used to reset a note object to a clean state before assigning new values.

This method is implemented as a separate function because it provides a standardized way to reset a note's musical properties while maintaining the object's structural integrity. It encapsulates the logic for resetting multiple attributes consistently, making the code more readable and maintainable compared to inline assignments throughout the codebase.

## Returns:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.name: Set to empty string ""
        - self.octave: Set to 0
        - self.channel: Set to _DEFAULT_CHANNEL (MIDI channel, typically 0)
        - self.velocity: Set to _DEFAULT_VELOCITY (MIDI velocity, typically 127)

## Constraints:
    Preconditions: The object must be an instance of Note class
    Postconditions: The note object will have empty name, octave 0, and default channel/velocity values

## Side Effects:
    None

### `mingus.containers.note.Note.augment` · *method*

## Summary:
Applies an accidental augmentation to the note by adding a sharp (#) or removing a flat (b).

## Description:
This method modifies the note's name by applying an augmentation operation. If the note name ends with a flat symbol ('b'), it removes the flat. Otherwise, it appends a sharp symbol ('#') to the note name. This is commonly used in music theory to convert flat notes to sharp notes or to add sharps to natural notes.

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
    Preconditions: The note name must be a valid musical note string
    Postconditions: The note name will have a sharp added if it didn't previously end with 'b', or the flat will be removed if it did end with 'b'

## Side Effects:
    None

### `mingus.containers.note.Note.diminish` · *method*

## Summary:
Reduces the accidental of a musical note by flattening it or removing a sharp.

## Description:
Applies a diminishment operation to the note by modifying its name attribute. If the note name does not end with a sharp symbol ('#'), it appends a flat symbol ('b') to the note name. If the note name ends with a sharp symbol ('#'), it removes the sharp. This operation is commonly used in music theory to convert sharp notes to flat notes or to flatten natural notes.

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
    Preconditions: The note name must be a valid musical note string
    Postconditions: The note name will have a flat added if it didn't previously end with '#', or the sharp will be removed if it did end with '#'

## Side Effects:
    None

### `mingus.containers.note.Note.change_octave` · *method*

## Summary:
Changes the octave of a musical note by a specified difference, ensuring the octave never drops below zero.

## Description:
Modifies the octave attribute of a musical note by adding the provided difference value. This method prevents negative octaves by clamping the value to zero if the calculation would result in a negative number. The method is typically called internally by `octave_up()` and `octave_down()` methods to adjust note octaves.

## Args:
    diff (int): The difference to add to the current octave value. Positive values raise the octave, negative values lower it.

## Returns:
    None: This method modifies the object in-place and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.octave
    Attributes WRITTEN: self.octave

## Constraints:
    Preconditions: The note object must be properly initialized with an octave attribute.
    Postconditions: The octave attribute will be updated to (original_octave + diff), but will never be less than 0.

## Side Effects:
    None: This method only modifies the internal state of the Note object.

### `mingus.containers.note.Note.octave_up` · *method*

## Summary:
Increases the octave of a musical note by one position.

## Description:
This method raises the octave of the current note by one position by calling the internal `change_octave` method with a difference of 1. It's a convenience method that provides a clear, semantic way to increase a note's octave without needing to remember the specific parameter value.

## Args:
    None: This method takes no arguments beyond the implicit `self` parameter.

## Returns:
    None: This method modifies the object in-place and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.octave
    Attributes WRITTEN: self.octave

## Constraints:
    Preconditions: The note object must be properly initialized with an octave attribute.
    Postconditions: The octave attribute will be incremented by 1, but will never be less than 0 due to the behavior of `change_octave`.

## Side Effects:
    None: This method only modifies the internal state of the Note object.

### `mingus.containers.note.Note.octave_down` · *method*

## Summary:
Lowers the octave of a musical note by one step.

## Description:
Decrements the octave attribute of the musical note by 1. This method is a convenience wrapper around the `change_octave` method, specifically designed to lower the note's octave. It ensures that the octave never goes below zero, maintaining valid musical note representations.

## Args:
    None: This method takes no arguments beyond the implicit `self` parameter.

## Returns:
    None: This method modifies the object in-place and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.octave
    Attributes WRITTEN: self.octave

## Constraints:
    Preconditions: The note object must be properly initialized with an octave attribute.
    Postconditions: The octave attribute will be decremented by 1, but will never be less than 0.

## Side Effects:
    None: This method only modifies the internal state of the Note object.

### `mingus.containers.note.Note.remove_redundant_accidentals` · *method*

## Summary:
Removes redundant accidentals from the note name, normalizing it to its canonical form.

## Description:
This method cleans up a note name by removing any redundant accidentals (sharps or flats) and converting it to its most basic representation. For example, a note named "C##" would be normalized to "D", and "Dbb" would become "C". This ensures consistent note naming throughout the application.

The method is called during various note processing operations to maintain clean, standardized note representations. It operates on the note's name attribute and modifies it in-place to produce a canonical form.

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
    Preconditions: The note name must be a valid string representation of a musical note
    Postconditions: The note name will be normalized to its canonical form with no redundant accidentals

## Side Effects:
    None

### `mingus.containers.note.Note.transpose` · *method*

## Summary:
Transposes the note by the specified interval, potentially adjusting the octave when crossing octave boundaries.

## Description:
This method modifies the note in-place by transposing it according to the given interval. When transposing upward, if the resulting note is lower than the original (due to octave wrapping), the octave is incremented. When transposing downward, if the resulting note is higher than the original (due to octave wrapping), the octave is decremented. This ensures proper handling of octave boundaries when transposing notes.

## Args:
    interval (str): The interval to transpose by (e.g., "M2", "m3", "P5").
    up (bool): Direction of transposition. True for upward transposition, False for downward. Defaults to True.

## Returns:
    None: This method modifies the instance in-place and does not return a value.

## Raises:
    None explicitly raised, but may raise exceptions from underlying functions like `intervals.from_shorthand` or `notes.is_valid_note`.

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: The note must be a valid note object with a valid note name and octave.
    Postconditions: The note's name and octave are updated to reflect the transposed value, with appropriate octave adjustments.

## Side Effects:
    None: This method only modifies the instance's attributes and doesn't perform I/O or external service calls.

### `mingus.containers.note.Note.from_int` · *method*

*No documentation generated.*

### `mingus.containers.note.Note.measure` · *method*

## Summary:
Calculates the interval in semitones between this note and another note.

## Description:
Computes the difference between the MIDI note numbers of two notes, returning the interval in semitones. This method enables calculation of the pitch distance between musical notes, where positive values indicate the other note is higher in pitch and negative values indicate it is lower.

The method is called during interval calculations and musical analysis operations where the distance between notes needs to be quantified in semitone units.

## Args:
    other (Note or int): Another note object or integer representation of a note to measure against

## Returns:
    int: The interval in semitones between self and other. Positive values indicate other is higher in pitch, negative values indicate other is lower in pitch.

## Raises:
    NoteFormatError: If other is a string that doesn't represent a valid note, or if other is an invalid type that cannot be converted to a note.

## State Changes:
    Attributes READ: None - this method only reads the note's integer representation via the __int__ method
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: The other object must be a Note instance, an integer, or convertible to a note representation
    Postconditions: Returns an integer representing the semitone interval between the notes

## Side Effects:
    None - This method performs no I/O operations or external service calls

### `mingus.containers.note.Note.to_hertz` · *method*

## Summary:
Converts a musical note to its frequency in Hertz using the equal temperament tuning system.

## Description:
This method transforms a musical note into its corresponding frequency in Hertz by calculating the frequency based on the note's position relative to a reference pitch. The calculation uses the standard MIDI note numbering system where note 57 corresponds to A4 (440 Hz), and applies the equal temperament formula f = 2^((n-57)/12) × standard_pitch to determine the frequency of any other note.

## Args:
    standard_pitch (float): Reference pitch in Hertz. Defaults to 440.0, representing the standard A4 pitch.

## Returns:
    float: The frequency of the note in Hertz.

## Raises:
    None explicitly documented in the method.

## State Changes:
    Method Calls: self.__int__() - calls the integer conversion method of the Note object to obtain the MIDI note number

## Constraints:
    Preconditions: The Note object must implement a `__int__()` method that returns a valid MIDI note number.
    Postconditions: The returned value is always a positive float representing the frequency in Hertz.

## Side Effects:
    None

### `mingus.containers.note.Note.from_hertz` · *method*

## Summary:
Converts a frequency in hertz to a musical note by setting the note's name and octave attributes.

## Description:
This method transforms a frequency value in hertz into a musical note representation. It calculates the corresponding MIDI note number using logarithmic mathematics and maps it to a note name and octave. The method is designed to be part of the Note class's conversion utilities, allowing users to create musical notes from frequency specifications.

## Args:
    hertz (float): The frequency in hertz to convert to a musical note
    standard_pitch (float): Reference pitch for calculation, defaults to 440.0 Hz (A4)

## Returns:
    Note: Returns self to enable method chaining

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: 
    - hertz must be a positive number
    - standard_pitch must be a positive number
    
    Postconditions:
    - self.name will be set to a valid musical note name (C, C#, D, etc.)
    - self.octave will be set to an integer representing the octave number

## Side Effects:
    None

### `mingus.containers.note.Note.to_shorthand` · *method*

## Summary:
Converts a musical note to its shorthand notation string representation with octave indicators.

## Description:
Transforms a Note object into a compact string representation using standard musical shorthand notation. When the note's octave is less than 3, the note name is used as-is. For octaves 3 and above, the note name is converted to lowercase. Octave adjustments are indicated using commas (for lower octaves) and apostrophes (for higher octaves) relative to octave 3.

## Args:
    None

## Returns:
    str: A shorthand notation string representing the note, such as "C", "c", "C,", "C'", "c''", etc.

## Raises:
    None

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must have valid name and octave attributes
    Postconditions: Returns a properly formatted shorthand string representation

## Side Effects:
    None

### `mingus.containers.note.Note.from_shorthand` · *method*

## Summary:
Parses a shorthand notation string and configures the note object with the corresponding musical note and octave.

## Description:
Converts a shorthand musical notation string into a proper note representation. This method processes each character in the shorthand string to determine the note name and octave, then configures the current note object accordingly. The shorthand notation supports lowercase and uppercase note names, sharps, flats, and octave modifiers.

## Args:
    shorthand (str): A string representing a musical note in shorthand format. Valid characters include:
        - Lowercase a-g: Sets note name to uppercase with octave 3
        - Uppercase A-G: Sets note name with octave 2
        - # or b: Appends accidental to current note name
        - ,: Decreases octave by 1
        - ': Increases octave by 1

## Returns:
    Note: Returns self to allow for method chaining after setting the note properties.

## Raises:
    NoteFormatError: Raised by the underlying set_note method when the parsed note name is invalid.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: name, octave, channel, velocity (through set_note call)

## Constraints:
    Preconditions: The shorthand string must contain valid musical notation characters
    Postconditions: The note object's name and octave attributes are updated according to the shorthand representation

## Side Effects:
    Mutates the note object's internal state through the set_note method call

### `mingus.containers.note.Note.__int__` · *method*

## Summary:
Converts a musical note to its integer MIDI note number representation.

## Description:
This method transforms a musical note (consisting of a name and octave) into an integer value representing the MIDI note number. This enables mathematical comparison and arithmetic operations between notes. The method is automatically called when converting a Note object to an integer using `int()`.

The conversion follows standard MIDI note numbering where:
- C4 = 60 (middle C)
- C#4 = 61
- Db4 = 61
- B4 = 67
- C5 = 72

## Args:
    None

## Returns:
    int: The MIDI note number representing the note's position in the chromatic scale.

## Raises:
    NoteFormatError: If the note name is invalid (though this should be caught during note creation via set_note)

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must have a valid note name (containing only valid note letters A-G and accidentals # or b) and a valid octave
    Postconditions: Returns an integer representing the note's position in the chromatic scale

## Side Effects:
    None

### `mingus.containers.note.Note.__lt__` · *method*

## Summary:
Compares two Note objects to determine if the current note has a lower pitch value than another note.

## Description:
Implements the less-than comparison operator (`<`) for Note objects by converting both notes to their integer MIDI note number representations and comparing those values. This method enables sorting and ordering of musical notes based on pitch.

The method is called during comparisons such as `note1 < note2` and follows the standard Python comparison protocol. When comparing with None, it returns False to avoid unexpected behavior.

## Args:
    other (Note, int, or None): Another note object, integer representation of a note, or None to compare against.

## Returns:
    bool: True if the current note has a lower pitch value than the other note, False otherwise.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The other object must be a Note instance, an integer, or None.
    Postconditions: Returns a boolean value representing whether self is less than other.

## Side Effects:
    None

### `mingus.containers.note.Note.__eq__` · *method*

## Summary:
Compares two Note objects for equality based on their integer representations.

## Description:
Defines equality comparison between Note instances by converting both objects to integer values and comparing those values. This method ensures that two notes with identical pitch and octave are considered equal, regardless of their internal representation or additional metadata like velocity and channel.

## Args:
    other (Note or None): Another Note object to compare against, or None

## Returns:
    bool: True if both notes have the same integer representation (same pitch/octave), False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Both self and other must be Note objects or other must be None
    Postconditions: Returns boolean indicating equality of integer representations

## Side Effects:
    None

### `mingus.containers.note.Note.__ne__` · *method*

## Summary:
Implements the not-equal comparison operator for Note objects by logically negating the equality comparison.

## Description:
Defines the behavior of the `!=` operator when comparing two Note instances. This method returns True if the two notes are not equal (based on their integer representations), and False if they are equal. It delegates to the `__eq__` method to determine equality and then negates the result.

This method is part of Python's standard comparison protocol and enables intuitive comparison expressions like `note1 != note2`.

## Args:
    other (Note or None): Another Note object to compare against, or None

## Returns:
    bool: True if the current note differs from the other note in pitch/octave, False if they are equivalent

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Both self and other must be Note objects or other must be None
    Postconditions: Returns boolean indicating inequality of the notes

## Side Effects:
    None

### `mingus.containers.note.Note.__gt__` · *method*

## Summary:
Implements the greater-than comparison operator for Note objects by logically negating the less-than-or-equal relationship.

## Description:
This method defines the behavior of the `>` operator when comparing two Note objects. It determines whether the current note has a higher pitch value than another note by returning the logical negation of `(self < other or self == other)`. This implementation leverages the existing `__lt__` and `__eq__` methods to maintain consistency in comparison logic.

## Args:
    other (Note or None): Another Note object to compare against, or None

## Returns:
    bool: True if the current note has a higher pitch value than the other note, False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Both self and other must be Note objects or other must be None
    Postconditions: Returns boolean indicating whether self is greater than other

## Side Effects:
    None

### `mingus.containers.note.Note.__le__` · *method*

## Summary:
Implements the less-than-or-equal-to comparison operator for musical notes.

## Description:
This method determines whether the current note is less than or equal to another note in terms of pitch. It leverages the existing `__lt__` and `__eq__` comparison methods to provide a complete ordering relationship between notes.

## Args:
    other (Note or None): Another note object to compare against, or None.

## Returns:
    bool: True if the current note is less than or equal to the other note, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The other object must be a Note instance or None.
    Postconditions: Returns a boolean value representing the comparison result.

## Side Effects:
    None.

### `mingus.containers.note.Note.__ge__` · *method*

## Summary:
Implements the greater than or equal to comparison operator for Note objects.

## Description:
This method enables the use of the >= operator between Note instances. It returns True if the current note is greater than or equal to the other note, and False otherwise. The implementation delegates to the less than comparison (`__lt__`) method, returning the logical negation of that result.

## Args:
    other (Note or int or None): Another note object, integer representation of a note, or None to compare against.

## Returns:
    bool: True if self is greater than or equal to other, False otherwise.

## Raises:
    NoteFormatError: If other is a string that doesn't represent a valid note, or if other is an invalid type that cannot be converted to a note.

## State Changes:
    Attributes READ: None - this method only reads the note's integer representation via the __int__ method
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: The other argument must be either a Note object, an integer, or None.
    Postconditions: Returns a boolean value representing the comparison result.

## Side Effects:
    None - This method performs no I/O operations or external service calls.

### `mingus.containers.note.Note.__repr__` · *method*

## Summary:
Returns a string representation of the note in the format "'name-octave'".

## Description:
This method provides a human-readable string representation of a Note object, displaying its musical name and octave. It is automatically called when the object needs to be displayed in a string context, such as in interactive sessions or when printing the object.

## Args:
    None

## Returns:
    str: A string in the format "'name-octave'" where name is the note name (e.g., "C", "D#") and octave is the octave number as an integer.

## Raises:
    None

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must have valid name and octave attributes that are accessible.
    Postconditions: The returned string format is always "'name-octave'" where name is the note name and octave is the integer octave value.

## Side Effects:
    None

