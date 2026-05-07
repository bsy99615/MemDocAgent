# `render_file.py`

## `src.ydata_profiling.report.structure.variables.render_file.render_file` · *function*

## Summary:
Generates presentation-ready template variables for file-type variable summaries, including file size histograms and timestamp frequency tables.

## Description:
This function processes file variable summaries to create structured template variables for report generation. It builds upon the path rendering logic by adding file-specific visualizations and statistics. The function creates tabbed containers with file size histograms and frequency tables for file creation, access, and modification timestamps.

The logic is extracted into its own function to separate file-specific presentation concerns from general path rendering logic, maintaining clean responsibility boundaries in the reporting system.

## Args:
    config (Settings): Configuration object containing report settings like frequency table limits and image format preferences
    summary (dict): Dictionary containing file variable analysis results with keys including 'varid', 'histogram_file_size', 'file_size', 'file_created_time', 'file_accessed_time', 'file_modified_time', and 'n'

## Returns:
    dict: Template variables dictionary containing updated presentation structure with file-specific tabs appended to the bottom section. The returned dictionary maintains the same structure as the input from render_path but adds a "File" tab containing file size histogram and timestamp frequency tables.

## Raises:
    KeyError: When required keys ('varid') are missing from summary dictionary
    AttributeError: When accessing attributes on objects that don't exist in summary data
    TypeError: When histogram function receives unexpected data types

## Constraints:
    Preconditions:
    - summary dictionary must contain 'varid' key
    - config object must have valid n_freq_table_max and plot.image_format attributes
    - If file size data exists, summary must contain 'histogram_file_size' key with appropriate data structure
    - File date fields (file_created_time, file_accessed_time, file_modified_time) must be pandas Series objects when present
    
    Postconditions:
    - Returned dictionary contains properly structured template variables
    - File tabs are appended to template_variables["bottom"].content["items"]
    - The 'var_type' in template_variables["top"].content["items"][0].content is set to "File"
    - All file-related tabs are properly formatted as Container objects with sequence_type="tabs"

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_file] --> B[Extract varid from summary]
    B --> C[Call render_path for base template]
    C --> D[Set var_type to "File"]
    D --> E[Check if file_size exists in summary]
    E -->|Yes| F[Create Image with histogram]
    E -->|No| G[Skip histogram creation]
    F --> H[Add histogram to file_tabs]
    G --> H
    H --> I[Iterate through file dates]
    I --> J[Check if date field exists in summary]
    J -->|Yes| K[Create FrequencyTable]
    J -->|No| L[Skip frequency table]
    K --> M[Add frequency table to file_tabs]
    L --> M
    M --> N[Create Container with file_tabs]
    N --> O[Append file_tab to template_variables["bottom"]["items"]]
    O --> P[Return template_variables]
```

## Examples:
```python
# Basic usage with file size data
config = Settings()
summary = {
    "varid": "file_var_1",
    "histogram_file_size": ([1, 2, 3], [10, 20, 30]),
    "file_created_time": pd.Series([1, 2, 3]),
    "file_accessed_time": pd.Series([1, 2, 3]),
    "file_modified_time": pd.Series([1, 2, 3]),
    "n": 100
}
result = render_file(config, summary)
# Returns template variables with file tabs added to bottom section

# Usage without file size data
summary_no_size = {
    "varid": "file_var_2",
    "file_created_time": pd.Series([1, 2, 3]),
    "file_accessed_time": pd.Series([1, 2, 3]),
    "file_modified_time": pd.Series([1, 2, 3]),
    "n": 100
}
result = render_file(config, summary_no_size)
# Returns template variables with only timestamp frequency tables
```

