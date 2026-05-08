# `common.py`

## `src.ydata_profiling.utils.common.update` · *function*

## Summary:
Recursively merges a mapping of updates into a target dictionary in-place, performing a deep update for nested mapping values and returning the (mutated) target dictionary.

## Description:
- Known callers:
    - No specific callers were provided in the supplied context. This utility is a generic helper intended for places that need to apply nested configuration or data updates (for example: merging user-provided settings into default settings).
- Why this logic is extracted:
    - Encapsulates the "deep merge" behavior (recursive merging of nested mappings) so callers can request a nested update without reimplementing recursion or in-place mutation logic.
    - Keeps higher-level code concise and ensures a single, well-tested place for merging semantics and edge-case handling.

## Args:
    d (dict): Target dictionary to update. This dictionary is mutated in place. Keys must be hashable. The function expects a true dict (or a mapping that supports item assignment and .get); passing a non-dict as `d` will typically lead to runtime errors.
    u (Mapping): Source mapping containing updates. Values in this mapping that are themselves Mapping instances trigger recursive merging into corresponding entries in `d`. Any Mapping compliant object (e.g., dict, OrderedDict, custom Mapping) is accepted.

Notes on interdependencies:
    - If u contains a mapping value for a key k and d already contains a mapping at d[k], the contents of u[k] are merged into the existing d[k] recursively.
    - If u contains a mapping value for a key k and d has no entry for k, an empty dict is used as the merge target and the merged dict becomes d[k].
    - If d contains a non-mapping value at k while u contains a mapping at k, the function will attempt to call update on that non-mapping value and will likely raise at runtime (see Raises / Constraints).

## Returns:
    dict: The same dictionary object passed in as `d`, after applying updates from `u`. The returned object is mutated in-place; callers can use the return value for chaining but should be aware it is the same object as `d`.

Edge-case return behavior:
    - Even when `u` is empty, the original `d` object is returned unchanged.
    - If the merge creates nested structures that did not previously exist in `d`, those nested dicts are created and assigned into `d`.

## Raises:
    - TypeError or AttributeError: Not explicitly raised in the code, but may occur if assumptions are violated:
        * If `d` is not a mapping that supports item assignment (d[k] = ...), assignment will raise a TypeError.
        * If `d.get(k, {})` returns an object that is not a mapping and the corresponding value in `u` is a Mapping, recursive call will attempt mapping operations on a non-mapping and may raise an AttributeError/TypeError.
    - Any exceptions raised by custom Mapping implementations used as `u` or `d` (e.g., in their .items() or __setitem__) will propagate.

## Constraints:
Preconditions:
    - `d` should be a mutable mapping that supports .get(key, default) and item assignment d[key] = value (concrete dict is the safe choice).
    - Keys in `u` and `d` must be hashable.
    - Values in `u` that are intended to be merged must implement collections.abc.Mapping (e.g., dict-like).

Postconditions:
    - For each key k in `u`:
        * If u[k] is a Mapping, then after return d[k] is a mapping with keys merged recursively from u[k] into the previous d[k] mapping (or into a fresh dict if none existed).
        * Otherwise, d[k] equals u[k].
    - The object identity of `d` is preserved (the same dict is returned).

## Side Effects:
    - Mutates the input dictionary `d` in-place.
    - No file, network, stdout, or external state (database/cache) side effects are performed.
    - No external service calls.

## Control Flow:
flowchart TD
    Start --> Iterate[for each (k, v) in u.items()]
    Iterate --> IsMapping{isinstance(v, Mapping)?}
    IsMapping -- Yes --> GetTarget[d_target = d.get(k, {})]
    GetTarget --> Recurse[call update(d_target, v)]
    Recurse --> Assign[d[k] = returned mapping]
    IsMapping -- No --> AssignDirect[d[k] = v]
    AssignDirect --> Next[continue loop]
    Assign --> Next
    Next --> Iterate
    Iterate --> End[return d]

## Examples:
- Typical nested merge:
    - Given d = {'a': {'x': 1}}, u = {'a': {'y': 2}, 'b': 3}
    - After call, d becomes {'a': {'x': 1, 'y': 2}, 'b': 3} and the same dict object is returned.

- Behavior when d lacks the nested mapping:
    - Given d = {}, u = {'a': {'y': 2}}
    - After call, d becomes {'a': {'y': 2}}.

- Caution / error handling:
    - If d already contains a non-mapping for key 'a' (e.g., d = {'a': 5}) and u = {'a': {'y': 2}}, the function will attempt to treat 5 as a mapping and will likely raise a TypeError or AttributeError. Guarding pattern:
        * Ensure mapping types before calling update, e.g., if not isinstance(d.get('a'), dict): d['a'] = {} then call update.

## `src.ydata_profiling.utils.common._copy` · *function*

## Summary:
Copies the file referenced by `self` to the given `target` path as a filesystem operation; no value is returned.

## Description:
This helper enforces that the source object represents an existing regular file and performs a filesystem copy to the provided destination using the standard library copy routine.

Known callers within the provided context:
- None discovered in the supplied fragment of the repository. In the larger codebase this is typically used by file-handling utilities or small Path-like convenience wrappers when an explicit file copy is required.

Why this is a separate function:
- Centralizes the precondition check (source must be a file) and the actual file-copy operation so callers do not duplicate assertion logic and do not need to directly interact with shutil. It encapsulates the responsibility "ensure this object is a file, then copy it to target" as a single atomic helper.

## Args:
    self (pathlib.Path or any object implementing is_file() and __str__()):
        - The source file object. Must implement is_file() returning bool and must yield a path string when converted to str().
        - Precondition: self.is_file() must evaluate to True (see Raises and Constraints).
    target (str or path-like):
        - Destination path where the file will be copied.
        - Accepts either a file path (overwrites or creates that file) or a directory path (in which case the source filename is used inside that directory) — behavior delegated to shutil.copy.

Interdependencies:
- The function assumes that converting `self` to a string yields a valid filesystem path for the source; `target` is passed unchanged to shutil.copy and must be acceptable to that API.

## Returns:
    None
    - The function does not return any value. Its observable outcome is the side-effect of having a copy of the source file placed at `target` (or raising an exception on failure).

## Raises:
    AssertionError
        - Raised when self.is_file() evaluates to False. This is an explicit precondition check implemented with an assert statement.
    AttributeError
        - If `self` does not implement is_file(), attempting to call self.is_file() will raise AttributeError.
    FileNotFoundError
        - Raised by the underlying shutil.copy if the source or an intermediate path component is missing due to a race condition (even if the earlier assert passed) or if `target`'s directory does not exist.
    PermissionError
        - Raised by shutil.copy when the process lacks permission to read the source or write the destination.
    shutil.SameFileError (or equivalent OSError)
        - May be raised by shutil.copy/copyfile when source and destination refer to the same file on the filesystem.
    OSError (general)
        - Any other OS-level errors produced by the underlying copy operation (disk full, I/O errors, invalid path syntax, etc).

## Constraints:
Preconditions:
    - `self` must be a path-like object representing a file (self.is_file() must return True).
    - `self` must be convertible to a string that denotes the source path on the filesystem.
    - The calling code must have appropriate filesystem permissions for reading the source and writing to the destination.

Postconditions (if no exception is raised):
    - A file exists at `target` (or inside `target` if `target` is a directory) that is a copy of the content of `self`.
    - The source file is unchanged.
    - No guarantee of atomicity: callers must be aware that partial copies are possible if an error occurs mid-copy.

## Side Effects:
    - Performs filesystem I/O (reads from source, writes to destination).
    - May overwrite an existing file at the destination without further checks (delegated to shutil.copy).
    - Does not modify any global variables, in-memory caches, or external network services.

## Control Flow:
flowchart TD
    Start --> CheckIsFile
    CheckIsFile{self.is_file() returns True?}
    CheckIsFile -->|False| RaiseAssertionError[AssertionError raised]
    CheckIsFile -->|True| CallShutilCopy[call shutil.copy(str(self), target)]
    CallShutilCopy -->|success| End[Return None]
    CallShutilCopy -->|error| PropagateException[Underlying exception propagated]

## Examples:
Example 1 — typical successful use (described steps):
    1. Ensure `source` is a Path-like object that points to an existing regular file.
    2. Call this helper with `self = source` and `target = destination_path`.
    3. If the operation succeeds, a copy of `source` will be present at `destination_path`.
    4. If `destination_path` is an existing directory, the copy will be created inside that directory with the same filename as `source`.

Example 2 — error handling pattern (described steps):
    1. Prepare a try/except block in the caller.
    2. Call the helper.
    3. Catch AssertionError to handle the case where the source was not a file.
    4. Catch FileNotFoundError, PermissionError, or OSError to handle filesystem-related failures (report to user, retry, or abort).
    5. On any caught exception, take corrective action (create missing directories, adjust permissions, or log and surface the error).

Notes and implementation remarks:
    - Because the function uses an assert, if Python is run with optimizations that remove assert statements (python -O), the precondition check will not execute; callers that rely on this check should not depend on asserts for critical correctness in production environments.
    - The helper imports shutil locally; the runtime behavior is identical to calling shutil.copy directly after the is_file check.

## `src.ydata_profiling.utils.common.extract_zip` · *function*

## Summary:
Extracts all files from a ZIP archive into a target directory, raising a clear ValueError when the archive is corrupt.

## Description:
This small utility opens the provided ZIP archive (filename or file-like object) and extracts its contents into the given destination path using Python's built-in zipfile module.

Known callers within the codebase:
    - No direct internal callers were found in a repository-wide scan for this function. It is typically used by higher-level routines that need to unpack uploaded or bundled datasets, examples, or resource archives before further processing.

Why this logic is extracted into a dedicated function:
    - Encapsulates zip extraction and error translation (converts zipfile.BadZipFile into a ValueError with a concise message).
    - Keeps higher-level code clean (they don't need to import zipfile or manage the BadZipFile exception directly).
    - Centralizes the extraction behavior so error handling and any future extraction-related changes live in one place.

## Args:
    outfile (str | os.PathLike | file-like): Path to the ZIP archive or a file-like object containing ZIP data.
        - Accepts a filesystem path (string or Path-like) or an open binary file-like object compatible with zipfile.ZipFile.
        - If a path is provided, it must refer to a readable file; if a file-like object is provided it must be open for reading in binary mode.
    effective_path (str | os.PathLike): Destination directory where archive contents will be extracted.
        - Can be a string path or a pathlib.Path.
        - The process must have permission to write into this path. If the path does not already exist, behavior depends on the environment and zipfile implementation (extraction will attempt to create files/directories under the given path).

## Returns:
    None
    - On success, the function returns None and the files from the archive will be present under effective_path (subject to file system permissions and archive contents).
    - There is no return value that conveys partial success; either extraction completes or an exception is raised.

## Raises:
    ValueError("Bad zip file")
        - Raised when zipfile.ZipFile(outfile) or extraction detects that the archive is not a valid ZIP (caught zipfile.BadZipFile is re-raised as ValueError with this message).
    FileNotFoundError
        - May be raised if outfile is given as a filesystem path that does not exist (bubbled up from zipfile.ZipFile).
    PermissionError
        - May be raised when writing extracted files to effective_path if the process lacks required filesystem permissions.
    zipfile.LargeZipFile
        - May be raised by zipfile.ZipFile or extractall for ZIP64 / large-archive conditions if the environment disallows large archives; this is not caught and will propagate.
    OSError (and subclasses)
        - Low-level I/O errors (disk full, filesystem errors, invalid paths) encountered during opening or extraction may propagate.

## Constraints:
Preconditions:
    - outfile must be a readable ZIP archive path or a readable file-like object (binary).
    - The caller should ensure effective_path is a valid path where the process can write extracted files (or accept that creation may fail and raise an exception).
    - The runtime must have access to sufficient disk space for the extracted contents.

Postconditions:
    - If the function returns normally (no exception), all files and directories contained in the archive will have been extracted into effective_path (preserving archive-internal paths), subject to filesystem permissions.
    - If a zipfile.BadZipFile was encountered, a ValueError("Bad zip file") will be raised and no guarantee is made about partial extraction (partial writes may have occurred before the exception).

## Side Effects:
    - Filesystem I/O: writes files and directories under effective_path according to the archive contents.
    - Opens the archive file (outfile) for reading; if outfile is a path, the file is opened and closed by this function.
    - No network activity, no global state mutation beyond filesystem changes.

## Control Flow:
flowchart TD
    Start --> TryOpen[Try: zipfile.ZipFile(outfile)]
    TryOpen --> OpenSuccess{opened successfully?}
    OpenSuccess -->|yes| ExtractAll[z.extractall(effective_path)]
    ExtractAll --> Success[Return None]
    OpenSuccess -->|no (BadZipFile)| CatchBadZip{zipfile.BadZipFile}
    CatchBadZip --> RaiseValueError[Raise ValueError("Bad zip file")]
    RaiseValueError --> End[End]

## Examples:
Example 1 — Extracting from a filesystem path (simple usage, with error handling):
    try:
        extract_zip("data/archive.zip", "/tmp/unpacked")
    except ValueError as e:
        # The archive was detected as invalid/corrupt
        handle_invalid_archive(e)
    except (FileNotFoundError, PermissionError, OSError) as e:
        # Filesystem or permission error occurred while opening or extracting
        handle_fs_error(e)

Example 2 — Extracting from an already-open file-like object:
    with open("data/archive.zip", "rb") as f:
        # Passing a binary file-like object is supported by zipfile.ZipFile
        extract_zip(f, Path("/tmp/unpacked"))

Usage notes:
    - Always validate or sanitize archive contents if you plan to extract untrusted ZIPs (this function does not perform filename sanitization or path traversal protection).
    - If extraction needs to be atomic or sandboxed, callers should extract to a temporary directory and perform validation before moving files to a final location.

## `src.ydata_profiling.utils.common.test_jpeg1` · *function*

## Summary:
Detects a JPEG file header by checking for the ASCII "JFIF" marker in the first 23 bytes of the provided header buffer and signals detection by returning the string 'jpeg'.

## Description:
This function implements a single, focused image-type test: it checks whether the byte sequence "JFIF" appears within the first 23 bytes of a header buffer. It follows the common signature used by image-detection test hooks (two-argument test functions that accept a header buffer and a file identifier) so it can be registered with or used by an image-type detection registry (for example, the standard library's imghdr test registry) or called directly where a file's initial bytes are already available.

Known callers within this repository:
- No direct call sites were identified in the local repository for this exact function. It is provided as a reusable test that is intended to be invoked by an image-detection dispatcher or by callers that already have a file's initial bytes.

Why this logic is extracted into its own function:
- Responsibility boundary: isolates the JPEG-specific detection heuristic (presence of "JFIF" within the first 23 bytes) so it can be registered, tested, and replaced independently of higher-level file-handling logic.
- Reusability: allows the same small test to be used in multiple detection pipelines without duplicating the string-match logic.
- Testability: simplifies unit testing of the detection rule in isolation from file I/O.

## Args:
    h (bytes or bytearray): A bytes-like buffer containing the initial bytes of a candidate image file. The function inspects up to the first 23 bytes (h[:23]). Must support slicing and membership testing against a bytes pattern.
    f (any): Unused in this implementation. Provided for compatibility with two-argument test function signatures (e.g., the imghdr test hook convention). Typical callers may pass a filename (str), a file object, or None; this function does not read or use it.

## Returns:
    str or None:
    - 'jpeg' if the ASCII sequence JFIF is found anywhere within the first 23 bytes of h.
    - None if the sequence is not found or the detection condition is not met.
    Edge cases:
    - If h is shorter than 23 bytes, the slice h[:23] gracefully yields a shorter bytes object and the membership check still works; the function will return 'jpeg' only if the marker is present in those available bytes.
    - No other strings are returned by this function.

## Raises:
    TypeError: If h is not a bytes-like object (for example, if h is None or an integer), then attempting h[:23] or membership testing against a bytes literal will raise a TypeError. The function does not explicitly raise exceptions itself.

## Constraints:
Preconditions:
    - The caller should supply a bytes-like object for h. The function expects h to be indexable/sliceable and to support membership tests with bytes (e.g., b"JFIF" in h[:23]).
    - f may be omitted or any value; it is kept for signature compatibility.

Postconditions:
    - No mutation of inputs occurs.
    - The output is either the literal string 'jpeg' (indicating detection) or None (indicating no detection).

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and does not call external services. It only examines the provided header buffer.

## Control Flow:
flowchart TD
    Start --> CheckHeader
    CheckHeader["Is b\"JFIF\" present in h[:23]?"]
    CheckHeader -- Yes --> ReturnJPEG["Return 'jpeg'"]
    CheckHeader -- No --> ReturnNone["Return None (no detection)"]
    ReturnJPEG --> End
    ReturnNone --> End

## Examples:
- Positive detection scenario:
    - Input: h is a bytes buffer whose first 23 bytes include the ASCII sequence JFIF (for example, a JPEG file header that embeds the "JFIF" marker).
    - Result: the function yields the string 'jpeg', indicating the header matches the JFIF-based JPEG signature.

- Negative detection scenario:
    - Input: h is a bytes buffer that does not contain "JFIF" within its first 23 bytes (including when h is shorter than 23 bytes and the marker is not present).
    - Result: the function yields None, indicating no JPEG detection by this heuristic.

- Note on usage in a detection pipeline:
    - A dispatcher that iterates over a list of such test functions can call this function with the first N bytes of a file and ignore the f parameter; if the function returns 'jpeg', the dispatcher records that type and stops further tests.

## `src.ydata_profiling.utils.common.test_jpeg2` · *function*

## Summary:
Performs a compact header inspection and returns the literal "jpeg" when the provided header bytes match a specific 32-byte JPEG marker sequence; otherwise returns None.

## Description:
This function implements a focused, fast heuristic to detect a particular JPEG signature by inspecting the first bytes of a file. It is intended to be registered as an imghdr-style test function or used by image-detection utilities that try multiple test functions in sequence.

Known callers within the repository:
- A function with the identical body appears in src.ydata_profiling.utils.imghdr_patch.test_jpeg2 (duplicate implementation). No other direct callers were found in scanned metadata; usage is typically via an image-type detection pipeline that iterates tests.

Reason for extraction:
- Encapsulating this check as a standalone function allows it to be composed with other detection callbacks, swapped or patched independently, and kept focused on the single responsibility of deciding whether a given header corresponds to this JPEG variant.

## Args:
    h (bytes | bytearray | memoryview or other bytes-like, indexable & sliceable): The file header bytes to test. The function uses len(h), indexing h[5], and slicing h[:32]. For meaningful detection, callers should provide at least 32 bytes.
    f (str or file-like or any): Filename or file-like object passed for API compatibility with imghdr-style test signatures. This parameter is not accessed by the function and may be None.

Interdependencies:
    - JPEG_MARK (module-level constant): The function compares h[:32] against JPEG_MARK. JPEG_MARK must be defined in the module where this function is executed and is expected to be a bytes object representing the 32-byte marker sequence for the JPEG variant.

## Returns:
    str or None:
    - "jpeg": returned when all of the following conditions are satisfied:
        * len(h) >= 32
        * h[5] == 67 (integer value 67, meaning the sixth byte equals 0x43)
        * h[:32] == JPEG_MARK
    - None: returned when any of the above conditions is not met. The function uses implicit fall-through; there is no explicit else branch.

## Raises:
    NameError:
        - If JPEG_MARK is not defined in the module scope at call time, attempting to evaluate h[:32] == JPEG_MARK will raise a NameError.
    TypeError / AttributeError:
        - The function itself does not explicitly raise these, but if h does not support len(), indexing, or slicing (for example, if h is an object without these operations), Python will raise the corresponding TypeError or AttributeError when those operations are attempted. This is a caller responsibility.

Notes on types and comparisons:
    - The comparison h[5] == 67 expects that indexing h yields an integer (the case for bytes, bytearray, memoryview). If h is a str, h[5] will be a one-character string; the comparison to integer 67 will be False (no exception), and h[:32] == JPEG_MARK will be False if JPEG_MARK is bytes — the function will simply return None.
    - It is recommended that JPEG_MARK be a bytes object of length 32. If JPEG_MARK has a different type or length, equality will normally evaluate to False (not raise) unless it is undefined.

## Constraints:
Preconditions:
    - JPEG_MARK must be defined in the module namespace before calling this function.
    - h should be a bytes-like, indexable and sliceable object; callers should provide at least 32 bytes to perform the full test.

Postconditions:
    - No mutation of inputs occurs.
    - The function either returns "jpeg" or None; no other side effects.

## Side Effects:
    - None. The function performs pure inspection and does not perform file I/O, network access, or modification of global state.

## Control Flow:
flowchart TD
    Start --> LenCheck{len(h) >= 32?}
    LenCheck -- No --> ReturnNone[return None]
    LenCheck -- Yes --> Byte5Check{h[5] == 67?}
    Byte5Check -- No --> ReturnNone
    Byte5Check -- Yes --> PrefixCheck{h[:32] == JPEG_MARK?}
    PrefixCheck -- No --> ReturnNone
    PrefixCheck -- Yes --> ReturnJPEG[return "jpeg"]

## Examples:
Usage pattern (safe, end-to-end description):
    1) Open the file in binary mode and read at least the first 32 bytes into a variable header_bytes (e.g., header_bytes = fileobj.read(32) or fileobj.read(64) to be safe).
    2) Call the detection function with header_bytes and the filename (or None) as the second argument.
    3) If the function returns the string "jpeg", treat the file as the detected JPEG variant. If it returns None, continue trying other format detectors or mark the type unknown.

Error handling guidance:
    - If JPEG_MARK might not be defined at import time (for example, if registration happens before constants are set), ensure JPEG_MARK is defined before registering or calling this test to avoid NameError.
    - If files may be shorter than 32 bytes, reading less than 32 bytes is safe: the function will return None (no exception) because the length check fails.

## `src.ydata_profiling.utils.common.test_jpeg3` · *function*

## Summary:
Identify whether a file header corresponds to a JPEG image by checking common JPEG magic markers; returns the string "jpeg" when a JPEG signature is detected.

## Description:
This small predicate function examines the first bytes of a file header to decide if the data represents a JPEG file. It is compatible with the signature test interface used by Python's imghdr module: it accepts a header byte sequence and a filename argument (the filename is not used by this implementation).

Known callers within this codebase:
- No direct call sites were found in the repository. The function is provided as an `imghdr`-style test function and is intended to be used by code that implements or extends the behavior of the Python standard library imghdr.what function or by a tests registry (for example, inserted into imghdr.tests). In practice it is invoked by image type detection utilities that iterate over such test functions.

Why this logic is extracted:
- Encapsulates the JPEG-detection heuristic (checking for "JFIF", "Exif" markers and the JPEG SOI marker 0xFFD8) so it can be reused or registered with imghdr-style test suites.
- Keeps the header-checking logic small, testable, and replaceable without inlining the byte checks at call sites.

## Args:
    h (bytes): The initial bytes of a file (commonly up to a few dozen bytes). This function slices and examines these bytes; if shorter than expected, slicing still works and the comparisons simply fail.
    f (str | os.PathLike | None): Filename or path of the inspected file. This parameter is accepted for compatibility with the imghdr test function signature but is not inspected or used by this function.

## Returns:
    str | None:
        - "jpeg" if the header matches a known JPEG signature:
            * bytes 6..9 equal to b"JFIF" or b"Exif" (commonly found in JPEG APP0/APP1 segments), or
            * the first two bytes equal to b"\xff\xd8" (JPEG Start Of Image marker).
        - None if no JPEG signature is detected.

## Raises:
    This function does not raise any exceptions for typical inputs.
    - It expects `h` to be bytes-like; passing types that do not support slicing like bytes (e.g., None or an unrelated object) may raise a TypeError at call time in Python. The implementation itself performs only slicing and comparisons.

## Constraints:
Preconditions:
    - `h` should be a bytes-like object (ideally a bytes object containing the first chunk of the file contents).
    - `f` may be any value compatible with code calling imghdr-style tests; it is ignored by the implementation.

Postconditions:
    - The function will either return the string "jpeg" (if one of the signature checks matches) or return None implicitly.
    - No mutation of inputs or global state occurs.

## Side Effects:
    - None. The function performs pure, local comparisons and returns a result. There is no I/O, no global state mutation, and no network or external service calls.

## Control Flow:
flowchart TD
    Start([Start])
    CheckSignatures{h[6:10] in (b"JFIF", b"Exif")\nOR h[:2] == b"\\xff\\xd8"}
    ReturnJPEG[/return "jpeg"/]
    ReturnNone[/return None (implicit)/]
    Start --> CheckSignatures
    CheckSignatures -- True --> ReturnJPEG
    CheckSignatures -- False --> ReturnNone

## Examples:
1) Using the function directly with a header chunk:
    - Provide the first bytes of a file to detect a JPEG by header markers.
    - Example (conceptual):
        header = b"\xff\xd8\xff\xe0\x00\x10JFIF..."  # typical JPEG header
        result = test_jpeg3(header, "image.jpg")
        # result == "jpeg"

2) When header is too short:
    - Short or truncated headers simply fail the checks and return None, rather than raising.
        header = b"\xff"  # too short to contain "JFIF", but h[:2] != b"\xff\xd8"
        result = test_jpeg3(header, "image.jpg")
        # result is None

3) Integration with imghdr-style detection:
    - This function is intended to be part of a list of test functions that are called with (h, filename) by an image type detection routine. The detection routine should handle None returns as "not matched" and continue to other tests.

## `src.ydata_profiling.utils.common.convert_timestamp_to_datetime` · *function*

## Summary:
Convert a Unix epoch timestamp (seconds since 1970-01-01) into a naive datetime.datetime instance, with explicit support for negative timestamps (seconds before the epoch).

## Description:
This utility centralizes timestamp→datetime conversion and ensures consistent handling of negative (pre-1970) timestamps across callers.

Known callers within the provided snapshot:
- None discovered in the provided snapshot. Intended to be used wherever integer-like Unix timestamps must be converted to datetime objects for reporting, profiling, or feature extraction.

Why this logic is extracted:
- Handles the platform-dependent behavior of datetime.fromtimestamp for positive timestamps while providing a deterministic arithmetic-based fallback for negative timestamps.
- Avoids duplicating the asymmetrical handling required for timestamps before the epoch and documents the behavior in one place so callers can decide whether they need different semantics (e.g., UTC-aware datetimes).

## Args:
    timestamp (int):
        - Annotated as int in the function signature (timestamp: int).
        - The function will accept numeric runtime values; however, callers should be aware of how different numeric types are handled (see Returns and Examples).
        - No default value; this parameter is required.

## Returns:
    datetime:
        - A naive datetime.datetime instance (tzinfo is None).
        - For timestamp >= 0: returned value is produced by datetime.fromtimestamp(timestamp). When a float is provided, fractional seconds are preserved (datetime includes microseconds).
        - For timestamp < 0: returned value is computed as datetime(1970, 1, 1) + timedelta(seconds=int(timestamp)). The int() conversion truncates toward zero for negative floats (e.g., -1.9 -> -1), so fractional parts of negative timestamps are discarded in this branch.
        - Edge cases:
            * Positive floats keep sub-second precision via datetime.fromtimestamp.
            * Negative floats are truncated to integer seconds before applying the timedelta.
            * Very large or very small numeric values may be outside the representable range of Python's datetime on the host platform.

## Raises:
    The function itself does not explicitly raise custom exceptions, but calling it may surface the following from underlying library calls:
    - OverflowError:
        - Raised if the timestamp is too large (or the arithmetic result too large) to be represented as a datetime on the current platform.
    - OSError:
        - datetime.fromtimestamp can raise OSError for out-of-range timestamps on some platforms.
    - TypeError or ValueError:
        - May be raised if the provided timestamp is non-numeric or invalid (for example, passing None, NaN, or a non-coercible string).
    Exact triggers:
        - For non-negative inputs, errors originate from datetime.fromtimestamp(timestamp).
        - For negative inputs, errors originate from int(timestamp) or from constructing datetime(1970, 1, 1) + timedelta(seconds=...).

## Constraints:
Preconditions:
    - Callers should pass a numeric timestamp (ideally an int). If floats are used, be explicit about expected behavior for positive vs negative values.
    - The numeric value must be within the representable datetime range on the executing platform (typically year 1..9999), otherwise an exception will occur.

Postconditions:
    - Returns a naive datetime representing the supplied timestamp according to the rules above.
    - No external state is modified.

## Side Effects:
    - None. The function performs pure computation and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    A[Start: receive timestamp]
    B{timestamp >= 0 ?}
    C[Return datetime.fromtimestamp(timestamp)  (preserves fractional seconds for floats)]
    D[Return datetime(1970-01-01) + timedelta(seconds=int(timestamp))  (negative: int() truncates)]
    E[End]
    A --> B
    B -- yes --> C --> E
    B -- no --> D --> E

## Examples:
Example 1 — positive integer timestamp:
    # Typical POSIX seconds (integer)
    dt = convert_timestamp_to_datetime(1609459200)
    # dt corresponds to host-local time for 2021-01-01 00:00:00 according to datetime.fromtimestamp semantics

Example 2 — positive float timestamp preserves sub-second precision:
    # Fractional seconds are preserved for non-negative inputs
    dt = convert_timestamp_to_datetime(1609459200.5)
    # dt.microsecond reflects the fractional .5 seconds (i.e., 500000 microseconds) on success

Example 3 — negative timestamp truncation behavior:
    # Negative floats are truncated via int() before applying timedelta
    dt = convert_timestamp_to_datetime(-1.9)
    # int(-1.9) == -1, so result equals datetime(1970,1,1) + timedelta(seconds=-1)

Example 4 — defensive usage with error handling and UTC note:
    try:
        dt = convert_timestamp_to_datetime(value)
    except (TypeError, ValueError):
        # invalid, non-numeric input
        handle_invalid_input()
    except (OverflowError, OSError):
        # timestamp outside representable range on this platform
        handle_out_of_range()

Notes and recommendations:
    - datetime.fromtimestamp returns a naive datetime in local time by default. If you require a UTC-aware datetime, use datetime.utcfromtimestamp(timestamp) or datetime.fromtimestamp(timestamp, tz=timezone.utc) instead.
    - To avoid the asymmetry between positive and negative floats, normalize/convert timestamps before calling this function: for example, convert floats to integer seconds deliberately, or use UTC-aware conversion functions depending on desired semantics.

