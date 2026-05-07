# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable` · *class*

## Summary:
WidgetCorrelationTable renders correlation matrices as interactive Jupyter widgets with title headers.

## Description:
This class implements a widget-based presentation layer for correlation matrices, extending the abstract CorrelationTable class. It provides a concrete implementation of the render() method that creates a visually appealing widget display suitable for Jupyter notebooks. The widget consists of a title header followed by an output area that displays the correlation matrix using IPython's display functionality.

The WidgetCorrelationTable class exists to provide a specific implementation for Jupyter environments where interactive widgets are preferred over static HTML representations. It leverages the standardized content structure defined by the CorrelationTable base class while utilizing ipywidgets for enhanced interactivity.

## State:
- Inherits all state from CorrelationTable parent class including:
  - item_type: Set to "correlation_table" 
  - content: Dictionary containing required keys "correlation_matrix" (pandas DataFrame) and "name" (str)
- No additional instance attributes beyond those inherited from parent classes

## Lifecycle:
- Creation: Instantiate with name (str) and correlation_matrix (pd.DataFrame) parameters; optional anchor_id and classes parameters
- Usage: Call render() method to generate widget presentation; typically called by report generation system
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetCorrelationTable.render] --> B[ipywidgets.Output]
    A --> C[ipywidgets.HTML]
    A --> D[ipywidgets.VBox]
    B --> E[IPython.display.display]
    E --> F[self.content["correlation_matrix"]]
```

## Raises:
- KeyError: If self.content dictionary lacks required keys "correlation_matrix" or "name"
- TypeError: If self.content["correlation_matrix"] is not a pandas DataFrame or compatible object
- AttributeError: If self.content is not a dictionary or lacks required methods
- NotImplementedError: Inherited from parent class CorrelationTable.render() if not properly overridden

## Example:
```python
import pandas as pd
from src.ydata_profiling.report.presentation.flavours.widget.correlation_table import WidgetCorrelationTable

# Create sample correlation matrix
corr_matrix = pd.DataFrame({
    'A': [1.0, 0.5, -0.3],
    'B': [0.5, 1.0, 0.2],
    'C': [-0.3, 0.2, 1.0]
})

# Create widget correlation table
widget_table = WidgetCorrelationTable("Feature Correlations", corr_matrix)

# Render to widget display
widget_output = widget_table.render()
# Displays a VBox with title header and correlation matrix output
```

### `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable.render` · *method*

## Summary:
Creates a widget-based visualization of a correlation matrix with a title header.

## Description:
This method generates a widget-based presentation of a correlation matrix by creating a vertical box container with a title and an output area. It displays the correlation matrix using IPython's display functionality within a widget context, making it suitable for Jupyter notebook environments. The method is part of the WidgetCorrelationTable class that extends CorrelationTable for widget-based rendering.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container containing:
        - A heading element (HTML) displaying the correlation table name
        - An output area (Output) displaying the correlation matrix

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content (accesses "correlation_matrix" and "name" keys)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing "correlation_matrix" key with a pandas DataFrame
    - self.content must be a dictionary containing "name" key with a string value
    Postconditions:
    - Returns a widgets.VBox instance with exactly two children in order: name header, correlation matrix output

## Side Effects:
    - Invokes IPython.core.display.display() to render the correlation matrix
    - Instantiates ipywidgets.Output and widgets.VBox objects
    - Triggers widget rendering in Jupyter environments

