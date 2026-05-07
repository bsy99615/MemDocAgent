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
Coordinates the generation and presentation of structured data profiling reports

## Description:
The report module serves as the central coordinator for creating comprehensive data profiling reports. It integrates data analysis results with presentation components to generate structured, visually appealing reports that can be displayed in various formats (HTML, widgets).

This module is organized into three main subsystems:
1. **Presentation Layer**: Provides the building blocks and conversion mechanisms for rendering reports in different formats
2. **Structure Layer**: Defines the logical organization and content assembly for profiling reports
3. **Formatters**: Offers utility functions for formatting data values for display in reports

The module acts as the bridge between raw data analysis and user-facing report generation, ensuring consistent presentation and logical organization of profiling information.

## Components:
*   `presentation.core.renderable.Renderable` - Abstract base class for all presentation elements that can be rendered in different formats
*   `presentation.core.container.Container` - Structural container for grouping renderable components together
*   `presentation.core.table.Table` - Tabular data presentation components for displaying structured information
*   `presentation.core.variable.Variable` - Variable information presentation components for displaying metadata about data columns
*   `presentation.core.frequency_table.FrequencyTable` - Frequency distribution table components for showing value distributions
*   `presentation.core.html.HTML` - Raw HTML content rendering components for embedding custom HTML snippets
*   `presentation.core.image.Image` - Image display components for charts and visualizations
*   `presentation.core.sample.Sample` - Data sample display components for showing representative data points
*   `presentation.core.dropdown.Dropdown` - Dropdown menu UI elements for interactive navigation
*   `presentation.core.collapse.Collapse` - Collapsible UI components with toggle functionality
*   `presentation.core.toggle_button.ToggleButton` - Interactive toggle button components for expanding/collapsing sections
*   `presentation.core.alerts.Alerts` - Alert presentation components for displaying data quality issues
*   `presentation.core.duplicate.Duplicate` - Duplicate data reporting components
*   `presentation.core.correlation_table.CorrelationTable` - Correlation matrix visualization components
*   `presentation.core.frequency_table_small.FrequencyTableSmall` - Compact frequency table components
*   `presentation.core.variable_info.VariableInfo` - Detailed variable metadata presentation components
*   `presentation.core.root.Root` - Top-level report container and entry point for report structures
*   `presentation.flavours.flavours.HTMLReport` - Converts a generic report structure into its HTML-specific representation
*   `presentation.flavours.flavours.WidgetReport` - Converts a generic report structure into its widget-specific representation
*   `structure.correlations.get_correlation_items` - Generates renderable correlation items for display in profiling reports
*   `structure.overview.get_dataset_items` - Collects and organizes various dataset-related components for report generation
*   `structure.report.get_report_structure` - Generates the complete hierarchical structure of a profiling report
*   `formatters.fmt` - Formats values for display by applying appropriate formatting based on value type
*   `formatters.fmt_array` - Formats a numpy array with controlled display options for concise representation
*   `formatters.fmt_badge` - Converts parenthetical numeric values in a string into HTML badge elements
*   `formatters.fmt_bytesize` - Formats numeric byte values into human-readable strings with appropriate binary prefixes
*   `formatters.fmt_class` - Wraps text content in an HTML span element with a specified CSS class attribute
*   `formatters.fmt_color` - Wraps text in HTML span tags with specified color styling for report formatting
*   `formatters.fmt_monotonic` - Converts integer monotonicity codes into human-readable descriptive strings
*   `formatters.fmt_number` - Formats an integer value with locale-aware number grouping
*   `formatters.fmt_numeric` - Formats numeric values with scientific notation support and HTML superscript formatting
*   `formatters.fmt_percent` - Formats a floating-point value as a percentage string with special handling for edge cases
*   `formatters.fmt_timespan` - Formats numeric time values into human-readable string representations with appropriate time units
*   `formatters.fmt_timespan_timedelta` - Formats time span values represented as pandas Timedelta objects or numeric values
*   `formatters.help` - Generates HTML markup for a help badge that displays a question mark icon with tooltip functionality
*   `formatters.list_args` - Decorator that enables a function to process both single values and lists of values uniformly

## Public API:
*   `presentation.core.renderable.Renderable` - Abstract base class for all presentation elements with render() method contract
*   `presentation.core.container.Container` - Structural container for grouping renderable items with content and metadata
*   `presentation.core.table.Table` - Tabular data presentation with content and styling options
*   `presentation.core.variable.Variable` - Variable information presentation with metadata display capabilities
*   `presentation.core.frequency_table.FrequencyTable` - Frequency distribution table with customizable display options
*   `presentation.core.html.HTML` - Raw HTML content rendering with embedded HTML string support
*   `presentation.core.image.Image` - Image display component with URL and image type specifications
*   `presentation.core.sample.Sample` - Data sample display with configurable sample size and content
*   `presentation.core.dropdown.Dropdown` - Dropdown menu UI element with option selection capabilities
*   `presentation.core.collapse.Collapse` - Collapsible UI component with toggle functionality and content management
*   `presentation.core.toggle_button.ToggleButton` - Interactive toggle button with state management
*   `presentation.core.alerts.Alerts` - Alert presentation components for displaying data quality issues
*   `presentation.core.duplicate.Duplicate` - Duplicate data reporting with duplicate detection capabilities
*   `presentation.core.correlation_table.CorrelationTable` - Correlation matrix visualization with statistical data
*   `presentation.core.frequency_table_small.FrequencyTableSmall` - Compact frequency table for space-constrained displays
*   `presentation.core.variable_info.VariableInfo` - Detailed variable metadata presentation with comprehensive information
*   `presentation.core.root.Root` - Top-level report container with body, footer, and style configuration
*   `presentation.flavours.flavours.HTMLReport(structure)` - Transforms a generic Root structure into its HTML presentation form
*   `presentation.flavours.flavours.WidgetReport(structure)` - Transforms a generic report structure into its widget-based presentation form
*   `structure.correlations.get_correlation_items(config, summary)` - Generates renderable correlation items for display in profiling reports
*   `structure.overview.get_dataset_items(config, summary, alerts)` - Collects and organizes various dataset-related components for report generation
*   `structure.report.get_report_structure(config, summary)` - Generates the complete hierarchical structure of a profiling report
*   `formatters.fmt(value)` - Formats values for display by applying appropriate formatting based on value type
*   `formatters.fmt_array(value, threshold)` - Formats a numpy array with controlled display options for concise representation
*   `formatters.fmt_badge(value)` - Converts parenthetical numeric values in a string into HTML badge elements
*   `formatters.fmt_bytesize(num, suffix)` - Formats numeric byte values into human-readable strings with appropriate binary prefixes
*   `formatters.fmt_class(text, cls)` - Wraps text content in an HTML span element with a specified CSS class attribute
*   `formatters.fmt_color(text, color)` - Wraps text in HTML span tags with specified color styling for report formatting
*   `formatters.fmt_monotonic(value)` - Converts integer monotonicity codes into human-readable descriptive strings
*   `formatters.fmt_number(value)` - Formats an integer value with locale-aware number grouping
*   `formatters.fmt_numeric(value, precision)` - Formats numeric values with scientific notation support and HTML superscript formatting
*   `formatters.fmt_percent(value, edge_cases)` - Formats a floating-point value as a percentage string with special handling for edge cases
*   `formatters.fmt_timespan(num_seconds, detailed, max_units)` - Formats numeric time values into human-readable string representations with appropriate time units
*   `formatters.fmt_timespan_timedelta(delta, detailed, max_units, precision)` - Formats time span values represented as pandas Timedelta objects or numeric values
*   `formatters.help(title, url)` - Generates HTML markup for a help badge that displays a question mark icon with tooltip functionality
*   `formatters.list_args(func)` - Decorator that enables a function to process both single values and lists of values uniformly

## Dependencies:
*   Internal: `ydata_profiling.config.Style` - Styling configuration for reports
*   Internal: `ydata_profiling.model.alerts.Alert` - Data quality alert definitions
*   Internal: `ydata_profiling.config.ImageType` - Image format enumeration
*   Internal: `ydata_profiling.report.presentation.core` - Core presentation classes that define the abstract interfaces
*   Internal: `ydata_profiling.report.presentation.flavours.html` - HTML-specific implementations for rendering
*   Internal: `ydata_profiling.report.presentation.flavours.widget` - Widget-specific implementations for interactive display
*   Internal: `ydata_profiling.report.structure.variables.*` - For variable-specific rendering functions
*   Internal: `ydata_profiling.model.types` - For type checking and resolution
*   Internal: `ydata_profiling.utils` - For utility functions used in report generation
*   External: `pandas` - Data manipulation and DataFrame handling
*   External: `numpy` - Numerical computations and array operations
*   External: `matplotlib.pyplot` - Static visualization creation
*   External: `seaborn` - Statistical data visualization
*   External: `plotly.graph_objects` - Interactive visualizations
*   External: `plotly.express` - Easy interactive chart creation
*   External: `scipy.stats` - Statistical functions and tests
*   External: `typing` - Type hinting support
*   External: `collections.Counter` - Counting hashable objects
*   External: `re` - Regular expression operations
*   External: `urllib.parse` - URL parsing and manipulation
*   External: `os` - Operating system dependent functionality
*   External: `math` - Mathematical functions
*   External: `datetime` - Date and time operations
*   External: `json` - JSON data handling
*   External: `base64` - Base64 encoding/decoding
*   External: `io` - In-memory file-like objects
*   External: `warnings` - Warning messages
*   External: `logging` - Logging functionality

## Constraints:
*   All concrete renderable classes must implement the abstract `render()` method
*   Components must be properly initialized with required parameters before use
*   Renderable components should be used within the proper inheritance hierarchy
*   Thread safety: Components are stateless and should be safe for concurrent use
*   Flavour conversion functions must operate in-place on the input structure to maintain reference consistency
*   The mapping dictionaries must contain entries for all core renderable types that are expected to be converted
*   The input structure for flavour conversion must be a valid Root instance with properly initialized content
*   All utility functions expect valid pandas Series inputs and appropriate numeric parameters
*   All functions expect valid configuration objects with properly initialized parameters
*   Summary dictionaries must contain all required keys for the specific data being processed
*   All functions must return consistent data structures (lists of renderable components or single renderable objects)
*   Functions must handle missing or invalid data gracefully without raising exceptions
*   All functions are pure and should not modify external state or perform I/O operations
*   Template variables returned must be compatible with the presentation layer components

---

## Files

- [`formatters.py`](report/formatters.md)

