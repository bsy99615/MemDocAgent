# `src.ydata_profiling.report.presentation.flavours`

## Tree:
```
flavours/
├── html/
│   ├── alerts/
│   ├── collapse/
│   ├── container/
│   ├── correlation_table/
│   ├── dropdown/
│   ├── duplicate/
│   ├── frequency_table/
│   ├── frequency_table_small/
│   ├── html/
│   ├── image/
│   ├── root/
│   ├── sample/
│   ├── table/
│   ├── templates/
│   ├── toggle_button/
│   ├── variable/
│   └── variable_info/
├── widget/
│   ├── alerts/
│   ├── collapse/
│   ├── container/
│   ├── correlation_table/
│   ├── dropdown/
│   ├── duplicate/
│   ├── frequency_table/
│   ├── frequency_table_small/
│   ├── html/
│   ├── image/
│   ├── notebook/
│   ├── root/
│   ├── sample/
│   ├── table/
│   ├── toggle_button/
│   ├── variable/
│   └── variable_info/
└── flavours.py
```

## Role:
Provides presentation flavour implementations for report generation, enabling rendering of abstract report structures into concrete HTML or Jupyter widget formats.

## Description:
This module implements different presentation flavours for generating reports. It contains two main presentation approaches: HTML-based rendering and Jupyter widget-based rendering. The module serves as a bridge between abstract report structures and their concrete visual representations, allowing the same report data to be rendered in different formats for various use cases.

The module is primarily consumed by the report generation pipeline in the presentation layer, which selects the appropriate flavour based on the output format requested by the user.

## Components:
*   `HTMLReport(structure)` - Converts a report structure to HTML format using HTML-specific renderables
*   `WidgetReport(structure)` - Converts a report structure to Jupyter widget format using widget-specific renderables
*   `apply_renderable_mapping(mapping, structure, flavour)` - Applies a mapping of abstract renderables to concrete implementations
*   `get_html_renderable_mapping()` - Creates a mapping between core renderable types and their HTML implementation counterparts
*   `get_widget_renderable_mapping()` - Creates a mapping between core renderable types and their widget implementation counterparts
*   `to_html(df)` - Converts a DataFrame to HTML string for duplicate display

## Public API:
*   `HTMLReport(structure: Root) -> Root` - Transforms a report structure into HTML-ready format
*   `WidgetReport(structure: Root) -> Root` - Transforms a report structure into widget-ready format
*   `apply_renderable_mapping(mapping: Dict[Type[Renderable], Type[Renderable]], structure: Renderable, flavour: Callable) -> None` - Applies renderable mappings to convert structure elements
*   `get_html_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]` - Provides mapping for HTML renderables
*   `get_widget_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]` - Provides mapping for widget renderables

## Dependencies:
*   Internal: `ydata_profiling.report.presentation.core` - Core renderable classes and base structures
*   Internal: `ydata_profiling.report.presentation.flavours.html` - HTML-specific renderable implementations
*   Internal: `ydata_profiling.report.presentation.flavours.widget` - Widget-specific renderable implementations
*   External: `jinja2` - Template engine for HTML rendering
*   External: `ipywidgets` - Jupyter widget framework for interactive UI components
*   External: `pandas` - Data processing for table rendering

## Constraints:
*   Callers must ensure that the input `structure` parameter is a valid `Root` renderable object
*   The module assumes that all renderable types in the structure have corresponding implementations in the mapping dictionaries
*   Thread safety is not guaranteed; concurrent usage may cause issues with global template configurations
*   The HTML flavour requires proper template files to be available in the templates directory
*   The widget flavour requires Jupyter environment to be properly configured

---

## Files

- [`flavours.py`](flavours/flavours.md)

