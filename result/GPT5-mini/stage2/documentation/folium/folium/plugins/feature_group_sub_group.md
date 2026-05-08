# `feature_group_sub_group.py`

## `folium.plugins.feature_group_sub_group.FeatureGroupSubGroup` · *class*

## Summary:
Represents a Folium layer-like wrapper that references an existing parent feature group and ensures the Leaflet featuregroup.subgroup plugin JavaScript is registered when the element is rendered.

## Description:
This class is a small plugin-style Layer that combines two responsibilities:
- Hold a reference to an existing group-like object (the parent FeatureGroup or LayerGroup), allowing higher-level code or templates to treat this instance as a logical subgroup of that parent.
- Declare and register the required frontend resource (leaflet.featuregroup.subgroup.js) via the JSCSSMixin so the Leaflet plugin is included in the Figure header at render time.

When to instantiate:
- Instantiate when you want to represent or manage a subgroup tied to an existing group object and ensure the client-side plugin is available in the generated HTML.
- Typical usage is by application code that organizes vector features into nested or labeled subgroups and attaches those subgroup objects to a Map/Figure. No internal factory is required — instantiate directly.

Motivation / responsibility boundary:
- Responsibility: maintain a lightweight association to a parent group and register the necessary JavaScript dependency. The class does not itself implement drawing or subgroup manipulation logic; it only provides the metadata and resource registration hook needed by Folium's rendering pipeline and by any templates that reference the stored group.
- Boundary: It delegates rendering/resource registration to JSCSSMixin and metadata handling (layer name / overlay / control / show flags) to Layer. It does not validate the type or capabilities of the provided group object.

## State:
Class attributes:
- _template (jinja2.Template)
    - Type: jinja2.Template
    - Value: an empty Template instance in the source. There is currently no template body declared in this class.
    - Invariant: exists as a class-level template object; subclasses could override to provide markup.

- default_js (list[tuple[str, str]])
    - Type: list of (name, url) pairs
    - Value: contains a single entry named "featuregroupsubgroupjs" pointing to the leaflet.featuregroup.subgroup plugin URL.
    - Purpose: Declared resources that JSCSSMixin will register on the Figure header at render time.
    - Invariant: should remain an iterable of 2-tuples; JSCSSMixin expects (name, url) pairs.

Instance attributes (set by __init__ and inherited initializers):
- _group
    - Type: object (no runtime type enforcement)
    - Description: The parent group object passed into the constructor. The code stores this reference as-is for later use by templates, renderers, or external code.
    - Valid values: any Python object; typically a folium FeatureGroup or LayerGroup-like object in intended usage, but not enforced by this class.
    - Invariant: the attribute refers to the same object for the lifetime of the instance unless modified by user code.

- _name
    - Type: str
    - Value: "FeatureGroupSubGroup" (constant assigned in __init__)
    - Purpose: internal identifier used by this class; may be used by inherited name-resolution mechanisms if needed.
    - Invariant: fixed to the literal string "FeatureGroupSubGroup" after construction.

Inherited instance attributes (from Layer.__init__ call):
- layer_name (str)
    - Set from the constructor parameter name if provided, otherwise resolved by calling self.get_name() through Layer's initialization process.
    - Purpose: public identifier used by parent containers or UI layer controls.

- overlay (bool), control (bool), show (bool)
    - Booleans passed through from constructor parameters; control whether the layer is treated as an overlay, whether it appears in UI layer controls, and whether it is visible by default.
    - Defaults: overlay=True (per this class's signature), control=True, show=True.
    - Invariant: should be boolean values for logical correctness.

Class invariants:
- _name == "FeatureGroupSubGroup" after __init__ completes.
- default_js contains the plugin entry which JSCSSMixin will register upon render.
- The instance retains a direct reference to the provided group object in _group.

## Lifecycle:
Creation:
- Constructor signature: FeatureGroupSubGroup(group, name=None, overlay=True, control=True, show=True)
    - Required: group (no validation)
    - Optional: name (str) — if None, Layer.__init__ will attempt to resolve a name by calling get_name() on the instance (this resolution is implemented by an ancestor; if get_name is missing or raises, that exception propagates).
    - Optional booleans: overlay (default True), control (default True), show (default True).

Typical usage sequence:
1. Instantiate with an existing group object:
   - Provide the parent group as the first argument (stored into _group).
   - Optionally provide a name and the overlay/control/show flags.
2. Add the instance to a Figure/Map element tree (for example via add_child on a Figure or Map) so it becomes part of the rendering tree.
3. When the Figure/Map rendering process reaches this element:
   - JSCSSMixin (mixed into this class) will execute during rendering and register each entry in default_js with the Figure.header (ensuring the external plugin JS is included in the HTML head).
   - Rendering then proceeds to any further Element rendering steps (delegated to super().render via the mixin chain).
4. Consumers or templates may access instance._group to read or manipulate the referenced parent group.

Destruction / cleanup:
- The class defines no explicit cleanup API. Resource registration (default_js) is performed once when the element is rendered; removing registered header links or removing the instance from a Figure is the responsibility of the Figure/header API or caller code.

Sequencing requirements:
- To successfully register JS resources at render time, the instance must be attached to a Figure (JSCSSMixin asserts that get_root() returns a Figure during render).
- If name is omitted at construction, get_name() must be available on the class/ancestor to avoid an error from Layer.__init__.

## Method Map:
flowchart LR
    A[Caller -> FeatureGroupSubGroup(group, name, overlay, control, show)] --> B[Layer.__init__ runs (sets layer_name, overlay, control, show)]
    B --> C[FeatureGroupSubGroup.__init__ assigns _group and _name]
    C --> D[Instance ready to be attached to Figure/Map]
    D --> E[Figure/Map rendering process reaches element]
    E --> F[JSCSSMixin.render: get_root() -> assert Figure]
    F --> G[for (name,url) in default_js -> register JavascriptLink on Figure.header]
    G --> H[continue Element rendering via super().render()]
    H --> I[Client-side HTML includes plugin JS and any rendered markup/template output]

(Note: this class does not define its own render method; it participates in the inherited Element/JSCSSMixin render pipeline.)

## Raises:
- __init__:
    - No explicit raises in this class body. However:
        - Exceptions from Layer.__init__ may propagate (for example, if name is None and the ancestor get_name() is missing or raises).
- render (indirect via JSCSSMixin):
    - JSCSSMixin.render will raise AssertionError if the element is not attached to a Figure (i.e., get_root() does not return a Figure). Any other exceptions raised during the creation of JavascriptLink/CssLink or Figure.header.add_child will propagate.

## Example:
- Creation and typical sequence (illustrative, not prescriptive API calls):
    1. Prepare or obtain an existing group object (for example, a FeatureGroup or LayerGroup instance).
    2. Instantiate the subgroup wrapper:
       - subgroup = FeatureGroupSubGroup(existing_group, name="My Subgroup", overlay=True, control=True, show=True)
    3. Add the subgroup instance to a Figure or Map so it becomes part of the rendering tree.
    4. When the Figure/Map is rendered, the leaflet.featuregroup.subgroup JavaScript URL declared in default_js will be added to the HTML document head automatically by the JSCSSMixin before element markup is emitted.
    5. Access subgroup._group later if application logic or templates need to enumerate or modify the referenced parent group.

Notes and best practices:
- The class stores the provided group as-is and performs no validation; callers should pass a group-like object consistent with downstream uses.
- If you expect the class to supply rendering markup or behavior beyond registering JS, consider subclassing and providing a non-empty _template or additional methods.
- Avoid relying on internal attribute names (_group, _name) from outside code unless necessary — treat them as implementation details that may change in future releases.

### `folium.plugins.feature_group_sub_group.FeatureGroupSubGroup.__init__` · *method*

## Summary:
Initializes the instance by delegating layer metadata setup to the Layer ancestor and then storing the provided parent group reference and a fixed internal identifier ("FeatureGroupSubGroup").

## Description:
Known callers and call context:
- Constructed directly by application code or higher-level helpers when a developer needs a lightweight wrapper that represents a logical subgroup tied to an existing group-like object (typically a FeatureGroup or LayerGroup) and participates in Folium's rendering/resource registration pipeline.
- Lifecycle stage: object construction time, before the instance is attached to a Figure/Map. After construction the instance is expected to be added to the rendering tree so that JSCSSMixin and Layer behaviors are applied at render time.

Rationale for separate method:
- Delegation to Layer.__init__ centralizes shared layer initialization (name resolution and overlay/control/show handling) in the ancestor class rather than duplicating that logic.
- The subclass-specific responsibilities are minimal (storing the parent group reference and setting a class-specific internal name) and are clearly separated into this initializer for readability and single-responsibility.

## Args:
    group (object):
        Positional required argument. The parent group object to reference from this subgroup wrapper. The method stores this object as-is in self._group. No runtime type checking or validation is performed; passing None is allowed syntactically but may be semantically invalid for downstream code that expects a group-like object.
    name (str | None, optional):
        Passed through to Layer.__init__ to be used as the public layer name. If None, ancestor initialization may derive a name via an instance method (for example, get_name()). Default: None.
    overlay (bool, optional):
        Passed through to Layer.__init__. Indicates whether this layer should be treated as an overlay. Default: True.
    control (bool, optional):
        Passed through to Layer.__init__. Indicates whether this layer should be included in layer control UI. Default: True.
    show (bool, optional):
        Passed through to Layer.__init__. Indicates whether this layer is visible by default. Default: True.

## Returns:
    None
    - As with all Python initializers, the method returns None. The observable effect is the mutation of the instance state (see State Changes).

## Raises:
    - This method's body does not explicitly raise exceptions.
    - Any exception raised by Layer.__init__ (the super() call) will propagate to the caller. Examples include errors from name resolution performed by ancestor initialization or other validation implemented by Layer.
    - No additional exceptions are raised by the attribute assignments in this method.

## State Changes:
Attributes READ:
    - Potential implicit read via ancestor initialization: if name is None, Layer.__init__ may call an instance method (e.g., get_name()) on self; that method may read instance state.
    - The initializer's body itself does not read any specific self.<attr> attributes before writing.

Attributes WRITTEN:
    - self._group: assigned the exact object provided via the group argument.
    - self._name: assigned the literal string "FeatureGroupSubGroup".
    - Attributes set by the super() call (Layer.__init__), which are not defined in this method but are initialized as part of ancestor initialization. This method passes name, overlay, control, and show to the ancestor so those metadata attributes are established by Layer.__init__.

## Constraints:
Preconditions:
    - The caller must supply the group positional argument (the function signature enforces a positional parameter). The value may be None but is not validated here.
    - If name is omitted (None), any instance-level method relied upon by Layer.__init__ for name derivation (for example, get_name()) must be implemented and must not raise, otherwise Layer.__init__ may raise an exception.

Postconditions:
    - After successful completion:
        * self._group refers to the provided group argument (identity preserved).
        * self._name equals "FeatureGroupSubGroup".
        * Layer.__init__ has been executed with the supplied name, overlay, control, and show values; the instance has the layer metadata initialized according to the ancestor's implementation.
        * The instance is ready to be attached to a Figure/Map for rendering and resource registration via JSCSSMixin.

## Side Effects:
    - No I/O (file, network) or global state modifications occur in this method.
    - Calls into Layer.__init__ may invoke instance methods and mutate additional attributes as part of ancestor initialization.
    - Only the instance (self) is mutated by this method's body (plus any mutations performed by Layer.__init__).

