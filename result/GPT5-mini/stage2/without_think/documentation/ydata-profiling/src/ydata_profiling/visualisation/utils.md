# `utils.py`

## `src.ydata_profiling.visualisation.utils.hex_to_rgb` · *function*

## Summary:
Convert a hexadecimal color string (optionally prefixed with '#') into a tuple of normalized channel values (floats in the range [0.0, 1.0]).

## Description:
This function:
- Removes an optional leading '#' from the input string.
- Splits the remaining hex string into equal-sized contiguous segments determined by integer division of the length by 3.
- Converts each segment from base-16 to an integer and normalizes it by dividing by 255, returning those values as a tuple of floats.

Known callers within the repository snapshot:
- No direct callers were found in the provided snapshot. Typical use is from visualization or plotting utilities that require matplotlib-style color channels (floats between 0 and 1).

Why this is a separate function:
- Parsing and normalizing hex color strings is a small, reusable responsibility used by multiple visualization utilities. Encapsulating it avoids duplication, centralizes parsing behavior, and makes testing and reuse straightforward.

## Args:
    hex (str):
        - A hexadecimal color representation as a Python str.
        - May include a leading '#' character (it will be removed).
        - Typical accepted forms:
            * 3-digit shorthand RGB (e.g., "f0a" or "#f0a") — this function treats each digit as a separate channel (no automatic doubling to "ff00aa").
            * 6-digit RGB (e.g., "ff00aa" or "#ff00aa") — treated as three 2-character channels.
        - Requirements:
            * After removing an optional leading '#', the string length (hlen) must be >= 3 for the function to proceed without raising a ValueError.
            * Characters must be valid hexadecimal digits (0-9, a-f, A-F).
        - If a non-str is passed, calling .lstrip("#") may raise AttributeError or TypeError depending on the object type.

## Returns:
    Tuple[float, ...]:
        - A tuple containing normalized channel values computed as int(segment, 16) / 255 for each extracted segment.
        - For common inputs:
            * If the hex (without '#') has length 3 -> returns a 3-tuple (one float per single hex digit).
            * If the hex length is 6 -> returns a 3-tuple (one float per two hex digits).
        - For other lengths, the number of returned elements equals len(range(0, hlen, step)) where step = hlen // 3 (integer division). Examples:
            * hlen = 4 -> step = 1 -> 4 returned values (each from one hex digit).
            * hlen = 5 -> step = 1 -> 5 returned values.
            * hlen = 7 -> step = 2 -> range(0,7,2) yields indices 0,2,4,6 -> 4 returned values.
        - Each returned float is within [0.0, 1.0] when conversion succeeds.

## Raises:
    ValueError:
        - If the computed step equals 0 (this happens when the input, after stripping '#', has length less than 3). In that case, range(0, hlen, step) is invoked with step=0 and Python raises ValueError (range() arg 3 must not be zero).
        - If any extracted substring is not valid hexadecimal, int(segment, 16) raises ValueError.
    TypeError or AttributeError:
        - If the provided argument is not a str-like object, calling .lstrip("#") may raise AttributeError (no lstrip attribute) or TypeError (wrong argument type for an existing lstrip). The precise error depends on the concrete type passed.

## Constraints:
    Preconditions:
        - Caller must pass a string-like object. Preferably, pass a str containing only hex digits and length >= 3 (after optional '#').
    Postconditions:
        - If the function returns normally, it yields a tuple of one or more floats, each in [0.0, 1.0].
        - The number of floats equals the number of slices produced using step = hlen // 3 and iterating i in range(0, hlen, step).

## Side Effects:
    - None. The function is pure: it performs string and numeric operations only and does not perform I/O or modify external state.

## Control Flow:
flowchart TD
    Start([Start]) --> Strip[/"Strip leading '#' from input"/]
    Strip --> ComputeLen[/"hlen = len(hex_without_hash)"/]
    ComputeLen --> ComputeStep[/"step = hlen // 3 (integer division)"/]
    ComputeStep --> CheckStep{step == 0?}
    CheckStep -- Yes --> RaiseRangeError["range(..., step) invoked with step=0\nPython raises ValueError"]
    CheckStep -- No --> Iterate[/"For i in range(0, hlen, step):\n  segment = hex[i:i+step]\n  value = int(segment,16)/255"/]
    Iterate --> IntError{"int(segment,16) may raise\nValueError for invalid hex"}
    IntError -- Error --> RaiseIntError["Raise ValueError (invalid hex substring)"]
    IntError -- OK --> ReturnTuple["Return tuple of floats"]
    ReturnTuple --> End([End])

## Examples:
- Standard 6-digit hex:
    Input: "#ff0000"
    Result: (1.0, 0.0, 0.0)

- Standard 3-digit shorthand (note: no doubling of digits):
    Input: "f0a"
    Segments: "f","0","a" -> ints (15,0,10) -> normalized
    Result: (15/255 ≈ 0.0588, 0.0, 10/255 ≈ 0.0392)

- Typical 6-digit without '#':
    Input: "80ff00"
    Segments: "80","ff","00" -> ints (128,255,0) -> normalized
    Result: (128/255 ≈ 0.5020, 1.0, 0.0)

- Non-standard length (demonstrates slicing logic):
    Input: "abcd"  (hlen = 4, step = 4 // 3 = 1)
    Slices: "a","b","c","d" -> 4 elements returned: (10/255, 11/255, 12/255, 13/255)

- Error handling example (illustrative, not code):
    - If input is "", then hlen = 0, step = 0 -> ValueError from range(...) (step is zero).
    - If input is "ggg", int("g", 16) raises ValueError indicating invalid hexadecimal digits.
    - If input is None, attempting .lstrip("#") will raise AttributeError.

Notes for implementers:
- This function intentionally does not implement common shorthand expansion (for instance, treating "f0a" as "ff00aa"). If the caller requires that behavior, perform preprocessing to expand single-character segments to two characters each before calling this function.
- The conversion accepts uppercase and lowercase hex digits since int(..., 16) handles both.

## `src.ydata_profiling.visualisation.utils.base64_image` · *function*

## Summary:
Encode raw image bytes into a data URI string ("data:<mime_type>;base64,<...>") that can be embedded directly in HTML or CSS.

## Description:
This utility performs the small, well-scoped task of converting binary image content into a percent-encoded base64 data URI using the supplied MIME type. It is intended for visualization and HTML-generation code that needs an inline image source (for example, embedding a matplotlib-rendered PNG into an HTML report).

Known callers within the codebase:
- Visualization and report generation modules that assemble HTML with inline images. (No single-file callsites are enumerated here; typical usage is during the final HTML assembly stage.)

Why this logic is extracted:
- Centralizes the sequence: base64 encoding -> percent-encoding -> data URI formatting. This prevents duplication across visualization modules and allows changing quoting/encoding behavior in a single place if needed.

## Args:
    image (bytes):
        Required. Raw image payload as a bytes-like object (bytes or bytearray).
        - Must be bytes-like because the function passes it to base64.b64encode which expects bytes.
    mime_type (str):
        Required. The MIME type to include in the data URI (e.g., "image/png", "image/svg+xml").
        - The value is inserted verbatim; the function does not validate that the MIME type matches the image bytes.

Interdependencies:
- The function does not inspect or validate that the image content matches mime_type.
- Internally: base64.b64encode(image) -> bytes; urllib.parse.quote(...) is then applied to that result. In common CPython implementations quote will accept bytes and return a str; callers targeting maximum portability may prefer decoding the base64 bytes to ASCII before calling quote (example provided below).

## Returns:
    str:
        A data URI string in the form "data:<mime_type>;base64,<percent-encoded-base64-data>".
        - Example pattern: "data:image/png;base64,iVBORw0KGgo%3D%3D..."
        - For empty input (b''), the function returns "data:<mime_type>;base64," (the base64 payload component will be empty).
        - The returned string is intended to be used directly in HTML <img src="..."> or CSS url(...).

## Raises:
    TypeError:
        - If image is not bytes-like, base64.b64encode(image) will raise TypeError.
    Other exceptions:
        - If an unexpected error occurs in the underlying standard library calls (base64.b64encode or urllib.parse.quote), those exceptions propagate unchanged; the function itself does not catch exceptions.
Note:
    - The function does not raise a TypeError simply because mime_type is not a str; mime_type is formatted into the f-string and will be converted to str via normal formatting rules. The principal TypeError risk is from base64.b64encode when given non-bytes input (and rarely from quote on unusual Python implementations).

## Constraints:
Preconditions:
    - image must be bytes-like.
    - mime_type should be a textual MIME type (str) for semantic correctness, though not strictly validated.

Postconditions:
    - On successful return, the caller gets a str data URI containing the provided MIME type and the percent-encoded base64 payload.
    - No external state is modified by this function.

## Side Effects:
    - None. The function performs in-memory transformations only and does not perform I/O, network, or global state changes.

## Control Flow:
flowchart TD
    A[Start: receive image (bytes) and mime_type (str)] --> B[base64.b64encode(image) -> base64_data (bytes)]
    B --> C[quote(base64_data) -> image_data (str in common CPython)]
    C --> D[Return "data:{mime_type};base64,{image_data}" (str)]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style D fill:#9f9,stroke:#333,stroke-width:1px

(Linear flow: encode -> quote -> format. Error paths: base64.b64encode or quote may raise and the function will propagate the exception.)

## Examples:
Example 1 — typical successful usage:
    1. Read binary image data:
       image_bytes = open("plot.png", "rb").read()
    2. Obtain data URI:
       data_uri = base64_image(image_bytes, "image/png")
    3. Embed in HTML:
       <img src="{data_uri}" alt="plot"/>

Example 2 — robust fallback to ensure portability across Python implementations:
    - Because base64.b64encode returns bytes, some callers prefer to explicitly decode those bytes to ASCII before quoting to avoid any subtle differences between Python implementations:
      base64_data = base64.b64encode(image_bytes)        # bytes
      base64_text = base64_data.decode("ascii")          # str (ASCII only)
      safe_payload = quote(base64_text)                  # str, safe to embed
      data_uri = f"data:{mime_type};base64,{safe_payload}"
    - Use this pattern if you need to be explicit about types or want to avoid relying on quote accepting bytes.

Example 3 — error handling:
    - If there's a possibility image is not bytes, validate or catch errors:
      try:
          data_uri = base64_image(maybe_bytes, "image/png")
      except TypeError as exc:
          # handle or re-raise with contextual message
          raise ValueError("image must be bytes-like") from exc

## `src.ydata_profiling.visualisation.utils.plot_360_n0sc0pe` · *function*

## Summary:
Render the current Matplotlib figure to an image and return either inline content (SVG text or a PNG data-URI) or a relative assets suffix pointing to a written file.

## Description:
This helper performs the final step of converting the active Matplotlib figure into an embeddable representation for HTML reports. Depending on configuration it will either produce inline content suitable for immediate embedding or save an image file under the configured assets directory and return the relative suffix for referencing in HTML.

Known callers within the codebase:
- No explicit callsites were provided in the available snapshot. Typical callers are visualization/report-generation code that has drawn a Matplotlib figure and needs the produced image for embedding or saving in the generated report.

Why this logic is extracted:
- It centralizes decision-making and side effects around output format selection, inline vs. file-backed output, base64 encoding for inline PNGs, DPI handling for PNGs, and deterministic asset suffix construction. This prevents duplicating plt.savefig/encoding/asset-path logic in many plot-generating places.

## Args:
    config (Settings):
        Required. An object providing configuration attributes accessed by this function:
            - config.plot.image_format.value (str): default format name used when image_format is None.
            - config.plot.dpi (int): DPI passed to savefig for PNG output.
            - config.html.inline (bool): if True produce inline content; if False save a file under assets_path.
            - config.html.assets_path (str | Path | None): base filesystem directory for non-inline output; must be non-None when config.html.inline is False.
            - config.html.assets_prefix (str): prefix used in the returned suffix when writing to assets.

    image_format (Optional[str], default=None):
        Optional override for the output format. If None, the function uses config.plot.image_format.value.
        Allowed values (case-sensitive): "png", "svg". Any other value causes a ValueError.

    bbox_extra_artists (Optional[List[matplotlib.artist.Artist]], default=None):
        Passed directly to matplotlib.pyplot.savefig as bbox_extra_artists.

    bbox_inches (Optional[str], default=None):
        Passed directly to matplotlib.pyplot.savefig as bbox_inches (commonly "tight" or None).

Interdependencies:
    - If image_format is None, config.plot.image_format.value is used and must be one of the supported values.
    - If config.html.inline is False, config.html.assets_path must not be None.

## Returns:
    str:
        One of:
            - Inline SVG: the SVG markup string when config.html.inline is True and format == "svg". (Produced by calling StringIO.getvalue().)
            - Inline PNG: a data URI string produced by the helper base64_image, of the form "data:image/png;base64,<percent-encoded-base64-data>", when config.html.inline is True and format == "png".
            - Asset suffix: when config.html.inline is False, returns the suffix string constructed exactly as:
                "{config.html.assets_prefix}/images/{uuid.uuid4().hex}.{image_format}"
              (a str). The file is written to Path(config.html.assets_path) / suffix.

Edge-case returns:
    - If matplotlib produces an empty payload, inline branches return the corresponding empty string or data URI with empty payload (dependent on matplotlib and base64_image behavior).
    - The function always returns a str on successful completion.

## Raises:
    ValueError:
        - If the resolved image_format is not "png" or "svg":
            Message: 'Can only 360 n0sc0pe "png" or "svg" format.'
        - If config.html.inline is False and config.html.assets_path is None:
            Message: "config.html.assets_path may not be none"

    Propagated exceptions:
        - Exceptions raised by matplotlib.pyplot.savefig or matplotlib.pyplot.close (I/O errors, backend errors) propagate unchanged.
        - Exceptions from base64_image (e.g., TypeError if given non-bytes) propagate; in this implementation it is called with bytes from BytesIO.getvalue().

## Constraints:
Preconditions:
    - The caller has drawn the Matplotlib figure/axes to be saved (they are the active figure when plt.savefig is called).
    - config provides the required attributes listed above.
    - A working Matplotlib backend is available for the requested format.

Postconditions:
    - matplotlib.pyplot.close() is invoked; the figure is closed before returning.
    - If non-inline output is chosen and save succeeds, a file exists at Path(config.html.assets_path) / suffix (constructed as above).
    - The function returns a string representing the inline content or the asset suffix.

## Side Effects:
    - Calls matplotlib.pyplot.savefig(...) and matplotlib.pyplot.close() (referred to as plt in the surrounding module).
    - For inline SVG: writes to an in-memory StringIO only.
    - For inline PNG: writes to an in-memory BytesIO and calls base64_image to produce a data URI (no filesystem I/O).
    - For non-inline output: writes an image file to disk at Path(config.html.assets_path) / suffix (filesystem I/O). The function does not create directories explicitly; save behavior depends on matplotlib and the filesystem.
    - No network I/O or global state changes beyond Matplotlib figure state.

## Control Flow:
flowchart TD
    Start[Start: call with config, image_format?] --> ResolveFormat{image_format is None?}
    ResolveFormat -- Yes --> UseConfigFormat[format = config.plot.image_format.value]
    ResolveFormat -- No --> UseArgFormat[format = image_format]
    UseConfigFormat --> ValidateFormat[Check format in {"png","svg"}]
    UseArgFormat --> ValidateFormat
    ValidateFormat -- invalid --> ErrFormat[Raise ValueError: unsupported format]
    ValidateFormat -- valid --> InlineCheck{config.html.inline is True?}
    InlineCheck -- True --> InlineBranch
    InlineCheck -- False --> FileBranch
    InlineBranch --> IsSVG{format == "svg"?}
    IsSVG -- True --> SaveToStringSVG[plt.savefig(to StringIO with format="svg", bbox_*), plt.close(), result = image_str.getvalue()]
    IsSVG -- False --> SaveToBytesPNG[plt.savefig(to BytesIO, dpi=config.plot.dpi, format="png", bbox_*), plt.close(), result = base64_image(bytes, "image/png")]
    FileBranch --> CheckAssets{config.html.assets_path is None?}
    CheckAssets -- True --> ErrAssets[Raise ValueError: config.html.assets_path may not be none]
    CheckAssets -- False --> ComposePath[Build suffix = f"{config.html.assets_prefix}/images/{uuid.uuid4().hex}.{format}", args={"fname": Path(config.html.assets_path)/suffix,"format":format,("dpi":config.plot.dpi if format=="png" else omitted)}]
    ComposePath --> SaveToFile[plt.savefig(**args), plt.close(), result = suffix]
    SaveToStringSVG --> End[Return result]
    SaveToBytesPNG --> End
    SaveToFile --> End

## Examples:
Example 1 — Inline SVG
    # Preconditions: a Matplotlib figure has been drawn.
    # config.html.inline == True and config.plot.image_format.value == "svg"
    svg_text = plot_360_n0sc0pe(config)
    # svg_text contains raw SVG markup suitable for embedding directly into HTML.

Example 2 — Inline PNG (data URI)
    # Preconditions: a Matplotlib figure has been drawn.
    # config.html.inline == True and config.plot.image_format.value == "png"
    data_uri = plot_360_n0sc0pe(config)
    # data_uri is a string like "data:image/png;base64,...", usable as <img src="...">

Example 3 — Save to assets directory
    # Preconditions: a Matplotlib figure has been drawn.
    # config.html.inline == False
    # config.html.assets_path points to an existing output directory
    # config.html.assets_prefix == "assets"
    suffix = plot_360_n0sc0pe(config, image_format="png")
    # suffix is "assets/images/<uuid>.png"
    # File is written to Path(config.html.assets_path) / suffix

Example 4 — Handling unsupported format
    try:
        plot_360_n0sc0pe(config, image_format="pdf")
    except ValueError as exc:
        # exc.args[0] == 'Can only 360 n0sc0pe "png" or "svg" format.'
        handle_error()

