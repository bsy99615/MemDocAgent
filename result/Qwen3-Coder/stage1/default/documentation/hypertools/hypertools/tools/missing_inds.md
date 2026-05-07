# `missing_inds.py`

## `hypertools.tools.missing_inds.missing_inds` · *function*

## Summary:
Finds indices of missing (NaN) values in arrays of data.

## Description:
Identifies positions of missing values (NaN) within input arrays. This function can optionally preprocess input data using the format_data function before searching for missing values. It's commonly used in data preprocessing pipelines where missing value detection is required.

## Args:
    x: Input data which can be a single array, list of arrays, or other data structures that will be formatted
    format_data (bool): When True, applies data formatting using format_data function before processing. Defaults to True.

## Returns:
    If multiple arrays are provided, returns a list where each element corresponds to the indices of missing values in each array. If a single array is provided, returns the indices of missing values directly as a numpy array or None if no missing values exist.

## Raises:
    None explicitly raised in the provided code

## Constraints:
    Preconditions:
    - Input x should be compatible with the format_data function
    - Arrays in x should be numpy arrays or array-like objects
    
    Postconditions:
    - Returns either None, a numpy array of indices, or a list of such arrays
    - All returned indices correspond to positions of NaN values in the input arrays

## Side Effects:
    None explicitly mentioned

## Control Flow:
```mermaid
flowchart TD
    A[Start missing_inds] --> B{format_data is True?}
    B -- Yes --> C[Call formatter(x, ppca=False)] 
    B -- No --> D[Skip formatting]
    C --> E[Process each array in x]
    D --> E
    E --> F{Array has NaN values?}
    F -- No --> G[Append None to inds]
    F -- Yes --> H[Find NaN indices with np.argwhere(np.isnan(arr))[:,0]]
    H --> I[Append indices to inds]
    G --> J
    I --> J
    J --> K{len(inds) > 1?}
    K -- Yes --> L[Return inds list]
    K -- No --> M[Return inds[0]]
```

## Examples:
    # Find missing indices in a single array
    data = np.array([1.0, np.nan, 3.0, np.nan])
    missing_indices = missing_inds(data)
    # Returns: array([1, 3])
    
    # Find missing indices in multiple arrays
    data1 = np.array([1.0, np.nan, 3.0])
    data2 = np.array([np.nan, 2.0, 3.0])
    missing_indices = missing_inds([data1, data2])
    # Returns: [array([1]), array([0])]
```

