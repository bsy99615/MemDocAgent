# `frequency_table_utils.py`

## `src.ydata_profiling.report.presentation.frequency_table_utils._frequency_table` · *function*

## Summary:
Builds a presentation-ready list of rows (dictionaries) from a pandas Series of value counts, providing normalized widths, raw counts, percentages and optional aggregated "Other" and "(Missing)" rows for rendering frequency bars or tables.

## Description:
This helper converts a counts Series into the specific row format expected by the report presentation layer:
- It lists up to max_number_to_print top categories as explicit rows.
- If the tail of categories (those omitted) has a combined frequency larger than the first omitted category, it appends a single "Other values (k)" row where k is the number of omitted non-missing categories.
- If there are missing observations (n - sum(freqtable) > threshold), it appends a "(Missing)" row.

Known callers within the codebase:
- Presentation/reporting code that renders categorical or discrete variable frequency tables (value-distribution UI components). Exact call sites are not provided here but this function is used during the report generation pipeline when formatting frequency/value-distribution components.

Reason for extraction:
- Centralizes the formatting and decision rules (how many categories to print, aggregation into "Other", when to show missing) so rendering code can stay simple and consistent across variable types.

## Args:
    freqtable (pandas.Series):
        A pandas Series of counts indexed by label. Expected properties:
        - Values are numeric counts (typically integers >= 0).
        - The Series is expected to be sorted descending by count so that freqtable.iloc[0] is the most frequent category.
        - May contain NA labels or NA values; note freqtable.count() (used in this function) counts non-NA entries and differs from len(freqtable).
        - If empty (len(freqtable) == 0), the function returns an empty list.
    n (int):
        Total number of observations used as denominator to compute percentages. Expected to be an integer >= 0.
        - If n == 0, percentage calculations will raise ZeroDivisionError.
        - If sum(freqtable) > n, freq_missing will be negative; the function will still run but percentages and missing count may be semantically incorrect. Callers should ensure n >= sum(freqtable) for sensible results.
    max_number_to_print (int):
        Maximum number of top labels to include explicitly in the output.
        - If max_number_to_print > n, it is reduced (clamped) to n.
        - Negative values are not validated by the function; passing a negative value will use pandas slicing/indexing semantics (e.g., freqtable.iloc[0:negative] and freqtable.values[negative]) and can produce non-intuitive results. Use non-negative integers for predictable behavior.

Interdependencies:
- n is used both as the percentage denominator and to compute freq_missing = n - sum(freqtable). For correct semantics, callers should pass an n consistent with freqtable.

## Returns:
List[Dict[str, Any]]:
- Each dictionary in the returned list has the keys:
    - label: category label, or a string like "Other values (k)" or "(Missing)".
    - width: float = count / max_freq where max_freq is the maximum of (largest category count, aggregated other count, missing count). When max_freq > 0, width ∈ [0.0, 1.0].
    - count: numeric raw count for the row (int or float depending on freqtable dtype).
    - percentage: float = count / n (for "Other" row this is clamped with min(..., 1.0)).
    - n: int, the provided total sample size.
    - extra_class: presentation hint string: "" for normal rows, "other" for aggregated tail, "missing" for missing row.
- Empty list [] is returned when:
    - freqtable is empty (len(freqtable) == 0), or
    - the computed max_freq == 0 (no non-zero counts among top category, other, or missing).
- The returned rows include up to max_number_to_print explicit category rows, and may include up to one "Other values (k)" row and one "(Missing)" row depending on thresholds described below.

## Raises:
- ZeroDivisionError: If n == 0, the code computes float(freq) / n and float(freq_missing) / n and will raise ZeroDivisionError.
- IndexError or other exceptions are possible if freqtable has unexpected internal structure, but the implementation guards common out-of-range accesses by checking len(freqtable) before accessing freqtable.values[0] and by using the branch that sets min_freq = 0 when max_number_to_print >= len(freqtable).
- Errors from numpy/pandas operations may propagate (e.g., TypeError if freqtable values are non-numeric). The function does not coerce types.

## Constraints:
Preconditions:
- freqtable should represent counts; values should be numeric and non-negative for meaningful output.
- Prefer n >= sum(freqtable) and max_number_to_print >= 0.
Postconditions:
- If non-empty list returned, at least one row will have width == 1.0 (the row(s) with count == max_freq).
- The "percentage" fields are computed relative to the provided n; callers relying on these percentages must ensure n is correct.

## Side Effects:
- None (pure function). No I/O, no global state mutation.

## Control Flow:
flowchart TD
    A[Start] --> B{max_number_to_print > n?}
    B -- yes --> C[set max_number_to_print = n]
    B -- no --> D[keep max_number_to_print]
    C --> E{max_number_to_print < len(freqtable)?}
    D --> E
    E -- yes --> F[compute freq_other = sum(freqtable.iloc[max_number_to_print:]) and min_freq = freqtable.values[max_number_to_print]]
    E -- no --> G[set freq_other = 0 and min_freq = 0]
    F --> H[freq_missing = n - sum(freqtable)]
    G --> H
    H --> I{len(freqtable) == 0?}
    I -- yes --> J[return []]
    I -- no --> K[max_freq = max(freqtable.values[0], freq_other, freq_missing)]
    K --> L{max_freq == 0?}
    L -- yes --> M[return []]
    L -- no --> N[for each (label, freq) in freqtable.iloc[0:max_number_to_print]: append normal row]
    N --> O{freq_other > min_freq?}
    O -- yes --> P[compute other_count = str(freqtable.count() - max_number_to_print) and append "Other values" row with extra_class="other"]
    O -- no --> Q[skip "Other" row]
    P --> R{freq_missing > min_freq?}
    Q --> R
    R -- yes --> S[append "(Missing)" row with extra_class="missing"]
    R -- no --> T[skip "(Missing)" row]
    S --> U[return rows]
    T --> U

## Examples:
1) Typical top-N with no missing
- Input:
    freqtable = pandas.Series([50, 30, 20], index=['a','b','c'])
    n = 100
    max_number_to_print = 2
- Behavior:
    - max_number_to_print remains 2.
    - freq_other = sum(series.iloc[2:]) = 20
    - min_freq = freqtable.values[2] = 20
    - freq_missing = 100 - 100 = 0
    - max_freq = max(50, 20, 0) = 50
    - Top rows for 'a' and 'b' added. Since freq_other (20) is not > min_freq (20), no "Other values" row is appended. No "(Missing)" row because freq_missing (0) is not > min_freq (20).
- Output rows (conceptual):
    [
      {"label":"a","width":1.0,"count":50,"percentage":0.5,"n":100,"extra_class":""},
      {"label":"b","width":0.6,"count":30,"percentage":0.3,"n":100,"extra_class":""}
    ]

2) Aggregated other and missing
- Input:
    freqtable = pandas.Series([3, 2], index=['x','y'])
    n = 10
    max_number_to_print = 1
- Behavior:
    - freq_other = sum(series.iloc[1:]) = 2; min_freq = freqtable.values[1] = 2
    - freq_missing = 10 - 5 = 5
    - max_freq = max(3, 2, 5) = 5
    - Top row for 'x' added.
    - freq_other (2) is not > min_freq (2) so no "Other" row.
    - freq_missing (5) > min_freq (2) so "(Missing)" row appended.
- Output rows (conceptual):
    [
      {"label":"x","width":3/5,"count":3,"percentage":0.3,"n":10,"extra_class":""},
      {"label":"(Missing)","width":1.0,"count":5,"percentage":0.5,"n":10,"extra_class":"missing"}
    ]

3) Caution: inconsistent n
- If sum(freqtable) > n (e.g., freqtable sums to 12 but n == 10), freq_missing becomes negative. The function will still run but percentages and the "(Missing)" row may be nonsensical; callers should avoid passing inconsistent n.

## `src.ydata_profiling.report.presentation.frequency_table_utils.freq_table` · *function*

## Summary:
Wraps the core _frequency_table formatter to produce one or more presentation-ready frequency tables. Accepts either a single pandas Series and a single total n, or parallel lists of Series and n values, and returns a list of formatted frequency-table rows (one list per input Series).

## Description:
This function is a small dispatcher that normalizes inputs for the presentation pipeline:
- If both freqtable and n are lists, it processes them pairwise and returns a list where each element is the formatted frequency-table (a list of row dictionaries) for the corresponding Series.
- Otherwise, it treats the inputs as a single frequency table and total, calls the underlying _frequency_table helper, and returns a singleton list whose only element is that formatted frequency-table.

Known callers:
- Presentation/reporting code that renders categorical or discrete variable frequency tables (value-distribution UI components) during report generation. The function is used when the pipeline needs to produce the presentation-ready rows for one or several variables at once. Exact call sites are not provided here.

Why this logic is extracted:
- Separates input-shape handling (single vs batch) from the formatting logic implemented in _frequency_table.
- Keeps calling code concise: callers receive a consistent output shape (a list of formatted tables) regardless of whether they supplied one or many inputs.

## Args:
    freqtable (pandas.Series | list[pandas.Series]):
        - Either a single pandas.Series of counts (index = labels, values = counts) or a list of such Series.
        - If a single Series is passed, n must be a single int (see below).
        - If a list is passed, it is expected that n is a list of the same length; the function zips the two lists and processes pairs.
        - If only one of freqtable/n is a list (and the other is not), the function will follow the "else" branch and pass the list object unchanged to _frequency_table, which will likely raise or produce incorrect output. Callers should ensure matching shapes.

    n (int | list[int]):
        - If a single Series was passed, n should be an integer representing the total number of observations.
        - If freqtable is a list, n should be a list of integers with the same length where each integer matches the corresponding Series.
        - n is forwarded to _frequency_table and used as the denominator for percentage calculations; inconsistent values (e.g., n < sum(freqtable)) can produce semantically incorrect percentages.

    max_number_to_print (int):
        - Maximum number of explicit category rows to include for each Series.
        - Passed through to _frequency_table unchanged. Use non-negative integers for predictable results.

## Returns:
    list[list[dict[str, Any]]]:
        - A list containing the formatted frequency-table(s). Each element is itself a list of row dictionaries produced by _frequency_table.
        - When called with a single Series and int, the result is a singleton list: [formatted_rows].
        - When called with lists, the result length equals min(len(freqtable), len(n)) due to zip semantics: one formatted_rows list per zipped pair.
        - Each formatted_rows (an element of the outer list) is a list of dictionaries with keys defined by _frequency_table (e.g., label, width, count, percentage, n, extra_class).

## Raises:
    - Any exception raised by _frequency_table will propagate unchanged. In practice this commonly includes:
        - ZeroDivisionError: if n == 0 and percentage computations occur within _frequency_table.
        - TypeError / ValueError from numpy/pandas operations if the Series values are not numeric or have unexpected structure.
    - No additional exceptions are raised by freq_table itself; however, misuse of input shapes (e.g., passing a list for freqtable but an int for n) may cause downstream errors in _frequency_table.

## Constraints:
Preconditions:
    - For predictable behavior, either:
        * Provide a single pandas.Series as freqtable and a single int as n, or
        * Provide a list of pandas.Series and a list of ints of matching length.
    - Each pandas.Series should represent counts (numeric, non-negative) and be sorted descending by count if _frequency_table's semantics are to be preserved.
    - max_number_to_print should be a non-negative integer.

Postconditions:
    - The function returns a list whose elements are the formatted frequency-tables corresponding to the processed inputs.
    - No input objects are mutated by freq_table; it only forwards to _frequency_table and returns the results it produces.

## Side Effects:
    - None. This function performs no I/O and does not mutate global state. Any side effects would originate from the underlying _frequency_table (which is pure in normal usage).

## Control Flow:
flowchart TD
    A[Start] --> B{isinstance(freqtable, list) AND isinstance(n, list)?}
    B -- Yes --> C[zip(freqtable, n) -> pairs]
    C --> D[For each (series, n_i) call _frequency_table(series, n_i, max_number_to_print)]
    D --> E[Collect results into list_of_tables]
    E --> F[Return list_of_tables]
    B -- No --> G[Call _frequency_table(freqtable, n, max_number_to_print)]
    G --> H[Wrap result into singleton list [result]]
    H --> I[Return [result]]

Notes:
    - When both inputs are lists, zip truncates to the shorter list: only the first min(len(freqtable), len(n)) pairs are processed.
    - The function does not validate element types beyond the list check; invalid element types will be handled (or fail) inside _frequency_table.

## Examples:
1) Single Series (typical)
- Given a Series of counts and a total sample size:
  - freqtable = pandas.Series([50, 30, 20], index=['a', 'b', 'c'])
  - n = 100
  - max_number_to_print = 2
- Call:
  - result = freq_table(freqtable, n, max_number_to_print)
- Behavior:
  - result is a list with one element: result[0] is the formatted list of rows for that Series (top 2 rows plus any "Other"/"(Missing)" rows as decided by _frequency_table).

2) Batch processing (parallel lists)
- Given several Series and matching totals:
  - freqtables = [series1, series2, series3]
  - ns = [n1, n2, n3]
  - max_number_to_print = 5
- Call:
  - batch_result = freq_table(freqtables, ns, max_number_to_print)
- Behavior:
  - batch_result is a list of length min(len(freqtables), len(ns)); each element is the formatted rows for the corresponding series.

3) Common misuse to avoid
- Passing a list for freqtable but a single int for n will send the list object into _frequency_table (since the early isinstance check fails), which is not the intended use and will likely raise in _frequency_table. Ensure matched shapes (both lists or both scalars).

## `src.ydata_profiling.report.presentation.frequency_table_utils._extreme_obs_table` · *function*

## Summary:
Produces a list of presentation-ready rows for the top entries of a frequency Series, including normalized width, raw count, and percentage of a provided total.

## Description:
This helper takes the first number_to_print entries from a pandas Series of frequencies, computes a normalized width per entry relative to the maximum frequency among those selected entries, and returns a list of dictionaries with label, width, count, percentage, and auxiliary fields used by presentation templates.

Known callers in this repository snapshot:
- No direct callers were found in the provided code snapshot.
Typical usage context:
- Used by presentation/reporting code that needs a ready-to-render structure for frequency tables (e.g., the most/least frequent values in a profiling report). Keeping the normalization and formatting logic here prevents duplication in rendering templates.

Reason for being a separate function:
- Encapsulates slicing, normalization, and percentage calculation to separate data preparation concerns from templating/rendering, making the logic reusable and testable.

## Args:
    freqtable (pandas.Series):
        Series mapping labels (index) -> frequency counts (values). Values are expected to be numeric (e.g., int, numpy integer). The function uses freqtable.iloc[:number_to_print] to select entries, so ordering (e.g., descending frequency) should be applied by the caller if a top-N selection is intended.
    number_to_print (int):
        Number of entries to include from the start of freqtable. Uses pandas iloc slice semantics: freqtable.iloc[:number_to_print]. If number_to_print is larger than the series length, all entries are used. If number_to_print == 0 the function returns an empty list. Negative values follow pandas iloc slicing semantics (e.g., -1 excludes the last item); callers should normally pass a non-negative integer.
    n (int):
        Denominator used to compute percentage values (float(count) / n). Intended to be the total number of observations (commonly sum(freqtable) or the dataset length). Must be non-zero to avoid an exception.

Interdependencies:
- The percentage values are meaningful only if n corresponds to the same population used to produce freqtable (i.e., n == sum of frequencies or dataset size).

## Returns:
List[Dict[str, Any]]:
    A list where each element is a dictionary with these keys:
    - label (Any): The Series index label corresponding to the observation.
    - width (float): Normalized width for visual rendering, computed as freq / max_freq among the selected observations. If max_freq == 0, width == 0 for all rows.
    - count (numeric): The raw frequency value from the Series for that label.
    - percentage (float): float(count) / n. If count is NaN, percentage will be NaN. If n == 0 a ZeroDivisionError is raised instead of returning a value.
    - extra_class (str): Always an empty string (placeholder for presentation hooks).
    - n (int): The provided denominator, repeated for convenience.

Edge-case return behavior:
- If freqtable has fewer elements than number_to_print, rows are returned for all available elements.
- If number_to_print == 0, an empty list is returned.
- If max_freq == 0 (all selected counts are zero or NaN), width is set to 0 for all rows.
- If an entry's count is NaN, its percentage will be NaN and width will behave according to numeric propagation rules (NaN propagates).

## Raises:
    ZeroDivisionError:
        Raised when n == 0 during the percentage computation float(freq) / n.
Other possible exceptions:
    AttributeError or TypeError:
        If freqtable does not support .iloc or .items() (i.e., is not a pandas.Series or array-like with those methods), the function will raise a lower-level exception when attempting to slice or iterate.

## Constraints:
Preconditions:
    - freqtable must be a pandas.Series with numeric values for counts.
    - number_to_print should be an integer (preferably >= 0).
    - n must be a numeric denominator and must not be zero.
Postconditions:
    - Returned list length equals min(number_to_print, len(freqtable)) when number_to_print >= 0, or follows pandas iloc semantics for negative inputs.
    - For finite numeric max_freq > 0, every width is in the interval [0, 1].
    - Each row's percentage equals float(count) / n (subject to floating-point and NaN semantics).

## Side Effects:
    - No I/O is performed.
    - The input Series is not mutated.
    - No global state or external services are modified.

## Control Flow:
flowchart TD
    Start --> Slice[Slice freqtable: obs_to_print = freqtable.iloc[:number_to_print]]
    Slice --> Max[Compute max_freq = obs_to_print.max()]
    Max --> Iterate[For each (label, freq) in obs_to_print.items()]
    Iterate --> CheckMax{max_freq != 0?}
    CheckMax -->|Yes| ComputeWidth1[width = freq / max_freq]
    CheckMax -->|No| ComputeWidth0[width = 0]
    ComputeWidth1 --> ComputePct[percentage = float(freq) / n]
    ComputeWidth0 --> ComputePct
    ComputePct --> BuildRow[Build dict: label,width,count,percentage,extra_class,n]
    BuildRow --> Collect[Append to rows]
    Collect --> More{More items?}
    More -->|Yes| Iterate
    More -->|No| End[Return rows]
    NoteOverMax((If n == 0) leads to ZeroDivisionError during percentage computation)

## Examples:
1) Typical usage:
    freqtable = pandas.Series([10, 5, 0], index=["a", "b", "c"])  # ordered by frequency
    number_to_print = 2
    n = 15
    -> Returns two rows for "a" and "b" with widths [1.0, 0.5] and percentages [10/15, 5/15].

2) number_to_print == 0:
    number_to_print = 0
    -> Returns [] (empty list).

3) Handling NaN counts:
    If freqtable contains NaN for a label, that row's count will be NaN and percentage will be NaN.

4) Error case (caller should avoid or handle):
    If n == 0:
        Calling this function will raise ZeroDivisionError; callers should guard or set n appropriately before calling.

## `src.ydata_profiling.report.presentation.frequency_table_utils.extreme_obs_table` · *function*

## Summary:
Accepts either a single frequency Series or parallel lists of frequency Series and denominators, and returns presentation-ready rows for the most/least frequent observations by delegating to a helper that builds normalized width, raw count, and percentage fields.

## Description:
This function is a thin dispatcher that supports two input shapes:
- Single-series mode: when freqtable is a single pd.Series (not a list) and n is an int, it calls the helper to produce one list of presentation rows and returns it wrapped in a one-element outer list.
- Batched/list mode: when both freqtable and n are lists, it zips them and calls the helper for each pair, returning a list of lists (one per input series).

Known callers within this repository snapshot:
- No direct callers were found in the provided snapshot. Typical usage is from report/presentation code that needs per-column frequency tables prepared for rendering (e.g., generating top-k / bottom-k tables for profiling reports).

Why this function exists separately:
- It centralizes the logic for handling either a single frequency Series or a batch of Series + denominators and delegates the actual row construction and numeric computations to a dedicated helper (_extreme_obs_table). This avoids duplicating the list-vs-single branching logic across callers and keeps callers simpler.

## Args:
    freqtable (Union[pd.Series, List[pd.Series]]):
        - If a single pd.Series: a mapping label -> frequency count to be processed by the helper.
        - If a list: a list of pd.Series instances. Only supported when n is also a list.
        - Precondition: each pd.Series should have numeric frequency values and support .iloc and .items().

    number_to_print (int):
        - Number of entries to select from the start of each Series (slicing with .iloc[:number_to_print]).
        - If number_to_print is greater than the Series length, all entries are used.
        - If number_to_print == 0, the helper will return an empty list for that Series.
        - Follows pandas .iloc semantics for negative values; callers should normally pass a non-negative integer.

    n (Union[int, List[int]]):
        - If a single int: the denominator used to compute percentages for the single-series mode.
        - If a list: a list of ints corresponding one-to-one with freqtable when freqtable is a list.
        - Precondition: denominators must be non-zero to avoid ZeroDivisionError during percentage computation.

Notes on parameter interdependencies:
- If freqtable is a list, n must also be a list. When both are lists, this function zips them; any excess elements in the longer list are ignored because zip truncates to the shorter length.
- If one argument is a list and the other is not, behavior falls through to the single-series branch and will pass the raw list to the helper — this is not a supported use and will likely raise an exception; callers should provide consistent types (both lists or both non-lists).

## Returns:
List[List[Dict[str, Any]]]:
    - Outer list: one element per input Series when lists were passed, or a single element when a single Series was passed.
    - Inner list: the list of dictionaries produced by the helper (_extreme_obs_table); each dictionary represents a row with keys such as:
        - label: the Series index label
        - width: normalized width (freq / max_freq among selected entries, or 0 if max_freq == 0)
        - count: raw frequency value
        - percentage: float(count) / n
        - extra_class: presentation placeholder (empty string)
        - n: the denominator repeated for convenience
    - Edge/shape cases:
        - If both freqtable and n are lists, the outer list length equals min(len(freqtable), len(n)) because of zip truncation.
        - If single-series mode, outer list is length 1 and the inner list length equals min(number_to_print, len(freqtable)) (subject to pandas iloc semantics).

## Raises:
    - ZeroDivisionError:
        - Propagated from the helper if any provided denominator n == 0 (percentage computation uses float(freq) / n).
    - TypeError / AttributeError:
        - If freqtable is not a pd.Series (or a list of pd.Series when list mode is used), the helper or slicing operations (.iloc/.items()) will raise a lower-level exception.
    - No new exceptions are introduced by this dispatcher beyond those raised by the helper or by Python when argument types are inconsistent.

## Constraints:
Preconditions:
    - Caller must supply either:
        * a single pd.Series as freqtable and a single int as n, or
        * a list of pd.Series as freqtable and a list of int as n.
    - Each pd.Series must support .iloc and .items() and contain numeric counts.
    - number_to_print should be an int; negative values follow pandas iloc semantics but are uncommon.

Postconditions:
    - The return value is always a list of lists; even single-series input yields a one-element outer list.
    - No mutation of input Series occurs; function is side-effect-free.

## Side Effects:
    - None intrinsic to this function: no I/O, no global state mutation, no external calls.
    - Any exceptions raised originate from the helper or from Python's type system.

## Control Flow:
flowchart TD
    Start --> CheckLists{Is freqtable a list AND is n a list?}
    CheckLists -->|Yes| ZipLoop[Zip(freqtable, n) and for each pair call _extreme_obs_table]
    ZipLoop --> CollectList[Collect each helper result into outer list]
    CollectList --> End[Return outer list of helper results]
    CheckLists -->|No| SingleCall[Call _extreme_obs_table(freqtable, number_to_print, n)]
    SingleCall --> Wrap[Wrap helper result in single-element list]
    Wrap --> End

## Examples:
1) Single-series usage (typical):
    - freqtable: a pd.Series([10, 5, 0], index=["a", "b", "c"]) ordered by frequency
    - number_to_print: 2
    - n: 15
    - return: [ [ row_for_a, row_for_b ] ] where rows contain normalized width and percentage computed with n==15.

2) Batched usage:
    - freqtable: [series1, series2]
    - number_to_print: 3
    - n: [100, 200]
    - behavior: returns [rows_for_series1, rows_for_series2]; len of outer list == min(len(freqtable), len(n)).

3) Incorrect/mismatched types (caller error):
    - freqtable is a list but n is an int -> the function will not enter the zipped branch and will call the helper with a list as freqtable. Since the helper expects pd.Series, this will likely raise an AttributeError/TypeError; callers should avoid mixing types.

Implementation hints for re-creating behavior:
    - The function must check for the "both-list" condition using a runtime isinstance check on Python lists.
    - Use zip when both are lists to iterate pairs and map to the helper.
    - Otherwise, call the helper once and wrap its result in a one-element list.
    - Do not attempt to coerce or broadcast scalars to lists — the original intention is strict pairing or single-mode operation.

