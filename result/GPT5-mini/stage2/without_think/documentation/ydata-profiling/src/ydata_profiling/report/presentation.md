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
Provide the presentation-layer model and conversion helpers used to build, convert and prepare report content for format-specific rendering. This module owns the canonical renderable item shapes, flavour mappings, and reusable frequency-table formatting utilities that the reporting pipeline relies on.

## Description:
- Where and when this module is used:
  - During report assembly and before final serialization/rendering: report builders construct a canonical presentation tree (Root and nested Renderable items) from profiling results.
  - Prior to producing a specific output format: presentation.flavours converts canonical items into flavour-specific implementations (HTML or widget) used by concrete renderers/exporters.
  - Frequency-table utilities are called when formatting categorical/discrete variable distributions into the rows expected by presentation templates/renderers.
  - Primary consumers:
    - High-level report composition code (ProfileReport builders)
    - Presentation factories and renderer constructors
    - Concrete renderers/exporters for HTML, widgets, JSON, etc.
- Why these components are grouped:
  - Cohesion: the package centralizes the presentation model (data + metadata shapes) and the thin conversion/formatting helpers that operate on that model.
  - Layer boundary: it forms a presentation-model layer between domain/profile generation and format-specific rendering; core defines the canonical shapes, flavours supplies mappings to concrete flavour types, and utilities prepare recurring presentation data (e.g., frequency tables).

## Components:
- core (package)
  - renderable.Renderable(content: Dict[str, Any], name: Optional[str]=None, anchor_id: Optional[str]=None, classes: Optional[str]=None)
    - Minimal abstract base for anything that can be rendered; stores a content dict plus optional metadata.
  - item_renderer.ItemRenderer(item_type: str, content: Dict[str, Any], name: Optional[str]=None, anchor_id: Optional[str]=None, classes: Optional[str]=None)
    - Adds a semantic item_type tag and forwards metadata handling.
  - container.Container(items: Sequence[Renderable], sequence_type: str, nested: bool=False, **kwargs)
    - Sequence-like wrapper for ordered child renderables.
  - collapse.Collapse(button: ToggleButton, item: Renderable, **kwargs)
    - Two-part container encoding a collapsible region (button + content).
  - dropdown.Dropdown(name: str, id: str, items: list, item: Container, anchor_id: str, classes: list, is_row: bool, **kwargs)
    - Encodes a dropdown UI with selectable items and a per-item container template.
  - alerts.Alerts(alerts: Union[List['Alert'], Dict[str, List['Alert']]], style: 'Style', **kwargs)
    - Packages Alert objects with a Style for presentation.
  - correlation_table.CorrelationTable(name: str, correlation_matrix: 'pd.DataFrame', **kwargs)
    - Container for a correlation matrix intended for rendering.
  - duplicate.Duplicate(name: str, duplicate: 'pd.DataFrame', **kwargs)
    - Holds duplicate-row DataFrame for presentation.
  - frequency_table.FrequencyTable(rows: list, redact: bool, **kwargs)
    - Full frequency-table item (rows + redact hint).
  - frequency_table_small.FrequencyTableSmall(rows: list, redact: bool, **kwargs)
    - Compact representation of a frequency table.
  - html.HTML(content: str, **kwargs)
    - Carry raw HTML string as a renderable item.
  - image.Image(image: str, image_format: 'ImageType', alt: str, caption: Optional[str]=None, **kwargs)
    - Encapsulate image payload and metadata for presentation.
  - root.Root(name: str, body: Renderable, footer: Renderable, style: 'Style', **kwargs)
    - Top-level report item packaging body, footer and Style for final rendering.
  - sample.Sample(name: str, sample: 'pd.DataFrame', caption: Optional[str]=None, **kwargs)
    - Small DataFrame preview container.
  - table.Table(rows: Sequence, style: 'Style', name: Optional[str]=None, caption: Optional[str]=None, **kwargs)
    - Typed holder for table rows and style.
  - toggle_button.ToggleButton(text: str, **kwargs)
    - Small wrapper for a labeled toggle control.
  - variable.Variable(top: Renderable, bottom: Optional[Renderable]=None, ignore: bool=False, **kwargs)
    - Logical two-part item grouping top and bottom renderables.
  - variable_info.VariableInfo(anchor_id: str, var_name: str, var_type: str, alerts: list, description: str, style: 'Style', **kwargs)
    - Metadata payload for a single variable.
  - Common pattern: many classes provide convert_to_class(obj, flv) hooks to enable in-place deserialization/conversion.
- flavours (package)
  - flavours.get_html_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]
    - Build mapping from canonical core types to HTML flavour implementations.
  - flavours.get_widget_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]
    - Build mapping from canonical core types to widget flavour implementations.
  - flavours.apply_renderable_mapping(mapping: Dict[Type[Renderable], Type[Renderable]], structure: Renderable, flavour: Callable) -> None
    - Convert a Renderable instance in-place by exact-type lookup and invoking mapped_class.convert_to_class.
  - flavours.HTMLReport(structure: Root) -> Root
    - Flavour entry point: convert a Root to HTML flavour in-place and return it.
  - flavours.WidgetReport(structure: Root) -> Root
    - Flavour entry point: convert a Root to widget flavour in-place and return it.
- frequency_table_utils.py
  - extreme_obs_table(freqtable: Union[pd.Series, List[pd.Series]], number_to_print: int, n: Union[int, List[int]]) -> List[List[Dict[str, Any]]]
    - Accepts either a single pandas.Series (a mapping label -> frequency count) or parallel lists of Series and denominators; returns presentation-ready rows for the most/least frequent observations. Single-series input yields a single-element outer list; batched/list input yields one inner list per zipped pair.
  - freq_table(freqtable: Union[pd.Series, List[pd.Series]], n: Union[int, List[int]], max_number_to_print: int) -> List[List[Dict[str, Any]]]
    - Produce presentation-ready frequency tables (top categories, optional "Other" and "(Missing)" rows) for single or batched inputs by delegating to the internal _frequency_table helper.
  - (internal helpers)
    - _extreme_obs_table(...) and _frequency_table(...) — implement core numeric/formatting logic (documented in component-level docs).

Mermaid dependency graph (high-level relationships):
graph TD
  Core[ presentation.core (canonical renderables) ]
  Flavours[ presentation.flavours (mapping + entry points) ]
  FreqUtils[ presentation.frequency_table_utils ]
  ProfileBuilders[ profile report builders ]
  Renderers[ concrete renderers/exporters ]
  HTMLImpls[ flavours.html implementations ]
  WidgetImpls[ flavours.widget implementations ]

  ProfileBuilders --> Core
  Core --> FreqUtils
  ProfileBuilders --> Flavours
  Flavours --> HTMLImpls
  Flavours --> WidgetImpls
  Flavours --> Core
  Renderers --> Flavours
  Renderers --> Core

## Public API:
- presentation.core (package)
  - Exposes canonical Renderable types (Renderable, ItemRenderer and all concrete item classes listed above).
  - Usage note: Build a presentation tree by instantiating these classes; renderers convert or consume them. Many classes expose convert_to_class hooks used by flavour conversion.
  - Important: these base classes do not implement rendering themselves — many render() methods raise NotImplementedError. Concrete rendering (HTML, widget, JSON) is supplied by flavour-specific implementations or external renderer modules.
- presentation.flavours (package)
  - get_html_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]
    - Returns a mapping for exact-type conversion to HTML flavour. Keep imports local to avoid import cycles; callers should handle ImportError.
  - get_widget_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]
    - Returns a mapping for exact-type conversion to widget flavour.
  - apply_renderable_mapping(mapping, structure, flavour) -> None
    - Performs exact-type mapping lookup and invokes mapped_class.convert_to_class(structure, flavour). Raises KeyError/AttributeError/TypeError as-is; callers should catch if necessary.
  - HTMLReport(structure: Root) -> Root
    - Convenience entry point for converting a canonical Root to HTML flavour in-place; returns the mutated Root.
  - WidgetReport(structure: Root) -> Root
    - Convenience entry point for converting a canonical Root to widget flavour in-place; returns the mutated Root.
  - Usage note: apply_renderable_mapping performs exact-type lookups only (type(obj)), not isinstance checks.
- presentation.frequency_table_utils (module)
  - extreme_obs_table(freqtable, number_to_print, n) -> List[List[Dict[str, Any]]]
    - Prepare presentation rows for extreme observations; supports single-series (pd.Series mapping label->count) or batched list inputs. Guard denominators (n != 0).
  - freq_table(freqtable, n, max_number_to_print) -> List[List[Dict[str, Any]]]
    - Produce presentation-ready frequency tables (top categories, optional "Other" and "(Missing)" rows) for single or batched inputs.
  - Usage note: Supply either scalar inputs (single pd.Series and int) or parallel lists (list[pd.Series], list[int]). Both functions return an outer list even for single inputs.

## Dependencies:
- Internal (repository)
  - ydata_profiling.config (Style, ImageType, other config types)
    - Purpose: carries style and image-format enumerations used by many presentation items.
  - Profile/report builders (higher-level modules)
    - Purpose: construct canonical presentation trees using core types.
  - Concrete flavour implementation packages:
    - ydata_profiling.report.presentation.flavours.html
    - ydata_profiling.report.presentation.flavours.widget
    - Purpose: provide concrete classes that flavours.get_*_renderable_mapping return as mapping values.
  - Domain types referenced by the content:
    - Alert (used by Alerts and VariableInfo)
    - pandas.DataFrame (used by CorrelationTable, Duplicate, Sample)
- External (third-party / stdlib)
  - pandas (pd.Series, pd.DataFrame)
    - Purpose: frequency tables and tabular payloads within presentation items.
  - typing (Dict, List, Optional, Sequence, Any, Type, Callable)
    - Purpose: API typing and documentation clarity.
  - Note on third-party usage:
    - The canonical core types intentionally do not implement format-specific rendering. Third-party libraries (templating engines, image/base64 helpers, widget frameworks, etc.) are required by flavour implementations or concrete renderers, not by the canonical core data-holder classes themselves. In short: core provides data shapes; flavour modules and final renderers are where external rendering dependencies appear.

## Constraints:
- Conversion semantics and in-place mutation:
  - Flavour conversion commonly mutates instances in-place via mapped_class.convert_to_class which may assign to obj.__class__ and recurse into nested children via a provided flavour callable. This requires that the mapped class is assignment-compatible and that callers are prepared for in-place mutation.
- Exact-type mapping:
  - apply_renderable_mapping uses exact runtime-type lookups (type(obj)). Provide mappings for the exact concrete canonical class types you expect to convert; subclass instances will not match unless their exact type is present in the mapping.
- Initialization / import-time:
  - get_html_renderable_mapping and get_widget_renderable_mapping perform local imports of flavour implementations. Missing flavour modules raise ImportError at call time rather than import time for the presentation package.
- Thread-safety and reentrancy:
  - Presentation items are simple mutable Python objects (content dicts, DataFrame references). Conversions and render operations are not thread-safe if concurrent mutation is possible. Synchronize externally when converting or rendering shared structures concurrently.
- Metadata and content shape expectations:
  - Many classes store data in a content dict with specific keys (name, anchor_id, classes, content payloads). Renderers and conversion hooks expect certain keys to be present; constructors and callers should populate required metadata or use content.get(...) defensively.
- Frequency utilities preconditions:
  - frequency_table_utils assumes pd.Series inputs with numeric counts and denominators n != 0. Passing n == 0 results in ZeroDivisionError; callers must validate denominators.
- Error propagation:
  - apply_renderable_mapping and flavour entry points intentionally do not wrap exceptions. Mapping-key misses (KeyError), missing convert_to_class attributes (AttributeError), incompatible __class__ assignments (TypeError) and ImportError propagate to callers and should be handled at the call site where appropriate.
- Ordering:
  - Build and convert the presentation model fully before invoking format-specific renderers. Conversions may be recursive and order-dependent; do not mutate the tree concurrently while conversion is in progress.

## Links to component docs:
- Core presentation types: src/ydata_profiling/report/presentation/core (see individual component docs for alerts, container, renderable, item_renderer, root, variable, frequency_table, table, image, sample, etc.)
- Flavours mapping & helpers: src/ydata_profiling/report/presentation/flavours/flavours.get_html_renderable_mapping, get_widget_renderable_mapping, apply_renderable_mapping, HTMLReport, WidgetReport
- Frequency-table utilities: src/ydata_profiling/report/presentation/frequency_table_utils.freq_table, extreme_obs_table, _frequency_table, _extreme_obs_table

---

## Files

- [`frequency_table_utils.py`](presentation/frequency_table_utils.md)

