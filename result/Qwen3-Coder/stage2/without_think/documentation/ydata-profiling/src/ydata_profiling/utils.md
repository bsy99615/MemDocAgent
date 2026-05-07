# `src.ydata_profiling.utils`

## Tree:
```
utils/
├── cache.py
├── common.py
├── compat.py
├── dataframe.py
├── imghdr_patch.py
├── notebook.py
├── paths.py
├── progress_bar.py
└── versions.py
```

## Role:
Provides foundational utilities and helper functions for data profiling operations, including file handling, data manipulation, path resolution, and compatibility checks.

## Description:
The utils module serves as a collection of reusable utility functions and classes that support various aspects of the ydata-profiling library. These utilities are designed to be independent components that can be imported and used across different parts of the profiling system. The module is organized around functional areas such as caching, data processing, path management, and version compatibility.

This module is used extensively throughout the ydata-profiling library for tasks ranging from file I/O operations to data transformation and compatibility handling. It provides a centralized location for common operations that don't belong in the core profiling logic but are essential for the system's functionality.

## Components:
*   `cache_file` (function): Downloads and caches files from URLs to local data directory
*   `cache_zipped_file` (function): Downloads and caches files from ZIP archives
*   `_copy` (method): Copies files from one location to another
*   `convert_timestamp_to_datetime` (function): Converts Unix timestamps to datetime objects
*   `extract_zip` (function): Extracts contents from ZIP archive files
*   `test_jpeg1` (function): Detects JPEG images by checking for JFIF signature
*   `test_jpeg2` (function): Tests JPEG image files by examining header signatures
*   `test_jpeg3` (function): Determines JPEG image format by checking byte patterns
*   `update` (function): Recursively updates dictionaries with nested merging
*   `pandas_version_info` (function): Returns pandas version as tuple for comparison
*   `expand_mixed` (function): Expands DataFrame columns containing container values
*   `hash_dataframe` (function): Creates SHA256 hash of a pandas DataFrame
*   `is_supported_compression` (function): Validates file extensions for supported compression formats
*   `read_pandas` (function): Reads data files of various formats into pandas DataFrames
*   `remove_suffix` (function): Safely removes suffixes from strings
*   `rename_index` (function): Renames "index" columns/index levels to avoid naming conflicts
*   `slugify` (function): Converts strings into URL-friendly slugs
*   `sort_column_names` (function): Sorts dictionary items by keys in specified order
*   `uncompressed_extension` (function): Extracts true file extension from compressed files
*   `warn_read` (function): Issues warnings for file reading operations
*   `full_width` (function): Applies CSS styling for full-width Jupyter notebook containers
*   `get_config` (function): Returns path to configuration files relative to module parent
*   `get_data_path` (function): Returns absolute path to project's data directory
*   `get_html_template_path` (function): Returns path to HTML template directory
*   `get_project_root` (function): Returns absolute path to project root directory
*   `progress` (function): Decorator for wrapping functions with progress bar updates
*   `is_pandas_1` (function): Checks if installed pandas version is 1.x
*   `pandas_major_version` (function): Returns major version number of pandas
*   `pandas_version` (function): Returns pandas version as list of integers

## Public API:
*   `cache_file(file_name: str, url: str) -> Path`: Downloads and caches a file from a URL
*   `cache_zipped_file(file_name: str, url: str) -> Path`: Downloads and caches a file from a ZIP archive
*   `convert_timestamp_to_datetime(timestamp: int) -> datetime`: Converts Unix timestamp to datetime object
*   `extract_zip(outfile: str, effective_path: str) -> None`: Extracts contents from a ZIP archive
*   `test_jpeg1(h: bytes, f: file-like object) -> str`: Detects JPEG images by checking JFIF signature
*   `test_jpeg2(h: bytes, f: file-like object) -> str or None`: Tests JPEG image files by examining header signatures
*   `test_jpeg3(h: bytes, f: Any) -> str`: Determines JPEG image format by checking byte patterns
*   `update(d: dict, u: Mapping) -> dict`: Recursively updates dictionaries with nested merging
*   `pandas_version_info() -> Tuple[int, ...]`: Returns pandas version as tuple for comparison
*   `expand_mixed(df: pd.DataFrame, types: Any = None) -> pd.DataFrame`: Expands DataFrame columns with container values
*   `hash_dataframe(df: pandas.DataFrame) -> str`: Creates SHA256 hash of a DataFrame
*   `is_supported_compression(file_extension: str) -> bool`: Validates compression format support
*   `read_pandas(file_name: Path) -> pd.DataFrame`: Reads data files into pandas DataFrames
*   `remove_suffix(text: str, suffix: str) -> str`: Safely removes suffix from strings
*   `rename_index(df: pandas.DataFrame) -> pandas.DataFrame`: Renames "index" columns/index levels
*   `slugify(value: str, allow_unicode: bool = False) -> str`: Converts strings to URL-friendly slugs
*   `sort_column_names(dct: dict, sort: Optional[str] = None) -> dict`: Sorts dictionary items by keys
*   `uncompressed_extension(file_name: Path) -> str`: Extracts true file extension from compressed files
*   `warn_read(extension: str) -> None`: Issues warnings for file reading operations
*   `full_width() -> None`: Applies CSS styling for full-width Jupyter notebook containers
*   `get_config(file_name: str) -> Path`: Returns path to configuration files
*   `get_data_path() -> Path`: Returns absolute path to project's data directory
*   `get_html_template_path() -> Path`: Returns path to HTML template directory
*   `get_project_root() -> Path`: Returns absolute path to project root directory
*   `progress(fn: Callable, bar: tqdm, message: str) -> Callable`: Decorator for progress bar updates
*   `is_pandas_1() -> bool`: Checks if installed pandas version is 1.x
*   `pandas_major_version() -> int`: Returns major version number of pandas
*   `pandas_version() -> list[int]`: Returns pandas version as list of integers

## Dependencies:
*   Internal imports:
    *   `src.ydata_profiling.utils.cache` - Provides caching functionality for files
    *   `src.ydata_profiling.utils.common` - Contains general utility functions
    *   `src.ydata_profiling.utils.compat` - Handles compatibility checks for different versions
    *   `src.ydata_profiling.utils.dataframe` - Provides DataFrame manipulation utilities
    *   `src.ydata_profiling.utils.imghdr_patch` - Extends image header detection capabilities
    *   `src.ydata_profiling.utils.notebook` - Provides notebook-specific utilities
    *   `src.ydata_profiling.utils.paths` - Manages path resolution utilities
    *   `src.ydata_profiling.utils.progress_bar` - Offers progress bar functionality
    *   `src.ydata_profiling.utils.versions` - Handles version-related checks and comparisons
*   External imports:
    *   `pathlib` - For path manipulation and file system operations
    *   `urllib` - For URL handling and network operations
    *   `shutil` - For file copying operations
    *   `zipfile` - For ZIP archive handling
    *   `pandas` - Core data manipulation library
    *   `tqdm` - Progress bar visualization library
    *   `warnings` - For issuing warnings during file operations
    *   `importlib.metadata` - For retrieving package version information

## Constraints:
*   All functions requiring file system access must have appropriate permissions
*   Functions that depend on pandas must ensure pandas is installed and importable
*   Path-related functions assume standard directory structures are maintained
*   Version checking functions require pandas to be installed
*   Progress bar functions require tqdm to be available
*   Thread safety: Most utility functions are stateless and therefore thread-safe
*   Ordering requirements: Some functions depend on others (e.g., `get_project_root` is used by other path functions)
*   Initialization prerequisites: Functions that access configuration files expect the project structure to be established

---

## Files

- [`cache.py`](utils/cache.md)
- [`common.py`](utils/common.md)
- [`compat.py`](utils/compat.md)
- [`dataframe.py`](utils/dataframe.md)
- [`imghdr_patch.py`](utils/imghdr_patch.md)
- [`notebook.py`](utils/notebook.md)
- [`paths.py`](utils/paths.md)
- [`progress_bar.py`](utils/progress_bar.md)
- [`versions.py`](utils/versions.md)

