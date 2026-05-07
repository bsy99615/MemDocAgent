# `missing_inds.py`

## `hypertools.tools.missing_inds.missing_inds` · *function*

## Summary:
Identifies indices of missing (NaN) values in array-like data structures.

## Description:
Finds positions of NaN values within input arrays and returns their indices. When multiple arrays are provided, it returns a list of index arrays. This function processes input data through the format_data function (when format_data=True) and handles both single and multiple array inputs.

## Args:
    x: Input data which can be a single array or list of arrays containing numeric data with potential NaN values.
    format_data (bool): Flag indicating whether to apply data formatting before processing using format_data function. Defaults to True.

## Returns:
    list or array or None: For multiple input arrays, returns a list where each element corresponds to the indices of NaN values in each array. For single input array, returns the indices directly. Returns None for arrays with no missing values.

## Raises:
    None explicitly raised in the current implementation.

## Constraints:
    Preconditions:
    - Input x should be compatible with numpy operations
    - When format_data=True, input should be compatible with the format_data function
    
    Postconditions:
    - Output indices are zero-based
    - Returns None for arrays without missing values
    - Returns single array or list of arrays based on input size

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start missing_inds] --> B{format_data?}
    B -- Yes --> C[Apply format_data(x, ppca=False)]
    B -- No --> C
    C --> D[Initialize inds list]
    D --> E[Iterate through arrays in x]
    E --> F{Any NaN in array?}
    F -- No --> G[Append None to inds]
    F -- Yes --> H[Find NaN indices with argwhere]
    H --> I[Extract column 0 indices]
    I --> J[Append to inds]
    J --> K[Check length of inds]
    K -- >1 --> L[Return inds list]
    K -- =1 --> M[Return inds[0]]
```

## Examples:
    # Single array with missing values
    data = np.array([1.0, np.nan, 3.0, np.nan])
    result = missing_inds(data)
    # Returns array([1, 3])
    
    # Multiple arrays with missing values
    data1 = np.array([1.0, np.nan, 3.0])
    data2 = np.array([np.nan, 2.0, 3.0])
    result = missing_inds([data1, data2])
    # Returns [array([1]), array([0])]
    
    # Array with no missing values
    data = np.array([1.0, 2.0, 3.0])
    result = missing_inds(data)
    # Returns None

