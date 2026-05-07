# `df2mat.py`

## `hypertools.tools.df2mat.df2mat` · *function*

## Summary:
Converts a pandas DataFrame with mixed data types into a numerical matrix suitable for visualization, automatically encoding categorical columns as dummy variables.

## Description:
This function transforms a pandas DataFrame containing both numerical and categorical data into a purely numerical matrix that can be used for plotting and data visualization. It separates object-type columns (categorical data) from numerical columns, then converts each categorical column into multiple binary dummy variables using pandas' get_dummies function. This ensures that categorical data can be properly visualized without assuming ordinal relationships between categories.

## Args:
    data (pandas.DataFrame): Input DataFrame containing mixed data types including both numerical and categorical columns
    return_labels (bool): Optional flag indicating whether to return column labels along with the numerical matrix. Defaults to False

## Returns:
    numpy.ndarray or tuple: If return_labels=False, returns a numpy.ndarray containing only numerical values. If return_labels=True, returns a tuple of (numpy.ndarray, list) where the first element is the numerical matrix and the second element is a list of column labels.

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
    - Input data must be a valid pandas DataFrame
    - All columns in the DataFrame should be compatible with pandas operations
    
    Postconditions:
    - Output matrix contains only numerical values
    - Categorical columns are converted to dummy variables
    - Column order is preserved from the original DataFrame

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start df2mat] --> B{Has object columns?}
    B -- Yes --> C[Separate object columns]
    B -- No --> C
    C --> D[Separate numeric columns]
    D --> E{Has object columns?}
    E -- Yes --> F[Process each object column]
    F --> G[Apply get_dummies to each object column]
    G --> H[Join dummy variables to numeric data]
    H --> I[Extract values as numpy array]
    I --> J[Get column labels]
    J --> K{return_labels=True?}
    K -- Yes --> L[Return (plot_data, labels)]
    K -- No --> M[Return plot_data]
    E -- No --> N[Extract values as numpy array]
    N --> O[Get column labels]
    O --> P{return_labels=True?}
    P -- Yes --> Q[Return (plot_data, labels)]
    P -- No --> R[Return plot_data]
```

## Examples:
    # Basic usage
    import pandas as pd
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
    matrix = df2mat(df)
    # Returns numpy array [[1, 1, 0, 0], [2, 0, 1, 0], [3, 0, 0, 1]]
    
    # With labels returned
    matrix, labels = df2mat(df, return_labels=True)
    # matrix: numpy array with dummy variables
    # labels: ['A', 'B_x', 'B_y', 'B_z']

