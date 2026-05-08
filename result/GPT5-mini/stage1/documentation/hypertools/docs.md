# `docs`

## Tree:
docs/
└── tutorials/
    └── tools/
        └── nb_to_doc.py

## Role:
Provide the repository's single, centralized tooling surface for converting tutorial Jupyter notebooks into documentation artifacts and normalized source notebooks, delegating all process execution to a caller-supplied process-runner.

## Description:
Where and when this module is used
- Primary consumers:
  - Documentation build scripts (local or CI) that transform tutorial notebooks into rendered documentation and ensure stored notebooks are cleaned.
  - Maintenance and developer tooling that batch-converts or normalizes notebooks prior to publishing.
  - Any utility that requires a stable, centralized notebook → documentation conversion sequence.
- Typical usage:
  - A caller configures a process-runner callable into the nb_to_doc module, then iterates notebook basenames and invokes convert_nb for each basename to execute the notebook, export to reStructuredText, and clear outputs in-place.
Why these components are grouped here
- Cohesion: groups utilities for producing and normalizing documentation source artifacts (tutorial notebooks) so the conversion sequence and policy are consistent across CI, local builds, and ad-hoc maintenance scripts.
- Layer boundary: this package is tooling-level (documentation generation) and intentionally avoids implementing its own subprocess plumbing; it relies on an injected helper for process execution.

## Components:
- tutorials.tools.nb_to_doc.convert_nb(nbname: str) -> None
  - Orchestrates a three-step jupyter nbconvert CLI sequence on the notebook named nbname + ".ipynb": (1) execute the notebook in-place, (2) export it to nbname + ".rst", and (3) clear outputs in-place. See the component-level documentation at docs.tutorials.tools.nb_to_doc.convert_nb for full behavior and examples.
- (Runtime requirement) tutorials.tools.nb_to_doc.sh
  - Not a defined symbol in code by this package; instead, the module expects a callable with the prescribed contract to be assigned into the module namespace before convert_nb is called (see Public API and Dependencies).

Mermaid dependency graph:
flowchart TD
    docs["docs (package)"]
    tutorials["docs.tutorials (subpackage)"]
    nb_to_doc["tutorials.tools.nb_to_doc (module)"]
    convert_nb["convert_nb(nbname)"]
    sh_helper["sh (injected callable)"]
    jupyter["jupyter nbconvert (external CLI)"]
    notebook["<nbname>.ipynb (filesystem)"]
    rstfile["<nbname>.rst (filesystem)"]

    docs --> tutorials
    tutorials --> nb_to_doc
    nb_to_doc --> convert_nb
    convert_nb --> sh_helper
    sh_helper --> jupyter
    convert_nb --> notebook
    convert_nb --> rstfile

## Public API:
- tutorials.tools.nb_to_doc.convert_nb(nbname: str) -> None
  - Description: Run a fixed CLI sequence against nbname + ".ipynb" to (a) execute the notebook in-place, (b) export to reStructuredText named nbname + ".rst", and (c) clear outputs in-place.
  - Expected input:
    - nbname: the notebook basename without the ".ipynb" extension (for example, pass "intro" to act on "intro.ipynb"). Supplying a value that already ends with ".ipynb" will produce malformed filenames (e.g., "intro.ipynb.ipynb").
  - Return value:
    - None on success. On failure, exceptions raised by the injected process-runner are propagated.
  - Usage notes (how to integrate):
    - Before calling convert_nb, assign a callable to the module-level name sh inside tutorials.tools.nb_to_doc. That callable will be used to run constructed CLI commands synchronously.
    - convert_nb mutates files on disk and should be run from a working directory where nbname + ".ipynb" is accessible, or callers should change the working directory accordingly.
    - convert_nb does not perform retries, logging, or stdout/stderr handling — those responsibilities belong to the injected process-runner.
  - Link to component-level docs:
    - See docs.tutorials.tools.nb_to_doc.convert_nb for exact command tokens used, expected exceptions, and postconditions.

- tutorials.tools.nb_to_doc.sh (injection contract)
  - Signature (expected): sh(cmd_tokens: Sequence[str]) -> Any
  - Behavior contract:
    - Accepts a sequence (list/tuple) of command tokens to execute (e.g., tokens that start with "jupyter", "nbconvert", ...).
    - Synchronously runs the command and:
      - Returns on success (return value is ignored by convert_nb).
      - Raises an exception on failure (for example, subprocess.CalledProcessError, FileNotFoundError, OSError). convert_nb propagates these exceptions.
    - The callable is responsible for logging, stdout/stderr capture, timeouts, and other operational policies as needed by the caller.

## Dependencies:
- Internal:
  - tutorials.tools.nb_to_doc (module): contains the concrete implementation of convert_nb and documents exact CLI sequences and token ordering. Module-level documentation here intentionally summarizes behavior while delegating implementation specifics to the component docs.
- External (system / third-party):
  - jupyter nbconvert must be installed and available on the system PATH; convert_nb constructs CLI invocations for this external tool.
  - No runtime Python package imports are required by the package-level surface; the heavy-lifting is performed by the external jupyter CLI executed via the injected process-runner.

## Call flow (high level):
1. Caller assigns a process-runner callable to tutorials.tools.nb_to_doc.sh.
2. Caller invokes convert_nb with nbname (basename without extension).
3. convert_nb builds three CLI command token lists (execute, export to rst, clear outputs) and calls sh for each in order.
4. Each sh invocation runs the external jupyter nbconvert CLI; if any call raises an exception, convert_nb stops and propagates the exception.
5. On success, a .rst file exists and the .ipynb has been executed and then cleared of outputs.

## Exceptions and error semantics:
- convert_nb does not wrap exceptions: any exception thrown by the injected sh callable (subprocess.CalledProcessError, FileNotFoundError, OSError, etc.) will propagate to the caller.
- Common failure modes:
  - Missing jupyter executable on PATH -> FileNotFoundError or subprocess-related error from sh.
  - Non-zero exit code from nbconvert -> subprocess.CalledProcessError or equivalent from sh.
  - Missing notebook file in current working directory -> sh will fail when nbconvert is invoked, resulting in propagated exceptions.
- Recommended caller behavior:
  - Catch and handle exceptions around convert_nb to perform retries, logging, or to translate exceptions into higher-level errors for CI scripts.

## Side effects and postconditions:
- Side effects:
  - Overwrites or creates nbname + ".rst".
  - Modifies nbname + ".ipynb" in-place (first executed, then cleared of outputs).
- Postconditions on successful return:
  - nbname + ".rst" exists and reflects the executed notebook export.
  - nbname + ".ipynb" has had outputs cleared.
  - No return value; success is indicated by absence of exception.

## Constraints and best practices:
- Provide nbname without ".ipynb".
- Ensure the working directory or path visibility contains the target .ipynb file before calling.
- Inject a robust sh callable that handles logging, captures stdout/stderr, enforces timeouts, and maps process failures to appropriate exceptions for your environment.
- Avoid running convert_nb concurrently on the same notebook basename to prevent race conditions.
- For batch operations, callers should sequence or isolate conversions (per-notebook working directories or external locks) when consistent results are required.
- For CI: treat convert_nb failures as build failures and capture stdout/stderr via the provided process-runner for diagnostics.

## Where to find implementation details:
- For the exact CLI token lists, ordering, and the expected sh callable examples, consult the component-level documentation at docs.tutorials.tools.nb_to_doc.convert_nb (component docs are stored under docs/tutorials and include the required sh contract and concrete command sequences).

