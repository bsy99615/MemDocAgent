# `conftest.py`

## `docs.conftest.load_selector` · *function*

## Summary:
Loads and parses a static file into a parsel Selector object for document testing.

## Description:
This function reads a file from the `_static` directory relative to the current module and creates a parsel Selector instance from its contents. It's designed to simplify loading test fixtures or documentation examples for parsing and validation in documentation tests.

The function is typically used in documentation testing setups where HTML/XML content needs to be parsed and validated as part of the documentation verification process.

## Args:
    filename (str): Name of the file to load from the `_static` directory
    **kwargs: Additional keyword arguments passed to the parsel Selector constructor

## Returns:
    parsel.Selector: A Selector object initialized with the contents of the loaded file

## Raises:
    FileNotFoundError: When the specified file cannot be found in the `_static` directory
    UnicodeDecodeError: When the file cannot be decoded with UTF-8 encoding

## Constraints:
    Preconditions:
        - The file must exist in the `_static` subdirectory relative to this module
        - The file must be readable and valid UTF-8 encoded text
    Postconditions:
        - Returns a valid parsel Selector object initialized with the file contents
        - The returned Selector can be used for CSS selector and XPath queries

## Side Effects:
    - Reads from the filesystem
    - Opens and closes a file handle

## Control Flow:
```mermaid
flowchart TD
    A[load_selector called] --> B{filename provided}
    B -- Yes --> C[Construct input_path]
    C --> D[Open file with utf-8 encoding]
    D --> E[Read file contents]
    E --> F[Create Selector(text=contents, **kwargs)]
    F --> G[Return Selector object]
    B -- No --> H[Raises TypeError]
```

## Examples:
```python
# Load a simple HTML file for parsing
selector = load_selector("example.html")

# Load with custom parser options
selector = load_selector("complex.html", type="html")
```

## `docs.conftest.setup` · *function*

## Summary:
Configures the test namespace with a utility function for loading HTML/XML documents in documentation tests.

## Description:
This function serves as a pytest configuration hook that extends the test namespace with the `load_selector` utility function. It's designed to make document parsing helpers available throughout documentation tests, particularly those using the Sybil documentation testing framework.

The function is typically called by pytest during test collection to prepare the testing environment with necessary utilities for parsing HTML/XML content in documentation examples.

## Args:
    namespace (dict): A dictionary representing the test namespace to be modified
        - Type: dict
        - Purpose: Provides a mechanism to inject test utilities into the global test scope

## Returns:
    None: This function modifies the namespace in-place and does not return a value

## Raises:
    None: This function does not raise any exceptions

## Constraints:
    Preconditions:
        - The `namespace` parameter must be a mutable dictionary
        - The `load_selector` function must be defined in the same module scope
    Postconditions:
        - The `load_selector` function is added to the namespace under the key "load_selector"
        - The namespace is modified in-place with the new utility function

## Side Effects:
    - Modifies the provided namespace dictionary in-place
    - No external I/O operations or state mutations beyond namespace modification

## Control Flow:
```mermaid
flowchart TD
    A[setup called with namespace] --> B{namespace is dict}
    B -- Yes --> C[Add load_selector to namespace]
    C --> D[Return None]
    B -- No --> E[Proceed anyway (no error)]
```

## Examples:
```python
# Typical usage in pytest conftest.py
def setup(namespace):
    namespace["load_selector"] = load_selector

# After setup, load_selector becomes available in tests:
def test_example():
    selector = load_selector("example.html")
    # Use selector for parsing documentation examples
```

