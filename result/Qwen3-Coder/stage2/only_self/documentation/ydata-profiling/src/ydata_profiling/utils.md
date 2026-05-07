# `src.ydata_profiling.utils`

## Tree:
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

## Role:
    Provides foundational utility functions that support core data profiling operations across the ydata-profiling library.

## Description:
    The utils module serves as a centralized repository of helper functions and utilities that support the main data profiling functionality throughout the ydata-profiling library. It encapsulates common operations needed across different parts of the system, such as file I/O, data transformation, version compatibility checks, and system integration.

    This module is consumed by various other modules in the ydata_profiling package, including the main profiling engine, report generation components, and data processing pipelines. The utilities are designed to be reusable, well-tested, and focused on solving common problems encountered during data analysis and profiling workflows.

    The module is organized around functional areas:
    - File and data handling utilities (cache, dataframe) - for managing data sources and transformations
    - System and environment utilities (paths, notebook) - for path resolution and notebook integration  
    - Compatibility and version management (compat, versions) - for maintaining pandas version compatibility
    - Common helper functions (common, progress_bar) - for general-purpose operations and user experience
    - Image header detection patches (imghdr_patch) - for enhanced image file type detection

## Components:
    - **cache.py**: Provides caching mechanisms for remote files and zipped archives to avoid repeated network requests and improve performance
    - **common.py**: Contains general-purpose utility functions for data processing, timestamp conversion, and file type detection
    - **compat.py**: Handles pandas version compatibility checks and utilities to maintain backward compatibility
    - **dataframe.py**: Offers DataFrame-specific utilities for data transformation, file reading, and structural manipulation
    - **imghdr_patch.py**: Extends Python's imghdr module with additional JPEG detection functions for robust image file identification
    - **notebook.py**: Contains utilities for Jupyter notebook integration and display optimization
    - **paths.py**: Provides path resolution utilities for configuration files, data directories, and template locations
    - **progress_bar.py**: Offers progress tracking decorators for long-running operations to improve user experience
    - **versions.py**: Manages version checking and compatibility utilities for pandas to ensure feature availability

## Public API:
    - **cache.cache_file(file_name: str, url: str) -> Path**: Downloads and caches remote files to local storage, avoiding repeated network requests for frequently accessed data
    - **cache.cache_zipped_file(file_name: str, url: str) -> Path**: Downloads and caches zipped files from URLs, extracting specific entries for efficient data access
    - **common.convert_timestamp_to_datetime(timestamp: int) -> datetime**: Converts Unix timestamps to datetime objects, handling both positive and negative timestamps for date/time operations
    - **common.extract_zip(outfile: str, effective_path: str) -> None**: Extracts contents from ZIP archives with enhanced error handling for robust file processing
    - **common.test_jpeg1(h: bytes, f: Optional[file-like object]) -> Optional[str]**: Tests if a file header contains JFIF signature to identify JPEG image files for image type detection
    - **common.test_jpeg2(h: bytes, f: str) -> Optional[str]**: Tests if a file header corresponds to a JPEG image format using binary signature matching for reliable JPEG detection
    - **common.test_jpeg3(h: bytes, f: Any) -> Optional[str]**: Determines if a byte sequence represents a JPEG image file by checking for valid JPEG file signatures for comprehensive image identification
    - **common.update(d: dict, u: Mapping) -> dict**: Recursively updates dictionaries with deep merging for configuration management and nested data structures
    - **compat.pandas_version_info() -> Tuple[int, ...]**: Extracts and returns the major, minor, and patch version numbers of the installed pandas library as a tuple for compatibility checks
    - **dataframe.expand_mixed(df: pandas.DataFrame, types: Optional[Any] = None) -> pandas.DataFrame**: Expands DataFrame columns containing list, dict, or tuple values into separate columns for easier analysis and processing
    - **dataframe.hash_dataframe(df: pd.DataFrame) -> str**: Computes a stable SHA256 hash of a pandas DataFrame for identification, caching, and change detection purposes
    - **dataframe.is_supported_compression(file_extension: str) -> bool**: Determines whether a given file extension corresponds to a supported compression format for file handling
    - **dataframe.read_pandas(file_name: Path) -> pd.DataFrame**: Unified file reader for various data formats that automatically detects and handles different file extensions for flexible data ingestion
    - **dataframe.remove_suffix(text: str, suffix: str) -> str**: Removes a specified suffix from a string if it exists at the end of the string for clean data processing
    - **dataframe.rename_index(df: pandas.DataFrame) -> pandas.DataFrame**: Renames columns and index names in a DataFrame that are named "index" to "df_index" to prevent naming conflicts
    - **dataframe.slugify(value: str, allow_unicode: bool = False) -> str**: Converts a string into a URL-safe slug for creating safe filenames, URL segments, or identifier names
    - **dataframe.sort_column_names(dct: dict, sort: Optional[str] = None) -> dict**: Sorts dictionary items by their keys in ascending or descending order for consistent data presentation
    - **dataframe.uncompressed_extension(file_name: Path) -> str**: Extracts the base file extension by removing compression suffixes from compressed files to identify underlying file formats
    - **dataframe.warn_read(extension: str) -> None**: Function that issues a warning about reading files with a specific extension (currently has syntax error)
    - **imghdr_patch.test_jpeg1(h: bytes, f: file-like object) -> Optional[str]**: Tests for JPEG image format by checking for JFIF signature in the header bytes for enhanced image detection
    - **imghdr_patch.test_jpeg2(h: bytes, f: file-like object) -> Optional[str]**: Tests if a given header matches JPEG image format by checking specific byte patterns and offsets for robust JPEG identification
    - **imghdr_patch.test_jpeg3(h: bytes, f: file-like object or None) -> Optional[str]**: Tests if a byte sequence represents a JPEG image file by checking for JFIF/Exif markers or SOI marker for comprehensive image format detection
    - **notebook.full_width() -> None**: Sets Jupyter notebook container width to 100% by injecting CSS styling for optimal report display in notebook environments
    - **paths.get_config(file_name: str) -> Path**: Returns a Path object pointing to a configuration file relative to the module's parent directory for consistent configuration access
    - **paths.get_data_path() -> Path**: Returns the absolute path to the project's data directory for standardized data file access
    - **paths.get_html_template_path() -> Path**: Returns the absolute path to the HTML template directory used for report generation for consistent report formatting
    - **paths.get_project_root() -> Path**: Returns the absolute path to the project root directory by traversing up four parent directories from the current file location for portable path resolution
    - **progress_bar.progress(fn: Callable, bar: tqdm, message: str) -> Callable**: Decorator that wraps a function to update a progress bar with a message before execution and increment after completion for user experience improvement
    - **versions.is_pandas_1() -> bool**: Determines whether the installed pandas library is version 1.x for version-specific feature compatibility
    - **versions.pandas_major_version() -> int**: Returns the major version number of the installed pandas library for version checking
    - **versions.pandas_version() -> list[int]**: Returns the pandas library version as a list of integer components for easy version comparison and validation

## Dependencies:
    - Internal imports:
        - `src.ydata_profiling.utils.paths` - for path resolution utilities to locate configuration and data files
        - `src.ydata_profiling.utils.compat` - for pandas version compatibility to ensure feature availability
        - `src.ydata_profiling.utils.dataframe` - for DataFrame utilities to process tabular data
    - External imports:
        - `pathlib` - for path manipulation to handle file system paths consistently
        - `shutil` - for file operations to perform file copying and management
        - `urllib` - for URL handling and network requests to access remote resources
        - `zipfile` - for ZIP file handling to process compressed data archives
        - `pandas` - for DataFrame operations and version checking to work with tabular data
        - `tqdm` - for progress bar functionality to provide user feedback during long operations
        - `importlib.metadata` - for package version inspection to check installed package versions
        - `warnings` - for issuing warnings to notify users of potential issues
        - `IPython.core.display` - for Jupyter notebook integration to enhance notebook experiences

## Constraints:
    - All path-related functions assume standard project directory structure for predictable path resolution
    - Version checking functions require pandas to be installed for accurate version information
    - File operations require appropriate filesystem permissions for successful file access
    - Progress bar utilities require valid tqdm progress bar instances for proper functionality
    - JPEG detection functions expect specific byte patterns in image headers for accurate detection
    - Cache functions require network connectivity for downloads (when needed) for remote resource access
    - Thread safety: Most utilities are stateless and thread-safe, except those that modify global state (like imghdr patching) for predictable behavior

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

