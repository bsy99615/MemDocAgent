# `errors.py`

## `src.exodus_bundler.errors.FatalError` · *class*

## Summary:
A custom exception class representing unrecoverable errors that terminate the Exodus bundler process.

## Description:
FatalError is a specialized exception type that signals critical failures in the Exodus bundler system. When raised, it indicates that the bundling process cannot continue and must be terminated immediately. This exception should only be used for situations where recovery is impossible or inappropriate, such as configuration errors, system resource exhaustion, or fundamental logical inconsistencies in the bundling pipeline.

The class inherits directly from Python's built-in Exception class, maintaining all standard exception behaviors while providing semantic clarity for error handling within the bundler context.

## State:
This class has no instance attributes beyond those inherited from Exception. It maintains the standard Exception interface with message, args, and traceback capabilities.

## Lifecycle:
Creation: Instances are created by calling FatalError() or FatalError(message) with optional error messages. The exception can be raised directly using the 'raise' keyword.

Usage: Typically used in error handling paths where the bundler encounters an unrecoverable condition. The exception propagates up the call stack until caught by the main error handler which terminates the process.

Destruction: No explicit cleanup is required as Python's garbage collector handles memory management. The exception object is automatically destroyed after being handled.

## Method Map:
```mermaid
graph TD
    A[Code Execution] --> B{Encounter Fatal Condition}
    B --> C[FatalError(message)]
    C --> D[Raise Exception]
    D --> E[Exception Propagation]
    E --> F[Main Error Handler]
    F --> G[Process Termination]
```

## Raises:
This class itself does not raise any exceptions during instantiation. It inherits standard Exception behavior for construction and propagation.

## Example:
```python
# Raising a fatal error
raise FatalError("Configuration file not found")

# Catching and handling
try:
    # Some bundling operation
    process_bundle(config)
except FatalError as e:
    print(f"Fatal error occurred: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.DependencyDetectionError` · *class*

## Summary:
A custom exception class representing unrecoverable errors that occur during dependency detection in the Exodus bundler process.

## Description:
DependencyDetectionError is a specialized exception type that signals critical failures in the dependency detection phase of the Exodus bundler system. When raised, it indicates that the bundler encountered an unrecoverable issue while attempting to identify or resolve dependencies required for the bundling process. This exception inherits from FatalError, ensuring that dependency detection failures result in immediate process termination.

This error class serves as a distinct abstraction to separate dependency detection failures from other types of fatal errors in the bundler system, allowing for more granular error handling and logging.

## State:
This class has no instance attributes beyond those inherited from Exception and FatalError. It maintains the standard Exception interface with message, args, and traceback capabilities.

## Lifecycle:
Creation: Instances are created by calling DependencyDetectionError() or DependencyDetectionError(message) with optional error messages. The exception can be raised directly using the 'raise' keyword.

Usage: Typically used in dependency resolution and analysis functions where the bundler encounters an irrecoverable condition that prevents proper dependency identification or resolution. The exception propagates up the call stack until caught by the main error handler which terminates the process.

Destruction: No explicit cleanup is required as Python's garbage collector handles memory management. The exception object is automatically destroyed after being handled.

## Method Map:
```mermaid
graph TD
    A[Code Execution] --> B{Encounter Dependency Detection Failure}
    B --> C[DependencyDetectionError(message)]
    C --> D[Raise Exception]
    D --> E[Exception Propagation]
    E --> F[Main Error Handler]
    F --> G[Process Termination]
```

## Raises:
This class itself does not raise any exceptions during instantiation. It inherits standard Exception behavior for construction and propagation.

## Example:
```python
# Raising a dependency detection error
raise DependencyDetectionError("Failed to resolve required package dependencies")

# Catching and handling
try:
    # Dependency resolution operation
    resolve_dependencies(package_list)
except DependencyDetectionError as e:
    print(f"Dependency detection failed: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.InvalidElfBinaryError` · *class*

## Summary:
Represents a fatal error that occurs when an invalid ELF binary is encountered during the Exodus bundling process.

## Description:
InvalidElfBinaryError is a specialized exception that extends FatalError. It is raised when the Exodus bundler encounters an ELF (Executable and Linkable Format) binary that fails validation checks or is fundamentally malformed, preventing further processing.

This exception inherits all behavior from FatalError, which signals critical failures in the bundling system that require immediate termination of the process.

## State:
This class inherits all state from FatalError and has no additional instance attributes. It maintains the standard Exception interface with message, args, and traceback capabilities.

## Lifecycle:
Creation: Instances are created by calling InvalidElfBinaryError() or InvalidElfBinaryError(message) with an optional error message describing the specific validation failure.

Usage: Typically used in ELF binary validation routines where the input fails all validity checks. The exception propagates up the call stack until caught by the main error handler which terminates the process.

Destruction: No explicit cleanup is required as Python's garbage collector handles memory management. The exception object is automatically destroyed after being handled.

## Method Map:
```mermaid
graph TD
    A[ELF Binary Processing] --> B{Validate ELF Format}
    B --> C{Validation Fails?}
    C -->|Yes| D[InvalidElfBinaryError(message)]
    D --> E[Raise Exception]
    E --> F[Exception Propagation]
    F --> G[Main Error Handler]
    G --> H[Process Termination]
    C -->|No| I[Continue Processing]
```

## Raises:
This class itself does not raise any exceptions during instantiation. It inherits standard Exception behavior for construction and propagation.

## Example:
```python
# Raising an invalid ELF binary error
raise InvalidElfBinaryError("ELF header magic number mismatch")

# Catching and handling
try:
    validate_elf_binary(file_path)
except InvalidElfBinaryError as e:
    print(f"Critical error: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.MissingFileError` · *class*

## Summary:
A custom exception class representing unrecoverable errors in the Exodus bundler system.

## Description:
MissingFileError is a specialized exception that extends FatalError. It is used within the Exodus bundler to signal critical failures where the bundling process cannot continue due to fundamental issues that prevent recovery. As a subclass of FatalError, it inherits all standard exception behaviors and follows the same error handling patterns used throughout the system.

The specific purpose of this exception is to indicate when file-related issues have occurred that make continued execution impossible. While the exact circumstances under which it's raised are not defined in this class, it follows the established pattern of FatalError for signaling unrecoverable conditions.

## State:
This class inherits all behavior from FatalError and has no additional instance attributes. It maintains the standard Exception interface with message, args, and traceback capabilities.

## Lifecycle:
Creation: Instances are created by calling MissingFileError() or MissingFileError(message) with an optional descriptive error message. The exception can be raised directly using the 'raise' keyword.

Usage: Typically used in error handling paths where the bundler encounters an unrecoverable condition related to file access or availability. The exception propagates up the call stack until caught by the main error handler which terminates the process.

Destruction: No explicit cleanup is required as Python's garbage collector handles memory management. The exception object is automatically destroyed after being handled.

## Method Map:
```mermaid
graph TD
    A[Code Execution] --> B{Encounter Critical Condition}
    B --> C[MissingFileError(message)]
    C --> D[Raise Exception]
    D --> E[Exception Propagation]
    E --> F[Main Error Handler]
    F --> G[Process Termination]
```

## Raises:
This class itself does not raise any exceptions during instantiation. It inherits standard Exception behavior for construction and propagation.

## Example:
```python
# Raising a missing file error
raise MissingFileError("Source file 'main.js' not found in project directory")

# Catching and handling
try:
    # Some bundling operation
    process_bundle(config)
except MissingFileError as e:
    print(f"Fatal error occurred: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.UnexpectedDirectoryError` · *class*

## Summary:
A custom exception indicating that an unexpected directory was encountered during the Exodus bundling process, requiring immediate termination.

## Description:
UnexpectedDirectoryError is a specialized exception that signals when the bundler encounters a directory structure or location that violates expected conventions or constraints. This error is classified as fatal, meaning the bundling process cannot continue and must be terminated immediately. The exception typically occurs when the bundler expects a specific directory layout or configuration but encounters an unexpected directory arrangement that could lead to incorrect processing or security vulnerabilities.

This exception follows the same pattern as other fatal errors in the Exodus bundler system, providing semantic clarity for directory-related critical failures while maintaining compatibility with the standard Exception interface.

## State:
This class inherits all state from Python's built-in Exception class and contains no additional instance attributes. It maintains the standard Exception interface with message, args, and traceback capabilities.

## Lifecycle:
Creation: Instances are created by calling UnexpectedDirectoryError() or UnexpectedDirectoryError(message) with optional error messages. The exception can be raised directly using the 'raise' keyword.

Usage: Typically used in directory validation and traversal logic where the bundler encounters directories that violate expected patterns, such as unexpected nested directories, unauthorized directory locations, or directories in invalid positions within the bundling structure.

Destruction: No explicit cleanup is required as Python's garbage collector handles memory management. The exception object is automatically destroyed after being handled.

## Method Map:
```mermaid
graph TD
    A[Directory Validation] --> B{Unexpected Directory Found}
    B --> C[UnexpectedDirectoryError(message)]
    C --> D[Raise Exception]
    D --> E[Exception Propagation]
    E --> F[Main Error Handler]
    F --> G[Process Termination]
```

## Raises:
This class itself does not raise any exceptions during instantiation. It inherits standard Exception behavior for construction and propagation.

## Example:
```python
# Raising an unexpected directory error
raise UnexpectedDirectoryError("Found unexpected directory 'temp' in bundle root")

# Catching and handling
try:
    # Directory traversal logic
    validate_directory_structure(bundle_path)
except UnexpectedDirectoryError as e:
    print(f"Fatal directory error occurred: {e}")
    sys.exit(1)
```

