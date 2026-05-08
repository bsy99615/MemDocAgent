# `image.py`

## `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage` · *class*

## Summary:
HTMLImage is a concrete Image renderer for the HTML presentation flavour. It produces an HTML fragment by rendering the "diagram.html" template with the image content payload inherited from Image.

## Description:
HTMLImage exists to convert an Image presentation item into an HTML string suitable for inclusion in an HTML report. It implements the abstract render() responsibility declared by the Image base class by delegating rendering to the HTML flavour's template subsystem.

Typical instantiation scenarios / callers:
- The HTML presentation layer or report builder that is assembling HTML report pages will instantiate Image items (or specifically HTMLImage) when an image needs to be embedded in the generated HTML.
- Presentation pipelines that choose the "html" flavour will prefer this renderer for Image items.
- Consumers call instance.render() to obtain the final HTML string to embed in the report output.

Motivation and responsibility boundary:
- Responsibility: take the standardized Image.content payload (provided by the Image base class / Renderable) and render it into an HTML fragment using the "diagram.html" template.
- Boundary: HTMLImage does not validate or mutate the content payload beyond passing it to the template renderer. It does not manage file I/O, resource allocation, or template configuration — those are responsibilities of the templating subsystem and the code that constructs the content.

## State:
Inherited state (no new instance attributes introduced by HTMLImage):

- content: dict[str, Any]
  - Description: Inherited from Image / Renderable. Holds the structured payload that the template expects.
  - Expected keys (guaranteed by Image.__init__):
    - "image" (str): The image payload or reference (e.g., data URL, base64 string, filename or identifier).
    - "image_format" (ImageType): Enum element indicating the image format (e.g., svg or png).
    - "alt" (str): Alternative text for accessibility.
    - "caption" (Optional[str]): Optional caption text or None.
  - Optional keys (may be present if passed through kwargs to Image.__init__):
    - "name" (str), "anchor_id" (str), "classes" (str).
  - Invariants:
    - After successful Image construction, content always contains at least "image", "image_format", "alt", and "caption".
    - HTMLImage.render() will pass the dictionary exactly as keyword arguments to the template renderer (render(**self.content)).

- item_type: str
  - Inherited invariant: equals "image" (set by Image/ItemRenderer).

Constructor parameters:
- HTMLImage does not define its own constructor; it inherits Image.__init__.
- Required parameters (per Image.__init__):
  - image (str): must not be None (Image.__init__ raises ValueError if None).
  - image_format (ImageType): required; must be a valid ImageType member.
  - alt (str): required.
- Optional:
  - caption (Optional[str]) default None.
  - Additional keyword arguments forwarded to the parent (name, anchor_id, classes).

Class invariants:
- content contains the expected keys.
- item_type == "image".
- render() returns a str containing HTML produced by the templating subsystem.

## Lifecycle:
Creation:
- Instantiate by calling the inherited constructor with the same parameters as Image:
  - Supply image, image_format, alt; caption and other kwargs are optional.
- No special factory is required; the presentation layer commonly constructs HTMLImage instances when assembling HTML output.

Usage:
- Primary operation: call instance.render() once you need the HTML representation. There are no prerequisite method calls.
- Typical sequence:
  1. Construct instance (inherited Image.__init__ runs and validates image is not None).
  2. Optionally inspect instance.content for metadata.
  3. Call instance.render() to obtain the rendered HTML fragment (a str).
  4. Insert returned HTML into the larger HTML report document.
- Concurrency: HTMLImage is a thin, stateless wrapper around content and the template call; concurrent calls are safe provided the templating subsystem supports concurrent rendering.

Destruction / cleanup:
- No cleanup responsibilities. HTMLImage holds no external resources and does not open files or maintain handles. Any resources used during rendering are owned and cleaned up by the templating subsystem.

## Method Map:
graph LR
  A[Create HTMLImage(image, image_format, alt, caption?, **kwargs)] --> B[instance.content dict]
  B --> C[HTMLImage.render()]
  C --> D[templates.template("diagram.html")]
  D --> E[Template.render(**instance.content)]
  E --> F[returns str (HTML fragment)]

(Notes: templates.template(...) returns a template-like object exposing a render(**context) -> str function; HTMLImage simply forwards self.content as keyword args.)

## Raises:
- ValueError:
  - Trigger: Inherited Image.__init__ will raise ValueError if the provided image argument is None. This happens at construction time before render() is ever called.
- Errors originating from the templates subsystem:
  - Trigger: If the template lookup or rendering fails, exceptions raised by the templates module or underlying templating engine will propagate out of render(). HTMLImage does not catch or translate template subsystem exceptions.
  - Nature: The exact exception types depend on the templating implementation used by templates.template (e.g., lookup errors, rendering errors, or errors caused by missing or malformed context values). Calling code should be prepared to handle templating-related exceptions when invoking render().

## Example:
Typical usage (described in steps, not as source code):
1. Construct an HTMLImage instance via the inherited Image constructor by providing:
   - image: a data URL, base64 payload, filename, or other representation the templating layer expects.
   - image_format: an ImageType value (svg or png).
   - alt: short alternative text.
   - caption: optional descriptive caption (or omit to leave None).
2. When ready to embed the image into the HTML report, call render() on the instance.
3. The call returns a string containing the HTML produced by rendering the "diagram.html" template with the instance's content dict as the template context.
4. Insert the returned HTML fragment into the larger HTML page or document.

Edge cases to consider:
- If image was passed as None at construction, construction raises ValueError.
- If the template "diagram.html" cannot be found or rendering fails because the template expects keys that are missing or content values are malformed, render() will raise an exception produced by the templating subsystem; handle or propagate as appropriate.

### `src.ydata_profiling.report.presentation.flavours.html.image.HTMLImage.render` · *method*

## Summary:
Renders the image item into an HTML fragment by applying the HTML flavour's "diagram.html" template to the instance's content and returns the resulting HTML string. The method does not mutate the instance.

## Description:
Known callers and context:
- Invoked by the report presentation pipeline (HTML flavour) during the final rendering phase when a collection of ItemRenderer / Image instances is converted into HTML output for a report.
- Typical caller pattern: a presentation or report builder iterates its list of renderable items and calls render() on each item to collect rendered fragments that are then joined into a full HTML report.

Why this is a separate method:
- Implements the concrete, flavour-specific rendering logic for Image items for the HTML presentation flavour. Keeping template lookup and render logic here preserves the polymorphic contract of the Image.render abstract API, isolates template concerns from higher-level report assembly, and allows alternate flavours or subclasses to override rendering without changing the pipeline.

## Args:
    None

## Returns:
    str: The rendered HTML fragment produced by calling the "diagram.html" template's render method with the instance content expanded as keyword arguments.
    - Typical value: a non-empty HTML string (an HTML fragment containing the rendered image markup).
    - Edge cases:
        - If the template renders to an empty string, an empty string is returned.
        - If the template engine returns a markup type (e.g., jinja2.Markup), it will be returned as-is but is usable where a str is expected.

## Raises:
    - TypeError: If self.content cannot be expanded as keyword arguments (for example, if a key in self.content is not a string, Python will raise "keywords must be strings" when applying **self.content).
    - Any exception raised by the template loader or template engine is propagated unchanged. Common examples (dependent on the configured template backend and filters) include:
        - TemplateNotFound / Loader error: if the named template "diagram.html" cannot be located by the template system.
        - TemplateSyntaxError / UndefinedError / TemplateRuntimeError: if the template contains syntax errors or runtime errors during render.
        - Exceptions raised by custom filters or functions used inside the template (these will propagate from template.render).
    - Note: This method does not catch or wrap template errors — callers should handle template/backend exceptions as appropriate.

## State Changes:
    Attributes READ:
        - self.content: used as the mapping of keyword arguments passed into the template render call.
    Attributes WRITTEN:
        - None. The method does not modify self or external variables.

## Constraints:
    Preconditions:
        - self.content must be present and be a mapping (typically a dict) whose keys are strings (so they can be expanded as keyword arguments).
        - The presentation environment must have the "diagram.html" template available via the templates.template(...) loader.
    Postconditions:
        - Returned value is the direct result of template.render(**self.content); the instance's content and other attributes are unchanged.
        - No internal caching or mutation of the template or content occurs in this method.

## Side Effects:
    - The method itself performs no explicit I/O or network operations.
    - Side effects may occur indirectly if the template engine, the template code, or any custom filters/functions invoked during rendering perform I/O, access external resources, or mutate global state. Those side effects originate from the template backend or filters, not from this method body.

