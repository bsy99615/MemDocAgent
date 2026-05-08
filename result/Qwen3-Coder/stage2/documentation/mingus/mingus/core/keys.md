# `keys.py`

## `mingus.core.keys.is_valid_key` · *function*

## Summary:
Validates whether a given key exists within a global collection of musical key tuples.

## Description:
This function checks membership of a key in a predefined global collection called 'keys'. It iterates through each tuple in the 'keys' collection and returns True if the provided key is found in any tuple, otherwise returns False. This serves as a validation utility for musical key values in the mingus library.

## Args:
    key (any): The key value to validate, typically representing a musical key or note.

## Returns:
    bool: True if the key exists in any of the tuples within the global 'keys' collection, False otherwise.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The global variable 'keys' must be defined and iterable
    - Each element in 'keys' must support the 'in' operator with the provided key
    - The 'keys' variable should contain iterable elements (tuples, lists, etc.)
    
    Postconditions:
    - The function returns a boolean value indicating membership in the keys collection
    - No modifications are made to the input or global state

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start is_valid_key(key)] --> B[Iterate through keys collection]
    B --> C{Is key in current couple?}
    C -- Yes --> D[Return True]
    C -- No --> E[Continue iteration]
    E --> F{End of keys?}
    F -- No --> B
    F -- Yes --> G[Return False]
```

## `mingus.core.keys.get_key` · *function*

## Summary:
Returns the musical key corresponding to a specified number of accidentals.

## Description:
Maps a numerical representation of accidentals (-7 to +7) to a musical key. This function serves as a lookup mechanism for musical key signatures, where negative values represent flats and positive values represent sharps. The function enforces a strict range constraint on the input parameter.

## Args:
    accidentals (int): Number of accidentals, ranging from -7 to +7. Negative values indicate flats, positive values indicate sharps, and zero indicates no accidentals (C major/A minor). Defaults to 0.

## Returns:
    The musical key representation corresponding to the specified number of accidentals. The exact type depends on the implementation of the global `keys` variable, but typically represents a key signature or scale.

## Raises:
    RangeError: When the accidentals parameter is outside the valid range of -7 to +7 (inclusive).

## Constraints:
    Preconditions:
    - The `accidentals` parameter must be an integer within the range [-7, 7]
    - The global variable `keys` must be defined as a sequence with at least 15 elements (indices 0-14)
    
    Postconditions:
    - Returns a valid key representation from the keys collection
    - The returned value is determined by `keys[accidentals + 7]`

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_key called with accidentals] --> B{accidentals in range [-7,7]?}
    B -- No --> C[Raise RangeError]
    B -- Yes --> D[Return keys[accidentals + 7]]
```

## Examples:
    # Get key with no accidentals (C major/A minor)
    key = get_key(0)
    
    # Get key with 2 sharps (D major/B minor)
    key = get_key(2)
    
    # Get key with 3 flats (Eb major/C minor)
    key = get_key(-3)
    
    # This would raise RangeError
    # key = get_key(8)
```

## `mingus.core.keys.get_key_signature` · *function*

## Summary:
Calculates the number of accidentals (sharps or flats) for a given musical key.

## Description:
Determines the number of sharps or flats associated with a musical key by looking up the key in a predefined collection and calculating its position relative to the reference key (C major/A minor). This function is used to compute key signatures for musical notation.

## Args:
    key (str): The musical key to calculate accidentals for, typically represented as a note name (e.g., "C", "G#", "F"). Defaults to "C".

## Returns:
    int: The number of accidentals for the key, where positive values indicate sharps and negative values indicate flats. Zero indicates no accidentals (C major/A minor).

## Raises:
    NoteFormatError: When the provided key string is not recognized or valid according to the musical key validation rules.

## Constraints:
    Preconditions:
    - The key parameter must be a valid musical key string recognized by the is_valid_key function
    - The global variable 'keys' must be defined and contain tuples of musical keys arranged in a specific order
    - The keys variable must be indexed in a way that allows calculation of accidentals relative to C major/A minor

    Postconditions:
    - The function returns an integer representing the number of accidentals for the specified key
    - No modifications are made to the input parameters or global state

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_key_signature(key)] --> B{Is key valid?}
    B -- No --> C[Raise NoteFormatError]
    B -- Yes --> D[Iterate through keys collection]
    D --> E{Is key in current couple?}
    E -- No --> F[Continue iteration]
    E -- Yes --> G[Calculate accidentals = keys.index(couple) - 7]
    G --> H[Return accidentals]
```

## `mingus.core.keys.get_key_signature_accidentals` · *function*

## Summary:
Returns a list of note names that represent the accidentals (sharps or flats) needed for a given musical key signature.

## Description:
This function takes a musical key and calculates the required accidentals for that key's signature. It converts the numeric accidental count returned by `get_key_signature` into a list of formatted note names. The function handles both sharps and flats by using the circle of fifths ordering from the notes module.

## Args:
    key (str): The musical key for which to calculate accidentals, typically represented as a note name (e.g., "C", "G#", "F"). Defaults to "C".

## Returns:
    list[str]: A list of note names with accidentals (either "#" for sharps or "b" for flats) in the order they appear in the key signature. Returns an empty list for keys with no accidentals (like C major or A minor).

## Raises:
    NoteFormatError: When the provided key string is not recognized or valid according to the musical key validation rules.

## Constraints:
    Preconditions:
    - The key parameter must be a valid musical key string recognized by the system
    - The global variable 'notes.fifths' must be defined and contain a sequence of notes in circle of fifths order
    
    Postconditions:
    - The function returns a list of strings representing note names with appropriate accidentals
    - No modifications are made to the input parameters or global state

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_key_signature_accidentals(key)] --> B[Call get_key_signature(key)]
    B --> C{accidentals < 0?}
    C -- Yes --> D[Loop -accidentals times]
    D --> E[Append reversed(fifths)[i] + "b"]
    C -- No --> F{accidentals > 0?}
    F -- Yes --> G[Loop accidentals times]
    G --> H[Append fifths[i] + "#"]
    F -- No --> I[Return empty list]
    E --> J[Return result]
    H --> J
```

## Examples:
    >>> get_key_signature_accidentals("G")
    ['F#']
    
    >>> get_key_signature_accidentals("D")
    ['F#', 'C#']
    
    >>> get_key_signature_accidentals("F")
    ['Bb']
    
    >>> get_key_signature_accidentals("Bb")
    ['Eb', 'Ab', 'Db', 'Gb', 'Cb', 'Fb']
    
    >>> get_key_signature_accidentals("C")
    []
```

## `mingus.core.keys.get_notes` · *function*

## Summary:
Generates a list of the seven notes that make up a musical key, including proper accidentals for sharps or flats.

## Description:
This function computes the set of notes that constitute a given musical key by cycling through a base scale and applying appropriate accidentals (sharps or flats) to notes that require them according to the key's signature. The function implements caching to avoid recomputing the same key multiple times.

## Args:
    key (str): The musical key for which to generate notes, typically represented as a note name (e.g., "C", "G#", "F"). Defaults to "C".

## Returns:
    list[str]: A list of seven note names in the key, with proper accidentals applied where needed. For example, "C" returns ["C", "D", "E", "F", "G", "A", "B"], while "G#" returns ["G#", "A#", "B#", "C#", "D#", "E#", "F##"].

## Raises:
    NoteFormatError: When the provided key string is not recognized or valid according to the musical key validation rules.

## Constraints:
    Preconditions:
    - The key parameter must be a valid musical key string recognized by the system
    - The global variable 'base_scale' must be defined and contain a sequence of note names in proper order
    - The global variable '_key_cache' must be initialized as a dictionary for caching results
    
    Postconditions:
    - The function returns a list of seven note names in the correct order for the specified key
    - The computed result is cached in '_key_cache' for future use with the same key

## Side Effects:
    - Modifies the global '_key_cache' dictionary by storing the computed note list for the given key
    - No other external state mutations or I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start get_notes(key)] --> B{Is key in _key_cache?}
    B -- Yes --> C[Return cached result]
    B -- No --> D{Is key valid?}
    D -- No --> E[Raise NoteFormatError]
    D -- Yes --> F[Get altered_notes from get_key_signature_accidentals]
    F --> G[Get key signature from get_key_signature]
    G --> H{Signature < 0?}
    H -- Yes --> I[Set symbol = "b"]
    H -- No --> J{Signature > 0?}
    J -- Yes --> K[Set symbol = "#"]
    J -- No --> L[Set symbol = ""]
    I --> M
    K --> M
    L --> M
    M --> N[Get raw_tonic_index from base_scale.index(key.upper()[0])]
    N --> O[Iterate through cycle of base_scale]
    O --> P{Note in altered_notes?}
    P -- Yes --> Q[Append note + symbol]
    P -- No --> R[Append note]
    Q --> S
    R --> S
    S --> T[Cache result in _key_cache]
    T --> U[Return result]
```

## Examples:
    >>> get_notes("C")
    ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    
    >>> get_notes("G")
    ['G', 'A', 'B', 'C', 'D', 'E', 'F#']
    
    >>> get_notes("F")
    ['F', 'G', 'A', 'Bb', 'C', 'D', 'E']
```

## `mingus.core.keys.relative_major` · *function*

## Summary:
Returns the relative major key for a given minor key by mapping minor key names to their corresponding major key equivalents.

## Description:
This function implements a lookup mechanism to find the relative major key associated with a specified minor key. It searches through a predefined collection of key pairs where each pair consists of a major key and its corresponding minor key. The function is designed to support music theory operations that require converting between major and minor key representations.

The function is extracted into its own component to encapsulate the key relationship mapping logic, separating the concern of key conversion from other musical operations. This promotes code reuse and makes the key relationship logic explicit and testable.

## Args:
    key (str): The name of a minor key to find the relative major for. Must be a valid minor key name that exists in the keys collection.

## Returns:
    str: The name of the relative major key corresponding to the input minor key.

## Raises:
    NoteFormatError: When the input key is not recognized as a valid minor key in the keys collection, indicating the key format is not supported by this mapping.

## Constraints:
    Preconditions:
    - The input key must be a string representing a valid minor key name
    - The global variable `keys` must be properly initialized with key pairs
    - Each entry in `keys` must be a tuple where the second element is a minor key and the first element is its relative major key
    
    Postconditions:
    - If successful, returns a string representing the relative major key
    - If unsuccessful, raises NoteFormatError with descriptive message

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start relative_major(key)] --> B{Is key in keys?}
    B -->|Yes| C[Return couple[0]]
    B -->|No| D[Raise NoteFormatError]
```

## Examples:
```python
# Find relative major of C minor
major_key = relative_major("Cm")  # Returns "Eb"

# Attempt to find relative major of invalid key
try:
    relative_major("InvalidKey")
except NoteFormatError as e:
    print(e)  # Prints "'InvalidKey' is not a minor key"
```

## `mingus.core.keys.relative_minor` · *function*

## Summary:
Maps a major key to its relative minor key in musical theory.

## Description:
Converts a major key signature into its corresponding relative minor key signature. This function implements the standard music theory relationship where each major key shares the same key signature as its relative minor key, differing only in their tonic notes. The function searches through predefined major key to relative minor mappings and returns the appropriate relative minor when a match is found.

## Args:
    key (str): A major key signature represented as a string (e.g., "C", "G", "D"). Must be a valid major key recognized by the library.

## Returns:
    str: The relative minor key signature corresponding to the input major key (e.g., "A" for input "C", "E" for input "G").

## Raises:
    NoteFormatError: When the input key is not recognized as a valid major key in the library's key mapping system.

## Constraints:
    Preconditions:
    - Input key must be a string representing a recognized major key
    - The keys variable must be properly initialized with major key to relative minor mappings
    
    Postconditions:
    - Returns a valid relative minor key string when input is valid
    - Raises NoteFormatError for unrecognized major keys

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[relative_minor(key)] --> B{Is key in keys?}
    B -->|Yes| C[Return couple[1]]
    B -->|No| D[Raise NoteFormatError]
```

## Examples:
```python
# Valid usage
relative_minor("C")  # Returns "A"
relative_minor("G")  # Returns "E"

# Error case
relative_minor("X")  # Raises NoteFormatError
```

## `mingus.core.keys.Key` · *class*

## Summary
Represents a musical key with major or minor mode, including its signature and formatted name.

## Description
The Key class encapsulates the concept of a musical key in the mingus music library. It handles both major and minor keys, parses key names to identify accidentals (sharps/flats), and computes key signatures. This class serves as a fundamental building block for musical theory operations within the library.

The class is typically instantiated with a key name string (e.g., "C", "G#", "Fm"), and automatically determines whether it represents a major or minor key based on capitalization. It provides access to the key's signature (number of sharps/flats) and a human-readable formatted name.

## State
- key (str): The raw key identifier (e.g., "C", "G#", "Fm")
- mode (str): Either "major" or "minor", determined by the case of the first character
- name (str): Human-readable formatted name (e.g., "C major", "G sharp minor")
- signature (int): Number of accidentals for the key (positive for sharps, negative for flats, zero for no accidentals)

## Lifecycle
- Creation: Instantiate with `Key(key="C")` where key is a valid musical key string
- Usage: Access properties like `key`, `mode`, `name`, and `signature` 
- Destruction: Standard Python object cleanup via garbage collection

## Method Map
```mermaid
graph TD
    A[Key(key="C")] --> B{Parse key name}
    B --> C{Determine mode}
    C --> D{Process accidentals}
    D --> E[Format name]
    E --> F[Calculate signature]
    F --> G[Return initialized Key]
    
    G --> H[__eq__ comparison]
    H --> I[Compare key strings]
```

## Raises
- NoteFormatError: Raised by `get_key_signature()` when the key string is not recognized or valid
- IndexError: May occur in accidental parsing if key string is too short (though handled by try/except)

## Example
```python
# Create major key
c_major = Key("C")
print(c_major.name)     # "C major"
print(c_major.signature) # 0 (no accidentals)

# Create minor key  
a_minor = Key("am")
print(a_minor.mode)     # "minor"
print(a_minor.signature) # -3 (3 flats)

# Create key with sharp
g_sharp = Key("G#")
print(g_sharp.name)     # "G sharp major"
print(g_sharp.signature) # 1 (1 sharp)
```

### `mingus.core.keys.Key.__init__` · *method*

## Summary:
Initializes a Key object with a musical key name, determining its mode, formatted name, and signature.

## Description:
The Key constructor sets up the fundamental properties of a musical key including its base note, major/minor mode, formatted display name, and key signature. This method parses the input key string to determine if it represents a major or minor key, extracts accidental information (sharp or flat), and computes the key's signature for musical notation purposes.

## Args:
    key (str, optional): The musical key to initialize, represented as a note name (e.g., "C", "G#", "F"). Defaults to "C".

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    NoteFormatError: When the provided key string is not recognized or valid according to the musical key validation rules, specifically when get_key_signature raises this exception.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.key: Stores the raw key string
    - self.mode: Stores either "major" or "minor" based on the first character of key
    - self.name: Stores the formatted display name (e.g., "C major", "G# minor")
    - self.signature: Stores the calculated number of accidentals for the key

## Constraints:
    Preconditions:
    - The key parameter must be a valid musical key string recognized by the is_valid_key function
    - The global variable 'keys' must be defined and contain tuples of musical keys arranged in a specific order
    - The key string should be properly formatted (first character uppercase for major, lowercase for minor)

    Postconditions:
    - self.key contains the original key string
    - self.mode contains either "major" or "minor"
    - self.name contains a properly formatted display name
    - self.signature contains an integer representing the number of accidentals for the key

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only manipulates internal object state.

### `mingus.core.keys.Key.__eq__` · *method*

## Summary:
Compares two Key objects for equality based on their musical key names.

## Description:
This method implements equality comparison between two Key objects by comparing their underlying key names. It is used to determine if two Key instances represent the same musical key, regardless of other attributes like mode or signature. This method is part of the standard Python object comparison protocol and enables using Key objects in contexts requiring equality checks, such as set operations or dictionary keys.

## Args:
    other (Key): Another Key instance to compare against this object.

## Returns:
    bool: True if both Key objects have identical key names, False otherwise.

## Raises:
    AttributeError: When the other object does not have a 'key' attribute, which would occur if comparing with a non-Key object.

## State Changes:
    Attributes READ: self.key, other.key
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The other object must be a Key instance (or have a 'key' attribute)
    - Both self.key and other.key must be comparable strings
    
    Postconditions:
    - The method returns a boolean value indicating equality
    - No modifications are made to either Key object's state

## Side Effects:
    None

### `mingus.core.keys.Key.__ne__` · *method*

## Summary:
Implements the not-equal comparison operator for Key objects, returning True when two keys are different.

## Description:
Defines the behavior of the `!=` operator when comparing two Key instances. This method returns True if the two Key objects represent different musical keys, and False if they represent the same key. It achieves this by delegating to the `__eq__` method and negating its result.

This method is part of Python's standard comparison protocol and enables intuitive comparison expressions like `key1 != key2`. The comparison is based solely on the `key` attribute of each Key object.

## Args:
    other (Key): Another Key instance to compare against this object.

## Returns:
    bool: True if the current Key object differs from the other Key object in terms of their key names, False if they represent the same musical key.

## Raises:
    AttributeError: When the other object does not have a 'key' attribute, which would occur if comparing with a non-Key object.

## State Changes:
    Attributes READ: self.key, other.key
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The other object must be a Key instance (or have a 'key' attribute)
    - Both self.key and other.key must be comparable strings
    
    Postconditions:
    - The method returns a boolean value indicating inequality
    - No modifications are made to either Key object's state

## Side Effects:
    None

