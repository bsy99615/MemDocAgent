# `render_path.py`

## `src.ydata_profiling.report.structure.variables.render_path.render_path` · *function*

## Summary:
Generates comprehensive HTML template variables for rendering path variable reports with detailed frequency distributions and statistics.

## Description:
This function orchestrates the creation of a complete path variable report by extending the categorical variable rendering with path-specific components. It processes path components (name, parent, suffix, stem, anchor) into frequency tables, creates an overview statistics table, and builds a tabbed interface for different path aspects. The function integrates seamlessly with the broader profiling report generation pipeline.

Known callers within the codebase:
- Called by the main profiling pipeline when processing path variables
- Triggered during report generation when path variable summaries are available
- Part of the variable-specific rendering chain that handles different data types differently

This logic is extracted into its own function rather than inlined because it encapsulates the specialized processing required for path data types, which have unique structural characteristics (file paths with components like name, parent directory, extension, etc.) that differ from regular categorical data.

## Args:
    config (Settings): Configuration object containing report settings including:
        - n_freq_table_max: Maximum number of frequency table entries to display
        - vars.cat.redact: Boolean flag indicating whether to redact sensitive information
        - report.precision: Precision setting for numeric formatting
        - html.style: HTML styling configuration
    summary (dict): Dictionary containing path variable statistics including:
        - varid: Variable identifier used for HTML anchor IDs
        - common_prefix: Common prefix among all paths
        - n_stem_unique: Count of unique stems
        - n_name_unique: Count of unique names
        - n_suffix_unique: Count of unique extensions
        - n_parent_unique: Count of unique parent directories
        - n_anchor_unique: Count of unique anchors
        - name_counts: Frequency counts for path names
        - parent_counts: Frequency counts for parent directories
        - suffix_counts: Frequency counts for file extensions
        - stem_counts: Frequency counts for file stems
        - anchor_counts: Frequency counts for anchors
        - n: Total count of observations

## Returns:
    dict: Template variables dictionary containing:
        - All template variables from render_categorical function
        - Additional path-specific variables including:
          * freqtable_name, freqtable_parent, freqtable_suffix, freqtable_stem, freqtable_anchor: Processed frequency tables for path components
          * Modified top section with var_type set to "Path" 
          * Extended bottom section with Path tab containing Overview and component frequency tables

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
        - config must be a valid Settings object with all required attributes
        - summary must contain all required keys for path variable analysis
        - All referenced keys in summary must be present and properly formatted
        - The summary must include path-specific counts for all components (name, parent, suffix, stem, anchor)
        - The summary must contain varid key for anchor ID generation

    Postconditions:
        - Returns a complete template_variables dictionary ready for HTML rendering
        - All returned containers are properly structured with correct sequence types
        - All HTML anchor IDs are properly prefixed with the variable ID
        - The variable type in the top section is set to "Path"
        - Path tab with all component frequency tables is appended to the bottom section
        - The structure maintains compatibility with the report generation framework

## Side Effects:
    None: This function is pure and does not modify external state or perform I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start render_path] --> B[Extract varid, n_freq_table_max, redact from config and summary]
    B --> C[Call render_categorical(config, summary)]
    C --> D[Initialize path component keys list]
    D --> E[Loop through path components (name, parent, suffix, stem, anchor)]
    E --> F[Generate freq_table for each component with n_freq_table_max limit]
    F --> G[Update template_variables with freqtable_ keys]
    G --> H[Set var_type to "Path" in top section]
    H --> I[Create path_overview_tab with Table of path statistics]
    I --> J[Create path_items list with overview tab and frequency tables]
    J --> K[Create path_tab Container with path_items]
    K --> L[Append path_tab to template_variables["bottom"]["content"]["items"]]
    L --> M[Return template_variables]
```

## Examples:
```python
# Basic usage in a profiling context
from ydata_profiling.config import Settings
from ydata_profiling.report.structure.variables.render_path import render_path

config = Settings()
summary = {
    "varid": "file_path_col",
    "common_prefix": "/home/user/",
    "n_stem_unique": 15,
    "n_name_unique": 20,
    "n_suffix_unique": 5,
    "n_parent_unique": 8,
    "n_anchor_unique": 1,
    "name_counts": pd.Series([10, 5, 3]),
    "parent_counts": pd.Series([8, 4, 2]),
    "suffix_counts": pd.Series([12, 3]),
    "stem_counts": pd.Series([15, 8, 2]),
    "anchor_counts": pd.Series([20]),
    "n": 30
}

template_vars = render_path(config, summary)
# Returns a complete template_variables dictionary with path-specific report structure
# The returned dictionary contains all categorical variables plus path-specific additions
# such as freqtable_* variables and the updated Path tab in the bottom section
```

