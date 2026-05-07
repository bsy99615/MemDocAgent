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
Provides widget-based presentation implementations for ydata-profiling reports in Jupyter environments

## Description:
The widget module implements the widget-based presentation flavour for ydata-profiling reports. It provides concrete implementations of various report components using ipywidgets to enable interactive visualization in Jupyter notebooks. This module bridges the gap between abstract report structures and concrete widget-based UI elements, making data profiling reports highly interactive and exploratory.

Primary consumers include the report generation pipeline and Jupyter notebook environments where interactive widgets are supported. The module is organized around specific presentation components (tables, alerts, variables, etc.) that are rendered using ipywidgets for enhanced user experience.

## Components:
*   `WidgetAlerts` - Renders data quality alerts using ipywidgets GridBox layout
*   `WidgetCollapse` - Implements collapsible sections with interactive toggle buttons
*   `WidgetContainer` - Converts structured containers into widget-based layouts
*   `WidgetCorrelationTable` - Displays correlation matrices in widget format
*   `WidgetDropdown` - Creates interactive dropdown selectors for content navigation
*   `WidgetDuplicate` - Renders duplicate data findings with title headers
*   `WidgetFrequencyTable` - Visualizes categorical frequency distributions with progress bars
*   `WidgetFrequencyTableSmall` - Renders compact frequency tables for smaller displays
*   `WidgetHTML` - Transforms HTML content into interactive ipywidgets.HTML elements
*   `WidgetImage` - Displays images with responsive styling and optional captions
*   `WidgetRoot` - Provides the main report container structure using VBox layout
*   `WidgetSample` - Renders data samples with styled headers and interactive outputs
*   `WidgetTable` - Displays tabular data with optional captions using GridspecLayout
*   `WidgetToggleButton` - Creates styled toggle buttons for interactive UI controls
*   `WidgetVariable` - Organizes variable content into top/bottom sections
*   `WidgetVariableInfo` - Presents variable metadata and alerts in HTML format

## Public API:
*   `WidgetAlerts(content: dict)` - Renders alerts as grid of HTML content and styled buttons
*   `WidgetCollapse(button: ToggleButton, item: Renderable)` - Creates collapsible sections with toggle functionality
*   `WidgetContainer(items: Sequence[Renderable], sequence_type: str)` - Converts containers to widget layouts
*   `WidgetCorrelationTable(name: str, correlation_matrix: pd.DataFrame)` - Displays correlation matrices with title headers
*   `WidgetDropdown(content: dict)` - Renders interactive dropdown menus with nested content control
*   `WidgetDuplicate(name: str, duplicate: Any)` - Shows duplicate data findings with title and output display
*   `WidgetFrequencyTable(rows: List[Dict], redact: bool)` - Renders frequency tables with progress bars and count labels
*   `WidgetFrequencyTableSmall(rows: List[List[Dict]], redact: bool)` - Renders compact frequency tables
*   `WidgetHTML(html: str)` - Converts HTML strings to interactive ipywidgets.HTML widgets
*   `WidgetImage(image: str, image_format: ImageType, alt: str, caption: Optional[str])` - Displays images with responsive styling
*   `WidgetRoot(name: str, body: Renderable, footer: Renderable, style: Style)` - Creates main report container structure
*   `WidgetSample(name: str, sample: Any, caption: Optional[str])` - Renders data samples with styled headers
*   `WidgetTable(rows: List[Dict], style: Style, caption: Optional[str])` - Displays tabular data with optional captions
*   `WidgetToggleButton(text: str)` - Creates styled toggle buttons for UI controls
*   `WidgetVariable(top: Renderable, bottom: Optional[Renderable])` - Organizes variable content sections
*   `WidgetVariableInfo(anchor_id: str, var_name: str, var_type: str, alerts: List[Alert], description: str, style: Style)` - Presents variable metadata and alerts

## Dependencies:
*   Internal: `ydata_profiling.report.presentation.core` - Base classes and abstract interfaces
*   Internal: `ydata_profiling.report.presentation.flavours.widget.alerts` - Alert rendering utilities
*   Internal: `ydata_profiling.report.presentation.flavours.widget.container` - Container layout helpers
*   Internal: `ydata_profiling.config` - Configuration and styling definitions
*   Internal: `ydata_profiling.model.alerts` - Alert data models
*   External: `ipywidgets` - Core widget library for interactive UI components
*   External: `jinja2` - Template engine for HTML rendering
*   External: `IPython.display` - Display system for Jupyter integration

## Constraints:
*   All components must be instantiated with valid content structures matching their parent class expectations
*   Widget-based rendering requires ipywidgets to be available in the execution environment
*   Jupyter notebook environments are required for full interactive functionality
*   All render methods must return valid ipywidgets objects compatible with Jupyter display system
*   Template-based components require valid Jinja2 templates to be present in the template directory

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

