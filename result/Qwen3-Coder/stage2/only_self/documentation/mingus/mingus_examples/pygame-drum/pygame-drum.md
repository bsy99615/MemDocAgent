# `pygame-drum.py`

## `mingus_examples.pygame-drum.pygame-drum.load_img` · *function*

## Summary:
Loads and prepares an image surface for display in pygame with appropriate color conversion based on transparency support.

## Description:
This function loads an image file using pygame's image loading capabilities and applies the appropriate surface conversion to ensure proper rendering. It handles both transparent and opaque images by checking for alpha channels and converting surfaces accordingly. The function is designed to be a centralized image loading utility that ensures consistent image preparation across the application.

## Args:
    name (str): The full path or filename of the image to load.

## Returns:
    tuple[pygame.Surface, pygame.Rect]: A tuple containing the loaded image surface and its rectangular bounding box.

## Raises:
    SystemExit: Raised when pygame fails to load the image file, causing the application to terminate.

## Constraints:
    Preconditions:
        - The image file must exist at the specified path
        - The image file must be in a format supported by pygame
    Postconditions:
        - The returned surface is properly converted for optimal rendering
        - The returned rectangle represents the image dimensions

## Side Effects:
    - File I/O operation to read the image file
    - Prints error message to standard output when image loading fails

## Control Flow:
```mermaid
flowchart TD
    A[Start load_img] --> B{Try to load image}
    B -- Success --> C{Image has alpha channel?}
    C -- Yes --> D[Convert with alpha]
    C -- No --> E[Convert without alpha]
    D --> F[Return (image, rect)]
    E --> F
    B -- Failure --> G[Print error message]
    G --> H[Raise SystemExit]
```

## Examples:
```python
# Load a background image
background, rect = load_img("assets/background.png")

# Load a drum sprite
drum_sprite, rect = load_img("assets/drum.png")
```

## `mingus_examples.pygame-drum.pygame-drum.play_note` · *function*

## Summary:
Plays a musical note through fluidsynth audio system while mapping specific notes to drum sound indices.

## Description:
This function implements the core note playback functionality for the pygame-drum system. It maps specific musical notes to predefined drum sound indices (0-8) and plays them using the fluidsynth audio engine. The function contains a logical error where it references an undefined global variable `status` in its conditional recording logic.

The function is designed to handle a fixed set of musical notes that correspond to different drum sounds, serving as a bridge between the musical note representation and the audio playback system.

## Args:
    note (Note): A musical note object from the mingus.containers module specifying the pitch and octave to be played.

## Returns:
    None: This function does not return any value.

## Raises:
    ValueError: If the note parameter is invalid or unsupported by the fluidsynth system.
    RuntimeError: If fluidsynth fails to initialize or play the note.
    TypeError: If the note parameter is of an incompatible type.

## Constraints:
    Preconditions:
    - The fluidsynth audio system must be properly initialized and configured
    - The note parameter must be a valid Note object from mingus.containers
    - Global variables `status`, `playing`, `recorded`, `recorded_buffer`, and `tick` must be defined and accessible
    - When in recording mode (status == "record"), the recording-related global lists must be initialized
    
    Note: The function contains a logical error - it references an undefined global variable `status` which would cause a NameError at runtime.

    Postconditions:
    - The specified note will be played through the fluidsynth audio system
    - If recording were properly implemented, the note event would be added to recording buffers
    - No state changes occur in the calling application beyond audio playback

## Side Effects:
    - Audio output through the system's default audio device via fluidsynth
    - Potential initialization of fluidsynth audio subsystem if not already running
    - Possible blocking behavior while audio is being processed

## Control Flow:
```mermaid
flowchart TD
    A[play_note called with note] --> B{Note matches predefined mapping?}
    B -- Yes --> C[Set index to corresponding value]
    B -- No --> D[Set index to None]
    D --> E{index != None AND status == "record"?}
    E -- Yes --> F[Add to playing buffer]
    F --> G[Add to recorded buffer]
    G --> H[Add to recorded_buffer]
    E -- No --> I[Skip recording]
    I --> J[Play note via fluidsynth]
    C --> E
    J --> K[End]
```

## Examples:
    # Basic note playback
    note = Note("C", 2)
    play_note(note)
    
    # In recording mode, note would also be stored in recording buffers
    # (requires proper global variable setup)

