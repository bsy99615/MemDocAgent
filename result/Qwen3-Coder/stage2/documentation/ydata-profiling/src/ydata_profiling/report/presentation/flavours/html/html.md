# `html.py`

## `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML` · *class*

## Summary:
Represents an HTML content renderer that outputs raw HTML content from a content dictionary.

## Description:
The HTMLHTML class is a concrete implementation of the HTML base class designed specifically for rendering raw HTML content. It inherits from the HTML class which itself extends ItemRenderer, providing a standardized interface for HTML content within the ydata-profiling report presentation framework. This class serves as a bridge between structured HTML content stored in dictionaries and the final rendered HTML output.

This class is typically instantiated by the report generation system when HTML content needs to be embedded directly into reports without further processing. It's commonly used for embedding custom HTML snippets, styled content, or complex HTML structures that don't require additional transformation.

## State:
- content (dict): Dictionary containing HTML content under the "html" key, along with optional metadata such as name, anchor_id, and classes. The "html" key is required for proper rendering.
- item_type (str): Set to "html" by the parent class constructor, identifying this as an HTML item type.
- name (Optional[str]): Optional human-readable identifier accessible through the content dictionary.
- anchor_id (Optional[str]): Optional unique identifier for HTML anchors accessible through the content dictionary.
- classes (Optional[str]): Optional CSS classes for styling accessible through the content dictionary.

## Lifecycle:
- Creation: Instantiate with a content dictionary containing at least an "html" key, plus optional metadata parameters (name, anchor_id, classes)
- Usage: Call render() method to extract and return the HTML content string from the content dictionary
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLHTML.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[HTMLHTML.render]
    D --> E[Return content["html"]]
```

## Raises:
- KeyError: When the content dictionary doesn't contain the required "html" key
- TypeError: If content is not a dictionary or if the "html" value is not a string

## Example:
```python
# Create HTMLHTML instance with HTML content
html_content = {
    "html": "<div class='custom-content'><h1>Title</h1><p>Paragraph</p></div>",
    "name": "custom_section",
    "anchor_id": "section-anchor"
}
html_renderer = HTMLHTML(html_content)

# Render the HTML content
rendered_html = html_renderer.render()
# Returns: "<div class='custom-content'><h1>Title</h1><p>Paragraph</p></div>"
```

### `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML.render` · *method*

## Summary:
Returns the HTML content string from the content dictionary.

## Description:
This method extracts and returns the HTML content stored in the instance's content dictionary under the "html" key. It provides a concrete implementation of the abstract render method inherited from the HTML base class, enabling the HTMLHTML component to produce rendered output for report presentations.

The render method is typically called during the report generation pipeline when the presentation layer needs to convert the HTML content into its final string representation for inclusion in the generated report.

## Args:
    None

## Returns:
    str: The HTML content string stored in self.content["html"]

## Raises:
    KeyError: If the "html" key is not present in self.content dictionary

## State Changes:
    Attributes READ:
    - self.content: Dictionary containing HTML content and metadata
    - self.content["html"]: The HTML string content to be returned

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The instance must be properly initialized with content
    - The self.content dictionary must contain an "html" key with a string value
    - The instance should be a concrete implementation of HTML class

    Postconditions:
    - Returns the HTML string content without modifying the instance state
    - The returned string is identical to the content stored in self.content["html"]

## Side Effects:
    None: This method performs no I/O operations or external state mutations.

