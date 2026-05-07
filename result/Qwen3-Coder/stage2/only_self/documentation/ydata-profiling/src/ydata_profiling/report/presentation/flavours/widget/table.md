# `table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.table.get_table` · *function*

## Summary:
Creates a widget-based table layout from a list of name-value pairs with optional alert styling.

## Description:
Generates a GridspecLayout widget containing name-value pairs arranged in rows. Each row consists of two columns: one for the name and one for the value. When an item contains an "alert" flag set to True, both the name and value are formatted with error coloring.

## Args:
    items (List[Dict[str, Any]]): A list of dictionaries, each containing at minimum "name" and "value" keys. Optional "alert" key can be used to indicate error states.

## Returns:
    GridspecLayout: A widget layout object with dimensions matching the number of items (rows) and 2 columns, where each cell contains HTML widgets for names and values.

## Raises:
    None explicitly raised, but may raise exceptions from underlying widget creation if invalid data is provided.

## Constraints:
    Preconditions:
    - Each dictionary in items must contain "name" and "value" keys
    - Items must be a valid list (not None)
    
    Postconditions:
    - Returns a GridspecLayout with proper dimensions
    - All items are rendered as HTML widgets in the grid

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_table] --> B{items is empty?}
    B -- Yes --> C[Return empty GridspecLayout]
    B -- No --> D[Create GridspecLayout with len(items) rows, 2 cols]
    D --> E[For each item in items]
    E --> F{item has alert=True?}
    F -- Yes --> G[Apply error color formatting to name and value]
    F -- No --> H[Use name and value as-is]
    G --> I[Set table[row_id, 0] = HTML(name)]
    H --> I
    I --> J[Set table[row_id, 1] = HTML(value)]
    J --> K[Next item]
    K --> L{All items processed?}
    L -- No --> E
    L -- Yes --> M[Return table]
```

## Examples:
```python
# Basic usage
items = [
    {"name": "Count", "value": "100"},
    {"name": "Mean", "value": "50.5"}
]
table_widget = get_table(items)

# Usage with alerts
items_with_alerts = [
    {"name": "Error Count", "value": "5", "alert": True},
    {"name": "Success Rate", "value": "95%", "alert": False}
]
table_widget = get_table(items_with_alerts)
```

## `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable.render` · *method*

## Summary:
Creates a widget-based table presentation with optional caption from structured data rows.

## Description:
Generates a vertical box container (VBox) containing a widget table layout and optional caption for display in Jupyter environments. This method transforms tabular data into an interactive widget representation that can be rendered directly in notebook interfaces.

The render method is specifically designed for the widget-based presentation flavour of the ydata profiling system, enabling interactive table displays within Jupyter notebooks. It leverages the get_table utility function to create the main table structure and adds a caption if one is provided.

This method is part of the WidgetTable class hierarchy and follows the abstract Table class's pattern of implementing the render() method for specific presentation formats.

## Args:
    None - This is an instance method that operates on self

## Returns:
    VBox: A vertical box container holding the table layout and optional caption, suitable for direct display in Jupyter environments. The VBox contains at least one item (the table) and potentially two items (table plus caption).

## Raises:
    None explicitly raised by this method, though underlying widget creation may raise exceptions from ipywidgets if invalid data is provided

## State Changes:
    Attributes READ:
    - self.content["rows"]: Dictionary key containing the tabular data rows to be converted into a widget table. Expected to be a list of dictionaries with "name" and "value" keys.
    - self.content["caption"]: Dictionary key containing optional caption text for the table, which can be None or a string value.
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing "rows" key with valid data for get_table function
    - self.content["rows"] must be compatible with the get_table function's expected format (list of dictionaries with "name" and "value" keys)
    - self.content["caption"] must be either None or a string value
    
    Postconditions:
    - Returns a VBox widget containing properly formatted table content
    - If caption exists, it's wrapped in HTML em tags and added to the VBox items
    - The returned VBox is suitable for direct display in Jupyter notebook environments

## Side Effects:
    None - This method is pure and doesn't modify external state or cause I/O operations

