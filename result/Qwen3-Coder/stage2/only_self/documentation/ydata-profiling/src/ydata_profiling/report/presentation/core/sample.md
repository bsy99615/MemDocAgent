# `sample.py`

## `src.ydata_profiling.report.presentation.core.sample.Sample` · *class*

## Summary:
Concrete implementation of ItemRenderer for displaying data samples in profiling reports.

## Description:
The Sample class represents a data sample component in the ydata profiling report presentation layer. It inherits from ItemRenderer and is specifically designed to encapsulate and render data samples from pandas DataFrames within profiling reports. This class serves as a specialized container for sample data that can be rendered in various report formats.

The class is intended to be used by report generators that need to display sample data from datasets being profiled. It follows the standard ItemRenderer pattern where the actual rendering logic is left to subclasses that implement the abstract render() method.

## State:
- name: str - Human-readable identifier for the sample item
- sample: pd.DataFrame - The actual data sample to be displayed, stored in the content dictionary
- caption: Optional[str] - Optional descriptive caption for the sample, stored in the content dictionary
- item_type: str - Fixed value "sample" identifying this item type, inherited from parent class
- content: dict - Dictionary containing the sample data and caption, inherited from parent class

## Lifecycle:
- Creation: Instantiate with a name string, pandas DataFrame sample, optional caption, and additional keyword arguments
- Usage: Typically used as part of a report generation pipeline where render() method would be called to produce the formatted output
- Destruction: Inherits standard Python object lifecycle management; no special cleanup required

## Method Map:
```mermaid
graph TD
    A[Sample.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    A --> D[Sets item_type="sample"]
    A --> E[Stores sample and caption in content]
    F[Sample.render()] --> G[NotImplementedError]
```

## Raises:
- NotImplementedError: Raised by the render() method which must be implemented by subclasses

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.core.sample import Sample

# Create a sample data frame
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create a Sample instance
sample_item = Sample(name="First_100_rows", sample=sample_data, caption="Sample of dataset")

# The render method would be implemented by subclasses
# result = sample_item.render()  # Would raise NotImplementedError
```

### `src.ydata_profiling.report.presentation.core.sample.Sample.__init__` · *method*

## Summary:
Initializes a Sample instance with a data frame sample and optional caption for report presentation.

## Description:
Configures a Sample object for report presentation by setting up the item type identifier as "sample" and storing the data sample and optional caption in the content dictionary. This constructor prepares the object for rendering within the ydata profiling report system by establishing its identity and data payload.

The method delegates to the parent ItemRenderer.__init__ method which handles the standard initialization of item type and content management, ensuring consistency with other report components in the presentation layer.

## Args:
    name (str): Human-readable identifier for the sample item
    sample (pd.DataFrame): The actual data sample to be displayed in the report
    caption (Optional[str]): Optional descriptive caption for the sample, defaults to None

## Returns:
    None: This method initializes the object state and returns nothing

## Raises:
    None: This method does not explicitly raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "sample" by parent class
    - self.content: Dictionary containing "sample" and "caption" keys

## Constraints:
    Preconditions:
    - name must be a string
    - sample must be a pandas DataFrame
    - caption must be either None or a string
    
    Postconditions:
    - The object is properly initialized with item_type="sample"
    - The sample data and caption are stored in the content dictionary
    - The object inherits all standard ItemRenderer functionality

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.sample.Sample.__repr__` · *method*

## Summary:
Returns a string representation of the Sample object for debugging and identification purposes.

## Description:
The `__repr__` method provides a simple string representation of Sample instances, returning the literal string "Sample". This implementation is typically used for debugging and development purposes to quickly identify Sample objects in console output or logs. The method is part of the standard Python object protocol and is called by repr() built-in function and when displaying objects in interactive environments.

## Args:
    None

## Returns:
    str: Always returns the string "Sample"

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the string "Sample"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.sample.Sample.render` · *method*

## Summary:
Abstract rendering method that raises NotImplementedError, requiring subclasses to implement sample-specific rendering logic for report presentation.

## Description:
This method implements the abstract render() interface required by the ItemRenderer base class. As a concrete implementation of ItemRenderer, the Sample class inherits this method signature but does not provide a concrete implementation, making it a placeholder that must be overridden by subclasses to define how sample data should be rendered for presentation in profiling reports.

The render method is invoked during the report generation pipeline when the system processes sample items in the presentation layer. It serves as the interface contract that ensures all ItemRenderer subclasses provide their own rendering implementation.

Known callers:
- Called by the report generation framework during the rendering phase when processing sample items
- Invoked by the presentation layer when building report sections that include sample data
- Part of the standard ItemRenderer interface contract that all concrete renderers must implement

This method exists as a separate implementation rather than being inlined because:
1. It follows the established abstract base class pattern from ItemRenderer
2. It allows for flexible rendering strategies tailored to different sample presentation needs
3. It maintains consistency with other ItemRenderer subclasses that implement their own rendering logic
4. It separates the interface definition from the concrete implementation

## Args:
    None

## Returns:
    Any: This method intentionally raises NotImplementedError and never returns a value

## Raises:
    NotImplementedError: Always raised when this method is called, indicating that subclasses must implement this method with specific rendering logic for data samples

## State Changes:
    Attributes READ: 
    - self.item_type: String identifier indicating this is a "sample" type item (inherited from ItemRenderer)
    - self.content: Dictionary containing the sample data under the "sample" key and optional caption under "caption" key (inherited from ItemRenderer)
    - self.name: Optional human-readable identifier for the sample item (inherited from ItemRenderer)
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The Sample instance must be properly initialized with valid data
    - The content dictionary must contain the required "sample" key with DataFrame data
    - The content dictionary may optionally contain a "caption" key with descriptive text
    
    Postconditions: 
    - This method never completes execution successfully
    - The method always raises NotImplementedError to indicate missing implementation

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state

