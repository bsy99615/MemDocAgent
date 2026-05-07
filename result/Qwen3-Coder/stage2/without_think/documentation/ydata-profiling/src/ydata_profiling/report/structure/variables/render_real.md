# `render_real.py`

## `src.ydata_profiling.report.structure.variables.render_real.render_real` · *function*

## Summary:
Generates HTML report structure for real number variable profiling, organizing statistical summaries, visualizations, and frequency distributions into a structured presentation format.

## Description:
The `render_real` function is responsible for creating the complete HTML report structure for real number variables in data profiling. It builds upon the common template variables provided by `render_common` and adds variable-specific information including descriptive statistics, quantile information, histograms, and frequency distributions. This function orchestrates the creation of multiple UI components to present comprehensive insights about real-valued data.

The function is part of the variable-specific rendering pipeline and is called during report generation when processing real number variables. It handles the organization of data into logical sections (top and bottom panels) and manages different histogram formats (list vs tuple) for visualization.

## Args:
    config (Settings): Configuration object containing report settings including HTML styling, image format preferences, and precision requirements for numeric formatting
    summary (dict): Dictionary containing comprehensive statistical summary of the real number variable with required keys:
        - "varid": Unique identifier for the variable
        - "varname": Human-readable name of the variable
        - "alerts": List of alert objects indicating issues with the variable
        - "description": Detailed description of the variable's purpose
        - "n_distinct": Count of distinct values
        - "p_distinct": Percentage of distinct values
        - "n_missing": Count of missing values
        - "p_missing": Percentage of missing values
        - "n_infinite": Count of infinite values
        - "p_infinite": Percentage of infinite values
        - "mean": Mean value of the variable
        - "min": Minimum value
        - "max": Maximum value
        - "n_zeros": Count of zero values
        - "p_zeros": Percentage of zero values
        - "n_negative": Count of negative values
        - "p_negative": Percentage of negative values
        - "memory_size": Memory consumption in bytes
        - "histogram": Histogram data (either list of tuples or tuple of arrays)
        - "5%": 5th percentile value
        - "25%": 25th percentile value (Q1)
        - "50%": 50th percentile value (median)
        - "75%": 75th percentile value (Q3)
        - "95%": 95th percentile value
        - "range": Difference between max and min
        - "iqr": Interquartile range
        - "std": Standard deviation
        - "cv": Coefficient of variation
        - "kurtosis": Kurtosis measure
        - "mad": Median absolute deviation
        - "skewness": Skewness measure
        - "sum": Sum of all values
        - "variance": Variance measure
        - "monotonic": Monotonicity indicator
        - "alert_fields": Set of field names that have triggered alerts

## Returns:
    dict: Template variables dictionary containing all components needed for rendering the real number variable report:
        - "top": Container with variable information, basic statistics tables, and mini histogram
        - "bottom": Container with detailed statistics, full histogram, frequency table, and extreme values

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - Config object must contain valid plot.image_format and html.style attributes
        - Summary dictionary must contain all required keys with appropriate data types
        - Histogram data in summary must be either a list of tuples or a tuple of arrays
        - All numeric values in summary must be valid numbers or NaN
        - Alert fields in summary must be a set of strings

    Postconditions:
        - Returns a dictionary with exactly two keys: "top" and "bottom"
        - Both "top" and "bottom" values are Container instances
        - All contained UI components are properly initialized with valid data
        - The returned dictionary is ready for template rendering

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_real] --> B[Extract varid and call render_common]
    B --> C[Initialize basic variables and components]
    C --> D[Create VariableInfo component]
    D --> E[Create first statistics Table]
    E --> F[Create second statistics Table]
    F --> G[Process histogram data (list vs tuple)]
    G --> H[Create mini histogram Image]
    H --> I[Assemble top Container]
    I --> J[Create quantile statistics Table]
    J --> K[Create descriptive statistics Table]
    K --> L[Create statistics Container]
    L --> M[Process histogram data again for full histogram]
    M --> N[Create full histogram Image]
    N --> O[Create frequency table]
    O --> P[Create extreme values Container]
    P --> Q[Assemble bottom Container]
    Q --> R[Return template_variables]
```

## Examples:
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "varid": "var_123",
    "varname": "age",
    "alerts": [],
    "description": "Age of participants",
    "n_distinct": 50,
    "p_distinct": 0.8,
    "n_missing": 5,
    "p_missing": 0.01,
    "n_infinite": 0,
    "p_infinite": 0.0,
    "mean": 35.2,
    "min": 18.0,
    "max": 85.0,
    "n_zeros": 0,
    "p_zeros": 0.0,
    "n_negative": 0,
    "p_negative": 0.0,
    "memory_size": 1024,
    "histogram": ([1, 2, 3], [10, 20, 30]),
    "5%": 20.0,
    "25%": 25.0,
    "50%": 35.0,
    "75%": 45.0,
    "95%": 70.0,
    "range": 67.0,
    "iqr": 20.0,
    "std": 12.5,
    "cv": 0.35,
    "kurtosis": -0.5,
    "mad": 10.0,
    "skewness": 0.2,
    "sum": 1000.0,
    "variance": 156.25,
    "monotonic": 1,
    "alert_fields": set()
}

template_vars = render_real(config, summary)
# Returns dictionary with "top" and "bottom" containers ready for HTML rendering
```

