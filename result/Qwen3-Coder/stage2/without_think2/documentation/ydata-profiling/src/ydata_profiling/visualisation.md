# `src.ydata_profiling.visualisation`

## Tree:
visualisation/
├── context.py
├── missing.py
├── plot.py
└── utils.py

## Role:
Manages visualization generation and rendering for data profiling reports, including missing data patterns, time series analysis, and statistical distributions.

## Description:
The visualisation module is responsible for creating graphical representations of data profiling results. It provides functions for generating various types of plots including missing data visualizations, time series heatmaps, correlation matrices, histograms, and categorical distributions. The module handles both the creation of matplotlib figures and their conversion to HTML-compatible formats, ensuring consistent styling and proper integration with the profiling report generation pipeline.

This module is used primarily by the reporting system to generate visual summaries of data characteristics. It integrates with the configuration system to apply consistent styling and formatting across all visualizations, and provides utilities for handling different data types and visualization requirements.

## Components:
*   **context.py**: Contains matplotlib context management utilities for consistent visualization styling
*   **missing.py**: Provides functions for creating missing data pattern visualizations (bar charts, heatmaps, matrices)
*   **plot.py**: Core plotting functions for time series, histograms, scatter plots, correlation matrices, and other statistical visualizations
*   **utils.py**: Utility functions for image encoding, color conversion, and plot formatting

## Public API:
*   `manage_matplotlib_context()`: Context manager for temporary matplotlib/seaborn styling
*   `get_font_size()`: Calculates appropriate font size for missing data visualizations
*   `plot_missing_bar()`: Creates bar chart visualization of missing data patterns
*   `plot_missing_heatmap()`: Generates heatmap visualization of missing value correlations
*   `plot_missing_matrix()`: Creates matrix visualization of missing data patterns
*   `plot_overview_timeseries()`: Generates overview time series plots
*   `plot_timeseries_gap_analysis()`: Creates time series plots with gap highlighting
*   `plot_word_cloud()`: Generates word cloud visualizations from text frequency data
*   `scatter_complex()`: Creates scatter plots for complex number data
*   `scatter_pairwise()`: Generates pairwise scatter plots with adaptive rendering
*   `scatter_series()`: Creates scatter or hexbin plots for series data
*   `timeseries_heatmap()`: Creates time series heatmaps for grouped entity data
*   `base64_image()`: Encodes binary image data into base64 URL-safe strings
*   `hex_to_rgb()`: Converts hexadecimal color strings to normalized RGB values
*   `plot_360_n0sc0pe()`: Formats and saves plots for HTML report inclusion

## Dependencies:
*   Internal: `src.ydata_profiling.config.Settings` for configuration management
*   External: `matplotlib`, `seaborn`, `numpy`, `pandas`, `wordcloud`, `base64`, `urllib.parse`

## Constraints:
*   All plotting functions must respect the configuration settings for styling and output format
*   Functions must properly close matplotlib figures to prevent memory leaks
*   Image generation must support both inline base64 encoding and file-based storage modes
*   Visualization functions should handle edge cases like empty data or invalid inputs gracefully

---

## Files

- [`context.py`](visualisation/context.md)
- [`missing.py`](visualisation/missing.md)
- [`plot.py`](visualisation/plot.md)
- [`utils.py`](visualisation/utils.md)

