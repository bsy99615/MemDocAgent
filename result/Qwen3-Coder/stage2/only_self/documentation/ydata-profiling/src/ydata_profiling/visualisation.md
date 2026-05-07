# `src.ydata_profiling.visualisation`

## Tree:
visualisation/
├── context.py
├── missing.py
├── plot.py
└── utils.py

## Role:
Manages data visualization components for statistical profiling reports, providing reusable plotting utilities and specialized visualizations for missing data, time series, and categorical distributions.

## Description:
The visualisation module serves as the core component for generating graphical representations within the ydata-profiling library. It provides a comprehensive set of plotting utilities and specialized visualizations that transform data insights into visual formats suitable for reporting and analysis. This module encapsulates the complexity of matplotlib and seaborn integration, ensuring consistent styling and high-quality visual outputs across different data profiling contexts.

The module is organized around three primary areas:
1. Core plotting utilities (plot.py) - Fundamental visualization functions for various data types
2. Missing data visualizations (missing.py) - Specialized plots for analyzing missing value patterns
3. Utility functions (utils.py) - Supporting functions for image handling and color conversions
4. Context management (context.py) - Matplotlib configuration management for consistent styling

This separation allows for clean modularity while maintaining cohesive visualization capabilities that support the broader profiling workflow.

## Components:
- manage_matplotlib_context (context.py): Context manager for consistent matplotlib styling
- plot_missing_bar (missing.py): Bar chart visualization for missing value distributions
- plot_missing_heatmap (missing.py): Heatmap visualization for missing value correlations
- plot_missing_matrix (missing.py): Matrix visualization for missing data patterns
- cat_frequency_plot (plot.py): Categorical frequency visualization (bar/pie)
- correlation_matrix (plot.py): Correlation matrix heatmap visualization
- create_comparison_color_list (plot.py): Color palette generation for comparisons
- histogram (plot.py): Main histogram visualization interface
- mini_histogram (plot.py): Compact histogram for dashboards
- mini_ts_plot (plot.py): Formatted time series plot for reports
- missing_bar (plot.py): Missing data bar chart visualization
- missing_heatmap (plot.py): Missing data correlation heatmap
- missing_matrix (plot.py): Missing data pattern matrix visualization
- plot_acf_pacf (plot.py): Dispatch function for ACF/PACF plots
- plot_overview_timeseries (plot.py): Time series overview visualization
- plot_timeseries_gap_analysis (plot.py): Time series gap highlighting
- plot_word_cloud (plot.py): Word cloud visualization interface
- scatter_complex (plot.py): Complex number scatter visualization
- scatter_pairwise (plot.py): Pairwise scatter plot with adaptive rendering
- scatter_series (plot.py): Series scatter plot with hexbin support
- timeseries_heatmap (plot.py): Time series heatmap visualization
- base64_image (utils.py): Convert binary image to base64 data URI
- hex_to_rgb (utils.py): Convert hex color to RGB tuple
- plot_360_n0sc0pe (utils.py): Plot saving utility with inline/file options

## Public API:
- manage_matplotlib_context: Context manager for matplotlib styling
- plot_missing_bar: Generate bar chart for missing value distributions
- plot_missing_heatmap: Generate heatmap for missing value correlations
- plot_missing_matrix: Generate matrix visualization for missing data patterns
- cat_frequency_plot: Generate categorical frequency visualization (bar/pie)
- correlation_matrix: Generate correlation matrix heatmap
- create_comparison_color_list: Generate color palette for comparisons
- histogram: Main histogram visualization interface
- mini_histogram: Compact histogram for dashboards
- mini_ts_plot: Formatted time series plot for reports
- missing_bar: Missing data bar chart visualization
- missing_heatmap: Missing data correlation heatmap
- missing_matrix: Missing data pattern matrix visualization
- plot_acf_pacf: Dispatch function for ACF/PACF plots
- plot_overview_timeseries: Time series overview visualization
- plot_timeseries_gap_analysis: Time series gap highlighting
- plot_word_cloud: Word cloud visualization interface
- scatter_complex: Complex number scatter visualization
- scatter_pairwise: Pairwise scatter plot with adaptive rendering
- scatter_series: Series scatter plot with hexbin support
- timeseries_heatmap: Time series heatmap visualization
- base64_image: Convert binary image to base64 data URI
- hex_to_rgb: Convert hex color to RGB tuple
- plot_360_n0sc0pe: Plot saving utility with inline/file options

## Dependencies:
Internal imports:
- From ydata_profiling.config: Settings class for configuration management
- From ydata_profiling.visualisation.context: manage_matplotlib_context for styling
- From ydata_profiling.visualisation.missing: plot_missing_* functions for missing data visualizations
- From ydata_profiling.visualisation.plot: All plotting functions for core visualizations
- From ydata_profiling.visualisation.utils: Utility functions for image handling and color conversion

External imports:
- matplotlib.pyplot: Core plotting functionality
- matplotlib.figure: Figure management
- matplotlib.axis: Axis manipulation
- matplotlib.backends.backend_agg: Backend for PNG generation
- matplotlib.ticker: Tick formatting utilities
- matplotlib.colors: Color handling utilities
- seaborn: Statistical visualization library
- numpy: Numerical computation support
- pandas: Data manipulation and analysis
- wordcloud: Word cloud generation
- PIL: Image processing capabilities
- base64: Base64 encoding for inline images
- io: Input/output stream handling
- typing: Type hinting support

## Constraints:
- All plotting functions must be used within the manage_matplotlib_context context manager for consistent styling
- Configuration objects must be properly initialized with valid settings before use
- Image format must be either 'png' or 'svg' for plot_360_n0sc0pe function
- When using file-based output, config.html.assets_path must be set
- All matplotlib operations should be performed within the managed context to prevent global state pollution
- Color conversion functions expect valid hex color strings
- Time series plotting functions require properly formatted datetime indices

---

## Files

- [`context.py`](visualisation/context.md)
- [`missing.py`](visualisation/missing.md)
- [`plot.py`](visualisation/plot.md)
- [`utils.py`](visualisation/utils.md)

