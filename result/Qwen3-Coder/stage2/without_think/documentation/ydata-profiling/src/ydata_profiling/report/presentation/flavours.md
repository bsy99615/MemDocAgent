# `src.ydata_profiling.report.presentation.flavours`

## Tree:
```
flavours/
├── html/
├── widget/
└── flavours.py
```

## Role:
Provides presentation flavour conversion mechanisms that transform generic report structures into flavour-specific representations for HTML and widget-based outputs.

## Description:
This module serves as the central coordination point for converting generic report structures into flavour-specific presentations. It contains the core logic for applying type mappings that transform abstract renderable components into their concrete implementations for different presentation formats (HTML, widgets). The module acts as a bridge between the generic presentation layer and flavour-specific implementations, enabling flexible report generation for different output targets.

The module is organized around the concept of presentation flavours, where each flavour (HTML, widget) has its own set of concrete implementations that handle the actual rendering logic. This module provides the infrastructure to apply these flavour-specific mappings to generic report structures.

Primary consumers of this module include:
- Report generation pipeline components that need to convert generic structures to specific presentation formats
- Presentation layer factories that manage flavour selection and application
- Core report processing systems that require flavour-specific transformations

The cohesion of this module is based on the shared responsibility of managing presentation flavour conversions, providing a consistent interface for applying different rendering strategies to the same underlying data structures.

## Components:
* `HTMLReport` - Converts a generic report structure into its HTML-specific representation by applying the HTML renderable mapping
* `WidgetReport` - Converts a generic report structure into its widget-specific representation by applying the widget renderable mapping  
* `apply_renderable_mapping` - Applies a type mapping to convert a renderable structure to its flavour-specific representation
* `get_html_renderable_mapping` - Creates a mapping from core renderable types to their HTML implementation types
* `get_widget_renderable_mapping` - Creates a mapping from core renderable types to their widget implementation types

```mermaid
graph TD
    A[HTMLReport] --> B[get_html_renderable_mapping()]
    B --> C[mapping_dict]
    C --> D[apply_renderable_mapping(mapping_dict, structure, HTMLReport)]
    D --> E[structure converted to HTML flavour]
    
    F[WidgetReport] --> G[get_widget_renderable_mapping()]
    G --> H[mapping_dict]
    H --> I[apply_renderable_mapping(mapping_dict, structure, WidgetReport)]
    I --> J[structure converted to widget flavour]
    
    K[apply_renderable_mapping] --> L[structure type lookup]
    L --> M{type in mapping?}
    M -->|Yes| N[convert_to_class call]
    N --> O[structure modified in-place]
    M -->|No| P[KeyError]
    
    Q[get_html_renderable_mapping] --> R[Core -> HTML type mappings]
    
    S[get_widget_renderable_mapping] --> T[Core -> Widget type mappings]
```

## Public API:
* `HTMLReport(structure)` - Transforms a generic Root structure into its HTML presentation form by applying HTML-specific renderable mappings
* `WidgetReport(structure)` - Transforms a generic Root structure into its widget-based presentation form by applying widget-specific renderable mappings
* `apply_renderable_mapping(mapping, structure, flavour)` - Applies a type mapping to convert a renderable structure to its flavour-specific representation
* `get_html_renderable_mapping()` - Returns a dictionary mapping core renderable types to their HTML implementations
* `get_widget_renderable_mapping()` - Returns a dictionary mapping core renderable types to their widget implementations

## Dependencies:
* Internal: `ydata_profiling.report.presentation.core` - Core presentation classes that define the abstract interfaces
* Internal: `ydata_profiling.report.presentation.flavours.html` - HTML-specific implementations for rendering
* Internal: `ydata_profiling.report.presentation.flavours.widget` - Widget-specific implementations for interactive display
* External: `typing` - Type hints for better code documentation and IDE support

## Constraints:
* All flavour conversion functions must operate in-place on the input structure to maintain reference consistency
* The mapping dictionaries must contain entries for all core renderable types that are expected to be converted
* The input structure must be a valid Root instance with properly initialized content
* Thread safety: Functions are stateless and can be safely used in multi-threaded environments
* Initialization: The mapping functions should be called after all flavour-specific implementations are properly imported

---

## Files

- [`flavours.py`](flavours/flavours.md)

