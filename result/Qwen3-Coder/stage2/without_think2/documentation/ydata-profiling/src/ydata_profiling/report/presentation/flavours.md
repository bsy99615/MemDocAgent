# `src.ydata_profiling.report.presentation.flavours`

## Tree:
flavours/
├── html/
├── widget/
└── flavours.py

## Role:
Provides presentation flavour implementations for ydata-profiling reports, enabling different output formats (HTML, widgets) through consistent interfaces.

## Description:
This module serves as the central coordination point for implementing different presentation flavours of ydata-profiling reports. It defines the core conversion mechanisms that transform abstract report structures into concrete presentation formats like HTML or interactive widgets. The module enforces a clean separation between report structure definition and presentation implementation, allowing for flexible output generation while maintaining consistent interfaces across different formats.

The module is used by the report generation pipeline to select and apply appropriate presentation transformations based on desired output format. It groups related functionality around the concept of "presentation flavours" - distinct ways of rendering the same underlying report data.

## Components:
* `HTMLReport` - Entry point for converting report structures to HTML presentation
* `WidgetReport` - Entry point for converting report structures to widget-based presentation  
* `apply_renderable_mapping` - Core dispatcher for applying flavour-specific type mappings
* `get_html_renderable_mapping` - Function that returns a mapping from core renderable types to HTML implementations
* `get_widget_renderable_mapping` - Function that returns a mapping from core renderable types to widget implementations

## Public API:
* `HTMLReport(structure: Root)` - Converts a report structure to HTML-ready components
* `WidgetReport(structure: Root)` - Converts a report structure to widget-ready components
* `apply_renderable_mapping(mapping: Dict[Type[Renderable], Type[Renderable]], structure: Renderable, flavour: Callable)` - Applies a type mapping to convert a structure to a specific flavour
* `get_html_renderable_mapping()` - Returns a mapping dictionary from core renderable types to their HTML implementations
* `get_widget_renderable_mapping()` - Returns a mapping dictionary from core renderable types to their widget implementations

## Dependencies:
* Internal: `ydata_profiling.report.presentation.core` - Base renderable classes and interfaces
* Internal: `ydata_profiling.report.presentation.flavours.html` - HTML-specific renderable implementations
* Internal: `ydata_profiling.report.presentation.flavours.widget` - Widget-specific renderable implementations
* External: `typing` - Type hinting support
* External: `collections.abc` - Abstract base classes for sequence types

## Constraints:
* All presentation flavour functions must be called with valid Root instances
* Type mappings must be complete and consistent for all supported renderable types
* Conversion operations modify objects in-place rather than creating new instances
* Presentation flavour selection must happen before rendering operations

---

## Files

- [`flavours.py`](flavours/flavours.md)

