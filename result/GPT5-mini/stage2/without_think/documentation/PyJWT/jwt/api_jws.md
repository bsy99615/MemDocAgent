# `api_jws.py`

## `jwt.api_jws.PyJWS` · *class*

*No documentation generated.*

### `jwt.api_jws.PyJWS.__init__` · *method*

## Summary:
Sets up the instance algorithm map and effective options: loads default algorithm implementations, restricts them to the provided allowed algorithm names (if any), and stores a merged options dict on the instance.

## Description:
This initializer runs at object construction time (i.e., when PyJWS() is instantiated) to produce a consistent instance state used by subsequent PyJWS methods. It performs three concrete tasks visible in the source:
1. Calls get_default_algorithms() and assigns its return value to self._algorithms.
2. Produces self._valid_algs as a set of allowed algorithm names determined from the algorithms argument or from the keys of self._algorithms when algorithms is None.
3. Prunes self._algorithms in-place by deleting any key not present in self._valid_algs, and establishes self.options by shallow-merging defaults with the provided options.

This logic is implemented in __init__ (rather than being inlined in other methods) so that other instance methods can rely on the presence and consistency of self._algorithms, self._valid_algs, and self.options without repeating selection/merging logic.

## Args:
    algorithms (list[str] | None): Optional list of algorithm names to allow for this instance. If provided (not None), it is converted to a set and assigned to self._valid_algs. If None, self._valid_algs is set to set(self._algorithms) where self._algorithms is the dict returned by get_default_algorithms(). An empty list is allowed and results in an empty set of valid algorithms.
    options (dict[str, Any] | None): Optional mapping of option names to values. If None, an empty dict is used. The final instance options are produced by merging the defaults returned by self._get_default_options() with this mapping; values in the provided options override defaults. Merging is shallow.

## Returns:
    None

## Raises:
    The __init__ body does not explicitly raise exceptions. Exceptions may propagate from called functions:
    - Exceptions raised by get_default_algorithms() will propagate.
    - Exceptions raised by self._get_default_options() will propagate.
    The method itself performs no validation that raises InvalidAlgorithmError, InvalidSignatureError, DecodeError, or InvalidTokenError.

## State Changes:
Attributes READ:
    - self._algorithms (read) — when algorithms is None the expression set(self._algorithms) is evaluated; this reads the keys of the dict previously assigned from get_default_algorithms().
    - self._get_default_options() is invoked to obtain default options (method call on self).

Attributes WRITTEN:
    - self._algorithms (dict): Set to the dict returned by get_default_algorithms(), then potentially pruned in-place by deleting keys missing from self._valid_algs.
    - self._valid_algs (set[str]): Created from the algorithms argument (converted to set) when provided; otherwise created from the keys of self._algorithms.
    - self.options (dict[str, Any]): Result of shallow-merging defaults (self._get_default_options()) with the caller-provided options; caller options override defaults.

## Constraints:
Preconditions:
    - No explicit type checks are performed. For predictable behavior, callers should pass algorithms as an iterable of strings (or None) and options as a dict-like mapping (or None).
    - If algorithms contains names not present in the default algorithm map, those names will appear in self._valid_algs but will not have corresponding entries in self._algorithms (see below).

Postconditions:
    - self._algorithms is a dict whose keys are a subset of self._valid_algs. Any key removed from the dict was deleted explicitly by the pruning loop.
    - self._valid_algs is a set of strings.
    - self.options is a dict containing all keys from the default options with overrides applied from the provided options; keys present only in provided options will be present in self.options.
    - The pruning loop iterates over list(self._algorithms.keys()) to avoid mutating the dict while iterating; deleted keys are removed from the dict object referenced by self._algorithms.

## Edge cases / Notes:
    - algorithms=[] results in self._valid_algs == set() and self._algorithms being pruned to an empty dict (no algorithms available).
    - algorithms containing names absent from get_default_algorithms() will result in those names being included in self._valid_algs but without corresponding implementations in self._algorithms.
    - options is merged shallowly: nested dictionaries are not deep-merged (a nested dict in options will replace the corresponding nested dict from defaults).
    - Because self._algorithms is assigned to the object returned by get_default_algorithms(), any assumptions about mutation or copy behavior depend on that function's return semantics; this method prunes the returned dict in-place.

## Side Effects:
    - Mutates the instance by assigning/altering self._algorithms, self._valid_algs, and self.options.
    - No direct I/O or external network calls are performed here; however, exceptions or side effects may arise from get_default_algorithms() or self._get_default_options() which are invoked during initialization.

## Example (descriptive):
    - If get_default_algorithms() returns {"HS256": <impl>, "RS256": <impl>} and the constructor is called with algorithms=["HS256"], then:
        * self._valid_algs == {"HS256"}
        * self._algorithms == {"HS256": <impl>}
        * self.options contains the default options with any provided option overrides applied.

### `jwt.api_jws.PyJWS._get_default_options` · *method*

## Summary:
Returns the minimal default options map used by PyJWS; specifically enables signature verification by default.

## Description:
This static helper produces the default options dictionary that the PyJWS instance uses during initialization. Known callers and usage context:
- PyJWS.__init__: called when a PyJWS instance is created to seed self.options via merging {**self._get_default_options(), **options}. This happens during the object's initialization lifecycle.
- Option merging/readers: the value produced here participates in later logic in decode_complete and decode where merged options determine whether signature verification is performed (merged_options["verify_signature"]).

Why this logic is a separate method:
- Encapsulates the default option set in one place so callers (including subclasses) can override or extend defaults by overriding this method.
- Keeps __init__ concise and makes unit testing of default behavior straightforward.
- Mirrors a similar design elsewhere in the codebase (e.g., PyJWT has a broader _get_default_options), allowing consistent extension across JWT-related classes.

## Args:
None.

## Returns:
dict[str, bool]
- A newly created mapping containing the key:
    - "verify_signature": True
- Possible values:
    - Always returns a dict with exactly the "verify_signature" key set to True.
- Edge-case return values:
    - None — not applicable; the function always returns the dict shown above.

## Raises:
None. The function is pure and does not raise exceptions.

## State Changes:
Attributes READ:
- None (method is a staticmethod and does not read instance attributes)

Attributes WRITTEN:
- None (method does not mutate self or any external state)

## Constraints:
Preconditions:
- None. Can be called without an instance (defined as a staticmethod) and requires no external state.

Postconditions:
- Caller receives a new dict containing {"verify_signature": True}.
- Callers that merge this dict into instance state (e.g., self.options = {**self._get_default_options(), **options}) will have "verify_signature" present unless overridden by the provided options.

## Side Effects:
- None. No I/O, no external service calls, and no mutation of objects outside the returned dict.

### `jwt.api_jws.PyJWS.register_algorithm` · *method*

## Summary:
Registers a new Algorithm implementation under the given algorithm identifier, updating the instance's algorithm registry and the set of valid algorithm names.

## Description:
Known callers and context:
- No internal callers are present in this module. This method is intended to be invoked by application code or library consumers during configuration time when adding support for a custom or third-party Algorithm implementation prior to performing encode/decode operations.
- Typical lifecycle: called at initialization/configuration stage (before encoding/decoding JWTs) to extend the PyJWS instance with additional signing/verification algorithms.

Why this logic is a dedicated method:
- Centralizes validation and mutation of the PyJWS algorithm registry (_algorithms and _valid_algs), ensuring a single place enforces uniqueness and type constraints for registered algorithm handlers.
- Keeps registration semantics explicit and reusable rather than duplicating membership checks and state updates elsewhere.

## Args:
    alg_id (str): Identifier name for the algorithm (e.g., "HS256", "RS256"). Must be a hashable string suitable for use as a dict key and set element. If an algorithm with this id is already registered, registration is rejected.
    alg_obj (Algorithm): An object implementing the Algorithm interface/class. The method requires the object to be an instance of Algorithm (or its subclass). The registered object will later be used for prepare_key, sign, and verify operations.

## Returns:
    None

## Raises:
    ValueError: Raised when alg_id is already present in self._algorithms (i.e., an algorithm with this identifier is already registered).
    TypeError: Raised when alg_obj is not an instance of Algorithm.

## State Changes:
    Attributes READ:
        self._algorithms — membership of alg_id is checked to prevent duplicate registration.
    Attributes WRITTEN:
        self._algorithms — a new mapping self._algorithms[alg_id] = alg_obj is inserted.
        self._valid_algs — alg_id is added to the set of valid algorithms via self._valid_algs.add(alg_id).

## Constraints:
    Preconditions:
        - self must have a mapping-like attribute _algorithms (supports membership test and item assignment).
        - self must have a set-like attribute _valid_algs (supports add()).
        - alg_id should be a hashable string (signature annotates str). While the method does not enforce the type of alg_id at runtime, non-hashable or non-string values will lead to runtime errors when used as dict/set keys elsewhere.
        - alg_obj must be an instance of Algorithm; otherwise a TypeError is raised.
    Postconditions:
        - If the call returns normally, self._algorithms contains an entry mapping alg_id to alg_obj.
        - If the call returns normally, self._valid_algs contains alg_id.
        - If the call raises ValueError or TypeError, neither self._algorithms nor self._valid_algs is modified for the given alg_id.

## Side Effects:
    - No I/O or network calls.
    - Mutates only the PyJWS instance state by updating self._algorithms and self._valid_algs.
    - The registered alg_obj is stored by reference and will be used later by other PyJWS methods (e.g., get_algorithm_by_name, encode, _verify_signature) which expect alg_obj to implement the Algorithm interface (prepare_key, sign, verify).

### `jwt.api_jws.PyJWS.unregister_algorithm` · *method*

## Summary:
Removes a previously registered algorithm from the instance's algorithm registry and from the set of valid algorithm names, updating the object's algorithm-related state.

## Description:
Known callers and context:
- No internal callers exist in this module; this method is intended to be invoked by application code or library consumers during configuration or teardown when an algorithm should no longer be available for signing/verification.
- Typical lifecycle: called during configuration changes (after PyJWS instantiation and before encode/decode operations that rely on algorithm availability), or when cleaning up custom algorithm registrations.

Why this logic is a dedicated method:
- Centralizes the removal of an algorithm handler and the corresponding valid-algorithm bookkeeping in one place, ensuring consistent mutation and a single point for raising an appropriate error when removal is invalid.
- Encapsulates both the registry mutation (dictionary) and the valid algorithm set update (set) so callers do not need to manage these two related structures themselves.

## Args:
    alg_id (str): Identifier of the algorithm to unregister (for example, "HS256" or "RS256").
        - Expected type: str (hashable).
        - Behavior on other types: not checked explicitly; passing a non-string or non-hashable value may raise a runtime error when used as a dict/set key.

## Returns:
    None
    - The method performs in-place mutation of the instance state and does not return a value.

## Raises:
    KeyError:
        - Raised when alg_id is not present in self._algorithms. The exact message raised by the implementation is:
          "The specified algorithm could not be removed because it is not registered."
        - Additionally, after deleting the entry from self._algorithms, the method calls self._valid_algs.remove(alg_id). If, due to external inconsistency, alg_id is absent from self._valid_algs, that call will raise KeyError (this is a possible secondary exception raised by the underlying set.remove operation).
    Notes:
        - No other exceptions are explicitly raised by this method. Type errors or other exceptions may occur elsewhere if self._algorithms or self._valid_algs do not behave like a dict and set respectively.

## State Changes:
    Attributes READ:
        self._algorithms — membership of alg_id is checked (alg_id in self._algorithms).
    Attributes WRITTEN:
        self._algorithms — the key alg_id is deleted (del self._algorithms[alg_id]).
        self._valid_algs — alg_id is removed from the set (self._valid_algs.remove(alg_id)).

## Constraints:
    Preconditions:
        - self must have a mapping-like attribute _algorithms supporting membership testing and deletion by key.
        - self must have a set-like attribute _valid_algs supporting removal via remove().
        - alg_id should be present in self._algorithms when this method is called, otherwise KeyError is raised.
        - For predictable behavior, alg_id should also be present in self._valid_algs; if not, a KeyError will be raised by the set removal.
    Postconditions:
        - On normal return (no exception), self._algorithms no longer contains alg_id and self._valid_algs no longer contains alg_id.
        - The method is not idempotent: calling it again for the same alg_id will raise KeyError.

## Side Effects:
    - Mutates only the in-memory state of the PyJWS instance (self._algorithms and self._valid_algs).
    - No I/O, network calls, or external side-effects are performed.
    - Not thread-safe: concurrent modifications to _algorithms or _valid_algs by other threads may cause race conditions or exceptions.

### `jwt.api_jws.PyJWS.get_algorithms` · *method*

## Summary:
Return a new list containing the algorithm identifier strings that this PyJWS instance currently accepts; the call is read-only and does not modify object state.

## Description:
This is a public accessor for consumers who need to inspect which signature algorithms are allowed by this PyJWS instance (for example, for UI display, validation, or to pass into decode calls). There are no callers within the PyJWS class itself; it exists to expose the configured algorithms to external code. The logic is separated into its own method to encapsulate access to the internal representation (_valid_algs) and to guarantee that callers receive a snapshot (a new list) rather than a reference to the internal collection.

## Args:
    None

## Returns:
    list[str]: A newly allocated list of algorithm identifier strings present in self._valid_algs at the time of the call.
    - If no algorithms are configured, an empty list is returned.
    - The order of elements is not defined (self._valid_algs is a set), so callers must not rely on any ordering.

## Raises:
    None under normal usage when the PyJWS instance has been constructed via its __init__ (which initializes self._valid_algs). The method body itself does not raise any exceptions.

## State Changes:
    Attributes READ:
        - self._valid_algs
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The PyJWS instance should have been initialized by PyJWS.__init__, which sets self._valid_algs to a set of algorithm name strings.
    Postconditions:
        - The PyJWS instance is unchanged.
        - The returned value is a shallow copy (list) containing the same strings that were in self._valid_algs at call time.

## Side Effects:
    - None (no I/O, no external calls, no mutation of self or other objects).

## Implementation notes:
    - Implement by returning list(self._valid_algs).
    - Ensure the returned list is a new object so callers cannot mutate the internal set via the returned value.
    - Do not sort or alter elements; preserve the snapshot semantics and unspecified ordering.

### `jwt.api_jws.PyJWS.get_algorithm_by_name` · *method*

## Summary:
Lookup and return the Algorithm implementation registered for the given algorithm identifier; does not modify the PyJWS instance.

## Description:
This method centralizes algorithm lookup for both signing and verification flows. Known callers include:
- encode(): called during JWT encoding to obtain the Algorithm used to prepare keys and sign the message.
- _verify_signature(): called during JWT verification to obtain the Algorithm used to prepare keys and verify the signature.

It exists as a dedicated method to:
- Keep algorithm lookup and the special handling for unavailable cryptography in one place instead of duplicating that logic in encode and verification code paths.
- Provide a single point to register/unregister algorithms (via register_algorithm/unregister_algorithm) and look them up consistently.

## Args:
    alg_name (str): The algorithm identifier (e.g., "HS256", "RS256").
        - Required. No default.
        - Expected to be a hashable string that is present in self._algorithms.
        - If alg_name is not hashable (e.g., a list), a TypeError from dict lookup will propagate.

## Returns:
    Algorithm: The Algorithm object previously registered under alg_name.
        - This is the object stored in the instance dict self._algorithms[alg_name].
        - There is no alternate "None" return; the method either returns an Algorithm instance or raises.

## Raises:
    NotImplementedError:
        - If alg_name is not a key in self._algorithms, this method raises NotImplementedError.
        - If the global flag has_crypto is False and alg_name is one that requires the cryptography dependency (alg_name in requires_cryptography),
          the raised NotImplementedError uses the message:
            "Algorithm '<alg_name>' could not be found. Do you have cryptography installed?"
        - Otherwise, the raised NotImplementedError uses the message:
            "Algorithm not supported"
        - The original KeyError from attempting to index the dict is chained as the __cause__ (raised from the KeyError).

    TypeError:
        - If alg_name is not hashable (e.g., a list), attempting to use it as a dict key will raise TypeError; this is not caught by this method and will propagate.

## State Changes:
    Attributes READ:
        - self._algorithms (dict[str, Algorithm]) — used to look up the requested algorithm.
    Attributes WRITTEN:
        - None — this method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - The PyJWS instance must have been initialized so that self._algorithms is a mapping of algorithm names to Algorithm instances (this is set in __init__ by get_default_algorithms and affected by register_algorithm/unregister_algorithm).
        - alg_name should normally be a string matching one of the registered algorithm identifiers.

    Postconditions:
        - If the method returns normally, it returns the Algorithm instance registered under alg_name and the PyJWS instance remains unchanged.
        - If the method raises NotImplementedError or TypeError, no mutation of self occurs.

## Side Effects:
    - None: this method performs no I/O, network access, or external service calls.
    - It reads the module-level flags has_crypto and requires_cryptography to decide on the error message when an algorithm is missing.

### `jwt.api_jws.PyJWS.encode` · *method*

## Summary:
Serialize the provided payload and headers into the JWS compact format, sign the assembled signing input with the selected algorithm, and return the UTF-8 compact JWS string. This method does not mutate the PyJWS instance.

## Description:
This method is the low-level JWS (compact serialization) constructor used when issuing signed tokens. Typical callers:
- Application code that needs to create a signed JWS/JWT for distribution.
- Higher-level library convenience wrappers that construct tokens and forward to this method.

Lifecycle/context:
- Invoked during token issuance: it composes the JWS header, encodes header and payload (or leaves the payload detached), computes the signature over header and payload segments, and returns the compact (dot-separated) representation.
- It is implemented as a separate method to centralize header normalization/validation, base64url encoding behavior, support for detached payloads (RFC 7797-style b64:false), and algorithm dispatch (selection + signing) in one place.

Why separate:
- Encapsulates multiple responsibilities (header validation/serialization, base64url encoding, algorithm lookup and signing) that are reused together and which must remain consistent across callers.
- Keeps higher-level APIs simple by exposing a single method for producing a signed compact JWS.

## Args:
    payload (bytes): Raw payload bytes. If is_payload_detached is False (default), these bytes will be base64url-encoded and used as the middle segment. If is_payload_detached is True, the bytes are treated as the detached payload (kept out of the returned compact string).
    key (AllowedPrivateKeys | str | bytes): Private key material (or key identifier) used for signing. The exact accepted types and normalization are delegated to the chosen Algorithm implementation (alg_obj.prepare_key).
    algorithm (str | None, optional): Algorithm identifier to use (default "HS256"). If None, the algorithm name used in the header becomes "none". If headers contains an "alg" entry, that header value takes precedence over this argument.
    headers (dict[str, Any] | None, optional): Optional header claims to merge into the produced header. If present:
        - headers["alg"] overrides the algorithm argument.
        - headers["b64"] when explicitly False enables detached payload mode (is_payload_detached will be set True).
        - headers are validated via self._validate_headers(headers) before being merged; invalid header values will raise.
    json_encoder (type[json.JSONEncoder] | None, optional): Custom JSONEncoder class passed through to json.dumps when serializing the header. Default None.
    is_payload_detached (bool, optional): If True, produce a compact serialization with an empty payload segment and set header["b64"]=False. Default False.
    sort_headers (bool, optional): If True (default), header JSON object will be serialized with sorted keys (json.dumps sort_keys=True), producing a deterministic header representation.

## Returns:
    str: A UTF-8 string containing the JWS compact serialization in the form "<base64url(header)>.<base64url(payload)|''>.<base64url(signature)>".
        - Normal case (is_payload_detached is False): all three segments are base64url-encoded bytes joined by '.' and returned as a UTF-8 decoded string.
        - Detached payload (is_payload_detached is True or headers specify b64=False): the returned compact string contains an empty payload segment (two dots with nothing between them); the original payload bytes are not included in the compact string.

## Raises:
    NotImplementedError:
        - Raised by self.get_algorithm_by_name(algorithm_) if the requested algorithm is not registered or not supported. This propagates directly from get_algorithm_by_name.
    InvalidTokenError:
        - Raised by self._validate_headers(headers) (via _validate_kid) when a header parameter violates header validation rules (for example, "kid" is not a string).
    TypeError or ValueError:
        - May be raised by json.dumps(header, ...) if the header contains objects that are not JSON-serializable with the provided json_encoder.
    Any exception raised by alg_obj.prepare_key(key):
        - prepare_key is implementation-specific (Algorithm implementations may raise ValueError, TypeError, or other exceptions for invalid key material); such exceptions propagate out of this method.
    Any exception raised by alg_obj.sign(signing_input, prepared_key):
        - sign is implementation-specific and may raise for invalid inputs or runtime errors in the cryptographic backend.

(Note: this method itself does not explicitly catch these exceptions; they originate from helper calls and are surfaced to the caller.)

## State Changes:
Attributes READ:
    self.header_typ - used as the default "typ" header value when constructing the header dictionary.
    self._algorithms and self._valid_algs - indirectly read by self.get_algorithm_by_name(algorithm_) when resolving the Algorithm implementation.
    (Indirectly) any internal checks performed by self._validate_headers which may read or call validation helpers.

Attributes WRITTEN:
    None. This method does not modify any PyJWS instance attributes.

## Constraints:
Preconditions:
    - payload must be bytes. Passing other types will not be accepted by this method (the code assumes payload is bytes and will pass it to base64url_encode or include it raw when detached).
    - key must be a value acceptable to the selected Algorithm implementation; validation/normalization is performed by alg_obj.prepare_key.
    - headers, if provided, must be a mapping/dict-like object; header values must be JSON-serializable (unless a custom json_encoder can handle them).

Postconditions:
    - The returned string is a compact JWS (three dot-separated UTF-8 segments) except when is_payload_detached is True, in which case the middle segment is empty.
    - The header included in the returned token reflects:
        * "alg" set to algorithm_ (either the algorithm arg or headers["alg"] if provided),
        * "typ" equal to self.header_typ unless a falsy typ was provided (in which case the "typ" entry is omitted),
        * "b64": False if is_payload_detached is True (or headers explicitly set b64=False).
    - No attributes on self are modified.

## Side Effects:
    - Calls into the selected Algorithm implementation (alg_obj.prepare_key and alg_obj.sign), which will invoke cryptographic operations in-process (hashing, HMAC, asymmetric signing). These operations may depend on external cryptography libraries (and may raise errors if such libraries are missing or key material is invalid).
    - No file I/O, network I/O, or other external side effects are performed by this method itself.

### `jwt.api_jws.PyJWS.decode_complete` · *method*

## Summary:
Decode and (optionally) verify a JWS token, returning the raw payload, protected header, and signature without transforming the payload; does not modify the object state.

## Description:
Known callers and usage context:
- PyJWS.decode calls this method and returns only the payload portion. decode_complete is the underlying implementation used during the token-decoding stage of the JWS/JWT processing pipeline.
- External users may call decode_complete directly when they require the full tuple of (payload, header, signature) rather than just the payload.

Why this is a separate method:
- Provides a single, reusable implementation that returns all low-level components (payload, header, signature), enabling both a simple decode() wrapper (which returns only payload) and direct callers that need header or signature.
- Keeps token parsing and signature verification responsibilities separated from higher-level transformations (e.g., JSON decoding of payload), improving testability and reuse.

## Args:
    jwt (str | bytes):
        The JWS compact-serialized token to decode. If a str is provided it will be encoded as UTF-8; if the value is not bytes (after trying to encode a str) a DecodeError is raised by the loader.
    key (AllowedPublicKeys | str | bytes, optional):
        Public key material (format depends on configured algorithms) used for signature verification. Defaults to an empty string (no key). This value is forwarded to algorithm handlers' prepare/verify functions.
    algorithms (list[str] | None, optional):
        Whitelist of allowed algorithm names (e.g., ["RS256", "HS256"]). If signature verification is enabled (see options), this argument must be provided; otherwise DecodeError is raised. If provided, the token's "alg" header must be present in this list.
    options (dict[str, Any] | None, optional):
        Per-call options merged with self.options. Recognized option:
            "verify_signature" (bool) — when True (default) the method will validate the signature; when False signature verification is skipped.
        If None, an empty dict is used. Any unsupported/extra kwargs passed via **kwargs produce a deprecation warning (see below).
    detached_payload (bytes | None, optional):
        When the token header contains "b64": False (indicating a detached payload), caller must pass the raw detached payload bytes here. If header.b64 is False and detached_payload is None, a DecodeError is raised.
    **kwargs:
        Deprecated. If any extra keyword arguments are passed, a RemovedInPyjwt3Warning deprecation warning is issued listing the unsupported keys.

## Returns:
    dict[str, Any]:
        A dictionary with three keys:
            "payload" (bytes): The raw payload bytes. For a normal (non-detached) token this is the result of base64url decoding the payload segment; when header["b64"] is False and detached_payload is supplied, payload is detached_payload.
            "header" (dict[str, Any]): The parsed JOSE header as a dict (JSON object).
            "signature" (bytes): The raw signature bytes (result of base64url decoding the final JWS segment).
        Note: payload is returned as raw bytes — this method does not JSON-decode or otherwise interpret the payload.

## Raises:
    DecodeError:
        - If verify_signature is True and algorithms argument is not provided: a DecodeError is raised stating algorithms must be provided.
        - If jwt is not a str or bytes (or not convertible to bytes via UTF-8 encoding): raised indirectly by the loader.
        - If the compact serialization does not have three segments or cannot be split correctly: "Not enough segments".
        - If header, payload, or signature segments fail base64url decoding (padding/format errors): "Invalid header/payload/crypto padding".
        - If header JSON is not valid or not a JSON object: "Invalid header string" or "Invalid header string: must be a json object".
        - If header["b64"] is False and detached_payload is not provided: a DecodeError stating detached_payload is required.
    InvalidAlgorithmError:
        - Raised indirectly from _verify_signature when:
            * header lacks "alg" or
            * header["alg"] is not in the allowed algorithms (either because it's falsy or not in the supplied algorithms list) or
            * the algorithm handler cannot be found / is not implemented.
    InvalidSignatureError:
        - Raised by _verify_signature when the algorithm's verify(...) returns False (signature did not match).
    Note: Many of the specific decoding/parsing errors originate in the internal _load() method; callers should expect DecodeError for malformed tokens.

## State Changes:
Attributes READ:
    - self.options: read to obtain default per-instance options which are merged with the options argument (specifically the "verify_signature" flag).
    - self._algorithms (indirectly): read by _verify_signature / get_algorithm_by_name when resolving the algorithm handler during signature verification.
Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.options must exist and be a mapping that includes a boolean value for "verify_signature" (this is established in PyJWS.__init__).
    - If verify_signature is True (default), the caller MUST provide the algorithms argument (non-empty list of allowed alg names).
    - jwt must be a str or bytes (if str it must be UTF-8 encodable). The compact JWS serialization must have the expected dot-separated segments.
    - If the JOSE header contains "b64": False, caller MUST supply detached_payload as bytes.

Postconditions:
    - Returns a dict containing the raw payload bytes, parsed header dict, and raw signature bytes.
    - No changes are made to the PyJWS instance state.
    - If verify_signature was True, either signature verification succeeded (no exception) or an InvalidAlgorithmError / InvalidSignatureError was raised.

## Side Effects:
    - Emits a RemovedInPyjwt3Warning via warnings.warn if extra **kwargs are supplied (lists unsupported keys).
    - Calls internal helpers that perform:
        * base64url decoding and JSON parsing (CPU and memory work; no network I/O).
        * Algorithm handler lookup and cryptographic verification via algorithm implementations (may perform CPU-bound crypto operations).
    - May raise exceptions described above; does not perform any I/O (file, network) nor mutate external objects.

### `jwt.api_jws.PyJWS.decode` · *method*

## Summary:
Returns the decoded JWS payload (raw bytes) by delegating full parsing and verification to the lower-level decode_complete method.

## Description:
This method is the convenience API for callers who only need the message payload of a JWS/JWT and do not require the header or signature. It performs a lightweight check for deprecated keyword arguments, forwards all parameters to decode_complete, and returns the "payload" field from decode_complete's result.

Known callers / usage contexts:
- Library consumers who want to decode and (optionally) verify a compact JWS/JWT and only need the payload.
- Typically invoked during the token validation/consumption stage of an authentication/authorization pipeline, immediately after receiving a token string from a client or another service.

Why this is a separate method:
- decode_complete returns a dict with payload, header and signature; decode is a convenience wrapper that exposes the most common use-case (payload-only) while leaving the more detailed decode_complete API for callers that need header or signature information. Keeping this wrapper avoids duplicating post-processing logic and centralizes warnings about deprecated kwargs.

## Args:
    jwt (str | bytes):
        The compact JWS/JWT token to decode. A str will be encoded to UTF-8 before parsing (this conversion happens in the delegated _load method).
    key (AllowedPublicKeys | str | bytes, optional):
        Verification key or key material to use for signature verification if enabled. Defaults to an empty string.
    algorithms (list[str] | None, optional):
        List of allowed algorithm names (e.g., ["HS256", "RS256"]). When signature verification is enabled, this must be provided (see Preconditions). Defaults to None.
    options (dict[str, Any] | None, optional):
        Per-call options merged with the PyJWS instance options. Supported option used by decode/decode_complete: "verify_signature" (bool). Defaults to None.
    detached_payload (bytes | None, optional):
        When decoding a JWS whose header declares "b64": false (detached payload), pass the detached payload bytes here. Defaults to None.
    **kwargs:
        Any additional keyword arguments — currently unsupported and deprecated. If provided, a RemovedInPyjwt3Warning deprecation warning will be emitted listing the unsupported keys.

## Returns:
    bytes:
        The decoded payload as raw bytes (this is the "payload" value returned by decode_complete/_load). Typical callers will parse/interpret these bytes (for example, as JSON) after receiving them.

## Raises:
    DecodeError:
        - If the token structure is invalid (not enough segments) or header/payload/signature segments have invalid base64url encoding or invalid JSON header. These errors are raised by decode_complete/_load and will propagate.
        - If verify_signature is True and algorithms is not provided (decode_complete enforces this).
        - If header declares "b64": false but detached_payload is not supplied.
    InvalidAlgorithmError:
        - If the token header lacks an "alg" value or if the algorithm is not in the provided algorithms allow-list or not supported by the library. Raised by _verify_signature and can propagate through decode.
    InvalidSignatureError:
        - If signature verification fails. Raised by _verify_signature and will propagate through decode.

Note: The method itself does not perform these checks; it delegates to decode_complete, so the same exceptions raised there will propagate unchanged.

## State Changes:
Attributes READ:
    - None directly. This method itself does not directly access or mutate instance attributes.
    - Implementation detail: the delegated decode_complete call reads instance state (e.g., self.options, registered algorithms) and may use them during verification.

Attributes WRITTEN:
    - None. This method does not modify self.

## Constraints:
Preconditions:
    - jwt must be a str or bytes. If not bytes, decode_complete/_load will raise DecodeError for invalid token type.
    - If signature verification is enabled (the merged options' "verify_signature" is True — the default), callers must provide a non-empty algorithms list argument; otherwise decode_complete raises DecodeError.
    - If the token header contains "b64": false, callers must supply detached_payload (bytes) or decode_complete will raise DecodeError.

Postconditions:
    - On success, returns the raw payload bytes (as produced by base64url decoding or the provided detached_payload).
    - The PyJWS instance is unchanged by this call.

## Side Effects:
    - Emits a RemovedInPyjwt3Warning via warnings.warn if any unsupported **kwargs are passed.
    - Delegates to decode_complete which:
        - Parses and base64url-decodes token segments,
        - May perform cryptographic operations and call into registered Algorithm implementations (which can use external crypto libraries),
        - May raise the exceptions listed above.
    - No file I/O or network I/O is performed by this method itself.

### `jwt.api_jws.PyJWS.get_unverified_header` · *method*

## Summary:
Return the decoded JWS/JWT header (JSON object) from a token without performing signature verification; does not modify the PyJWS instance.

## Description:
This method extracts and returns the header portion of a JWS/JWT token without verifying the token's signature. It is intended for callers that need to inspect header fields (for example, to determine the algorithm, key id, or whether the payload is detached) prior to or instead of full verification.

Known callers and context:
- Primarily intended for external library users who want to inspect token headers quickly.
- Not used elsewhere inside this class for verification flows (internal flows use decode/decode_complete which call _load and _verify_signature).
- Typical lifecycle stage: an early inspection step in token processing and diagnostic workflows, or when a client needs metadata (e.g., "alg" or "kid") before selecting a verification key.

Why this is a separate method:
- Offers a safe, explicit API to parse headers without performing signature checks.
- Keeps header parsing logic single-responsibility and avoids duplicating _load/_validate_headers logic in multiple places.

## Args:
    jwt (str | bytes): The compact JWS/JWT token to parse. Accepts a str (which will be UTF-8 encoded) or bytes. Must be the compact serialization with three segments separated by b"." (header.payload.signature). 

## Returns:
    dict[str, Any]: The decoded header as a Python dict (the JSON object parsed from the header segment).
    - The returned dict is the parsed header object produced by json.loads(header_data).
    - The method returns the header exactly as parsed (no signature verification is implied).
    - Edge cases: if returned, header is guaranteed to be a dict (otherwise _load raises).

## Raises:
The method delegates parsing to _load and validation to _validate_headers, so it may raise the following exceptions exactly as produced by those helpers:

    DecodeError: Raised by _load under these conditions:
        - If jwt is not a str or bytes:
            message: "Invalid token type. Token must be a <class 'bytes'>"
        - If the token does not contain the expected segments:
            message: "Not enough segments"
        - If the header segment is not valid Base64URL (TypeError or binascii.Error):
            message: "Invalid header padding"
        - If header JSON cannot be parsed:
            message: "Invalid header string: <orig_exception_message>"
        - If the parsed header is not a JSON object (dict):
            message: "Invalid header string: must be a json object"
        - If payload segment Base64URL is invalid:
            message: "Invalid payload padding"
        - If signature segment Base64URL is invalid:
            message: "Invalid crypto padding"

    InvalidTokenError: Raised by _validate_headers if header contains a "kid" value that is not a string:
        message: "Key ID header parameter must be a string"

No other exceptions are raised by this method itself; exceptions are propagated from the called helpers.

## State Changes:
Attributes READ:
    - None (the method does not read or depend on any self.<attribute> values).

Attributes WRITTEN:
    - None (the method does not modify any attributes on self).

## Constraints:
Preconditions:
    - jwt must be either a str (will be encoded to UTF-8) or bytes.
    - jwt must be the JWS/JWT compact serialization with three dot-separated segments.
    - The header segment must be base64url-encoded JSON that decodes to a JSON object (dict).

Postconditions:
    - If the call returns normally, the returned value is a dict representing the header, and the PyJWS instance is unchanged.
    - No signature verification has been performed; the header may come from an untrusted source.

## Side Effects:
    - No network I/O or filesystem I/O is performed.
    - No mutation of external objects occurs.
    - The method may raise exceptions described above; callers should treat returned headers as untrusted until signature verification is performed separately.

### `jwt.api_jws.PyJWS._load` · *method*

## Summary:
Parse a JWS compact serialization token (JWT/JWS) into its decoded payload, the original signing input bytes, the JSON header as a Python dict, and the decoded signature bytes; does not verify the signature or mutate object state.

## Description:
This method is the parser/extractor used early in the decode pipeline. Known callers:
- PyJWS.decode_complete(...) — called during full decoding and prior to signature verification and detached-payload handling.
- PyJWS.decode(...) — indirectly called (via decode_complete) to obtain the payload.
- PyJWS.get_unverified_header(...) — called to obtain and validate the header without verifying the signature.

When invoked, the method:
- Accepts a compact-serialization JWS token as text (str) or raw bytes,
- Ensures the input is bytes (encodes str as UTF-8),
- Splits the token into segments (header, payload, signature) using dot separators,
- Base64url-decodes the header and payload segments and JSON-deserializes the header,
- Base64url-decodes the signature segment,
- Returns (payload_bytes, signing_input_bytes, header_dict, signature_bytes).

This logic is factored into its own method so the token parsing/decoding is centralized and can be reused by multiple public APIs (full decode, header-only retrieval, detached-payload handling) without duplicating the split/base64/JSON parsing logic. It intentionally does not perform signature verification or header validation beyond basic JSON object shape — those responsibilities are implemented elsewhere.

## Args:
    jwt (str | bytes):
        The compact JWS token to parse. If a str, it will be encoded to bytes with UTF-8.
        Allowed values: a bytes object representing the token, or a str. Any other type raises DecodeError.

## Returns:
    tuple[bytes, bytes, dict[str, Any], bytes]:
        - payload (bytes): The base64url-decoded payload segment as raw bytes. May be empty bytes if the token's payload segment is empty.
        - signing_input (bytes): The signing input bytes (the original header and payload segments joined by b'.'). This is the exact bytes used for signature computation/verification and is NOT altered by this method.
        - header (dict[str, Any]): The header parsed from the base64url-decoded JSON header segment. Guaranteed to be a Python dict on success.
        - signature (bytes): The base64url-decoded signature bytes (decoded from the last segment).

## Raises:
    DecodeError("Invalid token type. Token must be a <class 'bytes'>"):
        If the provided jwt is not a str or bytes (after the optional UTF-8 encoding step).
    DecodeError("Not enough segments"):
        If the token cannot be split into header, payload and signature segments (i.e., splitting by dots fails to yield the required parts).
    DecodeError("Invalid header padding"):
        If base64url decoding of the header segment fails due to TypeError or binascii.Error (invalid base64url input/padding).
    DecodeError("Invalid header string: <msg>"):
        If the header segment decodes to bytes that are not valid JSON; <msg> is the ValueError message returned by json.loads.
    DecodeError("Invalid header string: must be a json object"):
        If the decoded header JSON is valid JSON but not a JSON object (i.e., not decoded to a Python dict).
    DecodeError("Invalid payload padding"):
        If base64url decoding of the payload segment fails due to TypeError or binascii.Error.
    DecodeError("Invalid crypto padding"):
        If base64url decoding of the signature (crypto) segment fails due to TypeError or binascii.Error.

Note: The method converts low-level TypeError/binascii.Error and json.ValueError errors into the above DecodeError variants and preserves the original error as the __cause__.

## State Changes:
Attributes READ:
    - None (this method does not access or depend on instance attributes)

Attributes WRITTEN:
    - None (this method does not modify the PyJWS instance state)

## Constraints:
Preconditions:
    - If jwt is a str, it must be valid UTF-8 (since it will be encoded with "utf-8").
    - The token must be a compact serialization with at least two dot separators (header.payload.signature). The method expects the last dot to separate the signature from the signing input; the signing input must contain at least one dot to separate header and payload.
    - The header segment must be base64url-encoded JSON that decodes to a JSON object (mapping).
    - The payload and signature segments must be base64url-encoded bytes (or empty payload when supported by higher-level logic).

Postconditions:
    - On successful return, the header is a Python dict parsed from the JSON header segment.
    - The payload and signature are the base64url-decoded bytes of their respective segments.
    - signing_input is the original bytes of the header and payload segments joined by a single b'.' (suitable for passing to signature verification routines).

## Side Effects:
    - No I/O or external service interactions.
    - No mutation of external objects.
    - Calls utility functions base64url_decode and json.loads; any exceptions from these utilities are caught and translated into DecodeError variants as described above.

### `jwt.api_jws.PyJWS._verify_signature` · *method*

## Summary:
Verifies the cryptographic signature on a JWS signing input using the algorithm declared in the header; raises on any verification or algorithm errors. Does not modify object state.

## Description:
This method is invoked during the JWT/JWS decode pipeline to validate the signature after the token has been parsed and the signing input produced. Known callers:
- PyJWS.decode_complete — called when verify_signature is enabled to assert the token's integrity before returning the payload.
- (Indirect) PyJWS.decode calls decode_complete, so decode() -> decode_complete() -> _verify_signature when verification is requested.

This logic is extracted into its own method to separate concerns (parsing/loading vs. verification), to centralize algorithm lookup and verification logic, and to make unit testing and reuse of verification behavior straightforward.

## Args:
    signing_input (bytes):
        The byte sequence that was signed (typically the base64url-encoded header and payload joined by b'.'). Must be a bytes object.
    header (dict[str, Any]):
        The decoded header object extracted from the JWT/JWS. Must be a dict containing an 'alg' entry (algorithm identifier).
    signature (bytes):
        The raw signature bytes obtained by base64url-decoding the final segment of the token.
    key (AllowedPublicKeys | str | bytes, optional):
        The public key, key-like object, or key identifier used to verify the signature. Defaults to an empty string; interpretation is delegated to the selected Algorithm.prepare_key implementation.
    algorithms (list[str] | None, optional):
        An allowlist of algorithm names that are permitted for verification. If provided, the header's 'alg' must be present in this list. If None, no additional allowlist check is applied beyond the algorithm registry.

## Returns:
    None
    On success the method returns None. Success means no exception was raised and the signature was accepted by the underlying Algorithm.verify implementation.

## Raises:
    InvalidAlgorithmError:
        - If the header does not contain an 'alg' key (missing algorithm).
        - If the header's 'alg' value is falsy (e.g., empty string) or if `algorithms` is provided and the header's alg is not contained in that list.
        - If get_algorithm_by_name does not find a matching algorithm (wraps NotImplementedError from algorithm lookup) — reported as "Algorithm not supported".
    InvalidSignatureError:
        - If the algorithm object's verify(signing_input, prepared_key, signature) returns a falsy value indicating signature validation failed.
    (Propagated exceptions from algorithm implementations)
        - prepare_key or verify implementations may raise other exceptions (e.g., TypeError or library-specific errors); those are not wrapped here and will propagate to the caller.

## State Changes:
Attributes READ:
    - self._algorithms (indirectly) — accessed via self.get_algorithm_by_name to resolve the Algorithm object.
    - No other self.<attr> fields are read directly by this method.
Attributes WRITTEN:
    - None — this method does not modify attributes on self.

## Constraints:
Preconditions:
    - signing_input must be bytes.
    - header must be a dict and must include an 'alg' key with a non-empty value.
    - signature must be bytes (result of base64url_decode of the crypto segment).
    - If `algorithms` is provided, it must be an iterable of algorithm identifiers (strings); the header 'alg' must be one of them.

Postconditions:
    - If the method returns normally (no exception), the signature has been validated by the resolved Algorithm.verify call using a prepared key derived from `key`.
    - No attributes of self are changed by the method.

## Side Effects:
    - Calls self.get_algorithm_by_name(alg) to map the algorithm name to an Algorithm object (may raise NotImplementedError which is converted to InvalidAlgorithmError).
    - Calls Algorithm.prepare_key(key) on the resolved Algorithm object to adapt the provided key into the algorithm's expected form.
    - Calls Algorithm.verify(signing_input, prepared_key, signature) which performs the cryptographic verification. Those calls may invoke external cryptographic libraries (e.g., cryptography) depending on the Algorithm implementation.
    - No I/O (file, network) or mutation of external objects is performed by this method itself, although underlying Algorithm implementations may have their own side effects or exceptions.

### `jwt.api_jws.PyJWS._validate_headers` · *method*

## Summary:
Validate JWT header parameters minimally by checking the "kid" (Key ID) header when present; does not modify the object's state.

## Description:
This method performs a focused validation step for JWT headers: if the header object contains a "kid" key, the value is validated to ensure it is a string. It is called in at least two places within the PyJWS lifecycle:
- PyJWS.encode(...) — when user-supplied headers are merged into the outgoing JWT header and must be validated before encoding/signing.
- PyJWS.get_unverified_header(...) — when extracting headers from an existing token; headers are validated before being returned.

Having this logic in a dedicated method centralizes the small but important validation for the "kid" parameter (keeping encode() and header-extraction code concise and avoiding duplication), and isolates the specific validation rules so they can be extended consistently (for example, additional header checks) without changing call sites.

## Args:
    headers (dict[str, Any]):
        The decoded header object (JSON -> dict) that follows the JOSE/JWT header structure.
        Expected to be a mapping of string keys to arbitrary values; this method will only examine the "kid" key if present.

## Returns:
    None

## Raises:
    InvalidTokenError:
        Raised when the header contains a "kid" key whose value is not a string.
        Exact message raised by the underlying helper: "Key ID header parameter must be a string"

## State Changes:
    Attributes READ:
        None — the method does not read or depend on any PyJWS instance attributes.
    Attributes WRITTEN:
        None — the method does not modify any PyJWS instance attributes.

## Constraints:
    Preconditions:
        - The caller should pass a dictionary-like header (type hinted as dict[str, Any]).
        - The header follows JWT header semantics (optional "kid" key).
    Postconditions:
        - If the method returns normally, the header either does not contain "kid" or contains a "kid" whose value is a str.
        - No mutation of the header object is performed by this method.

## Side Effects:
    - No I/O, network access, or calls to external services.
    - May raise InvalidTokenError (see Raises) if validation fails.
    - Calls the helper method self._validate_kid(kid) to perform the type check for the "kid" value.

### `jwt.api_jws.PyJWS._validate_kid` · *method*

## Summary:
Checks that the provided JWS header "kid" (Key ID) value is a string; if not, raises InvalidTokenError. This validation does not modify the object's state.

## Description:
This method is intended to be called during processing and validation of JWS headers (for example, when decoding or verifying a JSON Web Signature) to enforce the type constraint on the "kid" header parameter. Typical callers are header-parsing or header-validation routines that examine token headers and ensure header parameter types are correct before selecting or retrieving keys.

This logic is factored into a short, dedicated method to centralize the type check and the resulting error message (so the behavior is consistent across different call sites) and to make it straightforward to override in subclasses if different semantics are required.

## Args:
    kid (Any): The extracted "kid" header value from a JWS header. Any Python object may be passed in, but only instances of str are considered valid.

## Returns:
    None: The method returns None on success (i.e., when kid is a str). No value is produced or propagated.

## Raises:
    InvalidTokenError: Raised when the provided kid is not an instance of str.
        Exact raised message: "Key ID header parameter must be a string"

## State Changes:
    Attributes READ:
        None — the method does not read any self.<attr> fields.
    Attributes WRITTEN:
        None — the method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - A value for kid (possibly None) has been extracted from the token header and is being validated.
        - No special setup on self is required; the method's behavior depends solely on the runtime type of kid.

    Postconditions:
        - If the method returns normally, the provided kid is guaranteed to be an instance of str.
        - If the provided kid is not a str, the method will not return; it raises InvalidTokenError.

## Side Effects:
    - None. The method performs no I/O, makes no external service calls, and does not mutate objects outside of its scope.

