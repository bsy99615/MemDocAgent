# `src`

## Tree:
src/
└── ydata_profiling/

## Role:
Acts as the repository source root that contains the project's Python packages and modules. Its single responsibility is to hold and expose package(s) that make up the library/application. It does not itself implement runtime logic beyond being a container for importable packages.

## Description:
- Where/when this module is used:
  - The src directory is the code root that will be placed on PYTHONPATH during development and packaging. Consumers import packages beneath it (for example: import ydata_profiling).
  - Typical consumers are application code, tests, command-line entry points, and packaging tooling that import the top-level package(s) under src/.

- Why these components are grouped here:
  - The src layout isolates importable library packages from other repository artifacts (docs, tests, CI config, packaging metadata). All library source code belongs under src/ to create a clear boundary between code and non-code content and to avoid accidental imports from the repository root during development.

## Components:
- Public subpackages and modules (one-line descriptions)
  - ydata_profiling (package)
    - The top-level package directory for the project. Holds the library implementation and submodules. See dedicated module-level documentation for ydata_profiling for detailed components and APIs.

Mermaid dependency graph (high-level):
graph LR
    SRC["src/ (source root)"]
    YP["ydata_profiling/"]
    SRC --> YP

## Public API:
- The src directory itself does not expose runtime APIs.
- The effective public API of this module is the set of packages placed underneath it — currently:
  - ydata_profiling
    - Usage note: Import the library with "import ydata_profiling" (or specific submodules, e.g., ydata_profiling.<submodule>) after ensuring src/ is on PYTHONPATH or the package is installed.
- No other public symbols are defined at the src level.

## Dependencies:
- Internal dependencies:
  - None at the src root. All functional dependencies are inside the packages under src/ (e.g., ydata_profiling). Refer to the ydata_profiling module documentation for its internal and external dependencies.

- External dependencies:
  - The src container has no third-party dependencies. Third-party libraries are required by the packages placed inside src/ and will be listed in their respective module docs and in packaging metadata (pyproject.toml / setup.cfg / requirements files).

## Constraints:
- Callers must ensure the repository's layout places src/ on PYTHONPATH (one of):
  - Install the package into the environment (recommended for production/testing).
  - During development, run code with PYTHONPATH set to the repository root or use tooling (e.g., pip install -e .) so imports resolve to the src/ packages.
- Thread-safety / ordering:
  - None enforced at the src level. Thread-safety concerns are the responsibility of the packages beneath src/.
- Initialization prerequisites:
  - None at the src container level. Import-time side effects (if any) will be defined by the packages (ydata_profiling.__init__ and its submodules); consult the ydata_profiling module docs for any required initialization steps.

Notes and Next Steps:
- This document intentionally avoids implementation details because the src/ tree is a container. To complete module-level documentation that lists functions, classes, public symbols, dependencies, and constraints, provide the file-level listings or the module-level documentation for the ydata_profiling package. Once those are available, they should be linked here (e.g., "See MODULE: ydata_profiling") rather than duplicated.

