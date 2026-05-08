# `hypertools._externals`

## Tree:
_externals/
├── ppca.py
└── srm.py

## Role:
Provide local, self-contained implementations of two numeric algorithms needed by the repository: a Probabilistic PCA solver that handles missing numeric data and produces low-dimensional projections, and Shared Response Model (SRM) estimators (deterministic and probabilistic) for aligning multi-subject time-series. This module isolates algorithmic concerns (linear algebra, EM/SVD updates) from application logic and exposes small, documented estimator APIs for consumers.

## Description:
Where and when this module is used
- Used when code needs:
  - Robust linear dimensionality reduction that tolerates NaNs and computes explained variance (PPCA).
  - Multi-subject alignment of voxel/time-series into a common low-dimensional response (SRM/DetSRM).
- Typical consumers:
  - Visualization, preprocessing, and analysis code that imports PPCA or SRM/DetSRM to obtain embeddings or aligned signals.
  - Any internal pipelines that require lightweight, dependency-contained implementations of PPCA or SRM.

Why these components are grouped here
- Cohesion: both PPCA and SRM are numerical, linear-algebra-based algorithms that are conceptually related (latent subspace estimation). Grouping them keeps numerical routines together, preserves a clear layer boundary (algorithms vs application), and simplifies reuse/testing.

## Components:
Public classes (one-line descriptions and signatures)
- PPCA
  - Signature: PPCA()
  - One-line role: Probabilistic PCA estimator that fits a linear loading matrix from possibly incomplete numeric data and provides fit/transform/save/load utilities.
  - Primary public methods (see component docs for details): fit(data, d=None, tol=1e-4, min_obs=10, verbose=False), transform(data=None), save(fpath), load(fpath).

- SRM
  - Signature: SRM(n_iter: int = 10, features: int = 50, rand_seed: int = 0)
  - One-line role: Scikit-learn-compatible probabilistic Shared Response Model estimator for multi-subject alignment (fits per-subject transforms and a shared response).
  - Primary public methods: fit(X, y=None), transform(X, y=None).

- DetSRM
  - Signature: DetSRM(n_iter: int = 10, features: int = 50, rand_seed: int = 0)
  - One-line role: Deterministic SRM estimator (SVD/orthogonal updates) providing fit/transform APIs for multi-subject alignment.
  - Primary public methods: fit(X, y=None), transform(X, y=None).
  - transform input expectation: transform(X) expects X to be a sequence (e.g., list or tuple) of per-subject 2-D numeric arrays, where each element X[m] has shape (n_voxels_m, n_timepoints). The method returns a list of projected arrays, one per subject.

Core internal helpers (internal, not part of the public API)
- hypertools._externals.ppca.PPCA._standardize(X)
  - One-line role: Private helper to center and scale using stored means/stds; used inside PPCA.fit.
- hypertools._externals.ppca.PPCA._calc_var()
  - One-line role: Private helper to compute cumulative explained variance after fit.
- hypertools._externals.srm._init_w_transforms(data, features)
  - One-line role: Initialize per-subject orthonormal transforms via random matrices + QR.
- hypertools._externals.srm.SRM._init_structures(data, subjects)
  - One-line role: Prepare demeaned per-subject data, means, initial rho2, and trace statistics.
- hypertools._externals.srm.SRM._srm(data)
  - One-line role: Core iterative SRM optimizer (internal). Return value: tuple (sigma_s, w, mu, rho2, shared_response).
- hypertools._externals.srm.SRM._likelihood(...)
  - One-line role: Numeric objective calculator used for optional logging in the SRM EM loop.

Mermaid dependency graph (internal relationships)
graph LR
    PPCA[PPCA] --> PPCA._standardize
    PPCA --> PPCA._calc_var
    SRM[SRM] --> _init_w_transforms[_init_w_transforms]
    SRM --> _init_structures[_init_structures]
    SRM --> _srm[_srm]
    _srm --> _likelihood[_likelihood]
    DetSRM[DetSRM] --> DetSRM._srm[_srm (DetSRM variant)]
    style PPCA fill:#f9f,stroke:#333,stroke-width:1px
    style SRM fill:#9ff,stroke:#333,stroke-width:1px
    style DetSRM fill:#9ff,stroke:#333,stroke-width:1px

## Public API:
Summary of exported, intended-for-use interfaces with usage notes

- PPCA()
  - Constructor: PPCA()
  - Key methods:
    - fit(data, d=None, tol=1e-4, min_obs=10, verbose=False)
      - Fit the PPCA model from a 2-D numeric array (N×D_total). Replaces infinities in the supplied array in-place, filters columns by min_obs, computes means/stds, standardizes, performs EM-like estimation, and sets self.C, self.data, self.eig_vals, self.var_exp.
      - Usage note: Pass a copy if you must preserve the original array because fit mutates infinite values in-place.
    - transform(data=None)
      - If data is None: returns projection of internally-stored standardized data (self.data @ self.C).
      - If data is provided: returns data @ self.C; caller is responsible for standardizing provided data with PPCA._standardize.
    - save(fpath) / load(fpath)
      - Save persists self.C via numpy.save; load restores self.C via numpy.load but does not restore means/stds or data.

- SRM(n_iter=10, features=50, rand_seed=0)
  - Constructor: SRM(n_iter, features, rand_seed)
  - Key methods:
    - fit(X, y=None)
      - Validates input (len(X) >= 2, consistent timepoints, finite entries, timepoints >= features) and calls the internal _srm optimizer. On success assigns self.sigma_s_, self.w_, self.mu_, self.rho2_, self.s_ and returns self.
      - Note: fit seeds NumPy's global RNG via rand_seed (global RNG state modified).
    - transform(X, y=None)
      - Requires the estimator to be fitted (self.w_ exists). Returns a list where each element is self.w_[m].T.dot(X[m]) for subject m.
      - Usage note: len(X) must equal len(self.w_); matrix dimensions must be compatible.

- DetSRM(n_iter=10, features=50, rand_seed=0)
  - Constructor and method contracts mirror SRM above but use a deterministic/SVD-based variant in their internal _srm routine.
  - transform behavior:
    - transform(X) must be called after fit. X must be a sequence of per-subject 2-D numeric arrays (each with shape (n_voxels_m, n_timepoints)). The returned value is a list of per-subject projected arrays computed as self.w_[m].T.dot(X[m]).

Internal helpers and intended use
- Underscored helpers (e.g., _srm, _init_structures, _init_w_transforms, _standardize) are implementation details. They are accessible but considered private; callers should use the public estimator APIs (fit/transform/save/load) unless performing advanced testing or diagnostics.
- SRM._srm (and DetSRM._srm) return a tuple (sigma_s, w, mu, rho2, shared_response) — fit assigns these values to instance attributes.

## Dependencies:
External libraries
- numpy: array operations, nan-aware statistics, linear algebra.
- scipy.linalg: orthonormalization (orth), Cholesky factorization/solves, SVD/QR support.
- sklearn.utils.assert_all_finite: input validation in SRM.fit.
These are used for matrix computations and numerical stability.

Internal dependencies
- This module is self-contained with respect to other hypertools subpackages; higher-level code imports the estimator classes from hypertools._externals.

## Constraints:
Caller responsibilities and module constraints
- Fit-before-transform: Call fit(...) before calling transform() without supplying appropriately standardized data. If you load only a projection matrix (e.g., PPCA.load), you must restore or provide compatible standardized data to transform correctly.
- Data requirements:
  - PPCA.fit expects numeric 2-D arrays; NaNs are permitted (treated as missing) but infinities are replaced in-place; columns with insufficient non-NaN observations can be dropped by min_obs.
  - SRM/DetSRM.fit expects finite numeric arrays (no NaN/Inf), consistent timepoints across subjects, and at least two subjects.
- RNG and thread-safety:
  - SRM and some initialization helpers use NumPy's global RNG (np.random.seed, np.random.random). This mutates global RNG state and is not thread-safe. If you require isolation, manage RNG externally.
- File I/O:
  - PPCA.save/load delegate to numpy.save/load; load asserts file existence (assert may be skipped under python -O).
- Numerical stability:
  - Both PPCA and SRM perform matrix inversions, SVD/QR, and Cholesky factorizations; ill-conditioned inputs can raise numpy/scipy linear algebra exceptions (LinAlgError). Validate inputs (non-constant columns, sufficient observations) to reduce failure risk.

## Implementation pointers and where to read details:
- For precise method contracts, edge cases, exceptions, and per-attribute behavior, consult the component-level documentation:
  - hypertools._externals.ppca.PPCA and its methods (_standardize, _calc_var, fit, transform, save, load).
  - hypertools._externals.srm.SRM (including _srm, _init_structures, _init_w_transforms, _likelihood) and hypertools._externals.srm.DetSRM (including DetSRM._srm and transform).
- Notable internal contract: SRM._srm returns (sigma_s, w, mu, rho2, shared_response) which fit assigns to instance attributes.

---

## Files

- [`ppca.py`](_externals/ppca.md)
- [`srm.py`](_externals/srm.md)

