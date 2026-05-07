# `pygame-drum.py`

## `mingus_examples.pygame-drum.pygame-drum.load_img` · *function*

## Summary:
Loads an image file from disk into a pygame Surface, converts it to an appropriate blitting format (using convert() or convert_alpha()), and returns the Surface together with its Rect.

## Description:
This small utility centralizes the common pygame pattern of loading an image asset and preparing it for fast rendering.

Known callers / usage context:
- No callers are visible in the provided file snippet. Typical callers include application initialization code, asset-loading utilities, or UI/widget setup routines that need a ready-to-blit Surface before entering the main loop.
- Typical trigger: called during startup or when dynamically loading an asset (e.g., loading a sprite, button graphic, or background) prior to performing blit operations each frame.

Why this logic is extracted:
- Encapsulates error reporting and program termination behavior for missing or invalid image assets.
- Hides the convert() vs convert_alpha() decision so callers get an already-optimized Surface and its Rect without duplicating the pattern everywhere.
- Provides a single consistent return shape (Surface, Rect) simplifying downstream code.

## Args:
    name (str): Filesystem path to the image file. Can be absolute or relative to the current working directory. Must be a path accepted by pygame.image.load (common formats: PNG, JPEG, BMP, etc., depending on SDL_image support).

Notes on parameter behavior:
- The function treats the argument as a path string; it does not normalize paths or search multiple directories.
- Passing a non-string may cause pygame.image.load to raise an error which is handled as described below.

## Returns:
    tuple (pygame.Surface, pygame.Rect):
        - pygame.Surface: The loaded image converted for blitting. If the image has per-pixel alpha, convert_alpha() is used; otherwise convert() is used to match the display format.
        - pygame.Rect: The rectangle returned by surface.get_rect(), describing the Surface bounds (width, height, and origin, typically at (0, 0)).

All normal executions return this tuple. No partial or alternate success values are returned by this function.

## Raises:
    SystemExit: Raised when any pygame.error is raised during image loading or conversion. The original pygame.error instance is passed as the argument to SystemExit (i.e., SystemExit(message) where message is the pygame.error). Before raising, the function prints an error message using print:

    Exact printed text pattern:
        Error: couldn't load image:  <name>

    (print writes to standard output by default; the comma in the code causes a space between the fixed text and the filename.)

Trigger conditions:
- Any pygame.error raised by pygame.image.load(fullname), image.get_alpha(), image.convert(), or image.convert_alpha() will be caught and re-raised as described.

## Constraints:
Preconditions:
- pygame must be importable and properly installed.
- The value of name must be a valid path to an image file readable by the process and supported by pygame.image.load.
- For convert()/convert_alpha() to produce an optimized Surface matching the display, it is common to initialize a video mode via pygame.display.set_mode(...) before calling this function. The function does not enforce that; conversion calls may still succeed without a video mode but will not be display-optimized.

Postconditions:
- On normal return, the Surface has been converted (either via convert() or convert_alpha()) and the returned Rect accurately represents the Surface dimensions.
- On failure, the function will not return normally; instead it prints an error and raises SystemExit with the underlying pygame.error.

## Side Effects:
- File I/O: Reads the image file from disk through pygame.image.load.
- Output: Prints an error message to standard output (print) if image loading/conversion fails.
- Control flow: Raises SystemExit on error, which, unless caught by the caller, will terminate the process.
- No modifications to global variables or external persistent state are performed.

## Control Flow:
flowchart TD
    Start --> TryLoad[Call pygame.image.load(fullname)]
    TryLoad -->|Success| GetAlphaCall[Call image.get_alpha()]
    GetAlphaCall -->|is None| UseConvert[Call image.convert()]
    GetAlphaCall -->|not None| UseConvertAlpha[Call image.convert_alpha()]
    UseConvert --> Return[(return (image, image.get_rect()))]
    UseConvertAlpha --> Return
    TryLoad -->|pygame.error raised| PrintErr[print("Error: couldn't load image: ", fullname)]
    PrintErr --> RaiseExit[raise SystemExit(message)]
    RaiseExit --> End
    Return --> End

## Examples (usage guidance; no embedded code block):
- Minimal successful usage (description):
    1. Ensure pygame is installed and imported; optionally initialize video with pygame.display.set_mode to get optimized conversions.
    2. Call the function with the path to your asset. On success you will receive (surface, rect).
    3. Blit surface onto your display surface each frame and use rect for positioning.

- Handling missing assets without terminating the entire program:
    1. Wrap the call in an exception handler that catches SystemExit.
    2. When SystemExit is caught, inspect the exception argument to obtain the original pygame.error and implement fallback logic (e.g., load a placeholder asset, skip the sprite, or log a detailed error).
    3. Example flow (narrative): try to load asset; if SystemExit occurs, load "missing.png" or set a flag to disable that UI element.

- Notes on alpha handling:
    - If the image file has per-pixel alpha (e.g., a PNG with transparency), the function will return a Surface converted via convert_alpha(); otherwise it will use convert() which yields a Surface optimized for blitting to the current display format.

## `mingus_examples.pygame-drum.pygame-drum.play_note` · *function*

## Summary:
Plays the provided Note through Fluidsynth (channel 9, velocity 100) and, if the Note matches a hard-coded drum-pad mapping and the module is in recording mode, appends timestamped entries to three module-level recording lists.

## Description:
This function performs two concrete actions visible in the source:
1. Maps a small, explicit set of Note(name, octave) values to integer pad indices. If a mapping is found and the module-level variable status equals the string "record", it appends timestamped entries to three module-level lists: playing, recorded, and recorded_buffer.
2. Unconditionally calls fluidsynth.play_Note(note, 9, 100) to request audio playback.

The function source contains no explicit caller definitions. In typical Pygame applications this function would be invoked from an input event handler (e.g., on key press or MIDI note-on), but that calling location is not present in this file.

## Args:
    note (mingus.containers.Note or compatible object): The musical note to play. The function compares the incoming object against explicit Note instances using equality (e.g., Note("B", 2)). The object must be comparable to mingus.containers.Note instances for equality checks to behave as intended.

Mapped Note -> index values (exact comparisons performed in source):
    Note("B", 2)   -> index 0
    Note("A", 2)   -> index 1
    Note("G", 2)   -> index 2
    Note("E", 2)   -> index 3
    Note("C", 2)   -> index 4
    Note("A", 3)   -> index 5
    Note("B", 3)   -> index 6
    Note("A#", 2)  -> index 7
    Note("G#", 2)  -> index 8

Notes not in the list do not set an index (index remains None) and therefore are not recorded, but are still played.

## Returns:
    None — the function has no return value; its observable effects are side effects (mutations and audio playback).

## Raises:
    - NameError: If any of the referenced module-level variables (status, playing, recorded, recorded_buffer, tick) are not defined, a NameError will occur when the code attempts to access them.
    - Any exception raised by fluidsynth.play_Note may propagate out of this function (the source makes a direct call to fluidsynth.play_Note without try/except).

No exceptions are explicitly raised by this function in the source.

## Constraints:
Preconditions:
    - The module must define the following globals prior to calling:
        status (str): compared for equality to the string "record".
        playing (list): expected to be a mutable list; function will append [index, tick].
        recorded (list): expected to be a mutable list; function will append [index, tick, note].
        recorded_buffer (list): expected to be a mutable list; function will append [index, tick].
        tick (int or numeric): used as the timestamp value in appended lists.
    - fluidsynth must be imported and initialized such that fluidsynth.play_Note(note, 9, 100) is callable.

Postconditions:
    - If the incoming note matches one of the mapped Note instances and status == "record":
        - playing has a new element appended: [index, tick]
        - recorded has a new element appended: [index, tick, note]
        - recorded_buffer has a new element appended: [index, tick]
    - fluidsynth.play_Note(note, 9, 100) is always invoked (regardless of mapping or status).

## Side Effects:
    - Mutates module-level lists: playing, recorded, recorded_buffer by appending elements when recording and mapping conditions are met.
    - Triggers audio playback via fluidsynth.play_Note(note, 9, 100). This interacts with the audio/MIDI subsystem (I/O) but does not write files or perform network I/O within this function.

## Control Flow:
flowchart TD
    Start([Start]) --> MapCheck{note == one of hard-coded Note(...) ?}
    MapCheck -->|Yes| SetIndex[index = mapped integer]
    MapCheck -->|No| IndexNone[index = None]
    SetIndex --> RecordCheck{status == "record"?}
    IndexNone --> SkipRecording
    RecordCheck -->|Yes| DoRecord[append [index,tick] to playing;\nappend [index,tick,note] to recorded;\nappend [index,tick] to recorded_buffer]
    RecordCheck -->|No| SkipRecording
    SkipRecording --> PlayCall[call fluidsynth.play_Note(note, 9, 100)]
    DoRecord --> PlayCall
    PlayCall --> End([End])

## Examples:
1) Minimal setup and recording example:
    # Required module-level setup (must be done by caller)
    status = "record"
    playing = []
    recorded = []
    recorded_buffer = []
    tick = 42  # current tick value
    # Now call
    play_note(Note("B", 2))
    # After call:
    # playing == [[0, 42]]
    # recorded == [[0, 42, Note("B",2)]]
    # recorded_buffer == [[0, 42]]
    # fluidsynth.play_Note was invoked with (Note("B",2), 9, 100)

2) Play-only (no recording):
    status = "idle"
    play_note(Note("C", 4))  # C4 is not in the mapping
    # No lists are modified; fluidsynth.play_Note is still invoked with (Note("C",4), 9, 100)

Implementation notes:
    - The function uses equality against freshly constructed Note(...) instances; to ensure mapping works, pass Note instances from mingus.containers or compatible objects whose equality behaves like mingus Note equality.
    - Channel and velocity are fixed in the source: channel = 9, velocity = 100. Change these only by editing the source call to fluidsynth.play_Note.

