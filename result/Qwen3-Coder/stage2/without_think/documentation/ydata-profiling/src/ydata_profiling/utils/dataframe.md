# `dataframe.py`

## `src.ydata_profiling.utils.dataframe.warn_read` · *function*

## Summary:
Issues a warning message through Python's warnings module for a given file extension.

## Description:
This function serves as a centralized warning mechanism for file reading operations. It accepts a file extension parameter and issues an appropriate warning message through Python's warnings module. The function is typically used to alert users about potential issues, deprecations, or compatibility concerns when working with specific file formats.

## Args:
    extension (str): The file extension (including the leading dot) for which a warning should be issued.

## Returns:
    None: This function does not return any value.

## Raises:
    None: This function does not raise any exceptions directly.

## Constraints:
    Preconditions:
    - The extension parameter must be a string representing a file extension
    - The extension should include the leading dot character (e.g., '.csv', '.xlsx')
    
    Postconditions:
    - A warning message is issued via Python's warnings module
    - No other state changes occur

## Side Effects:
    - Issues a warning message to Python's warnings module
    - May result in console output if warnings are configured to be displayed

## Control Flow:
```mermaid
flowchart TD
    A[warn_read called] --> B{extension provided}
    B -->|Valid string| C[Call warnings.warn()]
    C --> D[Return None]
```

## Examples:
```python
# Issue warning for CSV files
warn_read('.csv')

# Issue warning for Excel files  
warn_read('.xlsx')
```

## `src.ydata_profiling.utils.dataframe.is_supported_compression` · *function*

## Summary:
Determines whether a given file extension corresponds to a supported compression format.

## Description:
This utility function validates if a file extension represents one of the commonly supported compression formats (.bz2, .gz, .xz, .zip). It performs a case-insensitive comparison by converting the input to lowercase before checking against the list of supported extensions.

## Args:
    file_extension (str): The file extension to validate, including the leading dot (e.g., ".gz", ".zip"). May be in any case.

## Returns:
    bool: True if the file extension is one of the supported compression formats (.bz2, .gz, .xz, .zip), False otherwise.

## Raises:
    None: This function does not raise any exceptions under normal operation.

## Constraints:
    Preconditions:
    - The input file_extension parameter must be a string
    - The function assumes the input contains a valid file extension format (with or without leading dot)
    
    Postconditions:
    - The function always returns a boolean value (True or False)
    - The comparison is case-insensitive due to the .lower() conversion

## Side Effects:
    None: This function has no side effects. It only performs string operations and comparisons.

## Control Flow:
```mermaid
flowchart TD
    A[Input file_extension] --> B{file_extension.lower() in [".bz2",".gz",".xz",".zip"]}
    B -->|True| C[Return True]
    B -->|False| D[Return False]
```

## Examples:
    >>> is_supported_compression(".gz")
    True
    >>> is_supported_compression(".GZ")
    True
    >>> is_supported_compression(".txt")
    False
    >>> is_supported_compression(".bz2")
    True
    >>> is_supported_compression(".xz")
    True
    >>> is_supported_compression(".zip")
    True
```

## `src.ydata_profiling.utils.dataframe.remove_suffix` · *function*

## Summary:
Removes a specified suffix from the end of a string if present.

## Description:
This utility function safely removes a suffix from a string by checking if the string ends with the specified suffix. It is designed to handle edge cases gracefully without raising exceptions.

## Args:
    text (str): The input string from which to remove the suffix
    suffix (str): The suffix to remove from the end of the text

## Returns:
    str: The text with the suffix removed if it was present at the end, otherwise returns the original text unchanged

## Raises:
    None: This function does not raise any exceptions

## Constraints:
    Preconditions:
        - Both `text` and `suffix` should be strings
        - The function handles empty strings gracefully
    
    Postconditions:
        - If the suffix is empty or the text doesn't end with the suffix, the original text is returned unchanged
        - If the suffix is present at the end, it is completely removed from the text

## Side Effects:
    None: This function has no side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start remove_suffix] --> B{suffix is empty?}
    B -- Yes --> C[Return text]
    B -- No --> D{text ends with suffix?}
    D -- Yes --> E[Return text without suffix]
    D -- No --> F[Return text]
```

## Examples:
    >>> remove_suffix("hello.txt", ".txt")
    'hello'
    
    >>> remove_suffix("document.pdf", ".txt")
    'document.pdf'
    
    >>> remove_suffix("test", "")
    'test'
    
    >>> remove_suffix("", ".txt")
    ''
```

## `src.ydata_profiling.utils.dataframe.uncompressed_extension` · *function*

## Summary:
Extracts the true file extension from a filename, accounting for compressed files by removing compression suffixes.

## Description:
This utility function determines the actual file extension of a file by stripping away compression suffixes such as .gz, .bz2, .xz, or .zip. When a file has a compression extension, the function returns the extension of the underlying file (e.g., for "archive.tar.gz", it returns ".tar"). For uncompressed files, it simply returns the file's extension.

The function is designed to handle nested compression formats properly by recursively removing compression extensions until the base file extension is reached.

## Args:
    file_name (Path): A pathlib.Path object representing the full path to a file

## Returns:
    str: The true file extension (including the leading dot) after removing compression suffixes. For example:
        - ".txt" for "document.txt"
        - ".tar" for "archive.tar.gz"
        - ".pdf" for "report.pdf.gz"

## Raises:
    None: This function does not raise any exceptions under normal operation.

## Constraints:
    Preconditions:
        - The input file_name must be a valid pathlib.Path object
        - The file_name should represent a valid file path
        
    Postconditions:
        - The returned string always includes a leading dot
        - The returned extension represents the actual file type after decompression
        - The function handles edge cases like empty paths gracefully

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start uncompressed_extension] --> B[Get file extension with .suffix.lower()]
    B --> C{Is extension supported compression?}
    C -->|Yes| D[Remove extension from file name]
    D --> E[Get new extension from remaining file name]
    C -->|No| F[Return original extension]
    E --> G[Return new extension]
    F --> G
```

## Examples:
    >>> from pathlib import Path
    >>> uncompressed_extension(Path("document.txt"))
    '.txt'
    
    >>> uncompressed_extension(Path("archive.tar.gz"))
    '.tar'
    
    >>> uncompressed_extension(Path("data.csv.bz2"))
    '.csv'
    
    >>> uncompressed_extension(Path("report.pdf"))
    '.pdf'
```

## `src.ydata_profiling.utils.dataframe.read_pandas` · *function*

## Summary:
Reads data files of various formats into a pandas DataFrame based on file extension.

## Description:
This function provides a unified interface for reading data files into pandas DataFrames, automatically detecting the appropriate reading method based on the file extension. It supports numerous file formats including CSV, JSON, Excel, Parquet, Pickle, and various statistical formats while handling compressed files appropriately.

The function delegates to specific pandas reading methods based on file extensions, with special handling for compressed files through the `uncompressed_extension` utility. When encountering unsupported extensions, it falls back to CSV reading with a warning.

## Args:
    file_name (Path): A pathlib.Path object representing the full path to the data file to be read

## Returns:
    pd.DataFrame: A pandas DataFrame containing the data from the specified file

## Raises:
    ValueError: Raised when attempting to read a tar-compressed file directly, as pandas doesn't support it natively

## Constraints:
    Preconditions:
        - The file_name parameter must be a valid pathlib.Path object pointing to an existing file
        - The file must be readable and contain valid data for the specified format
        
    Postconditions:
        - Returns a valid pandas DataFrame object
        - For compressed files, the underlying file extension is used to determine the reading method
        - If a warning is issued, it occurs before attempting to read the file

## Side Effects:
    - May issue warnings through Python's warnings module for unsupported or deprecated file formats
    - Performs file I/O operations to read the data file
    - May trigger pandas-specific warnings or errors during file reading

## Control Flow:
```mermaid
flowchart TD
    A[read_pandas called] --> B[Get file extension with uncompressed_extension]
    B --> C{Extension matches known format?}
    C -->|Yes| D[Use appropriate pandas reader]
    C -->|No| E[Check if not CSV]
    E -->|Yes| F[Issue warning with warn_read]
    F --> G[Use pd.read_csv]
    D --> H[Return DataFrame]
    G --> H
```

## Examples:
    >>> from pathlib import Path
    >>> import pandas as pd
    
    # Reading a CSV file
    >>> df = read_pandas(Path("data.csv"))
    
    # Reading a JSON file
    >>> df = read_pandas(Path("data.json"))
    
    # Reading a compressed file (will detect .gz and read underlying format)
    >>> df = read_pandas(Path("data.csv.gz"))
    
    # Reading an Excel file
    >>> df = read_pandas(Path("data.xlsx"))
    
    # Reading a Parquet file
    >>> df = read_pandas(Path("data.parquet"))
```

## `src.ydata_profiling.utils.dataframe.rename_index` · *function*

## Summary:
Renames columns and index levels named "index" to "df_index" to avoid naming conflicts.

## Description:
This function standardizes column and index names by replacing any occurrence of "index" with "df_index". This prevents conflicts with pandas' built-in index naming conventions and ensures consistent naming throughout the profiling process. The function modifies the DataFrame in-place and returns the updated DataFrame.

## Args:
    df (pandas.DataFrame): Input pandas DataFrame whose columns and index names may contain "index"

## Returns:
    pandas.DataFrame: The same DataFrame with columns and index levels named "index" renamed to "df_index"

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a pandas DataFrame
    - DataFrame must be valid and not None
    
    Postconditions:
    - All columns named "index" are renamed to "df_index"
    - All index levels named "index" are renamed to "df_index"
    - Original DataFrame object is modified in-place

## Side Effects:
    - Modifies the input DataFrame in-place by changing column names and index names
    - No external I/O operations or state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start rename_index] --> B{Column "index" exists?}
    B -- Yes --> C[Rename columns {"index":"df_index"}]
    C --> D{Index name "index" exists?}
    D -- Yes --> E[Update index names]
    E --> F[Return DataFrame]
    D -- No --> F
    B -- No --> F
```

## Examples:
```python
import pandas as pd

# Example 1: DataFrame with index column
df = pd.DataFrame({'index': [1, 2, 3], 'value': [4, 5, 6]})
result = rename_index(df)
# result.columns will be ['df_index', 'value']

# Example 2: DataFrame with index level named "index"
df = pd.DataFrame({'value': [4, 5, 6]})
df.index.names = ['index']
result = rename_index(df)
# result.index.names will be ['df_index']

# Example 3: DataFrame with both column and index named "index"
df = pd.DataFrame({'index': [1, 2, 3]})
df.index.names = ['index']
result = rename_index(df)
# result.columns will be ['df_index'] 
# result.index.names will be ['df_index']
```

## `src.ydata_profiling.utils.dataframe.expand_mixed` · *function*

## Summary:
Expands DataFrame columns containing list, dict, or tuple values into separate columns, recursively processing nested structures.

## Description:
This function transforms DataFrame columns that contain list, dict, or tuple values into multiple separate columns. It identifies columns where all non-null entries are of the specified container types and not nested, then expands these entries into individual columns with prefixed names. The expansion process is recursive, allowing for multi-level expansion of nested structures.

## Args:
    df (pd.DataFrame): Input DataFrame to process
    types (Any, optional): List of types to consider for expansion. Defaults to [list, dict, tuple].

## Returns:
    pd.DataFrame: DataFrame with container-type columns expanded into multiple columns

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a pandas DataFrame
    - Column values must be compatible with type checking operations
    
    Postconditions:
    - Columns containing list, dict, or tuple values are replaced with expanded columns
    - Non-container columns remain unchanged
    - Recursive processing handles nested structures

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start expand_mixed] --> B{types is None?}
    B -- Yes --> C[Set types = [list, dict, tuple]]
    B -- No --> C
    C --> D[For each column in df]
    D --> E{non_nested_enumeration.all()?}
    E -- No --> F[Continue to next column]
    E -- Yes --> G[Get non-null values]
    G --> H[Convert to DataFrame]
    H --> I[Add prefix to column names]
    I --> J[Recursively call expand_mixed]
    J --> K[Drop original column]
    K --> L[Concatenate expanded columns]
    L --> M[Return modified DataFrame]
```

## Examples:
```python
import pandas as pd

# Basic usage
df = pd.DataFrame({
    'id': [1, 2, 3],
    'values': [[1, 2], [3, 4], [5, 6]]
})
expanded_df = expand_mixed(df)
# Result: columns 'id' and 'values_0', 'values_1'

# With custom types
df = pd.DataFrame({
    'id': [1, 2],
    'custom': [{'a': 1}, {'b': 2}]
})
expanded_df = expand_mixed(df, types=[dict])
# Result: columns 'id' and 'custom_a', 'custom_b'
```

## `src.ydata_profiling.utils.dataframe.hash_dataframe` · *function*

## Summary:
Creates a SHA256 hash of a pandas DataFrame for unique identification purposes.

## Description:
Generates a deterministic hash value for a pandas DataFrame by computing individual row hashes using pandas' internal hashing mechanism, concatenating these hashes with newlines, and then computing a SHA256 digest of the concatenated string. The resulting hash is prefixed with a constant prefix (HASH_PREFIX) to distinguish it from raw hashes.

This function is typically used for caching, comparison, or identifying DataFrame instances without storing the full data. It is part of the ydata-profiling utility module for data processing operations.

## Args:
    df (pandas.DataFrame): Input pandas DataFrame to be hashed

## Returns:
    str: SHA256 hash of the DataFrame prefixed with HASH_PREFIX constant

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - Input must be a valid pandas DataFrame
    - All data in the DataFrame must be hashable by pandas' internal hashing mechanism
    
    Postconditions:
    - Returns a string with format "{HASH_PREFIX}{sha256_hash}"
    - Same input DataFrame will always produce the same hash output

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start hash_dataframe] --> B[Get hash_pandas_object(df)]
    B --> C[Extract hash values as strings]
    C --> D[Join with newline separator]
    D --> E[Encode as UTF-8]
    E --> F[Compute SHA256 digest]
    F --> G[Prepend HASH_PREFIX]
    G --> H[Return result]
```

## Examples:
    # Basic usage
    import pandas as pd
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    hash_result = hash_dataframe(df)
    # Returns something like "hash_abc123def456..."
    
    # Same DataFrame always produces same hash
    df2 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    assert hash_dataframe(df) == hash_dataframe(df2)
```

## `src.ydata_profiling.utils.dataframe.slugify` · *function*

## Summary:
Converts a string into a URL-friendly slug by normalizing unicode characters, removing special characters, and standardizing whitespace.

## Description:
Transforms arbitrary strings into safe, lowercase identifiers suitable for URLs or file names. The function handles Unicode normalization differently based on the allow_unicode parameter, removes invalid characters, and ensures consistent hyphen-separated output.

## Args:
    value (str): Input string to convert into a slug
    allow_unicode (bool): When True, preserves Unicode characters using NFKC normalization; when False, strips Unicode characters using ASCII conversion (default: False)

## Returns:
    str: A URL-safe slug containing only lowercase letters, numbers, hyphens, and underscores, with no leading/trailing hyphens or underscores

## Raises:
    None explicitly raised

## Constraints:
    Precondition: Input value must be convertible to string
    Postcondition: Output is always a valid string with URL-safe characters only

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input value] --> B{allow_unicode}
    B -- True --> C[Normalize NFKC]
    B -- False --> D[Normalize NFKD]
    D --> E[Encode to ASCII, ignore non-ASCII]
    E --> F[Decode back to ASCII]
    C --> F
    F --> G[Convert to lowercase]
    G --> H[Remove special chars [^\\w\\s-]]
    H --> I[Replace [-\\s]+ with -]
    I --> J[Strip leading/trailing -_]
    J --> K[Return slug]
```

## Examples:
    >>> slugify("Hello World!")
    'hello-world'
    
    >>> slugify("Café & Restaurant")
    'cafe-restaurant'
    
    >>> slugify("Café & Restaurant", allow_unicode=True)
    'café-&-restaurant'
    
    >>> slugify("  Multiple   Spaces  ")
    'multiple-spaces'
    
    >>> slugify("Special@#$%Characters")
    'specialcharacters'

## `src.ydata_profiling.utils.dataframe.sort_column_names` · *function*

## Summary:
Sorts dictionary items by their keys in either ascending or descending order, case-insensitively.

## Description:
This utility function provides a standardized way to sort dictionary items representing column names. It accepts a dictionary mapping column names to their properties and sorts them according to the specified order. The sorting is performed case-insensitively to ensure consistent ordering regardless of letter casing.

The function is designed to be used in data profiling contexts where column ordering needs to be controlled for reproducible results or consistent presentation.

## Args:
    dct (dict): Dictionary containing column names as keys and their properties as values
    sort (Optional[str]): Sorting direction - "ascending", "descending", or None. If None, the dictionary is returned unchanged.

## Returns:
    dict: A new dictionary with sorted keys. If sort is None, returns the original dictionary unchanged.

## Raises:
    ValueError: When the sort parameter is not None, "ascending", or "descending".

## Constraints:
    Preconditions:
        - The input dictionary should have string keys
        - The sort parameter should be None, "ascending", "descending", or a string starting with "asc" or "desc"
    Postconditions:
        - The returned dictionary maintains the same key-value pairs as the input
        - Keys in the returned dictionary are sorted alphabetically (case-insensitive)
        - If sort is None, the original dictionary reference is returned (though this depends on implementation details)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[sort_column_names] --> B{sort is None?}
    B -- Yes --> C[Return dct]
    B -- No --> D[sort = sort.lower()]
    D --> E{sort starts with "asc"?}
    E -- Yes --> F[Sort dct ascending by key.casefold()]
    E -- No --> G{sort starts with "desc"?}
    G -- Yes --> H[Sort dct descending by key.casefold()]
    G -- No --> I[raise ValueError]
    F --> J[Return sorted dct]
    H --> J
    I --> J
```

## Examples:
```python
# Basic usage with ascending sort
columns = {"z": "int", "a": "str", "B": "float"}
sorted_asc = sort_column_names(columns, "ascending")
# Result: {"a": "str", "B": "float", "z": "int"}

# Basic usage with descending sort
sorted_desc = sort_column_names(columns, "descending")
# Result: {"z": "int", "B": "float", "a": "str"}

# No sorting (None)
no_sort = sort_column_names(columns, None)
# Result: {"z": "int", "a": "str", "B": "float"} (same as input)
```

