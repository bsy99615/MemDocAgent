# `render_image.py`

## `src.ydata_profiling.report.structure.variables.render_image.render_image` · *function*

## Summary
Renders HTML template variables for image-type variables by extending file variable rendering with image-specific analytics and visualizations.

## Description
The `render_image` function generates report template variables specifically for image data types. It builds upon the file variable rendering infrastructure by adding image-specific statistical information including dimensions, scatter plots, and frequency distributions. This function is called during report generation when processing columns identified as containing image data.

The function leverages the existing `render_file` infrastructure to establish the basic file variable structure, then enhances it with image-specific components such as dimension statistics, size scatter plots, and optionally EXIF metadata analysis. This approach ensures consistency with the broader reporting framework while providing specialized insights for image data.

## Args
    config (Settings): Configuration object containing report settings including:
        - `n_freq_table_max`: Maximum number of entries to display in frequency tables
        - `plot.image_format`: Format for generated plots (png, svg, etc.)
        - `vars.cat.redact`: Flag indicating whether sensitive categorical data should be redacted
        - `report.precision`: Number of significant digits for numeric formatting
        - `html.style`: Styling configuration for report elements
    summary (dict): Dictionary containing image variable statistics with the following required keys:
        - "varid": Variable identifier
        - "min_width", "median_width", "max_width": Width dimension statistics
        - "min_height", "median_height", "max_height": Height dimension statistics
        - "min_area", "median_area", "max_area": Area dimension statistics
        - "image_dimensions": Series containing width-height pairs for scatter plot
        - "n": Total count of observations
        - "exif_keys_counts" (optional): Frequency counts for EXIF keys
        - "exif_data" (optional): Dictionary of EXIF data series
        - Other keys required by underlying rendering functions

## Returns
    dict: Template variables dictionary containing:
        - All template variables from `render_file` extended with image-specific components
        - Updated "var_type" field in the top section set to "Image"
        - An "Image" tab in the bottom section containing:
          * Dimensions overview with width, height, and area statistics in tabular format
          * Scatter plot of image sizes showing width vs height relationships
          * Frequency table of common image dimensions
          * Optional EXIF data analysis if available, including EXIF keys and detailed EXIF data
        - All other standard template variables for HTML report rendering

## Raises
    KeyError: When required keys are missing from the summary dictionary (e.g., "varid", dimension statistics, "image_dimensions", "n", etc.)

## Constraints
    Preconditions:
        - The summary dictionary must contain "varid" key
        - The summary dictionary must contain dimension statistics keys (min_width, median_width, max_width, min_height, median_height, max_height, min_area, median_area, max_area)
        - The summary dictionary must contain "image_dimensions" key with width-height pairs as tuples
        - The summary dictionary must contain "n" key with total observation count
        - Config must contain required settings for rendering
        - If EXIF data is present, "exif_keys_counts" and "exif_data" keys must be present with valid data structures

    Postconditions:
        - Returns a complete template variables dictionary ready for HTML rendering
        - The returned dictionary maintains the same structure as `render_file`
        - Image-specific tabs are properly added to the bottom container
        - The var_type in the top section is set to "Image"

## Side Effects
    None - This function is pure and does not modify external state or perform I/O operations

## Control Flow
```mermaid
flowchart TD
    A[Start render_image] --> B[Extract varid, n_freq_table_max, redact from config and summary]
    B --> C[Call render_file to get base template variables]
    C --> D[Set var_type to "Image" in top section]
    D --> E[Initialize empty image_items list]
    E --> F[Create image_shape_items with dimension tables]
    F --> G[Create Container for image_shape_items]
    G --> H{exif_keys_counts in summary?}
    H -->|Yes| I[Create EXIF frequency tables from exif_data]
    I --> J[Append EXIF container to image_items]
    H -->|No| K[Skip EXIF processing]
    K --> L[Append image_shape container to image_items]
    L --> M[Create Container with image_items as tabs]
    M --> N[Append image_tab to template_variables["bottom"]["content"]["items"]]
    N --> O[Return template_variables]
```

## Examples
```python
# Basic usage for image variable report generation
config = Settings()
summary = {
    "varid": "image_var_1",
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
    "exif_keys_counts": {"Make": 50, "Model": 40},
    "exif_data": {
        "Make": pd.Series(["Canon", "Nikon", "Canon"]),
        "Model": pd.Series(["EOS 5D", "D850", "EOS 5D"])
    }
}

template_vars = render_image(config, summary)
# Returns complete template variables with image-specific tabs added to bottom section
```

