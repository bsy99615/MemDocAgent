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
Provides a standardized interface and base classes for rendering various UI components and report sections in data profiling reports.

## Description:
The core module implements the presentation layer for ydata-profiling report generation. It defines a hierarchy of renderable components that represent different types of UI elements and report sections. These components work together to structure and format data profiling results into consumable reports.

This module establishes a consistent framework for creating structured presentations of data quality insights, visualizations, and metadata. The component hierarchy starts with the abstract base classes (Renderable and ItemRenderer) and builds up to specialized components for specific data types and UI elements.

Primary consumers of this module include the report generation pipeline, which uses these components to construct structured presentations of data profiling results. The module's design promotes extensibility and flexibility, supporting different output formats through its abstract rendering interfaces.

## Components:
- Alerts: Base class for data quality alerts rendering (subclass required)
- Collapse: Collapsible UI component with toggle button and content (subclass required)
- Container: Structural element for grouping renderable components (subclass required)
- CorrelationTable: Specialized renderer for correlation matrix visualization (subclass required)
- Dropdown: Selectable dropdown menu component (subclass required)
- Duplicate: Base renderer for duplicate data visualization (subclass required)
- FrequencyTable: Frequency distribution table component (subclass required)
- FrequencyTableSmall: Compact frequency table renderer (subclass required)
- HTML: Wrapper for raw HTML content rendering (subclass required)
- Image: Image element with metadata for report inclusion (subclass required)
- ItemRenderer: Abstract base class for all specific item renderers
- Renderable: Abstract base class defining the rendering interface
- Root: Top-level container for complete report structure (subclass required)
- Sample: Data sample component for report presentation (subclass required)
- Table: Tabular data renderer (subclass required)
- ToggleButton: Interactive toggle button UI element (subclass required)
- Variable: Structured variable information component (subclass required)
- VariableInfo: Metadata container for variable-specific information (subclass required)

## Public API:
- Alerts: Base class for alert rendering, requires subclassing for implementation
  - Signature: `class Alerts(ItemRenderer)`
- Collapse: Collapsible component with button and content, requires subclassing for rendering
  - Signature: `class Collapse(ItemRenderer)`
- Container: Structural grouping of renderable items, requires subclassing for rendering
  - Signature: `class Container(Renderable)`
- CorrelationTable: Correlation matrix renderer, requires subclassing for implementation
  - Signature: `class CorrelationTable(ItemRenderer)`
- Dropdown: Selectable dropdown menu, requires subclassing for rendering
  - Signature: `class Dropdown(ItemRenderer)`
- Duplicate: Duplicate data visualization, requires subclassing for implementation
  - Signature: `class Duplicate(ItemRenderer)`
- FrequencyTable: Frequency distribution table, requires subclassing for implementation
  - Signature: `class FrequencyTable(ItemRenderer)`
- FrequencyTableSmall: Compact frequency table, requires subclassing for implementation
  - Signature: `class FrequencyTableSmall(ItemRenderer)`
- HTML: Raw HTML content wrapper, requires subclassing for rendering
  - Signature: `class HTML(ItemRenderer)`
- Image: Image element with metadata, requires subclassing for rendering
  - Signature: `class Image(ItemRenderer)`
- ItemRenderer: Abstract base class for item renderers
  - Signature: `class ItemRenderer(Renderable)`
- Renderable: Abstract base class defining rendering interface
  - Signature: `class Renderable`
- Root: Complete report structure container, requires subclassing for rendering
  - Signature: `class Root(ItemRenderer)`
- Sample: Data sample component, requires subclassing for implementation
  - Signature: `class Sample(ItemRenderer)`
- Table: Tabular data renderer, requires subclassing for implementation
  - Signature: `class Table(ItemRenderer)`
- ToggleButton: Interactive toggle button, requires subclassing for rendering
  - Signature: `class ToggleButton(ItemRenderer)`
- Variable: Structured variable information, requires subclassing for implementation
  - Signature: `class Variable(ItemRenderer)`
- VariableInfo: Variable metadata container, requires subclassing for implementation
  - Signature: `class VariableInfo(ItemRenderer)`

## Dependencies:
- Internal: 
  - ydata_profiling.config: Provides Style and ImageType configurations
  - ydata_profiling.report.presentation.core.item_renderer: Base class for item renderers
  - ydata_profiling.report.presentation.core.renderable: Base class for all renderables
- External:
  - pandas: Used for DataFrame handling in several components
  - typing: For type annotations

## Constraints:
- All concrete implementations must implement the abstract render() method
- Components must be properly initialized with required parameters before use
- Renderable components should not modify their internal state during rendering
- Thread safety: Components are stateless and should be safe for concurrent use
- Initialization: All components require proper parameter validation during construction

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

