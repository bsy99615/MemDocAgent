# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.html.duplicate.to_html` · *function*

## Summary:
Converts a pandas DataFrame containing duplicate data into styled HTML table format with appropriate handling for empty datasets.

## Description:
Transforms a pandas DataFrame into an HTML table with Bootstrap styling classes for display in web-based data profiling reports. When the input DataFrame is empty, it inserts a descriptive message indicating no duplicates were found. This function is part of the HTML presentation flavour for duplicate data reporting in the ydata-profiling library.

## Args:
    df (pd.DataFrame): A pandas DataFrame containing duplicate data records to be converted to HTML. May be empty.

## Returns:
    str: HTML table string with Bootstrap classes applied. For empty DataFrames, includes a message row indicating no duplicates were found.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - Input must be a valid pandas DataFrame object
    - DataFrame columns should be compatible with pandas.to_html() method
    
    Postconditions:
    - Output is a properly formatted HTML string with table structure
    - Empty DataFrames result in HTML with appropriate placeholder message

## Side Effects:
    None - This function is pure and has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start to_html(df)] --> B{df.empty?}
    B -->|Yes| C[Generate HTML with df.to_html()]
    C --> D[Replace <tbody> with message row]
    D --> E[Return modified HTML]
    B -->|No| F[Generate HTML with df.to_html()]
    F --> G[Return HTML unchanged]
```

## Examples:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.duplicate import to_html

# Example with duplicate data
duplicate_df = pd.DataFrame({
    'id': [1, 2, 3],
    'value': ['a', 'b', 'c']
})
html_output = to_html(duplicate_df)
# Returns HTML table with Bootstrap classes

# Example with empty DataFrame
empty_df = pd.DataFrame()
html_output = to_html(empty_df)
# Returns HTML table with message row indicating no duplicates
```

## `src.ydata_profiling.report.presentation.flavours.html.duplicate.HTMLDuplicate` · *class*

## Summary:
HTMLDuplicate is a concrete implementation that renders duplicate data findings as HTML content using Jinja2 templates.

## Description:
The HTMLDuplicate class extends the Duplicate abstract class and provides HTML rendering functionality for duplicate data reports in the ydata-profiling library. It overrides the render() method to generate properly formatted HTML output by converting duplicate data to HTML tables and rendering them within a Jinja2 template.

## State:
- `content` (dict): Inherited from parent class Duplicate, contains duplicate data under the key "duplicate"
- `name` (str): Inherited from parent class Duplicate, identifies this duplicate report instance  
- `item_type` (str): Inherited from parent class Duplicate, set to "duplicate" to identify this as a duplicate report type

## Lifecycle:
- Creation: Instantiate with a name string and a pandas DataFrame containing duplicate data, inheriting from Duplicate parent class
- Usage: Called during report generation when HTML rendering of duplicate data is required via the render() method
- Destruction: No special cleanup required; relies on parent class and Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLDuplicate.render] --> B[to_html(self.content["duplicate"])]
    B --> C[templates.template("duplicate.html").render()]
    C --> D[Returns HTML string]
```

## Raises:
- No explicit exceptions raised by HTMLDuplicate.__init__ as it inherits from Duplicate
- Potential exceptions from to_html() function if DataFrame processing fails
- Potential exceptions from templates.template() if template loading fails

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.duplicate import HTMLDuplicate

# Create duplicate data
duplicate_df = pd.DataFrame({'id': [1, 2, 3], 'value': ['a', 'b', 'c']})

# Create HTMLDuplicate instance
html_duplicate = HTMLDuplicate(name="my_duplicates", duplicate=duplicate_df)

# Render to HTML (this would be called internally during report generation)
html_output = html_duplicate.render()
# Returns HTML string with duplicate data rendered in template format
```

### `src.ydata_profiling.report.presentation.flavours.html.duplicate.HTMLDuplicate.render` · *method*

## Summary:
Converts duplicate data findings into HTML format for web-based data profiling reports.

## Description:
Generates HTML representation of duplicate data findings by converting the duplicate DataFrame into styled HTML table format and embedding it within a complete HTML template. This method is part of the HTML presentation flavour implementation for duplicate data reporting in the ydata-profiling library.

## Args:
    None: This method takes no parameters beyond the implicit self reference.

## Returns:
    str: A complete HTML string containing the formatted duplicate data report with Bootstrap styling.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying template rendering or data conversion may raise exceptions.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing duplicate data under the "duplicate" key
    
    Attributes WRITTEN: 
    - None: This method does not modify object state.

## Constraints:
    Preconditions:
    - The object must be properly initialized with duplicate data in self.content["duplicate"]
    - The duplicate data must be a valid pandas DataFrame
    - The "duplicate.html" template must be available in the templates system
    
    Postconditions:
    - Returns a valid HTML string with properly formatted duplicate data
    - The returned HTML includes Bootstrap styling classes for web display

## Side Effects:
    - Template rendering via Jinja2 engine
    - Calls to to_html() function for DataFrame conversion
    - Potential I/O operations during template loading

