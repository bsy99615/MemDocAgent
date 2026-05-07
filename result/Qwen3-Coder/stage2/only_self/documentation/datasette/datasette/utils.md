# `datasette.utils`

## Tree:
    utils/
    ├── __init__.py
    ├── asgi.py
    ├── baseconv.py
    ├── shutil_backport.py
    ├── sqlite.py
    └── testing.py

## Role:
    Provides foundational utilities and helper functions for Datasette's core functionality, including ASGI protocol handling, base conversion, file operations, SQLite version checking, and testing infrastructure.

## Description:
    The utils module serves as a centralized collection of low-level utility functions and classes that support Datasette's main components. It encapsulates common operations needed across the application, such as ASGI request/response handling for web interactions, numeral system conversions, file copying with advanced features, SQLite version compatibility checks, and testing utilities for integration testing.

    This module is used extensively throughout Datasette's codebase as a dependency for core functionality. Primary consumers include the web application layer (via asgi.py), data processing components (via baseconv.py and sqlite.py), and test suites (via testing.py).

    The cohesion of this module is based on shared utility concepts rather than a single architectural layer. All components provide general-purpose functionality that can be reused across different parts of the application, making it a crucial foundation for Datasette's implementation.

## Components:
    - Request: ASGI request wrapper for HTTP parsing and access
    - Response: ASGI response builder for HTTP responses  
    - asgi_send: Convenience function for sending ASGI HTTP responses
    - asgi_send_file: Async file sending utility for ASGI
    - asgi_send_html: Helper for sending HTML responses
    - asgi_send_json: Helper for sending JSON responses
    - asgi_send_redirect: Helper for sending redirect responses
    - asgi_start: ASGI response start message preparation
    - asgi_static: ASGI middleware for serving static files
    - BaseConverter: Numeral system converter for custom bases
    - _copytree: Internal directory tree copying implementation
    - copytree: Directory tree copying with advanced options
    - _sqlite_version: Retrieves SQLite version via database query
    - sqlite_version: Cached SQLite version getter
    - supports_generated_columns: Determines if SQLite supports generated columns
    - supports_table_xinfo: Determines if SQLite supports TABLE_XINFO feature
    - TestClient: Test client for making HTTP requests to Datasette instances
    - TestResponse: Wrapper for examining HTTP responses in tests

## Public API:
    - Request: ASGI request wrapper for HTTP parsing and access
    - Response: ASGI response builder for HTTP responses
    - asgi_send: Sends ASGI HTTP response with content, status, and headers
    - asgi_send_file: Sends file asynchronously over ASGI
    - asgi_send_html: Sends HTML response with proper content-type
    - asgi_send_json: Serializes data to JSON and sends HTTP response
    - asgi_send_redirect: Sends HTTP redirect response
    - asgi_start: Initializes ASGI HTTP response with headers
    - asgi_static: Creates ASGI middleware for serving static files
    - BaseConverter: Converts integers between decimal and custom numeral systems
    - copytree: Copies directory trees recursively with advanced options
    - sqlite_version: Returns cached SQLite version for compatibility checks
    - supports_generated_columns: Determines if SQLite supports generated columns
    - supports_table_xinfo: Determines if SQLite supports TABLE_XINFO feature
    - TestClient: Test client for making HTTP requests to Datasette instances
    - TestResponse: Wrapper for examining HTTP responses in tests

## Dependencies:
    - Internal: None (pure utility module)
    - External: 
        - httpx: Used by TestClient for HTTP requests
        - sqlite3: Used by SQLite version checking utilities
        - os: Used by shutil_backport utilities for filesystem operations
        - json: Used by JSON response utilities

## Constraints:
    - ASGI utilities require valid ASGI scopes and send functions
    - BaseConverter requires unique digit sets for proper numeral system conversion
    - File operations in shutil_backport require proper filesystem permissions
    - SQLite version utilities require SQLite library availability
    - TestClient requires a valid Datasette instance for proper operation

---

## Files

- [`__init__.py`](utils/__init__.md)
- [`asgi.py`](utils/asgi.md)
- [`baseconv.py`](utils/baseconv.md)
- [`shutil_backport.py`](utils/shutil_backport.md)
- [`sqlite.py`](utils/sqlite.md)
- [`testing.py`](utils/testing.md)

