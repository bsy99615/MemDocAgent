# `html.py`

## `src.ydata_profiling.report.presentation.core.html.HTML` · *class*

## Summary:
HTML is a presentation component that encapsulates raw HTML content for use in report generation.

## Description:
The HTML class serves as a container for raw HTML content within the ydata-profiling report generation framework. It inherits from ItemRenderer, which itself extends Renderable, establishing it as a fundamental building block for presentation elements. This class is designed to hold HTML content that will be rendered as-is in the final report output.

The class is intentionally abstract with a NotImplementedError in its render method, requiring concrete implementations to provide actual rendering logic. This design pattern ensures that all presentation components implement their own rendering behavior while maintaining a consistent interface throughout the reporting system.

## State:
- content (str): The raw HTML content to be rendered. This is stored in the parent Renderable's content dictionary under the key "html".
- item_type (str): Set to "html" by the constructor, identifying this component type.
- All attributes inherited from Renderable:
  - content (dict): Dictionary containing the HTML content and optional metadata like name, anchor_id, and classes.
  - name (str): Optional identifier for the component.
  - anchor_id (str): Optional anchor identifier for linking.
  - classes (str): Optional CSS classes to apply.

## Lifecycle:
- Creation: Instantiate with HTML(content: str, **kwargs) where content is the raw HTML string and kwargs can include name, anchor_id, and classes.
- Usage: Typically used within report generation workflows where the render() method is called by framework components to obtain the rendered HTML output.
- Destruction: No special cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[HTML Constructor] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set content with html key]
    D --> E[Set item_type to "html"]
    E --> F[HTML.__repr__]
    F --> G[Return "HTML"]
    G --> H[HTML.render]
    H --> I[Raise NotImplementedError]
```

## Raises:
- NotImplementedError: Raised by the render() method to indicate that subclasses must implement this method.

## Example:
```python
# Create an HTML component with raw HTML content
html_component = HTML("<h1>Hello World</h1>")

# The component can be inspected
print(html_component)  # Outputs: HTML

# During report generation, the render method would be called
# which raises NotImplementedError in this base implementation
# render_result = html_component.render()  # Would raise NotImplementedError
```

### `src.ydata_profiling.report.presentation.core.html.HTML.__init__` · *method*

## Summary:
Initializes an HTML component with raw HTML content for presentation rendering.

## Description:
This method serves as the constructor for HTML presentation components, initializing an HTML item by delegating to the parent ItemRenderer class. It wraps the provided HTML content in a dictionary structure with key "html" and sets the item type to "html". This allows the HTML content to be properly rendered within the reporting framework.

## Args:
    content (str): Raw HTML string content to be wrapped and rendered
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor

## Returns:
    None: This method initializes the object state and returns nothing

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "html" 
    - Content structure: Stored as {"html": content} in parent class

## Constraints:
    Preconditions:
    - The content parameter must be a valid string containing HTML markup
    - The parent ItemRenderer class must be properly initialized
    - All kwargs must be valid arguments for the parent constructor

    Postconditions:
    - The object is initialized as an HTML-type renderable item
    - The HTML content is properly encapsulated for rendering

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.html.HTML.__repr__` · *method*

## Summary:
Returns a string representation of the HTML object, consistently identifying it as "HTML".

## Description:
This method provides a standardized string representation for HTML objects, enabling easy identification during debugging or logging. It is called during object inspection or when converting the object to a string context. The method is part of the HTML class hierarchy, inheriting from ItemRenderer, which establishes the base structure for presentation components.

## Args:
    None

## Returns:
    str: Always returns the literal string "HTML" regardless of the object's internal state.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned string is always "HTML" and does not depend on any instance attributes.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.html.HTML.render` · *method*

## Summary:
Renders HTML content by raising a NotImplementedError indicating that subclasses must implement this method.

## Description:
This method serves as an abstract interface for rendering HTML content within the presentation layer. It is part of the Renderable base class hierarchy and is intended to be overridden by concrete implementations. The method raises NotImplementedError to enforce that subclasses provide their own rendering logic. This approach ensures that all presentation components implement their own rendering behavior while maintaining a consistent interface.

Known callers include framework components that invoke the render method during report generation, typically during the finalization phase of report building when HTML content needs to be serialized for output.

## Args:
    None

## Returns:
    Any: This method is expected to return rendered HTML content, but raises NotImplementedError in the base implementation.

## Raises:
    NotImplementedError: Always raised by this base implementation, indicating that subclasses must override this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

