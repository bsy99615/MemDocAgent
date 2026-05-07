# `describe.py`

## `hypertools.tools.describe.describe` · *function*

## Summary:
Analyzes dimensionality reduction performance by computing correlations between original and reduced data representations across varying numbers of components.

## Description:
This function evaluates how well different dimensionality reduction techniques preserve the structural relationships in data by comparing correlation matrices between original and reduced representations. It's designed to help determine optimal numbers of components for dimensionality reduction tasks.

The function is typically called during exploratory data analysis to understand how much information is retained when reducing data dimensions. It's commonly used in machine learning workflows when selecting appropriate embedding dimensions.

## Args:
    x: Input data to analyze, typically a numpy array or list of arrays
    reduce (str, optional): Dimensionality reduction technique to use. Defaults to 'IncrementalPCA'
    max_dims (int, optional): Maximum number of dimensions to test. If None, automatically determined based on data shape
    show (bool, optional): Whether to display a plot of correlation results. Defaults to True
    format_data (bool, optional): Whether to apply preprocessing to input data. Defaults to True

## Returns:
    dict: Dictionary containing:
        - 'average': List of correlation values averaged across all data samples
        - 'individual': List of correlation values for each individual data sample

## Raises:
    None explicitly raised in the provided code

## Constraints:
    Preconditions:
        - Input data should be numeric and properly formatted
        - If input is a list, it should contain compatible data arrays
        - Data dimensions should be reasonable for correlation computation
    
    Postconditions:
        - Function returns a dictionary with 'average' and 'individual' keys
        - If show=True, matplotlib figure is displayed

## Side Effects:
    - Displays matplotlib plot when show=True
    - Issues deprecation warning about computational complexity for large datasets
    - May modify input data if format_data=True

## Control Flow:
```mermaid
flowchart TD
    A[Start describe()] --> B{format_data?}
    B -- Yes --> C[Apply format_data preprocessing]
    B -- No --> C[Skip formatting]
    C --> D[Initialize result dictionary]
    D --> E[Call internal summary function on x]
    E --> F[Call internal summary function on each x_i in x]
    F --> G{max_dims None?}
    G -- Yes --> H[Set max_dims based on data dimensions]
    G -- No --> H[Use provided max_dims]
    H --> I{show?}
    I -- Yes --> J[Create matplotlib plot using seaborn]
    J --> K[Display plot]
    I -- No --> K[Skip plotting]
    K --> L[Return result dictionary]
```

## Examples:
```python
# Basic usage
result = describe(data)

# With custom reduction method
result = describe(data, reduce='PCA')

# Without plotting
result = describe(data, show=False)

# With custom maximum dimensions
result = describe(data, max_dims=50)
```

## `hypertools.tools.describe.get_corr` · *function*

## Summary:
Calculates the Pearson correlation coefficient between two flattened arrays.

## Description:
This function computes the linear correlation between two datasets by flattening them and calculating the Pearson correlation coefficient. It's commonly used in data analysis to measure the strength and direction of linear relationships between variables.

The function is typically used in the context of dimensionality reduction analysis where it compares the relationship between original high-dimensional data and its reduced representation.

## Args:
    reduced (array-like): The reduced dimensional data array to compare against
    alldims (array-like): The full dimensional data array to compare against

## Returns:
    float: The Pearson correlation coefficient between the flattened arrays, ranging from -1 to 1.
           - 1 indicates perfect positive linear correlation
           - 0 indicates no linear correlation  
           - -1 indicates perfect negative linear correlation

## Raises:
    None explicitly raised, but may raise exceptions from scipy.stats.pearsonr if inputs are invalid

## Constraints:
    Preconditions:
    - Both inputs must be array-like objects that can be flattened
    - Inputs should contain numeric data for meaningful correlation calculation
    
    Postconditions:
    - Returns a float value in the range [-1, 1]
    - The function does not modify the input arrays

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_corr called with reduced, alldims] --> B[Flatten reduced array]
    B --> C[Flatten alldims array]
    C --> D[Calculate pearsonr(reduced.ravel(), alldims.ravel())]
    D --> E[Return correlation coefficient [0]
```

## Examples:
```python
# Basic usage
import numpy as np
from hypertools.tools.describe import get_corr

# Example with correlated data
reduced_data = np.array([[1, 2], [3, 4], [5, 6]])
all_dims_data = np.array([[2, 4], [6, 8], [10, 12]])
corr = get_corr(reduced_data, all_dims_data)
print(corr)  # Should be close to 1.0

# Example with uncorrelated data
reduced_data = np.array([[1, 2], [3, 4], [5, 6]])
all_dims_data = np.array([[1, 5], [2, 6], [3, 7]])
corr = get_corr(reduced_data, all_dims_data)
print(corr)  # Should be close to 0.0
```

## `hypertools.tools.describe.get_cdist` · *function*

## Summary:
Computes the pairwise Euclidean distance matrix for all rows in the input data.

## Description:
This function calculates the pairwise Euclidean distances between all rows of the input matrix, returning a symmetric distance matrix where each element [i,j] represents the Euclidean distance between row i and row j of the input data. It serves as a thin wrapper around scipy's cdist function with identical input arguments, making it convenient for computing distance matrices in data analysis workflows.

## Args:
    x (array-like): Input data matrix where rows represent samples and columns represent features. Must be convertible to a numpy array with numeric values.

## Returns:
    ndarray: A square distance matrix of shape (n_samples, n_samples) where element [i,j] is the Euclidean distance between row i and row j of the input matrix. The diagonal elements are always zero since the distance from each point to itself is zero.

## Raises:
    ValueError: May be raised by scipy.spatial.distance.cdist if input arrays are invalid or incompatible.

## Constraints:
    Preconditions:
    - Input x must be a valid numeric array-like structure that can be converted to a numpy array
    - Input x should not contain infinite or NaN values for meaningful distance calculations
    
    Postconditions:
    - Output is a symmetric matrix with zeros on the diagonal
    - Output shape is (n_rows, n_rows) where n_rows is the number of rows in input x

## Side Effects:
    None

## Control Flow:
    ```mermaid
    flowchart TD
        A[Input x] --> B[cdist(x, x)]
        B --> C[Return distance matrix]
    ```

## Examples:
    >>> import numpy as np
    >>> data = np.array([[1, 2], [3, 4], [5, 6]])
    >>> distances = get_cdist(data)
    >>> print(distances)
    [[0.         2.82842712 5.65685425]
     [2.82842712 0.         2.82842712]
     [5.65685425 2.82842712 0.        ]]

