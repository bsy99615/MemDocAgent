# `table_spark.py`

## `src.ydata_profiling.model.spark.table_spark.spark_get_table_stats` · *function*

## Summary:
Aggregates table-level statistics from a PySpark DataFrame and a precomputed per-variable statistics mapping, returning counts, missing-value metrics and a type distribution.

## Description:
This function computes basic table-level metrics necessary for profiling a Spark DataFrame:
- It determines the number of rows and variables from the provided DataFrame.
- It aggregates missing-value counts and counts of variables containing missing values using the supplied variable-level summaries.
- It computes the proportion of missing cells across the whole table and tallies variable types.

Known callers within the provided context:
- No direct callers were provided in the preloaded context. Typically, this function is invoked by a Spark-based profiling pipeline after per-variable statistics have been computed, to assemble and return table-level statistics for reporting.

Why this logic is a separate function:
- Responsibility separation: it centralizes the aggregation logic for table-level metrics (counts, missingness, and type distribution) so variable-level statistics can be computed independently (possibly in distributed fashion) and then summarized in one place.
- Reusability: callers that compute variable_stats (possibly by different backends) can reuse this function to produce a consistent table-level output.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Purpose: Accepted for API compatibility with other backends/pipelines. This implementation does not read or modify config; it is kept to match a common function signature.
    df (pyspark.sql.DataFrame):
        - Type: PySpark DataFrame
        - Requirements: Must expose a count() method that returns the number of rows (non-negative integer) and a columns attribute (sequence of column names) whose length is the number of variables.
        - Note: Calling df.count() triggers a Spark job to compute the number of rows; this can be expensive.
    variable_stats (dict):
        - Type: mapping (str -> dict)
        - Expected shape for each value (series_summary):
            * Optional key "n_missing": integer >= 0 representing the number of missing values for that variable.
            * Required key "type": any hashable value representing the variable's type/category (this function uses it for counting).
        - Interdependencies: The function uses series_summary["n_missing"] only when the "n_missing" key is present. It requires "type" to be present for every variable; missing "type" will raise a KeyError.

## Returns:
    dict: A dictionary containing table-level statistics with the following keys:
        - "n" (int): Number of rows in df (value returned by df.count()).
        - "n_var" (int): Number of variables (len(df.columns)).
        - "p_cells_missing" (float): Proportion of missing cells across the table computed as n_cells_missing / (n * n_var) when n * n_var > 0, else 0. (Guard ensures division by zero is avoided.)
        - "n_cells_missing" (int): Total number of missing cells aggregated from variable_stats where "n_missing" is present.
        - "n_vars_all_missing" (int): Count of variables where n_missing == n (all rows missing for that variable).
        - "n_vars_with_missing" (int): Count of variables with > 0 missing values.
        - "types" (dict): A mapping type_value -> count of variables of that type (created using collections.Counter over series_summary["type"] for all variables).

    Edge-case returns:
        - If df has zero rows or zero columns (so n * n_var == 0), "p_cells_missing" is returned as 0.
        - If variable_stats is empty, missing-related counts are zero and "types" will be an empty dict.

## Raises:
    - AttributeError:
        - Condition: If df does not provide count() or columns, an AttributeError will be raised when attempting df.count() or accessing df.columns.
    - TypeError:
        - Condition: If variable_stats is not iterable/has no .values() method or if a series_summary is not a mapping when the code expects dictionary-like lookup.
    - KeyError:
        - Condition: If any series_summary in variable_stats.values() lacks the "type" key, the list comprehension that builds the types list will raise KeyError for "type".
    - ValueError / other exceptions from underlying Spark:
        - Condition: df.count() may raise exceptions propagated from Spark (e.g., due to failed computation, unavailable cluster).

## Constraints:
    Preconditions:
        - df must be a valid PySpark DataFrame (supporting count() and columns).
        - variable_stats should be a mapping of variable identifiers to dictionaries; each variable's dict should include a "type" key whose value is hashable.
    Postconditions:
        - The returned dict will always contain the keys: "n", "n_var", "p_cells_missing", "n_cells_missing", "n_vars_all_missing", "n_vars_with_missing", and "types".
        - No global state or input objects are mutated by this function.

## Side Effects:
    - Spark action: Calling df.count() executes a Spark job (Action) that can be expensive and incur network/I/O and cluster computation.
    - No file, network, stdout writes, database updates, or global variable mutations are performed by this function directly.

## Control Flow:
flowchart TD
    Start["Start: call spark_get_table_stats(config, df, variable_stats)"]
    A[Compute n = df.count()]
    B[Set result.n_var = len(df.columns)]
    C[Init table_stats counters = 0]
    D[For each series_summary in variable_stats.values()]
    E{Does series_summary contain "n_missing" and n_missing > 0?}
    F[Increment n_vars_with_missing; add n_missing to n_cells_missing]
    G{Is n_missing == n?}
    H[Increment n_vars_all_missing]
    I[After loop compute p_cells_missing if n * n_var > 0 else 0]
    J[Set result fields from table_stats]
    K[Compute types = Counter(v["type"] for v in variable_stats.values())]
    End["Return result dict"]

    Start --> A --> B --> C --> D
    D --> E
    E -- yes --> F --> G
    G -- yes --> H --> D
    G -- no --> D
    E -- no --> D
    D --> I --> J --> K --> End

## Examples:
Assume a small Spark DataFrame df with 3 rows and two columns ["a", "b"], and variable_stats computed elsewhere:

    from ydata_profiling.config import Settings
    # config can be any Settings instance; not used here
    cfg = Settings()

    # Example variable_stats mapping:
    variable_stats = {
        "a": {"type": "Numeric", "n_missing": 1},
        "b": {"type": "Categorical", "n_missing": 0},
    }

    # Calling the function (df must be a pyspark.sql.DataFrame):
    stats = spark_get_table_stats(cfg, df, variable_stats)

    # Example returned dict (given df.count() == 3):
    # {
    #   "n": 3,
    #   "n_var": 2,
    #   "p_cells_missing": 1 / (3 * 2) = 0.1666...,
    #   "n_cells_missing": 1,
    #   "n_vars_all_missing": 0,
    #   "n_vars_with_missing": 1,
    #   "types": {"Numeric": 1, "Categorical": 1}
    # }

Error handling example:
    - If any series_summary omits the "type" key, a KeyError will be raised from the types computation. To guard:
        for v in variable_stats.values():
            v.setdefault("type", "Unknown")
    - Because df.count() triggers a Spark action, callers may wish to cache/persist df beforehand if they plan to inspect or compute other derived metrics.

