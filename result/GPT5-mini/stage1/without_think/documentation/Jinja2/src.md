# `src`

## Tree:
src/
└── jinja2/
    ├── async_utils.py
    ├── debug.py
    ├── lexer.py
    ├── nativetypes.py
    ├── optimizer.py
    ├── sandbox.py
    ├── tests.py
    └── utils.py

## Role:
Provide the low-level runtime primitives and small reusable services required by the template engine: asynchronous normalization helpers, lexical/token utilities, native-code emission helpers, AST optimization, sandboxing and safety checks, testing predicates, and general-purpose utilities.

## Description:
- Where and when this module is used:
  - Primary consumers:
    * Parser and compiler (lexer → parser → optimizer → codegen) import lexer.py and optimizer.py.
    * Template runtime and renderer import async_utils.py, nativetypes.py, sandbox.py, and utils.py.
    * Developer and diagnostic tools import debug.py and utils.py.
    * Tests and built-in template "tests" registry use tests.py.
  - Typical usage contexts:
    * Lexing & parsing: lexer.py tokenizes template source and exposes Token and TokenStream for the parser.
    * Compilation: optimizer.py performs constant folding over AST nodes; nativetypes.py supplies helpers used when the engine emits native Python code or needs native concat semantics.
    * Runtime & rendering: async_utils.py normalizes awaitables and iterables for unified async rendering; sandbox.py enforces runtime attribute/item/call restrictions when templates run in restricted environments.
    * Utilities: utils.py contains caches, URL/link helpers, import resolution, JSON/HTML helpers, and small container types used repository-wide.
- Why these components are grouped:
  - They implement low-level engine concerns (parsing primitives, compilation helpers, runtime shims, and small utility types) which are highly cohesive and reused throughout the template pipeline. Grouping them keeps the core engine primitives separate from the public Environment/Template API.

## Components:
List of public submodules and their primary public symbols (signature hints are given where available). Each item is a one-line role description.

- async_utils
  - auto_aiter(iterable) -> AsyncIterator[V]: Normalize synchronous and asynchronous iterables to an async iterator.
  - auto_await(value) -> V: Await awaitables or return the value directly (helper for hybrid sync/async code).
  - auto_to_list(iterable) -> List[V]: Collect a synchronous or asynchronous iterable into a list in async code.

- debug
  - rewrite_traceback_stack(source: Optional[str]) -> BaseException: Convert an active traceback into a template-aware traceback chain for readable template errors.

- lexer
  - Failure(message: str, cls=TemplateSyntaxError): Deferred error factory to raise syntax errors with location later.
  - Lexer(environment): Compile lexing rules and produce tokens from template source.
  - Token(lineno: int, type: str, value): Immutable token object with test/test_any helpers and readable string form.
  - TokenStream(generator, name: str, filename: Optional[str]): Primed push-back stream with expect/next_if/look/close semantics.
  - _Rule(pattern, tokens, command): Passive description of a lexing rule used by Lexer.
  - OptionalLStrip: tuple-subclass marker used for lstrip behavior in lexing helpers.
  - Helpers: compile_rules(environment), get_lexer(environment), describe_token, describe_token_expr, count_newlines.

- nativetypes
  - NativeCodeGenerator: Helpers to emit native-Python representations or wrappers for dynamic children.
  - NativeEnvironment: Environment subclass tuned for native emission and a specialized concat policy.
  - NativeTemplate.render / render_async: Sync/async rendering entrypoints that call environment.concat.
  - native_concat(values): Join rendered fragments and attempt to parse the result into a Python literal where appropriate.

- optimizer
  - Optimizer(environment): AST NodeTransformer performing single-pass constant folding by attempting node.as_const.
  - optimize(node, environment): Convenience wrapper that runs Optimizer on an AST node.

- sandbox
  - SandboxedEnvironment: Enforces attribute/item/call safety checks and provides operator dispatch hooks for sandboxed execution.
  - ImmutableSandboxedEnvironment: Stronger attribute denial by consulting a known-mutable specification.
  - Utilities: is_internal_attribute(obj, attr), modifies_known_mutable(obj, attr) — helpers used by sandbox checks.

- tests
  - Collection of small predicate functions registered as template "tests" (examples include test_none, test_string, test_number, test_boolean, test_defined, test_iterable, test_integer, test_float, test_even, test_odd, test_sameas, test_undefined, test_upper, test_lower, test_filter, test_test).

- utils
  - Cycler(*items) -> Cycler: Round-robin helper with current/next/reset.
  - Joiner(sep) -> Joiner: Callable returning "" on first call and sep thereafter.
  - LRUCache(capacity) -> LRUCache: Bounded LRU mapping with support for copy and pickle; uses an internal lock for mutation methods.
  - Namespace(**kwargs) -> Namespace: Attribute-backed container backed by an internal dict.
  - _PassArg enum and decorators: pass_context / pass_environment / pass_eval_context — mark callables for runtime injection by setting jinja_pass_arg.
  - import_string(import_name: str, silent: bool=False): Resolve "module:attr" or "module.attr" strings to Python objects.
  - htmlsafe_json_dumps(obj, dumps=json.dumps, **kwargs): Serialize to JSON and escape HTML-sensitive characters; returns Markup.
  - pformat(obj) -> str: Pretty-print wrapper.
  - select_autoescape(enabled_extensions=..., disabled_extensions=..., default_for_string=True, default=False) -> Callable: Returns a function that decides whether to autoescape by template name/extension.
  - url_quote(obj, charset='utf-8', for_qs=False) -> str: Percent-encode bytes/strings with optional query-string '+' behavior.
  - urlize(text, trim_url_limit=None, rel=None, target=None, extra_schemes=None) -> str: Heuristic linkifier producing HTML-safe Markup (relies on module-level regexes).
  - open_if_exists(filename, mode='rb'): Return file object if path is a file, otherwise None.
  - consume(iterable): Exhaust an iterator discarding values.
  - generate_lorem_ipsum(...): Generate placeholder paragraphs (HTML/plain).
  - clear_caches(): Clear module-level caches (lexer/environment caches, etc.).

Mermaid dependency graph (high-level)
graph LR
  lexer --> parser[parser/compiler]
  optimizer --> nativetypes
  nativetypes --> utils
  sandbox --> utils
  async_utils --> nativetypes
  tests --> utils
  debug --> lexer

(Refer to individual component docs for precise intra-module import and call relationships.)

## Public API:
The primary interfaces this module exposes to the rest of the repository — recommended import targets and usage notes.

- jinja2.async_utils
  - auto_aiter(iterable): Use to iterate uniformly over possibly-sync or async iterables in async rendering code.
  - auto_await(value): Use to await awaitable values where templates may produce sync or async results.
  - auto_to_list(iterable): Use to collect sequences into lists in async contexts.

- jinja2.lexer
  - Lexer, Token, TokenStream: Import these for parsing/tokenization tasks. TokenStream supports lookahead, push-back, and expect semantics required by the parser.
  - Failure: Use to create deferred syntax errors that will be raised with contextual location information.

- jinja2.nativetypes
  - NativeEnvironment, NativeCodeGenerator, native_concat: Use when emitting or running native-Python-backed templates; native_concat encodes the specialized concatenation/typing semantics used by native templates.

- jinja2.optimizer
  - optimize(node, environment): Run a constant-folding pass before code generation.

- jinja2.sandbox
  - SandboxedEnvironment, ImmutableSandboxedEnvironment: Use to restrict attribute/item access, method calls, and operator behavior in untrusted templates. Consult sandbox docs for the exact safety policy and extension points.

- jinja2.tests
  - Named predicate functions: Import individual test predicates when constructing or inspecting the test registry.

- jinja2.utils
  - LRUCache: Use as a small bounded cache with pickling support; callers must honor the implemented locking model when sharing across threads.
  - import_string(import_name, silent=False): Use to dynamically resolve module or attribute references from strings (use silent=True to suppress ImportError and return None).
  - urlize, url_quote: Use for HTML-safe link generation and percent-encoding respectively.
  - select_autoescape: Use to create a callable passed to Environment to determine per-template autoescape behavior.

Usage notes:
- Many functions that produce HTML text return markupsafe.Markup; these values are already escaped for insertion into templates.
- Decorators pass_context / pass_environment / pass_eval_context only attach metadata (jinja_pass_arg) to callables; the runtime must inspect that metadata and perform argument injection.
- For components that interact with pickling (LRUCache) or native code emission (nativetypes), ensure initialization steps are replicated after deserialization (see component docs).

## Dependencies:
- Internal:
  - Parser/compiler code imports lexer and optimizer components.
  - Code generation and runtime components import nativetypes and utils.
  - Sandbox imports utility predicates (is_internal_attribute / modifies_known_mutable) from utils to implement safety checks.
  - urlize relies on module-level regular expressions compiled at import time (see urlize component doc for the regex names).

- External:
  - markupsafe (Markup, escape): For HTML-safe strings.
  - Standard library: re, ast (literal_eval), json, pprint, urllib.parse, random, threading, collections, types, operator, numbers — used by various helpers and must be present.

## Constraints:
- Thread-safety and initialization:
  - LRUCache uses an internal lock for mutation methods; if reimplemented, restore lock and bound methods after pickling/unpickling.
  - urlize and other regex-based helpers require regexes to be compiled before use; ensure module-level initialization occurs at import.
  - Sandbox enforcement depends on module-level policy data structures (UNSAFE_* sets and mutable-spec mappings). To replicate sandbox behavior, provide the same collections and consult the sandbox component docs for mutation/attribute rules.

- Callers must not assume automatic argument injection: pass_context/pass_environment/pass_eval_context only mark callables; the Environment/runtime must inspect and honor jinja_pass_arg.

- Error behavior:
  - Some utilities intentionally propagate underlying exceptions (import_string unless silent=True, json errors in htmlsafe_json_dumps). Callers should handle or let these exceptions bubble as appropriate.

Implementation guidance:
- This module groups foundational primitives; to faithfully reimplement behavior, consult the component-level documentation (token semantics in lexer, constant-folding rules in optimizer, exact sandbox policy in sandbox, regexes for urlize, and locking/pickle semantics for LRUCache). The component docs provide the precise contracts, edge cases, and messages required by the rest of the repository.

