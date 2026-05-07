# `utils.py`

## `parsel.utils.flatten` · *function*

## Summary:
Converts a nested iterable structure into a flat list, preserving strings and bytes as atomic elements.

## Description:
Flattens arbitrarily nested iterable structures (lists, tuples, sets, etc.) into a single-level list. This function serves as a convenience wrapper around the `iflatten` generator, converting its iterator output into a concrete list. Strings and bytes are treated as atomic elements and are not further flattened, maintaining semantic distinction between collection types and scalar values.

## Args:
    x (Iterable[Any]): An iterable containing potentially nested elements of any type, including lists, tuples, sets, and other iterable collections.

## Returns:
    List[Any]: A flat list containing all elements from the nested structure, with strings and bytes preserved as individual elements rather than being split into characters.

## Raises:
    None

## Constraints:
    Preconditions: Input must be iterable
    Postconditions: All nested structures are flattened into a single list, with strings and bytes remaining intact as atomic elements

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input Iterable x] --> B[Call iflatten(x)]
    B --> C[Convert iterator to list]
    C --> D[Return flattened list]
```

## Examples:
```python
# Basic flattening
flatten([[1, 2], [3, 4]])  # Returns [1, 2, 3, 4]

# Nested structures
flatten([1, [2, [3, 4]], 5])  # Returns [1, 2, 3, 4, 5]

# Preserving strings
flatten(["hello", ["world"]])  # Returns ["hello", "world"]

# Mixed types
flatten([1, "text", [2, [3, 4]], b"bytes"])  # Returns [1, "text", 2, 3, 4, b"bytes"]
```

## `parsel.utils.iflatten` · *function*

## Summary:
Generates flattened elements from a nested iterable structure, preserving strings and bytes as atomic elements.

## Description:
A recursive generator that traverses nested iterable structures and yields individual elements. Strings and bytes are treated as atomic elements and not further flattened, while other iterable types (lists, tuples, sets, etc.) are recursively expanded. This function is designed to handle arbitrarily nested structures while maintaining semantic distinction between collection types and scalar string/byte values.

## Args:
    x (Iterable[Any]): An iterable containing potentially nested elements of any type.

## Returns:
    Iterator[Any]: A generator yielding individual elements from the flattened structure.

## Raises:
    None

## Constraints:
    Preconditions: Input must be iterable
    Postconditions: All nested structures are flattened, strings and bytes remain intact

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input Iterable x] --> B{Iterate through elements}
    B --> C{Element is list-like?}
    C -- Yes --> D[Yield from flatten(element)]
    C -- No --> E[Yield element]
    D --> F[Back to iteration]
    E --> F
    F --> G{More elements?}
    G -- Yes --> B
    G -- No --> H[Generator completes]
```

## Examples:
```python
# Basic flattening
list(iflatten([[1, 2], [3, 4]]))  # Returns [1, 2, 3, 4]

# Nested structures
list(iflatten([1, [2, [3, 4]], 5]))  # Returns [1, 2, 3, 4, 5]

# Preserving strings
list(iflatten(["hello", ["world"]]))  # Returns ["hello", "world"]

# Mixed types
list(iflatten([1, "text", [2, [3, 4]], b"bytes"]))  # Returns [1, "text", 2, 3, 4, b"bytes"]
```

## `parsel.utils._is_listlike` · *function*

## Summary:
Determines whether an object is list-like (iterable but not a string or bytes).

## Description:
Checks if an object has an `__iter__` attribute while excluding string and bytes types. This utility function helps distinguish between iterable collections (like lists, tuples, sets) and string/bytes objects, which are technically iterable but often treated specially in parsing and processing contexts.

## Args:
    x (Any): The object to test for list-likeness.

## Returns:
    bool: True if the object is iterable and not a string or bytes; False otherwise.

## Raises:
    None

## Constraints:
    Preconditions: None
    Postconditions: Always returns a boolean value

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input x] --> B{hasattr(x, "__iter__")?}
    B -- Yes --> C{isinstance(x, (str, bytes))?}
    C -- Yes --> D[Return False]
    C -- No --> E[Return True]
    B -- No --> F[Return False]
```

## Examples:
```python
# List-like objects
_is_listlike([1, 2, 3])      # Returns True
_is_listlike((1, 2, 3))      # Returns True
_is_listlike({1, 2, 3})      # Returns True
_is_listlike(range(3))       # Returns True

# Non-list-like objects
_is_listlike("hello")        # Returns False
_is_listlike(b"hello")       # Returns False
_is_listlike(42)             # Returns False
_is_listlike(None)           # Returns False
```

## `parsel.utils.extract_regex` · *function*

## Summary
Extracts strings from text using regular expressions, with support for named capture groups and HTML entity processing.

## Description
This function provides a flexible way to extract text patterns from input text using regular expressions. It supports both compiled regex patterns and string patterns, and can handle named capture groups specifically designed for extraction. The function automatically flattens nested results and offers optional HTML entity decoding for cleaner output.

## Args
- regex (Union[str, Pattern[str]]): A regular expression pattern as either a string or compiled Pattern object
- text (str): The input text to search for matches
- replace_entities (bool): Whether to process HTML entities in extracted strings. Defaults to True

## Returns
- List[str]: A list of extracted strings. Returns an empty list if no matches are found or if the "extract" group is None.

## Raises
- None explicitly raised, though underlying regex operations may raise exceptions from the re module

## Constraints
- Preconditions: 
  - text must be a string
  - regex must be either a string or compiled Pattern object
- Postconditions:
  - Always returns a list of strings
  - If replace_entities=True, returned strings have HTML entities decoded (except lt and amp)

## Side Effects
- None

## Control Flow
```mermaid
flowchart TD
    A[Input regex and text] --> B{Is regex string?}
    B -->|Yes| C[Compile regex with re.UNICODE]
    B -->|No| C
    C --> D{Does regex have "extract" group?}
    D -->|Yes| E[Use regex.search()]
    D -->|No| F[Use regex.findall()]
    E --> G{AttributeError?}
    G -->|Yes| H[Set strings = []]
    G -->|No| I{extracted is None?}
    I -->|Yes| J[Set strings = []]
    I -->|No| K[Set strings = [extracted]]
    F --> L[Set strings = findall results]
    L --> M[Flatten strings]
    M --> N{replace_entities=False?}
    N -->|Yes| O[Return strings]
    N -->|No| P[Process HTML entities]
    P --> O
```

## Examples
```python
# Basic extraction
extract_regex(r'\d+', 'Price: $123')  # Returns ['123']

# Using named capture group
extract_regex(r'(?P<extract>\d+)', 'Price: $123')  # Returns ['123']

# With HTML entities
extract_regex(r'<title>(.*?)</title>', '<title>Test &amp; More</title>')  # Returns ['Test & More']

# Without entity replacement
extract_regex(r'<title>(.*?)</title>', '<title>Test &amp; More</title>', replace_entities=False)  # Returns ['Test &amp; More']
```

## `parsel.utils.shorten` · *function*

## Summary:
Truncates text to a specified width while preserving readability with an optional suffix.

## Description:
This utility function shortens input text to fit within a specified character limit, appending a suffix when truncation occurs. It's commonly used for creating concise representations of longer text strings while maintaining visual cues about truncation.

The function is designed to handle various edge cases including when text is already shorter than the width limit, when the suffix is longer than the available space, and when invalid width parameters are provided.

## Args:
    text (str): The input string to be truncated. Must be a valid string.
    width (int): Maximum allowed length of the returned string. Must be non-negative.
    suffix (str): Suffix to append when truncation occurs. Defaults to "...". Must be a valid string.

## Returns:
    str: The truncated text. If the original text is shorter than or equal to width, returns the original text unchanged. Otherwise, returns the truncated text with the suffix appended.

## Raises:
    ValueError: When width is negative (less than 0).

## Constraints:
    Preconditions:
        - text must be a valid string
        - width must be a non-negative integer
        - suffix must be a valid string
    
    Postconditions:
        - Returned string length will be less than or equal to width
        - If truncation occurs, suffix will be appended to the truncated text
        - If no truncation occurs, original text is returned unchanged

## Side Effects:
    None. This function is pure and has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start: shorten(text, width, suffix)] --> B{len(text) <= width?}
    B -- Yes --> C[Return text]
    B -- No --> D{width > len(suffix)?}
    D -- Yes --> E[Return text[:width-len(suffix)] + suffix]
    D -- No --> F{width >= 0?}
    F -- Yes --> G[Return suffix[len(suffix)-width:]]
    F -- No --> H[Raise ValueError]
```

## Examples:
    >>> shorten("Hello World", 5)
    'Hello...'
    
    >>> shorten("Short", 10)
    'Short'
    
    >>> shorten("Very long text", 8, "[...]")
    'Very [...]'
    
    >>> shorten("Test", 0)
    '...'
    
    >>> shorten("Test", -1)
    ValueError: width must be equal or greater than 0
```

