# `cache_extension.py`

## `docs.examples.cache_extension.FragmentCacheExtension` · *class*

## Summary:
A Jinja2 extension that provides template fragment caching functionality through the {% cache %} template tag.

## Description:
This extension enables caching of template fragments by implementing a custom "cache" tag. When a template contains a `{% cache %}` block, the extension caches the rendered content and serves it from cache on subsequent requests until the timeout expires. The extension integrates with Jinja2's template parsing and execution system to provide transparent caching capabilities.

The extension adds two attributes to the Jinja2 environment: `fragment_cache_prefix` (string) and `fragment_cache` (cache implementation). The cache implementation must support `get(key)` and `add(key, value, timeout)` methods for proper operation.

## State:
- `tags`: Set to {"cache"}, defining the template tag this extension handles
- `fragment_cache_prefix`: String prefix added to cache keys (initialized as empty string via environment.extend)
- `fragment_cache`: Cache object used for storing cached content (initialized as None via environment.extend)

## Lifecycle:
- Creation: Instantiate with a Jinja2 Environment object; environment.extend() initializes cache attributes
- Usage: Template rendering automatically invokes parse() when encountering {% cache %} tags, then _cache_support() when executing cached blocks
- Destruction: No explicit cleanup required; relies on Environment lifecycle management

## Method Map:
```mermaid
graph TD
    A[Template Parse] --> B[parse()]
    B --> C[_cache_support(name, timeout, caller)]
    C --> D{Cache Hit?}
    D -->|Yes| E[Return Cached Value]
    D -->|No| F[Execute Caller Function]
    F --> G[Store in Cache with Timeout]
    G --> H[Return Result]
```

## Raises:
- None explicitly raised by __init__
- Exceptions may occur during template parsing or execution if environment.fragment_cache is improperly configured or lacks required methods

## Example:
```python
from jinja2 import Environment
from docs.examples.cache_extension import FragmentCacheExtension

# Setup environment with cache extension
env = Environment(extensions=[FragmentCacheExtension])

# Configure cache (example with simple dict-based cache)
env.fragment_cache = {}  # Simple dictionary cache
env.fragment_cache_prefix = "template_"

# In template:
# {% cache "my_fragment", 300 %}
#   Content to cache for 5 minutes
# {% endcache %}

# Or with just a name (no timeout):
# {% cache "my_fragment" %}
#   Content to cache indefinitely
# {% endcache %}
```

### `docs.examples.cache_extension.FragmentCacheExtension.__init__` · *method*

## Summary:
Initializes a FragmentCacheExtension instance and configures the Jinja2 environment with cache-related attributes.

## Description:
This method sets up the FragmentCacheExtension by calling the parent Extension constructor and extending the Jinja2 environment with cache configuration attributes. The extension enables template fragment caching through the {% cache %} template tag.

## Args:
    environment (jinja2.Environment): The Jinja2 environment object to extend with cache functionality

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - environment.fragment_cache_prefix (set to empty string "")
    - environment.fragment_cache (set to None)

## Constraints:
    Preconditions:
    - The environment parameter must be a valid Jinja2 Environment instance
    - The environment must support the extend() method (standard in Jinja2)
    
    Postconditions:
    - The environment will have fragment_cache_prefix attribute initialized to empty string
    - The environment will have fragment_cache attribute initialized to None
    - The environment will have the FragmentCacheExtension properly registered

## Side Effects:
    None

### `docs.examples.cache_extension.FragmentCacheExtension.parse` · *method*

## Summary:
Parses the Jinja2 cache template tag syntax and generates a CallBlock node for cached content rendering.

## Description:
This method implements the parsing logic for the Jinja2 "cache" template tag. It processes the cache tag syntax, extracts the cache name and optional timeout parameters, captures the content block until "endcache", and constructs a CallBlock node that will invoke the cache support mechanism during template rendering.

## Args:
    parser (jinja2.parser.Parser): The Jinja2 parser instance currently processing the template.

## Returns:
    jinja2.nodes.CallBlock: A CallBlock node that will execute the cached content rendering logic when the template is rendered.

## Raises:
    None explicitly raised, but may raise Jinja2 parsing exceptions during expression or statement parsing.

## State Changes:
    Attributes READ: 
        - self.environment.fragment_cache_prefix (accessed via environment attribute)
        - self.environment.fragment_cache (accessed via environment attribute)
    Attributes WRITTEN: 
        - None directly modified, but indirectly affects cache storage through environment.fragment_cache

## Constraints:
    Preconditions:
        - The parser must be positioned at a "cache" tag token
        - The parser stream must contain valid Jinja2 expressions for cache name and optional timeout
        - The template must contain matching "endcache" closing tag
    Postconditions:
        - Returns a properly constructed CallBlock node with correct line number set
        - The returned node will execute the _cache_support method during template rendering

## Side Effects:
    None directly, but the resulting CallBlock node will cause:
        - Cache lookups in environment.fragment_cache during template rendering
        - Potential cache updates in environment.fragment_cache during template rendering

### `docs.examples.cache_extension.FragmentCacheExtension._cache_support` · *method*

## Summary:
Implements a fragment caching mechanism that retrieves cached content or generates new content when cache misses occur.

## Description:
This method provides a caching layer for Jinja2 template fragments. When a fragment is requested, it first checks if the content is available in the fragment cache. If found, it returns the cached content immediately. If not found, it executes the provided caller function to generate the content, stores it in the cache with the specified timeout, and then returns the generated content. This method is designed to be called internally by the Jinja2 template parsing system through the `_cache_support` call block.

## Args:
    name (str): The cache key identifier for the fragment, combined with the environment's fragment_cache_prefix
    timeout (int or None): The expiration time for the cached fragment in seconds, or None for no timeout
    caller (callable): A function that generates the content when there's a cache miss

## Returns:
    The cached content if available, or the newly generated content from the caller function

## Raises:
    None explicitly raised, but may propagate exceptions from the caller function

## State Changes:
    Attributes READ: self.environment.fragment_cache_prefix, self.environment.fragment_cache
    Attributes WRITTEN: None directly modified, but self.environment.fragment_cache is modified indirectly through add() call

## Constraints:
    Preconditions: 
    - self.environment.fragment_cache must be initialized (not None)
    - self.environment.fragment_cache_prefix must be a string
    - caller must be callable
    Postconditions:
    - If cache hit occurs, returns cached value immediately
    - If cache miss occurs, stores generated value in cache with provided timeout

## Side Effects:
    - Reads from and writes to self.environment.fragment_cache
    - Calls the provided caller function when cache miss occurs
    - May perform I/O operations depending on the cache implementation

