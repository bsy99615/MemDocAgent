# `utils.py`

## `src.ydata_profiling.visualisation.utils.hex_to_rgb` · *function*

## Summary:
Converts a hexadecimal color string to an RGB tuple with normalized values between 0 and 1.

## Description:
Transforms a hexadecimal color representation (like "#FF0000" for red) into a tuple of floating-point values representing the red, green, and blue components normalized to the range [0, 1]. This normalization is required by many visualization libraries such as matplotlib. The function accepts both 3-character (e.g., "F00") and 6-character (e.g., "FF0000") hexadecimal color codes.

## Args:
    hex (str): A hexadecimal color string, optionally prefixed with "#". Valid formats include "#FF0000", "FF0000", "#00FF00", "00FF00", "#F00", "F00", etc. The hex string must contain only valid hexadecimal characters (0-9, A-F, a-f).

## Returns:
    Tuple[float, float, float]: A tuple containing exactly 3 normalized RGB values as floats in the range [0.0, 1.0]. The first value is red, second is green, third is blue.

## Raises:
    ValueError: When the hex string contains invalid hexadecimal characters or has an invalid length (not 3 or 6 characters after stripping "#").

## Constraints:
    Preconditions:
        - Input must be a valid string
        - String length must be either 3 or 6 characters after removing "#" prefix  
        - All characters must be valid hexadecimal digits (0-9, A-F, a-f)
    
    Postconditions:
        - Output tuple always contains exactly 3 elements (R, G, B)
        - Each element is a float in the range [0.0, 1.0]

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input hex string] --> B[Strip # prefix if present]
    B --> C[Validate hex length (3 or 6)]
    C --> D{Valid length?}
    D -->|No| E[Raise ValueError]
    D -->|Yes| F[Split into 3 equal parts]
    F --> G[Convert each part to int base 16]
    G --> H[Divide by 255 for normalization]
    H --> I[Return (r, g, b) tuple]
```

## Examples:
    >>> hex_to_rgb("#FF0000")
    (1.0, 0.0, 0.0)
    
    >>> hex_to_rgb("00FF00")
    (0.0, 1.0, 0.0)
    
    >>> hex_to_rgb("#0000FF")
    (0.0, 0.0, 1.0)
    
    >>> hex_to_rgb("F00")
    (1.0, 0.0, 0.0)
    
    >>> hex_to_rgb("0F0")
    (0.0, 1.0, 0.0)
```

## `src.ydata_profiling.visualisation.utils.base64_image` · *function*

## Summary:
Converts binary image data into a base64-encoded data URI string for web embedding.

## Description:
Transforms raw binary image data into a data URI format that can be directly embedded in HTML documents or web applications. This utility function is commonly used to generate inline image representations that don't require separate HTTP requests.

## Args:
    image (bytes): Binary image data to be encoded
    mime_type (str): MIME type identifier (e.g., 'image/png', 'image/jpeg')

## Returns:
    str: A data URI string in the format "data:mime_type;base64,encoded_data"

## Raises:
    TypeError: If image parameter is not bytes-like object, as base64.b64encode requires bytes input

## Constraints:
    Preconditions:
        - image parameter must be bytes-like object
        - mime_type parameter must be a valid MIME type string
    Postconditions:
        - Returns a properly formatted data URI string
        - The returned string can be used directly in HTML img src attributes

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[base64_image function] --> B[image bytes input]
    B --> C{base64.b64encode(image)}
    C --> D[base64_data result]
    D --> E{quote(base64_data)}
    E --> F[image_data result]
    F --> G[Return data URI string]
```

## Examples:
    # Basic usage
    image_bytes = b'\x89PNG\r\n\x1a\n...'
    mime_type = 'image/png'
    data_uri = base64_image(image_bytes, mime_type)
    # Returns: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

## `src.ydata_profiling.visualisation.utils.plot_360_n0sc0pe` · *function*

## Summary:
Generates and returns image data for HTML report visualization, supporting both inline embedding and file-based storage modes.

## Description:
Creates image output from matplotlib figures according to configuration settings. This function abstracts the complexity of handling different image formats (PNG/SVG) and output modes (inline HTML embedding vs file assets). It's used internally by the profiling report generation system to produce visualizations that can be embedded directly in HTML reports or saved as separate asset files.

## Args:
    config (Settings): Configuration object containing plotting and HTML settings
    image_format (Optional[str]): Image format to generate ('png' or 'svg'). Defaults to config.plot.image_format.value
    bbox_extra_artists (Optional[List[Artist]]): Additional artists to include in bounding box calculation
    bbox_inches (Optional[str]): Bounding box inches specification for figure layout

## Returns:
    str: For inline mode, returns base64-encoded data URI string for direct HTML embedding. For file mode, returns relative file path string for asset reference.

## Raises:
    ValueError: When image_format is not 'png' or 'svg', or when config.html.assets_path is None in non-inline mode

## Constraints:
    Preconditions:
        - config parameter must be a valid Settings object
        - image_format must be 'png' or 'svg' if explicitly provided
        - config.html.assets_path must not be None when not using inline mode
    Postconditions:
        - matplotlib figure is closed after saving to prevent memory leaks
        - Proper image data is returned based on configuration mode

## Side Effects:
    - Creates temporary file objects (BytesIO/StringIO) in memory
    - May write files to disk when not using inline mode (if config.html.assets_path is set)
    - Calls matplotlib's savefig function which may perform I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[plot_360_n0sc0pe] --> B{image_format None?}
    B -->|Yes| C[Use config.plot.image_format.value]
    B -->|No| D[Use provided image_format]
    C --> E{image_format valid?}
    D --> E
    E -->|No| F[ValueError]
    E -->|Yes| G{config.html.inline?}
    G -->|Yes| H{image_format == svg?}
    H -->|Yes| I[StringIO savefig]
    H -->|No| J[BytesIO savefig with DPI]
    I --> K[plt.close()]
    J --> K
    K --> L[base64_image for PNG, getvalue for SVG]
    G -->|No| M{config.html.assets_path None?}
    M -->|Yes| N[ValueError]
    M -->|No| O[Create file path with UUID]
    O --> P[savefig to file path]
    P --> Q[plt.close()]
    Q --> R[Return file path suffix]
```

## Examples:
    # Inline mode usage
    config = Settings()
    config.html.inline = True
    image_data = plot_360_n0sc0pe(config, image_format="png")
    # Returns base64-encoded string for direct HTML embedding
    
    # File mode usage  
    config = Settings()
    config.html.inline = False
    config.html.assets_path = "/path/to/assets"
    image_path = plot_360_n0sc0pe(config, image_format="svg")
    # Returns relative file path string for asset reference
```

