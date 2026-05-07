# `frequency_table_small.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table_small.HTMLFrequencyTableSmall` · *class*

## Summary:
HTMLFrequencyTableSmall is an HTML renderer for the FrequencyTableSmall presentation model; it converts the stored frequency-table content into an HTML string by rendering the "frequency_table_small.html" Jinja2 template once per row-group.

## Description:
This class is a concrete renderer for the FrequencyTableSmall presentation item. It should be instantiated when the presentation pipeline needs an HTML fragment for a compact frequency table (for example, top-n values and counts for a dataset column). Typical callers are the report presentation pipeline or template-driven HTML report generators that choose this concrete subclass to produce final HTML output.

Motivation and responsibility boundaries:
- Responsibility: read the presentation model stored in self.content and produce a single HTML string suitable for inclusion in an HTML report.
- Not responsible for: validating or transforming the semantic structure of the rows, opening or configuring the Jinja2 environment, or writing the output to disk or network — it only returns the HTML string produced by the template renderer.
- It is intentionally thin: it delegates layout and escaping to the "frequency_table_small.html" Jinja2 template and only orchestrates repeated rendering for each row-group.

Known inputs:
- Relies on the inherited contract from FrequencyTableSmall: the instance has an attribute content which is a dict that must include at least the key "rows" (and typically "redact").
- Uses templates.template("frequency_table_small.html") to obtain a Jinja2 template object and calls its render(...) method.

## State:
Attributes (inherited or used):
- content (dict)
  - Type: dict
  - Required keys:
    - "rows": Iterable[Any]
      - Semantics for this renderer: treated as an iterable of row-groups. Each element yielded by iterating content["rows"] is passed to the template as the template variable rows. A row-group itself is application-dependent (commonly a list of (value, count) pairs or dicts with value/count/percent).
      - Constraint: content["rows"] must be iterable (supports enumeration). If it is not present or not iterable, render() will fail.
    - "redact": bool (commonly present)
      - Passed through to the template as part of kwargs (because the renderer forwards all content keys except "rows" to the template). If present, the template can use this to hide or mask sensitive values.
  - Other keys:
    - Any other keys present in content are forwarded to the template as template variables (for example, a display name, CSS classes, or flags). The renderer creates a shallow copy of content, removes the "rows" entry, and passes the remainder as keyword arguments to template.render(...).

Class invariants:
- Instances must satisfy the FrequencyTableSmall contract: item_type == "frequency_table_small" and content is a dict with at least the "rows" key.
- Rendering does not mutate the instance's content (the implementation uses a copy before removing "rows").

## Lifecycle:
Creation:
- This class does not define its own __init__; it inherits initialization from FrequencyTableSmall (which sets item_type and content).
- Required to create an instance: pass rows and redact as arguments according to FrequencyTableSmall constructor semantics (e.g., HTMLFrequencyTableSmall(rows=..., redact=...)).
Usage:
1. Instantiate a FrequencyTableSmall-derived object (rows and redact required).
2. Call render() on the HTMLFrequencyTableSmall instance to obtain the HTML fragment (a str).
3. Include the returned HTML string in the larger HTML report template or write it to the desired destination.
- Typical sequencing: render() may be called zero or more times; each call re-renders the current content and returns a fresh HTML string based on the then-current content.
Destruction:
- No explicit cleanup is required. The renderer holds no external resources and may be garbage-collected normally.

## Method Map:
graph LR
    A[render()] --> B[Shallow copy self.content to kwargs]
    B --> C[Delete kwargs["rows"]]
    A --> D[Iterate enumerate(self.content["rows"])]
    D --> E[For each idx, rows: templates.template("frequency_table_small.html").render(rows=rows, idx=idx, **kwargs)]
    E --> F[Concatenate rendered fragment into html variable]
    F --> G[Return html (str)]

## Raises:
- KeyError
  - Trigger: If self.content does not contain the key "rows", the implementation accesses self.content["rows"] and Python raises KeyError.
- TypeError
  - Trigger: If self.content is not a mapping-like object with .copy() or its "rows" value is not iterable, Python will raise a TypeError (for example, trying to enumerate a non-iterable).
- jinja2.exceptions.TemplateNotFound
  - Trigger: templates.template("frequency_table_small.html") delegates to the Jinja2 environment (get_template). If the named template is not available, Jinja2 raises TemplateNotFound.
- jinja2.exceptions.TemplateSyntaxError, jinja2.exceptions.UndefinedError, etc.
  - Trigger: During template.render(...), Jinja2 may raise its standard rendering errors if the template contains syntax errors or references undefined variables in a strict environment.
Notes:
- The class itself does not catch these exceptions; callers should handle them if they need resilient rendering.

## Example:
- Typical content shape consumed by this renderer:
  - content["rows"] = [
      [("A", 42), ("B", 7)],         # first row-group
      [("C", 3), ("D", 2), ("E",1)]  # second row-group
    ]
  - content["redact"] = False
  - Additional keys such as "name" or "classes" may also be present and will be forwarded to the template.
- Example usage (conceptual):
  1) Instantiate (using inherited constructor semantics):
     instance = HTMLFrequencyTableSmall(rows=[ [("A",42),("B",7)], [("C",3)] ], redact=False)
  2) Render HTML:
     html_fragment = instance.render()  # returns a concatenated string with each group rendered by the Jinja2 template
  3) Integrate:
     # Insert html_fragment into the page body or a larger template.
- Behavior to expect:
  - The returned html_fragment is the concatenation (in order) of template.render(...) outputs for each group in content["rows"].
  - The template receives these template variables:
      - rows: the current row-group (the element from content["rows"])
      - idx: integer index of the current row-group (0-based)
      - plus all other key/value pairs from content except the "rows" key (for example redact=True/False)

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table_small.HTMLFrequencyTableSmall.render` · *method*

## Summary:
Render the small frequency-table content into an HTML fragment by applying the "frequency_table_small.html" Jinja2 template to each row group and concatenating the results; does not modify the object's stored content.

## Description:
This method is the HTML-flavoured renderer for a FrequencyTableSmall presentation item. It is invoked by the presentation/report pipeline when converting presentation-model items into an HTML output (the stage that turns backend-agnostic item data into HTML fragments). Typical callers are the report/presentation orchestrator that iterates over ItemRenderer instances and calls their render() implementations to produce final report fragments.

Why this is a separate method:
- Rendering HTML involves template lookup and template rendering logic that is specific to the HTML flavour; keeping it in a dedicated render method keeps presentation concerns separated from the data model (FrequencyTableSmall).
- The method encapsulates the logic for preparing template arguments and iterating over multiple "row groups" so it can be reused wherever a FrequencyTableSmall must be converted to HTML.

Behavior summary:
- Make a shallow copy of self.content and remove the "rows" key from that copy so the "rows" are passed as a positional/template argument rather than duplicated in kwargs.
- For each element in self.content["rows"], render the Jinja2 template "frequency_table_small.html" with:
    - rows: the current rows element
    - idx: the zero-based index of the current iteration
    - plus any other keys present in the content dict (e.g., "redact", and forwarded kwargs like name, anchor_id, classes) passed as template keyword arguments
- Concatenate the rendered strings for all iterations and return the final HTML string.

## Args:
None (method is invoked on self)

## Returns:
str — The concatenated HTML fragment resulting from rendering "frequency_table_small.html" once per entry in self.content["rows"].
- If self.content["rows"] is an empty iterable, returns an empty string.
- If rows contains non-string-producing template inputs, template.render may convert them to strings according to the template logic.

## Raises:
- KeyError: If "rows" is not present in self.content (the method calls del kwargs["rows"] and iterates over self.content["rows"]; either operation will raise KeyError).
- TypeError: If self.content["rows"] exists but is not iterable, enumerate(self.content["rows"]) will raise TypeError.
- jinja2.exceptions.TemplateNotFound (or the equivalent raised by the template lookup): If the template "frequency_table_small.html" cannot be found by the templates.template helper.
- jinja2.exceptions.TemplateError or other rendering exceptions: If the template rendering fails (e.g., during evaluation of template expressions or filters), those template-rendering exceptions propagate.

(Note: The FrequencyTableSmall base class documents the invariant that content must contain "rows" and "redact", so in correct usage KeyError should not occur. The above raises list documents real runtime failure modes if those invariants are violated or template resources are missing.)

## State Changes:
Attributes READ:
- self.content — the method reads this attribute (shallow copy then indexed access to "rows" and other keys such as "redact" if present)

Attributes WRITTEN:
- None — the method does not modify any self.<attr> attributes. It makes a local shallow copy of self.content and mutates the copy (deleting the "rows" key) but leaves self.content unchanged.

## Constraints:
Preconditions:
- self.content must be a dict-like object containing at least the key "rows".
- self.content["rows"] must be an iterable (commonly a list); the items in this iterable are the per-iteration "rows" objects expected by the template.
- Templates must be available to the templates.template helper (the Jinja2 environment must have "frequency_table_small.html" loaded).

Postconditions:
- After return, self.content is unchanged.
- The returned value is a string produced by concatenating the results of template.render(...) for each element in self.content["rows"].

## Side Effects:
- Calls templates.template("frequency_table_small.html") which delegates to the shared Jinja2 environment to locate/load a template (this may access template loaders/resources, but does not mutate self).
- Calls template.render(...), which executes template code; templates may run filters or functions that have side effects if the template environment is configured with such callables (these are external to this method).
- No I/O (files, network) is performed by this method itself, but the underlying Jinja2 environment may perform I/O when loading templates depending on its loader configuration; any such I/O is performed by the templates/template retrieval and is not performed on self or by this method directly.

