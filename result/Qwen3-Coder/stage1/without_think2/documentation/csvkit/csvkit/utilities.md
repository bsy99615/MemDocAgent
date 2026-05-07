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
Provides command-line utilities for processing CSV files with standardized interfaces and argument parsing.

## Description:
The utilities module contains a collection of command-line tools designed to manipulate and transform CSV data. Each utility implements a specific operation such as filtering, sorting, joining, or converting CSV files. These tools share common patterns for argument handling, input/output processing, and error reporting, making them part of a cohesive CLI toolkit.

This module serves as the entry point for various CSV processing operations and is consumed by the main csvkit command-line interface. It groups related functionality under a unified framework that allows users to chain operations or execute individual transformations on CSV datasets.

## Components:
- csvclean.py: Cleans CSV data by detecting and fixing formatting issues.
- csvcut.py: Selects specific columns from CSV files.
- csvformat.py: Processes and reformats CSV data according to specified command-line arguments, handling input from files or stdin with optional header row management and line skipping.
- csvgrep.py: Filters rows based on regular expression matches in specified columns.
- csvjoin.py: Joins multiple CSV files horizontally or vertically.
- csvjson.py: Converts CSV data to JSON format.
- csvlook.py: Displays CSV data in a formatted table view.
- csvpy.py: Loads a CSV file into a Python object and drops the user into an interactive Python shell for exploration and analysis.
- csvsort.py: Sorts CSV data by one or more columns.
- csvsql.py: Converts CSV data to SQL statements or queries a database.
- csvstack.py: Stacks multiple CSV files vertically, optionally adding group identifiers.
- csvstat.py: Computes statistics over CSV data.
- in2csv.py: Converts various tabular formats to CSV.
- sql2csv.py: Converts SQL query results back to CSV format.

## Public API:
- csvclean: Command-line utility for cleaning CSV data.
- csvcut: Command-line utility for selecting columns from CSV data.
- csvformat: Command-line utility for reformatting CSV data.
- csvgrep: Command-line utility for filtering CSV data via regex.
- csvjoin: Command-line utility for joining CSV files.
- csvjson: Command-line utility for converting CSV to JSON.
- csvlook: Command-line utility for displaying CSV in table form.
- csvpy: Command-line utility for applying Python expressions to CSV data.
- csvsort: Command-line utility for sorting CSV data.
- csvsql: Command-line utility for working with CSV and SQL.
- csvstack: Command-line utility for stacking CSV files.
- csvstat: Command-line utility for computing statistics on CSV data.
- in2csv: Command-line utility for converting input formats to CSV.
- sql2csv: Command-line utility for converting SQL results to CSV.

## Dependencies:
- Internal: csvkit/arguments.py (for argument parsing), csvkit/core.py (for core CSV processing), csvkit/exceptions.py (for custom exceptions)
- External: argparse (for command-line argument parsing), csv (standard library for CSV handling), sys (for system-level operations)

## Constraints:
- All utilities must be invoked through the command-line interface.
- Utilities expect standard input/output streams unless redirected.
- Input files must be valid CSV or compatible formats.
- Utilities should handle errors gracefully and provide informative messages.

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

