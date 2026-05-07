# `render_file.py`

## `src.ydata_profiling.report.structure.variables.render_file.render_file` · *function*

## Summary:
Generates report template variables for file-type variables by creating visualizations and frequency tables for file size and timestamps.

## Description:
Processes file variable summary data to construct presentation-ready template variables containing file-specific visualizations and statistics. This function extends the path variable rendering by adding file-specific information including file size histograms and frequency tables for creation, access, and modification timestamps. It integrates seamlessly with the existing report generation pipeline by building upon the path rendering infrastructure.

The function is called during the report generation phase when processing file-type variables, specifically when the variable summary contains file-related metadata. It leverages existing rendering utilities and follows the same pattern as other variable-specific render functions in the system.

## Args:
    config (Settings): Configuration object containing report settings including plot formats and frequency table limits
    summary (dict): Dictionary containing file variable summary data including file size histograms, timestamp data, and metadata. Expected keys include 'varid', 'file_size', 'file_created_time', 'file_accessed_time', 'file_modified_time', and 'histogram_file_size'

## Returns:
    dict: Template variables dictionary containing updated presentation structure with file-specific tabs and visualizations. The returned dictionary is a modified version of the template variables produced by render_path, with additional file-specific content appended to the bottom section.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - summary dictionary must contain 'varid' key for anchor ID generation
        - config must contain valid n_freq_table_max and plot.image_format settings
        - summary may optionally contain 'file_size', 'file_created_time', 'file_accessed_time', and 'file_modified_time' keys
        - summary must contain 'histogram_file_size' when 'file_size' key is present

    Postconditions:
        - Returns a complete template_variables dictionary ready for report rendering
        - The returned dictionary maintains the structure expected by the report generation system
        - File-specific tabs are properly integrated into the existing template structure
        - The template_variables dictionary is modified in-place with new content added to the bottom section

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_file] --> B[Extract varid from summary]
    B --> C[Call render_path(config, summary) for base template]
    C --> D[Set var_type to "File" in template_variables["top"]["items"][0]["content"]]
    D --> E[Get config settings n_freq_table_max and image_format]
    E --> F[Initialize empty file_tabs list]
    F --> G{file_size in summary?}
    G -- Yes --> H[Create Image histogram for file size]
    H --> I[Add histogram to file_tabs]
    G -- No --> I
    I --> J[Iterate over file dates: created, accessed, modified]
    J --> K{file_date_id in summary?}
    K -- Yes --> L[Create FrequencyTable for date]
    L --> M[Add FrequencyTable to file_tabs]
    K -- No --> N
    N --> O[Create Container with file_tabs as tabs]
    O --> P[Append Container to template_variables["bottom"]["items"]]
    P --> Q[Return template_variables]
```

## Examples:
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "varid": "file_001",
    "file_size": True,
    "histogram_file_size": ([1, 2, 3], [10, 20, 30]),
    "file_created_time": pd.Series([1, 2, 3]),
    "n": 100
}

template_vars = render_file(config, summary)
# Returns template variables with file-specific tabs added to bottom section
```

