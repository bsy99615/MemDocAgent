# `table.py`

## `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable` · *class*

## Summary:
HTMLTable renders tabular data as an HTML string using the table.html Jinja2 template.

## Description:
The HTMLTable class provides HTML rendering for table-based data by leveraging the table.html Jinja2 template. It inherits from the Table abstract base class and implements the render() method to produce HTML markup from tabular content.

This class is used within the HTML presentation flavour of the ydata-profiling report generation system to convert structured table data into properly formatted HTML table elements.

## State:
- content: dict - Contains the table data and formatting information required for HTML rendering. This dictionary is passed directly to the Jinja2 template engine.
- Inherits all attributes from Table parent class including rows, style, name, and caption.

## Lifecycle:
- Creation: Instantiated with the same parameters as the parent Table class (rows, style, optional name, optional caption). The constructor initializes the parent Table class and sets up the content dictionary.
- Usage: Called by report generation systems when HTML rendering of table data is required. The render() method is invoked to produce HTML output by rendering the table.html template with the content dictionary.
- Destruction: Managed automatically by Python's garbage collection; no explicit cleanup required.

## Method Map:
```mermaid
graph TD
    A[HTMLTable.__init__] --> B[Table.__init__]
    B --> C[ItemRenderer.__init__]
    A --> D[HTMLTable.render()]
    D --> E[templates.template("table.html")]
    E --> F[template.render(**self.content)]
```

## Raises:
- TemplateNotFound: If the "table.html" template is not found in the Jinja2 environment
- UndefinedError: If required variables are missing from self.content when rendering the template
- TypeError: If content dictionary has incorrect types or missing required keys

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.flavours.html.table import HTMLTable

# Create table data
rows = [
    ["Feature", "Type", "Count"],
    ["age", "int", 1000],
    ["income", "float", 1000]
]

style = Style(primary_colors=["#377eb8", "#e41a1c"])

# Create HTML table instance
html_table = HTMLTable(
    rows=rows,
    style=style,
    name="demographics_table",
    caption="Demographic statistics"
)

# Render to HTML
html_output = html_table.render()
# Returns HTML string with properly formatted table
```

### `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable.render` · *method*

## Summary
Renders tabular data as an HTML string using the table.html Jinja2 template.

## Description
Generates HTML markup for tabular data by rendering the 'table.html' template with the content stored in `self.content`. This method is part of the HTML presentation flavour implementation for table components in data profiling reports, providing a concrete rendering solution for tabular data structures.

The method is called during the HTML report generation pipeline when tabular data needs to be converted into a web-friendly HTML representation. It leverages the Jinja2 templating system to process the table content and produce properly formatted HTML output.

## Args
None

## Returns
str: A complete HTML string containing the formatted table with proper structure and styling as defined by the 'table.html' template.

## Raises
jinja2.exceptions.TemplateNotFound: If the 'table.html' template file cannot be located in the template directory
jinja2.exceptions.UndefinedError: If required variables from self.content are missing in the template
AttributeError: If self.content is not properly initialized or is not a dictionary

## State Changes
Attributes READ:
- self.content: Dictionary containing table data and metadata that gets unpacked and passed to the template
- self.content["rows"]: The tabular data to be rendered
- self.content["name"]: Optional table name for identification
- self.content["caption"]: Optional table caption for context
- self.content["style"]: Styling configuration for the table

Attributes WRITTEN:
- None

## Constraints
Preconditions:
- self.content must be a dictionary containing valid table data and metadata
- The 'table.html' template must exist in the template directory
- All required template variables must be present in self.content for successful rendering

Postconditions:
- Returns a valid HTML string representation of the table
- The returned HTML follows the expected structure for report presentation

## Side Effects
- Invokes Jinja2 template rendering system to process the final HTML
- May perform file I/O operations when loading the HTML template
- No external service calls or mutations to objects outside the instance

