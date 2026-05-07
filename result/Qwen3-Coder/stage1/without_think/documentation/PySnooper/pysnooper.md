# `pysnooper`

## Tree:
    pysnooper/
    ├── pycompat.py
    ├── tracer.py
    ├── utils.py
    └── variables.py

## Role:
    Provides comprehensive code tracing and debugging capabilities for Python programs, enabling detailed monitoring of function execution, variable states, and execution flow.

## Description:
    The pysnooper module offers sophisticated debugging tools that allow developers to monitor function execution, track variable changes, and analyze program flow without modifying the source code. It's particularly valuable for debugging complex functions where traditional print statements or IDE debuggers are insufficient.

    This module is used throughout the repository wherever detailed execution monitoring is needed, especially in development environments, automated testing, and production debugging scenarios. It's consumed by:
    - Development tools that require detailed execution tracing
    - Automated test frameworks that need to monitor function behavior
    - Debugging utilities that provide runtime insights
    - Performance analysis tools that track execution timing

    The module is organized around a cohesive debugging theme:
    - Core tracing functionality in tracer.py
    - Variable inspection strategies in variables.py  
    - Utility functions in utils.py
    - Cross-version compatibility helpers in pycompat.py

## Components:
    - **Tracer**: Main class for enabling tracing of functions and code blocks
    - **FileWriter**: Utility for managing file output during tracing
    - **BaseVariable/Variables**: Classes for inspecting different types of variables
    - **Utils**: Various utility functions for formatting, representation, and processing
    - **Pycompat**: Compatibility layer for different Python versions

## Public API:
    - `Tracer`: Main debugging decorator and context manager
    - `Tracer.__call__`: Decorator interface for tracing functions/classes
    - `Tracer.__enter__/__exit__`: Context manager protocol for tracing blocks
    - `BaseVariable`: Abstract base class for variable inspection
    - `CommonVariable`: Base class for container-like variable inspection
    - `Keys`, `Indices`, `Attrs`, `Exploding`: Specific variable inspectors
    - `get_shortish_repr`, `truncate`, `normalize_repr`: Formatting utilities
    - `get_write_function`, `get_path_and_source_from_frame`: Core utilities

## Dependencies:
    - Internal: Uses components from all submodules (pycompat, tracer, utils, variables)
    - External: Standard library modules (inspect, sys, os, abc, collections, etc.)

## Constraints:
    - Thread safety: Uses thread-local storage for concurrent tracing contexts
    - Initialization: Requires proper setup of sys.trace function for tracing to work
    - Performance: Tracing adds overhead to execution, so should be used judiciously
    - File handling: When writing to files, overwrite flag must be used appropriately

---

## Files

- [`pycompat.py`](pysnooper/pycompat.md)
- [`tracer.py`](pysnooper/tracer.md)
- [`utils.py`](pysnooper/utils.md)
- [`variables.py`](pysnooper/variables.md)

