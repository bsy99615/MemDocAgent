# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable` · *class*

## Summary:
HTMLFrequencyTable renders frequency distribution data as HTML content, handling both single and multiple frequency table formats.

## Description:
This class provides HTML-specific rendering for frequency tables, extending the base FrequencyTable class. It is used in the ydata-profiling library to generate HTML representations of categorical data frequency distributions. The class handles two distinct data structures for rows: either a single list of frequency entries or a list of lists representing multiple frequency tables.

## State:
- Inherits all attributes from FrequencyTable including:
  - rows: list - A list of frequency table rows containing categorical values and their counts
  - redact: bool - Flag indicating whether sensitive data should be redacted in the output
  - item_type: str - Set to "frequency_table" by the constructor
  - content: dict - Dictionary containing the configuration data and inherited properties
- The content dictionary contains the data structure that gets passed to the Jinja2 template

## Lifecycle:
- Creation: Instantiate with rows (list of frequency data) and redact (bool) parameters, inheriting from FrequencyTable
- Usage: Call render() method to generate HTML string output
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLFrequencyTable.__init__] --> B[HTMLFrequencyTable.render]
    B --> C[templates.template("frequency_table.html").render]
```

## Raises:
- None explicitly raised by this implementation
- Inherits NotImplementedError from parent class if not properly overridden (though this is overridden here)

## Example:
```python
# Single frequency table case
rows = [
    {"value": "Category A", "count": 15},
    {"value": "Category B", "count": 8}
]
table = HTMLFrequencyTable(rows, redact=False)
html_output = table.render()

# Multiple frequency tables case  
rows = [
    [{"value": "Cat1", "count": 5}, {"value": "Cat2", "count": 3}],
    [{"value": "Cat3", "count": 7}, {"value": "Cat4", "count": 2}]
]
table = HTMLFrequencyTable(rows, redact=False)
html_output = table.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable.render` · *method*

## Summary:
Renders frequency table data as HTML by handling both single and multiple frequency table structures using Jinja2 templates.

## Description:
This method processes frequency table content and generates HTML output by delegating to the 'frequency_table.html' Jinja2 template. It handles two distinct data structures for frequency rows:

1. When rows is a list of lists (nested structure): Iterates through each sub-list and renders them separately with unique indices
2. When rows is a list of dictionaries (flat structure): Renders the entire structure directly

The method copies the content dictionary, removes the 'rows' key from the copy, and passes both the rows data and the remaining content to the template. This allows the template to access all original content fields while receiving the appropriate row data.

## Args:
    None - This is a method that operates on instance attributes

## Returns:
    str - HTML formatted string representing the frequency table(s)

## Raises:
    KeyError: If self.content does not contain required keys like "rows"
    TypeError: If self.content["rows"] is not iterable or if first element is neither list nor dict-like
    TemplateNotFound: If the 'frequency_table.html' template is not found in the template system

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing a "rows" key
    - self.content["rows"] must be iterable
    - The first element of self.content["rows"] must be either a list or a dictionary-like object
    - Templates must be available in the template system
    
    Postconditions:
    - Returns properly formatted HTML string
    - Handles both single and multiple frequency table structures correctly
    - Maintains all other content fields in self.content for template rendering

## Side Effects:
    - Calls templates.template() which may involve filesystem I/O for template loading
    - Invokes Jinja2 template rendering which may process template variables
    - May raise exceptions from template system if template is malformed or missing

