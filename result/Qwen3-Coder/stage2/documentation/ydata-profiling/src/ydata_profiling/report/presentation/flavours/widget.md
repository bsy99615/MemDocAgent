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
└── variable_info.py

## Role:
Provides concrete implementations of presentation components using ipywidgets for interactive display in Jupyter notebook environments.

## Description:
The widget module implements the widget-based presentation flavour of the ydata-profiling report system. It contains concrete classes that extend abstract base classes from the presentation core to provide interactive UI components specifically designed for Jupyter notebooks. These components leverage ipywidgets to create rich, interactive visualizations and controls that enhance the user experience when exploring data profiling reports in notebook environments.

This module is primarily consumed by the report generation pipeline when widget-based output is requested, and it groups components based on their shared concern of creating interactive UI elements for Jupyter notebooks.

## Components:
*   `WidgetAlerts` - Renders data quality alerts using ipywidgets for interactive display in Jupyter environments
*   `WidgetCollapse` - Implements collapsible UI components using ipywidgets for expanding/collapsing sections in reports
*   `WidgetContainer` - Renders containerized collections of renderable items as interactive ipywidgets
*   `WidgetCorrelationTable` - Renders correlation matrices as interactive widgets in Jupyter environments
*   `WidgetDropdown` - Creates interactive dropdown menus using ipywidgets for dynamic content switching
*   `WidgetDuplicate` - Displays duplicate data findings in an interactive HTML widget format
*   `WidgetFrequencyTable` - Renders categorical frequency data as interactive widgets with styled progress bars
*   `WidgetFrequencyTableSmall` - Specialized rendering for small frequency tables with styled progress bars
*   `WidgetHTML` - Converts HTML content into ipywidgets.HTML objects for Jupyter display
*   `WidgetImage` - Renders image elements as interactive Jupyter widgets for notebook display
*   `WidgetRoot` - Renders complete report presentations using ipywidgets VBox containers
*   `WidgetSample` - Displays data samples in a structured widget layout
*   `WidgetTable` - Renders tabular data as interactive Jupyter widgets with optional captions
*   `WidgetToggleButton` - Creates toggle button UI components using ipywidgets for interactive report presentations
*   `WidgetVariable` - Renders variable content as a vertical box of ipywidgets organizing top and bottom sections
*   `WidgetVariableInfo` - Renders variable information as interactive HTML widgets for Jupyter environments

## Public API:
*   `WidgetAlerts` - Concrete implementation of Alerts for widget-based presentation
*   `WidgetCollapse` - Concrete implementation of Collapse for widget-based collapsible sections
*   `WidgetContainer` - Concrete implementation of Container for widget-based container layouts
*   `WidgetCorrelationTable` - Concrete implementation of CorrelationTable for widget-based correlation displays
*   `WidgetDropdown` - Concrete implementation of Dropdown for widget-based dropdown menus
*   `WidgetDuplicate` - Concrete implementation of Duplicate for widget-based duplicate data displays
*   `WidgetFrequencyTable` - Concrete implementation of FrequencyTable for widget-based frequency displays
*   `WidgetFrequencyTableSmall` - Concrete implementation of FrequencyTableSmall for widget-based small frequency displays
*   `WidgetHTML` - Concrete implementation of HTML for widget-based HTML rendering
*   `WidgetImage` - Concrete implementation of Image for widget-based image displays
*   `WidgetRoot` - Concrete implementation of Root for widget-based complete report rendering
*   `WidgetSample` - Concrete implementation of Sample for widget-based sample displays
*   `WidgetTable` - Concrete implementation of Table for widget-based table displays
*   `WidgetToggleButton` - Concrete implementation of ToggleButton for widget-based toggle buttons
*   `WidgetVariable` - Concrete implementation of Variable for widget-based variable displays
*   `WidgetVariableInfo` - Concrete implementation of VariableInfo for widget-based variable information displays

## Dependencies:
*   Internal: `ydata_profiling.report.presentation.core.*` - Base classes for presentation components
*   Internal: `ydata_profiling.report.presentation.flavours.widget.*` - Other widget components for composition
*   External: `ipywidgets` - Core library for creating interactive Jupyter widgets
*   External: `jinja2` - Template engine for HTML rendering
*   External: `IPython.display` - Display system for Jupyter notebook integration

## Constraints:
*   All components must be instantiated with appropriate content dictionaries matching their expected schema
*   Components must be used within Jupyter notebook environments for proper widget rendering
*   Widget components rely on ipywidgets library which requires proper Jupyter integration
*   Thread safety: Widget components are not thread-safe as they depend on Jupyter's event loop
*   Initialization: Components must be properly initialized with required content before calling render()

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

