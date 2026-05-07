# `datasette`

## Tree:
- datasette/  (repository root)
    - Responsibility: repository container; may include packaging, docs, and configuration files if present
    - datasette/  (python package)
        - Responsibility: the core implementation package. Contains modules that implement the ASGI application, route handlers, database integration, templating, static assets, and any plugin or extension machinery.

Note: The available snapshot shows only the top-level package directory. This documentation intentionally avoids claiming the presence of any other files (README, pyproject.toml, etc.) unless they exist in the repository.

## Purpose:
- Problem solved and why it matters
    - Turn one or more SQLite database files into an HTTP-served, browsable API and web UI. This simplifies sharing, exploring, and embedding datasets without building a bespoke backend.
- Target users and scenarios
    - Data journalists, researchers, engineers, small teams needing a lightweight, read-oriented data server for exploration, publishing datasets, or powering dashboards.
- Position in the ecosystem
    - Designed as both a standalone tool (CLI) and an importable Python package (ASGI application) so it can be run directly or embedded in larger Python deployments.

## Architecture:
- End-to-end data flow (Mermaid flowchart)
flowchart TD
    CLIENT["Browser or HTTP client"]
    CLI["CLI / entry point (if present)"]
    CONFIG["Configuration (flags, env, metadata)"]
    APP["ASGI app (app factory)"]
    ROUTER["Router / URL dispatch"]
    HANDLERS["Request handlers / views"]
    DB_LAYER["SQLite adapter / query executor"]
    PLUGINS["Plugin registry / hooks"]
    TEMPLATING["Template renderer"]
    STATIC["Static assets (JS/CSS)"]

    CLI -->|start| CONFIG --> APP
    APP --> ROUTER
    ROUTER --> HANDLERS
    HANDLERS --> DB_LAYER
    HANDLERS --> TEMPLATING
    TEMPLATING --> STATIC
    APP --> PLUGINS
    CLIENT -->|HTTP| APP

- Key abstractions and patterns (explicit, implementation-oriented)
    - ASGI-compatible app factory: returns a callable (scope, receive, send) so the app can be hosted by any ASGI server.
    - CLI bootstrapper (optional): a thin layer that converts CLI arguments into app-factory parameters and runs an ASGI server for convenience.
    - Database adapter: encapsulates opening database files, executing parameterized SQL safely, managing per-request connections, and converting results to serializable structures.
    - Request handlers: small units that implement endpoints for listing databases/tables, returning table rows, returning single rows, and executing SQL queries.
    - Templating and static assets: separate presentation layer that renders HTML views from handler data.
    - Plugin/hook registry: central dispatch allowing third-party code to register callbacks at defined hook points (startup, shutdown, before/after query, request lifecycle, render).
    - Security boundaries: hooks or middleware for authentication/authorization; by default implement read-oriented semantics unless explicitly extended.

## Entry Points:
- Observed facts
    - The repository contains a Python package named datasette. The exact CLI entry point names, console_scripts, or app-factory function names are not visible in the supplied tree.
- Reconstruction guidance (what to provide when implementing)
    - Provide an app factory: function signature suggestion
        - create_app(databases: dict[str, str], settings: dict | None = None, plugins: list | None = None) -> Callable
        - Behavior: return an ASGI application configured to serve the specified databases and settings.
    - Provide a CLI layer (optional): parse command-line flags to produce the inputs required by create_app and then either run an ASGI server (uvicorn.run) or document how to hand off the returned app to an ASGI server.
- Where to verify actual repository entry points
    - Look for packaging metadata (pyproject.toml/setup.cfg/setup.py) and for module-level definitions inside the datasette package (files such as __init__.py, cli.py, app.py, or similarly named modules) to confirm the real function and command names.

## Core Features (reconstruction checklist)
Below are the concrete features a functional implementation should provide. Each item includes the minimal responsibilities required to be considered complete.

- Serve SQLite databases over HTTP
    - Responsibilities: accept a mapping of database name → path; expose those databases under stable URLs; avoid modifying database files by default.
- Listing and metadata endpoints
    - Responsibilities: provide an endpoint that lists all configured databases, their tables, and simple metadata (column names, primary keys).
- Table browsing with pagination and filtering
    - Responsibilities: paginated endpoints for table rows; query parameters for page/per_page and simple filters; server-side limits to avoid excessive responses.
- Row-level endpoints
    - Responsibilities: retrieve an individual row by primary key; return 404 for missing keys.
- SQL-execution endpoint (optional, with safety controls)
    - Responsibilities: accept SQL with parameter binding; enforce row/byte limits and execution timeouts; avoid executing dangerous statements (or restrict to read-only).
- JSON and HTML rendering
    - Responsibilities: return JSON for API consumers and render HTML pages using templates for human browsing.
- Plugin/hook system
    - Responsibilities: provide a registry where plugins can register callbacks for named hooks; handlers must call hooks at defined moments and honor their synchronous/async nature.
- Static asset serving
    - Responsibilities: serve JS/CSS files used by the HTML UI; support plugins providing additional static assets.

## Dependencies (practical minimal set)
- Minimal runtime components to implement the above:
    - Python 3.8+ for typing and async/await support.
    - sqlite3 module (stdlib) for direct file access.
    - An ASGI server (uvicorn, hypercorn) to run the ASGI app in production.
    - A template engine (e.g., Jinja2) for HTML rendering.
    - Optional CLI parsing tools (argparse — stdlib — or click) for the user-facing CLI experience.

Note: The actual repository may declare a different or larger set of dependencies — inspect packaging metadata inside the repository to learn exact required packages and pinned versions.

## Configuration
- Sources of configuration (implement or inspect)
    - CLI flags: databases to expose, host/port, reload/debug, enabled plugins.
    - Environment variables: tokens/secrets and any overrides.
    - Per-database metadata files: titles, labels, table descriptions, and per-table permissions.
- Effects of configuration
    - The set of exposed databases, enabled endpoints, plugin activation, and UI customization.

## Extension Points
- Plugin/hook system (recommended minimal design)
    - Essential hooks to include:
        - on_startup(app_config) / on_shutdown(app_config)
        - before_request(request_context) / after_request(request_context, response)
        - before_execute_sql(db_name, sql, params) / after_execute_sql(db_name, sql, params, results)
        - template_context(context) — allow plugins to add context variables to templates
        - route registration hook — allow plugins to register additional endpoints
    - Plugin discovery and registration
        - Support explicit plugin import paths passed to the app factory or a plugin discovery mechanism via entry points (if packaging defines them).
- Template and static overrides
    - Allow plugins to supply templates and static directories that the app will prefer/merge with core templates.

## Reconstructing a Minimal Working Implementation — Concrete step-by-step
This blueprint is written so a developer can implement a working server from scratch without assuming repo-specific names.

1. Implement an ASGI app factory
    - Input: mapping of database name → file path + optional settings + plugin instances.
    - Output: ASGI callable handling routing and request dispatch.
    - Responsibilities: initialize plugin registry, open/validate database files (but open connections lazily per-request), and register core routes.

2. Implement a routing layer and handlers
    - Core routes (suggested names; verify actual repo routes if present):
        - GET /            — list databases and basic metadata
        - GET /{db}/       — list tables in a database
        - GET /{db}/{table}/ — paginated rows
        - GET /{db}/{table}/{pk} — single-row view
        - POST /-/sql      — SQL execution endpoint (optional; enforce safety)
    - Each handler should call relevant hooks (before_request, before_execute_sql, after_execute_sql, after_request).

3. Implement a SQLite adapter
    - Provide safe parameter binding APIs and result munging (e.g., convert sqlite types to JSON-serializable Python types).
    - Provide query limits (max rows, max bytes) and optional timeouts.

4. Implement templating and static asset serving
    - Use a templating engine to render HTML for human browsing.
    - Serve static files under a stable prefix (e.g., /static/) and allow plugins to register additional assets.

5. Implement plugin registry and dispatch
    - Plugins register callbacks for named hooks.
    - The registry supports synchronous and asynchronous callbacks and ensures they are executed in deterministic order.

6. Implement a small CLI wrapper (optional)
    - Parse arguments to populate the app factory inputs.
    - Optionally run a development server via uvicorn or print instructions for production deployment.

## Unknowns to confirm in this repository
To convert the reconstruction suggestions into an exact mapping to this repository, inspect these locations (if present) and record their actual names and contents:
- Packaging metadata files at repo root (pyproject.toml, setup.cfg, setup.py, requirements.txt) — to find declared dependencies and console_scripts entry points.
- Files inside the datasette package that define the app factory or CLI glue (common names to check: __init__.py, cli.py, app.py, server.py).
- Any module or package named plugins or hooks — what hook names and signatures are implemented there.
- Templates and static asset directories to learn the URL prefixes and any asset pipeline details.
- README, docs/, or CONTRIBUTING files to learn recommended deployment patterns and exact CLI usage.

## Final notes
- This documentation intentionally limits factual claims to what is visible (a package named datasette) and focuses on a conservative, complete reconstruction plan that a developer can follow to implement equivalent functionality.
- After confirming the "Unknowns" items above, update the implementation with the exact function and file names found in the repository, and adjust configuration and dependency lists accordingly.

---

## Modules

- [`datasette`](datasette.md)
- [`datasette/publish`](datasette/publish.md)
- [`datasette/utils`](datasette/utils.md)
- [`datasette/views`](datasette/views.md)

