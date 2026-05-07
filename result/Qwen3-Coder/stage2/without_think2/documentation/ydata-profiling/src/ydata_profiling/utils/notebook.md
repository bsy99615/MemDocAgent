# `notebook.py`

## `src.ydata_profiling.utils.notebook.full_width` · *function*

## Summary:
Configures the Jupyter notebook interface to display content in full-width mode by applying CSS styling.

## Description:
This function modifies the CSS styling of a Jupyter notebook environment to ensure that content displays at 100% width, effectively removing any constrained container widths that might limit the visual space available for data visualization or tables. It is designed specifically for use within Jupyter notebook environments where IPython's display capabilities are utilized.

The function encapsulates the logic for applying full-width CSS styling, making it reusable across different parts of a profiling workflow where consistent display formatting is desired. This extraction prevents code duplication and centralizes the styling configuration.

## Args:
    None

## Returns:
    None

## Raises:
    None

## Constraints:
    Preconditions:
    - Must be executed within a Jupyter notebook environment where IPython's display functionality is available.
    - The IPython.core.display module must be importable and functional.

    Postconditions:
    - The notebook's CSS styling will be updated to set container width to 100%.
    - No return value is produced.

## Side Effects:
    - Modifies the display output of the Jupyter notebook by injecting CSS styles.
    - Calls the IPython display function to render the CSS changes to the notebook interface.

## Control Flow:
```mermaid
flowchart TD
    A[full_width function call] --> B[Import HTML and display from IPython.core.display]
    B --> C[Create HTML style string with .container width:100%]
    C --> D[Call display() with the HTML style object]
    D --> E[CSS applied to notebook interface]
```

## Examples:
```python
# Typical usage in a profiling workflow
from ydata_profiling.utils.notebook import full_width

full_width()  # Applies full-width styling to the notebook
```

