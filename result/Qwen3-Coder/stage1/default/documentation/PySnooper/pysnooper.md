# `pysnooper`

## Tree:
    pysnooper/
    ├── pycompat.py
    ├── tracer.py
    ├── utils.py
    └── variables.py

## Role:
    Provides comprehensive code tracing and variable inspection capabilities for debugging Python applications

## Description:
    The pysnooper module offers powerful debugging assistance by tracing function execution, monitoring variable changes, and providing detailed insights into program flow. It enables developers to understand how their code executes without modifying the source code or adding print statements.

    This module is primarily consumed by developers who need to debug complex programs or understand the behavior of existing code. It's used in development environments, testing frameworks, and debugging tools throughout the repository.

    The module is organized around three core concepts:
    1. Tracing infrastructure (tracer.py) - handles the core tracing mechanics
    2. Variable inspection (variables.py) - processes different types of variables for display
    3. Utility functions (utils.py) - provides supporting functionality for representation, streams, and compatibility

## Components:
    - **pycompat.py**: Contains compatibility utilities for cross-Python version support
    - **tracer.py**: Core tracing functionality including the Tracer class and related utilities
    - **utils.py**: Utility functions for streams, representations, and string handling
    - **variables.py**: Variable inspection classes for different data types (attributes, keys, indices)

    ```mermaid
    %%{init: {"theme": "default"}}%%
    graph TD
        A[tracer.Tracer] --> B[variables.Attrs]
        A --> C[variables.Keys]
        A --> D[variables.Indices]
        A --> E[variables.Exploding]
        A --> F[utils.WritableStream]
        A --> G[utils.get_shortish_repr]
        A --> H[utils.get_repr_function]
        A --> I[utils.truncate]
        A --> J[utils.normalize_repr]
        A --> K[pycompat.timedelta_format]
        A --> L[pycompat.timedelta_parse]
        B --> M[utils.get_shortish_repr]
        C --> M
        D --> M
        E --> M
        F --> N[utils.WritableStream]
        G --> O[utils.get_repr_function]
        G --> P[utils.normalize_repr]
        G --> Q[utils.truncate]
        H --> R[utils.get_repr_function]
        H --> S[utils.get_shortish_repr]
        I --> T[utils.truncate]
        J --> U[utils.normalize_repr]
        K --> V[pycompat.timedelta_format]
        L --> W[pycompat.timedelta_parse]
    ```

## Public API:
    - **Tracer**: Main class for creating tracing contexts with `__call__` and `__enter__`/`__exit__` methods
    - **get_write_function**: Factory function that produces write functions for specified output destinations
    - **get_local_reprs**: Creates ordered string representations of local variables from a Python execution frame
    - **WritableStream**: Abstract base class defining an interface for writable streams (requires implementation of write method)
    - **ensure_tuple**: Converts an input value to a tuple, preserving string values as single-element tuples
    - **get_repr_function**: Selects an appropriate representation function for an item based on custom type conditions
    - **get_shortish_repr**: Generates a shortened representation of an object with optional normalization and truncation
    - **normalize_repr**: Strips default formatting patterns from object representations for cleaner debugging output
    - **truncate**: Truncates a string to a specified maximum length, preserving characters from both ends
    - **shitcode**: Filters out non-printable ASCII characters from a string
    - **PathLike**: Abstract base class defining the protocol for path-like objects that support the `__fspath__` interface
    - **ABC**: Abstract base class compatibility wrapper for cross-Python-version support
    - **timedelta_format**: Formats a timedelta object by performing time extraction and formatting operations
    - **timedelta_parse**: Parses a time duration string into a datetime.timedelta object

## Dependencies:
    - Internal imports:
        - `pysnooper.pycompat`: Provides cross-version compatibility utilities including ABC and PathLike wrappers
        - `pysnooper.utils`: Supplies utility functions for representations, streams, and string handling
        - `pysnooper.variables`: Offers variable inspection classes for different data types
    - External imports:
        - `abc`: Standard library for abstract base class functionality (used by pycompat.ABC)
        - `collections`: Standard library for ordered dictionary support
        - `datetime`: Standard library for time-related operations
        - `inspect`: Standard library for introspection capabilities
        - `os`: Standard library for operating system interfaces
        - `sys`: Standard library for system-specific parameters and functions
        - `types`: Standard library for dynamic type creation and checking

## Constraints:
    - Tracer instances must be used as context managers (`with` statements) for proper resource management
    - The `depth` parameter in Tracer must be >= 1 to ensure meaningful tracing
    - Output destinations must be one of the supported types (None, str, PathLike, callable, or WritableStream)
    - When `overwrite=True` is specified, the output must be a path-like object (str or PathLike)
    - Thread safety: Tracer uses thread-local storage to maintain separate tracing contexts per thread
    - Variable inspection classes assume valid Python objects and handle exceptions gracefully

---

## Files

- [`pycompat.py`](pysnooper/pycompat.md)
- [`tracer.py`](pysnooper/tracer.md)
- [`utils.py`](pysnooper/utils.md)
- [`variables.py`](pysnooper/variables.md)

