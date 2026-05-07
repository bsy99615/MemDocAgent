# `paths.py`

## `src.ydata_profiling.utils.paths.get_project_root` · *function*

## Summary:
Returns a pathlib.Path that points to the directory four levels above this module's file location — used as a canonical project/repository root location.

## Description:
- Purpose: Encapsulates the relative-parent calculation (walk up four directory levels from this module file) so callers can consistently obtain a project-root Path without duplicating the parent-traversal logic.
- Known callers: No direct call sites were identified in the provided snapshot. Common consumers in a codebase include configuration loaders, test fixtures, packaging or build utilities, and any module that needs to reference top-level repository files (for example, pyproject.toml, setup.cfg, top-level data directories).
- Why a separate function: Centralizing this exact "four parents up" rule prevents subtle inconsistencies across the codebase (off-by-one parent mistakes), makes the intent explicit (project root), and allows a single place to change the traversal depth if the repository layout changes.
- What it does not do: It does not check that the returned path exists, does not resolve symlinks, does not convert to absolute form, and does not read filesystem metadata.

## Args:
- None

## Returns:
- pathlib.Path
  - A Path equal to Path(__file__).parent.parent.parent.parent.
  - If the module file path is near the filesystem root (i.e., fewer than four distinct parent directories above the file), the repeated .parent accesses return the filesystem root Path (pathlib semantics) and that root Path is returned.
  - If __file__ is a relative path, the returned Path will be relative (it is not automatically made absolute).
  - The function always returns a Path object; it never returns None.

## Raises:
- NameError
  - Condition: Executing module does not define the module-level variable __file__ (for example, certain embedded or interactive execution contexts).
  - Source: Direct reference to __file__ with no guard causes Python to raise NameError when __file__ is absent.
- TypeError
  - Condition: __file__ exists but is neither a str, bytes, nor os.PathLike object acceptable to pathlib.Path (an atypical situation).
  - Source: pathlib.Path will raise TypeError when constructed with incompatible types.
- Note: The function itself contains no try/except; any other exceptions would originate from the Path constructor given unusual environment conditions.

## Constraints:
- Preconditions:
  - The function should be called in a normal module execution environment where __file__ is present and holds a path-like string (typical for modules imported from files).
- Postconditions:
  - The caller receives a pathlib.Path representing exactly four parent traversals of this module file path (or the filesystem root if fewer parents exist).
  - No global state or external resources are modified by this call.

## Side Effects:
- None. The function does not perform I/O, does not read or write files, and does not mutate global state. It only constructs and returns an in-memory pathlib.Path object.

## Control Flow:
flowchart TD
    Start["Start"]
    A["Access __file__"]
    B["Call Path(__file__)"]
    C["Ascend to parent (1)"]
    D["Ascend to parent (2)"]
    E["Ascend to parent (3)"]
    F["Ascend to parent (4)"]
    G["Return resulting Path"]
    Start --> A --> B --> C --> D --> E --> F --> G

## Examples (usage described in prose and error-handling guidance):
- Typical usage:
  - Call the function to obtain a candidate project root Path object.
  - Combine the returned Path with a top-level filename or directory name (for example, a configuration file at the repository root).
  - If an absolute, symlink-resolved path is required, the caller should call .resolve() on the returned Path before using it.
  - Before opening or reading files under that path, the caller should check existence via .exists() or .is_file() and handle the missing-file case.

- Error handling guidance:
  - In environments where __file__ may be unavailable (packaged/frozen apps, some interactive runners), wrap the call in exception handling for NameError and TypeError and provide a fallback (for example, a configured path or environment variable).
  - Example flow in prose: attempt to obtain root = get_project_root(); if NameError or TypeError occurs, log a clear error and fall back to an explicit configured root path; otherwise use root.resolve() and verify that expected files exist before proceeding.

## `src.ydata_profiling.utils.paths.get_config` · *function*

## Summary:
Constructs and returns a pathlib.Path pointing to the provided file name joined to the package/repository root (resolved as two directory levels above this module).

## Description:
This tiny utility centralizes the convention that the package root for resource/config files is located two directories above this module file and appends the supplied file_name to that base. It is intended for callers that need a stable, package-relative path to configuration or resource files (for example, locating "config.yml" or files under a "configs/" directory).

Known callers within the codebase:
- No direct callers were discovered in the provided snapshot. Typical usage locations include configuration loaders, tests, CLI entry points, or utilities that need to locate package-relative resources.

Why this logic is extracted:
- Avoids repeating Path(__file__).parent.parent / file_name at multiple call sites.
- Encapsulates package-root resolution policy so it can be changed centrally if project layout evolves.
- Improves readability by expressing intent (get a package-root-relative path) in one place.

## Args:
    file_name (str):
        - Description: Name or relative path segment(s) to append to the package root (e.g., "config.yml" or "configs/default.yml").
        - Required: Yes — this parameter has no default.
        - Note on runtime behavior: the function's static annotation is str, but at runtime pathlib's division operator (Path / other) accepts any os.PathLike or objects that can be converted to strings. Passing path-like objects (e.g., pathlib.Path or os.PathLike) will normally work even though the annotation is str.

## Returns:
    pathlib.Path:
        - A Path equal to Path(__file__).parent.parent joined with file_name using pathlib semantics.
        - If file_name is a relative path, the returned Path represents the package root followed by those segments.
        - If file_name is an absolute path string (platform-specific), the right-hand operand's absolute path takes precedence per pathlib semantics and the returned Path will be the absolute path.
        - The function does not check filesystem existence or perform any I/O.

## Raises:
    TypeError:
        - Raised by pathlib internals if file_name is of an unsupported type for the division operation (e.g., a type that cannot be interpreted as a path or string).
    NameError (or similar):
        - In unusual runtimes where the module-level __file__ is not defined, evaluating Path(__file__) can raise NameError; callers should not rely on this function in such environments without validating __file__ availability.

## Constraints:
    Preconditions:
    - The caller must supply file_name (annotated as str).
    - The runtime must provide a file-backed module environment where __file__ is defined for the module.

    Postconditions:
    - The function returns a pathlib.Path representing the joined path. No files are created, modified, or validated.

## Side Effects:
    - None. The function only constructs and returns an in-memory pathlib.Path object; it performs no disk I/O, network access, logging, or global state mutation.

## Control Flow:
flowchart TD
    Start --> Base[Compute base = Path(__file__).parent.parent]
    Base --> Join[Compute result = base / file_name]
    Join --> Absolute{Is file_name an absolute path (pathlib-handled)?}
    Absolute -->|Yes| ReturnAbs[Return absolute-path result]
    Absolute -->|No| ReturnRel[Return base / file_name]
    ReturnAbs --> End
    ReturnRel --> End

## Examples:
    Typical relative filename:
        cfg_path = get_config("config.yml")
        # cfg_path == Path(<package_root>) / "config.yml"
        # Existence not checked; call cfg_path.exists() before opening.

    Subdirectory path:
        cfg_path = get_config("configs/default.yaml")
        # cfg_path == Path(<package_root>) / "configs" / "default.yaml"

    Passing a Path-like at runtime (works despite str annotation):
        cfg_path = get_config(Path("configs") / "default.yaml")  # pathlib.Path accepted at runtime

    Absolute-path behavior:
        cfg_path = get_config("/etc/project/config.yml")
        # On POSIX, result == Path("/etc/project/config.yml") — absolute right operand wins.

    Recommended pattern with existence check:
        cfg_path = get_config("config.yml")
        if not cfg_path.exists():
            raise FileNotFoundError(f"Configuration not found at {cfg_path}")
        fh = cfg_path.open("r", encoding="utf-8")
        # ... read from fh

## `src.ydata_profiling.utils.paths.get_data_path` · *function*

## Summary:
Returns a pathlib.Path pointing to the repository's top-level "data" directory (i.e., the project root joined with "data"), without performing any filesystem checks.

## Description:
- Known callers within the provided snapshot:
  - No direct call sites were identified in the provided snapshot. 
- Typical callers and context:
  - Configuration loaders or utilities that need a canonical location for repository test/example datasets.
  - Test fixtures or local scripts that read/write sample data stored under a top-level data/ directory.
  - Any module that needs a stable, central reference to the repository's "data" subdirectory for loading assets (CSV, JSON, etc.).
- Why this is a separate function:
  - Centralizes the single authoritative rule "project root + 'data'" so all callers obtain the same Path object consistently and avoid duplicating or mis-implementing the join logic.
  - Keeps callers free from needing to know how the project root is computed (the get_project_root function encapsulates that detail).

## Args:
- None

## Returns:
- pathlib.Path
  - A Path equal to get_project_root() / "data".
  - Behavior notes:
    - If get_project_root() returns a relative Path, the returned Path will be relative (it is not made absolute by this function).
    - If get_project_root() returns the filesystem root (for example, because the module file had fewer than four parents), the returned Path will be root / "data" (e.g., "/data").
    - The function always returns a pathlib.Path object and never returns None.

## Raises:
- Any exception raised by get_project_root() will propagate unchanged. In typical environments this includes:
  - NameError
    - Condition: The module-level variable __file__ is not defined in the execution environment used by get_project_root(). This occurs in certain embedded or interactive runtimes.
  - TypeError
    - Condition: get_project_root() attempts to construct a Path from a non-path-like object; this is unusual but will propagate as TypeError.
- This function itself does not perform try/except handling; it will not raise additional exceptions beyond what get_project_root() or pathlib.Path.__truediv__ would raise in abnormal conditions.

## Constraints:
- Preconditions:
  - The runtime should be a normal module execution environment where get_project_root() can read __file__ (typical for modules imported from files). If __file__ is absent, callers should expect NameError.
  - No filesystem guarantees (existence, permissions) are required before calling; the function merely composes Path objects in memory.
- Postconditions:
  - The caller receives a pathlib.Path representing the "data" child of whatever Path get_project_root() returned.
  - No filesystem state is changed by this function.

## Side Effects:
- None. The function performs no I/O, no filesystem checks, and does not mutate any global state. It only constructs and returns an in-memory pathlib.Path object.

## Control Flow:
flowchart TD
    Start["Start"]
    A["Call get_project_root()"]
    B{"get_project_root() raises? (NameError/TypeError/...)"}
    C["Compose returned Path with 'data' using Path.__truediv__"]
    D["Return resulting Path"]
    Start --> A --> B
    B -- Yes --> D
    B -- No --> C --> D

## Examples (usage and error-handling guidance; presented as prose steps):
- Typical successful use:
  1. Call root_data = get_data_path().
  2. Optionally convert to an absolute, symlink-resolved path if required: call root_data.resolve() before passing it to IO APIs.
  3. Before opening a specific file under the data directory, check existence with (root_data / "myfile.csv").exists() and handle the missing-file case.

- Robust usage with fallback:
  1. Attempt to obtain the data directory Path via get_data_path().
  2. If NameError or TypeError is raised (which indicates get_project_root() could not compute the repository root in the current environment), catch the exception and fall back to a configured path (for example, an environment variable or a CLI-provided absolute path).
  3. Validate the chosen Path with .exists() or .is_dir() prior to performing file operations and surface a clear error if the expected data directory is absent.

- Notes for callers that need absolute or verified paths:
  - This function only composes the path in memory. If callers require existence guarantees, they must explicitly check the filesystem (exists(), is_dir(), is_file()) and resolve symlinks/relative components with resolve() as needed.

## `src.ydata_profiling.utils.paths.get_html_template_path` · *function*

*No documentation generated.*

