# `update_checking.py`

## `onlinejudge_command.update_checking.describe_status_code` · *function*

## Summary:
Return a concise, human-readable HTTP status string combining the numeric status code and its standard reason phrase (for example, "200 OK").

## Description:
This utility formats an HTTP response status by looking up the standard reason phrase from the Python standard library mapping and concatenating it with the numeric code.

Known callers:
- No direct callers were discovered in the provided module snapshot. Typical call sites are places that need to present or log HTTP results (update-check logic, CLI output, diagnostic messages, or error logs) after receiving an HTTP response.

Responsibility boundary:
- This function is strictly a presentation helper: it centralizes the formatting of "<code> <reason>" and deliberately does not perform HTTP requests, perform defensive lookups, or provide fallback strings for unknown codes. Callers are responsible for handling unknown or non-standard status codes before calling this function if they want graceful fallbacks.

## Args:
    status_code (int):
        The HTTP status code to describe.
        - Expected type: int (function is annotated with int).
        - Typical/expected values: 100–599 (the standard HTTP status code range). However, the function accepts any integer that is present as a key in http.client.responses.
        - Allowed values: any integer key that exists in http.client.responses.
        - Interdependencies: None.

## Returns:
    str:
        A formatted string "<code> <reason>" where:
        - <code> is the decimal representation of status_code.
        - <reason> is the reason phrase obtained from http.client.responses[status_code].
        Examples:
            - Input 200 -> "200 OK"
            - Input 404 -> "404 Not Found"

        All successful returns produce a non-empty string containing the code, a single separating space, and the reason phrase.

## Raises:
    KeyError:
        Raised when status_code is not a key in http.client.responses.
        - Trigger: the implementation performs a direct indexing (http.client.responses[status_code]) which raises KeyError for unknown integer codes.
        - Example: describe_status_code(700) -> KeyError (700 not in the mapping).

    TypeError:
        Raised when the provided status_code is not usable as a dictionary key (e.g., an unhashable value such as a list) or when a non-integer, non-hashable type is passed.
        - Trigger: dict key lookup with an unhashable key raises TypeError.
        - Example: describe_status_code([200]) -> TypeError (lists are unhashable).

    Note:
        The function does not swallow or convert exceptions; callers who require tolerant behavior should perform their own checks or use a defensive lookup pattern (http.client.responses.get).

## Constraints:
    Preconditions:
        - The caller should prefer to pass an integer within the standard HTTP range (100–599) or otherwise ensure the code exists in http.client.responses if they expect a successful return.
        - http.client.responses must be available and behave like the standard library mapping (usually true in CPython).

    Postconditions:
        - If no exception is raised, the return value is a non-empty string formatted as "<status_code> <reason>".
        - The function does not modify global state or external resources.

## Side Effects:
    - None. The function performs a pure lookup and string formatting.
    - No network access, file I/O, logging, or mutation of external state.

## Control Flow:
flowchart TD
    Start[Start: receive status_code] --> IsHashable{Is status_code hashable?}
    IsHashable -- No --> RaiseTypeError[Raise TypeError]
    IsHashable -- Yes --> InResponses{status_code in http.client.responses?}
    InResponses -- No --> RaiseKeyError[Raise KeyError]
    InResponses -- Yes --> GetReason[reason = http.client.responses[status_code]]
    GetReason --> Format[Return "<status_code> <reason>"]
    RaiseTypeError --> End
    RaiseKeyError --> End
    Format --> End

## Examples:
    # Example 1: happy path (import shown for clarity)
    import http.client
    try:
        s = describe_status_code(200)
        # s == "200 OK"
    except (KeyError, TypeError) as e:
        # not expected for well-formed integer codes in the standard range
        raise

    # Example 2: handling unknown/edge status codes
    import http.client
    try:
        s = describe_status_code(700)
    except KeyError:
        # Provide a fallback or generate a custom message
        s = "{} {}".format(700, "Unknown Status")

    # Example 3: defensive pattern to avoid exceptions entirely
    import http.client
    code = 599
    reason = http.client.responses.get(code, "Unknown Status")
    s = "{} {}".format(code, reason)
    # This yields "599 Unknown Status" even if 599 is absent from http.client.responses

## `onlinejudge_command.update_checking.request` · *function*

## Summary:
Performs a single HTTP request using a provided requests.Session, logs the request and status, optionally raises for HTTP error status codes, and returns the requests.Response.

## Description:
This helper centralizes the logic for issuing HTTP requests from the update-checking subsystem so callers do not repeat logging, redirect detection, and error-handling boilerplate.

Known callers in the available snapshot:
- No direct callers were discovered in the provided module snapshot. Typical call sites are:
    - the module's update-check logic that polls a remote endpoint for release/version information,
    - CLI commands that fetch remote metadata,
    - diagnostic or telemetry code that needs to log HTTP responses.

Why this is a separate function:
- Responsibility is limited to issuing the HTTP request, applying default request options (allow_redirects=True), logging request/response metadata, running a human-readable status formatter (describe_status_code), and optionally raising for HTTP error statuses. Extracting this keeps callers focused on high-level control flow (when to check) and leaves the low-level request/logging behavior centralized and consistent.

## Args:
    method (str):
        - HTTP method to use. Allowed values: 'GET' or 'POST'.
        - Type: str.
        - Constraint: the function asserts the method is exactly 'GET' or 'POST'; passing any other value raises AssertionError.
    url (str):
        - Target URL to request.
        - Type: str.
    session (requests.Session):
        - A requests.Session instance used to perform the network request. Caller is responsible for creating/configuring the session (timeouts, headers, auth, adapters, etc.).
        - Type: requests.Session.
    raise_for_status (bool, optional):
        - If True (default), the function will call resp.raise_for_status(), which raises requests.HTTPError for 4xx/5xx responses.
        - If False, the response is returned regardless of status code and the caller inspects status as needed.
        - Type: bool. Default: True.
    **kwargs:
        - Any additional keyword arguments are forwarded directly to session.request(method, url, **kwargs).
        - Common forwarded kwargs include params, data, json, headers, timeout, allow_redirects, etc.
        - Note: The function sets a default for allow_redirects=True if the caller does not provide allow_redirects explicitly; an explicit allow_redirects in kwargs overrides the default.

## Returns:
    requests.Response
    - The Response object returned by session.request after the request completes.
    - Behavior details:
        - If the request completes normally, the Response returned is the same object produced by requests.Session.request.
        - If raise_for_status is True and the response status indicates an HTTP error (4xx or 5xx), resp.raise_for_status() will raise requests.HTTPError; in that case no Response is returned.
        - If session.request itself raises an exception (network error, timeout, connection error, etc.) that exception propagates (typically a subclass of requests.RequestException).

## Raises:
    AssertionError
        - If method is not 'GET' or 'POST' (trigger: the function's assert statement).
    requests.RequestException (or subclass)
        - Any exception raised by session.request (network issues, timeouts, invalid URL, etc.) will propagate unchanged.
        - Examples: requests.ConnectionError, requests.Timeout, requests.InvalidURL.
    requests.HTTPError
        - If raise_for_status is True and resp.raise_for_status() determines the response indicates an HTTP error (4xx or 5xx), it raises requests.HTTPError.
    KeyError, TypeError (from describe_status_code)
        - The function calls describe_status_code(resp.status_code) to produce a human-readable status line for logging.
        - describe_status_code can raise KeyError if resp.status_code is not present in http.client.responses, or TypeError if resp.status_code is an unhashable type; such exceptions will propagate.
        - Note: these failures are unlikely for well-formed integer status_code values delivered by requests, but are documented for completeness.

## Constraints:
Preconditions:
    - session must be a valid requests.Session (or compatible object exposing a request(method, url, **kwargs) method).
    - method must be either 'GET' or 'POST'; callers should pass a correct string to avoid AssertionError.
    - url must be a string acceptable to requests (well-formed URL).

Postconditions:
    - On successful return, a requests.Response has been obtained from the network (or cache if the session uses caching) and returned to the caller.
    - The function logs the request line, optionally the request data (if provided in kwargs), any redirect (if resp.url differs from the requested url), and a human-readable status line via describe_status_code.
    - If raise_for_status was True, either the function returned a 2xx/3xx response or it raised a requests.HTTPError for 4xx/5xx responses.

## Side Effects:
    - Network I/O: performs an HTTP(S) request via the provided requests.Session.
    - Logging: emits log messages via the module-level logger (info and debug). Specifically:
        - INFO: "<METHOD>: <url>"
        - DEBUG: "data: <repr(data)>" if data was passed in kwargs
        - INFO: "redirected: <resp.url>" if resp.url != url
        - INFO: result of describe_status_code(resp.status_code) (e.g., "200 OK")
    - No file I/O or persistent global state mutation is performed by this function itself.

## Control Flow:
flowchart TD
    Start[Start] --> AssertMethod{method in ['GET','POST']?}
    AssertMethod -- No --> RaiseAssertion[Raise AssertionError]
    AssertMethod -- Yes --> SetAllow[kwargs.setdefault('allow_redirects', True)]
    SetAllow --> LogReq[logger.info("%s: %s")]
    LogReq --> DataDebug{is 'data' in kwargs?}
    DataDebug -- Yes --> LogData[logger.debug("data: ...")]
    DataDebug -- No --> CallReq
    LogData --> CallReq[resp = session.request(method, url, **kwargs)]
    CallReq --> RedirectCheck{resp.url != url?}
    RedirectCheck -- Yes --> LogRedirect[logger.info('redirected: %s', resp.url)]
    RedirectCheck -- No --> SkipRedirectLog
    LogRedirect --> LogStatus
    SkipRedirectLog --> LogStatus
    LogStatus[logger.info(describe_status_code(resp.status_code))] --> RaiseForStatus{raise_for_status is True?}
    RaiseForStatus -- Yes --> MaybeRaise[resp.raise_for_status() (may raise requests.HTTPError)]
    RaiseForStatus -- No --> ReturnResp
    MaybeRaise --> ReturnResp[return resp]
    ReturnResp --> End[End]

## Examples:
# Example 1: basic usage (raise_for_status default True)
session = requests.Session()
try:
    resp = request('GET', 'https://example.com/update.json', session)
    # At this point resp is a requests.Response for a successful (non-HTTP-error) request.
    payload = resp.json()
except AssertionError:
    # method was not 'GET' or 'POST'
    raise
except requests.HTTPError as e:
    # HTTP error status (4xx/5xx) occurred and raise_for_status was True
    handle_http_error(e)
except requests.RequestException as e:
    # Network-level error (timeout, DNS failure, connection error, invalid URL, etc.)
    handle_network_error(e)
except (KeyError, TypeError) as e:
    # Rare: describe_status_code raised while formatting status for logging.
    # This indicates an unexpected resp.status_code shape or value.
    handle_unexpected_status_format(e)

# Example 2: inspect non-2xx responses without raising
session = requests.Session()
resp = request('GET', 'https://example.com/status', session, raise_for_status=False, timeout=5)
if resp.status_code >= 400:
    # handle error based on application logic without exceptions being raised automatically
    logger.warning('non-success status: %d', resp.status_code)
else:
    process_success(resp)

# Example 3: POST with data and explicit allow_redirects
session = requests.Session()
try:
    resp = request('POST', 'https://example.com/api/submit', session, data={'k':'v'}, allow_redirects=False)
    # If server returns a redirect, the request will not follow it because allow_redirects=False was passed explicitly.
except requests.RequestException as e:
    # handle network or HTTP errors
    raise

## `onlinejudge_command.update_checking.get_latest_version_from_pypi` · *function*

## Summary:
Fetches the latest published version string of a package from PyPI (with an 8-hour caching layer stored in the user's cache directory) and returns that version as a string.

## Description:
This function is responsible for obtaining the currently published version of a given PyPI package. It first checks a JSON cache file in the user's cache directory to avoid frequent network requests; if the cached entry for the package is present and younger than the configured update interval (8 hours), it returns the cached version. Otherwise it requests the package metadata JSON from PyPI, extracts the version field, updates the cache, and returns the fetched version. If an HTTP/network error occurs while fetching, it returns the sentinel version string '0.0.0' and still writes the cache entry with the timestamp.

Known callers within the codebase:
- No specific call sites were present in the provided snippet. Typical callers are CLI or background update-check flows that want to compare the installed package version with the latest PyPI version (for example, a "check for updates" command or startup check in the command-line tool).

Why this logic is extracted:
- The function encapsulates the responsibilities of fetching, parsing, caching, and error-tolerant fallback for PyPI version lookup. Extracting it prevents duplication of caching and network-handling logic across the codebase and provides a single place to adjust caching strategy, logging, and network behavior.

## Args:
    package_name (str):
        The PyPI package name to query (e.g., 'online-judge-tools').
        - Must be a non-empty string representing the package identifier used on PyPI.
        - No additional validation is performed on the string by this function (invalid names will either result in a network error or in PyPI returning a response without the expected fields).

## Returns:
    str:
        The version string for the latest release of the package on PyPI.
        Possible return values:
        - A semantic-version-like string extracted from the PyPI JSON at data['info']['version'] (e.g., '1.2.3').
        - The literal '0.0.0' when a requests.RequestException occurs during the network fetch (network failure is treated as non-fatal; this sentinel indicates an unknown/failed lookup).
        - A previously cached version string when a valid, unexpired cache entry exists.

## Raises:
    Any exceptions raised while writing the cache file or creating directories (e.g., OSError, PermissionError, IOError):
        - The function creates parent directories and writes the JSON cache file near the end; these filesystem operations are not protected by a try/except inside the function and will propagate to the caller.
    Any other unexpected exceptions not explicitly caught by the function (e.g., NameError if the request helper is missing):
        - The function catches broad exceptions only around loading the cache and specifically catches requests.RequestException around the network request; exceptions outside those guarded locations will propagate.

## Constraints:
    Preconditions:
        - The caller should ensure that user_cache_dir is a valid Path-like location and writable by the current process if persisting the cache is required.
        - package_name should be a valid PyPI package identifier string; otherwise the behavior depends on the remote response (missing fields or error responses).
    Postconditions:
        - On success or error, the cache file (user_cache_dir / "pypi.json") will contain an entry for package_name with keys:
            - 'time': int(timestamp) representing when the entry was stored
            - 'version': the version string returned by this call (possibly '0.0.0' on network error)
        - The function returns a string (never None).

## Side Effects:
    Network:
        - Performs an HTTP GET to 'https://pypi.org/pypi/{package_name}/json' via the code-path request('GET', pypi_url, session=requests.Session()). This causes outbound network I/O.
    Filesystem:
        - Reads from and writes to a JSON cache file at user_cache_dir / "pypi.json".
        - Ensures the parent directory of the cache file exists (creates it with parents=True, exist_ok=True).
    Logging:
        - Emits debug messages when loading or storing the cache, warning on cache load failure, and error-level logging for requests.RequestException errors.
    No other global state mutations are made by this function beyond the cache file and logging.

## Control Flow:
flowchart TD
    Start --> CheckCacheExists{cache file exists?}
    CheckCacheExists -- Yes --> TryLoadCache[try: load JSON cache]
    TryLoadCache --> CacheHasPackage{cache contains package_name and entry not expired?}
    CacheHasPackage -- True --> ReturnCachedVersion[return cached version]
    CacheHasPackage -- False --> FetchRemote[fetch JSON from PyPI]
    CheckCacheExists -- No --> FetchRemote
    FetchRemote --> TryParse[try: parse resp.content -> data['info']['version']]
    TryParse -- success --> value=version
    TryParse -- requests exception --> value='0.0.0'
    TryParse --> UpdateCache[cache[package_name] = {time: now, version: value}]
    UpdateCache --> EnsureDir[create parent dir if necessary]
    EnsureDir --> WriteCache[write JSON cache file]
    WriteCache --> ReturnValue[return value]
    ReturnCachedVersion --> End
    ReturnValue --> End

## Examples:
- Typical usage (happy path):
    version = get_latest_version_from_pypi('online-judge-tools')
    # version will be a string like '1.2.3' when the lookup succeeds or a cached value.

- Handling the '0.0.0' sentinel (network failure):
    version = get_latest_version_from_pypi('some-package')
    if version == '0.0.0':
        # The function encountered a network-level failure while fetching.
        # Treat this as "unknown" rather than as a real package version.
        handle_lookup_failure()

- Handling filesystem write errors (caller-side catch):
    try:
        version = get_latest_version_from_pypi('online-judge-tools')
    except (OSError, PermissionError) as e:
        # Cache write or directory creation failed (e.g., permission issue).
        # Decide whether to retry, warn the user, or continue without cache.
        warn_user_and_continue()

## `onlinejudge_command.update_checking.is_update_available_on_pypi` · *function*

## Summary:
Return whether a newer release of the given PyPI package exists than the provided installed version (True when a later version is available on PyPI).

## Description:
This function compares the supplied installed version against the latest version available on PyPI and returns True if the PyPI version is strictly greater.

Known callers within the codebase:
- No concrete call sites were present in the provided snippets. Typical callers are:
  - CLI commands or startup checks that implement an "update check" (for example, a command-line tool which warns the user if an upgrade is available).
  - Background or periodic update-checking flows that decide whether to prompt the user to upgrade.

Why this logic is extracted:
- It encapsulates the version comparison responsibility at a single place, centralizing the choice of comparison routine (distutils.version.StrictVersion) and the integration with the network/cache helper get_latest_version_from_pypi. Keeping this logic separate avoids code duplication and makes it straightforward to change version-comparison semantics or error handling in one place.

## Args:
    package_name (str):
        The PyPI package identifier to query (e.g., 'online-judge-tools').
        - Must be a non-empty string. Invalid package names will lead to network errors or unexpected responses from PyPI inside the delegated fetch function.
    current_version (str):
        The installed/current version string to compare against PyPI.
        - Must be a version string accepted by distutils.version.StrictVersion (numeric "major.minor[.patch]" style). Examples accepted: '1.2', '1.2.3'. Non-conforming strings (for example, containing 'rc', 'dev', or other non-numeric qualifiers) will cause StrictVersion to raise ValueError.

Notes on parameter interdependencies:
- package_name is only used to fetch the latest version via get_latest_version_from_pypi(package_name); there is no further validation here.
- current_version must be parseable by StrictVersion for the comparison to succeed.

## Returns:
    bool:
        True if and only if the latest version string retrieved from PyPI compares greater than the supplied current_version according to distutils.version.StrictVersion.
        Possible outcomes:
        - True: PyPI latest version > current_version.
        - False: PyPI latest version <= current_version, or the PyPI lookup returned the sentinel '0.0.0' (see behavior below) and that sentinel is not greater than current_version.

Edge cases:
- If get_latest_version_from_pypi returns the sentinel value '0.0.0' (which indicates a network fetch failure), this function will compare current_version against '0.0.0' and typically return False (i.e., do not report an update). This makes network failures conservative: they do not indicate an available update.

## Raises:
    ValueError:
        Raised when either current_version or the fetched PyPI version string cannot be parsed by distutils.version.StrictVersion. StrictVersion accepts a narrow numeric form (e.g., '1.2.3'); non-numeric qualifiers can cause ValueError.
    Any exceptions propagated from get_latest_version_from_pypi:
        - get_latest_version_from_pypi may raise filesystem-related exceptions (e.g., OSError, PermissionError, IOError) when creating/writing the cache file. Those exceptions are not caught here and will propagate to the caller.

Notes:
- Network-related errors during the PyPI fetch are handled inside get_latest_version_from_pypi (which returns '0.0.0' on request failures) and thus do not surface as RequestException here.

## Constraints:
Preconditions:
    - The caller should pass a current_version string valid for StrictVersion parsing when a strict numeric comparison is desired.
    - The runtime environment must allow get_latest_version_from_pypi to access the user cache directory; otherwise the underlying function may raise filesystem exceptions.

Postconditions:
    - The function returns a boolean and does not mutate global state itself.
    - Any side effects (network I/O and cache file updates) are performed by get_latest_version_from_pypi and therefore may have occurred when this function returns.

## Side Effects:
This function delegates to get_latest_version_from_pypi(package_name) and therefore may cause:
    - Network I/O: an HTTP GET to PyPI to fetch package metadata (if the cache is absent or stale).
    - Filesystem I/O: reading and/or writing a JSON cache file in the user's cache directory (user_cache_dir / "pypi.json").
    - Logging calls performed by the delegated function.
This function itself performs no direct file or network I/O beyond calling the helper.

## Control Flow:
flowchart TD
    Start --> ParseCurrent[StrictVersion(current_version)]
    ParseCurrent -- ValueError --> RaiseValueError1[raise ValueError]
    ParseCurrent --> FetchLatest[get_latest_version_from_pypi(package_name)]
    FetchLatest --> ParseLatest[StrictVersion(latest_version_str)]
    ParseLatest -- ValueError --> RaiseValueError2[raise ValueError]
    ParseLatest --> Compare[a < b?]
    Compare -- True --> ReturnTrue[return True]
    Compare -- False --> ReturnFalse[return False]
    ReturnTrue --> End
    ReturnFalse --> End

## Examples:
- Basic usage (happy path):
    try:
        if is_update_available_on_pypi('online-judge-tools', '1.2.3'):
            notify_user_upgrade_available()
    except ValueError:
        # Either the installed version or PyPI returned a non-StrictVersion string.
        # Decide whether to fallback to a different comparison method or skip the check.
        fallback_or_log()

- Handling cache/write errors (caller-side catch):
    try:
        available = is_update_available_on_pypi('some-package', '0.9.0')
    except (OSError, PermissionError) as e:
        # Underlying cache write failed in get_latest_version_from_pypi.
        # Decide whether to warn the user or continue silently.
        handle_cache_error(e)

- Behavior on transient network failure:
    # get_latest_version_from_pypi returns '0.0.0' when it cannot fetch from PyPI.
    # This function will then compare '0.9.0' (current) against '0.0.0' and return False.
    available = is_update_available_on_pypi('some-package', '0.9.0')  # -> False

## `onlinejudge_command.update_checking.run_for_package` · *function*

## Summary:
Returns whether the given installed package is already up-to-date (True) and logs a warning and upgrade hint when a newer PyPI release is available (returns False).

## Description:
This small orchestration function checks whether an update is available for a PyPI package by delegating the comparison logic to is_update_available_on_pypi(package_name, current_version). It inverts that boolean to produce an "is up-to-date" result. If an update is detected, it logs a warning containing the package name, the installed version, and the latest PyPI version (the latter is retrieved via get_latest_version_from_pypi(package_name)), and logs an informational pip command the user can run to upgrade.

Known callers and typical trigger contexts:
- CLI startup or command handlers that want to warn users about newer releases (for example, a "check for updates" step executed at tool startup or invoked explicitly by a subcommand).
- Background or periodic update-checking flows that determine whether the user should be prompted to upgrade.

Why this logic is extracted:
- It centralizes the user-facing behavior for the update check: compute up-to-date boolean, log a concise warning + actionable instruction if not up-to-date. Keeping this small orchestration separate from the lower-level network/caching (get_latest_version_from_pypi) and comparison logic (is_update_available_on_pypi) prevents duplication of logging/decision responsibilities and makes tests and callers simpler.

## Args:
    package_name (str):
        - The PyPI package identifier to check (e.g., 'online-judge-tools').
        - Must be a non-empty string. Invalid package names will cause the delegated fetch/comparison helpers to behave unpredictably or raise network/parse errors.

    current_version (str):
        - The currently installed version string for the package (e.g., '1.2.3').
        - This string is passed to is_update_available_on_pypi, which expects a version parseable by distutils.version.StrictVersion if strict numeric comparison is being used. If it is not parseable, a ValueError may be raised by the helper and will propagate.

Notes on interdependencies:
- run_for_package itself does not parse or validate version strings; instead it relies on is_update_available_on_pypi to perform the comparison and on get_latest_version_from_pypi to obtain the latest version string when logging an available update.

## Returns:
    bool:
        - True: the installed package is considered up-to-date (no newer release detected on PyPI).
        - False: a newer release is available on PyPI (an update is available). In this case the function also logs a warning and an informational pip upgrade command.

Behavioral details:
- The boolean is computed as the logical negation of is_update_available_on_pypi(package_name, current_version).
- The function always returns a boolean and never returns None.
- When an update is available and logging occurs, the function first calls get_latest_version_from_pypi(package_name) to include the latest version in the log message; that call may trigger network and cache I/O.

## Raises:
    - Any exception raised by is_update_available_on_pypi will propagate.
        * In particular, is_update_available_on_pypi may raise ValueError when either the provided current_version or the version fetched from PyPI cannot be parsed by distutils.version.StrictVersion.
    - Any exception raised by get_latest_version_from_pypi will propagate if it occurs while retrieving the latest version for the log message.
        * get_latest_version_from_pypi may raise filesystem-related exceptions (OSError, PermissionError, IOError) during cache file writes or directory creation; these will propagate if they occur in the logging branch.
    - No exceptions are caught by run_for_package itself; callers should handle these exceptions if they want to avoid crash propagation.

## Constraints:
Preconditions:
    - package_name should be a valid PyPI package identifier string.
    - current_version should be a version string compatible with the comparison logic used by is_update_available_on_pypi (commonly a StrictVersion-compatible numeric form).
    - The runtime must permit any I/O performed by the delegated helpers if the caller expects logging of latest-version details (i.e., network access and writable user cache directory).

Postconditions:
    - The function returns a boolean indicating up-to-dateness.
    - If it returned False (update available), a warning and an info log have been emitted; the warning message includes the latest version as obtained at call time and the info message suggests the pip upgrade command.
    - No global state is mutated by run_for_package itself beyond delegating to helpers that may update a cache file or emit logs.

## Side Effects:
    - Logging: emits at least one warning and one info entry when an update is detected (calls logger.warning and logger.info as seen in the implementation).
    - Conditional network and filesystem I/O: only when an update is detected the function calls get_latest_version_from_pypi(package_name), which may perform an HTTP GET to PyPI and read/write a JSON cache file in the user cache directory. If no update is available, those I/O actions are avoided.
    - No stdout/stderr printing is performed here directly; messages are emitted through the module logger.

## Control Flow:
flowchart TD
    Start --> CheckUpdate[call is_update_available_on_pypi(package_name, current_version)]
    CheckUpdate -- True (update available) --> IsUpdatedFalse[is_updated = False]
    IsUpdatedFalse --> FetchLatest[call get_latest_version_from_pypi(package_name) for logging]
    FetchLatest --> LogWarn[logger.warning('update available for %s: %s -> %s', package_name, current_version, latest)]
    LogWarn --> LogInfo[logger.info('run: $ pip3 install -U %s', package_name)]
    LogInfo --> ReturnFalse[return False]
    CheckUpdate -- False (no update) --> IsUpdatedTrue[is_updated = True]
    IsUpdatedTrue --> ReturnTrue[return True]
    ReturnTrue --> End
    ReturnFalse --> End

## Examples:
- Typical usage (caller wants to notify the user and handle parse errors):
    try:
        up_to_date = run_for_package(package_name='online-judge-tools', current_version='1.2.3')
        if not up_to_date:
            # A warning and upgrade hint were already logged by this function.
            prompt_user_to_upgrade_if_desired()
    except ValueError:
        # Version strings could not be parsed by the comparison helper.
        # Fall back to a looser comparison or skip the update check.
        handle_version_parse_failure()

- Handling filesystem/network errors (defensive caller):
    try:
        up_to_date = run_for_package(package_name='some-package', current_version='0.9.0')
    except (OSError, PermissionError) as e:
        # Underlying cache write or directory creation failed when attempting to fetch latest version
        # (this only happens if an update was detected and fetching the latest version for logging triggered I/O).
        log_exception_and_continue(e)
    except requests.RequestException:
        # If a network request exception reaches this level (unlikely because get_latest_version_from_pypi
        # maps request failures to a sentinel value), handle as needed.
        handle_network_issue()

Notes:
- Because get_latest_version_from_pypi is only called when an update is detected, callers that cannot tolerate network/cache errors may call is_update_available_on_pypi directly and handle logging or fetch behavior themselves.

## `onlinejudge_command.update_checking.run` · *function*

## Summary:
Performs the repository's two-package update checks (tool package and API package) and returns whether the tool should be considered up-to-date; treats any error during checking as "up-to-date" to avoid interrupting normal execution.

## Description:
This function orchestrates two calls to the single-package checker and returns their logical conjunction:
- It calls the helper onlinejudge_command.update_checking.run_for_package for the main package (using the module-level version object) and for the API package (using the api_version object).
- If both helpers report the installed package is already up-to-date, this function returns True. If either helper reports an available update, it returns False.
- Any Exception raised during the process (from the helpers or other unexpected errors) is caught, an error is logged, and the function returns True. This design favors not obstructing normal CLI operation when the update check fails.

Known callers and typical trigger conditions:
- CLI startup code and command handlers that want to perform a non-blocking update check at launch or before executing user commands.
- Periodic or background tasks that run a short update-checking step and decide whether to prompt the user.
- See the component documentation for onlinejudge_command.update_checking.run_for_package for the detailed behavior and logging performed for each individual package check.

Why this logic is extracted:
- Centralizes high-level control: combining two package-level checks into a single boolean result and applying uniform error-handling policy (log-and-continue).
- Keeps callers simple: callers only need to call this no-argument function to determine whether to display update prompts, without duplicating the logic of checking both packages and handling exceptions.

## Args:
    None

## Returns:
    bool
        - True: both the tool package and the API package are considered up-to-date, OR an error occurred during the checking process and the function chose to treat that as “up-to-date” to avoid interrupting execution.
        - False: at least one of the two package checks reported that an update is available (the function successfully checked and detected newer PyPI releases).
    Notes:
        - Because exceptions are caught and mapped to a True return, callers cannot distinguish between "actually up-to-date" and "check failed" from the return value alone. If callers need that distinction, they should call run_for_package or the lower-level helpers directly and handle exceptions.

## Raises:
    None (all exceptions are caught)
        - The function catches any Exception arising during execution, logs it with logger.error('failed to check update: %s', e), and returns True. No exceptions propagate out of this function under normal operation.

## Constraints:
Preconditions:
    - Module-level symbols used by this function must be available and populated:
        * A symbol named version (typically bound to onlinejudge.__about__ or an equivalent object) must expose attributes __package_name__ and __version__.
        * A symbol named api_version (typically bound to onlinejudge_command.__about__ or similar) must expose attributes __package_name__ and __version__.
    - The helper run_for_package must be accessible in the same module and implement the expected behavior (see its documentation).
    - The runtime should allow logging (the function emits logger.error on failure and relies on run_for_package for other logs).

Postconditions:
    - The function returns a boolean as described above.
    - If an exception occurred, an error log entry has been emitted and the function returned True.
    - If one or both package checks detect updates, run_for_package will have emitted warning/info logs for each detected update, and this function returns False.

## Side Effects:
    - Logging:
        * On successful checks: no additional logging beyond what run_for_package emits.
        * On error: logs an error via logger.error('failed to check update: %s', e).
    - Indirect I/O: run_for_package may perform network and cache I/O when an update is available; this function indirectly triggers those effects when it calls the helper.
    - No other global state is modified by this function itself.

## Control Flow:
flowchart TD
    Start --> TryBlock[try]
    TryBlock --> CallMain[call run_for_package(package_name=version.__package_name__, current_version=version.__version__)]
    CallMain --> CallAPI[call run_for_package(package_name=api_version.__package_name__, current_version=api_version.__version__)]
    CallAPI --> ComputeResult[compute is_updated and is_api_updated]
    ComputeResult --> ReturnResult{both True?}
    ReturnResult -- Yes --> ReturnTrue[return True]
    ReturnResult -- No --> ReturnFalse[return False]
    TryBlock -. Exception .-> ExceptBlock[except Exception as e]
    ExceptBlock --> LogError[logger.error('failed to check update: %s', e)]
    LogError --> ReturnOnError[return True]
    ReturnTrue --> End
    ReturnFalse --> End
    ReturnOnError --> End

## Examples:
- Typical CLI startup usage (non-blocking, prefer availability over strict checking):
    # Called during startup; return value True means continue as normal without prompting.
    up_to_date = run()
    if not up_to_date:
        # run_for_package already logged warnings and an upgrade hint
        maybe_prompt_user_for_upgrade()

- If the caller needs to know whether the check failed (distinguish failure from "up-to-date"):
    try:
        # call lower-level helpers directly so exceptions are propagated for diagnosis
        main_ok = run_for_package(package_name=version.__package_name__, current_version=version.__version__)
        api_ok = run_for_package(package_name=api_version.__package_name__, current_version=api_version.__version__)
        up_to_date = main_ok and api_ok
    except Exception:
        # Handle network/cache/parse errors explicitly
        handle_update_check_failure()

