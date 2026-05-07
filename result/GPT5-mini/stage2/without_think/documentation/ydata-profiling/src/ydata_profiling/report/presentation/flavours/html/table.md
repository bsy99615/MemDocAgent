# `table.py`

## `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable` · *class*

## Summary:
A concrete Table renderer that produces an HTML fragment by applying the "table.html" Jinja2 template to the Table's content mapping.

## Description:
Instantiate HTMLTable when you need a presentation-layer table rendered into HTML for inclusion in an HTML report. HTMLTable is a minimal subclass of Table that implements the render() contract by delegating to the HTML flavour's template loader and the "table.html" Jinja2 template.

Typical usage scenarios:
- A report builder constructs tables (rows + Style + optional name/caption) and uses HTMLTable to render those tables into HTML fragments during the HTML report assembly phase.
- Rendering pipelines that iterate over heterogeneous renderable items call render() on each; HTMLTable implements the HTML-specific render() for table items.

Motivation and responsibility:
- HTMLTable separates the table data model (Table) from HTML-specific rendering logic.
- It enforces a single responsibility: map the Table.content mapping into the "table.html" Jinja2 template and return the produced string. It does not alter content, perform I/O, or manage template configuration.

Known callers / factories:
- Report builders and presentation factories that create Table-like payloads and need HTML output.
- Any code that expects a Table subclass implementing render() to return an HTML string.

## State:
Inherited state from Table that HTMLTable relies on (public attributes):

- item_type (str)
  - Value: "table"
  - Invariant: remains "table" for the lifetime of the instance.

- content (dict-like)
  - Required keys (placed by Table.__init__):
    - "rows": typing.Sequence
        - Semantics: ordered collection of row data. Each row may be a tuple/list/dict depending on template expectations.
        - Constraints: Table accepts any Sequence; HTMLTable expects the structure that "table.html" expects (e.g., iterable of cells).
    - "style": Style
        - Type: ydata_profiling.config.Style (pydantic model)
        - Constraints: Style validation happens at construction of the Style object. Accessing certain Style properties (e.g., color lists) may raise errors if Style is misconfigured.
    - "name": Optional[str] (may be None)
    - "caption": Optional[str] (may be None)

- Other metadata forwarded via **kwargs to ItemRenderer (e.g., anchor_id, classes) are preserved by Table and available to the template through content or metadata (depending on higher-level ItemRenderer implementation).

Class invariants:
- self.item_type == "table"
- "rows", "style", "name", and "caption" keys exist in self.content after construction (values may be None).
- render() returns a str when successful and does not mutate self.content or other instance attributes.

Notes on __init__ parameters (inherited from Table.__init__):
- rows (Sequence): required; no runtime type enforcement beyond being stored in content.
- style (Style): required; must be a validated Style instance to avoid downstream errors inside the template.
- name (Optional[str]): default None.
- caption (Optional[str]): default None.
- Additional kwargs are forwarded upstream; provide them if your rendering pipeline relies on ItemRenderer metadata.

## Lifecycle:
Creation:
- Instantiate like a Table but using the HTMLTable class:
  - Required: rows (Sequence), style (Style)
  - Optional: name (str | None) default None, caption (str | None) default None
  - Additional kwargs (anchor_id, classes) may be forwarded to the parent ItemRenderer.

Usage:
- Typical call sequence:
  1. Create Style and rows data.
  2. Create HTMLTable(rows=..., style=..., name=..., caption=..., **kwargs).
  3. Call html = instance.render() to obtain the HTML fragment (a str).
- There is no required ordering of other methods; only render() is meaningful for output.

Destruction / cleanup:
- HTMLTable does not hold external resources and requires no explicit cleanup. If your template or template globals perform side effects, manage those resources externally.

## Method Map:
graph TD
  A[Create HTMLTable(rows, style, name=None, caption=None, **kwargs)] --> B[Table.__init__ populates content dict]
  B --> C[HTMLTable.render()]
  C --> D[templates.template("table.html")]
  D --> E[jinja2.Template.render(**self.content)]
  E --> F[str: rendered HTML fragment]

(Interpretation: instantiation populates content; render() loads the Jinja2 template named "table.html" via templates.template and calls Template.render with content expanded as keyword arguments; the result is the HTML string returned to the caller.)

## Raises:
The render() implementation may propagate exceptions originating from template lookup or rendering. Callers should be prepared to handle:

- jinja2.exceptions.TemplateNotFound
  - Trigger: the configured Jinja2 environment cannot locate "table.html" by the environment used by templates.template.

- jinja2.exceptions.TemplateError (and subclasses such as UndefinedError)
  - Trigger: runtime errors during template rendering (e.g., referencing undefined variables, filter errors, or other Jinja2 template runtime problems).

- TypeError
  - Trigger: if self.content is not a mapping compatible with Python's keyword expansion (i.e., not dict-like), then calling Template.render(**self.content) will raise TypeError.

- Any exception raised by expressions evaluated inside the template
  - Trigger: method calls, attribute access, or filters executed by the template that raise (e.g., IndexError, AttributeError). These originate from application code reachable from the values in self.content and are not caught/translated by HTMLTable.

Behavioral guarantees:
- On success, render() returns a str and does not mutate instance state.
- On failure, HTMLTable.render() propagates exceptions to the caller; it performs no partial state writes.

## Example:
- Typical usage sketch (no imports shown):
  1) Construct a Style instance (validated by the Style model).
  2) Prepare rows as a sequence (e.g., list of row tuples or dicts).
  3) Instantiate the renderer:
     table = HTMLTable(rows=rows, style=style, name="Summary", caption="Top rows")
  4) Render to HTML:
     html_fragment = table.render()
  5) Include html_fragment into the larger report HTML.

Notes:
- For unit testing, stub templates.template(...) to return a simple object whose render(**kwargs) returns a known string; assert that render() calls Template.render with the expanded content mapping and returns the expected string.
- Ensure the provided rows and style match what "table.html" expects to avoid template runtime errors.

### `src.ydata_profiling.report.presentation.flavours.html.table.HTMLTable.render` · *method*

## Summary:
Renders this table's content into an HTML fragment by applying the "table.html" Jinja2 template to the renderer's content and returns the resulting string. Does not modify object state.

## Description:
This method is the concrete HTML rendering implementation for a table-renderer object. It is invoked during the report presentation phase when HTML output is being assembled — typical callers include report builders or presentation/rendering pipelines that iterate over renderable items and call each item's render() to collect rendered fragments for inclusion in a final HTML report.

Why this is a separate method:
- Keeps formatting concerns (HTML templating) separated from the Table data model and from higher-level composition logic.
- Allows subclasses or alternative flavour renderers to provide different templating or output formats by overriding render().
- Encapsulates the single responsibility of mapping the Table's content dict into the "table.html" template so the rest of the pipeline can treat all renderers uniformly (call render() and get a string).

## Args:
    None

## Returns:
    str: The rendered HTML fragment produced by Jinja2 Template.render. Under normal conditions this is an HTML string representing the table; if the template renders to an empty body the returned string may be empty, but the type is always str when successful.

## Raises:
    jinja2.exceptions.TemplateNotFound:
        - If the "table.html" template cannot be located by the Jinja2 environment used by templates.template(...).
    jinja2.exceptions.TemplateError (including jinja2.exceptions.UndefinedError and other Template runtime errors):
        - If an error occurs while rendering the template (for example, dereferencing a missing attribute in the template, or a filter raising).
    TypeError:
        - If self.content is not a mapping suitable for use with Python's keyword expansion (i.e., not a dict-like object) then the **self.content call will raise TypeError.
    Any exception raised by expressions evaluated inside the template:
        - Exceptions originating from attribute access or method calls on objects passed in self.content may propagate (for example, IndexError from Style.primary_color if the Style instance exposes code that raises when empty). These originate from template evaluation and are not caught here.

## State Changes:
Attributes READ:
    - self.content: read and expanded as keyword arguments into the template render call. Per Table semantics, content is a dict-like mapping that contains at least the keys "rows", "style", "name", and "caption".

Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.content must be a mapping (dict-like) so it can be expanded into keyword arguments for Template.render(**self.content).
    - The Jinja2 environment accessible via templates.template must be configured and able to load "table.html" if rendering is expected to succeed.
    - The values inside self.content (notably the Style object under "style" and the "rows" value) should be shaped in the way the "table.html" template expects (field names, iterable row structure, etc.). Table.__init__ ensures the presence of keys "rows", "style", "name", and "caption", but it does not validate the internal structure of their values.

Postconditions:
    - On successful return, a str containing the rendered HTML fragment is returned.
    - The object's observable state is unchanged (self.content and other attributes remain the same).
    - If rendering fails, an exception is raised and no partial/alternate state is written to self by this method.

## Side Effects:
    - No direct I/O is performed by this method itself: it delegates rendering to Jinja2 and returns the resulting string.
    - Indirect side effects are possible if the Jinja2 environment or template uses custom globals, filters, or functions that perform I/O or mutate external state — such side effects originate inside template evaluation and are not controlled by this method.
    - Exceptions raised during template lookup or render may propagate to callers; the method does not catch or wrap them.

## Implementation Notes (for reimplementation):
    - Use templates.template("table.html") to obtain a Jinja2 Template object (this function delegates to the configured jinja2 environment).
    - Call Template.render(**self.content) and return the result (a str).
    - Do not modify self.content or other attributes in this method.
    - Keep this logic minimal so tests can stub the template function or supply a test template to assert correct call semantics.

