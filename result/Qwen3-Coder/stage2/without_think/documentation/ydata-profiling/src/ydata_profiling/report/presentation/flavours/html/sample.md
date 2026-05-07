# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample` · *class*

## Summary:
HTMLSample is a presentation layer class that renders data samples as HTML tables with Bootstrap styling for use in profiling report web interfaces.

## Description:
The HTMLSample class implements the rendering logic for data samples specifically for HTML-based report presentations. It extends the abstract Sample class and provides concrete implementation of the render() method that generates HTML markup for displaying sample data in web browsers. This class is part of the HTML flavour presentation layer in the ydata-profiling library, designed to create visually appealing sample displays with Bootstrap CSS classes.

The class is typically instantiated by report generation components that need to present sample data in HTML format. It leverages the parent Sample class's structure for holding sample data and metadata, then transforms this into HTML using Jinja2 templating and pandas' built-in HTML rendering capabilities.

## State:
- Inherits all attributes from Sample parent class including:
  - name: str - Human-readable identifier for the sample item
  - sample: pd.DataFrame - The actual data sample to be displayed, stored in content["sample"]
  - caption: Optional[str] - Optional descriptive text for the sample, stored in content["caption"] 
  - item_type: str - Fixed value "sample" identifying this item type
  - content: dict - Dictionary containing the sample data and caption under keys "sample" and "caption"
  - anchor_id: Optional[str] - Unique identifier for HTML anchors (inherited from ItemRenderer)
  - classes: Optional[str] - CSS classes for styling (inherited from ItemRenderer)

## Lifecycle:
- Creation: Instantiate with name (str), sample (pd.DataFrame), and optional caption (str) parameters, inheriting from Sample constructor
- Usage: Call render() method to generate HTML markup for displaying a data sample in a profiling report with Bootstrap styling
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLSample.render()] --> B[self.content["sample"].to_html()]
    B --> C[templates.template("sample.html").render()]
    C --> D[Return HTML string]
```

## Raises:
- AttributeError: If self.content["sample"] is not properly initialized or doesn't have a to_html() method
- TemplateNotFound: If the "sample.html" template is not available in the Jinja2 environment
- Exception: Any exception raised by the to_html() method or Jinja2 template rendering process

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.sample import HTMLSample

# Create sample data
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create HTMLSample instance
html_sample = HTMLSample(
    name="first_sample", 
    sample=sample_data, 
    caption="First 3 rows of data"
)

# Render to HTML
html_output = html_sample.render()
# Returns HTML string with Bootstrap-styled table
```

### `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample.render` · *method*

## Summary:
Generates HTML markup for displaying a data sample in a profiling report with Bootstrap styling.

## Description:
Converts a data sample into an HTML table representation with Bootstrap CSS classes and renders it using a Jinja2 template. This method is part of the HTML presentation flavour implementation for data profiling reports, specifically designed to render sample data items within the report interface.

The method takes the sample data stored in `self.content["sample"]`, converts it to an HTML table with Bootstrap styling, and then uses a predefined template to incorporate this HTML into a complete report section. This implementation is specific to the HTML presentation flavour and overrides the abstract render method from the parent Sample class.

## Args:
    None

## Returns:
    str: Complete HTML string containing the formatted sample data section with proper Bootstrap styling

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ:
    - self.content: Dictionary containing the sample data and associated metadata
    - self.content["sample"]: Pandas DataFrame containing the actual sample data to be rendered
    - self.content["caption"]: Optional caption for the sample (if present)

    Attributes WRITTEN:
    - None

## Constraints:
    Preconditions:
    - self.content must contain a key "sample" with a valid pandas DataFrame value
    - self.content must contain a key "caption" with a string or None value
    - The sample DataFrame must be compatible with pandas DataFrame.to_html() method
    - The HTML template "sample.html" must exist in the template environment
    
    Postconditions:
    - Returns a valid HTML string with properly formatted sample data
    - The returned HTML follows the expected structure for report presentation

## Side Effects:
    - Calls pandas DataFrame.to_html() method to generate table HTML
    - Invokes Jinja2 template rendering system to process the final HTML
    - No external service calls or I/O operations beyond standard Python libraries

