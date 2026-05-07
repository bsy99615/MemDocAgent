# `mingus.extra`

## Tree:
extra/
├── fft.py
├── lilypond.py
├── musicxml.py
├── tablature.py
└── tunings.py

## Role:
Provides utility functions and conversion tools for working with musical data in various external formats and representations.

## Description:
The extra module serves as a collection of utility tools that extend mingus' core functionality by providing conversions to and from various musical formats and representations. It enables users to export musical compositions to standard formats like MusicXML, LilyPond, and tablature, as well as analyze audio files to extract musical information.

This module is primarily consumed by applications that need to integrate with external music notation software, audio processing tools, or display musical information in different formats. The cohesive principle behind this module is that it provides a bridge between mingus' internal musical representation and external systems through standardized formats and tools.

## Components:
- fft.py: Audio analysis functions for frequency detection and melody extraction
- lilypond.py: Conversion utilities for LilyPond notation format
- musicxml.py: Conversion utilities for MusicXML notation format
- tablature.py: Conversion utilities for guitar/bass tablature format
- tunings.py: String instrument tuning management and fingering calculations

## Public API:
- `fft.analyze_chunks`: Analyzes audio chunks to extract musical notes
- `fft.data_from_file`: Reads audio data from WAV files
- `fft.find_Note`: Finds the dominant note in audio data
- `fft.find_frequencies`: Converts audio data to frequency spectrum
- `fft.find_melody`: Extracts melody from audio file
- `fft.find_notes`: Maps frequency data to musical notes
- `lilypond.from_Bar`: Converts Bar object to LilyPond format
- `lilypond.from_Composition`: Converts Composition object to LilyPond format
- `lilypond.from_Note`: Converts Note object to LilyPond format
- `lilypond.from_NoteContainer`: Converts NoteContainer object to LilyPond format
- `lilypond.from_Track`: Converts Track object to LilyPond format
- `lilypond.to_pdf`: Generates PDF from LilyPond string
- `lilypond.to_png`: Generates PNG from LilyPond string
- `musicxml.from_Bar`: Converts Bar object to MusicXML format
- `musicxml.from_Composition`: Converts Composition object to MusicXML format
- `musicxml.from_Note`: Converts Note object to MusicXML format
- `musicxml.from_Track`: Converts Track object to MusicXML format
- `musicxml.write_Composition`: Writes Composition to MusicXML file
- `tablature.from_Bar`: Converts Bar object to tablature format
- `tablature.from_Composition`: Converts Composition object to tablature format
- `tablature.from_Note`: Converts Note object to tablature format
- `tablature.from_NoteContainer`: Converts NoteContainer object to tablature format
- `tablature.from_Track`: Converts Track object to tablature format
- `tunings.StringTuning`: Class for managing string instrument tunings
- `tunings.add_tuning`: Adds a new tuning to the registry
- `tunings.get_instruments`: Gets list of available instruments
- `tunings.get_tuning`: Retrieves a specific tuning
- `tunings.get_tunings`: Gets list of available tunings

## Dependencies:
- Internal: mingus.core (for Note, NoteContainer, Bar, Track, Composition classes)
- External: numpy, wave, struct, subprocess, os, datetime, zipfile, xml.dom.minidom

## Constraints:
- Audio analysis functions require valid WAV files with proper audio data
- LilyPond and MusicXML export functions require proper mingus objects with valid structure
- Tablature generation requires valid instrument tunings to be defined
- All conversion functions assume proper data structures and valid musical objects
- Thread safety is not guaranteed for functions that modify global state (like FFT cache)

---

## Files

- [`fft.py`](extra/fft.md)
- [`lilypond.py`](extra/lilypond.md)
- [`musicxml.py`](extra/musicxml.md)
- [`tablature.py`](extra/tablature.md)
- [`tunings.py`](extra/tunings.md)

