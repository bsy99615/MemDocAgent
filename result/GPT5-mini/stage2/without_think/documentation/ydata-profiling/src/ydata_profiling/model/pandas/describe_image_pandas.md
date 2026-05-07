# `describe_image_pandas.py`

## `src.ydata_profiling.model.pandas.describe_image_pandas.open_image` · *function*

## Summary:
Open a filesystem path with Pillow and return a PIL Image on success; return None when opening fails due to OSError or AttributeError.

## Description:
Known callers within the provided context:
    - No direct callers were discovered in the provided snapshot. This function is intended as a small, reusable utility for higher-level image-processing or image-summary code that needs a safe way to attempt loading an image from disk.

Typical usage context and trigger:
    - Used when the pipeline needs to load an image file (for hashing, metadata extraction, summarization, etc.) but wants to treat unreadable or invalid images as "missing" rather than raising exceptions.

Why this logic is extracted:
    - Consolidates try/except behavior around PIL.Image.open so callers do not duplicate identical error handling.
    - Provides a clear contract: errors of type OSError or AttributeError are normalized to a None result, simplifying upstream handling and allowing callers to skip invalid images without exception handling logic.

## Args:
    path (pathlib.Path): A pathlib.Path pointing to the candidate image file. The function signature requires a Path object; while PIL.Image.open also accepts path-like strings or file-like objects, passing non-Path values to this wrapper is not the intended usage and may cause exceptions to propagate.

## Returns:
    Optional[PIL.Image.Image]:
        - A PIL Image instance when Image.open(path) succeeds.
        - None when Image.open(path) raises OSError or AttributeError.
    Edge cases:
        - If the file does not exist, is unreadable, or is not recognized as an image, Image.open commonly raises an OSError (or a subclass); this function returns None in those cases.
        - If Image.open raises an exception type other than OSError or AttributeError (for example TypeError if an unsupported argument type is passed), that exception will propagate to the caller.

## Raises:
    - Any exception raised by PIL.Image.open that is not OSError or AttributeError will propagate unchanged. Example: TypeError may be raised and propagate if an inappropriate object is passed as path.
    - The function itself does not raise OSError or AttributeError because those are caught and cause the function to return None.

## Constraints:
    Preconditions:
        - The caller should pass a pathlib.Path instance that refers to a filesystem location accessible for reading.
        - The calling process must have sufficient file-system permissions to read the target file.

    Postconditions:
        - On return, the value is either a PIL.Image.Image (ready for use) or None (indicating open failed due to OSError/AttributeError).
        - If a PIL Image is returned, it may internally hold file resources; callers should call image.close() when deterministic resource release is required.

## Side Effects:
    - Performs filesystem I/O by invoking PIL.Image.open(path); this may open a file descriptor until the returned Image is closed.
    - Does not mutate global variables, perform network I/O, or write persistent state.

## Control Flow:
flowchart TD
    Start --> TryOpen[Call Image.open(path)]
    TryOpen -->|Success| ReturnImage[Return PIL Image]
    TryOpen -->|Raises OSError or AttributeError| CatchAndReturnNone[Return None]
    TryOpen -->|Raises other exception| Propagate[Exception propagates to caller]

## Examples (prose):
    Typical successful flow:
        1. Caller constructs a pathlib.Path pointing to a candidate image file.
        2. Caller calls this function with that Path.
        3. If a PIL Image is returned, the caller performs desired processing (e.g., read size, compute hash).
        4. When finished, the caller calls image.close() to release any underlying file resources.

    Typical failure/skip flow:
        1. Caller constructs a pathlib.Path for a file that is missing, unreadable, or not an image.
        2. Caller calls this function; it returns None.
        3. The caller treats None as "skip this item" and continues without raising.

    Error propagation:
        - If the caller passes an unsupported type instead of a pathlib.Path (contrary to the annotation), PIL.Image.open may raise (for example, TypeError). Such exceptions are not caught here and will propagate; callers that might pass non-Path values should handle exceptions themselves.

## `src.ydata_profiling.model.pandas.describe_image_pandas.is_image_truncated` · *function*

## Summary:
Attempt to fully load a PIL Image and return True if loading fails due to the image being truncated or otherwise unloadable; return False when the load succeeds.

## Description:
This helper encapsulates a single, focused check: it calls the image object's load() method and treats certain failures as indicating a truncated or unreadable image.

Known callers:
- No direct callers were present in the supplied code snapshot for this function.
- Typical callers (in the image-profiling pipeline) are higher-level image description or validation routines — for example, functions that compute image hashes, extract metadata, or generate summary statistics (e.g., image description / profiling stages such as describe_image_1d). These callers use this check before attempting operations that require the image to be fully decodable.

Why this is a separate function:
- Centralizes the try/except logic for detecting truncated/unloadable images so callers do not duplicate exception-handling logic.
- Conveys a clear responsibility boundary: determine whether an image can be safely used for downstream processing without performing the downstream work itself.

## Args:
    image (PIL.Image.Image):
        - A PIL Image instance (or any object exposing a compatible load() method).
        - None or objects lacking a load attribute will result in the function reporting the image as truncated (see behavior below).
        - There are no other parameters. No interdependencies.

## Returns:
    bool:
        - True: The image.load() call raised either OSError or AttributeError, which this function treats as the image being truncated/unloadable.
        - False: The image.load() call completed without raising OSError or AttributeError, indicating the image appears loadable.
        - Note: If image.load() raises an exception type other than OSError or AttributeError, that exception will not be caught by this function and will propagate to the caller.

## Raises:
    - This function does not raise any exceptions on its own for the two checked failure modes: OSError and AttributeError are caught and result in returning True.
    - Any other exception raised by image.load() (e.g., MemoryError or custom exceptions) is not caught here and will propagate to the caller.

## Constraints:
Preconditions:
    - The caller should pass an object representing an image (ideally a PIL Image instance) that provides a load() method.
    - If the caller passes None or a non-image without load(), an AttributeError will be raised by the call to image.load(), but this function catches AttributeError and will return True (treating it as truncated).

Postconditions:
    - If the function returns False, image.load() has been invoked successfully; the image's internal pixel data is expected to be loaded into memory according to PIL semantics.
    - If the function returns True, the image is considered truncated/unloadable and callers should avoid further decoding operations that assume successful loading.

## Side Effects:
    - Calls image.load(), which may:
        - Trigger underlying I/O to read image data from a file or stream (depending on how the Image object was created).
        - Allocate memory for the decoded pixel data.
        - Modify internal state of the Image object (PIL typically caches or populates pixel data when load() is called).
    - No network calls, file writes, global state mutations, or external service interactions are performed by this function itself (any I/O is performed within PIL.Image.load()).

## Control Flow:
flowchart TD
    Start --> CallLoad[Call image.load()]
    CallLoad -->|No exception| ReturnFalse[/Return False (load succeeded)/]
    CallLoad -->|OSError or AttributeError raised| ReturnTrue[/Return True (truncated or unloadable)/]
    CallLoad -->|Other exception raised| Propagate[Propagate exception to caller]

## Examples:
Example — skip truncated images in a profiling step:
    from PIL import Image
    img = Image.open("some_image.jpg")
    if is_image_truncated(img):
        # Skip hashing, feature extraction, or other processing for this image
        handle_unloadable_image("some_image.jpg")
    else:
        # Safe to perform downstream operations that require fully decoded image
        process_image(img)

Example — handle errors propagated from unexpected exceptions:
    try:
        img = Image.open("some_corrupt_file.jpg")
        if is_image_truncated(img):
            print("Image appears truncated or unreadable; skipping.")
        else:
            run_heavy_processing(img)
    except MemoryError:
        # image.load() may raise MemoryError in low-memory scenarios; handle separately
        fallback_for_memory_pressure()

## `src.ydata_profiling.model.pandas.describe_image_pandas.get_image_shape` · *function*

## Summary:
Safely retrieve the dimensions of a PIL image object, returning the (width, height) tuple when accessible or None if the size cannot be read.

## Description:
This helper extracts the size information from a PIL image-like object by returning its .size attribute. It is designed as a resilient accessor that avoids raising for common failures when reading image metadata.

Known callers within the available context:
    - No direct callers were discovered in the retrieval step for this documentation. Typically this function is used by higher-level image description routines within the image profiling pipeline to obtain image dimensions before computing derived summaries (for example, shape-aware summaries or size-dependent features).

Why this logic is extracted:
    - Accessing image.size can raise OSError or AttributeError for malformed/unsupported or non-image objects. Encapsulating the try/except here centralizes the error handling policy (return None on inaccessible size) and avoids duplicating the same defensive pattern wherever image dimensions are needed.

## Args:
    image (PIL.Image.Image): A PIL image object (or any object exposing a .size attribute).
        - Allowed values: a valid PIL image instance (opened via PIL.Image.open or constructed in memory), or any object that provides a .size attribute.
        - If `image` is None, missing the attribute, or accessing .size raises OSError/AttributeError, the function returns None.
        - No other arguments.

## Returns:
    Optional[Tuple[int, int]]:
        - On success: a tuple (width, height). These are typically integers for standard PIL Image instances.
        - On failure: None if image.size cannot be accessed because of an OSError or AttributeError.
        - No other return values are produced by this function.

## Raises:
    - This function does not propagate OSError or AttributeError raised during access to image.size; those exceptions are caught and result in returning None.
    - Any other exception types raised while evaluating image.size (i.e., exceptions not explicitly caught) will propagate to the caller.

## Constraints:
    Preconditions:
        - The caller should pass an object intended to represent an image (commonly a PIL.Image.Image). Passing unrelated objects may lead to AttributeError (handled) or other exceptions (may propagate).
    Postconditions:
        - If the function returns a tuple, it guarantees that accessing image.size succeeded and the returned value is identical to the object's .size attribute at call time.
        - If the function returns None, it guarantees that either an OSError or AttributeError occurred while trying to access image.size.

## Side Effects:
    - None. The function performs no I/O, does not modify the input image object, and does not alter external/global state.

## Control Flow:
flowchart TD
    A[Start: receive image] --> B[Attempt to access image.size]
    B -->|Success| C[Return image.size tuple (width, height)]
    B -->|OSError or AttributeError| D[Return None]
    C --> E[End]
    D --> E[End]

## Examples:
    - Valid PIL image:
        Context: A valid PIL Image opened from disk with dimensions 800x600.
        Outcome: The function returns the tuple (800, 600).
    - Non-image or incomplete object:
        Context: An object without a .size attribute or with a broken internal representation that raises AttributeError when .size is accessed.
        Outcome: The function returns None (AttributeError is caught).
    - Corrupted image leading to I/O error:
        Context: A PIL Image instance whose internal state causes an OSError when querying .size.
        Outcome: The function returns None (OSError is caught).
    - Unexpected exception:
        Context: Accessing .size triggers an unexpected exception type not in (OSError, AttributeError).
        Outcome: That exception is not caught by this function and will propagate to the caller; callers needing to be robust to these cases should wrap calls in their own try/except.

## `src.ydata_profiling.model.pandas.describe_image_pandas.hash_image` · *function*

## Summary:
Compute a perceptual hash for a given PIL Image and return its string representation, or return None if hashing fails due to common image-read errors.

## Description:
This utility computes a perceptual (phash) fingerprint of a PIL.Image.Image using the imagehash library and returns the result as a string produced by calling str() on the ImageHash object. The function centralizes error handling for common failure modes so callers receive a simple Optional[str] result instead of having to manage imagehash-related exceptions.

Known callers within the codebase:
    - A repository-wide scan did not reveal any direct callers of this exact symbol. It is intended for use by image summarization or profiling routines in the same module to generate a compact identifier for an image's visual content.

Why this logic is extracted:
    - Responsibility boundary: encapsulates the conversion of an Image object to a stable string hash and collapses common, recoverable failures (OSError, AttributeError) to a single None return value. This keeps higher-level pipelines simpler and avoids repeated try/except blocks.

## Args:
    image (PIL.Image.Image):
        A PIL Image instance to hash (for example, one returned by PIL.Image.open or created in-memory). The parameter name must be `image`. Passing None or a non-image object is not supported and may cause exceptions.

## Returns:
    Optional[str]:
        - On success: the string returned by calling str() on the imagehash.ImageHash value produced by imagehash.phash(image).
        - On failure when imagehash.phash raises OSError or AttributeError (for example, due to unreadable/corrupt image data or a missing attribute on the image object): returns None.
        - Other exceptions raised by imagehash.phash or other underlying libraries (e.g., TypeError, MemoryError) are not caught here and will propagate to the caller.

## Raises:
    - No OSError or AttributeError will be raised by this function because those two exception types are explicitly caught and translated to None.
    - Any other exception thrown by imagehash.phash or by operations on the provided object (for instance, TypeError if an unsupported object is supplied) will propagate unchanged.

## Constraints:
    Preconditions:
        - The caller must supply a valid PIL.Image.Image instance that is fully initialized and readable.
        - If the image wraps file-backed data, that file must be accessible and not corrupted.

    Postconditions:
        - The return value is either a non-empty string (the str() of the ImageHash) or None.
        - No files, network connections, or global state are modified by this function.

## Side Effects:
    - None observable: the function operates in-memory on the provided Image and returns a value. It does not perform file I/O, network I/O, or mutate global state.

## Control Flow:
flowchart TD
    A[Start: receive PIL Image] --> B[Call imagehash.phash(image)]
    B -->|succeeds| C[Convert ImageHash to string via str() and return string]
    B -->|raises OSError or AttributeError| D[Catch and return None]
    B -->|raises other exception| E[Let exception propagate to caller]

## Examples:
Typical usage (end-to-end):
    from PIL import Image
    # Open an image file (caller is responsible for file I/O)
    img = Image.open("photo.jpg")
    # Compute perceptual hash
    h = hash_image(img)
    if h is None:
        # Handle unreadable or otherwise un-hashable image
        print("Image could not be hashed; skipping hash-based comparisons.")
    else:
        # Use hash (store, compare, index)
        print("Perceptual hash:", h)

Error-handling guidance:
    - If callers need to distinguish specific failure reasons (e.g., file I/O vs unsupported image mode), perform validation or call imagehash.phash in a custom try/except that inspects the exception type and message. This helper intentionally converts the common OSError/AttributeError cases into None for simplicity.

## `src.ydata_profiling.model.pandas.describe_image_pandas.decode_byte_exif` · *function*

## Summary:
Convert an EXIF tag value that may be bytes into a Python string by returning string inputs unchanged and decoding bytes inputs using the default bytes.decode() behavior.

## Description:
This small utility normalizes EXIF metadata values to str. Many EXIF extraction pipelines yield values that can be either already-decoded Python str or raw bytes; this function centralizes the logic that normalizes either case to a str.

Known callers within the codebase:
    - No direct call sites were detected during analysis of the isolated function. It is intended to be used by image metadata handling code (for example, functions that iterate over an image object's EXIF tags and need a stable string representation).

Why this is a separate function:
    - It encapsulates a single responsibility (normalizing EXIF values to str) and avoids duplicating the type-check-and-decode pattern wherever EXIF metadata is processed. Extracting the logic improves readability and localizes decisions about decoding defaults and error behavior.

## Args:
    exif_val (Union[str, bytes]):
        - Allowed values: a Python str or a bytes-like object that implements a decode() method.
        - Semantics: If exif_val is already a str, it is returned as-is. Otherwise the function calls exif_val.decode() with no arguments (i.e., using the default encoding and error handling of the object's decode implementation).
        - Interdependencies: None; behavior depends only on the runtime type of exif_val.

## Returns:
    str:
        - If input was a str: the same string object is returned (no transformation performed).
        - If input was bytes (or another object with a decode method): the result of exif_val.decode() is returned — typically a UTF-8 decoded str when exif_val is bytes.
        - Edge-case returns: there are no alternate sentinel return values; failures raise exceptions described below.

## Raises:
    AttributeError:
        - Trigger: exif_val is not a str and does not provide a decode() method (for example, None or an int). The code attempts to call exif_val.decode(), which raises AttributeError.
    UnicodeDecodeError:
        - Trigger: exif_val is a bytes instance (or other decodable object) but decoding with the default parameters fails because the byte sequence is not valid under the default encoding (typically UTF-8). The underlying bytes.decode() raises UnicodeDecodeError.
    Any other exception:
        - The function does not catch exceptions from exif_val.decode(); other exceptions raised by a custom decode implementation will propagate.

## Constraints:
Preconditions:
    - Caller should pass an object that is either a str or a bytes-like object (or another object implementing decode()).
    - If a bytes input is expected to decode successfully, it should be encoded in the default encoding used by the environment (commonly UTF-8) or provide a decode implementation that handles the bytes.

Postconditions:
    - On successful return, the result is always a Python str.
    - The function performs no mutation of the input object.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not call external services. It only queries the type and potentially invokes the in-memory decode() method of the input.

## Control Flow:
flowchart TD
    A[Start: exif_val]
    A --> B{isinstance(exif_val, str)?}
    B -- yes --> C[Return exif_val (str, unchanged)]
    B -- no --> D[Call exif_val.decode() with default params]
    D --> E[Return decoded string or propagate exception]

## Examples:
- Successful cases:
    - Input: a Python str value such as "CameraModel" -> Output: "CameraModel" (returned unchanged).
    - Input: bytes value b"CameraModel" -> Output: "CameraModel" (decoded using default bytes.decode()).

- Error case (must be handled by caller):
    - Input: bytes with invalid UTF-8 sequence (for example a sequence that cannot be decoded with the environment default) -> Behavior: bytes.decode() raises UnicodeDecodeError which propagates to the caller.
    - Input: None or integer -> Behavior: calling decode() on these objects raises AttributeError which propagates to the caller.

- Usage guidance:
    - If callers expect potentially non-UTF-8 encodings, they should pre-decode bytes with the appropriate encoding before calling this function, or wrap calls in a try/except to catch UnicodeDecodeError and handle fallback decoding strategies.

## `src.ydata_profiling.model.pandas.describe_image_pandas.extract_exif` · *function*

## Summary:
Extracts EXIF metadata from a PIL Image object and returns a mapping of human-readable EXIF tag names to normalized values.

## Description:
This function queries the provided PIL Image for EXIF metadata using the image._getexif() API. If EXIF data is present it converts EXIF tag numeric keys to their human-readable names (using PIL.ExifTags.TAGS) and normalizes each tag value via the module's decode_byte_exif helper so that byte-valued tags become Python strings when possible.

Known callers within the codebase:
    - No direct static call sites were detected during isolated analysis of the repository. Typical call sites are image-processing / summarization routines in the image description pipeline (for example, higher-level functions in the same describe_image_pandas module or other image summarizers) which request EXIF metadata as part of an image profiling step. These callers invoke this function when they need a stable, human-readable dictionary of EXIF metadata to include in an image summary record.

Why this logic is a separate function:
    - Responsibility separation: it isolates all EXIF retrieval and normalization concerns (presence/absence of EXIF, mapping numeric EXIF keys to names, decoding byte values) behind a single, well-defined API. That keeps image summarization code focused on summary statistics and avoids duplicating EXIF-decoding logic scattered across the profiling pipeline.
    - Error handling centralization: the function centralizes the handling of common failure modes (missing _getexif, non-EXIF images) and returns a consistent empty-dict fallback.

## Args:
    image (PIL.Image.Image):
        - A PIL Image instance (or any object exposing a compatible _getexif() method).
        - Allowed values: a valid PIL image object opened by PIL.Image.open(...) or an object implementing _getexif().
        - If image does not provide _getexif or _getexif raises AttributeError/OSError, the function will return an empty dict.

## Returns:
    dict:
        - A dictionary mapping EXIF tag names (str) to normalized values.
        - Keys: human-readable tag names taken from PIL.ExifTags.TAGS (for every numeric key k present in the image's EXIF mapping where k exists in ExifTags.TAGS).
        - Values: the result of decode_byte_exif(v) for each EXIF value v — typically a Python str for tag values that were originally bytes or already str. For tag values that are other types (e.g., integers, tuples) the decode_byte_exif helper may raise AttributeError (see Raises) — such errors are caught by this function and result in an empty dict fallback.
        - Edge-case returns:
            * If the image has no EXIF metadata (_getexif() returns None), returns {}.
            * If image._getexif() or subsequent processing raises AttributeError or OSError, returns {}.
            * If EXIF is present and processed successfully, returns a dict of tag-name -> normalized-value.

## Raises:
    UnicodeDecodeError:
        - Condition: decode_byte_exif(v) attempts to decode a bytes object and the bytes cannot be decoded with the default decoding parameters (the underlying bytes.decode() raises UnicodeDecodeError).
        - Behavior: This exception is NOT caught inside extract_exif and therefore will propagate to the caller.
    (Note: AttributeError and OSError raised while calling image._getexif() or during the comprehension are explicitly caught by this function and handled by returning an empty dict — they are not re-raised.)

## Constraints:
    Preconditions:
        - The caller should pass an object with a _getexif() method (a PIL Image is the canonical input).
        - When callers expect particular EXIF values, they should be aware that some EXIF tags may be non-string types (tuples, ints) and that decode_byte_exif is intended primarily to normalize bytes/str values.
    Postconditions:
        - On normal return, the function returns a dict whose keys are EXIF tag names (str). If any AttributeError or OSError occurs during EXIF access/processing, the function returns an empty dict.
        - If a UnicodeDecodeError occurs during value decoding it will propagate and the function will not return.

## Side Effects:
    - No I/O is performed (no file or network access).
    - No global state is mutated.
    - The function only inspects the provided Image object and calls its in-memory methods.

## Control Flow:
flowchart TD
    Start[Start: receive image]
    Start --> TryGet[Try image._getexif()]
    TryGet --> |raises AttributeError or OSError| ReturnEmpty1[Return {}]
    TryGet --> |returns None| ReturnEmpty2[Return {}]
    TryGet --> |returns mapping| Iterate[Iterate k,v over mapping.items()]
    Iterate --> Filter{is k in ExifTags.TAGS?}
    Filter -- no --> Skip[Skip pair]
    Filter -- yes --> Decode[Call decode_byte_exif(v)]
    Decode --> |raises AttributeError or OSError| ReturnEmpty3[Return {}]
    Decode --> |raises UnicodeDecodeError| Propagate[Propagate UnicodeDecodeError]
    Decode --> |succeeds| Add[Add ExifTags.TAGS[k] : decoded_value to exif dict]
    Add --> Iterate
    Iterate --> End[Return assembled exif dict]

## Examples:
- Typical (happy path):
    Open an image and obtain its EXIF mapping for inclusion in a summary.
    >>> img = Image.open("photo.jpg")
    >>> exif = extract_exif(img)
    >>> # exif is a dict like {"Make": "Canon", "Model": "EOS 80D", "DateTime": "2021:05:01 12:34:56"}

- No EXIF present:
    >>> img = Image.open("no_exif.png")
    >>> extract_exif(img)
    {}  # function returns empty dict when _getexif() is None

- Handling potential Unicode decode issues:
    Because decode_byte_exif uses the default decode mechanism for bytes, callers that may encounter non-UTF-8 byte sequences should handle UnicodeDecodeError:
    >>> try:
    ...     exif = extract_exif(img)
    ... except UnicodeDecodeError:
    ...     # Fallback strategy, e.g., try different encodings or skip problematic tags
    ...     exif = {}

## `src.ydata_profiling.model.pandas.describe_image_pandas.path_is_image` · *function*

## Summary:
Return True when the file at the given filesystem path appears to be a recognized image based on its header bytes; otherwise return False.

## Description:
This utility uses the standard library imghdr.what function to inspect the file header and determine whether the file is a known image format (for example 'jpeg', 'png', 'gif', etc.). It performs only a read-only header inspection and does not attempt to fully decode the image.

Known callers within the codebase:
    - No direct call-sites were present in the provided file context. Typical callers are image-processing or profiling routines that need to filter candidate file paths before opening them with PIL.Image.open, computing hashes, or extracting metadata.

Why this is a separate function:
    - Encapsulates the header-based image recognition logic in one place so higher-level code can ask a simple boolean question (is this an image?) without repeating imghdr usage.
    - Keeps the image-validation step consistent across the codebase and isolates behavior that may change (for example, adding additional checks) to a single location.

## Args:
    p (pathlib.Path): Path to the filesystem entry to inspect.
        - The implementation accepts any os.PathLike object; the codebase uses pathlib.Path in the signature for clarity.
        - If callers supply a string path, they may wrap it with Path(...) or rely on functions that accept os.PathLike.

## Returns:
    bool: 
        - True if imghdr.what(p) returns a non-None string (i.e., the header matches a known image type such as 'jpeg', 'png', 'gif', etc.).
        - False if imghdr.what(p) returns None (the header is not recognized as a supported image type).

    Notes:
        - A True return value indicates the header matched a known format but does not guarantee the file can be fully decoded without errors.
        - A False return value means header inspection did not identify a known image type; the file may still be an image with an uncommon header or be corrupted.

## Raises:
    FileNotFoundError:
        - Propagated if the path does not exist when imghdr.what attempts to open it.
    IsADirectoryError:
        - Propagated if the path points to a directory and an attempt is made to open it as a file.
    PermissionError (OSError subtype):
        - Propagated when the process lacks permission to read the file.
    OSError (other kinds):
        - Other low-level I/O errors when opening/reading the file may be propagated.

    Notes:
        - The function itself contains no try/except; these exceptions are raised by the underlying file-open/read operations used by imghdr.what and will bubble up to callers.
        - Type hints are advisory only; passing an incompatible type (neither a path-like object nor a file-like object) may lead to exceptions from the underlying APIs.

## Constraints:
Preconditions:
    - The calling code should pass an os.PathLike object (pathlib.Path or str) or otherwise ensure the object is usable by imghdr.what.
    - The file should be accessible for read operations (correct permissions, not locked).

Postconditions:
    - No filesystem modifications are made by this function.
    - The return value reflects only header-based recognition; it does not validate full image decodability.

## Side Effects:
    - No intentional side effects. The function performs a read-only header inspection via imghdr (may open the file briefly).
    - No network I/O, global state, or external service interaction.

## Control Flow:
flowchart TD
    Start --> Call_imghdr_what
    Call_imghdr_what -->|raises FileNotFoundError / PermissionError / IsADirectoryError / OSError| Propagate_Exception
    Call_imghdr_what -->|returns None| Return_False
    Call_imghdr_what -->|returns non-None string| Return_True
    Propagate_Exception --> End
    Return_False --> End
    Return_True --> End

## Examples:
    from pathlib import Path

    p = Path("dataset/img_001.jpg")
    try:
        if path_is_image(p):
            # safe to attempt heavier operations like PIL.Image.open or hashing
            img = Image.open(p)
            process_image(img)
        else:
            # skip or log: header did not match known image formats
            logger.warning("%s is not a recognized image", p)
    except FileNotFoundError:
        logger.error("File not found: %s", p)
    except PermissionError:
        logger.error("No read permission for file: %s", p)

## `src.ydata_profiling.model.pandas.describe_image_pandas.count_duplicate_hashes` · *function*

## Summary:
Return the count of duplicate image-hash occurrences in a collection of image description mappings (total repeated items beyond the first occurrence per unique hash).

## Description:
This function extracts the 'hash' field from each element in the provided collection of image description objects, counts occurrences of each distinct hash, and returns the number of repeated occurrences computed as (total items-with-hash) - (number of distinct hashes).

Known callers within the codebase:
    - No direct callers were identified in the available repository scan for this specific function. It is implemented alongside other image-description/summarization helpers and is intended to be called by image-summary aggregation or reporting code that needs to report or deduplicate images by perceptual/content hash.

Why this logic is extracted:
    - Counting duplicate hashes is a focused utility operation used by higher-level summarizers. Keeping it as a small, well-tested helper isolates the counting semantics (including Pandas behavior) from the rest of the summarization pipeline and makes unit-testing and reuse straightforward.

## Args:
    image_descriptions (dict):
        - Although the function signature declares dict, the implementation expects an iterable (e.g., list, tuple, other sequence) of mapping-like objects (for example, dicts) where each element may contain a 'hash' key.
        - Each element x will be considered if and only if the membership test "'hash' in x" is valid and True; then x['hash'] is read.
        - Valid element examples: {'hash': 'abc'}, {'hash': 12345}, {'hash': numpy.int64(1)}
        - Elements without a 'hash' key are silently ignored.
        - If image_descriptions is not iterable, a TypeError will be raised by the list-comprehension or pandas constructor.

## Returns:
    int:
        - The number of duplicate hash occurrences found among the provided image descriptions.
        - Computed precisely as:
            N_with_hash = number of elements where 'hash' in x is True
            K_distinct = number of distinct hash values among those elements (pandas.value_counts drops NaN by default)
            return_value = N_with_hash - K_distinct
        - Typical return values:
            * 0 when there are no hash-bearing items or every hash is unique.
            * Positive integer when at least one hash appears multiple times.
        - Return value implementation note:
            * The expression uses pandas.Series.value_counts().sum() and len(counts); these operations commonly produce numpy integer scalars (e.g., numpy.int64). The function is annotated to return int; callers that require a built-in int can safely wrap the result with int(...).
        - Edge cases:
            * If no elements contain 'hash', returns 0.
            * Hash values that are pandas-NaN (numpy.nan) are excluded from value_counts() by default and therefore do not contribute to the counts.

## Raises:
    - TypeError:
        * If image_descriptions is not iterable, or if an element does not support the membership test "'hash' in x", a TypeError from the list comprehension or that membership test may propagate.
    - NameError:
        * The function references pd.Series. If the pandas module is not available under the name pd in the execution context (for example, if pandas was imported as pandas without aliasing to pd), a NameError will be raised. Ensure pandas is imported as "import pandas as pd" or that pd is defined in the module global scope.
    - Any exceptions raised by pandas.Series(...) or pandas.Series.value_counts() (for example, due to dtype issues) will propagate; the function does not catch them.

## Constraints:
    Preconditions:
        - The caller must pass an iterable of mapping-like objects where membership test "'hash' in x" is valid for elements to be considered.
        - pandas must be available under the pd name used in the function.
    Postconditions:
        - The function returns a non-negative integer (or a numpy integer scalar convertible to int) representing duplicate occurrences.
        - No input data is mutated by this function.

## Side Effects:
    - None. The function performs in-memory computation only; it does not perform I/O, modify external/global state, or call external services.

## Control Flow:
flowchart TD
    A[Start: receive image_descriptions] --> B{Is image_descriptions iterable?}
    B -- No --> E[TypeError or other exception propagates]
    B -- Yes --> C[Build list: [x['hash'] for x in image_descriptions if 'hash' in x]]
    C --> D[Create pandas Series from list]
    D --> F[Call value_counts() to get counts per distinct hash (NaN dropped)]
    F --> G[Compute total_occurrences = counts.sum()]
    G --> H[Compute distinct_hashes = len(counts)]
    H --> I[Return duplicates = total_occurrences - distinct_hashes]
    I --> J[End]

## Examples:
    - Typical usage:
        Given image_descriptions = [{'hash': 'a'}, {'hash': 'a'}, {'hash': 'b'}]
        counts -> {'a': 2, 'b': 1}; N_with_hash = 3, K_distinct = 2 -> returns 1

    - No hashes present:
        Given image_descriptions = [{'path': 'img1.jpg'}, {}, {'path': 'img2.jpg'}]
        returns 0

    - All identical hashes:
        Given image_descriptions = [{'hash': 'x'}, {'hash': 'x'}, {'hash': 'x'}]
        returns 2

    - Handling return type explicitly:
        result = count_duplicate_hashes(items)
        # result may be a numpy integer type in practice; convert to built-in int if needed:
        duplicates = int(result)

## `src.ydata_profiling.model.pandas.describe_image_pandas.extract_exif_series` · *function*

## Summary:
Aggregate a list of per-image EXIF mappings into overall counts: a dict of EXIF key occurrence counts and, for each EXIF key, a pandas Series counting observed values.

## Description:
Processes multiple per-image EXIF mappings (one mapping per image) and returns:
- "exif_keys": a plain Python dict mapping each EXIF key -> number of images in which that key appeared.
- For every EXIF key observed, an entry series[k] which is a pandas Series mapping each observed value -> integer count (how many images had that exact value for that key).

Typical caller context:
- Called by an image summarization stage after extracting EXIF metadata from many images, when the pipeline needs aggregated frequency summaries for reporting or further analysis.
- No explicit callers were present in the provided snapshot; it is intended to be invoked with a pre-collected list of EXIF dicts.

Responsibility boundary:
- This function only performs aggregation of keys and values across image-level EXIF dicts. It does not parse image files, interpret EXIF tag semantics, or format results for presentation.

## Args:
    image_exifs (list):
        - Type: list of mapping-like objects (typically dict).
        - Each element must support .keys() and .items().
        - Keys: EXIF tag identifiers (commonly strings or ints; must be hashable to appear in the resulting dict/Series indices).
        - Values: EXIF values (any type accepted by pd.Series; ideally hashable primitives for meaningful value_counts).
        - Allowed values: the list may be empty; individual mappings may omit keys (sparse metadata).
        - Interdependencies: none between list elements; the function does not mutate inputs.

## Returns:
    dict:
        - "exif_keys" -> dict[str, int]
            * Constructed by pd.Series(exif_keys, dtype=object).value_counts().to_dict().
            * Maps EXIF key -> number of times that key appeared across input mappings.
            * If image_exifs is empty, this will be an empty dict {}.
        - For each EXIF key k observed:
            * series[k] -> pandas.Series
            * Index: unique observed values for key k
            * Values: integer counts (result of pd.Series(v).value_counts())
            * The pandas Series is returned as-is (not converted to dict), preserving index dtype and labels.
            * If all observed values for a key are identical, the Series contains a single index entry with the total count.

    Example return shape:
    {
        "exif_keys": {"Model": 3, "ISO": 2},
        "Model": pd.Series({"Canon": 2, "Nikon": 1}),
        "ISO": pd.Series({100: 1, 200: 1})
    }

## Raises:
    - NameError:
        * Condition: if the module namespace does not contain the name pd (the function calls pd.Series). This will raise NameError before any pandas operations occur.
    - AttributeError or TypeError:
        * Condition: if an element in image_exifs lacks .keys() or .items(), attribute access/iteration will raise these exceptions.
    - Any pandas exception (e.g., TypeError, ValueError) raised by pd.Series(...) or .value_counts():
        * Condition: if pandas cannot construct a Series from collected values or cannot compute value_counts (for example, due to incompatible value types). These exceptions are propagated.

## Constraints:
    Preconditions:
        - The module must expose pd (typically pandas imported as pd); the implementation calls pd.Series explicitly.
        - image_exifs must be an iterable (list/tuple) of mapping-like objects.
    Postconditions:
        - The returned dict always contains the "exif_keys" key (possibly empty).
        - For every EXIF key present in any input mapping, the returned dict contains a pandas.Series with counts for that key.
        - The input list and its contained mapping objects are not modified by this function.

## Side Effects:
    - None. The function performs in-memory computations only. It does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start --> LoopImages["for each image_exif in image_exifs"]
    LoopImages --> ExtendKeys["exif_keys.extend(list(image_exif.keys()))"]
    LoopImages --> LoopKV["for each exif_key, exif_val in image_exif.items()"]
    LoopKV --> InitList["if exif_key not in exif_values: exif_values[exif_key] = []"]
    InitList --> AppendVal["exif_values[exif_key].append(exif_val)"]
    AppendVal --> LoopKV
    LoopKV --> LoopImages
    LoopImages --> AfterCollect
    AfterCollect --> BuildKeyCounts["series['exif_keys'] = pd.Series(exif_keys, dtype=object).value_counts().to_dict()"]
    BuildKeyCounts --> ForEachKey["for each k, v in exif_values.items()"]
    ForEachKey --> BuildValCounts["series[k] = pd.Series(v).value_counts()"]
    BuildValCounts --> ForEachKey
    ForEachKey --> Return["return series"]
    Return --> End

## Examples:
1) Basic example:
    import pandas as pd
    # image_exifs: list of per-image EXIF dicts
    image_exifs = [
        {"Model": "Canon EOS 80D", "ISO": 100},
        {"Model": "Nikon D750", "ISO": 200},
        {"Model": "Canon EOS 80D", "FNumber": 2.8}
    ]
    result = extract_exif_series(image_exifs)
    # result["exif_keys"] -> {"Model": 3, "ISO": 2, "FNumber": 1}
    # result["Model"] -> pd.Series({"Canon EOS 80D": 2, "Nikon D750": 1})
    # result["ISO"] -> pd.Series({100: 1, 200: 1})

2) Empty input:
    result = extract_exif_series([])
    # result == {"exif_keys": {}}

3) Defensive wrapper ensuring pd and input structure:
    import pandas as pd
    def safe_extract(image_exifs):
        if "pd" not in globals():
            raise NameError("pd (pandas) must be available in module namespace before calling extract_exif_series")
        if not isinstance(image_exifs, (list, tuple)):
            raise TypeError("image_exifs must be a list or tuple of mapping-like objects")
        for i, x in enumerate(image_exifs):
            if not hasattr(x, "items") or not hasattr(x, "keys"):
                raise TypeError(f"element at index {i} is not mapping-like")
        return extract_exif_series(image_exifs)

    try:
        summary = safe_extract(my_exif_list)
    except Exception as e:
        # handle malformed input or pandas aggregation errors
        raise

## `src.ydata_profiling.model.pandas.describe_image_pandas.extract_image_information` · *function*

## Summary:
Return a compact dictionary of metadata about an image file at the given filesystem path: whether it could be opened, whether it appears truncated, its pixel dimensions (when readable), and optional EXIF metadata and perceptual hash when requested.

## Description:
Known callers and usage context:
- Typical callers are higher-level image-profiling or summarization routines in the image-description pipeline (for example: functions that implement per-column image summarization such as describe_image_1d or other image-aggregation code). These callers invoke this function when constructing a one-row summary for a single image file or when scanning a dataset of image file paths.
- Trigger: called when the pipeline needs a small, consistent set of properties about a file at a Path (opened status, truncation check, size, optionally EXIF and a perceptual hash) while tolerating common image-read errors.

Why this logic is extracted:
- Centralizes the open / validation / optional-metadata extraction sequence behind a single, testable API so callers do not duplicate try/except and conditional logic.
- Encapsulates the dependency and ordering between steps: attempt to open -> check whether fully loadable -> only if loadable, extract size / exif / hash. This keeps higher-level code concise and robust to corrupt or unreadable files.

## Args:
    path (pathlib.Path):
        - Filesystem path to the candidate image file. The function expects a Path object; passing other types may lead to exceptions from lower-level routines.
    exif (bool, optional, default False):
        - If True and the image is successfully opened and not truncated, attempt to extract EXIF metadata via extract_exif(image) and include it under the "exif" key.
        - If False (default) EXIF extraction is skipped.
        - Note: EXIF extraction will only be attempted when the image was opened successfully and is not reported truncated.
    hash (bool, optional, default False):
        - If True and the image is successfully opened and not truncated, attempt to compute a perceptual hash via hash_image(image) and include it under the "hash" key.
        - If False (default) hashing is skipped.
        - Note: hashing will only be attempted when the image was opened successfully and is not reported truncated.

## Returns:
    dict:
        - A mapping describing what the function discovered about the image. Possible keys:
            * "opened" (bool) — always present: True when open_image(path) returned a PIL Image, False when open_image returned None (open_image returns None for common read errors such as OSError or AttributeError).
            * "truncated" (bool) — present only if "opened" is True: True when is_image_truncated(image) indicates the image could not be fully loaded (is_image_truncated treats OSError/AttributeError from image.load() as truncated); False otherwise.
            * "size" (tuple[int, int]) — present only when "opened" is True and "truncated" is False: the image.size (width, height) tuple as returned by PIL Image.
            * "exif" (dict) — present only if exif=True and the image was opened and not truncated: the dict returned by extract_exif(image). extract_exif returns {} when the image has no EXIF or if it encounters AttributeError/OSError during EXIF access; note that extract_exif may raise UnicodeDecodeError for undecodable EXIF byte sequences (this exception will propagate).
            * "hash" (Optional[str]) — present only if hash=True and the image was opened and not truncated: string hash returned by hash_image(image) or None if hashing failed for common read-related errors (hash_image returns None for OSError/AttributeError during hashing).
        - Example return shapes:
            * For a non-existent file: {"opened": False}
            * For an opened-but-truncated image: {"opened": True, "truncated": True}
            * For a successfully opened and decoded image with exif/hash requested: {"opened": True, "truncated": False, "size": (640,480), "exif": {...}, "hash": "abc123..."}
        - The function never returns None; it returns a dict describing the outcome.

## Raises:
    - UnicodeDecodeError:
        - Condition: when exif=True and extract_exif(image) encounters a bytes EXIF value that cannot be decoded; extract_exif will propagate UnicodeDecodeError and it is not caught by extract_image_information.
    - Any exception raised by open_image(path) that is not normalized by open_image (for example, TypeError if a non-Path incompatible object is passed and open_image does not catch it) will propagate.
    - Any exception raised by hash_image(image) other than the OSError/AttributeError cases that hash_image itself catches and converts to None (for example MemoryError or TypeError inside imagehash.phash) will propagate to the caller.
    - Summary of helper contracts (for clarity):
        * open_image(path): returns a PIL Image or None; it normalizes OSError and AttributeError to None.
        * is_image_truncated(image): returns True when image.load() raised OSError or AttributeError (treated as truncated); other exceptions will propagate.
        * extract_exif(image): returns {} on AttributeError or OSError during EXIF access; may raise UnicodeDecodeError when decoding EXIF byte values.
        * hash_image(image): returns a string hash on success or None if hashing failed due to OSError/AttributeError; other exceptions may propagate.

## Constraints:
    Preconditions:
        - The caller should pass a pathlib.Path that points to a readable filesystem location.
        - The process must have permission to access the file at path.
        - Callers should expect that network-mounted files or special file-like objects may behave like other file I/O and can raise exceptions.
    Postconditions:
        - The returned dict always contains the "opened" boolean.
        - If "opened" is True, the returned dict also contains "truncated" (bool).
        - If "opened" is True and "truncated" is False, the returned dict will contain "size" and may additionally contain "exif" and/or "hash" depending on the boolean flags and downstream helper behavior.
        - The function does not close image resources itself; if open_image returns a PIL Image object, it is not explicitly closed here — callers or helper functions may close it. (Note: open_image returns a PIL Image in the success case; callers who need deterministic release should close images if necessary.)

## Side Effects:
    - Performs filesystem I/O indirectly by calling open_image(path) which invokes PIL.Image.open; this may open a file descriptor until the image object is closed.
    - Calls is_image_truncated(image) which executes image.load(); that may perform further I/O and allocate memory to decode pixel data.
    - Calling extract_exif(image) inspects in-memory EXIF structures but does not perform additional I/O.
    - Calling hash_image(image) computes an in-memory perceptual hash (no network or file writes).
    - No global variables, databases, or external services are modified by this function.

## Control Flow:
flowchart TD
    Start[Start: receive path, exif flag, hash flag]
    Start --> Open[Call open_image(path)]
    Open -->|open_image returned None| ReturnOpenedFalse[Set information["opened"]=False and return information]
    Open -->|open_image returned Image| SetOpenedTrue[Set information["opened"]=True]
    SetOpenedTrue --> TruncCheck[Call is_image_truncated(image)]
    TruncCheck -->|True| SetTruncated[Set "truncated"=True and return information]
    TruncCheck -->|False| SetNotTruncated[Set "truncated"=False]
    SetNotTruncated --> SetSize[Set "size" = image.size]
    SetSize -->|exif is True| DoExif[Call extract_exif(image) -> set "exif" (may raise UnicodeDecodeError)]
    DoExif --> Next1
    SetSize -->|exif is False| Next1[continue]
    Next1 -->|hash is True| DoHash[Call hash_image(image) -> set "hash" (may be None)]
    DoHash --> Next2
    Next1 -->|hash is False| Next2[continue]
    Next2 --> ReturnFull[Return assembled information dict]

## Examples:
1) Basic usage (no EXIF / hash):
    - Caller wants only whether the file is readable and its size if so.
    - result = extract_image_information(Path("/data/images/img1.jpg"))
    - Possible outcomes:
        * {"opened": False}
        * {"opened": True, "truncated": True}
        * {"opened": True, "truncated": False, "size": (1024,768)}

2) Request EXIF and hash, with defensive handling for decode errors:
    - If you need EXIF and a perceptual hash for downstream indexing, and you want to gracefully handle non-decodable EXIF bytes:
    - try:
          info = extract_image_information(Path("photo.jpg"), exif=True, hash=True)
      except UnicodeDecodeError:
          # EXIF decoding encountered an undecodable bytes sequence;
          # decide fallback (e.g., skip EXIF or use a best-effort decode)
          info = extract_image_information(Path("photo.jpg"), exif=False, hash=True)
      # Now inspect info: if info["opened"] is False -> skip; if info["truncated"] True -> skip processing; otherwise use size/exif/hash.

3) Batch processing pattern:
    - For each Path p in a dataset:
          info = extract_image_information(p, exif=False, hash=True)
          if not info["opened"] or info.get("truncated", False):
              continue  # skip unreadable or truncated images
          # use info["size"] and info["hash"] (hash may be None if hashing failed)

## `src.ydata_profiling.model.pandas.describe_image_pandas.image_summary` · *function*

## Summary:
Produce an aggregated per-series summary of image files: counts of truncated images, a Series of image dimensions, aggregate statistics for width/height/area, and optional duplicate-hash and EXIF summaries when requested.

## Description:
This function is designed to summarize a pandas Series containing image file references (typically pathlib.Path objects or file path strings) by applying a per-file extractor and aggregating results.

Known callers within the codebase and typical context:
- describe_image_1d and other per-column image summarizers in the image-profiling pipeline. These callers pass a pandas Series representing a dataset column and request a compact image-level summary to include in a column report.
- Typical trigger: invoked during dataset profiling when a column has been detected or annotated as containing image file paths and the profiling pipeline needs image-specific aggregate statistics and optional metadata (EXIF or perceptual hash analysis).

Why this logic is extracted:
- Centralizes the per-column aggregation logic for image files: mapping per-file extracted metadata into column-level aggregates. Keeping this logic in a single function avoids duplication of the apply + aggregation pattern (count truncated, compute width/height/area, optionally deduplicate by hash and aggregate EXIF) across higher-level profiling code.

Note on helper usage:
- When hash=True, this function calls the local helper count_duplicate_hashes to compute the number of duplicate perceptual hashes. Per the helper's own documentation, count_duplicate_hashes is implemented as a small utility and the repository snapshot did not identify any other direct callers beyond usage by summarization helpers; image_summary is a legitimate caller of that helper in the image-aggregation pipeline.

## Args:
    series (pd.Series):
        - A pandas Series whose elements are filesystem references to image files (commonly pathlib.Path objects or path-like strings).
        - Requirement: elements should be suitable inputs for extract_image_information (which expects a pathlib.Path; strings may be coerced elsewhere, but passing Path objects is the safe choice).
    exif (bool, optional, default False):
        - If True, the function requests per-file EXIF data from extract_image_information and aggregates EXIF keys/values via extract_exif_series.
        - Interdependency: EXIF extraction is only attempted for files that extract_image_information reports as opened=True and truncated=False. If extract_image_information raises UnicodeDecodeError while extracting EXIF, that exception will propagate out of image_summary.
    hash (bool, optional, default False):
        - If True, the function requests per-file perceptual hashes from extract_image_information and computes a duplicate-hash count using the local helper count_duplicate_hashes.
        - Interdependency: hashing is only attempted for files that extract_image_information reports as opened=True and truncated=False. Hash values may be None for individual files (hashing failed); count_duplicate_hashes ignores entries that lack a 'hash' key.

## Returns:
    dict:
        - A mapping of summary metrics. The returned dictionary always contains at least:
            * "n_truncated" (int) — number of images reported as truncated by extract_image_information (count of items where the image_information mapping contains "truncated" and its value is True).
            * "image_dimensions" (pd.Series) — a pandas Series named "image_dimensions" whose values are (width, height) tuples for every image where extract_image_information returned a "size" key (only non-truncated, opened images).
        - Additional entries added by aggregation:
            * All keys returned by named_aggregate_summary(image_widths, "width") are merged into the top-level summary (these are the aggregate statistics computed over image widths; exact key names depend on named_aggregate_summary's contract).
            * All keys returned by named_aggregate_summary(image_heights, "height") are merged into the top-level summary (aggregate statistics for heights).
            * All keys returned by named_aggregate_summary(image_areas, "area") are merged into the top-level summary (aggregate statistics for areas).
        - Conditional entries:
            * If hash is True:
                - "n_duplicate_hash" (int) — number of duplicate perceptual hash occurrences across the images, computed by count_duplicate_hashes(image_information). A value of 0 indicates no duplicates (or no hash-bearing items).
            * If exif is True:
                - "exif_keys_counts" (dict) — the mapping exif_series["exif_keys"] returned by extract_exif_series; maps EXIF key -> number of images that contained that key.
                - "exif_data" (dict) — the full dict returned by extract_exif_series: includes "exif_keys" and, for each observed EXIF key, a pandas.Series counting observed values for that key.
        - Edge cases / shapes:
            * If no image yielded a "size" key, "image_dimensions" will be an empty pd.Series (name "image_dimensions"); subsequent aggregates will be computed on empty Series (behavior depends on named_aggregate_summary implementation).
            * If no images provided hashes (or hash=False), "n_duplicate_hash" will be omitted.
            * If exif=True but no images had EXIF, "exif_keys_counts" will be an empty dict and "exif_data" will be the dict returned by extract_exif_series for empty input.

## Raises:
    - Propagated exceptions from helpers:
        * UnicodeDecodeError:
            - Condition: occurs when exif=True and extract_image_information invokes extract_exif which attempts to decode EXIF byte sequences that are invalid; extract_image_information does not catch UnicodeDecodeError and it will propagate through image_summary.
        * Any exception raised by extract_image_information during per-element processing:
            - Because series.apply executes the extractor for each element, exceptions raised inside extract_image_information (other than those it normalizes) will propagate and may cause the apply to raise; examples include TypeError if an element is an incompatible type.
        * Any exception raised by named_aggregate_summary or count_duplicate_hashes or extract_exif_series:
            - For example, NameError if pandas is not available under the expected name in a helper that uses pd.Series, or pandas-specific exceptions from aggregate computations.
    - The function itself contains no explicit raise statements, but callers must handle exceptions coming from the underlying helpers.

## Constraints:
    Preconditions:
        - Input must be a pandas Series (pd.Series). Passing a non-Series object will likely cause AttributeError/TypeError from the call series.apply(...).
        - Elements of series should be appropriate for extract_image_information (prefer pathlib.Path); otherwise helper may raise TypeError or other I/O-related errors.
        - The runtime must have access (permissions) to files referenced by the series if those files are to be opened (extract_image_information performs filesystem I/O).
    Postconditions:
        - The returned dict contains "n_truncated" and "image_dimensions" keys.
        - If exif/hash are requested, corresponding summary keys (exif_data/exif_keys_counts and/or n_duplicate_hash) are present unless helper functions raise.
        - The function does not mutate the input Series itself; it constructs new pandas Series objects for aggregated values.

## Side Effects:
    - Indirect filesystem I/O: extract_image_information will open image files via PIL.Image.open and call image.load() for truncation checks and decoding; these operations may open file descriptors and allocate memory.
    - CPU and memory use: decoding images and computing perceptual hashes (when hash=True) may be CPU- and memory-intensive.
    - No network I/O, no file writes, no global variable mutations are performed by image_summary itself; any side effects arise purely from the helper functions it calls.

## Control Flow:
flowchart TD
    Start[Start: receive series, exif flag, hash flag]
    Start --> Map[Call series.apply(partial(extract_image_information, exif=exif, hash=hash))]
    Map --> image_information[image_information: iterable of per-file dicts]
    image_information --> CountTrunc[Compute n_truncated = count of items with 'truncated'==True]
    CountTrunc --> BuildDims[Build image_dimensions Series from items with 'size' key]
    BuildDims --> Widths[Compute image_widths = image_dimensions.map(lambda x: x[0])]
    Widths --> AggregateWidth[Update summary with named_aggregate_summary(image_widths, "width")]
    AggregateWidth --> Heights[Compute image_heights = image_dimensions.map(lambda x: x[1])]
    Heights --> AggregateHeight[Update summary with named_aggregate_summary(image_heights, "height")]
    AggregateHeight --> Areas[Compute image_areas = image_widths * image_heights]
    Areas --> AggregateArea[Update summary with named_aggregate_summary(image_areas, "area")]
    AggregateArea --> CheckHash{hash flag?}
    CheckHash -- Yes --> DupHash[Compute n_duplicate_hash = count_duplicate_hashes(image_information); add to summary]
    CheckHash -- No --> SkipHash
    DupHash --> CheckExif{exif flag?}
    SkipHash --> CheckExif
    CheckExif -- Yes --> ExifSeries[Call extract_exif_series([x["exif"] for x in image_information if "exif" in x])]
    ExifSeries --> AddExif[Add exif_keys_counts and exif_data to summary]
    CheckExif -- No --> SkipExif
    AddExif --> Return[Return assembled summary dict]
    SkipExif --> Return

## Examples:
1) Basic usage (width/height/area aggregates only):
    - Input: a pandas Series of pathlib.Path objects referencing image files
    - summary = image_summary(series)
    - Typical keys in summary:
        * "n_truncated": 2
        * "image_dimensions": pd.Series([(640,480), (1024,768), ...], name="image_dimensions")
        * plus keys produced by named_aggregate_summary for "width", "height", and "area"

2) Request EXIF and hash with defensive handling:
    - To collect EXIF and duplicate-hash info but handle EXIF decode failures gracefully:
        try:
            summary = image_summary(series, exif=True, hash=True)
        except UnicodeDecodeError:
            # EXIF decoding failed for at least one image; retry without EXIF or handle per-project policy
            summary = image_summary(series, exif=False, hash=True)
    - On success, summary will also include:
        * "n_duplicate_hash": integer count of duplicate perceptual hashes (if any)
        * "exif_keys_counts": dict mapping EXIF key -> occurrence count
        * "exif_data": dict containing series per EXIF key with value counts

3) Handling empty or non-image entries:
    - If the input series contains non-existent paths or non-image files, extract_image_information will mark such items as opened=False or truncated=True; image_summary will exclude these from image_dimensions and aggregates. The function returns a dictionary that reflects only successfully-decoded image sizes.

## `src.ydata_profiling.model.pandas.describe_image_pandas.pandas_describe_image_1d` · *function*

## Summary:
Accepts a profiling Settings object, a pandas Series of image file references, and a summary dict; validates the Series and delegates image-specific aggregation to the image_summary helper, merging its results into the provided summary and returning the unchanged config and series together with the updated summary.

## Description:
- Known callers and typical context:
    - This function is used as the pandas-specific 1D image describer within the dataset profiling pipeline when a column has been identified or annotated as containing image file paths. Higher-level profiling code (for example, per-column describers in the image-profiling pipeline) will call this function as part of producing a column report.
    - Typical trigger: invoked during column-level profiling when the pipeline needs image-specific statistics (dimensions, area aggregates, optional EXIF and duplicate-hash summaries).

- Why this logic is extracted:
    - Enforces the input validation and the responsibility boundary for pandas Series inputs (no NaNs, must expose a .str accessor) and centralizes the delegation of per-file image aggregation to image_summary. Keeping these checks and the summary.merge step here prevents duplication of validation and merging logic across other callers.

## Args:
    config (Settings):
        - A profiling configuration object.
        - Used only to read the boolean flag at config.vars.image.exif and pass it to image_summary to control whether EXIF extraction is requested.
        - No mutation of config is performed by this function.
    series (pd.Series):
        - A pandas Series containing image file references (path-like strings or pathlib.Path objects).
        - Preconditions:
            * series.hasnans must be False (no NaNs allowed).
            * series must expose a .str accessor (i.e., hasattr(series, "str") must be True). This typically holds for pandas Series of string-like values.
    summary (dict):
        - A mapping object to which image_summary will add keys/metrics.
        - The function mutates this dict in-place by calling summary.update(...).
        - Caller-supplied summary may contain other column-level metrics; keys from image_summary will be merged into it (overwriting any existing keys with the same names).

## Returns:
    Tuple[Settings, pd.Series, dict]:
        - The function returns a 3-tuple: (config, series, summary).
        - Semantics:
            * config: the same Settings instance passed in (returned unchanged).
            * series: the same pd.Series passed in (returned unchanged).
            * summary: the same dict object passed in, after it has been updated in-place with the dict returned by image_summary(series, config.vars.image.exif).
        - All image-derived summary keys that image_summary produces (minimum includes "n_truncated" and "image_dimensions", plus width/height/area aggregates and conditionally EXIF/hash-related keys) will be present in the returned summary, subject to the helper's behavior and flags.

## Raises:
    ValueError:
        - If series.hasnans is True, raises ValueError with the exact message: "May not contain NaNs".
        - If the series does not have a .str accessor (hasattr(series, "str") is False), raises ValueError with the exact message: "series should have .str accessor".
    Propagated exceptions from helpers:
        - Any exceptions raised by image_summary (or its transitive helpers) will propagate unchanged. Notable examples (raised by underlying helpers, not by this function directly) include:
            * UnicodeDecodeError — may occur if EXIF extraction is requested and decoding of EXIF bytes fails.
            * IO or PIL-related errors if file access or image decoding fails for an element.
            * TypeError/AttributeError if series elements are of incompatible types for the helpers.
        - This function does not wrap or transform exceptions from image_summary.

## Constraints:
- Preconditions:
    - Caller must provide a pandas Series with no NaNs and with a .str accessor.
    - config.vars.image.exif must be a valid boolean-like value (the code reads and passes it directly to image_summary). The function does not validate the type; passing a non-boolean may produce downstream errors in image_summary.
    - The runtime must have permission to read files referenced by the series for image_summary to succeed.
- Postconditions:
    - The returned summary dict has been updated with entries produced by image_summary.
    - The original config and series objects are not modified by this function (aside from potential external mutations from image_summary that operate on other objects; this function itself only calls image_summary and updates the summary dict).

## Side Effects:
- Mutates the provided summary dict in-place by merging the image_summary result into it.
- Indirect I/O and CPU work occurs because image_summary (and its helpers) will generally open and read image files, decode image data, optionally compute perceptual hashes, and may extract EXIF metadata. Those operations may open file descriptors and use CPU/memory.
- The function itself performs no file writes, network calls, or global state mutations beyond the summary dict update.

## Control Flow:
flowchart TD
    Start[Start: receive config, series, summary]
    Start --> CheckNaN{series.hasnans?}
    CheckNaN -- True --> RaiseNaN[Raise ValueError "May not contain NaNs"]
    CheckNaN -- False --> CheckStr{hasattr(series,"str")?}
    CheckStr -- False --> RaiseStr[Raise ValueError "series should have .str accessor"]
    CheckStr -- True --> CallImageSummary[Call image_summary(series, config.vars.image.exif)]
    CallImageSummary --> UpdateSummary[summary.update(result_of_image_summary)]
    UpdateSummary --> Return[Return (config, series, summary)]

## Examples:
1) Typical (happy-path) usage inside a profiling pipeline:
    - Given:
        * config is a Settings instance with config.vars.image.exif == False
        * series is a pd.Series of pathlib.Path objects with no NaNs
        * summary is an existing dict (e.g., {})
    - Call:
        try:
            config, series, summary = pandas_describe_image_1d(config, series, summary)
        except ValueError as exc:
            # Handle validation failure (bad series input)
            raise
    - Result:
        * summary now contains image-derived keys produced by image_summary (e.g., "n_truncated", "image_dimensions", width/height/area aggregates).

2) Defensive usage with EXIF enabled and error handling:
    - If config.vars.image.exif is True, EXIF extraction may raise UnicodeDecodeError for malformed EXIF bytes. Wrap the call if you wish to fall back:
        try:
            config, series, summary = pandas_describe_image_1d(config, series, summary)
        except UnicodeDecodeError:
            # Fallback strategy: retry without EXIF extraction
            config.vars.image.exif = False
            config, series, summary = pandas_describe_image_1d(config, series, summary)

3) Handling invalid series inputs:
    - If the input series may contain NaNs or non-string-like values, sanitize before calling:
        if series.hasnans:
            series = series.dropna()
        if not hasattr(series, "str"):
            series = series.astype(str)
        config, series, summary = pandas_describe_image_1d(config, series, summary)

