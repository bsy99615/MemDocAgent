# `html.py`

## `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML` · *class*

## Summary:
Concrete implementation of HTML content rendering specifically designed for HTML output format.

## Description:
The HTMLHTML class represents a specialized renderer for HTML content within the ydata-profiling report generation system's HTML presentation flavour. It inherits from the base HTML class and provides a concrete implementation of the render() method that directly returns the raw HTML content stored in the content dictionary.

This class is part of the HTML presentation flavour architecture, which is responsible for generating HTML-formatted reports. It serves as a concrete implementation that bridges HTML content items to their final HTML string representation for web-based report outputs. The class is typically instantiated by report generators or presentation layer components that need to convert HTML content items into their final HTML string representation.

The motivation for this distinct abstraction is to provide a specific implementation for HTML output format while maintaining compatibility with the general HTML content interface. This allows the presentation layer to handle different output formats (HTML, JSON, etc.) through a consistent interface while providing format-specific implementations.

## State:
- Inherits all attributes from HTML parent class:
  - content (dict): Dictionary containing HTML content under the "html" key and optional metadata (name, anchor_id, classes)
  - item_type (str): Set to "html" by parent constructor
  - name (str): Optional name identifier for the item
  - anchor_id (str): Optional anchor ID for linking
  - classes (str): Optional CSS classes to apply
- No additional instance attributes beyond those inherited from parent class

## Lifecycle:
- Creation: Instantiate with HTML content string and optional metadata parameters (name, anchor_id, classes) via parent class constructor
- Usage: Called by HTML presentation renderer when processing HTML content items for HTML output generation
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLHTML Constructor] --> B[HTML.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set content with html key]
    D --> E[Set item_type to "html"]
    E --> F[render() called by HTML renderer]
    F --> G[Return self.content["html"]]
```

## Raises:
- None explicitly raised by __init__ method (inherits from parent class)
- The render() method itself doesn't raise exceptions but returns the HTML content directly

## Example:
```python
# Create HTML content item for HTML output
html_item = HTMLHTML("<h1>Hello World</h1>", name="welcome_header")

# Create HTML content with additional metadata for HTML output
html_with_metadata = HTMLHTML(
    "<p>This is a paragraph with <strong>bold text</strong>.</p>",
    name="paragraph_content",
    anchor_id="para1",
    classes="highlight"
)

# When processed by HTML renderer, this will return the raw HTML string
# html_item.render() returns "<h1>Hello World</h1>"
```

### `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML.render` · *method*

## Summary:
Returns the raw HTML content stored in the HTML item for presentation in HTML format.

## Description:
This method extracts and returns the HTML content that was originally provided during object initialization. It implements the render interface required by the presentation layer's rendering system for HTML content items.

The render method is part of the HTML presentation flavour that converts HTML content items into their final string representation for inclusion in web-based reports. This method is called by the HTML rendering engine during report generation when HTML elements need to be rendered.

## Args:
    None

## Returns:
    str: The raw HTML string content stored in the HTML item's content dictionary under the "html" key.

## Raises:
    KeyError: Raised if the "html" key is not present in the content dictionary, though this should not occur in properly initialized instances.

## State Changes:
    Attributes READ: 
    - self.content: Reads the "html" key from the content dictionary

## Constraints:
    Preconditions:
    - The HTMLHTML instance must have been properly initialized with valid content
    - The content dictionary must contain an "html" key with string value
    
    Postconditions:
    - The returned value is the exact HTML string that was provided during initialization

## Side Effects:
    None

