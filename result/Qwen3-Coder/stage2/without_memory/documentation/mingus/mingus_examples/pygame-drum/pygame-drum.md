# `pygame-drum.py`

## `mingus_examples.pygame-drum.pygame-drum.load_img` · *function*

## Summary:
Loads and prepares an image file for display in a pygame application, handling proper color conversion based on transparency.

## Description:
This function loads an image file using pygame's image loading capabilities and ensures proper color format conversion. It automatically detects if the image has an alpha channel and applies the appropriate conversion method to optimize rendering performance. The function is designed to be a centralized utility for image loading throughout the pygame application.

## Args:
    name (str): The full path or filename of the image to load.

## Returns:
    tuple[pygame.Surface, pygame.Rect]: A tuple containing the loaded image as a pygame Surface object and its bounding rectangle as a pygame Rect object.

## Raises:
    SystemExit: Raised when pygame fails to load the image file, causing the application to terminate with an error message.

## Constraints:
    Precondition: The file specified by 'name' must exist and be a valid image file that pygame can load.
    Postcondition: The returned image is properly converted for optimal rendering performance based on its transparency characteristics.

## Side Effects:
    I/O: Reads from the filesystem to load the image file.
    Error Output: Prints an error message to standard output when image loading fails.

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
# Basic usage
try:
    image, rect = load_img("assets/drum_kit.png")
    screen.blit(image, rect)
except SystemExit:
    print("Failed to load image, exiting...")
```

## `mingus_examples.pygame-drum.pygame-drum.play_note` · *function*

## Summary:
Plays a musical note using fluidsynth and records the note event when in recording mode.

## Description:
This function translates specific musical notes into numeric indices and plays them through the fluidsynth MIDI synthesizer. When the application is in "record" mode, it also logs the note event with timing information for later playback or analysis. The function handles a predefined set of musical notes mapped to specific indices.

## Args:
    note (Note): A musical note object from the mingus.containers library to be played

## Returns:
    None: This function does not return any value

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The `note` parameter must be a valid Note object from mingus.containers
    - Global variables `status`, `playing`, `recorded`, `recorded_buffer`, and `tick` must be defined in the global scope
    - The application must be properly initialized with fluidsynth for audio playback
    - The `status` variable must be a string that can be compared to "record"
    
    Postconditions:
    - The specified note is played through the MIDI synthesizer using fluidsynth
    - If in recording mode (status == "record"), the note event is added to global recording buffers:
      * `playing` list receives [index, tick] 
      * `recorded` list receives [index, tick, note]
      * `recorded_buffer` list receives [index, tick]

## Side Effects:
    - Audio output through the MIDI synthesizer via fluidsynth.play_Note()
    - Modification of global lists: `playing`, `recorded`, `recorded_buffer` when in recording mode
    - Access to global variable `tick` for timing information

## Control Flow:
```mermaid
flowchart TD
    A[Start play_note] --> B{note matches known note?}
    B -- Yes --> C[Set index]
    B -- No --> D[Set index = None]
    C --> E{index != None AND status == "record"?}
    E -- Yes --> F[Add [index, tick] to playing]
    F --> G[Add [index, tick, note] to recorded]
    G --> H[Add [index, tick] to recorded_buffer]
    E -- No --> I[Continue]
    D --> J[Continue]
    I --> K[Play note with fluidsynth]
    H --> K
    J --> K
    K --> L[End]
```

## Examples:
    # Basic usage - plays a note without recording
    note = Note("C", 4)
    play_note(note)
    
    # Usage in recording mode - plays note and records event
    status = "record"
    play_note(Note("B", 2))  # Maps to index 0, plays note, and records [0, tick] in all buffers
    
    # Usage in non-recording mode - plays note but doesn't record
    status = "play"
    play_note(Note("A", 3))  # Maps to index 5, plays note, but doesn't modify recording buffers
```

