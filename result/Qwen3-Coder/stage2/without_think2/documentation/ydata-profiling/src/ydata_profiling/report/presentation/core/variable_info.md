# `variable_info.py`

## `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo` · *class*

## Summary:
Represents metadata and alert information for a variable in a profiling report.

## Description:
The VariableInfo class is a specialized renderer that encapsulates metadata and alert information for a specific variable within a dataset profiling report. It inherits from ItemRenderer and provides a standardized structure for storing variable details such as name, type, description, and associated alerts. This class serves as a data container for variable-specific information that will be rendered in the final report.

## State:
- anchor_id: str - Unique identifier for HTML anchor points in the rendered report
- var_name: str - Human-readable name of the variable
- var_type: str - Data type classification of the variable (e.g., 'Numeric', 'Categorical')
- alerts: List[Alert] - Collection of data quality alerts associated with this variable
- description: str - Detailed description or explanation of the variable
- style: Style - Styling configuration for report appearance

## Lifecycle:
- Creation: Instantiate with required parameters including anchor_id, var_name, var_type, alerts, description, and style
- Usage: Used as part of report generation pipeline where subclasses implement the render() method
- Destruction: Managed by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[VariableInfo.__init__] --> B[ItemRenderer.__init__]
    B --> C[content populated with variable info]
    C --> D[VariableInfo.__repr__]
    D --> E[render() method - Not implemented]
```

## Raises:
- No explicit exceptions raised during __init__ as it delegates to parent constructor
- render() method raises NotImplementedError to enforce implementation in subclasses

## Example:
```python
from ydata_profiling.config import Style
from ydata_profiling.model.alerts import Alert, AlertType

# Create sample alerts
alert1 = Alert(AlertType.HIGH_CORRELATION, column_name="var1")
alerts = [alert1]

# Create style configuration
style = Style(primary_colors=["#377eb8"])

# Create variable info instance
variable_info = VariableInfo(
    anchor_id="var1-anchor",
    var_name="Variable 1",
    var_type="Numeric",
    alerts=alerts,
    description="This is a sample numeric variable",
    style=style
)

# The instance can be used in report generation pipeline
# Note: render() must be implemented by concrete subclasses
```

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.__init__` · *method*

## Summary:
Initializes a VariableInfo object with metadata for variable information display in reports.

## Description:
This method sets up the VariableInfo instance by calling the parent ItemRenderer's constructor with the appropriate configuration. It establishes the item type as "variable_info" and stores key variable metadata including anchor ID, variable name, type, alerts, description, and styling information in the content dictionary. This method is part of the VariableInfo class that renders variable-specific information in profiling reports.

## Args:
    anchor_id (str): Unique identifier for HTML anchor linking
    var_name (str): Name of the variable being described
    var_type (str): Data type of the variable (e.g., 'numeric', 'categorical')
    alerts (List[Alert]): List of alert objects associated with this variable
    description (str): Detailed description of the variable's characteristics
    style (Style): Styling configuration for report presentation
    **kwargs: Additional keyword arguments passed to parent ItemRenderer constructor

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    No explicit exceptions defined in this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "variable_info"
    - self.content: Populated with anchor_id, var_name, description, var_type, alerts, and style

## Constraints:
    Preconditions:
    - anchor_id must be a string
    - var_name must be a string
    - var_type must be a string
    - alerts must be a list of Alert objects
    - description must be a string
    - style must be a Style object
    
    Postconditions:
    - self.item_type is set to "variable_info"
    - self.content contains all provided parameters in a dictionary format

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.variable_info.VariableInfo.__repr__` · *method*

## Summary:
Returns a string representation of the VariableInfo object indicating its class name.

## Description:
The `__repr__` method provides a standardized string representation for VariableInfo instances, returning the literal string "VariableInfo". This method is part of the standard Python object protocol and is typically used for debugging and development purposes to quickly identify object types.

## Args:
    None

## Returns:
    str: The string "VariableInfo" regardless of the object's internal state.

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
Raises NotImplementedError as this is an abstract method requiring implementation by subclasses.

## Description:
This method is declared as abstract in the VariableInfo class and raises NotImplementedError to enforce that concrete implementations must override this method. The VariableInfo class inherits from ItemRenderer, which defines the render() interface, but provides no concrete implementation for variable information rendering.

## Args:
    None

## Returns:
    Any: This method never returns normally due to the NotImplementedError exception

## Raises:
    NotImplementedError: Always raised when this method is called on VariableInfo instances

## State Changes:
    Attributes READ: 
    - self.item_type (inherited from ItemRenderer)
    - self.content (inherited from ItemRenderer)
    - self.name (inherited from ItemRenderer)
    - self.anchor_id (inherited from ItemRenderer)
    - self.classes (inherited from ItemRenderer)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - This method should only be called on concrete subclasses that properly implement render()
    - The VariableInfo instance must be properly initialized with required parameters
    
    Postconditions:
    - The method always raises NotImplementedError when called on VariableInfo directly
    - No state changes occur in the instance

## Side Effects:
    None

