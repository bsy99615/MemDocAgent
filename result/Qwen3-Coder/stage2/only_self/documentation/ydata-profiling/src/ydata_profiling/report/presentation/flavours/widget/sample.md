# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample` · *class*

## Summary:
WidgetSample is a concrete implementation of the Sample class that renders data samples using ipywidgets for interactive Jupyter notebook display.

## Description:
The WidgetSample class provides a widget-based rendering implementation for data samples within the ydata profiling system. It inherits from the Sample class and implements the abstract render() method to produce a visually appealing widget-based representation of data samples suitable for Jupyter notebook environments.

This class is specifically designed for use in widget-based report presentations where interactive visualization is desired. It leverages ipywidgets to create a structured display with a heading for the sample name and an output area for the actual sample data.

## State:
- content: dict - Dictionary containing the sample data and metadata, inherited from Renderable parent class
  - Keys are determined by the parent Sample class initialization
  - Expected to contain at least "sample" and "name" keys based on usage in render() method
- name: str - Human-readable identifier for the sample item, stored in content dictionary
- anchor_id: str - Optional anchor identifier for HTML/CSS linking, stored in content dictionary
- classes: str - Optional CSS classes for styling, stored in content dictionary

## Lifecycle:
- Creation: Instantiate with a name string, pandas DataFrame sample, optional caption, and additional keyword arguments. The parent Sample class handles initialization of content dictionary with required keys.
- Usage: Call render() method to generate a widgets.VBox containing the sample name and data display
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetSample.render()] --> B[Output()]
    B --> C[display(self.content["sample"])]
    C --> D[widgets.HTML("<h4>" + self.content["name"] + "</h4>")]
    D --> E[widgets.VBox([name, out])]
```

## Raises:
- None explicitly raised by __init__ method
- May raise exceptions from ipywidgets or display functions if invalid data is provided

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.sample import WidgetSample

# Create sample data
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create WidgetSample instance
widget_sample = WidgetSample(
    name="First_100_rows", 
    sample=sample_data, 
    caption="Sample of dataset"
)

# Render the widget
widget_output = widget_sample.render()

# The result is a widgets.VBox containing:
# 1. An HTML heading with the sample name
# 2. An Output widget displaying the sample data
```

### `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample.render` · *method*

*No documentation generated.*

