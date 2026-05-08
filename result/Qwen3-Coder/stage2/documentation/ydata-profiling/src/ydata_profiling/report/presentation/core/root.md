# `root.py`

## `src.ydata_profiling.report.presentation.core.root.Root` · *class*

## Summary:
Root represents the top-level container for report presentations, serving as the main entry point for rendering complete profiling reports.

## Description:
The Root class acts as the primary container for entire profiling reports, encapsulating the main body content, footer, and styling configuration. It serves as the root node in the report presentation hierarchy and is responsible for orchestrating the rendering of complete reports. As a specialized ItemRenderer, it enforces a consistent structure for report-level elements while providing mechanisms for dynamic class conversion during processing.

This class is typically instantiated by report generation systems rather than directly by end-users, and it forms the foundation upon which complete profiling reports are built.

## State:
- item_type: str - Set to "report" by constructor, identifying this as a report-level renderer
- content: dict - Contains keys "body" (Renderable), "footer" (Renderable), and "style" (Style) 
- name: str - Human-readable identifier for the report, passed through from constructor
- anchor_id: str - Optional anchor identifier, inherited from Renderable parent
- classes: str - Optional CSS classes, inherited from Renderable parent

## Lifecycle:
- Creation: Instantiate with required parameters name (str), body (Renderable), footer (Renderable), and style (Style)
- Usage: Called by report generation pipelines during rendering process; render() method is expected to be implemented by subclasses or replaced during processing
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Root.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[content setup]
    D --> E[Root.render()]
    E --> F[NotImplementedError]
    G[Root.convert_to_class] --> H[obj.__class__ = cls]
    H --> I[flv(body)]
    I --> J[flv(footer)]
```

## Raises:
- NotImplementedError: Raised when render() method is called directly, as this class is intended to be subclassed or replaced during processing

## Example:
```python
# Typical usage would be through report generation pipeline
from ydata_profiling.report.presentation.core.root import Root
from ydata_profiling.report.presentation.core.html import HTML
from ydata_profiling.config import Style

# Create body and footer renderables
body_content = HTML("Report Body Content")
footer_content = HTML("Report Footer")

# Create style configuration
style_config = Style(primary_colors=["#0000ff"])

# Create root container
root = Root(
    name="my_report",
    body=body_content,
    footer=footer_content,
    style=style_config
)

# The render method should not be called directly on this base class
# It's intended to be overridden or replaced during the report generation process
```

### `src.ydata_profiling.report.presentation.core.root.Root.__init__` · *method*

## Summary:
Initializes a Root object that serves as the top-level container for report presentations, setting up the report structure with body content, footer, and styling configuration.

## Description:
The Root.__init__ method constructs a report-level container that encapsulates the main body content, footer, and styling configuration for a complete profiling report. This method establishes the fundamental structure for report rendering by initializing the item_type to "report" and organizing the core components (body, footer, style) within the content dictionary. The method is typically called during report generation pipelines when constructing the complete report hierarchy.

This logic is separated into its own method to ensure proper initialization of the report structure while maintaining consistency with the ItemRenderer base class interface. It provides a clean abstraction for report-level elements that can be processed and rendered as a complete unit.

## Args:
    name (str): Human-readable identifier for the report
    body (Renderable): Main content body of the report, implementing the Renderable interface
    footer (Renderable): Footer content of the report, implementing the Renderable interface  
    style (Style): Styling configuration object that defines visual presentation parameters for the report
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer.__init__ method

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions, though parent class initialization may raise TypeError if arguments are invalid

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "report" to identify this as a report-level renderer
    - self.content: Dictionary containing "body", "footer", and "style" keys with their respective values
    - self.name: Set to the provided name parameter
    - Other inherited attributes from Renderable parent class (anchor_id, classes)

## Constraints:
    Preconditions:
    - body must be a Renderable instance
    - footer must be a Renderable instance  
    - style must be a Style instance
    - name must be a string
    - All parameters must be properly initialized before calling

    Postconditions:
    - The object is initialized as an ItemRenderer with item_type="report"
    - The content dictionary contains the body, footer, and style components
    - The name attribute is properly set for identification

## Side Effects:
    None: This method performs only object initialization and does not cause external I/O, service calls, or mutations to objects outside the instance being constructed

### `src.ydata_profiling.report.presentation.core.root.Root.__repr__` · *method*

## Summary:
Returns a string representation of the Root object, identifying it as "Root".

## Description:
Provides a standardized string representation for Root instances, returning the literal string "Root". This method is automatically invoked when the built-in repr() function is called on a Root object or when the object is displayed in interactive environments.

## Args:
    None

## Returns:
    str: The string "Root" identifying this object type.

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

## Summary:
Renders the root element of a report presentation into its final formatted output.

## Description:
The render method is an abstract interface that must be implemented by subclasses to convert the root report element into its final presentation format. This method serves as the entry point for generating the complete report output from the hierarchical structure of renderable elements.

The Root class implements this abstract method but raises NotImplementedError to enforce that concrete implementations must override it with specific rendering logic appropriate for the target output format (HTML, JSON, etc.).

## Args:
    **kwargs: Additional keyword arguments that may be used by specific implementations for formatting, styling, or output configuration.

## Returns:
    Any: The rendered output in the appropriate format for the target presentation system (typically HTML string, dictionary, or other serialized format).

## Raises:
    NotImplementedError: Always raised by the base Root class implementation, indicating that subclasses must provide their own rendering logic.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing the body and footer renderable elements
    - self.name: Optional identifier for the root element
    - self.style: Styling configuration for the report
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Root instance must be properly initialized with required content (body and footer renderables)
    - Subclasses must implement this method with specific rendering logic
    - The method should handle any additional kwargs appropriately for the target output format
    
    Postconditions:
    - When implemented, the method returns a properly formatted representation of the report
    - The returned value should be compatible with the target presentation system

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state. However, concrete implementations may have side effects such as file I/O or network calls depending on the output format.

### `src.ydata_profiling.report.presentation.core.root.Root.convert_to_class` · *method*

## Summary:
Changes the runtime class of a Renderable object to the Root class while processing its body and footer content through a provided function.

## Description:
This classmethod dynamically transforms a Renderable object into a Root instance by changing its class type. It's specifically designed for use within the ydata-profiling report presentation layer to convert renderable objects into root-level containers during report generation. The method processes the object's body and footer content (if present) by applying the provided callback function to each, enabling content transformation during the class conversion process.

The method follows a consistent pattern with similar convert_to_class implementations across the presentation layer, allowing for dynamic type conversion while preserving content structure and enabling content processing.

## Args:
    obj: A Renderable object whose class will be changed to Root
    flv: A callable function that processes the object's body and footer content elements

## Returns:
    None: This method modifies the object in-place and does not return a value

## Raises:
    None explicitly raised: The method assumes the provided arguments are valid and doesn't raise explicit exceptions

## State Changes:
    Attributes READ: obj.content (accessed to check for "body" and "footer" keys)
    Attributes WRITTEN: obj.__class__ (modified in-place to change object's class to Root)

## Constraints:
    Preconditions:
    - obj must be an instance of Renderable or a subclass
    - flv must be callable
    - obj.content must be a dictionary-like object containing "body" and/or "footer" keys
    
    Postconditions:
    - obj's __class__ attribute will be set to Root
    - If "body" exists in obj.content, flv will be called with obj.content["body"] as argument
    - If "footer" exists in obj.content, flv will be called with obj.content["footer"] as argument

## Side Effects:
    None: This method only modifies the object's class reference and applies a callback function to content elements, but doesn't perform any I/O operations or mutate external state

