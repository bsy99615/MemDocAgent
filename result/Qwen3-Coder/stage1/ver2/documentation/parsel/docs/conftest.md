# `conftest.py`

## `docs.conftest.load_selector` · *function*

## Summary:
Loads a static file and creates a parsable selector object from its content.

## Description:
This function provides a convenient way to load static content files from the `_static` directory and convert them into selector objects for parsing and extraction. It's primarily used in testing or documentation contexts where static content needs to be parsed using the parsel library's CSS/XPath selection capabilities.

## Args:
    filename (str): Name of the file to load from the `_static` directory relative to this module.
    **kwargs: Additional keyword arguments passed directly to the Selector constructor.

## Returns:
    parsel.Selector: A selector object initialized with the content of the specified file.

## Raises:
    FileNotFoundError: When the specified file cannot be found in the `_static` directory.
    UnicodeDecodeError: When the file cannot be decoded using UTF-8 encoding.
    ValueError: When the Selector constructor receives invalid arguments.

## Constraints:
    Preconditions:
    - The file must exist in the `_static` directory relative to this module
    - The file must be readable and valid UTF-8 encoded text
    - The Selector constructor must accept the provided kwargs

    Postconditions:
    - Returns a valid parsel.Selector object
    - The returned selector contains the content of the specified file

## Side Effects:
    - Reads from the filesystem
    - May raise file I/O related exceptions

## Control Flow:
```mermaid
flowchart TD
    A[load_selector called] --> B{filename provided}
    B -- Yes --> C[Construct input_path]
    C --> D[Open file with UTF-8 encoding]
    D --> E[Read file content]
    E --> F[Create Selector(text=content, **kwargs)]
    F --> G[Return Selector object]
    B -- No --> H[Raises TypeError]
```

## Examples:
```python
# Load HTML content for parsing
selector = load_selector("example.html")

# Load XML content with custom namespace handling
selector = load_selector("example.xml", namespaces={'ns': 'http://example.com'})
```

## `docs.conftest.setup` · *function*

## Summary:
Assigns the load_selector function to a namespace dictionary.

## Description:
This function performs an in-place assignment operation that adds the load_selector function to the provided namespace dictionary with the key "load_selector". It is typically used in pytest conftest files to make test utilities available to test fixtures and documentation examples.

## Args:
    namespace (dict): A dictionary-like object that will be modified in-place.

## Returns:
    None: This function modifies the namespace in-place and does not return a value.

## Raises:
    None: This function does not explicitly raise exceptions.

## Constraints:
    Preconditions:
    - The namespace parameter must be a mutable mapping object (like a dict)
    
    Postconditions:
    - The namespace dictionary will contain a 'load_selector' key

## Side Effects:
    - Modifies the input namespace dictionary by adding a new key-value pair
    - No external I/O operations occur during this function call itself

## Control Flow:
```mermaid
flowchart TD
    A[setup called with namespace] --> B{namespace is dict-like}
    B -- Yes --> C[Assign load_selector to namespace["load_selector"]]
    C --> D[Return None]
    B -- No --> E[Proceed anyway (no error)]
```

## Examples:
```python
# Typical usage in pytest conftest.py
def setup(namespace):
    namespace["load_selector"] = load_selector

# After this call, namespace["load_selector"] references the load_selector function
```

