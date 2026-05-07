# `conftest.py`

## `docs.conftest.load_selector` · *function*

## Summary:
Loads and parses HTML/XML content from a static file into a Parsel Selector object.

## Description:
This function provides a convenient way to load static test or documentation files and parse them into Parsel Selector objects for content extraction and manipulation. It is primarily used in documentation testing and static content processing workflows.

The function is extracted into its own utility to encapsulate the file I/O and parsing logic, making test configurations cleaner and reducing code duplication when multiple tests need to load similar static content.

## Args:
    filename (str): The name of the file to load from the `_static` directory relative to this module's location.
    **kwargs: Additional keyword arguments passed to the Parsel Selector constructor for custom parsing options.

## Returns:
    parsel.Selector: A Parsel Selector object initialized with the content of the loaded file.

## Raises:
    FileNotFoundError: When the specified file does not exist in the `_static` directory.
    UnicodeDecodeError: When the file cannot be decoded using UTF-8 encoding.

## Constraints:
    Preconditions:
        - The file must exist in the `_static` subdirectory relative to this module's location.
        - The file must be readable and valid UTF-8 encoded text.
    Postconditions:
        - The returned Selector object is ready for content extraction operations.
        - The file is properly closed after reading.

## Side Effects:
    - Reads from the filesystem at runtime.
    - May raise file system related exceptions if the file is inaccessible or malformed.

## Control Flow:
```mermaid
flowchart TD
    A[load_selector called] --> B{filename valid?}
    B -- Yes --> C[Construct input_path]
    C --> D[Open file with utf-8 encoding]
    D --> E[Read file content]
    E --> F[Create Selector(text=content, **kwargs)]
    F --> G[Return Selector object]
    B -- No --> H[Throw FileNotFoundError]
```

## Examples:
```python
# Basic usage
selector = load_selector("example.html")

# With custom selector options
selector = load_selector("example.html", namespaces={'ns': 'http://example.com'})

# Usage in a test context
def test_content_extraction():
    selector = load_selector("test_page.html")
    assert selector.css('h1').get() == '<h1>Example</h1>'
```

## `docs.conftest.setup` · *function*

## Summary:
Configures a test namespace by registering the load_selector utility function for use in documentation tests.

## Description:
This function serves as a configuration hook for the Sybil documentation testing framework. It registers the load_selector utility function in the provided namespace, making it available for use in doctest and code block parsers within documentation files. This enables documentation authors to reference load_selector directly in their examples, simplifying the process of loading static content for testing purposes.

The function is extracted into its own utility to maintain clean separation between test configuration logic and the core functionality it enables. This approach allows for easy reuse across different documentation test suites while keeping the namespace management centralized.

## Args:
    namespace (dict): A dictionary representing the test namespace to be configured. This namespace will be modified in-place to include the load_selector function.

## Returns:
    None: This function does not return a value. It modifies the namespace dictionary in-place.

## Raises:
    None: This function does not explicitly raise any exceptions.

## Constraints:
    Preconditions:
        - The namespace parameter must be a mutable dictionary object.
        - The load_selector function must be defined in the same module scope.
    Postconditions:
        - The namespace dictionary will contain a key "load_selector" mapping to the load_selector function.
        - The namespace modification occurs in-place.

## Side Effects:
    - Modifies the input namespace dictionary by adding a new key-value pair.
    - No external I/O operations or state changes beyond the namespace update.

## Control Flow:
```mermaid
flowchart TD
    A[setup called with namespace] --> B{namespace is dict?}
    B -- Yes --> C[Set namespace["load_selector"] = load_selector]
    C --> D[Return None]
    B -- No --> E[Proceed with assignment anyway]
    E --> D
```

## Examples:
```python
# Typical usage in conftest.py for documentation testing
import pytest
from docs.conftest import setup

def pytest_configure(config):
    # Configure the test namespace for documentation tests
    namespace = {}
    setup(namespace)
    config.option.namespace = namespace

# Usage in documentation examples
# >>> selector = load_selector("example.html")
# >>> selector.css('h1').get()
# '<h1>Example</h1>'
```

