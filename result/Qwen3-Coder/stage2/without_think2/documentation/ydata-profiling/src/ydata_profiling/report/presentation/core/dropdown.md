# `dropdown.py`

## `src.ydata_profiling.report.presentation.core.dropdown.Dropdown` · *class*

## Summary:
Dropdown is a presentation component that renders interactive dropdown menus in profiling reports, inheriting from ItemRenderer to provide structured content organization.

## Description:
The Dropdown class represents an interactive dropdown menu element in the ydata-profiling report presentation layer. It extends ItemRenderer to provide a specialized container for dropdown functionality, allowing users to toggle visibility of nested content sections. This component is typically used in reports to organize related information under collapsible sections, improving readability and navigation.

The class is designed to work within a hierarchical presentation structure where dropdowns can contain other renderable components such as containers or individual items. It provides a standardized interface for dropdown rendering while delegating the actual visual implementation to subclasses that implement the abstract render() method.

Known callers include the presentation rendering engine and various report generation pipelines that construct dropdown-based UI components. The class is particularly useful for creating expandable sections in profiling reports where detailed information can be hidden by default to reduce visual clutter.

## State:
- name: str - Human-readable identifier for the dropdown, stored in content dictionary under "name" key
- id: str - Unique identifier for the dropdown element, stored in content dictionary under "id" key  
- items: list - Collection of items to display in the dropdown menu, stored in content dictionary under "items" key
- item: Container - Single container item that represents the dropdown's content, stored in content dictionary under "item" key
- anchor_id: str - Unique identifier for HTML anchors, stored in content dictionary under "anchor_id" key
- classes: list - CSS classes for styling the dropdown element, joined into a space-separated string and stored in content dictionary under "classes" key
- is_row: bool - Boolean flag indicating whether the dropdown should be rendered as a row layout, stored in content dictionary under "is_row" key
- content: dict - Dictionary containing all configuration parameters and metadata, inherited from Renderable parent class
- item_type: str - String identifier "dropdown" that specifies the component type, set during initialization via ItemRenderer.__init__

## Lifecycle:
- Creation: Instantiate with required parameters including name, id, items, item (Container), anchor_id, classes (list), and is_row boolean flag. Additional kwargs are passed to parent constructor.
- Usage: Typically used as part of a presentation hierarchy where dropdowns group related renderable elements. The render() method must be implemented by subclasses to define presentation-specific output formats.
- Destruction: No explicit cleanup required; relies on Python's garbage collection for resource management.

## Method Map:
```mermaid
graph TD
    A[Dropdown.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set content dictionary]
    D --> E[Store name/id/items/item/anchor_id/classes/is_row]
    F[Dropdown.render] --> G[Abstract method - NotImplementedError]
    H[Dropdown.convert_to_class] --> I[Class method - Change obj class to cls]
    I --> J[Apply flv to obj.content["item"] if present]
```

## Raises:
- NotImplementedError: Raised by render() method when called directly on the base Dropdown class, requiring subclasses to implement concrete rendering logic
- TypeError: May be raised during initialization if incompatible types are passed for parameters (though not explicitly validated in current implementation)
- AttributeError: May occur if content dictionary operations fail due to invalid state

## Example:
```python
# Create a dropdown with container content
dropdown_item = Container([Text("Details")], sequence_type="list")
dropdown = Dropdown(
    name="Advanced Options",
    id="advanced_dropdown",
    items=["option1", "option2"],
    item=dropdown_item,
    anchor_id="advanced_anchor",
    classes=["dropdown-class"],
    is_row=False
)

# Convert a renderable object to dropdown type
some_renderable = SomeRenderable(...)
Dropdown.convert_to_class(some_renderable, lambda x: x)  # Transform to dropdown
```

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.__init__` · *method*

## Summary:
Initializes a Dropdown component by configuring its content dictionary with rendering parameters and establishing its type as a dropdown element.

## Description:
Sets up a Dropdown instance with all necessary configuration parameters for rendering interactive dropdown menus in profiling reports. This method configures the component's content dictionary with essential properties including name, ID, items, associated container item, anchor ID, CSS classes (joined into a space-separated string), and layout preference. The method ensures proper inheritance from ItemRenderer and Renderable base classes while establishing the dropdown's identity through the item_type attribute.

This initialization method is part of the presentation layer in ydata-profiling, specifically designed to create dropdown UI components that can be rendered in various output formats. The method delegates to parent constructors to handle content dictionary setup and type registration.

## Args:
- name (str): Human-readable identifier for the dropdown element
- id (str): Unique identifier for the dropdown HTML element
- items (list): Collection of items to display in the dropdown menu
- item (Container): Single container representing the dropdown's content area
- anchor_id (str): Unique identifier for HTML anchor references
- classes (list): List of CSS class names for styling the dropdown element (will be joined with spaces)
- is_row (bool): Boolean flag indicating row-based layout rendering
- **kwargs: Additional keyword arguments passed to parent constructors

## Returns:
None

## Raises:
- TypeError: If incompatible types are passed for parameters (inherited from parent constructors)
- AttributeError: If content dictionary operations fail during initialization

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - Sets up self.content dictionary with keys: "name", "id", "items", "item", "anchor_id", "classes", "is_row"
  - Sets self.item_type to "dropdown" (inherited from ItemRenderer)

## Constraints:
- Preconditions: All required parameters must be provided with appropriate types
- Postconditions: The Dropdown instance is properly initialized with content dictionary containing all specified parameters, and item_type is set to "dropdown"

## Side Effects:
None

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.__repr__` · *method*

## Summary:
Returns a string representation of the Dropdown instance, identifying it as a Dropdown object.

## Description:
The `__repr__` method provides a standardized string representation for Dropdown instances, returning the literal string "Dropdown". This method is part of the standard Python object protocol and is used primarily for debugging and development purposes to quickly identify objects in console output or logs.

This logic is implemented as its own method rather than being inlined because:
1. It follows Python conventions for implementing `__repr__` methods
2. It provides a consistent interface for object identification
3. It allows for future extension without modifying the class's core functionality
4. It enables proper debugging and logging behavior

## Returns:
    str: The string "Dropdown" that identifies this object type.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Dropdown"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.render` · *method*

## Summary:
Abstract method that must be implemented by subclasses to render dropdown components in the presentation layer.

## Description:
This method defines the rendering contract for dropdown components within the ydata-profiling report presentation framework. As an abstract method inherited from the Renderable base class, it establishes a standardized interface that all dropdown implementations must satisfy. The method is intentionally left unimplemented in the base Dropdown class to enforce proper inheritance and polymorphism within the presentation layer architecture.

Known callers include the presentation layer's rendering engine which invokes this method during report generation when processing dropdown components. This method is part of the standard rendering pipeline that converts renderable components into their final presentation format. The Dropdown class is designed to work with Container components and other renderable items to create structured presentation hierarchies.

## Args:
    self: The instance of the Dropdown class or its subclass that requires rendering.

## Returns:
    Any: This method raises NotImplementedError and thus never actually returns a value.

## Raises:
    NotImplementedError: Always raised when this method is called directly on the base Dropdown class, requiring subclasses to implement their own rendering logic.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method is designed to be overridden by subclasses to provide concrete rendering behavior.
    Postconditions: None, as the method always raises an exception when called on the base class.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.dropdown.Dropdown.convert_to_class` · *method*

## Summary:
Converts a Renderable object to a specified class type and processes its item content if present.

## Description:
This class method changes the class type of a Renderable object to the specified class and optionally applies a transformation function to the object's item content. It is used during presentation hierarchy construction to dynamically convert objects between different renderable types while preserving their content structure. The method enables flexible presentation formatting by allowing runtime type switching of renderable components.

This method is called during the presentation rendering pipeline when objects need to be transformed from one type to another based on context or requirements. It specifically handles the case where an object contains an "item" key in its content dictionary by applying the provided transformation function to that item.

## Args:
    cls: Type[Renderable] - The target class to convert the object to. Must be a subclass of Renderable.
    obj: Renderable - The renderable object to convert. Must have a content dictionary attribute.
    flv: Callable - A function to apply to the object's item content if it exists. Should accept a single argument.

## Returns:
    None - This method modifies the object in-place and does not return a value.

## Raises:
    AttributeError: If obj does not have a __class__ attribute or content dictionary
    KeyError: If "item" key access fails in obj.content dictionary
    TypeError: If flv is not callable or cannot be applied to obj.content["item"]

## State Changes:
    Attributes READ:
    - obj.content: Accesses the content dictionary to check for "item" key
    Attributes WRITTEN:
    - obj.__class__: Modifies the object's class type to cls

## Constraints:
    Preconditions:
    - obj must be an instance of Renderable or subclass
    - obj.content must be a dictionary-like object
    - cls must be a valid class that inherits from Renderable
    - flv must be callable or None
    Postconditions:
    - obj.__class__ will be set to cls
    - If "item" exists in obj.content, flv will be called with obj.content["item"] as argument

## Side Effects:
    None - This method only modifies the object's class type and applies a function to content. No external I/O or service calls occur.

