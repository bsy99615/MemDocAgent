# `describe_path_pandas.py`

## `src.ydata_profiling.model.pandas.describe_path_pandas.path_summary` · *function*

## Summary:
Compute aggregated path statistics from a pandas Series of filesystem-like paths: common prefix (or a sentinel) plus frequency counts and unique counts for stems, suffixes, basenames, parent directories, and drive anchors.

## Description:
This utility parses each element of the provided pandas Series as a filesystem path and returns a dictionary of aggregated statistics derived from standard os.path operations:
- common_prefix: longest common prefix across all entries (or "No common prefix" when empty),
- stem_counts / suffix_counts / name_counts / parent_counts / anchor_counts: frequency counts obtained by mapping os.path.splitext, os.path.basename, os.path.dirname, and os.path.splitdrive respectively,
- n_*_unique: integer counts of unique items for each corresponding *_counts Series.

Why this is a separate function:
- Centralizes path tokenization and counting so profiling code can call a single, well-defined helper for path-like columns.
- Keeps parsing semantics consistent across any consumers that need the same path-derived statistics.

## Args:
    series (pd.Series):
        The input pandas Series whose elements are expected to be path-like values (strings or os.PathLike).
        - Required; no default.
        - The function calls .values.tolist() and .map(...) on this object, so it must support these operations.
        - If elements are not string-like (for example None, numpy.nan, numeric types), underlying os.path functions may raise exceptions; callers should sanitize the Series beforehand when necessary (e.g., dropna(), astype(str), or filter by instance).

## Returns:
    dict
        A dictionary with these keys and types:

        - "common_prefix" (str)
            The value returned by os.path.commonprefix(list_of_values). If that value is the empty string '', the function returns the literal string "No common prefix" instead.
        - "stem_counts" (pandas.Series[int])
            value_counts() of os.path.splitext(x)[0] applied to each element. Index: unique stem strings; Values: integer counts (sorted descending by pandas.value_counts()).
        - "suffix_counts" (pandas.Series[int])
            value_counts() of os.path.splitext(x)[1] (the extension including leading dot, or '' when no extension).
        - "name_counts" (pandas.Series[int])
            value_counts() of os.path.basename(x).
        - "parent_counts" (pandas.Series[int])
            value_counts() of os.path.dirname(x).
        - "anchor_counts" (pandas.Series[int])
            value_counts() of os.path.splitdrive(x)[0] (drive/anchor on Windows or '' on POSIX).
        - "n_stem_unique" (int)
            len(stem_counts)
        - "n_suffix_unique" (int)
            len(suffix_counts)
        - "n_name_unique" (int)
            len(name_counts)
        - "n_parent_unique" (int)
            len(parent_counts)
        - "n_anchor_unique" (int)
            len(anchor_counts)

    Edge-case returns:
        - Empty input Series: value_counts results are empty pandas.Series objects; all "n_*_unique" are 0. os.path.commonprefix([]) yields '' so the function returns "No common prefix".
        - Entries without extensions: suffix_counts will include the empty string '' as a key for those items.

## Raises:
    The function itself does not explicitly raise new exceptions, but operations it performs may propagate exceptions from Python or pandas:
    - TypeError: may occur if any element is not string-like or os.PathLike when passed to os.path functions (e.g., None, numpy.nan, numeric types). To avoid this, sanitize the Series before calling.
    - AttributeError: may occur if the provided object does not have .map or .values attributes (i.e., it's not a pandas.Series or similar).

## Constraints:
    Preconditions:
    - The caller must provide an object that behaves like a pandas.Series (supports .map and .values.tolist()).
    - Preferably the Series elements are strings or os.PathLike objects.

    Postconditions:
    - The returned dict contains all keys described in Returns.
    - Each "n_*_unique" equals len(corresponding "*_counts").
    - The input Series is not mutated.

## Side Effects:
    - None. The function performs in-memory computations only and does not perform I/O, logging, or modify global state.

## Complexity:
    - Time complexity: O(n * L) where n is number of elements and L is average path length (mapping and commonprefix scanning).
    - Memory complexity: O(n) for the temporary list produced by series.values.tolist() and for the value_counts outputs.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> ToList[series.values.tolist() -> list_of_values]
    ToList --> ComputeCommon[common = os.path.commonprefix(list_of_values)]
    ComputeCommon --> CheckEmpty{common == ''}
    CheckEmpty -- true --> SetNoPrefix[common_prefix = "No common prefix"]
    CheckEmpty -- false --> KeepPrefix[common_prefix = common]
    KeepPrefix --> MapStems[stem_counts = series.map(lambda x: os.path.splitext(x)[0]).value_counts()]
    SetNoPrefix --> MapStems
    MapStems --> MapSuffixes[suffix_counts = series.map(lambda x: os.path.splitext(x)[1]).value_counts()]
    MapSuffixes --> MapNames[name_counts = series.map(lambda x: os.path.basename(x)).value_counts()]
    MapNames --> MapParents[parent_counts = series.map(lambda x: os.path.dirname(x)).value_counts()]
    MapParents --> MapAnchors[anchor_counts = series.map(lambda x: os.path.splitdrive(x)[0]).value_counts()]
    MapAnchors --> CountUniques[Compute n_*_unique = len(corresponding *_counts)]
    CountUniques --> Assemble[Assemble summary dict with all keys]
    Assemble --> Return([Return summary dict])
    Return --> End([End])

## Examples:
1) Typical usage:
    import pandas as pd
    # Ensure pandas is available as pd in the caller scope (the function's annotation uses pd.Series)
    s = pd.Series([
        "/home/alice/project/report.pdf",
        "/home/alice/project/data.csv",
        "/home/alice/notes/todo.txt"
    ])
    summary = path_summary(s)
    # summary["common_prefix"] is the common prefix string or "No common prefix"
    # summary["suffix_counts"] contains counts for ".pdf", ".csv", ".txt"

2) Sanitizing input with missing/non-string entries:
    s_mixed = pd.Series(["/a/x.txt", None, float("nan"), 123])
    s_clean = s_mixed.dropna().astype(str)   # coerce to strings or filter non-string items
    summary = path_summary(s_clean)

3) Empty series:
    empty = pd.Series([], dtype=object)
    summary = path_summary(empty)
    # summary["common_prefix"] == "No common prefix"
    # All *_counts are empty; all "n_*_unique" are 0

## `src.ydata_profiling.model.pandas.describe_path_pandas.pandas_describe_path_1d` · *function*

## Summary:
Validate a pandas Series of path-like strings and merge path-derived aggregate statistics into the provided summary dictionary, returning the unchanged config and series alongside the updated summary.

## Description:
This function performs light validation on a pandas Series intended to contain filesystem-like paths and then augments the provided summary dict with the results of a path tokenization/counting helper (path_summary). It is intended to be used as the pandas-specific implementation for describing 1D "path" columns in the profiling pipeline.

Known callers and typical context:
- No direct callers were found in the provided code snapshot. In the profiling pipeline, a dispatcher or higher-level "describe" routine selects a backend implementation (e.g., the pandas-specific function) for a path-typed column and invokes this function during the column-description stage.
- It implements the pandas specialization of the abstract describe_path_1d interface (the generic entrypoint that profiling code uses to describe path-like columns).

Why this is extracted:
- Keeps validation and the merge-with-summary step separate from the path-parsing/tokenization logic (which lives in path_summary). This enforces a clear responsibility boundary: validate inputs and integrate algorithmic results into the profiling summary without inlining the parsing/counting logic.

## Args:
    config (Settings):
        Configuration object for the profiling run. This function does not read or mutate config in the current implementation; it is passed through to preserve a consistent function signature used by the profiling pipeline.
    series (pd.Series):
        The pandas Series to describe. Requirements:
        - Must be a pandas Series (or pandas-like object) exposing attributes used below.
        - Must not contain missing values (series.hasnans must be False).
        - Must expose the .str accessor (hasattr(series, "str") must be True), which implies element types compatible with string operations.
        - Elements should be path-like strings or os.PathLike-compatible values to avoid exceptions when path_summary applies os.path functions.
    summary (dict):
        A mutable dictionary representing the accumulating column summary. The function updates this dict in-place by merging the dict returned from path_summary(series). The caller should provide a dict instance; it will be mutated and returned.

Interdependencies:
- The function assumes the path tokenization and counting is implemented by path_summary(series). Any contract changes in path_summary affect this function's behavior and the shape of keys merged into summary.

## Returns:
    Tuple[Settings, pd.Series, dict]
        - The original config object (unchanged).
        - The original series object (unchanged).
        - The summary dict after being updated in-place with the dictionary produced by path_summary(series).

Possible return shapes/edge cases:
- For an empty input series, path_summary returns counts as empty pandas.Series and sets "common_prefix" to the sentinel "No common prefix"; these keys will be merged into summary.
- The function does not create a new summary dict; it mutates the provided summary and returns it, so callers should not assume a fresh dict is returned.

## Raises:
    ValueError("May not contain NaNs"):
        Raised when series.hasnans is True. The function refuses to operate on Series with missing values to avoid ambiguous path parsing.
    ValueError("series should have .str accessor"):
        Raised when the provided series lacks the .str accessor (hasattr(series, "str") is False). This indicates the series elements are not string-like or the object is not a pandas Series.
    Any exception propagated from path_summary(series):
        - path_summary may raise TypeError or other exceptions if elements are not string-like or os.PathLike, or if the passed object does not behave like a pandas Series (missing .map or .values). These exceptions are not caught here and will propagate to callers.

## Constraints:
Preconditions:
- Caller must supply a pandas-like Series with no NaNs and with string-like elements (or otherwise compatible with os.path operations).
- Caller must supply a mutable dict for summary.

Postconditions:
- summary contains all keys produced by path_summary (for example: "common_prefix", "stem_counts", "suffix_counts", "name_counts", "parent_counts", "anchor_counts", and the "n_*_unique" integer counts).
- The returned tuple preserves the original config and series objects.

## Side Effects:
- Mutates the provided summary dictionary by updating it with the mapping returned from path_summary(series).
- No file, network, stdout I/O, global state mutation, or external service calls are performed by this function itself.
- Any side effects from path_summary (none in its documented behavior) would be indirect effects of calling this function.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> CheckNaN{series.hasnans ?}
    CheckNaN -- true --> RaiseNaN[Raise ValueError("May not contain NaNs")]
    CheckNaN -- false --> CheckStr{hasattr(series,"str") ?}
    CheckStr -- false --> RaiseStr[Raise ValueError("series should have .str accessor")]
    CheckStr -- true --> CallPath[path_summary(series)]
    CallPath --> UpdateSummary[summary.update(path_summary_result)]
    UpdateSummary --> Return([Return config, series, summary])
    Return --> End([End])

## Examples (usage described in prose):
- Typical successful usage:
  1. The profiling dispatcher determines a column is of path-like type and prepares a Settings object, the pandas Series for that column (with missing values removed), and an empty summary dict.
  2. It calls this function with (config, series, summary).
  3. The function validates the series, uses path_summary to compute path statistics (common prefix, counts of stems/suffixes/names/parents/anchors, and unique counts), merges those into the provided summary dict, and returns (config, series, summary).
  4. The caller continues the profiling pipeline using the enriched summary.

- Handling invalid input:
  - If the series contains NaNs, callers should either pre-clean the Series (drop or fill missing values) or catch ValueError("May not contain NaNs") and handle accordingly.
  - If the series elements are not string-like (for example, numbers or None), callers should coerce to strings or filter non-string elements before calling; otherwise, path_summary may raise TypeError propagated through this function.

- Integration note:
  - Because this function mutates the provided summary dict in-place and returns it, callers that reuse the same summary object across multiple steps should be aware that subsequent updates will accumulate on the same dict instance.

