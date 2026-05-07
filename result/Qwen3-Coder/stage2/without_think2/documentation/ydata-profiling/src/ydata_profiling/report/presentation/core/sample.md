# `sample.py`

## `src.ydata_profiling.report.presentation.core.sample.Sample` · *class*

## Summary:
Represents a sample data item for report presentation, extending ItemRenderer to display data samples in profiling reports.

## Description:
The Sample class encapsulates sample data (typically a pandas DataFrame) for inclusion in profiling reports. It inherits from ItemRenderer and provides a standardized interface for displaying data samples with optional captions. This class serves as a container for sample data and associated metadata, enabling consistent integration into various report formats.

## State:
- name: str - Human-readable identifier for the sample, used for labeling in reports
- sample: pd.DataFrame - The actual sample data to be displayed, stored in the content dictionary
- caption: Optional[str] - Optional descriptive text to accompany the sample data display
- item_type: str - Fixed value "sample" identifying this as a sample-type report item
- content: dict - Dictionary containing the sample data and caption information
- anchor_id: Optional[str] - Unique identifier for HTML anchors, used for navigation in reports
- classes: Optional[str] - CSS classes for styling the rendered sample output

## Lifecycle:
- Creation: Instantiate with a name, sample DataFrame, and optional caption. The constructor calls the parent ItemRenderer.__init__ with item_type="sample" and the content dictionary.
- Usage: Typically used within report generation pipelines where render() is called on concrete implementations to produce presentation-ready output.
- Destruction: No special cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[Sample.__init__] --> B[ItemRenderer.__init__]
    B --> C[Sets item_type="sample"]
    C --> D[Stores sample and caption in content]
    D --> E[Sample.__repr__]
    E --> F[Returns "Sample"]
    F --> G[Sample.render]
    G --> H[Raises NotImplementedError]
```

## Raises:
- No explicit exceptions raised by __init__
- render() method raises NotImplementedError when called on the base class

## Example:
```python
import pandas as pd
from ydata_profiling.report.presentation.core.sample import Sample

# Create a sample DataFrame
sample_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

# Create a Sample instance
sample_item = Sample(name="First Sample", sample=sample_data, caption="Example dataset")

# The repr method returns a consistent string
print(repr(sample_item))  # Output: "Sample"

# The render method must be implemented by subclasses
# sample_item.render()  # Would raise NotImplementedError
```

### `src.ydata_profiling.report.presentation.core.sample.Sample.__init__` · *method*

## Summary:
Initializes a Sample instance with a DataFrame sample and optional caption, setting up the item type and content structure.

## Description:
This method constructs a Sample object by calling the parent ItemRenderer.__init__ method with the item type "sample" and a content dictionary containing the sample DataFrame and optional caption. The Sample class represents a data sample in the profiling report presentation layer, typically used to display a subset of data for inspection.

## Args:
    name (str): The name identifier for this sample item, used for labeling and referencing in the report.
    sample (pd.DataFrame): The pandas DataFrame containing the sample data to be displayed.
    caption (Optional[str]): An optional caption to describe or annotate the sample data, defaults to None.
    **kwargs: Additional keyword arguments passed to the parent constructor for metadata like anchor_id and classes.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "sample" 
    - self.content: Updated with sample data and caption in a dictionary structure

## Constraints:
    Preconditions:
    - name must be a string
    - sample must be a valid pandas DataFrame
    - caption must be None or a string
    - All kwargs must be valid parameters for the parent constructor
    Postconditions:
    - The Sample instance is properly initialized with item_type="sample"
    - The content dictionary contains the sample DataFrame under the "sample" key
    - The caption is stored in the content dictionary under the "caption" key

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `src.ydata_profiling.report.presentation.core.sample.Sample.__repr__` · *method*

## Summary:
Returns a string representation of the Sample object, consistently returning "Sample".

## Description:
The `__repr__` method provides a standardized string representation for Sample instances. This method overrides the default object representation to return a fixed string "Sample" regardless of the object's internal state. It is called automatically when the built-in `repr()` function is applied to a Sample instance or when the object is displayed in interactive environments.

## Args:
    None

## Returns:
    str: Always returns the literal string "Sample"

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: Always returns the same string value "Sample"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.sample.Sample.render` · *method*

## Summary:
Generates a visual representation of sample data for report presentation.

## Description:
The render method is an abstract interface that must be implemented by subclasses to convert sample data into a presentation-ready format. This method is part of the ItemRenderer hierarchy and is responsible for transforming the sample data (stored in self.content['sample']) and associated metadata into a format suitable for report rendering, such as HTML tables or markdown representations.

## Args:
    None

## Returns:
    Any: The rendered representation of the sample data, typically HTML or markdown formatted content that can be embedded in profiling reports

## Raises:
    NotImplementedError: When called on the base class without a concrete implementation

## State Changes:
    Attributes READ: 
    - self.item_type: Identifies this as a "sample" type item
    - self.content: Contains the sample data (pd.DataFrame) and caption information
    - self.name: Provides human-readable label for the sample
    - self.anchor_id: May be used for HTML anchor generation in reports
    - self.classes: May be used for CSS styling of the rendered output

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The Sample instance must be properly initialized with valid sample data (pd.DataFrame) and caption
    - The render method should only be called on concrete implementations, not the base class
    - The sample data must be a valid pandas DataFrame
    
    Postconditions:
    - Returns a valid presentation-ready representation of the sample data
    - The returned value should be compatible with the reporting framework's rendering pipeline
    - The output format should be appropriate for embedding in HTML/markdown reports

## Side Effects:
    None

