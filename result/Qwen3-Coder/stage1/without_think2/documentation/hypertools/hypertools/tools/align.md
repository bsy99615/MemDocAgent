# `align.py`

## `hypertools.tools.align.align` · *function*

## Summary:
Performs hyperalignment or SRM-based alignment of multi-subject neuroimaging data to find a common shared response space.

## Description:
The align function provides two primary alignment methods for neuroimaging data: hyperalignment (default) and Shared Response Model (SRM). It processes input data to ensure compatibility with alignment algorithms, handles edge cases like insufficient data or dimensionality issues, and applies appropriate preprocessing steps. The function is designed to enable comparison of neural data across multiple subjects by projecting them into a common shared response space.

## Args:
    data (list): List of numpy arrays representing neuroimaging data from multiple subjects. Each array should have shape (samples, features).
    align (str or bool, optional): Alignment method to use. Options are 'hyper' for hyperalignment, 'SRM' for Shared Response Model, or True/False for legacy compatibility. Defaults to 'hyper'.
    normalize (None): Deprecated parameter for data normalization. Currently unused.
    ndims (None): Deprecated parameter for dimensionality reduction. Currently unused.
    method (str, optional): Legacy parameter for specifying alignment method. Superseded by align parameter. Defaults to None.
    format_data (bool, optional): Whether to apply preprocessing formatting to the data. Defaults to True.

## Returns:
    list: List of aligned numpy arrays, each transformed to the common shared response space. All arrays will have the same shape.

## Raises:
    ValueError: Raised when data has inconsistent shapes or insufficient samples for alignment.

## Constraints:
    Precondition: Input data must be a list of numpy arrays with compatible dimensions.
    Precondition: When using SRM alignment, data should have more samples than features per subject.
    Postcondition: All returned arrays will have identical shapes representing the aligned shared response space.

## Side Effects:
    Issues warnings for deprecated parameters, insufficient data, or potential overfitting conditions.
    May modify data through preprocessing steps when format_data=True.

## Control Flow:
```mermaid
flowchart TD
    A[Start align function] --> B{align is None?}
    B -- Yes --> C[Return original data]
    B -- No --> D{align is dict?}
    D -- Yes --> E{align['model'] is None?}
    E -- Yes --> C
    E -- No --> F[Process deprecated parameters]
    F --> G{align is True?}
    G -- Yes --> H[Set align='hyper']
    G -- No --> I[Check format_data]
    I --> J{len(data) == 1?}
    J -- Yes --> K[Warn and skip alignment]
    J -- No --> L{data[0].shape[1] >= data[0].shape[0]?}
    L -- Yes --> M[Warn about overfitting risk]
    L -- No --> N[Proceed to alignment method check]
    N --> O{align == 'hyper' or method == 'hyper'?}
    O -- Yes --> P[Execute hyperalignment algorithm]
    O -- No --> Q{align == 'SRM' or method == 'SRM'?}
    Q -- Yes --> R[Execute SRM alignment]
    Q -- No --> S[Return original data]
    P --> T[Return hyperaligned data]
    R --> U[Return SRM-aligned data]
```

## Examples:
```python
import numpy as np
from hypertools.tools.align import align

# Basic hyperalignment
data = [np.random.rand(100, 50), np.random.rand(120, 50)]
aligned_data = align(data, align='hyper')

# SRM alignment
aligned_data = align(data, align='SRM')

# Using deprecated method parameter (will warn)
aligned_data = align(data, method='hyper')

# Skip alignment completely
aligned_data = align(data, align=None)
```

