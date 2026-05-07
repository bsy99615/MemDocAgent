# `src`

## Tree:
```
ydata_profiling/
├── controller/
├── model/
├── report/
├── utils/
├── visualisation/
├── compare_reports.py
├── config.py
├── expectations_report.py
├── profile_report.py
└── serialize_report.py
```

## Role:
Provides comprehensive data profiling and analysis capabilities for pandas and Spark DataFrames, generating statistical summaries, visualizations, and data quality assessments.

## Description:
The ydata_profiling module is a comprehensive data profiling library that delivers detailed statistical analysis, visualizations, and quality assessments for datasets. It serves as the core engine for generating insightful reports about data characteristics, helping users understand their data quickly and effectively.

This module is organized around several key subsystems:
- Core profiling functionality (`profile_report.py`) 
- Configuration management (`config.py`)
- Report generation and serialization (`serialize_report.py`)
- Expectations integration (`expectations_report.py`)
- Comparison capabilities (`compare_reports.py`)

The module is designed to work with both pandas and Spark DataFrames, offering flexible analysis modes and extensive customization options through its configuration system. It provides both programmatic interfaces and file-based export capabilities for easy integration into data science workflows.

## Components:
- **ProfileReport** (`profile_report.py`): Main interface for creating and managing profiling reports with lazy evaluation and caching mechanisms. Provides properties for HTML, JSON, and widget outputs, along with methods for exporting reports and accessing analysis results.
- **Settings** (`config.py`): Central configuration class managing all profiling parameters including parallelism, visualization settings, report formatting, and feature-specific configurations. Inherits from Pydantic BaseSettings for validation.
- **ExpectationsReport** (`expectations_report.py`): Converts profiling results into Great Expectations validation suites for automated data quality assurance. Integrates with the profiling system to generate executable validation rules.
- **SerializeReport** (`serialize_report.py`): Handles serialization and deserialization of profiling results for persistence and transfer between sessions. Enables saving and loading of complete profiling reports.
- **CompareReports** (`compare_reports.py`): Provides functionality for comparing multiple profiling reports to highlight differences and similarities between datasets. Supports side-by-side analysis of data characteristics.
- **Config classes** (`config.py`): Various configuration models for different profiling aspects including numerical analysis (NumVars), text analysis (TextVars), categorical analysis (CatVars), and more specialized settings.
- **Controller/Model/Report/Utils/Visualisation**: Supporting infrastructure components for report generation, data processing, and visualization.

## Public API:
- `ProfileReport(df, config=None, **kwargs)`: Main constructor for creating profiling reports with comprehensive configuration options including minimal mode, time-series analysis, and various analysis modes.
- `Settings(...)`: Configuration class for customizing profiling behavior including parallelism, visualization, and feature-specific settings with support for file-based configuration loading.
- `ExpectationsReport(...)`: Interface for generating Great Expectations validation suites from profiling results with options for validation execution and documentation generation.
- `SerializeReport(...)`: Serialization/deserialization utilities for persisting profiling results to files or byte streams.
- `compare_reports(report1, report2, config=None)`: Function for comparing multiple reports to highlight differences and similarities between datasets.
- `config.*`: All configuration classes and enums including ImageType, Theme, NumVars, TextVars, and specialized settings for different data types.

## Dependencies:
- Internal: 
  - `controller/`: Infrastructure for report generation workflows and data processing pipelines
  - `model/`: Core data analysis and summarization logic with statistical computations and type detection
  - `report/`: Report structure and rendering components for HTML, JSON, and widget outputs
  - `utils/`: Utility functions for data processing, type conversion, and helper operations
  - `visualisation/`: Visualization and chart generation components for statistical plots and diagrams
- External:
  - pandas: Primary DataFrame manipulation library for data analysis
  - numpy: Numerical computing support for mathematical operations
  - matplotlib/seaborn: Visualization libraries for generating charts and plots
  - pydantic: Configuration validation and serialization framework
  - visions: Data type detection system for automatic variable classification
  - great_expectations: Optional validation framework integration for data quality assurance

## Constraints:
- Thread-safety: Not thread-safe; each ProfileReport instance should be used by one thread at a time
- Initialization: ProfileReport requires a valid DataFrame or lazy=True to be instantiated
- Memory usage: Large datasets may require significant memory for full analysis
- Configuration: All configuration must be valid Pydantic models to ensure type safety
- Spark compatibility: Some features are limited in Spark environments due to distributed computing constraints
- Caching: Reports are cached for performance but may need manual invalidation when underlying data changes
- File I/O: Serialization operations require appropriate file system permissions

