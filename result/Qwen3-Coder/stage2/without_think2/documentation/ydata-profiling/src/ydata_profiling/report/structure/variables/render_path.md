# `render_path.py`

## `src.ydata_profiling.report.structure.variables.render_path.render_path` · *function*

## Summary:
Generates a comprehensive report structure for path-type variables by extending categorical variable rendering with path-specific metadata and frequency tables.

## Description:
Creates a complete presentation-ready structure for path variables in data profiling reports. This function builds upon the standard categorical variable rendering by adding path-specific analysis components including common prefix statistics, unique path component counts, and detailed frequency tables for different path parts (name, parent, suffix, stem, anchor).

The function is designed to be called during the report generation phase specifically for path variables. It extends the categorical rendering framework to incorporate path-specific metadata and organizes the data into a structured template_variables dictionary that can be consumed by downstream rendering components to generate the final HTML report.

This logic is extracted into its own function rather than being inlined in the categorical renderer because path variables require specialized processing for their hierarchical structure and component analysis that differs from general categorical variables.

## Args:
    config (Settings): Configuration object containing report settings including styling, frequency table limits, and categorical variable analysis options
    summary (dict): Dictionary containing pre-computed path variable statistics and metadata including:
        - varid (str): Unique identifier for the variable
        - n (int): Total count of observations
        - common_prefix (str): Most common directory path prefix
        - n_stem_unique (int): Count of unique path stems
        - n_name_unique (int): Count of unique path names
        - n_suffix_unique (int): Count of unique file extensions
        - n_parent_unique (int): Count of unique parent directories
        - n_anchor_unique (int): Count of unique anchors
        - name_counts (dict): Frequency counts of path names
        - parent_counts (dict): Frequency counts of parent directories
        - suffix_counts (dict): Frequency counts of file extensions
        - stem_counts (dict): Frequency counts of path stems
        - anchor_counts (dict): Frequency counts of anchors
        - freq_table_rows (list): Row data for full frequency table

## Returns:
    dict: Template variables dictionary containing structured report components organized into 'top' and 'bottom' sections with additional path-specific elements:
        - Includes all standard categorical template variables returned by render_categorical
        - Adds path-specific frequency tables for each path component (freqtable_name, freqtable_parent, etc.)
        - Updates variable type to "Path" in the top section
        - Appends path tab container to the bottom section with overview and component frequency tables

## Raises:
    KeyError: If summary dictionary is missing required keys for path-specific components
    AttributeError: If config object lacks required attributes or methods
    TypeError: If input parameters are not of expected types

## Constraints:
    Preconditions:
        - config must be a valid Settings object with properly initialized attributes
        - summary must contain all required keys for path variable metadata and statistics
        - All referenced configuration options must be properly initialized
    Postconditions:
        - Returns a dictionary with properly structured report components
        - All generated anchor IDs follow consistent naming conventions
        - Path-specific frequency tables are properly populated
        - Variable type is correctly set to "Path" in the top section

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_path] --> B[Extract config and summary values]
    B --> C[Call render_categorical for base categorical structure]
    C --> D[Initialize path component keys]
    D --> E{Loop through path components}
    E --> F[Generate freq_table for each path part]
    F --> G[Update var_type to "Path" in top section]
    G --> H[Create path overview table]
    H --> I[Create path_items list with overview and frequency tables]
    I --> J[Create path_tab container with tabs]
    J --> K[Append path_tab to bottom section]
    K --> L[Return template_variables]
```

## Examples:
```python
# Basic usage in report generation for path variables
config = Settings()
summary = {
    "varid": "path_var_1",
    "n": 1000,
    "common_prefix": "/home/user/",
    "n_stem_unique": 450,
    "n_name_unique": 320,
    "n_suffix_unique": 15,
    "n_parent_unique": 200,
    "n_anchor_unique": 5,
    "name_counts": {"file1.txt": 150, "file2.txt": 120},
    "parent_counts": {"/home/user/documents": 300, "/home/user/pictures": 250},
    "suffix_counts": {".txt": 400, ".jpg": 300},
    "stem_counts": {"file1": 150, "file2": 120},
    "anchor_counts": {"#section1": 50, "#section2": 30},
    "freq_table_rows": [["file1.txt", 150], ["file2.txt", 120]]
}

template_vars = render_path(config, summary)
# Returns structured template variables with path-specific report components
```

