# `api_jwk.py`

## `jwt.api_jwk.PyJWK` · *class*

## Summary:
Represents a single JSON Web Key (JWK) and provides construction, algorithm resolution, and a concrete cryptographic key object derived from the JWK contents.

## Description:
PyJWK encapsulates a single JWK mapping and is responsible for:
- Validating the minimal required JWK fields (at least "kty").
- Inferring or accepting an explicit algorithm name for use with the key.
- Selecting an algorithm implementation from the default algorithm registry.
- Constructing a concrete cryptographic key object by delegating to the selected algorithm's from_jwk routine.

Instantiate PyJWK when you have a single JWK (as a mapping/dict or as JSON text) and you need a ready-to-use key object for signing, verification, or inspection. Typical callers/factories:
- PyJWK.from_dict(obj, algorithm) — when you already have a mapping-like JWK.
- PyJWK.from_json(data, algorithm) — when you have a JSON-encoded JWK string.

This class separates concerns: it is responsible for input validation and algorithm selection/dispatch, while cryptographic parsing/initialization is delegated to algorithm implementations.

## State:
Attributes (instance-level)
- _algorithms: mapping[str, AlgorithmClass]
    - Populated by calling get_default_algorithms() during construction.
    - Invariant: must be a mapping-like object that supports .get(name) and returns algorithm implementations or None.
- _jwk_data: JWKDict
    - The original JWK mapping provided at construction. Expected to implement .get(key, default).
    - Invariant: after successful construction it contains at least a "kty" entry.
- Algorithm: AlgorithmClass | None
    - The algorithm implementation selected from _algorithms for the resolved algorithm name.
    - Valid values: an algorithm class/object that exposes at least a classmethod/staticmethod from_jwk(jwk_data) used to produce the concrete key.
    - Invariant after successful construction: not None.
- key: Any
    - The concrete cryptographic key object returned by Algorithm.from_jwk(self._jwk_data).
    - Type depends on the algorithm implementation (could be a cryptography object, bytes, or other key representation).
    - Invariant after successful construction: set and usable with the corresponding algorithm routines.

Constructor parameters and constraints
- jwk_data (JWKDict): required. A mapping-like object representing a single JWK. Must include "kty" or construction will fail.
- algorithm (str | None): optional. If provided, used directly to select the algorithm. If omitted, the constructor tries:
    1) jwk_data.get("alg")
    2) Infer from jwk_data["kty"] (and when required jwk_data["crv"]) using the built-in mapping:
       - EC: crv None or "P-256" -> "ES256"; "P-384" -> "ES384"; "P-521" -> "ES512"; "secp256k1" -> "ES256K".
       - RSA: -> "RS256"
       - oct: -> "HS256"
       - OKP: requires crv; "Ed25519" -> "EdDSA"
    - If the inference fails because of unsupported or missing values, an InvalidKeyError is raised.

Class invariants (post-construct success)
- _jwk_data contains a valid "kty" and any other fields required by the chosen algorithm.
- Algorithm is resolved (not None) and key is assigned by Algorithm.from_jwk.
- If an algorithm requiring external crypto support is selected, the environment had that support available at construction time.

## Lifecycle:
Creation
- Direct constructor:
    - PyJWK(jwk_data: JWKDict, algorithm: str | None = None)
    - Required: jwk_data is a mapping-like object.
- Factory methods:
    - PyJWK.from_dict(obj: JWKDict, algorithm: str | None = None) -> PyJWK
      Convenience wrapper that calls the constructor.
    - PyJWK.from_json(data: str, algorithm: str | None = None) -> PyJWK
      Parses JSON with json.loads(data) into a mapping and delegates to from_dict.

Usage
- Typical sequence:
    1) Instantiate via constructor or factory.
    2) Access metadata via properties: key_type, key_id, public_key_use.
    3) Use the .key attribute with algorithm-specific routines (sign/verify/serialize) — the actual operations are provided by the algorithm implementation and the key object.
- No required ordering of property accesses; properties simply read _jwk_data.

Destruction / Cleanup
- PyJWK holds in-memory references (algorithm registry and key objects). There is no explicit cleanup API (no close() or context manager). If underlying algorithm/key objects require cleanup, that must be handled by those implementations; PyJWK does not manage resource release.

## Method Map:
flowchart LR
    A[from_json(data, algorithm?)] --> B[json.loads -> obj]
    B --> C[from_dict(obj, algorithm?)]
    C --> D[PyJWK.__init__(jwk_data=obj, algorithm?)]
    D --> E[get_default_algorithms() -> _algorithms]
    D --> F[resolve algorithm name: algorithm or obj['alg'] or infer from kty/crv]
    F --> G[check cryptography requirement: if algorithm in requires_cryptography and not has_crypto -> raise PyJWKError]
    G --> H[Algorithm = _algorithms.get(algorithm)]
    H --> I[if not Algorithm -> raise PyJWKError]
    I --> J[key = Algorithm.from_jwk(_jwk_data)]
    J --> K[object ready; properties read _jwk_data]

Note: Properties (key_type, key_id, public_key_use) are read-only accessors that simply return _jwk_data.get("kty"/"kid"/"use").

## Raises:
Exceptions raised directly by PyJWK operations:
- InvalidKeyError:
    - If jwk_data.get("kty") is falsy or missing.
    - If kty == "EC" and crv is present but not one of the supported values {"P-256", "P-384", "P-521", "secp256k1"}.
    - If kty == "OKP" and crv is missing.
    - If kty == "OKP" and crv is present but not "Ed25519".
    - If kty is present but not one of the supported key types {"EC", "RSA", "oct", "OKP"}.
- PyJWKError:
    - If the chosen algorithm name requires the 'cryptography' package but the runtime lacks it (determined via has_crypto and requires_cryptography).
    - If no algorithm implementation is found in the default algorithm registry for the resolved algorithm name.
- json.JSONDecodeError:
    - Raised by from_json when the provided string is not valid JSON (propagated directly).
- AttributeError:
    - If callers pass a non-mapping to the constructor/from_dict/from_json that lacks .get, operations that call .get will raise AttributeError.
- Any exceptions raised by Algorithm.from_jwk:
    - Construction delegates to Algorithm.from_jwk(self._jwk_data); exceptions thrown there (parsing, cryptographic errors) propagate to the caller.

## Example:
- Creation from a dict:
    - Provide a JWK mapping (e.g., {"kty": "RSA", "n": "<base64url>", "e": "AQAB", "kid": "my-key"}).
    - Call PyJWK.from_dict(jwk_mapping) or PyJWK(jwk_mapping).
    - On success: inspect returned.key to perform algorithm-specific operations; use returned.key_id to match keys.

- Creation from JSON:
    - Provide a JSON string representing a single JWK object.
    - Call PyJWK.from_json(json_text).
    - This decodes the JSON and follows the same construction flow as above.

Notes and implementation hints for reimplementation:
- get_default_algorithms() should return a mapping from algorithm name strings (e.g., "RS256", "ES256", "EdDSA") to algorithm handler objects/classes exposing a from_jwk(jwk_dict) method.
- has_crypto is a boolean flag indicating whether optional cryptography dependencies are available.
- requires_cryptography is an iterable/set of algorithm names whose implementations require the external cryptography dependency; if an algorithm is in this set and has_crypto is False, constructing a PyJWK for that algorithm must raise an error.
- Algorithm.from_jwk must accept the raw jwk mapping and return an algorithm-specific key object (type Any). PyJWK does not inspect or modify that key object after assignment.

### `jwt.api_jwk.PyJWK.__init__` · *method*

## Summary:
Initializes a PyJWK instance from a JWK dictionary and resolves the signing/verification algorithm and concrete key object, updating the instance with algorithm and key state.

## Description:
This initializer constructs internal algorithm mappings, validates and inspects the provided JWK data, determines the appropriate algorithm (using the explicit algorithm argument, the JWK "alg" member if present, or by inferring from "kty" and "crv"), enforces any cryptography dependency requirements, locates the algorithm implementation, and builds the key object via the algorithm's from_jwk factory.

Known callers and context:
- Called when a library consumer or higher-level helper constructs a PyJWK to represent a single JWK for use in signing or verification.
- Typically invoked during JWK set parsing or key-loading pipeline (e.g., a PyJWKSet loader) as the step that validates and materializes a raw JWK into a usable key object.
Why this is a dedicated method:
- The logic performs validation, algorithm-resolution, dependency checks, and key construction — a distinct and reusable responsibility that cleanly separates raw JWK parsing from key usage and keeps callers simple.

## Args:
    jwk_data (JWKDict):
        - The JWK representation for a single key. Expected to be a mapping-like object with get(key, default) behavior.
        - Must include the "kty" member (key type). May include "alg" (explicit algorithm) and "crv" (curve) depending on kty.
    algorithm (str | None, optional):
        - Explicit algorithm name to use (e.g., "RS256", "ES256", "EdDSA"). If provided, it takes precedence over any "alg" member in jwk_data.
        - If omitted, the initializer will use jwk_data["alg"] when jwk_data is a dict and "alg" is present, otherwise will infer from "kty" and "crv".

## Returns:
    None
    - On success, instance attributes are set so the object is ready for cryptographic operations:
        * self.Algorithm — algorithm implementation/class resolved for the chosen algorithm name.
        * self.key — concrete key object produced by Algorithm.from_jwk(jwk_data).
    - The constructor itself returns None (standard for __init__).

## Raises:
    InvalidKeyError:
        - If the JWK data does not contain "kty" (key type).
        - If an unsupported or unknown "kty" is present.
        - If an EC/OKP curve ("crv") is present but is unsupported.
        - If "crv" is required by the kty (OKP) but missing.
        - Error messages include the offending jwk_data or value for debugging.
    PyJWKError:
        - If the resolved algorithm requires the optional 'cryptography' dependency but has_crypto is False:
          raised with message "{algorithm} requires 'cryptography' to be installed."
        - If after resolution there is no known algorithm implementation available for the chosen algorithm string:
          raised with message "Unable to find an algorithm for key: {jwk_data}".
    Any exceptions raised by the resolved Algorithm.from_jwk(jwk_data):
        - The initializer does not catch exceptions from the algorithm's from_jwk factory, so errors during key construction (parsing, decoding, or cryptographic construction) propagate to the caller.

## State Changes:
Attributes READ:
    - self._jwk_data: read to inspect "kty", "alg", and "crv" members after being assigned from the jwk_data argument.
Attributes WRITTEN:
    - self._algorithms: set to the mapping returned by get_default_algorithms().
    - self._jwk_data: set to the provided jwk_data argument.
    - self.Algorithm: set to the algorithm implementation/class resolved from the algorithm name.
    - self.key: set to the value returned by self.Algorithm.from_jwk(self._jwk_data).

## Constraints:
Preconditions:
    - jwk_data must be a mapping-like object (supports get) and must include the "kty" member.
    - If jwk_data is not a dict, algorithm argument should be supplied when jwk_data lacks an "alg" member (since algorithm inference uses jwk_data.get only when jwk_data is a dict).
Postconditions:
    - On success (no exception), the instance will have:
        * self.Algorithm referencing the chosen algorithm implementation.
        * self.key holding the concrete key object produced by Algorithm.from_jwk.
    - The chosen algorithm is determined in the following precedence:
        1. explicit algorithm parameter (if provided)
        2. jwk_data["alg"] (if jwk_data is a dict and "alg" present)
        3. inferred from jwk_data["kty"] and jwk_data.get("crv") using these rules:
            - kty == "EC": crv -> "ES256" (P-256 or missing), "ES384" (P-384), "ES512" (P-521), "ES256K" (secp256k1)
            - kty == "RSA": "RS256"
            - kty == "oct": "HS256"
            - kty == "OKP": requires crv; "Ed25519" -> "EdDSA"
        - If inference fails due to unsupported values, an InvalidKeyError is raised.

## Side Effects:
    - No file I/O, network calls, or global state mutation beyond assigning instance attributes.
    - May trigger import/module-level dependency checks by referencing has_crypto and requires_cryptography.
    - Calls Algorithm.from_jwk(jwk_data), which may perform decoding, cryptographic object construction, or other side effects dependent on the algorithm implementation; any side effects/errors from that call propagate.

### `jwt.api_jwk.PyJWK.from_dict` · *method*

## Summary:
Creates and returns a new PyJWK instance from a JWK dictionary, delegating all validation and key construction to the PyJWK constructor; does not modify any existing PyJWK.

## Description:
This static factory method is a convenience wrapper that constructs a PyJWK from a JWK-like mapping and an optional algorithm hint.

Known callers and usage context:
- PyJWK.from_json calls this method after parsing a JSON string into a dict.
- Typical usage: invoked when converting a parsed JWK (for a single key) into a PyJWK object during JWK loading/parsing pipelines or when code explicitly constructs a PyJWK from an in-memory JWK dict.

Why this is a separate method:
- Provides a clear, intention-revealing factory named for the input type (dict) and keeps call sites concise.
- Keeps creation call-site code readable (PyJWK.from_dict(...)) instead of directly invoking the constructor; the constructor contains the actual validation and key building logic.

## Args:
    obj (JWKDict):
        A JWK dictionary (mapping) representing the key. Expected to support .get(key, default).
        Must include at least a "kty" member (key type), otherwise construction raises InvalidKeyError.
    algorithm (str | None, optional):
        An optional algorithm name (e.g., "RS256", "ES256", "EdDSA") used to select the signing/verification algorithm.
        If None, the constructor will attempt to infer the algorithm from obj.get("alg") or from the key type ("kty") and curve ("crv") according to the following rules used by the constructor:
          - EC / crv "P-256" (or missing crv): "ES256"
          - EC / crv "P-384": "ES384"
          - EC / crv "P-521": "ES512"
          - EC / crv "secp256k1": "ES256K"
          - RSA: "RS256"
          - oct: "HS256"
          - OKP / crv "Ed25519": "EdDSA"
        If crv is missing for OKP, or an unsupported crv/kty is present, the constructor raises InvalidKeyError.

## Returns:
    PyJWK:
        A newly constructed PyJWK instance whose internal validation has completed and whose .key attribute is assigned by the algorithm-specific from_jwk routine.
        Edge cases:
          - This method never returns None.
          - If construction fails due to invalid input or missing dependencies it raises an exception instead of returning.

## Raises:
    InvalidKeyError:
        - If the provided obj lacks "kty" (i.e., obj.get("kty") is falsy).
        - If kty == "EC" and crv is present but not one of the supported values ("P-256", "P-384", "P-521", "secp256k1").
        - If kty == "OKP" and crv is missing.
        - If kty == "OKP" and crv is present but not "Ed25519".
        - If kty is present but not one of the supported key types ("EC", "RSA", "oct", "OKP").
    PyJWKError:
        - If the selected algorithm requires the 'cryptography' library but the runtime has no cryptography support (checked via has_crypto and requires_cryptography).
        - If no matching algorithm implementation is found in the default algorithms registry (Algorithm is unresolved).
    Any exception raised by the underlying Algorithm.from_jwk implementation:
        - Algorithm.from_jwk(self._jwk_data) is called during construction; exceptions raised there (parsing/crypto errors) propagate through this factory.

## State Changes:
    Attributes READ:
        - None on an existing PyJWK instance (this is a staticmethod that constructs a new instance).
    Attributes WRITTEN (on the returned PyJWK instance during construction):
        - _algorithms: set to the result of get_default_algorithms().
        - _jwk_data: set to the passed obj.
        - Algorithm: set to the algorithm class/object selected from the default algorithms by name.
        - key: set to the result of Algorithm.from_jwk(self._jwk_data).

## Constraints:
    Preconditions:
        - obj must be a mapping-like object providing .get(key, default) (the code uses .get extensively).
        - If algorithm is omitted, obj must contain sufficient information (either "alg", or a supported "kty" and, when required, a supported "crv") so that an algorithm name can be inferred.
        - If the chosen algorithm requires cryptography, the environment must have the cryptography dependency available (i.e., has_crypto must be True) or the call will raise PyJWKError.
    Postconditions:
        - If no exception is raised, the returned PyJWK will have a valid Algorithm assigned and its .key attribute initialized by Algorithm.from_jwk.
        - The returned object's helper properties (key_type, key_id, public_key_use) will reflect the contents of the provided obj.

## Side Effects:
    - No I/O is performed by this method itself.
    - May indirectly perform cryptographic key parsing/initialization through Algorithm.from_jwk; that routine may interact with cryptography libraries and allocate in-memory cryptographic key objects.
    - Does not mutate the passed-in obj or any existing PyJWK instances.

### `jwt.api_jwk.PyJWK.from_json` · *method*

## Summary:
Parse a JSON string containing a single JWK object and return a newly constructed PyJWK whose algorithm, key, and metadata are initialized.

## Description:
This static factory decodes the provided JSON text into a Python object and delegates creation, validation, and key construction to the dict-based factory (PyJWK.from_dict → PyJWK.__init__). Use this when a JWK is available as JSON (for example, when receiving a JWK from an external source, reading it from storage, or parsing a JWK payload) and you want a ready-to-use PyJWK for signing, verification, or inspection.

Why this is its own method:
- Centralizes json.loads + construction logic so callers don't need to duplicate parsing code.
- Provides an intention-revealing factory for JSON input (PyJWK.from_json(...)).

Typical callers / usage context:
- Application code that receives or loads a single JWK as a JSON string and needs a PyJWK instance.
- This method internally calls: PyJWK.from_dict(parsed_obj, algorithm)

## Args:
    data (str):
        JSON-encoded text representing a single JWK object (a JSON object → mapping). The decoded value must be a mapping-like object that implements .get(key, default). Passing non-str types is outside the declared signature and may behave differently.
    algorithm (annotation: None = None):
        The function signature annotates this parameter as None and defaults to None. The value is forwarded unchanged to PyJWK.from_dict, which (in its implementation) accepts an algorithm hint of type str | None. In practice, callers should pass either None or a string algorithm name (e.g., "RS256", "ES256", "EdDSA"); passing other types is forwarded and may lead to errors during construction.

## Returns:
    PyJWK:
        A newly constructed PyJWK instance. On success the returned object has:
          - _algorithms set to the default algorithms registry,
          - _jwk_data set to the decoded mapping,
          - Algorithm set to the matched algorithm implementation,
          - key initialized via Algorithm.from_jwk(self._jwk_data).
        This method never returns None; failures raise exceptions.

## Raises:
    json.JSONDecodeError:
        If data is not valid JSON (raised directly by json.loads).
    AttributeError:
        If the JSON decodes to a non-mapping value (for example, a list, number, or string) that does not implement .get, the PyJWK constructor will attempt to call .get and Python will raise AttributeError.
    InvalidKeyError:
        If the decoded mapping does not include a required "kty", contains unsupported "kty"/"crv" combinations, or otherwise violates constructor validation rules (these checks occur in PyJWK.__init__).
    PyJWKError:
        If the chosen or inferred algorithm requires the 'cryptography' package but it is not available, or if no algorithm implementation matches the chosen name in the default algorithms registry.
    Any exception raised by Algorithm.from_jwk:
        Algorithm-specific parsing/initialization errors (propagated from Algorithm.from_jwk called in the constructor) will bubble up.

## State Changes:
    Attributes READ:
        - None on an existing PyJWK instance (this is a static factory; it does not access instance attributes).
    Attributes WRITTEN:
        - On the returned PyJWK instance (via PyJWK.__init__ and Algorithm.from_jwk):
            - _algorithms: assigned to get_default_algorithms()
            - _jwk_data: assigned to the parsed mapping
            - Algorithm: assigned to the selected algorithm implementation
            - key: assigned to the result of Algorithm.from_jwk(self._jwk_data)

## Constraints:
    Preconditions:
        - data must be a JSON string that decodes to a mapping-like object (provides .get). If it decodes to a non-mapping value, construction will fail (see Raises).
        - If algorithm is None, the decoded mapping must contain either an explicit "alg" or a supported "kty" (and "crv" when required) so the constructor can infer an algorithm.
        - If the inferred algorithm requires cryptography, the runtime must have the 'cryptography' dependency available (checked via has_crypto); otherwise construction raises PyJWKError.
    Postconditions:
        - On success, the returned PyJWK has a resolved Algorithm and a cryptographic key object stored in .key; helper properties (key_type, key_id, public_key_use) reflect _jwk_data.
        - On failure, no PyJWK is returned and an exception is raised.

## Side Effects:
    - Calls json.loads (in-memory JSON parsing); no file or network I/O is performed by this method.
    - Delegates to Algorithm.from_jwk during object construction; that call may allocate cryptographic objects and call into third-party crypto libraries, which can have library-specific side effects or raise additional exceptions.

## Example (prose):
Given data = '{"kty":"RSA","n":"<base64url>","e":"AQAB"}', call PyJWK.from_json(data) to obtain a PyJWK; on success access the constructed key via returned_instance.key for signing/verification or inspect returned_instance.key_id for identifier.

### `jwt.api_jwk.PyJWK.key_type` · *method*

## Summary:
Returns the JSON Web Key (JWK) "kty" (key type) value from the object's internal JWK data, or None if that field is absent — does not modify object state.

## Description:
This accessor exposes the JWK "kty" member stored inside the instance's internal JWK dictionary. It is intended for callers that need to inspect the key type (for example, to select an algorithm, validate key compatibility, or route handling based on key family).

Known callers and context:
- Any code that needs the JWK's "kty" value to decide algorithm selection or key-handling logic will call this method. Within a JWK-processing lifecycle, it is typically invoked after the PyJWK instance has been constructed/loaded and before constructing or validating a cryptographic key from the JWK contents.

Why this is its own method:
- Encapsulates access to the underlying JWK storage and centralizes the retrieval semantics (returns None when "kty" is missing).
- Improves readability where callers need to query the key type without exposing or duplicating access to the raw _jwk_data structure.

## Args:
None.

## Returns:
- type: str | None
- Description: The value of the "kty" field from the instance's internal JWK data if present; otherwise None.
- Possible example values: "RSA", "EC", "oct", "OKP" (these are common JWK key types defined by the JWK specification). The method does not validate or normalize this string — it returns the stored value verbatim.

## Raises:
- AttributeError: If self._jwk_data is not a mapping-like object that implements .get, calling this method will raise an AttributeError when attempting to access .get.
- (No method-specific exceptions are raised by the implementation itself.)

## State Changes:
- Attributes READ:
    - self._jwk_data
- Attributes WRITTEN:
    - None (the method is read-only and does not modify self or external state)

## Constraints:
- Preconditions:
    - The instance must have an attribute _jwk_data that behaves like a mapping (supports .get(key, default)). Typical implementations set this to a dict-like object holding JWK members.
    - _jwk_data should be populated (constructed or loaded) before calling this method if callers expect a non-None key type.
- Postconditions:
    - After the call, the instance state is unchanged.
    - The return is either the raw string stored under "kty" in _jwk_data, or None if that key is absent.

## Side Effects:
- None (no I/O, no external service interaction, no mutation of objects outside self).

### `jwt.api_jwk.PyJWK.key_id` · *method*

## Summary:
Return the value of the JWK "kid" (key identifier) stored in the instance's internal JWK mapping, or None if no "kid" entry exists. This is a read-only accessor and does not modify the object's state.

## Description:
Reads and returns the "kid" entry from self._jwk_data via its mapping .get method. Typical call sites are key-loading, JWK set handling, or JWT verification preparation where the key identifier is used to select or match a key. This logic is an accessor to encapsulate access to the underlying mapping and keep callers from depending on the internal representation.

Known callers and invocation context:
- No specific callers are present in the provided context. In normal use, callers call this after a PyJWK instance is created or parsed to obtain the key identifier for matching, selection, or metadata purposes.

Why this is a separate method:
- Provides a stable, single point to access the "kid" value so future changes to storage or computation of the key identifier do not require modifications across call sites.

## Args:
- None

## Returns:
- str | None: The value returned by self._jwk_data.get("kid", None).
  - By JWK convention this value should be a string; callers should treat the return value as an Optional[str].

## Raises:
- AttributeError: If the instance lacks a self._jwk_data attribute or if self._jwk_data is None or otherwise does not provide a .get method. This arises from attempting to call self._jwk_data.get("kid", None).

## State Changes:
- Attributes READ:
    - self._jwk_data
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - For normal operation, self._jwk_data must be present and mapping-like (for example, a dict).
- Postconditions:
    - No mutation of self or external objects.
    - The return value equals the result of self._jwk_data.get("kid", None) at the time of the call.

## Side Effects:
- None: this method performs no I/O, calls no external services, and does not modify any objects.

### `jwt.api_jwk.PyJWK.public_key_use` · *method*

## Summary:
Return the JWK "use" parameter (as stored in the object's underlying JWK dictionary), or None if it is not present.

## Description:
This accessor reads the internal JWK representation and exposes the "use" member (the JWK public key use). It is used whenever consumers need to inspect whether the key was intended for a particular use (e.g., signature vs. encryption) without exposing the entire internal dictionary.

Known callers and context:
- Called by any code that needs to inspect a PyJWK instance's declared usage; typical call sites are key-selection or validation steps in JWT verification or key management pipelines.
- Invoked during key inspection stages (for example, when filtering a JWK set to select keys appropriate for a requested operation).

Why this is its own method:
- Encapsulates direct access to the internal _jwk_data mapping so callers do not depend on the underlying data structure layout.
- Centralizes access logic (single place to adjust behavior if the internal representation changes), improving maintainability and testability.

## Args:
    None

## Returns:
    str | None: The value of the "use" member from the internal JWK data if present; otherwise None.
    - Typical values (per JWK conventions, not enforced by this method): "sig" (signature) or "enc" (encryption).
    - Edge case: returns None when the "use" key is absent from the underlying dictionary.

## Raises:
    None

## State Changes:
Attributes READ:
    - self._jwk_data

Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - self._jwk_data must be a mapping (e.g., dict-like) that supports .get(key, default).
    - The PyJWK instance must be properly initialized such that _jwk_data exists.

Postconditions:
    - No mutation of self or external objects occurs.
    - The returned value equals the result of self._jwk_data.get("use", None).

## Side Effects:
    - None: this method performs no I/O, no network calls, and does not modify objects outside of the method.

## `jwt.api_jwk.PyJWKSet` · *class*

## Summary:
Represents a JSON Web Key Set (JWK Set) — a collection of usable PyJWK objects created from an input list or JSON object. Primary responsibility is to validate the incoming JWK set, construct PyJWK instances for each usable key, and provide keyed access to those PyJWKs by their key ID ("kid").

## Description:
PyJWKSet is a thin container abstraction around one or more PyJWK instances. Instantiate PyJWKSet when you have a JWK Set (a mapping with a "keys" list or a JSON-encoded JWK Set) and you want a validated, ready-to-use collection of PyJWK objects for use in verification or key lookup.

Typical construction patterns:
- Direct construction with a list of JWK mappings: PyJWKSet(keys_list)
- Using the factory that accepts a dictionary: PyJWKSet.from_dict(obj)
- Using the factory that accepts a JSON string: PyJWKSet.from_json(json_text)

Motivation and responsibility boundary:
- Responsibility: Validate that the incoming JWK Set container is structurally valid, construct PyJWK instances for each individual JWK that can be successfully turned into a PyJWK, and surface a collection of usable keys. Provide lookup by "kid".
- Not responsible for: cryptographic parsing/validation beyond what PyJWK performs; persistent storage; key rotation workflows. Cryptographic construction and algorithm-specific errors are delegated to PyJWK and the underlying algorithm implementations.

## State:
Attributes (instance-level)
- keys: list[PyJWK]
    - Type: list containing PyJWK instances.
    - Invariant: after successful construction, this list is non-empty and contains only PyJWK objects that were successfully constructed from the input JWK entries.
    - Visibility: public attribute; callers may iterate over it or index into it directly.

Constructor parameters (inputs to __init__)
- keys (list[JWKDict])
    - Expected type: list (specifically a Python list) of JWK mapping objects (JWKDict).
    - Constraints:
        - Must be truthy (non-empty). If falsy (None, empty list, empty container), construction raises PyJWKSetError.
        - Must be an actual list instance; passing other sequence types (tuple, set, generator) that are truthy will raise PyJWKSetError with message "Invalid JWK Set value".
        - Elements should be mapping-like JWK objects (objects supporting .get). Each element is passed to PyJWK for construction; elements that cause PyJWK to raise PyJWTError are skipped.

Class invariants (post-construction)
- self.keys is a non-empty list of PyJWK objects.
- Every element in self.keys was produced by a successful PyJWK(...) call (i.e., PyJWK did not raise a PyJWTError for that element).
- If no input keys were usable (all elements failed PyJWK construction), construction fails with PyJWKSetError.

## Lifecycle:
Creation
- Direct:
    - Call PyJWKSet(keys_list) where keys_list is a non-empty list of JWK mapping objects.
    - Behavior:
        1) If keys is falsy: raise PyJWKSetError("The JWK Set did not contain any keys").
        2) If keys is not an instance of list: raise PyJWKSetError("Invalid JWK Set value").
        3) Iterate over keys; for each element call PyJWK(element). If PyJWK raises PyJWTError for an element, that element is skipped.
        4) If after iteration self.keys is empty: raise PyJWKSetError("The JWK Set did not contain any usable keys. Perhaps 'cryptography' is not installed?").
- From dict:
    - Call PyJWKSet.from_dict(obj) where obj is a mapping; this pulls obj.get("keys", []) and delegates to the constructor.
- From JSON:
    - Call PyJWKSet.from_json(json_str); this parses JSON with json.loads(json_str) (JSONDecodeError can propagate) and delegates to from_dict.

Usage
- Key lookup by kid:
    - Use indexing syntax pyjwkset[kid] which returns the first PyJWK in self.keys whose key_id equals the provided kid string.
    - If no matching key is found, a KeyError is raised with message "keyset has no key for kid: {kid}".
- Direct iteration/access:
    - Callers may iterate over pyjwkset.keys or index into that list directly to enumerate available keys.

Destruction / Cleanup
- PyJWKSet holds in-memory references to PyJWK objects; there is no explicit cleanup, context manager, or close() API. Any resource management required by underlying cryptographic objects must be handled by those objects themselves.

## Method Map:
flowchart LR
    A[PyJWKSet.from_json(data:str)] --> B[json.loads(data) -> obj:dict]
    B --> C[PyJWKSet.from_dict(obj:dict)]
    C --> D[PyJWKSet.__init__(keys:list)]
    D --> E[validate keys truthiness -> raise PyJWKSetError if falsy]
    D --> F[validate isinstance(keys, list) -> raise PyJWKSetError if not list]
    D --> G[for each key in keys: try PyJWK(key) -> on success append to self.keys; on PyJWTError skip]
    G --> H[if self.keys empty -> raise PyJWKSetError]
    I[pyjwkset.__getitem__(kid:str)] --> J[iterate self.keys and return first where key.key_id == kid]
    J --> K[if no match -> raise KeyError]

## Raises:
Exceptions that can be raised directly by PyJWKSet methods and the conditions that trigger them:
- PyJWKSetError
    - Raised by __init__ when the provided keys parameter is falsy (empty list, None, etc.).
      Message: "The JWK Set did not contain any keys"
    - Raised by __init__ when the provided keys parameter is not a list instance.
      Message: "Invalid JWK Set value"
    - Raised by __init__ when the input list exists but none of the entries produced a usable PyJWK (every element raised PyJWTError during PyJWK construction).
      Message: "The JWK Set did not contain any usable keys. Perhaps 'cryptography' is not installed?"
- KeyError
    - Raised by __getitem__ when no PyJWK in self.keys has a key_id equal to the requested kid.
      Message: "keyset has no key for kid: {kid}"
- json.JSONDecodeError
    - May be raised by from_json if the provided JSON string is malformed (propagated from json.loads).
- PyJWTError (and its subclasses)
    - Not raised directly by the PyJWKSet constructor in normal flow because individual PyJWK construction exceptions are caught and cause skipping; however:
        - If a caller passes an element to the constructor that leads to an AttributeError (e.g., element lacking .get), that exception may propagate.
        - Any exceptions from PyJWK.from_dict/from_json or Algorithm.from_jwk are handled per PyJWK's behavior; PyJWKSet itself only catches PyJWTError during per-key construction.

## Example:
- Create from a dict-like JWK Set:
    - Given a mapping: jwks = {"keys": [ {"kty":"RSA","n":"...","e":"AQAB","kid":"rsa1"}, {"kty":"oct","k":"...","kid":"sym1"} ]}
    - Construct: pyjwkset = PyJWKSet.from_dict(jwks)
    - Lookup by kid: rsa_key = pyjwkset["rsa1"]  # returns a PyJWK instance
    - Iterate available keys: for pyjwk in pyjwkset.keys: do_something(pyjwk)

- Create from JSON:
    - json_text = '{"keys":[{"kty":"RSA","n":"...","e":"AQAB","kid":"rsa1"}]}'
    - Construct: pyjwkset = PyJWKSet.from_json(json_text)  # may raise JSONDecodeError if json_text invalid

Notes and implementation hints:
- The constructor deliberately filters out individual JWKs that fail to construct as PyJWK instances; this makes the container resilient to partially malformed sets.
- The code requires the keys parameter to be an actual Python list instance; other iterables are rejected.
- The error message about 'cryptography' in the final PyJWKSetError is informative: often PyJWK construction fails for algorithm implementations that require optional crypto dependencies.

### `jwt.api_jwk.PyJWKSet.__init__` · *method*

## Summary:
Initialize the PyJWKSet instance by validating a provided list of JWK mappings, constructing PyJWK wrappers for each usable key, and storing the resulting PyJWK objects on the instance.

## Description:
This constructor accepts a sequence of JWK dictionary objects (a JWK Set's "keys" list), validates the container, and attempts to convert each entry to a PyJWK. It performs three distinct checks in order:
1. Ensures the caller supplied a truthy value for keys (non-empty).
2. Ensures the supplied value is a list instance.
3. Iterates the list and constructs PyJWK(key) for each entry, silently skipping entries that raise PyJWTError during PyJWK construction.

Typical callers and lifecycle context:
- Callers are routines that have parsed or otherwise obtained a JWK Set (for example: configuration loaders, remote JWKS fetchers, or token-verification setup code). Those callers pass the JWK Set's "keys" list into this constructor to obtain an object containing usable cryptographic key wrappers.
- This constructor is invoked during the setup phase where keys are normalized/validated prior to use for signature verification or key selection.

Reason for separate constructor logic:
- Construction, validation, and filtering of multiple JWK entries is a distinct responsibility from a single-key PyJWK. Grouping this logic in the PyJWKSet constructor centralizes JWK Set-level validation and produces a predictable, ready-to-use collection of PyJWK objects for the rest of the library to consume.

## Args:
    keys (list[JWKDict]):
        - Required. A Python list of JWK mappings (each mapping is a JWKDict).
        - Must be a list instance (not a tuple or other sequence).
        - Must be non-empty (a falsy value or empty list triggers a PyJWKSetError).
        - Each element is forwarded to PyJWK(element) for per-key validation and construction.
        - Note: elements that are syntactically invalid JWKs or unsupported keys may cause PyJWK to raise PyJWTError; those elements are skipped. Other exception types raised by PyJWK (e.g., AttributeError if an element lacks mapping semantics) will propagate.

## Returns:
    None
    - On success: the instance (self) is initialized and self.keys contains a non-empty list of PyJWK instances (one per usable entry).
    - The constructor does not return a value; successful construction is indicated by no exception being raised and self.keys populated.

## Raises:
    PyJWKSetError("The JWK Set did not contain any keys")
        - Trigger: keys is falsy (e.g., None, empty list, empty sequence evaluated as False).
        - Happens before type-checking the container type.

    PyJWKSetError("Invalid JWK Set value")
        - Trigger: keys is truthy but not an instance of list (e.g., a dict, tuple, or other container).

    PyJWKSetError("The JWK Set did not contain any usable keys. Perhaps 'cryptography' is not installed?")
        - Trigger: keys is a list but, after attempting to construct PyJWK for every element, zero usable PyJWK objects were appended to self.keys.
        - Typical cause: all entries were invalid or their construction required optional cryptography dependencies that are not available; the message hints at that possibility.

    Any exception raised by PyJWK construction that is not a subclass of PyJWTError
        - Trigger: if PyJWK(key) raises an exception type other than PyJWTError (for example AttributeError or TypeError due to a malformed element), that exception will propagate and abort construction. Only PyJWTError (and subclasses) are caught and treated as "skip this key".

## State Changes:
    Attributes READ:
        - None of the instance's prior attributes are read by this method.

    Attributes WRITTEN:
        - self.keys is set to an empty list at start of the constructor.
        - self.keys is appended with PyJWK instances for each successfully constructed key (preserves the original order for usable keys).
        - On successful return, self.keys contains at least one PyJWK instance.

## Constraints:
    Preconditions:
        - Caller must pass a non-empty list object (list[JWKDict]). Passing a falsy value or a non-list will raise PyJWKSetError.
        - Each list element should be a mapping-like JWK representation acceptable to PyJWK (e.g., has .get or dict-like access). If an element is not mapping-like, PyJWK may raise an error that will propagate.
        - The environment should provide any optional cryptography dependencies required by algorithms used by PyJWK if those algorithms are present in the input JWKs; otherwise those keys may be skipped, potentially causing the final error described below.

    Postconditions:
        - On success (no exception), self.keys is a non-empty list where every element is a successfully-constructed PyJWK instance.
        - On failure (exceptions described above), the instance is not guaranteed to be fully usable; an exception will have been raised and no guarantee is made about self.keys contents beyond the fact it was set during the attempt.

## Side Effects:
    - No file or network I/O is performed directly by this constructor.
    - Creating each PyJWK(key) can have side effects: algorithm selection and key material parsing (which may import optional crypto libraries or perform CPU work). Those effects occur during the loop and are visible to the process (e.g., importing cryptography if required by a key's algorithm).
    - The constructor swallows PyJWTError exceptions raised by individual PyJWK constructions to allow other entries to be considered; only non-PyJWTError exceptions propagate.
    - No mutation is performed on the supplied keys list itself; elements are read but not modified.

### `jwt.api_jwk.PyJWKSet.from_dict` · *method*

## Summary:
Create a PyJWKSet instance from a dictionary containing a "keys" entry, returning a PyJWKSet whose keys attribute contains the usable PyJWK objects constructed from the provided key dicts.

## Description:
Known callers and usage contexts:
- PyJWKSet.from_json uses this method after parsing a JSON JWKS payload; this is typically invoked when loading a JWKS fetched from an authorization server or read from configuration.
- External callers that deserialize a JWKS (JSON Web Key Set) into a Python dict and want a PyJWKSet instance should call this method.

Why this is a separate method:
- Encapsulates the mapping from a deserialized JWKS dict to the library's PyJWKSet abstraction.
- Keeps JSON parsing (from_json) and dict→object conversion separate for clarity and reuse.
- Provides a single, documented entry point for creating a PyJWKSet from in-memory data without duplicating constructor-call logic.

## Args:
    obj (dict[str, Any]):
        A dictionary representation of a JWK Set (JWKS). Expected to contain a "keys" member whose value should be a list of JWK dictionaries (each JWK typically follows RFC 7517).
        - If "keys" is missing, the method will pass an empty list to the constructor (which will raise a PyJWKSetError).
        - If "keys" is present but not a list, the constructor will raise a PyJWKSetError indicating an invalid JWK Set.

## Returns:
    PyJWKSet:
        A newly constructed PyJWKSet instance whose .keys attribute is a list of PyJWK objects created from the supplied key dicts.
        - The returned PyJWKSet will contain only "usable" PyJWK objects; key entries that fail PyJWK construction are silently skipped by the constructor.
        - This method never returns None; it either returns a PyJWKSet or raises an exception.

## Raises:
    PyJWKSetError:
        - If the "keys" value is empty or missing (the constructor raises: "The JWK Set did not contain any keys").
        - If the "keys" value is not a list (the constructor raises: "Invalid JWK Set value").
        - If the provided list contains no usable keys after filtering invalid/unusable entries (the constructor raises: "The JWK Set did not contain any usable keys. Perhaps 'cryptography' is not installed?").
    Any other exceptions raised by calling code (e.g., AttributeError or TypeError) may occur if a non-dict-like object is passed as obj (this method calls obj.get("keys", [])).

Notes on exceptions:
- When the constructor iterates the "keys" list it attempts to build PyJWK(key) for each entry; PyJWK construction failures raise PyJWTError which the constructor catches and ignores for that entry. Thus invalid key entries do not propagate as exceptions from from_dict; they are filtered out. Only the constructor's final validations raise PyJWKSetError.

## State Changes:
Attributes READ:
    None (staticmethod — does not read any self attributes).

Attributes WRITTEN:
    None (this static method does not modify any existing object). 
    Note: it constructs and returns a new PyJWKSet whose constructor will set that instance's attributes (specifically, .keys).

## Constraints:
Preconditions:
    - obj must be a dict-like mapping with a get method (ideally dict[str, Any]).
    - Each element of obj["keys"] (if present) should be a JWK dictionary acceptable to PyJWK (conforming to expected fields such as "kty", "kid", etc.) to be turned into a usable PyJWK.

Postconditions:
    - On success, returns a PyJWKSet whose .keys is a non-empty list of PyJWK objects (guaranteed by the constructor).
    - If preconditions are not met or no usable keys remain, a PyJWKSetError is raised and no PyJWKSet is returned.

## Side Effects:
    - No I/O or network calls are performed by this method itself.
    - Side effects occur via the PyJWKSet constructor: construction of PyJWK objects (which may perform cryptographic checks/initialization and may depend on optional libraries such as 'cryptography').
    - Invalid key entries may be logged or ignored depending on PyJWK implementation; this method does not log or emit warnings itself.

### `jwt.api_jwk.PyJWKSet.from_json` · *method*

## Summary:
Parses a JSON-formatted JWK Set and returns a new PyJWKSet instance whose keys attribute is populated with usable PyJWK objects (or raises if none are usable).

## Description:
Converts the provided JSON text into a Python object and delegates to the class helper that constructs a PyJWKSet from the resulting mapping.

Known callers:
    - No direct callers are present in the provided class source. Typical callers (outside this file) are code that:
        * Fetches a JWKS (JSON Web Key Set) document from a JWKS HTTP endpoint, configuration file, or discovery document, and needs to construct a PyJWKSet from the HTTP response body or file contents.
        * Runs during key discovery/initialization or when refreshing keys used to verify/validate JWTs.

Why this is a separate method:
    - Convenience and single responsibility: it isolates JSON parsing from object construction so callers can either provide a parsed dict (via from_dict) or raw JSON text (via from_json). Keeping JSON parsing here centralizes error handling and makes higher-level code simpler.

## Args:
    data (str):
        The JSON text representing a JWK Set. Expected to decode to a JSON object (mapping) that may contain a "keys" member. The method calls json.loads(data) — if a non-string/non-bytes value is passed, json.loads may raise TypeError.

## Returns:
    PyJWKSet:
        A newly-constructed PyJWKSet instance. On success, the returned object's .keys attribute is a non-empty list of PyJWK instances (each representing a usable key).
        The method does not return None; it either returns a valid PyJWKSet or raises an exception.

## Raises:
    json.JSONDecodeError:
        If the `data` string is not valid JSON, json.loads raises this error.

    TypeError:
        If `data` is not an acceptable type for json.loads (for example, passing an unexpected Python type), json.loads may raise TypeError.

    AttributeError:
        If the decoded JSON is not a mapping/object (for example, a JSON array), PyJWKSet.from_dict expects a mapping and will attempt to call .get on the decoded value; that will raise AttributeError.

    PyJWKSetError:
        Propagated from the class constructor / from_dict in the following conditions:
            - The decoded mapping does not contain a "keys" list (i.e., "keys" missing or falsy) -> "The JWK Set did not contain any keys".
            - The "keys" value is present but is not a list -> "Invalid JWK Set value".
            - All entries in the provided keys list are unusable (e.g., parsing each key raised PyJWTError) -> "The JWK Set did not contain any usable keys. Perhaps 'cryptography' is not installed?"

    Other exceptions:
        Unexpected exceptions raised during construction of individual PyJWK objects are caught in PyJWKSet.__init__ when they are of type PyJWTError (those are ignored for that key). Other exception types raised by PyJWK constructor would propagate unless caught elsewhere.

## State Changes:
Attributes READ:
    - None on an existing PyJWKSet instance (this is a static method and does not read instance attributes).

Attributes WRITTEN:
    - None on an existing PyJWKSet instance.

New-object state written:
    - The returned PyJWKSet instance will have its `.keys` attribute set to a list of PyJWK objects corresponding to usable entries in the input "keys" list.

## Constraints:
Preconditions:
    - `data` must be valid JSON text.
    - The decoded JSON must be a mapping/object (so that .get("keys", []) is available).
    - If the mapping contains "keys", its value should be a list of JWK-like dictionaries for successful construction.

Postconditions:
    - If the call returns successfully, the returned PyJWKSet contains at least one usable PyJWK in `.keys`.
    - If the JSON was invalid, or the decoded object does not meet the expected structure, an exception as described in Raises will be thrown and no PyJWKSet will be returned.

## Side Effects:
    - No network or filesystem I/O is performed.
    - The method performs CPU-bound work (JSON parsing and PyJWK object construction).
    - No global state is mutated. Only the newly-created PyJWKSet instance is populated.

### `jwt.api_jwk.PyJWKSet.__getitem__` · *method*

## Summary:
Return the PyJWK instance in this JWK set whose kid equals the provided identifier; performs a linear search and does not modify the set.

## Description:
This method is the canonical lookup routine for resolving a key by its 'kid' within a previously constructed PyJWKSet. Typical callers and contexts:
- JWT verification logic that receives a JWK Set (JWKS) and needs to pick the correct signing/verification key based on the JWT header's "kid".
- Any JWKS consumer that indexes a PyJWKSet with square-bracket syntax (e.g., keyset[kid]) to retrieve a prepared PyJWK object for signing, verification, or inspection.

Why this logic is its own method:
- Implements the Python mapping-like access pattern (supporting keyset[kid]) and centralizes the lookup behavior and error message.
- Keeps lookup semantics consistent and isolated (single place to change search behavior, error text, or future caching strategies) rather than duplicating the loop at call sites.

## Args:
    kid (str): The key identifier to search for. Must be the same string form used when the contained PyJWK objects were created (comparison is equality-based and case-sensitive). No default; required.

## Returns:
    PyJWK: The first PyJWK instance from self.keys whose key_id attribute equals kid.
    Edge cases:
      - If multiple entries have the same key_id, the first matching PyJWK in self.keys (iteration order) is returned.
      - If a match exists, the returned object is the exact stored instance (no copy).

## Raises:
    KeyError: Raised when no PyJWK in self.keys has key_id equal to the provided kid. The message is exactly: "keyset has no key for kid: {kid}" where {kid} is replaced by the argument.
    AttributeError: May propagate if an element of self.keys does not expose a key_id attribute (this indicates an internal invariant violation; PyJWKSet normally contains PyJWK instances so this should not occur in correct construction).

## State Changes:
    Attributes READ:
      - self.keys (iterated)
      - For each candidate key: key.key_id (read to perform the comparison)
    Attributes WRITTEN:
      - None (the method performs no mutation of self or of contained keys)

## Constraints:
    Preconditions:
      - The PyJWKSet must have been constructed successfully and self.keys should be an iterable (typically a list) of PyJWK instances or objects exposing a key_id attribute.
      - kid should be provided as a str (the method's annotation expects a string and comparisons are string-equality).
    Postconditions:
      - If the method returns, the returned PyJWK is an element of self.keys and returned.key_id == kid.
      - If the method raises KeyError, self.keys remains unchanged.

## Side Effects:
    - None. The method performs no I/O, no external service calls, and does not mutate external objects or the PyJWKSet instance.

## `jwt.api_jwk.PyJWTSetWithTimestamp` · *class*

## Summary:
A minimal container that pairs a PyJWKSet instance with a monotonic timestamp captured at construction.

## Description:
PyJWTSetWithTimestamp is used to associate a retrieval/creation time with a PyJWKSet so callers (for example, caches or rotation logic) can determine the age of a JWK set and decide when to refresh it. The class does not validate, copy, or otherwise transform the provided jwk_set — it stores a reference and records the monotonic time at which the container was created.

Instantiate this class when you already have a validated PyJWKSet (see PyJWKSet.from_dict/from_json or direct construction) and you want to retain both the set and the moment it was obtained for TTL, expiry, or rotation decisions.

## State:
- Attributes (instance-level)
    - jwk_set (PyJWKSet)
        - Type: PyJWKSet (type-hinted in source).
        - Meaning: a reference to the JWK set being tracked.
        - Valid values: any object may be assigned by the caller; code does not enforce runtime type checks. Callers should pass a properly constructed PyJWKSet for correct semantics.
        - Mutability: public and mutable — callers can read or replace this attribute after construction; such changes are visible through get_jwk_set().
    - timestamp (float)
        - Type: float
        - Meaning: monotonic timestamp captured at construction using time.monotonic().
        - Units: seconds (monotonic clock). Useful only for elapsed time calculations; not comparable to wall-clock time (time.time()).
        - Mutability: public attribute set at construction; although writable by callers, the class itself sets it only once during __init__.

- Class invariants:
    - Immediately after construction, get_jwk_set() returns the same object passed as jwk_set.
    - Immediately after construction, get_timestamp() returns a float equal to the value of time.monotonic() taken during __init__.
    - The class does not itself enforce or maintain further invariants (e.g., it does not validate the jwk_set contents).

## Lifecycle:
- Creation:
    - Required parameter: jwk_set — the PyJWKSet instance to associate with a timestamp.
    - On construction, the object stores the passed jwk_set reference and records the current monotonic time: self.timestamp = time.monotonic().
    - No validation or type enforcement is performed by the constructor.
- Usage:
    - get_jwk_set(): returns the stored jwk_set reference. Use the returned PyJWKSet according to its API (lookup by kid, iterate keys, etc.).
    - get_timestamp(): returns the recorded monotonic timestamp (float). Compute elapsed time as time.monotonic() - get_timestamp().
    - Typical sequence: construct the container, later call get_timestamp() and/or get_jwk_set() in any order. There is no required call ordering beyond construction first.
- Destruction / Cleanup:
    - No explicit cleanup API. Object lifecycle follows normal Python garbage collection. If the underlying PyJWKSet requires resource management, that is its responsibility.

## Method Map:
flowchart LR
    A[__init__(jwk_set)] --> B[set self.jwk_set = jwk_set]
    A --> C[set self.timestamp = time.monotonic()]
    B --> D[get_jwk_set() returns self.jwk_set]
    C --> E[get_timestamp() returns self.timestamp]

## Raises:
- The class does not raise application-level exceptions during normal operation.
- No explicit checks in __init__ imply no PyJWKSet-specific exceptions are thrown by this class.
- Only runtime exceptions from Python itself (e.g., MemoryError) could occur; those are not specific to this implementation.

## Example:
- Use-case: caching a JWK set with TTL-based eviction.
    1) Given pyjwkset (a PyJWKSet instance), create the container:
       container = PyJWTSetWithTimestamp(pyjwkset)
    2) Store container in cache.
    3) Later, to check staleness, compute:
       elapsed = time.monotonic() - container.get_timestamp()
       if elapsed > ttl_seconds:
           refresh the JWK set
    4) Access the underlying keys via:
       pyjwkset = container.get_jwk_set()
       # then use pyjwkset.lookup or iteration per PyJWKSet API

Notes:
- Because timestamp is taken with time.monotonic(), it is safe against system clock adjustments but only meaningful for elapsed-time comparisons.
- This class intentionally remains small and does not attempt to encapsulate or protect the provided PyJWKSet from mutation by callers.

### `jwt.api_jwk.PyJWTSetWithTimestamp.__init__` · *method*

## Summary:
Stores a reference to a PyJWKSet on the instance and records the creation time using a monotonic clock.

## Description:
Initializes the container that pairs a JWK set with the monotonic timestamp at which the container was created.

Known callers and context:
- Typically instantiated by caching, key-rotation, or JWK-fetching code paths immediately after a PyJWKSet is obtained (for example, after calling PyJWKSet.from_dict or PyJWKSet.from_json).
- Used in lifecycle stages where callers need to track age/staleness of a JWK set (e.g., TTL checks, refresh/rotation decisions).

Why this is its own method:
- The constructor encapsulates the minimal, atomic operation of associating a JWK set with the moment it was observed. Keeping timestamp capture and storage together ensures callers get a reliable, consistent timestamp taken as close as possible to the time the JWK set was acquired, rather than relying on callers to duplicate this logic.

## Args:
    jwk_set (PyJWKSet):
        A PyJWKSet instance to be stored by reference. No runtime type enforcement is performed by this constructor; callers should pass a properly constructed PyJWKSet for correct semantics.
        - Allowed values: any object, but semantics assume a PyJWKSet.
        - Default: none (required positional argument).

## Returns:
    None
    - As a constructor, it does not return a value; it initializes instance attributes.

## Raises:
    - No application-level exceptions are raised by this constructor.
    - Runtime exceptions from the Python runtime (e.g., MemoryError) or from time.monotonic() are the only possible failures; the constructor does not explicitly raise or catch exceptions.

## State Changes:
    Attributes READ:
        - (none) The constructor does not read existing instance attributes.

    Attributes WRITTEN:
        - self.jwk_set (PyJWKSet): set to the provided jwk_set reference.
        - self.timestamp (float): set to the value returned by time.monotonic() at construction.

## Constraints:
    Preconditions:
        - The caller should have obtained or constructed a valid PyJWKSet prior to calling this constructor if they expect the stored jwk_set to be usable.
        - No attribute on self is required to have any particular value before calling __init__ (standard object construction).

    Postconditions:
        - After the call, self.jwk_set refers to the exact object passed as jwk_set (no copy or validation performed).
        - After the call, self.timestamp holds a float value equal to the monotonic clock reading taken during construction (time.monotonic()).
        - No additional validation or mutation of jwk_set is performed by this constructor.

## Side Effects:
    - Calls time.monotonic() to capture a monotonic timestamp (no I/O or external network calls).
    - Stores a direct reference to the provided jwk_set; because the stored object is not copied, subsequent mutations to the jwk_set by external code are visible through this instance.

### `jwt.api_jwk.PyJWTSetWithTimestamp.get_jwk_set` · *method*

## Summary:
Return the PyJWKSet object stored on this instance without modifying the instance state.

## Description:
This is a simple accessor that returns the exact object assigned to self.jwk_set in the constructor. There are no callers defined inside this class; external code that needs the stored JWK set can call this method to obtain the reference.

Why this is a separate method:
- Provides a stable, explicit public accessor for the stored JWK set.
- Keeps the public API consistent with the paired get_timestamp accessor and centralizes future changes (for example, adding validation or defensive copying) in one place.

## Args:
- None

## Returns:
- PyJWKSet
    - The same object reference that was passed to PyJWTSetWithTimestamp.__init__ and stored on self.jwk_set.
    - No validation, copying, or transformation is performed; the returned reference is exactly the stored value.

## Raises:
- None

## State Changes:
- Attributes READ:
    - self.jwk_set
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - The PyJWTSetWithTimestamp instance must have been constructed (its __init__ initializes self.jwk_set).
    - Callers should treat the returned object according to the expected PyJWKSet contract; this method does not perform runtime type checks.
- Postconditions:
    - No attributes on self are modified by this call.
    - The return value equals the current value of self.jwk_set.

## Side Effects:
- None: no I/O, no external calls, and no mutation of the PyJWTSetWithTimestamp instance.

## Example:
- Given an instance p of PyJWTSetWithTimestamp constructed with a PyJWKSet value, p.get_jwk_set() returns that same PyJWKSet object (by reference).

### `jwt.api_jwk.PyJWTSetWithTimestamp.get_timestamp` · *method*

## Summary:
Returns the stored monotonic timestamp captured when the PyJWTSetWithTimestamp instance was created, without modifying any object state.

## Description:
This method provides read-only access to the timestamp recorded in the instance's constructor. The timestamp is captured using time.monotonic() during PyJWTSetWithTimestamp.__init__ and represents a monotonic clock value (seconds as a float) used to measure elapsed time relative to the instance creation.

Known callers and usage context:
- No direct callers are present in the immediate module definition. The method is intended to be used by any code that needs the original creation timestamp for the PyJWKSet instance, for example to compute elapsed time since the set was loaded or to implement caching/expiry policies that rely on monotonic time.
- Typical lifecycle: invoked after a PyJWTSetWithTimestamp object is constructed and stored, when a consumer needs the creation time (e.g., during validation, refresh, or logging steps).

Purpose of having this logic as a separate method:
- Encapsulates access to the stored timestamp so callers need not know the internal attribute name.
- Keeps reads of the timestamp explicit and testable; separating this accessor simplifies mocking or overriding in subclasses or tests.

## Args:
None.

## Returns:
float
- The value is the same float assigned to self.timestamp in __init__, which originates from time.monotonic().
- Units and meaning: seconds (fractional), monotonic clock reference; useful for computing elapsed durations by subtraction (e.g., time.monotonic() - returned_value).
- Edge cases: returns the original float even if the system clock changes; monotonic semantics mean the value cannot be used to determine wall-clock absolute time.

## Raises:
None. This accessor does not raise exceptions in normal operation. It will raise an AttributeError only if called on an incompletely-initialized instance that lacks the timestamp attribute (i.e., if __init__ was not run).

## State Changes:
Attributes READ:
- self.timestamp

Attributes WRITTEN:
- None. This method does not modify any attributes.

## Constraints:
Preconditions:
- The instance must have been initialized (PyJWTSetWithTimestamp.__init__ must have executed) so that self.timestamp exists and holds a float.
Postconditions:
- self.timestamp remains unchanged.
- The returned float is equal to self.timestamp at the time of call.

## Side Effects:
- None. The method performs no I/O, no external service calls, and does not mutate objects outside of self.

