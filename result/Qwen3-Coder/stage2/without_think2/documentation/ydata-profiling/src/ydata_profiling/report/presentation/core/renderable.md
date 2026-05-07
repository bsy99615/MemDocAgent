# `renderable.py`

## `src.ydata_profiling.report.presentation.core.renderable.Renderable` · *class*

## Summary:
Abstract base class for renderable components in the ydata-profiling report presentation layer.

## Description:
The Renderable class serves as an abstract base class for all components that can be rendered in a report. It provides a common interface for storing content and metadata, while enforcing a contract for rendering functionality. This abstraction enables polymorphic handling of different types of report elements (charts, tables, text blocks, etc.) within the presentation layer.

## State:
- content: Dict[str, Any] - Core data structure containing the component's content and metadata. While the class expects this dictionary to contain the keys "name", "anchor_id", and "classes" for proper property access, these keys are not guaranteed to exist at instantiation time.
- name: str - Property that retrieves the component's name from content dictionary. Accessing this property assumes the "name" key exists in content.
- anchor_id: str - Property that retrieves the component's anchor ID from content dictionary. Accessing this property assumes the "anchor_id" key exists in content.
- classes: str - Property that retrieves the component's CSS classes from content dictionary. Accessing this property assumes the "classes" key exists in content.

## Lifecycle:
- Creation: Instantiate with content dictionary and optional metadata parameters (name, anchor_id, classes). The content dictionary should contain the required keys for properties to work properly, though they may be added during initialization.
- Usage: Call render() method to generate the actual representation of the component. Properties can be accessed at any time to retrieve metadata.
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[Renderable.__init__] --> B[Renderable.render]
    A --> C[Renderable.name]
    A --> D[Renderable.anchor_id]
    A --> E[Renderable.classes]
    B --> F[Concrete render implementation]
    C --> G[Access content[name]]
    D --> H[Access content[anchor_id]]
    E --> I[Access content[classes]]
```

## Raises:
- KeyError: When accessing name, anchor_id, or classes properties if the corresponding keys are not present in the content dictionary after initialization.

## Example:
```python
# Create a renderable instance
content = {"name": "my_chart", "anchor_id": "chart_1", "classes": "chart"}
renderable = Renderable(content, name="my_chart", anchor_id="chart_1", classes="chart")

# Access properties
print(renderable.name)  # Output: my_chart
print(renderable.anchor_id)  # Output: chart_1

# Render (abstract method must be implemented by subclasses)
# result = renderable.render()  # Would raise TypeError if not subclassed
```

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__init__` · *method*

## Summary:
Initializes a Renderable object with content and optional metadata fields.

## Description:
The `__init__` method constructs a Renderable instance by storing the provided content dictionary and conditionally adding metadata fields (name, anchor_id, classes) to it. This method prepares the object for rendering operations by setting up its internal content structure.

## Args:
    content (Dict[str, Any]): The main content dictionary that holds the renderable data.
    name (Optional[str]): An optional name identifier to be stored in the content dictionary. Defaults to None.
    anchor_id (Optional[str]): An optional anchor ID to be stored in the content dictionary. Defaults to None.
    classes (Optional[str]): An optional CSS classes string to be stored in the content dictionary. Defaults to None.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.content: Assigned the content parameter value
    - self.content["name"]: Conditionally set if name parameter is not None
    - self.content["anchor_id"]: Conditionally set if anchor_id parameter is not None
    - self.content["classes"]: Conditionally set if classes parameter is not None

## Constraints:
    Preconditions:
    - The content parameter must be a dictionary
    - All parameters except content are optional and can be None
    - The content dictionary will be modified in-place when optional parameters are provided
    
    Postconditions:
    - self.content will reference the same dictionary object as the content parameter
    - If name, anchor_id, or classes are provided, they will be added to self.content as keys

## Side Effects:
    None: This method does not perform any I/O operations or mutate external objects.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.name` · *method*

## Summary:
Retrieves the name identifier from the renderable's content dictionary.

## Description:
Provides access to the name field stored within the renderable object's content dictionary. This method encapsulates access to the internal content structure, providing a clean interface for retrieving the name attribute while maintaining data abstraction.

## Args:
    None

## Returns:
    str: The name value stored in self.content["name"]

## Raises:
    KeyError: If the "name" key is not present in self.content dictionary

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary-like object
    - self.content must contain a "name" key
    Postconditions: 
    - The returned string is identical to the value stored at self.content["name"]

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.anchor_id` · *method*

## Summary:
Returns the anchor identifier associated with this renderable component.

## Description:
This method provides access to the anchor ID stored within the component's content dictionary. It serves as a property-like accessor for the "anchor_id" key in the content mapping.

The method is part of the Renderable base class and ensures consistent access to anchor identifiers across all renderable components in the presentation layer. It is implemented as a method rather than a simple property to maintain consistency with the pattern used by other similar accessors like name() and classes().

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
    Postconditions: The returned value is exactly the string stored under the "anchor_id" key in self.content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.classes` · *method*

## Summary:
Returns the CSS classes associated with the renderable content.

## Description:
This method provides access to the CSS classes stored in the content dictionary of a Renderable object. It serves as a getter for the "classes" key in the content attribute, allowing downstream components to retrieve styling information for rendering purposes. This method is part of the Renderable abstract base class and is implemented as a property.

## Args:
    None

## Returns:
    str: The CSS classes string stored under the "classes" key in the content dictionary.

## Raises:
    KeyError: If the "classes" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The content attribute must be a dictionary containing a "classes" key.
    Postconditions: The returned value is the exact string stored under the "classes" key in content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.render` · *method*

## Summary:
Abstract method that defines the interface for rendering content into presentation format.

## Description:
This abstract method establishes the contract for converting internal content into a presentation-ready format. As part of the abstract base class Renderable, this method must be implemented by all concrete subclasses to produce appropriate output representations. The method serves as the core interface for transforming internal data structures into formats suitable for display or serialization.

## Args:
    None

## Returns:
    Any: The rendered output, which varies by implementation but typically represents the content in a format suitable for presentation.

## Raises:
    NotImplementedError: When called on the abstract base class directly without a concrete implementation.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be a concrete subclass of Renderable with a valid content dictionary.
    Postconditions: The returned value represents the properly formatted presentation content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__str__` · *method*

## Summary:
Returns the class name of the renderable object as a string representation.

## Description:
This method provides a string representation of the renderable object by returning its class name. It is typically invoked when the object needs to be converted to a string format, such as during debugging, logging, or display operations. The method is part of the standard Python object protocol and allows for consistent identification of renderable objects through their class names.

## Args:
    None

## Returns:
    str: The name of the class to which the object instance belongs.

## Raises:
    None

## State Changes:
    Attributes READ: self.__class__
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be properly initialized and have a valid class reference.
    Postconditions: The returned string will always be the exact class name of the object instance.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.convert_to_class` · *method*

## Summary:
Changes the class type of a Renderable object to a specified class.

## Description:
This function dynamically alters the type of a Renderable object by replacing its class with a new class. It performs a runtime type conversion that allows objects to behave as instances of different classes while maintaining their existing attributes and data. This is commonly used in the presentation layer to adapt Renderable objects to different rendering contexts or requirements.

## Args:
    cls (type): The target class to convert the object to.
    obj (Renderable): The Renderable instance whose class will be changed.
    flv (Callable): A callable function parameter that may be used for value transformation or validation during the conversion process, though not directly utilized in this implementation.

## Returns:
    None: This function modifies the object in-place and does not return a value.

## Raises:
    None: This function does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions: 
    - The obj parameter must be an instance of Renderable or a subclass thereof.
    - The cls parameter must be a valid class type that can be assigned to obj.__class__.
    
    Postconditions:
    - The obj's class will be replaced with cls.
    - The object will retain all its existing attributes and methods, but will now behave according to the new class's implementation.

## Side Effects:
    None: This function only modifies the object's class attribute and does not perform any I/O operations or external service calls.

