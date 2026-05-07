# `online-judge-tools`

## Tree:
    online-judge-tools/               - Root of the repository containing the command package and packaging metadata
        onlinejudge_command/          - CLI package that implements the user-facing commands and programmatic API
            __init__.py               - Package initialization and public exports (CLI entry-points and helpers)
            (other modules)            - Submodules implementing commands, utilities, website adapters, I/O, etc.

Annotations:
- onlinejudge_command/: Responsible for exposing the CLI, parsing arguments, coordinating subcommands (problem fetch, test runner, submit), integrating online-judge adapters (site scrapers/APIs), and providing a stable importable API for other tools.

## Purpose:
- Problem solved:
    The repository implements tooling to interact with online programming-judge platforms from the command line and from scripts. It streamlines common workflows for competitive programmers and automated grading systems: fetching problem statements and samples, running and testing solutions locally, submitting solutions, and retrieving submission results.

- Why it matters:
    These tools automate repetitive, error-prone tasks involved in competitive programming and continuous grading, saving time and reducing friction when working across multiple judge websites.

- Target users and scenarios:
    - Competitive programmers who want quick CLI access to fetch samples and run local tests.
    - Educators and automated graders who need programmatic access to submit and verify solutions.
    - Scripters and integrators who want to embed judge interactions into pipelines (e.g., CI, custom graders).
    Typical scenarios: fetch problem samples, run solution against samples, compare outputs, submit solution, poll results, download problem statements.

- Position in ecosystem:
    - Primary: A standalone CLI toolset that also exposes an importable Python package for integration.
    - Secondary: Can be embedded into other services or automated workflows via its API.

## Architecture:
- High-level description:
    The system is organized around a core CLI entrypoint that dispatches subcommands. Each subcommand delegates to domain components:
    - Input/Output layer: CLI parsing, argument validation, file I/O, terminal output formatting.
    - Adapter layer: per-judge site adapters that know how to fetch problem metadata, samples, and perform submissions.
    - Execution layer: runs compiled/interpreted user programs against test inputs, captures outputs, and compares them.
    - Orchestration layer: coordinates sequences like "fetch → run → compare → submit → poll".

- Key abstractions:
    - Command Dispatcher: maps subcommands and flags to handler functions/classes.
    - Judge Adapter (Provider): an interface that encapsulates how to:
        - discover problem identifiers from URLs/input,
        - fetch problem statement and sample tests,
        - submit a solution and poll result status.
    - Runner: executes a user solution (binary or script) given input and captures stdout/stderr and exit code.
    - Comparator: compares expected vs. actual outputs (exact match, whitespace normalization, custom checker support).
    - Credential Store: secure local store for site credentials / API tokens.
    - Config: per-user or per-repo configuration that controls runtime defaults (e.g., preferred language, timeouts).

- End-to-end data flow (Mermaid flowchart):
flowchart TD
    UserCLI["User CLI (oj / onlinejudge)"] -->|parse subcommand| Dispatcher
    Dispatcher -->|invoke| AdapterSelector
    AdapterSelector --> Adapter[Judge Adapter (site-specific)]
    Adapter -->|fetch samples| IO[Local I/O: save samples]
    Dispatcher --> Runner[Runner: execute solution]
    Runner --> Comparator[Comparator: compare outputs]
    Dispatcher --> Adapter -->|submit| Adapter
    Adapter --> Poller[Submission poller]
    Poller -->|result| Dispatcher
    Dispatcher -->|report| UserCLI

- Architectural patterns:
    - Plugin/Adapter pattern for judge-specific logic.
    - Command-dispatch pipeline for CLI actions.
    - Separation of concerns: I/O, network/adapters, execution, and comparison are modular and testable.

## Entry Points:
- CLI entrypoint(s):
    - Primary executable (example name: oj or online-judge-tools):
        - Exposes subcommands such as: fetch, test, run, submit, login, download.
        - Required arguments depend on subcommand:
            - fetch: problem identifier or URL
            - test/run: path to source file or command to execute
            - submit: source file, language flag, problem id/URL
            - login: site name and credentials (or interactive)
        - Target audience: end users on the terminal (competitive programmers, graders).

- Importable API:
    - Package export (onlinejudge_command):
        - Programmatic interfaces to common operations: fetch_samples(problem), run_solution(cmd, input), compare_outputs(expected, actual), submit_solution(problem, source, language), get_submission_result(submission_id).
        - Target audience: integrators, graders, other Python programs.
    - Typical usage patterns:
        - from onlinejudge_command import fetch_samples, run_solution
        - results = fetch_samples("https://.../problem")
        - verdict = run_solution(["python", "solution.py"], results[0].input)

- Configuration endpoints:
    - Per-user config path (e.g., ~/.config/online-judge-tools/config or ~/.online-judge-tools/config)
    - Environment variable overrides for runtime behavior (e.g., OJ_TOOLS_TIMEOUT).

## Core Features:
- Fetch problem samples
    - Description: Download sample input/output pairs and problem metadata from a problem URL.
    - Implemented by: onlinejudge_command adapter modules (site adapters) and fetch command.

- Local test runner
    - Description: Run a user program against sample tests, capture output, and report pass/fail with diffs.
    - Implemented by: runner and comparator components in onlinejudge_command.

- Submit to online judges
    - Description: Submit source code to supported judge platforms and optionally poll for the result.
    - Implemented by: adapter submit/poller components and CLI submit command.

- Login / credential management
    - Description: Store and reuse site credentials securely for automated submissions.
    - Implemented by: credential store and auth utilities.

- Problem discovery / URL parsing
    - Description: Identify problem id and which adapter to use based on a given URL or shorthand.
    - Implemented by: URL parsing and adapter selector.

- Output comparison and custom checkers
    - Description: Provide strict/normalized comparisons and support for custom checker programs when available.
    - Implemented by: comparator module and checker integration.

## Dependencies:
- Network and HTML parsing:
    - requests (or an HTTP client) — performs HTTP requests to judge websites.
    - beautifulsoup4 / lxml — parse HTML pages to extract samples and submission forms.
- CLI parsing:
    - click or argparse — implement the CLI and subcommands.
- Execution:
    - subprocess (stdlib) — run user programs in a controlled environment.
- Optional:
    - keyring or similar — secure storage for credentials.
    - tqdm or rich — user-friendly progress and pretty terminal output.

Notes on versions and compatibility:
- No specific version constraints are asserted here (source not available). Implementations should aim for Python 3.8+ compatibility and pin stable versions of external libraries in packaging metadata (pyproject.toml / setup.cfg) as appropriate.

## Configuration:
- Configuration files:
    - Per-user config file (e.g., ~/.config/online-judge-tools/config) to define defaults: preferred language, timeout, default judge, proxy settings.
- Environment variables:
    - OJ_TOOLS_TIMEOUT — default execution timeout for user programs.
    - OJ_TOOLS_CONFIG — override path to config file.
- Runtime parameters:
    - Command-level flags override config and environment variables (e.g., --timeout, --language).

## Extension Points:
- Judge adapters:
    - Add new site adapters by implementing the Judge Adapter interface:
        - Must provide: identification from URL, fetch_samples(url) -> list of (input, output, metadata), submit(source, language) -> submission handle, poll(submission) -> result.
    - Adapters can be organized as modules under onlinejudge_command.adapters.<site> and registered with a central adapter registry.

- Custom comparators/checkers:
    - Provide a pluggable comparator API allowing exact-match, whitespace-normalized, or external custom checker binaries.

- CLI subcommands:
    - New subcommands can be registered with the command dispatcher; handlers should be small façades over the public API to enable reuse from scripts.

- Programmatic API:
    - The package should keep a stable, documented public API layer (thin wrappers over adapters, runner, comparator) so third-party tools can import and reuse functionality without invoking the CLI.

## Implementation guidance (high level)
- Keep network operations and HTML parsing encapsulated in adapter modules to make the core logic testable and resilient to site changes.
- Runner should sandbox and time-limit executed processes and provide clear stdout/stderr capture.
- Provide thorough logging and a verbose mode to ease debugging adapter scraping issues.
- Favor clear, typed interfaces for core abstractions (Adapter, Runner, Comparator) so implementers can create new adapters or runners safely.

---

## Modules

- [`onlinejudge_command`](onlinejudge_command.md)

