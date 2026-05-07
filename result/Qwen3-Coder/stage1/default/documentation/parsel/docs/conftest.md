# `conftest.py`

## `docs.conftest.load_selector` · *function*

## Summary:
Loads and parses static test files into parsel Selector objects for testing and documentation parsing.

## Description:
This function provides a convenient way to load static test fixture files and convert them into parsel Selector objects. It's primarily used in documentation testing contexts to parse HTML, XML, or text content from static files. The function constructs the full file path by joining the directory containing the conftest.py file with "_static" and the provided filename, then reads the file content and creates a Selector instance.

## Args:
    filename (str): Name of the static file to load, relative to the "_static" directory
    **kwargs: Additional keyword arguments passed to the Selector constructor

## Returns:
    parsel.Selector: A Selector object initialized with the content of the loaded file

## Raises:
    FileNotFoundError: When the specified file cannot be found at the constructed path
    UnicodeDecodeError: When the file cannot be decoded with UTF-8 encoding
    ValueError: When the Selector constructor receives invalid arguments
    TypeError: When the Selector constructor receives arguments of incorrect types

## Constraints:
    Preconditions:
    - The file must exist at the constructed path (dirname(__file__) + "/_static/" + filename)
    - The file must be readable and valid UTF-8 encoded text
    - The Selector constructor must receive valid arguments
    
    Postconditions:
    - Returns a properly initialized parsel.Selector object
    - The returned Selector contains the parsed content from the file

## Side Effects:
    - Reads from the filesystem
    - May raise file I/O related exceptions

## Control Flow:
```mermaid
flowchart TD
    A[load_selector called] --> B{filename provided}
    B -->|Yes| C[Construct input_path]
    C --> D[Open file with UTF-8 encoding]
    D --> E[Read file content]
    E --> F[Create Selector(text=content, **kwargs)]
    F --> G[Return Selector object]
```

## Examples:
```python
# Load an HTML file for testing
selector = load_selector("test_page.html")

# Load an XML file with custom namespace handling
selector = load_selector("test_data.xml", namespaces={"ns": "http://example.com"})
```

## `docs.conftest.setup` · *function*

## Summary:
Injects the load_selector utility function into the pytest test namespace.

## Description:
This function serves as a pytest conftest setup hook that makes the `load_selector` function available in the test namespace. It is used to configure documentation testing environments by providing access to the `load_selector` utility function.

## Args:
    namespace (dict): A dictionary representing the pytest test namespace that will be modified in-place

## Returns:
    None: This function modifies the namespace dictionary in-place and returns nothing

## Raises:
    None: This function does not raise any exceptions

## Constraints:
    Preconditions:
    - The namespace parameter must be a mutable dictionary object
    - The `load_selector` function must be defined in the same module scope
    
    Postconditions:
    - The namespace dictionary will have a "load_selector" key added
    - The value associated with the "load_selector" key will reference the load_selector function

## Side Effects:
    - Modifies the input namespace dictionary in-place
    - No direct I/O operations occur at this function level

## Control Flow:
```mermaid
flowchart TD
    A[setup called with namespace] --> B{namespace is dict}
    B -->|Yes| C[Assign load_selector to namespace["load_selector"]]
    C --> D[Return None]
```

## Examples:
```python
# In a pytest conftest.py file
def setup(namespace):
    namespace["load_selector"] = load_selector

# Usage in documentation tests
def test_example():
    selector = load_selector("sample.html")
    # Use selector for content extraction
```

