# `notes.py`

## `mingus.core.notes.int_to_note` · *function*

## Summary:
Converts an integer representation of a musical note to its corresponding note name string.

## Description:
This function maps integers from 0-11 to their respective musical note names, supporting both sharps and flats. It is designed to be a utility function for converting numeric note representations into human-readable note names within the mingus music theory library.

## Args:
    note_int (int): Integer representing a musical note (0-11). Must be within the range [0, 11].
    accidentals (str): Specifies the accidental style to use. Defaults to "#". Valid values are "#" for sharps and "b" for flats.

## Returns:
    str: The note name as a string. For example, 0 returns "C", 1 returns "C#", etc. When accidentals="b", returns flat equivalents like "Db" instead of "C#".

## Raises:
    RangeError: Raised when note_int is outside the valid range of 0-11.
    FormatError: Raised when accidentals parameter is neither "#" nor "b".

## Constraints:
    Preconditions:
        - note_int must be an integer in the range [0, 11]
        - accidentals must be either "#" or "b"
    Postconditions:
        - Returns a valid musical note name string
        - The returned string corresponds to the correct pitch class

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start int_to_note] --> B{note_int in range(12)?}
    B -- No --> C[Raise RangeError]
    B -- Yes --> D[Define ns and nf arrays]
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
This function evaluates whether two musical notes represent the same pitch class despite having different names (e.g., "C#" and "Db"). It leverages the `note_to_int` helper function to convert each note into its corresponding integer value within the chromatic scale, then compares these values for equality. This logic is encapsulated in a separate function to provide a clean interface for enharmonic checking while maintaining separation of concerns between note parsing and comparison logic.

## Args:
    note1 (str): First musical note string (e.g., "C", "D#", "Eb")
    note2 (str): Second musical note string (e.g., "C", "D#", "Eb")

## Returns:
    bool: True if both notes map to the same chromatic scale position (are enharmonic), False otherwise.

## Raises:
    NoteFormatError: When either note string does not conform to the expected format (empty string, invalid base note, or invalid accidental characters). This exception is propagated from the underlying `note_to_int` function.

## Constraints:
    Preconditions:
        - Both arguments must be valid note string formats
        - Notes must follow standard musical notation conventions (base note A-G with optional sharps or flats)
    Postconditions:
        - Function returns a boolean value indicating enharmonic equivalence
        - No side effects occur

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start is_enharmonic] --> B[note_to_int(note1)]
    C[note_to_int(note2)] --> D[Compare results]
    B --> D
    D --> E{Equal?}
    E -- Yes --> F[Return True]
    E -- No --> G[Return False]
```

## Examples:
    >>> is_enharmonic("C#", "Db")
    True
    >>> is_enharmonic("D", "Eb")
    True
    >>> is_enharmonic("C", "D")
    False
```

## `mingus.core.notes.is_valid_note` · *function*

## Summary:
Checks whether a note string conforms to the valid note format used in the mingus music library.

## Description:
This function validates that a note string follows the expected format for musical notes in the mingus library. It ensures the note starts with a valid note letter (defined in the internal _note_dict) and is followed only by accidentals (sharp '#' or flat 'b' symbols). This validation is extracted into a separate function to enforce a clear boundary between note parsing and note validation logic, making the code more modular and testable.

## Args:
    note (str): A string representing a musical note, such as "C", "D#", "Eb", etc. Must not be empty.

## Returns:
    bool: True if the note string is valid according to the mingus note format rules, False otherwise.

## Raises:
    None explicitly raised, but may raise IndexError if note is an empty string.

## Constraints:
    Preconditions:
        - The input note must be a string
        - The note string must not be empty
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
    D --> E{post != "b" AND post != "#"?}
    E -- Yes --> F[Return False]
    E -- No --> G[Continue Loop]
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
    >>> is_valid_note("F##")
    True
    >>> is_valid_note("X")
    False
    >>> is_valid_note("C#b")
    True
    >>> is_valid_note("")
    False
```

## `mingus.core.notes.note_to_int` · *function*

## Summary:
Converts a musical note string into its corresponding integer representation within the chromatic scale.

## Description:
Transforms a musical note (like "C", "D#", "Eb") into an integer value from 0-11, representing its position in the chromatic scale. This function handles standard note names and accidentals (sharps and flats) by converting them to a base note and applying pitch adjustments. The logic is separated from validation to allow for clean parsing and conversion workflows.

## Args:
    note (str): A musical note string composed of a base note letter (A-G) followed by zero or more accidentals ('#' for sharp, 'b' for flat). Must be a valid note format.

## Returns:
    int: An integer between 0 and 11 inclusive, representing the note's position in the chromatic scale (C=0, C#=1, D=2, ..., B=11).

## Raises:
    NoteFormatError: When the input note string does not conform to the expected format (empty string, invalid base note, or invalid accidental characters).

## Constraints:
    Preconditions:
        - Input note must be a non-empty string
        - Base note character must be one of the valid note letters (A-G)
        - Accidental characters must be either '#' or 'b'
    Postconditions:
        - Output is always in the range [0, 11]
        - Function is deterministic for valid inputs

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start note_to_int] --> B{is_valid_note(note)?}
    B -- No --> C[Raise NoteFormatError]
    B -- Yes --> D[val = _note_dict[note[0]]]
    D --> E[Loop through note[1:]]
    E --> F{post == "b"?}
    F -- Yes --> G[val -= 1]
    F -- No --> H{post == "#"?}
    H -- Yes --> I[val += 1]
    H -- No --> J[Invalid accidental]
    J --> K[Raise NoteFormatError]
    G --> L[Continue Loop]
    I --> L
    L --> M{End of loop?}
    M -- No --> E
    M -- Yes --> N[val % 12]
    N --> O[Return result]
```

## Examples:
    >>> note_to_int("C")
    0
    >>> note_to_int("C#")
    1
    >>> note_to_int("Db")
    1
    >>> note_to_int("B")
    11
    >>> note_to_int("A#")
    10
```

## `mingus.core.notes.reduce_accidentals` · *function*

## Summary:
Reduces a musical note with accidentals to its simplest enharmonic equivalent within the chromatic scale.

## Description:
Transforms a musical note string containing sharps and flats into its canonical form, choosing between sharp and flat representations based on the note's position in the chromatic scale. This function ensures consistent note representation by normalizing accidentals while preserving the correct pitch class.

## Args:
    note (str): A musical note string composed of a base note letter (A-G) followed by zero or more accidentals ('#' for sharp, 'b' for flat). Must be a valid note format.

## Returns:
    str: The simplified note name as a string, using either sharps or flats consistently. For example, "C#" and "Db" both map to the same pitch class but return "C#" when the normalized value is >= 0, or "Db" when it's negative.

## Raises:
    NoteFormatError: When the input note string contains invalid characters or does not conform to the expected format.

## Constraints:
    Preconditions:
        - Input note must be a non-empty string
        - Base note character must be one of the valid note letters (A-G)
        - Accidental characters must be either '#' or 'b'
    Postconditions:
        - Output is always a valid musical note name string
        - The returned note represents the same pitch class as the input

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start reduce_accidentals] --> B[val = note_to_int(note[0])]
    B --> C[Loop through note[1:]]
    C --> D{token == "b"?}
    D -- Yes --> E[val -= 1]
    D -- No --> F{token == "#"?}
    F -- Yes --> G[val += 1]
    F -- No --> H[Raise NoteFormatError]
    E --> I[Continue Loop]
    G --> I
    I --> J{End of loop?}
    J -- No --> C
    J -- Yes --> K{val >= note_to_int(note[0])?}
    K -- Yes --> L[return int_to_note(val % 12)]
    K -- No --> M[return int_to_note(val % 12, "b")]
```

## Examples:
    >>> reduce_accidentals("C#")
    'C#'
    >>> reduce_accidentals("Db")
    'C#'
    >>> reduce_accidentals("B#")
    'C'
    >>> reduce_accidentals("Ebb")
    'D'
```

## `mingus.core.notes.remove_redundant_accidentals` · *function*

## Summary:
Normalizes musical note strings by removing redundant accidentals and returning the simplest enharmonic equivalent.

## Description:
This function processes a musical note string containing multiple accidentals and returns a normalized version with redundant accidentals eliminated. It calculates the net accidental adjustment needed by analyzing the tokens after the first character, then applies the appropriate augmentation or diminishment operations to produce the final note with the simplest enharmonic spelling.

The function serves as a dedicated utility for note normalization, extracting this logic from inline code to ensure consistent handling of enharmonic spellings throughout the system. This abstraction enables cleaner code organization and prevents duplication of accidental processing logic.

## Args:
    note (str): A musical note string where the first character represents the base note (e.g., 'C', 'D') and subsequent characters represent accidentals ('#', 'b'). Must be a non-empty string with valid musical note format.

## Returns:
    str: A normalized note string with redundant accidentals removed. The result maintains the same pitch but uses the most conventional enharmonic spelling.

## Raises:
    None

## Constraints:
    Precondition: The input note must be a non-empty string with valid musical note format.
    Postcondition: The returned note string represents the same pitch as the input but with redundant accidentals eliminated.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start remove_redundant_accidentals()] --> B[val = 0]
    B --> C[For each token in note[1:]]
    C --> D{token == "b"?}
    D -- Yes --> E[val -= 1]
    D -- No --> F{token == "#"?}
    F -- Yes --> G[val += 1]
    F -- No --> H[Continue loop]
    E --> I[Loop continue]
    G --> I
    H --> I
    I --> J[result = note[0]]
    J --> K[val > 0?]
    K -- Yes --> L[while val > 0: result = augment(result); val -= 1]
    K -- No --> M[val < 0?]
    M -- Yes --> N[while val < 0: result = diminish(result); val += 1]
    M -- No --> O[Return result]
    L --> P[Loop continue]
    N --> Q[Loop continue]
    P --> O
    Q --> O
```

## Examples:
    >>> remove_redundant_accidentals("C##")
    'D#'
    >>> remove_redundant_accidentals("Eb")
    'E'
    >>> remove_redundant_accidentals("Bbb")
    'A'
```

## `mingus.core.notes.augment` · *function*

## Summary:
Adjusts musical note accidentals by adding sharps or removing flats to maintain proper enharmonic notation.

## Description:
This function modifies musical note representations by adjusting their accidentals. When a note does not end with a flat symbol ("b"), it appends a sharp symbol ("#"). When a note ends with a flat symbol, it removes the flat to create the equivalent sharp note. This ensures proper enharmonic spelling in music theory applications where notes like "Eb" and "D#" represent the same pitch but are written differently.

## Args:
    note (str): A string representing a musical note, such as "C", "D#", "Eb", or "Bb". Must be a valid note representation.

## Returns:
    str: The transformed note with adjusted accidentals. If the input note doesn't end with "b", a "#" is appended. If it ends with "b", the "b" is removed.

## Raises:
    None

## Constraints:
    Precondition: The input note must be a valid string representing a musical note.
    Postcondition: The returned note will either have a "#" appended or have its trailing "b" removed, maintaining proper enharmonic spelling.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start augment()] --> B{note[-1] != "b"?}
    B -- Yes --> C[note + "#"]
    B -- No --> D[note[:-1]]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> augment("C")
    'C#'
    >>> augment("Eb")
    'E'
    >>> augment("Bb")
    'B'
    >>> augment("D#")
    'D##'

## `mingus.core.notes.diminish` · *function*

## Summary:
Transforms a musical note by lowering its pitch by one semitone, either by removing a sharp (#) or adding a flat (b).

## Description:
This function performs a basic pitch reduction operation on musical notes. When given a sharp note (ending with '#'), it removes the sharp symbol. When given a natural note (without accidental), it appends a flat symbol. This is a simplified implementation that works for basic note transformations but does not account for all chromatic relationships (e.g., it doesn't handle enharmonic equivalents properly like C# = Db).

## Args:
    note (str): A string representing a musical note, such as 'C', 'C#', or 'Db'. Must be a non-empty string.

## Returns:
    str: The transformed note string. For example:
        - 'C#' becomes 'D' (removes sharp)
        - 'Db' becomes 'C' (removes flat)
        - 'A' becomes 'Ab' (adds flat)

## Raises:
    TypeError: If note is not a string.
    IndexError: If note is an empty string.

## Constraints:
    - Preconditions: The input note must be a non-empty string.
    - Postconditions: The returned string is a valid note representation that follows the transformation logic.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start diminish()] --> B{note[-1] != "#"}
    B -- True --> C[note + "b"]
    B -- False --> D[note[:-1]]
    C --> E[Return modified note]
    D --> E
```

## Examples:
    >>> diminish("C#")
    'D'
    >>> diminish("Db")
    'C'
    >>> diminish("A")
    'Ab'

