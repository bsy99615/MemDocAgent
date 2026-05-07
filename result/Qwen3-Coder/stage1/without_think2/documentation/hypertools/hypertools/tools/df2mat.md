# `df2mat.py`

## `hypertools.tools.df2mat.df2mat` · *function*

## Summary:
Converts a pandas DataFrame with mixed data types into a numerical matrix suitable for plotting, optionally returning column labels.

## Description:
This function transforms a pandas DataFrame containing both numerical and categorical columns into a purely numerical matrix by converting categorical columns into dummy/indicator variables. It's designed to prepare data for visualization tools that require numerical input. The function separates string/object columns from numerical columns, converts each string column into binary dummy variables, and combines them into a single numerical matrix.

## Args:
    data (pandas.DataFrame): Input DataFrame containing mixed data types including object/string and numerical columns.
    return_labels (bool): Flag indicating whether to return column labels along with the numerical matrix. Defaults to False.

## Returns:
    numpy.ndarray or tuple: If return_labels is False, returns a numpy array containing the numerical matrix. If return_labels is True, returns a tuple of (numpy.ndarray, list) where the first element is the numerical matrix and the second element is a list of column labels.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
        - Input data must be a valid pandas DataFrame
        - Data may contain mixed data types including object/string and numerical columns
    
    Postconditions:
        - Output matrix contains only numerical values
        - Categorical columns are converted to dummy variables
        - Column order preserves original numerical columns followed by dummy variables

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start df2mat] --> B[Select object columns with select_dtypes(include=['object'])]
    B --> C[Select numerical columns with select_dtypes(exclude=['object'])]
    C --> D[For each object column]
    D --> E[Create dummy variables using pd.get_dummies]
    E --> F[Join dummies to numerical data]
    F --> G[Extract values as numpy array]
    G --> H{return_labels flag}
    H -- True --> I[Return (matrix, labels)]
    H -- False --> J[Return matrix]
```

## Examples:
    # Basic usage
    import pandas as pd
    data = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
    matrix = df2mat(data)
    # Returns: array([[1, 1, 0, 0], [2, 0, 1, 0], [3, 0, 0, 1]])
    
    # With labels
    matrix, labels = df2mat(data, return_labels=True)
    # Returns: (array([[1, 1, 0, 0], [2, 0, 1, 0], [3, 0, 0, 1]]), ['A', 'B_x', 'B_y', 'B_z'])
```

