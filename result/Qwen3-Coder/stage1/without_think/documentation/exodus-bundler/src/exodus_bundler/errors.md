# `errors.py`

## `src.exodus_bundler.errors.FatalError` · *class*

## Summary:
Represents a fatal error condition in the Exodus bundler that cannot be recovered from.

## Description:
FatalError is a custom exception class that extends Python's built-in Exception class. It is specifically designed to indicate critical failures in the Exodus bundler system where recovery is not possible or meaningful. Unlike regular exceptions that might be caught and handled gracefully, FatalError signals that the bundling process must terminate immediately.

This exception is typically raised when encountering irrecoverable issues such as:
- Critical configuration problems
- Core system failures
- Invalid state that prevents further processing
- Resource exhaustion that cannot be mitigated

## State:
The class has no additional attributes beyond those inherited from Exception. It maintains the standard Exception behavior with message and args properties.

## Lifecycle:
Creation: Instances are created by calling FatalError() with optional error message arguments, e.g., FatalError("Critical failure occurred").

Usage: The exception should be raised to indicate unrecoverable errors and typically not caught in application code, but rather allowed to propagate up to the main error handler which will terminate the process.

Destruction: No special cleanup is required as it inherits standard Python exception behavior.

## Method Map:
```mermaid
graph TD
    A[FatalError()] --> B[Exception.__init__]
    B --> C[Standard Exception behavior]
```

## Raises:
The constructor raises no additional exceptions beyond those that could occur during normal Exception instantiation.

## Example:
```python
# Raising a fatal error
raise FatalError("Configuration file is missing or invalid")

# Catching and handling (not recommended for fatal errors)
try:
    # Some operation that might fail fatally
    process_bundle()
except FatalError as e:
    log_error(f"Fatal error occurred: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.DependencyDetectionError` · *class*

## Summary:
Represents a fatal error that occurs during dependency detection in the Exodus bundler.

## Description:
DependencyDetectionError is a specialized fatal exception that indicates a critical failure in the dependency resolution process. This error is raised when the bundler encounters issues that prevent it from successfully identifying or resolving project dependencies, such as circular dependencies, missing dependencies, or malformed dependency specifications.

The error inherits from FatalError, indicating that the bundling process cannot continue once this error is encountered. This is a terminal condition that requires immediate termination of the bundling operation.

## State:
This class inherits from FatalError and follows the standard Exception behavior. It can be initialized with error messages and maintains standard exception properties.

## Lifecycle:
Creation: Instances are created by calling DependencyDetectionError() with optional error message arguments, e.g., DependencyDetectionError("Failed to resolve dependency tree").

Usage: The exception should be raised to indicate unrecoverable dependency detection failures and typically not caught in application code, but rather allowed to propagate up to the main error handler which will terminate the process.

Destruction: No special cleanup is required as it inherits standard Python exception behavior.

## Method Map:
```mermaid
graph TD
    A[DependencyDetectionError()] --> B[FatalError.__init__]
    B --> C[Exception.__init__]
    C --> D[Standard Exception behavior]
```

## Raises:
The constructor raises no additional exceptions beyond those that could occur during normal Exception instantiation.

## Example:
```python
# Raising a dependency detection error
raise DependencyDetectionError("Circular dependency detected in package.json")

# Catching and handling (not recommended for fatal errors)
try:
    # Some operation that might fail during dependency detection
    detect_dependencies()
except DependencyDetectionError as e:
    log_error(f"Dependency detection failed: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.InvalidElfBinaryError` · *class*

## Summary:
Represents a fatal error condition indicating that an ELF binary is invalid or corrupted in the Exodus bundler.

## Description:
InvalidElfBinaryError is a specialized exception that extends FatalError and is raised when the Exodus bundler encounters an ELF (Executable and Linkable Format) binary that cannot be processed due to being malformed, corrupted, or otherwise invalid. This error indicates a critical failure in the bundling process where the system cannot continue because the ELF binary doesn't meet the expected format requirements.

The error is typically raised during ELF binary validation or processing phases when the bundler detects inconsistencies in the binary structure, invalid headers, unsupported architectures, or other fundamental issues that prevent proper analysis or packaging of the binary.

## State:
This class inherits all state from FatalError and has no additional attributes. It maintains the standard Exception behavior with message and args properties.

## Lifecycle:
Creation: Instances are created by calling InvalidElfBinaryError() with optional error message arguments, e.g., InvalidElfBinaryError("ELF binary is corrupted").

Usage: The exception should be raised to indicate unrecoverable ELF processing failures and typically not caught in application code, but rather allowed to propagate up to the main error handler which will terminate the process.

Destruction: No special cleanup is required as it inherits standard Python exception behavior.

## Method Map:
```mermaid
graph TD
    A[InvalidElfBinaryError()] --> B[FatalError.__init__]
    B --> C[Exception.__init__]
    C --> D[Standard Exception behavior]
```

## Raises:
The constructor raises no additional exceptions beyond those that could occur during normal Exception instantiation.

## Example:
```python
# Raising an invalid ELF binary error
raise InvalidElfBinaryError("ELF binary header is invalid")

# Catching and handling (not recommended for fatal errors)
try:
    validate_elf_binary(binary_path)
except InvalidElfBinaryError as e:
    log_error(f"Fatal ELF processing error: {e}")
    sys.exit(1)
```

## `src.exodus_bundler.errors.MissingFileError` · *class*

## Summary:
Represents a fatal error condition indicating that a required file is missing during the Exodus bundling process.

## Description:
MissingFileError is a specialized exception that extends FatalError to specifically indicate when the bundler encounters a situation where a required file cannot be found or accessed. This error is raised when the bundling process depends on a file that is either missing from the filesystem, has incorrect permissions, or is otherwise inaccessible.

This exception is part of the Exodus bundler's fatal error handling system, signaling that the bundling process cannot continue due to a critical resource deficiency. Unlike recoverable errors, MissingFileError indicates an irrecoverable condition that requires immediate termination of the bundling process.

## State:
The class inherits all state from FatalError and has no additional attributes. It maintains the standard Exception behavior with message and args properties.

## Lifecycle:
Creation: Instances are created by calling MissingFileError() with optional error message arguments, e.g., MissingFileError("Required file 'config.json' not found").

Usage: The exception should be raised to indicate that a critical file dependency is missing and the bundling process must terminate immediately.

Destruction: No special cleanup is required as it inherits standard Python exception behavior from Exception.

## Method Map:
```mermaid
graph TD
    A[MissingFileError()] --> B[FatalError.__init__]
    B --> C[Exception.__init__]
    C --> D[Standard Exception behavior]
```

## Raises:
The constructor raises no additional exceptions beyond those that could occur during normal Exception instantiation.

## Example:
```python
# Raising a missing file error
raise MissingFileError("Required asset file 'main.js' not found in bundle directory")

# Typical usage in bundler code
def load_required_file(filepath):
    if not os.path.exists(filepath):
        raise MissingFileError(f"Required configuration file '{filepath}' is missing")
    # ... rest of file loading logic
```

## `src.exodus_bundler.errors.UnexpectedDirectoryError` · *class*

## Summary:
Represents a fatal error condition that occurs when an unexpected directory structure is encountered during the Exodus bundling process.

## Description:
UnexpectedDirectoryError is a specialized fatal exception that indicates the bundler has encountered a directory structure that violates expected conventions or constraints. This error is raised when the bundling process detects directories that shouldn't be present, directories in unexpected locations, or directory layouts that break the bundler's assumptions about project organization.

The error serves as a safeguard to prevent processing invalid directory structures that could lead to corrupted bundles or undefined behavior. As a FatalError subclass, it signals that the bundling process must terminate immediately and cannot recover from this condition.

## State:
The class inherits all state from FatalError including the standard Exception behavior with message and args properties. It maintains no additional attributes beyond those inherited from Exception.

## Lifecycle:
Creation: Instances are created by calling UnexpectedDirectoryError() with optional error message arguments, e.g., UnexpectedDirectoryError("Unexpected directory structure detected").

Usage: The exception should be raised when the bundler encounters directory structures that violate its expected layout, typically during validation phases of the bundling process.

Destruction: No special cleanup is required as it inherits standard Python exception behavior.

## Method Map:
```mermaid
graph TD
    A[UnexpectedDirectoryError()] --> B[FatalError.__init__]
    B --> C[Exception.__init__]
    C --> D[Standard Exception behavior]
```

## Raises:
The constructor raises no additional exceptions beyond those that could occur during normal Exception instantiation.

## Example:
```python
# Raising an unexpected directory error
raise UnexpectedDirectoryError("Found unexpected node_modules directory in source folder")

# Typical usage in bundler validation
def validate_directory_structure(self, path):
    if os.path.exists(os.path.join(path, "node_modules")):
        raise UnexpectedDirectoryError("node_modules directory found in unexpected location")
```

## `src.exodus_bundler.errors.UnsupportedArchitectureError` · *class*

## Summary:
Represents a fatal error condition that occurs when the Exodus bundler encounters an unsupported CPU architecture.

## Description:
`UnsupportedArchitectureError` is a specialized fatal exception that indicates the bundling process cannot proceed because the current system's CPU architecture is not supported by the Exodus bundler. This error extends `FatalError`, signaling that the failure is irrecoverable and the bundling process must terminate immediately.

This exception is typically raised during the initialization or execution phases of the bundler when:
- The target architecture is not among the supported architectures
- The system architecture cannot be determined or is unrecognized
- An architecture-specific operation fails due to lack of support

The purpose of having this distinct exception type is to provide clear error categorization for architecture-related failures, allowing for more specific error handling or logging while maintaining the fatal nature of the condition.

## State:
The class inherits all behavior from `FatalError` and follows standard Python Exception inheritance. It does not add any additional instance attributes beyond those inherited from the exception hierarchy.

## Lifecycle:
Creation: Instances are created by calling `UnsupportedArchitectureError()` with optional error message arguments, e.g., `UnsupportedArchitectureError("ARM64 architecture is not supported on this platform")`.

Usage: The exception should be raised to indicate unsupported architecture conditions and typically not caught in application code, but rather allowed to propagate up to the main error handler which will terminate the process.

Destruction: No special cleanup is required as it inherits standard Python exception behavior.

## Method Map:
```mermaid
graph TD
    A[UnsupportedArchitectureError()] --> B[FatalError.__init__]
    B --> C[Exception.__init__]
    C --> D[Standard Exception behavior]
```

## Raises:
The constructor raises no additional exceptions beyond those that could occur during normal Exception instantiation.

## Example:
```python
# Raising an unsupported architecture error
raise UnsupportedArchitectureError("x86_64 architecture is not supported on this platform")

# Typical usage in architecture validation
def validate_target_architecture(arch):
    supported_archs = ["amd64", "arm64"]
    if arch not in supported_archs:
        raise UnsupportedArchitectureError(f"Architecture '{arch}' is not supported")
```

