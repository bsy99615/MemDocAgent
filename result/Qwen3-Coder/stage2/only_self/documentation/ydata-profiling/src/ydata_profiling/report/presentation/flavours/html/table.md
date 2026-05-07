# `table.py`

## `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable` · *class*

## Summary:
HTMLTable is a concrete implementation of the Table abstract class that renders tabular data as HTML markup for report presentation.

## Description:
The HTMLTable class provides HTML-specific rendering capabilities for tabular data within the ydata profiling report system. It inherits from the Table base class and implements the render() method to generate HTML table markup from structured data. This class is typically instantiated by report generators when HTML output is required for tabular content.

The motivation for this abstraction is to separate HTML presentation logic from the conceptual representation of tabular data, enabling different rendering strategies (HTML, Markdown, etc.) while maintaining a consistent interface for report components.

## State:
- content: dict - Dictionary containing table data and metadata including rows, style configuration, name, and caption; populated during initialization from parent Table class
- Inherits all attributes from Table parent class including rows, style, name, and caption

## Lifecycle:
- Creation: Instantiate with required rows and style parameters from parent Table class, optionally providing name and caption
- Usage: Call render() method to generate HTML table markup; typically called by report rendering systems
- Destruction: Inherits standard object lifecycle management from parent classes

## Method Map:
```mermaid
graph TD
    A[HTMLTable.__init__] --> B[Table.__init__]
    B --> C[content setup]
    A --> D[HTMLTable.render]
    D --> E[templates.template("table.html").render(**self.content)]
```

## Raises:
- TemplateNotFound: May be raised if "table.html" template is not found in the templates module
- Exception: May propagate from template rendering if content structure is invalid

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.flavours.html.table import HTMLTable

# Create a table with sample data
rows = [
    ["Name", "Age", "City"],
    ["Alice", 25, "New York"],
    ["Bob", 30, "San Francisco"]
]

style = Style()
table = HTMLTable(rows, style, name="Demographics", caption="User demographics table")

# Render to HTML
html_output = table.render()
# Returns HTML string representation of the table
```

### `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable.render` · *method*

## Summary:
Generates an HTML string representation of tabular data using the table.html Jinja2 template.

## Description:
This method implements the abstract render() interface from the parent Table class to produce HTML output for tabular data. It utilizes the Jinja2 templating system to process the table's content dictionary and generate a complete HTML table string.

The method is invoked during the HTML report generation phase when structured tabular data needs to be displayed in web-based reports. It serves as the presentation layer implementation for tables within the HTML flavour of the ydata-profiling system, maintaining separation between data representation and formatting logic.

This dedicated method exists rather than being inlined to provide a clean abstraction layer between the data model (self.content) and its HTML rendering, supporting the template-driven architecture of the reporting system.

## Args:
    None

## Returns:
    str: A complete HTML string containing the formatted table with data from self.content properly rendered

## Raises:
    Exception: Potentially raises exceptions from Jinja2 template rendering if content is incomplete or template processing fails

## State Changes:
    Attributes READ: self.content (a dictionary containing table data and formatting parameters)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary compatible with the table.html template's expected variables
    - The "table.html" template must be available in the Jinja2 environment
    - Parent Table class must be properly initialized
    
    Postconditions:
    - Returns a valid HTML string representing the table structure
    - Does not modify any instance attributes

## Side Effects:
    - Template loading and rendering operations (potentially involving filesystem I/O)
    - Potential exceptions during template processing if content is malformed

