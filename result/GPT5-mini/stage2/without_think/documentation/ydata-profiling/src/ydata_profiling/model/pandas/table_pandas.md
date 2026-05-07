# `table_pandas.py`

## `src.ydata_profiling.model.pandas.table_pandas.pandas_get_table_stats` · *function*

## Summary:
Compute aggregate table-level statistics for a pandas DataFrame given per-variable summaries, returning counts (rows, variables), memory usage, missing-value metrics and a distribution of variable types.

## Description:
This function summarizes table-level metrics derived from a pandas DataFrame and a precomputed mapping of per-variable statistics. It is intended to be called as a step in a profiling pipeline that aggregates column-level summaries into a single table summary (for example, a table-profile generator or a higher-level get_table_stats routine in the profiling model). The logic is factored out to keep table-aggregation concerns separate from per-variable calculation: variable statistics are computed elsewhere and passed in so this function focuses only on assembling table-wide aggregates (row/column counts, memory footprint, missing-value totals, and a type distribution).

Known or expected callers (based on repository structure and typical profiling flow):
- Higher-level table profiling code that orchestrates per-variable profiling and table aggregation (e.g., module-level table stats aggregator). The file imports get_table_stats from ydata_profiling.model.table, indicating this function is part of the module's table-statistics implementation for pandas DataFrames and will be used by the profiling pipeline or a backend-dispatcher that selects pandas-specific logic.

Why this is a separate function:
- Separation of concerns: keeps table-level aggregation logic independent from the variable-level measurement routines.
- Reusability: multiple profiling entry points can reuse the same table-aggregation logic.
- Testability: simplifies unit testing of table-level metrics without recomputing variable-level statistics.

## Args:
    config (Settings): Profiling configuration object. Must have a boolean attribute memory_deep that is passed to pandas.DataFrame.memory_usage(deep=...).
    df (pandas.DataFrame): The DataFrame to summarize. If df.empty is True, the function treats the number of rows as 0 and avoids division by zero.
    variable_stats (dict): Mapping (usually column name -> dict) of per-variable summaries. Each value is expected to be a dictionary that may contain:
        - "n_missing" (int): number of missing cells for that variable (optional; only read if present).
        - "type" (hashable, e.g., str): variable type label used to compute the type distribution (required — missing "type" will raise a KeyError).
    Interdependencies:
        - variable_stats should correspond to, or at least reflect, the columns in df for accurate aggregates. The function iterates over variable_stats.values() (not df.columns) so extra or missing entries in variable_stats will affect the computed totals and type distribution.

## Returns:
    dict: A dictionary containing the aggregated table statistics with the following keys:
        - "n" (int): number of rows in df (0 when df.empty is True).
        - "n_var" (int): number of variables (columns) in df, i.e., len(df.columns).
        - "memory_size" (int): total memory usage in bytes computed as df.memory_usage(deep=config.memory_deep).sum().
        - "record_size" (float): average memory per record (memory_size / n) when n > 0, otherwise 0.
        - "n_cells_missing" (int): total number of missing cells across variables (sum of series_summary["n_missing"] for those variable entries where "n_missing" is present and > 0).
        - "n_vars_with_missing" (int): count of variables that have any missing values (n_missing > 0).
        - "n_vars_all_missing" (int): count of variables for which n_missing == n (entire column missing).
        - "p_cells_missing" (float): proportion of missing cells over total cells (n_cells_missing / (n * n_var)) when n>0 and n_var>0, otherwise 0.
        - "types" (dict): mapping from variable type label to occurrence count, produced by counting v["type"] for each v in variable_stats.values(). Example: {"Numeric": 5, "Categorical": 3}.
    Edge-case returns:
        - For empty DataFrame (n == 0): "record_size" is 0; "p_cells_missing" is 0 to prevent division by zero.
        - If variable_stats contains no entries, "n_cells_missing", "n_vars_with_missing", "n_vars_all_missing" will remain 0 and "types" will be an empty dict.

## Raises:
    KeyError:
        - If any series_summary in variable_stats.values() lacks the "type" key, the list comprehension that builds the types counter will raise a KeyError.
    AttributeError:
        - If config does not expose a memory_deep attribute expected by df.memory_usage(deep=config.memory_deep), accessing that attribute will raise an AttributeError.
    Any pandas-related exceptions propagated from df.memory_usage(...) are not caught and will propagate (e.g., if df is not a DataFrame and does not implement memory_usage).

## Constraints:
    Preconditions:
        - df must be a pandas.DataFrame or an object implementing the same memory_usage and columns/empty/len semantics.
        - config must be a Settings-like object with a boolean attribute memory_deep.
        - variable_stats must be an iterable mapping whose values are dict-like and ideally correspond to df's columns. Each value should contain "type" (required) and may contain "n_missing".
    Postconditions:
        - The returned dict contains the keys listed in Returns and provides consistent numeric aggregates computed from df and variable_stats.
        - No in-place modification of df or variable_stats occurs; the function is read-only with respect to its inputs.

## Side Effects:
    - No I/O (no file, network, or stdout/stderr output).
    - No mutation of global state.
    - Calls pandas DataFrame.memory_usage(deep=...) which queries in-memory sizes; this is a read-only operation on df.
    - No external service calls.

## Control Flow:
flowchart TD
    Start --> CheckEmptyDF{df.empty?}
    CheckEmptyDF -- False --> n = len(df)
    CheckEmptyDF -- True --> n = 0
    n --> memory_size[Compute memory_size = df.memory_usage(deep=config.memory_deep).sum()]
    memory_size --> record_size{n > 0?}
    record_size -- True --> record_size = memory_size / n
    record_size -- False --> record_size = 0
    record_size --> InitTableStats[Initialize table_stats counters (n_cells_missing, n_vars_with_missing, n_vars_all_missing = 0)]
    InitTableStats --> LoopVars[For each series_summary in variable_stats.values()]
    LoopVars --> HasNMissing{"'n_missing' in summary and > 0 ?"}
    HasNMissing -- Yes --> inc_n_vars_with_missing[Increment n_vars_with_missing]
    inc_n_vars_with_missing --> add_n_cells_missing[Add series_summary['n_missing'] to n_cells_missing]
    add_n_cells_missing --> AllMissingCheck{"series_summary['n_missing'] == n ?"}
    AllMissingCheck -- Yes --> inc_n_vars_all_missing[Increment n_vars_all_missing]
    AllMissingCheck -- No --> LoopVars
    HasNMissing -- No --> LoopVars
    LoopVars --> ComputePCells[Compute p_cells_missing if n>0 and n_var>0 else 0]
    ComputePCells --> TypesCalc[Compute types = Counter(v['type'] for v in variable_stats.values())]
    TypesCalc --> Return[Return table_stats]
    Return --> End

## Examples:
Example (illustrative usage; assumes variable-level stats already computed):
    # Given:
    #   config: a Settings instance with memory_deep = True
    #   df: a pandas DataFrame with shape (100, 5)
    #   variable_stats: {
    #       "col1": {"type": "Numeric", "n_missing": 0},
    #       "col2": {"type": "Categorical", "n_missing": 10},
    #       "col3": {"type": "Numeric", "n_missing": 100},  # fully-missing column
    #       "col4": {"type": "Datetime", "n_missing": 0},
    #       "col5": {"type": "Numeric"}  # no "n_missing" key present
    #   }
    # Calling the function returns a dict including:
    #   - "n": 100
    #   - "n_var": 5
    #   - "memory_size": <sum of df.memory_usage(deep=...)>
    #   - "record_size": memory_size / 100
    #   - "n_cells_missing": 110 (10 from col2 + 100 from col3)
    #   - "n_vars_with_missing": 2 (col2 and col3)
    #   - "n_vars_all_missing": 1 (col3)
    #   - "p_cells_missing": 110 / (100 * 5) = 0.22
    #   - "types": {"Numeric": 3, "Categorical": 1, "Datetime": 1}
    #
    # Error handling note:
    #   - If a series_summary is missing the "type" key, the types aggregation will raise a KeyError; callers should ensure variable_stats includes "type" for each variable.

