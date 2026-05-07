# `variable.py`

## `src.ydata_profiling.report.presentation.core.variable.Variable` · *class*

## Summary:
Represents a variable element in a profiling report with top and bottom content sections.

## Description:
The Variable class is a specialized item renderer designed to display variable-related information in profiling reports. It consists of two main content sections: a top section for primary variable data and an optional bottom section for additional details or metadata. This class is part of the presentation layer of the ydata profiling system and is used to structure variable-specific report elements.

The class is typically instantiated by report generation components that need to display variable information in a structured format. It provides a standardized way to organize variable data with a clear visual hierarchy through its top and bottom content sections. The class also includes a utility method for converting existing renderable objects to the Variable class type.

## State:
- top: Renderable - Required content for the primary variable information displayed at the top
- bottom: Optional[Renderable] - Optional secondary content displayed below the top section, can be None
- ignore: bool - Flag indicating whether this variable should be ignored during processing, defaults to False
- item_type: str - Class attribute identifying this as a "variable" type item, inherited from ItemRenderer
- content: dict - Dictionary containing the item's data and metadata, inherited from Renderable parent class

## Lifecycle:
- Creation: Instantiate with a required top Renderable object and optional bottom Renderable and ignore flag
- Usage: Typically used in report generation workflows where variable data needs structured presentation
- Destruction: Inherits standard Python object lifecycle management

## Method Map:
```mermaid
graph TD
    A[Variable.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[content = {"top": top, "bottom": bottom, "ignore": ignore}]
    D --> E[Variable.__str__]
    E --> F[Variable.__repr__]
    F --> G[Variable.convert_to_class]
    G --> H[Variable.render()] --> I[NotImplementedError]
```

## Raises:
- None explicitly raised by __init__
- render() method raises NotImplementedError when called on Variable instances

## Example:
```python
# Create a variable with top content
top_content = Text("Age Variable")
bottom_content = Table([["Min", "Max"], [18, 85]])

# Create variable instance
variable = Variable(top_content, bottom_content, ignore=False)

# String representation
print(str(variable))  # Shows formatted variable structure

# Convert existing renderable to Variable class
existing_renderable = Renderable({"some": "content"})
Variable.convert_to_class(existing_renderable, lambda x: None)
```

### `src.ydata_profiling.report.presentation.core.variable.Variable.__init__` · *method*

## Summary:
Initializes a Variable instance with top and bottom content sections for report presentation.

## Description:
The Variable.__init__ method constructs a variable element for profiling reports by setting up the required content structure with top and bottom renderable components. This method is part of the presentation layer that organizes variable-specific information in a structured format with clear visual hierarchy.

The method delegates to the parent ItemRenderer.__init__ which handles the core initialization logic including setting the item type identifier and storing the content dictionary. This approach maintains consistency with the reporting system's architecture where all renderable items follow the same initialization pattern.

## Args:
    top (Renderable): Required top content section for primary variable information
    bottom (Optional[Renderable]): Optional bottom content section for additional details, defaults to None
    ignore (bool): Flag indicating whether this variable should be ignored during processing, defaults to False
    **kwargs: Additional keyword arguments passed to the parent class initialization

## Returns:
    None: This method initializes the instance and does not return a value

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "variable" by parent class
    - self.content: Dictionary containing {"top": top, "bottom": bottom, "ignore": ignore}

## Constraints:
    Preconditions:
    - top must be a Renderable instance
    - bottom must be either a Renderable instance or None
    - ignore must be a boolean value
    
    Postconditions:
    - Instance is properly initialized with the specified content structure
    - The item_type is set to "variable" 
    - Content dictionary contains all specified parameters

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.variable.Variable.__str__` · *method*

## Summary:
Returns a formatted string representation of the Variable object showing its top and bottom content sections.

## Description:
Creates a human-readable string representation of a Variable instance by formatting its top and bottom content sections. This method is particularly useful for debugging and logging purposes, providing a clear view of the variable's structure and content without exposing internal implementation details.

The method accesses the content dictionary's "top" and "bottom" keys, converts them to strings, and formats newlines with tab indentation for improved readability. It's called automatically when the built-in `str()` function is applied to a Variable instance.

## Args:
    None: This method takes no parameters beyond the implicit self reference.

## Returns:
    str: A formatted string with the structure:
         "Variable\n- top: <formatted_top_content>\n- bottom: <formatted_bottom_content>"
         where newlines in content are replaced with "\n\t" for proper indentation.

## Raises:
    KeyError: If self.content does not contain "top" or "bottom" keys.
    TypeError: If self.content["top"] or self.content["bottom"] cannot be converted to string.

## State Changes:
    Attributes READ:
    - self.content: Reads the content dictionary to access "top" and "bottom" keys
    - self.content["top"]: Accesses the top content value
    - self.content["bottom"]: Accesses the bottom content value

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing "top" and "bottom" keys
    - Both self.content["top"] and self.content["bottom"] must be convertible to strings
    - The content dictionary must be properly initialized by the parent class

    Postconditions:
    - Returns a properly formatted string representation
    - Does not modify the object's state
    - The returned string contains the "Variable" header followed by formatted top and bottom sections

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside self. It only reads from existing instance attributes and returns a formatted string.

### `src.ydata_profiling.report.presentation.core.variable.Variable.__repr__` · *method*

## Summary:
Returns a string representation identifying this object as a Variable instance.

## Description:
Provides a concise string identifier for Variable objects, typically used for debugging and logging purposes. This method follows Python conventions where `__repr__` should return an unambiguous representation of the object that ideally could recreate the object.

## Args:
    None

## Returns:
    str: The string "Variable" that identifies this object's type.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the literal string "Variable"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.variable.Variable.render` · *method*

## Summary:
Abstract rendering interface that must be implemented by subclasses to generate presentation output for variable report components.

## Description:
This method serves as the abstract rendering interface for Variable objects in the ydata profiling report presentation system. As a required method of the ItemRenderer base class, it must be implemented by concrete subclasses to define how a variable structure containing top and bottom renderable components should be rendered into presentation format.

The Variable class acts as a structural container for report elements, with the render method providing the mechanism for converting this structure into displayable content. This follows the standard pattern in the ydata-profiling system where abstract base classes define interfaces that concrete implementations must fulfill.

## Args:
    None

## Returns:
    Any: This method raises NotImplementedError when called on the base Variable class and is intended to be overridden by subclasses to return presentation-ready content.

## Raises:
    NotImplementedError: Always raised when invoked on the base Variable class before subclass implementation.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.variable.Variable.convert_to_class` · *method*

## Summary:
Converts a Renderable object to a different class while processing its top and bottom content.

## Description:
This method dynamically changes the class of a Renderable object to a specified class and processes any top/bottom content through a provided function. It's used in the presentation layer to transform renderable objects during rendering operations.

## Args:
    cls: The target class to convert the object to
    obj: A Renderable object whose class will be changed
    flv: A callable function that processes the content items

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: obj.content, obj.content["top"], obj.content["bottom"]
    Attributes WRITTEN: obj.__class__

## Constraints:
    Preconditions: 
    - obj must be a Renderable instance
    - flv must be callable
    - obj.content must be a dictionary-like object
    
    Postconditions:
    - obj's class will be changed to cls
    - If obj.content contains "top" key with non-None value, flv will be called on it
    - If obj.content contains "bottom" key with non-None value, flv will be called on it

## Side Effects:
    Mutates the class of the input object
    Calls the provided flv function with content items

