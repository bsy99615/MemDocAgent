# `align.py`

## `hypertools.tools.align.align` · *function*

## Summary:
Performs data alignment across multiple datasets using either hyperalignment or shared response model (SRM) techniques to find common representations.

## Description:
The align function applies dimensionality reduction and alignment techniques to multiple datasets to find shared representations across subjects or conditions. It supports two primary alignment methods: hyperalignment ('hyper') which uses iterative Procrustes analysis to align data, and shared response model ('SRM') which finds common low-dimensional representations across subjects.

This function is designed to be a central interface for data alignment operations in the hypertools toolkit, handling data preprocessing, validation, and applying appropriate alignment algorithms based on user specifications.

## Args:
    data (list): List of data matrices to align, where each matrix represents data from a different subject or condition
    align (str or bool, optional): Alignment method to use. Options are 'hyper', 'SRM', True (deprecated), or None (no alignment). Defaults to 'hyper'
    normalize (None): Deprecated parameter for normalization settings
    ndims (None): Deprecated parameter for specifying number of dimensions
    method (str, optional): Alternative parameter name for alignment method. Deprecated in favor of `align` parameter. Defaults to None
    format_data (bool): Whether to apply preprocessing formatting to the data. Defaults to True

## Returns:
    list: List of aligned data matrices with the same shape, where each matrix represents the aligned version of the corresponding input dataset

## Raises:
    ValueError: When data has inconsistent shapes or insufficient samples for alignment
    Warning: Various warnings about data characteristics such as feature/sample ratios, single-item lists, and deprecated parameter usage

## Constraints:
    Precondition: Input data must be a list of numpy arrays with compatible dimensions
    Precondition: For hyperalignment, data should ideally have more samples than features
    Postcondition: All returned matrices will have the same shape and represent aligned versions of the input data

## Side Effects:
    Issues warnings via Python's warnings module for deprecated parameters and data quality issues
    May modify data through preprocessing steps when format_data=True

## Control Flow:
```mermaid
flowchart TD
    A[Start align function] --> B{align is None?}
    B -- Yes --> C[Return original data]
    B -- No --> D{align is dict?}
    D -- Yes --> E{align['model'] is None?}
    E -- Yes --> C
    E -- No --> F[Process deprecated parameters]
    D -- No --> F
    F --> G{format_data?}
    G -- Yes --> H[Apply format_data preprocessing]
    G -- No --> I[Skip preprocessing]
    I --> J{len(data) == 1?}
    J -- Yes --> K[Warn about single item and skip alignment]
    J -- No --> L{data[0].shape[1] >= data[0].shape[0]?}
    L -- Yes --> M[Warn about feature excess]
    L -- No --> N[Proceed to alignment]
    N --> O{align == 'hyper' OR method == 'hyper'?}
    O -- Yes --> P[Execute hyperalignment algorithm]
    O -- No --> Q{align == 'SRM' OR method == 'SRM'?}
    Q -- Yes --> R[Execute SRM alignment]
    Q -- No --> S[Return original data]
    P --> T[Return hyperaligned data]
    R --> U[Return SRM-aligned data]
```

## Examples:
```python
# Basic hyperalignment of multiple datasets
import numpy as np
data = [np.random.rand(100, 50), np.random.rand(120, 50), np.random.rand(110, 50)]
aligned_data = align(data, align='hyper')

# Using SRM alignment method
aligned_data = align(data, align='SRM')

# With deprecated method parameter (will warn)
aligned_data = align(data, method='hyper')

# Skip alignment entirely
aligned_data = align(data, align=None)
```

