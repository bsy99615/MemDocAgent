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
Provides foundational musical theory concepts and utilities for representing and manipulating musical elements.

## Description:
The core module serves as the fundamental building block for all musical theory operations in the mingus library. It contains the essential classes and functions needed to represent musical concepts such as notes, scales, chords, intervals, and rhythmic values. This module provides the low-level abstractions that higher-level modules depend upon for music composition, analysis, and generation.

The module is organized around musical theory concepts, grouping related functionality together to maintain conceptual coherence. It provides both basic musical primitives (notes, intervals) and higher-level constructs (scales, chords, progressions) that enable complex musical operations.

## Components:
*   **chords.py**: Implements chord classes and operations for creating and analyzing musical chords
*   **intervals.py**: Provides interval definitions and operations for measuring distances between musical notes
*   **keys.py**: Contains key definitions and operations for musical keys and key signatures
*   **meter.py**: Handles meter and time signature representations for rhythmic organization
*   **mt_exceptions.py**: Defines custom exceptions used throughout the musical theory components
*   **notes.py**: Core note representations and operations for musical note handling
*   **progressions.py**: Implements chord progression analysis and generation capabilities
*   **scales.py**: Contains scale definitions and operations for various musical scale types
*   **value.py**: Provides rhythmic value calculations and timing operations

## Public API:
*   **chords.Chord**: Class for representing and manipulating musical chords
*   **intervals.Interval**: Class for representing and calculating musical intervals
*   **keys.Key**: Class for representing musical keys and key signatures
*   **meter.TimeSignature**: Class for representing time signatures and meter
*   **mt_exceptions.NoteFormatError**: Exception raised for invalid note format errors
*   **mt_exceptions.RangeError**: Exception raised for out-of-range parameter errors
*   **mt_exceptions.FormatError**: Exception raised for invalid format errors
*   **notes.Note**: Class for representing individual musical notes
*   **progressions.ChordProgression**: Class for representing and analyzing chord progressions
*   **scales.Scale**: Abstract base class for musical scales
*   **scales.Major**: Class for major scales
*   **scales.Minor**: Class for minor scales
*   **scales.HarmonicMinor**: Class for harmonic minor scales
*   **scales.MelodicMinor**: Class for melodic minor scales
*   **scales.NaturalMinor**: Class for natural minor scales
*   **scales.Diatonic**: Class for diatonic scales
*   **scales.Phrygian**: Class for Phrygian scales
*   **scales.Lydian**: Class for Lydian scales
*   **scales.Mixolydian**: Class for Mixolydian scales
*   **scales.Octatonic**: Class for octatonic scales
*   **scales.WholeTone**: Class for whole tone scales
*   **scales.MinorNeapolitan**: Class for minor Neapolitan scales
*   **scales.determine**: Function to identify possible scales for a set of notes
*   **value.add**: Computes harmonic mean for combining parallel values
*   **value.determine**: Normalizes musical values into standardized rhythmic representations
*   **value.dots**: Calculates dotted note value multipliers
*   **value.quintuplet**: Applies 5:4 rhythmic scaling for quintuplets
*   **value.septuplet**: Applies 7:4 or 7:8 rhythmic scaling for septuplets
*   **value.subtract**: Computes harmonic mean-related operation for differences
*   **value.triplet**: Applies 3:2 rhythmic scaling for triplets
*   **value.tuplet**: General-purpose tuplet scaling function

## Dependencies:
*   **Internal imports**:
    *   `mingus.core.notes`: Provides note representations and operations
    *   `mingus.core.intervals`: Provides interval definitions and operations
    *   `mingus.core.keys`: Provides key definitions and operations
    *   `mingus.core.meter`: Provides meter and time signature representations
    *   `mingus.core.chords`: Provides chord definitions and operations
    *   `mingus.core.progressions`: Provides chord progression analysis
    *   `mingus.core.scales`: Provides scale definitions and operations
    *   `mingus.core.value`: Provides rhythmic value calculations
*   **External imports**:
    *   `typing`: Used for type hints throughout the module
    *   `math`: Used for mathematical operations in value calculations

## Constraints:
*   All note representations must follow standard musical notation conventions (uppercase letters, optional accidentals)
*   Scale classes require valid note names and positive integer octave counts
*   Musical value operations assume valid numeric inputs and proper ratio parameters
*   Thread safety is not guaranteed for stateful operations that modify internal caches
*   Initialization of musical objects requires valid parameters to prevent runtime errors

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

