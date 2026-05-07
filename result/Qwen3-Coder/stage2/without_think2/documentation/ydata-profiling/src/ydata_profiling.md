# `src.ydata_profiling`

## Tree:
- ydata_profiling/
  - controller/
  - model/
  - report/
  - utils/
  - visualisation/
  - compare_reports.py
  - config.py
  - expectations_report.py
  - profile_report.py
  - serialize_report.py

## Role:
Manages configuration, profiling, and serialization of data analysis reports for pandas and Spark DataFrames.

## Description:
The ydata_profiling module provides a comprehensive framework for data profiling and analysis. It offers tools to automatically generate detailed statistical summaries, detect data quality issues, identify patterns, and produce interactive reports in multiple formats (HTML, JSON, widgets). The module supports both pandas and Spark DataFrames, with specialized handling for time-series data and distributed computing environments.

This module is designed to be the central hub for data profiling operations, integrating type inference, statistical summarization, visualization, and report generation. It provides both programmatic APIs and command-line interfaces for data exploration and validation.

Primary consumers include:
- Data scientists and analysts working with pandas or Spark DataFrames
- Automated data quality monitoring systems
- Machine learning pipelines requiring data validation
- Data engineering teams performing data discovery and profiling

The cohesion of this module stems from its shared responsibility for data profiling workflows, encompassing configuration management, data analysis, report generation, and serialization capabilities.

## Components:
- config.py: Configuration management for profiling settings
- profile_report.py: Main ProfileReport class for data profiling
- serialize_report.py: Serialization utilities for saving/loading reports
- expectations_report.py: Integration with Great Expectations for validation
- compare_reports.py: Comparison functionality between profiling reports

## Public API:
- ProfileReport: Main class for creating data profiling reports
- Settings: Configuration class for profiling parameters
- SerializeReport: Utility for serializing/deserializing reports
- ExpectationsReport: Interface for generating Great Expectations suites
- compare_reports: Function for comparing two profiling reports

## Dependencies:
- Internal: 
  - controller/: Data processing controllers
  - model/: Data models and schemas
  - report/: Report generation components
  - utils/: Utility functions
  - visualisation/: Visualization components
- External:
  - pandas: Core DataFrame operations
  - pyarrow: Arrow format support
  - numpy: Numerical computations
  - matplotlib/seaborn: Visualization libraries
  - jinja2: Template engine for HTML reports
  - visions: Type inference system
  - great_expectations: Validation framework integration

## Constraints:
- All profiling operations assume valid DataFrame inputs
- Configuration objects must be properly initialized before use
- Serialization requires pickle-compatible data structures
- Thread-safety is not guaranteed for concurrent report generation
- Memory usage scales with dataset size and complexity

---

## Files

- [`compare_reports.py`](ydata_profiling/compare_reports.md)
- [`config.py`](ydata_profiling/config.md)
- [`expectations_report.py`](ydata_profiling/expectations_report.md)
- [`profile_report.py`](ydata_profiling/profile_report.md)
- [`serialize_report.py`](ydata_profiling/serialize_report.md)

