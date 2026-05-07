# `root.py`

## `src.ydata_profiling.report.presentation.core.root.Root` · *class*

## Summary:
Root is a specialized ItemRenderer that serves as the top-level container for report components in the ydata-profiling system, managing body content, footer, and styling information.

## Description:
The Root class represents the highest level container in the report presentation hierarchy. It inherits from ItemRenderer and is specifically designed to wrap the complete report structure including body content, footer, and styling configuration. This class acts as the entry point for report rendering and provides mechanisms for dynamic conversion of renderable components to different types during the report generation pipeline.

Root is instantiated with essential report components: a body (the main content), a footer (additional information), and styling configuration. It enforces a consistent structure for report containers while allowing for flexible content composition through its inheritance from ItemRenderer.

## State:
- item_type: str - Set to "report" by the constructor, identifying this component as a report container
- content: dict - Dictionary containing the core report structure with keys:
  - "body": Renderable - The main content of the report
  - "footer": Renderable - Additional information or metadata for the report
  - "style": Style - Styling configuration for the entire report
- name: str - Optional human-readable identifier for the report, stored in content dictionary
- anchor_id: str - Optional unique identifier for HTML anchors, stored in content dictionary
- classes: str - Optional CSS classes to apply to the rendered report, stored in content dictionary

## Lifecycle:
- Creation: Instantiate with name (str), body (Renderable), footer (Renderable), style (Style), and optional metadata parameters. The constructor initializes the parent ItemRenderer with item_type="report" and the specified content structure.
- Usage: Typically called during report generation when the complete report structure needs to be rendered. The render() method should be overridden by concrete implementations to provide actual rendering logic.
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[Root.__init__] --> B[ItemRenderer.__init__]
    B --> C[item_type="report"]
    C --> D[content={"body": body, "footer": footer, "style": style}]
    D --> E[Root.__repr__]
    E --> F[Returns "Root"]
    A --> G[Root.render]
    G --> H[NotImplementedError raised]
    A --> I[Root.convert_to_class]
    I --> J[Object class conversion]
    J --> K[flv applied to body/footer]
```

## Raises:
- NotImplementedError: Raised by the render() method, indicating that concrete implementations must override this method to provide actual rendering functionality.

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.core.renderable import Renderable

# Create a basic report structure
style = Style()
body = Renderable({"content": "Main report content"})
footer = Renderable({"content": "Report footer"})

# Create root container
root = Root(
    name="My Report",
    body=body,
    footer=footer,
    style=style
)

# The root can be converted to different types during processing
# root.convert_to_class(target_class, transform_function)
```

### `src.ydata_profiling.report.presentation.core.root.Root.__init__` · *method*

## Summary:
Initializes a Root object with report structure components including body, footer, and styling configuration.

## Description:
The Root.__init__ method sets up the foundational structure for a report by initializing the parent ItemRenderer class with a fixed item_type of "report" and a content dictionary containing the body, footer, and style components. This method establishes the core report container that wraps all other report elements.

This logic is encapsulated in its own method to maintain clean separation of concerns, ensuring that the Root class properly inherits from ItemRenderer while establishing the specific report structure requirements. The method delegates to the parent constructor to handle standard initialization while providing the specialized content structure needed for report containers.

## Args:
- name (str): Human-readable identifier for the report
- body (Renderable): Main content component of the report
- footer (Renderable): Footer component containing additional information
- style (Style): Styling configuration for the entire report
- **kwargs: Additional metadata parameters (name, anchor_id, classes) passed to parent constructor

## Returns:
    None: This method initializes the object's state but does not return a value

## Raises:
    No explicit exceptions raised by this method

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - self.item_type: Set to "report"
  - self.content: Dictionary containing "body", "footer", and "style" keys

## Constraints:
- Preconditions: 
  - body and footer must be Renderable instances
  - style must be a Style instance
  - name must be a string
- Postconditions:
  - self.item_type is set to "report"
  - self.content contains the required keys: "body", "footer", "style"

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.root.Root.__repr__` · *method*

## Summary:
Returns a string representation of the Root object, consistently identifying it as "Root".

## Description:
This method provides a standardized string representation for Root instances, enabling clear identification in debugging contexts and logging. It is invoked during object inspection or when converting the object to a string, such as in print statements or logging frameworks.

## Args:
    None

## Returns:
    str: Always returns the literal string "Root".

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned string is always "Root" regardless of the object's internal state.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.root.Root.render` · *method*

## Summary:
Renders the root report component by raising a NotImplementedError, indicating that concrete implementations must override this method.

## Description:
The render method in the Root class is an abstract interface that must be implemented by concrete subclasses. It raises NotImplementedError to enforce that all Root implementations provide their own rendering logic. This method is part of the rendering pipeline for report components and would typically be called during report generation to produce the final output representation.

Root is the top-level container for report components in the ydata-profiling system, containing body content, footer, and styling information. The render method serves as the entry point for generating the complete report output, though concrete implementations must provide the actual rendering logic.

## Args:
    **kwargs: Arbitrary keyword arguments that may be passed to the rendering process, though not utilized in the base implementation.

## Returns:
    Any: The return type is intentionally unspecified as this method raises NotImplementedError and should be overridden by concrete implementations.

## Raises:
    NotImplementedError: Always raised by this base implementation, indicating that subclasses must provide their own rendering logic.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - This method should only be called on concrete subclasses that have implemented the render method
    - The Root instance must be properly initialized with valid content including body, footer, and style components
    
    Postconditions:
    - The method will always raise NotImplementedError unless overridden by a subclass

## Side Effects:
    None: This method does not perform any I/O operations or external service calls.

### `src.ydata_profiling.report.presentation.core.root.Root.convert_to_class` · *method*

## Summary:
Converts a Renderable object to a different class type while processing its body and footer content.

## Description:
This classmethod converts a Renderable object to a specified class type, enabling dynamic polymorphism in the report presentation system. It modifies the object's class directly using `obj.__class__ = cls` and applies a transformation function to the object's body and footer content when present. This functionality is primarily used during report generation to adapt renderable components to specific presentation requirements while preserving their structural content.

The method is particularly useful in the report rendering pipeline where objects need to be dynamically converted to different types while maintaining their content structure for further processing.

## Args:
    cls: type - The target class to convert the object to
    obj: Renderable - The renderable object to be converted
    flv: Callable - Function applied to body and footer content when present

## Returns:
    None - This function modifies the object in-place and does not return a value

## Raises:
    None explicitly raised - However, exceptions from the flv function may propagate

## State Changes:
    Attributes READ: obj.content
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions:
    - obj must be an instance of Renderable or its subclasses
    - obj.content must be a dictionary-like object
    - cls must be a valid class type
    - flv must be callable

    Postconditions:
    - obj.__class__ will be set to cls
    - If body exists in obj.content, flv will be called with obj.content["body"]
    - If footer exists in obj.content, flv will be called with obj.content["footer"]

## Side Effects:
    None - This function only modifies the object's class and calls the provided function

