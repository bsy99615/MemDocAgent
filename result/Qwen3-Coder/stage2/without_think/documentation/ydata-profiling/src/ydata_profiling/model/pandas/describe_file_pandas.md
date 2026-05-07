# `describe_file_pandas.py`

## `src.ydata_profiling.model.pandas.describe_file_pandas.file_summary` · *function*

## Summary
Extracts and formats file system metadata (size and timestamps) for a series of file paths.

## Description
Processes a pandas Series containing file paths to compute and format file system statistics including file size and creation/access/modification timestamps. This function isolates file metadata extraction logic to enable reuse in profiling workflows while maintaining clean separation between file system operations and data analysis.

## Args
    series (pandas.Series): A pandas Series containing file paths as strings

## Returns
    dict: A dictionary containing four keys:
        - "file_size": pandas.Series with file sizes in bytes
        - "file_created_time": pandas.Series with creation timestamps formatted as "%Y-%m-%d %H:%M:%S"
        - "file_accessed_time": pandas.Series with last access timestamps formatted as "%Y-%m-%d %H:%M:%S"
        - "file_modified_time": pandas.Series with last modification timestamps formatted as "%Y-%m-%d %H:%M:%S"

## Raises
    FileNotFoundError: When any file path in the series does not exist
    PermissionError: When access to a file path is denied
    OSError: When system-level errors occur during file stat operations

## Constraints
    Preconditions:
        - Input series must contain valid file paths as strings
        - Files must be accessible for stat operations
    Postconditions:
        - All returned Series have the same length as the input series
        - Timestamps are consistently formatted as "%Y-%m-%d %H:%M:%S"

## Side Effects
    - Performs file system operations (os.stat) for each file path in the input series
    - May trigger file system I/O errors if files don't exist or aren't accessible

## Control Flow
```mermaid
flowchart TD
    A[Input Series of file paths] --> B{For each path}
    B --> C[os.stat(path) to get file stats]
    C --> D[Extract st_size, st_ctime, st_atime, st_mtime]
    D --> E[Format timestamps with convert_datetime]
    E --> F[Return summary dictionary]
```

## Examples
```python
import pandas as pd
from src.ydata_profiling.model.pandas.describe_file_pandas import file_summary

# Basic usage
file_paths = pd.Series(['/path/to/file1.txt', '/path/to/file2.txt'])
summary = file_summary(file_paths)
print(summary['file_size'])  # Series with file sizes
print(summary['file_created_time'])  # Series with formatted creation times

# Error handling example
try:
    summary = file_summary(pd.Series(['/nonexistent/file.txt']))
except (FileNotFoundError, PermissionError) as e:
    print(f"Error accessing files: {e}")
```

## `src.ydata_profiling.model.pandas.describe_file_pandas.pandas_describe_file_1d` · *function*

## Summary
Processes a pandas Series of file paths to extract file system metadata and compute file size distribution statistics.

## Description
This function serves as a specialized data processing step for file-based datasets in the profiling workflow. It validates input file paths, extracts comprehensive file system metadata (sizes and timestamps), and computes statistical distributions of file sizes. The function is designed to be part of a larger data profiling pipeline where file metadata needs to be analyzed alongside other data characteristics.

The logic is extracted into its own function to separate file system operations from general data analysis, enabling cleaner code organization and easier testing of file-specific processing logic.

## Args
    config (Settings): Configuration object containing plotting settings and parameters
    series (pd.Series): A pandas Series containing file paths as strings
    summary (dict): Dictionary to be updated with file metadata and statistics

## Returns
    Tuple[Settings, pd.Series, dict]: A tuple containing the updated configuration, the original series, and the updated summary dictionary

## Raises
    ValueError: When the input series contains NaN values or lacks string accessor
    FileNotFoundError: When any file path in the series does not exist (propagated from file_summary)
    PermissionError: When access to a file path is denied (propagated from file_summary)
    OSError: When system-level errors occur during file stat operations (propagated from file_summary)

## Constraints
    Preconditions:
        - Input series must not contain NaN values
        - Input series must have string accessor (.str attribute)
        - All file paths in the series must be valid and accessible
    Postconditions:
        - Summary dictionary is updated with file metadata and histogram statistics
        - The returned series remains unchanged from input

## Side Effects
    - Performs file system operations (os.stat) for each file path in the input series
    - May trigger file system I/O errors if files don't exist or aren't accessible
    - Modifies the input summary dictionary in-place by updating it with new key-value pairs

## Control Flow
```mermaid
flowchart TD
    A[Input: config, series, summary] --> B{Validate series hasnans}
    B -->|True| C[raise ValueError("May not contain NaNs")]
    B -->|False| D{Validate series.str accessor}
    D -->|False| E[raise ValueError("series should have .str accessor")]
    D -->|True| F[Update summary with file_summary results]
    F --> G[Compute histogram using histogram_compute]
    G --> H[Return config, series, summary]
```

## Examples
```python
import pandas as pd
from ydata_profiling.config import Settings
from src.ydata_profiling.model.pandas.describe_file_pandas import pandas_describe_file_1d

# Basic usage
config = Settings()
file_paths = pd.Series(['/path/to/file1.txt', '/path/to/file2.txt'])
summary = {}

try:
    config, series, summary = pandas_describe_file_1d(config, file_paths, summary)
    print("File metadata:", summary.keys())
    print("File sizes:", summary.get('file_size'))
    print("Histogram computed:", 'histogram_file_size' in summary)
except ValueError as e:
    print(f"Validation error: {e}")
except (FileNotFoundError, PermissionError) as e:
    print(f"File access error: {e}")
```

