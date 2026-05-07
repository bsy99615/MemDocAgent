# `PySnooper`

# PySnooper Repository Documentation

## Tree Structure

```
PySnooper/
├── misc/          # Miscellaneous supporting files, examples, or documentation
├── pysnooper/     # Main library source code containing the core PySnooper implementation
└── setup.py       # Package installation and metadata configuration
```

## Purpose

PySnooper is a Python library that provides debugging and profiling capabilities by automatically tracking variable changes and function execution. It enables developers to monitor program execution without manually instrumenting their code.

**Target Users:**
- Python developers debugging complex programs
- Software engineers performing performance analysis
- Anyone needing to understand variable state changes during execution

**Scenarios:**
- Debugging hard-to-reproduce bugs
- Profiling function execution and variable evolution
- Understanding program flow in complex applications

## Architecture

PySnooper follows a decorator-based architecture where functions can be wrapped with tracing capabilities. The system uses Python's AST (Abstract Syntax Tree) manipulation to instrument code at runtime.

## Entry Points

### Importable API
- `pysnooper.snoop()`: Main decorator for function tracing
- `pysnooper.trace()`: Alternative tracing mechanism

### CLI Commands
- Command-line interface for profiling scripts (if available)

## Core Features

1. **Function Tracing**: Automatically tracks function entry, exit, and execution
2. **Variable Monitoring**: Logs variable assignments and changes during execution
3. **Call Stack Analysis**: Shows function call hierarchy and execution flow

## Dependencies

- **Python 3.6+**: Required runtime environment
- **ast**: Standard library for AST manipulation
- **inspect**: Standard library for introspection
- **datetime**: Standard library for timestamp generation

## Configuration

### Environment Variables
- `PYSNOOPER_OUTPUT`: Controls output destination (console, file, etc.)
- `PYSNOOPER_LEVEL`: Sets verbosity level of tracing

### Runtime Parameters
- `output`: File path for output redirection
- `max_variable_length`: Maximum length of variable values to display
- `truncate`: Whether to truncate long variable values

## Extension Points

### Custom Tracers
Developers can extend PySnooper by:
- Creating custom decorators that inherit from base tracing classes
- Implementing custom output formatters

