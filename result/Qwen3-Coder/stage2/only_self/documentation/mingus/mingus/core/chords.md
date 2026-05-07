# `chords.py`

## `mingus.core.chords.triad` · *function*

## Summary:
Generates a musical triad by calculating the root note, third, and fifth intervals from a given note and key.

## Description:
Creates a triad by taking a root note and key, then computing the third and fifth intervals relative to that note within the key's scale. This function encapsulates the core logic for building basic triads in music theory applications.

## Args:
    note (str): The root note of the triad, represented as a string (e.g., 'C', 'D#', 'Bb'). Must be a valid note recognized by the notes module.
    key (str): The musical key in which to calculate the intervals, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the triad: [root note, third interval, fifth interval]. The intervals are calculated using the interval arithmetic defined in the intervals module, where the third is 2 semitones above the root and the fifth is 4 semitones above the root.

## Raises:
    KeyError: When the provided note is not a valid note according to the notes.is_valid_note() function.
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The note parameter must be a valid note string recognized by the notes module.
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The third interval is calculated as the second interval in the key's scale.
        - The fifth interval is calculated as the fourth interval in the key's scale.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[triad(note, key)] --> B{Is note valid?}
    B -- No --> C[Raise KeyError]
    B -- Yes --> D[Get notes in key]
    D --> E[Find note index in key]
    E --> F[Calculate third interval]
    F --> G[Calculate fifth interval]
    G --> H[Return [note, third, fifth]]
```

## Examples:
    >>> triad('C', 'C')
    ['C', 'E', 'G']
    >>> triad('A', 'C')
    ['A', 'C', 'E']

## `mingus.core.chords.triads` · *function*

## Summary:
Generates all triads for the notes in a given musical key by creating a triad for each note in that key.

## Description:
Creates a collection of triads by iterating through each note in the specified musical key and generating the corresponding triad using the triad() function. This function implements a caching mechanism to avoid recomputing the same set of triads for identical keys, improving performance for repeated operations.

## Args:
    key (str): The musical key for which to generate triads, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[list[str]]: A list of triads, where each triad is a list of three note strings [root, third, fifth]. The returned list contains one triad for each note in the key, ordered according to the notes in the key's scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly one triad for each note in the key.
        - Each triad in the returned list is a valid triad structure with three notes.
        - The order of triads matches the order of notes in the key's scale.

## Side Effects:
    - Modifies the global `_triads_cache` dictionary by storing computed results for future use.
    - May modify the global `_key_cache` dictionary indirectly through calls to `keys.get_notes()`.

## Control Flow:
```mermaid
flowchart TD
    A[triads(key)] --> B{Is key in _triads_cache?}
    B -- Yes --> C[Return cached result]
    B -- No --> D[Get notes in key]
    D --> E[Generate triad for each note]
    E --> F[Cache results in _triads_cache]
    F --> G[Return triads]
```

## Examples:
    >>> triads('C')
    [['C', 'E', 'G'], ['D', 'F#', 'A'], ['E', 'G', 'B'], ['F', 'A', 'C'], ['G', 'B', 'D'], ['A', 'C', 'E'], ['B', 'D', 'F#']]
    >>> triads('G')
    [['G', 'B', 'D'], ['A', 'C#', 'E'], ['B', 'D#', 'F#'], ['C', 'E', 'G'], ['D', 'F#', 'A'], ['E', 'G#', 'B'], ['F#', 'A#', 'C#']]
```

## `mingus.core.chords.major_triad` · *function*

## Summary
Constructs a major triad chord by combining a root note with its major third and perfect fifth intervals.

## Description
Creates a list containing three musical notes that form a major triad: the root note, its major third interval, and its perfect fifth interval. This function encapsulates the core logic for building major triads in music theory applications.

The function is typically called when constructing chords programmatically or when analyzing harmonic structures in musical compositions. It's designed to be a reusable building block for more complex chord manipulation operations.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the major triad.

## Returns
    list[str]: A list containing exactly three strings representing the notes of the major triad in the order [root, major third, perfect fifth]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying interval calculation functions if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions (major_third and perfect_fifth).
    Postcondition: The returned list always contains exactly three elements representing a proper major triad structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major third via intervals.major_third()]
    B --> C[Get perfect fifth via intervals.perfect_fifth()]
    C --> D[Return [note, major_third, perfect_fifth]]
```

## Examples
    >>> major_triad("C")
    ['C', 'E', 'G']
    
    >>> major_triad("A")
    ['A', 'C#', 'E']

## `mingus.core.chords.minor_triad` · *function*

## Summary:
Constructs a minor triad chord by combining a root note with its minor third and perfect fifth.

## Description:
Creates a minor triad chord by taking a root note and generating the notes that form a minor triad. This function extracts the common chord construction logic to ensure consistent triad formation regardless of the specific note used as the root.

## Args:
    note (str): A musical note represented as a string (e.g., "C", "D#", "Bb"). The note serves as the root of the minor triad.

## Returns:
    list[str]: A list containing exactly three notes forming a minor triad in the order [root, minor third, perfect fifth]. All notes are represented as strings in the same format as the input note.

## Raises:
    None explicitly raised by this function, though underlying interval calculation functions may raise exceptions if invalid note formats are provided.

## Constraints:
    Preconditions:
    - The input note must be a valid note string format recognized by the mingus library
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned list always contains exactly three notes
    - The notes are arranged in the standard minor triad pattern (root, minor third, perfect fifth)
    - All returned notes are in the same format as the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -->|Valid| C[Get minor third]
    B -->|Invalid| D[Raise exception]
    C --> E[Get perfect fifth]
    E --> F[Return [note, minor_third, perfect_fifth]]
```

## Examples:
    >>> minor_triad("C")
    ['C', 'Eb', 'G']
    
    >>> minor_triad("A")
    ['A', 'C', 'E']
    
    >>> minor_triad("F#")
    ['F#', 'A', 'C#']
```

## `mingus.core.chords.diminished_triad` · *function*

## Summary
Generates a diminished triad chord consisting of a root note, minor third, and minor fifth.

## Description
Creates a diminished triad by taking a root note and calculating the corresponding minor third and minor fifth intervals. This function implements the standard music theory concept of a diminished triad, which consists of three notes where the intervals between each pair are minor thirds.

The function extracts the logic for creating diminished triads into a reusable component to avoid code duplication and provide a clear interface for chord generation. This allows other parts of the music theory system to consistently generate diminished triads without reimplementing the interval calculation logic.

## Args
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). The note serves as the root of the diminished triad.

## Returns
    list[str]: A list containing exactly three notes representing the diminished triad in the order [root, minor third, minor fifth]. All notes are returned in the same format as the input note, preserving the original accidental (sharp/flats).

## Raises
    NoteFormatError: When the input note is not in a valid format recognized by the notes module. This occurs when the note string cannot be parsed or is not a recognized musical note.

## Constraints
    Preconditions:
        - The input note must be a valid musical note string format (e.g., 'C', 'C#', 'Db', 'B')
        - The note must be recognizable by the notes module's validation system
    
    Postconditions:
        - The returned list always contains exactly three notes
        - The notes in the returned list form a proper diminished triad structure
        - All returned notes maintain the same pitch class as the input note but with appropriate interval calculations

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -- Invalid --> C[Raise NoteFormatError]
    B -- Valid --> D[Get minor third]
    D --> E[Get minor fifth]
    E --> F[Return [note, minor_third, minor_fifth]]
```

## Examples
    >>> diminished_triad('C')
    ['C', 'Eb', 'Gb']
    
    >>> diminished_triad('A#')
    ['A#', 'C', 'D#']
    
    >>> diminished_triad('Bb')
    ['Bb', 'D', 'F']
```

## `mingus.core.chords.augmented_triad` · *function*

## Summary:
Creates an augmented triad chord from a given note by combining the root note, major third, and augmented fifth intervals.

## Description:
This function generates an augmented triad, which is a three-note chord consisting of a root note, a major third interval above it, and an augmented fifth interval above it. The function leverages existing interval and note manipulation utilities to construct the chord properly.

The function is extracted into its own component to encapsulate the logic for creating augmented triads, separating this specific musical chord construction from other chord-related operations and making the intent clear and reusable. This modularization allows for consistent creation of augmented triads throughout the library.

## Args:
    note (str): A note string representing the root of the augmented triad (e.g., "C", "D#", "Bb"). Must be a valid note format recognized by the mingus library.

## Returns:
    list[str]: A list containing three note strings forming the augmented triad [root, major third, augmented fifth]. The returned list always contains exactly three elements.

## Raises:
    FormatError: If the input note is not in a valid format recognized by the mingus library
    NoteFormatError: If the input note cannot be processed by underlying note manipulation functions

## Constraints:
    Preconditions:
        - The input note must be a valid note string format recognized by the mingus library
        - The note should follow standard musical note naming conventions (e.g., "C", "C#", "Cb", "D", etc.)
    
    Postconditions:
        - The returned list always contains exactly three note strings
        - The second element is always a major third above the root note
        - The third element is always an augmented fifth above the root note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start: augmented_triad(note)] --> B[Get major third of note]
    B --> C[Get major fifth of note]
    C --> D[Augment the major fifth]
    D --> E[Return [note, major_third, augmented_fifth]]
```

## Examples:
    >>> augmented_triad("C")
    ['C', 'E', 'G#']
    
    >>> augmented_triad("A")
    ['A', 'C#', 'F#']

## `mingus.core.chords.seventh` · *function*

## Summary:
Generates a seventh chord by combining a triad with a seventh interval.

## Description:
Creates a seventh chord by first generating a triad from the given note and key, then appending the seventh interval to form a complete four-note chord. This function serves as a convenience wrapper that combines the triad generation logic with the seventh interval calculation to produce standard seventh chords in music theory applications.

## Args:
    note (str): The root note of the seventh chord, represented as a string (e.g., 'C', 'D#', 'Bb'). Must be a valid note recognized by the notes module.
    key (str): The musical key in which to calculate the intervals, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing four note strings representing the seventh chord: [root note, third interval, fifth interval, seventh interval]. The intervals are calculated using the interval arithmetic defined in the intervals module, where the seventh is the 6th interval in the key's scale.

## Raises:
    KeyError: When the provided note is not a valid note according to the notes.is_valid_note() function.
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The note parameter must be a valid note string recognized by the notes module.
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly four note strings.
        - All returned notes are valid within the context of the specified key.
        - The seventh interval is calculated as the sixth interval in the key's scale.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[seventh(note, key)] --> B{Is note valid?}
    B -- No --> C[Raise KeyError]
    B -- Yes --> D[Get triad using triad()]
    D --> E[Get seventh interval using intervals.seventh()]
    E --> F[Combine triad and seventh]
    F --> G[Return [triad + [seventh]]]
```

## Examples:
    >>> seventh('C', 'C')
    ['C', 'E', 'G', 'B']
    >>> seventh('A', 'C')
    ['A', 'C', 'E', 'G']

## `mingus.core.chords.sevenths` · *function*

## Summary:
Generates all seventh chords for the given musical key by computing the seventh chord for each note in that key's scale.

## Description:
Computes the complete set of seventh chords available in a musical key by applying the seventh chord function to each note of the key's scale. This function implements a caching mechanism to avoid recomputing the same results for identical keys, making it efficient for repeated queries. It essentially builds a complete seventh chord progression for the specified key.

## Args:
    key (str): The musical key for which to generate seventh chords, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[list[str]]: A list of seventh chords, where each chord is represented as a list of four note strings. Each chord corresponds to a note in the key's scale, with the chord built on that note. The order follows the diatonic scale of the key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly seven seventh chords (one for each note in the diatonic scale).
        - Each seventh chord is a list of four note strings representing the root, third, fifth, and seventh intervals.
        - The chords are ordered according to the key's diatonic scale.

## Side Effects:
    - Modifies the global `_sevenths_cache` dictionary by storing computed results for future use.
    - May cause cache growth over time as new keys are processed.

## Control Flow:
```mermaid
flowchart TD
    A[sevenths(key)] --> B{Is key in _sevenths_cache?}
    B -- Yes --> C[Return cached result]
    B -- No --> D[Get notes in key using keys.get_notes(key)]
    D --> E[Apply seventh() to each note in the key's scale]
    E --> F[Store results in _sevenths_cache[key]]
    F --> G[Return list of seventh chords]
```

## Examples:
    >>> sevenths('C')
    [['C', 'E', 'G', 'B'], ['D', 'F', 'A', 'C'], ['E', 'G', 'B', 'D'], ['F', 'A', 'C', 'E'], ['G', 'B', 'D', 'F'], ['A', 'C', 'E', 'G'], ['B', 'D', 'F', 'A']]
    >>> sevenths('G')
    [['G', 'B', 'D', 'F#'], ['A', 'C', 'E', 'G'], ['B', 'D', 'F#', 'A'], ['C', 'E', 'G', 'B'], ['D', 'F#', 'A', 'C'], ['E', 'G', 'B', 'D'], ['F#', 'A', 'C', 'E']]

## `mingus.core.chords.major_seventh` · *function*

## Summary
Constructs a major seventh chord by combining a major triad with a major seventh interval above the root note.

## Description
Creates a list containing four musical notes that form a major seventh chord: the root note, its major third, perfect fifth, and major seventh intervals. This function serves as a specialized chord construction utility for generating major seventh harmonies in music theory applications.

The function is typically called when building complex harmonic structures or when analyzing extended chord progressions in musical compositions. It leverages existing chord construction utilities (`major_triad`) and interval calculation functions to maintain consistency with the rest of the music theory framework.

This logic is extracted into its own function rather than being inlined because it provides a clear semantic abstraction for major seventh chords, making the code more readable and maintainable while ensuring consistent chord construction patterns throughout the system.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the major seventh chord.

## Returns
    list[str]: A list containing exactly four strings representing the notes of the major seventh chord in the order [root, major third, perfect fifth, major seventh]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`major_triad` and `intervals.major_seventh`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly four elements representing a proper major seventh chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major triad via major_triad(note)]
    B --> C[Get major seventh via intervals.major_seventh(note)]
    C --> D[Concatenate triad and seventh]
    D --> E[Return [major_triad + [major_seventh]]]
```

## Examples
    >>> major_seventh("C")
    ['C', 'E', 'G', 'B']
    
    >>> major_seventh("A")
    ['A', 'C#', 'E', 'G#']

## `mingus.core.chords.minor_seventh` · *function*

## Summary:
Constructs a minor seventh chord by combining a minor triad with a minor seventh interval.

## Description:
Generates a minor seventh chord by first creating a minor triad from the given root note, then appending the minor seventh interval to form a complete four-note chord. This function encapsulates the standard musical theory construction of a minor seventh chord, which consists of a root note, minor third, perfect fifth, and minor seventh.

## Args:
    note (str): A musical note represented as a string (e.g., "C", "D#", "Bb"). This serves as the root note of the minor seventh chord.

## Returns:
    list[str]: A list containing exactly four notes forming a minor seventh chord in the order [root, minor third, perfect fifth, minor seventh]. All notes are represented as strings in the same format as the input note.

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions if invalid note formats are provided.

## Constraints:
    Preconditions:
    - The input note must be a valid note string format recognized by the mingus library
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned list always contains exactly four notes
    - The notes are arranged in the standard minor seventh chord pattern (root, minor third, perfect fifth, minor seventh)
    - All returned notes are in the same format as the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -->|Valid| C[Get minor triad using minor_triad()]
    C --> D[Get minor seventh using intervals.minor_seventh()]
    D --> E[Concatenate triad and seventh]
    E --> F[Return [minor_triad + [minor_seventh]]]
```

## Examples:
    >>> minor_seventh("C")
    ['C', 'Eb', 'G', 'Bb']
    
    >>> minor_seventh("A")
    ['A', 'C', 'E', 'G']
    
    >>> minor_seventh("F#")
    ['F#', 'A', 'C#', 'E']
```

## `mingus.core.chords.dominant_seventh` · *function*

## Summary
Constructs a dominant seventh chord by combining a major triad with a minor seventh interval.

## Description
Generates a list of four musical notes representing a dominant seventh chord built on the specified root note. This function combines the major triad of the input note with a minor seventh interval to create the characteristic sound of a dominant seventh chord.

This function is typically called when building harmonic progressions, analyzing jazz chords, or constructing musical scales programmatically. It serves as a specialized chord construction utility that leverages existing major triad and interval functions to create complex harmonic structures.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. This note serves as the root of the dominant seventh chord.

## Returns
    list[str]: A list containing exactly four strings representing the notes of the dominant seventh chord in the order [root, major third, perfect fifth, minor seventh]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (major_triad and intervals.minor_seventh) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly four elements representing a proper dominant seventh chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major triad via major_triad()]
    B --> C[Get minor seventh via intervals.minor_seventh()]
    C --> D[Combine results: major_triad + [minor_seventh]]
    D --> E[Return four-note chord]
```

## Examples
    >>> dominant_seventh("C")
    ['C', 'E', 'G', 'Bb']
    
    >>> dominant_seventh("A")
    ['A', 'C#', 'E', 'G']

## `mingus.core.chords.half_diminished_seventh` · *function*

## Summary
Generates a half-diminished seventh chord (also known as a minor seventh flat five chord) by combining a diminished triad with a minor seventh interval.

## Description
Creates a four-note chord consisting of a root note, minor third, diminished fifth, and minor seventh interval. This function implements the standard music theory concept of a half-diminished seventh chord, commonly notated as °7 or ø7. The chord is constructed by first generating a diminished triad (root, minor third, diminished fifth) and then appending a minor seventh interval to complete the chord structure.

This function extracts the logic for generating half-diminished seventh chords into a reusable component to avoid code duplication and provide a clear interface for chord generation. It enables consistent creation of these specific chord types throughout the music theory system without reimplementing the interval calculation logic.

## Args
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). This serves as the root note of the half-diminished seventh chord.

## Returns
    list[str]: A list containing exactly four notes representing the half-diminished seventh chord in the order [root, minor third, diminished fifth, minor seventh]. All notes are returned in the same format as the input note, preserving the original accidental (sharp/flats).

## Raises
    NoteFormatError: When the input note is not in a valid format recognized by the notes module. This occurs when the note string cannot be parsed or is not a recognized musical note.

## Constraints
    Preconditions:
        - The input note must be a valid musical note string format (e.g., 'C', 'C#', 'Db', 'B')
        - The note must be recognizable by the notes module's validation system
    
    Postconditions:
        - The returned list always contains exactly four notes
        - The notes in the returned list form a proper half-diminished seventh chord structure
        - All returned notes maintain the same pitch class as the input note but with appropriate interval calculations

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -- Invalid --> C[Raise NoteFormatError]
    B -- Valid --> D[Get diminished triad using diminished_triad()]
    D --> E[Get minor seventh using intervals.minor_seventh()]
    E --> F[Combine triad and seventh]
    F --> G[Return [diminished_triad + [minor_seventh]]]
```

## Examples
    >>> half_diminished_seventh('C')
    ['C', 'Eb', 'Gb', 'Bb']
    
    >>> half_diminished_seventh('A#')
    ['A#', 'C', 'D#', 'F#']
    
    >>> half_diminished_seventh('Bb')
    ['Bb', 'D', 'F', 'Ab']
```

## `mingus.core.chords.minor_seventh_flat_five` · *function*

## Summary
Generates a half-diminished seventh chord (also known as a minor seventh flat five chord) by combining a diminished triad with a minor seventh interval.

## Description
Creates a four-note chord consisting of a root note, minor third, diminished fifth, and minor seventh interval. This function implements the standard music theory concept of a half-diminished seventh chord, commonly notated as °7 or ø7. The chord is constructed by first generating a diminished triad (root, minor third, diminished fifth) and then appending a minor seventh interval to complete the chord structure.

This function serves as an alias for `half_diminished_seventh` and provides a clear semantic interface for generating half-diminished seventh chords. It enables consistent creation of these specific chord types throughout the music theory system without reimplementing the interval calculation logic.

## Args
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). This serves as the root note of the half-diminished seventh chord.

## Returns
    list[str]: A list containing exactly four notes representing the half-diminished seventh chord in the order [root, minor third, diminished fifth, minor seventh]. All notes are returned in the same format as the input note, preserving the original accidental (sharp/flats).

## Raises
    NoteFormatError: When the input note is not in a valid format recognized by the notes module. This occurs when the note string cannot be parsed or is not a recognized musical note.

## Constraints
    Preconditions:
        - The input note must be a valid musical note string format (e.g., 'C', 'C#', 'Db', 'B')
        - The note must be recognizable by the notes module's validation system
    
    Postconditions:
        - The returned list always contains exactly four notes
        - The notes in the returned list form a proper half-diminished seventh chord structure
        - All returned notes maintain the same pitch class as the input note but with appropriate interval calculations

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -- Invalid --> C[Raise NoteFormatError]
    B -- Valid --> D[Call half_diminished_seventh()]
    D --> E[Return result]
```

## Examples
    >>> minor_seventh_flat_five('C')
    ['C', 'Eb', 'Gb', 'Bb']
    
    >>> minor_seventh_flat_five('A#')
    ['A#', 'C', 'D#', 'F#']
    
    >>> minor_seventh_flat_five('Bb')
    ['Bb', 'D', 'F', 'Ab']
```

## `mingus.core.chords.diminished_seventh` · *function*

## Summary
Generates a diminished seventh chord by combining a diminished triad with a diminished seventh interval.

## Description
Creates a four-note diminished seventh chord by first generating a diminished triad from the input note, then appending the diminished seventh interval. This function implements the standard music theory concept of a diminished seventh chord, which consists of a root note, minor third, minor fifth, and diminished seventh - all stacked in thirds.

The function extracts the logic for creating diminished seventh chords into a reusable component to avoid code duplication and provide a clear interface for chord generation. This allows other parts of the music theory system to consistently generate diminished seventh chords without reimplementing the interval calculation logic.

## Args
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). The note serves as the root of the diminished seventh chord.

## Returns
    list[str]: A list containing exactly four notes representing the diminished seventh chord in the order [root, minor third, minor fifth, diminished seventh]. All notes are returned in the same format as the input note, preserving the original accidental (sharp/flats).

## Raises
    NoteFormatError: When the input note is not in a valid format recognized by the notes module. This occurs when the note string cannot be parsed or is not a recognized musical note.

## Constraints
    Preconditions:
        - The input note must be a valid musical note string format (e.g., 'C', 'C#', 'Db', 'B')
        - The note must be recognizable by the notes module's validation system
    
    Postconditions:
        - The returned list always contains exactly four notes
        - The notes in the returned list form a proper diminished seventh chord structure
        - All returned notes maintain the same pitch class as the input note but with appropriate interval calculations

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -- Invalid --> C[Raise NoteFormatError]
    B -- Valid --> D[Get diminished triad]
    D --> E[Get minor seventh interval]
    E --> F[Diminish minor seventh]
    F --> G[Combine triad and diminished seventh]
    G --> H[Return [triad + [diminished_seventh]]]
```

## Examples
    >>> diminished_seventh('C')
    ['C', 'Eb', 'Gb', 'Bbb']
    
    >>> diminished_seventh('A#')
    ['A#', 'C', 'D#', 'F']
    
    >>> diminished_seventh('Bb')
    ['Bb', 'D', 'F', 'Abb']
```

## `mingus.core.chords.minor_major_seventh` · *function*

## Summary
Constructs a minor major seventh chord by combining a minor triad with a major seventh interval above the root note.

## Description
Creates a list containing four musical notes that form a minor major seventh chord: the root note, its minor third, perfect fifth, and major seventh intervals. This function serves as a specialized chord construction utility for generating minor major seventh harmonies in music theory applications.

The function is typically called when building complex harmonic structures or when analyzing extended chord progressions in musical compositions. It leverages existing chord construction utilities (`minor_triad`) and interval calculation functions to maintain consistency with the rest of the music theory framework.

This logic is extracted into its own function rather than being inlined because it provides a clear semantic abstraction for minor major seventh chords, making the code more readable and maintainable while ensuring consistent chord construction patterns throughout the system.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the minor major seventh chord.

## Returns
    list[str]: A list containing exactly four strings representing the notes of the minor major seventh chord in the order [root, minor third, perfect fifth, major seventh]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`minor_triad` and `intervals.major_seventh`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly four elements representing a proper minor major seventh chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get minor triad via minor_triad(note)]
    B --> C[Get major seventh via intervals.major_seventh(note)]
    C --> D[Concatenate triad and seventh]
    D --> E[Return [minor_triad + [major_seventh]]]
```

## Examples
    >>> minor_major_seventh("C")
    ['C', 'Eb', 'G', 'B']
    
    >>> minor_major_seventh("A")
    ['A', 'C', 'E', 'G#']
    
    >>> minor_major_seventh("F#")
    ['F#', 'A', 'C#', 'E#']

## `mingus.core.chords.minor_sixth` · *function*

## Summary:
Constructs a minor sixth chord by combining a minor triad with a major sixth interval.

## Description:
Creates a minor sixth chord by taking a root note and generating the notes that form a minor sixth chord. This function extracts the chord construction logic for a minor sixth chord to ensure consistent formation regardless of the specific note used as the root.

## Args:
    note (str): A musical note represented as a string (e.g., "C", "D#", "Bb"). The note serves as the root of the minor sixth chord.

## Returns:
    list[str]: A list containing exactly four notes forming a minor sixth chord in the order [root, minor third, perfect fifth, major sixth]. All notes are represented as strings in the same format as the input note.

## Raises:
    None explicitly raised by this function, though underlying interval calculation functions may raise exceptions if invalid note formats are provided.

## Constraints:
    Preconditions:
    - The input note must be a valid note string format recognized by the mingus library
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned list always contains exactly four notes
    - The notes are arranged in the standard minor sixth chord pattern (root, minor third, perfect fifth, major sixth)
    - All returned notes are in the same format as the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -->|Valid| C[Get minor triad]
    B -->|Invalid| D[Raise exception]
    C --> E[Get major sixth]
    E --> F[Combine triad and sixth]
    F --> G[Return [minor_triad, major_sixth]]
```

## Examples:
    >>> minor_sixth("C")
    ['C', 'Eb', 'G', 'A']
    
    >>> minor_sixth("A")
    ['A', 'C', 'E', 'F#']
    
    >>> minor_sixth("F#")
    ['F#', 'A', 'C#', 'D#']
```

## `mingus.core.chords.major_sixth` · *function*

## Summary
Constructs a major sixth chord by combining a root note with its major triad and major sixth interval.

## Description
Creates a list containing four musical notes that form a major sixth chord: the root note, its major third interval, its perfect fifth interval, and its major sixth interval. This function builds upon the existing `major_triad` function and extends it by adding the major sixth interval to create a complete major sixth chord.

This logic is extracted into its own function to provide a clean interface for generating major sixth chords specifically, rather than having to manually combine triad construction with interval addition. It maintains consistency with the library's pattern of providing chord construction functions that encapsulate common musical chord structures.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the major sixth chord.

## Returns
    list[str]: A list containing exactly four strings representing the notes of the major sixth chord in the order [root, major third, perfect fifth, major sixth]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`major_triad` and `intervals.major_sixth`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly four elements representing a proper major sixth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major triad via major_triad(note)]
    B --> C[Get major sixth via intervals.major_sixth(note)]
    C --> D[Return [major_triad_result, major_sixth_note]]
```

## Examples
    >>> major_sixth("C")
    ['C', 'E', 'G', 'A']
    
    >>> major_sixth("A")
    ['A', 'C#', 'E', 'F#']

## `mingus.core.chords.dominant_sixth` · *function*

## Summary
Constructs a dominant sixth chord by combining a major sixth chord with a minor seventh interval.

## Description
Creates a list containing five musical notes that form a dominant sixth chord: the root note, its major third interval, its perfect fifth interval, its major sixth interval, and its minor seventh interval. This function builds upon the existing `major_sixth` function and extends it by adding the minor seventh interval to create a complete dominant sixth chord.

This logic is extracted into its own function to provide a clean interface for generating dominant sixth chords specifically, rather than having to manually combine major sixth construction with interval addition. It maintains consistency with the library's pattern of providing chord construction functions that encapsulate common musical chord structures.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the dominant sixth chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the dominant sixth chord in the order [root, major third, perfect fifth, major sixth, minor seventh]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`major_sixth` and `intervals.minor_seventh`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a proper dominant sixth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major sixth via major_sixth(note)]
    B --> C[Get minor seventh via intervals.minor_seventh(note)]
    C --> D[Combine results: major_sixth_result + [minor_seventh_note]]
    D --> E[Return complete dominant sixth chord]
```

## Examples
    >>> dominant_sixth("C")
    ['C', 'E', 'G', 'A', 'Bb']
    
    >>> dominant_sixth("A")
    ['A', 'C#', 'E', 'F#', 'G']

## `mingus.core.chords.sixth_ninth` · *function*

## Summary
Constructs a sixth-ninth chord by combining a major sixth chord with an added major second interval.

## Description
Creates a list containing five musical notes that form a sixth-ninth chord: the root note, its major third interval, its perfect fifth interval, its major sixth interval, and its major second interval. This function builds upon the existing `major_sixth` function and extends it by adding the major second interval to create a complete sixth-ninth chord structure.

This logic is extracted into its own function to provide a clean interface for generating sixth-ninth chords specifically, rather than having to manually combine chord construction with interval addition. It maintains consistency with the library's pattern of providing chord construction functions that encapsulate common musical chord structures.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the sixth-ninth chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the sixth-ninth chord in the order [root, major third, perfect fifth, major sixth, major second]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`major_sixth` and `intervals.major_second`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a proper sixth-ninth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major sixth via major_sixth(note)]
    B --> C[Get major second via intervals.major_second(note)]
    C --> D[Combine results: major_sixth_result + [major_second_note]]
    D --> E[Return combined chord]
```

## Examples
    >>> sixth_ninth("C")
    ['C', 'E', 'G', 'A', 'D']
    
    >>> sixth_ninth("A")
    ['A', 'C#', 'E', 'F#', 'B']

## `mingus.core.chords.minor_ninth` · *function*

## Summary:
Constructs a minor ninth chord by combining a minor seventh chord with a major second interval.

## Description:
Generates a minor ninth chord by first creating a minor seventh chord from the given root note, then appending the major second interval to form a complete nine-note chord. This function implements the standard musical theory construction of a minor ninth chord, which consists of a root note, minor third, perfect fifth, minor seventh, and major second. The resulting chord is commonly used in jazz and contemporary music.

## Args:
    note (str): A musical note represented as a string (e.g., "C", "D#", "Bb"). This serves as the root note of the minor ninth chord.

## Returns:
    list[str]: A list containing exactly five notes forming a minor ninth chord in the order [root, minor third, perfect fifth, minor seventh, major second]. All notes are represented as strings in the same format as the input note.

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions if invalid note formats are provided.

## Constraints:
    Preconditions:
    - The input note must be a valid note string format recognized by the mingus library
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned list always contains exactly five notes
    - The notes are arranged in the standard minor ninth chord pattern (root, minor third, perfect fifth, minor seventh, major second)
    - All returned notes are in the same format as the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B[Call minor_seventh(note)]
    B --> C[Get major second interval]
    C --> D[Concatenate results]
    D --> E[Return [minor_seventh + [major_second]]]
```

## Examples:
    >>> minor_ninth("C")
    ['C', 'Eb', 'G', 'Bb', 'D']
    
    >>> minor_ninth("A")
    ['A', 'C', 'E', 'G', 'B']
    
    >>> minor_ninth("F#")
    ['F#', 'A', 'C#', 'E', 'G#']

## `mingus.core.chords.major_ninth` · *function*

## Summary
Constructs a major ninth chord by combining a major seventh chord with a major second interval above the root note.

## Description
Creates a list containing five musical notes that form a major ninth chord: the root note, its major third, perfect fifth, major seventh, and major ninth intervals. This function serves as a specialized chord construction utility for generating major ninth harmonies in music theory applications.

The function is typically called when building extended harmonic structures or when analyzing complex chord progressions in musical compositions. It leverages the existing `major_seventh` chord construction function and the `intervals.major_second` function to maintain consistency with the rest of the music theory framework.

This logic is extracted into its own function rather than being inlined because it provides a clear semantic abstraction for major ninth chords, making the code more readable and maintainable while ensuring consistent chord construction patterns throughout the system.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the major ninth chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the major ninth chord in the order [root, major third, perfect fifth, major seventh, major ninth]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`major_seventh` and `intervals.major_second`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a proper major ninth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major seventh via major_seventh(note)]
    B --> C[Get major second via intervals.major_second(note)]
    C --> D[Create list with major second]
    D --> E[Concatenate major seventh and major second]
    E --> F[Return [major_seventh + [major_second]]]
```

## Examples
    >>> major_ninth("C")
    ['C', 'E', 'G', 'B', 'D']
    
    >>> major_ninth("A")
    ['A', 'C#', 'E', 'G#', 'B']

## `mingus.core.chords.dominant_ninth` · *function*

## Summary
Constructs a dominant ninth chord by extending a dominant seventh chord with a major second interval.

## Description
Generates a list of five musical notes representing a dominant ninth chord built on the specified root note. This function extends the dominant seventh chord by adding a major second interval, creating the characteristic sound of a dominant ninth chord commonly used in jazz harmony.

This function is typically called when building complex harmonic progressions, analyzing jazz chords, or constructing extended chord voicings programmatically. It serves as a specialized chord construction utility that leverages existing dominant seventh and interval functions to create sophisticated harmonic structures.

The logic is extracted into its own function rather than being inlined to maintain clean separation of concerns and promote code reuse. It provides a clear semantic meaning for dominant ninth chord construction while relying on well-tested underlying functions for the constituent parts.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. This note serves as the root of the dominant ninth chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the dominant ninth chord in the order [root, major third, perfect fifth, minor seventh, major second]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (dominant_seventh and intervals.major_second) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a proper dominant ninth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant seventh via dominant_seventh()]
    B --> C[Get major second via intervals.major_second()]
    C --> D[Combine results: dominant_seventh + [major_second]]
    D --> E[Return five-note chord]
```

## Examples
    >>> dominant_ninth("C")
    ['C', 'E', 'G', 'Bb', 'D']
    
    >>> dominant_ninth("A")
    ['A', 'C#', 'E', 'G', 'B']

## `mingus.core.chords.dominant_flat_ninth` · *function*

## Summary
Constructs a dominant flat ninth chord by replacing the ninth interval of a dominant ninth chord with a minor second interval.

## Description
Generates a list of five musical notes representing a dominant flat ninth chord built on the specified root note. This function first retrieves a dominant ninth chord structure via the dominant_ninth function, then replaces the fifth element (at index 4) with a minor second interval calculated from the input note, producing a dominant flat ninth chord.

This function is typically called when building complex harmonic progressions, analyzing jazz chords, or constructing extended chord voicings programmatically. It serves as a specialized chord construction utility that leverages existing dominant ninth and interval functions to create sophisticated harmonic structures.

The logic is extracted into its own function rather than being inlined to maintain clean separation of concerns and promote code reuse. It provides a clear semantic meaning for dominant flat ninth chord construction while relying on well-tested underlying functions for the constituent parts.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. This note serves as the root of the dominant flat ninth chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the dominant flat ninth chord. The structure consists of the same notes as a dominant ninth chord except that the ninth interval (originally a major second) is replaced with a minor second interval.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (dominant_ninth and intervals.minor_second) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a valid chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant ninth via dominant_ninth()]
    B --> C[Replace index 4 with minor second via intervals.minor_second()]
    C --> D[Return five-note chord]
```

## Examples
    >>> dominant_flat_ninth("C")
    # Returns a 5-note chord where the 5th element is a minor second above C
    
    >>> dominant_flat_ninth("A")
    # Returns a 5-note chord where the 5th element is a minor second above A

## `mingus.core.chords.dominant_sharp_ninth` · *function*

## Summary
Constructs a dominant sharp ninth chord by modifying the ninth interval of a dominant ninth chord to be augmented (sharpened).

## Description
Generates a list of five musical notes representing a dominant sharp ninth chord built on the specified root note. This function extends the dominant ninth chord by sharpening the ninth interval, creating the characteristic sound of a dominant sharp ninth chord commonly used in jazz harmony.

This function is typically called when building complex harmonic progressions, analyzing jazz chords, or constructing extended chord voicings programmatically. It serves as a specialized chord construction utility that leverages existing dominant ninth and interval functions to create sophisticated harmonic structures.

The logic is extracted into its own function rather than being inlined to maintain clean separation of concerns and promote code reuse. It provides a clear semantic meaning for dominant sharp ninth chord construction while relying on well-tested underlying functions for the constituent parts.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. This note serves as the root of the dominant sharp ninth chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the dominant sharp ninth chord in the order [root, major third, perfect fifth, minor seventh, augmented second]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (dominant_ninth, intervals.major_second, notes.augment) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a proper dominant sharp ninth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant ninth via dominant_ninth()]
    B --> C[Get major second interval via intervals.major_second()]
    C --> D[Augment the major second via notes.augment()]
    D --> E[Replace 5th element of dominant ninth with augmented second]
    E --> F[Return five-note chord]
```

## Examples
    >>> dominant_sharp_ninth("C")
    ['C', 'E', 'G', 'Bb', 'D#']
    
    >>> dominant_sharp_ninth("A")
    ['A', 'C#', 'E', 'G', 'B#']

## `mingus.core.chords.eleventh` · *function*

## Summary:
Constructs an eleventh chord by returning the root note and its perfect fifth, minor seventh, and perfect fourth intervals.

## Description:
This function generates the basic interval components for an eleventh chord. It takes a musical note as input and returns a list containing the root note and three interval notes that form part of an eleventh chord structure. The function extracts the interval relationships without considering the full chord voicing or inversion patterns.

## Args:
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). Must be a valid note format according to the mingus library conventions.

## Returns:
    list[str]: A list containing four musical notes representing:
        - The original root note
        - The perfect fifth interval above the root
        - The minor seventh interval above the root  
        - The perfect fourth interval above the root

## Raises:
    None explicitly raised by this function, though underlying interval functions may raise NoteFormatError if the input note is malformed.

## Constraints:
    Preconditions:
        - Input note must be a valid note string format recognized by the mingus library
        - Note should follow standard musical note naming conventions (e.g., 'C', 'C#', 'Db', 'Bb')
    
    Postconditions:
        - Returns exactly 4 notes in the specified order
        - All returned notes are valid musical note representations

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note}
    B --> C[Get perfect fifth]
    C --> D[Get minor seventh]
    D --> E[Get perfect fourth]
    E --> F[Return list of 4 notes]
```

## Examples:
    >>> eleventh('C')
    ['C', 'G', 'Bb', 'F']
    
    >>> eleventh('A')
    ['A', 'E', 'G', 'D']

## `mingus.core.chords.minor_eleventh` · *function*

## Summary:
Constructs a minor eleventh chord by combining a minor seventh chord with a perfect fourth interval.

## Description:
Generates a minor eleventh chord by taking a minor seventh chord built on the given root note and appending a perfect fourth interval (equivalent to a major fourth) to form a five-note chord. This function implements the standard musical theory construction of a minor eleventh chord, which consists of a root note, minor third, perfect fifth, minor seventh, and perfect fourth.

## Args:
    note (str): A musical note represented as a string (e.g., "C", "D#", "Bb"). This serves as the root note of the minor eleventh chord.

## Returns:
    list[str]: A list containing exactly five notes forming a minor eleventh chord in the order [root, minor third, perfect fifth, minor seventh, perfect fourth]. All notes are represented as strings in the same format as the input note.

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions if invalid note formats are provided.

## Constraints:
    Preconditions:
    - The input note must be a valid note string format recognized by the mingus library
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned list always contains exactly five notes
    - The notes are arranged in the standard minor eleventh chord pattern (root, minor third, perfect fifth, minor seventh, perfect fourth)
    - All returned notes are in the same format as the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B[Get minor seventh chord]
    B --> C[Get perfect fourth interval]
    C --> D[Combine chords: minor_seventh(note) + [intervals.perfect_fourth(note)]]
    D --> E[Return 5-note chord]
```

## Examples:
    >>> minor_eleventh("C")
    ['C', 'Eb', 'G', 'Bb', 'F']
    
    >>> minor_eleventh("A")
    ['A', 'C', 'E', 'G', 'D']
    
    >>> minor_eleventh("F#")
    ['F#', 'A', 'C#', 'E', 'B']
```

## `mingus.core.chords.minor_thirteenth` · *function*

## Summary:
Constructs a minor thirteenth chord by combining a minor ninth chord with a major sixth interval.

## Description:
Generates a minor thirteenth chord by first creating a minor ninth chord from the given root note, then appending the major sixth interval to form a complete thirteen-note chord. This function implements the standard musical theory construction of a minor thirteenth chord, which consists of a root note, minor third, perfect fifth, minor seventh, major second, and major sixth. The resulting chord is commonly used in jazz and contemporary music.

## Args:
    note (str): A musical note represented as a string (e.g., "C", "D#", "Bb"). This serves as the root note of the minor thirteenth chord.

## Returns:
    list[str]: A list containing exactly six notes forming a minor thirteenth chord in the order [root, minor third, perfect fifth, minor seventh, major second, major sixth]. All notes are represented as strings in the same format as the input note.

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions if invalid note formats are provided.

## Constraints:
    Preconditions:
    - The input note must be a valid note string format recognized by the mingus library
    - The note should follow standard musical notation conventions
    
    Postconditions:
    - The returned list always contains exactly six notes
    - The notes are arranged in the standard minor thirteenth chord pattern (root, minor third, perfect fifth, minor seventh, major second, major sixth)
    - All returned notes are in the same format as the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B[Call minor_ninth(note)]
    B --> C[Get major sixth interval]
    C --> D[Create list with major sixth]
    D --> E[Concatenate minor_ninth result with major sixth list]
    E --> F[Return complete minor thirteenth chord]
```

## Examples:
    >>> minor_thirteenth("C")
    ['C', 'Eb', 'G', 'Bb', 'D', 'A']
    
    >>> minor_thirteenth("A")
    ['A', 'C', 'E', 'G', 'B', 'F#']
    
    >>> minor_thirteenth("F#")
    ['F#', 'A', 'C#', 'E', 'G#', 'D#']
```

## `mingus.core.chords.major_thirteenth` · *function*

## Summary
Constructs a major thirteenth chord by combining a major ninth chord with a major sixth interval above the root note.

## Description
Creates a list containing six musical notes that form a major thirteenth chord: the root note, its major third, perfect fifth, major seventh, major ninth, and major sixth intervals. This function serves as a specialized chord construction utility for generating major thirteenth harmonies in music theory applications.

The function is typically called when building extended harmonic structures or when analyzing complex chord progressions in musical compositions. It leverages the existing `major_ninth` chord construction function and the `intervals.major_sixth` function to maintain consistency with the rest of the music theory framework.

This logic is extracted into its own function rather than being inlined because it provides a clear semantic abstraction for major thirteenth chords, making the code more readable and maintainable while ensuring consistent chord construction patterns throughout the system.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. The note serves as the root of the major thirteenth chord.

## Returns
    list[str]: A list containing exactly six strings representing the notes of the major thirteenth chord in the order [root, major third, perfect fifth, major seventh, major ninth, major sixth]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`major_ninth` and `intervals.major_sixth`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly six elements representing a proper major thirteenth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get major ninth via major_ninth(note)]
    B --> C[Get major sixth via intervals.major_sixth(note)]
    C --> D[Create list with major sixth]
    D --> E[Concatenate major ninth and major sixth]
    E --> F[Return [major_ninth + [major_sixth]]]
```

## Examples
    >>> major_thirteenth("C")
    ['C', 'E', 'G', 'B', 'D', 'A']
    
    >>> major_thirteenth("A")
    ['A', 'C#', 'E', 'G#', 'B', 'F#']

## `mingus.core.chords.dominant_thirteenth` · *function*

## Summary
Constructs a dominant thirteenth chord by extending a dominant ninth chord with a major sixth interval.

## Description
Generates a list of six musical notes representing a dominant thirteenth chord built on the specified root note. This function extends the dominant ninth chord by adding a major sixth interval, creating the characteristic sound of a dominant thirteenth chord commonly used in jazz harmony.

This function is typically called when building complex harmonic progressions, analyzing jazz chords, or constructing extended chord voicings programmatically. It serves as a specialized chord construction utility that leverages existing dominant ninth and interval functions to create sophisticated harmonic structures.

The logic is extracted into its own function rather than being inlined to maintain clean separation of concerns and promote code reuse. It provides a clear semantic meaning for dominant thirteenth chord construction while relying on well-tested underlying functions for the constituent parts.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. This note serves as the root of the dominant thirteenth chord.

## Returns
    list[str]: A list containing exactly six strings representing the notes of the dominant thirteenth chord in the order [root, major third, perfect fifth, minor seventh, major second, major sixth]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (dominant_ninth and intervals.major_sixth) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly six elements representing a proper dominant thirteenth chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant ninth via dominant_ninth()]
    B --> C[Get major sixth via intervals.major_sixth()]
    C --> D[Combine results: dominant_ninth + [major_sixth]]
    D --> E[Return six-note chord]
```

## `mingus.core.chords.suspended_triad` · *function*

## Summary:
Creates a suspended fourth triad by returning a note along with its perfect fourth and perfect fifth intervals.

## Description:
Generates a suspended fourth triad, which is a chord consisting of a root note, its perfect fourth interval, and its perfect fifth interval. This function serves as a simplified interface for creating suspended fourth triads, delegating the actual implementation to the suspended_fourth_triad function. The name "suspended_triad" is somewhat misleading as it specifically implements suspended fourth triads rather than general suspended triads.

## Args:
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). The note should be in a valid format recognized by the mingus library.

## Returns:
    list[str]: A list containing exactly three elements representing the suspended fourth triad:
        - The original note
        - The perfect fourth interval of the note
        - The perfect fifth interval of the note

## Raises:
    None explicitly raised by this function, though underlying interval functions may raise exceptions for invalid note formats.

## Constraints:
    Preconditions:
        - The input note must be a valid note string format supported by the mingus library
        - The note should be in a format compatible with the intervals module's processing functions
    
    Postconditions:
        - The returned list always contains exactly three elements
        - The first element is identical to the input note
        - The second element is the perfect fourth of the input note
        - The third element is the perfect fifth of the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B[Call suspended_fourth_triad]
    B --> C[Return triad result]
```

## Examples:
    >>> suspended_triad('C')
    ['C', 'F', 'G']
    
    >>> suspended_triad('A')
    ['A', 'D', 'E']

## `mingus.core.chords.suspended_second_triad` · *function*

## Summary:
Returns a suspended second triad chord built from the specified note.

## Description:
Creates a musical triad consisting of the root note, major second interval, and perfect fifth interval. This chord type is commonly used in music theory and composition, particularly in jazz and popular music contexts where the second interval is "suspended" (held as a tension before resolution).

This function extracts the chord construction logic into a reusable component to avoid duplication when creating suspended second triads in various musical contexts.

## Args:
    note (str): A valid musical note string (e.g., 'C', 'D#', 'Bb') representing the root of the triad

## Returns:
    list[str]: A list containing three note strings forming the suspended second triad [root, major_second, perfect_fifth]

## Raises:
    NoteFormatError: When the input note string is not in a recognized musical note format

## Constraints:
    Preconditions:
        - The input note must be a valid musical note string that can be processed by the notes module
        - The note must conform to standard musical notation conventions
    
    Postconditions:
        - The returned list always contains exactly three note strings
        - All returned notes are in the same octave as the input note
        - The intervals between consecutive notes follow the suspended second triad pattern

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note format}
    B -- Valid --> C[Get major second]
    B -- Invalid --> D[Raise NoteFormatError]
    C --> E[Get perfect fifth]
    E --> F[Return [note, major_second, perfect_fifth]]
    D --> G[Exit]
```

## Examples:
    >>> suspended_second_triad('C')
    ['C', 'D', 'G']
    
    >>> suspended_second_triad('A#')
    ['A#', 'B#', 'E#']
```

## `mingus.core.chords.suspended_fourth_triad` · *function*

## Summary:
Creates a suspended fourth triad by returning a note along with its perfect fourth and perfect fifth intervals.

## Description:
Generates a suspended fourth triad, which is a chord consisting of a root note, its perfect fourth interval, and its perfect fifth interval. This function extracts the core logic of creating such a triad into a reusable component to avoid code duplication when generating suspended fourth chords.

## Args:
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). The note should be in a valid format recognized by the mingus library.

## Returns:
    list[str]: A list containing exactly three elements representing the suspended fourth triad:
        - The original note
        - The perfect fourth interval of the note
        - The perfect fifth interval of the note

## Raises:
    None explicitly raised by this function, though underlying interval functions may raise exceptions for invalid note formats.

## Constraints:
    Preconditions:
        - The input note must be a valid note string format supported by the mingus library
        - The note should be in a format compatible with the intervals module's processing functions
    
    Postconditions:
        - The returned list always contains exactly three elements
        - The first element is identical to the input note
        - The second element is the perfect fourth of the input note
        - The third element is the perfect fifth of the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note}
    B --> C[Get perfect fourth]
    C --> D[Get perfect fifth]
    D --> E[Return [note, fourth, fifth]]
```

## Examples:
    >>> suspended_fourth_triad('C')
    ['C', 'F', 'G']
    
    >>> suspended_fourth_triad('A')
    ['A', 'D', 'E']
```

## `mingus.core.chords.suspended_seventh` · *function*

## Summary:
Creates a suspended seventh chord by combining a suspended fourth triad with a minor seventh interval.

## Description:
Generates a suspended seventh chord, which consists of a root note, its perfect fourth interval, its perfect fifth interval, and a minor seventh interval above the root. This function extracts the logic for creating suspended seventh chords into a reusable component to avoid code duplication when generating various suspended seventh chord variations.

## Args:
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). The note should be in a valid format recognized by the mingus library.

## Returns:
    list[str]: A list containing exactly four elements representing the suspended seventh chord:
        - The original note (root)
        - The perfect fourth interval of the note
        - The perfect fifth interval of the note
        - The minor seventh interval of the note

## Raises:
    None explicitly raised by this function, though underlying functions (suspended_fourth_triad and intervals.minor_seventh) may raise exceptions for invalid note formats.

## Constraints:
    Preconditions:
        - The input note must be a valid note string format supported by the mingus library
        - The note should be in a format compatible with the intervals module's processing functions
    
    Postconditions:
        - The returned list always contains exactly four elements
        - The first element is identical to the input note
        - The second element is the perfect fourth of the input note
        - The third element is the perfect fifth of the input note
        - The fourth element is the minor seventh of the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note}
    B --> C[Get suspended fourth triad]
    C --> D[Get minor seventh]
    D --> E[Concatenate triad and seventh]
    E --> F[Return [triad + [seventh]]]
```

## Examples:
    >>> suspended_seventh('C')
    ['C', 'F', 'G', 'Bb']
    
    >>> suspended_seventh('A')
    ['A', 'D', 'E', 'G']

## `mingus.core.chords.suspended_fourth_ninth` · *function*

## Summary:
Creates a suspended fourth ninth chord by combining a suspended fourth triad with a minor second interval.

## Description:
Generates a suspended fourth ninth chord, which extends the suspended fourth triad (root, perfect fourth, perfect fifth) by adding a minor second interval. This function encapsulates the logic for creating this specific chord type to promote code reuse and maintainability.

## Args:
    note (str): A musical note represented as a string (e.g., 'C', 'D#', 'Bb'). The note should be in a valid format recognized by the mingus library.

## Returns:
    list[str]: A list containing exactly four elements representing the suspended fourth ninth chord:
        - The original note (root)
        - The perfect fourth interval of the note
        - The perfect fifth interval of the note
        - The minor second interval of the note

## Raises:
    KeyError: When the input note is not a valid note format recognized by the mingus library. This exception may be raised by underlying interval calculation functions and propagated to the caller.

## Constraints:
    Preconditions:
        - The input note must be a valid note string format supported by the mingus library
        - The note should be in a format compatible with the intervals module's processing functions
    
    Postconditions:
        - The returned list always contains exactly four elements
        - The first three elements form a suspended fourth triad
        - The fourth element is the minor second of the input note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input note] --> B{Validate note}
    B --> C[Get suspended fourth triad]
    C --> D[Get minor second]
    D --> E[Combine triad and minor second]
    E --> F[Return chord]
```

## Examples:
    >>> suspended_fourth_ninth('C')
    ['C', 'F', 'G', 'D']

    >>> suspended_fourth_ninth('A')
    ['A', 'D', 'E', 'B']
```

## `mingus.core.chords.augmented_major_seventh` · *function*

## Summary:
Creates an augmented major seventh chord from a given note by combining an augmented triad with a major seventh interval.

## Description:
This function generates an augmented major seventh chord, which is a four-note chord consisting of a root note, a major third interval above it, an augmented fifth interval above it, and a major seventh interval above the root. The function leverages existing chord construction utilities to build the chord properly.

The function is extracted into its own component to encapsulate the logic for creating augmented major seventh chords, separating this specific musical chord construction from other chord-related operations and making the intent clear and reusable. This modularization allows for consistent creation of augmented major seventh chords throughout the library.

## Args:
    note (str): A note string representing the root of the augmented major seventh chord (e.g., "C", "D#", "Bb"). Must be a valid note format recognized by the mingus library.

## Returns:
    list[str]: A list containing four note strings forming the augmented major seventh chord [root, major third, augmented fifth, major seventh]. The returned list always contains exactly four elements.

## Raises:
    FormatError: If the input note is not in a valid format recognized by the mingus library
    NoteFormatError: If the input note cannot be processed by underlying note manipulation functions

## Constraints:
    Preconditions:
        - The input note must be a valid note string format recognized by the mingus library
        - The note should follow standard musical note naming conventions (e.g., "C", "C#", "Cb", "D", etc.)
    
    Postconditions:
        - The returned list always contains exactly four note strings
        - The second element is always a major third above the root note
        - The third element is always an augmented fifth above the root note
        - The fourth element is always a major seventh above the root note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start: augmented_major_seventh(note)] --> B[Get augmented triad of note]
    B --> C[Get major seventh of note]
    C --> D[Combine triad and seventh]
    D --> E[Return [augmented_triad_result, major_seventh_note]]
```

## Examples:
    >>> augmented_major_seventh("C")
    ['C', 'E', 'G#', 'B']
    
    >>> augmented_major_seventh("A")
    ['A', 'C#', 'F#', 'E']

## `mingus.core.chords.augmented_minor_seventh` · *function*

## Summary:
Creates an augmented minor seventh chord by combining an augmented triad with a minor seventh interval.

## Description:
Generates a four-note chord consisting of a root note, major third, augmented fifth, and minor seventh interval. This function combines the augmented triad construction with a minor seventh interval to create a specific chord voicing commonly used in jazz and classical music theory.

The function is extracted into its own component to encapsulate the logic for creating augmented minor seventh chords, separating this specific musical chord construction from other chord-related operations and making the intent clear and reusable. This modularization allows for consistent creation of augmented minor seventh chords throughout the library.

## Args:
    note (str): A note string representing the root of the augmented minor seventh chord (e.g., "C", "D#", "Bb"). Must be a valid note format recognized by the mingus library.

## Returns:
    list[str]: A list containing four note strings forming the augmented minor seventh chord [root, major third, augmented fifth, minor seventh]. The returned list always contains exactly four elements.

## Raises:
    FormatError: If the input note is not in a valid format recognized by the mingus library
    NoteFormatError: If the input note cannot be processed by underlying note manipulation functions

## Constraints:
    Preconditions:
        - The input note must be a valid note string format recognized by the mingus library
        - The note should follow standard musical note naming conventions (e.g., "C", "C#", "Cb", "D", etc.)
    
    Postconditions:
        - The returned list always contains exactly four note strings
        - The second element is always a major third above the root note
        - The third element is always an augmented fifth above the root note
        - The fourth element is always a minor seventh above the root note

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start: augmented_minor_seventh(note)] --> B[Get augmented_triad(note)]
    B --> C[Get minor_seventh(note)]
    C --> D[Combine results: augmented_triad + [minor_seventh]]
    D --> E[Return combined chord]
```

## Examples:
    >>> augmented_minor_seventh("C")
    ['C', 'E', 'G#', 'Bb']
    
    >>> augmented_minor_seventh("A")
    ['A', 'C#', 'F#', 'Eb']

## `mingus.core.chords.dominant_flat_five` · *function*

## Summary
Creates a dominant flat five chord by taking a dominant seventh chord and flattening its fifth degree.

## Description
Constructs a dominant flat five chord (also known as a half-diminished seventh chord or m7♭5) by starting with a dominant seventh chord and flattening the fifth degree. This produces a chord with the interval pattern: root, major third, diminished fifth, minor seventh.

This function is typically used in jazz harmony and classical music theory applications where diminished fifth intervals are needed. The extraction of this logic into a separate function allows for clean composition of complex chord structures while maintaining the modular nature of chord construction utilities.

## Args
    note (str): A musical note represented as a string that serves as the root of the chord. Must be a valid musical note compatible with the intervals and notes modules.

## Returns
    list[str]: A list of four strings representing the notes of the dominant flat five chord in the order [root, major third, diminished fifth, minor seventh]. The exact note names depend on the input note and the interval calculations performed by the intervals and notes modules.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (dominant_seventh and notes.diminish) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals and notes modules.
    Postcondition: The returned list always contains exactly four elements representing a proper dominant flat five chord structure where the third note is flattened by one semitone.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant seventh chord via dominant_seventh()]
    B --> C[Flatten the fifth degree via notes.diminish()]
    C --> D[Return modified four-note chord]
```

## Examples
    >>> dominant_flat_five("C")
    ['C', 'E', 'Gb', 'Bb']
    
    >>> dominant_flat_five("A")
    ['A', 'C#', 'Eb', 'G']

## `mingus.core.chords.lydian_dominant_seventh` · *function*

## Summary
Constructs a lydian dominant seventh chord by combining a dominant seventh chord with an augmented fourth interval.

## Description
Generates a five-note chord that extends the standard dominant seventh chord by adding an augmented fourth interval. This creates a distinctive harmonic sound often found in jazz and contemporary music theory. The function builds upon the established dominant seventh chord construction and modifies it by raising the fourth degree of the scale by a semitone, creating what is sometimes called a "lydian dominant" sound.

This function is typically called when constructing advanced harmonic progressions, analyzing jazz chords, or creating extended chord voicings. It serves as a specialized chord construction utility that extends the basic dominant seventh structure with an augmented fourth interval, producing a tension-filled harmony with a unique color.

## Args
    note (str): A musical note represented as a string that is compatible with the intervals module's processing functions. This note serves as the root of the lydian dominant seventh chord.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the lydian dominant seventh chord in the order [root, major third, perfect fifth, minor seventh, augmented fourth]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (dominant_seventh, intervals.perfect_fourth, notes.augment) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a proper lydian dominant seventh chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant seventh via dominant_seventh()]
    B --> C[Get perfect fourth via intervals.perfect_fourth()]
    C --> D[Augment the perfect fourth via notes.augment()]
    D --> E[Combine results: dominant_seventh + [augmented_fourth]]
    E --> F[Return five-note chord]
```

## Examples
    >>> lydian_dominant_seventh("C")
    ['C', 'E', 'G', 'Bb', 'F#']
    
    >>> lydian_dominant_seventh("A")
    ['A', 'C#', 'E', 'G', 'D#']

## `mingus.core.chords.hendrix_chord` · *function*

## Summary
Constructs a Hendrix-style extended chord by adding a minor third to a dominant seventh chord.

## Description
Generates a five-note musical chord that extends the standard dominant seventh chord with an additional minor third interval. This creates a distinctive harmonic texture commonly associated with jazz and rock music, particularly in the style of Jimi Hendrix's guitar arrangements.

The function is designed to create extended chord voicings that go beyond basic triads and seventh chords, enabling composers and musicians to explore more complex harmonic possibilities. It serves as a specialized utility for building sophisticated chord progressions and harmonic structures in musical composition.

## Args
    note (str): A musical note represented as a string that serves as the root of the chord. This note must be compatible with the intervals module's processing functions.

## Returns
    list[str]: A list containing exactly five strings representing the notes of the Hendrix chord in the order [root, major third, perfect fifth, minor seventh, minor third]. The exact note names depend on the input note and the interval calculations performed by the intervals module.

## Raises
    This function itself does not explicitly raise exceptions, but may propagate exceptions from underlying functions (`dominant_seventh` and `intervals.minor_third`) if the note parameter is malformed or unsupported.

## Constraints
    Precondition: The input note must be a valid musical note string that can be processed by the intervals module functions.
    Postcondition: The returned list always contains exactly five elements representing a properly constructed Hendrix-style chord structure.

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Input note] --> B[Get dominant seventh via dominant_seventh()]
    B --> C[Get minor third via intervals.minor_third()]
    C --> D[Combine results: dominant_seventh + [minor_third]]
    D --> E[Return five-note Hendrix chord]
```

## Examples
    >>> hendrix_chord("C")
    ['C', 'E', 'G', 'Bb', 'Eb']
    
    >>> hendrix_chord("A")
    ['A', 'C#', 'E', 'G', 'C']

## `mingus.core.chords.tonic` · *function*

## Summary:
Returns the tonic triad for a given musical key, which represents the first triad in the diatonic chord progression of that key.

## Description:
This function extracts the tonic triad from the complete set of diatonic triads for a specified musical key. The tonic triad consists of the root note, third, and fifth notes of the key's scale, forming the foundational harmony of that key. This function serves as a convenient accessor for the most fundamental chord in any musical key.

The `tonic` function is typically called when working with harmonic analysis or chord progressions, where the first chord of a key's diatonic set needs to be quickly accessed. It's commonly used in music theory applications and chord progression generators.

## Args:
    key (str): The musical key for which to retrieve the tonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the tonic triad: [root note, third interval, fifth interval]. The returned triad represents the first chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the root note of the key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[tonic(key)] --> B[Call triads(key)]
    B --> C[Get first triad from list (index 0)]
    C --> D[Return tonic triad]
```

## Examples:
    >>> tonic('C')
    ['C', 'E', 'G']
    >>> tonic('G')
    ['G', 'B', 'D']
    >>> tonic('A')
    ['A', 'C#', 'E']

## `mingus.core.chords.tonic7` · *function*

## Summary:
Returns the tonic seventh chord for a given musical key.

## Description:
Extracts the first seventh chord from the complete set of seventh chords generated for the specified musical key. This function serves as a convenient accessor for the tonic seventh chord, which is the seventh chord built on the first degree (tonic) of the key's diatonic scale.

The function relies on the `sevenths()` function to compute all seventh chords for the given key, then returns only the first chord (the tonic seventh) from that collection. This approach separates the concerns of chord generation and chord selection, making the code more modular and reusable.

## Args:
    key (str): The musical key for which to retrieve the tonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing four note strings representing the tonic seventh chord: [root note, third interval, fifth interval, seventh interval]. The chord is built on the tonic note of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly four note strings.
        - All returned notes are valid within the context of the specified key.
        - The chord represents the seventh chord built on the tonic note of the key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.
    - Accesses and potentially modifies the global `_sevenths_cache` dictionary through the `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[tonic7(key)] --> B[Call sevenths(key)]
    B --> C[Get first element of result (index 0)]
    C --> D[Return tonic seventh chord]
```

## Examples:
    >>> tonic7('C')
    ['C', 'E', 'G', 'B']
    >>> tonic7('G')
    ['G', 'B', 'D', 'F#']

## `mingus.core.chords.supertonic` · *function*

## Summary:
Returns the supertonic triad for a given musical key, which represents the second triad in the diatonic chord progression of that key.

## Description:
This function extracts the supertonic triad from the complete set of diatonic triads for a specified musical key. The supertonic triad consists of the second note of the key's scale, along with its third and fifth intervals, forming the second most important chord in the diatonic set of that key. This function serves as a convenient accessor for the supertonic chord, which is commonly used in harmonic analysis and chord progression generators.

The function is part of a family of chord accessors including `tonic()` and `dominant()`, all of which extract specific triads from the complete diatonic set using index-based access.

## Args:
    key (str): The musical key for which to retrieve the supertonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the supertonic triad: [root note, third interval, fifth interval]. The returned triad represents the second chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the second note of the key's scale.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[supertonic(key)] --> B[Call triads(key)]
    B --> C[Get second triad from list (index 1)]
    C --> D[Return supertonic triad]
```

## Examples:
    >>> supertonic('C')
    ['D', 'F#', 'A']
    >>> supertonic('G')
    ['A', 'C#', 'E']
    >>> supertonic('A')
    ['B', 'D#', 'F#']

## `mingus.core.chords.supertonic7` · *function*

## Summary:
Returns the supertonic seventh chord for a given musical key.

## Description:
Extracts the supertonic seventh chord from the complete set of seventh chords generated for the specified musical key. The supertonic seventh chord is built on the second degree of the diatonic scale and consists of four notes forming a seventh chord. This function provides convenient access to the ii chord in seventh form within any musical key.

## Args:
    key (str): The musical key for which to retrieve the supertonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the supertonic seventh chord in the specified key. The chord contains the root note, third, fifth, and seventh intervals built on the second degree of the key's scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the second degree (supertonic) of the diatonic scale for the given key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[supertonic7(key)] --> B[Call sevenths(key)]
    B --> C[Return sevenths(key)[1]]
```

## Examples:
    >>> supertonic7('C')
    ['D', 'F', 'A', 'C']
    >>> supertonic7('G')
    ['A', 'C', 'E', 'G']
    >>> # In the key of C major, the supertonic seventh chord is Dm7 (D-F-A-C)

## `mingus.core.chords.mediant` · *function*

## Summary:
Returns the mediant chord from the triads of a given musical key.

## Description:
Extracts the third triad from the complete set of triads generated for a musical key. In music theory, the mediant is the third degree of a scale, and this function provides access to the corresponding triad built on that degree.

## Args:
    key (str): The musical key for which to extract the mediant chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the mediant triad [root, third, fifth]. Returns an empty list if the key has no triads (should not occur with valid keys).

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function, which is propagated from the underlying triads() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The triad represents the mediant (third degree) of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary by calling `triads()` which implements caching.
    - May modify the global `_key_cache` dictionary indirectly through calls to `keys.get_notes()` via the `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[mediant(key)] --> B[Call triads(key)]
    B --> C[Get triads list for key]
    C --> D[Return triads[key][2]]
```

## Examples:
    >>> mediant('C')
    ['E', 'G', 'B']
    >>> mediant('G')
    ['B', 'D', 'F#']

## `mingus.core.chords.mediant7` · *function*

## Summary:
Returns the mediant seventh chord for a given musical key by extracting the third seventh chord from the complete diatonic seventh chord progression.

## Description:
This function computes the mediant seventh chord for a specified musical key. The mediant seventh chord is the seventh chord built on the third degree of the diatonic scale of the given key. It leverages the `sevenths()` function to generate all seventh chords for the key and extracts the third one (at index 2) from the resulting list.

The function is designed to provide quick access to the mediant seventh chord without requiring the caller to compute the full diatonic progression. This abstraction allows for cleaner code when only the mediant seventh chord is needed.

## Args:
    key (str): The musical key for which to retrieve the mediant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the mediant seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the third degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a valid seventh chord.
        - The chord is built on the third degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.
    - Accesses and potentially modifies the global `_sevenths_cache` dictionary through the `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[mediant7(key)] --> B[Call sevenths(key)]
    B --> C[Extract element at index 2]
    C --> D[Return mediant seventh chord]
```

## Examples:
    >>> mediant7('C')
    ['E', 'G', 'B', 'D']
    >>> mediant7('G')
    ['B', 'D', 'F#', 'A']

## `mingus.core.chords.subdominant` · *function*

## Summary:
Returns the subdominant triad for a given musical key, which represents the fourth triad in the diatonic chord progression of that key.

## Description:
This function extracts the subdominant triad from the complete set of diatonic triads for a specified musical key. The subdominant triad consists of the fourth note of the key's scale, along with its third and fifth intervals, forming the fourth most important chord in the diatonic set of that key. This function serves as a convenient accessor for the subdominant chord, which is commonly used in harmonic analysis and chord progression generators.

The `subdominant` function is part of a family of chord accessors including `tonic()`, `dominant()`, and others, all of which extract specific triads from the complete diatonic set using index-based access. It specifically retrieves the fourth triad (index 3) from the list returned by the `triads()` function.

## Args:
    key (str): The musical key for which to retrieve the subdominant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the subdominant triad: [root note, third interval, fifth interval]. The returned triad represents the fourth chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function, which is propagated from the underlying triads() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the fourth note of the key's scale.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[subdominant(key)] --> B[Call triads(key)]
    B --> C[Get fourth triad from list (index 3)]
    C --> D[Return subdominant triad]
```

## Examples:
    >>> subdominant('C')
    ['F', 'A', 'C']
    >>> subdominant('G')
    ['C', 'E', 'G']
    >>> subdominant('A')
    ['D', 'F#', 'A']

## `mingus.core.chords.subdominant7` · *function*

## Summary:
Returns the subdominant seventh chord for a given musical key.

## Description:
Computes and returns the seventh chord built on the fourth degree (subdominant) of the diatonic scale for the specified musical key. This function leverages the `sevenths()` function to generate all seventh chords for the key and extracts the fourth chord from the resulting list.

## Args:
    key (str): The musical key for which to generate the subdominant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the subdominant seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the fourth degree of the key's scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the fourth degree of the diatonic scale for the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[subdominant7(key)] --> B[Call sevenths(key)]
    B --> C[Extract element at index 3]
    C --> D[Return subdominant seventh chord]
```

## Examples:
    >>> subdominant7('C')
    ['F', 'A', 'C', 'E']
    >>> subdominant7('G')
    ['C', 'E', 'G', 'B']

## `mingus.core.chords.dominant` · *function*

## Summary:
Returns the dominant triad for a given musical key.

## Description:
Extracts the dominant triad (the fifth degree of the scale) from all triads generated for the specified musical key. This function provides a convenient way to access the dominant chord without manually indexing into the full triad list.

## Args:
    key (str): The musical key for which to retrieve the dominant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the dominant triad [root, third, fifth]. Returns the triad corresponding to the fifth degree of the scale in the given key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The root note of the returned triad is the fifth degree of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[dominant(key)] --> B[Call triads(key)]
    B --> C[Return triads(key)[4]]
```

## Examples:
    >>> dominant('C')
    ['G', 'B', 'D']
    >>> dominant('G')
    ['D', 'F#', 'A']
    >>> dominant('A')
    ['E', 'G#', 'B']

## `mingus.core.chords.dominant7` · *function*

## Summary:
Returns the dominant seventh chord for a given musical key, which is the seventh chord built on the fifth degree of the diatonic scale.

## Description:
Extracts the dominant seventh chord (V7 in Roman numeral analysis) from all seventh chords available in the specified musical key. This function serves as a convenient accessor for the dominant seventh chord specifically, avoiding the need to compute all seventh chords when only the dominant seventh is required. The dominant seventh chord is formed by taking the fifth degree of the diatonic scale and building a seventh chord on that note.

## Args:
    key (str): The musical key for which to generate the dominant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the dominant seventh chord in the specified key. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing the dominant seventh chord.
        - The chord is built on the fifth degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying sevenths() function.

## Control Flow:
```mermaid
flowchart TD
    A[dominant7(key)] --> B[Call sevenths(key)]
    B --> C[Return sevenths(key)[4]]
```

## Examples:
    >>> dominant7('C')
    ['G', 'B', 'D', 'F']
    >>> dominant7('G')
    ['D', 'F#', 'A', 'C']

## `mingus.core.chords.submediant` · *function*

## Summary:
Returns the submediant triad for a given musical key by extracting the sixth triad from the complete set of triads in that key.

## Description:
This function retrieves the submediant triad from a musical key by accessing the sixth triad (at index 5) from the list of all triads generated for that key. The submediant represents the 6th degree of the diatonic scale and is commonly used in harmonic analysis and chord progressions. This function serves as a convenience wrapper around the triads() function to specifically extract the submediant chord, separating the concern of retrieving a specific scale degree triad from the general triad generation logic.

## Args:
    key (str): The musical key for which to retrieve the submediant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the submediant triad [root, third, fifth] for the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
        - The key must contain at least 6 notes to have a submediant triad.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The triad returned represents the 6th degree of the diatonic scale for the given key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary through calls to `triads()` function.
    - May modify the global `_key_cache` dictionary indirectly through calls to `keys.get_notes()`.

## Control Flow:
```mermaid
flowchart TD
    A[submediant(key)] --> B[Call triads(key)]
    B --> C{triads(key) has at least 6 elements?}
    C -- Yes --> D[Access triads[key][5]]
    D --> E[Return submediant triad]
    C -- No --> F[Raises exception]
```

## Examples:
    >>> submediant('C')
    ['A', 'C', 'E']
    >>> submediant('G')
    ['E', 'G', 'B']

## `mingus.core.chords.submediant7` · *function*

## Summary:
Returns the submediant seventh chord for a given musical key.

## Description:
Extracts the submediant seventh chord (the seventh chord built on the 6th degree of the diatonic scale) from all seventh chords available in the specified musical key. This function serves as a convenience wrapper to quickly access the submediant seventh chord without manually indexing into the full seventh chord progression.

## Args:
    key (str): The musical key for which to retrieve the submediant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the submediant seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the 6th degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the 6th degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[submediant7(key)] --> B[Call sevenths(key)]
    B --> C[Return sevenths(key)[5]]
```

## Examples:
    >>> submediant7('C')
    ['A', 'C', 'E', 'G']
    >>> submediant7('G')
    ['E', 'G', 'B', 'D']
```

## `mingus.core.chords.subtonic` · *function*

## Summary:
Returns the subtonic chord from the triads of a given musical key.

## Description:
This function retrieves the subtonic chord (the seventh degree of the diatonic scale) from the set of triads built for the specified musical key. The subtonic chord is formed by taking the seventh note of the key's scale and building a triad on that note.

## Args:
    key (str): The musical key for which to retrieve the subtonic chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the subtonic triad in the format [root, third, fifth].

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
        - The key must contain at least 7 notes to have a subtonic chord.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad.
        - The triad represents the seventh degree of the key's diatonic scale.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[subtonic(key)] --> B[Call triads(key)]
    B --> C{triads(key) returns list of 7+ triads}
    C -->|Yes| D[Access element at index 6]
    D --> E[Return subtonic triad]
    C -->|No| F[Raises exception via triads()]
```

## Examples:
    >>> subtonic('C')
    ['B', 'D', 'F#']
    >>> subtonic('G')
    ['F#', 'A#', 'C#']

## `mingus.core.chords.subtonic7` · *function*

## Summary:
Returns the subtonic seventh chord for a given musical key.

## Description:
Extracts the seventh chord built on the subtonic (7th degree) of the diatonic scale for the specified musical key. This function provides convenient access to the subtonic seventh chord without requiring manual indexing of the full seventh chord progression.

## Args:
    key (str): The musical key for which to retrieve the subtonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the subtonic seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the subtonic degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the subtonic (7th degree) of the specified key's diatonic scale.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[subtonic7(key)] --> B[Call sevenths(key)]
    B --> C[Return sevenths(key)[6]]
```

## Examples:
    >>> subtonic7('C')
    ['B', 'D', 'F', 'A']
    >>> subtonic7('G')
    ['F#', 'A', 'C', 'E']

## `mingus.core.chords.I` · *function*

## Summary:
Returns the tonic triad for a given musical key, serving as a shorthand alias for the tonic function.

## Description:
This function provides a convenient alias for retrieving the tonic triad of a musical key. In music theory, the Roman numeral "I" represents the first degree of a scale, which corresponds to the tonic chord - the foundational harmony of any key. This function serves as a more concise way to access the same functionality as the `tonic` function.

The `I` function is typically called when working with harmonic analysis or chord progressions where quick access to the tonic triad is needed. It's commonly used in music theory applications and chord progression generators as a shorthand notation.

## Args:
    key (str): The musical key for which to retrieve the tonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the tonic triad: [root note, third interval, fifth interval]. The returned triad represents the first chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the root note of the key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[I(key)] --> B[Call tonic(key)]
    B --> C[Return tonic triad]
```

## Examples:
    >>> I('C')
    ['C', 'E', 'G']
    >>> I('G')
    ['G', 'B', 'D']
    >>> I('A')
    ['A', 'C#', 'E']

## `mingus.core.chords.I7` · *function*

## Summary:
Returns the tonic seventh chord for a given musical key, serving as a convenient alias for the tonic seventh chord function.

## Description:
This function provides a shorthand way to retrieve the tonic seventh chord (the seventh chord built on the first degree of a key's diatonic scale) for a specified musical key. It acts as an alias for the `tonic7` function, offering a more concise interface for accessing the tonic seventh chord.

The function is particularly useful in contexts where Roman numeral analysis notation is employed, where "I7" represents the dominant seventh chord in the key. It leverages the existing `tonic7` implementation to ensure consistency and maintainability.

## Args:
    key (str): The musical key for which to retrieve the tonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing four note strings representing the tonic seventh chord: [root note, third interval, fifth interval, seventh interval]. The chord is built on the tonic note of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly four note strings.
        - All returned notes are valid within the context of the specified key.
        - The chord represents the seventh chord built on the tonic note of the key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.
    - Accesses and potentially modifies the global `_sevenths_cache` dictionary through the `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[I7(key)] --> B[Call tonic7(key)]
    B --> C[Return result]
```

## Examples:
    >>> I7('C')
    ['C', 'E', 'G', 'B']
    >>> I7('G')
    ['G', 'B', 'D', 'F#']

## `mingus.core.chords.ii` · *function*

## Summary:
Returns the supertonic triad (second degree chord) for a given musical key.

## Description:
This function provides a convenient accessor for the supertonic triad, which represents the second chord in the diatonic set of a musical key. In music theory, the supertonic chord is denoted by the Roman numeral "ii" and consists of the second note of the key's scale along with its third and fifth intervals.

The function serves as a shorthand alternative to calling `supertonic(key)` directly, making it easier to work with chord progressions and harmonic analysis where Roman numeral notation is commonly used.

## Args:
    key (str): The musical key for which to retrieve the supertonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the supertonic triad: [root note, third interval, fifth interval]. The returned triad represents the second chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the second note of the key's scale.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[ii(key)] --> B[Call supertonic(key)]
    B --> C[Return supertonic triad]
```

## Examples:
    >>> ii('C')
    ['D', 'F#', 'A']
    >>> ii('G')
    ['A', 'C#', 'E']
    >>> ii('A')
    ['B', 'D#', 'F#']

## `mingus.core.chords.II` · *function*

## Summary:
Returns the supertonic triad for a given musical key, representing the second chord in the diatonic chord progression of that key.

## Description:
This function serves as an alias for the `supertonic()` function, providing access to the second triad in the diatonic set of a specified musical key. In Roman numeral notation, the supertonic chord is denoted as "II" and consists of the second note of the key's scale, along with its third and fifth intervals.

The function is part of a family of chord accessors that use Roman numeral notation to reference specific positions in the diatonic chord progression. This naming convention is widely used in music theory and harmonic analysis.

## Args:
    key (str): The musical key for which to retrieve the supertonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the supertonic triad: [root note, third interval, fifth interval]. The returned triad represents the second chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the second note of the key's scale.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[II(key)] --> B[Call supertonic(key)]
    B --> C[Return supertonic triad]
```

## Examples:
    >>> II('C')
    ['D', 'F#', 'A']
    >>> II('G')
    ['A', 'C#', 'E']
    >>> II('A')
    ['B', 'D#', 'F#']

## `mingus.core.chords.ii7` · *function*

## Summary:
Returns the supertonic seventh chord for a given musical key.

## Description:
Provides access to the ii seventh chord (supertonic seventh chord) in any musical key. This function serves as an alias for the supertonic7 function, offering a more intuitive naming convention for users familiar with Roman numeral notation where ii represents the supertonic chord.

## Args:
    key (str): The musical key for which to retrieve the supertonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the supertonic seventh chord in the specified key. The chord contains the root note, third, fifth, and seventh intervals built on the second degree of the key's scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the second degree (supertonic) of the diatonic scale for the given key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[ii7(key)] --> B[Call supertonic7(key)]
    B --> C[Return result]
```

## Examples:
    >>> ii7('C')
    ['D', 'F', 'A', 'C']
    >>> ii7('G')
    ['A', 'C', 'E', 'G']
    >>> # In the key of C major, the ii7 chord is Dm7 (D-F-A-C)

## `mingus.core.chords.II7` · *function*

## Summary:
Returns the supertonic seventh chord for a given musical key.

## Description:
Returns the supertonic seventh chord (also known as the ii7 chord) for the specified musical key. This function serves as an alias for the supertonic7 function, providing a more conventional Roman numeral notation for accessing the second-degree seventh chord in any musical key.

## Args:
    key (str): The musical key for which to retrieve the supertonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the supertonic seventh chord in the specified key. The chord contains the root note, third, fifth, and seventh intervals built on the second degree of the key's scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the second degree (supertonic) of the diatonic scale for the given key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[II7(key)] --> B[Call supertonic7(key)]
    B --> C[Return result]
```

## Examples:
    >>> II7('C')
    ['D', 'F', 'A', 'C']
    >>> II7('G')
    ['A', 'C', 'E', 'G']
    >>> # In the key of C major, the II7 chord is Dm7 (D-F-A-C)

## `mingus.core.chords.iii` · *function*

## Summary:
Returns the mediant chord (third degree triad) from the triads of a given musical key.

## Description:
Provides access to the mediant triad built on the third degree of a musical scale. This function serves as an alias for the `mediant` function, offering a more concise way to access the third triad of a key. The mediant is the third degree of a scale and forms the foundation for many harmonic progressions.

## Args:
    key (str): The musical key for which to extract the mediant chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the mediant triad [root, third, fifth]. Returns an empty list if the key has no triads (should not occur with valid keys).

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function, which is propagated from the underlying triads() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The triad represents the mediant (third degree) of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary by calling `triads()` which implements caching.
    - May modify the global `_key_cache` dictionary indirectly through calls to `keys.get_notes()` via the `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[iii(key)] --> B[Call mediant(key)]
    B --> C[Return mediant result]
```

## Examples:
    >>> iii('C')
    ['E', 'G', 'B']
    >>> iii('G')
    ['B', 'D', 'F#']

## `mingus.core.chords.III` · *function*

## Summary:
Returns the mediant degree (third scale degree) of a musical key.

## Description:
This function serves as a convenience accessor for the mediant degree of a musical key. The mediant represents the third degree of a scale and is commonly used in chord construction and harmonic analysis. This function delegates the computation to an underlying `mediant` function that performs the actual calculation.

## Args:
    key (str or Note): The musical key for which to calculate the mediant degree. This parameter is passed directly to the underlying implementation.

## Returns:
    Note: The mediant degree of the specified key, typically represented as a Note object.

## Raises:
    NoteFormatError: If the provided key is not a valid note representation that can be processed by the underlying implementation.

## Constraints:
    Preconditions: The input key must be a valid musical note representation.
    Postconditions: The returned value represents the third scale degree of the input key.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[III(key)] --> B[mediant(key)]
    B --> C[Return result]
```

## `mingus.core.chords.iii7` · *function*

## Summary:
Returns the mediant seventh chord for a given musical key by delegating to the mediant7 function.

## Description:
This function serves as a wrapper that delegates to the mediant7 function to compute the mediant seventh chord (iii7) for the specified musical key. The mediant seventh chord is built on the third degree of a musical scale and typically contains a seventh interval above the root.

## Args:
    key (str or int): The musical key for which to generate the mediant seventh chord. This parameter is passed directly to the underlying mediant7 implementation.

## Returns:
    The result produced by calling mediant7(key). The exact format depends on the implementation of mediant7.

## Raises:
    None explicitly documented in the source code.

## Constraints:
    Preconditions: The input key must be a valid musical key representation acceptable to the mediant7 function.
    Postconditions: The function returns whatever value mediant7(key) produces.

## Side Effects:
    None explicitly documented in the source code.

## Control Flow:
```mermaid
flowchart TD
    A[Call iii7(key)] --> B[Call mediant7(key)]
    B --> C[Return result]
```

## Examples:
    >>> iii7('C')
    # Returns the iii7 chord in the key of C (implementation-dependent)
    >>> iii7('A')
    # Returns the iii7 chord in the key of A (implementation-dependent)
```

## `mingus.core.chords.III7` · *function*

## Summary:
Returns the mediant seventh chord (III7) for a given musical key, which is the seventh chord built on the third degree of the diatonic scale.

## Description:
This function provides a convenient way to retrieve the mediant seventh chord for a specified musical key. In Roman numeral analysis, the mediant seventh chord is denoted as III7, representing the seventh chord built on the third degree of the diatonic scale. The function internally calls the `mediant7()` function to compute the result.

This abstraction allows developers to easily access the mediant seventh chord without needing to understand the underlying implementation details of chord progression calculation. It's particularly useful in music theory applications where specific diatonic chords need to be accessed quickly.

## Args:
    key (str): The musical key for which to retrieve the mediant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the mediant seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the third degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a valid seventh chord.
        - The chord is built on the third degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.
    - Accesses and potentially modifies the global `_sevenths_cache` dictionary through the `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[III7(key)] --> B[Call mediant7(key)]
    B --> C[Return mediant seventh chord]
```

## Examples:
    >>> III7('C')
    ['E', 'G', 'B', 'D']
    >>> III7('G')
    ['B', 'D', 'F#', 'A']
```

## `mingus.core.chords.IV` · *function*

## Summary:
Returns the subdominant triad for a given musical key, representing the IV chord in Roman numeral notation.

## Description:
This function serves as an alias for the `subdominant()` function, providing a convenient way to access the subdominant triad (the fourth chord in the diatonic set) of a specified musical key. The subdominant triad consists of the fourth note of the key's scale, along with its third and fifth intervals, forming the IV chord in standard Roman numeral analysis.

The `IV` function follows the established pattern of chord accessor functions in the chords module, where each function provides a named reference to a specific position in the diatonic chord progression. This naming convention aligns with traditional music theory terminology, making it easier for musicians and developers familiar with Roman numeral analysis to work with chord progressions.

## Args:
    key (str): The musical key for which to retrieve the subdominant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the subdominant triad: [root note, third interval, fifth interval]. The returned triad represents the IV chord in the diatonic set of the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function, which is propagated from the underlying triads() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list always contains exactly three note strings.
        - All returned notes are valid within the context of the specified key.
        - The first note in the returned triad is the fourth note of the key's scale.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[IV(key)] --> B[Call subdominant(key)]
    B --> C[Call triads(key)]
    C --> D[Get fourth triad from list (index 3)]
    D --> E[Return subdominant triad]
```

## Examples:
    >>> IV('C')
    ['F', 'A', 'C']
    >>> IV('G')
    ['C', 'E', 'G']
    >>> IV('A')
    ['D', 'F#', 'A']

## `mingus.core.chords.IV7` · *function*

## Summary:
Returns the subdominant seventh chord (IV7) for a given musical key.

## Description:
Generates the seventh chord built on the fourth degree (subdominant) of the diatonic scale for the specified musical key. This function serves as a convenient alias for the subdominant7 function, providing a more intuitive name for musicians familiar with Roman numeral analysis where IV7 represents the subdominant seventh chord.

## Args:
    key (str): The musical key for which to generate the IV7 chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the IV7 chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the fourth degree of the key's scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the fourth degree of the diatonic scale for the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[IV7(key)] --> B[Call subdominant7(key)]
    B --> C[Return result]
```

## Examples:
    >>> IV7('C')
    ['F', 'A', 'C', 'E']
    >>> IV7('G')
    ['C', 'E', 'G', 'B']

## `mingus.core.chords.V` · *function*

## Summary:
Returns the dominant triad for a given musical key, representing the V chord in Roman numeral notation.

## Description:
Provides a convenient alias for accessing the dominant triad (the fifth degree of the scale) of a specified musical key. In music theory, the Roman numeral "V" represents the dominant chord, which is built on the fifth note of the diatonic scale. This function serves as a shorthand notation for retrieving the dominant triad, following the established naming convention used throughout the chords module.

This function is typically called when working with harmonic analysis, chord progressions, or Roman numeral analysis where quick access to the dominant triad is needed. It's particularly useful in music theory applications and chord progression generators.

## Args:
    key (str): The musical key for which to retrieve the dominant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the dominant triad [root, third, fifth]. Returns the triad corresponding to the fifth degree of the scale in the given key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The root note of the returned triad is the fifth degree of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[V(key)] --> B[Call dominant(key)]
    B --> C[Call triads(key)]
    C --> D[Return triads(key)[4]]
```

## Examples:
    >>> V('C')
    ['G', 'B', 'D']
    >>> V('G')
    ['D', 'F#', 'A']
    >>> V('A')
    ['E', 'G#', 'B']

## `mingus.core.chords.V7` · *function*

## Summary:
Returns the dominant seventh chord (V7) for a given musical key.

## Description:
Provides a convenient accessor for the dominant seventh chord, which is the seventh chord built on the fifth degree of the diatonic scale. This function serves as an alias for the dominant7 function, using Roman numeral notation to identify the chord.

## Args:
    key (str): The musical key for which to generate the dominant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the dominant seventh chord in the specified key. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing the dominant seventh chord.
        - The chord is built on the fifth degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying sevenths() function.

## Control Flow:
```mermaid
flowchart TD
    A[V7(key)] --> B[dominant7(key)]
    B --> C[Return dominant seventh chord]
```

## `mingus.core.chords.vi` · *function*

## Summary:
Returns the submediant triad (sixth degree chord) for a given musical key using Roman numeral notation.

## Description:
Provides convenient access to the submediant triad, which represents the sixth chord in the diatonic set of a musical key. This function serves as an alias for the `submediant()` function, following the standard Roman numeral notation convention where 'vi' denotes the sixth degree of the diatonic scale. The submediant chord is commonly used in harmonic analysis and chord progressions.

## Args:
    key (str): The musical key for which to retrieve the submediant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the submediant triad [root, third, fifth] for the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
        - The key must contain at least 6 notes to have a submediant triad.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The triad returned represents the 6th degree of the diatonic scale for the given key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary through calls to `triads()` function.
    - May modify the global `_key_cache` dictionary indirectly through calls to `keys.get_notes()`.

## Control Flow:
```mermaid
flowchart TD
    A[vi(key)] --> B[Call submediant(key)]
    B --> C[Return submediant result]
```

## `mingus.core.chords.VI` · *function*

## Summary:
Returns the submediant triad for a given musical key using Roman numeral notation.

## Description:
Provides a convenient alias for accessing the submediant triad (the sixth degree of the diatonic scale) of a specified musical key. In music theory, the Roman numeral "VI" represents the submediant chord, which is built on the sixth note of the key's scale. This function serves as a shorthand notation for retrieving the submediant triad, following the established naming convention used throughout the chords module.

This function is typically called when working with harmonic analysis, chord progressions, or Roman numeral analysis where quick access to the submediant triad is needed. It's particularly useful in music theory applications and chord progression generators.

## Args:
    key (str): The musical key for which to retrieve the submediant triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the submediant triad [root, third, fifth]. Returns the triad corresponding to the sixth degree of the scale in the given key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The root note of the returned triad is the sixth degree of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[VI(key)] --> B[Call submediant(key)]
    B --> C[Call triads(key)]
    C --> D[Return triads(key)[5]]
```

## Examples:
    >>> VI('C')
    ['A', 'C', 'E']
    >>> VI('G')
    ['E', 'G', 'B']
    >>> VI('A')
    ['F#', 'A', 'C#']

## `mingus.core.chords.vi7` · *function*

## Summary:
Returns the submediant seventh chord (vi7) for a given musical key.

## Description:
Provides a convenient interface for retrieving the submediant seventh chord, which is the seventh chord built on the 6th degree of the diatonic scale. This function serves as a shorthand for accessing the vi7 chord in Roman numeral notation without needing to manually index into the full seventh chord progression.

## Args:
    key (str): The musical key for which to retrieve the submediant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the submediant seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the 6th degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the 6th degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[vi7(key)] --> B[Call submediant7(key)]
    B --> C[Return result]
```

## Examples:
    >>> vi7('C')
    ['A', 'C', 'E', 'G']
    >>> vi7('G')
    ['E', 'G', 'B', 'D']

## `mingus.core.chords.VI7` · *function*

## Summary:
Returns the submediant seventh chord (VII chord) for a given musical key.

## Description:
Provides a convenient interface to retrieve the submediant seventh chord, also known as the VII chord, from a specified musical key. This function serves as a shorthand for accessing the seventh chord built on the 6th degree of the diatonic scale.

## Args:
    key (str): The musical key for which to retrieve the submediant seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the submediant seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the 6th degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the 6th degree of the diatonic scale of the specified key.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[VI7(key)] --> B[Call submediant7(key)]
    B --> C[Return submediant7(key) result]
```

## Examples:
    >>> VI7('C')
    ['A', 'C', 'E', 'G']
    >>> VI7('G')
    ['E', 'G', 'B', 'D']

## `mingus.core.chords.vii` · *function*

## Summary:
Returns the subtonic triad for a given musical key using Roman numeral notation.

## Description:
This function provides access to the subtonic triad (the seventh degree of the diatonic scale) for a specified musical key. It serves as an alias for the `subtonic()` function, offering a convenient interface for users familiar with Roman numeral analysis in music theory where vii represents the 7th degree chord.

The function retrieves the seventh triad from the complete set of diatonic triads for the specified key, returning a list of three notes that form the subtonic chord. This chord is commonly used in harmonic analysis and chord progression generators.

## Args:
    key (str): The musical key for which to retrieve the subtonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the subtonic triad [root, third, fifth] for the specified key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
        - The key must contain at least 7 notes to have a subtonic chord.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The triad represents the 7th degree of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[vii(key)] --> B[Call subtonic(key)]
    B --> C[Return subtonic triad]
```

## Examples:
    >>> vii('C')
    ['B', 'D', 'F#']
    >>> vii('G')
    ['F#', 'A#', 'C#']
    >>> vii('A')
    ['G#', 'B', 'D']

## `mingus.core.chords.VII` · *function*

## Summary:
Returns the subtonic triad for a given musical key, representing the seventh chord in Roman numeral notation.

## Description:
This function serves as an alias for the `subtonic()` function, providing a convenient way to access the subtonic triad (the seventh degree of the diatonic scale) of a specified musical key. In music theory, the Roman numeral "VII" represents the subtonic chord, which is built on the seventh note of the key's scale. This function follows the established naming convention used throughout the chords module, where each function provides a named reference to a specific position in the diatonic chord progression.

The `VII` function is typically called when working with harmonic analysis, chord progressions, or Roman numeral analysis where quick access to the subtonic triad is needed. It's particularly useful in music theory applications and chord progression generators.

## Args:
    key (str): The musical key for which to retrieve the subtonic triad, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list containing three note strings representing the subtonic triad [root, third, fifth]. Returns the triad corresponding to the seventh degree of the scale in the given key.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly three notes forming a valid triad structure.
        - The root note of the returned triad is the seventh degree of the specified musical key.

## Side Effects:
    - May modify the global `_triads_cache` dictionary indirectly through calls to `triads()` function.

## Control Flow:
```mermaid
flowchart TD
    A[VII(key)] --> B[Call subtonic(key)]
    B --> C[Return subtonic triad]
```

## Examples:
    >>> VII('C')
    ['B', 'D', 'F#']
    >>> VII('G')
    ['F#', 'A#', 'C#']
    >>> VII('A')
    ['G#', 'B', 'D#']
```

## `mingus.core.chords.vii7` · *function*

## Summary:
Returns the subtonic (7th degree) of a given musical key by delegating to the subtonic function.

## Description:
This function serves as a direct interface to retrieve the subtonic (leading tone) of a musical key. It simply passes the provided key parameter to the underlying `subtonic` function and returns its result. The naming follows standard musical notation conventions where "vii7" represents the diminished seventh chord built on the subtonic degree.

This function is part of the chord manipulation utilities in the mingus library and provides a clean API for accessing the 7th degree of a key.

## Args:
    key (any): The musical key input to be processed by the subtonic function. This parameter is passed directly through to the subtonic function without modification.

## Returns:
    The result of calling subtonic(key). The exact return type and format depend on the implementation of the subtonic function.

## Raises:
    Exceptions that may be raised by the subtonic function, though specific exceptions are not declared in this wrapper function.

## Constraints:
    Preconditions:
    - The key parameter must be a valid input for the subtonic function
    - The key parameter must be compatible with the internal subtonic implementation
    
    Postconditions:
    - Returns the same value that subtonic(key) would return
    - No side effects beyond those of the subtonic function

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call vii7(key)] --> B[Return subtonic(key)]
```

## Examples:
    # Retrieve subtonic of C major
    result = vii7("C")
    
    # Retrieve subtonic of G# minor
    result = vii7("G#")

## `mingus.core.chords.VII7` · *function*

## Summary:
Returns the subtonic seventh chord for a given musical key.

## Description:
Provides convenient access to the VII7 (dominant seventh) chord built on the subtonic (7th degree) of the specified musical key. This function serves as an alias for the subtonic7 function, offering a more conventional chord naming convention for users familiar with Roman numeral notation.

## Args:
    key (str): The musical key for which to retrieve the subtonic seventh chord, represented as a string (e.g., 'C', 'G#', 'F#'). Must be a valid key recognized by the keys module.

## Returns:
    list[str]: A list of four note strings representing the subtonic seventh chord. The chord consists of the root note, major third, perfect fifth, and minor seventh intervals built on the subtonic degree of the key's diatonic scale.

## Raises:
    NoteFormatError: When the provided key is not a recognized key format according to keys.is_valid_key() function.

## Constraints:
    Preconditions:
        - The key parameter must be a valid key string recognized by the keys module.
    Postconditions:
        - The returned list contains exactly four note strings representing a complete seventh chord.
        - The chord is built on the subtonic (7th degree) of the specified key's diatonic scale.

## Side Effects:
    - May cause cache growth over time as new keys are processed through the underlying `sevenths()` function.

## Control Flow:
```mermaid
flowchart TD
    A[VII7(key)] --> B[Call subtonic7(key)]
    B --> C[Return result]
```

## Examples:
    >>> VII7('C')
    ['B', 'D', 'F', 'A']
    >>> VII7('G')
    ['F#', 'A', 'C', 'E']

## `mingus.core.chords.invert` · *function*

## Summary:
Creates a chord inversion by moving the root note to the highest position.

## Description:
This function implements basic chord inversion by taking the first note of a chord and placing it at the end of the chord list. This operation transforms a chord from its root position to its first inversion, which is fundamental in music theory for creating different voicings of the same chord.

## Args:
    chord (list): A list representing a chord, typically containing note names or note objects in ascending order.

## Returns:
    list: A new list representing the inverted chord with the original first note moved to the end.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - The input chord must be a non-empty list
        - The chord should contain valid musical note representations
    
    Postconditions:
        - The returned list has the same length as the input chord
        - The first element of the input becomes the last element of the output
        - All other elements maintain their relative order

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input chord] --> B{Chord not empty?}
    B -- Yes --> C[Return chord[1:] + [chord[0]]]
    B -- No --> D[Return empty list]
```

## Examples:
    >>> invert(['C', 'E', 'G'])
    ['E', 'G', 'C']
    
    >>> invert(['A', 'C', 'E', 'G'])
    ['C', 'E', 'G', 'A']
```

## `mingus.core.chords.first_inversion` · *function*

## Summary:
Computes the first inversion of a chord by invoking the invert() function.

## Description:
This function serves as a convenience wrapper that computes the first inversion of a given chord. In musical terms, the first inversion of a triad places the third note of the chord in the bass position. This function delegates the actual inversion calculation to the underlying invert() function.

## Args:
    chord: A chord representation that is compatible with the invert() function. The exact format depends on the chord representation system used in this library.

## Returns:
    The first inversion of the input chord, as computed by the invert() function. The return format matches the input chord format.

## Raises:
    Exceptions that may be raised by the invert() function, such as FormatError or NoteFormatError if the chord is malformed.

## Constraints:
    Precondition: The input chord must be a valid chord representation according to the library's chord formatting rules.
    Postcondition: The returned chord is in its first inversion form.

## Side Effects:
    None. The function is pure and does not modify external state or perform I/O operations.

## Control Flow:
```mermaid
flowchart TD
    A[Input chord] --> B{Call invert(chord)}
    B --> C[Return first inversion]
```

## Examples:
    # Example usage
    chord = ['C', 'E', 'G']  # C major triad
    first_inv = first_inversion(chord)
    # Returns the first inversion of C major triad
    
    # Another example
    chord = ['A', 'C', 'E']  # A minor triad  
    first_inv = first_inversion(chord)
    # Returns the first inversion of A minor triad

## `mingus.core.chords.second_inversion` · *function*

## Summary:
Computes the second inversion of a chord by applying the inversion operation twice.

## Description:
This function calculates the second inversion of a musical chord by applying the basic inversion operation twice. In music theory, the second inversion of a triad places the fifth note of the chord in the bass position. This function serves as a convenience wrapper that provides direct access to the second inversion without requiring manual chaining of inversion operations.

The function delegates to the underlying `invert()` function, which moves the first note of the chord to the end. Applying this operation twice results in the root note being moved up two positions in the chord structure.

## Args:
    chord (list): A list representing a chord, typically containing note names or note objects in ascending order. Must be a non-empty list with valid musical note representations.

## Returns:
    list: A new list representing the second inversion of the input chord, where the original first note has been moved to the second-to-last position, and the second note has been moved to the last position.

## Raises:
    None explicitly raised by this function, though exceptions from the underlying `invert()` function may propagate (such as FormatError or NoteFormatError if the chord is malformed).

## Constraints:
    Preconditions:
        - The input chord must be a non-empty list
        - The chord should contain valid musical note representations
    
    Postconditions:
        - The returned list has the same length as the input chord
        - The first element of the input becomes the third-to-last element of the output
        - The second element of the input becomes the last element of the output
        - All other elements maintain their relative order

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input chord] --> B[Call invert(chord)]
    B --> C[Call invert(result)]
    C --> D[Return second inversion]
```

## Examples:
    >>> second_inversion(['C', 'E', 'G'])
    ['G', 'C', 'E']
    
    >>> second_inversion(['A', 'C', 'E', 'G'])
    ['E', 'G', 'A', 'C']

## `mingus.core.chords.third_inversion` · *function*

## Summary:
Applies third inversion to a chord by cycling the root note three positions upward.

## Description:
This function implements the third inversion of a chord by applying the basic inversion operation three times. In music theory, chord inversions rearrange the notes of a chord to create different voicings. Third inversion specifically refers to the process where the root note (first degree) of a chord is moved to the highest position through three sequential inversions. This results in a chord where the original root note becomes the highest pitch while maintaining the same set of notes.

## Args:
    chord (list): A list representing a chord containing note names or note objects in ascending order.

## Returns:
    list: A new list representing the chord in third inversion, where the original root note has been moved to the highest position through three sequential inversions.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - The input chord must be a non-empty list
        - The chord should contain valid musical note representations
    
    Postconditions:
        - The returned list has the same length as the input chord
        - The original first element of the input becomes the last element of the output (after three inversions)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input chord] --> B[Apply invert() three times]
    B --> C[Return result]
```

## Examples:
    >>> third_inversion(['C', 'E', 'G'])
    ['G', 'C', 'E']
    
    >>> third_inversion(['A', 'C', 'E', 'G'])
    ['G', 'A', 'C', 'E']

## `mingus.core.chords.from_shorthand` · *function*

## Summary:
Converts musical chord shorthand notation into a list of note names representing the chord.

## Description:
Parses chord shorthand strings (like "Cmaj7", "Am", "Dm7", "C/G") and returns the corresponding list of note names that make up the chord. Handles various musical notation conventions including accidentals, chord extensions, and slash chords. This function serves as the primary interface for converting human-readable chord notation into machine-processable chord data.

## Args:
    shorthand_string (str or list): Musical chord shorthand notation. Can be a single string or a list of strings. Valid formats include basic chords (C, Am), extended chords (Cmaj7, Dm7), and slash chords (C/G).
    slash (str or list, optional): Specifies the bass note for slash chords. When provided, it overrides the default bass note derived from the shorthand string.

## Returns:
    list[str]: A list of note names that constitute the chord. Returns an empty list for "NC" or "N.C." shorthand. For slash chords, returns the bass note followed by the chord notes.

## Raises:
    NoteFormatError: When the first character of the shorthand string is not a recognized note letter, or when a slash note is invalid.
    FormatError: When the shorthand string contains unrecognized chord notation.

## Constraints:
    Preconditions:
    - The shorthand_string must be a valid string or list of strings
    - For valid note names, the first character must be a recognized note letter (C, D, E, F, G, A, B)
    - Note names may include sharps (#) or flats (b) but must follow standard musical notation rules
    
    Postconditions:
    - Returns a list of valid note names in proper musical notation
    - Slash chords are properly formatted with bass note first

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start from_shorthand] --> B{shorthand_string is list?}
    B -- Yes --> C[Process each item recursively]
    B -- No --> D{shorthand_string in ["NC", "N.C."]?}
    D -- Yes --> E[Return empty list]
    D -- No --> F[Normalize shorthand abbreviations]
    F --> G[Validate first note character]
    G --> H{First note valid?}
    H -- No --> I[raise NoteFormatError]
    H -- Yes --> J[Parse note name with accidentals]
    J --> K[Find slash or pipe separators]
    K --> L{Slash found and not special case?}
    L -- Yes --> M[Split and recurse on both parts]
    L -- No --> N{Pipe found?}
    N -- Yes --> O[Recursively process both sides]
    N -- No --> P[Extract chord type]
    P --> Q{Chord type in chord_shorthand?}
    Q -- No --> R[raise FormatError]
    Q -- Yes --> S[Generate chord notes]
    S --> T{Slash parameter provided?}
    T -- Yes --> U{Slash is string?}
    U -- Yes --> V{Is slash note valid?}
    V -- No --> W[raise NoteFormatError]
    V -- Yes --> X[Prepend slash note to result]
    U -- No --> Y{Slash is list?}
    Y -- Yes --> Z[Combine slash list with chord notes]
    T -- No --> AA[Return chord notes]
```

## Examples:
    >>> from_shorthand("C")
    ['C']
    
    >>> from_shorthand("Am")
    ['A', 'C', 'E']
    
    >>> from_shorthand("C/G")
    ['G', 'C', 'E', 'G']
    
    >>> from_shorthand("Dm7")
    ['D', 'F', 'A', 'C']
    
    >>> from_shorthand("NC")
    []

## `mingus.core.chords.determine` · *function*

## Summary
Determines the chord type and inversion for musical chords of varying note counts by delegating to specialized analysis functions.

## Description
The `determine` function serves as the primary interface for chord identification in the mingus library. It analyzes musical chords composed of 1 to 14 notes and returns standardized chord name representations that include type, inversion, and extension information. The function routes input to specialized handlers based on the number of notes in the chord, ensuring appropriate analysis for different chord complexities.

This logic is extracted into its own function to provide a unified interface for chord analysis while maintaining modularity through delegation to specialized determination functions. This architectural choice enables clean separation of concerns, allowing each chord size to be handled by optimized, focused implementations.

## Args
    chord (list): A list of musical notes represented as strings (e.g., ['C', 'E', 'G']). The number of notes determines which analysis function is used.
    shorthand (bool): When True, returns abbreviated chord names (e.g., "Cm"). When False, returns full descriptive names with inversion information (e.g., "C, first inversion"). Defaults to False.
    no_inversions (bool): When True, prevents consideration of chord inversions and only analyzes root position. Defaults to False.
    no_polychords (bool): When True, disables polychord detection for chords with 4 or more notes. Defaults to False.

## Returns
    list: A list of chord name representations for valid input chords. Each string in the list represents the same chord in different inversion positions or as different polychord combinations. For empty chords, returns an empty list. For single-note chords, returns the chord unchanged. For two-note chords, returns interval descriptions. For chords with 3-7 notes, returns chord names from specialized determination functions. For chords with more than 7 notes, returns polychord combinations.

## Raises
    None: This function does not explicitly raise exceptions, though underlying functions may raise FormatError or NoteFormatError.

## Constraints
    Preconditions: The input chord must be a list of musical note strings.
    Postconditions: Returns a list of chord name representations for valid inputs, or an empty list for empty inputs.

## Side Effects
    None: This function has no side effects.

## Control Flow
```mermaid
flowchart TD
    A[Start determine] --> B{chord == []?}
    B -- Yes --> C[Return []]
    B -- No --> D{len(chord) == 1?}
    D -- Yes --> E[Return chord]
    D -- No --> F{len(chord) == 2?}
    F -- Yes --> G[Call intervals.determine(chord[0], chord[1])]
    F -- No --> H{len(chord) == 3?}
    H -- Yes --> I[Call determine_triad(chord, shorthand, no_inversions, no_polychords)]
    H -- No --> J{len(chord) == 4?}
    J -- Yes --> K[Call determine_seventh(chord, shorthand, no_inversions, no_polychords)]
    J -- No --> L{len(chord) == 5?}
    L -- Yes --> M[Call determine_extended_chord5(chord, shorthand, no_inversions, no_polychords)]
    L -- No --> N{len(chord) == 6?}
    N -- Yes --> O[Call determine_extended_chord6(chord, shorthand, no_inversions, no_polychords)]
    N -- No --> P{len(chord) == 7?}
    P -- Yes --> Q[Call determine_extended_chord7(chord, shorthand, no_inversions, no_polychords)]
    P -- No --> R[Call determine_polychords(chord, shorthand)]
```

## Examples
    >>> determine(['C', 'E', 'G'])
    # Returns chord representations for C major triad in all inversions
    
    >>> determine(['C', 'E', 'G'], shorthand=True)
    # Returns shorthand chord representations for C major triad in all inversions
    
    >>> determine(['C', 'E', 'G', 'B'])
    # Returns chord representations for C major seventh chord in all inversions
    
    >>> determine(['C', 'E', 'G', 'B', 'D', 'F'])
    # Returns extended chord representations for C11 chord in all inversions
    
    >>> determine([])
    # Returns []
    
    >>> determine(['C'])
    # Returns ['C']

## `mingus.core.chords.determine_triad` · *function*

## Summary:
Analyzes a three-note musical triad to identify its chord type and inversion positions.

## Description:
Examines interval relationships between three musical notes to classify them as standard triadic chords (major, minor, diminished, augmented, etc.). The function systematically tests all possible inversions of the triad and returns comprehensive chord name representations. This modular design separates chord identification logic from other musical operations, enabling reuse across different contexts.

## Args:
    triad (list): A list containing exactly three musical notes represented as strings (e.g., ['C', 'E', 'G']). Must contain exactly 3 elements.
    shorthand (bool): When True, returns abbreviated chord names (e.g., "Cm"). When False, returns full descriptive names with inversion information (e.g., "C, first inversion"). Defaults to False.
    no_inversions (bool): When True, prevents consideration of chord inversions and only analyzes root position. Defaults to False.
    placeholder (None): Unused parameter in current implementation. Defaults to None.

## Returns:
    list or bool: Returns a list of chord name representations if the input contains exactly 3 notes. Each entry in the list represents the same chord in a different inversion position. Returns False if the input does not contain exactly 3 notes.

## Raises:
    None: This function does not explicitly raise exceptions, though it may return False for invalid inputs.

## Constraints:
    Preconditions: The input triad must contain exactly 3 notes.
    Postconditions: If input is valid, returns a list of chord name representations; if invalid, returns False.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start determine_triad] --> B{len(triad) != 3?}
    B -- Yes --> C[Return False]
    B -- No --> D[Call inversion_exhauster(triad, shorthand, 1, [])]
    D --> E[intervals.determine(triad[0], triad[1])]
    E --> F[intervals.determine(triad[0], triad[2])]
    F --> G[Combine intervals into intval]
    G --> H{intval matches pattern?}
    H --> I[add_result with chord type]
    I --> J{tries != 3 AND not no_inversions?}
    J -- Yes --> K[Recursively call inversion_exhauster with rotated triad]
    J -- No --> L[Build result list with shorthand/full format]
    L --> M[Return result list]
```

## Examples:
    >>> determine_triad(['C', 'E', 'G'])
    # Returns chord representations for C major triad in root position, first inversion, and second inversion
    
    >>> determine_triad(['C', 'E', 'G'], shorthand=True)
    # Returns shorthand chord representations for C major triad in all inversions

## `mingus.core.chords.determine_seventh` · *function*

## Summary:
Determines the chord name for a four-note seventh chord by analyzing triad types and interval relationships, including support for inversions and polychords.

## Description:
Analyzes a four-note musical chord to identify its specific seventh chord type. The function examines the triad formed by the first three notes and the interval between the root and the fourth note to determine the appropriate chord designation. It supports multiple inversion positions and can identify polychord combinations when requested.

This logic is extracted into its own function to encapsulate the complex analysis of seventh chord identification, separating this specific musical analysis from basic chord identification routines. This modular approach allows for reuse in various contexts where seventh chord recognition is needed, while maintaining clean separation of concerns.

## Args:
    seventh (list): A list of exactly four musical notes represented as strings (e.g., ['C', 'E', 'G', 'B']). Must contain exactly 4 elements.
    shorthand (bool): When True, returns abbreviated chord names. When False, returns full descriptive names with inversion information. Defaults to False.
    no_inversion (bool): When True, prevents consideration of chord inversions and only analyzes root position. Defaults to False.
    no_polychords (bool): When True, disables polychord detection. Defaults to False.

## Returns:
    list or bool: Returns a list of chord name representations if the input contains exactly 4 notes. Returns False if the input does not contain exactly 4 notes.

## Raises:
    None: This function does not explicitly raise exceptions, though underlying functions may raise FormatError or NoteFormatError.

## Constraints:
    Preconditions: The input seventh must contain exactly 4 notes.
    Postconditions: If input is valid, returns a list of chord name representations; if invalid, returns False.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
The function first validates that exactly 4 notes are provided. If valid, it recursively analyzes different inversions of the chord using an internal helper function. For each inversion, it:
1. Determines the triad from the first three notes using determine_triad
2. Calculates the interval between the root and fourth note using intervals.determine
3. Matches the triad type and interval to determine the chord abbreviation
4. Processes inversion and polychord information
5. Returns results formatted according to the shorthand parameter

## Examples:
    >>> determine_seventh(['C', 'E', 'G', 'B'])
    # Returns chord representations for C major seventh chord in all inversions
    
    >>> determine_seventh(['C', 'E', 'G', 'B'], shorthand=True)
    # Returns shorthand chord representations for C major seventh chord in all inversions

## `mingus.core.chords.determine_extended_chord5` · *function*

## Summary:
Determines extended chord names for five-note musical chords by analyzing interval relationships and inversion positions.

## Description:
Analyzes a five-note musical chord to identify its extended chord designation, including ninth, eleventh, and thirteenth chords. The function systematically evaluates all possible inversions of the chord and identifies specific extended chord types based on the interval relationships between notes. It also supports polychord detection when enabled.

This logic is extracted into its own function to encapsulate the complex analysis of extended chord identification, separating this specific musical analysis from basic chord identification routines. This modular approach enables reuse in various contexts where extended chord recognition is needed while maintaining clean separation of concerns.

## Args:
    chord (list): A list of exactly five musical notes represented as strings (e.g., ['C', 'E', 'G', 'B', 'D']). Must contain exactly 5 elements.
    shorthand (bool): When True, returns abbreviated chord names (e.g., "Cm9"). When False, returns full descriptive names with inversion information (e.g., "C, first inversion, m9"). Defaults to False.
    no_inversions (bool): When True, prevents consideration of chord inversions and only analyzes root position. Defaults to False.
    no_polychords (bool): When True, disables polychord detection. Defaults to False.

## Returns:
    list or bool: Returns a list of extended chord name representations if the input contains exactly 5 notes. Each entry in the list represents the same chord in a different inversion position or as a polychord combination. Returns False if the input does not contain exactly 5 notes.

## Raises:
    None: This function does not explicitly raise exceptions, though underlying functions may raise FormatError or NoteFormatError.

## Constraints:
    Preconditions: The input chord must contain exactly 5 notes.
    Postconditions: If input is valid, returns a list of extended chord name representations; if invalid, returns False.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start determine_extended_chord5] --> B{len(chord) != 5?}
    B -- Yes --> C[Return False]
    B -- No --> D[Call inversion_exhauster(chord, shorthand, 1, [], [])]
    D --> E{tries == 1 AND not no_polychords?}
    E -- Yes --> F[Call determine_polychords(chord, shorthand)]
    E -- No --> G[Skip polychord detection]
    F --> H[Set polychords = result]
    G --> I[Call determine_triad(chord[:3], True, True)]
    I --> J[Call determine_seventh(chord[:4], True, True, True)]
    J --> K[Process sevenths and intervals]
    K --> L{seventh == "M7"?}
    L -- Yes --> M{intval4 == "major second"?}
    M -- Yes --> N[Add "M9" to result]
    L -- No --> O{seventh == "m7"?}
    O -- Yes --> P{intval4 == "major second"?}
    P -- Yes --> Q[Add "m9" to result]
    P -- No --> R{intval4 == "perfect fourth"?}
    R -- Yes --> S[Add "m11" to result]
    O -- No --> T{seventh == "7"?}
    T -- Yes --> U{intval4 == "major second"?}
    U -- Yes --> V[Add "9" to result]
    U -- No --> W{intval4 == "minor second"?}
    W -- Yes --> X[Add "7b9" to result]
    W -- No --> Y{intval4 == "augmented second"?}
    Y -- Yes --> Z[Add "7#9" to result]
    Y -- No --> AA{intval4 == "minor third"?}
    AA -- Yes --> AB[Add "7b12" to result]
    AA -- No --> AC{intval4 == "augmented fourth"?}
    AC -- Yes --> AD[Add "7#11" to result]
    AC -- No --> AE{intval4 == "major sixth"?}
    AE -- Yes --> AF[Add "13" to result]
    T -- No --> AG{seventh == "M6"?}
    AG -- Yes --> AH{intval4 == "major second"?}
    AH -- Yes --> AI[Add "6/9" to result]
    AH -- No --> AJ{intval4 == "minor seventh"?}
    AJ -- Yes --> AK[Add "6/7" to result]
    AK --> AL[Check if tries != 5 AND not no_inversions]
    AL -- Yes --> AM[Recursively call inversion_exhauster with rotated chord]
    AL -- No --> AN[Build result list with shorthand/full format]
    AN --> AO[Return result + polychords]
```

## Examples:
    >>> determine_extended_chord5(['C', 'E', 'G', 'B', 'D'])
    # Returns extended chord representations for Cmaj9 chord in all inversions
    
    >>> determine_extended_chord5(['C', 'E', 'G', 'B', 'D'], shorthand=True)
    # Returns shorthand extended chord representations for Cmaj9 chord in all inversions
    
    >>> determine_extended_chord5(['C', 'E', 'G', 'B', 'D'], no_inversions=True)
    # Returns extended chord representations for Cmaj9 chord in root position only
    
    >>> determine_extended_chord5(['C', 'E', 'G', 'B', 'D'], no_polychords=True)
    # Returns extended chord representations without polychord combinations

## `mingus.core.chords.determine_extended_chord6` · *function*

## Summary:
Determines extended chord names (9th, 11th, 13th) for 6-note chords by analyzing interval relationships and inversion patterns.

## Description:
Analyzes a 6-note chord to identify extended chord extensions such as 9th, 11th, and 13th chords. This function processes chords by testing different inversions and determining the appropriate extension based on the interval relationship between the first and sixth notes. It can also detect polychords when enabled.

This logic is extracted into its own function to handle the complexity of extended chord identification for 6-note chords, separating this specific functionality from simpler chord detection methods while maintaining consistency with the existing chord analysis framework.

## Args:
    chord (list): A list of 6 musical notes to analyze
    shorthand (bool): When True, returns abbreviated chord names (e.g., "C11"). When False, returns full names with inversion descriptions (e.g., "C11, first inversion"). Defaults to False.
    no_inversions (bool): When True, disables inversion testing and only returns root position results. Defaults to False.
    no_polychords (bool): When True, disables polychord detection. Defaults to False.

## Returns:
    list or bool: Returns a list of possible extended chord names for the given 6-note chord, or False if the input chord doesn't contain exactly 6 notes. The returned list contains strings representing various interpretations of the chord based on different inversions and extensions.

## Raises:
    None: This function doesn't explicitly raise exceptions, though underlying functions may raise FormatError or NoteFormatError.

## Constraints:
    Preconditions: The input chord must contain exactly 6 notes.
    Postconditions: If successful, returns a list of extended chord names representing valid interpretations of the input chord.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start determine_extended_chord6] --> B{len(chord) != 6?}
    B -- Yes --> C[Return False]
    B -- No --> D[Initialize inversion_exhauster]
    D --> E{tries == 1 and not no_polychords?}
    E --> F[Call determine_polychords]
    F --> G[Call determine_extended_chord5]
    G --> H[Get interval between first and last notes]
    H --> I{Process each extended chord from determine_extended_chord5}
    I --> J{c == "9"}
    J --> K{intval5 == "perfect fourth"?}
    K --> L[Add "11" to result]
    K --> M{intval5 == "augmented fourth"?}
    M --> N[Add "7#11" to result]
    M --> O{intval5 == "major sixth"?}
    O --> P[Add "13" to result]
    J --> Q{c == "m9"}
    Q --> R{intval5 == "perfect fourth"?}
    R --> S[Add "m11" to result]
    R --> T{intval5 == "major sixth"?}
    T --> U[Add "m13" to result]
    Q --> V{c == "M9"}
    V --> W{intval5 == "perfect fourth"?}
    W --> X[Add "M11" to result]
    W --> Y{intval5 == "major sixth"?}
    Y --> Z[Add "M13" to result]
    I --> AA{More inversions possible?}
    AA --> AB[Recursively call inversion_exhauster]
    AA --> AC{No more inversions?}
    AC --> AD[Build final result strings]
    AD --> AE[Return combined results]
```

## Examples:
    >>> determine_extended_chord6(['C', 'E', 'G', 'B', 'D', 'F'])
    ['C11', 'C7#11', 'C13']
    
    >>> determine_extended_chord6(['C', 'E', 'G', 'B', 'D', 'F'], shorthand=True)
    ['C11', 'C7#11', 'C13']
    
    >>> determine_extended_chord6(['C', 'E', 'G', 'B', 'D', 'F'], no_inversions=True)
    ['C11', 'C7#11', 'C13']
```

## `mingus.core.chords.determine_extended_chord7` · *function*

## Summary:
Determines extended chord names (13th chords) for 7-note chords by analyzing interval relationships and inversion patterns.

## Description:
Analyzes a 7-note chord to identify extended chord extensions such as 13th chords. This function processes chords by testing different inversions and determining the appropriate extension based on the interval relationship between the first and seventh notes. It specifically converts 11th chord extensions to 13th chords when the interval between the root and the 7th note is a major sixth.

This logic is extracted into its own function to handle the complexity of extended chord identification for 7-note chords, separating this specific functionality from simpler chord detection methods while maintaining consistency with the existing chord analysis framework. It builds upon the functionality of `determine_extended_chord6` to extend chord analysis to 7-note combinations.

## Args:
    chord (list): A list of 7 musical notes to analyze
    shorthand (bool): When True, returns abbreviated chord names (e.g., "C13"). When False, returns full names with inversion descriptions (e.g., "C13, first inversion"). Defaults to False.
    no_inversions (bool): When True, disables inversion testing and only returns root position results. Defaults to False.
    no_polychords (bool): When True, disables polychord detection. Defaults to False.

## Returns:
    list or bool: Returns a list of possible extended chord names for the given 7-note chord when successful, or False if the input chord doesn't contain exactly 7 notes. The returned list contains strings representing various interpretations of the chord based on different inversions and extensions.

## Raises:
    None: This function doesn't explicitly raise exceptions, though underlying functions may raise FormatError or NoteFormatError.

## Constraints:
    Preconditions: The input chord must contain exactly 7 notes.
    Postconditions: If successful, returns a list of extended chord names representing valid interpretations of the input chord.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start determine_extended_chord7] --> B{len(chord) != 7?}
    B -- Yes --> C[Return False]
    B -- No --> D[Initialize inversion_exhauster]
    D --> E{tries == 1 and not no_polychords?}
    E --> F[Call determine_polychords]
    F --> G[Call determine_extended_chord6]
    G --> H[Get interval between first and seventh notes]
    H --> I{Process each extended chord from determine_extended_chord6}
    I --> J{c == "11" and intval6 == "major sixth"?}
    J --> K[Add "13" to result]
    J --> L{c == "m11" and intval6 == "major sixth"?}
    L --> M[Add "m13" to result]
    L --> N{c == "M11" and intval6 == "major sixth"?}
    N --> O[Add "M13" to result]
    I --> P{More inversions possible?}
    P --> Q[Recursively call inversion_exhauster]
    P --> R{No more inversions?}
    R --> S[Build final result strings]
    S --> T[Return combined results]
```

## `mingus.core.chords.int_desc` · *function*

## Summary:
Converts chord inversion numbers into descriptive text labels.

## Description:
Maps numeric inversion indicators to their corresponding textual descriptions for chord inversions. This utility function is used to generate human-readable representations of chord inversions in musical notation.

## Args:
    tries (int): The inversion number, where 1 represents root position and higher numbers represent successive inversions (2 = first inversion, 3 = second inversion, 4 = third inversion). Expected values are integers 1 through 4.

## Returns:
    str: Textual description of the chord inversion. Returns empty string for root position (1), and descriptive strings for inversions 2-4. For values outside the expected range (1-4), the function will return None implicitly.

## Raises:
    None: This function does not explicitly raise any exceptions.

## Constraints:
    Preconditions: The input parameter `tries` should be an integer between 1 and 4 inclusive for defined behavior.
    Postconditions: The returned string will be one of the predefined descriptions or an empty string for valid inputs (1-4).

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start int_desc(tries)] --> B{tries == 1?}
    B -- Yes --> C[Return ""]
    B -- No --> D{tries == 2?}
    D -- Yes --> E[Return ", first inversion"]
    D -- No --> F{tries == 3?}
    F -- Yes --> G[Return ", second inversion"]
    F -- No --> H{tries == 4?}
    H -- Yes --> I[Return ", third inversion"]
    H -- No --> J[Return None]
```

## Examples:
    >>> int_desc(1)
    ''
    >>> int_desc(2)
    ', first inversion'
    >>> int_desc(3)
    ', second inversion'
    >>> int_desc(4)
    ', third inversion'

## `mingus.core.chords.determine_polychords` · *function*

## Summary:
Identifies and generates all possible polychord combinations from chords containing 4 to 14 notes by decomposing the chord into two constituent chords.

## Description:
Analyzes chords with 4-14 notes to determine all valid polychord combinations. A polychord consists of two separate chords played simultaneously, where one chord is formed from the first portion of the original chord and another from the latter portion. This function systematically tests different ways to split the chord and identifies valid constituent chords using specialized chord determination functions.

The function is extracted into its own component to encapsulate the complex logic of polychord generation, separating this specific musical analysis from basic chord identification routines. This modular approach enables efficient reuse of chord detection logic while providing a clean interface for polychord analysis.

## Args:
    chord (list): A list of musical notes (as strings) representing the chord to analyze. Must contain between 4 and 14 notes inclusive.
    shorthand (bool): When True, attempts to append " polychord" to each polychord result. Note: This functionality appears to be broken in the current implementation as it does not modify the returned list. Defaults to False.

## Returns:
    list: A list of strings representing all possible polychord combinations in the format "chord1|chord2". Each combination represents a valid decomposition of the input chord into two constituent chords. Returns an empty list for chords with 3 or fewer notes, or chords with more than 14 notes.

## Raises:
    None: This function does not explicitly raise exceptions, though underlying functions may raise FormatError or NoteFormatError.

## Constraints:
    Preconditions: The input chord must contain between 4 and 14 notes inclusive.
    Postconditions: Returns a list of valid polychord combinations or an empty list for invalid inputs.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start determine_polychords] --> B{len(chord) <= 3?}
    B -- Yes --> C[Return []]
    B -- No --> D{len(chord) > 14?}
    D -- Yes --> E[Return []]
    D -- No --> F{len(chord) - 3 <= 5?}
    F -- Yes --> G[function_nr = range(0, len(chord) - 3)]
    F -- No --> H[function_nr = range(0, 5)]
    G --> I[For each f in function_nr]
    H --> I
    I --> J[For each f2 in function_nr]
    J --> K[Call function_list[f] with chord[len(chord)-(3+f):], True, True, True]
    K --> L[For each chord1 in result]
    L --> M[Call function_list[f2] with chord[:f2+3], True, True, True]
    M --> N[For each chord2 in result]
    N --> O[Append "%s|%s" % (chord1, chord2) to polychords]
    O --> P{shorthand?}
    P -- Yes --> Q[Loop through polychords and attempt to append " polychord" to each (buggy implementation)]
    P -- No --> R[Continue]
    R --> S[Return polychords]
```

## Examples:
    >>> determine_polychords(['C', 'E', 'G', 'B'])
    # Returns all possible polychord combinations for a 4-note chord
    
    >>> determine_polychords(['C', 'E', 'G', 'B', 'D'], shorthand=True)
    # Returns polychord combinations (with buggy shorthand handling) for a 5-note chord

