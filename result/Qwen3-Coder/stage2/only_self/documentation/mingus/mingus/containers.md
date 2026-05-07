# `mingus.containers`

## Tree:
```
containers/
├── bar.py
├── composition.py
├── instrument.py
├── mt_exceptions.py
├── note.py
├── note_container.py
├── suite.py
└── track.py
```

## Role:
Manages musical entities and their organizational structures for music theory and composition applications.

## Description:
The containers module provides foundational classes for representing and manipulating musical elements in the mingus library. It offers abstractions for individual musical notes, collections of notes, musical bars, tracks, compositions, and suites - forming the core building blocks for musical composition and analysis. This module serves as the backbone for organizing musical data in a structured, semantically meaningful way that supports both theoretical analysis and practical music generation.

The module is used extensively throughout the mingus library for creating, manipulating, and analyzing musical content. Primary consumers include the core music theory modules, MIDI generation tools, and user-facing APIs that work with musical notation and composition.

## Components:
*Note* - Represents individual musical notes with pitch, octave, and MIDI properties
*NoteContainer* - A container for managing collections of musical notes with chord, interval, and progression-based construction
*Suite* - Organizes musical compositions into structured suites with metadata
*Track* - Manages sequences of musical bars, optionally associated with instruments and tunings

## Public API:
- **Note**: Core class for representing individual musical notes
- **NoteContainer**: Main interface for working with collections of musical notes
- **Suite**: Interface for organizing musical compositions into suites
- **Track**: Interface for managing musical sequences and bar structures

## Dependencies:
- Internal imports: 
  - mingus.containers.bar (for Bar class)
  - mingus.containers.composition (for Composition class)
  - mingus.containers.instrument (for Instrument class)
  - mingus.containers.note (for Note class)
  - mingus.containers.note_container (for NoteContainer class)
  - mingus.containers.suite (for Suite class)
  - mingus.containers.track (for Track class)
  - mingus.core.chords (for chord analysis functions)
  - mingus.core.intervals (for interval analysis functions)
  - mingus.core.progressions (for progression analysis functions)
  - mingus.core.notes (for note validation and processing functions)
  - mingus.mt_exceptions (for custom exception handling)
- External imports: 
  - None explicitly listed in the provided documentation

## Constraints:
- All musical objects must maintain valid note representations and adhere to musical theory principles
- NoteContainer operations preserve sorted order of notes
- Track operations validate note ranges against associated instruments when present
- Suite compositions must have valid "tracks" attributes
- Bar structures must maintain proper musical timing and content organization

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

