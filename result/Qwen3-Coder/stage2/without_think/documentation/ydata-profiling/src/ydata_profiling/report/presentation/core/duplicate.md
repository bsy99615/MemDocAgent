# `duplicate.py`

## `src.ydata_profiling.report.presentation.core.duplicate.Duplicate` · *class*

## Summary:
Represents a duplicate data report in a data profiling presentation layer.

## Description:
The Duplicate class is a specialized renderer for displaying duplicate data findings in data profiling reports. It inherits from ItemRenderer and is designed to handle data structures containing duplicate records. This class serves as a base for implementing specific duplicate reporting functionality in data profiling tools.

## State:
- `name` (str): The name identifier for this duplicate report instance
- `duplicate` (pandas.DataFrame): A pandas DataFrame containing the duplicate data records to be displayed
- `item_type` (str): Set to "duplicate" by the constructor, identifying this as a duplicate report type
- `content` (dict): Dictionary containing the duplicate DataFrame under the key "duplicate"

## Lifecycle:
- Creation: Instantiate with a name string and a pandas DataFrame containing duplicate data
- Usage: Typically used within data profiling report generation workflows where duplicate detection results need to be rendered
- Destruction: No explicit cleanup required; relies on parent class lifecycle management

## Method Map:
```mermaid
graph TD
    A[Duplicate.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    A --> D[Sets item_type="duplicate"]
    D --> E[Stores duplicate data in content dict]
    F[Duplicate.render] --> G[NotImplementedError]
```

## Raises:
- `NotImplementedError`: Raised when the render() method is called, as this class is intended to be subclassed for actual rendering implementations

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.core.duplicate import Duplicate

# Create a duplicate report with sample data
duplicate_df = pd.DataFrame({'id': [1, 2, 3], 'value': ['a', 'b', 'c']})
duplicate_report = Duplicate(name="my_duplicates", duplicate=duplicate_df)

# Note: render() method raises NotImplementedError and needs to be implemented in subclasses
print(duplicate_report)  # Output: Duplicate
```

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.__init__` · *method*

## Summary:
Initializes a Duplicate instance with duplicate data and configuration parameters.

## Description:
Constructs a Duplicate object that represents duplicate data findings in data profiling reports. This method sets up the internal state by calling the parent class constructors and storing the duplicate data in the content dictionary.

## Args:
    name (str): Unique identifier for this duplicate report instance
    duplicate (pd.DataFrame): Pandas DataFrame containing the duplicate records to be displayed
    **kwargs: Additional keyword arguments passed to parent constructors

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    None: This method does not explicitly raise exceptions, though parent constructors may raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "duplicate"
    - self.content: Dictionary containing the duplicate DataFrame under the key "duplicate"

## Constraints:
    Preconditions:
    - The `name` parameter must be a string
    - The `duplicate` parameter must be a valid pandas DataFrame
    - The `duplicate` DataFrame should contain the duplicate records to be reported

    Postconditions:
    - The object's item_type attribute is set to "duplicate"
    - The duplicate DataFrame is stored in the content dictionary under the "duplicate" key
    - All parent class initialization is completed successfully

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.__repr__` · *method*

## Summary:
Returns a string representation of the Duplicate object indicating its type.

## Description:
This method provides a standardized string representation for Duplicate objects, returning the literal string "Duplicate". It is called by Python's built-in repr() function and is useful for debugging and logging purposes. This method overrides the default object representation to provide a clear indication of the object's type.

## Args:
    None

## Returns:
    str: The string "Duplicate" indicating the object type.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Duplicate"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.render` · *method*

## Summary:
Renders the duplicate data information into a displayable format for report generation.

## Description:
This method implements the abstract render interface required by the Renderable base class. It transforms the duplicate data stored in the object's content into a format suitable for presentation in reports. The method is intended to be overridden by subclasses to provide specific rendering logic for duplicate data visualization.

## Args:
    None

## Returns:
    Any: The rendered representation of duplicate data, typically a string, HTML fragment, or other presentation-ready format.

## Raises:
    NotImplementedError: This method is not implemented in the base Duplicate class and must be overridden by subclasses.

## State Changes:
    Attributes READ: 
    - self.content: The dictionary containing duplicate data information
    - self.item_type: The type identifier for this item renderer
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Duplicate instance must be properly initialized with content
    - The content dictionary should contain relevant duplicate data information
    
    Postconditions:
    - The returned value should be a valid presentation format for report generation

## Side Effects:
    None

