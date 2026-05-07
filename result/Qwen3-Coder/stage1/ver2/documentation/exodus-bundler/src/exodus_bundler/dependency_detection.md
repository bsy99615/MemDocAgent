# `dependency_detection.py`

## `src.exodus_bundler.dependency_detection.PackageManager` · *class*

## Summary:
Abstract base class for package managers that detects file dependencies using system package management tools.

## Description:
The PackageManager class serves as a foundation for implementing package manager-specific dependency detection logic. It provides common infrastructure for finding dependencies of files by querying system package managers like dpkg, rpm, or others. Subclasses must define class variables such as cache_directory, list_command, list_regex, owner_command, and owner_regex to specify the package manager behavior.

This class is intended to be subclassed rather than instantiated directly, with each subclass implementing the specific package manager interface for their respective system.

## State:
- cache_directory (str): Path to the package manager's cache directory. Must be set by subclasses.
- list_command (list[str]): Command and arguments to list dependencies for a package. Must be set by subclasses.
- list_regex (str): Regular expression pattern to extract dependency paths from list command output. Defaults to '(.*)'.
- owner_command (list[str]): Command and arguments to find which package owns a file. Must be set by subclasses.
- owner_regex (str): Regular expression pattern to extract package name from owner command output. Defaults to '(.*)'.

## Lifecycle:
- Creation: Instantiate subclasses that properly configure all required class variables (cache_directory, list_command, owner_command).
- Usage: Call find_dependencies() with a file path to discover its dependencies, or call find_owner() to find which package owns a file.
- Destruction: No explicit cleanup required; uses standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[find_dependencies(path)] --> B[find_owner(path)]
    B --> C[cache_exists]
    B --> D[commands_exist]
    D --> E[find_executable()]
    C --> F[os.path.exists()]
    F --> G[os.path.isdir()]
    A --> H[subprocess.Popen()]
    H --> I[stdout.decode()]
    I --> J[re.search()]
    J --> K[os.path.exists()]
    K --> L[not os.path.isdir()]
```

## Raises:
- None explicitly raised by __init__ (as it's an abstract base class with no constructor)
- All methods may return None when preconditions aren't met (cache doesn't exist, commands don't exist, etc.)

## Example:
```python
# Subclass example for a specific package manager
class DpkgPackageManager(PackageManager):
    cache_directory = '/var/lib/dpkg'
    list_command = ['dpkg', '-L']
    list_regex = r'^/usr/lib/.*?(\S+)$'
    owner_command = ['dpkg', '-S']
    owner_regex = r'^[^:]+: (.+)$'

# Usage
pm = DpkgPackageManager()
dependencies = pm.find_dependencies('/usr/bin/python3')
if dependencies:
    print(f"Dependencies: {dependencies}")
```

### `src.exodus_bundler.dependency_detection.PackageManager.find_dependencies` · *method*

## Summary:
Finds and returns the list of file dependencies for a given path by executing a system command and parsing its output.

## Description:
This method determines the dependencies of a specified file by first identifying the owning executable or script, then executing a configured system command to list those dependencies. It parses the command output using a regular expression pattern to extract dependency file paths, filtering out directories and non-existent files.

## Args:
    path (str): The absolute or relative path to the file whose dependencies are to be discovered.

## Returns:
    list[str] | None: A list of absolute paths to dependency files, or None if no owner could be determined for the input path.

## Raises:
    None explicitly raised, though subprocess execution may raise OSError or other subprocess-related exceptions.

## State Changes:
    Attributes READ: self.find_owner, self.list_command, self.list_regex
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The path argument must be a valid string representing a file path
        - The PackageManager instance must have properly initialized list_command and list_regex attributes
        - The system command specified by list_command must be executable and capable of listing dependencies for the owner
        
    Postconditions:
        - Returns a list of existing regular files (not directories) that match the regex pattern
        - Returns None if no owner can be determined for the input path
        - All returned paths are absolute paths to existing files

## Side Effects:
    - Executes external subprocess commands
    - Reads from the filesystem to check existence of dependency paths
    - May perform I/O operations to execute system commands and read their output

### `src.exodus_bundler.dependency_detection.PackageManager.find_owner` · *method*

## Summary:
Finds the package owner of a given file path by executing a system command and parsing its output.

## Description:
This method determines which package owns a specified file path by running a configured system command (typically from dpkg or rpm) and extracting the package name from the command's output using a regular expression pattern. It serves as a crucial component in the dependency resolution pipeline, enabling the bundler to identify which packages contain specific files.

The method is called during the dependency detection phase when resolving file ownership for inclusion in the bundle. It's separated from other logic to encapsulate the file ownership determination functionality and make it reusable across different parts of the dependency detection system.

## Args:
    path (str): The absolute path to the file whose owning package needs to be identified

## Returns:
    str or None: The name of the package that owns the file, or None if:
        - The cache directory doesn't exist or isn't a directory
        - Required system commands aren't available
        - The command execution fails
        - No match is found in the command output using the owner_regex pattern

## Raises:
    None explicitly raised, though subprocess execution may raise OSError or other subprocess-related exceptions

## State Changes:
    Attributes READ: self.cache_exists, self.commands_exist, self.owner_command, self.owner_regex
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The PackageManager instance must have properly initialized attributes:
          cache_directory, owner_command, and owner_regex
        - The cache_directory must exist and be a directory
        - The owner_command must reference valid system commands
    Postconditions:
        - Returns None if any prerequisite conditions fail
        - Returns a string containing the package name if successful

## Side Effects:
    - Executes a subprocess command using the system's package management tool
    - Reads environment variables (copies os.environ)
    - May cause I/O operations through subprocess communication

### `src.exodus_bundler.dependency_detection.PackageManager.cache_exists` · *method*

## Summary:
Checks whether the configured cache directory exists and is a valid directory.

## Description:
This property determines if the cache directory specified by `self.cache_directory` exists and is a directory. It's used as a configuration validation check in the package manager's dependency resolution workflow.

## Args:
    None

## Returns:
    bool: True if `self.cache_directory` exists and is a directory; False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: self.cache_directory
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - `self.cache_directory` must be set to a string path
    - The path should be a valid filesystem path
    
    Postconditions:
    - Returns a boolean indicating directory existence status
    - Does not modify any object state

## Side Effects:
    I/O: Performs filesystem operations using `os.path.exists()` and `os.path.isdir()`

### `src.exodus_bundler.dependency_detection.PackageManager.commands_exist` · *method*

## Summary:
Checks whether the required system commands for package management exist in the system PATH.

## Description:
This property verifies that both the list command and owner command required for dependency detection are available in the system PATH. It is used as a prerequisite check before attempting to resolve package dependencies or ownership information.

## Args:
    None

## Returns:
    bool: True if both commands exist in PATH, False otherwise.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self.list_command[0] (first element of list command tuple/list)
    - self.owner_command[0] (first element of owner command tuple/list)

## Constraints:
    Preconditions:
    - self.list_command must be a sequence with at least one element
    - self.owner_command must be a sequence with at least one element
    - Both commands should be valid command names that can be found in PATH
    
    Postconditions:
    - Returns a boolean value indicating existence of both commands

## Side Effects:
    None

## `src.exodus_bundler.dependency_detection.Apt` · *class*

## Summary:
A Debian/Ubuntu package manager implementation that detects file dependencies using dpkg tools.

## Description:
The Apt class implements package management functionality for Debian-based Linux distributions using the dpkg package manager. It inherits from PackageManager and provides specific configuration for dpkg commands to find file dependencies and package ownership. This class is intended to be used as a concrete implementation for systems running Debian, Ubuntu, or similar distributions that utilize dpkg as their package manager.

## State:
- cache_directory (str): Path to the dpkg cache directory, set to '/var/cache/apt'
- list_command (list[str]): Command to list package contents, set to ['dpkg-query', '-L']
- list_regex (str): Regular expression to extract dependency paths from list command output, set to '(.+)'
- owner_command (list[str]): Command to find which package owns a file, set to ['dpkg', '-S']
- owner_regex (str): Regular expression to extract package names from owner command output, set to '(.+): '

## Lifecycle:
- Creation: Instantiate directly as Apt() - no special construction requirements
- Usage: Call find_dependencies() or find_owner() methods to detect file dependencies
- Destruction: Uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[find_dependencies(path)] --> B[find_owner(path)]
    B --> C[cache_exists]
    B --> D[commands_exist]
    D --> E[find_executable()]
    C --> F[os.path.exists()]
    F --> G[os.path.isdir()]
    A --> H[subprocess.Popen()]
    H --> I[stdout.decode()]
    I --> J[re.search()]
    J --> K[os.path.exists()]
    K --> L[not os.path.isdir()]
```

## Raises:
- None explicitly raised by __init__ (inherits from PackageManager base class)
- All methods may return None when preconditions aren't met (cache doesn't exist, commands don't exist, etc.)

## Example:
```python
# Create an Apt package manager instance
apt_manager = Apt()

# Find dependencies of a file
dependencies = apt_manager.find_dependencies('/usr/bin/python3')
if dependencies:
    print(f"Dependencies: {dependencies}")

# Find which package owns a file
owner = apt_manager.find_owner('/lib/x86_64-linux-gnu/libc.so.6')
if owner:
    print(f"Package owner: {owner}")
```

## `src.exodus_bundler.dependency_detection.Pacman` · *class*

## Summary:
Pacman package manager implementation for dependency detection in Arch Linux systems.

## Description:
The Pacman class implements package manager functionality specifically for Arch Linux's Pacman package manager. It inherits from PackageManager and provides the necessary configuration to detect file dependencies and find which packages own specific files using the pacman command-line tool.

This class is designed to be used as a subclass of PackageManager and should not be instantiated directly. It provides the specific configuration needed for Arch Linux's Pacman package manager to detect package dependencies and file ownership.

## State:
- cache_directory (str): Path to the Pacman cache directory, set to '/var/cache/pacman'
- list_command (list[str]): Command to list package contents, set to ['pacman', '-Ql']
- list_regex (str): Regular expression to extract file paths from list command output, set to r'.*\s+(\/.+)'
- owner_command (list[str]): Command to find package ownership of files, set to ['pacman', '-Qo']
- owner_regex (str): Regular expression to extract package names from owner command output, set to r' is owned by (.*)\s+.*'

## Lifecycle:
- Creation: Instantiate as a subclass of PackageManager with all required class variables configured (this class is not meant to be instantiated directly, but rather used as a base for dependency detection)
- Usage: Call find_dependencies() or find_owner() methods to detect package dependencies or ownership
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[find_dependencies(path)] --> B[find_owner(path)]
    B --> C[cache_exists]
    B --> D[commands_exist]
    D --> E[find_executable()]
    C --> F[os.path.exists()]
    F --> G[os.path.isdir()]
    A --> H[subprocess.Popen()]
    H --> I[stdout.decode()]
    I --> J[re.search()]
    J --> K[os.path.exists()]
    K --> L[not os.path.isdir()]
```

## Raises:
- None explicitly raised by __init__ (inherited from PackageManager base class)
- Methods may return None when preconditions aren't met (cache doesn't exist, commands don't exist, etc.)

## Example:
```python
# This class is meant to be used as a subclass for dependency detection
# Usage would be through the parent class interface
pacman_manager = Pacman()  # This is allowed but typically used via PackageManager interface
dependencies = pacman_manager.find_dependencies('/usr/bin/python3')
if dependencies:
    print(f"Dependencies: {dependencies}")

# Find which package owns a specific file
owner = pacman_manager.find_owner('/etc/passwd')
if owner:
    print(f"File owned by package: {owner}")
```

## `src.exodus_bundler.dependency_detection.Yum` · *class*

## Summary:
Subclass of PackageManager that implements RPM-based dependency detection for YUM package manager used in Red Hat-based Linux distributions.

## Description:
The Yum class extends PackageManager to provide RPM-based dependency detection infrastructure for systems using the YUM package manager. As a concrete subclass, it implements the required class variables to interface with RPM-based package management systems on Red Hat, CentOS, and Fedora distributions.

This class leverages the common infrastructure provided by PackageManager to query system package managers and find file dependencies or determine package ownership. It specifically configures the package manager interface for YUM/RPM environments.

## State:
- cache_directory (str): Path to YUM's cache directory, set to '/var/cache/yum'
- list_command (list[str]): Command to list package contents, set to ['rpm', '-ql'] 
- list_regex (str): Regular expression pattern to extract dependency paths, set to r'(.+)'
- owner_command (list[str]): Command to find package ownership of files, set to ['rpm', '-qf']
- owner_regex (str): Regular expression pattern to extract package names, set to r'(.+)'

All class variables are static class attributes that define YUM-specific behavior for package management operations.

## Lifecycle:
- Creation: Instantiate Yum directly as it's a concrete subclass with no special construction requirements
- Usage: Call find_dependencies() or find_owner() methods to detect dependencies or find package ownership
- Destruction: Standard Python garbage collection handles cleanup

## Method Map:
```mermaid
graph TD
    A[Yum.find_dependencies(path)] --> B[Yum.find_owner(path)]
    B --> C[Yum.cache_exists]
    B --> D[Yum.commands_exist]
    D --> E[find_executable()]
    C --> F[os.path.exists()]
    F --> G[os.path.isdir()]
    A --> H[subprocess.Popen()]
    H --> I[stdout.decode()]
    I --> J[re.search()]
    J --> K[os.path.exists()]
    K --> L[not os.path.isdir()]
```

## Raises:
- None explicitly raised by __init__ (inherits from PackageManager base class)
- All methods may return None when preconditions aren't met (cache doesn't exist, commands don't exist, etc.)

## Example:
```python
# Create YUM package manager instance
yum_manager = Yum()

# Find dependencies of a file
dependencies = yum_manager.find_dependencies('/usr/bin/python3')
if dependencies:
    print(f"Dependencies: {dependencies}")

# Find which package owns a file
owner = yum_manager.find_owner('/lib/libc.so.6')
if owner:
    print(f"Package owning file: {owner}")
```

## `src.exodus_bundler.dependency_detection.detect_dependencies` · *function*

## Summary:
Detects project dependencies by trying multiple package managers in priority order until dependencies are found.

## Description:
This function implements a priority-based dependency detection system that attempts to identify project dependencies using various package managers. It sequentially tests each package manager in a predefined order until one successfully finds dependencies, returning the first valid result. This approach allows for support of multiple package management systems (npm, pip, yarn, etc.) while prioritizing detection methods.

The function is designed to be flexible and extensible, supporting different package managers through a common interface. By trying package managers in priority order, it ensures that the most appropriate detection method is used for a given project type.

## Args:
    path (str): The filesystem path to the project directory where dependencies should be detected.

## Returns:
    list[str] or None: A list of detected dependency identifiers if dependencies are found, or None if no dependencies are detected by any package manager.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The `path` parameter must be a valid filesystem path to a project directory
    - The `package_managers` variable must be defined in scope as an iterable of objects
    - Each object in `package_managers` must implement a `find_dependencies` method that accepts a path parameter
    - The `find_dependencies` method should return a list of dependency identifiers or an empty list if no dependencies are found
    
    Postconditions:
    - Returns immediately upon finding the first non-empty dependency list from any package manager
    - Returns None if no package manager successfully detects dependencies

## Side Effects:
    None explicitly stated in the function itself.

## Control Flow:
```mermaid
flowchart TD
    A[Start detect_dependencies] --> B{package_managers defined?}
    B -- Yes --> C[Iterate package_managers]
    C --> D[Call package_manager.find_dependencies(path)]
    D --> E{Dependencies found?}
    E -- Yes --> F[Return dependencies]
    E -- No --> G[Continue to next package_manager]
    G --> H{More package_managers?}
    H -- Yes --> C
    H -- No --> I[Return None]
    B -- No --> J[Return None]
```

## Examples:
    # Basic usage with error handling
    try:
        deps = detect_dependencies("/path/to/nodejs/project")
        if deps:
            print(f"Found {len(deps)} dependencies:")
            for dep in deps:
                print(f"  - {dep}")
        else:
            print("No dependencies detected")
    except Exception as e:
        print(f"Dependency detection failed: {e}")

    # Usage in a bundler context
    project_path = "/my/app"
    dependencies = detect_dependencies(project_path)
    if dependencies:
        # Proceed with bundling using detected dependencies
        bundle_with_dependencies(project_path, dependencies)
    else:
        # Fall back to manual dependency specification
        bundle_fallback(project_path)

