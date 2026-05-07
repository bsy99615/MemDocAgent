# `src.ydata_profiling.report.structure`

## Tree:
structure/
├── variables/
│   ├── render_boolean.py
│   ├── render_categorical.py
│   ├── render_common.py
│   ├── render_complex.py
│   ├── render_count.py
│   ├── render_date.py
│   ├── render_file.py
│   ├── render_generic.py
│   ├── render_image.py
│   ├── render_path.py
│   ├── render_real.py
│   ├── render_text.py
│   ├── render_timeseries.py
│   └── render_url.py
├── correlations.py
├── overview.py
└── report.py

## Role:
Coordinates the construction and organization of data profiling report structures by integrating various analytical sections and presentation components.

## Description:
This module serves as the central coordinator for building comprehensive data profiling reports. It orchestrates the assembly of different analytical sections (overview, variables, interactions, correlations, missing values, sample data, and duplicates) into a unified hierarchical report structure. The module maintains a clear separation between data processing logic and presentation concerns, enabling modular report construction where each section can be built independently and reused across different report templates.

Primary consumers of this module include:
- The main report generation pipeline in the profiling system
- The HTML template rendering engine that consumes the structured report components
- Various data analysis components that require organized report structures

The cohesion principle behind this module is that all report structure and organization logic is centralized here, making it easier to maintain consistent report layouts and enabling flexible report generation based on available data and configuration settings.

## Components:
- correlations.py: Contains functions for generating correlation-related report components including heatmaps and tables
- overview.py: Handles dataset overview sections including metadata, schema, column definitions, time series analysis, alerts, and reproduction information
- report.py: Manages the overall report structure construction, combining various analytical sections into a complete hierarchical report
- variables/: Directory containing specialized rendering functions for different variable types in data profiling reports

## Public API:
- get_correlation_items(config, summary): Generates renderable correlation items for report inclusion, including heatmaps and tables for various correlation methods
- get_dataset_alerts(config, alerts): Creates unified Alerts presentation component from either a single list of alerts or a tuple of multiple alert collections, filtering out rejected alerts for count calculation
- get_dataset_column_definitions(config, definitions): Creates a structured table presentation of dataset column definitions for report generation
- get_dataset_items(config, summary, alerts): Creates a structured collection of report components for dataset overview, including metadata, schema, column definitions, time series analysis, alerts, and reproduction information
- get_dataset_overview(config, summary): Creates a structured overview of dataset statistics and variable types for reporting purposes
- get_dataset_reproduction(config, summary): Creates a reproducibility section for dataset profiling reports containing metadata about the analysis run
- get_dataset_schema(config, metadata): Creates a structured dataset metadata presentation component containing key dataset identification and attribution information
- get_timeseries_items(config, summary): Creates a structured container with time series statistics and visualization plots for inclusion in profiling reports
- get_definition_items(definitions): Creates a renderable component for displaying column definitions in a data profiling report when definition data is available
- get_duplicates_items(config, duplicates): Converts duplicate data into renderable UI components for report visualization
- get_interactions(config, interactions): Converts interaction plot data into renderable UI components for report visualization
- get_missing_items(config, summary): Creates presentation components for missing data visualization patterns in a data profiling report
- get_report_structure(config, summary): Constructs a hierarchical report structure for data profiling by organizing various analytical sections into a navigable UI layout
- get_sample_items(config, sample): Processes sample data structures into renderable components for report generation, handling both single samples and batches of samples
- render_variables_section(config, dataframe_summary): Converts variable analysis results into presentation-ready components for data profiling reports

## Dependencies:
Internal imports:
- Variables rendering functions from the variables/ subdirectory (render_boolean, render_categorical, render_common, etc.)
- Various utility functions for formatting and data processing
- Component-specific helper functions for specialized rendering logic

External imports:
- pandas: Used for DataFrame operations in data processing
- numpy: Used for numerical computations and array operations
- matplotlib/seaborn: Used for generating visualizations and plots
- Other visualization libraries for chart generation

## Constraints:
- All functions must accept consistent parameter signatures for proper integration
- Report structure functions must maintain proper ordering and hierarchy
- Configuration objects must be properly initialized before use
- Thread safety: Functions are stateless and can be called concurrently
- Initialization prerequisites: All required data structures must be populated before calling report construction functions

---

## Files

- [`correlations.py`](structure/correlations.md)
- [`overview.py`](structure/overview.md)
- [`report.py`](structure/report.md)

