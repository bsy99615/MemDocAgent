# `sample.py`

## `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample` · *class*

## Summary:
HTMLSample is a concrete renderer for Sample items that converts the stored pandas DataFrame sample into an HTML table and injects that HTML into a Jinja2 "sample.html" template, returning the fully rendered HTML string.

## Description:
HTMLSample is a small presentation-class tailored for embedding a data preview (a pandas DataFrame) into an HTML report. It is a concrete subclass of Sample and implements the abstract render() method required by the Sample contract.

When to instantiate:
- Use HTMLSample when you need a report element that renders a DataFrame sample as a styled HTML table inside the project's "sample.html" Jinja2 template.
- Typical callers: report builders, presentation factories, or orchestration code that assemble a full HTML report and that create Sample instances for each data preview.

Why this class exists:
- Separates rendering concerns: Sample holds the semantic payload (DataFrame + caption + metadata) and HTMLSample implements the HTML-specific rendering strategy.
- Keeps template-binding and table-generation logic encapsulated here so other renderers (JSON/plain text) can be implemented independently.

Known collaborators:
- Inherits construction and state layout from ydata_profiling.report.presentation.core.sample.Sample.
- Uses ydata_profiling.report.presentation.flavours.html.templates.template to fetch the Jinja2 template named "sample.html".

## State:
Inherited state (from Sample):
- item_type: str
  - Value: the literal "sample".
  - Invariant: must remain "sample" for the lifetime of the instance.

- content: Dict[str, Any]
  - Required keys set by Sample.__init__:
    - "sample": pandas.DataFrame
      - Type: pandas.DataFrame (the object must support DataFrame.to_html()).
      - Constraint: Sample does not perform defensive type-checking; callers must pass a DataFrame.
      - Invariant: content["sample"] is the same object reference passed to the constructor.
    - "caption": Optional[str]
      - Type: str or None
      - Behavior: May be None; always present as a key after construction.
  - Optional keys (forwarded via **kwargs to the base class):
    - "name": str (required by Sample.__init__)
    - "anchor_id": Optional[str]
    - "classes": Optional[str]

Derived/used state in HTMLSample:
- sample_html: str (local variable inside render())
  - Value: the HTML fragment returned by content["sample"].to_html(classes="sample table table-striped")
  - Not stored on self; computed each render() invocation.

Class invariants (must hold across method calls):
- self.item_type == "sample"
- self.content contains at least the keys "sample" and "caption"
- content["sample"] must be an object exposing a to_html(classes=...) method that returns a str

## Lifecycle:
Creation:
- HTMLSample does not define its own __init__; it relies on Sample.__init__.
- To create an instance, call Sample-style constructor (implemented by Sample):
  - Required arguments:
    - name: str (presentation name / identifier)
    - sample: pandas.DataFrame (the DataFrame to render)
  - Optional:
    - caption: Optional[str] = None
    - **kwargs: forwarded to Renderable/ItemRenderer (commonly anchor_id, classes)
- The constructor will set item_type to "sample" and place {"sample": sample, "caption": caption} into self.content.

Usage:
- Primary method: render() -> str
  - Sequence when render() is called:
    1. Retrieve the DataFrame from self.content["sample"].
    2. Call the DataFrame's to_html method with classes="sample table table-striped" to produce sample_html.
    3. Obtain the Jinja2 template object by calling templates.template("sample.html").
    4. Call the template's render(**self.content, sample_html=sample_html) to produce the final HTML string and return it.
- Typical ordering:
  - Instantiate HTMLSample (via Sample constructor).
  - Call html_string = instance.render().
  - Insert returned html_string into a larger HTML report or write to disk.

Destruction / cleanup:
- HTMLSample does not hold external resources and has no explicit cleanup responsibilities.
- No context-manager or close() method is provided; normal garbage collection applies.

## Method Map:
graph LR
  RenderCall[render()] --> GetSample[access self.content["sample"]]
  GetSample --> ToHtmlCall[call .to_html(classes="sample table table-striped")]
  ToHtmlCall --> TemplateFetch[templates.template("sample.html")]
  TemplateFetch --> TemplateRender[template.render(**self.content, sample_html=sample_html)]
  TemplateRender --> Return[return rendered HTML string]

(Interpretation: render reads state -> generates table HTML -> fetches Jinja2 template -> renders template with content and sample_html -> returns str)

## Raises:
Possible exceptions and their triggers (explicit or implicit):
- KeyError
  - Trigger: self.content does not contain the "sample" key. This would occur if a caller bypassed the Sample constructor contract or modified content after construction.
- AttributeError
  - Trigger: content["sample"] exists but does not expose to_html (e.g., the provided sample is not a pandas.DataFrame or a DataFrame-like object). The AttributeError arises when attempting to call to_html.
- jinja2.TemplateNotFound (from Jinja2)
  - Trigger: templates.template("sample.html") delegates to jinja2_env.get_template("sample.html"); if the named template is not present in the environment, Jinja2 will raise TemplateNotFound.
- jinja2.TemplateError or other Jinja2 rendering exceptions
  - Trigger: Template rendering fails due to template logic, missing context keys expected by "sample.html", or runtime errors in the template.
- Any exceptions raised by pandas.DataFrame.to_html
  - Trigger: Unlikely for normal DataFrame inputs, but errors in DataFrame conversion or extension methods will propagate.

Notes on exception handling:
- HTMLSample does not catch or wrap these exceptions; callers that need robust behavior should catch them around the render() call.

## Example:
1. Prepare a pandas DataFrame object named df containing the rows to display.
2. Instantiate the renderer using the Sample constructor signature (inherited by HTMLSample), supplying a name and the DataFrame, and optionally a caption and presentation kwargs. For example, create an HTMLSample that holds df and an optional caption.
3. Call the instance's render() method. The method returns a string containing the DataFrame rendered into a styled HTML table and embedded within the "sample.html" Jinja2 template.
4. Use the returned HTML string in the larger report (write to file, insert into a larger template, or return it via an HTTP response). No explicit cleanup is required.

Implementation notes for reimplementation:
- Ensure pandas is available and that the "sample" object supports to_html(classes=...).
- Ensure a Jinja2 environment is available and that templates.template("sample.html") returns a valid jinja2.Template (templates.template delegates to jinja2_env.get_template).
- Preserve the exact classes string "sample table table-striped" passed to DataFrame.to_html so that the produced table receives the expected CSS classes in the default styling pipeline.

### `src.ydata_profiling.report.presentation.flavours.html.sample.HTMLSample.render` · *method*

## Summary:
Renders the sample DataFrame stored in the instance into an HTML fragment and returns the full rendered HTML for the "sample" template without mutating the instance.

## Description:
This method is the HTML flavour's concrete implementation of the abstract Sample.render() contract. It is called during the HTML report-generation step when a Sample presentation item needs to be converted into an HTML representation (for example, when building the HTML report body or a report section that contains a sample table).

Known callers and context:
- Presentation factories, report builders, or HTML-report orchestration code that assemble a final HTML report from multiple renderable items call this method on concrete HTML Sample renderers.
- Lifecycle stage: invoked at render-time within the presentation pipeline (the step that serializes presentation items into HTML fragments and stitches them into the report templates).

Reason this logic is a separate method:
- It isolates HTML-specific rendering behavior (DataFrame.to_html + Jinja template rendering) from other flavours (JSON, text, etc.) and from the generic Sample data container. This separation keeps presentation-logic modular and testable and allows swapping or extending flavours without changing core data structures.

## Args:
- None (method is parameterless and uses instance state)

## Returns:
- str: The final HTML string produced by the Jinja template render call. This string contains:
    - sample_html: the HTML table produced by pandas.DataFrame.to_html(classes="sample table table-striped")
    - any other template placeholders resolved using the keys/values from self.content via **self.content

Edge-case return values:
- The returned string may be empty if the template renders to an empty string (unlikely for a typical "sample.html" template).
- The method never returns None.

## Raises:
This method does not raise custom exceptions, but the following exceptions may propagate directly from the underlying operations:

- KeyError
  - Condition: self.content does not have the key "sample".
  - Exact trigger: attempting to evaluate self.content["sample"].

- AttributeError
  - Condition: the object stored in self.content["sample"] does not have a callable to_html attribute.
  - Exact trigger: calling .to_html(...) on a non-DataFrame object that lacks that attribute.

- Any exception raised by pandas.DataFrame.to_html (e.g., TypeError, ValueError)
  - Condition: pandas encounters an invalid parameter or an internal failure while converting the DataFrame to HTML.
  - Exact trigger: the call self.content["sample"].to_html(classes=...) raises the exception.

- jinja2.exceptions.TemplateNotFound
  - Condition: the template named "sample.html" is not available in the configured Jinja environment.
  - Exact trigger: templates.template("sample.html") calls get_template and the template cannot be located.

- jinja2.exceptions.TemplateError (and subclasses)
  - Condition: a template-rendering error occurs (syntax error, issues invoking template-side filters, or other rendering-time problems).
  - Exact trigger: calling .render(...) on the Jinja template raises a TemplateError subclass.

Note: The method does not catch these exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
- self.content (the content dictionary)
- self.content["sample"] (the pandas.DataFrame expected under that key)
- potentially other keys inside self.content indirectly passed into the template via **self.content (e.g., "caption", "name", "anchor_id", "classes")

Attributes WRITTEN:
- None. The method does not modify self or any attribute on self. It constructs local variables and returns an HTML string.

## Constraints:
Preconditions:
- self.content must be a mapping-like object that contains the key "sample".
- self.content["sample"] should be a pandas.DataFrame (or any object that implements to_html(classes: str) -> str).
- The Jinja environment used by templates.template must be configured and contain the "sample.html" template.

Postconditions:
- After successful completion, no attributes on self are changed.
- The returned value is a string containing the template output with the variable sample_html set to the DataFrame HTML table produced by pandas.

## Side Effects:
- No I/O (files, network) or mutations of external objects are performed by this method itself.
- It delegates to:
    - pandas.DataFrame.to_html(...) which computes an HTML representation (pure in-memory).
    - Jinja2's Template.render(...) which performs in-memory template rendering.
- Template rendering consumes the values in self.content (passed into the template context) but does not mutate self.content.
- If the object under self.content["sample"] has side-effecting properties in its to_html implementation (non-standard), those effects will occur; the method itself does not introduce side effects.

