# `correlations.py`

## `src.ydata_profiling.model.correlations.Correlation` · *class*

*No documentation generated.*

### `src.ydata_profiling.model.correlations.Correlation.compute` · *method*

## Summary:
Abstract contract for computing correlations for a dataset given profiler settings and a precomputed variable summary; implementations compute and return a Sized correlation result (e.g., matrix/array/dataframe) or None and must raise NotImplementedError when not implemented on the base class.

## Description:
This function defines the interface and expectations for a concrete correlation-computation implementation. It exists so different correlation estimators (Pearson, Spearman, Cramér's V, mutual information–based, etc.) can provide their own computation while exposing a consistent signature to the profiling pipeline.

Known callers and lifecycle stage:
- Intended to be called by the profiling pipeline's correlation-calculation stage when the profiler aggregates correlation results for a dataset or for a subset of variables.
- Callers supply: 1) a Settings-like configuration object that controls which method and parameters to use, 2) a Sized dataset (commonly a pandas.DataFrame or numpy array-like), and 3) a summary dict with metadata for variables produced earlier in the profiling pipeline.
- The base implementation raises NotImplementedError; concrete subclasses or multimethod overloads implement the actual computation.

Why this is a separate method:
- Separation allows multiple correlation algorithms to be implemented, tested, and swapped independently without changing the profiling pipeline.
- Encapsulating correlation logic in its own implementation makes testing and extension (new estimators, heuristics, or performance optimizations) straightforward.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings (or the correlation-specific nested config model).
        - Semantics: Contains declarative options that control whether to calculate correlations, which estimator to use, thresholds, binning parameters, and reporting heuristics.
        - Allowed values: Valid Settings/Correlation config instances; implementations should read relevant fields (e.g., calculate, key, n_bins, threshold).
    df (Sized):
        - Type: any object implementing the Sized protocol (commonly pandas.DataFrame, pandas.Series, numpy.ndarray, or similar).
        - Semantics: The data on which correlations should be computed. Implementations should treat df as read-only.
        - Preconditions: df must be non-null and have a length; implementations may require DataFrame-like column semantics to compute pairwise correlations.
    summary (dict):
        - Type: dict
        - Semantics: Precomputed summary/metadata for variables (e.g., types, unique counts). Implementations may consult this to choose estimation strategies or skip unsuitable variables.
        - Allowed values: a mapping whose structure is defined by the profiling pipeline (not enforced here); implementers must defensively handle missing or partial information.

## Returns:
    Optional[Sized]:
        - Type: A Sized object representing correlation results (commonly a pandas.DataFrame for pairwise correlations, a pandas.Series for one-vs-rest correlations, or a numpy.ndarray). Returning None signals that no correlation result could be produced for the given input (for example, if config.calculate is False or when all variables are unsuitable).
        - Edge cases:
            * Return None when computation is intentionally skipped (e.g., configuration disables calculation) or when no valid variable pairs exist.
            * When returning an array-like, its dimensions must match the number of variables involved (consistent and documented by the implementation).
            * Do not return empty inconsistent structures; prefer None to ambiguous empty arrays where semantics would be unclear.

## Raises:
    NotImplementedError:
        - Condition: The base function always raises this exception; concrete implementations must override it.
    DataError (recommended for implementers):
        - Condition: Implementations SHOULD raise pandas.errors.DataError (or pandas.core.base.DataError) when input data are malformed or insufficient (e.g., zero-length series where a numeric correlation is required).
        - Note: The base function does not raise DataError itself, but the module imports DataError to encourage its use by implementations.

## State Changes:
    Attributes READ:
        - None in the base function (no self parameter). Concrete class implementations may read only their own instance state if they are instance methods; this interface defines no required instance attributes.
    Attributes WRITTEN:
        - None in the base function. Implementers should avoid mutating the passed df or summary objects; any caching or state mutation should be limited to the implementer's own instance fields and documented there.

## Constraints:
    Preconditions:
        - config must be a valid Settings (or correlation settings) instance.
        - df must implement Sized and typically be non-empty; implementers may require DataFrame-like semantics for column/series access.
        - summary should be a dict or mapping that may be incomplete; implementations must handle missing keys defensively.
    Postconditions:
        - If a Sized object is returned, it must be a consistent correlation result whose shape and index/column semantics (if applicable) are documented by the concrete implementation.
        - The function must not modify the input df or summary (treat them as read-only).
        - Concrete implementations that skip computation should return None rather than raising unless an actual error occurred.

## Side Effects:
    - The base function has no I/O side effects and raises NotImplementedError immediately.
    - Implementations MAY:
        * Emit warnings via warnings.warn to surface non-fatal issues (module-level warnings is already imported).
        * Read but should not modify external resources.
    - Implementers should avoid external service calls; correlation computation is expected to be local CPU/numpy/pandas work.

Implementation notes for implementers:
- Follow the signature exactly: compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized].
- Validate inputs early and raise DataError for malformed inputs.
- Prefer returning a pandas.DataFrame for pairwise correlations when working with DataFrame inputs so downstream report code can attach variable names and indices.
- Keep the method deterministic and side-effect-free with respect to inputs to simplify testing and caching.

## `src.ydata_profiling.model.correlations.Auto` · *class*

## Summary:
Auto is a stateless dispatcher/strategy-selector for correlation and association computation. It exposes a single static entry point, compute(config, df, summary), which is responsible for selecting the most appropriate pairwise association method for each variable pair based on profiling metadata and configuration and returning a pairwise association matrix (or None when no computation is applicable). The current source is a stub that raises NotImplementedError; the following documents the intended contract and a reimplementation recipe.

## Description:
- Purpose and role:
    - Centralizes decision logic that chooses a correlation/association technique for each variable pair (numeric-numeric, categorical-categorical, numeric-categorical) based on configuration and per-variable metadata (summary).
    - Orchestrates per-pair computation, error handling, fallbacks and the assembly of a final pairwise association matrix for the profiling pipeline.
- Typical callers and usage scenarios:
    - Called by the profiling pipeline after dataset summary generation during the correlations/associations stage.
    - Called when generating the correlations section of a profile report or when a user requests correlation matrices for analysis.
- Responsibility boundary:
    - Should not implement the low-level correlation algorithms itself (Pearson, Spearman, Cramér's V, Phi_k, etc.). Instead it should select among those strategy implementations, call them, and assemble results.
    - Should not perform I/O or modify the input summary or DataFrame. It may emit non-fatal warnings.
- Rationale:
    - Keeps selection and fallback logic in one place to avoid duplication across multiple correlation implementations and to provide consistent behavior (missing-value handling, minimum-sample-size checks, warnings).

## State:
- Class-level state:
    - None. Auto is stateless; compute is a static method and does not rely on or mutate instance attributes.
- Method signature (contract):
    - compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]
        - config: ydata_profiling.config.Settings — controls which techniques are enabled and selection heuristics.
        - df: Sized — typically a pandas.DataFrame containing the variables to analyze (may be coerced if array-like).
        - summary: dict — per-variable metadata produced by the summary step (expected keys: variable type, distinct values count, non-missing count, is_constant, etc.).
    - Valid return types:
        - None when computation is not applicable (fewer than two analyzable variables).
        - pandas.DataFrame (recommended) indexed and columned by variable names with shape (n, n).
        - or numpy.ndarray of shape (n, n) as an alternative.
- Invariants:
    - The method must not modify df or summary.
    - If a matrix is returned:
        - It is square with one row/column per analyzed variable.
        - Uncomputable pairs are represented as numpy.nan.
        - Diagonal semantics must be documented/consistent (recommended: 1.0 for correlation coefficients).
    - Warnings (recoverable issues) are emitted via the warnings module; exceptions are reserved for fatal / invalid inputs.

## Lifecycle:
- Creation:
    - No instantiation is required to use Auto.compute because the method is static.
    - If a system prefers an instance form, instantiation is permitted (inherits whatever behavior Correlation supplies) but is not necessary for working with compute.
- Usage (recommended sequence):
    1. Prepare a Settings object (or obtain from the global profiling settings).
    2. Ensure df is a pandas.DataFrame (or coercible to one) and that summary contains per-variable metadata.
    3. Call Auto.compute(config, df, summary).
    4. The method validates inputs, selects strategies per pair, computes pairwise associations, fills the symmetric matrix, finalizes the diagonal, and returns the matrix or None.
- Destruction / cleanup:
    - No resources to close; no cleanup required. The method does not open files or network connections.

## Method Map:
flowchart LR
    A[Start: Auto.compute(config, df, summary)] --> B[Validate inputs]
    B --> C[Determine analyzable variables using summary & config]
    C --> D{n_variables >= 2?}
    D -- No --> E[Return None]
    D -- Yes --> F[Initialize n x n matrix (numpy.nan)]
    F --> G[For each pair (i,j) with i <= j]
    G --> H[Select strategy based on types & config]
    H --> I[Align/drop missing; check sample size]
    I --> J{Sufficient data?}
    J -- No --> K[Set matrix[i,j] and [j,i] = numpy.nan; warn]
    J -- Yes --> L[Call strategy.compute(...)]
    L --> M{Success?}
    M -- Yes --> N[Assign result to matrix[i,j] and [j,i]]
    M -- Exception --> O[Catch, warn, leave numpy.nan]
    N --> P[Continue pairs]
    O --> P
    P --> Q[Finalize diagonal values; clip/normalize if needed]
    Q --> R[Return pandas.DataFrame or numpy.ndarray]

## Raises:
- Current (source) behavior:
    - NotImplementedError: the present implementation is a stub and raises this immediately.
- Recommended/future implementation - possible exceptions and when they should be raised:
    - TypeError:
        - If config is not a Settings instance.
        - If df is not coercible to a pandas.DataFrame.
    - KeyError:
        - If required per-variable keys are missing from summary and cannot be derived.
    - pandas.core.base.DataError / pandas.errors.DataError:
        - Low-level pandas operations used by strategy implementations may raise these; Auto should catch such exceptions for individual pairs, emit a warning, and set the corresponding cell to numpy.nan rather than propagating the error for the whole matrix.
    - ValueError:
        - If a strategy implementation raises ValueError for invalid input; Auto should treat this as a recoverable pair-level error unless the error indicates misconfiguration (in which case rethrowing with a descriptive message is acceptable).
- Recommended behavior on recoverable errors:
    - Catch pair-level exceptions (DataError, ValueError, etc.), warn with a clear message (including variable names and reason), and set the pair's cell to numpy.nan.

## Example:
- Purpose:
    - Show the typical (prose) sequence for computing correlations without showing raw code.
- Steps:
    1. Construct or obtain a Settings object with the correlation options you want (for example, enabling Pearson or specifying a preferred categorical association measure).
    2. Generate or obtain the profiling summary for your DataFrame; ensure it contains per-variable type, distinct count, and non-missing count fields.
    3. Ensure your data is in a tabular form (pandas.DataFrame) with variables as columns.
    4. Invoke the dispatcher: call Auto.compute with the Settings, the DataFrame, and the summary.
    5. Inspect the return value:
        - If None is returned, fewer than two analyzable variables were detected.
        - If a matrix is returned, it will be square and symmetric; inspect top correlations, handle numpy.nan entries for uncomputable pairs, and apply any reporting thresholds from your Settings.
- Notes on integration:
    - Upstream code (the profiling pipeline) should capture warnings emitted by Auto to surface fallback decisions to users.
    - Strategy implementations called by Auto should themselves be pure functions that operate on two aligned pandas.Series or a two-column DataFrame and return a single numeric association value or raise a recoverable exception.

### `src.ydata_profiling.model.correlations.Auto.compute` · *method*

## Summary:
Currently a stub that raises NotImplementedError. Intended to select an appropriate correlation/association strategy based on configuration and per-variable summary metadata, compute the pairwise association matrix for the provided dataset, and return that matrix (or None when no valid association can be computed). This method is static and does not modify object state.

## Description:
Known callers and context:
- Intended usage: called by the profiling pipeline after dataset summary generation during the correlations/associations stage of a profile report.
- Typical lifecycle (intended): dataset -> summary generation -> Auto.compute(config, df, summary) -> correlation matrix inserted into the report.

Why this logic is separated:
- The method is expected to centralize decision logic that chooses the most appropriate correlation/association technique for variable pairs based on metadata and configuration. This separation avoids duplicating selection logic and centralizes fallback and error-handling behavior.

NOTE: The current implementation in source code is a stub and immediately raises NotImplementedError. The remainder of this document describes the intended contract and a suggested implementation strategy to guide a developer implementing this method.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Role: configuration object that controls which correlation techniques are enabled and thresholds for method selection (e.g., minimum unique values to treat a variable as categorical).
        - Validation: implementation should verify config is an instance of Settings and that required keys/attributes are present; otherwise raise TypeError or a descriptive error.

    df (Sized)
        - Type: Any object implementing Sized; typically a pandas.DataFrame (recommended) or pandas.Series / array-like.
        - Role: dataset from which variables (columns) are taken for pairwise association computation.
        - Preconditions: for pairwise correlation, df should be a DataFrame with at least two columns and at least two rows. Implementations should coerce array-like inputs to a DataFrame where feasible or raise TypeError.

    summary (dict)
        - Type: dict
        - Role: per-variable metadata produced by the profiling summary stage, used to choose correlation strategies (expected keys include variable type, distinct count, non-missing count, is_constant flag).
        - Validation: if required metadata is missing, implementations should either derive it from df or raise KeyError with a clear message.

## Returns:
    Optional[Sized]
        - Type specified by the stub: Optional[Sized].
        - Contract (intended): On success, return a pairwise association matrix covering the variables considered. Recommended concrete return types:
            * pandas.DataFrame indexed and columned by variable names, shape (n_variables, n_variables), or
            * numpy.ndarray of shape (n_variables, n_variables).
        - If no computation is applicable (e.g., fewer than two variables), return None.
        - Edge-case behavior: uncomputable pairs should be represented as numpy.nan in the matrix.

## Raises:
    - NotImplementedError
        - The current source implementation raises this immediately.
    - (Suggested for a full implementation) TypeError
        - If config is not a Settings instance or df is not coercible to a DataFrame.
    - (Suggested for a full implementation) KeyError
        - If summary lacks required per-variable keys and derivation is not possible.
    - (Suggested for a full implementation) pandas.core.base.DataError or pandas.errors.DataError
        - Underlying pandas operations may raise these; recommended behavior is to catch them per-pair, warn, and place numpy.nan instead of letting the whole method raise.

## State Changes:
Attributes READ:
    - None (method is static and should not read instance attributes)

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - config is a valid Settings instance (implementation must validate).
    - df contains sufficient data for pairwise computations when required (typically at least two columns and two rows).
    - summary contains (or allows derivation of) per-variable type and cardinality information.

Postconditions (intended for implementations):
    - If a matrix is returned:
        * It contains one row/column per variable analyzed.
        * It is square with shape (n, n).
        * Cells for computable pairs contain numeric association values; uncomputable pairs contain numpy.nan.
    - The input summary dict and df must remain unmodified.

## Side Effects:
    - The current stub performs no I/O. A correct implementation should also avoid performing file or network I/O.
    - Recommended behavior: emit warnings via the warnings module for recoverable issues (e.g., fallback decisions, skipped pairs due to insufficient data).
    - The method may call other correlation strategy compute functions; these calls should be pure-computation only.

## Suggested implementation guidance (for developers implementing this method):
This section provides a clear, step-by-step recipe to implement Auto.compute while preserving the contract above.

1. Validate inputs:
    - Confirm config is a Settings instance; confirm df is coercible to a pandas.DataFrame.
    - If df is not a DataFrame, convert: df = pandas.DataFrame(df) (attempt to preserve column names).

2. Determine variables to analyze:
    - Use summary and config to filter variables (e.g., exclude constants, apply whitelist/blacklist from config).
    - If fewer than two variables remain, return None.

3. Initialize result container:
    - Create an n x n numpy.ndarray filled with numpy.nan where n is number of variables.
    - Track variable order and labels for constructing a pandas.DataFrame at return.

4. For each pair (i, j) with i <= j:
    a. Use summary metadata (variable type, unique counts) and config to select a correlation strategy:
        - numeric-numeric: prefer Pearson (or Spearman/Kendall if config requests nonparametric)
        - categorical-categorical: use Cramér's V or Phi_k depending on config and cardinalities
        - numeric-categorical: choose Phi_k or appropriate measure based on config
    b. Extract the two series from df, align indices if necessary, and drop rows where both are missing.
    c. If the pair has insufficient valid observations (below configured minimum), set cell to numpy.nan and warn.
    d. Call the selected strategy's compute(config, pair_df, summary_subset) inside a try/except:
        - On success, assign value to matrix[i, j] and matrix[j, i].
        - On pandas DataError, ValueError, or other recoverable exceptions, emit a warning and leave cell as numpy.nan.

5. Finalize:
    - Set diagonal values according to metric semantics (e.g., 1.0 for correlation coefficients).
    - Optionally clip results to expected ranges (e.g., [-1, 1] or [0, 1]).
    - Construct and return a pandas.DataFrame using variable labels and the computed matrix.

6. Logging and warnings:
    - Collect non-fatal warnings (method fallbacks, skipped pairs) using warnings.warn so calling code can capture them.

This document defines the observable contract (matching the source signature and its immediate NotImplementedError) and provides an explicit, safe, and testable suggested implementation path for developers to implement Auto.compute.

## `src.ydata_profiling.model.correlations.Spearman` · *class*

## Summary:
Spearman is a stateless correlation-method class that declares a static multimethod entrypoint to compute Spearman rank correlations; in the current source this entrypoint is a stub that raises NotImplementedError. This document specifies the intended, implementable behavior for a full implementation.

## Description:
Role and usage intent
- The class provides a single public entrypoint:
    - compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]
  The method is decorated with @staticmethod and @multimethod to allow overloads for specific input types (for example, a pandas.DataFrame specialization).
- Current source status: the compute method in the repository is a placeholder that raises NotImplementedError. The content below describes how a correct, production implementation should behave so a developer can implement it to replace the stub.
- Intended callers:
    - The profiling pipeline's correlation orchestration layer that selects which correlation metric to compute (e.g., "spearman") and dispatches to this class.
    - Unit tests and utilities that need Spearman correlation matrices.

Responsibility boundary
- Compute and return pairwise Spearman rank correlations for selected variables in a tabular dataset.
- Do not perform I/O, and do not mutate the input arguments (config, df, summary) in-place.
- The orchestration layer performs higher-level tasks (choosing which correlation method to run, passing config and summary, and consuming the result).

## State:
- Class-level state: none (stateless).
- Instance-level state: none (instantiation is unnecessary).
- Method signature (as declared in source):
    - compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]
    - The method is decorated with @staticmethod and @multimethod.

Parameter expectations and invariants
- config: a Settings-like object. Implementations must access attributes defensively (e.g., getattr(config, "calculate", True)).
- df: any object implementing __len__ and column-oriented access (preferred: pandas.DataFrame). Implementations should coerce convertible Sized inputs using pandas.DataFrame(df) and raise TypeError if coercion fails.
- summary: expected to be a dict mapping column names to per-column metadata produced earlier by the profiler. The implementation must handle missing keys or an empty dict gracefully; do not assume summary is None (the signature types it as dict).
- Output invariants (for a non-None return):
    - Preferred return: pandas.DataFrame of shape (n, n), index and columns equal to the selected variable names in the same order.
    - Values are floats in [-1.0, 1.0] or numpy.nan for undefined correlations; diagonal entries should be 1.0 where defined.
- Class invariant:
    - No mutation of inputs; produce new objects for intermediate transformations where needed.

## Lifecycle:
Creation
- No instantiation required: call Spearman.compute(config, df, summary) directly.

Usage (intended for a full implementation)
1. Prepare a Settings object (config) and a per-column summary dict produced earlier in the profiling pipeline.
2. Ensure df is a Sized object containing observations (rows) and variables (columns).
3. Call Spearman.compute(config, df, summary).
4. If the returned value is None, treat it as "no computation performed" (e.g., fewer than two eligible variables or computation disabled by config). Otherwise, expect a labeled pandas.DataFrame with pairwise Spearman correlations.

Destruction / cleanup
- No cleanup required.

Sequencing constraints
- compute is callable repeatedly and independently. Ensure config and summary are ready before calling.

## Method Map (intended call flow for a full implementation)
flowchart LR
    Orchestration[Correlation orchestration] -->|dispatches to| Compute[Spearman.compute(config, df, summary)]
    Compute --> Validate["Defensive validation: config, df, summary"]
    Validate --> Coerce["If needed, coerce df -> pandas.DataFrame"]
    Coerce --> Select["Select eligible variables (use summary to exclude non-numeric/constant)"]
    Select --> ShortCircuit{"n_selected < 2 or config.calculate is False?"}
    ShortCircuit -->|yes| ReturnNone[Return None]
    ShortCircuit -->|no| ComputeCorr["Compute correlations (prefer data.corr(method='spearman'))"]
    ComputeCorr --> HandleNaNs["Pairwise deletion for missing values; preserve numpy.nan where undefined"]
    HandleNaNs --> Postprocess["Postprocess (replace inf, ensure diag, optional thresholding)"]
    Postprocess --> ReturnResult[Return pandas.DataFrame or other Sized representation]
    ComputeCorr -.->|may raise| PandasDataError[Pandas DataError]
    Compute -.->|may warn| Warnings[warnings.warn(...)]

Note: This diagram describes the intended behaviour for an implementer replacing the NotImplementedError. The current repository implementation does not perform these steps.

## Implementation guidance (sufficient to reimplement compute)
Input validation and coercion
- Read config defensively; short-circuit and return None if getattr(config, "calculate", True) is False.
- If df is None or len(df) == 0: return None.
- If df is not a pandas.DataFrame, attempt coercion via pandas.DataFrame(df). If coercion fails, raise TypeError (or emit a warning and return None according to project policy).

Column selection
- Use pandas.DataFrame.select_dtypes(include=[numpy.number]) to find numeric variables by default.
- Use summary (dict) to exclude columns that are marked non-numeric, constant, or otherwise ineligible.
- Emit warnings.warn when columns are skipped for recoverable reasons.

Short-circuit
- If fewer than two eligible variables remain after selection: return None.

Computation
- Recommended straightforward approach:
    - result = data_selected.corr(method="spearman")
    - This performs pairwise Spearman correlation using rank transformation with average ranks for ties and pairwise deletion for missing data.
- Preserve numpy.nan for undefined correlations (e.g., those involving constant columns).

Postprocessing
- Replace non-finite values (e.g., inf) with numpy.nan.
- Ensure diagonal is 1.0 where self-correlation is defined; leave diag as numpy.nan for constant variables if applicable.
- Prefer returning the full DataFrame unchanged; do not automatically mask values below a config.threshold. Let orchestration decide how to use threshold values (unless project policy requires thresholding here—document any deviation).

Performance considerations
- For moderate numbers of columns, pandas' corr(method="spearman") is efficient and clear.
- For very wide datasets, compute only the necessary pairs (for example, pairs that could exceed threshold) to save memory/time.

Exceptions and warnings
- The current source raises NotImplementedError; a real implementation should remove that and:
    - Raise TypeError if df is not Sized and not coercible.
    - Raise ValueError for invalid config parameters (e.g., non-numeric threshold when numeric is required).
    - Catch pandas.core.base.DataError or pandas.errors.DataError from pandas and either re-raise with contextual information or emit a warnings.warn and return None (follow the pipeline's error-handling policy).
- Use warnings.warn for non-fatal issues (skipped columns, coercion fallbacks, insufficient pairwise observations).

Side effects
- Do not mutate inputs. Use copies or views for transformations.

Return types
- Preferred: pandas.DataFrame with float values (in [-1.0, 1.0] or numpy.nan) and index/columns equal to the selected variable names.
- Alternative: None to signal no computation or, if explicitly required by orchestration, a Sized list/array of (col_a, col_b, corr) triples for significant pairs — if this alternative is chosen, document the format and ensure it is consistent across correlation method implementations.

## Raises:
- NotImplementedError
    - Present in the repository stub. Implementers must remove this by providing a working implementation.
- TypeError
    - If df is not Sized and cannot be coerced into a tabular structure.
- ValueError
    - For invalid config parameter values required by compute.
- pandas.core.base.DataError or pandas.errors.DataError
    - May be raised by underlying pandas operations; catch and handle according to pipeline policy (re-raise with context or return None after warning).

## Example (intended usage after implementing compute)
- Setup:
    - config = Settings(...)  # ensure config.calculate is True if you want computation
    - df = pandas.DataFrame(...)  # tabular data
    - summary = {...}  # per-column metadata dict, possibly empty
- Call:
    result = Spearman.compute(config, df, summary)
- Interpret:
    - If result is None: insufficient eligible variables or computation disabled.
    - If result is a pandas.DataFrame: result.loc['x', 'y'] is the Spearman rank correlation between 'x' and 'y'; numpy.nan indicates undefined correlation.

Implementation note:
- Provide concrete multimethod overloads for common types (e.g., (Settings, pandas.DataFrame, dict)) to make dispatch explicit and allow optimized, type-specific implementations.

### `src.ydata_profiling.model.correlations.Spearman.compute` · *method*

## Summary:
Computes pairwise Spearman rank correlations for the provided tabular data and returns a labeled correlation matrix; currently the method is a stub and raises NotImplementedError.

## Description:
Known callers and lifecycle stage:
- Called by the correlation orchestration component of the profiling pipeline after per-column summaries are computed. Typical call site: correlation selection logic that dispatches to the requested correlation method (e.g., "spearman") and invokes its static compute(config, df, summary) entrypoint.
- Invocation occurs during the correlation-analysis stage of profiling, when variable relationships are being measured to produce a correlations report and detect high-correlation pairs.

Why this is a separate method:
- Spearman correlation requires ranking of variables (handling ties and ordinal behavior) before estimating monotonic relationships; isolating this logic allows specialized preprocessing (ranking), tie-aware policies, and method-specific error handling without complicating the orchestration code.
- The static multimethod-decorated compute function permits optimized overloads for specific input types (e.g., pandas.DataFrame versus numpy.ndarray) while keeping a consistent public interface.

## Args:
    config (Settings): Profiling configuration object that controls whether correlations are computed and may provide thresholds and reporting parameters. Implementations should read attributes defensively (e.g., config.correlation or similar nested structures). If config indicates computation is disabled (e.g., config.calculate is False or an equivalent flag), the method should short-circuit and return None.
    df (Sized): Tabular dataset (expected: pandas.DataFrame). Any object implementing __len__ and column-oriented access may be accepted if coercible to a DataFrame (e.g., numpy.ndarray, dict-of-arrays). The method should coerce df to pandas.DataFrame when reasonable. If df is None, empty, or cannot be coerced to a tabular structure, behavior is documented below.
    summary (dict): Per-column metadata produced earlier by the profiler. Use this to exclude non-numeric, constant, or otherwise ineligible columns. Must be handled gracefully if missing or partial (e.g., an empty dict).

## Returns:
    Optional[Sized]:
    - Preferred concrete return: pandas.DataFrame of shape (n, n) where n is the number of selected variables. Index and columns are the selected variable names in a deterministic order. Values are Spearman correlation coefficients (floats in [-1.0, 1.0]) or numpy.nan where correlation is undefined (for example, involving constant columns).
    - Alternative acceptable returns: None when computation is not applicable (fewer than two eligible variables, config disables computation, or df is invalid), or a Sized collection of (var_i, var_j, rho) tuples if the pipeline expects a sparse representation — choose one and document the choice consistently.
    - Edge cases:
        * If fewer than two eligible columns are available: return None.
        * If df has zero rows: return None.
        * Pairwise missing data policy: use pairwise-complete observations (pandas.DataFrame.corr(method="spearman") behavior is recommended).

## Raises:
    NotImplementedError: The current method body raises this unconditionally (stub).
    (Recommendations for a concrete implementation)
    TypeError: If df is not Sized and cannot be coerced to a tabular structure, or if required arguments are of incompatible types.
    ValueError: For invalid config parameters required by compute (for example, a non-numeric threshold where a numeric threshold is required).
    pandas.core.base.DataError or pandas.errors.DataError: May be raised by underlying pandas operations; implementations should catch these, warn, and either re-raise with contextual information or return None depending on pipeline policy.

## State Changes:
Attributes READ:
    - None (this is a static method; it does not read any self.<attr> attributes). It does read the passed parameters config and summary but does not mutate any self attributes.
Attributes WRITTEN:
    - None (no self.<attr> modifications; implementations must avoid mutating config, df, or summary in-place).

## Constraints:
Preconditions:
    - config must be a Settings-like object (or compatible) with flags indicating whether correlation calculation should be performed.
    - df must be Sized (implement __len__) and ideally convertible to a pandas.DataFrame with columns representing variables and rows representing observations.
    - summary, if provided, should be mapping-like; the method must tolerate missing keys or empty dicts.
Postconditions:
    - If a non-None result is returned as a pandas.DataFrame:
        * Shape will be (n, n) where n is the number of selected variables.
        * Index and columns correspond to the same selected variable names in identical order.
        * Values are in [-1.0, 1.0] or numpy.nan for undefined correlations.
        * The diagonal is 1.0 for variables where self-correlation is defined; constant-variable diagonals may be numpy.nan depending on implementation choices.
    - If returning None, no modifications are made to input arguments.

## Side Effects:
    - No external I/O or network calls should be performed.
    - Prefer not to mutate df, config, or summary in-place; operate on a shallow copy or on views that do not alter the caller's data.
    - Use python warnings.warn(...) to surface recoverable issues (e.g., skipped columns, pandas DataError caught during computation).
    - May consume CPU and memory proportional to the number of numeric columns; for very wide datasets, consider computing only the upper triangle or streaming pairs to reduce memory footprint.

Implementation notes / guidance to reimplement:
    - Coerce df to pandas.DataFrame when needed. Handle pandas.Series specially (treat as single-column DataFrame).
    - Select eligible variables:
        * Use summary to exclude non-numeric or flagged columns, or fall back to pd.DataFrame.select_dtypes(include=[numpy.number]) and sensible defaults for ordinal/ordinal-like variables.
        * Exclude constant columns (single unique non-NaN value) if desired; document whether such columns lead to NaN correlations or are filtered out before computation.
    - Short-circuit if fewer than two eligible columns: return None.
    - Compute Spearman correlations:
        * Recommended: use pandas' built-in pairwise correlation: df_selected.corr(method="spearman"), which handles ranking and pairwise-complete observations.
        * Ensure deterministic column ordering.
    - Postprocess:
        * Replace non-finite values with numpy.nan.
        * Optionally apply thresholding/filtering according to config; if a threshold is applied, clearly document whether the returned structure is the full matrix with masked/zeroed entries or a filtered list of pairs.
    - Error handling:
        * Catch pandas DataError, warn with context, and return None or re-raise as ValueError depending on the severity policy.
        * Validate numeric config parameters before use and raise ValueError for invalid values.

## Example usage (conceptual):
    - Prepare a Settings config that allows correlation calculation and provides thresholds if needed.
    - Ensure a pandas.DataFrame df and a summary dict exist.
    - Call: result = Spearman.compute(config, df, summary)
    - Interpret result:
        * If None: not enough eligible variables or computation disabled.
        * If DataFrame: result.loc['var_a', 'var_b'] is the Spearman rho between var_a and var_b (or numpy.nan).

## `src.ydata_profiling.model.correlations.Pearson` · *class*

## Summary:
A correlation-method class representing Pearson correlation computation. It defines a static, multimethod-dispatched compute entrypoint intended to produce a Pearson correlation matrix (or an equivalent sized collection) for tabular data given a profiling configuration and per-column summary.

## Description:
The Pearson class groups the implementation of Pearson correlation computation as a distinct, re-usable component of the profiling pipeline. The class itself contains no instance state; instead it exposes a static method compute that is intended to be overloaded via multimethod for different input types (for example, a pandas.DataFrame-specific overload). The existing source is a placeholder that raises NotImplementedError; a concrete implementation should:

- Be invoked during the correlation-analysis stage after per-column summaries are available.
- Accept a Settings-like configuration object, a Sized dataset (typically a pandas.DataFrame), and a summary dict produced earlier in the pipeline.
- Return either:
  - A square pandas.DataFrame of Pearson correlation coefficients (index and columns equal to the selected numeric column names), or
  - None if fewer than two numeric columns exist, or
  - An alternative Sized collection of correlated pairs if the codebase prefers that representation — but that must be documented and consistent across the pipeline.

Because compute is declared static and decorated with multimethod, callers can use Pearson.compute(...) without instantiating the class; alternative overloads should be added to the same name to handle specific df types.

## State:
- Class attributes: none (no persistent state).
- Instance attributes: none (class is used as a stateless namespace for the compute function).
- For __init__: not applicable; Pearson relies on static methods and does not require instantiation.

Invariants:
- The class itself holds no mutable state and must not assume side-effects or stateful behavior across calls.
- Implementations of compute must not mutate the provided df in-place unless explicitly documented. Prefer working on a copy or using non-mutating pandas operations.

## Lifecycle:
Creation:
- No instantiation required. Use the class directly to call the static multimethod compute.

Usage:
- Typical call: Pearson.compute(config, df, summary)
  - config: a ydata_profiling.config.Settings (or equivalent) used to control thresholds/behavior
  - df: a Sized object (preferably pandas.DataFrame) containing the dataset to analyze
  - summary: dict with per-column summaries produced earlier by the profiler; used optionally to skip non-numeric/constant columns
- If multiple overloads are required, register them by adding additional @multimethod-decorated static methods with different type signatures (for example, handling numpy arrays or sparse matrices).
- Recommended invocation order:
  1. Build/obtain the profiling Settings that indicate whether to compute correlations and any thresholds.
  2. Ensure per-column summaries are available and pass them in.
  3. Call Pearson.compute(config, df, summary).
  4. Inspect the returned correlation matrix (or None) and handle NaNs/constant columns as needed.

Destruction:
- No special cleanup; no context manager or close() is required.

## Method Map:
flowchart LR
    A[Caller: profiling pipeline] --> B[Pearson.compute(config, df, summary)]
    B --> C{Validate inputs}
    C -->|df convertible to DataFrame| D[Select numeric columns]
    C -->|df not convertible| E[Raise TypeError]
    D --> F{Count numeric columns}
    F -->|<2| G[Return None]
    F -->|>=2| H[Compute correlations]
    H --> I[Handle NaNs/constant cols]
    H --> J[Apply config threshold/filtering]
    I --> K[Return pandas.DataFrame correlation matrix]
    J --> K

Notes:
- The multimethod dispatcher sits conceptually before "Validate inputs". Overloads for specific df types can short-circuit conversion and perform optimized computations.

## Behavior and Implementation Guidance (sufficient to reimplement compute):
Inputs:
- config (Settings): Read defensively using getattr(config, "attribute", fallback) since the Settings object may vary. Relevant attributes: calculate (bool), threshold (float), warn_high_correlations (int) and any other user extensions.
- df (Sized): Prefer a pandas.DataFrame. If df is not a DataFrame but is convertible (numpy.ndarray, dict-of-arrays, etc.), coerce via pandas.DataFrame(df). If conversion fails or df lacks __len__, raise TypeError.
- summary (dict): Optional per-column metadata. Use to skip non-numeric or constant columns if available.

Selection of columns:
- Select numeric columns using pandas' dtype checks, e.g., DataFrame.select_dtypes(include=[numpy.number]).
- Optionally exclude columns flagged in summary as non-numeric or constant to avoid computing meaningless correlations.

Early exit:
- If fewer than two numeric columns remain, return None.

Missing data:
- Use pairwise complete observations for each pair. pandas.DataFrame.corr(method="pearson") performs pairwise deletion by default and is recommended for full-matrix computation.
- Document the missing-value policy (pairwise deletion) clearly.

Constant or zero-variance columns:
- pandas returns NaN for correlations involving constant columns. Preferred behavior is to preserve NaN so downstream components can detect constant columns, but a project-wide policy may instead replace NaN with 0.0. Choose one and document it.

Thresholding and reporting:
- If config.threshold exists and is numeric, callers may expect either:
  - a full matrix with values masked/zeroed for abs(value) < threshold, or
  - an extracted list of correlated pairs whose absolute correlation >= threshold.
- Implementations must document which representation they return.

Return value:
- Recommended: pandas.DataFrame with index and columns equal to the selected numeric column names, values in [-1.0, 1.0] or numpy.nan for undefined pairs.
- Alternative valid return: None when no correlations computed, or a Sized list/tuple of (col_a, col_b, correlation) triples for significant pairs.

Performance:
- For moderate numbers of numeric columns, use DataFrame.corr(method="pearson") to compute the full matrix efficiently.
- For very wide data, consider a pairwise iteration that computes only the upper triangle and yields/filter pairs of interest.

Exception handling:
- The placeholder raises NotImplementedError.
- A full implementation should:
  - Raise TypeError if df is not Sized and cannot be coerced.
  - Raise ValueError for invalid config values (e.g., threshold not numeric or outside [0,1]).
  - Catch pandas DataError (pandas.core.base.DataError or pandas.errors.DataError) for malformed input; either re-raise with contextual information or issue warnings and return None.
  - Use python warnings.warn for recoverable problems (skipped columns, NaNs in result).

Side effects:
- Avoid mutating df in-place; operate on a copy if alterations are necessary (e.g., coercions, dtype conversions).
- Emit warnings for skipped columns, caught DataError, or other non-fatal problems.

## Raises:
- NotImplementedError: always raised by the current placeholder compute.
- TypeError (recommended in concrete implementation): if df is not Sized or cannot be converted to a tabular DataFrame.
- ValueError (recommended): if config contains invalid values required by compute (e.g., invalid threshold).
- pandas.core.base.DataError or pandas.errors.DataError: may be raised by underlying pandas operations; implementations should catch, annotate, or re-raise with context.

## Example:
- Typical usage (conceptual):
  1. Ensure you have a profiling Settings object (config), a pandas.DataFrame df, and a per-column summary dict.
  2. Call the static method:
     result = Pearson.compute(config, df, summary)
  3. Interpret result:
     - If result is None: fewer than two numeric columns were available.
     - If result is a pandas.DataFrame: use result.index/result.columns for variable names and inspect numeric cells (NaN indicates undefined correlation).
  4. If config.threshold was consulted by the implementation, inspect only entries with abs(value) >= threshold to find high correlations.

Implementation note:
- Because compute is decorated with multimethod, provide concrete overloads for the types you expect (e.g., (Settings, pandas.DataFrame, dict)) to avoid ambiguous dispatch and to enable optimized implementations for known input types.

### `src.ydata_profiling.model.correlations.Pearson.compute` · *method*

## Summary:
A static, type-dispatched placeholder for computing Pearson correlation coefficients over a dataset; the current implementation is unimplemented and always raises NotImplementedError. Intended effect when implemented: compute and return a correlation matrix (or None) without mutating object state.

## Description:
- Known callers and context:
    - Conceptually invoked during the correlation-analysis stage of the profiling pipeline after per-column summaries are available. Callers are expected to pass the profiling configuration (Settings), the dataset (typically a pandas.DataFrame), and the summary dict produced by earlier steps.
    - Because this definition is decorated as a multimethod and declared static, different overloads are intended for different input types (for example, a pandas.DataFrame-specific overload).
- Why this method is separate:
    - Computing correlations is a distinct responsibility with many edge cases (non-numeric columns, missing values, constant columns, small sample sizes) and many possible optimizations (vectorized matrix computation vs. pairwise loops). Extracting it into a dedicated, dispatchable method isolates that complexity and allows type-specific implementations.
- Implementation guidance (how to reimplement):
    1. Input validation:
        - Prefer a pandas.DataFrame for df. If df is not a DataFrame but is convertible (e.g., numpy array, dict-of-arrays), convert with pandas.DataFrame(df). If conversion fails, raise TypeError.
        - Ensure df implements Sized (len(df) available).
    2. Select numeric columns:
        - Identify numeric columns via pandas' dtypes (e.g., DataFrame.select_dtypes(include=[numpy.number])).
        - Optionally consult the summary dict to skip columns flagged as non-numeric or constant.
    3. Minimum columns and early exit:
        - If fewer than two numeric columns are available, return None (Optional return) — signal that no Pearson correlations are computed.
    4. Missing values handling:
        - Use pairwise deletion: for a given pair (A, B) compute correlation over rows where both A and B are non-missing (pandas.Series.corr does this by default).
        - Alternatively, compute the full matrix with DataFrame.corr(method='pearson'), which uses pairwise complete observations.
    5. Constant columns and NaN correlations:
        - pandas returns NaN for correlations involving constant columns (zero variance). Decide one consistent policy:
            * Preferred: keep NaN in the matrix so the caller can detect constant columns; or
            * Alternative: set NaN to 0.0 if you prefer to treat constant relationships as zero correlation.
        - Document and implement whichever choice is used across the codebase.
    6. Thresholding and filtering:
        - If the Settings object exposes a threshold (e.g., correlation threshold), read it defensively: threshold = getattr(config, "correlation_threshold", None). If provided and numeric, you may zero or remove entries with absolute value below threshold or return a filtered list of highly correlated pairs instead of a full matrix — be explicit in the implementation.
    7. Output shape and index/columns:
        - Return a pandas.DataFrame (or other Sized matrix-like object) whose index and columns are the selected numeric column names and whose values are Pearson correlation coefficients in [-1.0, 1.0] or NaN for undefined pairs.
    8. Performance considerations:
        - For many numeric columns use the vectorized DataFrame.corr(method='pearson') to compute the full matrix efficiently.
        - For extremely wide datasets where memory is a concern, compute only the upper triangle or compute pairwise correlations iteratively and yield/store only significant pairs.
    9. Exception handling:
        - Catch pandas.DataError (pandas.core.base.DataError or pandas.errors.DataError) if DataFrame operations fail, re-raise or convert to a user-friendly exception after adding context.
        - Validate any numeric threshold from config and raise ValueError for invalid threshold values (non-numeric or outside [0,1]).
    10. Document decisions:
        - Clearly document whether the function returns None when no correlations are computed, how NaNs are handled in the result, and what the config-driven filtering behavior is.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: configuration options that influence computation (e.g., thresholds, whether to return a full matrix or only significant pairs). Implementations must access config attributes defensively (use getattr) because Settings may not expose a given attribute.
    df (Sized):
        - Type: Any object implementing __len__; typical usage expects a pandas.DataFrame.
        - Constraints: If not a DataFrame, implementation should attempt conversion or raise TypeError.
    summary (dict):
        - Type: dict
        - Purpose: auxiliary, per-column summary data produced earlier in the pipeline. Implementations may read this to skip non-numeric or invalid columns or to reuse precomputed statistics.

## Returns:
    Optional[Sized]
    - Typical successful return: pandas.DataFrame representing the Pearson correlation matrix (index and columns are the selected numeric column names). Each cell is a float in [-1.0, 1.0] or numpy.nan if undefined (e.g., constant column pair).
    - Alternate successful return: a Sized collection of significant correlated pairs (implementation choice; must be documented).
    - Edge-case returns:
        - None if fewer than two numeric columns exist (no correlations computed).
        - Empty pandas.DataFrame is also acceptable if documented as a design choice.

## Raises:
    NotImplementedError:
        - Condition: Always raised by the current placeholder implementation.
    TypeError (recommended for a full implementation):
        - Condition: If df is not Sized or cannot be converted to a tabular structure (pandas.DataFrame).
    ValueError (recommended):
        - Condition: Invalid configuration values (e.g., threshold not numeric or outside [0, 1]).
    pandas.core.base.DataError or pandas.errors.DataError (may be raised by pandas operations):
        - Condition: Underlying pandas correlation computation fails due to malformed data; implementations should catch, annotate (via warnings or a wrapped exception), or re-raise with context.

## State Changes:
    Attributes READ:
        - None. The method is declared static and does not read instance attributes (no self).
    Attributes WRITTEN:
        - None. The method must not mutate object attributes.
    Note: Implementations may mutate the provided df if they explicitly choose to (not recommended). Document any such mutation if performed.

## Constraints:
    Preconditions:
        - The caller should pass:
            * config: a Settings-like object (attributes read defensively).
            * df: a Sized, tabular dataset (pandas.DataFrame recommended) with column names.
            * summary: dict produced earlier in the pipeline.
        - Implementations expecting pandas.DataFrame may call pandas.DataFrame(df) to coerce convertible inputs.
    Postconditions:
        - If the method returns a pandas.DataFrame, it is a square matrix with index and columns equal to the selected numeric columns and contains Pearson correlation coefficients or NaN for undefined values.
        - If the method returns None, the caller can assume fewer than two numeric columns were available.

## Side Effects:
    - The current placeholder has no side effects (no I/O, no external calls, no mutation of objects outside the function scope).
    - A concrete implementation should avoid mutating the input df; if it must, it should operate on a copy or document the mutation explicitly.
    - Implementations may emit warnings (via python warnings) when:
        * invalid columns were skipped,
        * correlations could not be computed for some pairs (NaNs),
        * DataError was caught and handled.

## `src.ydata_profiling.model.correlations.Kendall` · *class*

## Summary:
Represents the Kendall rank-correlation implementation used by the profiling pipeline; exposes a static multimethod compute(...) that produces pairwise Kendall tau correlations for a set of variables.

## Description:
This class is a thin abstraction that groups the Kendall correlation implementation and exposes a single public entrypoint: the static multimethod compute(config, df, summary). It is intended to be invoked by the profiling pipeline's correlation orchestration layer (which selects the desired correlation metric and dispatches to the corresponding implementation), by test code, or by utilities needing a Kendall correlation matrix.

Why this class exists:
- Kendall's tau computation has distinct requirements from Pearson and Spearman (tie handling, pairwise-complete handling of missing values, different numerical characteristics). Isolating Kendall logic allows tailored preprocessing, robust error handling, and specific postprocessing without complicating the general orchestration code.

Responsibility boundaries:
- Responsible only for computing Kendall pairwise correlations and returning them in a labeling-preserving structure (preferably a pandas.DataFrame).
- Must not mutate inputs (config, df, or summary) in-place nor perform external I/O.

Primary caller:
- The correlation orchestration component in the profiling pipeline (the component that chooses between Pearson, Spearman, Kendall, etc., based on configuration) and unit tests.

Decorator note:
- The compute method is decorated with both @staticmethod and @multimethod. The multimethod decorator enables runtime dispatch based on argument types; implementations should respect this and ensure overloads, if provided, match intended argument type signatures.

## State:
Class-level:
- No persistent instance state. The class groups a static method and does not maintain attributes.

Method-level (compute):
- Signature: compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]
- Parameters:
    - config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: Declarative configuration for correlation computation (e.g., whether to calculate correlations, thresholds). Implementations must read its attributes defensively.
    - df (Sized):
        - Type: Any object implementing __len__ and data-access (expected: pandas.DataFrame or pandas.Series; other 2D array-like objects may be coercible).
        - Role: Observational data with rows as samples and columns as variables. Implementations should coerce non-DataFrame Sized inputs to pandas.DataFrame where reasonable.
        - Constraint: If df is None or has zero rows, computation should short-circuit and return None.
    - summary (dict):
        - Type: dict or mapping-like
        - Role: Optional per-variable metadata produced earlier in the profiling pipeline. Can be used to include/exclude columns (e.g., based on detected type, flags). Implementation must handle missing, empty, or partial summary gracefully.
- Return value:
    - Optional[Sized]
        - Preferred concrete return: pandas.DataFrame of shape (n_vars, n_vars) with index and columns labeled by the selected variable names; values are pairwise Kendall tau correlations (floats ∈ [-1, 1] or numpy.nan for undefined).
        - Alternatives: numpy.ndarray (shape [n, n]) if downstream consumers expect raw arrays.
        - Return None when computation should not be performed (e.g., fewer than 2 eligible variables, config.calculate is False, or input is invalid).
- Invariants:
    - The method must not mutate df, config, or summary.
    - If a non-None result is returned:
        - Shape is (n, n) where n is the number of selected variables.
        - If returning a DataFrame, index and columns correspond to the selected variable names in the same order.
        - Diagonal entries are 1.0 where self-correlation is defined; undefined/self-constant cases may be numpy.nan.
        - Off-diagonal values lie in [-1.0, 1.0] or numpy.nan where undefined.

## Lifecycle:
Creation:
- The class serves as a namespace for the static compute method. Callers should invoke Kendall.compute(config, df, summary) directly; instantiating Kendall is not required and is not part of normal usage.

Usage pattern:
1. Input validation and coercion:
    - Validate config presence and that summary is mapping-like if provided.
    - If df is None or len(df) == 0: return None.
    - Coerce df into pandas.DataFrame if it is not already one (handle pandas.Series specially).
2. Column selection:
    - Use summary metadata (if present) to include/exclude columns.
    - Otherwise select numeric or ordinal-compatible columns.
    - Exclude columns that are constant (single unique value) or contain only NaNs; emit warnings about such exclusions instead of raising unless pipeline policy dictates otherwise.
3. Short-circuit:
    - If fewer than 2 eligible columns remain: return None.
4. Computation:
    - Work on a shallow copy of the selected data subset to avoid mutating caller data.
    - Prefer pandas' built-in pairwise correlation: data.corr(method="kendall"), wrapped in try/except for pandas.DataError.
5. Postprocessing:
    - Replace non-finite values with numpy.nan; ensure diagonal is 1.0 where applicable.
    - Optionally apply thresholding/sparsification based on config flags (read defensively).
6. Return:
    - Return a labeled pandas.DataFrame by default; return an ndarray only if explicitly required by caller.
Destruction:
- No cleanup required.

Sequencing constraints:
- compute can be called repeatedly and independently; ensure config and summary are prepared prior to calling.

## Method Map:
flowchart LR
    Pipeline[Correlation Orchestration] -->|requests "kendall"| KendallCompute[Kendall.compute(config, df, summary)]
    KendallCompute --> Coerce["Coerce df -> pandas.DataFrame"]
    Coerce --> Select["Select eligible columns (use summary)"]
    Select --> ShortCircuit{"n_selected < 2 ?"}
    ShortCircuit -->|yes| ReturnNone[Return None]
    ShortCircuit -->|no| ComputeCorr["Compute corr: data.corr(method='kendall')"]
    ComputeCorr --> Postprocess["Replace non-finite -> numpy.nan; ensure diag"]
    Postprocess --> ReturnResult[Return pandas.DataFrame]
    ComputeCorr -.->|may raise| PandasDataError[Pandas DataError]
    KendallCompute -.->|may warn| Warnings[warnings.warn(...)]

## Raises:
- NotImplementedError
    - Current stub raises this unconditionally. Implementers must remove this and provide a working implementation.
- ValueError
    - Recommended when input coercion fails (e.g., df cannot be converted to a column-oriented structure) or when summary is provided but is not mapping-like.
- pandas.errors.DataError or pandas.core.base.DataError
    - These may be propagated from pandas' correlation routines; implementations may catch them and either re-raise as ValueError with clearer context or return None after emitting a warning, depending on pipeline policy.
- TypeError
    - Suggested when provided arguments are of incompatible types and cannot be coerced.

Guideline: Prefer returning None or emitting warnings for recoverable/expected conditions (e.g., single-value columns) and reserve raised exceptions for irrecoverable input errors.

## Example:
- Typical usage (illustrative):
    1. Ensure a Settings instance exists (config) and that summary metadata has been computed or is available.
    2. Prepare data as a pandas.DataFrame (df) with rows as records and columns as variables.
    3. Call:
       result = Kendall.compute(config, df, summary)
    4. Interpret result:
       - If result is None: insufficient eligible columns or computation disabled.
       - If result is a pandas.DataFrame: result.loc['col_x', 'col_y'] contains the Kendall tau between 'col_x' and 'col_y'; diagonal entries are 1.0 where defined.
    5. No explicit cleanup is required.

Implementation notes:
- Prefer returning a labeled pandas.DataFrame to preserve variable names for downstream reporting.
- Avoid mutating inputs; operate on shallow copies.
- Use warnings.warn for non-fatal issues (skipping columns, coercion fallbacks).
- Ensure deterministic ordering of selected columns so returned matrices are predictable across runs.

### `src.ydata_profiling.model.correlations.Kendall.compute` · *method*

## Summary:
Specification for computing pairwise Kendall rank correlations for the provided dataset. Current implementation is a placeholder and raises NotImplementedError; this document defines the expected behavior, inputs, outputs, and a step-by-step implementation guide so a developer can implement the method correctly.

## Description:
This method is declared as a static multimethod and must implement the Kendall rank correlation computation for use by the profiling pipeline's correlation stage. Currently, the method body raises NotImplementedError.

Expected callers and lifecycle stage:
- Typically invoked by the profiling pipeline's correlation orchestration component that dispatches to per-method correlation implementations (pearson, spearman, kendall).
- Also callable by unit tests or utilities that request a Kendall correlation matrix for diagnostic or reporting purposes.

Why this is its own method:
- Kendall's tau requires treatment for ties, pairwise-complete handling of NaNs, and has different computational characteristics from Pearson/Spearman. Isolating Kendall logic allows tailored preprocessing, error handling, and choice of computation routine without duplicating orchestration.

Decorator and implementation note:
- The method is decorated with @staticmethod and @multimethod (multimethod dispatch may route on argument types). The current stub raises NotImplementedError.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Role: Global configuration object. Implementations SHOULD access correlation-specific options defensively (check attributes exist before use).
    df (Sized)
        - Type: Sized (expected to be pandas.DataFrame or pandas.Series; other sequence-like objects allowed if coercible)
        - Role: Observational data where rows are samples and columns are variables. Implementations SHOULD coerce non-DataFrame Sized inputs to pandas.DataFrame where reasonable.
    summary (dict)
        - Type: dict
        - Role: Per-variable metadata produced earlier in the profiling pipeline. MAY be used to select or exclude columns (e.g., skip flagged columns, favor numeric/ordinal columns).
        - Implementations MUST handle missing, empty, or partial summary information gracefully.

## Returns:
    Optional[Sized]
        - Expected behavior: return a two-dimensional sized correlation object representing pairwise Kendall tau correlations among selected variables.
            * Preferred concrete type: pandas.DataFrame (index and columns labeled by variable names).
            * Alternative: numpy.ndarray (shape [n_vars, n_vars]) if the caller expects raw arrays.
        - Return None:
            * When computation cannot/should not be performed (e.g., fewer than 2 selected variables, computation disabled, unsupported input).
        - Edge-case signaling:
            * Use numpy.nan for undefined pairwise correlations (e.g., when one variable is constant).
            * Diagonal should be 1.0 where self-correlation is defined; use numpy.nan where undefined.

## Raises:
    NotImplementedError
        - Condition: Current stub raises this unconditionally.
    ValueError (implementation-defined)
        - Suggested: when df cannot be coerced to a column-oriented structure or summary is not a mapping.
    pandas.errors.DataError or pandas.core.base.DataError
        - Propagated if raised by underlying pandas correlation routines; implementations may choose to catch and re-raise as ValueError with a clearer message.
    TypeError
        - Suggested: when incompatible dtypes or unexpected argument types are provided and not handled.

Implementations SHOULD avoid raising generic Exception for predictable conditions.

## State Changes:
Attributes READ:
    - None on self/class (method is static). The method will read from:
        - config (only to consult options)
        - summary (to select/exclude columns)
        - df contents (data values and dtypes)

Attributes WRITTEN:
    - None on self/class. The method MUST NOT mutate df, summary, or config in-place; work on local copies.

## Constraints:
Preconditions:
    - df must be Sized and ideally column-oriented (pandas.DataFrame preferred). If df is a pandas.Series, behavior should be well-defined (likely return None because no pairwise correlations exist).
    - At least two non-constant, eligible variables should be present after filtering to produce a non-None result.

Postconditions:
    - If a non-None correlation object is returned:
        * It has shape (n, n) with n equal to the number of selected variables.
        * Index/columns correspond to selected variable names (if returning DataFrame).
        * Values lie in [-1.0, 1.0] where defined; undefined entries are numpy.nan.

## Side Effects:
    - No external I/O or network calls should be performed.
    - The method MAY emit warnings (via warnings.warn) for non-fatal conditions such as skipped columns.
    - Memory allocation proportional to O(n^2) is expected for n selected variables.

## Specification / Implementation guidance (step-by-step):
The following pseudocode is a recommended implementation plan. Treat it as a specification rather than an assertion about the current code.

1. Input validation:
    - If df is None or len(df) == 0: return None.
    - If summary is provided but not a dict/mapping: raise ValueError.

2. Coerce to pandas.DataFrame:
    - If isinstance(df, pandas.Series): convert to DataFrame with single column (but if only one column, return None).
    - If not a DataFrame but Sized and indexable, attempt pandas.DataFrame(df); on failure raise ValueError.

3. Select candidate columns:
    - If summary contains explicit type/skip flags, honor those to include/exclude columns.
    - Otherwise select columns where pandas.api.types.is_numeric_dtype is True (or other ordinal-compatible dtypes).
    - Exclude columns with all NaNs or with a single unique value (constant columns). Optionally warnings.warn about exclusions.

4. Short-circuit:
    - If number of selected columns < 2: return None.

5. Compute correlation:
    - Work on a shallow copy: data = df[selected_columns].copy()
    - Prefer using pandas' pairwise routine:
        try:
            corr = data.corr(method="kendall")
        except (pandas.errors.DataError, pandas.core.base.DataError) as e:
            either re-raise or warnings.warn and return None depending on pipeline policy
    - Ensure corr preserves row/column labels in the same order as selected_columns.

6. Postprocess:
    - Replace non-finite entries with numpy.nan.
    - Ensure diagonal entries are 1.0 where defined.
    - If config contains thresholding/sparsification options (check defensively), apply them here.

7. Return:
    - Return corr (pandas.DataFrame) by default, or corr.values if a raw array is required by the caller.

## Example (illustrative, not runtime code):
- Given a DataFrame df with numeric columns ['a','b','c']:
    * result = Kendall.compute(config, df, summary)
    * If result is a DataFrame: result.loc['a','b'] is the Kendall tau between 'a' and 'b'
    * If result is None: fewer than 2 eligible variables after filtering or computation disabled.

## Notes:
- Favor pandas.DataFrame returns to preserve labels for downstream reporting.
- Use warnings.warn rather than raising for recoverable or informational conditions (e.g., skipping a constant column).
- Keep the implementation deterministic and side-effect free: do not mutate caller-supplied structures.

## `src.ydata_profiling.model.correlations.Cramers` · *class*

## Summary:
A stateless placeholder class representing the Cramér's V correlation estimator for categorical variables. The class exposes a static multimethod compute(config: Settings, df: Sized, summary: dict) that is declared but currently raises NotImplementedError; it is intended to be implemented to calculate Cramér's V.

## Description:
- What exists in source:
  - Cramers is a subclass of Correlation and defines a single static method decorated with @multimethod:
    - compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]
  - In the provided source, compute immediately raises NotImplementedError, indicating this class is an abstract/placeholder implementation.

- Where to use / call-sites:
  - The profiling correlation dispatcher or registry should call Cramers.compute(...) when the configuration requests the Cramér's V estimator (for example when Settings.correlation.key == "cramers_v").
  - Unit tests or utilities may call the static compute method directly to compute categorical-categorical association once implemented.

- Responsibility boundary:
  - As declared, this class's only responsibility is to provide the static entry point for computing the association between categorical variables. It should not perform dataset-wide orchestration (pair selection) or mutate Settings/summary.

## State:
- Class-level:
  - Stateless: there are no instance attributes and no persistent state.
  - __init__ is not used; the class is intended to be used via its static method.

- compute signature (must match source exactly):
  - config: Settings
  - df: Sized
  - summary: dict
  - return type: Optional[Sized]

- Invariants and expectations:
  - Implementations of compute should be pure (no mutation of inputs) and deterministic.
  - Implementations should ensure returned numeric results (when applicable) lie within [0.0, 1.0].
  - If computation is not applicable (e.g., degenerate inputs), compute should return None rather than raising, unless the input is malformed (then raise a descriptive exception).

## Lifecycle:
- Creation:
  - No instantiation required. Use the class as a namespace:
    - Call Cramers.compute(config, df, summary)

- Usage sequence (recommended; the current source only provides the method signature and NotImplementedError):
  1. Prepare inputs:
     - config: an instance of Settings (read-only inside compute).
     - df: sized container representing the two categorical variables; acceptable inputs include:
       - pandas.DataFrame with exactly two columns
       - A 2-tuple/list of two pandas.Series/array-like objects
       - Two aligned pandas.Series combined into a small DataFrame or equivalent sized container
     - summary: dict containing optional precomputed metadata. Implementations should not rely on summary being present.
  2. Call compute once per variable pair: Cramers.compute(config, df, summary)
  3. Interpret return:
     - None: computation not applicable (degenerate inputs, insufficient data)
     - float or numpy scalar: Cramér's V in [0.0, 1.0]
  4. No explicit cleanup required.

- Destruction:
  - No resources to release; standard garbage collection suffices.

## Recommended implementation guidance (for implementers)
This section describes a correct, portable algorithm that can be implemented behind the declared compute signature. Note: this is guidance — the current source does not implement it.

- Input normalization:
  - If df is a DataFrame, treat the two columns as the variables.
  - If df is a sized iterable of two elements, unpack them into two series-like objects.
  - Convert inputs to pandas.Series for convenience and alignment.
  - If the two variables have different lengths, raise ValueError.

- Missing values:
  - Drop pairwise rows where either value is missing. Let n be the number of remaining pairs.
  - If n == 0, return None.

- Contingency table:
  - Use pandas.crosstab or equivalent to compute observed counts T_ij.
  - Compute row sums R_i, column sums C_j and total n.

- Degenerate checks:
  - Let r = number of non-empty rows (unique categories in variable A), k = number of non-empty columns (unique categories in variable B).
  - If r < 2 or k < 2, return None.

- Chi-squared and Cramér's V:
  - Compute expected counts E_ij = (R_i * C_j) / n.
  - Compute chi2 = sum((T_ij - E_ij)^2 / E_ij) over cells with E_ij > 0.
  - Uncorrected V = sqrt( chi2 / (n * min(r - 1, k - 1)) )

- Optional bias correction (recommended):
  - Compute phi2 = chi2 / n
  - phi2_corr = max(0, phi2 - ((k - 1)*(r - 1)) / (n - 1))
  - denom = min(k - 1, r - 1) - ((k - 1)*(r - 1)) / (n - 1)
  - If denom <= 0: V_corr = 0.0 else V_corr = sqrt(phi2_corr / denom)
  - Choose to return V_corr when bias correction is desired; otherwise return V_uncorrected.

- Final step:
  - Clamp result to [0.0, 1.0] to mitigate floating-point noise.
  - Return Python float or numpy scalar.

- Numerical safety:
  - Use numpy float arithmetic, guard against division-by-zero, and skip cells with E_ij == 0.
  - Prefer returning None for truly inapplicable inputs rather than raising generic exceptions.

## Method Map
flowchart LR
    A[Prepare inputs: Settings, df (sized), summary] --> B[Cramers.compute(config, df, summary)]
    B --> C[Normalize inputs -> two pandas.Series]
    C --> D[Drop missing values and compute n]
    D --> E[Contingency table via pandas.crosstab]
    E --> F[Compute chi2]
    F --> G[Compute V_uncorrected]
    G --> H{Apply bias correction? (optional)}
    H -- yes --> I[Compute V_corrected]
    H -- no --> J[Use V_uncorrected]
    I --> K[Clamp to [0,1]]
    J --> K
    K --> L[Return float or None]

## Raises
- Present in source:
  - NotImplementedError: compute currently raises this to indicate no implementation exists.

- Recommended/expected if implementing:
  - TypeError: if df is not Sized or cannot be interpreted as two variables.
  - ValueError: if two input variables have mismatched lengths.
  - pandas.core.base.DataError or pandas.errors.DataError: re-raise if pandas operations fail.
  - Implementations should avoid raising for degenerate-but-valid inputs; prefer returning None in those cases.

## Example (usage described)
- Given a profiling Settings instance and two categorical pandas.Series a and b of the same length:
  1. Combine a and b into a two-column pandas.DataFrame or pass them as a 2-tuple/list.
  2. Call Cramers.compute(settings, df_pair, summary_dict).
  3. If the result is None: treat as "association not computed" (insufficient distinct categories or data). Otherwise the returned float is the Cramér's V in [0.0, 1.0].

Notes:
- Preserve the exact signature and decorators (@staticmethod and @multimethod) in any reimplementation to keep multimethod dispatch behavior consistent with the rest of the codebase.
- This documentation clarifies both the current source behavior (NotImplementedError) and the recommended, fully-specified algorithm to implement behind the declared API.

### `src.ydata_profiling.model.correlations.Cramers.compute` · *method*

## Summary:
A static multimethod placeholder that is intended to compute Cramér's V (or related categorical association) for the provided dataset; as currently implemented it does not perform any computation and immediately raises NotImplementedError.

## Description:
- Current behavior and callers:
    - This function is declared as a static multimethod and, in the repository snapshot provided, immediately raises NotImplementedError. Therefore, it performs no runtime computation or mutation.
    - It is intended to be invoked by the correlation-dispatching logic in the profiling pipeline when the Cramér-based categorical association (often named "cramers_v" or similar) is requested. (Note: specific caller locations are not present in this file; this sentence describes expected usage context, not the current implementation.)
- Why this is a separate method:
    - Cramér's V computation requires distinct logic (contingency tables, bias correction, optional discretization) and is conceptually separate from numeric correlation computations (Pearson/Spearman). Placing it in its own method keeps categorical-association concerns isolated and enables multimethod dispatch based on input types or configuration.

## Args:
    config (Settings):
        Correlation-related configuration (from ydata_profiling.config.Settings).
        - Expected fields used by this routine (typical): indicator whether to calculate correlations, discretization bin counts, or other correlation-specific options. The method signature requires a Settings-derived object; concrete fields used depend on the implementation chosen.
    df (Sized):
        The dataset view on which to compute the association(s). The type annotation is Sized to accept pandas DataFrame-like or other objects exposing len() and iteration/column access; concrete implementations typically expect a pandas.DataFrame or similar mapping from column names to Series.
        - Preconditions: df must be an object containing categorical variables (or variables that can be discretized into categories) for which pairwise association is meaningful.
    summary (dict):
        A dictionary holding per-column summaries (type inference, unique counts, precomputed histograms, etc.). The method may read column-level metadata from this dict to decide which columns to include and how to preprocess them.
        - Expected shape: mapping of column-name -> column-summary (structure depends on the rest of the codebase).

## Returns:
    Optional[Sized]:
        - As currently implemented the function never returns (it raises NotImplementedError).
        - In a completed implementation, the function is expected to return either:
            * A Sized object representing a pairwise association matrix (for example, a pandas.DataFrame symmetric matrix of float association values), or
            * None if the computation is skipped due to configuration (e.g., config.calculate is False) or because the input contains no categorical variables.
        - Edge-case return values to consider in an implementation:
            * None when not applicable or calculation disabled
            * An empty DataFrame (or equivalent zero-sized container) when there are no valid categorical column pairs
            * A square DataFrame with index and columns matching the included variables when associations are computed

## Raises:
    NotImplementedError:
        - Unconditionally raised by the current implementation. Calling this function will always result in this exception until the method is implemented.

## State Changes:
- Attributes READ:
    - None from self, because this function is declared as a static method (no self parameter). Any state read must come from the provided arguments (config, df, summary).
- Attributes WRITTEN:
    - None. The current implementation performs no mutations.

## Constraints:
- Preconditions:
    - The caller must provide:
        * config: an instance compatible with ydata_profiling.config.Settings
        * df: a Sized object containing the variables to analyze (ideally a pandas.DataFrame)
        * summary: a dict with per-column metadata (structure as used elsewhere in the pipeline)
    - If a concrete implementation expects pandas operations, df must support indexing by column names and pandas-like Series operations.
- Postconditions:
    - Current: the function always raises NotImplementedError; no state or return value is produced.
    - Implemented variant: upon successful completion, returns an association matrix or None as documented above; does not mutate external state or the passed-in df/summary.

## Side Effects:
    - Current implementation: none other than raising NotImplementedError.
    - Implemented variant (guidance): typically pure computation with no I/O or external service calls; may allocate memory proportional to the number of categorical variables squared when producing a full pairwise matrix.

## Suggested implementation (developer guidance; not present in the current code):
The following recipe describes a standard, practical way to implement Cramér's V pairwise association for categorical variables. Treat this section as guidance to produce a correct implementation; it is not executed by the current placeholder.

1. Input selection and preprocessing:
    - Determine which columns are categorical or should be treated as categorical (use summary metadata or infer by dtype and unique counts).
    - If needed, discretize continuous variables into a fixed number of bins (e.g., config.n_bins) before forming contingency tables.
    - Exclude columns with only one unique value.

2. Pairwise contingency and statistic:
    - For each unordered pair of included columns (A, B):
        a. Build the contingency table (observed counts) using pandas.crosstab or numpy.histogram2d-like approach.
        b. Compute the chi-squared statistic (chi2) from the contingency table:
            - chi2 = sum( (observed - expected)**2 / expected ) over cells, where expected = (row_sum * col_sum) / total
        c. Compute Cramér's V:
            - V = sqrt(chi2 / (n * (k - 1))) where:
                * n = total observations used (sum of contingency table)
                * k = min(number_of_rows, number_of_columns) of the contingency table
            - Optionally apply bias correction (e.g., Bergsma & Wicher correction) to reduce upward bias for small tables:
                * Use corrected chi2 and corrected k following standard formulas if needed.

3. Edge-case handling:
    - If total observations n == 0, set association to NaN or skip the pair.
    - If k == 1 (one row or one column), V is undefined; set value to NaN or 0 depending on project conventions.
    - If expected cell count is zero for some cells, avoid division-by-zero in the chi-squared formula (skip or treat expected as a small epsilon if appropriate).

4. Aggregation and return:
    - Assemble results into a symmetric matrix/dataframe with variable names as index and columns. Fill diagonal with 1.0 (variable perfectly associated with itself) or 0.0 depending on convention.
    - If computation is disabled via config (e.g., config.calculate is False), return None.

5. Performance considerations:
    - For high-cardinality categoricals, contingency tables can be large; consider limiting pairs by cardinality thresholds or sampling.
    - Vectorized pandas crosstab or grouped-count approaches are preferred over Python-level nested loops for speed.

6. Example return type:
    - A pandas.DataFrame named assoc_df where assoc_df.loc[col_i, col_j] is the Cramér's V value (float) and assoc_df is symmetric.

Note: When implementing, ensure unit tests cover degenerate inputs (empty df, single-column df, columns with NaNs only, extremely high cardinality) and configuration-driven skipping.

## `src.ydata_profiling.model.correlations.PhiK` · *class*

## Summary:
A Correlation subclass that defines the phi_k correlation computation entry point. The compute static multimethod is declared but not implemented; calling it raises NotImplementedError.

## Description:
This class exists to provide the canonical location and interface for a phi_k correlation computation within the correlations module. It declares the expected API (a static, multimethod-dispatched compute method) but contains no implementation in this source version.

Scenarios where this class is referenced:
- Callers that request phi_k correlation are expected to call PhiK.compute(config, df, summary). The file does not include callers or factories; any such orchestration lives elsewhere in the codebase.

Responsibility boundary:
- Provide the API surface (method name, parameter types, decorator usage) for phi_k correlation computations.
- Do not perform any computation in this version; the class intentionally signals that the implementation is absent.

## State:
- Attributes: None declared on the class. There is no __init__ defined here; the class is effectively stateless in this source form.
- __init__ parameters: None required or defined by this class.
- Invariants:
  - Because the class holds no instance state, there are no internal invariants to maintain within this class as written.

## Lifecycle:
- Creation:
  - Instantiation is optional and unnecessary for use because compute is a static method. No constructor arguments are required by this class.
- Usage:
  - Primary entry: PhiK.compute(config, df, summary)
  - The compute method is decorated with @multimethod and @staticmethod; callers invoke it directly on the class or instance, and multimethod dispatch will select an implementation if additional overloads are defined elsewhere.
  - In this code version, any call to compute results in NotImplementedError.
- Destruction:
  - No resources are allocated by the class; there are no cleanup steps.

## Method Map:
flowchart TD
    Caller[Caller prepares arguments] --> ComputeCall[PhiK.compute(config, df, summary)]
    ComputeCall --> Raises[Raises NotImplementedError]
    %% Note: Multimethod decorator allows additional overloads to be added separately.

## Method: compute
- Signature (exact): compute(config: Settings, df: Sized, summary: dict) -> Optional[Sized]
- Decorators: @staticmethod, @multimethod
- What it is: The defined API entry point for phi_k correlation computation.
- Current behavior: Immediately raises NotImplementedError (no computation implemented here).
- Return type in signature: Optional[Sized] (the implementation may return a Sized object or None when implemented; currently there is no return because the method raises).

## Raises:
- NotImplementedError: raised unconditionally by the current implementation of compute.

## Example:
- Current behavior (will raise NotImplementedError):
  - Prepare:
    - config = Settings()  # Settings class available in the codebase
    - df = ...             # any object satisfying Sized
    - summary = {}
  - Call:
    - try:
          result = PhiK.compute(config, df, summary)
      except NotImplementedError:
          # Expected for this source version: the phi_k compute method is not implemented here.
          result = None

## Notes for implementers (explicitly not part of this source):
- The class is the intended place to implement phi_k computation. This section only advises where an implementer would add behavior; it does not describe existing code behavior.
- Any concrete implementation must preserve the declared signature and decorator usage so that existing call sites and multimethod dispatching continue to work.

### `src.ydata_profiling.model.correlations.PhiK.compute` · *method*

## Summary:
Current implementation: placeholder that raises NotImplementedError. Intended purpose (proposal): compute Phi_k pairwise correlations for the given dataset and return a correlation matrix (or None) without mutating external state.

## Description:
Current, verifiable facts:
- This is declared as a static multimethod on the PhiK class and has the signature (config: Settings, df: Sized, summary: dict) -> Optional[Sized].
- The present implementation immediately raises NotImplementedError.

Implementation contract and guidance for future implementers (clearly labeled as recommendations):
- Purpose: perform Phi_k correlation computation for variables in df, producing a symmetric pairwise correlation matrix (preferably a pandas.DataFrame indexed and columned by variable names) consumable by the profiling pipeline.
- Placement rationale: Phi_k calculation is non-trivial (binning/contingency tables, specialized statistics) and belongs in a dedicated method to keep the correlation pipeline modular, configurable, and testable.

Known callers and lifecycle:
- Not verifiable from the current implementation. As guidance, the method is expected to be invoked by the profiling correlation step when Phi_k correlations are enabled in configuration.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: read-only configuration values controlling correlation computation (e.g., enable flag, binning options). The current implementation does not use it.

    df (Sized):
        - Type: Any object implementing Sized. Typical concrete type: pandas.DataFrame.
        - Role: the dataset to analyze. The current implementation does not inspect df.

    summary (dict):
        - Type: dict
        - Role: auxiliary per-variable summaries produced earlier in the profiling pipeline. May be empty; the current implementation does not use it.

## Returns:
    Optional[Sized]:
        - Current behavior: the function does not return — it raises NotImplementedError.
        - Recommended contract for implementers: return a Sized correlation object (ideally a pandas.DataFrame) or None when computation is intentionally skipped (for example, insufficient variables or disabled in config).

## Raises:
    NotImplementedError:
        - Exact condition: always raised by the current placeholder implementation.

    (Recommendations for implementers — listed as guidance, not current behavior)
    - pandas.errors.DataError or pandas.core.base.DataError: may be raised by implementations that coerce/validate pandas DataFrames and encounter irrecoverable input shapes or types.
    - ValueError: may be raised for invalid config values or invalid input shapes detected during validation.

## State Changes:
Attributes READ :
    - None from instance state (method is static). The method may read values from the supplied config, df, and summary (as inputs) in an implementation.

Attributes WRITTEN :
    - None. The current placeholder does not modify state. Implementations should avoid mutating df, summary, config, or global state.

## Constraints:
Preconditions (for a correct implementation):
    - config must be a valid Settings object if code reads config fields.
    - df must be a sized, tabular-like object; implementations that require pandas.DataFrame should coerce/validate and raise appropriate errors if coercion fails.
    - summary, if relied upon, should follow the profiling pipeline schema; implementations must handle missing fields robustly.

Postconditions (if implemented according to the recommended contract):
    - Returns a symmetric correlation matrix (Sized) with identical index and columns representing the variables used, or returns None for documented skip reasons.
    - Does not mutate df, summary, or config.

## Side Effects:
Current behavior:
    - Raises NotImplementedError; no I/O or external side effects.

Recommended constraint for implementations:
    - Avoid performing file I/O, network calls, or persistent external effects. Heavy CPU or memory usage is acceptable for computation but should be documented and controlled via config if needed.

## Minimal implementation checklist for developers:
1. Validate types: ensure config is Settings, df is coercible to pandas.DataFrame (or handle generic Sized), summary is a dict.
2. Identify candidate variables (optionally using summary) and return None if fewer than two variables are eligible.
3. Binning/preprocessing: bin continuous variables per config or sensible defaults; limit categorical cardinality as needed.
4. Compute Phi_k pairwise (use phik library if available or compute from contingency tables).
5. Assemble results into a symmetric pandas.DataFrame (variables as index/columns), set diagonal to self-correlation (typically 1.0), and return it.
6. Document and propagate deterministic exceptions for invalid inputs; do not silently swallow pandas exceptions.

This document separates what the code currently does (a verifiable placeholder) from a detailed, auditable implementation contract to aid correct reintegration.

## `src.ydata_profiling.model.correlations.warn_correlation` · *function*

## Summary:
Intended to emit a formatted warning about a failed correlation computation, but the current implementation is incomplete and raises a NameError because the warning message expression is undefined.

## Description:
This helper function is supposed to centralize issuing warnings when a correlation computation fails (for example, when computing Pearson, Spearman, Kendall, or other correlation measures between variables). In the provided source, the function calls warnings.warn with an incomplete expression (an undefined identifier named f), which will raise a NameError at runtime before any warning is emitted.

Known callers within the repository:
- No direct call sites were present in the provided snippet. Typically, correlation computation routines in this module would call this helper after catching exceptions during a correlation calculation.

Why this logic is extracted:
- Centralizing warning formatting ensures consistent user-facing messages across different correlation implementations.
- It isolates warning emission so callers only handle detection and decision logic (whether to warn and how to proceed) and delegate message construction to this function.

Intended responsibility (what implementers should provide):
- Construct a single human-readable message that includes the correlation method name and the error text.
- Emit the message using Python's warnings.warn() API.
- Be robust to None or non-string inputs by coercing to strings safely.

Suggested correct implementation (step-by-step instructions for reimplementation):
1. Validate/coerce inputs:
   - Ensure correlation_name and error are present or coerce them to strings via str().
   - If correlation_name is empty, use a fallback like "unknown correlation".
2. Build a concise message string that includes both fields, for example:
   - "Correlation '<correlation_name>' failed: <error>"
   - Ensure the message is a plain str (not bytes) and safe to stringify.
3. Call warnings.warn(message) to emit the warning. Optionally, choose a warning category such as UserWarning and provide a stacklevel (e.g., stacklevel=2) to point to the caller.
4. Do not reference undefined variables (the current code references an undefined identifier that causes NameError).

## Args:
    correlation_name (str):
        Short name of the correlation method (e.g., "pearson", "spearman", "cramers_v").
        - Required: expected to be non-empty or else a sensible fallback used.
    error (str):
        Error text or exception string describing why the correlation failed.
        - Required: should be safe to coerce to str().

Interdependencies:
    - Both arguments are combined to form the warning message. Neither is used independently by the current (buggy) implementation, because it references an undefined variable.

## Returns:
    None

Current implementation does not return any value. If executed as provided, it will not reach a normal return (see Raises).

## Raises:
    NameError:
        In the provided source, the function attempts to evaluate an undefined identifier named f when calling warnings.warn(f), causing a NameError and preventing normal warning emission.
    Exception propagation from str() calls:
        If coercing inputs to strings triggers an exception (for example, an object's __str__ raises), that exception will propagate.

## Constraints:
Preconditions:
    - The provided source currently assumes an identifier f is defined; because it is not, callers should not expect a warning to be emitted.
    - For a correct implementation, correlation_name and error must be convertible to strings.

Postconditions (for a corrected implementation):
    - A warning (UserWarning by default) has been emitted via warnings.warn with a message containing the correlation name and error.
    - No other global state is modified.

## Side Effects:
    - Current implementation: raises NameError (no warning emitted).
    - Corrected implementation: emits a warning via the warnings subsystem (which by default writes to stderr or follows the process's warnings filters).
    - No file, network, or persistent state changes are performed.

## Control Flow:
flowchart TD
    A[Call warn_correlation(correlation_name, error)] --> B{Is implementation the provided buggy version?}
    B -- Yes --> C[Attempt to evaluate 'f' in warnings.warn(f)]
    C --> D[NameError raised] --> E[Function aborts with exception]
    B -- No (correct implementation) --> F[Coerce correlation_name and error to str]
    F --> G[Format message: "Correlation '<name>' failed: <error>"]
    G --> H[Call warnings.warn(message)] --> I[Return None]

## Examples:
Example demonstrating the current (buggy) observable behavior:
- If called as: warn_correlation("pearson", "division by zero")
  - Outcome: NameError is raised due to an undefined identifier referenced in the warning call. No warning is emitted.

Example (how to implement and use correctly; provided as descriptive guidance, not as source code):
- Caller catches an exception when computing a correlation, then:
  - Build readable strings for the correlation method and the exception (e.g., use str(exception)).
  - Invoke the helper which should emit: Correlation 'pearson' failed: division by zero
  - In unit tests, capture warnings using warnings.catch_warnings(record=True) and assert that the recorded warning message contains both the method name and the error fragment.

Notes for maintainers:
- Fix the function by replacing the undefined expression with explicit message construction and a call to warnings.warn(message, UserWarning, stacklevel=2) or equivalent.
- Add unit tests that assert a proper warning is emitted rather than a NameError, and tests that the message contains correlation_name and a summary of the error.

## `src.ydata_profiling.model.correlations.calculate_correlation` · *function*

## Summary:
Dispatches a correlation/association request to the configured correlation implementation and returns the resulting pairwise association matrix (or None when no matrix is produced).

## Description:
This function is the dispatcher that maps a short correlation name (e.g., "pearson", "spearman") to the corresponding correlation implementation class and invokes its compute entrypoint with the provided inputs. It centralizes error handling for the call and normalizes empty/degenerate results to None.

Known callers and typical trigger contexts:
- The profiling pipeline's correlations/associations stage (the orchestration layer that builds the correlations section of a profile report).
- The higher-level "Auto" dispatcher when it explicitly requests a single correlation method for the whole dataset or for a subset of variable pairs.
- Any user-facing API or utility that requests a single named correlation matrix for a DataFrame after per-column summary metadata is available.
Typical trigger: called after the per-column summary has been produced and the system or user requests a specific correlation measure (or "auto") to compute pairwise associations.

Why this logic is a separate function:
- Encapsulates the mapping of short names to implementation classes.
- Centralizes the coarse-grained error handling for correlation computation (so callers don't duplicate try/except logic).
- Normalizes empty/degenerate results (len(correlation) <= 0) to None in a single place.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: declarative options that downstream correlation implementations may read (e.g., enabling/disabling techniques, thresholds).
        - Requirement: passed through to the implementation; callers should provide a Settings instance appropriate for the profiling run.
    df (Sized):
        - Type: any object implementing __len__; typically a pandas.DataFrame (rows = observations, columns = variables).
        - Role: the dataset to analyze; it is forwarded to the chosen correlation implementation which is responsible for coercion/validation.
    correlation_name (str):
        - Type: str
        - Allowed values (explicit mapping implemented in this function):
            - "auto"   -> Auto
            - "pearson"-> Pearson
            - "spearman"-> Spearman
            - "kendall"-> Kendall
            - "cramers"-> Cramers
            - "phi_k"  -> PhiK
        - Notes: supplied value must be one of the keys above. Passing any other string will raise KeyError (this function does not catch KeyError).
    summary (dict):
        - Type: dict
        - Role: profiling per-column metadata produced earlier in the pipeline (used by correlation implementations to decide which columns to analyze, skip constants, etc.).
        - Allowed to be empty; implementations should handle missing expected fields defensively.

Interdependencies:
- correlation_name selects which class's compute(config, df, summary) is invoked. The semantics of df and summary (what is expected) are defined by the chosen implementation (e.g., Pearson/Spearman expect numeric columns).

## Returns:
    Optional[Sized]
    - When successful:
        - Preferable concrete return: a square pairwise association matrix (pandas.DataFrame or numpy.ndarray) whose length/size > 0. If a matrix is returned, it must be sized such that len(correlation) > 0.
        - The returned object is the raw result from the chosen implementation (this function does not reformat it).
    - When no computation is performed or a recoverable error occurs:
        - None is returned in these scenarios:
            * The chosen implementation returned None.
            * The chosen implementation returned a Sized result whose length is 0 (the function converts empty results to None).
            * A recoverable exception was raised by the implementation and caught by this function; the function will call warn_correlation(...) and return None.
    - Edge cases:
        - If the implementation returns an object that implements __len__ but len(...) <= 0, it will be treated as None.
        - If an implementation raises an exception not caught by this function (e.g., KeyError for an unknown correlation_name, or any exception outside the caught tuple), that exception will propagate to the caller.

## Raises:
    - KeyError:
        - Condition: correlation_name not present in the internal mapping (i.e., not one of the explicit keys listed above). The function indexes correlation_measures[correlation_name] without guarding KeyError.
    - Any exception raised by the chosen implementation that is not in the handled tuple will propagate unchanged.
    - Note on handled exceptions:
        - The function catches and consumes the following exceptions raised from compute(...): ValueError, AssertionError, TypeError, DataError (pandas.core.base.DataError / pandas.errors.DataError), IndexError.
        - When such an exception is caught, the function does NOT re-raise it; instead it calls warn_correlation(correlation_name, str(e)) and proceeds, ultimately returning None.
    - Important: warn_correlation (the helper called on caught exceptions) has a known bug in the current codebase that may raise NameError instead of emitting a warning. Callers should be aware that calling calculate_correlation may surface that NameError indirectly until the helper is fixed.

## Constraints:
Preconditions:
    - correlation_name must be a string matching one of the supported keys in the mapping.
    - config should be a Settings-compatible object expected by downstream implementations.
    - df should be an analyzable sized container (preferably a pandas.DataFrame) appropriate for the selected correlation method.
    - summary should be the profiling summary mapping accessible to the correlation implementations.

Postconditions:
    - The function returns either:
        - A non-empty Sized correlation matrix produced by the invoked implementation; or
        - None, if no matrix is available or a handled error occurred.
    - No mutation is performed by this function on config, df, or summary (the actual implementations may operate on copies or views; callers should consult the concrete implementation documentation for those guarantees).

## Side Effects:
    - Calls warn_correlation(correlation_name, str(e)) when compute(...) raises a handled exception. Intended effect: emit a human-readable warning via Python warnings. Current caveat: the warn_correlation helper in the present codebase contains a bug that can raise NameError instead of emitting a warning.
    - No I/O, network calls, global state mutations, or file writes are performed by this function itself.

## Control Flow:
flowchart TD
    Start[Start: calculate_correlation(config, df, correlation_name, summary)]
    Start --> Map[Lookup correlation_measures mapping]
    Map --> ValidName{correlation_name in mapping?}
    ValidName -- No --> KeyError[Raise KeyError -> exit]
    ValidName -- Yes --> CallImpl[Call implementation.compute(config, df, summary)]
    CallImpl --> Success{compute returned without raising}
    Success -- Yes --> Assign[corr = returned object]
    Assign --> EmptyCheck{corr is not None and len(corr) <= 0?}
    EmptyCheck -- Yes --> SetNone[Set corr = None]
    EmptyCheck -- No --> Keep[Keep corr as result]
    Keep --> Return[Return corr]
    Success -- No (exception) --> Catch[Catch ValueError/AssertionError/TypeError/DataError/IndexError]
    Catch --> Warn[Call warn_correlation(correlation_name, str(e))]
    Warn --> ReturnNone[Return None]

## Examples (usage patterns and error handling):
- Typical successful usage (conceptual):
    - Prepare: config (Settings), df (pandas.DataFrame), summary (per-column metadata).
    - Call: calculate_correlation(config, df, "pearson", summary)
    - Interpret:
        * If result is a pandas.DataFrame: inspect cells for pairwise Pearson coefficients.
        * If result is None: no correlation matrix could be produced (e.g., fewer than two analyzable columns, or a handled error occurred).

- Handling an invalid correlation name:
    - If a caller may receive user input for correlation_name, guard the call:
      * Verify correlation_name is one of ["auto","pearson","spearman","kendall","cramers","phi_k"] before calling to avoid KeyError.
      * Alternatively, call and catch KeyError around calculate_correlation to provide a user-friendly message.

- Handling compute-time exceptions:
    - The function already catches recoverable exceptions listed above and calls warn_correlation; in production code, you may also want to capture warnings or monitor logs to surface those recoverable failures to users.
    - Be aware of the current warn_correlation bug: the caught exception may cause a NameError when warn_correlation is invoked; until warn_correlation is fixed, callers may want to wrap calculate_correlation in a try/except catching NameError if they must avoid the process abort.

## Implementation notes for re-implementers:
- The core responsibilities are:
    1. Map correlation_name to an implementation class.
    2. Invoke implementation.compute(config, df, summary) inside a protective try/except.
    3. Convert empty-sized results (len(...) <= 0) to None.
    4. Call a central warning helper when recoverable exceptions occur.
- Preserve the exact mapping keys used by callers and tests. If adding new correlation methods, extend the mapping here and ensure the new class exposes compute(config, df, summary).
- Keep the try/except tuple in sync with project-wide error-handling policy; the current implementation handles ValueError, AssertionError, TypeError, DataError, and IndexError as recoverable and warns rather than re-raising.

## `src.ydata_profiling.model.correlations.perform_check_correlation` · *function*

## Summary:
Returns a mapping from each column label to the list of other column labels whose absolute correlation with it meets or exceeds the given threshold (self-correlations are excluded).

## Description:
This function inspects a correlation matrix and reports, for every column that has at least one sufficiently strong correlation, which other columns meet the threshold.

Known callers:
- No call sites were available in the provided context. Typical usage is inside correlation-checking or feature-selection stages of a profiling pipeline where highly correlated variables must be identified for further processing (e.g., reporting, dropping, or aggregating features).

Why this is a separate function:
- Encapsulates the logic that converts a numeric correlation matrix into a compact, human-usable adjacency mapping of "correlated columns".
- Keeps thresholding, diagonal exclusion, and mapping construction in one unit so callers can reuse a standard, well-documented behavior without reimplementing the mask and iteration logic.

## Args:
    correlation_matrix (pandas.DataFrame):
        A 2-D correlation matrix whose columns are the labels to be compared. Expected to behave like a square DataFrame (index and columns correspond to the same labels). The DataFrame's .values attribute must be a 2-D numeric array (e.g., dtype float).
    threshold (float):
        Threshold on the absolute value of correlation to consider two variables "correlated".
        - Typical/expected range: 0.0 <= threshold <= 1.0 (correlation coefficients are normally in [-1, 1]).
        - Behavior for other values:
            * threshold < 0: abs(values) >= threshold will be true for all finite correlations, effectively treating all non-self pairs as "correlated".
            * threshold > 1: will typically yield an empty result because abs(correlation) <= 1 for standard correlation matrices.
        - Interdependencies: threshold is compared with the absolute values in the matrix; negative/positive sign of original correlations is ignored.

## Returns:
    dict[str, list[str]]:
        Mapping where each key is a column label from the input DataFrame and the corresponding value is a list of column labels that have |correlation| >= threshold with that key, excluding the key itself.
        - Only columns that have at least one other column meeting the threshold appear as keys in the dictionary.
        - Order of values: values follow the order of columns in correlation_matrix.columns.
        - If no pairs meet the threshold, an empty dictionary is returned.

## Raises:
    - The function does not explicitly raise exceptions.
    - It will propagate errors raised by attribute access or indexing on the provided objects. For example:
        * If correlation_matrix lacks .columns or .values attributes (i.e., is not a suitable DataFrame-like object), AttributeError or similar will be raised by attribute access.
        * If correlation_matrix.values has a shape incompatible with correlation_matrix.columns (non-square or mismatched dimensions), indexing bool_index[i] may raise IndexError.
    - No custom exceptions are raised by the implementation.

## Constraints:
    Preconditions:
        - correlation_matrix must be a 2-D, square, numeric matrix-like object represented as a pandas DataFrame (index/columns expected to refer to the same labels).
        - correlation_matrix.columns must be an ordered sequence of hashable labels (these labels are used verbatim in the result).
        - threshold must be a numeric value (float or convertible to float).
    Postconditions:
        - Returned dictionary keys are a subset of correlation_matrix.columns.
        - For every mapping key 'A' and each listed 'B' in its list, abs(correlation_matrix.loc[A, B]) >= threshold (or the corresponding matrix cell that aligns with A/B if index/column alignment differs).
        - Self-correlations are always excluded (no column will list itself), because the diagonal entries are explicitly ignored.

## Side Effects:
    - None: the function performs pure computation and returns a new dictionary. It does not write to files, mutate the input DataFrame, print to stdout, or call external services.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> GetCols{Read columns from correlation_matrix}
    GetCols --> BuildMask[Compute bool_index = abs(values) >= threshold]
    BuildMask --> ClearDiag[Set diagonal entries of mask to False]
    ClearDiag --> Iterate[For each column index i and label col]
    Iterate --> CheckAny{any(bool_index[i])?}
    CheckAny -- Yes --> AddEntry[Add mapping: col -> labels where mask True]
    CheckAny -- No --> Skip[Skip column]
    AddEntry --> Iterate
    Skip --> Iterate
    Iterate --> End([Return dictionary])

## Examples (described in prose):
    Example 1 — typical case:
        - Given a symmetric 3x3 correlation DataFrame with columns ['a', 'b', 'c']:
            * correlations: a-b = 0.9, a-c = 0.2, b-c = -0.85, diagonals = 1.0
        - Calling the function with threshold = 0.8 will:
            * exclude diagonals
            * find a->b (0.9), b->a (0.9), and b->c (|-0.85| = 0.85)
            * return: {'a': ['b'], 'b': ['a', 'c']}
        - Note: 'c' is absent as a key because it has no other correlations |r| >= 0.8 besides the ones already captured under 'b'.

    Example 2 — threshold outside [0,1]:
        - threshold < 0 (e.g., -0.5): since abs(correlation) >= negative thresholds is always true for finite values, the function will mark every non-self pair as correlated (assuming a square numeric matrix).
        - threshold > 1 (e.g., 1.1): no abs(correlation) will meet the threshold, so the result will be an empty dictionary.

    Example 3 — malformed input:
        - If a non-DataFrame object without .values/.columns is passed, the call will fail by raising AttributeError or a similar propagated exception.
        - If a non-square numeric array is passed by accident (mismatched rows vs columns), indexing into the boolean mask during iteration can raise IndexError.

Notes:
    - If the input matrix is symmetric (as correlation matrices typically are), the returned adjacency is symmetric in content: B appears in A's list iff A appears in B's list. If the matrix is non-symmetric, the mapping may be asymmetric.
    - The function compares absolute correlations; it does not distinguish positive from negative relationships.

## `src.ydata_profiling.model.correlations.get_active_correlations` · *function*

## Summary:
Return the keys from the provided Settings.correlations mapping for which the corresponding entry's calculate attribute is truthy.

## Description:
This function inspects the correlations configuration on a Settings object and returns the identifiers (mapping keys) of correlation entries that are enabled for computation (i.e., whose calculate attribute evaluates to a truthy value). It centralizes the simple filtering rule so callers do not duplicate the logic for deciding which correlation methods to execute.

Known callers within the codebase:
    - No direct callers are referenced in this module's source. Call-sites must be located elsewhere in the codebase; this function is a small utility intended to be used by higher-level profiling or report-generation code that needs to know which correlation calculations to run.

Reason for extraction:
    - Encapsulates the responsibility of selecting enabled correlations from configuration. Keeping this logic in one place reduces duplication and simplifies future changes to the enablement rule (for example, if the flag name or semantics change).

## Args:
    config (Settings): A Settings object (from ydata_profiling.config) that:
        - exposes a 'correlations' attribute, and
        - config.correlations behaves like a mapping (supports .keys() and subscription).
    Notes:
        - The function does not enforce that correlation keys are strings; it returns keys as provided by the mapping.
        - For each key k in config.correlations, the corresponding value config.correlations[k] must have an attribute named 'calculate'. The attribute's truthiness (not strict boolean equality) determines inclusion.

## Returns:
    list[str]: A list containing each key from config.correlations.keys() for which config.correlations[key].calculate is truthy.
    - If no entries have a truthy calculate attribute, returns an empty list [].
    - If config.correlations is empty, returns [].
    - The concrete type of list elements matches the mapping's key types (conventionally strings in this codebase).

## Raises:
    - AttributeError: If the provided config object has no attribute 'correlations', or if a correlation entry object lacks the 'calculate' attribute, attribute access will raise AttributeError.
    - TypeError: If config.correlations exists but is not a mapping-like object with .keys() (e.g., None or an incompatible type), calling .keys() may raise TypeError.
    - KeyError: There is a small window where a mapping mutated between iterating .keys() and indexing may cause a KeyError when accessing config.correlations[k]. This function does not guard against concurrent mutations.
    - Any other exceptions raised by the mapping's methods or by property access on the correlation entry objects will propagate.

## Constraints:
    Preconditions:
        - config is not None.
        - config has a 'correlations' attribute.
        - config.correlations is a mapping-like object with a .keys() method and supports item access via [].
        - For every key k returned by config.correlations.keys(), config.correlations[k] has a 'calculate' attribute.
    Postconditions:
        - The returned list contains exactly those keys k from config.correlations.keys() for which config.correlations[k].calculate is truthy at the time of access.
        - The function does not modify config or config.correlations.

## Side Effects:
    - None. The function performs only read operations on the provided objects and returns a new list. It performs no I/O, does not mutate global state, and does not call external services.

## Control Flow:
flowchart TD
    Start([Start]) --> HasCorrelations{config has 'correlations' attribute?}
    HasCorrelations -- No --> AttrError([AttributeError raised by attribute access])
    HasCorrelations -- Yes --> GetKeys[Call config.correlations.keys()]
    GetKeys --> ForEachKey[Iterate over each key k]
    ForEachKey --> CheckCalculate{Is config.correlations[k].calculate truthy?}
    CheckCalculate -- Yes --> Append[Append k to results]
    CheckCalculate -- No --> Skip[Do not append]
    Append --> NextKey[Continue iteration]
    Skip --> NextKey
    NextKey --> ForEachKey
    ForEachKey --> Return([Return results list])

## Examples:
- Normal use:
  Given config where
    config.correlations = {
      "pearson": obj1,  # obj1.calculate == True
      "spearman": obj2, # obj2.calculate == False
      "kendall": obj3   # obj3.calculate == 1 (truthy)
    }
  the function returns ["pearson", "kendall"].

- Empty mapping:
    If config.correlations == {}, the function returns [].

- Error case:
    If config has no 'correlations' attribute, calling this function will raise AttributeError; callers should validate the Settings object shape if that cannot be guaranteed.

