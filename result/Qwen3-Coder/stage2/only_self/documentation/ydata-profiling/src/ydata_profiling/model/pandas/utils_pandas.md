# `utils_pandas.py`

## `src.ydata_profiling.model.pandas.utils_pandas.weighted_median` · *function*

## Summary:
Computes the weighted median of a dataset given values and their corresponding weights.

## Description:
Calculates the weighted median by sorting the data and weights, then finding the value at which the cumulative weight reaches half of the total weight. This function is used in statistical analysis to find a representative central value that accounts for varying importance of observations.

## Args:
    data (np.ndarray): Array of numerical values for which to compute the weighted median
    weights (np.ndarray): Array of weights corresponding to each data point, must be non-negative

## Returns:
    float: The weighted median value. The result may be a float even when input arrays contain integers.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - Both data and weights must be convertible to numpy arrays
    - Weights should be non-negative values
    - Data and weights arrays must have the same length
    
    Postconditions:
    - Returns a value that represents the weighted median of the input data
    - The returned value corresponds to a data point where cumulative weight reaches or exceeds half the total weight

## Side Effects:
    None

## Control Flow:
    ```mermaid
    flowchart TD
        A[Start weighted_median] --> B{data is ndarray?}
        B -- No --> C[Convert data to ndarray]
        B -- Yes --> D[Skip data conversion]
        C --> D
        D --> E{weights is ndarray?}
        E -- No --> F[Convert weights to ndarray]
        E -- Yes --> G[Skip weights conversion]
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
        Q[End]
    ```

## Examples:
    # Basic usage with numpy arrays
    data = np.array([1, 2, 3, 4, 5])
    weights = np.array([1, 1, 1, 1, 1])
    result = weighted_median(data, weights)  # Returns 3
    
    # Usage with different weights
    data = np.array([10, 20, 30])
    weights = np.array([1, 2, 3])
    result = weighted_median(data, weights)  # Returns 30
    
    # Usage with floating point data
    data = np.array([1.5, 2.5, 3.5])
    weights = np.array([1, 2, 3])
    result = weighted_median(data, weights)  # Returns 3.5

