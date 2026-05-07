# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable` · *class*

## Summary:
HTMLFrequencyTable renders frequency distribution data as HTML tables with support for both simple and nested row structures.

## Description:
The HTMLFrequencyTable class is a presentation layer component that transforms frequency distribution data into HTML table format. It extends the abstract FrequencyTable base class and provides HTML-specific rendering capabilities. This component is used in data profiling reports to display categorical data distributions in a web-friendly format.

The class handles two distinct data structures for frequency rows:
1. Simple rows: Each row is a dictionary with category and count information
2. Nested rows: Rows are organized in sublists, allowing for grouped frequency tables

This class is typically instantiated by report generation pipelines when creating HTML output for data profiling dashboards.

## State:
- Inherits all attributes from FrequencyTable parent class including:
  - rows: list - Collection of frequency data rows to display, where each row typically contains a category and its count/frequency
  - redact: bool - Flag indicating whether sensitive data should be redacted from display
  - item_type: str - Set to "frequency_table" identifying the component type
  - content: dict - Dictionary containing the configuration data including rows and redact flag
- Additional internal state managed by the render method:
  - Uses templates.template("frequency_table.html") for HTML generation
  - The content dictionary contains all configuration data passed during initialization

## Lifecycle:
- Creation: Instantiate with rows (list of frequency data) and optional redact flag
- Usage: Call render() method to generate HTML output
- Destruction: No special cleanup required, relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLFrequencyTable.render] --> B[templates.template("frequency_table.html")]
    B --> C[HTML Template Rendering]
```

## Raises:
- None explicitly raised by the render method itself
- Inheritance-based exceptions from FrequencyTable parent class may propagate:
  - TypeError: If rows parameter is not a list or redact parameter is not a boolean
  - NotImplementedError: If called on base FrequencyTable class (not applicable to HTMLFrequencyTable)

## Example:
```python
# Simple frequency table
rows = [
    {"category": "A", "count": 10},
    {"category": "B", "count": 5}
]
table = HTMLFrequencyTable(rows=rows, redact=False)
html_output = table.render()

# Nested frequency table
nested_rows = [
    [{"category": "A", "count": 10}, {"category": "B", "count": 5}],
    [{"category": "C", "count": 8}, {"category": "D", "count": 3}]
]
nested_table = HTMLFrequencyTable(rows=nested_rows, redact=True)
html_output = nested_table.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable.render` · *method*

## Summary:
Generates HTML markup for frequency table display by rendering Jinja2 templates with appropriate data structures based on the row format.

## Description:
This method renders frequency table data into HTML format by selecting the appropriate template rendering strategy based on the structure of the content's rows. When the first element of rows is a list (indicating grouped frequency data), it iterates through each group and renders them separately with incrementing index values. When the first element of rows is not a list (indicating a single frequency table), it renders the entire dataset directly with index 0. The method leverages the Jinja2 templating system to generate properly formatted HTML output.

## Args:
    None - This is an instance method that operates on self

## Returns:
    str - HTML string containing the formatted frequency table representation

## Raises:
    TypeError: If self.content["rows"] is not iterable or if self.content["rows"][0] doesn't exist
    KeyError: If self.content doesn't contain required keys like "rows"

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None - This method is read-only

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing a "rows" key
    - self.content["rows"] must be iterable
    - self.content["rows"][0] must exist when rows is not empty
    
    Postconditions:
    - Returns valid HTML string representation of frequency table
    - The returned HTML uses the frequency_table.html template
    - The idx parameter is correctly set for template rendering (0 for single group, incremental for multiple groups)

## Side Effects:
    None - This method is pure and doesn't cause any I/O operations or external service calls

