# `imghdr_patch.py`

## `src.ydata_profiling.utils.imghdr_patch.test_jpeg1` · *function*

## Summary:
Detects JPEG files by checking for the JFIF marker within the first 23 bytes of a header buffer and returns the string "jpeg" when found.

## Description:
This small predicate is intended to be used as an imghdr-style test function: given a header buffer and an optional file indicator it determines whether the data represents a JPEG file using the JFIF signature. Typical integration is to register this function in a list of tests used by a higher-level image type detector (for example, the standard library imghdr.what mechanism). No direct callers are discovered inside this component; it is designed to be invoked by image-detection dispatchers that pass the first bytes of a file as h.

This logic is extracted into its own function because:
- It encapsulates a single, well-defined detection heuristic (presence of the JFIF signature in a bounded header range).
- It matches the expected shape of imghdr-style test functions (two-argument signature), allowing it to be appended to a tests list and reused by detection frameworks without inlining conditional checks throughout the codebase.
- It isolates the heuristic so it can be tested independently and replaced or extended without changing caller code.

## Args:
    h (bytes or bytes-like): The header buffer containing at least the initial bytes of the file. The function examines h[:23], so h should be a sequence type supporting slicing and membership checks (typically bytes). Passing a non-bytes-like object may raise TypeError.
    f (str | file-like | None): Secondary file indicator passed by the caller (for compatibility with imghdr-style test signatures). This argument is ignored by this function.

## Returns:
    str | None:
        - "jpeg" if the byte sequence b"JFIF" appears anywhere within the first 23 bytes of h (h[:23]).
        - None if the JFIF signature is not found in the examined slice.
    Notes:
        - The function uses an implicit None return when the condition fails (no explicit return statement).
        - The return value is a simple discriminator string intended for use by detection frameworks that aggregate results from multiple test functions.

## Raises:
    TypeError:
        - If h does not support slicing or membership testing with a bytes literal (for example, if h is None or an incompatible type), Python will raise a TypeError when evaluating b"JFIF" in h[:23. This exception is not explicitly raised by the function but can occur from the attempted operations on h.

## Constraints:
    Preconditions:
        - The caller must supply h as a bytes-like object (commonly the first N bytes read from a file). The function only inspects up to the first 23 bytes, so providing at least that many bytes is typical but not strictly required: shorter buffers are sliced and inspected normally.
        - f may be any value; it is unused.
    Postconditions:
        - If the function returns "jpeg", the caller can rely on the presence of the ASCII JFIF marker somewhere within the first 23 bytes of the provided header buffer.
        - If the function returns None, it guarantees nothing about the file beyond the absence of the JFIF marker in h[:23].

## Side Effects:
    - None. This function performs only in-memory checks and does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start([Start]) --> SliceHeader["Compute h[:23]"]
    SliceHeader --> CheckJFIF{"Does b\"JFIF\" appear in h[:23]?"}
    CheckJFIF -- Yes --> ReturnJPEG[/"Return \"jpeg\""/]
    CheckJFIF -- No --> ReturnNone[/"Return None (implicit)"/]
    ReturnJPEG --> End([End])
    ReturnNone --> End

## Examples:
    Example 1 — Direct usage with a bytes header:
        # Suppose header is the first bytes read from a file
        header = b'...JFIF...\x00'  # contains JFIF within the first 23 bytes
        result = test_jpeg1(header, None)
        # result == "jpeg"

    Example 2 — Registering for imghdr-style detection:
        # A detection dispatcher typically calls a sequence of test functions
        import imghdr
        # If integrating manually: append this test to the list used by the dispatcher
        imghdr.tests.append(test_jpeg1)
        # Then imghdr.what(filename) will invoke registered tests (subject to imghdr's behavior).

    Example 3 — Handling unexpected input types:
        try:
            result = test_jpeg1(None, None)  # passing None will raise TypeError
        except TypeError:
            # Handle the invalid header buffer case (e.g., log or skip)
            result = None

## `src.ydata_profiling.utils.imghdr_patch.test_jpeg2` · *function*

## Summary:
Performs a quick header-based detection and returns the string "jpeg" when the provided header bytes match a specific 32-byte JPEG marker sequence; otherwise returns None.

## Description:
This function implements a focused, fast heuristic intended for use as an imghdr-style test callback or within an image-type detection pipeline that tries multiple header tests in sequence. It inspects a small prefix of the file header and only reports a match when the header length, a specific sixth-byte value, and an exact 32-byte prefix all match the expected JPEG marker.

Known callers and typical usage:
- Typically invoked by an imghdr-style test runner or an image-detection pipeline that iterates through registered test functions and passes the file header (first bytes) and the filename/file object to each test.
- No direct callers are required in this module; the function is designed to be registered (or inserted) into a sequence of detector callbacks. In many setups this function will be appended to or inserted into imghdr.tests so the stdlib-like detection loop can call it.
- Within this repository a closely identical implementation exists in another module; usage is generally via generic image detection utilities rather than direct imports.

Reason for extraction:
- Encapsulates a single detection heuristic so it can be registered, swapped, or unit-tested independently from other detection logic. Keeping the check isolated keeps the responsibility narrow (single-responsibility) and allows reuse across detection pipelines.

## Args:
    h (bytes | bytearray | memoryview | other bytes-like, required)
        - The header bytes to test. The function uses len(h), indexing h[5], and slicing h[:32].
        - For meaningful detection callers should provide at least 32 bytes (reading the first 32 bytes of the file). If fewer than 32 bytes are provided, the function returns None.
    f (Any, optional)
        - Filename or file-like object provided for API compatibility with imghdr-style test signatures.
        - This parameter is not accessed by the function and may be None.

Interdependencies:
    - JPEG_MARK (module-level constant): The function compares h[:32] against JPEG_MARK. JPEG_MARK must exist in the module scope where this function is executed and is expected to be a bytes object of length 32 representing the expected JPEG marker sequence. If JPEG_MARK is not defined, a NameError will be raised at evaluation time.

## Returns:
    str or None
    - "jpeg": returned when all of the following are true:
        * len(h) >= 32
        * h[5] == 67 (integer 67, equals 0x43)
        * h[:32] == JPEG_MARK
    - None: returned when any of the above conditions is not met. The function uses implicit fall-through and returns None when it does not explicitly return "jpeg".

## Raises:
    NameError
        - If JPEG_MARK is not defined in the module namespace at the time the function executes, attempting to evaluate the equality h[:32] == JPEG_MARK will raise a NameError.
    TypeError / AttributeError / IndexError
        - If h does not support len(), indexing, or slicing, or if indexing yields a type incompatible with the numeric comparison, Python will raise the corresponding error (e.g., TypeError if h is None, IndexError should not occur because the function first checks len(h) >= 32).
        - These exceptions are not raised explicitly by the function but arise from standard Python operations on the provided arguments.

## Constraints:
Preconditions:
    - JPEG_MARK must be defined (as a bytes-like object of length 32) in the module namespace before calling this function.
    - Callers should pass an indexable, sliceable bytes-like object (bytes, bytearray, or memoryview). For a chance to match, h should contain at least 32 bytes.

Postconditions:
    - No mutation of inputs occurs.
    - The function will either return the literal string "jpeg" (on match) or None (no match); no other return values or side effects occur.

## Side Effects:
    - None. The function performs pure inspection of its inputs and does not perform file I/O, network access, or mutate external/global state.

## Control Flow:
flowchart TD
    Start --> LenCheck{len(h) >= 32?}
    LenCheck -- No --> ReturnNone1[return None]
    LenCheck -- Yes --> Byte5Check{h[5] == 67?}
    Byte5Check -- No --> ReturnNone2[return None]
    Byte5Check -- Yes --> PrefixCheck{h[:32] == JPEG_MARK?}
    PrefixCheck -- No --> ReturnNone3[return None]
    PrefixCheck -- Yes --> ReturnJPEG[return "jpeg"]

## Examples:
Usage pattern (end-to-end, safe):
    1) Open the file in binary mode and read at least the first 32 bytes into header_bytes (e.g., read 64 bytes to be conservative).
    2) Call the detection function with header_bytes as the first argument and the filename (or None) as the second:
        - If the function returns "jpeg" then treat the file as the detected JPEG variant and stop further detection.
        - If the function returns None continue with other detector functions or mark the file type unknown.
    3) Ensure JPEG_MARK is defined in the module prior to registering or calling this test to avoid NameError.

Error-handling guidance:
    - When reading headers from untrusted inputs, guard file reads (e.g., catch OSError when opening/reading).
    - If you cannot guarantee JPEG_MARK will be defined at import time, delay registration of this function until after JPEG_MARK is set, or wrap calls in a try/except NameError if you must call it earlier.

## `src.ydata_profiling.utils.imghdr_patch.test_jpeg3` · *function*

## Summary:
Detects JPEG image headers by inspecting the provided header bytes and returns the string "jpeg" when the header matches common JPEG signatures.

## Description:
This function examines raw header bytes (the initial bytes read from a candidate image file) to determine whether the data represents a JPEG image. It is intended to be used as a probing/test function compatible with the imghdr test function API (functions that inspect header bytes and optionally a file object and return a format name or None). Typical callers:
- imghdr.what() or any code that iterates over a list of imghdr-style test functions (for example, when this function is appended to imghdr.tests). In that pipeline, a header byte sequence and an optional file object are passed in; if this function recognizes the header as JPEG it returns "jpeg", allowing imghdr.what() to report the image type.

This logic is extracted into its own function because:
- It encapsulates the signature-specific detection rules for JPEG, isolating byte-level pattern checks from higher-level file inspection and registration logic.
- It fits the imghdr extensibility model (small functions that return a format name or None), so separating it simplifies adding or overriding detection logic without modifying calling code.

## Args:
    h (bytes-like): A bytes-like object containing the initial bytes read from a file (the "header"). The function performs slicing and comparisons on this object (h[6:10], h[:2]), so it must support those operations. There is no minimum required length to call safely: slicing on short byte sequences returns shorter bytes rather than raising.
    f (file-like or any): An unused second parameter kept for API compatibility with imghdr test functions. Callers may pass a file-like object or None; the function does not read or use it.

## Returns:
    str or None:
    - "jpeg": returned when either of the following conditions is true:
        * bytes 6..9 of h (h[6:10]) exactly equal b"JFIF" or b"Exif"
        * the first two bytes of h (h[:2]) exactly equal the JPEG SOI marker b"\xff\xd8"
    - None: implicitly returned when neither condition is met (the function contains no explicit return in that case).

## Raises:
    This function does not raise exceptions under normal operation. The slicing and byte comparisons used are safe on short byte sequences (they produce shorter bytes objects); no explicit error conditions are triggered by the implementation.

## Constraints:
    Preconditions:
    - The caller should supply a bytes-like header in h. While the function tolerates short inputs, providing at least the first 10 bytes of the file increases chance of correct detection (some JPEGs are identified by bytes at offsets 6–9).
    - f can be any value or None; it is present only for compatibility.
    Postconditions:
    - If the header matches known JPEG signatures (JFIF or Exif at offset 6 or SOI at start), the function returns "jpeg".
    - Otherwise, the function returns None and has no side effects.

## Side Effects:
    - None. The function performs pure inspection of the given header bytes and does not perform I/O, mutate external state, or call external services.

## Control Flow:
flowchart TD
    Start([Start: test_jpeg3(h,f)])
    CheckExifJFIF{h[6:10] in (b"JFIF", b"Exif")}
    CheckSOI{h[:2] == b"\\xff\\xd8"}
    ReturnJPEG([return "jpeg"])
    ReturnNone([return None (implicit)])

    Start --> CheckExifJFIF
    CheckExifJFIF -- True --> ReturnJPEG
    CheckExifJFIF -- False --> CheckSOI
    CheckSOI -- True --> ReturnJPEG
    CheckSOI -- False --> ReturnNone

## Examples (usage context described; no code imports shown):
- Integration example (conceptual):
  1. A caller collects the first N bytes from a file into a header buffer `h` (preferably >=10 bytes).
  2. The caller passes `h` and an optional file object `f` to each imghdr-style test function in turn.
  3. When this function is invoked, it returns "jpeg" if it detects either:
     - the ASCII identifier "JFIF" or "Exif" at offset 6..9, or
     - the JPEG Start Of Image marker in the first two bytes (0xFF 0xD8).
  4. The caller uses the returned "jpeg" value to classify the file; if None is returned, the caller proceeds to other tests or declares the type unknown.

- Practical note on robustness:
  - For best detection reliability, callers should supply at least the first 10 bytes of the file as `h`. If only 2 bytes are provided, the SOI check (h[:2]) can still detect typical JPEG files; detection via JFIF/Exif requires offset 6..9 to be present.

