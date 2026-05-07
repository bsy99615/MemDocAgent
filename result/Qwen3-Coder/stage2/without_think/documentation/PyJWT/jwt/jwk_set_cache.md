# `jwk_set_cache.py`

## `jwt.jwk_set_cache.JWKSetCache` · *class*

## Summary:
Manages a cached JSON Web Key Set with automatic expiration based on a configurable lifespan.

## Description:
The JWKSetCache class provides a simple caching mechanism for JSON Web Key Sets (JWK Sets) that automatically expires cached entries after a specified time period. This class wraps PyJWKSet objects with timestamp information to enable expiration checking. It is typically used in JWT processing contexts where JWK sets need to be cached temporarily to avoid repeated fetching from remote sources while ensuring keys don't become stale beyond a configured threshold.

The cache is thread-unsafe and assumes single-threaded access patterns. It's designed to be lightweight and efficient for short-term storage of cryptographic keys used in token validation.

## State:
- jwk_set_with_timestamp: Optional[PyJWTSetWithTimestamp] - The cached JWK set wrapped with timestamp information, or None if empty
- lifespan: int - Maximum age in seconds for cached JWK sets before they expire; negative values indicate infinite lifetime

## Lifecycle:
Creation: Instantiate with a lifespan parameter specifying maximum cache duration in seconds. A lifespan of -1 indicates infinite cache lifetime.
Usage: Call put() to store a JWK set, then get() to retrieve it. The get() method automatically checks expiration.
Destruction: No explicit cleanup required; standard Python garbage collection handles resource management.

## Method Map:
```mermaid
graph TD
    A[JWKSetCache.put] --> B{jwk_set is not None?}
    B -->|Yes| C[Create PyJWTSetWithTimestamp]
    B -->|No| D[Set to None]
    C --> E[Store in jwk_set_with_timestamp]
    D --> E
    
    F[JWKSetCache.get] --> G{jwk_set_with_timestamp is None?}
    G -->|Yes| H[Return None]
    G -->|No| I[Call is_expired()]
    I --> J{is_expired returns True?}
    J -->|Yes| H
    J -->|No| K[Call get_jwk_set()]
    K --> L[Return JWK set]
    
    M[JWKSetCache.is_expired] --> N{jwk_set_with_timestamp is not None?}
    N -->|No| O[Return False]
    N -->|Yes| P{lifespan > -1?}
    P -->|No| O
    P -->|Yes| Q[Compare time.monotonic() with timestamp + lifespan]
    Q --> R[Return comparison result]
```

## Raises:
- None explicitly raised by __init__
- The underlying PyJWTSetWithTimestamp constructor may raise exceptions when wrapping invalid JWK sets, but these are propagated through the put() method

## Example:
```python
# Create a cache with 3600 second (1 hour) lifespan
cache = JWKSetCache(lifespan=3600)

# Store a JWK set
jwk_set = PyJWKSet.from_json(json_data)
cache.put(jwk_set)

# Retrieve the cached JWK set
cached_jwk_set = cache.get()
if cached_jwk_set is not None:
    # Use the cached key set for JWT validation
    pass

# Later, after cache expiration, get() will return None
expired_jwk_set = cache.get()  # Returns None if expired
```

### `jwt.jwk_set_cache.JWKSetCache.__init__` · *method*

## Summary:
Initializes a JWKSetCache instance with a specified lifespan for cached key sets.

## Description:
Configures the cache instance with an expiration threshold and initializes the cache state. This constructor sets up the internal tracking of cached JWK sets and establishes the maximum lifetime for cached entries. The cache starts empty with no cached key set and stores the lifespan configuration for future expiration checks.

## Args:
    lifespan (int): Maximum age in seconds for cached JWK sets before they expire. Negative values indicate infinite lifetime.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.jwk_set_with_timestamp: Set to None to indicate empty cache state
    - self.lifespan: Set to the provided lifespan parameter value

## Constraints:
    Preconditions: The lifespan parameter should be an integer representing seconds, though negative values are accepted to indicate infinite lifetime.
    Postconditions: After initialization, the cache is ready to store JWK sets with the specified expiration policy.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `jwt.jwk_set_cache.JWKSetCache.put` · *method*

## Summary:
Stores a JSON Web Key Set in the cache, either wrapped with a timestamp or as None.

## Description:
Sets the cached JWK set to either a timestamp-wrapped version of the provided key set or None. This method serves as the primary interface for updating the cached key set in the JWKSetCache instance. It is typically called during key set refresh operations or when initializing the cache with new key material.

The method is part of a cache management pattern where key sets are stored with timestamps to enable expiration checking. When a None value is provided, it clears the cache entry.

## Args:
    jwk_set (PyJWKSet): The JSON Web Key Set to cache, or None to clear the cache

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.jwk_set_with_timestamp

## Constraints:
    Preconditions: The JWKSetCache instance must be properly initialized
    Postconditions: The cached key set reference is updated to either a PyJWTSetWithTimestamp wrapper or None

## Side Effects:
    None

### `jwt.jwk_set_cache.JWKSetCache.get` · *method*

## Summary:
Retrieves the cached JWK set if it exists and hasn't expired, otherwise returns None.

## Description:
Fetches the currently cached JSON Web Key set from the JWK set cache. This method implements cache validation by checking both the existence of a cached key set and its expiration status. When the cached key set is either missing or has exceeded its configured lifespan, the method returns None to indicate a cache miss.

The method is designed as a separate utility to encapsulate the cache retrieval and validation logic, making it reusable and testable. It follows the principle of lazy evaluation by only performing the expensive operations (checking expiration and retrieving the actual key set) when needed.

## Args:
    None

## Returns:
    Optional[PyJWKSet]: The cached JWK set if it exists and hasn't expired, otherwise None

## Raises:
    None

## State Changes:
    Attributes READ: self.jwk_set_with_timestamp, self.lifespan
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The JWKSetCache instance must be properly initialized with a valid lifespan
    Postconditions: The returned PyJWKSet (if not None) is guaranteed to be valid and unexpired at the time of retrieval

## Side Effects:
    None

### `jwt.jwk_set_cache.JWKSetCache.is_expired` · *method*

## Summary:
Checks whether the cached JWK set has exceeded its configured lifespan and should be considered expired.

## Description:
Determines if the currently cached JWK set with timestamp has surpassed its maximum allowed lifetime. This method evaluates three conditions: the presence of a valid JWK set with timestamp, a positive lifespan configuration, and whether the current time exceeds the cached timestamp plus the configured lifespan. This method is primarily used internally by the `get` method to validate cache freshness before returning cached data.

## Args:
    None

## Returns:
    bool: True if the JWK set has expired (current time > timestamp + lifespan), False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self.jwk_set_with_timestamp: Optional[PyJWTSetWithTimestamp] - The cached JWK set with timestamp
    - self.lifespan: int - Configured maximum lifetime in seconds

## Constraints:
    Preconditions:
    - self.jwk_set_with_timestamp must be either None or a valid PyJWTSetWithTimestamp instance
    - self.lifespan must be an integer (typically >= 0, though -1 indicates infinite lifetime)
    
    Postconditions:
    - Returns a boolean value indicating cache expiration status
    - Does not modify any object state

## Side Effects:
    None

