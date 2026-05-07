# `pygame-drum.py`

## `mingus_examples.pygame-drum.pygame-drum.load_img` · *function*

## Summary:
Loads and prepares a Pygame image with appropriate color conversion based on alpha channel presence.

## Description:
This function handles the loading of image files using Pygame while ensuring proper color format conversion. It automatically detects whether an image contains an alpha channel and applies the appropriate conversion method to optimize rendering performance. The function also includes robust error handling for missing or corrupted image files.

## Args:
    name (str): The full path or filename of the image to load.

## Returns:
    tuple[pygame.Surface, pygame.Rect]: A tuple containing the loaded image surface and its rectangular bounding box for positioning.

## Raises:
    SystemExit: Raised when pygame fails to load the image file, typically due to file not found or corrupted image data.

## Constraints:
    Preconditions:
        - The file specified by `name` must exist and be readable
        - The file must be a valid image format supported by Pygame
    Postconditions:
        - The returned image surface is properly converted for optimal rendering
        - The returned rectangle represents the image dimensions and position

## Side Effects:
    - Reads from the filesystem to load the image file
    - Prints error message to standard output when image loading fails

## Control Flow:
```mermaid
flowchart TD
    A[Start load_img] --> B{Load image with pygame}
    B --> C{pygame.error caught?}
    C -->|Yes| D[Print error message]
    D --> E[Raise SystemExit]
    C -->|No| F{Has alpha channel?}
    F -->|Yes| G[Convert with convert_alpha()]
    F -->|No| H[Convert with convert()]
    G --> I[Return (image, rect)]
    H --> I
    I --> J[End]
```

## Examples:
```python
# Load a background image
background, rect = load_img("assets/background.png")
screen.blit(background, rect)

# Load a sprite image
sprite, rect = load_img("assets/player_sprite.png")
# Use sprite and rect for rendering
```

## `mingus_examples.pygame-drum.pygame-drum.play_note` · *function*

## Summary:
Plays a musical note using fluidsynth and conditionally records the note event for sequencing.

## Description:
The `play_note` function handles playback of musical notes by mapping specific Note objects to indexed representations for recording purposes, then delegates actual note playback to the fluidsynth library. This function is designed for use in a musical application where notes can be both played and recorded for later playback or sequencing.

The function implements a fixed mapping of specific musical notes to integer indices (0-8) that are used for recording purposes. When the application is in recording mode, note events are stored in global recording buffers along with timing information.

## Args:
    note (mingus.containers.Note): A musical note object to be played. The function specifically handles these predefined notes: B2, A2, G2, E2, C2, A3, B3, A#2, G#2.

## Returns:
    None: This function does not return any value.

## Raises:
    Exception: May raise exceptions from the underlying `fluidsynth.play_Note` function if MIDI playback fails.

## Constraints:
    Preconditions:
    - The `note` parameter must be a valid Note object from the mingus library
    - Global variables `status`, `playing`, `recorded`, `recorded_buffer`, and `tick` must be defined in the calling scope
    - The underlying MIDI system must be properly initialized for fluidsynth to function
    - The note must be one of the nine predefined notes in the mapping table

    Postconditions:
    - The specified note will be played through the MIDI system on channel 9 with velocity 100
    - If recording is enabled (`status == "record"`), the note event will be stored in recording buffers with timing information
    - The note will be played with the specified MIDI channel and velocity parameters

## Side Effects:
    - Produces audible sound through configured audio output devices via fluidsynth
    - Modifies global recording buffers (`playing`, `recorded`, `recorded_buffer`) when recording is enabled
    - May cause I/O operations if audio recording is enabled

## Control Flow:
```mermaid
flowchart TD
    A[play_note called with note] --> B{Note matches predefined mapping?}
    B -->|Yes| C[Set index for note]
    B -->|No| D[Set index = None]
    C --> E{index != None AND status == "record"?}
    E -->|Yes| F[Append [index, tick] to playing]
    F --> G[Append [index, tick, note] to recorded]
    G --> H[Append [index, tick] to recorded_buffer]
    E -->|No| I[Skip recording]
    D --> J[Skip recording]
    I --> K[Play note via fluidsynth.play_Note]
    H --> K
    J --> K
    K --> L[End]
```

## Examples:
```python
# Basic note playback
from mingus.containers import Note
note = Note("C", 4)
play_note(note)  # Plays the note but won't be recorded due to no matching index

# In a recording context (requires proper global variable setup)
status = "record"
tick = 100
playing = []
recorded = []
recorded_buffer = []
play_note(Note("B", 2))  # Plays B2 and records it with index 0
```

