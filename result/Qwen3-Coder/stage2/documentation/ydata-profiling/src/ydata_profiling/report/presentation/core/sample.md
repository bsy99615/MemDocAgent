# `sample.py`

## `src.ydata_profiling.report.presentation.core.sample.Sample` · *class*

## Summary:
Represents a data sample item for report presentation, containing a pandas DataFrame sample and optional caption.

## Description:
The Sample class is a specialized item renderer designed to display data samples within report presentations. It inherits from ItemRenderer and provides a standardized way to encapsulate and render sample data, typically used to show representative rows from a dataset in profiling reports. This class serves as an abstract base class that must be subclassed to provide concrete rendering implementations.

## State:
- name: str - Human-readable identifier for the sample item
- sample: pd.DataFrame - The actual data sample to be displayed, stored in content["sample"]
- caption: Optional[str] - Optional descriptive text for the sample, stored in content["caption"] 
- item_type: str - Fixed value "sample" identifying this item type
- content: dict - Dictionary containing the sample data and caption under keys "sample" and "caption"
- anchor_id: Optional[str] - Unique identifier for HTML anchors (inherited from ItemRenderer)
- classes: Optional[str] - CSS classes for styling (inherited from ItemRenderer)

## Lifecycle:
- Creation: Instantiate with name (str), sample (pd.DataFrame), and optional caption (str)
- Usage: Subclasses must implement the render() method to generate the rendered representation
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Sample.__init__] --> B[ItemRenderer.__init__]
    B --> C[Renderable.__init__]
    C --> D[Sample.render()]
    D --> E{NotImplementedError}
```

## Raises:
- NotImplementedError: When render() method is called directly on Sample instance, as this is an abstract method requiring implementation in subclasses

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.core.sample import Sample

# Create a sample DataFrame
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
sample_item = Sample(name="first_sample", sample=sample_data, caption="First 3 rows")

# Note: render() method raises NotImplementedError and must be implemented
# in a subclass for actual usage
```

### `src.ydata_profiling.report.presentation.core.sample.Sample.__init__` · *method*

## Summary:
Initializes a sample item renderer with data and optional caption for report presentation.

## Description:
Constructs a Sample object that encapsulates a pandas DataFrame sample along with an optional caption for display in profiling report presentations. This method sets up the internal state by calling the parent ItemRenderer's constructor with the appropriate parameters to establish the item type, content dictionary, and name.

The Sample class is designed to be an abstract base class for rendering data samples in reports, requiring subclasses to implement the render() method for actual presentation logic.

## Args:
    name (str): Human-readable identifier for the sample item
    sample (pd.DataFrame): The actual data sample to be displayed in the report
    caption (Optional[str]): Optional descriptive text for the sample, defaults to None
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor (such as anchor_id, classes)

## Returns:
    None: This method initializes the object's state and does not return a value

## Raises:
    TypeError: If required arguments are missing or incorrectly typed during initialization
    NotImplementedError: If render() method is called directly on Sample instance (as it's abstract)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "sample" to identify this item type
    - self.content: Dictionary containing "sample" and "caption" keys with respective values
    - self.name: Set to the provided name parameter
    - self.anchor_id: Inherited from ItemRenderer if provided in kwargs
    - self.classes: Inherited from ItemRenderer if provided in kwargs

## Constraints:
    Preconditions:
    - name must be a string
    - sample must be a pandas DataFrame
    - caption must be a string or None
    - All kwargs must be valid parameters for ItemRenderer initialization
    
    Postconditions:
    - self.item_type is set to "sample"
    - self.content contains the sample DataFrame and caption in a dictionary with keys "sample" and "caption"
    - self.name is properly assigned

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object state.

### `src.ydata_profiling.report.presentation.core.sample.Sample.__repr__` · *method*

## Summary:
Returns a string representation of the Sample object, consistently identifying it as "Sample".

## Description:
The `__repr__` method provides a standardized string representation for Sample objects in the report presentation layer. This implementation returns the literal string "Sample" regardless of the object's internal state, serving as a simple identification mechanism for debugging and logging purposes.

This method is part of the presentation layer's rendering infrastructure and follows the standard Python convention for `__repr__` methods. It's called during debugging sessions, interactive Python sessions, or when objects need to be displayed in a human-readable form.

## Args:
    None

## Returns:
    str: Always returns the string "Sample" as a fixed identifier for the class type.

## Raises:
    None

## State Changes:
    Attributes READ: None - This method does not access any instance attributes.
    Attributes WRITTEN: None - This method does not modify any instance attributes.

## Constraints:
    Preconditions: None - No specific conditions must be met before calling.
    Postconditions: The returned string is always exactly "Sample" with no variation based on object state.

## Side Effects:
    None - This method performs no I/O operations, external service calls, or mutations to external objects.

### `src.ydata_profiling.report.presentation.core.sample.Sample.render` · *method*

## Summary:
Enforces implementation requirement for rendering sample data items in report presentations.

## Description:
This method serves as an abstract interface definition that must be implemented by subclasses of Sample. It raises NotImplementedError to prevent direct usage of the base Sample class and enforces that concrete implementations provide rendering logic for sample data within the ydata-profiling report presentation layer.

During report generation, this method is invoked by the presentation layer infrastructure when processing sample data items. It forms part of the standard ItemRenderer interface that ensures all sample renderers provide their own specific rendering behavior for different output formats (HTML, JSON, etc.).

The method exists purely as a contract enforcement mechanism rather than providing executable functionality. Concrete subclasses must override this method to define how sample data should be rendered.

## Args:
    None

## Returns:
    Any: This method never returns normally due to the NotImplementedError being raised

## Raises:
    NotImplementedError: Always raised to indicate that subclasses must implement this method

## State Changes:
    Attributes READ: 
    - self.item_type: Read from parent ItemRenderer class (value is "sample")
    - self.content: Read from parent ItemRenderer class (contains sample DataFrame and caption)
    - self.name: Read from parent ItemRenderer class
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Must be called on an instance of a concrete subclass that implements this method
    - The instance must have been properly initialized with required parameters
    
    Postconditions: 
    - Method always raises NotImplementedError (no postcondition applies to return value)

## Side Effects:
    None

