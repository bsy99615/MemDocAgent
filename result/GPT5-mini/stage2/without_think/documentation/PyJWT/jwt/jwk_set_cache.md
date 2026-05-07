# `jwk_set_cache.py`

## `jwt.jwk_set_cache.JWKSetCache` · *class*

## Summary:
A small in-memory cache that stores a PyJWKSet together with the monotonic timestamp when it was inserted, and exposes retrieval guarded by a configurable lifespan (TTL).

## Description:
JWKSetCache encapsulates simple TTL-based caching for JSON Web Key Sets (PyJWKSet instances). Typical callers:
- A JWK fetch/refresh routine or initialization code calls put(pyjwkset) after obtaining and validating a JWK set.
- Token validators or request handlers call get() to obtain the currently cached PyJWKSet for signature verification or key lookup.

The class exists to centralize timestamping and expiry logic:
- When a PyJWKSet is stored via put, it is wrapped in a PyJWTSetWithTimestamp which records time.monotonic() at construction.
- get() applies the expiry rule (via is_expired()) and returns either the stored PyJWKSet reference or None.
- The cache does not perform background eviction; expiry is evaluated on read.

Responsibility boundary:
- Stores at most one timestamped JWK set.
- Determines staleness using a lifespan (seconds).
- Does not perform concurrency control, network I/O, or persistent storage.

## State:
Attributes (instance-level)
- jwk_set_with_timestamp: Optional[PyJWTSetWithTimestamp]
    - Type: Optional[PyJWTSetWithTimestamp]
    - Initial value: None (set in __init__)
    - Valid values: None, or an instance of PyJWTSetWithTimestamp that wraps a PyJWKSet and stores the monotonic timestamp when put(...) was called.
    - Invariant: If not None, get_jwk_set() on the contained PyJWTSetWithTimestamp returns the PyJWKSet passed to put.
- lifespan: int
    - Type: int (seconds)
    - Meaning: maximum allowed age for a cached entry before it is considered expired.
    - Valid values and interpretation:
        - Any integer accepted by the constructor. Negative values are treated specially: lifespan <= -1 disables expiry ("never expires").
    - No internal enforcement of non-negativity; callers should pass intended semantics.

Class invariants:
- jwk_set_with_timestamp is either None or a PyJWTSetWithTimestamp whose timestamp reflects when the last successful put(non-None) occurred.
- get() never mutates self.jwk_set_with_timestamp (it may return None if expired but leaves the stored wrapper in place).
- is_expired() returns True only when jwk_set_with_timestamp is not None, lifespan > -1, and the elapsed monotonic time strictly exceeds stored_timestamp + lifespan.

## Lifecycle:
Creation:
- Instantiate with a lifespan in seconds: JWKSetCache(lifespan).
- Required argument: lifespan (int). The constructor only assigns attributes and does not validate or type-check lifespan.

Usage:
1. Populate: call put(pyjwkset) with a validated PyJWKSet to store it in the cache (this wraps it in PyJWTSetWithTimestamp which records time.monotonic()).
2. Retrieve: call get() to obtain the stored PyJWKSet if present and not expired; otherwise get() returns None.
3. Clear: call put(None) to remove the cached entry immediately.

Typical invocation ordering:
- put(...) before get() to make a value available.
- get() may be called repeatedly; is_expired() is used internally by get() to decide visibility.
- There is no required ordering between is_expired() and get() for callers; is_expired() is provided for callers that need an explicit staleness check.

Destruction / cleanup:
- No explicit cleanup API. Instances are ordinary Python objects and require no close() or context management.
- If the underlying PyJWKSet holds resources, managing those resources is the responsibility of that object.

Thread-safety:
- The class performs plain attribute reads/writes and does not implement locking. If accessed concurrently (threads/processes), callers must provide synchronization externally.

## Method Map:
flowchart TD
    A[put(jwk_set)] -->|jwk_set is not None| B[create PyJWTSetWithTimestamp(jwk_set)]
    A -->|jwk_set is None| C[set jwk_set_with_timestamp = None]
    B --> D[jwk_set_with_timestamp updated]
    C --> D
    E[get()] --> F[if jwk_set_with_timestamp is None -> return None]
    E --> G[else if is_expired() is True -> return None]
    E --> H[else -> return jwk_set_with_timestamp.get_jwk_set()]
    I[is_expired()] --> J[check jwk_set_with_timestamp is not None]
    J --> K[check lifespan > -1]
    K --> L[compare time.monotonic() > stored_timestamp + lifespan]

## Methods (behavioral summary)
- __init__(lifespan: int) -> None
    - Stores lifespan and initializes the internal storage to None.
    - Expected parameter: lifespan (seconds). No runtime validation is performed.

- put(jwk_set: PyJWKSet) -> None
    - If jwk_set is not None: wraps the given PyJWKSet in a PyJWTSetWithTimestamp (which records a monotonic timestamp) and stores it in jwk_set_with_timestamp.
    - If jwk_set is None: clears the cache by setting jwk_set_with_timestamp to None.
    - The call always overwrites any existing cached entry.

- get() -> Optional[PyJWKSet]
    - Returns the cached PyJWKSet (the same object reference that was passed to put) when and only when:
        1) jwk_set_with_timestamp is not None, and
        2) is_expired() returns False.
    - Returns None if no entry exists or if the entry is expired.
    - Does not mutate stored jwk_set_with_timestamp (expired entries remain stored until explicitly cleared by put(None) or overwritten).

- is_expired() -> bool
    - Returns True if:
        * jwk_set_with_timestamp is not None, and
        * lifespan > -1 (expiry is enabled), and
        * time.monotonic() > (jwk_set_with_timestamp.get_timestamp() + lifespan)
    - Returns False otherwise (including when no entry is stored or lifespan <= -1).
    - Uses time.monotonic() to avoid wall-clock adjustments.

## Raises:
- __init__: Does not raise application-level exceptions. Passing a non-int lifespan will not raise here but may cause semantically incorrect behavior.
- put: No application-level exceptions raised by JWKSetCache itself. Exceptions may propagate from PyJWTSetWithTimestamp(...) constructor (e.g., if that constructor raises), or runtime errors (MemoryError).
- get and is_expired:
    - Do not raise in the normal code path. However, if the contained PyJWTSetWithTimestamp.get_timestamp() or .get_jwk_set() implementations raise, those exceptions will propagate.
    - time.monotonic() is expected not to raise; if it does (extremely unlikely), that will propagate.

## Example:
- Create a cache with 5-minute TTL:
    1) cache = JWKSetCache(300)
    2) cache.put(pyjwkset)  # store a PyJWKSet (wraps and timestamps)
    3) cached = cache.get()  # returns pyjwkset until expired, else None
    4) if cache.is_expired(): fetch a fresh PyJWKSet and cache.put(new_pyjwkset)
    5) cache.put(None)  # clear the cache immediately

Notes and constraints:
- Lifespan units are seconds and measured against time.monotonic() timestamps stored by PyJWTSetWithTimestamp.
- A lifespan <= -1 disables expiry — values stored remain retrievable until explicitly cleared or overwritten.
- get() returns the original PyJWKSet reference (no defensive copy).
- The class is intentionally minimal; callers that require concurrency safety or background eviction should add those mechanisms externally.

### `jwt.jwk_set_cache.JWKSetCache.__init__` · *method*

## Summary:
Initializes a JWKSetCache object by setting its cached JWK set to None and recording the lifespan value used to determine cache expiry.

## Description:
This constructor prepares a JWKSetCache instance for use by:
- Setting the internal jwk_set_with_timestamp slot to None (no cached value on creation).
- Storing the provided lifespan (an integer interpreted as seconds) on the instance for later expiry checks.

Known callers and context:
- Called whenever a JWKSetCache instance is constructed (e.g., at application startup or when creating a cache object to manage a JSON Web Key Set).
- Typical lifecycle stage: object construction / initialization before any get/update cache operations are invoked.

Why this logic is its own method:
- As the class constructor, this method centralizes initial state setup for the cache object (clearing any cached set and recording the cache duration). Keeping initialization in __init__ ensures consistent, minimal-ready state immediately after instantiation.

## Args:
    lifespan (int):
        Number of seconds a cached JWK set is considered valid. Expected to be an integer representing seconds.
        - Allowed values: any integer; semantically should be non-negative (0 means no lifespan). This is a semantic expectation only — the constructor does not validate the value.
        - Required: yes (no default).

## Returns:
    None

## Raises:
    None — the constructor does not raise exceptions. Type hints indicate an int is expected, but no runtime type checking is performed here.

## State Changes:
Attributes READ:
    - None

Attributes WRITTEN:
    - self.jwk_set_with_timestamp: set to None (type: Optional[PyJWTSetWithTimestamp])
    - self.lifespan: set to the provided lifespan value (type: int)

## Constraints:
Preconditions:
    - The caller should pass an integer-like value for lifespan; the implementation assumes lifespan is meaningful as seconds.
    - No other attributes on self are required to exist before calling __init__ (this is the object initializer).

Postconditions:
    - After return, self.jwk_set_with_timestamp is guaranteed to be None.
    - After return, self.lifespan equals the provided lifespan argument.

## Side Effects:
    - No I/O, no external service calls.
    - Mutates only the newly-created instance (writes to self.jwk_set_with_timestamp and self.lifespan); does not modify external objects.

### `jwt.jwk_set_cache.JWKSetCache.put` · *method*

## Summary:
Store or clear the cached JWK set by replacing self.jwk_set_with_timestamp with a timestamped container when a PyJWKSet is provided, or clearing the cache when None is provided.

## Description:
This method is the single place that updates the cache entry held by JWKSetCache. It is called at the point in the JWK retrieval/refresh lifecycle when a freshly-obtained PyJWKSet should replace (or clear) the cached value. Typical callers are code that fetches or constructs a new PyJWKSet (for example: a JWK fetch/refresh routine, an initialization path that loads keys at startup, or any cache-management component). No direct call sites were provided in the source snapshot; callers should invoke put immediately after obtaining a validated PyJWKSet to make it available to subsequent get() calls.

Why this is a separate method:
- Centralizes cache mutation so the cache attribute is updated consistently (always wrapped with a timestamp container when present).
- Encapsulates the semantic of "store or clear" so callers do not need to manipulate the internal jwk_set_with_timestamp attribute directly.
- Ensures the timestamping behavior (via PyJWTSetWithTimestamp) is applied uniformly at the moment of cache population.

## Args:
    jwk_set (PyJWKSet or None): The validated JWK set to cache. If a PyJWKSet instance is provided, it will be wrapped in a PyJWTSetWithTimestamp and stored in self.jwk_set_with_timestamp. If None is provided, the cache entry will be cleared (self.jwk_set_with_timestamp set to None).
    Note: The function signature is annotated with PyJWKSet (non-Optional), but the implementation explicitly accepts None as a valid value to clear the cache.

## Returns:
    None

## Raises:
    This method does not raise any application-level exceptions itself.
    - If invalid objects are passed, PyJWTSetWithTimestamp's constructor will accept and store the reference without validation (it does not perform type checks); therefore, no exception is produced here. Runtime errors only arise from Python-level failures (e.g., MemoryError) or from PyJWTSetWithTimestamp if that implementation were changed to raise.

## State Changes:
- Attributes READ:
    - None (this method does not read any existing attributes of self to decide behavior).
- Attributes WRITTEN:
    - self.jwk_set_with_timestamp: overwritten unconditionally.
        - If jwk_set is not None: set to PyJWTSetWithTimestamp(jwk_set)
        - If jwk_set is None: set to None

## Constraints:
- Preconditions:
    - None required by the implementation. For correct semantics, callers should pass a properly constructed PyJWKSet (not a raw dict or malformed object) when intending to cache keys.
    - Callers should be aware that the method accepts None to clear the cache.
- Postconditions:
    - After return, self.jwk_set_with_timestamp is either:
        - a PyJWTSetWithTimestamp instance that wraps the same object passed as jwk_set (and records a monotonic timestamp at construction), or
        - None if jwk_set was None.
    - Subsequent calls to get() will return the stored PyJWKSet (via the wrapper) unless the entry becomes expired (see is_expired()) or is cleared by a later put(None).

## Side Effects:
    - Instantiates PyJWTSetWithTimestamp when jwk_set is not None; that constructor captures a monotonic timestamp (time.monotonic()) and stores a reference to the provided jwk_set.
    - No network, file I/O, or external service calls are performed by this method.
    - No locking or concurrency controls are performed here; if the cache is accessed concurrently, callers must coordinate synchronization externally if required.

### `jwt.jwk_set_cache.JWKSetCache.get` · *method*

## Summary:
Return the currently cached PyJWKSet if present and not expired; otherwise leave object state unchanged and return None.

## Description:
- Known callers and context:
    - Code paths that need the active JWK set for operations such as JWT verification or key lookup typically call this method during the "retrieve from cache" stage of token validation or JWK rotation logic.
    - Typical lifecycle: an external producer calls JWKSetCache.put(...) to populate the cache; later, validators or request handlers call get() to obtain the cached set (if any) for signature verification.
- Why this is a separate method:
    - Encapsulates the retrieval and staleness check in one place so callers do not need to reimplement expiry logic.
    - Keeps public API simple (single accessor that applies TTL rules) and centralizes potential future changes (e.g., defensive copying or metrics).

## Args:
- None

## Returns:
- Optional[PyJWKSet]
    - Returns the PyJWKSet instance previously stored via put(...) (the same object reference) when and only when:
        - self.jwk_set_with_timestamp is not None, and
        - the cached entry is not expired (is_expired() returns False).
    - Returns None when:
        - No JWK set has been stored yet (self.jwk_set_with_timestamp is None), or
        - The stored JWK set is considered expired according to is_expired().
    - Edge cases:
        - If lifespan is <= -1 (cache configured to never expire), and a jwk_set_with_timestamp exists, this method will return the stored PyJWKSet (because is_expired() will be False).
        - The returned PyJWKSet is the original reference stored inside PyJWTSetWithTimestamp; no defensive copy is performed.

## Raises:
- None: this method does not raise application-level exceptions. Only runtime exceptions from the environment (e.g., MemoryError) could occur.

## State Changes:
- Attributes READ:
    - self.jwk_set_with_timestamp
    - self.lifespan (accessed indirectly via is_expired())
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - The JWKSetCache instance must have been constructed (its __init__ sets self.lifespan and initializes self.jwk_set_with_timestamp to None).
    - There is no requirement that self.jwk_set_with_timestamp be non-None; callers should handle None returns.
- Postconditions:
    - The JWKSetCache object is not modified by this call (no attributes are changed).
    - If a PyJWKSet is returned, it is the exact object that was stored in the associated PyJWTSetWithTimestamp container.
    - If None is returned, the cache remains unchanged (the stored container is not cleared by get()).

## Side Effects:
- Observes elapsed time via is_expired(), which calls time.monotonic() and PyJWTSetWithTimestamp.get_timestamp(); these are read-only operations with respect to instance state.
- No I/O, no network calls, and no mutation of objects outside self are performed by this method.

### `jwt.jwk_set_cache.JWKSetCache.is_expired` · *method*

## Summary:
Returns whether the cached JWK set has exceeded its allowed lifespan and should be considered expired; does not mutate the cache.

## Description:
Known callers and context:
- JWKSetCache.get: called as part of retrieving a cached PyJWKSet to decide whether the stored entry is still valid. This occurs in the retrieval stage of the cache lifecycle (on-read validation before returning the cached value to callers).
- The method is deliberately separated from get to centralize expiration logic so other cache-accessing code can reuse the same expiration check and to keep get focused on retrieval semantics.

Behavior summary:
- The method evaluates three conditions and returns True only if all are satisfied:
  1. A cached entry exists (self.jwk_set_with_timestamp is not None).
  2. The configured lifespan allows expiration (self.lifespan > -1).
  3. The current monotonic time has advanced beyond the stored entry timestamp plus the lifespan.

Implementation note:
- Uses time.monotonic() to compare elapsed durations (robust against system clock adjustments).
- The stored timestamp is obtained from self.jwk_set_with_timestamp.get_timestamp(); get_timestamp is guarded by the existence check so it will not be called when jwk_set_with_timestamp is None.

## Args:
- None

## Returns:
- bool: 
    - True if a cached PyJWKSet exists and the elapsed monotonic time since the stored timestamp strictly exceeds the configured lifespan (i.e., the entry is expired).
    - False in all other cases, including:
        * No cached entry exists (self.jwk_set_with_timestamp is None).
        * lifespan is -1 or any negative value (interpreted as "never expires").
        * Current monotonic time is less than or equal to stored_timestamp + lifespan (not yet expired).

## Raises:
- None by this method itself.
- (Implicit) If self.jwk_set_with_timestamp is not None but its get_timestamp() implementation raises, that exception will propagate; however, the method prevents get_timestamp() being called when jwk_set_with_timestamp is None.

## State Changes:
- Attributes READ:
    - self.jwk_set_with_timestamp
    - self.lifespan
    - indirectly uses self.jwk_set_with_timestamp.get_timestamp()
- Attributes WRITTEN:
    - None (this method does not modify any attributes on self)

## Constraints:
- Preconditions:
    - self.lifespan is expected to be an integer (or numeric) representing seconds; negative values are allowed and treated as "never expire" when <= -1.
    - If self.jwk_set_with_timestamp is not None, it must implement get_timestamp() returning a monotonic clock timestamp (compatible with time.monotonic()) captured when the entry was created.
- Postconditions:
    - The cache object (self) is unchanged after the call.
    - The return value correctly reflects the three-condition check described above.

## Side Effects:
- None: the method performs no I/O and does not mutate self or external state.
- Possible exception propagation if get_timestamp() or time.monotonic() (extremely unlikely) raise errors, but no side-effecting calls are made here.

