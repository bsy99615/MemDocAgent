# `render_common.py`

## `src.ydata_profiling.report.structure.variables.render_common.render_common` · *function*

## Summary:
Generates common template variables for variable report rendering, including frequency tables and extreme observation displays.

## Description:
Creates standardized template variables used across different variable report types in the profiling system. This function centralizes the logic for preparing frequency distribution data and extreme observations for presentation, ensuring consistent data formatting regardless of the specific variable type being reported. It prepares data for rendering frequency tables and displaying extreme observations (both highest and lowest values) in variable reports.

## Args:
    config (Settings): Configuration object containing rendering parameters such as maximum frequency table entries (n_freq_table_max) and extreme observation limits (n_extreme_obs)
    summary (dict): Dictionary containing variable summary statistics with the following required keys:
        - "value_counts_without_nan": pandas Series with frequency counts indexed by values
        - "value_counts_index_sorted": pandas Series with frequency counts sorted by index values
        - "n": integer representing total count of observations

## Returns:
    dict: Template variables dictionary containing:
        - "freq_table_rows": Formatted frequency table data showing top frequency values with "Other values" grouping
        - "firstn_expanded": Top extreme observations sorted by value (highest frequencies first)
        - "lastn_expanded": Bottom extreme observations sorted by value (lowest frequencies first)

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - config must contain n_extreme_obs and n_freq_table_max attributes
        - summary must contain "value_counts_without_nan", "value_counts_index_sorted", and "n" keys
        - All referenced keys in summary must map to valid data structures (pandas Series, integers, etc.)
        - The value_counts_index_sorted series must be properly sorted

    Postconditions:
        - Returns a dictionary with exactly three keys: "freq_table_rows", "firstn_expanded", "lastn_expanded"
        - All returned values are properly formatted for template rendering
        - The "lastn_expanded" variable contains reversed sorted data from "value_counts_index_sorted"

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_common] --> B[Extract config values n_extreme_obs, n_freq_table_max]
    B --> C[Generate freq_table_rows using freq_table()]
    C --> D[Generate firstn_expanded using extreme_obs_table()]
    D --> E[Generate lastn_expanded using extreme_obs_table() with reversed data]
    E --> F[Return template_variables dict]
```

## Examples:
```python
# Typical usage in variable report generation
config = Settings()
summary = {
    "value_counts_without_nan": pd.Series([10, 5, 3], index=['A', 'B', 'C']),
    "value_counts_index_sorted": pd.Series([3, 5, 10], index=['C', 'B', 'A']),
    "n": 18
}
template_vars = render_common(config, summary)
# Returns dict with:
# - freq_table_rows: Formatted frequency table data
# - firstn_expanded: Top 3 observations by frequency
# - lastn_expanded: Bottom 3 observations by frequency (reversed order)
```

