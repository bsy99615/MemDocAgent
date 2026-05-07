# `datasette.utils`

## Tree:
```
utils/
├── __init__.py
├── asgi.py
├── baseconv.py
├── shutil_backport.py
├── sqlite.py
└── testing.py
```

## Role:
Provides foundational utilities and helper functions for Datasette's core functionality, including ASGI web handling, base conversions, file operations, SQLite version checking, and testing infrastructure.

## Description:
The utils module serves as a collection of low-level utility functions and classes that support Datasette's core operations. It provides essential building blocks for web request/response handling, data conversion, file system operations, database compatibility checking, and testing infrastructure. These utilities are designed to be reused across different parts of the Datasette codebase and help maintain consistency in how common operations are implemented.

This module groups together disparate utility functions that don't belong in any specific domain module but are fundamental to Datasette's operation. The cohesion is based on shared utility nature rather than domain-specific functionality.

## Components:
- **asgi.py**: ASGI request/response handling utilities for HTTP operations
- **baseconv.py**: Base conversion utilities for encoding/decoding numbers in custom numeral systems
- **shutil_backport.py**: Backported shutil functions for directory copying operations
- **sqlite.py**: SQLite version checking utilities for feature compatibility
- **testing.py**: Testing utilities for simulating HTTP requests and inspecting responses

## Public API:
The module exposes the following public interfaces:
- `asgi.Request`: ASGI request wrapper class for HTTP request handling
- `asgi.Response`: ASGI response wrapper class for HTTP response handling
- `asgi.asgi_send`: Utility function for sending ASGI HTTP responses
- `asgi.asgi_send_file`: Utility function for sending files via ASGI
- `asgi.asgi_static`: ASGI middleware for serving static files
- `baseconv.BaseConverter`: Class for converting numbers between different numeral systems
- `shutil_backport.copytree`: Function for recursively copying directory trees
- `sqlite.sqlite_version`: Function for getting cached SQLite version information
- `sqlite.supports_generated_columns`: Function for checking SQLite generated column support
- `sqlite.supports_table_xinfo`: Function for checking SQLite table XINFO support
- `testing.TestClient`: Test utility for making HTTP requests to Datasette instances
- `testing.TestResponse`: Wrapper for inspecting HTTP test responses

Note: The exact public API may vary based on what is imported and re-exported in the module's `__init__.py` file.

## Dependencies:
- Internal: None (pure utility module)
- External: 
  - `httpx` (for testing utilities)
  - `json` (for JSON serialization)
  - `os` (for file operations)
  - `sqlite3` (for SQLite version checking)
  - `typing` (for type hints)

## Constraints:
- All ASGI utilities require proper ASGI scope initialization
- BaseConverter requires unique digit sets for valid conversions
- SQLite version checking functions rely on SQLite installation availability
- Testing utilities require a properly initialized Datasette instance
- Thread safety: Most utilities are stateless and thus thread-safe

---

## Files

- [`__init__.py`](utils/__init__.md)
- [`asgi.py`](utils/asgi.md)
- [`baseconv.py`](utils/baseconv.md)
- [`shutil_backport.py`](utils/shutil_backport.md)
- [`sqlite.py`](utils/sqlite.md)
- [`testing.py`](utils/testing.md)

