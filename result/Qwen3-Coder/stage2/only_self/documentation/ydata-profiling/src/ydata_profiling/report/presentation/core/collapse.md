# `collapse.py`

## `src.ydata_profiling.report.presentation.core.collapse.Collapse` · *class*

## Summary:
Represents a collapsible UI component that contains a toggle button and a collapsible item.

## Description:
The Collapse class implements a collapsible interface element that consists of a toggle button and a content item that can be shown or hidden. It serves as a presentation layer component for creating interactive collapsible sections in reports. This class is typically created by converting existing Renderable objects using the convert_to_class method.

## State:
- button: ToggleButton instance that controls the collapse state
- item: Renderable instance containing the content that gets collapsed/expanded
- content: Dictionary containing the button and item components
- item_type: String identifier set to "collapse" that defines this component type
- name: Optional string identifier for the component (inherited from Renderable)
- anchor_id: Optional string for HTML anchor identification (inherited from Renderable)
- classes: Optional CSS classes for styling (inherited from Renderable)

The __init__ method requires a ToggleButton instance and a Renderable instance as positional arguments. The item_type is fixed to "collapse".

## Lifecycle:
Creation: Instantiate with a ToggleButton and Renderable object, optionally providing additional keyword arguments for name, anchor_id, and classes.
Usage: Typically used in report generation where the convert_to_class method transforms existing Renderable objects into Collapse instances. The render() method would be called during presentation rendering.
Destruction: No explicit cleanup required; inherits standard object destruction behavior.

## Method Map:
```mermaid
graph TD
    A[Collapse Constructor] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Sets item_type="collapse"]
    D --> E[Stores button and item in content]
    
    F[convert_to_class] --> G[Changes obj.__class__ to Collapse]
    G --> H[Processes button if present]
    H --> I[Processes item if present]
    
    J[render] --> K[NotImplementedError raised]
```

## Raises:
- NotImplementedError: Raised by the render() method, indicating that rendering logic must be implemented by subclasses or in the presentation layer.

## Example:
```python
# Create a toggle button
toggle_btn = ToggleButton("Show Details")

# Create a content item
content_item = Text("This is collapsible content")

# Create a collapse component
collapse = Collapse(toggle_btn, content_item)

# Convert an existing renderable to collapse type
existing_renderable = SomeRenderable()
Collapse.convert_to_class(existing_renderable, lambda x: x)  # Apply transformation function
```

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__init__` · *method*

## Summary:
Initializes a collapsible UI component with a toggle button and content item.

## Description:
Configures a Collapse instance by setting up its internal structure with a toggle button and collapsible content item. This method establishes the component's identity as a "collapse" type and stores the required UI elements in the content dictionary.

## Args:
    button (ToggleButton): The toggle button that controls the collapse state
    item (Renderable): The content item that will be shown or hidden when toggled
    **kwargs: Additional optional parameters for name, anchor_id, and classes

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "collapse"
    - self.content: Populated with button and item components

## Constraints:
    Preconditions:
    - button must be a valid ToggleButton instance
    - item must be a valid Renderable instance
    - All kwargs must be valid parameters for the parent Renderable.__init__ method
    
    Postconditions:
    - The object is initialized as a "collapse" type component
    - Both button and item are stored in the content dictionary under keys "button" and "item" respectively

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__repr__` · *method*

## Summary:
Returns a string representation of the Collapse object indicating its type.

## Description:
This method provides a human-readable string representation for Collapse instances, returning the literal string "Collapse". It overrides the default object representation to give a clear indication of the object's type when printed or converted to string.

## Args:
    None

## Returns:
    str: The string "Collapse" indicating the object type.

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
Renders a collapsible UI component containing a toggle button and a collapsible item.

## Description:
This method is responsible for rendering the visual representation of a collapsible component. It combines a toggle button with a collapsible item to create a UI element that can be expanded or collapsed. The method is abstract and must be implemented by subclasses to provide the actual rendering logic for the specific presentation layer (HTML, JSON, etc.).

## Args:
    None: This method does not accept any arguments beyond the implicit `self`.

## Returns:
    Any: The rendered representation of the collapsible component, typically in the format appropriate for the target presentation layer (HTML string, JSON structure, etc.).

## Raises:
    NotImplementedError: This method raises NotImplementedError as it is intended to be overridden by concrete implementations in subclasses.

## State Changes:
    Attributes READ: 
        - self.content (accessed via parent classes)
        - self.content["button"] (the toggle button component)
        - self.content["item"] (the collapsible content item)
    Attributes WRITTEN: None (this method is abstract and doesn't modify state directly)

## Constraints:
    Preconditions:
        - The Collapse instance must have been properly initialized with a button and item
        - The button must be a ToggleButton instance
        - The item must be a Renderable instance
    Postconditions:
        - The method must return a valid representation of the collapsible component
        - The returned value should be compatible with the target presentation layer

## Side Effects:
    None: This method does not have side effects beyond returning the rendered representation.

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.convert_to_class` · *method*

## Summary:
Converts a Renderable object to a Collapse instance and processes its button and item content elements.

## Description:
This class method transforms a Renderable object into a Collapse instance by changing its class type and recursively applying a transformation function to its button and item content elements. It's primarily used during presentation layer rendering to dynamically change object types while maintaining content structure.

## Args:
    cls: The target class to convert the object to (expected to be Collapse)
    obj (Renderable): The Renderable object to convert
    flv (Callable): Function to apply to button and item content elements

## Returns:
    None: This method modifies the object in-place and doesn't return anything

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: obj.content
    Attributes WRITTEN: obj.__class__ (modified in-place)

## Constraints:
    Preconditions:
        - obj must be an instance of Renderable or subclass
        - flv must be callable
        - obj.content must be a dictionary-like object
    Postconditions:
        - obj.__class__ will be set to cls
        - If "button" key exists in obj.content, flv will be called on obj.content["button"]
        - If "item" key exists in obj.content, flv will be called on obj.content["item"]

## Side Effects:
    - Modifies the class type of the input object in-place
    - Calls the provided function flv on button and item content elements

