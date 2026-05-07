# `root.py`

## `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot` · *class*

## Summary:
HTMLRoot is a concrete Root renderer that produces an HTML report string by extracting navigation entries from the report body and rendering the "report.html" Jinja2 template.

## Description:
HTMLRoot implements Root.render for the HTML flavour. It expects to be used when you already have a fully assembled Root instance (name, body, footer, style). Its sole responsibility is to transform the Root content mapping into a rendered HTML string by:

- reading the list of sections from the report body, building a navigation list (pairs of section name and anchor),
- obtaining the "report.html" template via the templates.template helper, and
- calling the template's render method with the report content and navigation items.

Do not use HTMLRoot to construct body/footer/style objects — these must be prepared beforehand and conform to the Renderable contract (see Root).

## State:
HTMLRoot does not add new attributes; it relies on the inherited Root state. Relevant expectations:

- item_type (str)
  - Value: "report" (set by Root/ItemRenderer).
  - Invariant: remains "report".

- content (dict[str, Any])
  - Required keys set by Root.__init__:
    - "body": Renderable — must expose a .content mapping.
    - "footer": Renderable
    - "style": Style
    - "name": str
  - HTMLRoot-specific expectations about content["body"]:
    - content["body"].content must be a mapping that contains key "items".
    - content["body"].content["items"] must be an iterable of section-like objects.
    - Each section-like object must provide:
      - name (str)
      - anchor_id (str or None)
  - Mutability note: content is the same dict object created by Root.__init__; HTMLRoot reads from it at render time.

- name, anchor_id, classes
  - Available in content["name"], content.get("anchor_id"), content.get("classes") as provided to Root.

## Lifecycle:
Creation:
- Use the inherited Root constructor:
  - HTMLRoot(name: str, body: Renderable, footer: Renderable, style: Style, **kwargs)
  - Required parameters: name, body, footer, style.
  - Optional **kwargs (for example anchor_id, classes) are forwarded by Root into the content mapping.

Usage (rendering steps and sequencing):
1. Ensure body and footer are concrete Renderable instances and that body.content["items"] exists and is an iterable of section-like objects (each with .name and .anchor_id).
2. Instantiate via the Root constructor (no separate HTMLRoot.__init__).
3. Call render(**kwargs):
   - Signature: render(self, **kwargs) -> str
   - Behavior (in order):
     a. Build nav_items as a list of pairs (section.name, section.anchor_id) for each section in self.content["body"].content["items"].
     b. Call templates.template("report.html") to obtain a jinja2.Template.
     c. Call template.render with the merged context:
        - All key/value pairs from self.content are expanded into the template context.
        - A keyword nav_items is provided (the list from step a).
        - Any keys provided in **kwargs are expanded last and therefore take precedence: if kwargs contains a key that is also present in self.content or if it contains "nav_items", the value from kwargs will override the earlier value passed from content or the nav_items constructed by HTMLRoot.
     d. Return the string result produced by template.render.
4. No special teardown is required by HTMLRoot itself.

Destruction:
- HTMLRoot does not manage external resources and implements no explicit cleanup. Manage cleanup for underlying components (if any) separately.

## Method Map:
flowchart TD
    render[render(self, **kwargs) -> str]
    render --> build_nav[Build nav_items: iterate self.content["body"].content["items"]]
    build_nav --> get_template[Call templates.template("report.html") -> jinja2.Template]
    get_template --> template_render[Call template.render(**self.content, nav_items=nav_items, **kwargs)]
    template_render --> return_str[Return rendered HTML string]

## Raises:
HTMLRoot does not catch exceptions; errors come from data access or from Jinja2. Possible exceptions and their trigger conditions:

- KeyError
  - Trigger: self.content does not contain "body", or content["body"].content does not contain "items". The code performs direct indexing via self.content["body"].content["items"].

- AttributeError
  - Trigger: content["body"] is not an object with a .content mapping, or a section item does not provide .name or .anchor_id.

- TypeError
  - Trigger: content["body"].content["items"] is not iterable (e.g., None or a non-iterable), or kwargs contain improperly typed values that the template expects to iterate or attribute-access.

- jinja2.exceptions.TemplateNotFound
  - Trigger: templates.template("report.html") delegates to the configured Jinja2 environment's get_template; if "report.html" is not present, get_template raises TemplateNotFound.

- jinja2.exceptions.TemplateError (and its subclasses)
  - Trigger: template.render fails due to template syntax errors or runtime errors during rendering.

Notes:
- Because HTMLRoot forwards self.content and **kwargs into template.render and because **kwargs is expanded last, values in kwargs will override values from content (including the constructed nav_items) if the same key is provided.

## Example (usage described in prose):
- Prepare section-like objects that expose .name and .anchor_id, put them into the report body at body.content["items"] (an iterable).
- Prepare footer and style objects and call the Root constructor to create the report container (HTMLRoot uses the Root constructor; supply name, body, footer, style).
- Call html = html_root.render() to receive the rendered HTML string.
- If you want to inject or override template context variables at render time, pass them as keyword arguments to render; note that these kwargs override the values from the internal content mapping and the autogenerated nav_items when keys collide.

## Implementation guidance (for reimplementers):
- Exactly perform these steps in render:
  1. Iterate the items in self.content["body"].content["items"], collecting for each section its name and anchor_id into a list of pairs.
  2. Obtain the template by calling templates.template with the literal "report.html".
  3. Call the template object's render method, expanding the content mapping, providing nav_items as a keyword, and finally expanding **kwargs so that callers can override context values if needed.
- Avoid swallowing exceptions; let KeyError/AttributeError/TypeError and Jinja2 exceptions propagate so calling code can detect malformed content or template issues.
- Document the exact expected shape of body.content["items"] to help callers supply correctly-formed data and prevent runtime attribute errors.

### `src.ydata_profiling.report.presentation.flavours.html.root.HTMLRoot.render` · *method*

## Summary:
Renders the report as an HTML string by collecting navigation items from the report body and invoking the "report.html" Jinja2 template; does not mutate the HTMLRoot instance.

## Description:
This method is the final step in producing an HTML representation of a report. It is called once a Root-derived report object has been fully assembled (body, footer, style, name). Known callers and typical context:
- Presentation layer code that produces the final serialized report (e.g., report builders, presentation factories, or any code that takes a Root instance and needs an HTML string).
- The lifecycle stage is the final rendering/serialization step after the report's body and footer Renderable components have been created and attached to the Root.

Why this is a dedicated method:
- It centralizes the HTML-specific rendering logic for a Root into one place (template selection, nav item extraction, and template invocation).
- Keeping templating in a small, well-defined method separates presentation concerns from data assembly (done by Root and its callers) and allows subclasses/variants to override render behavior if necessary.

## Args:
    **kwargs: Arbitrary keyword arguments forwarded to the Jinja2 Template.render() call.
        - Allowed values: any serializable objects expected by the Jinja2 template.
        - Caution: If any key in kwargs duplicates a key already present in self.content or the explicit nav_items keyword, Python will raise a TypeError for multiple values of the same keyword.

## Returns:
    str: The rendered HTML produced by the "report.html" template.
        - Normal case: a non-empty HTML string representing the report.
        - Edge cases:
            - Empty string: possible if the template and provided context produce no output.
            - The method does not return None.

## Raises:
    KeyError:
        - If self.content does not contain the "body" key.
        - If self.content["body"].content does not contain the "items" key.
    AttributeError:
        - If self.content["body"] does not expose a .content mapping.
        - If an item in self.content["body"].content["items"] lacks .name or .anchor_id attributes.
    TypeError:
        - If kwargs contains a key that duplicates an already-provided keyword (either a key from self.content or the explicit nav_items), Python will raise a TypeError: multiple values for keyword argument.
        - If assignment/calls within the Jinja2 environment raise TypeErrors.
    jinja2.exceptions.TemplateNotFound:
        - If the template loader cannot locate "report.html" (raised by templates.template()).
    jinja2.exceptions.TemplateError (or subclasses, e.g., UndefinedError):
        - Any error raised during template rendering (syntax, undefined variables, filters, etc.) are propagated from template.render().

## State Changes:
Attributes READ:
    - self.content
    - self.content["body"]
    - self.content["body"].content
    - self.content["body"].content["items"]
    - attributes of each section item: .name and .anchor_id

Attributes WRITTEN:
    - None. This method does not modify self or nested objects; it only reads state and produces a string.

## Constraints:
Preconditions:
    - self.content must be a mapping containing at least the key "body".
    - self.content["body"] must expose a .content mapping that contains an "items" iterable.
    - Each element in self.content["body"].content["items"] must be an object with .name and .anchor_id attributes accessible for read.
    - The Jinja2 environment (templates.template) must be configured and able to load "report.html".

Postconditions:
    - Returns a str containing the HTML output produced by rendering "report.html" with the context derived from self.content plus nav_items and any kwargs.
    - self.content and nested objects remain unmodified.

## Side Effects:
    - May trigger template loading (I/O) when templates.template("report.html") obtains the template from the Jinja2 environment; actual I/O depends on the template loader configuration (filesystem, package loader, etc.).
    - May raise template-related exceptions (see Raises) which propagate to the caller.
    - No direct I/O (files, network) is performed by this method itself beyond what the Jinja2 environment may perform during template retrieval/rendering.

