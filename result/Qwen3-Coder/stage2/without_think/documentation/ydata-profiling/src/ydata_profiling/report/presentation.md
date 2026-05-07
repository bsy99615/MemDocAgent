# `src.ydata_profiling.report.presentation`

## Tree:
presentation/
├── core/
│   ├── alerts.py
│   ├── collapse.py
│   ├── container.py
│   ├── correlation_table.py
│   ├── dropdown.py
│   ├── duplicate.py
│   ├── frequency_table.py
│   ├── frequency_table_small.py
│   ├── html.py
│   ├── image.py
│   ├── item_renderer.py
│   ├── renderable.py
│   ├── root.py
│   ├── sample.py
│   ├── table.py
│   ├── toggle_button.py
│   ├── variable.py
│   └── variable_info.py
├── flavours/
│   ├── html/
│   ├── widget/
│   └── flavours.py
└── frequency_table_utils.py

## Role:
Provides the foundational rendering infrastructure and concrete presentation components for generating data profiling reports.

## Description:
The presentation module serves as the core infrastructure for creating structured, visually appealing data profiling reports. It provides both the fundamental building blocks (renderable components) and the mechanisms for converting these components into different presentation formats (HTML, widgets). This module enables the creation of rich, interactive reports that can be displayed in various environments while maintaining consistent data presentation standards.

The module is organized into three main areas:
1. Core presentation components that define the basic building blocks for reports
2. Flavour conversion systems that transform generic structures into specific presentation formats
3. Utility functions for processing frequency table data for visualization

This separation allows for flexible report generation where the same underlying data structures can be rendered in different ways (HTML vs. widget) while maintaining consistent interfaces and behaviors.

## Components:
*   `core.renderable.Renderable` - Abstract base class for all presentation elements that can be rendered in different formats
*   `core.item_renderer.ItemRenderer` - Abstract base class for item-based renderers that extend Renderable with item-type identification
*   `core.container.Container` - Structural container for grouping renderable components together
*   `core.table.Table` - Tabular data presentation components for displaying structured information
*   `core.variable.Variable` - Variable information presentation components for displaying metadata about data columns
*   `core.frequency_table.FrequencyTable` - Frequency distribution table components for showing value distributions
*   `core.html.HTML` - Raw HTML content rendering components for embedding custom HTML snippets
*   `core.image.Image` - Image display components for charts and visualizations
*   `core.sample.Sample` - Data sample display components for showing representative data points
*   `core.dropdown.Dropdown` - Dropdown menu UI elements for interactive navigation
*   `core.collapse.Collapse` - Collapsible UI components with toggle functionality
*   `core.toggle_button.ToggleButton` - Interactive toggle button components for expanding/collapsing sections
*   `core.alerts.Alerts` - Alert presentation components for displaying data quality issues
*   `core.duplicate.Duplicate` - Duplicate data reporting components
*   `core.correlation_table.CorrelationTable` - Correlation matrix visualization components
*   `core.frequency_table_small.FrequencyTableSmall` - Compact frequency table components
*   `core.variable_info.VariableInfo` - Detailed variable metadata presentation components
*   `core.root.Root` - Top-level report container and entry point for report structures
*   `flavours.flavours.HTMLReport` - Converts a generic report structure into its HTML-specific representation
*   `flavours.flavours.WidgetReport` - Converts a generic report structure into its widget-specific representation
*   `flavours.flavours.apply_renderable_mapping` - Applies a type mapping to convert a renderable structure to its flavour-specific representation
*   `flavours.flavours.get_html_renderable_mapping` - Creates a mapping from core renderable types to their HTML implementation types
*   `flavours.flavours.get_widget_renderable_mapping` - Creates a mapping from core renderable types to their widget implementation types
*   `frequency_table_utils.freq_table` - Processes frequency table data for visualization by handling both single and multiple frequency table inputs
*   `frequency_table_utils.extreme_obs_table` - Creates formatted table representations of extreme observations from frequency distributions
*   `frequency_table_utils._frequency_table` - Internal utility for processing frequency table data into standardized display records
*   `frequency_table_utils._extreme_obs_table` - Internal utility for creating formatted table representations of the most frequent observations from a frequency distribution

## Public API:
*   `core.renderable.Renderable` - Abstract base class for all presentation elements with render() method contract
*   `core.item_renderer.ItemRenderer` - Abstract base class for item-based renderers with item_type identification
*   `core.container.Container` - Structural container for grouping renderable items with content and metadata
*   `core.table.Table` - Tabular data presentation with content and styling options
*   `core.variable.Variable` - Variable information presentation with metadata display capabilities
*   `core.frequency_table.FrequencyTable` - Frequency distribution table with customizable display options
*   `core.html.HTML` - Raw HTML content rendering with embedded HTML string support
*   `core.image.Image` - Image display component with URL and image type specifications
*   `core.sample.Sample` - Data sample display with configurable sample size and content
*   `core.dropdown.Dropdown` - Dropdown menu UI element with option selection capabilities
*   `core.collapse.Collapse` - Collapsible UI component with toggle functionality and content management
*   `core.toggle_button.ToggleButton` - Interactive toggle button with state management
*   `core.alerts.Alerts` - Alert presentation components for displaying data quality issues
*   `core.duplicate.Duplicate` - Duplicate data reporting with duplicate detection capabilities
*   `core.correlation_table.CorrelationTable` - Correlation matrix visualization with statistical data
*   `core.frequency_table_small.FrequencyTableSmall` - Compact frequency table for space-constrained displays
*   `core.variable_info.VariableInfo` - Detailed variable metadata presentation with comprehensive information
*   `core.root.Root` - Top-level report container with body, footer, and style configuration
*   `flavours.flavours.HTMLReport(structure)` - Transforms a generic Root structure into its HTML presentation form
*   `flavours.flavours.WidgetReport(structure)` - Transforms a generic Root structure into its widget-based presentation form
*   `flavours.flavours.apply_renderable_mapping(mapping, structure, flavour)` - Applies a type mapping to convert renderable structure to flavour-specific representation
*   `flavours.flavours.get_html_renderable_mapping()` - Returns mapping from core renderable types to HTML implementations
*   `flavours.flavours.get_widget_renderable_mapping()` - Returns mapping from core renderable types to widget implementations
*   `frequency_table_utils.freq_table(freqtable, n, max_number_to_print)` - Processes frequency table data for visualization
*   `frequency_table_utils.extreme_obs_table(freqtable, number_to_print, n)` - Creates formatted table representations of extreme observations
*   `frequency_table_utils._frequency_table(freqtable, n, max_number_to_print)` - Internal utility for processing frequency table data into standardized display records
*   `frequency_table_utils._extreme_obs_table(freqtable, number_to_print, n)` - Internal utility for creating formatted table representations of extreme observations

## Dependencies:
*   Internal: `ydata_profiling.config.Style` - Styling configuration for reports
*   Internal: `ydata_profiling.model.alerts.Alert` - Data quality alert definitions
*   Internal: `ydata_profiling.config.ImageType` - Image format enumeration
*   Internal: `ydata_profiling.report.presentation.core` - Core presentation classes that define the abstract interfaces
*   Internal: `ydata_profiling.report.presentation.flavours.html` - HTML-specific implementations for rendering
*   Internal: `ydata_profiling.report.presentation.flavours.widget` - Widget-specific implementations for interactive display
*   External: `pandas` - Data manipulation and DataFrame handling
*   External: `typing` - Type hinting support

## Constraints:
*   All concrete renderable classes must implement the abstract `render()` method
*   Components must be properly initialized with required parameters before use
*   Renderable components should be used within the proper inheritance hierarchy
*   Thread safety: Components are stateless and should be safe for concurrent use
*   Flavour conversion functions must operate in-place on the input structure to maintain reference consistency
*   The mapping dictionaries must contain entries for all core renderable types that are expected to be converted
*   The input structure for flavour conversion must be a valid Root instance with properly initialized content
*   All utility functions expect valid pandas Series inputs and appropriate numeric parameters

---

## Files

- [`frequency_table_utils.py`](presentation/frequency_table_utils.md)

