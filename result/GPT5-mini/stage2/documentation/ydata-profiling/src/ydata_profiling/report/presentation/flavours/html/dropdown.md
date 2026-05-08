# `dropdown.py`

## `src.ydata_profiling.report.presentation.flavours.html.dropdown.HTMLDropdown` · *class*

## Summary:
A concrete Dropdown renderer that produces an HTML string by rendering the "dropdown.html" Jinja2 template with the inherited Dropdown.content mapping.

## Description:
HTMLDropdown is a thin, HTML-specific implementation of the abstract Dropdown renderer. It exists so that a Dropdown presentation node (which stores identity, styling, item list and an item Container) can be converted into an HTML fragment by applying those values to the "dropdown.html" template provided by the HTML flavour templates module.

When to instantiate:
- When building the HTML flavour of a report presentation tree: factories or deserializers convert generic Renderable-like structures into Dropdown instances and then may wrap or replace them with HTMLDropdown to indicate HTML rendering behavior.
- When a rendering pipeline specifically targets HTML output and needs a renderer object that exposes render() returning an HTML string.

Why this abstraction:
- Keeps rendering concerns for HTML output separate from structural Dropdown data.
- Allows the same Dropdown content to be rendered differently in other flavours (JSON, component-tree) by providing other renderer subclasses.
- Encapsulates the single responsibility: obtain the correct template and render it with the node's content.

Responsibility boundary:
- HTMLDropdown is responsible only for mapping the Dropdown.content into the "dropdown.html" template and returning the resulting string.
- It does not modify content, perform validation on content keys, or manage templates beyond requesting the named template from the flavour's template registry.
- Template selection is fixed ("dropdown.html"); to change markup, update the template file or use a different renderer subclass.

## State:
HTMLDropdown does not introduce new instance attributes. It relies entirely on the inherited Renderable/ItemRenderer/Dropdown state stored in self.content.

Key inherited content keys (see Dropdown for authoritative details):
- content["name"] (str | optional): Human-readable label for the dropdown.
- content["id"] (str): Unique identifier; used by the DOM/template.
- content["items"] (list): Sequence of selectable entries (Renderable instances or values).
- content["item"] (Container): Container/template describing how each entry is rendered.
- content["anchor_id"] (str): Anchor identifier for linking.
- content["classes"] (str): Space-joined CSS classes.
- content["is_row"] (bool): Layout hint (row vs. column).

Invariants:
- content is a dict created by Dropdown.__init__ and is expected to contain the keys above (subject to caller-provided values).
- content["classes"] is a string (result of " ".join(classes) during construction).
- HTMLDropdown does not mutate these invariants; it only reads from content when rendering.

## Lifecycle:
Creation:
- HTMLDropdown inherits Dropdown's constructor. Instantiate using the same arguments required by Dropdown (name, id, items, item, anchor_id, classes, is_row, plus any kwargs forwarded to the base classes).
- No additional constructor arguments or factory methods are required by HTMLDropdown.

Usage (typical sequence):
1. Construct an instance (or convert a generic Renderable into HTMLDropdown via the system conversion utilities).
2. Call html = instance.render() to obtain the HTML fragment for this dropdown.
   - render() uses templates.template("dropdown.html") to fetch the Jinja2 template and calls Template.render(**self.content).
3. Insert or compose the returned HTML string into the final report output.

Destruction:
- No special cleanup is required. HTMLDropdown holds only in-memory Python objects and does not manage external resources or contexts.

## Method Map:
flowchart LR
    DropdownBase[Dropdown.render() -> NotImplementedError] --> HTMLDropdownRender[HTMLDropdown.render() -> str]
    HTMLDropdownRender --> TemplatesTemplate[templates.template("dropdown.html") -> jinja2.Template]
    TemplatesTemplate --> TemplateRender[Template.render(**self.content) -> str]

## Methods
- render(self) -> str
    - Behavior: Fetches the "dropdown.html" template from the HTML flavour templates registry and renders it using the current self.content dict as the template context. Returns the template output as a string.
    - Output type: str (HTML fragment).
    - Side effects: None on the instance; may raise exceptions originating from the templates subsystem.

## Raises:
Exceptions raised by this method are not created by HTMLDropdown itself but are propagated from the template lookup/rendering steps. Notable examples (raised by the underlying jinja2/template system or the template registry):
- jinja2.exceptions.TemplateNotFound: if "dropdown.html" is not available in the template environment used by templates.template(...)
- jinja2.TemplateError (and more specific jinja2 rendering exceptions): if rendering fails due to template logic errors, undefined variables when strict undefined is enabled, or other template-related runtime errors
- Any exception raised by templates.template(...) or by Template.render(...) will propagate to the caller (e.g., AttributeError, TypeError) if the template registry or template instance behaves unexpectedly.

Edge cases:
- If self.content contains objects that the template cannot serialize or access, Template.render may raise a rendering error; callers should ensure that content only contains values the template expects or provide filters to accommodate complex objects.
- HTMLDropdown does not perform content validation; missing expected keys will surface as template undefined-variable behavior according to the Jinja2 configuration.

## Example (conceptual usage):
- Preparation:
  - Build Dropdown content via the Dropdown constructor (name, id, items, item container, anchor_id, classes, is_row).
  - Ensure the HTML template "dropdown.html" is present in the HTML flavour template environment.

- Render flow:
  1. Given an instance d of HTMLDropdown (or a Dropdown converted to HTMLDropdown), call result = d.render().
  2. The call will return a string containing the rendered HTML for the dropdown, which you can embed into the larger HTML report.

Note: HTMLDropdown provides no additional cleanup or lifecycle hooks; treat the returned string as an immutable fragment for composition into the final output.

### `src.ydata_profiling.report.presentation.flavours.html.dropdown.HTMLDropdown.render` · *method*

## Summary:
Renders the dropdown node to an HTML string by loading the "dropdown.html" Jinja2 template and calling its render function with this object's content dictionary as template variables. Does not modify the instance.

## Description:
Known callers and context:
- The HTML flavour presentation renderer (the code path that serializes the presentation tree to HTML) calls this method for Dropdown nodes as the final step to obtain HTML output for a dropdown.
- Higher-level report-generation routines that traverse the presentation tree will invoke this method when they encounter an HTMLDropdown instance.
Lifecycle stage:
- Invoked during the presentation → HTML serialization stage (i.e., when converting a typed presentation tree into HTML).
Why this is a separate method:
- Encapsulates HTML-specific rendering logic (template selection and invocation) so the Dropdown data structure remains renderer-agnostic.
- Allows subclassing or replacement by other flavour renderers (e.g., JSON or component-framework renderers) without changing the Dropdown data model.
- Keeps template name ("dropdown.html") centralized and makes it easy to override/patch in tests.

## Args:
None (method uses instance state; no parameters).

## Returns:
str
- The rendered HTML produced by Jinja2's Template.render when called with the mapping self.content as keyword arguments.
- Edge cases:
  - When rendering succeeds, a Unicode string containing HTML is returned.
  - If the Jinja2 template returns non-string types via custom filters, they are coerced by Jinja2.render into a string in the final result; callers should expect a str.

## Raises:
- TypeError: If self.content is not a mapping of valid keyword names (for example, if it is not a dict-like object or contains keys that are not strings or not valid Python identifiers), the function call using **self.content will raise a TypeError.
- jinja2.exceptions.TemplateNotFound: If the "dropdown.html" template is not available in the configured Jinja2 environment (raised by templates.template).
- jinja2.exceptions.TemplateSyntaxError: If the template contains syntax errors (raised when Jinja2 parses/loads the template).
- jinja2.exceptions.UndefinedError or jinja2.exceptions.TemplateRuntimeError: If the template fails while rendering (e.g., filters or expressions raise during render).
Note: This method does not catch these exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
- self.content (the entire mapping is read and expanded into keyword arguments)
Attributes WRITTEN:
- None (this method does not modify any attributes on self)

## Constraints:
Preconditions:
- self.content must exist and be a mapping (the Dropdown base class guarantees self.content is a dict when properly constructed).
- Keys of self.content used as template variables should be valid Python identifier strings if they are to be passed as keyword arguments (otherwise **self.content may raise TypeError).
- The Jinja2 environment must be configured with a "dropdown.html" template available via templates.template.
Postconditions:
- On success, returns a str containing the rendered HTML and leaves self.content and other object state unchanged.
- On failure, an exception from the Raises section will be propagated and no partial mutation of self is performed.

## Side Effects:
- Triggers Jinja2 template loading which may perform file I/O (depending on the Jinja2 loader configuration) and uses the Jinja2 template cache managed by the Jinja2 environment.
- Calls into template rendering code (filters, tests, or globals configured in the environment) which may themselves have side effects (I/O, logging, or raising exceptions) depending on the environment configuration.
- No network calls are made by this method itself; any external I/O depends on template code or loader configuration.

