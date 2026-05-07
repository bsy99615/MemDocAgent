# `collapse.py`

## `src.ydata_profiling.report.presentation.core.collapse.Collapse` · *class*

## Summary:
A collapsible UI component that wraps a toggle button and associated content for presentation in profiling reports.

## Description:
The Collapse class represents a collapsible user interface element that combines a toggle button with associated content. It serves as a container for creating interactive report sections that can be expanded or collapsed by users. This component is part of the presentation layer responsible for generating HTML or other presentation formats for data profiling reports.

The class extends ItemRenderer, which itself inherits from Renderable, establishing it within a hierarchy of presentation components. The Collapse component is designed to work in conjunction with ToggleButton and other Renderable items to create dynamic, user-controlled report sections.

## State:
- button: ToggleButton instance that controls the collapse/expand state
- item: Renderable instance containing the content to be shown/hidden  
- item_type: String identifier set to "collapse" by constructor
- content: Dictionary containing the button and item, inherited from Renderable parent class
- name: Optional string identifier, inherited from Renderable parent class
- anchor_id: Optional string for HTML anchors, inherited from Renderable parent class
- classes: Optional CSS classes, inherited from Renderable parent class

## Lifecycle:
- Creation: Instantiate with a ToggleButton and Renderable item; optional name, anchor_id, and classes parameters
- Usage: Call render() method to generate presentation output (must be implemented by subclasses)
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[Collapse Constructor] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D{Set item_type="collapse"}
    D --> E{Store button and item in content}
    
    F[Collapse.render] --> G[NotImplementedError]
    
    H[Collapse.convert_to_class] --> I[obj.__class__ = cls]
    I --> J{Process button content}
    J --> K{Process item content}
```

## Raises:
- NotImplementedError: Raised by render() method as it is intended to be overridden by subclasses

## Example:
```python
# Create a toggle button
toggle = ToggleButton("Show Details")

# Create content to be toggled
content = Text("This is hidden content")

# Create collapse component
collapse = Collapse(toggle, content)

# The render method would be implemented by subclasses to generate output
# collapse.render()  # Would raise NotImplementedError
```

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__init__` · *method*

## Summary:
Initializes a collapsible UI component that pairs a toggle button with associated content for presentation in profiling reports.

## Description:
The `__init__` method constructs a Collapse instance by initializing its parent classes and setting up the internal structure with a toggle button and associated content. This method establishes the foundational configuration for a collapsible element that can be expanded or collapsed by users in the generated report interface.

The method delegates initialization to the parent `ItemRenderer` class, which in turn calls `Renderable.__init__`. This creates a proper inheritance chain that ensures the component integrates correctly within the presentation hierarchy. The component stores both the toggle button and content within its internal `content` dictionary, making them available for rendering operations.

## Args:
    button (ToggleButton): The toggle button instance that controls the collapse/expand state of this component
    item (Renderable): The renderable content that will be shown/hidden when the component is toggled
    **kwargs: Additional keyword arguments passed to parent constructors for name, anchor_id, and classes

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    None: This method does not explicitly raise exceptions, though parent class constructors may raise exceptions for invalid arguments

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "collapse" string identifier
    - self.content: Populated with "button" and "item" keys referencing the provided arguments

## Constraints:
    Preconditions:
    - The `button` argument must be a valid ToggleButton instance
    - The `item` argument must be a valid Renderable instance
    - All kwargs must be valid arguments for parent class constructors
    
    Postconditions:
    - The object is properly initialized with item_type set to "collapse"
    - The content dictionary contains both button and item references
    - Parent class state is properly configured

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.__repr__` · *method*

## Summary:
Returns a string representation of the Collapse component indicating its type.

## Description:
The `__repr__` method provides a standardized string representation for Collapse instances, returning the literal string "Collapse". This method is part of the standard Python object protocol and enables developers to quickly identify Collapse objects during debugging or logging.

This logic is implemented as its own method rather than being inlined because:
1. It follows Python conventions for implementing `__repr__` methods
2. It provides a consistent interface for object identification
3. It allows for future extension without modifying the class constructor or other methods

## Returns:
    str: The string "Collapse" that identifies this component type.

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
Renders a collapsible UI component that displays a toggle button and associated content.

## Description:
The render method implements the abstract rendering interface for the Collapse component, which creates a collapsible user interface element consisting of a toggle button and associated content. This component is part of the presentation layer responsible for generating HTML or other presentation formats for profiling reports. The Collapse component is designed to be used in conjunction with ToggleButton and other Renderable items to create interactive report sections that can be expanded or collapsed by users.

The render method is intentionally left unimplemented (raises NotImplementedError) to enforce that subclasses must provide specific rendering logic for different output formats (HTML, JSON, etc.). This design pattern allows for flexible rendering strategies while maintaining a consistent interface.

## Args:
    None

## Returns:
    Any: The rendered representation of the collapsible component, typically HTML content or similar presentation format

## Raises:
    NotImplementedError: This method raises NotImplementedError as it is intended to be overridden by subclasses to provide specific rendering implementations

## State Changes:
    Attributes READ: 
    - self.content (accessed via parent class Renderable)
    - self.item_type (inherited from ItemRenderer)
    - self.content['button'] (from constructor, contains ToggleButton instance)
    - self.content['item'] (from constructor, contains Renderable instance)

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Collapse class must be properly initialized with valid button and item parameters
    - The method should only be called on instances that have been properly constructed
    - Subclasses must implement this method to provide concrete rendering behavior
    
    Postconditions:
    - The method raises NotImplementedError as it is abstract
    - The component maintains its structural integrity through proper initialization

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.collapse.Collapse.convert_to_class` · *method*

## Summary:
Changes the class type of a Renderable object and processes nested button/item content through a provided function.

## Description:
This standalone function dynamically changes the class of a Renderable object to a specified class, enabling runtime polymorphism. It also recursively applies a transformation function to any button or item content contained within the object's content dictionary. This approach allows for flexible rendering behavior by enabling objects to be reclassified while preserving their structural content.

## Args:
    cls: The target class to change the object's type to
    obj: A Renderable instance whose class will be changed
    flv: A callable function that will be applied to button/item content if present

## Returns:
    None: This method modifies the object in-place and does not return a value

## Raises:
    KeyError: If 'button' or 'item' keys are present in obj.content but their corresponding values are not accessible through the flv function

## State Changes:
    Attributes READ: obj.content
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions: 
    - obj must be an instance of Renderable or its subclasses
    - cls must be a valid class that can be assigned to obj.__class__
    - flv must be callable
    Postconditions:
    - obj.__class__ will be set to cls
    - If 'button' key exists in obj.content, flv will be called with obj.content['button'] as argument
    - If 'item' key exists in obj.content, flv will be called with obj.content['item'] as argument

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects. However, the flv function may have side effects.

