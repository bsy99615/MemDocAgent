# `src.ydata_profiling.model`

## Tree:
```
model/
├── pandas/
├── spark/
├── alerts.py
├── correlations.py
├── dataframe.py
├── describe.py
├── description.py
├── duplicates.py
├── expectation_algorithms.py
├── handler.py
├── missing.py
├── pairwise.py
├── sample.py
├── summarizer.py
├── summary.py
├── summary_algorithms.py
├── table.py
├── timeseries_index.py
├── typeset.py
└── typeset_relations.py
```

## Role:
Provides the foundational type inference and data profiling infrastructure for the ydata-profiling library.

## Description:
The model module serves as the core data modeling layer of ydata-profiling, implementing the type inference system and data profiling algorithms. It contains the Visions-based type system that automatically categorizes data columns, along with specialized profiling components for analyzing various data characteristics like missing values, correlations, duplicates, and statistical summaries. This module bridges the gap between raw data and meaningful insights by providing the structural foundation for data analysis.

Primary consumers include:
- The main ProfileReport class for data profiling workflows
- Various presentation components that render profiling results
- Statistical analysis modules that require type-aware operations

The module is organized around two main concepts: type inference through the Visions framework and data profiling operations that leverage these types for meaningful analysis.

## Components:
*   `alerts.py`: Defines alerting mechanisms for data quality issues
*   `correlations.py`: Implements correlation analysis between data columns
*   `dataframe.py`: Provides DataFrame-specific profiling utilities
*   `describe.py`: Core data description and summary generation
*   `description.py`: Data description and metadata extraction
*   `duplicates.py`: Duplicate detection and analysis algorithms
*   `expectation_algorithms.py`: Validation and expectation checking utilities
*   `handler.py`: Base classes for handling different data types
*   `missing.py`: Missing value analysis and reporting
*   `pairwise.py`: Pairwise analysis between data columns
*   `sample.py`: Sample data generation and selection utilities
*   `summarizer.py`: Data summarization and aggregation logic
*   `summary.py`: High-level summary statistics and reporting
*   `summary_algorithms.py`: Algorithms for computing summary statistics
*   `table.py`: Table structure and layout handling
*   `timeseries_index.py`: Time series index handling and validation
*   `typeset.py`: Visions-based type inference system implementation
*   `typeset_relations.py`: Type relationship and validation functions

## Public API:
*   `typeset.ProfilingTypeSet`: Main type set class for data profiling that extends VisionsTypeset with profiling-specific configurations
*   `typeset_relations.*`: Utility functions for type validation and conversion
*   `summary.Summary`: High-level summary statistics generator
*   `correlations.Correlations`: Correlation analysis tools
*   `missing.Missing`: Missing value analysis utilities

## Dependencies:
*   Internal: `src.ydata_profiling.config` for configuration management
*   Internal: `src.ydata_profiling.report.presentation` for rendering components
*   External: `pandas` for data manipulation and analysis
*   External: `visions` for type inference framework
*   External: `numpy` for numerical computations
*   External: `scipy` for statistical functions

## Constraints:
*   All type inference operations must be thread-safe and deterministic
*   Type validation functions must handle edge cases gracefully without raising exceptions
*   The ProfilingTypeSet must initialize efficiently and support dynamic configuration
*   All profiling components must respect the configured data types and transformations

---

## Files

- [`alerts.py`](model/alerts.md)
- [`correlations.py`](model/correlations.md)
- [`dataframe.py`](model/dataframe.md)
- [`describe.py`](model/describe.md)
- [`description.py`](model/description.md)
- [`duplicates.py`](model/duplicates.md)
- [`expectation_algorithms.py`](model/expectation_algorithms.md)
- [`handler.py`](model/handler.md)
- [`missing.py`](model/missing.md)
- [`pairwise.py`](model/pairwise.md)
- [`sample.py`](model/sample.md)
- [`summarizer.py`](model/summarizer.md)
- [`summary.py`](model/summary.md)
- [`summary_algorithms.py`](model/summary_algorithms.md)
- [`table.py`](model/table.md)
- [`timeseries_index.py`](model/timeseries_index.md)
- [`typeset.py`](model/typeset.md)
- [`typeset_relations.py`](model/typeset_relations.md)

