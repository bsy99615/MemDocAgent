# `ppca.py`

## `hypertools._externals.ppca.PPCA` · *class*

## Summary:
Probabilistic PCA (PPCA) model that learns a linear low-dimensional projection (loading matrix C) from possibly incomplete numeric data using an EM-like iterative algorithm; provides projection (transform), explained-variance metrics, and simple persistence (save/load) of the projection matrix.

## Description:
PPCA encapsulates a small PPCA solver that:
- Handles input arrays with NaN (missing) entries by performing expectation-style imputation during fitting.
- Replaces infinite values in the provided input with the maximum finite value present (in-place).
- Learns a projection / loading matrix C of shape (D, d) that maps D observed variables to d latent dimensions.

When to instantiate:
- Create an instance with PPCA() whenever you need a probabilistic PCA projection for data that may contain missing values.
- After instantiation, call fit(data, ...) to estimate the model before calling transform() without argument or _standardize()/_calc_var().

Why this abstraction exists:
- Provides a self-contained PPCA implementation with missing-data support and a minimal API for fitting, transforming, and persisting the learned projection matrix. It purposely excludes higher-level functionality (e.g., cross-validation, advanced I/O, automatic mean/std persistence) so callers compose those responsibilities.

## State:
After construction:
- raw: None
- data: None
- C: None
- means: None
- stds: None
- eig_vals: (not present until after fit)
- var_exp: (not present until after fit)

Attributes set by fit (types and shapes):
- raw (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (N, D_total) — equals the exact array object passed as the data argument to fit.
  - Notes: fit assigns self.raw = data and then modifies it in-place to replace infinite values; NaNs remain.
- data (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (N, D) — D is the number of columns retained after filtering by min_obs.
  - Notes: This is a standardized copy of the selected columns (mean-centered and divided by std); originally-missing entries are replaced with 0 for the EM iterations.
- C (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (D, d)
  - Invariant: After successful fit, columns of C are orthonormal (C.T @ C ≈ I_d).
  - Note: If you set self.C prior to calling fit, fit will use that matrix as an initialization (warm start). If self.C is None, fit initializes C randomly.
- means (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (D,)
  - Notes: Per-column means computed with numpy.nanmean on the retained columns; required by _standardize.
- stds (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (D,)
  - Notes: Per-column standard deviations from numpy.nanstd. The implementation does not guard against stds == 0; stds == 0 will produce infinities/nan during standardization and may break computations.
- eig_vals (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (d,)
  - Notes: Eigenvalues of the covariance of the projected data (used to compute var_exp).
- var_exp (numpy.ndarray)
  - Type: numpy.ndarray (float)
  - Shape: (d,)
  - Notes: Cumulative explained-variance ratio computed in _calc_var() from eig_vals and the total variance of the projected data.

Class invariants (post-fit):
- self.C is a 2D numpy array with shape (D, d).
- self.data is a 2D numpy array with shape (N, D), with missing entries used during fit replaced by 0 in the working copy.
- self.means and self.stds are both set and used for standardization via _standardize.
- self.eig_vals and self.var_exp exist and are consistent with the stored projection.

## Lifecycle:
Creation:
- ppca = PPCA()
  - No constructor arguments.

Primary usage sequence:
1. fit(data, d=None, tol=1e-4, min_obs=10, verbose=False)
   - Required argument:
     - data (numpy.ndarray): 2D array of shape (N, D_total). May contain NaN for missing values and +/-inf. WARNING: fit assigns this object to ppca.raw and modifies it in-place to replace infinities.
   - Optional arguments:
     - d (int or None): target latent dimensionality. If None, d is set to the number of retained columns after filtering (data.shape[1], i.e., D).
     - tol (float): relative convergence tolerance for the EM-like objective (default 1e-4).
     - min_obs (int): minimum number of non-NaN observations required for a column to be retained in the fit (default 10).
     - verbose (bool): if True, prints per-iteration relative differences.
   - Behavior and side effects:
     - Replaces infinite values in the provided data (in-place) with the maximum finite value found in the array.
     - Drops columns with fewer than min_obs non-NaN entries.
     - Computes means and stds with numpy.nanmean / numpy.nanstd and standardizes retained columns.
     - Replaces remaining NaNs with 0 in the working data for iterative estimation.
     - Initializes C from self.C if present (warm start) or randomly (np.random.randn) if not.
     - Iteratively updates latent scores X, loadings C, and variance ss until convergence as measured by relative change in the objective; no maximum-iteration cap is enforced besides the convergence criterion, but a minimum of >5 iterations is required before break if diff < tol.
     - At the end of fitting C is orthonormalized with scipy.linalg.orth and rotated by eigenvectors of the covariance of the projected data.
     - Sets self.C, self.data, self.eig_vals and calls _calc_var() to populate var_exp.
   - Important constraints:
     - If all columns are removed by min_obs, subsequent operations will fail (no explicit custom error is raised).
     - If any stds are zero, standardization divides by zero and will produce invalid values.
     - The caller may set numpy.random.seed before fit for reproducible random initialization.

2. transform(data=None)
   - Signature: transform(self, data=None)
   - Preconditions: self.C must not be None (otherwise raises RuntimeError with exact message 'Fit the data model first.').
   - Behavior:
     - If data is None: returns numpy.dot(self.data, self.C), with shape (N, d) where N is the stored number of observations in self.data.
     - If data is provided: returns numpy.dot(data, self.C). The caller is responsible for ensuring that data has compatible shape (n_rows, D) and appropriate standardization (e.g., use self._standardize on retained columns) — transform does not standardize input.
   - Return type: numpy.ndarray (float) with shape (n_rows, d).

3. _standardize(X)
   - Private helper that returns (X - self.means) / self.stds.
   - Raises RuntimeError("Fit model first") if self.means is None or self.stds is None.
   - Caller must provide X with shape compatible with means/stds: (n_rows, D).

4. _calc_var()
   - Recomputes self.var_exp using self.eig_vals and the variance (numpy.nanvar) of self.data (transposed) and sets self.var_exp = eig_vals.cumsum() / total_var.
   - Raises RuntimeError('Fit the data model first.') if self.data is None.

5. Persistence:
   - save(fpath)
     - Calls numpy.save(fpath, self.C). numpy.save will append the .npy extension if not present (behavior of numpy.save); the file will contain the array stored in self.C.
     - May raise file-system-related exceptions from numpy.save if writing fails.
   - load(fpath)
     - Asserts that os.path.isfile(fpath) is True; otherwise an AssertionError is raised.
     - Loads self.C via numpy.load(fpath).
     - Note: load only restores C. It does not restore means, stds, data, eig_vals, or var_exp. Callers must recompute or reassign those if needed (e.g., to project raw/unstandardized data consistently).

Destruction:
- No explicit cleanup, context management, or resource finalization is required.

## Method Map:
flowchart TD
    Init[PPCA.__init__()] --> Fit[fit(data,d=...,tol=...,min_obs=...,verbose=...)]
    Fit --> ReplaceInf[replace +/-inf in raw (in-place)]
    Fit --> FilterCols[filter columns by min_obs]
    Fit --> ComputeMeanStd[means,stds via nanmean/nanstd]
    ComputeMeanStd --> Standardize[_standardize(data)]
    Fit --> InitC[use self.C if present else random init]
    Fit --> EMloop[EM-like iterations: update X, C, ss]
    EMloop --> Orthonormalize[orth(C) + eigen-rotation]
    Orthonormalize --> SetState[self.C, self.data, self.eig_vals]
    SetState --> CalcVar[_calc_var()]
    CalcVar --> Transform[transform(data=None or data)]
    Transform --> Save[save(fpath)]
    Transform --> Load[load(fpath)]

## Raises:
- _standardize(X)
  - RuntimeError("Fit model first") if means or stds are not set.

- fit(...)
  - May raise numpy.linalg.LinAlgError or other numerical exceptions if matrix inversions/decompositions fail (e.g., singular matrices).
  - Division-by-zero or invalid-value warnings/exceptions may occur if any stds == 0.
  - No custom exception is raised if all columns are filtered out by min_obs; subsequent operations will generally raise shape or linear-algebra errors.

- transform(data=None)
  - RuntimeError('Fit the data model first.') if self.C is None.

- _calc_var()
  - RuntimeError('Fit the data model first.') if self.data is None.

- save(fpath)
  - File-system or numpy.save-related exceptions may be raised when attempting to write.

- load(fpath)
  - AssertionError if os.path.isfile(fpath) is False.
  - numpy.load-related exceptions may be raised if the file is not a valid numpy archive.

## Example (usage pattern, no source code):
- Instantiate PPCA().
- Call fit(data, d=desired_dim) with a 2D numpy array (observations × variables). Be aware that fit assigns the passed array to raw and will modify it in-place to replace infinite values. If you need to preserve the original array, pass a copy (e.g., data.copy()).
- After fit completes, call transform() with no arguments to get the low-dimensional embedding of the fitted, internally-standardized data; this returns an array of shape (N, d).
- To project external data, first standardize that data with the same means/stds used in fit (use ppca._standardize on the retained columns) and then call transform(data_standardized) to obtain projections.
- Use save(fpath) to persist the learned loading matrix self.C; in a new process use load(fpath) to restore C. Note that load only sets C — you must restore means/stds/data if you want to reproduce projections of raw data without re-fitting.

Practical recommendations:
- Set numpy.random.seed(...) externally for reproducible random initialization of C when self.C is None.
- Ensure no constant columns (std == 0) are passed to fit or preprocess them, because the implementation does not guard against zero standard deviation.
- If you expect many missing values, choose min_obs appropriately to retain useful columns.

### `hypertools._externals.ppca.PPCA.__init__` · *method*

## Summary:
Initializes a new PPCA object by creating and setting the instance attributes used by the model (raw, data, C, means, stds) to None, establishing the object's baseline state.

## Description:
This method is the class constructor and is executed automatically when a PPCA instance is created (i.e., when PPCA() is called). It centralizes initialization of the instance attributes so that subsequent methods (fitting, transforming, or inspecting) can rely on the attributes' existence even before they are assigned meaningful values.

Known callers:
- The Python runtime when instantiating the PPCA class (PPCA()).
- Any factory, higher-level routine, or test that constructs a PPCA object prior to calling fit/transform methods.

Why this is a separate method:
- As the class constructor, it must exist to properly allocate instance attributes and provide a consistent initial state. Keeping initialization here prevents AttributeError in other methods and makes the class invariants explicit.

## Args:
This constructor takes no parameters.

## Returns:
None (constructors in Python implicitly return the new instance). There is no meaningful return value from this method.

## Raises:
This method does not raise any exceptions.

## State Changes:
Attributes READ:
- None

Attributes WRITTEN (set on self):
- self.raw: set to None
- self.data: set to None
- self.C: set to None
- self.means: set to None
- self.stds: set to None

## Constraints:
Preconditions:
- None. The method may be called on a newly-created PPCA instance by the Python object model; no attribute values are required beforehand.

Postconditions:
- After execution, the instance has the attributes raw, data, C, means, and stds defined on self, each with the value None.
- The object is in a stable, minimal-initialized state suitable for subsequent calls to methods that will populate these attributes (e.g., fit, load, or set-data routines).

## Side Effects:
- No I/O, no external service calls, and no mutations of objects external to self occur. The method only assigns attributes on the instance.

### `hypertools._externals.ppca.PPCA._standardize` · *method*

## Summary:
Standardizes input data by centering with the pretrained column means and scaling by the pretrained column standard deviations; does not modify object state.

## Description:
This method is called by PPCA.fit during the preprocessing step immediately after computing column-wise means and standard deviations and before downstream EM iterations and missing-value handling. Specifically, PPCA.fit computes self.means and self.stds, then invokes this method to produce a z-scored version of the input data.

The logic is isolated into its own method to centralize the standardization behavior and the precondition check (ensuring the model has been fit / means and stds are available), making the preprocessing step reusable and easier to test.

Known callers:
    - PPCA.fit: invoked right after self.means and self.stds are set, to standardize the training data prior to EM updates.

## Args:
    X (numpy.ndarray):
        Numeric array of observations to standardize. Expected to be 2-D with shape (N, D) where D equals the length of self.means and self.stds, or otherwise broadcastable so that column-wise subtraction/division is meaningful.
        Elements may be NaN (they are preserved through the arithmetic).

## Returns:
    numpy.ndarray:
        A new array with the same shape as X containing the standardized values computed elementwise as (X - self.means) / self.stds.
        - NaN entries in X remain NaN in the result.
        - If any entry of self.stds is zero, division yields NumPy infinities or NaNs at those columns (no special handling in this method).
        - If X has an incompatible shape that cannot be broadcast against self.means/self.stds, NumPy will raise a broadcasting/ValueError.

## Raises:
    RuntimeError:
        If either self.means or self.stds is None. Message: "Fit model first".
    ValueError / broadcasting errors (propagated from NumPy):
        If X cannot be broadcast against self.means/self.stds (this method does not validate shapes beyond relying on NumPy broadcasting).

## State Changes:
    Attributes READ:
        - self.means
        - self.stds
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> fields)

## Constraints:
    Preconditions:
        - The PPCA instance must have been prepared by calling fit (so self.means and self.stds are non-None).
        - self.means and self.stds are expected to be 1-D arrays whose length matches the number of columns in X (or is broadcast-compatible).
    Postconditions:
        - Returns an array whose values equal (X - self.means) / self.stds computed elementwise; self attributes are unchanged.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self (the input X is not modified unless the caller passes a view and relies on in-place semantics from NumPy broadcasting — the method returns a new array expression).
    - Any exceptions from NumPy arithmetic (e.g., due to incompatible shapes or invalid operations) propagate to the caller.

### `hypertools._externals.ppca.PPCA.fit` · *method*

## Summary:
Estimate a probabilistic PCA model from input data (handling NaNs and infinities) and update the instance with learned factor loadings, standardized training data, ordered eigenvalues, and explained-variance; the method mutates instance state and does not return a value.

## Description:
This method performs the full PPCA training routine (preprocessing, EM-like parameter estimation, and postprocessing). Typical usage is model.fit(data, ...) as the principal training step before calling transform, saving, or inspecting explained variance.

Known callers and lifecycle stage:
- Called directly by user code to train a PPCA instance (e.g., PPCA().fit(data)).
- Invoked in the model training stage immediately prior to using transform() or save()/load().
- Internally calls PPCA._standardize to z-score selected features and PPCA._calc_var to compute cumulative explained variance at the end.

Why this is a separate method:
- The procedure contains non-trivial preprocessing, an iterative EM-like update routine, and postprocessing (orthogonalization and eigen-rotation). Encapsulating this in a single method keeps responsibilities localized and avoids duplicating complex logic.

## Args:
    data (numpy.ndarray):
        2-D numeric array with shape (N, D_total) where N is number of observations (rows) and D_total is the total number of feature series (columns). The array may contain numpy.nan for missing values and +/-numpy.inf for infinite values.
        Behavior:
            - Assigned to self.raw (reference to the same object).
            - +/-inf entries in self.raw are replaced in-place with the maximum finite value present in self.raw.
        Notes:
            - If the array contains no finite values (all entries are NaN or infinite), replacing infinities uses np.max on an empty array and will raise a ValueError.
    d (int or None, optional):
        Target latent dimensionality (number of components). If None, defaults to the number of columns retained after filtering by min_obs.
        Allowed values: integer >= 1. If d is incompatible with the selected feature count D (e.g., mismatch with a pre-set self.C), linear-algebra operations will fail.
        Default: None.
    tol (float, optional):
        Relative convergence tolerance used on the objective-like quantity. The algorithm stops when the relative change falls below tol and at least 6 iterations have completed.
        Must be a small positive float. Default: 1e-4.
    min_obs (int, optional):
        Minimum number of non-NaN observations required for a feature (column) to be kept for fitting. Columns with fewer than min_obs valid entries are dropped.
        Must be an integer >= 0. Default: 10.
    verbose (bool, optional):
        If True, prints the relative change (diff) each EM iteration for monitoring convergence. Default: False.

## Returns:
    None.
    - All learned parameters and bookkeeping fields are stored on self (see State Changes). The method does not return a value.

## Raises:
    ValueError:
        - If replacing infinities requires computing the maximum of an empty finite set (e.g., all entries are NaN or non-finite).
        - If no columns remain after filtering with min_obs, downstream code will typically raise a ValueError or IndexError due to D == 0 (this method does not explicitly raise in that case).
    RuntimeError:
        - If helper methods (_standardize or _calc_var) raise RuntimeError due to unexpected internal state (these are normally prevented because fit sets required fields).
    numpy.linalg.LinAlgError:
        - Propagated when matrix inverse, determinant, or eigendecomposition fail due to singular or ill-conditioned matrices.
    TypeError / ValueError (NumPy):
        - If data is not numeric or has an incompatible shape for the operations performed; broadcasting errors raised by NumPy will propagate.

## State Changes:
Attributes READ:
    - self.C: used to determine whether to initialize C randomly or reuse an existing matrix.

Attributes WRITTEN:
    - self.raw (numpy.ndarray): set to the provided data object reference; +/-inf entries replaced in-place.
    - self.means (1-D numpy.ndarray, shape (D,)): column-wise means of the selected features computed via numpy.nanmean.
    - self.stds (1-D numpy.ndarray, shape (D,)): column-wise standard deviations computed via numpy.nanstd.
    - self.data (2-D numpy.ndarray, shape (N, D)): standardized copy of the selected features used for fitting; missing entries are initially set to 0 and later imputed during iterations.
    - self.C (2-D numpy.ndarray, shape (D, d)): final orthogonalized factor-loading matrix with columns ordered by descending explained variance after rotation.
    - self.eig_vals (1-D numpy.ndarray, length k where k == number of columns of rotated C): eigenvalues of covariance of projected data, sorted descending.
    - self.var_exp (1-D numpy.ndarray): cumulative fraction of variance explained (set by _calc_var).

## Key intermediate array shapes (for implementers):
    - raw: (N, D_total)  (input)
    - valid_series: (D_total,) boolean mask
    - data (after filtering): (N, D) where D is number of kept features
    - C: (D, d)
    - CC = C.T @ C: (d, d)
    - X: (N, d)  (latent scores / posterior means)
    - Sx: (d, d) (posterior covariance matrix per observation, same for all)
    - XX = X.T @ X: (d, d)
    - recon = X @ C.T: (N, D)
    - eig_vals / eig_vecs produced from eig(cov(data @ C).T): eig_vals length equals number of columns in C

## Behavior and algorithmic steps (detailed):
1. Preprocessing:
    - Assign provided data to self.raw.
    - Replace +/-inf in self.raw with the maximum finite value found in self.raw:
        finite_mask = numpy.isfinite(self.raw)
        if not finite_mask.any(): raising ValueError occurs when calling numpy.max on an empty slice.
        self.raw[~finite_mask] = numpy.max(self.raw[finite_mask])
    - Compute valid_series = numpy.sum(~numpy.isnan(self.raw), axis=0) >= min_obs and keep only those columns:
        data = self.raw[:, valid_series].copy()
      Set N = data.shape[0], D = data.shape[1].
    - Compute self.means = numpy.nanmean(data, axis=0) and self.stds = numpy.nanstd(data, axis=0).
    - Standardize with self._standardize(data) which computes (data - self.means) / self.stds (NaNs preserved).
    - observed = ~numpy.isnan(data); missing = int(numpy.sum(~observed)); then set data[~observed] = 0 for initial computations.

2. Initialization:
    - If d is None, set d = D (number of kept features).
    - Initialize C:
        - If self.C is None: C = numpy.random.randn(D, d)
        - Else: C = self.C (caller is expected to ensure compatible shapes)
    - Compute CC = C.T @ C.
    - Initialize latent scores X = data @ C @ inv(CC).
    - Compute initial reconstruction recon = X @ C.T and set recon[~observed] = 0.
    - Estimate initial noise variance ss = sum((recon - data)**2) / (N*D - missing).

3. Iterative EM-like updates (repeat until convergence):
    - v0 initialized to numpy.inf and counter = 0.
    - Loop:
        - Compute Sx = inv(I_d + CC/ss) where I_d is identity matrix of size d.
        - Store ss0 = ss.
        - If missing > 0: proj = X @ C.T; use proj's values to fill missing entries in data (data[~observed] = proj[~observed]).
        - Update X = (data @ C @ Sx) / ss.
        - Compute XX = X.T @ X.
        - Update C = data.T @ X @ pinv(XX + N*Sx)  (pseudoinverse for numerical stability).
        - Recompute CC, recon = X @ C.T (and recon[~observed] = 0), then update ss:
            ss = (sum((recon - data)**2) + N * sum(CC * Sx) + missing * ss0) / (N * D)
        - Compute det = log(det(Sx)). If det is infinite, fall back to abs(slogdet(Sx)[1]) to obtain a finite magnitude.
        - Compute objective-like scalar v1 = N*(D*log(ss) + trace(Sx) - det) + trace(XX) - missing*log(ss0).
        - diff = abs(v1/v0 - 1). If verbose is True, print diff.
        - If (diff < tol) and counter > 5: break.
        - Increment counter and set v0 = v1.

    Notes:
        - The algorithm requires at least 6 iterations before allowing early termination (counter > 5).
        - Using pinv for XX + N*Sx helps when XX is rank-deficient.

4. Postprocessing:
    - Orthogonalize C: C = scipy.linalg.orth(C) (returns orthonormal basis for span of C).
    - Project data onto orthonormal directions and compute covariance: cov = numpy.cov((data @ C).T).
    - Compute eigendecomposition vals, vecs = numpy.linalg.eig(cov). Order eigenvalues descending and reorder eigenvectors accordingly.
    - Rotate C by vecs so that columns are aligned with descending-variance directions: C = C @ vecs.
    - Store final parameters:
        self.C = C
        self.data = data   (standardized data with imputed missing entries)
        self.eig_vals = vals (ordered descending)
    - Call self._calc_var() to compute and store self.var_exp (cumulative explained variance).

## Constraints and preconditions:
    - Input must be a numeric 2-D array-like with shape (N, D_total).
    - At least one column must remain after filtering by min_obs; otherwise the algorithm cannot proceed sensibly.
    - If reusing a pre-existing self.C, its shape must be compatible with the retained number of columns D and the chosen d; mismatches will raise linear algebra errors.
    - self.stds must not contain zeros in columns that will be standardized; otherwise standardization produces infinities/NaNs and may cause failure.

## Postconditions (guarantees after successful call):
    - self.raw references the input array with infinities replaced.
    - self.means and self.stds contain column-wise statistics for the retained features.
    - self.data is the standardized training matrix of shape (N, D) with missing entries imputed by the final projections.
    - self.C is orthogonalized and rotated so columns are ordered by descending explained variance; shape is (D, d).
    - self.eig_vals contains eigenvalues sorted descending and self.var_exp (set by _calc_var) contains cumulative explained-variance fractions.
    - transform() can be used to project stored data (when called with no argument it returns self.data @ self.C). If projecting new raw data, the caller must standardize the new data using the stored self.means and self.stds before calling transform(new_standardized_data).

## Side Effects:
    - Mutates the provided data array in-place via self.raw when replacing infinite values.
    - Allocates temporary arrays; memory usage scales with N*D and D*d.
    - Does not perform file I/O or network activity.
    - May emit NumPy runtime warnings (e.g., invalid or divide-by-zero) and may raise NumPy/Scipy exceptions for singular matrices.

## Implementation hints:
    - Use numpy.isfinite to detect finite entries and handle the empty-finite case explicitly to provide a clear error.
    - Use numpy.nanmean/nanstd for column statistics so NaNs are ignored.
    - For stability, use numpy.linalg.pinv when inverting XX + N*Sx and handle determinant log with numpy.linalg.slogdet fallback.
    - Ensure the pre/post shape expectations above are enforced or clearly documented so callers know how to prepare data and any reusable self.C.

### `hypertools._externals.ppca.PPCA.transform` · *method*

## Summary:
Project data into the PPCA latent subspace using the learned loading matrix, returning the low-dimensional representation. Does not modify the PPCA object's attributes.

## Description:
This method computes the linear projection of input observations onto the principal subspace stored in the model (the loading matrix). It is intended to be used after the model has been fitted (or a loading matrix loaded) to obtain the d-dimensional latent coordinates for either the data used during fit or for new observations.

Known callers and typical context:
- Called by downstream code that needs the low-dimensional embedding produced by PPCA after fit. In typical usage it is invoked immediately after PPCA.fit(...) to obtain the projection of the fitted dataset, or later to project new data for visualization, clustering, or further processing.
- No callers are required inside this file; the method is a public API for consumers of PPCA.

Why this is a separate method:
- Projection is a distinct operation from model fitting and variance calculation; separating it keeps responsibilities clear (fit builds the model and stores the loading matrix, transform applies the model).
- It allows projecting arbitrary datasets (including held-out or streaming data) without re-fitting.

## Args:
    data (numpy.ndarray or array-like, optional): 
        2-D array of shape (N, D) where N is the number of observations and D is the number of features expected by the model (must match the first dimension of the model's loading matrix self.C). If omitted (None), the stored, standardized dataset self.data is projected. Default: None.

## Returns:
    numpy.ndarray:
        2-D array of shape (N, d) where d == self.C.shape[1] is the dimensionality of the latent subspace (number of columns in self.C). 
        - If data is None, returns np.dot(self.data, self.C).
        - If data is provided, returns np.dot(data, self.C).
        Edge cases:
        - If provided data is empty (zero rows), returns an array with shape (0, d).
        - If data or self.data has incompatible number of columns (not equal to self.C.shape[0]), numpy will raise a ValueError during the dot product.

## Raises:
    RuntimeError:
        If self.C is None. The method raises RuntimeError('Fit the data model first.') to indicate that no loading matrix is available because the model was not fitted or no C has been loaded.

    ValueError / TypeError:
        Propagated from numpy.dot if the provided data (or stored self.data) is not array-like, has incorrect dimensionality (should be 2-D), or its second dimension does not match self.C.shape[0]. These errors are not raised explicitly by transform but are possible when numpy attempts the matrix multiplication.

## State Changes:
    Attributes READ:
        self.C
        self.data

    Attributes WRITTEN:
        None — this method does not modify the object's attributes.

## Constraints:
    Preconditions:
        - self.C must be not None (model fit or C loaded).
        - If data is None: self.data must be not None and correctly shaped (N, D).
        - If data is provided: it must be a 2-D array-like object with dtype compatible for numpy.dot and with second dimension equal to self.C.shape[0].
        - If projecting raw (unstandardized) observations, the caller must standardize them (using the same means and stds used to fit the model) before calling transform. The method does not perform automatic standardization.

    Postconditions:
        - On successful return, no attributes of self are changed.
        - Returned array has shape (N, d) where d == self.C.shape[1].

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self (the input data argument is not modified by this method).
    - May propagate exceptions raised by numpy operations (e.g., due to type or shape mismatches).

## Usage notes and recommendations:
    - Typical use after fitting:
        1. Call ppca.fit(raw_data, ...) which sets self.means, self.stds, self.data, and self.C.
        2. To project the fitted dataset, call ppca.transform() with no arguments.
        3. To project new raw observations, first standardize them using the same parameters:
           standardized = ppca._standardize(new_raw_data)
           latent = ppca.transform(standardized)
    - Loading only a saved C (via load) without also setting self.data means transform() with data=None will fail (self.data is None). Provide a data argument in that case.

### `hypertools._externals.ppca.PPCA._calc_var` · *method*

## Summary:
Compute and store the cumulative fraction of total data variance explained by the model eigenvalues, updating the instance state.

## Description:
Known callers and lifecycle:
- Called by PPCA.fit immediately after self.data and self.eig_vals are computed and assigned. This is the finalization step of model fitting where variance-explained information is derived for later use (e.g., for plotting or deciding how many components to keep).
- May also be invoked manually if a user modifies or reloads self.data or self.eig_vals and needs to recompute the explained-variance vector.

Why this is a separate method:
- Isolates the explained-variance calculation from the longer EM-style fitting routine, keeping fit focused on parameter estimation and leaving bookkeeping (normalization and storage of variance-explained) to a single, testable function.
- Encourages reuse (recompute var_exp without repeating parts of fit) and improves readability.

## Args:
- None.

## Returns:
- None.
- Side effect: self.var_exp is set to a numpy.ndarray described below.

## Raises:
- RuntimeError('Fit the data model first.') 
    - Raised when self.data is None, i.e., fit has not been run (or self.data was not otherwise initialized).

## State Changes:
Attributes READ:
- self.data (expected: numpy.ndarray)
    - Interpretation: standardized data matrix with shape (N, D) where N is number of observations and D is number of features; fit sets this attribute before calling this method.
- self.eig_vals (expected: numpy.ndarray, 1-D)
    - Interpretation: eigenvalues produced from the covariance of projected data (length k, typically k <= D).

Attributes WRITTEN:
- self.var_exp (numpy.ndarray, 1-D)
    - After the call, contains the cumulative explained-variance fraction computed as cumulative_sum(self.eig_vals) / total_var.

## Constraints:
Preconditions:
- self.data must not be None (otherwise a RuntimeError is raised).
- self.eig_vals must be present and numeric (1-D array). The method does not explicitly validate this, so callers should ensure eig_vals has been set (fit sets it).
- The numeric interpretation assumes self.data rows are observations (N) and columns are features (D) prior to the method transposing it; in the PPCA.fit pipeline, self.data has shape (N, D).

Postconditions (guarantees after successful call):
- self.var_exp is a numpy.ndarray with length equal to len(self.eig_vals).
- Each entry equals the cumulative sum of self.eig_vals up to that index divided by total_var, where total_var is the sum of per-feature variances computed from self.data.
- If self.eig_vals contains non-negative values and total_var > 0, self.var_exp is non-decreasing and ranges from eig_vals[0]/total_var up to 1.0 for the final element (modulo floating point rounding).

## Edge cases and numerical considerations:
- The method uses numpy.nanvar to compute per-feature variances and therefore tolerates NaN values in self.data (variance is computed ignoring NaNs). If an entire feature column is NaN, nanvar returns NaN for that feature which will propagate into total_var and produce NaNs in self.var_exp.
- If total_var is zero (all features have zero variance), division yields inf or NaN values and no special handling is performed; callers should avoid or handle this situation if it can occur.
- If self.eig_vals contains negative entries (unexpected for covariance eigenvalues), the cumulative fractions may be non-monotonic or contain negative values; the method does not validate eigenvalue signs.

## Side Effects:
- No I/O, no external service calls.
- Mutates only the instance attribute self.var_exp.
- Uses numpy operations (np.nanvar and vectorized arithmetic) and thus may emit numpy runtime warnings (e.g., for invalid value encountered in true_divide or nanvar on all-NaN slices).

## Implementation notes (for reimplementation):
- Compute per-feature variance across observations as var = numpy.nanvar(self.data.T, axis=1).
- Compute total_var = var.sum() (scalar).
- Compute cumulative explained variance as numpy.cumsum(self.eig_vals) / total_var and assign to self.var_exp.
- Ensure the method raises RuntimeError('Fit the data model first.') if self.data is None.

### `hypertools._externals.ppca.PPCA.save` · *method*

## Summary:
Persist the model's projection matrix by calling np.save with the provided file destination and the current value of self.C.

## Description:
Writes the projection matrix (self.C) to disk by delegating the operation directly to np.save. Typical usage and lifecycle:
- Invoked after a successful PPCA.fit when the projection matrix has been computed and stored in self.C.
- Used by callers performing model checkpointing or when saving a trained PPCA model for later restoration.
This functionality is factored into its own method to centralize persistence behavior and to provide a symmetric API with PPCA.load.

## Args:
    fpath: Passed unchanged as the first argument to np.save. The method does not validate or modify this argument.

## Returns:
    None. The method does not return a value.

## Raises:
    Propagates any exception raised by np.save. The method itself performs no error handling. Calling code should expect and handle exceptions from the underlying np.save call (for example, filesystem-related I/O errors).

## State Changes:
    Attributes READ:
        self.C

    Attributes WRITTEN:
        none — this method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - For meaningful persistence, self.C should contain the learned projection matrix (typically set by PPCA.fit). If self.C is None, np.save will be called with None; behavior in that case is determined by np.save.
        - The caller is responsible for ensuring that fpath is a valid destination for np.save.

    Postconditions:
        - If np.save completes successfully, the destination provided to np.save will contain NumPy's serialized representation of self.C.
        - The in-memory attribute self.C remains unchanged.

## Side Effects:
    - Filesystem I/O via np.save (writing or overwriting the target destination).
    - No network calls or mutations of objects external to self, aside from the file produced/overwritten by np.save.

### `hypertools._externals.ppca.PPCA.load` · *method*

## Summary:
Loads a NumPy file from disk and stores its contents onto the instance, replacing the object's C attribute.

## Description:
This method performs a single-step deserialization of a previously saved NumPy object and stores the loaded object on the PPCA instance as attribute C.

Known callers and lifecycle context:
- No explicit callers are identified here; typically this method is invoked during a model/state deserialization or initialization step when an existing PPCA component matrix (or other NumPy-saved object) needs to be restored from disk prior to further processing or inference.
- It is separated into its own method to encapsulate the file-existence check and the assignment to the instance state (self.C), making load semantics explicit and simple to reuse anywhere the PPCA object's C attribute needs to be restored.

## Args:
    fpath (str or os.PathLike): Path to a filesystem entry expected to be a regular file that contains data saved by NumPy (for example, .npy or .npz files). No other types are validated; passing non-string path-like objects that os.path.isfile accepts is supported.

## Returns:
    None
    - The method does not return a value. Its effect is to set/overwrite self.C with the value returned by numpy.load(fpath).

## Raises:
    AssertionError:
        - If os.path.isfile(fpath) evaluates to False, the method triggers an AssertionError due to the assert statement.
        - Note: since this uses the assert statement, the check is skipped when Python is run with optimizations enabled (python -O), which can remove this guard.
    Any exception raised by numpy.load(fpath):
        - numpy.load may raise exceptions (for example, IOError/FileNotFoundError on I/O failure, ValueError for incompatible file content, or other numpy-specific errors). Those exceptions are not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - None of the instance attributes are read by this method.
    Attributes WRITTEN:
        - self.C: overwritten (or created) and set to the exact object returned by numpy.load(fpath).

## Constraints:
    Preconditions:
        - fpath must point to an existing regular file on disk. The method asserts this using os.path.isfile(fpath).
        - The file at fpath must be in a format accepted by numpy.load (e.g., .npy or .npz, or another format numpy.load can parse). The caller must ensure compatibility between how the data was saved and how it will be used after loading.
    Postconditions:
        - After successful completion, self.C references the object returned by numpy.load(fpath). No other attributes on self are changed.
        - If the assert fails or numpy.load raises, self.C is not modified by this method (the assignment occurs only after the assert and load complete).

## Side Effects:
    - Performs disk I/O by reading the file at fpath via numpy.load.
    - No network or external service calls.
    - No other objects are mutated by this method beyond setting self.C on the instance.
    - Exceptions from numpy.load propagate to the caller; there is no internal error handling or logging.

