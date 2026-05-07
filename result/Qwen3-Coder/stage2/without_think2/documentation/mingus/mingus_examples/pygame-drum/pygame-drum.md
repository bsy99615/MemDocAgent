# `pygame-drum.py`

## `mingus_examples.pygame-drum.pygame-drum.load_img` · *function*

## Summary:
Loads and processes a Pygame image file, ensuring proper color format conversion for display compatibility.

## Description:
This function loads an image file using Pygame and automatically converts it to an appropriate pixel format based on whether the image contains transparency information. It centralizes image loading logic with proper error handling and format conversion, making it easier to manage image resources consistently throughout the application.

## Args:
    name (str): The file path to the image to be loaded.

## Returns:
    tuple: A tuple containing (pygame.Surface, pygame.Rect) where the Surface is the loaded image and Rect represents its bounding rectangle for positioning.

## Raises:
    SystemExit: When a pygame.error occurs during image loading, indicating the image file could not be loaded.

## Constraints:
    Precondition: The file path provided must be valid and accessible.
    Postcondition: The returned surface will be in a format compatible with Pygame's display surface.

## Side Effects:
    I/O: Reads from the file system to load the image file.
    Prints an error message to stdout if image loading fails.

## Control Flow:
```mermaid
flowchart TD
    A[Start load_img] --> B{Try to load image}
    B -->|Success| C{Image has alpha?}
    C -->|Yes| D[Convert with alpha]
    C -->|No| E[Convert without alpha]
    D --> F[Return (image, rect)]
    E --> F
    B -->|Failure| G[Print error]
    G --> H[Raise SystemExit]
```

## Examples:
```python
# Load an image file
try:
    img_surface, img_rect = load_img("assets/player.png")
    # Use the image in rendering
    screen.blit(img_surface, img_rect)
except SystemExit:
    # Handle image loading failure
    print("Failed to load image")
```

## `mingus_examples.pygame-drum.pygame-drum.play_note` · *function*

## Summary:
Plays a musical note using fluidsynth and records it if in recording mode.

## Description:
The play_note function translates specific musical notes into drum pad indices and plays them through the fluidsynth MIDI synthesizer. When in recording mode, it also tracks the note events in various recording buffers for later playback or analysis. This function serves as the core note-playing mechanism for the drum sequencer application.

The function is extracted from inline code to provide a centralized location for note playback logic and recording management. This separation allows for cleaner code organization and makes it easier to modify playback behavior or recording functionality independently.

## Args:
    note (Note): A mingus Note object representing the musical note to be played. Must be one of the predefined drum notes: B2, A2, G2, E2, C2, A3, B3, A#2, G#2

## Returns:
    None: This function does not return any value

## Raises:
    None explicitly raised: The function relies on fluidsynth.play_Note for MIDI playback, which may raise exceptions internally

## Constraints:
    Preconditions: 
    - The note parameter must be a valid mingus Note object
    - Global variables 'status', 'playing', 'recorded', 'recorded_buffer', and 'tick' must be defined in the global scope
    - The 'status' variable must be set to "record" to enable recording functionality
    
    Postconditions:
    - The note is played through the fluidsynth MIDI synthesizer
    - If recording is enabled, the note event is added to recording buffers

## Side Effects:
    - Audio output through the MIDI synthesizer via fluidsynth.play_Note
    - Global state modifications when recording is enabled:
      * Appends to the global 'playing' list with [index, tick] format
      * Appends to the global 'recorded' list with [index, tick, note] format  
      * Appends to the global 'recorded_buffer' list with [index, tick] format

## Control Flow:
```mermaid
flowchart TD
    A[play_note called] --> B{note matches known drum pattern?}
    B -->|Yes| C[Set index value]
    B -->|No| D[Set index = None]
    D --> E{index != None AND status == "record"?}
    E -->|Yes| F[Append to playing, recorded, recorded_buffer]
    E -->|No| G[Skip recording]
    C --> G
    G --> H[Play note via fluidsynth.play_Note]
```

## Examples:
```python
# Basic usage - play a note
from mingus.containers import Note
note = Note("B", 2)
play_note(note)

# In recording mode - note will be recorded
status = "record"
play_note(Note("C", 2))  # Will be added to recording buffers
```

