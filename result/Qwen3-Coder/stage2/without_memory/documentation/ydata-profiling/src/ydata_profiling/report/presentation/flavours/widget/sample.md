# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample` · *class*

## Summary:
WidgetSample renders a sample data visualization as an interactive Jupyter widget using ipywidgets.

## Description:
WidgetSample is a presentation layer component that transforms sample data into an interactive widget representation suitable for Jupyter environments. It inherits from the core Sample class and implements the render method to produce a widgets.VBox containing a styled header and an output area displaying the sample data.

This class serves as a concrete implementation of the abstract render method defined in the base Renderable class, specifically designed for widget-based user interfaces in Jupyter notebooks. It provides a standardized way to display sample datasets with appropriate styling and formatting.

## State:
- content: dict - Contains the sample data and metadata with keys:
  - "sample": pd.DataFrame - The actual sample data to display
  - "caption": Optional[str] - Optional caption for the sample
  - "name": str - The name/title of the sample
- All inherited attributes from parent classes including item_type, anchor_id, and classes

## Lifecycle:
- Creation: Instantiate with name (str), sample (pd.DataFrame), and optional caption (Optional[str])
- Usage: Call render() method to generate the widgets.VBox representation
- Destruction: No explicit cleanup required; widgets handle their own lifecycle management

## Method Map:
```mermaid
graph TD
    A[WidgetSample.__init__] --> B[Renderable.__init__]
    B --> C[ItemRenderer.__init__]
    C --> D[Sample.__init__]
    D --> E[WidgetSample.render]
    E --> F[widgets.VBox]
    F --> G[widgets.HTML]
    F --> H[Output]
    H --> I[display(sample)]
```

## Raises:
- No explicit exceptions raised by WidgetSample.__init__
- May raise exceptions from ipywidgets operations during rendering if invalid data is provided

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.sample import WidgetSample

# Create sample data
sample_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
sample_widget = WidgetSample(name="Test Sample", sample=sample_df, caption="Sample Data")

# Render the widget
widget_container = sample_widget.render()
# widget_container is a widgets.VBox containing the styled name and sample display
```

### `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample.render` · *method*

## Summary:
Renders a widget-based sample display with a heading and data content.

## Description:
Creates a vertical box layout containing a formatted heading and an output area displaying the sample data. This method is responsible for converting the sample data stored in self.content into a visual widget representation suitable for Jupyter notebook environments.

The render method is called during the presentation phase of report generation when widget-based output is required. It leverages ipywidgets to create interactive UI components that display sample data in a structured format.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing the sample name header and data display area.

## Raises:
    KeyError: If self.content does not contain the required keys "sample" or "name".
    Exception: Any exception that might occur during the display() operation or widget creation.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing "sample" key with valid data to display
    - self.content must contain "name" key with a string value for the heading
    - The sample data must be compatible with IPython.display.display() function
    
    Postconditions:
    - Returns a properly initialized widgets.VBox instance
    - The returned widget contains exactly two children: a name header and an output area

## Side Effects:
    I/O: Writes to the Jupyter notebook display area via IPython.display.display()
    Widget creation: Creates ipywidgets.VBox, Output, and HTML widgets

