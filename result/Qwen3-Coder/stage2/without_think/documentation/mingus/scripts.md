# `scripts`

## Tree:
```
scripts/
└── api_doc_generator.py
```

## Role:
Generates comprehensive reStructuredText API documentation for Python modules and packages

## Description:
The scripts module provides tools for automatically generating API documentation in reStructuredText format for Python modules and packages. It is specifically designed to create wiki-style documentation suitable for Sphinx or similar documentation systems. This module serves as a documentation generation utility that recursively analyzes Python code structures to produce structured, readable documentation.

## Components:
- **Documize**: Main documentation generator class that creates reStructuredText documentation for Python modules
- **_is_class**: Utility function that filters classes for documentation inclusion by checking if they are regular classes and not excluded superclasses
- **_is_method**: Utility function that checks if an object is of a method type by comparing its type against a predefined set of method types
- **generate_package_wikidocs**: Function that generates reStructuredText wiki-style documentation files for all non-callable attributes of a specified Python package
- **main**: Entry point function for generating reStructuredText API documentation for the mingus music library across its core subpackages

## Public API:
- **Documize**: Core class for generating documentation for Python modules
  - `__init__(module_string='')`: Initializes the documentation generator with an optional module string
  - `output_wiki()`: Generates and returns complete wiki-style documentation for the configured module
  - `set_module(module_string)`: Sets the module to be documented
- **generate_package_wikidocs(package_string, file_prefix='ref', file_suffix='.wiki')**: Generates documentation files for all non-callable attributes of a Python package
- **main()**: Command-line entry point for generating documentation for mingus library subpackages
- **_is_class(cls)**: Utility function to determine if a class should be included in documentation
- **_is_method(obj)**: Utility function to check if an object is a method type

## Dependencies:
- **Internal imports**: None
- **External imports**: 
  - `sys`: Used for command-line argument handling and file I/O operations
  - `os`: Used for directory validation and file path operations
  - `inspect`: Used for inspecting function signatures and documentation
  - `types`: Used for type checking operations

## Constraints:
- The module requires valid Python module strings that can be evaluated using `eval()`
- All target modules must be importable and accessible in the current Python environment
- Command-line usage requires exactly one argument specifying a valid output directory
- Documentation generation may raise exceptions when dealing with malformed or inaccessible modules
- The generated documentation follows reStructuredText conventions and requires appropriate formatting tools for rendering

---

## Files

- [`api_doc_generator.py`](scripts/api_doc_generator.md)

