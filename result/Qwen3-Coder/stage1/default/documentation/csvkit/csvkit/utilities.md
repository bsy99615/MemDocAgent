# `csvkit.utilities`

## Tree:
utilities/
├── csvclean.py
├── csvcut.py
├── csvformat.py
├── csvgrep.py
├── csvjoin.py
├── csvjson.py
├── csvlook.py
├── csvpy.py
├── csvsort.py
├── csvsql.py
├── csvstack.py
├── csvstat.py
├── in2csv.py
└── sql2csv.py

## Role:
Provides command-line utilities for processing and transforming CSV data

## Description:
The utilities module serves as the command-line interface layer for csvkit, containing individual scripts that provide specific CSV processing capabilities. Each script in this module implements a distinct utility for working with CSV files, such as cleaning, filtering, joining, sorting, and converting CSV data to various formats.

This module acts as the primary entry point for users interacting with csvkit via the command line, providing a suite of tools that can be chained together for complex CSV processing workflows.

## Components:
*   **csvclean.py**: Cleans CSV files by detecting and fixing common formatting issues
*   **csvcut.py**: Selects specific columns from CSV files
*   **csvformat.py**: Converts CSV files to different formats and encodings
*   **csvgrep.py**: Filters CSV files based on various criteria including regular expressions, exact matches, and range conditions
*   **csvjoin.py**: Joins multiple CSV files together
*   **csvjson.py**: Converts CSV files into JSON or GeoJSON format with support for streaming, indentation, and geographic data
*   **csvlook.py**: Displays CSV files in a formatted table view
*   **csvpy.py**: Executes Python expressions on CSV data
*   **csvsort.py**: Sorts CSV files by specified columns
*   **csvsql.py**: Converts CSV files to SQL statements or executes SQL queries on them
*   **csvstack.py**: Stacks multiple CSV files into a single output file, optionally adding group identifiers to distinguish rows from different input files
*   **csvstat.py**: Computes statistical summaries of CSV files
*   **in2csv.py**: Converts various tabular data formats to CSV
*   **sql2csv.py**: Converts SQL query results back to CSV format

## Public API:
*   **csvclean** - Command-line utility for cleaning CSV files
*   **csvcut** - Command-line utility for selecting columns from CSV files
*   **csvformat** - Command-line utility for formatting CSV files
*   **csvgrep** - Command-line utility for filtering CSV files with various criteria
*   **csvjoin** - Command-line utility for joining CSV files
*   **csvjson** - Command-line utility for converting CSV to JSON/GeoJSON
*   **csvlook** - Command-line utility for displaying CSV in table format
*   **csvpy** - Command-line utility for executing Python expressions on CSV data
*   **csvsort** - Command-line utility for sorting CSV files
*   **csvsql** - Command-line utility for SQL operations on CSV files
*   **csvstack** - Command-line utility for stacking CSV files
*   **csvstat** - Command-line utility for computing statistics on CSV files
*   **in2csv** - Command-line utility for converting data formats to CSV
*   **sql2csv** - Command-line utility for converting SQL results to CSV

## Dependencies:
*   Internal: csvkit/core - Core CSV processing functionality
*   Internal: csvkit/exceptions - Custom exception handling
*   External: argparse - Command-line argument parsing
*   External: sys - System-specific parameters and functions
*   External: csv - Standard library CSV processing
*   External: json - JSON serialization/deserialization

## Constraints:
*   All utilities must be invoked via command-line interface
*   Utilities expect properly formatted CSV input unless otherwise noted
*   Utilities operate on standard input/output streams by default
*   Utilities should be thread-safe when processing independent files
*   Utilities require appropriate permissions to read input files and write output files

---

## Files

- [`csvclean.py`](utilities/csvclean.md)
- [`csvcut.py`](utilities/csvcut.md)
- [`csvformat.py`](utilities/csvformat.md)
- [`csvgrep.py`](utilities/csvgrep.md)
- [`csvjoin.py`](utilities/csvjoin.md)
- [`csvjson.py`](utilities/csvjson.md)
- [`csvlook.py`](utilities/csvlook.md)
- [`csvpy.py`](utilities/csvpy.md)
- [`csvsort.py`](utilities/csvsort.md)
- [`csvsql.py`](utilities/csvsql.md)
- [`csvstack.py`](utilities/csvstack.md)
- [`csvstat.py`](utilities/csvstat.md)
- [`in2csv.py`](utilities/in2csv.md)
- [`sql2csv.py`](utilities/sql2csv.md)

