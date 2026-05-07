# `shutil_backport.py`

## `datasette.utils.shutil_backport._copytree` · *function*

## Summary:
Copies a directory tree recursively while handling symbolic links, ignored files, and preserving metadata.

## Description:
This function implements a custom directory tree copying mechanism that supports symbolic links, file ignoring patterns, and various copy options. It's designed as a backport or alternative implementation of Python's shutil.copytree functionality with enhanced control over the copying process. The function processes directory entries and handles different file types appropriately, including regular files, directories, and symbolic links.

## Args:
    entries (list): Directory entries to copy, typically obtained from os.scandir() or similar objects with name, is_dir(), and is_symlink() methods.
    src (str): Source directory path to copy from.
    dst (str): Destination directory path to copy to.
    symlinks (bool): If True, symbolic links are copied as symbolic links; otherwise, the linked files are copied.
    ignore (callable, optional): Function that takes (src, names) and returns a set of names to ignore. If None, no files are ignored.
    copy_function (callable): Function used to copy files (e.g., shutil.copy, shutil.copy2).
    ignore_dangling_symlinks (bool): If True, dangling symbolic links are ignored.
    dirs_exist_ok (bool): If True, destination directory can already exist. Defaults to False.

## Returns:
    str: The destination directory path that was copied to.

## Raises:
    Error: When errors occur during the copying process, with detailed error information containing tuples of (src, dst, error_message).
    OSError: When OS-level errors occur during file operations.

## Constraints:
    Preconditions:
    - Source directory must exist and be readable
    - Entries must be valid directory entries with name, is_dir(), and is_symlink() methods
    - Copy function must be callable and handle appropriate file types
    
    Postconditions:
    - Destination directory will exist after successful completion
    - All files and subdirectories will be copied according to the specified parameters
    - Metadata will be preserved when using copy2 or copy functions that support it

## Side Effects:
    - Creates directories in the destination path
    - Copies files from source to destination
    - May create symbolic links in the destination
    - Modifies filesystem state through directory creation and file copying
    - Calls copystat to preserve metadata

## Control Flow:
```mermaid
flowchart TD
    A[Start _copytree] --> B{ignore is not None?}
    B -- Yes --> C[Get ignored names via ignore(src, set(os.listdir(src)))]
    B -- No --> D[ignored_names = set()]
    C --> D
    D --> E[Create dst directory with os.makedirs(dst, exist_ok=dirs_exist_ok)]
    E --> F[Initialize errors list]
    F --> G[Set use_srcentry flag based on copy_function]
    G --> H[Process each entry in entries]
    H --> I{Entry name in ignored_names?}
    I -- Yes --> J[Skip entry]
    I -- No --> K[Build srcname and dstname paths]
    K --> L{Is symlink?}
    L -- Yes --> M{symlinks=True?}
    M -- Yes --> N[Create symlink with os.symlink(linkto, dstname)]
    M -- No --> O{Dangling link + ignore_dangling_symlinks?}
    O -- Yes --> P[Skip entry]
    O -- No --> Q{Is directory?}
    Q -- Yes --> R[Recursive call to _copytree with srcobj, dstname, etc.]
    Q -- No --> S[Copy file with copy_function(srcobj, dstname)]
    N --> T[Copy stats with copystat(srcobj, dstname, follow_symlinks=not symlinks)]
    R --> U[Continue processing]
    S --> U
    P --> U
    L -- No --> V{Is directory?}
    V -- Yes --> W[Recursive call to _copytree with srcobj, dstname, etc.]
    V -- No --> X[Copy file with copy_function(srcentry, dstname)]
    W --> U
    X --> U
    U --> Y{Errors occurred?}
    Y -- Yes --> Z[Raise Error with errors list]
    Y -- No --> AA[Copy src stats to dst with copystat(src, dst)]
    AA --> AB{Windows error check?}
    AB -- Yes --> AC[Add Windows-specific error to list]
    AB -- No --> AD[Return dst path]
```

## Examples:
    # Basic usage
    import os
    from shutil import copy2
    from datasette.utils.shutil_backport import _copytree
    
    entries = list(os.scandir('/path/to/source'))
    _copytree(entries, '/path/to/source', '/path/to/destination', False, None, copy2, False)
    
    # With ignore function
    def ignore_func(src, names):
        return {'.git', '__pycache__'}
    
    _copytree(entries, '/path/to/source', '/path/to/destination', False, ignore_func, copy2, False)

## `datasette.utils.shutil_backport.copytree` · *function*

## Summary:
Copies a directory tree recursively from source to destination, with support for symbolic links, ignoring specified files, and handling existing directories.

## Description:
This function provides a backport implementation of Python's shutil.copytree functionality with performance improvements using os.scandir. It recursively copies all files and subdirectories from a source directory to a destination directory, preserving file metadata and handling various edge cases like symbolic links and existing directories.

The function was extracted into its own component to provide a reusable, optimized directory copying mechanism that can handle complex scenarios while maintaining compatibility with standard shutil behavior.

## Args:
    src (str): Source directory path to copy from
    dst (str): Destination directory path to copy to
    symlinks (bool): If True, copy symbolic links as symbolic links; if False, copy the contents of the linked files. Defaults to False.
    ignore (callable, optional): Function that takes (src, names) and returns a set of names to ignore. Defaults to None.
    copy_function (callable): Function used to copy files (defaults to copy2 which preserves metadata). Must accept two arguments (source, destination).
    ignore_dangling_symlinks (bool): If True, ignore dangling symbolic links. Defaults to False.
    dirs_exist_ok (bool): If True, don't raise an exception if the destination directory already exists. Defaults to False.

## Returns:
    str: The destination path that was copied to

## Raises:
    Error: Raised when there are issues copying files or directories during the operation
    OSError: Raised when there are OS-level issues such as permission errors, invalid paths, or filesystem errors

## Constraints:
    Preconditions:
    - Source directory must exist and be readable
    - Parent directories of destination must exist or be creatable
    - If dirs_exist_ok=False, destination directory must not already exist
    
    Postconditions:
    - All files and subdirectories from source are copied to destination
    - File metadata is preserved when using copy2 or copy_function that preserves metadata
    - Destination directory structure matches source directory structure

## Side Effects:
    - Creates new directories in the destination path
    - Copies files from source to destination
    - May modify file permissions and timestamps if copy_function preserves metadata
    - May create symbolic links in destination if symlinks=True

## Control Flow:
```mermaid
flowchart TD
    A[Start copytree] --> B{os.scandir(src)}
    B --> C[Initialize entries]
    C --> D[_copytree with entries]
    D --> E{Ignore function defined?}
    E -->|Yes| F[Get ignored names]
    E -->|No| G[Set empty ignored names]
    G --> H[Create dst directory with dirs_exist_ok]
    H --> I[Initialize errors list]
    I --> J[Check copy_function type]
    J --> K[Process each entry]
    K --> L{Entry is symlink?}
    L -->|Yes| M[Handle symlink]
    L -->|No| N{Entry is dir?}
    N -->|Yes| O[Recursively copy dir]
    N -->|No| P[Copy file with copy_function]
    M --> Q{symlinks flag?}
    Q -->|True| R[Create symlink]
    Q -->|False| S{ignore_dangling_symlinks?}
    S -->|True| T[Skip dangling symlink]
    S -->|False| U[Copy contents]
    U --> V[Recursive copy or file copy]
    R --> W[Copy metadata]
    T --> X[Continue processing]
    O --> Y[Recursive call to copytree]
    P --> Z[Copy file with copy_function]
    Y --> AA[Return from recursive call]
    Z --> AB[Continue processing]
    V --> AC[Continue processing]
    AC --> AD{Any errors?}
    AD -->|Yes| AE[Raise Error with errors]
    AD -->|No| AF[Copy source metadata]
    AF --> AG[Return dst path]
```

## Examples:
    # Basic usage - copy directory with metadata preservation
    copytree('/path/to/source', '/path/to/destination')
    
    # Copy without preserving metadata
    copytree('/path/to/source', '/path/to/destination', copy_function=copy)
    
    # Copy symbolic links as links
    copytree('/path/to/source', '/path/to/destination', symlinks=True)
    
    # Ignore specific files/directories
    def ignore_patterns(src, names):
        return {'.git', '__pycache__'}
    
    copytree('/path/to/source', '/path/to/destination', ignore=ignore_patterns)
    
    # Allow overwriting existing destination directory
    copytree('/path/to/source', '/path/to/destination', dirs_exist_ok=True)
    
    # Handle dangling symlinks gracefully
    copytree('/path/to/source', '/path/to/destination', ignore_dangling_symlinks=True)

