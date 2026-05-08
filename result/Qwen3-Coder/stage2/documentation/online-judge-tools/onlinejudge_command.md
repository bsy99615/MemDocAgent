# `onlinejudge_command`

## Tree:
```
onlinejudge_command/
├── download_history.py
├── format_utils.py
├── log_formatter.py
├── output_comparators.py
├── pretty_printers.py
├── update_checking.py
└── utils.py
```

## Role:
Provides supporting utilities and helper functions for the onlinejudge command-line tool's command implementations.

## Description:
This module serves as a collection of cross-cutting utilities that support various command-line operations for interacting with online judges. It contains helper functions, formatters, and utilities that are commonly needed across different commands but don't belong in the core business logic.

The module is used primarily by the main command-line entry points and individual command implementations that require standardized utilities for:
- Managing persistent data (download history)
- Formatting output for users
- Comparing program outputs
- Handling logging and user feedback
- Checking for tool updates
- General command-line utilities

The cohesion is based on shared functionality needed across different command implementations rather than domain-specific logic.

## Components:
*   `download_history.py` - Manages persistent storage and retrieval of downloaded problem data and metadata
*   `format_utils.py` - Provides utilities for formatting output strings and data presentation  
*   `log_formatter.py` - Implements custom logging formatters for command-line interface output
*   `output_comparators.py` - Contains logic for comparing program outputs with expected results using various comparison methods
*   `pretty_printers.py` - Offers enhanced printing capabilities for structured data and command output
*   `update_checking.py` - Handles checking for updates to the onlinejudge tool itself
*   `utils.py` - General utility functions for command-line operations and common tasks

## Public API:
*   `download_history` - Interface for managing download history persistence and retrieval
*   `format_utils` - Utilities for formatting output and data presentation
*   `log_formatter` - Custom logging formatters for CLI output
*   `output_comparators` - Logic for comparing program outputs with expected results
*   `pretty_printers` - Enhanced printing capabilities for structured data
*   `update_checking` - Update checking functionality for the tool
*   `utils` - General utility functions for CLI operations

## Dependencies:
*   Internal: Standard library modules (os, json, logging, sys, pathlib, etc.)
*   External: Potentially requests for HTTP operations, rich for enhanced terminal output

## Constraints:
*   All components should be thread-safe for concurrent command execution
*   Utility functions should avoid side effects that interfere with command execution
*   Logging components must be configurable for different verbosity levels
*   Output comparison functions should handle various whitespace and newline variations
*   Update checking should not block command execution and must gracefully handle network failures
*   All utilities should work consistently across different operating systems

---

## Files

- [`download_history.py`](onlinejudge_command/download_history.md)
- [`format_utils.py`](onlinejudge_command/format_utils.md)
- [`log_formatter.py`](onlinejudge_command/log_formatter.md)
- [`output_comparators.py`](onlinejudge_command/output_comparators.md)
- [`pretty_printers.py`](onlinejudge_command/pretty_printers.md)
- [`update_checking.py`](onlinejudge_command/update_checking.md)
- [`utils.py`](onlinejudge_command/utils.md)

