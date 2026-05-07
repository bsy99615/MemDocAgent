# `image.py`

## `src.ydata_profiling.report.presentation.core.image.Image` · *class*

## Summary:
Represents a renderable image item for report presentation. Encapsulates the image payload, its format, alternative text, and optional caption, and forwards rendering responsibilities to concrete renderer implementations.

## Description:
Instantiate this class when you need to represent an image as a report item (for example, an inline chart snapshot or an embedded image in a generated report). The Image class collects the necessary metadata (payload, format, alt text, caption) and registers itself as an item of type "image" with the presentation framework via its ItemRenderer base class.

Known factories/callers:
- Presentation/report builder code that constructs a list of ItemRenderer instances for final rendering.
- Any code that prepares report content and wishes to include an image item in the presentation pipeline.

Motivation and responsibility boundary:
- Image is a lightweight container for image data and metadata; it does not perform rendering or format conversion itself. The concrete rendering logic is intentionally left to subclasses or external renderer components which implement the render() method.
- This class enforces minimal validation (image must not be None) and provides a consistent content dictionary shape consumed by the presentation layer.

## State:
Attributes (derived from constructor and inherited state):

- content: dict[str, Any]
  - Description: primary storage for this item's data created by Renderable.__init__.
  - Keys present for Image instances:
    - "image" (str): the image payload or reference supplied by the caller.
    - "image_format" (ImageType): the format enum member (ImageType.svg or ImageType.png).
    - "alt" (str): alternative text describing the image.
    - "caption" (Optional[str]): optional caption text or None.
    - Optionally "name", "anchor_id", "classes" if provided via kwargs are added by Renderable.__init__.
  - Invariants: content always contains at least the four keys listed above after successful construction.

- item_type: str
  - Value set to "image" by Image.__init__ (via ItemRenderer).
  - Invariant: item_type == "image" for all instances of this class.

- The following attribute accessors are available via Renderable:
  - name -> str (comes from content["name"], present only if provided)
  - anchor_id -> str (content["anchor_id"], present only if provided)
  - classes -> str (content["classes"], present only if provided)

Constructor parameters (and constraints):
- image: str
  - Required. Must not be None. Empty string is accepted by the code, but callers should pass valid image data or a reference (e.g., base64 data URL, file path, or identifier) consistent with downstream renderers.
- image_format: ImageType
  - Required. Must be one of the ImageType members (ImageType.svg or ImageType.png). No runtime type check is performed here.
- alt: str
  - Required. Short text describing the image for accessibility/labeling.
- caption: Optional[str] = None
  - Optional. If omitted, content["caption"] will be None.
- **kwargs
  - Forwarded to ItemRenderer/Renderable. Common accepted keys: name (str), anchor_id (str), classes (str). These are optional and, if provided, become entries inside content.

Class invariants:
- content is a dict that includes "image", "image_format", "alt", and "caption".
- item_type always equals the literal "image".
- render() is abstract for this class and concrete implementations must override it.

## Lifecycle:
Creation:
- Instantiate with required arguments:
  - Image(image=<str>, image_format=<ImageType>, alt=<str>, caption=<Optional[str]>[, name=..., anchor_id=..., classes=...])
- Internally, Image validates image is not None and then calls ItemRenderer.__init__("image", content_dict, **kwargs) which in turn initializes Renderable.content.

Usage:
- Typical sequence:
  1. Create instance (as shown above).
  2. Optionally read metadata via instance.content, instance.name, instance.anchor_id, instance.classes.
  3. Call instance.render() to produce the final rendered output — note: Image.render is not implemented and will raise NotImplementedError unless a concrete subclass or renderer provides an implementation.
  4. __repr__() returns the string "Image" — useful in logs or debugging.

Destruction / cleanup:
- No explicit cleanup is required by Image. It does not open resources or implement a context manager. If a concrete renderer allocates resources during render, that renderer is responsible for cleanup.

## Method Map:
graph LR
  A[External code] --> B[Image.__init__(image, image_format, alt, caption, **kwargs)]
  B --> C[ItemRenderer.__init__("image", content_dict, **kwargs)]
  C --> D[Renderable.__init__(content_dict, name, anchor_id, classes)]
  B --> E[instance.content contains image,image_format,alt,caption]
  F[Caller] -->|reads| E
  G[Renderer subclass] -->|implements| H[render() -> Any]
  H --> I[Rendered output (format depends on subclass)]

Note: Image.render() itself raises NotImplementedError; a concrete renderer must implement the H node.

## Raises:
- ValueError: raised by __init__ if the supplied image argument is None. Message includes alt and caption values for debugging.
- NotImplementedError: raised by render() to indicate that subclasses must implement rendering logic.

## Example:
Create an Image item and inspect its metadata:

img = Image(
    image="data:image/png;base64,iVBORw0KGgoAAAANS...", 
    image_format=ImageType.png, 
    alt="Histogram of ages", 
    caption="Age distribution", 
    name="age_histogram"
)
# Inspect content:
print(img.content["image_format"].value)  # "png"
print(img.name)                            # "age_histogram"
print(repr(img))                           # "Image"

# Attempting to render with this base class will raise:
try:
    img.render()
except NotImplementedError:
    # A concrete renderer implementation must provide render()
    pass

Typical usage in practice:
- A concrete renderer (part of the presentation layer) will accept this Image instance and implement the rendering step (convert data URL or binary into an embedded HTML/SVG element, save to disk, etc.). The Image class only provides the standardized content payload and minimal validation.

### `src.ydata_profiling.report.presentation.core.image.Image.__init__` · *method*

## Summary:
Validate and initialize an Image renderable by storing an image-specific content dictionary on the instance and delegating common renderable metadata handling to the base classes; after this call the instance represents an image item with item_type set to "image".

## Description:
Called when constructing an Image presentation item as part of report construction or rendering preparation. The constructor:
- enforces that an image value is provided (not None),
- builds a standardized content dictionary with the keys expected by image renderers,
- forwards the content and optional metadata (name, anchor_id, classes) into the Renderable/ItemRenderer initialization chain.

This remains a dedicated initializer to centralize image-specific validation and to keep the construction of the image content payload consistent across the codebase. It relies on the shared Renderable/ItemRenderer behavior to persist content and attach metadata.

## Args:
    image (str):
        Image payload as a string. This value must not be None. The constructor does not otherwise validate the string format or semantics.
    image_format (ImageType):
        Enum value describing the image format (type defined by ydata_profiling.config.ImageType). Used by renderers to decide how to embed or present the image.
    alt (str):
        Alternative text for the image (accessibility / fallback text). Should be provided as a string.
    caption (Optional[str], optional):
        Optional human-readable caption for the image. Defaults to None.
    **kwargs:
        Additional keyword arguments forwarded to ItemRenderer.__init__. Recognized and accepted keyword names are:
        - name (Optional[str])
        - anchor_id (Optional[str])
        - classes (Optional[str])
        If any other keyword names are supplied, a TypeError will be raised at runtime because ItemRenderer.__init__ does not accept them.

## Returns:
    None
    This is an initializer; it returns None and mutates the instance.

## Raises:
    ValueError:
        If the provided image is None. The raised message is constructed exactly as:
        "Image may not be None (alt={alt}, caption={caption})"
        where {alt} and {caption} are the provided alt and caption values (their string representations).
    TypeError:
        If kwargs contains unexpected keyword arguments not in (name, anchor_id, classes). This error originates from Python's function call mechanism when ItemRenderer.__init__ receives unexpected keyword arguments.

## State Changes:
Attributes READ:
    - None on self. The method references only its parameters. Note: alt and caption parameter values are interpolated into the ValueError message when image is None.
Attributes WRITTEN (in order of effects):
    1. self.content (dict): assigned to the content dictionary passed down to Renderable.__init__. That dictionary initially contains the keys:
        - "image": image
        - "image_format": image_format
        - "alt": alt
        - "caption": caption
       Renderable.__init__ may then insert additional keys into this same dict when optional metadata arguments are provided (see below).
    2. (possible) self.content["name"], self.content["anchor_id"], self.content["classes"]:
       If kwargs included name, anchor_id, or classes, Renderable.__init__ inserts these keys into the content dict.
    3. self.item_type (str): set to the literal "image" by ItemRenderer.__init__ after Renderable.__init__ returns.

## Constraints:
Preconditions:
    - image is not None (otherwise ValueError is raised).
    - image_format and alt should be provided according to their intended types; no runtime type checking is performed beyond what Python enforces.
Postconditions:
    - self.content exists and contains at least the keys "image", "image_format", "alt", and "caption" with the values passed to the constructor.
    - self.item_type == "image".
    - If name/anchor_id/classes were passed via kwargs, the corresponding keys are present in self.content.
    - Accessing Renderable.name, Renderable.anchor_id, or Renderable.classes will succeed only if the corresponding keys were inserted into self.content; otherwise those property accesses will raise a KeyError.

## Side Effects:
    - No I/O, logging, or external network calls are performed.
    - Mutates the instance by setting self.content and self.item_type and possibly adding metadata keys to the content dict.
    - May raise TypeError if unexpected kwargs are provided (this originates from forwarding kwargs to ItemRenderer.__init__).

### `src.ydata_profiling.report.presentation.core.image.Image.__repr__` · *method*

## Summary:
Returns a stable, concise textual identifier for this renderer object; does not modify the object's state.

## Description:
- Known callers and context:
    - Python built-in mechanisms that request an object's representation (for example, calls to repr(obj) in debugging, logging, REPL inspection, or test assertions).
    - Any code that serializes or logs item-renderer objects and expects a brief human-readable identifier.
    - Lifecycle stage: invoked during debugging, logging, interactive inspection, or anywhere a textual representation of the renderer is required by the reporting pipeline or developer tooling.
- Rationale for being a separate method:
    - Overriding __repr__ provides a consistent, short identifier ("Image") for instances of this renderer without exposing internal state.
    - Keeping this logic in a dedicated method centralizes the object's printed/represented form and enables readable, stable output for logs and tests; it is small and intentional so inlining elsewhere would reduce clarity.

## Args:
    None

## Returns:
    str: The exact string "Image". This is a constant, stateless representation; it does not depend on any instance attributes.

## Raises:
    None. This method does not raise exceptions.

## State Changes:
- Attributes READ:
    - None (the implementation does not access any self.<attr> attributes)
- Attributes WRITTEN:
    - None (the implementation does not modify self or any external state)

## Constraints:
- Preconditions:
    - The object must be a valid instance; no additional invariants are required before calling.
- Postconditions:
    - Calling the method returns the constant string "Image" and leaves the object unchanged.

## Side Effects:
    - None. The method performs no I/O, network access, or mutation of objects outside self.

### `src.ydata_profiling.report.presentation.core.image.Image.render` · *method*

## Summary:
Abstract entry point for producing a presentation-specific representation of an Image item; the base implementation always raises NotImplementedError and does not modify object state.

## Description:
Known callers and lifecycle stage:
- Called by the presentation layer / renderer dispatcher during the report rendering phase. Typical caller patterns include a renderer that iterates over ItemRenderer instances and calls render() to obtain the serialized form for each item when building the final report output.
- This method is invoked after an Image instance has been constructed (Image.__init__) and included in a renderable structure (e.g., a report section or component list).

Why this is its own method:
- Rendering is presentation-specific (HTML, JSON, text, framework nodes, etc.). Keeping render() abstract separates data (the Image item's content provided at construction) from presentation logic so multiple backends can implement their own output format without changing the data model.

## Args:
- None

## Returns:
- Any
  - The base implementation does not return; it raises NotImplementedError.
  - Concrete subclasses should return a renderer-appropriate value (for example, an HTML string, a dict for JSON serialization, or a framework-specific node). The exact return type and semantics are defined by the concrete renderer implementation.

## Raises:
- NotImplementedError
  - The base Image.render implementation unconditionally raises NotImplementedError to signal that subclasses must override this method.

## State Changes:
Attributes READ:
- None in the base implementation. The base method does not read or mutate instance attributes.

Attributes WRITTEN:
- None in the base implementation. The base method does not modify instance attributes.

Note for implementers:
- Although the base render() does not access instance state, concrete renderers will typically read the data supplied at construction. Image.__init__ populates the Renderable/ItemRenderer content dict with these keys:
  - "image": str (the image source; Image.__init__ enforces that this value is not None)
  - "image_format": ImageType (from ydata_profiling.config)
  - "alt": str (alt text)
  - "caption": Optional[str] (caption or None)
- Implementations should treat the content dict as read-only unless the renderer contract explicitly allows mutation.

## Constraints:
Preconditions:
- The Image instance must be constructed via Image.__init__, which raises ValueError if the provided image parameter is None. Callers may rely on content["image"] being present and non-None for well-formed instances.
- There is no other state required by the base method. Concrete renderers may impose additional preconditions (for example, requiring local file access, network availability, or particular image formats) and must document them.

Postconditions:
- Base implementation: NotImplementedError is raised and no state is modified.
- Concrete implementations: must return the renderer-defined representation and should not have hidden side effects unless explicitly documented by that renderer.

## Side Effects:
- Base implementation: none (only raises NotImplementedError).
- Concrete implementations may perform side effects such as:
  - I/O to read image bytes from disk or network
  - Encoding image bytes (e.g., base64) or writing temporary files
  - Calling external services (e.g., image hosting or CDN APIs)
  - Logging or emitting metrics
- Any such side effects are implementation-specific and must be documented by the subclass/renderer.

## Implementation guidance for subclasses:
- Override render(self) to produce the final presentation artifact for the Image item.
- Read image data from the content dict keys listed above; do not assume additional attributes exist.
- Prefer returning deterministic, self-contained representations (or document any required external dependencies).
- Avoid mutating self.content or other instance attributes during rendering unless the renderer's API explicitly allows it.
- Document renderer-specific error handling: whether the renderer raises on missing resources, returns a fallback placeholder, or embeds an error indicator in the returned representation.

