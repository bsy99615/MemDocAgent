# `src.ydata_profiling.report`

## Tree:
report/
├── presentation/
│   ├── core/
│   │   ├── alerts.py
│   │   ├── collapse.py
│   │   ├── container.py
│   │   ├── correlation_table.py
│   │   ├── dropdown.py
│   │   ├── duplicate.py
│   │   ├── frequency_table.py
│   │   ├── frequency_table_small.py
│   │   ├── html.py
│   │   ├── image.py
│   │   ├── item_renderer.py
│   │   ├── renderable.py
│   │   ├── root.py
│   │   ├── sample.py
│   │   ├── table.py
│   │   ├── toggle_button.py
│   │   ├── variable.py
│   │   └── variable_info.py
│   ├── flavours/
│   │   ├── html/
│   │   ├── widget/
│   │   └── flavours.py
│   └── frequency_table_utils.py
├── structure/
│   ├── variables/
│   │   ├── render_boolean.py
│   │   ├── render_categorical.py
│   │   ├── render_common.py
│   │   ├── render_complex.py
│   │   ├── render_count.py
│   │   ├── render_date.py
│   │   ├── render_file.py
│   │   ├── render_generic.py
│   │   ├── render_image.py
│   │   ├── render_path.py
│   │   ├── render_real.py
│   │   ├── render_text.py
│   │   ├── render_timeseries.py
│   │   └── render_url.py
│   ├── correlations.py
│   ├── overview.py
│   └── report.py
└── formatters.py

## Role:
Generates structured, multi-format data profiling reports from analytical results.

## Description:
The report module is responsible for transforming processed data analysis results into comprehensive, visually-structured reports that can be displayed in various formats (HTML, Jupyter widgets). It provides a unified interface for organizing data quality insights, statistical summaries, and visualizations into coherent report structures while maintaining consistent formatting standards.

This module decouples the data analysis logic from presentation concerns, enabling flexible report generation that adapts to different output environments. It manages the complete lifecycle of report creation, from organizing analytical components into logical sections to applying appropriate formatting and rendering strategies for different target platforms.

Primary consumers of this module include:
- The main profiling pipeline that orchestrates report generation
- Presentation layers that render reports in different environments
- Formatting utilities used throughout the reporting system

The cohesion principle centers on report generation and formatting, ensuring that all components work together to deliver consistent, professional-quality data profiling reports regardless of output format.

## Components:
- presentation: Framework for rendering reports in different formats (HTML, widgets) with hierarchical components and flavour-specific implementations
- structure: Logic for organizing report content into logical sections and components including overview, variables, correlations, and other analytical sections
- formatters: Utility functions for formatting data values for display in reports with specialized handlers for different data types

## Public API:
- presentation: Core rendering infrastructure for report components including renderable base classes, flavour-specific mappings, and conversion utilities
- structure: Report construction and organization logic including functions for building dataset overview, variable sections, correlations, missing data, and other report components
- formatters: Formatting utilities for data display including numeric, textual, and special-purpose formatters for percentages, bytes, timespans, and other common data types

## Dependencies:
- Internal:
  - ydata_profiling.config: Configuration management for styling and rendering options
  - ydata_profiling.report.presentation: Rendering framework components
  - ydata_profiling.report.structure: Report structure and organization logic
- External:
  - pandas: Data manipulation and analysis
  - numpy: Numerical operations and array handling
  - matplotlib/seaborn: Visualization generation
  - typing: Type annotations for better code clarity

## Constraints:
- All report components must be properly initialized before use
- Thread safety: Components are stateless and can be safely used concurrently
- Report structure construction requires proper parameter validation
- Presentation components must be compatible with their target rendering flavour
- Formatting functions should handle all data types gracefully
- The module assumes proper configuration availability for rendering decisions

---

## Files

- [`formatters.py`](report/formatters.md)

