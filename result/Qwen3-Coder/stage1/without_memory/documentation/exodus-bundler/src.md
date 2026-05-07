# `src`

## Tree:
```
src/
└── exodus_bundler/
    ├── __init__.py
    ├── bundling.py
    ├── cli.py
    ├── dependency_detection.py
    ├── errors.py
    ├── input_parsing.py
    ├── launchers.py
    └── templating.py
```

## Role:
This module provides a system for creating portable bundles of ELF binary executables that include all their runtime dependencies, allowing them to be relocated and executed on systems with incompatible system libraries.

## Description:
This module implements a sophisticated bundling system that takes ELF binary executables and packages them along with their dependencies into relocatable bundles. It handles ELF binary analysis, dependency resolution, and creates either installation scripts or tarballs that can be deployed on different systems.

The module is used primarily by the command-line interface (`cli.py`) but also provides core functionality that can be imported and used programmatically. It's designed to solve the problem of creating portable applications that don't depend on the specific system libraries present on the target machine.

## Components:
*   `Bundle` - Manages the collection and packaging of files into a bundle
*   `Elf` - Represents and analyzes ELF binary files
*   `File` - Represents individual files in the bundle
*   `bytes_to_int` - Utility function for converting bytes to integers
*   `create_bundle` - Main entry point for creating bundles
*   `create_unpackaged_bundle` - Core bundle creation logic
*   `detect_elf_binary` - Checks if a file is an ELF binary
*   `parse_dependencies_from_ldd_output` - Parses ldd output to extract dependencies
*   `resolve_binary` - Resolves binary paths from environment
*   `resolve_file_path` - Validates and resolves file paths
*   `run_ldd` - Executes ldd command to get dependencies
*   `stored_property` - Descriptor for memoized properties
*   `StderrFilter` - Logging filter for stderr messages
*   `StdoutFilter` - Logging filter for stdout messages
*   `configure_logging` - Sets up logging configuration
*   `main` - Command-line entry point
*   `parse_args` - Parses command-line arguments
*   `Apt` - Package manager implementation for Debian/Ubuntu systems
*   `PackageManager` - Base class for package managers
*   `Pacman` - Package manager implementation for Arch Linux systems
*   `Yum` - Package manager implementation for Red Hat/CentOS systems
*   `detect_dependencies` - Detects dependencies using package managers
*   `DependencyDetectionError` - Exception for dependency detection failures
*   `FatalError` - Base exception for fatal errors
*   `InvalidElfBinaryError` - Exception for invalid ELF binaries
*   `MissingFileError` - Exception for missing files
*   `UnexpectedDirectoryError` - Exception for unexpected directories
*   `UnsupportedArchitectureError` - Exception for unsupported architectures
*   `extract_exec_path` - Extracts executable paths from strace output
*   `extract_open_path` - Extracts file paths from open() calls in strace output
*   `extract_paths` - Extracts file paths from input content
*   `extract_stat_path` - Extracts file paths from stat() calls in strace output
*   `strip_pid_prefix` - Removes PID prefixes from strace lines
*   `CompilerNotFoundError` - Exception when no suitable compiler is found
*   `compile` - Compiles launcher code
*   `compile_diet` - Compiles with diet compiler
*   `compile_helper` - Helper for compilation processes
*   `compile_musl` - Compiles with musl compiler
*   `construct_bash_launcher` - Creates bash-based launchers
*   `construct_binary_launcher` - Creates binary launchers
*   `find_executable` - Finds executables in PATH
*   `render_template` - Renders templates with context
*   `render_template_file` - Renders template files with context

## Public API:
*   `create_bundle(executables, output, tarball=False, rename=[], chroot=None, add=[], no_symlink=[], shell_launchers=False, detect=False)` - Main function to create a bundle from executables
*   `create_unpackaged_bundle(executables, rename=[], chroot=None, add=[], no_symlink=[], shell_launchers=False, detect=False)` - Core bundle creation logic without output handling
*   `main()` - Command-line entry point that parses arguments and invokes bundle creation
*   `parse_args()` - Parses command-line arguments into a dictionary

## Dependencies:
*   Internal imports: `errors`, `dependency_detection`, `input_parsing`, `launchers`, `templating`
*   External imports: `argparse`, `base64`, `collections.defaultdict`, `filecmp`, `io`, `json`, `logging`, `os`, `shutil`, `signal`, `stat`, `struct`, `subprocess`, `sys`, `tempfile`, `threading`, `time`, `re`, `hashlib`, `tarfile`, `Popen`, `PIPE`, `find_executable_original`, `parent_directory`

## Constraints:
*   All input paths must be valid files, not directories
*   ELF binaries must be 32 or 64-bit little-endian architecture
*   The system must have `ldd` available for dependency detection
*   When using `--detect` flag, appropriate package manager tools must be installed
*   Bundle creation requires write permissions to temporary directories
*   Thread safety is not guaranteed for concurrent bundle creation operations

