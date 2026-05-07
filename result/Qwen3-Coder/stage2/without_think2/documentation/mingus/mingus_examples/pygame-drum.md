# `mingus_examples.pygame-drum`

## Tree:
    pygame-drum/
    └── pygame-drum.py

## Role:
    Manages audio playback and visual representation of drum sequences using Pygame and FluidSynth

## Description:
This module provides the core functionality for a drum sequencer application that combines visual feedback with MIDI sound synthesis. It handles both the graphical interface elements (loading and displaying images) and the audio playback mechanisms (using FluidSynth) for drum patterns.

The module is specifically designed for the pygame-drum example within the mingus_examples collection, serving as the primary implementation for creating interactive drum sequencing experiences. It integrates with the broader mingus music theory library for note handling and with Pygame for graphics rendering.

## Components:
    - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]
    - play_note(note: Note) -> None

```mermaid
graph TD
    A[load_img] --> B[pygame.image.load]
    A --> C[pygame.Surface.convert_alpha]
    A --> D[pygame.Surface.convert]
    B --> C
    B --> D
    C --> E[Return (surface, rect)]
    D --> E
    E --> F[Main loop uses image for rendering]
    F --> G[play_note]
    G --> H[fluidsynth.play_Note]
    G --> I[Global recording buffers]
    H --> J[Audio output]
    I --> K[Recording management]
```

## Public API:
    - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]
        Loads an image file and returns a Pygame surface with proper format conversion for display compatibility.
        Usage: Call with a valid image file path to get a surface and rectangle for positioning in the UI.
        
    - play_note(note: Note) -> None
        Plays a musical note using FluidSynth and optionally records it for playback.
        Usage: Pass a mingus Note object to trigger audio playback. When recording mode is active, note events are logged.

## Dependencies:
    - Internal: None
    - External: 
        - pygame: Used for image loading, surface management, and display operations
        - fluidsynth: Provides MIDI synthesis capabilities for audio playback
        - mingus.containers.Note: For musical note representation and handling
        - sys: For system-level operations like exiting on errors

## Constraints:
    - The load_img function requires valid file paths and will terminate the program if images fail to load
    - The play_note function depends on global variables being properly initialized (status, playing, recorded, recorded_buffer, tick)
    - Both functions assume proper setup of Pygame display and FluidSynth environment
    - Thread safety is not guaranteed; functions should be called from the main thread

---

## Files

- [`pygame-drum.py`](pygame-drum/pygame-drum.md)

