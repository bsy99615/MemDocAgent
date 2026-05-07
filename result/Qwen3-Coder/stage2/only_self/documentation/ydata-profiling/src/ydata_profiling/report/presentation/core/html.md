# `html.py`

## `src.ydata_profiling.report.presentation.core.html.HTML` · *class*

## Summary:
Represents an HTML content item in the report presentation layer that wraps raw HTML string content for rendering.

## Description:
The HTML class is a specialized renderer for HTML content within the ydata-profiling report generation system. It extends ItemRenderer to provide a structured way to handle raw HTML strings that should be rendered as-is in reports. This class serves as a container for HTML content while maintaining the standard interface expected by the presentation layer's rendering system.

This class is typically instantiated by report generators or other components that need to embed raw HTML content into the final report output. It provides a clean abstraction for HTML content that preserves the original HTML while integrating properly with the rest of the report's rendering pipeline.

The render() method is intentionally left unimplemented (raises NotImplementedError) as it's meant to be implemented by concrete rendering engines that know how to process HTML content for the target output format.

## State:
- content (str): The raw HTML string content to be rendered. This is stored in the parent Renderable's content dictionary under the key "html".
- item_type (str): Set to "html" by the constructor, identifying this item as HTML content.
- All inherited attributes from Renderable:
  - content (dict): Dictionary containing the HTML content and optional metadata (name, anchor_id, classes)
  - name (str): Optional name identifier for the item
  - anchor_id (str): Optional anchor ID for linking
  - classes (str): Optional CSS classes to apply

## Lifecycle:
- Creation: Instantiate with a required HTML content string and optional metadata parameters (name, anchor_id, classes)
- Usage: Typically used within a report generation context where render() is called by the presentation layer's rendering engine
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTML Constructor] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set content with html key]
    D --> E[Set item_type to "html"]
    E --> F[render() called by renderer]
    F --> G[NotImplementedError raised]
```

## Raises:
- NotImplementedError: Raised when the render() method is called, indicating that concrete implementation is required by the rendering system

## Example:
```python
# Create HTML content item with basic content
html_item = HTML("<h1>Hello World</h1>", name="welcome_header")

# Create HTML content with additional metadata
html_with_metadata = HTML(
    "<p>This is a paragraph with <strong>bold text</strong>.</p>",
    name="paragraph_content",
    anchor_id="para1",
    classes="highlight"
)

# The HTML item would be processed by a renderer that implements the render() method
# The render() method is abstract and must be implemented by concrete renderers
```

### `src.ydata_profiling.report.presentation.core.html.HTML.__init__` · *method*

## Summary:
Initializes an HTML presentation component with the specified HTML content.

## Description:
Creates an HTML item renderer that wraps raw HTML content for presentation purposes. This method sets up the internal structure required for rendering HTML content within the reporting framework.

## Args:
    content (str): Raw HTML content to be wrapped and rendered
    **kwargs: Additional keyword arguments passed to parent constructors (name, anchor_id, classes)

## Returns:
    None: This method initializes the object's state rather than returning a value

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "html"
    - self.content: Dictionary containing {"html": content} plus any additional metadata from kwargs

## Constraints:
    Preconditions:
    - content must be a string containing valid HTML markup
    - All kwargs must be valid parameters for the parent Renderable class
    
    Postconditions:
    - The instance is properly initialized with item_type="html"
    - The content is stored in a dictionary format under the "html" key
    - Any additional metadata from kwargs is properly integrated into the content dictionary

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.html.HTML.__repr__` · *method*

## Summary:
Returns a string representation of the HTML object indicating its type.

## Description:
This method provides a standardized string representation for HTML objects, returning the literal string "HTML". It is called when the built-in repr() function is used on an HTML instance or when the object is displayed in interactive environments.

## Args:
    None

## Returns:
    str: The string "HTML" indicating the object type.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "HTML"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.html.HTML.render` · *method*

## Summary:
Returns the raw HTML content stored in the HTML item for presentation.

## Description:
This method implements the abstract render interface required by the Renderable base class. It provides the mechanism to extract and return the HTML content that was originally provided during object initialization. This method is typically called during report generation when the presentation layer needs to render HTML elements.

The render method is part of the presentation layer architecture that converts data representations into HTML output for web-based reports.

## Args:
    None

## Returns:
    str: The raw HTML string content stored in the HTML item's content dictionary under the "html" key.

## Raises:
    NotImplementedError: This method is not implemented in the base HTML class and must be overridden by subclasses.

## State Changes:
    Attributes READ: 
    - self.content: Reads the "html" key from the content dictionary
    - self.item_type: Accesses the item type (inherited from ItemRenderer)

## Constraints:
    Preconditions:
    - The HTML instance must have been properly initialized with valid content
    - The content dictionary must contain an "html" key with string value
    
    Postconditions:
    - The returned value is the exact HTML string that was provided during initialization

## Side Effects:
    None

