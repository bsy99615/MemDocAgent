# `imbalance_pandas.py`

## `src.ydata_profiling.model.pandas.imbalance_pandas.column_imbalance_score` · *function*

## Summary:
Calculates the imbalance score for a categorical column distribution using entropy-based normalization.

## Description:
Computes a normalized entropy score that quantifies how imbalanced a categorical distribution is. The score ranges from 0 (perfectly balanced) to 1 (completely imbalanced), making it useful for identifying skewed distributions in data profiling.

## Args:
    value_counts (pd.Series): A pandas Series containing the count of occurrences for each category/class in a column
    n_classes (int): The total number of unique classes/categories in the column

## Returns:
    Union[float, int]: Imbalance score between 0 and 1, where 0 indicates perfect balance and 1 indicates complete imbalance. Returns 0 when n_classes <= 1.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - value_counts should be a pandas Series with numeric values
    - n_classes must be a positive integer
    - value_counts should represent counts for all classes (not probabilities)
    
    Postconditions:
    - Returns a value in the range [0, 1]
    - Returns 0 when n_classes <= 1

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start column_imbalance_score] --> B{Is n_classes > 1?}
    B -- Yes --> C[Convert value_counts to numpy array]
    C --> D[Calculate entropy with base 2]
    D --> E[Normalize by log2(n_classes)]
    E --> F[Return 1 - (entropy / log2(n_classes))]
    B -- No --> G[Return 0]
```

## Examples:
    # Perfectly balanced distribution
    >>> value_counts = pd.Series([50, 50, 50])
    >>> column_imbalance_score(value_counts, 3)
    0.0
    
    # Completely imbalanced distribution  
    >>> value_counts = pd.Series([100, 0, 0])
    >>> column_imbalance_score(value_counts, 3)
    1.0
    
    # Single class (edge case)
    >>> value_counts = pd.Series([50, 50, 50])
    >>> column_imbalance_score(value_counts, 1)
    0
```

