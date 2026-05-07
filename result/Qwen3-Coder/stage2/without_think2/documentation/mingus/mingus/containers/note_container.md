# `note_container.py`

## `mingus.containers.note_container.NoteContainer` · *class*

## Summary:
A container class for managing collections of musical notes, providing methods for note manipulation and chord progression handling.

## Description:
The NoteContainer class serves as a container for musical notes, offering functionality to add, remove, and manipulate notes within a collection. It provides methods for creating note collections from chord shorthands, interval relationships, and musical progressions. The class supports basic operations like sorting, transposition, and removing duplicate notes, making it useful for organizing musical note sequences in composition and analysis applications.

## State:
- notes (list): A list of Note objects stored in the container. The list is maintained in sorted order.
  - Type: list of mingus.containers.note.Note objects
  - Valid range: Empty list or list containing Note objects
  - Invariant: The notes list is always kept sorted after modifications

## Lifecycle:
- Creation: Instantiate with optional initial notes via `__init__(notes=None)` or use factory methods like `from_chord_shorthand()` or `from_progression_shorthand()`
- Usage: Add/remove notes using `add_note()`, `add_notes()`, `remove_note()`, `remove_notes()`. Perform operations like sorting, transposition, and duplicate removal
- Destruction: Uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[NoteContainer.__init__] --> B[empty()]
    B --> C[add_notes()]
    D[from_chord_shorthand] --> E[empty() + add_notes()]
    F[from_progression_shorthand] --> G[empty() + add_notes()]
    H[add_note] --> I[Note construction + sorting]
    J[transpose] --> K[note.transpose()]
    L[remove_note] --> M[filter notes]
    N[get_note_names] --> O[extract note names]
    P[sort] --> Q[notes.sort()]
```

## Raises:
- UnexpectedObjectError: Raised when attempting to add an object that is not a Note instance
- NoteFormatError: Raised when invalid note names are encountered during chord or progression parsing
- FormatError: Raised when unknown chord shorthand notation is encountered

## Example:
```python
# Create a container and add notes
container = NoteContainer()
container.add_note("C", 4)
container.add_note("E", 4)
container.add_note("G", 4)

# Create from chord shorthand
container.from_chord_shorthand("C")
print(container)  # [C-4, E-4, G-4]

# Transpose up a perfect fifth
container.transpose("P5")
print(container)  # [G-4, B-4, D-5]

# Remove a note
container.remove_note("G", 4)
print(container)  # [B-4, D-5]
```

### `mingus.containers.note_container.NoteContainer.__init__` · *method*

## Summary:
Initializes a NoteContainer object by clearing existing notes and adding a collection of notes.

## Description:
The `__init__` method sets up a NoteContainer instance by first clearing any existing notes and then populating it with the provided notes. This method ensures a clean initialization state regardless of whether notes are provided during construction. It delegates the actual note handling to the `empty()` and `add_notes()` methods, making the initialization process modular and reusable.

This logic is encapsulated in its own method to provide a clear separation of concerns, ensuring that initialization follows the same pattern as other operations on the container. It also allows for consistent behavior when creating new containers or resetting existing ones. The method handles various input types for notes, including lists, individual notes, and chord shorthand representations.

## Args:
    notes (list, optional): A collection of notes to initialize the container with. Defaults to None, which results in an empty container. Can accept various formats including lists of notes, individual notes, or note names as strings.

## Returns:
    None

## Raises:
    UnexpectedObjectError: If any note in the provided collection is not a valid Note object.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.notes: Reset to empty list via `empty()` call, then populated with provided notes

## Constraints:
    Preconditions: None
    Postconditions: The container will have an empty state before adding notes, and the notes parameter can be any iterable of note-like objects.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.empty` · *method*

## Summary:
Clears all notes from the note container, leaving it empty.

## Description:
This method resets the internal notes list to an empty list, effectively removing all notes from the container. It is primarily used as a utility method to prepare a NoteContainer for reuse or to clear its contents before populating it with new notes.

The method is called during initialization of NoteContainer instances and is also invoked by several factory methods like `from_chord_shorthand`, `from_interval_shorthand`, and `from_progression_shorthand` to ensure clean state before adding new notes.

## Args:
    None

## Returns:
    None

## Raises:
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
Adds a note to the container, handling string inputs by converting them to Note objects and maintaining sorted order.

## Description:
The `add_note` method adds a musical note to the NoteContainer's collection. It accepts various input formats including Note objects, note names as strings, or note specifications with octave and dynamics. When a string is provided, it creates a Note object with appropriate octave assignment based on existing notes in the container. The method ensures no duplicate notes are added and maintains the notes in sorted order.

This method is called during container initialization and when adding individual notes to a container. It serves as the primary mechanism for note insertion while enforcing uniqueness and proper ordering.

## Args:
    note (str, Note, or other): The note to add, which can be a string name (e.g., "C", "D#"), a Note object, or other note-like object.
    octave (int, optional): The octave number for string-based note specifications. Defaults to None.
    dynamics (dict, optional): Dynamics information for the note. Defaults to None.

## Returns:
    list[Note]: The updated list of notes in the container, sorted in ascending order.

## Raises:
    UnexpectedObjectError: When the note parameter is not a valid Note object or note-like object.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions:
    - The note parameter must be either a Note object or a valid note specification (string, integer, etc.)
    - If note is a string, octave must be specified or the container must not be empty
    - Dynamics parameter must be a dictionary if provided
    
    Postconditions:
    - The note is added to self.notes if not already present
    - self.notes remains sorted in ascending order
    - Duplicate notes are not added

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. It only modifies the internal state of self.notes.

### `mingus.containers.note_container.NoteContainer.add_notes` · *method*

## Summary:
Adds multiple notes to the container, supporting various input formats including Note objects, note names, and nested structures.

## Description:
The `add_notes` method provides a flexible way to add multiple notes to a NoteContainer. It handles various input types including NoteContainer objects, individual Note objects, string representations of notes, and lists of notes with optional octave/dynamics specifications. This method acts as a unified entry point for adding collections of notes while delegating individual note processing to the `add_note` method.

The method is designed to be called during container initialization or when programmatically adding multiple notes. It processes different input formats through a series of type checks and dispatches to appropriate handling logic. The method ensures that all notes are properly added to the container while maintaining the sorted order and avoiding duplicates.

## Args:
    notes: A collection of notes to add, which can be:
        - A NoteContainer object with a notes attribute (iterates through its notes)
        - A single Note object with a name attribute (adds directly)
        - A string representing a note name (converts to Note and adds)
        - An iterable of notes, where each element can be:
          - A string note name
          - A Note object
          - A list containing note information [note_name, octave] or [note_name, octave, dynamics]

## Returns:
    list[Note]: The updated list of notes in the container, sorted in ascending order.

## Raises:
    UnexpectedObjectError: When a note object doesn't have a valid name attribute or is not a recognized note type.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (through calls to add_note)

## Constraints:
    Preconditions:
    - The notes parameter must be iterable or have the appropriate attributes for type checking
    - Individual note objects must be valid Note objects or convertible to Note objects
    - When providing note information as lists, the list must contain valid note specifications
    
    Postconditions:
    - All valid notes from the input are added to self.notes
    - Duplicate notes are not added to the container
    - Notes remain sorted in ascending order after addition

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. It only modifies the internal state of self.notes through calls to add_note.

### `mingus.containers.note_container.NoteContainer.from_chord` · *method*

## Summary:
Initializes the note container with notes derived from a chord shorthand string.

## Description:
This method serves as a convenience wrapper that converts a chord shorthand representation into individual notes and populates the note container. It delegates the actual parsing and conversion to the `from_chord_shorthand` method, which clears the existing notes and adds the parsed chord notes. Common shorthand examples include "C", "G7", "Am", "Fmaj7", "Dm7", etc.

## Args:
    shorthand (str): A string representing a chord in shorthand notation (e.g., "Cmaj7", "G7", "Am"). Valid shorthand includes basic triads, seventh chords, and extended chords.

## Returns:
    NoteContainer: The current instance with its notes replaced by those derived from the chord shorthand.

## Raises:
    NoteFormatError: If the shorthand contains an unrecognized note.
    FormatError: If the shorthand format is not recognized.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The shorthand string must be a valid chord shorthand notation.
    Postconditions: The note container's notes attribute will contain the notes of the specified chord.

## Side Effects:
    Mutates the self.notes attribute by clearing it and replacing it with new notes.

### `mingus.containers.note_container.NoteContainer.from_chord_shorthand` · *method*

## Summary:
Initializes the note container with notes derived from a chord shorthand string, clearing any existing notes.

## Description:
The `from_chord_shorthand` method serves as a factory method to populate a NoteContainer with notes representing a musical chord specified in shorthand notation. It clears the container's existing notes and replaces them with the notes from the specified chord. This method is part of the NoteContainer's chord creation utilities and is typically used when building musical structures programmatically.

This method is called by the `from_chord` method as an alias, making it part of the standard interface for creating chord-based note containers. The method leverages the core `chords.from_shorthand` function to parse the shorthand notation and convert it into a list of note specifications, which are then added to the container.

## Args:
    shorthand (str): A string representing a chord in shorthand notation (e.g., "Cmaj", "Am", "G7").

## Returns:
    NoteContainer: The current instance with its notes replaced by those from the parsed chord, enabling method chaining.

## Raises:
    NoteFormatError: When the shorthand string contains an unrecognized note.
    FormatError: When the shorthand string represents an unknown chord type.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (through calls to empty() and add_notes())

## Constraints:
    Preconditions:
    - The shorthand parameter must be a valid string representing a chord in shorthand notation
    - The chord shorthand must be recognizable by the underlying chords.from_shorthand function
    
    Postconditions:
    - The container's notes list is cleared and replaced with notes from the chord
    - The returned container instance is the same object (self) for method chaining

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. It only modifies the internal state of self.notes.

### `mingus.containers.note_container.NoteContainer.from_interval` · *method*

## Summary:
Creates a NoteContainer with two notes separated by a specified musical interval, starting from a given note.

## Description:
This method generates a container with exactly two notes: the starting note and another note positioned at a specific musical interval above or below it. It serves as a convenient interface for creating interval-based musical constructs by delegating to the underlying `from_interval_shorthand` method. The method is particularly useful in musical composition and analysis workflows where interval relationships between notes need to be quickly established.

## Args:
    startnote (Note or str): The base note from which the interval is calculated. Can be a Note object or a string representation (e.g., "C", "D#").
    shorthand (str): A string representing the musical interval (e.g., 'm3', 'P5'). See mingus.core.intervals for valid interval specifications.
    up (bool): Direction of transposition, True for upward, False for downward. Defaults to True.

## Returns:
    NoteContainer: The same NoteContainer instance with two notes added - the start note and the interval note.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (through calls to empty() and add_notes())

## Constraints:
    Preconditions: The startnote must be a valid Note object or string representation, and the shorthand must represent a valid musical interval.
    Postconditions: The NoteContainer will contain exactly two notes - the original start note and the transposed note.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.from_interval_shorthand` · *method*

## Summary:
Creates a two-note container with a starting note and its transposed counterpart using interval shorthand notation.

## Description:
This method constructs a NoteContainer with exactly two notes: the original startnote and a transposed version derived from applying an interval shorthand to the startnote. It's designed to facilitate quick creation of interval-based note pairs for musical analysis, composition, or educational purposes. The method handles both Note objects and string representations of notes as input for the startnote parameter.

The method is implemented as a dedicated utility to provide a clean, reusable interface for creating interval-based note pairs. It encapsulates the workflow of clearing the container, creating a transposed note, and adding both notes to the container in a single operation.

## Args:
    startnote (Note or str): The base note for the interval calculation. Can be either a Note object or a string representation of a note (e.g., "C", "D#").
    shorthand (str): A string representing the musical interval to transpose by (e.g., 'm3', 'P5').
    up (bool): Direction of transposition, True for upward, False for downward. Defaults to True.

## Returns:
    NoteContainer: The current NoteContainer instance with two notes added: the original startnote and its transposed version.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes (through calls to empty() and add_notes())

## Constraints:
    Preconditions: 
    - The startnote parameter must be either a Note object or a valid string representation of a note
    - The shorthand parameter must be a valid interval shorthand string
    - The NoteContainer must be properly initialized
    
    Postconditions:
    - The container will contain exactly two notes: the original startnote and its transposed version
    - The container's notes list will be sorted in ascending order
    - The original startnote remains unchanged in the container

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.from_progression` · *method*

## Summary:
Initializes the note container with notes derived from a musical progression shorthand in a specified key.

## Description:
This method converts a musical progression expressed in Roman numeral shorthand into actual chord notes and populates the note container with those notes. It serves as a convenient interface for building note containers from harmonic progressions, delegating the actual conversion logic to the internal `from_progression_shorthand` method.

## Args:
    shorthand (str): A string representing a musical progression using Roman numerals (e.g., "I", "IV", "V"). May also accept a list of such strings.
    key (str): The musical key in which to interpret the Roman numerals. Defaults to "C".

## Returns:
    NoteContainer or bool: The current instance with notes populated from the progression. Returns False if the progression produces no valid chords.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes

## Constraints:
    - Preconditions: The shorthand argument must be a valid Roman numeral representation or list of such representations. The key must be a recognized musical key.
    - Postconditions: The note container will contain notes from the first chord of the progression, or remain empty if no valid chords are produced.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.from_progression_shorthand` · *method*

## Summary:
Initializes the note container with notes derived from the first chord of a musical progression shorthand.

## Description:
Converts a musical progression shorthand (in Roman numeral notation) into actual note objects and populates the note container with the notes from the first chord in the progression. This method serves as a factory method for creating note containers from harmonic progressions, making it easy to work with chord-based musical concepts in a note-oriented container.

The method is called during the lifecycle of a NoteContainer when initializing from a musical progression, typically in the context of music theory applications or chord progression analysis. It leverages the progressions module to parse Roman numeral notation and convert it into playable musical notes.

## Args:
    shorthand (str): A string representing a musical progression in Roman numeral notation (e.g., "I", "IV", "V7", "ii-V-I").
    key (str): The musical key in which to interpret the Roman numerals. Defaults to "C".

## Returns:
    NoteContainer or bool: Returns the NoteContainer instance (self) if successful, or False if the progression produces no valid chords.

## Raises:
    None explicitly raised by this method, though underlying functions may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.notes: Cleared and populated with notes from the first chord of the progression

## Constraints:
    Preconditions: 
    - The shorthand parameter must be a valid Roman numeral progression string
    - The key parameter must be a valid musical key string
    - The NoteContainer must be properly initialized
    
    Postconditions:
    - The container's notes are cleared before adding new notes
    - If the progression results in no valid chords, the container remains empty and False is returned
    - If successful, the container contains notes from the first chord of the progression

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. It only modifies the internal state of self.notes.

### `mingus.containers.note_container.NoteContainer._consonance_test` · *method*

## Summary:
Tests whether all pairs of notes in the container satisfy a given consonance condition.

## Description:
This private method performs a systematic pairwise comparison of all notes in the container using a supplied consonance testing function. It evaluates every unique pair of notes to determine if they meet the specified consonance criteria. The method implements a nested loop approach where each note is compared against all subsequent notes in the container.

The method is used internally by several public consonance-checking methods such as `is_consonant()`, `is_perfect_consonant()`, and `is_imperfect_consonant()` to perform their respective consonance evaluations. By abstracting the pairwise comparison logic into this private method, the code avoids duplication and ensures consistent application of consonance testing across different interval types.

## Args:
    testfunc (callable): A function that takes note names as arguments and returns a boolean indicating consonance.
    param (any, optional): Additional parameter to pass to testfunc. Defaults to None.

## Returns:
    bool: True if all pairs of notes in the container satisfy the consonance test, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must have at least one note
        - The testfunc must accept note names as arguments and return a boolean
        - If param is provided, testfunc must accept the additional parameter
    Postconditions:
        - The method returns a boolean value indicating whether all note pairs pass the test
        - The original notes in the container remain unchanged

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.is_consonant` · *method*

## Summary:
Checks if all note pairs in the container form consonant intervals, optionally including perfect fourths.

## Description:
This method determines whether all pairs of notes in the container form consonant intervals according to Western music theory. It leverages the internal `_consonance_test` method to systematically compare every unique pair of notes in the container using the `intervals.is_consonant` function. The method supports an optional parameter to control whether perfect fourths are considered consonant intervals.

The method is part of a suite of consonance-checking utilities in the NoteContainer class, providing a convenient way to assess the harmonic properties of a collection of musical notes. It's particularly useful for analyzing chord voicings, melodic intervals, and harmonic progressions.

## Args:
    include_fourths (bool): Flag indicating whether perfect fourths (5 semitones) should be considered as perfect consonances. Defaults to True.

## Returns:
    bool: True if all pairs of notes in the container form consonant intervals, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must have at least one note
        - All notes in the container must be valid Note objects
    Postconditions:
        - The method returns a boolean value indicating whether all note pairs pass the consonance test
        - The original notes in the container remain unchanged

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.is_perfect_consonant` · *method*

## Summary:
Tests whether all pairs of notes in the container form perfect consonances, optionally including perfect fourths.

## Description:
Determines if every pair of notes in the note container forms a perfect consonance according to Western music theory. This method leverages the internal `_consonance_test` mechanism to systematically compare all unique pairs of notes in the container. It specifically uses the `intervals.is_perfect_consonant` function to evaluate each pair, making it suitable for musical analysis where identifying perfect consonant intervals is crucial.

The method serves as a specialized interface for checking perfect consonance conditions within a collection of musical notes. It provides a convenient way to validate that all intervals between notes in a chord or melodic sequence qualify as perfect consonances, with the option to include or exclude perfect fourths based on musical convention.

## Args:
    include_fourths (bool): Flag indicating whether perfect fourths (5 semitones) should be considered as perfect consonances. Defaults to True.

## Returns:
    bool: True if all pairs of notes in the container form perfect consonances, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must have at least one note
        - All notes in the container must be valid musical notes
    Postconditions:
        - The method returns a boolean value indicating whether all note pairs pass the perfect consonance test
        - The original notes in the container remain unchanged

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.is_imperfect_consonant` · *method*

## Summary:
Tests whether all pairs of notes in the container form imperfect consonant intervals.

## Description:
Determines if every pair of notes within the container forms an imperfect consonant interval (major third, minor third, major sixth, or minor sixth). This method leverages the private `_consonance_test` method to systematically evaluate all unique note pairs against the `intervals.is_imperfect_consonant` function.

The method is part of a suite of consonance-checking utilities that allow musical analysis of note containers. It specifically identifies harmonically pleasing intervals that are neither perfect nor dissonant, but fall into the category of imperfect consonances commonly used in Western music theory.

## Args:
    None

## Returns:
    bool: True if all pairs of notes in the container form imperfect consonant intervals, False otherwise.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must have at least one note
        - All notes in the container must be valid Note objects
    Postconditions:
        - The method returns a boolean value indicating whether all note pairs pass the imperfect consonance test
        - The original notes in the container remain unchanged

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.is_dissonant` · *method*

## Summary:
Determines whether the note container contains dissonant intervals by negating the result of the consonant check.

## Description:
This method evaluates whether the collection of notes in the container forms dissonant intervals. It achieves this by inverting the result of the `is_consonant` method, effectively providing a direct way to check for dissonance. The method accepts an optional parameter to control whether perfect fourths are treated as consonant intervals, which is passed through to the underlying consonance check.

The method exists as a separate utility to provide symmetry with the `is_consonant` method and to allow developers to easily check for dissonant intervals without having to manually negate the consonance result. This design choice improves code readability and maintains consistency with the existing API pattern.

## Args:
    include_fourths (bool): Flag indicating whether perfect fourths (5 semitones) should be considered as perfect consonances. Defaults to False.

## Returns:
    bool: True if the container contains at least one dissonant interval, False if all intervals are consonant.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The container must have at least one note
        - All notes in the container must be valid Note objects
    Postconditions:
        - The method returns a boolean value indicating whether any note pairs in the container form dissonant intervals
        - The original notes in the container remain unchanged

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.remove_note` · *method*

## Summary:
Removes notes from the container matching the specified note name or note object, with optional octave filtering.

## Description:
This method removes all notes from the container that match either a note name (string) or a Note object. When removing by note name, it can optionally filter by octave. When removing by a Note object, it performs strict object identity comparison. This method is typically called when a user wants to remove specific notes from a collection, such as when constructing chord progressions or modifying existing note sets.

## Args:
    note (str or Note): The note name (as string) or Note object to remove from the container.
    octave (int): Optional octave number to filter removals when note is a string. Defaults to -1 (no filtering).

## Returns:
    list[Note]: A new list containing the remaining notes after removal.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The note parameter must be either a string (representing a note name) or a Note object.
    Postconditions: The self.notes attribute will contain only notes that do not match the specified note (and octave, if applicable).

## Side Effects:
    None.

### `mingus.containers.note_container.NoteContainer.remove_notes` · *method*

## Summary:
Removes one or more notes from the container, supporting single notes, note names, or collections of notes.

## Description:
This method provides flexible removal of notes from the container. It accepts a single note (either as a string name or Note object) or a collection of notes, and removes all matching entries. When a single note is provided as a string, it delegates to remove_note() for handling. When a Note object is provided, it also delegates to remove_note(). For collections of notes, it iterates and removes each note individually. This method is typically used during note manipulation workflows where specific notes need to be excluded from a container.

## Args:
    notes (str or Note or iterable): A single note represented as a string name, a Note object, or an iterable of such notes to remove.

## Returns:
    list[Note]: The updated list of notes in the container after removal operations. When removing a single note, returns the result of remove_note(). When removing multiple notes, returns self.notes.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The notes parameter must be either a string, a Note object, or an iterable of such objects.
    Postconditions: The self.notes attribute will contain only notes that do not match the specified note(s) being removed.

## Side Effects:
    None.

### `mingus.containers.note_container.NoteContainer.remove_duplicate_notes` · *method*

## Summary:
Removes duplicate notes from the note container while preserving order and returns the deduplicated list.

## Description:
This method eliminates duplicate notes from the internal `notes` list of the NoteContainer instance, maintaining the original order of unique elements. It is designed to clean up note collections that may have been populated with duplicates through various operations like chord construction or note addition.

The method is implemented as a separate function because it performs a specific data cleaning operation that could be reused in multiple contexts, and it provides a clear interface for deduplicating notes without requiring external logic to manage the process.

## Args:
    None

## Returns:
    list[Note]: A list containing the unique notes from the container, preserving their original order.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The `self.notes` attribute must be a list-like object containing Note objects or objects that support equality comparison.
    Postconditions: The `self.notes` attribute will contain only unique notes in their original order, and the returned list will match this deduplicated collection.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.sort` · *method*

## Summary:
Sorts the notes in the note container in ascending order by pitch.

## Description:
This method sorts the internal list of notes in-place using Python's built-in sort algorithm. It is typically called after adding notes to ensure they are arranged in proper ascending pitch order. The sorting is performed on the `self.notes` attribute, which contains Note objects ordered by their pitch values.

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
    Postconditions: The `self.notes` list will be sorted in ascending order by pitch value.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.augment` · *method*

## Summary:
Increases the pitch of all notes in the container by one semitone through augmentation.

## Description:
The augment method applies the augmentation operation to each note in the container, raising their pitches by one semitone. This method serves as a convenient bulk operation for applying the same transformation to all notes contained within the NoteContainer instance.

This logic is implemented as a separate method rather than being inlined because:
1. It provides a clean, semantic interface for applying pitch augmentation to entire note collections
2. It maintains consistency with other similar operations like diminish() that operate on all notes
3. It allows for potential future extensions or validation logic around the bulk operation

The method delegates to each individual note's augment() method, which increases each note's pitch by one semitone by modifying its name attribute.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.notes (iterable of Note objects)
    Attributes WRITTEN: Each note's name attribute in self.notes (via n.augment())

## Constraints:
    Preconditions: The NoteContainer must contain valid Note objects in its notes attribute. Each note must support the augment() method.
    Postconditions: All notes in the container will have been augmented (pitch increased by one semitone).

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.diminish` · *method*

## Summary:
Reduces the pitch of all notes in the container by one semitone using the diminish operation.

## Description:
This method applies the diminish operation to each note in the container's notes list. It systematically flattens all notes in the container, effectively lowering their pitch by one semitone. The method is typically used in musical contexts where chord or interval modifications require reducing the pitch of all constituent notes. This method serves as a convenient bulk operation for applying the diminish transformation to an entire note container.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: Individual notes in self.notes (via n.diminish())

## Constraints:
    Preconditions: The container must contain valid Note objects in its notes attribute.
    Postconditions: All notes in the container will have been diminished by one semitone.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.determine` · *method*

## Summary:
Determines the chord name or shorthand representation for the notes contained in this NoteContainer.

## Description:
This method identifies the musical chord represented by the collection of notes stored in the NoteContainer. It extracts the unique note names from the container's notes and delegates the actual chord determination logic to the `chords.determine` function from the mingus.core module.

The method is designed to be a clean interface for chord identification that abstracts away the complexity of determining chord names from raw note data. It leverages the existing chord determination infrastructure in the mingus library while providing a convenient way to identify chords from NoteContainer objects.

Typical usage includes identifying what chord is represented by a collection of notes, such as when analyzing musical passages or building chord progression tools. The method supports both full chord names (like "C major seventh") and shorthand notation (like "C7").

## Args:
    shorthand (bool): When True, returns abbreviated chord names like 'C7' or 'Dm'. When False, returns full names with inversion descriptions. Defaults to False

## Returns:
    list[str]: A list of possible chord representations (as strings) when successful. Returns an empty list for empty input chords, or the original chord for single-note chords. Each entry in the list represents a possible chord name based on different inversions or polychord combinations of the input notes.

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The NoteContainer must contain valid note objects with name attributes
    Postconditions: The returned list contains at least one chord representation (except for empty chords)

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.transpose` · *method*

## Summary:
Transposes all notes in the container by the specified interval, modifying them in-place and returning the container itself.

## Description:
The transpose method applies a musical interval transposition to every note contained within the NoteContainer. It iterates through all notes in the container and calls the transpose method on each individual note, effectively shifting all pitches by the same interval. This method is designed to provide a convenient way to transpose entire musical structures (chords, scales, progressions) uniformly.

This logic is implemented as a separate method rather than being inlined because it enables bulk transposition of musical elements while maintaining consistency across all notes in the container. It also provides a fluent interface by returning self, allowing for method chaining.

## Args:
    interval (str): A string representing the musical interval (e.g., 'm3', 'P5') to transpose by
    up (bool): Direction of transposition, True for upward, False for downward. Defaults to True

## Returns:
    NoteContainer: Returns self to enable method chaining

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None (notes themselves are modified in-place, but the container's notes attribute is not reassigned)

## Constraints:
    Preconditions: The container must contain valid Note objects, and the interval must be properly formatted for transposition
    Postconditions: All notes in the container will have been transposed by the specified interval

## Side Effects:
    Mutates the individual Note objects contained within the container by calling their transpose method

### `mingus.containers.note_container.NoteContainer.get_note_names` · *method*

## Summary:
Returns a list of unique note names from the container, preserving the order of first appearance.

## Description:
Extracts note names from all notes in the container, removing duplicates while maintaining the order in which each unique note name first appears. This method provides a clean view of the distinct note names contained within the container without modifying the original notes list.

The method is implemented as a separate utility to allow callers to inspect the note composition without side effects, making it useful for analysis, display, or further processing of note information.

## Args:
    None

## Returns:
    list[str]: A list of unique note names in the order of their first appearance in the container's notes collection.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The container must have a notes attribute that is iterable and contains objects with a name attribute.
    Postconditions: The returned list contains only unique note names in the order of their first appearance.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__repr__` · *method*

## Summary:
Returns a string representation of the note container's internal note list.

## Description:
This method provides a string representation of the NoteContainer's internal `notes` attribute, which is a list of Note objects. It is invoked during debugging or when the object needs to be displayed as a string, such as in print statements or logging contexts. The method serves as a standard Python magic method to define the object's string representation.

## Args:
    None

## Returns:
    str: A string representation of the internal `self.notes` list, which contains Note objects.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have a `notes` attribute that is iterable.
    Postconditions: The returned string accurately reflects the current state of `self.notes`.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__getitem__` · *method*

## Summary:
Retrieves a note or sublist of notes from the container's internal note collection using indexing.

## Description:
This method implements Python's sequence protocol by providing indexed access to the notes stored in the NoteContainer's internal `notes` list. It allows users to retrieve individual notes or slices of notes using standard Python indexing syntax (integers or slices). This method is essential for iterating over notes and accessing specific elements within the container.

## Args:
    item (int or slice): The index or slice object used to select notes from the internal notes list. Can be a positive or negative integer for single element access, or a slice object for sublists.

## Returns:
    Note or list[Note]: Returns a single Note object when item is an integer index, or a list of Note objects when item is a slice. The returned list maintains the same order as the original notes list.

## Raises:
    IndexError: When item is out of bounds for the internal notes list. This occurs when accessing an index that doesn't exist or when a slice extends beyond the list boundaries.

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The internal `self.notes` list must be initialized and contain at least one note if accessing by index.
    Postconditions: The returned value preserves the original note ordering and types, with proper handling of negative indices and slice bounds.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__setitem__` · *method*

## Summary:
Sets a note in the container at the specified index, converting string representations to Note objects when necessary.

## Description:
This method provides indexed assignment functionality for NoteContainer objects, allowing users to set notes at specific positions in the container. When a string is provided as the value, it automatically converts it to a Note object before storing it. This enables convenient direct assignment of note names as strings while maintaining internal consistency with Note objects.

The method is separated from inline logic to provide a clean interface for container manipulation and to handle the automatic conversion of string representations to proper Note objects. This design choice improves usability by allowing string-based note specification while preserving the internal type consistency of the container.

## Args:
    item (int): The index position where the note should be set
    value (str or Note): The note value to set, either as a string name or Note object

## Returns:
    list[Note]: The updated notes list after setting the value

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.notes

## Constraints:
    Preconditions: The item parameter must be a valid index for the notes list
    Postconditions: The notes list will contain the provided value at the specified index

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__add__` · *method*

## Summary:
Adds notes to the note container and returns the container instance for chaining operations.

## Description:
This method enables fluent interface patterns by allowing note addition operations to be chained together. It delegates the actual note addition logic to the `add_notes` method and returns `self` to support method chaining. This approach allows for expressive syntax like `container.add_notes(note1).add_notes(note2).add_notes(note3)`.

The method serves as a wrapper around `add_notes` specifically designed to support operator overloading for the `+` operation, making it possible to write expressions such as `container1 + container2` or `container + note`.

## Args:
    notes: Can be a single note, a collection of notes, or a note container. Accepts various formats including Note objects, string representations of notes, lists containing note information, or other NoteContainer instances.

## Returns:
    NoteContainer: Returns the instance itself (`self`) to enable method chaining.

## Raises:
    UnexpectedObjectError: When a note object is provided that doesn't have a 'name' attribute, indicating it's not a valid Note instance.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: Modifies `self.notes` through the `add_notes` method.

## Constraints:
    Preconditions: The `notes` argument must be compatible with the `add_notes` method's expectations. The NoteContainer instance must be properly initialized.
    Postconditions: The notes contained in the container are updated to include the newly added notes, maintaining sorted order.

## Side Effects:
    Mutates the internal `notes` list of the NoteContainer instance by appending new notes.

### `mingus.containers.note_container.NoteContainer.__sub__` · *method*

## Summary:
Removes specified notes from the note container and returns the modified container instance.

## Description:
This method implements the Python magic method `__sub__` for the NoteContainer class, enabling the use of the `-` operator to remove notes from a note container. It delegates the removal logic to the `remove_notes` method and returns `self` to support method chaining. This allows for expressive syntax like `container - note1 - note2` to remove multiple notes from a container in a fluent interface pattern.

The method is designed to mirror the behavior of `__add__` but for subtraction operations, providing a consistent API for manipulating note collections. It's particularly useful in musical contexts where you might want to subtract notes from a chord or scale to create variations.

## Args:
    notes: Can be a single note, a collection of notes, or another NoteContainer. Accepts various formats including Note objects, string representations of notes, lists containing note information, or other NoteContainer instances.

## Returns:
    NoteContainer: Returns the instance itself (`self`) to enable method chaining after removing notes.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: Modifies `self.notes` through the `remove_notes` method.

## Constraints:
    Preconditions: The `notes` argument must be compatible with the `remove_notes` method's expectations. The NoteContainer instance must be properly initialized.
    Postconditions: The notes contained in the container are updated to exclude the removed notes.

## Side Effects:
    Mutates the internal `notes` list of the NoteContainer instance by removing specified notes.

### `mingus.containers.note_container.NoteContainer.__len__` · *method*

## Summary:
Returns the number of notes contained in this NoteContainer instance.

## Description:
This method provides the length of the note collection stored in the NoteContainer. It is implemented as a special method (__len__) to enable Python's built-in len() function to work with NoteContainer instances. The method is called during operations like len(container) or when the container is evaluated in a boolean context.

## Args:
    None

## Returns:
    int: The number of Note objects currently stored in the self.notes list attribute.

## Raises:
    None

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.notes attribute must be a list-like object that supports the len() function.
    Postconditions: The method returns an integer count representing the number of notes in the container.

## Side Effects:
    None

### `mingus.containers.note_container.NoteContainer.__eq__` · *method*

## Summary:
Compares two NoteContainer objects for equality by checking if all notes in self exist in the other container.

## Description:
This method implements the equality comparison operator (==) for NoteContainer objects. It determines whether two NoteContainer instances contain the same set of notes by iterating through each note in self and verifying that it exists in the other container. This method is crucial for comparing musical note collections regardless of order. The comparison relies on the `__contains__` method of NoteContainer and the equality comparison of Note objects.

## Args:
    other (NoteContainer): Another NoteContainer instance to compare against

## Returns:
    bool: True if all notes in self exist in other, False otherwise

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.notes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - other must be a NoteContainer instance (though no explicit type check occurs)
    - self.notes should be iterable
    - other should support the 'in' operator with Note objects
    - Note objects must properly implement equality comparison
    
    Postconditions:
    - Returns boolean value indicating equality of note sets
    - Does not modify either container's state

## Side Effects:
    None

## Implementation Details:
This method performs a subset check - it verifies that every note in self is contained within other. However, it does not verify that other contains all notes in self, which means this comparison is not symmetric. For true equality, both directions would need to be checked. The implementation relies on the `in` operator which internally uses Note's equality comparison.

