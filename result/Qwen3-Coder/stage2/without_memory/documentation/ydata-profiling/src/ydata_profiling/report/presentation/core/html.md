# `html.py`

## `src.ydata_profiling.report.presentation.core.html.HTML` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.html.HTML.__init__` · *method*

## Summary:
Initializes an HTML item renderer with the specified HTML content.

## Description:
Configures an HTML item for presentation by setting up the internal content structure with the provided HTML string. This method establishes the item type as "html" and stores the HTML content in a structured format for later rendering.

## Args:
    content (str): The HTML content to be wrapped by this HTML item renderer.
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor, including optional name, anchor_id, and classes parameters.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though parent class constructors may raise exceptions for invalid parameters.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "html"
    - self.content: Set to a dictionary containing {"html": content} plus any additional content from kwargs

## Constraints:
    Preconditions:
    - content must be a string containing valid HTML markup
    - All kwargs must be valid parameters supported by the parent ItemRenderer class
    
    Postconditions:
    - The object is initialized with item_type set to "html"
    - The content dictionary contains the html key with the provided content value
    - All additional parameters from kwargs are properly stored in the content dictionary

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object state.

### `src.ydata_profiling.report.presentation.core.html.HTML.__repr__` · *method*

## Summary:
Returns a string representation of the HTML object indicating its type.

## Description:
This method provides a standardized string representation for HTML objects, returning the literal string "HTML". It is used primarily for debugging and logging purposes to quickly identify HTML instances in the codebase. This method overrides the default object representation to provide a more meaningful identifier for HTML elements within the ydata-profiling report generation framework.

## Args:
    None

## Returns:
    str: The string "HTML" representing the type of this object.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned string is always "HTML"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.html.HTML.render` · *method*

## Summary:
Renders HTML content by raising NotImplementedError, requiring subclasses to implement the rendering logic.

## Description:
This method serves as an abstract interface for rendering HTML content within the report presentation system. As part of the Renderable abstract base class hierarchy, it defines the contract that all renderable components must implement. The HTML class extends this contract by providing a concrete implementation that stores HTML content, while leaving the actual rendering behavior to be defined by subclasses.

The method is intentionally left unimplemented in the base HTML class to enforce proper inheritance and polymorphism within the report presentation framework. This design allows different HTML-based components to implement their own rendering strategies while maintaining a consistent interface.

In practice, subclasses of HTML should override this method to provide specific rendering logic that converts the stored HTML content into the appropriate output format (typically HTML string or DOM elements) for inclusion in reports.

## Args:
    None

## Returns:
    Any: This method raises NotImplementedError and never actually returns a value.

## Raises:
    NotImplementedError: Always raised when this method is called on the base HTML class.

## State Changes:
    Attributes READ: 
    - self.content (accessed through parent Renderable class properties like name, anchor_id, classes)
    - self.item_type (inherited from ItemRenderer)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - This method should only be called on subclasses that properly implement the render logic
    - The HTML class must be properly initialized with valid content
    
    Postconditions:
    - Method execution always results in NotImplementedError being raised
    - No state changes occur on the instance

## Side Effects:
    None

