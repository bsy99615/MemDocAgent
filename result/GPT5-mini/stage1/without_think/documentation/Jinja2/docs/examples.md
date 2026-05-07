# `docs.examples`

## Tree:
examples/
├── cache_extension.py
└── inline_gettext_extension.py

## Role:
Provide two example Jinja2 extension implementations that illustrate common template-engine customizations: fragment-level block caching and compile-time rewriting of inline gettext-style expressions. The module collects small, self-contained extension examples intended for reuse or reference.

## Description:
- Where and when used:
  - These extensions are registered on a Jinja2 Environment during environment construction or via the extensions mechanism. They are used at two different stages:
    - FragmentCacheExtension: used at template render time to avoid re-rendering expensive template fragments via a {% cache %}...{% endcache %} block.
    - InlineGettext: used at template compile time to transform inline gettext-like markers in text nodes into explicit {% trans %}...{% endtrans %} blocks.
  - Primary consumers: template rendering code, test suites demonstrating extension behavior, and application code that configures Jinja2 Environments.

- Why grouped together:
  - Both files serve as concise examples of implementing Jinja2 Extension hooks (parse/filter_stream and runtime methods). Grouping keeps example extensions in one location for discoverability and reuse.

## Components:
- cache_extension.py
  - FragmentCacheExtension(environment)
    - One-line: Jinja2 Extension providing a {% cache %}...{% endcache %} block to memoize rendered template fragments via an external cache.
    - See: docs.examples.cache_extension.FragmentCacheExtension
  - FragmentCacheExtension.__init__(environment)
    - One-line: Register default environment slots fragment_cache_prefix and fragment_cache.
    - See: docs.examples.cache_extension.FragmentCacheExtension.__init__
  - FragmentCacheExtension.parse(parser)
    - One-line: Compile-time parser hook that converts a cache block into a CallBlock invoking the runtime helper.
    - See: docs.examples.cache_extension.FragmentCacheExtension.parse
  - FragmentCacheExtension._cache_support(name, timeout, caller)
    - One-line: Runtime helper that consults environment.fragment_cache.get/add to return or store rendered fragments.
    - See: docs.examples.cache_extension.FragmentCacheExtension._cache_support

- inline_gettext_extension.py
  - InlineGettext (class)
    - One-line: Jinja2 Extension that rewrites inline gettext-like constructs inside data tokens into explicit trans/endtrans block tokens during token-stream filtering.
    - See: docs.examples.inline_gettext_extension.InlineGettext
  - InlineGettext.filter_stream(self, stream)
    - One-line: Token-stream filter that passes non-"data" tokens unchanged and rewrites "data" tokens containing inline gettext expressions into sequences of synthetic block tokens.
    - See: docs.examples.inline_gettext_extension.InlineGettext.filter_stream
  - _outside_re (compiled regex)
    - One-line: Pattern used to detect potential inline-gettext openings or escape markers in data text; only applied to "data" tokens.
  - _inside_re (compiled regex)
    - One-line: Pattern used to scan the interior of an inline-gettext expression (parentheses, nested tokens); only applied while inside an opened expression.

Mermaid dependency graph:
graph LR
  subgraph cache_extension.py
    CClass[FragmentCacheExtension]
    CParse[parse(parser)]
    CRun[_cache_support(name, timeout, caller)]
    CClass --> CParse
    CClass --> CRun
    CRun --> EnvFrag[environment.fragment_cache]
    CRun --> EnvPrefix[environment.fragment_cache_prefix]
  end
  subgraph inline_gettext_extension.py
    IClass[InlineGettext]
    IFilt[filter_stream(stream)]
    IRegex1[_outside_re]
    IRegex2[_inside_re]
    IClass --> IFilt
    IFilt --> IRegex1
    IFilt --> IRegex2
  end

## Public API:
- FragmentCacheExtension
  - Signature: class FragmentCacheExtension(environment)
  - Description: Extension class to attach to a Jinja2 Environment to support a {% cache name, timeout %}...{% endcache %} block that uses environment.fragment_cache for get/add operations.
  - Usage note:
    - Register with the Environment (via extensions or instantiate with the environment).
    - Ensure environment has:
      - fragment_cache_prefix: str (default "")
      - fragment_cache: object implementing get(key: str) -> Any|None and add(key: str, value: Any, timeout: int|None) -> None
    - The cache key computed is environment.fragment_cache_prefix + name (string concatenation).
    - Name should render to a string-like value; timeout is passed through to the backend.

- InlineGettext
  - Signature: class InlineGettext()
  - Description: Extension that rewrites inline-gettext markers at tokenization/compile time.
  - Usage note:
    - Attach to Environment before compiling templates that use inline gettext syntax.
    - No environment attributes required.
    - The filter_stream method expects the lexer token stream to have .name and .filename attributes; it will pass through any non-"data" tokens unchanged and only inspect "data" tokens for inline-gettext patterns.

- InlineGettext.filter_stream(stream)
  - Signature: filter_stream(self, stream: Iterable[Token]) -> Generator[Token, None, None]
  - Description: Jinja2 filter hook invoked with the lexer Token stream. Yields tokens; for input tokens with type != "data" it yields them unchanged. For "data" tokens it splits text, handles escape sequences, and emits synthetic block tokens (block_begin, name("trans"), block_end, ... , block_begin, name("endtrans"), block_end).
  - Error behavior: raises jinja2.exceptions.TemplateSyntaxError("unclosed gettext expression") when the stream ends while an inline expression is still open. The exception uses stream.name and stream.filename for context.

- Module internals (not required for external use)
  - _outside_re, _inside_re
    - Compiled regular expressions used exclusively by InlineGettext.filter_stream when processing "data" tokens. They are implementation details and subject to change.

## Dependencies:
- Internal repository dependencies:
  - None besides assuming standard Jinja2 extension API objects (parser, nodes, Token) are available from the jinja2 package.

- External dependencies:
  - jinja2
    - Purpose: Extension base class, parser/tokenizer interfaces, AST node types (nodes.CallBlock), Token type, and exceptions for syntax errors.
  - re (stdlib)
    - Purpose: Compiling patterns used by InlineGettext.filter_stream for text matching.

## Constraints:
- Initialization and ordering:
  - FragmentCacheExtension: must be instantiated with an object that supports the Jinja2 Extension contract (the environment). The constructor calls environment.extend(fragment_cache_prefix="", fragment_cache=None). Before rendering templates that use {% cache %}, callers must set environment.fragment_cache to an object implementing get/add.
  - InlineGettext: register before compiling templates that rely on inline-gettext conversion.

- Call-time constraints and preconditions:
  - FragmentCacheExtension:
    - The fragment name expression must evaluate to a string-like value that can be concatenated to the fragment_cache_prefix.
    - The configured fragment_cache must implement:
      - get(key: str) -> Any|None (None signals a cache miss)
      - add(key: str, value: Any, timeout: int|None) -> None
    - Backends must be prepared for possible concurrent access if templates are rendered concurrently.
  - InlineGettext.filter_stream:
    - The provided stream must be an iterable producing Token objects with attributes type, value, lineno and stream must expose .name and .filename for error messages.
    - Non-"data" tokens are yielded unchanged; regex scanning and rewriting are only applied to "data" tokens.

- Thread-safety:
  - Neither extension itself provides synchronization. If the fragment_cache backend will be shared across threads, it must ensure thread-safety.

- Error behavior:
  - Jinja2 parser/lexer exceptions (TemplateSyntaxError, etc.) propagate from parsing/compilation.
  - InlineGettext.filter_stream raises TemplateSyntaxError("unclosed gettext expression") with the last processed token lineno, stream.name, and stream.filename when an inline expression is not properly closed.

## Usage example (conceptual):
- Fragment caching:
  1. env = Environment(...)
  2. env.add_extension(FragmentCacheExtension) or instantiate FragmentCacheExtension(env)
  3. env.fragment_cache = my_cache_backend  # implements get/add
  4. env.fragment_cache_prefix = "site1:"
  5. Use in template: {% cache "sidebar_users", 300 %}...{% endcache %}

- Inline gettext conversion:
  1. env = Environment(...)
  2. env.add_extension(InlineGettext)
  3. In template source include inline gettext markers inside text; during compilation they will be rewritten into trans/endtrans blocks.

## Links to component docs:
- docs.examples.cache_extension.FragmentCacheExtension
- docs.examples.cache_extension.FragmentCacheExtension.__init__
- docs.examples.cache_extension.FragmentCacheExtension.parse
- docs.examples.cache_extension.FragmentCacheExtension._cache_support
- docs.examples.inline_gettext_extension.InlineGettext
- docs.examples.inline_gettext_extension.InlineGettext.filter_stream

---

## Files

- [`cache_extension.py`](examples/cache_extension.md)
- [`inline_gettext_extension.py`](examples/inline_gettext_extension.md)

