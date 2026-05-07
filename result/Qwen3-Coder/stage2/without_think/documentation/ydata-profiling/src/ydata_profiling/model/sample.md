# `sample.py`

## `src.ydata_profiling.model.sample.Sample` · *class*

## Summary:
Represents a data sample with identifying metadata for profiling reports.

## Description:
The Sample class is a Pydantic BaseModel designed to encapsulate data samples used in ydata-profiling reports. It provides a standardized structure for storing sample data along with identifying metadata including an ID, name, and optional caption.

This class is intended to be generic over some data type T, allowing it to hold various kinds of sample data while maintaining consistent metadata structure. The exact type of the data field depends on how instances are created and used within the profiling framework.

## State:
- id: str - Unique identifier for the sample
- data: T - Generic data payload for the sample (type T is defined elsewhere in the codebase)
- name: str - Human-readable name for the sample
- caption: Optional[str] - Optional descriptive caption for the sample, defaults to None

The class inherits validation and serialization capabilities from Pydantic's BaseModel. The data field uses a generic type variable T, which indicates that the actual data type will be determined by the specific instantiation context.

## Lifecycle:
- Creation: Instantiate with id, data, and name parameters; caption is optional
- Usage: Access fields directly to retrieve sample metadata and data
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Sample Constructor] --> B[Validate id (str)]
    B --> C[Validate data (T)]
    C --> D[Validate name (str)]
    D --> E[Validate caption (Optional[str])]
    E --> F[Return Sample instance]
```

## Raises:
- ValidationError: May be raised by Pydantic validation if provided arguments don't meet field requirements

## Example:
```python
# Creating a sample with string data
sample1 = Sample(id="sample_1", data="example_string", name="Example String")

# Creating a sample with numeric data  
sample2 = Sample(id="sample_2", data=42, name="Example Number", caption="A numeric sample")

# Accessing sample properties
print(sample1.id)      # "sample_1"
print(sample1.data)    # "example_string" 
print(sample1.name)    # "Example String"
print(sample1.caption) # None
```

## `src.ydata_profiling.model.sample.get_sample` · *function*

## Summary:
Creates a list of data samples (head, tail, and random) from a dataframe according to configured sampling parameters.

## Description:
Generates a collection of Sample objects representing different views of the input dataframe. These samples typically include the first few rows (head), last few rows (tail), and randomly selected rows (random) based on configuration settings. This function abstracts the sampling logic to provide consistent sample generation for profiling reports.

The function extracts sampling configuration from the Settings object's samples attribute, which specifies how many head, tail, and random samples to generate. Each returned Sample object contains the sampled data along with identifying metadata such as an ID, name, and optional caption.

## Args:
    config (Settings): Configuration object containing sampling parameters in the samples attribute. The samples attribute should define head, tail, and random integer values indicating how many samples of each type to generate.
    df (T): Input dataframe or data structure to sample from. The type T is generic and represents the specific dataframe type being processed.

## Returns:
    List[Sample]: A list of Sample objects, each containing a subset of the input data along with identifying metadata. The list may contain zero or more samples depending on the configuration values for head, tail, and random.

## Raises:
    NotImplementedError: Currently always raised as the implementation is not yet completed.

## Constraints:
    Preconditions:
    - The config parameter must be a valid Settings object with properly initialized samples configuration
    - The df parameter must be a valid dataframe-like object that supports indexing operations
    
    Postconditions:
    - Returns a list of Sample objects with valid metadata and data
    - Each Sample object's data field contains the appropriate subset of the original dataframe

## Side Effects:
    None: This function is pure and does not perform any I/O operations or mutate external state.

## Control Flow:
```mermaid
flowchart TD
    A[get_sample called] --> B[Extract samples config from Settings]
    B --> C{head > 0?}
    C -->|Yes| D[Get head samples]
    C -->|No| E[Skip head samples]
    D --> F[Get tail samples]
    E --> F
    F --> G{random > 0?}
    G -->|Yes| H[Get random samples]
    G -->|No| I[Skip random samples]
    H --> J[Combine all samples]
    I --> J
    J --> K[Return List[Sample]]
```

## Examples:
```python
from src.ydata_profiling.config import Settings
from src.ydata_profiling.model.sample import get_sample

# Configure sampling settings
config = Settings(samples=Samples(head=5, tail=5, random=3))

# Assuming df is a pandas DataFrame
samples = get_sample(config, df)

# Process the samples
for sample in samples:
    print(f"Sample {sample.name}: {len(sample.data)} rows")
```

## `src.ydata_profiling.model.sample.get_custom_sample` · *function*

## Summary
Creates a list containing a single sample object from a dictionary specification.

## Description
Transforms a dictionary representation of a sample into a properly structured sample object with default handling for missing metadata fields. This function processes a dictionary containing sample data and metadata, ensuring that optional fields are handled gracefully by providing default values.

The function serves as a factory method for creating sample objects, promoting code reuse and maintaining clean separation between data preparation and sample creation logic.

## Args
    sample (dict): Dictionary containing sample data with required "data" key and optional "name" and "caption" keys

## Returns
    List[Sample]: A list containing exactly one sample object with the following characteristics:
        - The sample object is constructed with id="custom"
        - The sample object contains data from sample["data"] 
        - The sample object has name set to sample["name"] or None if missing
        - The sample object has caption set to sample["caption"] or None if missing

## Raises
    KeyError: If the input dictionary does not contain a "data" key

## Constraints
    Preconditions:
        - Input dictionary must contain a "data" key
        - Input dictionary may optionally contain "name" and "caption" keys
        
    Postconditions:
        - Returned list contains exactly one sample object
        - Sample object has id field set to "custom"
        - Sample object has data field populated from input
        - Sample object has name field set to input value or None
        - Sample object has caption field set to input value or None

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Start get_custom_sample] --> B{Is "name" in sample?}
    B -->|No| C[Set sample["name"] = None]
    C --> D{Is "caption" in sample?}
    D -->|No| E[Set sample["caption"] = None]
    E --> F[Create Sample instance]
    F --> G[Return list with Sample]
    B -->|Yes| D
    D -->|Yes| F
```

## Examples
```python
# Basic usage with minimal data
sample_dict = {"data": [1, 2, 3, 4]}
result = get_custom_sample(sample_dict)
# Returns: [Sample(...)] where Sample has id="custom", data=[1, 2, 3, 4], name=None, caption=None

# Usage with full metadata
sample_dict = {
    "data": {"feature1": [1, 2], "feature2": [3, 4]}, 
    "name": "My Custom Sample", 
    "caption": "A sample dataset"
}
result = get_custom_sample(sample_dict)
# Returns: [Sample(...)] where Sample has id="custom", data={"feature1": [1, 2], "feature2": [3, 4]}, name="My Custom Sample", caption="A sample dataset"
```

