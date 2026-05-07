# `dual_map.py`

## `folium.plugins.dual_map.DualMap` · *class*

*No documentation generated.*

### `folium.plugins.dual_map.DualMap.__init__` · *method*

## Summary:
Initializes a DualMap plugin by creating two synchronized Map instances laid out side-by-side or stacked and attaches them (and this plugin) to a new Figure. The call configures the two internal maps' CSS sizing and absolute positions and prepares internal lists used to mirror children into the right-side/bottom map.

## Description:
- Known callers and lifecycle:
    - Called when a developer or higher-level factory constructs a DualMap instance (e.g., dual = DualMap(...)). This occurs at the plugin creation stage, before the plugin or its internal maps are added into a larger page, and before any layers or child elements are attached to the maps.
    - Typical usage: instantiate DualMap, then add layers or children to dual.m1 and/or dual using plugin APIs; the plugin later ensures appropriate children are mirrored to the second map.
- Why this is a separate method:
    - Encapsulates all initialization logic required to create two independent Map objects with coordinated sizing/positioning and to register them in a Figure. Keeping this logic in __init__ centralizes layout validation, creation of the two Map instances, and initialization of bookkeeping lists, which would be error-prone and repetitive if scattered elsewhere.

## Args:
    location (sequence[float] | None):
        Starting geographic location (latitude, longitude) passed through to both internal Map instances. May be None to use Map defaults.
    layout (str, optional):
        Visual layout of the two maps. Allowed values:
            - "horizontal" (default): maps are placed side-by-side; each map is 50% width and 100% height.
            - "vertical": maps are stacked; each map is 100% width and 50% height.
    **kwargs:
        Arbitrary keyword arguments forwarded to both internal Map constructors except the following keys are forbidden:
            - "width", "height", "left", "top", "position"
        If any of these forbidden keys are present in kwargs an AssertionError is raised. Remaining kwargs are passed unchanged to the two Map instances.

## Returns:
    None
    - As a Python constructor, no value is returned. The effect is reflected in the modified state of the created DualMap object and the new Figure containing children.

## Raises:
    AssertionError:
        If any forbidden keyword argument is present in kwargs. Exact trigger:
            for key in ("width", "height", "left", "top", "position"):
                assert key not in kwargs, f"Argument {key} cannot be used with  DualMap."
    ValueError:
        If layout is not one of the supported strings ("horizontal", "vertical"). Exact trigger:
            if layout not in ("horizontal", "vertical"):
                raise ValueError("Undefined option for argument `layout`: {}. Use either 'horizontal' or 'vertical'.".format(layout))

## State Changes:
- Attributes READ:
    - None of self's persisted attributes are read before being set by this method. The method does call super().__init__(), which may initialize parent state (not inspected here).
- Attributes WRITTEN:
    - self.m1 (folium.folium.Map): created Map instance for the left or top view.
        - Constructed with parameters:
            - location=location
            - width="50%" if layout == "horizontal" else "100%"
            - height="100%" if layout == "horizontal" else "50%"
            - left="0%"
            - top="0%"
            - position="absolute"
            - plus any remaining **kwargs
    - self.m2 (folium.folium.Map): created Map instance for the right or bottom view.
        - Constructed with parameters:
            - location=location
            - width and height same as m1
            - left="50%" if layout == "horizontal" else "0%"
            - top="0%" if layout == "horizontal" else "50%"
            - position="absolute"
            - plus any remaining **kwargs
    - self.children_for_m2 (list): initialized to an empty list; used to track which children should be mirrored to the second map.
    - self.children_for_m2_copied (list): initialized to an empty list; used to track already-copied child elements for the second map.
    - Additionally, the method instantiates a local Figure and calls:
        - figure.add_child(self.m1)
        - figure.add_child(self.m2)
        - figure.add_child(self)
      These calls modify the Figure object's internal child list(s) and establish parent-child relationships between the Figure, the two Map instances, and this DualMap plugin.

## Constraints:
- Preconditions:
    - kwargs must not contain any of the keys: "width", "height", "left", "top", "position". If any are present the constructor raises AssertionError.
    - layout must be exactly either "horizontal" or "vertical" (strings). Any other value raises ValueError.
    - location may be None or a sequence acceptable to Map; the method does not validate location beyond passing it through to the Map constructors.
- Postconditions:
    - After successful return:
        - self.m1 and self.m2 exist and are folium Map instances configured with the exact CSS size and absolute position strings described above.
        - A new Figure instance exists (local variable) that has self.m1, self.m2 and this DualMap instance added as children.
        - self.children_for_m2 and self.children_for_m2_copied are present as empty lists on the DualMap instance.
        - The DualMap instance is ready to accept children and to coordinate mirroring of children to the second map according to other plugin methods.

## Side Effects:
    - Allocates two Map objects and one Figure object.
    - Mutates the Figure by adding three children (m1, m2, self) via figure.add_child(...).
    - Does not perform any file, network, or other external I/O.
    - Does not return or expose the created Figure object; the Figure's internal child relationships are relied on by the folium/branca element model.

### `folium.plugins.dual_map.DualMap._repr_html_` · *method*

## Summary:
Return an HTML representation for display by delegating to the object's parent Figure; if no parent exists, temporarily attach the DualMap to a new Figure to obtain the HTML, and restore the original parent state.

## Description:
This method is invoked when a DualMap instance is rendered in HTML contexts (for example, by the Jupyter/IPython display machinery which looks for an object's _repr_html_ method). It produces the HTML string that embeds the map(s) and required assets by delegating to the parent's own _repr_html_ implementation.

The logic is separated into its own method because HTML rendering must be delegated to the container Figure (which aggregates scripts, styles, and children). If the DualMap has not been attached to a Figure, rendering requires a temporary, minimal Figure to correctly generate the full HTML bundle; keeping this logic in one place ensures the temporary attach/detach is handled consistently and restores the object's state after rendering.

Known callers and contexts:
- Jupyter/IPython display system (automatic HTML rendering of objects with _repr_html_).
- Any code path that programmatically requests an HTML representation of a DualMap instance (e.g., utilities that embed maps into HTML pages or notebook cells).
- The method forwards any keyword rendering options to the parent's _repr_html_ implementation.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments forwarded unchanged to the parent's _repr_html_ method.
        There are no constraints on keys here — acceptable keys depend on the parent's implementation.

## Returns:
    str
        The HTML string produced by the parent's _repr_html_ method. Typical value is an HTML document fragment that includes necessary <style> and <script> references and the map container markup. If the delegate parent's _repr_html_ returns an empty string, this method returns that same empty string.

## Raises:
    AttributeError
        - If self._parent is None and self.add_to(Figure()) fails to attach the DualMap to the Figure such that self._parent remains None, then the subsequent attempt to call self._parent._repr_html_(...) will raise AttributeError.
        - If self._parent is not None but the parent object does not implement a callable _repr_html_ attribute, attempting to call self._parent._repr_html_(...) will raise AttributeError.
    Any exception raised by the parent's _repr_html_ implementation is propagated unchanged.

## State Changes:
Attributes READ:
    - self._parent

Attributes WRITTEN:
    - self._parent (may be set by self.add_to(Figure()) and is explicitly set to None in the temporary-attach branch).
Notes on net effect:
    - If self._parent is None on entry, the method temporarily sets a parent via self.add_to(Figure()), uses the parent's rendering, and then resets self._parent back to None. The object's public parent relationship is therefore restored to its original value after the call.
    - If self._parent is not None on entry, the method does not modify self._parent.

Other object interactions:
    - Calls self.add_to(Figure()), which is expected to attach the DualMap to the new Figure and establish the parent relationship. The behavior and side effects of add_to depend on the DualMap implementation.
    - Calls self._parent._repr_html_(**kwargs), delegating HTML generation to the parent.

## Constraints:
Preconditions:
    - The DualMap instance must have a working add_to method that, when called with a Figure(), sets self._parent to an object that implements _repr_html_.
    - If self._parent is not None on entry, it must implement a callable _repr_html_ method.
Postconditions:
    - After the method returns, self._parent will be the same value it had before the call (i.e., the method preserves the object's parent state).
    - The returned string equals whatever the parent's _repr_html_ returned for the forwarded kwargs.

## Side Effects:
    - May instantiate a temporary Figure object (branca.element.Figure) when no parent exists.
    - Mutates self._parent during the temporary attach branch (it is set to the new Figure via add_to, then explicitly set back to None).
    - Delegates to the parent's _repr_html_ which may perform additional work (rendering, asset aggregation, I/O-like operations such as reading template files) and may raise exceptions; those effects propagate through this method.

### `folium.plugins.dual_map.DualMap.add_child` · *method*

## Summary:
Adds a child element to the left/top map immediately and records a plan to add (a copy of) that child to the right/bottom map during render, modifying the DualMap's scheduling state.

## Description:
Known callers and lifecycle stage:
- Typically invoked by user code or helper functions when constructing the dual map (e.g., adding layers, markers, or controls). It is used during the "build" stage of map construction before final rendering.
- Called any time a developer wants an element to appear on both panes of the DualMap; the element is added to the first map (m1) immediately and scheduled for copying into the second map (m2) during render().

Why this is a separate method:
- DualMap needs to perform two distinct actions when a child is added: (1) immediately attach the original child to the first map (m1) so it participates in any immediate Map behavior, and (2) record metadata so a deep copy of the child can be attached to the second map (m2) later during render. Encapsulating these steps in a dedicated add_child method centralizes the scheduling logic and prevents callers from having to manage the copy/sync bookkeeping themselves.

## Args:
    child (object): The element to add. Expected to be a folium/Branca element or other object accepted by Map.add_child (commonly a MacroElement or subclass). The object should have any attributes required by Map.add_child and should have a stable ._id used later by render() when copying.
    name (str | None, optional): Optional name passed through to m1.add_child and recorded for m2's future copy. Default: None.
    index (int | None, optional): Optional insertion index passed through to m1.add_child. If None, the method computes an index for m2 as the current length of m2._children and records that value. Default: None.

## Returns:
    None
    - The method does not return a value. Its observable effects are the side effects described below.

## Raises:
    Any exception raised by self.m1.add_child(child, name, index)
        - This method directly calls m1.add_child; any exception that Map.add_child (or the child's methods invoked by that call) raises will propagate.
    Any exception raised while computing len(self.m2._children) if self.m2 or its _children attribute does not support len()
        - Unlikely in normal DualMap instances (m2 is initialized in __init__), but will propagate if encountered.

## State Changes:
Attributes READ:
    - self.m1 (accessed to call m1.add_child)
    - self.m2._children (only when index is None; read via len(self.m2._children))
Attributes WRITTEN / MUTATED:
    - self.children_for_m2: appended with a tuple (child, name, index) recording the plan to add a copy to m2 during render.
    - self.m1: mutated indirectly by the call self.m1.add_child(...); specifically, m1's internal children state will be modified as Map.add_child implements.

## Constraints:
Preconditions:
    - self.m1 and self.m2 must be valid Map instances attached to this DualMap (the DualMap constructor sets these up). If either is missing or malformed, behavior may raise exceptions.
    - self.children_for_m2 must be an existing list (initialized in DualMap.__init__). If replaced with a non-list, append may fail.
    - The provided child should be compatible with Map.add_child (e.g., have any attributes Map.add_child expects, typically a MacroElement-like object). In practice, child should have a stable ._id attribute used later by render().

Postconditions:
    - The provided child has been added to m1 via m1.add_child(child, name, index).
    - The tuple (child, name, index_used_for_recording) has been appended to self.children_for_m2. If index was None on entry, index_used_for_recording equals len(self.m2._children) as evaluated at the time of the call.
    - No copy of the child is created at this time; copies are created (deep_copy) and added to m2 during DualMap.render().

## Side Effects:
    - Mutates m1 by adding the child (delegated to Map.add_child).
    - Mutates DualMap.children_for_m2 by appending scheduling metadata.
    - Does not perform any I/O, network access, or rendering. No external services are called.
    - Does not itself create or attach a copy to m2; that occurs later in render(). Any side effects from Map.add_child (such as registering resources or updating parent pointers) will occur immediately for m1.

### `folium.plugins.dual_map.DualMap.render` · *method*

## Summary:
Renders the DualMap and ensures each child previously added to the first map is deep-copied and added to the second map exactly once, updating the object's copy-tracking state.

## Description:
This method is part of the folium rendering pipeline for DualMap. It is invoked when the DualMap is rendered as part of a Figure or when the parent rendering process calls render on child MacroElement objects (for example, indirectly via DualMap._repr_html_ which ensures the element is attached to a Figure before producing HTML). The method first delegates to its superclass render to perform standard MacroElement rendering, then performs the copy-and-add logic for children that were registered to be mirrored on the second map (self.m2).

This logic is a separate method because copying and attaching children to the second map must occur at render time (after initialization and after the parent/figure render context exists) and requires calling the rendering lifecycle on the copied children. Separating it keeps add_child lightweight (it only registers children for mirroring) and centralizes the copy/render semantics in a single render-time step.

Known callers and invocation context:
- The folium rendering pipeline when a Figure or parent element calls render on its children (e.g., via DualMap._repr_html_ which attaches to a Figure and triggers rendering).
- It is not intended to be called directly by user code except as part of that rendering pipeline.

## Args:
    **kwargs: Mapping[str, Any]
        Forwarded to super().render. These are render-time keyword arguments expected by the MacroElement rendering API (no specific keys are required by DualMap itself).

## Returns:
    None
    The method does not return a value; it performs rendering-side effects on self and on self.m2.

## Raises:
    Any exceptions raised by underlying operations may propagate:
    - Exceptions from deep_copy(child) if the child cannot be deep-copied.
    - Exceptions from self.m2.add_child(child_copy, name, index) if adding the child is invalid.
    - Exceptions from child_copy.render() if rendering the copied child fails.
    The method does not raise new exceptions itself; it allows these underlying errors to propagate.

## State Changes:
    Attributes READ:
        - self.children_for_m2: list of (child, name, index) tuples previously registered via add_child. Each child is inspected and its _id is read.
        - self.children_for_m2_copied: list of original child ids used to check whether a child was already copied.
        - self.m2: the second Map instance where copies are attached.
    Attributes WRITTEN:
        - self.children_for_m2_copied: original child._id values are appended for each child copied during this render invocation.
        - self.m2 (indirectly): mutated by calling self.m2.add_child(...), which modifies m2's internal children collection.
    Other object mutations:
        - New child copy objects are created (via deep_copy) and attached to self.m2.
        - If a copied child is a LayerControl, its reset() method is invoked (mutates the copy).

## Constraints:
    Preconditions:
        - self.m2 must be initialized (the __init__ of DualMap creates self.m2).
        - self.children_for_m2 must be a sequence of tuples (child, name, index) where each child has a unique _id attribute.
        - self.children_for_m2_copied must be a mutable sequence (list) used to track which original children have already been copied.
        - The method should be executed in the rendering phase (after DualMap was added to a Figure or its parent render context is established).
    Postconditions:
        - For every tuple (child, name, index) in self.children_for_m2 that was not previously recorded in self.children_for_m2_copied, there will be a deep copy of child added to self.m2 at the given name and index, child_copy.render() will have been invoked, and child._id will have been appended to self.children_for_m2_copied.
        - Subsequent calls to render will not duplicate already-copied children because their original _id values are recorded in children_for_m2_copied.

## Side Effects:
    - Mutates self and self.m2 (adds children to the second map).
    - Allocates new objects via deep_copy.
    - Calls reset() on copied LayerControl instances to ensure their internal state is appropriate for the second map.
    - Calls render() on each copied child, which may perform additional in-memory processing (template rendering) and may further mutate the child's internal state or its own descendants.
    - No network or filesystem I/O is performed directly by this method; any such I/O would be the result of operations performed by child_copy.render() or other deeper render logic.

### `folium.plugins.dual_map.DualMap.fit_bounds` · *method*

## Summary:
Applies the same fit-bounds instruction to both internal Map instances so each child map will update its viewport to show the provided geographic bounds.

## Description:
This method forwards all positional and keyword arguments it receives to the fit_bounds method of both child Map objects (self.m1 and self.m2). Typical callers and context:
- User code or higher-level library code that configures a DualMap instance and wants both maps to display the same geographic extent (commonly invoked after adding markers or layers and prior to rendering).
- Lifecycle stage: configuration/setup phase of the map-building pipeline; the FitBounds element created by Map.fit_bounds is serialized into each map and executed in the browser when the map is rendered.

Why this is a dedicated method:
- DualMap wraps two independent Map objects; providing a DualMap.fit_bounds convenience method ensures both maps receive identical fit-bounds instructions via a single call, preserving API parity with folium.folium.Map and centralizing forwarding logic.

## Args:
    *args: tuple
        Positional arguments forwarded unchanged to each child Map.fit_bounds call. Typical usage supplies:
        - bounds: any object accepted by Map.fit_bounds (commonly a two-element bounding box [[southWest_lat, southWest_lng], [northEast_lat, northEast_lng]] or an iterable of LatLng-like pairs).
    **kwargs: dict
        Keyword arguments forwarded unchanged to each child Map.fit_bounds call. Map.fit_bounds supports (documented here for clarity):
        - padding_top_left (tuple[float, float] | None, default None): Pixel padding added to top-left when fitting bounds.
        - padding_bottom_right (tuple[float, float] | None, default None): Pixel padding added to bottom-right when fitting bounds.
        - padding (tuple[float, float] | float | None, default None): Global padding (pair or scalar) to apply when fitting bounds.
        - max_zoom (int | None, default None): Maximum zoom level to apply when fitting bounds.
        Note: DualMap.fit_bounds does not validate or coerce these values; they are passed through to Map.fit_bounds as-is.

## Returns:
    None
    - The method does not return a value. Any return values produced by the underlying Map.fit_bounds calls (Map.fit_bounds returns None) are not captured.

## Raises:
    - Propagates any exception raised by the underlying Map.fit_bounds calls without additional handling. Examples include:
        * TypeError or ValueError if the bounds or padding arguments are malformed for FitBounds construction.
        * Exceptions raised by self.m1.fit_bounds or self.m2.fit_bounds during their internal add_child or FitBounds creation steps.
    - If self.m1 or self.m2 are missing (AttributeError), that exception will also propagate.

## State Changes:
    Attributes READ:
        - self.m1
        - self.m2

    Attributes WRITTEN:
        - None on the DualMap object itself (this method does not assign to any self.<attr>).

    Mutations caused (side-effect on child objects):
        - Each child Map (self.m1 and self.m2) will be mutated by its fit_bounds implementation: typically, a FitBounds child element is constructed and added to the map's children collection, changing the child's internal state so the fit instruction is serialized during rendering.

## Constraints:
    Preconditions:
        - self.m1 and self.m2 must be initialized Map instances (created in DualMap.__init__). Calling this method before initialization completes or after attributes have been removed will raise AttributeError.
        - The provided args/kwargs must be acceptable to folium.folium.Map.fit_bounds (see Args). DualMap.fit_bounds performs no validation beyond forwarding.

    Postconditions:
        - Both child maps will have had Map.fit_bounds invoked with the identical arguments; consequently, both maps will include a FitBounds instruction (or equivalent behavior from Map.fit_bounds) that will influence their rendered viewport.
        - No DualMap-level attributes will be changed by this call.

## Side Effects:
    - Mutates the internal state of self.m1 and self.m2 (adds FitBounds children to their element trees).
    - No external I/O, network calls, or interactions with services are performed by this method itself; side effects are limited to in-memory mutations on the child Map objects.

### `folium.plugins.dual_map.DualMap.keep_in_front` · *method*

## Summary:
Delegates marking of one or more objects to be kept visually in front to both underlying Map instances (the left/top and right/bottom maps), causing the same state change on each sub-map.

## Description:
Known callers and context:
    - Intended to be called by client/user code or higher-level library code after creating or adding elements to a DualMap and before rendering.
    - Typical lifecycle stage: configuration stage of a DualMap (after adding layers or controls and before calling render or displaying the map).
    - There are no internal callers in DualMap beyond user code in normal usage; it provides a convenience API so callers do not need to call keep_in_front on each sub-map individually.

Why this is a separate method:
    - Applies the keep-in-front intent consistently to both constituent Map objects (self.m1 and self.m2) with a single call.
    - Encapsulates the delegation logic so users of DualMap do not need to know or manage the two internal Map instances directly.

## Args:
    *args (any): Zero or more objects to be marked to "stay in front".
        - Type: any Python object. The method does not enforce type checking.
        - Typical values: instances representing map elements (e.g., Layer, MacroElement instances).
        - Semantics: the exact arguments are forwarded unchanged to each underlying Map.keep_in_front call. Passing an iterable as a single positional argument will append that iterable object as one entry (it will not be expanded).

## Returns:
    None

## Raises:
    - AttributeError: if self.m1 or self.m2 does not exist or does not expose a keep_in_front attribute (this will occur at call time).
    - Any exception raised by the underlying Map.keep_in_front implementation will propagate unchanged (for example, runtime errors from that method, although the Map implementation does not raise under normal use).

## State Changes:
    Attributes READ:
        - self.m1
        - self.m2
    Attributes WRITTEN:
        - No attributes of self (the DualMap) are modified by this method.
        - Side-effect mutations occur on the sub-maps: each call delegates to m.keep_in_front(*args), which (in the Map implementation) appends the provided objects to m.objects_to_stay_in_front. Thus, self.m1.objects_to_stay_in_front and self.m2.objects_to_stay_in_front are mutated.

## Constraints:
    Preconditions:
        - self.m1 and self.m2 must have been initialized (DualMap.__init__ creates both as Map instances).
        - Each sub-map must implement a keep_in_front method (the normal DualMap initialization ensures this).
    Postconditions:
        - For each positional argument provided, the same object(s) will have been passed to keep_in_front on both self.m1 and self.m2 in the same order.
        - If called with no arguments, no changes are made to either sub-map.
        - If an exception is raised while processing the first sub-map (self.m1), the second sub-map (self.m2) will not be processed and the exception propagates to the caller.

## Side Effects:
    - Mutates internal state of self.m1 and self.m2 (their objects_to_stay_in_front lists are appended to by the delegated calls).
    - No I/O, no network calls, and no interaction with external services occur in this method itself.
    - Exceptions from underlying calls propagate to the caller (no additional error handling is performed).

