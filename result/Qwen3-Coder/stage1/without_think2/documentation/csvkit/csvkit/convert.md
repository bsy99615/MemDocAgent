# `csvkit.convert`

## Tree:
```
convert/
├── __init__.py
├── fixed.py
└── geojs.py
```

## Role:
Provides utilities for converting various non-CSV data formats into CSV format, specifically supporting fixed-width and GeoJSON data sources.

## Description:
The convert module serves as a data format conversion layer within csvkit, enabling seamless transformation of diverse data formats into the standardized CSV format. It offers specialized converters for fixed-width formatted data and GeoJSON FeatureCollections, facilitating integration with CSV-based data processing workflows. This module encapsulates the complexity of format-specific parsing and provides unified interfaces for common conversion tasks.

## Components:
- `guess_format(filename)` - Determines data format from filename extension
- `FixedWidthReader` - Iterator for fixed-width formatted files with schema support
- `FixedWidthRowParser` - Parses fixed-width lines according to schema definitions
- `SchemaDecoder` - Converts schema rows into structured field definitions
- `fixed2csv(f, schema, output=None, skip_lines=0, **kwargs)` - Main interface for fixed-width to CSV conversion
- `geojson2csv(f, key=None, **kwargs)` - Converts GeoJSON FeatureCollection to CSV format

## Public API:
- `guess_format(filename: str) -> str | None`: Infers data format from filename extension
- `fixed2csv(f, schema, output=None, skip_lines=0, **kwargs) -> str | None`: Converts fixed-width data to CSV format
- `geojson2csv(f, key=None, **kwargs) -> str`: Converts GeoJSON FeatureCollection to CSV format

## Dependencies:
- Internal: `agate.csv` for CSV writing operations
- External: `csv` module for CSV parsing, `json` for JSON parsing, `io.StringIO` for in-memory buffers

## Constraints:
- All converters require properly formatted input data
- Fixed-width converters need valid schema definitions
- GeoJSON converters expect valid FeatureCollection format
- Thread safety: Not guaranteed for stateful readers

---

## Files

- [`__init__.py`](convert/__init__.md)
- [`fixed.py`](convert/fixed.md)
- [`geojs.py`](convert/geojs.md)

