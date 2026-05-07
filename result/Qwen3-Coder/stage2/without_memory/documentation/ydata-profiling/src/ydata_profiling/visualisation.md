# `src.ydata_profiling.visualisation`

## Tree:
visualisation/
├── context.py
├── missing.py
├── plot.py
└── utils.py

## Role:
Manages all visualization-related functionality for generating plots and charts in the profiling report

## Description:
This module provides comprehensive visualization capabilities for data profiling reports. It handles the creation of various chart types including missing data visualizations, correlation matrices, time series plots, histograms, and categorical frequency plots. The module ensures consistent styling and formatting across all visualizations while managing matplotlib contexts properly.

Primary consumers of this module include the report generation pipeline and the HTML output formatter, which rely on this module to create visual representations of data characteristics.

The components are grouped together because they all serve the common purpose of creating visual representations of data profiles, sharing common utilities for styling, base64 encoding, and matplotlib context management.

## Components:
- context.py: Contains matplotlib context management utilities
  - `manage_matplotlib_context()` - Context manager for setting consistent matplotlib styling
- missing.py: Missing data visualization functions
  - `get_font_size()` - Calculates appropriate font size for labels based on column count
  - `plot_missing_bar()` - Creates bar chart visualization of missing data
  - `plot_missing_heatmap()` - Creates heatmap visualization of missing data patterns
  - `plot_missing_matrix()` - Creates matrix visualization of missing data
- plot.py: Core plotting functions and utilities
  - `_create_timeseries_heatmap()` - Creates heatmap for time series data
  - `_format_ts_date_axis()` - Formats time series date axes
  - `_get_ts_lag()` - Calculates appropriate lag for time series analysis
  - `_plot_acf_pacf()` - Plots autocorrelation and partial autocorrelation functions
  - `_plot_acf_pacf_comparison()` - Plots comparison of ACF/PACF for multiple series
  - `_plot_histogram()` - Creates histogram plots
  - `_plot_pie_chart()` - Creates pie charts
  - `_plot_stacked_barh()` - Creates horizontal stacked bar charts
  - `_plot_timeseries()` - Creates time series plots
  - `_plot_word_cloud()` - Creates word cloud visualizations
  - `_prepare_heatmap_data()` - Prepares data for heatmap visualization
  - `_set_visibility()` - Sets visibility for plot spines and ticks
  - `cat_frequency_plot()` - Creates categorical frequency plots (bar or pie)
  - `correlation_matrix()` - Creates correlation matrix heatmaps
  - `create_comparison_color_list()` - Generates color lists for comparisons
  - `format_fn()` - Formats timestamp values for display
  - `get_cmap_half()` - Creates half colormap for correlation matrices
  - `get_correlation_font_size()` - Calculates font size for correlation labels
  - `histogram()` - Creates standard histogram plots
  - `mini_histogram()` - Creates compact histogram plots
  - `mini_ts_plot()` - Creates compact time series plots
  - `missing_bar()` - Creates missing data bar chart
  - `missing_heatmap()` - Creates missing data heatmap
  - `missing_matrix()` - Creates missing data matrix visualization
  - `plot_acf_pacf()` - Plots ACF/PACF for time series analysis
  - `plot_overview_timeseries()` - Creates overview of time series variables
  - `plot_timeseries_gap_analysis()` - Creates time series gap analysis plots
  - `plot_word_cloud()` - Creates word cloud visualizations
  - `scatter_complex()` - Creates scatter plots for complex numbers
  - `scatter_pairwise()` - Creates pairwise scatter plots
  - `scatter_series()` - Creates scatter plots for series data
  - `timeseries_heatmap()` - Creates time series heatmap
- utils.py: Utility functions for visualization
  - `base64_image()` - Encodes image bytes to base64 string
  - `hex_to_rgb()` - Converts hex color codes to RGB tuples
  - `plot_360_n0sc0pe()` - Handles saving and encoding of plots

## Public API:
- `manage_matplotlib_context()` - Context manager for matplotlib styling
- `get_font_size()` - Calculate font size for labels
- `plot_missing_bar()` - Create missing data bar chart
- `plot_missing_heatmap()` - Create missing data heatmap
- `plot_missing_matrix()` - Create missing data matrix
- `cat_frequency_plot()` - Create categorical frequency plots
- `correlation_matrix()` - Create correlation matrix heatmap
- `histogram()` - Create standard histogram
- `mini_histogram()` - Create compact histogram
- `missing_bar()` - Create missing data bar chart
- `missing_heatmap()` - Create missing data heatmap
- `missing_matrix()` - Create missing data matrix
- `plot_acf_pacf()` - Plot ACF/PACF for time series
- `plot_overview_timeseries()` - Create time series overview
- `plot_timeseries_gap_analysis()` - Create time series gap analysis
- `plot_word_cloud()` - Create word cloud visualization
- `scatter_complex()` - Create scatter plot for complex numbers
- `scatter_pairwise()` - Create pairwise scatter plot
- `scatter_series()` - Create scatter plot for series data
- `timeseries_heatmap()` - Create time series heatmap
- `base64_image()` - Encode image to base64
- `hex_to_rgb()` - Convert hex to RGB
- `plot_360_n0sc0pe()` - Save and encode plots

## Dependencies:
Internal:
- `src.ydata_profiling.config.Settings` - Configuration object for plot settings
- `src.ydata_profiling.visualisation.utils` - Utility functions for image handling
- `src.ydata_profiling.visualisation.missing` - Missing data visualization functions
- `src.ydata_profiling.visualisation.plot` - Core plotting functions
- `src.ydata_profiling.visualisation.context` - Matplotlib context management

External:
- `matplotlib` - Main plotting library
- `seaborn` - Statistical data visualization library
- `numpy` - Numerical computing library
- `pandas` - Data manipulation library
- `wordcloud` - Word cloud generation library
- `base64` - Base64 encoding library
- `io` - Input/output operations
- `urllib.parse` - URL parsing utilities
- `uuid` - Unique identifier generation

## Constraints:
- All plotting functions must be called within a matplotlib context managed by `manage_matplotlib_context()`
- Plotting functions require a valid `Settings` configuration object
- When `config.html.inline` is True, plots are returned as base64 encoded strings
- When `config.html.inline` is False, plots are saved to disk and paths are returned
- All color conversions must use `hex_to_rgb()` for consistency
- Time series functions require proper datetime indexing on input data
- Font sizing calculations depend on column counts and label lengths

---

## Files

- [`context.py`](visualisation/context.md)
- [`missing.py`](visualisation/missing.md)
- [`plot.py`](visualisation/plot.md)
- [`utils.py`](visualisation/utils.md)

