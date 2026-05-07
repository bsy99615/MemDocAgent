# `describe.py`

## `hypertools.tools.describe.describe` · *function*

## Summary:
Analyzes dimensionality reduction performance by computing correlation between original and reduced-dimensional data across varying numbers of components.

## Description:
The `describe` function evaluates how well different dimensionality reduction techniques preserve the structure of input data by comparing the pairwise distances in the original high-dimensional space with those in reduced-dimensional spaces. It systematically reduces data to different numbers of components and measures the correlation between distance matrices to assess information retention.

This function is particularly useful for determining optimal number of components in dimensionality reduction workflows. It provides both average correlation analysis across all data points and individual correlation analysis for each data point when dealing with multi-sample data.

## Args:
    x (array-like): Input data to analyze. Can be a single dataset or list of datasets.
    reduce (str, optional): Dimensionality reduction technique to use. Defaults to 'IncrementalPCA'.
    max_dims (int, optional): Maximum number of dimensions to test. If None, automatically determined based on data shape.
    show (bool, optional): Whether to display visualization of results. Defaults to True.
    format_data (bool, optional): Whether to preprocess input data. Defaults to True.

## Returns:
    dict: Dictionary containing:
        - 'average' (list): Correlation values averaged across all data points for each number of components tested.
        - 'individual' (list): Correlation values for each individual data point for each number of components tested.

## Raises:
    None explicitly raised by this function, though underlying operations may raise:
    - ValueError: From scipy functions when invalid inputs are provided
    - RuntimeWarning: From scipy functions when encountering NaN or infinite values

## Constraints:
    Preconditions:
    - Input data must be convertible to numpy arrays
    - Data should have sufficient samples and features for meaningful dimensionality reduction
    - When max_dims is None, data dimensions must be valid for automatic determination
    
    Postconditions:
    - Returns a dictionary with 'average' and 'individual' keys containing correlation lists
    - Visualization is displayed if show=True (though this may vary by environment)

## Side Effects:
    - Issues deprecation warnings for certain parameter combinations
    - May modify input data through formatting if format_data=True
    - Displays matplotlib plot when show=True (requires matplotlib backend)

## Control Flow:
```mermaid
flowchart TD
    A[describe called with x, reduce, max_dims, show, format_data] --> B{format_data}
    B -- True --> C[Apply format_data(x, ppca=True) to x]
    B -- False --> C[Skip data formatting]
    C --> D{max_dims is None}
    D -- True --> E[Determine max_dims based on data shape (min of rows and columns)]
    D -- False --> E[Use provided max_dims]
    E --> F[Call summary(x, max_dims) for average correlations]
    F --> G[Call summary(x_i, max_dims) for each x_i in x for individual correlations]
    G --> H{show}
    H -- True --> I[Create matplotlib figure]
    I --> J[Plot individual correlations using seaborn.tsplot]
    J --> K[Display plot]
    H -- False --> K
    K --> L[Return result dictionary]
```

## Examples:
```python
# Basic usage with single dataset
import numpy as np
data = np.random.rand(100, 10)
result = describe(data)

# With custom reduction method and visualization disabled
result = describe(data, reduce='PCA', show=False)

# With multiple datasets
datasets = [np.random.rand(50, 5), np.random.rand(50, 5)]
result = describe(datasets)
```

## `hypertools.tools.describe.get_corr` · *function*

## Summary:
Calculates the Pearson correlation coefficient between two arrays of data.

## Description:
This function computes the Pearson correlation coefficient between two datasets, typically used to measure the linear relationship between reduced-dimensional data and full-dimensional data. It's commonly used in dimensionality reduction analysis to quantify how much variance is preserved when reducing data dimensions.

The function takes two arrays, flattens them using ravel(), and computes their correlation coefficient using scipy's pearsonr function. It returns only the correlation value (not the p-value) as the primary metric of interest.

## Args:
    reduced (array-like): The reduced-dimensional data array to compare against.
    alldims (array-like): The full-dimensional data array to compare against.

## Returns:
    float: The Pearson correlation coefficient between the two arrays, ranging from -1 to 1.
           - 1 indicates perfect positive linear correlation
           - 0 indicates no linear correlation  
           - -1 indicates perfect negative linear correlation

## Raises:
    None explicitly raised by this function, though underlying scipy.stats.pearsonr may raise:
    - ValueError: If inputs are empty or contain non-numeric data
    - RuntimeWarning: If inputs contain NaN or infinite values

## Constraints:
    Preconditions:
    - Both input arrays must be numeric
    - Arrays should have the same number of elements when flattened
    - Inputs should not be empty
    
    Postconditions:
    - Returns a float value in the range [-1, 1]
    - Function execution is deterministic for given inputs

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_corr(reduced, alldims)] --> B[Flatten reduced array]
    B --> C[Flatten alldims array]
    C --> D[Calculate pearsonr(reduced.ravel(), alldims.ravel())]
    D --> E[Return correlation coefficient [0]]
```

## Examples:
```python
# Basic usage
import numpy as np
from scipy.stats.stats import pearsonr

# Example with perfectly correlated data
reduced_data = np.array([[1, 2, 3], [4, 5, 6]])
all_dims_data = np.array([[1, 2, 3], [4, 5, 6]])
corr = get_corr(reduced_data, all_dims_data)
print(corr)  # Should be 1.0

# Example with uncorrelated data
reduced_data = np.array([[1, 2, 3], [4, 5, 6]])
all_dims_data = np.array([[1, 2, 3], [7, 8, 9]])
corr = get_corr(reduced_data, all_dims_data)
print(corr)  # Should be close to 0.0
```

## `hypertools.tools.describe.get_cdist` · *function*

## Summary:
Computes pairwise Euclidean distances between all rows of input data.

## Description:
This function calculates the pairwise Euclidean distances between all rows in the input matrix using scipy's cdist function. It serves as a simplified interface for computing distance matrices from data points.

## Args:
    x (array-like): Input data matrix where rows represent samples and columns represent features.

## Returns:
    ndarray: A square distance matrix of shape (n_samples, n_samples) where element (i,j) represents the Euclidean distance between row i and row j of the input data.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Precondition: Input x must be a valid array-like object that can be converted to a numpy array.
    Postcondition: Output is always a symmetric square matrix with zeros on the diagonal.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[get_cdist called with x] --> B[Convert x to numpy array]
    B --> C[Call scipy.spatial.distance.cdist(x, x)]
    C --> D[Return distance matrix]
```

## Examples:
```python
# Basic usage
import numpy as np
data = np.array([[1, 2], [3, 4], [5, 6]])
distances = get_cdist(data)
print(distances)
# Output: [[ 0.          2.82842712  5.65685425]
#          [ 2.82842712  0.          2.82842712]
#          [ 5.65685425  2.82842712  0.        ]]
```

