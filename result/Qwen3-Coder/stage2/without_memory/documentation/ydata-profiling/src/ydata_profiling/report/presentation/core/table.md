# `table.py`

## `src.ydata_profiling.report.presentation.core.table.Table` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.table.Table.__init__` · *method*

## Summary:
Initializes a table presentation component with rows, styling, and optional metadata.

## Description:
Constructs a table item renderer that encapsulates tabular data for report generation. This method sets up the internal content structure with rows, styling information, and optional identifying metadata such as name and caption.

## Args:
    rows (Sequence): The tabular data to display, typically a sequence of sequences or dictionaries representing rows and columns.
    style (Style): Configuration object containing styling parameters for the table presentation.
    name (Optional[str]): Unique identifier for the table, defaults to None.
    caption (Optional[str]): Optional descriptive caption for the table, defaults to None.
    **kwargs: Additional keyword arguments passed to the parent initializer.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "table"
    - self.content: Populated with rows, name, caption, and style information

## Constraints:
    Preconditions:
    - rows should be a sequence-like object that can be processed for tabular display
    - style should be a properly initialized Style configuration object
    - All arguments except name and caption should be provided

    Postconditions:
    - The instance is properly initialized as a table-type renderable component
    - self.content contains all provided data in a structured format

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.ydata_profiling.report.presentation.core.table.Table.__repr__` · *method*

## Summary:
Returns a string representation identifying the object as a Table instance.

## Description:
This method provides a standard string representation for Table objects, returning the literal string "Table". It is called when the built-in repr() function is used on a Table instance or when the object is displayed in interactive environments.

## Args:
    None

## Returns:
    str: The string "Table" that identifies this object as a Table instance.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Table"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.table.Table.render` · *method*

## Summary:
Renders the table component into a formatted representation using the stored data and styling configuration.

## Description:
This method implements the abstract render interface required by the Renderable base class. It converts the table's row data, caption, and styling information into a rendered output format. The Table class stores its data in a content dictionary containing rows, name, caption, and style configuration, which this method processes to generate the appropriate representation. This is a placeholder implementation that raises NotImplementedError and must be overridden by concrete subclasses to provide actual rendering functionality.

## Args:
    None - This is an instance method that operates on the object's stored state

## Returns:
    Any - The rendered representation of the table, typically HTML or a formatted string, though the exact return type depends on the implementing subclass

## Raises:
    NotImplementedError - This base implementation raises NotImplementedError and must be overridden by subclasses to provide actual rendering functionality

## State Changes:
    Attributes READ: 
    - self.content (accessed via parent classes)
    - self.content["rows"] 
    - self.content["caption"]
    - self.content["style"]
    - self.item_type

## Constraints:
    Preconditions:
    - The Table instance must have been properly initialized with valid rows and style parameters
    - The content dictionary must contain the required keys: "rows", "name", "caption", "style"
    - The style parameter must be a valid Style instance

    Postconditions:
    - The method must return a valid rendered representation of the table data
    - The returned value should be compatible with the presentation layer's rendering system

## Side Effects:
    None - This method does not perform any I/O operations or mutate external state

