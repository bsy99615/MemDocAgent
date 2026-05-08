# `float_image.py`

## `folium.plugins.float_image.FloatImage` · *class*

## Summary:
A lightweight MacroElement subclass that captures configuration for a floating image overlay: it stores an image reference, bottom/left offsets, and an arbitrary dictionary of styling options (css) for later rendering by the host rendering pipeline.

## Description:
FloatImage exists to represent the data needed to render an image that "floats" over a map or other rendered surface. It does not itself perform rendering in the supplied source; instead it records the configuration that a rendering layer (the branca/folium rendering pipeline or a consumer of MacroElement instances) will use to produce the final HTML/CSS/JS.

Typical scenarios when to instantiate:
- You want to add a non-map-tiled image (e.g., logo, badge, or legend) positioned relative to the map container and let the existing rendering pipeline convert the stored information to HTML/CSS.
- You need a simple object to carry an image reference and offset/style metadata into a template-based renderer that processes MacroElement instances.

Known callers/factories:
- Instances are normally created by application code using the class constructor and then attached to a Map or other MacroElement via the host library's APIs (for example, Map.add_child or equivalent attachment methods provided by folium/branca). The class itself does not implement map-attachment helpers beyond inheriting MacroElement behavior.

Responsibility boundary:
- FloatImage's responsibility is storing configuration only. It does not validate image contents, fetch remote resources, or perform rendering. Those tasks are the responsibility of the rendering pipeline that consumes MacroElement instances.

## State:
Class-level attributes:
- _template (jinja2.Template)
  - Type: jinja2.Template
  - Value in source: constructed at class definition time with no template source (Template() called with empty contents).
  - Invariant: _template is always a Template instance on the class.

Instance attributes created by __init__:
- _name (str)
  - Value: "FloatImage"
  - Invariant: constant identifier for the element type.

- image (any)
  - Type/Typical: commonly a str (URL or data URI) but code accepts any type.
  - Constraint: required positional argument; no validation or transformation is performed.
  - Invariant: after __init__, instance.image equals the passed value.

- bottom (int|str)
  - Default: 75
  - Typical meaning: vertical offset from the bottom of the container, expressed as pixels (int) or any CSS length string (e.g., "10px", "5%").
  - Constraint: no validation; callers should supply values meaningful to the renderer.
  - Invariant: after __init__, instance.bottom equals the passed value or 75.

- left (int|str)
  - Default: 75
  - Typical meaning: horizontal offset from the left of the container, expressed as pixels (int) or CSS length string.
  - Constraint: no validation.
  - Invariant: after __init__, instance.left equals the passed value or 75.

- css (dict)
  - Type: dict[str, any]
  - Value: a dictionary capturing all additional named keyword arguments passed to __init__ (kwargs).
  - Constraint: stored verbatim; if no kwargs supplied, css is an empty dict.
  - Intended use: carry styling keys or arbitrary metadata to be used by the renderer.

Class invariants (post-__init__):
- _name is "FloatImage".
- _template is a jinja2.Template instance.
- image, bottom, left, and css attributes are present on every instance after construction.

## Lifecycle:
Creation:
- Constructor signature: FloatImage(image, bottom=75, left=75, **kwargs)
  - image: required (no enforced type)
  - bottom: optional (default 75)
  - left: optional (default 75)
  - kwargs: any additional named options; captured into css dict

- Behavior during construction:
  1. Calls MacroElement.__init__ via super().__init__().
  2. Sets self._name = "FloatImage".
  3. Stores the provided image, bottom, left on the instance.
  4. Stores kwargs in self.css as a dict.

Usage:
- Typical sequence:
  1. Instantiate FloatImage with image and optional offsets/styles.
  2. Attach the instance to a Map or container using the host library's attachment API (e.g., Map.add_child or equivalent). The host's rendering pipeline will read instance attributes and class _template to produce output.
  3. No additional instance methods are required to prepare the object for rendering.

Destruction / cleanup:
- No explicit cleanup is implemented. Instances rely on normal Python garbage collection.
- There is no context-manager protocol, close(), or other resource-release methods on FloatImage in the provided source.

## Method Map:
flowchart LR
    Caller --> Init[FloatImage.__init__(image, bottom=75, left=75, **kwargs)]
    Init --> SuperInit[MacroElement.__init__()]
    Init --> SetName[_name = "FloatImage"]
    Init --> StoreImage[self.image = image]
    Init --> StoreBottom[self.bottom = bottom]
    Init --> StoreLeft[self.left = left]
    Init --> StoreCSS[self.css = kwargs]
    ClassLevel[_template: jinja2.Template(empty source)] -. available .-> Init

Notes: The class defines no other instance methods; interactions are via its attributes and inherited MacroElement behavior.

## Raises:
- __init__ does not explicitly raise exceptions in the provided source.
- Possible exceptions:
  - Errors raised by MacroElement.__init__ (super().__init__) — behavior depends on MacroElement implementation and is not specified here.
  - Errors from constructing the class-level jinja2.Template at import/class-definition time if Template construction fails (in the supplied source the Template is created with empty input, which typically does not raise).
- No validation errors are thrown for invalid types or values of image, bottom, left, or kwargs — callers must ensure their values are appropriate for the renderer.

## Example:
1) Instantiate an overlay descriptor:
   - Provide an image reference (for example, a URL or a base64 data URI), and optionally override offsets and provide style options.
   - Example instantiation (conceptual): FloatImage("https://example.com/logo.png", bottom=10, left="5%", opacity=0.8)
     - After this call:
       - instance.image == "https://example.com/logo.png"
       - instance.bottom == 10
       - instance.left == "5%"
       - instance.css == {"opacity": 0.8}

2) Attach and render:
   - Use the host library's Map or MacroElement attachment API to add the instance to the render tree (for example, Map.add_child(instance) in the folium API).
   - The rendering pipeline reads instance._template and the instance attributes to generate the final display.

3) Inspect:
   - Access instance.image, instance.bottom, instance.left, and instance.css to examine the stored configuration prior to attaching or rendering.

Implementation note:
- To reproduce this class from scratch: subclass the MacroElement base class, create a class-level _template by instantiating jinja2.Template (the supplied source uses an empty template), implement __init__ to call super().__init__(), set self._name, and assign the constructor arguments to the attributes described above.

### `folium.plugins.float_image.FloatImage.__init__` · *method*

## Summary:
Initializes the FloatImage plugin instance by recording the provided image reference and positioning/CSS parameters on the instance.

## Description:
- Known callers and context:
    - This method is invoked when a FloatImage is instantiated (for example, by user code that creates a FloatImage and then adds it to a map). There are no calls or validations inside this method; instantiation is the lifecycle stage where the plugin's initial state is created.
- Rationale for being a separate method:
    - This is the class constructor responsible for creating a usable, consistent object state. Keeping this initialization logic in __init__ centralizes attribute assignment and makes subsequent rendering/templating logic depend on a well-defined instance state rather than ad-hoc initialization elsewhere.

## Args:
    image (Any):
        - The value assigned to self.image with no validation performed by this method.
        - Accepts any Python value; typical use is a URL, file path, data URI, or other image reference, but the constructor does not enforce or inspect format.
    bottom (int or float, optional):
        - Distance in pixels (or other units interpreted by consuming code/CSS) from the bottom edge where the image will float.
        - Defaults to 75.
        - No type checking is performed; any value will be assigned as-is.
    left (int or float, optional):
        - Distance in pixels (or other units interpreted by consuming code/CSS) from the left edge where the image will float.
        - Defaults to 75.
        - No type checking is performed; any value will be assigned as-is.
    **kwargs:
        - Arbitrary keyword arguments captured into a dict and stored on self.css.
        - Intended to represent CSS property names/values or other configuration used later during rendering, but this constructor does not validate keys or values.

## Returns:
    None
    - This is an initializer; it does not return a value.

## Raises:
    - None explicitly raised by this method.
    - Any exception raised would come from Python interpreter-level errors (e.g., memory errors) but there are no explicit checks or raises here.

## State Changes:
- Attributes READ:
    - None directly read from self (the method does not inspect existing instance attributes).
- Attributes WRITTEN:
    - self._name: set to the string "FloatImage".
    - self.image: set to the passed image argument.
    - self.bottom: set to the passed bottom argument (or default).
    - self.left: set to the passed left argument (or default).
    - self.css: set to a dict containing any passed keyword arguments.

## Constraints:
- Preconditions:
    - No preconditions enforced by the constructor; callers should supply meaningful values for image/bottom/left/kwargs for correct downstream behavior.
- Postconditions:
    - After calling __init__, the instance will have _name, image, bottom, left, and css attributes populated as described under "Attributes WRITTEN".
    - No normalization, validation, or type conversion is performed; values are preserved exactly as passed.

## Side Effects:
    - Calls super().__init__(), which initializes the superclass (MacroElement) internal state; any side effects from that call are delegated to the superclass and not performed here directly.
    - No I/O, no network calls, and no mutations to objects other than setting attributes on self.

