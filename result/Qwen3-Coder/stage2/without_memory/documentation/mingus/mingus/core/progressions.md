# `progressions.py`

## `mingus.core.progressions.to_chords` · *function*

## Summary
Converts Roman numeral chord progressions into actual chord note arrays for a specified musical key.

## Description
Transforms a Roman numeral chord progression (like "I", "IV", "V7") into concrete musical chords represented as lists of note names. This function serves as the core converter for translating theoretical chord progressions into playable musical structures.

The function accepts either a single chord string or a list of chord strings, parses each according to Roman numeral notation, applies any accidentals, and handles common chord shorthand notations (like "7" for seventh chords).

## Args
    progression (str or list[str]): Single Roman numeral chord string or list of such strings representing a chord progression
    key (str): Musical key for chord construction, defaults to "C"

## Returns
    list[list[str]]: List of chord note arrays, where each inner array contains note names forming a chord. Returns an empty list if an invalid Roman numeral is encountered.

## Raises
    None explicitly raised in the code shown

## Constraints
    Preconditions:
    - Input progression must be valid Roman numeral notation
    - Valid Roman numerals are limited to those defined in the module's numerals constant
    - Chord shorthand suffixes must be supported by the chords.chord_shorthand mapping
    
    Postconditions:
    - Returns empty list for invalid Roman numerals
    - Each returned chord is properly constructed in the specified key
    - Accidentals are correctly applied to all chord notes

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Start to_chords] --> B{progression is string?}
    B -- Yes --> C[Wrap in list]
    B -- No --> C
    C --> D[Initialize result list]
    D --> E[For each chord in progression]
    E --> F[Parse chord string]
    F --> G{Roman numeral valid?}
    G -- No --> H[Return empty list]
    G -- Yes --> I{Suffix is "7" or empty?}
    I -- Yes --> J[Append suffix to roman numeral]
    J --> K[Get base chord from chords module]
    I -- No --> L[Get base chord from chords module]
    L --> M[Apply chord shorthand to root note]
    K --> N[Apply accidentals]
    M --> N
    N --> O[Add chord to result]
    O --> P[Loop to next chord]
    P --> Q[Return result]
```

## Examples
    # Basic usage with single chord
    chords = to_chords("I", "C")
    # Returns [['C', 'E', 'G']] - C major chord in C key
    
    # Usage with progression
    chords = to_chords(["I", "IV", "V"], "G")
    # Returns [['G', 'B', 'D'], ['C', 'E', 'G'], ['D', 'F#', 'A']] - G major, C major, D major chords in G key
    
    # Usage with accidentals
    chords = to_chords("bVI", "C")
    # Returns [['Ab', 'C', 'Eb']] - A-flat minor chord in C key
    
    # Usage with seventh chords
    chords = to_chords("V7", "D")
    # Returns [['A', 'C#', 'E', 'G#']] - D dominant seventh chord in D key

## `mingus.core.progressions.determine` · *function*

## Summary:
Determines the functional harmony role of a chord within a musical key, returning either abbreviated or descriptive names for the chord's position in the scale.

## Description:
This function analyzes a musical chord in the context of a given key and identifies its functional role (tonic, supertonic, mediant, etc.). It supports both shorthand notation (like "I", "vii°") and full descriptive names (like "tonic", "subtonic seventh"). The function can handle both single chords and lists of chords recursively.

## Args:
    chord (list or str): A musical chord represented as a list of notes or a string representation
    key (str): The musical key (e.g., "C", "G#", "Fb") against which to analyze the chord
    shorthand (bool): When True, returns abbreviated functional names (e.g., "I", "vii°"); when False, returns descriptive names (e.g., "tonic", "subtonic seventh"). Defaults to False

## Returns:
    list: A list containing functional harmony descriptions for the input chord(s). Each element corresponds to a chord in the input and follows these patterns:
        - For single chords: String describing the functional role (e.g., "tonic", "minor dominant")
        - For chord lists: Nested list with the same structure as input
        - Always returns a list, even for single chords

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
        - The chord parameter must be a valid musical chord representation
        - The key parameter must be a valid musical key (single letter with optional accidentals)
        - The chord must be compatible with the specified key for meaningful functional analysis
    
    Postconditions:
        - Returns a list of functional harmony descriptions matching the input structure
        - Each returned string accurately reflects the chord's relationship to the key's scale

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start determine()] --> B{Is chord[0] list?}
    B -- Yes --> C[For each chord in chord]
    C --> D[determine(c, key, shorthand)]
    D --> E[Return result]
    B -- No --> F[Initialize func_dict]
    F --> G[Initialize expected_chord]
    G --> H[Get type_of_chord from chords.determine()]
    H --> I[For each chord in type_of_chord]
    I --> J[Extract name and chord_type]
    J --> K[Get interval_type and interval from intervals.determine()]
    K --> L{Interval type}
    L -->|unison| M[func = "I"]
    L -->|second| N[func = "ii"]
    L -->|third| O[func = "iii"]
    L -->|fourth| P[func = "IV"]
    L -->|fifth| Q[func = "V"]
    L -->|sixth| R[func = "vi"]
    L -->|seventh| S[func = "vii"]
    S --> T[Match expected_chord]
    T --> U{chord_type matches}
    U -->|Yes| V{shorthand=False}
    V -->|True| W[func = func_dict[func]]
    V -->|False| X[func = func_dict[func]]
    U -->|No| Y{chord_type matches 2nd element}
    Y -->|Yes| Z{shorthand=True}
    Z -->|True| AA[func += "7"]
    Z -->|False| AB[func = func_dict[func] + " seventh"]
    Y -->|No| AC[Use chord_shorthand_meaning lookup]
    AC --> AD[Apply shorthand/descriptive formatting]
    AD --> AE[Append to result]
    AE --> AF[Return result]
```

## Examples:
    # Basic usage with descriptive names
    >>> determine(["C", "E", "G"], "C")
    ['tonic']
    
    # Basic usage with shorthand notation  
    >>> determine(["C", "E", "G"], "C", shorthand=True)
    ['I']
    
    # Chord with seventh
    >>> determine(["C", "E", "G", "B"], "C", shorthand=True)
    ['I7']
    
    # Multiple chords
    >>> determine([["C", "E", "G"], ["D", "F#", "A"]], "C")
    [['tonic'], ['supertonic']]

## `mingus.core.progressions.parse_string` · *function*

## Summary:
Parses a musical progression string into Roman numeral components, accidental adjustments, and remaining suffix.

## Description:
Extracts Roman numerals (I or V) and their associated accidentals (# or b) from the beginning of a progression string, returning the parsed components along with any remaining text.

## Args:
    progression (str): A string representing a musical progression, typically starting with Roman numerals followed by accidentals.

## Returns:
    tuple[str, int, str]: A tuple containing:
        - roman_numeral (str): The extracted Roman numeral(s) (uppercase I or V)
        - acc (int): The accidental adjustment (-1 for flat, 0 for natural, 1 for sharp)
        - suffix (str): The remaining portion of the input string after parsing

## Raises:
    None explicitly raised

## Constraints:
    - Preconditions: Input must be a string
    - Postconditions: The returned tuple always contains exactly three elements in the specified order

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start parse_string] --> B{Character is #?}
    B -- Yes --> C[acc += 1]
    C --> G[Increment i]
    B -- No --> H{Character is b?}
    H -- Yes --> I[acc -= 1]
    I --> G
    H -- No --> J{Character is I or V?}
    J -- Yes --> K[Append to roman_numeral]
    K --> G
    J -- No --> L[Break loop]
    G --> M{End of string?}
    M -- No --> B
    M -- Yes --> N[Set suffix = progression[i:]
    N --> O[Return (roman_numeral, acc, suffix)]
```

## Examples:
    >>> parse_string("V#")
    ('V', 1, '')
    
    >>> parse_string("ivb")
    ('IV', -1, '')
    
    >>> parse_string("I##sus4")
    ('I', 2, 'sus4')
    
    >>> parse_string("invalid")
    ('', 0, 'invalid')
```

## `mingus.core.progressions.tuple_to_string` · *function*

## Summary:
Converts a progression tuple into a formatted string representation with proper accidentals.

## Description:
Transforms a tuple containing roman numeral, accidental adjustment, and suffix components into a string format suitable for displaying musical progressions. This function handles the conversion of accidental values to appropriate flat ('b') or sharp ('#') notations and properly formats the resulting progression string.

## Args:
    prog_tuple (tuple): A 3-element tuple containing (roman, acc, suff) where:
        - roman (str): Roman numeral representation (e.g., "I", "V")
        - acc (int): Accidental adjustment value that determines flat/sharp symbols
        - suff (str): Suffix to append to the formatted result

## Returns:
    str: Formatted progression string with accidentals applied to the roman numeral and suffix appended

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - prog_tuple must be a 3-element tuple
        - roman must be a string
        - acc must be an integer
        - suff must be a string
    
    Postconditions:
        - Returns a string combining roman numeral with applied accidentals and suffix
        - The returned string will have proper flat/sharp notation based on acc value

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start tuple_to_string] --> B{acc > 6?}
    B -- Yes --> C[acc = 0 - acc % 6]
    B -- No --> D{acc < -6?}
    D -- Yes --> E[acc = acc % 6]
    D -- No --> F[acc unchanged]
    C --> F
    E --> F
    F --> G{acc < 0?}
    G -- Yes --> H[Prepend "b" to roman]
    H --> I[acc += 1]
    I --> J{acc < 0?}
    J -- Yes --> H
    J -- No --> K{acc > 0?}
    K -- Yes --> L[Prepend "#" to roman]
    L --> M[acc -= 1]
    M --> N{acc > 0?}
    N -- Yes --> L
    N -- No --> O[Return roman + suff]
```

## Examples:
    >>> tuple_to_string(("I", 2, "maj"))
    "#I:maj"
    
    >>> tuple_to_string(("V", -1, "min"))
    "bV:min"
    
    >>> tuple_to_string(("IV", 0, "sus"))
    "IV:sus"
```

## `mingus.core.progressions.substitute_harmonic` · *function*

## Summary:
Replaces Roman numeral harmonies in a progression with their harmonic substitutions according to predefined rules.

## Description:
This function performs harmonic substitution on a specific index of a Roman numeral progression. It takes a progression list and substitutes a Roman numeral at a given index with its harmonic equivalents based on established musical theory patterns. The function is designed to work with Roman numeral notation commonly used in music theory analysis.

## Args:
    progression (list[str]): A list of Roman numeral harmony strings (e.g., ["I", "IV", "V7"])
    substitute_index (int): Index of the harmony in the progression to be substituted
    ignore_suffix (bool): When True, applies substitutions regardless of suffix (like "7"). Defaults to False

## Returns:
    list[str]: A list of possible substituted harmonies. May be empty if no substitution matches the input harmony.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The progression list must contain valid Roman numeral strings
    - The substitute_index must be a valid index within the progression list bounds
    - The progression elements should be in a format compatible with parse_string function
    
    Postconditions:
    - Returns a list of harmonies that are valid Roman numeral strings
    - All returned harmonies maintain proper formatting with accidentals and suffixes

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start substitute_harmonic] --> B[Get progression element at substitute_index]
    B --> C[Parse Roman numeral with parse_string]
    C --> D{Suff is empty or "7" or ignore_suffix?}
    D -- No --> E[Return empty list]
    D -- Yes --> F[Iterate through simple_substitutions]
    F --> G{Current roman equals first element of substitution?}
    G -- Yes --> H[Set r to second element of substitution]
    G -- No --> I{Current roman equals second element of substitution?}
    I -- Yes --> J[Set r to first element of substitution]
    I -- No --> K[Skip to next substitution]
    H,J,K --> L{r is not None?}
    L -- Yes --> M[Adjust suffix if needed]
    M --> N[Append substituted harmony to result]
    L -- No --> O[Continue to next substitution]
    F --> P[Return result list]
```

## Examples:
    # Basic substitution
    progression = ["I", "IV", "V7"]
    result = substitute_harmonic(progression, 0)  # Substitute "I"
    # Returns: ["III", "VI"] (I can be substituted with III or VI)
    
    # With suffix ignored
    progression = ["I7", "IV", "V"]
    result = substitute_harmonic(progression, 0, ignore_suffix=True)
    # Returns: ["III", "VI"] (ignores the "7" suffix)
    
    # No substitution available
    progression = ["II", "III", "VI"]
    result = substitute_harmonic(progression, 0)  # Substitute "II"
    # Returns: [] (no substitution defined for II)

## `mingus.core.progressions.substitute_minor_for_major` · *function*

## Summary:
Converts minor chords to major chords in a musical progression at a specified index.

## Description:
This function examines a chord at a given position in a musical progression and converts minor chords (indicated by 'm' suffix) to their major equivalents. It specifically targets chords with 'm', 'm7', or certain diatonic chords (II, III, VI) without suffixes. The conversion changes the suffix from minor ('m') to major ('M'), minor seventh ('m7') to major seventh ('M7'), or removes the suffix for major chords.

## Args:
    progression (list[str]): A list of chord representations in Roman numeral notation
    substitute_index (int): Index of the chord in the progression to potentially convert
    ignore_suffix (bool): When True, forces conversion regardless of chord suffix. Defaults to False

## Returns:
    list[str]: A list containing the converted chord string, or empty list if no conversion occurs

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - progression must be a list of valid Roman numeral chord strings
    - substitute_index must be a valid index within the progression list bounds
    
    Postconditions:
    - Returns either an empty list or a single-element list with the converted chord
    - The returned chord maintains proper Roman numeral formatting

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Check if conversion should occur?}
    B -- Yes --> C[Calculate new chord]
    C --> D{Determine suffix for result}
    D --> E{suffix == "m" OR ignore_suffix?}
    E -- Yes --> F[Return "M" suffix]
    E -- No --> G{suffix == "m7" OR ignore_suffix?}
    G -- Yes --> H[Return "M7" suffix]
    G -- No --> I[Return empty suffix]
    B -- No --> J[Return empty list]
    F --> K[End]
    H --> K
    I --> K
    J --> K
```

## Examples:
    # Convert minor ii chord to major II
    progression = ["I", "ii", "IV", "V"]
    result = substitute_minor_for_major(progression, 1)  # Returns ["II"]
    
    # Convert minor vi chord to major VI  
    progression = ["I", "vi", "IV", "V"]
    result = substitute_minor_for_major(progression, 1)  # Returns ["VI"]
    
    # With ignore_suffix=True, convert any chord
    progression = ["I", "iv", "IV", "V"]
    result = substitute_minor_for_major(progression, 1, ignore_suffix=True)  # Returns ["IV"]
```

## `mingus.core.progressions.substitute_major_for_minor` · *function*

## Summary:
Replaces major chords with their relative minor equivalents in a musical progression at a specified position.

## Description:
This function transforms major chords into their corresponding relative minor chords within a musical progression. It specifically targets chords that are major (indicated by "M" suffix) or dominant seventh chords (indicated by "M7" suffix), or major triads without suffix (when the Roman numeral is I, IV, or V). The transformation maintains the harmonic function while changing the chord quality from major to minor.

## Args:
    progression (list[str]): A list of chord strings representing a musical progression.
    substitute_index (int): Index of the chord in the progression to potentially substitute.
    ignore_suffix (bool): When True, treats all chords as major for substitution purposes. Defaults to False.

## Returns:
    list[str]: A list containing the substituted minor chord(s) if the conditions are met, otherwise an empty list.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - The progression list must contain valid Roman numeral chord representations.
    - The substitute_index must be a valid index within the progression list bounds.
    - The chord at substitute_index must be parseable by parse_string function.

    Postconditions:
    - If substitution occurs, the returned list contains exactly one string representing the minor equivalent.
    - If no substitution occurs, the returned list is empty.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Is suffix M or M7 or (empty and roman in [I,IV,V]) or ignore_suffix?}
    B -- Yes --> C[Calculate minor equivalent using skip and interval_diff]
    C --> D{Suffix is M or ignore_suffix?}
    D -- Yes --> E[Append "m" to result]
    D -- No --> F{Suffix is M7 or ignore_suffix?}
    F -- Yes --> G[Append "m7" to result]
    F -- No --> H[Append empty suffix to result]
    B -- No --> I[Return empty list]
    E --> J[Return result]
    G --> J
    H --> J
    I --> J
```

## Examples:
    # Example 1: Substitute major chord
    progression = ["I", "IV", "V"]
    result = substitute_major_for_minor(progression, 0)  # Substitutes "I" with "i"
    
    # Example 2: Substitute major seventh chord
    progression = ["I7", "IV", "V"]
    result = substitute_major_for_minor(progression, 0)  # Substitutes "I7" with "i7"
    
    # Example 3: Ignore suffix flag
    progression = ["I", "IV", "V"]
    result = substitute_major_for_minor(progression, 0, ignore_suffix=True)  # Substitutes "I" with "i"
```

## `mingus.core.progressions.substitute_diminished_for_diminished` · *function*

## Summary:
Replaces a diminished chord with a sequence of three consecutive diminished chords in a musical progression.

## Description:
This function takes a musical progression and substitutes a specified diminished chord with three consecutive diminished chords that follow the same pattern. It's used to expand diminished chords in harmonic progressions, particularly for VII dim chords and other diminished chords. The function handles various chord suffixes ("dim", "dim7", or empty string) and generates appropriate accidentals for the substituted chords.

## Args:
    progression (list): A list of chord strings representing a musical progression
    substitute_index (int): Index of the chord in the progression to be substituted
    ignore_suffix (bool): When True, treats all chords as diminished regardless of suffix. Defaults to False

## Returns:
    list: A list containing three chord strings representing the substituted diminished chords

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - The progression list must contain at least one element
    - The substitute_index must be a valid index for the progression list
    - The chord at substitute_index must be parseable by parse_string function
    
    Postconditions:
    - Returns exactly 3 chord strings when substitution occurs
    - Returns empty list when no substitution is performed

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start function] --> B{Is diminished chord?}
    B -- Yes --> C[Set suffix to "dim" if empty]
    C --> D[Initialize result list]
    D --> E[Loop 3 times]
    E --> F[Get next Roman numeral]
    F --> G[Calculate accidental adjustment]
    G --> H[Create chord string]
    H --> I[Add to result list]
    I --> J[Update last Roman numeral]
    J --> K{Loop end?}
    K -- No --> E
    K -- Yes --> L[Return result]
    B -- No --> M[Return empty list]
```

## Examples:
    # Example 1: Substitute VII dim with three diminished chords
    progression = ["I", "VII", "IV"]
    result = substitute_diminished_for_diminished(progression, 1)
    # Returns: ["VII", "IX", "XI"] (with appropriate accidentals)
    
    # Example 2: Substitute V dim7 with three diminished chords  
    progression = ["I", "VII dim7", "IV"]
    result = substitute_diminished_for_diminished(progression, 1)
    # Returns: ["VII dim", "IX dim", "XI dim"]
    
    # Example 3: With ignore_suffix=True
    progression = ["I", "VII", "IV"]
    result = substitute_diminished_for_diminished(progression, 1, ignore_suffix=True)
    # Returns: ["VII", "IX", "XI"] (with appropriate accidentals)
```

## `mingus.core.progressions.substitute_diminished_for_dominant` · *function*

## Summary:
Replaces a diminished chord with a series of dominant seventh chords in a musical progression.

## Description:
This function transforms a diminished chord (such as VII dim or VII dim7) into a sequence of four dominant seventh chords that create a similar harmonic function. It's commonly used in music theory to analyze or modify progressions where diminished chords appear.

The function is designed to handle various chord suffixes and can be configured to process any chord in a progression regardless of its suffix. It's extracted as a separate function to encapsulate the complex logic of harmonic substitution while maintaining clean separation of concerns in the progression processing pipeline.

## Args:
    progression (list[str]): A list of chord representations in string format (e.g., "VII", "VII dim", "VII dim7")
    substitute_index (int): Index of the chord in the progression to be substituted
    ignore_suffix (bool): When True, treats any chord at the specified index as a diminished chord for substitution purposes. Defaults to False.

## Returns:
    list[str]: A list of four dominant seventh chord representations that substitute the original diminished chord. Each chord is represented as a string in the same format as the input progression elements.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The progression list must contain at least one element
    - The substitute_index must be a valid index for the progression list
    - The progression element at substitute_index must be parseable by parse_string function
    
    Postconditions:
    - The returned list always contains exactly 4 elements when substitution occurs
    - Each returned chord string follows the same format as input progression elements
    - The function only performs substitution when the chord matches the criteria for diminished chords

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start function] --> B{Is diminished chord?}
    B -- Yes --> C[Set suffix to "dim" if empty]
    C --> D[Initialize last = roman]
    D --> E[Loop 4 times]
    E --> F[Calculate next = skip(last, 2)]
    F --> G[Calculate dom = skip(last, 5)]
    G --> H[Calculate acc adjustment]
    H --> I[Append dom7 chord to result]
    I --> J[Update last = next]
    J --> K{Loop counter < 4?}
    K -- Yes --> E
    K -- No --> L[Return result]
    B -- No --> L
```

## Examples:
    # Example 1: Substituting a VII dim chord
    progression = ["I", "VII dim", "IV"]
    result = substitute_diminished_for_dominant(progression, 1)
    # Returns: ["III dom7", "V dom7", "VII dom7", "II dom7"]
    
    # Example 2: Substituting a VII chord with no suffix
    progression = ["I", "VII", "IV"]
    result = substitute_diminished_for_dominant(progression, 1)
    # Returns: ["III dom7", "V dom7", "VII dom7", "II dom7"]
    
    # Example 3: Using ignore_suffix=True
    progression = ["I", "VI", "IV"]
    result = substitute_diminished_for_dominant(progression, 1, ignore_suffix=True)
    # Returns: ["III dom7", "V dom7", "VII dom7", "II dom7"]
```

## `mingus.core.progressions.substitute` · *function*

## Summary:
Performs chord substitution operations on a Roman numeral chord progression by replacing chords with their theoretical equivalents according to music theory rules.

## Description:
This function implements chord progression substitutions commonly used in music theory and composition. It takes a chord progression represented as Roman numerals and replaces a specified chord at a given index with various theoretical alternatives based on established harmonic relationships. The function supports recursive substitution when depth is greater than zero.

## Args:
    progression (list[str]): List of Roman numeral chord representations (e.g., ["I", "V7", "vi"])
    substitute_index (int): Index of the chord in the progression to be substituted
    depth (int): Recursion depth for nested substitutions. Defaults to 0 (no recursion)

## Returns:
    list[str]: List of all possible substituted chord progressions. Each string represents a valid Roman numeral chord. May return an empty list if no substitutions are applicable.

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
    - progression must be a non-empty list of valid Roman numeral chord strings
    - substitute_index must be a valid index within the progression list bounds
    - All chord strings must follow the Roman numeral notation format (e.g., "I", "V7", "ii", "bVIIm7")

    Postconditions:
    - Returns a list containing all valid chord substitutions for the specified position
    - The returned list may be empty if no substitutions are applicable
    - All returned strings follow proper Roman numeral chord notation

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start substitute] --> B[Parse chord at substitute_index]
    B --> C{suffix is \"\" or \"7\"}
    C -- Yes --> D[Process simple substitutions]
    C -- No --> E[Skip simple substitutions]
    D --> F[Check each simple substitution pair]
    F --> G{Match found?}
    G -- Yes --> H[Add basic substitution]
    H --> I{Substitution ends with \"7\"?}
    I -- No --> J[Add 7th version]
    I -- Yes --> K[Add root version]
    E --> L{suffix is \"\" or \"M\" or \"m\"}
    L -- Yes --> M[Add 7th version]
    L -- No --> N[Skip M/m additions]
    M --> O{suffix is \"m\" or \"m7\"}
    O -- Yes --> P[Calculate 2nd skip]
    O -- No --> Q[Skip m additions]
    P --> R[Add M and M7 versions]
    Q --> S{suffix is \"M\" or \"M7\"}
    S -- Yes --> T[Calculate 5th skip]
    S -- No --> U[Skip M additions]
    T --> V[Add m and m7 versions]
    U --> W{suffix is \"dim7\" or \"dim\"}
    W -- Yes --> X[Add dom7 versions]
    W -- No --> Y[Skip dim additions]
    X --> Z[Add dom7 versions]
    Z --> AA[Loop 4 times for dim7]
    AA --> AB[Return results]
    Y --> AB
    AB --> AC{depth > 0?}
    AC -- Yes --> AD[Create new progression]
    AD --> AE[Recursive call]
    AE --> AF[Combine results]
    AF --> AG[Return final result]
    AC -- No --> AG
```

## Examples:
    >>> progression = ["I", "V7", "vi"]
    >>> result = substitute(progression, 1, depth=0)
    # Returns possible substitutions for V7 chord
    
    >>> progression = ["I", "V7", "vi"] 
    >>> result = substitute(progression, 1, depth=1)
    # Returns substitutions for V7 and their substitutions recursively

## `mingus.core.progressions.interval_diff` · *function*

## Summary:
Computes an adjustment value based on interval comparisons between two indexed progression values.

## Description:
This function calculates an adjustment value by comparing the difference between two indexed progression values against a target interval. It uses lookup tables (numeral_intervals and numerals) to convert progression identifiers into numerical values and performs iterative adjustments to reach the target interval difference.

## Args:
    progression1 (any): First progression identifier used as index into numerals list
    progression2 (any): Second progression identifier used as index into numerals list
    interval (int): Target interval value for comparison

## Returns:
    int: Adjustment value indicating steps needed to reach target interval

## Raises:
    ValueError: When progression1 or progression2 are not found in numerals list
    IndexError: When indexing operations exceed list bounds
    TypeError: When numeral_intervals or numerals are not properly initialized

## Constraints:
    Preconditions:
        - progression1 and progression2 must be valid keys/indexes for numerals list
        - numeral_intervals and numerals must be properly initialized sequences
        - interval must be a numeric value
    
    Postconditions:
        - Returns an integer adjustment value
        - The calculation is based purely on numerical comparisons and arithmetic

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start interval_diff] --> B[i = numeral_intervals[numerals.index(progression1)]]
    B --> C[j = numeral_intervals[numerals.index(progression2)]]
    C --> D{if j < i?}
    D -- Yes --> E[j += 12]
    D -- No --> F[j unchanged]
    E --> G[Goto F]
    F --> H{while j - i > interval?}
    H -- Yes --> I[acc -= 1; j -= 1]
    H -- No --> J{while j - i < interval?}
    I --> K[Evaluate again]
    J -- Yes --> L[acc += 1; j += 1]
    L --> K
    K --> M{Loop conditions}
    M -- Continue --> H
    M -- Done --> N[return acc]
```

## Examples:
    # Basic usage pattern:
    # result = interval_diff(some_progression1, some_progression2, target_interval)
    # Returns adjustment steps needed to achieve target_interval

## `mingus.core.progressions.skip` · *function*

## Summary:
Returns the Roman numeral that is a specified number of positions ahead in the diatonic scale sequence.

## Description:
This function calculates the next Roman numeral in a musical progression by advancing a given number of positions through the standard diatonic scale sequence. It's commonly used in music theory applications to navigate through chord progressions or scale degrees.

## Args:
    roman_numeral (str): A Roman numeral representing a degree in the diatonic scale (typically I-VII).
    skip_count (int): Number of positions to advance forward in the sequence. Defaults to 1.

## Returns:
    str: The Roman numeral at the skipped position, wrapping around to the beginning of the sequence if needed.

## Raises:
    ValueError: When the roman_numeral is not found in the global numerals sequence.
    IndexError: When the numerals sequence is not properly initialized.

## Constraints:
    Preconditions: 
    - The roman_numeral must be present in the global numerals list
    - The global numerals list must be defined and contain at least 7 elements
    - The numerals list must support the .index() method
    
    Postconditions:
    - The returned value will always be a valid Roman numeral from the numerals sequence
    - The result wraps around using modulo arithmetic when exceeding sequence bounds

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input roman_numeral] --> B{Find index in numerals}
    B --> C[Add skip_count]
    C --> D[Apply modulo 7]
    D --> E[Return numerals[result]]
```

## Examples:
    >>> skip('I', 2)
    'III'
    >>> skip('VII', 1)
    'I'
    >>> skip('III', 5)
    'I'
```

