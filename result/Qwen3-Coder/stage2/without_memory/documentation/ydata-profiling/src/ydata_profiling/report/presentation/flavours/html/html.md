# `html.py`

## `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML` · *class*

## Summary:
Represents an HTML content item that renders raw HTML content directly.

## Description:
The HTMLHTML class is a concrete implementation of the abstract HTML class designed specifically for rendering raw HTML content. It serves as a wrapper for HTML strings that can be directly embedded in HTML documents. This class is part of the HTML presentation flavour system and is typically used when raw HTML needs to be inserted into reports without additional processing or formatting.

This class exists as a distinct abstraction to provide a standardized interface for HTML content within the reporting framework, ensuring consistency in how HTML elements are handled across different presentation formats.

## State:
- content: dict containing the HTML content under the key "html"
  - Type: dict
  - Valid values: Must contain a key "html" with string value
  - Invariant: The content dictionary must have an "html" key with valid HTML string content
- item_type: str set to "html" by the parent constructor
  - Type: str
  - Valid values: Always "html"
  - Invariant: Set once during initialization and remains constant

## Lifecycle:
- Creation: Instantiate with HTMLHTML(content_string) where content_string is a valid HTML string
- Usage: Call render() method to retrieve the raw HTML content
- Destruction: No special cleanup required; uses standard Python object destruction

## Method Map:
```mermaid
graph TD
    A[HTMLHTML] --> B[render]
    B --> C{Return self.content["html"]}
```

## Raises:
- No explicit exceptions raised by __init__ as it inherits from HTML which handles validation
- The render method itself doesn't raise exceptions but assumes content["html"] exists

## Example:
```python
# Create HTML content item
html_content = "<p>This is a paragraph</p>"
html_item = HTMLHTML(html_content)

# Render the content
rendered_html = html_item.render()
# Returns: "<p>This is a paragraph</p>"
```

### `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML.render` · *method*

## Summary:
Returns the HTML content stored in the object's content dictionary.

## Description:
This method extracts and returns the HTML string content that was originally passed to the constructor. It serves as the concrete implementation of the abstract render method defined in the parent Renderable class, providing the specific rendering behavior for HTML content within the HTML presentation flavour.

## Args:
    None

## Returns:
    str: The HTML content string stored under the "html" key in the content dictionary.

## Raises:
    KeyError: If the "html" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The content dictionary must contain a key "html" with a string value.
    Postconditions: The returned string is identical to the HTML content originally provided to the constructor.

## Side Effects:
    None

