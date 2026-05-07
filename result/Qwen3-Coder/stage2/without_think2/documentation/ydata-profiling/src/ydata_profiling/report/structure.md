# `src.ydata_profiling.report.structure`

## Tree:
- structure/
  - variables/
  - correlations.py
  - overview.py
  - report.py

## Role:
Generates structured presentation components for data profiling reports, orchestrating various data sections into a cohesive report structure.

## Description:
This module is responsible for transforming profiling analysis results into structured, presentation-ready components for report generation. It provides functions to create individual report sections (dataset overview, variable analysis, correlations, etc.) and coordinates their assembly into a complete hierarchical report structure. The module follows a clear separation of concerns by handling presentation logic independently from data processing, enabling modular development and testing of report components.

The module is primarily consumed by the report generation pipeline and integrates with various data processing modules to produce comprehensive profiling reports. It groups related presentation functions together to support the logical organization of profiling report content.

## Components:
- get_correlation_items (function): Creates structured correlation analysis components with heatmaps and tables
- get_dataset_alerts (function): Processes dataset-level alerts into presentation-ready Alerts components
- get_dataset_column_definitions (function): Converts column definitions into formatted table containers
- get_dataset_items (function): Orchestrates dataset overview components including metadata, schema, and reproduction info
- get_dataset_overview (function): Generates dataset statistics and variable type distribution tables
- get_dataset_reproduction (function): Creates reproducibility metadata tables for analysis runs
- get_dataset_schema (function): Formats dataset metadata into structured presentation containers
- get_timeseries_items (function): Presents time series analysis statistics and visualization plots
- get_definition_items (function): Creates UI components for displaying column definitions
- get_duplicates_items (function): Converts duplicate data into renderable components
- get_interactions (function): Transforms interaction plots into structured presentation containers
- get_missing_items (function): Generates presentation components for missing data visualizations
- get_report_structure (function): Assembles all report sections into a complete hierarchical structure
- get_sample_items (function): Processes sample data into renderable components for report display
- render_variables_section (function): Transforms variable-level profiling summaries into presentation-ready Variable components

## Public API:
- get_correlation_items(config, summary): Generates correlation analysis presentation components
- get_dataset_alerts(config, alerts): Creates Alerts component from dataset-level alerts
- get_dataset_column_definitions(config, definitions): Converts column definitions to formatted table container
- get_dataset_items(config, summary, alerts): Orchestrates dataset overview report components
- get_dataset_overview(config, summary): Generates dataset statistics and variable type tables
- get_dataset_reproduction(config, summary): Creates reproducibility metadata table
- get_dataset_schema(config, metadata): Formats dataset metadata into presentation container
- get_timeseries_items(config, summary): Presents time series analysis components
- get_definition_items(definitions): Creates UI component for column definitions
- get_duplicates_items(config, duplicates): Converts duplicate data to renderable components
- get_interactions(config, interactions): Transforms interaction plots into structured containers
- get_missing_items(config, summary): Generates missing data visualization components
- get_report_structure(config, summary): Assembles complete report structure with all sections
- get_sample_items(config, sample): Processes sample data into renderable components
- render_variables_section(config, dataframe_summary): Transforms variable summaries into Variable components

## Dependencies:
- Internal: 
  - ydata_profiling.config.Settings: Configuration object for styling and report settings
  - ydata_profiling.model.BaseDescription: Data structure containing profiling results
  - ydata_profiling.report.structure.variables: Variable-specific rendering utilities
- External:
  - pandas: Used for DataFrame operations in sample and duplicate processing
  - matplotlib: Used for generating time series plots and visualization components
  - typing: Provides type hints for better code documentation and IDE support

## Constraints:
- All functions must receive properly initialized configuration objects with required attributes
- Input data structures must conform to expected schemas (e.g., summary objects must contain required attributes)
- Functions should handle empty or missing data gracefully without raising exceptions
- All returned renderable components must be properly initialized with required metadata
- Thread safety: Functions are stateless and can be safely called concurrently
- Initialization prerequisites: Configuration objects must be fully configured before passing to functions

---

## Files

- [`correlations.py`](structure/correlations.md)
- [`overview.py`](structure/overview.md)
- [`report.py`](structure/report.md)

