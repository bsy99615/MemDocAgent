# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate` · *class*

## Summary:
WidgetDuplicate is a concrete widget-based renderer for duplicate data findings in data profiling reports.

## Description:
The WidgetDuplicate class provides a Jupyter widget-based visualization for duplicate data findings. It inherits from the abstract Duplicate class and implements the render() method to create an interactive UI component using ipywidgets. This component displays duplicate data in a structured format with a heading and an output area for the actual duplicate content.

Unlike the parent Duplicate class which is abstract and meant to be subclassed, WidgetDuplicate is a concrete implementation that can be instantiated and used directly. It serves as a bridge between the abstract duplicate data representation and its concrete widget-based visualization in Jupyter environments.

## State:
- Inherits all attributes from Duplicate class including:
  - content (dict): Dictionary containing "duplicate" (pandas DataFrame with duplicate records) and "name" (str identifier) keys
  - item_type (str): Set to "duplicate" indicating the type of rendered item
  - name (str): Optional identifier for the component instance
  - anchor_id (str): Optional HTML anchor identifier for linking
  - classes (str): Optional CSS classes for styling
- The content dictionary must contain:
  - "duplicate": A pandas DataFrame containing the duplicate records to be displayed
  - "name": A string identifier for the duplicate finding

## Lifecycle:
- Creation: Instantiate with a name string and a pandas DataFrame containing duplicate data
- Usage: Call the render() method to generate a widgets.VBox containing the duplicate data visualization
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetDuplicate.__init__] --> B[Duplicate.__init__]
    B --> C[ItemRenderer.__init__]
    C --> D[Renderable.__init__]
    D --> E[WidgetDuplicate.render]
    E --> F[widgets.Output()]
    F --> G[display(self.content["duplicate"])]
    G --> H[widgets.HTML(f"<h4>{self.content['name']}</h4>")]
    H --> I[widgets.VBox([name, out])]
```

## Raises:
- None explicitly raised by WidgetDuplicate.__init__
- The render() method may raise exceptions from ipywidgets operations or display functions if the underlying data cannot be rendered

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.duplicate import WidgetDuplicate

# Create sample duplicate data
duplicate_data = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'value': ['A', 'B', 'A', 'C']
})

# Create WidgetDuplicate instance
widget_duplicate = WidgetDuplicate(name="Sample Duplicates", duplicate=duplicate_data)

# Render the widget for display in Jupyter
widget = widget_duplicate.render()

# The resulting widget will display:
# - An h4 header with "Sample Duplicates"
# - The duplicate DataFrame in an output area
# - The widget can be displayed directly in a Jupyter cell
```

### `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate.render` · *method*

## Summary:
Generates a widget-based UI component displaying duplicate data findings with a styled header.

## Description:
Constructs a vertical box widget containing a styled heading and an output area for displaying duplicate data content. This method is part of the widget-based presentation implementation for duplicate data visualization in data profiling reports, specifically designed for interactive Jupyter notebook environments.

The method creates a hierarchical widget structure where:
1. A styled HTML heading displays the component name
2. An Output widget renders the duplicate data content using IPython's display function

This implementation follows the widget presentation pattern for data profiling reports, enabling interactive exploration of duplicate data findings within Jupyter notebooks.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget with two children:
        - widgets.HTML: Styled heading element showing the component name
        - widgets.Output: Output widget displaying the duplicate data content

## Raises:
    None explicitly raised

## State Changes:
    - Attributes READ: 
        - self.content["duplicate"]: The duplicate data to be displayed via IPython display
        - self.content["name"]: The name/title for the component header
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions:
        - self.content must be a dictionary containing both "duplicate" and "name" keys
        - The "duplicate" value must be compatible with IPython's display function
        - The "name" value must be a string that can be safely formatted into HTML
    - Postconditions:
        - Returns a properly structured widgets.VBox with exactly two children in order
        - The returned widget maintains proper widget hierarchy for Jupyter frontend integration

## Side Effects:
    - I/O operations through IPython's display function during widget rendering
    - Widget object creation and registration with the Jupyter frontend
    - Memory allocation for widget objects and their associated display content

