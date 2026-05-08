# `time_slider_choropleth.py`

## `folium.plugins.time_slider_choropleth.TimeSliderChoropleth` · *class*

## Summary:
TimeSliderChoropleth is a folium Layer plugin that normalizes GeoJSON input and a time-indexed style dictionary (styledict), computes a deterministic, ordered timeline (timestamps), and stores an initial timestamp index for a client-side time-slider choropleth visualization.

## Description:
This class prepares the server-side state required by the plugin's Jinja2 template and client-side JavaScript to render a choropleth whose styles change over discrete timestamps. It performs input normalization and validation but does not itself render or manipulate the DOM — rendering is handled by folium's template/JS system when the layer is added to a Map.

When to instantiate:
- When you have GeoJSON geographic data and a per-feature mapping of timestamp -> style dictionaries and want to expose a time slider that updates feature styles according to time.
- Typical caller sequence: create TimeSliderChoropleth, then call add_to(map). The folium Map rendering pipeline will use the instance attributes (data, styledict, timestamps, init_timestamp) when generating HTML/JS for the browser.

Motivation / responsibility boundary:
- Validate that styledict is of the expected shape (dict of dicts).
- Normalize GeoJSON input via GeoJson.process_data to ensure consistent data structure for templates.
- Aggregate and sort unique timestamps from styledict entries, applying numeric sort when possible.
- Validate and normalize the initial timestamp index for client-side use.
- The class does not: match styledict keys to GeoJSON features, perform style application, or implement client-side slider logic.

## State:
Public instance attributes created by __init__:
- data
  - Type: dict (normalized GeoJSON-like structure as returned by folium.features.GeoJson.process_data)
  - Description: the GeoJSON data normalized for downstream rendering.
  - Invariant: always set by GeoJson.process_data(GeoJson({}), data) on construction.

- styledict
  - Type: dict[Any -> dict[Any -> dict]]
  - Description: maps a feature identifier (key type depends on how the GeoJSON identifies features) to a dict mapping timestamp keys to style dictionaries.
  - Constraints: must be a dict; each value must also be a dict. Violations raise ValueError in __init__.
  - Note: This class does not verify that keys in styledict correspond to any particular GeoJSON property — the caller must ensure that the keys match the way features will be identified in the client-side rendering (commonly a feature "id" or another unique property).

- timestamps
  - Type: list[str | int]
  - Description: sorted list of all unique timestamp keys gathered from every inner dict in styledict.
  - Sorting rules:
    - The constructor first aggregates timestamp keys into a set.
    - It attempts numeric ordering by calling sorted(..., key=int). If any key cannot be converted to int (TypeError or ValueError), it falls back to lexical sorted(...) order.
  - Invariant: contains unique timestamp keys in deterministic order.

- init_timestamp
  - Type: int
  - Description: normalized index into timestamps indicating the initially-selected timestamp for display.
  - Input constraint: caller may pass a value in the inclusive lower bound and exclusive upper bound range [-len(timestamps), len(timestamps)). Negative values act like Python negative indices and are normalized internally by adding len(timestamps).
  - Postcondition: after __init__, 0 <= init_timestamp < len(timestamps) (unless assertions were disabled by running under python -O, see Raises).

Class-level attributes:
- _template (jinja2.Template)
  - Purpose: Jinja2 template used by folium to generate the HTML/JS for this plugin. In this source the template is present but empty; the template object is required by folium's rendering system.
- default_js
  - Value: [("d3v4", "https://d3js.org/d3.v4.min.js")]
  - Purpose: declares a JavaScript dependency (D3 v4) that the client-side plugin code may use.

Class invariants:
- styledict is a dict whose values are dicts.
- timestamps is the sorted aggregation of keys present in the inner dicts of styledict.
- init_timestamp is (normally) a valid index into timestamps.

## Lifecycle:
Creation:
- Required parameters:
  - data: GeoJSON-like data accepted by folium.features.GeoJson.process_data (e.g., a GeoJSON mapping or other supported input).
  - styledict: dict mapping feature identifiers to timestamp->style dicts.
- Optional parameters (with defaults):
  - name: str | None = None — passed to Layer base class to label this layer.
  - overlay: bool = True — passed to Layer base class.
  - control: bool = True — passed to Layer base class.
  - show: bool = True — passed to Layer base class.
  - init_timestamp: int = 0 — initial timestamp index (may be negative, which indexes from the end).
- Instantiation effect:
  - Calls Layer.__init__ with (name, overlay, control, show).
  - Normalizes data via GeoJson.process_data.
  - Validates styledict shape.
  - Aggregates and sorts timestamp keys.
  - Validates and normalizes init_timestamp.

Usage:
- Typical order:
  1. Construct the plugin: TimeSliderChoropleth(data, styledict, name=..., init_timestamp=...)
  2. Attach to a Map: plugin.add_to(map)
  3. Render the Map (save to HTML or display in a Jupyter notebook). The template/JS will read the instance state and implement the slider behavior.
- There are no additional public methods on this class; the main interaction after creation is via folium's layer management (add_to, Layer controls).

Destruction / cleanup:
- No explicit cleanup API; relies on folium's removal semantics in the rendering pipeline and Python garbage collection. There is no context-manager or close() method.

## Method Map:
flowchart TD
    __init__ --> process_data[GeoJson.process_data(GeoJson({}), data)]
    __init__ --> validate1[assert styledict is dict -> ValueError if not]
    __init__ --> validate2[assert each styledict value is dict -> ValueError if not]
    __init__ --> aggregate[aggregate timestamp keys from all inner dicts]
    aggregate --> sort_try[try numeric sort: sorted(..., key=int)]
    sort_try --> sort_fallback[except -> lexical sorted(...)]
    sort_fallback --> set_timestamps[set self.timestamps]
    set_timestamps --> check_init[assert -len(timestamps) <= init_timestamp < len(timestamps)]
    check_init --> normalize_neg[if init_timestamp < 0: add len(timestamps)]
    normalize_neg --> finalize[set self.init_timestamp]

(Note: the above summarizes the control flow inside __init__. There are no other methods defined in this class.)

## Raises:
- ValueError
  - If styledict is not a dict:
    - Message: "styledict must be a dictionary, got <repr>"
  - If any value in styledict is not a dict:
    - Message: "Each item in styledict must be a dictionary, got <repr>"

- AssertionError
  - Trigger: when init_timestamp is not in the required range [-len(timestamps), len(timestamps)).
  - Message example: "init_timestamp must be in the range [-N, N) but got X" where N == len(timestamps) and X is the provided init_timestamp.
  - Important note: this check uses assert; running Python with optimizations (python -O) disables assertions and therefore will skip this validation. In optimized runs, an invalid init_timestamp could result in an inconsistent instance state. Callers who require guaranteed validation should ensure init_timestamp is in-range prior to construction.

- Edge cases:
  - If styledict contains no timestamp keys across all features (i.e., timestamps == []), then len(timestamps) == 0 and the assertion for init_timestamp will always fail (because there is no valid index into an empty timeline). This raises an AssertionError during construction. Therefore styledict must include at least one timestamp key across its feature entries.

## Example:
Minimal illustrative example tying a GeoJSON feature identifier to a styledict key:

- Minimal GeoJSON (conceptual):
  { "type": "FeatureCollection",
    "features": [
      { "type": "Feature", "id": "feature-1", "geometry": { ... }, "properties": {} }
    ]
  }

- Corresponding styledict:
  {
    "feature-1": {
      "2000": {"fillColor": "#ffffb2", "fillOpacity": 0.6},
      "2001": {"fillColor": "#fecc5c", "fillOpacity": 0.6}
    }
  }

- Usage (pseudocode):
  m = Map(...)
  slider = TimeSliderChoropleth(data, styledict, name="Temporal Choropleth", init_timestamp=0)
  slider.add_to(m)
  # Save or display the map. The plugin's template/JS will use slider.data, slider.styledict,
  # slider.timestamps, and slider.init_timestamp to render a time slider and apply styles over time.

### `folium.plugins.time_slider_choropleth.TimeSliderChoropleth.__init__` · *method*

## Summary:
Initialize the TimeSliderChoropleth plugin instance, validate and normalize inputs, and populate instance state used by the plugin.

## Description:
This initializer is invoked when a TimeSliderChoropleth object is instantiated (for example, when application code or a map-building pipeline constructs the plugin to add it to a folium.Map). It performs the work required to prepare the plugin's runtime state so that subsequent methods can render and animate styled GeoJSON features across timestamps.

The method is an initializer because it must:
- call the parent Layer initializer with control/visibility parameters,
- transform the provided geo-data into the internal representation expected by the plugin,
- validate and normalize the styledict and initial timestamp,
so this logic belongs in __init__ rather than being deferred or inlined elsewhere.

## Args:
    data (any):
        Input passed to GeoJson.process_data. The implementation delegates processing/normalization to GeoJson.process_data and stores the result in self.data. Accepted concrete formats are defined by GeoJson.process_data (not inspected here).
    styledict (dict):
        Required. A mapping whose values must themselves be dictionaries. Each value dictionary is expected to map timestamp keys (strings or values usable as keys) to style dictionaries. Example shape: {feature_id: {timestamp_key: style_dict, ...}, ...}. The initializer validates that styledict is a dict and that each value is a dict; otherwise it raises ValueError.
    name (str | None, optional):
        Passed through to the parent Layer initializer. Defaults to None.
    overlay (bool, optional):
        Passed through to the parent Layer initializer. Defaults to True.
    control (bool, optional):
        Passed through to the parent Layer initializer. Defaults to True.
    show (bool, optional):
        Passed through to the parent Layer initializer. Defaults to True.
    init_timestamp (int, optional):
        Index indicating which timestamp to use initially. Default 0. Negative indices are allowed and are interpreted relative to the end of the sorted timestamps list (Python-like negative indexing). Must satisfy -N <= init_timestamp < N where N is the number of distinct timestamps derived from styledict; otherwise an AssertionError is raised.

## Returns:
    None: As an initializer, it does not return a value; it always returns None implicitly.

## Raises:
    ValueError:
        - If styledict is not a dict: raised with message "styledict must be a dictionary, got {styledict!r}".
        - If any value in styledict.values() is not a dict: raised with message "Each item in styledict must be a dictionary, got {val!r}".
    AssertionError:
        - If init_timestamp is not in the allowed range [-N, N) where N is the number of timestamps extracted from styledict. The assertion message mirrors the code: "init_timestamp must be in the range [-{N}, {N}) but got {init_timestamp}".
    Any exceptions raised by GeoJson.process_data or by the parent Layer.__init__:
        - These may propagate; their types and conditions depend on those implementations (not inspected here).

## State Changes:
Attributes READ:
    - None of this method's behavior depends on pre-existing self.* attributes; it only reads local variables and calls super().__init__.

Attributes WRITTEN:
    - self.data: Assigned to the value returned by GeoJson.process_data(GeoJson({}), data).
    - self.timestamps: Assigned to a sorted list of distinct timestamp keys collected from styledict values.
    - self.styledict: Assigned to the provided styledict (after validation).
    - self.init_timestamp: Assigned to the normalized init_timestamp (converted to non-negative index when a negative index is given).

Additionally, the method calls super().__init__(...), which may mutate parent-class-managed attributes (e.g., name, overlay/control/show state) as implemented by the parent Layer initializer.

## Constraints:
Preconditions:
    - styledict must be a dict whose values are dicts (the method enforces this and raises ValueError on violation).
    - The number of timestamps N inferred from styledict must be such that the provided init_timestamp satisfies -N <= init_timestamp < N. If N == 0 (no timestamps found), the assertion will fail for any init_timestamp.

Postconditions:
    - self.data is set to whatever GeoJson.process_data returns for the given data input and a fresh GeoJson({}) instance.
    - self.timestamps is a list containing the distinct timestamp keys collected from all inner dicts of styledict, sorted. Sorting is attempted numerically by converting keys to int; if conversion raises TypeError or ValueError for any key, fallback lexicographic sorting is used.
    - self.styledict references the user-provided styledict (no deep copy is performed by this initializer).
    - self.init_timestamp is a non-negative integer index within [0, N-1] when N > 0; negative init_timestamp values are normalized to the corresponding positive index.

## Side Effects:
    - Calls super().__init__(name=name, overlay=overlay, control=control, show=show) which may alter object state defined by the parent Layer class.
    - Instantiates a GeoJson({}) and calls GeoJson.process_data with the provided data; any side effects or I/O triggered by those operations depend on their implementations and may propagate exceptions.
    - No direct file, network, or external I/O is performed by this code fragment itself.

