# `dataframe_pandas.py`

## `src.ydata_profiling.model.pandas.dataframe_pandas.pandas_check_dataframe` · *function*

## Summary:
Performs a minimal runtime validation: if the provided object is not a pandas DataFrame, emits a warning and returns None.

## Description:
This utility inspects the provided value and uses the Python warnings system to signal when the input is not a pandas DataFrame. It does not modify the input or raise an exception under normal operation.

Known callers within the provided code context:
    - No direct callers are visible in the supplied file fragment. The function is intended as a small, reusable validation step that other DataFrame-preprocessing or profiling routines may call before performing DataFrame-specific operations.

Responsibility boundary:
    - Enforces a lightweight runtime type check and warning emission only. It deliberately avoids raising errors or performing any conversion/validation beyond an isinstance check.

Important note about type annotation in the source:
    - The function signature annotates the parameter with pd.DataFrame. In the file-level imports supplied alongside this function, pandas is imported as "import pandas" (not aliased to pd). If the module does not define the name pd at function-definition time and Python is evaluating annotations eagerly (pre-PEP 563 or without postponed evaluation enabled), this mismatch will raise a NameError during module import. If postponed annotation evaluation (from __future__ import annotations) or Python 3.10+ postponed evaluation semantics are used, the annotation will not be evaluated at definition time and no NameError will occur at import.

## Args:
    df (pd.DataFrame):
        - The object expected to be an instance of pandas.DataFrame.
        - The type annotation in the function signature is pd.DataFrame (relies on the name pd being defined in the module namespace at annotation-evaluation time unless annotations are postponed).
        - No other constraints are enforced (e.g., empty vs non-empty DataFrame is not checked).

## Returns:
    None
    - The function returns None implicitly in all cases.
    - The only observable effect when the input is not a DataFrame is that a warning is emitted; otherwise there is no output.

## Raises:
    - No exceptions are raised by the function body itself.
    - Potential NameError at import/module-load time: If the module defines the function with an evaluated annotation using the undefined name pd (i.e., pandas not aliased as pd and annotations evaluated eagerly), a NameError will be raised when the function is defined.
    - Indirect exceptions: Unusual user-defined objects with atypical type machinery could cause isinstance to raise, but that would be a property of the provided object, not of this function's logic.

## Constraints:
    Preconditions:
        - The caller must pass an object to the df parameter. There is no requirement on df beyond being any Python object; the function will check its type.
        - The module should ensure consistent usage of the pandas alias (pd) in annotations or use postponed annotation evaluation to avoid import-time NameError.

    Postconditions:
        - The input object is unmodified.
        - If the input was not a pandas DataFrame, a warning with the exact message "df is not of type pandas.DataFrame" has been emitted (category: UserWarning by default).

## Side Effects:
    - Emits a warning via warnings.warn when the type check fails. The message emitted is exactly: "df is not of type pandas.DataFrame".
    - No file, network, or stdout I/O is performed by this function.
    - No mutation of global state or the df object occurs.

## Control Flow:
flowchart TD
    Start --> Check{isinstance(df, pd.DataFrame)?}
    Check -- True --> Return[return None (no action)]
    Check -- False --> Warn[warnings.warn("df is not of type pandas.DataFrame")]
    Warn --> Return

## Examples (prose only):
    - Correct usage with pandas DataFrame:
        Provide a pandas.DataFrame instance as df. The function performs the isinstance check, emits no warning, and returns None. Typical call site: early in a data-profiling pipeline immediately before DataFrame-specific preprocessing.

    - Non-DataFrame input:
        Provide a list, dict, numpy.ndarray, or other non-DataFrame object. The function calls warnings.warn with the message "df is not of type pandas.DataFrame" (UserWarning) and returns None. No exception is raised by this function.

    - Import-time annotation caution:
        If the module that defines this function imports pandas as "import pandas" (no alias to pd) and Python evaluates annotations eagerly, the function definition will raise NameError because pd is undefined. To avoid this, either import pandas as pd in the module or enable postponed annotation evaluation (for example, via from __future__ import annotations) so the pd.DataFrame annotation is treated as a string and not evaluated at definition time.

    - Strict enforcement alternative:
        Because this function only emits a warning, calling code that requires strict type enforcement should perform an explicit isinstance check and raise an exception (TypeError) or otherwise handle the non-DataFrame case instead of relying solely on this helper.

## `src.ydata_profiling.model.pandas.dataframe_pandas.pandas_preprocess` · *function*

## Summary:
Normalize DataFrame labels for profiling by renaming any column or index level named "index" to "df_index" and converting all column labels to strings; returns the (mutated) DataFrame.

## Description:
This function prepares a pandas.DataFrame for the profiling pipeline by applying two deterministic normalizations:

1. Calls rename_index(df) which:
   - Renames any column exactly named "index" to "df_index" using df.rename(..., inplace=True).
   - If an index level name equals "index", replaces that name with "df_index" using a list comprehension over df.index.names.
   - Returns the same DataFrame object.

2. Converts every column label to its string representation by assigning df.columns = df.columns.astype("str").

Known callers:
- No direct callers were identified in the retrieved code subset. The function is designed to be invoked as part of a larger preprocessing chain in the profiling pipeline.

Reason for extraction:
- Encapsulates label normalization into a single, reusable preprocessing step so downstream code can assume stable, string-typed column names and absence of a literal "index" label. This avoids duplicating the same normalization at multiple call sites.

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Description: Pipeline configuration object supplied by the caller.
        - Note: The current implementation does not read or mutate this object; it is accepted for API consistency with other preprocessing functions.

    df (pd.DataFrame)
        - Type: pandas.DataFrame
        - Description: The DataFrame to normalize.
        - Preconditions: Must implement pandas DataFrame API (methods/attributes used: .rename, .columns, .index.names).

## Returns:
    pd.DataFrame
        - The same DataFrame instance passed in, after in-place modifications:
            * Any column named exactly "index" is renamed to "df_index".
            * Any index level name equal to "index" is replaced with "df_index".
            * All column labels are cast to strings (df.columns.dtype becomes object/string).
        - Edge cases:
            * If casting column labels to strings yields duplicate names, this function does not resolve or deduplicate them — pandas will keep duplicates as-is.
            * If no renames or casts are necessary, the DataFrame is still returned (may be the identical object).

## Raises:
    - The function does not explicitly raise exceptions.
    - Runtime exceptions thrown by pandas operations (e.g., AttributeError if df is not a DataFrame or a pandas-specific error during astype) will propagate to the caller.

## Constraints:
    Preconditions:
        - Caller must pass a pandas.DataFrame-like object supporting the used DataFrame API.
        - If the caller must preserve the original DataFrame unchanged, they must pass a copy (e.g., df.copy()) because this function mutates the DataFrame in-place.

    Postconditions:
        - The returned DataFrame will not contain a column label equal to "index" (such labels become "df_index").
        - No index level name will be equal to "index" after return.
        - All column labels will be strings.

## Side Effects:
    - In-place mutation of the provided DataFrame:
        * rename_index uses df.rename(..., inplace=True).
        * Setting df.columns = df.columns.astype("str") mutates the DataFrame's columns.
    - No file, network, stdout operations, or global-state mutations occur.

## Control Flow:
flowchart TD
    Start([Start]) --> CallRenameIndex[/"Call rename_index(df)"/]
    CallRenameIndex --> RenameCols{"Does df have column named \"index\"?"}
    RenameCols --> RenameIndexLevel{"Does df.index.names contain \"index\"?"}
    RenameIndexLevel --> CastColumns["Cast df.columns to str\n(df.columns.astype('str'))"]
    CastColumns --> AssignColumns["Assign back to df.columns"]
    AssignColumns --> ReturnDF([Return df])
    ReturnDF --> End([End])

## Examples:
- Typical (in-place) usage where caller supplies a Settings instance:
    # config is assumed to be provided by the caller (an instance of Settings)
    # df is a pandas.DataFrame possibly containing a column named "index"
    df_normalized = pandas_preprocess(config, df)
    # After call: df (and df_normalized) has no column named "index"
    # and all column labels are strings.

- Preserve original DataFrame:
    df_copy = df.copy()         # caller-side copy to preserve the original
    df_normalized = pandas_preprocess(config, df_copy)

- Verifying the effects:
    # Before: columns may include "index" and non-string labels
    assert "index" not in df_normalized.columns
    assert all(isinstance(col, str) for col in df_normalized.columns)

