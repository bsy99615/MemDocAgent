# `table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.table.get_table` · *function*

## Summary:
Creates a grid layout table widget from a list of item dictionaries with optional color formatting for alert items.

## Description:
Generates an interactive table widget using ipywidgets GridspecLayout where each row displays a name-value pair from the input items. Items with an 'alert' flag set to True will have their name and value text colored in red using the report's error color scheme. This function is used to render tabular data in Jupyter notebook environments.

## Args:
    items (List[Dict[str, Any]]): A list of dictionaries, each containing 'name' and 'value' keys, and optionally an 'alert' boolean key.

## Returns:
    GridspecLayout: A grid layout widget with two columns (name and value) and rows matching the input items count.

## Raises:
    KeyError: When any item dictionary does not contain the required 'name' or 'value' keys.

## Constraints:
    Preconditions:
        - Each dictionary in items must contain 'name' and 'value' keys
        - Items list may be empty, resulting in a zero-row grid
    Postconditions:
        - The returned GridspecLayout will have exactly len(items) rows and 2 columns
        - All items are rendered as HTML widgets in their respective positions

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_table called] --> B{items empty?}
    B -->|Yes| C[Create empty GridspecLayout(0,2)]
    B -->|No| D[Create GridspecLayout(len(items),2)]
    D --> E[Iterate through items]
    E --> F{item has alert?}
    F -->|Yes| G[Apply error color formatting]
    F -->|No| H[Use raw values]
    G --> I[Set HTML widgets in grid]
    H --> I
    I --> J[Return table]
```

## Examples:
Example 1: Basic usage with regular items
    Input: [{"name": "Count", "value": "100"}, {"name": "Average", "value": "50.5"}]
    Output: GridspecLayout with 2 rows, 2 columns showing the name-value pairs

Example 2: Usage with alert items
    Input: [{"name": "Error Count", "value": "5", "alert": True}, {"name": "Success Rate", "value": "95%"}]
    Output: GridspecLayout where first row has red-colored text for both name and value
```

## `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable` · *class*

## Summary:
WidgetTable is a concrete implementation of the Table presentation class that renders tabular data as interactive Jupyter widgets with optional captions.

## Description:
WidgetTable implements the render() method from the base Table class to produce interactive Jupyter widget output. The render() method returns a VBox container widget that holds a GridspecLayout table widget and an optional HTML caption. This class enables rich, interactive data visualization in notebook environments while maintaining consistency with the broader reporting framework's presentation layer architecture.

The WidgetTable class is part of the widget-based presentation flavour in ydata-profiling, designed specifically for Jupyter notebook environments where interactive widgets provide enhanced user experience compared to static HTML representations.

## State:
- content: Dict[str, Any] - Dictionary containing table data with "rows" and "caption" keys; "rows" expects a sequence of item dictionaries, and "caption" expects a string or None value
- Inherits all state from Table parent class including style configuration and metadata fields

## Lifecycle:
- Creation: Instantiated through standard inheritance from Table class, requiring rows and style parameters; caption is optional
- Usage: Called by the presentation layer's rendering pipeline when processing table-type report items; render() method is invoked to generate widget output
- Destruction: Managed by Python's garbage collection; no explicit cleanup required

## Method Map:
```mermaid
flowchart TD
    A[render()] --> B[get_table(content["rows"])]
    B --> C[VBox(items)]
    C --> D[Return VBox]
    A --> E{content["caption"] != None}
    E -->|Yes| F[widgets.HTML(caption)]
    E -->|No| G[Skip caption]
    F --> H[items.append(caption)]
```

## Raises:
- No explicit exceptions raised by WidgetTable's __init__ method
- KeyError may be raised by get_table() if content["rows"] contains malformed item dictionaries
- TypeError may occur if content["rows"] is not iterable or content["caption"] is not a string/None

## Example:
```python
from ydata_profiling.report.presentation.flavours.widget.table import WidgetTable
from ydata_profiling.config import Style

# Create a table with data and caption
style = Style()
rows = [{"name": "Count", "value": "100"}, {"name": "Average", "value": "50.5"}]
table = WidgetTable(rows=rows, style=style, caption="Summary Statistics")

# Render the table widget
widget = table.render()  # Returns VBox containing table and caption
```

### `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable.render` · *method*

## Summary:
Renders a widget-based table presentation with optional caption from the table content.

## Description:
Creates a vertical widget layout containing a table widget and optional caption. This method serves as the primary rendering interface for WidgetTable objects, transforming structured table data into an interactive Jupyter widget display. The method is called during the presentation layer's rendering phase when converting table content into visual components for notebook environments.

## Args:
    None explicitly taken, but accesses self.content

## Returns:
    VBox: A vertical container widget holding the table and optional caption

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.content must be a dictionary with "rows" and "caption" keys
        - self.content["rows"] must be a valid input for get_table function
        - self.content["caption"] must be either None or a string value
    Postconditions:
        - Returns a VBox widget containing exactly one or two children
        - The first child is always a table widget created by get_table
        - The second child (if present) is an HTML widget displaying the caption

## Side Effects:
    None

