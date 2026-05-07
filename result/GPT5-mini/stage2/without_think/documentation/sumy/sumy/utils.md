# `utils.py`

## `sumy.utils.normalize_language` · *function*

## Summary:
Resolve a short ISO language identifier (alpha-2 or alpha-3) to a canonical language name (lowercased) when possible; otherwise return the original input unchanged.

## Description:
This small utility attempts to normalize language identifiers by using pycountry.languages to map common short codes to their human-readable names.

Known callers within the available repository memory:
- No direct callers were discovered in the available memory snapshot. Typical use-cases: normalizing incoming language metadata (e.g., "en" or "eng") into a consistent human-readable form before downstream decisions such as selecting language-specific resources, tokenizers, or display labels.

Why this is a standalone function:
- It encapsulates the pycountry lookup and its error handling in one place so callers don't duplicate lookup semantics (two lookup forms, KeyError handling) or string-normalization (lowercasing). Extracting this logic enforces a single, testable normalization behavior across the codebase.

## Args:
    language (any): A language identifier to normalize.
        - Common expected values: ISO 639-1 two-letter codes (alpha_2) like "en", ISO 639-2/3 three-letter codes (alpha_3) like "eng".
        - The function accepts any value but makes no type conversions; passing non-string types is supported only insofar as pycountry.languages.get accepts them (and may raise).

## Returns:
    The function returns one of:
        - A string: the canonical language name lowercased (e.g., "english") if a pycountry.languages lookup succeeds for either alpha_2 or alpha_3.
        - The original input value unchanged if neither lookup succeeds.
    Notes on types and edge cases:
        - There is no strict type coercion guarantee: if the caller passes a non-string object and no lookup succeeds, that same object will be returned unchanged.
        - If a lookup succeeds, the function converts the pycountry result's name attribute to lowercase and returns that string.
        - If the first lookup (alpha_2) succeeds and the second lookup (alpha_3) also succeeds, the later successful lookup will overwrite the previous value (the function always proceeds through both lookups in sequence).

## Raises:
    - The function explicitly catches KeyError raised inside the lookup attempt and will ignore it (continue to the next lookup key).
    - Any other exceptions raised by pycountry.languages.get or by attribute access (for example TypeError, AttributeError, or other runtime errors) are not caught and will propagate to the caller.

## Constraints:
    Preconditions:
        - pycountry.languages must be installed and importable in the runtime environment.
        - Callers should preferably pass string-like language codes; passing other types may lead to exceptions from pycountry or result in the same object being returned.
    Postconditions:
        - If a pycountry lookup succeeded, the return value is a lowercase string of the language name.
        - If no lookup succeeded, the function returns exactly the input value (same object/type) unchanged.

## Side Effects:
    - None. The function performs only in-memory lookups via pycountry and does not perform I/O, mutate global variables, or call external network services.

## Control Flow:
flowchart TD
    Start --> ForLoop{"Iterate lookup_key in (alpha_2, alpha_3)"}
    ForLoop --> Try["Attempt languages.get(**{lookup_key: language})"]
    Try --> KeyErr{"KeyError raised?"}
    KeyErr -- Yes --> Continue["pass -> continue to next lookup_key"]
    KeyErr -- No --> LangFound{"lang is truthy?"}
    LangFound -- Yes --> Assign["Set language = lang.name.lower()"]
    LangFound -- No --> Continue
    Assign --> Continue
    Continue --> NextKey{"More lookup_keys?"}
    NextKey -- Yes --> ForLoop
    NextKey -- No --> Return["return language"] --> End

## Examples:
    Example A — Two-letter code:
        Input: "en"
        Behavior: languages.get(alpha_2="en") matches English -> returns "english"

    Example B — Three-letter code:
        Input: "eng"
        Behavior: alpha_2 lookup fails, languages.get(alpha_3="eng") matches English -> returns "english"

    Example C — Already a name:
        Input: "English"
        Behavior: neither alpha_2 nor alpha_3 lookups find a match -> returns "English" unchanged

    Example D — Unrecognized value:
        Input: "zzz"
        Behavior: no match -> returns "zzz" unchanged

    Example E — Non-string input and error handling:
        Input: None (or another non-string)
        Behavior: pycountry may raise TypeError or another exception; the caller should handle such exceptions. For robust use, call sites should validate inputs or wrap calls in try/except to handle unexpected types or pycountry errors.

## `sumy.utils.fetch_url` · *function*

## Summary:
Performs an HTTP GET and returns the raw response body as bytes; raises on HTTP error responses.

## Description:
This helper issues a single HTTP GET using the requests library, ensures the response status indicates success by calling response.raise_for_status(), and returns response.content (bytes). It uses contextlib.closing to ensure the response object is closed before returning.

Known callers within the provided context:
- No explicit callers are present in the provided snippet. Typically, higher-level modules that need to download remote resources (HTML fetchers, importers, parsers) call this helper as the network I/O step in their pipeline.

Why this is a separate function:
- Consolidates request construction (headers), error handling via raise_for_status, and deterministic response cleanup.
- Prevents repetition of the requests.get + raise_for_status + closing pattern across the codebase.

## Args:
    url (str):
        - URL to fetch. Required positional argument.
        - Must be a value acceptable to requests.get (e.g., a string or string-like object).
        - The call passes a module-level variable _HTTP_HEADERS as the headers argument; that variable must be defined in the module.

## Returns:
    bytes:
        - The raw response body as returned by requests.Response.content.
        - If the HTTP response has no body, an empty bytes object (b'') may be returned.

## Raises:
    requests.exceptions.HTTPError
        - Raised by response.raise_for_status() when the HTTP response status indicates an error.
    requests.exceptions.RequestException (and its subclasses)
        - Any network-level error raised by requests.get (connection errors, DNS failures, timeouts, invalid URL, SSL errors, etc.) will propagate to the caller.
    NameError
        - If the module-level identifier _HTTP_HEADERS is not defined when the function is called, a NameError will be raised when evaluating the headers argument.

## Constraints:
Preconditions:
    - _HTTP_HEADERS must be defined in the module namespace before calling this function.
    - The caller must supply a URL acceptable to requests.get.
    - Network connectivity is required for the HTTP request to succeed.
    - The function does not pass a timeout argument to requests.get (the call is made without an explicit timeout).

Postconditions:
    - On success (no exception), the returned value is a bytes object containing the response body and the Response resource has been closed.
    - On exception, no bytes are returned and the raised exception indicates the failure mode.

## Side Effects:
    - Performs outbound network I/O (HTTP GET).
    - May produce observable effects on the remote server (e.g., server logs).
    - Does not modify files, global variables, or perform logging by itself.

## Control Flow:
flowchart TD
    Start --> DoGet[Call requests.get(url, headers=_HTTP_HEADERS)]
    DoGet -->|network error| NetErr[requests.exceptions.RequestException raised]
    DoGet --> Resp[Response received]
    Resp --> RaiseStatus[Call response.raise_for_status()]
    RaiseStatus -->|error status| HTTPErr[requests.exceptions.HTTPError raised]
    RaiseStatus -->|success status| ReturnBytes[Return response.content (bytes)]
    ReturnBytes --> End

## Examples:
Example usage pattern (concrete, minimal):
    try:
        data = fetch_url('https://example.org/resource')
    except requests.exceptions.HTTPError as e:
        # Handle HTTP error responses (e.g., 404, 500)
        handle_http_failure(e)
    except requests.exceptions.RequestException as e:
        # Handle network-level issues (connection errors, timeouts, etc.)
        handle_network_failure(e)
    except NameError:
        # _HTTP_HEADERS was not defined in the module
        fix_headers_definition()
    else:
        # On success, `data` is bytes. Decode or parse as needed.
        text = data.decode('utf-8', errors='replace')
        process_text(text)

Recommendations:
    - If callers need bounded latency, wrap this call with a timeout-aware and/or retry/backoff mechanism or modify the helper to pass a timeout to requests.get.
    - Ensure _HTTP_HEADERS is present and contains any required request headers (User-Agent, Accept, etc.) before invoking this function.

## `sumy.utils.cached_property` · *function*

## Summary:
Caches the result of a single-argument instance getter on the instance by storing it as a private attribute and exposes it as a read-only property.

## Description:
This helper converts an instance method (a getter that accepts only self) into a property that computes its value once per instance and then reuses the cached value on subsequent accesses. It constructs an instance attribute named by prefixing "_cached_property_" to the getter function's name and stores the computed result there on the first access.

Known callers within this repository snapshot:
    - No direct call sites or usages were discovered in the available repository fragment. Typical usage is to decorate expensive, idempotent instance getters (for example, computed descriptors derived from instance state) so that they are evaluated lazily and cached.

Why this logic is extracted:
    - Separates the caching policy from the getter implementation, enabling any instance getter to become a cached, read-only property without duplicating caching code.
    - Keeps getter functions pure of caching concerns and centralizes the single-access memoization pattern.

## Args:
    getter (callable): A function defined on the class that accepts exactly one parameter (self) and returns a computed value to be cached. The decorator assumes this signature; other signatures are unsupported.

## Returns:
    property: A built-in property object whose fget will:
        - On first access for a given instance:
            * Call getter(self) and capture the returned value.
            * Store that value on the instance using setattr(instance, "_cached_property_" + getter.__name__, value).
            * Return the computed value.
        - On subsequent accesses:
            * Return the previously stored value retrieved with getattr(instance, "_cached_property_" + getter.__name__).

    Edge cases:
        - If the instance already has an attribute with the same "_cached_property_<name>" key before any access, that existing value will be returned and the getter will not be invoked.
        - If the getter raises an exception during its first invocation, the attribute is not set and the exception propagates to the caller; a subsequent access will attempt to call the getter again.

## Raises:
    - Any exception raised by getter(self) is propagated to the caller; the decorator does not catch or wrap exceptions.
    - AttributeError or TypeError will surface if the getter is called with an incompatible instance (e.g., wrong binding), as with any method call.

## Constraints:
    Preconditions:
        - The decorated function must be an instance method that accepts a single positional argument (self).
        - The target instances must allow attribute assignment via setattr (for example, have a writable __dict__ or a suitable __setattr__ implementation). If the instance blocks assignment to the chosen cache attribute, setattr may raise, causing the property access to fail.
    Postconditions:
        - After a successful first access, the instance will have a new attribute named "_cached_property_" + getter.__name__ whose value equals the getter's returned value.
        - Subsequent accesses will not call the getter again unless the cached attribute is removed or overwritten.

## Side Effects:
    - Mutates the instance by creating or overwriting the attribute "_cached_property_" + getter.__name__ to store the computed value.
    - No I/O operations, network access, or global state modification occur as a result of the decorator itself (side effects originate only from the getter implementation).
    - No interaction with external services.

## Control Flow:
flowchart TD
    A[Access property on instance] --> B{Instance has attribute "_cached_property_<name>"?}
    B -- Yes --> C[Return stored value via getattr]
    B -- No --> D[Call getter(self)]
    D --> E{getter raises exception?}
    E -- Yes --> F[Propagate exception; do not set cache attribute]
    E -- No --> G[setattr(instance, "_cached_property_<name>", value)]
    G --> C

## Examples (described usage steps; no code definitions included):
    - Typical successful usage:
        1. Define an instance method that computes a value from expensive work or from other instance attributes.
        2. Decorate that method with this cached-property decorator.
        3. On first access via instance.property, the method is invoked, its result stored on the instance under the internal cache key, and the result returned.
        4. On subsequent accesses, the stored value is returned directly without invoking the method again.

    - When the getter fails:
        1. First access invokes the getter.
        2. If the getter raises, the exception is propagated outward and no cache attribute is set.
        3. A subsequent access will retry invoking the getter until it succeeds (or until some external code sets the cache attribute).

    - Manual cache invalidation:
        - Remove or reassign the attribute named "_cached_property_<name>" on the instance to force recomputation on the next access.

    - Important usage notes:
        - Do not use this decorator for methods that rely on non-idempotent side effects on each call (unless caching that single result is desired).
        - Avoid naming collisions on instances that intentionally use attributes starting with "_cached_property_".

## `sumy.utils.expand_resource_path` · *function*

## Summary:
Builds an absolute filesystem path into the package's bundled "data" directory by combining the installed sumy package directory, the fixed "data" segment, and the provided relative path fragment — unless the provided path is absolute, in which case the absolute path is returned per os.path.join semantics.

## Description:
This small utility resolves a filesystem path that points to a resource shipped with the sumy package. It computes the package root directory from the currently loaded sumy module, converts the fixed "data" segment and the provided path to strings via the project's to_string helper, and joins them into a single path.

Known callers within the codebase:
- No direct callers were discovered in the scanned snapshot. Typical callers (if present) would be modules responsible for loading bundled resources (e.g., corpora loaders, default model files, or example data readers).

Why this logic is a separate function:
- Centralizes and documents the assumption that package resources live under a "data" subdirectory.
- Prevents duplication of sys.modules / __file__ resolution and platform-specific path joining across the codebase.
- Makes unit-testing and potential future adjustments (e.g., changing the data layout) easier by having a single, well-documented point of change.

## Args:
    path (str or bytes or any to_string-acceptable value): Relative path fragment under the "data" directory (for example "corpora/en.xml" or "models/stopwords.txt").
        - The function calls to_string on the provided value; therefore the argument must be convertible by that helper (commonly str or bytes).
        - If path is an empty string (''), the result points to the "data" directory itself.
        - If path is an absolute path string (platform-specific; e.g., starts with '/' on POSIX or contains a drive/root on Windows), os.path.join semantics apply (see Returns and Control Flow).

## Returns:
    str: A filesystem path string produced by joining, in order:
        1) abspath(dirname(sys.modules["sumy"].__file__)),
        2) to_string("data"),
        3) to_string(path)
    Important behaviors and edge cases:
        - If path is relative, the returned path will be located under the package data directory (package_root/data/<path>).
        - If path is an absolute path, os.path.join will ignore the earlier components and return path (after joining), so the returned path will effectively be the provided absolute path converted via to_string.
        - The function does not test whether the returned path exists on disk.
        - The returned path is not additionally normalized beyond the effects of abspath called on the package directory; if callers need a normalized, canonical path they should call os.path.normpath or os.path.abspath on the returned value themselves.

## Raises:
    KeyError:
        - If "sumy" is not present in sys.modules, accessing sys.modules["sumy"] raises KeyError.
    AttributeError:
        - If the module object found at sys.modules["sumy"] does not have a __file__ attribute, accessing module.__file__ will raise AttributeError.
    TypeError / ValueError (propagated from to_string):
        - If to_string cannot convert the provided path or "data" to a string, its implementation may raise TypeError or ValueError; these propagate out of this function.
    Notes:
        - These exceptions are raised implicitly by the operations used; the function contains no explicit raise statements.

## Constraints:
    Preconditions:
        - The sumy package should already be importable and present in sys.modules (typically by doing import sumy before calling this function).
        - The module object for sumy must have a filesystem __file__ attribute pointing to its installed location.
        - The provided path must be compatible with to_string.

    Postconditions:
        - The function returns a string value without performing any I/O.
        - If the provided path is relative, the returned path will start with the package data directory segment; if the provided path is absolute, the returned path will be that absolute path (not prefixed by the package directory).

## Side Effects:
    - None: the function only reads from sys.modules and performs in-memory string/path operations. It does not read or write files, network, stdout, or mutate global state.

## Control Flow:
flowchart TD
    Start --> ReadSysModules["Read sys.modules['sumy']"]
    ReadSysModules --> IfMissing{"Is 'sumy' in sys.modules?"}
    IfMissing -- No --> RaiseKeyError["KeyError raised to caller"]
    IfMissing -- Yes --> GetModule["module = sys.modules['sumy']"]
    GetModule --> AccessFile{"Does module have __file__?"}
    AccessFile -- No --> RaiseAttributeError["AttributeError raised to caller"]
    AccessFile -- Yes --> ModuleDir["dirname(module.__file__)"]
    ModuleDir --> AbsDir["directory = abspath(ModuleDir)"]
    AbsDir --> ToData["data_segment = to_string('data')"]
    ToData --> ToPath["path_segment = to_string(path)"]
    ToPath --> Join["result = join(abs_dir, data_segment, path_segment)"]
    Join --> Return["Return result (no existence check)"]
    Return --> End

## Examples:
- Typical relative path usage:
    resource_path = expand_resource_path('corpora/example_corpus.xml')
    # resource_path -> "<abs path to installed sumy>/data/corpora/example_corpus.xml"
    # Check existence before opening:
    # if not exists(resource_path): handle_missing_resource()

- When caller may not have imported sumy yet:
    try:
        p = expand_resource_path('models/stopwords.txt')
    except KeyError:
        import sumy
        p = expand_resource_path('models/stopwords.txt')

- Absolute path passed (important behavior):
    # Suppose '/tmp/external.dat' is an absolute path
    p = expand_resource_path('/tmp/external.dat')
    # p will be '/tmp/external.dat' (the provided absolute path), not "<sumy>/data/tmp/external.dat"

- Handling invalid path types:
    try:
        p = expand_resource_path(12345)  # likely will cause to_string to raise
    except (TypeError, ValueError) as exc:
        raise RuntimeError('Invalid resource path') from exc

## `sumy.utils.get_stop_words` · *function*

## Summary:
Retrieve and parse the packaged stop-word list for a language identifier and return it as an immutable frozenset of stop-words.

## Description:
This function normalizes the provided language identifier, loads the corresponding stop-words resource file shipped with the "sumy" package, and parses its contents into a frozenset using the shared parse_stop_words logic.

Known callers within the codebase:
    - No direct callers were discovered in the available memory snapshot.
    - Typical usage context: called by language-specific preprocessing, tokenizers, or summarization pipelines when they need a stop-word set for filtering tokens (triggered during initialization or when selecting language resources).

Why this is a standalone function:
    - Encapsulates three responsibilities in a single, reusable place:
        1. Normalizing arbitrary language identifiers to the canonical form via normalize_language.
        2. Locating and reading the packaged stop-words resource using pkgutil.get_data.
        3. Converting raw resource content into a frozenset via parse_stop_words.
    - Keeping these steps together prevents duplication of resource-loading, error mapping (IOError -> LookupError), and parsing semantics in multiple callers.

## Args:
    language (any):
        - Expected: string-like language identifier (commonly ISO 639-1 two-letter codes like "en", or ISO 639-2/3 three-letter codes like "eng"), or already-normalized language names.
        - The function accepts any value that normalize_language can accept; normalize_language may return a string or the original value unchanged.
        - No default.

## Returns:
    frozenset:
        - An immutable set of stop-word strings parsed from the package resource file "data/stopwords/<language>.txt", where <language> is the normalized language identifier returned by normalize_language.
        - Typical value: frozenset of non-empty strings (each element corresponds to a trimmed stop-word line in the file).
        - Edge cases:
            * If the stop-words file exists but contains only empty or whitespace-only lines, parse_stop_words semantics may include the empty string in the frozenset (see parse_stop_words docs).
            * If parse_stop_words raises an exception (e.g., UnicodeDecodeError for invalid bytes), that exception is propagated.

## Raises:
    LookupError:
        - Raised if pkgutil.get_data("sumy", "data/stopwords/%s.txt" % language) raises an IOError (resource not available or unreadable).
        - Exact message: "Stop-words are not available for language %s." where %s is the normalized language value.

    Propagated exceptions (not caught here):
        - Any exception raised by normalize_language (for example, TypeError from pycountry if invalid non-string input is used) will propagate.
        - Any exception raised by parse_stop_words (e.g., UnicodeDecodeError when bytes cannot be decoded) will propagate unchanged.

## Constraints:
    Preconditions:
        - The "sumy" package must include stop-word resource files at data/stopwords/<language>.txt for the desired languages.
        - normalize_language must be available in the module namespace and behave as documented (may perform pycountry lookups).
        - parse_stop_words must be available and able to handle the bytes or text returned by pkgutil.get_data.

    Postconditions:
        - On successful completion, returns a frozenset representing the stop words parsed from the package resource for the normalized language.
        - If the stop-words resource is not available, the function raises LookupError and does not return a value.

## Side Effects:
    - No explicit I/O beyond reading a packaged resource via pkgutil.get_data (this is read-only access to package data).
    - No mutation of global state, no network calls, no stdout/stderr output.
    - Any side effects originate from called helpers (normalize_language or parse_stop_words) if those helpers have side effects (they do not in the provided memory).

## Control Flow:
flowchart TD
    Start --> Normalize[normalize_language(language)]
    Normalize --> TryLoad{try: pkgutil.get_data("sumy", "data/stopwords/%s.txt" % language)}
    TryLoad -->|IOError raised| RaiseLookup[raise LookupError("Stop-words are not available for language %s." % language)]
    TryLoad -->|data obtained| Parse[parse_stop_words(stopwords_data)]
    Parse --> Return[frozenset stop-words returned]
    RaiseLookup --> End
    Return --> End

    %% Note: exceptions from normalize_language or parse_stop_words are not caught here and therefore propagate to the caller.

## Examples:
- Typical successful use:
    # Caller supplies a language code; normalize_language returns "english"
    stop_words = get_stop_words("en")
    # stop_words is a frozenset({'the', 'and', 'or', ...})

- Handling missing stop-word resource:
    try:
        stop_words = get_stop_words("unsupported-lang")
    except LookupError as e:
        # Fallback to an empty set or a default language
        stop_words = frozenset()

- Propagated decode error example:
    # If the resource file exists but contains invalid bytes and parse_stop_words raises UnicodeDecodeError
    try:
        stop_words = get_stop_words("some-language")
    except UnicodeDecodeError:
        # handle decoding problem (for example, log and fallback)
        stop_words = frozenset()

## `sumy.utils.read_stop_words` · *function*

## Summary:
Read a stop-word file from disk (binary mode), parse its contents, and return an immutable set of stop words.

## Description:
Known callers within the codebase:
    - No direct callers were discovered in the provided context. Typical consumers are language processing components that need a frozenset of stop words for token filtering, e.g., tokenizers, stop-word filters, or language-specific pipelines.

Typical context / pipeline stage:
    - Used at resource-loading time when stop-word lists are stored as plain-text files packaged with the project or supplied by the user.
    - Typical pipeline: locate a stop-words file on disk -> call read_stop_words(path) -> obtain frozenset -> supply to downstream text processing components.

Why this is a separate function:
    - Separates file I/O concerns (opening and reading a file in binary) from parsing/normalization logic (handled by parse_stop_words). This keeps file access isolated and ensures consistent parsing semantics by delegating normalization and conversion to a single parsing routine.

## Args:
    filename (str or os.PathLike): Path to the stop-words file on disk.
        - Expected to point to a readable regular file.
        - The path may be absolute or relative to the current working directory.
        - Interdependencies: The function always opens the file in binary mode ("rb") and passes the raw bytes to parse_stop_words; callers should provide files encoded as UTF-8 (or otherwise decodable by the module helper to_unicode) to avoid decode errors.

## Returns:
    frozenset:
        - An immutable set of text strings (module text type) produced by parse_stop_words applied to the file contents.
        - Semantics and edge cases derive from parse_stop_words:
            * Empty file -> empty frozenset().
            * Duplicate lines collapse to a single element.
            * Lines consisting only of whitespace become the empty string "" in the result (because parse_stop_words includes truthy lines then applies rstrip()).
            * Trailing whitespace is removed from each included line; leading/internal whitespace is preserved.
        - The file handle is closed before the function returns.

## Raises:
    - FileNotFoundError: If the named file does not exist when attempting to open it.
    - PermissionError: If the file cannot be opened due to permission issues.
    - OSError / IOError: Any low-level I/O error raised by open() or read() (e.g., path is a directory).
    - UnicodeDecodeError: If the file's bytes cannot be decoded by parse_stop_words' to_unicode helper (e.g., invalid UTF-8), this error is propagated.
    - Any exception raised by parse_stop_words (since the function forwards the file bytes directly), e.g., unexpected type-conversion errors.

## Constraints:
Preconditions:
    - The caller must provide a valid filesystem path to a readable file.
    - If the file contains non-UTF-8 bytes, callers should be prepared to handle UnicodeDecodeError or ensure the file is encoded in UTF-8 or another encoding supported by to_unicode.

Postconditions:
    - On success, returns a frozenset of parsed stop-word strings.
    - The file resource is closed and no file descriptor is leaked.
    - No global state is modified.

## Side Effects:
    - Performs local file I/O: opens the given path in binary mode and reads its entire contents into memory.
    - Memory usage equals the file size (contents are read at once).
    - No network access, no modifications to external persistent state, and no global variable mutations.

## Control Flow:
flowchart TD
    Start((Start)) --> OpenFile[Try open(filename, "rb")]
    OpenFile -->|open fails (FileNotFoundError,PermissionError,OSError)| PropagateOpenErr[Propagate exception]
    OpenFile -->|open succeeds| Read[read bytes = open_file.read()]
    Read --> CloseFile[close file handle (context manager)]
    Read --> CallParse[Call parse_stop_words(bytes)]
    CallParse -->|parse raises (UnicodeDecodeError, other)| PropagateParseErr[Propagate exception]
    CallParse -->|parse succeeds| ReturnResult[Return frozenset]
    PropagateOpenErr --> End((End with exception))
    PropagateParseErr --> End((End with exception))
    ReturnResult --> End((End successfully))

## Examples:
- Typical usage (happy path):
    # Given a path to a UTF-8 encoded stop-words file:
    words = read_stop_words("/path/to/stopwords_en.txt")
    # `words` is a frozenset of strings suitable for membership checks:
    # 'the' in words  -> True  (if "the" was listed)

- Handling missing file or permission issues:
    try:
        words = read_stop_words("missing.txt")
    except FileNotFoundError:
        # fallback behavior: use empty set or provide default stop words
        words = frozenset()

- Handling decode errors for malformed files:
    try:
        words = read_stop_words("maybe-not-utf8.txt")
    except UnicodeDecodeError:
        # decode failed; choose recovery strategy (skip file, re-encode, or raise)
        words = frozenset()

## `sumy.utils.parse_stop_words` · *function*

## Summary:
Convert raw multi-line stop-word text into an immutable frozenset of stop words by decoding to text, splitting into lines, filtering, and trimming trailing whitespace.

## Description:
Known callers and typical usage:
    - Called after retrieving stop-word lists (e.g., reading a .txt file, loading a package resource, or receiving downloaded content) to produce a lookup-friendly set used by tokenizers, filters, or language processors.
    - Typical pipeline stage: resource retrieval -> parse_stop_words(data) -> use frozenset in stop-word filtering.

Why this is a separate function:
    - Encapsulates the universal normalization logic (text decoding via to_unicode, line splitting, empty-line filtering, trailing-whitespace trimming, and immutability via frozenset) so all callers get consistent behavior without duplication.

## Args:
    data (any):
        - Raw stop-word content. Expected values:
            * Text string (module text type) with one stop word per line.
            * Bytes object containing UTF-8 encoded text.
            * Any object convertible to text by the module helper to_unicode.
        - There is no default; the caller must supply the data. to_unicode determines how the input is converted to text and may raise exceptions (see Raises).

## Returns:
    frozenset:
        - Immutable set of strings (module text type). Each element corresponds to a non-empty input line after applying rstrip() to remove trailing whitespace.
        - Important edge cases:
            * Lines that are exactly empty (zero-length) are falsey and therefore excluded by the "if w" filter.
            * Lines that contain only whitespace characters (e.g., "   ", "\t") are truthy before rstrip; after w.rstrip() they become the empty string "". Such empty-string elements will be included in the returned frozenset if any input line is whitespace-only.
        - Duplicate lines collapse into a single set element due to set semantics.
        - If there are no included lines, the function returns an empty frozenset().

## Raises:
    - UnicodeDecodeError:
        * If `data` is bytes that cannot be decoded as UTF-8 by to_unicode, the UnicodeDecodeError is propagated.
    - Any exception raised by to_unicode:
        * For non-bytes, non-text inputs, to_unicode may delegate to instance conversion which can raise arbitrary exceptions; such exceptions propagate out of parse_stop_words unchanged.
    - parse_stop_words performs no additional explicit exception raising.

## Constraints:
Preconditions:
    - to_unicode must be available in the module namespace and should return a text string when given `data`.
    - Callers should provide bytes that are UTF-8 encoded if passing bytes to avoid UnicodeDecodeError.

Postconditions:
    - The return value is a frozenset containing the parsed stop-word strings (possibly including the empty string if any input line consisted only of whitespace).
    - No global state is modified.

## Side Effects:
    - The function itself does not perform I/O, network access, or mutate external state.
    - Indirect side effects can occur only if to_unicode triggers user-defined conversion hooks that have side effects; such effects originate from to_unicode, not from parse_stop_words.

## Control Flow:
flowchart TD
    Start((Start)) --> A[Call to_unicode(data)]
    A -->|to_unicode raises| Err[Propagate exception]
    A -->|returns text|string| B[Call text.splitlines()]
    B --> C[Iterate over each line `w`]
    C --> D{Is `w` truthy?}
    D -->|No (empty string)| C
    D -->|Yes| E[Compute trimmed = w.rstrip()]
    E --> F[Add trimmed to accumulator set (may be "")]
    F --> C
    C --> G[Finish iteration and convert accumulator to frozenset]
    G --> Return[Return frozenset]

## Examples:
- Standard multi-line text:
    content = "the\nand\nbut\n\nor  \n"
    # Returned frozenset: {'the', 'and', 'but', 'or'}

- UTF-8 bytes:
    bcontent = b"der\nund\naber\n"
    # Returned frozenset: {'der', 'und', 'aber'}

- Whitespace-only line produces empty-string element:
    content = "a\n   \nb\n"
    # The middle line is truthy before rstrip; w.rstrip() == ""
    # Returned frozenset: {'a', 'b', ''}  (contains the empty string)

- Handling invalid bytes (error handling):
    try:
        bad = b'\xff'  # not valid UTF-8
        words = parse_stop_words(bad)
    except UnicodeDecodeError:
        # handle decode failure, e.g., fallback to empty set
        words = frozenset()

Notes:
    - splitlines() treats all common newline sequences uniformly (\\n, \\r\\n, \\r). Newline characters are not included in returned lines.
    - Leading whitespace and internal spacing are preserved by this function; if callers need normalized casing or leading/trailing stripping beyond rstrip, they should apply that normalization separately.

## `sumy.utils.ItemsCount` · *class*

## Summary:
Represents a callable selector that, given a sequence, returns the first N items where N is configured at construction time. N can be specified as an absolute count (int or numeric string), a percentage string (e.g., "25%"), or a numeric type (int/float).

## Description:
ItemsCount is a small utility object intended to be instantiated with a single value that determines how many items to select from a sequence when the instance is later called with that sequence.

Typical scenarios:
- Pass an ItemsCount instance as a parameter to consumer code that requests a "slice" of the first items from a list/tuple-like collection.
- Use it when you need a reusable selector whose selection logic (absolute count or percentage) is configured once and applied repeatedly.

Known callers/factories:
- Any code that expects a callable taking a sequence and returning a subsequence (slice of the original). This class does not depend on other parts of the repository; it is a small, standalone helper.

Motivation and responsibility boundary:
- Encapsulates the logic of converting flexible user input (e.g., "10%", "5", 3.0) into an integer count and returning the leading subsequence.
- It does not validate the sequence beyond using len() and slicing; it does not modify the input sequence and does not manage resources.

## State:
Attributes (internal, private):
- _value (type: str | int | float)
  - Description: The original configuration determining how many items to return.
  - Valid values:
    - A string ending with '%' (e.g., "10%") to indicate a percentage of the sequence length.
    - A numeric string without '%' (e.g., "5") representing an absolute count.
    - An int or float used as an absolute count (the float is converted to int via int()).
  - Invariants:
    - _value is stored as-is with no coercion in __init__.
    - No normalization or validation is performed at construction; validation occurs at call-time in __call__.
    - There is no internal state that changes across calls; ItemsCount is immutable after __init__ (attribute is prefixed with underscore but not enforced).

## Lifecycle:
Creation:
- Instantiate with one required positional parameter:
  - ItemsCount(value)
  - value: must be one of the accepted types listed in State (string, int, float).
- Example creation forms (conceptual):
  - ItemsCount("10%")
  - ItemsCount("5")
  - ItemsCount(3)
  - ItemsCount(2.0)

Usage:
- Call the instance with a single argument "sequence" (any object supporting len() and slicing, e.g., list, tuple, str, other sequence-like containers).
- Execution path inside __call__:
  - If _value is a string:
    - If it ends with '%': interpret the prefix as an integer percentage; compute count = max(1, total_count * percentage // 100); return sequence[:count].
    - Otherwise: convert the whole string to int and return sequence[:int(string)].
  - If _value is an int or float: convert to int and return sequence[:int(_value)].
  - If _value is any other type: the implementation constructs a ValueError object but does not raise it (see Known bug below); the method then returns None implicitly.
- No explicit cleanup or destruction is required.

Destruction:
- No resources to free. Instances are plain objects without context-manager behavior or close() methods.

Known bug / implementation note:
- For unsupported _value types (neither string_types nor (int, float)), the implementation executes the expression ValueError("...") but does not raise it. That means __call__ will return None instead of raising an exception. This is likely unintended and should be corrected (raise ValueError(...)) if callers expect an exception for invalid configuration.

## Method Map:
A simplified call-flow (Mermaid flowchart representation):

flowchart TD
    A[ItemsCount(value) constructed] --> B[__call__(sequence)]
    B --> C{_value is a string?}
    C -- yes --> D{endswith '%' ?}
    D -- yes --> E[percentage = int(prefix)]
    E --> F[count = max(1, len(sequence) * percentage // 100)]
    F --> G[return sequence[:count]]
    D -- no --> H[return sequence[:int(_value)]]
    C -- no --> I{_value is int or float?}
    I -- yes --> J[return sequence[:int(_value)]]
    I -- no --> K[construct ValueError(...) but do not raise]
    K --> L[implicit return None]

## Behavior details, edge cases and constraints:
- Sequence requirements:
  - The object passed to __call__ must support len() and slicing (sequence[:n]). If it does not, calls to len(sequence) or sequence[:n] may raise TypeError or other exceptions native to the object.
- Percentage strings:
  - The percentage prefix is parsed using int(self._value[:-1]). If the prefix is not a valid integer (e.g., "a%") or empty ("%" produces empty prefix), int(...) will raise ValueError which propagates to the caller.
  - Percentage computation uses integer arithmetic: total_count * percentage // 100; final count is max(1, computed_value) so it never returns zero as the chosen count (the max ensures at least a 1 is requested). Note: slicing a sequence[:1] on an empty sequence returns an empty sequence.
- Numeric strings and numeric types:
  - Strings without '%' are converted via int(...) and may raise ValueError if the string is not a valid integer representation.
  - Float values are converted to int using Python's int() conversion (truncation toward zero).
  - Negative numeric values are accepted and passed to slicing as negative indices (sequence[: -3] semantics apply).
- Empty sequence:
  - For percentage inputs, computed count can be 1 even on an empty sequence; sequence slicing semantics mean sequence[:1] on an empty sequence returns the empty sequence.
- Unsupported _value types:
  - As implemented, unsupported types result in no exception being raised and an implicit None return from __call__ (see Known bug).

## Raises:
- Exceptions that may propagate from __call__:
  - ValueError:
    - Raised by int(...) conversions if the percentage prefix or numeric string cannot be parsed as an integer (e.g., ItemsCount("x%") or ItemsCount("abc")).
    - Note: for unsupported _value type branch, the code constructs a ValueError but does not raise it — so in that branch __call__ returns None rather than raising.
  - TypeError or other exceptions:
    - May be raised by len(sequence) or sequence slicing if the passed "sequence" does not implement these operations.
- __init__ does not raise under normal circumstances (it only stores the value). Any validation failures occur at call-time.

## Example (usage patterns and expected results):
- Conceptual usages (illustrative, not function/class definitions):

1) Absolute count with integer
- Instantiate: value = 3
- Behavior: calling the instance with [10,20,30,40] returns [10,20,30]

2) Absolute count with numeric string
- Instantiate: value = "2"
- Behavior: returns first 2 items; invalid string (e.g., "two") will raise ValueError during int conversion.

3) Percentage selection
- Instantiate: value = "50%"
- For sequence of length 10 -> percentage = 50 -> computed count = max(1, 10 * 50 // 100) = 5 -> returns first 5 items.
- For sequence of length 1 and "10%" -> computed count = max(1, 1*10//100 = 0) => 1 -> returns first 1 item (slice may be shorter if sequence is empty).

4) Float value
- Instantiate: value = 2.9
- Behavior: int(2.9) -> 2 -> returns first 2 items.

5) Unsupported value type (known-bug behavior)
- Instantiate: value = None (or a list/dict)
- Behavior: current implementation constructs a ValueError object but does not raise it and thus __call__ returns None implicitly. This is likely an implementation bug; callers should not rely on an exception being raised for invalid types.

## Representation:
- __repr__ returns a string formatted as "<ItemsCount: <value!r>>", wrapped by to_string(...) to provide compatibility between unicode/bytes across Python versions.

### `sumy.utils.ItemsCount.__init__` · *method*

## Summary:
Stores the provided configuration value on the instance as the private attribute that will later determine how many items to select.

## Description:
This constructor is invoked when creating an ItemsCount instance (e.g., ItemsCount("10%"), ItemsCount(3)). Typical callers are factory or setup code that prepare a reusable selector to be passed into consumer code which expects a callable that, when invoked with a sequence, returns the leading subsequence. The constructor intentionally performs no validation or coercion; all parsing and validation of the stored value occur later in the instance's __call__ method. Keeping initialization minimal (assignment only) separates object creation from input parsing, allowing lightweight, safe instantiation and deferring error-prone parsing to the point of use.

Known callers / context:
- Any code that constructs an ItemsCount to configure a selector for subsequent repeated use.
- Creation typically occurs at configuration time or when parsing user input; the resulting instance is later used in a pipeline step that slices sequences.

Rationale for being a separate method:
- Encapsulates instance initialization and makes the object immutable in practice (no automatic normalization), leaving parsing/validation to __call__ so that creation cannot fail due to transient parsing errors and objects remain cheap to create.

## Args:
    value (any): The configuration determining how many items to select. Common and expected types:
        - str: either a percentage string ending with '%' (e.g., "25%") or a numeric string (e.g., "5")
        - int: absolute count
        - float: absolute count (will be truncated to int by __call__)
    Note: __init__ accepts any object and does not enforce type constraints; invalid types are handled (or cause errors) only when the instance is later called.

## Returns:
    None

## Raises:
    None — this constructor does not raise exceptions. Any parsing or conversion errors occur later in __call__.

## State Changes:
Attributes READ:
    - None

Attributes WRITTEN:
    - self._value: stores the provided value exactly as passed (no coercion)

## Constraints:
Preconditions:
    - None enforced by this method. Callers may assume the instance stores the provided value.

Postconditions:
    - After return, self._value exists on the instance and is identical (by assignment) to the value argument.
    - No other attributes are created or modified.

## Side Effects:
    - None. The method does not perform I/O, network calls, logging, or mutate objects other than assigning to self._value.

### `sumy.utils.ItemsCount.__call__` · *method*

## Summary:
Returns the first N items from the provided sequence determined by the instance's configured value, without modifying the instance.

## Description:
This callable encapsulates the logic for truncating or selecting a prefix of a sequence according to the ItemsCount instance's _value:

- If _value is a string that ends with "%", the prefix before '%' is parsed as an integer percentage P and the method returns the first max(1, floor(len(sequence) * P / 100)) items.
- If _value is a numeric string (no trailing '%'), it is converted to int and that many items are returned.
- If _value is an int or float, it is converted to int and that many items are returned.

Known callers / usage context:
- There are no explicit callers in the provided snippet. Typical usage is as a truncation policy passed into higher-level code that needs to select a top-K or proportional subset from a list of items (for example, selecting top sentences/items in a summarization pipeline). Making this behavior a callable class centralizes parsing, validation, and selection semantics so callers need only call instance(sequence) to apply the policy.

Why this is its own method:
- Consolidates parsing rules (percent vs numeric), enforces a minimum 1 item for percentage mode, and isolates edge-case handling (invalid formats, large counts). This improves reusability and testability compared to inlining the logic at each call site.

## Args:
    sequence (Sequence): Any object supporting __len__() and slicing via sequence[:n] (e.g., list, tuple, str).
        - Required. No default.
        - Allowed: any sliceable sequence type. If sequence lacks len() or slicing, TypeError will be raised by Python operations.

## Returns:
    A slice of the provided sequence (sequence[:n]) where n is computed from self._value.
    - If n >= len(sequence), returns the full sequence (slicing semantics).
    - If n is negative, Python slicing semantics apply and the returned slice will exclude items from the end (e.g., n == -1 returns sequence[:-1]).
    - If sequence is empty, an empty slice is returned.
    - If self._value is of an unsupported type, the current implementation returns None due to a bug (see Raises / Notes).

## Raises:
    ValueError:
        - Raised by int(...) when parsing non-integer strings:
            * Percentage mode: int(self._value[:-1]) will raise ValueError for inputs like "12.5%" or "a%".
            * Numeric string mode: int(self._value) will raise ValueError for inputs like "abc".
        - Converting float('nan') to int raises ValueError.
    OverflowError:
        - Converting float('inf') (or an extremely large float) to int may raise OverflowError.
    TypeError:
        - If the provided sequence does not implement __len__ or slicing, the underlying len(sequence) or sequence[:n] will raise TypeError.
    Note (implementation bug):
        - When self._value is neither a string_types instance nor an int/float, the code constructs a ValueError object but does not raise it (it executes ValueError("...") without the raise keyword). Consequently, the method returns None silently instead of raising an error. The intended behavior is almost certainly to raise the ValueError.

## State Changes:
    Attributes READ:
        - self._value: read to determine parsing mode and numeric value.
    Attributes WRITTEN:
        - None. The method does not modify self or external objects.

## Constraints:
    Preconditions:
        - self._value must be present (set at initialization). It should be:
            * a string (percentage format "P%" or numeric string "N") or
            * a numeric type (int or float).
        - The provided sequence must support len(sequence) and slicing sequence[:n].
    Postconditions:
        - The instance remains unchanged.
        - The returned value is a slice of the original sequence determined by the interpreted count, except in the buggy unsupported-type branch where None is returned.

## Side Effects:
    - No I/O or network access.
    - No mutation of the input sequence or other external objects.
    - Side-effect risks from conversions: int(...) may raise ValueError or OverflowError that propagate to the caller.

## Edge cases and examples:
    - _value = "30%" with sequence length 10 -> n = max(1, 10*30 // 100) = 3 -> returns first 3 items.
    - _value = "0%" with sequence length 10 -> n = max(1, 0) = 1 -> returns first item (percentage mode enforces minimum 1).
    - _value = "-10%" with sequence length 10 -> percentage parsed as -10 -> n = max(1, 10 * -10 // 100) = max(1, -1) = 1 -> returns first item.
    - _value = "5" -> returns first 5 items; if sequence has fewer than 5 items, returns entire sequence.
    - _value = -2 -> sequence[:int(-2)] == sequence[:-2] (Python negative-slicing semantics apply).
    - _value = "12.5%" -> int("12.5") in percentage parsing raises ValueError.
    - _value = float('inf') -> int(float('inf')) raises OverflowError.

## Implementation note / Recommended fix:
    - Fix the unsupported-type branch to raise the constructed ValueError instead of discarding it. Replace:
          ValueError("Unsuported value of items count '%s'." % self._value)
      with:
          raise ValueError("Unsupported value of items count '%s'." % self._value)
    - Consider validating and normalizing self._value at __init__ time (e.g., pre-parsing percent strings or rejecting malformed inputs) to fail fast and simplify __call__.

### `sumy.utils.ItemsCount.__repr__` · *method*

## Summary:
Returns the library-canonical textual representation of the ItemsCount instance that includes the current internal _value; this representation is suitable for debugging and logging and follows the module's to_string conversion policy.

## Description:
Known callers and context:
- The built-in repr() and interactive REPL when an ItemsCount instance is inspected.
- Logging or debugging code that formats or records objects (e.g., logging.debug(items_count)).
- Any code that includes an ItemsCount instance inside a container or formatted string which implicitly calls repr() on its members.
- Lifecycle stage: invoked when the instance is being inspected or reported (diagnostics, error messages, or developer-oriented output). It is not part of the object's primary functional pipeline (i.e., it does not affect how the object slices sequences).

Why this logic is its own method:
- Implements Python's standard object representation protocol so that repr(items_count) yields a consistent, human-readable, and library-canonical value.
- Keeps representation logic centralized and separate from operational methods (like __call__), so debugging and logging produce stable output even if other behavior changes.
- Uses the shared to_string helper to honor the library's PY3/PY2 compatibility policy for string/bytes return type.

## Args:
    self (ItemsCount):
        - The instance whose representation is requested.
        - No additional parameters.

## Returns:
    str or bytes:
        - The result of to_string("<ItemsCount: %r>" % self._value).
        - On a Python-3 (PY3=True) runtime this will be the module text type (typically str).
        - On a Python-2 compatibility mode (PY3=False) this may be a bytes object, as produced by to_string.
        - Example outputs:
            * "<ItemsCount: 10>"
            * "<ItemsCount: '25%'>"
        - Edge cases:
            * If self._value's repr() produces unusual or multi-line text, that exact repr() output is embedded inside the angle-bracket wrapper.
            * If to_string raises (encoding/decoding errors or other conversion errors), no value is returned (the exception propagates).

## Raises:
    AttributeError:
        - If the instance does not have the attribute _value (e.g., malformed or partially-initialized instance).
    Any exception raised by repr(self._value):
        - If calling repr(self._value) raises an exception, it propagates directly.
    Any exception raised by to_string:
        - to_string delegates to to_unicode or to_bytes; exceptions from those functions (e.g., UnicodeDecodeError, TypeError) propagate through __repr__ unchanged.

## State Changes:
    Attributes READ:
        - self._value
    Attributes WRITTEN:
        - None (this method does not modify the instance state)

## Constraints:
    Preconditions:
        - The instance must have been initialized so that self._value exists and holds the intended value.
        - The module-level helper to_string must be available and correctly configured for the runtime compatibility mode.
    Postconditions:
        - No mutation to self or external state occurs.
        - The returned string/bytes reflects the current value of self._value (as produced by repr(self._value)) wrapped in "<ItemsCount: ...>".

## Side Effects:
    - No I/O, network access, or mutation of objects outside self.
    - The only observable effects are the computation of repr(self._value) and running the to_string conversion (which may perform encoding/decoding work internally).
    - Any side effect originates from the called helpers (repr on the contained object or to_string) and not from this method itself.

