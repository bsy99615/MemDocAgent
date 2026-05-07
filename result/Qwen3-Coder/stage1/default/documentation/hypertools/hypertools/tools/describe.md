# `describe.py`

## `hypertools.tools.describe.get_corr` · *function*

## Summary:
Computes the Pearson correlation coefficient between two flattened arrays to measure linear relationship strength.

## Description:
Calculates the linear correlation between two datasets by flattening them to 1D arrays and computing the Pearson correlation coefficient. This function is commonly used to evaluate how well a dimensionality reduction technique preserves the relationships in the original data by comparing the reduced representation with the full-dimensional data.

## Args:
    reduced (array-like): The reduced-dimension dataset, typically the result of a dimensionality reduction operation such as PCA or t-SNE.
    alldims (array-like): The full-dimensional dataset, typically the original data before dimensionality reduction.

## Returns:
    float: The Pearson correlation coefficient between the flattened arrays, ranging from -1 to 1. A value of 1 indicates perfect positive linear correlation, -1 indicates perfect negative linear correlation, and 0 indicates no linear correlation.

## Raises:
    ValueError: If either input array contains non-numeric data or if the arrays are empty after flattening.

## Constraints:
    Preconditions:
        - Both inputs must be array-like objects that support the .ravel() method
        - Both inputs must have compatible shapes for flattening
        - Inputs should contain numeric data for meaningful correlation calculation
    Postconditions:
        - Returns a float value in the range [-1, 1]
        - The result represents the linear correlation between flattened versions of the input arrays

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_corr called] --> B[Validate inputs]
    B --> C[Flatten reduced array]
    C --> D[Flatten alldims array]
    D --> E[Calculate pearsonr(reduced.ravel(), alldims.ravel())]
    E --> F{Success?}
    F -->|Yes| G[Return correlation coefficient]
    F -->|No| H[Raise ValueError]
```

## Examples:
```python
import numpy as np
from scipy.stats import pearsonr

# Example 1: Comparing reduced vs original data
original_data = np.random.rand(100, 10)
reduced_data = np.random.rand(100, 3)  # Reduced version
correlation = get_corr(reduced_data, original_data)
print(f"Correlation between reduced and original: {correlation:.3f}")

# Example 2: Perfect correlation case
x = np.array([[1, 2, 3], [4, 5, 6]])
y = np.array([[2, 4, 6], [8, 10, 12]])  # Perfect linear relationship
corr = get_corr(x, y)
print(f"Perfect positive correlation: {corr}")  # Should be close to 1.0

# Example 3: No correlation case  
x = np.array([[1, 2, 3], [4, 5, 6]])
y = np.array([[1, 5, 3], [2, 4, 6]])  # No linear relationship
corr = get_corr(x, y)
print(f"No linear correlation: {corr:.3f}")
```

## `hypertools.tools.describe.get_cdist` · *function*

## Summary:
Computes pairwise Euclidean distances between all rows of a data matrix with itself.

## Description:
This function serves as a thin wrapper around scipy's cdist function to compute pairwise Euclidean distances between all rows of the input data matrix. It is designed to calculate a symmetric distance matrix where each element [i,j] represents the Euclidean distance between row i and row j of the input data. This utility function is commonly used in clustering, similarity analysis, and distance-based machine learning algorithms.

## Args:
    x (array-like): Input data matrix where rows represent samples and columns represent features. Should be convertible to a numpy array with shape (n_samples, n_features).

## Returns:
    ndarray: A square distance matrix of shape (n_samples, n_samples) where element [i,j] represents the Euclidean distance between row i and row j of the input matrix x. The diagonal elements are zero since each point is zero distance from itself.

## Raises:
    ValueError: If the input arrays have incompatible shapes for distance computation.
    TypeError: If the input cannot be converted to a numpy array or contains invalid data types.
    Exception: Other exceptions that may be raised by scipy.spatial.distance.cdist for invalid inputs.

## Constraints:
    Preconditions:
    - Input x must be convertible to a numpy array
    - Input x should have at least one sample (row)
    - Input x should have finite numeric values
    
    Postconditions:
    - Output is a symmetric matrix of size (n_samples, n_samples)
    - Diagonal elements are zero (distance from each point to itself)
    - All values in the output matrix are non-negative

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_cdist called with x] --> B{Input validation}
    B --> C[Call scipy.spatial.distance.cdist(x, x)]
    C --> D[Return distance matrix]
```

## Examples:
```python
import numpy as np
from hypertools.tools.describe import get_cdist

# Basic usage with 3 points in 2D space
data = np.array([[0, 0], [1, 0], [0, 1]])
distances = get_cdist(data)
print(distances)
# Output: [[0.         1.         1.        ]
#          [1.         0.         1.41421356]
#          [1.         1.41421356 0.        ]]

# With 2D array
data = np.array([[1, 2], [3, 4]])
distances = get_cdist(data)
print(distances)
# Output: [[0.         2.82842712]
#          [2.82842712 0.        ]]

# With 1D array (will be treated as single sample)
data = np.array([1, 2, 3])
distances = get_cdist(data)
print(distances)
# Output: [[0.]]
```

