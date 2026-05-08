# `src.ydata_profiling.controller`

## Tree:
controller/
├── console.py
└── pandas_decorator.py

## Role:
Coordinates the execution flow and provides entry points for data profiling functionality.

## Description:
The controller module serves as the coordination layer that manages the interaction between user interfaces (command-line and programmatic) and the core profiling logic. It handles argument parsing, command-line interface orchestration, and provides convenient factory methods for creating profiling reports. This module ensures that the profiling workflow is properly orchestrated regardless of how it's invoked.

## Components:
- main(args: Optional[List[Any]] = None) -> None: Entry point for command-line interface that processes arguments, loads data, and generates reports
- parse_args(args: Optional[List[Any]] = None) -> argparse.Namespace: Parses command-line arguments for configuring report generation
- profile_report(df: DataFrame, **kwargs) -> ProfileReport: Factory method for creating ProfileReport instances from pandas DataFrames

## Public API:
- main(args: Optional[List[Any]] = None) -> None: Command-line entry point for generating profiling reports. Processes command-line arguments, loads data from input file, creates a ProfileReport, and saves it to an output file.
- parse_args(args: Optional[List[Any]] = None) -> argparse.Namespace: Parses command-line arguments for configuring report generation. Defines available options for file paths, configuration settings, and reporting modes.
- profile_report(df: DataFrame, **kwargs) -> ProfileReport: Creates ProfileReport instances for exploratory data analysis from pandas DataFrames. Acts as a factory method that encapsulates ProfileReport instantiation logic.

## Dependencies:
- Internal: Uses `ydata_profiling.readers.pandas.read_pandas` for data loading
- Internal: Uses `ydata_profiling.report.ProfileReport` for report generation
- External: `argparse` for command-line argument parsing
- External: `sys` for accessing command-line arguments

## Constraints:
- Command-line arguments must be properly formatted and valid
- Input files must be readable and contain valid tabular data
- ProfileReport creation requires valid DataFrame input or lazy initialization
- All configuration parameters must be compatible with ProfileReport constructor requirements

---

## Files

- [`console.py`](controller/console.md)
- [`pandas_decorator.py`](controller/pandas_decorator.md)

