# `table.py`

## `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable` · *class*

## Summary:
HTMLTable is an HTML presentation component that renders tabular data as HTML content using a Jinja2 template.

## Description:
HTMLTable serves as an HTML-specific implementation of the abstract Table class, responsible for converting structured tabular data into HTML markup. It is part of the HTML presentation flavour system and is typically instantiated by the reporting framework when rendering tables in HTML reports. The class leverages a template-based approach to generate semantically correct HTML tables from structured data.

## State:
- `content`: Dictionary containing table data including rows, name, caption, and style information inherited from the parent Table class
- The class inherits all attributes from Table including rows, style, name, and caption
- The content dictionary is populated during initialization with table metadata and data
- All parameters from Table constructor (rows, style, name, caption) are preserved and passed through

## Lifecycle:
- Creation: Instantiated with rows, style, and optional name/caption parameters, inheriting from Table constructor
- Usage: Called by the reporting framework when rendering HTML content, typically through the render() method
- Destruction: No special cleanup required; follows standard Python object lifecycle

## Method Map:
```mermaid
graph TD
    A[HTMLTable.__init__] --> B[Table.__init__]
    B --> C[ItemRenderer.__init__]
    C --> D[HTMLTable.render]
    D --> E[templates.template("table.html")]
    E --> F[HTMLTable.render return]
```

## Raises:
- No explicit exceptions raised by HTMLTable.__init__
- Template rendering may raise exceptions if the template is malformed or if required data is missing

## Example:
```python
# Create a table with sample data
from ydata_profiling.report.presentation.flavours.html.table import HTMLTable

rows = [
    ["Name", "Age", "City"],
    ["Alice", 30, "New York"],
    ["Bob", 25, "San Francisco"]
]

style = Style()  # Assuming Style class exists
table = HTMLTable(rows, style, name="Sample Data", caption="Employee Information")

# Render to HTML
html_content = table.render()
print(html_content)  # Outputs HTML table markup
```

### `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable.render` · *method*

## Summary:
Renders a table HTML template using the table's content data.

## Description:
This method implements the HTML rendering logic for table components. It takes the table's content data (including rows, name, caption, and style) and renders it using the Jinja2 "table.html" template. This method is part of the HTML presentation flavour implementation and is called during the HTML report generation process.

## Args:
    None

## Returns:
    str: The rendered HTML string representation of the table.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing the required keys: 'rows', 'name', 'caption', and 'style'
    - The "table.html" template must exist in the Jinja2 template directory
    
    Postconditions:
    - Returns a valid HTML string representation of the table
    - The returned HTML is properly formatted according to the template

## Side Effects:
    None

