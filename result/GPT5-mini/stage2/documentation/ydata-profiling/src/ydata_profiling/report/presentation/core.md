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
└── variable_info.py

## Role:
Provide the presentation-layer building blocks (typed renderable items, structural containers and small UI primitives) used to model report content before format-specific rendering (HTML/JSON/widget). This module centralizes the content shapes, item_type identifiers and conversion hooks that the presentation/rendering pipeline expects.

## Description:
- Where/when used:
  - Used by report builders, presentation factories and rendering orchestration code that assemble profiling reports into a renderable tree.
  - Consumers include higher-level report composition code (ProfileReport builders) and concrete renderers / exporters that serialize or convert these items into HTML, JSON or other outputs.
- Why these components are grouped:
  - Cohesion: all classes build or describe the presentation model (items, containers, UI primitives).
  - Layer boundary: these classes form the model layer of the presentation subsystem — they package data + metadata and expose a single render() extension point so format-specific renderers remain orthogonal.

## Components:
List of public classes (module export surface). For implementation details, see the corresponding component-level documentation.

- renderable.Renderable(content: Dict[str, Any], name: Optional[str]=None, anchor_id: Optional[str]=None, classes: Optional[str]=None)
  - One-line role: Minimal abstract base for anything that can be rendered; stores a content dict plus optional metadata.

- item_renderer.ItemRenderer(item_type: str, content: Dict[str, Any], name: Optional[str]=None, anchor_id: Optional[str]=None, classes: Optional[str]=None)
  - One-line role: Adds a semantic item_type to a Renderable and forwards metadata handling.

- container.Container(items: Sequence[Renderable], sequence_type: str, nested: bool=False, **kwargs)
  - One-line role: Sequence-like wrapper for ordered child renderables, recording a sequence_type and nested flag.

- collapse.Collapse(button: 'ToggleButton', item: Renderable, **kwargs)
  - One-line role: Structural two-part container representing a collapsible region (button + collapsible item).

- dropdown.Dropdown(name: str, id: str, items: list, item: Container, anchor_id: str, classes: list, is_row: bool, **kwargs)
  - One-line role: Encodes a dropdown UI: metadata, selectable items list and a per-item Container template.

- toggle_button.ToggleButton(text: str, **kwargs)
  - One-line role: Small wrapper for a labeled toggle control (payload stored under content["text"]).

- container.Container.convert_to_class / collapse.Collapse.convert_to_class / dropdown.Dropdown.convert_to_class / root.Root.convert_to_class / variable.Variable.convert_to_class
  - One-line role: Class-specific deserialization hooks that mutate obj.__class__ and recursively convert nested children via a provided flv callable.

- alerts.Alerts(alerts: Union[List['Alert'], Dict[str, List['Alert']]], style: 'Style', **kwargs)
  - One-line role: Packages profiling Alert objects with a Style for presentation.

- correlation_table.CorrelationTable(name: str, correlation_matrix: 'pd.DataFrame', **kwargs)
  - One-line role: Container for a correlation matrix intended for rendering.

- duplicate.Duplicate(name: str, duplicate: 'pd.DataFrame', **kwargs)
  - One-line role: Holds duplicate-row DataFrame for presentation.

- frequency_table.FrequencyTable(rows: list, redact: bool, **kwargs)
  - One-line role: Holds a variable frequency table (rows + redact hint) for renderers.

- frequency_table_small.FrequencyTableSmall(rows: list, redact: bool, **kwargs)
  - One-line role: Compact frequency-table item for concise displays.

- html.HTML(content: str, **kwargs)
  - One-line role: Carry a raw HTML string as a renderable item (item_type "html").

- image.Image(image: str, image_format: 'ImageType', alt: str, caption: Optional[str]=None, **kwargs)
  - One-line role: Encapsulate image payload/metadata for presentation (format, alt, caption).

- root.Root(name: str, body: Renderable, footer: Renderable, style: 'Style', **kwargs)
  - One-line role: Top-level report item packaging body, footer and Style for final rendering.

- sample.Sample(name: str, sample: 'pd.DataFrame', caption: Optional[str]=None, **kwargs)
  - One-line role: Package a small DataFrame sample and caption for renderers.

- table.Table(rows: Sequence, style: 'Style', name: Optional[str]=None, caption: Optional[str]=None, **kwargs)
  - One-line role: Typed holder for table rows, style and optional metadata used by table renderers.

- variable.Variable(top: Renderable, bottom: Optional[Renderable]=None, ignore: bool=False, **kwargs)
  - One-line role: Group two nested renderables (top and bottom) under the "variable" semantic type.

- variable_info.VariableInfo(anchor_id: str, var_name: str, var_type: str, alerts: list, description: str, style: 'Style', **kwargs)
  - One-line role: Metadata payload for one variable (name/type/alerts/desc/style) for presentation.

Mermaid dependency (high-level) graph showing inheritance and composition relationships among internal components:

graph TD
    Renderable --> ItemRenderer
    ItemRenderer --> Alerts
    ItemRenderer --> Collapse
    ItemRenderer --> Container
    ItemRenderer --> CorrelationTable
    ItemRenderer --> Dropdown
    ItemRenderer --> Duplicate
    ItemRenderer --> FrequencyTable
    ItemRenderer --> FrequencyTableSmall
    ItemRenderer --> HTML
    ItemRenderer --> Image
    ItemRenderer --> Root
    ItemRenderer --> Sample
    ItemRenderer --> Table
    ItemRenderer --> ToggleButton
    ItemRenderer --> Variable
    ItemRenderer --> VariableInfo

    Container -->|contains sequence of| Renderable
    Collapse -->|content.button| ToggleButton
    Collapse -->|content.item| Renderable
    Dropdown -->|content.item| Container
    Dropdown -->|content.items| Renderable
    Root -->|content.body/footer| Renderable
    Variable -->|content.top/bottom| Renderable

    style Renderable fill:#f0f8ff,stroke:#333,stroke-width:1px
    style ItemRenderer fill:#fef6e4,stroke:#333,stroke-width:1px
    style Container fill:#e6f9e6,stroke:#333,stroke-width:1px

## Public API:
The module exposes a set of typed renderable classes (all subclasses of Renderable/ItemRenderer). Below are the primary public symbols, their signatures and usage notes.

- Renderable(content: Dict[str, Any], name: Optional[str]=None, anchor_id: Optional[str]=None, classes: Optional[str]=None)
  - Description: Base contract; stores content dict and optional metadata. Use when implementing new renderable types; implement render() in subclasses.

- ItemRenderer(item_type: str, content: Dict[str, Any], name: Optional[str]=None, anchor_id: Optional[str]=None, classes: Optional[str]=None)
  - Description: Adds an item_type tag. Concrete item classes call super().__init__ with item_type and a content dict.

- Container(items: Sequence[Renderable], sequence_type: str, nested: bool=False, **kwargs)
  - Description: Use to group ordered children; subclasses must override render().

- Collapse(button: ToggleButton, item: Renderable, **kwargs)
  - Description: Structural representation of a collapsible widget; render() must be provided by concrete renderer.

- Dropdown(name: str, id: str, items: list, item: Container, anchor_id: str, classes: list, is_row: bool, **kwargs)
  - Description: Represents a dropdown control with a per-item template; convert_to_class will convert the 'item' container during deserialization.

- ToggleButton(text: str, **kwargs)
  - Description: Small payload for a toggle control; implement render() in a renderer or subclass.

- Alerts(alerts: Union[List['Alert'], Dict[str,List['Alert']]], style: 'Style', **kwargs)
  - Description: Container for Alert objects + Style; base render() raises NotImplementedError (renderers will implement HTML/JSON formatting).

- CorrelationTable(name: str, correlation_matrix: 'pd.DataFrame', **kwargs)
  - Description: Holds a DataFrame correlation matrix; renderer chooses output format (HTML table, JSON, heatmap spec).

- Duplicate(name: str, duplicate: 'pd.DataFrame', **kwargs)
  - Description: Holds duplicate rows DataFrame for a variable.

- FrequencyTable(rows: list, redact: bool, **kwargs)
  - Description: Full frequency table (rows + redact flag).

- FrequencyTableSmall(rows: list, redact: bool, **kwargs)
  - Description: Compact form of frequency table.

- HTML(content: str, **kwargs)
  - Description: Carries raw HTML string; a renderer may return that string verbatim.

- Image(image: str, image_format: 'ImageType', alt: str, caption: Optional[str]=None, **kwargs)
  - Description: Contains image payload and metadata. Constructor validates image is not None.

- Root(name: str, body: Renderable, footer: Renderable, style: 'Style', **kwargs)
  - Description: Top-level report container. Concrete Root subclasses implement render() to compose body/footer/style into final output.

- Sample(name: str, sample: 'pd.DataFrame', caption: Optional[str]=None, **kwargs)
  - Description: Small DataFrame preview container.

- Table(rows: Sequence, style: 'Style', name: Optional[str]=None, caption: Optional[str]=None, **kwargs)
  - Description: Generic table payload; render() is backend specific.

- Variable(top: Renderable, bottom: Optional[Renderable]=None, ignore: bool=False, **kwargs)
  - Description: Logical two-part item; render() must handle ignore and nested rendering.

- VariableInfo(anchor_id: str, var_name: str, var_type: str, alerts: list, description: str, style: 'Style', **kwargs)
  - Description: Variable metadata payload for variable detail blocks.

Usage notes:
- All classes place their primary data into content dict keys (the exact keys are documented in each component). Callers and renderers access these via instance.content or via the documented property accessors.
- None of these base classes implement rendering (most render() methods raise NotImplementedError). Concrete backends must implement rendering for the target format.
- For deserialization, use the class.convert_to_class(obj, flv) hooks (available on many classes) to mutate runtime class and recursively convert nested children.

## Dependencies:
Internal (other repo modules)
- ydata_profiling.config.Style / ImageType
  - Purpose: shared style/config types used by many items (Image, Root, Table, Alerts, VariableInfo, etc.).
- profile/report building code (higher-level code) — consumers that build instances of these classes.
- domain objects used by content:
  - Alert (alert objects referenced by Alerts and VariableInfo)
  - pandas DataFrame (used by CorrelationTable, Duplicate, Sample)

External (third-party)
- pandas (pd.DataFrame): many items store DataFrame payloads (CorrelationTable, Duplicate, Sample).
- typing (Union, Dict, List, Optional, Sequence, Any): used in annotations across component APIs.
- htmlmin or templating libraries may be used by concrete renderers elsewhere (not in these data-holder classes) — the module itself carries no mandatory runtime dependency on htmlmin, but consumers commonly use template engines.
- image format enumeration (ImageType) uses the repo config; renderers may depend on base64, image libs, or I/O if they implement image handling.

## Constraints:
- Content is shared by reference: constructors store the exact dict/objects passed; callers must not rely on defensive copies. Mutating objects placed into content (e.g., DataFrame, lists) will be visible to the instance.
- Renderers must implement render():
  - The base classes intentionally raise NotImplementedError for render(). Before calling render() ensure you have a concrete subclass or renderer implementation available.
- convert_to_class mutates obj.__class__:
  - The convert_to_class classmethod (present on many types) assigns obj.__class__ = cls and calls flv on nested entries. This in-place mutation requires that cls is assignment-compatible with obj; Python may raise TypeError for incompatible assignments.
  - convert_to_class depends on the provided flv callable to convert nested children; choose or implement flv carefully (it is responsible for recursive conversion).
- Metadata properties are stored in content keys:
  - Properties name/anchor_id/classes expect corresponding keys to exist in content (accessing them when missing raises KeyError). Callers should either pass these metadata values in the constructors or read content.get(...) directly.
- Thread-safety and reentrancy:
  - Instances are simple Python objects with mutable content; they are not thread-safe for concurrent mutation. Rendering can be called concurrently only if callers ensure the content and nested objects are not mutated concurrently.
- Ordering:
  - Build the presentation model (construct/convert nested items) before invoking downstream renderers, especially when using convert_to_class to mutate runtime types.
- Validation:
  - These classes perform minimal runtime validation (Image.__init__ checks image is not None; other constructors do not validate types). Renderers should validate required content shapes (e.g., DataFrame presence, expected keys) and raise clear errors if preconditions are violated.

## Links to component docs:
- Alerts: src.ydata_profiling.report.presentation.core.alerts.Alerts
- Collapse: src.ydata_profiling.report.presentation.core.collapse.Collapse
- Container: src.ydata_profiling.report.presentation.core.container.Container
- CorrelationTable: src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable
- Dropdown: src.ydata_profiling.report.presentation.core.dropdown.Dropdown
- Duplicate: src.ydata_profiling.report.presentation.core.duplicate.Duplicate
- FrequencyTable: src.ydata_profiling.report.presentation.core.frequency_table.FrequencyTable
- FrequencyTableSmall: src.ydata_profiling.report.presentation.core.frequency_table_small.FrequencyTableSmall
- HTML: src.ydata_profiling.report.presentation.core.html.HTML
- Image: src.ydata_profiling.report.presentation.core.image.Image
- ItemRenderer: src.ydata_profiling.report.presentation.core.item_renderer.ItemRenderer
- Renderable: src.ydata_profiling.report.presentation.core.renderable.Renderable
- Root: src.ydata_profiling.report.presentation.core.root.Root
- Sample: src.ydata_profiling.report.presentation.core.sample.Sample
- Table: src.ydata_profiling.report.presentation.core.table.Table
- ToggleButton: src.ydata_profiling.report.presentation.core.toggle_button.ToggleButton
- Variable: src.ydata_profiling.report.presentation.core.variable.Variable
- VariableInfo: src.ydata_profiling.report.presentation.core.variable_info.VariableInfo

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

