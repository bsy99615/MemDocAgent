# `utils.py`

## `parsel.utils.flatten` · *function*

## Summary:
Converts a nested iterable structure into a flat list by recursively expanding list-like objects while preserving scalar values.

## Description:
This function provides a convenient way to flatten nested iterable structures into a single-level list. It leverages the `iflatten` generator function to process the input and convert the resulting iterator into a concrete list. The function handles nested structures of arbitrary depth, treating list-like objects (lists, tuples, etc.) as containers to be expanded while preserving scalar values such as strings and numbers.

The extraction of flattening logic into separate `iflatten` and `flatten` functions allows for flexibility in usage - the generator version can be used when memory efficiency is important, while the list version provides immediate access to all flattened elements.

## Args:
    x (Iterable[Any]): An iterable containing potentially nested list-like objects and scalar values

## Returns:
    List[Any]: A flat list containing all elements from the nested structure, with all list-like objects recursively expanded

## Raises:
    None

## Constraints:
    Preconditions: Input must be iterable
    Postconditions: All nested list-like structures are flattened into a single sequence of elements

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start flatten(x)] --> B[Call iflatten(x)]
    B --> C[Get iterator from iflatten]
    C --> D[Convert iterator to list]
    D --> E[Return flattened list]
```

## Examples:
    >>> flatten([1, [2, 3], 4])
    [1, 2, 3, 4]
    
    >>> flatten([[1, 2], [3, [4, 5]]])
    [1, 2, 3, 4, 5]
    
    >>> flatten(["hello", ["world", "!"]])
    ['hello', 'world', '!']
    
    >>> flatten([1, [2, [3, [4]]], 5])
    [1, 2, 3, 4, 5]
```

## `parsel.utils.iflatten` · *function*

## Summary:
Generates flattened elements from a nested iterable structure, recursively expanding list-like objects while preserving scalar values.

## Description:
This generator function processes an iterable and recursively flattens nested list-like structures. It distinguishes between list-like objects (such as lists, tuples, and other iterables) and scalar values (including strings and bytes). When encountering a list-like element, it recursively flattens that element; otherwise, it yields the element as-is. This approach prevents strings and bytes from being treated as iterables of individual characters.

The function is designed to work in conjunction with the `_is_listlike` helper function to identify appropriate elements for flattening, and it relies on the `flatten` function for recursive processing of nested structures.

## Args:
    x (Iterable[Any]): An iterable containing potentially nested list-like objects and scalar values

## Returns:
    Iterator[Any]: A generator yielding individual elements from the flattened structure

## Raises:
    None

## Constraints:
    Preconditions: Input must be iterable
    Postconditions: All nested list-like structures are flattened into a single sequence of elements

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start iflatten(x)] --> B{Iterate through elements}
    B --> C{Element is list-like?}
    C -- Yes --> D[Recursively flatten(element)]
    D --> E[Yield flattened elements]
    C -- No --> F[Yield element as-is]
    E --> G[Continue iteration]
    F --> G
    G --> H{More elements?}
    H -- Yes --> B
    H -- No --> I[End generator]
```

## Examples:
    >>> list(iflatten([1, [2, 3], 4]))
    [1, 2, 3, 4]
    
    >>> list(iflatten([[1, 2], [3, [4, 5]]]))
    [1, 2, 3, 4, 5]
    
    >>> list(iflatten(["hello", ["world", "!"]]))
    ['hello', 'world', '!']
    
    >>> list(iflatten([1, [2, [3, [4]]], 5]))
    [1, 2, 3, 4, 5]
```

## `parsel.utils._is_listlike` · *function*

## Summary:
Determines whether an object should be treated as a list-like iterable, excluding strings and bytes.

## Description:
This utility function identifies objects that are iterable but should not be treated as strings or bytes. It's commonly used in parsing contexts where you want to iterate over collections but avoid treating text as individual characters.

## Args:
    x (Any): The object to check for list-like properties

## Returns:
    bool: True if the object has an `__iter__` attribute and is not an instance of str or bytes; False otherwise

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
Extracts strings from text using regular expressions, with optional HTML entity processing.

## Description:
The `extract_regex` function provides a flexible way to extract text patterns from input text using regular expressions. It supports both string and compiled regex patterns, and offers optional processing of HTML entities in the extracted results. The function handles two distinct extraction modes: when the regex contains a named group called "extract", it extracts only that specific group; otherwise, it finds all matches using findall.

## Args:
    regex (Union[str, Pattern[str]]): Either a regular expression pattern string or a compiled regex object. When a string is provided, it gets compiled with UNICODE flag.
    text (str): The input text to search for matches.
    replace_entities (bool): If True (default), HTML entities in extracted strings are processed using w3lib.html.replace_entities. If False, raw strings are returned without entity processing.

## Returns:
    List[str]: A list of extracted strings. When the regex contains a named group "extract":
               - Returns a list with one element if the group matches and is not None
               - Returns an empty list if no match is found or the group is None
               When the regex does not contain a named group "extract":
               - Returns all matches found by findall() as a flat list of strings

## Raises:
    None explicitly raised, though underlying regex operations may raise exceptions.

## Constraints:
    Preconditions: 
    - The `text` parameter must be a string
    - The `regex` parameter must be either a string or compiled regex pattern
    - The `replace_entities` parameter must be a boolean
    
    Postconditions:
    - Always returns a list of strings
    - If "extract" group is present in regex, result contains at most one element
    - If "extract" group is not present, result contains all matches from findall()

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start extract_regex] --> B{Is regex string?}
    B -->|Yes| C[Compile regex with re.UNICODE]
    B -->|No| D[Use regex directly]
    C --> E{Is "extract" in groupindex?}
    D --> E
    E -->|Yes| F[Try regex.search(text)]
    E -->|No| G[Use regex.findall(text)]
    F --> H{AttributeError?}
    H -->|Yes| I[Set strings = []]
    H -->|No| J[Extract group("extract")]
    J --> K{extracted is None?}
    K -->|Yes| L[Set strings = []]
    K -->|No| M[Set strings = [extracted]]
    G --> N[Set strings = regex.findall(text)]
    N --> O[Flatten strings]
    O --> P{replace_entities is False?}
    P -->|Yes| Q[Return strings]
    P -->|No| R[Process HTML entities]
    R --> S[Return processed strings]
```

## Examples:
    >>> extract_regex(r'(\w+)@(\w+\.\w+)', 'Contact us at john@example.com')
    ['john@example.com']
    
    >>> extract_regex(r'(?P<extract>\w+)@(\w+\.\w+)', 'Contact us at john@example.com')
    ['john']
    
    >>> extract_regex(r'\d+', 'Price: $100 and tax: $20')
    ['100', '20']
    
    >>> extract_regex(r'(?P<extract>\w+)', 'Hello world')
    ['Hello']  # Extracts only the first word due to the named group
    
    >>> extract_regex(r'(?P<extract>\w+)', 'No match here')
    []  # Returns empty list when no match is found
```

## `parsel.utils.shorten` · *function*

## Summary:
Truncates text to a specified width while preserving a suffix, returning either the original text or a shortened version with the suffix appended.

## Description:
This function is used to limit the length of text strings to a specified maximum width. When the text exceeds the width limit, it truncates the text and appends a suffix to indicate truncation. This is commonly used for displaying long text in constrained UI spaces or generating summaries.

The function was extracted into its own utility to provide consistent text truncation behavior across the codebase, separating the logic of text manipulation from business logic that might use it.

## Args:
    text (str): The input text to be truncated
    width (int): Maximum allowed length of the returned string (excluding suffix)
    suffix (str): String to append when text is truncated. Defaults to "..."

## Returns:
    str: Either the original text if it fits within the width, or a truncated version with suffix appended

## Raises:
    ValueError: When width is negative

## Constraints:
    Preconditions:
    - text must be a string
    - width must be a non-negative integer
    - suffix must be a string
    
    Postconditions:
    - Returned string length will be <= width + len(suffix)
    - If text is shorter than or equal to width, original text is returned unchanged

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{len(text) <= width?}
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
    
    >>> shorten("Very long text", 8, "...")
    'Very lo...'
    
    >>> shorten("Test", 0, "...")
    '...'
    
    >>> shorten("Test", -1)
    ValueError: width must be equal or greater than 0
```

