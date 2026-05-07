# `docs`

## Tree:
docs/
└── conf.py

## Role:
Provide small, self-contained helpers used by the Sphinx configuration to read files relative to the docs package and to extract a canonical package version string from a source file without importing the package.

## Description:
Where and when this module is used:
- Primary consumer: the Sphinx configuration process that builds project documentation (conf.py). Typical call sites in a repo: variables such as release, version, or long_description within the same conf.py use these helpers to obtain the project version and to include README/CHANGELOG text.
- Secondary usage: any tooling that needs a safe, import-free way to read files relative to the docs directory or to parse a top-level __version__ assignment from a source file.

Why these components are grouped together:
- Cohesion principle: both helpers deal with file-reading operations used during documentation build time. Grouping them keeps docs-specific I/O concerns (resolving paths relative to the docs package, consistent encoding, and a safe pattern for reading version strings) in a single place and avoids importing the project package while generating docs.

## Components:
- read(*parts: Union[str, os.PathLike]) -> str
  - Reads and returns the UTF-8 decoded text of a file resolved by joining the docs package directory with the supplied path components.
- find_version(*file_paths: Union[str, os.PathLike]) -> str
  - Forwards the supplied path components to read to obtain the file contents, then searches that text using a regular expression (with multiline mode) to find the first top-level __version__ assignment and return the string inside the quotes.

Mermaid dependency graph (internal relationships)
graph LR
    conf_py[conf.py module] --> read_func[read(*parts) -> str]
    conf_py --> find_version_func[find_version(*file_paths) -> str]
    find_version_func --> read_func

(Interpretation: conf.py exposes read and find_version; find_version calls read.)

Links to component-level documentation:
- docs.conf.read — detailed behavior, exceptions, and examples for read
- docs.conf.find_version — detailed behavior, regex constraints, and examples for find_version

## Public API:
- read(*parts: Union[str, os.PathLike]) -> str
  - Description: Open and read the file located at path = os.path.join(<docs package directory>, *parts) and return its entire contents decoded as UTF-8.
  - Usage notes:
    - Pass one or more path components (e.g., "README.rst" or "..", "README.md").
    - If no parts are given, the function will attempt to open the docs package directory itself and will raise IsADirectoryError on most systems.
    - Exceptions from file I/O and decoding (FileNotFoundError, IsADirectoryError, PermissionError, UnicodeDecodeError) propagate to the caller.
  - See: docs.conf.read for examples and exact exception behaviors.

- find_version(*file_paths: Union[str, os.PathLike]) -> str
  - Description: Read the file resolved by the supplied path components (delegates to read) and return the first version string captured from a top-level assignment of the exact form:
    __version__ = 'x' or __version__ = "x"
    Implementation details: the function calls read(*file_paths) to obtain a UTF-8-decoded string, then runs re.search with the pattern:
    ^__version__ = ['"]([^'"]*)['"]
    using re.M (multiline) mode. The first capture group's contents are returned.
  - Usage notes:
    - Intended for use in Sphinx conf.py to populate release/version variables without importing the package.
    - Delegates all file I/O errors to read (they are not caught inside find_version).
    - If the file is read successfully but no matching top-level __version__ assignment is found, the function raises RuntimeError("Unable to find version string.").
  - See: docs.conf.find_version for exact pattern constraints and examples.

## Dependencies:
Internal (other repo modules):
- None required. Both helpers are self-contained and intended to be used from within docs/conf.py or other docs-time code in the repository.

External (standard library):
- os / os.path
  - Purpose: resolve and join filesystem paths; allow passing os.PathLike objects.
- re
  - Purpose: find_version uses a regular expression with multiline mode to locate a top-level __version__ assignment.
- typing (optional)
  - Purpose: type hints in documentation (Union[str, os.PathLike]) — not required at runtime.

Note: All I/O uses built-in open() with explicit UTF-8 decoding.

## Constraints:
- Input types:
  - Callers must pass path components as str or os.PathLike objects. Passing other types will raise a TypeError during path join.
- File existence and readability:
  - Both functions perform file I/O and will raise FileNotFoundError, IsADirectoryError, PermissionError, or UnicodeDecodeError as raised by underlying operations. Callers should handle these where appropriate.
- find_version pattern constraints (critical):
  - The version assignment must be a single top-level line that starts at the beginning of the line (no leading whitespace).
  - Exactly one ASCII space on each side of the '=' is required by the used regex: "__version__ = '1.2.3'" or "__version__ = \"1.2.3\"".
  - Variations that will NOT match: leading whitespace, tabs, missing spaces around '=', computed values, multi-line assignments, or different formatting.
  - If no match is found but the file was read successfully, find_version raises RuntimeError("Unable to find version string.").
- Thread-safety and state:
  - Both functions are pure in the sense that they do not modify module-level state and have no side effects other than reading files. They are safe to call concurrently from multiple threads provided callers understand concurrent file access semantics at the OS level.
- Initialization prerequisites:
  - No special initialization is required beyond importing the module. read resolves paths relative to the docs package location; callers should ensure that the runtime working environment makes the docs package importable if relative path resolution depends on package location.
- Ordering:
  - No ordering constraints between calls. find_version always calls read internally; callers that need to avoid repeated disk access should cache results themselves.

---

## Files

- [`conf.py`](docs/conf.md)

