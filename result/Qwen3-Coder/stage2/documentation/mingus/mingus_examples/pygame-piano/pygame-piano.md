# `pygame-piano.py`

## `mingus_examples.pygame-piano.pygame-piano.load_img` · *function*

## Summary:
Loads an image file and prepares it for display with appropriate color conversion.

## Description:
This utility function loads an image from disk using Pygame's image loading capabilities and applies the correct color conversion based on whether the image contains transparency information. It serves as a centralized image loading mechanism that ensures consistent image preparation for rendering operations.

## Args:
    name (str): The full path or filename of the image to load.

## Returns:
    tuple[pygame.Surface, pygame.Rect]: A tuple containing the loaded image as a pygame Surface object and its bounding rectangle as a pygame Rect object.

## Raises:
    SystemExit: Raised when pygame fails to load the image, typically due to file not found or unsupported format.

## Constraints:
    Precondition: The file specified by `name` must exist and be a valid image file supported by Pygame.
    Postcondition: The returned image will have appropriate color depth and transparency handling applied.

## Side Effects:
    I/O: Reads from the filesystem to load the image file.
    Memory allocation: Creates new pygame.Surface objects for the loaded image.

## Control Flow:
```mermaid
flowchart TD
    A[Start load_img] --> B{Try to load image}
    B -->|Success| C{Image has alpha?}
    C -->|Yes| D[Convert with alpha]
    C -->|No| E[Convert without alpha]
    D --> F[Return (image, rect)]
    E --> F
    B -->|Failure| G[Print error message]
    G --> H[Raise SystemExit]
```

## Examples:
```python
# Load a background image
background_image, background_rect = load_img("assets/background.png")

# Load a sprite image
sprite_image, sprite_rect = load_img("assets/player_sprite.png")
```

## `mingus_examples.pygame-piano.pygame-piano.play_note` · *function*

## Summary:
Plays a musical note on a virtual piano interface and displays chord information.

## Description:
This function handles the playback and visualization of musical notes in a pygame-based piano application. It positions notes on white and black keys, maintains a list of currently playing notes, determines chords being played, and displays chord names on screen. The function integrates with the mingus music library for note playback and chord detection.

## Args:
    note (Note): A mingus Note object representing the musical note to be played. Must have name and octave attributes.

## Returns:
    None: This function does not return any value.

## Raises:
    None explicitly raised: The function doesn't contain explicit try/except blocks or raise statements.

## Constraints:
    Preconditions:
    - The note parameter must be a valid mingus Note object with proper name and octave attributes
    - Global variables must be initialized before calling this function:
        * LOWEST: Minimum octave value for the piano keyboard
        * width: Width dimension for keyboard layout calculations  
        * WHITE_KEYS: List of white key note names
        * BLACK_KEYS: List of black key note names
        * playing_w: List tracking currently playing white keys (each item is [position, tick, note])
        * playing_b: List tracking currently playing black keys (each item is [position, tick, note])
        * tick: Current time/tick counter for note tracking
        * font: Pygame font object for text rendering
        * text: Pygame surface for displaying chord information
        * channel: MIDI channel number for sound output
    
    Postconditions:
    - The note is added to either playing_w or playing_b list with position and timing data
    - Notes are sorted by position in ascending order
    - Chord information is determined and displayed on the text surface
    - The note is played via fluidsynth

## Side Effects:
    - Modifies global lists playing_w and playing_b by appending note data [position, tick, note]
    - Renders text to the global text surface using pygame
    - Calls fluidsynth.play_Note() to produce audio output
    - Updates the display with rendered chord information

## Control Flow:
```mermaid
flowchart TD
    A[Start play_note] --> B{note.name in WHITE_KEYS?}
    B -- Yes --> C[Calculate white key position]
    B -- No --> D[Calculate black key position]
    C --> E[Add to playing_w]
    D --> F[Add to playing_b]
    E --> G[Combine playing_w + playing_b]
    F --> G
    G --> H[Sort notes by position]
    H --> I[Extract note names from note objects]
    I --> J[Determine chords using mingus.chords.determine()]
    J --> K{Chord detected?}
    K -- Yes --> L[Set det = first chord from determine result]
    K -- No --> M[Set det = ""]
    L --> N[Render chord text with pygame.font.render()]
    M --> N
    N --> O[Fill text surface with white background]
    O --> P[Blit rendered text to text surface]
    P --> Q[Play note via fluidsynth.play_Note()]
    Q --> R[End]
```

## Examples:
    # Typical usage in a pygame event loop:
    # for event in pygame.event.get():
    #     if event.type == pygame.KEYDOWN:
    #         note = Note("C", 4)
    #         play_note(note)

