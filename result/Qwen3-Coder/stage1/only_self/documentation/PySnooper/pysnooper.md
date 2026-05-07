# `pysnooper`

## Tree:
    pysnooper/
    ├── pycompat.py
    ├── tracer.py
    ├── utils.py
    └── variables.py

## Role:
    Provides comprehensive function tracing and debugging capabilities for Python programs, enabling detailed monitoring of variable states, execution flow, and timing information during runtime.

## Description:
    The pysnooper module offers a powerful debugging solution that allows developers to monitor function execution in real-time. It provides detailed insights into variable states, execution flow, and performance metrics without requiring traditional breakpoints or debuggers. The module is designed to be used as a decorator or context manager to trace function calls and variable modifications.

    This module is primarily consumed by developers who need to debug complex functions or understand program behavior without modifying source code extensively. It's particularly valuable for:
    - Debugging nested function calls and variable interactions
    - Monitoring performance bottlenecks through timing information
    - Understanding data flow through complex programs
    - Inspecting variable states at different execution points

    The module is organized around a cohesive debugging philosophy where tracing functionality is centralized in the Tracer class, while supporting utilities are distributed across specialized modules for different concerns:
    - pycompat.py: Handles Python version compatibility and path protocols
    - tracer.py: Implements the core tracing engine and utilities
    - utils.py: Provides general-purpose utilities for formatting and I/O
    - variables.py: Manages variable inspection and representation logic

## Components:
    - **pycompat.py**: Contains compatibility layers for Python versions and filesystem path protocols
    - **tracer.py**: Houses the main Tracer class and related tracing utilities
    - **utils.py**: Provides utility functions for writing, representation, and string manipulation
    - **variables.py**: Implements variable inspection classes for different data structures

## Public API:
    - `pysnooper.snoop()`: Main decorator function that creates a Tracer instance with default settings
    - `pysnooper.Tracer`: Main tracing class for configuring and applying tracing to functions or classes
    - `pysnooper.Tracer.__call__()`: Enables tracing of functions or classes when used as a decorator
    - `pysnooper.Tracer.__enter__()`: Enters tracing context for manual tracing
    - `pysnooper.Tracer.__exit__()`: Exits tracing context and reports execution duration
    - `pysnooper.Tracer.__init__()`: Initializes a Tracer instance with configuration options
    - `pysnooper.utils.get_shortish_repr()`: Creates cleaned and optionally truncated string representations of objects
    - `pysnooper.utils.get_repr_function()`: Selects appropriate representation functions for objects
    - `pysnooper.utils.truncate()`: Truncates strings with ellipsis in the center
    - `pysnooper.utils.normalize_repr()`: Applies regex-based cleaning to representation strings
    - `pysnooper.utils.shitcode()`: Filters out non-printable characters from strings
    - `pysnooper.utils.ensure_tuple()`: Converts inputs to tuples with special handling for strings
    - `pysnooper.utils.WritableStream`: Abstract base class for writable streams
    - `pysnooper.variables.BaseVariable`: Abstract base class for variable inspection
    - `pysnooper.variables.CommonVariable`: Abstract base class for common variable inspection functionality
    - `pysnooper.variables.Attrs`: Variable inspection for object attributes
    - `pysnooper.variables.Keys`: Variable inspection for dictionary-like objects
    - `pysnooper.variables.Indices`: Variable inspection for sequence objects
    - `pysnooper.variables.Exploding`: Dynamic variable inspection dispatcher
    - `pysnooper.tracer.FileWriter`: Utility for writing content to files with overwrite/append behavior
    - `pysnooper.tracer.UnavailableSource`: Sentinel object for unavailable source code
    - `pysnooper.tracer.get_local_reprs()`: Generates formatted representations of local variables
    - `pysnooper.tracer.get_path_and_source_from_frame()`: Retrieves file path and source code from frames
    - `pysnooper.tracer.get_write_function()`: Returns appropriate write function based on output destination
    - `pysnooper.pycompat.ABC`: Compatibility wrapper for abstract base classes
    - `pysnooper.pycompat.PathLike`: Abstract base class for filesystem path protocol

## Dependencies:
    - Internal imports:
        - `pysnooper.utils`: Used for representation and utility functions
        - `pysnooper.variables`: Used for variable inspection logic
        - `pysnooper.pycompat`: Used for compatibility features
    - External imports:
        - `sys`: Used for setting trace functions and managing execution context
        - `inspect`: Used for accessing frame information and execution context
        - `time`: Used for timing measurements
        - `os`: Used for file system operations and path handling
        - `types`: Used for type checking and frame objects
        - `collections`: Used for OrderedDict data structures
        - `threading`: Used for thread-local storage and synchronization
        - `abc`: Used for abstract base class definitions
        - `re`: Used for regular expression operations in normalization
        - `itertools`: Used for chain operations in key enumeration
        - `pathlib`: Used for path manipulation in some compatibility cases
        - `zipfile`: Used for reading from ZIP archives in Ansible contexts

## Constraints:
    - Thread-safety: The module uses thread-local storage to maintain separate tracing contexts per thread
    - Ordering requirements: Tracing must be properly entered and exited using context managers or decorators
    - Initialization prerequisites: The Tracer class requires proper initialization with valid configuration parameters
    - Depth control: The tracing depth parameter must be >= 1 to avoid invalid tracing behavior
    - Output handling: When using overwrite=True, the output must be a file path (str or PathLike)
    - Normalization conflicts: When normalize flag is True, thread_info flag must be False

---

## Files

- [`pycompat.py`](pysnooper/pycompat.md)
- [`tracer.py`](pysnooper/tracer.md)
- [`utils.py`](pysnooper/utils.md)
- [`variables.py`](pysnooper/variables.md)

