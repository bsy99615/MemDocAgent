# `render_image.py`

## `src.ydata_profiling.report.structure.variables.render_image.render_image` · *function*

## Summary
Generates report template variables for image-type variables by constructing visualizations and statistical summaries of image properties including dimensions, file sizes, and EXIF metadata.

## Description
Processes image variable summary data to build presentation-ready template variables containing image-specific visualizations and statistics. This function extends the file variable rendering by adding detailed image analysis including dimension statistics, scatter plots of image sizes, frequency distributions of common dimensions, and EXIF metadata analysis when available.

The function is called during report generation when processing image-type variables, specifically when the variable summary contains image-related metadata such as dimensions, file sizes, and EXIF data. It leverages existing rendering utilities and follows the same pattern as other variable-specific render functions in the system.

## Args
    config (Settings): Configuration object containing report settings including plot formats, frequency table limits, and styling preferences
    summary (dict): Dictionary containing image variable summary data including image dimensions, file sizes, and metadata. Expected keys include 'varid', 'min_width', 'median_width', 'max_width', 'min_height', 'median_height', 'max_height', 'min_area', 'median_area', 'max_area', 'image_dimensions', and optionally 'exif_keys_counts' and 'exif_data'

## Returns
    dict: Template variables dictionary containing updated presentation structure with image-specific tabs and visualizations. The returned dictionary is a modified version of the template variables produced by render_file, with additional image-specific content appended to the bottom section.

## Raises
    None explicitly raised

## Constraints
    Preconditions:
        - summary dictionary must contain 'varid' key for anchor ID generation
        - config must contain valid n_freq_table_max and plot.image_format settings
        - summary must contain dimension-related keys ('min_width', 'median_width', 'max_width', 'min_height', 'median_height', 'max_height', 'min_area', 'median_area', 'max_area')
        - summary must contain 'image_dimensions' key with Series data for scatter plot generation
        - config must contain valid html.style and plot.image_format configurations

    Postconditions:
        - Returns a complete template_variables dictionary ready for report rendering
        - The returned dictionary maintains the structure expected by the report generation system
        - Image-specific tabs are properly integrated into the existing template structure
        - The template_variables dictionary is modified in-place with new content added to the bottom section

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Start render_image] --> B[Extract varid, n_freq_table_max, redact from config and summary]
    B --> C[Call render_file(config, summary) for base template]
    C --> D[Set var_type to "Image" in template_variables["top"]["items"][0]["content"]]
    D --> E[Initialize empty image_items list]
    E --> F[Create image_shape_items with dimension tables]
    F --> G[Create image_shape Container with image_shape_items]
    G --> H{exif_keys_counts in summary?}
    H -- Yes --> I[Create EXIF frequency tables]
    I --> J[Add EXIF Container to image_items]
    H -- No --> J
    J --> K[Add image_shape to image_items]
    K --> L[Create image_tab Container with image_items]
    L --> M[Append image_tab to template_variables["bottom"]["items"]]
    M --> N[Return template_variables]
```

## Examples
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "varid": "image_001",
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
    "n_freq_table_max": 10
}

template_vars = render_image(config, summary)
# Returns template variables with image-specific tabs added to bottom section
```

