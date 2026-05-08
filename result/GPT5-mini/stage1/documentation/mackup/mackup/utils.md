# `utils.py`

## `mackup.utils.confirm` · *function*

## Summary:
Prompts the user (via console) to answer a Yes/No question and returns True for affirmative answers and False for negative answers; if a module-level FORCE_YES flag is truthy, the function returns True immediately without prompting.

## Description:
This small utility centralizes interactive confirmation logic for command-line workflows that must obtain explicit user approval before taking actions (for example, deleting backups or performing destructive operations).

Known callers within the provided context:
- None discovered in the supplied snippet. The function is intended to be called by higher-level CLI operations in the project; search the repository for confirm(...) to find concrete callers.

Why this logic is extracted:
- Ensures a consistent prompt format and accepted responses across the codebase.
- Encapsulates input normalization and validation so callers do not reimplement prompting behavior.
- Simplifies testing and automation by allowing a single place to short-circuit prompting (via FORCE_YES) or to monkeypatch the input function.

Implementation note:
- The function uses six.moves.input (imported at file level) to read user input. That function is the one actually called and thus is the target to patch in tests/mocks.

## Args:
    question (str): The prompt text describing the action to confirm. The implementation performs direct string concatenation: question + " <Yes|No> ".
        - Required: must be convertible to str for concatenation; otherwise a TypeError will be raised.
        - The function does not strip or trim the user's response before matching; whitespace on either side of the entered text will prevent a match.

## Returns:
    bool: 
        - True if an affirmative response is received ("yes" or "y", case-insensitive).
        - False if a negative response is received ("no" or "n", case-insensitive).
        - If the module-level name FORCE_YES is truthy at call time, the function immediately returns True without performing any I/O.
    - The function loops until one of the accepted answers is entered; there are no other possible return values.

## Raises:
    NameError: If FORCE_YES is not defined in the module namespace when the function is executed (the global name is evaluated before any prompting).
    TypeError: If concatenation of question with the literal " <Yes|No> " is invalid (e.g., question is an object that cannot be concatenated with a str).
    EOFError: Propagated when the underlying input function encounters EOF on stdin.
    KeyboardInterrupt: Propagated if the user interrupts input (Ctrl-C).
    Any other exception raised by six.moves.input or by str.lower() will propagate to the caller.

## Constraints:
Preconditions:
    - The caller should ensure a human-readable question string is provided.
    - The module-level variable FORCE_YES is expected to exist (boolean-like) if the caller relies on that behavior; otherwise be prepared to handle NameError.

Postconditions:
    - The function returns either True or False.
    - No global state, files, network resources, or persistent storage are modified by this function (it only reads the FORCE_YES flag and performs console I/O).

## Side Effects:
    - Synchronous console I/O via six.moves.input: the prompt (question + " <Yes|No> ") is written to stdout (or the environment's prompt hook) and input is read from stdin.
    - When FORCE_YES is truthy, no I/O occurs.
    - No other external side effects (no filesystem/network/database mutations).

## Control Flow:
flowchart TD
    Start --> Check_FORCE_YES
    Check_FORCE_YES{FORCE_YES truthy?}
    Check_FORCE_YES -- Yes --> ReturnTrue[Return True]
    Check_FORCE_YES -- No --> Prompt[Call six.moves.input(question + " <Yes|No> ")]
    Prompt --> Normalize[answer = input(...).lower()]
    Normalize --> IsYes{answer == "yes" or answer == "y"?}
    IsYes -- Yes --> ReturnTrue
    IsYes -- No --> IsNo{answer == "no" or answer == "n"?}
    IsNo -- Yes --> ReturnFalse[Return False]
    IsNo -- No --> Prompt
    ReturnTrue --> End
    ReturnFalse --> End
    End((End))

## Examples and usage guidance:
- Interactive behavior (illustrative, line-oriented):
    - Call: confirm("Delete all backups?")
    - Prompt shown: Delete all backups? <Yes|No> 
    - If user types "yes" or "y" (any case): function returns True.
    - If user types "no" or "n" (any case): function returns False.
    - If user types " y " (with surrounding spaces) or "Yes!" (extra characters), the input is not accepted because the function only lowercases the input but does not strip whitespace or perform fuzzy matching; the function will re-prompt until an exact accepted token is entered.

- Automation / testing:
    - To avoid interactive prompts in automated scripts or CI, set the module-level FORCE_YES variable to a truthy value; the function will return True without calling input.
    - For unit tests, monkeypatch six.moves.input (the imported input) to return predetermined responses and verify confirm's behavior; patching the six.moves.input name used in this module is the correct target.

- Error handling guidance:
    - If the caller wants to treat EOFError or KeyboardInterrupt as a negative answer, wrap the call in try/except and handle these exceptions accordingly:
        try:
            ok = confirm("Proceed with destructive operation?")
        except (EOFError, KeyboardInterrupt):
            ok = False  # treat interruption as rejection

This documentation describes the exact behavior you must implement to match the original function: the FORCE_YES short-circuit, prompt format, accepted tokens, lack of trimming, and exceptions that propagate.

## `mackup.utils.delete` · *function*

## Summary:
Remove a filesystem entry at the given path after attempting to clear ACLs and immutable attributes so deletion succeeds where platform protections might otherwise block it.

## Description:
This helper performs a best-effort, platform-aware cleanup and then deletes the target path. It first invokes two platform-specific helpers to clear access-control lists and immutable attributes, then removes the target according to its type:
- If the path is a regular file or a symbolic link, the function removes the file/link.
- If the path is a directory, the function removes the directory and its entire tree recursively.

Known callers within the available repository snapshot:
- No direct call sites for delete were discovered in the scanned snapshot. The function is intended for use in cleanup/teardown, restore, or uninstall flows where filesystem entries must be removed and OS-level protections might block deletion.

Relationship to module helpers:
- delete(filepath) calls remove_acl(filepath) and remove_immutable_attribute(filepath). In the scanned repository snapshot those helper functions are implemented as module-level functions in the same utils module; delete relies on them to perform platform-specific pre-deletion cleanup. The helpers themselves were documented separately and likewise show no external callers in the snapshot.

Why this is extracted into its own function:
- The deletion sequence involves multiple responsibilities (clearing ACLs, clearing immutable attributes, then deleting) and platform-dependent side effects. Encapsulating the sequence:
  - Reuses common pre-deletion logic in one place.
  - Makes higher-level code simpler and easier to test or mock.
  - Ensures the two cleanup steps always run (in order) before attempting to delete.

## Args:
    filepath (str or os.PathLike): Path to the target filesystem entry to remove.
        - Allowed values: any path string or path-like object accepted by os.path and os.remove/shutil.rmtree.
        - Interdependencies: The path value is passed verbatim to remove_acl and remove_immutable_attribute; those helpers may invoke external tools and assume the path is a string/path-like. Passing non-path types (e.g., None) will likely raise TypeError before deletion.

## Returns:
    None
    - The function does not return a value. Its purpose is the side-effect of removing filesystem state and running the pre-removal helpers.

## Raises:
The function does not catch exceptions from its sub-operations; callers should expect and handle exceptions that originate from the two helper functions and the deletion calls:
    - TypeError:
        * If filepath is not a string or path-like object such that os.path.isfile/os.path.islink/os.path.isdir raises TypeError (e.g., None).
    - NameError / AttributeError:
        * Can propagate from remove_acl or remove_immutable_attribute if required module-level names (such as constants) are missing or malformed.
    - OSError / FileNotFoundError / PermissionError:
        * From os.remove(filepath) when the file cannot be removed (permission denied, missing file due to race).
        * From shutil.rmtree(filepath) when recursive removal fails (permission denied, I/O error).
        * From subprocess-level errors raised by remove_acl or remove_immutable_attribute when starting external commands (e.g., OSError if the external binary cannot be executed).
    - Note on non-raising failures:
        * remove_acl and remove_immutable_attribute ignore non-zero exit codes from the external commands they invoke; those failures do not raise by themselves (only OS-level failures when starting the subprocess raise).

## Constraints:
Preconditions:
    - The caller should supply a valid filesystem path (string or os.PathLike).
    - If deletion is expected to succeed, the invoking process must have adequate filesystem permissions and any OS-level protections must be removable by the helper commands (or already absent).
    - The module defines remove_acl and remove_immutable_attribute in the scanned snapshot; delete calls those helpers at runtime.

Postconditions:
    - If the function runs to completion without raising and the target existed and was deletable, the target will no longer exist on disk.
    - If the target did not exist at the time of the existence checks, no deletion is attempted.
    - The function makes a best-effort attempt to clear ACLs and immutable attributes before deletion, but there is no guarantee those attributes were successfully removed — success depends on external tools and privileges.

## Side Effects:
    - Executes external commands indirectly via:
        * remove_acl(filepath) — may run platform commands (e.g., /bin/chmod, /bin/setfacl) to clear ACLs.
        * remove_immutable_attribute(filepath) — may run platform commands (e.g., /usr/bin/chflags, /usr/bin/chattr).
    - Mutates filesystem state by removing a file, link, or directory tree (os.remove or shutil.rmtree).
    - No module-level global variables are modified by delete itself; side effects are limited to filesystem and any external commands invoked.

## Control Flow:
flowchart TD
    Start --> CallRemoveACL
    CallRemoveACL --> CallRemoveImmutable
    CallRemoveImmutable --> CheckIsFileOrLink
    CheckIsFileOrLink --> |True| CallOsRemove
    CheckIsFileOrLink --> |False| CheckIsDir
    CallOsRemove --> End
    CheckIsDir --> |True| CallShutilRmtree
    CheckIsDir --> |False| EndNoop
    CallShutilRmtree --> End
    EndNoop --> End
    End --> Finish

## Examples:
Example 1 — Defensive deletion with error handling:
    # Attempt to delete a backup directory, but handle common failures.
    try:
        delete("/var/backups/myapp")
    except FileNotFoundError:
        # target already removed by another process; treat as success
        pass
    except PermissionError as exc:
        # insufficient privileges to remove files or run platform tools
        log_error("Permission denied removing backup: %s", exc)
    except OSError as exc:
        # other OS-level errors (I/O error, resource limits, failed subprocess start)
        log_error("Failed to remove backup due to OS error: %s", exc)

Example 2 — Best-effort cleanup in a restore/uninstall pipeline:
    # Before restoring or reinstalling, remove any previous installation state.
    try:
        delete("/opt/myapp")
    except Exception as exc:
        # Log and decide whether to continue; caller may choose to abort the pipeline
        log_warning("Could not fully remove previous install at /opt/myapp: %s", exc)
        # Depending on the pipeline, continue with caution or abort.

Notes and implementation hints:
    - The function checks the type of the path (file/link vs directory) using os.path helpers and performs deletion accordingly; a race condition can cause the existence check to pass and the subsequent delete to fail — callers should be prepared to handle FileNotFoundError and OSError.
    - If callers require strict guarantees that ACLs or immutable attributes were cleared successfully before deletion, consider invoking the helpers directly with stricter checks (e.g., using subprocess.check_call) and handling CalledProcessError, rather than relying on this function’s best-effort semantics.

## `mackup.utils.copy` · *function*

## Summary:
Copies a file or directory tree from src to dst on the local filesystem, creating any missing destination parent directories, and then unconditionally invokes the repository permission helper on the provided dst path.

## Description:
Known callers:
    - No direct callers were discovered in the available snapshot. Conceptually, this is used by higher-level restore/installation routines that place backed-up configuration files or configuration directories into their target locations (for example, restoring dotfiles or application config bundles).

Why this logic is extracted:
    - Centralizes the standard sequence for copying filesystem objects and the mandatory post-copy permission step: validate inputs, ensure destination parent exists, perform the appropriate copy (file vs. directory tree), and then enforce the repository permission policy (via chmod). This prevents inconsistent mkdir/copy/permission handling across the codebase.

## Args:
    src (str):
        - Path to the source filesystem object.
        - Must be a str (the function asserts this).
        - Must exist on the filesystem at call time (the function asserts os.path.exists(src)).
        - Allowed types: regular file or directory. Other filesystem object types (socket, FIFO, device node, etc.) are treated as unsupported and will cause a ValueError.

    dst (str):
        - Destination path where src will be copied to.
        - Must be a str (the function asserts this).
        - May be absolute or relative. The function ensures dst's parent directory exists; missing parents are created using os.makedirs.
        - Important semantics:
            * If dst is an existing directory and src is a file, shutil.copy places the file at dst/<basename(src)>.
            * If dst is an existing file and src is a file, shutil.copy overwrites dst.
            * If dst already exists and src is a directory, shutil.copytree will raise FileExistsError.
        - After the copy completes, chmod(dst) is invoked unconditionally (see Side Effects for implications when dst is a directory).

## Returns:
    None
    - The function performs filesystem side effects and returns implicitly None on success.
    - Postconditions: dst exists in a form corresponding to the copy semantics described above, and chmod(dst) has been invoked.

## Raises:
    AssertionError:
        - If src is not a str.
        - If src does not exist.
        - If dst is not a str.
        Note: assertions may be disabled under Python -O; callers that require enforced validation should perform explicit checks.

    ValueError:
        - If src exists but is neither a regular file nor a directory:
            raise ValueError("Unsupported file: {}".format(src))

    FileExistsError:
        - If src is a directory and dst already exists, shutil.copytree will raise FileExistsError.
        - os.makedirs(abs_path) may raise FileExistsError when a non-directory filesystem node exists at the computed parent path.

    OSError / PermissionError:
        - Other filesystem operations may raise these (e.g., failures creating directories, reading/writing files, insufficient privileges).

    Other exceptions:
        - Exceptions raised by chmod(dst) (such as OSError from os.chmod or errors from remove_immutable_attribute) will propagate.

## Constraints:
Preconditions:
    - src and dst must be str.
    - src must exist and be a file or directory.
    - Caller must have permission to read src and to create/write the destination (including creating parent directories).

Postconditions (on success):
    - Source has been copied according to Python shutil semantics:
        * File source: a file exists at dst (or at dst/<basename(src)> if dst is an existing directory).
        * Directory source: a directory tree exists at dst (copytree behavior).
    - Parent directories for dst have been created if necessary.
    - chmod(dst) has been invoked unconditionally:
        * If dst is a file path, chmod operates on that file.
        * If dst is an existing directory path (or copytree created a directory tree at dst), the chmod helper will operate on that directory. Per the chmod helper's documented behavior, when given a directory it applies owner-only modes recursively to the directory and its contents, so the newly copied files/directories under dst will also receive permission changes.

## Side Effects:
    - Creates directories on disk for dst's parent path via os.makedirs.
    - Reads from src and writes files/directories to dst via shutil.copy or shutil.copytree.
    - May overwrite existing files when src is a file and dst targets an existing file path.
    - Calls chmod(dst) unconditionally. The chmod helper may:
        * Remove platform-specific immutable attributes (running platform tools) and
        * Change permission bits on dst; if dst is a directory, chmod will recurse and modify permissions of files and subdirectories under dst.
    - No network I/O or global Python-level state mutation.

## Control Flow:
flowchart TD
    Start --> AssertSrcIsStr
    AssertSrcIsStr --> AssertSrcExists
    AssertSrcExists --> AssertDstIsStr
    AssertDstIsStr --> ComputeDstParentAbs
    ComputeDstParentAbs --> ParentDirExists?
    ParentDirExists? -->|no| TryMakeParentDirs
    ParentDirExists? -->|yes| DetermineSrcType
    TryMakeParentDirs -->|success| DetermineSrcType
    TryMakeParentDirs -->|FileExistsError/OSError| RaiseError
    DetermineSrcType -->|isfile| DoShutilCopy
    DetermineSrcType -->|isdir| DoShutilCopytree
    DetermineSrcType -->|other| RaiseValueError
    DoShutilCopy --> CallChmodOnDst
    DoShutilCopytree --> CallChmodOnDst
    CallChmodOnDst --> End
    RaiseError --> End

## Examples:
Example 1 — Copy a file into a directory and note chmod behavior:
    # If /tmp/restore exists as a directory, this will copy settings.json -> /tmp/restore/settings.json
    # and then call chmod("/tmp/restore"). Because chmod applies recursively for directories,
    # the copied file will receive the permission changes.
    try:
        copy("/home/alice/.config/myapp/settings.json", "/tmp/restore")
    except Exception as exc:
        print("Copy failed:", exc)

Example 2 — Copy a file to a specific path and ensure that path receives chmod:
    # If dst is a file path, that exact file is created/overwritten and chmod(dst) will apply to it.
    try:
        copy("/home/alice/.config/myapp/settings.json", "/tmp/restore/settings.json")
    except Exception as exc:
        print("Copy failed:", exc)

Example 3 — Copy a directory tree (caller must ensure dst does not already exist):
    try:
        copy("/var/backups/myapp/config", "/etc/myapp/config")
    except FileExistsError:
        print("Destination already exists; remove it first or choose another destination.")
    except Exception as exc:
        print("Failed to restore configuration:", exc)

Notes:
    - Because assertions are used for input validation, they may be no-ops under Python -O. If callers cannot tolerate invalid inputs, validate before calling.
    - shutil.copy and shutil.copytree behaviors (including symlink handling and metadata preservation) follow the Python standard library semantics.
    - chmod(dst) is always executed with the exact dst argument passed to copy; callers should choose dst accordingly if they require permission changes to apply to the copied contents.

## `mackup.utils.link` · *function*

## Summary:
Create a symbolic link at the specified destination pointing to an existing filesystem object, ensuring the destination directory exists and the target's permissions are made owner-writable before linking.

## Description:
Known callers within this repository snapshot:
    - No direct callers were discovered in the available snapshot. Typical callers in the project call this function during restore or install steps that re-create user configuration symlinks from a backup location into their original locations (for example, when restoring dotfiles or linking managed config files into a user's home directory).

Why this logic is extracted:
    - Encapsulates the common sequence required when creating a symlink: validate inputs, ensure the destination directory exists, apply the repository's canonical permission policy to the target (via chmod), and then create the symlink. Extracting it prevents repeating the parent-directory creation, permission-hardening, and symlink creation steps in multiple places and centralizes error semantics for link creation.

## Args:
    target (str):
        - Path to the existing filesystem object that the symlink should point to.
        - Must be a str. The function asserts this.
        - Must exist on the filesystem at call time. The function asserts this.
        - The function does not canonicalize or transform this path; the symlink content will be exactly the provided string (so it may be absolute or relative as given).
    link_to (str):
        - Destination path where the symbolic link will be created.
        - Must be a str. The function asserts this.
        - If parent directories of link_to do not exist, they will be created with os.makedirs (default mode) before creating the link.
        - If link_to already exists, os.symlink will raise an error (see Raises).

Notes on interdependencies:
    - The function calls chmod(target) before creating the symlink; any exceptions raised by chmod propagate to the caller.
    - No other parameters or optional flags are supported.

## Returns:
    None
    - On success the function returns implicitly with no value. The observable effect is the creation of a new symlink at link_to that references target and the side effects described below.
    - If the function completes without raising, then:
        * The parent directory of link_to exists (created if necessary).
        * chmod(target) has been executed.
        * A filesystem symlink exists at link_to (os.path.islink(link_to) will be True on POSIX systems).

## Raises:
    - AssertionError:
        * If target is not a str (first assert).
        * If target does not exist (second assert).
        * If link_to is not a str (third assert).
        Note: these assertions may be disabled when Python runs with -O, so they are not guaranteed in optimized runs.
    - OSError / PermissionError:
        * Any failure in os.makedirs(abs_path) (e.g., lacking permissions, race conditions, invalid path) will raise OSError or a subclass (PermissionError).
        * Any failure in os.symlink(target, link_to) (e.g., insufficient privileges, platform not supporting symlinks, invalid paths) will raise OSError or a subclass. On many platforms attempting to create a symlink where link_to already exists raises FileExistsError (a subclass of OSError).
    - FileExistsError:
        * Raised by os.symlink if the destination link_to already exists.
    - Errors propagated from chmod(target):
        * chmod may raise AssertionError, ValueError, OSError, PermissionError, or other errors (for example from remove_immutable_attribute). Those propagate out of this function unchanged.

## Constraints:
Preconditions:
    - target must be a string and must exist at the time of call.
    - link_to must be a string.
    - Caller should expect that assertion-based checks may be disabled under Python -O.
    - Caller should have sufficient permissions to:
        * create directories under the parent of link_to (if absent),
        * change permission bits on the target (chmod may require privileges),
        * create a symbolic link (on some platforms, creating symlinks requires elevated privileges).

Postconditions:
    - If the function returns successfully:
        * The directory containing link_to exists.
        * chmod(target) has executed (so target's permission bits may have been changed according to chmod's behavior).
        * A symlink is created at link_to referencing the exact string provided in target.
    - If an exception is raised, partial side effects may have occurred (e.g., parent directories may have been created, chmod may have modified target permissions) — there is no transactional rollback.

## Side Effects:
    - Creates missing parent directories for link_to using os.makedirs (filesystem write).
    - Calls chmod(target), which itself mutates filesystem permission bits and may invoke platform-specific utilities to remove immutable attributes.
    - Creates a filesystem symbolic link at link_to that points to target (filesystem write).
    - No network I/O, no modification of global Python state or in-memory caches.

## Control Flow:
flowchart TD
    Start --> CheckTargetType
    CheckTargetType -->|target is str| CheckTargetExists
    CheckTargetType -->|target not str| AssertError
    CheckTargetExists -->|exists| CheckLinkToType
    CheckTargetExists -->|missing| AssertError
    CheckLinkToType -->|link_to is str| EnsureParentDir
    CheckLinkToType -->|not str| AssertError
    EnsureParentDir -->|parent exists| CallChmod
    EnsureParentDir -->|parent missing| Mkdirs then CallChmod
    CallChmod --> ChmodSuccess
    ChmodSuccess --> CreateSymlink
    CreateSymlink -->|success| EndSuccess
    CreateSymlink -->|fails (OSError/FileExistsError)| RaiseOSError
    AssertError --> EndError
    RaiseOSError --> EndError

## Examples:
Example 1 — Typical usage, create a symlink to a backup config file:
    try:
        link("/backup/dotfiles/.vimrc", "/home/alice/.vimrc")
    except AssertionError:
        # target wasn't a str or didn't exist, or link_to wasn't a str
        raise
    except FileExistsError:
        # link_to already exists
        print("Destination already exists; remove it or choose another path.")
    except (OSError, PermissionError) as exc:
        # insufficient permissions or platform-specific failure when creating the link
        print("Failed to create symlink:", exc)

Example 2 — Overwrite an existing path by removing it first (explicit handling):
    import os
    try:
        if os.path.lexists(dest):        # lexists returns True for broken symlinks too
            if os.path.isdir(dest) and not os.path.islink(dest):
                raise RuntimeError("Refusing to remove an existing directory")
            os.remove(dest)
        link(source, dest)
    except Exception as exc:
        # handle or log the failure
        raise

Notes and platform caveats:
    - The created symlink content equals the provided target string; if you pass a relative path, the link will contain that relative path.
    - On platforms that restrict symlink creation (notably some Windows configurations), os.symlink may require administrative privileges or developer-mode settings and will raise OSError if not permitted.
    - Because chmod(target) is invoked before creating the link, target's permissions will be altered on success; callers that must preserve original modes should copy or record modes in advance.

## `mackup.utils.chmod` · *function*

## Summary:
Set restrictive owner-only permissions on a file or a directory tree after clearing platform-specific immutable attributes, ensuring files are readable/writable only by the owner and directories are executable for traversal.

## Description:
Known callers within the repository snapshot:
    - No direct callers were discovered in the available snapshot. Typical callers (in other parts of the project) invoke this function before operations that must modify or remove files/directories (for example, before overwriting configuration files or recursive deletion).

Why this logic is extracted:
    - Centralizes the platform-independent permission-setting policy and the sequence of pre-steps required to make files writable (clearing immutable attributes then applying modes). This keeps filesystem-permission semantics consistent across the codebase and avoids repeating recursion/subprocess handling in multiple places.

## Args:
    target (str):
        - The filesystem path to operate on.
        - Must be a str (the function asserts isinstance(target, str)).
        - The path must exist (the function asserts os.path.exists(target)).
        - The function accepts files or directories; other filesystem object types will cause a ValueError.

## Returns:
    None
    - This function performs side effects (changes permissions) and does not return a value.
    - There are no meaningful alternative return values; on success it returns None implicitly.

## Raises:
    - AssertionError:
        * If target is not a str (first assert).
        * If the path does not exist (second assert).
        Note: assertions may be disabled when Python is run with -O, so these checks are not guaranteed in all runtime modes.
    - ValueError:
        * Raised when the target exists but is neither a regular file nor a directory (for example: a socket, FIFO, device node, or other unsupported file type).
    - OSError / PermissionError:
        * Any os.chmod or os.walk underlying filesystem calls can raise OSError/PermissionError when the process lacks permission or when the filesystem reports an error.
    - Errors raised by remove_immutable_attribute:
        * remove_immutable_attribute(target) is called before changing modes; that helper may raise (e.g., NameError if constants are missing, OSError from subprocess execution, TypeError on invalid inputs). Those errors propagate unless handled by the caller.

## Constraints:
Preconditions:
    - target must be a str and must exist on the filesystem at call time.
    - Caller should expect that assertions are used for validation (they can be skipped under optimized runs).
    - Caller should have sufficient privileges to change permissions and to run any external immutable-attribute removal utilities invoked by remove_immutable_attribute.

Postconditions:
    - If the call completes without raising:
        * If target is a regular file: target's permission bits will be set to owner read/write only (octal 0o600; stat.S_IRUSR | stat.S_IWUSR).
        * If target is a directory: the directory and all directories under it will be set to owner read/write/execute (octal 0o700; stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR), and all files under it will be set to owner read/write only (0o600).
    - remove_immutable_attribute(target) will have been invoked prior to any chmods; any immutable attributes that could block permission changes or deletion may have been removed (best-effort, depends on platform and privileges).
    - If an exception is raised part-way through the recursion, some entries may have had their modes changed while others have not (no transactional guarantee).

## Side Effects:
    - Calls remove_immutable_attribute(target), which may execute external platform utilities (e.g., chflags or chattr) and modify filesystem metadata.
    - Calls os.chmod on the target and potentially many paths beneath it (when target is a directory), modifying permission bits.
    - Traverses the directory tree using os.walk (no network I/O).
    - No Python-level global state is mutated by this function.

## Control Flow:
flowchart TD
    Start --> CheckType
    CheckType -->|isinstance(target,str)| CheckExists
    CheckType -->|not str| AssertError
    CheckExists -->|os.path.exists(target)| SetModes
    CheckExists -->|not exists| AssertError
    SetModes --> RemoveImmutable
    RemoveImmutable -->|after| IsFile
    IsFile -->|True| ChmodFile
    IsFile -->|False| IsDir
    ChmodFile --> End
    IsDir -->|True| ChmodDirAndRecurse
    IsDir -->|False| RaiseValueError
    ChmodDirAndRecurse --> ForEachEntry
    ForEachEntry --> End
    AssertError --> End
    RaiseValueError --> End

## Examples:
Example 1 — Make a single file owner-read/write only, handling permission errors:
    try:
        chmod("/home/alice/.config/myapp/settings.json")
    except AssertionError:
        # Either target was not a str or did not exist
        raise
    except (OSError, PermissionError) as exc:
        # Could not change permissions or remove immutable attribute
        print("Failed to set permissions:", exc)

Example 2 — Make a project directory and its contents owner-only and robustly handle failures:
    try:
        chmod("/srv/myapp/backups")
    except AssertionError:
        raise ValueError("Provided path is invalid or does not exist")
    except ValueError as exc:
        # Unsupported file type (e.g., the path is a socket/device)
        print("Unsupported target type:", exc)
    except Exception as exc:
        # Log and surface unexpected errors from remove_immutable_attribute or os.chmod
        print("Unexpected error while changing permissions:", exc)

Notes and implementation hints:
    - The exact permission masks used are:
        * Files: stat.S_IRUSR | stat.S_IWUSR (0o600)
        * Folders: stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR (0o700)
    - The function uses os.walk without followlinks, so symbolic links to directories are not traversed; os.chmod on symlinks follows the link on many platforms and will affect the link target rather than the symlink itself—be cautious if the tree contains symlinks.
    - Because assertions are used for input validation, callers that rely on these checks should not assume they run when Python is executed with optimizations (-O).

## `mackup.utils.error` · *function*

## Summary:
Terminates the running process with a colored "Error: <message>" message by raising SystemExit.

## Description:
This helper emits a red-colored error message prefixed with "Error: " and then exits the process by invoking the system exit mechanism. It is intended for use whenever the program encounters an unrecoverable error and should stop immediately.

Known callers within a typical codebase:
- Called from command-line entry points, configuration/validation routines, or other places that detect fatal conditions and must abort execution. (No callers were provided in the limited context supplied; search the repository for references to this function to find concrete callers.)

Why this logic is factored into its own function:
- Centralizes consistent formatting and exit behavior for fatal errors (uniform prefix, color usage, and exit call).
- Makes unit testing easier: tests can catch the SystemExit raised and assert the message.
- Keeps calling code concise and expressive (callers can simply call this function instead of duplicating formatting and exit logic).

## Args:
    message (any): The error message to display. It will be converted to a string using str(message). Typical values are str objects describing the fatal condition.

## Returns:
    This function does not return normally. It always raises SystemExit (see Raises). There are no return values.

Possible outcomes:
- If not intercepted, the process will terminate after printing the message.
- If a caller catches SystemExit, no process termination occurs and the SystemExit instance contains the formatted message as its "code" attribute.

## Raises:
    SystemExit: Always raised by calling sys.exit(...) with a formatted, colorized string. The SystemExit.code value will be the full formatted message (the ANSI-colored string).

## Constraints:
Preconditions:
- The caller should ensure that exiting the process is the correct response for the detected condition (this function unconditionally requests process termination).
- message must be convertible to string (any object with a valid str() representation).

Postconditions:
- If SystemExit is not caught, the interpreter terminates. If it is caught, the caller will receive a SystemExit exception whose .code equals the colorized error string inserted by this function.

## Side Effects:
- Emits a formatted string containing ANSI color codes (red) and the text "Error: <message>". When uncaught, Python's interpreter prints the string to stderr during shutdown.
- Causes process termination by raising SystemExit; this is the primary side effect.
- No file, network, or persistent external state is modified by this function.

Platform notes:
- The ANSI color codes used (ESC[91m and ESC[0m) may not render as colored text on all terminals (e.g., some Windows consoles) and may appear as raw escape sequences if the terminal does not support ANSI escapes.

## Control Flow:
flowchart TD
    Start --> Format["Format message: 'Error: {message}'"]
    Format --> Colorize["Wrap with ANSI red and reset codes"]
    Colorize --> SysExit["Call sys.exit(formatted_message)"]
    SysExit --> Raise["Raise SystemExit(formatted_message)"]
    Raise --> End["End (process exits if not caught)"]

## Examples:
- Typical usage in a CLI script:
    error("configuration file not found")

- Example showing how a test or higher-level code can catch the exit for verification:
    try:
        error("invalid profile")
    except SystemExit as e:
        # e.code contains the ANSI-colored "Error: invalid profile" string
        msg = str(e.code)
        assert "Error: invalid profile" in msg
        # test can proceed without terminating the test runner

- Example showing safe guard before calling:
    if not os.path.exists(config_path):
        error("required config is missing: {}".format(config_path))

## `mackup.utils.get_dropbox_folder_location` · *function*

## Summary:
Return the path to the user's Dropbox folder by reading and decoding the Dropbox host.db file in the user's HOME directory.

## Description:
- Known callers within the provided context:
    - No direct callers were found in the supplied code excerpts. In a typical application this function is called by components that need to locate a user's Dropbox storage for backup, sync or migration tasks — for example: storage-detection code, initialization of sync routines, or routines that copy configuration files to/from Dropbox.

- Typical trigger/context:
    - Called during setup or runtime when the program needs the absolute filesystem path to the Dropbox folder for the current user.

- Why this logic is extracted into its own function:
    - Encapsulates the platform/user-specific logic of locating Dropbox storage (file location, file format parsing, base64 decoding) in one place.
    - Keeps callers simple (they receive a path string or the process exits on fatal error) and isolates error handling for the missing/invalid host.db file.
    - Makes the behavior reusable and testable — tests can verify successful decode or assert that fatal conditions call the shared error() routine.

## Args:
    None

## Returns:
    str: The decoded filesystem path of the Dropbox folder for the current user (a unicode/str object).
    - Normal outcome: a non-empty string representing the Dropbox home directory (e.g., "/home/alice/Dropbox" or "/Users/alice/Dropbox").
    - The function never returns on one common failure mode — when opening the host.db file fails it calls error(...), which raises SystemExit (see Raises).
    - This function does not validate that the returned path actually exists on disk; callers should check existence if required.

## Raises:
    SystemExit
        - Triggered when the host.db file cannot be opened for reading. The code catches IOError and calls error(constants.ERROR_UNABLE_TO_FIND_STORAGE.format(provider="Dropbox install")), which prints a formatted message and raises SystemExit.
    KeyError
        - If the HOME environment variable is not present (os.environ["HOME"]) a KeyError will be raised before the file-open attempt.
    IndexError
        - If host.db is read successfully but the file contents do not contain at least two whitespace-separated tokens, accessing data[1] will raise IndexError.
    binascii.Error (or equivalent from base64)
        - If data[1] is not valid base64, base64.b64decode will raise a decoding error (module-specific exception such as binascii.Error).
    UnicodeDecodeError
        - If the bytes returned by base64.b64decode cannot be decoded to text using the default text codec, decode() will raise UnicodeDecodeError.
    OSError / IOError variants
        - Although file-open failures are caught and handled by calling error(...), other low-level OS errors that occur outside the open call may still propagate.

## Constraints:
- Preconditions:
    - The caller should ensure the process' environment includes HOME (or be prepared to handle KeyError).
    - The Dropbox client must have created a ~/.dropbox/host.db file; the function expects that file to contain a second whitespace-separated token which is the base64-encoded Dropbox path.
- Postconditions:
    - On successful return, the function yields a string representing the decoded Dropbox folder path.
    - On a missing/unreadable host.db, the function does not return normally; it delegates to error(...) which raises SystemExit (terminating the process unless caught).

## Side Effects:
- I/O: Reads the file at $HOME/.dropbox/host.db.
- Process control: May call error(...), which prints a colored error message and raises SystemExit — this is the primary process-level side effect.
- No network activity, no file writes, and no mutation of global variables are performed by this function itself.

## Control Flow:
flowchart TD
    Start --> BuildPath["Build host_db_path = $HOME/.dropbox/host.db"]
    BuildPath --> TryOpen["Try open(host_db_path)"]
    TryOpen -->|open fails (IOError/OSError)| CallError["Call error(...) -> SystemExit"]
    CallError --> EndExit["Process exits unless SystemExit is caught"]
    TryOpen -->|open succeeds| ReadSplit["Read file and split() into tokens -> data"]
    ReadSplit -->|len(data) < 2| IndexErr["IndexError: accessing data[1]"]
    IndexErr --> EndErr["Exception propagates to caller"]
    ReadSplit -->|len(data) >= 2| DecodeBase64["base64.b64decode(data[1])"]
    DecodeBase64 -->|invalid base64| Base64Err["binascii.Error (decode failure)"]
    Base64Err --> EndErr
    DecodeBase64 --> DecodeText[".decode() bytes -> unicode"]
    DecodeText -->|unicode decode fails| UnicodeErr["UnicodeDecodeError"]
    UnicodeErr --> EndErr
    DecodeText --> ReturnPath["Return decoded dropbox_home string"]
    ReturnPath --> End

## Examples:
- Successful use (conceptual):
    - The program calls this function during initialization to obtain the Dropbox path to mirror configuration files there. After calling, the caller typically checks that the returned path exists and then proceeds to read/write within it.

- Defensive usage pattern:
    - Because this function may terminate the process via SystemExit or raise other exceptions (IndexError, decoding errors), callers that must continue running should catch these exceptions:
        - Catch SystemExit if you want to present a different fallback behavior instead of aborting.
        - Catch IndexError, binascii.Error, UnicodeDecodeError to detect and handle malformed host.db contents (for example, fall back to a configured path or skip Dropbox integration).

- Example handling approach (described in prose):
    - Try to call get_dropbox_folder_location().
    - If it returns a path, verify os.path.exists(path) before using it.
    - If SystemExit is raised (host.db missing/unreadable), log or surface a user-friendly message and either abort or continue with Dropbox disabled.
    - If IndexError or decoding errors occur, treat host.db as corrupted: report the corruption and skip Dropbox integration or prompt the user to re-link Dropbox.

## `mackup.utils.get_google_drive_folder_location` · *function*

## Summary:
Locate and return the user's Google Drive local sync root by reading the Google Drive SQLite sync_config.db and returning its local_sync_root_path value as a Python string.

## Description:
This function searches for Google Drive's sync_config.db under the current user's HOME directory, opens the database if present, executes a SELECT to read the data_value for the entry_key 'local_sync_root_path', and returns that value converted with str(...).

Known callers within the provided context:
- No direct callers were present in the supplied context. Typical callers are setup/backup routines or storage-detection code that must discover the local Google Drive folder before performing file operations, synchronisation, or creating links.

Why this logic is extracted:
- Centralizes platform- and schema-specific detection of Google Drive's local root into one reusable function. It hides file-path conventions, SQLite access, and error/exit handling so callers remain simple and do not duplicate discovery logic.

## Args:
    None

## Returns:
    str: The path stored in the Google Drive sync configuration under the 'local_sync_root_path' key, converted via str(...).
    Possible return forms and edge cases:
        - A normal filesystem path string, e.g. "/Users/alice/Google Drive".
        - If the fetched DB value is bytes, the function returns str(bytes_value), e.g. "b'/Users/alice/Google Drive'".
        - If the fetched DB value is None, the function returns the string "None" (because str(None) == "None").
        - If the fetched DB value is an empty string, the result is '' (empty string); this is falsy and will cause the function to call the module-level error(...) helper (which raises SystemExit).
    Note: The function never returns None on successful completion; either a string is returned or an exception is raised.

## Raises:
    KeyError:
        If the HOME environment variable is missing (os.environ["HOME"] access), a KeyError is raised before any filesystem or DB operations.
    sqlite3.Error (e.g., sqlite3.OperationalError):
        Any SQLite error raised by sqlite3.connect() or during SQL execution will propagate to the caller because the function does not catch database exceptions.
    TypeError:
        If the SELECT query executes successfully but cur.fetchone() returns None (no matching row), the function attempts to access data[0], which raises TypeError. This occurs before the module-level error(...) call and thus produces a TypeError rather than the formatted SystemExit in that specific case.
    SystemExit:
        If no googledrive_home value is set (the code checks the truthiness of googledrive_home after DB handling), the function calls error(constants.ERROR_UNABLE_TO_FIND_STORAGE.format(provider="Google Drive install")), and that helper raises SystemExit. This path happens when the DB file is not found under the checked locations, or when the DB returned an empty-string value for local_sync_root_path (''), making googledrive_home falsy. Note that when cur.fetchone() returned None, a TypeError is raised earlier and SystemExit is not reached.

## Constraints:
Preconditions:
    - The HOME environment variable must be defined and point to the current user's home directory.
    - The process must have read permission for the Google Drive sync_config.db file if it exists.
    - The function is written for environments where Google Drive places a sync_config.db under:
        - $HOME/Library/Application Support/Google/Drive/sync_config.db (default)
        - or the Yosemite variant: $HOME/Library/Application Support/Google/Drive/user_default/sync_config.db
Postconditions:
    - On success, returns a string representation of the database value for local_sync_root_path.
    - If no usable value is determined, the function will either raise TypeError (if the DB returned no row) or call error(...) which raises SystemExit (when googledrive_home remains falsy, e.g., DB missing or DB returned empty string).

## Side Effects:
    - Filesystem checks for existence of two database candidate paths under HOME.
    - Opens a SQLite connection (sqlite3.connect) and executes a SELECT query to read configuration.
    - May cause process termination by invoking error(...), which raises SystemExit.
    - Does not write to files or perform network I/O.

## Control Flow:
flowchart TD
    Start --> SetPaths["Set gdrive_db_path and yosemite_gdrive_db_path"]
    SetPaths --> ComputeYosemite["yosemite_gdrive_db = os.path.join(HOME, yosemite_gdrive_db_path)"]
    ComputeYosemite --> CheckYosemite{"Does yosemite_gdrive_db exist?"}
    CheckYosemite -->|yes| UseYosemite["gdrive_db_path = yosemite_gdrive_db_path"]
    CheckYosemite -->|no| UseDefault["gdrive_db_path remains default"]
    UseYosemite --> ComputeFull["gdrive_db = os.path.join(HOME, gdrive_db_path)"]
    UseDefault --> ComputeFull
    ComputeFull --> FileExists{"Is gdrive_db an existing file?"}
    FileExists -->|no| NoDB["googledrive_home stays None"]
    FileExists -->|yes| OpenConn["con = sqlite3.connect(gdrive_db)"]
    OpenConn --> Cursor["cur = con.cursor()"]
    Cursor --> Execute["Execute SELECT data_value FROM data WHERE entry_key = 'local_sync_root_path'"]
    Execute --> Fetch["data = cur.fetchone()"]
    Fetch -->|row returned| Extract["googledrive_home = str(data[0])"]
    Fetch -->|no row (None)| RaiseTypeError["Attempt to access data[0] -> TypeError raised (propagates)"]
    Extract --> CloseConn["con.close()"]
    CloseConn --> ResultCheck
    NoDB --> ResultCheck
    ResultCheck{"Is googledrive_home truthy?"} -->|yes| Return["Return googledrive_home (string)"]
    ResultCheck -->|no| CallError["Call error(...formatted...) -> raises SystemExit"]

## Examples:
- Typical usage (caller expects either a path or termination):
    try:
        path = get_google_drive_folder_location()
        # proceed using `path`
    except SystemExit:
        # error(...) already printed a formatted message and requested exit
        # handle or re-raise depending on program logic
    except sqlite3.Error as e:
        # database issue: inspect DB file permissions or integrity
        raise

- Defensive wrapper to translate TypeError into a clearer error:
    try:
        path = get_google_drive_folder_location()
    except TypeError:
        raise RuntimeError("Google Drive DB missing expected row 'local_sync_root_path' in sync_config.db")

- Diagnostic notes:
    - If you see TypeError, inspect the DB to confirm the 'data' table contains a row with entry_key 'local_sync_root_path'.
    - If SystemExit is raised with an "unable to find storage" error, check that the sync_config.db file exists in one of the two expected locations under $HOME and that it contains a non-empty data_value for the requested key.

## `mackup.utils.get_copy_folder_location` · *function*

## Summary:
Return the Copy Agent storage root path by reading the user's Copy Agent SQLite configuration; returns the configured path as a string on success.

## Description:
This function locates the Copy Agent configuration database under the current user's HOME directory, opens it with sqlite3, runs a SELECT on the config2 table for option='csmRootPath', and returns that value coerced to a string.

Known callers:
- None found in the provided repository snapshot. Typical callers are higher-level provider-detection, backup/restore orchestration, or synchronization setup logic that needs the Copy client's configured storage root during provider discovery or when constructing filesystem paths to operate on.

Why this is a separate function:
- Encapsulates provider-specific discovery details (macOS-style config path, SQLite access, and the SQL query) so callers do not need to know the config location or SQL schema.
- Centralizes error handling for the "not found" case via the global error(...) helper and a shared constants message, keeping client code simpler and consistent.

## Args:
This function takes no arguments.

## Returns:
Optional[str]
- On success: returns a str containing the value of the 'csmRootPath' entry from the Copy Agent config2 table. This is intended to be an absolute filesystem path.
- Edge cases:
  - If the database exists but the selected row's value is an empty string, the function treats it as falsy and will invoke the global error(...) call (see Raises / Side Effects). Therefore an empty-string stored in the DB is not treated as a successful path.
  - If error(...) does not terminate the process, the function will return the current copy_home value (which may be None).
  - If the config.db file does not exist at the expected path, the function calls error(...) and returns None only if error(...) does not terminate execution.

## Raises:
The function does not explicitly raise custom exceptions, but callers should be prepared to handle these exceptions that may be propagated from operations inside the function:
- KeyError: if the HOME environment variable is not present (os.environ["HOME"]).
- sqlite3.Error (or a subclass): if sqlite3.connect(copy_settings) fails or if executing the SQL query raises a database error.
- TypeError: if cur.fetchone() returns None (no matching row) and the code attempts data[0], resulting in 'NoneType' object is not subscriptable.
- Any other OSError/IO-related exceptions that may be raised by underlying os/path calls.

Additionally: If copy_home is falsy after the lookup (None or empty string), the function calls error(constants.ERROR_UNABLE_TO_FIND_STORAGE.format(provider="Copy install")). The exact effect (raise, exit, log) depends on the implementation of the global error(...) helper and is not defined here.

## Constraints:
Preconditions:
- The caller's process environment must provide a HOME variable pointing to the user's home directory, or the caller must handle KeyError.
- The platform is expected to have the Copy Agent config stored at HOME/Library/Application Support/Copy Agent/config.db; on non-macOS systems that path is unlikely to exist.

Postconditions:
- If a non-empty value exists for option='csmRootPath' in the Copy Agent config2 table, the function returns that value converted to str.
- If no such value exists or the file is missing, the function invokes error(...) with a provider-specific message. If error(...) returns, the function will return None (or an empty string if that was the DB value), otherwise the process may terminate according to error(...).

Important implementation detail visible in the code:
- The function closes the SQLite cursor (cur.close()) but does not close the sqlite3.Connection object (database.close()) before returning; the connection will remain open until garbage-collected or the process exits unless the global error(...) handling terminates execution. Callers running many such operations should be aware of potential resource usage.

## Side Effects:
- Reads the HOME environment variable (os.environ["HOME"]).
- Checks filesystem presence of the config.db file (os.path.isfile).
- Opens a sqlite3.Connection to the config database (sqlite3.connect); this opens the file for database access.
- Executes a SELECT statement against the database (read-only from this function).
- Closes the database cursor (cur.close()), but does not explicitly close the database connection.
- Calls the global error(...) function with constants.ERROR_UNABLE_TO_FIND_STORAGE formatted using provider="Copy install"; side effects from error(...) (logging, raising, exiting) are possible but depend on that external implementation.

## Control Flow:
flowchart TD
    Start --> BuildPath["Build copy_settings = os.path.join(HOME, 'Library/Application Support/Copy Agent/config.db')"]
    BuildPath --> FileExists{"os.path.isfile(copy_settings)?"}
    FileExists -->|No| CallError["Call error(constants.ERROR_UNABLE_TO_FIND_STORAGE(...))"]
    FileExists -->|Yes| ConnectDB["database = sqlite3.connect(copy_settings)"]
    ConnectDB -->|sqlite3.Error| DBError["sqlite3.Error propagates to caller"]
    ConnectDB --> Cursor["cur = database.cursor()"]
    Cursor --> ExecQuery["cur.execute(\"SELECT value FROM config2 WHERE option = 'csmRootPath';\")"]
    ExecQuery --> Fetch["data = cur.fetchone()"]
    Fetch -->|data is not None| SetCopyHome["copy_home = str(data[0]); cur.close()"]
    Fetch -->|data is None| FetchNone["Accessing data[0] -> TypeError ('NoneType' object not subscriptable)"]
    SetCopyHome --> CheckCopyHome{"if not copy_home (None or empty string)?"}
    CheckCopyHome -->|True| CallError
    CheckCopyHome -->|False| Return["return copy_home (str)"]
    CallError --> Return

## Examples (prose):
- Successful path (typical):
  1. A provider-detection routine needs the Copy client's storage root.
  2. It calls this function; the function locates HOME/Library/Application Support/Copy Agent/config.db, opens it, and selects value FROM config2 WHERE option='csmRootPath'.
  3. If a non-empty value exists, the caller receives that path as a Python string and proceeds to operate on files under that path.

- Error and robustness guidance:
  1. Protect callers against missing HOME by catching KeyError and providing a user-friendly message.
  2. Protect against sqlite3.Error when the DB is corrupt or unreadable — catch sqlite3.Error to provide a fallback or diagnostics.
  3. Be aware that if the DB contains an empty string for csmRootPath the function will treat it as missing and call error(...). If you want to tolerate empty strings, perform your own DB lookup or adjust error handling upstream.
  4. If your code will query many provider DBs in a loop, consider modifying this function to explicitly close the sqlite3.Connection to avoid accumulating open connections.

## `mackup.utils.get_icloud_folder_location` · *function*

## Summary:
Return the absolute filesystem path to the user's iCloud Drive "Mobile Documents" folder (~/Library/Mobile Documents/com~apple~CloudDocs/) after expanding the tilde; if that location does not exist as a directory, trigger the project's fatal error behavior (process exit).

## Description:
This function resolves the conventional macOS iCloud Drive folder by expanding the literal path "~/Library/Mobile Documents/com~apple~CloudDocs/" using os.path.expanduser and validating that the result is a directory with os.path.isdir.

Known callers within the provided context:
- No direct callers were supplied in the limited context for this task. In common usage inside a macOS backup/sync utility, callers include initialization, configuration validation, or any routine that needs the iCloud Drive root path before accessing files there.

Why this logic is extracted into its own function:
- Centralizes the platform-specific path literal and the existence check so callers receive a single validated path or experience a consistent fatal error behavior.
- Encapsulates the decision to abort on missing storage (delegated to the error(...) helper) so higher-level code can remain focused on business logic.

## Args:
    None

## Returns:
    str: The expanded absolute path to the iCloud Drive "Mobile Documents" folder. Specifically, the function returns the string result of str(os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/")).

    Guarantee on normal return:
    - The returned path points to an existing directory: os.path.isdir(returned_value) is True.

    Edge-case outcomes:
    - If the expanded path is a symlink that points to a directory, os.path.isdir returns True and the symlink path is returned.
    - If the expanded path does not exist or is not a directory, the function does not return normally (see Raises).

## Raises:
    SystemExit: Raised indirectly via the project's error(...) helper when the expanded path is missing or not a directory. The function calls:
        error(constants.ERROR_UNABLE_TO_FIND_STORAGE.format(provider="iCloud Drive"))
    According to the error helper's behavior, this call formats a colored "Error: ..." message and calls sys.exit(...), which raises SystemExit with the formatted message as its .code.

## Constraints:
Preconditions:
    - os.path.expanduser must be able to process "~" for the current environment (typical on OSes with a user home directory); if expanduser returns a non-directory path, the function will treat that as failure.
    - The function assumes the conventional iCloud Drive location used in the code literal; if iCloud is stored elsewhere on a given system, this function will consider the conventional location missing.

Postconditions:
    - On successful return, the function guarantees that the returned string is an existing directory path.
    - On failure, the function triggers the project's fatal exit behavior (SystemExit) unless the caller catches SystemExit.

## Side Effects:
    - Reads filesystem metadata: calls os.path.expanduser and os.path.isdir.
    - May cause a formatted error message to be emitted and the process to exit by delegating to error(...). The error(...) helper prints a colored "Error: <message>" and calls sys.exit(...), raising SystemExit.

## Control Flow:
flowchart TD
    Start --> SetLiteral["Set yosemite_icloud_path = '~/Library/Mobile Documents/com~apple~CloudDocs/'"]
    SetLiteral --> Expand["icloud_home = os.path.expanduser(yosemite_icloud_path)"]
    Expand --> IsDir{"os.path.isdir(icloud_home) ?"}
    IsDir -- Yes --> Return["return str(icloud_home)"]
    IsDir -- No --> CallError["error(constants.ERROR_UNABLE_TO_FIND_STORAGE.format(provider='iCloud Drive'))"]
    CallError --> SysExit["error(...) calls sys.exit(...) -> raises SystemExit"]
    SysExit --> End["End (process exits if not caught)"]

## Examples:
- Happy path:
    path = get_icloud_folder_location()
    # path is a string pointing to an existing directory under the user's home,
    # e.g. '/Users/alice/Library/Mobile Documents/com~apple~CloudDocs/'

- Handling the missing-directory case (explicitly catching the SystemExit raised by error(...)):
    try:
        path = get_icloud_folder_location()
    except SystemExit as e:
        # The project's error(...) helper raises SystemExit with a formatted message.
        # e.code contains the formatted (colored) error message string.
        msg = str(e.code)
        logger.error("Unable to locate iCloud Drive: %s", msg)
        # decide on fallback behavior or re-raise if desired

Notes:
- The function uses the exact hard-coded path literal "~/Library/Mobile Documents/com~apple~CloudDocs/" and will only succeed if that location (after expansion) exists and is a directory.
- Callers that must avoid process termination should catch SystemExit around this call.

## `mackup.utils.is_process_running` · *function*

## Summary:
Checks for a running process that matches the given name by invoking the system pgrep utility and returns True when pgrep reports a match; otherwise returns False.

## Description:
Known callers within the codebase:
- Call sites are not enumerated here; document consumers should search the repository for usages of this function to determine local callers.

Typical usage context:
- Used as a simple, platform-dependent probe to decide whether an operating-system process (identified by name or pattern) is already running before taking actions such as starting another instance or enabling an integration that depends on that process.

Why this logic is extracted:
- Encapsulates the dependency on an external binary (/usr/bin/pgrep), the filesystem existence check for that binary, and the interpretation of its exit code in one place so callers can ask a single boolean question instead of duplicating subprocess and path-checking logic.

## Args:
    process_name (str):
        - The name or pattern string forwarded as the single argument to the pgrep command.
        - Expected type: str. The function does not validate or sanitize the pattern; pgrep's matching semantics apply.
        - If callers provide a non-string type, behavior is determined by subprocess.call and is not handled by this function.

## Returns:
    bool:
        - True: /usr/bin/pgrep exists (os.path.isfile returned True), pgrep was executed, and its exit code was 0 (pgrep found at least one matching process).
        - False: either /usr/bin/pgrep does not exist on the filesystem or pgrep executed and returned a non-zero exit code (no matches or other non-zero status).
        - The function does not provide counts, PIDs, or any additional match information—only a boolean result based on pgrep's exit code and presence.

## Raises:
    OSError (including subclasses such as PermissionError):
        - Opening os.devnull may raise OSError if the null device is inaccessible on the platform.
        - subprocess.call may raise OSError if invoking the executable fails at the OS level (for example, if /usr/bin/pgrep is present but not executable, or if an exec failure occurs).
    Notes:
        - The function does not explicitly catch these exceptions; callers that need robust error handling should catch OSError (or more specific subclasses) around calls to this function.

## Constraints:
Preconditions:
    - Intended for environments where /usr/bin/pgrep is the expected pgrep location (typical Linux installs). On systems where pgrep is absent or located elsewhere, the function will return False.
    - The caller should pass a process_name appropriate for pgrep. The function does not perform quoting or pattern adjustment.

Postconditions:
    - The function returns a boolean reflecting the two checks described under Returns.
    - It does not guarantee that a file descriptor opened for os.devnull is closed before return (see Side Effects).

## Side Effects:
    - Opens the platform null device via open(os.devnull, "wb") and assigns it to a local variable (dev_null). The file object is not explicitly closed in the function, so a file descriptor may remain open until Python's garbage collector closes it—this is a resource leak risk if the function is called frequently.
    - Spawns a subprocess that runs /usr/bin/pgrep with the provided argument and waits for it to complete (subprocess.call). No stdout from pgrep is shown because stdout is redirected to the opened dev_null.
    - No files are written and no global state is modified by this function beyond the transient subprocess execution and the opened dev_null descriptor.

## Control Flow:
flowchart TD
    A[Start: is_process_running(process_name)] --> B{isfile("/usr/bin/pgrep")?}
    B -- False --> C[Return False]
    B -- True --> D[Open os.devnull for wb (dev_null)]
    D --> E[Call subprocess.call(['/usr/bin/pgrep', process_name], stdout=dev_null)]
    E --> F{returncode == 0?}
    F -- True --> G[Return True]
    F -- False --> C[Return False]

## Examples (usage guidance and error handling):
- Pre-start guard (prose): Before starting a service named "myservice", call this function with "myservice". If it returns True, skip starting another instance. Wrap the call in a try/except catching OSError to handle unexpected platform-level failures (e.g., permission issues or missing /dev/null).

- Robust cross-platform note: Because this implementation hard-codes /usr/bin/pgrep and only checks for its existence with os.path.isfile, code that must work across Linux, macOS, or other Unix-like systems should provide a fallback detection strategy (e.g., configurable pgrep path, using ps + filtering, or platform-specific APIs) rather than relying solely on this function.

- Resource safety recommendation: To avoid leaking file descriptors when calling this check frequently, replace the local open with a context-managed open (with ...) or reuse a shared opened devnull file object managed at a higher level.

## `mackup.utils.remove_acl` · *function*

## Summary:
Recursively strips filesystem Access Control Lists (ACLs) from the supplied path by invoking the platform-native tool when present (macOS: /bin/chmod -R -N; Linux: /bin/setfacl -R -b).

## Description:
This function performs a platform-specific, best-effort removal of ACLs under a given filesystem path. It detects the current operating system and, only when the exact expected system binary exists at the hard-coded path, executes a synchronous external command to remove ACL entries recursively.

Platform behavior implemented:
- macOS: If platform.system() equals constants.PLATFORM_DARWIN and the file /bin/chmod exists, runs /bin/chmod -R -N path.
- Linux: If platform.system() equals constants.PLATFORM_LINUX and the file /bin/setfacl exists, runs /bin/setfacl -R -b path.
- Otherwise: no action is taken.

Known callers within the scanned codebase:
- No direct call sites were found in the scanned portions of the codebase. In practice this utility is intended to be used in file-copy/restore/installation steps that must normalize permissions after restoring files from backups or synchronizing files between systems.

Why this is a separate helper:
- The operation is small but platform- and tool-specific and has side effects (external command invocation). Extracting it isolates the platform detection, binary-path checks, and subprocess invocation, making higher-level code simpler and enabling straightforward mocking in tests.

## Args:
    path (str): Filesystem path (file or directory) to operate on. Must be a string acceptable to the OS command and may be absolute or relative. No default value.

Interdependencies and constraints:
- The function expects the module environment to expose a `constants` object with attributes PLATFORM_DARWIN and PLATFORM_LINUX (typically provided by the package's constants module).
- The function checks for system binaries at the fixed absolute paths /bin/chmod and /bin/setfacl; binaries located elsewhere (for example, /usr/bin/chmod) will not be detected by this function.

## Returns:
    None

Notes:
- The function does not return any value. It invokes subprocess.call and discards the numeric exit code. Command success/failure (non-zero exit status) is not propagated.

## Raises:
The function does not explicitly raise exceptions but the underlying runtime may raise:
- TypeError: If `path` is not a string (e.g., None or another non-str type) such that constructing the argument list is invalid for subprocess.
- OSError / FileNotFoundError / PermissionError: If starting the subprocess fails (this can occur due to OS resource limits, permission problems, or a race condition where the binary was removed between the existence check and the call). These originate from subprocess.call's attempt to create or exec the child process.
- No exception is raised for non-zero exit statuses of the invoked command; subprocess.call returns the exit code but the function ignores it.

## Constraints:
Preconditions:
- `constants.PLATFORM_DARWIN` and `constants.PLATFORM_LINUX` must be defined and comparable to platform.system() results.
- The calling process must have sufficient permission to execute the system binary and to modify ACLs for the target path.
- The function assumes the caller validates the target path if existence is required; it will pass the path string directly to the external tool.

Postconditions:
- If the function invoked a platform tool, the corresponding external command has been executed synchronously; ACL entries may have been removed recursively depending on the command's success.
- If the platform is not macOS/Linux or the expected binary is missing, no external command is run and no change is made.

## Side Effects:
- Executes an external process synchronously (blocks until the external command completes).
- Alters filesystem ACL metadata when the invoked command succeeds.
- Does not modify global Python variables or return process results; side effects are limited to the external command effects on the filesystem and any OS-level errors raised when starting the process.

## Control Flow:
flowchart TD
    Start --> CheckPlatform
    CheckPlatform --> |platform == PLATFORM_DARWIN| CheckChmodExists
    CheckPlatform --> |platform == PLATFORM_LINUX| CheckSetfaclExists
    CheckPlatform --> |other| EndNoOp
    CheckChmodExists --> |/bin/chmod exists?| RunChmod
    CheckChmodExists --> |missing| EndNoOp
    RunChmod --> End
    CheckSetfaclExists --> |/bin/setfacl exists?| RunSetfacl
    CheckSetfaclExists --> |missing| EndNoOp
    RunSetfacl --> End
    EndNoOp --> End

## Examples:
- Typical invocation (ignore return value; function performs side-effect):
    Attempt to call the helper with a target path; if starting the external process fails, the calling code can catch and handle the OSError:
    try:
        remove_acl("/var/lib/myapp/data")
    except OSError as e:
        # handle inability to start the external command (permission/OS resource issues)
        handle_start_failure(e)

- Unit-testing guidance (description of approach; concrete test frameworks can use this pattern):
    1. Patch platform.system to return the desired platform constant (PLATFORM_DARWIN or PLATFORM_LINUX).
    2. Patch os.path.isfile so it returns True for the checked binary path (/bin/chmod or /bin/setfacl) and False otherwise.
    3. Patch subprocess.call with a spy/mocked function that records calls.
    4. Call remove_acl with a sample path string.
    5. Assert that subprocess.call was invoked exactly once with the expected argument list:
       - On macOS: [" /bin/chmod", "-R", "-N", "<path>"] (without quotes; exact list order)
       - On Linux: ["/bin/setfacl", "-R", "-b", "<path>"]
    6. Also include tests where os.path.isfile returns False to assert that subprocess.call is not invoked.

Notes on robustness:
- Because the function tests for the binary at a hard-coded absolute path, environments where the tool lives at a different path will not be handled; consider normalizing PATH or extending detection if broader support is required.
- Use mocking to verify behavior in unit tests rather than invoking real /bin/chmod or /bin/setfacl, which would mutate the test filesystem.

## `mackup.utils.remove_immutable_attribute` · *function*

## Summary:
Clear platform-specific immutable file/directory attributes for a given path by calling the appropriate system utility (macOS: chflags, Linux: chattr) when available; a best-effort, no-return operation.

## Description:
This small utility centralizes the logic for removing immutable attributes that can prevent modification or deletion of files and directories. It:
- Checks the current OS via platform.system() and compares it to constants.PLATFORM_DARWIN and constants.PLATFORM_LINUX (values provided by the project’s constants module).
- Verifies the existence of the platform-specific external binary at /usr/bin/chflags (macOS) or /usr/bin/chattr (Linux).
- Invokes the external utility with flags to recursively remove immutable attributes from the supplied path.

Known callers within the provided repository snapshot:
    - No callers were discovered in the available snapshot. In typical usage elsewhere in the codebase, callers invoke this function immediately before operations that need to modify or delete files (e.g., before shutil.rmtree or replacing a file).

Why this is extracted:
    - Encapsulates platform detection, binary existence checks, and subprocess invocation in one place so higher-level code does not duplicate OS-specific knowledge or subprocess details. It isolates side effects and makes it easy to adjust commands or add platforms later.

## Args:
    path (str or os.PathLike): Filesystem path (file or directory) whose immutable attribute should be removed. The path will be passed verbatim to the external command; it may be absolute or relative.

## Returns:
    None
    - The function does not return a value; it performs the operation as a best-effort side-effect.
    - The subprocess exit code is ignored by the function; failures of the external utility do not raise inside this function unless the underlying operating system raises an execution error.

## Raises:
    - NameError: If the name `constants` is not defined in the module scope when the function is executed (precondition violation).
    - AttributeError: If `constants` exists but does not expose PLATFORM_DARWIN or PLATFORM_LINUX attributes referenced by the function.
    - TypeError: If `path` is not a valid path-like object (for example, passing None may raise a TypeError when os.path.isfile is invoked).
    - OSError / PermissionError: If invoking the external binary fails at the OS level (for example, the binary cannot be executed due to permissions or other OS-level execution errors). Note: subprocess.call normally does not raise on non-zero exit codes, but OS-level failures can raise.

## Constraints:
Preconditions:
    - The module must provide a `constants` object with attributes PLATFORM_DARWIN and PLATFORM_LINUX. The function compares platform.system() to these attributes; if they are missing or incorrect, the platform branch logic will not behave as intended.
    - The process must have permission to execute the external binary if it exists.
    - The path argument must be a valid filesystem path or path-like object.

Postconditions:
    - If on a platform where platform.system() equals constants.PLATFORM_DARWIN and /usr/bin/chflags exists, the function will have executed: /usr/bin/chflags -R nouchg <path>.
    - If on a platform where platform.system() equals constants.PLATFORM_LINUX and /usr/bin/chattr exists, the function will have executed: /usr/bin/chattr -R -f -i <path>.
    - If neither platform matches or the respective binary is missing, the function performs no actions.
    - The operation is best-effort and does not guarantee that immutable attributes were successfully removed — success depends on the external tool’s exit status and system privileges.

## Side Effects:
    - Executes an external command which modifies filesystem metadata:
        * macOS branch: /usr/bin/chflags -R nouchg <path>
        * Linux branch: /usr/bin/chattr -R -f -i <path>
    - No Python-level global state is modified.
    - No files are directly created, written, or removed by this function itself; the side effects are performed by the external utilities.

## Control Flow:
flowchart TD
    Start --> GetPlatform
    GetPlatform -->|platform == constants.PLATFORM_DARWIN| CheckChflags
    GetPlatform -->|platform == constants.PLATFORM_LINUX| CheckChattr
    GetPlatform -->|other| End
    CheckChflags -->|/usr/bin/chflags exists| CallChflags
    CheckChflags -->|missing| End
    CheckChattr -->|/usr/bin/chattr exists| CallChattr
    CheckChattr -->|missing| End
    CallChflags --> End
    CallChattr --> End

## Examples:
Example 1 — Defensive usage before deleting a directory:
    import logging
    import shutil

    logging.basicConfig(level=logging.INFO)
    try:
        remove_immutable_attribute("/var/myapp/backups")
    except (NameError, AttributeError, TypeError, OSError) as exc:
        logging.warning("Could not clear immutable attribute on backups: %s", exc)
    # Proceed with deletion attempt (may still fail if immutable removal did not succeed)
    try:
        shutil.rmtree("/var/myapp/backups")
    except Exception as exc:
        logging.error("Failed to remove backups directory: %s", exc)

Example 2 — Best-effort cleanup before replacing a file:
    # Typical caller:
    remove_immutable_attribute("config/settings.json")
    # Continue to open/overwrite the file; if immutable attributes remain, the operation may raise.

Notes and implementation hints (for reimplementation):
    - The original implementation checks the exact path /usr/bin/chflags and /usr/bin/chattr. Replicate this behavior if you want identical semantics; alternatively, consider searching PATH or using shutil.which to be more flexible.
    - The function currently ignores subprocess return codes. If callers require certainty that attributes were removed, consider switching to subprocess.check_call and handling CalledProcessError.
    - Preserve the recursive (-R) flag to apply changes to directories and their contents.
    - Typical values for the platform constants correspond to platform.system() output: 'Darwin' for macOS and 'Linux' for Linux. Ensure the constants module uses matching strings or adapt comparisons accordingly.
    - The function is idempotent: calling it multiple times for the same path is harmless.

## `mackup.utils.can_file_be_synced_on_current_platform` · *function*

## Summary:
Decides whether a given path (joined to the user's HOME when relative) is eligible to be synced on the current platform; currently excludes items under the user's HOME/Library directory when running on Linux-like platforms.

## Description:
This small utility returns a boolean that indicates whether a file or directory should be considered for synchronization on the running platform. The only implemented exclusion rule is: if the current platform equals the module-level constant constants.PLATFORM_LINUX and the resolved path is located under HOME/Library/, then the path is not allowed to be synced (returns False). All other paths return True.

Known callers in the provided context:
- No direct callers were found in the provided source context. Typically this function is used as a pre-filter during a sync/backup pipeline that iterates candidate paths and skips those for which this function returns False.

Why this logic is extracted:
- Extracting platform-specific exclusion rules centralizes the decision, making it easier to test, extend (add other platform rules), and keep call sites free from platform-detection logic. It enforces the single responsibility: given a path and the current runtime platform, answer whether it is safe/appropriate to sync that path.

## Args:
    path (str):
        - A filesystem path to evaluate. Can be relative or absolute.
        - If relative: the function joins it to os.environ["HOME"] using os.path.join (i.e., fullpath = os.path.join(HOME, path)). The HOME environment variable must exist.
        - If absolute (os.path.isabs(path) is True), os.path.join will return the absolute path unchanged on POSIX-like platforms; the function therefore evaluates the absolute path directly.
        - Type constraint: must be a str. Passing non-str types (None, bytes on Python 3, etc.) will likely raise a TypeError.

## Returns:
    bool:
        - True: the file is allowed to be synced according to the implemented rule(s).
        - False: the file should not be synced. Under current logic, this occurs only when:
            * platform.system() equals constants.PLATFORM_LINUX, and
            * the computed full path starts with os.path.join(HOME, "Library/").
        - No other return values are used.

## Raises:
    KeyError:
        - Raised when the HOME environment variable is not set and os.environ["HOME"] is accessed. The function does not catch this.

    NameError:
        - Raised if the name constants is not defined in the module namespace when the function attempts to refer to constants.PLATFORM_LINUX.

    AttributeError:
        - Raised if the module-level name constants exists but does not define PLATFORM_LINUX (i.e., accessing constants.PLATFORM_LINUX fails).

    TypeError:
        - Possible if the provided path is not a str and os.path.join or fullpath.startswith is invoked with an incompatible type.

## Constraints:
Preconditions:
    - HOME must be defined in the environment when calling with a relative path.
    - constants must be available in the module namespace and define PLATFORM_LINUX for the platform comparison to work as intended.
    - Callers should pass a str for path.

Postconditions:
    - No global state or files are modified.
    - The function deterministically returns a boolean based solely on environment variables, platform.system(), and the string value of the provided path.

## Side Effects:
    - Reads the HOME environment variable (os.environ["HOME"]).
    - Calls platform.system() — this queries the runtime but does not mutate any state.
    - No filesystem I/O, network access, or external state mutation occurs.

## Implementation caveats (important for callers / reimplementers):
    - The function uses os.path.join and a string startswith check to decide membership in HOME/Library/. It does not resolve symbolic links, nor does it normalize '.' or '..' segments. If callers must correctly handle symlinks or canonical paths, they should normalize inputs (e.g., os.path.normpath or os.path.realpath) before calling.
    - startswith is a plain string comparison and is case-sensitive; behavior will vary by platform and filesystem (Linux: case-sensitive; Windows: case-insensitive). If case-insensitive matching is desired on case-insensitive filesystems, callers should normalize case before invoking.
    - On Windows, path separators and drive letters must be considered; absolute paths may start with a drive letter (e.g., "C:\\") and os.path.join semantics differ — reimplementers should use os.path.isabs to detect absolute inputs if needed.
    - The function expects constants.PLATFORM_LINUX to contain the same string returned by platform.system() for Linux-like systems (commonly "Linux"), but the exact value depends on the project's constants module.

## Control Flow:
flowchart TD
    Start[Start: call with path (str)] --> CheckHOME{HOME in os.environ?}
    CheckHOME -- no --> RaiseKeyError[Raise KeyError]
    CheckHOME -- yes --> ComputeFullpath[fullpath = os.path.join(HOME, path)]
    ComputeFullpath --> PlatformCheck{platform.system() == constants.PLATFORM_LINUX?}
    PlatformCheck -- no --> ReturnTrue[return True]
    PlatformCheck -- yes --> StartsWithLib{fullpath.startswith(HOME/Library/)?}
    StartsWithLib -- yes --> ReturnFalse[return False]
    StartsWithLib -- no --> ReturnTrue

## Examples:
Note: these examples assume HOME is set and constants.PLATFORM_LINUX corresponds to the Linux platform string expected by the project.

1) Relative path on Linux under HOME/Library:
    # os.environ["HOME"] == "/home/alice"
    # platform.system() == constants.PLATFORM_LINUX
    can_file_be_synced_on_current_platform("Library/Application Support/com.example")  # -> False

2) Relative path on non-Linux:
    # platform.system() != constants.PLATFORM_LINUX
    can_file_be_synced_on_current_platform("Library/Application Support/com.example")  # -> True

3) Absolute path input (evaluated directly):
    can_file_be_synced_on_current_platform("/home/alice/Library/Preferences/foo")  # -> False on Linux

4) Recommended caller pattern to avoid path-normalization pitfalls:
    import os
    p = os.path.normpath(os.path.join(os.environ["HOME"], "Library/Preferences/../Application Support/foo"))
    # Pass normalized absolute path or normalize inside caller
    allowed = can_file_be_synced_on_current_platform(os.path.relpath(p, os.environ["HOME"]))

5) Error handling:
    try:
        allowed = can_file_be_synced_on_current_platform("some/relative/path")
    except KeyError:
        # HOME missing; decide fallback behavior (e.g., treat as not allowed or skip)
        allowed = False
    except (NameError, AttributeError):
        # constants or constants.PLATFORM_LINUX missing; treat conservatively or re-raise after logging
        raise

