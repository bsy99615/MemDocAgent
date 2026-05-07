# `mingus.extra`

## Tree:
extra/
├── fft.py
├── lilypond.py
├── musicxml.py
├── tablature.py
└── tunings.py

## Role:
Provides utilities for exporting and converting musical data to external notation formats and tuning configurations.

## Description:
The mingus.extra module serves as a collection of utility functions and classes that enable the conversion of internal musical representations to external notation formats and tuning configurations. This module bridges the gap between mingus' internal musical data structures and external systems by providing exporters for popular music notation formats (MusicXML, LilyPond) and tablature representations, along with comprehensive tuning management capabilities.

The module is organized around three primary domains:
1. **Export Formats**: Converting musical compositions to standardized notation formats (MusicXML, LilyPond)
2. **Tablature Generation**: Creating guitar-style tablature representations from musical data
3. **Tuning Management**: Handling instrument tunings and fingering calculations

This separation allows developers to work with musical data in mingus' native format while easily exporting to various external systems or generating visual representations like tablature.

## Components:
- **fft.py**: Fast Fourier Transform utilities for audio signal processing
- **lilypond.py**: Conversion functions for LilyPond music notation format
- **musicxml.py**: Conversion functions for MusicXML music notation format  
- **tablature.py**: Tablature generation utilities for guitar-style notation
- **tunings.py**: Tuning configuration management and fingering calculations

## Public API:
- **from_Bar**: Converts a single musical bar to MusicXML format
- **from_Composition**: Converts a musical composition to MusicXML format
- **from_Note**: Converts a single musical note to MusicXML format
- **from_Track**: Converts a musical track to MusicXML format
- **write_Composition**: Writes a musical composition to a MusicXML file
- **to_pdf**: Generates a PDF from LilyPond notation
- **to_png**: Generates a PNG image from LilyPond notation
- **from_Bar**: Converts a musical bar to LilyPond format
- **from_Composition**: Converts a musical composition to LilyPond format
- **from_Note**: Converts a single musical note to LilyPond format
- **from_Suite**: Converts a musical suite to LilyPond format
- **from_Track**: Converts a musical track to LilyPond format
- **from_Bar**: Converts a musical bar to tablature format
- **from_Composition**: Converts a musical composition to tablature format
- **from_Note**: Converts a single musical note to tablature format
- **from_NoteContainer**: Converts a note container to tablature format
- **from_Suite**: Converts a musical suite to tablature format
- **from_Track**: Converts a musical track to tablature format
- **StringTuning**: Class for representing and manipulating musical instrument tunings
- **add_tuning**: Adds a new tuning configuration to the registry
- **get_instruments**: Retrieves all known instrument names
- **get_tuning**: Retrieves a specific tuning configuration
- **get_tunings**: Retrieves multiple tuning configurations based on criteria

## Dependencies:
- Internal: mingus.containers (for Composition, Track, Bar, Note, NoteContainer classes)
- Internal: mingus.core (for keys, values, and other core musical concepts)
- External: xml.dom.minidom (for MusicXML generation)
- External: os (for file operations and line separator handling)
- External: zipfile (for MXL file generation)
- External: subprocess (for LilyPond command execution)

## Constraints:
- All conversion functions require valid mingus musical objects as input
- LilyPond export requires LilyPond software to be installed and available in PATH
- MusicXML export requires valid DOM processing capabilities
- Tablature generation requires proper tuning configurations
- Tuning management functions assume valid note representations and string indices

---

## Files

- [`fft.py`](extra/fft.md)
- [`lilypond.py`](extra/lilypond.md)
- [`musicxml.py`](extra/musicxml.md)
- [`tablature.py`](extra/tablature.md)
- [`tunings.py`](extra/tunings.md)

