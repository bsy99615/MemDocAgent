# `procrustes.py`

## `hypertools.tools.procrustes.procrustes` · *function*

## Summary:
Performs Procrustes analysis to align two datasets by computing and applying a transformation matrix that minimizes the squared error between them.

## Description:
This function implements Procrustes analysis, a technique commonly used in shape analysis and data alignment to find the optimal linear transformation between two datasets. The function computes a transformation matrix that aligns the source dataset to the target dataset while preserving geometric relationships.

The function handles various configuration options including scaling, reflection control, dimensionality reduction, and oblique transformations. It normalizes the input datasets before computing the alignment transformation and applies the resulting transformation to the source data.

## Args:
    source (array-like): Source dataset to be transformed, shape (n_samples, n_features_source)
    target (array-like): Target dataset for alignment reference, shape (n_samples, n_features_target)
    scaling (bool): Whether to apply scaling to the transformation matrix. Defaults to True
    reflection (bool): Whether to allow reflections in the transformation. Defaults to True
    reduction (bool): Whether to allow dimensionality reduction when source has more features than target. Defaults to False
    oblique (bool): Whether to use oblique (non-orthogonal) transformation. Defaults to False
    oblique_rcond (float): Condition number for oblique least squares. Defaults to -1
    format_data (bool): Whether to apply data formatting before processing. Defaults to True

## Returns:
    array-like: Transformed source data aligned to the target space, shape (n_samples, n_features_target)

## Raises:
    ValueError: When datasets have incompatible sample counts (different number of samples), when handling invariant datasets (zero variance in all features), or when reduction=False and source has higher dimensionality than target
    RuntimeError: When the transformation matrix is not properly computed before use

## Constraints:
    Precondition: Both source and target datasets must have the same number of samples
    Precondition: Neither dataset should be invariant in time (all zero variance in features)
    Precondition: When reduction=False, source dataset must not have more features than target dataset
    Postcondition: Returned data is aligned to target space with minimal squared error

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start procrustes] --> B{format_data?}
    B -- Yes --> C[Apply format_data]
    B -- No --> C[Skip format_data]
    C --> D[Call fit(source, target)]
    D --> E{Source and target sample counts equal?}
    E -- No --> F[ValueError: Different sample counts]
    E -- Yes --> G{Invariant dataset?}
    G -- Yes --> H[ValueError: Invariant datasets]
    G -- No --> I[Normalize datasets]
    I --> J{Source features < Target features?}
    J -- Yes --> K[Pad source with zeros]
    J -- No --> L{Source features > Target features?}
    L -- Yes --> M{reduction enabled?}
    M -- Yes --> N[Pad target with zeros]
    M -- No --> O[ValueError: Higher dimensionality not supported]
    N --> P[Compute transformation matrix]
    P --> Q{Oblique transformation?}
    Q -- Yes --> R[Use least squares or solve]
    Q -- No --> S[Use SVD decomposition]
    S --> T[Apply reflection control]
    T --> U[Apply scaling if enabled]
    U --> V[Return transformed source]
```

## Examples:
    # Basic usage
    aligned_data = procrustes(source_data, target_data)
    
    # With custom parameters
    aligned_data = procrustes(source_data, target_data, scaling=False, reflection=False)
    
    # With dimensionality reduction
    aligned_data = procrustes(source_data, target_data, reduction=True)

