# `docs.tutorials`

## Tree:
- tutorials/
  - tools/
    - nb_to_doc.py

## Role:
Processes Jupyter notebooks for documentation by executing, converting to RST, and cleaning output cells.

## Description:
This module provides utilities for preparing Jupyter notebooks for documentation workflows. It automates the process of executing notebooks with timeouts, converting them to RST format for documentation rendering, and cleaning output cells from the original notebook files. This ensures notebooks remain both executable and publication-ready.

## Components:
- convert_nb(nbname: str) -> None: Executes a notebook, converts it to RST, and clears output cells from the original file.

## Public API:
- convert_nb(nbname: str) -> None: Execute notebook, convert to RST, and clean output cells from original file.

## Dependencies:
- subprocess: Used for executing shell commands to run Jupyter notebook conversion and execution.
- sh: Wrapper for subprocess calls to simplify command execution (assumed to be imported locally).

## Constraints:
- The notebook file (nbname + ".ipynb") must exist in the current working directory.
- Jupyter and nbconvert must be installed and available in the system PATH.
- The user must have appropriate permissions to execute the notebook and modify files.

