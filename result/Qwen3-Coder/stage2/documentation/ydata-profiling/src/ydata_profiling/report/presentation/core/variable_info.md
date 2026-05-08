# `variable_info.py`

## `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo` · *class*

## Summary:
Represents variable information for display in data profiling report presentations, serving as a container for variable metadata and alerts.

## Description:
The VariableInfo class is a specialized renderer for displaying variable-specific information within data profiling reports. It inherits from ItemRenderer and provides a standardized structure for organizing variable metadata including name, type, description, alerts, and styling information. This class acts as a data container that facilitates consistent presentation of variable-level information across different report sections.

The class is intended to be subclassed rather than used directly, as it implements the abstract render() method that must be overridden by concrete implementations to generate the actual visual representation.

## State:
- anchor_id (str): Unique identifier for HTML anchors referencing this variable
- var_name (str): Human-readable name of the variable being described
- var_type (str): Data type classification of the variable (e.g., 'Numeric', 'Categorical')
- alerts (List[Alert]): Collection of alert objects indicating issues or notable characteristics of the variable
- description (str): Detailed description or explanation of the variable's purpose or characteristics
- style (Style): Styling configuration object that controls the visual presentation of the variable information

## Lifecycle:
- Creation: Instantiate with required parameters anchor_id, var_name, var_type, alerts, description, and style
- Usage: Typically used as part of a report generation pipeline where subclasses implement the render() method to produce HTML or other formatted output
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[VariableInfo] --> B[ItemRenderer]
    B --> C[Renderable]
    C --> D{render()}
    D --> E[NotImplementedError]
```

## Raises:
- TypeError: If required arguments are missing or incorrectly typed during initialization
- NotImplementedError: When render() method is called without being overridden by a subclass

## Example:
```python
# Creating a VariableInfo instance (typically done through subclasses)
from ydata_profiling.config import Style
from ydata_profiling.model.alerts import Alert

# Create sample data
alerts = [Alert("Missing values detected", "warning")]
style = Style(primary_colors=["#377eb8"])

# Create variable info instance
variable_info = VariableInfo(
    anchor_id="var_123",
    var_name="age",
    var_type="Numeric",
    alerts=alerts,
    description="Age of participants in years",
    style=style
)

# Note: render() would raise NotImplementedError unless subclassed
```

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.__init__` · *method*

## Summary:
Initializes a VariableInfo object with metadata about a variable for report presentation.

## Description:
Constructs a VariableInfo instance that encapsulates information about a variable for display in profiling reports. This method sets up the internal state with variable metadata including name, type, alerts, description, and styling information. The method delegates to the parent ItemRenderer class to establish the proper rendering framework, which in turn inherits from Renderable to provide common presentation capabilities.

## Args:
    anchor_id (str): Unique identifier for HTML anchor linking
    var_name (str): Name of the variable being described
    var_type (str): Data type of the variable (e.g., 'numeric', 'categorical')
    alerts (List[Alert]): List of alert objects associated with this variable
    description (str): Detailed description of the variable's characteristics
    style (Style): Styling configuration for report presentation
    **kwargs: Additional keyword arguments passed to parent constructor for extra metadata

## Returns:
    None: This method initializes the object state and returns nothing

## Raises:
    TypeError: If required arguments are missing or incorrectly typed during initialization

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "variable_info" to identify this item type
    - self.content: Dictionary containing all variable metadata (anchor_id, var_name, description, var_type, alerts, style)

## Constraints:
    Preconditions:
    - anchor_id must be a valid string identifier
    - var_name must be a valid string representing the variable name
    - var_type must be a valid string indicating the data type
    - alerts must be a list of Alert objects
    - description must be a valid string
    - style must be a valid Style configuration object
    
    Postconditions:
    - self.item_type is set to "variable_info"
    - self.content contains all provided parameters in a structured dictionary format
    - The object inherits standard Renderable properties (name, anchor_id, classes) through the parent class hierarchy

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.__repr__` · *method*

## Summary:
Returns a string representation of the VariableInfo object for debugging and development purposes.

## Description:
This method provides a standardized string representation of VariableInfo instances, returning the literal string "VariableInfo". It is automatically invoked when the built-in `repr()` function is called on a VariableInfo instance or when the object is displayed in interactive Python sessions. This implementation follows Python conventions for `__repr__` methods by providing a clear identification of the object type.

## Args:
    None

## Returns:
    str: The string "VariableInfo" identifying the object type.

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

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.render` · *method*

## Summary:
Raises NotImplementedError as this method must be implemented by subclasses to render variable information in report presentations.

## Description:
This method serves as an abstract interface for rendering variable information within the ydata profiling report presentation layer. It is part of the VariableInfo class hierarchy that specializes in presenting detailed metadata about individual variables in a dataset. The method is intentionally left unimplemented in the base class and must be overridden by concrete subclasses to provide specific rendering logic for variable information.

The render() method is called during the report generation process when variable information needs to be converted into a presentation-ready format (such as HTML, markdown, or other output formats).

## Args:
    None

## Returns:
    Any: This method raises NotImplementedError and should be overridden by subclasses to return a rendered representation of variable information.

## Raises:
    NotImplementedError: Always raised by this base implementation to indicate that subclasses must implement this method.

## State Changes:
    Attributes READ: 
    - self.item_type: str - The type identifier for this item renderer ("variable_info")
    - self.content: dict - Dictionary containing variable metadata including anchor_id, var_name, description, var_type, alerts, and style
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The VariableInfo instance must be properly initialized with required parameters
    - The content dictionary must contain all expected keys (anchor_id, var_name, description, var_type, alerts, style)
    
    Postconditions: 
    - This method always raises NotImplementedError in the base implementation
    - Subclasses must ensure their implementation returns a valid rendered representation

## Side Effects:
    None

