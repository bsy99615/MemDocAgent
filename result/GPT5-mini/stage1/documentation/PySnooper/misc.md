# `misc`

## Tree:
misc/
└── generate_authors.py

## Role:
Provide small, focused utilities to extract, deduplicate, and emit contributor/author names derived from a Git commit history.

## Description:
This module is used to produce ordered, de-duplicated lists of commit authors from a Git repository and to emit those lists to stdout. It centralizes the subprocess logic, parsing, deduplication, and output formatting so calling code (scripts, developer tooling, CI steps, or other repo reporting utilities) can obtain a canonical author list without reimplementing git invocation or printed output conventions.

Primary consumers:
- No direct importers were discovered in repository inspection. Intended consumers are:
  - CLI scripts or entrypoints that need to print contributors (for example, a small utility that writes a CONTRIBUTORS file or prints a list to the terminal).
  - CI jobs or release tooling that generate author lists for changelogs or release notes.
  - Any repo-level reporting utilities that need an ordered, deduplicated author list.

Why these components are grouped:
- Cohesion: all functions share the single responsibility of obtaining and presenting author information derived from git history.
- Layering: the module separates concerns into (a) raw data extraction from git, (b) an order-preserving deduplication utility, and (c) presentation to stdout — making each piece reusable and testable independently.

## Components:
- drop_recurrences(iterable: Iterable[T]) -> Iterator[T]
    - Yields items from iterable while preserving the order of first appearance and dropping later duplicates.
- iterate_authors_by_chronological_order(branch: str) -> Iterator[str]
    - Runs git log for the given ref and returns an iterator of unique author names in chronological (oldest-first) order.
- print_authors(branch: str) -> None
    - Writes each unique author name (one per line) for the given git ref to sys.stdout.buffer.

Mermaid dependency graph:
graph LR
    iterate_authors_by_chronological_order --> drop_recurrences
    print_authors --> iterate_authors_by_chronological_order

(See component-level documentation for each function for full implementation-level details:
- misc.generate_authors.drop_recurrences
- misc.generate_authors.iterate_authors_by_chronological_order
- misc.generate_authors.print_authors)

## Public API:
- drop_recurrences(iterable: Iterable[T]) -> Iterator[T]
    - Description: Lazily yields each distinct hashable element from iterable, preserving the order of first occurrence.
    - Usage note: Use when you need order-preserving deduplication without materializing the entire result; elements must be hashable or a TypeError will be raised when an unhashable element is encountered.

- iterate_authors_by_chronological_order(branch: str) -> Iterator[str]
    - Description: Executes git log with a format that exposes timestamp and author fields, decodes and parses the output, and returns a lazy iterator of author names (oldest commit first) with duplicates removed.
    - Usage note: Requires the current working directory to be a Git repository and the 'git' executable to be available on PATH. The subprocess stdout is decoded and split into lines before the deduplication iterator is applied; parsing errors (IndexError) or decoding errors (UnicodeDecodeError) may surface when iterating.

- print_authors(branch: str) -> None
    - Description: Iterates the authors returned by iterate_authors_by_chronological_order and writes each as UTF-8-encoded bytes followed by a POSIX newline to sys.stdout.buffer.
    - Usage note: Intended for simple producer/consumer command-line use. If stdout has been replaced, it must provide a binary buffer attribute (sys.stdout.buffer) that accepts bytes. Exceptions from git invocation, decoding, parsing, encoding, or I/O (including BrokenPipeError) are not caught and propagate to the caller.

## Dependencies:
Internal imports (repo modules):
- None required or discovered. Component-level docs did not report importing other repo modules.

External (standard library and third-party) imports:
- subprocess (standard library)
    - Purpose: run git log and capture stdout/stderr.
- sys (standard library)
    - Purpose: access sys.stdout.buffer for binary writes in print_authors.
- typing (standard library; Optional/Iterable/Iterator/TypeVar)
    - Purpose: types for signatures and to document generic behavior (T for drop_recurrences).

Notes:
- The functions use only standard-library facilities; no third-party packages are required.

## Constraints:
- Preconditions callers must respect:
    - For iterate_authors_by_chronological_order and print_authors:
        - Current working directory must be a Git repository (or call from a process with appropriate working directory).
        - 'git' executable must be present on PATH; otherwise FileNotFoundError will be raised.
        - branch must be a str acceptable to git log (e.g., 'main', 'HEAD', 'origin/main').
        - The module assumes git log output is UTF-8 decodable and in the expected format; otherwise UnicodeDecodeError or IndexError may occur during iteration.
    - For drop_recurrences:
        - Iterable elements must be hashable; otherwise a TypeError will be raised when the function attempts to add an element to the seen set.

- Postconditions:
    - iterate_authors_by_chronological_order yields author names in chronological order (oldest-first) and each name appears at most once.
    - drop_recurrences yields each first-seen value of the input iterable exactly once.
    - print_authors writes each yielded author to sys.stdout.buffer as UTF-8 bytes followed by a newline; it does not flush.

- Thread-safety and ordering:
    - The utilities are not inherently synchronized. If multiple threads share the same stdout, writes from print_authors can interleave with other writers; callers must handle synchronization if needed.
    - iterate_authors_by_chronological_order executes a subprocess synchronously; callers should avoid running it in contexts that prohibit subprocess invocation or that require non-blocking I/O without additional orchestration.

- Performance/memory:
    - iterate_authors_by_chronological_order collects git stdout into memory (decoded and split into lines) before yielding; very large histories may use significant memory.
    - drop_recurrences keeps a set of seen items in memory; memory usage grows with the number of distinct items observed.

- I/O semantics:
    - print_authors writes to sys.stdout.buffer but does not handle BrokenPipeError; callers should be prepared to catch and handle I/O-related exceptions in pipeline scenarios.

---

## Files

- [`generate_authors.py`](misc/generate_authors.md)

