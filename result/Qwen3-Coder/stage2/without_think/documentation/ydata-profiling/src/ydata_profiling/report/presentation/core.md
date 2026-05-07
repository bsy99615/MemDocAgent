# `src.ydata_profiling.report.presentation.core`

## Tree:
core/
├── alerts.py
├── collapse.py
├── container.py
├── correlation_table.py
├── dropdown.py
├── duplicate.py
├── frequency_table.py
├── frequency_table_small.py
├── html.py
├── image.py
├── item_renderer.py
├── renderable.py
├── root.py
├── sample.py
├── table.py
├── toggle_button.py
├── variable.py
├── variable_info.py

## Role:
Provides the foundational rendering infrastructure and concrete presentation components for generating data profiling reports.

## Description:
The core presentation layer module serves as the foundation for all report generation in ydata-profiling. It defines the abstract base classes and concrete implementations for various UI components that make up data profiling reports. This module handles the structural organization and rendering of report elements, from basic components like text and images to complex structures like tables, containers, and interactive elements.

The module follows a clear inheritance hierarchy:
- `Renderable` is the base class for all presentation elements
- `ItemRenderer` extends `Renderable` with item-type identification and content management
- Specific component classes inherit from `ItemRenderer` to provide concrete implementations

This architecture enables consistent handling of different report elements while supporting flexible rendering strategies for various output formats.

## Components:
*   `alerts.py` - Alert presentation components for displaying data quality issues
*   `collapse.py` - Collapsible UI components with toggle functionality
*   `container.py` - Structural containers for grouping renderable components
*   `correlation_table.py` - Correlation matrix visualization components
*   `dropdown.py` - Dropdown menu UI elements
*   `duplicate.py` - Duplicate data reporting components
*   `frequency_table.py` - Frequency distribution table components
*   `frequency_table_small.py` - Compact frequency table components
*   `html.py` - Raw HTML content rendering components
*   `image.py` - Image display components for charts and visualizations
*   `item_renderer.py` - Abstract base class for item-based renderers
*   `renderable.py` - Abstract base class for all presentation elements
*   `root.py` - Top-level report container and entry point
*   `sample.py` - Data sample display components
*   `table.py` - Tabular data presentation components
*   `toggle_button.py` - Interactive toggle button components
*   `variable.py` - Variable information presentation components
*   `variable_info.py` - Detailed variable metadata presentation components

## Public API:
*   `alerts.Alerts` - Renders collections of data quality alerts
*   `collapse.Collapse` - Collapsible UI component with toggle button and content
*   `container.Container` - Structural container for grouping renderable items
*   `correlation_table.CorrelationTable` - Correlation matrix visualization
*   `dropdown.Dropdown` - Dropdown menu UI element
*   `duplicate.Duplicate` - Duplicate data reporting component
*   `frequency_table.FrequencyTable` - Frequency distribution table
*   `frequency_table_small.FrequencyTableSmall` - Compact frequency table
*   `html.HTML` - Raw HTML content rendering
*   `image.Image` - Image display component
*   `item_renderer.ItemRenderer` - Base class for item-based renderers
*   `renderable.Renderable` - Base class for all presentation elements
*   `root.Root` - Top-level report container
*   `sample.Sample` - Data sample display component
*   `table.Table` - Tabular data presentation
*   `toggle_button.ToggleButton` - Interactive toggle button
*   `variable.Variable` - Variable information presentation
*   `variable_info.VariableInfo` - Detailed variable metadata presentation

## Dependencies:
*   Internal: `ydata_profiling.config.Style` - Styling configuration for reports
*   Internal: `ydata_profiling.model.alerts.Alert` - Data quality alert definitions
*   Internal: `ydata_profiling.config.ImageType` - Image format enumeration
*   External: `pandas` - Data manipulation and DataFrame handling
*   External: `typing` - Type hinting support

## Constraints:
*   All concrete classes must implement the abstract `render()` method
*   Components must be properly initialized with required parameters before use
*   Renderable components should be used within the proper inheritance hierarchy
*   Thread safety: Components are stateless and should be safe for concurrent use
*   Initialization order: Parent classes must be initialized before child classes

---

## Files

- [`alerts.py`](core/alerts.md)
- [`collapse.py`](core/collapse.md)
- [`container.py`](core/container.md)
- [`correlation_table.py`](core/correlation_table.md)
- [`dropdown.py`](core/dropdown.md)
- [`duplicate.py`](core/duplicate.md)
- [`frequency_table.py`](core/frequency_table.md)
- [`frequency_table_small.py`](core/frequency_table_small.md)
- [`html.py`](core/html.md)
- [`image.py`](core/image.md)
- [`item_renderer.py`](core/item_renderer.md)
- [`renderable.py`](core/renderable.md)
- [`root.py`](core/root.md)
- [`sample.py`](core/sample.md)
- [`table.py`](core/table.md)
- [`toggle_button.py`](core/toggle_button.md)
- [`variable.py`](core/variable.md)
- [`variable_info.py`](core/variable_info.md)

