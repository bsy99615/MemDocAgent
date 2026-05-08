# `docs`

## Tree:
docs/
└── conftest.py

## Role:
Provide lightweight helpers that make HTML/XML fixture files accessible as parsel.Selector objects and expose that helper to execution namespaces used by tests or documentation parsers.

## Description:
This module is used at test and documentation-preparation time to simplify working with static fixture files packaged with the repository. Primary consumers include:
- Test suites and test fixtures that need to parse HTML/XML examples.
- Doctest or documentation executors (doctest runners, Sybil-like tools) that accept a mutable execution namespace and expect pre-populated helpers.
- Documentation parsing utilities that convert static fixture files into selector objects for extraction/validation.

These functions are grouped here because they implement a single cohesive concept: helpers for reading packaged static files and exposing a selector-creation helper to execution environments. Grouping keeps fixture I/O and namespace setup logic local to the docs/test-support layer and separate from production code.

## Components:
- load_selector(filename: str | os.PathLike, **kwargs) -> parsel.Selector
  - Read a UTF-8 file from the module's _static directory (or an absolute path) and return a parsel.Selector created from the file contents; forwards kwargs to parsel.Selector.
- setup(namespace: MutableMapping[str, Any]) -> None
  - Insert the load_selector callable into the supplied mapping under the key "load_selector".

Mermaid dependency graph:
graph LR
    A[setup(namespace)] --> B[assign "load_selector" -> namespace]
    B --> C[namespace mapping (MutableMapping)]
    D[load_selector(filename, **kwargs)] --> E[os.path.dirname(__file__)]
    D --> F[os.path.join(base_dir, "_static", filename) or absolute path]
    D --> G[open(..., encoding="utf-8")]
    D --> H[parsel.Selector(text=..., **kwargs)]
    setup --> D
    subgraph stdlib
        E
        F
        G
    end
    subgraph third-party
        H
    end

## Public API:
- load_selector(filename: str | os.PathLike, **kwargs) -> parsel.Selector
  - Description: Load the specified file (relative to docs/_static or an absolute path) as UTF-8 text and construct a parsel.Selector from it. All keyword arguments are forwarded to parsel.Selector (e.g., type="html" / type="xml").
  - Usage notes:
    - Prefer passing a filename relative to the module's _static subdirectory for packaged fixtures, e.g., "example.html".
    - If an absolute path is passed it bypasses the packaged _static prefix and is used as-is.
    - Exceptions from file I/O (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) and from parsel.Selector are propagated to the caller.
  - See component doc: docs.conftest.load_selector

- setup(namespace: MutableMapping[str, Any]) -> None
  - Description: Mutate the provided mapping by assigning namespace["load_selector"] = load_selector so callers running examples or doctests can call load_selector directly from that namespace.
  - Usage notes:
    - namespace must support item assignment (i.e., implement __setitem__); a plain dict is the common usage.
    - The function returns None and performs an in-place mutation; any existing value under the "load_selector" key will be overwritten.
  - See component doc: docs.conftest.setup

## Dependencies:
Internal imports:
- None (this module lives in the docs/test-support layer and does not import other repository modules).

Standard library:
- os (used to compute dirname(__file__) and join path components)
- typing (typing hints: MutableMapping, Any, Union, os.PathLike) — used conceptually for signatures and caller guidance
- builtins.open (for file I/O) and path semantics provided by os.path

Third-party:
- parsel.Selector — required to build CSS/XPath selector objects from the file contents; callers must ensure parsel is available in the environment where tests or docs are executed.

## Constraints:
- Caller-supplied filename:
  - The function does not sandbox or sanitize filename. If filename is absolute or contains traversal segments (e.g., "../"), os.path.join semantics can cause files outside docs/_static to be read. Callers that accept untrusted input must validate or canonicalize paths before calling.
  - Files must be UTF-8 encoded; attempting to read non-UTF-8 files will raise UnicodeDecodeError.
- setup(namespace):
  - The namespace must be a mutable mapping supporting __setitem__ for string keys. Passing None or an immutable mapping will raise a TypeError or mapping-specific exception.
- Thread-safety and concurrency:
  - The module itself performs no global mutation beyond the provided namespace in setup. Concurrent calls to setup that mutate the same mapping may race and overwrite values; callers requiring concurrent safety should coordinate mapping access externally.
- Initialization order:
  - No special initialization required prior to using load_selector beyond importing the module and ensuring that docs/_static (or the absolute path provided) contains the fixture files.
  - parsel must be importable in the execution environment where load_selector is invoked.

Additional notes:
- The module intentionally keeps responsibilities minimal: it centralizes consistent encoding and path resolution for packaged fixture files and provides a standard name ("load_selector") for test/documentation namespaces. For detailed behavior, edge cases, and examples, consult the component-level documentation entries: docs.conftest.load_selector and docs.conftest.setup.

---

## Files

- [`conftest.py`](docs/conftest.md)

