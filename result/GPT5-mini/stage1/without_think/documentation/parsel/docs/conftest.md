# `conftest.py`

## `docs.conftest.load_selector` · *function*

## Summary:
Load a text fixture file from this package's _static directory (or an absolute path) and return a parsel.Selector constructed from the file's UTF-8 decoded contents; any extra keyword arguments are forwarded to the Selector constructor.

## Description:
This small utility centralizes reading static fixture files and creating a parsel.Selector for downstream tests or documentation parsers.

Behavior:
- Builds input_path by joining the directory containing this module, the fixed segment "_static", and the provided filename using os.path.join(os.path.dirname(__file__), "_static", filename).
- Opens the resulting path with encoding="utf-8", reads the entire file into memory, and returns Selector(text=file_contents, **kwargs).
- Forwards all keyword arguments to parsel.Selector unchanged.

Known callers within the supplied snapshot:
- None discovered in the provided files. In typical usage this helper is invoked by tests or documentation parsing utilities that need a Selector for HTML/XML fixtures found under docs/_static.

Why extracted:
- Consolidates consistent encoding (UTF-8), canonical location (docs/_static), and Selector creation so callers do not duplicate path construction and file I/O.
- Keeps test code concise and reduces the chance of inconsistent file-reading behavior across the codebase.

## Args:
    filename (str | os.PathLike):
        Name of the file relative to this module's "_static" subdirectory, or an absolute filesystem path.
        - If filename is a relative path with nested segments (e.g., "examples/foo.html"), those segments are appended under docs/_static.
        - If filename is an absolute path (leading slash on POSIX or drive letter on Windows), os.path.join will return that absolute path and ignore the preceding directory and "_static" components (i.e., the provided absolute path bypasses the package _static directory).
        - Caller responsibility: avoid passing untrusted input to filename; the function does not perform path normalization or sandboxing.
    **kwargs:
        Any keyword arguments accepted by parsel.Selector. Typical examples: type="html" or type="xml". The exact accepted keys and their semantics are determined by parsel.Selector.

## Returns:
    parsel.Selector
        A Selector instance created from the full UTF-8 decoded contents of the resolved file. The returned Selector is ready for CSS/XPath queries per parsel's API.

Edge-case return behavior:
- On success the function always returns a Selector instance. It does not return None or partially-initialized objects.

## Raises:
    TypeError:
        If filename is not a str or os.PathLike object such that os.path.join cannot process it, a TypeError may be raised when calling os.path.join or open().
    FileNotFoundError:
        If the resolved input_path does not exist, open() will raise FileNotFoundError.
    PermissionError:
        If the process lacks permission to open the file, open() will raise PermissionError.
    IsADirectoryError:
        If input_path points to a directory rather than a file, open() will raise IsADirectoryError.
    OSError:
        Other OS-level errors from open() (for example, too many open files) may be raised as OSError or subclasses thereof.
    UnicodeDecodeError:
        If the file contents are not valid UTF-8, reading the file will raise UnicodeDecodeError.
    Exception (from parsel.Selector):
        Any exception raised by parsel.Selector when constructing the Selector (e.g., TypeError for an unexpected kwarg) is propagated.

Notes on exception provenance:
- File I/O exceptions originate from builtins.open/read. Selector-related exceptions originate from parsel.Selector constructor and are not wrapped.

## Constraints:
Preconditions:
    - The caller should pass a filename that is intended and safe to read from the filesystem; this function does not validate or sanitize path traversal.
    - The target file must be present and readable by the process.
    - Keyword arguments must conform to parsel.Selector's expectations.

Postconditions:
    - On normal return, the file descriptor used to read the file is closed (the function uses a context manager).
    - The returned Selector reflects the file's UTF-8 decoded contents.

Security considerations:
    - If filename is absolute or contains path traversal segments (e.g., "../"), os.path.join semantics may allow reading files outside docs/_static. Do not pass untrusted filenames; if callers must accept user-provided names, validate and sanitize the path (e.g., resolve and verify commonprefix or use pathlib and check parent relationships).

## Side Effects:
    - File I/O: reads the entire contents of the resolved file from the local filesystem into memory.
    - No writes are performed.
    - No network I/O, no global state mutation, and no external service interaction.
    - Memory: file content is loaded into a Python string; very large files will increase memory usage.

## Control Flow:
flowchart TD
    A[Start: call load_selector(filename, **kwargs)]
    A --> B[Compute base_dir = dirname(__file__)]
    B --> C[Compute input_path = os.path.join(base_dir, "_static", filename)]
    C --> D{Is input_path an existing file?}
    D -->|No| E[open() raises FileNotFoundError / OSError -> propagate]
    D -->|Yes| F[open(input_path, encoding="utf-8") as input_file]
    F --> G[Read entire file content into memory]
    G --> H[Call Selector(text=file_content, **kwargs)]
    H --> I{Selector construction success?}
    I -->|No| J[Propagate exception from Selector]
    I -->|Yes| K[Return Selector instance]
    K --> L[End]

## Examples:
Basic usage (HTML fixture under docs/_static):
    selector = load_selector("page_example.html")
    headings = selector.css("h1::text").getall()

Relative subpath usage:
    selector = load_selector("fragments/part1.html")
    links = selector.css("a::attr(href)").getall()

Using an absolute path (bypasses _static prefix):
    # Given "/tmp/fixture.html" exists, this will read that absolute path
    selector = load_selector("/tmp/fixture.html")

Path-like object example:
    from pathlib import Path
    selector = load_selector(Path("example.html"))

Error handling example:
    try:
        sel = load_selector("missing.html")
    except FileNotFoundError:
        # file absent: create fixture, skip test, or report failure
        handle_missing_fixture()

Sanitization recommendation (if filename may come from untrusted input):
    # Example pattern: resolve and ensure the target is within docs/_static
    from pathlib import Path
    base = Path(__file__).resolve().parent / "_static"
    candidate = (base / filename).resolve()
    if base not in candidate.parents and candidate != base:
        raise ValueError("filename resolves outside the intended _static directory")
    selector = load_selector(str(candidate))

## `docs.conftest.setup` · *function*

## Summary:
Injects the load_selector helper into a provided execution namespace so callers can access it by the key "load_selector".

## Description:
This helper is a tiny namespace-population function intended for use by test harnesses or documentation parsing tools that accept a mutable mapping (an execution namespace) and rely on pre-populated helper functions. In the provided snapshot there are no recorded callers that invoke this setup function; typical use is to pass a mapping/dict to this function during test or documentation setup so tests and doctests can call load_selector directly from the namespace.

Why this is extracted:
- Encapsulates the single responsibility of making load_selector available inside an execution namespace without duplicating the assignment site across many test files or test-framework configuration calls.
- Keeps callers (test harness configuration, doctest executors, Sybil-like tools) simple: they call a single setup routine that consistently names the helper.

See also:
- docs.conftest.load_selector for the behavior, side-effects, and error modes of the function being injected.

## Args:
    namespace (MutableMapping[str, Any]):
        A mutable mapping (for example, a dict) that accepts item assignment via namespace[key] = value.
        - The function will perform namespace["load_selector"] = load_selector.
        - Caller responsibility: provide a mapping that supports __setitem__ for string keys. Passing None or an immutable mapping will result in an exception.

## Returns:
    None
        The function performs an in-place mutation of the provided mapping and does not return a value.

## Raises:
    TypeError:
        If the supplied namespace does not support item assignment (for example, None or an immutable object), attempting namespace["load_selector"] = ... will raise a TypeError (or a similar object-specific error). This is the most common error when callers pass an inappropriate namespace.
    Exception (propagated from namespace.__setitem__):
        Any exception raised by the mapping's __setitem__ implementation will propagate (for example, a user-defined mapping might raise ValueError or a custom exception).
    NameError:
        If, in the module runtime environment, the symbol load_selector is not defined in the module/global scope, referencing it will raise NameError. (In the standard module layout this symbol is defined; this entry documents the general Python semantics.)

## Constraints:
Preconditions:
    - The caller must supply a mutable mapping that supports assignment via the indexing operator with string keys.
    - The module-level symbol load_selector must be present (normal module loading provides this).

Postconditions:
    - After successful return, namespace["load_selector"] is defined and references the load_selector callable from this module.
    - If a previous value existed under the "load_selector" key, it is overwritten.

## Side Effects:
    - Mutates the provided namespace mapping by adding or replacing the key "load_selector".
    - No file or network I/O is performed by this function itself. Any side effects originating from calling the injected load_selector (once placed in the namespace) are those documented under docs.conftest.load_selector.
    - No global state beyond the provided namespace mapping is modified by this function.

## Control Flow:
flowchart TD
    A[Start: call setup(namespace)] --> B{Is namespace a mutable mapping with __setitem__?}
    B -->|No| C[Assignment fails -> TypeError or mapping-specific exception propagates]
    B -->|Yes| D[Execute namespace["load_selector"] = load_selector]
    D --> E[Assignment succeeded]
    E --> F[Return None]
    C --> F

## Examples:
Basic usage with a plain dict:
    ns = {}
    setup(ns)
    # Now ns["load_selector"] is available and behaves as described in docs.conftest.load_selector
    selector = ns["load_selector"]("page_example.html")

Usage where the namespace is a mapping used by a doctest or parser:
    execution_namespace = {}
    setup(execution_namespace)
    # Pass execution_namespace into the test/doc parser so embedded examples can call load_selector(...)

Error handling example:
    try:
        setup(None)  # incorrect type: None does not support item assignment
    except TypeError:
        # Handle or report misconfigured test harness
        handle_bad_namespace()

Implementation note:
- The function intentionally performs a single, atomic assignment and does not validate or wrap load_selector; callers that need different key names or additional helpers should perform their own namespace manipulations before handing the namespace to the execution environment.

