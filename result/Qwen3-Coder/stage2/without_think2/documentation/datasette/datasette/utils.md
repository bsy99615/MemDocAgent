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
Provides foundational utilities for ASGI HTTP handling, data conversion, file operations, SQLite version management, and testing infrastructure.

## Description:
The utils module serves as a collection of low-level helper functions and classes that support core Datasette functionality. It provides essential building blocks for HTTP request/response handling in ASGI environments, data encoding/decoding utilities, file system operations, database version checking, and testing infrastructure. These utilities are designed to be reused across different parts of the Datasette codebase and are not tied to any specific application logic.

## Components:
- **ASGI Utilities**: Request and Response wrappers for ASGI applications, along with helper functions for sending various response types
- **Base Conversion**: Tools for encoding and decoding numbers using custom alphabets
- **Shutil Backport**: File copying utilities with enhanced functionality compared to standard library versions
- **SQLite Utilities**: Version checking and feature detection for SQLite database compatibility
- **Testing Infrastructure**: Test client and response wrappers for simulating HTTP requests in test environments

## Public API:
- `asgi.Request`: ASGI HTTP request wrapper with convenient property access
- `asgi.Response`: ASGI HTTP response builder with factory methods for common content types
- `asgi.asgi_send`, `asgi.asgi_send_html`, `asgi.asgi_send_json`, `asgi.asgi_send_redirect`, `asgi.asgi_static`: ASGI response sending utilities
- `baseconv.BaseConverter`: Base-N number conversion tools
- `shutil_backport.copytree`: Enhanced file tree copying with ignore patterns
- `sqlite.sqlite_version`, `sqlite.supports_generated_columns`, `sqlite.supports_table_xinfo`: SQLite version and feature detection utilities
- `testing.TestClient`, `testing.TestResponse`: Testing infrastructure for HTTP request simulation

## Dependencies:
- Internal: None
- External: `httpx`, `shutil`, `sqlite3`, `typing`, `os`, `pathlib`, `json`, `asyncio`, `contextlib`, `functools`, `inspect`, `re`, `time`, `urllib.parse`, `uuid`, `warnings`

## Constraints:
- All utilities must be thread-safe and stateless where possible
- ASGI utilities must comply with ASGI specification for interoperability
- SQLite utilities must handle version comparisons robustly
- Testing utilities must provide deterministic behavior for reproducible tests

---

## Files

- [`__init__.py`](utils/__init__.md)
- [`asgi.py`](utils/asgi.md)
- [`baseconv.py`](utils/baseconv.md)
- [`shutil_backport.py`](utils/shutil_backport.md)
- [`sqlite.py`](utils/sqlite.md)
- [`testing.py`](utils/testing.md)

