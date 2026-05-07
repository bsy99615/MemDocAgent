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
Provides concrete implementations of UI components for widget-based data profiling report presentations in Jupyter notebooks.

## Description:
The widget module implements a comprehensive suite of interactive UI components specifically designed for rendering data profiling reports in Jupyter notebook environments. These components leverage ipywidgets to create rich, interactive visualizations that enable users to explore and understand their data effectively.

This module serves as the presentation layer for the widget-based flavour of ydata-profiling reports, transforming abstract data representations into concrete interactive widgets. It provides both fundamental building blocks (like containers and basic elements) and specialized components (like frequency tables, correlation matrices, and variable information displays) that work together to create comprehensive data profiling dashboards.

## Components:
*   **WidgetAlerts**: Renders data quality alerts as interactive ipywidgets in a grid layout
*   **WidgetCollapse**: Implements collapsible UI components using ipywidgets for interactive report presentations
*   **WidgetContainer**: Renders container content as specific widget types based on sequence configuration
*   **WidgetCorrelationTable**: Renders correlation matrix data as an interactive ipywidgets VBox component
*   **WidgetDropdown**: Creates interactive dropdown widgets for selecting and displaying associated content
*   **WidgetDuplicate**: Displays duplicate data findings in a structured widget format
*   **WidgetFrequencyTable**: Creates interactive widget-based frequency table displays with colored progress bars
*   **WidgetFrequencyTableSmall**: Specialized renderer for small frequency tables using ipywidgets
*   **WidgetHTML**: Renders HTML content as ipywidgets.HTML objects for interactive notebook display
*   **WidgetImage**: Displays image elements as interactive Jupyter widgets with optional captions
*   **WidgetRoot**: Renders content as a vertical box widget for Jupyter notebook interfaces
*   **WidgetSample**: Renders data samples using ipywidgets for interactive Jupyter notebook display
*   **WidgetTable**: Creates widget-based table presentations with optional captions
*   **WidgetToggleButton**: Renders interactive toggle buttons using ipywidgets for Jupyter notebooks
*   **WidgetVariable**: Renders variable content as an interactive IPython widget VBox container
*   **WidgetVariableInfo**: Renders variable information as interactive HTML widgets for Jupyter environments

## Public API:
*   **WidgetAlerts(content)**: Renders data quality alerts as interactive ipywidgets in a grid layout
*   **WidgetCollapse(button, item)**: Renders collapsible UI components using ipywidgets
*   **WidgetContainer(sequence_type, content)**: Renders container content as specific widget types
*   **WidgetCorrelationTable(content)**: Renders correlation matrix data as an interactive ipywidgets VBox component
*   **WidgetDropdown(content)**: Creates interactive dropdown widgets for content selection
*   **WidgetDuplicate(name, duplicate)**: Displays duplicate data findings in a structured widget format
*   **WidgetFrequencyTable(content)**: Creates interactive widget-based frequency table displays
*   **WidgetFrequencyTableSmall(rows, redact)**: Specialized renderer for small frequency tables
*   **WidgetHTML(html, name, anchor_id, classes)**: Renders HTML content as ipywidgets.HTML objects
*   **WidgetImage(image, image_format, alt, caption)**: Displays image elements as interactive Jupyter widgets
*   **WidgetRoot()**: Renders content as a vertical box widget for Jupyter notebook interfaces
*   **WidgetSample(name, sample, caption)**: Renders data samples using ipywidgets
*   **WidgetTable(content)**: Creates widget-based table presentations with optional captions
*   **WidgetToggleButton(text, name, anchor_id, classes)**: Renders interactive toggle buttons
*   **WidgetVariable(top, bottom, ignore)**: Renders variable content as an interactive widget container
*   **WidgetVariableInfo(content)**: Renders variable information as interactive HTML widgets

## Dependencies:
*   **Internal**: 
    *   `ydata_profiling.report.presentation.core` - Base classes and abstract interfaces
    *   `ydata_profiling.report.presentation.flavours.widget.alerts` - Alert rendering utilities
    *   `ydata_profiling.report.presentation.flavours.widget.container` - Container layout helpers
    *   `ydata_profiling.report.presentation.flavours.widget.notebook` - Notebook-specific iframe handling
*   **External**: 
    *   `ipywidgets` - Core library for creating interactive Jupyter widgets
    *   `jinja2` - Template engine for HTML rendering
    *   `IPython.display` - Display system for Jupyter notebook integration

## Constraints:
*   All components must be instantiated with valid content structures that match their expected interfaces
*   Components depend on ipywidgets being available in the execution environment
*   Widget-based rendering requires Jupyter notebook context for proper display
*   All render methods must return valid ipywidgets objects compatible with Jupyter frontend
*   Components should be thread-safe as they are typically used in single-threaded notebook environments

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

