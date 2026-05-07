# `docs`

## Tree:
```
docs/
└── tutorials/
    └── tools/
        └── nb_to_doc.py
```

## Role:
Manages documentation assets and tutorial materials for the project.

## Description:
The docs module serves as the central hub for all documentation-related assets and tutorial materials within the project. It provides infrastructure for maintaining, converting, and integrating tutorial content into the broader documentation system. This module ensures that tutorial notebooks are properly processed, converted, and kept up-to-date with the latest code changes.

## Components:
- tutorials: Sub-module containing tools for processing Jupyter notebooks into documentation formats
- nb_to_doc.py: Contains the convert_nb function for executing and converting tutorial notebooks

## Public API:
- tutorials.tools.nb_to_doc.convert_nb(nbname: str) -> None: Processes a Jupyter notebook file through three sequential nbconvert operations. The function executes the notebook with a timeout, converts it to reStructuredText format, and clears all cell outputs from the notebook. This utility function automates the complete processing pipeline for tutorial notebooks.

## Dependencies:
- External: subprocess module for executing shell commands
- External: Jupyter nbconvert tool for notebook conversion

## Constraints:
- Notebook files must exist in the current working directory
- Jupyter nbconvert must be installed and available in the system PATH
- Users must have appropriate permissions to execute notebooks and modify files
- Execution may consume significant disk I/O due to file modifications and creation

