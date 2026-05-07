# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate` · *class*

## Summary:
WidgetDuplicate is a widget-based renderer for displaying duplicate data findings in data profiling reports using ipywidgets.

## Description:
WidgetDuplicate extends the core Duplicate class to provide a concrete implementation for rendering duplicate data reports in Jupyter notebook environments using ipywidgets. This class is specifically designed for use in widget-based presentation flavors of data profiling reports, where duplicate data findings need to be displayed in an interactive HTML widget format.

## State:
- `content` (dict): Dictionary containing the duplicate data under the key "duplicate" and the report name under the key "name"
- Inherits all attributes from the parent Duplicate class including `name` (str) and `item_type` (str)

## Lifecycle:
- Creation: Instantiate with a name string and a pandas DataFrame containing duplicate data, inheriting from Duplicate parent class
- Usage: Call the `render()` method to generate a widget-based UI component for displaying duplicate data findings in a Jupyter notebook environment
- Destruction: No explicit cleanup required; relies on ipywidgets' automatic resource management

## Method Map:
```mermaid
graph TD
    A[WidgetDuplicate.render] --> B[widgets.Output()]
    B --> C[display(self.content["duplicate"])]
    C --> D[widgets.HTML("<h4>" + self.content["name"] + "</h4>")]
    D --> E[widgets.VBox([name, out])]
```

## Raises:
- No explicit exceptions raised by WidgetDuplicate.__init__ (inherits from Duplicate)
- The render method may raise exceptions from ipywidgets operations if invalid data is provided

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.duplicate import WidgetDuplicate

# Create sample duplicate data
duplicate_df = pd.DataFrame({'id': [1, 2, 3], 'value': ['a', 'b', 'c']})

# Create WidgetDuplicate instance
widget_duplicate = WidgetDuplicate(name="my_duplicates", duplicate=duplicate_df)

# Render the widget
widget = widget_duplicate.render()
# Returns a widgets.VBox containing an HTML heading with the name and an Output widget displaying the duplicate data
```

### `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate.render` · *method*

## Summary:
Creates a widget-based visual representation of duplicate data findings with a header and output display area.

## Description:
This method generates a widget-based UI component for displaying duplicate data findings in a Jupyter notebook environment. It constructs a vertical box layout containing a heading element and an output area that displays the duplicate data content. The method leverages ipywidgets for UI construction and IPython's display functionality to render the duplicate data within the output area. This method is part of the widget-based presentation flavour for data profiling reports.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box widget containing two child elements in order:
        1. An HTML widget displaying the duplicate report name as a heading (h4)
        2. An Output widget that renders the duplicate data content via IPython.display()

## Raises:
    None explicitly raised

## State Changes:
    - Attributes READ: 
        - self.content (dictionary containing "duplicate" and "name" keys)
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions:
        - self.content must be a dictionary containing both "duplicate" and "name" keys
        - The "duplicate" key must reference content suitable for IPython.display()
        - The "name" key must contain a string value for HTML heading rendering
    - Postconditions:
        - Returns a properly structured widgets.VBox with exactly two child elements in the specified order

## Side Effects:
    - I/O operations: Uses IPython.core.display.display() to render content in Jupyter notebooks
    - Widget creation: Instantiates ipywidgets.Output and widgets.VBox objects
    - Environment dependency: Requires Jupyter notebook environment for proper rendering

