# `ydata-profiling`

## Tree:
- ydata-profiling/ (repository root)
    - src/                      — Source root containing importable Python packages
        - ydata_profiling/      — Top-level package for the library (implementation lives here)

Notes:
- The provided repository snapshot contains only the src/ directory and the ydata_profiling package. No file-level listing inside ydata_profiling/, packaging metadata (pyproject.toml, setup.cfg, setup.py), or README/docs were included in the snapshot.
- This document deliberately avoids asserting file names or exact API symbols that are not present in the snapshot. It identifies confirmed structure, describes the expected high-level behavior, and gives a concrete, minimal blueprint a developer can follow to reconstruct the system.

## Purpose:
- Problem solved:
  - Provide automated exploratory data analysis (EDA) and dataset profiling for tabular data so users quickly understand data shape, quality, and statistical summaries.
- Target users:
  - Data scientists, analysts, and ML engineers who need fast, reproducible profiling of pandas DataFrames or dataset files (CSV/Parquet).
- How the project is typically consumed:
  - As an importable Python library that accepts DataFrame-like inputs and produces programmatic results and human-readable reports (HTML/JSON) that can be embedded in notebooks or saved to disk.

## Confirmed repository responsibilities
- src/: Contains the importable code. It must be placed on PYTHONPATH or the package installed for consumers to import ydata_profiling.
- ydata_profiling/: All runtime logic, analyzers, renderers, and public API will be under this package (not expanded here due to lack of file listing).

## Architecture (conceptual)
- Data flow (Mermaid flowchart)
flowchart TD
    Input[Input: pandas.DataFrame or dataset file] --> Ingest[Ingest & Normalization]
    Ingest --> Profiler[Profiler Orchestrator]
    Profiler --> ColumnAnalyzers[Per-column Analyzers]
    Profiler --> CrossAnalyzers[Cross-column Analyzers]
    ColumnAnalyzers --> Aggregator[Aggregated Metrics Store]
    CrossAnalyzers --> Aggregator
    Aggregator --> Renderer[Renderers / Exporters]
    Renderer --> Outputs[HTML / JSON / Notebook / dict / file]

- Key abstractions and patterns (explicit, minimal):
  - Ingest & Normalization: Convert user input (DataFrame, CSV, Parquet) to a canonical internal representation (pandas DataFrame with controlled dtypes and sampling).
  - Profiler Orchestrator: Coordinates running analyzers and collecting results into a shared metrics structure.
  - Analyzer: A small, focused component that computes metrics for a column (or cross-column). Contract: accepts column data and config, returns a metrics dict and optional visual artifacts.
  - Aggregated Metrics Store: Structured object (e.g., nested dict or lightweight dataclass) that gathers analyzer outputs per-column and global analyses.
  - Renderer/Exporter: Receives aggregated metrics and produces outputs (HTML report, JSON/dict, notebook display, or file write). Uses templates/plotting libs.
  - Config object: Centralized config controlling which analyzers run, thresholds, sampling behavior, and output formats.

## Entry Points (what to expect / implement)
- Importable API (primary, conservative description):
  - A top-level object or function (e.g., a Profileer-like class or create_report function) that:
    - Inputs: pandas.DataFrame or path to dataset; optional config object or kwargs.
    - Outputs: Report object (programmatic) or writes an HTML/JSON report to disk.
  - Suggested minimal Report object interface (recommended for reconstruction):
    - to_html(path: Optional[str] = None) -> str | None  — returns HTML string or writes to file when path provided
    - to_json(path: Optional[str] = None) -> dict | None
    - to_notebook() -> IPython.display.HTML (for inline rendering)
    - get_metrics() -> dict (machine-readable metrics)
- CLI (possible, optional):
  - Many profiling libraries expose a console script to profile files; if present, it should accept input file path and output path with optional config flags. Packaging metadata will reveal exact entrypoint names.
- Notebook integration:
  - Renderer should support returning embeddable HTML for inline display.

Note: The above entry point descriptions are intentionally generic and conservative; concrete function/class names and CLI entrypoints must be read from packaging metadata and module-level code.

## Core Features (conceptual mapping)
- Per-column statistics (counts, missingness, unique, min/max, mean, std)
  - Implemented by: Column analyzers inside ydata_profiling
- Missingness analysis and patterns
  - Implemented by: Missingness analyzer(s)
- Distribution summaries and plots (histograms, bar charts)
  - Implemented by: Visualization-capable analyzers + Renderer
- Correlations and cross-feature interactions
  - Implemented by: Cross-column analyzers
- Report rendering to HTML / JSON / notebook
  - Implemented by: Renderer / Exporter components
- Configurability (enable/disable analyzers, thresholds, sampling)
  - Implemented by: Centralized Config object consumed by Profiler and Analyzers

(Each item above maps to internal modules under ydata_profiling — create MODULE-level docs for concrete filenames and function/class contracts.)

## Dependencies (typical, to verify)
- Likely required third-party libraries (confirm exact versions in packaging metadata):
  - pandas — primary input and data handling
  - numpy — numeric computations
  - matplotlib / seaborn / plotly — for visualizations (at least one plotting backend)
  - Jinja2 or similar — for HTML templating (if using templated reports)
  - jupyter / ipython (optional) — for richer notebook display
- Action required: read pyproject.toml / setup.cfg / requirements.txt to confirm exact dependency names and version constraints.

## Configuration (where behavior meaningfully changes)
- Config sources to search for in the repo:
  - Programmatic API signatures (constructor params)
  - Example config files (YAML/JSON) under docs/ or examples/
  - CLI flags (if console scripts are provided)
- Typical configurable knobs:
  - sampling (sample size or fraction)
  - which analyzers to run
  - thresholds for alerts (e.g., high missingness)
  - output format(s) and storage location

## Extension Points (how to extend)
- Analyzer plugin pattern:
  - Provide an Analyzer base class or interface; allow registration (decorator or registry) so users can add custom analyzers without modifying core.
- Renderer/template override:
  - Allow custom templates or renderer classes to be plugged in via config.
- Export hooks:
  - Let report objects be serialized to custom sinks (databases, S3) via a small exporter interface.

## Minimal blueprints to reconstruct core functionality (recommended)
- Data ingestion:
  - Function: load_data(source: Union[pd.DataFrame, str], sample: Optional[float] = None) -> pd.DataFrame
- Analyzer interface:
  - Class Analyzer:
      - __init__(self, config: dict)
      - run(self, series: pd.Series) -> dict  # returns metrics and optionally plots as bytes/base64
- Profiler orchestrator:
  - Class Profiler:
      - __init__(self, analyzers: Iterable[Analyzer], config: dict)
      - run(self, df: pd.DataFrame) -> Report
- Report:
  - Class Report:
      - metrics: dict
      - to_html(path: Optional[str]) -> Optional[str]
      - to_json(path: Optional[str]) -> Optional[dict]
      - display_notebook() -> None
- Renderer:
  - Class Renderer:
      - render(self, metrics: dict) -> str  # returns HTML
- These blueprints are intentionally minimal and should be implemented under ydata_profiling/ if reconstructing from scratch.

## Next steps / Actionable items (exact files to provide)
To upgrade this repository-level documentation into a complete, verified REPO doc and to enable MODULE- and COMPONENT-level documents, provide the following artifacts from the repository:

1. File tree for src/ydata_profiling/ (3 levels deep) listing filenames and top-of-file docstrings for each Python module.
2. Packaging metadata: pyproject.toml, setup.cfg, or setup.py (to extract package name, version, dependencies, and console entry points).
3. README.md, docs/, and example notebooks (to capture usage examples and CLI invocation patterns).
4. Any tests or examples that demonstrate the public API (calls/instantiation patterns).
5. Top-of-package docstring or ydata_profiling/__init__.py contents (often contains exported API and top-level documentation).

Once these files are available, produce MODULE-level docs for ydata_profiling and component-level docs for core classes and functions.

## Assumptions and disclaimers
- This document only asserts confirmed repository structure and describes a conservative, implementation-agnostic architecture for a profiling library. Any specific API names, module filenames, or exact dependency versions are intentionally omitted until the requested files are made available.
- The provided "blueprints to reconstruct" are suggested minimal interfaces to help a developer reimplement the system when module-level details are absent; they are not claims about existing symbols in the repository.

---

## Modules

- [`src`](src.md)
- [`src/ydata_profiling`](src/ydata_profiling.md)
- [`src/ydata_profiling/controller`](src/ydata_profiling/controller.md)
- [`src/ydata_profiling/model`](src/ydata_profiling/model.md)
- [`src/ydata_profiling/model/pandas`](src/ydata_profiling/model/pandas.md)
- [`src/ydata_profiling/model/spark`](src/ydata_profiling/model/spark.md)
- [`src/ydata_profiling/report`](src/ydata_profiling/report.md)
- [`src/ydata_profiling/report/presentation`](src/ydata_profiling/report/presentation.md)
- [`src/ydata_profiling/report/presentation/core`](src/ydata_profiling/report/presentation/core.md)
- [`src/ydata_profiling/report/presentation/flavours`](src/ydata_profiling/report/presentation/flavours.md)
- [`src/ydata_profiling/report/presentation/flavours/html`](src/ydata_profiling/report/presentation/flavours/html.md)
- [`src/ydata_profiling/report/presentation/flavours/widget`](src/ydata_profiling/report/presentation/flavours/widget.md)
- [`src/ydata_profiling/report/structure`](src/ydata_profiling/report/structure.md)
- [`src/ydata_profiling/report/structure/variables`](src/ydata_profiling/report/structure/variables.md)
- [`src/ydata_profiling/utils`](src/ydata_profiling/utils.md)
- [`src/ydata_profiling/visualisation`](src/ydata_profiling/visualisation.md)

