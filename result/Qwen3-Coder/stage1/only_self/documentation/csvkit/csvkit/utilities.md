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
Command-line utilities for CSV data processing and transformation

## Description:
This module provides a collection of command-line utilities that enable users to perform various operations on CSV files. Each utility implements a specific CSV processing task, following Unix philosophy of creating small, focused tools that can be combined for complex data workflows. These utilities form the core interface for csvkit's CSV processing capabilities and are invoked through the main csvkit command-line program.

The utilities share common infrastructure for argument parsing, input/output handling, and error reporting, while implementing distinct CSV processing operations such as cleaning, filtering, transformation, analysis, and conversion. They are designed to work seamlessly with standard input/output streams and support piping in shell environments.

## Components:
*   **csvclean** - Detects and fixes common CSV formatting issues like unclosed quotes, malformed lines, and inconsistent quoting
*   **csvcut** - Extracts and selects specific columns from CSV files, supporting column ranges (e.g., "1-3"), names (e.g., "name,email"), and positional selection
*   **csvformat** - Reformats CSV files with customizable delimiter, quote character, escape character, and encoding settings
*   **csvgrep** - Filters CSV rows based on regular expression patterns in specified columns, supporting case-insensitive matching and inverted filtering
*   **csvjoin** - Joins multiple CSV files horizontally on common key columns, supporting inner, outer, and left joins
*   **csvjson** - Converts CSV data to JSON format with configurable output styles including arrays of objects, arrays of arrays, and streaming formats
*   **csvlook** - Displays CSV data in a formatted ASCII table for easy viewing, automatically adjusting column widths
*   **csvpy** - Evaluates Python expressions on CSV data row-by-row, enabling complex transformations and calculations
*   **csvsort** - Sorts CSV files by one or more columns in ascending or descending order, supporting numeric and string sorting
*   **csvsql** - Converts CSV files to SQL INSERT statements or executes SQL queries on CSV data using SQLite backend
*   **csvstack** - Stacks multiple CSV files vertically (concatenates rows) with optional header handling and validation
*   **csvstat** - Computes statistical summaries including count, mean, median, min, max, standard deviation, and quartiles for numeric columns
*   **in2csv** - Converts various tabular formats (XLS, XLSX, JSON, etc.) to CSV format with automatic schema detection
*   **sql2csv** - Converts SQL query results back to CSV format, supporting connection to various database systems

## Public API:
*   **csvclean** - Command-line utility that cleans CSV files by detecting and fixing formatting issues
*   **csvcut** - Command-line utility for selecting specific columns from CSV files
*   **csvformat** - Command-line utility for changing CSV formatting parameters
*   **csvgrep** - Command-line utility for filtering CSV rows using regular expressions
*   **csvjoin** - Command-line utility for joining CSV files on common columns
*   **csvjson** - Command-line utility for converting CSV to JSON format
*   **csvlook** - Command-line utility for displaying CSV data in formatted tables
*   **csvpy** - Command-line utility for applying Python expressions to CSV data
*   **csvsort** - Command-line utility for sorting CSV files by column values
*   **csvsql** - Command-line utility for SQL operations on CSV data
*   **csvstack** - Command-line utility for vertically concatenating CSV files
*   **csvstat** - Command-line utility for computing statistical summaries of CSV data
*   **in2csv** - Command-line utility for converting various formats to CSV
*   **sql2csv** - Command-line utility for converting SQL query results to CSV

## Dependencies:
*   **Internal**: csvkit/core - Core CSV processing and parsing functionality
*   **Internal**: csvkit/exceptions - Custom exception handling for CSV operations
*   **Internal**: csvkit/config - Configuration management for utilities
*   **External**: argparse - Command-line argument parsing and help generation
*   **External**: sys - System-specific parameters and functions
*   **External**: csv - Standard library CSV reader/writer
*   **External**: json - Standard library JSON processing
*   **External**: sqlite3 - Database connectivity for csvsql utility
*   **External**: re - Regular expression support for csvgrep
*   **External**: xlrd, openpyxl - Excel file support for in2csv
*   **External**: pandas - Data frame support for some conversions in in2csv

## Constraints:
*   All utilities must be invoked through the csvkit command-line interface
*   Input files must be readable and output destinations must be writable
*   Utilities process data sequentially and are not thread-safe
*   Some utilities require additional dependencies (sqlite3 for csvsql, xlrd/openpyxl for Excel files)
*   Utilities assume UTF-8 encoding by default unless specified otherwise
*   Column indices in csvcut and csvsort are 1-based, not 0-based
*   CSV files should be properly formatted for best results with all utilities

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

