# `discretize_pandas.py`

## `src.ydata_profiling.model.pandas.discretize_pandas.DiscretizationType` · *class*

## Summary:
Represents the discretization strategy to use when converting continuous pandas series into discrete bins; enumerates the supported strategies ("uniform" and "quantile").

## Description:
This enumeration defines the allowed discretization strategies consumed by components that discretize numeric pandas Series (for example, routines that compute bin edges and assign integer bin indices). Instantiate or reference members when you need to parameterize a discretization operation with a named, type-safe choice instead of a raw string. Typical callers are functions or classes that accept a discretization strategy parameter; these callers should accept and prefer members of this enum (e.g., DiscretizationType.UNIFORM) but may also accept equivalent string values and convert them to the enum where convenient.

Motivation: Using a small enum centralizes the supported strategies, prevents typos in string literals, and provides an explicit API contract for functions that implement discretization behavior.

## State:
- This is an Enum subclass; instances are its members.
- Members:
    - UNIFORM
        - Type: DiscretizationType (enum member)
        - .value: "uniform" (str)
        - Meaning: Use equal-width (uniform) bins across the numeric range.
    - QUANTILE
        - Type: DiscretizationType (enum member)
        - .value: "quantile" (str)
        - Meaning: Use quantile-based bins such that each bin contains (approximately) the same number of observations.
- Valid values when constructing from a string: exactly "uniform" or "quantile" (case-sensitive).
- Invariants:
    - There are exactly these two supported members in this enum.
    - Each member's .value attribute is a unique string identifying the strategy.

## Lifecycle:
- Creation:
    - Preferred creation forms:
        - Direct member access: refer to DiscretizationType.UNIFORM or DiscretizationType.QUANTILE.
        - Conversion from the underlying value: DiscretizationType("uniform") or DiscretizationType("quantile") — this uses Enum's constructor and will validate the input.
    - No constructor parameters are defined by this class beyond what Enum provides.
- Usage:
    - Typical operations:
        - Pass a member as a configuration parameter to discretization functions.
        - Compare by identity or equality: use "is" (identity) or "==" to check the selected strategy.
        - Read .value to obtain the canonical string for serialization, logging, or use by downstream code that expects "uniform"/"quantile".
        - Access .name to get the member name ("UNIFORM" or "QUANTILE").
    - No specific ordering or sequence of method calls is required for correct operation — this is a passive value object.
- Destruction:
    - No cleanup or explicit destruction is required. Enum members are singletons managed by Python's Enum machinery.

## Method Map:
graph LR
    A[Caller] --> B[Select strategy]
    B --> C[DiscretizationType.UNIFORM or .QUANTILE]
    C --> D[Use .value for serialization]
    C --> E[Compare with is / ==]
    E --> F[Control discretization algorithm branch]
    D --> F

(Above graph shows typical flow: a caller chooses a strategy, references an enum member, optionally reads .value to serialize, compares the member to dispatch to the correct discretization implementation.)

## Raises:
- ValueError:
    - Trigger condition: attempting to construct a DiscretizationType from a string not equal to one of the defined .value strings, e.g., DiscretizationType("bad") will raise ValueError coming from Enum's value lookup.
- TypeError:
    - Trigger condition: passing a non-hashable or unsupported type to Enum machinery in uncommon code paths; not typical for normal usage where strings or enum members are used.

## Example:
- Create or reference a strategy:
    - Prefer referencing a member directly: use the UNIFORM or QUANTILE member.
    - Alternatively, convert from a canonical string (this validates the string and returns the matching member).
- Typical sequence:
    1. A caller determines which strategy to use (from user config, UI selection, or default).
    2. Obtain a DiscretizationType member, e.g., by direct member reference or by converting a validated string to the enum.
    3. Use member equality (or identity) to choose the discretization algorithm implementation.
    4. When persisting the chosen strategy, use member.value to store the canonical string ("uniform" or "quantile").
- Notes:
    - Do not assume case-insensitive matching when converting from string; the constructor requires exact match of the .value string.
    - Because members are singletons, comparing with "is" is safe and idiomatic when both operands are enum members.

## `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer` · *class*

## Summary:
Discretizer is a small utility class that converts numeric columns in a pandas DataFrame into integer bin indices using a chosen discretization strategy (quantile or uniform).

## Description:
Use this class when you need a reproducible way to convert continuous numeric columns of a pandas DataFrame into discrete integer bins prior to profiling, aggregation, or categorical analysis. The class is instantiated with a DiscretizationType (an enum with QUANTILE and UNIFORM members), the number of bins to produce, and an optional reset_index flag.

Typical callers:
- Preprocessing pipelines that prepare numeric data for categorical summaries.
- Reporting or profiling code that wants to present binned numeric features.
- Any code that needs a programmatic, per-column discretization over a DataFrame and desires to keep non-numeric columns unchanged.

Responsibility boundary:
- This class only handles selection of numeric columns, dispatching to pandas.qcut or pandas.cut to convert a single Series into integer bin labels, and applying that conversion across a DataFrame's numeric columns.
- It does not attempt to validate or coerce non-numeric columns, handle categorical columns, or persist/return bin edge definitions. It also does not sanitize or impute missing values — behavior for NaNs follows pandas.qcut/pandas.cut semantics.

## State:
Attributes (set by __init__):
- discretization_type (DiscretizationType)
    - Type: DiscretizationType enum member.
    - Meaning: Strategy used to discretize numeric Series. Supported members: DiscretizationType.QUANTILE, DiscretizationType.UNIFORM.
    - Invariant: Must be one of the enum members; otherwise, _discretize_column will not return a valid array (method only handles the two known members).
- n_bins (int)
    - Default: 10
    - Meaning: Target number of bins to produce per numeric column.
    - Valid range / constraints: The code does not validate this value; callers should provide a positive integer (>= 1). Invalid values (e.g., <= 0 or non-integers) may cause pandas.cut / pandas.qcut to raise exceptions.
- reset_index (bool)
    - Default: False
    - Meaning: If True, the DataFrame returned by discretize_dataframe will have its index reset (drop=True). If False, the original index is preserved.

Class invariants:
- After construction, the three attributes above exist and are used unchanged during discretization.
- The discretizer expects discretization_type to be either QUANTILE or UNIFORM; other values are not handled and will result in None being returned from _discretize_column (leading to invalid column assignment).

## Lifecycle:
Creation:
- Instantiate with:
    - method: DiscretizationType (no automatic conversion from string inside this class — pass an enum member)
    - n_bins: int = 10 (optional)
    - reset_index: bool = False (optional)
  Example: Discretizer(DiscretizationType.QUANTILE, n_bins=4, reset_index=True)

Usage (typical sequence):
1. Create a Discretizer instance.
2. Call discretize_dataframe(dataframe) passing a pandas DataFrame (the code expects the DataFrame type referenced as pd.DataFrame in the signature).
   - The method:
     - Makes a shallow copy of the DataFrame.
     - Identifies numeric columns via _get_numerical_columns.
     - Replaces each numeric column with integer bin indices returned by _discretize_column (one integer per row for that column).
     - Reorders columns back to the original ordering.
     - Optionally resets the index if reset_index is True.
3. Use the returned DataFrame for downstream tasks.

Method ordering and requirements:
- No special ordering of method calls is required by the caller other than calling discretize_dataframe after construction.
- The helper methods (_discretize_column, _descritize_quantile, _descritize_uniform, _get_numerical_columns) are internal implementation details and are invoked by discretize_dataframe automatically.

Destruction / cleanup:
- No cleanup or resource management is required. The class does not open files or hold external resources.

## Method Map:
graph LR
    A[User] --> B[Discretizer.__init__]
    B --> C[discretize_dataframe(dataframe)]
    C --> D[_get_numerical_columns(dataframe)]
    C --> E[_discretize_column(series)]
    E --> F{discretization_type}
    F -->|QUANTILE| G[_descritize_quantile(series) -> pd.qcut -> ndarray]
    F -->|UNIFORM| H[_descritize_uniform(series) -> pd.cut -> ndarray]
    G --> I[assign integer ndarray back to column]
    H --> I
    I --> J[reorder columns, optionally reset index]
    J --> K[return DataFrame]

## Behavior details (per-method):
- __init__(method: DiscretizationType, n_bins: int = 10, reset_index: bool = False) -> None
    - Stores the provided configuration onto the instance.
    - Does not validate argument types or values (no exceptions are raised explicitly here).

- discretize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame
    - Input: a pandas DataFrame (referred to as pd.DataFrame in the signature).
    - Operation:
        - Makes dataframe.copy() to avoid mutating the caller's DataFrame.
        - Computes numeric column names via _get_numerical_columns.
        - For each numeric column name, replaces that column with the numpy array returned by _discretize_column applied to the corresponding Series.
        - Keeps the original column order and optionally resets the index (drop=True) if reset_index is True.
    - Non-numeric columns are preserved unchanged.
    - Returns: a pandas DataFrame with numeric columns replaced by integer bin labels (0..k-1). The exact number of bins per column may be <= n_bins if pandas.qcut/pandas.cut drop duplicate edges.
    - Edge cases:
        - If a column contains too few distinct values, pandas.qcut/pandas.cut may drop duplicate bin edges (duplicates="drop") and return fewer bins; if the input is unsuitable, pandas may raise an exception (ValueError) — see Raises below.
        - If discretization_type is not one of the two supported enum members, _discretize_column returns None which will be assigned into the DataFrame column (likely causing an exception or producing an invalid column).

- _discretize_column(column: pd.Series) -> pd.Series (internal)
    - Dispatches to either _descritize_quantile or _descritize_uniform based on self.discretization_type (compares to DiscretizationType.QUANTILE and DiscretizationType.UNIFORM).
    - If discretization_type is neither member, the method returns None (no explicit fallback).

- _descritize_quantile(column: pd.Series) -> numpy.ndarray
    - Uses pandas.qcut with q=self.n_bins, labels=False, retbins=False, duplicates="drop".
    - Returns the .values of the qcut result (an ndarray of integer bin indices).
    - Note: qcut attempts to create quantile-based bins; duplicates="drop" reduces the number of bins if bin edges are not unique.

- _descritize_uniform(column: pd.Series) -> numpy.ndarray
    - Uses pandas.cut with bins=self.n_bins, labels=False, retbins=True, duplicates="drop".
    - Returns the first element [0] of the returned tuple (the array of integer bin labels), then .values.
    - Note: cut creates equal-width bins across the value range; retbins=True is requested but only the labels (index 0) are used.

- _get_numerical_columns(dataframe: pd.DataFrame) -> List[str]
    - Returns dataframe.select_dtypes(include=np.number).columns.tolist()
    - Effect: selects columns whose dtype is numeric (NumPy number types) and returns their names as a list of strings.

## Raises:
- __init__:
    - This constructor does not explicitly raise exceptions. Passing incorrect types will not be validated here and may cause errors at usage time.
- discretize_dataframe and internal helpers:
    - pandas.qcut / pandas.cut may raise ValueError for pathological inputs (for example, if n_bins is inappropriate for the data, or the Series contains insufficient unique values even with duplicates="drop" in some pandas versions). These exceptions originate from pandas and are not caught in this class.
    - Assigning the result of _discretize_column may raise exceptions if _discretize_column returns None (e.g., when discretization_type is an unsupported value).

## Example:
- Typical usage:
    - from src.ydata_profiling.model.pandas.discretize_pandas import Discretizer
    - from src.ydata_profiling.model.pandas.discretize_pandas import DiscretizationType
    - d = Discretizer(DiscretizationType.QUANTILE, n_bins=4, reset_index=True)
    - discretized = d.discretize_dataframe(df)  # df is a pandas DataFrame
    - # nondiscretized (non-numeric) columns remain unchanged; numeric columns are replaced by integer bin indices
    - # No explicit cleanup needed.

### `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer.__init__` · *method*

## Summary:
Configure the Discretizer by storing the chosen discretization strategy, target bin count, and index-reset preference on the instance.

## Description:
Known callers and context:
- Instantiated by preprocessing or profiling code that needs to discretize numeric columns of a pandas DataFrame before aggregation, reporting, or categorical analysis.
- Typical usage: construct during pipeline configuration, then call discretize_dataframe(dataframe) to apply binning.

Why this logic is its own method:
- Centralizes instance configuration so other methods can rely on the presence of well-known attributes (discretization_type, n_bins, reset_index). Keeping initialization separate simplifies downstream logic and testing.

## Args:
    method (DiscretizationType): Discretization strategy to use. Expected to be a DiscretizationType enum member (supported members include DiscretizationType.QUANTILE and DiscretizationType.UNIFORM). The constructor does not coerce or validate the value.
    n_bins (int, optional): Target number of bins per numeric column. Defaults to 10. The constructor does not enforce constraints; callers should provide a sensible positive integer.
    reset_index (bool, optional): If True, later calls such as discretize_dataframe will reset the returned DataFrame's index (drop=True). Defaults to False.

## Returns:
    None — the method initializes instance attributes and returns no value.

## Raises:
    None — this constructor does not raise exceptions itself. It performs no validation; any errors arising from invalid configuration values will manifest later when other methods (e.g., discretize_dataframe) use these attributes or when callers validate inputs before construction.

## State Changes:
Attributes READ:
    - None. The constructor does not read pre-existing instance attributes.

Attributes WRITTEN:
    - self.discretization_type (DiscretizationType): set to method
    - self.n_bins (int): set to n_bins
    - self.reset_index (bool): set to reset_index

## Constraints:
Preconditions:
    - The caller is expected to provide a DiscretizationType member for method and an integer >= 1 for n_bins for meaningful behavior. These are caller responsibilities; the constructor does not validate them.

Postconditions:
    - After construction, the instance has discretization_type, n_bins, and reset_index attributes initialized to the provided values and downstream methods can rely on their presence.

## Side Effects:
    - No I/O or external calls occur.
    - The constructor mutates only the instance (assigns three attributes) and performs no other side effects.

### `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer.discretize_dataframe` · *method*

## Summary:
Creates and returns a copy of the input DataFrame where every numeric column (as determined by pandas/numpy dtypes) has been replaced by its discretized bin labels; may reset the index on the returned DataFrame depending on the instance configuration. The Discretizer object's persistent state is not modified.

## Description:
This method performs a full discretization pass over the provided pandas DataFrame:
- It starts by making a shallow copy of the input DataFrame to avoid mutating the caller's object.
- It asks _get_numerical_columns(dataframe) to determine which columns are numeric (selected using pandas.select_dtypes(include=np.number)).
- For each numeric column, it calls _discretize_column on the column's Series and assigns the returned bin-label sequence back into the corresponding column of the copied DataFrame.
- After processing numeric columns, it reorders/retains the original column ordering and optionally resets the index if the Discretizer instance has reset_index set to True.

Known callers and lifecycle context:
- No specific internal callers are present in the immediate module memory. The method is intended for use by higher-level preprocessing or profiling pipelines that need to convert continuous numeric features into discrete bins before downstream analysis or modelling.
- Typical lifecycle: invoked once per DataFrame when discretization is required as a preprocessing step.

Why this is a separate method:
- Encapsulates the end-to-end DataFrame-level discretization logic (copying, column selection, per-column dispatch, final reordering/index handling) in a single, reusable place rather than duplicating the loop and index-management logic where discretization is needed.
- Keeps higher-level code simple and allows the per-column discretization logic to be tested independently via _discretize_column.

## Args:
    dataframe (pandas.DataFrame):
        - The input table to be discretized. Must be a pandas DataFrame (or an object compatible with pandas.DataFrame.copy, .columns, .loc, and .select_dtypes).
        - There is no modification of the caller-supplied DataFrame; a copy is used.
        - Allowed contents: any dtypes. Only columns that pandas.select_dtypes(include=np.number) recognizes as numeric are processed.

## Returns:
    pandas.DataFrame:
        - A new DataFrame (a copy) with the same columns as the input (same order) where numeric columns have been replaced by the discretized bin labels produced by _discretize_column.
        - The returned DataFrame will have the same number of rows as the input unless an exception occurs during assignment (see Raises).
        - If self.reset_index is True, the returned DataFrame will have a new default integer index (original index dropped); otherwise the original index from the copy is preserved.
        - Edge-case return observations:
            * If the input contains no numeric columns, the returned DataFrame is effectively a shallow copy of the input (possibly with the index reset if configured).
            * If _discretize_column returns an array of bin labels with dtype that contains NaN for missing values, the resulting column dtype may be float where NaN is present.

## Raises:
    - Propagated exceptions from pandas and the helper methods; this method does not catch them:
        * ValueError: may be raised by pandas.qcut or pandas.cut when bins/quantiles cannot be computed (e.g., insufficient unique values), or by pandas when attempting to assign an output array whose length does not match the number of rows in the DataFrame.
        * TypeError: may be raised if the column dtype is not compatible with pandas.cut/qcut or if assignment is invalid.
        * AttributeError: if the supplied object does not implement required DataFrame methods (.copy, .columns, .loc, .select_dtypes).
    - Behavioral note: If _discretize_column returns None (for example, because the configured discretization type is unsupported), assigning None to a DataFrame column will replace that column's values with None/NaN-like values for all rows; this is not explicitly checked here and will not raise before the assignment, though downstream usage may fail.

## State Changes:
    Attributes READ:
        - self.reset_index: read to decide whether to reset index on the returned DataFrame.
        - self.discretization_type and self.n_bins: read indirectly by the called helper methods (_discretize_column -> _descritize_quantile/_descritize_uniform).
        - Note: those reads happen via method calls; discretize_dataframe itself only directly references reset_index and calls the helper methods.

    Attributes WRITTEN:
        - None. The Discretizer instance is not modified by this method.

## Constraints:
    Preconditions:
        - The argument must be a pandas.DataFrame (or compatible object exposing .copy, .columns, .loc, and .select_dtypes).
        - The Discretizer instance should be configured with a valid DiscretizationType and a positive integer self.n_bins for meaningful discretization.
        - The DataFrame should have at least as many rows/unique values as required by the selected pandas binning strategy to avoid qcut/cut errors (otherwise pandas will raise).

    Postconditions:
        - The returned DataFrame is a copy of the input with numeric columns replaced by the bin-label sequences produced by _discretize_column.
        - The original input DataFrame is left unmodified.
        - Column order is preserved exactly as in the input (all_columns is used to reindex).
        - If reset_index was True, the returned DataFrame's index is a new RangeIndex with the original index dropped.

## Side Effects:
    - No external I/O (no files, databases, or network calls).
    - No mutation of the input DataFrame (a copy is used), and no mutation of any other external objects is performed by this method.
    - The primary side effects are the computational work performed by pandas functions (qcut/cut) called indirectly via _discretize_column and the memory allocated for the returned DataFrame and intermediate copies.
    - Exceptions thrown by pandas (see Raises) will propagate to the caller and may interrupt caller workflows.

### `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer._discretize_column` · *method*

## Summary:
Chooses the configured discretization strategy and applies it to a numeric pandas Series, returning the sequence of bin labels (or None if no matching strategy is configured). This method does not modify object state.

## Description:
This method implements the strategy selection step of the discretization pipeline. It is invoked by Discretizer.discretize_dataframe for each numeric column discovered by _get_numerical_columns. By centralizing the dispatch to per-strategy helpers, the code keeps individual discretization algorithms (_descritize_quantile and _descritize_uniform) focused and testable, and allows adding new strategies without duplicating call-site logic.

Known callers:
- Discretizer.discretize_dataframe — called for each numeric column while building the discretized DataFrame.

Why this is a separate method:
- Encapsulates the mapping from DiscretizationType to a concrete discretization routine.
- Keeps the control flow for selecting a discretization algorithm separate from the implementation details of each algorithm.

## Args:
    column (pandas.Series): The input one-dimensional Series to discretize. Expected to hold numeric data (integer or float). The Series may contain missing values (NaN); these are handled by the underlying pandas routines.

## Returns:
    numpy.ndarray | None:
        - numpy.ndarray: A 1-D array with length equal to len(column) when a recognized discretization strategy is applied.
            * Non-missing input values are replaced by integer bin labels (0-based). The dtype will commonly be integer, but if NaNs are present pandas may return a float array where NaN denotes missing labels.
            * The effective number of bins can be less than self.n_bins when pandas.drop duplicates in bin edges (duplicates="drop").
        - None: If self.discretization_type is not one of the handled values (QUANTILE or UNIFORM), the method returns None because there is no else branch handling other enum values.

    Note: Although the method signature is annotated to return a pandas.Series, the current implementation delegates to helper methods that return .values from pandas.cut/qcut (i.e., numpy arrays). Callers should expect a numpy.ndarray unless the implementation changes.

## Raises:
    Any exception raised by the underlying pandas functions (propagated):
        - ValueError: Raised by pandas.qcut when there are insufficient unique values to compute the requested quantiles (e.g., q > number of distinct values), or by pandas.cut for invalid bin specifications.
        - TypeError: May be raised by pandas if the Series dtype is inappropriate for numeric binning.
    This method does not catch these exceptions; they propagate to the caller.

## State Changes:
    Attributes READ:
        - self.discretization_type: read to determine which helper to call
        - self.n_bins: read indirectly by the helper methods invoked
    Attributes WRITTEN:
        - None (the object state is not modified)

## Constraints:
    Preconditions:
        - self.discretization_type should be a DiscretizationType, and ideally one of DiscretizationType.QUANTILE or DiscretizationType.UNIFORM for a non-None return.
        - column should be a pandas.Series of numeric dtype; in practice discretize_dataframe passes only columns returned by _get_numerical_columns (which selects numpy.number dtypes).
    Postconditions:
        - If a supported discretization_type is set, the returned 1-D numpy.ndarray has length equal to the input Series.
        - Each non-missing input maps to a bin label; missing inputs map to NaN in the returned array (depending on pandas behavior).
        - If self.discretization_type is unsupported, the method returns None.

## Side Effects:
    - No file or network I/O.
    - No mutation of the input Series or other external objects.
    - Exceptions and their side effects (if any) come exclusively from pandas.cut / pandas.qcut invoked by the helper methods.

### `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer._descritize_quantile` · *method*

## Summary:
Convert a numeric pandas Series into discrete quantile-based bin labels and return the labels as a numpy array; does not modify object state.

## Description:
This method applies quantile-based discretization (equal-frequency bins) to the supplied pandas Series using pandas.qcut and returns the resulting bin labels as a numpy array. Known callers:
- Discretizer._discretize_column — calls this method when self.discretization_type == DiscretizationType.QUANTILE.
- Discretizer.discretize_dataframe — indirectly invokes this method via _discretize_column for each numerical column during the dataset discretization pipeline.

This logic is separated into its own method because quantile discretization requires different pandas API parameters than uniform discretization, and isolating it keeps the discretization strategy implementations modular and easier to test.

## Args:
    column (pandas.Series): A one-dimensional pandas Series containing the values to discretize. Expected to be numeric (integers/floats) or convertible to numeric bins. The method does not coerce types — non-numeric or incompatible dtypes may cause pandas.qcut to raise.

## Returns:
    numpy.ndarray: A 1-D numpy array with length equal to len(column) containing the bin labels assigned by pandas.qcut.
    - Typical values are integer labels in the range [0, k-1] where k is the number of bins actually created.
    - Missing entries in the input (NaN) will be represented as numpy.nan in the output array (which may force the array dtype to float).
    - If pandas.qcut reduces the number of bins due to duplicate edges, the label range will reflect the reduced bin count.
Note: The method's annotation indicates a pandas.Series return, but the implementation returns the .values attribute from qcut, i.e., a numpy.ndarray.

## Raises:
    ValueError: Propagated from pandas.qcut for invalid q or when qcut cannot construct bins (for example, if q is not a positive integer or if the column values make bin edges invalid in a way pandas cannot handle).
    TypeError: May be raised by pandas.qcut if the input Series has an unsupported dtype for quantile binning.
These exceptions are not caught by this method and will surface to callers.

## State Changes:
Attributes READ:
    self.n_bins
Attributes WRITTEN:
    None — the method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.n_bins must be an integer-like value suitable for pandas.qcut (typically >= 1).
    - The input column should be a pandas.Series of length >= 0. For an empty Series, pandas.qcut will return an empty array.
    - The method assumes it is called only when quantile discretization is intended (i.e., the caller checks self.discretization_type).

Postconditions:
    - Returns an array of bin labels with the same length as the input Series.
    - The Discretizer instance's attributes remain unchanged.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside of returning the computed array.
    - Relies on pandas.qcut internals; side effects are limited to the memory allocation of the returned numpy array.

### `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer._descritize_uniform` · *method*

## Summary:
Convert a numeric pandas Series into uniform-width bin indices (0-based) using the object's configured number of bins; updates no object state but returns an array of bin codes corresponding to the input values.

## Description:
Known callers and lifecycle:
- Called by Discretizer._discretize_column when self.discretization_type == DiscretizationType.UNIFORM.
- Indirectly invoked for each numeric column by Discretizer.discretize_dataframe during the discretization pipeline that produces a discretized DataFrame from an input DataFrame.
- This method encapsulates the specific logic for "uniform" binning (as opposed to quantile binning), keeping binning concerns isolated so the column-dispatch and overall pipeline can remain simple and the two discretization strategies can be tested and maintained independently.

Why this is its own method:
- Separates algorithmic (uniform binning) details from dispatching and DataFrame-level iteration.
- Makes unit-testing the uniform binning behavior straightforward and avoids duplicating pandas.cut call-site configuration.
- Keeps API parity with the quantile discretization implementation (_descritize_quantile).

## Args:
    column (pandas.Series): 1-D pandas Series containing numeric data to be discretized.
        - Allowed values: numeric dtypes (integers or floats). NaN values are allowed and are preserved as NaN in the output codes.
        - Precondition: column should represent the values for a single feature/column (length >= 0). The calling code selects numeric columns, so callers are expected to pass numeric Series.

## Returns:
    numpy.ndarray:
        - A 1-D numpy array with length equal to len(column) containing integer bin indices in the range [0, k-1], where k is the number of bins actually produced by pandas.cut (k <= self.n_bins when duplicate bin edges are dropped).
        - Positions corresponding to input NaN values are preserved as NaN in the returned array; when any NaN values are present the array dtype will generally be a float (because NaN is a float), otherwise integer dtype is typical.
        - Note: Although the method signature is annotated to return pandas.Series, this implementation returns the raw .values array from pandas.cut (i.e., a numpy.ndarray).

## Raises:
    - Propagates exceptions raised by pandas.cut called internally. In particular:
        - ValueError: may be raised if bins/self.n_bins is invalid for the data (for example, if bin edges cannot be constructed); exact conditions are those raised by pandas.cut.
        - TypeError: may be raised by pandas.cut if the provided column contains non-comparable/non-numeric types incompatible with numeric binning.
    - The method does not raise its own custom exceptions; callers should handle or allow propagation of pandas errors.

## State Changes:
    Attributes READ:
        - self.n_bins: used to set the number of uniform bins passed to pandas.cut.
    Attributes WRITTEN:
        - None (no attributes of self are modified).

## Constraints:
    Preconditions:
        - self.n_bins must be an integer-like value accepted by pandas.cut as the bins argument (typically int >= 1).
        - column should be a pandas.Series of numeric values (calling code in Discretizer already selects numeric columns).
    Postconditions:
        - The Discretizer instance remains unchanged.
        - The returned array has the same length and index order as the input series (index is not preserved in the numpy array — if index preservation is required callers must re-wrap into a Series).
        - The number of distinct bins produced (k) will be <= self.n_bins when duplicate bin edges are removed by pandas.cut with duplicates="drop".

## Side Effects:
    - No I/O, no network calls.
    - No mutation of the input column or any external object; the only mutation is the creation of an in-memory numpy array returned to the caller.
    - Relies on pandas.cut side effects only (none that mutate inputs).

### `src.ydata_profiling.model.pandas.discretize_pandas.Discretizer._get_numerical_columns` · *method*

## Summary:
Return the DataFrame's numeric column labels (in original column order) as a list, without modifying the Discretizer instance.

## Description:
This helper determines which columns in the provided pandas DataFrame have numeric dtypes and returns their labels. It delegates the dtype detection to pandas.DataFrame.select_dtypes using include=np.number so the exact set of recognized numeric types follows pandas/numpy rules.

Known callers:
    - Discretizer.discretize_dataframe(dataframe: pd.DataFrame)
      Context: Called at the start of the discretization pass to build the list of columns that will be discretized by the Discretizer.

Why this is a separate method:
    - Keeps dtype-selection logic isolated from the main discretization loop for clarity and single responsibility.
    - Easier to override or extend numeric-column selection behavior in subclasses or tests.
    - Improves testability: numeric-column selection can be unit-tested independently.

## Args:
    dataframe (pd.DataFrame): The pandas DataFrame to inspect.
        - Expected: a pandas DataFrame (an object supporting select_dtypes and having a .columns attribute).
        - Any DataFrame is allowed; if no numeric columns exist the method returns an empty list.

## Returns:
    List[str]: A list of the DataFrame's column labels that pandas.select_dtypes(include=np.number) classifies as numeric.
        - Order: labels appear in the same order as dataframe.columns.
        - Note on types: although the type hint is List[str], the method returns the column labels as they exist on the DataFrame. For example, if the DataFrame uses a MultiIndex for columns the returned items may be tuples; if column labels are integers they will be integers.
        - Edge cases:
            * No numeric columns => returns [].
            * MultiIndex columns => returns a list of the MultiIndex keys (tuples) corresponding to numeric dtypes.

## Raises:
    - This method does not raise its own custom exceptions. Exceptions raised by pandas are propagated to the caller, for example:
        - AttributeError if the provided object does not implement select_dtypes (i.e., not DataFrame-like).
        - TypeError or ValueError if pandas.select_dtypes is invoked with an invalid include argument (unlikely here because include=np.number is valid).
        - Any internal pandas exception encountered during dtype inspection.

## State Changes:
    Attributes READ:
        - None. The method does not access any self.<attr> fields.

    Attributes WRITTEN:
        - None. The method does not modify the Discretizer instance.

## Constraints:
    Preconditions:
        - The caller must pass a pandas.DataFrame or a compatible object exposing select_dtypes(include=...) and a .columns attribute.
        - If strict string column names are required by downstream code, callers must coerce or validate labels after receiving the result.

    Postconditions:
        - The Discretizer instance remains unchanged.
        - The returned list contains exactly the DataFrame's column labels that pandas considers numeric according to numpy.number.

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not mutate the input DataFrame or other external objects.

