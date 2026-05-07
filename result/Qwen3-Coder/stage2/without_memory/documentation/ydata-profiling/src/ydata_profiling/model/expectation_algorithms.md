# `expectation_algorithms.py`

## `src.ydata_profiling.model.expectation_algorithms.generic_expectations` · *function*

## Summary:
Applies basic data quality expectations to a column based on its statistical summary.

## Description:
This function evaluates column statistics and applies appropriate Great Expectations validations to assess data quality. It ensures columns exist, are not null when they shouldn't be, and are unique when all values are distinct. This function is typically called during automated data profiling to establish baseline quality expectations for each column.

## Args:
    name (str): The name of the column to validate
    summary (dict): Statistical summary of the column containing keys 'n_missing' and 'p_unique'
    batch (Any): Great Expectations batch object that supports expectation methods
    *args: Additional arguments (currently unused)

## Returns:
    Tuple[str, dict, Any]: A tuple containing the column name, its summary statistics, and the updated batch object with applied expectations

## Raises:
    None explicitly raised - relies on Great Expectations batch methods to handle validation failures

## Constraints:
    Preconditions:
    - The batch parameter must support Great Expectations expectation methods
    - The summary dictionary must contain 'n_missing' and 'p_unique' keys
    - The name parameter must be a valid column identifier

    Postconditions:
    - The batch object will have expectations applied based on summary statistics
    - The returned tuple preserves the original parameters with potential modifications to the batch

## Side Effects:
    None directly observable - modifies the batch object internally through Great Expectations methods

## Control Flow:
```mermaid
flowchart TD
    A[Start generic_expectations] --> B{summary["n_missing"] == 0?}
    B -- Yes --> C[batch.expect_column_values_to_not_be_null(name)]
    B -- No --> D[Skip null check]
    C --> E[batch.expect_column_to_exist(name)]
    D --> E
    E --> F{summary["p_unique"] == 1.0?}
    F -- Yes --> G[batch.expect_column_values_to_be_unique(name)]
    F -- No --> H[Skip uniqueness check]
    G --> I[Return (name, summary, batch)]
    H --> I
```

## Examples:
    # Basic usage with a column summary
    column_name = "age"
    column_summary = {"n_missing": 0, "p_unique": 1.0}
    result = generic_expectations(column_name, column_summary, data_batch)
    # Returns (column_name, column_summary, data_batch) with expectations applied

## `src.ydata_profiling.model.expectation_algorithms.numeric_expectations` · *function*

## Summary:
Generates Great Expectations for numeric column validation based on summary statistics and type requirements.

## Description:
Applies a series of Great Expectations to validate numeric column properties including data type compliance, monotonicity constraints, and value range boundaries. This function is typically called during automated data profiling to establish baseline expectations for numeric columns.

## Args:
    name (str): The name of the column being validated
    summary (dict): Dictionary containing column summary statistics including:
        - monotonic_increase (bool): Whether values should be monotonically increasing
        - monotonic_increase_strict (bool): Whether monotonic increase should be strict
        - monotonic_decrease (bool): Whether values should be monotonically decreasing
        - monotonic_decrease_strict (bool): Whether monotonic decrease should be strict
        - min (float, optional): Minimum acceptable value
        - max (float, optional): Maximum acceptable value
    batch (Any): Great Expectations batch object containing the data to validate
    *args: Additional arguments (unused in current implementation)

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original column name, summary statistics, and batch object unchanged

## Raises:
    None explicitly raised - delegates to Great Expectations methods which may raise their own exceptions

## Constraints:
    Preconditions:
    - The batch parameter must be a valid Great Expectations batch object with expect_column_* methods
    - The summary dictionary must contain the expected keys for monotonicity and range validation
    - Column name must be a valid string identifier

    Postconditions:
    - The batch object will have additional expectations added for the specified column
    - The returned tuple maintains the same structure as the input

## Side Effects:
    - Modifies the batch object by adding new expectation definitions
    - No external I/O operations performed

## Control Flow:
```mermaid
flowchart TD
    A[Start numeric_expectations] --> B{Is monotonic_increase True?}
    B -- Yes --> C[Add expect_column_values_to_be_increasing]
    B -- No --> D[Skip monotonic increase]
    D --> E{Is monotonic_decrease True?}
    E -- Yes --> F[Add expect_column_values_to_be_decreasing]
    E -- No --> G[Skip monotonic decrease]
    G --> H{Is min/max in summary?}
    H -- Yes --> I[Add expect_column_values_to_be_between]
    H -- No --> J[Skip range validation]
    J --> K[Return (name, summary, batch)]
```

## Examples:
```python
# Basic usage with minimal summary
name = "age"
summary = {"monotonic_increase": False, "monotonic_decrease": False}
batch = get_batch()  # Great Expectations batch object
result = numeric_expectations(name, summary, batch)
# Returns (name, summary, batch) with expectations added to batch

# Usage with range constraints
summary = {
    "min": 0, 
    "max": 100, 
    "monotonic_increase": True, 
    "monotonic_increase_strict": True
}
result = numeric_expectations(name, summary, batch)
# Adds type, monotonicity, and range expectations to batch
```

## `src.ydata_profiling.model.expectation_algorithms.categorical_expectations` · *function*

## Summary:
Applies categorical value set expectations to data batches based on distinct value thresholds.

## Description:
This function determines whether to apply a categorical expectation to validate that column values belong to a predefined set of categories. It evaluates whether the number of distinct values or the proportion of distinct values falls below specified thresholds, and if so, creates a Great Expectations expectation for the column.

## Args:
    name (str): The name of the column to process
    summary (dict): Dictionary containing column summary statistics including:
        - n_distinct: Number of distinct values in the column
        - p_distinct: Proportion of distinct values relative to total count
        - value_counts_without_nan: Dictionary mapping values to their counts
    batch (Any): Great Expectations batch object that will receive the expectation
    *args: Additional arguments (not used in current implementation)

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original column name, summary dictionary, and batch object unchanged

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - summary dictionary must contain keys: "n_distinct", "p_distinct", and "value_counts_without_nan"
    - batch must support the expect_column_values_to_be_in_set method
    - name must be a string

    Postconditions:
    - The batch object may have a new expectation added to it
    - The returned tuple contains the original inputs unchanged

## Side Effects:
    - Modifies the batch object by adding a new expectation via expect_column_values_to_be_in_set method call
    - No external I/O operations or state mutations beyond the batch modification

## Control Flow:
```mermaid
flowchart TD
    A[Start categorical_expectations] --> B{summary["n_distinct"] < 10 OR summary["p_distinct"] < 0.2?}
    B -- Yes --> C[batch.expect_column_values_to_be_in_set()]
    B -- No --> D[Return original tuple]
    C --> D
```

## Examples:
    # Basic usage with a summary containing categorical data
    name = "category_column"
    summary = {
        "n_distinct": 5,
        "p_distinct": 0.15,
        "value_counts_without_nan": {"A": 10, "B": 5, "C": 3}
    }
    batch = SomeBatchObject()
    result = categorical_expectations(name, summary, batch)
    # Result will contain the batch with a new expectation added
    
    # Usage with data that doesn't meet threshold criteria
    name = "numeric_column"  
    summary = {
        "n_distinct": 100,
        "p_distinct": 0.8,
        "value_counts_without_nan": {1: 10, 2: 5, 3: 3}
    }
    batch = SomeBatchObject()
    result = categorical_expectations(name, summary, batch)
    # Result will be identical to inputs (no expectation added)
```

## `src.ydata_profiling.model.expectation_algorithms.path_expectations` · *function*

## Summary:
Returns the input parameters as a standardized tuple for path-based expectation processing.

## Description:
This function serves as a simple passthrough mechanism for path expectation algorithms, taking a name identifier, summary dictionary, batch object, and optional additional arguments, then returning them in a consistent tuple format. It appears to be part of a standardized interface for expectation algorithms within the profiling system.

## Args:
    name (str): A string identifier for the expectation being processed.
    summary (dict): A dictionary containing summary statistics or metadata about the data being profiled.
    batch (Any): An object representing the data batch being analyzed, likely containing the actual data samples.
    *args: Additional positional arguments that may be passed to the expectation algorithm.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in that order.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: All input parameters must be provided with correct types (name as str, summary as dict, batch as Any).
    Postconditions: The returned tuple maintains the exact same values as the input parameters.

## Side Effects:
    None: This function has no side effects and does not perform any I/O operations or mutate external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start path_expectations] --> B{Validate inputs}
    B --> C[Return (name, summary, batch)]
```

## Examples:
```python
# Basic usage
result = path_expectations("my_path", {"count": 100}, my_batch_object)
# Returns: ("my_path", {"count": 100}, my_batch_object)

# With additional arguments
result = path_expectations("path_name", {"stats": {}}, batch_obj, "extra_arg1", "extra_arg2")
# Returns: ("path_name", {"stats": {}}, batch_obj)
```

## `src.ydata_profiling.model.expectation_algorithms.datetime_expectations` · *function*

## Summary:
Generates Great Expectations for datetime column validation by setting value range constraints.

## Description:
This function creates data validation expectations for datetime columns by checking if minimum and maximum values exist in the summary statistics. When these bounds are present, it configures a Great Expectations constraint that ensures all values in the column fall within the specified datetime range. The function is designed to work with the Great Expectations framework for data profiling and validation.

## Args:
    name (str): The name of the column being validated
    summary (dict): Dictionary containing statistical summary of the column, potentially including "min" and "max" keys
    batch (Any): Great Expectations batch object that will store the expectation
    *args: Additional arguments (unused in current implementation)

## Returns:
    Tuple[str, dict, Any]: Returns the original input parameters unchanged as a tuple (name, summary, batch)

## Raises:
    None explicitly raised - however, the underlying batch.expect_column_values_to_be_between method may raise exceptions if invalid parameters are passed

## Constraints:
    Preconditions:
    - The batch parameter must be a valid Great Expectations batch object with expect_column_values_to_be_between method
    - The summary dictionary should contain appropriate datetime values if min/max keys are present
    
    Postconditions:
    - If min/max values exist in summary, the batch will contain a new expectation
    - The returned tuple contains the original parameters unchanged

## Side Effects:
    - Mutates the batch object by adding a new expectation
    - No external I/O operations or state changes beyond the batch mutation

## Control Flow:
```mermaid
flowchart TD
    A[Start datetime_expectations] --> B{min/max in summary?}
    B -- Yes --> C[batch.expect_column_values_to_be_between]
    C --> D[Return (name, summary, batch)]
    B -- No --> D
```

## Examples:
```python
# Basic usage with min/max values
name = "date_column"
summary = {"min": "2020-01-01", "max": "2023-12-31"}
batch = SomeGreatExpectationsBatch()
result = datetime_expectations(name, summary, batch)
# Result: ("date_column", {"min": "2020-01-01", "max": "2023-12-31"}, batch)
# With expectation added to batch

# Usage without min/max values
name = "date_column"
summary = {"count": 100}
batch = SomeGreatExpectationsBatch()
result = datetime_expectations(name, summary, batch)
# Result: ("date_column", {"count": 100}, batch)
# No expectation added to batch
```

## `src.ydata_profiling.model.expectation_algorithms.image_expectations` · *function*

## Summary:
Returns the input parameters unchanged as a tuple, serving as a base implementation for image data type expectations.

## Description:
This function acts as a placeholder or base implementation for handling image data type expectations within the profiling system. It accepts a name identifier, summary dictionary containing image statistics, and a batch object, returning them unmodified as a tuple. This function likely serves as a fallback or default implementation that can be overridden by more specific expectation handlers for image data types.

## Args:
    name (str): Identifier or name for the expectation being processed.
    summary (dict): Dictionary containing statistical summary information about the image data.
    batch (Any): Batch object containing the image data being profiled.
    *args: Additional positional arguments that may be passed to the function.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in the same order as received.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: 
    - The name parameter must be a string
    - The summary parameter must be a dictionary
    - The batch parameter can be any type
    
    Postconditions:
    - The returned tuple maintains the same order as the input parameters
    - All input parameters are returned unchanged

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start image_expectations] --> B[Return (name, summary, batch)]
```

## Examples:
```python
# Basic usage
name = "image_summary"
summary = {"mean": 0.5, "std": 0.1}
batch = some_image_batch_object
result = image_expectations(name, summary, batch)
# result = ("image_summary", {"mean": 0.5, "std": 0.1}, some_image_batch_object)
```

## `src.ydata_profiling.model.expectation_algorithms.url_expectations` · *function*

## Summary:
Minimal passthrough implementation for URL data validation expectations.

## Description:
This function serves as a basic implementation for URL expectation validation within a data profiling or validation framework. It accepts a name identifier, summary statistics, a data batch, and optional additional arguments, then returns them as a tuple. This function likely acts as a base template or placeholder that can be extended or overridden by more specific URL validation implementations in derived classes or plugins.

The function follows a common pattern in expectation frameworks where expectation functions are expected to return a standardized tuple format (name, summary, batch) to maintain consistency in how validation results are processed and reported throughout the system.

## Args:
    name (str): The name identifier for the expectation.
    summary (dict): A dictionary containing summary statistics or metadata about the data being validated.
    batch (Any): The data batch or dataset being processed for validation.
    *args: Additional positional arguments that may be passed to customize or extend the expectation behavior.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in that order. The *args are not included in the return value.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: All input parameters must be provided with correct types (name as str, summary as dict, batch as Any).
    Postconditions: The returned tuple maintains the exact same values as the input parameters (name, summary, batch).

## Side Effects:
    None: This function has no side effects and does not perform any I/O operations or state mutations.

## Control Flow:
```mermaid
flowchart TD
    A[Start url_expectations] --> B[Receive name: str, summary: dict, batch: Any, *args]
    B --> C[Return (name, summary, batch)]
    C --> D[End url_expectations]
```

## Examples:
```python
# Basic usage - typical pattern for expectation functions
result = url_expectations("url_check", {"count": 10}, my_data_batch)
# Returns: ("url_check", {"count": 10}, my_data_batch)

# Usage with additional arguments - common in expectation frameworks
result = url_expectations("url_validation", {"error_count": 0}, large_dataset, "extra_param")
# Returns: ("url_validation", {"error_count": 0}, large_dataset)
# Note: extra_param is ignored in the return value
```

## `src.ydata_profiling.model.expectation_algorithms.file_expectations` · *function*

## Summary:
Validates that a specified file exists within a Great Expectations batch and returns the input parameters unchanged.

## Description:
This function implements a file existence expectation validation. It serves as a standardized interface for validating file presence in data profiling workflows. The function integrates with Great Expectations by calling the `expect_file_to_exist` method on the provided batch object, which records the expectation in the batch's validation results.

## Args:
    name (str): The name or path of the file to validate for existence.
    summary (dict): Metadata or summary information about the file being validated.
    batch (Any): A Great Expectations batch object that contains the file validation methods.
    *args: Additional positional arguments that may be passed to the expectation function (currently unused in this implementation).

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in the same order they were provided.

## Raises:
    None explicitly raised by this function. However, the underlying `batch.expect_file_to_exist(name)` call may raise exceptions if the batch object or expectation method is not properly configured.

## Constraints:
    Preconditions:
    - The `batch` parameter must be a valid Great Expectations batch object with an `expect_file_to_exist` method.
    - The `name` parameter must be a string representing a valid file path or identifier.
    
    Postconditions:
    - The file existence expectation is recorded in the batch's validation results.
    - All input parameters are returned unchanged.

## Side Effects:
    - Modifies the internal state of the `batch` object by recording the file existence expectation.
    - May perform I/O operations if the underlying batch implementation requires file system access to validate existence.

## Control Flow:
```mermaid
flowchart TD
    A[Start file_expectations] --> B{batch.expect_file_to_exist(name)}
    B --> C[Return (name, summary, batch)]
```

## Examples:
```python
# Basic usage
name = "data.csv"
summary = {"size": 1024, "type": "csv"}
batch = create_batch_from_file("data.csv")

result_name, result_summary, result_batch = file_expectations(name, summary, batch)
# result_name == "data.csv"
# result_summary == {"size": 1024, "type": "csv"}
# result_batch now contains the file existence expectation
```

