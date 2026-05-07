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
Provides a collection of low-level utility functions and classes that support core functionality across the profiling system, including file caching, data manipulation, compatibility handling, and infrastructure utilities.

## Description:
This module serves as a centralized location for reusable utility functions and classes that are used throughout the ydata-profiling system. It encapsulates common operations that don't belong to any specific domain but are essential for the proper functioning of the profiling pipeline. The module is organized around logical groupings of functionality to maintain clean separation of concerns while providing easy access to commonly needed utilities.

Primary consumers of this module include:
- The main profiling engine for data processing and validation
- Report generation components for formatting and presentation
- File I/O operations for reading datasets
- Compatibility layers for supporting different pandas versions

The cohesive principle behind this module is that all components share the common characteristic of being general-purpose utilities that support the core profiling workflow rather than implementing domain-specific logic.

## Components:
- **cache.py**: Provides caching mechanisms for downloading and managing remote files
- **common.py**: Contains general-purpose utility functions for data processing and image handling
- **compat.py**: Offers compatibility utilities for handling different pandas versions and library features
- **dataframe.py**: Contains utilities for dataframe manipulation, reading, and validation
- **imghdr_patch.py**: Patches image header detection for improved JPEG recognition
- **notebook.py**: Provides utilities for Jupyter notebook integration and display
- **paths.py**: Manages project and configuration file paths
- **progress_bar.py**: Implements progress tracking utilities for long-running operations
- **versions.py**: Handles version checking and compatibility verification

## Public API:
- **cache.cache_file**: Download and cache a file from a URL to a local path
- **cache.cache_zipped_file**: Download and cache a zipped file from a URL, extracting it to a local path
- **common.convert_timestamp_to_datetime**: Convert Unix timestamp to datetime object
- **common.extract_zip**: Extract a ZIP archive to a specified directory
- **common.test_jpeg1**, **common.test_jpeg2**, **common.test_jpeg3**: JPEG image header detection functions
- **common.update**: Recursively update nested dictionaries
- **compat.pandas_version_info**: Get pandas version information as tuple
- **dataframe.expand_mixed**: Expand mixed-type columns in a DataFrame
- **dataframe.hash_dataframe**: Generate SHA256 hash of a DataFrame
- **dataframe.is_supported_compression**: Check if file extension is a supported compression format
- **dataframe.read_pandas**: Read various file formats into a pandas DataFrame
- **dataframe.remove_suffix**: Remove suffix from string
- **dataframe.rename_index**: Rename index column to avoid conflicts
- **dataframe.slugify**: Convert string to URL-friendly slug
- **dataframe.sort_column_names**: Sort dictionary keys by column names
- **dataframe.uncompressed_extension**: Get uncompressed file extension
- **dataframe.warn_read**: Issue warning about unsupported file format
- **imghdr_patch.test_jpeg1**, **imghdr_patch.test_jpeg2**, **imghdr_patch.test_jpeg3**: JPEG image header detection functions (patched)
- **notebook.full_width**: Set Jupyter notebook display to full width
- **paths.get_config**: Get path to configuration file
- **paths.get_data_path**: Get path to data directory
- **paths.get_html_template_path**: Get path to HTML template directory
- **paths.get_project_root**: Get root directory of the project
- **progress_bar.progress**: Wrap function with progress bar tracking
- **versions.is_pandas_1**: Check if pandas version is 1.x
- **versions.pandas_major_version**: Get major version of pandas
- **versions.pandas_version**: Get pandas version as list of integers

## Dependencies:
- Internal imports:
  - `src.ydata_profiling.utils.paths` - for path management utilities
  - `src.ydata_profiling.utils.compat` - for pandas version compatibility
  - `src.ydata_profiling.utils.dataframe` - for dataframe utilities
- External imports:
  - `requests` - for HTTP requests in cache utilities
  - `zipfile` - for ZIP file handling
  - `pandas` - for DataFrame operations
  - `tqdm` - for progress bar functionality
  - `pathlib` - for path manipulation
  - `warnings` - for issuing warnings
  - `hashlib` - for generating hashes
  - `unicodedata` - for Unicode normalization
  - `re` - for regular expressions
  - `collections.abc` - for abstract base classes

## Constraints:
- All path-related functions require the project root to be properly configured
- Cache utilities assume network connectivity for remote downloads
- Progress bar utilities require a valid tqdm progress bar instance
- Version checking utilities depend on proper pandas installation
- Some functions like `read_pandas` may raise exceptions for unsupported file formats
- Thread safety is not guaranteed for stateful utilities like path managers

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

