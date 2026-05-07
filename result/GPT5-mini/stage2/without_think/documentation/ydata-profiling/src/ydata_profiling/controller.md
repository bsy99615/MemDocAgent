# `src.ydata_profiling.controller`

## Tree:
controller/
├── console.py
└── pandas_decorator.py

## Role:
Provide small, focused orchestration and convenience helpers used by the project's CLI and caller code to convert user-supplied input (files or DataFrames) into a ProfileReport and persist it. The module owns CLI parsing + console orchestration and a minimal DataFrame->ProfileReport factory.

## Description:
Where and when this module is used
- Primary consumers:
  - The package's CLI entry point (ydata-profiling console script) calls console.main to handle an invocation.
  - Programmatic callers that want to create a ProfileReport from an existing pandas.DataFrame can import the profile_report helper from pandas_decorator.
  - Higher-level orchestration code that needs to parse CLI arguments for batch/report runs can call parse_args directly.
- Why these components are grouped here
  - Cohesion: both files are small controller-layer utilities that bridge user-facing input (CLI or in-memory DataFrame) to core profiling functionality (ProfileReport construction and persistence). Grouping them under a controller package isolates interaction/orchestration responsibilities from I/O, data handling, and the ProfileReport implementation.

## Components:
- parse_args(args: Optional[List[Any]] = None) -> argparse.Namespace
  - Parse CLI options and positional arguments and return a Namespace containing configuration for report generation (input_file, output_file, silent, minimal, explorative, pool_size, title, infer_dtypes, config_file, etc.).
  - See component docs: src.ydata_profiling.controller.console.parse_args

- main(args: Optional[List[Any]] = None) -> None
  - CLI orchestration entry point: parse args, read the input file into a pandas.DataFrame, create a ProfileReport (forwarding remaining kwargs), and persist the report to an output file.
  - See component docs: src.ydata_profiling.controller.console.main

- profile_report(df: pandas.DataFrame, **kwargs) -> ydata_profiling.profile_report.ProfileReport
  - Convenience wrapper that constructs and returns a ProfileReport given a pandas DataFrame and ProfileReport constructor kwargs.
  - See component docs: src.ydata_profiling.controller.pandas_decorator.profile_report

Mermaid dependency graph (internal relationships)
graph TD
    parse_args --> main
    read_pandas["read_pandas (I/O helper in repo)"] --> main
    ProfileReport["ydata_profiling.profile_report.ProfileReport"] --> main
    ProfileReport --> profile_report
    profile_report --> ProfileReport
    main --> ProfileReport
    main --> write_report["ProfileReport.to_file(...)"]

## Public API:
- parse_args(args: Optional[List[Any]] = None) -> argparse.Namespace
  - Description: Build and run an argparse.ArgumentParser for the profiling CLI and return the parsed Namespace.
  - Usage note: Callers provide a list of string arguments for programmatic parsing or pass None to parse sys.argv[1:]. The Namespace contains at minimum input_file and output_file attributes; parse_args may raise SystemExit for help/version/invalid args.
  - See: src.ydata_profiling.controller.console.parse_args

- main(args: Optional[List[Any]] = None) -> None
  - Description: Top-level console orchestration that turns CLI args into a persisted profiling report.
  - Usage note: main expects parse_args to produce a Namespace where vars() include keys input_file, output_file, and silent. main does not catch exceptions from reading data, building the report, or writing the file; callers should handle exceptions if needed. When output_file is None main computes a default output path by replacing the input file extension with .html.
  - See: src.ydata_profiling.controller.console.main

- profile_report(df: pandas.DataFrame, **kwargs) -> ydata_profiling.profile_report.ProfileReport
  - Description: Construct and return a ProfileReport for the given DataFrame by forwarding kwargs to ProfileReport.__init__.
  - Usage note: This is a minimal wrapper; it does not validate df or kwargs. Any constructor errors propagate unchanged. Use when you need a concise import point to create ProfileReport instances from in-memory DataFrames.
  - See: src.ydata_profiling.controller.pandas_decorator.profile_report

## Dependencies:
Internal imports (other repo modules)
- ydata_profiling.profile_report.ProfileReport
  - Purpose: Core class used to create profiling reports. The controller constructs ProfileReport instances or uses them to write reports to disk.
- read_pandas (I/O helper located elsewhere in the repo)
  - Purpose: File-format-aware reader used by console.main to load input_file into a pandas.DataFrame. The controller relies on its supported file formats; read_pandas explicitly rejects .tar compression.
- The controller module itself is intentionally lightweight and delegates heavy work (I/O, profiling algorithm, configuration parsing beyond CLI) to these internal modules.

External imports (third-party and stdlib)
- argparse (stdlib)
  - Purpose: CLI argument definition and parsing used by parse_args.
- pandas (third-party)
  - Purpose: Type and runtime expectations for DataFrame parameters and for reading file formats via read_pandas.
- pathlib.Path (stdlib)
  - Purpose: File path manipulation (computing default output filename from input path).
- typing (Optional, List, Any) (stdlib)
  - Purpose: Type hints used on public APIs.

## Constraints:
- Preconditions callers must respect
  - parse_args:
    - args should be a list-like of string-like items or None.
    - The environment must have the package __version__ available (used by --version action).
  - main:
    - parse_args must yield a Namespace where vars(parsed_args) contains keys "input_file", "output_file", and "silent" (main pops these three).
    - The input_file must be a path supported by the repository's read_pandas helper (note: .tar compression is explicitly unsupported and causes read_pandas to raise ValueError).
    - When passing args programmatically to main, provide the same shape as parse_args expects (strings); parse_args may raise SystemExit.
  - profile_report:
    - df should be a pandas.DataFrame or otherwise acceptable to ProfileReport.__init__.
    - kwargs must be valid ProfileReport constructor options; invalid keys/values will cause ProfileReport to raise.

- Ordering and lifecycle
  - main enforces an order: parse_args -> read_pandas -> ProfileReport(...) -> ProfileReport.to_file(...). Callers who need to bypass or customize these steps should call read_pandas or profile_report/ProfileReport directly.
  - parse_args may raise SystemExit which prevents further steps; callers that want to intercept help/version behavior must call parse_args inside an exception handler.

- Thread-safety
  - The controller functions are stateless wrappers with no module-level mutable state; they are safe to call from multiple threads as long as the underlying dependencies are thread-safe.
  - ProfileReport construction and file writes (ProfileReport.to_file) may not be thread-safe depending on the ProfileReport implementation and configuration; callers performing concurrent profiling should coordinate access or construct separate processes/instances as appropriate.

- Error handling expectations
  - These functions deliberately propagate exceptions from downstream components:
    - parse_args: SystemExit for invalid args and help/version.
    - read_pandas: IO and format-specific exceptions (ValueError for unsupported formats like .tar).
    - ProfileReport.__init__ and ProfileReport.to_file: any exceptions they raise will propagate.
  - The controller does not perform retries or silent error swallowing; callers must implement higher-level error handling if desired.

Notes and links to component documentation
- See component documentation for details and reimplementation guidance:
  - src.ydata_profiling.controller.console.parse_args
  - src.ydata_profiling.controller.console.main
  - src.ydata_profiling.controller.pandas_decorator.profile_report

---

## Files

- [`console.py`](controller/console.md)
- [`pandas_decorator.py`](controller/pandas_decorator.md)

