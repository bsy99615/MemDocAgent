# `src.ydata_profiling.controller`

## Tree:
controller/
├── console.py
└── pandas_decorator.py

## Role:
Coordinates data profiling workflows through unified command-line and programmatic interfaces.

## Description:
The controller module implements the application's entry points and orchestration layer, providing both command-line and programmatic access to data profiling capabilities. This module serves as the boundary between user interaction and the core profiling engine, handling argument parsing, file I/O operations, and workflow coordination. The components are grouped together because they all facilitate the same fundamental operation—enabling data profiling—with different user interaction patterns (CLI vs. direct API usage).

## Components:
- main(args=None): Main command-line entry point that orchestrates the complete profiling workflow from argument parsing to report generation and output
- parse_args(args=None): Command-line argument parser that validates and normalizes user input for profiling configuration
- profile_report(df, **kwargs): Convenience wrapper for ProfileReport instantiation that enables easy DataFrame profiling with flexible configuration

## Public API:
- main(args=None): Command-line interface for generating profiling reports; processes file paths, configuration options, and output specifications
- parse_args(args=None): Parses command-line arguments into structured configuration for profiling operations
- profile_report(df, **kwargs): Programmatic interface for creating ProfileReport objects from pandas DataFrames with optional configuration

## Dependencies:
Internal:
- ydata_profiling.profile_report: Core profiling engine responsible for analysis and report generation
- ydata_profiling.config: Configuration management for profiling settings and behaviors
- ydata_profiling.utils: Utility functions for file operations, validation, and system interactions

External:
- argparse: Standard library for command-line argument parsing and validation
- sys: Standard library for system-level operations and argument handling
- pandas: Data manipulation library for DataFrame support and operations
- tqdm: Progress bar library for visualizing long-running operations
- webbrowser: Standard library for browser automation when opening reports

## Constraints:
- Command-line interface requires valid file paths with appropriate read/write permissions
- Programmatic interface requires valid pandas DataFrame inputs that meet profiling engine requirements
- All configuration parameters must be compatible with ProfileReport constructor interface
- Thread safety: Not guaranteed for concurrent execution due to potential global state interactions
- Input validation occurs at multiple layers: argument parsing, file operations, and profiling engine

---

## Files

- [`console.py`](controller/console.md)
- [`pandas_decorator.py`](controller/pandas_decorator.md)

