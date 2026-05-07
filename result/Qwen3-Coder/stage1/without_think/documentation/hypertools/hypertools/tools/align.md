# `align.py`

## `hypertools.tools.align.align` · *function*

## Summary:
Performs hyperalignment or shared response model (SRM) alignment on multi-subject neuroimaging data to find a common representation across subjects.

## Description:
The align function applies either hyperalignment or shared response model (SRM) techniques to align neural data from multiple subjects into a common coordinate system. This enables comparison and analysis of brain activity patterns across different individuals. The function supports two main alignment approaches: hyperalignment (which uses Procrustes analysis) and SRM (which uses a probabilistic shared response model). The function also handles data preprocessing, validation, and provides deprecation warnings for legacy parameter usage.

## Args:
    data (list of numpy.ndarray): List of subject data matrices, where each matrix represents neural activity for one subject. Each matrix should have shape (n_samples, n_features).
    align (str or bool or dict, optional): Alignment method to use. Can be 'hyper', 'SRM', True (deprecated), or None (no alignment). Defaults to 'hyper'.
    normalize (None): Deprecated parameter, ignored in current implementation.
    ndims (None): Deprecated parameter, ignored in current implementation.
    method (str, optional): Legacy parameter for specifying alignment method. Deprecated in favor of `align` parameter. Defaults to None.
    format_data (bool, optional): Whether to preprocess data using format_data function. Defaults to True.

## Returns:
    list of numpy.ndarray: Aligned data matrices for each subject in the same coordinate system. Returns original data unchanged if align=None or align is a dict with model=None. For hyperalignment, returns list of aligned matrices with same shape as input. For SRM, returns list of transformed matrices with potentially different dimensions based on the shared feature extraction.

## Raises:
    ValueError: When insufficient subjects (< 2) are provided for training (in SRM case)
    ValueError: When subjects have inconsistent numbers of samples (in SRM case)
    ValueError: When data has zero variance (in procrustes case)
    ValueError: When template and target spaces have incompatible dimensions (in procrustes case)

## Constraints:
    Precondition: Data should be a list of numpy arrays with consistent sample dimensions
    Precondition: For SRM alignment, data should have at least 2 subjects
    Precondition: For hyperalignment, data should have at least 1 subject
    Postcondition: All returned arrays will have the same shape and be aligned in common space

## Side Effects:
    Issues warnings for deprecated parameter usage
    Issues warnings for potential overfitting conditions (more features than samples)
    Issues warnings for single subject data (cannot be aligned)
    May modify data shapes through padding and truncation operations

## Control Flow:
```mermaid
flowchart TD
    A[Start align function] --> B{align is None?}
    B -- Yes --> C[Return original data]
    B -- No --> D{align is dict?}
    D -- Yes --> E{align['model'] is None?}
    E -- Yes --> F[Return original data]
    E -- No --> G[Continue processing]
    D -- No --> H[Process deprecated parameters]
    H --> I{align is True?}
    I -- Yes --> J[Set align='hyper']
    I -- No --> K[Continue processing]
    K --> L{format_data?}
    L -- Yes --> M[Apply format_data preprocessing]
    M --> N{len(data) == 1?}
    N -- Yes --> O[Warn about single subject]
    N -- No --> P[Continue processing]
    P --> Q{data[0].shape[1] >= data[0].shape[0]?}
    Q -- Yes --> R[Warn about overfitting]
    Q -- No --> S[Continue processing]
    S --> T{align == 'hyper' OR method == 'hyper'?}
    T -- Yes --> U[Perform hyperalignment]
    T -- No --> V{align == 'SRM' OR method == 'SRM'?}
    V -- Yes --> W[Perform SRM alignment]
    V -- No --> X[Return original data]
    U --> Y[Return hyperaligned data]
    W --> Z[Return SRM-aligned data]
```

## Examples:
    # Basic hyperalignment
    aligned_data = align([subject1_data, subject2_data, subject3_data])
    
    # Explicit hyperalignment
    aligned_data = align([subject1_data, subject2_data], align='hyper')
    
    # SRM alignment
    aligned_data = align([subject1_data, subject2_data], align='SRM')
    
    # No alignment
    unaligned_data = align([subject1_data, subject2_data], align=None)
    
    # With deprecated method parameter
    aligned_data = align([subject1_data, subject2_data], method='hyper')
```

