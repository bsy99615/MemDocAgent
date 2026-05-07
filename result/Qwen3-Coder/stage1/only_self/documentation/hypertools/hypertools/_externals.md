# `hypertools._externals`

## Tree:
    _externals/
    ├── ppca.py
    └── srm.py

## Role:
    Houses specialized statistical algorithms for dimensionality reduction and multi-subject data alignment in neuroimaging applications.

## Description:
    The `_externals` module contains specialized implementations of statistical algorithms that extend the core capabilities of hypertools for advanced data analysis. These algorithms are primarily designed for neuroimaging data processing but can be applied to general statistical modeling tasks. The module provides two main families of algorithms: probabilistic dimensionality reduction techniques and shared response modeling approaches for aligning multi-subject data.

    The module is imported and utilized by various analysis components within the hypertools framework that require robust statistical methods for preprocessing, feature extraction, and data alignment operations. These implementations offer enhanced capabilities compared to standard algorithms, particularly in handling missing data and aligning heterogeneous datasets from multiple subjects.

## Components:
    - PPCA: Probabilistic Principal Component Analysis implementation that handles missing data points and provides methods for fitting models, transforming data, and saving/loading learned projection matrices.
    - DetSRM: Deterministic Shared Response Model transformer implementing scikit-learn compatible interfaces for aligning multi-subject neuroimaging data by finding common response patterns across subjects.
    - SRM: Statistical Reuse Method implementation providing probabilistic shared response modeling for multi-subject neuroimaging data alignment.

## Public API:
    - `PPCA`: Class for probabilistic PCA with missing data handling
    - `DetSRM`: sklearn-compatible transformer for deterministic shared response modeling
    - `SRM`: Class for probabilistic shared response modeling

## Dependencies:
    - Internal: None
    - External: numpy, scipy, sklearn (for validation and base classes)

## Constraints:
    - All algorithms require numeric input data with compatible dimensions
    - PPCA requires data with potentially missing values (NaN) that it can handle appropriately
    - SRM implementations require consistent number of samples across subjects
    - Models must be fitted before transformation operations can be performed
    - Thread safety is not guaranteed for in-place operations on fitted models

---

## Files

- [`ppca.py`](_externals/ppca.md)
- [`srm.py`](_externals/srm.md)

