# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.get_table` · *function*

## Summary:
Creates a widget-based frequency table layout from labeled data items.

## Description:
Generates a vertical box container with a grid layout containing frequency table entries. Each entry consists of a label, progress indicator, and count value arranged in a three-column grid.

## Args:
    items (List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]): 
        A list of tuples where each tuple contains three ipywidgets components:
        - widgets.Label: Display label for the item
        - widgets.FloatProgress: Progress bar showing relative frequency
        - widgets.Label: Count display for the item

## Returns:
    VBox: A vertical box container holding the grid layout of the frequency table

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - Each tuple in items must contain exactly three elements
        - All elements in each tuple must be valid ipywidgets components
        - Items list can be empty, resulting in a grid with 0 rows
    
    Postconditions:
        - Returns a VBox container with exactly one child (the GridspecLayout)
        - GridspecLayout has 3 columns and len(items) rows
        - Widget components are properly positioned in the grid

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_table] --> B{items empty?}
    B -- Yes --> C[Create empty GridspecLayout(0,3)]
    B -- No --> D[Create GridspecLayout(len(items),3)]
    D --> E[For each item in items]
    E --> F[Set table[row_id,0] = label]
    F --> G[Set table[row_id,1] = progress]
    G --> H[Set table[row_id,2] = count]
    H --> I[Return VBox([table])]
```

## Examples:
```python
# Basic usage with sample data
from ipywidgets import Label, FloatProgress
items = [
    (Label("Category A"), FloatProgress(value=0.3), Label("30")),
    (Label("Category B"), FloatProgress(value=0.7), Label("70"))
]
widget_table = get_table(items)
```

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable` · *class*

## Summary:
WidgetFrequencyTable renders categorical frequency data as an interactive Jupyter widget with styled progress bars.

## Description:
This class extends FrequencyTable to provide a widget-based visualization of categorical frequency distributions. It transforms structured frequency data into an interactive ipywidgets UI component suitable for Jupyter notebooks, displaying each category with a labeled progress bar and count value. The widget styling varies based on category types (missing, other, regular) to provide visual distinction.

The class is designed for use in Jupyter environments where interactive visualizations are beneficial for exploring categorical data distributions. It leverages ipywidgets for creating responsive UI elements while maintaining compatibility with the ydata-profiling report generation pipeline.

## State:
- Inherits all state from FrequencyTable parent class including:
  - rows: list of frequency data entries
  - redact: boolean flag for data redaction
  - item_type: string identifier set to "frequency_table"
  - content: dictionary containing configuration data
- Additional internal state:
  - items: temporary list used during rendering process

## Lifecycle:
- Creation: Instantiate with rows (list of frequency data) and redact (boolean) parameters, inheriting from FrequencyTable
- Usage: Call render() method to generate VBox widget containing the frequency table visualization
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
flowchart TD
    A[WidgetFrequencyTable.render] --> B[Process rows from self.content["rows"][0]]
    B --> C{row["extra_class"] == "missing"?}
    C -- Yes --> D[Create danger-styled FloatProgress]
    C -- No --> E{row["extra_class"] == "other"?}
    E -- Yes --> F[Create info-styled FloatProgress]
    E -- No --> G[Create default-styled FloatProgress]
    D --> H[Add to items list]
    F --> H
    G --> H
    H --> I[Call get_table(items)]
    I --> J[Return VBox widget]
```

## Raises:
- KeyError: If self.content["rows"][0] does not contain expected keys (label, count, n, extra_class)
- TypeError: If self.content["rows"][0] is not iterable or contains invalid data structures
- ValueError: If row["count"] or row["n"] values are not numeric for FloatProgress initialization

## Example:
```python
# Create a frequency table with sample data
from ydata_profiling.report.presentation.flavours.widget.frequency_table import WidgetFrequencyTable

rows = [
    {"label": "Category A", "count": 15, "n": 100, "extra_class": ""},
    {"label": "Missing Values", "count": 5, "n": 100, "extra_class": "missing"},
    {"label": "Other Category", "count": 10, "n": 100, "extra_class": "other"}
]

table = WidgetFrequencyTable(rows, redact=False)
widget = table.render()  # Returns VBox widget for Jupyter display
```

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable.render` · *method*

## Summary:
Renders a frequency table as an interactive widget with progress bars and labels.

## Description:
Transforms frequency table data into an interactive ipywidgets-based UI component. This method processes categorical frequency data and displays it using labeled progress bars with different styling based on data categories (missing, other, regular). The rendered output is a VBox container holding a grid layout of frequency table entries.

This method is specifically designed to create widget-based visualizations for Jupyter notebook environments, providing an interactive way to view categorical data distributions with visual progress indicators.

## Args:
    None

## Returns:
    VBox: A vertical box container holding the frequency table grid layout with three columns (label, progress bar, count) for each frequency entry.

## Raises:
    KeyError: If self.content["rows"][0] does not contain the expected keys (label, count, n, extra_class)
    TypeError: If self.content["rows"][0] is not iterable or contains invalid data structures

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.content must contain a "rows" key with a list structure
        - self.content["rows"][0] must be iterable and contain dictionaries with keys: "label", "count", "n", "extra_class"
        - Each row dictionary must have valid string values for "label" and "extra_class"
        - "count" and "n" values must be numeric for FloatProgress widget initialization
        
    Postconditions:
        - Returns a VBox widget containing a properly formatted grid layout
        - Each row in the grid contains exactly three components: label, progress bar, and count
        - Progress bars are styled differently based on extra_class values ("danger" for missing, "info" for other, empty for regular)

## Side Effects:
    None

