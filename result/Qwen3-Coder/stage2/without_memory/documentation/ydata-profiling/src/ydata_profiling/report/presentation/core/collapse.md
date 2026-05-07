# `collapse.py`

## `src.ydata_profiling.report.presentation.core.collapse.Collapse` · *class*

## Summary:
A collapsible UI component that contains a toggle button and a renderable item, used to create interactive expandable sections in report presentations.

## Description:
The Collapse class represents a collapsible UI element that combines a ToggleButton with another Renderable item. It serves as a container for creating interactive expandable/collapsible sections in report presentations. This class is part of the presentation layer of the ydata-profiling library, designed to generate HTML reports with interactive elements.

The class is typically instantiated by the report generation system when creating collapsible sections in the final report output. It provides a mechanism to group related content under a toggleable header.

## State:
- item_type: str, set to "collapse" by constructor, identifies this component type
- content: dict containing two keys:
  - "button": ToggleButton instance that controls the collapse/expand state
  - "item": Renderable instance that gets shown/hidden when toggled
- name: Optional[str], inherited from Renderable, provides a name identifier
- anchor_id: Optional[str], inherited from Renderable, provides an HTML anchor ID
- classes: Optional[str], inherited from Renderable, provides CSS classes

The constructor requires a ToggleButton and a Renderable instance, with optional additional keyword arguments for naming, anchoring, and styling.

## Lifecycle:
Creation: Instantiate with a ToggleButton and Renderable object, optionally providing name, anchor_id, and classes parameters.
Usage: Typically rendered by the presentation layer system, which calls the render() method. The convert_to_class() classmethod is used internally to transform existing Renderable objects into Collapse instances.
Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[Collapse Constructor] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Sets item_type="collapse"]
    D --> E[Stores button and item in content dict]
    
    F[convert_to_class classmethod] --> G[Changes obj.__class__ to Collapse]
    G --> H[Processes button if present]
    H --> I[Processes item if present]
    
    J[render method] --> K[NotImplementedError raised]
```

## Raises:
- NotImplementedError: Raised by the render() method, indicating that rendering logic must be implemented by subclasses or the presentation system.

## Example:
```python
# Create a toggle button
toggle = ToggleButton("Show Details")

# Create a content item (could be any Renderable)
content_item = Text("This is hidden content")

# Create a collapse component
collapse = Collapse(toggle, content_item)

# Convert an existing Renderable to Collapse type
Collapse.convert_to_class(existing_renderable, lambda x: x)
```

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__init__` · *method*

## Summary:
Initializes a collapsible component that wraps a toggle button and a renderable item.

## Description:
Constructs a Collapse object that combines a toggle button with a renderable item to create a collapsible UI element. This method sets up the internal structure for a collapsible component by storing the button and item within the content dictionary.

## Args:
    button (ToggleButton): The toggle button that controls the collapse state
    item (Renderable): The renderable content that will be collapsed/expanded
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor

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
    - Both button and item must be compatible with the rendering system
    
    Postconditions:
    - The object is initialized with item_type set to "collapse"
    - The content dictionary contains both button and item under their respective keys

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__repr__` · *method*

## Summary:
Returns a string representation of the Collapse object indicating its type.

## Description:
The `__repr__` method provides a standardized string representation for Collapse instances, returning the literal string "Collapse". This method is part of the object's representation protocol and is typically used for debugging and logging purposes.

## Args:
    None

## Returns:
    str: The string "Collapse" that identifies this object type.

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
Abstract rendering method that must be implemented by subclasses to generate the presentation representation of a collapse component.

## Description:
This abstract method defines the interface for rendering collapse components in the ydata-profiling report generation system. As part of the Renderable abstract base class hierarchy, it establishes a contract that all concrete Collapse implementations must fulfill. 

The collapse component represents an interactive UI element containing a toggle button and associated content that can be shown or hidden. This abstract method ensures that subclasses provide their own implementation for converting the collapse structure into a presentation-ready format (such as HTML, JSON, or other markup formats).

In the report generation pipeline, this method is invoked when the presentation layer processes Collapse instances to produce their final rendered output. The method is intentionally left unimplemented in the base Collapse class to enforce proper inheritance and implementation patterns.

## Args:
    None

## Returns:
    Any: This method never returns normally due to NotImplementedError being raised.

## Raises:
    NotImplementedError: Always raised to indicate that subclasses must override this method with concrete implementation.

## State Changes:
    Attributes READ: 
    - self.content (inherited from Renderable base class)
    - self.item_type (inherited from ItemRenderer base class)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - This method should only be called on properly initialized Collapse instances
    - Subclasses must implement this method with valid rendering logic
    - The Collapse instance must have valid button and item content in self.content
    
    Postconditions:
    - Method execution always terminates with NotImplementedError
    - No state changes occur in the Collapse instance

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.convert_to_class` · *method*

## Summary:
Changes the class of a renderable object and processes its button and item content elements.

## Description:
This function dynamically changes the class of a Renderable object to the specified class and applies a transformation function to any button or item content elements. It's used to convert renderable objects to different types while preserving their content structure and applying appropriate transformations to nested elements.

## Args:
    cls: The target class to convert the object to
    obj: A Renderable object whose class will be changed
    flv: A callable function that transforms content elements

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: obj.content
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions: 
    - obj must be an instance of Renderable or its subclasses
    - flv must be callable
    - obj.content must be a dictionary-like object
    
    Postconditions:
    - obj.__class__ will be set to cls
    - Content elements referenced by "button" and "item" keys will have flv applied to them

## Side Effects:
    Mutates the class of the input object obj
    Calls the flv function on content elements if they exist

