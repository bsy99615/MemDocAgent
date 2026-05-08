# `parsel`

## Tree:
parsel/
    docs/                      - Documentation & test helpers used by doctests and test fixtures
        conftest.py            - Test/doc helper: exposes load_selector and setup for fixtures
    parsel/                    - Core library package (implementation modules and public API live here; internal layout omitted)

Notes:
- The tree shows the repository top-level. The parsel/parsel package contains the library implementation and its modules (not enumerated here because detailed module-level layout was not provided).

## Purpose:
- Problem solved:
    - Provide a reusable Python library for constructing selector objects from HTML/XML fixture content and supporting extraction-driven workflows in applications and tests.
    - Provide lightweight test/documentation helpers that make it easy to load packaged HTML/XML fixtures as selector objects during doctest or unit-test execution.
- Why it matters:
    - Centralizes fixture-loading behavior and encoding/path handling for tests and docs.
    - Offers an importable API (the parsel package) for downstream consumers to parse and work with HTML/XML content.
- Target users and scenarios:
    - Developers writing extraction/parsing code and tests that validate HTML/XML contents.
    - Documentation and test tooling that execute examples or doctests and need a pre-populated execution namespace.
- Position:
    - A standalone, importable Python library plus test/doc helpers. It is intended for embedding in applications and test suites, not as a long-running service.

## Architecture:
- High-level flow (Mermaid flowchart):
flowchart TD
    A[Raw HTML / XML input (string or file)] --> B[parsel.Selector creation]
    B --> C[Consumer code uses Selector to run selection/extraction]
    subgraph Test/Docs
        D[docs.conftest.load_selector] --> B
        E[docs.conftest.setup(namespace)] --> F[Namespace with load_selector]
        F --> G[Doctest / test runners invoking examples]
    end

- Key architectural points:
    - Separation of concerns: production parsing/extraction code lives in parsel/, test and documentation helpers live under docs/.
    - Single, small test helper module (docs.conftest) that:
        - Reads UTF-8 fixture files from a _static directory by convention (or accepts absolute paths)
        - Returns a parsel.Selector created from the file content
        - Can inject that helper into an execution namespace for doctests
    - The repository exposes an importable package (parsel) as the primary integration point for applications and tests.

## Entry Points:
- Importable package:
    - import parsel
      - What it exposes: the package-level public API (types, classes, and functions) implemented under parsel/. The exact class and function names and signatures are defined inside the package modules; consult module-level docs for exact signatures.
      - Audience: application and library developers who need to parse and extract from HTML/XML.
- Test/doc helpers (docs/conftest):
    - load_selector(filename: str | os.PathLike, **kwargs)
      - What it exposes: reads a UTF‑8-encoded file from docs/_static (or uses an absolute path) and returns a parsel.Selector built from the file contents; forwards kwargs to the Selector constructor.
      - Audience: test authors and documentation runners that need selectors from fixture files.
    - setup(namespace: MutableMapping[str, Any])
      - What it exposes: injects load_selector into the supplied mapping under the key "load_selector" so doctests or other executors can call it directly.
      - Audience: test frameworks or documentation tools that accept an execution namespace.

## Core Features (high level):
- Construct selector objects from text or fixture files
    - Description: Create selector objects from HTML/XML content for downstream selection/extraction. (Implemented in parsel/ package; docs.conftest uses this.)
- Test and documentation fixture utilities
    - Description: Load fixture files and inject a convenience loader (load_selector) into execution namespaces to simplify doctests and tests. (Implemented in docs/conftest.py)
- Composable extraction usage (consumer responsibility)
    - Description: The package is intended to be used by client code to perform selection and extraction tasks. The specifics of available selection APIs and transformation helpers are documented in module-level docs inside parsel/.

## Dependencies:
- Standard library:
    - os and built-in file I/O: used by docs/conftest to resolve paths and read files as UTF-8.
    - typing (for type hints in documentation and expected signatures).
- Internal:
    - parsel (the package in this repository): docs.conftest constructs and returns parsel.Selector objects; therefore the parsel package must be importable in the environment where docs helpers are executed.
- Notes about parser backends and optional extras:
    - The repository-level view does not assert a particular HTML/XML parsing backend or third-party requirement for the parsel package itself; check the package metadata (pyproject.toml / setup.cfg) and module-level docs for exact runtime dependencies and optional extras.

## Configuration:
- No global runtime configuration is visible at the top level in the supplied tree.
- docs.conftest.load_selector behavior depends on file paths:
    - By convention it looks for fixture files under docs/_static; passing an absolute path bypasses that convention.
    - Files must be UTF-8 encoded; non-UTF-8 files will raise UnicodeDecodeError on read.

## Extension Points:
- Test helpers:
    - Replace or augment the injected namespace via docs.conftest.setup(namespace) to add additional helpers or fixtures for doctests.
- Library usage:
    - Extend or wrap the public API offered by parsel/ (subclassing or adapter patterns) — exact extension points depend on the package's module-level public API.

## Where to find implementation details:
- Module-level and component-level documentation inside parsel/ (not included here) contains:
    - Exact class and function names, parameter names and types, return types, and raised exceptions.
    - Concrete examples of selection and extraction usage.
- The docs/conftest component documentation (available in memory) contains precise and actionable details for load_selector and setup.

## Practical notes for developers:
- To run tests or examples that use docs helpers, ensure the parsel package is importable in the test environment.
- Use docs.conftest.setup to populate a namespace with load_selector when running doctests that reference fixtures by name.
- Consult the package's module-level docs (or inspect parsel/__init__.py) to learn the exact public API surface and implementation modules.

## Summary:
This repository provides an importable parsel package (core parsing/selector functionality) and a small docs helper module (docs/conftest.py) that makes loading fixture files and creating parsel.Selector objects convenient for tests and documentation. For reimplementation or deeper integration, consult the module-level source files inside parsel/ and the package metadata for dependency constraints.

---

## Modules

- [`docs`](docs.md)
- [`parsel`](parsel.md)

