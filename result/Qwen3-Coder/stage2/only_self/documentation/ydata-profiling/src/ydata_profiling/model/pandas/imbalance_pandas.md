# `imbalance_pandas.py`

## `src.ydata_profiling.model.pandas.imbalance_pandas.column_imbalance_score` · *function*

## Summary:
Computes the imbalance score for a categorical column based on the distribution of values using entropy-based normalization.

## Description:
Calculates a normalized entropy score that quantifies how evenly distributed the values are in a categorical column. Lower scores indicate more balanced distributions, while higher scores indicate greater imbalance. This function is used in profiling to identify columns with skewed value distributions that may require special attention.

## Args:
    value_counts (pd.Series): A pandas Series containing the count of each unique value in the column, typically obtained from value_counts() method
    n_classes (int): The total number of unique classes/categories in the column

## Returns:
    Union[float, int]: A value between 0 and 1 representing the imbalance score. Returns 0 when n_classes <= 1 (no meaningful imbalance calculation possible)

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - value_counts should contain non-negative integers representing counts
    - n_classes should be a positive integer
    - When n_classes <= 1, the function returns 0 without processing
    
    Postconditions:
    - Returns a value in the range [0, 1]
    - For perfectly uniform distribution, returns 0 (least imbalance)
    - For highly skewed distribution, approaches 1 (most imbalance)

## Side Effects:
    None

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
    # Example 1: Perfectly balanced distribution
    value_counts = pd.Series([5, 5, 5, 5])  # 4 classes with equal counts
    n_classes = 4
    score = column_imbalance_score(value_counts, n_classes)  # Returns ~0.0 (balanced)
    
    # Example 2: Highly imbalanced distribution  
    value_counts = pd.Series([90, 5, 3, 2])  # 4 classes with very unequal counts
    n_classes = 4
    score = column_imbalance_score(value_counts, n_classes)  # Returns ~0.8+ (imbalanced)
    
    # Example 3: Single class
    value_counts = pd.Series([100])
    n_classes = 1
    score = column_imbalance_score(value_counts, n_classes)  # Returns 0 (no imbalance possible)
```

