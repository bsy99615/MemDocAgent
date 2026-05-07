# `hypertools`

## Tree:
hypertools/
    docs/                      # Documentation tooling and notebook-to-doc helpers
        tutorials/
            tools/
                nb_to_doc.py    # Notebook → documentation conversion tool (expects injected process-runner)
    hypertools/                 # Main application package: data orchestration, plotting, and small numeric algorithms
        _externals/             # Lightweight numeric algorithm implementations (PPCA, SRM/DetSRM)
            ppca.py             # Probabilistic PCA (missing-data aware)
            srm.py              # SRM and deterministic SRM implementations
        _shared/                # Shared utilities (internal helpers used across modules)
        plot/                   # Plotting/rendering implementation (entrypoint for DataGeometry.plot)
        tools/                  # Pipeline helpers: format_data, normalize, reduce, align
        datageometry.py         # DataGeometry container and pipeline orchestration (primary runtime entry)

## Purpose:
- What this repository does and why it matters
    - Hypertools provides a compact data-processing and visualization pipeline that:
        1. Converts heterogeneous user inputs into standardized numeric arrays,
        2. Runs a configurable pipeline (format → normalize → reduce → align),
        3. Renders results via a plotting backend, and
        4. Includes lightweight internal implementations of numeric algorithms required by the pipeline.
    - The docs/ tooling supplies a centralized, deterministic utility to convert tutorial Jupyter notebooks into documentation artifacts (.rst) and normalized notebooks for CI and maintenance workflows.
- Target users and scenarios
    - Data scientists and researchers who need an opinionated pipeline for exploratory visualization and inter-subject alignment.
    - Developers who build tutorials and CI processes that convert notebooks into repository documentation.
    - Integrators who embed the pipeline in notebooks, scripts, or automated builds.
- Position in the ecosystem
    - Library-style package intended to be imported by applications and scripts (not a standalone service).
    - Lightweight substitute for heavier external dependencies by bundling minimal algorithmic implementations internally.
    - Documentation conversion tool depends on an external CLI (jupyter nbconvert) but is intentionally decoupled via injection.

## Architecture:
- High-level architecture summary
    - Single canonical runtime object (DataGeometry) owns input data, pipeline configuration, caches, and plotting defaults.
    - Pipeline helpers (tools) implement the sequence: format_data → normalize → reduce → align.
    - _externals contains minimal numeric algorithm implementations (PPCA, SRM, DetSRM) used when specialized behavior is required.
    - Plotting concerns are implemented in hypertools.plot and invoked from DataGeometry.plot.
    - docs.tutorials.tools.nb_to_doc provides an orthogonal, tooling-only flow for converting tutorial notebooks to docs; it relies on a caller-supplied process-runner to execute jupyter nbconvert commands.

- End-to-end data flow (Mermaid flowchart)
flowchart TD
    U[User / Caller] --> DG[DataGeometry]
    DG --> F[tools.format_data]
    F --> PPCA[_externals.ppca.PPCA]
    DG --> N[tools.normalize]
    DG --> R[tools.reduce]
    R --> PPCA
    DG --> A[tools.align]
    A --> SRM[_externals.srm.SRM / DetSRM]
    DG --> P[plot.plot]
    style DG fill:#efe,stroke:#333,stroke-width:1px
    style F fill:#ffd,stroke:#333,stroke-width:1px
    style PPCA fill:#f9f,stroke:#333,stroke-width:1px
    style SRM fill:#9ff,stroke:#333,stroke-width:1px
    style P fill:#ffd,stroke:#333,stroke-width:1px

- Key abstractions and architectural patterns
    - Pipeline pattern: fixed transformation order (format → normalize → reduce → align) orchestrated by DataGeometry.
    - Composition/delegation: DataGeometry composes tools and delegates plotting to plot module.
    - Pluggable algorithms: _externals exposes replaceable algorithm instances (PPCA, SRM, DetSRM) that tools may call.
    - Injection for tooling: docs.tutorials.tools.nb_to_doc expects a caller-injected process-runner to perform CLI operations.

## Entry Points:
- Importable API entry points (for developers embedding or using the library)
    - hypertools.datageometry.DataGeometry
        - Exposes: constructor to create the canonical pipeline container; methods get_data, get_formatted_data, transform, plot, save.
        - Required args: typically raw data (numpy arrays, pandas DataFrames, lists) and optional plotting/pipeline kwargs; see component-level docs for constructor signature.
        - Target audience: application code, notebooks, scripts that want the full pipeline + plotting integration.
    - hypertools.tools (module-level helpers)
        - Exposes: format_data, normalize, reduce, align (pipeline primitives).
        - Required args: numeric arrays or DataGeometry instance attributes depending on the helper; consult tools module docs for exact signatures.
        - Target audience: advanced users who need fine-grained control over pipeline stages or custom pipelines.
    - hypertools._externals.ppca.PPCA and hypertools._externals.srm.SRM / DetSRM
        - Exposes: fit, transform (and save/load where applicable).
        - Required args: numeric arrays; see component docs for input shape constraints and options.
        - Target audience: users needing algorithm-level control or reusing these estimators outside tools pipeline.
    - hypertools.plot (plotting module)
        - Exposes: plotting functions used by DataGeometry.plot (see module for exact call signatures).
        - Required args: transformed numeric arrays and rendering options.
        - Target audience: visualization customization and embedding in GUI/interactive contexts.
- Tooling entry point (documentation generation)
    - docs.tutorials.tools.nb_to_doc.convert_nb(nbname: str)
        - Exposes: single function to run a three-step jupyter nbconvert CLI sequence on nbname.ipynb.
        - Required args: nbname (basename without ".ipynb"). Prior to calling, assign a callable to the module-level name sh that accepts command token lists and executes them synchronously.
        - Target audience: CI scripts, docs build processes, and ad-hoc maintenance scripts that convert notebooks to .rst and normalize stored notebooks.

## Core Features:
- Canonical pipeline orchestration (hypertools.datageometry.DataGeometry)
    - One-line: Encapsulates data, pipeline config, and plotting defaults; runs format→normalize→reduce→align and exposes plot/save helpers.
- Data formatting utilities (hypertools.tools.format_data)
    - One-line: Coerces heterogeneous inputs into a list of 2-D numeric arrays suitable for numeric processing.
- Normalization helpers (hypertools.tools.normalize)
    - One-line: Implements configurable normalization strategies applied prior to dimensionality reduction/visualization.
- Dimensionality reduction wiring (hypertools.tools.reduce)
    - One-line: Coordinates reduction step(s) and delegates to internal or external reducers; consult tools module for algorithms used.
- Multi-subject alignment (hypertools.tools.align and _externals.srm)
    - One-line: Aligns multi-subject time-series using SRM or deterministic SRM implementations.
- Lightweight numeric algorithms (_externals.ppca, _externals.srm)
    - One-line: Internal implementations of PPCA and SRM variants to reduce external dependency surface and handle edge-cases like missing data.
- Plotting integration (hypertools.plot)
    - One-line: Rendering implementation invoked by DataGeometry.plot, using stored defaults merged with per-call kwargs.
- Notebook → docs conversion tool (docs.tutorials.tools.nb_to_doc.convert_nb)
    - One-line: Deterministic three-step jupyter nbconvert orchestration (execute → export .rst → clear outputs) driven by an injected process-runner.

## Dependencies:
- Key external dependencies (roles)
    - numpy: core numeric arrays and vectorized operations.
    - scipy.linalg: linear algebra routines (SVD/QR/Cholesky) used by numeric algorithms for stability.
    - scikit-learn utilities: input validation helpers (e.g., assert_all_finite) used by SRM.fit.
    - pickle, warnings (stdlib): used for DataGeometry.save and related serialization/notifications.
    - jupyter nbconvert (external CLI, runtime): required by docs.tutorials.tools.nb_to_doc.convert_nb; must be available on PATH for notebook conversion to succeed.
- Compatibility notes and constraints
    - Algorithmic components assume reasonably recent NumPy/SciPy versions that provide stable SVD/QR behavior; specific version constraints are enforced in the packaging metadata (consult setup/pyproject when present).
    - SRM.fit may seed NumPy's global RNG; callers requiring reproducibility in concurrent contexts should manage RNG externally.

## Extension Points:
- Pipeline customization
    - Modify DataGeometry instance attributes (normalize, reduce, align, semantic, vectorizer, corpus) to change pipeline behavior without editing library internals.
    - Replace or wrap tools helpers (format_data/normalize/reduce/align) with custom implementations and call them directly or inject them into workflows.
- Algorithm substitution
    - Use or subclass hypertools._externals.ppca.PPCA, SRM, or DetSRM to provide alternative fit/transform semantics; tools.align can be adapted to call different estimators.
- Plotting customization
    - DataGeometry.plot delegates to hypertools.plot; replace or monkey-patch plot module functions for different rendering backends or interactive behavior.
- Tooling injection
    - docs.tutorials.tools.nb_to_doc requires a module-level callable named sh that executes command token lists. Provide a robust process-runner (handles logging, stdout/stderr capture, retries, and timeouts) to integrate the notebook conversion into CI.
- File-format serialization hooks
    - DataGeometry.save serializes a pickle-safe snapshot while temporarily nulling plotting handles; override or extend save/load to add compression, metadata schemas, or alternate persistence backends.

## Where to find component-level contracts and implementation details
- Consult component-level documentation and source files for precise function/class signatures, parameter types, edge cases, and examples:
    - hypertools.datageometry.DataGeometry (constructor and methods)
    - hypertools.tools (format_data, normalize, reduce, align)
    - hypertools._externals.ppca.PPCA (ppca.py)
    - hypertools._externals.srm.SRM and DetSRM (srm.py)
    - hypertools.plot (plotting entrypoints)
    - docs.tutorials.tools.nb_to_doc.convert_nb (nb_to_doc.py) — includes the sh injection contract and exact nbconvert token sequences

---

## Modules

- [`docs`](docs.md)
- [`docs/tutorials`](docs/tutorials.md)
- [`docs/tutorials/tools`](docs/tutorials/tools.md)
- [`hypertools`](hypertools.md)
- [`hypertools/_externals`](hypertools/_externals.md)
- [`hypertools/_shared`](hypertools/_shared.md)
- [`hypertools/plot`](hypertools/plot.md)
- [`hypertools/tools`](hypertools/tools.md)

