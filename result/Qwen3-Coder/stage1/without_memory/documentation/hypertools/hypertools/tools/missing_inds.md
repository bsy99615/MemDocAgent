# `missing_inds.py`

## `hypertools.tools.missing_inds.missing_inds` · *function*

## Summary:
Identifies and returns the indices of missing (NaN) values in input arrays.

## Description:
This function processes input data to locate positions of missing values (NaN entries) within arrays. It can optionally preprocess the input data using a formatting function before identifying missing indices. The function handles both single arrays and collections of arrays, returning appropriate data structures based on input length.

**Important Implementation Notes**: 
- The current implementation contains two critical bugs:
  1. Uses `np.argwhere()` but imports `numpy` as `import numpy` (should be `import numpy as np`)
  2. References undefined `formatter` function instead of `format_data` function

## Args:
    x: Input data that can be a single array or collection of arrays containing potential NaN values
    format_data (bool): When True, applies preprocessing to the input data using `format_data` function. Defaults to True.

## Returns:
    When input contains multiple arrays: list of arrays, where each array contains indices of NaN values for the corresponding input array. When input contains a single array: array of indices of NaN values, or None if no NaN values exist.

## Raises:
    None explicitly raised in the provided code

## Constraints:
    Preconditions:
    - Input x should be compatible with numpy operations
    - If format_data is True, the `format_data` function must be available (note: this is currently broken due to undefined `formatter` reference)
    
    Postconditions:
    - Returns None for arrays with no missing values
    - Returns indices as numpy arrays for arrays with missing values
    - Returns appropriate structure based on input size

## Side Effects:
    None explicitly mentioned

## Control Flow:
```mermaid
flowchart TD
    A[Start missing_inds] --> B{format_data?}
    B -- Yes --> C[Call format_data(x, ppca=False)]
    B -- No --> D[Skip formatting]
    C --> E[Initialize inds list]
    D --> E
    E --> F[Iterate through arrays in x]
    F --> G{Any NaN in array?}
    G -- No --> H[Append None to inds]
    G -- Yes --> I[Find NaN indices with np.argwhere]
    I --> J[Append indices to inds]
    H --> K
    J --> K
    K --> L{Length of inds > 1?}
    L -- Yes --> M[Return inds list]
    L -- No --> N[Return inds[0]]
```

## Examples:
    # Single array with missing values
    data = np.array([1.0, np.nan, 3.0, np.nan])
    result = missing_inds(data)  # Returns array([1, 3])
    
    # Multiple arrays with missing values
    data1 = np.array([1.0, np.nan, 3.0])
    data2 = np.array([np.nan, 2.0, 3.0])
    result = missing_inds([data1, data2])  # Returns [array([1]), array([0])]
    
    # Single array with no missing values
    data = np.array([1.0, 2.0, 3.0])
    result = missing_inds(data)  # Returns None

