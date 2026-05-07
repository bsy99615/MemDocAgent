# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample` · *class*

## Summary:
HTMLSample is a presentation layer component that renders sample data as an HTML table with Bootstrap styling.

## Description:
This class implements the HTML rendering for sample data items in the ydata-profiling report generation system. It extends the core Sample class and provides HTML-specific rendering capabilities by leveraging Jinja2 templating. The class is responsible for converting sample data into a styled HTML table that integrates seamlessly with Bootstrap-based report layouts.

The HTMLSample class is typically instantiated by the report generation pipeline when creating HTML presentations of sample data sections. It serves as a bridge between the core data representation and its HTML visualization.

## State:
- content: dict - Contains the sample data and associated metadata (sample DataFrame, caption, name, etc.)
- item_type: str - Set to "sample" by the parent constructor
- name: str - The name identifier for this sample item
- anchor_id: str - Unique identifier for HTML anchors
- classes: str - CSS classes for styling (typically "sample table table-striped")

## Lifecycle:
- Creation: Instantiated with a name, sample DataFrame, and optional caption through the parent Sample constructor
- Usage: Called by the report generation system when rendering HTML content, specifically via the render() method
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLSample.render()] --> B[content["sample"].to_html()]
    B --> C[templates.template("sample.html").render()]
    C --> D[Returns formatted HTML string]
```

## Raises:
- AttributeError: If self.content["sample"] doesn't exist or doesn't have a to_html() method
- KeyError: If required keys are missing from self.content dictionary
- TemplateNotFound: If the "sample.html" template is not found in the templates directory

## Example:
```python
# Create a sample instance
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
html_sample = HTMLSample("My Sample", sample_data, "First 3 rows")

# Render to HTML
html_output = html_sample.render()
# Returns HTML string with Bootstrap-styled table
```

### `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample.render` · *method*

## Summary:
Renders a sample DataFrame as an HTML table with Bootstrap styling within a sample template.

## Description:
This method converts a DataFrame sample into an HTML table representation and embeds it within a predefined HTML template. It's part of the HTML presentation flavour for report generation, specifically handling the rendering of sample data sections in reports.

## Args:
    None

## Returns:
    str: HTML string containing the formatted sample data table embedded in a template structure.

## Raises:
    None explicitly mentioned

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a key "sample" with a pandas DataFrame value
    - The DataFrame must support the .to_html() method
    - templates.template("sample.html") must return a valid Jinja2 template
    
    Postconditions:
    - Returns a properly formatted HTML string
    - The returned HTML includes Bootstrap CSS classes for styling

## Side Effects:
    None

