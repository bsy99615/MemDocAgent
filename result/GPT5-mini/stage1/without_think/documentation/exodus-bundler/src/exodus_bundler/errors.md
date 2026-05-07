# `errors.py`

## `src.exodus_bundler.errors.FatalError` · *class*

## Summary:
A lightweight semantic exception type used to signal a non-recoverable (fatal) error condition inside the exodus_bundler package.

## Description:
FatalError exists solely as a distinct exception class to differentiate fatal, non-retryable failures from other exceptions. It does not add behavior or state beyond Python's built-in Exception; its purpose is to communicate intent to callers and to allow callers to catch or let fatal errors propagate explicitly.

Typical scenarios to instantiate FatalError:
- When an operation encounters a condition from which recovery or retry is not possible and the code should abort the current operation flow.
- When a library-internal check detects a corruption, invariant violation, or misconfiguration that callers should treat as terminal.
- Tests and higher-level orchestration code may raise FatalError to force immediate termination of a logical operation.

Known callers/factories:
- The class itself is a marker only. Specific call sites within the repository that raise FatalError are not enumerated here; treat FatalError as the designated exception to raise for fatal conditions.

Responsibility boundary:
- Use FatalError when you want a clearly identifiable, catchable signal for a fatal condition. Do not use it for routine or expected errors where the caller can recover; use more specific or standard exceptions instead.

## State:
- Attributes inherited from BaseException:
    - args (tuple): Tuple of positional arguments passed at construction; typically (message,).
    - __cause__, __context__, __traceback__ (as provided by Python's exception machinery).
- There are no additional attributes added by FatalError.
- Valid values:
    - Any values valid for Exception.args ( FatalError accepts any number of positional arguments; most callers pass a single string message ).
- Class invariants:
    - No additional invariants beyond those guaranteed by Python's BaseException (i.e., args exists and may be empty).

## Lifecycle:
Creation:
- Instantiate like any Exception:
    - FatalError("human-readable message") or FatalError(message, detail1, detail2)
- No required arguments; zero-argument construction is valid (args will be empty).

Usage:
- Raise to signal a fatal condition:
    - raise FatalError("irrecoverable error")
- Catch explicitly when the caller intends to handle or transform fatal conditions:
    - except FatalError as exc:
          handle_fatal_condition(exc)
- Typical sequencing:
    1. Code detects fatal condition.
    2. Code raises FatalError with a descriptive message and optional details.
    3. Either a local handler catches FatalError and performs shutdown/cleanup, or it propagates upward to a global handler which logs, reports, or terminates the operation.
Destruction:
- No explicit cleanup required by FatalError instances. They participate in Python's normal exception lifecycle (traceback capture, garbage collection). Do not rely on FatalError to perform any resource cleanup; perform cleanup in except/finally blocks.

## Method Map:
A minimal flow/interaction diagram (Mermaid flowchart) showing inheritance and typical raise/catch flow.

graph LR
    A[Code detects fatal condition] --> B[raise FatalError(...)]
    B --> C{Caught locally?}
    C -->|yes| D[except FatalError: handle / cleanup]
    C -->|no| E[Propagate to caller or top-level handler]
    E --> F[Global handler logs/reports and terminates operation]
    subgraph Inheritance
        G[FatalError] --> H[Exception]
        H --> I[BaseException]
    end

## Raises:
- __init__ does not raise exceptions of its own (it inherits BaseException.__init__). Typical construction does not raise.
- Note: Python may raise a TypeError if the exception machinery itself is misused (this is inherited behavior and not specific to FatalError). There are no FatalError-specific raise conditions.

## Example:
- Create and raise a fatal error with a message:
    raise FatalError("Configuration missing required key X")

- Catch and handle a fatal error at a boundary where cleanup is required:
    try:
        perform_critical_operation()
    except FatalError as e:
        logger.error("Fatal error encountered: %s", e)
        perform_shutdown_cleanup()
        raise  # optionally re-raise to let a higher-level handler terminate

- Construct with supplementary details:
    detail = {"stage": "bundle_write", "file": filename}
    raise FatalError("Bundle write failed", detail)

Notes:
- Since FatalError subclasses Exception, typical Exception tooling (logging.exception, traceback printing, catching by type) works unchanged.
- Prefer descriptive messages to aid diagnostics because FatalError carries no additional structured fields by default.

## `src.exodus_bundler.errors.DependencyDetectionError` · *class*

## Summary:
A specific marker exception indicating a fatal error that occurred during dependency detection within the exodus_bundler package.

## Description:
DependencyDetectionError is a lightweight, semantic exception type used to signal that the process which inspects, resolves, or validates package/module dependencies has encountered a non-recoverable error. It exists solely to distinguish dependency-detection failures from other fatal conditions so callers can catch, log, or respond to this category explicitly.

Scenarios where this class should be instantiated:
- When code that enumerates or resolves runtime/build-time dependencies detects a configuration problem, missing dependency, incompatible version constraint, or corrupted metadata that makes continuing impossible.
- When a dependency graph check detects a cycle or an unrecoverable conflict that must abort the bundling process.

Known callers/factories:
- Specific call sites are not enumerated here. Treat DependencyDetectionError as the designated exception to raise from dependency-detection code paths inside the exodus_bundler module.

Motivation and responsibility boundary:
- Provides a distinct type for dependency-related fatal errors so higher-level orchestration can distinguish them from other fatal conditions (e.g., disk I/O failures). It does not add behavior or state beyond FatalError; its responsibility is purely semantic classification.

## State:
- Inherited attributes (from BaseException via FatalError):
    - args (tuple): Positional arguments passed at construction (commonly a single human-readable message).
    - __cause__, __context__, __traceback__: Standard Python exception attributes for chaining and diagnostics.
- No additional attributes are introduced by DependencyDetectionError.
- Valid values:
    - Any values valid for Exception.args (strings, tuples, structured details). Typical usage: a single descriptive message string, optionally followed by supplemental context objects.
- Class invariants:
    - There are no invariants beyond BaseException guarantees (args exists and may be empty). Instances must be immutable in the sense that they carry only the constructor-provided state and Python's exception bookkeeping.

## Lifecycle:
- Creation:
    - Instantiate like any exception: DependencyDetectionError("descriptive message") or DependencyDetectionError(message, details).
    - No required arguments; zero-argument construction is valid (args will be empty).
- Usage:
    - Raise from within dependency-detection routines to abort processing and signal a fatal dependency problem.
    - Typical handling patterns:
        1. Raise immediately when an unrecoverable dependency issue is detected.
        2. Catch at a boundary responsible for cleanup, logging, or user-facing error reporting.
        3. Optionally re-raise to propagate to global error handlers.
    - There are no methods on this class; usage consists of raising and catching by type.
- Destruction:
    - No cleanup responsibilities. Exception instances participate in normal Python exception lifecycle and garbage collection. Perform resource cleanup in surrounding try/except/finally blocks, not in the exception class.

## Method Map:
graph LR
    A[Dependency detection code] --> B[raise DependencyDetectionError(...)]
    B --> C{Caught locally?}
    C -->|yes| D[except DependencyDetectionError: log, cleanup, transform]
    C -->|no| E[Propagate to caller or top-level handler]
    E --> F[Global handler logs/reports and terminates operation]
    subgraph Inheritance
        G[DependencyDetectionError] --> H[FatalError]
        H --> I[Exception]
        I --> J[BaseException]
    end

## Raises:
- __init__ does not raise exceptions of its own; it inherits BaseException.__init__ behavior.
- Typical construction does not raise; only Python-level errors unrelated to this class (e.g., misuse of exception machinery) could surface as TypeError from the interpreter, which is not specific to DependencyDetectionError.

## Example:
- Raise with a descriptive message:
    raise DependencyDetectionError("Missing required dependency 'libfoo' for bundle 'mybundle'")

- Raise with supplemental context:
    context = {"bundle": "mybundle", "stage": "resolve_deps", "missing": "libfoo"}
    raise DependencyDetectionError("Dependency resolution failed", context)

- Catch at a boundary to perform cleanup and re-raise or transform:
    try:
        resolve_dependencies(bundle)
    except DependencyDetectionError as exc:
        logger.error("Dependency detection failed: %s", exc)
        cleanup_partial_state(bundle)
        raise  # optionally re-raise for higher-level handling

## `src.exodus_bundler.errors.InvalidElfBinaryError` · *class*

## Summary:
A marker exception type indicating that an ELF binary is invalid or malformed; it is a specific kind of fatal error used to signal non-recoverable problems during ELF parsing, validation, or processing.

## Description:
InvalidElfBinaryError exists to distinguish fatal errors that specifically relate to invalid ELF binaries from other fatal conditions. It is a semantic subclass of FatalError (which itself subclasses Exception) and does not add behavior or state beyond its parent. Use this exception when code that reads, parses, validates, or processes ELF binaries encounters a condition that makes continuing the current operation impossible (for example: malformed headers, inconsistent program/header table sizes, unsupported ELF class/endianness discovered at runtime, or failed integrity checks that invalidate the binary).

Typical instantiation scenarios:
- ELF loader or parser detects structural corruption (bad magic, truncated sections, header inconsistencies).
- Validation step finds unsupported ELF properties (unexpected class, ABI mismatch) that cannot be automatically adapted to.
- Post-processing discovers checksums or content invariants that fail, making produced artifacts unusable.

Motivation and responsibility boundary:
- Provides a narrow, catchable type for callers that want to handle ELF-specific fatal failures differently from other fatal errors (e.g., log specialized diagnostics, skip a single input file, or increment an ELF-specific failure metric).
- Do not use this class for recoverable or non-ELF-related errors; prefer more specific or standard exceptions where appropriate.

## State:
- Inherited attributes (from BaseException via FatalError):
    - args (tuple): Positional arguments passed at construction, typically a single human-readable message but may include additional context objects.
    - __cause__, __context__, __traceback__: Standard exception attributes managed by Python.
- This class adds no new attributes or properties.
- Valid values:
    - Any values valid for Exception.args; commonly a single string message describing the ELF validation failure.
- Class invariants:
    - No additional invariants beyond those guaranteed by Python's BaseException (args exists and may be empty).
    - Instances must always be treated as immutable exception objects after construction (standard Python exception semantics).

## Lifecycle:
Creation:
- Instantiate like any Exception / FatalError:
    - InvalidElfBinaryError("human-readable message describing why the ELF binary is invalid")
    - Additional contextual objects may be supplied in args (e.g., InvalidElfBinaryError("Bad header", header_bytes))
- No constructor arguments are required; zero-argument construction is valid (args will be empty).

Usage:
- Typical pattern is to raise when an ELF-related irrecoverable condition is detected:
    - raise InvalidElfBinaryError("truncated section header table")
- Callers may catch this specific class to perform ELF-specific handling, or catch FatalError/Exception to handle more generally.
- No methods are defined on this class; usage is identical to standard exceptions: raise, catch, inspect .args or str() for messaging.

Destruction / cleanup:
- No cleanup responsibilities. Exception instances participate in Python's usual traceback and garbage collection lifecycle.
- Resource cleanup should be performed in the surrounding code (except/finally), not by the exception itself.

## Method Map:
graph LR
    A[Code detects invalid ELF condition] --> B[raise InvalidElfBinaryError(...)]
    B --> C{Caught by caller?}
    C -->|yes - specific| D[except InvalidElfBinaryError: handle ELF-specific recovery/diagnostics]
    C -->|yes - general| E[except FatalError/Exception: general cleanup, log and terminate]
    C -->|no| F[Propagate to higher-level handler or top-level process]
    subgraph Inheritance
        G[InvalidElfBinaryError] --> H[FatalError]
        H --> I[Exception]
        I --> J[BaseException]
    end

## Raises:
- The class itself does not raise exceptions during construction beyond what Python's BaseException may raise in abnormal misuse scenarios.
- Typical triggers for raising InvalidElfBinaryError (by callers) include:
    - Detection of malformed ELF headers or tables.
    - Unsupported or inconsistent ELF metadata discovered at runtime.
    - Integrity or validation checks failing in a way that prevents further processing.
- No additional runtime exceptions are introduced by this subclass.

## Example:
- Raise when ELF header magic is invalid:
    raise InvalidElfBinaryError("ELF magic missing or corrupted for file 'foo.so'")

- Catch specifically to log ELF diagnostics and continue processing other inputs:
    try:
        parse_and_validate_elf(path)
    except InvalidElfBinaryError as exc:
        logger.warning("Skipping file %s: invalid ELF binary: %s", path, exc)
        metrics.increment("elf_invalid_count")
        # continue with next file

- Re-raise as a FatalError for higher-level handling (optional; redundant because subclass relationship already qualifies):
    try:
        perform_elf_workflow()
    except InvalidElfBinaryError:
        logger.error("Fatal ELF error; aborting workflow")
        raise  # propagates InvalidElfBinaryError (also a FatalError)

## `src.exodus_bundler.errors.MissingFileError` · *class*

## Summary:
A semantic, fatal exception raised when a required file is missing; it marks a non-recoverable "file not found" condition inside the exodus_bundler package.

## Description:
MissingFileError exists solely as a specific subtype of FatalError to signal that a required filesystem artifact (file) was expected but not present, and that the condition is considered terminal for the current operation. It does not add behavior or attributes beyond those provided by FatalError (and Python's BaseException); its purpose is to make callers' intent explicit and to allow exception handlers to catch "missing-file" fatal errors distinctly from other fatal conditions.

Typical scenarios to instantiate MissingFileError:
- A bundling step attempts to open or validate an input file and discovers it does not exist or is inaccessible.
- A configuration or manifest references a file that cannot be located on disk.
- A pre-flight or integrity check confirms a required payload file is absent and the operation must abort.

Known callers/factories:
- Any component in exodus_bundler that validates filesystem inputs, reads bundle sources, or enforces manifest constraints should raise MissingFileError for irrecoverable missing-file cases. Specific call-sites are not enumerated here; treat MissingFileError as the designated exception to signal fatal missing-file conditions.

Responsibility boundary:
- Use MissingFileError when the absence of a file cannot be sensibly recovered from at the current call site and higher-level code should treat the situation as fatal. Do not use it for recoverable file-not-found cases where retry, fallback, or user prompting is expected.

## State:
- Inherited attributes (from BaseException / FatalError):
    - args (tuple): Positional arguments passed to the constructor. Typical usage is a single human-readable message and optionally supplemental details (e.g., filename, context dict).
    - __cause__, __context__, __traceback__: Standard exception attributes managed by Python.
- No new attributes or methods are introduced by MissingFileError.
- Valid values:
    - args may be empty or contain any Python objects; most callers pass a string message and optionally structured details.
- Class invariants:
    - No invariants beyond those of BaseException: args exists (possibly empty) and exception instances are immutable in typical usage (no methods that mutate instance state).

## Lifecycle:
- Creation:
    - Instantiate like any Exception / FatalError. No required parameters.
    - Example canonical instantiations:
        - MissingFileError("Required file not found: config.yml")
        - MissingFileError("Missing input", filename)
    - There are no factory methods on the class itself; construction is direct.
- Usage:
    - Typical usage is to raise the exception where the missing-file condition is detected:
        - raise MissingFileError(...)
    - Handlers may catch MissingFileError explicitly to run cleanup, logging, or user-facing error reporting:
        - except MissingFileError as exc: handle_missing_file(exc)
    - For error chaining when a lower-level file operation raises a built-in error (e.g., FileNotFoundError), raise MissingFileError from the original exception to preserve traceback and cause:
        - raise MissingFileError("...") from e
    - No special ordering of method calls is required; the class has no public methods other than those inherited from BaseException.
- Destruction:
    - No cleanup or resource management responsibilities. Instances participate in normal exception tracebacks and garbage collection. Perform resource cleanup in except/finally blocks surrounding the raise site or in handlers.

## Method Map:
graph LR
    A[Code attempts to access required file] --> B{File exists?}
    B -->|no| C[raise MissingFileError(message, details)]
    C --> D{Handler present?}
    D -->|yes| E[except MissingFileError: log / cleanup / notify]
    D -->|no| F[Propagate to caller or top-level fatal handler]
    F --> G[Global handler logs/reports and terminates operation]
    subgraph Inheritance
        H[MissingFileError] --> I[FatalError]
        I --> J[Exception]
        J --> K[BaseException]
    end

## Raises:
- __init__ does not raise exceptions on its own; construction follows BaseException semantics.
- Typical Python runtime errors may occur if exception machinery is misused (e.g., a TypeError raised by Python internals), but there are no MissingFileError-specific raise conditions.

## Example:
- Raising with a descriptive message and filename:
    raise MissingFileError("Required manifest file missing", filename)

- Chaining from a lower-level FileNotFoundError to preserve cause:
    try:
        open(path, "rb")
    except FileNotFoundError as e:
        raise MissingFileError("Unable to open required file", path) from e

- Catching, logging, and performing cleanup:
    try:
        perform_bundle_stage()
    except MissingFileError as exc:
        logger.error("Fatal missing-file error: %s", exc)
        perform_cleanup()
        raise  # optionally re-raise to propagate fatal termination

## `src.exodus_bundler.errors.UnexpectedDirectoryError` · *class*

## Summary:
A semantic, marker exception indicating that an operation encountered a directory where a non-directory (usually a file) was expected. It signals a non-recoverable error specific to unexpected directory/path-type conditions.

## Description:
UnexpectedDirectoryError exists to provide a distinct, catchable type for code that must specifically handle the case when a filesystem path is a directory but a file (or non-directory path) was required. Instantiate or raise this exception at call sites that detect a directory in an unexpected place (for example: when attempting to open, overwrite, or treat a path as a file during bundling, extraction, or validation).

Motivation and responsibility boundary:
- Purpose: make intent explicit and allow higher-level code to catch this specific fatal condition separately from other errors (for example, to provide clearer diagnostics or to apply different shutdown semantics).
- Boundary: it does not carry structured fields or behavior beyond its identity as a subclass of FatalError. Use it only to signal the "unexpected directory" condition; do not use it for general filesystem errors (use OSError or more specific exceptions for permission or I/O errors).

Known callers/factories:
- File/path validation and preprocessing routines that validate input/output locations before performing file operations.
- Bundler or extractor logic that expects a file but finds a directory at the target path.
- Higher-level orchestration code that converts filesystem-type checks into fatal conditions for the bundling pipeline.

## State:
- Inherited state:
    - args (tuple): positional arguments passed at construction (typically a single human-readable message).
    - __cause__, __context__, __traceback__: standard Python exception attributes maintained by the interpreter.
- No additional attributes or methods are defined by UnexpectedDirectoryError.
- Valid values:
    - Any values valid for Exception.args; typical usage supplies a single descriptive message string.
- Class invariants:
    - Instances are plain exceptions with no additional invariants beyond BaseException (i.e., args exists and may be empty).

## Lifecycle:
- Creation:
    - Instantiate like any Exception or FatalError, for example by supplying a human-readable message: UnexpectedDirectoryError("path /foo/bar is a directory, expected file").
    - No required constructor parameters; zero-argument construction is valid (args will be empty).
- Usage:
    - Raise to abort an operation when a directory is encountered in a place where a file/non-directory was required.
    - Catch either as UnexpectedDirectoryError to handle this specific case, or as FatalError/Exception to handle it generically.
    - No methods to call on the exception instance; interact through standard exception handling (except, logging, re-raising).
    - Typical sequencing:
        1. Detect path-type mismatch (is-directory check).
        2. Raise UnexpectedDirectoryError with a message describing the path and expected type.
        3. Local or higher-level handler logs and performs cleanup or terminates the process.
- Destruction:
    - No cleanup or resource management responsibilities. Cleanup must be performed by the code that catches the exception (finally/except blocks).

## Method Map:
graph LR
    A[Detect path-type mismatch] --> B[raise UnexpectedDirectoryError(...)]
    B --> C{Caught locally?}
    C -->|yes| D[except UnexpectedDirectoryError: handle specific cleanup or diagnostics]
    C -->|no| E[Propagate as FatalError to global handler]
    E --> F[Global handler logs/reports and terminates operation]
    subgraph Inheritance
        U[UnexpectedDirectoryError] --> V[FatalError]
        V --> W[Exception]
        W --> X[BaseException]
    end

## Raises:
- __init__ (inherited from BaseException/FatalError) does not raise its own exceptions under normal use.
- Construction may raise interpreter-level errors (e.g., in pathological misuse of the exception machinery), but there are no UnexpectedDirectoryError-specific raise conditions.

## Example:
- Create and raise with a message:
    raise UnexpectedDirectoryError("Target path '/tmp/bundle' is a directory; expected a file path")

- Catch and handle this specific condition:
    try:
        validate_target_path(path)
    except UnexpectedDirectoryError as e:
        logger.error("Unexpected directory at target: %s", e)
        perform_cleanup()
        raise  # optionally re-raise to let a higher-level FatalError handler terminate

- Construct without message (allowed but not recommended for diagnostic clarity):
    raise UnexpectedDirectoryError()

## `src.exodus_bundler.errors.UnsupportedArchitectureError` · *class*

## Summary:
A sentinel exception type indicating the bundler encountered an architecture (CPU/ABI/OS combination) it does not support. It is a fatal, non-recoverable error used to abort bundling operations when an unsupported target architecture is detected.

## Description:
UnsupportedArchitectureError exists solely to name a specific fatal condition: the target architecture (for example, a CPU architecture, OS/ABI, or platform variant) is not supported by the bundling operation. The class adds no behavior beyond its base class; its purpose is semantic — to make intent explicit and to allow callers to catch this specific failure mode separately from other fatal errors.

Scenarios to instantiate:
- The bundler examines a requested target architecture and determines it is not implemented or explicitly disallowed.
- A platform discovery routine returns an architecture string that the bundler cannot map to a supported runtime/packaging flow.
- Validation of a package's declared supported architectures finds none that match the execution environment.

Known callers/factories:
- Any component of the exodus_bundler package that validates or selects target architectures and treats an unsupported case as terminal should raise this exception. (The base FatalError documentation lists general usage for fatal exceptions; specific call sites are repository-local and not enumerated here.)

Motivation and responsibility boundary:
- Use UnsupportedArchitectureError when an operation must stop because continuing would produce invalid or unusable output for the requested architecture.
- Do not use this class for recoverable errors (e.g., transient I/O failures) or for policy/permission errors — those should use more specific exception types or standard exceptions.

## State:
- This class does not add any instance attributes beyond those provided by Python's BaseException.
- Inherited attributes:
    - args (tuple): Positional arguments passed at construction (commonly a single human-readable message).
    - __cause__, __context__, __traceback__: standard exception bookkeeping provided by Python.
- Valid values and constraints:
    - args may be empty or contain any values valid for Exception.args; typical usage is a single string message describing the unsupported architecture.
- Class invariants:
    - There are no additional invariants beyond those of BaseException and FatalError (i.e., args exists and may be empty).

## Lifecycle:
Creation:
- Instantiate like any exception:
    - UnsupportedArchitectureError("human-readable message describing architecture details")
- No required constructor arguments; zero-argument construction is valid (args will be empty).

Usage:
- Raise to indicate an unrecoverable unsupported-architecture condition:
    - raise UnsupportedArchitectureError("arm64 not supported on this platform")
- Typical call flow:
    1. Architecture validation code detects an unsupported target.
    2. It raises UnsupportedArchitectureError with a clear message (optionally including the offending architecture string and contextual details).
    3. A local boundary that can present a helpful error to users or perform cleanup may catch this specific exception type; otherwise it propagates as a fatal error.
- Cleanup and resource management should be handled by surrounding try/except/finally logic; the exception itself performs no cleanup.

Destruction:
- No explicit destruction or cleanup responsibilities. Instances participate in normal Python exception lifecycle and garbage collection.

## Method Map:
A minimal Mermaid flowchart (inheritance and raise/catch flow):

graph LR
    A[Validation detects unsupported architecture] --> B[raise UnsupportedArchitectureError(...)]
    B --> C{Caught locally?}
    C -->|yes| D[except UnsupportedArchitectureError: present friendly error / cleanup]
    C -->|no| E[Propagate to caller or global handler]
    E --> F[Global handler treats as fatal: log/report/terminate]
    subgraph Inheritance
        U[UnsupportedArchitectureError] --> F1[FatalError]
        F1 --> F2[Exception]
        F2 --> F3[BaseException]
    end

## Raises:
- __init__ inherits BaseException.__init__; constructing an instance does not raise exceptions of its own in normal usage.
- Typical triggers for raising this exception in code:
    - Unsupported architecture string or unsupported platform combination detected by validation logic.
- Note: Python-level errors unrelated to this class (TypeError from malformed exception usage, MemoryError, etc.) are possible but not specific to this exception.

## Example:
- Raise with a message describing the unsupported architecture:
    raise UnsupportedArchitectureError("Target architecture 'mips64' is not supported by this bundler")

- Catch and handle to provide a user-friendly error and perform cleanup:
    try:
        validate_and_bundle(target_arch)
    except UnsupportedArchitectureError as exc:
        logger.error("Cannot bundle for requested architecture: %s", exc)
        perform_user_facing_error_report(exc)
        # optional: re-raise or exit, depending on the caller's shutdown policy

- Construct with additional context (details tuple or dict may be provided as args, but no structured fields are enforced):
    detail = ("requested_arch", "mips64", "available", ["x86_64", "arm64"])
    raise UnsupportedArchitectureError("Unsupported target architecture", detail)

