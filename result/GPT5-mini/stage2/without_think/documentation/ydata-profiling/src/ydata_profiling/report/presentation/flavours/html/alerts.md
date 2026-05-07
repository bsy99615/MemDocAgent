# `alerts.py`

## `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts` · *class*

## Summary:
HTMLAlerts is a concrete Alerts renderer that converts an Alerts container into an HTML fragment by rendering the "alerts.html" Jinja2 template with the Alerts content and a fixed mapping of alert-to-style names.

## Description:
HTMLAlerts provides an HTML-specific rendering of the generic Alerts presentation container. It should be instantiated anywhere the presentation pipeline needs an HTML fragment representing the collected profiling alerts (for example, in an HTML report builder or presentation factory). The class inherits all construction and state from the Alerts base class; its only responsibility is to implement render() to return an HTML string.

Motivation and responsibility boundary:
- Purpose: centralize the HTML rendering logic for alert items and to provide a consistent mapping from alert types to visual style names used by the "alerts.html" template.
- Boundary: HTMLAlerts does not validate alert data, mutate the Alerts.content structure, or manage template configuration — it only supplies a predefined styles mapping and delegates rendering to the templates.template(...) Jinja2 pipeline.

Known callers / typical instantiation:
- A report builder or presentation factory that already produces an Alerts instance may directly instantiate HTMLAlerts (Alerts constructor signature applies) and call render() to obtain HTML.
- Template-driven report assembly code that composes multiple HTML fragments into a larger document will call HTMLAlerts.render() to get the alerts fragment.

## State:
HTMLAlerts does not declare new instance attributes; it relies on the state inherited from Alerts / ItemRenderer. Relevant observable attributes inherited from Alerts:

- item_type : str
  - Value: "alerts" (invariant set by Alerts.__init__).
  - Meaning: identifies this renderer kind.

- content : Dict[str, Any]
  - Structure: {"alerts": <alerts_arg>, "style": <style_arg>}
  - "alerts" value:
    - Type: Union[List[Alert], Dict[str, List[Alert]]]
    - Constraint: HTMLAlerts assumes the downstream Jinja template knows how to iterate or handle the provided shape; HTMLAlerts does not modify or validate it.
  - "style" value:
    - Type: Style
    - Meaning: style configuration used by templates.

Notes about HTMLAlerts-specific behavior:
- During render(), HTMLAlerts constructs a local styles mapping (dictionary) that maps alert keys (string identifiers such as "constant", "unique", "missing", etc.) to template style names (for example "warning", "primary", "info", "default"). This mapping is passed into the template context under the key styles. The mapping keys are:
    - "constant", "unsupported", "type_date"
    - "constant_length", "high_cardinality", "imbalance", "unique", "uniform"
    - "infinite", "zeros", "truncated", "missing", "skewed"
    - "high_correlation", "duplicates", "non_stationary", "seasonal"
  with corresponding style values ("warning", "primary", "info", "default") as defined by the mapping.

Class invariants:
- self.content remains the dict supplied by Alerts.__init__ and must contain keys "alerts" and "style".
- render() will always call templates.template("alerts.html") and pass (**self.content, styles=styles) to the template's render() method.

## Lifecycle:
Creation:
- Use the Alerts constructor signature (inherited):
    Alerts(alerts: Union[List[Alert], Dict[str, List[Alert]]], style: Style, **kwargs)
  where kwargs may include name, anchor_id, classes and are forwarded to ItemRenderer.__init__.
- Example: html_alerts = HTMLAlerts(alerts, style, name="column-alerts")

Usage:
- Call html_fragment = html_alerts.render() to get an HTML string representing the alerts.
- There is no mandatory ordering of other method calls; render() can be invoked any time after instantiation provided that self.content was properly initialized by the inherited constructor.

Destruction:
- No explicit cleanup is required. HTMLAlerts does not open resources nor implement context management; standard garbage collection suffices.

## Method Map:
graph TD
    A[HTMLAlerts.render()] --> B[Construct styles dict (alert_type -> style_name)]
    B --> C[templates.template("alerts.html")]
    C --> D[Template.render(**self.content, styles=styles)]
    D --> E[Return rendered HTML string]

## Raises:
The implementation does not raise custom exceptions itself, but callers should be aware of exceptions that can propagate from its dependencies:

- jinja2.exceptions.TemplateNotFound
  - Trigger: the Jinja environment cannot find "alerts.html".
  - Origin: templates.template() which calls jinja2_env.get_template(template_name).

- jinja2.exceptions.TemplateSyntaxError
  - Trigger: syntax errors inside the "alerts.html" template discovered at load/compile time.

- jinja2.exceptions.UndefinedError (or other runtime template rendering errors)
  - Trigger: attempting to render the template when expected variables are missing or when template expressions fail (for example, if the template expects particular keys/attributes on alerts or the style object that are not present).

- TypeError / ValueError during rendering
  - Trigger: if self.content is not a mapping that can be unpacked into template keyword arguments, or if the values passed are not compatible with the template's expectations (for example, non-iterable alerts where the template expects an iterable).

Note: HTMLAlerts does not validate or coerce self.content; such validation must be performed by the caller or by the template itself.

## Example:
- Creation:
    1. Collect Alert objects into a list or grouped dict.
    2. Obtain or create a Style instance describing presentation choices.
    3. Instantiate HTMLAlerts with the alerts and style (optional name/anchor_id/classes can be passed).

- Typical sequence:
    - html_alerts = HTMLAlerts(alerts_collection, style)
    - html_fragment = html_alerts.render()  # returns an HTML string from "alerts.html"
    - Insert html_fragment into the larger HTML report or write it to disk.

Practical notes:
- The template receives three keys in its context: "alerts" and "style" (from self.content) plus "styles" (the mapping injected by HTMLAlerts). The template author should use the "styles" mapping to choose CSS classes or presentation tokens based on alert type keys.
- To reimplement this class: subclass Alerts, implement render() to construct the styles mapping exactly as specified above, obtain the Jinja2 Template for "alerts.html" (using the project's template loader), and call template.render(**self.content, styles=styles) returning the resulting string.

### `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts.render` · *method*

## Summary:
Produce an HTML fragment for the alerts section by rendering the alerts.html Jinja2 template with the Alerts.content context plus a fixed mapping of alert keys to CSS-style tokens; does not mutate the object.

## Description:
- Known callers and context:
    - Invoked during the HTML presentation step of report generation when an Alerts instance is converted into HTML (for example by a report builder or a presentation factory that assembles report sections).
    - Lifecycle stage: called while assembling the final HTML report to obtain the alerts section markup.
- Why this is its own method:
    - Encapsulates HTML-specific rendering details (the template selection and the mapping of logical alert keys to style tokens) so the Alerts base class stays rendering-agnostic.
    - Keeps the mapping centralized and easily maintainable; other flavours (JSON, plain text) can implement different render strategies without duplication.

## Args:
    None. Uses instance state (self.content) prepared by Alerts.__init__.

## Returns:
    str: The rendered HTML produced by Jinja2's Template.render for the alerts.html template.
    - Guaranteed type on success: Python str (the Jinja2 rendering API returns a unicode string).
    - Possible edge-case: an empty string if the template produces no output.

## Raises:
    - TypeError:
        - Condition: Raised by Python when attempting to expand **self.content if self.content is not a mapping (for example, if self.content is None or a list). The exact Python error originates from the argument unpacking operation in Template.render(**self.content, styles=styles).
    - jinja2.exceptions.TemplateNotFound:
        - Condition: Raised by templates.template("alerts.html") if the alerts.html template cannot be located by the Jinja2 environment (templates.template delegates to jinja2_env.get_template).
    - jinja2.exceptions.TemplateError (and its subclasses, e.g., TemplateRuntimeError, UndefinedError):
        - Condition: Raised during template.render(...) if the template contains errors, template execution triggers runtime issues, or template filters/globals raise errors. Any exception raised inside the template evaluation will propagate out.
    - Any exception raised by custom filters, tests, globals or other callables invoked during template rendering will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.content (expected to be a mapping with the keys mandated by Alerts: "alerts" and "style"). The method expands this mapping into the template context via **self.content.
- Attributes WRITTEN:
    - None. The method does not modify self or any attributes on self.

## Constraints:
- Preconditions:
    - self.content must be a mapping (dict-like) so that **self.content is valid for keyword expansion.
    - Per Alerts invariant, self.content should contain:
        - "alerts": Union[List[Alert], Dict[str, List[Alert]]] — the alert objects or grouped alerts expected by the template.
        - "style": Style — the style/configuration object the template may use.
    - The Jinja2 environment must be configured so templates.template("alerts.html") returns a valid Template object.
- Postconditions:
    - On success, returns a str containing the rendered HTML alerts fragment.
    - self and self.content remain unchanged.

## Template interaction / exact call:
- The method obtains the template and renders it by calling:
    - templates.template("alerts.html").render(**self.content, styles=styles)
- The method injects a local variable into the template context named "styles" whose value is the following mapping (string keys → string style tokens):
    - "constant": "warning"
    - "unsupported": "warning"
    - "type_date": "warning"
    - "constant_length": "primary"
    - "high_cardinality": "primary"
    - "imbalance": "primary"
    - "unique": "primary"
    - "uniform": "primary"
    - "infinite": "info"
    - "zeros": "info"
    - "truncated": "info"
    - "missing": "info"
    - "skewed": "info"
    - "high_correlation": "default"
    - "duplicates": "default"
    - "non_stationary": "default"
    - "seasonal": "default"

## Side Effects:
- Template lookup may perform I/O (file/resource access) depending on the configured Jinja2 loader.
- Template rendering executes template code and any invoked filters, tests, or global functions; those callables may produce side effects (I/O, logging, database calls) which are not performed by this method directly but occur as a result of template execution.

