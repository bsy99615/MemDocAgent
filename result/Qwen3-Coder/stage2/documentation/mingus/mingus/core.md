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
The core module provides fundamental musical concepts and utilities for the mingus library, serving as the foundational layer for all musical operations including notes, scales, intervals, chords, and rhythmic calculations.

## Description:
The core module is the foundational component of the mingus library that implements basic musical concepts and utilities. It provides the essential building blocks for musical analysis and composition operations. This module is used throughout the library to support higher-level functionality in areas such as musical theory, composition, and analysis.

The module is organized around core musical concepts:
- Musical fundamentals (notes, intervals, keys)
- Scale systems (major, minor, modal scales)
- Harmonic structures (chords, progressions)
- Rhythmic calculations (value manipulation, tuplets)
- Musical metadata (meter, exceptions)

Primary consumers of this module include:
- The `mingus.containers` module for musical object creation
- The `mingus.midi` module for MIDI-related operations
- The `mingus.analyzers` module for musical analysis
- The `mingus.visual` module for musical visualization

## Components:
- **chords.py**: Implements chord generation and manipulation with classes like Chord and ChordProgression
- **intervals.py**: Provides interval calculations and classifications with Interval class and related functions
- **keys.py**: Defines musical keys with properties like major/minor mode, signature, and formatted names
- **meter.py**: Handles time signature and rhythmic meter calculations with Meter class
- **mt_exceptions.py**: Custom exception classes for musical operations including NoteFormatError and RangeError
- **notes.py**: Core note handling and manipulation utilities with Note class and related functions
- **progressions.py**: Chord progression generation and analysis with ChordProgression class
- **scales.py**: Scale generation and manipulation with specific scale types including Major, Minor, Diatonic, MelodicMinor, etc.
- **value.py**: Rhythmic value calculations and tuplet operations with functions like add, subtract, triplet, tuplet

## Public API:
- **chords**: `Chord`, `ChordProgression` classes for harmonic structures
- **intervals**: `Interval` class and functions for interval calculations
- **keys**: `Key` class for key analysis with properties like mode, signature, and formatted name
- **meter**: `Meter` class for time signature handling
- **mt_exceptions**: Custom exceptions like `NoteFormatError`, `RangeError`
- **notes**: `Note` class and functions for note manipulation
- **progressions**: `ChordProgression` class for harmonic progressions
- **scales**: Scale classes including `Major`, `Minor`, `Diatonic`, `MelodicMinor`, `HarmonicMinor`, `NaturalMinor`, `Phrygian`, `Lydian`, `Mixolydian`, `Locrian`, `Dorian`, `Ionian`, `Blues`, `MinorNeapolitan`, `Octatonic`, `WholeTone` and others
- **value**: Functions for rhythmic value calculations including `add`, `subtract`, `triplet`, `tuplet`, `quintuplet`, `septuplet`, `dots`, `determine`

## Dependencies:
- Internal: None (pure module dependencies)
- External: Standard Python libraries (collections, math, etc.)

## Constraints:
- All note representations must be in uppercase format
- Scale operations require valid octave ranges (positive integers)
- Interval calculations assume standard Western musical tuning
- All rhythmic value operations must use numeric inputs

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

