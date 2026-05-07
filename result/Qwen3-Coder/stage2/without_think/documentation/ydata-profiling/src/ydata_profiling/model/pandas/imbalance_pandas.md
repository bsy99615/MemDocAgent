# `imbalance_pandas.py`

## `src.ydata_profiling.model.pandas.imbalance_pandas.column_imbalance_score` · *function*

## Summary:
Computes the imbalance score for a categorical column based on the distribution of class frequencies using entropy-based normalization.

## Description:
This function calculates an imbalance score that quantifies how evenly distributed the classes are in a categorical column. The score ranges from 0 (perfectly balanced) to 1 (completely imbalanced), making it useful for identifying columns with skewed class distributions that might affect model performance.

The function is designed to be used in profiling pipelines where understanding data distribution characteristics is important for data quality assessment and preprocessing decisions.

## Args:
    value_counts (pd.Series): A pandas Series containing the frequency counts of each class in the column. The index represents the class labels and values represent their counts.
    n_classes (int): The total number of unique classes in the column. Must be a positive integer greater than 0.

## Returns:
    Union[float, int]: Returns 0 when n_classes <= 1 (no meaningful imbalance calculation possible). When n_classes > 1, returns a float value between 0 and 1 representing the normalized entropy-based imbalance score, where 0 indicates perfect balance and 1 indicates maximum imbalance.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - value_counts should be a pandas Series with numeric values representing class frequencies
    - n_classes must be a positive integer
    - When n_classes > 1, value_counts should contain at least one non-zero count
    
    Postconditions:
    - Returns 0 when n_classes <= 1
    - Returns a value in the range [0, 1] when n_classes > 1
    - The result represents a normalized entropy score where higher values indicate greater imbalance

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Is n_classes > 1?}
    B -- No --> C[Return 0]
    B -- Yes --> D[Convert value_counts to numpy array]
    D --> E[Calculate entropy(value_counts, base=2)]
    E --> F[Calculate log2(n_classes)]
    F --> G[Divide entropy by log2(n_classes)]
    G --> H[Subtract from 1]
    H --> I[Return result]
```

## Examples:
    # Perfectly balanced distribution
    >>> value_counts = pd.Series([50, 50, 50])
    >>> column_imbalance_score(value_counts, 3)
    0.0
    
    # Imbalanced distribution  
    >>> value_counts = pd.Series([90, 5, 5])
    >>> column_imbalance_score(value_counts, 3)
    0.736...
    
    # Single class (edge case)
    >>> value_counts = pd.Series([100])
    >>> column_imbalance_score(value_counts, 1)
    0
```

