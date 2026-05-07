# `api_jwt.py`

## `jwt.api_jwt.PyJWT` · *class*

*No documentation generated.*

### `jwt.api_jwt.PyJWT.__init__` · *method*

## Summary:
Initializes the PyJWT instance's runtime options map by merging the canonical default verification options with any user-supplied overrides, and stores the result on the instance.

## Description:
Known callers and context:
- Called when a PyJWT object is instantiated (e.g., PyJWT()). This occurs during the object's construction lifecycle before the instance is used for encoding, decoding, or verification operations.
- Library consumers, tests, or higher-level helpers that need a configured JWT helper will invoke this as part of creating a PyJWT instance.

Why this logic is its own method:
- Keeps instance construction concise while centralizing default option provision in _get_default_options. This separation makes defaults discoverable, testable, and overrideable without duplicating default values inside __init__.

## Args:
    options (dict[str, Any] | None): Optional mapping of option names to values that will override the defaults.
        - Allowed keys: any string keys used by the library (common keys provided by _get_default_options include "verify_signature", "verify_exp", "verify_nbf", "verify_iat", "verify_aud", "verify_iss", and "require").
        - Default: None — when None, an empty dict is used (no overrides).
        - Notes: The function expects a mapping (a dict-like object) for options so it can be merged via mapping unpacking.

## Returns:
    None

## Raises:
    TypeError: If options is provided but is not a mapping suitable for dictionary unpacking (e.g., passing a non-mapping value). This arises from the {**defaults, **options} unpack operation.
    Any exception raised by self._get_default_options (none in the current implementation) will propagate.

## State Changes:
Attributes READ:
    - None (this method does not read any self.<attr> instance fields).

Attributes WRITTEN:
    - self.options (dict[str, Any]): Set to a newly created dict produced by merging the defaults and the provided options. The resulting mapping is stored on the instance and will be used by subsequent methods.

Additional internal calls:
    - Calls self._get_default_options() to obtain the base options mapping before merging.

## Constraints:
Preconditions:
    - The caller may pass None or a dict-like mapping. If an options value that is not a mapping is passed, a TypeError will occur during merging.
    - No other preconditions on the instance are required.

Postconditions:
    - After return, self.options exists and is a dict[str, Any] containing all keys from the default options, with any keys present in the provided options overriding the defaults.
    - The "require" default (an empty list returned by _get_default_options) will be present unless overridden by the provided options; the list produced by _get_default_options is a fresh list per call (mutating that list later will not affect other instances created earlier/later).
    - The instance is ready to be used by other PyJWT methods that consult self.options for verification behavior.

## Side Effects:
    - No I/O or external service interaction.
    - Does not mutate the caller-provided options mapping; it produces a new merged dict and assigns it to self.options.

### `jwt.api_jwt.PyJWT._get_default_options` · *method*

## Summary:
Returns a fresh mapping of the JWT default verification options used to seed an instance's options state; enables all verification checks by default and provides an empty list for required claims.

## Description:
Known callers and context:
- PyJWT.__init__: Called during object initialization to build the instance options map via merging this defaults map with user-supplied options (self.options = {**self._get_default_options(), **options}). This occurs in the object's construction lifecycle so every PyJWT instance starts with these defaults unless overridden.
- Callers may also invoke this as PyJWT._get_default_options() (it's a static helper) when they need the canonical default options map without instantiating the class.

Why this logic is a separate method:
- Centralizes the canonical default option set so tests and subclasses can override or inspect defaults in a single place.
- Keeps __init__ concise and makes behavior explicit (defaults are not inlined in multiple places).
- Ensures consistency across code that needs the same baseline options.

## Args:
None.

## Returns:
dict[str, bool | list[str]]
- Structure and content:
    - "verify_signature": True
    - "verify_exp": True
    - "verify_nbf": True
    - "verify_iat": True
    - "verify_aud": True
    - "verify_iss": True
    - "require": []  (an empty list)
- Notes:
    - Each call returns a newly constructed dict. The "require" value is a newly created empty list on every call (i.e., callers may mutate the returned list without affecting other callers).
    - Types follow the annotation: boolean flags for verification keys and a list[str] for "require".

## Raises:
None. The function is pure and does not raise exceptions.

## State Changes:
Attributes READ:
- None (method is a static helper and does not access instance attributes).

Attributes WRITTEN:
- None (method does not modify self or external state).

## Constraints:
Preconditions:
- None. Can be safely called without any instance or external state.

Postconditions:
- The caller receives a dict containing the seven keys listed above with the specified default values.
- When merged into an instance's options (e.g., {**self._get_default_options(), **options}), the returned mapping guarantees presence of all verification flags and the "require" key unless explicitly overridden by the caller's merge.

## Side Effects:
- None. No I/O, no external calls, and no mutation of objects outside the returned dict.

### `jwt.api_jwt.PyJWT.encode` · *method*

## Summary:
Encodes a JSON-serializable payload into a compact signed JWT string by normalizing time claims, JSON-encoding the payload, and delegating to the JWS encoder.

## Description:
This public instance method is the PyJWT-level entry point used to create (sign/encode) a JWT from a Python mapping. Typical callers are:
- Library consumers who call the PyJWT object directly when they need to generate JWTs.
- Higher-level convenience wrappers (for example, a module-level jwt.encode function that obtains a PyJWT instance and forwards arguments).

It is separated into its own method because it:
- Performs argument validation and payload normalization (notably converting datetime claims to epoch seconds).
- Encapsulates the JSON payload encoding step so that the low-level JWS encoder (api_jws.encode) receives a canonical byte payload.
- Keeps signing/encoding concerns (api_jws) distinct from JWT payload preparation.

Lifecycle/context: invoked when an application or library component needs a compact serialized JWT (string) to send to clients or another system. The method does not perform claim validation (that occurs during decode path); it only prepares and encodes the payload for signing.

## Args:
    payload (dict[str, Any]):
        The JWT claims object. Must be a dict (JSON object). A shallow copy is made internally so the original dict is not directly overwritten by the method's own modifications.
    key (AllowedPrivateKeys | str | bytes):
        The private key or secret used to sign the token. The concrete accepted forms depend on the configured signing algorithms (see algorithms.AllowedPrivateKeys).
    algorithm (str | None, optional): Default "HS256"
        The signing algorithm name or None. Passed through to api_jws.encode unchanged.
    headers (dict[str, Any] | None, optional): Default None
        Optional JOSE header values to include in the token. Passed through to api_jws.encode.
    json_encoder (type[json.JSONEncoder] | None, optional): Default None
        Custom JSON encoder class to use when serializing the payload. Passed to the internal payload encoder and forwarded to api_jws.encode.
    sort_headers (bool, optional): Default True
        If True, headers may be sorted by the underlying JWS encoder; forwarded to api_jws.encode.

## Returns:
    str:
        A compact JWT (JWS) string resulting from api_jws.encode. This method returns whatever api_jws.encode returns, which is intended to be the serialized JWT token ready for transport/storage.

## Raises:
    TypeError:
        If payload is not a dict, raises TypeError with message:
        "Expecting a dict object, as JWT only supports JSON objects as payloads."
    TypeError (propagated):
        If json.dumps fails because the payload contains non-serializable objects, the TypeError from json.dumps will propagate.
    Any exception raised by api_jws.encode:
        Signing/encoding errors (e.g., unsupported algorithm, invalid key) raised by the underlying api_jws.encode are propagated upward.

## State Changes:
Attributes READ:
    - self._encode_payload (calls the instance method to serialize the payload)
Attributes WRITTEN:
    - None (the method does not modify instance attributes)

Notes:
    - The method creates a shallow copy of the provided payload (payload.copy()) and may mutate that copy (e.g., replacing datetime claims), but it does not mutate the caller's original mapping reference. Nested mutable values are not deep-copied.

## Constraints:
Preconditions:
    - payload must be a dict mapping string keys to JSON-serializable values.
    - If algorithm requires a specific key type, callers must provide a key of an allowed type (enforced by api_jws.encode or signing layer).
Postconditions:
    - Datetime objects in payload["exp"], payload["iat"], and payload["nbf"] (if present) are converted into integer seconds since the epoch (UTC) using calendar.timegm(payload.utctimetuple()) before JSON serialization.
    - The returned value is the exact result of api_jws.encode when called with the JSON-encoded payload and forwarded parameters.
    - The original payload object passed by the caller remains intact at the top-level reference (because of the shallow copy).

## Side Effects:
    - Calls json.dumps via self._encode_payload to produce a UTF-8 encoded JSON byte string; this may raise serialization errors for unsupported types.
    - Delegates to api_jws.encode(json_payload, key, algorithm, headers, json_encoder, sort_headers=sort_headers), which performs the JWS signing/encoding. Any side effects or external interactions performed by api_jws.encode (e.g., using cryptographic backends) will occur and exceptions will propagate.

### `jwt.api_jwt.PyJWT._encode_payload` · *method*

## Summary:
Serialize the given payload dictionary to compact JSON and return its UTF-8 encoded bytes; does not modify the PyJWT instance or the input payload.

## Description:
This helper converts a JSON-serializable payload mapping into a compact JSON byte sequence (no extra whitespace) which is then used by the JWS encoding/signing step. Known caller:
- PyJWT.encode — invoked during the encode pipeline to produce the JSON payload bytes immediately prior to calling the JWS encoder/signing routine.

The logic is factored out into its own method to centralize JSON serialization options (compact separators and optional custom encoder), make the serialization behavior overrideable in subclasses or tests, and to keep the encode() method focused on high-level signing flow. The headers parameter is accepted for API symmetry with other encoder methods but is intentionally unused by this implementation.

## Args:
    payload (dict[str, Any]):
        A mapping representing the JWT claims. Must be JSON-serializable (values must be types supported by json.dumps or handled by the provided json_encoder).
    headers (dict[str, Any] | None, optional):
        Present for API compatibility. This implementation does not read or use headers; callers may pass None. Default: None.
    json_encoder (type[json.JSONEncoder] | None, optional):
        Optional JSON encoder class to pass to json.dumps via the cls parameter. If provided, it must be a JSONEncoder subclass or a compatible class that json.dumps accepts. Default: None (use the stdlib JSON encoder).

## Returns:
    bytes:
        UTF-8 encoding of the compact JSON representation of payload. Example values: b"{}", b'{"sub":"123"}', etc. For an empty mapping the result is b"{}". The returned bytes are produced by applying json.dumps(..., separators=(",", ":")) and then .encode("utf-8").

## Raises:
    TypeError (propagated from json.dumps):
        If payload contains objects that are not JSON serializable and the provided json_encoder does not handle them, json.dumps will raise TypeError which is propagated to the caller.
    Any other exception raised by json.dumps or by the json_encoder:
        Errors raised by the encoder class or json.dumps (for example invalid encoder types) are not caught here and will propagate.

## State Changes:
    Attributes READ:
        None — this method does not read any self.<attr> fields.
    Attributes WRITTEN:
        None — this method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - The caller should provide a mapping of claims (payload) appropriate for JSON serialization.
        - If a custom json_encoder is provided, it must be a class acceptable to json.dumps(cls=...).
    Postconditions:
        - The returned value is a bytes object containing a compact JSON representation of the provided payload.
        - The input payload mapping and the PyJWT instance remain unchanged.

## Side Effects:
    - No I/O (no file, network, or external resource access).
    - No mutation of objects outside the method (payload is not modified).
    - Uses only the stdlib json module and in-memory string/byte operations.

### `jwt.api_jwt.PyJWT.decode_complete` · *method*

## Summary:
Decode a compact JWT/JWS token into its full decoded structure, parse its JSON payload into a Python dict, and run claim validation according to the instance defaults merged with per-call options; returns the decoded mapping with the parsed payload substituted.

## Description:
This method performs the higher-level decode workflow: it delegates low-level parsing and (when enabled) cryptographic signature verification to api_jws.decode_complete, then parses the returned raw payload as JSON and validates standard JWT claims (exp, nbf, iat, aud, iss, and any claims listed in "require") according to merged verification options.

Known callers and context:
- PyJWT.decode calls this method internally and returns only decoded["payload"] to callers that want just the payload. decode_complete is used when callers need the entire decoded structure (headers, raw signature, etc.) along with the parsed payload.
- It is invoked during token processing/verification steps where application code needs to verify token integrity and claims before granting access or trusting embedded claims.

Why this is its own method:
- Cryptographic parsing/verification (api_jws) and application-level JSON parsing plus claim validation are separate concerns; keeping them separate clarifies responsibility and enables reuse (e.g., different JWS/JWT parsers can be plugged in while preserving claim validation logic).

## Args:
    jwt (str | bytes):
        The compact JWT/JWS token to decode.
    key (AllowedPublicKeys | str | bytes, optional):
        Public key(s) or key identifier(s) used for signature verification by the underlying api_jws. Defaults to "" (empty string).
    algorithms (list[str] | None, optional):
        Accepted signing algorithms (e.g. ["HS256", "RS256"]). Required when signature verification is enabled (see options). Defaults to None.
    options (dict[str, Any] | None, optional):
        Per-call verification options. A shallow copy is made internally (the passed-in dict is not mutated). Common keys:
            - verify_signature (bool): whether to verify signature. If not provided, defaults to True via setdefault on the local copy.
            - verify_exp, verify_nbf, verify_iat, verify_aud, verify_iss (bool): whether to validate the corresponding claim. If verify_signature is set to False locally, the method will set defaults of False for these verify_* flags on the local options copy.
            - require (list[str]): names of claims that must be present.
            - strict_aud (bool): controls strict audience matching behavior in _validate_aud.
    verify (bool | None, optional):
        Deprecated compatibility flag. If provided and different from options["verify_signature"], a DeprecationWarning is emitted. This parameter is ignored for behavior (it does not change verification).
    detached_payload (bytes | None, optional):
        Detached payload bytes for JWS where the payload is detached. Passed through to api_jws.decode_complete.
    audience (str | Iterable[str] | None, optional):
        Expected audience claim. Must be a string or an iterable of strings if provided. Validation behavior depends on options["verify_aud"] and strict_aud.
    issuer (str | None, optional):
        Expected issuer claim. If None, issuer validation is skipped unless options require the "iss" claim.
    leeway (float | timedelta, optional):
        Allowance (in seconds) for clock skew in time-based claim checks. A timedelta will be converted to total seconds. Defaults to 0.
    **kwargs (Any):
        Any additional keyword arguments: their presence triggers a RemovedInPyjwt3Warning and they are otherwise ignored.

## Returns:
    dict[str, Any]:
        The decoded token structure returned by api_jws.decode_complete, with the following guarantee:
        - The "payload" key is present and its value is a Python dict parsed from the token's JSON payload.
        - Other keys returned by api_jws.decode_complete (such as "header", "signature", etc.) are preserved.
    Edge cases:
        - If the raw payload is invalid JSON or does not parse to a JSON object, a DecodeError is raised.
        - If api_jws.decode_complete returns a mapping without a "payload" key, accessing decoded["payload"] will raise a KeyError which propagates to the caller (this method does not transform or wrap that KeyError).

## Raises:
    DecodeError:
        - If options["verify_signature"] is True but no algorithms list is provided (explicit check near the start of the method).
        - If the raw payload is not valid JSON or does not parse to a JSON object (raised by _decode_payload).
    KeyError:
        - If api_jws.decode_complete returns a mapping missing the "payload" key (raised when attempting decoded["payload"] inside _decode_payload).
    MissingRequiredClaimError:
        - If any name in merged_options["require"] is missing from the parsed payload (raised by _validate_required_claims).
    InvalidIssuedAtError:
        - If the iat claim cannot be converted to an integer (raised by _validate_iat).
    ImmatureSignatureError:
        - If iat or nbf indicates the token is not yet valid beyond allowed leeway (raised by _validate_iat or _validate_nbf).
    ExpiredSignatureError:
        - If exp indicates the token has expired beyond allowed leeway (raised by _validate_exp).
    InvalidAudienceError:
        - If audience validation fails due to missing claim, bad format, or value mismatch (raised by _validate_aud).
    InvalidIssuerError:
        - If issuer validation fails because the token's iss does not match the expected issuer (raised by _validate_iss).
    TypeError:
        - If audience is provided but is not a str or an Iterable (checked by _validate_claims).
    Other:
        - Exceptions raised by api_jws.decode_complete (for example, signature verification failures or token format errors) will propagate through this method.

## State Changes:
    Attributes READ:
        - self.options: instance default verification options are read and later merged with the per-call options.
        - self._decode_payload: invoked to parse the raw payload out of the api_jws response.
        - self._validate_claims: invoked to validate parsed claims using merged options, audience, issuer, and leeway.
    Attributes WRITTEN:
        - None. The method does not modify instance attributes. It mutates a local copy of the options dict and mutates the returned decoded dict by assigning decoded["payload"] = parsed_payload.

## Constraints:
    Preconditions:
        - If signature verification is left enabled (options["verify_signature"] True on the local options copy), the caller must supply a non-empty algorithms list or a DecodeError is raised.
        - api_jws.decode_complete must return a mapping that contains a "payload" entry holding the raw payload (bytes or str); otherwise a KeyError is raised.
        - The raw payload must be JSON that parses to a JSON object (top-level), otherwise _decode_payload raises DecodeError.
        - audience, if provided, must be a string or an iterable of strings; otherwise a TypeError is raised in _validate_claims.
    Postconditions:
        - On success, the returned dict is the original decoded mapping from api_jws.decode_complete with decoded["payload"] replaced by a Python dict representing the parsed JSON object.
        - All claim validations enabled by the merged options have been performed; if any check fails, the corresponding validation exception is raised and nothing is returned.

## Side Effects:
    - Emits a RemovedInPyjwt3Warning (via warnings.warn) if any unexpected extra keyword arguments are passed in **kwargs; the warning includes the unsupported kwarg names.
    - Emits a DeprecationWarning (via warnings.warn) if the deprecated verify argument is supplied and does not match options["verify_signature"].
    - Delegates to api_jws.decode_complete which may perform CPU-intensive cryptographic operations and raise verification-related exceptions; those effects and exceptions come from api_jws and propagate here.
    - No external I/O or network calls are performed by this method itself, and no instance attributes are mutated.

### `jwt.api_jwt.PyJWT._decode_payload` · *method*

## Summary:
Parse the JSON payload string from a decoded JWS/JWT structure and return it as a Python dict, validating that the payload is a JSON object; does not mutate the PyJWT instance.

## Description:
This method is invoked after the lower-level JWS decoding routine returns a "decoded" mapping whose "payload" entry is expected to be a JSON-encoded string (for example, in PyJWT.decode_complete). Known callers:
- PyJWT.decode_complete: calls this immediately after api_jws.decode_complete returns, to convert the returned decoded["payload"] JSON string into a dict before claim validation.
- Indirectly, PyJWT.decode calls decode_complete and therefore uses this logic as part of the decode pipeline.

Why this is a separate method:
- Encapsulates the responsibility of parsing and validating the payload JSON independently from signature / structure decoding and claim validation.
- Keeps decode_complete focused on orchestration (calling JWS decode, claim validation) while centralizing JSON payload parsing and its error-handling semantics here so other entry points can reuse identical behavior.

## Args:
    decoded (dict[str, Any]):
        A mapping produced by the lower-level JWS decode routine. MUST contain a "payload" key whose value is a JSON-encoded string (or other input accepted by json.loads) representing the JWT payload.

## Returns:
    dict[str, Any]:
        The parsed payload as a Python mapping (dict). Guaranteed to be a dict on successful return.

## Raises:
    DecodeError:
        - If json.loads raises a JSON decode error (subclass of ValueError). The raised DecodeError message wraps the original json error: "Invalid payload string: <original error>".
        - If the parsed JSON is not a mapping (i.e., not a JSON object), this raises DecodeError with message: "Invalid payload string: must be a json object".
    KeyError:
        - If the provided decoded mapping does not contain the "payload" key, a KeyError will be raised by decoded["payload"] (not caught by this method).
    TypeError:
        - If decoded["payload"] is of a type not acceptable to json.loads (e.g., an unsupported object), json.loads may raise TypeError which will propagate (not caught and rewrapped here).

## State Changes:
    Attributes READ:
        - None (this method does not read or depend on any self.<attr> attributes).
    Attributes WRITTEN:
        - None (this method does not modify self or external objects).

## Constraints:
    Preconditions:
        - decoded must be a mapping-like object and contain the "payload" key.
        - decoded["payload"] should be a JSON string (or bytes/bytearray acceptable to json.loads) that encodes a JSON object.
    Postconditions:
        - On successful return, the returned value is a dict parsed from decoded["payload"].
        - No modifications are made to self or to the input decoded mapping by this method.

## Side Effects:
    - No I/O is performed.
    - No network or external service calls.
    - No mutation of objects outside the method (aside from the possible propagation of raised exceptions).

### `jwt.api_jwt.PyJWT.decode` · *method*

## Summary:
Decode a JWT and return its payload (the claims object) after delegating verification and decoding to the class's decode_complete method.

## Description:
This public method is the primary, user-facing entry point for decoding a JSON Web Token (JWT) into its payload/claims. It delegates the heavy lifting — parsing, signature verification, and claim validation — to self.decode_complete and returns only the payload portion of the result.

Known callers and context:
- Application code and library users calling the PyJWT API to decode tokens (e.g., after receiving an Authorization header).
- Higher-level helpers or wrappers that need only the token claims (not the full decode metadata).
- It is invoked during runtime token validation / authentication pipeline steps where an incoming token must be turned into a claims object for authorization or session handling.

Why this is a separate method:
- Keeps the public API simple: callers commonly only need the claims, not the full decode metadata.
- Separates concerns: decode_complete provides a complete decode result (payload + headers + signature info) while this method provides a convenient, minimal return value.
- Allows backward-compatible deprecation of older parameter patterns (kwargs) at a single, central API entrypoint.

## Args:
    jwt (str | bytes):
        The encoded JWT as a string or bytes. This value is forwarded to decode_complete unchanged.
    key (AllowedPublicKeys | str | bytes, optional):
        The public key(s) or secret used to verify the token signature. Default: "".
    algorithms (list[str] | None, optional):
        Allowed algorithms for verifying the token signature (e.g., ["HS256", "RS256"]). If None, algorithm checks are delegated to decode_complete and any defaults it applies.
    options (dict[str, Any] | None, optional):
        Options controlling verification behavior (passed through to decode_complete). If None, default verification options are used.
    verify (bool | None, optional):
        Whether to perform signature/claim verification. None delegates to decode_complete's default behavior.
    detached_payload (bytes | None, optional):
        For detached payload tokens: the external payload bytes to use during verification. Default: None.
    audience (str | Iterable[str] | None, optional):
        Expected audience claim(s). If provided, used by decode_complete to validate the "aud" claim.
    issuer (str | None, optional):
        Expected issuer claim ("iss"). If provided, used by decode_complete to validate the issuer.
    leeway (float | timedelta, optional):
        Amount of leeway to allow when validating time-based claims (exp, nbf, iat). Default: 0.
    **kwargs (Any):
        Additional keyword arguments. Passing any kwargs emits a RemovedInPyjwt3Warning indicating that extra kwargs are deprecated and will be removed in pyjwt v3. These kwargs are otherwise ignored by this method.

## Returns:
    Any:
        The decoded JWT payload (the "claims" object) extracted from the mapping returned by decode_complete under the "payload" key. In typical usage this is a dictionary of claim names to values (dict[str, Any]), but the exact type is whatever decode_complete produces for the payload (e.g., dict or other JSON-decodable structure).

## Raises:
    Any exception raised by self.decode_complete:
        This method forwards exceptions raised by decode_complete. Common exceptions (imported by the module and typically raised during decode_complete) include:
        - DecodeError: Malformed token, invalid segments, or other generic decode failures.
        - ExpiredSignatureError: The token's "exp" claim indicates it is expired.
        - ImmatureSignatureError: The token's "nbf" claim indicates it is not yet valid.
        - InvalidAudienceError: The "aud" claim did not match the expected audience.
        - InvalidIssuedAtError: The "iat" claim is invalid (e.g., in the future).
        - InvalidIssuerError: The "iss" claim did not match the expected issuer.
        - MissingRequiredClaimError: A required claim was absent.
    Note: This method itself does not raise for kwargs, but it will emit a deprecation warning when kwargs are provided.

## State Changes:
    Attributes READ:
        - self.decode_complete (method): this method is invoked/read to perform the full decode/verification flow.
    Attributes WRITTEN:
        - None. This method does not modify attributes on self.

## Constraints:
    Preconditions:
        - jwt must be a str or bytes. Other types will be passed through to decode_complete and may result in a DecodeError.
        - If audience or issuer are provided they must be of the types documented above (audience may be a str or iterable of strings).
        - Callers expecting exceptions must be prepared to catch verification and claim-related exceptions raised by decode_complete.

    Postconditions:
        - No attributes on self are modified.
        - If decode_complete completes successfully, a mapping-like payload (commonly dict[str, Any]) is returned.
        - If kwargs were passed, a RemovedInPyjwt3Warning has been emitted via warnings.warn before delegating.

## Side Effects:
    - Emits a RemovedInPyjwt3Warning via warnings.warn when any extra kwargs are supplied.
    - Calls self.decode_complete, which may perform cryptographic operations, time-based claim checks (using system time), signature verification, and could raise the verification-related exceptions listed above.
    - No I/O (file/network) is performed by this method itself; any I/O-like behavior would be a consequence of what decode_complete performs.

### `jwt.api_jwt.PyJWT._validate_claims` · *method*

## Summary:
Validate standard JWT time- and identity-related claims (iat, nbf, exp, iss, aud, and required claims) according to the provided verification options and raise a specific exception on any validation failure. This method does not modify the PyJWT instance state.

## Description:
This method is invoked during the JWT decoding pipeline immediately after a token's payload has been parsed from JSON and before the decoded payload is returned to callers. Known callers:
- PyJWT.decode_complete — calls this method with a merged options dictionary after decoding the JWS/JWT and parsing the payload.
- PyJWT.decode — calls decode_complete which in turn invokes this method.

Lifecycle/context: claim verification stage of token decoding. It centralizes claim-level validation so the decode flow (signature verification, payload decoding, claim validation) remains separated into clear steps.

Why a standalone method:
- Claim validation involves multiple separate checks (required claims, numeric time checks, issuer and audience rules) with branching based on options and presence of claims; extracting this logic improves readability, testability, and reuse.
- Keeps decode_* methods focused on I/O and signature handling while delegating claim semantics to a single method.

## Args:
    payload (dict[str, Any]):
        Decoded JWT payload (parsed JSON object). Expected to be a mapping of claim names to values.
    options (dict[str, Any]):
        A dictionary of verification flags and options indicating which checks to perform. The implementation expects keys (booleans) at least for:
        - "verify_iat", "verify_nbf", "verify_exp", "verify_aud", "verify_iss"
        - "require" (iterable/list of claim names required)
        Optionally "strict_aud" may be present and is used when verifying audience.
        This method will index into options directly; callers should supply a dictionary containing these keys (typically produced by merging default options and caller-supplied options).
    audience (str | Iterable[str] | None, optional; default None):
        The expected audience(s) for audience validation. Allowed values:
        - None: indicates caller did not provide a required audience.
        - str: a single acceptable audience string.
        - Iterable[str]: multiple acceptable audience strings (e.g., list or tuple of strings).
        If audience is not None and is not a str or an iterable, a TypeError is raised.
    issuer (str | None, optional; default None):
        The expected issuer string. If None, issuer validation is a no-op.
    leeway (float | timedelta, optional; default 0):
        A clock skew allowance in seconds. If a timedelta is provided, it is converted to total seconds (float). Negative values behave as normal numeric leeway (but are rarely useful).

## Returns:
    None
    - Normal return indicates all enabled validations passed successfully.
    - The method never returns a value on failure; it raises a specific exception indicating the failure reason.

## Raises:
    TypeError("audience must be a string, iterable or None")
        - Condition: caller provided an audience value that is not None and is not an instance of str or an Iterable.
    MissingRequiredClaimError(claim_name)
        - Condition: a claim listed in options["require"] is missing or has value None in the payload.
        - Raised by: _validate_required_claims.
    InvalidIssuedAtError("Issued At claim (iat) must be an integer.")
        - Condition: the payload contains "iat" but its value cannot be coerced to int (ValueError when casting).
        - Raised by: _validate_iat.
    ImmatureSignatureError("The token is not yet valid (iat)")
        - Condition: "iat" is present and its integer value is strictly greater than (now + leeway).
        - Raised by: _validate_iat.
    DecodeError("Not Before claim (nbf) must be an integer.")
        - Condition: "nbf" is present but its value cannot be coerced to int.
        - Raised by: _validate_nbf.
    ImmatureSignatureError("The token is not yet valid (nbf)")
        - Condition: "nbf" is present and its integer value is strictly greater than (now + leeway).
        - Raised by: _validate_nbf.
    DecodeError("Expiration Time claim (exp) must be an integer.")
        - Condition: "exp" is present but its value cannot be coerced to int.
        - Raised by: _validate_exp.
    ExpiredSignatureError("Signature has expired")
        - Condition: "exp" is present and its integer value is less than or equal to (now - leeway).
        - Raised by: _validate_exp.
    MissingRequiredClaimError("iss")
        - Condition: options["verify_iss"] is True, issuer argument is not None, but the payload does not contain "iss".
        - Raised by: _validate_iss.
    InvalidIssuerError("Invalid issuer")
        - Condition: options["verify_iss"] is True, issuer argument is not None, and payload["iss"] != issuer.
        - Raised by: _validate_iss.
    InvalidAudienceError(...)
        - Several possible messages and conditions (raised by _validate_aud):
            * "Invalid audience" — audience is None but token contains a truthy "aud" claim (caller did not expect any audience but token specifies one).
            * "Invalid audience (strict)" — strict mode requested but caller-provided audience is not a str.
            * "Invalid claim format in token (strict)" — strict mode and token's "aud" is not a str.
            * "Audience doesn't match (strict)" — strict mode and audience string differs from token's aud string.
            * "Invalid claim format in token" — non-strict mode and token's aud claim is neither a str nor a list[str], or the list contains non-str elements.
            * "Audience doesn't match" — non-strict mode and none of the provided audience values appear in the token's aud list.
        - These conditions reflect token format issues or mismatches as handled by the audience validator.

## State Changes:
Attributes READ:
    - None of the PyJWT instance attributes are read by this method. (It operates only on the provided payload and options argument; callers typically merge instance defaults into options before calling.)

Attributes WRITTEN:
    - None. The method does not modify self, payload, or options.

## Constraints:
Preconditions:
    - payload must be a dict-like mapping parsed from the JWT JSON payload.
    - options should be a dict containing boolean flags for the verifications this method will check:
        "verify_iat", "verify_nbf", "verify_exp", "verify_aud", "verify_iss", and "require" (iterable).
      The usual caller merges default options into this dict before invoking this method.
    - If audience is provided, it must be a str or an Iterable[str]; otherwise a TypeError will be raised.

Postconditions:
    - On successful return, all enabled verifications (as dictated by options and presence of claims) have been performed and passed.
    - No mutations have been made to self, payload, or options.
    - On failure, a specific exception (see Raises) has been raised describing the cause.

## Side Effects:
    - No I/O, logging, or external service calls.
    - Raises exceptions that propagate to callers, affecting control flow.
    - Converts timedelta leeway to seconds (local variable only); does not mutate the caller's leeway argument.

### `jwt.api_jwt.PyJWT._validate_required_claims` · *method*

## Summary:
Ensures every claim named in the options["require"] list is present (and not None) in the provided payload; raises an error if any required claim is missing.

## Description:
This private helper is invoked during token validation as part of the decode/decode_complete → _validate_claims pipeline to enforce explicitly required claims before other claim-specific validations run. Known callers:
- PyJWT._validate_claims — called early in the validation stage after payload decoding.
- Indirectly used during PyJWT.decode_complete and PyJWT.decode as part of the decode flow.

This logic is separated into its own method to isolate the single responsibility of "required claims" enforcement (improves readability and testability) and to allow reuse by the overall claim-validation routine without inlining the loop every time claims must be checked.

## Args:
    payload (dict[str, Any]):
        A mapping representing the JWT payload (decoded JSON object). Expected to be a dict where keys are claim names and values are claim values. The method will treat a missing key or a key whose value is None as "missing".
    options (dict[str, Any]):
        A configuration mapping that MUST contain the key "require". options["require"] is expected to be an iterable (typically a list) of claim names (usually strings) that MUST be present in payload. Typical value from the class defaults is an empty list.

## Returns:
    None
    Successful return guarantees that every claim listed in options["require"] exists in payload and that payload[claim] is not None for each required claim.

## Raises:
    MissingRequiredClaimError
        Raised for the first claim in options["require"] for which payload.get(claim) is None. This covers both the key being absent from payload and the key existing with value None.
    KeyError
        If the options mapping does not contain the "require" key, a KeyError will be raised when attempting to iterate options["require"].
    TypeError
        If options["require"] is not iterable, or if a claim in options["require"] cannot be used as a mapping key (e.g., an unhashable object), Python will raise a TypeError while iterating or when calling payload.get(claim). These are not converted into library-specific errors by this method.

## State Changes:
Attributes READ:
    None — this method does not read or depend on any self.<attr> attributes; it operates only on the provided payload and options arguments.
Attributes WRITTEN:
    None — this method does not modify self or any external objects; it only inspects payload and options.

## Constraints:
Preconditions:
    - payload must be a mapping-like object supporting .get(key). In this codebase it is expected to be a dict[str, Any] produced by payload decoding.
    - options must be a mapping that contains the "require" key whose value is an iterable of claim identifiers (commonly strings).
Postconditions:
    - If the method returns normally, then for every claim in options["require"], payload.get(claim) is not None.
    - If a required claim is missing or explicitly None, the method will not return; it will raise MissingRequiredClaimError naming that claim.

## Side Effects:
    - No I/O, no external service calls.
    - The only observable effect is raising an exception when a required claim is missing; it performs no mutation of payload, options, or self.

### `jwt.api_jwt.PyJWT._validate_iat` · *method*

## Summary:
Validates the token's Issued At (iat) claim by ensuring it is an integer and not in the future beyond the allowed leeway. Does not modify object state; raises a specific exception when validation fails.

## Description:
This method is invoked during JWT validation/decoding as part of the claims verification pipeline to enforce the semantics of the "iat" (Issued At) claim. Typical callers are the PyJWT token decoding/verification routines that iterate over and validate standard claims (e.g., expiration, not-before, issued-at). The check is factored into its own method to keep claim-specific validation isolated, testable, and reusable across different decode/verify code paths.

Behavior summary:
- Reads the "iat" value from the provided payload.
- Attempts to coerce it to an integer.
- If coercion fails with a ValueError, raises InvalidIssuedAtError with the exact message from the implementation.
- If the integer iat is strictly greater than now + leeway, raises ImmatureSignatureError with the exact message from the implementation.
- Otherwise, returns None (indicating the iat check passed).

## Args:
    payload (dict[str, Any]):
        The decoded JWT payload (claims). Must contain the "iat" key for this method to operate without raising KeyError.
    now (float):
        Current time as a numeric POSIX timestamp in seconds (e.g., time.time()). Used as the reference "now" against which iat is compared.
    leeway (float):
        Number of seconds of allowed clock skew when comparing iat to now. Typically non-negative; the method does not enforce non-negativity but behavior is defined as checking iat > (now + leeway).

## Returns:
    None
    - Successful completion (no exception) means the payload's iat claim is an integer and iat <= now + leeway.

## Raises:
    InvalidIssuedAtError
        - Condition: When converting payload["iat"] to int raises ValueError.
        - Message exactly: "Issued At claim (iat) must be an integer."
        - Note: This corresponds exactly to the code path that catches ValueError from int(...).
    ImmatureSignatureError
        - Condition: When the integer iat value is strictly greater than (now + leeway).
        - Message exactly: "The token is not yet valid (iat)"
    KeyError
        - Condition: If the payload does not contain the "iat" key (payload["iat"] access). This method does not catch KeyError; callers are expected to ensure required claims exist or handle this exception.
    TypeError (propagated)
        - Condition: If payload["iat"] is a value that causes int(...) to raise TypeError (for example None). The method only catches ValueError, so TypeError will propagate to the caller.

## State Changes:
    Attributes READ:
        - None (the method does not read or depend on any self.<attr> attributes)
    Attributes WRITTEN:
        - None (the method does not modify any self.<attr> attributes)

## Constraints:
    Preconditions:
        - payload must be a mapping containing the "iat" key; otherwise a KeyError will be raised.
        - now and leeway should be numeric (float or int). If non-numeric types are passed, comparison or arithmetic may raise TypeError.
        - The semantic expectation: iat is representable as an integer number of seconds since epoch (UTC).
    Postconditions:
        - If the method returns normally, payload["iat"] was successfully converted to an integer iat and iat <= now + leeway.
        - No attributes of self or payload are modified by this method.

## Side Effects:
    - No I/O performed.
    - No external services called.
    - No mutation of objects outside the method's local scope (the payload mapping is read but not modified).
    - Exceptions described above may be raised and must be handled by the caller.

### `jwt.api_jwt.PyJWT._validate_nbf` · *method*

## Summary:
Validates the Not Before (nbf) claim in a JWT payload and raises if the token is not yet valid; does not modify the object state.

## Description:
This method is called during JWT decoding validation to ensure the token's "nbf" (Not Before) timestamp indicates the token is currently valid. Known callers and lifecycle context:
- PyJWT._validate_claims calls this method when:
  - the payload contains an "nbf" entry, and
  - the merged options enable verify_nbf (decode_complete -> _validate_claims -> _validate_nbf).
- Thus it runs in the token validation stage of decode/decode_complete.

This logic is factored into its own method to keep claim-specific checks modular and consistent with the separate validators for "iat" and "exp". Splitting each claim validation into its own helper improves readability, testability, and reuse.

## Args:
    payload (dict[str, Any]):
        The decoded JWT payload (JSON object) that must contain an "nbf" key when this validator is invoked.
        The value associated with "nbf" should be an integer or a value convertible to an integer representing seconds since the epoch (UTC). Fractional seconds are truncated by int().
    now (float):
        Current time as seconds since the epoch (UTC). Typically produced by datetime.now(tz=timezone.utc).timestamp().
    leeway (float):
        Allowed clock skew in seconds. The check uses now + leeway as the effective current time.

## Returns:
    None
    - If the claim passes validation no value is returned; the method completes normally.

## Raises:
    DecodeError:
        Raised when payload["nbf"] is present but cannot be converted to an integer because int(...) raised ValueError.
        Exact condition: int(payload["nbf"]) raises ValueError.
    ImmatureSignatureError:
        Raised when the numeric nbf value is strictly greater than now + leeway (i.e., the token's valid-from time is in the future).
        Exact condition: int(payload["nbf"]) > (now + leeway)

    Other exceptions that may propagate from the underlying operations:
    - KeyError: If called when "nbf" is not present in payload, accessing payload["nbf"] will raise KeyError. (In typical use _validate_claims only calls this method when "nbf" is present.)
    - TypeError: If payload["nbf"] has a type that int(...) does not accept (for example None), int(...) may raise TypeError; this is not caught by this method and will propagate.

## State Changes:
    Attributes READ:
        None (the method does not read any self.<attr> attributes).
    Attributes WRITTEN:
        None (the method does not modify self or the payload).

## Constraints:
    Preconditions:
        - The payload must be a mapping containing an "nbf" key if this method is invoked (the caller _validate_claims ensures this before calling).
        - now and leeway must be numeric seconds (floats or ints); if leeway was supplied as a timedelta it should be converted to total seconds by the caller (this conversion is performed by _validate_claims).
    Postconditions:
        - If the method returns normally, no exception was raised and the nbf claim is less than or equal to now + leeway (after integer conversion/truncation).
        - The object state and the payload are unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of self or of payload.
    - Only effect is potential raising of exceptions described above.

### `jwt.api_jwt.PyJWT._validate_exp` · *method*

## Summary:
Validates the token expiration (exp) claim in a payload and raises if the token is expired; does not modify the object state.

## Description:
This method is invoked during JWT decoding/validation to check that the "exp" claim represents a timestamp that has not passed (subject to leeway). Known callers:
- PyJWT._validate_claims — called when decoding a token if "exp" is present and options["verify_exp"] is True.
- PyJWT.decode_complete → PyJWT._validate_claims — overall decode pipeline invokes this as part of claim validation.

Lifecycle/context:
- Executed in the validation stage of decoding a JWT (after payload parsing and before returning the decoded payload).
- It is a separate method to isolate expiration-checking logic from other claim checks (iat/nbf/aud/iss), making the validation steps modular, testable, and reusable.

## Args:
    payload (dict[str, Any]):
        The decoded JWT payload as a JSON object (dictionary). Must contain the "exp" key when this method is called.
    now (float):
        Current time as a POSIX timestamp in seconds (e.g., from datetime.now(tz=timezone.utc).timestamp()).
    leeway (float):
        Allowed clock skew in seconds. Caller typically normalizes timedelta to seconds before calling; must be a numeric value (can be 0).

## Returns:
    None
    - On success (not expired) the method returns None and performs no mutations.

## Raises:
    DecodeError:
        Raised when the "exp" claim cannot be converted to an integer due to an invalid literal (ValueError from int()).
        Condition: payload["exp"] is present but int(payload["exp"]) raises ValueError (e.g., "123.45" or non-numeric string).
    ExpiredSignatureError:
        Raised when the expiration time is in the past taking leeway into account.
        Condition: int(payload["exp"]) <= (now - leeway).
    KeyError (propagates):
        If "exp" is not present in payload, accessing payload["exp"] raises KeyError. _validate_claims ensures "exp" exists before calling, but callers that call this method directly may see KeyError.
    TypeError (propagates):
        If payload["exp"] is of a type that int() cannot convert (e.g., None or an arbitrary object), int(...) may raise TypeError which will propagate.

## State Changes:
    Attributes READ:
        None — this method does not read or depend on any self.<attr> fields.
    Attributes WRITTEN:
        None — this method does not modify self or assign object attributes.

## Constraints:
    Preconditions:
        - The payload must be a dict-like mapping and contain the "exp" key (the standard caller, _validate_claims, tests for presence before calling).
        - now must be a POSIX timestamp in seconds (float).
        - leeway must be a numeric value in seconds (float); if a timedelta is provided it should be converted by the caller.
    Postconditions:
        - If no exception is raised, the payload is considered not expired under the provided now/leeway.
        - The method does not mutate payload or the PyJWT instance.

## Side Effects:
    - No I/O, no network calls.
    - No mutation of objects outside self (payload is read but not modified).

### `jwt.api_jwt.PyJWT._validate_aud` · *method*

## Summary:
Validate the token's "aud" (audience) claim against the provided expected audience(s); raises a specific exception on any mismatch or malformed claim. Does not modify self or payload.

## Description:
This method is called during JWT claim validation as part of the decode pipeline. Known callers:
- PyJWT._validate_claims — invoked when verifying claims after payload decoding and before returning the decoded payload.
- Indirect callers: PyJWT.decode_complete and PyJWT.decode (both call _validate_claims during token decoding).

Context/lifecycle: After a token is decoded and its payload parsed into a dict, _validate_claims delegates audience verification to this method if audience verification is enabled in the options. This method encapsulates all audience-specific validation logic (presence, type/format checks, strict vs. non-strict semantics, and matching rules) so the claim validation pipeline remains organized and reusable.

Reasons for being a standalone method:
- Audience validation has multiple distinct rules (strict mode, type coercions, presence checks) that are reused and complex enough to justify isolation for readability, testability, and reuse.
- Separates concern of audience validation from other claim checks (exp, nbf, iat, iss).

## Args:
    payload (dict[str, Any]):
        The decoded JWT payload (JSON object parsed to a dict). If present, the "aud" key holds the audience claim.
    audience (str | Iterable[str] | None):
        The expected audience(s) supplied by the caller. Allowed values:
        - None: indicates the caller did not provide an expected audience.
        - str: a single acceptable audience value.
        - Iterable[str]: multiple acceptable audience values (e.g., list or tuple of strings).
    strict (bool, optional; default False):
        If True, enforce strict rules: both provided audience and the token's aud claim must be strings and must be exactly equal.

## Returns:
    None
    - On successful validation the function returns None.
    - On validation failure it never returns; instead it raises one of the documented exceptions.

## Raises:
    InvalidAudienceError("Invalid audience")
        - Condition: audience is None but the token has a truthy "aud" claim (i.e., "aud" in payload and payload["aud"] is truthy).
        - Semantic: the caller did not expect any audience but the token specifies one.

    MissingRequiredClaimError("aud")
        - Condition: audience is not None (caller expects a match) but the token is missing "aud" or payload["aud"] is falsy (e.g., empty string, empty list, None).
        - Semantic: an audience claim is required for verification but absent/empty in the token.

    InvalidAudienceError("Invalid audience (strict)")
        - Condition: strict is True but the caller-provided audience is not a str.
        - Semantic: strict mode requires a single-string audience argument.

    InvalidAudienceError("Invalid claim format in token (strict)")
        - Condition: strict is True but the token's "aud" claim is not a str.
        - Semantic: strict mode requires the token's aud claim be a single string.

    InvalidAudienceError("Audience doesn't match (strict)")
        - Condition: strict is True, both audience and token "aud" are strings, but they are not equal (audience != payload["aud"]).
        - Semantic: strict equality failed.

    InvalidAudienceError("Invalid claim format in token")
        - Conditions (any of the following):
            * After non-strict conversion, the token's "aud" claim is not a list (e.g., dict, int, etc.).
            * The token's "aud" claim is a list but contains at least one non-str element.
        - Semantic: malformed aud claim in token for non-strict matching.

    InvalidAudienceError("Audience doesn't match")
        - Condition: non-strict mode, token "aud" normalized to a list[str], caller-provided audience normalized to an iterable of strings (if it was a str it's converted to a single-item list), and none of the caller audiences is present in the token's audience claim list.
        - Notes:
            * If caller supplies an empty iterable for audience, the all(...) check vacuously succeeds and this exception is raised (i.e., empty audiences do not match).
            * The code only checks membership of caller audiences in the token's audience list and does not validate types of elements in caller-provided iterable.

## State Changes:
Attributes READ:
    - None of self's attributes are read. (The method only inspects the provided payload and the audience argument.)

Attributes WRITTEN:
    - None of self's attributes are modified.
    - Local variables may be reassigned (e.g., audience_claims, audience) but no external mutation occurs.

## Constraints:
Preconditions:
    - payload must be a dict-like object (the caller is expected to pass the parsed JSON payload as a dict).
    - If audience is not None, it should be either a str or an iterable of acceptable audience values; callers (e.g., _validate_claims) typically enforce this and raise TypeError otherwise.
    - The method assumes payload may contain an "aud" key with a value that is one of: str, list[str], or other; non-conforming types lead to InvalidAudienceError.

Postconditions:
    - If the function returns normally, the provided audience (if any) matched the token's "aud" claim according to strict or non-strict rules, or audience was None and the token had no aud claim.
    - The method does not mutate payload or the PyJWT instance.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside the method scope (payload is read but not modified).
    - Raises exceptions on failure which propagate to the caller and affect control flow.

## Implementation notes / important behaviors to preserve when reimplementing:
    - Falsy "aud" values (empty string, empty list, None) are treated as "missing/empty".
    - strict=True requires exact string equality; both audience argument and token "aud" must be strings.
    - Non-strict mode:
        - Single-string token "aud" is treated as a single-element list for comparison.
        - Token "aud" must be either str or list; list elements must all be strings.
        - Caller-provided audience str is converted to a single-element iterable; other iterables are iterated as-is.
        - Matching passes if any element from the caller-provided audience iterable is equal to any element of the token's audience list; otherwise raise InvalidAudienceError("Audience doesn't match").
    - Messages in raised exceptions match those used by callers and tests and should be preserved for compatibility.

### `jwt.api_jwt.PyJWT._validate_iss` · *method*

## Summary:
Validate that the payload's "iss" (issuer) claim matches the expected issuer; performs no state mutation on the PyJWT instance and raises if the claim is missing or does not match.

## Description:
- Known callers and call context:
  - PyJWT._validate_claims calls this method when options["verify_iss"] is True during token validation.
  - PyJWT.decode_complete invokes _validate_claims as part of the decode/validation pipeline.
  - PyJWT.decode calls decode_complete, so typical invocation occurs during decode(...) or decode_complete(...) when issuer validation is requested.
  - Lifecycle stage: this method runs during JWT validation (decode path) after the token payload has been decoded into a Python dict and before the decode method returns a validated payload.
- Rationale for being a separate method:
  - Separates issuer-specific validation from other claim checks for single-responsibility, easier testing, and reuse from the centralized _validate_claims orchestration.
  - Keeps decode flow modular so options can selectively enable/disable issuer verification.

## Args:
    payload (dict[str, Any]):
        - A decoded JWT payload (JSON object) represented as a dict.
        - Expected to be the result of payload decoding (PyJWT._decode_payload guarantees payload is a dict).
    issuer (Any):
        - The expected issuer value to validate against the payload's "iss" claim.
        - Allowed values: Any JSON-compatible type (commonly a str) or None.
        - Behavior:
            - If issuer is None, validation is skipped (method returns immediately).
            - Otherwise, issuer is compared to payload["iss"] using Python equality (==).

## Returns:
    None
    - Successful return means either issuer was None (validation skipped) or payload contained an "iss" claim that equals the provided issuer.
    - No value is returned; success is signaled by absence of an exception.

## Raises:
    MissingRequiredClaimError:
        - Raised when issuer is not None and the payload does not contain the "iss" key.
        - Exact trigger: issuer is not None AND "iss" not in payload.
    InvalidIssuerError:
        - Raised when issuer is not None, the payload contains an "iss" key, but payload["iss"] != issuer (inequality by Python's ==).
        - Exact trigger: issuer is not None AND "iss" in payload AND payload["iss"] != issuer

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> attributes on the PyJWT instance)
    Attributes WRITTEN:
        - None (this method does not modify the PyJWT instance)

## Constraints:
    Preconditions:
        - payload must be a dict (decoded JSON object). Calling code (e.g., _decode_payload) should ensure this.
        - issuer may be None; if None, the method will not perform any checks.
    Postconditions:
        - If the method returns without raising:
            - Either issuer was None (validation skipped) OR payload contains "iss" and payload["iss"] == issuer.
        - No mutation to payload or the PyJWT instance is performed.

## Side Effects:
    - No I/O, no network calls, and no mutations to objects outside the method's local scope.
    - The only observable effects are raising one of the documented exceptions when validation fails.

