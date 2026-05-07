# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable` · *class*

## Summary:
HTMLCorrelationTable is a presentation layer component that renders correlation matrices as HTML tables with Bootstrap styling.

## Description:
This class implements the HTML rendering for correlation tables in the ydata-profiling report generation system. It extends the abstract CorrelationTable class and provides a concrete implementation of the render() method that generates HTML output suitable for web presentation. The component is typically instantiated by report generation pipelines when creating HTML reports containing correlation matrix visualizations.

## State:
- correlation_matrix: pandas.DataFrame stored in self.content["correlation_matrix"] - contains the correlation coefficients to be rendered
- name: str - optional name identifier for the correlation table
- content: dict - dictionary containing the correlation_matrix under the key "correlation_matrix"
- All inherited attributes from ItemRenderer base class

## Lifecycle:
- Creation: Instantiated with a correlation_matrix DataFrame and optional name parameter
- Usage: Called by report generation systems when rendering HTML content containing correlation tables
- Destruction: No special cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLCorrelationTable.__init__] --> B[ItemRenderer.__init__]
    B --> C[CorrelationTable.__init__]
    C --> D[HTMLCorrelationTable.render]
    D --> E[templates.template("correlation_table.html").render]
    D --> F[self.content["correlation_matrix"].to_html]
```

## Raises:
- TypeError: If correlation_matrix is not a pandas DataFrame
- AttributeError: If correlation_matrix doesn't have a to_html method
- TemplateNotFound: If the "correlation_table.html" template is not found in the templates directory

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.correlation_table import HTMLCorrelationTable

# Create sample correlation matrix
data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
correlation_matrix = data.corr()

# Create HTML correlation table renderer
html_renderer = HTMLCorrelationTable(name="Sample Correlation", correlation_matrix=correlation_matrix)

# Render to HTML
html_output = html_renderer.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable.render` · *method*

## Summary:
Converts a correlation matrix DataFrame into HTML format and renders it using a Jinja2 template.

## Description:
This method transforms the correlation matrix stored in `self.content["correlation_matrix"]` into an HTML table with specific formatting and styling. It serves as the HTML presentation layer for correlation table data within the ydata-profiling report generation pipeline.

The method is part of the HTML presentation flavour implementation and is called during the report generation process when HTML output is required for correlation tables. It leverages the Jinja2 templating engine to generate the final HTML structure.

## Args:
    None

## Returns:
    str: HTML string containing the formatted correlation table rendered with the correlation_table.html template

## Raises:
    AttributeError: If `self.content` does not contain a "correlation_matrix" key or if the correlation_matrix object does not have a `to_html` method
    jinja2.exceptions.TemplateNotFound: If the "correlation_table.html" template is not found
    jinja2.exceptions.UndefinedError: If required variables are missing from the template context
    Exception: Any other exceptions raised by the pandas DataFrame.to_html() method or Jinja2 template rendering process

## State Changes:
    Attributes READ: 
    - self.content (reads the "correlation_matrix" key)
    - self.content (passed to template rendering via **kwargs)

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - `self.content` must contain a "correlation_matrix" key with a pandas DataFrame value
    - The correlation_matrix must have a `to_html` method (typically a pandas DataFrame)
    - The template "correlation_table.html" must exist in the templates directory
    - The correlation_matrix should contain numeric data suitable for correlation display

    Postconditions:
    - Returns a properly formatted HTML string with correlation data
    - The returned HTML includes the correlation matrix table with CSS classes "correlation-table table table-striped"
    - All numeric values in the correlation matrix are formatted to 3 decimal places
    - The HTML structure follows the expected template layout

## Side Effects:
    None

