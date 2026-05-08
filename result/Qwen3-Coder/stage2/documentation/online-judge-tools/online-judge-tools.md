# `online-judge-tools`

## Repository Overview

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
The online-judge-tools repository provides command-line utilities and helper functions for interacting with online programming judges. It offers a set of supporting modules that facilitate common operations needed when working with competitive programming problems through command-line interfaces.

This repository serves as a foundational component for online judge-related command-line tools, providing reusable utilities that support various operations such as downloading problem data, formatting output, comparing results, and managing user interactions.

### Target Users
- Developers working with competitive programming platforms
- Users of command-line tools for online judge interactions
- Contributors to online judge automation tools

### Position in Ecosystem
This repository functions as a supporting library for command-line tools that interface with online judges. It provides utility functions and infrastructure that enable higher-level command implementations to operate consistently and efficiently.

### Entry Points
1. **CLI Commands**: Command-line interface for online judge operations
   - Accessible through standard command-line tools
   - Requires problem identifiers or URLs as arguments
   - Target audience: Competitive programmers and contest participants

2. **Importable APIs**: Direct module imports for programmatic use
   - Module: `onlinejudge_command`
   - Provides utility functions for command-line operations
   - Target audience: Developers building extensions or integrations

### Core Features
1. **Download History Management** - Persistent storage and retrieval of downloaded problem data
   - Implemented in: `download_history.py`

2. **Output Formatting** - Utilities for presenting structured data and command results
   - Implemented in: `format_utils.py`, `pretty_printers.py`

3. **Logging and Display** - Custom formatters for command-line interface output
   - Implemented in: `log_formatter.py`

4. **Output Comparison** - Logic for comparing program outputs with expected results
   - Implemented in: `output_comparators.py`

5. **Update Checking** - Mechanism for monitoring tool version updates
   - Implemented in: `update_checking.py`

6. **General Utilities** - Common helper functions for command-line operations
   - Implemented in: `utils.py`

### Dependencies
- Standard Python libraries (os, json, logging, sys, pathlib)
- External libraries for HTTP operations and terminal formatting

### Extension Points
- Modular design allows for adding new utility components
- Plugin-like architecture through separate utility modules
- Configuration options for different behaviors and formatting styles

---

## Modules

- [`onlinejudge_command`](onlinejudge_command.md)

