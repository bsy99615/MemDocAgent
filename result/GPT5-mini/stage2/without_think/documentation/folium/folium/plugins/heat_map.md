# `heat_map.py`

## `folium.plugins.heat_map.HeatMap` · *class*

*No documentation generated.*

### `folium.plugins.heat_map.HeatMap.__init__` · *method*

## Summary:
Initialize a HeatMap plugin instance by normalizing and validating the supplied point data, setting plugin metadata via the Layer constructor, and storing normalized rendering options on the instance.

## Description:
Known callers and lifecycle:
    - Typically invoked by user code when creating a HeatMap plugin: HeatMap(data, ...).
    - Called during the construction stage of a plugin before the instance is added to a Map. After this __init__ finishes, the instance will hold normalized data and options suitable for later serialization to JavaScript and rendering.
Why this is a separate method:
    - Encapsulates normalization (pandas → ndarray), per-point location validation, NaN checking, and options parsing in one place so the constructor remains a clear sequence: delegate to Layer initialization, normalize input data, validate content, and compute options. This separation centralizes input validation and option normalization logic and makes it easier to test and reuse.

## Args:
    data (iterable of sized/indexable sequences): Required.
        - Each element ("line") must be an indexable/sized object with at least two elements representing latitude and longitude in that order.
        - Typical concrete shapes:
            * [[lat, lon], ...]
            * [[lat, lon, intensity], ...]
            * numpy.ndarray shape (n_rows, n_cols) where first two columns are (lat, lon)
            * pandas.DataFrame with two or more columns (when the module-level pandas handling is available). In that case, the function if_pandas_df_convert_to_numpy will be applied first to obtain an array-like input.
        - The constructor transforms each element into a list whose first two entries are validated floats (via validate_location) and whose subsequent entries (if any) are preserved verbatim (commonly an intensity value).
    name (str | None): Optional. Passed to the Layer base class to identify the layer. Default: None.
    min_opacity (float): Optional. Default: 0.5.
        - Semantic expectation: value in [0.0, 1.0]. Not enforced by this method.
    max_zoom (int): Optional. Default: 18.
        - Semantic expectation: integer zoom level at which circle size is unchanged. Not enforced here.
    radius (int | float): Optional. Default: 25.
        - Semantic expectation: rendering radius in pixels.
    blur (int | float): Optional. Default: 15.
        - Semantic expectation: blur amount used by the heatmap kernel.
    gradient (dict | None): Optional. Default: None.
        - If provided, expected to be a mapping used by front-end rendering (keys and values are passed through to parse_options unchanged). No schema validation is performed here.
    overlay (bool): Optional. Default: True. Passed to the Layer base class.
    control (bool): Optional. Default: True. Passed to the Layer base class.
    show (bool): Optional. Default: True. Passed to the Layer base class.
    **kwargs: Any additional keyword options to be forwarded to parse_options. Special behavior:
        - If kwargs contains a key "max_val", its value is popped and a deprecation warning is emitted because max intensity is now computed automatically. The "max_val" entry is not included in self.options.
        - Remaining kwargs are normalized by parse_options (snake_case → camelCase and removal of None-valued entries) and assigned to self.options.

## Returns:
    None (constructor). On success, instance attributes will have been initialized (see State Changes).

## Raises:
    ValueError:
        - Raised explicitly if any NaN is present among the normalized data points:
            * Trigger: after building self.data, the code checks for NaNs using NumPy (np.any(np.isnan(self.data))). If that expression is True, ValueError("data may not contain NaNs.") is raised.
    Propagated exceptions from helpers (may be raised during input processing or options parsing):
        - TypeError:
            * From validate_location if an input "line" is not sized or not indexable (e.g., missing __len__ or indexing fails); message indicates the input is not sized/indexable.
            * From parse_options/camelize if non-string keys or otherwise invalid option keys are provided.
        - ValueError:
            * From validate_location if a location does not contain exactly two entries or a coordinate cannot be converted to float or is NaN.
        - NameError or AttributeError:
            * Possible if module-level aliases expected by helper utilities are not present (for example, if if_pandas_df_convert_to_numpy or the NaN-checking code expects a numpy alias named np or a pandas alias named pd but those names are not defined). These will propagate from the helper or name resolution.
    Notes:
        - The constructor itself only explicitly raises the ValueError for NaNs; other exceptions listed above are not raised directly here but will propagate from the called utilities if encountered.

## State Changes:
Attributes READ:
    - None of the instance's attributes are read prior to modification by this method (the method does not access self.<attr> for existing values before writing).
    - The method does call external helper functions (validate_location, if_pandas_df_convert_to_numpy, parse_options) which do not read instance state.
Attributes WRITTEN:
    - self._name: set to the literal string "HeatMap".
    - Properties initialized by Layer.__init__ via the super() call: name, overlay, control, show (delegated to the Layer base class constructor).
    - self.data: set to a list of lists; each inner list begins with two floats [lat, lon] (validated and normalized) followed by any remaining elements of the original data row (e.g., intensity).
    - self.options: set to the dict returned by parse_options(min_opacity=..., max_zoom=..., radius=..., blur=..., gradient=..., **kwargs) after the "max_val" deprecation pop and warning.

## Constraints:
Preconditions (what must be true before calling):
    - data must be an iterable of sized/indexable items where each item has at least two elements convertible to float (the first two elements are treated as latitude and longitude). If data is a pandas.DataFrame, the module must support conversion via if_pandas_df_convert_to_numpy (this helper expects pandas to be available under the environment the helper uses).
    - The runtime environment must provide NumPy functions referenced by the constructor (np.any and np.isnan) — otherwise name resolution errors may occur.
    - kwargs should use key names that parse_options (and its camelize call) can accept (typically string keys in snake_case); non-string keys may raise exceptions.
Postconditions (guarantees after calling):
    - self._name == "HeatMap".
    - self.data is a list of lists where each inner list has at least two elements and the first two elements are Python floats (latitude and longitude) that are not NaN.
    - self.options is a dict mapping camelCased option names to their provided (non-None) values; any "max_val" keyword was removed and produced a deprecation warning instead.

## Side Effects:
    - Emits a warning via warnings.warn if a "max_val" keyword was provided in kwargs (this is a non-fatal deprecation notice).
    - No file, network I/O, or mutation of external objects is performed by the constructor itself (all transformations are in-memory).
    - The constructor mutates the instance (self) by setting attributes described above and delegates to Layer.__init__ which may mutate other inherited attributes.

### `folium.plugins.heat_map.HeatMap._get_self_bounds` · *method*

## Summary:
Compute the axis-aligned bounding box of the layer's point data by finding per-coordinate minima and maxima for the first two coordinates, returning a 2x2 list and leaving the object's attributes unchanged.

## Description:
This method iterates over self.data and computes coordinate-wise minima and maxima using the utility functions none_min and none_max. Those helpers treat None as an absent value: if one operand is None the other operand is returned unchanged; if both operands are None the result is None; otherwise the built-in min/max is applied.

Known callers and lifecycle:
    - No direct callers were discovered in the provided snapshot. Conceptually, this method is intended to be invoked by map composition or rendering code that needs the spatial extent of the HeatMap layer (for example: when fitting map bounds to include this layer or when aggregating bounds across multiple layers).
    - It is typically called during map composition or when a caller explicitly requests the layer bounds prior to rendering or serialization.

Why this is a separate method:
    - Encapsulates the bounds-computation and None-handling policy in a single place so callers obtain a consistent bounding-box representation without duplicating iteration or None-checking logic.
    - Keeps construction and rendering paths focused by isolating this utility operation.

## Args:
    None (method uses only self)

## Returns:
    list[list[float | int | None]]:
        A nested 2x2 list of the form:
            [[min_coord0, min_coord1], [max_coord0, max_coord1]]
        - Each entry is either:
            * the numeric minimum/maximum found for that coordinate across all points, or
            * None, if no non-None values were encountered for that coordinate.
        - If self.data is empty, returns [[None, None], [None, None]].
        - Only the first two elements of each point in self.data are inspected; any additional elements (e.g., intensity/weight) are ignored.
        - Coordinate semantics: typically coordinate0 is latitude and coordinate1 is longitude when data represents [lat, lng, ...], but the method itself treats them generically as the first two values of each point.

## Raises:
    IndexError
        - If any element in self.data is a sequence with fewer than two entries, accessing point[0] or point[1] will raise IndexError.
    TypeError (or other comparison errors)
        - If none_min/none_max receive two non-None values that are not mutually comparable (for example mixing int and str), the underlying built-in min/max may raise TypeError. This method does not catch such exceptions; they propagate to the caller.

## State Changes:
    Attributes READ:
        - self.data
    Attributes WRITTEN:
        - None (this method does not modify self attributes)

## Constraints:
    Preconditions:
        - self.data must be an iterable of sequences (lists, tuples, or 1D numpy arrays).
        - Each point must provide at least two accessible entries (point[0], point[1]).
        - When multiple non-None coordinate values exist for the same axis, they must be mutually comparable types (typically numeric).
    Postconditions:
        - The returned value is a 2x2 list where each element is either None or exactly one of the inspected coordinate values from self.data.
        - self.data is unchanged after the call.

## Side Effects:
    - No I/O or network calls are performed.
    - No mutation of external objects occurs; the only observable effect is the returned nested list.

