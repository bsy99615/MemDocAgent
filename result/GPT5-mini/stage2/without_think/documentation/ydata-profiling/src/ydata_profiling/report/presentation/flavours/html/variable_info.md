# `variable_info.py`

## `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo` · *class*

## Summary:
Represents an HTML-specific VariableInfo presenter whose responsibility is to render a single variable information block by applying this instance's content mapping to the "variable_info.html" Jinja2 template and returning the rendered HTML string.

## Description:
HTMLVariableInfo exists to separate HTML templating concerns for a variable-information fragment from the data-preparation and higher-level report assembly logic. It is a thin HTML flavour implementation of the generic VariableInfo presentation component and is instantiated by report-generation code that prepares per-variable context dicts (the content) and hands them to a VariableInfo factory or initializer.

Typical scenarios and callers:
- A report builder that iterates over dataset variables, creates a VariableInfo (flavoured) instance for each variable, and collects HTML fragments to assemble a full HTML report.
- Presentation utilities that accept VariableInfo instances and call render() to obtain the HTML snippet for insertion into a page layout.

Motivation and responsibility boundary:
- This class is solely responsible for converting the prepared variable context (self.content) into an HTML fragment using the project's Jinja2 templates. It intentionally does not prepare or validate the content beyond passing it into the template rendering step; data validation and content construction are the responsibility of callers or of the VariableInfo superclass.

## State:
Attributes (inherited or required by this class)
- content (Mapping[str, Any])
  - Type: a mapping (for example, dict) whose keys are strings used as template variable names and whose values are the corresponding objects to be rendered.
  - Required: Yes — HTMLVariableInfo.render() unpacks this mapping as keyword arguments for template rendering.
  - Valid values: any mapping that can be safely expanded via Python's "**" argument-unpacking. Keys must be valid Python identifiers when used as keyword names in the template context (typical case: string keys).
  - Invariant: content is present and mapping-like when render() is called.

Notes on __init__ parameters:
- HTMLVariableInfo does not declare its own __init__; it inherits construction and public attributes from VariableInfo. This documentation does not assume the exact signature of VariableInfo.__init__; callers must ensure the resulting instance has a content mapping before calling render().

Class invariants:
- For correct operation, any instance of HTMLVariableInfo must expose a content attribute that is a mapping. The implementation guarantees no mutation of instance state during rendering.

## Lifecycle:
Creation:
- Instantiate via whatever factory or constructor the codebase provides for VariableInfo-flavoured classes (e.g., a presentation factory). No additional constructor arguments are introduced by this subclass.
- Alternatively, create an instance using the VariableInfo constructor and then cast/subclass to HTMLVariableInfo if necessary — the key requirement is that the instance has a valid content mapping assigned prior to render().

Usage:
- Typical sequence:
  1. Prepare a mapping with keys that match the expected template variables for "variable_info.html".
  2. Ensure an HTMLVariableInfo instance exists with its content attribute referencing that mapping.
  3. Call instance.render() to obtain an HTML string.
  4. Insert the returned HTML fragment into the larger report layout.

- Ordering constraints: There is no required order among multiple instances; render() may be called repeatedly on the same instance to produce updated HTML if content is mutated by the caller between calls.

Destruction / Cleanup:
- There are no explicit cleanup responsibilities: HTMLVariableInfo does not open persistent resources, nor does it implement context-manager semantics or close methods. Any cleanup is the responsibility of the caller or the template environment if it holds resources.

## Method Map:
flowchart TD
    Render[render()] -->|calls| TemplateLookup[templates.template("variable_info.html")]
    TemplateLookup -->|returns| JinjaTemplate[Jinja2 Template]
    JinjaTemplate -->|calls| TemplateRender[Template.render(**self.content)]
    TemplateRender -->|returns| HTMLStr[returns str]

Typical invocation:
- render() -> templates.template(...) -> Template.render(**self.content) -> returned HTML string

## Raises:
The render() method performs no explicit error handling and propagates exceptions from attribute access, the template lookup helper, and Jinja2 rendering. Notable exceptions include:
- AttributeError: If the instance lacks a content attribute (accessing self.content will raise).
- TypeError: If self.content is not a mapping (for example, None or a list); the "**self.content" unpacking will raise TypeError.
- jinja2.exceptions.TemplateNotFound: If the module-level templates.template cannot locate "variable_info.html".
- jinja2.exceptions.TemplateSyntaxError: If the template contains invalid Jinja2 syntax.
- jinja2.exceptions.UndefinedError or other TemplateRuntimeError subclasses: If rendering fails due to undefined variables or runtime errors in the template.
- IOError / OSError: If the configured Jinja2 loader performs filesystem I/O and that I/O fails during template loading or reading.
- Any other exception raised by the module-level templates.template helper or the Jinja2 environment is propagated to the caller.

## Example:
- Preparation: Build a mapping (for example, a dict) whose keys match the variables expected by the "variable_info.html" template (e.g., "name", "type", "missing_count", "statistics", etc.). The exact keys are defined by the template itself and by the code that prepares variable contexts.
- Instantiation: Obtain an HTMLVariableInfo instance via the project's presentation factory or by constructing the appropriate presentation class so the instance has its content attribute set to the prepared mapping.
- Rendering: Call render() on the instance. On success, you receive an HTML string containing the fully rendered variable-info fragment ready to be inlined into the report's HTML.
- Reuse: To re-render with updated data, update the content mapping on the instance (or create a new instance) and call render() again.
- Error handling: Wrap the call to render() in try/except if you want to recover from missing templates or runtime rendering errors (for example, by substituting a fallback fragment or logging a clear diagnostic).

### `src.ydata_profiling.report.presentation.flavours.html.variable_info.HTMLVariableInfo.render` · *method*

## Summary:
Renders the "variable_info.html" Jinja2 template using this object's content dict and returns the resulting HTML string. Does not modify the object's state.

## Description:
This method loads the "variable_info.html" template via the module-level templates.template(...) helper and renders it with the mapping held in self.content. It is typically invoked during HTML report assembly to produce the HTML fragment for a single variable's information section.

Known callers:
- No concrete callers were discovered in the provided context. Typical call sites are:
  - Higher-level report rendering code that assembles page sections into a full HTML report.
  - Presentation utilities that convert VariableInfo instances to an HTML string before insertion into a report layout.

Why this is a separate method:
- Encapsulates the template lookup and rendering logic for a variable-info block, keeping template-related code isolated from data preparation and higher-level report assembly.
- Makes it straightforward to override or extend rendering in subclasses (for example, to use a different template or to pre-process content) without changing callers.

## Args:
None.

However, this method relies on an attribute on self:
- content (mapping): A mapping (for example, dict) whose keys are strings matching the template context variables. The method performs a parameter expansion using **self.content, so content must be a mapping compatible with Python's argument unpacking.

## Returns:
str: The rendered template output (typically an HTML fragment). On success this is the string returned by Jinja2's Template.render(...).

Edge-case return values:
- There are no alternate successful return types; on failure the method raises an exception instead of returning a non-str value.

## Raises:
This method does not catch exceptions; it propagates errors raised while locating or rendering the template. Notable exceptions that may be raised include (but are not limited to):
- AttributeError: If the instance has no attribute content, accessing self.content will raise AttributeError.
- TypeError: If self.content is not a mapping (e.g., None or a list), using **self.content raises TypeError.
- jinja2.exceptions.TemplateNotFound: If the configured Jinja2 loader cannot locate "variable_info.html" (propagated from templates.template).
- jinja2.exceptions.TemplateSyntaxError: If the template contains invalid Jinja2 syntax (propagated from templates.template).
- jinja2.exceptions.UndefinedError or other TemplateRuntimeError subclasses: If rendering fails due to undefined variables, filter errors, or runtime issues inside the template.
- IOError / OSError: If the underlying loader performs filesystem I/O and that I/O fails (propagated from templates.template or Jinja2 during rendering).
- NameError / AttributeError: If the templates module is misconfigured such that the module-level environment is missing or malformed (propagated from templates.template).

## State Changes:
Attributes READ:
- self.content

Attributes WRITTEN:
- None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
- self.content must exist and be a mapping (dict-like) with string keys suitable for use as keyword argument names in the template context.
- The module-level templates helper must be correctly configured so templates.template("variable_info.html") resolves to a valid Jinja2 Template object.

Postconditions:
- On normal return, the method returns a str that is the rendered template output.
- The object's attributes remain unchanged.

## Side Effects:
- Template lookup may perform file I/O (depending on the configured Jinja2 loader); those reads occur during the call and may raise I/O-related exceptions.
- Template rendering may execute template code, filters, or calls configured in the Jinja2 environment. Any side effects triggered by template code or custom filters (e.g., logging, database calls) are possible but are induced by the template or filters themselves, not by this method directly.
- No network calls, file writes, or mutation of external objects are performed by this method itself (aside from effects performed by Jinja2 filters or the loader).

