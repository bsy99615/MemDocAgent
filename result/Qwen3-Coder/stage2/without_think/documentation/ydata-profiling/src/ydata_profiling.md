# `src.ydata_profiling`

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
Provides comprehensive data profiling capabilities for pandas and Spark DataFrames, generating detailed statistical summaries, visualizations, and quality assessments.

## Description:
The ydata_profiling module serves as the core data profiling system, offering a complete solution for understanding dataset characteristics, identifying data quality issues, and generating actionable insights. It provides both programmatic and interactive interfaces for data analysis, supporting multiple output formats including HTML reports, JSON data, and interactive widgets.

This module is designed to be the primary entry point for data profiling workflows, integrating with various subsystems including type inference, statistical summarization, visualization rendering, and data validation. It supports both lazy and eager evaluation modes, caching mechanisms, and extensive customization through configuration options.

## Components:
- **ProfileReport**: Main class for creating and managing data profiling reports
- **Settings**: Configuration class for customizing profiling behavior  
- **ExpectationsReport**: Class for converting profiling results into data validation frameworks
- **SerializeReport**: Utility for persisting and loading profiling reports
- **compare_reports**: Module for comparing multiple datasets
- **config**: Module containing configuration classes and utilities
- **controller/**: Controller components coordinating report generation workflows
- **model/**: Data models and structures used in profiling
- **report/**: Report generation and presentation logic
- **utils/**: Utility functions and helpers
- **visualisation/**: Visualization components and rendering

## Public API:
- `ProfileReport`: Main interface for creating data profiling reports
- `Settings`: Configuration class for customizing profiling behavior
- `ExpectationsReport`: Interface for generating data validation suites
- `SerializeReport`: Utility for serializing/deserializing reports
- `compare_reports.compare`: Function for comparing multiple datasets
- `config.*`: All configuration classes and utilities

## Dependencies:
- **Internal imports**: 
  - `controller/`: Components coordinating report generation workflows
  - `model/`: Data models and structures used in profiling
  - `report/`: Report generation and presentation logic
  - `utils/`: Utility functions and helpers
  - `visualisation/`: Visualization components and rendering
  - `compare_reports`: For dataset comparison functionality
  - `config`: For configuration management
- **External imports**: 
  - `pandas`, `numpy`, `matplotlib`, `seaborn`: Data manipulation and visualization libraries
  - `pydantic`: For configuration validation and serialization
  - `visions`: For data type detection
  - `tqdm`: For progress indicators
  - `IPython`: For notebook integration
  - `great_expectations`: For expectation suite generation

## Constraints:
- Thread-safety: Not guaranteed for concurrent access to the same ProfileReport instance
- Initialization: ProfileReport requires a valid DataFrame for non-lazy initialization
- Memory usage: Large datasets may require significant memory for full profiling
- Configuration: Some configuration options are mutually exclusive (e.g., minimal=True and config_file)
- Spark compatibility: Certain features are not supported with Spark DataFrames

---

## Files

- [`compare_reports.py`](ydata_profiling/compare_reports.md)
- [`config.py`](ydata_profiling/config.md)
- [`expectations_report.py`](ydata_profiling/expectations_report.md)
- [`profile_report.py`](ydata_profiling/profile_report.md)
- [`serialize_report.py`](ydata_profiling/serialize_report.md)

