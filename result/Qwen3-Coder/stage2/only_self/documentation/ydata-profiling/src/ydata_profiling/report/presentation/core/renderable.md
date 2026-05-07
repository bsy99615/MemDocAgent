# `renderable.py`

## `src.ydata_profiling.report.presentation.core.renderable.Renderable` · *class*

## Summary:
Abstract base class defining the interface for renderable objects in a reporting/presentation system.

## Description:
The Renderable class serves as the foundation for all objects that can be rendered in a report or presentation. It provides a standardized way to store content and metadata while enforcing a contract for rendering behavior through its abstract render() method. Concrete implementations must provide their own rendering logic while leveraging the shared content management and metadata handling capabilities.

This class enables a flexible reporting system where different types of report elements (tables, charts, text blocks, etc.) can be treated uniformly while maintaining their specific rendering requirements.

## State:
- content: Dict[str, Any] - Main data storage for the renderable object's content and metadata
- name: str (via property) - Optional identifier for the renderable object
- anchor_id: str (via property) - Optional anchor identifier for HTML/CSS linking
- classes: str (via property) - Optional CSS classes for styling

The content dictionary serves as the central data store, with name, anchor_id, and classes being stored as keys within this dictionary when provided during initialization.

## Lifecycle:
Creation: Instantiate with content dictionary and optional metadata (name, anchor_id, classes). The content dictionary is stored directly and metadata is added as keys to it.

Usage: Call render() method to generate the appropriate output representation. The render() method must be implemented by concrete subclasses.

Destruction: No explicit cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[Renderable.__init__] --> B[content = content]
    B --> C{name stored in content dict}
    C --> D{anchor_id stored in content dict}
    D --> E{classes stored in content dict}
    E --> F[Renderable.render()]
    F --> G[ConcreteImplementation.render()]
```

## Raises:
- None explicitly raised by __init__
- render() method raises NotImplementedError if called on the abstract base class

## Example:
```python
# Creating a renderable object
content = {"title": "Sample Report", "data": [1, 2, 3]}
renderable = Renderable(content, name="sample_report", anchor_id="report1")

# Accessing metadata properties
print(renderable.name)        # "sample_report"
print(renderable.anchor_id)   # "report1"

# Rendering (requires concrete implementation)
# result = renderable.render()  # Would raise NotImplementedError on base class
```

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__init__` · *method*

## Summary:
Initializes a Renderable object with content and optional metadata fields.

## Description:
Sets up the Renderable instance with the provided content dictionary and conditionally adds metadata fields (name, anchor_id, classes) to the content. This method serves as the constructor for Renderable objects, preparing them for presentation rendering.

## Args:
    content (Dict[str, Any]): The main content dictionary for this renderable item
    name (Optional[str]): Optional name identifier for the renderable item, defaults to None
    anchor_id (Optional[str]): Optional anchor ID for HTML linking, defaults to None
    classes (Optional[str]): Optional CSS classes for styling, defaults to None

## Returns:
    None: This method doesn't return anything

## Raises:
    None: This method doesn't explicitly raise any exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.content: Set to the provided content parameter
        - self.content["name"]: Conditionally set if name parameter is not None
        - self.content["anchor_id"]: Conditionally set if anchor_id parameter is not None
        - self.content["classes"]: Conditionally set if classes parameter is not None

## Constraints:
    Preconditions:
        - content must be a dictionary
        - name, anchor_id, and classes must be strings or None
    Postconditions:
        - self.content is initialized with the provided content
        - Metadata fields are added to self.content only when their respective parameters are not None

## Side Effects:
    None: This method doesn't perform any I/O operations or mutate external objects

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.name` · *method*

## Summary:
Returns the name identifier stored in the renderable content dictionary.

## Description:
Provides access to the name identifier associated with this renderable object. This property serves as a convenient accessor for the "name" key within the object's content dictionary, which is typically set during initialization.

## Args:
    None

## Returns:
    str: The name identifier stored in the content dictionary. This represents the logical name or identifier of the renderable component.

## Raises:
    KeyError: When the "name" key is not present in the content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The content dictionary must contain a "name" key, or a KeyError will be raised.
    Postconditions: The returned string value is immutable and represents the name identifier as set during object construction.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.anchor_id` · *method*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.classes` · *method*

## Summary:
Returns the CSS classes associated with this renderable component.

## Description:
This method provides access to the CSS classes stored in the component's content dictionary. It is used to retrieve the styling information that should be applied to the rendered HTML element.

## Args:
    None

## Returns:
    str: The CSS classes string stored in the component's content under the "classes" key.

## Raises:
    KeyError: If the "classes" key is not present in self.content dictionary.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.content dictionary must contain a "classes" key.
    Postconditions: The returned string is exactly the value stored under the "classes" key in self.content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.render` · *method*

## Summary:
Transforms the component's internal data into a presentation-ready format for report generation.

## Description:
The render method is an abstract interface that must be implemented by all concrete subclasses of Renderable to convert the component's internal data representation into a format suitable for inclusion in profiling reports. This method serves as the core abstraction point for the rendering pipeline, enabling polymorphic rendering of diverse report elements such as HTML content, tables, images, and structured containers.

During report generation, the rendering engine calls this method on each Renderable component to obtain presentation-ready output that can be embedded into the final report format (HTML, PDF, etc.). The method transforms the internal content dictionary and associated metadata into a standardized output format appropriate for the specific component type.

## Args:
    None

## Returns:
    Any: Presentation-ready output representing the component's content. Common return types include:
    - str: For HTML content and text-based components
    - dict: For structured data that needs further processing
    - Other format-specific representations depending on the concrete implementation

## Raises:
    NotImplementedError: When called on the abstract base class or when a concrete subclass fails to implement this method.

## State Changes:
    Attributes READ: 
    - self.content: The internal data storage dictionary containing component-specific data
    - All inherited attributes from Renderable (name, anchor_id, classes)

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Renderable instance must be properly initialized with valid content
    - Concrete subclasses must implement this method with appropriate rendering logic
    - The method should not modify the internal state of the object

    Postconditions:
    - Returns a valid presentation-ready representation of the component's content
    - The returned value should be compatible with the target output format of the report

## Side Effects:
    None: The method is intended to be pure and not cause any external I/O or state changes beyond returning the rendered content.

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.__str__` · *method*

## Summary:
Returns the class name of the renderable object as its string representation.

## Description:
This method provides a string representation of the renderable object by returning its class name. It is implemented as part of the standard Python `__str__` protocol and is typically called when the object is converted to a string using `str()` or when printed.

## Args:
    None

## Returns:
    str: The name of the class that instantiated this object.

## Raises:
    None

## State Changes:
    Attributes READ: self.__class__.__name__
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be an instance of Renderable or its subclasses.
    Postconditions: The returned value is always a string containing the class name.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.renderable.Renderable.convert_to_class` · *method*

## Summary:
Changes the class of a Renderable object to the class on which this method is called.

## Description:
This class method serves as a dynamic class conversion utility that allows changing the runtime type of a Renderable object to another class. It's typically used in presentation layer rendering pipelines where objects need to be transformed into different specialized types during processing.

## Args:
    obj (Renderable): The Renderable object whose class will be changed
    flv (Callable): A callable parameter (currently unused in implementation)

## Returns:
    None: This method modifies the object in-place and returns nothing

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: obj.__class__ (the class of the passed object is modified)

## Constraints:
    Preconditions: 
    - The `obj` parameter must be an instance of Renderable or its subclasses
    - The `cls` parameter (implicit via class method) must be a valid class type
    
    Postconditions:
    - The `obj` parameter's class will be changed to the class on which this method was called
    - The object maintains all its existing attributes and methods from the new class

## Side Effects:
    None: This method only modifies the object's class reference, not external state or I/O resources

