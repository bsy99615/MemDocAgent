# `mingus.midi`

## Tree:
    - midi/
      - fluidsynth.py
      - midi_file_in.py
      - midi_file_out.py
      - midi_track.py
      - pyfluidsynth.py
      - sequencer.py
      - sequencer_observer.py
      - win32midi.py
      - win32midisequencer.py

## Role:
    - Provides cross-platform MIDI sequencing and playback capabilities for musical applications

## Description:
    - This module offers a complete MIDI infrastructure for creating, manipulating, and playing musical sequences across different platforms. It provides both high-level interfaces for musical constructs (compositions, tracks, bars) and low-level MIDI event handling for precise control over playback.
    - Primary consumers include the mingus.core modules for musical composition and playback, as well as any application requiring MIDI sequencing capabilities.
    - The module is organized around the principle of platform independence, with specific implementations for different operating systems (Windows, Linux, macOS) while maintaining a consistent API.

## Components:
    - **Sequencer**: Abstract base class defining the interface for MIDI sequencing operations
    - **SequencerObserver**: Abstract base class for observing MIDI sequencing events
    - **Win32MidiSequencer**: Windows-specific implementation of the MIDI sequencer
    - **Win32MidiPlayer**: Windows-specific MIDI player using the Windows Multimedia API
    - **Win32MidiException**: Custom exception class for Windows MIDI errors
    - **PyFluidSynth**: Cross-platform FluidSynth integration for software MIDI synthesis
    - **FluidSynth**: Alternative FluidSynth implementation for software MIDI synthesis
    - **MidiFileIn**: Reader for MIDI files
    - **MidiFileOut**: Writer for MIDI files
    - **MidiTrack**: Representation of a MIDI track

## Public API:
    - **Sequencer** (abstract base class): Defines interfaces for MIDI playback, control changes, instrument changes, and event notification
    - **SequencerObserver** (abstract base class): Defines interfaces for observing MIDI sequencing events
    - **Win32MidiSequencer**: Concrete Windows MIDI sequencer implementation
    - **Win32MidiPlayer**: Windows MIDI player using winmm.dll
    - **Win32MidiException**: Exception type for Windows MIDI errors
    - **PyFluidSynth**: FluidSynth integration for software MIDI synthesis
    - **FluidSynth**: Alternative FluidSynth implementation
    - **MidiFileIn**: MIDI file reader
    - **MidiFileOut**: MIDI file writer
    - **MidiTrack**: MIDI track representation

## Dependencies:
    - Internal: None
    - External: 
        - ctypes (for Windows API access)
        - fluidsynth (for FluidSynth support)
        - os, sys (for platform detection)
        - time (for timing operations)

## Constraints:
    - Platform-specific implementations must be used on their respective platforms
    - Sequencer instances must be properly initialized before use
    - MIDI devices must be opened before attempting MIDI operations
    - All MIDI event parameters must be within valid ranges (0-127 for note/control numbers, 0-15 for channels)

---

## Files

- [`fluidsynth.py`](midi/fluidsynth.md)
- [`midi_file_in.py`](midi/midi_file_in.md)
- [`midi_file_out.py`](midi/midi_file_out.md)
- [`midi_track.py`](midi/midi_track.md)
- [`pyfluidsynth.py`](midi/pyfluidsynth.md)
- [`sequencer.py`](midi/sequencer.md)
- [`sequencer_observer.py`](midi/sequencer_observer.md)
- [`win32midi.py`](midi/win32midi.md)
- [`win32midisequencer.py`](midi/win32midisequencer.md)

