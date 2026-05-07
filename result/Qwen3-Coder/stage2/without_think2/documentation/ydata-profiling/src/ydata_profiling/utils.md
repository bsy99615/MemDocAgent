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
Provides low-level utility functions and shared helpers for data profiling operations, including file handling, data manipulation, path resolution, and compatibility checks.

## Description:
The `utils` module serves as a collection of foundational utilities that support various aspects of the data profiling workflow. It contains functions for managing file caching, manipulating data structures, handling different data formats, resolving paths, and ensuring compatibility across different Python and library versions. These utilities are designed to be reused across different parts of the profiling system, promoting code consistency and reducing duplication.

This module is organized into several submodules, each focusing on a specific category of utilities:
- `cache.py`: File caching mechanisms for remote data
- `common.py`: General-purpose helper functions and data transformations
- `compat.py`: Version compatibility checks and utilities
- `dataframe.py`: DataFrame-specific operations and file readers
- `imghdr_patch.py`: Image header detection enhancements
- `notebook.py`: Jupyter notebook integration utilities
- `paths.py`: Path resolution and management functions
- `progress_bar.py`: Progress tracking decorators
- `versions.py`: Library version checking utilities

## Components:
*   **cache.py**: Functions for caching remote files and zipped archives locally
*   **common.py**: Generic helpers like timestamp conversion, dictionary updates, and JPEG format detection
*   **compat.py**: Utilities for checking pandas version compatibility
*   **dataframe.py**: DataFrame manipulation and file reading utilities
*   **imghdr_patch.py**: Enhanced JPEG image detection functions
*   **notebook.py**: Jupyter notebook display configuration
*   **paths.py**: Path resolution functions for project root, data directory, and templates
*   **progress_bar.py**: Progress tracking decorator for tqdm
*   **versions.py**: Library version checking functions

## Public API:
*   `cache.cache_file(file_name: str, url: str) -> Path`: Downloads and caches a remote file
*   `cache.cache_zipped_file(file_name: str, url: str) -> Path`: Downloads and caches a file from a zipped archive
*   `common.convert_timestamp_to_datetime(timestamp: int) -> datetime`: Converts Unix timestamp to datetime object
*   `common.extract_zip(outfile: str, effective_path: str) -> None`: Extracts a ZIP archive to a directory
*   `common.test_jpeg1(h: bytes, f: Any) -> str or None`: Tests JPEG format using JFIF signature
*   `common.test_jpeg2(h: bytes, f: file-like object or None) -> str`: Tests JPEG format using header bytes
*   `common.test_jpeg3(h: bytes, f: Any) -> str`: Tests JPEG format using multiple signature patterns
*   `common.update(d: dict, u: Mapping) -> dict`: Recursively updates a dictionary with another mapping
*   `compat.pandas_version_info() -> Tuple[int, ...]`: Returns pandas version as tuple of integers
*   `dataframe.expand_mixed(df: pd.DataFrame, types: Any = None) -> pd.DataFrame`: Expands mixed-type columns in DataFrame
*   `dataframe.hash_dataframe(df: pd.DataFrame) -> str`: Generates SHA256 hash of DataFrame content
*   `dataframe.is_supported_compression(file_extension: str) -> bool`: Checks if file extension is a supported compression format
*   `dataframe.read_pandas(file_name: Path) -> pd.DataFrame`: Reads data file into pandas DataFrame
*   `dataframe.remove_suffix(text: str, suffix: str) -> str`: Removes suffix from end of string
*   `dataframe.rename_index(df: pd.DataFrame) -> pd.DataFrame`: Renames 'index' column/index name to 'df_index'
*   `dataframe.slugify(value: str, allow_unicode: bool = False) -> str`: Converts string to URL-friendly slug
*   `dataframe.sort_column_names(dct: dict, sort: Optional[str]) -> dict`: Sorts dictionary items by column names
*   `dataframe.uncompressed_extension(file_name: Path) -> str`: Returns uncompressed file extension
*   `dataframe.warn_read(extension: str) -> None`: Issues deprecation warning for unsupported file extensions
*   `imghdr_patch.test_jpeg1(h: bytes, f: Any) -> str or None`: Tests JPEG format using JFIF signature (patched)
*   `imghdr_patch.test_jpeg2(h: bytes, f: file-like object) -> str or None`: Tests JPEG format using header markers (patched)
*   `imghdr_patch.test_jpeg3(h: bytes, f: file-like object) -> str or None`: Tests JPEG format using multiple patterns (patched)
*   `notebook.full_width() -> None`: Configures Jupyter notebook for full-width display
*   `paths.get_config(file_name: str) -> Path`: Resolves path to configuration file
*   `paths.get_data_path() -> Path`: Returns path to project's data directory
*   `paths.get_html_template_path() -> Path`: Returns path to HTML templates directory
*   `paths.get_project_root() -> Path`: Returns path to project root directory
*   `progress_bar.progress(fn: Callable, bar: tqdm, message: str) -> Callable`: Decorator for progress bar updates
*   `versions.is_pandas_1() -> bool`: Checks if pandas version is 1.x
*   `versions.pandas_major_version() -> int`: Returns major version of pandas
*   `versions.pandas_version() -> list[int]`: Returns pandas version as list of integers

## Dependencies:
*   **Internal imports**:
    *   `src.ydata_profiling.utils.cache`: Provides file caching utilities
    *   `src.ydata_profiling.utils.common`: Provides general-purpose helpers
    *   `src.ydata_profiling.utils.compat`: Provides compatibility utilities
    *   `src.ydata_profiling.utils.dataframe`: Provides DataFrame utilities
    *   `src.ydata_profiling.utils.imghdr_patch`: Provides patched image detection
    *   `src.ydata_profiling.utils.notebook`: Provides notebook integration
    *   `src.ydata_profiling.utils.paths`: Provides path resolution utilities
    *   `src.ydata_profiling.utils.progress_bar`: Provides progress tracking
    *   `src.ydata_profiling.utils.versions`: Provides version checking utilities
*   **External imports**:
    *   `pathlib`: For path manipulation and object creation
    *   `tqdm`: For progress bar functionality
    *   `importlib.metadata`: For retrieving package version information
    *   `pandas`: For DataFrame operations and version checking
    *   `shutil`: For file copying operations
    *   `urllib.error`: For handling URL-related errors
    *   `zipfile`: For ZIP archive handling
    *   `warnings`: For issuing deprecation warnings
    *   `datetime`: For timestamp conversion
    *   `collections.abc`: For abstract base classes in dictionary updates
    *   `IPython.core.display`: For Jupyter notebook styling

## Constraints:
*   Callers must ensure that all file paths are valid and accessible
*   When using version checking functions, pandas must be installed
*   Progress bar decorators require a valid tqdm instance
*   File caching functions require network connectivity when downloading
*   All path resolution functions assume standard project directory structures
*   Thread safety is not guaranteed for functions that modify global state or file systems

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

