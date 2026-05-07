# `frequency_table.py`

## `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable` · *class*

## Summary:
FrequencyTable is a presentation layer component that represents a frequency table for data profiling reports, serving as a base class for specific rendering implementations.

## Description:
FrequencyTable is an abstract base class that defines the structure and interface for frequency table representations in data profiling reports. It inherits from ItemRenderer, which itself extends Renderable, establishing it as part of the presentation layer responsible for converting data analysis results into visual or textual formats. This class provides the foundational structure for frequency table rendering while deferring the actual rendering implementation to subclasses.

The class is designed to be instantiated with frequency data (rows) and a redaction flag, making it suitable for creating frequency tables that may need to hide sensitive information. It serves as a building block for various presentation formats like HTML, markdown, or other report formats.

## State:
- rows: list - A list containing frequency data rows to be displayed in the table
- redact: bool - A flag indicating whether sensitive information should be hidden/redacted in the rendered output
- item_type: str - Set to "frequency_table" by the constructor, identifying this as a frequency table item type
- content: dict - Dictionary containing the configuration and data for rendering, including rows and redact settings
- name: str (inherited property) - Optional name identifier for the frequency table
- anchor_id: str (inherited property) - Optional anchor identifier for linking within documents
- classes: str (inherited property) - Optional CSS classes for styling the rendered output

## Lifecycle:
- Creation: Instantiate with rows (list) and redact (bool) parameters, optionally providing name, anchor_id, and classes via keyword arguments
- Usage: The render() method must be implemented by subclasses to provide specific rendering logic for different output formats (HTML, markdown, etc.). Calling render() on the base class raises NotImplementedError.
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[FrequencyTable.__init__] --> B[FrequencyTable.render]
    B --> C[Subclass.render()]
    A --> D[ItemRenderer.__init__]
    D --> E[Renderable.__init__]
```

## Raises:
- TypeError: May be raised during initialization if incompatible types are passed for rows or redact parameters
- NotImplementedError: Raised when render() is called on the base class (must be implemented by subclasses)

## Example:
```python
# Creating a FrequencyTable instance
rows = [
    ["Category A", 100],
    ["Category B", 75],
    ["Category C", 50]
]
table = FrequencyTable(rows, redact=False)

# Note: render() must be called on a subclass implementation
# table.render()  # Would raise NotImplementedError in base class
```

### `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable.__init__` · *method*

## Summary:
Initializes a FrequencyTable object with rows and redaction settings, configuring it as a frequency table item renderer for report generation.

## Description:
This method serves as the constructor for FrequencyTable instances, establishing the foundational configuration for displaying frequency data in profiling reports. It inherits from ItemRenderer and sets up the necessary internal state for rendering frequency tables with optional data redaction capabilities. This method is typically called during the report generation pipeline when constructing presentation components.

## Args:
    rows (list): A list of row data to be displayed in the frequency table, typically containing categorical value counts
    redact (bool): Boolean flag indicating whether sensitive data should be redacted from display
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor for optional configuration

## Returns:
    None: This method initializes the object's internal state and does not return a value

## Raises:
    None: This method does not explicitly raise exceptions, though parent class initialization may raise exceptions for invalid arguments

## State Changes:
    Attributes READ: None
    Attributes WRITTEN:
    - self.item_type: Set to "frequency_table" string identifier
    - self.content: Set to dictionary containing "rows" and "redact" keys with provided values
    - Other attributes inherited from Renderable parent class (content, name, anchor_id, classes)

## Constraints:
    Preconditions:
    - rows parameter must be a valid list-like object containing frequency data
    - redact parameter must be a boolean value (True or False)
    - All kwargs must be valid arguments accepted by the parent ItemRenderer class
    
    Postconditions:
    - The object is properly initialized as a frequency table item renderer
    - The item_type attribute is set to "frequency_table"
    - The content dictionary contains the provided rows and redact settings
    - The object is ready for rendering in report generation pipelines

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside self

### `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable.__repr__` · *method*

## Summary:
Returns a string representation of the FrequencyTable object that identifies its type.

## Description:
This method provides a standardized string representation for FrequencyTable instances, enabling easy identification of the object type during debugging or logging operations. It is part of the presentation layer's rendering system and inherits from ItemRenderer base class.

## Args:
    None

## Returns:
    str: Always returns the literal string "FrequencyTable" regardless of the object's internal state.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned string is always exactly "FrequencyTable"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable.render` · *method*

## Summary:
Abstract method that generates a rendered representation of a frequency table for data profiling reports.

## Description:
This abstract method defines the interface for rendering frequency tables in data profiling reports. It is part of the presentation layer that converts data analysis results into visual or textual representations. The method must be implemented by subclasses to provide specific rendering logic for different output formats (HTML, markdown, etc.).

## Args:
    None

## Returns:
    Any: The rendered representation of the frequency table, which varies by implementation (HTML string, markdown, etc.)

## Raises:
    NotImplementedError: This abstract method is not implemented in the base class and must be overridden by subclasses.

## State Changes:
    Attributes READ: 
    - self.content (inherited from Renderable base class)
    - self.name (property from Renderable base class)
    - self.anchor_id (property from Renderable base class)
    - self.classes (property from Renderable base class)
    - self.item_type (from ItemRenderer parent class)

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The FrequencyTable instance must be properly initialized with valid rows and redact parameters
    - The render method must be called on a properly constructed FrequencyTable object
    
    Postconditions:
    - Calling render raises NotImplementedError in the base class
    - Subclasses must implement this method to return a valid representation
    - The returned representation should be appropriate for the target presentation format

## Side Effects:
    None

