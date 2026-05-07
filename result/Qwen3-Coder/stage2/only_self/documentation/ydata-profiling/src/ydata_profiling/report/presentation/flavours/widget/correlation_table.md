# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable` · *class*

## Summary:
WidgetCorrelationTable renders correlation matrix data as an interactive ipywidgets VBox component.

## Description:
This class implements a widget-based presentation layer for correlation tables, specifically designed for Jupyter notebook environments. It overrides the render method of the base CorrelationTable class to provide a visual representation using ipywidgets. The component creates a structured display with a heading and the correlation matrix visualization.

## State:
- Inherits from CorrelationTable base class
- `content` dictionary attribute containing:
  - `correlation_matrix`: The correlation matrix data to display
  - `name`: String identifier for the correlation table
- All other attributes inherited from parent class

## Lifecycle:
- Creation: Instantiated with standard CorrelationTable initialization parameters
- Usage: Call render() method to generate widgets.VBox component
- Destruction: Managed automatically by ipywidgets lifecycle

## Method Map:
```mermaid
graph TD
    A[render] --> B[Output()]
    B --> C[display(correlation_matrix)]
    A --> D[widgets.HTML(name)]
    D --> E[widgets.VBox([name, out])]
```

## Raises:
- No explicit exceptions documented in render method
- May inherit exceptions from parent CorrelationTable class during initialization

## Example:
```python
# Create widget correlation table instance
widget_table = WidgetCorrelationTable(content={"name": "Feature Correlations", "correlation_matrix": matrix_data})

# Render the widget
widget_component = widget_table.render()

# Display in Jupyter notebook
display(widget_component)
```

### `src.ydata_profiling.report.presentation.flavours.widget.correlation_table.WidgetCorrelationTable.render` · *method*

## Summary:
Renders a correlation table visualization as a widget VBox containing a name header and correlation matrix display.

## Description:
Creates a widget-based visualization of a correlation matrix by rendering the correlation table content within an IPython Output widget. This method is responsible for presenting correlation data in a structured widget format suitable for Jupyter notebook environments.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing an HTML header with the correlation table name and an Output widget displaying the correlation matrix.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing both "correlation_matrix" and "name" keys
    - The correlation_matrix value must be compatible with IPython.display.display() function
    
    Postconditions:
    - Returns a properly formatted widgets.VBox with two children: HTML header and Output widget
    - The correlation matrix is displayed within the Output widget context

## Side Effects:
    - Displays correlation matrix content using IPython.display
    - Creates widget objects (Output, HTML, VBox) that will be rendered in Jupyter environment

