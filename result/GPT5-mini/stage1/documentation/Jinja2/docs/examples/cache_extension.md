# `cache_extension.py`

## `docs.examples.cache_extension.FragmentCacheExtension` · *class*

## Summary:
A small Jinja2 extension that provides a {% cache %} ... {% endcache %} block to render and memoize template fragments using an external fragment cache. It looks up a cached value by a composed key and returns it, otherwise renders the block, stores the result in the cache with an optional timeout, and returns the rendered result.

## Description:
This class implements a Jinja2 Extension exposing a "cache" block tag. Template authors use it as:
    {% cache "name", 60 %} ... template fragment ... {% endcache %}
When the template is rendered, the extension asks the configured fragment cache for the value keyed by (fragment_cache_prefix + name). If present, the cached value is returned; otherwise the block body is rendered, added to the cache with the specified timeout, and then returned.

When to instantiate:
- Attach an instance to a Jinja2 Environment when you want per-template fragment caching.
- Typical creation occurs when constructing/configuring a Jinja2 Environment or when registering extensions programmatically. The Environment will call __init__(environment) and the extension will add default attributes to the environment.

Motivation and responsibility:
- Separates template fragment caching concerns from rendering logic: the extension manages the tag parsing and the integration point with whatever cache is provided on the environment.
- It does not implement a cache backend itself — it requires the environment to provide a fragment_cache object with a small, well-defined interface (get/add). This keeps the extension backend-agnostic and testable.

## State:
Attributes established by this class and environment interactions:

- tags: set[str]
  - Value in code: {"cache"}
  - Invariant: identifies the Jinja2 tags the extension parses. Constant for the class.

- environment (implicit): jinja2.Environment
  - Provided to __init__ by the Jinja2 extension system.
  - After initialization, the environment will have two extended attributes:
    - fragment_cache_prefix (str)
      - Default value set by __init__: "" (empty string)
      - Valid values: any string. It is concatenated with the fragment name to create the cache key.
      - Invariant: must be a string; used as prefix when computing keys.
    - fragment_cache (object or None)
      - Default value set by __init__: None
      - Expected interface (required by _cache_support):
        - get(key: str) -> Any | None: return stored value or None if not present
        - add(key: str, value: Any, timeout: int | None) -> None: store the value with optional timeout
      - Invariant: when rendering cache blocks, fragment_cache must be a cache-like object implementing get and add; otherwise attribute accesses will raise at runtime.

No other instance attributes are created by this extension. The extension relies on the environment object for runtime state.

Class invariants:
- environment.fragment_cache_prefix is a string.
- environment.fragment_cache either implements get/add or remains None; callers must set it to a proper cache implementation before rendering templates that use the cache tag.

## Lifecycle:
Creation:
- Instantiate by passing a Jinja2 Environment instance to the constructor (this is how Jinja2 constructs extensions).
- The constructor calls environment.extend(fragment_cache_prefix="", fragment_cache=None) to ensure the environment has these attributes with defaults.
- Required argument: environment (a Jinja2 Environment-like object with an extend method).

Usage / Typical method sequence:
1. During parsing of templates, Jinja2 calls parse(parser) when it encounters a "cache" tag.
   - parse consumes the tag token and the following expression(s): the fragment name expression and an optional timeout expression (separated by a comma).
   - parse reads the block body up to the matching endcache tag and returns a nodes.CallBlock that, when the template is executed, will invoke this extension's _cache_support method.
2. At template render time, the Jinja2 runtime invokes _cache_support(name, timeout, caller) for this block:
   - name: evaluated value of the first expression (expected to be a string or string-like)
   - timeout: evaluated value of the second expression, or None if omitted (expected to be an integer number of seconds or None)
   - caller: a zero-argument callable that renders the block body and returns the rendered fragment (string or markup)
3. _cache_support constructs a cache key by concatenating environment.fragment_cache_prefix and name, queries fragment_cache.get(key), and:
   - If get returns a non-None value -> return it immediately (cached value used).
   - If get returns None -> call caller() to render the fragment, call fragment_cache.add(key, rendered_value, timeout), and return the rendered_value.

Destruction / Cleanup:
- The extension holds no resources requiring explicit cleanup (no open filehandles or network connections).
- It does not implement context manager protocol or close(). Cleanup of cache entries is the responsibility of the cache backend.
- If consumers set environment.fragment_cache to an object that needs explicit shutdown, they must manage that object's lifecycle separately.

## Method Map:
flowchart LR
    P[Template parsing] --> ParseMethod[FragmentCacheExtension.parse(parser)]
    ParseMethod --> CallBlockNode[nodes.CallBlock(self.call_method("_cache_support", args))]
    RenderTime --> CacheSupport[FragmentCacheExtension._cache_support(name, timeout, caller)]
    CacheSupport --> GetCall[fragment_cache.get(key)]
    GetCall -- found --> ReturnCached[return cached value]
    GetCall -- not found --> CallerCall[rv = caller()]
    CallerCall --> AddCall[fragment_cache.add(key, rv, timeout)]
    AddCall --> ReturnNew[return rv]

(Above: Template parsing path creates a CallBlock node; at render time the runtime calls _cache_support, which either uses the cache or renders and stores the fragment.)

## Raises:
- __init__(environment)
  - AttributeError: if the provided environment does not expose an extend method. The constructor calls environment.extend(...); absence of that attribute will raise.
  - No other exceptions are raised explicitly by __init__.

- parse(parser)
  - May raise Jinja2 parser exceptions when the template syntax is malformed (e.g., missing closing endcache). These are errors raised by the parser object and are not created by this extension directly.
  - It also expects parser.stream to provide tokens as per Jinja2; misuse of parser may raise AttributeError/TypeError from the parser interface.

- _cache_support(name, timeout, caller)
  - AttributeError: if environment.fragment_cache is None or does not implement get/add, attempting to call fragment_cache.get(...) will raise an AttributeError.
  - TypeError: if fragment_cache.get/add raise TypeError for bad key types, or if name is not string-like and concatenation with fragment_cache_prefix fails.
  - Exceptions raised by caller(): rendering the block body may raise arbitrary exceptions from template execution; these propagate out of _cache_support.

Notes:
- The class itself does not validate the types of name or timeout; callers should ensure name renders to a string and timeout to an integer or None. The cache backend may impose further constraints.

## Example:
1) Setup (conceptual steps; do not include specific imports or environment construction here):
   - Create or obtain a Jinja2 Environment.
   - Register this extension with the Environment (e.g., include it in the environment's extensions list or otherwise instantiate it with the environment).
   - Provide a fragment cache backend on the environment that implements:
       - get(key: str) -> Any | None
       - add(key: str, value: Any, timeout: int | None) -> None
     Then set environment.fragment_cache_prefix to a suitable prefix string if desired.

2) Template usage:
   - In a template, use:
       {% cache "user_list", 300 %}
           ... expensive rendering for user list ...
       {% endcache %}
     When rendered:
       - The extension computes key = fragment_cache_prefix + "user_list".
       - If fragment_cache.get(key) returns a value, that value is injected directly into the rendered template.
       - Otherwise the block body is rendered, stored into the cache with add(key, value, 300), and returned.

3) Minimal recommended cache backend behavior:
   - get: return stored value or None when not found (None is used by the extension to mean "cache miss").
   - add: store the value and honor timeout semantics if applicable. The extension does not use return values from add.

Implementation hints for reimplementation:
- The parse method must:
  - Consume the 'cache' token (first parser.stream token).
  - Parse one expression (the fragment name).
  - Optionally, if a comma follows, parse a second expression (timeout); otherwise supply a constant None node for the timeout argument.
  - Parse statements until encountering 'endcache' and collect the body.
  - Return a CallBlock node that calls a method on the extension (named _cache_support) with the parsed arguments and with the collected body as the block content.

- The runtime _cache_support method must:
  - Compute the key as environment.fragment_cache_prefix + name (string concatenation).
  - Use environment.fragment_cache.get(key) and treat a non-None return as cached content.
  - On cache miss, call the provided caller callable to render the block content, store it via environment.fragment_cache.add(key, value, timeout), and return the rendered content.

This documentation contains the complete behavioral contract and integration points necessary to reimplement FragmentCacheExtension compatible with Jinja2's extension API.

### `docs.examples.cache_extension.FragmentCacheExtension.__init__` · *method*

## Summary:
Initializes the extension and registers two fragment-caching configuration slots on the provided Jinja2 environment, ensuring the environment is aware of the keys this extension uses.

## Description:
This constructor is executed when the extension instance is created and connected to a Jinja2 environment. Typical callers:
- Jinja2's extension loading process (e.g., when an Environment instantiates configured extensions during Environment construction or when add_extension/load_extensions is used).
- Any code that explicitly constructs the extension with a Jinja2 Environment and registers it.

This logic is kept in __init__ so that the extension's required environment attributes are established as soon as the extension is created and so other extension logic can rely on these environment attributes being present. Centralizing environment setup here avoids repeating the same initialization in multiple methods and ensures the environment-level defaults are configured before the extension is used.

## Args:
    environment (jinja2.Environment or compatible object): The Jinja2 environment instance (or any object exposing an extend(**kwargs) method) that will host this extension. There is no default; the caller must supply an environment object that accepts keyword-based extension of attributes.

## Returns:
    None

## Raises:
    AttributeError: If the provided environment does not implement an extend method and the call to environment.extend(...) fails.
    Any exception raised by the parent Extension.__init__ when called with the provided environment (for example, if the environment is invalid for the base class). These exceptions are propagated.

## State Changes:
Attributes READ:
    None on self (this method does not access or read any self.<attr> attributes).

Attributes WRITTEN:
    None on self (this method does not modify self.<attr> attributes).

Note: The method mutates the provided environment (see Side Effects) but does not change the extension instance state.

## Constraints:
Preconditions:
    - The caller must pass an object named environment that implements an extend(**kwargs) method accepting keyword arguments and applying them to the environment (the standard jinja2.Environment meets this requirement).
    - The environment must be a valid argument for the parent Extension.__init__ (the base class may validate or store the environment).

Postconditions:
    - environment.extend(fragment_cache_prefix="", fragment_cache=None) has been invoked. As a result, the environment has been requested to register the keys 'fragment_cache_prefix' and 'fragment_cache' with the provided values (an empty string and None respectively). Exact behavior (e.g., whether existing values are overwritten) depends on the environment.extend implementation.

## Side Effects:
    - Calls the base class constructor: super().__init__(environment), which may register the extension with the environment or perform other framework-level setup.
    - Calls environment.extend(fragment_cache_prefix="", fragment_cache=None), which mutates the provided environment object (typically by setting attributes or defaults named fragment_cache_prefix and fragment_cache).
    - No I/O or external network calls are performed by this method itself.

### `docs.examples.cache_extension.FragmentCacheExtension.parse` · *method*

## Summary:
Parses the extension's opening tag and its block body into a Jinja2 CallBlock AST node that will, at render time, invoke this extension's _cache_support method with two expression arguments (the first required, the second optional) and the parsed body. The resulting node's lineno is set to the opening tag's line.

## Description:
This parse method implements the Jinja2 Extension API for handling a custom block tag (the opening tag name is registered elsewhere in the extension). It runs during template compilation (AST construction) when the parser dispatches to this extension's parse method for the matching opening tag.

Lifecycle and known callers:
- Called by Jinja2's parsing pipeline during template compilation when the active parser reaches the extension's opening tag.
- The returned nodes.CallBlock is not executed at parse time; during rendering the CallBlock will call the extension instance's _cache_support runtime method with the parsed arguments and block body.

Why this is a separate method:
- Token consumption and AST construction are responsibilities of the extension's parse implementation per Jinja2's Extension API. Separating parse (compile-time AST work) from _cache_support (runtime cache logic) keeps compile-time concerns isolated from runtime behavior and follows the expected extension structure.

## Args:
    parser (jinja2.parser.Parser): The active Jinja2 parser instance positioned at the opening tag. The parser must provide:
        - stream: a token stream object that is iterable and whose next() yields a token with a lineno attribute,
        - parse_expression(): a method that parses and returns an expression AST node from the current parser position,
        - parse_statements(end_tokens, drop_needle=True): a method that parses and returns a list/node representing the block body up to one of end_tokens.

## Returns:
    jinja2.nodes.CallBlock: An AST CallBlock node constructed with:
        - call: the node returned by self.call_method("_cache_support", args) where args is a list of two AST nodes described below,
        - three additional positional parameters as shown in the code: an empty list, an empty list, and the parsed body node,
        - lineno: explicitly set to the lineno taken from the opening tag token.
    Details of the two argument AST nodes passed to _cache_support:
        - First positional argument: the AST node returned by the first parser.parse_expression() call (required).
        - Second positional argument: if parser.stream.skip_if("comma") evaluated to True, this is the AST node from a second parser.parse_expression() call; otherwise it is nodes.Const(None).
    Edge cases:
        - The function always returns a nodes.CallBlock when parsing succeeds; it does not return None.

## Raises:
    - StopIteration: If next(parser.stream) is called when the parser's token stream is exhausted (no next token available), StopIteration will propagate.
    - Any exception raised by parser.parse_expression(): e.g., jinja2.exceptions.TemplateSyntaxError or other parser-specific exceptions if the expressions are invalid or unexpected tokens are encountered.
    - Any exception raised by parser.parse_statements(...): e.g., if a matching "endcache" token is missing or malformed, parser.parse_statements may raise a parser error (commonly TemplateSyntaxError).
    - AttributeError / TypeError: If the provided parser does not implement the expected attributes/methods (stream, parse_expression, parse_statements, or stream.skip_if), attribute access will raise an error.

Exact conditions that trigger raises:
    - StopIteration occurs exactly if parser.stream has no next token when next(parser.stream) is invoked to obtain lineno.
    - parse_expression() and parse_statements(...) propagate their own error types for syntax problems; this method does not catch them.

## State Changes:
Attributes READ:
    - self.call_method: invoked to create the call node that references the runtime helper "_cache_support".
    - (implicitly) self: the instance is referenced to create the method call node but no instance attributes are read beyond the method lookup.

Attributes WRITTEN:
    - None. This method does not assign to or mutate any self.<attr> attributes.

Parser / external state mutated:
    - parser.stream position is advanced: the opening tag token is consumed by next(parser.stream) and subsequent tokens are consumed while parsing expressions and the block body.
    - parser internal position is advanced past the closing "endcache" token because parse_statements(..., drop_needle=True) consumes the end token.

## Constraints:
Preconditions:
    - parser must be a valid Jinja2 parser positioned at this extension's opening tag (the token returned by next(parser.stream) should correspond to the opening tag).
    - The template must include a matching "endcache" closing tag for the block; parse_statements is invoked with end token "name:endcache".
    - parser must implement the methods/attributes used here: stream (iterable), parse_expression, parse_statements, and stream.skip_if.

Postconditions:
    - The parser's position is advanced past the entire block and its "endcache" token.
    - The returned nodes.CallBlock has lineno equal to the opening tag's lineno and a call node that will invoke _cache_support with exactly two positional AST arguments (second may be nodes.Const(None)).
    - No attributes on self are modified.

## Side Effects:
    - No I/O, network access, or external service calls occur.
    - AST nodes (jinja2.nodes.CallBlock and related expression nodes) are created and returned.
    - Parser/token stream state is mutated (tokens consumed).
    - The runtime cache behavior is not executed here; runtime effects occur later when the CallBlock invokes _cache_support during rendering.

### `docs.examples.cache_extension.FragmentCacheExtension._cache_support` · *method*

## Summary:
Look up a rendered fragment in the environment's fragment cache and return it if present; otherwise call the provided renderer, store its result in the fragment cache with the given timeout, and return the newly rendered result. This mutates the external fragment cache via its add method but does not change the extension object's own attributes.

## Description:
This method is the runtime helper used by the FragmentCacheExtension Jinja2 extension to implement the "cache" tag. The parse method builds a CallBlock that invokes this method during template rendering; therefore this method is called at template render time by the Jinja2 runtime (via the CallBlock produced by FragmentCacheExtension.parse). It is implemented as a separate method so it can be referenced by name from the AST (callable by Jinja2's call_method) and executed in the rendering phase rather than in the parsing phase.

Known callers and context:
- FragmentCacheExtension.parse: constructs a nodes.CallBlock which references this method, so the Jinja2 rendering engine calls _cache_support when the template is rendered.
- Jinja2 template rendering pipeline: the CallBlock invokes this method at render-time to either fetch the cached fragment or execute the inner block (caller) to produce and cache the fragment.

Why this is a separate method:
- It must be addressable by Jinja2's call_method mechanism (needs a method name and a callable signature).
- It encapsulates runtime cache lookup, miss handling, and cache-write side effects in one place, keeping parse-time logic minimal and focused on AST construction.

## Args:
    name (str): A unique fragment name or key suffix used to build the final cache key. It is concatenated with the environment.fragment_cache_prefix using the + operator.
    timeout (int | None): Timeout (in seconds) to attach to the cached value when storing it. May be None if the underlying cache supports a non-expiring entry. The method does not validate ranges; the value is passed through to fragment_cache.add.
    caller (callable): A zero-argument callable that, when invoked, returns the rendered fragment. This is typically the CallBlock body renderer supplied by Jinja2.

## Returns:
    Any: The cached value returned by fragment_cache.get(key) if the cache contains a non-None value for the key; otherwise the value returned by caller(). Note: a stored cache value of None is treated as a cache miss (the method treats only non-None get results as hits).

## Raises:
    AttributeError: If self.environment is missing or does not provide fragment_cache_prefix or fragment_cache attributes, or if fragment_cache does not implement get/add.
    TypeError: If fragment_cache_prefix and name cannot be concatenated with + (e.g., incompatible types), or if caller is not callable.
    Any exception raised by caller(): exceptions produced while rendering the block will propagate unchanged.
    Any exception propagated from fragment_cache.get or fragment_cache.add is also raised as-is.

## State Changes:
Attributes READ:
    self.environment
    (implicitly) self.environment.fragment_cache_prefix
    (implicitly) self.environment.fragment_cache

Attributes WRITTEN:
    None on self (the extension object itself is not modified)

Note: The method mutates external state by calling self.environment.fragment_cache.add(...), which alters the cache storage object rather than attributes on the extension instance.

## Constraints:
Preconditions:
    - self.environment must be set (the Extension base provides this in __init__).
    - self.environment.fragment_cache must be an object exposing get(key) and add(key, value, timeout) methods.
    - self.environment.fragment_cache_prefix should be of a type that supports concatenation with name using + (commonly an empty string or other string).
    - caller must be a callable taking no arguments.

Postconditions:
    - If fragment_cache.get(key) returned a non-None value, that value is returned and fragment_cache.add is not called.
    - If fragment_cache.get(key) returned None, caller() is invoked; its return value is passed to fragment_cache.add(key, value, timeout) and then returned to the caller.
    - No attributes on self are changed.

## Side Effects:
    - Calls self.environment.fragment_cache.get(key) (read-only from the extension's perspective).
    - Potentially calls self.environment.fragment_cache.add(key, value, timeout), which mutates the external cache (I/O or in-memory mutation depending on cache implementation).
    - Invokes caller(), which may perform arbitrary rendering work and side effects; any exceptions raised by caller propagate outward.

