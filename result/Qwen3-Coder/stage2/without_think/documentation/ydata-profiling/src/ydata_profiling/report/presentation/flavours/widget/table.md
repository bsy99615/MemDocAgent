# `table.py`

## `src.ydata_profiling.report.presentation.flavours.widget.table.get_table` · *function*

## Summary:
Creates a two-column grid layout displaying name-value pairs from a list of dictionaries, with optional alert coloring.

## Description:
Generates an interactive grid layout using ipywidgets that displays tabular data in a two-column format. Each row contains a name in the first column and its corresponding value in the second column. When an item contains an "alert" flag set to True, both the name and value are rendered with error-colored styling.

This function is part of the widget-based presentation flavour for data profiling reports, specifically designed for creating interactive table displays in Jupyter environments. It abstracts the complexity of widget creation and layout management into a reusable component.

## Args:
    items (List[Dict[str, Any]]): A list of dictionaries, each containing at minimum "name" and "value" keys. Each dictionary may optionally contain an "alert" boolean key to indicate special formatting requirements.

## Returns:
    GridspecLayout: A grid layout object with rows equal to the number of items and exactly 2 columns, where each cell contains an HTML widget displaying the respective name or value.

## Raises:
    None: This function does not explicitly raise exceptions, though underlying widget operations may raise exceptions if invalid parameters are passed.

## Constraints:
    Preconditions:
    - Each dictionary in the items list must contain "name" and "value" keys
    - The items list should not be empty (though technically works with empty lists)
    
    Postconditions:
    - The returned GridspecLayout is properly initialized with the correct dimensions
    - All name and value entries are wrapped in HTML widgets
    - Alert formatting is applied consistently when the alert flag is present

## Side Effects:
    None: This function has no side effects beyond creating and returning the GridspecLayout object.

## Control Flow:
```mermaid
flowchart TD
    A[get_table called] --> B[Create GridspecLayout]
    B --> C[Iterate through items]
    C --> D{Has alert key?}
    D -->|Yes| E[Apply fmt_color to name and value]
    E --> F[Assign name to grid[row, 0]]
    F --> G[Assign value to grid[row, 1]]
    D -->|No| H[Assign name to grid[row, 0]]
    H --> I[Assign value to grid[row, 1]]
    I --> J[Next item?]
    J -->|Yes| C
    J -->|No| K[Return GridspecLayout]
```

## Examples:
    >>> items = [
    ...     {"name": "Age", "value": "25"},
    ...     {"name": "Income", "value": "$50,000", "alert": True}
    ... ]
    >>> layout = get_table(items)
    >>> # Returns a GridspecLayout with 2 rows and 2 columns
    >>> # First row shows "Age" and "$50,000" normally
    >>> # Second row shows both fields in red due to alert flag

## `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable` · *class*

## Summary:
WidgetTable renders tabular data as an interactive Jupyter widget VBox container with optional caption support.

## Description:
WidgetTable is a concrete implementation of the abstract Table class that generates interactive table presentations using ipywidgets. It creates a vertical box container (VBox) containing a grid layout of table data, making it suitable for Jupyter notebook environments where interactive visualization is desired.

This class serves as a bridge between structured tabular data and interactive widget-based presentation, enabling users to view data in a visually appealing and interactive format within Jupyter notebooks. It's particularly useful for data profiling reports where tables need to be displayed with proper styling and interactivity.

## State:
- content: Dict - Dictionary containing table data with "rows" and "caption" keys. The "rows" key holds the tabular data structure, and "caption" holds optional descriptive text.
- rows: Sequence - Inherited from parent Table class, representing the structured data rows to be displayed in the table.
- caption: Optional[str] - Inherited from parent Table class, providing optional descriptive text for the table.

## Lifecycle:
- Creation: Instantiate with rows and style parameters (inherited from Table parent class). The WidgetTable constructor accepts the same parameters as its parent Table class.
- Usage: Call render() method to generate the VBox widget representation. The render() method processes the content and returns a properly formatted VBox container.
- Destruction: Managed automatically by Python's garbage collection; no explicit cleanup required.

## Method Map:
```mermaid
graph TD
    A[WidgetTable.render()] --> B[get_table(content["rows"])]
    B --> C[VBox([GridspecLayout])]
    C --> D{content["caption"] != None?}
    D -->|Yes| E[VBox([GridspecLayout, HTML(caption)])]
    D -->|No| F[VBox([GridspecLayout])]
```

## Raises:
- None explicitly raised by WidgetTable.__init__ or render() methods
- May propagate exceptions from underlying ipywidgets operations or get_table() function

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.flavours.widget.table import WidgetTable

# Create sample data
rows = [
    ["Feature", "Type", "Count"],
    ["age", "int", 1000],
    ["income", "float", 1000]
]

style = Style(primary_colors=["#377eb8", "#e41a1c"])

# Create WidgetTable instance
table = WidgetTable(
    rows=rows,
    style=style,
    name="demographics_table",
    caption="Demographic statistics"
)

# Render to widget
widget = table.render()
# Returns VBox containing GridspecLayout with table data and optional caption
```

### `src.ydata_profiling.report.presentation.flavours.widget.table.WidgetTable.render` · *method*

## Summary:
Renders a widget-based table with optional caption in a vertical box container.

## Description:
Creates a vertical box layout containing a widget table and optional caption. This method transforms the table content stored in self.content["rows"] into an interactive widget grid layout, and optionally adds a caption as HTML text below the table. The method is part of the widget-based presentation flavour for data profiling reports, specifically designed for Jupyter notebook environments.

The render method is separated from the initialization logic to provide a clean separation of concerns, allowing the table to be rendered independently while maintaining the flexibility to add additional UI elements like captions. This approach enables consistent rendering behavior across different table implementations while keeping the widget creation logic encapsulated.

## Args:
    None: This method does not accept any parameters beyond the implicit self reference.

## Returns:
    VBox: A vertical box container holding the table grid layout and optional caption as child widgets.

## Raises:
    None explicitly raised: The method does not raise exceptions directly, though underlying widget operations may raise exceptions if invalid parameters are passed.

## State Changes:
    Attributes READ:
        - self.content: Dictionary containing "rows" and "caption" keys
        - self.content["rows"]: Data structure representing table rows to be rendered
        - self.content["caption"]: Optional string caption for the table

    Attributes WRITTEN:
        - None: This method does not modify any instance attributes.

## Constraints:
    Preconditions:
        - self.content["rows"] must be a valid input for the get_table function
        - self.content["caption"] must be either None or a string value
        - The get_table function must be available in the module scope

    Postconditions:
        - Returns a VBox container with at least one child (the table grid)
        - If caption is present, the VBox contains two children (table + caption)
        - The returned VBox is suitable for display in Jupyter notebooks

## Side Effects:
    None: This method has no side effects beyond creating and returning widget objects.

