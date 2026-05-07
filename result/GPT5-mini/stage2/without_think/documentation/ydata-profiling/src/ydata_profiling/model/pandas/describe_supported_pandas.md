# `describe_supported_pandas.py`

## `src.ydata_profiling.model.pandas.describe_supported_pandas.pandas_describe_supported` · *function*

## Summary:
Compute and augment a statistics mapping with distinct/unique counts and proportions for a pandas Series, and return the unchanged config and series together with the augmented stats dictionary.

## Description:
Given a pre-computed series_description that contains at least the non-missing observation count and the value counts excluding NaN, this function derives:
- number of distinct values,
- proportion of distinct values relative to the non-missing count,
- whether every non-missing value is unique,
- number of unique values (values occurring exactly once),
- proportion of unique values.

Known callers and calling context:
- This function is intended to be invoked by the profiling/summary pipeline that describes pandas Series. Typical usage is after a preliminary description step has produced a mapping with keys such as "count" and "value_counts_without_nan". The function finalizes the per-series stats used in profiling reports or further aggregation.

Reason for extraction:
- Encapsulates a narrowly scoped, reusable computation (derivation of distinct/unique metrics) so multiple describers or pipeline stages can reuse the same logic without duplication. It enforces a clear boundary between "raw counts preparation" and "summary metric derivation".

## Args:
    config (Settings)
        - Type: ydata_profiling.config.Settings
        - Role: Pipeline configuration object passed through unchanged; returned for pipeline signature consistency.
    series (pd.Series)
        - Type: pandas.Series
        - Role: The series being described; returned unchanged.
    series_description (dict)
        - Type: dict
        - Required keys:
            * "count": integer-like — the number of non-missing (non-NaN) observations for this series.
            * "value_counts_without_nan": pandas.Series — counts per distinct value, computed excluding NaN (index = distinct values; values = occurrence counts).
        - Interdependencies:
            * Proportions (p_distinct, p_unique) are computed using "count". If "count" is zero, the function uses the code's fallback to avoid division by zero.

## Returns:
    Tuple[Settings, pd.Series, dict]
    - First element: the same config object provided as input (unchanged).
    - Second element: the same pandas Series provided as input (unchanged).
    - Third element: stats (dict) — the result dictionary containing:
        * Computed keys (present immediately after construction):
            - "n_distinct": int — len(value_counts_without_nan), number of distinct non-NaN values.
            - "p_distinct": numeric — distinct_count / count when count > 0 (float), otherwise 0 (an int in the code).
            - "is_unique": bool — True if every non-missing value is unique (n_unique == count and count > 0), otherwise False.
            - "n_unique": int — number of values that occur exactly once (count of entries in value_counts_without_nan equal to 1).
            - "p_unique": numeric — n_unique / count when count > 0 (float), otherwise 0 (an int in the code).
        * After computing these keys, the function merges the input series_description into stats via stats.update(series_description). This means any keys present in series_description will overwrite the computed keys in stats (series_description takes precedence).
    - Edge cases:
        * When count == 0: p_distinct and p_unique are assigned the literal 0 from the code (int); n_distinct and n_unique will be 0 if value_counts_without_nan is empty; is_unique will be False.
        * When value_counts_without_nan is empty: n_distinct == 0 and n_unique == 0.

## Raises:
    - KeyError:
        * If "count" or "value_counts_without_nan" are missing from series_description, accessing them will raise a KeyError.
    - TypeError / AttributeError:
        * If series_description["value_counts_without_nan"] is not a pandas.Series or an object supporting len(), .where(...), and .count(), attribute or type errors may be raised. The function assumes value_counts_without_nan behaves like pandas.Series of integer counts.
    - No custom exceptions are raised by this function.

## Constraints:
Preconditions:
    - series_description must include "count" (>= 0) and "value_counts_without_nan" (a counts Series excluding NaN).
    - The count value should correspond to the number of non-missing entries used to compute value_counts_without_nan; mismatches will lead to inaccurate proportions.

Postconditions:
    - The returned stats dict contains the computed keys described above, but any keys present in the input series_description will overwrite those computed keys.
    - No modifications are made to config or series objects.

## Side Effects:
    - None. The function performs in-memory computation only and does not perform I/O, logging, network access, or global state mutation.

## Control Flow:
flowchart TD
    Start --> ReadInputs
    ReadInputs --> GetCount["Read 'count' from series_description"]
    GetCount --> GetValueCounts["Read 'value_counts_without_nan' from series_description"]
    GetValueCounts --> DistinctCount["distinct_count = len(value_counts)"]
    DistinctCount --> UniqueCount["unique_count = value_counts.where(value_counts == 1).count()"]
    UniqueCount --> ComputeStats["Build stats dict with computed keys"]
    ComputeStats --> CheckCount{"count > 0 ?"}
    CheckCount -->|Yes| ComputeProportions["p_distinct = distinct_count / count\np_unique = unique_count / count\nis_unique = (unique_count == count) and True"]
    CheckCount -->|No| ZeroProportions["p_distinct = 0\np_unique = 0\nis_unique = False"]
    ComputeProportions --> Merge["stats.update(series_description)  (series_description overwrites computed keys)"]
    ZeroProportions --> Merge
    Merge --> Return["return (config, series, stats)"]
    Return --> End

## Examples (usage and error handling, described):
- Typical usage scenario (conceptual):
    1. A profiling pipeline computes a preliminary description for a pandas Series: it determines the non-missing count and builds value_counts_without_nan as the counts per distinct non-NaN value.
    2. The pipeline calls this function, which returns the passed-through config and series plus a stats dict augmented with distinct/unique metrics.
    3. The pipeline then formats or aggregates stats for reporting.

- Handling missing keys:
    - If the calling code cannot guarantee that series_description contains the required keys, it should either compute them before calling this function or catch KeyError and handle the series appropriately (for example, skip this summarizer or recompute the missing entries).

- Typical edge cases:
    - Series with only NaNs: count == 0 and value_counts_without_nan empty -> n_distinct = 0, n_unique = 0, p_distinct = 0, p_unique = 0, is_unique = False.
    - Every non-missing value distinct: n_unique == count -> is_unique will be True (provided count > 0) and p_unique will be 1.0.

