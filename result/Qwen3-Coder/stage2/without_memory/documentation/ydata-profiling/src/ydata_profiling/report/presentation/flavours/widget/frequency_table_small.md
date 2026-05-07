# `frequency_table_small.py`

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.WidgetFrequencyTableSmall` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.WidgetFrequencyTableSmall.render` · *method*

## Summary:
Renders a frequency table as an interactive widget VBox with progress bars.

## Description:
Converts frequency table data into an interactive widget representation showing progress bars for each category. This method is part of the widget-based presentation flavour for frequency tables.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container holding the frequency table visualization with progress bars and count labels.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing a "rows" key
    - self.content["rows"] must be a list of lists containing dictionaries with keys: "count", "n", "label", and "extra_class"
    Postconditions: 
    - Returns a valid widgets.VBox object with properly formatted progress bars

## Side Effects:
    None

## `src.ydata_profiling.report.presentation.flavours.widget.frequency_table_small.frequency_table_nb` · *function*

## Summary:
Creates a widget-based frequency table display with progress bars and labels for each category.

## Description:
Renders frequency table data as interactive widgets using ipywidgets. This function processes frequency data and displays it as horizontal progress bars with associated counts, styled differently based on category types (missing, other, or regular categories). It's typically used in widget-based data profiling reports to visualize categorical distributions.

## Args:
    rows (List[List[dict]]): Nested list of dictionaries containing frequency table data. The first list (rows[0]) is processed to create the display elements. Each dictionary should contain keys: 'count', 'n', 'label', and 'extra_class'. The function assumes rows[0] contains valid data.

## Returns:
    widgets.VBox: A vertical container widget holding horizontal containers (HBox) with progress bars and count labels for each frequency category. Returns an empty VBox if rows[0] is empty.

## Raises:
    KeyError: When a dictionary in rows[0] is missing required keys ('count', 'n', 'label', or 'extra_class').
    IndexError: When rows is empty or rows[0] does not exist.

## Constraints:
    Preconditions:
    - rows must be a list containing at least one list
    - rows[0] must be a list of dictionaries with required keys
    - Each dictionary in rows[0] must contain 'count', 'n', 'label', and 'extra_class' keys
    - All referenced values in dictionaries must be accessible

    Postconditions:
    - Returns a widgets.VBox instance containing properly formatted widget elements
    - Progress bars are created with appropriate styling based on extra_class values
    - All data from rows[0] is represented in the returned widget structure

## Side Effects:
    None - This function is pure and doesn't modify external state or perform I/O operations.

## Control Flow:
```mermaid
flowchart TD
    A[Start frequency_table_nb] --> B{rows[0] exists?}
    B -- Yes --> C[Initialize items list]
    C --> D[Iterate over fq_rows]
    D --> E{row["extra_class"] == "missing"?}
    E -- Yes --> F[Create danger style FloatProgress]
    F --> G[Add HBox with progress and label to items]
    G --> H[Next row]
    E -- No --> I{row["extra_class"] == "other"?}
    I -- Yes --> J[Create info style FloatProgress]
    J --> K[Add HBox with progress and label to items]
    K --> L[Next row]
    I -- No --> M[Create default style FloatProgress]
    M --> N[Add HBox with progress and label to items]
    N --> L
    L --> O[Return widgets.VBox(items)]
    B -- No --> P[Raises IndexError]
```

## Examples:
```python
# Basic usage with sample data
sample_rows = [[
    {
        "count": 10,
        "n": 100,
        "label": "Category A",
        "extra_class": "missing"
    },
    {
        "count": 25,
        "n": 100,
        "label": "Category B", 
        "extra_class": "other"
    },
    {
        "count": 65,
        "n": 100,
        "label": "Category C",
        "extra_class": ""
    }
]]

widget = frequency_table_nb(sample_rows)
```

