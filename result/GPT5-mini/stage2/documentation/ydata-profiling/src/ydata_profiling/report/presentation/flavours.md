# `src.ydata_profiling.report.presentation.flavours`

## Tree:
flavours/
├── html/
├── widget/
└── flavours.py

## Role:
Provide the presentation-layer "flavour" boundary that constructs flavour-specific mappings and the minimal conversion helpers that turn canonical Renderable instances into flavour-specific implementations.

## Description:
Where and when this module is used
- Primary consumers:
  - Presentation factories and renderer construction code that need to select concrete implementations for canonical Renderable types when producing output in a particular flavour (e.g., HTML, widget).
  - Report assembly or traversal code that converts a pre-built canonical Renderable tree into a flavour-specific tree immediately prior to rendering.
  - Any orchestration code that selects the "html" or "widget" flavour for output.
- Typical usage phase:
  - During report generation, after a canonical Renderable tree (Root) has been built by core presentation code and an output flavour has been chosen, callers use the mapping constructors to obtain core->flavour type associations and then apply the conversion helper (or the flavour entry points) to convert nodes in-place.

Why these components are grouped together
- Cohesion principle: this module centralizes two related responsibilities: (1) building flavour-specific mappings that pair canonical core Renderable classes with concrete flavour implementations (html/ and widget/), and (2) providing a single-step conversion helper and small flavour entry-points that consistently apply those mappings. Grouping supports lazy imports, avoids import cycles, and keeps conversion semantics consistent across the presentation layer.

## Components:
- get_html_renderable_mapping() -> dict[Type[Renderable], Type[Renderable]]
  - Returns the mapping from core Renderable types to HTML-specific Renderable classes.
  - See component-level documentation: src.ydata_profiling.report.presentation.flavours.flavours.get_html_renderable_mapping

- get_widget_renderable_mapping() -> dict[Type[Renderable], Type[Renderable]]
  - Returns the mapping from core Renderable types to widget-specific Renderable classes.
  - Important: this function only constructs and returns the mapping; it does not perform any conversion of Renderable instances.
  - See component-level documentation: src.ydata_profiling.report.presentation.flavours.flavours.get_widget_renderable_mapping

- apply_renderable_mapping(mapping: Dict[Type[Renderable], Type[Renderable]], structure: Renderable, flavour: Callable) -> None
  - Perform an exact-type lookup (type(structure)) in mapping and call the mapped class's convert_to_class(structure, flavour) to convert the instance in-place.
  - See component-level documentation: src.ydata_profiling.report.presentation.flavours.flavours.apply_renderable_mapping

- HTMLReport(structure: Root) -> Root
  - Flavour conversion entry point for HTML. Obtains the HTML mapping via get_html_renderable_mapping() and delegates to apply_renderable_mapping to convert the provided Root in-place, then returns that same Root instance (typically mutated).
  - See component-level documentation: src.ydata_profiling.report.presentation.flavours.flavours.HTMLReport

- WidgetReport(structure: Root) -> Root
  - Flavour conversion entry point for widget. Obtains the widget mapping via get_widget_renderable_mapping() and delegates to apply_renderable_mapping to convert the provided Root in-place, then returns that same Root instance (typically mutated).
  - See component-level documentation: src.ydata_profiling.report.presentation.flavours.flavours.WidgetReport

Mermaid dependency graph (internal relationships)
graph LR
  CoreTypes[core Renderable types (presentation.core)]
  getHTML[get_html_renderable_mapping()]
  getWidget[get_widget_renderable_mapping()]
  apply[apply_renderable_mapping(mapping, structure, flavour)]
  HTMLReportNode[HTMLReport(structure)]
  WidgetReportNode[WidgetReport(structure)]
  HTMLImpls[flavours.html: HTML-specific classes]
  WidgetImpls[flavours.widget: widget-specific classes]
  ConvertToClass[<mapped_class>.convert_to_class(structure, flavour)]

  CoreTypes --> getHTML
  CoreTypes --> getWidget
  getHTML --> HTMLImpls
  getWidget --> WidgetImpls
  HTMLReportNode --> getHTML
  HTMLReportNode --> apply
  WidgetReportNode --> getWidget
  WidgetReportNode --> apply
  apply --> ConvertToClass
  ConvertToClass --> HTMLImpls
  ConvertToClass --> WidgetImpls

## Public API:
- get_html_renderable_mapping() -> dict[Type[Renderable], Type[Renderable]]
  - Description: Build and return a dict mapping canonical core Renderable classes to HTML-specific implementations.
  - Usage note: Imports are local to the function; callers should handle ImportError/ModuleNotFoundError if HTML flavour dependencies are unavailable. The returned mapping is intended for exact-type lookups (type(obj)).

- get_widget_renderable_mapping() -> dict[Type[Renderable], Type[Renderable]]
  - Description: Build and return a dict mapping canonical core Renderable classes to widget-specific implementations.
  - Usage note: This function does not perform any conversion itself — it only returns the mapping. Callers that need to convert an instance should pass the mapping to apply_renderable_mapping or call the WidgetReport entry point.

- apply_renderable_mapping(mapping, structure, flavour) -> None
  - Description: Convert the provided structure in-place by looking up mapping[type(structure)] and calling its convert_to_class(structure, flavour).
  - Usage note: Performs an exact runtime-type lookup; does not perform subclass/isinstance matching. Does not catch exceptions from mapping lookup or convert_to_class — callers should handle KeyError, AttributeError, TypeError, ImportError, and any exceptions thrown by convert_to_class.

- HTMLReport(structure) -> Root
  - Description: Convert the supplied Root to the HTML flavour by calling get_html_renderable_mapping() and delegating to apply_renderable_mapping; returns the (mutated) Root instance.
  - Usage note: Use this entry point when preparing a canonical Root for HTML rendering. Guard against ImportError and KeyError.

- WidgetReport(structure) -> Root
  - Description: Convert the supplied Root to the widget flavour by calling get_widget_renderable_mapping() and delegating to apply_renderable_mapping; returns the (mutated) Root instance.
  - Usage note: Use this entry point when preparing a canonical Root for widget rendering. Guard against ImportError and KeyError.

## Dependencies:
Internal (repository) imports
- ydata_profiling.report.presentation.core
  - Purpose: defines canonical Renderable types used as mapping keys (e.g., Container, Variable, VariableInfo, Table, Root, Image, FrequencyTable, etc.).
- ydata_profiling.report.presentation.flavours.html (package)
  - Purpose: provides HTML flavour concrete Renderable implementations that are the values in the HTML mapping.
- ydata_profiling.report.presentation.flavours.widget (package)
  - Purpose: provides widget flavour concrete Renderable implementations that are the values in the widget mapping.
- Internal relationships:
  - Mapping functions import core types and flavour-specific implementations locally and return dictionaries pairing them.
  - apply_renderable_mapping expects mapping values to expose a callable convert_to_class.

External (stdlib / third-party) imports
- typing (Dict, Type, Callable) — used for type hints and documenting mapping signatures.
- Flavour implementation modules (html/ and widget/) may have additional external deps; those are not required by this module's helpers themselves.

## Constraints:
- Exact-type lookup
  - All mapping lookups use the exact runtime type (type(structure)) as the key. Subclass or isinstance-style matching is not performed. Callers must ensure mapping contains an entry for the exact runtime class of the object being converted, or handle KeyError.

- Initialization / import prerequisites
  - The mapping builder functions perform local imports when called; the modules providing the core types and flavour implementations must be importable. Missing modules will raise ImportError/ModuleNotFoundError at call time.

- In-place mutation and threading
  - Conversions are typically performed in-place via mapped_class.convert_to_class, which commonly assigns to structure.__class__ and mutates nested attributes. Because of these in-place mutations, conversions are not inherently thread-safe — concurrent conversions or concurrent reads of structures undergoing conversion can produce race conditions. If concurrent access is possible, callers must synchronize conversions externally.

- Ordering and recursion
  - convert_to_class implementations may perform recursive conversion of nested Renderable nodes by calling back into the flavour callable (HTMLReport or WidgetReport). Callers should expect recursive traversal and not assume a traversal order beyond what convert_to_class implements.

- Error propagation
  - apply_renderable_mapping and the flavour entry points intentionally do not catch or wrap exceptions: KeyError for missing mapping keys, AttributeError for missing convert_to_class, TypeError for invalid operations, ImportError for missing dependencies, and any exceptions thrown by convert_to_class all propagate to the caller.

- Validation recommendations
  - For robust operation, consider validating mappings at startup (assert each mapped class exposes a callable convert_to_class) or wrap calls in try/except where callers can provide fallbacks for missing entries or import failures.

## Implementation / integration notes
- Keep imports local to get_html_renderable_mapping and get_widget_renderable_mapping to avoid import cycles and defer flavour dependency import-time cost until needed.
- apply_renderable_mapping enforces an exact-match contract; perform any subclass-aware resolution outside this helper if needed.
- The module intentionally separates mapping construction (pure function returning a dict) from the conversion step. Callers can either:
  - Use the small entry points (HTMLReport, WidgetReport) which perform mapping retrieval + single-step conversion, or
  - Call get_*_renderable_mapping() and use apply_renderable_mapping explicitly if they need mapping inspection or different application logic.

---

## Files

- [`flavours.py`](flavours/flavours.md)

