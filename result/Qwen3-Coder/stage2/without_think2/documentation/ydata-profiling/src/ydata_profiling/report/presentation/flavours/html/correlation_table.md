# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable` · *class*

## Summary:
HTMLCorrelationTable is a presentation layer component that renders correlation matrices as styled HTML tables using Jinja2 templating.

## Description:
This class implements the HTML-specific rendering logic for correlation tables by converting a pandas DataFrame correlation matrix into an HTML table with Bootstrap styling and formatting, then embedding it within a dedicated Jinja2 template. It inherits from CorrelationTable, which provides the core structure and content management for correlation data, and specializes the render() method for HTML output. The class specifically handles the conversion of correlation data into HTML format suitable for web presentation.

## State:
- Inherits all state from CorrelationTable parent class including:
  - item_type: str, set to "correlation_table" 
  - content: dict, containing correlation_matrix DataFrame and optional metadata (name, anchor_id, classes)
- Additional internal state:
  - correlation_matrix_html: str, temporary variable storing intermediate HTML table representation

## Lifecycle:
- Creation: Instantiate with a name (str) and correlation_matrix (pd.DataFrame); optional anchor_id and classes parameters
- Usage: Call render() method to generate complete HTML output
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLCorrelationTable.render] --> B[self.content["correlation_matrix"].to_html]
    B --> C[templates.template("correlation_table.html").render]
    C --> D[Return complete HTML string]
```

## Raises:
- AttributeError: If self.content["correlation_matrix"] does not have a to_html method
- KeyError: If self.content does not contain the "correlation_matrix" key
- Exception: Any exceptions raised by pandas DataFrame.to_html() or Jinja2 template rendering

## Example:
```python
import pandas as pd
from src.ydata_profiling.report.presentation.flavours.html.correlation_table import HTMLCorrelationTable

# Create sample correlation matrix
corr_matrix = pd.DataFrame({
    'A': [1.0, 0.5, -0.3],
    'B': [0.5, 1.0, 0.2],
    'C': [-0.3, 0.2, 1.0]
})

# Create HTML correlation table
html_table = HTMLCorrelationTable("Correlation Matrix", corr_matrix)

# Generate HTML output
html_output = html_table.render()
# Returns complete HTML with styled correlation matrix table
```

### `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable.render` · *method*

## Summary:
Generates HTML representation of a correlation matrix table with styled formatting and template integration.

## Description:
This method converts a correlation matrix DataFrame into an HTML table with specific CSS classes and numeric formatting, then embeds it within a Jinja2 template for complete HTML output. It's part of the HTML presentation flavour implementation for correlation tables.

## Args:
    None

## Returns:
    str: Complete HTML string containing the formatted correlation matrix table embedded in a correlation_table.html template

## Raises:
    AttributeError: If self.content["correlation_matrix"] does not have a to_html method
    KeyError: If self.content does not contain the "correlation_matrix" key
    Exception: Any exceptions raised by pandas DataFrame.to_html() or Jinja2 template rendering

## State Changes:
    Attributes READ: 
    - self.content (accessed via self.content["correlation_matrix"])
    
    Attributes WRITTEN: 
    - None

## Constraints:
    Preconditions:
    - self.content must contain a key "correlation_matrix" with a pandas DataFrame value
    - The correlation_matrix DataFrame must have a to_html method available
    - The templates.template("correlation_table.html") must be available in the template registry
    
    Postconditions:
    - Returns a properly formatted HTML string with CSS classes "correlation-table table table-striped" applied
    - The returned HTML includes the correlation matrix rendered with 3 decimal places using "{:.3f}".format
    - All content from self.content is passed to the template rendering context

## Side Effects:
    - Calls pandas DataFrame.to_html() method to generate HTML table
    - Invokes Jinja2 template rendering engine via templates.template()
    - Accesses global template registry via templates.template()

