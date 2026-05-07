# `online-judge-tools`

## Repository-Level Documentation: online-judge-tools

### Tree Structure
```
online-judge-tools/
└── onlinejudge_command/
    ├── download_history.py
    ├── format_utils.py
    ├── log_formatter.py
    ├── output_comparators.py
    ├── pretty_printers.py
    ├── update_checking.py
    └── utils.py
```

### Purpose
The online-judge-tools repository provides a command-line interface for competitive programming practitioners to interact with online judges. It automates common tasks such as downloading problems, submitting solutions, testing against sample cases, and managing problem sets.

This tool is particularly valuable for competitive programmers who want to practice on various online judges (like Codeforces, AtCoder, UVa, etc.) and need efficient workflows for problem solving, testing, and submission management.

### Target Users
- Competitive programmers preparing for programming contests
- Participants in online coding competitions
- Developers practicing algorithmic problem solving
- Educators teaching competitive programming

### Position in Ecosystem
This is a standalone command-line tool designed to work with various online judges. It serves as a bridge between competitive programming platforms and local development environments, enabling automation of repetitive tasks in competitive programming workflows.

### Architecture Overview
The system follows a modular architecture with distinct responsibilities:

1. **Download Management** (`download_history.py`) - Handles problem downloading and caching with history tracking
2. **Format Utilities** (`format_utils.py`) - Manages test case file naming and pattern matching for various judge formats
3. **Output Comparison** (`output_comparators.py`) - Provides flexible comparison modes for judging solution correctness
4. **Pretty Printing** (`pretty_printers.py`) - Formats diffs and outputs for human readability with color highlighting
5. **Update Checking** (`update_checking.py`) - Verifies if newer versions are available
6. **Utility Functions** (`utils.py`) - Common helpers for execution, formatting, and system interactions

### Entry Points
- **CLI Command**: `oj` - Main command-line interface for all operations
- **Importable APIs**: Available through `onlinejudge_command` module for programmatic use

### Core Features
1. **Problem Downloading** - Fetch problems from online judges with history tracking
2. **Test Case Management** - Handle input/output test cases with flexible naming formats
3. **Solution Testing** - Run solutions against sample cases with detailed diff output
4. **Output Comparison** - Support for multiple comparison modes (exact, ignore spaces, floating point)
5. **Pretty Diff Display** - Human-readable output differences with color highlighting
6. **Update Checking** - Automatically notify users of available updates

### Dependencies
- Python 3.6+
- requests library for HTTP operations
- colorama for colored terminal output
- difflib for diff computation
- Various standard library modules (os, json, subprocess, etc.)

### Extension Points
- Custom output comparators can be implemented by extending `OutputComparator`
- New problem format patterns can be added through format utilities
- Additional online judge services can be integrated by implementing appropriate interfaces

---

## Modules

- [`onlinejudge_command`](onlinejudge_command.md)

