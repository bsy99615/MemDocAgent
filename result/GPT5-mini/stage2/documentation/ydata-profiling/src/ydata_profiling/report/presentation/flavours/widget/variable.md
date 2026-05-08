# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable` · *class*

## Summary:
A concrete Variable presentation that renders its nested top (required) and optional bottom renderables as an ipywidgets VBox — i.e., it aggregates the rendered top and bottom widget children into a vertical box for display in Jupyter/IPython frontends.

## Description:
WidgetVariable is the 'widget' flavour implementation of the generic Variable presentation type. It should be used when the report/presentation is rendered as interactive ipywidgets components rather than HTML or static formats.

Typical callers / factories:
- Presentation factories producing the "widget" flavour of a report.
- Report builders assembling widget-based report sections.
- Conversion utilities that convert plain item dictionaries into concrete Variable instances for the widget flavour.

Motivation and responsibility:
- Encapsulates the presentation detail of "how to display a Variable using ipywidgets". The base Variable class groups two nested renderables ("top" and optional "bottom") but does not implement rendering; WidgetVariable provides that concrete rendering by calling each nested element's render() and returning an ipywidgets.VBox containing those rendered children.
- Responsibility boundary: accepts that nested content is already or will be converted to Renderable-like objects whose render() returns ipywidgets-compatible widget children. It does not validate nested types beyond calling their render() methods and does not alter nested content.

## State:
Inherited state (from Variable / ItemRenderer / Renderable):
- self.content (dict) — required keys populated by Variable.__init__:
  - "top": Renderable
    - Type: object implementing render() that returns an ipywidgets.Widget (or widget-compatible child accepted by widgets.VBox).
    - Constraint: required and expected to be non-None. Variable.__init__ guarantees the key exists; callers must provide a usable renderable.
  - "bottom": Optional[Renderable] or None
    - Type: object implementing render() that returns an ipywidgets.Widget (or widget-compatible child), or None if no secondary view is desired.
    - Constraint: may be None. If not None, must implement render().
  - "ignore": bool
    - Type: bool
    - Default: False (per Variable.__init__)
- self.item_type: str == "variable" (inherited invariant; set when Variable constructed)

Class invariants:
- self.content is a mapping that contains keys "top", "bottom", and "ignore" for the lifetime of the instance.
- content["top"] is expected to be a renderable object; calling render() on it must be valid before WidgetVariable.render() is invoked.
- WidgetVariable.render() does not mutate self.content.

## Lifecycle:
Creation:
- Instantiation uses the inherited Variable constructor:
  - Required: top (Renderable)
  - Optional: bottom (Renderable | None) — default None
  - Optional: ignore (bool) — default False
  - Optional kwargs forwarded to ItemRenderer/Renderable (commonly name, anchor_id, classes)
  - Example signature (inherited): WidgetVariable(top, bottom=None, ignore=False, **kwargs)

Usage (typical call sequence):
1. Construct a WidgetVariable with a top renderable and optionally a bottom renderable.
2. Ensure nested renderables are ready to render (factories often call convert_to_class on nested items before rendering).
3. Call var.render() to obtain an ipywidgets.VBox containing the rendered children.
   - Execution flow: WidgetVariable.render() calls content["top"].render() to get the top widget; if content["bottom"] is not None it calls content["bottom"].render() and appends the result; finally it returns widgets.VBox(items).
4. Display the returned VBox in a Jupyter/IPython context (e.g., simply evaluate the returned VBox or use display()).

Destruction / cleanup:
- WidgetVariable has no explicit cleanup. If nested renderables allocate resources, those renderables are responsible for their own cleanup. There is no context-manager protocol or close() to call on WidgetVariable itself.

## Method Map:
graph LR
  A[Caller] --> B[WidgetVariable.__init__(top, bottom=None, ignore=False, **kwargs)]
  B --> C[instance ready with content.top, content.bottom, content.ignore]
  C --> D[WidgetVariable.render()]
  D --> E[call content["top"].render() -> top_widget]
  D --> F{content["bottom"] is not None?}
  F -- yes --> G[call content["bottom"].render() -> bottom_widget]
  F -- no --> H[skip bottom]
  E --> I[collect children list]
  G --> I
  I --> J[widgets.VBox(children) returned to caller]

## Behavior and constraints of render():
- Return type: ipywidgets.VBox (widgets.VBox).
- Behavior:
  - Calls self.content["top"].render() and includes the returned widget as the first child.
  - If self.content["bottom"] is not None, calls self.content["bottom"].render() and appends it as the next child.
  - Wraps the collected children in widgets.VBox(items) and returns that VBox.
- Non-mutating: render() does not modify self.content.
- Compatibility: top.render() and bottom.render() must return widget instances (subclasses of ipywidgets.Widget) or objects that widgets.VBox accepts as children.

## Edge cases and failure modes (what can go wrong):
- If self.content lacks the "top" key (should not happen when constructed via Variable.__init__), a KeyError will be raised when accessing content["top"].
- If content["top"] or content["bottom"] is not an object with a render() method, AttributeError will be raised when attempting to call .render().
- If top.render() or bottom.render() returns an object not accepted by ipywidgets.VBox (e.g., a raw primitive), widgets.VBox may raise a TypeError at construction time.
- Exceptions thrown by nested render() calls (any exception) propagate up unchanged; WidgetVariable does not catch or transform them.
- If content["bottom"] is None, it is simply omitted (no placeholder child is created).

## Raises:
- AttributeError: if a nested entry does not implement render().
- KeyError: if self.content does not contain required keys (unexpected if constructed via Variable.__init__).
- TypeError: if widgets.VBox rejects the provided children (e.g., children are not widget-like).
- Any exceptions raised by nested render() implementations are propagated.

## Example:
Assume SimpleWidgetRenderable implements a render() method that returns an ipywidgets.Widget (for example, widgets.Label).

1) Construct nested renderables:
   top = SimpleWidgetRenderable(...)
   bottom = SimpleWidgetRenderable(...)

2) Create the WidgetVariable:
   var = WidgetVariable(top=top, bottom=bottom, name="age", anchor_id="var-age")

3) Render to obtain a VBox and display in Jupyter:
   vbox = var.render()   # widgets.VBox([top.render(), bottom.render()])
   display(vbox)         # or simply evaluate vbox in a notebook cell

4) If there is no bottom:
   var2 = WidgetVariable(top=top)
   vbox2 = var2.render()  # widgets.VBox([top.render()])

Notes:
- Because WidgetVariable relies on nested render() implementations to return ipywidgets-compatible widgets, use widget-flavour concrete renderable classes for nested content when building widget-based reports.
- WidgetVariable is safe to use as a concrete Variable implementation for interactive notebook presentations; it is intentionally minimal — composing and vertically stacking child widgets without additional styling.

### `src.ydata_profiling.report.presentation.flavours.widget.variable.WidgetVariable.render` · *method*

## Summary:
Renders this variable as an ipywidgets.VBox by calling render() on the mandatory top sub-renderable and, if present, on the optional bottom sub-renderable, and grouping the resulting widget children into a single vertical container.

## Description:
- Context / known callers:
  - Invoked during the widget-flavour presentation/rendering stage of the reporting pipeline where report items are converted into interactive Jupyter widgets. Typical call sites are presentation factories and report builders that assemble a report's widget representation and then call render() on top-level item renderers to obtain displayable ipywidgets objects.
  - This method is the widget-specific implementation for Variable-like items (the "widget" flavour). It is called when an instance of WidgetVariable (a Variable subclass specialized for ipywidgets output) is expected to produce a visual widget for display in notebooks or other ipywidgets-capable frontends.

- Rationale for being a separate method:
  - Keeps widget-specific composition logic isolated from other flavours (HTML, JSON, etc.). The Variable base class defines the content structure (top/bottom) but does not implement rendering; this method implements the widget-flavour composition by delegating to nested renderables and wrapping their outputs in a VBox. This separation enables multiple presentation flavours to implement their own render strategies without duplicating nesting/assembly logic.

## Args:
- None.

## Returns:
- widgets.VBox
  - A new ipywidgets.VBox instance whose children are the results of:
    - self.content["top"].render() (always included)
    - self.content["bottom"].render() (included only when self.content["bottom"] is not None)
  - Edge cases / possible returned states:
    - Under normal operation the VBox contains valid ipywidgets.Widget children. If nested render() calls return non-widget values, creation of VBox may raise an error (see Raises).
    - The returned VBox is newly constructed on every call; calling render() multiple times produces distinct VBox objects wrapping fresh outputs of nested render() calls.

## Raises:
- KeyError
  - If self.content does not contain the "top" key (this is a violation of Variable's invariants). The implementation assumes "top" exists.
- AttributeError
  - If self.content["top"] (or self.content["bottom"] when present) does not expose a callable render() method.
- Any exception raised by nested render() calls
  - Exceptions raised within self.content["top"].render() or self.content["bottom"].render() propagate unchanged (e.g., RuntimeError, TypeError from nested implementations).
- TypeError / traitlets/ValueError (from ipywidgets)
  - If the items list contains values that are not valid ipywidgets children (e.g., None or plain data), instantiating widgets.VBox(items) may raise a TypeError or traitlets-related validation error.

## State Changes:
- Attributes READ:
  - self.content["top"] — accessed to call its render() method.
  - self.content["bottom"] — accessed (read) to decide whether to call its render() method and include its result.
- Attributes WRITTEN:
  - None. This method does not mutate self or nested content; it only reads nested content and constructs a new ipywidgets.VBox.

## Constraints:
- Preconditions:
  - self.content must be a mapping that contains the key "top" whose value is a renderable object (per Variable invariant).
  - The "top" object's render() method must be callable.
  - If present, the "bottom" value must be either None or a renderable object with a callable render() method.
  - Nested render() methods are expected to return objects compatible with ipywidgets children (ipywidgets.Widget instances); otherwise widgets.VBox construction may fail.
- Postconditions:
  - The returned value is a widgets.VBox containing the outputs from nested render() calls in vertical order: top first, then bottom if present.
  - No mutation to self.content or other attributes of self is performed.

## Side Effects:
- Calls render() on nested renderables (self.content["top"] and optionally self.content["bottom"]). Those nested render() implementations may have their own side effects (allocating resources, performing computations, raising exceptions); those side effects are not managed here and will propagate.
- Creates and returns ipywidgets objects (widget construction). There is no external I/O performed by this method itself (no file/network access), but the creation of widgets may trigger front-end-related behavior when displayed in a notebook.

