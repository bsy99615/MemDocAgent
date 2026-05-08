# `procrustes.py`

## `hypertools.tools.procrustes.procrustes` · *function*

## Summary:
Performs Procrustes analysis to find the optimal linear transformation between two datasets.

## Description:
The procrustes function implements a Procrustes analysis algorithm that finds the best linear transformation to align one dataset (source) with another (target). This is commonly used for shape analysis, data alignment, and dimensionality reduction tasks. The function supports various configurations including scaling, reflection control, and oblique transformations.

This function is extracted into its own component to encapsulate the complex mathematical operations of Procrustes analysis, separating the fitting (computation of transformation matrix) from the transformation (application of matrix to data). This modular approach allows for reuse and testing of the core alignment algorithm.

## Args:
    source (array-like): The source dataset to be transformed.
    target (array-like): The target dataset to align against.
    scaling (bool, optional): Whether to apply scaling to the transformation matrix. Defaults to True.
    reflection (bool, optional): Whether to allow reflections in the transformation. Defaults to True.
    reduction (bool, optional): Whether to allow dimensionality reduction. Defaults to False.
    oblique (bool, optional): Whether to use oblique (non-orthogonal) transformation. Defaults to False.
    oblique_rcond (float, optional): Condition number for oblique least squares. Defaults to -1.
    format_data (bool, optional): Whether to format input data using the format_data function. Note: The code references 'formatter' but imports 'format_data', which may cause runtime errors. Defaults to True.

## Returns:
    array-like: The transformed source data aligned with the target space. The result has the same shape as the target data (n_samples, target_features).

## Raises:
    ValueError: If datasets have different numbers of samples, if datasets are invariant in time (zero variance), or if dimensionality reduction is not allowed but required.
    RuntimeError: If the mapper needs to be trained before use (though this shouldn't occur in normal operation).

## Constraints:
    Preconditions:
    - Source and target datasets must have the same number of samples (rows)
    - Datasets must not be invariant in time (all zero variance)
    - When source dimensionality (sm) is greater than target dimensionality (tm) and reduction=False, an error is raised
    - When source dimensionality is less than target dimensionality, zeros are padded to the source matrix
    
    Postconditions:
    - The returned transformation matrix has the correct dimensions
    - The transformation preserves the geometric relationship between datasets
    - The output data is properly scaled and aligned

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start procrustes] --> B{format_data?}
    B -- Yes --> C[format_data(source, target)]
    B -- No --> C
    C --> D[Call fit(source, target)]
    D --> E{sn != tn?}
    E -- Yes --> F[ValueError: Different sample counts]
    E -- No --> G{ssqs[i] <= eps?}
    G -- Yes --> H[ValueError: Invariant datasets]
    G -- No --> I[Calculate norms]
    I --> J{sm < tm?}
    J -- Yes --> K[Pad source with zeros]
    J -- No --> L{sm > tm?}
    L -- Yes --> M{reduction?}
    M -- Yes --> N[Pad target with zeros]
    M -- No --> O[ValueError: Dimensionality reduction not allowed]
    L -- No --> P[Normalize data]
    P --> Q{oblique?}
    Q -- Yes --> R[Use linalg.solve or lstsq]
    Q -- No --> S[Use SVD decomposition]
    S --> T{reflection?}
    T -- No --> U[Adjust singular values]
    T -- Yes --> V[Continue with SVD result]
    V --> W[Apply scaling if enabled]
    W --> X[Return projection matrix]
    R --> X
    X --> Y[Call transform(source, proj)]
    Y --> Z[Return transformed data]
```

## Examples:
```python
# Basic usage
source_data = [[1, 2], [3, 4], [5, 6]]
target_data = [[2, 3], [4, 5], [6, 7]]
result = procrustes(source_data, target_data)

# With scaling disabled
result = procrustes(source_data, target_data, scaling=False)

# With reflection disabled
result = procrustes(source_data, target_data, reflection=False)

# With oblique transformation
result = procrustes(source_data, target_data, oblique=True)
```

