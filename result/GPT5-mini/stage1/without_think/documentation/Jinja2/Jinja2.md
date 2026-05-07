# `Jinja2`

## Tree:
Jinja2/
    docs/                     # Example extension snippets and usage examples for developers
        examples/
            cache_extension.py        # Example: fragment-level caching extension
            inline_gettext_extension.py# Example: inline-gettext token rewrite extension
    scripts/                  # Offline utilities and repository maintenance scripts
        generate_identifier_pattern.py# Generator that emits a compact Unicode identifier regex module
    src/
        jinja2/                # Core library package (runtime primitives and utilities)
            async_utils.py     # Async iteration/await helpers
            debug.py           # Template-aware traceback rewriting utilities
            lexer.py           # Tokenizer, Token & TokenStream primitives
            nativetypes.py     # Helpers for native-Python-backed templates and concat semantics
            optimizer.py       # AST optimization (constant folding)
            sandbox.py         # Sandboxed environment classes and safety checks
            tests.py           # Predicate functions exposed as template "tests"
            utils.py           # General-purpose helpers (LRUCache, urlize, import_string, etc.)

## Purpose:
- Problem solved and why it matters
  - Provides the core building blocks of an extensible templating engine: tokenization, optimization, native-code helpers, sandboxed execution, and a toolbox of utilities used by template rendering and integrations.
  - Enables safe, efficient, and extensible template rendering across web frameworks, CLI tools, and other host applications.

- Target users and scenarios
  - Application developers embedding templates in services.
  - Integrators writing extensions or custom Environments.
  - Maintainers running offline maintenance tasks (e.g., identifier regex generation) and consulting example extensions.

- Position in the ecosystem
  - A reusable library (importable package) intended to be embedded into applications and extended; not a standalone service.

## Architecture:
- End-to-end data flow (flowchart TD):
  flowchart TD
    SourceTemplate[Source template text] --> Lexer[lexer.py: Tokenizer (TokenStream)]
    Lexer --> Parser[parser/compiler (upstream component; not present in provided tree)]
    Parser --> Optimizer[optimizer.py: AST constant-folding]
    Optimizer --> CodeGen[Native/bytecode code generation (nativetypes.py assists)]
    CodeGen --> Renderer[Template runtime: render / render_async]
    Renderer --> AsyncHelpers[async_utils.py]
    Renderer --> Sandbox[sandbox.py for restricted execution]
    Utils[utils.py] --> Renderer
    Scripts[scripts/generate_identifier_pattern.py] -->|generates| IdentifierModule[_identifier.py used by lexer/token rules]
    DocsExamples[docs/examples/*] -->|extension patterns| Renderer

- Key abstractions and architectural patterns
  - Pipeline: clear separation of concerns across lexing → parsing → optimizing → code generation → rendering.
  - Extension hooks: compile-time parser hooks and token-stream filters allow extensions to rewrite or inject behavior (examples under docs/examples).
  - Sandbox policy object: pluggable environment subclasses that intercept attribute/item/call operations to restrict untrusted templates.
  - Async normalization: utilities that let renderers treat synchronous and asynchronous iterables/awaitables uniformly.

## Entry Points:
- Importable API package
  - package: src/jinja2 (import as jinja2)
  - Exposes: submodules and public symbols such as jinja2.lexer, jinja2.utils, jinja2.async_utils, jinja2.sandbox, jinja2.nativetypes, jinja2.optimizer, and jinja2.tests.
  - Target audience: application developers, extension authors, and integrators.

- Maintenance script
  - scripts/generate_identifier_pattern.py
  - Purpose: Offline generator that writes a compact Unicode identifier pattern module (../src/jinja2/_identifier.py relative to the script).
  - Invocation: run from the repository (no special runtime flags required). Requires filesystem write permission to the target path.
  - Audience: maintainers and contributors; not intended for runtime use in applications.

- Example extensions
  - docs/examples/cache_extension.py and docs/examples/inline_gettext_extension.py
  - Purpose: Demonstrate how to implement parser-based and token-stream-based Jinja2 extensions.
  - Audience: extension authors and documentation readers.

## Core Features:
- Tokenization primitives (lexer.py) — Token, TokenStream, lexer construction helpers.
- Async/sync normalization (async_utils.py) — Helpers for awaitables and iterables.
- AST optimization (optimizer.py) — Constant-folding passes for AST nodes.
- Native template helpers (nativetypes.py) — Native-Python template helpers and concat policies.
- Sandboxed execution (sandbox.py) — Environment classes enforcing attribute/item/call restrictions.
- Utility toolbox (utils.py) — LRUCache, urlize/url_quote, import_string, select_autoescape, htmlsafe JSON dumps, and small containers.
- Example extension patterns (docs/examples) — Fragment caching and inline-gettext rewriting.
- Identifier regex generation (scripts/generate_identifier_pattern.py) — Offline pipeline producing a compact regex module for identifier handling.

For each feature, see the corresponding module-level documentation stored in memory for signatures, behaviors, and edge cases.

## Dependencies:
- Key external dependency
  - markupsafe (Markup / escape)
    - Role: Returned values from many utilities are Markup objects representing HTML-safe strings; markupsafe is required at runtime.

- Standard-library dependencies (explicit)
  - Common across modules: re, ast, json, pprint, urllib.parse, sys, os, threading, collections, types, operator, numbers
    - Role: Regex handling, literal parsing, JSON serialization, URL quoting, concurrency primitives, container utilities, and numeric predicates.
  - scripts/generate_identifier_pattern.py (offline generator) depends on the Python standard library modules:
    - re: pattern handling and final compilation checks
    - sys: to determine sys.maxunicode when enumerating code points
    - os / os.path: to compute repository-relative output path and perform file I/O
    - builtins ord, chr: convert between code points and characters
    - These are all standard-library features; the generator does not require third-party packages.
- Version/compatibility notes
  - The code targets modern Python 3 interpreters. markupsafe must be present for runtime. Exact minimum Python version is not specified in the provided tree; consult project packaging/CI for pinned constraints.

## Configuration:
- Environment-level configuration surfaces (examples)
  - environment.fragment_cache and environment.fragment_cache_prefix (used by the cache extension example).
  - select_autoescape callable (created by utils.select_autoescape) used to configure per-template autoescape decisions.
- These configuration points are typically set when constructing an Environment or by subclassing Environment.

## Extension Points:
- Token-stream filters: implement filter_stream(token_stream) to rewrite tokens during lexing/tokenization (see docs/examples/inline_gettext_extension.py).
- Parser hooks: implement parse(parser) in an Extension to compile custom blocks into CallBlocks or AST transformations (see docs/examples/cache_extension.py).
- Environment subclassing: swap or extend runtime policies with SandboxedEnvironment or NativeEnvironment to change safety and concat semantics.
- Decorator metadata: pass_context / pass_environment / pass_eval_context attach metadata that the renderer must inspect to perform argument injection.

## Quick-start guidance for maintainers
- Run the offline identifier generator:
  - Execute scripts/generate_identifier_pattern.py from the repository root; it writes ../src/jinja2/_identifier.py and requires write permission.
- Experiment with extension examples:
  - Register classes from docs/examples/ onto an Environment during development to observe compile-time and token-stream behaviors.
- Reimplementation roadmap:
  - Implement lexer/token primitives (Token, TokenStream).
  - Provide parser/AST and a code generation stage (the parser/compiler is considered an upstream component; it is not included in the provided snapshot).
  - Implement optimizer passes and runtime helpers (async_utils, nativetypes, sandbox, utils) to match the contracts described in the module-level documentation.

---

## Modules

- [`docs`](docs.md)
- [`docs/examples`](docs/examples.md)
- [`scripts`](scripts.md)
- [`src`](src.md)
- [`src/jinja2`](src/jinja2.md)

