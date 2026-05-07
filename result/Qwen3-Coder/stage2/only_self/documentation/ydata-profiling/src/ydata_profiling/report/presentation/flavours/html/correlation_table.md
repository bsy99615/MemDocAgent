# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable` · *class*

## Summary
HTMLCorrelationTable renders correlation matrices as styled HTML tables for web reporting.

## Description
This class implements HTML presentation logic for correlation matrix visualizations by extending CorrelationTable. It converts correlation matrix data into Bootstrap-styled HTML tables with three-decimal precision formatting. The component integrates with the ydata-profiling report generation system to produce web-friendly correlation analysis reports.

The render method processes the correlation matrix stored in self.content["correlation_matrix"], formats it with pandas DataFrame.to_html() using specific CSS classes ("correlation-table table table-striped"), and renders it through the "correlation_table.html" Jinja2 template.

## State
- self.content: Dictionary containing correlation matrix data and associated metadata. Must contain a "correlation_matrix" key with a pandas DataFrame-like object that supports the to_html() method interface.
- The correlation_matrix value should contain numeric correlation values typically ranging from -1 to 1.

## Lifecycle
- Creation: Instantiated with standard constructor parameters inherited from CorrelationTable parent class
- Usage: Called via render() method to generate HTML output for correlation matrix visualization
- Destruction: No special cleanup required; follows standard Python object lifecycle

## Method Map
```mermaid
graph TD
    A[HTMLCorrelationTable.render] --> B[content["correlation_matrix"].to_html]
    B --> C[templates.template("correlation_table.html").render]
    C --> D[Return HTML string]
```

## Raises
- AttributeError: If self.content["correlation_matrix"] does not have a to_html() method
- KeyError: If self.content does not contain the "correlation_matrix" key
- Exception: Any exceptions raised by the underlying to_html() method or Jinja2 template rendering

## Example
```python
# Typically created by report generation system
# Render correlation matrix to HTML
html_output = html_correlation_table.render()
# Returns HTML string with styled correlation matrix table
```

### `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable.render` · *method*

## Summary:
Converts a correlation matrix into a styled HTML table using Jinja2 templating.

## Description:
Processes a correlation matrix stored in self.content["correlation_matrix"] by converting it to HTML format with three-decimal precision and Bootstrap CSS classes. The resulting HTML is then rendered through the "correlation_table.html" template, which receives all content from self.content plus the formatted correlation_matrix_html variable. This method serves as the presentation layer for displaying correlation analysis results in HTML reports.

## Args:
    None

## Returns:
    str: HTML-formatted string containing a styled correlation matrix table with Bootstrap classes "correlation-table table table-striped".

## Raises:
    AttributeError: If self.content["correlation_matrix"] does not have a to_html() method.
    KeyError: If self.content does not contain the "correlation_matrix" key.
    Exception: Any exceptions raised by the underlying to_html() method or Jinja2 template rendering.

## State Changes:
    Attributes READ: 
    - self.content (dictionary containing correlation_matrix)
    - self.content["correlation_matrix"] (expected to be a pandas DataFrame or similar structure with to_html method)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing a "correlation_matrix" key
    - self.content["correlation_matrix"] must support the pandas DataFrame.to_html() method interface
    - The correlation_matrix should contain numeric correlation values between -1 and 1
    
    Postconditions:
    - Returns a properly formatted HTML string with correlation values rounded to 3 decimal places
    - The HTML includes CSS classes "correlation-table table table-striped" for styling
    - All content from self.content is passed to the template for rendering
    - The returned HTML maintains the structure expected by the correlation_table.html template

## Side Effects:
    None

