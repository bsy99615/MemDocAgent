# `note.py`

## `mingus.containers.note.Note` · *class*

## Summary:
Represents a musical note with name, octave, MIDI channel, and velocity attributes, supporting multiple input formats and musical operations.

## Description:
The Note class provides a comprehensive representation of musical notes, enabling creation from various input formats including note names, MIDI note numbers, and other Note objects. It maintains core musical attributes (name, octave) alongside MIDI-specific attributes (channel, velocity) and offers extensive functionality for musical manipulation such as transposition, octave adjustment, and pitch conversion.

This class is designed for use within the mingus music library ecosystem, supporting standard musical notation conventions and MIDI specifications. It handles note validation and provides methods for common musical operations while maintaining proper state management.

## State:
- name (str): The note name (e.g., "C", "D#", "Eb"). Must be a valid note according to mingus.core.notes.is_valid_note(). 
- octave (int): The octave number (typically 0-9). Negative values are clamped to 0 during octave modifications.
- channel (int): MIDI channel number (0-15). Default value is defined as _DEFAULT_CHANNEL elsewhere in the module.
- velocity (int): MIDI velocity value (0-127). Default value is defined as _DEFAULT_VELOCITY elsewhere in the module.

## Lifecycle:
- Creation: Notes can be instantiated using string note names (e.g., "C4"), integers (MIDI note numbers), or other Note objects. Constructor accepts optional parameters for dynamics, velocity, and channel.
- Usage: Common operations include transposition, octave modification, pitch conversion, and note comparison. The class implements comparison operators (__lt__, __eq__, etc.) for note ordering.
- Destruction: Standard Python garbage collection handles object lifetime with no special cleanup required.

## Method Map:
```mermaid
graph TD
    A[Note.__init__] --> B{Input Type}
    B -->|String| C[set_note]
    B -->|Note Object| D[set_note]
    B -->|Integer| E[from_int]
    C --> F[notes.is_valid_note]
    C --> G[set_velocity|set_channel]
    D --> H[set_note]
    H --> I[notes.is_valid_note]
    H --> J[set_velocity|set_channel]
    E --> K[notes.int_to_note]
    L[transpose] --> M[intervals.from_shorthand]
    N[change_octave] --> O[octave_up|octave_down]
    P[augment|diminish] --> Q[notes.augment|notes.diminish]
    R[remove_redundant_accidentals] --> S[notes.remove_redundant_accidentals]
    T[__int__] --> U[notes.note_to_int]
    V[to_hertz] --> W[__int__]
    X[from_hertz] --> Y[log]
    Z[to_shorthand] --> AA[formatting]
    AB[from_shorthand] --> AC[parsing]
    AD[__lt__|__eq__|__gt__|etc.] --> AE[__int__]
    AF[dynamics] --> AG[channel|velocity]
```

## Raises:
- NoteFormatError: Raised when invalid note representations are provided to __init__ or set_note methods.
- ValueError: Raised when channel values are outside the valid MIDI range (0-15) or velocity values are outside the valid MIDI range (0-127).

## Example:
```python
# Create notes using different methods
note1 = Note("C4")           # String notation
note2 = Note(60)             # MIDI note number  
note3 = Note(note1)          # Copy from another note

# Modify notes
note1.octave_up()            # Move up one octave
note1.augment()              # Sharpen the note
note1.transpose("m3")        # Transpose up a minor third

# Access properties
channel = note1.channel      # Get MIDI channel
velocity = note1.velocity    # Get MIDI velocity
dynamics = note1.dynamics    # Get both channel and velocity

# Convert between formats
midi_number = int(note1)     # Get MIDI note number
frequency = note1.to_hertz() # Get frequency in Hz
shorthand = note1.to_shorthand()  # Get shorthand notation
```

### `mingus.containers.note.Note.__init__` · *method*

## Summary:
Initializes a musical note object with name, octave, and optional dynamics parameters, supporting multiple input formats including note names, MIDI note numbers, and other Note objects.

## Description:
Constructs a Note instance by processing various input formats for note identification. The constructor accepts a flexible range of input types and properly handles MIDI dynamics parameters (velocity and channel) through the dynamics dictionary or direct parameters. This method serves as the primary entry point for creating Note objects and ensures proper initialization of all musical attributes.

## Args:
    name (str, int, Note, optional): The note identifier, which can be a note name string (e.g., "C", "D#"), an integer MIDI note number, or another Note object. Defaults to "C".
    octave (int, optional): The octave number for the note. Only used when name is a string. Defaults to 4.
    dynamics (dict, optional): Dictionary containing MIDI dynamics properties such as "velocity" and "channel". Defaults to None.
    velocity (int, optional): MIDI velocity value (0-127) for the note. Defaults to None.
    channel (int, optional): MIDI channel number (0-15) for the note. Defaults to None.

## Returns:
    None: This method initializes the object in-place and does not return a value.

## Raises:
    NoteFormatError: Raised when the name parameter is not a recognized note format (string, integer, or Note object).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave, and potentially self.velocity and self.channel if dynamics, velocity, or channel parameters are provided

## Constraints:
    Preconditions:
    - If name is a string, it must be a valid note name according to mingus.core.notes.is_valid_note()
    - If velocity is provided, it must be between 0 and 127 inclusive
    - If channel is provided, it must be between 0 and 15 inclusive
    
    Postconditions:
    - The Note object is properly initialized with name and octave attributes
    - If velocity or channel parameters are provided, the corresponding attributes are set
    - Dynamics dictionary is properly processed and merged with velocity/channel parameters

## Side Effects:
    - May call self.set_note() when name is a string or Note object
    - May call self.from_int() when name is an integer
    - May call self.set_velocity() when velocity parameter is provided
    - May call self.set_channel() when channel parameter is provided

### `mingus.containers.note.Note.dynamics` · *method*

## Summary:
Returns a dictionary containing the MIDI channel and velocity properties of the note.

## Description:
This method provides access to the dynamic properties of a Note object, specifically its MIDI channel and velocity values. It serves as a convenient way to retrieve both dynamic attributes simultaneously in a structured format. The method is implemented as a property, making it accessible without parentheses like an attribute.

## Args:
    None

## Returns:
    dict[str, int]: A dictionary with two keys:
        - "channel" (int): The MIDI channel number (0-15)
        - "velocity" (int): The MIDI velocity value (0-127)

## Raises:
    None

## State Changes:
    - Attributes READ: self.channel, self.velocity
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: The Note object must be properly initialized with valid channel and velocity values
    - Postconditions: The returned dictionary contains valid MIDI channel (0-15) and velocity (0-127) values

## Side Effects:
    None

### `mingus.containers.note.Note.set_channel` · *method*

## Summary:
Sets the MIDI channel for a musical note, validating that the channel is within the valid range of 0-15.

## Description:
This method configures the MIDI channel associated with a musical note. MIDI channels are numbered from 0 to 15, with channel 0 being the default channel. This validation ensures that the channel value conforms to MIDI specifications before assignment.

The method is separated from inline assignment to provide centralized validation logic and maintain consistency with other similar setters in the class (like `set_velocity`). This approach allows for future extension of validation rules without modifying the assignment logic directly.

## Args:
    channel (int): MIDI channel number, must be an integer between 0 and 15 inclusive.

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: Raised when the channel parameter is less than 0 or greater than or equal to 16.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.channel

## Constraints:
    Preconditions: The channel parameter must be an integer within the range [0, 15].
    Postconditions: After execution, self.channel will contain the validated channel value.

## Side Effects:
    None: This method only modifies the object's internal state and has no external side effects.

### `mingus.containers.note.Note.set_velocity` · *method*

## Summary:
Sets the MIDI velocity value for the note, validating that it falls within the valid MIDI range of 0-127.

## Description:
This method assigns a velocity value to the note's velocity attribute after validating that it conforms to MIDI standards. Velocity values in MIDI range from 0-127, where 0 represents a note off event and 127 represents maximum velocity. This validation ensures that the note's velocity attribute maintains valid MIDI values throughout its lifetime.

The method is separated from inline assignment to provide centralized validation logic and maintain consistency with other MIDI value validations in the class (such as `set_channel`).

## Args:
    velocity (int): MIDI velocity value, must be between 0 and 127 inclusive

## Returns:
    None: This method does not return a value

## Raises:
    ValueError: If velocity is less than 0 or greater than or equal to 128

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.velocity

## Constraints:
    Preconditions: The velocity argument must be an integer within the range [0, 127]
    Postconditions: The self.velocity attribute is updated to the provided velocity value

## Side Effects:
    None: This method only modifies the object's internal state

### `mingus.containers.note.Note.set_note` · *method*

## Summary:
Sets the note name and octave while handling dynamics parameters for velocity and channel.

## Description:
Configures a Note object with a specified musical note name and octave, supporting multiple input formats. This method processes optional dynamics parameters to set velocity and channel properties, then validates and assigns the note name and octave. The method supports two input formats for note names: simple note names (like "C", "D#") or note-octave combinations separated by hyphens (like "C-4", "D#-5").

## Args:
    name (str, optional): The note name (e.g., "C", "D#", "Eb"). Defaults to "C".
    octave (int, optional): The octave number. Defaults to 4.
    dynamics (dict, optional): Dictionary containing dynamic properties like "velocity" and "channel". Defaults to None.
    velocity (int, optional): MIDI velocity value (0-127). Defaults to None.
    channel (int, optional): MIDI channel number (0-15). Defaults to None.

## Returns:
    Note: Returns self to allow method chaining.

## Raises:
    NoteFormatError: When the note name format is invalid or the note name is not recognized by the validation system.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: 
    - If velocity is provided, it must be between 0 and 127 inclusive
    - If channel is provided, it must be between 0 and 15 inclusive
    - The note name must be valid according to the notes.is_valid_note() function
    
    Postconditions:
    - self.name is set to the validated note name
    - self.octave is set to the provided octave value
    - If velocity is provided, self.velocity is updated via set_velocity()
    - If channel is provided, self.channel is updated via set_channel()

## Side Effects:
    - Calls self.set_velocity() if velocity parameter is provided or present in dynamics dict
    - Calls self.set_channel() if channel parameter is provided or present in dynamics dict
    - May raise ValueError from set_velocity() or set_channel() if parameters are out of valid ranges

### `mingus.containers.note.Note.empty` · *method*

## Summary:
Resets the note to its default empty state by clearing the note name and octave, and restoring default MIDI channel and velocity settings.

## Description:
The empty() method clears the note's musical content by setting the name to an empty string and octave to 0, while resetting the MIDI channel and velocity to their default values. This method is typically used to prepare a Note object for reuse or to clear its contents when transitioning between different musical operations.

This logic is encapsulated in its own method rather than being inlined because it provides a clean, reusable interface for resetting a note's state, making the intent clear to developers and ensuring consistent reset behavior across the application.

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
    - self.channel: Set to default MIDI channel value (_DEFAULT_CHANNEL)
    - self.velocity: Set to default MIDI velocity value (_DEFAULT_VELOCITY)

## Constraints:
    Preconditions: None
    Postconditions: The note object will have an empty name, octave 0, and default MIDI channel/velocity settings

## Side Effects:
    None

### `mingus.containers.note.Note.diminish` · *method*

## Summary:
Reduces the pitch of a musical note by flattening it one semitone.

## Description:
This method applies the diminishing operation to the note's name, effectively lowering its pitch by one semitone. It modifies the note's name attribute by either appending a flat symbol ("b") if the note is not already flattened, or removing a sharp symbol ("#") if the note is sharped.

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
    Preconditions: The note must be a valid musical note string that can be processed by the notes.diminish function
    Postconditions: The note's name attribute will be modified according to the diminishing operation rules

## Side Effects:
    None

### `mingus.containers.note.Note.change_octave` · *method*

*No documentation generated.*

### `mingus.containers.note.Note.octave_up` · *method*

## Summary:
Increases the octave of the note by one position.

## Description:
This method serves as a convenience function to raise the note by one octave. It internally calls the change_octave method with an increment value of 1. This provides a cleaner interface for octave manipulation compared to calling change_octave directly.

## Args:
    None

## Returns:
    None

## Raises:
    Exceptions may be raised by the underlying change_octave method implementation

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: The octave attribute of the note is modified by the change_octave method call

## Constraints:
    Preconditions: The Note object must be properly initialized with a mutable octave attribute
    Postconditions: The note's octave attribute will be incremented by 1

## Side Effects:
    None

### `mingus.containers.note.Note.octave_down` · *method*

## Summary:
Decrements the note's octave by one semitone, ensuring the octave never goes below zero.

## Description:
This method reduces the octave value of the note by one unit. It serves as a convenient wrapper around the change_octave method with a fixed decrement of -1. This allows for easy manipulation of note octaves in musical contexts where transposition down by one octave is needed.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.octave
    Attributes WRITTEN: self.octave

## Constraints:
    Preconditions: The note object must be properly initialized with a valid octave value
    Postconditions: The octave value will be reduced by 1, but will never be less than 0

## Side Effects:
    None

### `mingus.containers.note.Note.remove_redundant_accidentals` · *method*

## Summary:
Removes redundant accidentals from the note's name attribute by normalizing enharmonic equivalents.

## Description:
This method normalizes a note's name by eliminating redundant accidentals that represent the same pitch in different forms. For example, "C##" becomes "D", and "Abb" becomes "G". This ensures consistent representation of the same musical pitch across different notational forms.

The method is called during note processing to maintain clean, standardized note representations. It's particularly useful when notes have been modified through operations like augmentation or diminishment that may introduce redundant accidentals.

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
    Preconditions: The note's name attribute must be a valid note string that can be processed by the underlying notes.remove_redundant_accidentals function
    Postconditions: The note's name attribute will contain a normalized form without redundant accidentals

## Side Effects:
    None

### `mingus.containers.note.Note.transpose` · *method*

## Summary:
Transposes the note by the specified interval, potentially adjusting the octave to maintain proper musical pitch relationships.

## Description:
Modifies the note's pitch by shifting it up or down according to the given interval. When transposing up, if the resulting note has a lower pitch value than the original, the octave is incremented. When transposing down, if the resulting note has a higher pitch value than the original, the octave is decremented. This ensures proper handling of octave boundaries when transposing across octaves.

## Args:
    interval (str): The interval to transpose by (e.g., 'm3', 'P5', 'M2')
    up (bool): Direction of transposition. True for upward transposition, False for downward. Defaults to True.

## Returns:
    None: This method modifies the instance in-place and does not return a value.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: The note must be a valid Note instance with a valid note name and octave
    Postconditions: The note's name and octave are updated to reflect the transposed pitch

## Side Effects:
    None

### `mingus.containers.note.Note.from_int` · *method*

## Summary:
Converts an integer representation of a musical note into its name and octave components.

## Description:
This method transforms an integer into a musical note by mapping the integer to a note name and octave. It's primarily used internally by the Note class constructor when an integer is passed as the initial note value. The method uses modular arithmetic to map integers to note names (0-11) and integer division to determine the octave.

## Args:
    integer (int): An integer representing a musical note, where 0-11 maps to C-B respectively, and higher values represent notes in higher octaves

## Returns:
    Note: Returns self to enable method chaining

## Raises:
    None explicitly raised, but note conversion may raise NoteFormatError from underlying functions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: The integer parameter should be a valid integer
    Postconditions: The Note instance will have its name and octave attributes set according to the integer mapping

## Side Effects:
    None

### `mingus.containers.note.Note.measure` · *method*

## Summary:
Calculates the interval (in semitones) between this note and another note.

## Description:
Measures the musical interval between the current note and another note by computing the difference in their MIDI note numbers. This method is used to determine how many semitones separate two musical notes, with positive results indicating the other note is higher in pitch and negative results indicating it's lower.

## Args:
    other: A note object or integer representing the destination note. When a Note object is passed, it's converted to its MIDI note number using the __int__ method. When an integer is passed, it's used directly.

## Returns:
    int: The interval in semitones between this note and the other note. Positive values indicate the other note is higher in pitch, negative values indicate it's lower, and zero indicates the same pitch.

## Raises:
    TypeError: If other cannot be converted to an integer (e.g., if it's a string that isn't a valid note representation).

## State Changes:
    Attributes READ: None - This method only reads the note's properties internally through the __int__ method
    Attributes WRITTEN: None - This method doesn't modify any attributes of self

## Constraints:
    Preconditions:
    - The other parameter must be convertible to an integer (either a Note object with a valid __int__ implementation or an integer)
    - Both notes should be valid musical notes for meaningful interval calculations
    
    Postconditions:
    - Returns an integer representing the semitone difference between the notes
    - The result is consistent with standard musical interval calculation (note2 - note1)

## Side Effects:
    None - This method performs no I/O, external service calls, or mutations to objects outside self

### `mingus.containers.note.Note.to_hertz` · *method*

## Summary
Converts a musical note to its frequency in Hertz using the standard MIDI to frequency conversion formula.

## Description
This method transforms a musical note represented as a Note object into its corresponding frequency in Hertz. It implements the standard formula for converting MIDI note numbers to frequencies, where A4 (the standard tuning pitch) is set to 440Hz by default. The method uses the relationship f = 2^(n/12) × A4_frequency, where n is the number of semitones away from the reference note.

## Args
    standard_pitch (float): The reference pitch in Hertz for A4. Defaults to 440.0.

## Returns
    float: The frequency of the note in Hertz.

## Raises
    None explicitly raised by this method.

## State Changes
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints
    Preconditions: The Note object must have valid note name and octave values.
    Postconditions: The returned value is a positive floating-point number representing the frequency.

## Side Effects
    None.

### `mingus.containers.note.Note.from_hertz` · *method*

## Summary:
Converts a frequency in Hertz to a musical note by updating the note's name and octave attributes.

## Description:
Transforms a frequency value (in Hertz) into a musical note representation using a logarithmic conversion formula. This method calculates the corresponding MIDI note number from the frequency, maps it to a note name (C through B), and determines the appropriate octave. The conversion follows a specific mathematical approach that accounts for standard pitch tuning and uses a 1024 multiplier in the calculation.

The method modifies the current Note instance's name and octave attributes, making it suitable for initializing or updating notes from frequency data. This is particularly useful in audio processing or music analysis applications where frequency measurements need to be converted to musical notation.

## Args:
    hertz (float): The frequency in Hertz to convert to a musical note. Must be positive.
    standard_pitch (float): The reference pitch in Hertz for tuning. Defaults to 440.0.

## Returns:
    Note: Returns self to enable method chaining for fluent interface patterns.

## Raises:
    None explicitly raised by this method, though underlying operations in notes.int_to_note may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.name, self.octave

## Constraints:
    Preconditions: 
    - hertz must be a positive number
    - standard_pitch should be a positive number
    
    Postconditions:
    - self.name will be set to a valid musical note name (e.g., "C", "C#", "D", etc.)
    - self.octave will be set to an appropriate octave number

## Side Effects:
    None

### `mingus.containers.note.Note.to_shorthand` · *method*

## Summary:
Converts a musical note to its shorthand notation representation using octave-adjusted letter names.

## Description:
Transforms a musical note into a compact string representation where:
- Notes in octave 3 or below use uppercase letter names (A, B, C, D, E, F, G)
- Notes in higher octaves use lowercase letter names (a, b, c, d, e, f, g)
- Octave adjustments are indicated by comma (,) for octaves below 3 and apostrophe (') for octaves above 3
- The reference octave is 3, so notes in octave 3 maintain their base letter name

This method provides a standardized way to represent musical notes in a compact format commonly used in music theory and notation systems.

## Args:
    None

## Returns:
    str: A shorthand string representation of the note in the format:
        - Base letter (uppercase for octave <= 3, lowercase for octave > 3)
        - Zero or more comma characters (,) for octaves below 3
        - Zero or more apostrophe characters (') for octaves above 3
        Examples: "C", "c'", "G,,", "f''"

## Raises:
    None explicitly raised

## State Changes:
    - Attributes READ: self.name, self.octave
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: The object must have `name` and `octave` attributes properly initialized
    - Postconditions: Returns a valid shorthand notation string with proper case and octave indicators

## Side Effects:
    None

### `mingus.containers.note.Note.from_shorthand` · *method*

## Summary:
Parses a shorthand musical note representation and sets the note's name and octave accordingly.

## Description:
Converts a shorthand string notation (like "c'", "B,", "db") into a proper note object by parsing the note name and octave modifiers. This method handles common musical shorthand formats where:
- Lowercase letters (a-g) represent notes in octave 3
- Uppercase letters (A-G) represent notes in octave 2
- Accidentals (#, b) are appended to the note name
- Comma (,) characters decrease the octave by 1
- Apostrophe (') characters increase the octave by 1

This method is part of the Note class's initialization and parsing capabilities, allowing for flexible note creation from string representations.

## Args:
    shorthand (str): A string representing a musical note in shorthand format, containing note names (a-g, A-G), accidentals (#, b), and octave modifiers (', ,)

## Returns:
    Note: The current Note instance (self) with updated name and octave properties

## Raises:
    NoteFormatError: When the note name portion of the shorthand is invalid

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: name, octave

## Constraints:
    Preconditions: The shorthand string must contain valid note characters and proper formatting
    Postconditions: The Note instance will have its name and octave set according to the shorthand representation

## Side Effects:
    None

### `mingus.containers.note.Note.__int__` · *method*

## Summary:
Converts a Note object to its MIDI note number representation.

## Description:
This special method transforms a Note object into an integer representing the MIDI note number. It calculates the note value by combining the octave (multiplied by 12) with the base note value, then adjusts for any accidentals (# or b) in the note name. This method enables Note objects to be used in arithmetic operations and comparisons.

## Args:
    None - This is a special method that takes no arguments beyond 'self'

## Returns:
    int: The MIDI note number (0-127) representing this note, where C4 = 60, C#4 = 61, Db4 = 61, etc.

## Raises:
    None - This method does not explicitly raise exceptions, but may propagate exceptions from underlying functions like notes.note_to_int()

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.name must be a valid note name string (e.g., "C", "C#", "Db", "Bb")
    - self.octave must be a valid integer
    - The note name should follow standard musical notation conventions
    
    Postconditions:
    - Returns an integer representing the MIDI note number
    - The returned value is consistent with standard MIDI note numbering

## Side Effects:
    None - This method performs no I/O or external service calls

### `mingus.containers.note.Note.__lt__` · *method*

## Summary:
Implements the less-than comparison operator for musical notes by comparing their MIDI note number representations.

## Description:
This special method enables the use of the `<` operator between Note objects. It converts both the current Note instance and the compared object to integer representations using the `__int__` method and compares those integers. This allows musical notes to be ordered by pitch, where lower MIDI note numbers represent lower pitches. The method also handles the special case where the comparison object is None by returning False.

## Args:
    other (Note or None): Another Note object to compare with, or None

## Returns:
    bool: True if the current note has a lower pitch than the other note, False otherwise. Returns False when comparing with None.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None (reads no instance attributes directly)
    Attributes WRITTEN: None (modifies no instance attributes)

## Constraints:
    Preconditions: The other parameter can be a Note instance or None
    Postconditions: Returns a boolean value indicating the result of the < comparison

## Side Effects:
    None

### `mingus.containers.note.Note.__eq__` · *method*

## Summary:
Compares two Note objects for equality by their integer representations.

## Description:
This method implements the equality comparison operator (`==`) for Note objects. It converts both the current Note instance and the compared object to integer representations using the `__int__` method and checks if these integers are equal. This approach ensures that notes with the same pitch (regardless of enharmonic equivalents) are considered equal.

## Args:
    other (Note or None): Another Note object to compare with, or None

## Returns:
    bool: True if both notes have the same integer representation, False otherwise. Always returns False when comparing with None.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None (reads no instance attributes directly)
    Attributes WRITTEN: None (modifies no instance attributes)

## Constraints:
    Preconditions: The `other` parameter can be a Note object or None
    Postconditions: Returns a boolean value indicating equality of the integer representations of both notes

## Side Effects:
    None

### `mingus.containers.note.Note.__ne__` · *method*

## Summary:
Implements the "not equal" comparison operation for Note objects by negating the result of equality comparison.

## Description:
This method defines the behavior of the `!=` operator for Note objects. It returns the logical negation of the equality comparison between this Note instance and another object. When called, it delegates the actual comparison logic to the `__eq__` method and negates its result.

## Args:
    other (Note or None): Another Note object or None to compare with this instance

## Returns:
    bool: True if the notes are not equal according to their integer representations, False if they are equal

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None (reads no instance attributes directly)
    Attributes WRITTEN: None (modifies no instance attributes)

## Constraints:
    Preconditions: The `other` parameter can be a Note object or None
    Postconditions: Returns a boolean value indicating inequality of the two notes

## Side Effects:
    None

### `mingus.containers.note.Note.__gt__` · *method*

## Summary:
Implements the greater-than comparison operator for musical notes by logically negating the combination of less-than and equal comparisons.

## Description:
This method determines whether the current note is greater than another note in musical pitch. It leverages the existing `__lt__` and `__eq__` comparison methods to implement the greater-than operation using boolean logic: `not (self < other or self == other)`. This approach ensures consistency with the note comparison system and avoids duplicating the integer conversion and comparison logic.

## Args:
    other (Note or None): Another note object to compare against, or None

## Returns:
    bool: True if the current note has a higher pitch than the other note, False otherwise

## Raises:
    None explicitly raised, but may propagate exceptions from underlying comparison operations

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The other object must be a Note instance or None
    Postconditions: Returns a boolean value indicating pitch relationship

## Side Effects:
    None

### `mingus.containers.note.Note.__le__` · *method*

## Summary:
Implements the less-than-or-equal-to comparison operator for musical notes.

## Description:
This method enables the use of the `<=` operator between Note objects. It returns True if the current Note object has a pitch that is less than or equal to the other Note object's pitch. The comparison is performed by delegating to the existing `__lt__` and `__eq__` methods, ensuring consistency with the note comparison system.

## Args:
    other (Note or None): Another Note object to compare with, or None

## Returns:
    bool: True if the current note has a pitch less than or equal to the other note, False otherwise. Returns False when comparing with None.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None (reads no instance attributes directly)
    Attributes WRITTEN: None (modifies no instance attributes)

## Constraints:
    Preconditions: The `other` parameter can be a Note instance or None
    Postconditions: Returns a boolean value indicating the result of the <= comparison

## Side Effects:
    None

### `mingus.containers.note.Note.__ge__` · *method*

## Summary:
Implements the greater than or equal comparison operator for Note objects by negating the less than comparison.

## Description:
This method enables the use of the `>=` operator between Note objects. It returns True if the current Note object is greater than or equal to the other Note object, and False otherwise. The implementation leverages the existing `__lt__` method to avoid code duplication and maintain consistency in comparison logic.

## Args:
    other (Note or None): Another Note object to compare with, or None

## Returns:
    bool: True if the current note is greater than or equal to the other note, False otherwise. When comparing with None, returns False.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None (reads no instance attributes directly)
    Attributes WRITTEN: None (modifies no instance attributes)

## Constraints:
    Preconditions: The `other` parameter can be a Note object or None
    Postconditions: Returns a boolean value indicating the result of the >= comparison

## Side Effects:
    None

### `mingus.containers.note.Note.__repr__` · *method*

## Summary:
Returns a string representation of the Note object in the format "'note-octave'" (e.g., "'C-4'").

## Description:
This method provides a human-readable string representation of a Note object, primarily intended for debugging and development purposes. It formats the note name and octave into a standardized string format that clearly identifies the musical note.

The method is called automatically when the built-in `repr()` function is applied to a Note instance, or when the object is displayed in interactive environments like Python REPL. This allows developers to quickly identify the note's identity without having to inspect individual attributes.

## Args:
    None

## Returns:
    str: A formatted string representation of the note in the form "'name-octave'" where name is the note letter (e.g., 'C', 'D#') and octave is an integer.

## Raises:
    None

## State Changes:
    Attributes READ: self.name, self.octave
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Note object must have valid `name` and `octave` attributes that are accessible.
    Postconditions: The returned string follows the format "'name-octave'" where name is the note name and octave is the octave number.

## Side Effects:
    None

