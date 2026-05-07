# `html.py`

## `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML` · *class*

## Summary:
Concrete implementation of the HTML presentation component that renders raw HTML content.

## Description:
The HTMLHTML class provides a concrete implementation of the abstract HTML base class for rendering raw HTML content in report generation. It serves as a specialized component that directly returns stored HTML content without further processing, making it suitable for embedding pre-formatted HTML snippets into reports.

This class is instantiated when raw HTML content needs to be embedded directly into a report without additional transformation or formatting. It acts as a bridge between raw HTML data and the report generation pipeline, ensuring that HTML content is preserved exactly as provided.

## State:
- content (dict): Dictionary containing the HTML content under the "html" key, inherited from the parent Renderable class
- item_type (str): Set to "html" by the parent class, identifying this component type
- All attributes inherited from Renderable:
  - content (dict): Dictionary containing the HTML content and optional metadata like name, anchor_id, and classes
  - name (str): Optional identifier for the component
  - anchor_id (str): Optional anchor identifier for linking
  - classes (str): Optional CSS classes to apply

## Lifecycle:
- Creation: Instantiate with HTMLHTML(content: str, **kwargs) where content is the raw HTML string and kwargs can include name, anchor_id, and classes
- Usage: Called during report generation when the framework invokes the render() method to obtain the raw HTML content
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLHTML Constructor] --> B[HTML.__init__]
    B --> C[ItemRenderer.__init__]
    C --> D[Renderable.__init__]
    D --> E[Set content with html key]
    E --> F[Set item_type to "html"]
    F --> G[HTMLHTML.render]
    G --> H[Return self.content["html"]]
```

## Raises:
- KeyError: If the "html" key is not present in the content dictionary, though this would indicate an invalid internal state

## Example:
```python
# Create an HTMLHTML component with raw HTML content
html_component = HTMLHTML("<div class='example'>Hello World</div>")

# During report generation, the render method returns the raw HTML
rendered_html = html_component.render()  # Returns: "<div class='example'>Hello World</div>"
```

### `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML.render` · *method*

## Summary:
Returns the raw HTML content stored in the component's content dictionary.

## Description:
This method retrieves and returns the HTML content that was originally provided during component initialization. It serves as the concrete implementation of the render method for HTML components, providing direct access to the stored HTML string.

The method is part of the HTMLHTML class, which is a concrete implementation of the abstract HTML base class. While the base HTML class defines a render method that raises NotImplementedError, the HTMLHTML class provides the actual implementation needed for rendering HTML content in the report generation pipeline.

This method is called during the report generation process when the framework needs to obtain the rendered HTML representation of this component. It accesses the HTML content stored in the component's content dictionary under the "html" key.

## Args:
    None

## Returns:
    str: The raw HTML content stored under the "html" key in the component's content dictionary.

## Raises:
    KeyError: If the "html" key is not present in the content dictionary, though this would indicate an invalid internal state.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The component must have been properly initialized with HTML content, ensuring self.content contains the "html" key.
    Postconditions: The returned string is identical to the HTML content provided during initialization.

## Side Effects:
    None

