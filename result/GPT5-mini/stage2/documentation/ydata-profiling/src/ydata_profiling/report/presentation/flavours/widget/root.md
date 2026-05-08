# `root.py`

## `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot` · *class*

## Summary:
WidgetRoot is a concrete Root subclass that renders a report as an ipywidgets VBox. It composes the rendered widgets produced by the report body and footer into a single vertical box suitable for display in Jupyter frontends.

## Description:
WidgetRoot is used when the presentation "flavour" for a report should be a live ipywidgets-based UI. Instantiate WidgetRoot in presentation factories or report builders that target an interactive notebook or other frontends that understand ipywidgets.

Typical callers:
- Flavour-specific presentation factories that construct a Root with body and footer Renderable components and choose the widget flavour.
- Code paths that need to display a report inside a Jupyter notebook (e.g., notebook reporting utilities).

Responsibility and boundary:
- Responsibility: convert the conceptual report structure stored on the inherited content mapping into an ipywidgets.VBox containing the body and footer widget representations.
- Boundary: WidgetRoot does not construct body/footer/style itself — those are supplied by the caller and are expected to follow the Renderable contract (i.e., have a render() method). WidgetRoot also does not manage lifecycle or cleanup for ipywidgets objects beyond assembling and returning the VBox.

## State:
Inherited state (from Root) that WidgetRoot depends on:
- content: dict[str, Any]
  - Required keys (must exist after construction):
    - "body": Renderable — an object exposing render() that returns an ipywidgets-compatible widget
    - "footer": Renderable — same contract as "body"
    - "style": Style — configuration; unused directly by WidgetRoot but part of the Root contract
    - "name": str — present after construction
  - Optional keys (may or may not exist):
    - "anchor_id", "classes" — produced only if passed to the constructor by the caller

WidgetRoot-specific invariants:
- After construction, content remains a mapping and content["body"] and content["footer"] must be valid Renderable objects when render() is called.
- WidgetRoot does not mutate content during render(); it reads body and footer and uses their render() outputs.

Constraints on inputs:
- body.render() and footer.render() are expected to return objects acceptable as children to ipywidgets.VBox (typically instances of ipywidgets.Widget or subclasses).
- If body or footer are missing, or if their render() methods are absent or return invalid objects, runtime exceptions will occur.

## Lifecycle:
Creation:
- WidgetRoot inherits Root.__init__ and is instantiated the same way:
  - Required constructor arguments (forwarded to Root):
    - name: str
    - body: Renderable (object with render())
    - footer: Renderable
    - style: Style
  - Optional kwargs forwarded to parent (e.g., anchor_id, classes)
- No WidgetRoot-specific constructor parameters.

Usage:
1. Construct body and footer Renderable objects whose render() methods return ipywidgets.Widget-compatible objects.
2. Instantiate WidgetRoot via the standard Root constructor (provided name, body, footer, style).
3. Call render(**kwargs) on the WidgetRoot instance to receive an ipywidgets.VBox.
   - Note: WidgetRoot.render accepts **kwargs but currently ignores them.
4. Display the returned VBox in a Jupyter notebook (for example using display()) or otherwise use it in an ipywidgets-compatible UI container.

Destruction / Cleanup:
- WidgetRoot performs no explicit cleanup. It returns a new widgets.VBox instance assembled from the children returned by the nested render() calls. If widget disposal is required, callers must manage widget cleanup (e.g., calling close() on widgets) — WidgetRoot does not implement context-manager behavior or close methods.

## Method Map:
flowchart TD
    RenderCall[WidgetRoot.render(**kwargs)] --> BodyRender[Call content["body"].render()]
    RenderCall --> FooterRender[Call content["footer"].render()]
    BodyRender --> CollectChildren[Collect body_widget, footer_widget]
    FooterRender --> CollectChildren
    CollectChildren --> CreateVBox[widgets.VBox([body_widget, footer_widget])]
    CreateVBox --> ReturnVBox[Return widgets.VBox instance]

Notes:
- render() does not call or modify other methods; it only reads content and invokes nested render() methods on the body and footer.

## Methods (behavioral summary):
- render(self, **kwargs) -> widgets.VBox
  - Behavior:
    - Calls self.content["body"].render() and self.content["footer"].render().
    - Constructs and returns an ipywidgets.VBox whose children are the two returned widget objects, in order [body_widget, footer_widget].
  - Effect of kwargs: ignored by the current implementation (present to match broader render() signature).
  - Return type: ipywidgets.widgets.VBox
  - Side effects: may trigger side effects present in body.footer.render() implementations.

## Raises:
Possible runtime exceptions that callers should be prepared to handle:
- KeyError: if content lacks the "body" or "footer" keys (this is a programming error because Root guarantees these keys immediately after construction).
- AttributeError: if content["body"] or content["footer"] does not have a render() attribute.
- Exception propagated from body.render() or footer.render(): any exception raised during nested rendering will propagate out of WidgetRoot.render.
- TypeError (or ipywidgets-related errors): if the objects returned by body.render() or footer.render() are not valid children for widgets.VBox, the ipywidgets constructor may raise an error.

## Example (typical usage pattern):
1. Ensure body and footer implement the Renderable contract and their render() methods return ipywidgets widgets (for example, widgets.HTML, widgets.VBox, or a custom widget).
2. Instantiate via the inherited constructor:
   - Provide name, body, footer, and style (plus optional anchor_id/classes).
3. Render:
   - Call render() on the WidgetRoot instance to obtain a widgets.VBox containing the rendered body and footer in order.
4. Display and manage lifecycle:
   - Use the returned VBox in the Jupyter display pipeline; if long-lived widgets are created, callers should manage widget cleanup by calling close() when appropriate.

Best practices:
- Construct fresh body/footer Renderable instances to avoid unexpected shared-state in content dictionaries.
- Validate that nested render() returns ipywidgets-compatible objects prior to embedding them if you need precise error handling.
- Use WidgetRoot only when the target environment supports ipywidgets (e.g., Jupyter notebooks). For non-widget outputs, use a different Root subclass (HTML/JSON flavours).

### `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot.render` · *method*

## Summary:
Returns an ipywidgets vertical box container that composes the rendered body and footer widgets, producing the widget-based representation of the report without mutating the WidgetRoot instance.

## Description:
- Known callers and lifecycle:
  - Called by presentation code or report builders that produce a widget-based representation of a report (the "widget" flavour). Typical callers are presentation factories or higher-level rendering routines that choose the widget flavour and invoke render on the concrete Root subclass.
  - Invocation occurs at the rendering stage of the report lifecycle: after the report's body and footer have been assembled into a Root/WidgetRoot instance and a consumer requests a widget UI representation (for example, to display in a Jupyter notebook).
- Rationale for being its own method:
  - This method implements the widget-specific rendering strategy (ipywidgets-based) for a report top-level container. Keeping widget composition logic in WidgetRoot.render separates presentation concerns by flavour (HTML vs widget vs other formats) and avoids inlining widget assembly into generic code paths.

## Args:
- **kwargs: dict
  - Type: arbitrary keyword arguments (mapping of str to Any)
  - Behavior: accepted but not inspected or forwarded by this implementation. Present to keep a uniform render signature across flavours and to allow future options without changing the API.

## Returns:
- Type: ipywidgets.widgets.VBox
- Description: A VBox whose children are the results of calling render() on self.content["body"] followed by self.content["footer"] (in that order). The returned VBox is a new widget container and does not alter self.content.
- Edge cases:
  - If the child render() calls return non-widget objects, ipywidgets.VBox may raise a TypeError or ValueError depending on ipywidgets' validation. The method itself does not coerce or validate child return types.

## Raises:
- KeyError: if self.content does not contain the keys "body" or "footer" (dict-style access using content["..."] will raise).
- AttributeError: if the retrieved body/footer objects do not expose a callable render attribute (attempting to call .render() will raise).
- Any exception raised by the nested render() calls (propagated directly). For example, nested render() implementations may raise their own domain-specific exceptions.
- TypeError or ValueError from ipywidgets.VBox: if the children sequence passed to VBox is invalid per ipywidgets' constructor validation.
- Note: The method itself does not catch or translate exceptions; callers should handle errors if they need controlled failure modes.

## State Changes:
- Attributes READ:
  - self.content (reads the mapping)
  - self.content["body"] (reads the body Renderable)
  - self.content["footer"] (reads the footer Renderable)
- Attributes WRITTEN:
  - None. This method does not mutate any attributes on self or on the content mapping.

## Constraints:
- Preconditions:
  - self.content must be a mapping containing the keys "body" and "footer".
  - self.content["body"] and self.content["footer"] must be objects implementing a callable render() method that returns an ipywidgets-compatible widget (or sequence acceptable to VBox).
  - The caller must be prepared to accept exceptions propagated from nested render() calls or from ipywidgets.
- Postconditions:
  - Returns an ipywidgets.VBox instance whose children correspond to the rendered body and footer outputs (in that order).
  - self and self.content are unchanged by this call.

## Side Effects:
- Instantiates ipywidgets widgets (a VBox container and whatever widgets are created by body.render() and footer.render()).
- Invokes render() on nested components; those nested renderers may perform side effects (widget creation, lazy computations, caching, or other non-local state changes) depending on their implementations.
- No network I/O, file I/O, or external service calls are performed by this method itself.

