# `render_path.py`

## `src.ydata_profiling.report.structure.variables.render_path.render_path` · *function*

## Summary:
Processes path-type variable data and generates template variables for report rendering with frequency tables and overview statistics.

## Description:
This function handles the rendering of path-type variables in statistical reports by building comprehensive template variables that include frequency distributions for different path components (name, parent, suffix, stem, anchor) along with overview statistics about the path data.

The function leverages `render_categorical` as a base implementation and extends it with path-specific processing. It creates detailed frequency tables for each path component and organizes them in a tabbed interface within the report structure.

## Args:
    config (Settings): Configuration object containing report settings including frequency table limits and formatting options
    summary (dict): Dictionary containing path variable summary data including counts, unique values, and metadata

## Returns:
    dict: Template variables containing the structured data for rendering path-type variables in reports, including:
        - Base categorical rendering from render_categorical
        - Frequency tables for path components (freqtable_name, freqtable_parent, etc.)
        - Overview statistics table
        - Tabbed container with all path-related information

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
        - summary dictionary must contain required keys: "varid", "n", "common_prefix", "n_stem_unique", "n_name_unique", "n_suffix_unique", "n_parent_unique", "n_anchor_unique", and path component count keys
        - config must be a valid Settings object with proper nested configuration structure
    
    Postconditions:
        - Returns a dictionary with properly structured template variables for report generation
        - All path component frequency tables are properly formatted and limited by n_freq_table_max

## Side Effects:
    None explicitly mentioned in the function body

## Control Flow:
```mermaid
flowchart TD
    A[Start render_path] --> B{Call render_categorical}
    B --> C[Initialize variables]
    C --> D[Process path components]
    D --> E{Loop through keys}
    E --> F[Create freq_table for each component]
    F --> G[Update var_type to "Path"]
    G --> H[Create overview table]
    H --> I[Build path_items array]
    I --> J[Create path_tab Container]
    J --> K[Append path_tab to bottom.content.items]
    K --> L[Return template_variables]
```

## Examples:
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "varid": "path_var_1",
    "n": 1000,
    "common_prefix": "/home/user/",
    "n_stem_unique": 50,
    "n_name_unique": 100,
    "n_suffix_unique": 10,
    "n_parent_unique": 20,
    "n_anchor_unique": 5,
    "name_counts": {...},
    "parent_counts": {...},
    "suffix_counts": {...},
    "stem_counts": {...},
    "anchor_counts": {...}
}
template_vars = render_path(config, summary)
```

