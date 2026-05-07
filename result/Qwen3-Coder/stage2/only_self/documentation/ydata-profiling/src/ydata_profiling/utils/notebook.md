# `notebook.py`

## `src.ydata_profiling.utils.notebook.full_width` · *function*

## Summary:
Sets Jupyter notebook container width to 100% by injecting CSS styling.

## Description:
This function applies CSS styling to make the notebook container span the full width of the browser window. It's designed to be used in Jupyter notebook environments to improve the display of profiling reports by removing width restrictions.

## Args:
    None

## Returns:
    None

## Raises:
    None

## Constraints:
    Preconditions:
    - Must be run in a Jupyter notebook environment with IPython
    - IPython.core.display module must be available
    
    Postconditions:
    - CSS styling is injected into the current notebook cell output
    - The notebook container width is set to 100% (width:100% !important)

## Side Effects:
    - Injects CSS styling into the current Jupyter notebook cell output
    - Modifies the display appearance of the notebook container in Jupyter environments

## Control Flow:
```mermaid
flowchart TD
    A[full_width() called] --> B[Import HTML and display from IPython]
    B --> C[Create HTML style element]
    C --> D[Display style element to notebook]
```

## Examples:
```python
# Typical usage in a Jupyter notebook
from ydata_profiling.utils.notebook import full_width

# Call the function to expand container width
full_width()

# This will make the subsequent profiling report display in full width
```

