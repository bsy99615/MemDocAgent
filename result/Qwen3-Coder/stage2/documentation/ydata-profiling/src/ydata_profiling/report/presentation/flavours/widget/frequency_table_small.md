# `frequency_table_small.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.WidgetFrequencyTableSmall` · *class*

## Summary:
WidgetFrequencyTableSmall renders small frequency tables as interactive Jupyter widgets with styled progress bars and count labels.

## Description:
The WidgetFrequencyTableSmall class is a specialized implementation of FrequencyTableSmall designed for Jupyter notebook environments. It transforms frequency table data into interactive ipywidgets that display progress bars with appropriate styling based on data categories (missing, other, regular). This class serves as a concrete renderer for small frequency tables in widget-based reporting contexts.

This class exists as a distinct abstraction to separate the presentation logic for small frequency tables in Jupyter environments from other rendering implementations. It leverages the ipywidgets library to create interactive visualizations that enhance data exploration in notebook interfaces.

## State:
- `content`: Dictionary containing frequency table data with "rows" and "redact" keys
- `rows`: List of dictionaries representing frequency table data rows
- `redact`: Boolean flag indicating whether sensitive data should be redacted
- All inherited attributes from FrequencyTableSmall including `item_type`, `name`, `anchor_id`, and `classes`

The constructor inherits all parameters from FrequencyTableSmall:
- `rows`: Required List[Any] parameter containing frequency table data in dictionary format
- `redact`: Required boolean parameter controlling data redaction
- `**kwargs`: Additional keyword arguments for name, anchor_id, and classes

## Lifecycle:
Creation: Instantiate with required `rows` and `redact` parameters, optionally providing additional kwargs for name, anchor_id, and classes. The rows parameter must contain dictionaries with keys "count", "n", "label", and "extra_class".
Usage: Call render() method to generate the interactive widget presentation. The render() method internally calls frequency_table_nb with the content's rows.
Destruction: No explicit cleanup required; relies on Python garbage collection and ipywidgets' automatic resource management.

## Method Map:
```mermaid
graph TD
    A[WidgetFrequencyTableSmall.render()] --> B[frequency_table_nb(content["rows"])]
    B --> C[widgets.VBox]
```

## Raises:
- TypeError: If rows parameter is not a list, rows[0] is not iterable, or if "count" or "n" values are not numeric
- KeyError: If any dictionary in rows[0] is missing required keys ("count", "n", "label", or "extra_class")
- IndexError: If rows is empty or rows[0] does not exist

## Example:
```python
# Create a small frequency table with widget rendering
rows = [[{
    "count": 10,
    "n": 100,
    "label": "Category A",
    "extra_class": "missing"
}, {
    "count": 25,
    "n": 100,
    "label": "Category B", 
    "extra_class": "other"
}, {
    "count": 65,
    "n": 100,
    "label": "Category C",
    "extra_class": "normal"
}]]
table = WidgetFrequencyTableSmall(rows=rows, redact=False)

# Render the widget for display in Jupyter notebook
widget = table.render()
display(widget)
```

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.WidgetFrequencyTableSmall.render` · *method*

## Summary:
Converts frequency table data into an interactive widget-based display for Jupyter notebooks.

## Description:
Transforms the frequency table data stored in `self.content["rows"]` into a visual representation using ipywidgets. This method serves as the rendering implementation for the widget-based frequency table presentation, creating styled progress bars and count labels for each frequency entry.

The method is called during the report generation pipeline when a widget-based presentation is required for small frequency tables. It leverages the `frequency_table_nb` helper function to create the actual widget structure.

## Args:
    None - This method takes no parameters beyond the implicit `self`.

## Returns:
    widgets.VBox: A vertical box container holding horizontal boxes, each containing a FloatProgress widget and a Label widget representing one row of the frequency table.

## Raises:
    KeyError: If any dictionary in `self.content["rows"][0]` is missing required keys ("count", "n", "label", or "extra_class").
    TypeError: If `self.content["rows"]` is not a list, `self.content["rows"][0]` is not iterable, or if "count" or "n" values are not numeric.
    IndexError: If `self.content["rows"]` is empty or `self.content["rows"][0]` does not exist.

## State Changes:
    Attributes READ: 
    - self.content (reads the "rows" key from the content dictionary)
    
    Attributes WRITTEN: 
    - None - This method does not modify any instance attributes.

## Constraints:
    Preconditions:
    - `self.content` must be a dictionary containing a "rows" key
    - `self.content["rows"]` must be a list containing at least one element
    - `self.content["rows"][0]` must be iterable (list, tuple, etc.)
    - Each dictionary in `self.content["rows"][0]` must contain the keys: "count", "n", "label", and "extra_class"
    - All values for "count", "n" must be numeric (int or float)
    - "extra_class" values must be either "missing", "other", or any other string for default styling
    
    Postconditions:
    - Returns a widgets.VBox instance
    - All returned widgets are properly configured with their respective properties
    - Widget hierarchy follows the expected structure (VBox containing HBoxes)
    - Progress bars are styled appropriately based on extra_class values

## Side Effects:
    None - This method is pure and doesn't modify external state or perform I/O operations.

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.frequency_table_nb` · *function*

## Summary:
Creates a widget-based frequency table display with styled progress bars and count labels for Jupyter notebooks.

## Description:
Transforms a nested list of frequency table data into an interactive widget presentation using ipywidgets. This function specifically handles the small frequency table variant for Jupyter notebook environments, creating visual progress indicators with appropriate styling based on data categories.

The function is designed to be used in Jupyter notebook contexts where interactive widgets are supported. It processes the first dataset in the rows parameter and creates appropriate visual representations for different data categories (missing, other, regular).

## Args:
    rows (List[List[dict]]): A nested list where the first element contains dictionaries representing frequency table rows. Each dictionary must have keys: "count", "n", "label", and "extra_class". The "count" and "n" values must be numeric, and "extra_class" determines the styling of the progress bar.

## Returns:
    widgets.VBox: A vertical box container holding horizontal boxes, each containing a FloatProgress widget and a Label widget representing one row of the frequency table.

## Raises:
    KeyError: If any dictionary in rows[0] is missing required keys ("count", "n", "label", or "extra_class").
    TypeError: If rows is not a list, rows[0] is not iterable, or if "count" or "n" values are not numeric.
    IndexError: If rows is empty or rows[0] does not exist.

## Constraints:
    Preconditions:
    - rows must be a list containing at least one element
    - rows[0] must be iterable (list, tuple, etc.)
    - Each dictionary in rows[0] must contain the keys: "count", "n", "label", and "extra_class"
    - All values for "count", "n" must be numeric (int or float)
    - "extra_class" values must be either "missing", "other", or any other string for default styling
    
    Postconditions:
    - Returns a widgets.VBox instance
    - All returned widgets are properly configured with their respective properties
    - Widget hierarchy follows the expected structure (VBox containing HBoxes)
    - Progress bars are styled appropriately based on extra_class values

## Side Effects:
    None - This function is pure and doesn't modify external state or perform I/O operations.

## Control Flow:
```mermaid
flowchart TD
    A[Start frequency_table_nb] --> B{rows is valid?}
    B -- No --> C[Throw TypeError]
    B -- Yes --> D{rows[0] exists?}
    D -- No --> E[Throw IndexError]
    D -- Yes --> F[Initialize items list]
    F --> G[Iterate through fq_rows]
    G --> H{row["extra_class"] == "missing"?}
    H -- Yes --> I[Create danger style FloatProgress]
    H -- No --> J{row["extra_class"] == "other"?}
    J -- Yes --> K[Create info style FloatProgress]
    J -- No --> L[Create default style FloatProgress]
    I --> M[Add HBox to items]
    K --> M
    L --> M
    M --> N[Continue iteration]
    G --> O[Return widgets.VBox(items)]
```

## Examples:
```python
# Basic usage with sample data
sample_data = [[{
    "count": 10,
    "n": 100,
    "label": "Category A",
    "extra_class": "missing"
}, {
    "count": 25,
    "n": 100,
    "label": "Category B", 
    "extra_class": "other"
}, {
    "count": 65,
    "n": 100,
    "label": "Category C",
    "extra_class": "normal"
}]]
widget = frequency_table_nb(sample_data)

# Usage in a Jupyter notebook cell
display(widget)
```

