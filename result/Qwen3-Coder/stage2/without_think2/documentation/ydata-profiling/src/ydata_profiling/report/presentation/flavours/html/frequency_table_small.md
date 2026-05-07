# `frequency_table_small.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table_small.HTMLFrequencyTableSmall` · *class*

## Summary:
HTMLFrequencyTableSmall is a concrete implementation that renders categorical frequency data as HTML markup using a Jinja2 template.

## Description:
This class specializes the abstract FrequencyTableSmall to provide HTML-specific rendering capabilities. It takes categorical data rows and formats them into an HTML table structure by repeatedly rendering a template fragment for each row. The class is designed to be used within the ydata-profiling report generation pipeline where it transforms structured frequency data into presentation-ready HTML.

## State:
- Inherits all state from FrequencyTableSmall parent class:
  - item_type: str, set to "frequency_table_small" during initialization
  - content: dict, containing:
    - rows: List[Any], the categorical data rows to display
    - redact: bool, flag indicating whether sensitive data should be masked
  - name: Optional[str], optional identifier for the table (inherited from Renderable)
  - anchor_id: Optional[str], optional HTML anchor identifier (inherited from Renderable)
  - classes: Optional[str], optional CSS classes for styling (inherited from Renderable)

## Lifecycle:
- Creation: Instantiate with rows (List[Any]) and redact (bool) parameters, optionally providing name, anchor_id, and classes via keyword arguments. The constructor inherits from FrequencyTableSmall and validates these parameters.
- Usage: Call render() method to generate HTML output by processing each row through a Jinja2 template
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLFrequencyTableSmall.render] --> B[templates.template("frequency_table_small.html")]
    B --> C[jinja2.Template.render]
```

## Raises:
- TypeError: If required parameters rows or redact are not provided during initialization (inherited from parent)
- NotImplementedError: When render() method is called on the parent class (inherited from parent, but overridden here)

## Example:
```python
# Create a frequency table with sample data
rows = [("Category A", 10), ("Category B", 5), ("Category C", 3)]
table = HTMLFrequencyTableSmall(rows=rows, redact=False)

# Render to HTML
html_output = table.render()
# Returns HTML string with formatted frequency table
```

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table_small.HTMLFrequencyTableSmall.render` · *method*

## Summary:
Generates HTML markup for a small frequency table by rendering template fragments for each row of categorical data.

## Description:
This method implements the rendering logic for HTML frequency tables, taking the stored categorical data rows and formatting them using a Jinja2 template. It processes each row sequentially, applying the template with appropriate context variables including the row data, index position, and shared configuration parameters.

## Args:
    None

## Returns:
    str: Complete HTML string containing the formatted frequency table with all rows rendered

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a "rows" key with a list of data rows
    - self.content must contain all other required configuration parameters for the template
    - The "rows" key in self.content must be iterable
    
    Postconditions:
    - Returns a properly formatted HTML string
    - All rows in self.content["rows"] are processed exactly once
    - Template rendering preserves the structure defined in frequency_table_small.html

## Side Effects:
    - Calls templates.template() to retrieve the Jinja2 template
    - Invokes the template's render() method for each row
    - May perform I/O operations during template rendering if the template accesses external resources

