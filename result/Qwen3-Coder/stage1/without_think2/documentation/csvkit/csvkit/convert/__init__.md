# `__init__.py`

## `csvkit.convert.__init__.guess_format` · *function*

## Summary:
Guesses the data format of a file based on its filename extension.

## Description:
This function determines the likely data format of a file by examining its extension. It is designed to support various data formats commonly used in data processing workflows. The function is typically called during file import operations when the format needs to be inferred automatically.

## Args:
    filename (str): The name of the file, including its extension.

## Returns:
    str or None: Returns the guessed format as a string ('csv', 'dbf', 'fixed', 'xls', 'xlsx', 'json') or None if the extension is unrecognized.

## Raises:
    None

## Constraints:
    Precondition: The filename argument must be a string.
    Postcondition: The returned value will be one of the supported format strings or None.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start guess_format] --> B{filename has extension?}
    B -- No --> C[Return 'fixed']
    B -- Yes --> D[Extract extension]
    D --> E{extension in ('csv','dbf','fixed','xls','xlsx')?}
    E -- Yes --> F[Return extension]
    E -- No --> G{extension in ('json','js')?}
    G -- Yes --> H[Return 'json']
    G -- No --> I[Return None]
```

## Examples:
    >>> guess_format("data.csv")
    'csv'
    >>> guess_format("document.txt")
    None
    >>> guess_format("report.fixed")
    'fixed'
    >>> guess_format("data.json")
    'json'
    >>> guess_format("data.js")
    'json'
    >>> guess_format("data")
    'fixed'
```

