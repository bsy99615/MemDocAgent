# `scripts`

## Tree:
scripts/
└── api_doc_generator.py

## Role:
Generates Sphinx-compatible API documentation for Python modules by recursively analyzing their attributes, functions, and classes.

## Description:
The scripts.api_doc_generator module is responsible for automatically generating comprehensive API documentation in reStructuredText format for Python modules. It provides tools for both detailed module documentation generation and individual attribute documentation creation. The module is primarily used for maintaining the API reference documentation of the mingus music library.

## Components:
- Documize: Main class for generating documentation from Python modules
- generate_package_wikidocs: Function to generate wiki documentation files for package attributes
- main: Entry point function for generating complete API documentation
- _is_class: Utility function to filter user-defined classes from built-ins
- _is_method: Utility function to identify method types for documentation processing

## Public API:
- Documize(module_string: str = ''): Constructor for documentation generator
- Documize.output_wiki(): Generates complete documentation string for the configured module
- generate_package_wikidocs(package_string: str, file_prefix: str = 'ref', file_suffix: str = '.wiki'): Creates individual wiki files for package attributes
- main(): Entry point for command-line documentation generation

## Dependencies:
- Internal: None
- External: sys (for command-line argument handling and file I/O)

## Constraints:
- The module uses eval() operations which can pose security risks with untrusted input
- Requires valid Python module paths for documentation generation
- Command-line usage expects exactly one argument specifying a valid output directory

---

## Files

- [`api_doc_generator.py`](scripts/api_doc_generator.md)

