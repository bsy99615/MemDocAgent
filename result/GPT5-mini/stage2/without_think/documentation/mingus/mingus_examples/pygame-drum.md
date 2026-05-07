# `mingus_examples.pygame-drum`

## Tree:
pygame-drum/
└── pygame-drum.py

## Role:
Provide small runtime utilities for a simple Pygame-based drum pad example: one helper to load/prepare image assets for fast blitting, and one helper to play/record drum notes via Fluidsynth.

## Description:
- Where and when this module is used:
  - This module is used during the initialization and runtime of a small Pygame drum-pad demo. Typical consumers are the application entry point or UI/input handlers which:
    - load graphics to display drum pads or UI elements (calls load_img)
    - trigger audio playback and optionally record played pads (calls play_note)
  - It is a focused helper module: it does not implement the main loop, input dispatching, or UI layout — those responsibilities live in the application's higher-level code.

- Why these components are grouped:
  - Cohesion principle: both utilities are small runtime helpers needed by the Pygame-based drum example and share the same execution context (Pygame display & Fluidsynth audio). Grouping keeps all demo-specific integrations (asset loading and note playback/recording) in a single, easy-to-find module separate from core library code.

## Components:
- load_img(name: str) -> (pygame.Surface, pygame.Rect)
  - Loads an image from disk, converts it (convert() or convert_alpha()) for fast blitting, and returns the Surface and its Rect.

- play_note(note)
  - Plays the provided Note through Fluidsynth (channel 9, velocity 100). If the note matches a hard-coded mapping and the module is in record mode, appends timestamped events to module-level recording lists.

- Module-level globals (expected by play_note; not defined inside this module snippet but required by callers)
  - status (str) — controller status string; compared against "record"
  - playing (list) — mutable list appended with [index, tick] when recording
  - recorded (list) — mutable list appended with [index, tick, note] when recording
  - recorded_buffer (list) — mutable list appended with [index, tick] when recording
  - tick (int/number) — timestamp value used when recording

Mermaid dependency graph:
graph LR
    load_img -->|uses| pygame
    play_note -->|uses| fluidsynth
    play_note -->|reads/writes| module_globals[Module-level globals: status, playing, recorded, recorded_buffer, tick]
    module_globals -->|expected by| play_note
    pygame -->|runtime requirement| display_init[pygame.display.set_mode (recommended for optimal conversion)]

## Public API:
- load_img(name: str) -> (pygame.Surface, pygame.Rect)
  - Description: Load an image file and return a display-optimized Surface and its Rect. Uses convert_alpha() if the image has per-pixel alpha; otherwise uses convert().
  - Usage notes:
    - Pass a filesystem path accepted by pygame.image.load (PNG/JPEG/BMP depending on SDL_image).
    - If pygame.display has been initialized via pygame.display.set_mode(...), convert()/convert_alpha() will produce Surfaces optimized for blitting to the display.
    - On error (pygame.error during load/convert), the function prints an error message and raises SystemExit containing the original pygame.error.

- play_note(note)
  - Description: Play a note via fluidsynth.play_Note(note, channel=9, velocity=100). If the note equals one of several hard-coded Note(...) values and status == "record", append timestamped entries to playing, recorded, and recorded_buffer.
  - Usage notes:
    - The note argument should be a mingus.containers.Note or a compatible object whose equality compares as expected.
    - The function always calls fluidsynth.play_Note; it does not return a value.
    - To enable recording behavior, ensure module-level globals (status, playing, recorded, recorded_buffer, tick) exist and status is set to "record".
    - If these globals are missing, calling code will raise NameError.

- Module-level globals (for callers who manage recording):
  - status: str — set to "record" to enable recording.
  - playing: list — entries appended as [index, tick].
  - recorded: list — entries appended as [index, tick, note].
  - recorded_buffer: list — entries appended as [index, tick].
  - tick: int or numeric — current tick/time used for timestamps.

## Dependencies:
- Internal (other repo modules):
  - None required within the repository for these two helpers. They are small demo utilities and interact with external libraries and module-level state supplied by the application.

- External (third-party libraries):
  - pygame
    - Purpose: load image assets (pygame.image.load), operate on Surfaces and Rects, and (optionally) rely on display format conversion via convert()/convert_alpha().
  - mingus.containers.Note (or mingus library)
    - Purpose: play_note expects Note objects (or compatible) and compares incoming notes against Note(...) instances for mapping to drum-pad indices.
  - fluidsynth (fluidsynth.play_Note)
    - Purpose: audio/MIDI playback; play_note calls fluidsynth.play_Note(note, 9, 100).
  - Builtins:
    - SystemExit is raised by load_img on image load/convert failure.

## Constraints:
- Initialization:
  - pygame must be importable. For best performance, initialize the video display with pygame.display.set_mode(...) before calling load_img so convert()/convert_alpha() produces display-optimized surfaces.
  - fluidsynth must be importable and initialized appropriately so fluidsynth.play_Note(...) is callable.

- Module-level state:
  - play_note expects certain module-level globals (status, playing, recorded, recorded_buffer, tick) to already exist if recording behavior is required. Callers are responsible for creating and maintaining these lists and for updating tick.

- Error handling and control flow:
  - load_img will print an error message and raise SystemExit wrapping the underlying pygame.error on any load/convert failure. Callers who must survive missing assets should catch SystemExit and implement fallback logic.
  - play_note does not handle exceptions from fluidsynth.play_Note; such exceptions will propagate to the caller.

- Thread-safety:
  - Not thread-safe. Pygame and Fluidsynth are generally not safe to call from multiple threads without explicit synchronization; callers should perform calls from the main thread (or otherwise ensure proper locking).

- Ordering:
  - For optimal behavior, perform pygame initialization (including display mode) before loading images.
  - Initialize or configure Fluidsynth before invoking play_note.

---

## Files

- [`pygame-drum.py`](pygame-drum/pygame-drum.md)

