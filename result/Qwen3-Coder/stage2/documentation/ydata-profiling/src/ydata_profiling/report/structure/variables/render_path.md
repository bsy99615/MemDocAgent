# `render_path.py`

## `src.ydata_profiling.report.structure.variables.render_path.render_path` · *function*

## Summary
Generates HTML report structure for path-type variables by extending categorical variable templates with path-specific frequency tables and overview statistics.

## Description
Creates a complete template variables dictionary for rendering path variable reports in HTML format. This function builds upon the standard categorical variable rendering by adding specialized path analysis components including frequency tables for path components (name, parent, suffix, stem, anchor) and an overview tab with path-specific statistics.

The function extracts path-related frequency information from the summary dictionary and integrates it into the existing categorical template structure. It specifically enhances the categorical report by adding path-specific analysis while maintaining compatibility with the standard report layout.

This logic is extracted into its own function to separate path-specific rendering concerns from general categorical rendering, enabling clean modularity in the variable reporting pipeline.

## Args
    config (Settings): Configuration object containing report settings including:
        - `n_freq_table_max`: Maximum number of frequency table entries to display
        - `vars.cat.redact`: Whether to redact sensitive information in frequency tables
        - `html.style`: HTML styling configuration
        - `report.precision`: Decimal precision for numeric formatting
    summary (dict): Dictionary containing path variable statistics including:
        - "varid": Variable identifier
        - "n": Total count of observations
        - "common_prefix": Common prefix among all paths
        - "n_stem_unique": Count of unique stems
        - "n_name_unique": Count of unique names
        - "n_suffix_unique": Count of unique extensions
        - "n_parent_unique": Count of unique parents/directories
        - "n_anchor_unique": Count of unique anchors
        - "{path_part}_counts": Frequency counts for each path component (name, parent, suffix, stem, anchor)
        - "freq_table_rows": Base frequency table rows from categorical rendering

## Returns
    dict: Template variables dictionary containing:
        - All keys from the categorical template variables
        - Additional keys for path-specific frequency tables: "freqtable_{name,parent,suffix,stem,anchor}"
        - Enhanced "top" section with variable type set to "Path"
        - Extended "bottom" section with a "Path" tab containing:
          * Overview tab with path statistics
          * Full frequency table
          * Stem frequency table
          * Name frequency table
          * Extension frequency table
          * Parent frequency table
          * Anchor frequency table

## Raises
    None explicitly raised - All potential errors are handled by underlying components

## Constraints
    Preconditions:
        - config must be a valid Settings object with properly initialized configurations
        - summary must contain all required keys for path variable analysis
        - Required keys include: "varid", "n", "common_prefix", "n_stem_unique", "n_name_unique", "n_suffix_unique", "n_parent_unique", "n_anchor_unique", and all "{path_part}_counts" keys
        - All frequency count dictionaries must be properly formatted

    Postconditions:
        - Returns a complete template variables dictionary ready for HTML rendering
        - All returned components are properly styled and anchored
        - The structure follows the expected report layout with top and bottom containers
        - Path-specific frequency tables are properly formatted and integrated

## Side Effects
    None - This function is pure and does not modify external state or perform I/O operations

## Control Flow
```mermaid
flowchart TD
    A[Start render_path] --> B[Extract config and summary values]
    B --> C[Call render_categorical for base template variables]
    C --> D[Initialize path component keys]
    D --> E[Loop through path components]
    E --> F{Process each path component}
    F --> G[Call freq_table for frequency table generation]
    G --> H[Store frequency table in template_variables]
    H --> I[Update top section with var_type = "Path"]
    I --> J[Create path overview table with statistics]
    J --> K[Build path_items list with overview and frequency tables]
    K --> L[Create path_tab Container with tabs]
    L --> M[Append path_tab to bottom section]
    M --> N[Return template_variables]
```

## Examples
```python
# Basic usage for path variable report generation
config = Settings()
summary = {
    "varid": "path_var_1",
    "n": 1000,
    "common_prefix": "/home/user/",
    "n_stem_unique": 50,
    "n_name_unique": 100,
    "n_suffix_unique": 10,
    "n_parent_unique": 25,
    "n_anchor_unique": 1,
    "name_counts": pd.Series([50, 30, 20], index=['file1.txt', 'file2.txt', 'file3.txt']),
    "parent_counts": pd.Series([800, 150, 50], index=['/home/user/documents/', '/home/user/pictures/', '/home/user/downloads/']),
    "suffix_counts": pd.Series([700, 200, 100], index=['.txt', '.jpg', '.pdf']),
    "stem_counts": pd.Series([600, 300, 100], index=['file1', 'file2', 'file3']),
    "anchor_counts": pd.Series([1000], index=['/home/user/']),
    "freq_table_rows": [...]
}

template_vars = render_path(config, summary)
# Returns complete template variables for HTML rendering with path-specific analysis
```

