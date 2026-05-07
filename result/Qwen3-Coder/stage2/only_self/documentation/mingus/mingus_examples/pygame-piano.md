# `mingus_examples.pygame-piano`

## Tree:
pygame-piano/
└── pygame-piano.py

## Role:
Provides image loading utilities and musical note playback functionality for a pygame-based piano application.

## Description:
This module implements core functionality for a pygame-based piano interface application. It offers utilities for loading and preparing images for pygame display, along with the fundamental note-playing capabilities that drive the piano simulation. The module integrates with MIDI synthesis to produce audible musical notes while providing visual feedback through chord detection and display.

The module is part of the mingus_examples package and serves as a foundational component for interactive piano applications that combine graphical user interface elements with musical note playback and chord recognition.

## Components:
- load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]: Loads and prepares an image surface for pygame applications with appropriate color conversion
- play_note(note: mingus.containers.Note) -> None: Plays a musical note on virtual piano interface and displays detected chord information

## Public API:
- load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]: Loads an image file and returns the surface with its rectangle bounds. Handles both transparent and opaque images with proper pygame surface conversion.
- play_note(note: mingus.containers.Note) -> None: Plays a musical note through MIDI synthesis while managing visual representation on a virtual piano keyboard and detecting/displaying chords formed by simultaneous notes.

## Dependencies:
- Internal: mingus.containers.Note (for musical note objects)
- External: pygame (for graphics rendering and surface management)
- External: fluidsynth (for MIDI audio synthesis)

## Constraints:
- Global variables must be initialized before calling play_note: text, playing_w, playing_b, width, LOWEST, WHITE_KEYS, BLACK_KEYS, white_key_width, tick, font, channel
- The note parameter must be a valid mingus Note object with proper name and octave attributes
- Note name must be either in WHITE_KEYS or BLACK_KEYS constants
- The LOWEST constant defines the lowest playable octave
- WHITE_KEYS and BLACK_KEYS are lists defining valid note names for each key type

---

## Files

- [`pygame-piano.py`](pygame-piano/pygame-piano.md)

