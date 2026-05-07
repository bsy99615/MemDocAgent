# `__init__.py`

## `csvkit.convert.__init__.guess_format` · *function*

## Summary:
Guesses the file format based on the file extension, returning a standardized format identifier.

## Description:
This function analyzes a filename's extension to determine the appropriate data format. It serves as a utility for identifying file formats in data processing pipelines where automatic format detection is needed.

The function is called by the CSVKit conversion utilities when determining how to process input files without explicit format specification.

## Args:
    filename (str): The name of the file, potentially including path information

## Returns:
    str or None: Returns a standardized format identifier ('csv', 'dbf', 'fixed', 'xls', 'xlsx', 'json') when a recognized extension is found, 'fixed' when no extension is present, or None for unrecognized extensions.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions:
        - The filename parameter must be a string
        - The filename may contain path separators but should be a valid file path string
    
    Postconditions:
        - Returns one of the predefined format strings or None
        - The returned format string is always lowercase

## Side Effects:
    None: This function performs no I/O operations or external state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start guess_format] --> B{filename has extension?}
    B -- Yes --> C[Extract extension]
    C --> D{extension in ('csv','dbf','fixed','xls','xlsx')?}
    D -- Yes --> E[Return extension]
    D -- No --> F{extension in ('json','js')?}
    F -- Yes --> G[Return 'json']
    F -- No --> H[Return None]
    B -- No --> I[Return 'fixed']
```

## Examples:
    >>> guess_format("data.csv")
    'csv'
    >>> guess_format("document.json")
    'json'
    >>> guess_format("no_extension")
    'fixed'
    >>> guess_format("unknown.xyz")
    None
```

