# `procrustes.py`

## `hypertools.tools.procrustes.procrustes` · *function*

## Summary:
Performs Procrustes analysis to find the optimal linear transformation between two datasets by minimizing the squared Frobenius norm of the difference between transformed source and target data.

## Description:
Implements a generalized Procrustes analysis algorithm that computes the best linear transformation to align one dataset (source) with another (target). This function is commonly used in shape analysis, data alignment, and comparative studies where datasets need to be compared in a common coordinate system. The transformation accounts for translation, rotation, scaling, and reflection based on the specified parameters.

The function internally validates that both datasets have the same number of samples, normalizes the data, and applies either orthogonal (standard Procrustes) or oblique (generalized least squares) transformations depending on configuration. Note: The original implementation contains a bug where `formatter` is referenced instead of `format_data` (which is imported from the module).

## Args:
    source (array-like): Source data matrix with shape (n_samples, n_features_source)
    target (array-like): Target data matrix with shape (n_samples, n_features_target)  
    scaling (bool, optional): Whether to apply scaling factor in transformation. Defaults to True.
    reflection (bool, optional): Whether to allow reflections in the transformation. Defaults to True.
    reduction (bool, optional): Whether to reduce dimensionality when source has more features than target. Defaults to False.
    oblique (bool, optional): Whether to use oblique (generalized least squares) transformation instead of orthogonal. Defaults to False.
    oblique_rcond (float, optional): Condition number for oblique transformation. Defaults to -1.
    format_data (bool, optional): Whether to preprocess input data using format_data function. Defaults to True.

## Returns:
    numpy.ndarray: Transformed source data aligned to the target space with shape (n_samples, n_features_target)

## Raises:
    ValueError: When datasets have incompatible dimensions or when invariant datasets are encountered
    RuntimeError: When transform is called before fit has been performed

## Constraints:
    Precondition: Both source and target datasets must have the same number of samples (n_samples)
    Precondition: Neither dataset should be invariant in time (all zero variance)
    Precondition: When source has more features than target and reduction=False, ValueError is raised
    Postcondition: Returned array has same number of rows as input datasets and matches target feature count

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start procrustes] --> B{format_data?}
    B -- Yes --> C[Apply format_data to [source, target]]
    B -- No --> D[Skip formatting]
    C --> E[Validate sample counts]
    D --> E
    E --> F{Sample counts equal?}
    F -- No --> G[ValueError: Different sample counts]
    F -- Yes --> H[Check for invariant datasets]
    H --> I{Invariant dataset?}
    I -- Yes --> J[ValueError: Invariant datasets]
    I -- No --> K[Normalize data]
    K --> L{Source features < Target features?}
    L -- Yes --> M[Pad source with zeros]
    L -- No --> N{Source features > Target features?}
    N -- Yes --> O{reduction=True?}
    O -- No --> P[ValueError: Higher dimensional mapping not supported]
    O -- Yes --> Q[Pad target with zeros]
    N -- No --> R[Continue]
    R --> S[Compute transformation matrix]
    S --> T{oblique=True?}
    T -- Yes --> U[Use least squares (numpy.linalg.lstsq)]
    T -- No --> V[Use SVD decomposition (numpy.linalg.svd)]
    V --> W[Apply reflection constraint if reflection=False]
    U --> X[Calculate projection matrix]
    W --> X
    X --> Y[Scale if scaling=True]
    Y --> Z[Transform source data]
    Z --> AA[Return result]
```

## Examples:
```python
# Basic usage with two datasets of same dimensions
source_data = [[1, 2], [3, 4], [5, 6]]
target_data = [[2, 1], [4, 3], [6, 5]]
aligned_data = procrustes(source_data, target_data)

# Usage with scaling disabled
aligned_no_scale = procrustes(source_data, target_data, scaling=False)

# Usage with oblique transformation
aligned_oblique = procrustes(source_data, target_data, oblique=True)

# Usage with dimensionality reduction
source_high_dim = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
target_low_dim = [[1, 2], [3, 4], [5, 6]]
aligned_reduced = procrustes(source_high_dim, target_low_dim, reduction=True)
```

