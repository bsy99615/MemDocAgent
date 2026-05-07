# `notes.py`

## `mingus.core.notes.int_to_note` · *function*

## Summary:
Converts an integer representation of a musical note to its corresponding note name string.

## Description:
Transforms an integer value (0-11) into a musical note name, supporting both sharps and flats. This function serves as a utility for converting numerical note representations into human-readable musical notation.

## Args:
    note_int (int): Integer representing a musical note (0-11). 0=C, 1=C#, 2=D, etc.
    accidentals (str): Optional parameter specifying accidental type. Defaults to "#". 
        Must be either "#" for sharps or "b" for flats.

## Returns:
    str: Musical note name corresponding to the input integer. Returns note names in 
        either sharp format (C#, D#, etc.) or flat format (Db, Eb, etc.) based on the 
        accidentals parameter.

## Raises:
    RangeError: When note_int is not within the valid range of 0-11.
    FormatError: When accidentals parameter is neither "#" nor "b".

## Constraints:
    Preconditions:
        - note_int must be an integer in the range [0, 11]
        - accidentals must be either "#" or "b"
    Postconditions:
        - Returns a valid musical note name string
        - The returned note name corresponds to the input integer value

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start int_to_note] --> B{note_int in range(12)?}
    B -- No --> C[Raise RangeError]
    B -- Yes --> D{accidentals == "#"?}
    D -- Yes --> E[Return ns[note_int]]
    D -- No --> F{accidentals == "b"?}
    F -- Yes --> G[Return nf[note_int]]
    F -- No --> H[Raise FormatError]
```

## Examples:
    >>> int_to_note(0)
    'C'
    >>> int_to_note(1, "#")
    'C#'
    >>> int_to_note(1, "b")
    'Db'
    >>> int_to_note(12)
    # Raises RangeError
    >>> int_to_note(0, "x")
    # Raises FormatError
```

## `mingus.core.notes.is_enharmonic` · *function*

## Summary:
Determines whether two musical note names represent the same pitch by comparing their integer equivalents.

## Description:
Compares two musical note strings to check if they are enharmonically equivalent, meaning they represent the same pitch but with different names (such as C# and Db). This function converts each note to its corresponding integer value in semitones using the note_to_int() function and compares these values for equality.

The function is extracted into its own component to provide a clean interface for enharmonic comparison while encapsulating the underlying conversion logic. This separation allows other components to perform enharmonic checks without duplicating the note-to-integer conversion code.

## Args:
    note1 (str): A musical note string in standard format such as "C", "C#", "Cb", "Dbb", etc. Must be a valid note format.
    note2 (str): A second musical note string in standard format for comparison. Must also be a valid note format.

## Returns:
    bool: True if both notes represent the same pitch (are enharmonically equivalent), False otherwise. For example, "C#" and "Db" would return True, while "C" and "D" would return False.

## Raises:
    NoteFormatError: When either note1 or note2 does not conform to valid musical note format as validated by the note_to_int() function.

## Constraints:
    Preconditions:
    - Both note1 and note2 must be valid musical note strings
    - Each note must be a non-empty string
    - Each note must be a valid format recognized by the note_to_int() function
    
    Postconditions:
    - Returns a boolean value indicating enharmonic equivalence
    - The function does not modify any external state

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start is_enharmonic] --> B[note_to_int(note1)]
    C[note_to_int(note2)] --> D[Compare integers]
    B --> E{Equal?}
    E -->|Yes| F[Return True]
    E -->|No| G[Return False]
```

## Examples:
    # Enharmonic equivalents
    assert is_enharmonic("C#", "Db") == True    # Same pitch: C sharp equals D flat
    assert is_enharmonic("B#", "C") == True     # Same pitch: B sharp equals C
    assert is_enharmonic("Dbb", "C") == True    # Same pitch: Double flat D equals C
    
    # Different pitches
    assert is_enharmonic("C", "D") == False     # Different pitches
    assert is_enharmonic("A", "A#") == False    # Adjacent pitches
```

## `mingus.core.notes.is_valid_note` · *function*

## Summary:
Validates whether a note string follows proper musical notation format with valid note names and optional sharps or flats.

## Description:
Checks if a note string conforms to standard musical notation by verifying that the note name is valid according to the internal note dictionary and that any accidentals (sharp '#' or flat 'b') are properly formatted. This function serves as a format validator for note representations in the mingus music library.

The function separates note name validation from accidental validation, enforcing a clear responsibility boundary that keeps note parsing logic modular and reusable. Rather than inlining this validation logic, extracting it into a dedicated function improves code organization and testability.

## Args:
    note (str): A musical note string to validate, typically in format like "C", "C#", "Cb", "Dbb", etc. The first character must be a valid note name according to internal note dictionary.

## Returns:
    bool: True if the note string is properly formatted with a valid note name followed by zero or more accidentals ('#' or 'b'), False otherwise.

## Raises:
    None: This function does not raise exceptions directly, though it may be used in contexts where NoteFormatError or other exceptions are raised.

## Constraints:
    Preconditions:
    - The note parameter must be a string
    - The note string must not be empty
    
    Postconditions:
    - Returns boolean value indicating validity of note format
    - Does not modify any external state

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start is_valid_note] --> B{note[0] in _note_dict?}
    B -->|No| C[Return False]
    B -->|Yes| D[Loop through note[1:]]
    D --> E{post != "b" AND post != "#"?}
    E -->|Yes| F[Return False]
    E -->|No| G[Continue Loop]
    G --> H{End of note[1:]?}
    H -->|No| D
    H -->|Yes| I[Return True]
```

## Examples:
    # Valid note formats
    assert is_valid_note("C") == True
    assert is_valid_note("C#") == True
    assert is_valid_note("Cb") == True
    assert is_valid_note("Dbb") == True
    
    # Invalid note formats  
    assert is_valid_note("X") == False
    assert is_valid_note("C#x") == False  # 'x' is not a valid accidental
    assert is_valid_note("") == False     # Empty string

## `mingus.core.notes.note_to_int` · *function*

## Summary:
Converts a musical note string representation into its corresponding integer value in semitones, with support for sharps and flats.

## Description:
Transforms musical note names (like "C", "C#", "Cb") into integer values representing their position in the chromatic scale, where C=0, C#=1, Db=1, etc. The function handles standard musical notation with optional accidentals and normalizes results to the range [0, 11].

This function extracts the core logic of note-to-integer conversion from the broader note processing pipeline, allowing other components to reuse this mapping without duplicating the conversion logic. The separation enables clean testing and maintenance of the note conversion functionality.

## Args:
    note (str): A musical note string in standard format such as "C", "C#", "Cb", "Dbb", etc. Must be a valid note format as determined by is_valid_note() function. The note name portion must be a valid key in the internal _note_dict mapping.

## Returns:
    int: An integer value in the range [0, 11] representing the note's position in the chromatic scale. For example, C=0, C#=1, Db=1, D=2, etc. The result is computed by starting with the base note value and adjusting for accidentals, then taking modulo 12.

## Raises:
    NoteFormatError: When the note parameter does not conform to valid musical note format as validated by is_valid_note() function.

## Constraints:
    Preconditions:
    - The note parameter must be a non-empty string
    - The note must be a valid musical note format (as validated by is_valid_note())
    - The note name (first character) must be a valid key in the internal _note_dict mapping
    
    Postconditions:
    - Returns an integer in the range [0, 11] 
    - The result represents the note's position in the chromatic scale modulo 12
    - The calculation accounts for all accidentals in the note string

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start note_to_int] --> B{is_valid_note(note)?}
    B -->|No| C[raise NoteFormatError]
    B -->|Yes| D[val = _note_dict[note[0]]]
    D --> E[for post in note[1:]]
    E --> F{post == "b"?}
    F -->|Yes| G[val -= 1]
    F -->|No| H{post == "#"?}
    H -->|Yes| I[val += 1]
    H -->|No| J[Continue loop]
    J --> K{End of note[1:]?}
    K -->|No| E
    K -->|Yes| L[val % 12]
    L --> M[Return val]
```

## Examples:
    # Basic note conversions
    assert note_to_int("C") == 0      # Middle C
    assert note_to_int("C#") == 1     # Chromatic semitone above C
    assert note_to_int("Db") == 1     # Flat D equals sharp C
    assert note_to_int("D") == 2      # D note
    
    # Multiple accidentals
    assert note_to_int("Dbb") == 0    # Double flat D equals C
    assert note_to_int("E#") == 3     # Sharp E equals F
    
    # Error case
    try:
        note_to_int("X")
    except NoteFormatError:
        pass  # Expected behavior for invalid note format

## `mingus.core.notes.reduce_accidentals` · *function*

## Summary:
Reduces a musical note with accidentals to its canonical representation using either sharps or flats.

## Description:
Converts a musical note string containing accidentals (sharps '#' and flats 'b') into its simplest form, choosing between sharp or flat notation based on the resulting pitch value. This function ensures consistent musical notation by normalizing enharmonic equivalents.

The function processes note strings like "C#", "Cb", "Cbb", "C###" and returns a normalized representation. It separates the note name from accidentals, calculates the total semitone offset, and then maps back to a standard note name using either sharp or flat notation depending on the calculated value.

This logic is extracted into its own function to provide a clean interface for note normalization while keeping the core conversion logic separate from other note processing operations.

## Args:
    note (str): A musical note string in standard format such as "C", "C#", "Cb", "Cbb", "C###", etc. The note must start with a valid note letter (A-G) followed by zero or more accidentals ('#' or 'b').

## Returns:
    str: A normalized musical note string in either sharp or flat notation. The result will be one of the standard note names (C, C#, D, Db, etc.) where the accidental choice follows the convention that positive values use sharps and negative/low values use flats.

## Raises:
    NoteFormatError: When the note parameter contains invalid characters or format that cannot be processed.

## Constraints:
    Preconditions:
    - The note parameter must be a non-empty string
    - The note must start with a valid note letter (A-G)
    - All subsequent characters must be either '#' or 'b' for accidentals
    - The note must represent a valid musical note format
    
    Postconditions:
    - Returns a valid musical note string in standard format
    - The returned note represents the same pitch as the input note
    - The note is normalized to either sharp or flat notation

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce_accidentals] --> B[val = note_to_int(note[0])]
    B --> C[for token in note[1:]]
    C --> D{token == "b"?}
    D -->|Yes| E[val -= 1]
    D -->|No| F{token == "#"?}
    F -->|Yes| G[val += 1]
    F -->|No| H[raise NoteFormatError]
    H --> I[Continue loop]
    I --> J{End of note[1:]?}
    J -->|No| C
    J -->|Yes| K[val >= note_to_int(note[0])?]
    K -->|Yes| L[return int_to_note(val % 12)]
    K -->|No| M[return int_to_note(val % 12, "b")]
```

## Examples:
    # Basic note reduction
    assert reduce_accidentals("C#") == "C#"      # Already canonical
    assert reduce_accidentals("Db") == "C#"     # Enharmonic equivalent
    assert reduce_accidentals("Cbb") == "A#"    # Double flat C equals A#
    
    # Complex accidentals
    assert reduce_accidentals("C###") == "D#"   # Triple sharp C equals D#
    assert reduce_accidentals("Cbbbb") == "A"   # Quadruple flat C equals A
    
    # Error case
    try:
        reduce_accidentals("C$")
    except NoteFormatError:
        pass  # Expected behavior for invalid format

## `mingus.core.notes.remove_redundant_accidentals` · *function*

## Summary:
Normalizes a musical note string by eliminating redundant accidentals and converting between enharmonic equivalents.

## Description:
Processes a musical note string by analyzing its accidental symbols and returning a canonical representation. The function calculates the net number of sharps and flats (excluding the first character which is the note name) and applies appropriate augmentation or diminishment operations to produce a normalized note representation. This handles cases like "C##" becoming "D" or "Dbb" becoming "C".

## Args:
    note (str): A musical note string where the first character is the base note name (e.g., 'C', 'D', 'A') and subsequent characters are accidental symbols ('#' for sharp, 'b' for flat). Valid examples include "C#", "Db", "A##", "Bbb", "Fb".

## Returns:
    str: A normalized musical note string with redundant accidentals eliminated. The result follows standard musical notation conventions where consecutive sharps/flats are reduced to a single representation, and enharmonically equivalent notes are converted to their preferred form.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - Input note must be a string with at least one character
    - First character must be a valid musical note name (A-G)
    - Subsequent characters must be either '#' or 'b' symbols
    
    Postconditions:
    - Returns a string representing a normalized musical note
    - The result contains at most one accidental symbol (or none for natural notes)

## Side Effects:
    None

## Control Flow:
The function first counts the net number of sharps and flats by iterating through the accidental portion of the note string. Then it applies the appropriate number of augmentations (for positive net values) or diminishments (for negative net values) to arrive at the normalized result.

## `mingus.core.notes.augment` · *function*

## Summary:
Converts a musical note string by adding a sharp symbol or removing a flat symbol.

## Description:
Transforms musical note representations by either appending a sharp symbol (#) to notes that don't end with flat (b) or removing the flat symbol from notes that end with flat. This function serves as a utility for converting between sharp and flat note representations in musical notation.

## Args:
    note (str): A musical note string that typically ends with either a sharp (#) or flat (b) symbol, or neither.

## Returns:
    str: The transformed note string with either a sharp added or flat removed, depending on the input note's ending character.

## Raises:
    None explicitly raised by this function based on the source code.

## Constraints:
    Preconditions:
    - Input note must be a string
    - Note should follow standard musical notation conventions
    
    Postconditions:
    - Output is always a string
    - If input doesn't end with 'b', output ends with '#'
    - If input ends with 'b', output doesn't end with 'b'

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start augment(note)] --> B{note[-1] != "b"?}
    B -->|True| C[note + "#"]
    B -->|False| D[note[:-1]]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> augment("C")
    "C#"
    >>> augment("D#")
    "D#"
    >>> augment("Eb")
    "E"
    >>> augment("Fb")
    "F"
```

## `mingus.core.notes.diminish` · *function*

## Summary:
Reduces a musical note by flattening it, converting sharps to flats or adding flats to natural notes.

## Description:
This function manipulates musical note names by either appending a flat symbol (b) to natural notes or removing a sharp symbol (#) from sharp notes. It's designed to transform notes according to musical theory conventions where a diminished interval reduces the pitch by a semitone.

## Args:
    note (str): A musical note represented as a string, such as "C", "D#", "Ab", etc.

## Returns:
    str: The flattened version of the input note. If the note ends with "#", the "#" is removed. Otherwise, a "b" is appended to the note.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The input note must be a valid string representing a musical note
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned note will either be a natural note with a flat suffix or a note with the sharp removed
    - The function maintains the note's pitch relationship in musical theory

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Ends with "#"?}
    B -->|No| C[Append "b"]
    B -->|Yes| D[Remove last character]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> diminish("C")
    "Cb"
    >>> diminish("D#")
    "D"
    >>> diminish("Ab")
    "Ab"
```

