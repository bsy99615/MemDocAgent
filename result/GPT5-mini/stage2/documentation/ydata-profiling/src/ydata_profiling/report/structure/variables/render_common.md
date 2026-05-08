# `render_common.py`

## `src.ydata_profiling.report.structure.variables.render_common.render_common` · *function*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Produce a dictionary of presentation-ready frequency and extreme-observation tables by delegating to the frequency-table presentation utilities and applying limits from the provided Settings.

## Description:
Maps values from a per-variable summary and a Settings object into the exact calls required by the presentation helpers freq_table and extreme_obs_table. The function does not perform numeric computations itself; it only:
- reads two integer limits from the provided Settings,
- reads three entries from the provided summary dict,
- calls freq_table and extreme_obs_table with those values,
- and returns a dict of the three helper results.

This extraction centralizes the mapping between summary keys and the presentation helpers so that callers receive consistent template variables without duplicating the call-site wiring.

## Args:
    config (Settings):
        - Type: Settings-like object.
        - Required attributes (accessed directly; no validation beyond attribute access):
            * n_extreme_obs (int): maximum number of entries to request from extreme_obs_table for top/bottom lists. Should be a non-negative integer.
            * n_freq_table_max (int): maximum number of explicit rows to request from freq_table. Should be a non-negative integer.
        - If these attributes are missing or not integers, AttributeError or TypeError will be raised at access time.

    summary (dict):
        - Type: dict
        - Required keys and expected shapes:
            * "value_counts_without_nan": pandas.Series or list[pandas.Series]
                - Forwarded as the freqtable argument to freq_table.
            * "value_counts_index_sorted": pandas.Series or list[pandas.Series]
                - Forwarded as the freqtable argument to extreme_obs_table for the "first n" (top) entries.
            * "n": int or list[int]
                - Forwarded as the n (denominator) argument to both freq_table and extreme_obs_table.
        - Interdependencies:
            * If freqtables are lists then "n" may also be a list; freq_table and extreme_obs_table implement the dispatching behavior for single vs. list inputs (zip semantics when both are lists).
            * The function does not attempt to coerce or validate shapes beyond passing them through to the helpers.

## Returns:
    dict with keys:
        - "freq_table_rows": list[list[dict]]
            - Value: the return value of freq_table(
                freqtable=summary["value_counts_without_nan"],
                n=summary["n"],
                max_number_to_print=config.n_freq_table_max
              )
            - Shape: outer list corresponding to single or batched inputs (singleton list if single-series input). Each inner list contains row-dictionaries produced by _frequency_table (e.g., label, width, count, percentage, n, extra_class).
        - "firstn_expanded": list[list[dict]]
            - Value: the return value of extreme_obs_table(
                freqtable=summary["value_counts_index_sorted"],
                number_to_print=config.n_extreme_obs,
                n=summary["n"]
              )
            - Shape: same outer/inner-list convention as extreme_obs_table's contract.
        - "lastn_expanded": list[list[dict]]
            - Value: the return value of extreme_obs_table(
                freqtable=summary["value_counts_index_sorted"][::-1],
                number_to_print=config.n_extreme_obs,
                n=summary["n"]
              )
            - Note: the input Series is reversed to select the bottom (least frequent) entries before delegating to extreme_obs_table.
    Edge-case returns:
        - If number_to_print == 0 or freqtables are empty, the corresponding inner lists may be empty lists; the outer list shape still follows helper behavior (singleton list for scalar input or one element per zipped pair for list inputs).

## Raises:
    - KeyError:
        - If summary is missing any of the required keys: "value_counts_without_nan", "value_counts_index_sorted", or "n".
    - AttributeError / TypeError:
        - If config lacks n_extreme_obs or n_freq_table_max, or those attributes are not accessible as integers.
        - If the objects passed as freqtables do not support the operations expected by freq_table/extreme_obs_table (e.g., not pandas.Series or list thereof).
    - ZeroDivisionError:
        - Can propagate from freq_table or extreme_obs_table if any denominator in summary["n"] equals 0 and a percentage computation divides by it.
    - Any exception raised by freq_table or extreme_obs_table will propagate unchanged.

## Constraints:
    Preconditions:
        - config must expose n_extreme_obs and n_freq_table_max as readable attributes (integers).
        - summary must be a dict containing the keys "value_counts_without_nan", "value_counts_index_sorted", and "n".
        - Values under those keys must conform to the types/shape conventions expected by freq_table and extreme_obs_table (pandas.Series or lists of Series, and int or list[int] denominators).
    Postconditions:
        - The function returns a dict with the three keys described in Returns.
        - The function does not mutate the summary or config objects.

## Side Effects:
    - None intrinsic: no I/O, no global state mutation, no network calls. Any side effects are those of the called helpers, which are pure in normal usage.
    - Exceptions from helpers propagate through this function.

## Control Flow:
flowchart TD
    Start --> ReadConfig[Read config.n_extreme_obs and config.n_freq_table_max]
    ReadConfig --> ReadSummary[Access summary["value_counts_without_nan"], summary["value_counts_index_sorted"], summary["n"]]
    ReadSummary --> CallFreq[freq_table(freqtable=value_counts_without_nan, n=summary["n"], max_number_to_print=n_freq_table_max)]
    CallFreq --> CallFirst[extreme_obs_table(freqtable=value_counts_index_sorted, number_to_print=n_extreme_obs, n=summary["n"])]
    CallFirst --> CallLast[extreme_obs_table(freqtable=value_counts_index_sorted[::-1], number_to_print=n_extreme_obs, n=summary["n"])]
    CallLast --> Assemble[Assemble dict {"freq_table_rows", "firstn_expanded", "lastn_expanded"}]
    Assemble --> Return[Return assembled dict]
    ReadSummary -->|missing key| RaiseKeyError[KeyError raised]
    CallFreq -->|helper error| PropagateError[Propagate helper exception]
    CallFirst --> PropagateError
    CallLast --> PropagateError

## Examples:
1) Single-series example (shapes only):
    - Inputs:
        * config.n_extreme_obs = 3
        * config.n_freq_table_max = 5
        * summary = {
            "value_counts_without_nan": pandas.Series([50, 30, 20], index=["a","b","c"]),
            "value_counts_index_sorted": pandas.Series([50, 30, 20], index=["a","b","c"]),
            "n": 100
          }
    - Behavior:
        * "freq_table_rows" is a singleton list: [ formatted_rows ] where formatted_rows is a list of up to 5 row dicts produced by freq_table.
        * "firstn_expanded" is a singleton list: [ top_3_rows ] produced by extreme_obs_table on the original Series.
        * "lastn_expanded" is a singleton list: [ bottom_3_rows ] produced by extreme_obs_table on the reversed Series.

2) Batched example (shapes only):
    - Inputs:
        * summary values are lists: "value_counts_without_nan" = [s1, s2], "value_counts_index_sorted" = [s1, s2], "n" = [100, 200]
        * config as above
    - Behavior:
        * "freq_table_rows" is a list with one element per zipped pair (min length of the lists): [ formatted_rows_s1, formatted_rows_s2 ].
        * "firstn_expanded" and "lastn_expanded" follow the same zipped/list semantics as extreme_obs_table.

3) Error handling snippet (pattern):
    - Validate presence of required summary keys and config attributes before calling to provide clearer errors or custom fallbacks (e.g., convert ZeroDivisionError into showing "N/A" percentages).

