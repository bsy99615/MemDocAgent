# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton` · *class*

## Summary:
Renders a ToggleButton as an HTML fragment by applying the 'toggle_button.html' Jinja2 template to the instance's content.

## Description:
HTMLToggleButton is a concrete renderer for the semantic toggle item provided by ToggleButton. It exists to produce the HTML representation of a toggle control (for example, "Show details" / "Hide details") by loading the preconfigured Jinja2 template named "toggle_button.html" and rendering it with the ToggleButton instance's content dictionary as the template context.

Typical usage scenarios:
- Report generation pipelines or presentation factories that build a list of presentation items and need an HTML-specific renderer for items with item_type "toggle_button".
- Places where ToggleButton instances are created (via ToggleButton constructor or presentation factories) and later passed to a renderer that expects an object implementing render() returning a string.

Why this class:
- Separates HTML-specific rendering from the generic ToggleButton payload/semantics.
- Keeps rendering concerns (template lookup + context binding) encapsulated in a single class so the rest of the presentation code can work with ToggleButton instances uniformly.

Known callers / factories:
- Presentation factories or report builders that assemble HTML-flavored renderers.
- Any code that expects an object implementing a render() -> str for inclusion in an HTML report.

## State:
Inherited state (from ToggleButton / ItemRenderer chain)
- item_type: str
  - Value: the literal "toggle_button".
  - Invariant: must remain "toggle_button" for the lifetime of the instance.

- content: dict[str, Any]
  - Required keys: at minimum the key "text" is populated by ToggleButton initialization with the label passed by the caller.
  - Optional keys that may be present (provided via kwargs during creation by the ItemRenderer/Renderable chain): "name", "anchor_id", "classes".
  - Constraint: keys must be strings when render() is invoked because content is unpacked into keyword arguments (**self.content).
  - Note: content is a live, mutable dict. External mutation affects subsequent renders.

Derived / implicit state:
- There is no new attribute introduced by HTMLToggleButton; it relies on the attributes established by the ToggleButton base class.

Class invariants:
- self.content is a dict and contains at least "text".
- self.item_type == "toggle_button".
- Before calling render(), callers should ensure that self.content keys are strings (so **self.content is valid).

## Lifecycle:
Creation:
- Instantiation uses the same constructor signature as ToggleButton (text: str, **kwargs). The required argument is the textual label that will appear on the toggle control and is stored as content["text"] by the ToggleButton initializer.
- No HTMLToggleButton-specific initialization is required beyond ToggleButton's constructor.

Usage:
- After creation, call render() once or multiple times to obtain an HTML string.
- Typical call sequence:
  1. Instantiate: provide the label via the text parameter (and optional kwargs such as name, anchor_id, classes).
  2. Optionally mutate or augment self.content with additional keys expected by the template (ensuring keys are strings).
  3. Call render() to produce the HTML string.
- There is no required ordering of other methods; render() is self-contained and does not require prior setup beyond ensuring the Jinja2 environment and template are available.

Destruction / cleanup:
- HTMLToggleButton does not open or own external resources and therefore has no cleanup or close() responsibilities.
- If external code injects resources into content values that require cleanup, that is the responsibility of that external code.

## Method Map:
graph LR
  A[HTMLToggleButton.render()] --> B[templates.template("toggle_button.html")]
  B --> C[Jinja2 Template object]
  C --> D[Template.render(**self.content)]
  Note[Preconditions: self.content keys must be strings] --> A
  Note2[Possible exceptions propagate from template lookup and render] --> A

(Interpretation: render() calls the templates.template helper to obtain a Template, then calls Template.render with the instance's content unpacked into template variables.)

## Behavior and I/O:
- render() -> str
  - Action: loads the template named "toggle_button.html" via the module-level template helper and calls Template.render(**self.content).
  - Return: the result of Template.render, expected to be a string (HTML fragment).
  - Side effects: may perform template file I/O during template lookup (delegated to the Jinja2 loader).

## Raises:
Exceptions that may be raised by __init__ (inherited behavior):
- TypeError
  - Trigger: if invalid keyword arguments are passed that are not accepted by the upstream initializer, or if other type-related issues occur during superclass initialization. ToggleButton itself does not explicitly validate types.

Exceptions that may be raised by render():
- jinja2.exceptions.TemplateNotFound
  - Trigger: when the configured Jinja2 loader cannot locate "toggle_button.html".
- jinja2.exceptions.TemplateSyntaxError
  - Trigger: if the template contains invalid Jinja2 syntax and the environment raises this when compiling the template.
- TypeError
  - Trigger: if self.content contains non-string keys; Python raises a TypeError when attempting to expand a mapping with non-string keys as keyword arguments (**mapping).
- jinja2.exceptions.UndefinedError or other TemplateRuntimeError variants
  - Trigger: errors during template rendering (for example, attribute access on None if the template expects attributes not present, or explicit runtime errors raised by expressions inside the template).
- Any other exceptions raised by the underlying template loader/environment (IOError/OSError during file access, configuration-related NameError/AttributeError if the module-level jinja2_env is misconfigured). These are propagated; HTMLToggleButton does not catch them.

Notes:
- HTMLToggleButton does not perform validation of content values; it trusts that content has the keys/values the template expects. If strict validation is required, callers should validate or transform content before calling render().

## Example:
1) Creation and simple render (happy path):
   - Create an instance by supplying the toggle label as the text argument. After construction, the instance's content contains {"text": <label>}.
   - Call render() to receive an HTML string generated by the "toggle_button.html" template using the content dict as the template context.

2) Safe rendering with error handling (pattern):
   - Ensure the Jinja2 environment and the "toggle_button.html" template are available.
   - Optionally ensure all expected keys are present in content and that keys are strings.
   - Call render() inside try/except to handle TemplateNotFound or rendering errors and provide a fallback (for example, a simple fallback HTML snippet).

3) Mutating content before render:
   - If the template uses additional variables such as name, anchor_id, or classes, set those keys on content (ensuring keys are strings) before calling render() so the template has access to them.

Summary of typical minimal usage:
- Construct with a text label -> optionally add metadata to content -> call render() -> insert returned HTML into the larger report page.

### `src.ydata_profiling.report.presentation.flavours.html.toggle_button.HTMLToggleButton.render` · *method*

## Summary:
Renders the toggle button's HTML by loading the "toggle_button.html" Jinja2 template and rendering it with this object's content, returning the produced HTML string.

## Description:
This method is called when the presentation pipeline needs the HTML fragment for a toggle button (for example, when assembling or serializing an HTML report). Typical callers are higher-level HTML report builders or presentation renderers that iterate over presentation components and call render() on each to produce final HTML pages.

This logic is separated into its own method to centralize HTML rendering for this component:
- Keeps template lookup and rendering in one place and decouples HTML generation from business logic.
- Allows subclasses or presentation flavours to override or extend rendering behavior without duplicating template handling code.
- Makes testing and substitution (e.g., using a different template environment) straightforward.

## Args:
    None.

The method does not accept parameters; it uses the instance attribute self.content as the rendering context.

## Returns:
    str: The rendered HTML produced by Jinja2 Template.render. On success this is the HTML fragment for the toggle button (possibly an empty string if the template renders to empty output).

Edge-case returns:
- The method does not return None. If rendering succeeds it always returns a str. If rendering fails an exception is raised instead of returning.

## Raises:
    Propagates exceptions raised during template lookup or rendering:
    - jinja2.exceptions.TemplateNotFound and jinja2.exceptions.TemplateSyntaxError (or other errors) raised by templates.template("toggle_button.html") if the template cannot be found or is invalid (these are documented behaviors of the template() helper).
    - TypeError if self.content is not a mapping suitable for argument-unpacking with ** (for example, None or a non-mapping object).
    - Any exception raised during Template.render (for example runtime errors originating from template expressions) is propagated to the caller.

No exceptions are caught or wrapped by this method; callers should handle or propagate them.

## State Changes:
Attributes READ:
    - self.content: used as the context passed into the template rendering.

Attributes WRITTEN:
    - None. This method does not modify the object's attributes.

## Constraints:
Preconditions:
    - self.content must be a mapping (e.g., dict) whose keys are valid Python identifiers/strings suitable as template variable names. The mapping will be expanded into keyword arguments via **self.content.
    - The module-level Jinja2 environment used by templates.template must be configured such that "toggle_button.html" is resolvable.

Postconditions:
    - If the method returns normally, it guarantees a str containing the rendered HTML fragment.
    - The object's state is unchanged (no side-effect on self).

## Side Effects:
    - Template loading may perform I/O (file reads) depending on the configured Jinja2 loader; those I/O errors may surface as exceptions from templates.template.
    - No external network calls, file writes, or mutation of global state are performed by this method itself (aside from whatever side effects may occur inside the template engine during rendering).
    - No logging is performed by this method.

## Implementation notes (for reimplementation):
    - Call the project's template resolver for "toggle_button.html" to obtain a Jinja2 Template object, then call Template.render(**self.content).
    - Avoid catching exceptions here unless the caller expects graceful degradation; the current design propagates template lookup and rendering errors to callers.

