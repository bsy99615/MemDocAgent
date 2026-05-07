# `docs.tutorials`

## Tree:
```
tutorials/
└── tools/
    └── nb_to_doc.py
```

## Role:
Converts and processes Jupyter notebooks into documentation formats while executing them.

## Description:
This module provides functionality for processing Jupyter notebooks as part of the documentation pipeline. It automates the conversion of tutorial notebooks into reStructuredText format while executing them and clearing outputs. The module serves as a utility for maintaining up-to-date tutorial documentation that can be integrated into the project's documentation system.

## Components:
- `convert_nb(nbname: str) -> None`: Executes a Jupyter notebook and converts it to multiple formats through nbconvert operations.

## Public API:
- `convert_nb(nbname: str) -> None`: Processes a Jupyter notebook file through three sequential nbconvert operations. The function executes the notebook with a timeout, converts it to reStructuredText format, and clears all cell outputs from the notebook. This utility function automates the complete processing pipeline for tutorial notebooks.

## Dependencies:
- Uses `subprocess` module for executing shell commands
- Relies on Jupyter nbconvert tool being installed and available in system PATH

## Constraints:
- The notebook file (nbname + ".ipynb") must exist in the current working directory
- Jupyter nbconvert must be installed and available in the system PATH
- The user must have appropriate permissions to execute the notebook and modify files
- Execution may consume significant disk I/O due to file modifications and creation

