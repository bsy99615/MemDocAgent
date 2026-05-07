# `docs`

## Tree:
```
docs/
└── conftest.py
```

## Role:
Provides pytest configuration and utility functions for documentation-related tests and fixtures.

## Description:
This module serves as a pytest conftest file that configures test environments and provides reusable helper functions for documentation testing. It specifically offers utilities for loading selectors from static test data files, making these available to test functions through pytest's fixture system.

## Components:
- `load_selector(filename, **kwargs)` - Loads a Selector instance from a static test file
- `setup(namespace)` - Configures the pytest namespace with the load_selector function

```mermaid
graph TD
    A[setup] --> B[load_selector]
    B --> C[Selector(text=content)]
```

## Public API:
- `load_selector(filename, **kwargs)` - Loads a Selector from a static file in _static directory
  - Signature: `load_selector(filename, **kwargs)`
  - Description: Reads a selector definition from a static test file and creates a Selector instance
  - Usage: Used in documentation tests to load predefined selector configurations
- `setup(namespace)` - Sets up pytest namespace with load_selector
  - Signature: `setup(namespace)`
  - Description: Registers the load_selector function in the pytest namespace for test use
  - Usage: Automatically discovered and executed by pytest's conftest mechanism

## Dependencies:
- `os` - Standard library module for file path operations
- `Selector` - From `selinon` package, used for creating selector instances
- `__file__` - Built-in variable providing access to the current module's file path

## Constraints:
- The `load_selector` function expects selector definitions to exist in the `_static` subdirectory relative to this module
- All selector files loaded via `load_selector` must be valid text files containing selector definitions

---

## Files

- [`conftest.py`](docs/conftest.md)

