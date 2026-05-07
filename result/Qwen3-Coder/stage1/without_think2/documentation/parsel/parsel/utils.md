# `utils.py`

## `parsel.utils.flatten` · *function*

## Summary:
Converts a nested iterable structure into a flat list by recursively traversing all levels of nesting.

## Description:
The `flatten` function takes an iterable containing potentially nested structures and returns a single-level list with all elements from the nested structure in their original order. This function serves as a convenient wrapper around the `iflatten` generator function, providing eager evaluation of the flattened result.

The logic is extracted into its own function to separate the flattening algorithm from the conversion to a list, enabling lazy evaluation and allowing the flattened result to be consumed incrementally without materializing the entire result in memory at once.

## Args:
    x (Iterable[Any]): An iterable containing elements that may be scalars or nested iterables.

## Returns:
    List[Any]: A flat list containing all scalar elements from the nested structure in flattened order.

## Raises:
    None

## Constraints:
    Preconditions: The input must be an iterable.
    Postconditions: The returned list will contain all elements from the nested structure in a flattened order.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input Iterable x] --> B[Call iflatten(x)]
    B --> C[Convert Iterator to List]
    C --> D[Return Flat List]
```

## Examples:
    >>> flatten([1, [2, 3], [4, [5, 6]]])
    [1, 2, 3, 4, 5, 6]
    
    >>> flatten([[1, 2], (3, 4), "hello"])
    [1, 2, 3, 4, 'hello']
    
    >>> flatten([1, [2, [3, [4]]]])
    [1, 2, 3, 4]

## `parsel.utils.iflatten` · *function*

## Summary:
Flattens nested iterables into a single-level iterator, recursively processing nested structures while preserving scalar values.

## Description:
The `iflatten` function recursively flattens nested iterable structures (such as lists, tuples, etc.) into a single-level iterator. It processes each element in the input iterable, and if an element is itself list-like (as determined by `_is_listlike`), it recursively flattens that element. Otherwise, it yields the element as-is. This function is designed to handle arbitrarily nested structures while treating strings and bytes as scalar values rather than iterables.

This logic is extracted into its own function to separate the flattening algorithm from the conversion to a list, enabling lazy evaluation and allowing the flattened result to be consumed incrementally without materializing the entire result in memory at once.

## Args:
    x (Iterable[Any]): An iterable containing elements that may be scalars or nested iterables.

## Returns:
    Iterator[Any]: An iterator over all scalar elements from the flattened structure.

## Raises:
    None

## Constraints:
    Preconditions: The input must be an iterable.
    Postconditions: The returned iterator will yield all elements from the nested structure in a flattened order.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input Iterable x] --> B{For each element el in x}
    B --> C{Is el list-like?}
    C -- Yes --> D[Recursively flatten el using flatten()]
    C -- No --> E[Yield el as-is]
    D --> F[Yield from flatten(el)]
    F --> G[Continue to next element]
    E --> G
    G --> H{End of x?}
    H -- No --> B
    H -- Yes --> I[Stop iteration]
```

## Examples:
    >>> list(iflatten([1, [2, 3], [4, [5, 6]]]))
    [1, 2, 3, 4, 5, 6]
    
    >>> list(iflatten([[1, 2], (3, 4), "hello"]))
    [1, 2, 3, 4, 'hello']
    
    >>> list(iflatten([1, [2, [3, [4]]]]))
    [1, 2, 3, 4]

## `parsel.utils._is_listlike` · *function*

## Summary:
Determines whether a given object is iterable but not a string or bytes type.

## Description:
This utility function checks if an object supports iteration (has the `__iter__` method) while excluding string and bytes types, which are technically iterable but often treated as scalar values in many contexts.

## Args:
    x (Any): The object to check for list-like properties.

## Returns:
    bool: True if the object is iterable and not a string or bytes type; False otherwise.

## Raises:
    None

## Constraints:
    Preconditions: The input can be any Python object.
    Postconditions: The return value is always a boolean indicating the result of the check.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input x] --> B{hasattr(x, "__iter__")}?
    B -- Yes --> C{isinstance(x, (str, bytes))}?
    C -- Yes --> D[Return False]
    C -- No --> D
    B -- No --> D
    D[Return False]
```

## Examples:
    >>> _is_listlike([1, 2, 3])
    True
    >>> _is_listlike((1, 2, 3))
    True
    >>> _is_listlike("hello")
    False
    >>> _is_listlike(b"hello")
    False
    >>> _is_listlike(42)
    False
```

## `parsel.utils.extract_regex` · *function*

## Summary:
Extracts strings from text using regular expressions, with optional HTML entity decoding.

## Description:
The `extract_regex` function applies a regular expression pattern to extract substrings from input text. It supports both string and compiled regex patterns, and provides optional HTML entity decoding for the extracted results. The function handles two extraction modes: when the regex contains a group named "extract", it extracts only that specific group; otherwise, it finds all matches in the text.

This logic is extracted into its own function to encapsulate the complex interaction between regex processing, group extraction, and HTML entity handling, making the code more modular and testable.

## Args:
    regex (Union[str, Pattern[str]]): A regular expression pattern as a string or compiled Pattern object.
    text (str): The input text to search for matches.
    replace_entities (bool): Whether to decode HTML entities in extracted strings. Defaults to True.

## Returns:
    List[str]: A list of extracted strings. Returns an empty list if no matches are found or if the "extract" group is None.

## Raises:
    None

## Constraints:
    Preconditions: 
    - The `regex` parameter must be either a string or a compiled regex Pattern object.
    - The `text` parameter must be a string.
    - The `replace_entities` parameter must be a boolean.
    
    Postconditions:
    - The returned list will contain all extracted strings in the order they appear in the text.
    - If `replace_entities` is True, all HTML entities in the extracted strings will be decoded.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start extract_regex] --> B{Is regex str?}
    B -- Yes --> C[Compile regex with re.UNICODE]
    B -- No --> D[Use regex as-is]
    C --> E{Does regex have "extract" group?}
    D --> E
    E -- Yes --> F[Try regex.search(text)]
    E -- No --> G[Call regex.findall(text)]
    F --> H{AttributeError?}
    H -- Yes --> I[Set strings = []]
    H -- No --> J{extracted is None?}
    J -- Yes --> I
    J -- No --> K[Set strings = [extracted]]
    G --> L[Set strings = regex.findall(text)]
    L --> M[Call flatten(strings)]
    M --> N{replace_entities False?}
    N -- Yes --> O[Return strings]
    N -- No --> P[Apply w3lib.html.replace_entities to each string]
    P --> O
```

## Examples:
    >>> extract_regex(r'(\w+)@(\w+\.\w+)', 'Contact us at john@example.com')
    ['john@example.com']
    
    >>> extract_regex(r'(?P<extract>\w+)@(\w+\.\w+)', 'Contact us at john@example.com')
    ['john@example.com']
    
    >>> extract_regex(r'<p>(.*?)</p>', '<p>Hello &amp; welcome</p>')
    ['Hello & welcome']

## `parsel.utils.shorten` · *function*

## Summary:
Truncates a string to a specified width while preserving readability by appending a suffix.

## Description:
This function shortens text to fit within a given character width by removing excess characters from the end and appending a suffix. It is commonly used for displaying truncated content in user interfaces or logs where space is limited.

## Args:
    text (str): The input string to be shortened.
    width (int): Maximum allowed length of the returned string including the suffix.
    suffix (str): String to append when truncating. Defaults to "...".

## Returns:
    str: The truncated string with suffix appended if text was shortened, otherwise the original text.

## Raises:
    ValueError: When width is negative.

## Constraints:
    Preconditions:
        - text must be a string
        - width must be non-negative
        - suffix must be a string
    Postconditions:
        - Returned string length will not exceed width
        - If text was truncated, suffix will be appended
        - Original text is returned unchanged if it fits within width

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[shorten] --> B{len(text) <= width?}
    B -- Yes --> C[Return text]
    B -- No --> D{width > len(suffix)?}
    D -- Yes --> E[Return text[:width-len(suffix)] + suffix]
    D -- No --> F{width >= 0?}
    F -- Yes --> G[Return suffix[len(suffix)-width:]]
    F -- No --> H[raise ValueError]
```

## Examples:
    >>> shorten("Hello World", 5)
    'Hello...'
    
    >>> shorten("Short", 10)
    'Short'
    
    >>> shorten("Very long text", 8, "...")
    'Very l...'
    
    >>> shorten("Test", 0)
    '...'
    
    >>> shorten("Test", -1)
    Traceback (most recent call last):
        ...
    ValueError: width must be equal or greater than 0

