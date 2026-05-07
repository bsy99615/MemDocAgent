# `ydata-profiling`

## Tree:
```
ydata-profiling/
├── src/
│   ├── controller/          # Workflow control and data processing pipelines
│   ├── model/               # Core data analysis and summarization logic
│   ├── report/              # Report structure and rendering components
│   ├── utils/               # Utility functions for data processing and helpers
│   ├── visualisation/       # Visualization and chart generation components
│   ├── profile_report.py    # Main profiling report interface
│   ├── config.py            # Configuration management system
│   ├── expectations_report.py # Great Expectations integration
│   ├── compare_reports.py   # Report comparison functionality
│   └── serialize_report.py  # Serialization utilities
```

## Purpose:
The ydata-profiling repository provides comprehensive data profiling and analysis capabilities for pandas and Spark DataFrames. It addresses the critical need for quick, automated data understanding in data science workflows by generating statistical summaries, visualizations, and data quality assessments. This tool helps data scientists and analysts rapidly gain insights into dataset characteristics, identify potential issues, and make informed decisions about data preprocessing and modeling strategies.

## Target Users:
- Data Scientists and Analysts conducting exploratory data analysis
- Machine Learning Engineers validating training data quality
- Data Engineers performing data quality assessments
- Business Intelligence professionals examining data sources
- Anyone needing rapid, automated insights into tabular datasets

## Position in Ecosystem:
Standalone data profiling library that integrates seamlessly with existing data science workflows. It serves as both a standalone tool for quick data exploration and as a foundation for more complex data quality systems. Can be used programmatically or via command-line interface, and integrates with popular data science tools like Jupyter notebooks, Great Expectations, and Spark environments.

## Architecture:
The system follows a pipeline architecture with clear separation of concerns between data processing, analysis, and presentation layers. The core components include:
- Controller layer: Manages workflow control and data processing pipelines
- Model layer: Implements core data analysis and summarization logic with statistical computations
- Report layer: Handles report structure and rendering components for various output formats
- Visualization layer: Generates charts and plots for statistical representations
- Utilities layer: Provides helper functions for data processing and type conversions

Key architectural patterns:
- Plugin-style design for modular report generation
- Separation of concerns between data analysis and presentation layers
- Lazy evaluation for performance optimization
- Configuration-driven approach for customization

## Entry Points:
- **Programmatic API**: `ProfileReport(df, config=None)` - Main constructor for creating profiling reports
- **Configuration**: `Settings(...)` - Central configuration class for customizing profiling behavior  
- **CLI Interface**: Command-line tools for batch processing and report generation
- **Great Expectations Integration**: `ExpectationsReport(...)` - Converts profiling results into validation suites
- **Comparison Tools**: `compare_reports(report1, report2)` - Function for comparing multiple reports
- **Serialization**: `SerializeReport(...)` - Utilities for saving/loading profiling results

## Core Features:
- **Statistical Analysis**: Comprehensive numerical and categorical statistics for all columns
- **Data Quality Assessment**: Automated detection of missing values, duplicates, outliers, and inconsistencies
- **Data Type Detection**: Automatic identification of variable types using the visions library
- **Visualizations**: Interactive charts and plots for data exploration (histograms, scatter plots, correlation matrices)
- **Customizable Reports**: Configurable output formats including HTML, JSON, and interactive widgets
- **Great Expectations Integration**: Convert profiling results into executable validation rules
- **Report Comparison**: Side-by-side analysis of multiple datasets to highlight differences
- **Serialization**: Save and load complete profiling reports for later analysis
- **Spark Support**: Compatibility with Apache Spark DataFrames for large-scale data analysis
- **Parallel Processing**: Multi-threaded analysis for improved performance on large datasets

## Dependencies:
- **pandas**: Primary DataFrame manipulation library for data analysis
- **numpy**: Numerical computing support for mathematical operations
- **matplotlib/seaborn**: Visualization libraries for generating charts and plots
- **pydantic**: Configuration validation and serialization framework
- **visions**: Data type detection system for automatic variable classification
- **great_expectations**: Optional validation framework integration for data quality assurance
- **jinja2**: Template engine for HTML report generation
- **requests**: HTTP client for remote data fetching (when applicable)

## Configuration:
The system uses a hierarchical configuration approach:
- Global Settings class in `config.py` manages all profiling parameters
- Environment variables and YAML configuration files supported for deployment flexibility
- Runtime parameters allow fine-grained control over analysis behavior
- Configuration inheritance enables consistent settings across multiple reports

## Extension Points:
- **Custom Analysis Modules**: Extend `model/` components to add domain-specific analysis
- **New Visualizations**: Implement in `visualisation/` to create custom chart types
- **Report Formats**: Add new output formats in `report/` module
- **Data Type Detection**: Extend `visions` integration for specialized data types
- **Plugins**: Hook into the controller workflow for custom preprocessing or post-processing steps
- **Configuration Extensions**: Inherit from base config classes to add new parameters
- **Report Templates**: Customize HTML templates in the report module for branding or layout changes

---

## Modules

- [`src`](src.md)
- [`src/ydata_profiling`](src/ydata_profiling.md)
- [`src/ydata_profiling/controller`](src/ydata_profiling/controller.md)
- [`src/ydata_profiling/model`](src/ydata_profiling/model.md)
- [`src/ydata_profiling/model/pandas`](src/ydata_profiling/model/pandas.md)
- [`src/ydata_profiling/model/spark`](src/ydata_profiling/model/spark.md)
- [`src/ydata_profiling/report`](src/ydata_profiling/report.md)
- [`src/ydata_profiling/report/presentation`](src/ydata_profiling/report/presentation.md)
- [`src/ydata_profiling/report/presentation/core`](src/ydata_profiling/report/presentation/core.md)
- [`src/ydata_profiling/report/presentation/flavours`](src/ydata_profiling/report/presentation/flavours.md)
- [`src/ydata_profiling/report/presentation/flavours/html`](src/ydata_profiling/report/presentation/flavours/html.md)
- [`src/ydata_profiling/report/presentation/flavours/widget`](src/ydata_profiling/report/presentation/flavours/widget.md)
- [`src/ydata_profiling/report/structure`](src/ydata_profiling/report/structure.md)
- [`src/ydata_profiling/report/structure/variables`](src/ydata_profiling/report/structure/variables.md)
- [`src/ydata_profiling/utils`](src/ydata_profiling/utils.md)
- [`src/ydata_profiling/visualisation`](src/ydata_profiling/visualisation.md)

