# `utilities.py`

## `folium.utilities.validate_location` · *function*

## Summary:
Validate and normalize a two-element geographic coordinate container into a list of two floats (latitude, longitude), raising clear errors for invalid shapes or non-numeric values.

## Description:
This helper centralizes the input validation and normalization for any folium API that accepts a geographic location (latitude, longitude). Typical callers are constructors or factory functions that accept a location argument and need a normalized numeric pair for downstream code — for example, map initializers and geometry/marker factories (e.g., Map, Marker, Circle). It is implemented as a separate function to enforce a single, consistent validation policy (sizing, indexing support, numeric conversion, NaN checks) and to avoid duplicating error handling across the codebase.

Behavior summary:
- If the incoming value is a NumPy ndarray (checked via the module alias np) or a pandas DataFrame (checked via the module alias pd, if pd is present), the function squeezes singleton dimensions and converts to a Python list.
- The function requires a sized, indexable object of length 2 (e.g., list, tuple, array-like).
- Each of the two elements is converted to float; non-convertible values or NaNs raise ValueError.
- On success, returns a plain Python list of two float values [lat, lon].

## Args:
    location (sized, indexable):
        - Any sized, indexable container representing two coordinates (latitude, longitude).
        - Acceptable concrete types include: list, tuple, and, when available, numpy.ndarray or pandas.DataFrame (these are handled specially by squeezing and converting to list).
        - The function expects exactly two entries (len(location) == 2).
        - Each entry must be convertible to float (e.g., numeric strings like "12.34" are allowed).
        - Interdependencies: if a numpy ndarray or pandas DataFrame is provided, the function will first call the module-level np.squeeze and then .tolist() before further checks. For the pandas branch, the module alias pd must be present and not None for that branch to be evaluated.

## Returns:
    list[float]:
        - A list of two floats corresponding to the supplied coordinates: [float(location[0]), float(location[1])].
        - Always returns exactly two elements on success.
        - The returned floats are guaranteed not to be NaN.

## Raises:
    TypeError:
        - If the input has no __len__ attribute (i.e., is not sized). Trigger condition: not hasattr(location, "__len__").
          Example message: "Location should be a sized variable, for example a list or a tuple, instead got {location!r} of type {type(location)}."
        - If the input does not support indexing (attempt to access location[0] or location[1] raises TypeError or KeyError). Trigger condition: exception raised when evaluating (location[0], location[1]).
          Example message: "Location should support indexing, like a list or a tuple does, instead got {location!r} of type {type(location)}."

    ValueError:
        - If the input length is not exactly 2. Trigger condition: len(location) != 2.
          Example message: "Expected two (lat, lon) values for location, instead got: {location!r}."
        - If either coordinate cannot be converted to float (float(coord) raises TypeError or ValueError). Trigger condition: attempting float(coord) for each coord raises TypeError or ValueError.
          Example message: "Location should consist of two numerical values, but {coord!r} of type {type(coord)} is not convertible to float."
        - If either coordinate converts to a float that is NaN. Trigger condition: math.isnan(float(coord)) is True.
          Example message: "Location values cannot contain NaNs."

## Constraints:
Preconditions:
    - The caller must provide a sized, indexable object representing exactly two values.
    - If relying on the numpy/pandas special-case branch, the module-level aliases used by this function (np for numpy and pd for pandas) must be defined in the module namespace as the expected libraries (or in the case of pd, possibly None to disable the DataFrame check). Otherwise, the code expects those names to exist and refer to the appropriate modules.

Postconditions:
    - The function returns a list of two Python float values.
    - Both returned floats are finite numbers (not NaN). Note: the function does not explicitly check for +/-inf; they will pass through if convertible to float and not NaN.

## Side Effects:
    - No I/O (no files, network, stdout).
    - No mutation of passed-in input objects (the function produces a new list of floats; if numpy/pandas branches convert via .tolist(), that operation creates a Python list but does not mutate the original array/DataFrame).
    - No external service calls or global state changes.

## Control Flow:
flowchart TD
    A[Start: validate_location(location)] --> B{Is location a numpy ndarray?}
    B -- yes --> C[np.squeeze(location).tolist()]
    B -- no --> D{Is pd defined AND location a pandas DataFrame?}
    D -- yes --> C
    D -- no --> E[Proceed with original location]
    C --> E
    E --> F{Has __len__ attribute?}
    F -- no --> G[Raise TypeError: not sized]
    F -- yes --> H{len(location) == 2?}
    H -- no --> I[Raise ValueError: expected two values]
    H -- yes --> J[Try coords = (location[0], location[1])]
    J -- raises TypeError/KeyError --> K[Raise TypeError: not indexable]
    J --> L[For each coord in coords:]
    L --> M{float(coord) succeeds?}
    M -- no --> N[Raise ValueError: not convertible to float]
    M -- yes --> O{math.isnan(float(coord))?}
    O -- yes --> P[Raise ValueError: contains NaNs]
    O -- no --> Q[Continue]
    Q --> R[After both coords validated] --> S[Return [float(coord0), float(coord1)]]

## Examples:
1) Valid list input
    try:
        coords = validate_location([51.5074, -0.1278])
        # coords == [51.5074, -0.1278]
    except Exception as e:
        # handle unexpected validation failure
        raise

2) Valid tuple of numeric strings
    try:
        coords = validate_location(("51.5074", "-0.1278"))
        # coords == [51.5074, -0.1278]
    except ValueError as e:
        # will not be raised here because strings are convertible to float
        raise

3) NumPy ndarray input (requires module alias np to refer to numpy)
    import numpy as np
    try:
        arr = np.array([[51.5074, -0.1278]])  # shape (1, 2) or similar
        coords = validate_location(arr)
        # coords == [51.5074, -0.1278]
    except Exception:
        raise

4) pandas DataFrame input (requires module alias pd to refer to pandas)
    import pandas as pd
    try:
        df = pd.DataFrame([[51.5074, -0.1278]])
        coords = validate_location(df)
        # coords == [51.5074, -0.1278]
    except Exception:
        raise

5) Error handling example: wrong length
    try:
        validate_location([1.0, 2.0, 3.0])
    except ValueError as e:
        # e contains "Expected two (lat, lon) values for location"
        pass

6) Error handling example: non-numeric entry
    try:
        validate_location([51.5, "not-a-number"])
    except ValueError as e:
        # e contains "is not convertible to float"
        pass

## `folium.utilities.validate_locations` · *function*

## Summary:
Normalize and validate an iterable of geographic locations (either a flat sequence of (lat, lon) pairs or a nested sequence of such sequences), returning the same nesting structure but with every leaf coordinate pair validated and converted to a list of two Python floats.

## Description:
Known callers (typical, not exhaustive):
    - Code paths that accept multiple locations and need normalized coordinate lists before serialization or geometry construction. Typical examples include PolyLine/Polygon constructors or GeoJSON-like helpers that accept sequences of coordinates or rings.
    - Call sites that accept either a single ring (list of coordinate pairs) or multiple rings (list of lists of coordinate pairs) and rely on a single validation entry point.

Why this is a separate function:
    - This logic centralizes the decision and recursion needed to accept both flat and nested sequences of coordinates. It enforces uniform validation policy (via validate_location for leaves), supports inputs that are pandas DataFrames (normalized by if_pandas_df_convert_to_numpy), and avoids duplicating depth-inspection and recursion across callers.

## Args:
    locations (iterable):
        - Any iterable representing coordinates. Acceptable shapes:
            * A flat iterable of coordinate pairs, e.g., [(lat, lon), [lat, lon], ...]
            * A nested iterable of iterables of coordinate pairs, e.g., [[(lat, lon), ...], [(lat,lon), ...], ...]
        - The function first calls if_pandas_df_convert_to_numpy(locations) to convert a pandas.DataFrame input (if the helper is configured to do so). After that conversion, 'locations' must be an iterable.
        - There is no explicit type restriction beyond being an iterable; nested iterables are supported and preserved.

## Returns:
    list:
        - A list with the same outer nesting structure as the input, where every leaf coordinate pair has been validated and normalized by validate_location into a plain list of two floats [lat, lon].
        - Two main return shapes:
            * Flat input (sequence of coordinate pairs) -> returns [validate_location(coord_pair) for coord_pair in locations], i.e., a list of [float, float] elements.
            * Nested input (sequence of sequences of coordinate pairs) -> returns [validate_locations(lst) for lst in locations], i.e., a nested list structure where the recursion ensures leaves are [float, float].
        - Edge-case returns:
            * If input is a numpy array converted by the pandas helper or provided directly (and interpreted as nested iterables), the returned structure will be a list (not a numpy.ndarray), with leaf lists of floats.

## Raises:
    TypeError:
        - If the post-conversion 'locations' is not iterable:
            Raised when iter(locations) raises TypeError.
            Message produced: "Locations should be an iterable with coordinate pairs, but instead got {!r}." where {!r} is the supplied value.
        - If any inner element later passed to validate_location is not indexable or sized, validate_location will raise TypeError (propagated).

    ValueError:
        - If the top-level iterable is empty:
            Raised when next(iter(locations)) raises StopIteration.
            Message produced: "Locations is empty."
        - validate_location may raise ValueError for invalid coordinate pairs (wrong length, non-numeric or NaN entries). Those exceptions propagate from the list comprehension and indicate invalid leaf elements.

## Constraints:
Preconditions:
    - if_pandas_df_convert_to_numpy must be available and correctly handle pandas.DataFrame inputs. In the module context this helper depends on the module's pandas binding behavior (see that helper's documentation).
    - The provided 'locations' must be iterable and must not be empty.
    - Leaf coordinate containers (when reached) must satisfy validate_location's preconditions: sized, indexable, length == 2, convertible to float, and not NaN.

Postconditions:
    - The function returns a Python list structure mirroring the input nesting depth, with every leaf replaced by a list of two Python float values.
    - No input objects are mutated by this function.

## Side Effects:
    - None: no I/O, no network access, no global-state mutation.
    - The function may convert pandas DataFrame inputs to their numpy values via the helper, and subsequent recursion produces new Python list objects; these operations do not mutate the original input.

## Control Flow:
flowchart TD
    Start([Start: receive locations]) --> Convert[Call if_pandas_df_convert_to_numpy(locations) -> locations2]
    Convert --> IsIterable{Can iter(locations2) be created?}
    IsIterable -- No --> RaiseTypeError[Raise TypeError: not iterable]
    IsIterable -- Yes --> HasFirst{next(iter(locations2)) yields an element?}
    HasFirst -- No --> RaiseValueError[Raise ValueError: Locations is empty]
    HasFirst -- Yes --> DepthProbe[Try float(locations2[0][0][0])] 
    DepthProbe -- TypeError/StopIteration --> FlatBranch[Assume flat: return [validate_location(coord_pair) for coord_pair in locations2]]
    DepthProbe -- Success --> NestedBranch[Assume nested: return [validate_locations(lst) for lst in locations2]]

## Examples:
1) Flat list of coordinate pairs
    Input:
        locations = [[51.5074, -0.1278], [48.8566, 2.3522]]
    Behavior:
        - Function detects flat structure and returns [[51.5074, -0.1278], [48.8566, 2.3522]] with each pair validated and converted to floats (same values in this case).

2) Nested list (e.g., multiple rings, each ring is a list of coordinate pairs)
    Input:
        locations = [
            [[51.5, -0.1], [51.6, -0.2]],      # ring 1
            [[48.8, 2.3], [48.9, 2.4]]         # ring 2
        ]
    Behavior:
        - Function detects nested structure and recursively validates each ring, returning a nested list where each leaf is a two-float list.

3) Handling pandas DataFrame (requires the pandas-to-numpy helper to be available and configured)
    Input:
        # Suppose if_pandas_df_convert_to_numpy converts a DataFrame to its values
        df = pandas.DataFrame([[51.5, -0.1], [51.6, -0.2]])
        result = validate_locations(df)
    Behavior:
        - The DataFrame is converted to an array-like; the function then validates the sequence of coordinate pairs and returns a list of two-float lists.

4) Error example: non-iterable input
    Input:
        locations = 12345
    Behavior:
        - iter(locations) raises TypeError; validate_locations raises TypeError with a message that the input is not an iterable of coordinate pairs.

5) Error example: empty iterable
    Input:
        locations = []
    Behavior:
        - next(iter(locations)) raises StopIteration; validate_locations raises ValueError("Locations is empty.").

Notes:
    - Any ValueError or TypeError raised by validate_location for invalid leaf coordinate pairs will propagate out of validate_locations; callers should catch these exceptions if they expect potentially malformed coordinates.
    - This function deliberately distinguishes between a flat sequence of coordinate pairs and a nested sequence by probing three levels deep on the first element; deeply irregular nesting or heterogeneous element shapes may produce exceptions or unexpected recursion.

## `folium.utilities.if_pandas_df_convert_to_numpy` · *function*

## Summary:
Convert a pandas DataFrame input to its underlying array (obj.values); return the input unchanged for any other type.

## Description:
Known callers:
    - No callers were discovered in the provided repository snapshot or context.
    - Intended typical usage: used by code paths that accept arbitrary inputs and must normalize pandas.DataFrame inputs into a plain array-like representation for downstream numeric processing or serialization.

Why this helper exists:
    - Encapsulates the small, repeated decision "if this object is a pandas DataFrame, extract its values" so callers do not duplicate isinstance checks and the .values access.
    - Keeps conversion semantics (DataFrame → underlying array) centralised and makes it easier to update conversion behavior in one place.

Important note about module-level imports:
    - In the provided file context, pandas is imported as `import pandas` (no alias), so the name `pd` is not defined by the module-level imports as shown. As written, calling this function in that module will raise NameError because `pd` is referenced but not bound. To make this function safe to call from this module, bind `pd = pandas` (e.g., `import pandas as pd` or assign `pd = pandas`) or modify the function to reference the existing module name (`pandas.DataFrame`).

## Args:
    obj (any): The value to inspect and possibly convert.
        - If obj is an instance of pandas.DataFrame (determined by isinstance(obj, pd.DataFrame)), the function returns obj.values.
        - Otherwise the input is returned unchanged.
    Notes on interdependencies:
        - The behavior depends on the module-level name `pd` being defined and being the pandas module (or at least exposing a DataFrame type). If `pd` is None, the function treats it as "do not convert" and returns obj unchanged; if `pd` is undefined, a NameError occurs (see Raises).

## Returns:
    numpy.ndarray or original object:
        - If obj is a pandas.DataFrame (isinstance(obj, pd.DataFrame) is True): returns obj.values.
            * Typical concrete result: for a DataFrame with shape (n_rows, n_cols), obj.values is a numpy.ndarray with shape (n_rows, n_cols) in most common cases (homogeneous dtypes). For mixed dtypes or certain extension dtypes, obj.values may be an object-dtype ndarray or an extension-array object depending on pandas version and dtypes.
        - If obj is not a DataFrame: returns the original obj unchanged (no copy performed by this function itself).

## Raises:
    NameError:
        - Raised when evaluating the expression `pd is not None` if the name `pd` is not defined in the module/global scope at runtime. In the provided file-level imports (`import pandas`), `pd` is not defined, so NameError is the expected outcome unless the module binds `pd`.
    AttributeError:
        - Possible if `pd` exists but does not have attribute `DataFrame` (e.g., `pd` bound to an unexpected object). This would surface when evaluating isinstance(obj, pd.DataFrame).
    TypeError:
        - Possible if `pd.DataFrame` exists but is not a valid type/class for use in isinstance (very unusual). These latter two are not typical in a correct environment where `pd` is the pandas module.

## Constraints:
    Preconditions:
        - For intended behavior, the module should bind `pd` to the pandas module (commonly via `import pandas as pd`) or the function should be updated to reference the actually-imported name (e.g., `pandas.DataFrame`).
        - Callers should not rely on this function to convert pandas.Series, Index, or other pandas objects — it only converts pandas.DataFrame instances.
    Postconditions:
        - After returning, if input was a DataFrame, the caller receives the DataFrame's underlying values (array-like) and can proceed with array-based operations.
        - The function makes no modifications to the original obj.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not modify the input DataFrame.
    - Accessing obj.values is a read-only operation.

## Control Flow:
flowchart TD
    Start([Start: receive obj]) --> EvalPD{Is name `pd` defined in scope?}
    EvalPD -- No --> Err[NameError raised when evaluating `pd is not None`]
    EvalPD -- Yes --> CheckNone{Is pd is not None?}
    CheckNone -- No --> ReturnObj[Return obj unchanged]
    CheckNone -- Yes --> IsDF{isinstance(obj, pd.DataFrame)?}
    IsDF -- Yes --> ReturnValues[Return obj.values]
    IsDF -- No --> ReturnObj

## Examples:
1) Correct environment where pandas is bound to pd:
    import pandas as pd
    df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    result = if_pandas_df_convert_to_numpy(df)
    # result is a numpy.ndarray with shape (2, 2); rows correspond to DataFrame rows.

2) Non-DataFrame input (unchanged):
    x = [1, 2, 3]
    result = if_pandas_df_convert_to_numpy(x)
    # result is the same list object [1, 2, 3]

3) Handling module where pd is not bound (current file-level imports show `import pandas`):
    # In this module, `pd` is not defined. Calling the function as-is will raise NameError.
    # Two remedies:
    #  - Bind pd: `import pandas as pd` or `pd = pandas`
    #  - Change the function to use the existing import name: isinstance(obj, pandas.DataFrame)

Recommendations:
    - For robustness prefer referencing the actual imported name or ensure `pd` is defined in the module scope.
    - Consider using obj.to_numpy() in place of obj.values if you want the modern pandas API that is explicit about copy behavior and dtype handling.

## `folium.utilities.image_to_url` · *function*

## Summary:
Converts an image-like input into a consumable URL/JSON value suitable for embedding in HTML or passing to downstream code — producing a data URL for local files and array images, or returning JSON-serializable values unchanged.

## Description:
Known callers:
- No direct callers were discovered in the provided module snapshot. Typical callers are higher-level rendering/export utilities that accept either (a) a local image file path, (b) a numpy-like image array, or (c) a URL or JSON-serializable image descriptor. Those callers use this function during the pipeline stage that prepares image inputs for embedding into HTML, JavaScript, or JSON payloads.

Typical trigger and pipeline stage:
- Called when the system must normalize heterogeneous image inputs into a stable representation for embedding (e.g., inline data URLs) or when ensuring a provided URL or JSON descriptor is safe to embed.
- This is typically executed immediately before injecting the image into an HTML template, a Leaflet popup, or a JSON configuration that expects either a data URL, a remote URL, or a JSON object.

Why this logic is extracted into its own function:
- It centralizes the branching logic that distinguishes local file paths, in-memory numeric arrays, and already-formed URLs or serializable descriptors.
- It encapsulates the file I/O, PNG encoding, base64 encoding, and lightweight JSON normalization so callers do not duplicate these error-prone steps.
- It cleanly separates "prepare image for embedding" responsibility from rendering and higher-level UI logic.

## Args:
    image (str | numpy.ndarray | any JSON-serializable):
        - If a str and not recognized as a URL by the module helper _is_url, it is treated as a local filesystem path and read as binary.
        - If the object's class name contains "ndarray" (e.g., numpy.ndarray), it is treated as an image array and passed to write_png for PNG encoding.
        - Otherwise, it is treated as a JSON-serializable descriptor which will be round-tripped via json.dumps/json.loads.
        - Note: Passing bytes or non-JSON-serializable objects will typically raise TypeError from json.dumps.
    colormap (callable | None, optional):
        - Only used when image is an ndarray (mono/grayscale): forwarded to write_png as the colormap argument.
        - Contract: same as write_png.colormap (callable that maps scalars to 3- or 4-length color tuples). If None, write_png uses its default grayscale colormap.
    origin (str, optional):
        - Only used when image is an ndarray: forwarded to write_png (defaults to "upper").
        - Accepted values: "upper" (no vertical flip) or "lower" (flip vertically). Any value other than "lower" results in no flip (treated as "upper").

Interdependencies:
- colormap and origin are ignored unless image is an ndarray-like object.
- The meaning of "is a URL" is determined by the module helper _is_url (which relies on module-level valid URL schemes); this changes the branch for str inputs.

## Returns:
    str or JSON-equivalent object:
        - Local file path (string, not recognized as URL):
            Returns a data URL string of the form "data:image/{ext};base64,{b64}" where {ext} is the file extension (without dot) extracted with os.path.splitext. If the file has no extension, the MIME subtype portion may be empty (e.g., "data:image/;base64,...").
        - ndarray-like image:
            Returns a PNG data URL string "data:image/png;base64,{b64}" where the PNG bytes are produced by write_png(image, origin=origin, colormap=colormap).
        - String recognized as a URL by _is_url:
            Returns the original string (preserved) via a json.dumps/json.loads round-trip (effectively returns the same string).
        - Other JSON-serializable objects (dict, list, number, etc.):
            Returns the deserialized object produced by json.loads(json.dumps(image)) — i.e., a JSON-normalized copy of the input (may change types for some inputs, e.g., tuples -> lists).
    Post-processing:
        - Any newline characters in the returned string (if present) are replaced with a single space before returning (return_value.replace("\n", " ")). This prevents embedded newlines in data URLs or strings.

Edge-case return values:
    - If the local file has no extension, the data URL's MIME subtype will be empty (the code does not map extension to MIME type beyond using the raw extension).
    - For numpy-like but invalid images, write_png may raise (see Raises) — no special fallback exists in image_to_url.
    - For strings that are valid URLs, the returned value is the same URL string.
    - For non-serializable inputs, json.dumps will raise TypeError (see Raises).

## Raises:
    - FileNotFoundError, PermissionError, OSError:
        - If image is a local file path (string not recognized as URL) and opening/reading the file fails.
    - TypeError:
        - If image is neither a recognized string/file path nor ndarray-like and is not JSON-serializable, json.dumps(image) will raise TypeError which will propagate.
        - If image is bytes and not JSON-serializable, json.dumps will raise TypeError.
    - ValueError, AssertionError:
        - If image is ndarray-like and write_png validates shape/contents and raises ValueError (e.g., unsupported channel count) or AssertionError from write_png invariants, these exceptions propagate.
    - Any other exception raised by write_png or json.dumps/json.loads will propagate to the caller (the function does not catch these).

## Constraints:
Preconditions:
    - If passing ndarray-like images:
        * numpy (or an ndarray-like class whose __class__.__name__ contains "ndarray") should be available and the array must meet write_png's shape and dtype expectations (2D or 3D with last dimension 1, 3, or 4).
        * colormap, if provided, must satisfy write_png's colormap contract (return 3- or 4-length tuples).
    - If passing a file path:
        * The path must point to a readable file and have appropriate file permissions.
    - If passing a URL string:
        * The scheme detection depends on _is_url and module-level valid URL schemes; ensure those schemes include the forms you expect (e.g., 'http', 'https', 'data' if needed).

Postconditions:
    - The returned value will have no newline characters (all '\n' replaced with spaces).
    - If a data URL is returned, it will be base64-encoded and represent the file bytes (local file) or PNG bytes (ndarray).

## Side Effects:
    - File I/O:
        * If image is a local file path, the function opens the file in binary read mode and reads its entire contents into memory.
    - Memory allocation:
        * Converting ndarray inputs to PNG bytes and base64 encoding both allocate memory proportional to the image size.
    - No network I/O is performed by this function.
    - No persistent external state is modified.

## Control Flow:
flowchart TD
    Start([Start]) --> IsStr{isinstance(image, str)?}
    IsStr -- yes --> IsUrl{_is_url(image) == True?}
    IsUrl -- yes --> JsonRoundtrip[json.loads(json.dumps(image))] --> ReplaceNewline[replace("\\n", " ")] --> Return([Return value])
    IsUrl -- no --> ReadFile[open(path) as f -> img = f.read()] --> B64File[base64.b64encode(img).decode("utf-8")] --> MakeDataURLFile[data:image/{ext};base64,{b64}] --> ReplaceNewline --> Return
    IsStr -- no --> IsNDArray{"ndarray" in image.__class__.__name__?}
    IsNDArray -- yes --> PNGBytes[img = write_png(image, origin=origin, colormap=colormap)] --> B64PNG[base64.b64encode(img).decode("utf-8")] --> MakeDataURLPNG[data:image/png;base64,{b64}] --> ReplaceNewline --> Return
    IsNDArray -- no --> JsonRoundtrip

## Examples:

Example 1 — Local file path -> data URL
    try:
        url = image_to_url("/path/to/logo.png")
        # url: "data:image/png;base64,...."
    except FileNotFoundError:
        # handle missing file

Example 2 — Remote URL string preserved
    remote = "https://example.com/img.png"
    url = image_to_url(remote)
    # url == "https://example.com/img.png"

Example 3 — NumPy array -> PNG data URL
    import numpy as np
    arr = np.zeros((20, 30, 3), dtype=np.uint8)
    arr[..., 0] = 255
    url = image_to_url(arr)  # produces "data:image/png;base64,...."

Example 4 — Non-serializable input -> TypeError
    class NotSerializable:
        pass
    try:
        image_to_url(NotSerializable())
    except TypeError:
        # json.dumps raised TypeError because object is not JSON-serializable

Example 5 — ndarray with invalid channels -> ValueError from write_png
    import numpy as np
    bad = np.zeros((10, 10, 2))
    try:
        image_to_url(bad)
    except ValueError as exc:
        # write_png enforces valid channel counts and raises ValueError
        print("Invalid image:", exc)

## `folium.utilities._is_url` · *function*

## Summary:
Return True when the provided input parses to a URL whose scheme is one of the module's allowed schemes; otherwise return False.

## Description:
Known callers:
- No direct callers were found in the pre-loaded module-level context supplied for this task. If other modules in the repository call this helper, they were not available in the provided memory snapshot.
Typical callers and usage context:
- This helper is typically used where a function must accept either a remote resource (URL) or a local resource identifier (file path, raw data). Callers use it to branch between "fetch-from-network" logic and "read-from-local" logic (for example, choosing whether to download a tileset, image, or JSON from a remote URL vs. reading a local file or embedded data).
Why this function exists (responsibility boundary):
- Centralizes the logic for deciding whether a string represents an allowed URL scheme. Extracting this test avoids repeated parsing and scheme-checking logic across the codebase, ensures consistent behavior (including how parse failures are handled), and encapsulates the dependency on the module-level _VALID_URLS set.

## Args:
    url (str or any): The value to test for being a URL. Although a string is expected, the function tolerates non-string inputs; non-string inputs are passed to urlparse and any exception raised during parsing is caught and results in False. There is no default value.

Notes:
- The function depends on a module-level variable named _VALID_URLS (an iterable of allowed scheme strings). The exact contents of _VALID_URLS are not specified here; callers should consult the module to see which schemes are considered valid.

## Returns:
    bool: 
        - True if urlparse(url).scheme is present in _VALID_URLS.
        - False if the parsed scheme is not in _VALID_URLS, if parsing fails, if url is None, or if any exception occurs during the check.

Edge-case return values:
- If url is None, not a string, or malformed such that urlparse raises or returns an unexpected result, the function returns False.
- If _VALID_URLS is missing or misconfigured (e.g., not defined), that error is caught by the function and False is returned — note that this masks the configuration error (see Constraints).

## Raises:
    None: The function catches all Exceptions raised during parsing or membership testing and returns False instead of propagating them. Therefore, callers will not see exceptions originating inside this function.

## Constraints:
Preconditions:
- Best practice: pass a string-like value when possible.
- The module-level variable _VALID_URLS must be populated with the allowed scheme strings for the test to be meaningful.

Postconditions:
- The function always returns a boolean value (True or False).
- The function does not modify any external state.

Caveat:
- Because the function swallows all exceptions and returns False, configuration issues (for example, _VALID_URLS not defined or mis-typed) or programming errors in callers may be masked. For debugging, ensure _VALID_URLS exists and contains the expected scheme strings.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and makes no network calls.

## Control Flow:
flowchart TD
    Start([Start]) --> TryParse{Try: urlparse(url)}
    TryParse -->|success| GetScheme[Get parsed.scheme]
    GetScheme --> InValid{scheme in _VALID_URLS?}
    InValid -->|yes| ReturnTrue[Return True]
    InValid -->|no| ReturnFalse[Return False]
    TryParse -->|exception| ExceptHandler[Except Exception]
    ExceptHandler --> ReturnFalse2[Return False]
    ReturnTrue --> End([End])
    ReturnFalse --> End
    ReturnFalse2 --> End

## Examples:
- Typical decision point when accepting either a URL or a local path (assumes _VALID_URLS contains 'http' and 'https'):
    _is_url('https://example.com/resource')  -> True
    _is_url('http://example.com')             -> True
    _is_url('/home/user/data/file.geojson')   -> False
    _is_url(None)                             -> False

- Realistic usage pattern:
    1. Receive user input or configuration value that may be a URL or a local filename.
    2. Call this helper to decide:
       - If True: fetch the resource over HTTP(S).
       - If False: treat the input as a local path or embedded data and handle accordingly.

Notes for implementers:
- Ensure _VALID_URLS (module-level) is assigned an iterable of lower-case scheme strings (e.g., 'http', 'https', 'ftp', 'data' as needed).
- If you need to detect more URL forms (for example, schemeless URLs like '//example.com'), pre-normalize the input before calling this helper or extend the helper accordingly.

## `folium.utilities.write_png` · *function*

## Summary:
Encodes a numeric image array (grayscale, RGB, or RGBA) into complete PNG-format bytes (8-bit RGBA) ready to be written to a file or embedded.

## Description:
Converts image-like numeric data into a valid PNG file in memory. The function:
- Accepts 2D grayscale or 3D image arrays and ensures a 4-channel (RGBA) image with 8-bit channels.
- Applies a colormap if the input is 2D (monochrome) to produce RGB(A) tuples per pixel.
- Adds an alpha channel if the input is RGB.
- Normalizes non-uint8 arrays to 0–255 per channel, replacing non-finite results with 0, then casts to uint8.
- Optionally flips the vertical origin when origin == "lower".
- Packs PNG chunks (IHDR, IDAT with zlib compression level 9, IEND) and returns the concatenated bytes.

Known callers in the provided context:
- None were discovered in the provided code snapshot. This is a general-purpose utility typically used by image rendering/export code that needs PNG bytes from numeric arrays.

Why this logic is a separate function:
- PNG encoding requires specific byte layout and CRC-chunk construction plus pixel normalization steps. Centralizing these concerns avoids duplication and ensures consistent PNG output across callers.

## Args:
    data (array-like or numpy.ndarray):
        - Shape: either (height, width) for grayscale or (height, width, channels) for color.
        - Allowed channels (when 3D): 1 (mono), 3 (RGB), or 4 (RGBA). If not one of these, a ValueError is raised.
        - Element types: integers or floats. If dtype is not uint8, the function performs per-channel normalization (see Returns and Constraints).
        - Note: the function uses numpy.atleast_3d internally, so 2D inputs are promoted to 3D for processing.

    origin (str, optional):
        - "upper" (default) or "lower".
        - If "lower", the rows are flipped vertically (arr = arr[::-1, :, :]) before encoding to convert from bottom-left origin to PNG top-left origin.
        - Any value other than the string "lower" results in no flip (equivalent to "upper").

    colormap (callable, optional):
        - Only used when `data` has a single layer (mono / nblayers == 1).
        - Default: When colormap is None, the function uses the identity grayscale-to-RGBA mapping:
            colormap(x) -> (x, x, x, 1)
          i.e., maps each scalar to RGB equal channels and alpha 1.
        - Contract: callable that accepts a scalar and returns a tuple of length 3 (R,G,B) or 4 (R,G,B,A).
            * Each tuple element may be float or int. Typical ranges are 0.0–1.0 (floats) or 0–255 (ints).
            * If the tuple length is 3, an alpha channel will later be added (opaque 1) and normalization still applies if dtype != uint8.

## Returns:
    bytes: The full PNG file contents.
    - PNG specifics produced:
        * IHDR: width, height, bit depth 8, color type 6 (RGBA), compression=0, filter=0, interlace=0.
        * IDAT: zlib.compress(raw_data, 9) where raw_data is the image scanlines formatted as:
            for each row i: b"\x00" + row_bytes  (0x00 is PNG filter type 0 for each scanline).
        * IEND: empty final chunk.
    - Normalization details for non-uint8 inputs:
        * For arrays with dtype != uint8, the function computes per-channel maxima: m = arr.max(axis=(0,1)).reshape((1,1,4))
        * Then arr = arr * 255.0 / m.
        * Any non-finite values resulting from division (inf, -inf, nan) are set to 0 (arr[~np.isfinite(arr)] = 0).
        * Finally arr is cast to dtype uint8.
        * This makes each channel's maximum value map to 255; channels with all-zero max produce zeros.
    - Edge-case returns:
        * For zero height or width the function will still return a syntactically valid PNG container; however, typical image consumers expect positive dimensions.

## Raises:
    ValueError:
        - If an input 3D array's last dimension is not in {1, 3, 4}:
            "Data must be NxM (mono), NxMx3 (RGB), or NxMx4 (RGBA)"
        - If `data` is mono (nblayers == 1) and the provided `colormap` returns tuples whose length is not 3 or 4:
            "colormap must provide colors of length 3 (RGB) or 4 (RGBA)"

    AssertionError:
        - Internal assertions enforce shapes and expected layer counts (these may raise AssertionError if invariants fail during execution). These asserts are:
            * arr.shape == (height, width, nblayers) at several points
            * final nblayers == 4

## Constraints:
Preconditions:
    - numpy is available and `data` is convertible to a numeric numpy array.
    - The input's height and width must be non-negative integers representable by Python/numpy.

Postconditions:
    - Output bytes represent a valid 8-bit RGBA PNG reflecting the transformed input image (colormap applied if mono, alpha added if needed, dtype normalized to uint8).

## Side Effects:
    - No file or network I/O is performed.
    - No modification of global state.
    - Memory: allocates intermediate arrays proportional to the image size; CPU work includes array normalization and zlib compression at level 9.

## Control Flow:
flowchart TD
    A[Start: call write_png] --> B{colormap is None?}
    B -- yes --> B1[set default colormap(x)->(x,x,x,1)]
    B -- no --> C
    B1 --> C
    C[Convert data to numpy.atleast_3d] --> D[height,width,nblayers = arr.shape]
    D --> E{nblayers in {1,3,4}?}
    E -- no --> F[raise ValueError: Data must be NxM...]
    E -- yes --> G{nblayers==1?}
    G -- yes --> H[apply colormap to each scalar via map over arr.ravel()]
    H --> I[nblayers = arr.shape[1]; if not in {3,4} raise ValueError]
    I --> J[reshape arr -> (height,width,nblayers)]
    G -- no --> J
    J --> K{nblayers==3?}
    K -- yes --> L[append alpha channel of ones -> nblayers=4]
    K -- no --> M[keep nblayers=4]
    L --> M
    M --> N{arr.dtype != uint8?}
    N -- yes --> O[normalize per-channel: arr = arr * 255 / arr.max(axis=(0,1))]
    O --> P[set non-finite to 0; cast to uint8]
    N -- no --> P
    P --> Q{origin == "lower"?}
    Q -- yes --> R[flip vertical rows: arr = arr[::-1,:,:]]
    Q -- no --> S[no flip]
    R --> T[create raw_data: join b"\x00"+row_bytes for each row]
    S --> T
    T --> U[pack PNG chunks: IHDR, IDAT(zlib.compress(raw_data,9)), IEND]
    U --> V[return bytes]

## Examples:

Example 1 — Grayscale floats (0.0–1.0) using default colormap:
    import numpy as np
    gray = np.linspace(0.0, 1.0, 100*200).reshape((100, 200))
    # default colormap maps each scalar to (x, x, x, 1)
    png_bytes = write_png(gray)  # normalized per-channel so max->255
    with open("gradient_default.png", "wb") as f:
        f.write(png_bytes)

Example 2 — Grayscale integers (0–255) with custom 3-tuple colormap:
    import numpy as np
    gray = np.random.randint(0, 256, size=(64, 64), dtype=np.uint8)
    def cmap_int(x):
        # returns ints in 0..255 (R,G,B); alpha will be added as 1 by default then normalized if needed
        return (x, 255-x, x//2)
    png_bytes = write_png(gray, colormap=cmap_int)
    open("random_cmap.png", "wb").write(png_bytes)

Example 3 — RGB uint8 array and bottom-origin flip:
    import numpy as np
    rgb = np.zeros((10, 20, 3), dtype=np.uint8)
    rgb[..., 1] = 128
    # origin="lower" flips rows vertically before encoding
    png_bytes = write_png(rgb, origin="lower")
    with open("flipped.png", "wb") as f:
        f.write(png_bytes)

Example 4 — Handling a bad input (2-channel image):
    import numpy as np
    bad = np.zeros((10, 10, 2))
    try:
        write_png(bad)
    except ValueError as exc:
        # exc message should include "Data must be"
        print("Invalid image shape:", exc)

## `folium.utilities.mercator_transform` · *function*

## Summary:
Transforms raster data from linear geographic-latitude sampling into Web Mercator (pseudo-mercator) latitude sampling by vertically resampling each column using 1D interpolation, producing an array suitable for map displays that use the Mercator projection.

## Description:
This function accepts a 2D or 3D raster-like array (height × width × channels) whose rows correspond to regularly spaced geographic latitudes, and returns a vertically resampled array whose rows correspond to evenly spaced Web Mercator-projected latitudes.

Known callers within the inspected codebase:
    - None discovered in the inspected codebase snapshot. (If present, typical callers would be raster/image layer renderers that need to present an image on a Web Mercator map.)

Typical usage context:
    - Convert an image or heatmap whose vertical axis is linear latitude (e.g., global gridded data or an image extracted from a geographic source) into the vertical sampling required for Web Mercator map tiles so the visual alignment with other Mercator-projected layers is correct.

Reason for extraction:
    - Latitudinal re-sampling using the Mercator transform is a self-contained numerical operation (clamping lat bounds, computing projection, and column-wise interpolation). Extracting it isolates the geometric transformation, makes it reusable across multiple raster rendering paths, and keeps projection-specific math out of higher-level rendering code.

## Args:
    data (array-like | numpy.ndarray):
        - Input raster. Can be 2D (height × width) or 3D (height × width × n_channels). The function internally converts to at least 3D.
        - Accepts numeric arrays (integers or floats). Note: output dtype will be floating-point (numpy.float64) because interpolation and np.zeros create floating output.
    lat_bounds (sequence[float, float]):
        - (lat_min, lat_max) in degrees, representing the geographic latitude range covered by the first and last rows of `data`.
        - Values are interpreted as south (minimum) then north (maximum). Precondition: lat_bounds[0] < lat_bounds[1] for meaningful output.
    origin (str, optional):
        - Either "upper" or anything else. Defaults to "upper".
        - If "upper", the function treats the first row of `data` as the northernmost row (typical image convention) and flips the vertical ordering before and after processing so the interpolation assumes increasing-latitude order internally.
        - If not "upper", the function assumes the first row is the southernmost row (increasing-latitude order already).
    height_out (int | None, optional):
        - Desired output height in rows. If None (default), the output height equals input height.
        - Must be a positive integer if provided.

## Returns:
    numpy.ndarray:
        - A 3D numpy.ndarray with shape (height_out, width, n_channels).
        - The returned array is of floating type (numpy.float64) because interpolation and initialization use floats.
        - Values are the vertically resampled pixel/band values mapped from the input latitude sampling to Web Mercator latitude sampling.
        - If `data` was 2D, the returned array will have a singleton third dimension (n_channels == 1).

Edge-case return behaviors:
    - If width == 0 or height == 0 in the input, the function will return an array with corresponding zero dimension(s).
    - If input contains NaNs, interpolated outputs inherit NaNs wherever interpolation uses NaN values in the source vector.

## Raises:
    - The implementation does not explicitly raise custom exceptions.
    - Potential exceptions coming from underlying numpy operations:
        * TypeError/ValueError: if invalid types are passed that cannot be converted to numeric arrays.
        * IndexError/ValueError: unlikely but possible if shapes are inconsistent in a modified environment.
    - Preconditions (documented above) should be used to avoid invalid numerical results; the function itself does not validate lat_bounds ordering beyond clamping to valid Mercator latitude limits.

## Constraints:
Preconditions:
    - lat_bounds[0] should be strictly less than lat_bounds[1] to represent a valid range.
    - height_out, if provided, must be a positive integer.
    - The input's vertical axis must correspond to evenly spaced geographic latitudes across lat_bounds.

Postconditions:
    - The output covers the same longitudinal sampling (width) and number of layers/channels as the input.
    - Output vertical sampling corresponds to equally spaced positions in Web Mercator latitude between the clamped lat_bounds.
    - Latitude bounds are clamped to the valid Web Mercator interval [-85.051128779806589, 85.051128779806589] before projection.

## Side Effects:
    - No I/O (no file, network, stdout operations).
    - No mutation of global state.
    - The function copies input data early (np.atleast_3d(data).copy()), so the caller's input array is not modified.

## Control Flow:
flowchart TD
    A[Start] --> B[Convert input to at least 3D and copy]
    B --> C[Extract height, width, n_channels]
    C --> D[Clamp lat_bounds to [-85.0511..., 85.0511...]]
    D --> E{height_out provided?}
    E -- yes --> F[use provided height_out]
    E -- no --> G[set height_out = input height]
    F --> H{origin == "upper"?}
    G --> H
    H -- yes --> I[flip array vertically (rows reversed)]
    H -- no --> J[do not flip]
    I --> K[compute evenly spaced source lat sample centers (lats)]
    J --> K
    K --> L[compute mercator(lats) and target mercator-sampled lat centers (latslats)]
    L --> M[allocate out array of zeros (height_out x width x n_channels)]
    M --> N[narrow loops: for each column i and channel j -> one-dimensional interpolation]
    N --> O{origin == "upper"?}
    O -- yes --> P[flip out vertically back]
    O -- no --> Q[leave out as-is]
    P --> R[Return out]
    Q --> R[Return out]

## Examples:
Example 1 — Resample an RGB image (assumes numpy imported, shown as a usage line):
    out = mercator_transform(image_array, (-60.0, 60.0), origin="upper", height_out=512)
    # `out` is a (512, width, 3) float64 array sampled for Web Mercator display.

Example 2 — Grayscale 2D array input:
    out = mercator_transform(grayscale_2d_array, (-45.0, 45.0))
    # Input shaped (h, w) becomes output shaped (h, w, 1).

Example 3 — Defensive checks a caller should perform:
    - Verify lat_bounds[0] < lat_bounds[1]; swap if necessary or raise a ValueError before calling.
    - Ensure height_out is a positive integer if a different output height is required.

## `folium.utilities.none_min` · *function*

## Summary:
Return the lesser of two comparable values while treating None as "no value" (i.e., propagate the non-None operand when one is None).

## Description:
This small utility centralizes the common pattern of taking a minimum between two values that may be None. It ensures that None is treated as "absent" rather than as a value that should participate in ordering.

Known callers in the codebase:
    - No direct call sites were identified in the provided repository snapshot. The function is intended for use anywhere the code needs a safe min operation when inputs may be optional (None).

Why this is a separate function:
    - Encapsulates the None-handling policy (None means "use the other value") in one place so callers do not duplicate conditional logic.
    - Keeps call sites concise and avoids repeated None-checking scattered through the codebase.
    - Makes the intent explicit and reduces errors when combining optional values.

## Args:
    x (comparable | None): First operand. May be None to indicate "no value".
    y (comparable | None): Second operand. May be None to indicate "no value".

Notes on types and interdependencies:
    - x and y must be of types that are comparable with the built-in min function when both are not None (for example, two numbers or two strings).
    - If one argument is None, the other is returned unchanged (even if the other is also None).
    - If both are None, the result is None.

## Returns:
    comparable | None
    - If x is None, returns y.
    - Else if y is None, returns x.
    - Else returns min(x, y) where min is Python's built-in comparison.
    - Possible return values: one of the original inputs (x or y), or None if both inputs are None.

## Raises:
    TypeError
    - Raised indirectly if both x and y are not None but are not mutually comparable by Python's ordering (for example an int and a str in Python 3). The function does not catch or wrap this exception; it propagates whatever exception min() raises.

## Constraints:
Preconditions:
    - Caller should ensure that when both x and y are non-None, they are of compatible/comparable types for the built-in min operation.
Postconditions:
    - The returned value is either None or exactly one of the provided arguments (no transformation of values occurs).
    - No mutation of x or y is performed.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not call external services.

## Control Flow:
flowchart TD
    Start --> CheckXIsNone{"x is None?"}
    CheckXIsNone -- Yes --> ReturnY["return y (may be None)"]
    CheckXIsNone -- No --> CheckYIsNone{"y is None?"}
    CheckYIsNone -- Yes --> ReturnX["return x"]
    CheckYIsNone -- No --> ReturnMin["return min(x, y)"]
    ReturnY --> End[End]
    ReturnX --> End
    ReturnMin --> End

## Examples:
- Both values present and comparable:
    none_min(3, 5)  -> 3

- One value is None:
    none_min(None, 10)  -> 10
    none_min(7, None)   -> 7

- Both None:
    none_min(None, None)  -> None

- Incompatible types when both non-None (demonstrates raised error):
    none_min(1, "2")  -> raises TypeError (propagated from min) because int and str are not comparable in Python 3

Usage pattern (typical):
    - Use when you want the minimum value but treat None as "absent" and prefer the other operand rather than raising or doing explicit checks at each call site.

## `folium.utilities.none_max` · *function*

## Summary:
Return the non-None maximum of two values, treating None as "missing" and otherwise returning the larger of the two values according to Python's built-in ordering.

## Description:
This utility returns the other operand when one argument is None, and otherwise returns the result of Python's built-in max(x, y). It encapsulates the common pattern "if either side is missing, prefer the present value; otherwise pick the larger value."

Known callers within the codebase:
    - No direct callers are declared in this file excerpt. This is a general-purpose helper intended for use anywhere the codebase needs to compute a maximum while treating None as a missing/absent value (for example: combining optional numeric bounds, selecting the greater of two optional measurements, or merging optional timestamps).

Why this logic is extracted:
    - Centralizes and documents the specific policy for handling None when taking maxima (prefer the present value, return None only if both are None).
    - Avoids repeating the None-checking + max logic at every call site.
    - Keeps call sites concise and reduces the risk of inconsistent handling of None across the codebase.

## Args:
    x (Any | None): First operand. May be None to indicate an absent/missing value.
    y (Any | None): Second operand. May be None to indicate an absent/missing value.
    - Interdependencies: At least one of x or y may be non-None; if both are non-None they must be comparable by Python's built-in max() for the intended behavior to succeed.

## Returns:
    Any | None:
    - If x is None and y is not None: returns y.
    - Else if y is None and x is not None: returns x.
    - Else if both x and y are not None: returns max(x, y) using Python's built-in max semantics.
    - If both x and y are None: returns None.

    Note: The concrete returned object is always one of the input objects (x or y) or None.

## Raises:
    - TypeError or other exceptions raised by Python's built-in max() when both x and y are non-None but not mutually comparable (for example, mixing incompatible types such as int and str will raise a TypeError).
    - Any exception that arises from custom comparison operators on user-defined types will propagate here.

## Constraints:
    Preconditions:
        - Callers should expect that x and y may be None.
        - If both x and y are non-None, they should be comparable by the built-in ordering used by max(); otherwise an exception may be raised.
    Postconditions:
        - The result is either None or one of the input values.
        - If exactly one input is non-None, that input is returned.
        - If both inputs are non-None and comparable, the larger according to max() is returned.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> CheckX{is x None?}
    CheckX -- yes --> ReturnY[return y]
    CheckX -- no --> CheckY{is y None?}
    CheckY -- yes --> ReturnX[return x]
    CheckY -- no --> ReturnMax[return built-in max(x, y)]
    ReturnY --> End([End])
    ReturnX --> End
    ReturnMax --> End

## Examples:
    - Numeric operands:
        none_max(3, None) -> 3
        none_max(None, 5) -> 5
        none_max(2, 7) -> 7
        none_max(None, None) -> None

    - Strings:
        none_max("apple", None) -> "apple"
        none_max("apple", "banana") -> "banana"  (since "banana" > "apple" under string ordering)

    - Incompatible types:
        none_max(1, "a") -> raises TypeError (built-in max cannot compare int and str)

    - Usage pattern (conceptual):
        When merging optional upper bounds where missing bound is represented by None:
            resulting_bound = none_max(bound_a, bound_b)
            # If one bound is missing, the present bound is used.
            # If both present, the larger bound is selected.

## `folium.utilities.iter_coords` · *function*

## Summary:
Yields coordinate tuples extracted from a GeoJSON-like object or nested sequence by recursively traversing its coordinate structures until numeric coordinate tuples are found.

## Description:
iter_coords accepts either a sequence of coordinates or a GeoJSON-like mapping and returns a generator that yields 2D/ND coordinate tuples for every coordinate encountered. It handles:
- Plain sequences (tuple, list) representing coordinates or nested coordinate arrays.
- GeoJSON FeatureCollection-like objects that contain a "features" key (it collects each feature's geometry.coordinates).
- GeoJSON Feature-like objects with a top-level "geometry" key.
- GeoJSON GeometryCollection-like objects that contain "geometries" where the first geometry element has "coordinates".
- Generic mappings with a "coordinates" key.

Known callers within the codebase:
- No specific callers were provided in the supplied context. Typical callers are functions that need to iterate all coordinates from GeoJSON-like inputs (for example, bounding-box calculations, coordinate transformation routines, or rendering helpers).

Why this logic is extracted:
- The function encapsulates the recursive traversal and normalization of many common GeoJSON and sequence shapes into a single, reusable generator. Extracting it avoids duplicating recursion and shape detection logic wherever code needs to iterate raw coordinates.

## Args:
    obj (any):
        A GeoJSON-like mapping or nested sequence of coordinates.
        - Allowed types:
            - list or tuple of coordinates or nested coordinate lists/tuples
            - dict-like mapping (e.g., parsed GeoJSON) with keys such as "features", "geometry", "geometries", or "coordinates"
        - If obj is a mapping, it must behave like a dict for key access (support __getitem__) and may support get for the fallback path.
        - Interdependencies: if obj contains "features", each element of obj["features"] is expected to be a dict with a "geometry" mapping that contains "coordinates". If "geometries" is present, the function only inspects the first geometry's "coordinates".

## Returns:
    generator[tuple]:
        A generator that yields coordinate tuples. Each yielded value is the tuple conversion of the numeric coordinate container found at the leaf level (for example (x, y) or (x, y, z)).
        Possible return outcomes:
        - Yields zero tuples when no coordinates are present (empty input).
        - Yields one or multiple tuples depending on the nesting and structure.
        - If the input represents a single coordinate (e.g., [x, y]), the generator yields exactly one tuple (x, y).
        - For nested arrays (e.g., a list of points or a polygon), it yields a tuple per point encountered.

## Raises:
    AttributeError:
        If obj is not a list/tuple and does not support key access in expected ways, access to obj.get(...) or other attribute/dictionary lookups may raise AttributeError.
    KeyError:
        If obj is a mapping but expected keys (e.g., "geometry", "coordinates") are missing when the code accesses them using indexing, a KeyError may be raised.
    IndexError:
        If "geometries" is present but the list is empty, accessing geometries[0] can raise IndexError.
    TypeError:
        If the structure of obj is not compatible with the assumptions (for example, passing a scalar where a sequence or mapping is expected), iteration or indexing may raise TypeError.
    Notes:
        The function does not explicitly raise these exceptions but they can arise from the direct dictionary/list access patterns used in the implementation.

## Constraints:
    Preconditions:
        - Caller should pass a GeoJSON-like mapping or a sequence of coordinates/nested coordinate sequences.
        - For mapping inputs, the mapping should match one of the inspected shapes ("features", "geometry", "geometries", or "coordinates") or implement get("coordinates", obj) semantics.
    Postconditions:
        - No mutable input is modified by iter_coords.
        - The returned generator will produce only tuples whose elements are numeric types (int or float), according to how the function detects leaf nodes.

## Side Effects:
    - None: the function performs no I/O and does not mutate global state.
    - Note: If obj contains generator objects or other one-time-iterables, iterating inside iter_coords will consume them; this is a consumption side effect of iterating in Python, not specific to this function.

## Control Flow:
flowchart TD
    Start --> IsSeq{"obj is tuple or list?"}
    IsSeq -- Yes --> coords[coords = obj] --> ForLoop
    IsSeq -- No --> HasFeatures{"'features' in obj?"}
    HasFeatures -- Yes --> coords_features[coords = [geom['geometry']['coordinates'] for geom in obj['features']]] --> ForLoop
    HasFeatures -- No --> HasGeometry{"'geometry' in obj?"}
    HasGeometry -- Yes --> coords_geom[coords = obj['geometry']['coordinates']] --> ForLoop
    HasGeometry -- No --> HasGeometries{"'geometries' in obj and 'coordinates' in obj['geometries'][0]?"}
    HasGeometries -- Yes --> coords_firstgeom[coords = obj['geometries'][0]['coordinates']] --> ForLoop
    HasGeometries -- No --> coords_get[coords = obj.get('coordinates', obj)] --> ForLoop
    ForLoop --> IterateCoord["for coord in coords:"]
    IterateCoord --> IsNumber{"is coord a float or int?"}
    IsNumber -- Yes --> YieldTuple["yield tuple(coords)"] --> BreakLoop
    IsNumber -- No --> Recurse["yield from iter_coords(coord)"] --> ForLoop
    BreakLoop --> End
    Recurse --> End

## Examples:
- Point (single coordinate container)
    Input: a mapping {'type': 'Point', 'coordinates': [1.0, 2.0]}
    Behavior: iter_coords yields one tuple (1.0, 2.0).

- FeatureCollection (multiple features)
    Input: mapping with key "features", where each feature has geometry.coordinates.
    Behavior: The function collects geometry['coordinates'] for every feature and yields coordinate tuples found by traversing each feature's coordinates.

- GeometryCollection (first geometry only)
    Input: mapping with key "geometries" and geometries[0] contains "coordinates".
    Behavior: Only geometries[0]['coordinates'] is inspected; coordinates in subsequent geometries are ignored by this function.

- Nested coordinate arrays (e.g., Polygon, MultiPolygon)
    Behavior: The function recursively traverses nested lists until numeric leaf arrays are reached and yields a tuple per numeric leaf coordinate (for example each vertex of a polygon).

- Error handling note
    If a feature in a FeatureCollection is missing "geometry" or "coordinates", iteration may raise KeyError. If "geometries" is present but is empty, accessing geometries[0] will raise IndexError. Guard or validate input before calling iter_coords if the shape of the mapping is uncertain.

## `folium.utilities._locations_mirror` · *function*

*No documentation generated.*

## `folium.utilities.get_bounds` · *function*

## Summary:
Computes a two-point bounding box (min and max per coordinate axis) for the coordinates found in the given locations input. Returns [[min0, min1], [max0, max1]] where each entry is either a numeric value or None if no points were found.

## Description:
This function iterates all coordinate tuples discovered in the provided locations using the shared iter_coords generator, and maintains running minima and maxima for the first two coordinate axes.

Known callers:
- No direct callers were found in the supplied repository snapshot. Typical callers (intended use) are routines that need to compute a viewport/extent or feed a bounding box to a mapping/rendering helper (for example: map fit/zoom functions or tile-generation helpers).

Why extracted:
- Bounding-box computation over potentially heterogeneous GeoJSON-like or nested coordinate inputs is a reusable operation that requires coordinated iteration (provided by iter_coords) plus None-safe min/max semantics (provided by none_min/none_max). Extracting it keeps calling code concise and centralizes edge-case handling (empty inputs, None propagation) in one place.

## Args:
    locations (any):
        A GeoJSON-like mapping or nested sequence of coordinates acceptable to iter_coords.
        - Expected behavior: iter_coords(locations) yields coordinate tuples; get_bounds uses the first two elements of each yielded tuple.
        - Constraints: If iter_coords yields tuples/lists with fewer than two elements, IndexError will be raised by indexing; if it yields non-comparable types, comparison operations may raise TypeError.

    lonlat (bool, optional):
        Default: False.
        If True, the computed bounds are passed to the helper _locations_mirror and the result of that call is returned. The exact semantics of the transformation depend on _locations_mirror and are not implemented here; when False the raw computed bounds are returned.

## Returns:
    list[list[float|int|None], list[float|int|None]]
    - Shape and meaning:
        - The return is a list of two lists: [mins, maxs].
        - mins is [min0, min1] representing the minimum observed values of coordinate element 0 and element 1 across all points.
        - maxs is [max0, max1] representing the maximum observed values of coordinate element 0 and element 1 across all points.
        - Each entry may be a numeric (int or float) or None.
    - Possible outcomes:
        - If no coordinates are yielded by iter_coords(locations), returns [[None, None], [None, None]].
        - If exactly one point (a, b) is yielded, returns [[a, b], [a, b]].
        - For multiple points, mins and maxs reflect the aggregated minima and maxima of the first two axes.
        - If lonlat is True, the function returns whatever _locations_mirror(bounds) returns after the above computation.

## Raises:
    IndexError:
        If iter_coords yields a coordinate container with fewer than two elements, indexing point[0] or point[1] will raise IndexError.

    TypeError:
        May be raised when none_min/none_max attempt to compare two non-None values that are not mutually comparable (for example, comparing int and str). This is propagated directly from the built-in min/max comparisons used by none_min/none_max.

    Any exception raised by iter_coords:
        iter_coords may raise AttributeError, KeyError, TypeError, or IndexError for malformed mapping/sequence inputs — those will propagate to the caller.

## Constraints:
    Preconditions:
        - Caller must pass an object accepted by iter_coords (see iter_coords documentation): a mapping with GeoJSON-like keys or a nested sequence of coordinates.
        - If coordinates are intended to be 2D, ensure the leaf tuples/lists yielded by iter_coords are length >= 2.

    Postconditions:
        - The returned object is a nested list structure representing minima and maxima for the first two coordinate elements.
        - The returned minima and maxima are either None or exactly values that appeared in one of the yielded coordinate tuples.
        - No mutation is performed on the input locations by this function.

## Side Effects:
    - None intrinsic to get_bounds: no I/O, no global state mutation, no external calls other than calling the provided helper functions (iter_coords, none_min, none_max, and possibly _locations_mirror).
    - Note: iterating iter_coords may consume any iterator-like inputs passed inside locations (standard Python iteration behavior).

## Control Flow:
flowchart TD
    Start --> Init["bounds = [[None,None],[None,None]]"]
    Init --> Iterate["for point in iter_coords(locations)"]
    Iterate --> Update["update mins/maxs using none_min/none_max on point[0], point[1]"]
    Update --> Iterate
    Iterate --> DoneIter["after iteration completes"]
    DoneIter --> CheckLonlat{"lonlat is True?"}
    CheckLonlat -- Yes --> MirrorCall["_locations_mirror(bounds) -> return value"]
    CheckLonlat -- No --> Return["return bounds"]
    MirrorCall --> Return

## Examples:
- Typical 2D points:
    Input: locations = [[0, 1], [2, -1], [1, 3]]
    Behavior: iter_coords yields (0,1), (2,-1), (1,3)
    Output: [[0, -1], [2, 3]]

- Single point:
    Input: locations = [5, 10] (or a GeoJSON Point whose coordinates are [5,10])
    Behavior: yields (5,10)
    Output: [[5, 10], [5, 10]]

- Empty / no coordinates:
    Input: locations = [] or a mapping with no coordinates
    Output: [[None, None], [None, None]]

- Non-numeric or incompatible types:
    If coordinates mix incomparable types (e.g., [1, "a"]), the call may raise TypeError during comparison.

- Using lonlat:
    Input: locations as above, lonlat=True
    Behavior: get_bounds computes bounds as above and then returns the result of _locations_mirror(bounds). The exact returned shape/axis order depends on the _locations_mirror implementation.

Notes:
- get_bounds focuses only on the first two elements of each coordinate yielded by iter_coords; higher-dimensional coordinates are ignored beyond element index 1.
- This function intentionally delegates coordinate traversal and None-handling comparisons to iter_coords, none_min, and none_max respectively to keep behavior consistent across the codebase.

## `folium.utilities.camelize` · *function*

## Summary:
Converts a snake_case identifier into camelCase by removing underscores and capitalizing each segment after the first, producing a single camelCase string.

## Description:
Known callers within this repository snapshot:
    - No direct call sites were discovered in the provided snapshot. (Search for "camelize(" in a full checkout to locate usages.)

Typical contexts / when to use:
    - Translating Python-style snake_case keys (e.g., dict keys, option names, or attribute names) into camelCase names expected by JavaScript consumers, frontend configuration objects, or web APIs.
    - Performing key transformations during serialization or when building objects passed to libraries that follow camelCase conventions.

Why this is a separate function:
    - Centralizes the canonical transformation from snake_case to camelCase so all callers share consistent behavior.
    - Isolates the split-and-capitalize rule (including handling of empty segments and capitalization semantics) so edge cases are handled uniformly.

## Args:
    key (str): Input identifier in snake_case.
        - Expected type: str (string-like objects with the same split and capitalize semantics are sometimes accepted but not guaranteed).
        - Allowed values: any string, including the empty string and strings with leading, trailing, or consecutive underscores.
        - Interdependencies: None.
        - Required: yes (no default).

## Returns:
    str: The camelCase representation of the input.
    - Construction rule:
        * Split the input on the underscore character ('_') into segments.
        * Keep the first segment exactly as-is (no case changes).
        * For every subsequent segment, apply str.capitalize() (which uppercases the first character and lowercases the rest) and concatenate.
    - All notable cases:
        * No underscores: returns the original string unchanged (e.g., "tiles" -> "tiles").
        * Multiple segments: lower-case remainder of each subsequent segment per str.capitalize semantics (e.g., "a_b_c" -> "aBC").
        * Empty input: "" -> "" (empty string stays empty).
        * Leading underscore: "_a" -> "A" (first segment is empty string; next segment capitalized becomes the returned result).
        * Trailing underscore: "a_" -> "a" (final empty segment capitalized yields an empty string, so result is unchanged from preceding segments).
        * Consecutive underscores: "a__b" -> "aB" (empty middle segment contributes nothing).
        * Capitalization effect: "HTTP_server" -> "HTTPServer"; "http_SERVER" -> "httpServer" because subsequent segments are passed through str.capitalize().
    - If non-str inputs are passed, the function's behavior depends on those objects' split/capitalize implementations; when they produce non-str segments, the final join will raise a TypeError.

## Raises:
    - AttributeError: If key is None or does not provide a split method (e.g., camelize(None)).
    - TypeError: If any segment produced by split is not a str-like object so that "".join(...) cannot concatenate them (for example, if key is a bytes object producing bytes segments; the join of bytes with a str fails).
    - The function does not explicitly validate types; these exceptions originate from underlying string methods and the final join operation.

## Constraints:
    Preconditions:
        - Prefer passing a str. The implementation assumes str.split("_") returns an iterable of str segments and that str.capitalize() is valid for each segment.
    Postconditions:
        - The return value is a str (assuming input was a str) formed by concatenating the first segment unchanged followed by capitalized versions of subsequent segments.
        - No mutation of the input occurs.

## Side Effects:
    - None. Pure function: no I/O, no global state mutation, no network or filesystem access.

## Control Flow:
flowchart TD
    Start --> Split["split input on '_' -> segments"]
    Split --> Enumerate["enumerate(segments) -> (i, x) pairs"]
    Enumerate --> ForEach["for each (i, x)"]
    ForEach --> CheckIndex{"i > 0?"}
    CheckIndex -->|Yes| Capitalize["x.capitalize() -> capitalized segment (may be '')"]
    CheckIndex -->|No| Keep["x (first segment unchanged)"]
    Capitalize --> Collect["append to output list"]
    Keep --> Collect
    Collect --> NextItem["more segments?"]
    NextItem -->|Yes| ForEach
    NextItem -->|No| Join["''.join(collected segments)"]
    Join --> Return["return resulting string"]
    Return --> End

## Examples:
    - Typical usage:
        result = camelize("map_center")
        # result == "mapCenter"

    - Single word:
        result = camelize("tiles")
        # result == "tiles"

    - Multiple segments:
        result = camelize("a_b_c")
        # result == "aBC"

    - Empty string:
        result = camelize("")
        # result == ""

    - Leading underscore:
        result = camelize("_a")
        # segments ['', 'a'] -> result == "A"

    - Trailing underscore:
        result = camelize("a_")
        # segments ['a', ''] -> result == "a"

    - Consecutive underscores:
        result = camelize("a__b")
        # segments ['a', '', 'b'] -> result == "aB"

    - Capitalization behavior for subsequent segments:
        result = camelize("http_SERVER")
        # result == "httpServer" (subsequent segment is capitalized via str.capitalize())

    - Non-string input leads to TypeError on join:
        try:
            camelize(b"bytes_like")
        except TypeError:
            # join expects strings; handle or convert to str before calling
            pass

    - Bulk transform example (serialize dict keys for JS):
        python_obj = {"map_center": [0, 0], "tile_layer": "osm"}
        js_ready = {camelize(k): v for k, v in python_obj.items()}

## `folium.utilities._parse_size` · *function*

## Summary:
Parses a size input and normalizes it to a numeric value plus a unit tag ("px" for numeric inputs, "%" for non-numeric inputs).

## Description:
Parses an input that represents a size either as a numeric pixel value or as a percent string. The function returns a tuple (value, value_type) where value is a float and value_type is either "px" or "%".

Known callers within the provided code snapshot:
- No direct callers were identified in the supplied code snapshot. Typical callers in folium-like codebases are layout/element constructors or rendering helpers that accept width/height arguments (e.g., map, iframe, or control element factories) and need normalized numeric sizes for template rendering.

Why this function exists:
- Centralizes parsing, validation, and normalization of size inputs so callers do not duplicate logic for accepting integers/floats and percent strings, and so that consistent validation rules (positive pixel values, percent range 0–100) are enforced in a single place.

## Args:
value (int | float | str | any): The size to parse.
- If value is an int or float: it is treated as a pixel measurement and must be strictly greater than 0.
- If value is any other type (commonly a string): it is treated as a percentage representation. The code expects a string-like object supporting strip("%") followed by conversion to float; the percentage value must be in the inclusive range 0 to 100.
- Notes:
  - A numeric string without a trailing "%" (e.g., "50") is treated as a percentage (value_type "%"), not pixels.
  - Passing non-string, non-numeric objects (e.g., None) will result in a ValueError because the function attempts string operations / float conversion and will map all exceptions to ValueError.

## Returns:
tuple[float, str]:
- (value, value_type)
  - value (float): The parsed numeric value (float). For pixels it is the positive pixel magnitude; for percentages it is the numeric percentage value (0.0–100.0).
  - value_type (str): Either "px" when the original input was an int/float, or "%" when the input was treated as a percentage (non-numeric input).

All possible return examples:
- _parse_size(200) -> (200.0, "px")
- _parse_size(12.5) -> (12.5, "px")
- _parse_size("50%") -> (50.0, "%")
- _parse_size("0%") -> (0.0, "%")
- _parse_size("50") -> (50.0, "%")  (note: no trailing '%' — still treated as "%")

## Raises:
ValueError: Raised for any input that cannot be parsed according to the rules or violates range checks. The raised message follows the format:
- "Cannot parse value {!r} as {!r}".format(value, value_type)
Examples of conditions that trigger ValueError:
- Numeric pixel input <= 0 (e.g., -10, 0) — fails the assert that numeric pixels must be > 0.
- Percentage value outside the range 0..100 (e.g., "150%") — fails the assert for percent range.
- Non-numeric string that cannot be converted to float (e.g., "abc%") or non-string objects lacking required methods — any Exception during parsing is caught and re-raised as ValueError with the formatted message.

## Constraints:
Preconditions:
- Caller should pass either a numeric pixel value (int/float) or a string-like representation for percentage that can be stripped of '%' and converted to float.
- For pixel inputs: numeric value must be > 0.
- For percentage inputs: numeric value must be between 0 and 100 inclusive.

Postconditions:
- The function returns a tuple where the second element is either "px" or "%".
- If "px": the returned numeric value is a float strictly greater than 0.
- If "%": the returned numeric value is a float in the inclusive range [0.0, 100.0].
- If parsing fails or a precondition is violated, the function raises ValueError and does not return.

## Side Effects:
- None. The function does not perform any I/O, global state mutation, or external service calls. All exceptions are caught and transformed into ValueError for the caller.

## Control Flow:
flowchart TD
    A[Start: receive value] --> B{isinstance(value, (int, float))?}
    B -- Yes --> C[value_type = "px"]
    C --> D[value = float(value)]
    D --> E{value > 0 ?}
    E -- Yes --> F[Return (value, "px")]
    E -- No --> G[Raise ValueError("Cannot parse value ... as 'px'")]
    B -- No --> H[value_type = "%"]
    H --> I[value = float(value.strip("%"))]
    I --> J{0 <= value <= 100 ?}
    J -- Yes --> K[Return (value, "%")]
    J -- No --> L[Raise ValueError("Cannot parse value ... as '%'")]
    note right of I: any exception in strip/float is caught and re-raised as ValueError

## Examples:
- Successful usages:
  - _parse_size(200)  => (200.0, "px")
  - _parse_size(12.5) => (12.5, "px")
  - _parse_size("50%") => (50.0, "%")
  - _parse_size("0%") => (0.0, "%")
  - _parse_size("50") => (50.0, "%")  (string without '%' is treated as percentage)

- Error handling examples:
  - _parse_size(-5) raises ValueError - numeric pixel values must be > 0
  - _parse_size("150%") raises ValueError - percent must be in 0..100
  - _parse_size("abc") raises ValueError - cannot convert to float

Usage note for callers:
- If you intend to allow numeric strings to mean pixels (e.g., "200" -> 200px), perform that conversion before calling this function or wrap calls to detect and handle such semantics — this function treats all non-numeric Python numeric types as percentages by design.

## `folium.utilities.compare_rendered` · *function*

## Summary:
Compares two rendered values for equivalence after applying the same normalization rules to each, returning True when their normalized forms are equal and False otherwise.

## Description:
Compares two arbitrary values by normalizing each with the shared normalize utility and then performing an equality comparison on the normalized results.

Known callers within the provided codebase:
- None listed in the provided context. In typical usage within rendering or templating utilities, this function is used by test helpers or rendering code paths that need to decide whether two rendered outputs (e.g., short HTML fragments, labels, tooltips) are semantically identical after whitespace and punctuation normalization.

Why this is a separate function:
- Encapsulates the common pattern "normalize then compare" so callers do not need to duplicate normalization calls and can rely on a single, well-tested point of truth for equivalence checks.
- Improves readability where intent is "are these renderings equivalent?" and keeps equality semantics consistent across the codebase.
- Simplifies unit testing (compare_rendered itself can be tested once instead of repeating normalization checks in many places).

## Args:
    obj1 (any):
        - The first value to compare. It will be passed directly to normalize(obj1).
        - Typical inputs: str or falsy values (None, '', False). If non-falsy but non-str, behavior depends on normalize (may raise).
    obj2 (any):
        - The second value to compare. It will be passed directly to normalize(obj2).
        - Same type expectations and caveats as obj1.

Notes on interdependencies:
    - Both values are independently normalized. The comparison is performed on the normalized outputs; no short-circuiting is done before normalization.
    - Passing the exact same object for obj1 and obj2 still results in normalization being called twice (no identity shortcut).

## Returns:
    bool:
        - True if normalize(obj1) == normalize(obj2).
        - False otherwise.
    Edge cases:
        - If both inputs are the same falsy value (for example, None and None), normalize returns the same falsy value for each and the function returns True.
        - If normalize produces differing types for the two inputs that are still comparable via ==, the equality semantics of Python apply.
        - If normalize raises an exception for either input, the exception propagates and no boolean is returned.

## Raises:
    - No exceptions are explicitly raised by compare_rendered itself.
    - Implicit exceptions are propagated from normalize (documented in normalize). Common ones callers may need to handle:
        * TypeError: if a non-falsy, non-str-like object is provided to normalize and operations inside normalize expect str.
        * AttributeError: if the input does not support methods used by normalize (split, replace, strip).
        * Any other exception raised by normalize or by the equality comparison implementation of returned objects will propagate.

## Constraints:
    Preconditions:
        - If inputs are non-falsy, they should behave like str (support split, replace, strip) to avoid implicit exceptions from normalize.
        - Callers that cannot guarantee string-like inputs should coerce (e.g., decode bytes to str or str() cast) or catch exceptions.

    Postconditions:
        - The function returns a boolean indicating whether the normalized representations are equal.
        - No inputs are modified by this function.
        - No global or external state is changed.

## Side Effects:
    - None. The function is pure: it performs no I/O, does not mutate global state, and only calls normalize (which itself is pure string transformation).

## Control Flow:
flowchart TD
    Start --> CallNormalize1[Call normalize(obj1)]
    CallNormalize1 --> CallNormalize2[Call normalize(obj2)]
    CallNormalize2 --> Compare[Compute normalized1 == normalized2]
    Compare --> ReturnBool[Return True or False based on equality]
    CallNormalize1 -->|normalize raises| PropagateError1[Propagate exception]
    CallNormalize2 -->|normalize raises| PropagateError2[Propagate exception]

## Examples:
- Simple equivalence (whitespace/punctuation differences normalized away):
    Input: obj1 = "Hello  world...", obj2 = "Hello world."
    Outcome: normalize(obj1) == normalize(obj2) -> True

- Falsy inputs preserved and compared:
    Input: obj1 = None, obj2 = None
    Outcome: normalize(None) == normalize(None) -> True

- Non-string or potentially invalid input (defensive pattern):
    If callers cannot guarantee string-like inputs, they should coerce or handle errors:
      * Decode bytes to str before calling, or
      * Wrap the call in a try/except to catch TypeError/AttributeError propagated from normalize.

- Example (pseudo-step):
    1) Prepare two rendered fragments from different renderers.
    2) Call compare_rendered(fragment_a, fragment_b).
    3) If True, treat them as equivalent and skip updating the output; if False, update the output.

## `folium.utilities.normalize` · *function*

## Summary:
Clean and normalize a rendered text value by collapsing whitespace, normalizing common quote/dash/ellipsis characters, and making spacing around basic punctuation consistent; returns the trimmed, human-readable string or returns the original falsy input unchanged.

## Description:
This utility performs a small series of text-cleanup steps suitable for final presentation of short human-readable strings (e.g., labels, tooltips, small HTML snippets). It is intended to be called near the end of a rendering pipeline to remove accidental extra whitespace and to normalize a few common typographic variants into simple ASCII forms.

Known callers within the codebase:
- None listed in the provided context. In practice within folium-like projects it is used by rendering or templating utilities to finalize strings before insertion into HTML or other outputs.

Why this logic is a separate function:
- Consolidates many small, fragile string-cleanup rules into a single, testable place.
- Keeps rendering code focused on structure while delegating presentation normalization to one utility.
- Makes it straightforward to adjust or extend normalization rules without touching template/render logic.

## Args:
    rendered (str | falsy):
        - Type: expected to be a str when non-falsy.
        - Behavior for falsy values: if rendered is falsy (None, '', False, 0), the function returns that exact falsy value immediately without performing normalization.
        - If a non-falsy value that is not a str is passed (e.g., bytes, numeric types), the function may raise implicit exceptions (see Raises).

## Returns:
    str | same falsy input:
        - If input is falsy, returns the same object/value unchanged (for example, None -> None, '' -> '').
        - If input is a non-empty string, returns a new str with the following effects:
            * Collapses all runs of whitespace (spaces, tabs, newlines, etc.) into single spaces.
            * Replaces double double-quotes ("") with a single double-quote (").
            * Replaces double single-quotes ('') with a single single-quote (').
            * Replaces en-dash (–) and em-dash (—) with ASCII hyphen (-).
            * Replaces every occurrence of three consecutive dots ("...") with a single period ('.').
            * Removes spaces immediately before punctuation characters: , . : ; ! ?
            * Ensures a single space after punctuation characters , . : ; ! ? when followed by an ASCII letter (a–z or A–Z). Note: the regex uses [a-zA-Z] and therefore only matches ASCII letters.
        - The returned string is stripped of leading/trailing whitespace.

## Raises:
    - No explicit exceptions are raised by the code.
    - Implicit exceptions that callers should be aware of:
        * TypeError may occur if a non-falsy, non-str object is provided (for example, passing bytes will cause the string join to fail because ' '.join expects str items).
        * AttributeError may occur if a non-string object lacks the split/replace/strip methods used.
    - Callers should validate or coerce inputs to str if there is any chance of receiving bytes or other types.

## Constraints:
    Preconditions:
        - If the input is non-falsy, it must behave like a str (support split, replace, strip). Prefer passing a str to avoid implicit exceptions.
        - The punctuation-followed-by-letter normalization uses ASCII letters only; Unicode letters (é, ü, Cyrillic, etc.) are not matched by the [a-zA-Z] pattern.

    Postconditions:
        - Falsy inputs are returned exactly as received.
        - Non-empty string inputs are returned as a str with normalized whitespace and punctuation spacing as described above.
        - No external state is modified.

## Side Effects:
    - None. The function performs pure string transformations and does not perform I/O, mutate globals, or interact with external services.

## Control Flow:
flowchart TD
    Start --> IsFalsy{Is input falsy?}
    IsFalsy -- Yes --> ReturnFalsy[Return input unchanged]
    IsFalsy -- No --> CollapseWS[Collapse whitespace using ' '.join(split())]
    CollapseWS --> ReplaceQuotes[Replace "" -> " and '' -> ']
    ReplaceQuotes --> ReplaceDashes[Replace en-dash/em-dash -> -]
    ReplaceDashes --> ReplaceEllipsis[Replace "..." -> "."]
    ReplaceEllipsis --> RemoveSpaceBefore[Remove spaces before , . : ; ! ?]
    RemoveSpaceBefore --> EnsureSpaceAfter[Ensure single space after , . : ; ! ? when followed by ASCII letter]
    EnsureSpaceAfter --> FinalStrip[Strip leading/trailing whitespace]
    FinalStrip --> ReturnStr[Return normalized string]
    ReturnStr --> End

## Examples:
- Collapse whitespace and replace ellipsis:
    Input: "Hello   world  ..."
    Output: "Hello world."

- Fix punctuation spacing:
    Input: "Wait ,please!Are  you  ok?"
    Processing highlights:
      * Remove space before ',' -> "Wait,please!Are you ok?"
      * Ensure space after '!' before ASCII letters -> "Wait,please! Are you ok?"
      * Collapse whitespace -> "Wait, please! Are you ok?"
    Output: "Wait, please! Are you ok?"

- Normalize quotes and dashes (accurate reflection of the function's behavior):
    Input: 'He said: ""Hello'' —and left.'
    Processing:
      * '""' -> '"'  and "''" -> "'"  (may yield unmatched quotes if input is unbalanced)
      * em-dash -> '-'
      * punctuation spacing applied only for , . : ; ! ? and ASCII letters
    Output (exact): 'He said: "Hello' -and left.'  (note: hyphen adjacency and unmatched single-quote remain because the function does not remove unmatched quotes or adjust hyphen spacing except via punctuation rules)

- Falsy preserved:
    Input: None
    Output: None

- Defensive caller pattern:
    If input may be bytes, decode first:
      try:
          text = value.decode('utf-8') if isinstance(value, bytes) else str(value)
      except Exception:
          handle_invalid_input()
      else:
          normalized = normalize(text)

## `folium.utilities.temp_html_filepath` · *function*

## Summary:
Creates a temporary .html file containing the provided data, yields the file path to the caller, and ensures the temporary file is removed when the generator is finalized.

## Description:
This function is implemented as a generator that performs three responsibilities: (1) create a uniquely-named temporary file with an ".html" suffix, (2) write the given data into that file, and (3) yield the file path for use by the caller. The finally block removes the file from disk when the generator is finalized (e.g., when the generator is closed or when used via a context manager wrapper).

Known callers within the codebase:
- No direct callers were found in the provided repository snapshot for this exact function name. It is implemented to be used where a consumer needs a short-lived HTML file path (for example, to hand to a browser, an OS-level preview, or a subprocess that requires a path).

Why this logic is extracted into its own function:
- Encapsulates the lifecycle of a temporary HTML file (creation, write, and cleanup) so callers do not need to manage file naming, encoding, removal, or error-prone cleanup manually.
- Keeps file I/O and cleanup concerns separate from higher-level code that only needs to consume a path to an on-disk HTML file.

## Args:
    data (str | bytes):
        Content to write into the temporary file.
        - If a str is provided, it is encoded to UTF-8 before writing.
        - If bytes are provided, they are written as-is.
        - Any other type will result in a lower-level error when os.write is invoked (TypeError or similar).

## Returns:
    generator that yields:
        filepath (str): Absolute path to the newly-created temporary file (string).
    Behavior details:
        - The function is a generator (it uses yield). The caller receives the filepath by advancing the generator (e.g., next(gen) or using a context manager wrapper).
        - After the generator completes (finally block executes) the file is removed from disk if it exists.
        - The generator does not explicitly return a value after yield; it yields exactly once.

## Raises:
    OSError:
        - If tempfile.mkstemp or os.write or os.close fail due to OS-level errors (disk full, permission denied, etc.), the error will propagate.
    TypeError:
        - If data is neither str nor bytes (os.write will raise when passed a non-bytes-like object).
    Note:
        - The function itself does not catch these exceptions; callers should handle them as needed.

## Constraints:
Preconditions:
    - Caller must be prepared to handle the fact that this is a generator; to guarantee cleanup the generator must be finalized (by closing, exhausting, or using a context-manager wrapper).
    - The environment must permit creation and deletion of files in the system temporary directory.

Postconditions:
    - If the generator's finally block is executed, the temporary file will be removed from disk (os.path.isfile(filepath) check before removal).
    - If the generator is abandoned without being closed (e.g., never resumed or closed), the finally block may not run and the file may remain on disk until process exit or external cleanup.

## Side Effects:
    - Creates a temporary file on disk with a name of the form folium_<random>*.html in the platform temporary directory.
    - Writes the provided data to that file (I/O).
    - Removes the file during cleanup (I/O).
    - No network calls, global variable mutation, or external database/cache access are performed by this function.

## Control Flow:
flowchart TD
    Start --> CreateTempFile[mkstemp(suffix=".html", prefix="folium_")]
    CreateTempFile --> WriteData{is data str?}
    WriteData -->|yes| EncodeAndWrite[data.encode("utf8") -> os.write]
    WriteData -->|no| WriteRaw[os.write(data)]
    EncodeAndWrite --> CloseFD[os.close(fid)]
    WriteRaw --> CloseFD
    CloseFD --> YieldPath[yield filepath]
    YieldPath --> CallerUsesPath[caller uses filepath]
    CallerUsesPath --> Finalize[generator finalized/closed/exhausted]
    Finalize --> ExistsCheck{os.path.isfile(filepath)?}
    ExistsCheck -->|yes| RemoveFile[os.remove(filepath)]
    ExistsCheck -->|no| End
    RemoveFile --> End
    End --> Stop

## Examples:
- Using the generator API directly (manual lifecycle management):
  1) gen = temp_html_filepath("<html>...</html>")
  2) filepath = next(gen)               # create file and get path
  3) try:
         use filepath (open it, pass to a subprocess, etc.)
     finally:
         gen.close()                    # triggers finally and removes file

- Using contextlib.contextmanager to use as a with-statement (recommended for automatic cleanup):
  1) from contextlib import contextmanager
  2) temp_html_ctx = contextmanager(temp_html_filepath)
  3) with temp_html_ctx("<html>...</html>") as filepath:
         use filepath inside the with-block
     # when the with-block exits, the temporary file is removed

Notes and usage tips:
    - Prefer the contextmanager wrapper shown above to ensure deterministic cleanup even in the presence of exceptions.
    - Be aware that if os.write raises before os.close is reached, the file descriptor may not be closed by this function; consider wrapping calls at a higher level if you need stricter resource guarantees.
    - Do not assume the filepath remains valid after the generator is finalized; callers must perform all work that requires the file while the generator/context is active.

## `folium.utilities.deep_copy` · *function*

## Summary:
Creates and returns a shallow-copied replica of a tree-like element, assigning a fresh unique identifier and recursively copying any child elements so that the returned object and its children form a separate tree with correct parent links.

## Description:
deep_copy performs a shallow copy of the provided object and then, if the object exposes a non-empty _children mapping, recursively duplicates each child and replaces the copied object's _children with a new OrderedDict of those child copies. Each copied child has its _parent attribute set to the newly copied parent and is inserted into the new children mapping using the child's get_name() value as the key.

Known callers within the current codebase snapshot:
    - No direct callers were discovered in the provided repository snapshot. (A repository-wide search did not return call sites in memory at the time of documentation generation.)

Typical usage context:
    - This function is intended for use when creating an independent duplicate of an object tree composed of objects that follow the child/parent pattern: objects that optionally expose a _children mapping (mapping-like object with len() and values()), whose values are child elements exposing a get_name() method, and that use _parent references to point to parents. It encapsulates the responsibility of cloning node identity and parent/child structure while avoiding inlining this logic at many call sites.

Reason for extraction:
    - The recursive traversing and re-linking logic is a self-contained concern (duplicate node identity and reconstruct child->parent links) and is therefore extracted to ensure consistent behavior across the codebase and to avoid replication of recursion and ordering logic.

## Args:
    item_original (object):
        The object to duplicate. Expected characteristics:
            - May have an attribute _id (string) but it's not required—the function will set/override item._id.
            - Optionally has an attribute _children which must be a mapping-like container when present:
                * Must support len(item._children) and item._children.values().
                * The values() iterator must yield child objects for recursion.
            - Child objects yielded by _children.values() must provide a get_name() method (callable that returns a hashable key).
        Allowed values: any Python object; if the object does not conform to the expectations above, the function may raise AttributeError, TypeError, or other exceptions as described below.

## Returns:
    object:
        The shallow-copied object (not the original). Guarantees:
            - item._id is set to a new unique hex string generated by uuid.uuid4().hex.
            - If the original had a non-empty _children mapping:
                * The returned object's _children is replaced with a new collections.OrderedDict containing the recursively copied children.
                * Each child in the new mapping is a shallow copy of the original child (produced by a recursive deep_copy call).
                * Each copied child has its _parent attribute set to the returned parent object.
                * Keys in the new children OrderedDict are the values returned by each child's get_name() method.
        Edge-case returns:
            - If the original object lacks a _children attribute or it is empty (len == 0), the returned object will be a shallow copy with only a new _id and no modifications to children.
            - The function always returns a new object reference distinct from item_original (a shallow copy); however, non-child attributes that reference mutable objects remain shared with the original because copy.copy is used.

## Raises:
    AttributeError:
        - Raised if a required attribute is missing at a point where the code accesses it, for example:
            * item_original has a _children attribute but that attribute lacks a values() method or get_name() is missing on a child object.
            * A child returned by item._children.values() does not implement get_name().
    TypeError (or other exceptions propagated from copy.copy):
        - If copy.copy cannot create a shallow copy of item_original, a TypeError or other exception from the copy machinery may be propagated.
    RecursionError:
        - If the object graph is excessively deep (very deep nested children), recursion can exhaust the Python recursion limit.
    Note:
        - The function does not raise new custom exceptions; it propagates errors from shallow-copying and attribute access.

## Constraints:
Preconditions:
    - The caller should ensure that item_original represents a node in a tree-like structure that adheres to the expected minimal interface if children are present:
        * If item_original has _children, it should be a mapping-like object with a working __len__ and values() method.
        * Children yielded by values() should implement get_name() and be copyable via copy.copy.
Postconditions:
    - Returned object has a new _id string (uuid4 hex).
    - If children existed, returned object's _children is an OrderedDict whose values are fresh shallow copies of original child objects, and each copied child's _parent points to the returned parent.
    - The original item_original and its child objects are not modified by deep_copy (the function constructs new copies for returned items and their children). Non-child attributes that are shared references remain shared because shallow copying is used.

## Side Effects:
    - Mutates attributes on the returned objects only:
        * Sets item._id to a new uuid4 hex string on the returned item.
        * Sets subitem._parent on returned child copies to the new parent copy.
    - No I/O is performed (no file, network, or stdout/stderr interaction).
    - No global variables, caches, or external services are modified.
    - The original input objects are not intentionally modified by the function (except insofar as copy.copy may call user-defined __copy__ which could have side effects; any such side effects would come from the object's own copy implementation).

## Control Flow:
flowchart TD
    A[Start: receive item_original] --> B[Create shallow copy via copy.copy -> item]
    B --> C[Set item._id = uuid.uuid4().hex]
    C --> D{hasattr(item, "_children") and len(item._children) > 0?}
    D -- No --> G[Return item]
    D -- Yes --> E[Create children_new = OrderedDict()]
    E --> F[For each subitem_original in item._children.values():]
    F --> F1[subitem = deep_copy(subitem_original)] --> F2[subitem._parent = item] --> F3[children_new[subitem.get_name()] = subitem] --> F (loop)
    F -- loop complete --> H[item._children = children_new]
    H --> G[Return item]

## Examples:
Usage pattern (descriptive steps):
    1. Prepare a root element object that optionally has:
         - a mapping-like _children attribute (for example, an OrderedDict or dict) whose values are child element objects,
         - child objects exposing a get_name() method and optionally a _parent attribute.
    2. Call deep_copy(root_element). The call returns a new object which:
         - has a new unique _id,
         - if root_element had children, the returned root's _children is an OrderedDict of child copies keyed by each child's get_name(),
         - each copied child's _parent is set to the returned parent.
    3. Handle potential exceptions:
         - If a child lacks get_name(), an AttributeError will be raised; validate the child interface before calling if needed.
         - For very deep trees, be prepared to catch RecursionError.

Realistic example scenario (prose):
    - When programmatically duplicating a UI/element tree (for example to render a copy without changing the original), call deep_copy on the root element. This will yield a new tree where node identities (_id) differ and parent references point to the new nodes rather than the originals. After deep_copy, you can mutate the returned tree (add/remove children, change attributes) without affecting the original structure, except for any shared mutable attributes that were not explicitly deep-copied (because this function uses shallow copies for object fields other than the child mapping).

Important implementation notes (for callers and implementers):
    - Because copy.copy (shallow copy) is used, attributes that are references to mutable objects (lists, dicts, etc.) remain shared between the original and the copy unless those attributes are part of the _children recursive copying. If complete independence is required for all nested mutable attributes, callers should perform deeper copying of those attributes themselves or adjust deep_copy accordingly.
    - The function expects get_name() to return unique keys for children. If multiple children return the same name, later children will overwrite earlier entries in the resulting OrderedDict.

## `folium.utilities.get_obj_in_upper_tree` · *function*

## Summary:
Traverse an object's parent links (via the _parent attribute) upward and return the nearest ancestor that is an instance of the provided class; raise ValueError when the top of the chain is reached without a match.

## Description:
This helper walks the implicit parent-linked tree formed by the attribute named _parent on elements. It reads element._parent, checks whether that parent is an instance of cls, and if not, repeats the process on the parent until a matching ancestor is found or traversal can no longer continue.

Known callers within the provided scan:
    - No direct call sites were found in the supplied scan. Typical use-cases (not confirmed here) include child widgets or layers that need to locate the nearest container object (for example, finding the parent Map, Layer, or FeatureGroup from a nested element).

Why this logic is a standalone function:
    - Centralizes ancestor-lookup logic and top-of-tree termination handling so callers do not duplicate recursive traversal and error message construction.
    - Encapsulates the invariant "walk parent links until you find an instance of cls or fail" so callers simply request the nearest ancestor by type.

## Args:
    element (object):
        Any Python object expected to be part of a parent-linked tree where each intermediate node exposes a _parent attribute that points to its ancestor. The function does not require element itself to be an instance of cls; it always begins by inspecting element._parent.
        Notes:
            - If element has no attribute named _parent, the function immediately raises ValueError.
            - If element._parent exists but is None, the function will handle that value (see Returns and Raises).

    cls (type or tuple[type, ...]):
        A class object or a tuple of class objects accepted by isinstance as its classinfo parameter.
        Notes:
            - Passing an invalid cls (anything not accepted by isinstance, such as an integer or other non-type) will cause isinstance to raise a TypeError; this function does not catch that error.

## Returns:
    object or None:
        - The nearest ancestor object (one of element._parent, element._parent._parent, ...) that is an instance of cls.
        - If cls is type(None) (the NoneType) and an ancestor in the chain equals None, the function will return that None ancestor (i.e., it can legitimately return None).
        - The function never returns a sentinel to indicate "not found"; instead it raises ValueError when traversal terminates without a matching ancestor.

## Raises:
    ValueError:
        - Raised when the traversal cannot continue because the current element (on any recursive call) does not have an attribute named _parent. The exact message produced is:
            "The top of the tree was reached without finding a {cls}"
        where {cls} is the string/interpolated representation of the cls argument.
        Examples of situations producing this ValueError:
            * The initial element does not have _parent.
            * During traversal, a parent value is None (or any object) that does not have attribute _parent, causing the next recursive call to detect the missing _parent and raise ValueError (unless that parent matched cls before recursion).

    TypeError:
        - Raised indirectly if cls is not a valid argument for isinstance (for example, passing an integer or other non-type), because isinstance(parent, cls) will raise TypeError. This function does not intercept that exception.

    RecursionError:
        - If the ancestor chain length exceeds the Python recursion limit, recursive calls may raise RecursionError. This is an indirect consequence of the recursive implementation.

## Constraints:
    Preconditions:
        - Caller should supply an element that is part of a parent-linked structure using _parent attributes on intermediate nodes, or be prepared to handle ValueError.
        - cls must be a type or tuple of types acceptable to isinstance.

    Postconditions:
        - On successful return, the returned value is an ancestor of the original element (reached by following one or more _parent attributes) and is an instance of cls.
        - If the function completes without raising, the caller can assume a matching ancestor was found and returned.

## Side Effects:
    - None: the function performs no I/O and does not mutate the element or any ancestor; it only reads _parent attributes.
    - No global state or external services are used.

## Control Flow:
flowchart TD
    Start[Start: call get_obj_in_upper_tree(element, cls)]
    HasParent{does element have attribute _parent?}
    Start --> HasParent
    HasParent -- No --> RaiseValueError[Raise ValueError: "The top of the tree was reached without finding a {cls}"]
    HasParent -- Yes --> SetParent[Set parent = element._parent]
    SetParent --> IsInstance{is parent an instance of cls?}
    IsInstance -- Yes --> ReturnParent[Return parent (may be None if cls is NoneType)]
    IsInstance -- No --> Recurse[Call get_obj_in_upper_tree(parent, cls)]
    Recurse --> Start

## Examples (realistic usage and error handling described):
    Example — successful lookup:
        - Context: child._parent -> layer, layer._parent -> map; both layer and map expose _parent attributes.
        - Action: ask for the nearest Map ancestor by invoking the helper with the child and Map as cls.
        - Outcome: the Map instance (an ancestor) is returned.

    Example — ancestor is None and cls is NoneType:
        - Context: an element has _parent attribute set to None (explicit top marker).
        - Action: call helper with cls set to type(None).
        - Outcome: the function checks element._parent (which is None), isinstance(None, type(None)) is True, and the function returns None.

    Example — top reached without matching ancestor:
        - Context: ancestors exist as objects but none are instances of the requested class, and eventually a node without a _parent attribute or a None without matching NoneType is encountered.
        - Action: call helper and catch ValueError.
        - Outcome: the function raises ValueError with the message shown above; caller can handle this by creating a fallback ancestor or surfacing the error.

    Example — invalid cls argument:
        - Context: caller mistakenly passes cls=42 (an int).
        - Action: call helper; isinstance will raise TypeError.
        - Outcome: the caller should validate cls before calling or be prepared to handle TypeError.

Notes and implementation advice:
    - If the parent chain may be extremely deep, prefer an iterative implementation to avoid RecursionError.
    - Validate cls (e.g., ensure it is a type or tuple of types) before calling the helper if you want to avoid propagating TypeError from isinstance.

## `folium.utilities.parse_options` · *function*

## Summary:
Transforms keyword arguments into a dictionary whose keys are converted from snake_case to camelCase and whose values exclude any entries with value None.

## Description:
Known callers within this codebase:
    - folium.map.Tooltip.parse_options: used when preparing option dictionaries for tooltip objects before validation and serialization to JavaScript.

Typical usage/context:
    - Convert Python-style option names (snake_case) supplied as kwargs into camelCase keys expected by front-end JavaScript APIs or Leaflet configuration objects, while omitting options explicitly set to None.
    - This function is used as a small normalization step in the pipeline that collects Python kwargs, normalizes their names, removes absent options, and then passes the result to validators or serializers.

Reason for extracting this logic:
    - Centralizes the naming normalization and None-filtering behavior so multiple map components can share consistent preprocessing.
    - Keeps callers focused on validation/serialization logic (type checks, allowed keys) by providing a single responsibility helper for key normalization and omission of absent options.

## Args:
    **kwargs: Any keyword arguments mapping names to values.
        - Expected key types: str is expected and typical; non-str keys are accepted syntactically but will be passed to camelize and may raise exceptions.
        - Value semantics: any Python object is allowed as a value. Entries whose value is exactly None are removed from the output.
        - Interdependencies: None between keys or values. If multiple keys normalize to the same camelCase name, the later one in kwargs iteration order will overwrite earlier ones.

## Returns:
    dict[str, Any]: A dictionary containing:
        - Keys: result of converting each original keyword name with camelize(key). Keys corresponding to values that were None are omitted.
        - Values: identical objects to the provided values (no transformation).
    Edge cases and details:
        - If a keyword value is None, that key/value is not present in the returned dict.
        - If two different kwargs produce the same camelCase key (e.g., "a_b" and "aB"), the last occurrence in the kwargs iteration order wins and overwrites previous values.
        - If kwargs is empty, an empty dict is returned.

## Raises:
    - Any exception raised by camelize(key) will propagate. Typical exceptions include:
        * AttributeError: if a key is None or doesn't provide the required string methods (e.g., split/capitalize).
        * TypeError: if camelize attempts to join non-str segments (occurs when non-str-like keys are used and their split/capitalize yield incompatible types).
    - parse_options itself does not explicitly raise its own exceptions; exceptions arise from camelize or from unusual key types.

## Constraints:
    Preconditions:
        - Prefer passing string keys (snake_case). The implementation assumes camelize can operate on each key.
        - Callers should not rely on preserving keys whose values are None; such entries are intentionally omitted.
    Postconditions:
        - The returned dict's keys are the camelCase forms of the provided keys (assuming camelize succeeds) and none of the returned values are None.
        - No mutation occurs to the original kwargs objects.

## Side Effects:
    - None. The function is pure with respect to external state: it performs in-memory transformations only and does not perform I/O, network access, or mutate global state.

## Control Flow:
flowchart TD
    Start --> Receive["receive kwargs mapping"]
    Receive --> Iterate["for each (key, value) in kwargs.items()"]
    Iterate --> CheckNone{"value is None?"}
    CheckNone -->|Yes| Skip["skip this key (do not add to result)"]
    CheckNone -->|No| Camelize["call camelize(key)"]
    Camelize --> Add["add/overwrite result[camel_key] = value"]
    Add --> Next["more items?"]
    Next -->|Yes| Iterate
    Next -->|No| Return["return result dict"]
    Return --> End

## Examples:
    - Basic filtering and camelization:
        result = parse_options(color='red', fill_opacity=None, max_zoom=18)
        # result == {'color': 'red', 'maxZoom': 18}

    - Keys already camelCase are preserved:
        result = parse_options(tileSize=256, background_color='white')
        # result == {'tileSize': 256, 'backgroundColor': 'white'}

    - Duplicate keys after normalization (later wins):
        result = parse_options(a_b=1, aB=2)
        # camelize('a_b') -> 'aB', camelize('aB') -> 'aB'
        # result == {'aB': 2}  (the second argument overwrites the first)

    - Non-string key (will raise when camelize is called):
        try:
            result = parse_options(**{None: 'x'})
        except AttributeError:
            # camelize(None) raises; callers should ensure keys are strings
            pass

    - Typical integration pattern in a component:
        # component receives kwargs from user, normalizes them, then validates:
        normalized = parse_options(**user_kwargs)
        validated = component_specific_validation(normalized)
        component_emit_to_js(validated)

## `folium.utilities.escape_backticks` · *function*

## Summary:
Escape every unescaped backtick in the input string by prefixing it with a single backslash, leaving backticks that are already immediately preceded by a backslash unchanged.

## Description:
This small utility performs a targeted text sanitization: it finds backtick characters (`) that are not immediately preceded by a backslash (\) and replaces each with the two-character sequence backslash + backtick (\`). It is typically used before embedding user-provided text into contexts where literal backticks might be interpreted (for example, insertion into JavaScript/HTML templates or Markdown fragments) to prevent unintentional code spans or delimiter termination.

Known callers within this repository:
    - No direct callers were found in the provided repository scan. Typical call sites in folium-like codebases would be template rendering or JavaScript string construction functions that must ensure embedded text does not inject raw backticks.

Why this logic is a dedicated function:
    - Centralizes a single escaping rule so callers do not duplicate regular-expression logic.
    - Improves testability and future maintainability (behavior can be changed in one place).
    - Keeps rendering logic free of low-level escaping details.

## Args:
    text (str)
        - Required. The input text to transform.
        - Must be a Python str object. Because the regular expression pattern and replacement are specified as str literals, passing a bytes object will raise a TypeError.
        - If callers may pass other types, they should explicitly coerce to str (for example, str(value)) before calling.

## Returns:
    str
        - A new string derived from the input where each backtick character that was not immediately preceded by a backslash is replaced by a backslash + backtick sequence.
        - If the input is the empty string, the function returns the empty string.
        - The original string is not modified (strings are immutable); a fresh str value is returned.

## Raises:
    TypeError
        - Raised by the underlying regular expression implementation if `text` is not a str. Specifically, because both the regex pattern and replacement are str literals, supplying a bytes object for `text` results in TypeError.
        - For example, calling the function with None, an int, or bytes will trigger this exception unless the caller converts the value to str first.

    re.error
        - Not possible in this implementation because the pattern and replacement are fixed valid str literals; therefore re.error will not be raised by this function as written.

## Constraints:
    Preconditions:
        - Caller should provide a Python str. Non-str inputs must be converted beforehand.
        - The escaping decision inspects only the single character immediately before each backtick (a simple negative lookbehind); it does not compute the parity (even/odd) of runs of backslashes.

    Postconditions:
        - In the returned string, every backtick whose immediate preceding character in the original input was not a backslash will now be preceded by a single backslash.
        - Backticks that were immediately preceded by a backslash in the input remain unchanged (they are not double-escaped).
        - No other characters are added or removed except the inserted backslashes required for escaping.

Important behavioral detail:
    - Because the implementation uses a negative lookbehind (?<!\\), only the single preceding character matters. For sequences of multiple backslashes before a backtick, the decision uses the last character before the backtick:
        * If that last character is a backslash, the backtick is considered already escaped and left unchanged.
        * If that last character is not a backslash, the backtick is escaped.
    - This means the function does not normalize or interpret backslash-run parity; it only enforces "do not add another backslash when a backslash immediately precedes the backtick."

## Side Effects:
    - None. The function performs no I/O and does not mutate external or global state.

## Control Flow:
    flowchart TD
        Start([Start])
        Input["Receive input: text (must be str)"]
        Iterate["Scan text for backtick characters (`)"]
        Check["For each backtick, is the immediately preceding character a backslash?"]
        Replace["If NOT preceded by backslash → replace ` with \\`"]
        Keep["If preceded by backslash → leave ` unchanged"]
        Return["Construct and return transformed string"]
        End([End])

        Start --> Input --> Iterate --> Check
        Check -->|No preceding backslash| Replace --> Return --> End
        Check -->|Preceded by backslash| Keep --> Return --> End

## Examples:
    1) Basic escaping
        Input (display):    Hello `world`
        Returned:           Hello \`world\`
        Notes: Both unescaped backticks are prefixed with backslashes.

    2) Already escaped backticks remain unchanged
        Input (display):    Already escaped: \`code\`
        Returned:           Already escaped: \`code\`
        Notes: Backticks that are immediately preceded by a backslash are not double-escaped.

    3) Mixed run of backslashes before a backtick
        Input (display):    example: \\`a`
        Returned:           example: \\`a\`
        Notes:
            - The backtick immediately following the two backslashes is preceded by a backslash (the last of the two), so it is left unchanged.
            - The backtick after 'a' is not preceded by a backslash, so it is escaped.

    4) Non-str input should be coerced
        - If the caller has a value that may be None or bytes, explicitly convert it:
            * Good: escape_backticks(str(value))
            * Bad: escape_backticks(b"`")   # bytes -> raises TypeError
        - Passing None, an int, or bytes to the function will result in TypeError raised by the regex engine unless the caller coerces to str first.

## `folium.utilities.escape_double_quotes` · *function*

## Summary:
Replace every double-quote character (") in the input text with an escaped sequence (backslash + double-quote), producing text safe to embed inside surrounding double-quoted string literals (for example, in generated JavaScript or HTML attributes).

## Description:
Known callers within the provided snippet:
    - No callers are present in the supplied file fragment. (This statement reflects only the provided source; callers may exist elsewhere in the repository.)

Typical usage context:
    - Before embedding Python strings into double-quoted string literals of another language (e.g., generating inline JavaScript, building HTML attributes, or composing JSON-like snippets by hand), to prevent internal double quotes from prematurely ending the surrounding literal.

Why this is a separate function:
    - Encapsulates the single responsibility of escaping double quotes so code that generates embedded text can call a single, well-named utility rather than repeating the replace expression inline.
    - Centralizes the behavior to make it easier to change escape rules later (for example, to also escape backslashes or other characters) and to document expected preconditions/postconditions in one place.

## Args:
    text (str): Input text in which each double-quote character (") should be escaped.
        - Expected type: str. The function calls text.replace('"', r'\"'), so the caller should normally supply a Python str.
        - Default: no default; this argument is required.
        - Interdependencies: None.
        - If a non-str is supplied, the function delegates to that object's replace method; see "Returns" and "Raises" for the implications.

## Returns:
    str: When called with a Python str, returns a new str where every " is replaced by the two-character sequence backslash + double-quote (\").
    Other behaviors:
        - If the provided object is not a str but implements a compatible replace(old, new) method that accepts two str arguments, the function returns whatever that replace method returns (which may be a different type).
        - If the provided object is a str that contains no double quotes, the returned value is equal in content to the input (Python may or may not reuse the same internal string object; callers should treat the return as a fresh str value).

## Raises:
    - AttributeError: If the provided text has no replace attribute (for example, text is None); condition: calling text.replace(...) raises AttributeError.
    - TypeError: If the provided object's replace method exists but rejects the given argument types (for example, passing str arguments to bytes.replace); condition: underlying replace implementation raises TypeError.
    - No custom exceptions are raised by this function; it only propagates exceptions thrown by the underlying replace call.

## Constraints:
Preconditions:
    - Prefer providing a str. The function assumes the replace method accepts old/new values as str.
Postconditions:
    - Every " present in the input (when replace executes successfully) is replaced with \".
    - No other characters are modified.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not call external services. It returns a value and leaves inputs unchanged (strings are immutable).

## Control Flow:
flowchart TD
    Start[Start] --> CallReplace["Call text.replace('\"', '\\\"')"]
    CallReplace --> Success{"replace succeeded?"}
    Success -- Yes --> Return[Return escaped result]
    Success -- No --> Propagate[Propagate exception (AttributeError/TypeError/etc.)]
    Propagate --> End[End]
    Return --> End

## Examples:
Note on string representations:
    - Python source code uses backslashes to write literal characters. To show the actual returned contents clearly, use repr() which reveals escape sequences, or print() to view the rendered string.

Example 1 — basic usage and visualizing the result
    original = 'He said, "Hello, world!"'
    escaped = escape_double_quotes(original)
    # repr(escaped) -> 'He said, \\"Hello, world!\\"'
    # print(escaped) -> He said, \"Hello, world!\"

Example 2 — embedding into an inline JavaScript snippet
    user_text = 'A "quote" and a \\ backslash'
    # Escape double quotes so the string can be placed inside double quotes in JS:
    js_snippet = f'var msg = "{escape_double_quotes(user_text)}";'
    # js_snippet (repr) -> 'var msg = "A \\"quote\\" and a \\ backslash";'
    # When sent into an HTML <script> block this prevents early termination of the JS string.

Example 3 — defensive calling
    raw = maybe_none()  # could return None or a non-str
    if not isinstance(raw, str):
        # Decide how to handle non-str inputs explicitly:
        raise ValueError("escape_double_quotes expects a str")
    safe = escape_double_quotes(raw)

## `folium.utilities.javascript_identifier_path_to_array_notation` · *function*

## Summary:
Convert a dot-separated identifier path into JavaScript array-access notation by wrapping each path segment in bracket-double-quoted form (e.g., 'a.b.c' -> '["a"]["b"]["c"]') with internal double quotes escaped.

## Description:
Known callers within the supplied code fragment:
    - No direct callers were found in the provided file fragment. (Callers may exist elsewhere in the repository; this documentation reflects only the supplied context.)

Typical usage context:
    - Used when generating inline JavaScript expressions or HTML/JS snippets that need to access nested properties dynamically where each property name must be represented as a double-quoted string inside bracket notation.
    - Converts a human- or program-supplied dotted path into a safe, quoted bracket-access sequence so it can be concatenated directly into generated JavaScript.

Why this logic is a separate function:
    - Encapsulates the specific transformation from dotted-path notation to bracket-array notation and centralizes escaping of double quotes in path segments (delegated to escape_double_quotes), avoiding repeated formatting logic at call sites.
    - Keeps concerns separated: callers assemble or validate the path, this function performs the formatting and escaping.

## Args:
    path (str): A dot-separated identifier path.
        - Expected type: str (e.g., "a.b.c"). Each segment is the substring between dots.
        - Allowed values: any string. Empty string and segments are allowed (see edge cases below).
        - Interdependencies: None within this function, but correctness assumes callers intend dot as the separator. If segments themselves must contain dots, callers must not use this dot-separated representation or must encode segments before calling.

## Returns:
    str: A string containing the input path transformed into JavaScript array-access notation where each path segment is represented as ["<escaped-segment>"] and concatenated in order.
    - Examples:
        * Input "foo.bar" -> '["foo"]["bar"]'
        * Input "" (empty string) -> '[""]' (because ''.split('.') -> [''])
        * Input "a." -> '["a"][""]' (trailing empty segment)
    - All double-quote characters contained in each segment are escaped using escape_double_quotes before insertion into the surrounding double-quoted strings.

## Raises:
    - AttributeError: If the provided path does not support split(".") (e.g., path is None), the call to path.split(".") will raise AttributeError and it will propagate.
    - TypeError: If the provided path is a bytes object or another type whose split method rejects a str separator (for example, bytes.split expects a bytes separator), the underlying split call will raise TypeError which will propagate.
    - Any exception raised by escape_double_quotes for a segment will propagate unchanged (for example, AttributeError or TypeError as documented by escape_double_quotes) when that segment's replace call fails.
    - No exceptions are explicitly raised by this function itself; it only propagates errors from path.split and from escape_double_quotes.

## Constraints:
Preconditions:
    - The caller should provide a str (or an object whose split accepts a str separator and returns an iterable of segment-like values).
    - Each segment produced by split should be acceptable to escape_double_quotes (i.e., either a str or an object whose replace method accepts two str arguments).

Postconditions:
    - The returned value is a str (if the operations succeed) containing only bracketed, double-quoted segments joined together with no additional separators.
    - Every double quote occurring in any original segment has been escaped according to escape_double_quotes before being placed inside the double-quoted bracket notation.

## Side Effects:
    - None. This function performs no I/O, mutates no global state, and does not call external services. It builds and returns a new string.

## Control Flow:
flowchart TD
    Start[Start] --> Split["Call path.split('.')"]
    Split --> ForEach["For each segment x"]
    ForEach --> Escape["Call escape_double_quotes(x)"]
    Escape --> Format["Format as [\"<escaped>\"]"]
    Format --> Join["Concatenate formatted segments"]
    Join --> Return[Return resulting string]
    Split --> SplitError{"split raised exception?"}
    SplitError -- Yes --> PropagateSplitError[Propagate exception]
    Escape --> EscapeError{"escape_double_quotes raised exception?"}
    EscapeError -- Yes --> PropagateEscapeError[Propagate exception]
    PropagateSplitError --> End[End]
    PropagateEscapeError --> End
    Return --> End

## Examples:
1) Basic transformation
    path = "location.lat"
    # returns '["location"]["lat"]'
    # Typical: embed in JS: f"obj{javascript_identifier_path_to_array_notation(path)}"

2) Segments containing double quotes (escaped)
    path = 'user."name"'   # a single segment that includes a double-quote character would normally be represented differently;
                          # for this example we show the effect on a segment's internal quote if present
    # If path is a single segment containing a quote and no dots: path = 'a"b'
    # javascript_identifier_path_to_array_notation('a"b') -> '["a\"b"]'

3) Edge cases: empty and trailing segments
    javascript_identifier_path_to_array_notation("")   # returns '[""]'
    javascript_identifier_path_to_array_notation("a.") # returns '["a"][""]'

4) Defensive usage with error handling
    raw = get_candidate_path()
    if not isinstance(raw, str):
        # Provide a clearer error to the caller rather than letting an AttributeError/TypeError bubble up.
        raise ValueError("path must be a str")
    safe_js_path = javascript_identifier_path_to_array_notation(raw)

