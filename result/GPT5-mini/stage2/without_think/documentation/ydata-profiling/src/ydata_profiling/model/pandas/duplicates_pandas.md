# `duplicates_pandas.py`

## `src.ydata_profiling.model.pandas.duplicates_pandas.pandas_get_duplicates` · *function*

## Summary:
Compute summary metrics for duplicate rows over a subset of columns and return the top duplicate groups (by occurrence) as a DataFrame limited by a configurable head count.

## Description:
This function detects rows in the provided DataFrame that are duplicates with respect to the supplied supported_columns, aggregates identical combinations into groups with counts, computes summary metrics (number and proportion of duplicate groups), and returns the top groups ordered by their counts.

Known callers in the provided repository snapshot:
    - No direct callers were found in the provided snapshot.
    - Typical usage: invoked as part of a data-profiling pipeline's duplicate-detection stage to produce metrics and example duplicate groups for reporting.

Why this is a separate function:
    - Encapsulates pandas-specific duplicate-detection and grouping logic, including configuration-reading (head, key), collision-checking for the chosen count column name, and producing both compact metrics and a top-N grouped DataFrame so that callers do not duplicate this logic.

## Args:
    config (Settings)
        - Must expose the attributes accessed by this function under config.duplicates:
            * head (int): maximum number of duplicate groups to return (n_head). Treated as an integer; if head <= 0 the function skips computation and returns an empty metrics dict and None for the DataFrame.
            * key (str): the column name to use in the returned grouped DataFrame for the duplicate counts.
        - If config or config.duplicates is missing, attribute access will raise AttributeError.
    df (pd.DataFrame)
        - The pandas DataFrame to analyze.
        - Must be a valid pd.DataFrame. If len(df) == 0 and n_head > 0, the function returns zeroed metrics and None for the DataFrame.
    supported_columns (Sequence)
        - Sequence of column identifiers (typically strings or other pandas-acceptable column keys) used to define equality for duplication detection.
        - If falsy (e.g., empty list), the function will not perform duplicate computation and will return metrics with zeros and None for the DataFrame.
        - If any element refers to a non-existent column in df, pandas will raise KeyError when selecting/grouping.

Interdependencies:
    - The function requires that config.duplicates.key is not already a column name in df; otherwise it raises ValueError to avoid overwriting existing columns.

## Returns:
    Tuple[Dict[str, Any], Optional[pd.DataFrame]]
        - metrics (dict):
            * If config.duplicates.head <= 0: returns an empty dict {}.
            * If head > 0 and supported_columns truthy and len(df) > 0:
                - "n_duplicates" (int): number of distinct duplicate groups found (i.e., number of rows in the grouped duplicates DataFrame).
                - "p_duplicates" (float): proportion computed as n_duplicates / len(df).
            * If head > 0 but supported_columns falsy or len(df) == 0:
                - "n_duplicates": 0
                - "p_duplicates": 0.0
        - duplicates_df (pd.DataFrame | None):
            * When computed: a DataFrame with columns [*supported_columns, <duplicates_key>] where <duplicates_key> is config.duplicates.key; each row represents a unique combination across supported_columns and the number of original rows with that combination. The DataFrame is sorted descending by the duplicates count and contains at most head rows (nlargest).
            * Otherwise: None

Edge-case return behaviors:
    - For head <= 0: returns ({}, None).
    - For head > 0 but no supported_columns or empty df: returns ({"n_duplicates": 0, "p_duplicates": 0.0}, None).

## Raises:
    ValueError
        - Raised when config.duplicates.key is present in df.columns. Exact condition: if duplicates_key in df.columns, the function raises ValueError with guidance to rename the DataFrame column or change the duplicates.key setting.
    KeyError
        - May be raised by pandas if supported_columns references columns not present in df (during selection or groupby).
    AttributeError
        - If config or config.duplicates does not exist or does not expose head/key attributes, attribute access will raise AttributeError.

## Constraints:
Preconditions:
    - config must have a duplicates attribute with head (int) and key (str).
    - df must be a pandas DataFrame (pd.DataFrame).
    - supported_columns should be a sequence of valid column keys for df.

Postconditions:
    - If computation occurs, the returned metrics contain integer "n_duplicates" and float "p_duplicates", and the returned DataFrame (when present) is sorted by the duplicates count and contains at most head rows.
    - The input DataFrame object is not modified; the function constructs derived DataFrames. It refuses (via ValueError) to proceed if the configured duplicates key would overwrite an existing column.

## Side Effects:
    - No file, network, or stdout I/O.
    - No mutation of global state.
    - Interacts only with pandas in-memory operations.
    - May propagate pandas-raised exceptions (e.g., KeyError) to the caller.

## Control Flow:
flowchart TD
    Start --> CheckHead{config.duplicates.head > 0?}
    CheckHead -- No --> ReturnEmpty[Return {}, None]
    CheckHead -- Yes --> CheckSupported{supported_columns truthy AND len(df) > 0?}
    CheckSupported -- No --> ReturnZeroed[Return {"n_duplicates":0,"p_duplicates":0.0}, None]
    CheckSupported -- Yes --> GetKey[duplicates_key = config.duplicates.key]
    GetKey --> KeyInDF{duplicates_key in df.columns?}
    KeyInDF -- Yes --> RaiseValue[Raise ValueError]
    KeyInDF -- No --> MarkDuplicated[mask = df.duplicated(subset=supported_columns, keep=False)]
    MarkDuplicated --> Filter[df_filtered = df[mask]]
    Filter --> Group[group = df_filtered.groupby(supported_columns, dropna=False, observed=True).size().reset_index(name=duplicates_key)]
    Group --> ComputeMetrics[metrics["n_duplicates"]=len(group[duplicates_key]); metrics["p_duplicates"]=metrics["n_duplicates"]/len(df)]
    ComputeMetrics --> SelectTop[duplicates_df = group.nlargest(n_head, duplicates_key)]
    SelectTop --> ReturnResult[Return metrics, duplicates_df]

## Examples (usage pattern in prose):
    - Prepare configuration:
        * Ensure config.duplicates.head is an integer (e.g., 5) and config.duplicates.key is a string (e.g., "n_duplicates").
    - Call pattern:
        * If you want the top 5 duplicated groups by columns ["A", "B"], call pandas_get_duplicates(config, df, ["A", "B"]).
    - Handling outcomes:
        * If the returned duplicates_df is not None, it contains at most head rows with columns ["A", "B", "n_duplicates"] (or the name you configured).
        * Catch ValueError to detect a configuration collision where your chosen duplicates key already exists in df.columns.
        * Catch KeyError to detect invalid supported_columns referencing non-existent columns.
    - Typical integration:
        * Use metrics["n_duplicates"] and metrics["p_duplicates"] to report summary statistics in a profiling report; show duplicates_df as example rows to help users identify repeated data patterns.

Implementation hints (for reimplementation):
    - Use df.duplicated(subset=..., keep=False) to mark all rows that have at least one duplicate in the specified subset.
    - Use groupby(..., dropna=False, observed=True).size().reset_index(name=duplicates_key) to obtain counts per unique key combination (this treats NaNs as group keys).
    - Use DataFrame.nlargest(head, duplicates_key) to get the top groups by count.
    - Always check for collisions between duplicates_key and df.columns before constructing the grouped result to avoid silent overwrites.

