# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample` · *class*

## Summary:
HTMLSample is a concrete implementation of the Sample class that renders data samples as HTML tables with Bootstrap styling.

## Description:
The HTMLSample class specializes in presenting data samples from profiling reports in HTML format. It inherits from the Sample class and implements the abstract render() method to generate HTML output suitable for web-based report presentations. This class is specifically designed for use in HTML report generation where data samples need to be displayed in styled tables.

The class leverages Jinja2 templating to format the output and applies Bootstrap CSS classes to ensure consistent styling with the rest of the HTML report. It's typically used by report generators that produce HTML output for data profiling dashboards.

## State:
- Inherits all attributes from Sample and ItemRenderer parent classes
- content: dict - Contains the sample data and caption, with keys including "sample" (pandas DataFrame) and "caption" (Optional[str])
- item_type: str - Fixed value "sample" identifying this item type
- name: str - Human-readable identifier for the sample item
- anchor_id: Optional[str] - Unique identifier for HTML anchors
- classes: Optional[str] - CSS classes for styling

## Lifecycle:
- Creation: Instantiate with name string, pandas DataFrame sample, optional caption, and additional keyword arguments
- Usage: Call render() method to generate HTML representation of the sample data
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLSample.render()] --> B[sample.to_html()]
    B --> C[templates.template("sample.html")]
    C --> D[HTML output]
```

## Raises:
- AttributeError: May be raised if self.content["sample"] doesn't exist or doesn't have a to_html() method
- TemplateNotFound: May be raised if the "sample.html" template is not found in the templates directory
- Exception: Any exception raised by the to_html() method or Jinja2 template rendering process

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.sample import HTMLSample

# Create sample data
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create HTMLSample instance
html_sample = HTMLSample(
    name="First_100_rows", 
    sample=sample_data, 
    caption="Sample of dataset"
)

# Render to HTML
html_output = html_sample.render()
# Returns HTML string with Bootstrap-styled table
```

### `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample.render` · *method*

## Summary:
Generates HTML representation of a data sample with styled table formatting for report presentation.

## Description:
Converts a pandas DataFrame sample into an HTML table with Bootstrap styling and wraps it in a templated HTML structure for inclusion in profiling reports. This method implements the rendering logic specifically for HTML-based report generation, transforming raw sample data into properly formatted HTML content.

The method is called during the report generation pipeline when HTML output is required for sample data visualization. It leverages the existing pandas DataFrame.to_html() method for basic table conversion and applies Bootstrap CSS classes for consistent styling, then integrates the result into a predefined HTML template.

## Args:
    self: Instance of HTMLSample class containing sample data in self.content["sample"]

## Returns:
    str: HTML string containing the formatted sample data table wrapped in appropriate HTML structure for report display.

## Raises:
    None

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a "sample" key with a pandas DataFrame value
    - The DataFrame must be compatible with pandas DataFrame.to_html() method
    - The templates.template("sample.html") must be available in the template environment
    - self.content must be a dictionary containing all required template variables
    
    Postconditions:
    - Returns a valid HTML string with proper Bootstrap styling
    - The returned HTML is suitable for integration into larger HTML report documents

## Side Effects:
    None

