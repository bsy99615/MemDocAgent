# `mingus_examples.pygame-piano`

## Tree:
pygame-piano/
└── pygame-piano.py

## Role:
Provide a compact, runnable Pygame-based piano demonstration that ties input (keyboard/MIDI) to Fluidsynth audio playback and an on-screen rolling keyboard visualization.

## Description:
- Where and when this module is used:
  - This file is an example/demo entry point intended to be executed as a script or imported by an examples runner. It is consumed directly by a human-run example launcher or by developers exploring how to integrate Pygame visuals with Fluidsynth audio in the mingus examples collection.
  - Typical consumers:
    - A developer running the examples directory (e.g., python pygame-piano.py).
    - Any small demo runner that enumerates and runs example scripts in the repository.
- Why these components are grouped:
  - Cohesion principle: this module groups the minimal set of functions, globals, and visual/audio glue required to demonstrate a playable piano — image loading and conversion for fast rendering, visual bookkeeping for pressed keys, chord name inference and display, and live audio playback via Fluidsynth.
  - Boundary: it is a self-contained demo layer (presentation + sound) that depends on lower-level components (pygame for rendering, fluidsynth for audio, chords for chord inference) but keeps example-specific logic in one place.

## Components:
- Functions
  - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]
    - Loads an image from disk, converts it for fast blitting (convert() or convert_alpha()), and returns (surface, surface.get_rect()).
    - See component docs: mingus_examples.pygame-piano.pygame-piano.load_img
  - play_note(note) -> None
    - Handle a single note event: append a timestamped visual key entry (white or black), update the on-screen chord-name text, and request audio playback via Fluidsynth at fixed velocity.
    - See component docs: mingus_examples.pygame-piano.pygame-piano.play_note
- Key module-level globals / configuration (public, must be initialized by host or the module's init code)
  - LOWEST: int — reference lowest octave used when computing visual offsets
  - width: int/float — horizontal width per octave (pixel scale)
  - white_key_width: int/float — pixel width of one white key
  - WHITE_KEYS: sequence[str] — ordered white-key names for position indexing (e.g., ['C','D','E','F','G','A','B'])
  - BLACK_KEYS: sequence[str] — ordered black-key names for position indexing (e.g., ['C#','D#','F#','G#','A#'])
  - playing_w: list — list of active white-key visual entries in the form [x_position, tick, note]
  - playing_b: list — list of active black-key visual entries in the form [x_position, tick, note]
  - tick: int — current time/tick used as a timestamp for visual entries
  - font: object — font-like object exposing render(text, antialias, color) -> Surface
  - text: surface-like — Surface used to draw the current chord name (supports fill and blit)
  - channel: int — MIDI channel forwarded to fluidsynth.play_Note
- One-line role for each listed symbol provided above.

Mermaid dependency graph (internal relationships)
graph LR
    load_img -->|uses| pygame
    play_note -->|uses| fluidsynth
    play_note -->|uses| chords
    play_note -->|reads/writes| playing_w
    play_note -->|reads/writes| playing_b
    play_note -->|updates| text
    play_note -->|renders via| font
    pygame -->|provides| Surface
    chords -->|provides| determine
    fluidsynth -->|provides| play_Note

## Public API:
- load_img(name: str) -> (pygame.Surface, pygame.Rect)
  - Description: Load an image file and return a display-converted Surface and its Rect for immediate blitting/positioning.
  - Usage notes:
    - Best used after initializing pygame and (ideally) after calling pygame.display.set_mode(...) so convert()/convert_alpha() produces display-optimized Surfaces.
    - Raises SystemExit wrapping pygame.error on failure (prints an error line before exiting).
    - See: mingus_examples.pygame-piano.pygame-piano.load_img
- play_note(note) -> None
  - Description: Trigger the visual and audio actions for a single note: append visual key entry (playing_w or playing_b), update the chord-name text surface, and call fluidsynth.play_Note(note, channel, 100).
  - Usage notes:
    - Expects several module-level globals to be defined and correctly typed (LOWEST, width, white_key_width, WHITE_KEYS, BLACK_KEYS, playing_w, playing_b, tick, font, text, channel). If those are not initialized, NameError or other runtime errors will occur.
    - Does not return a value; it performs side effects (mutates playing lists, updates text Surface, calls Fluidsynth).
    - See: mingus_examples.pygame-piano.pygame-piano.play_note
- Module-level globals (LOWEST, width, white_key_width, WHITE_KEYS, BLACK_KEYS, playing_w, playing_b, tick, font, text, channel)
  - Description: Configuration/state used by play_note (positions, rendering, audio channel). Callers should treat these as part of the module's configuration contract: set them before invoking play_note.

## Component interaction / call flow (textual)
1. Initialization (module or script-level):
   - Set up pygame, optionally call pygame.display.set_mode(...)
   - Initialize Fluidsynth (backend) and set module-level channel
   - Initialize visual globals (WHITE_KEYS, BLACK_KEYS, LOWEST, width, white_key_width)
   - Initialize playing_w, playing_b, tick, font, text surfaces
2. Asset loading:
   - Use load_img(...) to load sprites or background images for the keyboard UI
3. Event handling:
   - On key press / MIDI note-on: call play_note(note)
     - play_note computes x position, appends to playing_w/playing_b, infers chord via chords.determine(...), updates text surface with font.render(...), and calls fluidsynth.play_Note(...)
4. Rendering loop:
   - Main loop blits key images, iterates playing_w/playing_b to draw pressed key effects, blits the chord text surface, and updates display.

## Dependencies:
- Internal / repository dependencies
  - chords (module providing determine(notenames) -> chord list/label)
    - Purpose: chord-name inference from a list of currently playing note names; used by play_note to display the inferred chord.
  - (Examples-level) other mingus helper modules may be referenced by the script depending on how the example is wired; consult the top-level example runner if used.
- External libraries
  - pygame
    - Purpose: windowing, rendering, image loading (pygame.image.load), Surface conversion (convert/convert_alpha), fonts (font.render), Rects, event loop.
    - Note: Surface conversions are most effective after creating a display surface with pygame.display.set_mode(...).
  - fluidsynth (Python binding)
    - Purpose: audio backend; play_Note(note, channel, velocity) is called by play_note to produce sound.
  - mingus containers / types (Note)
    - Purpose: example code expects Note-like objects with .name and .octave attributes (e.g., mingus.containers.Note) to be passed to play_note.

## Constraints:
- Initialization ordering:
  - pygame must be importable and initialized before calling load_img and before doing render operations. For best performance, call pygame.display.set_mode(...) prior to load_img so returned Surfaces are converted to the display format.
  - Fluidsynth must be initialized (and a valid channel assigned) before calling play_note to produce sound.
  - Module-level globals referenced by play_note must be set prior to its invocation (LOWEST, width, white_key_width, WHITE_KEYS, BLACK_KEYS, playing_w, playing_b, tick, font, text, channel).
- Thread-safety:
  - This module is not thread-safe. All calls to play_note, rendering, and pygame interactions are expected to run on the main thread where the Pygame event loop executes.
- Error handling policy:
  - load_img prints an error and raises SystemExit (wrapping pygame.error) on image-load/conversion failure; callers that want to continue must catch SystemExit and implement fallback logic.
  - play_note does not internally catch exceptions from chords.determine or fluidsynth.play_Note; callers should guard higher-level event handling if robust error recovery is required.
- Input constraints:
  - play_note expects note objects exposing .name (string found in WHITE_KEYS or BLACK_KEYS) and .octave (int). If note.name is absent from both key lists, ValueError will be raised by list.index usage.
- Resource assumptions:
  - Image formats supported depend on pygame/SDL_image build (typically PNG/JPEG/BMP). load_img does not search asset paths or normalize names — provide correct file paths.

## Links to component-level documentation:
- load_img: mingus_examples.pygame-piano.pygame-piano.load_img
- play_note: mingus_examples.pygame-piano.pygame-piano.play_note

---

## Files

- [`pygame-piano.py`](pygame-piano/pygame-piano.md)

