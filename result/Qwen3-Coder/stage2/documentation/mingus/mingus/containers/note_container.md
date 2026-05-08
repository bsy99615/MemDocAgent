# `note_container.py`

## `mingus.containers.note_container.NoteContainer` · *class*

## Summary:
A container class for managing collections of musical Note objects, providing methods for note manipulation, chord progression creation, and consonance analysis.

## Description:
The NoteContainer class manages a collection of mingus.containers.Note objects, offering functionality to add, remove, and manipulate musical notes. It provides specialized methods for creating note sequences from musical concepts like chords, intervals, and progressions, as well as analyzing the musical properties of note collections such as consonance.

This container is typically used when working with groups of notes rather than individual notes, enabling operations on musical sequences and facilitating music theory computations.

## State:
- notes (list): A list of Note objects stored in the container. The list is maintained in sorted order internally.
  - Type: list of mingus.containers.note.Note objects
  - Valid range: Empty list or list containing Note objects
  - Invariant: The notes list is always kept sorted alphabetically by note name and octave

## Lifecycle:
- Creation: Instantiate with optional initial notes via `__init__(notes=None)` or use factory methods like `from_chord_shorthand()`
- Usage: Add notes with `add_note()` or `add_notes()`, manipulate with `transpose()`, `augment()`, `diminish()`, or analyze with consonance methods
- Destruction: Uses standard Python garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[NoteContainer.__init__] --> B[empty()]
    B --> C[add_notes()]
    C --> D{Factory Methods}
    D --> E[from_chord_shorthand]
    D --> F[from_interval_shorthand]
    D --> G[from_progression_shorthand]
    D --> H[add_note/add_notes]
    H --> I[sort]
    I --> J[transpose]
    J --> K[consonance_analysis]
    K --> L[remove_note/remove_notes]
    L --> M[get_note_names]
    M --> N[determine]
```

## Raises:
- UnexpectedObjectError: Raised in `add_note()` when a non-Note object is passed that doesn't have a "name" attribute
- NoteFormatError: Raised by underlying functions when invalid note representations are encountered during chord/interval/progression parsing

## Example:
```python
# Create a container and add notes
container = NoteContainer()
container.add_note("C")
container.add_note("E")
container.add_note("G")

# Check consonance
print(container.is_consonant())  # True for major triad

# Create from chord shorthand
container.from_chord_shorthand("C:maj")
print(container)  # Shows C-E-G notes

# Transpose notes
container.transpose("P5")  # Move up a perfect fifth
print(container)  # Shows G-B-D notes

# Remove notes
container.remove_note("G")
print(container)  # Shows B-D notes
```

### `mingus.containers.note_container.NoteContainer.__init__` · *method*

## Summary:
Initializes a NoteContainer with optional notes, clearing any existing notes first.

## Description:
The NoteContainer constructor prepares the container for storing musical notes. It clears any existing notes and populates the container with the provided notes, if any. This method ensures a clean initialization state regardless of previous content.

## Args:
    notes (list, Note, str, or None, optional): A collection of notes to initialize the container with. Can be a list of notes, a single note, a string representation of a note, or None. Defaults to None.

## Returns:
    None: This method does not return a value.

## Raises:
    UnexpectedObjectError: If a note object is provided that doesn't have a 'name' attribute.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: None
    Postconditions: self.notes contains the provided notes (or is empty if no notes were provided)

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.empty` · *method*

## Summary:
Clears all notes from the note container by resetting the internal notes list to an empty list.

## Description:
The empty() method removes all notes currently stored in the note container by setting the internal notes attribute to an empty list. This method is primarily used to reset the container state before populating it with new notes from various musical constructs such as chords, intervals, or progressions.

Known callers:
- NoteContainer.from_chord_shorthand(): Called to clear existing notes before building a new chord
- NoteContainer.from_interval_shorthand(): Called to clear existing notes before building a new interval
- NoteContainer.from_progression_shorthand(): Called to clear existing notes before building a new progression

This method exists as a separate function rather than being inlined because it provides a clear semantic operation for resetting the container state, reduces code duplication across methods that need to clear notes before adding new ones, and allows for potential future enhancements without modifying multiple locations.

## Returns:
None

## State Changes:
Attributes READ: None
Attributes WRITTEN: self.notes

## Constraints:
Preconditions: None
Postconditions: self.notes will be an empty list

## Side Effects:
None

### `mingus.containers.note_container.NoteContainer.add_note` · *method*

## Summary:
Adds a musical note to the container, handling both string representations and Note objects while maintaining sorted order and uniqueness.

## Description:
This method provides flexible note addition to a NoteContainer, accepting either string representations of notes (like "C", "D#") or full Note objects. It automatically handles octave assignment for string notes and ensures that duplicate notes are not added to the container. The method maintains the container's notes in sorted order.

## Args:
    note (str or Note): Either a string representing a note name (e.g., "C", "D#") or a Note object to be added to the container.
    octave (int, optional): The octave number to assign when note is a string. If None, automatic octave assignment occurs based on existing notes.
    dynamics (dict, optional): Dynamics information to associate with the note. Defaults to an empty dictionary.

## Returns:
    list[Note]: The updated list of notes in the container, sorted in ascending order.

## Raises:
    UnexpectedObjectError: When the note parameter is neither a string nor a Note object with a 'name' attribute.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The note parameter must be either a string or a Note object with a 'name' attribute.
    Postconditions: The note is added to self.notes if not already present, and the list remains sorted.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.add_notes` · *method*

## Summary:
Adds multiple notes to the NoteContainer, supporting various input formats including Note objects, note names, and structured note data.

## Description:
This method provides a flexible interface for adding notes to a NoteContainer. It intelligently handles different input types by delegating to the underlying add_note method for individual note processing. The method is designed to support diverse musical notation inputs while maintaining consistent container state management.

This method exists to provide a unified interface for adding notes regardless of input format, avoiding the need to manually check and convert different input types before adding them to the container. It's particularly useful when working with chord shorthand, interval notation, or when building containers from various musical data sources.

## Args:
    notes: Supports multiple input types:
        - An object with a 'notes' attribute (e.g., another NoteContainer or chord-like object) - processes each note in the attribute
        - A Note object with a 'name' attribute - adds the single note directly
        - A string representing a note name - adds the note using default octave handling
        - An iterable of notes where each element can be:
          - A string note name
          - A Note object
          - A list containing note information (name, octave, dynamics) - handles 2-element or 3-element lists specially

## Returns:
    list[Note]: The updated list of notes in the container

## Raises:
    UnexpectedObjectError: When a note object doesn't have a 'name' attribute

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The NoteContainer instance must be properly initialized
    Postconditions: All notes in the input are added to self.notes if they don't already exist, and the list remains sorted

## Side Effects:
    Mutates the self.notes list by appending new Note objects
    May trigger sorting of notes in the container

### `mingus.containers.note_container.NoteContainer.from_chord` · *method*

## Summary:
Populates the note container with notes from a chord shorthand representation.

## Description:
Converts a chord shorthand string (like "Cmaj", "Am", "G7") into individual notes and adds them to the note container. This method clears any existing notes in the container before adding the new chord notes. It serves as a convenient interface for building chord-based note collections.

## Args:
    shorthand (str): A chord shorthand string representing the desired chord (e.g., "Cmaj", "Am", "G7").

## Returns:
    NoteContainer: Returns self to enable method chaining.

## Raises:
    NoteFormatError: When the shorthand contains an unrecognized note.
    FormatError: When the shorthand string format is not recognized.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (clears and repopulates with chord notes)

## Constraints:
    Preconditions: The shorthand string must be a valid chord shorthand format.
    Postconditions: The note container will contain exactly the notes that make up the specified chord.

## Side Effects:
    Mutates the internal notes list of the NoteContainer instance.

### `mingus.containers.note_container.NoteContainer.from_chord_shorthand` · *method*

## Summary:
Populates the note container with notes derived from a chord shorthand notation string, clearing any existing notes.

## Description:
Converts a chord shorthand notation (such as "C", "Am", "G7", "Bb:maj") into individual note representations and stores them in the container. This method clears all previously stored notes before adding the new ones. It serves as a convenient way to build chord-based note collections from human-readable chord symbols.

This method is part of a family of factory methods in NoteContainer that allow building note collections from various musical constructs (chords, intervals, progressions). It's separated from inline usage to provide a clean, reusable interface for chord creation.

## Args:
    shorthand (str): A chord shorthand notation string representing the desired chord. Supported formats include basic triads (C, Am), seventh chords (C7, Am7), extended chords (Cmaj7, G9), and slash chords (C/G). The shorthand must begin with a valid note name followed by optional chord modifiers.

## Returns:
    NoteContainer: Returns self to enable method chaining operations.

## Raises:
    NoteFormatError: When the shorthand contains an unrecognized note name or invalid note format.
    FormatError: When the shorthand notation is not recognized or unsupported by the chord parsing system.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (replaced with new note list)

## Constraints:
    Preconditions: The shorthand string must be a valid chord shorthand notation that can be parsed by the underlying chord parsing system.
    Postconditions: The container will contain exactly the notes that make up the specified chord.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.from_interval` · *method*

## Summary:
Creates a note container with two notes separated by a specified musical interval, starting from a given note.

## Description:
This method populates the note container with two notes that form a musical interval. It takes a starting note and creates a second note by transposing the starting note by the specified interval. The method delegates to `from_interval_shorthand` and provides a simplified interface with a default direction parameter.

This method is commonly used in musical composition and analysis workflows where interval-based note generation is needed, such as creating chord progressions or analyzing harmonic relationships.

## Args:
    startnote (Note or str): The starting note for the interval. Can be a Note object or a string representation (e.g., "C-4" or "C").
    shorthand (str): The interval shorthand notation (e.g., "m3", "P5", "M7").
    up (bool): Direction of the interval. True for ascending, False for descending. Defaults to True.

## Returns:
    NoteContainer: The same NoteContainer instance with two notes added: the starting note and the note at the specified interval.

## Raises:
    UnexpectedObjectError: If the startnote parameter cannot be properly converted to a Note object.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (the container is emptied and populated with two notes)

## Constraints:
    Preconditions: 
    - startnote must be a valid Note object or convertible string representation
    - shorthand must be a valid interval shorthand notation
    - The NoteContainer must be properly initialized
    
    Postconditions:
    - The container will contain exactly two notes
    - The notes will be sorted in ascending order
    - The second note will be positioned at the specified interval from the first note

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.from_interval_shorthand` · *method*

## Summary:
Creates a two-note sequence by transposing a starting note by an interval shorthand and adds both notes to the container.

## Description:
This method populates the NoteContainer with two notes: the original starting note and a transposed version of that note. It's designed to quickly build intervals from shorthand notation (like "M2", "m3", "P5") and is commonly used in musical composition and analysis workflows where interval construction is needed.

The method is particularly useful in musical contexts where you want to visualize or work with intervals, such as constructing scales, chords, or intervallic relationships. It serves as a convenient factory method for creating interval-based note sequences.

## Args:
    startnote (Note or str): The starting note for the interval. Can be a Note object or a string representation (e.g., "C4", "D#").
    shorthand (str): The interval shorthand notation (e.g., "M2", "m3", "P5") that defines the interval size and quality.
    up (bool): Direction of transposition. True for upward transposition, False for downward. Defaults to True.

## Returns:
    NoteContainer: Returns self to allow method chaining.

## Raises:
    None explicitly raised, but may propagate exceptions from:
    - Note constructor when string input is invalid
    - Note.transpose when interval shorthand is invalid
    - NoteContainer.add_notes when note validation fails

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (replaced with new note list)

## Constraints:
    Preconditions:
    - startnote must be a valid Note object or convertible string representation
    - shorthand must be a valid interval shorthand notation
    - The NoteContainer must be properly initialized
    Postconditions:
    - The container will contain exactly two notes: the original startnote and its transposed version
    - Both notes are sorted in the container according to the Note comparison logic

## Side Effects:
    None: This method only modifies the internal state of the NoteContainer instance.

### `mingus.containers.note_container.NoteContainer.from_progression` · *method*

## Summary:
Initializes the note container with notes from a Roman numeral chord progression in the specified key.

## Description:
Converts a Roman numeral chord progression (e.g., "I IV V") into actual musical notes and populates the note container with the first chord's notes. This method serves as a convenient interface for building note containers from harmonic progressions.

The method delegates to `from_progression_shorthand` which handles the actual conversion process using the `mingus.core.progressions.to_chords` function.

## Args:
    shorthand (str): A Roman numeral chord progression string (e.g., "I IV V" or "V7").
    key (str, optional): The musical key for chord construction. Defaults to "C".

## Returns:
    NoteContainer or bool: Returns self for method chaining if successful, or False if the progression produces no valid chords.

## Raises:
    None explicitly raised by this method, though underlying functions may raise exceptions for invalid inputs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (replaced with new chord notes)

## Constraints:
    Preconditions: The shorthand parameter must be a valid Roman numeral progression string.
    Postconditions: The note container will contain the notes of the first chord in the progression, or remain empty if no valid chords are produced.

## Side Effects:
    Mutates the internal `notes` attribute of the NoteContainer instance.
    Calls external functions from `mingus.core.progressions` module.

### `mingus.containers.note_container.NoteContainer.from_progression_shorthand` · *method*

## Summary:
Populates the note container with notes from the first chord of a Roman numeral progression shorthand.

## Description:
Converts a Roman numeral chord progression shorthand (e.g., "I", "V", "vi") into actual musical notes and loads them into the note container. This method clears any existing notes in the container before adding the new chord notes. It supports various progression formats including basic chords, seventh chords, and chords with accidentals.

Known callers:
- NoteContainer.from_progression(): Called when converting a progression shorthand to notes with a specified key
- Direct user invocation: Called when users want to populate a note container with progression-based notes

This method exists as a separate function rather than being inlined because it provides a clean abstraction for converting progression shorthand to note data, maintains consistency with other similar conversion methods in the class (like from_chord_shorthand and from_interval_shorthand), and allows for easy reuse of the progression-to-notes conversion logic.

## Args:
    shorthand (str): A Roman numeral progression shorthand string (e.g., "I", "V7", "#IV"). Supports basic Roman numerals, accidentals (#, b), and chord extensions.
    key (str): The musical key for chord construction, defaults to "C". Determines the base notes for chord formation.

## Returns:
    NoteContainer or bool: Returns the NoteContainer instance (self) if successful, or False if the progression shorthand could not be converted to any chords.

## Raises:
    None explicitly raised, though invalid progression shorthands may result in returning False.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.notes: Cleared and populated with notes from the first chord of the progression

## Constraints:
    Preconditions: The NoteContainer instance must be properly initialized
    Postconditions: If successful, self.notes will contain the notes of the first chord from the progression; if unsuccessful, self.notes will be empty

## Side Effects:
    Mutates the internal self.notes list by clearing existing notes and adding new ones

### `mingus.containers.note_container.NoteContainer._consonance_test` · *method*

## Summary:
Tests whether all pairs of notes in the container satisfy a given consonance condition.

## Description:
Performs pairwise comparison of all notes in the container using the provided test function. This method evaluates whether every combination of two notes in the container meets a specific consonance criterion defined by the test function.

The method is used internally by various consonance-checking methods such as `is_consonant()`, `is_perfect_consonant()`, and `is_imperfect_consonant()` to determine if all note pairs in the container satisfy the respective consonance requirements.

## Args:
    testfunc (callable): A function that takes two note name strings as arguments and returns a boolean indicating if they meet the consonance condition.
    param (any, optional): Additional parameter to pass to the test function. Defaults to None.

## Returns:
    bool: True if all pairs of notes satisfy the test condition; False if any pair fails the test.

## Raises:
    None explicitly raised - depends on the behavior of the testfunc parameter.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.notes contains valid note objects with a .name attribute
        - testfunc must accept note names as string arguments and return a boolean
        - When param is provided, testfunc must accept three arguments (including the parameter)
    
    Postconditions:
        - Method returns a boolean value indicating whether all note pairs satisfy the test condition
        - The original self.notes list remains unchanged

## Side Effects:
    None - This method performs no I/O operations or external service calls.

### `mingus.containers.note_container.NoteContainer.is_consonant` · *method*

## Summary:
Checks whether all pairs of notes in the container form consonant intervals.

## Description:
Determines if every combination of two notes in the container creates a consonant interval by testing all note pairs against the standard consonance criteria. This method evaluates whether the entire collection of notes forms a harmonically consonant set.

The method is part of a family of consonance-checking methods in NoteContainer that allow for different levels of consonance analysis. It specifically uses the standard definition of consonance that includes both perfect consonances (unisons, octaves, perfect fifths, and perfect fourths when included) and imperfect consonances (major and minor thirds, major and minor sixths).

Known callers include:
- Direct programmatic calls to check if a chord or note collection is consonant
- Internal use by the `is_dissonant()` method which negates the result of this method

This logic is encapsulated in its own method rather than being inlined because:
1. It provides a reusable interface for consonance checking
2. It follows the same pattern as other similar methods (`is_perfect_consonant`, `is_imperfect_consonant`) 
3. It leverages the existing `_consonance_test` infrastructure for consistent pairwise evaluation
4. It allows for easy extension or modification of consonance criteria

## Args:
    include_fourths (bool): Whether to consider perfect fourths as perfect consonances. Defaults to True. This parameter is passed directly to the underlying `intervals.is_consonant` function.

## Returns:
    bool: True if all pairs of notes in the container form consonant intervals; False if any pair forms a dissonant interval.

## Raises:
    None explicitly raised - depends on the behavior of the underlying `intervals.is_consonant` function.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must contain valid note objects with a `.name` attribute
        - All notes in the container must be properly initialized
        
    Postconditions:
        - The original note collection remains unchanged
        - Returns a boolean value indicating the overall consonance of the note set

## Side Effects:
    None - This method performs no I/O operations or external service calls.

### `mingus.containers.note_container.NoteContainer.is_perfect_consonant` · *method*

## Summary:
Checks whether all pairs of notes in the container form perfect consonant intervals.

## Description:
Determines if every combination of two notes in the container creates a perfect consonant interval by testing all note pairs against the perfect consonance criteria. This method evaluates whether the entire collection of notes forms a harmonically stable set based on perfect consonance definitions.

The method is part of a family of consonance-checking methods in NoteContainer that allow for different levels of consonance analysis. It specifically uses the standard definition of perfect consonance that includes unisons (0 semitones), perfect fifths (7 semitones), and optionally perfect fourths (5 semitones) when included.

Known callers include:
- Direct programmatic calls to check if a chord or note collection forms only perfect consonances
- Internal use by the `is_dissonant()` method which negates the result of this method

This logic is encapsulated in its own method rather than being inlined because:
1. It provides a reusable interface for perfect consonance checking
2. It follows the same pattern as other similar methods (`is_consonant`, `is_imperfect_consonant`) 
3. It leverages the existing `_consonance_test` infrastructure for consistent pairwise evaluation
4. It allows for easy extension or modification of perfect consonance criteria

## Args:
    include_fourths (bool): Whether to consider perfect fourths as perfect consonances. Defaults to True. This parameter is passed directly to the underlying `intervals.is_perfect_consonant` function.

## Returns:
    bool: True if all pairs of notes in the container form perfect consonant intervals; False if any pair forms a dissonant or imperfect consonant interval.

## Raises:
    None explicitly raised - depends on the behavior of the underlying `intervals.is_perfect_consonant` function.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must contain valid note objects with a `.name` attribute
        - All notes in the container must be properly initialized
        
    Postconditions:
        - The original note collection remains unchanged
        - Returns a boolean value indicating the overall perfect consonance of the note set

## Side Effects:
    None - This method performs no I/O operations or external service calls.

### `mingus.containers.note_container.NoteContainer.is_imperfect_consonant` · *method*

## Summary:
Tests whether all pairs of notes in the container form imperfect consonant intervals.

## Description:
Determines if every pair of notes in the note container creates an imperfect consonant interval. This method evaluates all possible combinations of two notes from the container and verifies that each pair forms an imperfect consonant (major third, minor third, major sixth, or minor sixth).

This method is part of the musical consonance analysis toolkit and is used to identify note collections that contain only imperfect consonant intervals, excluding perfect consonants (unison, perfect fifth, octave) and dissonant intervals.

## Args:
    None

## Returns:
    bool: True if all pairs of notes in the container form imperfect consonant intervals; False if any pair forms a perfect consonant or dissonant interval.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must contain valid note objects with a .name attribute
        - All notes in the container must be valid musical notes recognized by the notes module
    
    Postconditions:
        - Returns a boolean value indicating whether all note pairs satisfy the imperfect consonant condition
        - The original note collection remains unchanged

## Side Effects:
    None - This method performs no I/O operations or external service calls

### `mingus.containers.note_container.NoteContainer.is_dissonant` · *method*

## Summary:
Determines whether all pairs of notes in the container form dissonant intervals by negating the result of consonance checking.

## Description:
Checks if every combination of two notes in the container creates a dissonant interval rather than a consonant one. This method provides a convenient way to evaluate whether a collection of notes produces a harmonically dissonant sound.

The method is part of a family of consonance-checking methods in NoteContainer that allow for different levels of consonance analysis. It leverages the existing `is_consonant()` infrastructure but with inverted logic and modified parameter handling.

Known callers include:
- Direct programmatic calls to check if a chord or note collection is dissonant
- Internal use by application logic that needs to distinguish between consonant and dissonant note collections

This logic is its own method rather than being inlined because:
1. It provides a clear, semantic interface for dissonance checking
2. It maintains consistency with the existing consonance checking pattern
3. It allows for easy extension or modification of dissonance criteria
4. It separates concerns between consonance and dissonance evaluation

## Args:
    include_fourths (bool): Whether to consider perfect fourths as perfect consonances when determining dissonance. Defaults to False. This parameter is inverted before being passed to the underlying consonance checking function.

## Returns:
    bool: True if all pairs of notes in the container form dissonant intervals; False if any pair forms a consonant interval.

## Raises:
    None explicitly raised - depends on the behavior of the underlying `is_consonant` method.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must contain valid note objects with a `.name` attribute
        - All notes in the container must be properly initialized
        
    Postconditions:
        - The original note collection remains unchanged
        - Returns a boolean value indicating the overall dissonance of the note set

## Side Effects:
    None - This method performs no I/O operations or external service calls.

### `mingus.containers.note_container.NoteContainer.remove_note` · *method*

## Summary:
Removes notes from the container that match the specified note or note name, optionally filtering by octave.

## Description:
This method filters the notes in the container, removing any that match the provided note specification. When a note name string is provided, it removes all notes with that name. When a Note object is provided, it removes exact matches. The optional octave parameter allows for more precise filtering when removing by note name.

## Args:
    note (str or Note): Either a note name string (e.g., "C", "D#") or a Note object to remove from the container.
    octave (int): Optional octave number to filter by when note is a string. Defaults to -1 (no octave filtering).

## Returns:
    list[Note]: A new list containing the remaining notes after removal.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The method assumes self.notes is a list of Note objects.
    Postconditions: self.notes will contain only notes that do not match the removal criteria.

## Side Effects:
    None.

### `mingus.containers.note_container.NoteContainer.remove_notes` · *method*

## Summary:
Removes one or more notes from the container, supporting various input types for flexible note specification.

## Description:
This method provides a flexible interface for removing notes from a NoteContainer. It accepts different input types and delegates to the underlying remove_note method appropriately. The method is designed to handle single notes, collections of notes, or note names in various formats.

## Args:
    notes (str, Note, or iterable): A single note specification to remove, which can be:
        - A string representing a note name (e.g., "C", "D#")
        - A Note object to remove exactly
        - An iterable of note specifications to remove

## Returns:
    list[Note]: When removing a single note (string or Note object), returns the filtered list of remaining notes.
               When removing multiple notes (iterable), returns the updated self.notes list.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The container must have a notes attribute that is a list of Note objects.
    Postconditions: The notes attribute will contain only notes that do not match the removal criteria.

## Side Effects:
    None.

### `mingus.containers.note_container.NoteContainer.remove_duplicate_notes` · *method*

## Summary:
Removes duplicate notes from the container while preserving the order of first occurrences.

## Description:
Removes duplicate notes from the `self.notes` list by keeping only the first occurrence of each unique note. Duplicate detection is based on the `Note.__eq__` method, which compares notes by their integer representations (pitch and octave). This ensures that notes with the same pitch and octave, regardless of other attributes like velocity or channel, are treated as duplicates.

This method is separated from inline code because duplicate removal is a common operation that may be needed in various contexts within the music processing pipeline, such as after chord construction or interval calculations where duplicate notes might be inadvertently introduced.

## Args:
    None

## Returns:
    list[Note]: A list containing the deduplicated notes in their original order of appearance.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: 
    - The `self.notes` attribute must be a list-like object containing Note objects or objects that support equality comparison
    - All elements in `self.notes` must be comparable using the `==` operator
    
    Postconditions:
    - The `self.notes` attribute will contain no duplicate notes according to Note equality semantics
    - The order of notes in `self.notes` will match their first occurrence in the original list
    - The returned list will contain the same notes as the modified `self.notes` attribute

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.sort` · *method*

## Summary:
Sorts the notes in the container in ascending order based on their musical pitch.

## Description:
This method arranges the notes stored in the container according to their natural musical ordering, which is determined by the underlying Note class's comparison methods. The sorting is performed in-place, modifying the internal `notes` list directly. This method is typically called automatically when notes are added via `add_note()`.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The `self.notes` attribute must be a list containing Note objects that support comparison operations.
    Postconditions: The `self.notes` list will be sorted in ascending order by musical pitch.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.augment` · *method*

## Summary:
Applies augmentation to all notes in the container by adding sharps or removing flats from each note's name.

## Description:
This method applies the augmentation operation to every note contained in the NoteContainer. It iterates through all notes in the container and calls the individual note's augment() method, which modifies each note's name by either adding a sharp symbol (#) or removing a flat symbol (b). This is commonly used in music theory to convert flat notes to sharp notes or to add sharps to natural notes.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: Each note's name attribute in self.notes is modified

## Constraints:
    Preconditions: The NoteContainer must contain valid Note objects in self.notes
    Postconditions: All notes in the container will have been augmented (sharp added or flat removed)

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.diminish` · *method*

## Summary:
Reduces the accidental of all notes in the container by flattening them or removing sharps.

## Description:
Applies a diminishment operation to all notes contained in the NoteContainer. This method iterates through each note in the container and calls the individual note's diminish() method, which modifies each note's name by either adding a flat symbol ('b') or removing a sharp symbol ('#'). This operation is commonly used in music theory to convert sharp notes to flat notes or to flatten natural notes.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: Each note's name attribute in self.notes is modified

## Constraints:
    Preconditions: The NoteContainer must contain valid Note objects in self.notes
    Postconditions: All notes in the container will have been diminished (flat added or sharp removed)

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.determine` · *method*

## Summary
Determines the chord type and notation for the notes contained in this NoteContainer.

## Description
Analyzes the musical notes stored in this container and identifies the corresponding chord type using the mingus chord determination system. This method serves as a convenient interface to the core chord analysis functionality, delegating the actual determination process to `chords.determine()`.

The method is typically used during chord analysis or identification workflows where a collection of notes needs to be classified into standard musical chord forms. It's particularly useful when working with NoteContainers that represent musical chords or chord progressions.

## Args
    shorthand (bool): When True, returns abbreviated chord notation (e.g., 'CM' for C major). When False, returns full descriptive notation (e.g., 'C major'). Defaults to False.

## Returns
    list[str]: A list of strings representing possible chord identifications. For chords with 1 note, returns the note itself. For 2-note chords, returns interval notation. For larger chords, returns chord names based on the shorthand parameter. Returns an empty list for empty chords.

## Raises
    None explicitly raised.

## State Changes
    Attributes READ: self.notes (via get_note_names())
    Attributes WRITTEN: None

## Constraints
    Preconditions: The NoteContainer must contain valid musical notes that can be processed by the chord determination system.
    Postconditions: The returned list contains valid chord representations that accurately reflect the interval relationships between the notes in the container.

## Side Effects
    None.

### `mingus.containers.note_container.NoteContainer.transpose` · *method*

## Summary:
Transposes all notes in the container by the specified interval, modifying the container's notes in-place.

## Description:
This method applies a musical transposition to all notes contained within the NoteContainer. It iterates through each note in the container and calls the transpose method on each individual note, effectively shifting all notes by the same interval. This is useful for transposing entire chords or melodic fragments by a consistent interval.

## Args:
    interval (str): The musical interval to transpose by (e.g., "M2", "m3", "P5"). 
    up (bool): Direction of transposition. True for upward transposition, False for downward. Defaults to True.

## Returns:
    NoteContainer: Returns self to enable method chaining.

## Raises:
    None explicitly raised by this method, though underlying Note.transpose calls may raise exceptions from invalid intervals or note operations.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: Modifies the notes in self.notes in-place through calls to Note.transpose

## Constraints:
    Preconditions: The NoteContainer must contain valid Note objects in self.notes.
    Postconditions: All notes in the container are transposed by the specified interval and direction.

## Side Effects:
    None: This method only modifies the internal state of notes within the container and doesn't perform I/O or external service calls.

### `mingus.containers.note_container.NoteContainer.get_note_names` · *method*

## Summary:
Returns a list of unique note names from the notes contained in this container, preserving order of first appearance.

## Description:
Extracts the musical note names from all notes stored in this container, ensuring each name appears only once in the returned list. The order of note names in the result matches their first occurrence in the container's note collection.

This method is particularly useful for chord identification and musical analysis operations that require a clean list of unique note names without duplicates.

## Args:
    None

## Returns:
    list[str]: A list of unique note name strings in the order of their first appearance in the container's notes collection.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The container must have a notes attribute containing Note objects with name attributes
    Postconditions: The returned list contains only unique note names in order of first appearance

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__repr__` · *method*

## Summary:
Returns the string representation of the note container's internal list of notes.

## Description:
This special method provides a human-readable string representation of the NoteContainer object. It is automatically invoked when the built-in `repr()` function is called on a NoteContainer instance or when the object appears in interactive Python sessions. The method returns a string representation of the internal `notes` list, which contains all Note objects currently stored in the container.

## Args:
    None

## Returns:
    str: A string representation of the internal `notes` list, showing all Note objects contained in the container in their current order.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The NoteContainer instance must be properly initialized
    - The `self.notes` attribute must be accessible and contain a list of Note objects
    
    Postconditions:
    - The returned string accurately represents the current state of the note container
    - The method does not modify any instance attributes

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__getitem__` · *method*

## Summary:
Retrieves a note from the container at the specified index position.

## Description:
Provides indexed access to notes stored in the NoteContainer, enabling standard Python list-style indexing operations. This method implements the `__getitem__` protocol, allowing users to access individual notes using bracket notation (e.g., `container[0]`, `container[-1]`).

The method is called during indexing operations such as `container[index]` and delegates directly to the underlying `self.notes` list's indexing mechanism. This enables seamless integration with Python's container protocols and supports all standard list indexing behaviors including negative indices.

## Args:
    item (int): Index position of the note to retrieve. Can be positive (0-based from start) or negative (from end). Must be within the bounds of the notes list.

## Returns:
    Note: The Note object at the specified index position in the container's notes list.

## Raises:
    IndexError: When the specified index is out of range for the notes list.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The item parameter must be a valid integer index
    - The index must be within the valid range [0, len(self.notes)) or [-len(self.notes), -1]
    
    Postconditions:
    - Returns the Note object at the specified index position
    - Does not modify the container's state

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__setitem__` · *method*

*No documentation generated.*

### `mingus.containers.note_container.NoteContainer.__add__` · *method*

## Summary:
Adds notes to the current NoteContainer instance and returns self for method chaining.

## Description:
Implements the `+` operator for NoteContainer objects, enabling intuitive syntax for combining notes. This method allows for fluent interface patterns where multiple notes can be added sequentially using the addition operator.

## Args:
    notes: Can be a single note, list of notes, or another NoteContainer object containing notes to be added to this container.

## Returns:
    NoteContainer: Returns self to enable method chaining operations.

## Raises:
    UnexpectedObjectError: When attempting to add an object that is not a valid note representation.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes (modified by add_notes call)

## Constraints:
    Preconditions: The notes parameter must be compatible with the add_notes method's expectations.
    Postconditions: The notes from the input parameter are added to the current container's notes list, maintaining sorted order.

## Side Effects:
    Mutates the internal notes list of the NoteContainer instance.

### `mingus.containers.note_container.NoteContainer.__sub__` · *method*

## Summary:
Removes specified notes from the container and returns the modified container.

## Description:
Implements the subtraction operator (-) for NoteContainer objects. This method allows for intuitive syntax to remove notes from a container using the minus operator. It delegates to the internal `remove_notes` method to handle the actual removal logic and returns the modified container to enable method chaining.

## Args:
    notes: Can be a single note (string name or Note object), or a collection of notes to remove from the container.

## Returns:
    NoteContainer: The same container instance with the specified notes removed, enabling method chaining.

## Raises:
    None explicitly raised, but may propagate exceptions from underlying methods like `remove_notes`.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes (modified in-place)

## Constraints:
    Preconditions: The container must be initialized and the notes parameter must be compatible with the remove_notes method's expectations.
    Postconditions: The container will have the specified notes removed from its internal notes list.

## Side Effects:
    Mutates the internal notes list of the container in-place.

### `mingus.containers.note_container.NoteContainer.__len__` · *method*

## Summary:
Returns the number of notes contained in the NoteContainer instance.

## Description:
This special method implements the Python container protocol by returning the count of notes stored in the container. It enables the use of Python's built-in `len()` function on NoteContainer instances, providing a standard interface for determining container size.

## Args:
    None: This method takes no arguments beyond the implicit `self` parameter.

## Returns:
    int: The number of Note objects currently stored in the `self.notes` list attribute.

## Raises:
    None: This method does not raise any exceptions under normal circumstances.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `self.notes` attribute must be a list-like object that supports the `len()` function.
    Postconditions: The method returns an integer representing the count of elements in `self.notes`.

## Side Effects:
    None: This method is read-only and does not modify any object state or cause external effects.

### `mingus.containers.note_container.NoteContainer.__eq__` · *method*

## Summary:
Checks if all notes in this NoteContainer are present in another container, implementing a subset relationship check.

## Description:
Implements the equality comparison operator (`==`) for NoteContainer objects by verifying that every note in the current container (self) is present in the other container (other). This method does not implement full set equality but rather checks if self is a subset of other. For true equality, both self ⊆ other and other ⊆ self must hold.

This method is called during equality comparisons between NoteContainer instances, such as when using `container1 == container2`. It leverages Python's container protocol to check membership using the `in` operator.

## Args:
    other (NoteContainer or compatible container): Another container-like object to compare against this NoteContainer.

## Returns:
    bool: True if all notes in self are present in other, False otherwise.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None - this method only accesses container contents through iteration
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions:
    - The other parameter must support the container protocol (have `__contains__` method)
    - Both self and other must be iterable (support `for x in self` and `x in other`)
    - Behavior is undefined if other does not properly implement membership testing
    
    Postconditions:
    - Returns a boolean value indicating subset relationship (self ⊆ other)
    - The comparison is not symmetric in the traditional sense of equality
    - May return True even when containers have different sizes

## Side Effects:
    None

