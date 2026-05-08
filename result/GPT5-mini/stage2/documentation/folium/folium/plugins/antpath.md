# `antpath.py`

## `folium.plugins.antpath.AntPath` · *class*

*No documentation generated.*

### `folium.plugins.antpath.AntPath.__init__` · *method*

## Summary:
Initializes an AntPath layer by validating and storing the provided locations (via the BaseMultiLocation initializer), setting the element name, and constructing a canonical Leaflet-style options dictionary for the animated "ant path" with sensible defaults and plugin-specific overrides.

## Description:
Known callers and typical context:
- Instantiated directly by application or library code that creates an animated path layer to add to a folium Map (e.g., map.add_child(AntPath(...))).
- Constructed during map-building or layer-creation pipelines whenever an animated polyline-style visual is required.
- Lifecycle stage: called during object construction; the instance is fully configured after __init__ returns and ready to be added to a Map or serialized for rendering.

Why this logic is in __init__:
- Initialization centralizes state setup required for rendering and serialization: validated locations, optional Popup/Tooltip children (handled by BaseMultiLocation), and the options dict that will be embedded into the frontend Leaflet plugin template.
- Separating this logic into the constructor ensures the object invariants (self.locations and self.options) are established immediately after instantiation and avoids duplicating option-defaulting logic elsewhere.

## Args:
    locations (iterable):
        Required. Any iterable structure accepted by BaseMultiLocation.validate_locations (e.g., a list of [lat, lon] pairs or nested iterables). This value is validated and normalized by BaseMultiLocation.__init__ and assigned to self.locations. Preconditions and normalization behavior follow validate_locations (TypeError for non-iterables, ValueError for empty/invalid coordinates).

    popup (optional):
        Default: None.
        If provided and not already a Popup instance, BaseMultiLocation.__init__ will wrap popup with Popup(str(popup)) and add it as a child to this element.

    tooltip (optional):
        Default: None.
        If provided and not already a Tooltip instance, BaseMultiLocation.__init__ will wrap tooltip with Tooltip(str(tooltip)) and add it as a child.

    **kwargs (optional):
        Arbitrary style/control options. Recognized plugin-specific keys (snake_case names accepted) and their defaults:
        - paused (bool): whether the ant animation starts paused. Default False.
        - reverse (bool): whether the animation runs in reverse. Default False.
        - hardware_acceleration (bool): enable hardware acceleration. Default False. (becomes "hardwareAcceleration")
        - delay (int): animation delay in milliseconds. Default 400.
        - dash_array (list or str): dash pattern for the path. Default [10, 20]. (becomes "dashArray")
        - weight (int|float): stroke width. Default 5.
        - opacity (float): stroke opacity (0.0–1.0). Default 0.5.
        - color (str): stroke color (CSS/hex). Default "#0000FF".
        - pulse_color (str): pulse overlay color (CSS/hex). Default "#FFFFFF". (becomes "pulseColor")

        Additional kwargs are forwarded to path_options(line=True, **kwargs) which normalizes and supplies canonical Leaflet-style keys (camelCase) and defaults for common path properties (e.g., smoothFactor, noClip, stroke, fill, fillColor, etc.). path_options expects string-like keys; values should be JSON-serializable if the returned options will be serialized for the frontend.

## Returns:
    None (constructor). The method's effect is to mutate the instance state described under State Changes.

## Raises:
    Exceptions propagated from called routines:
    - TypeError:
        - If locations is not iterable or validate_locations raises TypeError (propagated from BaseMultiLocation during super().__init__).
        - If popup/tooltip string coercion triggers a TypeError (rare).
    - ValueError:
        - If validate_locations rejects locations (e.g., empty input or invalid coordinate shapes).
    - Exceptions from Popup/Tooltip constructors or MacroElement.add_child (if popup/tooltip provided and their constructors raise).
    - Any exception from path_options (rare; typically from invalid kwarg key types passed to camelize) will propagate.
    Note: kwargs.pop(...) calls always supply default values, so they will not raise KeyError.

## State Changes:
    Attributes READ:
        - None of this instance's attributes are read before they are written; the method delegates to BaseMultiLocation.__init__ which may read/establish MacroElement internals. The method does read the local kwargs mapping but not any pre-existing self attributes.

    Attributes WRITTEN or AFFECTED:
        - self._name: set to the string "AntPath".
        - self.options: created by calling path_options(line=True, **kwargs) and then updated with plugin-specific keys (see Args). The final dict uses canonical camelCase option names expected by the frontend plugin.
        - self.locations and children (Popup/Tooltip): established by BaseMultiLocation.__init__ called via super().__init__(...). That call assigns self.locations (validated/normalized) and may add Popup/Tooltip children if popup/tooltip were provided.

## Constraints:
    Preconditions:
        - locations must be an input acceptable to BaseMultiLocation/validate_locations (iterable of coordinate pairs or nested iterables).
        - Keys supplied in kwargs should be string-like names; values intended for frontend should be JSON-serializable.
        - Typical types for plugin keys should match the documented types in Args (e.g., paused/reverse/hardware_acceleration bools, delay int, color strings).

    Postconditions:
        - After return:
            - self._name == "AntPath"
            - self.locations contains the validated/normalized locations (invariants guaranteed by BaseMultiLocation).
            - self.options is a dict containing a canonical set of Leaflet-style keys from path_options(line=True, **kwargs) with plugin-specific keys (paused, reverse, hardwareAcceleration, delay, dashArray, weight, opacity, color, pulseColor) set to either user-supplied values (if provided in kwargs) or the documented defaults.
            - If popup or tooltip were provided, corresponding Popup/Tooltip children have been added to the element (via BaseMultiLocation.__init__).

## Side Effects:
    - Calls BaseMultiLocation.__init__(locations, popup=..., tooltip=...), which:
        - Validates and normalizes locations and assigns self.locations.
        - May add Popup and Tooltip children to self via self.add_child(...).
    - Calls path_options(line=True, **kwargs) to create a base options dict (no global state change; pure function).
    - Mutates the local kwargs mapping by popping plugin-specific keys (paused, reverse, hardware_acceleration, delay, dash_array, weight, opacity, color, pulse_color). This consumes those keys from the kwargs local dict (caller-visible only within this function; does not affect external callers).
    - No I/O, network calls, or changes to global state occur in this method itself.

