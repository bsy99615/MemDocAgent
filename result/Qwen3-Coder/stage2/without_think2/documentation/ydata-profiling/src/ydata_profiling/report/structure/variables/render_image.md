# `render_image.py`

## `src.ydata_profiling.report.structure.variables.render_image.render_image` · *function*

## Summary:
Processes image variable summaries to generate presentation-ready template variables including dimension statistics, scatter plots, and EXIF data frequency tables.

## Description:
This function takes image variable analysis results and transforms them into structured template variables suitable for report generation. It builds upon the file rendering logic by adding image-specific visualizations and statistics. The function creates tabbed containers with dimension overview tables, scatter plots of image sizes, and frequency tables for common image dimensions and EXIF metadata.

The logic is extracted into its own function to separate image-specific presentation concerns from general file rendering logic, maintaining clean responsibility boundaries in the reporting system. This allows for specialized handling of image data while reusing common file rendering infrastructure.

## Args:
    config (Settings): Configuration object containing report settings including frequency table limits, image format preferences, and styling options
    summary (dict): Dictionary containing image variable analysis results with keys including 'varid', 'min_width', 'median_width', 'max_width', 'min_height', 'median_height', 'max_height', 'min_area', 'median_area', 'max_area', 'image_dimensions', and 'n'. May also contain 'exif_keys_counts' and 'exif_data' for EXIF metadata analysis.

## Returns:
    dict: Template variables dictionary containing updated presentation structure with image-specific tabs appended to the bottom section. The returned dictionary maintains the same structure as the input from render_file but adds an "Image" tab containing dimension statistics, scatter plots, and EXIF data frequency tables.

## Raises:
    KeyError: When required keys ('varid') are missing from summary dictionary
    AttributeError: When accessing attributes on objects that don't exist in summary data
    TypeError: When scatter_series function receives unexpected data types

## Constraints:
    Preconditions:
    - summary dictionary must contain 'varid' key
    - config object must have valid n_freq_table_max and plot.image_format attributes
    - summary must contain dimension statistics (min_width, median_width, max_width, min_height, median_height, max_height, min_area, median_area, max_area)
    - summary must contain 'image_dimensions' key with appropriate data structure for scatter plot generation
    - If EXIF data exists, summary must contain 'exif_keys_counts' and 'exif_data' keys with appropriate data structures
    
    Postconditions:
    - Returned dictionary contains properly structured template variables
    - Image tabs are appended to template_variables["bottom"].content["items"]
    - The 'var_type' in template_variables["top"].content["items"][0].content is set to "Image"
    - All image-related tabs are properly formatted as Container objects with sequence_type="tabs"

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_image] --> B[Extract varid, n_freq_table_max, redact from config/summary]
    B --> C[Call render_file for base template]
    C --> D[Set var_type to "Image"]
    D --> E[Create image_shape_items container]
    E --> F[Create dimension overview tables (width, height, area)]
    F --> G[Create scatter plot image]
    G --> H[Create frequency table for image dimensions]
    H --> I[Create image_shape Container]
    I --> J{Is exif_keys_counts in summary?}
    J -- Yes --> K[Create Exif keys frequency table]
    J -- No --> L[Skip EXIF processing]
    K --> M[Iterate through exif_data items]
    M --> N{Key is "exif_keys"?}
    N -- Yes --> O[Skip exif_keys entry]
    N -- No --> P[Create frequency table for exif key]
    O --> Q[Continue iteration]
    P --> Q
    Q --> R[Add EXIF frequency table to items]
    R --> S[Create EXIF data Container]
    S --> T[Append EXIF container to image_items]
    L --> U[Append image_shape to image_items]
    U --> V[Create image_tab Container]
    V --> W[Append image_tab to template_variables["bottom"]["items"]]
    W --> X[Return template_variables]
```

## Examples:
```python
# Basic usage with image data
config = Settings()
summary = {
    "varid": "img_var_1",
    "min_width": 100,
    "median_width": 200,
    "max_width": 300,
    "min_height": 150,
    "median_height": 250,
    "max_height": 350,
    "min_area": 15000,
    "median_area": 50000,
    "max_area": 105000,
    "image_dimensions": pd.Series([(100, 150), (200, 250), (300, 350)]),
    "n": 100
}
result = render_image(config, summary)
# Returns template variables with image tabs added to bottom section

# Usage with EXIF data
summary_with_exif = {
    "varid": "img_var_2",
    "min_width": 100,
    "median_width": 200,
    "max_width": 300,
    "min_height": 150,
    "median_height": 250,
    "max_height": 350,
    "min_area": 15000,
    "median_area": 50000,
    "max_area": 105000,
    "image_dimensions": pd.Series([(100, 150), (200, 250), (300, 350)]),
    "n": 100,
    "exif_keys_counts": {"make": 50, "model": 30},
    "exif_data": {
        "make": pd.Series(["Canon", "Nikon", "Sony"]),
        "model": pd.Series(["EOS 5D", "D850", "A7R"])
    }
}
result = render_image(config, summary_with_exif)
# Returns template variables with both dimension and EXIF tabs
```

