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
Provides a standardized framework for rendering data profiling reports in different presentation formats.

## Description:
The presentation module implements a flexible architecture for generating structured data profiling reports that can be rendered in multiple formats (HTML, Jupyter widgets). It provides a hierarchical component system for building report structures and mechanisms for transforming these structures into specific presentation flavours.

This module serves as the UI layer of the ydata-profiling system, separating the data analysis logic from the presentation concerns. It enables consistent report generation across different environments while maintaining extensibility for new presentation formats.

Primary consumers of this module include the main report generation pipeline, which uses these components to construct structured presentations of data quality insights, visualizations, and metadata. The module's design promotes reuse and flexibility, allowing the same underlying data model to be presented in different ways depending on the target environment.

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
- HTMLReport: Converts a Root structure to HTML-flavored renderable components by applying an HTML renderable mapping
- WidgetReport: Converts a Root structure to widget-based renderable components for Jupyter notebook presentations by applying a widget renderable mapping
- apply_renderable_mapping: Generic utility for applying flavour-specific type mappings to convert renderable components
- get_html_renderable_mapping: Creates mapping from core renderable types to their HTML implementation counterparts
- get_widget_renderable_mapping: Creates mapping from core renderable types to their widget implementation counterparts
- _extreme_obs_table: Processes frequency table to extract top observations and format them into a structured list of dictionaries
- _frequency_table: Transforms frequency counts into standardized table format for visualization
- extreme_obs_table: Wrapper for creating extreme observations tables from frequency data
- freq_table: Dispatcher for processing frequency tables into visualization-ready format

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
- HTMLReport(structure: Root) - Converts a Root structure containing base renderable components to their HTML-specific implementations. Modifies the structure in-place and returns it.
- WidgetReport(structure: Root) - Converts a Root structure containing base renderable components to their widget-based implementations for Jupyter notebooks. Modifies the structure in-place and returns it.
- apply_renderable_mapping(mapping: Dict[Type[Renderable], Type[Renderable]], structure: Renderable, flavour: Callable) - Applies a mapping dictionary to convert a renderable structure from one flavour to another by changing the runtime class of components.
- get_html_renderable_mapping() - Returns a dictionary mapping core renderable types to their HTML implementation classes.
- get_widget_renderable_mapping() - Returns a dictionary mapping core renderable types to their widget implementation classes.
- _extreme_obs_table(freqtable: pd.Series, number_to_print: int, n: int) - Processes a frequency table to extract top observations and format them into a structured list of dictionaries suitable for presentation.
- _frequency_table(freqtable: pd.Series, n: int, max_number_to_print: int) - Transforms a frequency table into a standardized list of dictionary entries for visualization, handling special cases like "Other values" and missing data.
- extreme_obs_table(freqtable: Union[pd.Series, List[pd.Series]], number_to_print: int, n: Union[int, List[int]]) - Creates formatted table representations of extreme observations from frequency distributions for presentation purposes.
- freq_table(freqtable: Union[pd.Series, List[pd.Series]], n: Union[int, List[int]], max_number_to_print: int) - Creates standardized frequency table representations for visualization by processing raw frequency data through internal transformation functions.

## Dependencies:
- Internal:
  - ydata_profiling.config: Provides Style and ImageType configurations
  - ydata_profiling.report.presentation.core: Base renderable component definitions and abstract interfaces
  - ydata_profiling.report.presentation.core.item_renderer: Base class for item renderers
  - ydata_profiling.report.presentation.core.renderable: Base class for all renderables
  - ydata_profiling.report.presentation.flavours.html: HTML-specific renderable implementations
  - ydata_profiling.report.presentation.flavours.widget: Widget-specific renderable implementations
- External:
  - pandas: Used for DataFrame handling in several components
  - typing: For type annotations

## Constraints:
- All concrete implementations must implement the abstract render() method
- Components must be properly initialized with required parameters before use
- Renderable components should not modify their internal state during rendering
- Thread safety: Components are stateless and should be safe for concurrent use
- Initialization: All components require proper parameter validation during construction
- All transformations require that the target flavour implementations exist for all renderable types in the structure
- The mapping functions must return complete dictionaries with all required type mappings
- Transformations modify the structure in-place, so the original structure is altered
- The caller must ensure that the appropriate flavour-specific implementations are available in the respective submodules
- All renderable components must be of types that exist in the mapping dictionaries

---

## Files

- [`frequency_table_utils.py`](presentation/frequency_table_utils.md)

