# `renderable.py`

## `src.ydata_profiling.report.presentation.core.renderable.Renderable` · *class*

## Summary:
Abstract base class for renderable objects that encapsulates content and metadata.

## Description:
The Renderable class is an abstract base class designed to represent objects that can be rendered in a reporting or presentation context. It provides a simple container for content and associated metadata (name, anchor_id, classes) through a dictionary-based storage system. Subclasses must implement the render() method to define their specific rendering behavior.

This class serves as a foundation for creating renderable components in a reporting system, offering a consistent interface for storing and accessing content and metadata while requiring concrete implementations for rendering.

## State:
- content: Dict[str, Any] - Dictionary containing the core content and metadata for the renderable object. This is the primary storage mechanism.
- name: str (property) - Returns the name identifier stored in content["name"]. Raises KeyError if the key is not present.
- anchor_id: str (property) - Returns the anchor identifier associated with this renderable component. Raises KeyError if the key is not present.
- classes: str (property) - Returns the CSS classes associated with this renderable component. Raises KeyError if the key is not present.

__init__ parameters:
- content: Dict[str, Any] - Required dictionary containing the core content for the renderable object. Must not be None.
- name: Optional[str] = None - Optional name identifier that gets stored in content["name"] if provided.
- anchor_id: Optional[str] = None - Optional anchor identifier that gets stored in content["anchor_id"] if provided.
- classes: Optional[str] = None - Optional CSS classes that get stored in content["classes"] if provided.

Class invariants:
- The content dictionary must always be initialized and contain the required keys accessed by the property getters
- All property getters (name, anchor_id, classes) assume that their respective keys exist in the content dictionary

## Lifecycle:
Creation: Instantiate with content dictionary and optional metadata parameters. The content dictionary is required and must contain the basic structure for the renderable object.

Usage: Typically, subclasses implement the render() method to produce the actual rendered output. The content dictionary is used as the primary data source for rendering operations.

Destruction: No explicit cleanup required. The class implements __str__() for string representation but doesn't manage resources that require cleanup.

## Method Map:
```mermaid
graph TD
    A[Renderable.__init__] --> B[content dict setup]
    B --> C[name/anchor_id/classes setup]
    C --> D[Renderable.render()]:::abstract
    D --> E[Subclass.render()]
    
    classDef abstract fill:#ffcccc,stroke:#333;
```

## Raises:
- KeyError: Raised by property getters (name, anchor_id, classes) when the corresponding key is not present in the content dictionary.
- TypeError: Raised if render() is called directly on the abstract base class instance.

## Example:
```python
# Creating a renderable object
content = {"title": "Sample Chart", "data": [1, 2, 3]}
renderable_obj = Renderable(content, name="chart1", anchor_id="chart-anchor")

# Accessing properties
print(renderable_obj.name)  # Output: chart1
print(renderable_obj.anchor_id)  # Output: chart-anchor

# Note: Actual rendering would be implemented by subclasses
# renderable_obj.render()  # Would raise TypeError if called directly
```

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__init__` · *method*

## Summary:
Initializes a Renderable object with content and optional metadata fields.

## Description:
Sets up the Renderable instance with the provided content dictionary and optionally adds metadata fields (name, anchor_id, classes) to the content. This method serves as the constructor for Renderable objects, preparing them for presentation rendering.

## Args:
    content (Dict[str, Any]): The main content dictionary for this renderable element.
    name (Optional[str]): Optional name identifier for the renderable element. Defaults to None.
    anchor_id (Optional[str]): Optional HTML anchor ID for linking. Defaults to None.
    classes (Optional[str]): Optional CSS classes to apply. Defaults to None.

## Returns:
    None: This is an initializer method that sets up object state.

## Raises:
    No explicit exceptions are raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.content: Set to the provided content parameter
    - self.content["name"]: Conditionally set if name parameter is provided
    - self.content["anchor_id"]: Conditionally set if anchor_id parameter is provided  
    - self.content["classes"]: Conditionally set if classes parameter is provided

## Constraints:
    Preconditions:
    - content must be a dictionary
    - name, anchor_id, and classes must be strings or None
    Postconditions:
    - self.content will contain the provided content dictionary
    - If provided, name, anchor_id, and classes will be added as keys to self.content

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.name` · *method*

## Summary:
Returns the name identifier stored in the renderable object's content dictionary.

## Description:
Provides access to the name field of a renderable object by retrieving it from the internal content dictionary. This property serves as a convenient accessor for the name metadata associated with renderable presentation elements.

## Args:
    None

## Returns:
    str: The name identifier stored in the content dictionary under the "name" key.

## Raises:
    KeyError: When the "name" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The content dictionary must contain a "name" key.
    Postconditions: Returns the string value associated with the "name" key in content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.anchor_id` · *method*

## Summary:
Returns the anchor identifier associated with this renderable component.

## Description:
Provides access to the anchor ID stored in the component's content dictionary. This property enables retrieving the unique identifier used for HTML anchors or navigation targets within the rendered output.

## Args:
    None

## Returns:
    str: The anchor identifier string stored in the component's content dictionary under the "anchor_id" key.

## Raises:
    KeyError: If the "anchor_id" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.content dictionary must contain the "anchor_id" key.
    Postconditions: The returned value is the exact string stored in self.content["anchor_id"].

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.classes` · *method*

## Summary:
Returns the CSS classes associated with this renderable component.

## Description:
Provides access to the CSS classes stored in the component's content dictionary. This property is part of the Renderable abstract base class and allows access to styling information for presentation components.

## Args:
    None

## Returns:
    str: The CSS classes associated with this renderable component.

## Raises:
    KeyError: If the "classes" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The content dictionary must contain a "classes" key.
    Postconditions: Returns the string value associated with the "classes" key in content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.render` · *method*

## Summary:
Abstract interface method for transforming internal content into a presentation-ready format.

## Description:
This abstract method establishes the rendering contract for all Renderable objects. It must be implemented by concrete subclasses to produce a formatted representation of the internal content suitable for presentation in various output formats (HTML, JSON, etc.). The method enables polymorphic rendering behavior across different presentation components while maintaining a consistent interface.

## Args:
    None

## Returns:
    Any: The rendered representation of the internal content. Return type varies by implementation but typically includes HTML strings, serialized data structures, or presentation-ready objects.

## Raises:
    NotImplementedError: Raised when this abstract method is called directly on a Renderable instance or when a subclass has not implemented this method.

## State Changes:
    Attributes READ: 
    - self.content: The internal content dictionary containing the data to be rendered
    - self.name: Property accessing the name field from content (via self.content["name"])
    - self.anchor_id: Property accessing the anchor_id field from content (via self.content["anchor_id"])  
    - self.classes: Property accessing the classes field from content (via self.content["classes"])
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Renderable object must be properly initialized with content
    - Subclasses must override this method with concrete implementation
    - The internal content dictionary should be accessible and properly structured
    
    Postconditions:
    - The method returns a valid presentation representation of the content
    - The internal state of the object remains unmodified
    - The returned value should be compatible with the target presentation system

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__str__` · *method*

## Summary:
Returns the class name of the renderable object as its string representation.

## Description:
This method provides a string representation of the renderable object by returning its class name. It's implemented as a standard `__str__` magic method to enable easy identification of renderable objects during debugging or logging operations. This method is particularly useful in the ydata-profiling report generation pipeline where various renderable components need to be identified by their type.

## Args:
    None

## Returns:
    str: The name of the class that this renderable object belongs to.

## Raises:
    None

## State Changes:
    Attributes READ: self.__class__
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be an instance of Renderable or its subclasses.
    Postconditions: The returned string is always the exact class name of the object.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.convert_to_class` · *method*

## Summary:
Dynamically changes the class of a Renderable object to a specified class type.

## Description:
This utility function performs a runtime class conversion of a Renderable object by directly replacing its class with a new class. It's typically used in presentation layer systems to adapt renderable objects to different specialized implementations based on context or configuration requirements. The function modifies the object's type in-place without creating a new instance.

## Args:
    cls: The target class to convert the object to
    obj: A Renderable instance whose class will be changed
    flv: A callable parameter (likely intended for future use or transformation callbacks, currently unused)

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: obj.__class__ (directly modified)

## Constraints:
    Preconditions: 
    - obj must be an instance of Renderable or a subclass
    - cls must be a valid class type
    - The target class cls should be compatible with the existing object's interface to avoid runtime errors
    
    Postconditions:
    - The obj's type will be changed to cls
    - All existing attributes and methods of obj will be preserved
    - The object maintains its identity (same memory reference)

## Side Effects:
    None

