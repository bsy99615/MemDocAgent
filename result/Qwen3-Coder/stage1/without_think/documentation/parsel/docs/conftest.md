# `conftest.py`

## `docs.conftest.load_selector` · *function*

## Summary:
Loads a static file from the _static directory and creates a Parsel Selector instance from its content.

## Description:
This utility function facilitates documentation testing by loading static test files and converting their content into Parsel Selector objects. It's designed to be used in test fixtures or configuration files to provide consistent access to test data. The function constructs a path relative to the current module's directory, reads the specified file with UTF-8 encoding, and creates a Selector instance with any additional keyword arguments passed through.

## Args:
    filename (str): Name of the static file to load from the _static directory
    **kwargs: Additional keyword arguments passed to the Selector constructor

## Returns:
    parsel.Selector: A Parsel Selector instance created from the file content

## Raises:
    FileNotFoundError: When the specified file cannot be found in the _static directory
    UnicodeDecodeError: When the file cannot be decoded with UTF-8 encoding

## Constraints:
    Preconditions:
    - The _static directory must exist relative to the location of this function
    - The specified filename must refer to an existing file within the _static directory
    - The file content must be valid text that can be parsed by Parsel Selector
    
    Postconditions:
    - Returns a valid Parsel Selector instance
    - The returned selector contains the content of the specified file

## Side Effects:
    - Reads from the filesystem (specifically from the _static directory relative to this module)
    - No external state mutations or service calls

## Control Flow:
```mermaid
flowchart TD
    A[load_selector called] --> B{filename provided?}
    B -->|Yes| C[Construct path with _static]
    C --> D[Open file with UTF-8 encoding]
    D --> E[Read file content]
    E --> F[Create Selector(text=content, **kwargs)]
    F --> G[Return Selector instance]
    B -->|No| H[Raises TypeError]
```

## Examples:
```python
# Basic usage
selector = load_selector("test_page.html")

# Usage with additional Selector options
selector = load_selector("test_page.html", namespaces={"ns": "http://example.com"})
```

## `docs.conftest.setup` · *function*

## Summary:
Assigns the load_selector function to the provided namespace dictionary.

## Description:
This function takes a namespace dictionary and assigns the load_selector function to it under the key "load_selector". This is a simple utility function that enables the load_selector function to be accessed from the namespace.

## Args:
    namespace (dict): A dictionary representing the test namespace where utilities will be made available

## Returns:
    None: This function modifies the namespace in-place and does not return a value

## Raises:
    None: This function does not raise any exceptions

## Constraints:
    Preconditions:
    - The namespace parameter must be a mutable dictionary-like object
    - The `load_selector` function must be defined in the same module scope
    
    Postconditions:
    - The namespace dictionary will contain a "load_selector" key mapping to the `load_selector` function

## Side Effects:
    - Modifies the provided namespace dictionary in-place

## Control Flow:
```mermaid
flowchart TD
    A[setup called with namespace] --> B[Assign load_selector to namespace["load_selector"]]
    B --> C[Return None]
```

## Examples:
```python
# Basic usage
namespace = {}
setup(namespace)
# namespace now contains {"load_selector": load_selector}
```

