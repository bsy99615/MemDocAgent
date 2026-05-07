# `hypertools.plot`

## Tree:
- plot/
  - backend.py
  - draw.py
  - plot.py

## Role:
Manages plotting functionality with unified backend handling for both Jupyter notebooks and regular Python environments.

## Description:
The `plot` module provides a cohesive plotting interface that abstracts away the complexities of backend selection and switching across different execution environments. It handles the initialization and management of matplotlib backends, ensuring consistent behavior whether running in Jupyter notebooks or standard Python scripts. The module also provides drawing utilities and the main plotting interface.

This module is used throughout the hypertools library to provide visualization capabilities while maintaining compatibility with various execution contexts and backend requirements. It groups together backend management, drawing utilities, and the primary plotting interface to create a unified visualization experience.

## Components:
- `hypertools.plot.backend.BackendMapping`: Establishes bidirectional relationships between Python and IPython backend identifiers
- `hypertools.plot.backend.HypertoolsBackend`: Provides case-insensitive backend identifiers with conversion utilities
- `hypertools.plot.backend.ParrotDict`: Enables case-insensitive backend key lookup in dictionaries
- `hypertools.plot.backend._block_greedy_completer_execution`: Prevents IPython greedy completer interference
- `hypertools.plot.backend._get_runtime_args`: Resolves function arguments for backend operations
- `hypertools.plot.backend._init_backend`: Initializes matplotlib backend configuration
- `hypertools.plot.backend._null_backend_context`: Provides null backend context for plotting operations
- `hypertools.plot.backend._reset_backend_notebook`: Registers deferred backend reset for notebooks
- `hypertools.plot.backend._switch_backend_notebook`: Switches matplotlib backend in notebook environments
- `hypertools.plot.backend._switch_backend_regular`: Switches matplotlib backend in regular environments
- `hypertools.plot.backend.manage_backend`: Manages backend switching operations
- `hypertools.plot.backend.set_interactive_backend`: Sets interactive matplotlib backend
- `hypertools.plot.draw._draw`: Core drawing implementation for plots
- `hypertools.plot.plot.plot`: Main plotting interface function

## Public API:
- `hypertools.plot.plot.plot`: Main plotting interface that handles data visualization with automatic backend management
- `hypertools.plot.backend.HypertoolsBackend`: Class for case-insensitive backend identifier handling
- `hypertools.plot.backend.BackendMapping`: Class for bidirectional backend identifier mapping
- `hypertools.plot.backend.ParrotDict`: Dictionary subclass for case-insensitive backend key lookup

## Dependencies:
- Internal: `hypertools.plot.backend` (for backend management utilities)
- External: `matplotlib`, `IPython`, `sys`, `warnings`, `inspect`

## Constraints:
- Backend initialization is handled automatically during module import
- Thread safety: Backend operations are not thread-safe and should be called sequentially
- The module automatically detects execution environment (notebook vs regular Python)

---

## Files

- [`backend.py`](plot/backend.md)
- [`draw.py`](plot/draw.md)
- [`plot.py`](plot/plot.md)

