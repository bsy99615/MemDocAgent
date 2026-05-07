# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo` · *class*

## Summary:
A concrete VariableInfo renderer that produces an ipywidgets.HTML widget by rendering the "variable_info.html" Jinja2 template with the VariableInfo.content payload.

## Description:
WidgetVariableInfo is a small presentation-layer renderer intended for interactive / notebook environments. It should be instantiated when a report or presentation factory needs a widget-based representation of a single variable's metadata (anchor, name, type, description, alerts, and style) that can be displayed inside Jupyter notebooks or other ipywidgets-capable frontends.

Typical callers
- Presentation factories or report builders that construct VariableInfo payloads and choose a widget-based renderer for interactive reports.
- Higher-level orchestration code that collects VariableInfo-derived instances and calls render() to obtain displayable ipywidgets elements.

Motivation and responsibility boundary
- Responsibility: convert the structured content carried by the VariableInfo base class (self.content) into an ipywidgets.HTML instance by rendering a specific HTML template ("variable_info.html") with that content.
- Boundary: does not alter or validate content; it delegates template lookup to templates.template(...) and template rendering to Jinja2's Template.render(**context). It does not manage template environment configuration nor perform post-render sanitization.

## State:
Inherited attributes (from VariableInfo)
- item_type: str
  - Value: "variable_info"
  - Invariant: never changed by this class; present after construction.
- content: dict
  - Type: dict
  - Required keys (as produced by VariableInfo constructor and expected by the template):
      - "anchor_id": str
      - "var_name": str
      - "description": str
      - "var_type": str
      - "alerts": List[Alert]
      - "style": Style
  - Notes: WidgetVariableInfo uses this dict verbatim as the template context. The dict is shared by reference with the creator; callers must avoid unexpected mutation.

No additional attributes are introduced by WidgetVariableInfo.

Class invariants
- After construction (inherited): self.item_type == "variable_info" and self.content contains the keys listed above.
- For every successful render(): the returned object is an instance of ipywidgets.widgets.HTML whose value equals the string returned by the Jinja2 template render call when invoked with **self.content.

## Lifecycle:
Creation
- Instantiate exactly as for VariableInfo (WidgetVariableInfo does not override __init__):
  - Required positional arguments (inherited): anchor_id (str), var_name (str), var_type (str), alerts (List[Alert]), description (str), style (Style)
  - Optional: **kwargs forwarded to the base constructor for metadata insertion.
- No special factory methods are required; typical instantiation is performed by presentation factories that already create VariableInfo instances.

Usage
- Typical sequence:
  1. Create WidgetVariableInfo(...) with the same constructor signature as VariableInfo.
  2. Call instance.render() to obtain an ipywidgets.widgets.HTML object ready for display.
  3. In a notebook, pass the returned widget to display(...) or include it in a widget layout.
- There is no required ordering of other methods; render() may be called multiple times (idempotent from this class's perspective — each call re-renders the template from current self.content and returns a fresh widgets.HTML wrapper).

Destruction / cleanup
- No cleanup is required by this class. It creates an ipywidgets HTML widget but does not manage external resources or lifecycle beyond returning that widget. If callers attach widget event handlers or other external resources, callers are responsible for teardown.

## Method Map:
graph LR
  Instance[WidgetVariableInfo instance (has self.content)] --> RenderCall[render()]
  RenderCall --> TemplateLookup[templates.template("variable_info.html")]
  TemplateLookup --> JinjaRender[Template.render(**self.content)]
  JinjaRender --> WidgetsHTML[widgets.HTML(rendered_html_string)]
  WidgetsHTML --> Return[Return ipywidgets.widgets.HTML]

(Invocation path illustrated: render() → template lookup → Jinja2 render → wrap in widgets.HTML → return)

## Raises:
WidgetVariableInfo does not itself catch or raise new exception types. Errors that may propagate from render() include, but are not limited to:
- NameError, AttributeError: if the templates module or its jinja2 environment is misconfigured (propagated from templates.template).
- jinja2.exceptions.TemplateNotFound: if "variable_info.html" cannot be found by the configured Jinja2 loader.
- jinja2.exceptions.TemplateSyntaxError: if the template contains invalid Jinja2 syntax.
- jinja2.exceptions.UndefinedError (or other runtime errors during rendering): if Template.render(**self.content) fails because the context is missing expected names, or template logic raises errors.
- IOError / OSError: underlying loader I/O failures during template access.
- TypeError / ValueError: if widgets.HTML rejects the rendered output (e.g., invalid parameter types), or if invalid types are present in self.content that cause Template.render to fail.
Callers should catch and handle these exceptions at the presentation orchestration layer if they require graceful degradation or fallbacks.

## Example:
1) Creation (same constructor as VariableInfo):
   Create an instance supplying the metadata expected by VariableInfo (anchor_id, var_name, var_type, alerts, description, style). Example (conceptual, not a function definition):
   - instance = WidgetVariableInfo(anchor_id, var_name, var_type, alerts, description, style, name="Age block")

2) Rendering and display (typical notebook usage):
   - widget = instance.render()
   - Display the widget in a Jupyter notebook: display(widget)
   - The widget.value (or HTML body) equals the HTML string produced by rendering "variable_info.html" with the instance.content dict.

3) Error handling pattern:
   - Wrap render() in try/except to catch jinja2.exceptions.TemplateNotFound and provide a fallback (for example, log and render a minimal HTML string or a fallback template).
   - If the template relies on specific keys being present in content, ensure the factory that constructs the VariableInfo supplies them; otherwise, Template.render may raise UndefinedError at runtime.

Implementation note for re-implementers:
- Implement render() to perform exactly these steps:
  1. Call templates.template("variable_info.html") to obtain a Jinja2 Template (propagate any exceptions).
  2. Call template.render(**self.content) to produce an HTML string (propagate rendering exceptions).
  3. Wrap the resulting string into an ipywidgets.widgets.HTML instance and return it.
- Do not mutate self.content; do not swallow exceptions — allow callers to handle template-loading/rendering issues.

### `src.ydata_profiling.report.presentation.flavours.widget.variable_info.WidgetVariableInfo.render` · *method*

## Summary:
Creates and returns an ipywidgets.HTML widget containing the variable-info template rendered with this instance's content.

## Description:
This method builds the final widget representation for a single variable info block by:
1. Looking up the Jinja2 template named "variable_info.html" via the project's template helper.
2. Rendering that template with the mapping stored on the instance (self.content).
3. Wrapping the resulting HTML string in an ipywidgets.HTML widget and returning it.

Known callers and lifecycle stage:
- Called by presentation factories, report builders, or higher-level report orchestration code when producing a widget-based (notebook) representation of a variable summary. It is invoked after a WidgetVariableInfo instance has been constructed and fully populated with its content; typically this is part of the report-generation/rendering stage for Jupyter Notebook outputs.

Why this is a separate method:
- Rendering to an ipywidgets.HTML widget is a presentation concern specific to the "widget" flavour. Keeping this logic in a dedicated render() method (in a flavor-specific subclass) separates content preparation (done by VariableInfo and factories) from presentation conversion (templating + widget construction), enabling other flavours (HTML string, JSON, etc.) to implement their own rendering without duplication.

## Args:
- None (method uses state on self)

## Returns:
- ipywidgets.HTML
  - A newly-constructed HTML widget whose value is the template-rendered string produced by templates.template("variable_info.html").render(**self.content).
  - On success the returned widget contains the final HTML ready for display in a Jupyter environment.

## Raises:
This method does not catch exceptions; it propagates errors from the template lookup, template rendering, or widget construction. Notable exceptions callers should expect and may choose to handle:
- NameError: if the templates module or its module-level environment is not defined (propagated from the template wrapper).
- AttributeError: if the module-level object used by templates.template does not expose get_template (propagated from the template wrapper).
- jinja2.exceptions.TemplateNotFound: if "variable_info.html" cannot be located by the configured Jinja2 loader.
- jinja2.exceptions.TemplateSyntaxError: if the template contains invalid Jinja2 syntax.
- IOError / OSError: if the underlying template loader triggers I/O errors while reading template sources.
- Any exception raised by Template.render(...) (propagated; e.g., if custom filters or context processing raise errors).
- Any exception raised by ipywidgets.HTML constructor if widget creation fails (for example, if the underlying library raises for invalid input types).

## State Changes:
Attributes READ:
- self.content (dict): used as the template context. Expected keys (as provided by VariableInfo constructor) include:
  - "anchor_id": str
  - "var_name": str
  - "description": str
  - "var_type": str
  - "alerts": List[Alert]
  - "style": Style
Attributes WRITTEN:
- None. The method does not mutate self or external objects.

## Constraints:
Preconditions:
- self.content must exist and be a mapping compatible with Jinja2 Template.render keyword arguments.
- The module-level template environment accessed by templates.template(...) must be correctly initialized so that "variable_info.html" can be resolved (otherwise template lookup will raise).
- The content mapping should contain the keys expected by the template; missing keys may result in unexpected rendered output or template-related errors depending on the Jinja2 configuration.

Postconditions:
- If the method returns normally, a new ipywidgets.HTML instance has been created and returned containing the rendered HTML for this variable info block.
- The instance's state (self.content and other attributes) is unchanged.

## Side Effects:
- Template loading may perform file I/O (reading template sources) depending on the configured Jinja2 loader.
- Instantiates an ipywidgets.HTML object (UI widget allocation) which may interact with the Jupyter front-end when displayed later.
- No network calls, persistent storage writes, or modifications to global module state are performed by this method itself. Exceptions raised by template loading/rendering or widget construction are propagated to the caller.

