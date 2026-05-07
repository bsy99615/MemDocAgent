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
└── in2csv.py
└── sql2csv.py

## Role:
Command-line interface utilities for CSV data manipulation and analysis

## Description:
This module provides a collection of command-line utilities for processing CSV files. Each utility implements a specific CSV operation such as cleaning, filtering, joining, sorting, and conversion between different formats. These tools are designed to be used independently or chained together in shell pipelines for powerful CSV data processing workflows.

Primary consumers include:
- Command-line interfaces that invoke these utilities
- Shell scripts that chain multiple CSV operations
- Data processing pipelines that require CSV manipulation

These components are grouped together because they all serve the common purpose of CSV data manipulation and transformation, forming the core user-facing interface of the csvkit toolkit.

## Components:
- csvclean.py: Clean CSV data by detecting and fixing common formatting issues
- csvcut.py: Select specific columns from CSV files
- csvformat.py: Convert CSV files between different formats and encodings
- csvgrep.py: Filter CSV rows based on pattern matching in specified columns
- csvjoin.py: Join multiple CSV files horizontally or vertically
- csvjson.py: Convert CSV data to JSON format
- csvlook.py: Display CSV data in a formatted table view
- csvpy.py: Execute Python expressions on CSV data
- csvsort.py: Sort CSV data by one or more columns
- csvsql.py: Convert CSV files to SQL statements or execute queries
- csvstack.py: Stack multiple CSV files vertically
- csvstat.py: Calculate statistics for CSV data
- in2csv.py: Convert various tabular data formats to CSV
- sql2csv.py: Convert SQL query results back to CSV format

## Public API:
- csvclean: Command-line utility for cleaning CSV data
- csvcut: Command-line utility for selecting CSV columns  
- csvformat: Command-line utility for CSV format conversion
- csvgrep: Command-line utility for filtering CSV rows
- csvjoin: Command-line utility for joining CSV files
- csvjson: Command-line utility for converting CSV to JSON
- csvlook: Command-line utility for displaying CSV in table format
- csvpy: Command-line utility for executing Python expressions on CSV data
- csvsort: Command-line utility for sorting CSV data
- csvsql: Command-line utility for SQL operations on CSV files
- csvstack: Command-line utility for stacking CSV files
- csvstat: Command-line utility for calculating CSV statistics
- in2csv: Command-line utility for converting various formats to CSV
- sql2csv: Command-line utility for converting SQL results to CSV

## Dependencies:
Internal:
- csvkit: Core csvkit functionality and shared utilities
- csvkit.exceptions: Exception handling for CSV operations
- csvkit.configuration: Configuration management

External:
- argparse: Command-line argument parsing
- sys: System-specific parameters and functions
- io: Text I/O operations
- csv: Standard library CSV processing
- json: JSON serialization/deserialization

## Constraints:
- All utilities expect properly formatted CSV input or handle appropriate error conditions
- Utilities should be invoked via command-line interface, not directly as Python functions
- Input/output streams must be properly managed for large datasets
- Utilities should handle encoding properly and provide options for specifying character encodings
- Thread safety is not required as utilities are designed for sequential command-line execution

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

