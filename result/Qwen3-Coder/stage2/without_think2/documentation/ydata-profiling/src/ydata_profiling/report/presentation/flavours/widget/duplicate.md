# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate` · *class*

## Summary:
WidgetDuplicate is a concrete implementation of the Duplicate class that renders duplicate data findings using ipywidgets for display in Jupyter environments.

## Description:
This class specializes in presenting duplicate data detection results using the ipywidgets library, making it suitable for interactive notebook environments. It inherits from the core Duplicate class and implements the render() method to generate a structured widget-based UI element. The component displays a heading with the duplicate section name followed by an Output widget that renders the actual duplicate content using IPython's display functionality.

The WidgetDuplicate class is designed to be used within the widget-based presentation flavour of ydata-profiling reports, providing a clean, organized way to visualize duplicate records in Jupyter notebooks. It follows the standard pattern of separating title display from content rendering for better UI organization.

## State:
- Inherits all state from parent classes:
  - item_type: str, set to "duplicate" by parent class
  - content: dict, containing "duplicate" key with duplicate data and optional "name" key
  - name: str, optional identifier for the component (accessed via content dictionary)
  - anchor_id: str, optional anchor identifier (accessed via content dictionary)
  - classes: str, optional CSS classes (accessed via content dictionary)

## Lifecycle:
- Creation: Instantiate with a name string and duplicate data (pandas DataFrame or similar displayable object)
- Usage: Call render() method to generate a widgets.VBox containing the title and duplicate content
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetDuplicate.render] --> B[widgets.Output()]
    B --> C[display(self.content["duplicate"])]
    C --> D[widgets.HTML("<h4>" + self.content["name"] + "</h4>")]
    D --> E[widgets.VBox([name, out])]
```

## Raises:
- KeyError: May occur when accessing self.content["duplicate"] or self.content["name"] if these keys are not present in the content dictionary
- AttributeError: May occur if self.content is not properly initialized or is None
- TypeError: May occur if the content under self.content["duplicate"] is not displayable by IPython's display function

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.duplicate import WidgetDuplicate

# Create sample duplicate data
duplicate_df = pd.DataFrame({'A': [1, 2, 2], 'B': [3, 4, 4]})

# Create WidgetDuplicate instance
widget_duplicate = WidgetDuplicate(name="My Duplicates", duplicate=duplicate_df)

# Render the widget
widget_output = widget_duplicate.render()

# The returned widget_output is a widgets.VBox containing:
# 1. An HTML heading with "My Duplicates"
# 2. An Output widget that displays the duplicate DataFrame when rendered
```

### `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate.render` · *method*

## Summary:
Renders a widget-based duplicate report element containing a title and displayed duplicate content.

## Description:
This method generates a visual representation of a duplicate report using ipywidgets. It creates a VBox container with a heading displaying the report name and an Output widget that displays the actual duplicate content. This method is part of the widget-based presentation flavour for ydata-profiling reports, specifically designed to render duplicate detection results in Jupyter notebooks.

The method is called during the rendering phase of a profiling report when a duplicate section needs to be displayed in a widget interface. It separates the title display from the content display to provide a clean, organized presentation.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box layout containing the title and duplicate content display

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing keys "name" and "duplicate"
    - The "duplicate" key must be displayable by IPython's display function
    - The "name" key must be a string that can be formatted into HTML
    - The method assumes proper initialization of parent class Duplicate

    Postconditions:
    - Returns a properly structured widgets.VBox with two children: a title and output widget
    - The output widget will display the content from self.content["duplicate"] when rendered

## Side Effects:
    - Generates UI elements using ipywidgets
    - Triggers display of content via IPython's display function within the output context

