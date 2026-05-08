# `docs`

## Tree:
docs/
└── examples/
    ├── cache_extension.py
    └── inline_gettext_extension.py

## Role:
Collect and expose concise example Jinja2 extension implementations that demonstrate common template-engine customizations: fragment-level block caching and compile-time rewriting of inline gettext-style expressions.

## Description:
- Where and when this module is used:
  - These examples are registered on a Jinja2 Environment during environment construction or via the extensions mechanism when a developer wants to reuse or learn from concrete extension patterns.
  - Primary consumers:
    - Template rendering/configuration code that wants to adopt the shown patterns.
    - Test suites demonstrating extension behavior.
    - Documentation and developer guides.

- Why these components are grouped together:
  - Cohesion principle: both files demonstrate Jinja2 Extension hooks (parse/filter_stream and runtime helpers). Grouping them under docs/examples centralizes small, self-contained examples for discoverability and reuse.

## Components:
- docs.examples.cache_extension (module)
  - FragmentCacheExtension(environment)
    - One-line: Jinja2 Extension providing a {% cache %}...{% endcache %} block to memoize rendered template fragments via an external cache.
  - FragmentCacheExtension.__init__(environment)
    - One-line: Register default environment slots fragment_cache_prefix and fragment_cache.
  - FragmentCacheExtension.parse(parser)
    - One-line: Compile-time parser hook that converts a cache block into a CallBlock invoking a runtime helper.
  - FragmentCacheExtension._cache_support(name, timeout, caller)
    - One-line: Runtime helper that consults environment.fragment_cache.get/add to return or store rendered fragments.

- docs.examples.inline_gettext_extension (module)
  - InlineGettext (class)
    - One-line: Jinja2 Extension that rewrites inline gettext-like constructs inside data tokens into explicit trans/endtrans block tokens during token-stream filtering.
  - InlineGettext.filter_stream(self, stream)
    - One-line: Token-stream filter that passes non-"data" tokens unchanged and rewrites "data" tokens containing inline gettext expressions into sequences of synthetic block tokens.
  - _outside_re (compiled regex)
    - One-line: Pattern used to detect potential inline-gettext openings or escape markers in data text.
  - _inside_re (compiled regex)
    - One-line: Pattern used to scan the interior of an inline-gettext expression while parsing its contents.

Mermaid dependency graph:
graph LR
  Docs[docs/ (module)] --> Examples[docs.examples (package)]
  Examples --> CacheExt[(cache_extension.py)]
  Examples --> InlineExt[(inline_gettext_extension.py)]
  CacheExt --> FragmentCacheExt[FragmentCacheExtension]
  FragmentCacheExt --> EnvSlots[environment.fragment_cache_prefix, environment.fragment_cache]
  InlineExt --> InlineGettext[InlineGettext]
  InlineGettext --> Regexes[_outside_re, _inside_re]

## Public API:
- docs.examples.cache_extension.FragmentCacheExtension
  - Signature: class FragmentCacheExtension(environment)
  - Description: Example extension that provides a {% cache name, timeout %}...{% endcache %} block backed by environment.fragment_cache and using environment.fragment_cache_prefix for key construction.
  - Usage note:
    - Register/instantiate with a Jinja2 Environment prior to rendering templates that use the cache block.
    - Ensure the environment supplies:
      - fragment_cache_prefix: str (default "")
      - fragment_cache: object with get(key: str) -> Any | None and add(key: str, value: Any, timeout: int | None) -> None

- docs.examples.cache_extension.FragmentCacheExtension.parse
  - Signature: parse(self, parser) -> AST node
  - Description: Parser hook that compiles a cache block into a CallBlock which invokes a runtime helper when the template is rendered.

- docs.examples.cache_extension.FragmentCacheExtension._cache_support
  - Signature: _cache_support(self, name, timeout, caller) -> str
  - Description: Runtime helper invoked from the compiled CallBlock to consult environment.fragment_cache.get/add and return or store rendered content.

- docs.examples.inline_gettext_extension.InlineGettext
  - Signature: class InlineGettext()
  - Description: Extension that rewrites inline-gettext markers at tokenization/compile time.

- docs.examples.inline_gettext_extension.InlineGettext.filter_stream
  - Signature: filter_stream(self, stream: Iterable[Token]) -> Generator[Token, None, None]
  - Description: Token-stream filter that:
    - Yields non-"data" tokens unchanged.
    - For "data" tokens, scans for inline-gettext expressions using _outside_re and _inside_re and emits synthetic block tokens (trans/endtrans) and data tokens for literal parts.
  - Error behavior:
    - Raises jinja2.exceptions.TemplateSyntaxError("unclosed gettext expression") when the stream ends while an inline expression is still open; the exception is constructed using the token lineno and stream.name/stream.filename for context.

- docs.examples.inline_gettext_extension._outside_re, _inside_re
  - Signature: compiled re.Pattern
  - Description: Internal regex patterns used by InlineGettext.filter_stream; considered implementation details.

## Dependencies:
- Internal repository dependencies:
  - The module exposes example modules for import; the example modules themselves rely on the Jinja2 extension API described below.

- External (third-party / stdlib):
  - jinja2
    - Purpose: example implementations rely on Jinja2 Extension hooks, parser/tokenizer interfaces, AST node types, Token objects, and template exceptions.
  - re (stdlib)
    - Purpose: used by inline_gettext_extension for pattern matching.

## Constraints:
- Initialization and ordering:
  - InlineGettext must be registered on the Environment before compiling templates that should have inline-gettext rewriting applied.
  - FragmentCacheExtension must be instantiated/registered and the environment.fragment_cache attribute set to a backend implementing get/add before rendering templates that use {% cache %} blocks.

- Caller responsibilities:
  - For fragment caching:
    - Provide environment.fragment_cache with get/add methods and a fragment_cache_prefix string if desired.
    - Ensure name expressions yield string-like values usable for key concatenation.
    - Be aware that the example does not provide synchronization for concurrent access; backends should be thread-safe if used concurrently.
  - For inline-gettext:
    - Provide a token stream where tokens have type, value, lineno and the stream exposes .name and .filename for error reporting.

- Error behavior:
  - The inline-gettext example raises a TemplateSyntaxError("unclosed gettext expression") when an inline expression is left open at the end of the stream.

## Links to component-level documentation:
- docs.examples.cache_extension.FragmentCacheExtension
- docs.examples.cache_extension.FragmentCacheExtension.__init__
- docs.examples.cache_extension.FragmentCacheExtension.parse
- docs.examples.cache_extension.FragmentCacheExtension._cache_support
- docs.examples.inline_gettext_extension.InlineGettext
- docs.examples.inline_gettext_extension.InlineGettext.filter_stream

