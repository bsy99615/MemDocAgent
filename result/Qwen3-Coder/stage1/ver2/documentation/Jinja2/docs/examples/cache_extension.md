# `cache_extension.py`

## `docs.examples.cache_extension.FragmentCacheExtension` · *class*

## Summary:
A Jinja2 extension that provides template fragment caching functionality through a custom "cache" tag.

## Description:
This extension enables template authors to cache expensive-to-render template fragments using a custom {% cache %} tag. When a cached fragment is encountered during template rendering, it first checks if a cached version exists and is still valid. If so, it returns the cached content; otherwise, it renders the fragment, stores it in cache, and returns the result. The extension integrates with Jinja2's template parsing and execution system to provide transparent caching capabilities.

## State:
- `tags`: Class attribute defining the template tag this extension handles, set to {"cache"}
- `fragment_cache_prefix`: String prefix prepended to cache keys, initialized as empty string via `environment.extend()`
- `fragment_cache`: Cache storage object, initialized as None via `environment.extend()` and expected to be set by the application

## Lifecycle:
- Creation: Instantiate with a Jinja2 Environment object; the constructor calls `environment.extend()` to initialize cache infrastructure
- Usage: During template parsing, Jinja2 calls `parse()` when encountering `{% cache %}` tags; during template execution, `parse()` creates a CallBlock that invokes `_cache_support()`
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[Template Parse] --> B[parse()]
    B --> C[Create CallBlock]
    C --> D[_cache_support()]
    D --> E{Cache Hit?}
    E -->|Yes| F[Return Cached Value]
    E -->|No| G[Execute Caller]
    G --> H[Store in Cache]
    H --> I[Return Result]
```

## Raises:
- None explicitly raised by __init__
- Exceptions may occur during template parsing or execution if underlying cache implementation fails

## Example:
```python
from jinja2 import Environment
from docs.examples.cache_extension import FragmentCacheExtension

# Setup environment with cache extension
env = Environment(extensions=[FragmentCacheExtension])
# Application code must set up fragment_cache
env.fragment_cache = MyCacheImplementation()

# In template: {% cache "key" 300 %}{{ expensive_operation() }}{% endcache %}
# This caches the rendered content for 300 seconds under key "key"
```

### `docs.examples.cache_extension.FragmentCacheExtension.__init__` · *method*

## Summary:
Initializes the fragment cache extension and configures the Jinja2 environment with cache infrastructure.

## Description:
Sets up the Jinja2 extension environment with required cache attributes. This method is called during extension instantiation to prepare the environment for fragment caching operations. It initializes `fragment_cache_prefix` as an empty string and `fragment_cache` as None, allowing the application to later configure the actual cache implementation.

## Args:
    environment (jinja2.Environment): The Jinja2 environment instance to extend with cache functionality

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.fragment_cache_prefix: Set to empty string ""
    - self.fragment_cache: Set to None

## Constraints:
    Preconditions:
    - environment must be a valid Jinja2 Environment instance
    - environment must support the extend() method (standard Jinja2 Environment behavior)
    
    Postconditions:
    - The environment will have fragment_cache_prefix attribute initialized to ""
    - The environment will have fragment_cache attribute initialized to None

## Side Effects:
    None

### `docs.examples.cache_extension.FragmentCacheExtension.parse` · *method*

## Summary:
Parses the Jinja2 template cache tag syntax and constructs a CallBlock node for deferred execution of cached content.

## Description:
This method implements the parsing logic for the `{% cache %}` template tag extension. It processes the cache directive by extracting the fragment name and optional timeout parameters, parsing the content block between the cache and endcache statements, and returning a CallBlock node that will invoke the `_cache_support` method at render time.

The method is called during Jinja2's template parsing phase when encountering a `{% cache %}` tag, and it transforms the template syntax into executable code that implements fragment caching.

## Args:
    parser (Parser): The Jinja2 parser instance currently processing the template

## Returns:
    nodes.CallBlock: A CallBlock AST node representing the parsed cache directive that will execute the caching logic at render time

## Raises:
    None explicitly raised - relies on Jinja2's built-in parsing exceptions

## State Changes:
    Attributes READ: None (reads from parser stream and nodes)
    Attributes WRITTEN: None (does not modify instance state directly)

## Constraints:
    Preconditions:
    - Parser must be in a valid state to parse expressions and statements
    - Template must contain properly formatted cache/endcache block
    - Environment must have fragment_cache and fragment_cache_prefix configured
    
    Postconditions:
    - Returns a valid CallBlock node that can be compiled into executable code
    - The returned node will call _cache_support method with appropriate arguments

## Side Effects:
    - Consumes tokens from the parser stream
    - Creates AST nodes that will later trigger cache operations during template rendering
    - Depends on the environment's fragment_cache implementation for actual caching behavior

### `docs.examples.cache_extension.FragmentCacheExtension._cache_support` · *method*

## Summary:
Implements a caching mechanism for Jinja2 template fragments by checking cache, generating content when needed, and storing results.

## Description:
This method provides the core caching logic for the FragmentCacheExtension. It serves as a helper method that manages fragment caching by:
1. Creating a cache key from the prefix and fragment name
2. Checking if the fragment is already cached
3. Generating the fragment content via the caller function when cache misses
4. Storing the generated content in cache with the specified timeout

The method is designed to be called internally by the template parsing system when processing cache blocks.

## Args:
    name (str): The name identifier for the cached fragment
    timeout (int or None): Cache expiration time in seconds, or None for no timeout
    caller (callable): Function that generates the fragment content when cache misses

## Returns:
    The cached fragment content if available, or the newly generated content from caller()

## Raises:
    None explicitly raised - depends on the underlying cache implementation and caller function

## State Changes:
    Attributes READ: self.environment.fragment_cache_prefix, self.environment.fragment_cache
    Attributes WRITTEN: None (modifies cache state indirectly through fragment_cache.add)

## Constraints:
    Preconditions: 
    - self.environment.fragment_cache must be initialized (not None)
    - self.environment.fragment_cache_prefix must be a string
    - caller must be callable
    Postconditions:
    - If cache hit, returns cached value immediately
    - If cache miss, stores result in cache with provided timeout

## Side Effects:
    - Reads from and writes to self.environment.fragment_cache (external cache service)
    - Calls the caller() function which may have its own side effects

