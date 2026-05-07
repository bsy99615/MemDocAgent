# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.get_table` · *function*

## Summary:
Creates a vertical layout containing a grid-based frequency table from labeled items with progress bars and count labels.

## Description:
This function constructs a visual frequency table presentation using ipywidgets, arranging items in a grid layout with three columns: label, progress bar, and count. It's designed to display categorical frequency distributions in a structured, widget-based interface. The function is typically used within the ydata-profiling library to render frequency tables in Jupyter notebooks and interactive environments.

## Args:
    items (List[Tuple[widgets.Label, widgets.FloatProgress, widgets.Label]]): A list of tuples, each containing three elements:
        - widgets.Label: The category label to display
        - widgets.FloatProgress: Progress bar representing frequency proportion
        - widgets.Label: Count label showing absolute frequency

## Returns:
    VBox: A vertical container widget that holds the grid-based table layout

## Raises:
    None explicitly raised

## Constraints:
    - Preconditions: 
        * items must be a list (can be empty)
        * Each tuple in items must contain exactly three elements
        * All elements in tuples must be valid ipywidgets objects
        * The list length determines the number of rows in the resulting grid
    - Postconditions:
        * Returns a VBox widget containing a properly formatted GridspecLayout
        * The returned VBox contains exactly one child (the GridspecLayout)
        * GridspecLayout has 3 columns and len(items) rows

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_table] --> B{items is empty?}
    B -- Yes --> C[Create empty GridspecLayout(0, 3)]
    B -- No --> D[Create GridspecLayout with len(items) rows]
    D --> E[Iterate through items]
    E --> F{row_id, item_tuple}
    F --> G[Set table[row_id, 0] = label]
    G --> H[Set table[row_id, 1] = progress]
    H --> I[Set table[row_id, 2] = count]
    I --> J[Return VBox([table])]
```

## Examples:
```python
# Basic usage with sample data
from ipywidgets import Label, FloatProgress
items = [
    (Label("Category A"), FloatProgress(value=0.7), Label("70%")),
    (Label("Category B"), FloatProgress(value=0.3), Label("30%"))
]
widget = get_table(items)

# Empty list usage
empty_widget = get_table([])
```

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable` · *class*

## Summary
WidgetFrequencyTable is a widget-based frequency table renderer that displays categorical data with progress bars and count labels in Jupyter environments.

## Description
WidgetFrequencyTable extends the FrequencyTable base class to provide a widget-based rendering implementation specifically designed for Jupyter notebook environments. It transforms structured frequency table data into an interactive visualization that displays categorical data with progress bars showing proportions and count labels. The component categorizes rows by their "extra_class" attribute to apply distinct visual styling (danger for missing values, info for other values, or default styling for regular entries).

This class implements the render() method from the FrequencyTable base class, providing the specific widget-based rendering logic needed for interactive data profiling reports in Jupyter environments. It leverages the get_table helper function to construct the final widget hierarchy and integrates seamlessly with the existing ydata-profiling presentation layer architecture.

## State
- content: dict - Dictionary containing frequency table data with "rows" key, where rows[0] is a list of dictionaries with keys: "label", "count", "n", "extra_class"
- item_type: str - Set to "frequency_table" by parent class, identifying this as a frequency table item type
- name: str (inherited) - Optional name identifier for the frequency table
- anchor_id: str (inherited) - Optional anchor identifier for linking within documents
- classes: str (inherited) - Optional CSS classes for styling the rendered output

## Lifecycle
- Creation: Instantiate with rows (list) and redact (bool) parameters, optionally providing name, anchor_id, and classes via keyword arguments. The parent FrequencyTable class handles initialization of content structure.
- Usage: Call render() method to generate the ipywidgets.VBox representation. The render method processes self.content["rows"][0] to create widget components and returns a VBox container.
- Destruction: No explicit cleanup required; relies on Python's garbage collection for widget disposal.

## Method Map
```mermaid
flowchart TD
    A[WidgetFrequencyTable.render] --> B[get_table(items)]
    B --> C[VBox with GridspecLayout]
    A --> D[Process rows from self.content["rows"][0]]
    D --> E{Row extra_class}
    E -->|missing| F[FloatProgress with bar_style="danger"]
    E -->|other| G[FloatProgress with bar_style="info"]
    E -->|default| H[FloatProgress with bar_style=""]
    F --> I[Create items tuple]
    G --> I
    H --> I
    I --> J[Return VBox from get_table]
```

## Raises
- KeyError: If self.content does not contain the expected "rows" key structure or if rows data is malformed
- TypeError: If self.content["rows"][0] is not iterable or contains non-dictionary row data
- AttributeError: If row elements lack required keys ("label", "count", "n", "extra_class")

## Example
```python
# Create a frequency table with sample data
rows = [
    {"label": "Category A", "count": 75, "n": 100, "extra_class": ""},
    {"label": "Missing Values", "count": 25, "n": 100, "extra_class": "missing"},
    {"label": "Other Category", "count": 10, "n": 100, "extra_class": "other"}
]

# Create WidgetFrequencyTable instance
table = WidgetFrequencyTable(rows, redact=False)

# Render the widget
widget = table.render()  # Returns VBox containing the frequency table visualization

# In Jupyter notebook, the widget will display automatically
# The widget shows progress bars with different styles for different categories
```

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table.WidgetFrequencyTable.render` · *method*

## Summary:
Renders a frequency table with progress bars and count labels using ipywidgets, categorizing rows by missing/other status with distinct styling.

## Description:
Transforms frequency table data into an interactive widget-based visualization. This method processes the content from self.content["rows"][0] to create a structured table with three columns: category labels, progress bars showing proportions, and count labels. It applies different CSS styles to progress bars based on row categories (missing, other, or regular) to visually distinguish data patterns.

The method is part of the WidgetFrequencyTable class and serves as the rendering endpoint for frequency table visualizations in Jupyter environments. It leverages the get_table helper function to construct the final widget hierarchy.

## Args:
    None explicitly taken as arguments

## Returns:
    VBox: A vertical container widget holding the complete frequency table grid layout

## Raises:
    KeyError: If self.content does not contain the expected "rows" key structure
    TypeError: If self.content["rows"][0] is not iterable or contains malformed row data
    AttributeError: If row elements lack required keys ("label", "count", "n", "extra_class")

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        * self.content must be a dictionary containing "rows" key
        * self.content["rows"] must be a list with at least one element
        * self.content["rows"][0] must be iterable (list/tuple)
        * Each row in self.content["rows"][0] must be a dictionary with keys: "label", "count", "n", "extra_class"
    Postconditions:
        * Returns a VBox widget with exactly one child (GridspecLayout)
        * The returned widget displays all rows from the content data
        * Progress bars have appropriate min/max values set based on row data

## Side Effects:
    None

