# `procrustes.py`

## `hypertools.tools.procrustes.procrustes` · *function*

## Summary:
Performs Procrustes analysis to find the optimal linear transformation between two datasets.

## Description:
This function implements Procrustes analysis, a technique used to align two datasets by finding the optimal linear transformation that minimizes the squared distance between corresponding points. It's commonly used in shape analysis, data alignment, and dimensionality reduction applications.

The function handles various configurations including scaling, reflection control, and dimensionality reduction options. It internally normalizes the input data and applies singular value decomposition to compute the transformation matrix.

## Args:
    source (array-like): The source dataset to be transformed.
    target (array-like): The target dataset used as reference for alignment.
    scaling (bool, optional): Whether to apply scaling to the transformation. Defaults to True.
    reflection (bool, optional): Whether to allow reflections in the transformation. Defaults to True.
    reduction (bool, optional): Whether to allow dimensionality reduction. Defaults to False.
    oblique (bool, optional): Whether to use oblique (non-orthogonal) transformation. Defaults to False.
    oblique_rcond (float, optional): Condition number for oblique least squares. Defaults to -1.
    format_data (bool, optional): Whether to format input data using format_data function. Defaults to True.

## Returns:
    array-like: The transformed source data aligned to the target space.

## Raises:
    ValueError: If datasets have different numbers of samples, if datasets are invariant in time, or if dimensionality reduction is not allowed but required.
    RuntimeError: If the mapper needs to be trained before use.

## Constraints:
    Preconditions:
        - Source and target datasets must have the same number of samples
        - Datasets must not be invariant in time (all zero variance)
        - When sm > tm and reduction=False, dimensionality reduction is not supported
    Postconditions:
        - The returned data is properly aligned to the target space
        - Transformation matrix is computed and applied correctly

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start procrustes] --> B{format_data?}
    B -- Yes --> C[format_data(source, target)]
    B -- No --> C[Skip formatting]
    C --> D[Validate sample counts]
    D --> E{Sample counts equal?}
    E -- No --> F[ValueError]
    E -- Yes --> G[Check for invariant datasets]
    G --> H{Invariant dataset?}
    H -- Yes --> I[ValueError]
    H -- No --> J[Normalize datasets]
    J --> K{Source dims < Target dims?}
    K -- Yes --> L[Pad source with zeros]
    K -- No --> M{Source dims > Target dims?}
    M -- Yes --> N{reduction enabled?}
    N -- No --> O[ValueError]
    N -- Yes --> P[Pad target with zeros]
    M -- No --> Q[Proceed to transformation]
    Q --> R[Compute transformation matrix]
    R --> S{Oblique transformation?}
    S -- Yes --> T[Use lstsq or solve]
    S -- No --> U[Use SVD decomposition]
    U --> V{Reflection allowed?}
    V -- No --> W[Adjust for no reflection]
    V -- Yes --> X[Proceed normally]
    X --> Y[Apply scaling if requested]
    Y --> Z[Return transformed data]
```

## Examples:
    # Basic usage with two datasets
    source_data = [[1, 2], [3, 4], [5, 6]]
    target_data = [[2, 3], [4, 5], [6, 7]]
    result = procrustes(source_data, target_data)
    
    # Usage with scaling disabled
    result = procrustes(source_data, target_data, scaling=False)
    
    # Usage with reflection disabled
    result = procrustes(source_data, target_data, reflection=False)
```

