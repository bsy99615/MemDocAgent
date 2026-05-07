# `notes.py`

## `mingus.core.notes.int_to_note` · *function*

## Summary:
Converts an integer representation of a musical note to its corresponding note name string.

## Description:
Transforms an integer in the range [0, 11] into a musical note name, supporting both sharp and flat accidentals. This function serves as a utility for converting numeric note representations into human-readable musical notation.

## Args:
    note_int (int): Integer representing a musical note (0-11). Valid values are 0-11 inclusive.
    accidentals (str): Accidental style to use for note naming. Defaults to "#". 
        Must be either "#" for sharps or "b" for flats.

## Returns:
    str: Musical note name corresponding to the input integer. Returns note names in the format:
        - With "#" (default): "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
        - With "b": "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"

## Raises:
    RangeError: When note_int is outside the valid range [0, 11].
    FormatError: When accidentals parameter is neither "#" nor "b".

## Constraints:
    Preconditions:
        - note_int must be an integer in the range [0, 11]
        - accidentals must be either "#" or "b"
    Postconditions:
        - Returns a valid musical note name string
        - The returned note name corresponds to the input integer position in the chromatic scale

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start int_to_note] --> B{note_int in range(12)?}
    B -- No --> C[Raise RangeError]
    B -- Yes --> D[Define note arrays ns and nf]
    D --> E{accidentals == "#"?}
    E -- Yes --> F[Return ns[note_int]]
    E -- No --> G{accidentals == "b"?}
    G -- Yes --> H[Return nf[note_int]]
    G -- No --> I[Raise FormatError]
```

## Examples:
    >>> int_to_note(0)
    'C'
    >>> int_to_note(1, accidentals="#")
    'C#'
    >>> int_to_note(1, accidentals="b")
    'Db'
    >>> int_to_note(12)
    # Raises RangeError
    >>> int_to_note(0, accidentals="x")
    # Raises FormatError
```

## `mingus.core.notes.is_enharmonic` · *function*

## Summary:
Determines whether two musical notes are enharmonically equivalent by comparing their chromatic scale positions.

## Description:
Compares two musical note strings to check if they represent the same pitch but with different names (e.g., C# and Db). This function converts both notes to their corresponding chromatic scale integer positions using `note_to_int()` and evaluates if they are equal.

The function serves as a utility for identifying enharmonic equivalence in musical notation, which is important for music theory applications and note manipulation where different spellings of the same pitch need to be recognized as identical. This extraction into its own function provides a clean interface for enharmonic comparison while encapsulating the underlying conversion logic.

## Args:
    note1 (str): A musical note string containing a note letter followed by optional accidentals (e.g., "C", "D#", "Eb"). Must follow valid musical note formatting rules where the first character is a valid note letter (C, D, E, F, G, A, B) and subsequent characters are only "#" or "b".
    note2 (str): A second musical note string to compare against the first note, following the same formatting rules as note1.

## Returns:
    bool: True if both notes represent the same pitch (are enharmonically equivalent), False otherwise. For example, "C#" and "Db" would return True, while "C" and "D" would return False.

## Raises:
    NoteFormatError: When either note1 or note2 contains an invalid musical note format that cannot be processed by `note_to_int()`. This occurs when the note string doesn't follow proper musical notation conventions (e.g., invalid note letters or malformed accidentals).

## Constraints:
    Preconditions:
    - Both arguments must be valid musical note strings
    - Note strings must follow standard musical notation (first character is a valid note letter, subsequent characters are only "#" or "b")
    
    Postconditions:
    - Returns a boolean value (True or False)
    - Function execution does not modify any external state

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start is_enharmonic] --> B[note_to_int(note1)]
    B --> C[note_to_int(note2)]
    C --> D[Compare integers]
    D --> E{Are integers equal?}
    E -- Yes --> F[Return True]
    E -- No --> G[Return False]
```

## Examples:
    >>> is_enharmonic("C#", "Db")
    True
    >>> is_enharmonic("C", "D")
    False
    >>> is_enharmonic("A##", "Bb")
    True
    >>> is_enharmonic("Fb", "E")
    True
    >>> is_enharmonic("B#", "C")
    True
    >>> is_enharmonic("Dbb", "C")
    True
```

## `mingus.core.notes.is_valid_note` · *function*

## Summary:
Validates whether a string represents a properly formatted musical note name.

## Description:
Checks if a note string follows proper musical notation conventions by ensuring the first character is a valid note letter and any subsequent characters are only accidentals (sharps or flats). This function is used to validate note formatting in the mingus music library.

## Args:
    note (str): A string representing a musical note, such as "C", "D#", "Eb", "A##", etc. Must not be empty.

## Returns:
    bool: True if the note string is valid according to musical notation rules, False otherwise.

## Raises:
    IndexError: When an empty string is passed as input, as the function attempts to access note[0].

## Constraints:
    Preconditions:
    - The input must be a non-empty string
    - The first character must be a valid note letter (typically C, D, E, F, G, A, B)
    - Subsequent characters, if any, must only be "#" (sharp) or "b" (flat)
    
    Postconditions:
    - Returns a boolean value indicating validity of the note format
    - Does not modify any external state

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start is_valid_note] --> B{note[0] in _note_dict?}
    B -- No --> C[Return False]
    B -- Yes --> D[Loop through note[1:]]
    D --> E{char != "b" AND char != "#"?}
    E -- Yes --> F[Return False]
    E -- No --> G[Continue loop]
    G --> H{End of loop?}
    H -- No --> D
    H -- Yes --> I[Return True]
```

## Examples:
    >>> is_valid_note("C")
    True
    >>> is_valid_note("D#")
    True
    >>> is_valid_note("Eb")
    True
    >>> is_valid_note("A##")
    True
    >>> is_valid_note("C#b")
    True
    >>> is_valid_note("X")
    False
    >>> is_valid_note("C$")
    False
    >>> is_valid_note("")
    IndexError: string index out of range
```

## `mingus.core.notes.note_to_int` · *function*

## Summary:
Converts a musical note string to its corresponding chromatic scale integer position (0-11).

## Description:
Transforms musical note names (like "C", "D#", "Eb") into integer values representing their position in the chromatic scale. This function handles standard musical note notation including sharps (#) and flats (b) and normalizes all enharmonic equivalents to the same integer value.

The function validates note format using `is_valid_note()` and raises `NoteFormatError` for invalid inputs. It processes the note string by:
1. Getting the base value from the first letter using an internal note dictionary
2. Adjusting the value for accidentals (# increases by 1, b decreases by 1)
3. Applying modulo 12 to wrap around the chromatic scale

This extraction into a separate function allows for consistent note-to-integer conversion throughout the music library while maintaining clear validation and normalization logic.

## Args:
    note (str): A musical note string containing a note letter followed by optional accidentals. Must be a valid note format (e.g., "C", "D#", "Eb", "A##"). The first character must be a valid note letter (C, D, E, F, G, A, B) and subsequent characters can only be "#" or "b".

## Returns:
    int: An integer value between 0 and 11 representing the note's position in the chromatic scale. All enharmonic equivalents map to the same integer (e.g., "C#" and "Db" both map to 1).

## Raises:
    NoteFormatError: When the input note string is not a valid musical note format according to `is_valid_note()`.

## Constraints:
    Preconditions:
    - Input must be a non-empty string
    - First character must be a valid note letter (C, D, E, F, G, A, B)
    - Subsequent characters, if any, must only be "#" or "b"
    
    Postconditions:
    - Returns an integer in the range [0, 11]
    - All valid enharmonic equivalents return the same result

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start note_to_int] --> B{is_valid_note(note)?}
    B -- No --> C[raise NoteFormatError]
    B -- Yes --> D[val = _note_dict[note[0]]]
    D --> E[for post in note[1:]]
    E --> F{post == "b"?}
    F -- Yes --> G[val -= 1]
    F -- No --> H{post == "#"?}
    H -- Yes --> I[val += 1]
    H -- No --> J[Continue loop]
    J --> K{End of loop?}
    K -- No --> E
    K -- Yes --> L[val % 12]
    L --> M[Return val]
```

## Examples:
    >>> note_to_int("C")
    0
    >>> note_to_int("C#")
    1
    >>> note_to_int("Db")
    1
    >>> note_to_int("B#")
    0
    >>> note_to_int("Eb")
    3
    >>> note_to_int("A##")
    10
    >>> note_to_int("Fb")
    4
```

## `mingus.core.notes.reduce_accidentals` · *function*

## Summary:
Reduces a musical note with accidentals to its canonical representation using either sharps or flats.

## Description:
Converts a musical note string containing accidentals (sharps '#' or flats 'b') into a standardized note representation. This function processes note strings like "C#", "Db", "A##", or "Fb" and returns a normalized version that uses either sharps or flats consistently.

The function works by:
1. Converting the base note to an integer value using `note_to_int`
2. Processing each accidental character to adjust the integer value accordingly
3. Normalizing the result to ensure proper enharmonic equivalence handling

This extraction into a separate function provides a clean interface for note normalization while maintaining consistency with the existing note conversion utilities in the library.

## Args:
    note (str): A musical note string containing a note letter followed by optional accidentals. Must start with a valid note letter (C, D, E, F, G, A, B) and subsequent characters can only be "#" or "b".

## Returns:
    str: A normalized musical note name string. The result will use either sharps or flats consistently, with the choice determined by the algorithm to maintain proper enharmonic equivalence.

## Raises:
    NoteFormatError: When the input note string contains invalid characters or is not a valid musical note format.

## Constraints:
    Preconditions:
    - Input must be a non-empty string
    - First character must be a valid note letter (C, D, E, F, G, A, B)
    - Subsequent characters, if any, must only be "#" or "b"
    
    Postconditions:
    - Returns a valid musical note name string
    - The returned note name represents the same pitch as the input

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce_accidentals] --> B[val = note_to_int(note[0])]
    B --> C[for token in note[1:]]
    C --> D{token == "b"?}
    D -- Yes --> E[val -= 1]
    D -- No --> F{token == "#"?}
    F -- Yes --> G[val += 1]
    F -- No --> H[raise NoteFormatError]
    H --> I{val >= note_to_int(note[0])?}
    I -- Yes --> J[int_to_note(val % 12)]
    I -- No --> K[int_to_note(val % 12, "b")]
```

## Examples:
    >>> reduce_accidentals("C#")
    'C#'
    >>> reduce_accidentals("Db")
    'C#'
    >>> reduce_accidentals("A##")
    'C#'
    >>> reduce_accidentals("Fb")
    'E'
    >>> reduce_accidentals("B#")
    'C'
```

## `mingus.core.notes.remove_redundant_accidentals` · *function*

## Summary:
Normalizes musical note notation by removing redundant accidentals and converting enharmonic equivalents to a canonical form.

## Description:
Processes a musical note string containing accidentals (sharps '#' and flats 'b') and reduces it to its simplest form by eliminating redundant accidentals and converting between enharmonic equivalents. This function takes a note string and applies the appropriate augmentation or diminishment operations to normalize the accidental representation.

## Args:
    note (str): A musical note string where the first character represents the base note (e.g., 'C', 'D', 'E'), followed by zero or more accidental characters ('#' for sharp, 'b' for flat). The note string must not be empty.

## Returns:
    str: A normalized note string with redundant accidentals removed and enharmonic equivalents converted to a canonical form. The result contains only the base note and minimal accidentals.

## Raises:
    IndexError: If the input note string is empty, as attempting to access note[0] or note[1:] will fail.

## Constraints:
    Preconditions:
        - Input note must be a non-empty string
        - First character should represent a valid musical note name
        - Subsequent characters should only be '#' or 'b' for accidentals
    Postconditions:
        - Output is always a string representing a valid musical note
        - The resulting note has the same pitch as the input but in normalized form

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start remove_redundant_accidentals(note)] --> B[Initialize val = 0]
    B --> C[Count accidentals in note[1:]]
    C --> D{token == "b"?}
    D -- Yes --> E[val -= 1]
    D -- No --> F{token == "#"?}
    F -- Yes --> G[val += 1]
    F -- No --> H[Continue]
    H --> C
    C --> I[Initialize result = note[0]]
    I --> J{val > 0?}
    J -- Yes --> K[result = augment(result)]
    K --> L[val -= 1]
    L --> M{val > 0?}
    M --> J
    J -- No --> N{val < 0?}
    N -- Yes --> O[result = diminish(result)]
    O --> P[val += 1]
    P --> Q{val < 0?}
    Q --> N
    N -- No --> R[Return result]
```

## Examples:
    >>> remove_redundant_accidentals("C##")
    "C#"
    >>> remove_redundant_accidentals("Dbb")
    "Db"
    >>> remove_redundant_accidentals("A#b")
    "A"
    >>> remove_redundant_accidentals("F")
    "F"
    >>> remove_redundant_accidentals("B###")
    "B#"
    >>> remove_redundant_accidentals("Ebb")
    "Eb"
    >>> remove_redundant_accidentals("Cb")
    "B"
    >>> remove_redundant_accidentals("C#")
    "C#"

## `mingus.core.notes.augment` · *function*

## Summary:
Converts musical note notation between flat and sharp representations by modifying the suffix character.

## Description:
Transforms a musical note string by either appending a sharp symbol (#) or removing a flat symbol (b) from the end. This function serves as a utility for normalizing note representations in the music notation system, allowing conversion between flat and sharp notations.

## Args:
    note (str): A musical note string that typically ends with either a flat symbol "b" or no accidentals. The note string should represent a valid musical note.

## Returns:
    str: A modified note string where:
        - If the input note doesn't end with "b", a "#" is appended to create a sharp version
        - If the input note ends with "b", the "b" is removed to create a natural note

## Raises:
    IndexError: If the input note string is empty, as attempting to access note[-1] will fail.

## Constraints:
    Preconditions:
        - Input note must be a string
        - Note should be a valid musical note representation
    Postconditions:
        - Output is always a string with proper note formatting
        - The transformation maintains musical note semantics

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start augment(note)] --> B{note[-1] != "b"?}
    B -- Yes --> C[note + "#"]
    B -- No --> D[note[:-1]]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> augment("C")
    "C#"
    >>> augment("Db")
    "D"
    >>> augment("A#")
    "A#"
    >>> augment("")
    IndexError: string index out of range

## `mingus.core.notes.diminish` · *function*

## Summary:
Converts a musical note between sharp and flat representations by modifying the accidentals.

## Description:
Transforms a musical note name by either appending a flat symbol ('b') if the note doesn't already have a sharp, or removing the sharp symbol if the note has one. This function handles the conversion between enharmonic equivalents in musical notation.

## Args:
    note (str): A musical note name, potentially including accidental symbols like '#' or 'b'. Must be a non-empty string.

## Returns:
    str: The transformed note name with adjusted accidentals. If the note ends with '#', it removes the sharp. Otherwise, it appends 'b' to create a flat version.

## Raises:
    IndexError: If the note parameter is an empty string, as accessing note[-1] would fail.

## Constraints:
    Precondition: The note parameter must be a non-empty string
    Postcondition: The returned string will either have a 'b' appended or have its trailing '#' removed

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start diminish()] --> B{note[-1] != "#"}
    B -- True --> C[note + "b"]
    B -- False --> D[note[:-1]]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> diminish("C#")
    "C"
    >>> diminish("D")
    "Db"
    >>> diminish("F#")
    "F"
    >>> diminish("A")
    "Ab"
    >>> diminish("B#")
    "B"
    >>> diminish("Eb")
    "Ebb"

