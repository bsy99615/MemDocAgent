# `image.py`

## `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage` · *class*

## Summary:
An ipywidgets-based renderer for Image presentation items that converts the Image.content payload into an ipywidgets.Widget (either a single HTML widget or a VBox combining the image and an optional caption) for use in Jupyter-style notebook presentations.

## Description:
WidgetImage is the concrete renderer used when the report presentation flavour targets interactive notebook output via ipywidgets. Instantiate this class when you need an Image item rendered directly in a notebook cell (for example, embedding an SVG fragment, a data URL, or an image URL). Typical callers are report/presentation builder code that constructs ItemRenderer instances for notebook output and then invokes render() on each item to produce displayable widgets.

Motivation and responsibility:
- Provide a compact, predictable mapping from the standardized Image.content payload (see Image) to an ipywidgets.Widget suitable for display.
- Enforce minimal presentation-specific formatting:
  - If the image is SVG, inject inline style to constrain width and remove any fixed height attributes written as height="NNpt".
  - If the image is non-SVG, wrap the payload in an <img src="..."> element and set the alt attribute from content["alt"].
  - Optionally render a caption (muted, italicized) below the image as a second HTML widget inside a VBox.
- Do not perform image format conversion, validation beyond simple string manipulation, or any network/file I/O; it relies on the image payload provided in content to be appropriate for embedding.

## State:
WidgetImage introduces no new instance attributes beyond those provided by the Image base class. It consumes the following entries from the inherited content dict:

- content["image"] (str)
  - Type: str
  - Meaning: the image payload. For ImageType.svg this is expected to be SVG markup (an <svg ...>...</svg> string). For non-SVG formats this is typically a URL or a data URI that can be used as the src attribute of an <img> element.
  - Constraints: must be a string; Image.__init__ ensures image is not None. If not a string, render() may raise TypeError when string operations are attempted.

- content["image_format"] (ImageType)
  - Type: ImageType enum (from ydata_profiling.config)
  - Valid values: at least ImageType.svg and other types (e.g., ImageType.png) as provided by the enum.
  - Usage: drives SVG-specific handling in render().

- content["alt"] (str)
  - Type: str
  - Meaning: alternative text for non-SVG images; used as the alt attribute when the renderer produces an <img> tag.

- content["caption"] (Optional[str])
  - Type: Optional[str]
  - Meaning: optional caption text. If present and not None, render() creates a muted, italic HTML caption and returns a VBox([image_widget, caption_widget]). If absent or None, render() returns only the image widget.

Class invariants (inherited & relied upon):
- content contains at least the keys "image", "image_format", "alt", and "caption" after construction (guaranteed by Image.__init__).
- item_type == "image" (set by Image).
- render() expects content values to be strings (or None for caption). Violating these expectations may raise runtime errors.

## Lifecycle:
Creation:
- Instantiate using the Image constructor signature (inherited):
  - required: image (str), image_format (ImageType), alt (str)
  - optional: caption (Optional[str]) default None
  - optional kwargs forwarded to the base classes: name (str), anchor_id (str), classes (str)
- Example constructor pattern:
  - WidgetImage(image=<str>, image_format=<ImageType>, alt=<str>, caption=<Optional[str]>, name=..., anchor_id=..., classes=...)

Usage:
- Primary operation: call render() to obtain an ipywidgets.Widget for display in a notebook.
- Typical invocation order:
  1. Instantiate the WidgetImage (see Creation).
  2. Optionally inspect metadata via instance.content, instance.name, etc.
  3. Call widget = instance.render()
  4. Display the returned widget using the notebook front-end (for example, display(widget)).
- render() is pure with respect to persistent resources: it constructs and returns ipywidgets.HTML (and optionally ipywidgets.VBox) objects; no file or network I/O is performed by this method.

Destruction / cleanup:
- No explicit cleanup is required. The returned ipywidgets.Widget objects are managed by ipywidgets and the notebook front-end. WidgetImage does not implement context management or close semantics.

Sequencing constraints:
- There is no required sequence of method calls beyond proper construction before calling render(). render() may be called multiple times; each call will produce fresh ipywidgets objects.

## Method Map:
flowchart LR
    A[WidgetImage.render()] --> B[read content["image"], content["image_format"]]
    B --> C{Is image_format == ImageType.svg?}
    C -- yes --> D[Inject 'style="max-width: 100%"' into <svg> start tag]
    D --> E[Remove height="NNpt" attributes via regex]
    C -- no --> F[Build <img src="{image}" alt="{alt}" /> HTML string]
    E --> G[widget = widgets.HTML(modified_svg_or_html)]
    F --> G
    G --> H{caption present and not None?}
    H -- yes --> I[caption_widget = widgets.HTML(<p style="color: #999"><em>{caption}</em></p>)]
    I --> J[return widgets.VBox([widget, caption_widget])]
    H -- no --> K[return widget]

## Raises:
- From construction (inherited):
  - ValueError: raised by Image.__init__ if the provided image argument is None. Callers must supply a non-None image argument.
- From render():
  - TypeError: if content["image"] or other expected string fields are not strings, string operations (replace, re.sub, f-string) will raise TypeError.
  - KeyError: unlikely under normal use because Image.__init__ sets required content keys, but can occur if the content dict was mutated externally and required keys removed.
  - re.error: unlikely, but if the regex engine receives unexpected input types this could propagate (normally not raised because input is a string).
  - ipywidgets-related errors: constructing widgets.HTML or widgets.VBox may raise exceptions if ipywidgets is not available or is misconfigured in the environment. In typical notebook environments with ipywidgets installed, these calls succeed.
- Behavioral notes:
  - The method does not perform I/O; if content["image"] is a URL and the browser fails to load it after rendering, that failure is handled by the browser/front-end and not by this code.
  - Passing non-SVG markup when image_format == ImageType.svg may produce unexpected HTML; the caller is responsible for matching the payload to the declared image_format.

## Example:
- SVG image (inline SVG markup):
  1) Create the WidgetImage item with SVG markup:
     WidgetImage(image="<svg ...>...</svg>", image_format=ImageType.svg, alt="unused for svg", caption="A caption")
  2) Render to a widget:
     widget = instance.render()
  3) Display in a notebook:
     display(widget)

- Non-SVG image (URL or data URI):
  1) Create the WidgetImage item:
     WidgetImage(image="data:image/png;base64,...." or "https://example.com/img.png", image_format=ImageType.png, alt="Descriptive alt text")
  2) Render and display:
     widget = instance.render()
     display(widget)

Notes for implementers:
- Ensure content["image"] is a string appropriate to the declared image_format: SVG markup for ImageType.svg, otherwise a URL or data URI for embedding in an <img> element.
- WidgetImage is intentionally simple: it performs minimal, safe HTML adjustments for better notebook fit (max-width and removal of pt heights) and leaves complex image handling to upstream code that constructs the content payload.

### `src.ydata_profiling.report.presentation.flavours.widget.image.WidgetImage.render` · *method*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Produce an ipywidgets.Widget that displays the instance's image payload in a Jupyter environment, applying small SVG-specific fixes and optionally stacking a muted caption below the image. The call does not mutate the instance state.

## Description:
This method is called by the presentation/report rendering pipeline when a WidgetImage must be converted into a displayable UI widget — for example, when building the notebook/interactive output from a list of ItemRenderer objects. Typical callers are presentation/report builders or any code that iterates item renderers and calls render() to collect widgets for display.

It is a dedicated method because:
- Rendering concerns (HTML markup, widget construction, UI layout) are separated from the Image data container and higher-level report orchestration.
- Format-specific adjustments (SVG inline markup tweaks and height-attribute removal) are UI concerns best centralized in one place.
- It composes the final widget structure (single HTML widget vs. VBox with caption) which is a presentation-level decision.

## Args:
No explicit parameters. Operates on instance state:
- self.content (dict) — required keys and expected types:
    - "image" (str): SVG markup when image_format == ImageType.svg; otherwise an image source string suitable for use in an <img src="..."> attribute (e.g., data URL, file path, or HTTP URL).
    - "image_format" (ImageType): Enum value indicating image type; SVG handling occurs when equal to ImageType.svg.
    - "alt" (str): Alternative text used when constructing an <img> element for non-SVG images.
    - "caption" (Optional[str]): If present and not None, a caption is rendered underneath the image. Note: an empty string ("") is considered not None and will result in an (empty) caption widget being rendered.

These keys are normally provided by Image.__init__; if that contract is violated, the method may raise exceptions (see Raises).

## Returns:
ipywidgets.Widget (an instance of ipywidgets.widgets.Widget)
- If no caption is provided (either "caption" key missing or content["caption"] is None):
    - Returns widgets.HTML containing either:
        - the (possibly modified) SVG markup string (when image_format == ImageType.svg), or
        - an <img src="..."> HTML string constructed from content["image"] and content["alt"] (for non-SVG formats).
- If a caption is present and not None:
    - Returns widgets.VBox([image_widget, caption_widget]) where:
        - image_widget is the widgets.HTML described above.
        - caption_widget is widgets.HTML wrapping the caption text in a paragraph with style "color: #999" and italicized via <em>.
Edge cases:
- Caption presence check uses the exact test: "caption" in self.content and self.content["caption"] is not None. An empty caption string ("") passes this test and yields a caption widget.

## Raises:
The method does not deliberately raise new application-specific exceptions, but the following may propagate:
- KeyError: if required keys ("image", "image_format", "alt") are missing from self.content.
- TypeError / AttributeError: if content["image"] is not a string (string methods or re.sub may fail), or if content is not a dict.
- Any exception raised by ipywidgets.HTML or widgets.VBox constructors (e.g., if ipywidgets is misconfigured).
Notes:
- Under normal use Image.__init__ supplies the required keys and prevents image being None, so these exceptions are not expected for well-formed instances.

## State Changes:
Attributes READ:
- self.content["image"]
- self.content["image_format"]
- self.content["alt"]
- self.content.get("caption") via membership check and then read

Attributes WRITTEN:
- None. self and self.content remain unchanged; local variables hold transformed strings.

## Constraints:
Preconditions:
- self.content must be a dict containing "image", "image_format", and "alt" (Image.__init__ normally guarantees this).
- content["image"] must be a str (SVG markup or image source string).
- content["image_format"] must be an ImageType enum value (ImageType.svg triggers SVG handling).
Postconditions:
- The instance state is unchanged.
- A widgets.Widget is returned that represents the image (and optional caption) ready for display.

## Implementation details and exact transformations:
- SVG handling:
    - When content["image_format"] == ImageType.svg, the method:
        1) Replaces every occurrence of the substring 'svg ' with 'svg style="max-width: 100%" ' to limit rendered SVG width in the container.
        2) Removes any SVG height attributes that exactly match the regex pattern height="[\d]+pt" (one or more ASCII digits followed by "pt") using re.sub('height="[\\d]+pt"', "", image). This only strips height attributes specified in points (pt); other units (px, em, %) are unaffected.
    - The substitutions operate on a local copy of the image string and are not saved back into self.content.
- Non-SVG handling:
    - For non-SVG images, constructs the HTML string '<img src="{image}" alt="{alt}" />' using content["image"] and content["alt"].
    - The method does not validate that the src value points to an existing resource; it simply embeds the provided string.
- Widget construction:
    - The constructed HTML string (SVG markup or <img> tag) is wrapped in widgets.HTML(image_string).
    - If a caption exists and is not None, the method creates widgets.HTML(f'<p style="color: #999"><em>{caption}</em></p>') and returns widgets.VBox([image_widget, caption_widget]). Otherwise returns image_widget.

## Side Effects:
- Allocates ipywidgets objects (widgets.HTML and possibly widgets.VBox).
- No I/O (no network or filesystem access) is performed by this method itself.
- The HTML passed to widgets.HTML is inserted as-is into the widget and thus may include raw HTML/SVG content (be mindful of potential XSS issues if image or caption originate from untrusted sources).

