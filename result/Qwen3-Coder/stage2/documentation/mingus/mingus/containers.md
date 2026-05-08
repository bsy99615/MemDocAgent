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
Provides foundational data structures for representing and organizing musical content in the mingus library.

## Description:
The containers module offers a comprehensive set of classes for modeling musical content at various levels of granularity. It provides the core data structures that enable composition, manipulation, and analysis of musical works. The module includes containers for individual notes, collections of notes, musical measures (bars), musical tracks, complete compositions, and groups of compositions (suites).

These containers work together to form a complete musical data model that supports the creation and processing of musical compositions. The module is designed to be used throughout the mingus library for building, modifying, and analyzing musical content.

## Components:
- **Bar**: Represents a musical measure containing note entries with timing and placement information
- **Composition**: A complete musical work consisting of multiple tracks with metadata
- **Instrument**: Base class representing musical instruments with playable ranges and properties
- **Note**: Represents individual musical notes with pitch, octave, and MIDI properties
- **NoteContainer**: Manages collections of musical notes for chord and interval operations
- **Suite**: Groups multiple compositions together with shared metadata
- **Track**: A sequence of musical bars, optionally associated with an instrument for validation

## Public API:
- **Bar**: Core musical measure container with note placement and timing capabilities
- **Composition**: Complete musical work with metadata and track management
- **Instrument**: Abstract base class for musical instrument definitions with range validation
- **Note**: Individual musical note with pitch, octave, and MIDI properties
- **NoteContainer**: Collection of notes for chord and interval operations
- **Suite**: Grouping of compositions with metadata
- **Track**: Sequential musical content organized in bars with optional instrument validation

## Dependencies:
- Internal: `mingus.core.keys`, `mingus.core.meter`, `mingus.core.chords`, `mingus.core.progressions`
- External: `six` (Python 2/3 compatibility), `numpy` (for some mathematical operations)

## Constraints:
- All containers must be properly initialized before use
- NoteContainer maintains sorted order of notes internally
- Bar containers must be validated for proper meter and note placement
- Instrument validation is enforced when adding notes to tracks with assigned instruments
- Track integrity is maintained through bar management and full bar validation

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

