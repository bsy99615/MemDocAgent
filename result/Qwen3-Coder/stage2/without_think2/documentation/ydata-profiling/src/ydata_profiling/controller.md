# `src.ydata_profiling.controller`

## Tree:
controller/
├── console.py
└── pandas_decorator.py

## Role:
Manages the execution flow and interfaces for the ydata-profiling console application.

## Description:
The controller module serves as the central coordination layer for the ydata-profiling system, managing the interaction between user inputs, data processing, and report generation. It provides two main functional areas: console argument parsing and simplified report creation utilities.

This module maintains clean separation between input handling, data processing, and output generation, promoting modularity, testability, and reusability. It acts as the bridge between the command-line interface and the core profiling engine, while also offering convenient APIs for programmatic usage.

## Components:
*   `console.main(args: Optional[List[Any]] = None)` - Main entry point for the console application that orchestrates the complete profiling workflow from argument parsing to report generation and file output.
*   `console.parse_args(args: Optional[List[Any]] = None)` - Parses command-line arguments for configuring the profiling process and report settings.
*   `pandas_decorator.profile_report(df: DataFrame, **kwargs)` - Simplified interface for creating ProfileReport instances from pandas DataFrames with optional configuration.

## Public API:
*   `main(args: Optional[List[Any]] = None)` - Entry point for the console application. Accepts command-line arguments and executes the full profiling workflow.
*   `parse_args(args: Optional[List[Any]] = None)` - Parses command-line arguments into a structured namespace for configuration.
*   `profile_report(df: DataFrame, **kwargs)` - Creates a ProfileReport instance from a pandas DataFrame with optional configuration.

## Dependencies:
*   Internal: `src.ydata_profiling.utils` (for file reading utilities)
*   Internal: `src.ydata_profiling.report` (for ProfileReport class)
*   External: `argparse` (for command-line argument parsing)
*   External: `pandas` (for DataFrame handling)
*   External: `pathlib` (for path manipulation)

## Constraints:
*   Callers must ensure that input files are readable and output files are writable.
*   When using `config_file`, the `minimal` parameter cannot also be set to True.
*   Time-series mode is not supported with Spark DataFrames.
*   The module assumes that all internal components are properly initialized and available.

---

## Files

- [`console.py`](controller/console.md)
- [`pandas_decorator.py`](controller/pandas_decorator.md)

