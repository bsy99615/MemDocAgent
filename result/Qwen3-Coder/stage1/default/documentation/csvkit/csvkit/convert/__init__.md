# `__init__.py`

## `csvkit.convert.__init__.guess_format` · *function*

## Summary:
Guesses the file format based on its extension, returning a standardized format identifier.

## Description:
Determines the appropriate file format identifier by examining the file extension. This function extracts the extension from a filename and maps common extensions to standard format names used internally by the csvkit conversion system.

The function is designed to handle files with and without extensions, providing sensible defaults for unknown formats. It serves as a utility for determining how to process different file types in the conversion pipeline.

## Args:
    filename (str): The name of the file, potentially including path information. Must be a string representing a valid file path or name.

## Returns:
    str or None: Returns a standardized format identifier ('csv', 'dbf', 'fixed', 'xls', 'xlsx', 'json') when a recognized extension is found. Returns 'fixed' when no extension is present. Returns None for unrecognized extensions.

## Raises:
    None: This function does not raise any exceptions under normal operation.

## Constraints:
    Preconditions:
        - The filename parameter must be a string
        - The filename may contain path separators but should represent a valid file name
    
    Postconditions:
        - Returns one of the predefined format identifiers or None
        - The returned format identifier is always lowercase
        - No side effects occur during execution

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

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
    
    >>> guess_format("spreadsheet.xlsx")
    'xlsx'
    
    >>> guess_format("unknown.xyz")
    None

