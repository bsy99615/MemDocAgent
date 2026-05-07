# `variable.py`

## `src.ydata_profiling.report.presentation.core.variable.Variable` · *class*

## Summary:
Represents a variable presentation element that combines top and bottom content sections for display in ydata-profiling reports.

## Description:
The Variable class is a specialized presentation element that organizes content into top and bottom sections, commonly used to display variable information in profiling reports. It inherits from ItemRenderer, which in turn inherits from Renderable, establishing a clear hierarchy for presentation components in the ydata-profiling system.

This class serves as a container for variable-related data and metadata, allowing for structured presentation of variable statistics, distributions, and other profiling information. The class is designed to be subclassed, with the render() method requiring implementation in concrete subclasses to define how the variable content should be presented.

The Variable class is particularly useful for creating compound presentation elements where information needs to be organized in a hierarchical manner, such as showing variable names and descriptions in the top section and statistical summaries or visualizations in the bottom section.

## State:
- item_type: str - Set to "variable" by the constructor, identifying this as a variable-type presentation element
- content: dict - Contains the structured data with keys:
  - "top": Renderable - Required content for the top section
  - "bottom": Optional[Renderable] - Optional content for the bottom section
  - "ignore": bool - Flag indicating whether this variable should be ignored during rendering (default: False)
- name: str (inherited from Renderable) - Optional human-readable identifier
- anchor_id: str (inherited from Renderable) - Optional HTML anchor identifier
- classes: str (inherited from Renderable) - Optional CSS classes for styling

## Lifecycle:
- Creation: Instantiate with a required top Renderable, optional bottom Renderable, and optional ignore flag
- Usage: Call render() method on concrete subclasses to generate presentation output
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Variable] --> B[ItemRenderer]
    B --> C[Renderable]
    C --> D{render()}
    D --> E[Subclass Implementation]
    A --> F[__str__]
    A --> G[__repr__]
    A --> H[convert_to_class]
```

## Raises:
- TypeError: May be raised during initialization if parent class arguments are invalid
- NotImplementedError: Raised when render() method is called directly on Variable instances (must be implemented by subclasses)

## Example:
```python
# Create a Variable with top and bottom content
top_content = Text("Age Variable Statistics")
bottom_content = Table([["Mean", "25.5"], ["Std Dev", "5.2"]])

variable = Variable(top=top_content, bottom=bottom_content, ignore=False)

# String representation for debugging
print(str(variable))  # Shows formatted top/bottom content

# Convert existing renderable to Variable class (utility method)
# This would typically be used internally during report generation
# Variable.convert_to_class(existing_renderable, process_function)
```

### `src.ydata_profiling.report.presentation.core.variable.Variable.__init__` · *method*

## Summary:
Initializes a Variable presentation element with top and bottom content sections for ydata-profiling reports.

## Description:
Constructs a Variable object that organizes presentation content into top and bottom sections. This constructor initializes the object with the specified content structure and sets the item_type to "variable", enabling proper identification within the ydata-profiling report presentation system.

## Args:
    top (Renderable): Required top section content for the variable presentation.
    bottom (Optional[Renderable]): Optional bottom section content. Defaults to None.
    ignore (bool): Flag indicating whether this variable should be ignored during rendering. Defaults to False.
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    TypeError: If parent class initialization fails due to invalid argument types or missing required arguments.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "variable" 
    - self.content: Dictionary containing "top", "bottom", and "ignore" keys

## Constraints:
    Preconditions:
    - The `top` parameter must be a valid Renderable instance
    - The `bottom` parameter, if provided, must be a valid Renderable instance or None
    - The `ignore` parameter must be a boolean value
    
    Postconditions:
    - The object's item_type attribute is set to "variable"
    - The content dictionary contains the provided top, bottom, and ignore values
    - The object inherits all standard Renderable and ItemRenderer properties

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object state.

### `src.ydata_profiling.report.presentation.core.variable.Variable.__str__` · *method*

## Summary:
Returns a formatted string representation of a Variable object showing its top and bottom content.

## Description:
The `__str__` method generates a human-readable string representation of a Variable instance, displaying its top and bottom content sections. This method is primarily intended for debugging and development purposes, providing a clear view of the variable's structure and content without requiring detailed inspection of the underlying data structures.

The method accesses the content dictionary stored in the Variable instance, specifically retrieving the "top" and "bottom" entries, converting them to strings, and formatting them with proper indentation for multi-line content.

## Args:
    None

## Returns:
    str: A formatted string containing the Variable label followed by its top and bottom content sections, with multi-line content properly indented.

## Raises:
    KeyError: If the content dictionary does not contain the required "top" or "bottom" keys.
    TypeError: If the content values cannot be converted to strings.

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Variable instance must have a content dictionary with "top" and "bottom" keys.
    Postconditions: The returned string is formatted with proper indentation for multi-line content.

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.variable.Variable.__repr__` · *method*

## Summary:
Returns a string representation of the Variable class instance, consistently returning "Variable".

## Description:
The `__repr__` method provides a standardized string representation for Variable instances. This method is part of the Variable class which is designed to represent variable-specific elements in the ydata-profiling report presentation layer. The method is typically called by Python's built-in repr() function or when an object needs to be displayed in debugging contexts.

This implementation follows a convention where all instances of the Variable class return the same string representation, which helps in identifying the class type during debugging or logging operations.

## Args:
    None

## Returns:
    str: Always returns the literal string "Variable"

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The method always returns the string "Variable" regardless of the instance state

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.variable.Variable.render` · *method*

## Summary:
Raises NotImplementedError indicating that this method must be implemented by subclasses to render variable-specific content.

## Description:
This method serves as an abstract interface for rendering variable presentation elements in the ydata profiling report system. As a subclass of ItemRenderer, Variable implements the standard rendering contract but delegates the actual rendering logic to concrete implementations. The method is intentionally left unimplemented in the base Variable class to enforce that subclasses provide their own rendering behavior.

The render method is called during the report generation pipeline when presentation elements need to be converted to their final output format (HTML, JSON, etc.). This method is part of the standard rendering workflow that processes different types of report components.

## Args:
    None

## Returns:
    Any: This method is not implemented in the base Variable class and will always raise NotImplementedError.

## Raises:
    NotImplementedError: Always raised when this method is called on a Variable instance, indicating that subclasses must implement this method.

## State Changes:
    Attributes READ: None - This method does not read any instance attributes directly
    Attributes WRITTEN: None - This method does not modify any instance attributes

## Constraints:
    Preconditions: None - No specific preconditions apply to calling this method
    Postconditions: None - This method never successfully returns due to the NotImplementedError

## Side Effects:
    None - This method does not perform any I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.variable.Variable.convert_to_class` · *method*

## Summary:
Changes the runtime class of a Renderable object to the specified class while processing its top and bottom content elements.

## Description:
This utility function dynamically converts a Renderable object to a different class type by modifying its `__class__` attribute. It also processes the "top" and "bottom" content elements of the object by applying the provided callback function to each if they exist and are not None. This function is used during presentation rendering to transform renderable objects into specialized subclasses while preserving and processing their content structure.

## Args:
    cls: The target class to convert the object to
    obj: A Renderable object whose class will be changed
    flv: A callable function that processes the object's top and bottom content elements

## Returns:
    None: This method modifies the object in-place and does not return a value

## Raises:
    None explicitly raised: The method assumes the provided arguments are valid and doesn't raise explicit exceptions

## State Changes:
    Attributes READ: obj.content (accessed to check for "top" and "bottom" keys)
    Attributes WRITTEN: obj.__class__ (modified in-place to change object's class)

## Constraints:
    Preconditions:
    - obj must be an instance of Renderable or a subclass
    - flv must be callable
    - cls must be a valid class type
    
    Postconditions:
    - obj's __class__ attribute will be set to cls
    - If "top" exists in obj.content and is not None, flv will be called with obj.content["top"] as argument
    - If "bottom" exists in obj.content and is not None, flv will be called with obj.content["bottom"] as argument

## Side Effects:
    None: This method only modifies the object's class reference and applies a callback function to content elements, but doesn't perform any I/O operations or mutate external state

