# `utils.py`

## `parsel.utils.flatten` · *function*

## Summary:
Converts a nested iterable structure into a flat list by recursively expanding list-like elements while preserving strings and bytes.

## Description:
A utility function that takes any iterable input and returns a flattened list representation. This function serves as a convenient interface to the underlying `iflatten` generator, converting its output into a concrete list. The flattening process recursively expands nested list-like structures while treating strings and bytes as atomic elements that are not further decomposed.

This function is commonly used in web scraping and data processing pipelines where nested HTML structures or complex data formats need to be simplified into linear sequences for easier manipulation and analysis.

## Args:
    x (Iterable[Any]): An iterable containing elements that may be nested structures such as lists, tuples, or other iterable objects

## Returns:
    List[Any]: A flat list containing all elements from the nested structure, with list-like elements recursively expanded and strings/bytes preserved as atomic units

## Raises:
    None

## Constraints:
    Preconditions: Input must be iterable
    Postconditions: All nested structures are flattened into a single-level list structure

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input Iterable x] --> B[Call iflatten(x)]
    B --> C[Convert generator to list]
    C --> D[Return flattened list]
```

## Examples:
```python
# Basic flattening of nested lists
result = flatten([[1, 2], [3, 4]])
# Returns: [1, 2, 3, 4]

# Flattening deeply nested structures
result = flatten([1, [2, [3, 4]], 5])
# Returns: [1, 2, 3, 4, 5]

# Preserving strings and bytes
result = flatten(["hello", ["world"], "foo"])
# Returns: ['hello', 'world', 'foo']

# Mixed data types
result = flatten([1, [2, 3], "text", [4, [5, 6]]])
# Returns: [1, 2, 3, 'text', 4, 5, 6]
```

## `parsel.utils.iflatten` · *function*

## Summary:
Generates flattened elements from a nested iterable structure, recursively expanding list-like elements while preserving strings and bytes.

## Description:
A generator function that processes an iterable and yields elements in a flattened structure. When an element is identified as list-like (using the internal `_is_listlike` function), it recursively flattens that element. Strings and bytes are treated as atomic elements and not further expanded, even though they are technically iterable.

This function is part of a larger flattening utility system where `flatten` serves as the list-returning counterpart that converts the generator output into a concrete list.

## Args:
    x (Iterable[Any]): An iterable containing elements that may be nested structures

## Returns:
    Iterator[Any]: A generator yielding individual elements from the flattened structure

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
    A[Input Iterable x] --> B{For each element el in x}
    B --> C{_is_listlike(el)?}
    C -- Yes --> D[Recursively yield from flatten(el)]
    C -- No --> E[Yield el as-is]
    D --> F[Continue iteration]
    E --> F
    F --> G{More elements?}
    G -- Yes --> B
    G -- No --> H[End]
```

## Examples:
```python
# Flatten nested lists
list(iflatten([[1, 2], [3, [4, 5]]]))  # [1, 2, 3, 4, 5]

# Preserve strings and bytes
list(iflatten(["hello", ["world"]]))  # ['hello', 'world']

# Handle mixed types
list(iflatten([1, [2, 3], "text", [4, [5, 6]]]))  # [1, 2, 3, 'text', 4, 5, 6]
```

## `parsel.utils._is_listlike` · *function*

## Summary:
Determines whether an object is list-like (iterable but excluding strings and bytes).

## Description:
This utility function identifies objects that are iterable but should not be treated as strings or bytes. It's commonly used in parsing contexts where sequences of items need to be processed, but string data should be handled separately.

## Args:
    x (Any): The object to check for list-likeness

## Returns:
    bool: True if the object is iterable and not a string or bytes type, False otherwise

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
    D --> G[End]
    E --> G
    F --> G
```

## Examples:
```python
# Returns True for lists
_is_listlike([1, 2, 3])  # True

# Returns True for tuples  
_is_listlike((1, 2, 3))  # True

# Returns False for strings
_is_listlike("hello")  # False

# Returns False for bytes
_is_listlike(b"hello")  # False

# Returns False for integers
_is_listlike(42)  # False
```

## `parsel.utils.extract_regex` · *function*

## Summary:
Extracts text matches from input text using regular expressions, with optional HTML entity decoding.

## Description:
The `extract_regex` function provides a flexible way to extract text patterns from input text using regular expressions. It supports both string and compiled regex patterns, and offers automatic HTML entity decoding for extracted results. The function is particularly useful in web scraping and data extraction workflows where structured text parsing is required.

This function was extracted from inline usage patterns to provide a reusable utility for consistent regex-based text extraction with standardized post-processing. The separation allows for consistent handling of regex matching and entity replacement across different parts of the application.

## Args:
    regex (Union[str, Pattern[str]]): Either a regular expression pattern string or a compiled regex Pattern object. When a string is provided, it gets compiled with UNICODE flag.
    text (str): The input text string to search for matches.
    replace_entities (bool): Flag indicating whether to decode HTML entities in extracted results. Defaults to True.

## Returns:
    List[str]: A list of extracted strings. When the regex contains a named group called "extract", only that group's content is returned. Otherwise, all matches from findall() are returned. Empty list is returned when no matches are found.

## Raises:
    None explicitly raised, though underlying regex operations may raise exceptions from re module.

## Constraints:
    Preconditions: 
    - The `text` parameter must be a string
    - The `regex` parameter must be either a string or compiled Pattern object
    - The `replace_entities` parameter must be a boolean
    
    Postconditions:
    - Returns a list of strings (empty list if no matches)
    - If `replace_entities=True`, HTML entities in results are decoded (except "lt" and "amp")

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input regex and text] --> B{Is regex string?}
    B -->|Yes| C[Compile regex with UNICODE flag]
    B -->|No| D[Use regex directly]
    C --> E{Is "extract" group in regex?}
    D --> E
    E -->|Yes| F[Try regex.search()]
    E -->|No| G[Use regex.findall()]
    F --> H{AttributeError?}
    H -->|Yes| I[Set strings = []]
    H -->|No| J[Get "extract" group]
    J --> K{extracted is None?}
    K -->|Yes| L[Set strings = []]
    K -->|No| M[Set strings = [extracted]]
    G --> N[Set strings = regex.findall()]
    N --> O[Flatten strings]
    O --> P{replace_entities=False?}
    P -->|Yes| Q[Return strings]
    P -->|No| R[Apply w3lib_replace_entities to each string]
    R --> Q
```

## Examples:
```python
# Basic usage with string regex
result = extract_regex(r'\d+', 'Price: $123')
# Returns: ['123']

# Using named group "extract"
result = extract_regex(r'Price: (?P<extract>\$\d+)', 'Price: $123')
# Returns: ['$123']

# With entity replacement disabled
result = extract_regex(r'&(\w+);', '&lt;tag&gt;', replace_entities=False)
# Returns: ['lt']

# No matches
result = extract_regex(r'xyz', 'abc')
# Returns: []
```

## `parsel.utils.shorten` · *function*

## Summary:
Truncates a text string to a specified width while preserving a suffix at the end.

## Description:
This function shortens a text string to fit within a specified width by removing characters from the end and appending a suffix. It handles various edge cases including when the text is already shorter than the width, when the width is too small for the suffix, and when negative widths are provided.

## Args:
    text (str): The input text string to be truncated.
    width (int): Maximum allowed length of the returned string (including suffix).
    suffix (str): String to append at the end when truncation occurs. Defaults to "...".

## Returns:
    str: The truncated text with suffix appended if truncation occurred, otherwise the original text.

## Raises:
    ValueError: When width is less than 0.

## Constraints:
    Preconditions:
        - text must be a string
        - width must be a non-negative integer
        - suffix must be a string
    Postconditions:
        - Returned string length will be less than or equal to width
        - If truncation occurs, suffix will be appended to the result

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[shorten(text, width, suffix)] --> B{len(text) <= width?}
    B -- Yes --> C[return text]
    B -- No --> D{width > len(suffix)?}
    D -- Yes --> E[return text[:width-len(suffix)] + suffix]
    D -- No --> F{width >= 0?}
    F -- Yes --> G[return suffix[len(suffix)-width:]]
    F -- No --> H[raise ValueError]
```

## Examples:
    >>> shorten("Hello World", 8)
    'Hello...'
    
    >>> shorten("Hello World", 11)
    'Hello World'
    
    >>> shorten("Hello World", 5, "!!!")
    'Hell!!!'
    
    >>> shorten("Hello World", 3, "!!!")
    '!!!'
    
    >>> shorten("Hello World", -1)
    ValueError: width must be equal or greater than 0
```

