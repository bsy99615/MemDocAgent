# `input_parsing.py`

## `src.exodus_bundler.input_parsing.extract_exec_path` · *function*

*No documentation generated.*

## `src.exodus_bundler.input_parsing.extract_open_path` · *function*

## Summary:
Extracts a file path from log lines representing open system call operations.

## Description:
Parses log lines containing system call traces to extract file paths from 'open' and 'openat' system call entries. This function filters out error conditions and non-read-only file operations, returning only paths from valid read-only file opens. The function strips process ID prefixes before processing and applies several validation checks to ensure the extracted path represents a legitimate file access operation.

## Args:
    line (str): A log line potentially containing an open system call operation with optional process ID prefix.

## Returns:
    str or None: The extracted file path if the line matches a valid open system call pattern with O_RDONLY flag and no error conditions, otherwise None.

## Raises:
    None: This function does not explicitly raise exceptions.

## Constraints:
    Preconditions:
        - Input line should be a string representing a log entry
        - Line may contain process ID prefix that will be stripped by strip_pid_prefix
    Postconditions:
        - Returns the file path portion of a valid open system call or None if no match found
        - Does not modify the original input line
        - Only returns paths from O_RDONLY operations that aren't marked as errors

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Input line] --> B[strip_pid_prefix(line)]
    B --> C{Starts with 'openat(AT_FDCWD, \"'?}
    C -- Yes --> D[Extract path part after prefix]
    D --> E{Split by \", \" yields 2 parts?}
    E -- No --> F[Return None]
    E -- Yes --> G{Contains ENOENT?}
    G -- Yes --> F
    G -- No --> H{Contains O_RDONLY?}
    H -- No --> F
    H -- Yes --> I{Contains O_DIRECTORY?}
    I -- Yes --> F
    I -- No --> J[Return path part]
    C -- No --> K{Starts with 'open(\"'?}
    K -- No --> F
    K -- Yes --> L[Extract path part after prefix]
    L --> M{Split by \", \" yields 2 parts?}
    M -- No --> F
    M -- Yes --> N{Contains ENOENT?}
    N -- Yes --> F
    N -- No --> O{Contains O_RDONLY?}
    O -- No --> F
    O -- Yes --> P{Contains O_DIRECTORY?}
    P -- Yes --> F
    P -- No --> Q[Return path part]
```

## Examples:
    >>> extract_open_path('[pid 1234] openat(AT_FDCWD, "/etc/passwd", O_RDONLY|O_CLOEXEC) = 3')
    '/etc/passwd'
    
    >>> extract_open_path('[pid 5678] open("/tmp/test.txt", O_RDONLY) = 4')
    '/tmp/test.txt'
    
    >>> extract_open_path('[pid 999] openat(AT_FDCWD, "/nonexistent", O_RDONLY) = -2 (ENOENT)')
    None
    
    >>> extract_open_path('[pid 111] open("/var/log/app.log", O_RDWR) = 5')
    None
    
    >>> extract_open_path('[pid 222] open("/home/user/dir", O_RDONLY|O_DIRECTORY) = 6')
    None

## `src.exodus_bundler.input_parsing.extract_stat_path` · *function*

## Summary:
Extracts file paths from stat() system call log entries by parsing formatted log lines.

## Description:
Parses log lines containing system call information in the format 'stat("filename", ...)' and extracts the file path portion. This function is specifically designed to process log output from system calls that track file access patterns, particularly for analyzing file system interactions in program execution traces. It handles log lines that may contain process ID prefixes by first stripping them before parsing.

## Args:
    line (str): A log line that may contain a stat() system call entry in the format 'stat("filename", ...)'

## Returns:
    str or None: The extracted file path if the line matches the expected stat() format and contains no ENOENT error indicator, otherwise None

## Raises:
    None: This function does not explicitly raise exceptions

## Constraints:
    Preconditions:
        - Input line must be a string
        - Line should follow the format 'stat("filename", ...)' for successful extraction
    Postconditions:
        - Returns the first argument of the stat() call if valid, or None if invalid format
        - Original line is not modified

## Side Effects:
    None: This function has no side effects

## Control Flow:
```mermaid
flowchart TD
    A[Input line] --> B[Apply strip_pid_prefix]
    B --> C{Line starts with "stat("}
    C -- No --> D[Return None]
    C -- Yes --> E[Remove "stat(" prefix]
    E --> F[Split by "\", "]
    F --> G{Length == 2 AND "ENOENT" not in second part}
    G -- No --> H[Return None]
    G -- Yes --> I[Return first part (file path)]
```

## Examples:
    >>> extract_stat_path('stat("test.txt", 0x123)')
    'test.txt'
    
    >>> extract_stat_path('stat("nonexistent.txt", ENOENT)')
    None
    
    >>> extract_stat_path('regular line without stat')
    None
```

## `src.exodus_bundler.input_parsing.extract_paths` · *function*

*No documentation generated.*

## `src.exodus_bundler.input_parsing.strip_pid_prefix` · *function*

## Summary:
Removes process ID prefixes from log lines that follow the format `[pid <number>]`.

## Description:
Strips leading process ID prefixes of the form `[pid <number>]` followed by whitespace from log lines. This utility function is designed to clean log output by removing metadata that identifies the process that generated the log entry.

## Args:
    line (str): A string that may contain a process ID prefix in the format `[pid <number>]`.

## Returns:
    str: The input line with the process ID prefix removed if present, otherwise returns the original line unchanged.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions:
        - Input must be a string
    Postconditions:
        - If the line starts with `[pid <number>]` followed by whitespace, that prefix is stripped
        - If no matching prefix is found, the original line is returned unchanged

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Input line] --> B{Matches pattern \\[pid \\d+\\] \\s*}
    B -- Yes --> C[Return line without prefix]
    B -- No --> D[Return original line]
```

## Examples:
    >>> strip_pid_prefix("[pid 1234] Hello world")
    'Hello world'
    
    >>> strip_pid_prefix("[pid 5678]   Multiple spaces")
    'Multiple spaces'
    
    >>> strip_pid_prefix("No prefix here")
    'No prefix here'
    
    >>> strip_pid_prefix("[pid 999] ")
    ''
```

