# `render_image.py`

## `src.ydata_profiling.report.structure.variables.render_image.render_image` · *function*

## Summary:
Generates HTML report components for image-type variables by creating structured presentation elements including dimension statistics, scatter plots, and EXIF data frequency tables.

## Description:
This function processes image variable summary data and constructs a hierarchical HTML report structure containing statistical information about image dimensions, visualizations, and metadata. It extends the base file rendering functionality by adding image-specific components while maintaining consistent report formatting patterns.

The function is designed to be called as part of the variable-specific rendering pipeline, where it receives configuration settings and summary statistics for image variables, then transforms them into presentation-ready components that can be rendered in HTML reports.

## Args:
    config (Settings): Configuration object containing report settings such as precision, image formats, and frequency table limits
    summary (dict): Dictionary containing image variable summary statistics including dimensions, file sizes, and EXIF metadata. Must contain keys: "varid", "min_width", "median_width", "max_width", "min_height", "median_height", "max_height", "min_area", "median_area", "max_area", "image_dimensions", "n"

## Returns:
    dict: Template variables dictionary containing the complete HTML report structure for image variables, with structure matching the expected format for HTML report generation. The dictionary contains "top" and "bottom" sections with properly formatted content for rendering. The "top" section has its var_type set to "Image", and the "bottom" section contains an "Image" tab with all image-related content.

## Raises:
    KeyError: If required keys are missing from the summary dictionary
    TypeError: If summary["image_dimensions"] is not a pandas Series or if other expected data types are not provided
    AttributeError: If config or summary objects don't have expected attributes

## Constraints:
    Preconditions:
    - summary dictionary must contain required keys: "varid", "min_width", "median_width", "max_width", "min_height", "median_height", "max_height", "min_area", "median_area", "max_area", "image_dimensions", "n"
    - config must be a valid Settings object with proper nested configurations
    - summary["image_dimensions"] must be a pandas Series with valid data
    - If "exif_keys_counts" is present, summary must also contain "exif_data" with appropriate structure
    
    Postconditions:
    - Returns a dictionary with properly structured template variables for HTML rendering
    - The returned dictionary maintains the structure expected by the HTML report generation system
    - All image-specific components are properly integrated into the report hierarchy
    - The "top" section has its var_type set to "Image"
    - The "bottom" section contains an "Image" tab with all image-related content

## Side Effects:
    None directly - but the function modifies the template_variables dictionary passed from render_file, which becomes part of the HTML report structure

## Control Flow:
```mermaid
flowchart TD
    A[Start render_image] --> B{Has exif_keys_counts?}
    B -- Yes --> C[Create Exif keys FrequencyTable]
    B -- No --> D[Skip Exif processing]
    C --> E[Process exif_data items]
    E --> F[Add Exif data Container]
    D --> F
    F --> G[Create image_shape_items]
    G --> H[Create Dimension Tables]
    H --> I[Create Scatter Plot Image]
    I --> J[Create Common Values FrequencyTable]
    J --> K[Create image_shape Container]
    K --> L[Add image_shape to image_items]
    L --> M[Create image_tab Container]
    M --> N[Append image_tab to template_variables["bottom"]]
    N --> O[Return template_variables]
```

## Examples:
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "varid": "img_001",
    "min_width": 100,
    "median_width": 200,
    "max_width": 300,
    "min_height": 150,
    "median_height": 250,
    "max_height": 350,
    "min_area": 15000,
    "median_area": 50000,
    "max_area": 105000,
    "image_dimensions": pd.Series([(100, 150), (200, 250)]),
    "n": 1000,
    "exif_keys_counts": {"make": 500, "model": 300},
    "exif_data": {"make": pd.Series(["Canon", "Nikon"]), "model": pd.Series(["EOS", "D750"])}
}

result = render_image(config, summary)
# Returns template_variables ready for HTML report generation
```

