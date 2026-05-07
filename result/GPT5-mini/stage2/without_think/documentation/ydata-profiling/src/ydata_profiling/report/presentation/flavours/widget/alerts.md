# `alerts.py`

## `src.ydata_profiling.report.presentation.flavours.widget.alerts.get_row` · *function*

## Summary:
Construct and return an ipywidgets.GridBox configured with a fixed two-column layout (75% / 25%) containing the provided widget children.

## Description:
This helper builds an ipywidgets.GridBox with a layout that sets width to "100%" and grid_template_columns to "75% 25%". It places the supplied list of ipywidgets.Widget instances as the GridBox children and returns the GridBox for insertion into a larger widget-based UI.

Known callers within the provided code snapshot:
- No direct callers were identified in the supplied source fragments. The function is intended for alert/presentation UI code that requires a standardized two-column row layout.

Typical trigger/context:
- Used when composing an alert row or similar UI row where callers want a consistent 75%/25% column split and prefer not to inline layout creation.

Reason for extraction:
- Centralizes the layout policy for two-column alert rows so callers only supply the widgets to show. Keeps presentation code concise and consistent.

## Args:
    items (List[widgets.Widget]):
        - A list of ipywidgets.Widget instances to be used as the children of the returned GridBox.
        - The function does not validate element types; passing non-widget objects may cause runtime errors during rendering.
        - No interdependencies between elements are enforced by this function.

## Returns:
    widgets.GridBox
        - A GridBox instance whose .children are set to the provided items and whose layout is a widgets.Layout with width "100%" and grid_template_columns "75% 25%".
        - The function always returns a GridBox object constructed with the supplied items and the hard-coded layout.
        - The function does not alter, reorder, or wrap the provided items.

## Raises:
    - The function body contains no explicit raises; it will not raise intentionally.
    - Possible runtime errors (not raised by this function directly) include:
        * Type-related errors if elements in items are incompatible with ipywidgets children expectations.
        * Errors originating from widget construction if ipywidgets is misconfigured or unavailable.

## Constraints:
    Preconditions:
        - The caller should provide a sequence compatible with List[widgets.Widget]. The function does not coerce or validate types.
        - A Jupyter-compatible front-end is required for the GridBox to render meaningfully.
    Postconditions:
        - The returned GridBox has layout.width == "100%" and layout.grid_template_columns == "75% 25%".
        - No global state or external services are modified by this function.

## Side Effects:
    - None. This function performs in-memory construction only; it does not perform I/O, network access, or mutate external/global state.

## Control Flow:
flowchart TD
    Start --> CreateLayout["Create widgets.Layout(width='100%', grid_template_columns='75% 25%')"]
    CreateLayout --> CreateGridBox["Create widgets.GridBox(items, layout=layout)"]
    CreateGridBox --> Return["Return GridBox"]

## Examples (usage guidance):
Example 1 — Two widgets (common case):
1. Create two widgets, e.g., left = HTML(value="Alert text") and right = Button(description="Dismiss").
2. Call get_row([left, right]).
3. Insert the returned GridBox into the parent container; the GridBox will have the specified layout and the two widgets as children.

Example 2 — Zero or one widget:
- Calling get_row([]) returns a GridBox with no children and the fixed layout.
- Calling get_row([single_widget]) returns a GridBox whose sole child is the provided widget. How the front-end visually places a single child in the grid is determined by CSS grid rendering in the front-end.

Example 3 — Defensive advice:
- If your code may pass non-widget values, validate items before calling (e.g., ensure isinstance(item, widgets.Widget)) to avoid rendering-time errors.
- For different column proportions, create a separate helper rather than changing this function to preserve consistent alert styling.

## `src.ydata_profiling.report.presentation.flavours.widget.alerts.WidgetAlerts` · *class*

## Summary:
WidgetAlerts is a concrete Alerts renderer that converts Alert objects into a small ipywidgets-based UI row (HTML description + disabled status Button per alert) and returns an ipywidgets.GridBox suitable for insertion into a widget-based report.

## Description:
WidgetAlerts is a presentation-layer renderer intended to be used when generating interactive/prototyping reports inside a Jupyter-like environment. It reads the Alerts.content prepared by the Alerts base class (see Alerts) and builds a sequence of ipywidgets children: for each alert it produces an HTML widget containing the rendered alert template and a disabled Button that shows the alert type as a human-friendly label and conveys a visual style (info/warning/danger/empty). Finally it arranges these children into a two-column GridBox row using a shared get_row helper.

Typical callers / instantiation contexts:
- A report builder or presentation factory that already created an Alerts instance (with a list of Alert objects) and selected the "widget" flavour will instantiate or use WidgetAlerts and call render() to obtain a GridBox to include in a larger widget composition.
- A template/pipeline that wants a widget-based representation of alerts for display in a notebook.

Motivation / responsibility boundary:
- Responsibility: translate alert domain objects into a compact, consistent widget layout that pairs an explanatory HTML chunk with a small status Button.
- Boundary: WidgetAlerts only performs presentation. It expects Alerts to have set content["alerts"] and content["style"] (the latter is unused by this class). It does not validate alert contents beyond accessing attributes required to render (and will therefore surface errors from missing attributes or missing templates).

## State:
Inherited state (from Alerts / ItemRenderer):
- item_type: str
  - Value: "alerts"
  - Invariant: constant identifying the renderer kind.
- content: Dict[str, Any]
  - Expected structure: {"alerts": <alerts_arg>, "style": <style_arg>}
  - Important constraints for WidgetAlerts:
    - "alerts" must be a flat List[Alert]. WidgetAlerts iterates over content["alerts"] and expects each element to be an Alert object (not a mapping key). If callers pass a Dict[str, List[Alert]] (grouped alerts), WidgetAlerts will iterate over the dict's keys (strings) and fail later when trying to access .alert_type (AttributeError).
    - "style" is present per Alerts contract but is not used by WidgetAlerts.
- name, anchor_id, classes: Optional[str]
  - Forwarded from Alerts / ItemRenderer kwargs if provided. Not used by this class but preserved on the instance.

Class invariants:
- content contains "alerts" and "style".
- content["alerts"] should be a List[Alert] for WidgetAlerts to work correctly.
- Each Alert used must expose an attribute .alert_type with a .name string (e.g., Alert.alert_type.name).

## Lifecycle:
Creation:
- WidgetAlerts does not define a custom __init__; it inherits Alerts.__init__.
- Constructor signature (inherited): Alerts(alerts: Union[List[Alert], Dict[str, List[Alert]]], style: Style, **kwargs)
  - Required:
    - alerts: preferably a List[Alert] for WidgetAlerts usage.
    - style: Style instance (not used directly here).
  - Optional kwargs forwarded: name, anchor_id, classes.

Usage:
- Typical sequence:
  1. Instantiate Alerts (or a WidgetAlerts factory) with a flat list of Alert objects and a Style instance.
  2. Call WidgetAlerts.render() to obtain an ipywidgets.GridBox.
  3. Insert the returned GridBox into a parent widget layout or display it directly in a notebook.
- Method ordering:
  - No other methods are required. render() is the sole public method added by WidgetAlerts.
  - No special teardown required.

Destruction:
- No explicit cleanup or context-manager support. Normal garbage collection applies. The returned GridBox and its children are standard ipywidgets objects managed by the front-end.

## Method Map:
flowchart TD
    A[WidgetAlerts.render()] --> B[Read self.content["alerts"] (expected List[Alert])]
    B --> C[For each alert do:]
    C --> D[Compute type_name = alert.alert_type.name.lower()]
    D --> E{type_name == "rejected"?}
    E -- yes --> F[skip alert]
    E -- no --> G[Render templates.template("alerts/alert_{type_name}.html").render(alert=alert) -> html_str]
    G --> H[Create HTML widget from html_str and append to items]
    H --> I[Create Button(description=type_name.replace("_"," ").capitalize(), button_style=styles[type_name], disabled=True) and append to items]
    I --> J[After loop: return get_row(items) -> widgets.GridBox]

## Behavior (render):
- Input (via instance state):
  - Reads self.content["alerts"], which must be an iterable of Alert objects.
- Processing:
  - Maintains a hard-coded styles mapping from alert type string to ipywidgets Button.style values:
    - mapping keys include: "constant", "unsupported", "type_date", "high_cardinality", "unique", "uniform", "infinite", "zeros", "truncated", "missing", "skewed", "imbalance", "high_correlation", "duplicates", "empty", "non_stationary", "seasonal"
    - values: one of "warning", "danger", "info", or "" (empty string for default/no-style).
  - For each alert:
    - type_name = alert.alert_type.name.lower()
    - If type_name == "rejected": continue (the alert is skipped and not rendered).
    - Load a template at path "alerts/alert_{type_name}.html" via templates.template(...).
      - Call .render(alert=alert) to obtain an HTML fragment string.
      - Wrap this string in an ipywidgets.HTML widget and append to items.
    - Create a Button widget with:
      - description: a humanized label derived from the type name (underscores replaced with spaces, then capitalized).
      - button_style: styles[type_name] (must exist in the styles mapping).
      - disabled: True
      Append the Button to items.
  - After processing all alerts, call get_row(items) to produce and return a widgets.GridBox that places the generated widgets into a standard two-column row layout.
- Output:
  - Returns an ipywidgets.GridBox (widgets.GridBox) whose children are the sequence of HTML and Button widgets produced.
  - The exact layout is provided by the get_row helper (a fixed two-column 75%/25% split per module contract).

## Inputs / Outputs (types):
- Reads: self.content["alerts"] : List[Alert] (Alert must provide .alert_type.name attribute)
- Uses: templates.template(template_path).render(alert=alert) -> str (HTML string)
- Produces: widgets.GridBox (ipywidgets.GridBox)

## Edge cases and constraints:
- Alerts collection shape:
  - If content["alerts"] is a mapping (Dict[str, List[Alert]]), the iteration will yield keys (str) not Alert objects and attribute access will fail; therefore callers must supply a flat list for WidgetAlerts.
- Missing or unexpected alert_type:
  - If an Alert instance lacks .alert_type or .alert_type.name, AttributeError will be raised.
- Unknown type_name:
  - If an alert type name is not present in the local styles mapping, a KeyError will be raised when accessing styles[type_name].
- Template errors:
  - If templates.template(...) cannot find or load the requested template, the underlying template engine will raise (e.g., TemplateNotFound or other template-related exceptions). These propagate out of render().
  - If templates.template(...).render(...) raises during rendering (e.g., template references missing attributes), that exception will propagate.
- UI constraints:
  - The created Button uses disabled=True and a button_style value that must be valid for ipywidgets Button (valid values typically include "", "primary", "success", "info", "warning", "danger").
  - The get_row helper enforces a two-column layout (75%/25%). The layout semantics are provided by get_row and the front-end CSS grid; WidgetAlerts relies on that helper to wrap the created children correctly.
- Empty alerts:
  - If there are no alerts (empty list) the returned GridBox has no children; this is allowed and will render as an empty row in the front-end.

## Raises:
- Direct raises by WidgetAlerts.render():
  - KeyError: if an encountered type_name is not in the internal styles dict (styles[type_name]).
  - AttributeError: if an alert does not expose alert.alert_type.name.
  - Template engine exceptions (e.g., TemplateNotFound, TemplateSyntaxError, or runtime errors raised by templates.template(...).render()).
  - Any exceptions from get_row (e.g., layout construction), though the widget-specific get_row used here typically returns a GridBox and does not raise for normal item lists.
- No exceptions are raised by __init__ in WidgetAlerts itself (it inherits Alerts.__init__, which does not validate input types).

## Implementation notes (sufficient to reimplement):
- styles mapping: use the same keys and values as in the source to choose button styles.
- For each Alert in content["alerts"]:
  - Compute type_name = alert.alert_type.name.lower()
  - Skip type_name == "rejected"
  - Build template path = f"alerts/alert_{type_name}.html"
  - Call templates.template(template_path).render(alert=alert) to obtain markup.
  - Create an ipywidgets.HTML with that markup.
  - Create an ipywidgets.Button with:
    - description = type_name.replace("_", " ").capitalize()
    - button_style = styles[type_name]
    - disabled = True
  - Append the HTML widget and the Button to a flat list.
- After iterating, call get_row(items) (the 75%/25% GridBox helper) and return the resulting widgets.GridBox.

## Example:
Assume you have a list of Alert objects ready and a Style instance (style):
1. Construct the Alerts container (inherited creation):
   - alerts = collected_alerts_list
   - widget_alerts = WidgetAlerts(alerts=alerts, style=style)
2. Render into a GridBox:
   - grid = widget_alerts.render()
3. Display in a notebook:
   - display(grid)  # or insert into a parent ipywidgets container

Notes:
- Ensure alerts is a flat list of Alert objects where each Alert.alert_type.name is a string matching one of the expected type names (or be prepared to handle KeyError/AttributeError).
- Ensure the templates exist at the expected paths (alerts/alert_{type_name}.html) to avoid template loading/rendering errors.

### `src.ydata_profiling.report.presentation.flavours.widget.alerts.WidgetAlerts.render` · *method*

## Summary:
Render the alerts stored in the object's content into an ipywidgets.GridBox suitable for notebook display, leaving the object state unchanged.

## Description:
This method builds a sequence of presentation widgets for each alert in self.content["alerts"] (except alerts of type "rejected") and arranges them into a GridBox row layout by delegating to get_row.

Known callers and typical context:
- Invoked when a widget-based (ipywidgets) profile/report UI is being assembled and the Alerts block needs to be rendered as interactive widgets for display in a Jupyter notebook or similar front-end.
- Typically called by higher-level UI composition code that instantiates WidgetAlerts (a subclass of Alerts) and requests its widget representation during the report generation/rendering pipeline.

Why this is a separate method:
- Rendering alerts into ipywidgets involves multiple steps (template rendering, widget creation, layout composition) and is specific to the "widget" presentation flavour. Keeping it as a dedicated method isolates presentation logic from data/model logic and allows other presentation flavours (HTML, notebook, etc.) to implement their own renderers.

## Args:
    None

## Returns:
    widgets.GridBox
        - A GridBox instance produced by get_row(items), containing the rendered alert widgets and a layout chosen by get_row based on the number of children.
        - Typical contents: for each alert included, there are two children appended (an HTML-like rendered alert body and a Button widget used as a labeled style badge). Therefore the GridBox will usually contain 2 * N children for N non-rejected alerts.
        - Edge-case returns: If there are zero alerts (or all alerts are filtered out as "rejected"), this method will call get_row([]) and — given get_row's implementation in this codebase — will result in a ValueError (see Raises).

## Raises:
    KeyError
        - If an alert type name (alert.alert_type.name.lower()) is not present in the local styles mapping, accessing styles[type_name] will raise a KeyError.
    ValueError
        - If the number of items produced is not supported by get_row (get_row supports exactly 1, 2, 3 or 4 children per its implementation), get_row will raise ValueError("Layout undefined for this number of columns"). Common triggers:
            * Zero alerts (items == []) -> ValueError
            * More than two alerts (items length > 4 because each alert appends two items) -> ValueError
    Any exception raised by the template system
        - templates.template(...).render(alert=alert) may raise errors if the requested template is missing, invalid, or if rendering fails. Exact exceptions depend on the template engine used by templates.template.
    Any exception raised by ipywidgets constructors
        - Constructing HTML(...) or Button(...) may raise exceptions in pathological environments (e.g., if ipywidgets is unavailable or misconfigured). These are not raised intentionally by this method but may surface at runtime.

## State Changes:
    Attributes READ:
        - self.content (expects a mapping-like object)
        - self.content["alerts"] (iterable of alert objects)
        - For each alert: alert.alert_type.name (string) and the alert object is passed into the template renderer.
    Attributes WRITTEN:
        - None. The method does not mutate self or its attributes.

## Constraints:
    Preconditions:
        - self.content must be a mapping that contains the key "alerts".
        - Each element in self.content["alerts"] must be an object with at least an attribute alert_type whose name attribute is a string (accessible as alert.alert_type.name).
        - The templates subsystem must include templates named following the pattern "alerts/alert_{type_name}.html" (where type_name == alert.alert_type.name.lower()) or the template loader/rendering will fail.
        - The styles mapping defined in the method must contain entries for all type_name values emitted by alerts (except "rejected", which is explicitly skipped).
        - The get_row helper must accept the number of items produced; given this implementation, valid counts are 1..4 inclusive.
    Postconditions:
        - If no exception is raised, the method returns a widgets.GridBox whose children represent the rendered alert bodies and corresponding status buttons for the alerts present at call time, and self is unchanged.

## Side Effects:
    - In-memory creation of ipywidgets.Widget instances (HTML and Button) for each included alert.
    - Template rendering: calling templates.template(...).render(alert=alert) may cause I/O (reading template files from package resources) or CPU work within the template engine.
    - No network I/O is performed by this method itself, but template rendering or widget construction can indirectly trigger other side effects depending on their implementations.

## Implementation notes / behavior details:
    - The method maintains an internal styles dict mapping alert type names (lowercase) to ipywidgets button_style values (e.g., "warning", "danger", "info", or empty string).
    - For each alert:
        * The alert type name is computed as alert.alert_type.name.lower().
        * Alerts with type_name == "rejected" are skipped and not rendered.
        * The alert body widget is created by rendering a template named "alerts/alert_{type_name}.html" with the alert provided in the template context; the resulting content is passed to HTML(...).
        * A Button widget is created with description set to type_name.replace("_", " ").capitalize(), button_style set to styles[type_name], and disabled=True.
        * Both the body widget and the button are appended to items in that order.
    - Because each alert contributes two items, the method can produce 2, 4, 6, ... items — but get_row only accepts 1..4. Rendering more than two non-rejected alerts will therefore raise a ValueError from get_row.
    - This method is read-only with respect to the WidgetAlerts instance; it constructs and returns a new widget container.

## Example usage:
- Typical call site:
    1. widget_alerts = WidgetAlerts(content=some_content_dict)
    2. grid = widget_alerts.render()
    3. Insert grid into a parent ipywidgets layout or display(grid) in a notebook

