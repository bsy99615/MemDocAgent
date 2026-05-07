# `__init__.py`

## `csvkit.convert.__init__.guess_format` · *function*

## Summary:
Guesses the file format based on the file extension, returning a standardized format identifier.

## Description:
Attempts to determine a file's format by examining its extension. This function extracts the extension from a filename and maps it to a recognized format identifier. When no extension is present, it defaults to assuming fixed-width format.

## Args:
    filename (str): The name of the file, potentially including path information.

## Returns:
    str or None: Returns a format identifier string such as 'csv', 'json', 'fixed', 'xls', 'xlsx', 'dbf' if the extension matches known formats. Returns 'fixed' if no extension is present. Returns None if the extension doesn't match any known formats.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions:
        - The filename parameter must be a string
    Postconditions:
        - Returns one of the predefined format identifiers or None
        - The returned string is always lowercase

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start guess_format] --> B{Has extension?}
    B -- No --> C[Return 'fixed']
    B -- Yes --> D[Extract extension]
    D --> E{Extension in ('csv','dbf','fixed','xls','xlsx')?}
    E -- Yes --> F[Return extension]
    E -- No --> G{Extension in ('json','js')?}
    G -- Yes --> H[Return 'json']
    G -- No --> I[Return None]
```

## Examples:
    >>> guess_format("data.csv")
    'csv'
    >>> guess_format("document.json")
    'json'
    >>> guess_format("report")
    'fixed'
    >>> guess_format("file.unknown")
    None
```

