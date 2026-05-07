# `align.py`

## `hypertools.tools.align.align` · *function*

## Summary:
Performs data alignment across multiple datasets using either hyperalignment or SRM (Shared Response Model) methods.

## Description:
This function applies alignment techniques to transform multiple datasets into a common coordinate system. It supports two primary alignment methods: 'hyper' for hyperalignment and 'SRM' for Shared Response Model. The function handles various input configurations including None, boolean flags, and dictionary specifications for alignment parameters. It also includes deprecation warnings for legacy parameter usage and provides warnings for potential overfitting conditions.

The function internally calls a `formatter` function (not defined in the provided code) to preprocess data when `format_data=True`, which is intended to apply PCA preprocessing. The function also uses numpy (`np`) which should be imported in the calling scope.

## Args:
    data (list): List of numpy arrays representing datasets to be aligned
    align (str or bool or dict, optional): Alignment method specification. Can be 'hyper', 'SRM', True (deprecated), None (no alignment), or a dict with 'model' key. Defaults to 'hyper'.
    normalize (any, optional): Normalization parameter - not currently used in implementation. Defaults to None.
    ndims (int, optional): Number of dimensions - not currently used in implementation. Defaults to None.
    method (str, optional): Deprecated parameter - use align instead. Defaults to None.
    format_data (bool, optional): Whether to format data before alignment. Defaults to True.

## Returns:
    list: List of aligned numpy arrays with the same shape as input data, transformed into a common coordinate system. In the hyperalignment case, returns a list of aligned arrays. In the SRM case, returns a list of transformed arrays.

## Raises:
    None explicitly raised in the code shown, but may raise exceptions from underlying functions like procrustes or SRM.

## Constraints:
    Precondition: Input data must be a list of numpy arrays
    Precondition: When align='hyper', data should have more samples than features to avoid overfitting
    Postcondition: All returned arrays will have the same shape and be aligned in a common space

## Side Effects:
    Issues warnings via Python warnings module for deprecated parameters and potential overfitting conditions
    May modify data shapes through padding operations during hyperalignment process

## Control Flow:
```mermaid
flowchart TD
    A[Start align function] --> B{align is None?}
    B -- Yes --> C[Return data unchanged]
    B -- No --> D{align is dict?}
    D -- Yes --> E{align['model'] is None?}
    E -- Yes --> F[Return data unchanged]
    E -- No --> G[Continue processing]
    D -- No --> H[Check method deprecation]
    H --> I{align is True?}
    I -- Yes --> J[Set align='hyper']
    I -- No --> K[Continue processing]
    K --> L{format_data?}
    L -- Yes --> M[Apply formatter (undefined in provided code)]
    L -- No --> N[Skip formatting]
    N --> O{len(data) == 1?}
    O -- Yes --> P[Warn and skip alignment]
    O -- No --> Q{data[0].shape[1] >= data[0].shape[0]?}
    Q -- Yes --> R[Warn about overfitting]
    Q -- No --> S[Continue]
    S --> T{align == 'hyper' OR method == 'hyper'?}
    T -- Yes --> U[Perform hyperalignment]
    T -- No --> V{align == 'SRM' OR method == 'SRM'?}
    V -- Yes --> W[Perform SRM alignment]
    V -- No --> X[Return data unchanged]
    U --> Y[Return hyperaligned data]
    W --> Z[Return SRM aligned data]
```

## Examples:
```python
# Basic hyperalignment
aligned_data = align([dataset1, dataset2, dataset3])

# Using SRM alignment
aligned_data = align([dataset1, dataset2], align='SRM')

# With data formatting disabled
aligned_data = align([dataset1, dataset2], format_data=False)

# Using deprecated method parameter (will warn)
aligned_data = align([dataset1, dataset2], method='hyper')
```

