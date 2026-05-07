# `correlation_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable` · *class*

## Summary:
A concrete renderer for a correlation-table item that converts the stored pandas DataFrame correlation matrix into an HTML fragment using pandas.DataFrame.to_html and a Jinja2 template.

## Description:
HTMLCorrelationTable is a concrete subclass of CorrelationTable that implements the render() method to produce an HTML representation of a correlation matrix. Instantiate this class when you have an item containing a correlation matrix (a pandas DataFrame) that must be rendered into HTML for inclusion in an HTML report. Typical callers are report builders or presentation dispatchers that select an HTML flavour renderer for items with item_type == "correlation_table".

This class exists to separate the rendering concern (HTML generation) from the data/contract concern (CorrelationTable). CorrelationTable defines the expected content shape; HTMLCorrelationTable focuses solely on producing the final HTML string using:
- pandas.DataFrame.to_html(...) on the content["correlation_matrix"]
- a Jinja2 template fetched via templates.template("correlation_table.html") and rendered with the content dictionary plus the generated HTML fragment.

Responsibility boundary:
- HTMLCorrelationTable: convert content["correlation_matrix"] -> HTML string wrapped by the "correlation_table.html" template.
- CorrelationTable (base): supply/validate the content contract (item_type and presence of "correlation_matrix"); HTMLCorrelationTable does not re-declare the content contract.

## State:
(HTMLCorrelationTable inherits state from CorrelationTable and its parents. It introduces no new instance attributes.)

- name
  - Type: str
  - Description: Optional human-readable name forwarded to parent constructors.
  - Constraint: No validation performed here; supplied by caller.

- item_type
  - Type: str
  - Value: "correlation_table"
  - Invariant: Should remain the literal "correlation_table" after construction (set by base class).

- content
  - Type: dict
  - Required shape: {"correlation_matrix": pandas.DataFrame}
  - Invariant: content contains the correlation matrix under the key "correlation_matrix". HTMLCorrelationTable expects a pandas DataFrame-like object at that key with a to_html(method) that returns a string.

- anchor_id, classes (inherited, optional)
  - Type: Optional[str]
  - Purpose: Presentation metadata forwarded from callers via kwargs.
  - Constraint: May be None or any string; not validated by this class.

Class invariants:
- item_type == "correlation_table"
- "correlation_matrix" key exists in content and is intended to be a pandas.DataFrame or dataframe-like object with a to_html method.

## Lifecycle:
Creation:
- Instantiate by calling the inherited constructor from CorrelationTable (no __init__ override in this class).
- Required parameters (inherited):
  - name: str
  - correlation_matrix: pandas.DataFrame (passed into content under "correlation_matrix")
- Optional parameters:
  - anchor_id, classes, and other kwargs supported by ancestor constructors.
- Example instantiation pattern (described): Create a pandas DataFrame representing the correlation matrix and pass it along with a name to the CorrelationTable constructor that HTMLCorrelationTable inherits.

Usage (typical method sequence):
1. Construct the item (HTMLCorrelationTable(name, correlation_matrix, **kwargs)).
2. Call render() to obtain the HTML string. No other methods must be called first; render() is self-contained.
3. Insert the returned HTML string into the larger report output (for example, writing into an HTML file or combining with other rendered fragments).

Destruction / Cleanup:
- No explicit cleanup or context-manager support. The class holds references to the provided DataFrame and template objects only for the duration of the instance; rely on Python GC for cleanup.

## Method Map:
graph LR
    A[render()] --> B[lookup: self.content["correlation_matrix"]]
    B --> C[pandas.DataFrame.to_html(classes="correlation-table table table-striped", float_format="{:.3f}".format)]
    C --> D[correlation_matrix_html (str)]
    D --> E[templates.template("correlation_table.html")]
    E --> F[Jinja2 Template.render(**self.content, correlation_matrix_html=correlation_matrix_html)]
    F --> G[returns HTML string]

(Flow: render reads the DataFrame, converts it to an HTML table string with specific classes and float-formatting, injects that string into the "correlation_table.html" Jinja template along with the full content dict, and returns the final rendered HTML.)

## Method: render()
- Signature: render(self) -> str
- Purpose: Produce an HTML string representation of the correlation table item.
- Behavior details:
  1. Read self.content["correlation_matrix"].
  2. Call its to_html(...) method with:
     - classes="correlation-table table table-striped"
     - float_format="{:.3f}".format (ensures numeric cell values are formatted to 3 decimal places)
     The result is assigned to correlation_matrix_html (a str).
  3. Retrieve a Jinja2 template object via templates.template("correlation_table.html").
  4. Call the template's render method with:
     - all key/value pairs from self.content (expanded as keyword arguments)
     - an additional keyword correlation_matrix_html set to the HTML produced earlier
  5. Return the resulting rendered HTML string.
- Return:
  - str: fully rendered HTML for the correlation table section.
- Edge cases and constraints:
  - KeyError: If "correlation_matrix" does not exist in self.content, a KeyError is raised when accessing self.content["correlation_matrix"].
  - AttributeError: If the object at self.content["correlation_matrix"] does not implement to_html (for example, not a pandas DataFrame), attempting to call to_html will raise AttributeError.
  - Formatting: The float_format uses Python's format function to produce 3 decimal places; non-numeric cells will be left untouched by this formatting function as per pandas' to_html behavior.
  - Template errors: The call templates.template("correlation_table.html") may raise template lookup exceptions (e.g., jinja2.exceptions.TemplateNotFound) and Template.render may raise jinja2 exceptions if rendering fails.
  - The method performs no validation beyond relying on the DataFrame's to_html and the template rendering; callers should ensure content has the expected shape.

## Raises:
- KeyError
  - Trigger: content does not include "correlation_matrix" key.
- AttributeError
  - Trigger: content["correlation_matrix"] does not expose a to_html method (not a DataFrame-like object).
- jinja2.exceptions.TemplateNotFound (or other jinja2 exceptions)
  - Trigger: the named template "correlation_table.html" is not available in the Jinja environment returned by templates.template or rendering fails for reasons internal to the template.
- Any exceptions propagated from pandas.DataFrame.to_html (e.g., if internal DataFrame formatting fails).
- Note: The class does not raise custom exceptions itself; it lets underlying library exceptions bubble up.

## Example (how to use this class in practice):
1. Prepare a pandas DataFrame `df` representing the correlation matrix (square DataFrame, rows/columns labeled).
2. Create an HTMLCorrelationTable instance by supplying a name and the correlation matrix (the inherited constructor stores the DataFrame under content["correlation_matrix"]).
3. Call render() on the instance to obtain a string containing:
   - an HTML table for the correlation matrix (with classes "correlation-table table table-striped" and numeric values formatted to 3 decimal places),
   - wrapped by the "correlation_table.html" Jinja2 template with other content keys made available as template context.
4. Insert or write the returned HTML string into your report output.

### `src.ydata_profiling.report.presentation.flavours.html.correlation_table.HTMLCorrelationTable.render` · *method*

## Summary:
Renders the correlation matrix stored in the item's content into an HTML fragment and returns the final HTML for the correlation table template; does not modify the object's state.

## Description:
This method is invoked as the concrete HTML renderer for a CorrelationTable item during the presentation/report rendering pipeline. Typical callers are presentation-layer code or a renderer dispatcher that selects the HTML flavour renderer for items of type "correlation_table" and then calls render() to obtain the HTML snippet to embed in the report. It is executed at the stage where presentation items are converted into their final output format (HTML) immediately before assembling the full report.

The logic is separated into its own method because:
- It is the HTML-flavour-specific implementation of rendering a correlation-table item (keeps flavour logic distinct from the abstract item class).
- It isolates template invocation and HTML post-processing (DataFrame -> HTML string) so other flavours (JSON, image) can implement alternate render() methods without changing shared data structures.

## Args:
    This method takes no arguments (self only). It operates on the instance state:
    - self.content (dict): required to contain the key "correlation_matrix".

## Returns:
    str: A string containing the rendered HTML produced by:
        1. Converting self.content["correlation_matrix"] to an HTML table using its to_html method, and
        2. Rendering the Jinja2 template "correlation_table.html" with the content dict and an added variable correlation_matrix_html containing that table.
    Edge cases:
        - If the correlation matrix is empty, the returned HTML will be the template rendered with whatever HTML pandas.to_html produces for an empty DataFrame.
        - If conversion or template rendering fails, an exception is raised (see Raises).

## Raises:
    - KeyError: If self.content is not a dict or does not contain the "correlation_matrix" key. Trigger: self.content["correlation_matrix"] access.
    - AttributeError: If the object at self.content["correlation_matrix"] does not implement a to_html method (e.g., wrong type).
    - Any exception propagated from pandas.DataFrame.to_html: for example if float_format or data contents cause pandas to raise.
    - jinja2.exceptions.TemplateNotFound: If templates.template("correlation_table.html") cannot locate the template file (raised by the underlying jinja2 environment).
    - jinja2.exceptions.TemplateError (or subclasses): If template.render(...) fails due to template logic or rendering errors.
    Notes:
        - The method does not catch these exceptions; callers should handle them if needed.

## State Changes:
    Attributes READ:
        - self.content (dict)
        - self.content["correlation_matrix"] (expected to be a pandas.DataFrame or object exposing to_html)
    Attributes WRITTEN:
        - None. The method does not modify self or self.content.

## Constraints:
    Preconditions:
        - self.content must be a mapping containing the "correlation_matrix" key.
        - self.content["correlation_matrix"] should implement to_html(formatting args compatible with pandas.DataFrame.to_html) — typically a pandas.DataFrame.
        - The Jinja2 environment accessed via templates.template must be configured and able to load "correlation_table.html".
    Postconditions:
        - A string is returned containing the rendered HTML for the correlation table with a variable correlation_matrix_html injected into the template context.
        - The instance state (self.content and other attributes) is unchanged.

## Side Effects:
    - Reads a template from the configured Jinja2 environment (templates.template), which may perform file I/O when loading templates.
    - Performs no network I/O and does not mutate external objects (except for read-only calls like DataFrame.to_html which do not alter the DataFrame).
    - If the template contains side-effecting constructs (unusual in typical Jinja2 usage), executing template.render(...) could have side effects inside the template execution environment; this is dependent on template content and Jinja2 configuration rather than this method itself.

## Implementation notes (for reimplementation):
    - Convert the correlation matrix to HTML using the DataFrame.to_html API with:
        classes="correlation-table table table-striped"
        float_format="{:.3f}".format
      Capture this result in a local variable correlation_matrix_html (string).
    - Obtain the compiled Jinja2 template named "correlation_table.html" via the project's templates.loader function (templates.template(template_name) returning a jinja2.Template).
    - Call template.render(**self.content, correlation_matrix_html=correlation_matrix_html) and return the resulting string.
    - Do not catch exceptions here; allow callers to observe and handle template or conversion errors.

