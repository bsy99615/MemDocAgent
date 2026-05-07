# `utils_pandas.py`

## `src.ydata_profiling.model.pandas.utils_pandas.weighted_median` · *function*

## Summary:
Computes the weighted median of a dataset given values and their corresponding weights.

## Description:
Calculates the weighted median by sorting the data and weights, then finding the value at which the cumulative sum of weights reaches half the total weight. This function is used in statistical analysis to find a representative value that accounts for varying importance of data points.

## Args:
    data (np.ndarray): Array of numerical values to calculate median for
    weights (np.ndarray): Array of weights corresponding to each data point

## Returns:
    float: The weighted median value (can be float or int depending on calculation)

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Both data and weights must be convertible to numpy arrays
    - Data and weights arrays must have the same length
    
    Postconditions:
    - Returns a value that represents the weighted median of the input data

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
    I --> J{max weight > midpoint?}
    J -- Yes --> K[Find data point with max weight]
    J -- No --> L[Calculate cumulative weights]
    L --> M[Find index where cumsum <= midpoint]
    M --> N{cumsum at index == midpoint?}
    N -- Yes --> O[Return mean of two adjacent data points]
    N -- No --> P[Return next data point]
    K --> Q[Return result]
    O --> Q
    P --> Q
```

## Examples:
    # Basic usage
    data = np.array([1, 2, 3, 4, 5])
    weights = np.array([1, 1, 1, 1, 1])
    result = weighted_median(data, weights)  # Returns 3
    
    # Weighted case
    data = np.array([1, 2, 3, 4, 5])
    weights = np.array([1, 1, 2, 1, 1])
    result = weighted_median(data, weights)  # Returns 3 (weighted median)

