# `docs`

## Tree:
```
docs/
└── conftest.py
```

## Role:
Provides pytest configuration and test utilities for documentation-related tests

## Description:
The docs module serves as a pytest configuration and testing utilities container specifically for documentation-related test suites. It provides helper functions that facilitate loading static test files and making them available within test fixtures. This module acts as a centralized location for documentation test infrastructure, ensuring consistent access to test data and reducing boilerplate in test configurations.

## Components:
- `load_selector(filename, **kwargs)` - Loads static files from _static directory and creates Parsel Selector instances for parsing
- `setup(namespace)` - Configures test fixtures by making load_selector available in pytest test namespaces

## Public API:
- `load_selector(filename, **kwargs)` - Loads static test files and returns Parsel Selector instances for HTML/XML parsing
- `setup(namespace)` - Registers load_selector function in pytest test namespaces for easy access

## Dependencies:
- parsel - Used for HTML/XML parsing capabilities
- Standard library modules (os.path, io) - For file operations

## Constraints:
- The _static directory must exist relative to the module location
- Static files must be readable with UTF-8 encoding
- Namespace dictionaries must be mutable for setup function

---

## Files

- [`conftest.py`](docs/conftest.md)

