# `describe_text_pandas.py`

## `src.ydata_profiling.model.pandas.describe_text_pandas.pandas_describe_text_1d` · *function*

## Summary:
Produce a text-specific 1D summary for a pandas Series by casting values to strings, recording the first rows, and conditionally augmenting the provided summary dict with length, character, and word statistics derived from the Series' value counts.

## Description:
This function prepares and enriches a profiling summary for a text column. Typical callers and context:
- Called by higher-level text-description orchestrators in the profiling pipeline (for example, the pandas-backed describe_text_1d orchestration in the profiling module) when a column is being profiled as text.
- Invoked after a value-counts computation; it expects the caller to pass an initial "summary" dictionary which already contains "value_counts_without_nan".

Why this function is separated:
- It centralizes the data-type-specific transformations and conditional invocations of three non-trivial summarizers (length_summary_vc, unicode_summary_vc, word_summary_vc) and the histogram helper (histogram_compute). This isolates text-specific branching and ensures callers can treat profiling steps uniformly without inlining tokenization, Unicode grouping, or histogram logic.

## Args:
    config (Settings):
        - Profiling configuration object controlling which text analyses are enabled and histogram plotting parameters.
        - Must provide at least:
            * config.vars.text.length (truthy/falsey) — enable length summaries.
            * config.vars.text.characters (truthy/falsey) — enable character/Unicode summaries.
            * config.vars.text.words (truthy/falsey) — enable word summaries.
            * config.vars.cat.stop_words — list of stop words used when computing word summaries.
            * config.plot.histogram.* — used indirectly by histogram_compute via config.
        - If any expected attributes are missing, AttributeError may be raised by attribute access.

    series (pandas.Series):
        - The data column values to profile. The function casts this series to strings internally (equivalent to series.astype(str)) and returns the casted series.
        - Precondition: series should be convertible to strings; otherwise the cast may produce unexpected string representations (e.g., "nan" for NaN) but will not raise.

    summary (dict):
        - Mutable summary dictionary prepared by the caller that must include at least:
            * "value_counts_without_nan": a pandas.Series whose index is the unique observed values and whose values are the corresponding counts (numeric).
        - The function mutates/updates this dict in-place by adding keys described in Returns below.
        - If the required key is missing, a KeyError will be raised.

## Returns:
    Tuple[Settings, pandas.Series, dict]
    - config: the same Settings object passed in (returned for call-chain convenience).
    - series: the original pandas.Series coerced to string dtype (series.astype(str)).
    - summary: the mutated summary dict containing the new/updated keys described below.

    Summary dictionary updates performed by this function (keys that may be added or updated):
    - "first_rows" (pandas.Series): top 5 rows of the string-cast series (series.head(5)).
    - If config.vars.text.length is truthy:
        * All keys returned by length_summary_vc(value_counts) (e.g., "max_length", "min_length", "mean_length", "median_length", "length_histogram").
        * Additionally, a histogram entry named "histogram_length" created by histogram_compute; value is the numpy.histogram(...) tuple returned by histogram_compute (bins and counts or density as configured).
    - If config.vars.text.characters is truthy:
        * All keys returned by unicode_summary_vc(value_counts) (character-level aggregated counts and grouped series/dicts).
    - If config.vars.text.words is truthy:
        * Keys returned by word_summary_vc(value_counts, config.vars.cat.stop_words), typically {"word_counts": pandas.Series} or an empty dict when no tokens remain.

    Edge cases for return contents:
    - If "value_counts_without_nan" is empty, many added Series will be empty and numeric summaries may be NaN or may cause helper functions to raise (see Raises).
    - histogram_compute may return a histogram with weights=None in certain bin-reduction scenarios (when number of bins is adjusted), which affects the shape and meaning of the "histogram_length" entry.

## Raises:
    - KeyError:
        * If summary does not contain "value_counts_without_nan", the function will raise a KeyError on lookup.
    - AttributeError:
        * If config or expected attributes (config.vars.text.length, config.vars.cat.stop_words, config.plot.histogram, etc.) are missing or mis-typed, attribute access will raise AttributeError.
        * If value_counts is not a pandas.Series and .index/.values accessors or .astype calls are invalid, AttributeError/TypeError may occur.
    - Exceptions propagated from helpers:
        * length_summary_vc may raise ValueError (empty arrays for reductions), IndexError (weighted median on empty arrays), or TypeError/AttributeError for invalid input types; these propagate.
        * unicode_summary_vc may raise TypeError if value counts' index entries are not iterable (cannot be split into characters).
        * word_summary_vc may raise AttributeError/TypeError for incompatible input (non-string-like index entries) propagated from pandas operations.
        * histogram_compute may raise exceptions stemming from numpy (e.g., invalid inputs) though typical inputs from length_summary_vc are numeric arrays that are compatible.

## Constraints:
    Preconditions:
    - summary["value_counts_without_nan"] must be present and must be a pandas.Series where index entries represent textual values and values are numeric counts.
    - config must be a Settings-like object with nested attributes as described in Args.
    - Caller should decide how to handle NaNs in the original series before calling if that behavior matters; this function relies on the provided value_counts_without_nan to reflect the pre-filtering.

    Postconditions:
    - The returned series is the input series cast to string dtype.
    - The provided summary dict has been mutated in-place and now contains at least "first_rows" plus any additional keys produced by enabled analyzers (length, histogram_length, character summaries, word_counts).
    - The function does not return copies of the helpers' internal temporary objects beyond those inserted into summary.

## Side Effects:
    - In-place mutation of the provided summary dict: new keys are added/updated as described above.
    - No I/O operations (no file, network, or stdout).
    - No global state mutation.
    - Calls to helper functions perform in-memory computations and may allocate temporary pandas/numpy objects; these are local and returned via summary only.

## Control Flow:
flowchart TD
    Start([Start]) --> Cast[Cast series to str]
    Cast --> GetVC[Read value_counts = summary["value_counts_without_nan"]]
    GetVC --> IndexCast[Set value_counts.index = value_counts.index.astype(str)]
    IndexCast --> UpdateFirst[summary["first_rows"] = series.head(5)]
    UpdateFirst --> CheckLength{config.vars.text.length ?}
    CheckLength -- Yes --> CallLength[length_summary_vc(value_counts) -> update summary]
    CallLength --> CallHist[Compute histogram via histogram_compute(config, summary["length_histogram"].index.values, len(summary["length_histogram"]), name="histogram_length", weights=summary["length_histogram"].values)]
    CallHist --> Continue1
    CheckLength -- No --> Continue1
    Continue1 --> CheckChars{config.vars.text.characters ?}
    CheckChars -- Yes --> CallChars[summary.update(unicode_summary_vc(value_counts))]
    CallChars --> Continue2
    CheckChars -- No --> Continue2
    Continue2 --> CheckWords{config.vars.text.words ?}
    CheckWords -- Yes --> CallWords[summary.update(word_summary_vc(value_counts, config.vars.cat.stop_words))]
    CallWords --> Return
    CheckWords -- No --> Return
    Return([Return config, series, summary])

## Examples (usage patterns and expected outcomes):
1) Typical happy-path description
    - Preconditions: The caller has computed value_counts_without_nan = column.value_counts() and prepared a Settings config enabling specific text analyses.
    - What happens:
        * The function casts the series to strings and stores the top 5 rows in summary["first_rows"].
        * If length analysis is enabled, summary receives length statistics (max/min/mean/median) and a "length_histogram" Series; an additional "histogram_length" histogram (numpy histogram tuple) is added via histogram_compute.
        * If character analysis is enabled, summary receives character-level counts, grouped counts by Unicode block/script/category, and per-group character breakdowns from unicode_summary_vc.
        * If word analysis is enabled, summary receives token-weighted counts (word frequencies) in "word_counts" from word_summary_vc.

    - Expected result: The returned summary dict contains concrete Series/dicts appropriate for downstream visualization and metrics (first rows, numeric length stats, histograms, character and word counts).

2) Example error handling pattern (precondition violation)
    - Problem: Caller forgot to compute or pass "value_counts_without_nan" in summary.
    - Handling: Wrap call in try/except KeyError and either compute the value counts (series.value_counts()) and re-call or skip text profiling for this column.

3) Handling empty input
    - If value_counts_without_nan is empty:
        * "first_rows" will be the top 5 of the string-cast series (likely empty or short).
        * Helper functions may return empty Series/dicts or may raise helper-specific exceptions (e.g., reductions on empty arrays).
        * Best practice: caller should check for empty value_counts and either bypass text-specific summaries or accept that many returned entries will be empty/NaN.

Notes:
- This function delegates most algorithmic detail to its helper functions. For precise rules about how lengths, characters, words, and histograms are computed (weighted medians, block/script mapping, tokenization and stop-word filtering, bin selection), consult the component documentation for length_summary_vc, unicode_summary_vc, word_summary_vc, and histogram_compute.

