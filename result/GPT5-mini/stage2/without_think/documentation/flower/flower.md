# `flower`

## Tree:
flower/
├── docs/               # Example/demo "task" functions used for tests and documentation
│   └── tasks.py
├── examples/           # Lightweight example/demo tasks used in docs/tests/CI
│   └── tasks.py
└── flower/             # Primary library / application package (contents not present in snapshot)
    └── (package contents not included in current snapshot)

Notes:
- The two top-level example modules (docs/tasks.py and examples/tasks.py) are present in the snapshot and contain minimal task-like functions (see their module docs: docs.tasks and examples.tasks).
- The main package directory (flower/) exists but its implementation is not available in the provided snapshot; treat it as the primary library to be (re)implemented or documented later.

## Purpose:
- What this repository addresses:
  - Provides a tiny demonstration repository focused on "task"-style functions and a primary package named `flower`. The snapshot includes minimal example/demo tasks useful for documentation, testing, and exercising worker/task-runner integration.
- Why it matters:
  - The examples and docs modules provide deterministic, side-effect-light behaviors (pure add, echo, error, and blocking sleep/sub) that are ideal for unit/integration tests, examples, and validating scheduling/workers. A main `flower` package (not present) presumably provides the production functionality or library surface.
- Target users and scenarios:
  - Developers building or testing background task systems, CI scripts that exercise blocking vs. non-blocking tasks, or documentation authors who need minimal examples.
  - Test authors who need deterministic functions to validate serialization, dispatch, and error handling.
- Position in the ecosystem:
  - This snapshot is primarily an examples-and-stubs repository. It can be used as:
    - A lightweight library of example tasks (importable).
    - A foundation to implement a task-runner or service (the `flower` package).
    - A demo/test harness for external worker systems (e.g., Celery), if integrated.

## Architecture:
- High-level overview:
  - The repository exposes example/task modules that are imported directly by tests, docs, or worker runtimes. The main `flower` package is the intended primary library/application and should provide registration, dispatch, and runtime behaviors (missing from snapshot).
- End-to-end data/control flow (Mermaid flowchart):
flowchart TD
    Dev[Test/Docs] -->|import| Examples[examples.tasks]
    Dev -->|import| Docs[docs.tasks]
    Examples -->|use| WorkerRuntime[Worker / Task Runner (external)]
    Docs -->|use| WorkerRuntime
    WorkerRuntime -->|dispatch| FlowerPkg[flower (main package)]
    FlowerPkg -->|execute| RuntimeEnv[Processes / Threads / Async Executors]
    Note[Developer: flower package implementation not included in snapshot; see "Reconstruction guidance" below] --> FlowerPkg

- Key abstractions and architectural patterns:
  - Tasks (pure functions with simple deterministic behavior) — examples/docs modules.
  - Worker/Task Runner (external) — independent processes or threads that import tasks and execute them; not implemented in-snapshot but expected integration target (e.g., Celery).
  - Primary library/package (`flower`) — intended to be the core application/library; its responsibilities are not available in the snapshot but are the natural place for registration, runtime orchestration, and CLI.
  - Patterns:
    - Plugin/Registration: tasks are plain callables that can be imported and registered with a runtime.
    - Separation of concerns: minimal example tasks are isolated from the runtime so the same task functions can be used in tests, docs, and by workers.

## Entry Points:
- Importable APIs (present in snapshot):
  - examples.tasks
    - What it exposes: functions add(x, y), echo(msg), error(msg) (raises), sleep(seconds)
    - Required args / behavior: see examples.tasks module documentation in memory for precise signatures and edge cases.
    - Target audience: documentation examples, unit/integration tests, and demo scripts.
    - Documentation reference: examples.tasks (see stored module-level documentation).
  - docs.tasks
    - What it exposes: functions add(x, y), sub(x, y)
    - Required args / behavior: docs.tasks.add performs x + y; docs.tasks.sub sleeps for 30 seconds then returns x - y.
    - Target audience: demonstration code and integration tests that need both instantaneous and long-blocking tasks.
    - Documentation reference: docs.tasks (see stored module-level documentation).
- Service/CLI entry points (NOT present in the snapshot):
  - No explicit CLI script, __main__.py, setup.py, or pyproject.toml are present in the snapshot. The main package folder exists but its public entry points are not documented here.
  - Recommendation for implementers: provide one or more of the following in the top-level `flower` package:
    - A programmatic API: package-level functions/classes for registration, dispatch, and runtime management (e.g., FlowerApp, register_task, run_worker).
    - A CLI: python -m flower or a console_script entry point that starts a local worker or performs admin tasks (recommended arguments: --run-worker, --register-task <module:function>, --config <path>).
    - A __main__.py that maps CLI args to library APIs.

## Core Features:
- Present in snapshot:
  - Minimal example tasks for deterministic behavior and blocking behavior
    - Implemented in: examples/tasks.py, docs/tasks.py
- Recommended (to implement in flower/ to make the repository functional as a task framework):
  - Task registration API
    - One-line: Register importable callables as named tasks.
    - Suggested module: flower.registry
  - Task dispatching/execution runtime
    - One-line: Dispatch registered tasks to be executed synchronously or by worker processes/threads.
    - Suggested module: flower.runtime
  - Worker process/loop
    - One-line: Long-running process that polls task queue or executes tasks in-process for demos.
    - Suggested module: flower.worker
  - Optional: CLI for launching workers and performing housekeeping
    - One-line: Command-line entrypoint to run local demo workers and administrative actions.
    - Suggested module: flower.__main__ or console scripts in packaging config.

For each existing feature in examples/docs, see respective module documentation rather than duplicating details:
- See: docs.tasks (module doc)
- See: examples.tasks (module doc)

## Dependencies:
- Discovered (from existing modules in snapshot):
  - Python standard library:
    - time — used by blocking examples (time.sleep).
  - Optional / common integration:
    - celery (third-party) — mentioned as optional in docs’ memory; not required for examples to run but commonly used for registering and running tasks in production/demo contexts.
- Unknown / not available:
  - Because the `flower` package content is not present in the snapshot, any third-party dependencies required by it are unknown. Implementers should add explicit dependency declarations (pyproject.toml/setup.cfg) when (re)implementing the main package.
- Version constraints:
  - None found in the snapshot. When implementing a full `flower` package, record and pin versions for external libraries (e.g., Celery) as needed.

## Configuration:
- Minimal snapshot configuration:
  - The snapshot contains no config files (pyproject.toml, setup.cfg, setup.py, or environment-specific config).
  - Example modules have no runtime configuration; they are pure functions.
- Recommended configuration options for a reconstructed `flower` package:
  - Worker concurrency (threads/processes)
  - Task timeouts / retry policies
  - Broker/backing-store settings (if integrating with Celery/RQ): broker URL, result backend
  - Logging and metrics sinks
  - Provide these via a short config file (TOML/INI/YAML) or environment variables; document expected env vars in README.

## Extension Points:
- How to extend:
  - Add new example tasks:
    - Create module-level functions in examples/ or docs/ and export them in the module namespace.
    - Keep them deterministic and side-effect-light for tests.
  - Extend `flower` package (recommended structure):
    - flower/registry.py — task registration helpers (register_task, list_tasks, get_task)
    - flower/runtime.py — simple executor that can run a registered callable synchronously or schedule it for background execution
    - flower/worker.py — process/loop that polls a queue or executes tasks from a list for demo/CI usage
    - flower/cli.py or flower/__main__.py — thin CLI wrapper around the runtime
  - Hooks & plugins:
    - When implementing the runtime, add pre-execution and post-execution hook invocation (callbacks) to allow instrumentation and custom behaviors.
    - Allow tasks to be registered by import string (module:function) to avoid importing all task modules at startup.
- Design guidance:
  - Keep example tasks independent and side-effect-free so they are reliable in tests.
  - Make runtime & worker components optional so the package can be used as a lightweight library or a full local demo system.

## Reconstructing a Minimal Functional Implementation of `flower` (practical guide)
If you need to rebuild a minimal, useful `flower` package from this snapshot, implement the following components (suggested file/module names) to make the repo immediately functional for demos/tests:

1. flower/__init__.py
   - Expose package metadata (e.g., __version__) and convenience imports: from .registry import register_task, list_tasks; from .runtime import run_task_sync, run_worker

2. flower/registry.py
   - register_task(name: str, func: Callable) -> None
   - get_task(name: str) -> Callable | None
   - list_tasks() -> list[str]
   - Implementation notes: store tasks in a dict at module level; support registration by import path string (e.g., "examples.tasks:add") resolving lazily.

3. flower/runtime.py
   - run_task_sync(name_or_callable, *args, **kwargs) -> Any
     - Accept either a registered name or a direct callable. Return the callable's result or propagate exceptions.
   - schedule_task(name_or_callable, *args, **kwargs) -> TaskHandle
     - Minimal scheduler can be a thread-based background executor (concurrent.futures.ThreadPoolExecutor) that returns a Future-like handle.

4. flower/worker.py
   - run_worker(loop=True, poll_interval=1.0)
     - For a demo worker, the function can poll an in-memory queue and execute tasks using runtime APIs.
   - Useful for integration tests: provide a way to enqueue tasks programmatically.

5. flower/__main__.py (optional)
   - Parse simple CLI args (--run-worker, --run-task examples.tasks.add 1 2) and invoke runtime/worker accordingly.

Testing:
- Provide unit tests that import examples.tasks and docs.tasks and demonstrate:
  - add(2, 3) == 5
  - echo returns the same object reference (if implemented)
  - error raises Exception
  - sleep / sub block for approximately the given duration (use monkeypatch or time patching in tests to avoid real waits)

## Where to find module/component documentation
- Existing module docs in memory:
  - docs.tasks — contains component docs for docs/tasks.py functions (add, sub)
  - examples.tasks — contains module docs for examples/tasks.py functions (add, echo (implementation note), error, sleep)
- When populating the `flower` package, create module-level documentation files mirroring these examples and link from this REPO-level doc to them.

## Maintenance notes and checklist
- Add a pyproject.toml or setup.cfg to declare package metadata and dependencies.
- Provide explicit component-level docs for any new modules created inside flower/.
- If Celery or another queueing system is used, add integration guides and example configurations.
- Keep example functions minimal and deterministic for test reliability.

Summary:
- The snapshot is a tiny example/demo repository: two small example modules are present and documented (docs.tasks, examples.tasks). The main package folder exists but its implementation is absent from the snapshot. This REPO doc describes the current contents, points to existing module docs, and provides a concrete, minimal plan for reconstructing a functional `flower` package (registry, runtime, worker, CLI) so a developer can rebuild the system from this documentation.

---

## Modules

- [`docs`](docs.md)
- [`examples`](examples.md)
- [`flower`](flower.md)
- [`flower/api`](flower/api.md)
- [`flower/utils`](flower/utils.md)
- [`flower/views`](flower/views.md)

