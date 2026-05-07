# `scripts`

## Tree:
scripts/
└── generate_identifier_pattern.py

## Role:
Provide a focused pipeline that enumerates Unicode characters relevant to Python identifiers but not matched by \w, collapses contiguous code-point runs into ranges, formats those ranges compactly, and writes a small Python module containing a compiled regular-expression "pattern" suitable for use by the rest of the project.

## Description:
- Where and when used:
  - This module is used as an offline generation utility: a maintainer runs it to regenerate a compact identifier regular-expression fragment that is then written into the repository source tree (target: ../src/jinja2/_identifier.py relative to the script).
  - Primary consumers are downstream code that imports the generated module (the generated file exposes a compiled regex named pattern). The generator itself is intended to be invoked manually or as part of a build/maintenance step rather than from application runtime.
- Why these components are grouped together:
  - Cohesion principle: all components belong to a single generation pipeline that transforms a stream of Unicode code points into a compact regex fragment and persists it to disk. Pure helper functions (enumeration, collapsing, formatting) are separated from the I/O orchestration (main) so they can be tested independently and reused.

## Components:
- Functions:
  - build_pattern(ranges: Iterable[Tuple[str, str]]) -> str
    - Build a compact character-range string from an iterable of (start, end) character pairs (e.g., "a-z0-9_").
    - See component doc: scripts.generate_identifier_pattern.build_pattern
  - collapse_ranges(data: Iterable[str]) -> Iterator[Tuple[str, str]]
    - Collapse ordered single-character data into contiguous (start, end) tuples for runs of consecutive Unicode code points.
    - See component doc: scripts.generate_identifier_pattern.collapse_ranges
  - get_characters() -> Iterator[str]
    - Yield single-character strings whose presence augments \w to cover identifier continuation characters that are not matched by \w.
    - See component doc: scripts.generate_identifier_pattern.get_characters
  - main() -> None
    - Orchestrate the pipeline (get_characters -> collapse_ranges -> build_pattern) and write the generated module file assigning re.compile(...) to the name pattern.
    - See component doc: scripts.generate_identifier_pattern.main

Mermaid dependency graph (internal relationships):
graph LR
    get_characters --> collapse_ranges
    collapse_ranges --> build_pattern
    build_pattern --> main
    get_characters --> main
    collapse_ranges --> main
    main --> write_file[Writes ../src/jinja2/_identifier.py]

## Public API:
- build_pattern(ranges: Iterable[Tuple[str, str]]) -> str
  - Description: Render a compact textual representation for each inclusive (start, end) character pair from ranges.
  - Usage note: Accepts an iterable of two-item tuples of single-character strings; callers must ensure ord(start) <= ord(end) for expected results. Does not validate or reorder ranges.
- collapse_ranges(data: Iterable[str]) -> Iterator[Tuple[str, str]]
  - Description: Group contiguous code points in data into (start, end) tuples (preserves order).
  - Usage note: Input must be in the desired order (typically ascending by code point). Each element must be acceptable to ord() (single-character strings).
- get_characters() -> Iterator[str]
  - Description: Enumerate characters (single-character strings) for which ("a"+c).isidentifier() is True but c does not match \w.
  - Usage note: Full consumption scans up to sys.maxunicode and can be long-running; consume incrementally or persist results. Results are in ascending code-point order.
- main() -> None
  - Description: Run the full generation pipeline and write the output module to ../src/jinja2/_identifier.py (relative to the script).
  - Usage note: This performs file I/O and overwrites the target file; ensure the repository layout exists and you have write permission.

## Dependencies:
- Internal imports (other repo modules):
  - None required by the generator itself (it produces a module consumed later by other repo code).
- External / standard-library imports:
  - re: used to construct or compile the final regex pattern and for pattern-related checks (get_characters uses re.match; the generated file uses re.compile).
  - sys: used to determine sys.maxunicode when enumerating code points.
  - os / os.path: used by main to compute the target output path (dirname, join, abspath).
  - Builtins: ord and chr are used by the helpers to inspect and produce single-character strings.
- Note: All dependencies are standard library modules; no third-party dependencies are required.

## Key data flows and shared state:
- There is no global mutable state shared between components. Data flows in a linear pipeline:
  get_characters() -> collapse_ranges(...) -> build_pattern(...) -> main() writes file
- The only side-effecting operation is file I/O performed by main().

## Constraints:
- Preconditions callers must respect:
  - get_characters scans all Unicode code points supported by the interpreter (range(sys.maxunicode+1)). Do not call in hot code paths expecting fast return; treat it as an offline or maintenance operation.
  - collapse_ranges expects input in the intended order (sorted by code point) and that each element is a single-character string acceptable to ord(). Input duplicates or unsorted input may yield multiple single-element runs or unexpected ranges.
  - build_pattern expects an iterable of 2-tuples (start, end) where each element is a single-character string. ord(start) <= ord(end) should hold for semantically correct ranges.
  - main expects the repository directory structure to include ../src/jinja2 relative to the script's parent directory and sufficient filesystem permissions to write the target file.
- Thread-safety:
  - Helper functions (get_characters, collapse_ranges, build_pattern) are pure in the sense of not mutating global state and are safe to call concurrently from separate processes/threads as long as callers handle iteration correctly.
  - main performs file writes and is not safe to run concurrently if multiple invocations target the same output file without external synchronization.
- Ordering / initialization:
  - There is no module-level initialization required beyond standard interpreter availability. The pipeline must be invoked in the order: get_characters -> collapse_ranges -> build_pattern -> write file (main enforces this orchestration).
- Error propagation:
  - Helper functions deliberately surface built-in exceptions (TypeError, ValueError) arising from invalid inputs (e.g., non-single-character strings) so callers can handle or fix upstream data. main propagates filesystem-related exceptions (OSError variants) encountered while writing the generated module.

## Links to component-level documentation:
- scripts.generate_identifier_pattern.get_characters
- scripts.generate_identifier_pattern.collapse_ranges
- scripts.generate_identifier_pattern.build_pattern
- scripts.generate_identifier_pattern.main

---

## Files

- [`generate_identifier_pattern.py`](scripts/generate_identifier_pattern.md)

