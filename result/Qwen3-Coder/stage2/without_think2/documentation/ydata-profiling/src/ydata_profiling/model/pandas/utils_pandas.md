# `utils_pandas.py`

## `src.ydata_profiling.model.pandas.utils_pandas.weighted_median` · *function*

## Summary:
Computes the weighted median of a dataset given values and their corresponding weights.

## Description:
Calculates the weighted median by sorting the data and weights, then finding the value at which the cumulative weight reaches half of the total weight. This function handles special cases where the maximum weight exceeds half the total weight.

## Args:
    data (np.ndarray): Array of numerical values for which to compute the weighted median.
    weights (np.ndarray): Array of weights corresponding to each value in data. Must be the same length as data.

## Returns:
    Union[int, float]: The weighted median value. May return an integer or float depending on whether the result is computed as a mean of two values.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Both data and weights must be convertible to numpy arrays.
        - Data and weights arrays must have the same length.
    Postconditions:
        - Returns a single numeric value representing the weighted median.
        - The returned value is either from the original data array or the mean of two adjacent values.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start weighted_median] --> B{data is ndarray?}
    B -- No --> C[Convert data to ndarray]
    B -- Yes --> D[Skip conversion]
    C --> D
    D --> E{weights is ndarray?}
    E -- No --> F[Convert weights to ndarray]
    E -- Yes --> G[Skip conversion]
    F --> G
    G --> H[Sort data and weights]
    H --> I[Calculate midpoint = 0.5 * sum(weights)]
    I --> J{max weight > midpoint?}
    J -- Yes --> K[Find data value with max weight]
    J -- No --> L[Calculate cumulative weights]
    K --> M[Return data value with max weight]
    L --> N[Find index where cumsum <= midpoint]
    N --> O{cumsum at index == midpoint?}
    O -- Yes --> P[Return mean of two adjacent data values]
    O -- No --> Q[Return next data value]
    P --> R[Return weighted median]
    Q --> R
    M --> R
```

## Examples:
    >>> import numpy as np
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> weights = np.array([1, 1, 1, 1, 1])
    >>> weighted_median(data, weights)
    3
    
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> weights = np.array([1, 1, 2, 1, 1])
    >>> weighted_median(data, weights)
    3
    
    >>> data = np.array([1, 2, 3, 4])
    >>> weights = np.array([1, 1, 1, 1])
    >>> weighted_median(data, weights)
    2.5

