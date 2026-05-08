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
Handles the structural organization and component assembly for generating HTML data profiling reports

## Description:
This module provides the foundational structure and organization logic for creating comprehensive data profiling reports. It serves as the central coordination layer that orchestrates the assembly of various report components including dataset overview, variable analysis, correlations, missing data visualization, and sample data presentation.

The module is organized around three primary areas:
1. **Structure Components**: Core functions that define the hierarchical structure of reports
2. **Overview Components**: Logic for generating dataset-level information and metadata
3. **Correlations Components**: Processing and presentation of correlation analysis results

This module is essential for the report generation pipeline, providing the glue that connects data analysis results with their appropriate presentation formats.

Primary consumers of this module include:
- Report generation system (src/ydata_profiling/report/generate_report.py)
- Main report structure builder (src/ydata_profiling/report/structure/report.py)
- Presentation layer components that require structured data organization

The cohesion principle behind this module is that all components work together to transform raw profiling data into a well-organized, navigable HTML report structure that maintains logical groupings of related information.

## Components:
*   **correlations.get_correlation_items**: Generates renderable correlation items for display in profiling reports, handling multiple correlation methods and visualization formats
*   **overview.get_dataset_alerts**: Processes and formats data quality alerts for inclusion in profiling reports, handling both single and multiple report scenarios
*   **overview.get_dataset_column_definitions**: Creates a structured table presentation of dataset column definitions for inclusion in profiling reports
*   **overview.get_dataset_items**: Collects and organizes various dataset-related components for report generation into a structured list of renderable items
*   **overview.get_dataset_overview**: Creates a structured overview of dataset statistics and variable types for report generation
*   **overview.get_dataset_reproduction**: Generates a reproducibility section for dataset profiling reports containing analysis metadata and configuration information, relying on underlying formatters and data access patterns
*   **overview.get_dataset_schema**: Creates a structured dataset metadata container for inclusion in profiling reports
*   **overview.get_timeseries_items**: Generates a comprehensive time series overview report section with statistical summaries and visual plots
*   **report.get_definition_items**: Generates a presentation-ready component that displays column definitions as a duplicate data structure in the report
*   **report.get_duplicates_items**: Processes duplicate data and generates renderable components for inclusion in profiling reports
*   **report.get_interactions**: Converts interaction plot data into renderable components for report generation
*   **report.get_missing_items**: Transforms missing data summary information into presentation-ready renderable components
*   **report.get_report_structure**: Generates the complete hierarchical structure of a profiling report by assembling various data sections and presentation components
*   **report.get_sample_items**: Converts raw sample data into renderable presentation components for report generation
*   **report.render_variables_section**: Generates a list of Variable renderable objects for each column in a DataFrame summary, including type-specific rendering and alert handling

## Public API:
*   **correlations.get_correlation_items(config, summary)**: Generates renderable correlation items for display in profiling reports
*   **overview.get_dataset_alerts(config, alerts)**: Processes and formats data quality alerts for inclusion in profiling reports
*   **overview.get_dataset_column_definitions(config, definitions)**: Creates a structured table presentation of dataset column definitions
*   **overview.get_dataset_items(config, summary, alerts)**: Collects and organizes various dataset-related components for report generation
*   **overview.get_dataset_overview(config, summary)**: Creates a structured overview of dataset statistics and variable types
*   **overview.get_dataset_reproduction(config, summary)**: Generates a reproducibility section for dataset profiling reports containing analysis metadata and configuration information
*   **overview.get_dataset_schema(config, metadata)**: Creates a structured dataset metadata container
*   **overview.get_timeseries_items(config, summary)**: Generates a comprehensive time series overview report section
*   **report.get_definition_items(definitions)**: Generates a presentation-ready component that displays column definitions as a duplicate data structure in the report
*   **report.get_duplicates_items(config, duplicates)**: Processes duplicate data and generates renderable components
*   **report.get_interactions(config, interactions)**: Converts interaction plot data into renderable components
*   **report.get_missing_items(config, summary)**: Transforms missing data summary information into presentation-ready components
*   **report.get_report_structure(config, summary)**: Generates the complete hierarchical structure of a profiling report
*   **report.get_sample_items(config, sample)**: Converts raw sample data into renderable presentation components
*   **report.render_variables_section(config, dataframe_summary)**: Generates a list of Variable renderable objects for each column

## Dependencies:
*   **Internal imports**:
    *   `src.ydata_profiling.report.presentation.core.*` - For creating various presentation components (containers, tables, images, etc.)
    *   `src.ydata_profiling.report.structure.variables.*` - For variable-specific rendering functions
    *   `src.ydata_profiling.model.alerts` - For alert handling and processing
    *   `src.ydata_profiling.model.types` - For type checking and resolution
    *   `src.ydata_profiling.utils` - For utility functions used in report generation
*   **External imports**:
    *   `pandas` - For data manipulation and analysis operations
    *   `numpy` - For numerical computations and array operations
    *   `matplotlib.pyplot` - For creating static visualizations
    *   `seaborn` - For statistical data visualization
    *   `plotly.graph_objects` - For interactive visualizations
    *   `plotly.express` - For easy interactive chart creation
    *   `scipy.stats` - For statistical functions and tests
    *   `typing` - For type hinting support
    *   `collections.Counter` - For counting hashable objects
    *   `re` - For regular expression operations
    *   `urllib.parse` - For URL parsing and manipulation
    *   `os` - For operating system dependent functionality
    *   `math` - For mathematical functions
    *   `datetime` - For date and time operations
    *   `json` - For JSON data handling
    *   `base64` - For base64 encoding/decoding
    *   `io` - For in-memory file-like objects
    *   `warnings` - For warning messages
    *   `logging` - For logging functionality

## Constraints:
*   All functions expect valid configuration objects with properly initialized parameters
*   Summary dictionaries must contain all required keys for the specific data being processed
*   All functions must return consistent data structures (lists of renderable components or single renderable objects)
*   Functions must handle missing or invalid data gracefully without raising exceptions
*   All functions are pure and should not modify external state or perform I/O operations
*   Template variables returned must be compatible with the presentation layer components
*   Thread safety: Functions are stateless and can be safely called concurrently
*   Ordering requirements: No specific ordering is required between function calls
*   Initialization prerequisites: All functions assume valid configuration and summary data structures

---

## Files

- [`correlations.py`](structure/correlations.md)
- [`overview.py`](structure/overview.md)
- [`report.py`](structure/report.md)

