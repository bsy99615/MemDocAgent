# `docs.tutorials.tools`

## Tree:
```
tools/
└── nb_to_doc.py
```

## Role:
Prepares Jupyter notebooks for documentation generation by executing them and converting them to RST format.

## Description:
This module provides functionality to process Jupyter notebooks for documentation purposes. It executes notebooks with timeouts, converts them to reStructuredText format, and clears outputs from the original notebook files. The module serves as a utility for preparing tutorial notebooks for inclusion in documentation builds.

## Components:
- `convert_nb(nbname: str) -> None`: Processes a Jupyter notebook through three sequential nbconvert operations for documentation preparation.

## Public API:
- `convert_nb(nbname: str) -> None`: Processes a Jupyter notebook through three sequential nbconvert operations for documentation preparation.
  - Description: Executes a series of Jupyter nbconvert commands on a notebook file to prepare it for documentation generation.
  - Usage: Call with the base name of a notebook file (without .ipynb extension) to process it.

## Dependencies:
- Internal: None
- External: Requires Jupyter nbconvert to be installed and available in system PATH

## Constraints:
- The notebook file must exist with the name `{nbname}.ipynb`
- Jupyter nbconvert must be installed and available in the system PATH
- The user must have appropriate permissions to execute the notebook and modify files
- Function modifies the original notebook file in-place during execution and output clearing steps

---

## Files

- [`nb_to_doc.py`](tools/nb_to_doc.md)

