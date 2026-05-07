# `df2mat.py`

## `hypertools.tools.df2mat.df2mat` · *function*

## Summary:
Converts a pandas DataFrame into a numerical matrix by transforming categorical columns into dummy variables.

## Description:
This function transforms a mixed-type DataFrame (containing both numerical and categorical columns) into a purely numerical matrix suitable for machine learning or visualization tasks. Categorical columns (object dtype) are converted to dummy variables using pandas' get_dummies function, while numerical columns are preserved as-is. The function provides flexibility to also return column labels for the resulting matrix.

## Args:
    data (pandas.DataFrame): Input DataFrame containing mixed data types including object/categorical and numerical columns
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
    - Categorical columns are properly encoded as dummy variables
    - Column order in output preserves original column order with dummy variables appended

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start df2mat] --> B{Data has object columns?}
    B -->|Yes| C[Separate object columns]
    B -->|No| D[Skip object processing]
    C --> E[Process each object column]
    E --> F[Apply pd.get_dummies]
    F --> G[Join dummy variables to numeric data]
    G --> H[Extract numerical values]
    H --> I{Return labels requested?}
    I -->|Yes| J[Return (matrix, labels)]
    I -->|No| K[Return matrix only]
```

## Examples:
```python
import pandas as pd
import numpy as np

# Basic usage
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': ['x', 'y', 'z'],
    'C': [10.0, 20.0, 30.0]
})

# Convert to matrix only
matrix = df2mat(df)
print(matrix)
# Output: [[1. 1. 0. 0. 10.]
#          [2. 0. 1. 0. 20.]
#          [3. 0. 0. 1. 30.]]

# Convert to matrix with labels
matrix, labels = df2mat(df, return_labels=True)
print(labels)
# Output: ['A', 'B_x', 'B_y', 'B_z', 'C']
```

