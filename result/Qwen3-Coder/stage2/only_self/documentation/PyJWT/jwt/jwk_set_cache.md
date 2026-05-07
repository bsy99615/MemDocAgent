# `jwk_set_cache.py`

## `jwt.jwk_set_cache.JWKSetCache` · *class*

*No documentation generated.*

### `jwt.jwk_set_cache.JWKSetCache.__init__` · *method*

## Summary:
Initializes a JWKSetCache instance with a specified lifespan for cached JWK sets.

## Description:
This method serves as the constructor for the JWKSetCache class, initializing the cache with a specified lifespan. It prepares the object for subsequent operations involving JWK set caching by setting up internal state variables.

## Args:
    lifespan (int): The maximum duration (in seconds) that cached JWK sets remain valid before requiring refresh.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.jwk_set_with_timestamp: Set to None initially, indicating no cached JWK set is present
    - self.lifespan: Set to the provided lifespan value

## Constraints:
    Preconditions:
    - The lifespan parameter must be a non-negative integer
    - This method should only be called during object initialization
    
    Postconditions:
    - self.jwk_set_with_timestamp will be None upon initialization
    - self.lifespan will be set to the provided value

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `jwt.jwk_set_cache.JWKSetCache.put` · *method*

## Summary:
Stores a JSON Web Key Set in the cache with timestamp metadata, replacing any existing cached set.

## Description:
Sets the cached JWK set to the provided value, wrapped with timestamp metadata for expiration tracking. If None is provided, clears the current cache entry. This method serves as the primary interface for updating the cached JWK set and is typically called during JWK set refresh operations or initial population of the cache.

The method is separated from inline logic to provide a clean abstraction for cache management and to enable future enhancements such as cache eviction policies or logging of cache updates.

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
    Postconditions: The cached JWK set is either updated with the new timestamped wrapper or cleared when None is provided

## Side Effects:
    None

### `jwt.jwk_set_cache.JWKSetCache.get` · *method*

## Summary:
Retrieves the cached JSON Web Key Set if it exists and hasn't expired, otherwise returns None.

## Description:
Checks if a cached JWK set is available and still valid based on its timestamp and configured lifespan. If the cached set is either missing or has expired, returns None. Otherwise, extracts and returns the underlying JWK set from the timestamped wrapper.

This method implements cache validation logic by delegating to the `is_expired()` method to determine if the cached JWK set should be considered stale. It's designed to be called during JWT validation workflows where cached JWK sets are preferred over fetching fresh ones when possible.

## Args:
    None

## Returns:
    Optional[PyJWKSet]: The cached JSON Web Key Set if valid, or None if the cache is empty or expired.

## Raises:
    None

## State Changes:
    Attributes READ: self.jwk_set_with_timestamp, self.lifespan
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The JWKSetCache instance must be properly initialized with a valid lifespan value.
    Postconditions: The returned PyJWKSet object (when not None) represents the most recent valid JWK set that was cached.

## Side Effects:
    None

### `jwt.jwk_set_cache.JWKSetCache.is_expired` · *method*

## Summary:
Determines whether the cached JSON Web Key Set has exceeded its configured lifespan and should be considered expired.

## Description:
Checks if the currently cached JWK set has become stale based on its timestamp and the maximum allowed lifespan. This method is used internally by the JWKSetCache class to validate cache freshness before returning cached key sets to consumers.

The expiration logic evaluates three conditions in sequence:
1. A JWK set must be present in the cache
2. The configured lifespan must be valid (greater than -1)
3. The elapsed time since the JWK set was cached must exceed the configured lifespan

This method is called by the `get` method to determine if cached data should be invalidated and refreshed.

## Args:
    None

## Returns:
    bool: True if the cached JWK set has expired, False otherwise. Returns False when no JWK set is cached or when lifespan is disabled.

## Raises:
    None

## State Changes:
    Attributes READ: self.jwk_set_with_timestamp, self.lifespan
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The JWKSetCache instance must be properly initialized with a valid lifespan value.
    Postconditions: The method returns a boolean value indicating cache validity status without modifying any object state.

## Side Effects:
    None

