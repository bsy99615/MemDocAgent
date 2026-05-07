# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.html.duplicate.to_html` · *function*

## Summary:
Render a pandas DataFrame to an HTML table string with CSS classes for duplicate-row presentation; when the DataFrame is empty, replace table bodies with a single-row message stating no duplicate rows were found.

## Description:
This helper formats the duplicates DataFrame for the HTML presentation layer. It is intended to be called by HTML renderer code that receives a Duplicate item (whose content["duplicate"] holds the DataFrame) and needs a ready-to-embed HTML table fragment.

Known callers and contexts:
- HTML duplicate renderer components in the report presentation pipeline that handle Duplicate items during the final rendering/export stage (e.g., as part of the ProfileReport HTML generation).
- Indirect calls occur when the full report HTML is assembled and the renderer embeds this fragment into the larger report template.

Reason for extraction:
- Keeps HTML-formatting specifics (CSS classes and the empty-table message) centralized for reuse, testability, and consistent styling across duplicate renderers.
- Separates formatting responsibilities from higher-level templating/layout code.

## Args:
    df (pd.DataFrame): DataFrame to render.
        - Required: object must provide .to_html(...), .empty, and .columns with a usable __len__.
        - Typical input: DataFrame containing duplicated rows found by the duplicate-detection stage (or an empty DataFrame when no duplicates exist).

## Returns:
    str: HTML string produced from df.to_html(classes="duplicate table table-striped").
    - If df is not empty: the returned string is the DataFrame's HTML table (with header(s) and body rows) including the specified CSS classes.
    - If df is empty: the returned HTML string is the result of replacing every occurrence of "<tbody>" in the rendered HTML with:
        <tbody><tr><td colspan={len(df.columns) + 1}>Dataset does not contain duplicate rows.</td></tr>
      This injects a single-row message into each table body. The colspan uses len(df.columns) + 1 to account for the default index column rendered by pandas.DataFrame.to_html.

## Raises:
    - This function does not raise new exceptions itself.
    - It may propagate exceptions raised by df.to_html or attribute access on df (for example AttributeError if df lacks .to_html or .columns). Any propagated exception originates from pandas or the provided object rather than from this function.

## Constraints:
Preconditions:
    - df must be a pandas.DataFrame-like object with .to_html, .empty, and .columns attributes.
    - Callers expecting a single-table fragment should be aware that the function performs a global string replacement of "<tbody>", which will affect all table bodies present in df.to_html's output.

Postconditions:
    - The returned value is a str containing an HTML table representation of df with the CSS classes applied.
    - If df.empty is True, every "<tbody>" in the returned HTML will be followed by the inserted single-row message.

## Side Effects:
    - No external I/O or global state mutation.
    - Performs in-memory string operations only; the original DataFrame object is not modified.

## Control Flow:
flowchart TD
    Start[Start: call to_html(df)] --> Render[df.to_html(classes="duplicate table table-striped")]
    Render --> CheckEmpty{df.empty?}
    CheckEmpty -- Yes --> ReplaceAll[Replace all "<tbody>" occurrences with message row (colspan=len(df.columns)+1)]
    CheckEmpty -- No --> SkipReplace[No replacement]
    ReplaceAll --> Return[Return HTML string]
    SkipReplace --> Return

## Examples:
1) Typical usage (non-empty DataFrame)
    - Input: df with duplicated rows
    - Result: returns the HTML table produced by df.to_html(...) with classes "duplicate table table-striped"; the table contains header and duplicate-row entries.

2) Empty DataFrame (no duplicates)
    - Input: df where df.empty == True
    - Result: returns HTML where every table body begins with a single row:
        <tr><td colspan={len(df.columns) + 1}>Dataset does not contain duplicate rows.</td></tr>

Implementation hints:
    - Call df.to_html(classes="duplicate table table-striped") to get the base HTML.
    - Check df.empty and, when true, perform a string replacement of "<tbody>" with the augmented fragment using len(df.columns) + 1 for colspan.
    - Be cautious: because the function replaces all "<tbody>" occurrences, if pandas produces multiple separate table bodies in its output those will all receive the message when df.empty is True.

## `src.ydata_profiling.report.presentation.flavours.html.duplicate.HTMLDuplicate` · *class*

## Summary:
A concrete HTML renderer for Duplicate presentation items that converts the stored duplicates DataFrame into an HTML fragment and injects it into the "duplicate.html" Jinja2 template, returning the final rendered HTML string.

## Description:
HTMLDuplicate is a small renderer subclass whose only responsibility is to produce an HTML representation for a Duplicate item. It is intended to be instantiated in the same way as Duplicate (it inherits the construction and state) and then used by the report generation pipeline or by renderer factories that expect an ItemRenderer returning HTML.

Typical scenarios / callers:
- The report presentation pipeline that constructs a report (for example ProfileReport HTML generation) will create or receive a Duplicate instance (or directly instantiate HTMLDuplicate) to produce the duplicate-rows section of the HTML report.
- Renderer factories or higher-level HTMLReport components that assemble the full report HTML call HTMLDuplicate.render() to obtain a string fragment that will be embedded in the full report template.

Motivation and boundary:
- Responsibility: convert Duplicate.content["duplicate"] (a pandas.DataFrame) into a ready-to-embed HTML fragment (duplicate_html) using the to_html helper and then render the "duplicate.html" template with that fragment and the instance content.
- Boundary: HTMLDuplicate does not detect duplicates (that is the upstream concern), nor does it manage templates; it relies on the global templates.template(...) helper to obtain the Jinja2 template named "duplicate.html".

## State:
Attributes (inherited from Duplicate / ItemRenderer and relevant invariants):

- item_type (str)
  - Type: str
  - Value: the literal "duplicate"
  - Invariant: self.item_type == "duplicate"
  - Source: set by Duplicate base class during construction.

- content (dict)
  - Type: dict
  - Structure: {"duplicate": pandas.DataFrame}
  - Invariant: "duplicate" in self.content and self.content["duplicate"] is the DataFrame supplied at construction.
  - Note: HTMLDuplicate.render() reads self.content["duplicate"]. If this key is missing a KeyError will be raised.

- name (Optional[str])
  - Type: Optional[str]
  - Meaning: human-readable label; inherited from ItemRenderer constructor; may be None.

- anchor_id (Optional[str]) and classes (Optional[str])
  - Type: Optional[str]
  - Meaning: presentation hints forwarded via **kwargs to the parent constructor.

Constructor parameters (inherited):
- name (str)
  - Required positional parameter in Duplicate.__init__ as recorded in the base-class documentation.
- duplicate (pandas.DataFrame)
  - Required; expected pandas.DataFrame (object must provide .to_html, .empty, .columns).
- **kwargs
  - Forwarded to parent ItemRenderer (commonly anchor_id, classes).

Class invariants:
- After construction:
  - self.item_type == "duplicate"
  - isinstance(self.content, dict)
  - "duplicate" in self.content

## Lifecycle:
Creation:
- Instantiate using the Duplicate constructor signature:
  - Example: html_dup = HTMLDuplicate(name="duplicates", duplicate=df)
  - The instance inherits state initialization from Duplicate: item_type and content are set during construction.

Usage:
- Primary method: render() -> str
  - Typical sequence:
    1. Call HTMLDuplicate.render().
    2. The renderer invokes the helper to_html(self.content["duplicate"]) to obtain an HTML table fragment.
    3. It obtains the Jinja2 template via templates.template("duplicate.html") and calls .render(...) passing all content keys plus duplicate_html.
    4. The method returns the final rendered HTML string.
- No special ordering of other methods is required. render() is the only method implemented in this subclass.

Destruction / cleanup:
- There are no external resources or open handles tied to HTMLDuplicate. No explicit cleanup, close(), or context manager support is required.

## Method Map:
flowchart LR
    A[Instantiate HTMLDuplicate (inherited Duplicate.__init__)] --> B[content contains DataFrame at "duplicate"]
    B --> C[call HTMLDuplicate.render()]
    C --> D[to_html(self.content["duplicate"]) -> duplicate_html (str)]
    C --> E[templates.template("duplicate.html") -> jinja2.Template]
    D --> F[template.render(**self.content, duplicate_html=duplicate_html) -> final HTML (str)]
    E --> F
    F --> G[Return HTML string]

## Method: render(self) -> str
Summary:
- Produce the final HTML string for this Duplicate item by formatting the DataFrame to an HTML fragment and rendering it into the "duplicate.html" Jinja2 template.

Behavior details:
- Reads: self.content["duplicate"], expected to be a pandas.DataFrame-like object.
- Calls: to_html(df) helper (responsible for DataFrame -> HTML table conversion, with special handling for empty DataFrames).
- Calls: templates.template("duplicate.html") to retrieve a Jinja2 template and then .render(**self.content, duplicate_html=duplicate_html) to produce the final HTML.
- Returns: a str containing the fully rendered HTML for the duplicate section.

Edge cases and constraints:
- If "duplicate" is not present in self.content, render() raises KeyError.
- If the object at self.content["duplicate"] lacks .to_html or other DataFrame attributes expected by to_html, the underlying call will raise an AttributeError or another pandas-related exception; these are propagated.
- If the "duplicate.html" template is missing from the Jinja2 environment, templates.template(...) will raise the standard Jinja2 exception (e.g., TemplateNotFound), which will propagate.
- The to_html helper handles empty DataFrames by returning an HTML table with a single-row message ("Dataset does not contain duplicate rows") — thus render() will embed that message into the template for empty input DataFrames.

Side effects:
- No mutation of self.content or the DataFrame is performed by render().
- No filesystem or network I/O is performed by render() itself; template retrieval and rendering operate in-memory via the Jinja2 environment.

## Raises:
- During construction (__init__ inherited from Duplicate):
  - Duplicate.__init__ may raise exceptions if ItemRenderer.__init__ validates arguments; Duplicate itself does not perform runtime type checks, so construction normally succeeds even if duplicate is not a DataFrame (errors will surface later).
- During render():
  - KeyError if "duplicate" key is missing from self.content.
  - AttributeError or other exceptions propagated from the to_html helper or from pandas if the supplied object does not implement the expected interface (.to_html, .empty, .columns).
  - jinja2.TemplateNotFound or other Jinja2 rendering exceptions if the "duplicate.html" template is absent or rendering fails.
  - Any exception raised by template.render(...) (for example, if the template expects additional variables that are not present in **self.content) will propagate.

## Example:
- Typical usage (assume df is a pandas.DataFrame and required templates are available in the Jinja2 environment):

    # Create renderer instance (inherited constructor)
    html_dup = HTMLDuplicate(name="duplicates", duplicate=df)

    # Produce HTML for the duplicates section
    html_fragment = html_dup.render()

    # html_fragment is a str that can be embedded in a larger HTML document or written to disk.

Notes:
- If df is empty, the produced fragment will contain a single-row message (as produced by the to_html helper) stating that the dataset does not contain duplicate rows.
- No explicit cleanup is required after calling render(); subsequent calls to render() will repeat the conversion and template rendering.

### `src.ydata_profiling.report.presentation.flavours.html.duplicate.HTMLDuplicate.render` · *method*

## Summary:
Render the stored duplicate-rows DataFrame into an HTML fragment and embed it into the "duplicate.html" Jinja2 template, returning the resulting rendered HTML string. This method does not modify object state.

## Description:
- Known callers and context:
    - Called by the HTML presentation layer of the report-rendering pipeline when a Duplicate item must be converted to its final HTML representation (e.g., as part of assembling a ProfileReport's full HTML output).
    - Renderer factories or presentation orchestrators that iterate over presentation items (item_type == "duplicate") will invoke this method during the final render/export stage.
    - Indirectly invoked when the overall report rendering code (such as an HTMLReport renderer) asks each item renderer for its HTML fragment to include in the full report.
- Lifecycle stage:
    - Invoked at the "final rendering" stage after duplicate-detection and presentation-item construction; the Duplicate instance already holds its DataFrame under content["duplicate"].
- Why this is a separate method:
    - Separates concerns: converts the duplicates DataFrame to an HTML table fragment (via to_html) and delegates full-page layout to a template. Keeping conversion and templating distinct keeps formatting logic reusable and makes template composition explicit and testable.

## Args:
- None (method uses instance state; no parameters accepted).

## Returns:
- str: A fully rendered HTML string produced by rendering the Jinja2 template named "duplicate.html" with:
    - All keys in self.content passed as template variables (via keyword expansion),
    - An additional variable duplicate_html containing the preformatted HTML table fragment created from self.content["duplicate"].
- Edge cases:
    - If the DataFrame is empty, the to_html helper is expected to return an HTML fragment that includes a single-row "no duplicates" message; that behavior is handled by the to_html function called here.
    - The method always returns whatever templates.template(...).render(...) produces; it does not post-process that string.

## Raises:
- KeyError: if self.content does not contain the "duplicate" key (attempting to access self.content["duplicate"] triggers this).
- Any exception propagated from the to_html helper:
    - Examples: AttributeError if the stored object lacks .to_html/.empty/.columns, TypeError/ValueError from pandas.to_html, or other exceptions raised by to_html's internal logic.
- Any exceptions raised by template lookup or rendering:
    - Example: jinja2.TemplateNotFound if "duplicate.html" is not present in the Jinja2 environment, or exceptions raised by jinja2.Template.render if template evaluation fails (e.g., undefined variables used in template code or errors in template expressions).
- No new custom exceptions are raised by this method itself; it simply propagates exceptions from its calls and attribute access.

## State Changes:
- Attributes READ:
    - self.content (the method reads self.content and specifically self.content["duplicate"])
- Attributes WRITTEN:
    - None (the method does not modify any self.<attr> fields)

## Constraints:
- Preconditions:
    - self.content must be a mapping (dict-like) containing the key "duplicate".
    - self.content["duplicate"] must be a pandas.DataFrame (or DataFrame-like object) that satisfies the to_html helper's expectations: it must provide .to_html(...), .empty, and .columns attributes.
    - The Jinja2 environment must include a template named "duplicate.html" retrievable by templates.template("duplicate.html").
- Postconditions:
    - The method returns a string containing the template-rendered HTML for the duplicate section.
    - The instance's state is unchanged (no mutation of self.content or other attributes).
    - No caching or side-effectual registration occurs in this method.

## Side Effects:
- No filesystem or network I/O is performed directly by this method.
- Side effects are limited to:
    - CPU/memory usage for converting the DataFrame to HTML (the to_html helper) and for rendering the Jinja2 template.
    - Potential side-effects inside template rendering (if the Jinja2 environment or template code executes functions with side-effects, those will run during render).
- The original DataFrame object stored at self.content["duplicate"] is not modified by this method.

## Implementation notes (for reimplementation):
- Retrieve df = self.content["duplicate"].
- Call duplicate_html = to_html(df) to obtain the HTML table fragment (the to_html helper handles empty-DataFrame messaging).
- Obtain the template via templates.template("duplicate.html") and call its render method, passing all items from self.content as keyword arguments and an extra keyword duplicate_html with the fragment from to_html.
- Return the string result of template.render(...).
- Ensure exceptions from missing keys, to_html failures, or template rendering are allowed to propagate to the caller (do not catch or swallow them here).

