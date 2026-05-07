# `align.py`

## `hypertools.tools.align.align` · *function*

## Summary:
Performs data alignment across multiple datasets using either hyperalignment or Shared Response Model (SRM) methods to find a common representation space.

## Description:
This function aligns multiple datasets into a common coordinate system by finding shared patterns across datasets. It supports two primary alignment methods: hyperalignment (based on Procrustes analysis) and SRM (Shared Response Model). The function handles various data preprocessing steps and includes validation checks to ensure proper alignment conditions.

The function was designed as a separate component to encapsulate the complex alignment logic, allowing users to specify different alignment strategies while maintaining clean separation between data preparation and alignment operations.

## Args:
- data (list): List of data matrices to be aligned
- align (str or bool, optional): Alignment method to use. Options are 'hyper', 'SRM', True (deprecated), or None (no alignment). Defaults to 'hyper'.
- normalize (None): Deprecated parameter, ignored in current implementation.
- ndims (None): Deprecated parameter, ignored in current implementation.
- method (str, optional): Legacy parameter for specifying alignment method. Deprecated in favor of `align`. Defaults to None.
- format_data (bool): Whether to apply data formatting before alignment. Defaults to True.

## Returns:
- list: List of aligned data matrices in the common space. Each matrix has the same shape and represents the aligned version of the corresponding input dataset.

## Raises:
- Warning: Various deprecation warnings when using legacy parameters
- ValueError: When datasets have incompatible shapes for alignment (in some cases)

## Constraints:
- Precondition: Input data must be a list of numpy arrays
- Precondition: For hyperalignment, number of samples should exceed number of features to avoid overfitting
- Postcondition: All returned matrices will have the same shape and represent aligned data

## Side Effects:
- Issues deprecation warnings when legacy parameters are used
- May issue warnings about data dimensionality issues
- Modifies data through formatting and alignment processes

## Control Flow:
```mermaid
flowchart TD
    A[Start align function] --> B{align is None?}
    B -- Yes --> C[Return original data]
    B -- No --> D{align is dict?}
    D -- Yes --> E{align['model'] is None?}
    E -- Yes --> F[Return original data]
    E -- No --> G[Process alignment]
    D -- No --> G
    G --> H{method is not None?}
    H -- Yes --> I[Warn about deprecation, set align=method]
    H -- No --> J{align is True?}
    J -- Yes --> K[Warn about deprecation, set align='hyper']
    J -- No --> L{format_data?}
    L -- Yes --> M[Apply format_data with ppca=True]
    L -- No --> N[Skip formatting]
    N --> O{len(data) == 1?}
    O -- Yes --> P[Warn about single dataset, skip alignment]
    O -- No --> Q{data[0].shape[1] >= data[0].shape[0]?}
    Q -- Yes --> R[Warn about overfitting risk]
    Q -- No --> S[Continue]
    S --> T{align == 'hyper' OR method == 'hyper'?}
    T -- Yes --> U[Execute hyperalignment algorithm]
    T -- No --> V{align == 'SRM' OR method == 'SRM'?}
    V -- Yes --> W[Execute SRM alignment]
    V -- No --> X[Return original data]
    U --> Y[Return hyperaligned data]
    W --> Z[Return SRM-aligned data]
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

