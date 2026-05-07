# `srm.py`

## `hypertools._externals.srm._init_w_transforms` · *function*

## Summary:
Create per-subject orthonormal transform matrices by QR-decomposing randomly-initialized matrices; return the list of Q factors (one per subject) and a 1-D integer array of per-subject voxel counts.

## Description:
This internal helper initializes per-subject transform matrices used by an SRM-style estimator. For each subject in the provided collection it:
- reads the subject's voxel count from data[i].shape[0],
- allocates a random matrix of shape (voxels_i, features) using NumPy's RNG,
- computes a QR decomposition of that random matrix and takes the orthonormal Q factor as the subject's transform.

Known callers and typical context:
- Intended to be invoked by estimator initialization code (for example, an SRM.fit or an SRM._initialize routine) that requires per-subject orthonormal starting transforms prior to iterative fitting.
- No explicit callers were supplied in the provided snippet; treat this as an internal initialization helper.

Why this logic is separated:
- Encapsulates the initialization policy (random sampling + orthonormalization), isolating RNG usage and linear-algebra decisions from estimator control flow and making the strategy easier to test or replace.

## Args:
    data (Sequence[array-like]):
        - Name in code: data
        - A sized, indexable sequence (e.g., list or tuple) whose elements are array-like objects exposing a shape attribute.
        - For subject i, the function reads data[i].shape[0] to determine voxels_i (an integer).
        - Only the first axis (rows) is inspected; other dimensions are ignored.
    features (int):
        - Name in code: features
        - Desired number of latent features (columns) used when building the random matrix.
        - Must be an integer. For meaningful non-empty Q columns, features should be >= 1; features == 0 will produce empty column dimension and is allowed by NumPy allocation but yields no transform columns.

## Returns:
    tuple (w, voxels)
    - w (list[numpy.ndarray]):
        - A list with length equal to len(data). For subject i, w[i] is the Q factor returned by NumPy's QR decomposition of a random (voxels_i, features) matrix.
        - w[i].shape == (voxels_i, k) where k == min(voxels_i, features) (reduced QR yields Q with shape (M, min(M, N))).
        - Columns of w[i] are orthonormal (within numerical precision) and suitable as initial per-subject transforms.
    - voxels (numpy.ndarray of dtype int):
        - 1-D integer array of length len(data) with voxels[i] == int(data[i].shape[0]) for each subject.

Edge-case returns:
- If len(data) == 0: returns w as an empty list and voxels as an empty numpy integer array with shape (0,).
- If any voxels_i == 0 or features == 0: behavior follows NumPy's handling of zero-dimension arrays; returned Q may have zero columns or NumPy may raise an error depending on version. This is uncommon in normal use.

## Raises:
    TypeError:
        - If data is not a sized/indexable sequence (len(data) or indexing raises TypeError) or if features cannot be interpreted as an integer.
    AttributeError:
        - If an element data[i] does not have a .shape attribute (accessing data[i].shape fails).
    ValueError:
        - If features is negative or otherwise invalid for array allocation, NumPy will raise ValueError when attempting to create the random matrix.
    numpy.linalg.LinAlgError:
        - If NumPy's QR decomposition fails for numerical reasons on a particular random matrix (unlikely for random matrices), QR may raise LinAlgError.

## Constraints:
Preconditions:
- data must be a sequence with a valid length (len(data) succeeds) and indexable elements.
- For every subject i, data[i] must be array-like with a .shape attribute where data[i].shape[0] is an integer >= 0.
- features must be an integer; non-integer or negative values will typically cause allocation or type errors.

Postconditions:
- len(w) == len(data).
- voxels is a NumPy integer array with length len(data) and voxels[i] == int(data[i].shape[0]).
- For each i, w[i] has shape (voxels[i], min(voxels[i], features)) and contains orthonormal columns (Q factor), subject to numerical precision.

## Side Effects:
- Consumes/modifies the global NumPy RNG state by calling NumPy's random generator (np.random.random in the implementation). This affects subsequent uses of the global RNG unless a local RNG is used instead.
- No file, network, or stdout/stderr I/O.
- Does not mutate the input arrays; it only reads data[i].shape.

## Control Flow:
flowchart TD
    Start --> Compute_subjects[len(data) computed]
    Compute_subjects --> |0 subjects| Return_empty
    Compute_subjects --> |>0 subjects| Init_voxels_array
    Init_voxels_array --> For_each_subject
    For_each_subject --> Get_voxels[voxels[i] = data[i].shape[0]]
    Get_voxels --> Build_random_matrix[random matrix shape (voxels[i], features)]
    Build_random_matrix --> QR[q, r = numpy.linalg.qr(random_matrix)]
    QR --> Append_Q[w.append(q)]
    Append_Q --> More_subjects?{more subjects remain}
    More_subjects? --> |yes| For_each_subject
    More_subjects? --> |no| Return[w, voxels]

## Examples:
- Typical non-empty input:
  - Suppose data contains two subjects with shapes (100, 200) and (80, 200) and features == 10.
    - Returned voxels will be an integer array [100, 80].
    - w[0] will have shape (100, 10); w[1] will have shape (80, 10).
    - Columns of w[0] and w[1] are orthonormal and suitable for use as initial per-subject transforms.

- Empty input:
  - If data is an empty sequence, the result is w == [] and voxels == numpy.ndarray(shape=(0,), dtype=int).

Implementation hints:
- Use NumPy to reimplement: random matrix via numpy.random.random((voxels_i, features)), QR via numpy.linalg.qr(...).
- Allocate voxels as a NumPy integer array of length len(data) before the loop for efficiency and to match the original return type.

## `hypertools._externals.srm.SRM` · *class*

## Summary:
SRM is a scikit-learn-compatible estimator that fits a probabilistic Shared Response Model (SRM). It estimates a low-dimensional shared response (timecourses) and per-subject orthonormal transforms that project subject-specific voxel/time data into a common feature space.

## Description:
Instantiate SRM to align multi-subject time-series data where each subject's data is a 2-D array (voxels × timepoints). Typical workflow:
- Create SRM(n_iter=..., features=..., rand_seed=...).
- Call fit(X) with X being a sequence (list/tuple) of per-subject 2‑D numeric arrays (voxels × samples).
- Use transform(X_new) to project per-subject data into the learned shared feature space.

Responsibilities and boundaries:
- Validates inputs (subject count, consistent sample counts, finite values) in fit.
- Delegates the iterative numerical algorithm to the private _srm method.
- Does not perform any I/O or persistence; it only computes and returns in-memory arrays.
- fit stores learned parameters on the instance; internal helpers (_srm, _init_structures, _init_w_transforms, _likelihood) do not mutate the SRM instance — they return computed results which fit assigns to instance attributes.

Known callers:
- User code or scikit-learn pipelines that call srm.fit(X) and srm.transform(X).

## State:
Constructor parameters (stored on the instance):
- n_iter (int)
    - Default: 10
    - Purpose: number of EM-style iterations executed inside _srm.
    - Constraint: integer >= 0.
- features (int)
    - Default: 50
    - Purpose: dimensionality of the shared latent space.
    - Constraint: integer >= 1 in practical use; meaningful values should be <= per-subject voxel counts.
- rand_seed (int)
    - Default: 0
    - Purpose: seed for NumPy random initialization used inside _srm (note: seeding modifies global NumPy RNG state).

Attributes created by fit (post-fit):
- sigma_s_ (numpy.ndarray)
    - Shape: (features, features)
    - Meaning: estimated group-level covariance of the shared response. Returned by _srm and assigned by fit.
    - Invariant: symmetric within numerical precision.
- w_ (list[numpy.ndarray])
    - Length: number of fitted subjects
    - Each w_[i] shape: (voxels_i, effective_features) with effective_features == min(voxels_i, features)
    - Meaning: per-subject orthonormal transforms (columns approximately orthonormal).
- mu_ (list[numpy.ndarray])
    - Per-subject mean vectors (length voxels_i) returned by _init_structures.
- rho2_ (numpy.ndarray)
    - Shape: (n_subjects,)
    - Meaning: per-subject noise variance estimates (positive in normal operation).
- s_ (numpy.ndarray)
    - Shape: (features, samples)
    - Meaning: estimated shared response timecourses.

Class invariants after successful fit:
- self.sigma_s_, self.w_, self.mu_, self.rho2_, and self.s_ exist.
- len(self.w_) == len(self.mu_) == len(self.rho2_) == number of subjects used during fit.
- s_.shape[0] == features (the configured latent dimensionality).

## Lifecycle:
Creation:
- Call SRM(...) with desired hyperparameters. __init__ stores parameters but performs no validation beyond assignment.

Fitting:
- Call fit(X, y=None):
    - Validations performed in fit:
        - len(X) must be >= 2 (ValueError otherwise).
        - All X[i] must be 2-D arrays with the same number of timepoints (axis=1). Mismatch raises ValueError.
        - X[0].shape[1] (n_samples) must be >= features (ValueError otherwise).
        - Each X[i] is checked for finiteness using sklearn.utils.assert_all_finite (raises ValueError on NaN/Inf).
    - After validation, fit calls self._srm(X). Important behavioral contract:
        - _srm reads data and returns a tuple (sigma_s, w, mu, rho2, shared_response).
        - _srm and its helpers do NOT modify the SRM instance (they return computed results).
        - fit assigns the returned tuple to self.sigma_s_, self.w_, self.mu_, self.rho2_, self.s_ respectively, and returns self.
    - Side effect: _srm seeds NumPy RNG with rand_seed; this modifies the global NumPy RNG state.

Transforming:
- Call transform(X, y=None):
    - Preconditions:
        - fit must have been called (self.w_ must exist) else NotFittedError is raised.
        - len(X) must equal len(self.w_) else ValueError.
        - For each subject i, matrix multiplication self.w_[i].T.dot(X[i]) must be valid (rows of X[i] must match rows of w_[i]).
    - Returns a list s where s[i] = self.w_[i].T.dot(X[i]) for each subject.

Destruction / cleanup:
- No explicit cleanup or context management required.
- Be aware that fit modifies global RNG state; callers who depend on RNG sequence should save/restore RNG state if needed.

## Method Map:
flowchart LR
    __init__ --> fit
    fit --> _srm
    _srm --> _init_w_transforms
    _srm --> _init_structures
    _srm --> _likelihood:::optional
    fit --> assign_results[sigma_s_, w_, mu_, rho2_, s_]
    transform --> requires w_ --> compute_projections[w_[i].T @ X[i]]
    classDef optional fill:#f9f,stroke:#333,stroke-width:1px;

Notes:
- _likelihood is a pure calculator that returns a scalar objective (used only for logging when INFO level is enabled) and does not modify any instance state.

## Raises:
Exceptions surfaced by public methods (conditions and origins):

fit(X):
- ValueError:
    - If len(X) <= 1: "There are not enough subjects ({0:d}) to train the model."
    - If X[0].shape[1] < self.features: "There are not enough samples to train the model with {features:d} features."
    - If any subject's number of samples differs from the first subject: "Different number of samples between subjects."
    - If any X[subject] contains NaN or Inf: sklearn.utils.assert_all_finite raises ValueError.
- IndexError or TypeError:
    - If X is not a properly indexable sequence or elements lack the expected shape attributes.
- Exceptions propagated from _srm:
    - scipy.linalg.LinAlgError (from cho_factor/cho_solve or other SciPy routines) if matrices are not factorable.
    - ZeroDivisionError (if voxels count is zero and code divides by samples*voxels).
    - Other NumPy/SciPy exceptions depending on invalid shapes or numerical failure.
Note: _srm itself does not mutate the SRM instance; it returns computed structures and these exceptions reflect failures during computation.

transform(X):
- NotFittedError:
    - If self.w_ is not present (model not fit).
- ValueError:
    - If len(X) != len(self.w_).
- ValueError/TypeError:
    - If per-subject matrix multiplication shapes are incompatible.

## Example:
- Training and projecting (illustrative):
    from hypertools._externals.srm import SRM
    import numpy as np

    X = [np.random.randn(100, 200),
         np.random.randn(120, 200),
         np.random.randn(95, 200)]

    srm = SRM(n_iter=10, features=20, rand_seed=0)
    srm.fit(X)  # validates inputs, calls _srm, assigns returned results to self

    # Learned attributes:
    # srm.w_  -> list of projection matrices
    # srm.s_  -> shared response array shape (features, samples)

    # Project data (same shapes/order)
    projections = srm.transform(X)
    # projections[i].shape == (features, samples)

Implementation hints for reimplementation:
- The internal _srm algorithm (called by fit) returns (sigma_s, w, mu, rho2, shared_response) and does not set attributes on the SRM instance itself; fit performs the assignment.
- _srm relies on:
    - _init_w_transforms(data, features): initializes per-subject orthonormal w via random matrices and QR.
    - _init_structures(data, subjects): returns demeaned data x, per-subject means mu, initial rho2 (ones), and trace_xtx.
    - scipy.linalg.cho_factor and cho_solve for Cholesky factorization and inverses.
    - numpy.linalg.svd for per-subject orthogonal updates, with a small diagonal perturbation (0.001) added to stabilize SVD on near-degenerate matrices.
    - _likelihood to compute a scalar objective (pure function; used only for logging).
- Numeric precautions:
    - Ensure Cholesky inputs are positive-definite or handle LinAlgError.
    - Be aware that seeding the global NumPy RNG changes global state; consider using a local RandomState/Generator if you wish to avoid global side effects.

### `hypertools._externals.srm.SRM.__init__` · *method*

## Summary:
Stores the constructor hyperparameters on the SRM instance (n_iter, features, rand_seed) and performs no validation or heavy initialization.

## Description:
Known callers and context:
- User code or scikit-learn pipelines that instantiate the SRM before calling fit or using it in a pipeline. Typical lifecycle stage: object creation / configuration prior to fitting the model to data.
- Tests and higher-level orchestration code that build an SRM instance with specific hyperparameters for subsequent fit/transform calls.

Why this is a separate method:
- The constructor's responsibility is lightweight configuration: capturing user-supplied hyperparameters as instance attributes. Keeping initialization simple and free of computation or validation allows fast object creation and defers expensive validation and numerical work to fit, which is the appropriate lifecycle step for checking data-dependent constraints and performing model training.

## Args:
    n_iter (int, optional): Number of EM-style iterations the SRM algorithm will perform during fit. Default: 10.
        - Typical expected values: integer >= 0. (Note: __init__ does not validate this; fit will use it as provided.)
    features (int, optional): Dimensionality of the shared latent space (number of features/timecourses). Default: 50.
        - Practical constraint: integer >= 1 and typically <= per-subject voxel counts for meaningful operation. Not enforced here.
    rand_seed (int, optional): Integer seed used by the SRM algorithm for random initialization inside fit/_srm. Default: 0.
        - Note: seeding occurs in the SRM algorithm (e.g., _srm); __init__ merely stores the seed value.

## Returns:
    None

## Raises:
    None (the constructor only assigns attributes and does not raise exceptions). Any type/shape validations or numerical errors occur later during fit or other methods.

## State Changes:
Attributes READ:
    - None (constructor does not read existing instance attributes).

Attributes WRITTEN:
    - self.n_iter (int) set to the provided n_iter argument.
    - self.features (int) set to the provided features argument.
    - self.rand_seed (int) set to the provided rand_seed argument.

## Constraints:
Preconditions:
    - There are no enforced preconditions inside __init__; any semantics or ranges are recommendations for correct downstream behavior:
        * n_iter should be an integer >= 0.
        * features should be an integer >= 1 and practically not larger than per-subject voxel counts.
        * rand_seed should be an integer (used later to seed NumPy RNG).

Postconditions:
    - After calling __init__, the SRM instance has attributes n_iter, features, and rand_seed exactly as provided.
    - No other instance attributes required for fit (such as learned parameters) are created by __init__.

## Side Effects:
    - No I/O, no global state changes, and no numerical computation. The method only mutates the instance by assigning the three attributes listed above.
    - Note: although rand_seed is stored here, seeding of NumPy's RNG (and thus modification of global RNG state) occurs inside fit/_srm when the seed is used — not in __init__ itself.

### `hypertools._externals.srm.SRM.fit` · *method*

## Summary:
Performs probabilistic Shared Response Model training on multi-subject time-series data and stores the learned parameters on the estimator instance.

## Description:
This method expects a list/sequence of subject data arrays and runs the SRM training procedure (delegating the heavy-lifting to the internal _srm method). It is typically called by user code or scikit-learn pipelines as the training step (e.g., estimator.fit(X) or prior to calling transform/fit_transform). The transform() implementation in this class relies on the parameters produced by this method (notably self.w_), so fit must be called before transform.

This logic is a standalone method because it:
- Validates input consistency (subjects, sample counts, and finiteness),
- Enforces preconditions about minimum samples vs. features,
- Delegates the iterative probabilistic SRM algorithm to a dedicated helper (_srm), and
- Stores multiple learned attributes on the instance for later use (transform, inspection).

Known callers / contexts:
- Direct user invocation when training an SRM estimator: srm.fit(X)
- Any scikit-learn style training pipeline that invokes estimator.fit(X, y)
- Must be executed before calling SRM.transform(X)

## Args:
    X (Sequence[numpy.ndarray]):
        Required. A sequence (typically a list) of length S (number of subjects) where
        each element is a 2-D numpy.ndarray of shape (n_voxels, n_samples).
        - n_voxels: number of measurements (e.g., voxels) for that subject.
        - n_samples: number of time points / TRs; all subjects must have the same n_samples.
        Each array must contain finite numeric values (no NaN or +-Inf).
    y (Any, optional):
        Ignored. Present for API compatibility with scikit-learn. Default: None.

## Returns:
    self (SRM):
        The estimator instance with learned parameters attached as attributes. The method always
        returns the same instance (self) on success.

## Raises:
    ValueError:
        - If len(X) <= 1:
            "There are not enough subjects ({0:d}) to train the model."
            Trigger: fewer than two subject data arrays provided.
        - If X[0].shape[1] < self.features:
            "There are not enough samples to train the model with {self.features:d} features."
            Trigger: number of samples (time points) is less than the configured number of features.
        - If any subject's n_samples differs from the first subject:
            "Different number of samples between subjects."
            Trigger: inconsistent second-dimension size across arrays in X.
        - If any array in X contains non-finite values:
            assert_all_finite(X[subject]) will raise ValueError (e.g., for NaN or Inf).
    Any exception raised by the internal _srm method:
        _srm executes the iterative probabilistic SRM algorithm and may raise exceptions
        (e.g., from numpy / scipy linear algebra calls) which will propagate out of fit.

## State Changes:
    Attributes READ:
        - self.features (int): used to check minimum required samples.
        - Indirectly (via self._srm): self.n_iter and self.rand_seed are read by _srm.
    Attributes WRITTEN:
        - self.sigma_s_ : numpy.ndarray
        - self.w_       : list[numpy.ndarray]
        - self.mu_      : list[numpy.ndarray]
        - self.rho2_    : numpy.ndarray
        - self.s_       : numpy.ndarray
        These attributes are set from the tuple returned by self._srm(X).

## Constraints:
    Preconditions (caller must ensure):
        - X is a non-empty sequence of length >= 2.
        - Each element X[i] is a 2-D numpy.ndarray with shape (n_voxels_i, n_samples).
        - All subjects must share the same n_samples along axis 1.
        - n_samples (X[0].shape[1]) must be >= self.features.
        - All values in every X[i] must be finite (no NaN / +-Inf).
    Postconditions (guaranteed on successful return):
        - self.sigma_s_, self.w_, self.mu_, self.rho2_, self.s_ are assigned.
        - self.w_ will be a list whose length equals the number of subjects in X;
          transform() will use self.w_ to compute subject-specific shared responses.
        - The instance is returned (standard scikit-learn fit semantics).

## Side Effects:
    - Logging: emits informational log messages via the module logger (logger.info) about the start
      of SRM and iterations (the internal _srm logs iteration-level messages).
    - Global RNG state: the internal _srm method calls numpy.random.seed(self.rand_seed),
      which alters the global numpy RNG state. Callers that rely on numpy's RNG state should
      be aware this will be modified.
    - No external I/O (files, network) is performed by fit itself, but called numerical
      routines (numpy, scipy) may raise low-level exceptions on failure.

### `hypertools._externals.srm.SRM.transform` · *method*

## Summary:
Projects each subject's data into the model's learned subject-specific feature space using the fitted subject weight matrices, returning a list of projected arrays without modifying the model.

## Description:
This method is intended to be called after the model has been fitted (i.e., after fit has produced self.w_). Typical usage is in a transform step of a processing pipeline where one wants the per-subject projections of new or held-out data given the fitted subject projection matrices. It is separated into its own method to:
- follow the scikit-learn Transformer interface (allowing calls like transform or fit_transform),
- reuse the fitted per-subject weights without re-running fitting logic,
- keep projection logic distinct from fitting/estimation logic for clarity and testability.

Known callers / call contexts:
- External code or pipelines that have previously called fit on the SRM instance and now need the per-subject projected data (for example, a downstream analysis step or a prediction pipeline).
- fit_transform or other convenience wrappers in higher-level utilities (if present) that call transform after fitting.

This method intentionally ignores the optional y argument and only uses X and the fitted attributes to compute projections.

## Args:
    X (sequence[list|tuple|numpy.ndarray]): A sequence (list/tuple) of per-subject 2D array-like objects. Each element X[i] must be a 2-dimensional numeric array representing that subject's data (e.g., voxels x timepoints). The sequence length must match the number of fitted subject weight matrices (len(self.w_)).
    y (ignored): Present for API compatibility with scikit-learn; not used by this method.

## Returns:
    list[numpy.ndarray]: A list s of length len(X). For each subject i, s[i] is the result of self.w_[i].T.dot(X[i]). In linear-algebra terms, the method returns the projection of each subject's data into the fitted feature space (shape depends on the dimensions of self.w_[i] and X[i]). No elements are None in the normal (successful) return.

Edge-case returns:
- This method never returns None for subjects when successful.
- It never returns an empty list unless X is an empty sequence (in which case it returns an empty list).

## Raises:
    NotFittedError: Raised when the instance lacks the fitted attribute self.w_. Trigger condition: hasattr(self, 'w_') is False.
    ValueError: Raised when len(X) != len(self.w_). Trigger condition: the number of provided subjects in X does not match the number of fitted subject weight matrices.

## State Changes:
    Attributes READ:
        self.w_ (required): The list/sequence of fitted per-subject weight matrices. Each element is used to compute the projection via matrix multiplication.
    Attributes WRITTEN:
        None — this method does not modify attributes on self.

## Constraints:
    Preconditions:
        - The SRM instance must have been fitted and therefore must have attribute self.w_.
        - len(X) must equal len(self.w_).
        - For every subject index i, the matrix multiplication self.w_[i].T.dot(X[i]) must be valid. Concretely, if self.w_[i] has shape (m, k), then self.w_[i].T has shape (k, m) and X[i] must have shape (m, t) for some t (timepoints); the dot product will produce shape (k, t).
        - Each X[i] should be finite numeric data (arrays with numeric dtype). The method does not itself call assert_all_finite, so callers should ensure numerical validity if required.

    Postconditions:
        - Returns a list s where each s[i] is the projected array computed by self.w_[i].T.dot(X[i]).
        - The SRM instance's fitted attributes (including self.w_) remain unchanged.
        - The input X is not modified by this method (no in-place operations on X elements are performed).

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - No objects outside self are mutated by this method (it creates and returns new arrays derived from self.w_ and X).

### `hypertools._externals.srm.SRM._init_structures` · *method*

## Summary:
Initializes and returns per-subject working structures: demeaned data arrays, per-subject means, an array of rho^2 initialized to ones, and per-subject trace-of-X^T X (sum of squared entries). This prepares the data that downstream SRM steps consume without mutating the SRM instance.

## Description:
This helper computes and packages per-subject statistics needed for SRM initialization and iterative updates:
- For each subject index i in [0, subjects-1] it computes the mean vector across time, the demeaned data matrix, the sum of squared entries (trace of X^T X), and sets rho2[i] = 1.
- Typical usage: invoked during the SRM initialization/fit stage to produce per-subject inputs for alignment and model-fitting routines. It is separated into its own method to keep initialization logic modular and testable (isolates array-shaping and basic statistical setup from higher-level algorithm code).

Known callers and lifecycle stage:
- Intended to be called at the start of SRM model fitting / initialization to produce the per-subject data structures that the fitter will iterate on. (No explicit caller list is present in the provided snippet; the method itself only prepares and returns structures.)

Why this is a separate method:
- Concentrates reproducible, array-level preprocessing in one place (mean-centering, initial rho2, and trace calculation), simplifying testing and making higher-level SRM code easier to read and maintain.

## Args:
    data (Sequence[numpy.ndarray]):
        Sequence (list-like or array-like) indexed by subject. Each element must be a 2-D numeric array of shape (n_features, n_timepoints) — i.e., rows are features (voxels/channels) and columns are time points / samples.
        Requirement: len(data) must be >= subjects and every data[subject] must support indexing and numeric operations.
    subjects (int):
        Number of subjects to initialize. The method iterates subject indices 0 .. subjects-1 and accesses data[subject] for each. Must be a non-negative integer.

## Returns:
    tuple:
        x (list[numpy.ndarray]):
            List of demeaned data arrays, one per subject. Each element equals data[i] - mu[i][:, np.newaxis] and therefore has the same shape as the corresponding data[i].
        mu (list[numpy.ndarray]):
            List of 1-D mean vectors (length = n_features) computed with numpy.mean(data[i], axis=1) for each subject i.
        rho2 (numpy.ndarray):
            1-D array of length `subjects` with dtype numeric, initialized to 1 for every subject. Shape: (subjects,).
        trace_xtx (numpy.ndarray):
            1-D array of length `subjects` where element i equals the sum of squares of all entries in data[i] (computed via numpy.sum(data[i] ** 2)). Shape: (subjects,).

    Edge cases:
        - If a subject's data has zero timepoints but correct 2-D shape (n_features, 0), mu will be a vector of nan (numpy.mean over empty slice) and trace_xtx will be 0.
        - If n_features is zero (shape (0, n_timepoints)), mu will be an empty array and demeaned arrays will have zero rows.

## Raises:
    IndexError:
        If subjects is greater than the number of elements in `data` (i.e., data[subject] access fails).
    numpy.AxisError or ValueError:
        If data[subject] is not at least 2-D (so axis=1 is invalid) or otherwise incompatible with numpy.mean(data[subject], 1).
    TypeError:
        If data elements are not numeric arrays and do not support the arithmetic operations used (mean, exponentiation, subtraction).
    Note:
        These exceptions are not explicitly raised by the method but are the direct runtime exceptions that will surface from the numpy operations used.

## State Changes:
    Attributes READ:
        - None (the method does not access any self.<attr> fields in the provided implementation)
    Attributes WRITTEN:
        - None (the method does not modify self; it returns new structures)

## Constraints:
    Preconditions:
        - `subjects` is an integer >= 0.
        - `data` is indexable for indices 0 .. subjects-1 (len(data) >= subjects).
        - For each i in 0..subjects-1, data[i] is a 2-D numeric array-like object with shape (n_features, n_timepoints).
    Postconditions:
        - Returns four objects (x, mu, rho2, trace_xtx) as described in Returns.
        - For every subject i in 0..subjects-1:
            * mu[i] equals the per-feature mean vector computed along axis=1 of data[i].
            * x[i] equals data[i] with mu[i] subtracted from each column (demeaned along rows).
            * rho2[i] equals 1.
            * trace_xtx[i] equals the sum of squares of all entries of data[i].

## Side Effects:
    - No I/O, no network calls, and no mutation of input arrays (operations create new arrays/objects); the method only allocates and returns new Python lists and numpy arrays.
    - If input arrays are views with unusual behavior, the numpy arithmetic will produce new arrays for x entries (standard broadcasting/subtraction result), but the original data elements are not overwritten.

### `hypertools._externals.srm.SRM._likelihood` · *method*

## Summary:
Compute the scalar (log-)likelihood-like objective used by the SRM EM loop: combines determinants of covariance factors, a data-fit trace term, and a quadratic form term to produce a single numeric objective used for logging and comparison across iterations. This method does not mutate object state.

## Description:
Known callers and lifecycle stage:
- Called from SRM._srm inside the EM-like iteration loop (once per iteration when INFO logging is enabled) to compute the current objective value for logging:
    logger.info('Objective function %f' % loglike)
- The method is invoked after intermediate matrices (Cholesky factors, inverses, and weighted sums) have been computed for the current iteration and is used only to produce a scalar summary of the current model fit.

Why this logic is its own method:
- The objective calculation is compact but conceptually separate from the update logic: extracting it into a dedicated method keeps _srm focused on algorithmic updates and reduces duplication if the objective needs to be inspected or reused elsewhere. Encapsulation improves readability and unit-testability.

## Args:
    chol_sigma_s_rhos (numpy.ndarray):
        Triangular Cholesky factor of the matrix sigma_s_rhos as returned by scipy.linalg.cho_factor.
        Expected shape: (F, F) where F == number of latent features.
        Requirements: diagonal elements should be finite; non-zero diagonals are required to obtain a finite log-determinant.
    log_det_psi (float):
        Scalar term representing the log-determinant contribution from subject-specific noise factors (precomputed, e.g., sum(log(rho2) * voxels)).
    chol_sigma_s (numpy.ndarray):
        Triangular Cholesky factor of the shared covariance sigma_s (as returned by scipy.linalg.cho_factor).
        Expected shape: (F, F). Diagonal elements should be finite and non-zero for a finite log-determinant.
    trace_xt_invsigma2_x (float):
        Precomputed scalar trace term summarizing data fit weighted by inverse subject variances (sum over subjects of trace(X^T inv(Sigma_psi) X) or equivalent).
    inv_sigma_s_rhos (numpy.ndarray):
        Inverse of sigma_s_rhos (dense matrix).
        Expected shape: (F, F). Must be compatible for matrix-multiplication with wt_invpsi_x (i.e., feature-dimension F).
    wt_invpsi_x (numpy.ndarray):
        Weighted sum of per-subject projected data; shape (F, T) where T == samples (number of timepoints / observations).
        The method computes wt_invpsi_x.T @ inv_sigma_s_rhos @ wt_invpsi_x, so wt_invpsi_x.shape[0] must equal inv_sigma_s_rhos.shape[0].
    samples (int):
        Number of timepoints / columns used in the current iteration (T). Must be a non-negative integer matching wt_invpsi_x.shape[1].

## Returns:
    float:
        The computed scalar objective (named loglikehood in the implementation). Interpretation:
            - Larger values indicate a better fit under the model's Gaussian-form objective used here.
            - If inputs violate numeric preconditions (non-finite or non-positive diagonal elements), the returned value may be numpy.nan or +/-inf.
        Typical value: finite real number when inputs are valid.

## Raises:
    - ValueError (or numpy broadcasting error):
        - If array shapes are incompatible for the matrix multiplications performed (e.g., inv_sigma_s_rhos and wt_invpsi_x have mismatched feature dimensions), NumPy will raise a ValueError or shape-related exception.
    - Floating point warnings / invalids (may produce NaN/inf):
        - If any diagonal elements of the provided Cholesky factors are zero or non-finite, np.log on squared diagonals produces -inf or NaN; the function does not explicitly catch these, so the returned scalar may be -inf, +inf, or NaN and NumPy runtime warnings may be emitted.
    Notes:
        - The implementation does not explicitly raise specialized exceptions for invalid numeric content; instead, underlying NumPy operations will raise or return NaN/inf as appropriate.

## State Changes:
Attributes READ:
    - None (this method reads only its arguments; it does not access or depend on any self.<attr> attributes).

Attributes WRITTEN:
    - None (no modification of self or external objects; all inputs are treated as read-only from the method's perspective).

## Constraints:
Preconditions:
    - chol_sigma_s_rhos and chol_sigma_s must be triangular factors for which taking the diagonal and computing log(diag**2) yields finite numbers (i.e., diagonal elements finite and non-zero for a finite log-determinant).
    - inv_sigma_s_rhos must be square of shape (F, F) and numerically represent the inverse of the matrix corresponding to chol_sigma_s_rhos (or be compatible for multiplication).
    - wt_invpsi_x.shape == (F, samples) and samples must equal wt_invpsi_x.shape[1].
    - trace_xt_invsigma2_x and log_det_psi must be finite scalars when a finite result is required.

Postconditions:
    - The method returns a single float (possibly NaN/inf if preconditions are violated).
    - No object state is modified.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of input arrays is performed by this method.
    - May emit NumPy runtime warnings (divide-by-zero, invalid value) if inputs are numerically invalid.

## Implementation notes (for reimplementation):
    - Compute the log-determinant contribution by summing log(diag(chol)**2) for each Cholesky factor and adding log_det_psi.
    - The objective is assembled as:
        loglike = -0.5 * samples * log_det - 0.5 * trace_xt_invsigma2_x
                  + 0.5 * trace(wt_invpsi_x.T @ inv_sigma_s_rhos @ wt_invpsi_x)
    - Use numpy.trace and numpy.dot (or the @ operator) for the quadratic-form trace; ensure shapes are compatible to avoid broadcasting errors.
    - Be robust to numerical issues upstream (ensure Cholesky factors correspond to positive-definite matrices) to avoid NaN/inf results here.

### `hypertools._externals.srm.SRM._srm` · *method*

## Summary:
Performs the core EM-style optimization that estimates the shared response, subject-specific orthogonal transforms, noise variances, and the group-level covariance for the SRM model; returns those estimated objects without mutating the SRM instance.

## Description:
This private method runs the iterative expectation-maximization style updates that form the SRM training loop:
- Typical callers and context:
    - Called internally by the SRM training pipeline (for example SRM.fit or other fit/fit_transform helpers) during model fitting. It is invoked in the optimization stage where the model alternates between estimating the latent shared response and updating per-subject transforms/noise parameters.
- Why this logic is a separate method:
    - The procedure contains many iterative linear-algebraic steps, Cholesky-based solves, and per-subject updates; separating it as a private method keeps fit/entry-point code concise, isolates numerical details for testing, and allows reuse (e.g., for different fit entry points or diagnostic calls).

## Args:
    data (Sequence[numpy.ndarray]):
        - A sequence (typically a list or tuple) of length S where S is the number of subjects.
        - Each element data[s] must be a 2-D numeric array of shape (voxels_s, samples), where:
            * voxels_s is the number of measured features (voxels, channels) for subject s
            * samples is the number of timepoints (must be the same across all subjects)
        - dtype: float-like (NumPy arrays). The method reads data directly and does not copy it before use.
        - Precondition: len(data) >= 1 and data[0].shape[1] is defined (samples dimension).

## Returns:
    tuple containing (sigma_s, w, mu, rho2, shared_response)
    - sigma_s (numpy.ndarray):
        * Shape: (features, features)
        * Symmetric positive-semidefinite group-level covariance estimate for the shared response.
    - w (list[numpy.ndarray]):
        * Length: number of subjects (S).
        * Each element w[s] has shape (voxels_s, features) and is an (approximately) orthogonal transform mapping subject voxels to the shared feature space.
    - mu (object, as produced by _init_structures):
        * The per-subject means/structure returned by the SRM._init_structures helper. The method does not modify mu but returns it for caller use.
    - rho2 (numpy.ndarray or list of floats):
        * Length S: per-subject noise variance estimates (one scalar per subject).
    - shared_response (numpy.ndarray):
        * Shape: (features, samples)
        * The estimated latent response shared across subjects (timecourses in feature space).

    Notes:
    - The returned objects are the final estimates after self.n_iter iterations.
    - The order of the tuple is exactly (sigma_s, w, mu, rho2, shared_response).

## Raises:
    - IndexError:
        * If data is empty, accessing data[0] will raise IndexError.
    - ZeroDivisionError:
        * If any subject has zero voxels (voxels_s == 0), the code divides by (samples * voxels_s) when updating rho2 and will raise ZeroDivisionError.
    - scipy.linalg.LinAlgError (or underlying LAPACK/BLAS errors):
        * The method calls scipy.linalg.cho_factor / cho_solve; these may raise LinAlgError if a matrix is not factorable as expected (e.g., not positive-definite).
    - Any exception raised by the internal helpers:
        * _init_w_transforms(data, self.features) or self._init_structures(data, subjects) may raise their own exceptions (ValueError, TypeError, etc.) if inputs are malformed; these propagate up.

## State Changes:
    - Attributes READ:
        * self.rand_seed
        * self.features
        * self.n_iter
        * self._init_structures (method)
        * self._likelihood (method) — called only when INFO logging enabled
    - Attributes WRITTEN:
        * None — the method does not assign to self.*; it returns computed objects instead.

## Constraints:
    - Preconditions:
        * data must be a non-empty sequence of 2-D arrays with consistent samples dimension (data[s].shape[1] equal for all s).
        * Each voxels_s (rows per subject array) must be a positive integer.
        * self.features must be a positive integer less than or equal to each voxels_s (practically, features <= voxels_s to produce meaningful orthogonal transforms).
        * self.rand_seed should be an integer (or valid numpy seed) if reproducible behavior is desired.
        * self.n_iter must be a non-negative integer; if zero, the method will still run but perform no iterations of the loop and return initial estimates as produced by _init_w_transforms/_init_structures.
    - Postconditions:
        * The method returns:
            - sigma_s: final group covariance estimate (features x features)
            - w: list of per-subject transform matrices (voxels_s x features)
            - mu: the mu structure returned by _init_structures (unchanged)
            - rho2: updated per-subject noise variances
            - shared_response: the final shared-response estimate (features x samples)
        * The global numpy RNG state is modified by seeding with self.rand_seed (see Side Effects).

## Side Effects:
    - Modifies global NumPy RNG state by calling numpy.random.seed(self.rand_seed) at the start. This deterministic seeding affects subsequent numpy.random calls across the process unless the caller saves/restores RNG state.
    - Performs no file I/O or network calls.
    - Does not mutate input arrays in data (the code reads from data, and helper functions are expected to copy/return new arrays).
    - May log progress and objective values using the module logger at INFO level (logging calls only).

## Implementation notes and numerical details (for reimplementation):
    - Initialization:
        * The method relies on two helpers:
            - _init_w_transforms(data, features) returns an initial list of w matrices (one per subject) and a list of voxel counts per subject.
            - self._init_structures(data, subjects) returns x (per-subject data matrices shaped voxels x samples), mu, rho2 (per-subject scalars), and trace_xtx (per-subject traces used in variance updates).
        * It initializes shared_response to zeros with shape (features, samples) and sigma_s to identity(features).
    - Iterative updates (repeated self.n_iter times):
        * Compute rho0 = sum(1 / rho2)
        * Compute Cholesky factorization and inverse of sigma_s with scipy.linalg.cho_factor and cho_solve.
        * Form sigma_s_rhos = inv_sigma_s + I * rho0 and compute its Cholesky factor and inverse.
        * Accumulate wt_invpsi_x = sum_s (w[s].T @ x[s]) / rho2[s] and trace_xt_invsigma2_x = sum_s trace_xtx[s] / rho2[s]
        * Compute log_det_psi = sum(log(rho2[s]) * voxels_s)
        * Update shared_response = sigma_s @ (I - rho0 * inv_sigma_s_rhos) @ wt_invpsi_x
        * Update sigma_s = inv_sigma_s_rhos + (shared_response @ shared_response.T) / samples
        * Compute trace_sigma_s = samples * trace(sigma_s)
        * For each subject:
            - Compute a_subject = x[s] @ shared_response.T
            - Add a tiny diagonal perturbation (0.001) before SVD to stabilize numerical issues
            - Compute SVD of a_subject + perturbation and set w[s] = u @ v
            - Update rho2[s] with trace_xtx[s] - 2 * sum(w[s] * a_subject) + trace_sigma_s, then normalize by (samples * voxels_s)
        * Optionally compute and log the likelihood via self._likelihood when INFO logging is enabled.
    - Numerical cautions:
        * The method assumes per-subject voxel counts and samples are reasonably large to avoid degenerate covariance matrices; small or rank-deficient inputs can trigger LinAlgError or lead to noisy variance estimates.
        * The small diagonal perturbation before SVD is used to avoid exact-rank degeneracy when computing orthogonal transforms.

## `hypertools._externals.srm.DetSRM` · *class*

*No documentation generated.*

### `hypertools._externals.srm.DetSRM.__init__` · *method*

## Summary:
Store the provided SRM configuration parameters on the new instance; no computation or validation is performed.

## Description:
Executed when a DetSRM object is constructed via direct instantiation (calling DetSRM(...)). The constructor's sole responsibility is to record the three public configuration parameters on the instance so other code can read them later. This keeps default values and parameter assignment centralized in the class initializer.

Known callers / invocation context:
- Called implicitly by Python whenever DetSRM(...) is used to create a new instance.

Why this is its own method:
- As the class constructor, it establishes the object's initial state and centralizes parameter defaults and assignments in a single location instead of repeating them elsewhere.

## Args:
    n_iter (int, optional): Number of iterations the SRM procedure should run. Default: 10.
        - Expected type: integer.
        - No validation is performed here; callers should ensure the value is appropriate for later use (e.g., non-negative).
    features (int, optional): Target number of shared features/components. Default: 50.
        - Expected type: integer.
        - No validation is performed here; callers should ensure the value is appropriate (e.g., positive).
    rand_seed (int, optional): Integer seed for any downstream random initialization. Default: 0.
        - Expected type: integer.
        - No validation is performed here.

## Returns:
    None

## Raises:
    This constructor does not raise any exceptions. It performs direct assignments only; any errors arising from inappropriate types or values will occur later when these attributes are consumed.

## State Changes:
Attributes READ:
    - None (the constructor does not read any existing instance attributes)

Attributes WRITTEN:
    - self.n_iter is set to the provided n_iter value
    - self.features is set to the provided features value
    - self.rand_seed is set to the provided rand_seed value

## Constraints:
Preconditions:
    - There are no enforced preconditions in this method; callers should provide values of the expected types and ranges if required by later operations.

Postconditions:
    - After the call, the instance will have three public attributes (n_iter, features, rand_seed) set to the passed values.
    - No other attributes are modified by this constructor.

## Side Effects:
    - No I/O, logging, or external library calls are made.
    - The only observable effect is mutation of the newly-created instance by adding the three attributes above.

### `hypertools._externals.srm.DetSRM.fit` · *method*

## Summary:
Validates a list of subject data arrays and trains the Deterministic Shared Response Model, updating the estimator with per-subject linear transforms (self.w_) and a shared low-dimensional response (self.s_); returns self for sklearn-style chaining.

## Description:
This is the public training method for DetSRM and is called during the "fit" stage of the estimator lifecycle. Typical callers:
- User code invoking model.fit(X) directly to train the model.
- scikit-learn utilities and wrappers (e.g., Pipeline.fit, cross-validation routines) that call an estimator's fit method.
- Higher-level convenience methods that delegate to DetSRM.fit for model training.

Context and responsibilities:
- Performs input validation (number of subjects, matching timepoints, finiteness) and shape checks that are required before running the SRM algorithm.
- Delegates the iterative SRM algorithm and RNG seeding to the internal helper self._srm(X).
- Centralizing validation here ensures scikit-learn API compatibility and keeps algorithmic details encapsulated in _srm.

Important observable behavior:
- Immediately logs "Starting Deterministic SRM" at INFO level when invoked.
- Raises clear ValueError exceptions for invalid inputs (subject count, inconsistent timepoints, insufficient timepoints/features) and propagates exceptions from assert_all_finite on non-finite data.
- After validation, sets self.w_ and self.s_ by assigning the tuple returned from self._srm(X).

## Args:
    X (sequence[array-like], required):
        A sequence (e.g., list or tuple) of length M >= 2 where each element is a 2-D numeric array-like object.
        Expected element shape: (n_voxels_m, n_timepoints). All elements must have the same n_timepoints (same number of columns).
        Requirements:
            - Accessing X[i].shape[1] must be valid.
            - Arrays must contain finite numeric values (no NaN or Inf).
            - Arrays must support matrix multiplication (dot) with numpy arrays (used in _srm).
    y (ignored):
        Present for scikit-learn API compatibility; not used and may be None.

## Returns:
    self (DetSRM):
        On success, returns the estimator instance with the following attributes set:
            - self.w_: list of length M where each element is a numpy.ndarray transform for the corresponding subject.
                * For subject m, w_[m].shape == (n_voxels_m, self.features).
                * Each w_[m] is computed from an SVD-based update in _srm (u.dot(v)). When self.features <= n_voxels_m, the columns of w_[m] form an orthonormal set (i.e., column vectors are orthonormal).
            - self.s_: numpy.ndarray with shape (self.features, n_timepoints), representing the learned shared response across subjects.
        Edge cases:
            - If validation fails, the method raises and does not guarantee that w_ or s_ are set.
            - The method always returns self on successful completion to support method chaining.

## Raises:
    ValueError:
        - If len(X) <= 1:
            "There are not enough subjects ({0:d}) to train the model."
        - If X[0].shape[1] < self.features:
            "There are not enough samples to train the model with {0:d} features."
        - If any subject's number of columns differs from the first subject:
            "Different number of samples between subjects."
        - If any input array contains non-finite values (NaN or Inf):
            Raised by sklearn.utils.assert_all_finite and propagated (typically a ValueError).
    Notes:
        - This method itself does not raise NotFittedError; transform will raise NotFittedError if called before fit.

## State Changes:
    Attributes READ:
        - self.features: used to verify that the number of timepoints >= features.
    Attributes WRITTEN:
        - self.w_: populated with per-subject transform matrices returned from self._srm.
        - self.s_: populated with the shared response matrix returned from self._srm.

## Constraints:
    Preconditions:
        - X is a sequence-like container with length >= 2.
        - Each X[i] is 2-D and has the same number of columns.
        - The number of timepoints (columns) is >= self.features.
        - All array entries are finite.
    Postconditions:
        - After successful return:
            * len(self.w_) == len(X)
            * For each subject m, self.w_[m].shape == (n_voxels_m, self.features)
            * self.s_.shape == (self.features, n_timepoints)
            * The estimator is ready for transform; transform will compute per-subject projections using self.w_.

## Side Effects:
    - Logs progress and messages at INFO level (starts with "Starting Deterministic SRM" and additional objective/iteration logs emitted by _srm).
    - Delegates to self._srm(X), which:
        * Seeds numpy's global RNG via numpy.random.seed(self.rand_seed), mutating the process-wide random state.
        * Uses self.n_iter to control the number of SRM iterations.
        * Allocates temporary arrays and performs linear algebra (SVD) computations.
    - No file I/O or network calls are performed by this method.

## Usage (prose example):
    Construct a DetSRM, then call fit with a list of per-subject 2-D arrays (voxels x timepoints). After fit, use transform to obtain the projected shared responses. Because fit sets self.w_ and self.s_, calling transform before fit will raise NotFittedError.

### `hypertools._externals.srm.DetSRM.transform` · *method*

## Summary:
Project each subject's data into the learned subject-specific feature space using the fitted transform matrices and return per-subject projected timecourses; the method reads the fitted transforms (self.w_) but does not modify the estimator.

## Description:
Known callers and lifecycle:
- Called after DetSRM.fit (or fit_transform) in the typical "fit then transform" workflow when a developer/user wants to obtain the per-subject projections of data into the learned feature space.
- Typical usage pattern: estimator.fit(X); projections = estimator.transform(X_new).
- The method is separated from fit because it performs only the projection using already-learned transforms (self.w_) and may be reused for new datasets without retraining.

Why this is a separate method:
- Keeps training (fit) and inference/projection (transform) responsibilities distinct: fit estimates subject transforms and the shared response, while transform applies the subject transforms to data. This allows applying the same trained transforms to new data (or held-out data) without recomputing transforms.

What it does:
- For each subject index m, computes projected = self.w_[m].T dot X[m] and returns a list of these projected arrays in the same subject order as X.

## Args:
    X (sequence[numpy.ndarray]):
        Sequence (e.g., list or tuple) of per-subject 2-D numeric arrays. For subject m:
        - X[m] is expected to be a 2-D array with shape (n_voxels_m, n_timepoints_m).
        - The method enforces only that len(X) == len(self.w_); it does not validate finiteness or all array shapes beyond dot-product compatibility.
    y:
        Ignored; present to match the scikit-learn Transformer API.

Expected fitted attribute shapes (from fit/_srm behavior):
    - self.w_ is a sequence where each self.w_[m] is a 2-D array with shape (n_voxels_m, n_features).
    - Therefore, self.w_[m].T has shape (n_features, n_voxels_m) and self.w_[m].T.dot(X[m]) yields shape (n_features, n_timepoints_m).

## Returns:
    list[numpy.ndarray]:
        A list of length len(X). For each subject m the returned element is a 2-D numpy array with shape (n_features, n_timepoints_m), computed as self.w_[m].T.dot(X[m]).

Edge-case returns:
- If inputs are well-shaped and no numerical issues occur, returns the list described above.
- If any subject m has incompatible shapes for matrix multiplication, numpy will raise an exception (e.g., ValueError) which propagates to the caller; this method does not catch such exceptions.

## Raises:
    sklearn.utils.validation.NotFittedError:
        - Raised when the estimator has not been fitted (self.w_ attribute does not exist).
    ValueError:
        - Raised when len(X) != len(self.w_) (number of subjects provided does not match the number the model was fitted with).
    numpy / ValueError or TypeError:
        - If individual X[m] arrays are not 2-D numeric arrays or have incompatible shapes for the dot product, numpy may raise errors (these will propagate).

## State Changes:
    Attributes READ:
        - self.w_ (list/sequence of 2-D numpy arrays; subject-specific transform matrices)
    Attributes WRITTEN:
        - None. The method does not mutate estimator attributes.

## Constraints:
    Preconditions:
        - The estimator must have been fitted so that self.w_ exists.
        - len(X) must equal len(self.w_).
        - For each subject m, X[m] must be a 2-D numeric array and X[m].shape[0] must equal self.w_[m].shape[0] so that self.w_[m].T.dot(X[m]) is valid.
    Postconditions:
        - The estimator remains unchanged.
        - The return value is a list with per-subject projected arrays shaped (self.w_[m].shape[1], X[m].shape[1]) for each subject m.

## Side Effects:
    - No file or network I/O.
    - No external services are called.
    - No mutation of objects outside self is performed; returned numpy arrays are newly created by the dot-product operations.
    - The method does not check for NaN/Inf in X; such values will propagate to the outputs if present.

### `hypertools._externals.srm.DetSRM._objective_function` · *method*

## Summary:
Computes the SRM reconstruction error (half the mean squared Frobenius norm) between each subject's data and its reconstruction w[m] @ s, returning a non-negative scalar objective value suitable for logging or convergence checks.

## Description:
- Known callers and context:
    - DetSRM._srm: called after initial shared-response computation and at the end of each iteration when INFO logging is enabled, to compute and log the current objective value for monitoring optimization progress.
    - Lifecycle stage: invoked during model training (fit/_srm) to assess reconstruction quality of the current transforms w and shared response s.
- Why this logic is a separate method:
    - Encapsulates the objective calculation in one place for reuse (initial evaluation and per-iteration logging).
    - Improves readability and testability by isolating the numeric formula away from the optimization loop.
    - Keeps _srm focused on the optimization steps rather than the scalar computation and normalization detail.

## Args:
    data (Sequence[numpy.ndarray]):
        Sequence (typically list) of per-subject data matrices. Each element data[m] must be a 2-D array-like of shape (D_m, T), where D_m is the number of features (e.g. voxels) for subject m and T is the number of timepoints / samples. Must be non-empty (len(data) >= 1).
    w (Sequence[numpy.ndarray]):
        Sequence of per-subject linear transforms. Each w[m] must be a 2-D array-like of shape (D_m, K) where K is the number of shared features. These transforms are used to reconstruct each subject's data as w[m] @ s.
        The length of w must equal len(data).
    s (numpy.ndarray):
        Shared response matrix, a 2-D array-like of shape (K, T), where K is the number of shared features and T is the number of timepoints. Must be compatible for multiplication with every w[m] (i.e., w[m].shape[1] == s.shape[0]) and have s.shape[1] == data[m].shape[1] for all m.

## Returns:
    float:
        A scalar objective value equal to 0.5 * (sum_m ||data[m] - w[m] @ s||_F^2) / T, where ||·||_F is the Frobenius norm and T is the number of columns (timepoints) in data[0]. This value is non-negative. The concrete return type will typically be a Python float or numpy scalar.

## Raises:
    IndexError:
        If data is empty (len(data) == 0), access to data[0] will raise IndexError.
    ZeroDivisionError:
        If data[0].shape[1] == 0 (zero timepoints), dividing by T causes a ZeroDivisionError.
    ValueError (or numpy.linalg / broadcasting errors):
        If shapes are incompatible for matrix multiplication (w[m].dot(s)) or subtraction (data[m] - w[m].dot(s)), numpy will raise a ValueError or a related linear-algebra/broadcasting error. These are propagated unchanged.
    TypeError:
        If inputs do not provide the array-like interface (no .shape or dot method), Python attribute/TypeError may be raised by attempted operations.

## State Changes:
- Attributes READ:
    - None. This method does not read or depend on any DetSRM instance attributes (it only uses the arguments passed in).
- Attributes WRITTEN:
    - None. The method does not modify self or any attribute on the instance.

## Constraints:
- Preconditions:
    - len(data) >= 1.
    - len(w) == len(data).
    - For every subject m:
        - data[m] is 2-D with shape (D_m, T).
        - w[m] is 2-D with shape (D_m, K).
    - s is 2-D with shape (K, T).
    - T (number of timepoints) must be > 0.
    - All arrays must support numpy-compatible dot and Frobenius-norm operations.
- Postconditions:
    - No mutation of inputs or self occurs.
    - The method returns a non-negative scalar value. If inputs satisfy preconditions, the returned value is finite; otherwise exceptions described above may be raised.

## Side Effects:
- None. The function performs only pure numeric computations using the provided arguments. It does not perform I/O, logging, or mutate objects outside its local scope.

## Notes / Implementation details:
- The computation performed is:
    objective = sum_{m=0}^{M-1} ||data[m] - w[m] @ s||_F^2
    return 0.5 * objective / T
  where M = number of subjects and T = data[0].shape[1].
- Numerical behavior:
    - If any subject's reconstruction error is large, the sum may be large; the result is scaled by 0.5 / T to produce an average-like per-timepoint objective with a 0.5 factor commonly used in least-squares formulations.
    - Shape/incompatibility errors are intentionally not caught inside the method to allow callers to notice incorrect inputs immediately.

### `hypertools._externals.srm.DetSRM._compute_shared_response` · *method*

## Summary:
Compute and return the averaged shared-response matrix by projecting each subject's data into that subject's transform space and averaging across subjects; this is a pure computation and does not modify object state.

## Description:
Known callers:
- DetSRM._srm — used to compute the initial shared response and to update the shared response after each iteration of transform updates during model fitting.

Context / lifecycle:
- Invoked during SRM training to produce the current estimate of the shared response s from a provided list of per-subject data and the current list of per-subject linear transforms w.
- Factored into its own method to centralize the projection+averaging operation, avoid duplicating the same computation at multiple points in the SRM routine, and make the SRM loop clearer and easier to test.

## Args:
    data (Sequence[numpy.ndarray]):
        Sequence (e.g., list or tuple) of 2-D numeric arrays, one entry per subject.
        Each array is expected to have shape (n_voxels, n_timepoints). The method
        will access indices 0 .. len(w)-1 of this sequence.
    w (Sequence[numpy.ndarray]):
        Sequence (e.g., list or tuple) of 2-D numeric arrays, one per subject,
        containing subject-specific linear transforms. Each w[m] is expected to
        have shape (n_voxels, n_features). All w[m] must share the same number
        of columns (n_features). The method uses len(w) as the number of subjects.

## Returns:
    numpy.ndarray:
        A 2-D numeric array with shape (n_features, n_timepoints). It is equal to
        (1 / len(w)) * sum_{m=0..len(w)-1} (w[m].T @ data[m]).
        The returned dtype follows numpy's promotion rules based on the input arrays.
        Note: NaNs or Infs present in the inputs will propagate into the result
        (this method does not validate finiteness).

## Raises:
    IndexError:
        - If w is empty (the implementation reads w[0] to determine output shape), an IndexError is raised when attempting to access w[0].
        - If len(data) < len(w), attempting to access data[m] for m in range(len(w)) will raise IndexError.
    ValueError or TypeError (from numpy operations):
        - If array shapes are incompatible for the matrix multiplications (for example, if w[m].shape[0] != data[m].shape[0]), numpy.dot will raise a ValueError or TypeError; this method does not catch those errors.
    Any exception raised by numpy.dot or array operations may propagate.

## State Changes:
    Attributes READ:
        None — this method does not read or depend on any self.<attr> attributes.
    Attributes WRITTEN:
        None — this method does not modify any self.<attr> attributes.

## Constraints:
    Preconditions:
    - len(w) > 0.
    - len(data) >= len(w). (Typical and recommended usage is len(data) == len(w).)
    - For each m in 0 .. len(w)-1:
        * data[m] is a 2-D array shaped (n_voxels, n_timepoints).
        * w[m] is a 2-D array shaped (n_voxels, n_features).
        * All w[m].shape[1] (n_features) are identical across subjects.
        * All data[m].shape[1] (n_timepoints) are identical across subjects.
        * w[m].shape[0] == data[m].shape[0] so that w[m].T @ data[m] is valid and yields shape (n_features, n_timepoints).
    Postconditions:
    - The returned array s has shape (n_features, n_timepoints).
    - The returned s equals the arithmetic mean across subjects of w[m].T @ data[m] for m in 0..len(w)-1.

## Side Effects:
    - No I/O, no network or external service calls.
    - Does not mutate the provided input sequences or the arrays inside them.
    - Allocates a new numpy array for the accumulator/result.

## Usage note (prose example):
- When called inside the SRM training loop, pass the list of subject data arrays (each shaped voxel-by-time) and the list of current subject transforms (each shaped voxel-by-features). The method returns the shared-response matrix shaped features-by-time that the SRM algorithm uses for subsequent per-subject transform updates.

### `hypertools._externals.srm.DetSRM._srm` · *method*

*No documentation generated.*

