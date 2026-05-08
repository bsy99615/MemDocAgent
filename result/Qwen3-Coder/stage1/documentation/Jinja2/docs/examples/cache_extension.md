# `cache_extension.py`

## `docs.examples.cache_extension.FragmentCacheExtension` · *class*

## Summary:
A Jinja2 extension that provides template fragment caching functionality through the {% cache %} template tag.

## Description:
This extension enables caching of template fragments by implementing a custom {% cache %} tag. When a template contains a cached fragment, the extension will first check if the cached version exists and is still valid. If so, it returns the cached content; otherwise, it renders the fragment, caches the result, and returns it. This extension is particularly useful for improving performance of templates with expensive rendering operations.

The extension integrates with Jinja2's template parsing and execution system by defining a custom tag and providing the underlying caching logic.

## State:
- `tags`: Class attribute set to {"cache"}, indicating this extension registers a "cache" template tag
- `fragment_cache_prefix`: String prefix added to cache keys, initialized as empty string via environment.extend()
- `fragment_cache`: Cache object used for storing cached template fragments, initialized as None via environment.extend()

## Lifecycle:
- Creation: Instantiate with a Jinja2 Environment object. The constructor calls super().__init__() and extends the environment with fragment_cache_prefix and fragment_cache attributes
- Usage: Template engine automatically invokes parse() when encountering the {% cache %} tag, and _cache_support() when executing cached content
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[Template Parse] --> B[parse()]
    B --> C[parser.parse_expression()]
    C --> D[parser.parse_statements()]
    D --> E[nodes.CallBlock]
    E --> F[_cache_support()]
    F --> G[fragment_cache.get()]
    G --> H{Cache Hit?}
    H -->|Yes| I[Return Cached Value]
    H -->|No| J[caller()]
    J --> K[fragment_cache.add()]
    K --> L[Return New Value]
```

## Raises:
- None explicitly raised by __init__
- Exceptions may occur during template parsing or execution if the environment is improperly configured

## Example:
```python
from jinja2 import Environment
from docs.examples.cache_extension import FragmentCacheExtension

# Create environment with cache extension
env = Environment(extensions=[FragmentCacheExtension])

# Use in template:
# {% cache "my_fragment" 300 %}
#   Expensive template content here
# {% endcache %}
```

### `docs.examples.cache_extension.FragmentCacheExtension.__init__` · *method*

## Summary:
Initializes the fragment cache extension and configures the Jinja2 environment with cache-related attributes.

## Description:
This method sets up the fragment cache extension by calling the parent Extension class constructor and extending the Jinja2 environment with necessary cache configuration attributes. It initializes `fragment_cache_prefix` as an empty string and `fragment_cache` as None, which are later used by the caching mechanism when processing template fragments.

The method is called during the instantiation of the FragmentCacheExtension class and is part of the standard Jinja2 extension initialization process. This approach separates the environment configuration from the main extension logic, making the code more modular and following Jinja2's recommended patterns for extension development.

## Args:
    environment (jinja2.Environment): The Jinja2 environment instance to extend with cache configuration attributes.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.fragment_cache_prefix: Set to empty string via environment.extend()
    - self.fragment_cache: Set to None via environment.extend()

## Constraints:
    Preconditions:
    - The environment parameter must be a valid Jinja2 Environment instance
    - The environment must support the extend() method
    
    Postconditions:
    - The environment will have fragment_cache_prefix attribute set to ""
    - The environment will have fragment_cache attribute set to None

## Side Effects:
    - Modifies the Jinja2 environment object by adding new attributes
    - No external I/O operations or service calls are performed

### `docs.examples.cache_extension.FragmentCacheExtension.parse` · *method*

## Summary:
Parses Jinja2 template cache tags and constructs a CallBlock node for deferred cache execution.

## Description:
This method is invoked by the Jinja2 parser when encountering a `{% cache %}` template tag. It processes the cache directive by parsing the required arguments (cache name and optional timeout), collecting the cached block content, and returning a CallBlock node that will execute the caching logic at render time. The method is part of the FragmentCacheExtension class that enables template fragment caching.

## Args:
    parser (Parser): Jinja2 parser instance currently processing the template

## Returns:
    nodes.CallBlock: A CallBlock node that will invoke the _cache_support method with parsed arguments when the template is rendered

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Parser must be in a valid state to parse expressions and statements
        - Template must contain properly formatted cache tags with matching endcache
    Postconditions:
        - Returns a properly constructed CallBlock node with correct line number set
        - The returned node will execute _cache_support method with appropriate arguments

## Side Effects:
    - Consumes tokens from the parser stream
    - Creates and returns a CallBlock node for later execution

### `docs.examples.cache_extension.FragmentCacheExtension._cache_support` · *method*

## Summary:
Implements a caching mechanism for Jinja2 template fragments by checking cache first, generating content if missing, and storing results with timeout.

## Description:
This private method provides the core caching logic for the FragmentCacheExtension. It serves as a bridge between the template parsing phase and the runtime execution phase, handling the cache lookup and population for cached template fragments. The method is invoked internally by the Jinja2 template engine when processing cache blocks.

## Args:
    name (str): Unique identifier for the cached fragment
    timeout (int or None): Cache expiration time in seconds, or None for no timeout
    caller (callable): Function that generates the fragment content when not cached

## Returns:
    Any: Cached value if found, otherwise the result of calling the caller function

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.environment.fragment_cache_prefix, self.environment.fragment_cache
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - self.environment.fragment_cache must be initialized and support .get() and .add() methods
        - caller must be callable
        - name must be a string
    Postconditions:
        - If cache miss occurs, the returned value is stored in fragment_cache with the specified timeout
        - If cache hit occurs, the cached value is returned without calling caller

## Side Effects:
    - Reads from and writes to self.environment.fragment_cache
    - Calls the caller function when cache misses occur

