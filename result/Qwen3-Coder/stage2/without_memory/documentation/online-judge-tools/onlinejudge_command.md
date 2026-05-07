# `onlinejudge_command`

## Tree:
- onlinejudge_command/
  - download_history.py
  - format_utils.py
  - log_formatter.py
  - output_comparators.py
  - pretty_printers.py
  - update_checking.py
  - utils.py

## Role:
Provides command-line interface utilities for online judge tools, including file formatting, output comparison, logging, and system utilities.

## Description:
This module serves as a centralized collection of utility functions and classes that support the command-line interface of online judge tools. It handles various aspects of command execution, file processing, output comparison, and system interactions. The module acts as a foundation for common functionalities used throughout the online judge toolchain.

Primary consumers of this module include the main CLI entry points and various command implementations that require standardized utilities for handling files, comparing outputs, managing logs, and executing system commands.

The components are grouped together because they share a common purpose of supporting command-line operations and providing reusable utilities for online judge-related tasks.

## Components:
- download_history.py: Provides functionality for tracking download history of problems
- format_utils.py: Contains utilities for working with file formats and patterns
- log_formatter.py: Implements custom logging formatters for better console output
- output_comparators.py: Offers various methods for comparing program outputs
- pretty_printers.py: Provides enhanced pretty printing capabilities for diffs and file content
- update_checking.py: Handles checking for updates from PyPI
- utils.py: Contains general utility functions for system operations and command execution

## Public API:
- `DownloadHistory`: Class for managing download history tracking
  - `__init__(path: pathlib.Path = utils.user_cache_dir / 'download-history.jsonl')`
  - `add(problem: Problem, *, directory: pathlib.Path) -> None`
  - `remove(*, directory: pathlib.Path) -> None`
  - `get(*, directory: pathlib.Path) -> List[str]`
- `LogFormatter`: Custom logging formatter for colored console output
  - `__init__(datefmt: Optional[str] = None)`
  - `format(record: logging.LogRecord) -> str`
- `OutputComparator`: Abstract base class for output comparison strategies
  - `__call__(actual: bytes, expected: bytes) -> bool`
- `CompareMode`: Enum defining different comparison modes
  - `EXACT_MATCH = 'exact-match'`
  - `CRLF_INSENSITIVE_EXACT_MATCH = 'crlf-insensitive-exact-match'`
  - `IGNORE_SPACES = 'ignore-spaces'`
  - `IGNORE_SPACES_AND_NEWLINES = 'ignore-spaces-and-newlines'`
- `ExactComparator`: Compares outputs exactly
  - `__call__(actual: bytes, expected: bytes) -> bool`
- `CRLFInsensitiveComparator`: Compares outputs ignoring CRLF differences
  - `__init__(file_comparator: OutputComparator)`
  - `__call__(actual: bytes, expected: bytes) -> bool`
- `FloatingPointNumberComparator`: Compares floating-point numbers with tolerance
  - `__init__(*, rel_tol: float, abs_tol: float)`
  - `__call__(actual: bytes, expected: bytes) -> bool`
- `SplitComparator`: Splits outputs by whitespace and compares words
  - `__init__(word_comparator: OutputComparator)`
  - `__call__(actual: bytes, expected: bytes) -> bool`
- `SplitLinesComparator`: Splits outputs by lines and compares them
  - `__init__(line_comparator: OutputComparator)`
  - `__call__(actual: bytes, expected: bytes) -> bool`
- `check_lines_match`: Checks if two lines match according to a comparison mode
  - `check_lines_match(a: str, b: str, *, compare_mode: CompareMode) -> bool`
- `make_pretty_diff`: Creates a pretty-printed diff between two outputs
  - `make_pretty_diff(output_bytes: bytes, *, expected: str, compare_mode: CompareMode, limit: int) -> str`
- `make_pretty_all`: Pretty-prints entire file content
  - `make_pretty_all(content: bytes) -> str`
- `make_pretty_large_file_content`: Pretty-prints large file content with limits
  - `make_pretty_large_file_content(content: bytes, limit: int, head: int, tail: int) -> str`
- `exec_command`: Executes shell commands with timing and memory measurement
  - `exec_command(command_str: str, *, stdin: Optional[BinaryIO] = None, input: Optional[bytes] = None, timeout: Optional[float] = None, gnu_time: Optional[str] = None) -> Tuple[Dict[str, Any], subprocess.Popen]`
- `new_session_with_our_user_agent`: Creates a requests session with proper user agent
  - `new_session_with_our_user_agent(*, path: pathlib.Path) -> Iterator[requests.Session]`
- `is_update_available_on_pypi`: Checks if an update is available on PyPI
  - `is_update_available_on_pypi(package_name: str, current_version: str) -> bool`
- `run`: Runs update checking for all packages
  - `run() -> bool`
- `run_for_package`: Runs update checking for a specific package
  - `run_for_package(*, package_name: str, current_version: str) -> bool`
- `glob_with_format`: Finds files matching a format pattern
  - `glob_with_format(directory: pathlib.Path, format: str) -> List[pathlib.Path]`
- `match_with_format`: Matches a file path against a format pattern
  - `match_with_format(directory: pathlib.Path, format: str, path: pathlib.Path) -> Optional[Match[str]]`
- `path_from_format`: Constructs a file path from format components
  - `path_from_format(directory: pathlib.Path, format: str, name: str, ext: str) -> pathlib.Path`
- `percentformat`: Formats a string using percent-style placeholders
  - `percentformat(s: str, table: Dict[str, str]) -> str`
- `percentparse`: Parses a string using percent-style format patterns
  - `percentparse(s: str, format: str, table: Dict[str, str]) -> Optional[Dict[str, str]]`
- `percentsplit`: Splits a string by percent characters
  - `percentsplit(s: str) -> Generator[str, None, None]`
- `drop_backup_or_hidden_files`: Filters out backup and hidden files
  - `drop_backup_or_hidden_files(paths: List[pathlib.Path]) -> List[pathlib.Path]`
- `construct_relationship_of_files`: Builds relationship mapping from file paths
  - `construct_relationship_of_files(paths: List[pathlib.Path], directory: pathlib.Path, format: str) -> Dict[str, Dict[str, pathlib.Path]]`

## Dependencies:
Internal imports:
- `utils`: Provides general utility functions like user cache directory, session management, and command execution
- `version`: Used for version checking in update functionality
- `api_version`: Used for API version checking in update functionality
- `Problem`: Required for download history tracking

External imports:
- `pathlib`: For path manipulation and file system operations
- `logging`: For logging functionality
- `json`: For JSON serialization/deserialization
- `time`: For time-related operations
- `os`, `sys`, `subprocess`, `signal`: For system-level operations
- `re`, `difflib`, `collections`, `itertools`: For pattern matching and data processing
- `colorama`, `webbrowser`, `http.client`, `distutils.version`, `requests`, `shutil`, `traceback`: For terminal formatting, browser integration, HTTP operations, version comparisons, and more

## Constraints:
- All file operations must respect proper error handling and logging
- Commands executed via `exec_command` must handle timeouts and process cleanup properly
- Update checking requires network connectivity and proper caching mechanisms
- Logging must be consistent with the defined formatter
- File format utilities must handle cross-platform path separators correctly
- Output comparators must be thread-safe and handle edge cases appropriately

---

## Files

- [`download_history.py`](onlinejudge_command/download_history.md)
- [`format_utils.py`](onlinejudge_command/format_utils.md)
- [`log_formatter.py`](onlinejudge_command/log_formatter.md)
- [`output_comparators.py`](onlinejudge_command/output_comparators.md)
- [`pretty_printers.py`](onlinejudge_command/pretty_printers.md)
- [`update_checking.py`](onlinejudge_command/update_checking.md)
- [`utils.py`](onlinejudge_command/utils.md)

