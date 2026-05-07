# `df2mat.py`

## `hypertools.tools.df2mat.df2mat` · *function*

## Summary:
Converts a pandas DataFrame with mixed data types into a numerical matrix by transforming categorical columns into dummy variables.

## Description:
This function processes a pandas DataFrame by separating categorical (object) columns from numerical columns, then converts all categorical columns into binary dummy variables using pandas get_dummies. The resulting numerical matrix is suitable for machine learning algorithms and data visualization tools. This extraction allows for clean separation of data preprocessing logic from downstream analysis pipelines.

## Args:
    data (pandas.DataFrame): Input DataFrame containing mixed data types including categorical and numerical columns
    return_labels (bool): Optional flag indicating whether to return column labels along with the numerical matrix. Defaults to False

## Returns:
    numpy.ndarray or tuple: If return_labels=False, returns a numpy array containing the numerical matrix. If return_labels=True, returns a tuple of (numpy.ndarray, list) where the first element is the numerical matrix and the second element is a list of column labels.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
        - Input data must be a valid pandas DataFrame
        - All columns in the DataFrame should be compatible with pandas operations
    
    Postconditions:
        - Output matrix contains only numerical values
        - Categorical columns are converted to binary dummy variables
        - Column order is preserved from original DataFrame

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start df2mat] --> B{Data has object columns?}
    B -->|Yes| C[Separate object columns]
    B -->|No| C
    C --> D[Separate numeric columns]
    D --> E[Process each object column]
    E --> F{Has more object columns?}
    F -->|Yes| G[Apply get_dummies]
    G --> H[Join with numeric data]
    F -->|No| H
    H --> I[Extract values as numpy array]
    I --> J[Get column labels]
    J --> K{return_labels=True?}
    K -->|Yes| L[Return (matrix, labels)]
    K -->|No| M[Return matrix]
```

## Examples:
```python
import pandas as pd
import numpy as np

# Basic usage
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': ['x', 'y', 'z'],
    'C': [10.5, 20.3, 30.1]
})
matrix = df2mat(df)
print(matrix)
# Output: [[1.  1.  0.  0.]
#          [2.  0.  1.  0.]
#          [3.  0.  0.  1.]]

# With labels returned
matrix, labels = df2mat(df, return_labels=True)
print(labels)
# Output: ['A', 'B_x', 'B_y', 'B_z']
```

