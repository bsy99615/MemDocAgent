# `docs.tutorials`

## Tree:
```
tools/
└── nb_to_doc.py
```

## Role:
Processes Jupyter notebooks for documentation generation by executing and converting them to reStructuredText format.

## Description:
This module provides utilities for preparing Jupyter notebooks for inclusion in documentation builds. It executes notebooks with timeout protection, converts them to reStructuredText format, and clears output cells from the original notebook files. This ensures that documentation includes properly executed and formatted tutorial content.

## Components:
- `convert_nb(nbname: str) -> None`: Executes a Jupyter notebook and converts it to RST format for documentation.

## Public API:
- `convert_nb(nbname: str) -> None`: Processes a Jupyter notebook through nbconvert operations to prepare it for documentation.
  - Description: Takes a notebook file name (without .ipynb extension), executes it with timeout protection, converts it to reStructuredText format, and clears outputs from the original notebook.
  - Usage: Call with the base name of a notebook file to process it for documentation inclusion.

## Dependencies:
- Internal: None
- External: Requires Jupyter nbconvert to be installed and available in system PATH

## Constraints:
- The notebook file must exist with the name `{nbname}.ipynb`
- Jupyter nbconvert must be installed and available in the system PATH
- The user must have appropriate permissions to execute the notebook and modify files
- Function modifies the original notebook file in-place during execution and output clearing steps

