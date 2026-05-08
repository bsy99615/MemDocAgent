# `collapse.py`

## `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse` · *class*

## Summary:
A concrete HTML flavour renderer for Collapse that produces an HTML fragment by applying the "collapse.html" Jinja2 template to the instance's content mapping. Its sole responsibility is converting the structural Collapse instance into an HTML string.

## Description:
HTMLCollapse is a small platform-specific subclass of Collapse used when the reporting/presentation pipeline needs an HTML snippet for a collapsible widget. It is instantiated exactly like Collapse (it inherits Collapse.__init__) and is typically created by report builders or deserializers that choose the HTML flavour for presentation. During final report assembly an HTML renderer/dispatcher or template renderer will call HTMLCollapse.render() to obtain the HTML fragment to embed in the final report.

Why this class exists:
- Separates structural data (Collapse) from platform-specific rendering (HTML).
- Keeps template lookup/rendering logic centralized for the HTML flavour and makes it easy to override or mock rendering in tests.

Known callers / common creation sources:
- Report builders that construct presentation trees for HTML output.
- Deserialization routines that convert neutral representations into HTMLCollapse via Collapse.convert_to_class or factory functions that select the HTML flavour.

Behavior summary:
- render() returns the string result of templates.template("collapse.html").render(**self.content).
- HTMLCollapse does not mutate its state during rendering.

## State:
Attributes inherited from Collapse (the instance will have these, and HTMLCollapse relies on them):

- item_type (str)
  - Value: "collapse"
  - Invariant: must equal "collapse" for instances constructed by Collapse.

- content (Dict[str, Any])
  - Type: dict-like mapping
  - Required keys:
    - "button": ToggleButton
      - Expected type/shape: an object that represents the toggle control (typically a ToggleButton instance or a compatible object the template knows how to render).
    - "item": Renderable
      - Expected type/shape: any Renderable (or already-rendered HTML string) representing the collapsible content.
  - Optional (commonly-present) keys:
    - "name": str
    - "anchor_id": str
    - "classes": str
  - Constraint / invariant: content must be a mapping suitable for expansion with **self.content (i.e., keys are strings, mapping supports the mapping protocol).

Notes on __init__ parameters (inherited from Collapse):
- button (required): an object representing the toggle control. No runtime type enforcement in Collapse; callers must supply a suitable object.
- item (required): an object representing the content to collapse/show. Must be compatible with renderers or already a rendered value.
- **kwargs: optional parameters such as name, anchor_id, classes forwarded to the base Renderable constructor and stored in content.

Class invariants:
- After construction, instance.item_type == "collapse".
- content is a dict and, for well-formed instances, contains at least "button" and "item".
- HTMLCollapse does not add additional persistent state.

## Lifecycle:
Creation:
- Instantiate exactly as Collapse: provide button and item (plus optional kwargs).
  - Example pattern: create ToggleButton and content Renderable, then create Collapse-like instance (factories or deserializers may return an HTMLCollapse instance when HTML flavour is requested).
- No special factory method is required; instantiate using the same constructor that Collapse exposes (HTMLCollapse inherits it).

Usage:
- Typical sequence:
  1. Construct or obtain an HTMLCollapse instance (via builder, factory, or deserialization).
  2. Call render(): str to obtain the HTML fragment representing the collapse widget.
  3. Insert the returned HTML into the larger HTML report document.
- Ordering constraints: None beyond calling render after the instance has been constructed and its content populated with the expected keys.

Destruction / cleanup:
- No cleanup responsibilities (no context manager or close() behavior).
- If nested content objects require cleanup, callers are responsible for invoking their cleanup.

## Method Map:
mermaid
graph LR
    A[Create (Collapse.__init__) with button,item] --> B[instance: HTMLCollapse]
    B --> C[call render()]
    C --> D[templates.template("collapse.html")]
    D --> E[jinja2.Template.render(**self.content)]
    E --> F[returns str HTML fragment]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style C fill:#bbf,stroke:#333,stroke-width:1px

Notes on the flow:
- render() delegates to templates.template to obtain a jinja2.Template object for "collapse.html", then calls its .render method with the instance content expanded as keyword arguments.

## Raises:
The method does not explicitly raise custom errors itself, but the following exceptions can propagate from template lookup or rendering:

- jinja2.exceptions.TemplateNotFound
  - Trigger: the "collapse.html" template is not available to the Jinja2 environment used by templates.template.

- jinja2.exceptions.TemplateSyntaxError or other jinja2.exceptions.TemplateError
  - Trigger: the template contains invalid syntax or raises an error while being compiled/evaluated.

- TypeError
  - Trigger: self.content is None or is not a mapping; expanding **self.content will raise TypeError.
  - Trigger: if keys of content are not strings (invalid for keyword expansion).

- Any exception raised during template evaluation
  - Trigger: expressions inside the template access attributes or call methods on objects in content that raise exceptions; those exceptions propagate out of render().

I/O and side-effect notes:
- templates.template may perform I/O (e.g., filesystem reads) depending on the Jinja2 loader configuration; such I/O errors (e.g., OSError) may propagate indirectly.
- Template rendering may call methods on objects held in content that have side effects; HTMLCollapse itself performs no side effects beyond calling into the template system.

## Example:
- Creation and rendering (descriptive steps, not exact import lines):
  1. Build or obtain a ToggleButton instance representing the control and a Renderable (or rendered HTML string) for the collapsible content.
  2. Construct the Collapse-structured object using the Collapse constructor or factory that returns HTMLCollapse (the constructor parameters are the same as Collapse's): the resulting instance will have content mapping containing "button" and "item".
  3. Obtain HTML by calling render() on the HTMLCollapse instance. The returned value is a string containing the HTML fragment produced by the "collapse.html" Jinja2 template applied to the instance content.
  4. Insert the returned HTML into the larger HTML report.

Typical minimal usage pattern in prose:
- Given an HTMLCollapse instance named collapse:
  - html_fragment = collapse.render()
  - embed html_fragment into the final HTML report

Edge-case examples to be mindful of:
- If collapse.content is malformed (None or not a mapping), collapse.render() will raise TypeError when expanding **collapse.content.
- If the Jinja2 template is missing or broken, appropriate jinja2 exceptions will propagate; callers should catch these where needed.

### `src.ydata_profiling.report.presentation.flavours.html.collapse.HTMLCollapse.render` · *method*

## Summary:
Render the collapse widget to an HTML string by applying the "collapse.html" Jinja template to the instance's content mapping; this produces the final HTML fragment without mutating the object.

## Description:
- Known callers and lifecycle:
  - Called by HTML presentation renderers or dispatchers during the final presentation stage of report generation when a Collapse (or its HTML-specific subclass HTMLCollapse) must be converted into an HTML fragment.
  - Typical pipeline step: the report builder assembles presentation components (ToggleButton + item) into a Collapse instance; an HTML renderer locates the HTML flavour renderer for collapses and invokes this method to produce the snippet incorporated into the final HTML report.
- Reason for being its own method:
  - Encapsulates platform-specific presentation logic for collapsible widgets (HTML flavour) and isolates template rendering so it can be overridden or mocked in tests.
  - Keeps templating concerns out of structural classes (Collapse) and centralizes HTML rendering in the HTML flavour implementation.

## Args:
- None.

## Returns:
- str: The rendered HTML produced by templates.template("collapse.html").render(**self.content).
  - Typical value: a non-empty HTML fragment containing markup for the toggle control and the collapsible content.
  - Edge-case values:
    - Empty string: returned if the template renders to empty output.
    - If the template renders successfully but some variables are undefined, the exact output depends on the Jinja2 environment configuration (it may contain Jinja "undefined" placeholders or empty content).

## Raises:
- Any exception raised by the template lookup or rendering is propagated:
  - jinja2.exceptions.TemplateNotFound: if the "collapse.html" template cannot be located by the Jinja2 environment used by templates.template.
  - jinja2.exceptions.TemplateSyntaxError or other jinja2.exceptions.TemplateError: if the template contains invalid syntax or a template-time error occurs.
  - TypeError: if self.content is not a mapping (for example, if self.content is None or a non-mapping object), Python raises a TypeError when expanding **self.content into keyword arguments.
  - Any exception raised indirectly while evaluating template expressions (for example, if template attempts to call methods or access attributes on objects inside content that raise) will also propagate.

## State Changes:
- Attributes READ:
  - self.content — reads the instance's content mapping and uses its keys/values as template variables.
- Attributes WRITTEN:
  - None — this method does not mutate self or its attributes.

## Constraints:
- Preconditions:
  - self.content must be a mapping (dict-like) that can be expanded as keyword arguments (i.e., supports the mapping protocol required by ** unpacking). In practice, a dict created by Collapse contains at least:
    - "button": a ToggleButton object (or value the template expects for the control)
    - "item": a Renderable or already-rendered value for the collapsible content
  - The "collapse.html" template must be present in the Jinja2 environment used by templates.template.
- Postconditions:
  - The method returns a str containing the template rendering result.
  - The instance's state (including self.content) remains unchanged.

## Side Effects:
- Template lookup (templates.template(...)) may perform I/O depending on the Jinja2 loader configuration (e.g., filesystem access when loading templates).
- Template rendering may call methods or access attributes on objects contained in self.content; those calls can have side effects if the contained objects implement side-effecting behavior (this method does not itself perform such side effects, but they may occur during rendering).
- No network calls or external service calls are performed by this method directly; any external interactions that occur are indirect via template code or objects passed in content.

