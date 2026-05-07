# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo` · *class*

## Summary:
HTMLVariableInfo is an HTML renderer that transforms variable metadata into HTML markup using a Jinja2 template.

## Description:
This class implements the HTML presentation layer for variable information in data profiling reports. It inherits from VariableInfo and specializes in generating HTML output for variable metadata such as names, types, counts, and statistics. The component acts as a bridge between structured variable data and its HTML representation for web-based visualization.

## State:
- Inherits all attributes from VariableInfo parent class
- `content` attribute: dictionary containing variable metadata fields (typically including name, type, count, missing values, etc.)
- Content dictionary keys must align with variables defined in the "variable_info.html" template

## Lifecycle:
- Creation: Instantiated with parent class constructor, requiring content dictionary parameter
- Usage: Call render() method to generate HTML string output
- Destruction: Standard Python object cleanup via garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLVariableInfo.render()] --> B[templates.template("variable_info.html")]
    B --> C[Jinja2 Template Engine]
    C --> D[HTML String Output]
```

## Raises:
- TemplateNotFound: When "variable_info.html" template cannot be located in the template system
- UndefinedError: When content dictionary lacks required keys referenced by the template
- Other Jinja2 template rendering exceptions

## Example:
```python
# Create HTML variable info component
content = {
    "name": "age",
    "type": "numeric",
    "count": 1000,
    "missing": 0
}
info = HTMLVariableInfo(content=content)

# Generate HTML representation
html_output = info.render()
# Returns HTML-formatted string for web display
```

### `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo.render` · *method*

## Summary:
Renders variable information content using an HTML template.

## Description:
Generates HTML output for variable information by rendering the 'variable_info.html' template with the content stored in the instance. This method serves as the presentation layer for displaying variable metadata in HTML reports.

## Args:
    None

## Returns:
    str: HTML-formatted string containing the rendered variable information

## Raises:
    jinja2.TemplateNotFound: When the 'variable_info.html' template is not found in the Jinja2 environment

## State Changes:
    Attributes READ: 
        - self.content: Dictionary containing the data to be rendered in the template
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The Jinja2 template environment must be properly initialized
        - The 'variable_info.html' template must exist in the template directory
        - self.content must be a dictionary that can be unpacked with ** operator
        
    Postconditions:
        - Returns a valid HTML string representation of the variable information
        - Does not modify the instance state

## Side Effects:
    None - This method is pure and has no side effects beyond template rendering

