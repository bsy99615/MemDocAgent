# `jwks_client.py`

## `jwt.jwks_client.PyJWKClient` · *class*

*No documentation generated.*

### `jwt.jwks_client.PyJWKClient.__init__` · *method*

## Summary:
Initializes a PyJWKClient instance, validating caching parameters and establishing instance state used for fetching and caching JWK(s).

## Description:
This constructor is invoked when a caller creates a new PyJWKClient object to prepare it to fetch JSON Web Keys (JWKs) from a remote JWKS URI and optionally cache them or cache individual signing keys. Typical callers are client code or higher-level library components that need a configured JWK client during application startup or when preparing to verify JWTs. This logic is encapsulated in its own method because it centralizes:
- validation of incoming configuration (e.g., lifespan),
- construction of optional caching mechanisms (JWKSetCache),
- and conditional decoration of the instance method get_signing_key with an LRU cache — concerns that belong to object construction rather than runtime methods.

The constructor does not perform network I/O or fetch keys; it only prepares the client's configuration and cache layers that later methods will use.

## Args:
    uri (str): The JWKS endpoint URI. Must be a string; used as-is and stored on the instance.
    cache_keys (bool): Whether to enable per-key caching by wrapping get_signing_key with an LRU cache. Defaults to False.
    max_cached_keys (int): Maximum number of keys to retain in the LRU cache when cache_keys is True. Defaults to 16. Must be a non-negative integer (0 means no entries will be cached but the wrapper is still applied).
    cache_jwk_set (bool): Whether to enable caching of the full JWK set via a JWKSetCache. Defaults to True.
    lifespan (int): Lifespan (in seconds) for entries in the JWKSetCache if cache_jwk_set is True. Defaults to 300. Must be greater than 0 when cache_jwk_set is True.
    headers (Optional[Dict[str, Any]]): Optional HTTP headers to send when fetching the JWKS. If None, an empty dict is used. The dict is stored by reference on the instance (mutations to the passed dict will be visible to the instance).
    timeout (int): Network timeout in seconds to use when fetching JWKS in later operations. Stored on the instance. Defaults to 30.
    ssl_context (Optional[SSLContext]): Optional SSLContext to use for HTTPS requests when fetching JWKS. Defaults to None.

## Returns:
    None — as a Python constructor, it initializes instance attributes and does not return a value.

## Raises:
    PyJWKClientError: Raised if cache_jwk_set is True and lifespan <= 0. The exact error message is:
        'Lifespan must be greater than 0, the input is "<lifespan>"'
    (No network-related exceptions are raised by this constructor itself.)

## State Changes:
Attributes READ:
    - None of the instance attributes are required to exist prior to construction for this method to work. The method does implicitly reference the instance method get_signing_key when optionally wrapping it, but it does not otherwise read pre-existing instance state.

Attributes WRITTEN:
    - self.uri (str): set to the provided uri argument.
    - self.jwk_set_cache (Optional[JWKSetCache]): set to a new JWKSetCache(lifespan) when cache_jwk_set is True (and lifespan > 0); otherwise set to None.
    - self.headers (Dict[str, Any]): set to the provided headers dict, or to a new empty dict if headers was None.
    - self.timeout (int): set to the provided timeout value.
    - self.ssl_context (Optional[SSLContext]): set to the provided ssl_context value.
    - self.get_signing_key (callable): if cache_keys is True, replaced on the instance with an lru_cache-wrapped version of the existing get_signing_key method (maxsize set to max_cached_keys). If cache_keys is False, this attribute is left unchanged.

## Constraints:
Preconditions:
    - uri must be a string (no explicit type enforcement is performed here; passing other types may produce downstream errors).
    - If cache_jwk_set is True, lifespan must be an integer > 0. Otherwise a PyJWKClientError is raised.

Postconditions:
    - After return, self.uri, self.headers, self.timeout, and self.ssl_context reflect the provided inputs (with headers normalized to a dict if None was passed).
    - After return, self.jwk_set_cache is either None or an instance of JWKSetCache(initialized with lifespan).
    - After return, if cache_keys was True, self.get_signing_key is an LRU-cached callable with maxsize equal to max_cached_keys; otherwise it remains the original callable bound to the instance.

## Side Effects:
    - No network I/O or file I/O is performed.
    - The headers dict provided by the caller is stored by reference; subsequent external mutations to that dict will be observable by this instance.
    - If cache_keys is True, the instance's get_signing_key attribute is rebound to an lru_cache-wrapped callable. This mutation affects only this instance (not the class-level method).

### `jwt.jwks_client.PyJWKClient.fetch_data` · *method*

## Summary:
Fetches JSON data from the client's configured JWKS URI over HTTP(S), returns the parsed JSON object on success, and updates the optional JWK set cache (stores the fetched value or clears it on failure).

## Description:
This method performs the network request to retrieve the JWKS payload from the remote endpoint referenced by the client's uri, decodes the response body as JSON, and (when a cache is configured) writes the result into the JWKSetCache.

Known callers and usage context:
- PyJWKClient.get_jwk_set(refresh: bool = False) calls this method when there is no cached value or when a forced refresh is required.
- Higher-level helpers that obtain signing keys (get_signing_keys, get_signing_key, get_signing_key_from_jwt) indirectly invoke this method via get_jwk_set when they need up-to-date key material.
- Typical lifecycle stage: network fetch step invoked during key discovery/refresh before converting the JSON into a PyJWKSet.

Why this logic is separated:
- Isolates network I/O, error handling for connection/timeout failures, JSON decoding, and cache-write semantics into a single unit so higher-level logic (parsing into PyJWKSet, key selection) can assume it receives the raw JSON payload or a deterministic exception. This separation also ensures that cache update/clearing occurs reliably via the finally block regardless of the fetch outcome.

## Args:
This is an instance method and takes no explicit parameters beyond self. It relies on the following instance attributes:
- self.uri (str): URL to request; must be set to the JWKS endpoint.
- self.headers (Optional[Dict[str, Any]]): HTTP headers to include in the request (defaults provided by constructor).
- self.timeout (int): Request timeout in seconds (used as urllib timeout).
- self.ssl_context (Optional[SSLContext]): Optional SSLContext passed to urllib.request.urlopen; may be None.
- self.jwk_set_cache (Optional[JWKSetCache]): If not None, the method will call its put(...) method with the fetched JSON (or None on failure) before returning/propagating exceptions.

## Returns:
- Any: The value returned by json.load(response) — i.e., the JSON-deserialized response body.
  - Typical value: a dict representing the JWKS (expected by callers), but it may be any JSON type (list, None, etc.) depending on the remote server response.
  - On success (no exceptions): this value is returned from the method after being stored in the cache (if configured).

## Raises:
- PyJWKClientConnectionError:
  - Raised when urllib.request.urlopen or the request stage raises URLError or TimeoutError. The raised error message includes the original exception's string.
  - Side effect: before the exception propagates, if a JWKSetCache is configured, it receives put(None) (clearing the cache).
- Any exceptions raised by json.load (for example json.JSONDecodeError) or urllib that are not URLError/TimeoutError:
  - These exceptions are not caught by this method and will propagate to the caller.
  - Side effect: even when such an exception propagates, the finally block still runs and, if a cache is configured, put(None) will be called.

## State Changes:
Attributes READ:
- self.uri
- self.headers
- self.timeout
- self.ssl_context
- self.jwk_set_cache

Attributes WRITTEN:
- No direct assignment to self.<attr> is performed by this method.
- Indirect mutation: if self.jwk_set_cache is not None, the method calls self.jwk_set_cache.put(jwk_set). That call mutates the internal state of the JWKSetCache instance (stores the fetched PyJWKSet or clears the cache when jwk_set is None).

## Constraints:
Preconditions:
- self.uri should be a valid URL string pointing to a JWKS endpoint; the method does not validate URI format beyond passing it to urllib.
- self.headers should be a mapping of header names to values (the constructor ensures a default {} if None).
- self.timeout should be a number acceptable to urllib.request.urlopen as a timeout value.

Postconditions:
- On successful fetch and JSON decode:
  - The returned value equals the JSON-decoded response body.
  - If self.jwk_set_cache is configured, self.jwk_set_cache.put(returned_value) has been called before the method returns.
- On URLError or TimeoutError:
  - A PyJWKClientConnectionError is raised (wraps original exception text).
  - If self.jwk_set_cache is configured, self.jwk_set_cache.put(None) is called (cache cleared).
- On any other exception raised during json.load or elsewhere:
  - The exception propagates unchanged; if self.jwk_set_cache is configured, self.jwk_set_cache.put(None) is still called in the finally block.

## Side Effects:
- Network I/O: opens an HTTP(S) connection to self.uri using urllib.request.urlopen with the configured headers, timeout, and ssl_context. This may perform DNS resolution, TLS handshake, and contact external servers.
- Cache mutation: calls self.jwk_set_cache.put(jwk_set) when a cache is configured. The argument is the parsed JSON on success or None on failure/exception — thus either updates or clears the cached JWK set.
- No other external I/O (files, DB) or persistent changes to the PyJWKClient instance itself are performed.

## Implementation notes / edge cases to preserve when reimplementing:
- Always invoke the cache put(...) in a finally block so the cache is updated or cleared regardless of success or exception.
- Only URLError and TimeoutError are translated into PyJWKClientConnectionError. All other exceptions (including JSONDecodeError) should propagate unchanged.
- Use json.load on the response file-like object (i.e., do not read() then json.loads() unless behavior is preserved).
- Ensure headers are applied when constructing the urllib.request.Request so servers requiring specific headers can respond correctly.

### `jwt.jwks_client.PyJWKClient.get_jwk_set` · *method*

## Summary:
Return a validated PyJWKSet for this client by reading the cached JWKS when available (unless refresh is requested) or fetching it from the configured URI; this does not itself mutate attributes but may cause the client's cache to be updated indirectly via the fetch path.

## Description:
Known callers and when they call this method:
- PyJWKClient.get_signing_keys(refresh: bool = False) — calls this to obtain the PyJWKSet used to filter signing keys; usually invoked during token validation or key discovery.
- PyJWKClient.get_signing_key(kid: str) — indirectly depends on this via get_signing_keys when locating a specific key by kid.
- External callers who need the complete validated JWK set for inspection or custom logic may call this method directly.
Lifecycle / pipeline stage:
- Invoked at key lookup / token verification time: when code needs current JWKs to extract signing keys or to validate JWT signatures.
Why this is a separate method:
- Encapsulates cache lookup semantics (use cache unless refresh requested), fetch-on-miss behavior, JSON structure validation, and conversion into the PyJWKSet abstraction.
- Reused by multiple higher-level methods (get_signing_keys, get_signing_key) so centralizing this logic avoids duplication and ensures consistent error handling and caching behavior.

## Args:
    refresh (bool): Optional; defaults to False.
        - If False: attempt to retrieve a cached JWK set from self.jwk_set_cache (if present) before making a network call.
        - If True: bypass the cache and always invoke fetch_data() to obtain fresh JWKS from the remote URI.

## Returns:
    PyJWKSet
    - A PyJWKSet instance constructed from the JWKS returned by cache or fetch.
    - Guaranteed to be a PyJWKSet on successful return (method converts and validates the dict via PyJWKSet.from_dict).
    - Edge cases:
        - This method never returns None. Either a PyJWKSet is returned, or an exception is raised.

## Raises:
    PyJWKClientError
        - Raised when the retrieved JWKS value is not a dict (exact condition in code: not isinstance(data, dict)). Message: "The JWKS endpoint did not return a JSON object".
    PyJWKClientConnectionError
        - May be raised when fetch_data() encounters a network issue (urllib URLError or TimeoutError). Condition originates from fetch_data and is propagated to callers.
    json.JSONDecodeError
        - May propagate if fetch_data() receives a response that cannot be parsed as JSON (json.load raises); this is not caught by get_jwk_set.
    PyJWKSetError (or other exceptions raised by PyJWKSet.from_dict)
        - If the dict is missing required "keys" structure, contains no usable keys, or otherwise fails the PyJWKSet constructor/validation, from_dict (or the constructor it calls) will raise the relevant exception; that exception propagates to callers of get_jwk_set.
    Other exceptions
        - Any other exception that fetch_data() or PyJWKSet.from_dict may raise can propagate through this method (e.g., unexpected attribute errors). The method does not broadly catch or wrap non-network/non-structure errors.

## State Changes:
Attributes READ:
    - self.jwk_set_cache: inspected to decide whether to use a cached value (get()) or to fetch new data.
    - (implicitly) other attributes used by fetch_data when called (e.g., self.uri, self.headers, self.timeout, self.ssl_context) are read by fetch_data but not directly by this method.
Attributes WRITTEN:
    - Direct: None. get_jwk_set does not assign to any self.<attr> itself.
    - Indirect (side-effect of calling fetch_data): fetch_data()'s finally block calls self.jwk_set_cache.put(jwk_set) when self.jwk_set_cache is not None; therefore, calling get_jwk_set that results in fetch_data() may update the cache (either storing a new PyJWKSet-derived dict or clearing the cache by putting None). This write occurs inside fetch_data, not by get_jwk_set directly.

## Constraints:
Preconditions:
    - The PyJWKClient instance must be properly initialized (constructor run), so that attributes referenced by fetch_data and cache logic exist (uri, headers, timeout, ssl_context, jwk_set_cache).
    - No additional preconditions on the refresh parameter beyond being a boolean.

Postconditions:
    - On success: returns a PyJWKSet that represents the JWKS obtained either from cache or newly fetched data. If fetch_data was invoked, the client's jwk_set_cache may have been updated (see State Changes).
    - On failure: no PyJWKSet is returned and an exception is raised. The cache state may still have been updated by fetch_data's finally block (e.g., cleared on parse failure).

## Side Effects:
    - Network I/O: If cache miss or refresh=True, this method calls fetch_data(), which performs an HTTP(S) request to self.uri. That network call may raise PyJWKClientConnectionError on URLError/TimeoutError or propagate json.JSONDecodeError for bad JSON bodies.
    - Cache mutation (indirect): fetch_data() always executes its finally block which, when self.jwk_set_cache is not None, calls self.jwk_set_cache.put(jwk_set). As a result:
        - On successful fetch and JSON parse, the fetched data (the raw parsed JSON value) is put into the cache.
        - On fetch/parse failure, jwk_set passed to put may be None, which results in clearing the cache.
    - No other attributes on self are modified by get_jwk_set itself.
    - No logging, file I/O, or other external side effects are performed by get_jwk_set directly (but may occur inside fetch_data or the PyJWKSet.from_dict constructor).

### `jwt.jwks_client.PyJWKClient.get_signing_keys` · *method*

## Summary:
Return the list of PyJWK objects from the JWKS endpoint that are usable for verifying signatures, optionally forcing a refresh of the cached JWKS.

## Description:
Known callers and context:
- PyJWKClient.get_signing_key: calls this method to obtain candidate signing keys before selecting one matching a given "kid".
- PyJWKClient.get_signing_key_from_jwt: indirectly calls this method (via get_signing_key) when resolving the signing key for an incoming JWT.
- External callers may call this method directly to enumerate all available signing keys for diagnostics or verification tooling.

When invoked in the token verification lifecycle, this method represents the "discover usable signing keys" step: it fetches (or retrieves from cache) the JWK Set, filters keys to those intended for signature use and that carry a key identifier, and returns the filtered collection. This is a separate method to keep filtering and validation logic centralized (so callers like get_signing_key can reuse the same list, and to allow optional caching / lru_cache decoration of the higher-level get_signing_key method without duplicating filtering logic).

## Args:
    refresh (bool): If False (default), allow returning a JWKS from the client's internal cache (if present and valid). If True, force fetching a fresh JWKS from the configured URI and bypass cached JWKS contents.

## Returns:
    list[PyJWK]: A list of PyJWK instances selected from the JWKS where
        - each PyJWK.key_id is truthy (i.e., a non-empty kid),
        - and each PyJWK.public_key_use is either the string "sig" or None (no "use" field).
    Edge cases:
        - The returned list is guaranteed non-empty on success (the method raises instead of returning an empty list).
        - The method does not guarantee any particular ordering beyond the order produced by PyJWKSet.keys.

## Raises:
    PyJWKClientError:
        - Raised when the filtered list of signing keys is empty. Exact message from the implementation: "The JWKS endpoint did not contain any signing keys".
        - Also may be raised indirectly if get_jwk_set raises PyJWKClientError (for example if the JWKS JSON is invalid).
    PyJWKClientConnectionError:
        - May propagate if get_jwk_set triggers a network fetch that fails (fetch_data raises this on URL/timeout errors).
    Any exceptions raised by get_jwk_set or PyJWKSet/PyJWK construction:
        - Exceptions from JWKS parsing or PyJWK construction (e.g., JSONDecodeError, PyJWKSetError, PyJWKError) will propagate out of this method.

## State Changes:
Attributes READ:
    - None accessed directly by this method. (The method invokes self.get_jwk_set(refresh) but does not directly read self.<attr> fields.)
Attributes WRITTEN:
    - None directly written by this method.
Indirect state effects (caused by called methods):
    - get_jwk_set may read and/or write self.jwk_set_cache and may call fetch_data, which may update the cache via jwk_set_cache.put.

## Constraints:
Preconditions:
    - The PyJWKClient instance must be initialized correctly (valid uri, optional jwk_set_cache configured). More concretely, get_jwk_set(refresh) must be callable and must return a PyJWKSet instance or raise an appropriate exception.
    - Calling code must be prepared to handle the exceptions documented above (especially PyJWKClientError and PyJWKClientConnectionError).

Postconditions:
    - On successful return, a non-empty list of PyJWK objects is returned, and each returned PyJWK satisfies:
        - key_id (kid) is truthy,
        - public_key_use is either "sig" or None.
    - The method itself does not modify the PyJWKClient instance fields; however, if get_jwk_set caused a network fetch, the client's jwk_set_cache may have been updated.

## Side Effects:
    - Possible network I/O: if refresh is True or if there is no valid cached JWK Set, calling this method will cause get_jwk_set to fetch data from the configured JWKS URI (which performs an HTTP(S) request).
    - Cache mutation: a successful remote fetch performed by get_jwk_set/fetch_data may update the client's jwk_set_cache via its put method.
    - No file I/O, no direct cryptographic operations, and no mutation of returned PyJWK objects is performed by this method.

### `jwt.jwks_client.PyJWKClient.get_signing_key` · *method*

## Summary:
Return the PyJWK public signing key that matches the given key id (kid), retrying once by refreshing the JWKS if no immediate match is found. Does not modify PyJWKClient attributes directly, but may trigger network fetches and updates to the internal JWK set cache.

## Description:
This method is used to obtain the single signing key from the JWKS that corresponds to the provided kid. Typical callers and contexts:
- PyJWKClient.get_signing_key_from_jwt: called during JWT verification to look up the correct key after extracting the token header's "kid".
- External callers that need the public key for verifying a JWT signature or for key metadata access.

Why this is a separate method:
- Encapsulates the retry/refresh logic used when a kid is not found on the first read of cached keys.
- Enables memoization (via lru_cache) at the method level when PyJWKClient is instantiated with cache_keys=True.
- Keeps key-matching and JWKS-fetching concerns separated so the matching logic can be reused independently.

## Args:
    kid (str): Key identifier (kid) from the JWT header. This should be the exact key id string to match against PyJWK.key_id. Passing None or a non-string is allowed at runtime (Python typing is not enforced) but will not match any key and will lead to an error described below.

## Returns:
    PyJWK: The first PyJWK in the JWKS whose key_id equals the provided kid. Guarantee: on successful return, returned.key_id == kid (string equality). The function never returns None; if no matching key is found it raises an error.

## Raises:
    PyJWKClientError:
        - If no matching signing key is found after a refresh attempt:
            f'Unable to find a signing key that matches: "{kid}"'
        - May also be raised and propagated from underlying calls:
            * If the JWKS endpoint returned a non-dictionary value (get_jwk_set raises "The JWKS endpoint did not return a JSON object")
            * If the JWKS endpoint contained no signing keys (get_signing_keys raises "The JWKS endpoint did not contain any signing keys")
    PyJWKClientConnectionError:
        - Propagated from fetch_data when a network error occurs (URLError, TimeoutError) while trying to fetch the JWKS.
    Any exception raised by underlying components (e.g., JSON decoding errors) will propagate up as-is.

## State Changes:
Attributes READ:
    - self.jwk_set_cache (accessed indirectly via get_jwk_set/get_signing_keys)
    - self.uri, self.headers, self.timeout, self.ssl_context (used indirectly by fetch_data when a network request is performed)
Attributes WRITTEN:
    - self.jwk_set_cache contents may be updated (via JWKSetCache.put) when underlying fetch_data executes; this is an indirect mutation performed by get_signing_keys -> get_jwk_set -> fetch_data.

## Constraints:
Preconditions:
    - The caller should provide a kid that is intended to match one of the JWKS keys (string). If the kid is None or not present in the JWKS, the method will ultimately raise PyJWKClientError after a refresh attempt.
    - The PyJWKClient must have been constructed with a valid URI (self.uri) reachable by the environment when a network fetch is required.

Postconditions:
    - On success: returns a PyJWK whose key_id equals the provided kid.
    - On failure: either raises PyJWKClientError (no matching key or JWKS format problems) or propagates PyJWKClientConnectionError (network failure).

## Side Effects:
    - May perform network I/O to fetch the JWKS from self.uri (via fetch_data) if cached keys do not contain the requested kid or if refresh=True is triggered.
    - May update the internal JWKSetCache (self.jwk_set_cache.put) with the newly fetched JWKS.
    - If PyJWKClient was constructed with cache_keys=True, this instance method may be wrapped with functools.lru_cache; in that case repeated calls with the same kid may be served from the LRU cache and will not trigger network activity or cache updates on cache hits.
    - The method calls match_kid and get_signing_keys; any side effects or exceptions from those methods are inherited.

## Implementation notes (behavioral details to preserve when reimplementing):
    - First, attempt to obtain available signing keys by calling get_signing_keys() and try to match the kid using match_kid(signing_keys, kid).
    - If no match is found, call get_signing_keys(refresh=True) to force reloading the JWKS and try matching again.
    - If a match is still not found after refresh, raise PyJWKClientError with the exact message: 'Unable to find a signing key that matches: "{kid}"'.
    - Do not catch PyJWKClientConnectionError or the other PyJWKClientError cases raised by underlying calls; let them propagate.
    - When multiple keys share the same kid (unlikely but possible), return the first key encountered (match_kid selects the first equality match).

### `jwt.jwks_client.PyJWKClient.get_signing_key_from_jwt` · *method*

## Summary:
Extracts the JWT header without verifying the signature, obtains the header's "kid" value, and returns the PyJWK signing key that matches that kid by delegating to get_signing_key. The method itself does not mutate PyJWKClient attributes (any cache updates occur indirectly via the delegated key lookup).

## Description:
This helper is intended for verification flows that must look up which public key was used to sign a compact JWT before performing signature verification. It isolates the small, common operation of parsing a token's unverified header and resolving the matching key.

Known callers and contexts:
- Typical use: a JWT verification pipeline that receives a compact JWT string, calls this method to find the correct public key, then verifies the token signature using the returned PyJWK.
- External callers: any component that needs to retrieve the signing key for a token for verification or metadata inspection.
- Note: This repository does not show other in-repo callers; assume it is used by higher-level verification code.

Why this is a separate method:
- Separates "extract kid from token" from "resolve key from JWKS", enabling reuse and clearer testing.
- Keeps the header-extraction logic centralized and short, while leveraging get_signing_key's retry/cache/network behavior.
- Allows get_signing_key to be memoized (lru_cache) independently of token parsing.

## Args:
    token (str): Compact serialized JWT (expected to be a string using dot-separated segments). The method passes this token to an external decoder function with the signature decode_token(token, options=dict). Supplying a non-string token may cause the decoder or subsequent indexing operations to raise.

## Returns:
    PyJWK: The signing key object returned by self.get_signing_key(header.get("kid")). Guarantee on success: returned.key_id == header.get("kid") (string equality). The method never returns None; failures raise an exception.

## Raises:
    NameError:
        - If the name decode_token is not defined in the module scope, calling decode_token(...) will raise NameError immediately.
    Any exception raised by the decoder (decode_token):
        - If the token is malformed or the decoder fails, the decoder's exception (ValueError, custom DecodeError, etc.) will propagate.
    KeyError:
        - If the object returned by the decoder (unverified) does not support subscription with the key "header", then unverified["header"] raises KeyError.
    TypeError:
        - If the decoder returns None or a non-subscriptable value, unverified["header"] raises TypeError.
    AttributeError:
        - If the header value is not mapping-like and does not provide .get, calling header.get("kid") will raise AttributeError.
    PyJWKClientError:
        - Propagated from self.get_signing_key when no matching key is found after a refresh, or when the JWKS endpoint returns invalid data. Notable message on no-match: 'Unable to find a signing key that matches: "{kid}"'.
        - If header.get("kid") returns None (no kid in header), get_signing_key(None) will be called and will ultimately raise PyJWKClientError with the message containing "None".
    PyJWKClientConnectionError:
        - Propagated from underlying network failures (URLError, TimeoutError) raised by fetch_data called during get_signing_key/get_signing_keys.

## State Changes:
Attributes READ:
    - Indirectly reads attributes used by get_signing_key/get_signing_keys/get_jwk_set/fetch_data:
        * self.jwk_set_cache (to check/get/put cached JWKS)
        * self.uri, self.headers, self.timeout, self.ssl_context (used if a JWKS network fetch occurs)
Attributes WRITTEN:
    - The method does not directly assign to any self.<attr>.
    - Indirect side-effect: calling get_signing_key may cause fetch_data to execute and then self.jwk_set_cache.put(...) to update the cached JWKS (if a cache exists).

## Constraints:
Preconditions:
    - A function named decode_token must be available in the executing scope and accept (token, options=dict) returning an object that supports subscription with key "header" whose value is a mapping-like object exposing .get("kid").
    - The PyJWKClient instance should have a valid JWKS URI and any required network connectivity if get_signing_key must fetch keys.

Postconditions:
    - Success: returns a PyJWK whose .key_id equals the extracted header.kid.
    - Failure: raises one of the documented exceptions; the method itself does not leave self mutated except for any indirect cache updates performed by get_signing_key.

## Behavior (step-by-step; preserve this when reimplementing):
1. Call decode_token(token, options={"verify_signature": False}) to parse the token without attempting signature verification.
2. Read unverified["header"] from the decoder's return value and assign to header.
3. Extract kid = header.get("kid") (may return None if "kid" missing).
4. Call and return self.get_signing_key(kid). Do not catch exceptions raised by get_signing_key; let them propagate to the caller.

Edge cases and exact outcomes:
- If decode_token is absent (NameError) or raises due to token format, that exception propagates and no key lookup is attempted.
- If unverified["header"] is missing or malformed, KeyError/TypeError/AttributeError will be raised at steps 2–3.
- If kid is missing or None, get_signing_key(None) is invoked; because match will fail, get_signing_key will attempt a JWKS refresh and then raise PyJWKClientError with the message 'Unable to find a signing key that matches: "{kid}"' (kid formatted as the actual None or value).
- If the JWKS endpoint is unreachable during a forced refresh, PyJWKClientConnectionError will propagate.

## Side Effects:
    - Calls an external decoder with verify disabled; the decoder may internally perform parsing or validation.
    - Delegates to self.get_signing_key(header.get("kid")), which may:
        * Perform network I/O to fetch JWKS from self.uri.
        * Update the internal JWKSetCache via put(...) when a fresh fetch occurs.
        * Be cached via lru_cache if this PyJWKClient instance wrapped get_signing_key with caching; in that case repeated identical kid lookups may be served from in-memory cache without network I/O.
    - The method itself performs no I/O or logging; all side effects are indirect via the decoder and get_signing_key.

### `jwt.jwks_client.PyJWKClient.match_kid` · *method*

## Summary:
Performs a linear search over the provided PyJWK list and returns the first PyJWK whose key_id equals the given kid; does not modify the input list.

## Description:
This small utility locates a signing key by matching the JWK "kid" (key id) value. It is intended to be used by key-selection logic that operates on a list of PyJWK objects produced from a JWKS (for example, a JWKS client or a JWT verification pipeline). Separating this lookup into its own function keeps the matching semantics (first-match linear scan) encapsulated and reusable, and avoids duplicating the search logic wherever a kid-to-key lookup is needed.

Known / intended callers and context:
- Any code that has already parsed or constructed a List[PyJWK] (e.g., from a JWKS) and needs the PyJWK whose key_id equals the kid value extracted from a JWT header.
- Typically invoked during JWT verification when selecting which public key to use.

Why this is a standalone function:
- It expresses a single, well-scoped operation (kid → PyJWK lookup) that is used in multiple places during key-selection/verification flows.
- Implementing this as a discrete function improves readability and makes unit testing the lookup straightforward.

## Args:
    signing_keys (List[PyJWK]):
        - A list (or other iterable) of PyJWK instances to search.
        - Each element is expected to expose a key_id attribute or property (as provided by PyJWK).
        - No default; required.
    kid (str):
        - The key identifier to match against PyJWK.key_id.
        - Expected to be a string; exact equality comparison (==) is used.

## Returns:
    Optional[PyJWK]:
        - The first PyJWK instance from signing_keys for which key.key_id == kid.
        - Returns None if no matching key is found.
        - If multiple keys share the same kid, the function returns the first match encountered (left-to-right).

## Raises:
    - Does not explicitly raise exceptions in normal operation.
    - Possible runtime exceptions from incorrect inputs:
        * AttributeError: If an element in signing_keys does not have a key_id attribute/property.
        * TypeError: If signing_keys is not iterable (e.g., None) or if comparison operations between key_id and kid raise TypeError.
      These exceptions are not caught by the function and will propagate to the caller.

## State Changes:
    Attributes READ:
        - None on self (function is stateless and not a method on an object).
        - Reads each element.key_id from the provided signing_keys iterable.
    Attributes WRITTEN:
        - None (no mutation of signing_keys or its elements; the function assigns a local variable and returns it).

## Constraints:
    Preconditions:
        - signing_keys should be an iterable of PyJWK objects (or objects exposing key_id).
        - kid should be a value comparable to the key_id attributes (typically a str).
    Postconditions:
        - The input signing_keys is unmodified.
        - The returned value is either a PyJWK from the original iterable whose key_id equals kid, or None if no such element exists.

## Side Effects:
    - None: no I/O, no network access, no global state mutation.
    - The function only performs in-memory reads of the provided iterable and returns a reference to an existing PyJWK (does not clone or serialize it).

