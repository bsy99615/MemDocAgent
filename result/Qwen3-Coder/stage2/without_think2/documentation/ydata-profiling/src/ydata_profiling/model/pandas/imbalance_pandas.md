# `imbalance_pandas.py`

## `src.ydata_profiling.model.pandas.imbalance_pandas.column_imbalance_score` · *function*

## Summary:
Calculates the imbalance score for a categorical column based on its value distribution using entropy normalization.

## Description:
Computes a normalized entropy-based score that quantifies how evenly distributed the values are in a categorical column. Lower scores indicate higher imbalance, while scores near 1 indicate uniform distribution. This function is used to identify columns with skewed value distributions that may require special handling in data analysis.

## Args:
    value_counts (pd.Series): A pandas Series containing the count of each unique value in the column, indexed by the unique values themselves.
    n_classes (int): The total number of unique classes/categories in the column.

## Returns:
    Union[float, int]: A float value between 0 and 1 representing the imbalance score. Returns 0 when n_classes <= 1 (no meaningful imbalance calculation possible).

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - value_counts must be a pandas Series with numeric values
        - n_classes must be a positive integer
    Postconditions:
        - Returns a value in the range [0, 1]
        - When n_classes <= 1, returns exactly 0

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{Is n_classes > 1?}
    B -- Yes --> C[Convert value_counts to numpy array]
    C --> D[Calculate entropy with base 2]
    D --> E[Divide by log2(n_classes)]
    E --> F[Subtract from 1]
    F --> G[Return result]
    B -- No --> H[Return 0]
    G --> I[End]
    H --> I
```

## Examples:
```python
import pandas as pd
from scipy.stats import entropy
from numpy import log2

# Example 1: Balanced distribution
value_counts = pd.Series([50, 50, 50], index=['A', 'B', 'C'])
n_classes = 3
score = column_imbalance_score(value_counts, n_classes)
# Result: ~0.0 (highly balanced - low entropy)

# Example 2: Imbalanced distribution  
value_counts = pd.Series([90, 5, 5], index=['A', 'B', 'C'])
n_classes = 3
score = column_imbalance_score(value_counts, n_classes)
# Result: ~0.73 (highly imbalanced - high entropy)

# Example 3: Single class
value_counts = pd.Series([100], index=['A'])
n_classes = 1
score = column_imbalance_score(value_counts, n_classes)
# Result: 0 (no imbalance possible due to single class)
```

