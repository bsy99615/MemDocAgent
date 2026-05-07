# `src.ydata_profiling.report.presentation.flavours.widget`

## Tree:
widget/
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
├── notebook.py
├── root.py
├── sample.py
├── table.py
├── toggle_button.py
├── variable.py
├── variable_info.py

## Role:
Provides a collection of interactive Jupyter widgets for rendering data profiling reports with rich visualizations and structured layouts.

## Description:
This module implements a set of custom Jupyter widgets specifically designed for presenting data profiling results in a Jupyter notebook environment. It serves as the presentation layer for the ydata-profiling library, transforming structured report data into interactive, visually appealing components that can be displayed in Jupyter notebooks.

The module is consumed primarily by the report generation pipeline in the presentation layer, which orchestrates the assembly of various widget components into complete profiling reports. These widgets handle everything from simple HTML displays to complex interactive elements like collapsible sections, dropdown selectors, and statistical tables.

## Components:
*   `WidgetAlerts` - Renders visual alerts for data quality issues using styled buttons and HTML elements
*   `WidgetCollapse` - Creates collapsible sections that can expand/collapse content with interactive toggles
*   `WidgetContainer` - Manages layout containers for organizing multiple widgets in various arrangements (lists, tabs, grids, etc.)
*   `WidgetCorrelationTable` - Displays correlation matrices in an interactive output widget
*   `WidgetDropdown` - Implements dropdown selectors that control visibility of associated content
*   `WidgetDuplicate` - Shows duplicate data findings in an interactive output widget
*   `WidgetFrequencyTable` - Renders frequency distributions with progress bars and labels
*   `WidgetFrequencyTableSmall` - Displays smaller frequency tables optimized for compact views
*   `WidgetHTML` - Wraps raw HTML content for display in Jupyter notebooks
*   `WidgetImage` - Handles image display with optional captions and formatting adjustments
*   `WidgetRoot` - Provides the main container structure for complete report layouts
*   `WidgetSample` - Displays sample data in an interactive output widget
*   `WidgetTable` - Renders structured data tables with optional captions
*   `WidgetToggleButton` - Creates toggle buttons for interactive user controls
*   `WidgetVariable` - Organizes variable-specific content into top/bottom sections
*   `WidgetVariableInfo` - Displays detailed information about individual variables

## Public API:
The module exposes all widget classes as part of its public interface. Each widget implements a `render()` method that returns a Jupyter widget object suitable for display in notebooks.

## Dependencies:
*   `ipywidgets` - Core library for creating interactive Jupyter widgets
*   `jinja2` - Template engine for rendering HTML templates
*   `ydata_profiling.report.presentation.flavours.widget.container` - Utility functions for widget layouts
*   `ydata_profiling.report.presentation.flavours.widget.templates` - HTML template management
*   `ydata_profiling.report.presentation.flavours.widget.utils` - Utility functions for widget operations

## Constraints:
*   All widgets must be rendered within a Jupyter notebook environment to function properly
*   Widgets depend on proper initialization of the `content` dictionary with required keys
*   Layout-related widgets require appropriate sizing and positioning configurations
*   Interactive widgets (toggle, dropdown) require proper event handling setup

---

## Files

- [`alerts.py`](widget/alerts.md)
- [`collapse.py`](widget/collapse.md)
- [`container.py`](widget/container.md)
- [`correlation_table.py`](widget/correlation_table.md)
- [`dropdown.py`](widget/dropdown.md)
- [`duplicate.py`](widget/duplicate.md)
- [`frequency_table.py`](widget/frequency_table.md)
- [`frequency_table_small.py`](widget/frequency_table_small.md)
- [`html.py`](widget/html.md)
- [`image.py`](widget/image.md)
- [`notebook.py`](widget/notebook.md)
- [`root.py`](widget/root.md)
- [`sample.py`](widget/sample.md)
- [`table.py`](widget/table.md)
- [`toggle_button.py`](widget/toggle_button.md)
- [`variable.py`](widget/variable.md)
- [`variable_info.py`](widget/variable_info.md)

