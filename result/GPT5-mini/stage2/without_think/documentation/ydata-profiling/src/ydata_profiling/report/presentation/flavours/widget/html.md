# `html.py`

## `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML` · *class*

## Summary:
WidgetHTML is a concrete HTML renderer for the "widget" presentation flavour that converts the renderer's HTML payload into an ipywidgets-ready object: it wraps plain Python strings in ipywidgets.widgets.HTML and returns non-str payloads unchanged.

## Description:
WidgetHTML specializes the generic HTML item renderer for Jupyter/ipython widget output. It should be used when a piece of HTML content (usually provided as the HTML base-class payload) must be materialized into an object that can be attached to or displayed in a Jupyter notebook.

Typical instantiation: callers do not construct WidgetHTML differently from other HTML renderers — they call the HTML constructor (inherited) with the HTML payload (a string or a prebuilt widget-like object) and any optional metadata. Known callers are report builders, presentation pipelines, and flavour-specific renderers which assemble a presentation tree and then call render() on each item when producing the widget-flavour representation of a report.

Motivation and responsibility:
- Provide a backend-specific implementation of render() that knows how to return an ipywidgets-compatible representation.
- Keep widget-specific conversion logic local so higher-level code can remain flavour-agnostic and simply invoke render().

Boundary:
- WidgetHTML does not perform sanitization or validation of HTML content beyond type discrimination.
- It does not mutate the stored content or manage widget lifecycle beyond constructing/returning objects; actual display and frontend communication are the caller's responsibility.

## State:
Inherited state (from HTML / ItemRenderer) used by WidgetHTML:

- item_type: str
    - Value: always "html" for this class (inherited invariant).
    - Invariant: item_type == "html".

- content: dict
    - Shape: must contain the key "html". Typical shape: {"html": <payload>}.
    - Expected payload types:
        - str: plain Python string containing HTML markup. When the stored value's type is exactly str, WidgetHTML.render will wrap this value in an ipywidgets.widgets.HTML instance and return that.
        - Any non-str object: could be an existing widget instance (e.g., an ipywidgets.widgets.HTML object or another displayable object). WidgetHTML.render will return this object unchanged.
    - Invariant: content is a mapping that provides content["html"]. The HTML base-class constructor is responsible for establishing this invariant; WidgetHTML assumes it holds.

No new attributes are introduced by WidgetHTML itself.

## Lifecycle:
Creation:
- Instantiate via the HTML constructor inherited by WidgetHTML, providing the HTML payload and any optional metadata. Required argument:
    - content (str or prebuilt widget-like object), which will be stored as content["html"].
- No special factories are required — create the instance the same way HTML objects are created, but using the WidgetHTML class to ensure widget-flavour rendering behavior.

Usage:
- Single primary method: render()
    - Purpose: produce a widget-flavour rendering artifact.
    - Typical sequence:
        1. Presentation pipeline assembles item instances (WidgetHTML among them).
        2. When producing the widget-flavour output, the pipeline calls instance.render() for each item.
        3. The returned object is attached to the notebook UI or otherwise handled by the caller.
- Sequencing:
    - No special ordering is required with other methods; render() is safe to call any time after construction so long as content["html"] exists and is accessible.
    - Multiple calls to render() are allowed and will behave identically each time (stateless with respect to the instance).
Destruction:
- No explicit resource cleanup is required by WidgetHTML.
- If render() created a new widgets.HTML instance, the widget object lifecycle (frontend references, kernel comms) is managed by ipywidgets and the Jupyter environment; WidgetHTML does not need to close or deregister resources.

## Method Map:
graph TD
    A[instantiate WidgetHTML (via HTML constructor, content -> content["html"])] --> B[call render()]
    B --> |content["html"] type == str| C[construct widgets.HTML(content["html"]) and return]
    B --> |content["html"] type != str| D[return content["html"] unchanged]

Notes:
- The strict check uses exact type equality (type(payload) != str). Subclasses of str will be treated as non-str and returned unchanged.

## Raises:
The following exceptions can be raised by WidgetHTML.render (propagated to the caller):

- KeyError
    - Trigger: self.content does not contain the key "html". WidgetHTML accesses content["html"] directly; if the HTML base-class invariant was broken or a caller mutated content, a KeyError will be raised.
- Any exception raised by ipywidgets.widgets.HTML(...)
    - Trigger: when payload is a plain str and widgets.HTML(...) fails during construction (for example, if ipywidgets is misconfigured or if widgets.HTML raises due to invalid input). These exceptions are not caught by WidgetHTML and propagate to the caller.

No other exceptions are intentionally raised by WidgetHTML itself.

## Constraints and Edge Cases:
- Strict type test: uses type(self.content["html"]) != str rather than isinstance. Effects:
    - Instances of custom subclasses of str will be considered non-str and thus returned unchanged rather than wrapped.
- None and other non-str values:
    - If content["html"] is None (or any non-str), the value is returned unchanged; callers must handle displayability.
- Empty string:
    - An empty str will be wrapped into widgets.HTML("") and that widget returned.
- Mutability:
    - WidgetHTML.render does not modify self.content or any other instance attributes.

## Example (behavioral scenarios):
- Scenario A (plain string payload):
    - content["html"] is the Python string "<p>Hello</p>".
    - Calling render() constructs and returns an ipywidgets.widgets.HTML object wrapping "<p>Hello</p>".
- Scenario B (prebuilt widget payload):
    - content["html"] is an existing ipywidgets widget instance (for example, an ipywidgets.widgets.HTML already constructed elsewhere).
    - Calling render() returns that same widget instance unchanged (no new object created).
- Scenario C (subclass-of-str payload):
    - content["html"] is an instance of a custom class inheriting from str.
    - Because WidgetHTML checks type(...) exactly, this payload is treated as non-str and returned unchanged (i.e., not wrapped).

Implementation notes to reimplement behavior:
- Inherit from the HTML base class that ensures content["html"] exists and item_type == "html".
- Implement render() to:
    1. Read payload = self.content["html"].
    2. If type(payload) is exactly str, create and return widgets.HTML(payload).
    3. Otherwise, return payload unchanged.
- Do not catch exceptions from widgets.HTML construction; propagate them to the caller.

### `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML.render` · *method*

## Summary:
Return a widget-ready representation of this renderer's HTML payload: if the payload is a plain Python str, wrap it in an ipywidgets.widgets.HTML instance; otherwise return the payload object unchanged. The method does not mutate the renderer.

## Description:
- Known callers and lifecycle stage:
    - Called by the presentation/rendering stage of the report pipeline when an HTML item needs to be materialized for the "widget" flavour (Jupyter/ipython widgets output). Typical callers are flavour-specific renderers, report assemblers, or loops that iterate presentation items and invoke render() to obtain the backend-specific output.
    - This method is invoked after the presentation tree is assembled and just before display or attachment to the notebook UI.

- Why this is a separate method:
    - Different presentation flavours (plain HTML strings, templates, ipywidgets) require different conversion logic from the generic HTML item payload. Encapsulating widget-specific conversion in WidgetHTML.render keeps backend-specific code localized and lets other flavours implement their own render() without branching in higher-level code.
    - It keeps the rendering contract polymorphic: callers call render() on items without needing to know which flavour produced them.

- Important implementation detail:
    - The method performs a strict type check using type(self.content["html"]) != str (not isinstance). As a result, values whose type is a subclass of str will be treated as non-str and returned unchanged rather than being wrapped into widgets.HTML.

## Args:
    None.

## Returns:
    ipywidgets.widgets.HTML or Any
    - If type(self.content["html"]) == str:
        - Returns a newly created ipywidgets.widgets.HTML instance constructed with that string (widgets.HTML(self.content["html"])).
    - If type(self.content["html"]) != str:
        - Returns the object stored in self.content["html"] unchanged (assumed to be a preconstructed widget or other renderable object).
    - Edge cases and notes:
        - If self.content["html"] is an empty string, a widgets.HTML instance wrapping the empty string is returned.
        - If self.content["html"] is None or any other non-str value, that value is returned as-is (which may be None or non-displayable).
        - The method's static type annotation suggests widgets.HTML but, in practice, callers must expect Any because a non-str stored value can be returned.

## Raises:
    - KeyError: if self.content does not contain the key "html" (the method accesses self.content["html"] directly).
    - Any exception raised by ipywidgets.widgets.HTML(...) during construction (e.g., errors thrown by ipywidgets on invalid input) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.content (specifically self.content["html"])
    Attributes WRITTEN:
        - None (the method does not modify self or external objects)

## Constraints:
    Preconditions:
        - self.content must be a mapping containing the key "html" (this is the invariant established by the HTML base class).
        - No further type guarantees are required; the method handles both str and non-str values (with the strict-type-check behavior noted above).

    Postconditions:
        - The renderer instance remains unchanged.
        - The caller receives either a fresh widgets.HTML object (for plain str content) or the original content object (for non-str content).

## Side Effects:
    - Allocates a new ipywidgets.widgets.HTML object when wrapping a str.
    - No file I/O or network calls.
    - Returning a widget object may result in frontend activity later when the widget is displayed in a Jupyter environment (this occurs outside the method but is a consequential effect of returning a widget).

## Example usage (behavioral description):
    - If self.content["html"] == "<p>Hello</p>" (a plain str), the method returns widgets.HTML("<p>Hello</p>").
    - If self.content["html"] == existing_widget (an ipywidgets widget instance), the method returns existing_widget unchanged.
    - If a subclassed string type is stored (e.g., class MyStr(str): ...; content["html"] = MyStr("x")), the method will treat it as non-str and return the MyStr instance unchanged due to the strict type check.

