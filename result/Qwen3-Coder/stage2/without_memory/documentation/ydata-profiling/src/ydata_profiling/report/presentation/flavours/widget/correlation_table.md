# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable` · *class*

## Summary:
WidgetCorrelationTable renders correlation matrices as interactive Jupyter widgets with a styled header.

## Description:
This class implements the rendering of correlation tables specifically for Jupyter widget environments. It extends the abstract CorrelationTable class to provide a concrete implementation that displays correlation matrices using ipywidgets. The component is designed to be used in Jupyter notebooks where interactive widgets are supported, creating a structured display with a heading and the correlation matrix visualization.

## State:
- content: dict containing "correlation_matrix" (pd.DataFrame) and "name" (str) keys
- correlation_matrix: pandas DataFrame representing the correlation data to display
- name: string identifier for the correlation table that becomes the header text

## Lifecycle:
- Creation: Instantiate with a name and correlation_matrix DataFrame
- Usage: Call render() method to generate the ipywidgets.VBox display object
- Destruction: No explicit cleanup required; widgets manage their own lifecycle

## Method Map:
```mermaid
graph TD
    A[WidgetCorrelationTable] --> B[render]
    B --> C[Output()]
    C --> D[display(correlation_matrix)]
    B --> E[widgets.HTML(name)]
    B --> F[widgets.VBox([name, out])]
```

## Raises:
- None explicitly raised by __init__ (inherits from parent classes)
- May raise exceptions from ipywidgets operations during render() if invalid data is provided

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.correlation_table import WidgetCorrelationTable

# Create sample correlation matrix
corr_data = pd.DataFrame({
    'A': [1.0, 0.5, -0.3],
    'B': [0.5, 1.0, 0.2],
    'C': [-0.3, 0.2, 1.0]
})

# Create widget correlation table
widget_table = WidgetCorrelationTable("Feature Correlations", corr_data)

# Render the widget
display(widget_table.render())
```

### `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable.render` · *method*

## Summary:
Renders a correlation table as a Jupyter widget VBox containing a name header and correlation matrix display.

## Description:
This method creates a visual representation of a correlation matrix using ipywidgets. It displays the correlation matrix within an Output widget and adds a formatted name header. This method is part of the widget-based presentation flavour for correlation tables in the ydata-profiling library.

The render method is separated from the initialization logic to allow for flexible rendering of the correlation table in different contexts, such as Jupyter notebooks or interactive dashboards. This separation enables the correlation table to be rendered multiple times with potentially different states while maintaining clean encapsulation.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing:
        - An HTML widget displaying the correlation table name as a heading
        - An Output widget displaying the correlation matrix

## Raises:
    None explicitly raised

## State Changes:
    - Attributes READ: 
        - self.content["correlation_matrix"]: The correlation matrix DataFrame to display
        - self.content["name"]: The name/title of the correlation table
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions:
        - self.content must contain a "correlation_matrix" key with a pandas DataFrame value
        - self.content must contain a "name" key with a string value
    - Postconditions:
        - Returns a widgets.VBox instance containing exactly two children: name header and output widget
        - The correlation matrix is displayed within the Output widget using IPython.display

## Side Effects:
    - I/O: Uses IPython.core.display.display() to render the correlation matrix
    - Widget creation: Creates widgets.Output, widgets.HTML, and widgets.VBox instances
    - External service calls: None

