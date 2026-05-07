# `renderable.py`

## `src.ydata_profiling.report.presentation.core.renderable.Renderable` · *class*

## Summary:
Abstract base class defining the interface for renderable presentation elements in the ydata-profiling report system.

## Description:
The Renderable class serves as the foundational abstraction for all presentation elements that can be rendered in a report. It provides a common structure for storing content and metadata while enforcing a contract through its abstract render method. Subclasses must implement the render method to define how they should be converted to their final presentation format (HTML, JSON, etc.).

This class enables a consistent approach to handling various report components like charts, tables, text elements, and other visualizations that need to be rendered in different formats.

## State:
- content: Dict[str, Any] - Dictionary containing the main data and metadata for the renderable element
- name: str (via property) - Optional identifier for the element, accessible through the content dictionary
- anchor_id: str (via property) - Optional anchor identifier, accessible through the content dictionary  
- classes: str (via property) - Optional CSS classes, accessible through the content dictionary

## Lifecycle:
Creation: Instantiate via subclass constructors, passing content dictionary and optional metadata parameters
Usage: Call render() method on concrete implementations to generate presentation output
Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Renderable] --> B[render()]
    A --> C[__init__]
    A --> D[name property]
    A --> E[anchor_id property]
    A --> F[classes property]
    A --> G[convert_to_class]
```

## Raises:
- None explicitly raised in __init__
- render() method raises NotImplementedError if called on the abstract base class

## Example:
```python
# Creating a renderable instance (typically done through subclasses)
content = {"title": "Sample Chart", "data": [1, 2, 3]}
renderable = MyConcreteRenderable(content, name="chart1", anchor_id="chart-anchor")

# Rendering the element
output = renderable.render()

# Accessing metadata properties
print(renderable.name)  # "chart1"
print(renderable.anchor_id)  # "chart-anchor"
```

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__init__` · *method*

## Summary:
Initializes a Renderable object with content and optional metadata fields (name, anchor_id, classes).

## Description:
The constructor creates a Renderable instance by storing the provided content dictionary and conditionally adding metadata fields (name, anchor_id, classes) to the content. This method serves as the foundation for all renderable presentation elements in the ydata-profiling report system, establishing the basic structure for content storage and metadata management.

This logic is separated into its own method to provide a clean initialization pattern that allows subclasses to extend the behavior while maintaining consistency in how content and metadata are handled across all renderable components.

## Args:
    content (Dict[str, Any]): Main content dictionary containing the data and metadata for the renderable element
    name (Optional[str]): Optional identifier for the element, defaults to None
    anchor_id (Optional[str]): Optional anchor identifier for linking, defaults to None
    classes (Optional[str]): Optional CSS classes for styling, defaults to None

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.content: Set to the provided content dictionary
    - self.content["name"]: Conditionally set if name parameter is not None
    - self.content["anchor_id"]: Conditionally set if anchor_id parameter is not None
    - self.content["classes"]: Conditionally set if classes parameter is not None

## Constraints:
    Preconditions:
    - The content parameter must be a dictionary
    - All parameters must be of the correct type (Dict[str, Any], Optional[str])
    
    Postconditions:
    - self.content is initialized with the provided content dictionary
    - Metadata fields are added to self.content only when their respective parameters are not None

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.name` · *method*

## Summary:
Returns the name identifier stored in the renderable's content dictionary.

## Description:
Provides access to the "name" field from the renderable's internal content dictionary. This property serves as a convenient accessor for the name metadata associated with presentation elements in the profiling report.

## Args:
    None

## Returns:
    str: The name identifier stored in self.content["name"]

## Raises:
    KeyError: When the "name" key is not present in self.content dictionary

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.content dictionary must contain a "name" key
    Postconditions: Returns the string value associated with the "name" key in self.content

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.anchor_id` · *method*

## Summary:
Returns the anchor identifier associated with this renderable component.

## Description:
Provides access to the anchor identifier stored in the component's content dictionary. This property is part of the standard interface for renderable components that require unique identification within a presentation context.

## Args:
    None

## Returns:
    str: The anchor identifier string stored in the component's content dictionary under the "anchor_id" key.

## Raises:
    KeyError: When the "anchor_id" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `self.content` dictionary must contain the key "anchor_id"
    Postconditions: Returns the string value associated with the "anchor_id" key in self.content

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.classes` · *method*

## Summary:
Returns the CSS classes associated with this renderable component.

## Description:
Provides access to the CSS classes string stored in the component's content dictionary. This property is part of the standard interface for renderable components that require CSS styling information for presentation purposes.

## Args:
    None

## Returns:
    str: The CSS classes string stored in the component's content dictionary under the "classes" key.

## Raises:
    KeyError: When the "classes" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `self.content` dictionary must contain the key "classes"
    Postconditions: Returns the string value associated with the "classes" key in self.content

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.render` · *method*

## Summary:
Abstract method defining the rendering interface for content representation.

## Description:
This abstract method establishes the interface for converting internal content into a rendered output format. As an abstract method in the Renderable base class, it must be implemented by all concrete subclasses to provide specific rendering behavior.

## Args:
    None

## Returns:
    Any: The return type is intentionally unspecified (Any) to allow flexibility for different rendering implementations. Concrete implementations typically return HTML, markdown, or string representations of the content.

## Raises:
    NotImplementedError: When called directly on the abstract Renderable class or when a concrete subclass hasn't implemented this method.

## State Changes:
    Attributes READ: 
    - self.content: The internal content dictionary containing the data to be rendered
    - Other properties derived from content (name, anchor_id, classes)

## Constraints:
    Preconditions:
    - The object must be properly initialized with content
    - Concrete implementations must override this method
    - The content dictionary should contain valid data for rendering
    
    Postconditions:
    - Returns a valid representation of the content in the appropriate format
    - Does not modify the internal content state

## Side Effects:
    None: This method is expected to be pure and not cause any external I/O or state changes beyond returning the rendered result.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__str__` · *method*

## Summary:
Returns the class name of the renderable object for string representation purposes.

## Description:
This method provides a string representation of the renderable object by returning its class name. It's implemented as part of the standard Python `__str__` protocol to enable meaningful string conversion of renderable components in the ydata-profiling report presentation system. The method is particularly useful for debugging, logging, and identifying renderable objects in collections or hierarchies.

## Args:
    None

## Returns:
    str: The name of the class that this renderable object represents.

## Raises:
    None

## State Changes:
    Attributes READ: self.__class__.__name__
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be an instance of a class that inherits from Renderable
    Postconditions: The returned string is always the exact class name of the object instance

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.convert_to_class` · *method*

## Summary:
Changes the runtime class of a Renderable object to the specified class.

## Description:
This class method dynamically alters the type of a Renderable object by replacing its class with a new class. It's designed to enable runtime polymorphism and type conversion within the presentation layer of the ydata-profiling system. This method is typically used during report generation to transform renderable objects into specialized subclasses based on context or configuration.

## Args:
    cls: The target class to convert the object to
    obj: The Renderable instance whose class will be changed
    flv: A callable parameter (currently unused in implementation)

## Returns:
    None: This method modifies the object in-place and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: obj.__class__ (modified in-place)

## Constraints:
    Preconditions: 
    - The obj parameter must be an instance of a class that inherits from Renderable
    - The cls parameter must be a valid class type
    Postconditions:
    - The obj's __class__ attribute will be set to cls
    - The object will behave according to the methods defined in cls

## Side Effects:
    None: This method only modifies the object's class reference and does not perform any I/O operations or external service calls

