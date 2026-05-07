# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.get_table` · *function*

## Summary:
Creates a widget-based frequency table layout from a list of labeled data items.

## Description:
Constructs a grid-based layout for displaying frequency distribution data using ipywidgets. This function organizes categorical data items into a tabular format with three columns: labels, progress bars showing relative frequencies, and count indicators. It serves as a utility for building interactive frequency tables in Jupyter notebook environments.

## Args:
    items (List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]): 
        A list of tuples where each tuple contains three ipywidgets elements:
        - widgets.Label: Display text for the category or item
        - widgets.FloatProgress: Progress bar visualizing relative frequency
        - widgets.Label: Count or numerical value display

## Returns:
    VBox: A vertical box container holding the GridspecLayout table, making it suitable for display in Jupyter notebooks.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - Each tuple in items must contain exactly three elements: Label, FloatProgress, and Label widgets
    - All widgets must be properly initialized ipywidgets objects
    - Items list can be empty, in which case an empty GridspecLayout is created
    
    Postconditions:
    - Returns a VBox container wrapping a GridspecLayout with 3 columns
    - The returned VBox is suitable for direct display in Jupyter environments

## Side Effects:
    None - This function is purely functional and doesn't modify external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start get_table] --> B{items empty?}
    B -- Yes --> C[Create empty GridspecLayout(0,3)]
    B -- No --> D[Create GridspecLayout(len(items),3)]
    D --> E[Iterate through items]
    E --> F{row_id, (label, progress, count)}
    F --> G[Set table[row_id,0] = label]
    G --> H[Set table[row_id,1] = progress]
    H --> I[Set table[row_id,2] = count]
    I --> J[Return VBox([table])]
```

## Examples:
```python
# Basic usage with sample data
from ipywidgets import Label, FloatProgress
from src.ydata_profiling.report.presentation.flavours.widget.frequency_table import get_table

# Create sample widgets
label1 = Label(value="Category A")
progress1 = FloatProgress(value=75, min=0, max=100)
count1 = Label(value="150")

label2 = Label(value="Category B")
progress2 = FloatProgress(value=25, min=0, max=100)
count2 = Label(value="50")

items = [(label1, progress1, count1), (label2, progress2, count2)]
table_widget = get_table(items)
# Displays a 2-row table with labels, progress bars, and counts
```

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable.render` · *method*

## Summary:
Creates an interactive widget-based frequency table display with colored progress bars indicating relative frequencies.

## Description:
Processes frequency distribution data from the component's content and generates an interactive Jupyter widget table. The method constructs labeled rows with progress bars that visually represent relative frequencies, using different styling based on the category type (missing, other, or regular). This widget-based representation provides an intuitive visualization of categorical data distributions in notebook environments.

This method is specifically designed for the widget-based presentation flavour and separates the rendering logic from the data structure, allowing for clean separation of concerns in the presentation layer.

## Args:
    None

## Returns:
    VBox: A vertical container holding a grid-based layout of frequency table entries, suitable for display in Jupyter notebooks.

## Raises:
    KeyError: If self.content does not contain the expected "rows" key structure
    TypeError: If self.content["rows"][0] is not iterable or contains malformed row data
    AttributeError: If row data lacks required keys like "label", "count", "n", or "extra_class"

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a "rows" key with a list structure where rows[0] is iterable
    - Each row in self.content["rows"][0] must be a dictionary with keys: "label", "count", "n", and "extra_class"
    - The "extra_class" value must be either "missing", "other", or another value for default styling
    - All row data must contain valid numeric values for "count" and "n" for progress bar initialization
    - The "label", "count", and "n" values must be convertible to strings for widget creation
    
    Postconditions:
    - Returns a VBox widget containing properly formatted frequency table data
    - The returned widget maintains the original data structure while adding visual representation
    - Progress bars are correctly styled based on extra_class values:
      * "missing" rows use bar_style="danger"
      * "other" rows use bar_style="info"  
      * Other rows use bar_style="" (default)

## Side Effects:
    None - This method is pure and does not modify external state or perform I/O operations.

