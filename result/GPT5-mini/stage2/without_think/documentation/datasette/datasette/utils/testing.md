# `testing.py`

## `datasette.utils.testing.TestResponse` · *class*

*No documentation generated.*

### `datasette.utils.testing.TestResponse.__init__` · *method*

## Summary:
Assigns the provided response object to the instance attribute self.httpx_response, creating a simple wrapper reference.

## Description:
Initializes a TestResponse instance by storing the caller-provided object on the instance without modification.

Known callers and context:
    - No callers or usage sites were available in the provided source context. The implementation does not reference or enforce any particular caller patterns.

Why this is a separate method:
    - The constructor performs the single responsibility of establishing instance state for the wrapper; doing so in __init__ ensures subsequent instance methods can rely on self.httpx_response being present.

## Args:
    httpx_response (any):
        Required positional argument. The object passed is stored directly on the instance; there is no runtime type or interface checking in this method.

## Returns:
    None
    - As with all Python constructors, __init__ returns None; the effect of calling it is observed via the created object's attributes.

## Raises:
    None
    - The method contains only an assignment statement and does not explicitly raise exceptions. Any exception would originate from the caller or the Python object model (for example, if object construction fails before __init__ is run).

## State Changes:
    Attributes READ:
        - None (the method does not read any existing instance attributes)

    Attributes WRITTEN:
        - self.httpx_response is set to the value of the httpx_response parameter

## Constraints:
    Preconditions:
        - A value must be provided for the httpx_response parameter when constructing the object.

    Postconditions:
        - After __init__ completes, self.httpx_response references exactly the object passed as httpx_response.
        - No other instance attributes are created or modified by this method.

## Side Effects:
    - No I/O operations or external service calls are performed.
    - The method stores a direct reference to the provided object; it does not copy or clone it. Any external mutations to that object will be observable via self.httpx_response.

### `datasette.utils.testing.TestResponse.status` · *method*

## Summary:
Provides a read-only accessor that returns the underlying HTTP response object's status_code value for use in tests and assertions.

## Description:
- Known callers and context:
    - No direct callers were found in the available scanned memory. This property is part of the TestResponse helper class and is intended to be used by test code to assert or inspect the HTTP response status after an HTTP request has been executed and a TestResponse instance has been created.
    - Lifecycle stage: accessed during test assertion/verification steps after a request has completed.
- Why this is a separate property:
    - Encapsulates access to the underlying client's status_code, offering a stable, minimal API for test code without exposing the full httpx response object.
    - Keeps test assertions concise and avoids repeating attribute access in many places.

## Args:
    None — this is an instance-level read-only property and takes no parameters.

## Returns:
    The raw value of self.httpx_response.status_code.
    - Type and value: determined entirely by the underlying response object's status_code attribute (commonly an int for standard HTTP clients).
    - Edge-case behavior: if the underlying attribute has an unexpected type or value, that exact value is returned without coercion or validation by this property.

## Raises:
    AttributeError (may be raised) if self.httpx_response is None or the object assigned to self.httpx_response does not expose a status_code attribute.
    Any other exception would originate from the underlying response object's attribute access; this property performs no additional exception handling.

## State Changes:
- Attributes READ:
    - self.httpx_response
    - self.httpx_response.status_code (accessed)
- Attributes WRITTEN:
    - None — the property does not modify any attributes on self or external objects.

## Constraints:
- Preconditions:
    - self.httpx_response must be set to an object that exposes a status_code attribute prior to access.
- Postconditions:
    - No mutation occurs to the TestResponse instance or the underlying response as a result of accessing this property.
    - The return value equals the current value of the underlying response's status_code at the time of access.

## Side Effects:
    - None — the property performs only an attribute read and does not perform I/O, network activity, or mutate external state.

### `datasette.utils.testing.TestResponse.headers` · *method*

## Summary:
Returns the raw headers mapping from the underlying HTTP response object so callers can inspect response headers via the TestResponse facade.

## Description:
This property provides direct access to the headers attribute of the wrapped httpx_response object supplied at TestResponse construction time. It is intended for test code that needs to read response headers (for example, asserting presence or values of Set-Cookie, Content-Type, caching headers, etc.). Typical usage is in test assertion code that examines HTTP response metadata rather than the response body.

Known callers and lifecycle:
- No specific callers in this file; intended to be called by test suites or helpers that receive a TestResponse instance after making a test request.
- Called during test assertion phase when code under test has produced an httpx-style response and the test harness wrapped it in TestResponse.

Why this is a separate property:
- Provides a stable, concise public accessor on TestResponse so test code does not need to reference the wrapped httpx_response directly.
- Keeps the TestResponse interface minimal and consistent with other convenience properties (status, body, json, text, cookies) implemented on the class.

## Args:
- None.

## Returns:
- type: The headers object from self.httpx_response (exact runtime type depends on the HTTP client used; typically an httpx.Headers or other mapping-like header container).
- values: A mapping-like view where keys are header names and values are header values (usually strings). The returned object may also provide additional convenience methods such as get_list("header-name") for headers that occur multiple times.
- edge cases:
    - If the wrapped httpx_response.headers is itself a view/wrapper, this property returns that reference (no copy is made).
    - If httpx_response.headers is empty, an empty mapping-like object is returned.

## Raises:
- AttributeError: If self.httpx_response is not set or does not expose a headers attribute, attribute access will raise an AttributeError. This occurs if TestResponse was constructed incorrectly (e.g., httpx_response is None or an incompatible object).
- Any exception raised by accessing self.httpx_response.headers (propagated without modification).

## State Changes:
- Attributes READ:
    - self.httpx_response
- Attributes WRITTEN:
    - None (this property does not modify TestResponse state)

## Constraints:
- Preconditions:
    - self.httpx_response must be assigned (TestResponse.__init__ stores the object passed in).
    - The wrapped object's headers attribute should exist and behave like a header mapping (supporting item access and, optionally, methods like get_list).
- Postconditions:
    - The call returns a direct reference to the underlying headers object. No mutation of TestResponse internal attributes is performed.
    - No copying is performed, so subsequent mutations to the returned object (if mutable) will reflect on the underlying response's headers.

## Side Effects:
- None internal: no I/O, no network calls, and no modification of external state.
- External mutation caveat: because this returns the underlying headers reference, mutating the returned object (if supported by the header container) will mutate the underlying httpx_response.headers.

### `datasette.utils.testing.TestResponse.body` · *method*

## Summary:
Return the raw response payload as the underlying HTTP client's bytes content.

## Description:
This property returns the underlying httpx response object's content attribute (the raw response body in bytes). It is typically used during test-time inspection of responses after a TestResponse object has been constructed around an httpx.Response.

Known callers and context:
- TestResponse.text: decodes the bytes returned by this property to produce a UTF-8 string.
- TestResponse.json: uses TestResponse.text (and therefore indirectly this property) to parse JSON.
- External test assertions or helpers: tests may access this property directly when they need the raw bytes (for binary responses, signature checks, or custom decoding).

Why this is its own property:
- Provides a single, explicit access point for the raw response bytes, making the intent clear and allowing other derived properties (text, json) to reuse the same retrieval logic.
- Keeps the wrapper thin: it delegates to the underlying httpx response rather than inlining decoding/parsing behavior here.
- Enables future overrides or instrumentation (e.g., lazy fetching, logging, or validation) without changing callers.

## Args:
This is a zero-argument property.

## Returns:
bytes
- The return value is the value of self.httpx_response.content as provided by the underlying HTTP client.
- Typical values: non-empty bytes for normal responses, b'' for empty bodies, or any bytes sequence the underlying client produces.
- If the underlying response object provides a different type for its content attribute, that object/value is returned as-is.

## Raises:
- This property contains no explicit raise statements.
- Implicit exceptions that may occur:
    - AttributeError: if self.httpx_response is None or does not have a content attribute.
    - Any exception raised by evaluating the underlying object's content property (propagated unchanged).

## State Changes:
Attributes READ:
- self.httpx_response

Attributes WRITTEN:
- None. This property does not modify any attributes on self.

## Constraints:
Preconditions:
- self must be a TestResponse instance constructed with a valid httpx_response assigned to self.httpx_response (set in TestResponse.__init__).

Postconditions:
- The method returns the exact value of self.httpx_response.content and leaves self unchanged.

## Side Effects:
- No I/O performed by this property.
- No network calls, file operations, or external service interactions are performed here.
- No mutation of external objects occurs; the property only reads and returns the underlying content attribute.

### `datasette.utils.testing.TestResponse.cookies` · *method*

## Summary:
Return a snapshot dictionary of cookies present on the underlying HTTP response (read-only access to the response's cookies).

## Description:
This property provides a convenient, plain-dict view of cookies attached to the wrapped httpx response object. It is a thin wrapper around the underlying response's cookies collection and exists to present cookies as a simple mapping for tests and assertions.

Known callers and context:
- No direct callers are defined inside this module. Intended callers are test code or utilities that consume TestResponse instances after making HTTP requests using the test client; callers typically read this property during assertion phases of request/response lifecycle to verify cookies set by the server.

Why this is a separate property:
- Encapsulates the test-only representation of cookies so callers do not need to depend on httpx's cookies API or cookie jar implementation. Returning a dict normalizes the interface and prevents callers from needing to import or understand httpx cookie types.

## Args:
- None.

## Returns:
- dict[str, str]: A new dictionary mapping cookie names (strings) to their corresponding values (strings). If the underlying response has no cookies, an empty dict is returned.
- Edge cases:
    - If a cookie name appears multiple times in the underlying cookie store, the dict conversion yields the last value encountered by the underlying cookies iterable (consistent with standard dict construction behavior).

## Raises:
- None raised by this property itself. (If self.httpx_response is None or lacks a cookies attribute, attribute access will raise the corresponding AttributeError; callers should ensure TestResponse was constructed with a valid response object.)

## State Changes:
- Attributes READ:
    - self.httpx_response
- Attributes WRITTEN:
    - None (this property does not modify self or self.httpx_response)

## Constraints:
- Preconditions:
    - self.httpx_response must be a non-None object that exposes a cookies attribute that can be iterated/converted into a dict (e.g., an httpx response object).
- Postconditions:
    - Returns a new dict object representing the cookies at the time of the call. The returned dict is independent of the underlying response's cookie store (mutating the returned dict does not affect the underlying response).

## Side Effects:
- None. This property performs no I/O, does not modify external state, and only reads from the wrapped response object.

### `datasette.utils.testing.TestResponse.cookie_was_deleted` · *method*

## Summary:
Checks the wrapped HTTP response headers and returns True if a Set-Cookie header is present that begins with the exact sequence cookie=""; indicating the server attempted to delete that cookie; otherwise returns False.

## Description:
- Known callers and context:
    - Invoked by test code after performing an HTTP request when the test needs to assert that the server removed a cookie. Callers obtain a TestResponse (which wraps an httpx.Response) and call this method during the assertion phase of a test.
    - Typical lifecycle stage: immediately after receiving and wrapping the HTTP response in a TestResponse instance, during test validation/assertion.
- Why this logic is a separate method:
    - Encapsulates the specific header-inspection pattern used to detect one form of cookie-deletion Set-Cookie header so tests stay concise and expressive.
    - Prevents duplication of header parsing logic across many tests and centralizes the exact matching semantics in one place.

## Args:
    cookie (str): Name of the cookie to check. The value is interpolated verbatim into the matching pattern; callers should pass the cookie name as a plain string (no surrounding quotes or attributes).

## Returns:
    bool:
        - True if any Set-Cookie header string returned by self.httpx_response.headers.get_list("set-cookie") starts with the exact prefix cookie=""; (cookie name, equals, empty quoted value, semicolon).
        - False otherwise.
    Notes on edge cases:
        - This method looks for the exact prefix cookie=""; at the start of a Set-Cookie header. It will return False for headers where that sequence appears later in the string (not at the start).
        - It will return False for other valid cookie-deletion patterns such as:
            * headers that set an Expires or Max-Age attribute without an explicit empty quoted value,
            * headers that use cookie=; (empty value without quotes),
            * headers that express deletion using a different ordering of attributes or whitespace before the semicolon.
        - If there are no Set-Cookie headers, returns False.

## Raises:
    AttributeError: If self.httpx_response is None or does not expose a headers object with a get_list method, accessing self.httpx_response.headers.get_list("set-cookie") will raise.
    Any exception raised by the headers.get_list implementation will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.httpx_response
    - self.httpx_response.headers (to call get_list("set-cookie"))
- Attributes WRITTEN:
    - None — the method does not modify self or any external objects.

## Constraints:
- Preconditions:
    - self must be a TestResponse instance with a populated httpx_response attribute whose headers object implements get_list("set-cookie") and returns an iterable of header strings.
    - cookie must identify the cookie name; passing non-string objects will be coerced to string via Python f-string behavior, but callers should pass str for clarity.
- Postconditions:
    - No mutation to self or self.httpx_response.
    - The boolean return value accurately reflects whether a Set-Cookie header starting with cookie=""; existed at the time of the call.

## Side Effects:
    - None. The method performs only in-memory inspection of response headers and does not perform I/O or mutate external state.

## Usage (guidance):
    - To assert a cookie was deleted in a test, perform the HTTP request, wrap or obtain the httpx.Response as a TestResponse, then call this method with the cookie name and assert the result is True.
    - If your server deletes cookies using Expires/Max-Age or other forms, do not rely solely on this method — use a custom header inspection that matches those patterns or check cookies returned by the response.cookies mapping as appropriate.

### `datasette.utils.testing.TestResponse.json` · *method*

## Summary:
Return the HTTP response body parsed as a Python object by decoding its UTF-8 text and passing it through the JSON parser.

## Description:
This property is a convenience accessor used after a test request returns a TestResponse; tests and helper code call it when they expect the response body to be JSON and want it parsed into native Python types for assertions. Typical usage is in test assertion code immediately after obtaining a TestResponse from the test client (for example, assert response.json["key"] == value).

This logic is factored out into its own property to centralize the decoding+parsing behavior (UTF-8 decoding then JSON parsing) so callers do not need to repeatedly decode bytes or call json.loads themselves and to provide a single place that defines the expected encoding and error behavior.

## Args:
    None — accessed as a read-only property on an instance (no parameters).

## Returns:
    object: The result of json.loads(self.text). This will be a Python data structure corresponding to the JSON value in the response body, commonly:
        - dict for JSON objects
        - list for JSON arrays
        - str, int/float, bool, or None for simple JSON values
    Edge cases:
        - If the JSON value is null, returns None.
        - If the body is an empty string or otherwise not valid JSON, a JSONDecodeError is raised (see Raises).

## Raises:
    json.JSONDecodeError: If the UTF-8 decoded response text is not valid JSON (propagated from json.loads).
    UnicodeDecodeError: If the response body bytes cannot be decoded as UTF-8 (propagated from the text property, which calls bytes.decode("utf8")).

## State Changes:
    Attributes READ:
        - self.text (property): used as the JSON input string.
        - Indirectly reads self.body and self.httpx_response.content via the text property.
    Attributes WRITTEN:
        - None — this property does not mutate the TestResponse instance or external state.

## Constraints:
    Preconditions:
        - The TestResponse instance must have a valid body (self.body) that can be decoded as UTF-8 into text.
        - The decoded text must be valid JSON if the caller expects a successful parse.
    Postconditions:
        - On successful return, the caller receives the Python representation of the JSON value; the TestResponse instance remains unchanged.
        - On error, the original exception (JSONDecodeError or UnicodeDecodeError) propagates to the caller.

## Side Effects:
    - None. No I/O, network, or external service interactions occur.
    - No mutation of objects outside self; purely a read/parse operation.

### `datasette.utils.testing.TestResponse.text` · *method*

## Summary:
Return the HTTP response body decoded from UTF-8 as a Python string; does not modify the TestResponse instance.

## Description:
Known callers and context:
- TestResponse.json (in the same class) calls this property to obtain the UTF-8 decoded text before parsing it with json.loads. This is the only explicit caller found in the class definition.
- In practice, test code that receives a TestResponse may access this property to inspect or assert the textual content of an HTTP response after a test request completes.

Lifecycle stage:
- Invoked after a test HTTP request has been executed and TestResponse has been constructed/wrapped around an httpx.Response object; used in the assertion/inspection phase of a test.

Rationale for being a separate property:
- Centralizes UTF-8 decoding logic in one place so callers (including the json property) do not need to repeat decode('utf8') logic.
- Keeps higher-level behavior (e.g., JSON parsing) simple and focused on its own concern by delegating text decoding to this property.

## Args:
- None (this is a read-only property of the TestResponse instance).

## Returns:
- str: The decoded text obtained by decoding self.body using UTF-8.
  - If the original body is empty bytes (b''), returns an empty string ''.
  - Typical return values are the textual content of the HTTP response body.

## Raises:
- UnicodeDecodeError: If the underlying byte sequence in self.body contains invalid UTF-8 byte sequences, decode("utf8") will raise this exception.
- AttributeError: If self.body does not provide a decode method (for example, if it is None or an unexpected type), attempting to call decode will raise AttributeError.
(These are direct consequences of calling self.body.decode("utf8").)

## State Changes:
- Attributes READ:
    - self.body (reads the response content; this property in turn reads self.httpx_response.content)
- Attributes WRITTEN:
    - None (this property does not modify any attributes of self or other objects)

## Constraints:
Preconditions:
- self.httpx_response must be set on the TestResponse instance and self.httpx_response.content should normally provide a bytes-like object (as httpx.Response.content does).
- Callers should expect that the content will be decoded using UTF-8; callers that need a different encoding must perform their own decoding from self.body.

Postconditions:
- The method returns a Python str representing the response body decoded using UTF-8.
- No mutation to the TestResponse instance or the wrapped httpx.Response occurs.

## Side Effects:
- None: this property performs no I/O, makes no network calls, and mutates no external objects. It only reads the in-memory response body and decodes it.

## `datasette.utils.testing.TestClient` · *class*

## Summary:
A synchronous test HTTP client wrapper for a Datasette test fixture that provides convenient get/post/request helpers, actor cookie signing, automatic startup invocation, and built-in redirect and CSRF-token handling; returns TestResponse wrappers around underlying HTTP responses.

## Description:
TestClient is intended for use in unit/integration tests that exercise a Datasette instance via its test client (ds.client). It encapsulates common test interactions:
- Ensures Datasette startup is invoked before making requests.
- Normalizes headers, cookies, and body encoding (form-urlencoded by default for post()).
- Wraps raw HTTP responses in TestResponse for test assertions.
- Handles automatic following of 301/302 redirects (with a configurable limit).
- Provides a helper to create signed actor cookies.

Typical callers:
- Test suites that instantiate or receive a Datasette test fixture object `ds`.
- Test factories that expose a TestClient for convenience.

Responsibility boundary:
- TestClient orchestrates request preparation and delegates actual HTTP I/O to ds.client.request.
- It does not manage server lifecycle or connection teardown; resource management belongs to `ds`.

## State:
Attributes and invariants:
- ds (object): Required; the Datasette fixture provided to __init__. Must implement at minimum:
  - sign(value: dict, name: str) -> str: returns a signed string used for cookies (used by actor_cookie).
  - invoke_startup() -> coroutine: async function called before each request.
  - client.request(method: str, path: str, ..., cookies: dict|None, headers: dict|None, content: bytes|str|None, follow_redirects: bool, avoid_path_rewrites: bool) -> coroutine: performs HTTP request and returns an httpx-like response object.
  The TestClient relies on these members but does not enforce types at runtime beyond calling them.
- max_redirects (int, class attribute): Default 5. Treated as a non-negative integer limit for automatic redirect recursion. If reached, an AssertionError is raised.
- No other persistent state is stored; each request is independent aside from anything stored on `ds`.

Expectations about TestResponse returned by this client:
- Returned objects are instances of TestResponse (constructed with the raw httpx response).
- TestClient expects TestResponse to provide at least:
  - status (int): HTTP status code.
  - headers (mapping-like): supports headers["Location"] for redirect handling.
  - cookies (mapping-like): supports cookies["ds_csrftoken"] when csrftoken flow is used.
  - Any other TestResponse features (body, json, etc.) are tested elsewhere; TestClient only requires the above.

Class invariants:
- ds is non-null and implements the minimal API noted above.
- max_redirects governs redirect behavior and should be set to an integer >= 0.

## Lifecycle:
Creation:
- Instantiate with a single required argument:
  - __init__(ds)
    - ds: Datasette test fixture object as described in State.

Usage:
- Public methods (get, post, request) are synchronous-callable functions (they are async functions decorated with async_to_sync). Callers may use them directly in synchronous test code.
- Typical call order: instantiate TestClient, then call any combination of get/post/request. No explicit ordering is enforced.
- For csrftoken_from usage in post(): an internal request is made to the provided csrftoken_from value (which may be a path like "/path" or a full URL like "http://host/path") to obtain a ds_csrftoken cookie; that cookie is then included in the subsequent POST.

Destruction:
- TestClient has no close/cleanup methods. Resource cleanup (closing ds.client, shutting down servers) is the responsibility of the `ds` fixture or test harness.

Sequencing notes:
- If csrftoken_from is provided, TestClient will perform the csrf-token-fetching request before the POST. Any cookies passed into the post() call are forwarded to that preflight request.
- Redirect-following is recursive and tracked by redirect_count; callers normally do not supply redirect_count.

## Public method signatures, parameters, and return values:
All public methods return TestResponse.

- actor_cookie(actor: str) -> str
  - actor: actor identifier (string) used to create an actor cookie.
  - Returns: a signed cookie string produced by calling ds.sign({"a": actor}, "actor").
  - Raises: any exception propagated from ds.sign.

- get(
    path: str,
    follow_redirects: bool = False,
    redirect_count: int = 0,
    method: str = "GET",
    cookies: dict | None = None,
    if_none_match: str | None = None,
  ) -> TestResponse
  - path: path or full URL to request (e.g., "/_search" or "http://host/path").
  - follow_redirects: whether to automatically follow 301/302 Location responses. Default False for get().
  - redirect_count: internal recursion counter; callers normally leave as default.
  - method: HTTP method name; get() permits overriding but defaults to "GET".
  - cookies: mapping of cookie name to value to send with the request.
  - if_none_match: optional ETag value; if provided, sets the "if-none-match" header for the request.
  - Behavior: delegates to _request and returns a TestResponse.

- post(
    path: str,
    post_data: dict | list[tuple[str, str]] | None = None,
    body: str | bytes | None = None,
    follow_redirects: bool = False,
    redirect_count: int = 0,
    content_type: str = "application/x-www-form-urlencoded",
    cookies: dict | None = None,
    headers: dict | None = None,
    csrftoken_from: str | bool | None = None,
  ) -> TestResponse
  - path: path or full URL for the POST.
  - post_data: mapping or sequence of (key, value) pairs to be URL-encoded if provided. If provided, body must be None.
  - body: raw request body to send (string or bytes). If provided, post_data must be empty/None.
  - follow_redirects: see get; default False.
  - content_type: Content-Type header to set for the POST when provided (defaults to form-encoded).
  - cookies: mapping of cookie name to value; used for both token-fetch preflight (if csrftoken_from) and the POST.
  - headers: additional request headers mapping.
  - csrftoken_from:
    - If None (default): no CSRF preflight is done.
    - If True: the same path argument is used as the source to fetch the CSRF token.
    - If a string: that value (path or full URL) is used as the source to fetch the CSRF token.
    - When used, TestClient will perform an internal request to csrftoken_from (awaiting ds.invoke_startup and calling ds.client.request) and expects that the returned TestResponse has a cookie named "ds_csrftoken". That token is inserted into cookies["ds_csrftoken"] and post_data["csrftoken"] before performing the POST.
  - Returns: TestResponse for the POST result.

  - Important assertions and constraints:
    - Raises AssertionError("Provide one or other of body= or post_data=") if both post_data and body are provided.
    - Raises AssertionError("body= is not compatible with csrftoken_from=") if csrftoken_from is not None and body is provided.

- request(
    path: str,
    follow_redirects: bool = True,
    redirect_count: int = 0,
    method: str = "GET",
    cookies: dict | None = None,
    headers: dict | None = None,
    post_body: str | bytes | None = None,
    content_type: str | None = None,
    if_none_match: str | None = None,
  ) -> TestResponse
  - Generic request entrypoint; defaults differ from get() (follow_redirects default True here).
  - post_body: raw content for body (used directly as content passed to ds.client.request).
  - content_type: if provided, sets the "content-type" request header.
  - if_none_match: if provided, sets the "if-none-match" header.

Note: All methods are implemented as async functions wrapped with async_to_sync (except _request which is async), so calling them runs the complete operation synchronously in the caller's thread.

## Internal method (_request) behavior (async):
_signature: async def _request(path: str, follow_redirects: bool = True, redirect_count: int = 0, method: str = "GET", cookies: dict | None = None, headers: dict | None = None, post_body: str | bytes | None = None, content_type: str | None = None, if_none_match: str | None = None) -> TestResponse_

- Invokes await ds.invoke_startup() before making any HTTP call.
- Normalizes headers: creates headers dict if None, sets "content-type" header if content_type provided, sets "if-none-match" header if if_none_match provided.
- Calls await ds.client.request(method, path, follow_redirects=follow_redirects, avoid_path_rewrites=True, cookies=cookies, headers=headers, content=post_body)
  - Note: avoid_path_rewrites is set True to ensure the test client requests the path as provided.
- Wraps the returned raw httpx response with TestResponse(httpx_response) and assigns to response.
- Redirect handling:
  - If follow_redirects is True and response.status is 301 or 302:
    - Asserts redirect_count < self.max_redirects, otherwise raises AssertionError with message "Redirected {redirect_count} times, max_redirects={self.max_redirects}".
    - Reads location = response.headers["Location"] and recursively calls _request(location, follow_redirects=True, redirect_count=redirect_count + 1).
    - Note: location is passed as-is (it may be a relative path or absolute URL). The underlying ds.client.request will interpret it according to its own semantics.
- Returns the final TestResponse.

## Raises:
Direct exceptions/assertions from TestClient code:
- AssertionError("Provide one or other of body= or post_data="): when both post_data and body are provided to post().
- AssertionError("body= is not compatible with csrftoken_from="): when csrftoken_from is provided while body is also set.
- AssertionError(f"Redirected {redirect_count} times, max_redirects={self.max_redirects}"): when a redirect loop exceeds max_redirects.

Propagated errors (documented so callers know to expect them):
- KeyError when response.headers["Location"] is accessed for a 301/302 without a Location header.
- KeyError when token_response.cookies["ds_csrftoken"] is accessed but the cookie is not present.
- Any exceptions raised by ds.invoke_startup() or ds.client.request(...) propagate to the caller.

## Method Map:
flowchart LR
    get --> _request
    post --> _request
    request --> _request
    _request --> ds.invoke_startup
    ds.invoke_startup --> ds.client.request
    ds.client.request --> TestResponse
    TestResponse --> check_redirect{status in (301,302) and follow_redirects}
    check_redirect -- yes --> check_count{redirect_count < max_redirects}
    check_count -- ok --> _request
    check_redirect -- no --> return[TestResponse]

## Example:
- Setup (pseudo):
    ds = <Datasette test fixture implementing sign, invoke_startup, client.request>
    client = TestClient(ds)

- Simple GET:
    resp = client.get("/_status")
    assert resp.status == 200

- GET with ETag:
    resp = client.get("/_status", if_none_match='"abc123"')
    # If the underlying handler honors If-None-Match, resp.status may be 304.

- Form POST:
    resp = client.post("/submit", post_data={"name": "alice", "age": "30"})
    # post_data is URL-encoded; content-type defaults to application/x-www-form-urlencoded

- POST with CSRFTOKEN fetched from same path:
    resp = client.post("/submit", post_data={"x": "y"}, csrftoken_from=True)
    # Performs an internal request to "/submit" to fetch ds_csrftoken, inserts it into cookies
    # and post_data["csrftoken"], then performs the POST.

- Follow redirects:
    resp = client.get("/redirecting", follow_redirects=True)
    # If /redirecting returns 302 with Location, TestClient follows up to max_redirects.

### `datasette.utils.testing.TestClient.__init__` · *method*

## Summary:
Initializes the TestClient by storing the provided Datasette test fixture onto the instance so subsequent client methods can use it.

## Description:
- Known callers and context:
  - Test suites and test factories that create a TestClient for interacting with a Datasette test fixture (typically immediately after creating or receiving the `ds` fixture).
  - Typical use is at object construction time in test setup code: client = TestClient(ds). This occurs during the test lifecycle before any get/post/request calls are made against the client.
- Why this is its own method:
  - Encapsulates the single responsibility of wiring the TestClient to its Datasette fixture and documents the required fixture API in one place.
  - Keeps construction logic minimal and centralised so future validation, instrumentation, or dependency injection can be added without changing callers.

## Args:
- ds (object): Required. The Datasette test fixture instance the TestClient will use for all HTTP interactions.
  - Expected API on `ds` (TestClient does not enforce types at runtime; it assumes these members exist and are callable):
    - sign(value: dict, name: str) -> str
    - invoke_startup() -> coroutine
    - client.request(method: str, path: str, ..., cookies: dict|None, headers: dict|None, content: bytes|str|None, follow_redirects: bool, avoid_path_rewrites: bool) -> coroutine
  - Allowed values: any non-null object implementing the minimal API above. Passing None or an object missing those members will not raise here but will cause errors when TestClient methods attempt to call the missing API.

## Returns:
- None: Standard Python __init__ behavior; the method initializes instance state and does not return a value.

## Raises:
- TypeError: Raised by Python automatically if the caller does not supply the required `ds` positional argument.
- No other exceptions are raised by this method itself. Any validation or runtime errors resulting from using an incorrectly-shaped `ds` occur later when TestClient methods call into `ds`.

## State Changes:
- Attributes READ:
  - None.
- Attributes WRITTEN:
  - self.ds is assigned to refer to the provided `ds` fixture.

## Constraints:
- Preconditions:
  - Caller must provide exactly one positional argument `ds`.
  - For correct operation of the TestClient after construction, `ds` should implement the minimal API described in Args.
- Postconditions:
  - After __init__ completes, self.ds is equal to the `ds` argument and the TestClient is ready to perform request-related operations that delegate to `ds`.
  - No additional attributes are initialized by this method.

## Side Effects:
- No I/O, network calls, or external side effects occur in this method.
- The only observable effect is mutation of the newly-created TestClient instance by setting self.ds.

### `datasette.utils.testing.TestClient.actor_cookie` · *method*

## Summary:
Creates and returns a signed "actor" token by delegating to the datasource's signing facility; does not modify TestClient state.

## Description:
This helper constructs a payload with a single key "a" mapped to the provided actor value and passes it to the datasource (self.ds) signing function with the purpose/purpose-name "actor". It is intended for use by tests or callers that need a signed actor cookie value to include in requests generated by this TestClient.

Known callers / context:
- Intended to be called by test code (or test helpers) prior to invoking TestClient.get/post/request so the returned value can be included in the cookies argument. The TestClient methods accept a cookies mapping which can carry this signed token into outgoing HTTP requests.
- Lifecycle: used at test-time during request construction; not invoked by TestClient internally.

Why this is a separate method:
- Encapsulates the specific payload shape and signing purpose ("actor") in one place so tests do not duplicate the signing payload structure or purpose string.
- Keeps tests simpler and decouples the construction of signed actor tokens from request-making logic.

## Args:
    actor (any):
        The actor identifier or value to embed under the "a" key in the signed payload. The method does not validate the type; whatever is provided is put into the dict {"a": actor} and forwarded to self.ds.sign.

## Returns:
    Any:
        The exact return value produced by self.ds.sign({"a": actor}, "actor").
        The returned value is an opaque signed token (typically a string suitable for use as a cookie value), but this method makes no further guarantees about type or format — it simply returns whatever self.ds.sign returns.

## Raises:
    Any exception raised by self.ds.sign:
        This method does not catch exceptions from the underlying signing implementation; such exceptions will propagate to the caller. Exact exception types and conditions depend on the datasource's sign method.

## State Changes:
    Attributes READ:
        self.ds
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - self.ds must be set and provide a callable sign method that accepts (payload, purpose) as its parameters; otherwise an AttributeError or TypeError will occur when invoked.
        - The caller should pass an actor value appropriate for the datasource's signing expectations (the method does not perform validation).

    Postconditions:
        - No attributes on self are modified.
        - The return value equals the direct result of calling self.ds.sign({"a": actor}, "actor").

## Side Effects:
    - No I/O, network calls, or external side effects are performed by this method itself; any side effects depend on the implementation of self.ds.sign and will occur if that function performs I/O or other operations.

### `datasette.utils.testing.TestClient.get` · *method*

## Summary:
Delegates a GET-style request to the client's general request implementation and returns the response wrapper produced by that call; the method itself does not modify TestClient state.

## Description:
This async coroutine is a thin, method-specific wrapper around the TestClient._request implementation. It exists to provide a concise GET-oriented callsite (with appropriate defaults) while centralizing the actual request, startup, redirect and response-wrapping logic inside _request.

Known callers and context:
- Intended for use by test code that exercises HTTP endpoints on the Datasette test instance.
- In the TestClient class definition this coroutine is decorated with async_to_sync, so typical synchronous tests call TestClient.get(...) as a regular (synchronous) method; in asynchronous test code the underlying coroutine may be awaited if desired.
- Other TestClient convenience methods (e.g., post, request) reuse the shared _request implementation rather than duplicating request handling; get simply forwards its parameters to that implementation.

Why this is a separate method:
- Provides an explicit GET-oriented public API with method and default semantics set for GET requests.
- Keeps method-specific defaults and small per-method validation separate from the shared _request implementation that handles startup, header preparation, httpx invocation, response wrapping and redirect following.

## Args:
    path (str):
        Path or URL to request (for example "/_search" or "http://host/path"). Passed unchanged to the underlying httpx client via _request.
    follow_redirects (bool, optional):
        Whether to follow 301/302 redirects automatically. Defaults to False for this method (note: _request's own default differs).
    redirect_count (int, optional):
        Current redirect depth used when following redirects. Defaults to 0. Callers should pass 0 (or omit) — this parameter is for internal bookkeeping when _request performs recursive redirects.
    method (str, optional):
        HTTP method to use; default "GET". This parameter is preserved and forwarded but GET is the intended method for this helper.
    cookies (dict[str,str] | None, optional):
        Cookie name→value mapping to include with the request. Defaults to None.
    if_none_match (str | None, optional):
        Optional ETag value used to set an If-None-Match header for conditional requests. Defaults to None.

## Returns:
    The exact value returned by self._request(...) — typically a test response wrapper constructed by _request around the underlying httpx response (referred to in the codebase as a TestResponse). The documentation does not assert specific attributes on that object because its class definition is outside the scope of this method.

Edge cases:
- If follow_redirects=True and the response is an HTTP 301/302, _request may perform recursive calls and return the TestResponse for the final target URL.
- If an exception occurs during startup or the HTTP call, no response is returned and the exception propagates.

## Raises:
    Exceptions raised by the delegated _request and its underlying calls:
    - AssertionError:
        Raised by _request if a redirect loop exceeds the configured limit (redirect_count >= self.max_redirects). The assertion message indicates the number of redirects and max_redirects.
    - KeyError:
        If following a 301/302 redirect but the response headers do not contain a "Location" header, accessing response.headers["Location"] in _request will raise KeyError.
    - Any exception raised by self.ds.invoke_startup() or self.ds.client.request(...):
        These exceptions (network errors, runtime errors, etc.) propagate directly and are not caught by get.

## State Changes:
Attributes READ (via delegated _request):
    - self.ds: accessed by _request to run startup handlers and obtain the underlying httpx client.
    - self.max_redirects: accessed by _request to assert redirect depth limits.

Attributes WRITTEN:
    - None on TestClient. This method does not mutate TestClient instance attributes.

## Constraints:
Preconditions:
    - path must be a string acceptable to the Datasette httpx client.
    - redirect_count must be a non-negative integer; callers should generally leave it at the default 0.
    - If used via the sync wrapper (async_to_sync), callers must not call the wrapped synchronous method from within the same event loop expecting to await it.

Postconditions:
    - If the call completes normally, the returned object is the same object returned by _request (a response wrapper).
    - No TestClient attributes are changed by this call.

## Side Effects:
    - Delegates to self._request(...), which:
        - Awaits self.ds.invoke_startup(): may run Datasette startup logic.
        - Issues an HTTP request through self.ds.client.request(...): performs I/O via the test httpx client.
        - May perform additional requests if follow_redirects=True and 301/302 responses are encountered.
    - Any exceptions from startup or the HTTP client propagate to the caller.

### `datasette.utils.testing.TestClient.post` · *method*

## Summary:
Perform an asynchronous HTTP POST request through the TestClient, encoding form data as needed and optionally obtaining and attaching a CSRF token before the POST; returns the response produced by the client's request mechanism.

## Description:
This async helper is used by test code (and other internal client simulations) to simulate an HTTP POST against the application under test. Typical callers are test cases that exercise endpoint POST behavior, or higher-level test helpers that emulate browser-like POSTs including CSRF token handling.

This logic is separated into its own method because it consolidates several responsibilities required for POST interactions in tests:
- mutually-exclusive handling of raw request body vs. structured form data,
- automatic urlencoding of form data when provided,
- optional two-step CSRF token acquisition and attachment,
- consistent invocation of the underlying request mechanism (self._request) with the correct HTTP method, headers, cookies and content type,
- optional redirect-following behavior.

Keeping those responsibilities in one place avoids duplication and ensures consistent POST semantics across tests.

## Args:
    path (str):
        The request path (URL or path-like string) to POST to. If csrftoken_from is True, the same path is used to fetch the CSRF token.
    post_data (dict | sequence | None, optional):
        Mapping or sequence of key/value pairs to be sent as application/x-www-form-urlencoded form data.
        Values may be sequences (lists/tuples) when multiple values are required for a key (urlencode is called with doseq=True).
        Defaults to None.
    body (str | None, optional):
        Raw request body to send. Mutually exclusive with post_data. If provided, it is sent as-is as the POST body.
        Defaults to None.
    follow_redirects (bool, optional):
        If True, the client will follow server redirects. Passed through to self._request unchanged.
        Defaults to False.
    redirect_count (int, optional):
        Current redirect depth / counter passed to self._request for redirect handling. Defaults to 0.
    content_type (str, optional):
        The request Content-Type header. Defaults to "application/x-www-form-urlencoded".
    cookies (dict | None, optional):
        Cookie jar (mapping) to send with the request. If None, an internal dict is created.
        If a dict is provided by the caller, this method may mutate it in-place to add a CSRF cookie when csrftoken_from is used.
        Defaults to None.
    headers (dict | None, optional):
        Additional HTTP headers to send with the request. Passed through to self._request unchanged.
        Defaults to None.
    csrftoken_from (None | bool | str, optional):
        Controls CSRF token acquisition:
        - None: do not perform CSRF token acquisition.
        - True: fetch a CSRF token by making a preliminary request to the same path as the POST.
        - str: fetch a CSRF token by making a preliminary request to the provided path.
        When used, the token is read from the response cookies under the key "ds_csrftoken" and added to both the cookies sent with the POST and to the form data as the "csrftoken" field.
        Defaults to None.

## Returns:
    Any
        The exact return value produced by awaiting self._request(...). In the repository this is a response-like object provided by the TestClient infrastructure (it is expected to expose a .cookies mapping used by csrftoken handling). The returned object represents the POST response (after following redirects if requested).

## Raises:
    AssertionError:
        If both post_data and body are provided (they are mutually exclusive).
        If csrftoken_from is not None but body is provided (CSRF acquisition is incompatible with providing body=).
    KeyError:
        If csrftoken_from is used but the preliminary response does not include a "ds_csrftoken" cookie, attempting to read token_response.cookies["ds_csrftoken"] will raise KeyError.
    Any exception propagated from self._request:
        Underlying request implementation may raise network, HTTP handling, or other errors; these propagate out of this method.

## State Changes:
    Attributes READ:
        self._request (method) — invoked to perform HTTP requests.
    Attributes WRITTEN:
        None — the method does not assign to any self.<attr> fields.

## Constraints:
    Preconditions:
        - Exactly one of these must be true: post_data is provided or body is provided or neither; but not both post_data and body. The method asserts this.
        - If csrftoken_from is not None, body must be None (asserted).
        - post_data, if provided, must be an acceptable input for urllib.parse.urlencode with doseq=True (e.g., mapping of strings to strings or sequences).
    Postconditions:
        - If post_data was provided (and not empty), the method sets body to the urlencoded form string before sending.
        - If csrftoken_from was used, the cookies mapping passed to self._request contains a "ds_csrftoken" entry and the form data (post_data) contains a "csrftoken" entry set to the same token.
        - The method returns whatever result self._request yields for a POST with the supplied parameters.

## Side Effects:
    - Performs one HTTP request via self._request to the target path when csrftoken_from is None, or two requests when csrftoken_from is set (first to fetch the CSRF token, second to perform the POST).
    - May mutate the caller-provided cookies dict (adding "ds_csrftoken") and the caller-provided post_data dict (adding "csrftoken") in-place when csrftoken_from is used.
    - No file or network IO is performed directly by this method itself; all I/O occurs through self._request which is responsible for the actual HTTP interactions.

### `datasette.utils.testing.TestClient.request` · *method*

## Summary:
Async entry point that forwards all HTTP request parameters to the central request implementation and returns its TestResponse result; when the TestClient class exposes this coroutine it is typically decorated with async_to_sync so tests can call it synchronously. The method itself does not mutate TestClient state.

## Description:
This coroutine exists as the public, minimal surface for issuing HTTP requests in tests. It delegates all work to TestClient._request, preserving the exact semantics implemented there: startup invocation on the datasette instance, header normalization, delegation to the underlying HTTP client, TestResponse wrapping, and optional 301/302 redirect following.

Known callers and lifecycle context:
- Directly invoked by test code during the "act" phase to issue requests against the test datasette instance.
- Served as the target for the synchronous wrapper applied in the TestClient class via async_to_sync, allowing typical tests to call TestClient.request(...) without using await.
- Higher-level convenience methods in the same class (get and post) also call into the same underlying _request implementation; those methods perform small pre-processing (form-encoding, CSRF token handling) before delegating here.

Why this is a separate method:
- Provides a single, consistent API that forwards to the centralized request logic in _request so higher-level wrappers remain thin.
- Enables a single place to apply async_to_sync at the method level for synchronous test use.

## Args:
    path (str):
        Request path or URL acceptable to the underlying client. Required.
    follow_redirects (bool, optional):
        If True, instructs the underlying implementation to follow 301/302 redirects. Default True.
    redirect_count (int, optional):
        Internal recursion depth for redirect following. Must be a non-negative integer. Default 0.
    method (str, optional):
        HTTP method to use, e.g. "GET", "POST". Default "GET".
    cookies (dict|None, optional):
        Mapping of cookie names to values; forwarded as-is to the underlying client. Default None.
    headers (dict|None, optional):
        Mapping of header names to values; forwarded as-is to the underlying client. If None, the underlying implementation will substitute an empty dict. Default None.
    post_body (str|bytes|None, optional):
        Raw request body content to send (caller is responsible for encoding). Default None.
    content_type (str|None, optional):
        If provided, the underlying implementation will set the "content-type" header to this value. Default None.
    if_none_match (str|None, optional):
        If provided, the underlying implementation will set the "if-none-match" header to this value. Default None.

## Returns:
    TestResponse:
        The TestResponse object produced by TestClient._request for the final response (after following redirects if enabled). When called synchronously (via async_to_sync at the class level) or awaited directly, the caller receives this TestResponse. No other sentinel values are returned.

## Raises:
    Any exception raised by TestClient._request is propagated unchanged. Examples include:
        - AssertionError: if redirect following is enabled and redirect_count >= self.max_redirects (underlying implementation enforces a strict limit).
        - KeyError: if a redirect response lacks a "Location" header while following redirects.
        - Exceptions from await self.ds.invoke_startup() or await self.ds.client.request(...) (e.g., network/httpx errors).

## State Changes:
    Attributes READ:
        self._request (the bound method is accessed and invoked)
    Attributes WRITTEN:
        None — this method does not modify TestClient attributes.

## Constraints:
    Preconditions:
        - The TestClient instance must have a callable _request coroutine method that accepts the documented arguments.
        - If the method is invoked synchronously via async_to_sync, callers should not rely on any extra synchronous side effects beyond what _request performs.
        - redirect_count should be a non-negative integer (it is treated as an internal recursion counter).
    Postconditions:
        - On success, returns the TestResponse produced by the underlying _request call; TestClient instance attributes remain unchanged.
        - Exceptions from the underlying call are propagated to the caller.

## Side Effects:
    - This wrapper delegates to TestClient._request which may:
        * Invoke await self.ds.invoke_startup(), potentially mutating the datasette instance.
        * Perform I/O via await self.ds.client.request(...), issuing one or more HTTP requests.
        * Follow redirects, causing multiple requests.
    - The wrapper itself performs no I/O and only triggers the side effects indirectly by calling _request.

## Usage example (illustrative, not executable here):
    - Asynchronous use:
        response = await test_client.request("/path", method="GET")
    - Synchronous use (TestClient methods in the class are typically decorated with async_to_sync):
        response = test_client.request("/path", method="GET")
    The returned response is a TestResponse instance representing the HTTP response.

### `datasette.utils.testing.TestClient._request` · *method*

## Summary:
Performs an asynchronous HTTP request against the test DataScript/DS client, wraps the HTTPX response in a TestResponse, and optionally follows 301/302 redirects up to max_redirects without rewriting request paths.

## Description:
This async helper is the central implementation used by the synchronous TestClient convenience methods (get, post, request). It:
- Ensures the DataScript instance (self.ds) has run startup hooks by calling await self.ds.invoke_startup().
- Normalizes and injects common headers (content-type and if-none-match) into the outgoing request.
- Delegates the actual network interaction to self.ds.client.request(...), passing through cookies, headers and raw body content.
- Wraps the returned httpx response in a TestResponse and, when follow_redirects=True and the response is a 301 or 302, follows the Location header by recursively calling itself (incrementing redirect_count).

Known callers:
- TestClient.get (synchronous wrapper via async_to_sync)
- TestClient.post (synchronous wrapper via async_to_sync)
- TestClient.request (synchronous wrapper via async_to_sync)
- It also calls itself recursively to follow redirects (internal recursive caller).

Why this is a separate method:
- Centralizes request logic (startup invocation, header normalization, httpx client call, TestResponse wrapping, and redirect handling) so higher-level convenience methods (get, post, request) can remain thin and reuse consistent behavior.

## Args:
    path (str): Request path or URL to send to self.ds.client. Must be acceptable to the underlying client.request API.
    follow_redirects (bool): If True, automatically follow HTTP 301/302 redirects by issuing additional requests. Default True.
    redirect_count (int): Current redirect depth (internal recursion counter). Default 0.
    method (str): HTTP method to use (e.g., "GET", "POST"). Default "GET".
    cookies (dict|None): Mapping of cookie names to values to send with the request. Default None.
    headers (dict|None): Mapping of header names to values. If None, an empty dict is used and headers may be added by this method. Default None.
    post_body (str|bytes|None): Raw request body to send as the HTTP content parameter. Caller is responsible for encoding. Default None.
    content_type (str|None): If provided, sets the "content-type" header to this value (overwrites any same-named header in the provided headers mapping). Default None.
    if_none_match (str|None): If provided, sets the "if-none-match" header to this value. Default None.

## Returns:
    TestResponse: A TestResponse wrapper around the underlying HTTPX response representing the final response.
    - If follow_redirects=True and the server returns 301 or 302, returns the TestResponse from the final (after following redirects) request.
    - If follow_redirects=False, returns the TestResponse corresponding to the immediate response.
    - No other sentinel values are returned; exceptions are propagated.

## Raises:
    AssertionError: If follow_redirects is True and redirect_count >= self.max_redirects. Message includes the redirect_count and max_redirects.
    KeyError: If a redirect response (301/302) is received but the "Location" header is missing in response.headers.
    Any exceptions raised by await self.ds.invoke_startup() are propagated.
    Any exceptions raised by await self.ds.client.request(...) (e.g., httpx/network errors) are propagated.
    (No exceptions are caught or converted; callers should expect raw propagation.)

## State Changes:
    Attributes READ:
        self.ds (used to invoke startup and access ds.client)
        self.max_redirects (used to bound automatic redirect following)
    Attributes WRITTEN:
        None — this method does not modify TestClient attributes.

## Constraints:
    Preconditions:
        - self.ds must be set and have the following properties:
            * An async method invoke_startup() that can be awaited.
            * A client attribute exposing an async request(method, url, ...) coroutine compatible with the parameters used.
        - path must be a valid input for self.ds.client.request.
        - If callers intend to send form fields, they must encode them into post_body (TestClient.post assists with this).
        - The headers mapping, if provided, should be a mutable mapping; otherwise a fresh dict will be used.
    Postconditions:
        - After successful completion, a TestResponse object is returned representing the response to the final request (after following redirects if enabled).
        - No TestClient instance attributes are mutated by this call.
        - If redirect following occurred, redirect_count in the call stack will have incremented for each redirect followed (but no attribute on self retains that value).

## Side Effects:
    - Calls await self.ds.invoke_startup(), which may run startup side-effects on the DataScript instance (mutating ds state).
    - Performs I/O via await self.ds.client.request(...): network requests (or simulated requests in tests) are executed.
    - May perform multiple network requests when following redirects.
    - Constructs a TestResponse instance from the underlying client response (may allocate memory).
    - Reads response.headers["Location"] for redirect handling; missing header will raise KeyError.

## Implementation notes / edge cases to preserve:
    - The method sets headers = headers or {} so callers' None is treated as an empty dict and callers' provided dict is used directly (mutated) — preserve this behavior.
    - It sets header keys exactly as "content-type" and "if-none-match" (lowercase); preserve the exact header names used.
    - It passes avoid_path_rewrites=True to self.ds.client.request; preserve this flag when delegating to the client.
    - Redirect handling: only follows status codes 301 and 302 and only when follow_redirects is True.
    - The redirect limit check uses strict less-than: redirect_count < self.max_redirects; on equality an AssertionError is raised.
    - The method returns immediately with the TestResponse for non-redirect responses (or when follow_redirects is False).

