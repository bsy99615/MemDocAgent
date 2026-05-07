# `cache_extension.py`

## `docs.examples.cache_extension.FragmentCacheExtension` · *class*

## Summary:
A Jinja2 extension that provides template fragment caching functionality through a custom "cache" tag.

## Description:
This extension enables caching of template fragments by implementing a custom "cache" tag that can be used in Jinja2 templates. When a template contains a {%- cache key %}...{%- endcache %} block, the extension caches the rendered content and serves it from cache on subsequent requests until the timeout expires.

The extension integrates with a caching system provided through the Jinja2 environment's fragment_cache attribute. It allows developers to cache expensive template rendering operations while providing control over cache keys and expiration times.

## State:
- fragment_cache_prefix (str): Prefix added to cache keys to avoid naming conflicts. Default is empty string.
- fragment_cache (object): Cache implementation that supports get(key), add(key, value, timeout) methods. Default is None.

## Lifecycle:
- Creation: Instantiate with a Jinja2 Environment object. The extension automatically registers itself with the environment via environment.extend().
- Usage: Templates containing {%- cache key %}...{%- endcache %} blocks will trigger the caching mechanism during template rendering.
- Destruction: No explicit cleanup required; relies on Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[Template Parse] --> B[parse]
    B --> C[_cache_support]
    C --> D[fragment_cache.get]
    D --> E{Cache Hit?}
    E -->|Yes| F[Return Cached Value]
    E -->|No| G[caller()]
    G --> H[fragment_cache.add]
    H --> I[Return Value]
```

## Raises:
- None explicitly raised by __init__
- Template parsing errors may occur if cache tag syntax is malformed

## Example:
```python
from jinja2 import Environment
from docs.examples.cache_extension import FragmentCacheExtension

# Create environment with cache extension
env = Environment(extensions=[FragmentCacheExtension])

# Template with caching - single argument (key only)
template_source1 = '''
{%- cache user_profile %}
    <div>User: {{ user.name }}</div>
{%- endcache %}
'''

# Template with caching - two arguments (key and timeout)
template_source2 = '''
{%- cache user_profile, 3600 %}
    <div>User: {{ user.name }}</div>
{%- endcache %}
'''

template1 = env.from_string(template_source1)
template2 = env.from_string(template_source2)
result1 = template1.render(user={'name': 'John'})
result2 = template2.render(user={'name': 'John'})
```

### `docs.examples.cache_extension.FragmentCacheExtension.__init__` · *method*

## Summary:
Initializes the fragment cache extension and configures the Jinja2 environment with cache-related attributes.

## Description:
This method sets up the fragment cache extension by calling the parent Extension class constructor and extending the Jinja2 environment with cache configuration attributes. It prepares the environment to support template fragment caching functionality by initializing the fragment_cache_prefix and fragment_cache attributes.

The method is called during the instantiation of the FragmentCacheExtension class and is part of the standard Jinja2 extension initialization process. It ensures that the environment has the necessary cache infrastructure to support the custom cache tag functionality.

## Args:
    environment (jinja2.Environment): The Jinja2 environment instance to extend with cache capabilities.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - fragment_cache_prefix (str): Set to empty string as default value
    - fragment_cache (object): Set to None as default value

## Constraints:
    Preconditions:
    - The environment parameter must be a valid Jinja2 Environment instance
    - The environment must support the extend() method (standard in Jinja2)
    
    Postconditions:
    - The environment will have fragment_cache_prefix attribute initialized to ""
    - The environment will have fragment_cache attribute initialized to None

## Side Effects:
    - Modifies the provided Jinja2 environment object by adding cache-related attributes
    - No external I/O or service calls are made

### `docs.examples.cache_extension.FragmentCacheExtension.parse` · *method*

## Summary:
Parses the `{% cache %}` template tag syntax and constructs a CallBlock node that will invoke the cache support mechanism.

## Description:
This method is part of the Jinja2 template extension system and handles the parsing of the `{% cache %}...{% endcache %}` template syntax. It processes the cache tag arguments, captures the enclosed template content, and generates a CallBlock node that will execute the caching logic when the template is rendered.

The method is called during Jinja2's template parsing phase when the parser encounters a `{% cache %}` tag. It expects at least one argument (the cache key name) and optionally a second argument (timeout duration), followed by template content that gets cached.

## Args:
    parser (Parser): The Jinja2 parser object that provides access to the template stream and parsing capabilities

## Returns:
    nodes.CallBlock: A CallBlock AST node that represents the parsed cache construct, which will invoke `_cache_support` when executed

## Raises:
    None explicitly raised - relies on underlying Jinja2 parsing methods which may raise parsing-related exceptions

## State Changes:
    Attributes READ: 
    - self.environment.fragment_cache_prefix (accessed indirectly via environment)
    - self.environment.fragment_cache (accessed indirectly via environment)
    
    Attributes WRITTEN: 
    - None directly modified by this method

## Constraints:
    Preconditions:
    - The parser must be positioned at a `{% cache %}` token when this method is called
    - The parser stream must contain valid Jinja2 expressions for the arguments
    - The template must contain a matching `{% endcache %}` tag to close the cached block
    
    Postconditions:
    - Returns a properly constructed CallBlock node with correct line number set
    - The returned node will execute the `_cache_support` method with appropriate arguments when rendered

## Side Effects:
    None - This method only performs parsing operations and returns AST nodes. It doesn't perform I/O or modify external state directly.

### `docs.examples.cache_extension.FragmentCacheExtension._cache_support` · *method*

## Summary:
Implements a caching mechanism for Jinja2 template fragments by checking cache, generating content when needed, and storing results with timeout.

## Description:
This method provides a caching layer for template fragment rendering. When a fragment is requested, it first checks if the cached version exists and is still valid. If so, it returns the cached content. Otherwise, it executes the provided caller function to generate fresh content, stores it in cache with the specified timeout, and returns the result. This method is designed to be called from within the Jinja2 template parsing phase via the `CallBlock` node.

## Args:
    name (str): Cache key identifier for the template fragment
    timeout (int or None): Expiration time for cached content in seconds. None indicates no expiration
    caller (callable): Function that generates the content when cache misses occur

## Returns:
    Any: Cached content if available and valid, otherwise the result of executing the caller function

## Raises:
    None explicitly raised - relies on underlying cache implementation for exceptions

## State Changes:
    Attributes READ: 
        - self.environment.fragment_cache_prefix
        - self.environment.fragment_cache
    
    Attributes WRITTEN:
        - self.environment.fragment_cache (via add operation)

## Constraints:
    Preconditions:
        - self.environment.fragment_cache must be initialized (not None)
        - self.environment.fragment_cache_prefix must be a string
        - caller must be callable
    
    Postconditions:
        - If cache hit occurs, returns cached value immediately
        - If cache miss occurs, caller() is executed exactly once
        - Result is stored in cache with provided timeout
        - Return value is either cached or freshly generated content

## Side Effects:
    - Reads from and writes to self.environment.fragment_cache
    - Executes the caller function when cache misses occur
    - May perform I/O operations depending on cache implementation

