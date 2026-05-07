# `duplicate.py`

## `src.ydata_profiling.report.presentation.core.duplicate.Duplicate` · *class*

## Summary:
Represents a UI component for displaying duplicate data findings in profiling reports.

## Description:
The Duplicate class is a specialized renderer that handles the presentation of duplicate data detected during data profiling. It extends ItemRenderer to provide a structured way to display duplicate records found in datasets. This class serves as a base for implementing specific duplicate visualization strategies while maintaining consistent interface expectations.

## State:
- item_type: str, set to "duplicate" during initialization, identifies the type of UI component
- content: dict, contains the duplicate data under the key "duplicate", plus optional metadata like name, anchor_id, and classes
- name: str, optional identifier for the component (inherited from parent)
- anchor_id: str, optional anchor identifier for linking (inherited from parent)
- classes: str, optional CSS classes for styling (inherited from parent)

## Lifecycle:
- Creation: Instantiate with a name string and a pandas DataFrame containing duplicate records
- Usage: Call render() method to generate visualization output (must be implemented by subclasses)
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[Duplicate.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set item_type="duplicate"]
    D --> E[Set content={"duplicate": duplicate}]
    E --> F[Set name, anchor_id, classes if provided]
    F --> G[Duplicate.__repr__]
    G --> H[Return "Duplicate"]
    H --> I[Duplicate.render]
    I --> J[NotImplementedError]
```

## Raises:
- NotImplementedError: Raised by render() method indicating that concrete implementations must override this method

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.core.duplicate import Duplicate

# Create duplicate data
duplicate_df = pd.DataFrame({'A': [1, 2, 2], 'B': [3, 4, 4]})

# Create Duplicate instance
duplicate_component = Duplicate(name="my_duplicates", duplicate=duplicate_df)

# String representation
print(repr(duplicate_component))  # Output: "Duplicate"

# Note: render() would raise NotImplementedError until subclassed
```

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.__init__` · *method*

## Summary:
Initializes a Duplicate renderer with duplicate data and metadata.

## Description:
This method sets up the Duplicate object by calling the parent ItemRenderer's constructor with the appropriate parameters. It configures the renderer to display duplicate data while maintaining proper metadata such as name, anchor ID, and CSS classes. This method ensures that the Duplicate component is properly initialized with the required "duplicate" content type and associated data.

## Args:
    name (str): Unique identifier for this duplicate renderer instance
    duplicate (pd.DataFrame): DataFrame containing duplicate records to be displayed
    **kwargs: Additional keyword arguments passed to the parent constructor, including optional name, anchor_id, and classes

## Returns:
    None: This method initializes the object state but does not return a value

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.content: Updated with duplicate data and metadata
    - self.item_type: Set to "duplicate"

## Constraints:
    Preconditions:
    - The duplicate parameter must be a valid pandas DataFrame
    - The name parameter must be a string
    - All kwargs must be valid arguments for the parent constructors

    Postconditions:
    - The object's content dictionary will contain a "duplicate" key with the provided DataFrame
    - The object's item_type attribute will be set to "duplicate"
    - The object's content dictionary will contain name, anchor_id, and classes if provided

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.__repr__` · *method*

## Summary:
Returns a string representation of the Duplicate object, identifying it as a Duplicate instance.

## Description:
This method provides a standardized string representation for Duplicate objects, primarily used for debugging and logging purposes. It is called automatically when the built-in repr() function is applied to a Duplicate instance, or when the object is displayed in interactive environments.

## Args:
    None

## Returns:
    str: Always returns the literal string "Duplicate" regardless of the object's internal state.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned string is always exactly "Duplicate"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.duplicate.Duplicate.render` · *method*

## Summary:
Abstract method that must be implemented to render duplicate data visualization content.

## Description:
This method serves as an abstract interface for rendering duplicate data findings in profiling reports. As part of the `ItemRenderer` hierarchy, it defines the contract for how duplicate data should be visually represented. The method is declared as abstract in the parent `Renderable` class and must be implemented by concrete subclasses to provide actual rendering functionality.

## Args:
    None

## Returns:
    Any: The rendered output representing duplicate data findings, typically HTML or other visualization formats.

## Raises:
    NotImplementedError: This method is not implemented in the base class and must be overridden by subclasses.

## State Changes:
    Attributes READ: 
    - self.content: Accesses the content dictionary containing duplicate data
    - self.item_type: Accesses the item type identifier
    - self.name: Accesses the name property from parent class
    - self.anchor_id: Accesses the anchor ID property from parent class
    - self.classes: Accesses the CSS classes property from parent class

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The `Duplicate` class must be properly initialized with valid duplicate data
    - The `content` dictionary must contain the required "duplicate" key with valid DataFrame data
    - This method should only be called on instances that have been properly constructed

    Postconditions:
    - When implemented, the method must return a valid rendering output representing duplicate data findings
    - The returned output should be compatible with the reporting framework's rendering pipeline

## Side Effects:
    None

