# `table.py`

## `src.ydata_profiling.report.presentation.core.table.Table` · *class*

## Summary:
Table is a presentation layer component that represents structured tabular data for report generation, inheriting from ItemRenderer to provide standardized rendering behavior.

## Description:
The Table class serves as a specialized container for organizing and presenting tabular data within profiling reports. It inherits from ItemRenderer, establishing a consistent interface for report items while providing specific functionality for handling table-like data structures. This class acts as a base abstraction that enforces proper initialization of table content including rows, styling configuration, and optional metadata such as names and captions.

The Table class is intended to be subclassed by concrete implementations that provide specific rendering logic for different table formats or presentation styles. It maintains a standardized structure for table data while delegating the actual visualization to derived classes through the abstract render() method.

## State:
- rows: Sequence - Contains the tabular data rows to be displayed; type is constrained to any sequence-like structure (list, tuple, etc.)
- style: Style - Configuration object containing visual styling parameters for the table presentation; includes color schemes, logos, and UI themes
- name: Optional[str] - Human-readable identifier for the table, stored in the content dictionary for metadata purposes
- caption: Optional[str] - Optional descriptive text that appears as a table caption, stored in the content dictionary for presentation purposes

## Lifecycle:
- Creation: Instantiated with required rows and style parameters, optionally including name and caption metadata. Uses ItemRenderer's initialization pattern to set up the content dictionary with all necessary parameters.
- Usage: Typically used as a base class for concrete table implementations. The render() method must be overridden by subclasses to provide actual visualization logic.
- Destruction: Managed by Python's garbage collection; no explicit cleanup required.

## Method Map:
```mermaid
graph TD
    A[Table.__init__] --> B[ItemRenderer.__init__]
    B --> C[content dictionary setup]
    C --> D[Table.render()]
    D --> E[Subclass Implementation]
    A --> F[Table.__repr__]
```

## Raises:
- No explicit exceptions raised during __init__ as it delegates to parent class initialization
- NotImplementedError raised by render() method to enforce implementation in subclasses

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.core.table import Table

# Create a basic table with minimal configuration
style = Style()
rows = [["Name", "Age"], ["Alice", 30], ["Bob", 25]]
table = Table(rows=rows, style=style, name="Sample Data")

# The table can be rendered by subclasses that implement render()
# table.render()  # Would raise NotImplementedError in base class
```

### `src.ydata_profiling.report.presentation.core.table.Table.__init__` · *method*

## Summary:
Initializes a table item renderer with rows, styling, and optional metadata.

## Description:
Configures a table item for report presentation by setting up its core content including data rows, styling configuration, and optional identifying information. This method delegates initialization to the parent ItemRenderer class, ensuring consistent handling of report item properties like name, anchor ID, and CSS classes. The table item is designed to display tabular data in profiling reports with customizable styling and metadata.

## Args:
    rows (Sequence): Collection of data rows to display in the table structure
    style (Style): Configuration object defining visual styling properties for the table
    name (Optional[str]): Human-readable identifier for the table item, defaults to None
    caption (Optional[str]): Table caption text, defaults to None
    **kwargs: Additional keyword arguments passed to parent constructor for metadata

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    No explicit exceptions defined in this method signature

## State Changes:
    Attributes READ: No self attributes are read during initialization
    Attributes WRITTEN: 
    - self.item_type: Set to "table" string identifier
    - self.content: Dictionary containing rows, name, caption, and style data

## Constraints:
    Preconditions:
    - rows parameter must be a sequence-like object (list, tuple, etc.)
    - style parameter must be a valid Style configuration object
    - All kwargs must be valid metadata parameters accepted by parent class
    
    Postconditions:
    - Object is properly initialized as a table-type report item
    - Content dictionary contains all provided parameters under appropriate keys

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.table.Table.__repr__` · *method*

## Summary:
Returns a string representation of the Table object indicating its type.

## Description:
This method provides a simple string identifier for Table instances, primarily used for debugging and logging purposes. It's called during object representation operations (like when printing or converting to string) and returns a fixed string "Table" regardless of the table's content or configuration.

## Args:
    None

## Returns:
    str: Always returns the literal string "Table"

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.table.Table.render` · *method*

## Summary:
Abstract rendering interface that enforces implementation of table display logic in subclasses.

## Description:
The render method in the Table class serves as an abstract interface that enforces concrete implementations to provide rendering logic for tabular data. As a method inherited from ItemRenderer (the base class for all report items), this method establishes the standard contract that all table items must implement their own rendering behavior. When invoked on a Table instance, it raises NotImplementedError to signal that subclasses must override this method with their specific rendering implementation.

This method exists as part of the presentation layer architecture to ensure consistent rendering patterns across all report item types while allowing flexibility in how each item type is visually represented.

## Args:
    None: This method takes no arguments beyond the implicit self parameter.

## Returns:
    Any: The return type varies based on the concrete implementation but typically produces HTML, JSON, or other structured formats representing the rendered table.

## Raises:
    NotImplementedError: Always raised by this base implementation to enforce that subclasses must provide their own rendering logic.

## State Changes:
    Attributes READ: 
    - self.item_type: Read to identify the item type (inherited from ItemRenderer)
    - self.content: Read to access table data including rows, name, caption, and style (inherited from ItemRenderer)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - This method should only be called on instances of concrete subclasses that have implemented the render method
    - The Table instance must have been properly initialized with valid content including rows, style, and other optional parameters
    Postconditions:
    - The method will raise NotImplementedError unless overridden by a subclass implementing the rendering logic

## Side Effects:
    None: This method does not perform any I/O operations or external service calls in its base implementation.

