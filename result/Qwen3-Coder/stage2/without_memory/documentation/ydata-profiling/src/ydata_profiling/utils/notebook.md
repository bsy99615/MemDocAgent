# `notebook.py`

## `src.ydata_profiling.utils.notebook.full_width` · *function*

## Summary:
Sets the Jupyter notebook container width to 100% to utilize full available space.

## Description:
This function injects CSS styling into a Jupyter notebook environment to expand the main container width to 100% of the available space. It's commonly used to improve the visual presentation of profiling reports or dashboards by removing the default constrained width limitations.

## Args:
    None

## Returns:
    None

## Raises:
    None

## Constraints:
    Precondition: Must be executed in a Jupyter notebook environment with IPython display capabilities
    Postcondition: The notebook's main container CSS style is modified to use 100% width

## Side Effects:
    Modifies the CSS styling of the current Jupyter notebook display environment
    Injects HTML/CSS into the notebook output area via IPython's display mechanism

## Control Flow:
```mermaid
flowchart TD
    A[full_width() called] --> B[Import HTML and display from IPython]
    B --> C[Create HTML style string]
    C --> D[Display HTML with CSS style]
    D --> E[Notebook container width set to 100%]
```

## Examples:
```python
# Typical usage in a Jupyter notebook
from ydata_profiling.utils.notebook import full_width

# Apply full width styling to the notebook
full_width()
```

