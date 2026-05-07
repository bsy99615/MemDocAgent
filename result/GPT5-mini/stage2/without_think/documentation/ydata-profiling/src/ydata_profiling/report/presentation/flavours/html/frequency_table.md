# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable` · *class*

## Summary:
Renders a FrequencyTable presentation object's in-memory content into HTML using the "frequency_table.html" Jinja2 template. Produces either a single table fragment or a concatenation of multiple fragments depending on the shape of the content.

## Description:
HTMLFrequencyTable is a concrete HTML presentation wrapper that knows how to take the presentation state (self.content) prepared by a FrequencyTable-like object and convert it into an HTML string by invoking the "frequency_table.html" template from the HTML flavour templates module.

Typical scenarios for instantiation and use:
- Use when you have prepared frequency-table data (counts, value labels, percentages, or preformatted row structures) that you want to render into HTML fragments for inclusion in an HTML report.
- Higher-level report-rendering code or a report assembler will create or receive instances whose self.content has been filled with the required keys, and then call instance.render() to get the HTML markup.

Motivation and responsibility boundary:
- This class isolates template invocation and HTML assembly logic from data-preparation logic. It does not compute frequencies or prepare rows — it only inspects self.content and renders the appropriate template calls. It expects self.content to conform to a small contract (documented below).

## State:
This class relies on inherited instance state; the only required public attribute it reads is:

- content: dict[str, Any]
  - Required keys:
    - "rows": Sequence
      - Type: indexable, non-empty sequence (e.g., list, tuple)
      - Semantics:
        - If rows[0] is a list (or list-like sequence), then self.content["rows"] is treated as a sequence-of-tables: each element is itself a list of table rows. The renderer will render each sub-list separately and concatenate the results.
        - Otherwise, rows is treated as a single table's row collection and the template is called once with the entire content dict.
      - Invariants:
        - Must be present in content.
        - Must be non-empty (accessing rows[0] is required).
  - Optional additional keys:
    - Any other keys present in self.content are forwarded as keyword arguments into the template.render(...) call. Common examples (not enforced) might be "title", "variable_name", "count", "summary", etc. The template must accept whatever keys are provided.
  - Mutability and side-effects:
    - The renderer creates a shallow copy of the content when it needs to remove the "rows" key for per-subtable rendering, but it never mutates self.content itself.

Class invariants (that should hold across method calls):
- self.content exists and is a mapping that contains a non-empty "rows" sequence.
- The template "frequency_table.html" is available via templates.template(template_name) and supports rendering with the provided keys.

## Lifecycle:
Creation:
- Instantiate using the same constructor contract as the FrequencyTable base class (not included here). The only post-construction requirement before calling render() is that instance.content must be set to a mapping containing a non-empty "rows" key.

Usage:
- Call instance.render() to receive an HTML string.
- Behavior on call:
  - If content["rows"][0] is a list-like object:
    - A shallow copy of content is made, the "rows" key is removed from the copy, and for each element sub_rows in content["rows"]:
      - templates.template("frequency_table.html").render(rows=sub_rows, idx=current_index, **kwargs)
      - The returned string for each subtable is concatenated in index order; the final concatenated string is returned.
  - Otherwise:
    - templates.template("frequency_table.html").render(**content, idx=0) is called and its return value is returned directly.
- No required call ordering beyond setting content before render().

Destruction / cleanup:
- No special cleanup or close() is required. template.render(...) may perform templating engine operations internally, but HTMLFrequencyTable itself holds no external resources.

## Method Map:
flowchart LR
    A[create instance] --> B[set instance.content]
    B --> C{rows[0] is list?}
    C -->|yes| D[copy content; del copy['rows']]
    D --> E[for idx, rows in enumerate(content['rows']):]
    E --> F[render template with rows=rows, idx=idx, **copy]
    F --> G[concat rendered strings]
    C -->|no| H[render template with **content, idx=0]
    H --> I[return string]
    G --> I

(Above graph shows the typical invocation flow from creation to final returned HTML string. The only public method is render().)

## Raises:
The method may raise exceptions under these conditions — the method does not catch or translate these exceptions:

- KeyError
  - Trigger: self.content does not contain the "rows" key.
- IndexError
  - Trigger: self.content["rows"] is an empty sequence (accessing rows[0]).
- Any exception raised by templates.template("frequency_table.html") or its render(...) method:
  - Examples: template-not-found errors from the templating environment, TemplateSyntaxError, TypeError from unexpected keyword arguments, or runtime errors within template rendering. These are propagated to the caller.

## Example (usage pattern, described):
1. Ensure an instance of HTMLFrequencyTable (or a subclass) has been created.
2. Populate instance.content with a mapping that includes "rows":
   - Single-table example content:
     - content = {
         "rows": [ ["value1", 10, "10%"], ["value2", 5, "5%"] ],
         "title": "Top values",
         "variable_name": "my_var"
       }
     - Calling render() will call templates.template("frequency_table.html").render(rows=content["rows"], title="Top values", variable_name="my_var", idx=0) and return the resulting HTML string.
   - Multi-table example content:
     - content = {
         "rows": [
           [ ["a", 3], ["b", 2] ],
           [ ["x", 7], ["y", 1] ]
         ],
         "title": "Values per bin"
       }
     - Calling render() will:
       - Make a shallow copy of content and remove "rows" from the copy.
       - For idx=0 and idx=1 call template.render(rows=sub_rows, idx=idx, **copy) where sub_rows is the first and second inner list respectively.
       - Concatenate the two returned HTML fragments (in order) and return the combined string.

Notes:
- The exact keys expected by the "frequency_table.html" template are template-specific. Ensure that content includes the keys the template expects (rows always, plus any template-specific context keys).
- Because the implementation checks only the type/shape of rows[0], any sequence where the first element is list-like will be interpreted as a sequence of subtables. If you want a single table whose first row happens to be a list (common), use the single-table path by ensuring the overall content is structured accordingly (i.e., do not wrap multiple tables in the outer rows list unless you intend multiple fragments).

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable.render` · *method*

## Summary:
Render the object's frequency-table content into HTML and return the resulting HTML string. When the content represents multiple frequency tables (rows is a list of lists), this produces a concatenation of rendered table fragments; otherwise it renders a single table fragment.

## Description:
This method is the HTML renderer for a FrequencyTable presentation object. It inspects self.content["rows"] to decide whether to render one or multiple frequency-table fragments using the "frequency_table.html" template from the HTML flavour templates module.

Known callers and lifecycle:
- No specific caller is referenced inside this module. In the report generation pipeline, this method is intended to be invoked by a higher-level HTML report renderer or by code that assembles presentation objects into a final report string. It is the step that converts the in-memory frequency-table representation into HTML markup.

Why this is a separate method:
- The conditional rendering logic (single table vs. multiple tables) and the interaction with the template system are a distinct responsibility; separating it keeps template invocation and HTML string assembly isolated from data-preparation logic in other parts of the FrequencyTable class or the report pipeline.

## Args:
- None. Uses instance state (self.content) exclusively.

## Returns:
- str: The rendered HTML string.
  - If self.content["rows"][0] is a list, returns the concatenation of template renderings for each sublist in self.content["rows"] (each with its own idx).
  - Otherwise returns a single template rendering call with idx=0 and all keys from self.content passed into the template renderer.
  - Edge cases:
    - If there are multiple sub-tables, the order in the returned string matches enumerate(self.content["rows"]) order.
    - If the template rendering produces an empty string, that empty string is returned (or concatenated) as-is.

## Raises:
- KeyError: If self.content does not contain the key "rows".
- IndexError: If self.content["rows"] is an empty sequence (accessing [0] will raise IndexError).
- Any exception raised by templates.template("frequency_table.html").render(...) will propagate unchanged (e.g., template lookup errors, template rendering exceptions). The method does not catch these exceptions.

## State Changes:
- Attributes READ:
    - self.content (reads the mapping and specifically self.content["rows"] and other keys present in self.content when passed through to the template)
- Attributes WRITTEN:
    - None. The method does not modify any attribute on self. A shallow copy of self.content is created locally when needed but not stored back on self.

## Constraints:
- Preconditions:
    - self.content must be a mapping (e.g., dict-like) containing the key "rows".
    - self.content["rows"] must be an indexable sequence (supporting [0]) and non-empty.
    - If self.content["rows"][0] is a list, then self.content["rows"] is treated as a sequence of row-lists (list of lists). Each element will be passed as the rows argument into the template renderer.
    - The template "frequency_table.html" must be available via templates.template("frequency_table.html") and its render(...) method must accept the provided keyword arguments.
- Postconditions:
    - No mutation of self or self.content has occurred.
    - A str containing the rendered HTML (possibly empty) is returned.
    - If preconditions are violated, an exception (KeyError/IndexError or template-related exception) is raised before returning.

## Side Effects:
- Calls into the template system: templates.template("frequency_table.html").render(...). This may perform operations internal to the templating engine, but this method itself does not perform I/O (file, network) directly.
- No mutation of objects external to self is performed by this method.

