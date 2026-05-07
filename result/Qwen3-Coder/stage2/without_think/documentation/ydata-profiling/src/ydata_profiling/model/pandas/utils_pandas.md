# `utils_pandas.py`

## `src.ydata_profiling.model.pandas.utils_pandas.weighted_median` · *function*

## Summary:
Computes the weighted median of a dataset given values and their corresponding weights.

## Description:
Calculates the weighted median by sorting the data and weights, then finding the value at which the cumulative sum of weights reaches half the total weight. This function is used to find a representative central value that accounts for the importance (weight) of each data point.

## Args:
    data (np.ndarray): Array of numerical values for which to compute the weighted median.
    weights (np.ndarray): Array of weights corresponding to each data point. Must be the same length as data.

## Returns:
    float: The weighted median value. May be an integer or float depending on the calculation.

## Raises:
    None explicitly raised, but may raise numpy-related exceptions if inputs are invalid.

## Constraints:
    Preconditions:
        - Both data and weights must be convertible to numpy arrays
        - Data and weights arrays must have the same length
        - Weights should be non-negative values (though negative weights are technically allowed)
    
    Postconditions:
        - Returns a value that represents the weighted median of the input data
        - The returned value corresponds to a data point in the sorted array

## Side Effects:
    None

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
    I --> J{max(weights) > midpoint?}
    J -- Yes --> K[Find data point with max weight]
    J -- No --> L[Calculate cumulative weights]
    L --> M[Find index where cumsum <= midpoint]
    M --> N{cumsum[index] == midpoint?}
    N -- Yes --> O[Return mean of two adjacent data points]
    N -- No --> P[Return next data point]
    K --> Q[Return result]
    O --> Q
    P --> Q
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

