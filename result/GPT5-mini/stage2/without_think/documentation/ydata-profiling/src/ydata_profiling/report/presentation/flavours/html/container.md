# `container.py`

## `src.ydata_profiling.report.presentation.flavours.html.container.HTMLContainer` · *class*

## Summary:
An HTML-specific Container subclass that renders a grouped sequence of child renderables into an HTML fragment by selecting and invoking a Jinja2 template based on the container's sequence_type.

## Description:
HTMLContainer is used by the HTML presentation flavour to serialize Container-like groups (lists, tabs, grids, sections, etc.) into HTML snippets. The presentation/renderer builds Container instances (via factory code or direct construction) and calls render() on them when assembling the final HTML report.

Why this class exists:
- Centralizes the mapping from an abstract sequence_type token to a concrete HTML template and the exact template context keys required.
- Keeps template-selection logic colocated so adding new sequence types or changing context names is localized.

Typical callers:
- Report assembly or renderer components that traverse a tree of renderable nodes and need HTML fragments for container nodes.

## State:
(Attributes are inherited from Container / Renderable unless noted.)

- sequence_type (str)
    - Meaning: Template selector token that determines which HTML snippet to produce.
    - Supported values: "list", "accordion", "named_list", "tabs", "select", "sections", "grid", "batch_grid".
    - Invariant: Must be a str; if it is any other value, render() will raise ValueError.

- content (dict[str, Any])
    - Populated by Container.__init__. HTMLContainer expects these keys depending on sequence_type:
        - For "list" or "accordion":
            - Required: "items" (Sequence[Renderable]), "anchor_id" (str)
            - Template called: "sequence/list.html" with context (anchor_id, items)
        - For "named_list":
            - Required: "items", "anchor_id"
            - Template: "sequence/named_list.html"
        - For "tabs":
            - Required: "items" (passed to template as tabs), "anchor_id", "nested" (bool)
            - Template: "sequence/tabs.html" with context (tabs, anchor_id, nested)
        - For "select":
            - Required: "items" (passed as tabs), "anchor_id", "nested"
            - Template: "sequence/select.html" with context (tabs, anchor_id, nested)
        - For "sections":
            - Required: "items" (passed as sections), "full_width" (bool)
            - Template: "sequence/sections.html" with context (sections, full_width)
        - For "grid":
            - Required: "items"
            - Template: "sequence/grid.html" with context (items)
        - For "batch_grid":
            - Required: "items", "batch_size" (int)
            - Optional: "titles" (bool; default True used via content.get("titles", True)), "subtitles" (bool; default False via content.get("subtitles", False))
            - Template: "sequence/batch_grid.html" with context (items, batch_size, titles, subtitles)

Notes on content values:
- "items" is expected to be a sequence of child renderable objects (objects that the templates know how to render). HTMLContainer does not validate types and will access content keys directly.
- Missing keys required by a branch will raise KeyError when render() attempts to read them.

## Lifecycle:
Creation:
- HTMLContainer uses Container.__init__. Construct with the Container-style parameters:
    - Required:
        - items: Sequence[Renderable] — stored into content["items"]
        - sequence_type: str — stored on self.sequence_type
    - Optional (examples and typical names):
        - nested: bool = False — stored in content["nested"]
        - name: Optional[str] = None — stored in content["name"]
        - anchor_id: Optional[str] = None — stored in content["anchor_id"]
        - classes: Optional[str] = None — stored in content["classes"]
        - **kwargs: additional metadata merged into content (e.g., batch_size, full_width, titles, subtitles)

Usage:
- Call render() to produce an HTML fragment string. The method:
    1. Looks at self.sequence_type.
    2. Selects the corresponding template via templates.template(template_name) (templates.template delegates to jinja2_env.get_template(template_name)).
    3. Calls the template's render(...) with the specific context derived from content.
    4. Returns whatever the template.render(...) returns (typically a str).

- Multiple render() calls are allowed; render() does not mutate self.

Destruction:
- No cleanup required. HTMLContainer holds simple in-memory state and performs no resource management.

## Method Map:
flowchart LR
    A[render()] --> B{sequence_type}
    B --> C1["list" or "accordion"] --> D1[template("sequence/list.html").render(anchor_id, items)]
    B --> C2["named_list"] --> D2[template("sequence/named_list.html").render(anchor_id, items)]
    B --> C3["tabs"] --> D3[template("sequence/tabs.html").render(tabs=items, anchor_id, nested)]
    B --> C4["select"] --> D4[template("sequence/select.html").render(tabs=items, anchor_id, nested)]
    B --> C5["sections"] --> D5[template("sequence/sections.html").render(sections=items, full_width)]
    B --> C6["grid"] --> D6[template("sequence/grid.html").render(items)]
    B --> C7["batch_grid"] --> D7[template("sequence/batch_grid.html").render(items, batch_size, titles, subtitles)]
    B --> C8[other] --> E[raise ValueError("Template not understood", sequence_type)]

## Returns:
- Typically returns a str: the HTML fragment produced by the Jinja2 template.
- Caveat: if the template engine or the template returns a non-str value (unusual), that value is returned as-is.

## Raises:
- KeyError
    - When a required key for the selected sequence_type is missing from content (e.g., "items", "anchor_id", "nested", "full_width", or "batch_size").
- ValueError
    - When self.sequence_type is not one of the supported tokens. Raised as ValueError("Template not understood", self.sequence_type).
- jinja2 exceptions (propagated)
    - templates.template delegates to jinja2_env.get_template(template_name); this may raise jinja2.exceptions.TemplateNotFound or other template-loading errors.
    - template.render(...) may raise Jinja2 runtime exceptions (TemplateRuntimeError, UndefinedError, etc.). These exceptions propagate unchanged.
- Any exception raised while evaluating child renderables inside templates will also propagate.

## Example:
1. Tabs container:
    - Prepare child renderables (each implements render()):
        tab_items = [tab1, tab2]
    - Instantiate:
        tabs_container = HTMLContainer(items=tab_items, sequence_type="tabs", nested=False, anchor_id="tabs-1")
    - Render:
        html_fragment = tabs_container.render()

2. Batch-grid container (with optional flags):
    - Instantiate:
        batch_container = HTMLContainer(items=grid_items, sequence_type="batch_grid", batch_size=4)
    - Render:
        html = batch_container.render()
    - Notes: If "titles" or "subtitles" are not supplied in content, render() uses titles=True and subtitles=False defaults for the template call.

Implementation notes for integrators:
- To add a new sequence_type, add a new branch mapping sequence_type -> template name and the exact context keys expected by that template.
- Because HTMLContainer delegates to Jinja2 via templates.template(...), ensure the environment registers the referenced template names under the "sequence/" path.

### `src.ydata_profiling.report.presentation.flavours.html.container.HTMLContainer.render` · *method*

## Summary:
Render the container's children into an HTML string by selecting and applying the correct HTML template based on sequence_type; does not modify the container's state.

## Description:
This method is called during the HTML presentation/rendering stage of the report generation pipeline when a concrete Container subclass must produce an HTML fragment for a grouped sequence of child renderables. Typical callers are the report assembly or renderer components that traverse a renderable tree and invoke render() on each node to obtain serialized HTML fragments for inclusion in the final report output.

The logic is separated into its own method because rendering for Container instances depends on a small, discrete decision: choosing the appropriate template for the container's sequence_type and passing the relevant content keys into that template. Encapsulating this mapping keeps template selection and argument preparation localized (improving readability and making it straightforward to extend supported sequence types).

## Args:
    None

## Returns:
    str: The rendered HTML fragment produced by the selected template's render method. The returned string is typically a small HTML snippet (e.g., a list, tab panel, grid, or section block), ready to be concatenated into a larger HTML document.

    Edge cases:
    - If the underlying template engine returns a non-string (unlikely with standard templating engines used here), that value will be returned as-is; callers should expect and generally handle str.
    - If template rendering itself raises an exception, that exception propagates to the caller.

## Raises:
    KeyError:
        - If required keys are missing from self.content for the chosen sequence_type. Examples:
            * Accessing self.content["anchor_id"] or self.content["items"] will raise KeyError if those keys are absent.
            * Accessing self.content["nested"] or self.content["full_width"] or self.content["batch_size"] will raise KeyError when those keys are expected by the selected template branch and are not present.
    ValueError:
        - Always raised when self.sequence_type is not one of the supported tokens:
            ("list", "accordion", "named_list", "tabs", "select", "sections", "grid", "batch_grid").
        - The exception is raised with the tuple ("Template not understood", self.sequence_type) as provided by the implementation.
    Any exception raised by the template engine (for example, rendering-related exceptions) will propagate unchanged.

## State Changes:
    Attributes READ:
        - self.sequence_type
        - self.content (and specific keys read from it):
            * content["items"] (used by list, accordion, named_list, tabs/select, sections, grid, batch_grid)
            * content["anchor_id"] (used by list/accordion, named_list, tabs/select)
            * content["nested"] (used by tabs and select)
            * content["full_width"] (used by sections)
            * content["batch_size"] (used by batch_grid)
            * content.get("titles", True) (optional; used by batch_grid)
            * content.get("subtitles", False) (optional; used by batch_grid)
    Attributes WRITTEN:
        - None. This method does not mutate self or any external container state.

## Constraints:
    Preconditions:
        - self.sequence_type must be a str identifying one of the supported sequence templates.
        - self.content must be a mapping (dict-like) containing the keys required for the selected sequence_type:
            * At minimum, most branches require content["items"].
            * Some branches require content["anchor_id"], content["nested"], content["full_width"], or content["batch_size"] depending on sequence_type.
        - The values in content["items"] are expected to be renderable child objects (typically objects providing their own render() that the templates expect), though no runtime type enforcement is performed here.
    Postconditions:
        - If no exception is raised, the method returns a string representing the rendered HTML for this container.
        - No attributes on self are modified.

## Side Effects:
    - Calls into the templating subsystem via templates.template(...).render(...). This is the only external interaction; the method itself does not perform I/O (file, network) directly.
    - Any side effects or resource usage originating from the template engine are possible and will propagate (for example, template engine-specific logging, or exceptions).

