# `jwt`

## Tree:
jwt/
├── api_jwk.py
├── api_jws.py
├── api_jwt.py
├── exceptions.py
├── help.py
├── jwk_set_cache.py
├── jwks_client.py
└── warnings.py

## Role:
Provides a complete implementation of JSON Web Token (JWT) standards including encoding, decoding, signing, and verification with support for various cryptographic algorithms and key management.

## Description:
The jwt module implements the complete JSON Web Token (JWT) ecosystem according to RFC 7515 (JWS) and RFC 7519 (JWT) standards. It provides a unified interface for creating and validating JWT tokens with support for multiple cryptographic algorithms, key management, and secure token operations. The module is organized into distinct layers that handle different aspects of JWT processing: key management (JWK), signature operations (JWS), and token-level operations (JWT).

This module is designed to be the primary interface for JWT functionality in applications, offering both high-level convenience methods and low-level building blocks for advanced use cases. It supports standard JWT claims validation, cryptographic signature verification, and integration with external key management systems through the JWK Set client.

## Components:
*   `PyJWKSet` - Manages collections of JSON Web Keys with validation and conversion capabilities
*   `PyJWTSetWithTimestamp` - Wraps JWK sets with timestamp metadata for cache management
*   `PyJWS` - Implements JSON Web Signature operations for signing and verifying JWT tokens
*   `PyJWT` - Provides high-level JWT encoding and decoding with claim validation
*   `PyJWKClient` - Fetches and caches JWK sets from remote endpoints for key management
*   `JWKSetCache` - Implements caching for JWK sets with configurable expiration
*   `PyJWTError` - Base exception class for all JWT-related errors
*   `RemovedInPyjwt3Warning` - Warning class for deprecated features in upcoming releases

## Public API:
*   `PyJWT.encode(payload, key, algorithm='HS256', headers=None, json_encoder=None, sort_headers=True)` - Encodes a payload into a JWT token with standard claims handling
*   `PyJWT.decode(jwt, key, algorithms, options=None, verify=True, detached_payload=None, audience=None, issuer=None, leeway=0, **kwargs)` - Decodes and validates a JWT token with standard claims validation
*   `PyJWT.decode_complete(jwt, key, algorithms, options=None, verify=True, detached_payload=None, audience=None, issuer=None, leeway=0, **kwargs)` - Decodes and validates a JWT token with complete component access
*   `PyJWKClient(uri, cache_keys=False, max_cached_keys=16, cache_jwk_set=True, lifespan=300, headers=None, timeout=30, ssl_context=None)` - Creates a client for fetching JWK sets from remote endpoints
*   `PyJWKClient.get_signing_key(kid)` - Retrieves a signing key by key ID from the JWK set
*   `PyJWKClient.get_signing_key_from_jwt(token)` - Extracts and retrieves the signing key from a JWT token's header
*   `PyJWKClient.get_jwk_set(refresh=False)` - Fetches or retrieves the cached JWK set
*   `JWKSetCache(lifespan)` - Creates a cache for JWK sets with expiration control
*   `JWKSetCache.put(jwk_set)` - Stores a JWK set in the cache
*   `JWKSetCache.get()` - Retrieves a cached JWK set if not expired
*   `jwt.help.info()` - Collects and returns system/environment information
*   `jwt.help.main()` - Outputs system/environment information as JSON

## Dependencies:
*   Internal: 
    *   `api_jwk` - Provides JWK and JWK Set functionality
    *   `api_jws` - Provides JWS signing and verification operations
    *   `api_jwt` - Provides JWT encoding and decoding with claim validation
    *   `jwk_set_cache` - Provides caching infrastructure for JWK sets
    *   `jwks_client` - Provides client functionality for fetching JWK sets
    *   `exceptions` - Provides specialized exception classes for JWT operations
    *   `warnings` - Provides deprecation warnings for future changes
*   External: 
    *   `base64` - For base64url encoding/decoding operations
    *   `collections` - For ordered dictionary operations
    *   `copy` - For deep copying of objects
    *   `datetime` - For time-based claim validation
    *   `hashlib` - For cryptographic hash operations
    *   `json` - For JSON serialization/deserialization
    *   `os` - For environment variable access
    *   `platform` - For system information gathering
    *   `ssl` - For SSL/TLS context management
    *   `sys` - For system-level operations
    *   `time` - For timestamp operations
    *   `urllib` - For HTTP/HTTPS requests to JWK endpoints
    *   `typing` - For type annotations
    *   `warnings` - For issuing deprecation warnings

## Constraints:
*   Thread-safety: The module is not thread-safe and assumes single-threaded access patterns for internal state management
*   Initialization: All components must be properly initialized before use, especially PyJWKClient which requires a valid URI
*   Algorithm selection: When signature verification is enabled, algorithms must be explicitly specified
*   Key management: Keys must be compatible with the specified algorithms and properly formatted for cryptographic operations
*   Cache expiration: JWK set caching has configurable lifespans that must be respected for security and performance
*   Memory usage: Caching mechanisms may consume significant memory for large key sets or high-volume operations

---

## Files

- [`api_jwk.py`](jwt/api_jwk.md)
- [`api_jws.py`](jwt/api_jws.md)
- [`api_jwt.py`](jwt/api_jwt.md)
- [`exceptions.py`](jwt/exceptions.md)
- [`help.py`](jwt/help.md)
- [`jwk_set_cache.py`](jwt/jwk_set_cache.md)
- [`jwks_client.py`](jwt/jwks_client.md)
- [`warnings.py`](jwt/warnings.md)

