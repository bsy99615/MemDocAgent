# `correlations_pandas.py`

## `src.ydata_profiling.model.pandas.correlations_pandas.pandas_spearman_compute` · *function*

## Summary:
Computes the Spearman rank-order correlation matrix for the DataFrame's applicable columns and returns it as a pandas DataFrame.

## Description:
Delegates to pandas.DataFrame.corr(method="spearman") to produce a Spearman correlation matrix. The computation is equivalent to ranking each column (average ranks for ties) and then computing the Pearson correlation on those ranks.

Known callers:
- No direct callers were found in the inspected repository. Typically invoked by the profiling pipeline during the correlations computation stage when Spearman correlations are requested by configuration.

Why this logic is extracted:
- Centralizes the pandas-specific call to obtain Spearman correlations so the profiling module can maintain a consistent API across different correlation methods.
- Allows future extension (preprocessing, NA handling policies, dtype casting, or configuration-driven options) without changing callers.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: Profiling configuration object.
        - Note: Not used by the current implementation; accepted to keep a uniform function signature across correlation implementations.
    df (pd.DataFrame):
        - Type: pandas.DataFrame
        - Role: Input table whose columns will be compared pairwise.
        - Requirements & behavior:
            * Should be a pandas DataFrame. If an object without a corr method is passed, an AttributeError will be raised by Python when attempting to call df.corr.
            * Non-numeric columns are ignored by pandas.corr; only columns that pandas recognizes as numeric (or convertible for the operation) appear in the result.
            * NaN handling: pandas performs pairwise deletion (skipna=True) by default — for each pair of columns, only rows where both values are non-null are used to compute that pairwise correlation.
    summary (dict):
        - Type: dict
        - Role: Metadata/summary about df.
        - Note: Not used by the current implementation; present for API consistency.

## Returns:
    Optional[pd.DataFrame]:
        - The DataFrame returned by df.corr(method="spearman"): a square matrix indexed and columned by the (numeric) column names from df, containing Spearman correlation coefficients in the interval [-1.0, 1.0].
        - If df has zero columns suitable for correlation, the returned DataFrame will be empty (shape (0, 0)).
        - Although the signature is Optional[pd.DataFrame], the current implementation always returns the DataFrame produced by pandas and does not explicitly return None.

## Raises:
    - AttributeError: If df does not implement a corr method (e.g., wrong type passed).
    - Any exceptions raised internally by pandas.DataFrame.corr (propagated as-is). Examples include exceptions due to unexpected dtypes or internal pandas errors.

## Constraints:
Preconditions:
    - The caller should provide a pandas.DataFrame for df.
    - config and summary may be provided but are not required for correct execution.

Postconditions:
    - The returned DataFrame is a symmetric square correlation matrix for the columns used.
    - The input DataFrame df is not modified by this function.

## Side Effects:
    - None. No I/O, network, global state mutation, or modification of the input DataFrame occurs.

## Control Flow:
flowchart TD
    Start --> "Receive inputs (config, df, summary)"
    "Receive inputs (config, df, summary)" --> "Call df.corr(method='spearman')"
    "Call df.corr(method='spearman')" --> "Rank each column (ties => average rank)"
    "Rank each column (ties => average rank)" --> "Compute Pearson correlation on ranks (pairwise)"
    "Compute Pearson correlation on ranks (pairwise)" --> "Return resulting DataFrame"
    "Call df.corr(method='spearman')" -->|if df lacks corr or invalid type| "Exception propagated"
    "Return resulting DataFrame" --> End
    "Exception propagated" --> End

## Examples:
Example 1 — typical usage
    # Given a pandas DataFrame `df` with numeric columns a, b, c:
    corr_matrix = pandas_spearman_compute(config, df, summary)
    # corr_matrix is a pandas.DataFrame with Spearman correlation coefficients between a, b, c

Example 2 — NaN / pairwise behavior
    # For df that contains NaN values:
    #   df = pd.DataFrame({"x": [1.0, 2.0, None], "y": [3.0, None, 1.0], "z": ["a","b","c"]})
    # - Column "z" is non-numeric and will be excluded.
    # - The correlation between x and y is computed using the single row where both are non-null:
    #     pairwise_rows = rows where x and y both non-null
    #   corr_matrix = pandas_spearman_compute(config, df, summary)
    #   corr_matrix will be indexed by ["x","y"] and contain the Spearman coefficient computed on the pairwise non-null rows.
    #
    # Note: Because pairwise deletion is used, different column pairs may be computed over different subsets of rows.

Example 3 — defensive usage
    try:
        corr_matrix = pandas_spearman_compute(config, df, summary)
    except AttributeError:
        # df did not provide a corr method — ensure df is a pandas.DataFrame
        raise
    except Exception:
        # unexpected pandas error
        raise

## `src.ydata_profiling.model.pandas.correlations_pandas.pandas_pearson_compute` · *function*

## Summary:
Compute pairwise Pearson correlation coefficients for the numeric columns of a given pandas DataFrame and return them as a DataFrame.

## Description:
This function delegates to pandas' built-in correlation computation to produce a symmetric DataFrame containing Pearson correlation coefficients between pairs of numeric columns.

Known callers:
- No direct callers were identified in the provided source snapshot. The function is intended to be used by higher-level correlation orchestration logic that selects the correlation method (e.g., a dispatcher that supports Pearson, Spearman, Kendall, PhiK, Cramers, etc.) and normalizes the API for computing different correlation matrices.

Why this is a separate function:
- Provides a consistent function signature across different correlation methods so the dispatcher can call each method the same way.
- Isolates the Pearson-specific call (method="pearson") to one place, simplifying testing, mocking, and future changes (e.g., adding pre/post processing around pandas' corr).
- Keeps the correlation computation implementation compact and focused (single responsibility).

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: Configuration object passed by the caller for consistency with other correlation functions.
        - Note: This parameter is not used by the implementation but is kept for API consistency across correlation functions.
    df (pandas.DataFrame):
        - Type: pandas.DataFrame
        - Purpose: The table of data for which pairwise correlations are computed.
        - Requirements: Must implement the pandas DataFrame API, specifically the corr(method="pearson") call (i.e., typically a pandas.DataFrame).
    summary (dict):
        - Type: dict
        - Purpose: Optional metadata or summary information that higher-level callers may pass.
        - Note: Not used by this implementation; present for API uniformity.

## Returns:
    pandas.DataFrame:
        - A symmetric DataFrame of dtype float containing Pearson correlation coefficients between each pair of numeric columns in df.
        - Index and columns correspond to the numeric columns present in df (non-numeric columns are ignored by pandas.corr).
        - Diagonal entries are 1.0 for columns with at least one valid pairwise observation.
        - If no numeric columns or too few pairwise observations exist, pandas may produce NaN entries or an empty DataFrame depending on pandas' behavior.
    Note: The function signature types the return as Optional[pandas.DataFrame], but the current implementation always returns the DataFrame result of df.corr(...) or raises an exception; it does not explicitly return None.

## Raises:
    - Any exception raised by pandas.DataFrame.corr is propagated. In typical cases:
        - AttributeError: If df does not have a corr method (i.e., df is not a pandas-like DataFrame).
        - TypeError / ValueError: If pandas' corr detects invalid input shapes or types for the Pearson computation.
    The function does not catch or translate exceptions; callers should handle pandas-raised exceptions as needed.

## Constraints:
Preconditions:
    - df should be a pandas.DataFrame-like object that supports corr(method="pearson").
    - Caller should be prepared to handle exceptions raised by pandas if df is invalid or contains incompatible data.

Postconditions:
    - On successful return, a pandas.DataFrame of pairwise Pearson correlations is produced (no in-place modification of df).
    - The original df is not mutated by this call.

## Side Effects:
    - None intrinsic: the implementation makes no I/O calls, does not mutate global state, does not write files, and does not perform network access.
    - External side effects are limited to whatever pandas.corr may do internally (which is normally none visible to the caller).

## Control Flow:
flowchart TD
    Start --> Check_df_has_corr
    Check_df_has_corr{df has corr method?}
    Check_df_has_corr -- Yes --> Call_corr
    Check_df_has_corr -- No --> Raise_AttributeError
    Call_corr --> Return_result
    Raise_AttributeError --> End
    Return_result --> End

## Examples:
- Typical usage (conceptual):
    - A higher-level correlation dispatcher prepares a Settings instance and a DataFrame, then calls this function when Pearson correlations are requested. The function returns the pandas correlation matrix which the caller can then format, filter by magnitude, or embed in a report.
- Error handling:
    - Callers should catch exceptions to handle cases where the input is not a DataFrame or when pandas cannot compute correlations due to unsuitable data:
        - Validate that df is a pandas.DataFrame before calling, or wrap the call in a try/except block to log and recover from AttributeError/TypeError raised by pandas.

## `src.ydata_profiling.model.pandas.correlations_pandas.pandas_kendall_compute` · *function*

## Summary:
Compute the pairwise Kendall Tau correlation matrix for the provided pandas DataFrame and return it as a pandas DataFrame.

## Description:
This thin wrapper delegates the computation to pandas' built-in DataFrame.corr(method="kendall") and returns its result. The function accepts three parameters for API consistency within the profiling pipeline (config and summary are not used by this implementation).

Known callers:
- Higher-level correlation-dispatching code in the profiling pipeline (not in this file) that selects Kendall correlation as the desired method and invokes this function to obtain the correlation matrix.
- This function is intended to be used whenever a Kendall Tau correlation matrix for the dataset is requested as part of a profiling or exploratory-analysis step.

Responsibility boundary:
- Responsibility: produce a Kendall Tau correlation matrix for the input DataFrame using pandas' implementation.
- Boundary: it does not validate or transform the DataFrame beyond what pandas.DataFrame.corr performs; it does not modify input data, update any external state, or use config/summary values.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: Configuration placeholder for consistency with other correlation compute functions.
        - Notes: Not used by this implementation; callers may pass pipeline settings but they have no effect here.
    df (pandas.DataFrame):
        - Type: pandas.DataFrame
        - Purpose: Input table whose columns will be used to compute pairwise Kendall Tau correlations.
        - Constraints: Should be a well-formed DataFrame. Non-numeric columns are ignored by pandas.corr; only columns that can be coerced to numeric (or are numeric) will appear in the result.
    summary (dict):
        - Type: dict
        - Purpose: Summary metadata placeholder for symmetry with other compute functions.
        - Notes: Not used by this implementation.

Interdependencies:
- There are no interdependencies between the parameters; config and summary are ignored and may be None or any mapping-like object that the caller provides for API uniformity.

## Returns:
    pandas.DataFrame (or Optional[pandas.DataFrame] per function signature):
    - A DataFrame whose rows and columns are the input DataFrame's columns that pandas identified as valid for correlation.
    - Each cell (i, j) contains the Kendall Tau correlation coefficient between column i and column j.
    - Typical contents:
        * A symmetric matrix with 1.0 on the diagonal (correlation of a column with itself).
        * NaN for pairs where the correlation cannot be computed (e.g., constant columns, insufficient overlapping non-NA observations).
    - Notes on typing: Although the function signature uses Optional[pd.DataFrame], the pandas call returns a DataFrame on success. None is not returned by this implementation under normal operation; exceptions are propagated instead.

## Raises:
    - Propagates exceptions raised by pandas.DataFrame.corr:
        * AttributeError or TypeError if the provided df does not support .corr (for example, if df is not a pandas.DataFrame).
        * Any pandas-raised exceptions (ValueError, TypeError, etc.) stemming from invalid data types or internal pandas errors.
    - The function does not catch or convert exceptions — callers should handle exceptions arising from pandas.

## Constraints:
Preconditions:
    - The caller should pass a pandas.DataFrame for the df parameter.
    - If meaningful correlation is required, the DataFrame should contain at least one numeric/coercible-to-numeric column; otherwise the returned DataFrame may be empty.
Postconditions:
    - On success, returns a pandas.DataFrame representing the Kendall Tau pairwise correlation matrix; the input DataFrame is not mutated.
    - No side effects or external state changes are performed by the function.

## Side Effects:
    - None: there are no file, network, or stdout operations, and no mutation of global state.
    - The function simply invokes pandas' correlation routine and returns its result.

## Control Flow:
flowchart TD
    Start --> CallCorr["Call df.corr(method='kendall')"]
    CallCorr --> ReturnResult["Return pandas.DataFrame (correlation matrix)"]
    CallCorr --> Error["Exception propagated to caller"]

## Examples:
- Typical usage scenario (described, not relying on imports shown here):
    1. A profiling pipeline determines the user requested "kendall" correlations.
    2. The pipeline calls pandas_kendall_compute(config, df, summary).
    3. On success, the caller receives a DataFrame where each cell is the Kendall Tau correlation coefficient between the corresponding columns.
    4. The caller should handle exceptions from pandas (for example, by catching TypeError/AttributeError if an invalid object is passed as df).

- Example (conceptual):
    - Given a DataFrame with numeric columns "a", "b", "c", calling this function returns a 3x3 DataFrame with Kendall Tau coefficients for each pair (a,b), (a,c), (b,c), etc. If "b" is constant, correlations involving "b" will be NaN.

## `src.ydata_profiling.model.pandas.correlations_pandas._cramers_corrected_stat` · *function*

## Summary:
Compute the bias-corrected Cramér's V association measure from a contingency (confusion) table, returning a numeric association strength (close to 0 means weak association, close to 1 means strong or degenerate association).

## Description:
This helper converts a contingency table into a chi-squared statistic using scipy.stats.chi2_contingency and applies the bias-correction formula commonly used for Cramér's V in small or unbalanced samples. It performs the correction described in the literature: subtracting the small-sample bias from phi^2 and adjusting the denominator using corrected row/column counts.

Typical usage context:
- Intended as an internal helper for code that has already built a contingency table (pandas DataFrame) for two categorical variables and needs a numeric association metric.
- The caller is expected to pass the contingency table and decide whether to enable the chi-squared continuity correction via the correction flag; this function forwards the correction flag to scipy.stats.chi2_contingency.

Why this function is separated:
- Encapsulates the numeric/statistical transformation from chi-squared to corrected Cramér's V in a single, testable unit.
- Keeps higher-level correlation code responsible for data preparation (crosstabs) and orchestration, while this helper focuses on the statistical formula and degenerate/edge-case handling.

## Args:
    confusion_matrix (pd.DataFrame):
        - A pandas DataFrame representing the contingency (cross-tabulation) of observed counts.
        - Must support .empty, .shape and .sum() operations.
        - Expected to contain non-negative counts/frequencies. The function reads total count as n = confusion_matrix.sum().sum().
        - Special-case: if confusion_matrix.empty is True, the function returns 0 immediately (the literal integer 0 as returned by the code).

    correction (bool):
        - Boolean flag forwarded to scipy.stats.chi2_contingency as the continuity correction parameter.
        - True applies scipy's correction in the chi-squared computation; False does not.
        - No other interdependency with confusion_matrix beyond being used when computing chi2.

## Returns:
    float or int:
        - For non-empty, well-formed inputs the function returns a float representing Cramér's V (bias-corrected if correction is requested).
            * Typical returned range: 0.0 ≤ value ≤ 1.0 for non-degenerate inputs.
        - Special/edge-case returns:
            * If confusion_matrix.empty is True: the function returns the literal integer 0 (as implemented).
            * If the corrected denominator collapses to zero (see Control Flow), the function returns 1.0 (float) to indicate the degenerate mathematical condition handled by the implementation.
        - Implementation note: the function is annotated to return float, but it may return the integer 0 when the input table is empty.

## Raises:
    - Exceptions raised by scipy.stats.chi2_contingency:
        * If scipy detects invalid input (e.g., negative counts, non-finite values, or other input validation failures), it may raise ValueError or other exceptions. Those exceptions are not caught within this function.
    - The function suppresses numpy runtime warnings for divide/invalid within its computation block, but does not convert numpy warnings into exceptions.

## Constraints:
    Preconditions:
        - confusion_matrix should represent counts with total n = confusion_matrix.sum().sum(); meaningful results require n > 0.
        - The formula includes divisions by (n - 1) — when n == 1 these denominators become zero; the implementation uses numpy error suppression and then handles the resulting corrected-denominator check (rkcorr == 0.0) by returning 1.0.
        - The shape-derived k (number of columns) is computed as:
            k = confusion_matrix.shape[1] if len(confusion_matrix.shape) > 1 else 1
          so a 1-D-like object (len(shape) <= 1) is treated as having 1 column.
        - correction must be a boolean.

    Postconditions:
        - No global state is modified.
        - The numeric result is returned; for normal inputs it is finite and in [0,1]. Degenerate inputs may produce 1.0 or numeric edge results governed by scipy/numpy behavior.

## Side Effects:
    - No file, network, or stdout/stderr I/O.
    - No modification of global variables.
    - Calls out to scipy.stats.chi2_contingency and numpy functions for internal computation.

## Control Flow:
flowchart TD
    Start --> IsEmpty{confusion_matrix.empty?}
    IsEmpty -- Yes --> Return0[Return 0 (literal int)]
    IsEmpty -- No --> ComputeChi2[chi2 = stats.chi2_contingency(conf_matrix, correction)[0]]
    ComputeChi2 --> ComputeN[n = confusion_matrix.sum().sum()]
    ComputeN --> ComputePhi2[phi2 = chi2 / n]
    ComputePhi2 --> ReadDims[r = confusion_matrix.shape[0]]
    ReadDims --> ComputeK{k = confusion_matrix.shape[1] if len(confusion_matrix.shape) > 1 else 1}
    ComputeK --> WithErrState[with np.errstate(divide="ignore", invalid="ignore")]
    WithErrState --> Phi2Corr[phi2corr = max(0.0, phi2 - ((k - 1.0) * (r - 1.0)) / (n - 1.0))]
    Phi2Corr --> Rcorr[rcorr = r - ((r - 1.0) ** 2.0) / (n - 1.0)]
    Rcorr --> Kcorr[kcorr = k - ((k - 1.0) ** 2.0) / (n - 1.0)]
    Kcorr --> RkCorr[rkcorr = min((kcorr - 1.0), (rcorr - 1.0))]
    RkCorr --> RkZero{rkcorr == 0.0?}
    RkZero -- Yes --> ReturnOne[Return 1.0]
    RkZero -- No --> ComputeCorr[corr = sqrt(phi2corr / rkcorr)]
    ComputeCorr --> ReturnCorr[Return corr]
    ReturnOne --> End
    ReturnCorr --> End
    Return0 --> End

## Examples (usage guidance, descriptive):
- Typical (conceptual) flow:
    1. Build a contingency table for two categorical columns, for example via pandas.crosstab.
    2. Call this helper with the contingency table and correction=True/False depending on whether the chi-squared continuity correction is desired.
    3. Interpret the returned number as Cramér's V; treat 0 (returned as 0 when the table is empty) as "no data", and consider special-handling for a returned 1.0 which indicates a degenerate denominator condition rather than necessarily a practically meaningful "perfect" association.

- Edge-case guidance:
    * If total sample size n == 0, expect scipy.stats.chi2_contingency to raise or produce invalid chi2; handle or validate upstream.
    * If n == 1 (so n - 1 == 0), the correction arithmetic involves division by zero; this function suppresses runtime warnings and maps the degenerate denominator to 1.0. Callers that need a different convention (e.g., returning NaN instead) should handle that mapping after calling this helper.

## `src.ydata_profiling.model.pandas.correlations_pandas._pairwise_spearman` · *function*

*No documentation generated.*

## `src.ydata_profiling.model.pandas.correlations_pandas._pairwise_cramers` · *function*

## Summary:
Build a contingency table from two pandas Series and return the bias-corrected Cramér's V association score computed by the shared helper (continuity correction enabled).

## Description:
This thin wrapper constructs a contingency (cross-tabulation) table for two categorical variables using pandas.crosstab and then delegates the numeric association computation to the internal helper that implements the bias-corrected Cramér's V formula. It always forwards correction=True to the helper, enabling the chi-squared continuity correction for the underlying chi2 computation.

Known callers and context:
- No direct in-repository callers were discovered in the available snapshot for this component. Conceptually, it is intended for use by pairwise correlation matrix builders or profiling routines that compute categorical-categorical associations (i.e., higher-level code that iterates over column pairs and needs a single numeric association score per pair).

Why this logic is extracted:
- Keeps data-preparation (contingency table construction) separate from the numerical/statistical transformation and edge-case handling implemented by the shared helper.
- Centralizes the bias-correction behavior and degenerate-case handling in a single helper, while this wrapper normalizes how two Series are converted into the helper's expected input.

## Args:
    col_1 (pd.Series):
        - First categorical series (pandas.Series). Must be a 1-D sequence of observation values.
    col_2 (pd.Series):
        - Second categorical series (pandas.Series). Must be a 1-D sequence of observation values.
    Notes on inputs:
        - The two Series represent paired observations: position i in col_1 corresponds to position i in col_2. The wrapper does not perform explicit validation of length or alignment beyond calling pandas.crosstab; any alignment/compatibility concerns are delegated to pandas.crosstab's behavior.

## Returns:
    float or int:
        - The result from the internal bias-corrected Cramér's V helper.
        - Typical return: a float in [0.0, 1.0] for non-degenerate inputs.
        - Edge-case returns (produced by the helper and forwarded by this wrapper):
            * literal int 0 if the contingency table is empty (the helper returns 0 in this case).
            * float 1.0 when the helper detects a degenerate corrected-denominator condition (for example, resulting from extremely small sample size arithmetic).
        - The wrapper does not introduce new sentinel values beyond those produced by the helper.

## Raises:
    - Any exception raised by pandas.crosstab during contingency-table construction will propagate (no interception in this wrapper).
    - Any exception raised by the internal helper (including exceptions originating from scipy.stats.chi2_contingency) will propagate.
    - The wrapper does not catch, translate, or wrap exceptions from these calls.

## Constraints:
    Preconditions:
        - col_1 and col_2 should be pandas.Series-like 1-D sequences of observations.
        - For meaningful results, the combined observations should produce a contingency table with total count > 0; otherwise the helper may return 0 or raise (behavior of the helper applies).
        - The function always invokes the helper with correction=True (continuity correction requested).

    Postconditions:
        - No mutation of inputs or global state.
        - Either a numeric association value is returned or an exception is raised.

## Side Effects:
    - No file, network, or direct stdout/stderr I/O.
    - In-memory computation via pandas.crosstab and the internal helper; these calls may consume memory/CPU and may raise exceptions.

## Control Flow:
flowchart TD
    Start --> BuildCrosstab[Call pandas.crosstab(col_1, col_2)]
    BuildCrosstab --> CrosstabException{pandas.crosstab raises exception?}
    CrosstabException -- Yes --> PropagateCrosstabErr[Propagate exception to caller]
    CrosstabException -- No --> CallHelper[Call _cramers_corrected_stat(crosstab, correction=True)]
    CallHelper --> HelperException{helper raises exception?}
    HelperException -- Yes --> PropagateHelperErr[Propagate exception to caller]
    HelperException -- No --> ReturnValue[Return numeric Cramér's V (float) or int 0/1.0 per helper]
    ReturnValue --> End
    PropagateCrosstabErr --> End
    PropagateHelperErr --> End

## Examples (usage guidance and error-handling patterns; conceptual):
    - Typical usage:
        * When building a correlation matrix between categorical columns, call this wrapper for each column pair to obtain a single numeric association score to populate the matrix cell.

    - Error handling when computing many pairs:
        * If constructing a full pairwise matrix, wrap calls in try/except and map exceptions to NaN or another sentinel so processing can continue:
            - On exception from pandas.crosstab or the helper, log the error and store NaN for that cell.

    - Interpreting returned values:
        * 0 (literal integer) indicates an empty contingency table; handle as "no data" if desired.
        * 1.0 may indicate a degenerate arithmetic condition in the bias-correction (e.g., tiny sample size) — inspect raw counts before interpreting as a "perfect" association.

## `src.ydata_profiling.model.pandas.correlations_pandas.pandas_cramers_compute` · *function*

## Summary:
Compute a symmetric matrix of pairwise Cramér's V associations for categorical/boolean columns (subject to a distinct-value cap), returning a pandas DataFrame of float association scores or None when not enough categorical columns are present.

## Description:
This function selects columns from the provided summary that are flagged as categorical or boolean and whose number of distinct values lies strictly greater than 1 and no greater than the configured threshold. For every unique unordered pair among those selected columns it builds a contingency table (pandas.crosstab) from the DataFrame and computes a bias-corrected Cramér's V via the internal helper _cramers_corrected_stat (called with correction=True). The result is placed in a symmetric pandas DataFrame where the diagonal entries are 1.0 and missing/uncomputable pairwise associations are written as NaN.

Known callers / typical usage context:
- Invoked by higher-level correlation/feature-assessment code in the profiling pipeline when categorical-to-categorical association strengths are requested. Typical pipeline stage: after generating the dataset summary and before formatting the correlations for reporting or visualization.
- It is intended to be part of the correlations computation step of the ydata_profiling analysis, not a stand-alone statistical utility.

Why this logic is extracted:
- Separates column selection and orchestration of pairwise association computation from the numeric/statistical logic in _cramers_corrected_stat. This keeps responsibilities clear: this function manages filtering, data extraction (crosstabs) and matrix assembly; the helper computes the numeric association from a contingency table.

## Args:
    config (Settings):
        - The profiling Settings object.
        - Required attribute: categorical_maximum_correlation_distinct (int).
        - Purpose: upper bound (inclusive) on n_distinct for a column to be considered for Cramér's V computation.
    df (pandas.DataFrame):
        - The full data table containing the columns referenced by summary.
        - Columns used for pairwise crosstabs must exist in df; missing columns will raise a KeyError when accessed.
    summary (dict):
        - Mapping of column name -> summary-info dict.
        - For a column to be considered it must satisfy:
            * summary[col]["type"] is either "Categorical" or "Boolean"
            * 1 < summary[col]["n_distinct"] <= config.categorical_maximum_correlation_distinct
        - The function only reads the "type" and "n_distinct" keys for selection; other keys in the summary dict are ignored.

Interdependencies and notes:
- The list of columns considered is created from a set comprehension and then cast to a list. Because a set is unordered, the ordering of rows/columns in the returned DataFrame is not guaranteed to be stable across runs; callers that rely on a particular ordering must reorder the DataFrame after receiving it.
- The function uses the internal helper _cramers_corrected_stat(confusion_matrix, correction=True) to compute each pairwise metric.

## Returns:
    Optional[pandas.DataFrame]:
    - If fewer than two categorical columns meet the selection criteria, returns None.
    - Otherwise returns a pandas DataFrame (square, dtype float) with:
        * index and columns equal to the selected categorical column names (order determined by the set → list conversion).
        * diagonal entries equal to 1.0.
        * off-diagonal entries equal to the Cramér's V value computed for the corresponding column pair.
        * For pairs where pandas.crosstab yields an empty contingency table, the corresponding cell is set to NaN.
    - All computed association values are returned as floats. Diagonal entries are 1.0 (float). Empty-pair cases are NaN. The DataFrame is symmetric by construction.

## Raises:
    - KeyError:
        * If a column selected from summary does not exist in df, df[column] access will raise KeyError.
    - Any exception propagated from pandas.crosstab:
        * Unlikely for standard inputs but will propagate errors if pandas fails (e.g., invalid index types).
    - Any exception propagated from _cramers_corrected_stat:
        * That helper forwards to scipy.stats.chi2_contingency, so ValueError or other errors raised by scipy for invalid contingency tables (negative counts, non-finite values, zero total count, etc.) will propagate.
    - TypeError or KeyError:
        * If the summary entries do not contain the expected keys ("type" and "n_distinct") or they are of unexpected types, a TypeError/KeyError may be raised during evaluation of the selection condition.

## Constraints:
Preconditions:
    - config.categorical_maximum_correlation_distinct must be an integer-like upper bound.
    - summary must be a mapping whose values are mappings with at least "type" and "n_distinct".
    - df must contain the columns named in summary that meet the selection criteria.
    - Meaningful results require that the contingency tables have non-negative counts and a sensible total sample size; very small or degenerate tables may lead to edge behavior handled by the helper.

Postconditions:
    - No mutation of df or summary takes place.
    - The returned DataFrame (when not None) is symmetric, has diagonal 1.0, and contains computed Cramér's V floats or NaN; no global state is changed.

## Side Effects:
    - No I/O (no file, network or stdout/stderr).
    - No mutation of global variables.
    - Calls pandas.crosstab and the internal numerical helper _cramers_corrected_stat which in turn calls scipy.stats.chi2_contingency and numpy functions.

## Control Flow:
flowchart TD
    Start --> ComputeThreshold[Read threshold = config.categorical_maximum_correlation_distinct]
    ComputeThreshold --> SelectCols[Select columns from summary where type in {Categorical, Boolean} and 1 < n_distinct <= threshold]
    SelectCols --> CheckCount{len(categoricals) <= 1?}
    CheckCount -- Yes --> ReturnNone[Return None]
    CheckCount -- No --> InitMatrix[Create zero matrix of shape (m, m) and fill diagonal with 1.0]
    InitMatrix --> BuildDF[Wrap as pandas.DataFrame(index=cols, columns=cols)]
    BuildDF --> ForEachPair[For each unordered pair (name1, name2)]
    ForEachPair --> Crosstab[confusion_matrix = pandas.crosstab(df[name1], df[name2])]
    Crosstab --> IsEmpty{confusion_matrix.empty?}
    IsEmpty -- Yes --> SetNaN[Set correlation_matrix.loc[name2, name1] = NaN]
    IsEmpty -- No --> ComputeCramers[Set correlation_matrix.loc[name2, name1] = _cramers_corrected_stat(confusion_matrix, correction=True)]
    ComputeCramers --> MirrorValue[Set correlation_matrix.loc[name1, name2] = correlation_matrix.loc[name2, name1]]
    SetNaN --> MirrorValue
    MirrorValue --> NextPair{More pairs?}
    NextPair -- Yes --> ForEachPair
    NextPair -- No --> ReturnMatrix[Return correlation_matrix]
    ReturnMatrix --> End

## Examples (usage guidance, end-to-end description):
- Basic successful flow:
    1. Prepare a summary mapping with per-column metadata that includes for each column:
        - "type": either "Categorical" or "Boolean" to be eligible
        - "n_distinct": an integer count of distinct values
    2. Ensure config.categorical_maximum_correlation_distinct is set to an appropriate integer upper bound (e.g., 50).
    3. Call pandas_cramers_compute(config, df, summary).
    4. If the function returns None, fewer than two categorical columns met the criteria and no pairwise Cramér's V matrix was produced.
    5. If a DataFrame is returned, interpret each off-diagonal cell as the (bias-corrected) Cramér's V for that column pair; treat NaN as "no contingency data" for that pair.

- Handling errors and edge cases:
    * Missing column in df: validate that every column name present in summary and selected by the filter exists in df before calling; otherwise be prepared to catch KeyError.
    * Very small or degenerate contingency tables: the internal helper may raise exceptions coming from scipy or return edge indicator values (e.g., 1.0 for certain degenerate denominators). If your workflow requires different handling (for example returning NaN for n <= 1), perform an upstream check on total counts before calling this function or post-process the returned matrix to map special values to your convention.

Notes:
- The ordering of rows/columns in the returned DataFrame is derived from a conversion from a set to a list and is therefore not stable; callers that require deterministic ordering should explicitly sort the DataFrame (for example by index.sort_values or reindex with a deterministic ordering) after receiving it.
- This function deliberately uses correction=True when computing each pairwise Cramér's V; if you need uncorrected chi-squared behavior you must call a lower-level helper (or adapt the helper) since this function does not expose the correction flag.

## `src.ydata_profiling.model.pandas.correlations_pandas.pandas_phik_compute` · *function*

## Summary:
Computes a pairwise Phi_k (phik) correlation matrix for an input DataFrame using a selection of columns derived from a precomputed summary; returns a pandas DataFrame with phik correlations or None when there are not enough selectable columns.

## Description:
This function selects candidate columns from the provided DataFrame according to the summary metadata and configuration limits, then delegates the actual phik correlation computation to phik.phik_matrix while suppressing warnings. It encapsulates the logic for which columns should be considered numeric/interval vs. categorical and enforces the maximum distinct-values threshold for categorical columns.

Known callers within the provided source: None identified in the supplied context. Typical usage: invoked from the correlations computation stage of a dataset profiling pipeline when pairwise dependency measures are being assembled — i.e., after a per-column summary has been computed and when the profiling configuration is available.

Responsibility boundary: selection and ordering of columns to pass into phik_matrix, and returning the phik correlation matrix (or None if insufficient columns). It does not preprocess values (e.g., imputation or discretization) beyond selecting columns, nor does it persist results or mutate external state.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings (or an object with compatible attributes)
        - Required attributes used:
            * categorical_maximum_correlation_distinct (int): upper bound (inclusive) on number of distinct values allowed for categorical columns to be considered.
        - No default. Passing an object lacking the attribute will raise AttributeError.

    df (pd.DataFrame):
        - Type: pandas.DataFrame
        - Must contain columns whose names match the keys of summary (see Preconditions).
        - The function will index df columns and slice df[selected_cols] to compute correlations.

    summary (dict):
        - Type: dict mapping column name (str) -> metadata dict
        - Required keys in each metadata dict used by this function:
            * "type": string. Expected values observed in code: "Numeric", "Unsupported", or other categorical type strings.
            * "n_distinct": integer count of distinct values for that column.
        - Behavior:
            * Columns with value["type"] == "Numeric" and value["n_distinct"] > 1 are treated as interval (intcols).
            * Columns with value["type"] != "Unsupported" and 1 < value["n_distinct"] <= config.categorical_maximum_correlation_distinct are eligible categorical columns.
        - Interdependencies:
            * The function assumes summary keys correspond to df.columns; mismatch may raise KeyError later.

## Returns:
    Optional[pd.DataFrame]:
    - If at most one column is selected for correlation (<= 1), returns None.
    - Otherwise returns the DataFrame produced by phik.phik_matrix(df[selected_cols], interval_cols=list(intcols)):
        * A square pandas.DataFrame indexed and columned by the selected column names containing phi_k correlation values for each pair.
        * The exact contents and shape are determined by the phik_matrix implementation; typically a len(selected_cols) x len(selected_cols) correlation matrix with diagonal entries representing self-correlation.

## Raises:
    - KeyError:
        * If selected column names (derived from summary keys) are not present in df.columns, sorting selected_cols by df column order uses df_cols_dict[i] and will raise KeyError.
    - AttributeError:
        * If config lacks categorical_maximum_correlation_distinct (accessed as config.categorical_maximum_correlation_distinct).
    - ImportError / ModuleNotFoundError:
        * If the phik library is not installed or cannot be imported, the inner import or phik_matrix call will raise ImportError. This function does not catch ImportError.
    - Any exception raised by phik_matrix:
        * Errors coming from phik_matrix (e.g., due to unexpected input types, empty frames, or internal phik errors) will propagate.

## Constraints:
Preconditions:
    - summary must be a mapping containing an entry for each DataFrame column intended to be considered; keys in summary that will be used must appear in df.columns.
    - Each metadata dict in summary must contain "type" and "n_distinct" with appropriate types ("type": str, "n_distinct": int or numeric).
    - config must expose categorical_maximum_correlation_distinct as an integer value.
Postconditions:
    - If the function returns None, no correlation computation was performed because <= 1 columns were eligible.
    - If the function returns a DataFrame, it is the phik correlation matrix for the selected columns and was computed with interval_cols set to the numeric columns identified in summary.

## Side Effects:
    - No filesystem, network, or stdout/stderr side effects are performed by this function.
    - It temporarily adjusts the warnings filter (inside a warnings.catch_warnings context) to ignore warnings generated during import or phik_matrix computation; the original warning state is restored on exit.
    - No global variables or external state are mutated.

## Control Flow:
flowchart TD
    A[Start] --> B[Build df_cols_dict from df.columns]
    B --> C[Compute intcols: type == "Numeric" and n_distinct > 1]
    C --> D[Compute selcols: type != "Unsupported" and 1 < n_distinct <= categorical_maximum_correlation_distinct]
    D --> E[selcols = selcols ∪ intcols]
    E --> F[selected_cols = sort selcols by df column order]
    F --> G{len(selected_cols) <= 1?}
    G -- Yes --> H[Return None]
    G -- No --> I[Suppress warnings; import phik_matrix]
    I --> J[Call phik_matrix(df[selected_cols], interval_cols=list(intcols))]
    J --> K[Return correlation DataFrame]
    K --> L[End]

## Examples:
Example 1 — Typical usage (happy path):
    - Precondition: You have run column summarization and have `summary` where keys match df columns, and config.categorical_maximum_correlation_distinct is set appropriately.
    - Invocation:
        result = pandas_phik_compute(config, df, summary)
    - Follow-up:
        * If result is None: not enough eligible columns (<= 1) to compute correlations.
        * If result is a DataFrame: use it as the pairwise phik correlation matrix (e.g., to populate profiling report output).

Example 2 — Error handling:
    - Protect against phik not installed:
        try:
            correlation = pandas_phik_compute(config, df, summary)
        except ImportError:
            # Handle missing dependency: inform user or skip phik-based correlations
            correlation = None
    - Validate preconditions to avoid KeyError:
        if not set(summary.keys()).issuperset(set(df.columns)):
            # Build or update summary so keys match df.columns before calling

Notes:
    - The function intentionally suppresses warnings generated during phik import/computation but does not catch or suppress exceptions; callers should handle ImportError and other exceptions as appropriate.
    - The selection logic depends entirely on the "type" and "n_distinct" metadata fields in summary; adjust the summary generation stage if different behavior is required.

## `src.ydata_profiling.model.pandas.correlations_pandas.pandas_auto_compute` · *function*

## Summary:
Builds a symmetric pairwise association matrix for selected numeric and categorical columns by discretizing numeric data when needed and applying the appropriate pairwise scorer for each column pair; returns the matrix as a pandas.DataFrame or None when fewer than two eligible columns exist.

## Description:
This function implements the "auto" correlation step for profiling: it selects eligible columns from the provided summary (based on type and distinct-count thresholds), discretizes numeric columns into uniform bins for categorical-style comparisons, and computes pairwise association scores for every unordered pair of selected columns. It centralizes selection, discretization, and per-pair scoring so higher-level profiling code can obtain a ready-to-use association matrix without handling per-pair logic.

Known callers and context:
- No direct in-repository callers were discovered in the available snapshot. Conceptually, this function is invoked by profiling/report-generation flows that include an "auto" correlation block in the dataset summary.

Why this logic is extracted:
- Avoids duplicating column-selection and discretization logic across code that builds correlation matrices.
- Keeps scoring helpers small and focused (statistical computation, contingency construction) while this function handles orchestration and policy.

## Args:
    config (Settings)
        - Required configuration fields used:
            * config.categorical_maximum_correlation_distinct (int): maximum distinct values to include a categorical column for correlation.
            * config.correlations["auto"].n_bins (int): number of uniform bins used for discretizing numeric columns when comparing them categorically.
        - If these fields are missing or invalid, attribute access or downstream operations will raise exceptions.

    df (pd.DataFrame)
        - The DataFrame containing columns referenced by summary.
        - Column names in summary must exist in df; otherwise accessing df[column] or df_discretized[column] raises KeyError.

    summary (dict)
        - Mapping from column name (str) to metadata dict with at least:
            * "type": expected values include "Numeric", "TimeSeries", "Categorical", "Boolean".
            * "n_distinct": integer count of distinct values.
        - Selection rules applied by this function:
            * numerical_columns: type in {"Numeric","TimeSeries"} and n_distinct > 1
            * categorical_columns: type in {"Categorical","Boolean"} and 1 < n_distinct <= config.categorical_maximum_correlation_distinct

## Returns:
    Optional[pd.DataFrame]
        - Returns None when fewer than two total selected columns (numerical + categorical).
        - Otherwise returns a square, symmetric pandas.DataFrame indexed and columned by the tested column names (order: numerical_columns followed by categorical_columns).
        - Diagonal entries are 1. Off-diagonal entries are scalar scores returned by the chosen pairwise scorer for that pair.
        - Score semantics depend on the underlying scorer:
            * Cramér's V (categorical scorer) typically in [0.0, 1.0]; note that the categorical helper may return literal int 0 for empty contingency tables or float 1.0 for degenerate corrected-denominator cases — these are forwarded unchanged.
            * Rank/linear scorers (e.g., Spearman) typically in [-1.0, 1.0].
        - The function does not normalize or harmonize scores across different scorer types; downstream consumers must handle mixed scales if needed.

## Raises:
    - KeyError: if a selected column is missing from df (accessing df[column] or df_discretized[column]).
    - Any exception thrown by Discretizer.discretize_dataframe will propagate.
    - Any exception thrown by the chosen pairwise scorer (_pairwise_cramers, _pairwise_spearman, etc.) will propagate. The function does not catch or translate these exceptions.

## Constraints:
    Preconditions:
        - config provides the required parameters.
        - summary maps existing df column names to metadata dicts containing "type" and "n_distinct".
        - For meaningful results, input columns should have aligned observations (rows represent paired observations).

    Postconditions:
        - If a DataFrame is returned:
            * It is square and symmetric with ones on the diagonal.
            * Off-diagonal values are the raw outputs from pairwise scorers.

## Side Effects:
    - No file or network I/O.
    - Memory and CPU consumption proportional to DataFrame size and number of tested pairs; discretization copies data (Discretizer.discretize_dataframe makes a copy).
    - No global-state mutation.

## Control Flow:
flowchart TD
    Start --> ReadThreshold[Read threshold from config.categorical_maximum_correlation_distinct]
    ReadThreshold --> SelectNumeric[Select numerical_columns: type in {Numeric,TimeSeries} and n_distinct>1]
    SelectNumeric --> SelectCategorical[Select categorical_columns: type in {Categorical,Boolean} and 1 < n_distinct <= threshold]
    SelectCategorical --> CheckCount{len(numerical_columns + categorical_columns) <= 1?}
    CheckCount -- Yes --> ReturnNone[Return None]
    CheckCount -- No --> Discretize[Call Discretizer(UNIFORM,n_bins=config.correlations["auto"].n_bins).discretize_dataframe(df) => df_discretized]
    Discretize --> InitMatrix[Create correlation_matrix filled with ones indexed/columned by columns_tested]
    InitMatrix --> LoopPairs[For each unordered pair (col_1,col_2) in combinations(columns_tested,2)]
    LoopPairs --> ChooseMethod[Choose scorer per pair]
    ChooseMethod --> MethodLogic{Code expression used in source}
    MethodLogic --> SpearmanIf[Evaluate: (col_1_name) and (col_2_name not in categorical_columns) -> select _pairwise_spearman]
    MethodLogic --> ElseCramers[Else -> select _pairwise_cramers]
    ElseCramers --> PrepareSeries[For each column: if column in numerical_columns and chosen method is _pairwise_cramers, use df_discretized[column], else use df[column]]
    SpearmanIf --> PrepareSeries
    PrepareSeries --> CallMethod[Call method(series1, series2)]
    CallMethod --> AssignScore[Assign returned scalar symmetrically into correlation_matrix]
    AssignScore --> ContinueLoop{more pairs?}
    ContinueLoop -- Yes --> LoopPairs
    ContinueLoop -- No --> ReturnMatrix[Return correlation_matrix]
    ReturnMatrix --> End

Important alignment with categorical scorer behavior:
    - When _pairwise_cramers is selected by the above logic, pandas_auto_compute passes the two pandas.Series objects (either the original categorical series from df or the discretized numeric series from df_discretized) directly to _pairwise_cramers.
    - Per the categorical scorer's documented behavior, _pairwise_cramers:
        * Builds a contingency table using pandas.crosstab(col_1, col_2).
        * Delegates to a shared bias-corrected Cramér's V helper, always forwarding correction=True (i.e., continuity correction enabled).
        * Returns the bias-corrected Cramér's V value (typically float in [0.0, 1.0]) or specific sentinel values from the helper (e.g., literal int 0 for an empty contingency table or float 1.0 for degenerate arithmetic cases).
    - pandas_auto_compute does not alter, interpret, or normalize the values returned by _pairwise_cramers; these results are stored verbatim into the correlation matrix. Any exceptions raised by pandas.crosstab or the helper propagate to the caller.

Notes on method-selection subtlety:
    - The likely intended logic is "use Spearman when both columns are numeric, otherwise use Cramér's V when at least one column is categorical." However, the source code expression is written as: if col_1_name and col_2_name not in categorical_columns. Due to operator precedence, this evaluates as (col_1_name) and (col_2_name not in categorical_columns) — which effectively checks truthiness of col_1_name (non-empty string -> True) and whether col_2_name is not in categorical_columns. As a result, the code may select _pairwise_spearman whenever col_2 is non-categorical regardless of col_1's type. Reproduce this exact expression if you want behavior identical to the source; correct the expression to explicitly test both names for not-in-membership if you intend the "both non-categorical" semantics.

## Examples:
    - Conceptual example:
        * df: columns "age" (numeric), "income" (numeric), "city" (categorical).
        * summary: "age" and "income" -> type "Numeric", n_distinct>1; "city" -> type "Categorical", n_distinct within threshold.
        * config: categorical_maximum_correlation_distinct >= n_distinct("city"), config.correlations["auto"].n_bins = 5.
        * pandas_auto_compute builds columns_tested = ["age","income","city"], discretizes numeric columns into 5 uniform bins (used when comparing to categorical columns), and computes pairwise scores:
            - "age" vs "income": selected scorer (per source expression) likely _pairwise_spearman (numeric vs numeric); result typically in [-1,1].
            - "age" vs "city": if _pairwise_cramers is selected, _pairwise_cramers will build a contingency table via pandas.crosstab and return the bias-corrected Cramér's V (correction=True). Sentinel values such as int 0 (empty table) or float 1.0 (degenerate-case) are possible and forwarded unchanged.
            - The result is a 3x3 symmetric DataFrame with ones on the diagonal and the above scores in off-diagonal cells.

    - Error-tolerant usage patterns:
        * Validate that summary keys exist in df before calling to avoid KeyError.
        * If you need per-pair robustness (keep other pairs when one pair computation fails), implement your own pairwise loop with try/except around calls to the scorer and map exceptions to NaN.

## Implementation hints for re-implementation:
    - Reconstruct the column selection exactly as specified.
    - Use Discretizer(DiscretizationType.UNIFORM, n_bins=...) and call discretize_dataframe(df) to get df_discretized; Discretizer returns a copy and preserves column order.
    - Initialize the correlation DataFrame as numpy.ones((n,n)) with index and columns equal to columns_tested.
    - Iterate over itertools.combinations(columns_tested, 2), evaluate the method-selection expression verbatim if you must reproduce the original code's behavior (taking care about operator precedence), select the series sources (df vs df_discretized) as implemented, call the scorer, and assign the returned scalar symmetrically into the matrix.
    - Preserve exception propagation semantics unless you intentionally add error handling.

