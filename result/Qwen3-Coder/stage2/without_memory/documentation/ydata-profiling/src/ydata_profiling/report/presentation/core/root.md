# `root.py`

## `src.ydata_profiling.report.presentation.core.root.Root` · *class*

## Summary:
Root represents the top-level container for report presentations, serving as the main entry point for rendering complete reports with body content, footer, and styling configuration.

## Description:
The Root class acts as the primary container for report presentations in the ydata-profiling library. It should be instantiated when constructing a complete report structure that includes body content, footer elements, and styling configuration. This class serves as the root node in the presentation hierarchy, aggregating all report components under a single logical unit.

The motivation for this distinct abstraction is to provide a standardized container for complete report structures while maintaining the flexibility to compose various renderable components (body, footer) with consistent styling. It enforces the responsibility boundary of managing the complete report presentation lifecycle.

## State:
- item_type: str, set to "report" by constructor, invariant that identifies this as a report container
- content: dict, contains keys "body" (Renderable), "footer" (Renderable), and "style" (Style), invariant that maintains all report components
- name: str, optional parameter passed through to parent class, defaults to None
- anchor_id: str, optional parameter passed through to parent class, defaults to None  
- classes: str, optional parameter passed through to parent class, defaults to None

The class invariants ensure that the content dictionary always contains the required "body", "footer", and "style" keys, and that the item_type remains consistently set to "report".

## Lifecycle:
Creation: Instantiate with required parameters name, body (Renderable), footer (Renderable), and style (Style). Optional parameters anchor_id and classes can be provided for additional metadata.

Usage: Typically, the render() method would be called to generate the final presentation output, though this method raises NotImplementedError in the current implementation. The convert_to_class() classmethod allows dynamic conversion of existing Renderable objects to Root instances.

Destruction: No explicit cleanup is required as this is a data container. The class implements standard Python object lifecycle management through inheritance from Renderable and ItemRenderer.

## Method Map:
```mermaid
graph TD
    A[Root.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Root.render]
    D --> E[NotImplementedError]
    F[Root.convert_to_class] --> G[obj.__class__ = Root]
    G --> H[flv(obj.content["body"])]
    H --> I[flv(obj.content["footer"])]
```

## Raises:
- TypeError: May be raised by parent classes during initialization if parameters don't match expected types
- NotImplementedError: Raised by render() method when invoked (intentional limitation)

## Example:
```python
# Create a Root instance for a complete report
root = Root(
    name="my_report",
    body=body_component,  # Renderable instance
    footer=footer_component,  # Renderable instance  
    style=Style()  # Style configuration
)

# Convert an existing renderable to Root type
Root.convert_to_class(existing_renderable, lambda x: x)  # Apply transformation function
```

### `src.ydata_profiling.report.presentation.core.root.Root.__init__` · *method*

## Summary:
Initializes a Root renderable object that represents the main report structure with body content, footer, and styling configuration.

## Description:
Creates a Root instance that serves as the top-level container for report presentations. This method initializes the object with a "report" type identifier and sets up the internal content structure containing body, footer, and style components. The Root class acts as the main entry point for report rendering in the presentation layer, inheriting from ItemRenderer which in turn inherits from Renderable.

## Args:
    name (str): Unique identifier for the report
    body (Renderable): Main content body of the report
    footer (Renderable): Footer content of the report
    style (Style): Styling configuration for the report
    **kwargs: Additional keyword arguments passed to parent constructors

## Returns:
    None: This is an initializer method that sets up object state

## Raises:
    None explicitly raised: The method delegates to parent constructors which may raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.content dictionary with keys: "body", "footer", "style"
    - self.item_type set to "report"

## Constraints:
    Preconditions: 
    - body must be a Renderable instance
    - footer must be a Renderable instance  
    - style must be a Style instance
    - name must be a string

    Postconditions:
    - self.content contains keys: "body", "footer", "style"
    - self.item_type is set to "report"
    - The object is properly initialized as an ItemRenderer with report type

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.root.Root.__repr__` · *method*

## Summary:
Returns a string representation of the Root object, identifying it as a Root instance.

## Description:
This method provides a human-readable string representation of the Root object. It is part of the standard Python object protocol and is called by built-in functions like `repr()` and when the object is displayed in interactive environments. The method is implemented to consistently return "Root" regardless of the object's internal state.

## Args:
    None

## Returns:
    str: Always returns the literal string "Root"

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.root.Root.render` · *method*

## Summary:
Raises NotImplementedError to indicate that this method must be implemented by subclasses for rendering report content.

## Description:
This method serves as an abstract interface for rendering report components. It is defined in the Root class as part of the presentation layer architecture, but raises NotImplementedError to enforce that concrete implementations must override this method. The Root class is designed to be subclassed, with its render method being the primary entry point for generating rendered report output.

## Args:
    **kwargs: Arbitrary keyword arguments that may be used by concrete implementations for rendering configuration or context.

## Returns:
    Any: The return type varies by concrete implementation, but typically returns rendered HTML, JSON, or other formatted output representing the report.

## Raises:
    NotImplementedError: Always raised by this base implementation, indicating that subclasses must provide their own implementation.

## State Changes:
    Attributes READ: None - this method does not read any instance attributes directly
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: None - the method is abstract and doesn't validate preconditions
    Postconditions: None - the method never completes execution due to NotImplementedError

## Side Effects:
    None - this method does not perform any I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.root.Root.convert_to_class` · *method*

## Summary:
Changes the class of a Renderable object and processes its body and footer content sections.

## Description:
This utility function transforms a Renderable object into a different class while ensuring that any body and footer content within the object's content dictionary are processed by the provided flattening/visiting function. This is commonly used during report generation to dynamically change the type of rendered elements while maintaining their content structure.

## Args:
    cls: The target class to convert the object to
    obj: A Renderable object whose class will be changed
    flv: A callable function that processes content sections

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: obj.content
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions:
        - obj must be an instance of Renderable class
        - obj.content must be a dictionary-like object
        - flv must be callable
    Postconditions:
        - obj.__class__ will be set to cls
        - Body and footer content sections will be processed by flv if they exist

## Side Effects:
    Mutates the class of the input object
    Calls the provided flv function on body and footer content if present

