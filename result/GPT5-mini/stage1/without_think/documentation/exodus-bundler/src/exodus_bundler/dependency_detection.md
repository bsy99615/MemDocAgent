# `dependency_detection.py`

## `src.exodus_bundler.dependency_detection.PackageManager` · *class*

## Summary:
Represents an abstraction for interrogating a system package manager to determine which package "owns" a given filesystem path and to list files (dependencies) provided by that package. The class encapsulates command construction, subprocess invocation, output parsing via regular expressions, and filesystem filtering.

## Description:
PackageManager is intended to be a minimal, reusable adapter between the bundling/dependency-collection logic and an external package manager (e.g., dpkg, rpm, or other system/package-specific tooling). The class itself contains no __init__ initializer and exposes a small set of class/instance attributes that must be populated (usually by a concrete subclass or by setting attributes on an instance) to suit a specific package manager's command-line interface.

Typical scenarios where this class is used:
- During a bundling or packaging pipeline when the system needs to map a file path to the package that provides it, and then enumerate files owned by that package to include them as dependencies.
- As a base/adaptor class: concrete implementations set the appropriate commands and regexes for a specific package manager and may be instantiated by a factory or used as a mixin.

Known callers/factories:
- Higher-level dependency collection or bundling code will call find_dependencies(path) or find_owner(path). No constructor/factory is enforced by this class; callers must ensure required attributes are set prior to use.

Motivation and responsibility boundary:
- Isolates external command invocation and parsing of package-manager output from the rest of the codebase.
- Does not manage caching, network calls, or filesystem modification beyond reading the filesystem to validate parsed file paths.
- Does not assume or modify global environment beyond setting LC_ALL in the subprocess environment when resolving owners.

## State:
Attributes and expected types, defaults, and constraints:
- cache_directory: str | None
    - Default: None.
    - Meaning: Path to a package cache directory expected by the underlying package manager. The property cache_exists returns True only when this attribute is a path to an existing directory.
    - Constraint: If None or points to a non-existing path, cache_exists will be False and find_owner will return None without invoking commands.

- list_command: Sequence[str] | None
    - Default: None.
    - Meaning: The command template (as a list/sequence of strings) used to list files for a package owner. When invoking, the code appends the owner identifier as the final argument: args = self.list_command + [owner].
    - Constraint: Must be an indexable/concatenable sequence (commonly a list) whose first element is the executable name. If left None or set to a non-sequence, method calls that build args will raise TypeError.

- list_regex: str
    - Default: '(.*)'
    - Meaning: Regular expression applied (with re.search) to each stripped line of stdout from the list command. The first capture group (match.groups()[0]) is interpreted as a filesystem path for an owned file.
    - Constraint: If the regex does not include at least one capture group but a match occurs, accessing the first capture group will raise IndexError. The regex should be designed to capture a path-like substring.

- owner_command: Sequence[str] | None
    - Default: None.
    - Meaning: The command template (sequence of strings) used to resolve which package owns a given filesystem path. The invoked args are self.owner_command + [path].
    - Constraint: Must be a sequence whose first element is the executable name. If None or malformed, TypeError or subprocess exceptions may occur. The commands_exist property checks existence of the first element on PATH.

- owner_regex: str
    - Default: '(.*)'
    - Meaning: Regular expression applied (with re.search) to the full stdout output from the owner command. The first capture group is returned (trimmed) as the owner identifier when a match is found.
    - Constraint: Must be a valid regex. If it lacks a capture group, finding a match will not yield the expected capture and IndexError may result when the code attempts to extract groups()[0].

Class invariants:
- For find_owner to proceed to invoke external commands, both cache_exists and commands_exist must be True. If either is False, find_owner returns None without spawning processes.
- list_command and owner_command, when set, must be sequences with a valid executable name at index 0; commands_exist depends on those first elements.

## Lifecycle:
Creation:
- Instantiate normally (no required constructor arguments). Because no __init__ sets attributes, callers must either:
    - Create a subclass that sets class attributes (cache_directory, list_command, owner_command, regexes), or
    - Instantiate PackageManager and assign the required attributes on the instance before use.
- Required preconditions before calling find_owner or find_dependencies:
    - cache_directory must point to an existing directory if the concrete package manager expects a cache (or callers accept that find_owner will return None when no cache).
    - list_command and owner_command must be sequences of strings and the referenced executables should be discoverable by find_executable (i.e., available in PATH or found by the project's launcher behavior).

Usage:
- Typical call order:
    1. Optionally inspect cache_exists and commands_exist to confirm readiness.
    2. Call find_dependencies(path) to obtain a list of existing, non-directory file paths owned by the package that contains path. This method internally calls find_owner(path) as its first step.
    3. Alternatively, call find_owner(path) directly to resolve the package owner string without listing files.
- No explicit teardown is required. The class does not open persistent resources or file descriptors that require closing.

Destruction / cleanup:
- No special destruction or cleanup methods (no close(), no context-manager semantics). Clients must not expect automatic resource cleanup beyond normal subprocess termination. Subprocesses are launched synchronously and waited on via communicate().

## Method Map:
flowchart LR
    A[Client] --> B[PackageManager.find_dependencies(path)]
    B --> C[PackageManager.find_owner(path)]
    C --> D{cache_exists? and commands_exist?}
    D -- False --> E[Return None to caller]
    D -- True --> F[Run subprocess: owner_command + [path] with env LC_ALL=C]
    F --> G[Decode stdout UTF-8 and apply owner_regex via re.search]
    G -- No match --> E
    G -- Match --> H[owner = first capture group (trimmed)]
    H --> I[Run subprocess: list_command + [owner]]
    I --> J[Decode stdout UTF-8, split lines and re.search(list_regex) per line]
    J --> K[For each match: take first capture group as dependency_path]
    K --> L[If os.path.exists(dependency_path) and not os.path.isdir(dependency_path) => append]
    L --> M[Return final list of dependency paths]

Notes:
- The diagram shows the predominant sequence used by find_dependencies. find_owner can also be called standalone (A -> C).

## Raises:
Exceptions that may be raised by methods (conditions that trigger them):

Common to both find_owner and find_dependencies:
- TypeError
    - Trigger: list_command or owner_command is None or not a sequence that supports concatenation with [arg], causing expressions like self.list_command + [owner] to raise TypeError.
- OSError / FileNotFoundError (subclasses of OSError)
    - Trigger: subprocess.Popen fails because the executable is not found or is not executable; although commands_exist attempts to detect executables, races or misconfiguration can still raise these errors.
- UnicodeDecodeError
    - Trigger: stdout bytes cannot be decoded with UTF-8 during decode('utf-8').
- IndexError
    - Trigger: A regex match is found but the configured regex contains no capture groups, so match.groups()[0] access fails.
- Any exception raised by subprocess, os.path, or re operations will propagate because methods do not catch them.

Method-specific behavior:
- find_owner:
    - Returns None immediately (no subprocess spawn) if cache_exists is False or commands_exist is False.
    - When invoked and owner_regex yields no match, returns None.
    - Side-effect: sets LC_ALL='C' in the subprocess environment to normalize output for regex parsing.

- find_dependencies:
    - If find_owner returns a falsy value (None or empty string), returns None without running the list command.
    - On success, returns a Python list (possibly empty) of existing, non-directory paths. Does not return duplicates only by code — duplicates are preserved if the list command outputs them multiple times.

## Example:
This example describes how to prepare and use PackageManager without actual source code snippets:

1. Prepare an instance or subclass:
   - Ensure cache_directory is set to a directory path expected by the package manager, or understand that find_owner will return None if that directory does not exist.
   - Set owner_command to a sequence of strings representing the owner lookup executable and its fixed arguments (e.g., ["pkg-owner-binary", "--format=x"]). The first element must be the executable name discoverable by PATH.
   - Set list_command to a sequence representing the list-files executable and fixed arguments (e.g., ["pkg-list-binary", "--list-format=x"]).
   - Set owner_regex and list_regex to regular expressions that capture the owner identifier and each listed file path respectively; both must include at least one capture group.

2. Typical invocation sequence:
   - Optionally check readiness: read the boolean properties cache_exists and commands_exist to decide whether find_owner/find_dependencies are likely to succeed.
   - Call find_dependencies(path) with a filesystem path. If it returns None, handle this as "owner could not be resolved"; if it returns a list, the list contains filesystem paths that exist and are not directories.
   - If only the package identity is needed, call find_owner(path) directly. If it returns None, owner could not be determined.

3. Validation and normalization:
   - Returned dependency paths are taken verbatim from the capture group; callers should normalize (e.g., os.path.abspath) if canonical paths are required.
   - Be prepared to handle propagated exceptions if the underlying commands fail or output unexpected bytes that cannot be decoded.

Implementation notes for reimplementers:
- The class intentionally avoids catching subprocess exceptions so callers can observe and handle low-level failures.
- The class sets LC_ALL='C' for owner lookups to reduce locale-induced parsing differences.
- The commands_exist property relies on a repository helper (find_executable) to locate executables; implementers should provide a similar mechanism that returns an executable path or None.

### `src.exodus_bundler.dependency_detection.PackageManager.find_dependencies` · *method*

## Summary:
Resolve the package owner for the given path, invoke the package manager's list command for that owner, and return a list of existing, non-directory filesystem paths extracted (via a regex) from the command's stdout. The method does not modify the PackageManager instance.

## Description:
This method performs two distinct steps:
1. Resolve the package owner identifier for the provided path by calling self.find_owner(path).
2. If an owner is found, run the package manager "list" command (self.list_command with the owner appended), parse stdout line-by-line using self.list_regex (applied with re.search), and collect the first capture group's value from each matching line when that value points to an existing, non-directory filesystem path.

Known callers and lifecycle:
- Intended to be invoked by higher-level bundling or packaging logic when collecting files owned by a package that contains the input path. There are no in-file callers shown in this excerpt.
- Typically used during dependency-collection or packaging steps.

Why it's a separate method:
- It encapsulates external command execution, text parsing, and filesystem filtering — concerns that are easier to test and maintain when separated from other logic. Owner resolution is delegated to find_owner to keep responsibilities modular.

Behavior summary / algorithm:
1. Call owner = self.find_owner(path). If owner is falsy (None or empty string), return None immediately and do not run any subprocess.
2. Construct args = self.list_command + [owner]. This requires self.list_command to be an iterable (commonly a list) of strings.
3. Spawn the subprocess with subprocess.Popen(args, stdout=subprocess.PIPE) and wait for completion via process.communicate(). Only stdout is captured; stderr is not captured by this call and will be inherited by the parent process (communicate() will return None for stderr in that case).
4. Decode stdout bytes using UTF-8. If decoding fails, UnicodeDecodeError will propagate.
5. Split the decoded stdout on '\n' and iterate each line. For each line:
   a. Strip leading/trailing whitespace from the line.
   b. Apply re.search(self.list_regex, line). If a match is found, take match.groups()[0] (the first capture group) as dependency_path.
   c. If os.path.exists(dependency_path) is True and os.path.isdir(dependency_path) is False, append dependency_path to the results.
6. Return the list of collected dependency paths (which may be empty). If owner resolution failed, return None.

## Args:
    path (str): Filesystem path used to locate its owning package. Must be acceptable to the underlying package manager owner command.

## Returns:
    list[str] | None:
        - list[str]: List of dependency path strings extracted from the list command stdout that exist on disk and are not directories.
        - [] (empty list): If the list command runs but yields no matching, existing non-directory paths.
        - None: If owner resolution failed (self.find_owner returned a falsy value such as None or an empty string). In this case the list command is not executed.

Notes on returned values:
- Returned paths are taken directly from the regex capture (match.groups()[0]) with no further normalization or resolution. Lines are stripped before matching, but the captured substring is used as-is. Callers should normalize paths if needed.
- The method uses re.search (not re.match), so the regex may match anywhere in the line.

## Raises:
    TypeError: If self.list_command is not an iterable that supports concatenation with [owner] (e.g., None or a non-sequence), the expression self.list_command + [owner] may raise TypeError.
    OSError (or subclasses): If spawning the subprocess fails (e.g., executable not found), subprocess.Popen may raise OSError which will propagate.
    UnicodeDecodeError: If stdout cannot be decoded as UTF-8, decoding will raise and propagate.
    IndexError: If a regex match is found but self.list_regex contains no capturing groups, accessing match.groups()[0] will raise IndexError.
    Any other exceptions raised by subprocess, os.path, or re operations will propagate because the method does not catch exceptions.

## State Changes:
    Attributes READ:
        - self.find_owner (method) — invoked to determine the owner identifier.
        - self.list_command (sequence) — read when building subprocess args.
        - self.list_regex (str) — used to parse lines of stdout.
    Attributes WRITTEN:
        - None. The method does not assign to or mutate any self.<attr> fields.

## Constraints:
    Preconditions:
        - self.find_owner must be callable and return a truthy owner identifier (non-empty string) for listing to proceed.
        - self.list_command must be an iterable/sequence of strings suitable for subprocess.Popen; the first element should normally be an executable name present in PATH.
        - self.list_regex should be a valid regular expression string containing at least one capture group if a successful match is expected to yield a dependency path.
        - The environment and system PATH should allow executing the list command; otherwise subprocess spawning will fail.
    Postconditions:
        - If the method returns a list, every element exists on disk (os.path.exists True) and is not a directory (os.path.isdir False).
        - If the method returns None, no subprocess was launched and the PackageManager state remains unchanged.

## Side Effects:
    - Launches and blocks on an external subprocess (the package manager list command); long-running commands will block the caller.
    - Reads and decodes subprocess stdout, and performs regex matching and filesystem checks.
    - stderr from the subprocess is not captured by this call and will be left to the parent process's standard error handling.
    - Does not modify environment variables, filesystem content, or the PackageManager instance attributes.

### `src.exodus_bundler.dependency_detection.PackageManager.find_owner` · *method*

## Summary:
Run the package-manager-specific "owner" command for a given file path and return the parsed owner string, or None when owner cannot be determined; no object state is modified.

## Description:
Known callers and context:
- PackageManager.find_dependencies calls this method as the first step in resolving which package "owns" a file path, during dependency detection. It is invoked at dependency-resolution time in the bundling pipeline when the system needs to map a filesystem path to the package that provides it.

Why this logic is a separate method:
- The owner lookup is isolated because it is a single, testable step that executes an external command and parses its output. Separating it makes the behavior easier to mock in tests, reusable by other code that needs an owner lookup, and keeps find_dependencies focused on translating an owner into a dependency list rather than on the details of invoking and parsing the owner command.

## Args:
    path (str): Filesystem path (absolute or relative) to the file whose owning package should be determined.
        - Expected to be a string suitable for passing to the underlying owner command.
        - The method does not require that the path exists locally (the owner command may accept non-existent paths), but callers generally pass existing file paths.

## Returns:
    str or None:
        - If the method successfully runs the owner command and the command output matches self.owner_regex, returns the first captured group from that match with surrounding whitespace stripped (i.e., match.groups()[0].strip()).
        - If either self.cache_exists is False or self.commands_exist is False, returns None immediately.
        - If the owner command runs but its output does not match self.owner_regex, returns None.

## Raises:
    - Any exception raised by subprocess.Popen (e.g., FileNotFoundError/OSError) or by process.communicate will propagate out of this method. In normal operation this is guarded by self.commands_exist, which checks executables exist.
    - UnicodeDecodeError may be raised when decoding the command stdout if the bytes cannot be decoded using UTF-8.
    - TypeError or ValueError may be raised if self.owner_command is not a sequence of strings suitable for passing to subprocess.Popen; callers or initializers must ensure owner_command is well-formed.

## State Changes:
    Attributes READ:
        - self.cache_exists (property): checked to ensure the package cache directory exists
        - self.commands_exist (property): checked to ensure required executables are available
        - self.owner_command (list-like): used to construct the subprocess argument list
        - self.owner_regex (str): regular expression used to parse the command output

    Attributes WRITTEN:
        - None. This method does not modify attributes on self.

## Constraints:
    Preconditions:
        - self.cache_directory should point to an existing directory if the cache is expected to be present (cache_exists must be True to proceed).
        - self.owner_command must be an iterable (typically a list) where the first element is the owner executable and remaining elements are arguments; commands_exist checks that the executables referenced exist on PATH.
        - self.owner_regex must be a valid regular expression string suitable for re.search.
        - Caller should expect that if cache_exists or commands_exist are False, the method will return None without invoking external commands.

    Postconditions:
        - After successful return of a non-None value, the returned string is the first capture group from the owner command output, with surrounding whitespace removed.
        - No attributes on self are mutated.
        - If a non-None value is returned, it reflects the owner as present in the owner command output under the current LC_ALL='C' environment.

## Side Effects:
    - Spawns a subprocess via subprocess.Popen with arguments self.owner_command + [path].
    - Sets LC_ALL='C' in the subprocess environment (the method copies os.environ and sets env['LC_ALL'] = 'C') to ensure locale-independent output for reliable regex parsing.
    - Performs no filesystem I/O itself beyond what the external owner command may do; it does not create, modify, or delete files.
    - No network calls are made by the method directly (but the external command invoked could perform network or other side effects).

### `src.exodus_bundler.dependency_detection.PackageManager.cache_exists` · *method*

## Summary:
Return whether the configured cache directory exists on the filesystem and is a directory; this read-only check does not modify object state.

## Description:
This property is used by dependency-detection logic to determine whether a local cache directory is available before attempting operations that rely on that cache. Known callers:
    - PackageManager.find_owner: queried early in the owner-discovery step to decide whether owner lookup should proceed.
    - Indirectly affects PackageManager.find_dependencies via find_owner.

This logic is implemented as a dedicated property to centralize the canonical check for a valid cache directory (existence + directory-ness), to make the intent explicit and testable, and to avoid repeating low-level os.path checks elsewhere.

## Args:
    None (accessed as a property on the instance).

## Returns:
    bool: True if and only if self.cache_directory refers to a filesystem entry that currently exists and is a directory. Returns False when the path does not exist or exists but is not a directory.

    Edge cases:
        - If self.cache_directory is a symlink to a directory, the property returns True (os.path.isdir follows symlinks).
        - If the path does not exist, returns False.

## Raises:
    TypeError: If self.cache_directory is None or otherwise not a valid path-like object (not str, bytes, or os.PathLike). This arises from passing a non-path-like value to os.path.exists/os.path.isdir.
    (No other exceptions are raised explicitly by this property; typical filesystem permission issues generally cause os.path.exists/os.path.isdir to return False rather than raise.)

## State Changes:
    Attributes READ:
        - self.cache_directory

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The caller should ensure that self.cache_directory is set to a valid path-like value (str, bytes, or os.PathLike). By default the class-level attribute is None; calling this property without assigning a path-like value will raise TypeError.
    Postconditions:
        - No mutation of self or external state occurs. The property returns a boolean reflecting the current filesystem state.

## Side Effects:
    - Performs filesystem metadata queries (os.stat via os.path.exists/os.path.isdir) which issue kernel calls but do not modify files or directories.
    - No network, subprocess, or external service calls are made.

### `src.exodus_bundler.dependency_detection.PackageManager.commands_exist` · *method*

## Summary:
Returns whether the external command binaries required by this PackageManager are available on the system; does not modify object state.

## Description:
This property checks that both the package list command and the package owner command (the first element of each configured command sequence) resolve to an executable path via the repository helper find_executable. Known callers:
- PackageManager.find_owner — used as a pre-check before attempting to run the owner command to determine the owner of a file.
- Indirectly invoked in the dependency detection pipeline: PackageManager.find_dependencies calls find_owner, which consults this property.

This check is implemented as a separate property to centralize and make explicit the availability check for external binaries (avoiding duplicated checks prior to every subprocess call) and to keep callers simple and declarative (they can ask "are commands available?" rather than duplicated try/except or path lookups).

## Args:
This is a zero-argument property (accessed as self.commands_exist). No external arguments.

## Returns:
bool
- True if find_executable returns a non-None path for each unique binary name taken from self.list_command[0] and self.owner_command[0].
- False if any of the required binaries cannot be resolved (find_executable returned None for at least one binary).
- Note: because the two command names are placed into a set, identical binaries configured in both commands are checked only once.

Edge cases:
- If the set of commands to check is empty (not possible when both list_command and owner_command supply a 0th element), all(...) would return True for an empty iterable — but in normal configuration this does not occur because the code indexes index 0 of each configured command.

## Raises:
This property does not explicitly raise exceptions, but the operation can propagate errors from invalid configuration or from find_executable:
- TypeError: if self.list_command or self.owner_command is None or not subscriptable, indexing (self.list_command[0]) will raise TypeError.
- IndexError: if either configured command sequence is an empty sequence (no index 0).
- Any exception raised by find_executable (if its implementation is changed to raise) will propagate.

## State Changes:
Attributes READ:
- self.list_command (reads index 0)
- self.owner_command (reads index 0)
Attributes WRITTEN:
- None — the property does not assign to any self.* attributes.

## Constraints:
Preconditions:
- self.list_command and self.owner_command must be sequences (or other subscriptable containers) with at least one element each (index 0 must be valid).
- The first elements (index 0) of those attributes must be strings representing executable binary names.

Postconditions:
- The method returns True or False as described; object attributes remain unchanged.

## Side Effects:
- Calls the global function find_executable(binary_name). The current find_executable implementation may read and, in the absence of an existing PATH, set os.environ['PATH'] to a default value. Therefore, accessing this property can mutate process environment variables in that specific edge case.
- No subprocesses are started by this property itself.

## `src.exodus_bundler.dependency_detection.Apt` · *class*

## Summary:
A concrete PackageManager adapter configured for Debian/Ubuntu systems that uses dpkg (dpkg -S) to map a filesystem path to its owning package and dpkg-query (dpkg-query -L) to list files provided by a package.

## Description:
Apt is a minimal concrete subclass of PackageManager that binds the PackageManager abstraction to the well-known Debian packaging tools. It exists to let the bundling/dependency-collection pipeline resolve which installed package owns a file and to enumerate the files installed by that package so they can be considered dependencies for bundling.

When to instantiate:
- Use Apt when the target system is Debian/Ubuntu (or otherwise uses dpkg/dpkg-query) and you need to perform owner lookups and package file listings.
- Typical callers are higher-level dependency-collection or bundling code that call find_owner(path) or find_dependencies(path) on a PackageManager instance.

Why this class exists:
- To provide a ready-to-use mapping of the PackageManager contract to dpkg/dpkg-query by supplying the correct command templates, cache path, and regexes required to parse dpkg output.
- Keeps dpkg-specific configuration centralized rather than sprinkling dpkg command strings and regexes through the codebase.

## State:
This subclass defines only class-level configuration values. Instances inherit behavior from PackageManager and use these values as defaults.

- cache_directory (str)
    - Value: '/var/cache/apt'
    - Meaning: Path to the system package cache used by Apt/dpkg. PackageManager uses this to decide whether owner lookups should be attempted (cached package metadata present). If this path does not exist, PackageManager.find_owner will return None without invoking external commands.
    - Constraint: Caller may override by setting instance attribute. If set to None or to a non-existent path, owner lookups will be skipped.

- list_command (list[str])
    - Value: ['dpkg-query', '-L']
    - Meaning: Template for the command used to list files belonging to a resolved package. PackageManager will append the package identifier as the final argument when invoking: args = self.list_command + [owner].
    - Constraint: Must be a sequence of strings. The first element identifies the executable (dpkg-query) which PackageManager expects to be discoverable by find_executable.

- list_regex (str)
    - Value: '(.+)'
    - Meaning: Regular expression applied with re.search to each line of stdout from the list_command. The first capture group is interpreted as a filesystem path for an owned file.
    - Constraint: Must contain at least one capture group that yields the file path. A match without capture groups will cause IndexError when the code accesses the first capture.

- owner_command (list[str])
    - Value: ['dpkg', '-S']
    - Meaning: Template for the command used to find the owning package for a given filesystem path. PackageManager will append the target path as the final argument: args = self.owner_command + [path].
    - Constraint: Must be a sequence of strings. The first element (dpkg) must be discoverable by the environment (find_executable). If not discoverable, commands_exist will be False and lookups will be skipped.

- owner_regex (str)
    - Value: '(.+): '
    - Meaning: Regular expression applied (via re.search) to the full stdout of the owner_command; the first capture group is taken as the package identifier (text before the colon in dpkg -S output).
    - Constraint: Must contain at least one capture group that captures the package name. Unexpected dpkg output or a regex without capture groups will lead to an IndexError when extracting groups()[0].

Class invariants (that must hold during use):
- list_command and owner_command are sequences whose first element is the executable name that must be discoverable via the same mechanism PackageManager uses (typically find_executable).
- owner_regex and list_regex must include at least one capture group each to yield the expected package name and file path values.
- If cache_directory does not exist, PackageManager.find_owner will not spawn subprocesses and will return None.

## Lifecycle:
Creation:
- Instantiate directly with no constructor arguments: apt = Apt()
- The class-level attributes above are present on the instance by inheritance; callers may override them on the instance if needed:
    - apt.cache_directory = '/custom/cache'  # optional override
- No factory or special parameters are required.

Usage:
- Readiness checks:
    - Optionally inspect apt.cache_exists and apt.commands_exist (properties provided by PackageManager) before attempting lookups. On Apt these depend on '/var/cache/apt' existing and the executables 'dpkg' and 'dpkg-query' being discoverable.
- Typical sequence:
    1. owner = apt.find_owner(path)
        - Returns: package identifier string (trimmed) on success, or None if owner could not be determined or prerequisites (cache_exists/commands_exist) are not met.
    2. dependencies = apt.find_dependencies(path)
        - Behavior: calls find_owner internally; if owner found, executes list_command + [owner], parses each output line with list_regex, yields a list of file paths that exist on disk and are not directories (duplicates preserved).
- Order dependencies: find_owner is the first step inside find_dependencies; callers may call find_owner directly if they only need the package identifier.

Destruction:
- None. The class does not open persistent resources. Subprocesses are synchronous and are terminated after their outputs are read. There is no close() or context-manager support required.

## Method Map:
flowchart LR
    Client --> Apt.find_dependencies
    Apt.find_dependencies --> Apt.find_owner
    Apt.find_owner --> Check[check: cache_exists? && commands_exist?]
    Check -- False --> ReturnNone[Return None (no subprocesses)]
    Check -- True --> RunOwnerCmd[run: owner_command + [path] with env LC_ALL='C']
    RunOwnerCmd --> ParseOwner[decode stdout -> re.search(owner_regex)]
    ParseOwner -- NoMatch --> ReturnNone
    ParseOwner -- Match --> OwnerFound[owner = first capture group (trimmed)]
    OwnerFound --> RunListCmd[run: list_command + [owner]]
    RunListCmd --> ParseList[decode stdout -> splitlines -> per-line re.search(list_regex)]
    ParseList --> ForEach[for each match: candidate = first capture group]
    ForEach --> FilterExist[if os.path.exists(candidate) and not os.path.isdir(candidate) -> append to results]
    FilterExist --> ReturnList[return final list of dependency file paths]

Notes:
- find_owner can be invoked standalone (Client -> Apt.find_owner).
- All subprocess invocations are expected to be synchronous and use UTF-8 decoding of stdout.

## Raises:
Apt defines no custom __init__ or methods; it relies on the PackageManager implementation. The following exceptions are possible when calling inherited methods (conditions below indicate when they may occur on Apt):

- __init__:
    - No exceptions; Apt inherits the default object initializer and defines no explicit constructor.

- TypeError
    - Trigger: If list_command or owner_command are None or not sequences, expressions like self.list_command + [owner] will raise TypeError during argument construction.

- FileNotFoundError / OSError
    - Trigger: Subprocess creation fails because the executable (dpkg or dpkg-query) is not present or not executable. Even though PackageManager may check for executables prior to invocation, races or PATH misconfiguration can still cause these exceptions.

- UnicodeDecodeError
    - Trigger: When subprocess stdout cannot be decoded using UTF-8 (e.g., unexpected byte sequences) while reading owner/list command output.

- IndexError
    - Trigger: A regex match is found but the configured regex lacks capture groups (or the expected group is missing); accessing match.groups()[0] will raise IndexError.

- Any exception raised by os.path operations, subprocess, or re will propagate to the caller (PackageManager intentionally does not swallow low-level exceptions).

## Example:
- Instantiate Apt:
    apt = Apt()

- Quick readiness check:
    if not apt.cache_exists or not apt.commands_exist:
        # owner lookups or listing might return None or fail
        pass

- Resolve owner and list dependencies for a path:
    owner = apt.find_owner('/usr/bin/somebinary')  # returns package name (e.g., 'packagename') or None
    if owner:
        deps = apt.find_dependencies('/usr/bin/somebinary')  # returns list of existing file paths (may be empty)
    else:
        # handle unresolved owner

- No cleanup is needed after use.

Implementation note for reimplementers:
- Recreate Apt as a trivial subclass that sets the class attributes exactly as shown:
    - cache_directory = '/var/cache/apt'
    - list_command = ['dpkg-query', '-L']
    - list_regex = '(.+)'
    - owner_command = ['dpkg', '-S']
    - owner_regex = '(.+): '
- Ensure the PackageManager base class implements cache_exists, commands_exist, find_owner(path) and find_dependencies(path) consistent with the expectations described above.
- The discovery of the actual executable paths uses the project's find_executable helper; the PackageManager implementation should call this helper (or equivalent) to set commands_exist correctly before invoking subprocesses.

## `src.exodus_bundler.dependency_detection.Pacman` · *class*

## Summary:
Concrete PackageManager adapter configured for Arch Linux's pacman tool; it supplies pacman-specific command templates, cache directory, and regular expressions so the base PackageManager logic can resolve file ownership and enumerate package-provided files.

## Description:
Pacman is a minimal concrete subclass intended to be used wherever the system needs to map a filesystem path to the pacman package that owns it and then enumerate files provided by that package. The class itself does not implement new methods; it provides the pacman-specific configuration that the PackageManager base class expects:

- cache_directory: points at pacman's on-disk package cache (/var/cache/pacman).
- owner_command/list_command: command templates used to resolve an owner package for a file and to list files installed by a package, respectively.
- owner_regex/list_regex: regular expressions tuned to parse pacman output.

Scenarios for instantiation:
- Instantiate Pacman (no constructor args) and use inherited methods find_owner(path) and find_dependencies(path) from PackageManager.
- Use as the concrete backend when bundling software on systems that use pacman (Arch/Manjaro), so file ownership and package file lists can be discovered.

Motivation / responsibility boundary:
- Pacman exists solely to supply pacman-specific command templates and regexes. It relies on PackageManager for subprocess invocation, parsing, filtering, readiness checks (cache_exists, commands_exist), and result normalization. Pacman is not responsible for executing commands itself, handling retries, or caching results beyond the static cache_directory path it advertises.

Reference:
- See the PackageManager documentation for method semantics, subprocess behavior, and environment normalization assumptions required by callers.

## State:
Attributes (class-level defaults shown) and constraints. All attributes are intended to be readable from instances as well as from the class.

- cache_directory: str
    - Default (in this class): '/var/cache/pacman'
    - Meaning: Filesystem path where pacman stores package cache. PackageManager.cache_exists uses this to decide whether owner resolution should proceed.
    - Constraint: Should be an absolute path to an existing directory for cache_exists to return True. If the path does not exist, find_owner will return None without spawning subprocesses (per PackageManager semantics).

- list_command: list[str]
    - Default: ['pacman', '-Ql']
    - Meaning: Base command (as a list of argv parts) used to list all files belonging to a package. PackageManager will append the package owner identifier as the final argument when invoking.
    - Constraint: Must be a sequence of strings. The first element must be the executable name discoverable by PATH or by the repository's find_executable helper. If this is not a sequence or is malformed, concatenation in the base class will raise TypeError.

- list_regex: str (regular expression)
    - Default: r'.*\s+(\/.+)'
    - Meaning: Regex applied (via re.search) to each stripped line of stdout from pacman -Ql. The first capture group is interpreted as the installed file path (e.g., captures "/usr/bin/foo" from a line like "package /usr/bin/foo").
    - Constraint: Must include at least one capture group; the first capture group should produce a path-like string beginning with '/'. Matched strings should be passed through os.path.exists and os.path.isdir filtering by the base class.

- owner_command: list[str]
    - Default: ['pacman', '-Qo']
    - Meaning: Command template used to resolve which package owns a given filesystem path. PackageManager will append the queried path as the final argument when invoking.
    - Constraint: Same constraints as list_command regarding sequence shape and executable discovery.

- owner_regex: str (regular expression)
    - Default: r' is owned by (.*)\s+.*'
    - Meaning: Regex applied (via re.search) to the full stdout output returned by pacman -Qo /path. The first capture group is interpreted as the package identifier/name (e.g., captures "foo-package-1.2-3" from "path/to/file is owned by foo-package-1.2-3").
    - Constraint: Must include at least one capture group. The captured owner string is trimmed (whitespace removed) before use.

Class invariants:
- The base class behavior requires that owner_command and list_command are sequences whose first element is a valid executable name; commands_exist is expected to check for that executable via find_executable.
- For successful owner resolution, cache_directory must exist and commands_exist must be True. Otherwise, find_owner returns None as per PackageManager semantics.

## Lifecycle:
Creation:
- Instantiation: No constructor arguments are required for Pacman — default class attributes are already suitable. Example instantiation path is simply creating an instance of Pacman or using Pacman as a class attribute provider for PackageManager logic.
- No factory is required, but callers should verify readiness via the base-class properties:
    - Check cache_exists (True only if cache_directory exists on disk).
    - Check commands_exist (True only if the pacman executable can be located via find_executable).

Usage (typical sequence):
1. readiness checks (optional):
   - Inspect cache_exists and commands_exist on the Pacman instance.
2. owner resolution:
   - Call the inherited find_owner(path) to get the package owner identifier (string) or None.
   - The base class will set LC_ALL='C' when running the owner_command subprocess to normalize output for owner_regex.
3. dependency listing:
   - Call the inherited find_dependencies(path). This calls find_owner(path) internally; if ownership is resolved, it runs the list_command with the owner identifier appended, parses lines with list_regex, filters out non-existent paths and directories, and returns a list of file paths.
4. error propagation:
   - If underlying commands fail or output cannot be parsed/decoded, subprocess or parsing exceptions propagate to the caller.

Destruction / cleanup:
- Pacman does not maintain persistent resources. All subprocesses invoked by PackageManager are started synchronously and waited upon; no explicit cleanup or close() is required.

## Method Map:
The Pacman class itself supplies configuration only; the following Mermaid flowchart shows how callers interact with Pacman through PackageManager's methods and how those methods call into pacman.

flowchart LR
    Client[Client code] --> Call_find_dependencies[Pacman (PackageManager.find_dependencies(path))]
    Call_find_dependencies --> Call_find_owner[PackageManager.find_owner(path)]
    Call_find_owner --> Check_cache_commands{cache_exists AND commands_exist?}
    Check_cache_commands -- False --> Owner_None[Return None]
    Check_cache_commands -- True --> Owner_subproc[Run owner_command + [path] with env LC_ALL='C']
    Owner_subproc --> Owner_parse[Decode stdout (utf-8) and apply owner_regex (re.search)]
    Owner_parse -- NoMatch --> Owner_None
    Owner_parse -- Match --> Owner_ident[owner = first capture group (trimmed)]
    Owner_ident --> List_subproc[Run list_command + [owner]]
    List_subproc --> List_parse[Decode stdout, split lines, apply list_regex per line]
    List_parse --> Filter_paths[For each match: path = first capture group; keep if os.path.exists(path) and not os.path.isdir(path)]
    Filter_paths --> Return_list[Return list of dependency paths to caller]

Notes:
- find_owner may be invoked standalone: Client --> PackageManager.find_owner(path) and follow the same branches up to Owner_ident.

## Raises:
Pacman itself defines no new exceptions, but callers using the inherited PackageManager methods with Pacman's configuration may encounter the following exceptions and conditions:

- None (from __init__):
    - Pacman uses the default class attributes and does not define an __init__; instantiating Pacman will not raise by itself.

- TypeError
    - Trigger: If list_command or owner_command are not a concat-able sequence (e.g., set to None or a non-sequence), expressions like self.list_command + [arg] in the base class will raise TypeError.

- OSError / FileNotFoundError
    - Trigger: subprocess invocation (Popen) fails because the executable (pacman) cannot be executed or is not found despite commands_exist checks (race conditions or PATH changes can cause this).

- UnicodeDecodeError
    - Trigger: stdout bytes from pacman cannot be decoded with UTF-8 when the base class decodes subprocess output.

- IndexError
    - Trigger: owner_regex or list_regex matches but does not include capture groups; attempting to access the first capture group (match.groups()[0]) will raise IndexError.

- re.error
    - Trigger: If owner_regex or list_regex are set to invalid regular expressions, re.search/re.compile may raise re.error.

These exceptions originate in the base class implementation (subprocess, re, os operations) and are intentionally allowed to propagate so callers can handle them.

## Example:
This prose example shows how Pacman is typically used (no source code):

1. Prepare and check readiness:
   - Create a Pacman instance.
   - Confirm that '/var/cache/pacman' exists on the running system if you expect owner resolution to run (otherwise find_owner will return None).
   - Confirm that the pacman binary is discoverable on PATH (commands_exist True via the repository's find_executable behavior).

2. Resolve a file's owner:
   - Call find_owner('/usr/bin/somebinary') on the Pacman instance. If pacman -Qo outputs a line like "/usr/bin/somebinary is owned by somepkg-1.2-3", owner_regex (r' is owned by (.*)\s+.*') will capture "somepkg-1.2-3" and return that string. If the cache directory does not exist or pacman isn't found, find_owner returns None.

3. List files for that package:
   - Call find_dependencies('/usr/bin/somebinary'). The resolved owner identifier is appended to ['pacman', '-Ql'] and executed. Pacman's -Ql output typically contains lines like "somepkg /usr/bin/somebinary"; the list_regex (r'.*\s+(\/.+)') matches and captures "/usr/bin/somebinary". The base class filters out entries that do not exist on disk or that are directories, and returns a list of file paths.

4. Error handling:
   - Be prepared to catch OSError if pacman is missing at runtime, UnicodeDecodeError if unexpected encodings are encountered, and IndexError if regex configuration is changed incorrectly.

Implementation notes for reimplementers:
- Provide the same attribute defaults (cache_directory, commands, regexes) exactly as above to match pacman output expectations.
- Ensure that the readiness checks (cache_exists and commands_exist) behave as described in the PackageManager documentation and that owner subprocesses are run with LC_ALL='C' to normalize localized output.
- Use the project's find_executable behavior (or equivalent) to determine whether the pacman executable is available on PATH before invoking subprocesses.

## `src.exodus_bundler.dependency_detection.Yum` · *class*

## Summary:
Represents a concrete PackageManager adapter for RPM-based systems (yum/rpm). Provides the command templates and regular expressions used by the base PackageManager to resolve which package owns a filesystem path and to list files provided by that package.

## Description:
Yum is a lightweight concrete subclass of PackageManager that configures the RPM tooling used to perform owner and file-list lookups. It exists solely to supply the base class with the correct command templates, cache directory path, and simple regexes appropriate for rpm output; it does not implement additional behavior of its own. Instantiate this class when the host system uses RPM/YUM and you want the bundler/dependency-collector logic to enumerate files owned by RPM packages.

Typical callers:
- Higher-level dependency collection or bundling code that calls the base class methods find_owner(path) or find_dependencies(path). Because Yum sets class attributes rather than an __init__ contract, callers simply instantiate Yum() (or use it as a class directly if the base API supports class-level access) and call the inherited methods.

Motivation and responsibilities:
- Encapsulates the concrete command-lines for rpm-based owner and list queries:
    - Owner lookup: uses rpm -qf <path>
    - List files for a package: uses rpm -ql <package>
- Leaves parsing, subprocess invocation, filtering, and error propagation to PackageManager. Yum's responsibility is configuration only — providing correct commands, the RPM cache directory, and simple regexes that capture the full path text from command output.

## State:
Attributes provided by Yum (class-level defaults; instances inherit these unless overridden):

- cache_directory (str)
    - Value: '/var/cache/yum'
    - Meaning: Filesystem path to the yum cache directory. The base PackageManager checks for the existence of this path before attempting owner resolution; if it does not exist, find_owner returns None and no subprocess is executed.
    - Constraint: Must be a path string. If the directory does not exist on the host, owner resolution will be skipped.

- list_command (Sequence[str])
    - Value: ['rpm', '-ql']
    - Meaning: Template command used to list files for a resolved owner/package. PackageManager will append the package identifier as the final argument (forming ['rpm','-ql', <owner>]).
    - Constraint: First element ('rpm') is the executable name that must be discoverable by the system (via find_executable). If the sequence is replaced with a non-sequence, callers will see TypeError when the base class attempts concatenation.

- list_regex (str)
    - Value: r'(.+)'
    - Meaning: Regular expression applied to each line of stdout from the list command. The first capture group is interpreted as the path string for a listed file.
    - Constraint: Must include at least one capture group. The provided regex captures the entire non-empty line.

- owner_command (Sequence[str])
    - Value: ['rpm', '-qf']
    - Meaning: Template command used to find which package owns a given filesystem path. PackageManager will append the file path to this sequence when invoking the subprocess.
    - Constraint: First element ('rpm') must be discoverable on PATH. Malformed or non-sequence values will cause TypeError or subprocess errors.

- owner_regex (str)
    - Value: r'(.+)'
    - Meaning: Regular expression applied to the stdout from the owner command. The first capture group is used as the package identifier (owner).
    - Constraint: Must contain at least one capture group. The provided regex captures any non-empty stdout line.

Class invariants (inherited from PackageManager and enforced when using Yum):
- Before spawning subprocesses for owner resolution, PackageManager requires both:
    - cache_directory exists on the filesystem (cache_exists True), and
    - the command executables referenced by owner_command and list_command are discoverable (commands_exist True).
  If either condition fails, find_owner returns None without invoking commands.
- owner_regex and list_regex must include at least one capture group; otherwise the base class's extraction of groups()[0] will raise IndexError when a match is found.

## Lifecycle:
Creation:
- Instantiate normally: Yum() (no constructor arguments required).
- No special factory is required because Yum supplies class-level configuration. If system-specific overrides are necessary (different cache path or regex), set instance attributes after construction or subclass Yum.

Usage:
- Recommended sequence:
    1. Optionally check readiness:
       - Verify os.path.exists(Yum.cache_directory) or inspect the inherited cache_exists property.
       - Verify the rpm executable is available (commands_exist property via the base class).
    2. Call find_owner(path) to resolve which RPM package owns a given file path. If it returns None, the owner could not be resolved (missing cache directory, missing rpm executable, or no regex match).
    3. If an owner identifier is returned, call find_dependencies(path) to obtain the list of files provided by that package. The base class will invoke rpm -ql <owner>, apply list_regex to each line, and return existing, non-directory paths.
- Method sequencing: find_dependencies internally calls find_owner first; callers may call find_owner directly if they only need the package identity.

Destruction / cleanup:
- No explicit teardown or context-manager behavior is required. The class does not hold persistent handles; subprocesses are run synchronously and terminated before return. Callers are responsible for any higher-level resource management.

## Method Map:
flowchart LR
    Client --> find_dependencies[PackageManager.find_dependencies(path)]
    find_dependencies --> find_owner[PackageManager.find_owner(path)]
    find_owner --> check_cache_and_cmds{cache_exists AND commands_exist?}
    check_cache_and_cmds -- False --> owner_none[Return None (no subprocess)]
    check_cache_and_cmds -- True --> run_owner["Run subprocess: ['rpm','-qf', path] (env LC_ALL='C')"]
    run_owner --> decode_owner[Decode stdout as UTF-8]
    decode_owner --> apply_owner_regex[re.search(owner_regex) -> capture group 0]
    apply_owner_regex -- No match --> owner_none
    apply_owner_regex -- Match --> owner_id[owner identifier]
    owner_id --> run_list["Run subprocess: ['rpm','-ql', owner_id]"]
    run_list --> decode_list[Decode stdout UTF-8 and split lines]
    decode_list --> apply_list_regex[Apply list_regex to each line -> capture group 0 per match]
    apply_list_regex --> validate_paths[Filter: os.path.exists && not os.path.isdir]
    validate_paths --> return_list[Return list of dependency file paths]

Notes:
- For Yum, owner_command is ['rpm','-qf'] and list_command is ['rpm','-ql']. Both regexes capture the entire non-empty output line.

## Raises:
Yum itself defines no new exceptions; exceptions originate from the inherited PackageManager behavior and underlying system calls. Important cases:

- __init__:
    - Raises: None (inherits default; no initialization-time checks).

- find_owner / find_dependencies (inherited behavior when using Yum):
    - TypeError:
        - Trigger: If list_command or owner_command are not sequences or cannot be concatenated with [arg], concatenation in the base methods will raise TypeError.
    - OSError / FileNotFoundError:
        - Trigger: subprocess invocation fails because the rpm executable is missing or not executable (race conditions or PATH issues despite commands_exist checks).
    - UnicodeDecodeError:
        - Trigger: stdout bytes cannot be decoded with UTF-8.
    - IndexError:
        - Trigger: If an owner_regex or list_regex matches but contains no capture groups, accessing groups()[0] will raise IndexError.
    - Any other exceptions raised by os.path, re, or subprocess will propagate to the caller (the base class intentionally avoids swallowing these errors).

## Example:
- Setup and readiness:
  - Instantiate: create a Yum instance (no constructor args).
  - Confirm readiness: ensure the host has /var/cache/yum present and that the 'rpm' executable is available on PATH (commands_exist will use the repository's find_executable helper to determine availability).
- Typical call flow (prose):
  1. Call find_dependencies("/usr/bin/some-binary"):
     - PackageManager calls find_owner first (runs rpm -qf /usr/bin/some-binary with LC_ALL='C').
     - If owner is resolved to e.g. "mypackage-1.2.3", PackageManager runs rpm -ql mypackage-1.2.3.
     - Each stdout line is matched with r'(.+)' to capture paths; captured paths that exist on disk and are not directories are returned as a Python list.
  2. If find_owner returns None (e.g., cache missing or rpm not found), find_dependencies returns None and callers should treat this as "owner could not be determined".
- Cleanup: no explicit cleanup required; handle exceptions from subprocess or decoding as needed.

Implementation notes for reimplementers:
- Yum supplies concrete values for the fields the base PackageManager expects; any reimplementation must ensure:
  - Owner and list commands are invoked with LC_ALL='C' for owner resolution (per base class behavior).
  - Regexes include capture groups and are applied as re.search on decoded UTF-8 stdout.
  - The cache_directory is checked for existence before running owner resolution.
  - Executable discovery is performed (via a helper like find_executable) before spawning subprocesses to avoid predictable failures when possible.

## `src.exodus_bundler.dependency_detection.detect_dependencies` · *function*

## Summary:
Delegates dependency detection to each configured package manager detector in order and returns the first detector result that evaluates to true; returns None if no detector reports dependencies.

## Description:
This function centralizes orchestration of multiple package-manager-specific detectors. It iterates over a module-level iterable named package_managers and calls each detector's find_dependencies(path). The first detector that returns a truthy value has its return value forwarded directly to the caller; otherwise the function returns None.

Known callers:
    - No direct callers were discovered in the provided code snapshot. Typical callers are higher-level packaging, bundling, or analysis routines that need to discover a project's declared dependencies before further processing (e.g., building a bundle, creating a lockfile, or generating a dependency manifest).

Why this logic is extracted:
    - The function enforces a single, consistent orchestration point (ordering and short-circuiting) so individual detector implementations remain focused on determining dependencies for a specific packaging system. It avoids duplicating the iteration/short-circuit pattern and centralizes how the system chooses the first applicable detector.

## Args:
    path (any):
        A path-like value that will be passed unchanged to each detector's find_dependencies method.
        - The implementation does not validate type or existence; detectors define what they accept. In most codebases this is usually a string or os.PathLike pointing at a project root or a manifest file.
        - Do not assume callers will coerce this value; if detectors require a specific type, callers should prepare it.

    Interdependencies:
        - The function relies on a module-level iterable named package_managers. Each element must implement a callable method find_dependencies(path).
        - The semantics of path and the shape of the returned dependency information are defined by detector implementations and must be handled by callers.

## Returns:
    The function returns exactly one of:
    - The first truthy value returned by a detector's find_dependencies(path). The raw object returned by the detector is forwarded unchanged. Typical shapes include:
        * A sequence (list/tuple) of dependency identifiers
        * A mapping (dict) describing dependencies and metadata
        * A custom object representing parsed dependency information
    - None if every detector returned a falsy value (e.g., [], {}, None, False, or an empty custom container).

    Important semantics:
        - "Truthiness" is used to determine whether a detector "found" dependencies. The function does not attempt to normalize, validate, or merge results from multiple detectors; it returns the first detector result that evaluates to true in a boolean context.

## Raises:
    The function body itself contains no try/except handlers, so several errors may propagate to the caller:

    - NameError:
        * If package_managers is not defined at module scope, attempting to iterate it will raise NameError.
    - TypeError:
        * If package_managers is not iterable, attempting the for-loop will raise TypeError.
        * If a detector's find_dependencies is not callable, calling it will raise TypeError.
    - AttributeError:
        * If a detector object lacks a find_dependencies attribute, attempting to access it may raise AttributeError.
    - Any exception raised by a detector's find_dependencies(path):
        * Detector implementations may perform I/O, subprocess calls, parsing, or other operations that raise exceptions (OSError/FileNotFoundError, subprocess.CalledProcessError, ValueError, custom parsing exceptions, etc.). These exceptions are not caught and will propagate.

## Constraints:
    Preconditions:
        - package_managers must be defined and iterable at module load time.
        - Each element of package_managers must provide a callable find_dependencies(path).
        - Callers should pass a path value acceptable to the installed detectors (commonly a filesystem path to a project root).

    Postconditions:
        - If a non-None value is returned, it is the first truthy return value produced by a detector in the package_managers order.
        - If None is returned, every detector returned a falsy value.
        - The function does not modify module-level state, nor does it aggregate detector outputs.

## Side Effects:
    - The function itself does not perform I/O or external calls beyond invoking detector methods.
    - Any side effects (reading files, spawning subprocesses, network access, logging, caching) occur inside detector implementations and are visible to callers.
    - Because detectors are called in order and short-circuiting occurs on the first truthy result, later detectors are not invoked once a detector returns truthily — this can affect performance and side-effect ordering.

## Control Flow:
flowchart TD
    Start --> CheckPackageManagersDefined{Is package_managers defined and iterable?}
    CheckPackageManagersDefined -- No --> RaiseError[NameError or TypeError]
    CheckPackageManagersDefined -- Yes --> ForEach[For each package_manager in package_managers]
    ForEach --> GetMethod[Resolve package_manager.find_dependencies]
    GetMethod --> Call[Call find_dependencies(path)]
    Call --> ResultCheck{Is result truthy?}
    ResultCheck -- Yes --> ReturnResult[Return that result immediately]
    ResultCheck -- No --> Next[Continue to next package_manager]
    Next --> ForEach
    ForEach --> NoDetectorsLeft[Finished all detectors]
    NoDetectorsLeft --> ReturnNone[Return None]

## Examples:
    # Basic usage — caller expects possibly different detector return shapes
    result = detect_dependencies(project_path)
    if result is None:
        # No detector recognized dependencies for this path
        handle_no_deps()
    else:
        # If your code expects a list, normalize the detector output here
        deps_list = normalize_detector_output(result)
        process_dependencies(deps_list)

    # Defensive call pattern handling detector exceptions and missing module state
    try:
        deps = detect_dependencies(project_path)
    except NameError:
        # package_managers was not configured — treat as no detectors available
        handle_configuration_error()
    except (TypeError, AttributeError) as exc:
        # Some detector is malformed or package_managers is not iterable
        handle_detector_misconfiguration(exc)
    except Exception as exc:
        # Any detector-specific runtime error (I/O, parsing, subprocess)
        handle_detection_failure(exc)

