# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample` · *class*

## Summary:
HTMLSample is a concrete implementation of the Sample class that renders data samples as Bootstrap-styled HTML tables for report presentation.

## Description:
This class specializes the abstract Sample base class to provide HTML-specific rendering capabilities. It transforms sample data (typically a pandas DataFrame) into a Bootstrap-styled HTML table by leveraging the DataFrame's built-in `to_html()` method and integrating it with a Jinja2 template. The class serves as a bridge between data samples and their HTML presentation in profiling reports, ensuring consistent styling and formatting.

## State:
- Inherits all attributes from Sample parent class including:
  - name: str - Human-readable identifier for the sample, used for labeling in reports
  - sample: pd.DataFrame - The actual sample data to be displayed, stored in the content dictionary
  - caption: Optional[str] - Optional descriptive text to accompany the sample data display
  - item_type: str - Fixed value "sample" identifying this as a sample-type report item
  - content: dict - Dictionary containing the sample data and caption information
  - anchor_id: Optional[str] - Unique identifier for HTML anchors, used for navigation in reports
  - classes: Optional[str] - CSS classes for styling the rendered sample output

## Lifecycle:
- Creation: Instantiate with name, sample DataFrame, and optional caption parameters (inherited from Sample parent class)
- Usage: Call the render() method to generate HTML output
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLSample.__init__] --> B[Sample.__init__]
    B --> C[Sets item_type="sample"]
    C --> D[Stores sample and caption in content]
    D --> E[HTMLSample.render]
    E --> F[self.content["sample"].to_html(classes="sample table table-striped")]
    F --> G[templates.template("sample.html").render(**self.content, sample_html=sample_html)]
    G --> H[Returns HTML string]
```

## Raises:
- No explicit exceptions raised by __init__
- May raise exceptions from:
  - pandas DataFrame.to_html() if sample data is malformed
  - Jinja2 template rendering if template "sample.html" is missing or invalid
  - Parent class initialization if validation fails

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.flavours.html.sample import HTMLSample

# Create a sample DataFrame
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create an HTMLSample instance
html_sample = HTMLSample(name="First Sample", sample=sample_data, caption="Example dataset")

# Render to HTML
html_output = html_sample.render()
# Returns a complete HTML string with Bootstrap-styled table
```

### `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample.render` · *method*

## Summary:
Generates an HTML table representation of a data sample with Bootstrap CSS styling for report presentation.

## Description:
This method converts a pandas DataFrame sample into an HTML table with Bootstrap-styled classes. It leverages the pandas DataFrame's built-in `to_html()` method to create the table structure, applies specific CSS classes for consistent styling, and integrates the result into a Jinja2 template for final HTML generation. This approach separates the HTML generation logic from the data processing, enabling clean separation of concerns in the report presentation layer.

## Args:
    None

## Returns:
    str: A complete HTML string containing a Bootstrap-styled table representation of the sample data.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The `self.content` dictionary must contain a key "sample" with a valid pandas DataFrame value
        - The HTML template "sample.html" must be available in the Jinja2 templates environment
        - All keys in `self.content` must be compatible with Jinja2 template rendering
    
    Postconditions:
        - The returned string is a valid HTML fragment containing a properly formatted Bootstrap table
        - The sample data is presented in tabular form with appropriate CSS classes

## Side Effects:
    - Invokes pandas DataFrame.to_html() method to generate HTML table markup
    - Calls Jinja2 template rendering engine to combine data with HTML template
    - May perform file I/O operations if template loading requires filesystem access

