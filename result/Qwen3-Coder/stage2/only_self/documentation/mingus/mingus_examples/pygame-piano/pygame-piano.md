# `pygame-piano.py`

## `mingus_examples.pygame-piano.pygame-piano.load_img` · *function*

## Summary:
Loads and prepares an image surface for use in pygame applications with appropriate color conversion.

## Description:
This utility function loads an image file using pygame's image loading capabilities and applies the correct color conversion based on whether the image contains transparency information. It ensures optimal performance and compatibility with pygame's rendering system by converting images appropriately.

The function is extracted as a separate utility to encapsulate the common pattern of loading images with proper error handling and conversion, preventing code duplication throughout the application.

## Args:
    name (str): The full path or filename of the image to load.

## Returns:
    tuple[pygame.Surface, pygame.Rect]: A tuple containing the loaded image surface and its rectangular bounding box.

## Raises:
    SystemExit: Raised when pygame fails to load the specified image file, with an error message printed to standard output.

## Constraints:
    Precondition: The file specified by 'name' must exist and be a valid image format supported by pygame.
    Postcondition: The returned image surface is properly converted for optimal pygame rendering performance.

## Side Effects:
    I/O: Reads from the filesystem to load the image file.
    Standard Output: Prints error messages to stdout when image loading fails.

## Control Flow:
```mermaid
flowchart TD
    A[Start load_img] --> B{Try to load image}
    B -->|Success| C{Image has alpha channel?}
    C -->|No| D[Convert image]
    C -->|Yes| E[Convert image with alpha]
    D --> F[Return (image, rect)]
    E --> F
    B -->|Failure| G[Print error message]
    G --> H[Raise SystemExit]
```

## Examples:
```python
# Basic usage
try:
    image, rect = load_img("assets/player.png")
    screen.blit(image, rect)
except SystemExit:
    print("Failed to load image, exiting...")
```

## `mingus_examples.pygame-piano.pygame-piano.play_note` · *function*

## Summary:
Plays a musical note on a virtual piano interface and displays detected chord information.

## Description:
Handles the playback of a single musical note within a pygame-based piano application. This function manages the visual representation of notes on the piano keyboard, tracks currently playing notes, detects chords formed by simultaneous notes, and renders chord names to the display while playing the note through MIDI synthesis.

## Args:
    note (mingus.containers.Note): The musical note to be played, containing note name and octave information.

## Returns:
    None: This function does not return any value.

## Raises:
    None explicitly raised: The function doesn't contain try/except blocks or explicit raise statements.

## Constraints:
    Preconditions:
    - Global variables must be initialized: text, playing_w, playing_b, width, LOWEST, WHITE_KEYS, BLACK_KEYS, white_key_width, tick, font, channel
    - The note parameter must be a valid mingus Note object with proper name and octave attributes
    - Note name must be either in WHITE_KEYS or BLACK_KEYS constants
    - The LOWEST constant defines the lowest playable octave
    - WHITE_KEYS and BLACK_KEYS are lists defining valid note names for each key type
    
    Postconditions:
    - The note is added to either playing_w or playing_b list based on key type
    - The note's position is calculated based on octave and key type
    - Chord detection is performed and displayed on the text surface
    - The note is played through fluidsynth MIDI synthesis

## Side Effects:
    - Modifies global lists playing_w and playing_b by appending [position, tick, note] tuples
    - Renders text to the global pygame surface text
    - Calls fluidsynth.play_Note() which likely makes MIDI system calls
    - Updates the pygame display through text rendering operations

## Control Flow:
```mermaid
flowchart TD
    A[Start play_note] --> B{Note name in WHITE_KEYS?}
    B -- Yes --> C[Calculate white key position using index]
    B -- No --> D[Calculate black key position using hardcoded values]
    C --> E[Append [w, tick, note] to playing_w]
    D --> F[Append [w, tick, note] to playing_b]
    E --> G[Combine playing_w + playing_b]
    F --> G
    G --> H[Sort notes by position]
    H --> I[Extract note names from sorted notes]
    I --> J[Determine chords from note names]
    J --> K{Chord detected?}
    K -- Yes --> L[Set det = first chord]
    K -- No --> M[Set det = ""]
    L --> N[Render chord text to surface]
    M --> N
    N --> O[Fill text surface with white color]
    O --> P[Blit rendered text to text surface]
    P --> Q[Play note via fluidsynth]
    Q --> R[End]
```

## Examples:
    # Typical usage in a pygame event loop
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            note = Note("C", 4)
            play_note(note)

