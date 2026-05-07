# `docs`

## Tree:
```
docs/
└── tutorials/
```

## Role:
Manages documentation generation workflows for Jupyter notebooks.

## Description:
The docs module provides infrastructure for generating documentation from Jupyter notebooks. It specifically handles the processing of tutorial notebooks by executing them with timeout protection, converting them to reStructuredText format, and cleaning output cells from the original files. This ensures that documentation includes properly executed and formatted tutorial content.

## Components:
- tutorials: Sub-module containing utilities for processing Jupyter notebooks for documentation
  - convert_nb(nbname: str) -> None: Executes a Jupyter notebook and converts it to RST format for documentation

## Public API:
- tutorials.convert_nb(nbname: str) -> None: Processes a Jupyter notebook through nbconvert operations to prepare it for documentation.
  - Description: Takes a notebook file name (without .ipynb extension), executes it with timeout protection, converts it to reStructuredText format, and clears outputs from the original notebook.
  - Usage: Call with the base name of a notebook file to process it for documentation inclusion.

## Dependencies:
- Internal: None
- External: Jupyter nbconvert for notebook conversion capabilities

## Constraints:
- Notebook files must exist with the name `{nbname}.ipynb` in the expected location
- Jupyter nbconvert must be installed and available in the system PATH
- Users must have appropriate permissions to execute notebooks and modify files
- The convert_nb function modifies original notebook files in-place during execution and output clearing steps

