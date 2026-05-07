# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample` · *class*

## Summary:
WidgetSample is a Jupyter widget-based renderer for data samples in profiling reports, implementing the abstract Sample class for interactive visualization.

## Description:
WidgetSample provides a concrete implementation of the Sample class specifically designed for Jupyter notebook environments. It extends the core Sample functionality by rendering sample data as interactive ipywidgets, making it suitable for live exploration and analysis within Jupyter notebooks. This class leverages the parent's content structure to access sample data and metadata, transforming them into a visually appealing and interactive widget display.

## State:
- Inherits all attributes from Sample parent class including: name, sample data, caption, item_type, content dictionary, anchor_id, and classes
- The content dictionary is populated by the parent Sample.__init__ method with "sample" and "caption" keys
- The "sample" key contains the actual data to be displayed (typically a pandas DataFrame)
- The "name" key contains the human-readable identifier for the sample
- No additional instance attributes beyond those inherited from Sample

## Lifecycle:
- Creation: Instantiated with the same parameters as the parent Sample class (name, sample DataFrame, optional caption)
- Usage: Called by report generation systems that require widget-based rendering of samples in Jupyter environments
- Destruction: Managed by Python's garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[WidgetSample.render()] --> B[widgets.Output()]
    B --> C[IPython.display.display(self.content["sample"])]
    C --> D[widgets.HTML("<h4>" + self.content["name"] + "</h4>")]
    D --> E[widgets.VBox([name, out])]
    E --> F[Return VBox widget]
```

## Raises:
- No explicit exceptions raised by WidgetSample itself
- May raise exceptions from parent Sample class initialization if validation fails
- Potential runtime errors if self.content["sample"] or self.content["name"] are missing or incompatible
- Runtime errors from IPython.display.display() if sample data cannot be rendered

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.widget.sample import WidgetSample

# Create sample data (typically a pandas DataFrame)
sample_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create WidgetSample instance (inherits from Sample)
widget_sample = WidgetSample(name="Test Sample", sample=sample_df)

# Render the widget for display in Jupyter
rendered_widget = widget_sample.render()

# The rendered widget can be displayed directly in Jupyter notebooks
# The output will show:
# - A styled header "<h4>Test Sample</h4>"
# - The sample DataFrame rendered in an Output widget
```

### `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample.render` · *method*

## Summary:
Renders a data sample as a Jupyter widget with a styled header and interactive output display.

## Description:
This method implements the rendering logic for WidgetSample objects, creating a visual representation of a data sample using ipywidgets. It displays the sample data within an Output widget and presents the sample name as a styled HTML heading. The method is part of the widget-based presentation flavour for report generation, specifically designed for Jupyter notebook environments. It leverages the content dictionary inherited from the parent Sample class to access the sample data and name.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing the sample name header and the data output widget.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content (accessed via self.content["sample"] and self.content["name"])
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing both "sample" and "name" keys
    - The "sample" value must be compatible with IPython.display.display() for proper rendering
    - The "name" value must be a string for HTML formatting
    - The WidgetSample instance must be properly initialized with content from the parent Sample class

    Postconditions:
    - Returns a properly formatted widgets.VBox with two children: an HTML header and an Output widget
    - The Output widget contains the rendered sample data
    - The returned widget is suitable for display in Jupyter notebooks

## Side Effects:
    - Generates I/O operations through IPython.display.display() to render the sample data
    - Creates ipywidgets objects (Output, HTML, VBox) which may affect Jupyter notebook rendering
    - May trigger Jupyter's widget display system to render the content in the notebook

