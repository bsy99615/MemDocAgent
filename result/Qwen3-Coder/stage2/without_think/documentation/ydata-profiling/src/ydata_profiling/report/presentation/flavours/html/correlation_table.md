# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable` · *class*

## Summary:
HTMLCorrelationTable renders correlation matrix data as an HTML table component for data profiling reports.

## Description:
The HTMLCorrelationTable class is a presentation layer component that transforms correlation matrix data into an HTML-rendered table. It extends the abstract CorrelationTable base class and provides concrete HTML rendering functionality for correlation matrices in data profiling dashboards. This component is used to display correlation relationships between variables in an HTML report format.

## State:
- `content`: dict, contains the correlation_matrix DataFrame under the key "correlation_matrix" inherited from parent class
- The class inherits all attributes from CorrelationTable including item_type, name, anchor_id, and classes

## Lifecycle:
Creation: Instantiate with a name string and correlation_matrix DataFrame, following CorrelationTable constructor requirements
Usage: Call render() method to generate HTML output for inclusion in profiling reports
Destruction: No special cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLCorrelationTable.render] --> B[correlation_matrix.to_html]
    B --> C[templates.template("correlation_table.html").render]
    C --> D[HTML output string]
```

## Raises:
- None explicitly raised by this implementation
- Inherits any exceptions from parent class CorrelationTable construction

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.correlation_table import HTMLCorrelationTable

# Create a correlation matrix
corr_matrix = pd.DataFrame({
    'A': [1.0, 0.5, -0.3],
    'B': [0.5, 1.0, 0.2],
    'C': [-0.3, 0.2, 1.0]
})

# Create HTML correlation table component
html_corr_table = HTMLCorrelationTable("My Correlation Table", corr_matrix)

# Render to HTML
html_output = html_corr_table.render()
# Returns HTML string with styled correlation table
```

### `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable.render` · *method*

## Summary:
Converts a correlation matrix DataFrame into an HTML table representation and renders it using a Jinja2 template.

## Description:
This method transforms the correlation matrix stored in the component's content into an HTML table with specific CSS classes for styling. It leverages pandas' built-in HTML rendering capabilities with formatted floating-point numbers and integrates the result into a predefined HTML template structure.

The method is part of the HTML presentation flavour implementation for correlation tables, providing the concrete rendering logic that was abstract in the parent class. This separation allows for different presentation formats (HTML, JSON, etc.) while maintaining a consistent interface.

## Args:
    None

## Returns:
    str: A complete HTML string containing the formatted correlation table rendered within the correlation_table.html template structure.

## Raises:
    None explicitly raised, though underlying methods may raise exceptions if:
    - self.content["correlation_matrix"] is not a valid pandas DataFrame
    - templates.template("correlation_table.html") fails to load the template
    - The template rendering process encounters errors

## State Changes:
    Attributes READ:
    - self.content: Dictionary containing the correlation_matrix DataFrame under the key "correlation_matrix"
    
    Attributes WRITTEN:
    - None

## Constraints:
    Preconditions:
    - self.content must contain a key "correlation_matrix" with a valid pandas DataFrame value
    - The correlation_matrix DataFrame must support the .to_html() method
    - The templates.template("correlation_table.html") must be able to successfully load the template
    
    Postconditions:
    - Returns a properly formatted HTML string with the correlation matrix displayed as a table
    - The returned HTML includes appropriate CSS classes for styling

## Side Effects:
    - Calls pandas DataFrame.to_html() method to generate HTML table
    - Invokes Jinja2 template rendering system
    - May perform file I/O operations when loading the HTML template

