# `docs`

## Tree:
```
docs/
└── conf.py
```

## Role:
Provides utility functions for documentation configuration, specifically for reading files and extracting version information relative to the documentation configuration file.

## Description:
The docs module serves as a centralized location for documentation-related utilities, particularly those needed in Sphinx configuration files. It provides helper functions that enable documentation builds to dynamically access file contents and package version information while maintaining consistent relative path resolution from the documentation configuration file's location.

This module is primarily used in Sphinx documentation builds where configuration files need to programmatically access project metadata and file contents.

## Components:
- `read(*parts)` - Reads and returns the content of a file relative to the configuration file's directory
- `find_version(*file_paths)` - Extracts version string from a Python package version file by parsing the `__version__` assignment

```mermaid
graph TD
    A[read(*parts)] --> B[find_version(*file_paths)]
```

## Public API:
- `read(*parts)` - Reads file content relative to config file directory
- `find_version(*file_paths)` - Extracts version string from version file

## Dependencies:
- Standard library modules: `os`, `re`, `pathlib`
- No external dependencies

## Constraints:
- All file operations are relative to the documentation configuration file's directory
- File paths must be valid and accessible from the configuration file's location
- Version files must contain properly formatted `__version__ = "x.y.z"` lines at the beginning

---

## Files

- [`conf.py`](docs/conf.md)

