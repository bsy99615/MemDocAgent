# `src.ydata_profiling.visualisation`

## Tree:
visualisation/
├── context.py
├── missing.py
├── plot.py
└── utils.py

## Role:
Manages the creation and formatting of data visualizations for profiling reports, providing reusable components for generating charts, heatmaps, and other graphical representations of data characteristics.

## Description:
The visualisation module serves as the core component for generating graphical representations in data profiling reports. It provides a collection of functions and utilities that create various types of visualizations including bar charts, heatmaps, time series plots, scatter plots, and missing data visualizations. These components work together to present data insights in a visually intuitive manner.

This module is used extensively throughout the ydata-profiling library to generate HTML reports that include statistical visualizations. The module is organized around different visualization types and includes utility functions for common operations like color conversion, base64 encoding, and matplotlib context management.

## Components:
- **context.py**: Provides matplotlib context management for consistent styling
- **missing.py**: Contains functions for creating missing data visualizations (bar charts, heatmaps, matrices)
- **plot.py**: Houses core plotting functions for various data types including time series, histograms, scatter plots, and correlation matrices
- **utils.py**: Contains utility functions for image encoding, color conversion, and plot formatting

## Public API:
- `manage_matplotlib_context`: Context manager for matplotlib styling
- `get_font_size`: Calculates appropriate font size for missing data visualizations
- `plot_missing_bar`: Creates bar chart visualization for missing data distribution
- `plot_missing_heatmap`: Generates heatmap visualization of missing data patterns
- `plot_missing_matrix`: Produces matrix-style visualization of missing value patterns
- `plot_acf_pacf`: Dispatches to appropriate ACF/PACF plotting functions
- `_create_timeseries_heatmap`: Creates time series heatmap visualization
- `_format_ts_date_axis`: Formats x-axis for time series data
- `_get_ts_lag`: Calculates optimal lag size for time series analysis
- `_plot_acf_pacf`: Generates combined ACF and PACF plots
- `_plot_acf_pacf_comparison`: Creates comparative ACF/PACF plots for multiple series
- `_plot_histogram`: Creates customizable histogram plots
- `_plot_pie_chart`: Generates pie charts with percentage labels
- `_plot_stacked_barh`: Creates horizontal stacked bar charts
- `_plot_timeseries`: Creates time series plots for single or multiple series
- `_plot_word_cloud`: Generates word cloud visualizations from frequency data
- `_prepare_heatmap_data`: Transforms data for heatmap visualization
- `_set_visibility`: Configures axis visibility for clean chart presentation
- `cat_frequency_plot`: Generates categorical frequency plots (bar or pie)
- `correlation_matrix`: Creates correlation matrix heatmaps
- `create_comparison_color_list`: Generates color lists for comparison visualizations
- `format_fn`: Formats Unix timestamps for matplotlib axis labels
- `get_cmap_half`: Creates colormap from upper half of colors
- `get_correlation_font_size`: Determines font size for correlation matrix labels
- `histogram`: Generates histogram visualizations from numerical data
- `mini_histogram`: Creates compact histogram visualizations for space-constrained displays
- `mini_ts_plot`: Generates compact time series plots
- `missing_bar`: Creates bar chart for missing data
- `missing_heatmap`: Generates missing data correlation heatmaps
- `missing_matrix`: Creates matrix visualization of missing data patterns
- `plot_overview_timeseries`: Creates time series overview plots
- `plot_timeseries_gap_analysis`: Visualizes time series with gap highlighting
- `plot_word_cloud`: Generates word cloud visualizations
- `scatter_complex`: Creates scatter plots for complex number data
- `scatter_pairwise`: Generates pairwise scatter plots
- `scatter_series`: Creates scatter plots for bivariate data
- `timeseries_heatmap`: Creates time series heatmap visualizations
- `base64_image`: Converts binary image data to base64 data URI
- `hex_to_rgb`: Converts hexadecimal color strings to RGB tuples
- `plot_360_n0sc0pe`: Generates image data for HTML report visualization

## Dependencies:
- **Internal imports**:
  - `src.ydata_profiling.config.Settings`: Configuration object for visualization settings
  - Various plotting utilities from the same module
- **External imports**:
  - `matplotlib.pyplot` and `matplotlib.figure`: Core plotting functionality
  - `seaborn`: Statistical visualization library
  - `numpy`: Numerical computing library
  - `pandas`: Data manipulation library
  - `wordcloud`: Word cloud generation library
  - `scipy.stats`: Statistical functions for time series analysis
  - `matplotlib.colors`: Color handling utilities
  - `matplotlib.ticker`: Tick formatting utilities
  - `base64`: Base64 encoding for inline images
  - `uuid`: Unique identifier generation for file paths

## Constraints:
- All plotting functions must be called within a matplotlib context manager to ensure proper styling
- Visualization functions expect specific data structures (pandas Series, numpy arrays, etc.)
- Color-related functions require valid hex color strings or RGB tuples
- Time series functions assume datetime indexes for proper date formatting
- Missing data visualization functions require proper column naming and count data
- All matplotlib figures must be properly closed to prevent memory leaks
- Image generation functions must respect configuration settings for inline vs file-based output

---

## Files

- [`context.py`](visualisation/context.md)
- [`missing.py`](visualisation/missing.md)
- [`plot.py`](visualisation/plot.md)
- [`utils.py`](visualisation/utils.md)

