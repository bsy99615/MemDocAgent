# `missing_inds.py`

## `hypertools.tools.missing_inds.missing_inds` · *function*

## Summary:
Identifies indices of missing (NaN) values in arrays within a dataset.

## Description:
Processes input data to locate positions of missing values (NaN entries) in each array. When format_data is enabled, applies preprocessing to the input data before identifying missing indices. Returns either a single array of missing indices or a list of such arrays depending on input structure.

## Args:
    x: Input data containing arrays that may have missing values. Can be a single array or list of arrays.
    format_data (bool): Whether to apply preprocessing to the input data. Defaults to True.

## Returns:
    None or array-like: If input contains multiple arrays, returns a list where each element corresponds to missing indices for that array. If input contains a single array, returns the missing indices directly. Returns None for arrays with no missing values.

## Raises:
    None explicitly raised in the provided code.

## Constraints:
    Preconditions:
    - Input x should be compatible with numpy operations
    - Arrays in x should support numpy.nan operations
    
    Postconditions:
    - Returns None for arrays without missing values
    - Returns indices as 1D arrays for arrays with missing values
    - Returns list of results when multiple arrays are processed

## Side Effects:
    None explicitly mentioned in the provided code.

## Control Flow:
```mermaid
flowchart TD
    A[Start missing_inds] --> B{format_data enabled?}
    B -->|Yes| C[Call formatter(x, ppca=False)]
    B -->|No| D[Skip formatting]
    C --> E[Initialize inds list]
    D --> E
    E --> F[Iterate through arrays in x]
    F --> G{Any NaN in array?}
    G -->|No| H[Append None to inds]
    G -->|Yes| I[Find NaN indices with np.argwhere(np.isnan(arr))[:,0]]
    F --> J[End iteration]
    J --> K{inds length > 1?}
    K -->|Yes| L[Return inds list]
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
    
    # Array without missing values
    data = np.array([1.0, 2.0, 3.0])
    result = missing_inds(data)  # Returns None

