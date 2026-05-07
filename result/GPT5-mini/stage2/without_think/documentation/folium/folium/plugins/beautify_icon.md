# `beautify_icon.py`

## `folium.plugins.beautify_icon.BeautifyIcon` · *class*

*No documentation generated.*

### `folium.plugins.beautify_icon.BeautifyIcon.__init__` · *method*

## Summary:
Initialize a BeautifyIcon instance: call parent initializers, set the element name, and build a normalized options dict on self.options from the provided parameters.

## Description:
This constructor runs when a BeautifyIcon object is created (during object construction in user code or library code that builds icons). It performs construction-time initialization by delegating to parent constructors (super().__init__()), setting the element name, and preparing a canonical options dictionary suitable for later serialization to JavaScript or inclusion in a map object.

Why this logic lives in __init__:
- Centralizes the mapping of constructor arguments into the object's options so instances are ready-to-use immediately after construction.
- Delegates key normalization and None-filtering to folium.utilities.parse_options so normalization behavior is consistent across components and the constructor remains concise.

Known callers / call context:
- Any code that instantiates BeautifyIcon (user scripts, examples, or other library code). This method is invoked at construction-time, before the instance is added to a map or used for rendering.

## Args:
    icon (Any, optional)
        Forwarded to the options as "icon" (after camelCasing). Default: None.

    icon_shape (Any, optional)
        Forwarded to the options as "iconShape" (after camelCasing). Default: None.

    border_width (int, optional)
        Forwarded as "borderWidth". Default: 3.

    border_color (str, optional)
        Forwarded as "borderColor". Default: "#000".

    text_color (str, optional)
        Forwarded as "textColor". Default: "#000".

    background_color (str, optional)
        Forwarded as "backgroundColor". Default: "#FFF".

    inner_icon_style (str, optional)
        Forwarded as "innerIconStyle". Default: "".

    spin (bool, optional)
        Forwarded as "spin". Default: False.

    number (Any, optional)
        When provided (not None), two controlled behaviors occur:
        - The option "isAlphaNumericIcon" is set to True.
        - The option "text" is set to this value.
        When number is None, "isAlphaNumericIcon" is set to False and "text" is omitted (because parse_options removes keys whose value is exactly None).
        Default: None

    **kwargs
        Additional arbitrary options forwarded to parse_options. Keys will be camelCased and entries whose value is exactly None will be omitted.

Notes on argument handling:
- No further validation/coercion is performed here; parse_options performs camelCasing and the constructor places values into self.options for downstream use.

## Returns:
    None
    (Constructor only initializes instance state.)

## Raises:
    - No explicit raises in this method. However, exceptions from called routines can propagate:
        - Exceptions from super().__init__ (parent initialization).
        - Exceptions from folium.utilities.parse_options (for example AttributeError/TypeError if non-string keys are provided or camelize fails).
    - Under typical usage with string keys and valid values, no exception is expected.

## State Changes:
    Attributes READ:
        - None (this method does not access any existing self.<attr> attributes).

    Attributes WRITTEN:
        - self._name: set to "BeautifyIcon".
        - self.options: set to the dict returned by parse_options(...). Characteristics of self.options after the call:
            * Keys are camelCase forms of the constructor parameter names and any **kwargs keys (as produced by camelize within parse_options).
            * Values are the same objects passed into the constructor (no coercion).
            * Any entry whose value is exactly None is removed by parse_options.
            * The boolean "isAlphaNumericIcon" is always present because it is set to the boolean expression (number is not None). It will be True when number is provided, or False when number is None.
            * The "text" key is present only when number is not None (because text=number; parse_options will omit text when number is None).

## Constraints:
    Preconditions:
        - Caller should provide option names as normal keyword identifiers (strings). Supplying unusual non-string keys via **kwargs may lead to exceptions during normalization.
        - If an option should be omitted, pass value None (parse_options removes keys with value exactly None).

    Postconditions:
        - self._name == "BeautifyIcon".
        - self.options is a dict with camelCased keys and the provided values (except entries whose value was None are omitted).
        - self.options["isAlphaNumericIcon"] exists and equals (number is not None).
        - If number is not None, self.options["text"] == number; otherwise "text" is not present in self.options.

## Side Effects:
    - Calls super().__init__(), so any side effects from parent constructors (registration, attribute initialization, template setup) may occur.
    - Calls folium.utilities.parse_options (a pure in-memory transformation: camelCasing and removal of None-valued entries). parse_options itself performs no I/O or network calls.
    - No direct I/O, network access, or mutation of objects outside self is performed by this method.

