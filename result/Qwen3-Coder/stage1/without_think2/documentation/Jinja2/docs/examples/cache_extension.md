# `cache_extension.py`

## `docs.examples.cache_extension.FragmentCacheExtension` · *class*

## Summary:
A Jinja2 extension that provides template fragment caching functionality using the `{% cache %}` tag.

## Description:
This class implements a Jinja2 template extension that enables caching of template fragments. It adds support for the `{% cache %}` template tag, which allows developers to cache expensive template computations. The extension integrates with Jinja2's parsing and rendering system to provide efficient caching of template content.

## State:
- `tags`: Class attribute defining the template tag this extension handles, set to {"cache"}
- `fragment_cache_prefix`: String prefix applied to cache keys, initialized as empty string in environment via `environment.extend()`
- `fragment_cache`: Cache object used for storing cached template fragments, initialized as None in environment via `environment.extend()`

## Lifecycle:
- Creation: Instantiate with a Jinja2 Environment object; the `__init__` method calls `super().__init__(environment)` and extends the environment with `fragment_cache_prefix` and `fragment_cache` attributes
- Usage: When the Jinja2 parser encounters a `{% cache %}` template tag, it calls the `parse()` method to process the tag. The parsed tag creates a CallBlock that eventually invokes `_cache_support()` to handle the caching logic
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Template Parse] --> B[parse()]
    B --> C[parse_expression]
    B --> D[parse_expression]
    B --> E[parse_statements]
    E --> F[CallBlock]
    F --> G[_cache_support]
    G --> H[fragment_cache.get]
    H --> I{Found in cache?}
    I -->|Yes| J[Return cached value]
    I -->|No| K[caller()]
    K --> L[fragment_cache.add]
    L --> M[Return computed value]
```

## Raises:
- None explicitly raised by `__init__` or `parse` methods
- May raise exceptions from underlying cache operations (`fragment_cache.get`, `fragment_cache.add`) if the cache implementation is faulty

## Example:
```python
from jinja2 import Environment
from docs.examples.cache_extension import FragmentCacheExtension

# Create environment with the extension
env = Environment(extensions=[FragmentCacheExtension])

# Configure cache in environment
env.fragment_cache = SomeCacheImplementation()  # e.g., a dict-based cache
env.fragment_cache_prefix = "myapp_"

# In template: {% cache "user_profile_123" 300 %}{{ expensive_user_lookup() }}{% endcache %}
# This caches the result of expensive_user_lookup() for 300 seconds under the key "myapp_user_profile_123"
```

### `docs.examples.cache_extension.FragmentCacheExtension.__init__` · *method*

## Summary:
Initializes a FragmentCacheExtension instance and configures the Jinja2 environment with cache-related attributes for template fragment caching.

## Description:
This method initializes the FragmentCacheExtension by calling the parent Extension class constructor and extending the Jinja2 environment with two essential cache configuration attributes: `fragment_cache_prefix` (initialized as an empty string) and `fragment_cache` (initialized as None). These attributes are crucial for the caching mechanism to function properly when the `{% cache %}` template tag is processed. The method is part of the Jinja2 extension lifecycle and ensures the environment is properly prepared for fragment caching operations.

## Args:
    environment (jinja2.Environment): The Jinja2 environment instance to extend with cache functionality. This environment must support the `extend` method which is standard for Jinja2 environments.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - `fragment_cache_prefix`: Set to empty string in the environment to provide a default prefix for cache keys
    - `fragment_cache`: Set to None in the environment to indicate no cache implementation is initially configured

## Constraints:
    Preconditions:
    - The `environment` argument must be a valid Jinja2 Environment instance
    - The environment must support the `extend` method (standard for Jinja2 environments)
    
    Postconditions:
    - The environment will have `fragment_cache_prefix` attribute set to ""
    - The environment will have `fragment_cache` attribute set to None
    - The environment will be properly configured for fragment caching operations
    - The FragmentCacheExtension will be registered with the environment

## Side Effects:
    None: This method does not perform I/O, external service calls, or mutate objects outside the environment. It only modifies the environment's attribute dictionary through the extend mechanism.

### `docs.examples.cache_extension.FragmentCacheExtension.parse` · *method*

## Summary:
Parses a Jinja2 template cache tag and constructs a call block for cached content rendering.

## Description:
This method handles the parsing of the `{% cache %}` template tag, extracting arguments and constructing a CallBlock node that will invoke the cache support mechanism during template execution. It processes the cache tag's arguments (name and optional timeout), parses the cached content block, and creates a call block that wraps the caching logic. The method is part of the FragmentCacheExtension class and is invoked during template compilation when a cache tag is encountered.

## Args:
    parser (Parser): The Jinja2 parser instance currently processing the template.

## Returns:
    CallBlock: A Jinja2 CallBlock node representing the parsed cache tag with its arguments and body, properly configured with line number information.

## Raises:
    None explicitly raised, though underlying parser methods may raise exceptions during parsing.

## State Changes:
    Attributes READ: self.environment.fragment_cache_prefix, self.environment.fragment_cache
    Attributes WRITTEN: None directly modified, but indirectly affects cache state through call_method

## Constraints:
    Preconditions: The parser must be positioned at a cache tag token, and the environment must have fragment_cache and fragment_cache_prefix attributes initialized by the extension's __init__ method. The parser stream must contain valid expressions for parsing.
    Postconditions: Returns a properly constructed CallBlock node with correct lineno set, containing the cache support call and the parsed body statements. The parser's token stream is advanced during parsing operations.

## Side Effects:
    None directly, but the resulting CallBlock will trigger cache operations during template rendering when executed. The method reads from the parser's token stream and consumes tokens during parsing operations, specifically advancing the stream to consume the cache tag and its arguments.

### `docs.examples.cache_extension.FragmentCacheExtension._cache_support` · *method*

## Summary:
Implements fragment caching logic by retrieving cached values or generating new ones when cache misses occur.

## Description:
This method provides the core caching mechanism for Jinja2 template fragments. It constructs a cache key using the environment's fragment cache prefix and the provided name, attempts to retrieve a cached value, and if none exists, executes the caller function to generate the value, stores it in cache, and returns it. This method is designed to be called internally by the template parsing process through the CallBlock mechanism.

## Args:
    name (str): The name identifier used to construct the cache key.
    timeout (int or None): The expiration time for the cached value in seconds. If None, the cache entry has no timeout.
    caller (callable): A function that generates the value to be cached when a cache miss occurs.

## Returns:
    The cached value if found, otherwise the result of executing the caller function.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.environment.fragment_cache_prefix, self.environment.fragment_cache
    Attributes WRITTEN: self.environment.fragment_cache (via add method)

## Constraints:
    Preconditions: 
    - self.environment.fragment_cache must be initialized and support get() and add() methods.
    - The caller argument must be callable.
    Postconditions:
    - If a cache hit occurs, the cached value is returned immediately without executing caller.
    - If a cache miss occurs, the caller is executed exactly once and the result is stored in the cache.

## Side Effects:
    - Reads from and writes to the fragment cache managed by self.environment.fragment_cache.
    - May execute the caller function, which could have side effects such as database queries or network requests.

