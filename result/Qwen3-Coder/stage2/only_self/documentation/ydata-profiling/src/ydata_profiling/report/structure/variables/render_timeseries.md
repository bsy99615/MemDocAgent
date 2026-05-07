# `render_timeseries.py`

## `src.ydata_profiling.report.structure.variables.render_timeseries._render_gap_tab` · *function*

*No documentation generated.*

## `src.ydata_profiling.report.structure.variables.render_timeseries.render_timeseries` · *function*

## Summary
Generates HTML template variables for displaying numeric time series data in profiling reports, including statistical summaries, visualizations, and distribution analyses.

## Description
Creates a comprehensive set of template variables for time series variable reporting by combining common rendering logic with time series-specific visualizations and statistics. This function orchestrates the presentation of time series data including basic statistics, quantile information, descriptive statistics, histograms, time series plots, gap analysis, frequency tables, and autocorrelation analysis.

The function leverages `render_common` to establish base template variables and then extends them with time series-specific components like mini time series plots, histograms, and statistical measures. It organizes these elements into a structured layout with top and bottom sections for optimal report presentation.

Known callers within the codebase:
- Called by the main report generation pipeline when processing numeric time series variables
- Triggered during the variable-specific rendering phase of profiling reports

This logic is extracted into its own function to separate time series-specific presentation concerns from general variable rendering logic, enforcing a clear responsibility boundary between common variable presentation and time series-specific visualization and statistics.

## Args
    config (Settings): Configuration object containing rendering parameters including:
        - plot.image_format: Format for generated images (png, svg, etc.)
        - html.style: HTML styling configuration
        - report.precision: Numeric precision for statistical displays
        - n_extreme_obs: Number of extreme observations to display
    summary (dict): Dictionary containing time series summary statistics with required keys:
        - "varid": Variable identifier
        - "varname": Variable name
        - "alerts": List of alert conditions
        - "description": Variable description
        - "n_distinct": Count of distinct values
        - "p_distinct": Percentage of distinct values
        - "n_missing": Count of missing values
        - "p_missing": Percentage of missing values
        - "n_infinite": Count of infinite values
        - "p_infinite": Percentage of infinite values
        - "mean": Mean value
        - "min": Minimum value
        - "max": Maximum value
        - "n_zeros": Count of zero values
        - "p_zeros": Percentage of zero values
        - "memory_size": Memory usage in bytes
        - "std": Standard deviation
        - "cv": Coefficient of variation
        - "kurtosis": Kurtosis measure
        - "mad": Median absolute deviation
        - "skewness": Skewness measure
        - "sum": Sum of values
        - "variance": Variance
        - "monotonic": Monotonicity status
        - "addfuller": Augmented Dickey-Fuller test p-value
        - "range": Range of values
        - "iqr": Interquartile range
        - "histogram": Histogram data (either list or tuple)
        - "series": Time series data
        - "alert_fields": Fields that triggered alerts

## Returns
    dict: Template variables dictionary containing:
        - "top": Container with basic information, summary statistics, and mini time series plot
        - "bottom": Container with detailed statistics, histogram, time series plots, gap analysis, frequency tables, and autocorrelation analysis
        - All other keys inherited from render_common function

## Raises
    None explicitly raised

## Constraints
    Preconditions:
        - config must contain required attributes for image formats, HTML styling, and report precision
        - summary must contain all required keys with appropriate data types
        - Time series data in summary["series"] must be compatible with plotting functions
        - Histogram data in summary["histogram"] must be either a list or tuple with proper structure

    Postconditions:
        - Returns a complete template variables dictionary ready for HTML rendering
        - All visualizations are properly formatted with correct image formats
        - Statistical values are formatted according to configuration precision settings

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[Start render_timeseries] --> B[Call render_common for base variables]
    B --> C[Create VariableInfo component]
    C --> D[Create first summary table (basic stats)]
    D --> E[Create second summary table (descriptive stats)]
    E --> F[Create mini time series plot]
    F --> G[Assemble top container with info, tables, and plot]
    G --> H[Create quantile statistics table]
    H --> I[Create descriptive statistics table]
    I --> J[Create statistics container]
    J --> K[Process histogram data (list vs tuple)]
    K --> L[Create histogram image]
    L --> M[Create frequency table]
    M --> N[Create extreme values container]
    N --> O[Create ACF/PACF plot]
    O --> P[Create time series plot]
    P --> Q[Call _render_gap_tab for gap analysis]
    Q --> R[Assemble bottom container with all components]
    R --> S[Return template_variables]
```

## Examples
```python
# Typical usage in report generation pipeline
config = Settings()
summary = {
    "varid": "ts_var_1",
    "varname": "temperature_readings",
    "alerts": [],
    "description": "Hourly temperature measurements",
    "n_distinct": 1200,
    "p_distinct": 0.85,
    "n_missing": 10,
    "p_missing": 0.005,
    "n_infinite": 0,
    "p_infinite": 0.0,
    "mean": 23.5,
    "min": 18.2,
    "max": 32.1,
    "n_zeros": 0,
    "p_zeros": 0.0,
    "memory_size": 48000,
    "std": 4.2,
    "cv": 0.18,
    "kurtosis": -0.3,
    "mad": 3.1,
    "skewness": 0.2,
    "sum": 28200.0,
    "variance": 17.64,
    "monotonic": "increasing",
    "addfuller": 0.03,
    "range": 13.9,
    "iqr": 5.8,
    "histogram": ([bins], [counts]),
    "series": pd.Series([1, 2, 3, 4, 5]),
    "alert_fields": []
}

template_vars = render_timeseries(config, summary)
```

