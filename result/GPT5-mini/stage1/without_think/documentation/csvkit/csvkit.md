# `csvkit`

## Tree:
Observed repository top-level (as provided):
- csvkit/
    - csvkit/                       # Python package directory (contents not listed in tree)

Responsibility annotations for observed directories:
- csvkit/ (top-level): Project root expected to contain packaging metadata, README, and the Python package. Specific files inside the package were not supplied in the repository snapshot.
- csvkit/ (package): The runtime package; its contents were not listed in the observed tree. The package is the expected place for the CLI and library implementation.

Recommended / Proposed implementation layout (for reconstructing a functional implementation)
- csvkit/                       # Root package and packaging files
    - csvkit/                   # Main Python package
        - __init__.py
        - cli/                  # CLI entrypoints and command dispatch
            - __init__.py
            - commands.py
            - csvcut.py
            - csvjoin.py
            - csvstat.py
            - in2csv.py
            - csvsql.py
        - core/                 # Streaming CSV I/O and core transforms
            - io.py
            - rows.py
            - headers.py
            - types.py
        - converters/           # Format/DB adapters (Excel, JSON, SQL backends)
            - excel.py
            - json.py
            - db.py
        - formats/              # Output formats and schema generation
            - table.py
            - sql.py
        - utils/                # Helpers (arg parsing, logging, errors)
            - args.py
            - logging.py
            - errors.py
        - tests/                # Unit and integration tests
    - README.md
    - pyproject.toml / setup.cfg / setup.py

Notes:
- The above "Recommended layout" is a blueprint to reconstruct a csvkit-like toolkit. It is explicitly proposed and not asserted as present in the observed snapshot.

## Purpose:
- Problem solved:
  - Provide a small, focused toolkit for inspecting, cleaning, converting, and transforming CSV and other tabular data sources, both from the command line and programmatically.
- Why it matters:
  - CSV is a simple, ubiquitous tabular interchange format. A robust toolkit makes everyday data tasks (previewing schema, selecting columns, joining files, converting formats) fast and scriptable, without requiring heavyweight dependencies.
- Target users and scenarios:
  - Data analysts and engineers working at the shell, automation scripts, or light-weight Python programs.
  - Common scenarios: cleaning malformed CSVs, converting Excel/JSON to CSV, selecting columns, joining files, producing summary statistics, and loading/exporting to SQL.
- Position in the ecosystem:
  - Primarily a CLI-first toolkit with an importable Python API option. It complements heavier tools (pandas) by emphasizing streaming, composability, and small-memory usage.

## Architecture:
- Suggested end-to-end flow (Mermaid flowchart):
  flowchart TD
    User[User / Script] -->|CLI or API| Dispatcher[Command Dispatcher]
    Dispatcher -->|select command| Command[Command Implementation]
    Command --> Read[Reader (core.io) -> streaming rows]
    Command --> Transform[Composable Transformers (select/join/clean/stat)]
    Transform --> Write[Writer / Formatter (CSV, JSON, Pretty Table, SQL)]
    Write --> Sink[Stdout / File / Database]

- Key abstractions and architectural patterns (recommended):
  - Command Dispatcher / Registry: map CLI names to handler constructors; instantiate handlers with parsed args.
  - Streaming Row Iterator: a generator-based reader that yields rows and associated header metadata to support arbitrarily large files.
  - Header abstraction: object that maps header names to indices, supports renaming and projection.
  - Transformer stages: small pure functions or classes implementing transforms (filter, map, join, select) that accept and yield row iterators.
  - Converter adapters: pluggable adapters for other formats (Excel, JSON) and DB backends that present the same iterator + metadata contract.
  - SQL adapter: codepath that can generate schema (CREATE TABLE), emit INSERT statements, and/or write directly to a DB using parameterized statements.
  - Pipeline composition: compose reader -> zero or more transformers -> writer; keep each stage testable and memory-efficient.

## Entry Points:
- Observed: the repository contains a package directory named csvkit. Specific entry points (console scripts, function names) were not listed in the provided snapshot.
- Recommended entry points to implement:
  - CLI console scripts (installed via packaging):
    - csvcut: select/projection of columns by header name or index
      - Typical flags: -c/--columns, input file (or stdin), output file (or stdout)
    - csvjoin: join two or more CSVs on key columns
      - Typical flags: --left-on, --right-on, --type (inner/left/right/outer)
    - csvstat: produce column-wise summaries/statistics and type inference
      - Typical flags: --count, --min, --max, --unique, column selectors
    - in2csv: convert spreadsheets or other formats to CSV
      - Typical flags: --format, input file, sheet selection (for Excel)
    - csvsql: generate SQL schema or load CSV into a database
      - Typical flags: --db (connection string), --insert, --table
    - csvlook / csvformat / csvjson (auxiliary utilities)
  - Importable Python API (recommended function signatures):
    - read_csv(source: Union[str, BinaryIO], *, delimiter: str = ',', encoding: str | None = None, **options) -> Iterator[Dict[str, Any]]
      - Returns a streaming iterator of row dicts and exposes header metadata via an attribute or separate reader.get_headers()
    - write_csv(rows: Iterator[Mapping[str, Any]], out: BinaryIO, *, delimiter: str = ',', **options) -> None
    - register_command(name: str, handler: Callable) -> None (for plugin registration)
    - Converter classes with a .to_rows() -> Iterator[...] method and .headers attribute

## Core Features (recommended list to implement):
- Streaming CSV read/write with robust encoding/dialect handling — core.io
- Column selection and projection — csvcut / core.headers
- File joins with key-based matching — csvjoin / core.rows
- Schema inference and basic statistics (type detection, counts, uniques) — csvstat / core.types
- Conversion from common formats (Excel, JSON) to CSV — in2csv / converters.*
- SQL schema generation and DB import/export — csvsql / converters.db / formats.sql
- Pretty human-readable table output for terminal viewing — csvlook / formats.table

## Dependencies:
- Minimal & recommended:
  - Python 3.8+ (for typing and modern stdlib features)
  - Built-in csv module for baseline parsing
- Optional (to be declared as extras in packaging):
  - openpyxl or xlrd for Excel (.xlsx/.xls) reading (converters.excel)
  - simplejson or built-in json for JSON converters
  - chardet or charset-normalizer for robust encoding detection
  - sqlite3 (stdlib) for local DB-backed operations
  - click or argparse for CLI parsing; click preferred for composability and nicer help output
  - agate or pandas as optional heavy-weight dependency for richer statistical summaries
- Packaging guidance:
  - Keep optional heavy libraries as extras (e.g., csvkit[excel], csvkit[db], csvkit[stats]) to avoid forcing them on all users.

## Configuration:
- Recommended minimal configuration approach:
  - Prefer explicit CLI flags over global configuration files to maximize portability in shell pipelines.
  - Support environment variables for non-portable secrets (e.g., DB credentials) and for global overrides like CSVKIT_ENCODING and CSVKIT_LOG_LEVEL.
  - Allow per-command flags to control memory behavior (e.g., --max-rows-in-memory for join algorithms).

## Extension Points:
- Plugin discovery:
  - Use setuptools entry points to allow third-party packages to register extra CLI commands or converters.
  - Define light interfaces: CommandHandler (callable taking parsed args) and Converter (detect + to_rows).
- Programmatic hooks:
  - Allow command pipelines to accept map/filter callables for user-supplied row transformations.
- Subclassing:
  - Keep readers/writers, converters, and formatters as small classes to encourage subclassing and override.

## How to implement from scratch (detailed guidance):
- Reader contract:
  - Implement a Reader class or generator function that accepts a filename or file-like object and returns:
    - headers: list[str] (normalized)
    - rows: Iterator[Sequence[str]] or Iterator[Dict[str, str]] (choose a single canonical form; dicts are friendlier but tuples are faster)
  - Provide options for dialect, encoding detection, and error handling mode (strict/relax/repair).
- Header utilities:
  - Provide functions to normalize header names (trim, deduplicate, fill missing), and produce index lookups for name->index and index->name.
- Transformers:
  - Implement small reusable transformers: select(columns), rename(mapping), filter(predicate), join(stream_a, stream_b, keys, join_type).
  - Transformers accept and return iterators; avoid materializing entire datasets unless explicitly requested.
- Join strategy:
  - For large files, support streaming joins by building a keyed index in memory for the smaller input; provide options to force a particular side to be the build side and to spill to disk if memory limits are hit.
- SQL adapter:
  - Implement a generator that can create CREATE TABLE and parameterized INSERT statements based on inferred column types; provide an option to execute directly via DB API.
- CLI wiring:
  - Each console script should parse args, create a reader and pipeline, and invoke a writer to the selected sink. Exit codes should reflect success (0) or failure (non-zero) with meaningful messages on stderr.

## Tests and quality:
- Provide unit tests for each core reader/writer, header normalization, and transformers.
- Provide integration tests that exercise CLI end-to-end using temporary files and capturing stdout/stderr.
- Include tests for edge cases: mixed encodings, missing headers, irregular row lengths, large files (streaming), and malformed CSVs.

## README / CONTRIBUTING:
- README should include:
  - One-line synopsis, install instructions (including extras), quickstart CLI examples, and troubleshooting (encoding, memory).
- CONTRIBUTING.md should document:
  - How to add new CLI commands, converters, and tests; the expected testing and CI workflow.

---

## Modules

- [`csvkit`](csvkit.md)
- [`csvkit/convert`](csvkit/convert.md)
- [`csvkit/utilities`](csvkit/utilities.md)

