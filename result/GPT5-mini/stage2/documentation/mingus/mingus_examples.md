# `mingus_examples`

## Tree:
mingus_examples/
├── pygame-drum/
│   └── pygame-drum.py
└── pygame-piano/
    └── pygame-piano.py

## Role:
Provide a single, discoverable collection of small Pygame + Fluidsynth example programs and lightweight runtime helpers that demonstrate how to wire Mingus note objects into on-screen visuals and audio playback.

## Description:
- Where and when this module is used:
  - This package is an examples collection. Its modules are intended to be run by a developer exploring the repository or by an examples runner that enumerates and executes example scripts.
  - Primary consumers:
    - Humans running examples interactively (e.g., python mingus_examples/pygame-piano/pygame-piano.py)
    - Small example runners that import and launch the demo modules
    - Developers reading the code to learn how to integrate Pygame rendering, Mingus note objects, and Fluidsynth playback
- Why these components are grouped:
  - Cohesion principle: both subpackages demonstrate the same integration concern — presenting note events visually via Pygame and producing sound via Fluidsynth — and therefore belong together under a single examples namespace. Grouping keeps demo-specific glue code separated from the core library and from reusable utilities.

## Components:
- Public subpackages / scripts (with primary exported symbols)
  - mingus_examples.pygame-drum
    - load_img(name: str) -> (pygame.Surface, pygame.Rect)
    - play_note(note) -> None
    - Role: small runtime helpers for a drum-pad demo (asset loading; play and optional record helper)
    - Behavior summary:
      - play_note triggers audio playback by calling fluidsynth.play_Note(note, channel=9, velocity=100).
      - If module-level recording is enabled (status == "record"), play_note also appends timestamped entries to module-level recording lists to capture played pads.
    - Required module-level globals (when recording behavior is used or when imported):
      - status: str — controller status string; set to "record" to enable recording behavior
      - playing: list[list[int, number]] — appended with [index, tick] when recording
      - recorded: list[list[int, number, Note]] — appended with [index, tick, note] when recording
      - recorded_buffer: list[list[int, number]] — appended with [index, tick] when recording
      - tick: int | float — current timestamp/tick used when recording
    - Note: When executed as a standalone script the module may set up its own recording lists; when imported, callers must create and maintain these globals before invoking play_note if recording is required.
    - See detailed component-level docs: mingus_examples/pygame-drum (memory entry)
  - mingus_examples.pygame-piano
    - load_img(name: str) -> (pygame.Surface, pygame.Rect)
    - play_note(note) -> None
    - Role: a compact interactive piano demo that maps keyboard/MIDI input to visuals and Fluidsynth audio
    - Required module-level globals (must be present before calling play_note if the caller is not using the module's own initialization code):
      - LOWEST: int — lowest reference octave for computing visual offsets
      - width: int | float — horizontal pixel width per octave (scale)
      - white_key_width: int | float — pixel width of a single white key
      - WHITE_KEYS: list[str] — ordered white-key names (e.g., ['C','D','E','F','G','A','B'])
      - BLACK_KEYS: list[str] — ordered black-key names (e.g., ['C#','D#','F#','G#','A#'])
      - playing_w: list[list[float, number, Note]] — active white-key visual entries [x_position, tick, note]
      - playing_b: list[list[float, number, Note]] — active black-key visual entries [x_position, tick, note]
      - tick: int | float — current time/tick used for visual timestamps
      - font: object — font-like object exposing render(text, antialias, color) -> Surface
      - text: pygame.Surface-like — Surface used to draw the current chord name (supports fill and blit)
      - channel: int — MIDI channel forwarded to fluidsynth.play_Note
    - Initialization note: When run as the example script, the module's script-level initialization typically prepares these globals. If the module is imported (not executed), callers must initialize the above globals before calling play_note.
    - See detailed component-level docs: mingus_examples/pygame-piano (memory entry)

Mermaid dependency graph (high-level relations among internal components and shared external libs):
graph LR
    pygame_drum["pygame-drum module"] -->|uses| pygame[pygame]
    pygame_drum -->|uses| fluidsynth[fluidsynth]
    pygame_piano["pygame-piano module"] -->|uses| pygame
    pygame_piano -->|uses| fluidsynth
    pygame_piano -->|uses| chords_module[chords]
    pygame_drum -->|expected to be driven by| app_higher_level[application entry point / UI]
    pygame_piano -->|expected to be driven by| app_higher_level
    pygame -->|provides| Surface[Surface/Rect/fonts]
    fluidsynth -->|provides| play_Note[play_Note API]
    chords_module -->|provides| determine[chord inference]

## Public API:
- Package-level:
  - mingus_examples.pygame-drum (script/module)
    - Primary exported functions:
      - load_img(name: str) -> (pygame.Surface, pygame.Rect)
        - Brief: Load an image and return a display-optimized Surface and its Rect.
        - Usage note: Best called after initializing pygame and (ideally) after pygame.display.set_mode(...). Raises SystemExit wrapping pygame.error on failure.
      - play_note(note) -> None
        - Brief: Play a drum note via fluidsynth.play_Note(note, channel=9, velocity=100) and, if enabled, append timestamped events to module-level recording lists.
        - Usage note: Recording behavior depends on module-level globals (status, playing, recorded, recorded_buffer, tick). When used as a script these are often prepared by the module; when imported, callers must provide them.
  - mingus_examples.pygame-piano (script/module)
    - Primary exported functions:
      - load_img(name: str) -> (pygame.Surface, pygame.Rect)
        - Brief: Load and convert an image for fast blitting; return (Surface, Rect).
        - Usage note: Raises SystemExit on image-load failure; conversion benefits from an initialized display.
      - play_note(note) -> None
        - Brief: Handle a single note event: update visual playing lists, update chord-name surface, and call fluidsynth.play_Note(note, channel, velocity).
        - Usage note: Requires the visual and audio module-level globals listed above to be initialized. If the module is executed as a script it typically initializes them; if imported, callers must set them.

## Dependencies:
- Internal (repository):
  - chords (used by pygame-piano for chord inference)
    - Purpose: infer chord names from a set of currently playing note names (used to update on-screen chord text)
- External (third-party):
  - pygame
    - Purpose: windowing, rendering, image loading, Surfaces/Rects, fonts, event loop. Both examples use pygame for visuals and asset loading.
  - fluidsynth (Python bindings)
    - Purpose: play_Note API to produce audio from Note objects.
  - mingus (containers/types)
    - Purpose: Note-like objects expected by play_note functions (objects exposing .name and .octave or compatible equality semantics).

## Constraints:
- Initialization ordering:
  - Initialize pygame (and preferably call pygame.display.set_mode(...)) before calling load_img to ensure convert()/convert_alpha() returns display-optimized Surfaces.
  - Initialize and configure Fluidsynth (and select a channel) before invoking play_note to ensure audio playback.
  - For pygame-piano, either run the module as the example script (which typically initializes visual globals) or, if importing the module, ensure the listed module-level globals are initialized before calling play_note.
- Module-level state contract:
  - Several example functions rely on module-level globals (lists, tick counters, status flags). Callers or the script's init code must create and maintain these variables; absence will raise NameError or other runtime errors.
- Thread-safety:
  - Not thread-safe. Pygame and Fluidsynth interactions should be performed on the main thread or protected by caller-managed synchronization.
- Error handling:
  - load_img prints an error and raises SystemExit on failure; callers that need to survive should catch SystemExit and provide fallbacks.
  - play_note functions do not catch exceptions from external libraries (e.g., chords.determine or fluidsynth.play_Note); these exceptions propagate to callers.
- Input expectations:
  - play_note functions expect Note-like objects with .name (string) and .octave (int) or compatible equality semantics. If a note name is not found in the expected key lists, indexing operations will raise ValueError.

## Links to component-level documentation:
- mingus_examples/pygame-drum (component-level summary in memory)
- mingus_examples/pygame-piano (component-level summary in memory)

