# `pysnooper`

## Tree:
    - pysnooper/
      - pycompat.py
      - tracer.py
      - utils.py
      - variables.py

## Role:
    - Provides debugging instrumentation for Python functions and classes, capturing detailed execution traces including variable states, execution timing, and source code context.

## Description:
    - The pysnooper module enables comprehensive debugging by instrumenting Python functions and classes to capture and log detailed execution information. It leverages Python's tracing mechanism to monitor function calls, returns, and exceptions, providing insights into variable states, execution timing, and source code context.

    - Primary consumers include developers using the `@pysnooper.snoop` decorator or `pysnooper.Tracer` context manager to debug their code. The module is also used internally by the pysnooper library itself for its own tracing operations.

    - The module is organized around several cohesive layers:
        1. **Core Tracing Infrastructure** (`tracer.py`): Handles the main tracing logic, including the Tracer class, file writing, and event handling.
        2. **Variable Inspection System** (`variables.py`): Manages how different types of variables are inspected and displayed during tracing.
        3. **Utility Functions** (`utils.py`): Provides helper functions for representation, path handling, and compatibility.
        4. **Cross-Version Compatibility** (`pycompat.py`): Ensures consistent behavior across different Python versions.

## Components:
    - **pycompat.py**
        - `PathLike`: Abstract base class for path-like objects supporting the `__fspath__` protocol.
        - `timedelta_format`: Utility for formatting time deltas.
    - **tracer.py**
        - `FileWriter`: Writes text content to files with overwrite or append behavior.
        - `Tracer`: Main debugging utility that instruments functions and classes to provide detailed execution tracing.
        - `UnavailableSource`: Placeholder for unavailable source code.
        - `get_write_function`: Factory function that returns appropriate write functions for different output destinations.
    - **utils.py**
        - `WritableStream`: Abstract base class for writable streams.
        - `ensure_tuple`: Converts input to tuple format.
        - `get_repr_function`: Returns appropriate representation function for an item.
        - `get_shortish_repr`: Generates a shortened string representation of an object.
        - `normalize_repr`: Normalizes string representations.
        - `shitcode`: Sanitizes strings by replacing non-ASCII characters with '?'.
        - `truncate`: Truncates strings with ellipsis.
        - `_check_methods`: Validates class method implementations.
    - **variables.py**
        - `BaseVariable`: Abstract base class for variable inspection.
        - `CommonVariable`: Abstract base class implementing shared functionality for variable inspection.
        - `Attrs`: Inspects objects with attributes.
        - `Exploding`: Dynamically selects inspection strategy based on variable type.
        - `Indices`: Handles indexed sequence access patterns.
        - `Keys`: Inspects dictionary-like mappings.
        - `needs_parentheses`: Determines if parentheses are needed for correct parsing.

## Public API:
    - `pysnooper.snoop`: Decorator for tracing function execution.
    - `pysnooper.Tracer`: Context manager for tracing code blocks.
    - `pysnooper.get_write_function`: Factory for creating write functions for different output destinations.
    - `pysnooper.ensure_tuple`: Utility for converting inputs to tuples.
    - `pysnooper.get_shortish_repr`: Utility for generating short string representations.
    - `pysnooper.truncate`: Utility for truncating strings.
    - `pysnooper.shitcode`: Utility for sanitizing strings.
    - `pysnooper.normalize_repr`: Utility for normalizing string representations.

## Dependencies:
    - Internal imports:
        - `pysnooper.pycompat`: For cross-version compatibility utilities.
        - `pysnooper.tracer`: Core tracing functionality.
        - `pysnooper.utils`: Utility functions.
        - `pysnooper.variables`: Variable inspection system.
    - External imports:
        - `collections.abc`: For abstract base class definitions.
        - `inspect`: For introspecting Python frames and code.
        - `os`: For file system operations.
        - `sys`: For system-level operations and tracing.
        - `time`: For timing measurements.
        - `types`: For type checking and handling.
        - `typing`: For type annotations.

## Constraints:
    - Callers must respect the threading model: the Tracer class uses thread-local storage for safe concurrent operation.
    - The `normalize` parameter cannot be used with `thread_info=True` in Tracer.
    - File output destinations must be valid paths or writable streams.
    - Variables passed to `watch` or `watch_explode` must be valid Python expressions that can be evaluated in a frame context.
    - The `depth` parameter in Tracer must be >= 1.

---

## Files

- [`pycompat.py`](pysnooper/pycompat.md)
- [`tracer.py`](pysnooper/tracer.md)
- [`utils.py`](pysnooper/utils.md)
- [`variables.py`](pysnooper/variables.md)

