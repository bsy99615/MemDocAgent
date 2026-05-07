# `tablature.py`

## `mingus.extra.tablature.begin_track` · *function*

## Summary:
Generates formatted tablature track header strings from musical tuning information.

## Description:
This function creates properly formatted header lines for musical tablature representation by converting note names to shorthand format and aligning them with consistent spacing and separator characters. It's designed to prepare the initial track headers for tablature display, ensuring all tracks are properly aligned.

## Args:
    tuning (object): A tuning object containing musical note information with a `tuning` attribute that is iterable of note objects having a `to_shorthand()` method.
    padding (int): Number of dash characters to append after the track separator. Defaults to 2.

## Returns:
    list[str]: A list of formatted track header strings, each representing a track in a tablature. Each string consists of:
    - A space followed by the note shorthand name
    - Sufficient spaces to align all tracks to the same width
    - The separator "||"
    - The specified number of dash characters for padding

## Raises:
    AttributeError: If the tuning object lacks a `tuning` attribute or if note objects lack a `to_shorthand()` method.
    TypeError: If the tuning.tuning attribute is not iterable or if padding is not an integer.
    ValueError: If padding is negative.

## Constraints:
    Preconditions:
    - The tuning parameter must have a `tuning` attribute that is iterable
    - Each item in tuning.tuning must have a `to_shorthand()` method
    - The padding parameter must be a non-negative integer
    
    Postconditions:
    - Returns a list of strings with consistent formatting
    - All strings in the returned list have the same total length
    - Each string represents a properly aligned tablature track header

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[begin_track called] --> B{Validate tuning exists}
    B --> C{Validate padding is non-negative}
    C --> D[Extract shorthand names from tuning.tuning]
    D --> E[Find maximum name length]
    E --> F[Calculate basesize = max_length + 3]
    F --> G[Initialize empty result list]
    G --> H{Process each shorthand name}
    H -- Yes --> I[Format: " " + name]
    I --> J[Calculate spaces needed for alignment]
    J --> K[Append spaces + "||" + "-" * padding]
    K --> L[Add formatted string to result]
    H -- No --> M[Return result list]
```

## Examples:
    # Basic usage with default padding
    tuning = some_tuning_object
    headers = begin_track(tuning)
    # Returns list like [' E   ||--', ' A   ||--', ' D   ||--', ' G   ||--']
    # Where each string has the same total length and tracks are aligned
    
    # Usage with custom padding
    headers = begin_track(tuning, padding=5)
    # Returns list like [' E   ||-----', ' A   ||-----', ' D   ||-----', ' G   ||-----']

## `mingus.extra.tablature.add_headers` · *function*

## Summary:
Creates a formatted header section for tablature files containing metadata such as title, subtitle, author information, description, and instrument tunings.

## Description:
This function generates a properly formatted header block for musical tablature documents. It centers text within a specified width and organizes metadata in a standardized format. The function is designed to be reusable for creating consistent header sections across different tablature files.

The logic is extracted into its own function to separate the concerns of header formatting from the main tablature generation process, making the code more modular and testable.

## Args:
    width (int): Total width in characters for centering text. Defaults to 80.
    title (str): Main title of the tablature. Converted to uppercase. Defaults to "Untitled".
    subtitle (str): Secondary title or subtitle. Defaults to "".
    author (str): Name of the author. Defaults to "".
    email (str): Author's email address. Defaults to "".
    description (str): Description of the tablature content. Defaults to "".
    tunings (list): List of tuning objects with instrument and description attributes. Defaults to None (which becomes empty list).

## Returns:
    list[str]: List of formatted string lines comprising the header section.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - width should be a positive integer
    - All string parameters should be valid strings
    - tunings should be a list of objects with instrument and description attributes if provided
    
    Postconditions:
    - Returns a list of strings with proper formatting
    - Header always ends with two blank lines
    - Text is centered within the specified width

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start add_headers] --> B{tunings is None?}
    B -- Yes --> C[tunings = []]
    B -- No --> D[Continue]
    C --> E[title = upper(title)]
    D --> E
    E --> F{subtitle != ""}
    F -- Yes --> G[result += subtitle line]
    F -- No --> H[Skip subtitle]
    G --> H
    H --> I{author or email != ""}
    I -- Yes --> J[result += blank lines]
    J --> K{email != ""}
    K -- Yes --> L[result += author+email line]
    K -- No --> M[result += author only line]
    I -- No --> N[Skip author section]
    L --> N
    M --> N
    N --> O{description != ""}
    O -- Yes --> P[result += blank lines]
    P --> Q[Process description into lines]
    Q --> R[Add formatted description lines]
    O -- No --> S[Skip description]
    R --> S
    S --> T{tunings != []}
    T -- Yes --> U[result += blank lines]
    U --> V[Add instruments section]
    T -- No --> W[Skip instruments]
    V --> W
    W --> X[Add final blank lines]
    X --> Y[Return result]
```

## Examples:
    >>> add_headers(title="Amazing Grace", author="John Doe")
    ['', 'AMAZING GRACE', '', 'Written by: John Doe', '', '', '']

    >>> add_headers(width=60, title="Song Title", subtitle="Verse 1", description="A beautiful song")
    ['', 'SONG TITLE', '', 'Verse 1', '', '', 'Written by: ', '', '', 'A beautiful song', '', '', '']

## `mingus.extra.tablature.from_Note` · *function*

## Summary:
Converts a musical note into a tablature representation showing which string and fret position would play that note.

## Description:
This function takes a musical note and generates a visual tablature representation indicating which string and fret combination would produce that note on a guitar or similar stringed instrument. It attempts to find the optimal string-fret combination that plays the requested note, prioritizing exact matches over closest matches. The function is part of the tablature generation system in the mingus library.

## Args:
    note (object): A musical note object that either has string and fret attributes (indicating it's already a tablature position), or can be processed by the tuning system to find matching fret positions. Must be compatible with the tuning system's expectations.
    width (int): The desired width of the resulting tablature string. Defaults to 80 characters. Must be a positive integer.
    tuning (object, optional): A tuning object that defines the instrument's string configuration. If None, uses the default tuning defined in the module.

## Returns:
    str: A formatted tablature string showing the note's position on the instrument. The string contains multiple lines representing each string, with the note indicated by its fret number positioned appropriately. Each line represents a string and shows the appropriate fret position or hyphens for other strings. The result is reversed (so the highest string appears first) and joined with the OS-specific line separator.

## Raises:
    RangeError: When no fret position can be found that would play the requested note, indicating the note is outside the playable range of the instrument.

## Constraints:
    Preconditions:
    - The note parameter must be a valid musical note object compatible with the tuning system
    - The tuning parameter must be a valid tuning object with appropriate methods (get_Note, find_frets)
    - The width parameter must be a positive integer
    
    Postconditions:
    - Returns a properly formatted tablature string with consistent line lengths
    - The returned string represents a valid tablature visualization
    - All strings in the result have the same total length
    - The result is reversed so that the highest string appears first

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[from_Note called] --> B{tuning is None?}
    B -- Yes --> C[Set tuning = default_tuning]
    B -- No --> D[Use provided tuning]
    C --> E[Call begin_track(tuning)]
    D --> E
    E --> F{note has string and fret attrs?}
    F -- Yes --> G[Get note from tuning using string/fret]
    G --> H{Found note matches input note?}
    H -- Yes --> I[Set s,f = string,fret; min = 0]
    H -- No --> J[Continue to fret search]
    F -- No --> J
    J --> K[Find all fret positions for note]
    K --> L{Any fret found?}
    L -- Yes --> M[Find minimum fret position]
    M --> N[Set s,f = string,fret of minimum fret]
    L -- No --> O[Raise RangeError]
    N --> P{min != 1000?}
    P -- Yes --> Q[Format tablature with fret position]
    P -- No --> O
    Q --> R[Reverse result lines]
    R --> S[Join with OS line separator]
    O --> T[Throw RangeError]
```

## `mingus.extra.tablature.from_NoteContainer` · *function*

## Summary:
Converts a collection of musical notes into a formatted tablature representation showing string and fret positions.

## Description:
Transforms a container of musical notes into a visual tablature format that displays which strings and frets should be played to produce those notes. This function is specifically designed to generate guitar-style tablature where each line represents a string and shows the appropriate fret positions for the notes being played. The function encapsulates the core logic for mapping musical notes to playable fingerings and formatting them into a readable tablature display.

## Args:
    notes (list): A collection of musical note objects, each expected to have 'string' and 'fret' attributes representing the string number and fret position. These note objects are typically instances that have been processed by the tuning system.
    width (int): The desired width of the tablature output in characters. Defaults to 80.
    tuning (object): A musical tuning object that provides fingering information. If None, uses default_tuning which typically represents standard tuning.

## Returns:
    str: A multi-line string representing the tablature with each line corresponding to a string and showing the appropriate fret positions for the notes. Each line is properly formatted with alignment and separators between strings, ending with the platform's line separator.

## Raises:
    FingerError: When no playable fingering can be found for the provided notes, indicating that the combination of notes cannot be played with the given tuning.

## Constraints:
    Preconditions:
    - Notes must be objects with 'string' and 'fret' attributes
    - The tuning object must support the find_fingering() method
    - Width must be a positive integer
    
    Postconditions:
    - Returns a properly formatted tablature string with consistent line lengths
    - Each line represents a string in the tuning
    - Fret positions are displayed correctly aligned within the tablature
    - The returned string uses the platform's line separator

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[from_NoteContainer called] --> B{tuning is None?}
    B -- Yes --> C[Set tuning = default_tuning]
    B -- No --> C[Use provided tuning]
    C --> D[Call begin_track(tuning)]
    D --> E[Calculate width parameters]
    E --> F[Call tuning.find_fingering(notes)]
    F --> G{fingerings found?}
    G -- No --> H[Raise FingerError]
    G -- Yes --> I[Process notes with string/fret attributes]
    I --> J[Filter matching fingerings]
    J --> K{Matching fingerings found?}
    K -- Yes --> L[Use first matching fingering]
    K -- No --> L[Use first available fingering]
    L --> M[Build fret position dictionary]
    M --> N[Format tablature lines]
    N --> O[Reverse result order]
    O --> P[Join lines with OS line separator]
    P --> Q[Return formatted tablature]
```

## `mingus.extra.tablature.from_Bar` · *function*

## Summary:
Converts a musical bar object into a formatted tablature representation showing note positions on strings.

## Description:
Transforms a musical bar containing note events into a visual tablature format that displays which strings and frets should be played for each note. The function processes each note event in the bar, finds appropriate fingerings for the notes, and formats them into a multi-line tablature representation with proper timing and spacing.

This function is extracted from inline logic to separate the concerns of tablature conversion from the rest of the music processing pipeline, allowing for reusable tablature generation and easier testing of the formatting logic.

## Args:
    bar (object): A musical bar object containing note events with attributes:
        - bar (list): List of tuples (beat, duration, notes) representing musical events
        - meter (tuple): Time signature in format (numerator, denominator)
    width (int, optional): Total character width for the tablature display. Defaults to 40.
    tuning (object, optional): Musical tuning object with fingering capabilities. Defaults to None (uses default_tuning).
    collapse (bool, optional): Whether to join lines with OS-specific line separators. Defaults to True.

## Returns:
    str or list: Formatted tablature representation with the following characteristics:
        - When collapse=True: Single string with OS line separators joining all tablature lines
        - When collapse=False: List of tablature line strings
    The tablature includes:
        - Track headers showing string names (e.g., "E   ||", "A   ||", etc.)  
        - Note positions represented by fret numbers (e.g., "3", "5")
        - Timing indicators and bar markers
        - Proper spacing and alignment for musical timing
        - Final bar line with "|" marker

## Raises:
    FingerError: When no playable fingering can be found for a set of notes in a bar event.

## Constraints:
    Preconditions:
    - The bar object must have a `bar` attribute that is iterable of (beat, duration, notes) tuples
    - The bar object must have a `meter` attribute in format (numerator, denominator)
    - Notes in bar entries must either be None or have string and fret attributes
    - Tuning object must support find_fingering() and get_Note() methods
    - The tuning object must have a `tuning` attribute containing note objects with `to_shorthand()` method
    
    Postconditions:
    - Returns properly formatted tablature with consistent alignment
    - All tablature lines have equal length when collapsed
    - Fingering positions are accurately represented
    - Tablature lines are properly reversed for display orientation
    - Final tablature output includes proper bar termination markers

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start from_Bar(bar, width, tuning, collapse)] --> B{tuning is None?}
    B -- Yes --> C[Set tuning = default_tuning]
    C --> D[Calculate qsize = _get_qsize(tuning, width)]
    D --> E[Initialize result = begin_track(tuning, max(2, qsize//2))]
    E --> F[Iterate bar.bar entries]
    F --> G{fingering != [] OR notes is None?}
    G -- Yes --> H[Process note positions]
    H --> I[Find matching fingering positions]
    I --> J{Found matching fingering?}
    J -- Yes --> K[Use first matching fingering]
    J -- No --> L{notes is None?}
    L -- Yes --> M[Set f = [], maxlen = 1]
    L -- No --> N[Use first available fingering]
    N --> O[Build fret position dictionary]
    O --> P[Format each track line with fret positions]
    P --> Q[Add timing markers and finalize]
    G -- No --> R[raise FingerError]
    R --> S[End]
    Q --> T[Finalize tablature formatting]
    T --> U{collapse?}
    U -- Yes --> V[Join with os.linesep]
    U -- No --> W[Return list of lines]
    V --> X[End]
    W --> X
```

## Examples:
    # Basic usage with default parameters
    tablature_string = from_Bar(music_bar)
    # Returns formatted tablature string showing note positions
    
    # Custom width and tuning
    custom_tab = from_Bar(music_bar, width=60, tuning=custom_tuning)
    # Returns tablature with wider display and custom tuning
    
    # Non-collapsed output
    tab_lines = from_Bar(music_bar, collapse=False)
    # Returns list of tablature line strings for further processing

## `mingus.extra.tablature.from_Track` · *function*

## Summary:
Converts a musical track into a formatted tablature representation with automatic line wrapping and proper formatting.

## Description:
Transforms a Track object containing musical bars into a multi-line tablature string that displays note positions on guitar strings. The function processes each bar sequentially, applies tablature formatting, and intelligently wraps lines to respect the specified maximum width while maintaining proper musical alignment.

This function is extracted into its own component to separate the concerns of track-to-tab conversion from the core musical processing pipeline, enabling reusable tablature generation and easier maintenance of formatting logic. It handles automatic tuning detection and line wrapping to create readable tablature output.

## Args:
    track (Track): A mingus Track object containing musical bars to convert to tablature format
    maxwidth (int, optional): Maximum character width for tablature lines. Defaults to 80
    tuning (Tuning, optional): Specific tuning to use for tablature generation. If None, uses track's tuning or default. Defaults to None

## Returns:
    str: A formatted tablature string with proper line breaks and musical alignment, using OS-specific line separators

## Raises:
    FingerError: When no playable fingering can be found for notes in any bar during tablature generation

## Constraints:
    Preconditions:
    - The track parameter must be a valid mingus Track object with bars
    - Each bar in the track must be a valid Bar object with proper musical content
    - If tuning is provided, it must be a valid Tuning object with fingering capabilities
    - maxwidth must be a positive integer

    Postconditions:
    - Returns a properly formatted tablature string with consistent alignment
    - All tablature lines are properly spaced and aligned
    - Final output includes proper musical bar terminators

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start from_Track(track, maxwidth, tuning)] --> B[Initialize result = []]
    B --> C[Calculate width = _get_width(maxwidth)]
    C --> D{tuning is None?}
    D -- Yes --> E[Set tuning = track.get_tuning()]
    D -- No --> F[Use provided tuning]
    E --> G[Initialize lastlen = 0]
    F --> G
    G --> H[Iterate through track bars]
    H --> I[Call from_Bar(bar, width, tuning, collapse=False)]
    I --> J[Get barstart position from r[1].find("||") + 2]
    J --> K{((len(r[0]) + lastlen) - barstart) < maxwidth AND result != []?}
    K -- Yes --> L[Append continuation lines with proper alignment]
    K -- No --> M[Append new lines with empty separators]
    L --> N[Update lastlen = len(result[-1])]
    M --> N
    N --> O{More bars?}
    O -->|Yes| H
    O -->|No| P[Join result with os.linesep]
    P --> Q[Return formatted tablature string]
```

## Examples:
    # Basic usage with default settings
    track = Track()
    # Add bars to track...
    tablature = from_Track(track)
    # Returns formatted tablature string with 80-character width limit
    
    # Custom maximum width
    wide_tab = from_Track(track, maxwidth=120)
    # Returns tablature with wider line formatting
    
    # Custom tuning
    custom_tuning = Tuning("Standard")
    tuned_tab = from_Track(track, tuning=custom_tuning)
    # Returns tablature using specified tuning

## `mingus.extra.tablature.from_Composition` · *function*

## Summary:
Converts a musical composition into a formatted tablature representation showing note positions across multiple tracks and bars.

## Description:
Transforms a musical composition object into a text-based tablature format that displays which strings and frets should be played for each note across multiple tracks. The function processes each track in the composition, applies appropriate tunings (using default tuning when none specified), and formats the musical data into aligned tablature lines with proper timing markers.

This function is extracted into its own component to separate the concerns of composition-to-tablature conversion from the core musical data processing, enabling reusable tablature generation for compositions with multiple tracks and varying tunings.

## Args:
    composition (object): A musical composition object containing multiple tracks with musical data
        - Must be iterable (supports for loop)
        - Must have attributes: title, subtitle, author, email, description, tracks
        - Tracks should support get_tuning() method
    width (int, optional): Maximum character width for tablature formatting. Defaults to 80.

## Returns:
    str: A formatted tablature string with proper line breaks and alignment showing note positions across all tracks and bars. The output includes headers with composition metadata and properly formatted tablature lines for each bar across all tracks.

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions.

## Constraints:
    Preconditions:
    - The composition object must be iterable (support for loop)
    - Each track in composition must support get_tuning() method
    - Composition must have title, subtitle, author, email, description attributes
    - Tracks should contain musical bar data that can be processed by from_Bar function
    - default_tuning must be defined in the module scope
    
    Postconditions:
    - Returns properly formatted tablature with consistent alignment across tracks
    - All tablature lines have equal length when joined with OS line separators
    - Tablature includes proper headers with composition metadata
    - Final output includes proper bar termination markers

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start from_Composition] --> B[Collect instrument tunings]
    B --> C{Track has tuning?}
    C -- Yes --> D[Use track tuning]
    C -- No --> E[Use default_tuning]
    D --> F[Add headers with metadata]
    F --> G[Calculate width parameters]
    G --> H[Initialize bar tracking variables]
    H --> I[While barindex < maxlen]
    I --> J[For each track in composition]
    J --> K[Get track tuning]
    K --> L[Initialize ascii list]
    L --> M[For x in range(bars)]
    M --> N{barindex + x < len(tracks)?}
    N -- Yes --> O[Get bar from track]
    O --> P[Call from_Bar for bar]
    P --> Q[Process bar formatting]
    Q --> R{notfirst?}
    R -- Yes --> S[Adjust bar formatting]
    R -- No --> T[Skip adjustment]
    S --> U[Append formatted bar to ascii]
    T --> U
    U --> V[Update ascii with new content]
    V --> W[Check if notfirst and ascii not empty]
    W -- Yes --> X[Add padding lines]
    W -- No --> Y[Set notfirst = True]
    X --> Z[Add ascii lines to result]
    Y --> Z
    Z --> AA[Increment barindex]
    AA --> AB[Add blank lines to result]
    AB --> AC{barindex < maxlen?}
    AC -- Yes --> I
    AC -- No --> AD[Join result with os.linesep]
    AD --> AE[Return formatted tablature]
```

## Examples:
    # Basic usage with default width
    tablature = from_Composition(my_composition)
    # Returns formatted tablature string for entire composition
    
    # Custom width specification
    wide_tablature = from_Composition(my_composition, width=120)
    # Returns tablature with wider formatting

## `mingus.extra.tablature.from_Suite` · *function*

## Summary:
Converts a musical suite object into a formatted tablature representation containing multiple compositions with headers and horizontal dividers.

## Description:
Transforms a musical suite (collection of compositions) into a text-based tablature format that displays all compositions in sequence with proper metadata headers and visual separators. Each composition in the suite is converted using the from_Composition function, and the entire suite is formatted with a main header and horizontal rules between compositions.

This logic is extracted into its own function to separate the concerns of suite-level organization from individual composition formatting, enabling clean conversion of collections of musical compositions to tablature format without modifying core data structures.

## Args:
    suite (object): A musical suite object containing multiple compositions
        - Must have compositions attribute (used to determine count when subtitle is empty)
        - Must have title, subtitle, author, email, description attributes
        - Must be iterable (supports for loop to iterate over compositions)
    maxwidth (int, optional): Maximum character width for tablature formatting. Defaults to 80.

## Returns:
    str: A formatted tablature string containing the suite header followed by each composition's tablature representation separated by horizontal rules.

## Raises:
    None explicitly raised by this function, though underlying functions may raise exceptions.

## Constraints:
    Preconditions:
    - The suite parameter must be a valid object with compositions, title, subtitle, author, email, description attributes
    - The suite must be iterable (support for loop)
    - Each item in suite must be compatible with from_Composition function
    - maxwidth must be a positive integer
    
    Postconditions:
    - Returns properly formatted tablature with consistent alignment
    - All compositions are included in sequence with proper headers
    - Horizontal rules separate each composition
    - Final output includes proper line breaks and spacing

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start from_Suite] --> B{suite.subtitle == ""?}
    B -- Yes --> C[subtitle = str(len(suite.compositions)) + " Compositions"]
    B -- No --> D[subtitle = suite.subtitle]
    C --> E[Call add_headers with metadata]
    D --> E
    E --> F[Create horizontal rule hr = maxwidth * "="]
    F --> G[Create newline n = os.linesep]
    G --> H[Format main header section]
    H --> I[Add leading horizontal rule and spacing]
    I --> J[Initialize result with header]
    J --> K[Loop through suite compositions]
    K --> L[Call from_Composition for each composition]
    L --> M[Append composition result with separators]
    M --> N[Next composition]
    N --> K
    K --> O[End loop]
    O --> P[Return final formatted result]
```

## Examples:
    # Basic usage with default maxwidth
    suite_tablature = from_Suite(my_suite)
    # Returns formatted tablature string for entire suite
    
    # Custom width specification
    wide_suite_tablature = from_Suite(my_suite, maxwidth=100)
    # Returns suite tablature with wider formatting

## `mingus.extra.tablature._get_qsize` · *function*

## Summary:
Calculates the number of quarter-sized segments that can fit in a tablature display area based on tuning string names and available width.

## Description:
This function determines how many quarter-sized elements (representing musical note positions) can be displayed in a tablature view given the width constraint and the length of note names in the tuning. It's used internally by the tablature module to calculate appropriate display sizing for tablature notation.

The function extracts shorthand representations of notes from a tuning, calculates the space needed for note labels (plus padding), and computes how many quarter-sized segments can fit in the remaining space. This is essential for properly formatting tablature displays where each segment represents a quarter note position.

## Args:
    tuning: A tuning object containing musical notes with a `tuning` attribute that holds note objects
    width (int): The total available width for the tablature display

## Returns:
    int: The calculated number of quarter-sized segments that can fit, or 0 if insufficient space. This represents the maximum number of quarter-sized note positions that can be displayed given the width and note label lengths.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The tuning parameter must have a `tuning` attribute containing iterable note objects
    - Each note object in tuning must have a `to_shorthand()` method
    - The width parameter must be a numeric value
    
    Postconditions:
    - Returns a non-negative integer (0 or positive)
    - The returned value represents a discretized count of quarter-sized elements that can fit in the available space

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _get_qsize(tuning, width)] --> B[Extract shorthand names from tuning notes]
    B --> C[Calculate basesize = max_name_length + 3]
    C --> D[Calculate barsize = width - basesize - 2 - 1]
    D --> E[Return max(0, int(barsize / 4.5))]
```

## Examples:
    # Calculate how many quarter-sized elements fit in 80-character width
    # qsize = _get_qsize(some_tuning_object, 80)
    # Returns number of quarter-sized note positions that can be displayed
    
    # Example with narrow width - returns 0 when insufficient space
    # qsize = _get_qsize(some_tuning_object, 10)
    # Returns 0 because not enough space for note labels plus segments

## `mingus.extra.tablature._get_width` · *function*

## Summary:
Calculates an appropriate width value based on a maximum width constraint with different scaling factors for different input ranges.

## Description:
This function determines a suitable width measurement by applying different scaling rules based on the input maximum width value. It's designed to provide proportional width calculations that adapt to different size constraints, likely for formatting or display purposes in musical tablature rendering.

## Args:
    maxwidth (float or int): The maximum width constraint that determines the scaling factor to apply. This represents an upper bound for width calculation.

## Returns:
    float or int: The calculated width value based on the following rules:
        - If maxwidth <= 60: returns maxwidth unchanged
        - If 60 < maxwidth <= 120: returns maxwidth / 2  
        - Otherwise: returns maxwidth / 3

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
        - maxwidth must be a numeric value (int or float)
    Postconditions:
        - Returned value will always be less than or equal to maxwidth
        - Returned value will be greater than or equal to 0 if maxwidth >= 0

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start: _get_width(maxwidth)] --> B{maxwidth <= 60?}
    B -- Yes --> C[width = maxwidth]
    B -- No --> D{60 < maxwidth <= 120?}
    D -- Yes --> E[width = maxwidth / 2]
    D -- No --> F[width = maxwidth / 3]
    C --> G[Return width]
    E --> G
    F --> G
```

## Examples:
    # Example 1: Small maxwidth
    result = _get_width(50)  # Returns 50 (unchanged)
    
    # Example 2: Medium maxwidth  
    result = _get_width(80)  # Returns 40 (maxwidth / 2)
    
    # Example 3: Large maxwidth
    result = _get_width(150)  # Returns 50 (maxwidth / 3)
```

