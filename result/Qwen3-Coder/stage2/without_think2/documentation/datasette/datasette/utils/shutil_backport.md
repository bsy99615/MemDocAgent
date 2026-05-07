# `shutil_backport.py`

## `datasette.utils.shutil_backport._copytree` · *function*

## Summary:
Copies a directory tree from source to destination, handling symbolic links, ignored files, and various copy options.

## Description:
This function recursively copies an entire directory tree from a source location to a destination location. It processes directory entries and handles symbolic links, ignored files, and various copy functions. The function is designed to work with directory entries obtained via `os.scandir()` and provides a backport implementation for directory copying functionality.

Known callers within the codebase:
- Called internally by the `copytree` function when processing directory entries
- Triggered during directory duplication operations such as plugin installation or database export workflows

This logic is extracted into its own function to provide a reusable, robust directory copying mechanism that handles edge cases like symbolic links, ignored files, and existing destination directories. It encapsulates complex recursive copying logic while maintaining compatibility with standard shutil behaviors.

## Args:
- entries (list): Directory entries obtained from `os.scandir()` for the source directory
- src (str): Path to the source directory to be copied
- dst (str): Path to the destination directory where the copy will be created
- symlinks (bool): If True, symbolic links are copied as symbolic links; if False, the contents of the linked files are copied instead. Defaults to False.
- ignore (callable, optional): A callable that takes two arguments (src, names) and returns a set of names to ignore during copying. Defaults to None.
- copy_function (callable): Function used to copy individual files. Defaults to copy2 (preserves metadata).
- ignore_dangling_symlinks (bool): If True, dangling symbolic links are ignored. Defaults to False.
- dirs_exist_ok (bool): If True, destination directory can already exist. Defaults to False.

## Returns:
- str: The path to the destination directory that was created.

## Raises:
- Error: Raised when copying fails due to multiple errors encountered during the process.
- OSError: Raised when OS-level errors occur during file operations.

## Constraints:
- Preconditions:
  - Source directory must exist and be readable
  - Destination parent directory must be writable
  - If dirs_exist_ok is False, destination directory must not already exist
- Postconditions:
  - Destination directory will contain a copy of all files and subdirectories from source
  - All symbolic links are handled according to symlinks and ignore_dangling_symlinks parameters
  - Directory permissions and metadata are preserved when using copy2

## Side Effects:
- Creates new files and directories in the destination path
- May modify existing directories if dirs_exist_ok=True
- Reads from the source directory and its contents
- Writes to the destination directory and its contents

## Control Flow:
```mermaid
flowchart TD
    A[Start _copytree] --> B{ignore is not None}
    B -->|True| C[Get ignored names from ignore function]
    B -->|False| D[ignored_names = set()]
    C --> E[Create dst directory with os.makedirs]
    D --> E
    E --> F[Initialize errors list]
    F --> G[Set use_srcentry flag]
    G --> H[Loop through entries]
    H --> I{Entry name in ignored_names?}
    I -->|Yes| J[Skip entry]
    I -->|No| K[Build srcname and dstname]
    K --> L{Is symlink?}
    L -->|Yes| M{symlinks=True?}
    M -->|Yes| N[Create symlink with os.symlink]
    M -->|No| O{ignore_dangling_symlinks=True?}
    O -->|Yes| P[Skip dangling symlink]
    O -->|No| Q{srcentry.is_dir()?}
    Q -->|Yes| R[Recursively call copytree]
    Q -->|No| S[Use copy_function]
    L -->|No| T{Is directory?}
    T -->|Yes| U[Recursively call copytree]
    T -->|No| V[Use copy_function]
    W[End loop] --> X[Copy stats from src to dst]
    X --> Y{Errors occurred?}
    Y -->|Yes| Z[Raise Error with accumulated errors]
    Y -->|No| AA[Return dst]
```

## Examples:
```python
# Basic usage with directory entries
import os
entries = list(os.scandir('/path/to/source'))
_copytree(entries, '/path/to/source', '/path/to/destination')

# Copy with symbolic links preserved
entries = list(os.scandir('/path/to/source'))
_copytree(entries, '/path/to/source', '/path/to/destination', symlinks=True)

# Copy with ignored files
def ignore_func(src, names):
    return {'.git', '__pycache__'}

entries = list(os.scandir('/path/to/source'))
_copytree(entries, '/path/to/source', '/path/to/destination', ignore=ignore_func)
```

## `datasette.utils.shutil_backport.copytree` · *function*

## Summary:
Creates a copy of a directory tree from source to destination, supporting symbolic links, ignored files, and various copy options.

## Description:
This function recursively copies an entire directory tree from a source location to a destination location. It handles symbolic links, ignores specified files or directories, and supports various copy functions. The function is a backport implementation that mimics the behavior of Python's standard library shutil.copytree function with additional features.

Known callers within the codebase:
- The function is likely called by Datasette's internal file management utilities when copying directories during operations like plugin installation or database export.
- It's typically triggered during setup or deployment phases where directory duplication is required.

This logic is extracted into its own function to provide a reusable, robust directory copying mechanism that handles edge cases like symbolic links, ignored files, and existing destination directories. It encapsulates complex recursive copying logic while maintaining compatibility with standard shutil behaviors.

## Args:
- src (str): Path to the source directory to be copied
- dst (str): Path to the destination directory where the copy will be created
- symlinks (bool): If True, symbolic links are copied as symbolic links; if False, the contents of the linked files are copied instead. Defaults to False.
- ignore (callable, optional): A callable that takes two arguments (src, names) and returns a set of names to ignore during copying. Defaults to None.
- copy_function (callable): Function used to copy individual files. Defaults to copy2 (preserves metadata).
- ignore_dangling_symlinks (bool): If True, dangling symbolic links are ignored. Defaults to False.
- dirs_exist_ok (bool): If True, destination directory can already exist. Defaults to False.

## Returns:
- str: The path to the destination directory that was created.

## Raises:
- Error: Raised when copying fails due to multiple errors encountered during the process.
- OSError: Raised when OS-level errors occur during file operations.

## Constraints:
- Preconditions:
  - Source directory must exist and be readable
  - Destination parent directory must be writable
  - If dirs_exist_ok is False, destination directory must not already exist
- Postconditions:
  - Destination directory will contain a copy of all files and subdirectories from source
  - All symbolic links are handled according to symlinks and ignore_dangling_symlinks parameters
  - Directory permissions and metadata are preserved when using copy2

## Side Effects:
- Creates new files and directories in the destination path
- May modify existing directories if dirs_exist_ok=True
- Reads from the source directory and its contents
- Writes to the destination directory and its contents

## Control Flow:
```mermaid
flowchart TD
    A[Start copytree] --> B{os.scandir(src)}
    B --> C[Initialize entries]
    C --> D[Call _copytree with entries]
    D --> E{ignore is not None}
    E -->|True| F[Get ignored names]
    E -->|False| G[ignored_names = set()]
    F --> H[Create dst directory]
    G --> H
    H --> I[Loop through entries]
    I --> J{Entry name in ignored_names?}
    J -->|Yes| K[Skip entry]
    J -->|No| L[Build srcname and dstname]
    L --> M{Is symlink?}
    M -->|Yes| N{symlinks=True?}
    N -->|Yes| O[Copy symlink]
    N -->|No| P{ignore_dangling_symlinks=True?}
    P -->|Yes| Q[Skip dangling symlink]
    P -->|No| R{srcentry.is_dir()?}
    R -->|Yes| S[Recursively call copytree]
    R -->|No| T[Use copy_function]
    M -->|No| U{Is directory?}
    U -->|Yes| V[Recursively call copytree]
    U -->|No| W[Use copy_function]
    X[End loop] --> Y[Copystat src to dst]
    Y --> Z{Errors occurred?}
    Z -->|Yes| AA[Raise Error]
    Z -->|No| AB[Return dst]
```

## Examples:
```python
# Basic usage
copytree('/path/to/source', '/path/to/destination')

# Copy with symbolic links preserved
copytree('/path/to/source', '/path/to/destination', symlinks=True)

# Copy with ignored files
def ignore_func(src, names):
    return {'.git', '__pycache__'}

copytree('/path/to/source', '/path/to/destination', ignore=ignore_func)
```

