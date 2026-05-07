# `PyJWT`

## Tree:
PyJWT/
├── docs/                      # Sphinx documentation helpers and build-time utilities
│   └── conf.py                # Small helpers used by Sphinx: read() and find_version()
└── jwt/                       # Core library package implementing JWT/JWS APIs
    ├── api_jwt.py             # High-level JWT API (PyJWT: JSON payload handling, claim validation)
    ├── api_jws.py             # Low-level JWS API (PyJWS: compact serialization/parsing, alg registry)
    ├── algorithms/            # (Pluggable) Algorithm implementations — prepare_key, sign, verify
    ├── exceptions.py          # JWT/JWS-specific exception classes referenced by API
    └── __init__.py            # Package exports / convenience wrappers (may expose top-level encode/decode)

Notes:
- The tree shows the top-level organization two levels deep. The algorithms/ folder and exceptions.py are required responsibilities but their exact internal filenames/implementations can vary across releases.
- Known modules and components documented elsewhere:
  - docs.conf.read, docs.conf.find_version (see docs module documentation in memory)
  - jwt.api_jws.PyJWS and its methods: encode, decode, decode_complete, register_algorithm, unregister_algorithm, get_unverified_header (detailed component docs available)
  - jwt.api_jwt.PyJWT and its methods: encode, decode, decode_complete (detailed component docs available)

## Purpose:
- Problem this repository solves:
  - Provide a Python library to produce and consume JSON Web Tokens (JWT) and JSON Web Signatures (JWS) safely, with a focus on correct base64url handling, header normalization, pluggable cryptographic algorithms, and claim validation.
- Why it matters:
  - JWTs are widely used for stateless authentication and secure data exchange; this library reduces developer mistakes by centralizing encoding/decoding semantics and validations.
- Target users and scenarios:
  - Application developers implementing authentication middleware, API backends issuing tokens, and framework integrations needing standardized token handling.
- Position:
  - A standalone Python library (importable package) intended to be embedded as a dependency; it is not a network service or daemon.

## Architecture:
- Layered separation:
  1. JWS layer (jwt.api_jws): compact serialization, header handling, segment base64url encoding/decoding, algorithm registry and dispatch to Algorithm implementations.
  2. JWT layer (jwt.api_jwt): JSON payload encoding/decoding, claim normalization (exp/iat/nbf), claim validation (exp, nbf, iat, aud, iss, require), and public-facing convenience methods.
- Algorithm pluggability:
  - The JWS layer maintains a registry of Algorithm implementations that are used for prepare_key, sign, and verify. Algorithms are added/removed via register_algorithm/unregister_algorithm.
- Options-driven behavior:
  - Verification and validation behavior is controlled by per-instance defaults and per-call options (verify_signature, verify_exp, require, strict_aud, etc.) which are merged for each call.
- Data flow (encode and decode):

flowchart TD
    A[Application] -->|High-level encode| B(PyJWT.encode)
    B --> C[normalize claims, JSON-encode payload]
    C --> D(PyJWS.encode)
    D --> E[Algorithm.prepare_key & Algorithm.sign]
    E --> F[Compact JWS string]

    G[Token string] -->|High-level decode| H(PyJWT.decode)
    H --> I(PyJWS.decode_complete)
    I --> J[Algorithm.verify]
    J --> K[raw payload bytes]
    K --> L[PyJWT.decode_complete JSON-decode & claim validation]
    L --> M[Application receives validated claims]

## Entry Points:
- Class-based APIs (primary entry points):
  - jwt.api_jwt.PyJWT
    - encode(payload: dict, key, algorithm="HS256", headers=None, json_encoder=None, sort_headers=True) -> str
      - Behavior: normalize time claims (exp/iat/nbf to epoch seconds), JSON-encode payload bytes, delegate to PyJWS.encode.
      - Preconditions: payload must be a dict (JSON object); raises TypeError otherwise.
    - decode(jwt: str|bytes, key="", algorithms=None, options=None, verify=None, detached_payload=None, audience=None, issuer=None, leeway=0, **kwargs) -> Any
      - Behavior: delegates to self.decode_complete and returns parsed payload (claims).
      - Preconditions: when signature verification is enabled, algorithms must be provided.
    - decode_complete(...) -> dict
      - Behavior: full decode + claim validation; returns mapping with parsed payload under "payload".
  - jwt.api_jws.PyJWS
    - encode(payload: bytes, key, algorithm="HS256", headers=None, json_encoder=None, is_payload_detached=False, sort_headers=True) -> str
      - Behavior: build JOSE header, base64url-encode header and (unless detached) payload, sign and return compact serialization.
    - decode(jwt: str|bytes, key="", algorithms=None, options=None, detached_payload=None, **kwargs) -> bytes
      - Behavior: returns raw payload bytes; convenience wrapper around decode_complete.
    - decode_complete(...) -> dict
      - Behavior: parse header/payload/signature, optionally verify signature, return {"payload": bytes, "header": dict, "signature": bytes}.
    - register_algorithm(alg_id: str, alg_obj: Algorithm) -> None
    - unregister_algorithm(alg_id: str) -> None
    - get_unverified_header(jwt: str|bytes) -> dict
      - Behavior: parse and return the token header without verification.
- Module-level convenience wrappers (common but not guaranteed):
  - Repositories commonly expose top-level jwt.encode and jwt.decode convenience functions which simply instantiate a PyJWT and forward arguments to its encode/decode methods. If present, these wrappers should not add new semantics; they exist for ergonomic use.
- CLI / console scripts:
  - No CLI or console script entry points are documented in the available module/component summaries. If a CLI is required, implement a thin wrapper around PyJWT/PyJWS methods.

## Core Features (mapping to implementing modules/components):
- Token creation (compact JWS):
  - jwt.api_jws.PyJWS.encode (low-level), jwt.api_jwt.PyJWT.encode (high-level wrapper)
- Token parsing and signature verification:
  - jwt.api_jws.PyJWS.decode_complete and PyJWS._verify_signature (algorithm dispatch)
- JSON payload decoding and claim validation:
  - jwt.api_jwt.PyJWT.decode_complete and claim validation helpers
- Algorithm registry and extensibility:
  - jwt.api_jws.PyJWS.register_algorithm, unregister_algorithm
- Detached payload (b64:false) support:
  - Supported by PyJWS.encode and decode_complete
- Header inspection without verification:
  - jwt.api_jws.PyJWS.get_unverified_header
- Sphinx doc-time helpers:
  - docs.conf.read and docs.conf.find_version

## Public Exceptions (to be defined in exceptions.py)
- The decoding and validation flow references these exception classes (implementations should subclass an appropriate base exception):
  - DecodeError
  - InvalidAlgorithmError
  - InvalidSignatureError
  - InvalidTokenError
  - ExpiredSignatureError
  - ImmatureSignatureError
  - InvalidAudienceError
  - InvalidIssuerError
  - InvalidIssuedAtError
  - MissingRequiredClaimError
- Recommendation: define a common base (e.g., PyJWTError or JWTError) and derive specific exceptions for fine-grained catch behavior. Ensure messages match those described in component docs for consistency.

## Algorithms: Interface and Implementation Guidance
- Algorithm Interface (required methods; exact names from component docs):
  - prepare_key(key) -> backend_key
    - Purpose: normalize / validate raw key material for this algorithm (e.g., load PEM, convert password-protected keys, or validate HMAC secret length). May raise TypeError/ValueError for invalid key material.
  - sign(signing_input: bytes, prepared_key) -> bytes
    - Purpose: return raw signature bytes for the signing_input (typically the ASCII bytes of "<base64url(header)>.<base64url(payload)>").
  - verify(signing_input: bytes, signature: bytes, prepared_key) -> bool
    - Purpose: return True when the signature is valid for signing_input and the provided key, False otherwise (or raise InvalidSignatureError per choice).
- Typical algorithm implementations to provide (or reimplement):
  - HMAC family: HS256, HS384, HS512 (can be implemented with Python stdlib: hmac + hashlib)
  - RSA family: RS256, RS384, RS512 (commonly implemented using pyca/cryptography; prepare_key loads an RSA private/public key)
  - ECDSA family: ES256, ES384, ES512 (commonly implemented using pyca/cryptography; special handling for raw signature to/from ASN.1/DER)
- Optional dependencies:
  - Document that asymmetric algorithms typically require third-party crypto libraries (e.g., cryptography). Implementations should import these lazily and raise informative errors if missing.

## Dependencies:
- Required standard library modules:
  - json, base64, binascii, datetime, calendar, re, os, warnings, typing, hmac, hashlib
- Optional / algorithm-specific:
  - cryptography (pyca/cryptography) — for RSA/ECDSA
  - pycryptodome or other libraries as alternatives (implementation detail)
- Packaging note:
  - The repository should declare optional extras for asymmetric algorithms so that consumers can install only the crypto backends they need (e.g., extras named "crypto" or "crypto>=X").

## Configuration:
- No global config files. Behavior is controlled by:
  - Per-instance default options on PyJWT/PyJWS instances (a mapping)
  - Per-call options passed to encode/decode/decode_complete (a shallow-merged mapping)
- Sphinx build-time:
  - docs/conf.read and find_version are helpers used by conf.py to avoid importing the package at build time.

## Extension Points:
- Adding algorithms:
  - Implement the Algorithm interface and call PyJWS.register_algorithm(alg_id, alg_obj) before performing encode/decode.
- Subclassing:
  - Subclass PyJWT or PyJWS to change default options, header defaults, or to instrument behavior (logging/metrics).
- Key selection:
  - Use PyJWS.get_unverified_header to inspect "alg" or "kid" before selecting keys (be aware the header is untrusted until verified).
- Claim validation strategies:
  - Supply custom per-call options (verify_exp, require list, strict_aud) to change validation semantics.

## Reimplementation checklist (minimum viable set to reproduce core functionality)
To reimplement a functional compatible library that satisfies the component docs, implement the following elements:
1. Base exception hierarchy and the specific exceptions listed above.
2. jwt.api_jws:
   - PyJWS class with methods: encode, decode, decode_complete, get_unverified_header, register_algorithm, unregister_algorithm.
   - Implement base64url encode/decode helpers, JSON header parsing, detached payload handling, and algorithm registry mapping.
3. jwt.api_jwt:
   - PyJWT class with methods: encode, decode, decode_complete.
   - Implement JSON payload (de)serialization, time claim normalization, and claim validation (exp, nbf, iat, aud, iss, require).
4. algorithms/:
   - Provide at least HMAC (HS256) implementation using hmac+hashlib for completeness without external dependencies.
   - Provide clear Algorithm interface and hooks for optional asymmetric algorithm implementations that can be added later.
5. docs/conf helpers:
   - read(*parts) and find_version(*file_paths) as documented for Sphinx usage.

References:
- Use component-level documentation for jwt.api_jws.PyJWS.* and jwt.api_jwt.PyJWT.* (these components are documented separately in the repository memory and provide method-level behaviors, preconditions, exceptions, and side effects).
- For build-time helpers: see docs.conf.read and docs.conf.find_version component docs for exact regex and exception behaviors.

---

## Modules

- [`docs`](docs.md)
- [`jwt`](jwt.md)

