# `onlinejudge_command`

## Tree:
    onlinejudge_command/
    ├── download_history.py
    ├── format_utils.py
    ├── log_formatter.py
    ├── output_comparators.py
    ├── pretty_printers.py
    ├── update_checking.py
    └── utils.py

## Role:
    Provides command-line interface utilities and helper functions for online judge operations

## Description:
    The onlinejudge_command module serves as a collection of utility functions and classes that support the command-line interface functionality of the online judge system. This module encapsulates various helper components that facilitate common operations in the CLI environment, such as output formatting, logging, result comparison, and user interaction. The module follows a clear separation of concerns where each submodule addresses a specific aspect of command-line operation management.

## Components:
    * download_history.py - Manages persistent storage and retrieval of problem download history
    * format_utils.py - Provides formatting utilities for command-line output and display
    * log_formatter.py - Implements custom logging formatters for structured command-line output
    * output_comparators.py - Contains utilities for comparing program outputs against expected results
    * pretty_printers.py - Offers enhanced pretty printing capabilities for data structures in CLI
    * update_checking.py - Handles checking for updates to the online judge tools and notifying users
    * utils.py - General utility functions used throughout the command-line interface operations

## Public API:
    * download_history.py - Functions for saving, loading, and managing problem download records
    * format_utils.py - Formatting functions for CLI output, including alignment and color handling
    * log_formatter.py - Custom formatter classes for consistent logging output in command-line tools
    * output_comparators.py - Comparison functions for verifying program outputs against expected results
    * pretty_printers.py - Enhanced printing functions for displaying structured data in CLI
    * update_checking.py - Update checking mechanisms and notification utilities
    * utils.py - General-purpose utilities supporting various CLI operations

## Dependencies:
    * Internal imports: None (this is a standalone module)
    * External imports: Standard library modules (logging, json, os, sys) and potentially third-party CLI libraries

## Constraints:
    * All functions should be thread-safe for concurrent command execution
    * Utilities must maintain backward compatibility with existing CLI commands
    * Output formatting functions should handle various terminal sizes gracefully
    * Logging formatters must be compatible with the main application's logging configuration

---

## Files

- [`download_history.py`](onlinejudge_command/download_history.md)
- [`format_utils.py`](onlinejudge_command/format_utils.md)
- [`log_formatter.py`](onlinejudge_command/log_formatter.md)
- [`output_comparators.py`](onlinejudge_command/output_comparators.md)
- [`pretty_printers.py`](onlinejudge_command/pretty_printers.md)
- [`update_checking.py`](onlinejudge_command/update_checking.md)
- [`utils.py`](onlinejudge_command/utils.md)

