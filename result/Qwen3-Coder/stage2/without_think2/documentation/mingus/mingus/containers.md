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
Manages musical data structures and their relationships for composition and performance

## Description:
The containers module provides foundational musical data structures that form the backbone of the mingus music processing system. It encapsulates core musical concepts like notes, chords, bars, tracks, and compositions, enabling structured musical representation and manipulation. This module serves as the primary interface for creating, organizing, and transforming musical content within the system.

The module is organized around the principle of musical hierarchy: individual notes form containers, containers compose bars, bars form tracks, tracks compose compositions, and compositions can be grouped into suites. This layered approach allows for granular control over musical elements while maintaining semantic relationships between different levels of musical organization.

Primary consumers include:
- Core music processing modules that require structured musical data
- MIDI file generation and playback systems
- Music theory analysis tools
- Composition and arrangement interfaces

## Components:
- **Bar**: Represents a musical measure with time signature and note placement
- **Composition**: Top-level musical structure containing multiple tracks
- **Instrument**: Defines playable ranges and characteristics for musical elements
- **Note**: Fundamental musical pitch unit with pitch, octave, and dynamics
- **NoteContainer**: Collection of notes with chord and interval analysis capabilities
- **Suite**: Logical grouping of compositions with metadata
- **Track**: Sequential musical content organized into bars

## Public API:
- `Bar`: Musical measure container with time signature and note placement
- `Composition`: Multi-track musical structure with metadata
- `Instrument`: Musical instrument with playable range and tuning
- `Note`: Individual musical note with pitch, octave, and dynamics
- `NoteContainer`: Collection of notes with chord analysis and manipulation
- `Suite`: Grouping of compositions with metadata
- `Track`: Sequential musical content organized into bars
- `InstrumentRangeError`: Exception for notes outside instrument playable range
- `MeterFormatError`: Exception for invalid meter specifications
- `NoteFormatError`: Exception for invalid note formatting
- `UnexpectedObjectError`: Exception for unexpected object types

## Dependencies:
- Internal: `mingus.core` modules for note validation, chord determination, and interval analysis
- External: Standard Python libraries for basic data structures and mathematical operations

## Constraints:
- All musical objects must maintain valid pitch ranges and note formats
- Note containers must preserve sorted order of notes
- Tracks require proper bar structure with complete fills (except last bar)
- Instrument validation enforces playable range constraints
- Thread-safety: Objects are not thread-safe; concurrent access requires external synchronization

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

