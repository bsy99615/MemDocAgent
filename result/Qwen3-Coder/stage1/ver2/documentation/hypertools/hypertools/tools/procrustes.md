# `procrustes.py`

## `hypertools.tools.procrustes.procrustes` · *function*

## Summary:
Performs Procrustes analysis to find an optimal linear transformation between two datasets by minimizing the squared Frobenius norm of the difference between the transformed source and target datasets.

## Description:
This function implements Procrustes analysis, a technique commonly used in shape analysis and data alignment to find the best linear transformation that maps one dataset onto another. The transformation includes optional scaling, reflection handling, and dimensionality reduction capabilities. The function is designed to work with multi-dimensional numerical data and can handle various transformation modes including orthogonal (standard Procrustes), oblique (generalized), and reflection-constrained mappings.

## Args:
    source (array-like): Source dataset to be transformed, typically representing a reference or template space
    target (array-like): Target dataset that the source will be aligned to, typically representing a target space  
    scaling (bool, optional): Whether to apply scaling factor to the transformation matrix. Defaults to True
    reflection (bool, optional): Whether to allow reflections in the transformation. Defaults to True
    reduction (bool, optional): Whether to allow dimensionality reduction when source has higher dimensionality than target. Defaults to False
    oblique (bool, optional): Whether to perform oblique (generalized) Procrustes analysis instead of orthogonal. Defaults to False
    oblique_rcond (float, optional): Condition number for least squares solver in oblique mode. Defaults to -1
    format_data (bool, optional): Whether to apply data formatting preprocessing. Defaults to True

## Returns:
    numpy.ndarray: Transformed version of the source dataset aligned to the target space using the computed Procrustes transformation matrix. The result has the same number of samples as the input datasets but matches the target's feature dimensionality.

## Raises:
    ValueError: When datasets have incompatible sample counts, when datasets are invariant over time, or when dimensionality reduction is disabled but source has higher dimensionality than target
    RuntimeError: When transform is called before fit has been completed (though this shouldn't occur in normal usage)

## Constraints:
    Precondition: Both source and target datasets must have the same number of samples (rows)
    Precondition: Neither dataset should be invariant over time (all elements zero or nearly zero)
    Precondition: When reduction=False and source dimensionality > target dimensionality, an error is raised
    Postcondition: The returned array has the same number of samples as the input datasets but matches the target's feature dimensionality

## Side Effects:
    None - This function is pure and doesn't modify external state or perform I/O operations

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
    J --> K{Source dim < Target dim?}
    K -- Yes --> L[Pad source with zeros]
    K -- No --> M{Source dim > Target dim?}
    M -- Yes --> N{reduction enabled?}
    N -- No --> O[ValueError]
    N -- Yes --> P[Pad target with zeros]
    M -- No --> Q[Proceed to transformation]
    Q --> R[Compute transformation matrix T]
    R --> S{oblique mode?}
    S -- Yes --> T[Use least squares or solve]
    S -- No --> U[Use SVD decomposition]
    U --> V{reflection enabled?}
    V -- No --> W[Adjust for reflection constraint]
    V -- Yes --> X[Skip reflection adjustment]
    X --> Y[Apply scaling if requested]
    Y --> Z[Transform source data]
    Z --> AA[Return transformed data]
```

## Examples:
```python
# Basic Procrustes alignment
source_data = np.random.rand(10, 5)
target_data = np.random.rand(10, 5)
aligned_source = procrustes(source_data, target_data)

# Procrustes with scaling disabled
aligned_source = procrustes(source_data, target_data, scaling=False)

# Procrustes with reflection disabled
aligned_source = procrustes(source_data, target_data, reflection=False)
```

