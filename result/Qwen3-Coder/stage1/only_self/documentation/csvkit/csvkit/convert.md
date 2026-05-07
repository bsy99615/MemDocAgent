# `csvkit.convert`

## Tree:
convert/
├── __init__.py
├── fixed.py
└── geojs.py

## Role:
Provides utilities for converting between different structured data formats, particularly fixed-width text files and GeoJSON spatial data.

## Description:
The convert module offers functionality for transforming data between various structured formats. It specializes in handling fixed-width formatted text files and GeoJSON spatial data, making it easier to work with legacy data formats and geospatial information in tabular form.

This module is used internally by csvkit tools when format conversion is needed, particularly when users want to transform fixed-width data into more commonly used formats like CSV, or when working with GeoJSON spatial data.

## Components:
*   `guess_format(filename)` - Determines the appropriate data format based on file extension
*   `fixed2csv(f, schema, output, skip_lines, **kwargs)` - Converts fixed-width formatted text data into CSV format using a schema definition
*   `geojson2csv(f, key, **kwargs)` - Converts GeoJSON FeatureCollection data into CSV format with support for geometric coordinates

## Public API:
*   `guess_format(filename)` - Guesses the file format based on the file extension, returning a standardized format identifier
*   `fixed2csv(f, schema, output, skip_lines, **kwargs)` - Converts fixed-width formatted text data into CSV format using a schema definition
*   `geojson2csv(f, key, **kwargs)` - Converts GeoJSON FeatureCollection data into CSV format with support for geometric coordinates

## Dependencies:
*   Internal: csvkit.convert.fixed (provides fixed-width parsing infrastructure)
*   Internal: csvkit.convert.geojs (provides GeoJSON conversion functionality)
*   External: Standard library modules (io, json, csv, codecs) for file handling and data processing

## Constraints:
*   Callers must ensure input files are properly formatted for their intended conversion operations
*   Fixed-width conversions require valid schema definitions with proper field specifications
*   GeoJSON conversions require valid GeoJSON FeatureCollection structures
*   The module assumes standard Python encoding practices and file handling conventions

---

## Files

- [`__init__.py`](convert/__init__.md)
- [`fixed.py`](convert/fixed.md)
- [`geojs.py`](convert/geojs.md)

