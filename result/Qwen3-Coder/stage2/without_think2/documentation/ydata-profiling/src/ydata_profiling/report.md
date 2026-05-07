# `src.ydata_profiling.report`

## Tree:
report/
├── presentation/
│   ├── core/
│   ├── flavours/
│   │   ├── html/
│   │   ├── widget/
│   │   └── flavours.py
│   └── frequency_table_utils.py
├── structure/
│   ├── variables/
│   ├── correlations.py
│   ├── overview.py
│   └── report.py
└── formatters.py

## Role:
Generates structured data profiling reports with multiple presentation formats and formatting utilities.

## Description:
This module serves as the core reporting system for ydata-profiling, providing infrastructure for generating comprehensive data profiling reports in various formats. It orchestrates the transformation of raw profiling data into structured, presentation-ready components through two main subsystems: structure generation and presentation formatting.

The structure subsystem organizes profiling results into logical report sections (overview, variables, correlations, etc.), while the presentation subsystem handles conversion of these structures into different output formats (HTML, widgets). The module groups related functionality around the concept of report generation, separating data processing from presentation logic to enable flexible output formats.

## Components:
* `get_report_structure` - Main entry point for assembling complete report structures from profiling data
* `HTMLReport` - Converts report structures to HTML presentation format
* `WidgetReport` - Converts report structures to widget-based presentation format
* `fmt_*` functions - Various formatting utilities for different data types (numbers, dates, percentages, etc.)
* `list_args` - Decorator for functions that handle both single values and lists of values

## Public API:
* `get_report_structure(config, summary)` - Assembles all report sections into a complete hierarchical structure
* `HTMLReport(structure: Root)` - Converts a report structure to HTML-ready components
* `WidgetReport(structure: Root)` - Converts a report structure to widget-ready components
* `fmt_number(value: int)` - Formats integers with locale-aware grouping separators
* `fmt_numeric(value: float, precision: int)` - Formats numeric values with configurable precision and scientific notation handling
* `fmt_percent(value: float, edge_cases: bool)` - Formats decimal values as percentages with special edge case handling
* `fmt_bytesize(num: float, suffix: str)` - Formats byte sizes with binary prefixes (Ki, Mi, Gi, etc.)
* `fmt_timespan(num_seconds: Any, detailed: bool, max_units: int)` - Formats time durations into human-readable strings
* `fmt_timespan_timedelta(delta: Any, detailed: bool, max_units: int, precision: int)` - Formats timedelta or numeric values into time duration strings
* `fmt_class(text: str, cls: str)` - Wraps text in HTML span with specified CSS class
* `fmt_color(text: str, color: str)` - Wraps text in HTML span with inline color styling
* `fmt_badge(value: str)` - Converts parenthetical numeric values to HTML badge elements
* `fmt_array(value: np.ndarray, threshold: Any)` - Formats NumPy arrays with controlled truncation
* `fmt_monotonic(value: int)` - Converts monotonicity indicators to descriptive strings
* `help(title: str, url: Optional[str])` - Generates HTML help badges with tooltips
* `list_args(func: Callable)` - Decorator enabling functions to handle both single values and lists

## Dependencies:
* Internal: `ydata_profiling.config.Settings` - Configuration object for styling and report settings
* Internal: `ydata_profiling.model.BaseDescription` - Data structure containing profiling results
* Internal: `ydata_profiling.report.presentation.core` - Base renderable classes and interfaces
* Internal: `ydata_profiling.report.presentation.flavours.html` - HTML-specific renderable implementations
* Internal: `ydata_profiling.report.presentation.flavours.widget` - Widget-specific renderable implementations
* Internal: `ydata_profiling.report.structure.variables` - Variable-specific rendering utilities
* External: `pandas` - Used for DataFrame operations in sample and duplicate processing
* External: `matplotlib` - Used for generating time series plots and visualization components
* External: `typing` - Type hinting support
* External: `collections.abc` - Abstract base classes for sequence types
* External: `markupsafe` - HTML escaping for security
* External: `decimal` - Decimal arithmetic for precise time calculations
* External: `numpy` - Array formatting and mathematical operations

## Constraints:
* All report generation functions require properly initialized configuration objects
* Input data structures must conform to expected schemas (e.g., summary objects must contain required attributes)
* Presentation flavour functions must be called with valid Root instances
* Type mappings must be complete and consistent for all supported renderable types
* Conversion operations modify objects in-place rather than creating new instances
* Presentation flavour selection must happen before rendering operations
* Thread safety: Functions are stateless and can be safely called concurrently
* Initialization prerequisites: Configuration objects must be fully configured before passing to functions

---

## Files

- [`formatters.py`](report/formatters.md)

