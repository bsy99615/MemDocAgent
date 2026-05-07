# `__init__.py`

## `csvkit.convert.__init__.guess_format` · *function*

## Summary:
Guesses the file format based on the file extension, returning a standardized format identifier.

## Description:
This function analyzes a filename's extension to determine the likely file format. It handles files with and without extensions, mapping common extensions to standardized format identifiers. This logic is extracted into a separate function to provide a clean interface for format detection and to avoid duplicating the extension parsing logic throughout the codebase.

## Args:
    filename (str): The name of the file, potentially including path information

## Returns:
    str or None: Returns a standardized format identifier ('csv', 'dbf', 'fixed', 'xls', 'xlsx', 'json') when a recognized extension is found, 'fixed' when no extension is present, or None for unrecognized extensions.

## Raises:
    None: This function does not raise any exceptions

## Constraints:
    Preconditions:
        - The filename parameter must be a string
        - The filename may contain path separators but the function only examines the basename and extension
    
    Postconditions:
        - Returns one of the predefined format strings or None
        - The returned format string is always lowercase

## Side Effects:
    None: This function performs no I/O operations or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start: guess_format(filename)] --> B{filename.rfind('.')}
    B --> C{last_period == -1?}
    C -->|Yes| D[return 'fixed']
    C -->|No| E[extension = filename[last_period+1:].lower()]
    E --> F{extension in ('csv','dbf','fixed','xls','xlsx')?}
    F -->|Yes| G[return extension]
    F -->|No| H{extension in ('json','js')?}
    H -->|Yes| I[return 'json']
    H -->|No| J[return None]
```

## Examples:
    >>> guess_format("data.csv")
    'csv'
    
    >>> guess_format("document")
    'fixed'
    
    >>> guess_format("report.json")
    'json'
    
    >>> guess_format("unknown.xyz")
    None
```

