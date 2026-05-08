# `expectation_algorithms.py`

## `src.ydata_profiling.model.expectation_algorithms.generic_expectations` · *function*

## Summary:
Validates column properties using Great Expectations by checking for existence, null values, and uniqueness constraints based on summary statistics.

## Description:
This function applies a set of standard expectations to a data batch column based on statistical summary information. It serves as a generic validation layer that automatically generates appropriate expectations for data quality assessment. The function is designed to be called during profiling operations to establish baseline expectations for columns.

## Args:
    name (str): The name of the column being validated
    summary (dict): Statistical summary containing keys 'n_missing' and 'p_unique' 
    batch (Any): Great Expectations batch object that supports expect_* methods
    *args: Additional arguments (currently unused in implementation)

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original column name, summary dictionary, and batch object unchanged

## Raises:
    None explicitly raised - relies on Great Expectations methods to handle validation failures

## Constraints:
    Preconditions:
    - The batch parameter must support Great Expectations expect_* methods
    - The summary dictionary must contain 'n_missing' and 'p_unique' keys
    - The name parameter must be a valid column identifier
    
    Postconditions:
    - The batch object will have expectations applied for the specified column
    - All input parameters remain unchanged in the returned tuple

## Side Effects:
    - Mutates the batch object by applying expectations (side effect of Great Expectations methods)
    - No external I/O operations or state changes beyond the batch mutation

## Control Flow:
```mermaid
flowchart TD
    A[Start generic_expectations] --> B[Check column existence]
    B --> C{summary["n_missing"] == 0?}
    C -->|Yes| D[Expect not null values]
    C -->|No| E[Skip null check]
    D --> F[Check uniqueness]
    E --> F
    F --> G{summary["p_unique"] == 1.0?}
    G -->|Yes| H[Expect unique values]
    G -->|No| I[Skip uniqueness check]
    H --> J[Return tuple]
    I --> J
```

## Examples:
    # Basic usage in profiling workflow
    column_name = "age"
    column_summary = {"n_missing": 0, "p_unique": 1.0}
    batch = profiler.get_batch()
    
    result = generic_expectations(column_name, column_summary, batch)
    # Returns (column_name, column_summary, batch) with expectations applied

## `src.ydata_profiling.model.expectation_algorithms.numeric_expectations` · *function*

## Summary:
Applies numeric data type and value range expectations to a column using Great Expectations.

## Description:
This function validates that a column contains numeric data and applies additional constraints based on summary statistics. It integrates with Great Expectations to define data quality expectations for numeric columns during profiling. The function adds expectations to the batch object in-place and returns the original arguments unchanged.

## Args:
    name (str): The name of the column to validate.
    summary (dict): Dictionary containing statistical summary information about the column, including:
        - monotonic_increase (bool): Whether the column values should be monotonically increasing
        - monotonic_increase_strict (bool): Whether the monotonic increase should be strict
        - monotonic_decrease (bool): Whether the column values should be monotonically decreasing  
        - monotonic_decrease_strict (bool): Whether the monotonic decrease should be strict
        - min (float/int, optional): Minimum acceptable value for the column
        - max (float/int, optional): Maximum acceptable value for the column
    batch (Any): Great Expectations batch object that will store the generated expectations.
    *args: Additional positional arguments (unused in current implementation).

## Returns:
    Tuple[str, dict, Any]: Returns the input arguments unchanged as a tuple (name, summary, batch).

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The batch parameter must be a valid Great Expectations batch object with expectation methods.
    - The summary dictionary must contain the expected keys for monotonicity and min/max validation.
    
    Postconditions:
    - The batch object will have new expectations added to it.
    - The returned tuple contains the same values as the input arguments.

## Side Effects:
    - Modifies the batch object by adding new expectation methods to it.
    - No external I/O operations performed.

## Control Flow:
```mermaid
flowchart TD
    A[Start numeric_expectations] --> B[Define numeric type names]
    B --> C[expect_column_values_to_be_in_type_list]
    C --> D{summary['monotonic_increase']}
    D -- True --> E[expect_column_values_to_be_increasing]
    D -- False --> F{summary['monotonic_decrease']}
    F -- True --> G[expect_column_values_to_be_decreasing]
    F -- False --> H{any(['min', 'max'] in summary)}
    H -- True --> I[expect_column_values_to_be_between]
    H -- False --> J[Return result]
    E --> J
    G --> J
    I --> J
```

## Examples:
    # Basic usage with minimal summary
    name, summary, batch = numeric_expectations("age", {"min": 0, "max": 120}, my_batch)
    
    # Usage with monotonic increase constraint
    name, summary, batch = numeric_expectations(
        "sales", 
        {"monotonic_increase": True, "monotonic_increase_strict": True, "min": 0}, 
        my_batch
    )

## `src.ydata_profiling.model.expectation_algorithms.categorical_expectations` · *function*

## Summary:
Applies categorical data validation expectations based on distinct value thresholds.

## Description:
This function evaluates whether a categorical column should have a "values in set" expectation applied. When the number of distinct values is below a configured absolute threshold (10) or the proportion of distinct values is below a relative threshold (0.2), it adds an expectation to validate that all column values belong to the set of observed values.

## Args:
    name (str): The name of the column being validated
    summary (dict): Dictionary containing column statistics including:
        - n_distinct: Number of distinct values in the column
        - p_distinct: Proportion of distinct values relative to total count
        - value_counts_without_nan: Dictionary mapping values to their counts
    batch (Any): The data batch object that will receive the expectation
    *args: Additional arguments (not used in current implementation)

## Returns:
    Tuple[str, dict, Any]: Returns the original inputs unchanged as a tuple (name, summary, batch)

## Raises:
    None explicitly raised, but may raise exceptions from batch.expect_column_values_to_be_in_set() if called

## Constraints:
    Preconditions:
        - summary dictionary must contain keys: "n_distinct", "p_distinct", and "value_counts_without_nan"
        - batch must support expect_column_values_to_be_in_set() method
    Postconditions:
        - If thresholds are met, batch will contain an added expectation
        - If thresholds are not met, batch remains unchanged
        - All input parameters remain unmodified

## Side Effects:
    - Modifies the batch object by adding a new expectation
    - No external I/O operations or state mutations beyond the batch modification

## Control Flow:
```mermaid
flowchart TD
    A[Start categorical_expectations] --> B{summary["n_distinct"] < 10 OR summary["p_distinct"] < 0.2}
    B -- Yes --> C[batch.expect_column_values_to_be_in_set()]
    B -- No --> D[Return inputs unchanged]
    C --> D
```

## Examples:
    # Basic usage with a categorical column
    name = "category_column"
    summary = {
        "n_distinct": 5,
        "p_distinct": 0.15,
        "value_counts_without_nan": {"A": 10, "B": 5, "C": 3}
    }
    batch = SomeBatchObject()
    
    result = categorical_expectations(name, summary, batch)
    # Result contains the same inputs, but batch now has an expectation added
```

## `src.ydata_profiling.model.expectation_algorithms.path_expectations` · *function*

## Summary:
Processes and returns expectation-related data in a standardized tuple format for data profiling workflows.

## Description:
This function serves as a basic expectation processor that takes expectation metadata and returns it in a consistent tuple structure. It appears to be part of a data profiling framework that uses Great Expectations for validation and monitoring. The function acts as a wrapper that maintains the expected interface while potentially enabling future extension points for expectation processing logic.

## Args:
    name (str): The name or identifier of the expectation being processed
    summary (dict): A dictionary containing summary statistics or metadata about the expectation
    batch (Any): The data batch or context associated with the expectation
    *args: Additional positional arguments that may be used for future extensions

## Returns:
    Tuple[str, dict, Any]: A tuple containing (name, summary, batch) in that order, preserving the input parameters

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - name should be a string identifier
    - summary should be a dictionary-like object
    - batch can be any type of data structure
    - All parameters should be properly initialized before calling

    Postconditions:
    - Returns exactly three elements in the specified order
    - Input parameters are returned unchanged in tuple format

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start path_expectations] --> B{Validate inputs}
    B --> C[Return (name, summary, batch)]
    C --> D[End]
```

## Examples:
```python
# Basic usage
result = path_expectations("column_min_value", {"min": 0}, [1, 2, 3, 4])
# Returns: ("column_min_value", {"min": 0}, [1, 2, 3, 4])

# With additional arguments
result = path_expectations("column_max_value", {"max": 100}, {"data": [1, 2, 3]}, "extra_param")
# Returns: ("column_max_value", {"max": 100}, {"data": [1, 2, 3]})
```

## `src.ydata_profiling.model.expectation_algorithms.datetime_expectations` · *function*

## Summary:
Validates datetime column values against min/max bounds using Great Expectations.

## Description:
This function applies datetime value range validation to a column by checking if all values fall within specified minimum and maximum bounds. It integrates with Great Expectations profiling capabilities to enforce datetime constraints on data columns. The function is designed to be part of a series of expectation algorithms that validate different data types.

## Args:
    name (str): The name of the column being validated.
    summary (dict): A dictionary containing statistical summary information including optional "min" and "max" keys.
    batch (Any): A Great Expectations batch object that supports the expect_column_values_to_be_between method.
    *args: Additional positional arguments (currently unused but maintained for interface compatibility).

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original column name, summary dictionary, and batch object unchanged. This maintains the expected interface for expectation algorithm functions.

## Raises:
    None explicitly raised - relies on underlying Great Expectations method for any exceptions.

## Constraints:
    Preconditions:
    - The batch parameter must support the expect_column_values_to_be_between method
    - The summary dictionary may contain "min" and/or "max" keys for validation
    - The column name must be a valid string identifier

    Postconditions:
    - The batch object will have an expectation added if min/max values exist in summary
    - The returned tuple preserves all input parameters unchanged
    - Function execution does not modify the input summary or name parameters

## Side Effects:
    - Modifies the batch object by adding a new expectation using expect_column_values_to_be_between
    - No external I/O operations or state mutations beyond the batch modification

## Control Flow:
```mermaid
flowchart TD
    A[Start datetime_expectations] --> B{Are min/max keys present in summary?}
    B -- Yes --> C[batch.expect_column_values_to_be_between()]
    B -- No --> D[Skip validation]
    C --> E[Return (name, summary, batch)]
    D --> E
```

## Examples:
    # Basic usage with min/max values
    name = "date_column"
    summary = {"min": "2020-01-01", "max": "2023-12-31"}
    result = datetime_expectations(name, summary, batch)
    
    # Usage with only min value
    summary = {"min": "2020-01-01"}
    result = datetime_expectations(name, summary, batch)
    
    # Usage with no bounds
    summary = {"count": 100}
    result = datetime_expectations(name, summary, batch)
```

## `src.ydata_profiling.model.expectation_algorithms.image_expectations` · *function*

## Summary:
Returns the input parameters as a tuple for image expectation processing.

## Description:
This function serves as a minimal wrapper that passes through its input parameters unchanged. It is designed to conform to a standardized interface expected by the expectation algorithms framework, particularly for image data profiling scenarios. The function acts as a placeholder or default implementation that can be overridden by more specific expectation implementations.

## Args:
    name (str): The name identifier for the expectation.
    summary (dict): A dictionary containing summary statistics or metadata about the data.
    batch (Any): The data batch being processed, typically containing image data.
    *args: Additional positional arguments that may be used by more specialized implementations.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in that order.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: All input parameters must be of the expected types (str, dict, Any respectively).
    Postconditions: The returned tuple maintains the exact same values and types as the input parameters.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B[name, summary, batch]
    B --> C[Return (name, summary, batch)]
    C --> D[End]
```

## Examples:
```python
# Basic usage
result = image_expectations("image_quality", {"mean": 0.5}, [image_data])
print(result)  # Output: ("image_quality", {"mean": 0.5}, [image_data])

# With additional arguments
result = image_expectations("image_format", {"size": 100}, [img1, img2], "extra_param")
print(result)  # Output: ("image_format", {"size": 100}, [img1, img2])
```

## `src.ydata_profiling.model.expectation_algorithms.url_expectations` · *function*

## Summary:
Returns the input parameters as a tuple without modification.

## Description:
This function serves as a minimal expectation handler that accepts a name, summary dictionary, and batch object, returning them unchanged in a tuple format. It appears to be part of an expectations framework where various expectation handlers follow a consistent interface pattern.

## Args:
    name (str): A string identifier for the expectation.
    summary (dict): A dictionary containing summary statistics or metadata.
    batch (Any): An object representing a data batch or dataset slice.
    *args: Additional positional arguments that are accepted but not processed.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in that order.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: All input parameters must be of the specified types (name as str, summary as dict, batch as Any).
    Postconditions: The returned tuple contains exactly the same values as the input parameters, maintaining their original types and structures.

## Side Effects:
    None: This function has no side effects and does not perform any I/O operations or mutate external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start url_expectations] --> B[Receive name, summary, batch, *args]
    B --> C[Return (name, summary, batch)]
    C --> D[End]
```

## Examples:
```python
# Basic usage
result = url_expectations("test_name", {"count": 10}, [1, 2, 3])
# Returns: ("test_name", {"count": 10}, [1, 2, 3])

# With additional args
result = url_expectations("test", {"avg": 5.0}, {"data": "sample"}, "extra1", "extra2")
# Returns: ("test", {"avg": 5.0}, {"data": "sample"})
```

## `src.ydata_profiling.model.expectation_algorithms.file_expectations` · *function*

## Summary:
Validates that a file exists in the data batch and returns the validation results.

## Description:
This function serves as an expectation algorithm that verifies the existence of a file within a data batch using Great Expectations. It's designed to be part of a larger profiling pipeline where data expectations are validated. The function acts as a wrapper that integrates file existence checking into the expectation validation framework.

## Args:
    name (str): The name or path of the file to validate for existence
    summary (dict): A dictionary containing summary statistics or metadata about the data
    batch (Any): A Great Expectations batch object that contains the data and validation methods
    *args: Additional arguments that may be passed but are not utilized in this implementation

## Returns:
    Tuple[str, dict, Any]: A tuple containing:
        - name (str): The original file name passed as input
        - summary (dict): The original summary dictionary passed as input
        - batch (Any): The original batch object passed as input

## Raises:
    None explicitly raised in the function body, though the underlying `batch.expect_file_to_exist()` call may raise exceptions if the file doesn't exist or if validation fails.

## Constraints:
    Preconditions:
        - The batch parameter must be a valid Great Expectations batch object with the expect_file_to_exist method
        - The name parameter must be a valid string representing a file path
    Postconditions:
        - The file existence expectation has been added to the batch validation suite
        - The original parameters are returned unchanged in a tuple

## Side Effects:
    - Calls the Great Expectations validation method `expect_file_to_exist` on the batch object
    - May trigger file system operations internally within Great Expectations
    - Modifies the batch's validation suite by adding the file existence expectation

## Control Flow:
```mermaid
flowchart TD
    A[Start file_expectations] --> B{Validate batch has expect_file_to_exist}
    B --> C[Call batch.expect_file_to_exist(name)]
    C --> D[Return (name, summary, batch)]
```

## Examples:
    # Basic usage
    name = "data.csv"
    summary = {"count": 100, "columns": 5}
    result = file_expectations(name, summary, batch)
    # Returns: ("data.csv", {"count": 100, "columns": 5}, batch)
``

