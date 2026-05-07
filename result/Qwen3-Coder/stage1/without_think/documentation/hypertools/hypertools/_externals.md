# `hypertools._externals`

## Tree:
    _externals/
    ├── ppca.py
    └── srm.py

## Role:
    Provides external implementations of dimensionality reduction and shared response modeling techniques for handling multi-subject neuroimaging and general data analysis tasks.

## Description:
    The _externals module serves as a repository for specialized algorithms that extend beyond basic machine learning functionality. It contains implementations of probabilistic principal component analysis (PPCA) for handling missing data and shared response models (SRM) for aligning multi-subject neuroimaging data. These algorithms are used primarily in neuroscience research applications where data often contains missing values or needs to be aligned across different subjects.

    This module is consumed by various analysis pipelines in the hypertools package that require robust dimensionality reduction capabilities and multi-subject data alignment. The components are particularly valuable for preprocessing neuroimaging data before further analysis or visualization.

## Components:
    - PPCA (probabilistic principal component analysis): Implements a probabilistic approach to PCA that handles missing data points effectively
    - DetSRM (deterministic shared response model): Finds a common neural response space across multiple subjects using deterministic optimization
    - SRM (probabilistic shared response model): Implements a probabilistic shared response model for aligning multi-subject neuroimaging data

    ```mermaid
    graph TD
        A[PPCA] --> B[DetSRM]
        A --> C[SRM]
        B --> D[Shared Response Space]
        C --> D
    ```

## Public API:
    - `PPCA`: Class for probabilistic principal component analysis with missing data handling
      - Signature: `PPCA()`
      - Brief description: Implements probabilistic PCA that can handle missing data points
      - Usage note: Typically used for dimensionality reduction in datasets with missing values
      
    - `DetSRM`: Class for deterministic shared response model
      - Signature: `DetSRM(n_iter=10, features=50, rand_seed=0)`
      - Brief description: Finds a common neural response space across multiple subjects using deterministic optimization
      - Usage note: Used for aligning neuroimaging data from different subjects
      
    - `SRM`: Class for probabilistic shared response model
      - Signature: `SRM(n_iter=10, features=50, rand_seed=0)`
      - Brief description: Implements a probabilistic shared response model for aligning multi-subject neuroimaging data
      - Usage note: Alternative probabilistic implementation of shared response modeling

## Dependencies:
    - Internal: None
    - External: 
      - numpy: Required for all mathematical operations and array manipulations
      - scipy: Used for numerical optimization and linear algebra operations

## Constraints:
    - All algorithms expect numeric data inputs
    - PPCA can handle missing data points in the input data
    - SRM implementations require at least 2 subjects for training
    - Both PPCA and SRM models must be fitted before transformation operations can be performed
    - Thread safety: These implementations are not thread-safe and should not be shared across threads without synchronization

---

## Files

- [`ppca.py`](_externals/ppca.md)
- [`srm.py`](_externals/srm.md)

