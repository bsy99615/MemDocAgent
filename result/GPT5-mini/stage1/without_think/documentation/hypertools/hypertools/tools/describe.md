# `describe.py`

## `hypertools.tools.describe.describe` · *function*

*No documentation generated.*

## `hypertools.tools.describe.get_corr` · *function*

## Summary:
Returns the Pearson correlation coefficient (scalar) between two numeric arrays by flattening both inputs and delegating computation to scipy.stats.pearsonr.

## Description:
Known callers:
    - No internal callers were detected in the analyzed repository. This function is a small utility intended for use wherever a single-number linear-association measure is needed between two possibly multi-dimensional numeric arrays.

Typical context and pipeline stage:
    - Called after dimensionality reduction, transformation, or aggregation steps when code needs to compare a reduced representation with another set of dimensions and obtain a single Pearson r value.
    - The utility centralizes flattening (via .ravel()) and selects the correlation coefficient while discarding the p-value.

Why this logic is extracted:
    - Ensures a uniform flattening strategy (ndarray.ravel(), row-major/C order by default) across callers and prevents repeated boilerplate.
    - Encapsulates the selection of the correlation coefficient from pearsonr's (r, p) result.

## Args:
    reduced (object with ravel() method, required)
        - An object implementing the ndarray.ravel() interface (commonly a numpy.ndarray).
        - The function calls reduced.ravel() and expects a 1-D numeric sequence in return.
    alldims (object with ravel() method, required)
        - An object implementing .ravel() (commonly a numpy.ndarray).
        - The function calls alldims.ravel() and expects a 1-D numeric sequence in return.
    Interdependencies:
        - After calling .ravel() on both arguments, the flattened arrays must have the same length and length >= 2 for a meaningful Pearson correlation. If this is not true, scipy.stats.pearsonr will raise an exception which this function propagates.

## Returns:
    float
        - The Pearson correlation coefficient (Pearson's r) between the flattened contents of alldims and reduced.
        - This is the first element (index 0) of the tuple returned by scipy.stats.pearsonr(flat_alldims, flat_reduced).
        - For valid finite inputs, the value lies in [-1.0, 1.0]. If inputs are constant (zero variance) or invalid for correlation, scipy may return NaN; that NaN is returned unchanged.

## Raises:
    AttributeError
        - If either argument does not implement ravel(), since this function calls .ravel() directly (for example, passing a plain Python list will cause AttributeError).
    ValueError
        - Propagated from scipy.stats.pearsonr when flattened inputs differ in length, are too short (length < 2), or otherwise violate pearsonr's input requirements.
    Any exception from scipy.stats.pearsonr
        - For example, TypeError if the flattened contents are non-numeric in a way scipy cannot handle; such exceptions propagate unchanged.
    Warnings
        - scipy may emit ConstantInputWarning (or similar) when one or both inputs have zero variance; pearsonr typically returns NaN in that case. This function does not suppress those warnings.

## Constraints:
    Preconditions:
        - Both arguments must implement .ravel() and return numeric sequences when called.
        - Flattened arrays must have equal lengths and contain at least two elements.
        - Preferably, flattened arrays should be finite and not contain NaNs if a meaningful numeric result is required.
    Postconditions:
        - Inputs are not mutated.
        - A single float (possibly NaN) representing Pearson's r is returned, or an exception is raised if preconditions are violated.

## Side Effects:
    - No I/O (files, network) or global-state mutation.
    - May emit warnings issued by scipy.stats.pearsonr (e.g., ConstantInputWarning).

## Control Flow:
flowchart TD
    Start[Start] --> CallRavelAll[Call alldims.ravel() -> flat_alldims]
    CallRavelAll --> CallRavelReduced[Call reduced.ravel() -> flat_reduced]
    CallRavelReduced --> CompareLen{Are lengths equal and >= 2?}
    CompareLen -- No --> CallPearson_NoLen[Call pearsonr(flat_alldims, flat_reduced) -> ValueError (propagates)]
    CompareLen -- Yes --> CallPearson[Call scipy.stats.pearsonr(flat_alldims, flat_reduced)]
    CallPearson --> pearsonResult{pearsonr returns (r, p)}
    pearsonResult -- ConstantInput --> WarnNaN[Scipy may warn and return NaN]
    pearsonResult -- Valid --> ReturnR[Return r (element 0)]
    WarnNaN --> ReturnNaN[Return NaN as correlation coefficient]

## Examples:
Example 1 — Typical usage with numpy arrays (assumes numpy and get_corr are available):
    arr = numpy.array([[1.0, 2.0], [3.0, 4.0]])
    reduced = numpy.array([1.0, 2.0, 3.0, 4.0])  # already 1-D
    r = get_corr(reduced, arr)  # returns Pearson's r between arr.ravel() and reduced.ravel()

Example 2 — Avoiding AttributeError when starting from Python lists:
    list_a = [0.1, 0.2, 0.3]
    list_b = [[0.1], [0.2], [0.3]]
    # Convert lists to numpy arrays so .ravel() exists
    flat_a = numpy.asarray(list_a)
    flat_b = numpy.asarray(list_b)
    r = get_corr(flat_a, flat_b)

Example 3 — Defensive pattern with error handling:
    try:
        r = get_corr(reduced_candidate, alldims_candidate)
    except AttributeError:
        # convert inputs to numpy arrays or raise a clear error to caller
        raise
    except ValueError:
        # handle mismatched sizes or insufficient length
        raise
    # Inspect r; if numpy.isnan(r) then inputs were constant or invalid for correlation

## `hypertools.tools.describe.get_cdist` · *function*

## Summary:
Compute the full pairwise distance matrix between all rows of a numeric 2-D array, using SciPy's default distance metric.

## Description:
This small helper wraps scipy.spatial.distance.cdist to compute distances between every pair of observations (rows) in the supplied array x. It is purposely extracted as a single-call utility so callers do not need to import or call cdist directly, and so the codebase has a single place to adjust behavior (for example, to memoize, change metric, or add preprocessing) in the future.

Known callers in this codebase:
- No direct callers were discovered during analysis of the repository artifacts provided for this task. If present elsewhere, callers will typically be higher-level describe/analysis functions that need an N-by-N distance or dissimilarity matrix for visualization or clustering stages.

Why this is a separate function:
- Encapsulates "pairwise distance of rows" semantics (cdist(x, x)) so the rest of the codebase can request an observation-vs-observation distance matrix without duplicating the call or importing SciPy directly.
- Keeps a clear responsibility boundary: transform an array of observations into a full symmetric distance matrix.

## Args:
    x (array-like, shape (n_observations, n_dimensions)):
        Numeric input where each row is an observation/vector. Accepts numpy.ndarray or array-like objects that can be converted to a 2-D numeric array.
        - Required: must be 2-D or convertible to a 2-D numeric array where the second dimension is the feature dimension.
        - Allowed values: numeric values (finite or NaN). Non-numeric contents will typically cause conversion or computation errors propagated from SciPy/numpy.

Interdependencies:
- There are no optional parameters to select the distance metric or other options; the function relies on scipy.spatial.distance.cdist defaults (Euclidean metric by default) and will inherit its behavior.

## Returns:
    numpy.ndarray, shape (n_observations, n_observations)
    - A dense symmetric matrix of pairwise distances between rows of x.
    - Diagonal entries are zero (distance from an observation to itself).
    - dtype is a floating type (as returned by SciPy/numpy); distances that cannot be computed (e.g., because of NaN inputs) will be NaN in the corresponding entries.
    - Edge-case returns:
        * If n_observations == 0 (x has zero rows), returns an array with shape (0, 0).
        * If n_observations == 1, returns a 1x1 array containing 0.0.

## Raises:
    Any exception raised by scipy.spatial.distance.cdist will be propagated.
    Common raised exceptions include:
    - ValueError: if x cannot be interpreted as a 2-D array of vectors with consistent dimensionality, or if input dimensionalities are incompatible.
    - TypeError: if x contains non-numeric types that prevent numeric operations inside cdist.

## Constraints:
Preconditions:
    - Caller must provide an array-like x where each row represents a vector of equal length.
    - Intended for datasets where the full N-by-N matrix is acceptable in memory; caller should ensure sufficient memory for O(n^2) storage.

Postconditions:
    - The returned matrix is a numeric, symmetric distance matrix consistent with scipy.spatial.distance.cdist behavior for identical inputs.
    - No modification is made to the input x by this function.

## Side Effects:
    - None within the local environment: the function performs no I/O, prints nothing, and does not mutate global state.
    - External library calls: invokes SciPy's cdist, which performs numeric computations in memory.

## Control Flow:
flowchart TD
    A[Start: receive x] --> B{Can x be interpreted as 2-D numeric array?}
    B -- No --> C[cdist raises ValueError/TypeError -> propagated]
    B -- Yes --> D[Call cdist(x, x)]
    D --> E[Receive distance matrix]
    E --> F[Return distance matrix]
    C --> G[Error propagated to caller]

## Examples (prose):
- Typical usage scenario:
    1. A higher-level "describe" or visualization routine has a dataset of shape (100, 50) where each row is a 50-dimensional observation.
    2. That routine calls this helper to obtain a 100x100 pairwise distance matrix for clustering or heatmap visualization.
    3. The helper returns a symmetric 100x100 floating-point array; the caller may then normalize or visualize it.

- Handling invalid input:
    - If the caller accidentally passes a 1-D array (a length-M vector) rather than a 2-D array shaped (M, D), SciPy's cdist will raise ValueError or produce an error during conversion; callers should validate or reshape input to (n, 1) if appropriate before calling.
    - If the dataset is large (for example, more than a few tens of thousands of rows), callers should avoid calling this function directly because memory/time will grow as O(n^2); instead consider approximate or streaming distance methods.

- NaNs and missing data:
    - If x contains NaN entries, distances involving rows with NaNs will generally be NaN in the returned matrix. Callers that require finite distances should preprocess or impute missing values before calling.

## Implementation notes for reimplementation:
    - This function consists of a single call to scipy.spatial.distance.cdist with the same array used for both arguments.
    - Ensure the implementation accepts array-like inputs and allows SciPy/numpy to handle conversions and error messages to keep behavior consistent with the standard SciPy implementation.

