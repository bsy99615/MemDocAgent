# `csvkit`

## Repository Overview

### Tree Structure
```
csvkit/
├── csvkit/
│   ├── convert/           # Conversion utilities and helpers
│   ├── utilities/         # Command-line CSV processing tools
│   │   ├── csvclean.py    # Clean CSV files by fixing row length issues
│   │   ├── csvcut.py      # Select columns from CSV files
│   │   ├── csvformat.py   # Format CSV files for better readability
│   │   ├── csvgrep.py     # Filter CSV files using pattern matching
│   │   ├── csvjoin.py     # Join multiple CSV files
│   │   ├── csvjson.py     # Convert CSV to JSON
│   │   ├── csvlook.py     # Display CSV files in a formatted table
│   │   ├── csvpy.py       # Execute Python expressions on CSV data
│   │   ├── csvsort.py     # Sort CSV files
│   │   ├── csvsql.py      # Convert CSV to SQL or execute SQL queries on CSV
│   │   ├── csvstack.py    # Stack CSV files vertically
│   │   ├── csvstat.py     # Compute statistics for CSV files
│   │   ├── in2csv.py      # Convert other tabular formats to CSV
│   │   └── sql2csv.py     # Convert SQL results to CSV
│   ├── cleanup.py         # CSV row validation and repair utilities
│   ├── cli.py             # Command-line interface infrastructure
│   ├── exceptions.py      # Custom exception classes
│   └── grep.py            # Pattern-based CSV filtering
```

### Purpose

csvkit is a comprehensive command-line toolkit for processing CSV (Comma-Separated Values) files. It provides robust CSV parsing and manipulation capabilities that handle edge cases like embedded newlines in quoted fields, various encodings, and compressed file formats.

The repository solves the problem of working with messy or complex CSV data by providing:
- Reliable CSV parsing that handles real-world CSV quirks
- A rich set of utilities for common CSV operations (filtering, sorting, joining, etc.)
- Support for compressed file formats (.gz, .bz2, .xz)
- Flexible column selection and manipulation
- Integration with SQL databases
- JSON conversion capabilities

Target users include data analysts, scientists, and developers who need to quickly process CSV data from the command line or integrate CSV processing into shell scripts and automated workflows.

In the broader ecosystem, csvkit serves as a standalone command-line tool that complements other Unix utilities and data processing frameworks. It's particularly valuable in data engineering pipelines where CSV files are frequently manipulated and transformed.

### Architecture

```mermaid
flowchart TD
    A[Command Line Interface] --> B[CSVKitUtility Base Class]
    B --> C[CSV Processing Infrastructure]
    B --> D[Core CSV Operations]
    C --> E[File Handling (LazyFile)]
    C --> F[Argument Parsing]
    C --> G[Encoding & Locale Support]
    D --> H[Row Validation (RowChecker)]
    D --> I[Pattern Matching (FilteringCSVReader)]
    D --> J[Column Processing]
    H --> K[cleanup.join_rows]
    I --> L[grep.pattern_as_function]
    I --> M[grep.regex_callable]
    I --> N[grep.standardize_patterns]
    J --> O[Column Identifier Resolution]
    O --> P[parse_column_identifiers]
    O --> Q[match_column_identifier]
    P --> Q
    Q --> O
    L --> M
    N --> L
    N --> M
    B --> R[Individual Utilities]
    R --> S[Utilities Directory]
    S --> T[Specific Tool Implementations]
    T --> U[csvclean, csvcut, csvgrep, etc.]
```

The architecture follows a layered pattern:
1. **Infrastructure Layer**: Provides core CSV processing capabilities, file handling, and argument parsing
2. **Core Processing Layer**: Handles CSV validation, pattern matching, and column operations
3. **Utility Layer**: Implements specific CSV operations as command-line tools
4. **Entry Point Layer**: Command-line interfaces that expose functionality to users

### Entry Points

#### CLI Commands
All utilities are exposed as command-line tools:
- `csvclean` - Clean CSV files by fixing row length issues
- `csvcut` - Select columns from CSV files  
- `csvformat` - Format CSV files for better readability
- `csvgrep` - Filter CSV files using pattern matching
- `csvjoin` - Join multiple CSV files
- `csvjson` - Convert CSV to JSON
- `csvlook` - Display CSV files in a formatted table
- `csvpy` - Execute Python expressions on CSV data
- `csvsort` - Sort CSV files
- `csvsql` - Convert CSV to SQL or execute SQL queries on CSV
- `csvstack` - Stack CSV files vertically
- `csvstat` - Compute statistics for CSV files
- `in2csv` - Convert other tabular formats to CSV
- `sql2csv` - Convert SQL results to CSV

Each command accepts standard arguments for:
- Input file specification (`-f`, `--file`)
- Delimiter specification (`-d`, `--delimiter`)
- Encoding specification (`-e`, `--encoding`)
- Header row handling (`-H`, `--no-header-row`)
- Compression handling (automatic detection of .gz, .bz2, .xz files)

#### Importable APIs
The core functionality is also available as Python modules:
- `csvkit.cli` - Command-line interface infrastructure
- `csvkit.cleanup` - CSV row validation and repair utilities
- `csvkit.grep` - Pattern-based CSV filtering
- `csvkit.exceptions` - Custom exception classes

### Core Features

1. **CSV Validation & Repair** - `csvclean` and `cleanup.RowChecker` validate and fix inconsistent row lengths
2. **Column Selection** - `csvcut` and column identifier parsing allow flexible column manipulation
3. **Pattern Matching** - `csvgrep` enables filtering CSV data using text patterns or regular expressions
4. **Data Transformation** - `csvformat`, `csvlook` provide formatting and display utilities
5. **Data Aggregation** - `csvjoin`, `csvstack` combine multiple CSV files
6. **Statistical Analysis** - `csvstat` computes descriptive statistics for CSV data
7. **Format Conversion** - `csvjson`, `in2csv`, `sql2csv` convert between CSV and other formats
8. **SQL Integration** - `csvsql` bridges CSV processing with SQL databases
9. **Compression Support** - Automatic handling of gzipped, bzip2, and xz compressed files
10. **Flexible Input/Output** - Support for stdin/stdout piping and file redirection

### Dependencies

#### External Dependencies
- `argparse` - Standard library for command-line argument parsing
- `csv` - Standard library for CSV file handling
- `sys`, `os` - System-specific parameters and operating system interfaces
- `json` - For JSON serialization in `csvjson`
- `re` - Regular expression support in `csvgrep`
- `agate` - Data analysis library for type inference and CSV processing
- `gzip`, `bz2`, `lzma` - For handling compressed file formats

#### Internal Dependencies
- `csvkit.cleanup` - For row validation and repair functionality
- `csvkit.cli` - For command-line interface infrastructure and CSV processing utilities
- `csvkit.exceptions` - For custom exception handling
- `csvkit.grep` - For pattern-based CSV filtering
- `csvkit.utilities` - For command-line utility implementations

### Configuration

Configuration is primarily handled through command-line arguments:
- `-d`, `--delimiter` - Specify delimiter character
- `-t`, `--tabs` - Use tab delimiters
- `-e`, `--encoding` - Specify file encoding
- `-H`, `--no-header-row` - Treat first row as data, not header
- `-K`, `--skip-lines` - Skip initial lines before header
- `-l`, `--linenumbers` - Add line numbers to output
- `--zero` - Use zero-based column indexing

Environment variables:
- `PYTHONIOENCODING` - Controls default encoding for stdin/stdout

---

## Modules

- [`csvkit`](csvkit.md)
- [`csvkit/utilities`](csvkit/utilities.md)

