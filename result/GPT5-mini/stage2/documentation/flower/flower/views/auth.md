# `auth.py`

## `flower.views.auth.authenticate` · *function*

## Summary:
Checks whether an email string matches a configurable pattern; supports literal equality, pipe-separated alternatives, and a flawed "wildcard" branch that only treats an original '.*' sequence as a wildcard when present.

## Description:
This function centralizes pattern-based email matching using three strategies selected by inspecting the pattern string:

- Pipe-separated alternatives: If the pattern contains a '|' character, the pattern is split on '|' and the email is tested for exact equality against any alternative.
- Wildcard-ish regex: If the pattern contains any '*' character, the function escapes the entire pattern for safe regex use, then replaces the escaped sequence corresponding to an original '.*' (literally dot followed by star) with a character class that approximates allowed characters in email local-parts. The function then performs re.fullmatch on the resulting regex.
  - Important implementation detail: the replacement looks for the escaped substring '\.\*' after re.escape() — therefore only original occurrences of '.*' (dot-star) in the pattern are converted into the wildcard character class. A standalone '*' in the original pattern (for example "user*@example.com") will not be converted into a wildcard; it will be escaped and treated as a literal '*' in the regex.
- Exact equality: If neither '|' nor '*' is present, the function returns pattern == email.

Known callers and typical usage:
- No callers were provided in the supplied context. Typical callers are authentication/authorization checks and configuration-driven allowlists where allowed emails are stored as patterns.
- This function is extracted to provide a single, reusable policy for matching configuration patterns against runtime email values and to avoid duplicating escaping and matching logic across handlers.

## Args:
    pattern (str): Pattern describing allowed emails. Expected forms include:
        - Literal single email: "alice@example.com"
        - Pipe-separated alternatives: "alice@example.com|bob@example.com"
        - Patterns intended to use a wildcard: either "prefix.*@example.com" (works) or "prefix*@example.com" (does not act as wildcard; '*' becomes literal)
      Notes:
        - If both '|' and '*' appear in the same pattern string, the '|' branch takes precedence and the function performs literal equality checks on each alternative (no wildcard processing is applied).
        - The function inspects the raw pattern string; it does not normalize whitespace.
    email (str): Email string to test. Must be a str; passing non-string values will likely raise TypeError.

## Returns:
    bool or re.Match or None:
        - If pattern contains '|' : returns True if email equals one of the alternatives, otherwise False.
        - If pattern contains '*' : returns the result of re.fullmatch(regex_pattern, email):
            * A re.Match object when the entire email matches the constructed regex (truthy).
            * None when it does not match (falsy).
          Note: Because the wildcard branch returns the raw re.fullmatch result (Match or None), callers requiring a strict boolean should wrap the call in bool(...).
        - Otherwise: returns True if pattern == email, else False.

## Raises:
    - TypeError: If either pattern or email is not a str (e.g., None), operations like re.fullmatch may raise TypeError.
    - re.error: Unlikely because the function calls re.escape before making substitutions; however if the constructed regex is malformed for any reason, re.fullmatch may raise re.error. The function does not catch these exceptions.

## Constraints:
    Preconditions:
        - pattern must be a Python str.
        - email must be a Python str.
    Postconditions:
        - The function performs no external side effects.
        - The return value is either a boolean (for '|' or equality branches) or the direct re.fullmatch return (re.Match or None) for the '*' branch.

## Side Effects:
    - None. The function is pure (no I/O, no global state mutation, no external calls beyond pure computation and standard-library regex matching).

## Control Flow:
flowchart TD
    A[Start: receive pattern, email] --> B{pattern contains '|' ?}
    B -- Yes --> C[Split pattern on '|' into alternatives] --> D{email equals any alternative?}
    D -- Yes --> E[Return True]
    D -- No --> F[Return False]
    B -- No --> G{pattern contains '*' ?}
    G -- Yes --> H[Escape pattern with re.escape()] --> I[Replace escaped '\.\*' with email-safe char-class]
    I --> J[Call re.fullmatch(constructed_regex, email)]
    J -- Match --> K[Return re.Match object (truthy)]
    J -- No Match --> L[Return None (falsy)]
    G -- No --> M[Return pattern == email (True/False)]

    note right of I
      Replacement acts only when the original pattern contained '.*' (dot-star).
      A standalone '*' (e.g., "user*@domain") remains escaped and matches a literal '*'.
    end

## Examples:
1) Exact literal
    pattern = "alice@example.com"
    authenticate(pattern, "alice@example.com")  # -> True
    authenticate(pattern, "ALICE@example.com")  # -> False (case-sensitive literal compare)

2) Pipe-separated alternatives
    pattern = "alice@example.com|bob@example.com"
    authenticate(pattern, "bob@example.com")    # -> True
    authenticate(pattern, "carol@example.com")  # -> False

3) Wildcard nuance — '.*' works, '*' alone does not
    pattern1 = "admin.*@example.com"            # contains '.*' -> will be converted to wildcard char-class
    result1 = authenticate(pattern1, "admin123@example.com")
    bool(result1)                               # -> True (if matched)

    pattern2 = "admin*@example.com"             # contains '*' but not '.*' -> '*' is literal after escaping
    authenticate(pattern2, "admin123@example.com")  # -> None (no match) or falsy; does NOT act as wildcard
    authenticate(pattern2, "admin*@example.com")    # -> re.Match or True-like if email actually contains a literal '*'

4) Using as strict boolean
    is_allowed = bool(authenticate("user.*@example.com", "user@example.com"))

Recommendations:
    - Callers that need a boolean should wrap the result with bool().
    - Be cautious: a common expectation (that "user*@domain" works like shell-glob) is incorrect here — require "user.*@domain" for the wildcard to be activated.
    - If you control pattern creation, prefer using '.*' where a wildcard is intended, or extend/replace this function for more predictable wildcard semantics.

## `flower.views.auth.validate_auth_option` · *function*

## Summary:
Validate a single authentication-pattern string according to the repository's lightweight rules; returns True when the pattern is allowed and False when it violates any constraint.

## Description:
This function enforces syntactic constraints on an auth option "pattern" used by the application when parsing or matching authentication configuration entries. Typical callers (not present in the provided snippet) are configuration parsers, validation routines for user-provided auth options, or any place that needs to accept a canonical pattern for matching identities or addresses before storing/using it.

Why this is a separate function:
- Encapsulates the small but specific validation policy in one place so callers do not duplicate conditional logic.
- Keeps configuration parsing code simpler and clearer by delegating pattern correctness checks here.
- Centralizes changes to the validation policy (e.g., relaxing or tightening wildcard rules) to a single function.

## Args:
pattern (str)
    The pattern string to validate. Expected to be a text pattern representing an identity or address possibly containing a single wildcard ('*') and/or alternation operators ('|') when allowed.
    - Must be a string. Passing a non-string (e.g., None or an object without .count/.rsplit methods) will raise an attribute error from attempted method calls.
    - There is an implicit semantic: when a wildcard '*' is used it is only permitted in the left-side (local) portion of an '@'-separated address. If no '@' is present, wildcard characters are effectively disallowed by the third rule (see Returns/behavior below).
    - No default value; required positional argument.

## Returns:
bool
    True if the pattern meets all validation rules; False if it violates any rule.

    All possible outcomes:
    - True: pattern passed all checks.
    - False: pattern failed at least one rule:
        1. Contains more than one '*' (too many wildcards).
        2. Contains both '*' and '|' characters (wildcard disallowed when alternation/operator '|' is present).
        3. Contains '*' in the substring after the last '@' (i.e., in the domain/right-side). Note: when pattern has no '@', the substring after the last '@' is the whole string — thus a '*' anywhere in a pattern without '@' will fail rule #3.

Examples of return behavior:
- "user*@example.com" -> True (single '*' in local part).
- "*@example.com" -> True (single '*' in local part).
- "user@exam*ple.com" -> False (wildcard in domain/right-side).
- "user*" -> False (no '@' present; wildcard in entire string is prohibited by rule #3).
- "user*|admin@example.com" -> False (contains both '*' and '|').
- "us*er*@example.com" -> False (more than one '*').

## Raises:
AttributeError (or other exceptions raised by invoked methods)
    If the provided pattern does not support the string methods used (.count, .rsplit) — for example, passing None will result in AttributeError: 'NoneType' object has no attribute 'count'. The function does not perform explicit type checks; it expects a str-like object.

## Constraints:
Preconditions:
- Caller must pass a value that supports .count() and .rsplit() (ideally a Python str).
- The function assumes "pattern" is a single pattern string (not a list or other container).

Postconditions:
- A boolean is returned indicating validity per the three explicit rules in the function.
- The function does not mutate the input or any external state.

## Side Effects:
- None. The function performs no I/O, network calls, file writes, global state mutation, or external service interactions.

## Control Flow:
flowchart TD
    A[Start: receive pattern] --> B{count('*') > 1 ?}
    B -- Yes --> R[Return False]
    B -- No --> C{contains '*' AND contains '|' ?}
    C -- Yes --> R[Return False]
    C -- No --> D{'*' in last segment after last '@' ?}
    D -- Yes --> R[Return False]
    D -- No --> S[Return True]

Notes:
- "last segment after last '@'" is computed by splitting on the last '@' and taking the final element (equivalent to pattern.rsplit('@', 1)[-1]).
- The flow has no loops; three sequential checks determine the result.

## Examples:
Example 1 — Validate a simple local wildcard (allowed):
    pattern = "alice*@example.com"
    result = validate_auth_option(pattern)  # returns True

Example 2 — Wildcard in domain (disallowed):
    pattern = "alice@example*.com"
    result = validate_auth_option(pattern)  # returns False

Example 3 — Multiple wildcards (disallowed):
    pattern = "a*b*@example.com"
    result = validate_auth_option(pattern)  # returns False

Example 4 — Wildcard together with alternation operator (disallowed):
    pattern = "admin|user*@example.com"
    result = validate_auth_option(pattern)  # returns False

Example 5 — Non-string input (caller must guard or handle exceptions):
    pattern = None
    try:
        result = validate_auth_option(pattern)
    except AttributeError:
        # handle invalid input type
        pass

## `flower.views.auth.GoogleAuth2LoginHandler` · *class*

## Summary:
GoogleAuth2LoginHandler is a Tornado request handler that performs an OAuth2 login flow with Google and, on success, validates the returned email against the application's allowlist policy, sets a secure cookie with the user email, and redirects the client to the requested next page.

## Description:
This handler is intended to be mounted in a Tornado web application route (for example, at /auth/google). It uses tornado.auth.GoogleOAuth2Mixin to perform the OAuth2 exchange with Google.

Typical scenario:
- A client requests the login URL. If no OAuth "code" parameter is present, the handler redirects the client to Google's OAuth consent screen (authorize_redirect).
- After Google redirects back with a "code" query parameter, the handler exchanges the code for an access token (get_authenticated_user) and then requests the user's profile (https://www.googleapis.com/userinfo/v2/me) to obtain an email address.
- The handler calls the application's authenticate(...) policy with the configured auth pattern(s) and the retrieved email; if allowed, the handler sets a secure cookie "user" with the email and redirects the client to a next URL.

This class exists to encapsulate the full Google OAuth2 login flow and the post-auth authorization policy check. It keeps the OAuth details and the allowlist check centralized, so application code elsewhere can rely on the cookie set here to indicate an authenticated user.

Known callers/factories:
- Tornado's application/router when configured with a route mapping for this handler.
- No explicit factory in this file; instantiation is handled by Tornado when an incoming request matches the handler's route.

## State:
Class-level attributes:
- _OAUTH_SETTINGS_KEY (str): the settings key used to find OAuth configuration in self.settings. Value: 'oauth'.

Instance-visible state (inherited and used):
- self.settings (dict-like): Tornado application handler settings. This handler expects:
    - settings['oauth'] to be a dict containing:
        - 'redirect_uri' (str): the redirect URI registered with Google and used to exchange the code.
        - 'key' (str): the Google OAuth client id.
  Constraints: Accessing these keys without them present raises KeyError.
- self.application (Application): Tornado application instance. The handler reads:
    - self.application.options.auth: passed to authenticate(...) as the configured allowlist/pattern(s). The authenticate function may return a boolean or a re.Match/None; this handler checks truthiness.
    - self.application.options.url_prefix (optional str): used as a default for the "next" redirect target.
- Methods provided by tornado.auth.GoogleOAuth2Mixin and BaseHandler (inherited):
    - authorize_redirect(...)
    - get_authenticated_user(...)
    - get_auth_http_client()
    - set_secure_cookie(...)

Invariants:
- Before attempting to exchange a returned authorization code, the handler requires settings['oauth']['redirect_uri'] and settings['oauth']['key'] to exist.
- After a successful flow, if the authenticate(...) call is truthy, a secure cookie named "user" will have been set containing the string representation of the user's email.

## Lifecycle:
Creation:
- Instantiated by Tornado when registering the handler in an application route. The class does not define its own __init__, so Tornado/RequestHandler initialization applies.
- No constructor arguments beyond the standard Tornado RequestHandler parameters (application, request).

Usage (method sequence):
1. Client performs an HTTP GET request to the handler URL.
2. get() checks for the query parameter 'code':
   - If no code or code is falsy: calls authorize_redirect(...) to start Google OAuth2 flow (redirects to Google).
   - If code is present: calls get_authenticated_user(redirect_uri=..., code=...) to exchange code for tokens, then calls internal async method _on_auth(user).
3. _on_auth(user):
   - If user is falsy (None/empty): raises tornado.web.HTTPError(403).
   - Extracts access_token from user['access_token'].
   - Calls get_auth_http_client().fetch(...) to GET Google userinfo.
     - If fetch raises any exception, _on_auth catches it and raises tornado.web.HTTPError(403) with the underlying exception message appended.
   - Parses JSON from response.body and extracts the 'email' field.
   - Calls authenticate(self.application.options.auth, email).
     - If authenticate(...) is falsy, raises tornado.web.HTTPError(403) with a clear message instructing how to add the email to the allowlist.
   - Calls set_secure_cookie("user", str(email)) to persist the authenticated identity.
   - Computes next_ from the 'next' query parameter, defaulting to application.options.url_prefix or '/'.
     - If application.options.url_prefix is truthy and next_ does not begin with '/', the code prepends a '/' to next_.
     - Finally, calls self.redirect(next_).

Destruction / cleanup:
- No special cleanup is performed by this handler. Tornado manages request lifecycle. There is no context manager or explicit close() required by this class.

Sequencing constraints and caveats:
- The get() and _on_auth() methods are async and expect to be awaited by Tornado's async request loop.
- The handler assumes that the tornado.auth.GoogleOAuth2Mixin methods work as provided by Tornado. Reimplementation must provide equivalent behavior: authorize_redirect, get_authenticated_user, and get_auth_http_client().fetch.

## Method Map:
flowchart LR
    GET_REQUEST[/GET request received/] --> CHECK_CODE{query 'code' present and truthy?}
    CHECK_CODE -- No --> AUTHORIZE[authorize_redirect(...) -> redirect to Google OAuth consent]
    CHECK_CODE -- Yes --> EXCHANGE[get_authenticated_user(redirect_uri, code)]
    EXCHANGE --> ON_AUTH[_on_auth(user)]
    ON_AUTH --> USER_CHECK{user truthy?}
    USER_CHECK -- No --> RAISE_HTTP403[raise HTTPError(403, 'Google auth failed')]
    USER_CHECK -- Yes --> FETCH[fetch userinfo with access_token]
    FETCH -- Exception --> RAISE_FETCH_ERROR[raise HTTPError(403, f'Google auth failed: {e}')]
    FETCH -- Success --> PARSE[parse JSON, extract 'email']
    PARSE --> AUTHZ[authenticate(app.options.auth, email) truthy?]
    AUTHZ -- No --> RAISE_DENIED[raise HTTPError(403, "Access denied to '<email>'...")]
    AUTHZ -- Yes --> SET_COOKIE[set_secure_cookie("user", email)]
    SET_COOKIE --> COMPUTE_NEXT[get 'next' or default; ensure leading '/']
    COMPUTE_NEXT --> REDIRECT[redirect(next_)]

Note: This diagram describes typical successful and failure paths for a GET request.

## Raises:
Directly raised by this handler's code:
- tornado.web.HTTPError(403, 'Google auth failed')
    - Trigger: _on_auth called with falsy user (no authenticated user returned by get_authenticated_user).
- tornado.web.HTTPError(403, f'Google auth failed: {e}')
    - Trigger: any exception raised while fetching Google userinfo (network error, client error, etc.). The original exception message is included.
- tornado.web.HTTPError(403, "Access denied to '<email>'...") 
    - Trigger: authenticate(self.application.options.auth, email) evaluated as falsy (email not allowed).
Implicit/possible exceptions (raised by underlying calls; not explicitly raised in the code but should be considered by callers/implementers):
- KeyError
    - Trigger: settings['oauth'] missing or missing 'redirect_uri'/'key' entries.
- json.JSONDecodeError (subclass of ValueError)
    - Trigger: response.body cannot be decoded as valid JSON.
- IndexError
    - Trigger: If application.options.url_prefix is truthy and the 'next' parameter is present but equals the empty string, next_[0] access will raise IndexError. (The code accesses next_[0] without ensuring next_ is non-empty.)
- Exceptions from tornado methods (get_authenticated_user, get_auth_http_client().fetch, set_secure_cookie)
    - Trigger: lower-level Tornado errors, network errors, or misconfiguration (e.g., missing cookie_secret may cause cookie-setting issues in Tornado).

## Example:
Typical wiring and flow (described as steps that a developer should reproduce when implementing this handler):

1) Register handler in Tornado application routes so Tornado instantiates it for GET requests to the chosen endpoint (e.g., /auth/google).

2) Provide OAuth settings in application settings:
   - settings['oauth'] = {'redirect_uri': 'https://your.host/auth/google', 'key': '<GOOGLE_CLIENT_ID>'}

3) Configure application.options:
   - application.options.auth should contain the allowlist/pattern(s) understood by the authenticate(...) function.
   - application.options.url_prefix is optional; it influences default redirect target.

4) User visits /auth/google:
   - If no code query param => handler issues authorize_redirect(...) to Google's OAuth consent endpoint.

5) After consent, Google redirects back to /auth/google?code=...:
   - The handler exchanges the code, fetches the profile, extracts the email, validates it via authenticate(...), sets the secure cookie "user" to the email, computes or normalizes the next redirect URL, and redirects the client there.

Implementation notes for reimplementation:
- Ensure the mixin methods used by the original handler are available: authorize_redirect, get_authenticated_user, and get_auth_http_client().fetch.
- Preserve truthiness semantics when calling authenticate(...): the original code treats any truthy return value (True or re.Match object) as allowed.
- Reproduce the error paths that raise HTTP 403 when authentication or authorization fails.
- Reproduce the next_ normalization: if application.options.url_prefix is truthy and next_ does not start with '/', add a leading '/'.

### `flower.views.auth.GoogleAuth2LoginHandler.get` · *method*

## Summary:
Handles an HTTP GET for Google OAuth2 login: either issues a redirect to Google's OAuth2 authorization endpoint to start sign-in, or exchanges an authorization code for credentials and delegates final sign-in processing to _on_auth. The method itself does not directly persist state but causes HTTP side effects (redirects) and delegates cookie-setting/redirecting to _on_auth.

## Description:
- Known callers and lifecycle:
    - Invoked by Tornado's request dispatcher when a GET request is routed to GoogleAuth2LoginHandler (this is the handler's GET lifecycle method).
    - Two-phase lifecycle:
        1. Initiation phase (no valid code): issues an authorization redirect to Google so the user can grant consent.
        2. Completion phase (valid code present): exchanges the authorization code for credentials using the mixin helper get_authenticated_user(...) and then awaits _on_auth(user) to perform post-authentication steps (set cookie, final redirect).
- Why this is a separate method:
    - It cleanly encapsulates the GET entrypoint for Google OAuth2 flows (initiate vs complete) and delegates token-exchange and post-auth side effects to dedicated helpers (the GoogleOAuth2Mixin and _on_auth), improving modularity and testability.

## Args:
- No explicit Python arguments; reads HTTP query parameters:
    - 'code' (str | False): retrieved via self.get_argument('code', False).
        * If absent: get_argument returns default False → treated as "no code" (initiation).
        * If present but empty string (''): get_argument returns '' which is falsy → treated as "no code" (initiation).
        * If present and non-empty string: treated as an authorization code (completion).
    - 'next' (str): not used directly here but consumed inside _on_auth to determine the post-login redirect destination.

## Returns:
- None. Effects are performed via the Tornado HTTP response:
    - Initiation branch: calls authorize_redirect(...) which sends an HTTP redirect response to the client (no return value).
    - Completion branch: awaits get_authenticated_user(...) and then awaits _on_auth(user). _on_auth performs final response actions (cookie and redirect). No explicit return value is produced by this method.

## Raises:
- KeyError:
    - If self.settings does not contain the expected OAuth settings under self._OAUTH_SETTINGS_KEY (default 'oauth'), or if the expected subkeys ('redirect_uri' or 'key') are missing, indexing will raise KeyError.
- TypeError:
    - If self.settings[self._OAUTH_SETTINGS_KEY] exists but is not a mapping (e.g., None or wrong type), attempting to index into it can raise TypeError.
- Propagated exceptions:
    - Exceptions thrown by self.get_authenticated_user(...) (provided by tornado.auth.GoogleOAuth2Mixin) will propagate (network errors, provider errors).
    - Exceptions thrown by self._on_auth(user) will propagate (for example, _on_auth raises tornado.web.HTTPError(403, ...) on failed authentication).
    - authorize_redirect and get_argument may raise their own Tornado exceptions in abnormal situations; these are not caught here.

## State Changes:
- Attributes READ:
    - self.settings — read to obtain OAuth configuration.
    - self._OAUTH_SETTINGS_KEY — class-level key used to index the OAuth settings (value: 'oauth').
    - self.get_argument — called to read the 'code' (and 'next' indirectly later via _on_auth).
    - self.get_authenticated_user — called (awaited) when completing the flow (method provided by GoogleOAuth2Mixin).
    - self.authorize_redirect — called to issue the OAuth2 authorization redirect (provided by Tornado/mixin).
- Attributes WRITTEN:
    - None directly within this method.
    - Note: _on_auth (invoked on completion) writes state: it sets a secure cookie named "user" and performs a final redirect.

## Constraints:
- Preconditions:
    - self.settings must be a mapping containing an entry at key self._OAUTH_SETTINGS_KEY (default 'oauth') with at least:
        * 'redirect_uri' (str): redirect URL registered with Google (used as redirect_uri).
        * 'key' (str): OAuth2 client ID (used as client_id).
    - The handler is running in a Tornado request context so self.get_argument, authorize_redirect, and async/await semantics are valid.
    - get_authenticated_user is provided by tornado.auth.GoogleOAuth2Mixin (this class inherits that mixin).
- Expected oauth settings example:
    - oauth = {
          'redirect_uri': 'https://your-host.example.com/oauth2callback',
          'key': 'GOOGLE_CLIENT_ID',
          'secret': 'GOOGLE_CLIENT_SECRET'  # the secret may be used elsewhere, not in this method
      }
- Postconditions:
    - Initiation (no valid 'code'): authorize_redirect(...) is invoked with these exact arguments:
        * redirect_uri = self.settings['oauth']['redirect_uri']
        * client_id = self.settings['oauth']['key']
        * scope = ['profile', 'email']
        * response_type = 'code'
        * extra_params = {'approval_prompt': ''}
      The HTTP response will be a redirect to Google's authorization endpoint.
    - Completion (valid non-empty 'code'): get_authenticated_user(redirect_uri=..., code=...) is awaited. On successful return, _on_auth(user) is awaited and is expected to set a secure cookie and redirect the client. If get_authenticated_user returns a falsy value or _on_auth raises, the exception will propagate and the request may terminate with an error.

## Side Effects:
- Network I/O:
    - Completion branch causes get_authenticated_user(...) to perform OAuth token exchange with Google's servers (network call). _on_auth performs additional network fetch to Google's userinfo endpoint.
- HTTP response side effects:
    - Initiation branch: authorize_redirect(...) issues a redirect response to Google's OAuth2 consent page (client is redirected).
    - Completion branch: _on_auth sets a secure cookie ("user") and issues a redirect to the 'next' URL.
- No file I/O or persistent mutation of handler attributes occurs in this method itself.

### `flower.views.auth.GoogleAuth2LoginHandler._on_auth` · *method*

## Summary:
Performs post-Google-OAuth processing: validates the OAuth response, fetches the user's email from Google's userinfo endpoint, enforces configured allowlist/auth policy, sets the authenticated user cookie on the handler, and issues an HTTP redirect to the next URL.

## Description:
This async helper is intended to run after the OAuth provider (Google) has returned a user object (the OAuth exchange). Typical caller: the OAuth callback flow of the GoogleAuth2LoginHandler after a successful token exchange (i.e., in the handler that receives the OAuth provider response). It is separated into its own method to isolate the network call, error handling, auth-policy check, cookie-setting, and redirect logic so the handler's control flow is clearer and easier to test.

Call context / lifecycle stage:
- Invoked after receiving an OAuth result (user) from Google's auth flow.
- Runs inside a Tornado RequestHandler instance (self) and performs an async HTTP call to Google's userinfo API.

Why this logic is its own method:
- Centralizes the sequence: validate user object, perform userinfo fetch, check allowlist, set cookie, and redirect.
- Simplifies unit testing and error-path handling without inlining these steps into larger methods.

## Args:
    user (dict): OAuth result object returned by the earlier OAuth/token exchange.
        - Required key: 'access_token' (str) — OAuth access token to include in the Authorization Bearer header when calling Google's userinfo endpoint.
        - Allowed values: any truthy dict with a valid access_token string. If user is falsy (None, empty dict, etc.), the method immediately raises an HTTP 403.

## Returns:
    None.
    - On success: the method does not return a value; it sets a secure cookie and redirects the client (i.e., sends an HTTP redirect response).
    - On failure: it raises an HTTPError or allows other exceptions to propagate (see Raises).

## Raises:
    tornado.web.HTTPError(403, 'Google auth failed')
        - Raised when the provided user argument is falsy (e.g., None, {}).

    tornado.web.HTTPError(403, f'Google auth failed: {e}')
        - Raised when the async HTTP fetch to Google's userinfo endpoint raises any Exception (network error, timeout, underlying client error). The original exception string is included in the message.

    tornado.web.HTTPError(403, message)
        - Raised when the email extracted from Google's userinfo is not authorized by the configured auth policy (authenticate(...) returns a falsy value). The message contains the offending email and guidance about adding the email to the configured auth allowlist.

    Other uncaught exceptions that may propagate:
        - json.JSONDecodeError: if response.body is not valid JSON.
        - KeyError: if the parsed JSON does not contain an 'email' key.
        - TypeError / AttributeError: if response.body is None or not bytes, or if user['access_token'] is missing and indexing fails.
    Note: Only the explicit HTTPError cases above are converted to 403 responses by this method; other exceptions will propagate and typically result in a 500 error unless handled upstream.

## State Changes:
Attributes READ:
    - self.application.options.auth (used as the pattern/config passed to authenticate)
    - self.application.options.url_prefix (used to compute redirect 'next' default and to normalize next_)

Attributes WRITTEN:
    - None of the handler's Python attributes on self are directly overwritten by this method.
    - However, handler state exposed to the client is modified via:
        - set_secure_cookie("user", str(email)) — sets a cookie in the HTTP response (external client-visible state).
        - redirect(next_) — sends an HTTP redirect response (changes response state and ends the request).

## Constraints:
Preconditions:
    - user must be a truthy mapping and must contain the key 'access_token' whose value is a string or a value convertible to the Authorization header.
    - self.get_auth_http_client() must return an object with an awaitable fetch(...) method which yields a response object having a bytes-like .body attribute.
    - self.application.options.auth must be set (can be any pattern supported by authenticate()).
    - self.get_argument is callable for 'next' (typical of Tornado RequestHandler).

Postconditions:
    - On successful completion:
        - A secure cookie named "user" is set to the email string obtained from Google's userinfo.
        - The client is redirected to the computed next_ URL (either the 'next' request argument or application.options.url_prefix or '/').
    - On failure:
        - A tornado.web.HTTPError(403, ...) is raised for the explicit failure cases listed under Raises; other exceptions may propagate unchanged.

## Side Effects:
    - Network I/O: performs an outbound HTTPS GET to https://www.googleapis.com/userinfo/v2/me with an Authorization: Bearer <access_token> header.
    - HTTP response mutation:
        - Sets a secure cookie named "user".
        - Issues an HTTP redirect response (calls redirect()) which will short-circuit normal handler continuation.
    - No filesystem I/O or persistent DB mutations are performed by this method.

## Behavior detail and edge cases:
    - The method decodes response.body using UTF-8 and then parses JSON; malformed JSON or missing 'email' will raise exceptions (JSONDecodeError or KeyError) which are not caught by this method.
    - authenticate(...) may return a boolean or a match-like object (per the authenticate implementation). The code treats its return value by truthiness: any falsy value (False, None, empty) is treated as denial.
    - When computing next_:
        - next_ defaults to the 'next' request argument if present; otherwise it falls back to application.options.url_prefix or '/'.
        - If application.options.url_prefix is set and next_ does not start with '/', a leading '/' is prepended to next_.
    - Exceptions thrown by the auth-http-client fetch call (timeouts, connection errors, etc.) are wrapped and re-raised as a 403 with the original exception message included for debugging.

## Example (conceptual):
    - Called after obtaining OAuth tokens, where `user = {'access_token': '<token>'}`.
    - If token is valid and authenticate(...) allows the returned email, the method sets the secure cookie and redirects the browser to the intended page.

## `flower.views.auth.LoginHandler` · *class*

## Summary:
LoginHandler is a thin, configurable factory object that delegates construction to a pluggable authentication handler implementation (configured via options.auth_provider), falling back to NotFoundErrorHandler when no provider is configured.

## Description:
This class exists so application routing can refer to a stable name (LoginHandler) while the actual request-handler implementation can be swapped at runtime via configuration. When Python attempts to construct LoginHandler (for example, Tornado's request-dispatch pipeline instantiates the handler for an incoming HTTP request), LoginHandler.__new__ intercepts construction and returns whatever celery.utils.imports.instantiate(...) produces for the configured provider.

Scenarios where this is used:
- Tornado constructs request handlers while dispatching HTTP requests; LoginHandler appears in URL routing tables so Tornado will call LoginHandler(*args, **kwargs) when a matching request arrives.
- Tests or application code that directly instantiate LoginHandler will receive an instance of the configured provider rather than a plain LoginHandler.

Motivation and responsibility boundary:
- Responsibility: select and instantiate the concrete authentication handler implementation at object-creation time and forward all constructor arguments to that implementation.
- Boundary: It does not implement any request handling itself and does not perform any post-instantiation wiring. All behaviour beyond instantiation is the responsibility of the chosen provider instance.

## State:
This class intentionally has no instance state of its own because it never returns a plain LoginHandler instance; instead it returns an instance of the configured provider.

Attributes (observed/used):
- options.auth_provider (global, imported from tornado.options.options)
  - Type: any value accepted by celery.utils.imports.instantiate (commonly a class object or import path string)
  - Valid values: falsy (None, empty string, etc.) or a provider spec acceptable to instantiate
  - Invariant: if falsy, NotFoundErrorHandler is used as the provider.

Instance attributes:
- None defined by LoginHandler itself. The returned object will have whatever state the provider's class sets up.

Class invariants:
- Calling LoginHandler(...) always returns an object that was constructed by celery.utils.imports.instantiate with provider = options.auth_provider or NotFoundErrorHandler.
- No attributes of the original LoginHandler class are modified during this process.

## Lifecycle:
Creation:
- How to instantiate: call LoginHandler(*args, **kwargs) (e.g., Tornado will do this automatically when dispatching requests).
- Required args: exactly the arguments that the underlying provider's constructor expects; LoginHandler does not impose or validate any argument schema — it simply forwards all positional and keyword arguments to instantiate.
- Factory behavior: __new__ returns instantiate(provider, *args, **kwargs) instead of returning an instance of LoginHandler.

Usage:
- Typical sequence:
  1. Tornado (or caller) invokes LoginHandler(*args, **kwargs).
  2. Python calls LoginHandler.__new__(LoginHandler, *args, **kwargs).
  3. __new__ computes provider = options.auth_provider or NotFoundErrorHandler.
  4. __new__ calls celery.utils.imports.instantiate(provider, *args, **kwargs).
  5. The provider instance returned by instantiate is handed back to the caller; Python then (normally) would call __init__ on that instance if instantiate produced a fresh object requiring initialization (instantiate is expected to return a ready instance).
  6. The returned provider instance is used to handle the request as a Tornado RequestHandler.

Destruction / cleanup:
- LoginHandler itself has no cleanup responsibilities.
- Any cleanup or resource management is implemented by the concrete provider if required (e.g., provider may implement on_finish, close, or other lifecycle hooks used by Tornado).

Sequencing constraints:
- There is no additional sequencing enforced by LoginHandler beyond the normal Python object construction order; callers must supply constructor arguments appropriate for the configured provider.

## Method Map:
flowchart LR
    A[Tornado or caller calls LoginHandler(*args,**kwargs)] --> B[LoginHandler.__new__ invoked]
    B --> C{options.auth_provider truthy?}
    C -- Yes --> D[instantiate(options.auth_provider, *args, **kwargs)]
    C -- No  --> E[instantiate(NotFoundErrorHandler, *args, **kwargs)]
    D --> F[Return provider instance to caller]
    E --> F

(Note: the diagram shows the high-level flow; instantiate may dynamically import modules or create instances and may raise exceptions during this process.)

## Raises:
LoginHandler.__new__ does not explicitly raise its own exceptions, but it will propagate exceptions raised by celery.utils.imports.instantiate or by the provider's constructor. Common propagated errors include:
- ImportError / ModuleNotFoundError: if the configured provider is given as an import path that cannot be resolved.
- AttributeError or LookupError: if the import path does not reference a constructable object.
- TypeError: if the provider's constructor signature does not accept the forwarded arguments.
- Any exception raised inside the provider's __init__ will propagate to the caller.

If options.auth_provider is falsy and NotFoundErrorHandler is returned:
- The immediate construction succeeds, but NotFoundErrorHandler's HTTP verb handlers (get/post) will raise tornado.web.HTTPError(404) when those methods are invoked to handle a request.

## Example (usage, described in prose):
- Routing: the application registers LoginHandler in Tornado routes (e.g., (r"/login", LoginHandler)).
- Request-time:
  1. A request matches the route and Tornado attempts to construct the handler: LoginHandler(application, request, **kwargs).
  2. LoginHandler.__new__ runs and selects provider = options.auth_provider if set, else NotFoundErrorHandler.
  3. instantiate(provider, application, request, **kwargs) is invoked and returns a handler instance of the provider type.
  4. Tornado continues the normal request lifecycle using that returned handler.
- In tests: directly calling LoginHandler(...) returns an instance of the configured provider; tests should assert on the behavior of that provider, not on LoginHandler itself.

## Implementation notes for reimplementation:
- The class must override __new__ and return instantiate(options.auth_provider or NotFoundErrorHandler, *args, **kwargs).
- Do not call super().__new__ or attempt to initialize LoginHandler itself — the intent is to let instantiate produce and return the object.
- Ensure the module imports:
  - celery.utils.imports.instantiate must be available under the name instantiate.
  - options must be imported from tornado.options and provide attribute auth_provider.
  - NotFoundErrorHandler must be available as the fallback provider.
- Keep __new__ minimal and free of side-effectful logic beyond calling instantiate so that all provider selection is centralized and predictable.

### `flower.views.auth.LoginHandler.__new__` · *method*

## Summary:
Overrides object construction to delegate creating the actual handler instance to a pluggable auth provider (configured via options.auth_provider), falling back to NotFoundErrorHandler when no provider is configured.

## Description:
This __new__ method intercepts attempts to instantiate the LoginHandler class and instead returns the result of calling celery.utils.imports.instantiate(...) with the selected provider and the original construction arguments.

Known callers and invocation context:
- Tornado framework or any code that constructs the handler class (for example, Tornado's RequestHandler construction pipeline when dispatching an HTTP request). The call site is whenever Python evaluates LoginHandler(*args, **kwargs) — typically during request handling.
- Any direct code that instantiates LoginHandler in tests or application code.

Lifecycle stage:
- Executed at object construction time, before __init__ of any LoginHandler-like object would run (since __new__ controls the object returned).

Why this logic is a separate __new__:
- Enables runtime-pluggable replacement of the LoginHandler implementation via configuration (options.auth_provider) so a custom authentication handler can replace the built-in one without modifying application routing.
- Centralizes provider selection and instantiation in one place, preventing the need to branch in multiple call sites.

## Args:
    cls (type): The class being constructed (LoginHandler). Not used to produce the returned object except as the conventional __new__ receiver.
    *args (tuple): Positional arguments forwarded unchanged to the provider's constructor via instantiate.
    **kwargs (dict): Keyword arguments forwarded unchanged to the provider's constructor via instantiate.

Allowed/expected values:
- options.auth_provider: a configured provider value (may be falsy). This value is passed as the first argument to instantiate; it should be whatever celery.utils.imports.instantiate accepts (commonly a class object or an import path string). If falsy, NotFoundErrorHandler is used as the provider.

## Returns:
    object: The instance returned by celery.utils.imports.instantiate(options.auth_provider or NotFoundErrorHandler, *args, **kwargs).

Possible values / edge cases:
- If options.auth_provider is falsy (None, empty string, etc.), the returned object is an instance of NotFoundErrorHandler constructed with the forwarded args/kwargs.
- The concrete type is determined by the configured provider; callers must not assume the returned type is an instance of cls.
- If instantiate fails, no object is returned (see Raises).

## Raises:
- This method does not explicitly raise its own exceptions in the source code, but it will propagate any exception raised by celery.utils.imports.instantiate(...) (for example: import/lookup errors, TypeError on wrong constructor signature, or any exception raised during the provider's __init__). Those exceptions occur during instantiation and are not handled here.
- Note: NotFoundErrorHandler itself does not raise at construction time, but its HTTP verb handlers (get/post) raise tornado.web.HTTPError(404) when invoked at request-time.

## State Changes:
Attributes READ:
- None of self.<attr> are read by this method.
- It does read the global configuration value options.auth_provider.

Attributes WRITTEN:
- None of self.<attr> are modified by this method. The method returns an object produced by instantiate instead of producing/initializing the default LoginHandler instance.

## Constraints:
Preconditions:
- The global options object must be available and importable; options.auth_provider should be accessible.
- The configured provider (options.auth_provider) must be valid for celery.utils.imports.instantiate (i.e., an acceptable class object or import path recognized by instantiate), otherwise instantiate will raise.

Postconditions:
- An instance of the selected provider has been created and returned to the caller.
- No attributes on the original class object (cls) are modified.
- The caller of LoginHandler(...) receives the instantiated provider object in place of a LoginHandler instance.

## Side Effects:
- Dynamic import or lookup activity performed by celery.utils.imports.instantiate (may import modules or resolve dotted paths).
- Execution of the provider's constructor (__init__), which may perform arbitrary side effects (I/O, registration, database access, etc.) depending on the provider implementation.
- If NotFoundErrorHandler is selected and later used to handle requests, its get/post methods will raise tornado.web.HTTPError(404) when invoked (this is a runtime effect, not an immediate side effect of __new__).

## `flower.views.auth.GithubLoginHandler` · *class*

## Summary:
GithubLoginHandler is a Tornado request handler that implements the GitHub OAuth2 login flow: it either redirects the browser to GitHub's authorization URL or handles the callback by exchanging a code for an access token, fetching the user's verified emails, authorizing one via the application's configured pattern(s), setting a secure cookie with the chosen email, and redirecting the user to the next page.

## Description:
This handler is intended to be mounted as the HTTP endpoint that implements GitHub login for the Flower web UI. Typical deployment:
- The Tornado application settings must contain an 'oauth' mapping with at minimum the keys 'key' (client_id), 'secret' (client_secret), and 'redirect_uri' (the callback URL GitHub will invoke).
- The application must configure application.options.auth as the email-matching pattern(s) consumed by the authenticate(...) helper (see its behavior in module memory).
- Routes: a URL (e.g., /auth/github) should be mapped to GithubLoginHandler so GitHub can redirect with a 'code' query parameter, and users can also be sent to that URL to initiate login.

Responsibility boundary:
- This class encapsulates the OAuth2 authorization-code flow with GitHub only (token exchange and retrieving user emails). It does not modify global configuration, persist user records, or perform multi-factor checks. It sets a secure cookie named "user" with the chosen email and performs an HTTP redirect to complete the login sequence.

Known callers / instantiation:
- Tornado creates instances when a request matches the route mapped to this handler. There is no explicit factory in this class; it relies on Tornado's RequestHandler instantiation.

## State:
Class-level constants (immutable at runtime unless environment changes):
- _OAUTH_DOMAIN (str): hostname for GitHub API; default read from FLOWER_GITHUB_OAUTH_DOMAIN environment variable or "github.com".
- _OAUTH_AUTHORIZE_URL (str): constructed authorize URL, e.g., https://github.com/login/oauth/authorize
- _OAUTH_ACCESS_TOKEN_URL (str): constructed token exchange URL, e.g., https://github.com/login/oauth/access_token
- _OAUTH_NO_CALLBACKS (bool): set to False (used by Tornado OAuth mixin to indicate callback behavior)
- _OAUTH_SETTINGS_KEY (str): name of settings key where OAuth configuration is stored; default 'oauth'

Instance-visible state and invariants:
- self.settings (mapping-like): expected to contain self.settings['oauth'] which must be a mapping with keys:
    - 'key' (str): GitHub client id
    - 'secret' (str): GitHub client secret
    - 'redirect_uri' (str): the callback URL to pass to GitHub
  Invariant: handler operations that exchange code or start authorization assume these keys exist; missing keys will cause KeyError when accessed.
- self.application.options (object): used for application-level options:
    - .auth (str): pattern(s) passed to authenticate(...) to validate emails
    - .url_prefix (str or falsy): optional URL prefix used to normalize redirect destinations
  Invariant: .auth must be present and meaningful for email validation; otherwise no email will be accepted.
- Cookies:
    - sets a secure cookie named "user" whose value is the selected email (lowercased); invariant: cookie contains exactly one email string when login succeeds.

Notes on authenticate(...) usage:
- authenticate may return bool or a re.Match object (see its docs). This handler treats the return value truthily/falsily in conditionals; callers that expect a strict boolean should wrap it in bool() — this handler relies on truthiness.

## Lifecycle:
Creation:
- No explicit constructor arguments. The handler is instantiated by Tornado when a matching route is called (standard RequestHandler lifetime).

Usage:
- Typical call sequence for an HTTP GET:
    1. GET request arrives to the handler route.
    2. GithubLoginHandler.get() is invoked.
    3. get() checks request arguments for 'code':
        - If 'code' is missing: it calls authorize_redirect(...) (provided by tornado.auth.OAuth2Mixin) to redirect the user agent to GitHub's authorization page with client_id, scope=['user:email'], response_type='code', and redirect_uri from settings['oauth'].
        - If 'code' is present: it calls get_authenticated_user(redirect_uri, code) to exchange the authorization code for an access token, then calls _on_auth(user) with the token response dict.
    4. get_authenticated_user(...) performs an HTTP POST to the OAuth access token endpoint and returns the JSON-decoded response (a mapping expected to include 'access_token'), or raises tornado.auth.AuthError if the token endpoint response indicates an error.
    5. _on_auth(user):
        - Validates user is truthy; otherwise raises tornado.web.HTTPError(500).
        - Extracts access_token from the user mapping.
        - Fetches the GitHub user emails endpoint (/user/emails) using the token in Authorization header.
        - Parses the JSON response body (list of email objects), collects lowercased email['email'] values for which email['verified'] is truthy AND authenticate(self.application.options.auth, email['email']) evaluates truthy.
        - If no authorized emails are found: raises tornado.web.HTTPError(403) with an "Access denied" message.
        - Otherwise: selects one email (emails.pop()), sets it in a secure cookie "user", computes next_ from the 'next' query argument or application.options.url_prefix or '/', normalizes with a leading slash when necessary, and redirects to next_.
- Destruction / cleanup:
    - There are no special cleanup steps; no files or background resources are managed by this handler. Tornado's normal request lifecycle applies.

Sequencing constraints:
- get() must be invoked in a normal Tornado request context; get_authenticated_user and _on_auth assume the Tornado IOLoop and AsyncHTTPClient are available (they are async methods and use await).
- get_authenticated_user requires that self.settings['oauth'] contains valid client credentials before calling.

## Method Map:
flowchart TD
    A[GET request] --> B{has 'code' query arg?}
    B -- No --> C[authorize_redirect(redirect_uri, client_id, scope, ...)] --> D[Browser -> GitHub authorize page]
    B -- Yes --> E[get_authenticated_user(redirect_uri, code)] --> F{token response}
    F -- error in response --> G[raise tornado.auth.AuthError]
    F -- ok --> H[_on_auth(user)] --> I[fetch /user/emails with Authorization: token <access_token>]
    I --> J[parse JSON list of emails] --> K[filter by email['verified'] and authenticate(options.auth, email)]
    K -- no matches --> L[raise HTTPError(403) Access denied]
    K -- matches --> M[set_secure_cookie("user", selected_email)] --> N[compute/normalize next_] --> O[redirect(next_)]

Notes: get_authenticated_user and _on_auth are async coroutines and use await on HTTP fetches. authorize_redirect triggers an immediate HTTP 302/redirect response to the browser.

## Raises:
- get_authenticated_user:
    - tornado.auth.AuthError: raised if the HTTP response from the OAuth access token endpoint has a truthy .error attribute (the handler converts this into an AuthError).
    - Possible network/HTTP client exceptions: network failures or non-2xx responses may raise tornado.httpclient errors (propagated from the fetch call).
- get:
    - No explicit raise beyond those coming from called methods. If _on_auth raises an HTTPError (500 or 403) these propagate and result in corresponding HTTP responses.
- _on_auth:
    - tornado.web.HTTPError(500, 'OAuth authentication failed') if the `user` argument is falsy or missing required fields (e.g., no 'access_token').
    - tornado.web.HTTPError(403, message) if no verified & authorized emails are found.
    - Network/HTTP client exceptions may propagate from the fetch call to the GitHub API emails endpoint.
- Note: KeyError will occur if expected keys are missing from self.settings['oauth'] (e.g., 'key', 'secret', 'redirect_uri').

## Edge cases and implementation notes:
- Email selection:
    - The code lowercases emails when collecting them, and then calls emails.pop() to choose one. pop() returns and removes the last item in the list — if the GitHub API returned multiple authorized emails, the chosen email will be the last in the returned list. Callers should not assume deterministic priority beyond API order.
- authenticate(...) returns either a boolean or a re.Match/None object. The handler treats the return value by truthiness. If pattern matching is expected to return a strict bool, wrap with bool() in other contexts.
- If application.options.url_prefix is falsy, next_ defaults to '/'.
- If the 'next' argument contains no leading slash while a url_prefix exists, the handler prepends a '/' to next_ to ensure a path-like redirection.
- If settings['oauth'] is misconfigured or missing keys, explicit KeyError or misleading OAuth flow errors will occur. Ensure correct configuration before using this handler.

## Example:
- Configuration prerequisites (pseudocode; provided here for clarity of expected settings):
    - settings['oauth'] = {'key': '<GITHUB_CLIENT_ID>', 'secret': '<GITHUB_CLIENT_SECRET>', 'redirect_uri': 'https://yourhost/auth/github'}
    - application.options.auth = 'alice@example.com|devops@example.com'  (or a pattern supported by authenticate)
    - application.options.url_prefix = '/flower'  (optional)

- Typical login flow (high-level):
    1. User visits /auth/github (GET without 'code').
        - Handler calls authorize_redirect(...), user is redirected to GitHub to authorize the app.
    2. GitHub redirects back to /auth/github?code=XXXXX.
        - Handler.get() detects 'code', calls get_authenticated_user(redirect_uri, code).
        - Handler exchanges code at the access token endpoint, receives JSON including 'access_token'.
        - Handler calls _on_auth(user): fetches user's emails, filters for verified & allowed via authenticate(...).
        - If allowed, handler sets_secure_cookie("user", "<chosen_email>") and redirects the user to the configured next_ URL.
    3. Post-redirect, the application can read the secure cookie "user" to identify the logged-in user.

### `flower.views.auth.GithubLoginHandler.get_authenticated_user` · *method*

## Summary:
Exchanges the OAuth authorization code for an access token by POSTing a URL-encoded form to the provider's token endpoint and returns the provider's JSON response as a Python dict. This operation performs network I/O but does not modify handler state.

## Description:
This asynchronous method implements the token-exchange step of the OAuth2 authorization-code flow. It constructs an application/x-www-form-urlencoded request body with the authorization code, redirect URI, and client credentials from handler settings, then posts it to the configured access-token URL. After awaiting the HTTP response, it checks the response for an error and returns the decoded JSON payload.

Known callers and lifecycle:
- Called by GithubLoginHandler.get when an OAuth callback contains a 'code' query parameter. That occurs during request handling of the OAuth provider redirect (after user authorization).
- Separated from the GET handler because token exchange is a distinct network operation with its own error handling; extracting it simplifies testing, reuse, and clarity of the GET flow.

Request details:
- HTTP method: POST
- URL: self._OAUTH_ACCESS_TOKEN_URL (class attribute typically set to the provider's access-token endpoint)
- Headers sent:
    - Content-Type: application/x-www-form-urlencoded
    - Accept: application/json
- Form body fields (URL-encoded):
    - redirect_uri: the provided redirect_uri argument
    - code: the provided authorization code
    - client_id: taken from self.settings[self._OAUTH_SETTINGS_KEY]['key']
    - client_secret: taken from self.settings[self._OAUTH_SETTINGS_KEY]['secret']
    - grant_type: "authorization_code"

## Args:
    redirect_uri (str): Redirect URI that must match the provider-registered redirect for this client. Must be non-empty and match the original authorization request.
    code (str): The authorization code received from the OAuth provider. Must be a non-empty string.

## Returns:
    dict: The provider's response decoded from JSON (json.loads on the UTF-8-decoded response body). Common keys for OAuth2 token responses include 'access_token', 'token_type', and 'scope', but exact contents depend on the provider.

## Raises:
    tornado.auth.AuthError: Raised when the HTTP response object is returned with a truthy response.error attribute. The exception message includes the raw response object.
    UnicodeDecodeError: If response.body cannot be decoded as UTF-8 (raised by response.body.decode('utf-8')).
    json.JSONDecodeError: If the UTF-8-decoded response body is not valid JSON.
    Any exception raised by the underlying HTTP client fetch (e.g., network errors, timeouts, or HTTP client exceptions) will propagate to the caller.

## State Changes:
    Attributes READ:
        self._OAUTH_SETTINGS_KEY: used to index into self.settings to locate OAuth client credentials.
        self.settings: reads self.settings[self._OAUTH_SETTINGS_KEY]['key'] and ['secret'].
        self._OAUTH_ACCESS_TOKEN_URL: the target URL for the token exchange.
        self.get_auth_http_client (method): invoked to obtain an HTTP client used for the POST.
    Attributes WRITTEN:
        None — the method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - self.settings must contain an entry at key self._OAUTH_SETTINGS_KEY that is a mapping containing string values for 'key' and 'secret'.
        - self.get_auth_http_client() must return an object exposing an awaitable fetch(url, **kwargs) API that yields a response with .error and .body attributes (or raises on error).
        - redirect_uri must match the redirect URI registered with the OAuth provider for this client.
        - code must be a valid authorization code obtained from the provider.
    Postconditions:
        - No handler attributes are modified by this method.
        - On success, a dict parsed from the provider's JSON response is returned.
        - On failure, an exception is raised and no return value is produced.

## Side Effects:
    - Network I/O: performs an outbound HTTP POST to self._OAUTH_ACCESS_TOKEN_URL.
    - May raise exceptions originating from the HTTP client or network stack which propagate to the caller.
    - Does not set cookies, headers, or storage — higher-level handlers should act on the returned token (for example, to fetch user info or set session cookies).

### `flower.views.auth.GithubLoginHandler.get` · *method*

## Summary:
Handle an incoming HTTP GET to start or complete the GitHub OAuth2 login flow — either redirecting the user to GitHub's authorization page or exchanging the returned authorization code for an access token and delegating post-auth processing.

## Description:
This method is the Tornado RequestHandler entry point for the GitHub OAuth2 login route. It is invoked by Tornado's request dispatch when a client issues a GET request to the route mapped to GithubLoginHandler (typically the OAuth login/callback URL). The method implements a two-phase flow:

- Authorization phase (no "code" query parameter present): it calls the OAuth mixin's authorize_redirect to send an HTTP redirect to GitHub's user-authorization page, requesting the 'user:email' scope.
- Callback phase (the provider redirected back with a "code" query parameter): it exchanges the code for an access token by calling get_authenticated_user and then calls _on_auth to complete login (e.g., verifying allowed emails, setting a secure cookie, and redirecting to the next page).

Why this logic is a separate method:
- It is the canonical HTTP GET handler for this route and must run in the request/response context (read from query arguments, issue redirects, or await async token exchange). Keeping it as its own method keeps the request lifecycle clear and isolates the routing behavior from token-exchange and post-auth processing (which are delegated to get_authenticated_user and _on_auth respectively).

Known callers:
- Tornado's HTTP request dispatcher when a GET request arrives at the URL configured to use GithubLoginHandler. This is invoked during the web request handling pipeline (request dispatch -> handler.get()).

## Args:
None (method signature: async def get(self) -> None)

## Returns:
None (returns implicitly after completing the request handling). The method either:
- Issues an HTTP redirect response (via authorize_redirect) and returns, or
- Awaits internal async calls, then delegates to _on_auth which will perform further response actions (set cookies and redirect). In all code paths the handler ends by writing an HTTP response (redirect) rather than returning application data.

## Raises:
- KeyError: if required OAuth configuration keys are missing from self.settings[self._OAUTH_SETTINGS_KEY] (e.g., 'redirect_uri' or 'key') — this arises because the method directly indexes those dict keys.
- tornado.auth.AuthError: may be raised by get_authenticated_user if the token exchange HTTP request fails (propagated; not caught here).
- tornado.web.HTTPError: may be raised by _on_auth (for example, 500 or 403 in the post-auth checks) and will propagate to the Tornado request machinery.
- Any exceptions raised by authorize_redirect (unlikely in normal use) or by underlying Tornado I/O operations may propagate.

## State Changes:
Attributes READ:
- self.settings — read to access self.settings[self._OAUTH_SETTINGS_KEY]['redirect_uri'] and, for the authorization branch, ['key'].
- self._OAUTH_SETTINGS_KEY — class-level constant used as a dict key into settings.
- self.get_argument(...) — reads query arguments 'code' and (in delegated methods) possibly others (e.g., 'next' in _on_auth).
- Methods invoked (read access to method attributes):
  - self.get_authenticated_user(...)
  - self._on_auth(...)
  - self.authorize_redirect(...)

Attributes WRITTEN:
- None directly. (Any state writes — setting secure cookies or redirects — are performed by delegate methods such as _on_auth or authorize_redirect.)

## Constraints:
Preconditions:
- self.settings must contain a mapping under the key self._OAUTH_SETTINGS_KEY (default 'oauth') with at least:
  - 'redirect_uri' (a fully-qualified callback URL string)
  - 'key' (the OAuth client_id) when starting authorization
- The handler must be running within a Tornado RequestHandler context (so that get_argument, redirect, and cookie-setting features are available).
- The network environment must allow outbound HTTP(S) to the OAuth provider for token exchange during the callback phase.

Postconditions:
- If the request lacked a 'code' query parameter: an HTTP redirect response is sent (to the provider's authorization endpoint) and the handler returns.
- If the request included a 'code' query parameter and the token exchange and _on_auth succeed: control is delegated to _on_auth which will complete login (typically by setting a secure cookie and redirecting the user). If token exchange or _on_auth fails, an exception is raised and the request will terminate with an error status.

## Side Effects:
- When no 'code' is present: issues an HTTP redirect to the OAuth provider's authorization endpoint (via authorize_redirect). This sends response headers and ends the request.
- When 'code' is present: performs an outbound HTTP request to exchange the authorization code for an access token (via get_authenticated_user) — network I/O — and then delegates to _on_auth which performs further I/O and response mutations (may set secure cookies and issue a redirect).
- Exceptions from underlying calls will propagate and be converted by Tornado into HTTP error responses according to the framework's behavior.

### `flower.views.auth.GithubLoginHandler._on_auth` · *method*

## Summary:
Handles post-OAuth processing for a GitHub-authenticated user: validates the returned OAuth token, fetches the user's verified emails from GitHub, authorizes one of the emails against the application's auth policy, stores the chosen email in a secure cookie, and redirects the client to the next URL. On failure it raises an HTTPError to abort the request.

## Description:
This asynchronous helper is invoked after an OAuth code exchange has produced user information (the caller is GithubLoginHandler.get after get_authenticated_user returns). It encapsulates the HTTP call to the GitHub API to obtain the account's email addresses and centralizes the decision logic for whether any of those emails are permitted by the application configuration.

Why this logic is a separate method:
- Separates concerns: exchange/token retrieval (get_authenticated_user) vs. authorization, cookie placement and redirection.
- Improves testability and readability by isolating GitHub email lookup and app-specific authorization.
- Reused as a single place to enforce application auth policy and to prepare the HTTP response (cookie + redirect).

Known callers and invocation point:
- Called by GithubLoginHandler.get after successfully exchanging an OAuth code for an access token:
  * Lifecycle step: OAuth callback handling -> token exchange -> authorization + session creation -> redirect.

## Args:
    user (dict):
        - Required mapping (typically the decoded JSON returned by the OAuth token endpoint).
        - Expected keys: 'access_token' (str). If missing, a KeyError will be raised by the implementation.
        - Typical shape: {"access_token": "<token>", ...}

## Returns:
    None
    - On success the method does not return a value; instead it sets a secure cookie and issues an HTTP redirect to the client.
    - On failure the method raises a tornado.web.HTTPError (see Raises).

## Raises:
    tornado.web.HTTPError(500, 'OAuth authentication failed')
        - Condition: the provided user value is falsy (None or empty). This indicates the OAuth token exchange did not produce valid user info.

    tornado.web.HTTPError(403, <message>)
        - Condition: GitHub returned no verified email addresses that pass the application's auth policy (access denied).

    KeyError
        - Condition: expected keys missing from the user dict or from items in the emails list (for example, user['access_token'] or email['email'] missing). These are not caught by the method.

    json.JSONDecodeError
        - Condition: the response body fetched from the GitHub API is not valid JSON.

    tornado.httpclient.HTTPError (or other exceptions raised by the HTTP client)
        - Condition: network errors, non-2xx responses or other failures during the HTTP fetch to the GitHub API. The exact exception depends on the async HTTP client used by get_auth_http_client().

    Any exception raised by authenticate(self.application.options.auth, email) (e.g., TypeError, re.error)
        - Condition: problems inside the authenticate function or when it is called with unexpected types.

## State Changes:
Attributes READ:
    - self._OAUTH_DOMAIN
    - self.application.options.auth
    - self.application.options.url_prefix

Attributes WRITTEN:
    - None (the method does not modify attributes on self)

Notes:
    - The method mutates the outgoing HTTP response via set_secure_cookie and redirect (see Side Effects), but it does not change Python-level attributes on the handler instance.

## Constraints:
Preconditions:
    - self.get_auth_http_client() must return a working asynchronous HTTP client with a fetch method.
    - user must be a mapping containing the key 'access_token' whose value is a valid GitHub access token (string).
    - The GitHub API endpoint https://api.{self._OAUTH_DOMAIN}/user/emails must be reachable and must return JSON in the expected format (a list of objects containing at minimum 'email' and 'verified' keys).

Postconditions:
    - If a permitted verified email is found:
        * A secure cookie named "user" is set to the selected email (string form, lowercased).
        * The handler issues a redirect to the 'next' URL determined from the request or application configuration.
    - If no permitted verified email is found: an HTTPError(403) is raised and no cookie or redirect is performed.
    - If user input is invalid or an upstream error occurs: an appropriate exception is raised (see Raises).

## Side Effects:
    - External HTTP request:
        * Performs an authenticated GET to the GitHub API: GET https://api.{_OAUTH_DOMAIN}/user/emails
        * Headers include Authorization: token <access_token> and a User-agent header.
    - Cookies:
        * Calls self.set_secure_cookie("user", <email>) to persist the chosen email in a secure cookie.
    - Redirect:
        * Calls self.redirect(next_) to instruct the client to navigate to the next page.
    - Uses application configuration:
        * Calls authenticate(self.application.options.auth, email) to determine whether an email is allowed.
    - Potential side-effecting exceptions from the HTTP client, JSON decoding, or authenticate are propagated to the caller and can result in non-2xx HTTP responses from the handler.

## Implementation notes and important edge-cases (behavioral details you must reproduce):
    - The method lowercases the stored email value (email['email'].lower()) but calls authenticate(...) with the original-case email string. This means the authorization check may be case-sensitive while the cookie value is always lowercased — preserve this order if reimplementing.
    - The code collects only emails where email['verified'] is truthy and authenticate(...) returns truthy; authenticate may return a boolean or a regex Match object — the implementation uses truthiness to decide.
    - When multiple allowed emails exist, the code uses emails.pop() (last element) to choose which email to store. This selects the last permitted email after the list comprehension.
    - next_ resolution:
        * The handler reads the request argument 'next' with a default of self.application.options.url_prefix or '/'.
        * If application.options.url_prefix is set and the provided next_ does not begin with '/', a leading '/' is prepended before redirecting.
    - Network/JSON/key errors are not caught in this method; they will propagate and should be considered by callers or by a higher-level error handler if you want graceful error pages.

## `flower.views.auth.GitLabLoginHandler` · *class*

## Summary:
Handles OAuth2 login flow for GitLab: exchanges authorization code for an access token, validates the authenticated GitLab user (email and optional group membership), sets a secure session cookie and redirects the user to the requested page.

## Description:
This Tornado request handler implements the parts of an OAuth2 login flow specific to GitLab. It should be mounted as a route in a Tornado application as the OAuth callback/entrypoint for GitLab authentication.

Typical usage:
- Add a route (e.g., /auth/gitlab) pointing to this handler in the Tornado app's URL spec.
- Configure settings['oauth'] with keys: 'key' (client_id), 'secret' (client_secret), and 'redirect_uri' (the OAuth redirect/callback URL).
- Ensure the application exposes an 'options' object with 'auth' (an auth backend/config) and 'url_prefix' (optional).
- Provide an authenticate(auth_backend, email) callable in scope (imported or attached to the app) that returns a truthy value if the email is allowed.

Responsibility boundary:
- This class coordinates the OAuth2 protocol steps (redirect to GitLab, exchange code for token), HTTP calls to the GitLab API to obtain user details and groups, and basic authorization checks (email authorization via authenticate and optional group membership). It does not implement token persistence or detailed session management beyond setting a secure cookie named 'user'. It relies on BaseHandler and Tornado's OAuth2Mixin for common web and OAuth primitives.

Known callers/factories:
- Tornado's routing will instantiate the handler for matching requests (no custom factory required). Typically configured in the application's URLSpec/router.

## State:
Class-level attributes
- _OAUTH_GITLAB_DOMAIN (str): Domain to contact for GitLab OAuth operations. Default: value of env FLOWER_GITLAB_OAUTH_DOMAIN or "gitlab.com".
- _OAUTH_AUTHORIZE_URL (str): "https://{_OAUTH_GITLAB_DOMAIN}/oauth/authorize", used by authorize_redirect (inherited).
- _OAUTH_ACCESS_TOKEN_URL (str): "https://{_OAUTH_GITLAB_DOMAIN}/oauth/token", used when exchanging code for token.
- _OAUTH_NO_CALLBACKS (bool): Tornado OAuth mixin flag (False here).

Handler state (instance-level, provided/required but not stored explicitly)
- self.settings['oauth'] (dict) - required keys:
    - 'key' (str): OAuth client_id (no default; must be present).
    - 'secret' (str): OAuth client_secret (no default; must be present).
    - 'redirect_uri' (str): OAuth redirect URI used in exchanges.
  Constraint: all three keys must be present and valid strings; otherwise OAuth will fail on HTTP calls.
- self.application.options.auth: an auth backend (opaque to this handler) passed to authenticate().
- self.application.options.url_prefix (optional str): used to normalize redirect path following login.
- Environment variables used:
    - FLOWER_GITLAB_OAUTH_DOMAIN (optional): hostname for GitLab; default "gitlab.com".
    - FLOWER_GITLAB_AUTH_ALLOWED_GROUPS (optional): comma-separated list of group full_paths; if set, group membership is required in addition to email auth.
    - FLOWER_GITLAB_MIN_ACCESS_LEVEL (optional): minimal access level (as string) used when listing groups; default '20'.

Class invariants:
- _OAUTH_AUTHORIZE_URL and _OAUTH_ACCESS_TOKEN_URL are consistent with _OAUTH_GITLAB_DOMAIN.
- Settings for OAuth ('key', 'secret', 'redirect_uri') must remain available during the handler's lifetime.

## Lifecycle:
Creation:
- Instantiate via Tornado URL routing. No explicit __init__ args required by this class (it inherits BaseHandler constructor).
- Before first request, ensure settings['oauth'] exists and contains client key/secret/redirect_uri.

Usage sequence (typical):
1. A client GETs the handler's URL.
2. get() runs:
   - If query parameter 'code' is absent: call authorize_redirect(...) to send the user to GitLab's authorize URL. This performs the initial OAuth redirect.
   - If 'code' is present: call get_authenticated_user(redirect_uri, code) to exchange the code for an access token, then call _on_auth(user) to validate and complete login.
3. get_authenticated_user:
   - Performs POST to the token endpoint (_OAUTH_ACCESS_TOKEN_URL) with client credentials and code, returns parsed JSON (a dict) on success.
4. _on_auth:
   - Validates presence of user dict and access_token.
   - Fetches current user details from the GitLab API (/api/v4/user).
   - Calls authenticate(self.application.options.auth, user_email) to check the email.
   - If FLOWER_GITLAB_AUTH_ALLOWED_GROUPS is set, fetches groups with min_access_level and checks for any matching group 'full_path'.
   - If checks pass, stores the user email via set_secure_cookie('user', email) and redirects to the 'next' param (normalized by url_prefix).
Destruction:
- No explicit cleanup required. No file handles or persistent network sessions are kept by this handler. Tornado manages handler lifecycle.

## Methods (public behavior):
- async get_authenticated_user(redirect_uri: str, code: str) -> dict
    - Inputs:
        - redirect_uri: redirect/callback URL used in the token exchange.
        - code: authorization code received from GitLab.
    - Behavior:
        - Constructs application/x-www-form-urlencoded body with redirect_uri, code, client_id, client_secret, grant_type.
        - Performs a POST to the token endpoint and expects JSON response.
        - If the HTTP response includes .error truthy, raises tornado.auth.AuthError including the response.
        - Returns Python dict parsed from the JSON response body (expected keys include 'access_token', optionally 'token_type', 'expires_in', etc.).
    - Edge cases:
        - Raises tornado.auth.AuthError if response.error is truthy.
        - If response body is not valid JSON, json.loads will raise JSONDecodeError which propagates.
    - Notes:
        - Relies on self.settings['oauth']['key'] and ['secret'].

- async get(self) -> None
    - Behavior:
        - Reads redirect_uri = self.settings['oauth']['redirect_uri'].
        - If query parameter 'code' exists: exchanges it for token via get_authenticated_user and calls _on_auth(user).
        - If no 'code': calls authorize_redirect(...) to send user to GitLab OAuth authorize page with scope ['read_api'] and response_type 'code'.
    - Edge cases:
        - If settings['oauth']['redirect_uri'] missing, subsequent token exchange will likely fail.

- async _on_auth(self, user: dict) -> None
    - Inputs:
        - user: dict returned by get_authenticated_user, must include 'access_token'.
    - Behavior:
        - If user is falsy (None/empty), raises tornado.web.HTTPError(500, 'OAuth authentication failed').
        - Uses access_token = user['access_token'].
        - Reads FLOWER_GITLAB_AUTH_ALLOWED_GROUPS env var and converts it into list of stripped group full_path strings (empty list if not set).
        - Fetches GitLab API /api/v4/user to obtain user details; if the fetch raises any exception, raises HTTPError(403, "GitLab auth failed: {e}").
        - Extracts 'email' from the parsed JSON user object and calls authenticate(self.application.options.auth, user_email).
        - If allowed_groups was set, fetches /api/v4/groups?min_access_level={min_access_level}, parses response JSON and keeps group['id'] for groups whose 'full_path' is in allowed_groups. matching_groups is list of ids.
        - If email not allowed OR (allowed_groups present and matching_groups is empty), raises HTTPError(403, 'Access denied. Please use another account or contact your admin.').
        - On success: calls set_secure_cookie('user', str(user_email)), resolves 'next' via query parameter (defaults to application.options.url_prefix or '/'), ensures it begins with '/', and redirects there.
    - Edge cases / error conditions:
        - Missing 'access_token' key in user dict will raise a KeyError; the handler does not explicitly catch this (will propagate). In practice get_authenticated_user should return the expected shape.
        - Network errors or non-2xx responses while contacting GitLab APIs are wrapped as HTTPError(403).
        - If parsing JSON fails, JSONDecodeError propagates (not explicitly handled).
    - Dependencies:
        - authenticate(auth_backend, email) callable must be accessible in the module scope (the code calls authenticate(...)). This handler assumes it returns a truthy value for allowed emails and falsy otherwise.

## Method Map:
graph LR
    A[get (entrypoint)] --> B{has 'code' arg?}
    B -- no --> C[authorize_redirect -> redirect to GitLab authorize URL]
    B -- yes --> D[get_authenticated_user]
    D --> E[_on_auth]
    E --> F[fetch /api/v4/user]
    E --> G[maybe fetch /api/v4/groups (if allowed_groups)]
    E --> H[set_secure_cookie('user')]
    E --> I[redirect(next)]

Note: get_authenticated_user performs an outbound POST to _OAUTH_ACCESS_TOKEN_URL; _on_auth performs outbound GETs to GitLab API endpoints.

## Raises:
Exceptions raised directly by methods and when they are raised:
- tornado.auth.AuthError
    - Trigger: get_authenticated_user finds response.error truthy after token exchange POST.
- tornado.web.HTTPError(500, 'OAuth authentication failed')
    - Trigger: _on_auth received a falsy/None user argument.
- tornado.web.HTTPError(403, 'GitLab auth failed: {e}')
    - Trigger: any exception occurred while fetching /api/v4/user (network error, HTTP non-2xx, etc.). The original exception is interpolated into the message.
- tornado.web.HTTPError(403, 'Access denied. Please use another account or contact your admin.')
    - Trigger: authorize/auth checks failed: either authenticate(...) returned falsy, or allowed_groups was set and none of the user's groups matched the allowed list.
- JSONDecodeError (from json.loads)
    - Trigger: response bodies are not valid JSON; not explicitly caught.
- KeyError
    - Trigger: expected keys in returned JSON are missing (e.g., 'access_token' or 'email'); these will raise KeyError and propagate.

## Example:
- Precondition: Tornado app configured with settings['oauth'] = {'key': 'CLIENT_ID', 'secret': 'CLIENT_SECRET', 'redirect_uri': 'https://my.app/auth/gitlab'} and a route mapping to GitLabLoginHandler.
- Browser access flow:
    1. User visits /auth/gitlab with optional ?next=/protected.
    2. Handler.get sees no 'code' param -> calls authorize_redirect(...). Browser is redirected to GitLab authorize endpoint.
    3. User authorizes at GitLab; GitLab redirects back to redirect_uri with ?code=AUTH_CODE.
    4. Handler.get receives 'code', calls get_authenticated_user(redirect_uri, code) -> receives token dict.
    5. Handler._on_auth(token_dict) fetches user info and groups, validates via authenticate(...); on success sets secure cookie and redirects to next.

Notes and implementation hints:
- get_auth_http_client(), authorize_redirect(), and set_secure_cookie() are provided by Tornado (OAuth2Mixin and BaseHandler). Ensure BaseHandler implements/forwards secure cookie and settings access as expected.
- authenticate(...) is expected to be an imported/global function that evaluates whether an email is allowed; if your copy of the repository does not provide it, import or implement it to return boolean given application.options.auth and an email string.
- Keep environment variables documented above in deployment configuration; set FLOWER_GITLAB_AUTH_ALLOWED_GROUPS only if group-based restriction is required. When set, ensure group paths use GitLab's 'full_path' values (e.g., "org/subgroup").

### `flower.views.auth.GitLabLoginHandler.get_authenticated_user` · *method*

## Summary:
Exchanges an OAuth2 authorization code for an access token by POSTing to GitLab's token endpoint and returns the parsed JSON token response; does not modify handler state.

## Description:
This asynchronous method performs the token-exchange step of the OAuth2 "authorization code" flow for GitLab:
- It URL-encodes the required form fields (redirect_uri, code, client_id, client_secret, grant_type) and performs an HTTP POST to the token endpoint (self._OAUTH_ACCESS_TOKEN_URL) using the handler's auth HTTP client.
- On a successful response it parses the response body as UTF-8 JSON and returns the resulting Python object (typically a dict containing access_token and related fields).
- If the HTTP response indicates an error (response.error is truthy), it raises tornado.auth.AuthError.

Known callers and lifecycle stage:
- Called by GitLabLoginHandler.get during the OAuth callback branch after the request query contains an authorization code. It is awaited during request handling to obtain token data before continuing authentication (_on_auth).
- Implemented as a separate method to isolate HTTP token-exchange details (network I/O, form encoding, error handling, JSON parsing) from higher-level control flow and post-auth processing.

## Args:
    redirect_uri (str): The redirect / callback URI originally used when initiating the OAuth flow. Must be a string.
    code (str): The authorization code received from GitLab. Must be a string (expected to be non-empty when used in the callback branch).

## Returns:
    dict | list | any: The result of json.loads(response.body.decode('utf-8')). In typical GitLab usage this is a dict containing token-related fields such as:
        - access_token (str)
        - token_type (str)
        - expires_in (int) (optional)
        - refresh_token (str) (optional)
        - scope (str) (optional)
    Edge-case return values:
        - If the token endpoint returns JSON that is not an object, the raw parsed JSON (e.g., list) is returned.
        - If response.body is empty or invalid JSON, json.loads will raise json.JSONDecodeError (see Raises).

## Raises:
    tornado.auth.AuthError:
        Condition: When response.error is truthy after the HTTP fetch to the token endpoint. The exception message includes the response object.
    json.JSONDecodeError:
        Condition: The HTTP response body is not valid UTF-8 JSON or cannot be parsed by json.loads.
    Any exception raised by the underlying HTTP client fetch:
        Condition: Network failures, timeouts, or the HTTP client's own exceptions raised when awaiting get_auth_http_client().fetch. These exceptions propagate from the call site.

## State Changes:
Attributes READ:
    - self.settings: Accesses self.settings['oauth']['key'] and self.settings['oauth']['secret'] to populate client_id and client_secret.
    - self._OAUTH_ACCESS_TOKEN_URL: Reads the token endpoint URL to which the POST is made.
    - self.get_auth_http_client(): Called to obtain an HTTP client used for the fetch; the method is invoked (read).
    - response.body: read for decoding and JSON parsing.

Attributes WRITTEN:
    - None. This method does not assign to any self.<attr> fields.

## Constraints:
Preconditions:
    - self.settings must be a mapping containing an 'oauth' dict with string keys 'key' and 'secret'. Accessing missing keys will raise KeyError.
    - redirect_uri and code must be provided as strings. The caller (e.g., GitLabLoginHandler.get) is expected to ensure code is present and non-empty for the callback path.
    - self.get_auth_http_client() must return an object with an awaitable fetch(method, headers, body, ...) method that yields a response with .body (bytes-like) and .error attributes.

Postconditions:
    - On successful completion, the method returns the decoded JSON response from the token endpoint (parsed into Python objects).
    - On error responses from the token endpoint (response.error truthy), a tornado.auth.AuthError is raised and no return value is produced.
    - No handler attributes are modified by this method.

## Side Effects:
    - Network I/O: performs an outbound HTTP POST to the token endpoint (self._OAUTH_ACCESS_TOKEN_URL).
    - May raise exceptions that propagate to the caller (error responses, network errors, or JSON parsing failures).
    - No direct I/O to disk or mutation of external objects is performed by this method itself.

### `flower.views.auth.GitLabLoginHandler.get` · *method*

## Summary:
Handles the HTTP GET step of the GitLab OAuth2 login flow: if an authorization code is present, exchanges it for an access token and continues authentication; otherwise initiates OAuth authorization by redirecting the client to GitLab's authorization endpoint.

## Description:
This method is invoked by the Tornado request dispatcher when an HTTP GET request reaches the route handled by GitLabLoginHandler. It implements the branching logic for two stages of the OAuth dance:
- Initiation stage: when no (non-empty) 'code' query parameter is present, it redirects the client to GitLab's authorization URL to request consent/authorization.
- Callback stage: when a (non-empty) 'code' query parameter is present, it exchanges the code for an access token (via get_authenticated_user) and then completes authentication by delegating to _on_auth.

Known callers and lifecycle context:
- Called automatically by Tornado as the GET handler for the configured route for GitLab OAuth login. This is an entry point in the request lifecycle (request handling stage).
- get_authenticated_user and _on_auth are called by this method as part of the token exchange and post-auth processing.

Why this logic is its own method:
- This method orchestrates two distinct control flows (initiate authorization vs. handle callback). Keeping that orchestration separate keeps token-exchange and post-auth logic (get_authenticated_user and _on_auth) focused on their responsibilities (HTTP token exchange and user/session handling respectively), and simplifies testing of the control flow.

## Args:
This is an instance method and takes only self. It reads request query arguments via Tornado's RequestHandler.get_argument; no explicit parameters are passed.

## Returns:
None. The method's observable effects are performed through HTTP responses (redirects) and calls to helper methods; it does not return a Python value.

## Raises:
- tornado.auth.AuthError
    - Condition: If get_authenticated_user raises tornado.auth.AuthError during the token exchange (see get_authenticated_user implementation which raises AuthError when the token endpoint response indicates an error). This exception will propagate unless handled upstream.
- tornado.web.HTTPError
    - Condition: If _on_auth raises tornado.web.HTTPError (for example when user data are invalid or authorization is denied). _on_auth can raise HTTPError for authentication failures; those errors propagate here.
- Other exceptions from underlying I/O
    - Condition: Network or I/O errors raised by get_authenticated_user or underlying HTTP client calls may propagate (e.g., connection errors). These are not explicitly raised in this method but can bubble up.

Note: get_argument is used with a default in the initial check to avoid raising MissingArgumentError. The second call to get_argument('code') (without a default) is safe because it is only reached when the initial truthy check passed.

## State Changes:
Attributes READ:
- self.settings (reads self.settings['oauth']['redirect_uri'] and self.settings['oauth']['key'])
- self.get_argument (reads request query string 'code')
- self.get_authenticated_user (invoked; performs I/O and returns token data)
- self._on_auth (invoked; performs post-auth processing)
- self.authorize_redirect (invoked when initiating authorization)

Attributes WRITTEN:
- This method does not directly assign to self.<attr> fields.
- Indirect writes / mutations caused by called methods:
    - _on_auth may set secure cookies and call redirect (see _on_auth implementation).
    - get_authenticated_user performs HTTP requests but does not mutate handler attributes.

## Constraints:
Preconditions:
- self.settings must be a mapping containing an 'oauth' sub-mapping with at least:
    - 'redirect_uri' (string): the callback URI used for the OAuth flow.
    - 'key' (string): the OAuth client_id used to initiate authorization.
  If these keys are missing, KeyError will be raised when accessing self.settings['oauth'][...].
- The HTTP request object must be a valid Tornado request with accessible query arguments.
- If the handler is in the callback branch, the 'code' argument must be present in the query string and be truthy (non-empty). The initial check uses if self.get_argument('code', False): so an empty string is treated like no code (initiation flow).

Postconditions:
- If the 'code' parameter is absent or empty: the method invokes authorize_redirect and the HTTP response will instruct the client to go to the GitLab authorization endpoint (the request handling finishes with a redirect).
- If the 'code' parameter is present (truthy): the method calls get_authenticated_user and then _on_auth. After _on_auth returns (or raises), control returns to Tornado's request handling. Typical successful completion results in further side effects performed by _on_auth (e.g., setting cookies and redirecting to the next page).

## Side Effects:
- Initiates outbound HTTP I/O when exchanging the authorization code for an access token via get_authenticated_user (network call to GitLab token endpoint).
- If in initiation branch, issues a redirect response to GitLab's authorization endpoint via authorize_redirect (causes the client browser to navigate away).
- If in callback branch, delegates to _on_auth which:
    - performs additional HTTP requests to GitLab (user info, groups),
    - may set secure cookies (self.set_secure_cookie),
    - and performs a redirect to the application next URL (self.redirect).
- May propagate exceptions from downstream I/O or validation which will result in error responses if unhandled.

## Edge cases and notes:
- An empty 'code' query parameter (code="") is treated as absent and will trigger the initiation redirect instead of the token-exchange path.
- The second call to get_argument('code') in the callback branch is safe because it is only executed when the initial truthy check passes.
- This method does not itself validate scopes, allowed emails, or groups — those checks are done in _on_auth.

### `flower.views.auth.GitLabLoginHandler._on_auth` · *method*

## Summary:
Performs post-OAuth GitLab authorization: validates the OAuth response, verifies the user's email and (optionally) group membership against configured allowlists, sets a secure 'user' cookie, and redirects the client to the next URL on success.

## Description:
This asynchronous helper finalizes authentication after the OAuth access token has been obtained. Typical callers and call-site:
- Called by GitLabLoginHandler.get() immediately after get_authenticated_user(...) returns the OAuth token payload. This occurs during the OAuth callback handling stage of the login flow (when the handler receives a 'code' request parameter).
- It exists as a separate method to isolate the post-token authorization logic (HTTP API calls to GitLab, allowlist checking, cookie setting, redirect) from the OAuth token-exchange logic. This separation improves readability, testability, and reusability (e.g., different entry points could reuse this post-auth validation).

Lifecycle stage:
- Invocation happens during the request handling lifecycle after successful OAuth token exchange and before the final redirect back to the application UI.

Why separate:
- The method encapsulates multiple responsibilities (GitLab API calls, environment-driven configuration, authorization policy checks, and side-effecting response modifications). Extracting it keeps get() focused on orchestrating OAuth flow and lets this method concentrate on authorization and session creation.

## Args:
    user (dict): The parsed OAuth response from GitLab (returned by get_authenticated_user).
        - Required keys: 'access_token' (str). If user is falsy, the method immediately raises HTTPError(500).
        - Expected type: mapping-like (dict). Passing None or a falsy value triggers an HTTPError(500).

## Returns:
    None
    - On success the method performs response side effects (sets a secure cookie and issues an HTTP redirect) and does not return a meaningful value to the caller.
    - On failure it raises exceptions (see Raises).

## Raises:
    tornado.web.HTTPError(500)
        - Condition: the `user` argument is falsy (None, empty, etc.). Raised with message 'OAuth authentication failed'.

    tornado.web.HTTPError(403)
        - Condition A: The initial GitLab user-profile API request (GET /api/v4/user) raised an exception (network error, timeout, HTTP error from the underlying client, etc.). The caught exception `e` is interpolated into the message 'GitLab auth failed: {e}'.
        - Condition B: Authorization policy denied access because either:
            * the user's email did not pass the configured authenticate(...) check, or
            * FLOWER_GITLAB_AUTH_ALLOWED_GROUPS is configured and no groups returned from GitLab matched the configured allowed groups.
          In both cases the method raises HTTPError(403) with message 'Access denied. Please use another account or contact your admin.'.

    Exceptions propagated (not caught by this method)
        - JSONDecodeError (from json.loads) if GitLab returns non-JSON responses where JSON is expected.
        - KeyError when accessing expected JSON keys (e.g., missing 'email' or missing keys inside group objects).
        - Any exception thrown by get_auth_http_client().fetch for the second groups API call (these are not wrapped here and will propagate as-is).
        - Any other runtime exceptions arising while decoding or processing responses.

## State Changes:
Attributes READ:
    - self._OAUTH_GITLAB_DOMAIN (class attribute): used to build GitLab API URLs.
    - self.application.options.auth: passed to authenticate(...) to validate email.
    - self.application.options.url_prefix: used to normalize the 'next' redirect path.
    - Environment variables: FLOWER_GITLAB_AUTH_ALLOWED_GROUPS and FLOWER_GITLAB_MIN_ACCESS_LEVEL (read via os.environ).

Attributes WRITTEN:
    - None of the handler's Python attributes are modified by this method itself.

External / handler-side state mutated (observable effects):
    - Sets a secure cookie named 'user' via self.set_secure_cookie('user', str(user_email)).
    - Issues an HTTP redirect via self.redirect(next_), which finalizes the response for the client.

## Constraints:
Preconditions (what must be true before calling):
    - self must be a GitLabLoginHandler instance (inherits Tornado RequestHandler) with:
        * a working get_auth_http_client() method that returns an async-capable HTTP client exposing fetch(...)
        * working set_secure_cookie, get_argument and redirect methods provided by Tornado's RequestHandler
        * self.application.options and self.application.options.auth present (used for authenticate)
    - `user` must be a mapping-like object containing the 'access_token' key holding a valid GitLab OAuth token (string).
    - Network connectivity to the configured GitLab domain must be available for API calls to succeed.
    - If FLOWER_GITLAB_AUTH_ALLOWED_GROUPS is set, it must contain comma-separated group full paths (full_path values as returned by the GitLab groups API).

Postconditions (guarantees after successful call):
    - If the method returns normally (does not raise), the user's email has been validated against the configured policies, a secure cookie 'user' is set to the user's email (stringified), and the response has been redirected to the normalized 'next' URL (so no further body should be written by the caller).
    - If authorization fails, an appropriate tornado.web.HTTPError is raised and no cookie or redirect is performed by this method.

## Behavior details and edge cases:
    - Allowed-groups handling:
        * Reads FLOWER_GITLAB_AUTH_ALLOWED_GROUPS from environment; when empty or missing it is treated as no group-based restriction.
        * When set, the variable is split on commas and whitespace trimmed; only non-empty entries are kept.
        * If allowed groups are set, the method further calls the GitLab groups endpoint with a min_access_level parameter (defaulting to environment FLOWER_GITLAB_MIN_ACCESS_LEVEL or '20') and considers a group matching if its group['full_path'] is one of the configured allowed values. If none match, access is denied.

    - Email validation:
        * The user's email is read from the JSON response to GET /api/v4/user under the 'email' key. Missing or differently-structured responses will lead to KeyError or JSON errors.
        * Email authorization is delegated to authenticate(self.application.options.auth, user_email). The method accepts whatever truthy/falsy result that function returns (note: authenticate can return a re.Match object which is truthy; callers should be aware).

    - Redirect 'next' normalization:
        * The handler reads the 'next' query argument defaulting to self.application.options.url_prefix or '/'.
        * If a url_prefix is configured and the next path does not start with '/', a leading '/' is inserted to create a valid path under the prefix.

## Side Effects:
    - Network I/O: makes HTTP GET requests to GitLab:
        * GET https://{_OAUTH_GITLAB_DOMAIN}/api/v4/user (to retrieve the authenticated user's profile/email)
        * Optionally GET https://{_OAUTH_GITLAB_DOMAIN}/api/v4/groups?min_access_level={min_access_level} (when group allowlist is configured)
      Both requests include Authorization: Bearer <access_token> and a User-agent header.
    - Sets a secure cookie ('user') in the HTTP response.
    - Issues an HTTP redirect (modifies response status and Location header).
    - Reads runtime configuration from environment variables and from self.application.options; no persistent storage is modified.

## Implementation notes (for reimplementation):
    - Ensure to validate `user` is truthy before accessing 'access_token'.
    - Use a robust async HTTP client with proper exception types for network errors; catch the first user-profile fetch errors and map them to HTTP 403 with a clear message, but allow other exceptions (such as group-fetch errors or JSON decode errors) to propagate or be handled intentionally.
    - Normalize the 'next' argument relative to options.url_prefix to avoid open-redirect vulnerabilities (current logic only ensures a leading slash when a prefix exists; consider additional validation if reimplementing).
    - Be explicit about encoding/decoding the response body to UTF-8 before json.loads.

## `flower.views.auth.OktaLoginHandler` · *class*

## Summary:
Represents an OAuth2 login handler that implements Okta-specific endpoints for authorizing users, exchanging authorization codes for access tokens, retrieving user info, and establishing a secure "user" cookie for authenticated sessions.

## Description:
This Tornado request handler is intended to be mounted as an HTTP GET endpoint (typically the OAuth callback and initial authorization trigger) to support Okta-based OAuth2 sign-in for the Flower web UI. Common usage patterns:
- Add a route mapping (e.g., "/auth/okta") to this handler in the Tornado/web.Application routes.
- Configure application settings['oauth'] with keys: "key" (client_id), "secret" (client_secret), and "redirect_uri".
- Set the environment variable FLOWER_OAUTH2_OKTA_BASE_URL to your Okta org's base URL (for example: https://dev-123456.okta.com/oauth2/default).

This class is a distinct abstraction because it encapsulates the Okta-specific endpoints and the OAuth2 exchange logic while delegating lower-level HTTP client handling and cookie management to the BaseHandler / Tornado RequestHandler infrastructure. It enforces the responsibility boundary of:
- initiating the authorization redirect,
- verifying state tokens,
- exchanging authorization codes for tokens,
- fetching user info,
- translating the Okta user response into a local authenticated session (secure cookie "user").

Known dependencies:
- BaseHandler (superclass) — must provide Tornado RequestHandler-like methods and ideally a get_auth_http_client() method returning an async HTTP client.
- authenticate function (views.auth.authenticate) — used to validate an email against the configured auth pattern(s).
- Tornado's OAuth2Mixin (mixed in) providing authorize_redirect and other helper behavior.

## State:
Class attributes / properties:
- _OAUTH_NO_CALLBACKS (bool) = False
  - Indicates OAuth mixin uses callbacks; left as defined by class.
- _OAUTH_SETTINGS_KEY (str) = "oauth"
  - Settings key inside self.settings where oauth config is read from.

Dynamic properties (read-only):
- base_url -> str | None
  - Value read from environment variable FLOWER_OAUTH2_OKTA_BASE_URL.
  - Valid when non-empty string; None or empty means URLs derived from it will be invalid.
- _OAUTH_AUTHORIZE_URL -> str
  - Computed as "{base_url}/v1/authorize". Assumes base_url is non-None.
- _OAUTH_ACCESS_TOKEN_URL -> str
  - Computed as "{base_url}/v1/token".
- _OAUTH_USER_INFO_URL -> str
  - Computed as "{base_url}/v1/userinfo".

In-handler runtime state (via cookies/settings/application):
- settings: mapping-like (inherited). Expected to contain settings['oauth'] with:
    - "key" (str): OAuth client_id. Required.
    - "secret" (str): OAuth client_secret. Required.
    - "redirect_uri" (str): redirect URI registered with Okta. Required.
- Secure cookie "oauth_state" (str): randomly-generated UUID stored when initiating auth; must match the returned "state" query parameter on callback.
- Secure cookie "user" (str): email string stored on successful authentication.
- application.options.url_prefix (str | None): optional prefix used when computing redirect target "next".

Class invariants (assumptions that should hold during normal operation):
- self.settings[self._OAUTH_SETTINGS_KEY] exists and contains "key", "secret", and "redirect_uri".
- base_url is set (non-None) to form valid Okta endpoints.
- If "oauth_state" cookie is set, a subsequent callback must supply matching state or authentication fails.

## Lifecycle:
Creation:
- Instantiated by Tornado web.Application request handling when a matching route receives a GET request.
- No explicit __init__ parameters are required by this class; it uses the standard RequestHandler initialization.

Usage / method sequence (typical):
1. User visits the handler's route (GET).
2. Handler.get() runs:
   - If no "code" query parameter is present:
     - Generates a state UUID, stores it in secure cookie "oauth_state".
     - Calls authorize_redirect(...) to send the user to the Okta authorize URL with client_id, scope, response_type=code, redirect_uri, and state.
   - If "code" query parameter is present (callback from Okta):
     - Retrieves secure cookie "oauth_state" and compares to the "state" query parameter.
     - If mismatch: raises tornado.auth.AuthError.
     - Calls get_access_token(redirect_uri, code) to exchange the code for an access token response.
     - Calls _on_auth(access_token_response) to fetch user info and finalize login.
3. _on_auth(access_token_response):
   - Validates the token response exists and contains access_token; raises HTTPError 500 if missing.
   - Uses get_auth_http_client().fetch to call userinfo endpoint with Bearer token.
   - Parses JSON body for "email" and "email_verified".
   - Calls authenticate(self.application.options.auth, email) to perform configured email validation.
   - On success: sets secure cookie "user" to email, clears "oauth_state", computes next redirect target, and calls self.redirect(next_).
   - On failure: raises HTTPError 403 with an "Access denied" message.

Destruction / cleanup:
- No explicit destructor. The handler relies on Tornado's request lifecycle.
- It clears the "oauth_state" cookie after successful authentication; no other cleanup responsibilities.

Sequence constraints / ordering:
- authorize_redirect must be called before the Okta response callback occurs.
- The state cookie must be set before redirect and checked on callback; mismatch leads to AuthError.
- get_access_token requires redirect_uri and authorization code as inputs; called only after code is present.

## Method Map:
flowchart LR
    G[GET request -> OktaLoginHandler.get()] --> |no code| A[generate state UUID]
    A --> B[set_secure_cookie('oauth_state', state)]
    B --> C[authorize_redirect(...) -> redirect to Okta authorize endpoint]
    G --> |with code| D[verify state cookie equals returned state]
    D --> |mismatch| E[raise tornado.auth.AuthError (state tokens do not match)]
    D --> |match| F[get_access_token(redirect_uri, code)]
    F --> H[_on_auth(access_token_response)]
    H --> I[fetch userinfo with Bearer token]
    I --> J[parse JSON -> email, email_verified]
    J --> K[authenticate(application.options.auth, email)]
    K --> |not verified| L[raise HTTPError 403 access denied]
    K --> |verified| M[set_secure_cookie('user', email); clear_cookie('oauth_state'); redirect(next_)]

## Method-level behavior (implementation notes and edge cases):
- get(self):
    - Reads redirect_uri from self.settings['oauth']['redirect_uri'].
    - Branches on presence of query parameter "code" (uses self.get_argument('code', False) to detect).
    - When initiating authorize redirect:
        - Generates state via uuid.uuid4() and stores via set_secure_cookie("oauth_state", state).
        - Calls authorize_redirect with:
            - redirect_uri
            - client_id from settings['oauth']['key']
            - scope ['openid email']
            - response_type 'code'
            - extra_params {'state': state}
    - When handling callback:
        - Retrieves expected_state: (self.get_secure_cookie('oauth_state') or b'').decode('utf-8')
          - Note: missing cookie yields b'' decoding to ''.
        - Retrieves returned_state: self.get_argument('state')
        - If returned_state is None or doesn't match expected_state: raises tornado.auth.AuthError.
        - Calls get_access_token and then _on_auth.
    - Exceptions that can surface here:
        - tornado.auth.AuthError when state mismatch.
        - KeyError if settings or oauth keys are missing.
        - Any exceptions raised by get_access_token or _on_auth (HTTPError, network errors).

- get_access_token(self, redirect_uri, code) -> dict-like JSON:
    - URL-encodes a body containing redirect_uri, code, client_id, client_secret, grant_type=authorization_code.
    - Performs an async POST against _OAUTH_ACCESS_TOKEN_URL using self.get_auth_http_client().fetch(...).
      - Expected response.body contains JSON with keys including 'access_token'.
    - If response.error is truthy, raises tornado.auth.AuthError with the response included in message.
    - Returns parsed JSON as a Python dict (json.loads(response.body.decode('utf-8'))).
    - Edge cases:
      - If get_auth_http_client() is not implemented or returns an incompatible client, an AttributeError or other error will be raised.
      - If response.body is not valid JSON, json.loads will raise ValueError.
      - If settings lack 'key' or 'secret', KeyError will be raised when building the request body.

- _on_auth(self, access_token_response):
    - If access_token_response falsy -> raises tornado.web.HTTPError(500, 'OAuth authentication failed').
    - Expects access_token_response['access_token'] to exist; missing key will raise KeyError (unhandled) or downstream errors.
    - Fetches userinfo with Authorization: Bearer <access_token>.
    - Parses response body JSON and extracts email and email_verified flag.
    - Calls authenticate(self.application.options.auth, email) to decide whether the email is allowed.
      - The authenticate function is responsible for matching configured patterns and may return truthy/falsy values (see its documentation for return semantics).
    - If email is not verified (either missing email_verified or authenticate returns falsy), raises tornado.web.HTTPError(403, message).
    - On success, sets secure cookie 'user' to the stringified email and clears 'oauth_state'.
    - Computes the redirect target 'next':
      - Uses self.get_argument('next', self.application.options.url_prefix or '/').
      - If application.options.url_prefix is set and next_ does not begin with '/', prefix a '/'.
    - Calls self.redirect(next_).
    - Edge cases:
      - If response from userinfo endpoint is not 200 or lacks expected keys, json decoding or key lookup will raise exceptions.
      - authenticate may return a re.Match (truthy) or True; callers should treat returned value in boolean context as this code does.

## Raises:
Explicit exceptions raised by this handler's methods:
- tornado.auth.AuthError:
    - In get(): if state tokens do not match.
    - In get_access_token(): if the token endpoint response indicates error (response.error truthy).
- tornado.web.HTTPError(500): in _on_auth() when access_token_response is falsy.
- tornado.web.HTTPError(403): in _on_auth() when email not verified or not permitted by authenticate.
- KeyError / ValueError / TypeError:
    - Missing settings['oauth'] keys, invalid JSON responses, or unexpected response structures can raise standard Python exceptions (not explicitly caught).
- Network and HTTP client exceptions:
    - get_auth_http_client().fetch may raise connection-related exceptions (propagated).

## Example:
Assume a Tornado web.Application and environment configured:

    # Environment
    FLOWER_OAUTH2_OKTA_BASE_URL=https://dev-123456.okta.com/oauth2/default

    # Application settings (simplified)
    settings = {
        'oauth': {
            'key': 'OKTA_CLIENT_ID',
            'secret': 'OKTA_CLIENT_SECRET',
            'redirect_uri': 'https://myflower.example.com/auth/okta'
        }
    }
    # Routes
    application = tornado.web.Application([
        (r"/auth/okta", OktaLoginHandler),
        ...
    ], **settings)

Typical flow:
1. Unauthenticated user requests /auth/okta.
2. Handler.get() sees no 'code' query arg, generates a state UUID, stores it in secure cookie 'oauth_state', and redirects the user to Okta authorize URL.
3. User authenticates at Okta and Okta redirects back to the configured redirect_uri with query params ?code=...&state=...
4. Handler.get() runs again, this time with 'code':
   - Reads and verifies state cookie equals returned state (else raises AuthError).
   - Calls get_access_token(...) to exchange code for an access_token.
   - Calls _on_auth(access_token_response) to fetch userinfo, validate email via authenticate(...), set secure cookie 'user', and redirect to the configured "next" URL.

Notes:
- Ensure the OAuth client registration at Okta includes the redirect_uri used and that the base URL environment variable FLOWER_OAUTH2_OKTA_BASE_URL is set.
- The handler trusts the authenticate(...) function to enforce configured allowlists and patterns; it treats authenticate(...) result in boolean context.
- This handler performs no explicit logging; exceptions will propagate to Tornado's error handling.

### `flower.views.auth.OktaLoginHandler.base_url` · *method*

## Summary:
Return the configured Okta OAuth2 base URL from the environment (or None when unset), exposed as a read-only property so other OAuth URL properties can derive their endpoints.

## Description:
Known callers and call sites:
- _OAUTH_AUTHORIZE_URL (property): builds the authorization endpoint by appending /v1/authorize to this base URL; used when redirecting the user to Okta to start the OAuth flow.
- _OAUTH_ACCESS_TOKEN_URL (property): builds the token endpoint by appending /v1/token; used by get_access_token() to exchange an authorization code for tokens.
- _OAUTH_USER_INFO_URL (property): builds the userinfo endpoint by appending /v1/userinfo; used by _on_auth() to fetch user profile/email data.
- Tornado's OAuth2 flow in OktaLoginHandler.get() and OktaLoginHandler._on_auth(): these lifecycle steps read the derived _OAUTH_* URLs during request handling (authorization redirect, token exchange, userinfo fetch).

Lifecycle stage:
- Invoked during request handling when constructing the OAuth endpoints for initiating the authorization redirect and for subsequent token/userinfo HTTP requests (i.e., at runtime when a user triggers the OAuth login flow or callback).

Why this is a separate property:
- Centralizes retrieval of the Okta base URL (single source of truth).
- Enables easy overriding in tests or subclasses.
- Keeps environment access in one place rather than duplicating os.environ lookups across multiple properties.

## Args:
None (property with no parameters).

## Returns:
str | None
- If the environment variable FLOWER_OAUTH2_OKTA_BASE_URL is set, returns its value (the base URL string as stored in the environment).
- If the environment variable is not set, returns None.
- If the environment variable is set to an empty string, returns the empty string.

Typical expected format:
- An absolute URL including scheme and host (for example: "https://dev-12345.okta.com").
- The method does not modify or normalize the string; callers append path segments like "/v1/token".

## Raises:
None raised directly by this property. (Note: downstream callers that build URLs using the return value may fail or produce invalid URLs if this returns None or an improperly formatted value.)

## State Changes:
Attributes READ:
- None on self (does not access or read any self.<attr> fields)

Attributes WRITTEN:
- None (does not modify self)

## Constraints:
Preconditions:
- None enforced by the method itself. For correct operation of the OAuth handlers, the environment variable FLOWER_OAUTH2_OKTA_BASE_URL should be set to a valid, absolute Okta base URL before invoking OAuth-related request handling.

Postconditions:
- The method returns the raw environment value (string or None) and leaves the handler instance unchanged.

Recommendations to callers/implementers:
- Ensure FLOWER_OAUTH2_OKTA_BASE_URL is set to a scheme + host (no trailing path required).
- Prefer omitting a trailing slash to avoid double slashes when callers append "/v1/..." (the implementation does not strip or add slashes).
- In tests or deployments, override this property or set the environment variable to a testable URL.

## Side Effects:
- None. This property reads from process environment but performs no I/O, network calls, or mutations of external state.

### `flower.views.auth.OktaLoginHandler._OAUTH_AUTHORIZE_URL` · *method*

## Summary:
Returns the Okta OAuth2 authorization endpoint URL by concatenating the handler's base_url with the fixed path "/v1/authorize". This property does not mutate the object's state.

## Description:
- Known callers and context:
  - Called indirectly when initiating the OAuth2 authorization redirect in OktaLoginHandler.get(). The get() method calls self.authorize_redirect(...) (provided by tornado.auth.OAuth2Mixin), which uses provider-specific endpoint information — this property supplies the authorization endpoint for Okta.
  - No other methods in OktaLoginHandler reference this property directly in the class definition.
- Lifecycle stage:
  - Invoked during the "start" of the OAuth2 authorization flow, i.e., when the handler needs to redirect the user's browser to the identity provider to obtain an authorization code.
- Why this logic is its own method:
  - The tornado.auth.OAuth2Mixin expects provider-specific endpoints to be supplied as properties named _OAUTH_AUTHORIZE_URL, _OAUTH_ACCESS_TOKEN_URL, etc. Encapsulating the Okta authorization endpoint as a property makes the value easily overridable and keeps provider configuration centralized and consistent with the mixin's contract.

## Args:
- None.

## Returns:
- str: A URL string produced by concatenating self.base_url and the literal suffix "/v1/authorize".
  - Typical value example: if FLOWER_OAUTH2_OKTA_BASE_URL is "https://dev-12345.okta.com", the property returns "https://dev-12345.okta.com/v1/authorize".
  - Edge cases:
    - If the environment variable backing self.base_url is not set (self.base_url is None), the returned value will be the string "None/v1/authorize" (no explicit validation is performed).
    - If base_url ends with a trailing slash (e.g., "https://.../"), the result will contain a double slash before "v1" (e.g., "https://...//v1/authorize"); the property does not normalize or strip trailing slashes.

## Raises:
- None. The property does not raise exceptions itself.

## State Changes:
- Attributes READ:
  - self.base_url (property that reads os.environ.get('FLOWER_OAUTH2_OKTA_BASE_URL')).
- Attributes WRITTEN:
  - None. This property does not modify any attributes or persistent state.

## Constraints:
- Preconditions:
  - The environment variable FLOWER_OAUTH2_OKTA_BASE_URL should be set to a valid Okta base URL string for the returned URL to be correct and usable.
  - Caller code (typically OAuth2MixIn.authorize_redirect) should expect a simple string endpoint and be responsible for building query parameters.
- Postconditions:
  - After calling this property, the caller is guaranteed a str return value representing base_url + "/v1/authorize" (subject to the caveats about None or trailing slashes noted above). No object attributes are modified.

## Side Effects:
- Reads global process environment via self.base_url (which calls os.environ.get). There are no network I/O operations, no file I/O, and no mutations of objects or external state performed by this property.

### `flower.views.auth.OktaLoginHandler._OAUTH_ACCESS_TOKEN_URL` · *method*

## Summary:
Return the Okta token endpoint URL used to exchange an authorization code for an access token. Does not modify object state; computes the URL from the handler's configured base URL.

## Description:
This read-only property builds and returns the full token endpoint for the Okta OAuth2 provider by combining the handler's base_url with the fixed path "/v1/token". Known callers and contexts:
- OktaLoginHandler.get_access_token: called during the OAuth callback flow to POST an authorization-code grant and obtain an access token.
- The property also satisfies the expectation of tornado.auth.OAuth2Mixin-derived flows that the handler expose provider-specific endpoint properties.

This logic is implemented as its own property to:
- Centralize the provider-specific token endpoint in a single place (easy to test and override).
- Keep endpoint construction separate from network/IO logic (get_access_token) so the URL-forming rule can be inspected or overridden without modifying request behavior.

## Args:
None (accessed as a property on self).

## Returns:
str: The token endpoint URL formed as "<base_url>/v1/token".
- Normal case: if self.base_url is a valid base URL string (for example "https://example.okta.com"), returns "https://example.okta.com/v1/token".
- Edge cases:
  - If self.base_url is None, the returned value will be the string "None/v1/token" (indicating a misconfiguration).
  - If self.base_url is an empty string, the returned value will be "/v1/token".
  - If self.base_url contains a trailing slash, the result may contain a double slash (e.g., "https://x.okta.com//v1/token"); this method does not normalize trailing slashes.

## Raises:
None. This property performs no validation and does not raise exceptions by itself.

## State Changes:
Attributes READ:
- self.base_url

Attributes WRITTEN:
- None (the property is read-only and does not modify self).

## Constraints:
Preconditions:
- For a correct, usable URL, self.base_url must be set to a non-empty string representing the Okta base URL (typically provided via the FLOWER_OAUTH2_OKTA_BASE_URL environment variable accessed by the base_url property).

Postconditions:
- Returns a string concatenating the current value of self.base_url and "/v1/token".
- Does not alter any attributes on the handler.

## Side Effects:
- None. This property does not perform I/O, network calls, cookie/session changes, or mutations of objects outside self.

### `flower.views.auth.OktaLoginHandler._OAUTH_USER_INFO_URL` · *method*

## Summary:
Returns the full Okta userinfo endpoint URL by concatenating the handler's configured base URL with the static path /v1/userinfo.

## Description:
Known callers and context:
- Called by OktaLoginHandler._on_auth when fetching user profile information after exchanging an authorization code for an access token. It's invoked during the OAuth callback handling stage (i.e., post-token exchange) of the login lifecycle.
- Indirectly required by tornado.auth.OAuth2Mixin semantics: OAuth-related URL properties are provided on the handler for use when performing OAuth flows.

Why this is a separate method/property:
- The method centralizes construction of the provider-specific userinfo endpoint so all code uses a single, consistent value.
- Exposing it as a property aligns with tornado.auth.OAuth2Mixin conventions, which expect handler attributes/properties named _OAUTH_AUTHORIZE_URL, _OAUTH_ACCESS_TOKEN_URL, and _OAUTH_USER_INFO_URL to exist.
- Separating URL construction avoids duplicating base URL handling and makes it easier to adapt to different Okta base URLs obtained from configuration (environment variable).

## Args:
This is a zero-argument instance property accessor; no arguments are accepted.

## Returns:
str: The fully-qualified userinfo endpoint URL computed as "<base_url>/v1/userinfo", where base_url is the value returned by self.base_url (see below).
- Typical valid return: "https://example-okta-domain.com/v1/userinfo"
- Edge cases:
  - If self.base_url is None (e.g., FLOWER_OAUTH2_OKTA_BASE_URL not set), the method returns the string "None/v1/userinfo".
  - If self.base_url contains a trailing slash (e.g., "https://host/"), the result will contain a doubled slash before v1 (e.g., "https://host//v1/userinfo"); the method performs no normalization to remove duplicate slashes.

## Raises:
This accessor does not raise exceptions itself. Any errors arising from using the returned value (for example, HTTP client failures when fetching the URL) occur in the caller.

## State Changes:
Attributes READ:
- self.base_url

Attributes WRITTEN:
- None. This accessor does not modify any self attributes or external state.

## Constraints:
Preconditions:
- The handler instance must be initialized; self.base_url must be accessible (the property exists on the class).
- For a valid userinfo endpoint, the environment variable FLOWER_OAUTH2_OKTA_BASE_URL should be set to a valid base URL (including scheme and host). The method does not validate URL format.

Postconditions:
- After calling this accessor, the caller receives a string computed from the current value of self.base_url and the literal path "/v1/userinfo".
- No state in the handler is mutated.

## Side Effects:
- None. The method performs no I/O, does not access the network, and does not change external state. Any network I/O happens when callers (e.g., _on_auth) use the returned URL to fetch user info.

### `flower.views.auth.OktaLoginHandler.get_access_token` · *method*

## Summary:
Exchange an OAuth2 authorization code for an access token by POSTing a form-encoded request to the configured Okta token endpoint and return the parsed JSON token response. This method performs network I/O but does not modify the handler's attributes.

## Description:
This async method performs the OAuth2 "authorization code" grant exchange. It is called during the OAuth callback flow (see OktaLoginHandler.get) when the application receives a 'code' query parameter after the user authorizes the application. The get() method of the same handler invokes this method to retrieve the access token response, then continues authentication handling.

This logic is separated into its own method to isolate the token-exchange step (network I/O and request/response handling), making the flow clearer and allowing easy overriding or testing of the token exchange independently of request routing and user/session handling.

## Args:
    redirect_uri (str): The redirect URI originally supplied when initiating authorization. Must match the redirect_uri configured in the OAuth client settings.
    code (str): The authorization code received from the OAuth provider (Okta) via the redirect callback. Must be a non-empty string.

## Returns:
    dict: The JSON-decoded token response from the token endpoint. Typical contents (provider-dependent) include keys such as "access_token", "token_type", "expires_in", and possibly "refresh_token" and "id_token". In error-free execution this is the dict returned by json.loads(response.body.decode('utf-8')).

    Edge cases:
    - If the response body is not valid UTF-8 or not valid JSON, json.loads or .decode will raise the underlying exception (e.g., UnicodeDecodeError or json.JSONDecodeError), which will propagate to the caller.

## Raises:
    tornado.auth.AuthError:
        - Raised when the fetched HTTP response has a truthy response.error attribute. The exception message contains the full response representation as formatted in the code.

    Any exception raised by the underlying HTTP client:
        - If self.get_auth_http_client().fetch(...) itself raises an exception (for example an HTTP client exception), that exception will propagate to the caller. The method does not catch such exceptions.

## State Changes:
    Attributes READ:
        - self.settings: used to read OAuth client credentials at self.settings[self._OAUTH_SETTINGS_KEY]['key'] and ['secret'].
        - self._OAUTH_SETTINGS_KEY: constant key ('oauth') indicating where OAuth settings live inside settings.
        - self._OAUTH_ACCESS_TOKEN_URL: property that resolves the Okta token endpoint URL (depends on the handler's base_url environment variable).
        - self.get_auth_http_client(): called to obtain the HTTP client used for the request.

    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - redirect_uri and code should be non-empty strings appropriate for the OAuth flow.
        - self.settings must contain the OAuth configuration at self.settings[self._OAUTH_SETTINGS_KEY] with at least the keys 'key' (client_id) and 'secret' (client_secret).
        - self._OAUTH_ACCESS_TOKEN_URL must be a valid URL string (this property depends on the handler's base_url being set, typically via the FLOWER_OAUTH2_OKTA_BASE_URL environment variable).
        - self.get_auth_http_client() must return an object with an awaitable fetch(...) method that results in a response object having .error and .body attributes.

    Postconditions:
        - On successful completion, a dict parsed from the token endpoint's JSON response is returned.
        - On failure where response.error is truthy, tornado.auth.AuthError is raised and no return value is produced.
        - Any other errors raised by the HTTP client or JSON decoding will propagate.

## Side Effects:
    - Network I/O: performs a POST to the Okta token endpoint (self._OAUTH_ACCESS_TOKEN_URL) with form-encoded body containing redirect_uri, code, client_id, client_secret and grant_type=authorization_code.
    - Sends HTTP headers: 'Content-Type': 'application/x-www-form-urlencoded' and 'Accept': 'application/json'.
    - No modifications to cookies, session, or handler attributes are performed by this method; higher-level methods (e.g., _on_auth or get) handle cookies and redirects after receiving the token response.
    - Possible propagation of HTTP client exceptions (no additional error handling inside this method).

### `flower.views.auth.OktaLoginHandler.get` · *method*

## Summary:
Handles the GET step of the OAuth2/OpenID Connect login flow: either initiates an authorization redirect (saving a state token in a secure cookie) or, when returning from the provider with an authorization code, validates the state token, exchanges the code for tokens, and continues authentication via an async callback.

## Description:
This asynchronous GET handler is invoked by Tornado's request lifecycle when the associated route receives an HTTP GET request. Typical call scenarios:
- Initial login request: called with no query parameters to start the OAuth flow; it generates a state token, stores it in a secure cookie, and redirects the user to the provider's authorization endpoint.
- OAuth provider callback: called with a 'code' (authorization code) and 'state' query parameters after the provider redirects back; it validates the returned state token, exchanges the code for tokens, and passes the token response to the handler's authentication continuation.

This logic is in its own method because Tornado RequestHandler subclasses expose HTTP verbs (get/post/etc.) as methods that participate in the request lifecycle; placing the OAuth GET flow inside get() centralizes request handling, leverages Tornado's async/await for non-blocking token exchange, and cleanly separates request-processing logic from other handler responsibilities.

## Args:
None (this is a Tornado RequestHandler method; all input comes from self.get_argument and handler state).

## Returns:
None.
- The method does not return a value. Its observable effects are HTTP-side effects (redirect, cookies, or subsequent authentication actions).
- In the initial-redirect branch it triggers an HTTP redirect via authorize_redirect (no return value expected).
- In the code-exchange branch it awaits get_access_token and _on_auth which may produce side effects or further redirects.

## Raises:
- tornado.auth.AuthError: raised explicitly when the 'state' query parameter is missing or does not match the previously stored secure cookie (state tokens do not match).
- tornado.web.MissingArgumentError: may be raised by self.get_argument('state') if the 'state' argument is absent (this originates from Tornado's RequestHandler.get_argument).
- KeyError (or TypeError): may be raised while accessing self.settings[self._OAUTH_SETTINGS_KEY]['redirect_uri'] (or ['key']) if the expected settings key or nested keys are not present or not subscriptable.

## State Changes:
Attributes READ:
- self.settings — read to obtain OAuth configuration via self.settings[self._OAUTH_SETTINGS_KEY]['redirect_uri'] and self.settings[self._OAUTH_SETTINGS_KEY]['key'].
- self._OAUTH_SETTINGS_KEY — used as the lookup key into settings.
- Cookie read via self.get_secure_cookie('oauth_state') to obtain the previously-generated state token.
- Request arguments read via self.get_argument('code') and self.get_argument('state').

Attributes WRITTEN:
- A secure cookie named "oauth_state" is set via self.set_secure_cookie("oauth_state", state) in the initial-redirect branch. This persists the generated UUID state token to validate the callback later.

## Constraints:
Preconditions:
- self.settings must contain an entry at self._OAUTH_SETTINGS_KEY that is a mapping with at least:
    - 'redirect_uri' (string) used for the OAuth redirect URI.
    - 'key' (client id string) used for the authorization request.
- The request context must be a valid Tornado HTTP GET request (Tornado will call this method).
- For the code-exchange branch: the incoming request must include the query parameter 'code' (authorization code) and normally 'state' (the provider's returned state value).

Postconditions:
- If the initial-redirect branch runs: a secure cookie "oauth_state" is set (value: UUID string), and the response is an outbound redirect to the provider authorization endpoint (via authorize_redirect).
- If the code-exchange branch runs and state matches: get_access_token(...) is awaited and its response is passed to await self._on_auth(...). Depending on their implementations, authentication state (session, cookies, redirects) will be advanced by those methods.
- If the code-exchange branch runs and state does not match: tornado.auth.AuthError is raised and no token exchange is attempted.

## Side Effects:
- Network / external I/O: awaits self.get_access_token(...) which likely performs an HTTP call to exchange the authorization code for tokens; awaits self._on_auth(...) which may perform additional I/O or mutations (e.g., database, session storage, further redirects).
- HTTP response mutations:
    - Calls self.authorize_redirect(...) to issue an HTTP redirect to the OAuth provider in the initial branch.
    - Calls self.set_secure_cookie(...) to persist the OAuth state token as a secure cookie.
- Can raise exceptions that propagate to Tornado's error handling (e.g., AuthError or MissingArgumentError) if input validation fails.

### `flower.views.auth.OktaLoginHandler._on_auth` · *method*

## Summary:
Handles the OAuth2 token-response for an Okta login: verifies the access token by fetching userinfo, checks the user's email is allowed, sets the authenticated user cookie, clears the oauth state cookie, and redirects the client to the next page. On success this mutates the handler's cookie state and issues an HTTP redirect.

## Description:
This coroutine is invoked after an OAuth2 authorization code flow completes and the application has exchanged the code for an access token. Known callers:
- OktaLoginHandler.get: after exchanging the authorization code for an access token, get() calls await self._on_auth(access_token_response) to complete login.

Lifecycle / pipeline stage:
- Runs during the OAuth callback handling path. It is responsible for converting an access_token_response into an authenticated session for the user (or rejecting access).

Why this logic is a separate method:
- Separates the concerns of obtaining an access token (get_access_token) from validating the token and establishing a session (this method).
- Improves readability and testability by isolating userinfo fetch, email validation, cookie-setting, and redirect logic.
- Allows reuse or override in subclasses that might change only the userinfo/validation behavior.

## Args:
    access_token_response (dict): Expected to be the parsed JSON dictionary returned by the token endpoint (the result of get_access_token). Required keys:
        - 'access_token' (str): Bearer token used to call the userinfo endpoint.
    Notes:
        - If access_token_response is falsy (None, empty, False) the method raises an HTTPError(500).
        - If the 'access_token' key is missing a KeyError will be propagated.

## Returns:
    None
    - The handler does not return a value to the caller; on success it performs a redirect and therefore completes the HTTP response. Callers should await this coroutine but should not expect a return value.

## Raises:
    tornado.web.HTTPError(500, 'OAuth authentication failed')
        - Raised when access_token_response is falsy (None or empty).
    tornado.web.HTTPError(403, message)
        - Raised when the userinfo indicates the email is not verified or the email fails authentication policy checks (see authenticate()).
        - Error message: "Access denied. Please use another account or ask your admin to add your email to flower --auth."
    KeyError
        - If access_token_response does not contain 'access_token', the attempt to access access_token_response['access_token'] will raise KeyError.
    json.JSONDecodeError
        - If the response.body from the userinfo endpoint is not valid JSON, json.loads(...) will raise.
    Any exceptions raised by:
        - self.get_auth_http_client().fetch(...) (network, HTTP client-level errors)
        - authenticate(self.application.options.auth, email) (TypeError, re.error, etc. as documented by authenticate)
      These exceptions are not caught inside this method and will propagate to the caller.

## State Changes:
Attributes and methods READ:
    - self._OAUTH_USER_INFO_URL (str): used as the URL for the userinfo fetch.
    - self.get_auth_http_client() (method): invoked to obtain an HTTP client to call the userinfo endpoint.
    - response.body (bytes): read from the fetch result and decoded.
    - decoded_body (dict): used to extract 'email' and 'email_verified'.
    - authenticate (function): called with (self.application.options.auth, email) to decide whether the email is allowed.
    - self.application.options.auth: passed to authenticate; may be None or a pattern/configuration used by authenticate.
    - self.application.options.url_prefix (str or falsy): used when calculating the default/normalized redirect target.
    - self.get_argument('next', default) (method): reads the 'next' query parameter (or default) to decide redirect destination.

Attributes and methods WRITTEN / mutated:
    - self.set_secure_cookie("user", <email_str>): writes a secure cookie named "user". This mutates the outgoing response (cookie state).
    - self.clear_cookie('oauth_state'): clears the 'oauth_state' cookie.
    - self.redirect(next_): issues an HTTP redirect (mutates response state and terminates further request handling).
    - No direct mutation of Python attributes on self (no assignment to self.<attr>), only cookie and response mutations via handler methods.

## Constraints:
Preconditions:
    - access_token_response must be truthy and must contain the key 'access_token' whose value is a string (or an object convertible to str).
    - self.get_auth_http_client() must return a working HTTP client with an async fetch(url, ...) method that yields a response object with .body bytes.
    - The application should have a valid self.application.options.auth configuration compatible with authenticate().
    - The Okta base URL properties (self._OAUTH_USER_INFO_URL) must be correctly configured (see class properties returning base_url).

Postconditions (guarantees on success):
    - A secure cookie named "user" is set with the email string (str(email)).
    - The cookie 'oauth_state' is cleared.
    - The client is redirected to a normalized next_ URL:
        - next_ is taken from the request argument 'next' if present, else defaults to self.application.options.url_prefix or '/'.
        - If self.application.options.url_prefix is truthy and next_ does not start with '/', a leading '/' is prepended.
    - No value is returned; the response is redirected and the handler's HTTP response is sent to the client.

## Side Effects:
    - Network I/O: performs an asynchronous HTTP GET (via self.get_auth_http_client().fetch) to the userinfo endpoint (self._OAUTH_USER_INFO_URL) with an Authorization: Bearer <access_token> header.
    - JSON parsing: decodes and parses the response body using json.loads(...).
    - Calls authenticate(...) which performs pattern matching (may perform regex operations).
    - Mutates HTTP response cookies: sets "user", clears "oauth_state".
    - Issues an HTTP redirect to the client (terminates normal response flow).
    - May propagate network or parsing exceptions to the caller; these exceptions may affect the HTTP response sent to the client unless handled upstream.

## Implementation notes (edge cases and important details):
    - The method treats any falsy access_token_response as an immediate failure (500). If token endpoints return an empty object or unexpected structure, KeyError or 500 will occur.
    - email is extracted as (decoded_body.get('email') or '').strip() — an absent or null email becomes the empty string; this will cause authenticate(...) to likely fail and lead to a 403.
    - email_verified is computed by combining decoded_body.get('email_verified') (truthy/falsy) and authenticate(...). authenticate may return a boolean or a truthy/falsy re.Match; this code treats any truthy result as verification success. Callers should be aware authenticate may return re.Match (see its docs) and coerce to boolean if needed.
    - The method does not validate or sanitize the 'next' argument beyond ensuring it starts with '/' when url_prefix is set. It does not check for open-redirect vectors; callers or the application should ensure that the 'next' parameter is safe or restricted to internal paths if required.
    - All propagated exceptions are left for upstream handling; callers should wrap _on_auth in try/except if they need custom error handling.

