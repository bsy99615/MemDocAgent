# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.html.duplicate.to_html` · *function*

## Summary:
Converts a pandas DataFrame to HTML format with specific styling and handles empty DataFrames by displaying a descriptive message.

## Description:
This function transforms a pandas DataFrame into an HTML table representation with predefined CSS classes for styling. It specifically formats duplicate data tables for presentation in HTML reports. When the input DataFrame is empty, it injects a descriptive message row to indicate that no duplicate rows were found in the dataset.

The function is part of the HTML presentation flavour for data profiling reports and is designed to be used internally by HTML-based duplicate data renderers. It provides a standardized way to display duplicate data findings in web-based reports while maintaining proper formatting and user experience.

## Args:
    df (pandas.DataFrame): A pandas DataFrame containing duplicate data to be converted to HTML. The DataFrame may be empty.

## Returns:
    str: An HTML string representing the formatted DataFrame table. For non-empty DataFrames, this is a standard HTML table with CSS classes. For empty DataFrames, it includes an additional message row indicating no duplicates were found.

## Raises:
    None: This function does not explicitly raise exceptions, though pandas DataFrame operations may raise exceptions if the input is invalid.

## Constraints:
    Preconditions:
    - Input must be a valid pandas DataFrame object
    - The DataFrame should contain data related to duplicate records (though this is not enforced)
    
    Postconditions:
    - Output is always a valid HTML string
    - Empty DataFrames are handled gracefully with appropriate messaging

## Side Effects:
    None: This function performs no I/O operations or external state mutations. It only processes the input DataFrame and returns HTML string.

## Control Flow:
```mermaid
flowchart TD
    A[Start to_html(df)] --> B{df.empty?}
    B -->|Yes| C[Replace <tbody> with message row]
    B -->|No| D[Generate standard HTML table]
    C --> E[Return HTML string]
    D --> E
```

## Examples:
```python
import pandas as pd

# Example 1: Non-empty DataFrame
duplicate_df = pd.DataFrame({
    'id': [1, 2, 3],
    'value': ['A', 'B', 'A']
})
html_output = to_html(duplicate_df)
# Returns HTML table with duplicate data

# Example 2: Empty DataFrame
empty_df = pd.DataFrame()
html_output = to_html(empty_df)
# Returns HTML table with message: "Dataset does not contain duplicate rows."
```

## `src.ydata_profiling.report.presentation.flavours.html.duplicate.HTMLDuplicate` · *class*

## Summary:
HTMLDuplicate is an HTML presentation component that renders duplicate data findings as styled HTML content for data profiling reports.

## Description:
The HTMLDuplicate class implements the HTML rendering functionality for duplicate data visualization within data profiling reports. It extends the abstract Duplicate base class and provides concrete HTML rendering capabilities by converting duplicate data into properly formatted HTML tables using the to_html utility function and Jinja2 templating.

This component is part of the HTML presentation flavour of the ydata-profiling library and is specifically designed to integrate duplicate data findings into web-based reporting systems. It is typically instantiated and used internally by the report generation pipeline when HTML output is required for duplicate data sections.

The class follows the pattern of HTML presentation components in the ydata-profiling framework, where data is transformed through utility functions and then rendered using Jinja2 templates for consistent styling and layout.

## State:
- Inherits all attributes from Duplicate parent class:
  - item_type: str - Set to "duplicate" indicating the type of rendered item
  - content: dict - Contains the duplicate DataFrame under the key "duplicate"
  - name: str - Optional identifier for the component instance
  - anchor_id: str - Optional HTML anchor identifier for linking
  - classes: str - Optional CSS classes for styling

## Lifecycle:
- Creation: Instantiated with Duplicate constructor parameters (name, duplicate DataFrame)
- Usage: Called by report generation system when rendering HTML content for duplicate data sections
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLDuplicate.render] --> B[to_html(self.content["duplicate"])]
    B --> C[templates.template("duplicate.html").render()]
    C --> D[Return HTML string]
```

## Raises:
- None explicitly raised by HTMLDuplicate itself
- May propagate exceptions from to_html utility function or Jinja2 template rendering
- Inherits any exceptions that might occur during Duplicate parent class initialization

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.duplicate import HTMLDuplicate

# Create sample duplicate data
duplicate_data = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'value': ['A', 'B', 'A', 'C']
})

# Create HTMLDuplicate instance
duplicate_renderer = HTMLDuplicate(name="sample_duplicates", duplicate=duplicate_data)

# Render to HTML (typically called by report generation system)
html_output = duplicate_renderer.render()
# Returns formatted HTML string containing duplicate data table with appropriate styling
```

### `src.ydata_profiling.report.presentation.flavours.html.duplicate.HTMLDuplicate.render` · *method*

## Summary:
Renders duplicate data findings as an HTML-formatted string for inclusion in data profiling reports.

## Description:
Converts duplicate DataFrame content into HTML format and integrates it into a pre-defined HTML template. This method serves as the HTML presentation layer for duplicate data visualization, transforming structured duplicate information into a web-friendly format suitable for reporting.

The method is an implementation of the abstract render() method inherited from the Duplicate base class. It specifically handles the HTML rendering of duplicate data by converting the duplicate DataFrame to HTML format using the to_html utility function, then combining it with other content using Jinja2 templating.

This method is typically called during the report generation pipeline when HTML output is required for duplicate data sections, allowing users to visualize duplicate records found in their datasets.

## Args:
    None: This method does not accept any arguments beyond the implicit `self`.

## Returns:
    str: A complete HTML string containing the formatted duplicate data visualization, incorporating both the duplicate table and associated metadata.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying template rendering or HTML conversion may raise exceptions if inputs are malformed.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing duplicate data under the "duplicate" key
    - self.content["duplicate"]: The pandas DataFrame with duplicate records
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing a "duplicate" key with a valid pandas DataFrame value
    - The HTML template "duplicate.html" must be available in the templates system
    - The to_html function must be properly imported and accessible
    
    Postconditions:
    - Returns a valid HTML string that can be embedded in larger HTML documents
    - The returned HTML maintains proper formatting and styling conventions

## Side Effects:
    None: This method performs no external I/O operations or state mutations beyond returning the HTML string. It relies on the templates system for rendering, which is assumed to be properly configured.

