# `src.ydata_profiling.report`

## Tree:
report/
├── presentation/
│   ├── core/
│   ├── flavours/
│   └── frequency_table_utils.py
├── structure/
└── formatters.py

## Role:
Provide the reporting layer that bridges profiling results and renderable report outputs: define the presentation model and reusable formatting helpers, and host structure definitions that describe the assembled report's logical layout.

## Description:
- Where and when this module is used:
  - Report builders create a logical report representation (structure.*) and a canonical presentation tree (presentation.*) during ProfileReport assembly.
  - Before serializing/exporting, the presentation model is converted to a specific flavour (HTML, widgets) and then passed to renderers/exporters.
  - formatters.py provides small, focused text/HTML formatting utilities used by renderers, templates, and presentation helpers to produce consistent human-facing strings.
- Primary consumers:
  - ProfileReport builders and report composition code
  - Renderers/exporters and flavour converters (presentation.flavours)
  - Templates and HTML/widget flavour implementations
- Why these components are grouped:
  - Cohesion and layer separation: presentation contains canonical renderable types and conversion helpers; formatters centralize presentation-focused string formatting; structure (logical report layout definitions) sits alongside to keep report-shape definitions in the same package.

## Components:
- presentation (package) — see src/ydata_profiling/report/presentation for component-level docs
  - Role: canonical renderable item classes (Renderable, ItemRenderer) and utilities to build and convert presentation trees; contains flavour mappings and frequency-table helpers.
- structure (package) — src/ydata_profiling/report/structure
  - Role: (undocumented in memory) expected to define the logical report/section composition types and builders used by high-level report creation code.
  - Note: detailed component docs for this package were not available in the provided snapshot; consult the file tree at src/ydata_profiling/report/structure for concrete types and add component-level docs.
- formatters.py (module) — public functions (signatures and one-line role)
  - fmt(value: Any) -> str
    - Dispatch: numeric built-in ints/floats to numeric formatter; otherwise return HTML-escaped string.
  - fmt_array(value: Any, threshold: Any = np.nan) -> str
    - Produce a concise string representation of a (NumPy) array using temporary numpy.printoptions.
  - fmt_badge(value: str) -> str
    - Replace occurrences of "(digits)" with an HTML badge span.
  - fmt_bytesize(num: float, suffix: str = "B") -> str
    - Format a byte-like numeric value into a 1024-based human-readable string with one decimal.
  - fmt_class(text: str, cls: str) -> str
    - Wrap text in a span with the provided CSS class (no escaping performed).
  - fmt_color(text: str, color: str) -> str
    - Wrap text in a span with inline color style (no escaping performed).
  - fmt_monotonic(value: int) -> str
    - Map integer monotonicity codes (-2..2) to canonical human-readable labels.
  - fmt_number(value: int) -> str
    - Format integer-like value using Python's "n" (locale-aware) format specifier.
  - fmt_numeric(value: float, precision: int = 10) -> str
    - Format numeric values; convert scientific notation "e±" to " × 10<sup>...</sup>" HTML fragments.
  - fmt_percent(value: float, edge_cases: bool = True) -> str
    - Convert fraction to one-decimal percentage string with optional "< 0.1%" / "> 99.9%" shorthands.
  - fmt_timespan(value: Any, detailed: bool = False, max_units: int = 3) -> str
    - (Component-level doc not present in memory) Intended as the general timespan humanizer; consult source for exact behavior.
  - fmt_timespan_timedelta(delta: Any, detailed: bool = False, max_units: int = 3, precision: int = 10) -> str
    - When given a pandas Timedelta, normalize to seconds (including positive micro/nanoseconds) and delegate to fmt_timespan; otherwise forward to fmt_numeric.
  - help(title: str, url: Optional[str] = None) -> str
    - Return a small HTML help-badge fragment; optionally wrap it in a link when url is provided.
  - list_args(func: Callable) -> Callable
    - Decorator: allow a single-value callable to accept either a scalar or a Python list (apply element-wise when list).

Mermaid dependency graph (internal relationships):
graph TD
  Report[report module]
  Presentation[presentation/]
  Structure[structure/]
  Formatters[formatters.py]
  Flavours[presentation.flavours]
  HTMLImpls[presentation.flavours.html]
  WidgetImpls[presentation.flavours.widget]
  ProfileBuilders[profile builders]
  Renderers[renderers/exporters]
  Config[ydata_profiling.config]

  Report --> Presentation
  Report --> Structure
  Report --> Formatters
  Presentation --> Flavours
  Flavours --> HTMLImpls
  Flavours --> WidgetImpls
  ProfileBuilders --> Structure
  ProfileBuilders --> Presentation
  Renderers --> Flavours
  Renderers --> Presentation
  Presentation --> Config
  Formatters --> Presentation

## Public API:
- src/ydata_profiling/report/presentation (package)
  - Exposes canonical Renderable types (Renderable, ItemRenderer, Container, Collapse, Dropdown, Alerts, CorrelationTable, Duplicate, FrequencyTable, FrequencyTableSmall, HTML, Image, Root, Sample, Table, ToggleButton, Variable, VariableInfo) and conversion utilities (presentation.flavours and frequency_table_utils).
  - Usage note: instantiate canonical classes to build a presentation tree; convert to a flavour (HTMLReport/WidgetReport) before rendering.
  - Link to detailed docs: src/ydata_profiling/report/presentation (component-level docs available for core classes and frequency-table utilities).
- src/ydata_profiling/report/structure (package)
  - Exposes the logical report/section composition types used by ProfileReport builders.
  - Usage note: this package defines the higher-level structure used to assemble presentation trees; consult source files under src/ydata_profiling/report/structure for exact exported symbols (component docs missing in this snapshot).
- src/ydata_profiling/report/formatters.py
  - A set of pure utility functions focused on text and HTML fragment formatting described in the Components section above.
  - Usage notes:
    - fmt and fmt_numeric return strings suitable for embedding in HTML but do not perform escaping in all cases; callers must escape untrusted text where required.
    - list_args decorator only recognizes built-in Python list instances for batch dispatch; other iterables will be forwarded as single arguments.
    - fmt_timespan_timedelta depends on pandas.Timedelta detection and delegates accordingly.

## Dependencies:
- Internal (repository)
  - ydata_profiling.config: provides Style, ImageType, and other configuration types referenced by presentation items (Image, Root, Table, VariableInfo).
  - Profile report builders and reporting entry points: construct structure and presentation trees.
  - Flavour implementations under presentation.flavours.html and presentation.flavours.widget: provide concrete renderable classes returned by mapping functions.
- External (third-party / stdlib)
  - pandas (pd.Series, pd.DataFrame, pd.Timedelta): used by presentation items (tables, correlation, sample) and fmt_timespan_timedelta.
  - numpy (np): used by fmt_array and for numeric-like handling in formatters when adjusting print options.
  - markupsafe (escape): used by fmt to produce HTML-escaped strings for non-built-in numeric types.
  - re: used by fmt_badge.
  - typing (typing hints used across the module).
  - Note: flavour implementations and final renderers may depend on templating libraries or widget frameworks; the canonical presentation types intentionally avoid heavy rendering dependencies.

## Constraints:
- Initialization and import-time behavior:
  - presentation.flavours mapping functions perform local imports of flavour implementations and raise ImportError at call time if those implementations are unavailable. Callers should handle or defer these calls appropriately.
- Conversion semantics:
  - Flavour conversion often mutates objects in-place (convert_to_class may reassign __class__ and recurse). Callers must not assume immutability and should avoid sharing structures concurrently across threads while converting.
- Exact-type mapping:
  - apply_renderable_mapping uses exact type(obj) lookups (not isinstance). Provide mapping entries for the exact canonical types present in the tree when performing conversions.
- Thread-safety:
  - Presentation objects are mutable containers referencing potentially large DataFrame objects. Conversions and rendering are not thread-safe; if concurrent reads/writes may occur, callers must synchronize externally.
- Formatters preconditions:
  - fmt treats only exact built-in float and int as numeric for numeric formatting; numpy scalars, Decimal, and pandas numeric types are not auto-coerced — callers must convert them when numeric formatting is desired.
  - fmt_array requires numpy to be importable; threshold parameter is forwarded to numpy.printoptions edgeitems and may raise if incompatible.
  - fmt_timespan_timedelta requires pandas to be available and uses pd.Timedelta for detection; missing pandas or a mismatched pd symbol will cause runtime errors.
  - Many formatters produce HTML fragments without escaping — callers embedding user-controlled content must escape accordingly.
- Error propagation:
  - Mapping and conversion helpers intentionally do not swallow exceptions (KeyError, AttributeError, TypeError, ImportError, etc). Higher-level callers should catch and handle these where appropriate.
- Ordering:
  - Build the report structure and presentation tree fully before applying flavour conversion and rendering. Conversions traverse and mutate the tree recursively; concurrent mutations will cause undefined behavior.

## Links to component docs:
- Presentation package and component-level docs: src/ydata_profiling/report/presentation/ (core/, flavours/, frequency_table_utils.py)
- Formatters component docs: src/ydata_profiling/report/formatters.py (contains many standalone formatter helpers; component-level docs are available for individual functions in-memory)
- Structure package (needs component-level documentation): src/ydata_profiling/report/structure/ (component docs missing in the provided snapshot; add detailed docs per type for full module-level coverage)

---

## Files

- [`formatters.py`](report/formatters.md)

