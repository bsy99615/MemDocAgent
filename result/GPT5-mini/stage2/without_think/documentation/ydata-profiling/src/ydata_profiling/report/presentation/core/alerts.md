# `alerts.py`

## `src.ydata_profiling.report.presentation.core.alerts.Alerts` · *class*

## Summary:
Represents a presentation-layer container for one or more profiling Alert objects. It packages alert data together with a Style instance and delegates rendering to subclass implementations.

## Description:
Alerts is a thin presentation wrapper that prepares alert content for rendering pipelines. It accepts either a flat list of Alert objects or a mapping from string keys to lists of Alert objects, together with a Style instance that drives visual presentation choices. The class itself does not produce output: its render() method intentionally raises NotImplementedError so that concrete renderer subclasses (for example, HTML or JSON renderers in the report presentation layer) can implement the desired rendering strategy.

Typical instantiation scenarios:
- A report builder or presentation factory collects Alert objects produced by checks and creates an Alerts container to pass to a renderer.
- A template rendering pipeline receives an Alerts instance as part of a report context and calls the renderer's render method (via a concrete subclass) to produce markup or serialized output.

Motivation and responsibility boundary:
- Encapsulate the pair (alerts data, style) in a standard "item" with metadata accepted by the presentation subsystem.
- Enforce no rendering policy here — leave rendering details to concrete subclasses so that the same Alerts data can be rendered into multiple formats (HTML, JSON, etc.).
- Maintain a consistent item_type ("alerts") and content shape expected by presentation tooling that operates on ItemRenderer instances.

## State:
This class inherits storage and metadata fields from ItemRenderer (and ultimately from its Renderable base). After construction, an Alerts instance exposes the following observable state:

- item_type: str
  - Value: "alerts"
  - Invariant: constant string identifying this renderer's kind.

- content: Dict[str, Any]
  - Structure: {"alerts": <alerts_arg>, "style": <style_arg>}
  - "alerts" value:
    - Type: Union[List[Alert], Dict[str, List[Alert]]]
    - Meaning: either a flat list of Alert objects or a mapping (for grouped alerts) whose values are lists of Alert objects.
    - Constraints: No runtime validation is performed by Alerts; callers must supply Alert instances and/or container shapes expected by downstream renderers.
  - "style" value:
    - Type: Style
    - Meaning: visual/style configuration used by renderers to produce consistent output.

- name: Optional[str]
  - Origin: forwarded from kwargs to ItemRenderer.__init__ (if provided).
  - Meaning: optional human-friendly identifier for the item (not set by default).

- anchor_id: Optional[str]
  - Origin: forwarded from kwargs to ItemRenderer.__init__ (if provided).
  - Meaning: optional stable identifier for linking; if omitted, concrete renderers may compute their own anchors when needed.

- classes: Optional[str]
  - Origin: forwarded from kwargs to ItemRenderer.__init__ (if provided).
  - Meaning: optional CSS classes or style tags the renderer should apply.

Class-level invariants:
- content contains exactly the two keys "alerts" and "style" after __init__ returns.
- item_type equals the literal "alerts".
- No mutation or normalization of the alerts data is performed by Alerts itself; invariants about the structure of "alerts" are the caller's responsibility.

## Lifecycle:
Creation:
- Constructor signature:
    Alerts(alerts: Union[List[Alert], Dict[str, List[Alert]]], style: Style, **kwargs)
- Required arguments:
    - alerts: a list of Alert objects or a dict mapping strings to lists of Alert objects.
    - style: a Style instance.
- Optional keyword arguments (accepted and forwarded to ItemRenderer.__init__):
    - name: Optional[str]
    - anchor_id: Optional[str]
    - classes: Optional[str]
- Example instantiation pattern (described in prose): supply collected Alert objects and a Style instance to create a container for rendering.

Usage:
- Typical usage sequence:
    1. Instantiate Alerts with alerts data and a Style instance.
    2. Pass the Alerts instance to presentation code that expects ItemRenderer-like objects.
    3. A concrete subclass or a separate renderer obtains the Alerts.content and style and produces output by implementing render().
- Sequencing requirements:
    - No specific method-call ordering is required by Alerts itself.
    - Before rendering, callers should ensure the "alerts" content contains Alert objects in the structure expected by the chosen renderer.

Destruction:
- No explicit cleanup required. Instances are regular Python objects managed by garbage collection.
- Alerts defines no context-management protocol and does not require close()/dispose() calls.

## Method Map:
graph TD
    A[Alerts.__init__(alerts, style, **kwargs)] --> B[ItemRenderer.__init__(item_type="alerts", content={"alerts": alerts, "style": style}, **kwargs)]
    B --> C[item_type set to "alerts"]
    B --> D[content set to {"alerts": ..., "style": ...}]
    A --> E[__repr__() -> "Alerts"]
    A --> F[render() -> raises NotImplementedError (must be overridden by subclasses)]

## Public methods and behavior:
- __init__(alerts, style, **kwargs)
  - Behavior: calls ItemRenderer.__init__ with item_type "alerts" and content containing the provided alerts and style. Does not mutate or validate the alerts collection.
- __repr__()
  - Behavior: returns the literal string "Alerts". No side effects.
- render() -> Any
  - Behavior: intentionally unimplemented; raises NotImplementedError.
  - Purpose: concrete renderers must override this method to convert content into the desired representation (HTML string, JSON structure, etc.).

## Raises:
- __init__:
  - The constructor makes no explicit validations and therefore raises no class-specific exceptions.
  - Possible runtime errors may come from improper kwargs forwarded to ItemRenderer.__init__ or from incorrect types passed to downstream consumer code (but those are not raised by this class directly).
- render():
  - Always raises NotImplementedError to indicate the abstract rendering contract; subclasses must provide an implementation.

## Example (prose):
1. Preparing an Alerts container:
   - Collect Alert objects into either a list or a mapping grouped by some key (e.g., column name or severity).
   - Obtain or construct a Style instance describing presentation choices.
   - Call the Alerts constructor with these two items and optionally supply a name, anchor_id, or classes via kwargs.
2. Rendering:
   - Do not call Alerts.render() on the base Alerts class; it raises NotImplementedError.
   - To render alerts into concrete output, implement a subclass (or a separate renderer) that overrides render() and reads self.content["alerts"] and self.content["style"] to produce the desired output (for example, an HTML fragment or a JSON-serializable dict).
3. Inspection:
   - The string representation of the instance is simply "Alerts" (via __repr__).
   - The prepared data is available as self.content["alerts"] and self.content["style"] for downstream consumers.

### `src.ydata_profiling.report.presentation.core.alerts.Alerts.__init__` · *method*

## Summary:
Initializes an Alerts presentation item by storing the provided alerts collection and Style into the renderer's content and setting the item_type to "alerts". This configures the object's observable state for downstream rendering without performing validation or rendering.

## Description:
- Known callers and context:
    - Report builders or presentation factories that gather Alert objects produced by profiling checks and package them for rendering.
    - Template or rendering pipelines that accept ItemRenderer-like objects as part of a report context prior to calling a concrete renderer implementation.
    - Lifecycle stage: called at creation time when assembling a presentation-model for alerts; the resulting Alerts instance is later consumed by concrete renderers (HTML, JSON, etc.) that implement render().
- Reason for being a separate method:
    - Encapsulates the standard content shape and item type used by the presentation subsystem so callers do not need to replicate the exact keys or literals ("alerts", "style", "alerts" item_type).
    - Keeps construction simple and consistent across different presentation items and allows concrete rendering behavior to remain separated from content packaging.

## Args:
    alerts (Union[List[Alert], Dict[str, List[Alert]]]):
        - Description: The alerts data to present. Either a flat list of Alert objects or a mapping from string keys to lists of Alert objects (e.g., grouped by column name or severity).
        - Required: yes
        - Constraints/allowed values: callers should supply Alert instances or a mapping whose values are lists of Alert instances. No runtime type checking is performed here.
    style (Style):
        - Description: A Style instance describing visual/presentation settings to be used by renderers.
        - Required: yes
    **kwargs:
        - Forwarded optional keyword arguments accepted by ItemRenderer:
            - name (Optional[str]): optional human-friendly identifier for the item.
            - anchor_id (Optional[str]): optional anchor identifier for linking.
            - classes (Optional[str]): optional CSS classes or style tags.
        - Any other kwargs not expected by ItemRenderer may raise an error from the superclass constructor.

## Returns:
    None
    - The constructor initializes instance state and returns None implicitly. No meaningful return value.

## Raises:
    - Any exception raised by ItemRenderer.__init__ or its superclasses if invalid kwargs or other internal errors occur (e.g., unexpected keyword arguments). Alerts.__init__ itself performs no validation and raises no class-specific exceptions.
    - Typical possible runtime errors:
        - TypeError: if unexpected keyword arguments are passed and ItemRenderer or its parents do not accept them.
        - Any exceptions propagated from parent constructors.

## State Changes:
- Attributes READ:
    - None on self (the method does not inspect any existing self attributes).
- Attributes WRITTEN:
    - self.content
        - Set to a dict with exactly two keys after construction: {"alerts": <alerts arg>, "style": <style arg>}.
        - The stored values are the same objects passed in (no copying or normalization).
    - self.item_type
        - Set to the literal string "alerts".
    - self.name, self.anchor_id, self.classes
        - May be set if corresponding kwargs were provided (forwarded to the ItemRenderer / Renderable constructor); otherwise remain as whatever the parent initializer sets (commonly None).

## Constraints:
- Preconditions:
    - The caller should supply a valid alerts container (list of Alert or dict of lists of Alert) and a Style instance. The constructor does not verify types or contents.
    - If supplying kwargs, they should match the parameters accepted by ItemRenderer (name, anchor_id, classes) to avoid superclass errors.
- Postconditions:
    - After return:
        - self.item_type == "alerts"
        - self.content is a dict equal to {"alerts": alerts, "style": style} (where alerts and style are the exact objects passed).
        - Optional metadata attributes (name, anchor_id, classes) will reflect forwarded kwargs if provided.
        - No mutation or normalization of the provided alerts structure has been performed.

## Side Effects:
    - Mutates the instance by setting attributes described above; no I/O or external service calls.
    - No validation or deep-copying of inputs; downstream consumers receive the original objects.
    - Any exception raised will originate from the superclass constructors (propagated), not from this method's own logic.

### `src.ydata_profiling.report.presentation.core.alerts.Alerts.__repr__` · *method*

## Summary:
Return a stable, concise string label identifying this object for debugging, logging, or interactive inspection. This call does not modify the object's state.

## Description:
This method provides the canonical textual representation for an Alerts renderer instance. It is typically invoked by Python builtins and tooling when an object's representation is requested (for example, via the built-in repr() function, interactive interpreter inspection, or when objects are included in debug logs and test failure messages). There are no internal callers within this module that perform additional logic — the method exists to provide a predictable, human-readable identifier for the object rather than computing or displaying its rendered content.

Why this is a separate method:
- Separating this tiny, deterministic representation into __repr__ keeps debugging and logging behavior explicit and consistent across renderer types (so developers can quickly identify object types without invoking render()).
- It avoids inlining ad-hoc string building at callsites and keeps introspection behavior centralized on the object itself.

## Args:
None.

## Returns:
str
- Always returns the literal string "Alerts".
- There are no alternate return values or conditional branches — the return is deterministic and independent of the object's internal state.

## Raises:
None. This method performs no operations that could raise exceptions.

## State Changes:
Attributes READ:
- None. The implementation does not access any self.<attr> fields.

Attributes WRITTEN:
- None. The method does not modify self or any external object.

## Constraints:
Preconditions:
- Caller must supply a valid Alerts instance as self (standard Python method invocation). No other preconditions are required because the method does not read instance state.

Postconditions:
- The object's state is unchanged.
- The caller receives the string "Alerts".

## Side Effects:
- None. There is no I/O, no external service interaction, and no mutation of objects outside self.

### `src.ydata_profiling.report.presentation.core.alerts.Alerts.render` · *method*

## Summary:
Defines the rendering entrypoint for the Alerts item: it is expected to produce a presentation-ready representation of the alerts stored on this object. In the current source the method is intentionally unimplemented and raises NotImplementedError.

## Description:
- Known callers / invocation context:
    - This method is intended to be invoked by the report presentation pipeline when assembling the "alerts" section of a report. Typical call sites are higher-level presentation/renderer orchestration code that iterates over ItemRenderer instances and requests each to produce its rendered output before templating/serializing the final report.
    - There are no callers in this class file; the method exists to be implemented by the concrete presentation backend (HTML renderer, JSON exporter, etc.) or by a subclass.
- Why this is a separate method:
    - Rendering concerns are intentionally separated from data storage and detection logic. Alerts stores the alert data and small presentation helpers (via Alert instances); render() centralizes the transformation of that data into the presentation-specific structure (HTML fragments, dicts for JSON, or richer renderable objects) so different output formats can implement rendering consistently without duplicating traversal/formatting logic.

## Args:
- None.

## Returns:
- Type: Any
    - Current behavior: The method does not return; it immediately raises NotImplementedError.
    - Intended/Recommended behavior (when implemented): return a presentation-ready value appropriate for the chosen output format, for example:
        - For an HTML renderer: an HTML fragment as str or an object representing an HTML node/tree.
        - For a JSON/export renderer: a serializable structure (e.g., list[dict]) describing alerts with fields such as label, description, anchor_id, and metadata.
    - Edge cases:
        - If there are no alerts (empty list or empty dict), the implemented render should return an empty presentation (e.g., an empty list, empty string, or a neutral "no alerts" fragment) — never None unless the broader pipeline explicitly expects None.

## Raises:
- NotImplementedError:
    - Condition: Always in the current source implementation (the method body is raise NotImplementedError()).
- Potential runtime exceptions that concrete implementations should be aware of (raised by interacting components, not by this stub):
    - TypeError:
        - Trigger: Accessing Alert.anchor_id may raise TypeError if an Alert was created with an unhashable column_name (per Alert behavior).
    - KeyError:
        - Trigger: Calling Alert.fmt() for HIGH_CORRELATION alerts may raise KeyError if alert.values lacks expected keys ("fields" or "corr").
    - These exceptions are not raised by the stub itself but are realistic risks for any implementation that calls Alert helper methods; implementations should handle or document these as appropriate.

## State Changes:
- Attributes READ:
    - self.content (inherited container) — specifically:
        - self.content["alerts"]: the alerts provided to the Alerts instance; type accepted by __init__ is Union[List[Alert], Dict[str, List[Alert]]].
        - self.content["style"]: the Style object passed to __init__, used to influence presentation choices.
    - self.item_type: set during initialization by ItemRenderer, available if the implementation needs it.
- Attributes WRITTEN:
    - None in the current implementation (the stub does not modify object state).
    - Recommended implementations should avoid mutating self.content or other instance state; render() should be pure with respect to the Alerts object (read-only).

## Constraints:
- Preconditions (what must be true before calling render):
    - The Alerts instance must have been constructed via __init__, so self.content contains keys "alerts" and "style".
    - self.content["alerts"] must be either:
        - a list of Alert objects, or
        - a dict mapping group/section names (str) to lists of Alert objects.
    - Alert instances should be valid according to the Alert contract (see Alert docs): if implementations rely on alert.anchor_id or alert.fmt(), those fields/behaviors must be available and the underlying Alert.values should contain any keys required by fmt().
- Postconditions (what implementations should guarantee):
    - Do not mutate the stored alerts list/dict or the Style object.
    - Return a renderable object appropriate for the chosen output format that fully represents the alerts present in self.content["alerts"].
    - If no alerts are present, return an empty/neutral render result rather than raising.

## Side Effects:
- Current stub: none (it raises NotImplementedError).
- Typical implementation side effects (recommended practices):
    - Read-only access to Alert instances and Style; no I/O or external service calls should be performed inside render().
    - Implementations may call Alert.fmt() and access Alert.anchor_id — those calls may in turn compute or allocate small cached values (e.g., anchor_id is lazily cached on the Alert instance).
    - Do not perform file, network, or global state mutations inside render(); keep rendering deterministic and side-effect-free so the pipeline can call it multiple times for different outputs.

## Recommended Implementation (actionable guidance to reimplement):
- Input handling:
    - Extract alerts = self.content["alerts"] and style = self.content["style"].
    - Normalize alerts into a canonical form for rendering:
        - If alerts is a dict: treat keys as sections/groups (e.g., {"column_alerts": [...], "dataset_alerts": [...]}) and iterate per group.
        - If alerts is a list: render as a single unnamed group or as the default alerts group.
- Rendering each Alert:
    - For each Alert instance:
        - label: use alert.alert_type_name or alert.fmt() for a human-friendly label. Use fmt() when richer HTML/annotated text is required.
        - anchor_id: access alert.anchor_id when the presentation needs stable links/IDs.
        - description: use repr(alert) or a short string derived from alert values when a textual description is needed.
    - Safely handle potential exceptions from alert.fmt() and alert.anchor_id:
        - Catch KeyError/TypeError around fmt() / anchor_id access and fall back to safe defaults (simple label or omit anchor) or propagate after augmenting with context.
- Output shape suggestions (choose one per renderer):
    - HTML renderer: return str (HTML) or an HTML node object. Structure alerts into a list/section with anchors and labels.
    - JSON/struct renderer: return list[dict] where dict keys include:
        - "group": Optional[str] (group name when alerts is a dict)
        - "label": str (human label)
        - "description": str
        - "anchor_id": Optional[str]
        - "meta": dict (raw alert.values for downstream use)
- Empty-case behavior:
    - If the normalized alerts container is empty, return an empty list or a minimal fragment indicating "No alerts".
- Performance:
    - Avoid expensive operations per alert; avoid reformatting the same alert multiple times.
    - Do not modify the Alert instances; read-only access keeps rendering repeatable.

## Example (non-executable description):
- A minimal HTML-focused implementation would:
    - Normalize alerts to an iterable of (group_name, alerts_list).
    - For each alert produce a small dict: {"label": alert.fmt(), "anchor_id": alert.anchor_id, "meta": alert.values}
    - Assemble these dicts into a single HTML string or node list and return it.

