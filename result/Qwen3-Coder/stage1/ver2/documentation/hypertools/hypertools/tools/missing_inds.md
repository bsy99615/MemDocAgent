# `missing_inds.py`

## `hypertools.tools.missing_inds.missing_inds` · *function*

## Summary:
Identifies and returns the indices of missing (NaN) values in arrays within a dataset.

## Description:
Processes input data to locate positions of missing values (NaN entries) across arrays. When format_data is enabled, the input is preprocessed through the format_data function before analysis. The function returns either a single array of missing indices or a list of arrays, depending on whether the input contains multiple arrays. This function is commonly used in data preprocessing pipelines to identify patterns of missing data that may require imputation or removal before further analysis.

This function is extracted from the main processing pipeline to provide a reusable utility for missing data identification. It encapsulates the logic for detecting NaN values and returning their positional indices, which is useful for downstream data cleaning operations.

Note: There appears to be a bug in the source code where formatter is called instead of format_data, which would cause a NameError at runtime.

## Args:
    x: Input data containing arrays that may have missing values. Can be a single array or list of arrays.
    format_data (bool): Flag indicating whether to preprocess input data using format_data function. Defaults to True.

## Returns:
    list or array or None: If input contains multiple arrays, returns a list where each element corresponds to missing indices for that array. If input contains a single array, returns the missing indices directly as an array, or None if no missing values exist.

## Raises:
    None explicitly raised in the provided code.

## Constraints:
    Preconditions:
    - Input x should be compatible with numpy operations (arrays or lists of arrays)
    - When format_data=True, input should be compatible with the format_data preprocessing pipeline
    
    Postconditions:
    - Returns None for arrays with no missing values
    - Returns array of indices for arrays with missing values
    - Returns list of results when multiple arrays are processed

## Side Effects:
    None explicitly mentioned in the provided code.

## Control Flow:
```mermaid
flowchart TD
    A[Start missing_inds] --> B{format_data=True?}
    B -->|Yes| C[Apply format_data to x]
    B -->|No| D[Skip formatting]
    C --> D
    D --> E[Initialize inds = []]
    E --> F[For each array in x]
    F --> G{Any NaN values?}
    G -->|No| H[Append None to inds]
    G -->|Yes| I[Find NaN indices and append to inds]
    H --> J
    I --> J
    J --> K{len(inds) > 1?}
    K -->|Yes| L[Return inds (list)]
    K -->|No| M[Return inds[0]]
```

## Examples:
    # Single array with missing values
    data = np.array([1.0, np.nan, 3.0, np.nan])
    result = missing_inds(data)  # Returns array([1, 3])
    
    # Multiple arrays with missing values
    data1 = np.array([1.0, np.nan, 3.0])
    data2 = np.array([np.nan, 2.0, 3.0])
    result = missing_inds([data1, data2])  # Returns [array([1]), array([0])]
    
    # Array with no missing values
    data = np.array([1.0, 2.0, 3.0])
    result = missing_inds(data)  # Returns None
    
    # Using with format_data disabled
    result = missing_inds(data, format_data=False)

