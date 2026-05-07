# `root.py`

## `src.ydata_profiling.report.presentation.core.root.Root` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.root.Root.__init__` · *method*

## Summary:
Initializes a Root report component with body content, footer, and styling configuration.

## Description:
Constructs a Root instance that serves as the main container for report presentation elements. This method sets up the foundational structure for a complete report by establishing the report type identifier and storing the core components (body, footer, and style) within the content dictionary.

The Root component acts as the top-level container in the report hierarchy, aggregating all report elements under a unified presentation structure. This method is specifically designed to initialize the Root class with its essential building blocks while maintaining compatibility with the ItemRenderer inheritance chain.

## Args:
    name (str): Human-readable identifier for the report
    body (Renderable): Main content section of the report
    footer (Renderable): Footer section of the report
    style (Style): Styling configuration for report appearance
    **kwargs: Additional keyword arguments passed to parent constructors for metadata (name, anchor_id, classes, etc.)

## Returns:
    None: This method initializes the object state and returns nothing

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "report"
    - self.content: Dictionary containing "body", "footer", and "style" keys with their respective values
    - self.name: Stored in content dictionary via parent class

## Constraints:
    Preconditions:
    - body must be a Renderable instance
    - footer must be a Renderable instance  
    - style must be a Style instance
    - name must be a string

    Postconditions:
    - self.item_type is set to "report"
    - self.content contains the body, footer, and style components as specified
    - The object maintains proper inheritance from ItemRenderer and Renderable

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.root.Root.__repr__` · *method*

## Summary:
Returns a string representation of the Root object, identifying it as a Root instance.

## Description:
The `__repr__` method provides a concise string identifier for Root instances, returning the literal string "Root". This method is part of Python's standard object representation protocol and is used primarily for debugging and development purposes to quickly identify object types.

This method is specifically implemented in the Root class to provide a clear, unambiguous representation of Root instances in debugging contexts and interactive sessions. It's a standard practice to override `__repr__` in custom classes to make debugging easier.

## Args:
    None

## Returns:
    str: The string "Root" for all Root instances

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Root"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.root.Root.render` · *method*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.root.Root.convert_to_class` · *method*

## Summary:
Changes the class type of a Renderable object to the class on which this method is called and processes its body and footer content using a provided function.

## Description:
This classmethod dynamically converts a Renderable object to a specific class type by modifying its class attribute. When called on the Root class, it converts objects to Root instances. It's used during report presentation rendering to transform objects into specific types while preserving their content structure. The method applies a transformation function to the object's body and footer content elements when they exist.

## Args:
    obj (Renderable): The Renderable object whose class will be changed to the class on which this method is called
    flv (Callable): Function to apply to body and footer content elements if they exist

## Returns:
    None: This method modifies the object in-place and doesn't return anything

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
        - obj.content (to check for "body" and "footer" keys)
    Attributes WRITTEN:
        - obj.__class__ (modified to become the target class)

## Constraints:
    Preconditions:
        - obj must be an instance of Renderable or its subclasses
        - flv must be callable
        - obj.content must be a dictionary-like object
    Postconditions:
        - obj.__class__ will be set to the class on which this method was called
        - If "body" key exists in obj.content, flv will be called on obj.content["body"]
        - If "footer" key exists in obj.content, flv will be called on obj.content["footer"]

## Side Effects:
    - Modifies the class type of the input object in-place
    - Calls the provided function flv on body and footer content elements

