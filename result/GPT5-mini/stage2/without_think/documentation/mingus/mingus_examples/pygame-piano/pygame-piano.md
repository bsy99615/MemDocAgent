# `pygame-piano.py`

## `mingus_examples.pygame-piano.pygame-piano.load_img` · *function*

## Summary:
Loads an image file into a pygame Surface, converts it to the appropriate blitting format (using convert() or convert_alpha()), and returns the Surface together with its Rect for immediate use in rendering.

## Description:
Known callers within this codebase:
- No direct callers are visible in the provided snippet of mingus_examples/pygame-piano/pygame-piano.py. Typical callers include:
  - Application initialization or asset-loading routines that prepare sprites, backgrounds, or UI graphics before entering the main loop.
  - Widget or UI setup code that needs an already-optimized Surface and its Rect to position elements on screen.
  - Any runtime asset-reload logic that loads an image file on demand.

Typical trigger:
- Called during startup or when dynamically loading an asset (for example, to prepare a sprite or button graphic before blitting each frame).

Why this logic is extracted:
- Centralizes the common pygame pattern of loading an image and converting it for fast blitting so callers do not duplicate error handling and convert()/convert_alpha() selection.
- Ensures a consistent return shape (Surface, Rect) which simplifies downstream code that positions and blits the image.
- Encapsulates termination behavior for unrecoverable asset-loading errors (printing a diagnostic and raising SystemExit), making the failure policy uniform across callers.

## Args:
    name (str): Filesystem path to the image file. May be absolute or relative to the current working directory. The path is passed verbatim to pygame.image.load; supported formats depend on pygame/SDL_image (commonly PNG, JPEG, BMP, etc.).

Notes:
- The function does not normalize paths, check file existence beforehand, or search multiple asset directories.
- Passing a non-string value will be forwarded to pygame.image.load and likely cause pygame.error (which is handled as described below).

## Returns:
    tuple (pygame.Surface, pygame.Rect):
        - pygame.Surface: The loaded image converted for blitting. If the loaded Surface reports per-pixel alpha (image.get_alpha() is not None), convert_alpha() is used; otherwise convert() is used to match the display format as closely as possible.
        - pygame.Rect: The rectangle returned by surface.get_rect(), representing width, height, and origin (typically at (0, 0)).

Edge cases:
- The function always returns this tuple on successful load and conversion. There are no alternate success return values.

## Raises:
    SystemExit: Raised when any pygame.error is raised during image loading or surface conversion. The original pygame.error instance is passed as the argument to SystemExit (i.e., SystemExit(message) where message is the caught pygame.error).

Behavior on error:
- Before raising SystemExit, the function prints a diagnostic line to standard output using print with the pattern:
    Error: couldn't load image:  <name>
  (Note: the print call in the source uses a comma causing a space to be inserted before the filename.)

## Constraints:
Preconditions:
- pygame must be importable and initialized (import pygame).
- The provided path must point to a readable image file supported by pygame.image.load.
- For convert()/convert_alpha() to be fully display-optimized, it is common to initialize a display mode (pygame.display.set_mode(...)) before calling this function. The function will still attempt conversion without a display mode, but the resulting Surface may not be optimized for the eventual display.

Postconditions:
- On normal return, the returned Surface has been converted (either via convert() or convert_alpha()) and the returned Rect accurately reflects the Surface's dimensions.
- On failure, the function will not return normally; it prints an error and raises SystemExit wrapping the original pygame.error.

## Side Effects:
- File I/O: Reads the image file from disk (via pygame.image.load).
- Output: Prints an error message to standard output if loading/conversion fails.
- Control flow: Raises SystemExit on error, which will terminate the process unless the caller catches SystemExit.
- No writes to global/module-level state, files, network, or databases are performed.

## Control Flow:
flowchart TD
    Start --> TryLoad[Call pygame.image.load(fullname)]
    TryLoad -->|Success| GetAlpha[Call image.get_alpha()]
    GetAlpha -->|is None| UseConvert[Call image.convert()]
    GetAlpha -->|not None| UseConvertAlpha[Call image.convert_alpha()]
    UseConvert --> Return[(return (image, image.get_rect()))]
    UseConvertAlpha --> Return
    TryLoad -->|pygame.error raised| PrintErr[print("Error: couldn't load image: ", fullname)]
    PrintErr --> RaiseExit[raise SystemExit(message)]
    RaiseExit --> End
    Return --> End

## Examples (realistic usage and error handling; described as steps):
- Typical successful usage (narrative):
    1. Ensure pygame is installed and imported; optionally initialize video with pygame.display.set_mode(...) to obtain display-optimized surfaces.
    2. Call the function with the asset path: on success you receive (surface, rect).
    3. In the main loop, blit surface onto your display surface at rect.topleft or a modified position each frame.

- Handling missing assets without terminating the program (narrative):
    1. Wrap the call in a try/except that catches SystemExit.
    2. If SystemExit is raised, inspect the exception argument to access the underlying pygame.error and perform fallback logic: load a placeholder image, mark the sprite disabled, or log/notify the user.
    3. Example flow: attempt to load "button.png"; if SystemExit occurs, attempt to load "missing.png" or set a flag to skip rendering that UI element.

- Notes on alpha handling:
    - Images with per-pixel alpha (e.g., PNG with transparency) will be converted via convert_alpha() to preserve transparency. Images without per-pixel alpha will be converted via convert() to match the display.

## `mingus_examples.pygame-piano.pygame-piano.play_note` · *function*

## Summary:
Plays a single musical note via the Fluidsynth backend, records a visual key-press for a rolling on-screen keyboard (white or black key), updates the on-screen chord name text computed from currently-playing notes, and triggers audio playback with a fixed velocity.

## Description:
This function is the smaller, focused action executed when a single Note is triggered (for example, from a key press or a MIDI note-on message). It performs three responsibilities:
1. Compute the horizontal position for the visual key corresponding to the Note, and append a timestamped visual entry to either the white-key or black-key playing list (playing_w or playing_b).
2. Compose the set of currently-playing note names (from the two lists), call chords.determine(...) to infer a chord name (if any), and render that name into the module text surface (by calling font.render, text.fill, and text.blit).
3. Request audio playback by calling fluidsynth.play_Note(note, channel, 100).

Known callers within the codebase:
- None discovered in the provided snapshot. In a typical Pygame application this function is invoked from an input handler (keyboard or MIDI event loop) when a new Note is to be played.

Why this logic is extracted into its own function:
- Separates concerns: visual bookkeeping, chord-name inference/display, and audio playback are grouped for a single note event so input handlers can remain small and simply call play_note(note).
- Keeps graphical and audio side effects colocated, simplifying synchronization between onscreen visuals and audio playback for a single note event.

## Args:
    note (object): Required.
        - Expected attributes:
            * name (str): note name identifier (e.g., 'C', 'C#', 'D', ...). Used to determine whether the note is a white or black piano key and to index into WHITE_KEYS/BLACK_KEYS.
            * octave (int): octave number used to compute an octave_offset to translate key positions across octaves.
        - Typical concrete type: mingus.containers.Note or any object with the same .name (str) and .octave (int) attributes.
        - Preconditions on values:
            * note.name must be present in either the module-level WHITE_KEYS or BLACK_KEYS sequence. If it is in neither, BLACK_KEYS.index(note.name) will raise ValueError (see Raises).
            * note.octave must be numeric (int); it is used in arithmetic to compute pixel offsets.

Notes about interdependencies:
    - The function relies heavily on module-level global variables (LOWEST, width, white_key_width, WHITE_KEYS, BLACK_KEYS, playing_w, playing_b, tick, font, text, channel). These must be defined and initialized by the module prior to calling play_note.

## Returns:
    None — the function returns no value. Its observable effects are performed via side effects (mutations and rendering/audio calls).

## Raises:
    - NameError: If any required module-level global referenced in the function is not defined (for example, LOWEST, WHITE_KEYS, BLACK_KEYS, width, white_key_width, playing_w, playing_b, tick, font, text, channel). Accessing an undefined global raises NameError at runtime.
    - ValueError: If note.name is not found in WHITE_KEYS and also not found in BLACK_KEYS, the call BLACK_KEYS.index(note.name) will raise ValueError.
    - AttributeError: If font does not provide a callable render method or text is not a surface-like object providing fill/blit, attribute errors may be raised when attempting text rendering or blitting.
    - Any exception raised by chords.determine(...) or fluidsynth.play_Note(...) will propagate to the caller (these calls are not wrapped in try/except).

## Constraints:
Preconditions:
    - Module-level globals must exist and be correctly typed/initialized:
        * LOWEST (int): reference lowest octave used when computing octave offsets.
        * width (int/float): horizontal width per octave (used to compute octave_offset = (note.octave - LOWEST) * width).
        * WHITE_KEYS (sequence[str]): ordered white-key names used to compute white-key horizontal positions; contains note.name values for white keys.
        * BLACK_KEYS (sequence[str]): ordered black-key names used to compute black-key positions; contains note.name values for black keys.
        * white_key_width (int/float): width of a single white key in pixels; used to compute white key x coordinate.
        * playing_w (list): list to which new white-key playing entries are appended. Each entry is [w, tick, note].
        * playing_b (list): list to which new black-key playing entries are appended. Each entry is [w, tick, note].
        * tick (int): current time/tick value used as the timestamp for appended playing entries.
        * font (object): surface/font-like object exposing a render(text, antialias_flag, color) method returning a surface.
        * text (surface-like): object exposing fill(color) and blit(surface, pos) methods (a Pygame Surface is expected).
        * channel (int): MIDI channel forwarded to fluidsynth.play_Note.
    - fluidsynth must be imported and its play_Note function callable (this function calls fluidsynth.play_Note(note, channel, 100)).

Postconditions:
    - One of the two lists (playing_w or playing_b) will have a new entry appended: [w, tick, note] where w is the computed x position in pixels.
    - The module text surface is updated: previous content cleared with text.fill((255,255,255)), then the determined chord-name (or empty string) is rendered via font.render(...) and blitted at (0,0).
    - fluidsynth.play_Note has been invoked with (note, channel, 100).

## Side Effects:
    - Mutates playing_w or playing_b by appending [w, tick, note].
    - Mutates the visual text surface via text.fill and text.blit (in-screen label update).
    - Calls chords.determine(notenames) to infer a chord name from currently-playing notes (pure function in the chords module; may raise exceptions if input data is malformed).
    - Calls fluidsynth.play_Note(note, channel, 100) to request audio playback (this interacts with the system audio/MIDI backend).
    - No file or network I/O is performed directly by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> ComputeOffset[Compute octave_offset = (note.octave - LOWEST) * width]
    ComputeOffset --> IsWhite{note.name in WHITE_KEYS?}
    IsWhite -- Yes --> WhiteIndex[w = WHITE_KEYS.index(note.name) * white_key_width; w += octave_offset; append to playing_w]
    IsWhite -- No --> BlackIndex[i = BLACK_KEYS.index(note.name)]
    BlackIndex --> MapI{map i to w: 0->18,1->58,2->115,3->151,else->187}
    MapI --> AddOffset[w += octave_offset; append to playing_b]
    AddOffset --> Merge[notes = playing_w + playing_b; notes.sort()]
    WhiteIndex --> Merge
    Merge --> BuildNames[notenames = [n[2].name for n in notes]]
    BuildNames --> Determine[det = chords.determine(notenames)]
    Determine --> Normalize{det != [] ?}
    Normalize -- Yes --> det0[det = det[0]]
    Normalize -- No --> detEmpty[det = ""]
    det0 --> Render[ t = font.render(det, 2, (0,0,0)); text.fill((255,255,255)); text.blit(t,(0,0)) ]
    detEmpty --> Render
    Render --> PlayCall[fluidsynth.play_Note(note, channel, 100)]
    PlayCall --> End([End])

Notes on the flow:
    - If note.name is not in WHITE_KEYS and also not in BLACK_KEYS, BLACK_KEYS.index(note.name) will raise ValueError and the function will not continue.
    - The integer mapping for black keys (i -> w) is hard-coded in the function as: 0->18, 1->58, 2->115, 3->151, else->187 (before adding the octave offset).

## Examples:
1) Minimal successful call (assumes the module has been initialized correctly):
    # Required module-level setup (examples of plausible initial values)
    LOWEST = 2
    width = 200
    WHITE_KEYS = ['C','D','E','F','G','A','B']
    BLACK_KEYS = ['C#','D#','F#','G#','A#']
    white_key_width = 40
    playing_w = []
    playing_b = []
    tick = 123
    channel = 1
    # font: any object with render(text, antialias, color) -> surface
    # text: a pygame.Surface-like object with fill and blit
    # Example Note (mingus.containers.Note or compatible)
    from mingus.containers import Note
    n = Note("C", 4)
    play_note(n)
    # Effects:
    # - an entry [computed_w, 123, n] appended to playing_w (since "C" is a white key)
    # - text surface updated with the chord name inferred from all playing notes
    # - fluidsynth.play_Note(n, channel, 100) invoked

2) Defensive call with handling of missing globals or invalid note name:
    try:
        play_note(note)
    except NameError as e:
        # A required module-level global was not initialized
        raise RuntimeError("play_note requires certain module-level globals to be defined") from e
    except ValueError as e:
        # note.name not found in WHITE_KEYS nor BLACK_KEYS
        print("Invalid note name for visual keyboard:", note.name)

Implementation notes / tips for reimplementation:
    - Ensure playing_w and playing_b store items in the form [x_position, tick, note] so the sort() call orders entries by horizontal position then tick.
    - The chord inference uses only the .name attribute of the note objects; ensure note objects expose .name as a short pitch identifier string.
    - The second argument passed to font.render is the value 2 in the source; preserve it when reimplementing to match original rendering behavior (it is forwarded as-is).
    - Keep the final audio call at velocity 100 to preserve original loudness behavior; change only if you intend to modify the sound characteristics.

