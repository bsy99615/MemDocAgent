# `mingus.containers`

## Tree:
    containers/
    ├── bar.py
    ├── composition.py
    ├── instrument.py
    ├── mt_exceptions.py
    ├── note.py
    ├── note_container.py
    └── suite.py
    └── track.py

## Role:
    Provides container classes for musical elements and structural components

## Description:
    The containers module provides container classes that represent musical elements and structural components for building musical compositions in the mingus library. These containers form a hierarchy from individual notes up to complete musical suites.

    This module is primarily consumed by other modules in the mingus library such as the core musical theory components, MIDI handling modules, and user-facing APIs for creating and manipulating musical content. The containers are designed to be used in a hierarchical fashion: Notes form NoteContainers, which are placed in Bars, which compose Tracks, which make up Compositions, which can be grouped into Suites.

    The cohesion of this module stems from the shared concept of musical containers - all components represent different levels of musical organization and provide methods for musical manipulation like transposition, augmentation, and determining musical properties.

## Components:
    * Bar - Musical container for organizing notes within a time signature
    * Composition - Container for multiple musical tracks
    * Guitar - Specific guitar instrument with defined range
    * Instrument - Base class defining musical instrument properties
    * MidiInstrument - MIDI-compatible instrument with predefined instrument names
    * MidiPercussionInstrument - MIDI percussion instrument with drum mappings
    * Piano - Specific piano instrument with defined range
    * InstrumentRangeError - Exception for notes outside instrument range
    * MeterFormatError - Exception for invalid meter specifications
    * NoteFormatError - Exception for invalid note representations
    * UnexpectedObjectError - Exception for unexpected object types
    * Note - Musical note with pitch, octave, and dynamics
    * NoteContainer - Collection of notes with musical analysis capabilities
    * Suite - Container for multiple musical compositions
    * Track - Sequence of musical bars associated with an instrument

## Public API:
    * Bar(key="C", meter=(4, 4)) - Creates a musical bar with key and meter
    * Composition() - Creates a musical composition with tracks
    * Guitar() - Creates a guitar instrument instance
    * Instrument() - Base class for musical instruments
    * MidiInstrument(name="") - Creates a MIDI instrument with specified name
    * MidiPercussionInstrument() - Creates a MIDI percussion instrument
    * Piano() - Creates a piano instrument instance
    * InstrumentRangeError - Exception raised when notes are out of instrument range
    * MeterFormatError - Exception raised for invalid meter formats
    * NoteFormatError - Exception raised for invalid note formats
    * UnexpectedObjectError - Exception raised for unexpected object types
    * Note(name="C", octave=4, dynamics=None, velocity=None, channel=None) - Creates a musical note
    * NoteContainer(notes=None) - Creates a container for musical notes
    * Suite() - Creates a musical suite containing compositions
    * Track(instrument=None) - Creates a musical track with optional instrument

## Dependencies:
    * Internal: mingus.core (for intervals, progressions, chords, notes)
    * External: six (Python 2/3 compatibility)

## Constraints:
    * All musical objects must be properly initialized before use
    * Bars must be filled according to their meter specification
    * Instruments must be assigned to tracks before adding notes that might exceed their range
    * Thread safety is not guaranteed for container modifications

---

## Files

- [`bar.py`](containers/bar.md)
- [`composition.py`](containers/composition.md)
- [`instrument.py`](containers/instrument.md)
- [`mt_exceptions.py`](containers/mt_exceptions.md)
- [`note.py`](containers/note.md)
- [`note_container.py`](containers/note_container.md)
- [`suite.py`](containers/suite.md)
- [`track.py`](containers/track.md)

