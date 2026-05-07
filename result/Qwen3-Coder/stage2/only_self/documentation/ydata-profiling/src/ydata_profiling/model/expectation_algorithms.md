# `expectation_algorithms.py`

## `src.ydata_profiling.model.expectation_algorithms.generic_expectations` · *function*

## Summary:
Applies standard data validation expectations to a column based on its statistical properties.

## Description:
This function automatically generates and applies Great Expectations to validate fundamental data quality properties of a column. It determines which expectations to apply based on whether the column contains missing values and whether all values are unique. This abstraction allows for consistent application of common data quality checks across different columns in a dataset.

## Args:
    name (str): The name of the column to validate
    summary (dict): Dictionary containing column summary statistics with keys 'n_missing' and 'p_unique'
    batch (Any): Great Expectations batch object supporting expectation methods
    *args: Additional arguments (unused in current implementation)

## Returns:
    Tuple[str, dict, Any]: A tuple containing (column_name, summary_statistics, batch_object) where the batch has had expectations applied

## Raises:
    None explicitly raised, but underlying Great Expectations methods may raise exceptions

## Constraints:
    Preconditions:
    - The batch object must support the methods expect_column_to_exist, expect_column_values_to_not_be_null, and expect_column_values_to_be_unique
    - The summary dictionary must contain keys 'n_missing' and 'p_unique' with numeric values
    
    Postconditions:
    - The batch object will have expectations applied according to the column's statistical properties
    - The returned tuple preserves the original input values

## Side Effects:
    - Modifies the batch object by applying expectations to it
    - No external I/O operations or global state changes

## Control Flow:
```mermaid
flowchart TD
    A[Start generic_expectations] --> B{summary["n_missing"] == 0?}
    B -- Yes --> C[expect_column_values_to_not_be_null(name)]
    B -- No --> D[Skip null check]
    C --> E[expect_column_to_exist(name)]
    D --> E
    E --> F{summary["p_unique"] == 1.0?}
    F -- Yes --> G[expect_column_values_to_be_unique(name)]
    F -- No --> H[Skip uniqueness check]
    G --> I[Return (name, summary, batch)]
    H --> I
```

## Examples:
    # Apply expectations to a column with no missing values and all unique values
    column_name = "id"
    column_summary = {"n_missing": 0, "p_unique": 1.0}
    result = generic_expectations(column_name, column_summary, batch)
    # Result: (column_name, column_summary, batch_with_expectations_applied)
    
    # Apply expectations to a column with missing values
    column_summary = {"n_missing": 5, "p_unique": 0.8}
    result = generic_expectations(column_name, column_summary, batch)
    # Result: (column_name, column_summary, batch_with_expectations_applied)
```

## `src.ydata_profiling.model.expectation_algorithms.numeric_expectations` · *function*

## Summary:
Sets numeric data type and value range expectations for a column in a Great Expectations batch.

## Description:
This function configures a Great Expectations batch to validate that a specified column contains numeric data and meets optional monotonicity and value range constraints. It is used as part of the profiling process to establish data quality expectations for numeric columns.

## Args:
    name (str): The name of the column to validate.
    summary (dict): A dictionary containing column statistics including:
        - monotonic_increase (bool): Whether the column values should be monotonically increasing
        - monotonic_increase_strict (bool): Whether the increase should be strictly increasing
        - monotonic_decrease (bool): Whether the column values should be monotonically decreasing
        - monotonic_decrease_strict (bool): Whether the decrease should be strictly decreasing
        - min (float, optional): Minimum acceptable value for the column
        - max (float, optional): Maximum acceptable value for the column
    batch (Any): A Great Expectations batch object to configure expectations on.
    *args: Additional arguments (currently unused).

## Returns:
    Tuple[str, dict, Any]: A tuple containing the column name, summary dictionary, and batch object in the same order as the input parameters.

## Raises:
    None explicitly raised by this function, though underlying Great Expectations methods may raise exceptions.

## Constraints:
    Preconditions:
        - The batch parameter must be a valid Great Expectations batch object
        - The summary dictionary must contain the expected keys for monotonicity checks
        - The column name must exist in the batch

    Postconditions:
        - The batch will have numeric type expectations configured for the specified column
        - If monotonicity checks are enabled, appropriate expectations will be added
        - If min/max bounds are specified, a between expectation will be added

## Side Effects:
    - Modifies the batch object by adding expectations to it
    - No external I/O operations performed

## Control Flow:
```mermaid
flowchart TD
    A[Start numeric_expectations] --> B{Is monotonic_increase True?}
    B -- Yes --> C[Add expect_column_values_to_be_increasing]
    B -- No --> D[Skip monotonic increase check]
    C --> D
    D --> E{Is monotonic_decrease True?}
    E -- Yes --> F[Add expect_column_values_to_be_decreasing]
    E -- No --> G[Skip monotonic decrease check]
    F --> G
    G --> H{Are min/max specified?}
    H -- Yes --> I[Add expect_column_values_to_be_between]
    H -- No --> J[Skip range check]
    I --> J
    J --> K[Return (name, summary, batch)]
```

## Examples:
    # Basic usage for a numeric column
    name, summary, batch = numeric_expectations(
        "age", 
        {"monotonic_increase": False, "min": 0, "max": 120}, 
        my_batch
    )
    
    # Usage with monotonicity checks
    name, summary, batch = numeric_expectations(
        "temperature", 
        {
            "monotonic_increase": True, 
            "monotonic_increase_strict": True,
            "min": -50, 
            "max": 50
        }, 
        my_batch
    )

## `src.ydata_profiling.model.expectation_algorithms.categorical_expectations` · *function*

## Summary:
Applies categorical data validation expectations to a column based on distinct value thresholds.

## Description:
Generates Great Expectations for categorical columns when the number of distinct values is below a specified absolute threshold (10) or the proportion of distinct values is below a relative threshold (0.2). This function encapsulates the logic for determining when categorical expectations should be applied, separating the threshold checking logic from the expectation creation logic. It is typically called by higher-level profiling functions that iterate through columns.

## Args:
    name (str): The name of the column to generate expectations for.
    summary (dict): Dictionary containing column summary statistics including 'n_distinct', 'p_distinct', and 'value_counts_without_nan'. These keys must exist for proper operation.
    batch (Any): Great Expectations batch object that will have expectations added to it. Must support expect_column_values_to_be_in_set method.
    *args: Additional arguments (currently unused in implementation).

## Returns:
    Tuple[str, dict, Any]: Returns the original inputs (name, summary, batch) unchanged. This allows for chaining operations in data processing pipelines.

## Raises:
    KeyError: If summary dictionary is missing required keys ('n_distinct', 'p_distinct', or 'value_counts_without_nan').
    AttributeError: If batch object does not support expect_column_values_to_be_in_set method.
    Other exceptions: May propagate exceptions from the underlying Great Expectations expect_column_values_to_be_in_set call.

## Constraints:
    Preconditions:
    - summary dictionary must contain keys: 'n_distinct', 'p_distinct', and 'value_counts_without_nan'
    - batch must support the expect_column_values_to_be_in_set method
    - name must be a valid column identifier
    
    Postconditions:
    - If thresholds are met, the batch will have an additional expectation added via expect_column_values_to_be_in_set
    - The returned tuple contains the original inputs unchanged
    - No modifications are made to the summary or name parameters

## Side Effects:
    - Modifies the batch object by adding a new expectation via expect_column_values_to_be_in_set
    - No external I/O operations or state mutations beyond the batch modification

## Control Flow:
```mermaid
flowchart TD
    A[Start categorical_expectations] --> B{summary["n_distinct"] < 10 AND summary["p_distinct"] < 0.2}
    B -- True --> C[batch.expect_column_values_to_be_in_set(name, set(summary["value_counts_without_nan"].keys()))]
    B -- False --> D[Return inputs]
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
    batch = SomeGreatExpectationsBatch()
    
    result = categorical_expectations(name, summary, batch)
    # Result will be (name, summary, batch) with expectation added to batch
    
    # Usage in a profiling pipeline
    for column_name, column_summary in profile_results.items():
        name, summary, batch = categorical_expectations(column_name, column_summary, batch)
```

## `src.ydata_profiling.model.expectation_algorithms.path_expectations` · *function*

## Summary:
Returns input parameters as a tuple for path-based expectation processing in data profiling workflows.

## Description:
This function serves as a minimal wrapper that packages input parameters (name, summary, batch) into a standardized tuple format. It acts as a placeholder or adapter in an expectation algorithm pipeline where data profiling expectations are processed and returned in a consistent structure. The function is designed to maintain uniform interface requirements for path-related data expectations while passing through the original parameters unchanged.

## Args:
    name (str): A string identifier for the expectation or data path being processed.
    summary (dict): A dictionary containing summary statistics or metadata about the data.
    batch (Any): An object representing a batch of data, typically containing the actual data being profiled.
    *args: Additional positional arguments that may be accepted for interface compatibility or future extensibility but are not actively processed by this implementation.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original input parameters in the order (name, summary, batch). This maintains consistency in the expectation processing pipeline and allows for uniform handling of different expectation types.

## Raises:
    None: This function does not raise any exceptions as it simply returns its inputs.

## Constraints:
    Preconditions:
    - The name parameter should be a valid string identifier
    - The summary parameter should be a dictionary-like object
    - The batch parameter can be any type of object representing data

    Postconditions:
    - The returned tuple maintains the exact same values as the input parameters
    - The order of elements in the tuple is preserved as (name, summary, batch)

## Side Effects:
    None: This function has no side effects as it only returns its inputs without modifying any external state.

## Control Flow:
```mermaid
flowchart TD
    A[Input: name, summary, batch, *args] --> B[Return (name, summary, batch)]
    B --> C[Output Tuple]
```

## Examples:
    # Basic usage
    result = path_expectations("file_path", {"count": 100}, some_data_batch)
    # Returns: ("file_path", {"count": 100}, some_data_batch)
    
    # Usage with additional arguments (ignored)
    result = path_expectations("file_path", {"count": 100}, some_data_batch, "extra_arg1", "extra_arg2")
    # Returns: ("file_path", {"count": 100}, some_data_batch)

## `src.ydata_profiling.model.expectation_algorithms.datetime_expectations` · *function*

tags. Let me correct this and make sure the format is exactly as requested.
Action: WRITE
<DOCUMENTATION>
## Summary:
Validates datetime column values against minimum and maximum bounds when present in summary statistics.

## Description:
Processes datetime column expectations by checking if column values fall within specified min/max ranges. This function integrates with Great Expectations to enforce datetime value constraints based on summary statistics.

## Args:
    name (str): Column name to validate
    summary (dict): Dictionary containing column summary statistics including optional 'min' and 'max' keys
    batch (Any): Great Expectations batch object that supports expect_column_values_to_be_between method
    *args: Additional arguments (currently unused)

## Returns:
    Tuple[str, dict, Any]: Returns the original input parameters as a tuple (name, summary, batch) unchanged

## Raises:
    None explicitly raised - delegates to Great Expectations batch validation which may raise exceptions

## Constraints:
    Preconditions:
    - The batch parameter must support the expect_column_values_to_be_between method
    - The summary dictionary may contain 'min' and/or 'max' keys with datetime-compatible values
    
    Postconditions:
    - If min/max values exist in summary, the batch will have an expectation added for the column
    - The returned tuple contains the original parameters unchanged

## Side Effects:
    - Modifies the batch object by adding a new expectation via expect_column_values_to_be_between method
    - No external I/O operations or state mutations beyond the batch modification

## Control Flow:
```mermaid
flowchart TD
    A[Start datetime_expectations] --> B{min or max in summary?}
    B -- Yes --> C[Call expect_column_values_to_be_between]
    B -- No --> D[Skip expectation creation]
    C --> E[Return (name, summary, batch)]
    D --> E
```

## Examples:
    # Basic usage with min/max values
    name, summary, batch = datetime_expectations(
        "date_column", 
        {"min": "2020-01-01", "max": "2023-12-31"}, 
        batch_object
    )
    
    # Usage with only min value
    name, summary, batch = datetime_expectations(
        "timestamp_column", 
        {"min": "2020-01-01"}, 
        batch_object
    )
    
    # Usage with no bounds
    name, summary, batch = datetime_expectations(
        "date_column", 
        {"count": 100}, 
        batch_object
    )

## `src.ydata_profiling.model.expectation_algorithms.image_expectations` · *function*

## Summary:
Returns the input parameters as a tuple for image expectation processing.

## Description:
This function serves as a basic implementation for image expectation handling, taking a name identifier, summary statistics, and batch data, and returning them in a standardized tuple format. It acts as a minimal implementation that can be overridden by more specific image expectation functions.

## Args:
    name (str): Identifier for the expectation being processed.
    summary (dict): Dictionary containing summary statistics for the image data.
    batch (Any): Batch data object containing the image data to be processed.
    *args: Additional arguments that may be passed to the function.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the name, summary, and batch parameters in that order.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions: All input parameters must be provided as specified.
    Postconditions: The returned tuple maintains the exact same values as the input parameters.

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start image_expectations] --> B[Receive name, summary, batch]
    B --> C[Return (name, summary, batch)]
    C --> D[End]
```

## Examples:
```python
# Basic usage
result = image_expectations("image_quality", {"mean": 0.5}, batch_object)
print(result)  # Output: ("image_quality", {"mean": 0.5}, batch_object)
```

## `src.ydata_profiling.model.expectation_algorithms.url_expectations` · *function*

## Summary:
Returns the input parameters as a tuple for URL expectation validation.

## Description:
This function serves as a placeholder or default expectation algorithm for URL data validation. It accepts a name, summary dictionary, and batch object, then returns them unchanged in a standardized tuple format. This function likely acts as a base implementation or fallback for URL-related expectation processing within the profiling framework.

## Args:
    name (str): The name identifier for the expectation.
    summary (dict): A dictionary containing summary statistics or metadata about the URL data.
    batch (Any): The batch of data being processed for URL expectations.
    *args: Additional positional arguments that may be passed to the expectation function.

## Returns:
    Tuple[str, dict, Any]: A tuple containing the original name, summary, and batch parameters in that order.

## Raises:
    None: This function does not raise any exceptions.

## Constraints:
    Preconditions:
        - The name parameter should be a string identifier
        - The summary parameter should be a dictionary-like object
        - The batch parameter can be any type of data structure
    
    Postconditions:
        - The returned tuple maintains the exact same values as the input parameters
        - The order of elements in the returned tuple is preserved as (name, summary, batch)

## Side Effects:
    None: This function has no side effects and does not modify any external state.

## Control Flow:
```mermaid
flowchart TD
    A[Start url_expectations] --> B{Input Parameters Valid?}
    B -->|Yes| C[Return (name, summary, batch)]
    C --> D[End]
```

## Examples:
```python
# Basic usage
name = "url_validation"
summary = {"count": 100, "valid": 95}
batch = [{"url": "http://example.com"}, {"url": "https://google.com"}]

result = url_expectations(name, summary, batch)
# Returns: ("url_validation", {"count": 100, "valid": 95}, [{"url": "http://example.com"}, {"url": "https://google.com"}])
```

## `src.ydata_profiling.model.expectation_algorithms.file_expectations` · *function*

## Summary:
Validates that a specified file exists within a batch using Great Expectations and returns the validation results.

## Description:
This function serves as an expectation algorithm that verifies file existence within a Great Expectations batch. It's designed to be part of a pipeline for validating data files during profiling operations. The function follows a standard pattern where expectation algorithms take input parameters, perform validation, and return the validated data along with associated metadata.

## Args:
    name (str): The name or path of the file to validate for existence.
    summary (dict): A dictionary containing summary information about the file being validated.
    batch (Any): A Great Expectations batch object that contains the file validation methods.
    *args: Additional positional arguments that may be passed to the expectation function.

## Returns:
    Tuple[str, dict, Any]: A tuple containing:
        - name (str): The original file name passed as input
        - summary (dict): The original summary dictionary passed as input
        - batch (Any): The original batch object passed as input

## Raises:
    None explicitly documented - however, the underlying `batch.expect_file_to_exist(name)` call may raise exceptions if the file validation fails or if the batch object doesn't support this method.

## Constraints:
    Preconditions:
        - The batch parameter must be a Great Expectations batch object that implements the `expect_file_to_exist` method
        - The name parameter must be a valid string representing a file path or name
    Postconditions:
        - The file existence expectation is added to the batch's validation suite
        - All input parameters are returned unchanged

## Side Effects:
    - Calls the `expect_file_to_exist` method on the batch object, which likely adds validation expectations to the batch's expectation suite
    - May trigger I/O operations when the batch processes the expectation (depending on the batch implementation)

## Control Flow:
```mermaid
flowchart TD
    A[Start file_expectations] --> B{batch.expect_file_to_exist(name)}
    B --> C[Return (name, summary, batch)]
```

## Examples:
```python
# Typical usage in a profiling pipeline
name = "data.csv"
summary = {"size": 1024, "type": "csv"}
batch = create_batch_from_file("data.csv")

result_name, result_summary, result_batch = file_expectations(name, summary, batch)
# Returns: ("data.csv", {"size": 1024, "type": "csv"}, batch_with_expectation)
```

