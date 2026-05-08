# `bundling.py`

## `src.exodus_bundler.bundling.bytes_to_int` · *function*

## Summary:
Converts a sequence of raw bytes (bytes-like object) into a non-negative integer according to the specified byte order ('big' or 'little').

## Description:
This utility interprets an ordered sequence of unsigned bytes as a single multi-byte integer. It:
- Unpacks each input byte as an unsigned 8-bit value, arranges those values into least-significant-first order and computes the integer by summing value * 256**index for each byte.
- Accepts both bytes and other bytes-like objects (e.g., bytearray) that are acceptable to the struct.unpack call.

Known callers within the codebase:
- No callers were discovered in the provided file snippet. (If this function is used elsewhere in the repository, those references were not part of the provided input.) Typical places this function would be called: binary parsing routines, header/metadata extraction, or whenever a variable-length byte sequence must be interpreted as a single integer.

Why this logic is extracted into its own function:
- Encapsulates the precise conversion semantics (including the non-obvious detail of how byte order is handled) so callers don't need to reimplement or repeat the byte-to-integer logic.
- Keeps binary-parsing code concise and centralizes handling of endianness, input validation implications, and consistent exception behavior.

## Args:
    bytes (bytes|bytearray|memoryview): The input byte sequence to convert. Must be a bytes-like object whose length is >= 1. Note: the parameter name shadows the built-in type name `bytes`.
    byteorder (str): One of 'big' or 'little' (default: 'big').
        - 'big' treats the first byte in the input as the most-significant byte.
        - 'little' treats the first byte in the input as the least-significant byte.

Interdependencies:
- The function requires a valid byteorder string; any other value will not be accepted and will result in an immediate KeyError from the internal mapping lookup.

## Returns:
    int: A non-negative integer representing the input byte sequence interpreted according to byteorder.
    - For a non-empty input, returns the exact integer computed as sum(byte_value * 256**i for i, byte_value in enumerate(bytes_in_least_significant_first_order)).
    - The result is 0 for an input consisting of a single zero byte (b'\x00'); larger for other byte sequences.
    - The function can return very large integers for long input sequences (no explicit size limit enforced by the function itself).

Examples of return values:
    - bytes_to_int(b'\x01\x02', byteorder='big') -> 258
    - bytes_to_int(b'\x01\x02', byteorder='little') -> 513

## Raises:
    KeyError:
        - Raised when byteorder is not one of 'big' or 'little' because the function indexes a small mapping with the provided value.
    struct.error (from struct.unpack):
        - May be raised if the struct.unpack call receives an invalid format string (for example, when the format becomes empty for an empty input), or if the provided object is not an acceptable buffer for struct.unpack.
        - In practice this covers cases such as empty input (len(bytes) == 0) or a malformed/non-bytes-like argument.
    TypeError (possible, from struct.unpack):
        - If the provided argument is of a type that struct.unpack rejects (e.g., None or an incompatible type), struct.unpack may raise a TypeError.

Notes on exceptions:
- The function does not explicitly raise these exceptions; they result from the dict lookup and struct.unpack behavior. Callers should handle these exceptions if inputs may be invalid.

## Constraints:
Preconditions:
    - The caller should pass a bytes-like object (bytes, bytearray, memoryview).
    - The byteorder argument must be exactly 'big' or 'little'.
    - The input length should be >= 1 to avoid struct/format-related errors.

Postconditions:
    - No mutation of the input occurs.
    - The return value is a Python int >= 0 that encodes the input bytes per the specified byteorder.
    - No I/O or global state is modified.

## Side Effects:
    - None. The function performs pure computation on its inputs and does not perform file, network, stdout/stderr, or global state side effects.

## Control Flow:
flowchart TD
    A[Start] --> B{byteorder in {'big','little'}?}
    B -- no --> C[KeyError raised]
    B -- yes --> D[Construct format string: endian + 'B'*len(bytes)]
    D --> E[Call struct.unpack(format, bytes)]
    E --> F{byteorder == 'big'?}
    F -- yes --> G[Reverse tuple of byte values]
    F -- no --> H[Keep tuple as-is]
    G --> I[Enumerate byte values with indices starting at 0]
    H --> I
    I --> J[Compute sum(byte * 256**index for each (index,byte))]
    J --> K[Return computed integer]
    E --> L[struct.error or TypeError may be raised for invalid inputs]

## Examples:
1) Typical usage (big-endian interpretation)
    - Input: b'\x01\x02'
    - Call: bytes_to_int(b'\x01\x02', byteorder='big')
    - Result: 258
    - Reason: bytes interpreted as 0x01 0x02 -> 1*256 + 2 = 258

2) Typical usage (little-endian interpretation)
    - Input: b'\x01\x02'
    - Call: bytes_to_int(b'\x01\x02', byteorder='little')
    - Result: 513
    - Reason: bytes interpreted as least-significant-first: 1 + 2*256 = 513

3) Error handling (invalid byteorder)
    - Call: bytes_to_int(b'\x00', byteorder='middle')
    - Behavior: raises KeyError due to invalid byteorder mapping

4) Error handling (empty input)
    - Call: bytes_to_int(b'', byteorder='big')
    - Behavior: struct.unpack or struct format construction results in struct.error (or an error raised by struct) — callers should catch struct.error if empty inputs are possible.

Implementation notes for reimplementers:
    - The function unpacks each byte as unsigned 8-bit values and then arranges them into least-significant-first order for the summation step. For 'big' byteorder the tuple returned by struct.unpack is reversed before enumeration; for 'little' it is left as returned.
    - Using arithmetic with 256**i intentionally makes each byte weight a power-of-256 according to its significance.
    - Avoid using an empty input; handle or check len(bytes) == 0 before calling the function if empty payloads are possible.

## `src.exodus_bundler.bundling.create_bundle` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.create_unpackaged_bundle` · *function*

*No documentation generated.*

## `src.exodus_bundler.bundling.detect_elf_binary` · *function*

## Summary:
Determine whether a filesystem path refers to an ELF-format file by opening the file, reading its first four bytes, and checking for the ELF magic header; returns True for ELF files and False otherwise.

## Description:
Known callers:
- No direct callers were discovered in the provided repository snapshot for this function.
- Typical usage context: called in file-inspection or bundling workflows to decide whether to run ELF-specific parsing, dependency detection, or to construct a binary launcher for a given file path.

Reason for extraction:
- Centralizes the tiny but semantically important check for ELF-format files (the standard ELF magic bytes). This isolates file-existence checking and the byte-level magic comparison so higher-level code can call a single, well-tested utility rather than duplicating the low-level logic.

## Args:
    filename (str | os.PathLike):
        - Path to the file to inspect. Accepts strings or objects implementing os.PathLike (e.g., pathlib.Path).
        - Must be a path on the local filesystem accessible to the process.
        - If a broken symlink is supplied, os.path.exists will return False and a MissingFileError will be raised; if a symlink points to a file, the target file is opened and inspected.

## Returns:
    bool:
        - True if the file is successfully opened and its first four bytes equal the ELF magic bytes (b'\x7fELF').
        - False if the file is opened successfully but its first four bytes differ (this includes text files, scripts, Windows PE binaries, or files smaller than 4 bytes).
        - The function never returns None.

## Raises:
    MissingFileError:
        - Raised when os.path.exists(filename) returns False (the path does not exist at the moment of the existence check).
        - Message produced: 'The "<filename>" file was not found.'

    FileNotFoundError:
        - May be raised (propagated) if the file existed during the os.path.exists check but is removed before the open() call (race condition), or if the open() call otherwise fails to find the file.

    PermissionError:
        - Propagated when the process lacks permission to open the file for reading.

    IsADirectoryError:
        - Propagated when the given path exists but refers to a directory; attempting to open it in binary mode raises this error.

    OSError:
        - Other low-level I/O errors raised by open() or read() will propagate unchanged.

Notes:
- The function explicitly raises MissingFileError only when os.path.exists returns False. Any I/O issues encountered during open/read are not caught and will surface to the caller.

## Constraints:
Preconditions:
    - The supplied filename must be a valid path-like object referring to a filesystem entry (or a symlink).
    - The calling process should have permission to read the target file if it exists.

Postconditions:
    - No persistent filesystem or global state is modified.
    - The file (if opened) is closed prior to returning.
    - The return value accurately reflects the ELF magic byte comparison at the time the file was read.

## Side Effects:
    - Opens the specified file in binary read mode ("rb") and reads up to 4 bytes.
    - No writes, no network calls, and no changes to global variables or external resources.
    - Minimal memory usage (only the bytes read are kept in memory).

## Race condition and caller guidance:
- There is a small race between the os.path.exists check and opening the file: the file could be deleted or changed after exists() returns True but before open() executes. In that case, open() will raise FileNotFoundError (or another OSError), which this function does not convert into MissingFileError. Callers should therefore handle both MissingFileError and FileNotFoundError/OSError if they need robust behavior.
- If an atomic check-and-open is required, consider attempting to open the file directly and handling FileNotFoundError instead of relying on os.path.exists externally before calling this function.

## Control Flow:
flowchart TD
    Start --> ExistsCheck{os.path.exists(filename)?}
    ExistsCheck -- No --> RaiseMissing[Raise MissingFileError]
    ExistsCheck -- Yes --> OpenFile[open(filename, 'rb')]
    OpenFile --> Read4[read(4) -> first_four_bytes]
    Read4 --> Compare{first_four_bytes == b'\x7fELF'}
    Compare -- True --> ReturnTrue[return True]
    Compare -- False --> ReturnFalse[return False]
    OpenFile -- open errors --> PropagateError[Propagate FileNotFoundError/PermissionError/IsADirectoryError/OSError]

## Examples:
Example 1 — typical usage with basic handling
path = '/usr/bin/ls'
try:
    if detect_elf_binary(path):
        # Proceed with ELF-specific processing (dependency detection, binary launcher construction, etc.)
        print('ELF binary detected')
    else:
        print('Not an ELF binary (script, PE, text, or too-small file)')
except MissingFileError as e:
    # Path was not present at the moment of the existence check
    print('Missing file:', e)
except FileNotFoundError:
    # The file was removed between the existence check and open(); treat similarly to MissingFileError
    print('File disappeared before it could be read')
except PermissionError:
    print('Permission denied reading file')
except OSError as e:
    print('I/O error while checking file:', e)

Example 2 — when you already have bytes in memory
# If you already hold the file bytes in memory (data: bytes), avoid filesystem calls:
is_elf = (len(data) >= 4 and data[:4] == b'\x7fELF')
# This is faster and avoids race conditions inherent in filesystem operations.

Notes:
- This function only detects ELF format via the standard magic header. Other executable formats (e.g., PE/COFF on Windows) will not be recognized as ELF.
- Files smaller than 4 bytes return False because the read result cannot equal the 4-byte ELF signature.

## `src.exodus_bundler.bundling.parse_dependencies_from_ldd_output` · *function*

## Summary:
Parses stdout/stderr text from an ldd run and returns a list of filesystem paths to the shared libraries referenced in that output.

## Description:
This function accepts raw ldd output (as a single string or an iterable of lines) and extracts absolute filesystem paths that appear in the typical ldd output patterns. It is intended to be used after running ldd (or a similar tool) on a binary to collect the concrete library file paths that the binary depends on.

Known callers within the codebase:
- No explicit callers are visible in this file excerpt. Typical callers are functions that execute ldd (or other dynamic linker diagnostics) and pass the captured output (stdout and/or stderr) to this parser.

Why this logic is extracted:
- Parsing ldd output requires a small but focused set of regex rules and filtering semantics (e.g., skipping lines where the resolved target is ldd itself). Extracting it into a dedicated function keeps the ldd execution logic (running subprocesses, capturing output) separate from parsing and makes the behavior reusable and testable in isolation.

## Args:
    content (str | Iterable[str]):
        - If a str is provided, it is split on newline characters to form the lines to parse.
        - If an iterable of strings (e.g., list[str]) is provided, each element is treated as one line.
        - Each line is expected to be a textual line from ldd output; trailing whitespace is allowed.
        - Interdependencies: The function only handles text lines; do not pass bytes or binary objects (they will not be split and will likely fail regex matching).

## Returns:
    list[str]:
        - A list of extracted filesystem paths. Each item is the substring captured by the regex that starts with a forward slash (an absolute path).
        - Ordering: paths are returned in the same order they are discovered while iterating through the provided lines.
        - Duplicates: the function does not deduplicate; duplicate paths in the input lead to duplicate entries in the result.
        - If no matching paths are found, an empty list is returned.

## Raises:
    - This function does not explicitly raise any exceptions on its own.
    - However, if the caller passes non-textual input types that break upstream expectations (for example, bytes where str is expected), Python operations (e.g., regex) may raise TypeError. The function itself contains no try/except and performs no validation beyond a type-check for str.

## Constraints:
Preconditions:
    - The caller should ensure the input is either a str or an iterable of strings representing lines from ldd output.
    - Lines that are not textual or that contain embedded binary data will not be parsed correctly.

Postconditions:
    - Return value is a list of zero or more absolute file path strings (each path begins with '/').
    - No global state is modified and no I/O is performed by this function.

## Side Effects:
    - None. The function performs pure in-memory parsing and does not perform I/O, modify global variables, or call external services.

## Control Flow:
flowchart TD
    A[Start] --> B{Is content a str?}
    B -- Yes --> C[Split content on '\n' into lines]
    B -- No  --> D[Treat content as iterable of lines]
    C --> E[Initialize dependencies = []]
    D --> E
    E --> F[For each line in lines]
    F --> G{Line matches '^\s*(/.*?)\s*=>\s*ldd\s*\(' ?}
    G -- True --> H[skip line (continue)]
    G -- False --> I[Try match '=>\s*(/.*?)\s*\(']
    I --> J{match found?}
    J -- True --> K[append captured path to dependencies]
    J -- False --> L[Try match '\s*(/.*?)\s*\(']
    L --> M{match found?}
    M -- True --> K
    M -- False --> N[do nothing]
    K --> O[continue loop]
    N --> O
    O --> P[After loop return dependencies]

## Examples:
Example 1 — typical ldd output (happy path)
Input (as a single string or list of lines):
    linux-vdso.so.1 (0x00007ffd...)
    libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f...)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f...)
    /lib64/ld-linux-x86-64.so.2 (0x00007f...)

Return value:
    ['/lib/x86_64-linux-gnu/libm.so.6',
     '/lib/x86_64-linux-gnu/libc.so.6',
     '/lib64/ld-linux-x86-64.so.2']

Example 2 — skip lines pointing to ldd itself
Input:
    /usr/bin/ldd => ldd (0x00007f...)
    libfoo.so => /usr/lib/libfoo.so (0x00007f...)

Return value:
    ['/usr/lib/libfoo.so']

Example 3 — no matches
Input:
    some unrelated text
    another line with no path

Return value:
    []

Notes:
    - The function intentionally treats entries like "linux-vdso.so.1 (0x...)" which lack leading '/' as non-paths unless another pattern captures a leading '/'.
    - If the caller needs unique paths, they should deduplicate the returned list (for example, with an ordered set) after calling this function.

## `src.exodus_bundler.bundling.resolve_binary` · *function*

## Summary:
Resolve a binary name or path to a normalized absolute filesystem path, searching the current PATH when a non-existent path is provided, and raise a MissingFileError if the binary cannot be found.

## Description:
This function takes a user-supplied binary identifier (either a path or a program name) and returns an absolute, normalized path that points to an existing filesystem entry. It first treats the input as a path; if that path exists it is returned. If it does not exist, the function searches each directory listed in the PATH environment variable (or a built-in default if PATH is unset) and returns the first matching absolute path found. If no match is found, it raises MissingFileError.

Known callers:
- No direct callers were discovered by the repository scan performed during documentation generation. Conceptually, this helper is intended to be used anywhere the bundler needs to translate a program name or user-specified path into a concrete existing executable path (for example, when constructing launchers or detecting toolchain binaries).

Why this is a separate function:
- Centralizes and documents the exact policy for resolving program names vs. paths (priority, PATH lookup order, normalization).
- Encapsulates error handling (MissingFileError) so calling code can rely on a consistent exception type rather than duplicating lookup logic.
- Keeps filesystem and environment dependency logic isolated for easier testing and potential future platform-specific changes.

## Args:
    binary (str or os.PathLike): Path-like identifier for the binary. Allowed values:
        - An absolute or relative filesystem path (e.g., '/usr/bin/env', './myprog').
        - A bare program name to search for in PATH (e.g., 'bash', 'python3').
    Notes:
        - If an empty string is supplied, os.path.abspath('') resolves to the current working directory; because that directory typically exists, the function will return the absolute path to the current working directory.
        - The function does not accept None; passing None will raise a TypeError from underlying os.path functions.

## Returns:
    str: A normalized absolute path (os.path.abspath then os.path.normpath) that points to an existing filesystem entry.
    Possible outcomes:
        - Returns the normalized absolute form of the provided path when that path exists.
        - Returns the normalized absolute path to the first occurrence of the binary found by searching directories in PATH.
        - Does not return None — when no existing path can be determined the function raises MissingFileError instead.

## Raises:
    MissingFileError:
        - Raised when the binary cannot be found: the provided path does not exist and no matching entry is found in any directory yielded by splitting the PATH environment variable (or the function's default PATH string).
    Other propagated exceptions:
        - TypeError or ValueError may propagate from underlying os.path/os operations if an invalid type is passed (e.g., None or unsupported path-like object). These are not explicitly raised by this function but are possible.

## Constraints:
    Preconditions:
        - The caller should pass a path-like string (str or os.PathLike). Supplying non-path-like types may cause underlying functions to raise.
        - The runtime must allow reading environment variables and performing filesystem existence checks (os.getenv, os.path.exists).
    Postconditions:
        - On successful return, the returned string is an absolute, normalized path and refers to an existing filesystem entry (os.path.exists(return_value) is True).

## Side Effects:
    - Reads the PATH environment variable via os.getenv.
    - Performs filesystem existence checks (os.path.exists), which may perform metadata/stat system calls. No files are created, modified, or deleted.
    - No network I/O, no writes to stdout/stderr, and no global state mutation are performed.

## Control Flow:
flowchart TD
    Start --> ComputeAbs["Compute absolute_binary_path = normpath(abspath(binary))"]
    ComputeAbs --> ExistsCheck{"os.path.exists(absolute_binary_path)?"}
    ExistsCheck -- Yes --> ReturnAbs["Return absolute_binary_path"]
    ExistsCheck -- No --> ForEachPath["For each path in os.getenv('PATH','/bin/:/usr/bin/').split(os.pathsep)"]
    ForEachPath --> JoinPath["Compute candidate = normpath(abspath(join(path, binary)))"]
    JoinPath --> CandidateExists{"os.path.exists(candidate)?"}
    CandidateExists -- Yes --> ReturnCandidate["Return candidate (break loop)"]
    CandidateExists -- No --> NextPath["Continue to next PATH entry"]
    NextPath --> ForEachPath
    ForEachPath --> EndLoop{"No more PATH entries?"}
    EndLoop -- Yes --> RaiseError["Raise MissingFileError('The \"%s\" binary could not be found in $PATH.' % binary)"]
    ReturnAbs --> End
    ReturnCandidate --> End
    RaiseError --> End

## Examples / Usage notes:
- Typical successful resolution of a bare program name on a Unix system:
    - Input: 'ls'
    - Behavior: If '/bin/ls' exists and '/bin' is in PATH, the function returns '/bin/ls'.
- Typical successful resolution of an explicit path:
    - Input: './tools/mytool' (relative path)
    - Behavior: If the normalized absolute path exists on disk, it is returned immediately without consulting PATH.
- Handling the not-found case:
    - If neither the provided path nor any PATH directory contains the binary, the function raises MissingFileError and callers should catch this explicitly if they want to provide an alternative behavior or a clearer error message to users.

Platform note:
- If the PATH environment variable is unset, the function falls back to the literal string '/bin/:/usr/bin/' and splits that string on os.pathsep. On non-POSIX platforms where os.pathsep is not ':', that literal default will not be split into two entries as intended for POSIX; callers on such platforms should ensure PATH is set appropriately.

## `src.exodus_bundler.bundling.resolve_file_path` · *function*

## Summary:
Validate and normalize a filesystem path to an existing regular file, optionally resolving a program name via PATH first, and return its normalized absolute path.

## Description:
This utility ensures a caller-provided path-like identifier refers to an existing file (not a directory) and returns a stable absolute form suitable for subsequent bundling or launcher construction.

Known callers:
- No direct callers were discovered by the automated repository scan. Conceptual call sites include code that needs to accept either a user-supplied file path or a program name and must obtain a canonical existing file path before performing bundling, dependency detection, or launcher construction (for example, earlier stages of the bundling pipeline that prepare binaries or scripts for inclusion).

Typical trigger/context:
- Called during bundling preparation when the system must validate that an input (script, binary, or file) exists and is not a directory. When search_environment_path is True, the function is used to accept bare program names (e.g., "bash") and resolve them to concrete paths via PATH lookup before validation.

Why this is a separate function:
- Centralizes path validation (existence and file-vs-directory checks) and normalization so callers do not duplicate error messages or path normalization logic.
- Encapsulates the optional policy of resolving bare program names via the environment (delegating to resolve_binary) so callers can request either direct path validation or program-name resolution with a boolean flag.

## Args:
    path (str or os.PathLike):
        - A path-like identifier for the target file, or (when search_environment_path is True) a bare program name.
        - Must not be None. Passing None or an unsupported type may raise a TypeError from underlying os.path functions.
    search_environment_path (bool, optional):
        - If True, treat the incoming path as a program identifier and call resolve_binary(path) to attempt to locate it on the current PATH before validation.
        - Default: False

Interdependencies:
    - When search_environment_path is True, resolve_binary may raise MissingFileError (or other exceptions) which are propagated to the caller. The returned value from resolve_binary becomes the path validated by this function.

## Returns:
    str: A normalized absolute filesystem path that satisfies:
        - os.path.exists(return_value) is True
        - os.path.isdir(return_value) is False
        - The value is produced by os.path.abspath followed by os.path.normpath (i.e., normalized absolute form).
    Possible outcomes:
        - A normalized absolute path to an existing file when validation succeeds.
        - The function never returns None; on failure it raises one of the documented exceptions.

## Raises:
    MissingFileError:
        - Raised when the final candidate path does not exist on the filesystem. This includes the case where search_environment_path is False and the provided path is not found, or when search_environment_path is True and resolve_binary either returns a non-existent path or itself raises MissingFileError.
    UnexpectedDirectoryError:
        - Raised when the candidate path exists but is a directory rather than a file.

    Notes about propagated exceptions:
        - If search_environment_path is True, resolve_binary may raise MissingFileError or propagate TypeError/ValueError for malformed inputs; those propagate here.
        - Underlying os.path functions may raise TypeError when passed non-path-like types; such exceptions are not caught and will propagate.

## Constraints:
Preconditions:
    - The caller should supply a path-like string (str or os.PathLike). Supplying None or a non-path-like object can produce TypeError from os.path functions.
    - The environment and filesystem must be accessible for os.path.exists and os.path.isdir to perform checks.
Postconditions:
    - On successful return, the returned path is an absolute, normalized path that exists and is a file (not a directory).
    - No symlink resolution beyond what abspath provides is guaranteed; the function does not call os.path.realpath and therefore may return a path that is itself a symlink.

## Side Effects:
    - Performs filesystem metadata reads (os.path.exists and os.path.isdir), which may perform stat system calls.
    - If search_environment_path is True, resolve_binary may read environment variables (PATH) and perform additional filesystem checks.
    - No file creation, modification, deletion, network I/O, or global state mutation occurs.

## Control Flow:
flowchart TD
    Start --> CheckFlag{"search_environment_path == True?"}
    CheckFlag -- Yes --> CallResolveBinary["path = resolve_binary(path)"]
    CallResolveBinary --> ExistsCheck{"os.path.exists(path)?"}
    CheckFlag -- No --> ExistsCheck
    ExistsCheck -- No --> RaiseMissing["Raise MissingFileError('The \"%s\" file was not found.' % path)"]
    ExistsCheck -- Yes --> IsDirCheck{"os.path.isdir(path)?"}
    IsDirCheck -- Yes --> RaiseDir["Raise UnexpectedDirectoryError('\"%s\" is a directory, not a file.' % path)"]
    IsDirCheck -- No --> Normalize["Return os.path.normpath(os.path.abspath(path))"]
    RaiseMissing --> End
    RaiseDir --> End
    Normalize --> End

## Examples / Usage notes:
- Validate an explicit file path (happy path):
    - Caller provides a concrete file path for an included resource. Call with search_environment_path=False (default). If the file exists and is not a directory, the function returns its normalized absolute path for subsequent packaging.

- Resolve a program name via PATH and validate:
    - Caller provides "bash" and sets search_environment_path=True. The function delegates to resolve_binary to find an absolute path for "bash" and then validates that result exists and is not a directory, returning the normalized absolute path.

- Error handling pattern:
    - Callers that accept user input should catch MissingFileError to present a friendly "file not found" message, and catch UnexpectedDirectoryError to indicate a directory was supplied where a file was required. If search_environment_path=True, callers may also want to catch exceptions propagated from resolve_binary to present PATH-specific guidance.

- Practical notes:
    - This function does not ensure the returned path is executable. If executability must be enforced, callers should perform an additional check (e.g., os.access(path, os.X_OK) or inspect file mode bits).
    - The function uses abspath + normpath rather than realpath, so returned paths may still contain symlinks.

## `src.exodus_bundler.bundling.run_ldd` · *function*

## Summary:
Run the system ldd command against a candidate binary after verifying the file is an ELF executable; return the combined stdout and stderr output as a list of lines.

## Description:
- Known callers:
    - No direct callers were discovered in the provided repository snapshot.
    - Typical usage context: used during bundling or dependency-detection stages when the bundler needs to inspect a binary's shared-library dependencies by invoking the platform ldd tool. It is expected to be called when the bundling pipeline reaches the phase that collects runtime library dependencies for ELF binaries.

- Why this logic is extracted:
    - Encapsulates validation (ensure the file is an ELF) and the platform interaction (spawning ldd and capturing its output) in one place so callers do not need to duplicate subprocess handling, decoding, or ELF checks. This separation keeps error mapping (InvalidElfBinaryError) and ldd invocation consistent across the codebase.

## Args:
    ldd (str):
        - Path or program name for the ldd tool to execute (e.g., '/usr/bin/ldd' or 'ldd').
        - Must be a string; if ldd is not present on the system or the path is incorrect, subprocess invocation will raise FileNotFoundError/OSError.
    binary (str or os.PathLike):
        - A path-like identifier for the target program to inspect. May be an absolute path, relative path, or bare program name.
        - The function calls resolve_binary(binary) before invoking detect_elf_binary; resolve_binary either returns an absolute, normalized path to an existing file or raises MissingFileError if it cannot find the binary.
        - Note: the resolved path is used only for the ELF validation check; the original binary argument (as passed in) is what is given to the ldd subprocess invocation.

## Returns:
    list[str]:
        - A flat list of strings representing the ldd subprocess output, with each element corresponding to a line. The list is constructed by:
            1) decoding stdout with UTF-8 and splitting on '\n'
            2) decoding stderr with UTF-8 and splitting on '\n'
            3) returning stdout_lines + stderr_lines (stdout lines first, then stderr lines)
        - Possible return forms and edge cases:
            - If ldd prints nothing to stdout/stderr, the list may be [''] + [''] (two lists with a single empty string each) or a list containing empty strings depending on how split() behaves for empty bytes; callers should filter empty strings if desired.
            - If stdout or stderr contains trailing newline(s) the final list elements may be empty strings.
            - If the subprocess outputs non-UTF-8 bytes, decoding will raise UnicodeDecodeError (see Raises).
            - The function never returns None.

## Raises:
    InvalidElfBinaryError:
        - Raised explicitly when detect_elf_binary(resolve_binary(binary)) returns False, i.e., the resolved filesystem path does not appear to be an ELF binary.
        - Message produced by this function: 'The "<binary>" file is not a binary ELF file.' (binary is the original binary arg string)

    MissingFileError:
        - May be raised by resolve_binary(binary) if the provided binary cannot be located on disk (resolve_binary searches the provided path and then PATH).
        - The exact message and conditions are managed by resolve_binary.

    FileNotFoundError / OSError:
        - May be raised by Popen() if the ldd program cannot be found or cannot be executed, or if attempting to invoke the binary fails at the OS level.
        - May also propagate from resolve_binary or detect_elf_binary in race conditions (file disappears between checks).

    UnicodeDecodeError:
        - Raised when decoding stdout or stderr from bytes to UTF-8 fails because the subprocess emitted bytes that are not valid UTF-8 sequences.

    Other subprocess-related exceptions:
        - Popen may raise other OSError variants depending on the platform and environment (e.g., permission errors when launching ldd). These errors are propagated.

## Constraints:
- Preconditions:
    - The caller must supply ldd as a path or executable name and ensure the execution environment permits launching external commands.
    - The binary must be a filesystem entry or a name resolvable by resolve_binary; resolve_binary will perform existence checks and can raise MissingFileError.
    - The process must have permission to read the binary file (detect_elf_binary will open the resolved file).

- Postconditions:
    - If the function returns normally, the returned list contains decoded lines from ldd's stdout followed by decoded lines from ldd's stderr.
    - No files or global state are modified by this function (only a subprocess is spawned and its outputs are read).

## Side Effects:
    - Spawns an external process (ldd) using subprocess.Popen and waits for it to complete via communicate(). This can:
        - Consume CPU/time while ldd runs.
        - Block the calling thread until ldd finishes.
    - Reads data from the ldd process's stdout and stderr (captured; nothing is written to the parent's stdout/stderr).
    - Opens and reads the target binary indirectly via detect_elf_binary(resolve_binary(binary)) (read-only).
    - No files are written, no network I/O is performed, and no global variables are modified.

## Control Flow:
flowchart TD
    Start --> Resolve[Call resolve_binary(binary)]
    Resolve --> ResolveSuccess{exists?}
    ResolveSuccess -- No --> RaiseMissing[Raise MissingFileError]
    ResolveSuccess -- Yes --> DetectELF[Call detect_elf_binary(resolved_path)]
    DetectELF --> IsELF{is ELF?}
    IsELF -- No --> RaiseInvalid[Raise InvalidElfBinaryError]
    IsELF -- Yes --> Spawn[Call Popen([ldd, binary], stdout=PIPE, stderr=PIPE)]
    Spawn --> Communicate[proc.communicate() -> (stdout_bytes, stderr_bytes)]
    Communicate --> DecodeOut[stdout_bytes.decode('utf-8') -> str]
    Communicate --> DecodeErr[stderr_bytes.decode('utf-8') -> str]
    DecodeOut --> SplitOut[split('\\n') -> stdout_lines]
    DecodeErr --> SplitErr[split('\\n') -> stderr_lines]
    SplitOut --> Concat[return stdout_lines + stderr_lines]
    RaiseMissing --> End
    RaiseInvalid --> End

## Examples:
Example 1 — typical usage with error handling
try:
    lines = run_ldd('ldd', '/usr/bin/ls')
    # Filter out blank lines and inspect dependencies
    deps = [ln for ln in lines if ln.strip()]
    for line in deps:
        print(line)
except MissingFileError:
    print('Binary could not be found (resolve_binary failed).')
except InvalidElfBinaryError:
    print('Target file is not an ELF binary; skipping ldd.')
except FileNotFoundError:
    print('ldd executable not found or could not be launched.')
except UnicodeDecodeError:
    print('ldd output contained bytes that could not be decoded as UTF-8.')

Example 2 — handling ldd output robustly
lines = run_ldd('/usr/bin/ldd', './my_program')
# Partition output into stdout and stderr if needed
# The contract is stdout_lines first, then stderr_lines.
# If you need to preserve separation, re-run ldd using a direct subprocess call instead.

Notes and implementation hints for reimplementation:
- Validate the binary by resolving it with resolve_binary() and checking ELF magic using detect_elf_binary(). These helpers already define filesystem, PATH lookup, and ELF magic behavior.
- Use subprocess.Popen with stdout=PIPE and stderr=PIPE, call communicate(), decode both byte strings with 'utf-8', then split on '\n' and concatenate the resulting lists.
- Be intentional about error propagation: do not catch OSError/FileNotFoundError/UnicodeDecodeError unless you intend to convert them to library-specific exceptions.

## `src.exodus_bundler.bundling.stored_property` · *class*

## Summary:
A lightweight non-data descriptor that computes a value on first access, caches it on the instance, and thereafter yields the cached value.

## Description:
This descriptor is intended to be applied to an instance method (a callable that expects the instance as its sole explicit argument) to produce a lazily-computed, memoized attribute. On the first attribute access for a given instance, the wrapped callable is invoked with the instance; its result is stored in the instance's attribute dictionary under the callable's name and that stored result is provided on subsequent accesses. The descriptor itself is not invoked again for that instance once the cached value exists.

Typical usage scenarios:
- Use on an expensive-to-compute property that should be computed at most once per instance (e.g., expensive initialization, derived metadata).
- Use when it is acceptable for the computed value to be persisted in the instance's attribute dictionary and possibly overwritten by assignment.

Known callers/factories:
- Typically created implicitly via use as a decorator on an instance method definition.
- There are no special factory functions; construction requires providing the callable to be wrapped.

Motivation and responsibility boundary:
- Provides a minimal cached-property abstraction without producing a data descriptor; it relies on the instance attribute dictionary having precedence over the descriptor for subsequent accesses.
- It does not implement any explicit cache invalidation, locking, or descriptor-set behavior; those responsibilities lie outside this abstraction.

## State:
Attributes (per-descriptor instance)
- __doc__: str or None
  - Initialized from the wrapped callable's documentation string when the descriptor is created.
  - May be None if the wrapped callable has no docstring.
- function: callable
  - The wrapped callable used to compute the value.
  - Expected signature: function(instance) -> any value. No runtime enforcement is applied.

Instance-state produced by this descriptor
- The instance attribute dict (instance.__dict__) will contain an entry keyed by the wrapped callable's __name__ after the first access. The stored value is exactly what the callable produced.

Valid ranges / invariants
- The function attribute must be callable. The descriptor does not validate types at construction time; failures will manifest at access time.
- Invariant after first successful access: instance.__dict__[function.__name__] == computed value
- The descriptor is a non-data descriptor (no set or delete methods); therefore, explicit assignment to the same attribute name on the instance will shadow the descriptor.

Constraints and interactions
- The instance must provide an attribute dictionary (instance.__dict__). If the instance type lacks an attribute dict (for example, uses restricted slots without a dict), the descriptor will raise an attribute-related exception when invoked.
- The descriptor relies on the callable's __name__ to choose the cache key. If the callable's name does not match the attribute name it is bound to, the cache key will be the callable name, which may be surprising.

## Lifecycle:
Creation
- Instantiate by providing a callable: stored_property(callable). The most common pattern is using the descriptor as a decorator on an instance method.

Usage (typical sequence)
1. Define a user type with a method wrapped by this descriptor.
2. Instantiate that user type (instance).
3. Access the attribute on the instance:
   - If instance.__dict__ lacks the cache key, the descriptor's logic invokes the wrapped callable(function) with the instance, stores the computed value in instance.__dict__[function.__name__], and yields that value.
   - On subsequent attribute accesses, Python finds the cached value in instance.__dict__ and returns it directly without invoking the descriptor.
4. Optionally, directly assign to the same attribute name on the instance to replace the cached value; this assignment will shadow the descriptor.

Destruction / cleanup
- The descriptor has no cleanup responsibilities. No context-management or explicit close is required.
- If the cached value holds external resources, the owner of that value must manage their cleanup.

Sequencing constraints
- There is no required call order beyond: construction -> first access -> subsequent accesses. No explicit invalidation or reset is provided by the descriptor.

Threading and concurrency
- The descriptor is not thread-safe. Concurrent first accesses from multiple threads may result in the wrapped callable being invoked multiple times; no locking is provided.

## Method Map:
graph LR
  A[Create descriptor: stored_property(function)] --> B[Assigned to attribute on a user type]
  B --> C[Instance created]
  C --> D[First attribute access on instance]
  D --> E[Descriptor.__get__ invoked -> calls wrapped callable with instance]
  E --> F[Store result in instance.__dict__[function.__name__]]
  F --> G[Subsequent accesses read instance.__dict__[function.__name__] directly]

## Raises:
Exceptions that may be raised by operations involving this descriptor:
- AttributeError
  - Trigger: Accessing the descriptor with instance set to None (access via the owner type) or the instance lacks an attribute dictionary (e.g., restricted slots without a dict) will produce an attribute-related error when the descriptor attempts to use instance.__dict__.
- TypeError
  - Trigger: If the wrapped callable is not callable or its invocation signature is incompatible with being called with the instance, a TypeError from Python will propagate.
- Any exception raised by the wrapped callable
  - Trigger: If the wrapped callable raises while computing the value, that exception propagates to the caller; no caching is performed for that instance in that case.

Notes on exception behavior:
- The descriptor does not intercept or translate exceptions from the wrapped callable. If the wrapped callable raises, the instance.__dict__ will not receive a cached entry for the key, leaving the descriptor to attempt computation again on next access.

## Example:
- Setup:
  - Create a user-defined type that exposes a method wrapped by stored_property (used as a decorator).
  - Instantiate the user-defined type as instance.

- Typical use:
  - Access the attribute on instance for the first time:
    - The wrapped callable is invoked with instance and the resulting value is stored in instance.__dict__ under the callable's name.
  - Access the attribute again:
    - The cached value in instance.__dict__ is returned directly; the wrapped callable is not invoked again.
  - Replace the cached value:
    - Assign a new value to the same attribute name on instance to shadow the descriptor and change the stored result.

- Edge-case examples (described behavior, not code):
  - If instance has no attribute dictionary, first access will raise an attribute-related exception.
  - If the wrapped callable raises an error during computation, that error propagates and no cache entry is created.
  - Concurrent first accesses may compute the value multiple times due to lack of synchronization.

### `src.exodus_bundler.bundling.stored_property.__init__` · *method*

## Summary:
Sets up the descriptor by copying the wrapped callable reference onto the descriptor and mirroring the callable's docstring onto the descriptor object, preparing it for later lazy evaluation.

## Description:
Called when the stored_property descriptor is constructed — typically at class-definition time when the decorator is applied to a method. This constructor performs two minimal initialization steps required by the descriptor semantics:
- Reads the wrapped callable's __doc__ and assigns that value to the descriptor's own __doc__, so the descriptor exposes the same documentation as the wrapped callable.
- Stores the provided callable on self.function for later invocation by the descriptor's __get__ method.

This separation places one-time, creation-time work in __init__ (descriptor identity and metadata) and keeps run-time access and caching logic in the descriptor protocol methods (e.g., __get__), improving clarity and avoiding repeated work on every attribute access.

Known callers and lifecycle stage:
- Invoked when using the descriptor as a decorator on an instance method (e.g., @stored_property above a method). This occurs while the class body is being executed.
- No runtime factory functions; call sites directly pass the callable to stored_property(...).

## Args:
    function (object): The object provided to the constructor; intended to be a callable (an instance method that accepts the instance as its first argument).
        - Typical/expected: a function or function-like object with a __doc__ attribute and a __name__ attribute used later by the descriptor. The constructor does not enforce callability.

## Returns:
    None: As with all __init__ methods, this constructor returns None and only mutates the newly-created descriptor object.

## Raises:
    - Under normal circumstances, this constructor does not raise: getattr(function, '__doc__') returns None if the wrapped object has no docstring.
    - If the provided object implements custom attribute accessors (e.g., __getattribute__ or __getattr__) that raise exceptions when accessing '__doc__', those exceptions will propagate unchanged from getattr. Examples include AttributeError or other user-defined exceptions raised by the object's attribute logic. The constructor itself does not catch or translate such exceptions.

## State Changes:
Attributes READ:
    - function.__doc__ is read via getattr(function, '__doc__').

Attributes WRITTEN:
    - self.__doc__ is set to the value returned by getattr(function, '__doc__') (string or None).
    - self.function is set to the provided function object.

## Constraints:
Preconditions:
    - The caller must supply the 'function' parameter. Typical operation assumes 'function' is a callable intended to be invoked later with an instance.
    - The descriptor's proper caching behavior assumes the descriptor is assigned to a class attribute whose name matches function.__name__ (convention used by the stored_property implementation); this is a usage convention, not enforced here.

Postconditions:
    - After successful completion, self.function references the provided object, and self.__doc__ matches the wrapped object's docstring (possibly None). The descriptor is prepared for subsequent __get__-time lazy computation and caching.

## Side Effects:
    - No I/O or external interactions occur.
    - Only the descriptor object's attributes (self.__doc__ and self.function) are modified. The provided function object is not mutated.

### `src.exodus_bundler.bundling.stored_property.__get__` · *method*

## Summary:
Compute and cache a property's value on first access by calling the wrapped function and storing the result in the instance's __dict__, then return that value.

## Description:
This method implements the descriptor protocol's __get__ for a cached (stored) property. When an attribute decorated with this descriptor is accessed on an instance, this method:
- Calls the wrapped function with the instance to produce the value.
- Stores the produced value in instance.__dict__ under the wrapped function's name (caching).
- Returns the stored value.

Known callers and call contexts:
- Invoked automatically by Python when code accesses the descriptor-decorated attribute on an object instance (e.g., some_instance.property_name).
- Typical lifecycle: first access to the attribute during runtime triggers computation and caching; subsequent accesses return the cached value from instance.__dict__ without calling the wrapped function again.
- It is not intended to be called directly by user code; Python calls it as part of attribute lookup.

Rationale for being a separate method:
- Encapsulates the caching behavior (compute-once and store) in a reusable descriptor.
- Keeps decorated functions focused on computing the value while centralizing caching semantics here rather than in each consumer.

## Args:
    self: stored_property
        The descriptor object that holds a reference to the wrapped function (self.function).
    instance: object | None
        The object instance on which the attribute is being accessed. If None (attribute accessed on the class), this implementation will not handle that case and will raise an AttributeError when attempting to access instance.__dict__.
    type: type | None
        The owner class (passed by the descriptor protocol). This implementation does not use this parameter.

## Returns:
    Any
        The value returned by calling self.function(instance). After the call, the same value is stored in instance.__dict__[self.function.__name__] and subsequent attribute accesses will return that cached value.

## Raises:
    AttributeError
        If instance is None (i.e., the attribute is accessed on the class rather than an instance), the code attempts to access instance.__dict__ and this raises "'NoneType' object has no attribute '__dict__'".
    Any exception raised by the wrapped function (self.function):
        Exceptions raised while computing the value propagate unchanged; they are not caught here.
    AttributeError or TypeError
        If the instance lacks a writable __dict__ (for example, instances of classes with __slots__ and no __dict__), or if self.function is not callable as expected, attribute or type errors may occur when accessing or assigning into instance.__dict__ or when calling the function.

## State Changes:
Attributes READ:
    - self.function (the callable used to compute the value)
    - self.function.__name__ (the key name used in instance.__dict__)

Attributes WRITTEN:
    - instance.__dict__[self.function.__name__] is assigned the computed result.

## Constraints:
Preconditions:
    - instance must be a live object instance with a writable __dict__ attribute (i.e., instance.__dict__ must exist and be a mutable mapping).
    - self.function must be a callable that accepts the instance as its sole (first) positional argument.
    - The caller must expect that calling the wrapped function may have side effects or raise exceptions; those will propagate.

Postconditions:
    - After a successful call, instance.__dict__ contains an entry with key self.function.__name__ whose value is the result returned by self.function(instance).
    - Subsequent attribute accesses for the same attribute on that instance will retrieve the cached value directly from instance.__dict__, and the wrapped function will not be called again for that instance unless the entry is removed or replaced.

## Side Effects:
    - Calls the wrapped function self.function(instance), which may perform arbitrary side effects (I/O, mutation of instance, external calls).
    - Mutates the instance by inserting a new key-value pair into instance.__dict__.
    - No I/O or external service calls are performed by this method itself beyond what the wrapped function performs.

## `src.exodus_bundler.bundling.Elf` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.__init__` · *method*

*No documentation generated.*

### `src.exodus_bundler.bundling.Elf.__eq__` · *method*

## Summary:
Defines equality between this object and another by checking the other object is an Elf and (due to a bug in the current implementation) always comparing this object's path to itself; therefore it currently returns True for any other Elf instance regardless of path.

## Description:
This method is invoked whenever Python evaluates equality between two objects using the '==' operator — for example, in explicit comparisons, when checking membership in containers that call equality (such as list.index or when comparing items), and during set/dict operations if equality is used (note: Python uses both __hash__ and __eq__ for set/dict membership). There are no direct callers inside this module that explicitly call __eq__; it is invoked implicitly by the interpreter when needed.

This logic is implemented as a dedicated method because overriding __eq__ is the standard Python mechanism to define semantic equality for instances of a custom class. Defining equality here centralizes the comparison semantics for Elf objects so they can be used reliably in collections and comparison operations.

Implementation note (current vs intended):
- Current (literal) behavior in the source code: returns True iff other is an instance of Elf (because the method checks isinstance(other, Elf) and self.path == self.path, and the latter is always True).
- Intended/correct behavior: return True iff other is an Elf and the filesystem path values are equal (i.e., compare self.path to other.path). Reimplementers should use the latter to preserve consistency with __hash__ (which hashes self.path).

## Args:
    self: instance of Elf (must have been initialized; __init__ ensures self.path exists)
    other (any): object to compare against; may be any type

## Returns:
    bool: 
        - True when other is an instance of Elf and (in the current implementation) self.path == self.path (effectively: other is an Elf).
        - False otherwise.
    Edge cases:
        - When other is None or of a different type, returns False.
        - When other is an Elf subclass instance, isinstance(other, Elf) is True, so current implementation returns True even if other.path differs.
        - No exceptions are raised by this method.

## Raises:
    None. This method does not raise exceptions for any inputs. (It assumes self.path exists because Elf.__init__ ensures it.)

## State Changes:
    Attributes READ:
        - self.path
    Attributes WRITTEN:
        - None (no mutation of self or other)

## Constraints:
    Preconditions:
        - self must be a fully-initialized Elf instance with a valid self.path attribute (ensured by Elf.__init__).
        - other may be any object; the method handles non-Elf values by returning False.
    Postconditions:
        - No changes to self or other are made.
        - A boolean result is returned. If reimplemented correctly to compare paths, __eq__ should be consistent with __hash__ (which hashes self.path).

## Side Effects:
    - None. The method performs no I/O, no external calls, and mutates no external objects.

## Notes for correct reimplementation:
    - To make equality semantics meaningful and consistent with the class's __hash__, implement __eq__ to compare the two objects' path attributes (e.g., return isinstance(other, Elf) and self.path == other.path). This ensures two Elf instances referring to the same filesystem path are equal and that equality aligns with the value used by __hash__.
    - Maintain that __eq__ returns False for non-Elf objects to avoid spurious equality with unrelated types.
    - Consider also supporting comparisons with subclasses intentionally (isinstance check) or restricting to the exact class (type(...) is Elf) depending on desired polymorphic equality behavior.

### `src.exodus_bundler.bundling.Elf.__hash__` · *method*

## Summary:
Returns an integer hash derived from the object's path attribute so the instance can be used in hashed collections (sets, dict keys) while basing identity on the filesystem path.

## Description:
This method implements Python's object hashing protocol by delegating to the built-in hash of self.path. It is invoked by the Python runtime whenever hash(instance) is called or when an instance is used as a key in a dictionary or an element of a set. Typical lifecycle contexts include:
- When an Elf instance is inserted into a set or used as a dictionary key during dependency collection or bundling phases.
- When code explicitly calls hash(elf_instance) to obtain a stable integer identifier within the current interpreter process.

This behavior is factored into its own method (instead of inlining hash(self.path) at call sites) to centralize the object's hash policy so all uses of hashing rely on a single, consistent implementation and so subclasses can override the behavior if needed.

## Args:
    None

## Returns:
    int: The integer result of built-in hash(self.path). Possible values include any Python integer returned by hash(); commonly a platform-sized signed integer, and may be negative. Note that Python applies hash randomization for strings across interpreter processes, so hash values are not stable across separate process runs.

## Raises:
    AttributeError: If the instance does not have a .path attribute (attribute access fails).
    TypeError: If self.path exists but is not hashable (for example, an unhashable container like a list), the built-in hash call will raise TypeError.

## State Changes:
    Attributes READ:
        self.path
    Attributes WRITTEN:
        None (no attributes of self are modified)

## Constraints:
    Preconditions:
        - The instance must have a .path attribute accessible (commonly a str).
        - The .path value must be hashable (e.g., an immutable type such as str, int, or tuple).
    Postconditions:
        - The method returns an int derived from hashing self.path.
        - The instance's state is unchanged by this call.

## Side Effects:
    - No I/O or external calls.
    - No mutations to objects outside of self.
    - Any exceptions raised are limited to AttributeError or TypeError arising from accessing or hashing self.path (no hidden side effects).

### `src.exodus_bundler.bundling.Elf.__repr__` · *method*

## Summary:
Return a concise, developer-oriented string identifying the Elf object and showing its path attribute.

## Description:
Provides the object's printable representation used by Python's representation protocol (invoked by repr(obj) and implicitly by interactive shells, debuggers, and logging of containers). The listed callers are typical usage contexts for __repr__ but are not explicitly referenced in the source code:
    - repr() built-in or interactive REPL display
    - Logging, debugging, or diagnostic output that prints containers (lists, dicts) containing Elf instances
This logic is implemented as __repr__ to centralize a consistent debugging representation rather than duplicating formatting at call sites.

## Args:
    None.

## Returns:
    str: A string formatted exactly as '<Elf(path="...")>' where the ... is the string conversion of self.path (produced via the '%s' format specifier). Examples:
        - self.path == "/usr/bin/foo" -> '<Elf(path="/usr/bin/foo")>'
        - self.path == None -> '<Elf(path="None")>'

## Raises:
    AttributeError: If the Elf instance lacks a path attribute (accessing self.path triggers this).
    Exception (propagated): If converting self.path to a string raises an exception (for example, if self.path.__str__ raises), that exception will propagate out of this method. No explicit try/except is performed here.

## State Changes:
    Attributes READ:
        - self.path
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The instance should have an attribute named path. The attribute may be any object; it will be formatted via str().
    Postconditions:
        - No mutation of the object or external state occurs.
        - A str value consistent with the format above is returned unless an exception occurs during attribute access or string conversion.

## Side Effects:
    - None: no I/O, no external calls, and no mutations outside of reading self.path.

### `src.exodus_bundler.bundling.Elf.find_direct_dependencies` · *method*

## Summary:
Runs the system dynamic loader diagnostic (ldd) for this ELF file to discover its immediate shared-library dependencies and returns them as File-like objects produced by the instance's file_factory. Does not modify the Elf instance.

## Description:
This method executes an external ldd process (via subprocess.Popen) using the ELF's configured dynamic linker as the executable. It captures stdout and stderr from ldd, parses those lines to extract filesystem paths of resolved shared libraries, ensures the linker itself is included, and converts each discovered path into a file object by calling self.file_factory(..., chroot=self.chroot, library=True).

Known callers and lifecycle context:
- Elf.direct_dependencies (stored_property): directly returns the result of this method with no arguments; used during dependency resolution initialization for an ELF file.
- Elf.dependencies (stored_property): performs a transitive traversal of dependencies and calls dependency.elf.find_direct_dependencies(self.linker_file) to compute direct dependencies for each discovered dependency while resolving the full dependency graph.
- This method is intended to be invoked during bundling or dependency-discovery stages where the immediate (non-transitive) shared-library requirements of an ELF binary are needed.

Why it's a separate method:
- Running ldd, handling environment adjustments (especially for chrooted execution), parsing its combined stdout/stderr output, and converting paths into file objects is a coherent unit of work that is reused by multiple higher-level properties (direct_dependencies and dependencies). Isolating this logic keeps subprocess invocation and parsing concerns separated from graph traversal logic.

## Args:
    linker_file (optional): object with attribute `path` (str)
        - Default: None. If omitted, the method will use self.linker_file as the dynamic linker.
        - Expected shape: any object exposing a `.path` attribute containing a filesystem path string to the linker executable which will be used as the `executable` argument for subprocess.Popen.
        - Typical concrete type: the object returned by self.file_factory (commonly an instance of the project's File class), but the method only requires the `.path` attribute.

## Returns:
    set: A set of file objects produced by calling self.file_factory(path, chroot=self.chroot, library=True)
        - Each element is the result of invoking self.file_factory for a path discovered in ldd output or for the linker itself (linker_path is always appended).
        - If no linker is available (neither linker_file argument nor self.linker_file), returns an empty set().
        - The set de-duplicates file objects using their equality/hash semantics (i.e., duplicates removed).

## Raises:
    - MissingFileError (or other exceptions raised by self.file_factory): if file_factory attempts to construct a file object for a discovered path and that factory raises (for example, when the file is missing). The method itself does not catch exceptions from file_factory.
    - OSError / FileNotFoundError: if launching ldd via subprocess.Popen fails (e.g., ldd is not present, or executable permissions prevent invocation), Popen can raise OSError-derived exceptions.
    - UnicodeDecodeError: when decoding stdout/stderr with utf-8 if ldd emits non-UTF-8 byte sequences; the call to stdout.decode('utf-8') or stderr.decode('utf-8') would raise this error.
    - Note: The method does not explicitly raise DependencyDetectionError or other custom exceptions itself; any such errors must originate from called helpers (parse_dependencies_from_ldd_output) or file_factory.

## State Changes:
    Attributes READ:
        - self.linker_file: consulted when linker_file argument is not provided.
        - self.path: the ELF file path passed as the target argument to ldd.
        - self.chroot: used to adjust LD_LIBRARY_PATH entries and passed through to file_factory.
        - self.file_factory: invoked to construct return objects from discovered paths.
    Attributes WRITTEN:
        - None. The method does not modify attributes on self.

## Constraints:
    Preconditions:
        - Either the `linker_file` argument is provided or self.linker_file must be non-None. If both are None, the method returns an empty set and performs no subprocess call.
        - The provided linker_file must expose a `.path` attribute that is a valid string path to an executable to be used as the dynamic linker.
    Postconditions:
        - If a linker is available, the method has (1) spawned an ldd subprocess with environment variable LD_TRACE_LOADED_OBJECTS='1' and possibly a modified LD_LIBRARY_PATH when self.chroot is set, (2) parsed ldd output to a list of paths using parse_dependencies_from_ldd_output, and (3) returned a set of self.file_factory(...) objects for those paths plus the linker itself.
        - self attributes remain unchanged.

## Side Effects:
    - Spawns an external process: invokes the system 'ldd' command (via subprocess.Popen). The method supplies:
        - argv: ['ldd'] plus optional extra arguments (when self.chroot is truthy, extra arguments added are ['--inhibit-cache', '--inhibit-rpath', '']) and finally [self.path].
        - executable: set to linker_path (linker_file.path).
        - env: a copy of os.environ updated with LD_TRACE_LOADED_OBJECTS='1' and, when self.chroot is set, LD_LIBRARY_PATH adjusted to map standard library directories into the chroot.
    - Reads the subprocess's stdout and stderr into memory and decodes both using UTF-8.
    - Calls parse_dependencies_from_ldd_output with a list of textual lines derived from stdout and stderr combined.
    - Calls self.file_factory for each resulting filename passing chroot=self.chroot and library=True; any side effects of file_factory (I/O, validations, raising exceptions) may occur.
    - Does not mutate global os.environ (a local environment dict is constructed and passed to Popen).

### `src.exodus_bundler.bundling.Elf.dependencies` · *method*

## Summary:
Computes and returns the transitive closure of this ELF's dependencies (all files reachable from the direct dependencies). The result is computed once and typically cached by the stored_property decorator.

## Description:
This property walks the dependency graph starting from self.direct_dependencies and repeatedly expands each dependency that represents an ELF file by calling that dependency's Elf.find_direct_dependencies(self.linker_file). It continues until no new dependencies are discovered and returns the set of all discovered dependency File objects.

Known callers and lifecycle:
- Typically invoked by the bundling pipeline when assembling a bundle for an ELF binary to determine every library and helper file that must be included.
- Consumers include any bundling or packaging routines that need the full set of transitive shared-library and helper-file dependencies before copying or packaging files.
- Because resolving transitive dependencies may require invoking external tools (via find_direct_dependencies), this is normally called during the dependency-resolution stage of bundling rather than in tight loops.

Why this logic is a separate method/property:
- It implements a transitive-closure algorithm (graph traversal) distinct from the direct dependency discovery performed by find_direct_dependencies; separating it keeps concerns clear and allows caching the computed closure via the stored_property decorator so the expensive resolution is performed only once.

## Args:
- None (this is a zero-argument stored property).

## Returns:
- set[File]: A set of file-like objects produced by self.file_factory (one per discovered filename). The set contains:
    - All direct dependencies (self.direct_dependencies).
    - All dependencies discovered by recursively calling find_direct_dependencies on any dependency that has an associated Elf object.
    - No duplicates (set semantics).
    - If there are no dependencies, an empty set is returned.

Edge cases / notes:
- The returned set may include the dynamic linker/loader file (the linker file) because find_direct_dependencies always includes the linker path in its results.
- If a dependency has no .elf attribute or .elf is falsy, it is treated as a leaf and is not expanded further.

## Raises:
- The method body does not explicitly raise exceptions itself.
- It may propagate exceptions raised by underlying operations invoked during dependency discovery, notably:
    - Exceptions raised by dependency.elf.find_direct_dependencies (which invokes ldd via subprocess) — these could be subprocess-related errors or parsing failures.
    - Exceptions raised by self.file_factory when constructing File objects (for example, file-not-found errors in File initialization).
- Callers should be prepared to handle propagated errors originating from find_direct_dependencies or file_factory.

## State Changes:
Attributes READ:
    - self.direct_dependencies
    - self.linker_file

Attributes WRITTEN:
    - None within the function body.
    - Note: because the method is decorated with stored_property (see module), the computed result is typically cached on the instance after first computation; that caching mutates the instance's attribute storage (for example, by adding an attribute named 'dependencies' or similar). The exact cache attribute name and mechanism are handled by the stored_property implementation and are not modified here.

## Constraints:
Preconditions:
    - The Elf instance must be properly initialized (its path must exist and have been validated as an ELF in __init__), so that self.direct_dependencies and self.linker_file reflect valid state.
    - self.direct_dependencies must be an iterable of file-like objects (the values produced by self.file_factory), some of which may have an .elf attribute referencing other Elf instances.

Postconditions:
    - The returned set contains every file reachable from the initial direct dependencies by repeated application of find_direct_dependencies (i.e., the transitive closure).
    - No element appears more than once (set semantics).
    - The method does not modify the dependency objects; only discovery is performed (aside from possible caching by stored_property).

## Side Effects:
- Indirect subprocess execution: resolving further dependencies (dependency.elf.find_direct_dependencies) invokes ldd via Popen (see find_direct_dependencies), so calling this property can cause multiple ldd subprocesses to be executed.
- Indirect filesystem / object construction: find_direct_dependencies and file_factory construct File objects for discovered paths, which can involve filesystem access or raise filesystem-related errors.
- Potential caching: the stored_property decorator typically caches the result on the instance, mutating its attribute dictionary.

### `src.exodus_bundler.bundling.Elf.direct_dependencies` · *method*

## Summary:
Delegates to the underlying dependency-discovery routine and returns the set of direct shared-object files (as File-like objects) that the ELF binary directly depends on. This call does not modify the Elf object's state.

## Description:
This thin wrapper invokes the more complete find_direct_dependencies implementation to obtain the immediate, direct dynamic dependencies of the ELF at self.path.

Known callers and lifecycle:
- The Elf.dependencies stored property uses this method (via the stored_property direct_dependencies) during the bundling dependency-resolution phase to bootstrap recursive dependency discovery.
- Other code that needs only the immediate dependencies of an Elf instance may call this method during bundle construction or analysis.

Why this is a separate method:
- The substantive work (spawning ldd, parsing output, constructing File objects) is implemented in find_direct_dependencies. This wrapper exists to provide a simple public API and to keep the heavy logic testable and isolated from call-sites.

## Args:
None.

## Returns:
- set[File]: A set of file-like objects produced by self.file_factory that represent the direct runtime dependencies of this ELF binary, including the dynamic linker itself.
- Edge case: Returns an empty set when no linker/dynamic loader was found for this ELF (i.e., when self.linker_file is None).

## Raises:
This method does not itself raise new exceptions, but it propagates any exceptions raised by find_direct_dependencies. Notable propagated exceptions include:
- MissingFileError: may be raised if the linker or a reported dependency cannot be located by the file_factory.
- FileNotFoundError / OSError: may be raised if invoking the external 'ldd' process fails (for example, if 'ldd' is not available in the environment or the executable path is invalid).
- Any other exceptions that find_direct_dependencies or the configured file_factory may raise.

## State Changes:
Attributes READ:
- self.path (used to run ldd against the binary)
- self.linker_file (the dynamic linker used when invoking ldd; may be None)
- self.chroot (used by find_direct_dependencies to adjust LD_LIBRARY_PATH and dependency resolution)
- self.file_factory (used to construct file-like objects for each discovered filename)

Attributes WRITTEN:
- None. This method does not mutate the Elf instance.

## Constraints:
Preconditions:
- The Elf instance must have been successfully constructed (path exists and was validated as an ELF during __init__).
- If the environment requires a chroot-aware resolution, self.chroot should be set appropriately at construction time.

Postconditions:
- The return value is a set of File-like objects (possibly empty). The Elf instance's attributes remain unchanged.

## Side Effects:
- Invokes an external process ('ldd') via subprocess.Popen with a custom environment (LD_TRACE_LOADED_OBJECTS and potentially modified LD_LIBRARY_PATH). This spawns a child process and reads its stdout/stderr.
- Constructs File-like objects by calling self.file_factory(...) for each discovered dependency; those constructors may perform I/O or validations (and can raise exceptions).

## `src.exodus_bundler.bundling.File` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.File.__init__` · *method*

## Summary:
Initializes a File object by validating and normalizing the provided filesystem path, deriving an optional entry-point name, probing the path as an ELF binary (if possible), and setting up factory and metadata flags that describe how the file should be bundled.

## Description:
This constructor prepares an instance that represents a concrete filesystem artifact for the bundling pipeline. It performs three distinct responsibilities:
- Normalizes and validates the provided path via resolve_file_path, storing the absolute normalized result on self.path.
- Determines the instance's entry_point attribute based on the entry_point parameter and the resolved path.
- Attempts to construct an Elf wrapper for the artifact (Elf(path, ...)). If the artifact is not a valid ELF binary, the Elf construction failure is handled by setting self.elf to None.

Known callers and lifecycle context:
- Instances are created when the bundler builds an internal representation of items to include in a bundle (binaries, scripts, or other files). Typical lifecycle step: input validation and artifact discovery before dependency detection and launcher/template generation.
- This behavior is intentionally encapsulated in __init__ to centralize path validation, ELF detection, and initialization of the fields that drive later bundling logic (e.g., requires_launcher, no_symlink, file_factory).

Why this is its own method:
- Centralizes multiple initialization concerns (path normalization, entry-point determination, ELF probing) so downstream code can rely on a consistent object state without repeating these checks.

## Args:
    path (str or os.PathLike):
        - Path-like identifier for the target artifact.
        - Will be passed to resolve_file_path which validates existence and normalizes to an absolute path.
    entry_point (None | bool | str, optional):
        - Default: None
        - If True (the boolean True), the constructor derives an entry-point name from the resolved path by taking os.path.basename(self.path) and removing any os.sep characters from that basename.
        - If a non-empty string is provided, that string becomes the entry_point value.
        - If None, entry_point is left as None (no entry point).
        - Note: the code uses (entry_point is not None) when calling resolve_file_path, so passing any value other than None (including False) causes resolve_file_path to run with search_environment_path=True.
    chroot (str or os.PathLike or None, optional):
        - Default: None
        - Forwarded to the Elf constructor as the chroot argument.
    library (bool, optional):
        - Default: False
        - Stored on the instance as a boolean flag indicating whether this file should be treated as a library (affects bundling decisions elsewhere).
    file_factory (callable/class or None, optional):
        - Default: None
        - If provided, stored on the instance and forwarded to the Elf constructor.
        - If None, the instance will set self.file_factory to the File class itself.

## Returns:
    None (constructor). The instance attributes listed under "State Changes" are set as described.

## Raises:
    MissingFileError:
        - Trigger: resolve_file_path raises MissingFileError when the candidate path does not exist. Because resolve_file_path is called without an enclosing try/except here, this exception will propagate out of __init__.
    UnexpectedDirectoryError:
        - Trigger: resolve_file_path raises UnexpectedDirectoryError when the candidate path exists but is a directory. This exception is not caught here and will propagate.
    Any exception raised by resolve_file_path (e.g., TypeError if passed a non-path-like) will propagate.
    Any exception raised by the Elf constructor other than InvalidElfBinaryError will propagate. InvalidElfBinaryError is explicitly caught and handled by setting self.elf = None.
    AttributeError:
        - Trigger: evaluating self.requires_launcher during computation of self.no_symlink will raise AttributeError if the instance property/attribute requires_launcher does not exist or raises. This call happens after the Elf construction attempt; therefore AttributeError can arise during initialization if requires_launcher is missing or faulty.

## State Changes:
Attributes READ:
    - entry_point (parameter): read to determine search_environment_path passed to resolve_file_path and to set self.entry_point.
    - file_factory (parameter): read when forwarded to Elf and for deciding default self.file_factory.
    - self.requires_launcher: read when computing self.no_symlink (the code accesses this attribute/property).
Attributes WRITTEN:
    - self.path (str): set to the normalized absolute path returned by resolve_file_path(path, search_environment_path=(entry_point is not None)).
    - self.entry_point (None | str): set to:
        * os.path.basename(self.path).replace(os.sep, '') if entry_point is the boolean True
        * entry_point (if a non-None value is provided and not True)
        * None if entry_point is None or evaluates to None
    - self.elf (Elf instance or None): set to the Elf(...) return value, or None if Elf(...) raised InvalidElfBinaryError.
    - self.chroot: set to the chroot parameter value.
    - self.file_factory: set to file_factory if truthy, otherwise set to the File class.
    - self.library: set to the library parameter (boolean).
    - self.no_symlink (bool or truthy/falsey): set to the boolean result of self.entry_point and not self.requires_launcher using Python truthiness semantics (see Constraints).

## Constraints:
Preconditions:
    - path must be a path-like object (str or os.PathLike) acceptable to resolve_file_path. Passing None or an invalid type may raise TypeError from underlying calls.
    - If the class expects requires_launcher to be available (property or attribute), that attribute must be implemented on the class or by a mixin; otherwise AttributeError will be raised during initialization.
Postconditions / Guarantees:
    - On successful return (no exception), self.path contains the normalized absolute path returned by resolve_file_path and satisfies the file-existence checks that resolve_file_path enforces.
    - On successful return, self.elf is either an Elf instance wrapping the artifact (if Elf(...) completed successfully) or None (if Elf(...) raised InvalidElfBinaryError).
    - self.file_factory is guaranteed to be non-None after initialization (either the provided file_factory or the File class).
    - self.no_symlink will be truthy exactly when:
        * self.entry_point is a truthy value (non-empty string) AND
        * self.requires_launcher evaluates to a falsey value (False or any falsey return from the attribute/property).
      Otherwise self.no_symlink will be falsey.

## Side Effects:
    - Calls resolve_file_path(...) which performs filesystem metadata checks (exists/isdir) and may read environment PATH when search_environment_path is True.
    - Invokes the Elf constructor Elf(path, chroot=..., file_factory=...) which may open or inspect the file on disk and may itself perform dependency detection, filesystem reads, or raise errors; any side effects of Elf(...) are those of the Elf initializer.
    - No file system mutations (writes, deletions) are performed here directly by this method itself.

## Notes and Implementation Details:
    - Important subtlety: resolve_file_path is called with search_environment_path=(entry_point is not None). Therefore passing any entry_point value other than None (including False or an empty string) will enable environment-based resolution in resolve_file_path. Callers intending to avoid PATH-based resolution should pass entry_point=None.
    - When entry_point is the boolean True, the code derives a filesystem-base name for the entry point from self.path and removes os.sep characters from that basename. This typically yields the filename component, but callers should be aware that an empty basename or unusual characters could yield an empty string.
    - Elf(...) is constructed with the original path parameter (not the resolved self.path). This means the Elf constructor will receive whatever the caller supplied as path; any normalization performed by resolve_file_path is not forwarded to Elf in the current code path.

### `src.exodus_bundler.bundling.File.__eq__` · *method*

## Summary:
Compares this File object against another for equality and returns a boolean. (Note: due to a bug in the implementation, any two File instances compare as equal as long as the other object is a File.)

## Description:
This method is invoked implicitly by Python's equality operator (==) and by any data structures or algorithms that perform equality comparisons (for example, when checking membership in lists, sets, or when used as a key-comparison step in dict operations). In the bundling codebase File equality is intended to be used when deduplicating or comparing File objects in the bundling pipeline; the concrete call-sites are anywhere the code checks whether two File objects represent the same file entry.

This logic is implemented as a dedicated method to provide a single, consistent definition of equality for File instances (so that comparisons are portable throughout the bundling logic and can account for both the filesystem path and the entry_point identity). However, the current implementation contains a logical error: after verifying that other is an instance of File, it compares self.path to self.path and self.entry_point to self.entry_point (instead of comparing to other's corresponding attributes). As a result, equality returns True for any two File instances, regardless of their path or entry_point values, as long as other is an instance of File.

The method is kept separate (rather than inlined) to allow overriding or specialization for subclasses of File and to ensure object-level semantics are centralized.

## Args:
    other (object):
        - Any Python object. The method first checks whether other is an instance of the File class.
        - No default value.

## Returns:
    bool:
        - True if other is an instance of File (because of the implementation bug, all File instances compare equal).
        - False if other is not an instance of File.
        - There are no other possible return values.

## Raises:
    - This method does not raise any exceptions itself.
    - It assumes that self has attributes 'path' and 'entry_point'; if those attributes are missing on the instance, Python will raise AttributeError when the method attempts to access them (this reflects an object construction or mutation problem elsewhere, not an intended behavior here).

## State Changes:
    Attributes READ:
        - self.path
        - self.entry_point
        - type information of other (via isinstance)
    Attributes WRITTEN:
        - None. The method does not modify self or other.

## Constraints:
    Preconditions:
        - self must be a properly-initialized File instance with at least 'path' and 'entry_point' attributes (both may be None in normal usage, but the attributes must exist).
        - other may be any object; the method will perform an instance check first.
    Postconditions:
        - The method returns a boolean, with the current implementation guaranteeing:
            * False if other is not an instance of File.
            * True if other is an instance of File (regardless of attribute values).
        - No attributes of self or other are modified.

    Consistency note / contract violation:
        - The implementation violates the standard Python invariant that equal objects must have equal hashes because File.__hash__ computes hash((self.path, self.entry_point)). Because __eq__ returns True for all File instances (independent of those attributes), two objects that __eq__ considers equal can produce different hashes. This leads to undefined or surprising behavior when File instances are used as keys in dictionaries or as members of sets.

## Side Effects:
    - None: the method performs no I/O, no filesystem or network operations, and does not mutate any external state.

## Implementation guidance (for reimplementation or fix):
    - Correct behavior (intended): first verify other is a File, then compare the two instances' distinguishing attributes (typically self.path == other.path and self.entry_point == other.entry_point) and return that result.
    - Ensure that __hash__'s logic matches the equality definition so the equality/hash contract holds: if equality depends on (path, entry_point), __hash__ must hash the same tuple.
    - Be careful when either attribute can be None; comparisons should handle None consistently (Python's equality operators handle None safely).
    - Keep the method free of side effects and avoid accessing any expensive properties unless necessary.

### `src.exodus_bundler.bundling.File.__hash__` · *method*

## Summary:
Compute and return an integer hash for this File instance based solely on the instance's path and entry-point attributes, so the object can be used where Python hashing is required (e.g., as a dict key or set member).

## Description:
This method implements Python's hashing protocol for the File object by returning the built-in hash of the tuple (self.path, self.entry_point). It is invoked implicitly by operations that require a hash:
- the built-in hash() function when called on the instance
- insertion, membership checks, or lookups when the instance is used as a key in a dict or as an element of a set
- any third-party code or library that calls hash() on objects it works with

Why this is a separate method:
- Python expects __hash__ to be defined on classes whose instances must be hashable; centralizing the logic here ensures a single, stable definition of hash identity based on the file path and optional entry point.
- Using the tuple (path, entry_point) makes the hash deterministic from those attributes and easy to reason about and reproduce.

Important note about class equality/consistency:
- The Python requirement for hashable objects is: if a == b is True then hash(a) == hash(b) must also hold. In the current File class implementation, __hash__ depends on (path, entry_point) while the provided __eq__ implementation does not compare against the other instance's attributes (it compares self.path to itself and self.entry_point to itself). That implementation is a bug: it causes many distinct File instances to compare equal while producing different hashes. Developers reimplementing or relying on this class should ensure __eq__ compares the same attributes used by __hash__ (e.g., compare other.path and other.entry_point) to preserve the hash/eq contract.

## Args:
- None. The method reads the instance attributes and takes no parameters.

## Returns:
- int: The integer result of Python's hash((self.path, self.entry_point)).
  - The integer may be negative or positive as returned by Python's hash implementation.
  - If self.entry_point is None, the tuple contains None which is hashable; that is a valid case.
  - Repeated calls while attributes are unchanged yield the same value within the same Python process; if attributes change, the returned value may change.

## Raises:
- AttributeError: if the instance lacks .path or .entry_point (these are expected to be set by the class initializer).
- TypeError: if either .path or .entry_point is an unhashable object (very unlikely in normal usage because these are expected to be str or None).

## State Changes:
- Attributes READ:
    - self.path
    - self.entry_point
- Attributes WRITTEN:
    - None. This method is read-only and performs no mutations.

## Constraints:
- Preconditions:
    - The instance must have attributes .path and .entry_point defined before calling __hash__ (the class __init__ sets these).
    - Both attributes must be hashable (strings and None are safe).
    - Do not mutate .path or .entry_point while the object is stored in a hashed collection (dict/set); changing the attributes while the object is used as a key/element will break lookups.
- Postconditions:
    - No mutation to the instance or external state.
    - The returned integer is fully determined by the current values of .path and .entry_point.

## Side Effects:
- None. There is no I/O, no external calls, and no mutation of other objects.

## Implementation guidance / recommended fix:
- Implement __hash__ exactly as hash((self.path, self.entry_point)).
- Ensure __eq__ is implemented to compare the same attributes (for example, return isinstance(other, File) and self.path == other.path and self.entry_point == other.entry_point). This guarantees the necessary invariant that equal objects have equal hashes.

### `src.exodus_bundler.bundling.File.__repr__` · *method*

## Summary:
Returns a concise, human-readable representation of the File object that includes its path for debugging and logging purposes.

## Description:
- Known callers:
    - No explicit callers were discovered in the provided component source. This method is intended to be invoked implicitly by built-in operations that request an object's representation (for example, repr(file_obj), when an object is printed in interactive sessions, or when objects are logged/inspected).
- Lifecycle / pipeline stage:
    - Typically used during debugging, logging, inspection, or any point where a developer or system component requests a textual representation of the File instance.
- Rationale for being a separate method:
    - Providing a dedicated __repr__ supplies a consistent, short, and unambiguous textual form for the object across the codebase and standard library tooling. Keeping this logic in __repr__ centralizes the representation format and avoids duplicating ad-hoc string formatting in callers.

## Args:
    None

## Returns:
    str: A string in the exact format '<File(path="<path>")>' where <path> is the string result of self.path (i.e., str(self.path)).
    - Example resulting value: '<File(path="/some/path/to/file.txt")>'
    - Edge cases:
        - If self.path is None, the returned string will contain 'None' (i.e., '<File(path="None")>').
        - If self.path contains double-quote characters, they are inserted verbatim into the returned string (no escaping is performed).

## Raises:
    AttributeError: If the File instance does not have a path attribute, attempting to evaluate self.path will raise AttributeError.
    (No exceptions are explicitly raised by the method itself; the AttributeError arises from normal attribute access.)

## State Changes:
- Attributes READ:
    - self.path
- Attributes WRITTEN:
    - None (the method does not modify any attributes on self)

## Constraints:
- Preconditions:
    - The object must have a 'path' attribute accessible on self. The attribute's value should be convertible to str (i.e., implementing __str__); otherwise, the returned representation will incorporate whatever str(self.path) yields.
- Postconditions:
    - No internal state of the object is modified.
    - The method returns a new string that contains a snapshot of the value of self.path at the time of the call.

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not mutate objects outside of self.

## Implementation notes for reimplementation:
    - Use the exact formatting: '<File(path="%s")>' % self.path
    - Ensure no additional escaping or transformation of self.path is performed unless callers require it; preserving current behavior means double quotes and other characters in path are emitted as-is.

### `src.exodus_bundler.bundling.File.copy` · *method*

## Summary:
Copies the file referenced by the object into the bundler working tree and returns the absolute, normalized destination path on disk. If the destination already exists, no copy is performed and the existing path is returned.

## Description:
Known callers:
    - Exact call sites are not present in this snippet. This method is intended to be used by the bundling/orchestration logic that prepares files for inclusion in a bundle or working directory prior to packaging or dependency analysis.
    - Typical lifecycle: invoked during the bundling preparation step where each File-like object is materialized into a working directory.

Why this is a separate method:
    - Encapsulates the filesystem placement logic (destination path construction, directory creation, and copying) in a single reusable unit so higher-level bundling code can simply request materialization without duplicating IO and path-normalization logic.

## Args:
    working_directory (str): Base directory into which the file should be copied. May be absolute or relative. The method will combine this with the object's destination attribute to form the final target path.

## Returns:
    str: The absolute, normalized path to the target file on disk (i.e., os.path.normpath(os.path.abspath(<computed_path>))).
    - If the destination already exists on disk, returns that existing absolute path without performing a copy.
    - On successful copy, returns the absolute path to the newly created copy.

## Raises:
    - FileNotFoundError: If self.path does not exist (raised by shutil.copy) or if intermediate path components cannot be resolved when attempting to copy.
    - PermissionError: If the process lacks permission to create directories or to read the source or write the destination (raised by os.makedirs or shutil.copy).
    - IsADirectoryError: If self.path refers to a directory rather than a regular file (shutil.copy will raise).
    - OSError / IOError: For other lower-level filesystem errors propagated from os.path, os.makedirs, or shutil.copy (e.g., disk full, invalid path name).
    Note: The method does not raise custom bundler exceptions itself; it surfaces underlying filesystem exceptions.

## State Changes:
Attributes READ:
    - self.destination: used to build the relative/absolute placement inside working_directory.
    - self.path: used as the source file to copy.

Attributes WRITTEN:
    - None on the Python object itself. No attributes of self are modified by this method.

## Constraints:
Preconditions:
    - self.path must be a path-like string referring to an existing file readable by the process.
    - working_directory must be a valid path-like string (existing or creatable parent directories).
    - self.destination should be a path-like string describing the desired location inside or relative to working_directory. If it is absolute, it will be joined and then normalized/absoluted (normal os.path.join semantics apply).

Postconditions:
    - The returned string is an absolute, normalized path.
    - If the method returns without raising, either:
        * The destination path already existed prior to the call (no new file was created), or
        * A new file identical in content to self.path has been created at the returned path (shutil.copy semantics).
    - The method will not overwrite an existing destination file; it exits early when the computed destination path already exists.

## Side Effects:
    - May create one or more directories on disk (os.makedirs(parent_directory)) to ensure the destination's parent exists.
    - May create a file on disk by copying contents from self.path to the destination (shutil.copy). This affects external filesystem state.
    - Does not modify other in-memory objects besides potentially raising exceptions; no network or external service calls are performed.
    - Symlinks: shutil.copy follows symlinks (copies the target file contents), so if self.path is a symlink the file content at the link target is copied rather than recreating a symlink.

### `src.exodus_bundler.bundling.File.create_entry_point` · *method*

## Summary:
Ensure working_directory/bin exists and create a relative symbolic link inside it named by this file's entry_point that points to the file's staged source in bundle_root. This performs filesystem mutations but does not alter the File object's in-memory attributes.

## Description:
This method performs two filesystem responsibilities present in the implementation:
1. Ensure a bin directory exists under the supplied working_directory (checks existence and calls directory creation if absent).
2. Create a symbolic link located at working_directory/bin/<self.entry_point> whose target is the relative path from that bin directory to the file's staged source (computed from bundle_root and self.source).

Why this logic is its own method:
- It isolates filesystem layout and path-handling concerns (directory creation and relative symlink creation) from higher-level bundling logic such as staging, dependency detection, and packaging, making these concerns easier to test and reason about.
- The method centralizes behavior for creating relocatable entry points (relative symlinks) so callers need not duplicate path computations.

Known callers and lifecycle stage:
- No explicit callers are declared inside this source snippet. Conceptually, this is expected to be called during the bundling/packaging phase after files are staged into bundle_root and before final packaging or deployment.

## Args:
    working_directory (str): Path to the working tree where a bin/ subdirectory will be ensured (absolute or relative).
    bundle_root (str): Path to the root of the staged bundle containing this file's source (absolute or relative).

## Returns:
    None — the method does not return a value. Successful completion implies the filesystem side effects were performed.

## Raises:
- ValueError:
    - Raised by the relative-path computation (os.path.relpath) if a relative path cannot be computed (for example, on Windows when source_path and bin_directory are on different drives).
- FileExistsError:
    - Raised by os.symlink when an entry already exists at the computed entry_point_path.
    - May also be raised by os.makedirs if a race causes a conflicting object to appear between the os.path.exists check and the os.makedirs call.
- PermissionError (subclass of OSError) or OSError:
    - Raised when permissions or platform restrictions prevent creating directories or symlinks, or for other low-level filesystem failures (invalid path, too-long paths, etc.).
Notes:
    - The implementation does not check that the symlink target exists. Creating a symlink to a non-existent target typically succeeds and does not raise here.

## State Changes:
Attributes READ:
    - self.source: read to compute source_path via joining bundle_root and self.source.
    - self.entry_point: read to compute the name for the symlink under bin/.

Attributes WRITTEN:
    - None of the File object's attributes are modified.

Filesystem state mutated (outside the object):
    - Ensures working_directory/bin exists by creating it when missing (os.makedirs).
    - Creates a filesystem symbolic link at working_directory/bin/<self.entry_point> pointing to the relative path from that bin directory to the computed source_path (os.symlink with target from os.path.relpath).

## Constraints:
Preconditions:
    - working_directory and bundle_root must be valid path-like strings.
    - self.source and self.entry_point should be non-empty strings.
    - Prefer that self.entry_point is a relative filename (no directory separators). If entry_point contains directory components, this method does not create those intermediate directories under bin/ and symlink creation will fail unless callers create them first.
    - The runtime environment must permit symlink creation (some platforms require elevated privileges).

Postconditions:
    - On success:
        * working_directory/bin exists (created if necessary).
        * working_directory/bin/<self.entry_point> exists and is a symbolic link whose target equals the relative path computed by os.path.relpath(source_path, bin_directory).
    - On failure: partial side effects may remain (for example, bin/ may have been created even if symlink creation later failed).

## Behavior details and edge cases:
    - Path joining semantics:
        * source_path is computed as os.path.join(bundle_root, self.source). If self.source is an absolute path, the join yields that absolute path and bundle_root is ignored.
        * entry_point path is computed as os.path.join(bin_directory, self.entry_point). If self.entry_point is absolute, the join yields that absolute path and the symlink will be created at that absolute location (i.e., outside bin_directory).
    - Relative symlink target:
        * The symlink target is computed with os.path.relpath(source_path, bin_directory) so the created link is relative to bin_directory. This makes the link resilient to relocating the whole bundle as long as relative layout is preserved.
    - Windows drive mismatch:
        * os.path.relpath may raise ValueError if source_path and bin_directory are on different drives on Windows; callers should either ensure same-drive layout or handle ValueError.
    - Missing source file:
        * The method does not verify existence of source_path; a symlink to a non-existent target will typically be created without error.
    - Existing entry point:
        * If an entry already exists at the computed entry_point_path, os.symlink will raise FileExistsError. If replacing links is desired, callers must remove or overwrite existing entries beforehand.
    - Directory creation race:
        * The implementation checks os.path.exists before calling os.makedirs. A race between that check and makedirs by another process may result in FileExistsError or related OSError; callers should handle such races.
    - Non-atomic operations:
        * Directory creation and symlink creation occur in separate steps; failures after directory creation leave side effects in place.

## Side Effects:
    - Filesystem I/O: may create directories and a symlink (os.makedirs and os.symlink).
    - No network or external service calls.
    - No mutation of other in-memory objects beyond the filesystem.

## Example (illustrative, not executable code):
    Given:
        working_directory = "/tmp/work"
        bundle_root = "/tmp/staged"
        self.source = "scripts/run"        (so source_path = "/tmp/staged/scripts/run")
        self.entry_point = "run"           (so entry will be created at "/tmp/work/bin/run")
    Result after successful call:
        - Directory "/tmp/work/bin" exists.
        - A symlink "/tmp/work/bin/run" exists whose target is the relative path from "/tmp/work/bin" to "/tmp/staged/scripts/run" (e.g., "../../staged/scripts/run"), allowing the bundle tree to be relocated while preserving the link.

### `src.exodus_bundler.bundling.File.create_launcher` · *method*

## Summary:
Create and install a launcher file for this File into the bundle tree and return its absolute path; updates bundle filesystem state (creates directories, symlinks, copies the ELF linker, writes the launcher, and copies mode bits).

## Description:
This method builds a launcher wrapper for an ELF executable represented by this File and places it under the bundle root so that the bundled application can be started within the bundle layout.

Typical callers / context:
- Invoked during the bundling/packaging pipeline when a File instance represents an ELF executable that requires a runtime launcher (for example when File.requires_launcher is True or when creating entry-point launchers).
- Called as part of preparing the bundle filesystem before final packaging or export.

Why this is a separate method:
- The logic touches multiple filesystem operations (directory creation, symlink creation, copying the linker file, generating either a binary or a shell-based launcher, and applying permission bits). Encapsulating these steps in one focused method keeps higher-level bundling code simple and centralizes launcher-specific rules (library path computation, chroot handling, linker consistency checks, and binary vs shell fallback behavior).

## Args:
    working_directory (str):
        Absolute or relative path representing the bundle's working layout root where "destination" items will be placed (used to compute the final destination_path).
    bundle_root (str):
        Absolute or relative path to the root directory where bundle source files/launchers are created (used to compute source_path).
    linker_basename (str):
        Basename (filename only) to use for the copied linker inside the source parent directory (e.g. 'ld-musl-x86_64.so.1'). Must be a non-empty filename string.
    symlink_basename (str):
        Basename used to create a symlink in the same directory as the launcher pointing to the actual destination executable (used as the "executable" argument to the launcher). Must be a non-empty filename string.
    shell_launcher (bool, optional):
        Default False. If True forces the fallback shell (bash) launcher implementation instead of constructing a binary launcher. When False the code will attempt to create a binary launcher and automatically fall back to a shell launcher if the binary-constructor raises CompilerNotFoundError.

## Returns:
    str:
        Absolute, normalized path to the created launcher file (the on-disk source_path under bundle_root). The returned path is produced via os.path.normpath(os.path.abspath(source_path)).
        Edge cases:
        - If launcher creation fails by raising an exception, no path is returned (exception is propagated).
        - If the method succeeds, the returned path points to an existing file that contains the launcher content and has mode bits copied from self.path.

## Raises:
    AttributeError:
        If self.elf is None or self.elf.linker_file is missing and the code attempts to access self.elf.linker_file.path (i.e., method assumes an ELF with a linker file).
    FileNotFoundError:
        If self.path or the referenced linker file path does not exist when attempting to open or copy it.
    FileExistsError / OSError:
        If the symlink path (symlink at source_parent/symlink_basename) already exists, os.symlink will raise a FileExistsError (or a subclass of OSError) unless the caller ensured it did not exist.
    AssertionError:
        If a linker file already exists at the target linker_path but its contents differ from self.elf.linker_file.path. The assertion message will indicate which linker_path caused the conflict.
    Any exception propagated by construct_binary_launcher or construct_bash_launcher:
        construct_binary_launcher is invoked in the optimistic path and may raise CompilerNotFoundError (handled internally by falling back), or other exceptions if the launcher construction fails; construct_bash_launcher may raise exceptions for invalid inputs or I/O errors. I/O operations (writing files, copying) can raise standard I/O exceptions.

## State Changes:
Attributes READ:
    self.destination (reads stored_property to compute destination_path)
    self.source (reads stored_property to compute source_path)
    self.path (to compute original_file_parent and to copy modes)
    self.elf (to access linker_file.path and elf.dependencies)
    self.chroot (may be read when adjusting library search directories)

Attributes WRITTEN (object state modified):
    None of this File object's attributes are mutated by this method.

Filesystem / external state written (side-effects):
    - Creates directories under bundle_root and working_directory as needed (os.makedirs).
    - Creates a symlink at source_parent/symlink_basename pointing to the relative destination.
    - Copies the ELF linker file to source_parent/linker_basename (shutil.copy).
    - Writes the launcher content to source_path (binary or text depending on launcher type).
    - Copies file permission bits from self.path onto source_path (shutil.copymode).

## Constraints:
Preconditions (caller must ensure):
    - self.path must be a valid filesystem path to an existing file.
    - self.elf must be a valid ELF descriptor (not None) and self.elf.linker_file must exist with a readable .path.
    - linker_basename and symlink_basename should be valid filenames (no directory components); the caller must ensure they do not violate filesystem constraints for target directories.
    - Caller should ensure it has permission to create directories, symlinks, and files under bundle_root and working_directory.

Postconditions (guarantees after successful return):
    - A file exists at the returned absolute path containing the launcher content (binary or shell script).
    - A symlink exists beside the launcher (source_parent/symlink_basename) pointing relatively to working_directory/self.destination.
    - A linker file exists at source_parent/linker_basename with contents identical to self.elf.linker_file.path (or the method asserts/fails if a conflicting file already existed).
    - The launcher file's mode bits (permissions) match those of self.path (copied via shutil.copymode).
    - The returned path is normalized absolute path to the created launcher file.

## Behavior details & edge cases:
    - Library search path construction:
        * Starts from LD_LIBRARY_PATH environment variable split on ':' and then appends common system lib locations.
        * Adds the parent directories of each dependency in self.elf.dependencies.
        * Each directory is normalized to an absolute path; if self.chroot is set, the directory is prefixed with the chroot path (the original absolute directory's relative path to '/' is appended to self.chroot).
        * The final LD_LIBRARY_PATH value embedded in the launcher is a colon-joined list of relative paths from the original file's parent directory to each library directory (duplicates removed while preserving order).
    - Linker detection:
        * Reads the binary linker file at self.elf.linker_file.path to determine a boolean full_linker flag: True when the bytes b'inhibit-rpath' are present.
    - Launcher generation:
        * Attempts to build a binary launcher via construct_binary_launcher when shell_launcher is False. If construct_binary_launcher cannot be used (simulated or signaled by CompilerNotFoundError), the method logs a warning (unless shell_launcher was explicitly requested) and falls back to construct_bash_launcher.
        * Binary launcher content is written in binary mode ('wb'); shell launcher (bash fallback) is written as text ('w').
    - Existing linker collision:
        * If linker_basename already exists under source_parent, the method verifies that its contents match self.elf.linker_file.path using filecmp.cmp. If they differ, an AssertionError is raised with a message naming the conflicting path.
    - Symlink creation:
        * The method creates a symlink without pre-checking for an existing file at the symlink path; if the symlink path already exists, creation will raise an OSError/FileExistsError.
    - File permissions:
        * After writing the launcher file, permission bits are copied from the original file (self.path) to the launcher path to ensure executable permissions are preserved when appropriate.

## Side Effects:
    - Extensive filesystem I/O: may create directories, symlinks, copy files, open and write files, and change file permission bits.
    - Reads the LD_LIBRARY_PATH environment variable to seed the library search path.
    - Emits a logger.warning (module logger) when falling back to a shell launcher for performance/efficiency reasons.
    - Does not mutate the File instance itself but changes the on-disk bundle layout.

### `src.exodus_bundler.bundling.File.symlink` · *method*

## Summary:
Ensure a symbolic link exists at this File's source path inside bundle_root that points (using a relative path) to this File's destination inside working_directory, and return the normalized absolute path of that symlink.

## Description:
This method performs the precise filesystem steps implemented in the source:

1. Compute destination_path = os.path.join(working_directory, self.destination).
2. Compute source_path = os.path.join(bundle_root, self.source).
3. Compute source_parent = os.path.dirname(source_path). If source_parent does not exist, create it with os.makedirs(source_parent).
4. Compute relative_destination_path = os.path.relpath(destination_path, source_parent).
5. If os.path.exists(source_path) is True:
   - Assert os.path.islink(source_path) is True.
   - Assert os.path.realpath(source_path) == relative_destination_path.
   If both assertions succeed, no further action is taken.
6. If os.path.exists(source_path) is False:
   - Create a symlink with os.symlink(relative_destination_path, source_path).
7. Return os.path.normpath(os.path.abspath(source_path)).

Known callers and lifecycle context:
- The source code for this class shows no direct internal callers of this method. The method is written to be invoked by external bundling code after the destination file has been placed at working_directory/self.destination (for example, after File.copy or File.create_launcher). The method itself contains only the symlink-related operations listed above.

Why this logic is a separate method:
- It consolidates directory creation, relative-path computation, idempotency checks for pre-existing entries, and symlink creation into a single, reusable unit.

## Args:
    working_directory (str)
        Path used as the base for computing the destination file location.
    bundle_root (str)
        Path used as the base for computing where the symlink (source) should live.

## Returns:
    str
        The normalized absolute filesystem path to the symlink at os.path.join(bundle_root, self.source).
        - The returned string is computed with os.path.normpath(os.path.abspath(source_path)).
        - If the symlink already existed and satisfied the assertions, the same path is returned.
        - If the symlink was created by this method, the newly created path is returned.

## Raises:
    AssertionError
        - Raised when source_path exists and is not a symbolic link:
            Condition in code: os.path.exists(source_path) is True and os.path.islink(source_path) is False.
        - Raised when source_path exists as a symlink but os.path.realpath(source_path) != relative_destination_path:
            Condition in code: os.path.exists(source_path) is True, os.path.islink(source_path) is True, and os.path.realpath(source_path) != relative_destination_path.
        Note: these are plain assert statements in the source; no custom messages are provided.

    OSError (and subclasses raised by underlying os calls)
        - os.makedirs(source_parent) may raise OSError on failure to create directories.
        - os.symlink(relative_destination_path, source_path) may raise OSError on failure to create the symlink.
        These exceptions are not caught inside the method.

## State Changes:
Attributes READ:
    - self.destination (used to form destination_path)
    - self.source (used to form source_path)

Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - working_directory and bundle_root must be valid path strings.
    - The caller is responsible for ensuring that any required destination file at os.path.join(working_directory, self.destination) exists if needed by higher-level logic; this method does not validate the existence of the destination file.

Postconditions:
    - If the method returns successfully, os.path.join(bundle_root, self.source) exists and is a symbolic link.
    - The symlink's stored content equals the value of relative_destination_path computed inside the method (because the method writes that string when creating the symlink).
    - The method returns the normalized absolute path to that symlink (os.path.normpath(os.path.abspath(source_path))).

## Side Effects:
    - May create directories under bundle_root via os.makedirs(source_parent).
    - May create a symlink under bundle_root via os.symlink(relative_destination_path, source_path).
    - Reads filesystem metadata using os.path.exists, os.path.islink, and os.path.realpath.

## Edge cases and implementation notes:
    - The code uses os.path.realpath(source_path) and compares it for equality to the computed relative_destination_path; this exact comparison is implemented by the source and will trigger AssertionError if not equal.
    - The method does not handle races between checking for existence and creating directories or symlinks; underlying OSError exceptions are propagated.
    - The returned path is the symlink's absolute path; to obtain the symlink's resolved target, call os.path.realpath on the returned path yourself.

### `src.exodus_bundler.bundling.File.destination` · *method*

## Summary:
Returns the relative bundle-path where this file's contents should be stored inside the bundle data directory (./data/<sha256>), based on the file's content hash. This value is used to determine where the file will be copied or referenced within the bundle.

## Description:
Known callers and lifecycle stage:
- File.copy(working_directory): called when copying the file into the working bundle; the returned value is joined with the working_directory to form the destination filesystem path.
- File.create_launcher(...): used when building a launcher; the destination is used to construct the launcher/symlink target.
- File.symlink(working_directory, bundle_root): used to create symlinks from bundle entries back to the data location.
These calls occur during the bundling pipeline when files are being prepared for inclusion in a bundle (copying, creating launchers, or creating symlinks). The method provides a single authoritative place to compute the per-file bundle path from the content hash so all callers use a consistent layout.

Why this is a separate method:
- The destination string is a stable, derived attribute of a File (it depends on the content hash) and is used repeatedly by several File methods. Centralizing the path computation avoids duplicated string formatting logic and ensures consistent layout (./data/<hash>) across different parts of the bundling process.

## Args:
- None.

## Returns:
- str: A relative filesystem path in the form './data/<hash>', where <hash> is the SHA-256 hex digest of the file content (64 hex characters). Example: './data/3a7bd3e2360a...'.
- Edge cases:
    - If the underlying hash computation returns the SHA-256 of an empty file, the returned path will be './data/<sha256-of-empty-bytes>' (a valid 64-hex-character suffix).
    - The method itself does not normalize the returned path beyond os.path.join; callers normally join this value with a working directory (e.g., os.path.join(working_directory, self.destination)).

## Raises:
This method accesses self.hash; any exceptions thrown while computing or retrieving that attribute will propagate out of destination. Notable exceptions observable from the hash computation:
- FileNotFoundError: raised if the file at self.path does not exist when the hash is computed.
- PermissionError (or OSError): raised if the file cannot be opened due to permission or other I/O errors.
- Any other I/O-related exceptions raised while reading the file (e.g., IOError, OSError) will also propagate.

No exceptions are raised directly by simple string concatenation in destination itself.

## State Changes:
- Attributes READ:
    - self.hash (accessing this may in turn open and read the file at self.path)
- Attributes WRITTEN:
    - None by this method's body. Note: destination is declared with @stored_property in the class; depending on the stored_property implementation this may memoize the computed value (i.e., store it on self), but that cache write is an implementation detail of the stored_property decorator, not of destination's body.

## Constraints:
- Preconditions:
    - self.path must refer to the file whose content determines the hash. Typically established during File construction via resolve_file_path.
    - The caller should expect that accessing destination may trigger file I/O the first time (when self.hash must be computed).
- Postconditions:
    - The method returns a string path whose final path component equals the SHA-256 hex digest (64 hex characters) computed from the file content.
    - The returned path always begins with './data' joined to the hash component (formally: os.path.join('.', 'data', <hash>)).

## Side Effects:
- Implicit file I/O: accessing destination causes access to self.hash; if the hash is not yet cached, computing it will open and read the entire file at self.path (this is the primary side effect and can raise the exceptions listed above).
- No external I/O, network calls, or modifications to on-disk files are performed by destination itself (it only returns a path string). The returned path is subsequently used by other methods that perform file-copying or symlink creation.

### `src.exodus_bundler.bundling.File.executable` · *method*

## Summary:
Returns whether the underlying filesystem entry at this File object's resolved path is executable by the current process; used to determine whether the file should be treated as an executable during bundling.

## Description:
Known callers and lifecycle context:
- File.requires_launcher: calls this property while deciding whether a launcher wrapper is necessary for the file. This check occurs during bundle analysis and when preparing entry points/launchers for bundling.
- File.__init__: indirectly depends on requires_launcher (which uses this property) to set self.no_symlink at construction time.
- Any external code that inspects a File instance's executability by reading the executable stored property.

Why this is a separate method/property:
- The check is a single, well-defined OS-level permission query that is useful in multiple places (e.g., deciding whether to create launchers, entry-points, or symlinks). Exposing it as a (cached) property centralizes the logic, keeps call sites simple, and allows caching the result for the lifetime of the File instance.

## Args:
None.

## Returns:
bool
- True if the filesystem reports that the path is executable (os.access(self.path, os.X_OK)).
- False otherwise.
- Edge cases:
  - If the path does not exist or is a broken symlink, returns False.
  - If permissions disallow execution for the (real) user under which the process is running, returns False.
  - Platform-specific semantics apply (e.g., on some systems os.X_OK is interpreted differently); callers should treat the result as the system-level execute-permission check.

## Raises:
- The method itself does not raise application-level exceptions under normal operation.
- Possible lower-level exceptions (rare in normal usage):
  - TypeError if self.path is not a str/bytes path-like object (this is unlikely because File.__init__ resolves the path).
  - Any exceptions raised by the underlying os.access call are not handled here; in typical usage these do not occur for valid path strings.

## State Changes:
Attributes READ:
- self.path

Attributes WRITTEN:
- The method body does not mutate File attributes.
- Note: The File.executable attribute is declared with stored_property in the class; the stored_property decorator may cache the returned boolean on first access by writing into the instance dictionary (e.g., setting self.executable). That caching behavior is a side-effect of the decorator, not of the executable function body itself.

## Constraints:
Preconditions:
- self.path must be a valid filesystem path string (File.__init__ calls resolve_file_path to ensure this).
- The caller should be aware the result reflects the OS-level execute permission for the process; it is not a guarantee that executing the file will succeed at runtime (e.g., interpreter/linker issues, missing dependencies, or incompatible binary formats are not detected by this check).

Postconditions:
- Returns a boolean indicating the current OS permission state for executing the file at self.path.
- If stored_property caches results, subsequent reads return the same boolean for the lifetime of this File instance (no automatic re-checking of underlying filesystem changes).

## Side Effects:
- Performs a filesystem metadata check via os.access (no file contents are read or written).
- No modifications to filesystem or external services.
- Potential caching side-effect if stored_property is used (see "Attributes WRITTEN").

### `src.exodus_bundler.bundling.File.elf` · *method*

## Summary:
Lazily-inspects the file at this object's path and returns True if its first four bytes match the ELF magic header (b'\x7fELF'), otherwise False. This function is designed to be used as a cached (stored_property) attribute, but in the File class it is typically shadowed by an instance attribute set in __init__.

## Description:
Known callers and lifecycle context:
- The function itself is not directly invoked by name in the repository; it is intended to serve as a stored_property that computes an ELF-format boolean on first access.
- Within the File class, most code accesses the attribute self.elf. However, File.__init__ assigns an instance attribute named "elf" (an Elf instance or None), which takes precedence over the stored_property descriptor. As a result, in normal construction of File objects the stored_property version is usually not executed.
- The stored_property will run only if an instance does not already have an "elf" key in its __dict__ (for example, if the instance is created without running File.__init__, or if the attribute was deleted before access).
- Typical intended usage (if not shadowed): used during file-inspection and bundling to decide whether to run ELF-specific parsing, dependency detection, or to build binary launchers.

Why this logic is its own method:
- Encapsulates the simple but important ELF magic-byte check in one location so callers can use a clear boolean property instead of duplicating low-level I/O logic.
- Intended to be cached via stored_property to avoid repeated file reads when the descriptor is actually used.
- Separating the detection from higher-level logic clarifies intent and keeps I/O concerns isolated.

## Args:
    None.

## Returns:
    bool
    - True: successfully opened the file at self.path and its first four bytes equal b'\x7fELF'.
    - False: successfully opened the file but its first four bytes differ (including files smaller than 4 bytes).
    - Never returns None.

Important note:
- Although this function returns a boolean when invoked, typical File instances created via File.__init__ will have self.elf set to an Elf instance or None; therefore callers reading self.elf usually receive that object rather than this boolean.

## Raises:
    MissingFileError
    - Raised when detect_elf_binary observed os.path.exists(self.path) returned False before attempting to open the file.

    FileNotFoundError
    - Propagated when the file existed during any preliminary check but disappeared before open(), or when open() fails with FileNotFoundError (race condition).

    PermissionError
    - Propagated if opening/reading the file is forbidden.

    IsADirectoryError
    - Propagated if the path exists but refers to a directory.

    OSError (other)
    - Any other low-level I/O error raised by open()/read() is propagated unchanged.

Notes on exception behavior:
- This function does not convert open()/read() exceptions into MissingFileError; callers that need robust behavior should handle both MissingFileError and FileNotFoundError/OSError.

## State Changes:
Attributes READ:
    - self.path

Attributes WRITTEN:
    - instance.__dict__['elf'] (only when the stored_property descriptor is invoked). The descriptor writes the computed boolean into the instance dict under the key "elf" so subsequent accesses return the cached value.

Important interaction with File.__init__:
- File.__init__ assigns self.elf = Elf(path, ...) or None; such assignment populates instance.__dict__['elf'] before the descriptor is ever accessed, therefore the stored_property will not be invoked for typical instances. Only instances lacking an "elf" key in their __dict__ will trigger the descriptor and cause a cached boolean to be written.

## Constraints:
Preconditions:
    - self.path must be a valid filesystem path-like object (str or os.PathLike).
    - The process should have permission to open and read the file, if it exists.

Postconditions:
    - No persistent filesystem or global state is modified.
    - If the stored_property runs, the resulting bool is cached in instance.__dict__['elf'].
    - The returned boolean reflects the ELF magic-byte check at the time of the file read.

## Side Effects:
    - Opens the file at self.path in binary mode and reads up to 4 bytes (local filesystem I/O).
    - No network access or file writes.
    - Small race window exists between existence check and open(); FileNotFoundError may still be raised even if MissingFileError was not.

### `src.exodus_bundler.bundling.File.hash` · *method*

## Summary:
Compute and return the SHA-256 digest (hex string) of the file's current contents. When accessed via the stored_property wrapper, the result is computed once on first access and then cached on the File instance.

## Description:
Known callers and context:
- File.destination (a stored_property) references this property to form a bundle path of the form ./data/<hash>. Accessing File.destination will therefore trigger hash computation on first access.
- Methods that cause the hash to be computed as part of normal bundling include:
  - File.copy (reads File.destination to determine where to copy the file in the working directory),
  - File.create_launcher (reads File.destination when preparing launcher paths),
  - File.symlink (reads File.destination when creating symlinks into the bundle).
- Typical lifecycle: invoked during bundle assembly and deduplication phases when the bundler needs a stable, content-derived identifier for placement and comparison of files.

Why this logic is its own method:
- Content hashing is a reusable operation needed in multiple places (destination generation, deduplication). Keeping it separate makes the intent explicit and enables caching via the stored_property decorator so the potentially expensive computation runs at most once per File instance.

## Args:
This method takes no explicit arguments beyond self.

## Returns:
str
- A 64-character lowercase hexadecimal string produced by hashlib.sha256 over the file bytes and returned via hexdigest().
- For an empty file, returns the SHA-256 hex for zero-length input (a valid 64-character hex string).

## Raises:
- FileNotFoundError: if self.path does not exist at the time of open().
- PermissionError: if the process lacks read permission for the file.
- OSError or its subclasses: for other I/O-related failures during open/read.
Note: the method does not catch these exceptions; they propagate to callers.

## State Changes:
Attributes READ:
- self.path (used to open and read the file contents)

Attributes WRITTEN:
- The method body does not assign any attributes directly. However, because the hash attribute is defined with stored_property, the computed digest will be cached on the File instance by the descriptor on first access. The exact storage mechanism is provided by the stored_property implementation (it caches the computed value on the instance).

## Constraints:
Preconditions:
- self.path must be a valid filesystem path referring to a file that can be opened for binary reading.
- Callers should be aware that the implementation reads the entire file into memory (f.read()), so available memory must be sufficient for the file size.

Postconditions:
- Returns a deterministic SHA-256 hex string representing the file contents at the time of the call.
- After the first successful access, the stored_property descriptor will cache that value on the instance; subsequent accesses will yield the cached digest even if the underlying file changes on disk (callers are responsible for cache invalidation if up-to-date hashes are required).

## Side Effects:
- Performs file I/O: opens self.path in binary mode and reads the entire file into memory.
- CPU and memory usage are proportional to file size because the whole file is read into memory before hashing.
- No external network calls or file writes are performed by this method itself.

### `src.exodus_bundler.bundling.File.requires_launcher` · *method*

## Summary:
Determine whether this File instance needs a launcher to execute; caches the result on first access.

## Description:
Known callers and context:
- File.__init__: accessed during object construction to compute and set self.no_symlink (the presence/absence of a required launcher determines whether an entry-point symlink may be suppressed).
- Other callers: any bundling logic that needs to decide whether to produce a launcher or a direct symlink for an entry point will evaluate this property. Typical lifecycle: evaluated early after a File is created, before packaging steps that create entry points or launchers.

Why this is a separate method:
- Encapsulates the decision logic for when to wrap an executable with a generated launcher versus exposing it directly. The determination depends on multiple File attributes (library, ELF metadata, executable bit, path heuristics) and is reused in multiple places; isolating it improves readability and allows caching via stored_property to avoid repeatedly re-evaluating file system and ELF checks.

## Args:
- None (this is a parameterless stored property on File)

## Returns:
- Returns one of:
    - True (bool): explicit signal that a launcher is required.
    - False (bool): explicit signal that a launcher is not required.
    - re.Match object: the match object returned by re.search when the path ends with or contains a shared-object suffix (e.g., ".so" or ".so.1"), which is truthy and indicates a launcher is required according to the regex check.
    - None: when the regex check does not match; this is falsy and indicates a launcher is not required.
- Note on interpretation: callers should treat the return value by truthiness: truthy => launcher required; falsy => launcher not required. The implementation intentionally returns both booleans (in early branches) and the raw re.search result in the final branch.

## Raises:
- The method itself does not explicitly raise exceptions.
- Exceptions may propagate from accessed properties used during the decision:
    - Accessing self.executable may perform os.access and can raise OSError in certain edge environments.
    - Accessing self.elf or self.elf.linker_file may raise exceptions from ELF detection or filesystem access if those operations are lazily computed (for example, file-not-found or parsing errors that are not already handled by File.__init__).
- No new exception types are created by this method.

## State Changes:
Attributes READ:
- self.library
- self.elf
- self.elf.linker_file
- self.executable
- self.elf.type
- self.entry_point
- self.path

Attributes WRITTEN:
- Caches the computed result on the instance by writing self.__dict__['requires_launcher'] (the stored_property cache). No other attributes on self are modified.

## Constraints:
Preconditions:
- No strict preconditions enforced by this method; it defensively handles None-ish self.elf and missing linker_file by returning False where appropriate.
- Best practice: the File instance should have a valid self.path (string) and sensible values for the stored properties (self.executable and self.elf) to avoid propagated errors from underlying filesystem or ELF detection routines.

Postconditions:
- After the first access, self.__dict__['requires_launcher'] will be set to the computed result (True, False, re.Match, or None) and subsequent accesses will return that cached value.
- The returned value's truthiness indicates whether a launcher is required (truthy => launcher required).

## Behavior and decision logic (implementation notes):
- Immediately return False if any of:
    - self.library is truthy (explicit library flag)
    - self.elf is falsy (no ELF detected) OR self.elf.linker_file is falsy
    - self.executable is falsy (file is not executable)
- If self.elf.type == 'executable' => return True
- If self.entry_point is truthy => return True
- Directory-path heuristics:
    - If self.path contains any of ['/bin/', '/bin32/', '/bin64/'] but does not contain any of ['/lib/', '/lib32/', '/lib64/'] => return True
    - If self.path contains any of ['/lib/', '/lib32/', '/lib64/'] but not any of ['/bin/', '/bin32/', '/bin64/'] => return False
- Fallback:
    - Return the result of re.search(r'\.so(?:\.|$)', self.path) — a truthy re.Match when the filename contains or ends with ".so" (optionally followed by a dot and more chars), otherwise None.

## Edge cases and examples:
- Path contains both '/bin/' and '/lib/' substrings: directory heuristics neutralize; decision is made by the final regex.
- Files named like 'libfoo.so.1' will match the regex and thus produce a truthy match object.
- When self.elf is None or has no linker_file, the method returns False early (no launcher).
- Because the method is cached by stored_property, any change to underlying attributes (e.g., self.library toggled) after first access will not affect the cached result unless the cache is explicitly invalidated by the caller (by deleting self.requires_launcher from the instance dict).

## Side Effects:
- Caches the decision on the File instance via the stored_property mechanism (writes to instance.__dict__).
- Accessing the property may cause underlying stored properties to be evaluated, which can perform filesystem I/O (os.access) and ELF file parsing/reads. Those operations may have I/O side effects (file system reads) and can raise filesystem-related exceptions which propagate.

### `src.exodus_bundler.bundling.File.source` · *method*

## Summary:
Returns the file's path expressed relative to the filesystem root (no leading slash for typical POSIX absolute paths). The computed string is the bundle-local "source" location and, because this attribute is decorated with stored_property on the File class, the value is computed once and then cached on the instance.

## Description:
- Known callers and lifecycle stage:
    - File.create_entry_point: joins this value with the bundle root to create the symlink target for entry points during bundle assembly.
    - File.create_launcher: used to determine where launcher files are written inside the bundle structure.
    - File.symlink: used to create or validate symlinks placed under the bundle root.
  These callers invoke this property during the bundling phase when File instances are prepared for inclusion in a bundle (copied, symlinked, or having launchers/entry points created).
- Why this logic is a separate property:
    - Centralizes and normalizes conversion of an absolute filesystem path into a bundle-local, root-relative path string needed by multiple bundling operations.
    - Being a stored_property avoids recomputing the same relative path repeatedly and ensures consistent results across the bundling pipeline.

## Args:
    None.

## Returns:
    str:
        - The result of os.path.relpath(self.path, '/').
        - Examples:
            * '/usr/bin/bash' -> 'usr/bin/bash'
            * '/' -> '.'
        - If self.path is not absolute or contains unusual components the return may include '..' segments; callers should ensure self.path is a resolved absolute path when that is required.
        - Always returns a Python str.

## Raises:
    - ValueError: May be raised by os.path.relpath in platform-specific situations (for example, on Windows when self.path and the given start ('/') are on different drives). This method does not catch that exception.
    - The method itself does not perform filesystem access and will not raise FileNotFoundError; any such errors originate elsewhere.

## State Changes:
- Attributes READ:
    - self.path
- Attributes WRITTEN:
    - The function body does not modify any File attributes.
    - Note about the decorator: In the File class this attribute is annotated with stored_property. stored_property is a lightweight non-data descriptor that computes a value on first access, caches it on the instance, and thereafter yields the cached value. That descriptor behavior causes the computed return value to be cached on the instance as a decorator-side effect (not by the function body).

## Constraints:
- Preconditions:
    - Preferably self.path is a resolved absolute filesystem path. File.__init__ typically ensures this via resolve_file_path, so callers can usually expect an absolute path.
    - The bundler is intended for POSIX-style paths; behavior on non-POSIX platforms may be platform-specific.
- Postconditions:
    - The returned string represents self.path expressed relative to '/'.
    - After first access (because of stored_property), subsequent accesses will return the cached string without recomputing.

## Side Effects:
    - No I/O, no filesystem reads/writes, and no external service calls occur inside this method.
    - The only side effect is the stored_property caching behavior described above (the descriptor will cache the computed value on the instance).

## `src.exodus_bundler.bundling.Bundle` · *class*

*No documentation generated.*

### `src.exodus_bundler.bundling.Bundle.__init__` · *method*

## Summary:
Initializes a Bundle instance by recording the working directory and chroot path and creating empty file-tracking sets; optionally creates a temporary writable working directory when requested.

## Description:
This constructor sets up the minimal internal state required for a Bundle object used by the bundling pipeline. It is invoked during the setup phase of bundling when a new bundle object is instantiated to collect files, linker-related files, and optional filesystem isolation parameters.

Known callers and lifecycle context:
- Typically called by higher-level bundling orchestration code when beginning a bundling run (for example, code that prepares a packaging operation or constructs an object that will accumulate files and produce a bundle). There are no internal callers in this function body — it is the class constructor and is expected to be invoked externally wherever a Bundle is needed.
- It runs at the initialization step of the bundling lifecycle: immediately after object construction the caller may begin adding files or invoking dependency detection and packaging operations.

Why this is a separate method:
- Constructor encapsulates initial state creation and optional temporary-directory creation plus permission fixing; isolating this logic keeps object initialization clear and ensures filesystem side effects (creating and chmod-ing a temp dir) are centralized, making later code easier to reason about and test.

## Args:
    working_directory (str | bool | None): 
        - If None (default), no working directory is created or adjusted; self.working_directory will be set to None unless another truthy non-True value is provided.
        - If True, a new temporary directory is created (using tempfile.mkdtemp) and assigned to self.working_directory. The created directory will have its permissions adjusted using the process umask (see Side Effects).
        - If a string path is provided, that value is assigned to self.working_directory as-is (no creation/modification performed by this constructor).
    chroot (str | None):
        - Path to a directory to be used as a chroot base or None. The value is stored on the instance for later use by bundling operations; this constructor does not validate or mutate the chroot path.

## Returns:
    None — the constructor initializes instance attributes and returns implicitly.

## Raises:
    - OSError (propagated) — if underlying OS calls fail, e.g. tempfile.mkdtemp fails to create a directory or os.chmod fails to set permissions. The constructor does not catch these exceptions; they propagate to the caller.
    - Any other exceptions raised by the standard library calls used here (e.g. MemoryError from tempfile) may also propagate; no additional error translation is performed in the constructor.

## State Changes:
Attributes READ:
    - working_directory (local parameter) is read to decide whether to create a temporary directory and what to assign to self.working_directory
    - (indirect) the current process umask is read and stored into a local variable before being restored

Attributes WRITTEN:
    - self.working_directory: set to the provided value or to a newly-created temporary directory when working_directory is True
    - self.chroot: set to the provided chroot argument (possibly None)
    - self.files: initialized to an empty set() for tracking added files
    - self.linker_files: initialized to an empty set() for tracking linker-specific files

## Constraints:
Preconditions:
    - No preconditions are required by the constructor beyond valid argument types compatible with the described behavior (None, bool, or str for working_directory; None or str for chroot).
    - If working_directory is True, the running process must have permission to create a temporary directory and adjust its permissions in the system temporary directory.

Postconditions:
    - After successful return, self.files and self.linker_files are empty set objects.
    - self.chroot is equal to the chroot argument passed in (possibly None).
    - self.working_directory is:
        * the string path passed in if a non-True string was provided,
        * the newly-created temporary directory path if working_directory was True,
        * or the same value passed in (usually None) if working_directory was None or another non-True falsy value.
    - If a temporary directory was created, its mode will be chmod'ed to (0o777 & ~umask) where umask is the process umask that existed before the constructor briefly changed it.

## Side Effects:
    - If working_directory is True, a new temporary directory is created on the filesystem (tempfile.mkdtemp). The directory remains present on disk; the constructor does not register automatic cleanup or deletion.
    - The process umask is briefly changed by calling os.umask(0) and then restored to its previous value; this is a transient process-global side effect, but the original umask is restored before returning.
    - The constructor calls os.chmod on the newly-created directory to set permissions using the original umask; this modifies filesystem metadata for that directory.
    - No network I/O or external service calls are made by this constructor.

### `src.exodus_bundler.bundling.Bundle.add_file` · *method*

## Summary:
Adds a filesystem path (file or directory) to the bundle's file set, updating the bundle's tracked linker candidates and dependency set as needed, and returns the File object for the added path (or None when a directory is expanded).

## Description:
This method is used during bundle composition to register one or more filesystem entries with the Bundle instance prior to creating the final bundle. Typical usage is to call add_file repeatedly for each path the bundle should include; create_bundle later reads Bundle.files to materialize the bundle contents.

Known callers / call points:
- Recursively called by itself when the provided path refers to a directory (it walks the directory and calls add_file on each contained file).
- Intended to be called by client code (or higher-level orchestration code) during the "bundle assembly" phase, before create_bundle() is invoked.

Why this logic is a separate method:
- It encapsulates file discovery, normalization via the bundle's file_factory, and the bookkeeping around ELF linkers and dependency aggregation. Keeping this behavior in one method centralizes assertion checks, recursive directory handling, and linker-selection logic so other code (and callers) need only call add_file with a path.

## Args:
    path (str): Filesystem path to the file or directory to add. Can be absolute or relative; it will be resolved by file_factory/resolve_file_path.
    entry_point (str or None): Optional entry point name for executable files. Defaults to None. When adding a directory, entry_point must be None (an assertion enforces this).

## Returns:
    File or None:
        - If path resolves to a file, returns the File instance created or obtained from the bundle's file set.
        - If path resolves to a directory, the method walks the directory, adds each file found by recursive calls, and returns None (the directory branch returns without a File).

## Raises:
    - AssertionError: If add_file is called with a directory path and a non-None entry_point (the code asserts "Directories can't have entry points.").
    - Any exception raised by self.file_factory(...) or by constructing/initializing the File object will propagate out of this method (these may include module-defined errors such as MissingFileError, InvalidElfBinaryError, DependencyDetectionError, UnsupportedArchitectureError, etc., depending on the underlying file_factory/File implementation). UnexpectedDirectoryError is handled internally (it triggers the directory walk behavior and is not propagated).

## State Changes:
    Attributes READ:
        - self.file_factory (method is invoked)
        - self.chroot (value passed through to file_factory)
        - self.files (read for membership semantics in file_factory and later used in union operations)
        - self.linker_files (checked for length and iterated)
    Attributes WRITTEN / MUTATED:
        - self.files: the method adds the created File object (self.files.add(file)) and may union-add dependency File objects (self.files |= file.elf.dependencies).
        - self.linker_files: may add a linker candidate (self.linker_files.add(file.elf.linker_file)).
        - file.elf.linker_file: in one branch the method assigns a value from self.linker_files then immediately sets file.elf.linker_file = None (this mutates the File/ELF descriptor object).
        - Note: recursive calls to self.add_file when a directory is encountered produce additional mutations to self.files and self.linker_files.

## Constraints:
    Preconditions:
        - The caller must provide a valid filesystem path accessible to the environment where this code runs.
        - If path refers to a directory (detected when file_factory raises UnexpectedDirectoryError), entry_point must be None; otherwise an AssertionError is raised.
        - The Bundle instance must have been initialized (self.files and self.linker_files must be sets; this is true for Bundle.__init__).

    Postconditions:
        - For a non-directory path: the returned File instance is present in self.files.
        - Any ELF-related bookkeeping will be updated:
            - If the File has an ELF descriptor with a linker_file, that linker is recorded in self.linker_files and the file's ELF dependencies are added to self.files.
            - If the File is ELF and does not provide a linker_file but there is exactly one linker previously recorded in self.linker_files, that single linker is associated (temporarily) so the file's ELF dependencies are added to self.files, and the file's elf.linker_file field is then set to None in the local File/ELF object.
            - If the File is ELF and there is no suitable unique linker candidate, no linker/dependency bookkeeping is performed for this file and a warning is emitted.

## Side Effects:
    - May perform filesystem traversal (os.walk) when the provided path is a directory; this reads directory entries.
    - Delegates to self.file_factory (and File construction) which may inspect file system metadata, read file contents, or perform dependency detection (these operations occur in the file_factory/File code and therefore are side effects of calling add_file).
    - Emits a warning via logger.warning when an ELF binary is encountered without a uniquely-resolvable linker candidate.
    - Mutates in-memory bundle state (self.files, self.linker_files) and may mutate attributes on the returned/created File object (e.g., file.entry_point may be preserved/updated in file_factory; file.elf.linker_file may be overwritten/cleared).

### `src.exodus_bundler.bundling.Bundle.create_bundle` · *method*

## Summary:
Writes the bundle contents into working_directory/bundles/<hash> by creating directories, copying files that must not be symlinked, creating symlinks for other files, and generating per-executable launcher files where required; the method mutates the filesystem and calls methods on the contained File objects but does not return a value.

## Description:
This method is the materialization step of a Bundle. It iterates self.files and, for each file, records the intended bundle target path, invokes entry-point creation if requested, either copies the file into the bundle (for no_symlink files) or prepares a working-area copy and creates a symlink, and groups ELF executables that require special launchers so their linker can be copied once per target directory and launchers created per-file.

Known callers / invocation context:
- Intended to be invoked after constructing a Bundle and populating it (for example, using add_file / file_factory). Typical lifecycle: create Bundle -> add_file(...) for all inputs -> create_bundle(shell_launchers=...) to produce the on-disk bundle.

Why this logic is separate:
- The method performs filesystem operations and coordinates naming/collision logic across all files. Separating materialization from file discovery and dependency resolution keeps responsibilities clear.

## Args:
    shell_launchers (bool): If True, forward shell_launcher=True to file.create_launcher calls so that launchers are built as shell launchers; defaults to False.

## Returns:
    None

## Raises:
    - OSError (or subclasses) propagated from os.makedirs, os.path, os.chmod, shutil.copy and other OS-level calls when filesystem operations fail.
    - shutil.Error may be raised by shutil.copy on some failure conditions.
    - Any exception raised by the File object's methods invoked by this method (create_entry_point, copy, symlink, create_launcher) is propagated. The exact exceptions depend on the File implementation and are not created by create_bundle itself.

## State Changes:
Attributes READ:
    - self.files: iterated to determine which files to materialize (first for-loop).
    - self.bundle_root: accessed to compute file_path = os.path.join(self.bundle_root, file.source) (first loop).
    - self.working_directory: passed to file.create_entry_point, file.copy, file.symlink, and file.create_launcher.
    - self.hash: indirectly read via self.bundle_root property (bundle_root uses self.hash).

Attributes WRITTEN:
    - None of the Bundle instance's attributes are modified by this method. (The method only calls methods on File objects and performs filesystem mutations. It does not assign to self.* anywhere in the method.)

## Constraints:
Preconditions:
    - self.working_directory must be a valid directory path (bundle_root builds paths under it).
    - Each element of self.files must provide the attributes and methods this method uses:
        * Attributes: source (str), entry_point (str or falsy), no_symlink (bool), path (str), requires_launcher (bool), elf (object or None).
        * If elf is present and used here, elf.linker_file must be an object with attributes hash (used in filenames) and path (source path to copy).
        * Methods: create_entry_point(working_directory, bundle_root), copy(working_directory), symlink(working_directory, bundle_root), create_launcher(working_directory, bundle_root, linker_basename, symlink_basename, shell_launcher=False).
    - Caller should ensure the process has permission to create directories and write files under working_directory.

Postconditions (guaranteed by the method's control flow):
    - For every file in self.files:
        * file_path = os.path.join(self.bundle_root, file.source) has been added to the internal file_paths set (this happens before any copy/symlink). This ensures the method accounts for possible name collisions across the bundle.
        * If file.entry_point is truthy: create_entry_point(self.working_directory, self.bundle_root) is called for that file (this call occurs before copy/symlink logic for that file).
        * If file.no_symlink is truthy:
            - The parent directory of file_path is created if it does not exist (os.makedirs), and shutil.copy(file.path, file_path) is called to copy the file into the bundle, and the file is not symlinked or processed for launcher creation (continue).
        * Else:
            - file.copy(self.working_directory) is called.
            - If file.requires_launcher is True: the file is grouped by key (directory, linker) where directory = os.path.dirname(file_path) and linker = file.elf.linker_file — the group is recorded in files_needing_launchers for later processing.
            - Otherwise: file.symlink(working_directory=self.working_directory, bundle_root=self.bundle_root) is called to create the symlink within the bundle.
    - After processing all files, for each group keyed by (directory, linker) in files_needing_launchers:
        * The method computes a desired linker filename directory/'linker-<linker.hash>' and, if that path is already in file_paths, appends suffixes '-2', '-3', ... until a unique path is found (the loop "while linker_path in file_paths" implements this). The chosen linker_path is added to file_paths.
        * The linker directory is created if necessary, and shutil.copy(linker.path, linker_path) copies the linker into the bundle directory.
        * For each executable file in the group:
            - Compute file_basename = file.entry_point or os.path.basename(file.path).
            - Determine a desired launcher name directory/'<file_basename>-x' and, if that path collides with an existing path in file_paths, append '-2', '-3', ... until unique (the loop "while symlink_path in file_paths").
            - The chosen symlink_path is added to file_paths.
            - Call file.create_launcher(self.working_directory, self.bundle_root, linker_basename, symlink_basename, shell_launcher=shell_launchers) to create the launcher for that executable.

## Side Effects:
    - Creates directories (via os.makedirs) and copies files (via shutil.copy) into the filesystem under self.working_directory/bundles/<hash>.
    - Calls methods on File objects that may themselves perform additional filesystem or external operations.
    - Mutates the filesystem incrementally and does not perform explicit rollback on error; if an exception is raised partway through, files/directories created earlier in the run may remain.

## Naming and Collision Resolution:
    - file_path entries added at the start prevent later creations from accidentally reusing the same filename.
    - Linker filenames: base = 'linker-<linker.hash>'; if base exists in file_paths the code tries 'linker-<hash>-2', then '-3', etc.
    - Launcher filenames: base = '<basename>-x'; if base exists in file_paths the code tries '<basename>-x-2', then '-3', etc.
    - All uniqueness checks use membership in the in-memory file_paths set built during this method.

## Example usage:
    bundle = Bundle(working_directory='/tmp/work')
    bundle.add_file('/usr/bin/someapp', entry_point='app')
    bundle.add_file('/lib/somelib.so')  # may add dependencies via file_factory
    bundle.create_bundle(shell_launchers=False)

### `src.exodus_bundler.bundling.Bundle.delete_working_directory` · *method*

## Summary:
Removes the on-disk working directory referenced by this Bundle and clears the object's working_directory attribute.

## Description:
This method performs teardown/cleanup of the Bundle's temporary working directory by delegating removal to shutil.rmtree and then setting the Bundle's working_directory attribute to None.

Known callers and context:
- There are no internal callers inside the Bundle class. The create_bundle method reads and uses self.working_directory (e.g., when copying files and creating entry points) but does not delete it.
- This method is intended to be invoked by consumer code (callers external to this class) during teardown or after a bundle has been created and any necessary files have been read/copied. Typical lifecycle stage: cleanup after bundling or when the Bundle instance is being discarded.

Why this is a separate method:
- Centralizes cleanup semantics in one place so callers do not need to directly invoke shutil.rmtree or remember to clear the attribute.
- Ensures consistent state mutation (setting working_directory to None) that prevents accidental reuse of the removed path.
- Makes it easy to override or instrument teardown behavior in subclasses or tests.

## Args:
    None

## Returns:
    None

## Raises:
    Any exception raised by shutil.rmtree(self.working_directory) is propagated to the caller. Common exceptions that may be raised include, but are not limited to:
    - FileNotFoundError: if the path referenced by self.working_directory does not exist.
    - PermissionError: if the process lacks permissions to remove files or directories inside the tree.
    - OSError / WindowsError: filesystem-level errors (e.g., open file handles on Windows preventing deletion).
    - TypeError: if self.working_directory is None or otherwise not a valid path-like object (raised by shutil.rmtree or underlying functions).
    The method does not catch or translate these exceptions; callers must handle them if needed.

## State Changes:
Attributes READ:
    - self.working_directory (read to pass to shutil.rmtree)

Attributes WRITTEN:
    - self.working_directory is set to None after removal

## Constraints:
Preconditions:
    - self.working_directory should be a path-like string (or os.PathLike) representing the directory tree to remove.
    - The caller should expect that the directory and all its contents will be removed if the call succeeds.
    - The caller should ensure it is safe to remove the directory (no other active users expect its contents to persist).

Postconditions:
    - If the call returns normally (no exception), the filesystem tree previously at the path referenced by self.working_directory has been removed (subject to underlying OS semantics), and self.working_directory is set to None.
    - If an exception is raised by shutil.rmtree, the working_directory attribute will not be set to None (the exception propagates before the assignment), so the attribute remains unchanged.

## Side Effects:
    - Performs destructive I/O: deletes files and directories under the given path on the host filesystem.
    - May affect resources external to the object (other processes that expected the directory or its contents may fail).
    - Behavior can be platform-dependent (e.g., open file handles may prevent deletion on Windows).
    - No network or external service calls are made; only local filesystem mutation occurs.

### `src.exodus_bundler.bundling.Bundle.file_factory` · *method*

## Summary:
Resolve and normalize the provided path, deduplicate by existing bundle entries, and return the corresponding File object — updating the existing File's metadata (entry point and library flag) when appropriate; otherwise construct and return a new File instance.

## Description:
This method is called when the bundling pipeline needs a canonical File object representing a filesystem path before that file is added to the bundle. Known callers:
- Bundle.add_file: invoked during the process of adding a file (or directory-recursive expansion) to the bundle; add_file calls file_factory to obtain the File object to insert into the bundle's set of files.

Typical lifecycle stage:
- Used during bundle preparation when inputs (user-supplied paths or program names) must be validated, normalized, and represented as File objects that the bundler can later read, copy, symlink, or generate launchers for.

Why this is its own method:
- Centralizes path resolution, deduplication, and simple reconciliation of per-file metadata (entry_point, chroot, library). Keeping this logic in one method avoids duplicating resolve-and-merge semantics across callers and ensures consistent assertions and File construction semantics.

## Args:
    path (str or os.PathLike):
        - A path-like identifier for the target file, or (when entry_point is provided) a program name that will be resolved by resolve_file_path.
        - Must be a value acceptable to resolve_file_path; invalid or missing paths result in exceptions propagated from resolve_file_path.
    entry_point (str or None, optional):
        - If provided, marks the file as an entry point name used when creating launchers or symlink entry names. Default: None.
    chroot (str or None, optional):
        - An identifier for the chroot context this file should be associated with. When an existing File object is found for the resolved path, this value must equal file.chroot or an assertion is raised. Default: None.
    library (bool, optional):
        - If True, mark the file as a library (non-entry) candidate. The method ensures a file is not simultaneously treated as an entry point and a library. Default: False.
    file_factory (callable or None, optional):
        - Forwarded to the File constructor as provided; used to override/customize File creation. The method does not itself invoke this callable — it simply passes it through to File(...) when constructing a new File instance.

## Returns:
    File:
        - If a File object already exists in self.files with a matching resolved path (file.path == resolved_path), that existing File instance is returned (after reconciling/merging metadata described below).
        - If no matching File exists, a new File object is constructed by calling File(path, entry_point, chroot, library, file_factory) and returned (the new File is NOT automatically added to self.files by this method; callers such as Bundle.add_file perform that insertion).
        - Edge-case returns:
            * When multiple File objects cannot logically exist with the same path in self.files (self.files is a set), next(...) returns the first matching element; the method does not attempt to merge multiple matches.

## Raises:
    MissingFileError, UnexpectedDirectoryError (propagated from resolve_file_path):
        - resolve_file_path is called at the start and will raise MissingFileError if the resolved candidate does not exist, or UnexpectedDirectoryError if the candidate is a directory (unless the caller expected directories and handles that).
    AssertionError:
        - If an existing File is found and entry_point conflicts with the existing file.entry_point (i.e., both non-empty and different), an AssertionError is raised with the message: "The entry point property should always persist, but can't conflict."
        - If an existing File is found and the supplied chroot does not equal file.chroot, an AssertionError is raised with the message: "The chroot must match."
        - If an existing File would become both an entry point and a library (file.entry_point and file.library both truthy after reconciliation), an AssertionError is raised with the message: "A file can't be both an entry point and a library."

## State Changes:
    Attributes READ:
        - self.files: iterated to find an existing File with a matching resolved path.
    Attributes WRITTEN (on self):
        - None. The Bundle object's own attributes are not modified by this method.
    Object attribute mutations (not on self):
        - If an existing File is found:
            * file.entry_point is updated in-place to file.entry_point or entry_point (i.e., if previously None/falsey, it will be set to the provided entry_point).
            * file.library is updated in-place to file.library or library (i.e., once True it remains True; otherwise set to the supplied library boolean).
        - If no existing File is found:
            * A new File instance is constructed and returned; this method does not modify that File further and does not add it to self.files — the caller is responsible for insertion.

## Constraints:
    Preconditions:
        - resolve_file_path(path, search_environment_path=entry_point is not None) must succeed (i.e., path must exist and not be a directory, or resolve_binary must locate a program).
        - When an existing File for the resolved path is present in self.files:
            * The supplied chroot must match the existing file.chroot.
            * The supplied entry_point must not conflict with an already-set file.entry_point.
            * The library flag must not produce a state where both entry_point and library are true for the same File.
    Postconditions:
        - On successful return with an existing File: the returned File object will have entry_point and library reconciled (existing values preserved when present).
        - On successful return with a newly-constructed File: the returned object is a File configured with the provided constructor arguments; self.files is unchanged by this call.

## Side Effects:
    - Calls resolve_file_path(...) which performs filesystem checks (stat-like operations) and may read environment PATH when search_environment_path is True.
    - May mutate attributes on an existing File object (entry_point, library) that is referenced elsewhere (these are in-place mutations and therefore visible to other references to the same File).
    - Does not create, delete, or write filesystem files itself, nor modify the Bundle. Any actual copy/symlink/launcher work is performed by other methods (e.g., File.copy, File.symlink, File.create_entry_point, File.create_launcher) invoked later in the bundling pipeline.

## Implementation notes / usage tips:
    - Callers that want the returned File to be part of the bundle must add the returned instance to self.files (Bundle.add_file performs this).
    - Because this method relies on resolve_file_path to normalize the path, callers can supply either explicit file paths or program names (when using entry points) and expect a canonical absolute path to be used for deduplication.
    - Be defensive when calling from contexts that might pass differing chroot values for the same filesystem path: inconsistent chroot values cause assertions.

### `src.exodus_bundler.bundling.Bundle.bundle_root` · *method*

## Summary:
Returns the canonical absolute path of the bundle directory computed from the bundle's working directory and the current bundle hash. This accessor does not modify the object's state.

## Description:
- Known callers and context:
    - Bundle.create_bundle: used when assembling files, creating entry points, copying files, creating symlinks, and building launchers to compute target file locations under the bundle directory.
    - File.create_entry_point, File.symlink, File.create_launcher and related file-manipulation code that are passed self.bundle_root to determine where files or symlinks should be placed inside the bundle.
    - Any other code that needs the filesystem location where the bundle's per-hash files are stored.
  Typical lifecycle: invoked during the bundle-assembly phase after a working directory has been created and after the bundle's files set has been populated, so that the returned path points to the location under working_directory where files for the current bundle hash should be placed.

- Rationale for being a dedicated accessor:
  Centralizes the logic that composes the bundle directory path (working_directory + "bundles" + bundle-hash) and canonicalizes it (absolute, normalized). Having this in one place ensures consistent path computation across all callers and isolates normalization behavior from other file-manipulation logic.

## Args:
    None

## Returns:
    str: An absolute, normalized filesystem path of the form:
         <absolute-working-directory>/bundles/<hash>
    Notes:
    - The returned path is purely computed (os.path.join followed by os.path.abspath and os.path.normpath); the directory may or may not exist on disk when returned.
    - The hash portion is obtained from the bundle's hash property and therefore reflects the current contents of self.files at call time.

## Raises:
    TypeError: If self.working_directory is not a str or os.PathLike (e.g., is None), os.path.join will raise a TypeError.
    Any exception raised by evaluating self.hash: the property accesses self.hash (which computes a sha256 over file.hash values). If computing that value raises (for example due to missing file.hash attributes or other errors in file objects), that exception propagates through this accessor.

## State Changes:
- Attributes READ:
    - self.working_directory
    - self.hash (property access; in turn reads self.files and individual file.hash values)
- Attributes WRITTEN:
    - None (this accessor does not mutate any attribute)

## Constraints:
- Preconditions:
    - self.working_directory must be set to a valid string or os.PathLike before calling; in typical usage the working directory is created earlier in the bundle lifecycle.
    - self.files must be in a consistent state so that self.hash can be computed (each file in self.files must expose a usable .hash attribute).
- Postconditions:
    - Returns a stable, canonical absolute path string representing where the bundle for the current hash should live under working_directory.
    - Calling this accessor does not create directories or otherwise perform filesystem I/O.

## Side Effects:
    - None. This accessor performs only pure string/path manipulations (os.path.join, os.path.abspath, os.path.normpath); it does not perform filesystem reads/writes, create directories, or modify external state.

### `src.exodus_bundler.bundling.Bundle.hash` · *method*

## Summary:
Returns a deterministic 64-character lowercase SHA-256 hexadecimal identifier for the bundle based on the set of contained files' precomputed hashes. This identifier is a read-only property used to name and locate bundle output directories without mutating the Bundle.

## Description:
Known callers and lifecycle context:
- The bundle_root property in the same class uses this property to construct the filesystem path for the bundle; thus hash is computed when the code needs the canonical bundle identifier (for example, during bundle creation, lookup, or caching).
- create_bundle and other bundle-management routines access bundle_root (and therefore this property) during packaging and launcher/linker placement.

Why this logic is its own property:
- Centralizing the bundle identity computation in a single read-only property guarantees consistent, order-independent identifiers across the codebase and avoids duplicating the sorting, joining, encoding, and hashing steps in multiple places. Exposing it as a property makes it simple to use in expressions (e.g., build paths) while signaling that it does not mutate object state.

## Args:
- None. This is an instance-level read-only property (no parameters).

## Returns:
- type: str
- description: A 64-character lowercase hexadecimal string: the SHA-256 digest of the UTF-8 encoding of the newline-separated, sorted list of file.hash strings from self.files.
- Determinism and empty-case:
    - Sorting ensures the same set of file.hash values yields the same result regardless of insertion order into self.files.
    - If self.files is empty, the method computes SHA-256 over the empty byte string and returns:
      e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

## Raises:
- AttributeError:
    - If any element of self.files does not expose a .hash attribute, attribute access while iterating will raise AttributeError.
- TypeError:
    - If any file.hash value is not a str (for example bytes, None, or another non-str type), the join operation will raise a TypeError because str.join requires string elements and the subsequent encode step expects a str-to-bytes conversion.
- Propagated iteration errors:
    - If self.files is not iterable or iteration raises an exception, that exception will propagate.

## State Changes:
- Attributes READ:
    - self.files (iterated)
    - file.hash for each file in self.files
- Attributes WRITTEN:
    - None. The property does not mutate the Bundle or contained File objects.

## Constraints:
- Preconditions:
    - self.files must be an iterable collection (typically a set) of file-like objects.
    - Each file-like object must have a .hash attribute and that attribute should be a str containing the file's precomputed hash (commonly already a hex string).
- Postconditions:
    - The returned string is a deterministic identifier for the current membership of self.files (same set of file.hash strings -> same hash).
    - The returned string is always 64 chars long and contains only lowercase hexadecimal digits.

## Side Effects:
- None. This property performs no I/O, does not change the filesystem, and does not mutate self or external objects.

## Usage notes:
- Treat this property as a pure, read-only identifier: compute it when you need a stable bundle name or key (e.g., composing bundle_root) but avoid relying on it to trigger any side effects.
- Because the value depends only on file.hash strings, ensure those are computed and stable before accessing this property.

