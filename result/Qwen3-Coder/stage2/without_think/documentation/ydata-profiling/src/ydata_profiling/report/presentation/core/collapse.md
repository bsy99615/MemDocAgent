# `collapse.py`

## `src.ydata_profiling.report.presentation.core.collapse.Collapse` · *class*

## Summary:
Represents a collapsible UI component that contains a toggle button and a collapsible item.

## Description:
The Collapse class implements a collapsible interface element that consists of a toggle button and a content item that can be shown or hidden. It serves as a container for UI elements that can be toggled between expanded and collapsed states. This class is typically instantiated by the presentation layer when creating interactive report components that need collapsible sections.

The class is designed to work with the rendering pipeline where it can be converted from other Renderable objects using the static convert_to_class method.

## State:
- button: ToggleButton instance that controls the collapse state
- item: Renderable instance that gets shown/hidden when the collapse is toggled
- content: Dictionary containing the button and item components
- item_type: String identifier set to "collapse" indicating this is a collapse component

## Lifecycle:
- Creation: Instantiate with a ToggleButton and a Renderable item
- Usage: Call render() method to generate the UI representation (currently raises NotImplementedError)
- Conversion: Use convert_to_class() class method to transform existing Renderable objects into Collapse instances
- Destruction: No explicit cleanup required as it inherits from Renderable

## Method Map:
```mermaid
graph TD
    A[Collapse Constructor] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    D[convert_to_class] --> E[obj.__class__ = cls]
    E --> F[flv(button)]
    E --> G[flv(item)]
    H[Collapse.render] --> I[NotImplementedError]
```

## Raises:
- NotImplementedError: When render() method is called (as it's abstract in parent class)

## Example:
```python
# Create a toggle button
toggle = ToggleButton("Show Details")

# Create a content item
content = Text("This is collapsible content")

# Create a collapse component
collapse = Collapse(toggle, content)

# Convert existing renderable to collapse
existing_renderable = SomeRenderable()
Collapse.convert_to_class(existing_renderable, lambda x: x)
```

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__init__` · *method*

## Summary:
Initializes a collapsible component with a toggle button and associated content item.

## Description:
Creates a collapsible UI component that contains a toggle button and a renderable item. This component allows users to expand or collapse the content area by clicking the associated button. The initialization sets up the internal structure with the provided button and item, along with any additional configuration options.

## Args:
    button (ToggleButton): The toggle button used to control the collapse state
    item (Renderable): The renderable content that will be shown/hidden when collapsed/expanded
    **kwargs: Additional configuration options passed to the parent ItemRenderer constructor including:
        - name (Optional[str]): Optional name identifier for the component
        - anchor_id (Optional[str]): Optional anchor ID for HTML linking
        - classes (Optional[str]): Optional CSS classes to apply to the component

## Returns:
    None: This method initializes the object state and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.item_type: Set to "collapse"
        - self.content: Dictionary containing "button" and "item" keys with their respective values

## Constraints:
    Preconditions:
        - button must be a valid ToggleButton instance
        - item must be a valid Renderable instance
        - All kwargs must be valid parameters for the parent ItemRenderer constructor
    
    Postconditions:
        - The object is initialized as a collapsible component
        - The internal content dictionary contains the provided button and item
        - The item_type is set to "collapse"

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__repr__` · *method*

## Summary:
Returns a string representation of the Collapse object for debugging and logging purposes.

## Description:
This method provides a concise string identifier for Collapse instances, primarily intended for debugging and development purposes. The method is part of the standard Python object representation protocol and is automatically called by Python's repr() function or when objects are displayed in interactive environments.

## Args:
    None

## Returns:
    str: Always returns the literal string "Collapse"

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

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.render` · *method*

## Summary:
Abstract render method that must be implemented by subclasses to generate collapsible UI component representation.

## Description:
This abstract method serves as the interface for rendering a collapsible UI component containing a toggle button and associated content. It is inherited from the base Renderable class and must be implemented by subclasses to provide the actual rendering logic. When called, it raises NotImplementedError to indicate that the implementation is deferred to subclasses. This method is typically invoked during the presentation rendering phase when constructing the report interface.

## Args:
    None

## Returns:
    Any: The rendered representation of the collapsible component, typically HTML or similar markup structure.

## Raises:
    NotImplementedError: Raised when the method is called without being overridden by a subclass implementation.

## State Changes:
    Attributes READ: self.content (accesses "button" and "item" keys from the content dictionary)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Collapse instance must be properly initialized with a ToggleButton and Renderable item
    - The content dictionary must contain "button" and "item" keys
    - This method should only be called on properly initialized Collapse instances
    
    Postconditions:
    - The method must return a valid rendered representation of the collapsible component
    - The method should not modify the state of the Collapse instance

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.convert_to_class` · *method*

## Summary:
Changes the class of a Renderable object to the specified class while processing its button and item content through a provided function.

## Description:
This utility function transforms a Renderable object by changing its class to the specified target class. It also processes any "button" and "item" content elements contained within the object's content dictionary by applying the provided function to them. This function is typically used during presentation rendering to dynamically change object types while preserving and processing their content structure.

## Args:
    cls: The target class to convert the object to
    obj: A Renderable object whose class will be changed
    flv: A callable function that processes content elements

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: obj.content
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions: 
    - obj must be a Renderable instance
    - flv must be callable
    - cls must be a valid class type
    
    Postconditions:
    - obj's class is changed to cls
    - Content elements "button" and "item" (if present) are processed by flv

## Side Effects:
    Mutates the class of the input object
    Calls the provided flv function with content elements

