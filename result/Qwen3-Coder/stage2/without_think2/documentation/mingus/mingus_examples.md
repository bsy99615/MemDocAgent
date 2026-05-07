# `mingus_examples`

## Tree:
mingus_examples/
├── pygame-drum/
│   └── pygame-drum.py
└── pygame-piano/
    └── pygame-piano.py

## Role:
Provides example implementations of interactive musical applications using Pygame and FluidSynth for audio synthesis.

## Description:
This module contains two distinct example applications that demonstrate the integration of musical theory concepts with interactive visual interfaces. Both applications leverage the mingus music theory library for note handling and Pygame for graphical rendering, while utilizing FluidSynth for MIDI audio synthesis.

The pygame-drum example implements a visual drum sequencer with audio playback capabilities, managing both the graphical interface elements and audio synthesis for drum patterns. The pygame-piano example provides core functionality for playing musical notes through MIDI synthesis and displaying chord information on a virtual piano keyboard, combining musical data with visual feedback in a Pygame environment.

## Components:
- **pygame-drum/pygame-drum.py**:
  - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]: Loads and processes images for drum sequencer UI elements
  - play_note(note: Note) -> None: Handles audio playback of drum notes and optional recording functionality

- **pygame-piano/pygame-piano.py**:
  - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]: Centralized image loading utility for piano interface
  - play_note(note: mingus.containers.Note) -> None: Plays musical notes and performs real-time chord detection

## Public API:
- **pygame-drum/pygame-drum.py**:
  - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]: Loads an image file and returns a Pygame surface with proper format conversion for display compatibility. Requires valid file paths.
  - play_note(note: Note) -> None: Plays a musical note using FluidSynth and optionally records it for playback. Depends on global recording state variables.

- **pygame-piano/pygame-piano.py**:
  - load_img(name: str) -> tuple[pygame.Surface, pygame.Rect]: Loads and processes a Pygame image surface with appropriate color conversion. Requires valid file paths.
  - play_note(note: mingus.containers.Note) -> None: Plays a musical note using MIDI synthesis and updates the display with chord information. Requires extensive global state initialization.

## Dependencies:
- **Internal**: None
- **External**: 
  - pygame: Used for image loading, surface management, display operations, and rendering
  - fluidsynth: Provides MIDI synthesis capabilities for audio playback
  - mingus.containers.Note: For musical note representation and handling
  - sys: For system-level operations like exiting on errors

## Constraints:
- Both modules require proper initialization of Pygame display and FluidSynth environment
- Functions in both modules depend on global variable states being properly configured
- Thread safety is not guaranteed; functions should be called from the main thread
- File paths for image loading must be valid and accessible
- Note objects must conform to the mingus Note interface specifications
- The pygame-drum play_note function requires specific global recording variables
- The pygame-piano play_note function requires extensive global state variables for display and chord detection

