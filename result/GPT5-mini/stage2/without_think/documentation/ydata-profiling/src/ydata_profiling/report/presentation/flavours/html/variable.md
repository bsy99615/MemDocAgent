# `variable.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable` · *class*

## Summary:
HTMLVariable is a concrete presentation Variable that renders itself to an HTML string by loading the "variable.html" Jinja2 template and rendering it with the instance's content dictionary as template context.

## Description:
HTMLVariable is the HTML/flavour-specific implementation of the generic Variable presentation item. Instantiate this class when you have a Variable-style item (a required top renderable, an optional bottom renderable, and metadata like name/anchor_id/classes) and you want to produce an HTML fragment using the project's "variable.html" template.

Typical instantiation sites:
- Presentation factories and report builders that assemble HTML output.
- Conversion utilities that convert plain presentation objects into concrete HTML renderers before rendering.

Motivation and responsibility boundary:
- Keeps Variable's structure and semantics (top, bottom, ignore, metadata) but provides a single responsibility: convert that content into an HTML string using the standard "variable.html" template.
- Does not alter the content dict or do nested conversion itself; it delegates template lookup to the module template helper and delegates the rendering behavior to the template.

## State:
HTMLVariable does not introduce new stored attributes beyond those provided by the Variable base class / ItemRenderer / Renderable machinery. The relevant state (inherited) and invariants are:

- content (dict)
  - Keys guaranteed present after construction:
    - "top" -> Renderable (required): the primary nested renderable element. Must be present; Variable.__init__ sets it.
    - "bottom" -> Optional[Renderable] or None: optional secondary element; Variable.__init__ sets this key (may be None).
    - "ignore" -> bool: semantic flag, defaults to False if not provided to constructor.
  - Other optional keys forwarded through **kwargs by the constructor:
    - "name" -> str (optional)
    - "anchor_id" -> str (optional)
    - "classes" -> str (optional)
- item_type (str)
  - Value: "variable" (set by the base ItemRenderer constructor and invariant for the instance).

Class invariants:
- self.content remains a mapping for the instance lifetime.
- The keys "top", "bottom", and "ignore" exist in content after construction.
- HTMLVariable expects that the content values are prepared for use by the Jinja2 template (for example, pre-rendered strings or objects with attributes that the template accesses).

## Lifecycle:
Creation:
- HTMLVariable inherits the Variable constructor signature and behavior. To instantiate:
  - Required:
    - top: Renderable — primary nested renderable item.
  - Optional:
    - bottom: Optional[Renderable] = None — secondary nested renderable.
    - ignore: bool = False — semantic flag.
    - **kwargs: forwarded to ItemRenderer/Renderable (commonly name, anchor_id, classes).
- The constructor is provided by the Variable/ItemRenderer chain; no additional initialization is required by HTMLVariable.

Usage:
- Typical sequence:
  1. Construct the instance (provide top, optionally bottom and metadata).
  2. (Optional) Ensure nested content is converted/prepared (e.g., factories may call convert_to_class on nested items so templates receive ready-to-use objects).
  3. Call render() to produce the HTML string.
- Render contract:
  - render() loads the template named "variable.html" using the flavour templates.template helper, then calls Template.render(**self.content).
  - The template receives the content dict keys as template variables (for example, top, bottom, ignore, name, anchor_id, classes).
  - The template is responsible for how it expects top/bottom to be represented (strings, sub-HTML fragments, or objects with attributes).

Destruction:
- HTMLVariable does not manage external resources and has no cleanup or context-manager protocol. Any resource cleanup belongs to nested renderables, if applicable.

## Method Map:
graph LR
  Caller --> Instantiate[instantiate HTMLVariable(top, bottom=None, ignore=False, **kwargs)]
  Instantiate --> BaseInit[Variable.__init__(top,bottom,ignore, **kwargs)]
  BaseInit --> InstanceReady[HTMLVariable instance with content keys: top,bottom,ignore,...]
  InstanceReady --> RenderCall[HTMLVariable.render()]
  RenderCall --> TemplateLookup[templates.template("variable.html")]
  TemplateLookup --> TemplateObj[jinja2.Template]
  TemplateObj --> RenderExec[TemplateObj.render(**self.content)]
  RenderExec --> HTMLString[return str] 
  RenderExec --> RenderError[propagate Jinja2/runtime exceptions]
  TemplateLookup --> LookupError[propagate template loading exceptions]

(This graph shows the typical flow: construction → template lookup → template rendering → string result or propagated errors.)

## Raises:
When calling HTMLVariable.render(), exceptions raised by the underlying template lookup and rendering are propagated as-is. In particular:

- Exceptions from template lookup (delegated to templates.template), for example:
  - Template not found or loader errors (e.g., jinja2.exceptions.TemplateNotFound)
  - Template compilation errors (e.g., jinja2.exceptions.TemplateSyntaxError)
  - Module-level misconfiguration errors (e.g., NameError, AttributeError) as described by the templates.template helper
  - I/O errors from the loader (e.g., IOError/OSError)
- Exceptions from rendering the template (Template.render(**self.content)):
  - Any runtime exception raised by the template during rendering (propagated, e.g., runtime errors originating in template expressions). The exact exception types depend on the configured Jinja2 environment and template contents.
- Notes:
  - HTMLVariable.render does not catch or wrap these exceptions; callers should handle them if they need to recover or provide fallbacks.

## Example:
Assume SomeRenderable is a concrete Renderable implementation that itself produces string/html when rendered or exposes attributes the template uses.

1) Construct and render a simple variable:
   top = SomeRenderable(data_top)
   var = HTMLVariable(top=top, bottom=None, name="age", anchor_id="var-age")
   try:
       html_fragment = var.render()
   except Exception as e:
       # Handle template loading or rendering errors (e.g., fallback, logging)
       raise

2) Typical factory usage (conversion + render):
   # Factory prepares nested items so the template can use them directly
   top = SomeRenderable.prepare_from(value)
   bottom = SomeRenderable.prepare_from(extra)
   var = HTMLVariable(top=top, bottom=bottom)
   html = var.render()

Notes:
- Because HTMLVariable passes its entire content dict as keyword arguments to the template, ensure the template "variable.html" expects the keys present in content (top, bottom, ignore, plus any metadata keys).
- If nested renderables must be rendered to strings before being used in the template, the factory or template should perform that conversion (HTMLVariable does not implicitly call nested.render()).

### `src.ydata_profiling.report.presentation.flavours.html.variable.HTMLVariable.render` · *method*

## Summary:
Renders this Variable as an HTML fragment by loading the "variable.html" Jinja2 template and invoking its render method with the instance's content mapping; returns the produced HTML string and does not modify the instance state.

## Description:
- Callers and lifecycle:
    - Invoked during the presentation/report "render" stage by HTML-specific presentation code, report builders, or render orchestration that produces the final HTML output for each presentation item.
    - Typical pipeline: presentation objects are assembled/converted (so nested entries are template-ready), then the renderer for the HTML flavour calls this method to produce the HTML fragment for a variable item.
- Why this is a separate method:
    - Encapsulates the HTML-specific rendering logic (template lookup and rendering) so HTML formatting/layout is isolated from data model construction and other flavour renderers (e.g., JSON). Centralizing template usage here makes it easy to change template name, add caching or instrumentation, and keeps caller code concise.

## Args:
    None (the method uses instance state only).

## Returns:
    str: The HTML string returned by jinja2.Template.render(**self.content).
    - On success: a Unicode string containing the rendered HTML fragment.
    - There are no alternate return types; this method does not return None on success.
    - Edge-case returns: an empty string is possible if the template and context produce no visible output.

## Raises:
    - TypeError:
        - If self.content is not a mapping usable for keyword expansion (for example, if keys are not strings), the argument unpacking (**self.content) will raise TypeError.
    - jinja2.exceptions.TemplateNotFound:
        - If the module-level Jinja2 environment cannot locate "variable.html" via its loader.
    - jinja2.exceptions.TemplateSyntaxError:
        - If "variable.html" contains invalid Jinja2 syntax discovered during template compilation.
    - jinja2.exceptions.UndefinedError (or other Jinja2 evaluation errors):
        - If the template attempts to evaluate missing variables or perform operations that raise UndefinedError under the environment's undefined behavior.
    - NameError / AttributeError:
        - If the templates.template wrapper or the module-level jinja2 environment is misconfigured or missing, a NameError/AttributeError may occur when resolving the template.
    - Any exception propagated from the template render process:
        - Template rendering can execute attribute access and callables on context values; exceptions raised during those evaluations propagate out of this method.

## State Changes:
- Attributes READ:
    - self.content — the method reads the mapping and expands its keys/values into the template context.
- Attributes WRITTEN:
    - None. The method does not modify self.content, self.item_type, or any other attribute on self.

## Constraints:
- Preconditions:
    - The module-level Jinja2 environment must be correctly initialized and able to resolve "variable.html" via templates.template("variable.html").
    - self.content must be a dict-like mapping with string keys suitable for keyword expansion; non-string keys will cause a TypeError during ** expansion.
    - Values in self.content must be "template-ready" (e.g., primitives, strings, dicts, or objects whose attributes/methods the template expects). This method does not call nested Renderable.render() for child entries — if nested items require their own rendering, they must be converted to template-ready values before calling this method.
- Postconditions:
    - On normal return, the method returns a str containing the rendered HTML fragment.
    - The instance's state (self.content and self.item_type) is unchanged.

## Side Effects:
- May trigger I/O performed by the Jinja2 loader when templates.template("variable.html") resolves and loads the template (file reads, etc.).
- May allocate memory for the rendered string.
- May cause evaluation of attributes/callables on objects found in self.content as part of Jinja2 rendering; those evaluations may have side effects depending on the objects provided.
- No network calls, file writes, or global state mutations are performed by this method itself (aside from whatever side effects occur indirectly via template loading or evaluation).

## Implementation notes and important behavior to preserve if reimplementing:
- This method delegates entirely to the templates.template(...) wrapper and the resulting Jinja2 Template.render call; it must:
    1. Look up the "variable.html" template using templates.template("variable.html").
    2. Call Template.render(**self.content) and return the resulting str.
- Crucial behavioral detail: it does not call .render() on nested renderable children stored in self.content; callers must ensure nested values are already rendered or otherwise suitable for direct use by the template.
- Ensure that self.content is not mutated and that any errors from template lookup or rendering are allowed to propagate so callers can handle them (consistent with existing project behavior).

