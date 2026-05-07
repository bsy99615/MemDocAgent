# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable` · *class*

## Summary:
HTMLFrequencyTable is a presentation layer component that renders frequency table data as HTML markup, specifically designed for use in data profiling reports.

## Description:
This class implements the HTML rendering logic for frequency tables within the ydata-profiling framework. It extends the core FrequencyTable class and provides a concrete implementation of the render() method that generates HTML output. The component is responsible for transforming structured frequency data into properly formatted HTML tables, handling both simple and nested row structures.

The class is typically instantiated by the report generation system when creating HTML-based data profiling reports. It leverages Jinja2 templating to produce semantically correct HTML output that can be embedded in larger web documents. The render method specifically handles different row data structures by determining whether to iterate through nested lists or render directly.

## State:
- Inherits all state from FrequencyTable parent class including:
  - rows: list - Frequency data rows to display
  - redact: bool - Flag for hiding sensitive information
  - item_type: str - Set to "frequency_table"
  - content: dict - Configuration and data for rendering
  - name: str - Optional identifier
  - anchor_id: str - Optional anchor for linking
  - classes: str - Optional CSS classes

## Lifecycle:
- Creation: Instantiated with rows (list) and redact (bool) parameters, typically by report generation logic
- Usage: The render() method is called to generate HTML markup for frequency table content, processing the data according to row structure
- Destruction: No special cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLFrequencyTable.render] --> B[templates.template("frequency_table.html")]
    A --> C[Content processing logic]
    C --> B
```

## Raises:
- None explicitly raised by this implementation
- Inherited exceptions from parent class FrequencyTable may be raised during initialization

## Example:
```python
# Typical instantiation and usage in report generation
from ydata_profiling.report.presentation.flavours.html.frequency_table import HTMLFrequencyTable

# Create frequency table with sample data
rows = [
    ["Category A", 100],
    ["Category B", 75],
    ["Category C", 50]
]

# Instantiate the HTML renderer
html_table = HTMLFrequencyTable(rows, redact=False)

# Generate HTML output
html_output = html_table.render()
# Returns properly formatted HTML string
```

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable.render` · *method*

## Summary:
Generates HTML markup for a frequency table presentation element by rendering template content with appropriate row data structures.

## Description:
This method handles the rendering of frequency table content into HTML format, supporting both single-level and nested row structures. It determines the appropriate template rendering strategy based on the structure of the content's rows attribute and processes the data accordingly. This logic is separated into its own method to encapsulate the complexity of handling different row data structures while maintaining clean separation of concerns within the HTML presentation layer.

The method implements different rendering paths:
- When rows contain nested lists (multi-level frequency data), it iterates through each level and renders them separately
- When rows contain simple data structures, it renders them directly

## Args:
    None

## Returns:
    str: HTML string containing the rendered frequency table structure

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.content must be a dictionary containing a "rows" key
        - self.content["rows"] must be iterable
        - The template "frequency_table.html" must be available in the templates module
        - self.content["rows"][0] must exist for type checking
    Postconditions:
        - Returns valid HTML string representation of the frequency table
        - The returned HTML maintains proper structure regardless of row nesting level

## Side Effects:
    - Calls templates.template() which may involve file system I/O or template loading operations
    - Uses the templates module for HTML generation

