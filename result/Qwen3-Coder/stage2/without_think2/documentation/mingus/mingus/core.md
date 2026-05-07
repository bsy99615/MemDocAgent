# `mingus.core`

## Tree:
```
core/
├── chords.py
├── intervals.py
├── keys.py
├── meter.py
├── mt_exceptions.py
├── notes.py
├── progressions.py
├── scales.py
└── value.py
```

## Role:
Provides foundational musical theory concepts and utilities for representing and manipulating musical elements such as notes, scales, chords, intervals, and rhythmic values.

## Description:
The `mingus.core` module serves as the fundamental building block for musical theory computations within the mingus library. It encapsulates the core musical concepts and mathematical relationships that underpin higher-level musical operations. This module is responsible for defining the basic vocabulary and operations needed to represent musical elements like notes, scales, chords, and rhythmic values.

The module is organized around several key domains:
- **Notes and Intervals**: Core musical elements and their relationships
- **Scales**: Various musical scale types and their generation algorithms
- **Chords**: Harmonic structures built from notes
- **Keys**: Musical key systems and their properties
- **Value**: Rhythmic value calculations and tuplets
- **Meter**: Time signature and rhythmic grouping concepts

This module is consumed by higher-level modules such as `mingus.midi`, `mingus.containers`, and `mingus.visual` to build complete musical applications and representations.

## Components:
- **Classes**:
  - `Chord`: Represents musical chords with various inversions and extensions
  - `Interval`: Defines musical intervals and their properties
  - `Key`: Represents musical keys and their characteristics
  - `Scale`: Abstract base class for musical scales
  - `MajorScale`, `MinorScale`, `NaturalMinor`, `HarmonicMinor`, `MelodicMinor`, `Dorian`, `Phrygian`, `Lydian`, `Mixolydian`, `Locrian`, `WholeTone`, `Octatonic`, `Pentatonic`, `MinorPentatonic`, `MajorPentatonic`, `Blues`, `MinorBlues`, `MajorBlues`, `Diminished`, `Augmented`, `NeapolitanMajor`, `NeapolitanMinor`, `HungarianMinor`, `HungarianMajor`, `Oriental`, `SpanishEightTone`, `Enigmatic`, `LeadingTone`, `Altered`, `MinorNeapolitan`: Concrete scale implementations
  - `Progression`: Represents chord progressions
  - `Meter`: Represents musical meter and time signatures
  - `Note`: Represents individual musical notes
  - `NoteContainer`: Container for multiple notes
  - `Bar`: Represents a musical bar/measure
  - `Track`: Represents a musical track
  - `Song`: Represents a complete musical composition

- **Functions**:
  - `add`: Calculates harmonic mean of two values
  - `determine`: Identifies scales that could contain a set of notes
  - `dots`: Computes dotted note values
  - `quintuplet`: Calculates quintuplet rhythmic values
  - `septuplet`: Calculates septuplet rhythmic values
  - `subtract`: Computes reciprocal subtraction of two values
  - `triplet`: Calculates triplet rhythmic values
  - `tuplet`: General tuplet calculation function
  - `get_notes`: Retrieves notes for a given key
  - `get_key`: Determines the key of a set of notes
  - `get_chord`: Gets chord information for a given key and chord type
  - `get_scale`: Gets scale information for a given key and scale type
  - `get_interval`: Gets interval information for a given interval type
  - `get_progression`: Gets progression information for a given progression type
  - `get_meter`: Gets meter information for a given meter type
  - `get_note`: Gets note information for a given note name
  - `get_note_container`: Gets note container information for a given note container type
  - `get_bar`: Gets bar information for a given bar type
  - `get_track`: Gets track information for a given track type
  - `get_song`: Gets song information for a given song type

## Public API:
- `mingus.core.chords.Chord`: Musical chord representation
- `mingus.core.intervals.Interval`: Musical interval representation
- `mingus.core.keys.Key`: Musical key representation
- `mingus.core.scales.Scale`: Abstract base class for scales
- `mingus.core.scales.MajorScale`, `MinorScale`, `NaturalMinor`, `HarmonicMinor`, `MelodicMinor`, `Dorian`, `Phrygian`, `Lydian`, `Mixolydian`, `Locrian`, `WholeTone`, `Octatonic`, `Pentatonic`, `MinorPentatonic`, `MajorPentatonic`, `Blues`, `MinorBlues`, `MajorBlues`, `Diminished`, `Augmented`, `NeapolitanMajor`, `NeapolitanMinor`, `HungarianMinor`, `HungarianMajor`, `Oriental`, `SpanishEightTone`, `Enigmatic`, `LeadingTone`, `Altered`, `MinorNeapolitan`: Concrete scale implementations
- `mingus.core.progressions.Progression`: Chord progression representation
- `mingus.core.meter.Meter`: Musical meter representation
- `mingus.core.notes.Note`: Individual musical note representation
- `mingus.core.notes.NoteContainer`: Container for multiple notes
- `mingus.core.value.add`, `determine`, `dots`, `quintuplet`, `septuplet`, `subtract`, `triplet`, `tuplet`: Mathematical functions for rhythmic calculations

## Dependencies:
- Internal: `mingus.core.mt_exceptions` (for custom exception types)
- External: `mingus.utils` (for utility functions like `get_notes`, `get_key`, etc.)

## Constraints:
- All note names must be in uppercase format
- Scale classes require proper initialization with valid tonic notes and octave counts
- Rhythmic value functions assume valid numeric inputs
- Thread safety: The module is stateless and thus inherently thread-safe for concurrent access

---

## Files

- [`chords.py`](core/chords.md)
- [`intervals.py`](core/intervals.md)
- [`keys.py`](core/keys.md)
- [`meter.py`](core/meter.md)
- [`mt_exceptions.py`](core/mt_exceptions.md)
- [`notes.py`](core/notes.md)
- [`progressions.py`](core/progressions.md)
- [`scales.py`](core/scales.md)
- [`value.py`](core/value.md)

