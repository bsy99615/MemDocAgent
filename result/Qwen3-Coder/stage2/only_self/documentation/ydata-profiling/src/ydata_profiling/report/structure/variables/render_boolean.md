# `render_boolean.py`

## `src.ydata_profiling.report.structure.variables.render_boolean.render_boolean` · *function*

## Summary
Generates HTML template variables for rendering boolean variable reports with metadata, statistics, frequency tables, and optional visualization plots.

## Description
The `render_boolean` function is responsible for creating the complete presentation layer structure for boolean variable profiling reports. It combines metadata, statistical summaries, frequency distributions, and optional visualization elements into a structured template variables dictionary that can be consumed by the report generation system.

This function extracts boolean-specific information from the summary dictionary and organizes it into UI components including variable information, statistical tables, frequency tables, and conditional plots. The function is part of the variable-specific rendering pipeline that handles different data types differently.

The logic is extracted into its own function rather than being inlined because it handles the complete presentation logic for boolean variables, separating concerns between data summarization (handled by other components) and presentation formatting (handled here).

## Args
- config (Settings): Configuration object containing report settings including plot options, styling, and variable-specific configurations
- summary (dict): Dictionary containing pre-computed statistics and metadata about the boolean variable, including:
  - varid (str): Unique identifier for the variable
  - varname (str): Name of the variable
  - description (str): Variable description text
  - alerts (list): List of alert conditions detected for this variable
  - alert_fields (list): List of field names that triggered alerts
  - n_distinct (int): Number of distinct values
  - p_distinct (float): Percentage of distinct values
  - n_missing (int): Number of missing values
  - p_missing (float): Percentage of missing values
  - memory_size (int): Memory footprint in bytes
  - value_counts_without_nan (Union[pd.Series, List[pd.Series]]): Frequency counts for non-null values
  - value_counts_index_sorted (Union[pd.Series, List[pd.Series]]): Sorted frequency counts by index
  - n (int): Total number of observations

## Returns
- dict: Template variables dictionary containing:
  - "top" (Container): Top section with variable info, statistics table, and frequency table
  - "bottom" (Container): Bottom section with frequency table and optional plots
  - All keys from render_common function output including "freq_table_rows", "firstn_expanded", and "lastn_expanded"
  - Keys are always present with specific types as defined by the report presentation components

## Raises
- ValueError: When an invalid plot type is specified in config.plot.cat_freq.type (expected values are 'bar' or 'pie')
- KeyError: When summary dictionary is missing required keys (though this would be caught by earlier processing)

## Constraints
- Preconditions:
  - config must be a valid Settings object with properly initialized plot and html configurations
  - summary must contain all required keys for boolean variable analysis
  - summary["value_counts_without_nan"] must be either a pandas Series or list of pandas Series
  - summary["value_counts_index_sorted"] must be either a pandas Series or list of pandas Series
  - config.vars.bool.n_obs must be a valid integer
  - config.plot.image_format must be a valid image format string
- Postconditions:
  - Returns a dictionary with consistent structure for report generation
  - All UI components are properly instantiated with appropriate parameters
  - Conditional plotting logic respects config.plot.cat_freq.show and max_unique thresholds
  - The returned dictionary contains exactly the expected keys for report rendering

## Side Effects
- None directly observable (no file I/O, global state changes, or external service calls)
- The function relies on external functions that may have side effects (plot generation, formatting functions)

## Control Flow
```mermaid
flowchart TD
    A[Start render_boolean] --> B[Extract basic variables from summary/config]
    B --> C[Call render_common for base template variables]
    C --> D[Create VariableInfo component with varid, alerts, var_type="Boolean", var_name, description]
    D --> E[Create statistics Table with distinct, distinct%, missing, missing%, memory size]
    E --> F[Create FrequencyTableSmall with freq_table results]
    F --> G[Build top Container with info, table, fqm components]
    G --> H[Create FrequencyTable item with freq_table_rows]
    H --> I[Check plot conditions: show AND max_unique > 0]
    I -->|False| J[Skip plot creation, proceed to bottom container]
    I -->|True| K[Check if value_counts_without_nan is list]
    K -->|Yes| L[Create batch grid Container with multiple Image components]
    K -->|No| M[Create single Image component]
    L --> N[Add plots to bottom items]
    M --> N
    N --> O[Build bottom Container with tabs sequence_type]
    O --> P[Return template_variables dictionary]
```

## Examples
```python
# Basic usage with minimal configuration
config = Settings()
summary = {
    "varid": "bool_var_1",
    "varname": "is_active",
    "description": "Indicates if user is active",
    "alerts": [],
    "alert_fields": [],
    "n_distinct": 2,
    "p_distinct": 1.0,
    "n_missing": 5,
    "p_missing": 0.02,
    "memory_size": 1024,
    "value_counts_without_nan": pd.Series([95, 5], index=['True', 'False']),
    "value_counts_index_sorted": pd.Series([95, 5], index=['True', 'False']),
    "n": 100
}

template_vars = render_boolean(config, summary)
# Returns dictionary with 'top' and 'bottom' containers ready for report rendering
# The 'top' container includes VariableInfo, Table, and FrequencyTableSmall
# The 'bottom' container includes FrequencyTable and potentially Image components
```

