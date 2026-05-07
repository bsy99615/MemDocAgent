# `table.py`

## `src.ydata_profiling.report.presentation.core.table.Table` · *class*

## Summary:
Abstract base class for table item renderers in data profiling reports that encapsulates tabular data for presentation.

## Description:
The Table class serves as an abstract base class for rendering tabular data within data profiling reports. It provides a standardized interface for handling structured data in table format, ensuring consistent presentation across different report generation contexts. As an extension of ItemRenderer, it establishes a contract for table-based content rendering while inheriting common rendering capabilities.

This abstract class defines the structure and interface for table renderers, requiring subclasses to implement the render() method to produce the actual formatted output. It's designed to be extended by concrete implementations that handle specific rendering formats (HTML, JSON, etc.).

## State:
- rows: Sequence - A sequence of data rows that constitute the table content. Each row can be a list, tuple, or other sequence-like structure containing the data elements for that row.
- style: Style - A configuration object that defines the visual styling parameters for the table, including colors, themes, and branding elements.
- name: Optional[str] - An optional human-readable identifier for the table that can be used for labeling or referencing purposes.
- caption: Optional[str] - An optional caption that provides context or description for the table content.

## Lifecycle:
- Creation: Instantiate with required rows and style parameters, optionally providing name and caption. The constructor calls the parent ItemRenderer.__init__ with item_type="table" and the provided content dictionary.
- Usage: Intended to be subclassed by concrete implementations that provide actual rendering logic. The render() method must be implemented by subclasses to produce the formatted output.
- Destruction: Managed automatically by Python's garbage collection; no explicit cleanup required.

## Method Map:
```mermaid
graph TD
    A[Table.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    A --> D[Table.render()]
    D --> E[Subclass Implementation]
```

## Raises:
- TypeError: If required arguments are missing or incorrectly typed during initialization (inherited from ItemRenderer)
- NotImplementedError: When render() method is called without being overridden by a subclass

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.report.presentation.core.table import Table

# Create a table with sample data
rows = [
    ["Feature", "Type", "Count"],
    ["age", "int", 1000],
    ["income", "float", 1000]
]

style = Style(primary_colors=["#377eb8", "#e41a1c"])

# Create table instance (this is an abstract base class)
table = Table(
    rows=rows,
    style=style,
    name="demographics_table",
    caption="Demographic statistics"
)

# Concrete implementation would be needed for actual rendering
# table.render()  # Would raise NotImplementedError in this base class
```

### `src.ydata_profiling.report.presentation.core.table.Table.__init__` · *method*

## Summary:
Initializes a table item renderer with rows, styling configuration, and optional metadata.

## Description:
Configures a table item renderer by setting up its content dictionary with rows, style, name, and caption parameters. This method establishes the foundational structure for table-based report elements in the ydata profiling presentation layer, ensuring proper inheritance from the ItemRenderer base class.

The method is designed as a dedicated constructor to encapsulate the initialization logic for table items, separating concerns from other potential initialization code and ensuring consistent setup of table-specific properties.

## Args:
- rows (Sequence): Collection of table rows to be rendered, typically containing data cells
- style (Style): Styling configuration object that defines visual properties for the table
- name (Optional[str]): Human-readable identifier for the table, defaults to None
- caption (Optional[str]): Optional descriptive caption for the table, defaults to None
- **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor

## Returns:
None: This method initializes the object's state and does not return a value

## Raises:
- TypeError: If required arguments are missing or incorrectly typed during initialization
- NotImplementedError: If the parent ItemRenderer's __init__ raises this exception (though unlikely in normal usage)

## State Changes:
- Attributes READ: None
- Attributes WRITTEN: 
  - self.item_type: Set to "table" by the parent class
  - self.content: Dictionary containing "rows", "name", "caption", and "style" keys
  - self.name: Set from the name parameter (inherited from parent)
  - self.anchor_id: Set from kwargs or inherited from parent (inherited from parent)
  - self.classes: Set from kwargs or inherited from parent (inherited from parent)

## Constraints:
- Preconditions: 
  - rows parameter must be a sequence-like object
  - style parameter must be a valid Style instance
  - All parameters must be properly typed according to their annotations
- Postconditions:
  - The object is initialized with item_type="table"
  - Content dictionary contains all specified parameters
  - Parent class initialization completes successfully

## Side Effects:
None: This method performs no I/O operations, external service calls, or mutations to objects outside self

### `src.ydata_profiling.report.presentation.core.table.Table.__repr__` · *method*

## Summary:
Returns a string representation of the Table object for debugging purposes.

## Description:
Provides a simple string representation of the Table instance, returning "Table" to indicate the object type. This method is part of Python's standard object protocol and is primarily used for debugging and development to quickly identify the type of object being examined.

## Args:
    None: This method takes no arguments beyond the implicit self parameter.

## Returns:
    str: Always returns the literal string "Table".

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Table"

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.ydata_profiling.report.presentation.core.table.Table.render` · *method*

## Summary:
Abstract method that must be implemented by subclasses to generate a rendered representation of tabular data.

## Description:
This method serves as the abstract interface for rendering table data in different presentation formats. As an abstract method inherited from ItemRenderer, it must be overridden by concrete subclasses to provide specific rendering logic for tables. The method is part of the report presentation layer's rendering pipeline and is responsible for converting table data into a displayable format.

The Table class is designed to be extended by concrete implementations that handle specific rendering targets such as HTML, Markdown, or other presentation formats. Each subclass implements this method to produce appropriate output based on the target format.

## Args:
    None

## Returns:
    Any: The rendered representation of the table data, typically in the format appropriate for the concrete implementation (HTML string, dictionary, or other format-specific representation).

## Raises:
    NotImplementedError: Always raised by this base implementation, indicating that subclasses must override this method with their specific rendering logic.

## State Changes:
    Attributes READ: 
    - self.item_type: Read to identify the item type (inherited from ItemRenderer)
    - self.content: Read to access table data including rows, name, caption, and style (inherited from ItemRenderer)
    
    Attributes WRITTEN: 
    - None

## Constraints:
    Preconditions:
    - This method should only be called on concrete subclasses that have implemented the render logic
    - The Table instance must be properly initialized with required content including rows and style
    
    Postconditions:
    - Calling this method on a concrete subclass will return a valid rendered representation of the table data
    - The returned value should be appropriate for the target presentation format

## Side Effects:
    None

