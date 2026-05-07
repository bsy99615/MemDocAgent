# `src.jinja2`

## Tree:
jinja2/
├── async_utils.py
├── debug.py
├── lexer.py
├── nativetypes.py
├── optimizer.py
├── sandbox.py
├── tests.py
└── utils.py

## Role:
Provide foundational runtime services and small, widely reused primitives for the template engine: asynchronous normalization helpers, lexical/token utilities, native-code generation helpers, AST optimization, sandboxing and safety predicates, and general-purpose utilities and tests used across parsing, compilation, and rendering layers.

## Description:
- Where and when this module is used:
  - Consumers: parser and compiler (lexer → parser → optimizer → codegen), template runtime and renderer (async helpers, sandbox checks, URL/link helpers), and developer-facing utilities (debug tracebacks, lorem ipsum, pretty-print).
  - Primary usage contexts:
    * Lexing & parsing: lexer.py provides tokenization and TokenStream used by the parser.
    * Compilation: optimizer.py performs constant-folding; nativetypes.py provides helpers for native-code emission and the native Environment/concat behavior.
    * Runtime & rendering: async_utils.py normalizes awaitables/iterables; sandbox.py enforces attribute/call safety at runtime; utils.py contains caches, linkifiers, and small helpers.
    * Tests and filters: tests.py defines small predicate functions registered as template "tests".

- Module cohesion:
  - These submodules implement low-level engine concerns that are reused by higher-level components. Grouping them keeps parsing/compilation/runtime primitives in one place separate from public Environment and Template APIs.

## Components:
For full implementation details see the component-level documentation for each named module/class/function (component docs are stored alongside their source-level descriptions). The list below is a high-level index with a one-line role for each public symbol.

- async_utils
  - auto_aiter(iterable) -> AsyncIterator[V]: Normalize sync/async iterables to an async iterator.
  - auto_await(value) -> V: Await awaitables or return value; respects module short-circuit primitives.
  - auto_to_list(iterable) -> List[V]: Collect a sync/async iterable into a list in async code.

- debug
  - rewrite_traceback_stack(source: Optional[str]) -> BaseException: Convert active traceback into a template-aware traceback chain.

- lexer
  - Failure(message: str, cls=TemplateSyntaxError): Deferred error factory to raise syntax errors later with location.
  - Lexer(environment): Compile regex rules and provide tokenize/tokeniter/wrap pipelines.
  - Token(lineno:int, type:str, value): Immutable token object with test/test_any and __str__ helpers.
  - TokenStream(generator, name, filename): Primed, push-back token stream with expect/next_if/look/close semantics.
  - _Rule(pattern, tokens, command): Passive description of a single lexing rule.
  - OptionalLStrip: tuple-subclass marker used by lexer state.
  - Helpers: compile_rules(environment), get_lexer(environment), describe_token, describe_token_expr, count_newlines.

- nativetypes
  - NativeCodeGenerator: helpers to emit native-Python representations or wrappers for non-constant children.
  - NativeEnvironment: Environment subclass tuned for native emission and a concat policy.
  - NativeTemplate.render / render_async: sync/async entrypoints that call environment.concat on rendered fragments.
  - native_concat(values): join fragments and attempt to parse into a Python literal.

- optimizer
  - Optimizer(environment): NodeTransformer performing single-pass constant folding (generic_visit attempts node.as_const).
  - optimize(node, environment): Convenience wrapper that runs Optimizer over an AST node.

- sandbox
  - SandboxedEnvironment: Attribute/item/call safety checks, operator dispatch methods, and formatting hooks for sandboxed template execution.
  - ImmutableSandboxedEnvironment: Stronger attribute denial by consulting known-mutable specification.
  - Utilities: is_internal_attribute(obj, attr), modifies_known_mutable(obj, attr) — used by sandbox checks.

- tests
  - Small predicate functions used by the template tests registry (examples: test_none, test_string, test_number, test_boolean, test_defined, test_in, test_iterable, test_integer, test_float, test_even/odd, test_sameas, test_undefined, test_upper/lower, test_filter, test_test, etc.). See tests.py component docs for exact semantics.

- utils
  - Cycler(...) with current/next/reset: simple round-robin helper.
  - Joiner(sep): callable that returns "" on first call then sep thereafter.
  - LRUCache(capacity): bounded LRU mapping with copy/pickle support (mutation methods use an internal lock; see component doc for concurrency details).
  - Namespace(...): attribute-backed container whose attribute access routes to an internal dict.
  - _PassArg enum and helpers; decorators pass_context / pass_environment / pass_eval_context that set jinja_pass_arg on callables to signal argument injection at call time.
  - import_string(import_name, silent=False): resolve "module:attr" or "module.attr" strings to Python objects.
  - htmlsafe_json_dumps(obj, dumps=json.dumps, **kwargs): serialize to JSON and escape HTML-sensitive characters, returning Markup.
  - pformat(obj): pretty-print wrapper.
  - select_autoescape(enabled_extensions=..., disabled_extensions=..., default_for_string=True, default=False): returns a callable(template_name)->bool deciding autoescape by extension.
  - url_quote(obj, charset='utf-8', for_qs=False): bytes-percent-encode with optional query-string '+' behavior.
  - urlize(text, trim_url_limit=None, rel=None, target=None, extra_schemes=None): heuristic linkifier (requires module-level regexes described in urlize component docs).
  - open_if_exists(filename, mode='rb'): open only when path is a file, else return None.
  - consume(iterable): exhaust an iterator, discarding values.
  - generate_lorem_ipsum(...): generate placeholder paragraphs (HTML/plain).
  - clear_caches(): convenience to clear module-level caches (e.g., environment/lexer caches).

Mermaid dependency graph (high-level)
graph LR
  lexer --> parser[parser/compiler]
  optimizer --> nativetypes
  nativetypes --> utils
  sandbox --> utils
  async_utils --> nativetypes
  tests --> utils
  debug --> lexer

(Use component-level docs for exact direct imports and call relationships.)

## Public API:
- For each top-level submodule, the principal callable/class to import:
  - jinja2.async_utils.auto_aiter / auto_await / auto_to_list: async iteration/await helpers.
  - jinja2.lexer.Lexer / TokenStream / Token: tokenization and stream APIs. Consult lexer component docs for tokenize/wrap/tokeniter behavior and error conditions.
  - jinja2.nativetypes.NativeEnvironment / native_concat: for native-Python code emission and concat semantics.
  - jinja2.optimizer.optimize: run a constant-folding pass over an AST node.
  - jinja2.sandbox.SandboxedEnvironment / ImmutableSandboxedEnvironment: use these classes to run templates in a sandbox; see sandbox docs for attribute and call-safety contracts.
  - jinja2.tests.<test_name>: small test predicates registered by name in environments.
  - jinja2.utils.LRUCache: small bounded cache — see component doc for locking and pickling details.
  - jinja2.utils.import_string: resolve module/attribute reference strings; use silent=True for optional lookups.
  - jinja2.utils.urlize / url_quote: HTML-safe linkification and quoting helpers (see their docs for regex dependencies and punctuation handling).

Usage notes:
- Consult the component-level documentation for exact signatures, edge cases, and exceptions (each component doc contains the implementation-level contract required to reimplement it).
- Many helpers return markupsafe.Markup when producing HTML-safe output; treat such results as already escaped for template insertion.
- Decorators pass_context / pass_environment / pass_eval_context only set a marker attribute (jinja_pass_arg) on the object to signal the runtime; they do not validate callables or change invocation themselves. The runtime must inspect that attribute and act accordingly.

## Dependencies:
- Internal module dependencies:
  - lexer relies on helpers and token constants documented in its component doc.
  - sandbox consults utilities (is_internal_attribute, modifies_known_mutable) for its attribute-safety policy; see those component docs for the exact behavior and the expected global specification structures.
  - urlize relies on module-level regular expressions (see urlize component doc for the exact names and their expected behavior: _http_re, _email_re).

- External libraries:
  - markupsafe (Markup, escape) — for HTML-safe outputs.
  - re, ast (literal_eval), json, pprint, urllib.parse, random, threading, collections, types, operator, numbers — used throughout utilities and must be available.

## Constraints:
- Thread-safety and initialization:
  - Several components have specific initialization or runtime constraints; for example, LRUCache binds runtime helpers in _postinit and restores them after unpickling. If you reimplement LRUCache, ensure bound deque-methods and the write lock are re-established after deserialization (see LRUCache component doc).
  - Sandbox checks depend on module-level specifications (UNSAFE_* and _mutable_spec). Provide these collections to achieve the same policy behavior (see sandbox component docs).
  - urlize requires compiled regexes present at module import or before invocation (see urlize component doc for the exact regex names and matching expectations).

- Error and exception behavior:
  - Many utilities deliberately propagate underlying exceptions (e.g., import_string unless silent=True; json serialization errors in htmlsafe_json_dumps). Component docstrings specify when exceptions are converted vs propagated — consult them when reimplementing.

## Implementation guidance:
- Do not infer or copy behavior across components; rely on each component's documentation for precise input/output contracts, exceptions, and edge-case handling.
- Use the component-level docs as authoritative when reconstructing internal constants, regexes, or exact error messages.
- Where the module-level doc refers to concurrency or locking behavior, follow the corresponding component implementation details (e.g., LRUCache methods and comments) rather than assuming global invariants.

This module package is a collection of focused runtime building blocks. To reimplement it faithfully, consult each submodule's component documentation for the precise semantics, inputs, outputs, edge cases, and invariants required by callers.

---

## Files

- [`async_utils.py`](jinja2/async_utils.md)
- [`debug.py`](jinja2/debug.md)
- [`lexer.py`](jinja2/lexer.md)
- [`nativetypes.py`](jinja2/nativetypes.md)
- [`optimizer.py`](jinja2/optimizer.md)
- [`sandbox.py`](jinja2/sandbox.md)
- [`tests.py`](jinja2/tests.md)
- [`utils.py`](jinja2/utils.md)

