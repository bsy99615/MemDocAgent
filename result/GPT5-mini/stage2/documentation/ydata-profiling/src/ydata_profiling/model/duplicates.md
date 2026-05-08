# `duplicates.py`

## `src.ydata_profiling.model.duplicates.get_duplicates` · *function*

## Summary:
Current implementation: placeholder that always raises NotImplementedError.
Recommended usage: implement duplicate-row detection on a tabular object and return a summary dict plus an optional subset of duplicate rows.

## Current implementation (observed from source)
- Behavior:
    - The function signature is:
        get_duplicates(config: Settings, df: T, supported_columns: Sequence) -> Tuple[Dict[str, Any], Optional[T]]
    - The function body raises NotImplementedError() unconditionally.
- Raises:
    - NotImplementedError: always raised by the present source.

## Description (purpose and responsibilities)
- Purpose:
    - Centralize duplicate-row detection logic for the profiling pipeline: determine which rows are duplicates (optionally considering only a subset of columns), produce a stable summary usable by reporting components, and optionally return the duplicate rows themselves.
- Why separate function:
    - Consolidates validation, selection of columns, duplicate-detection strategy, summary construction, and optional sampling/return of duplicate rows in one place so downstream code (profile generation, report sections) can rely on a stable contract.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings (opaque to this file).
        - Current code: config is accepted but not inspected (no observed attribute access).
        - Recommended use: consult to control options such as whether to return the duplicates DataFrame and max number of sample rows to return.
    df (T)
        - Type: generic table-like object (TypeVar T). In practice, a pandas.DataFrame is expected.
        - Required capabilities (for a correct implementation):
            * Column selection by label (df[columns] or df.loc[:, columns]).
            * Row-wise duplicate detection like pandas.DataFrame.duplicated or equivalent.
            * Boolean indexing / subsetting to extract rows.
    supported_columns (Sequence)
        - Type: sequence of column identifiers (typically strings).
        - Observed: accepted but not validated by source.
        - Recommended semantics:
            * If empty or None: consider all columns.
            * Items should be column labels present in df; if labels are missing, raise ValueError.

## Returns:
- Observed (from signature):
    - A tuple (summary: Dict[str, Any], duplicates: Optional[T]).
- Recommended concrete contract:
    - summary (dict): a plain dict with stable keys that callers can rely on. Minimum recommended keys:
        * "n_duplicates" (int): count of duplicate rows (excluding the first occurrence of each unique row group).
        * "n_unique" (int): count of unique row patterns considering selected columns.
        * "duplicate_fraction" (float): n_duplicates / total_rows (0.0 when total_rows == 0).
        * "sample_rows" (int): number of rows included in the returned duplicates object (0 if duplicates is None).
    - duplicates (Optional[T]):
        * None when no duplicates exist or when config dictates not to return rows.
        * Otherwise, a table-like object (same concrete type as df, e.g., pandas.DataFrame) containing only the rows identified as duplicate occurrences (recommended: exclude the first occurrence in each duplicate group).
        * Preserve original index and the relative order of rows.

## Raises:
- Observed:
    - NotImplementedError: raised unconditionally by current implementation.
- When implemented (recommended):
    - TypeError: if df does not support required table-like operations.
    - ValueError: if supported_columns references columns not present in df.
    - Underlying exceptions from df operations (KeyError, IndexError) may propagate; consider wrapping them with clearer messages.

## Constraints
- Preconditions:
    - df must be a non-null tabular object that supports column selection and boolean/indexed subsetting.
    - supported_columns, if provided, must be interpretable as df column labels.
    - config must be provided (function accepts it), but current source does not require specific attributes.
- Postconditions (recommended if implemented):
    - The returned summary is a plain dictionary matching the structure above.
    - The returned duplicates (if not None) is a subset view/copy of df that contains only duplicate rows and does not modify the original df.

## Side Effects:
- Observed: none (function raises NotImplementedError before any side effects).
- Recommended design: pure function — no file I/O, networking, global state mutation, or modification of the input df.

## Suggested implementation control flow (for reimplementation)
- This flow is a recommended design and is not present in source code.

flowchart TD
    Start([Start])
    Start --> ValidateInputs{Validate inputs}
    ValidateInputs -->|df is None| RaiseTypeError[Raise TypeError]
    ValidateInputs -->|supported_columns invalid| RaiseValueError[Raise ValueError]
    ValidateInputs -->|empty df| EmptyReturn[Return summary zeros + None]
    ValidateInputs --> SelectColumns[Select columns to consider (supported_columns or all)]
    SelectColumns --> ComputeMask[Compute duplicated mask (row-wise, keep='first')]
    ComputeMask --> AnyDuplicates{Any duplicates found?}
    AnyDuplicates -->|No| NoDuplicates[Return summary with n_duplicates=0 + None]
    AnyDuplicates -->|Yes| BuildDuplicatesDF[Extract duplicate rows from df]
    BuildDuplicatesDF --> PossiblySample[Optionally sample/truncate rows per config]
    PossiblySample --> ComputeSummary[Assemble summary dict]
    ComputeSummary --> ReturnOK[Return (summary_dict, duplicates_df)]
    ReturnOK --> End([End])

## Examples (usage patterns)
- Handling the current placeholder:
    try:
        summary, duplicates = get_duplicates(config, df, supported_columns)
    except NotImplementedError:
        # Function is not implemented in this version
        fallback_behavior()

- Example of recommended call pattern (pseudocode for a developer implementing/using it):
    summary, duplicates = get_duplicates(config, df, ["colA", "colB"])
    if summary["n_duplicates"] > 0 and duplicates is not None:
        # include duplicates in report
        report.add_section("Duplicates", duplicates.head(10))
    else:
        # no duplicates detected
        pass

Notes for implementers:
- Respect the signature and return types exactly as declared.
- Do not assume specific attributes exist on Settings in the existing codebase; read and validate config attributes before use.
- Preserve input df immutability from the caller's perspective: return views or copies rather than modifying df in-place.
- Document any additional keys added to the summary dict, keeping the minimum recommended keys stable for downstream consumers.

