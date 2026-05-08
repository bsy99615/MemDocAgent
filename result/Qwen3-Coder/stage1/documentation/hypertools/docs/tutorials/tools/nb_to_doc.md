# `nb_to_doc.py`

## `docs.tutorials.tools.nb_to_doc.convert_nb` · *function*

## Summary:
Executes a Jupyter notebook and converts it to multiple formats through nbconvert operations.

## Description:
Processes a Jupyter notebook file through three sequential nbconvert operations. The function executes the notebook with a timeout, converts it to reStructuredText format, and clears all cell outputs from the notebook. This utility function automates the complete processing pipeline for tutorial notebooks.

## Args:
    nbname (str): The base name of the notebook file (without extension). Must correspond to an existing .ipynb file.

## Returns:
    None: This function does not return any value.

## Raises:
    subprocess.CalledProcessError: If any of the nbconvert shell commands fail during execution.

## Constraints:
    Preconditions:
    - The notebook file (nbname + ".ipynb") must exist in the current working directory
    - Jupyter nbconvert must be installed and available in the system PATH
    - The user must have appropriate permissions to execute the notebook and modify files
    
    Postconditions:
    - The original notebook file will be modified in-place during execution and output clearing steps
    - An RST version of the notebook will be created alongside the original file
    - All cell outputs will be cleared from the final notebook version

## Side Effects:
    - Modifies the original notebook file in-place during execution and output clearing steps
    - Creates a new RST file with the same base name as the notebook
    - Executes external shell commands through subprocess calls
    - May consume significant disk I/O due to file modifications and creation

## Control Flow:
```mermaid
flowchart TD
    A[Start convert_nb] --> B[Execute notebook with timeout via sh()]
    B --> C[Convert to RST format via sh()]
    C --> D[Clear outputs from notebook via sh()]
    D --> E[End]
```

## Examples:
```python
# Process a notebook named "tutorial_example"
convert_nb("tutorial_example")

# This will:
# 1. Execute tutorial_example.ipynb with 60 second timeout
# 2. Create tutorial_example.rst file
# 3. Modify tutorial_example.ipynb to remove all outputs
```

