# `mackup.py`

## `mackup.mackup.Mackup` · *class*

*No documentation generated.*

### `mackup.mackup.Mackup.__init__` · *method*

## Summary:
Initializes the Mackup instance by creating and storing a Config snapshot and allocating a unique temporary working directory; sets attributes used by other Mackup methods.

## Description:
Known callers and lifecycle:
- No explicit call-sites are available in this module snapshot. In typical usage the constructor is invoked during program startup by the top-level command-line entry point or by higher-level orchestration code that prepares and runs backup/restore operations. Unit tests that exercise Mackup behavior will also instantiate this class directly.
- This method is executed at object construction time (early in the object's lifecycle) to establish the configuration surface and an isolated filesystem workspace before any backup or restore operations run.

Why this is a separate method:
- Initialization concerns (reading/validating configuration and creating a temporary workspace) are setup actions that logically belong to the object's constructor. Keeping them inside __init__ centralizes required state creation, ensures the instance invariants are established before use, and makes the construction step easy to reason about and test.

## Args:
- None

## Returns:
- None (constructors in Python return None implicitly). After returning, the instance has the three attributes documented below initialized.

## Raises:
Direct or indirect exceptions that can propagate from this initialization code:
- ConfigError (custom): raised by config.Config() during parsing/validation if the configuration content is invalid (see config.Config documentation for exact triggers).
- KeyError: may be raised indirectly by config.Config() if it attempts to read os.environ["HOME"] and HOME is not set.
- AssertionError: may be raised indirectly by config.Config() if its constructor is given an invalid type for a filename (not directly relevant here because no argument is passed, but documented because it can originate from Config internals).
- SystemExit: config.Config() or provider-discovery helpers invoked during Config construction may call a fatal error routine that exits the process (utils.error(...) → sys.exit). This will terminate the process rather than raise a normal exception.
- OSError (or subclasses, e.g. PermissionError): raised by tempfile.mkdtemp() if the temporary directory cannot be created (insufficient permissions, no space, invalid temp directory base, etc).

Note: All exceptions except those coming from tempfile.mkdtemp originate from the Config construction and its helper routines; consult config.Config documentation for more detail.

## State Changes:
Attributes READ:
- None of self.<attr> values are read prior to assignment within this method.

Attributes WRITTEN:
- self._config (object): assigned to a new config.Config() instance.
- self.mackup_folder (str): assigned the string returned by self._config.fullpath (the resolved backup root path).
- self.temp_folder (str): assigned the pathname of a newly-created temporary directory returned by tempfile.mkdtemp(...).

## Constraints:
Preconditions:
- No parameters are required, but successful construction commonly assumes the environment is sane:
  - The HOME environment variable should be set (config.Config may access os.environ["HOME"] and will raise KeyError if missing).
  - The process must have permission to create a temporary directory in the system temp location, or tempfile.mkdtemp will raise OSError.

Postconditions:
- On successful return (no exception), the instance satisfies:
  - self._config is an instantiated Config object (a snapshot of runtime configuration).
  - self.mackup_folder is a string equal to self._config.fullpath.
  - self.temp_folder is a string path to a directory that exists on the filesystem and is owned/created by this process (created by tempfile.mkdtemp).
- No cleanup of the temporary directory is performed here; callers or other methods are responsible for removing it when appropriate.

## Side Effects:
- Filesystem: creates a new temporary directory on the host filesystem via tempfile.mkdtemp(prefix="mackup_tmp_"). The directory remains until explicitly removed.
- Configuration parsing: instantiating config.Config() may perform filesystem reads (reading the user's config file) and may exit the process via utils.error(...) in certain error conditions (SystemExit).
- No network I/O is performed directly by this method, but config.Config() may call provider-discovery helpers which in turn may perform platform-specific file-system checks.

### `mackup.mackup.Mackup.check_for_usable_environment` · *method*

## Summary:
Ensure the running environment is safe for Mackup operations by aborting early when running as root is disallowed or when the configured storage folder does not exist. If checks pass, the method returns normally (None); otherwise it terminates the process.

## Description:
Known callers and context:
- check_for_usable_backup_env: invoked during the pre-backup validation step (backup setup pipeline). This caller runs this check before attempting to create or use the Mackup storage/home.
- check_for_usable_restore_env: invoked during the pre-restore validation step (restore setup pipeline). This caller runs this check before attempting to read from the Mackup storage.
- Typical lifecycle: Called early in backup/restore command flows to validate that the process is not running in a dangerous context and that required storage directories are present.

Why this is a separate method:
- Centralizes environment safety checks used by multiple workflows (backup and restore).
- Keeps backup/restore setup code concise and avoids duplicating the same guard logic.
- Encapsulates process-termination behavior in one place for easier maintenance and testing.

## Args:
    None

## Returns:
    None
    - Returns normally (implicitly None) only when:
        * Either the current effective user ID is not root, or running as root is explicitly permitted by utils.CAN_RUN_AS_ROOT.
        * AND the configured storage path (self._config.path) exists and is a directory.
    - Edge-case return: the function never returns a meaningful value; its purpose is validation and (on failure) to exit the process.

## Raises:
    SystemExit
    - Triggered by calling utils.error(...) in two failure cases:
        1) If os.geteuid() == 0 (process running as root) and utils.CAN_RUN_AS_ROOT is falsy — utils.error prints a red "Error:" message and calls sys.exit.
        2) If os.path.isdir(self._config.path) is False — utils.error prints a red "Error:" message with the missing path and calls sys.exit.
    Possible implementation-specific exceptions (not explicitly raised by this method but possible at runtime):
    - AttributeError: if self._config is missing or lacks the .path attribute.
    - AttributeError: on non-POSIX platforms where os.geteuid does not exist (calling os.geteuid would raise AttributeError). The code does not guard against this; callers on such platforms should ensure compatibility.

## State Changes:
    Attributes READ:
    - self._config.path
    - (indirectly reads) utils.CAN_RUN_AS_ROOT
    Attributes WRITTEN:
    - None (this method does not modify any self attributes)

## Constraints:
    Preconditions:
    - self._config must be set and must expose a .path attribute (a string or path-like object).
    - The runtime should support os.geteuid (POSIX) or callers must ensure behavior is acceptable on non-POSIX systems.
    Postconditions:
    - If the method returns normally, the object is in a state where:
        * Running as root is either not the case, or is explicitly permitted.
        * The configured storage folder exists and is a directory.
    - If a precondition fails, the method will not return normally; it will call utils.error (which exits the process).

## Side Effects:
    - May terminate the process by calling utils.error(...), which prints a colored error message and calls sys.exit (raising SystemExit).
    - Calls os.geteuid() to determine the effective user id.
    - Calls os.path.isdir(...) to check the existence/type of the configured storage folder.
    - No filesystem mutations or network I/O are performed by this method itself.

### `mackup.mackup.Mackup.check_for_usable_backup_env` · *method*

## Summary:
Performs the two-step backup-environment preparation by sequentially invoking the instance helpers check_for_usable_environment and create_mackup_home; this method itself performs no direct computation or I/O beyond calling those helpers.

## Description:
This is a thin delegator that runs two helper methods in sequence:
1. Calls self.check_for_usable_environment().
2. Calls self.create_mackup_home().

Known callers and context:
- No callers were discovered in the provided source fragment. Conceptually, this method is intended to be called during backup setup or initialization by higher-level backup orchestration code before beginning backup operations.

Why this is a separate method:
- The method centralizes the two-step preparation sequence so callers need only invoke one method to perform both required setup steps and so the invocation order is enforced in a single place.

## Args:
    None

## Returns:
    NoneType
    - The method returns None on successful completion.

## Raises:
    - Propagates any exception raised by self.check_for_usable_environment().
    - If the first call completes successfully, propagates any exception raised by self.create_mackup_home().
    - This method does not catch, wrap, or suppress exceptions from either helper.

## State Changes:
    Attributes READ:
        - None directly read by this method implementation.

    Attributes WRITTEN:
        - None directly written by this method implementation.

    Note: Any attribute reads or writes are performed by the delegated helper methods; this wrapper invokes them but does not itself access self.<attr>.

## Constraints:
    Preconditions:
        - The instance must have callable attributes named check_for_usable_environment and create_mackup_home.
        - Any state those helper methods require (configuration attributes, paths, etc.) must be prepared by the caller or earlier initialization.

    Postconditions:
        - If the method returns without raising, both helper methods have been invoked and completed successfully.
        - If self.check_for_usable_environment() raises, self.create_mackup_home() will not be invoked.
        - If the first helper succeeds but the second raises, the system may be left in a partially-prepared state (observable effects depend entirely on the helpers' implementations).

## Side Effects:
    - This method performs no direct I/O or filesystem operations itself; any I/O or external effects result from the helper methods it calls.
    - Exceptions from the helpers propagate to the caller of this method.

### `mackup.mackup.Mackup.check_for_usable_restore_env` · *method*

## Summary:
Performs environment validation for a restore operation by running shared environment checks and verifying the Mackup storage folder exists; on failure it aborts the process via SystemExit.

## Description:
Known callers and context:
    - No direct callers of this method were found in the provided class memory. Conceptually, this method belongs to the start of the restore workflow and should be invoked before any restore actions attempt to read from the Mackup storage folder (for example, by a CLI restore command or a restore orchestration function).
    - This method is separate to keep restore-specific validation (existence of the Mackup folder) distinct from shared environment checks used by both backup and restore flows.

Why this logic is a separate method:
    - It composes a generic environment safety check (check_for_usable_environment) with a restore-specific precondition (mackup storage folder exists). This prevents duplication of the generic checks and makes the restore entrypoint explicit and easy to call.

## Args:
    None

## Returns:
    None
    - If the method returns normally, the environment passed validation:
        * check_for_usable_environment completed without triggering utils.error
        * self.mackup_folder exists and is a directory
    - The method does not return on error conditions because it calls utils.error which exits the process (raises SystemExit).

## Raises:
    SystemExit (via utils.error)
    - Triggered in any of these exact conditions:
        1. check_for_usable_environment triggers utils.error:
            - When running as root and running as root is not allowed:
                * Condition: os.geteuid() == 0 and not utils.CAN_RUN_AS_ROOT
                * Effect: utils.error is called with a message warning against running as superuser
            - When the configured storage folder does not exist:
                * Condition: not os.path.isdir(self._config.path)
                * Effect: utils.error is called with a message "Unable to find the storage folder: {self._config.path}"
        2. The Mackup storage folder required for restore does not exist:
            - Condition: not os.path.isdir(self.mackup_folder)
            - Effect: utils.error is called with a message recommending backing up files or syncing storage
    - Note: utils.error implementation calls sys.exit(...) which raises SystemExit and terminates the process.

## State Changes:
    Attributes READ:
        - self.mackup_folder (checked with os.path.isdir)
        - self._config (check_for_usable_environment reads self._config.path)
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Mackup instance must be initialized so that:
            * self._config exists and has attribute path (string path to configured storage folder).
            * self.mackup_folder is set to a path-like string (typically self._config.fullpath).
        - Caller must be prepared for the method to terminate the process on failure (SystemExit).

    Postconditions:
        - On normal return:
            * The generic environment checks in check_for_usable_environment passed (no utils.error invoked).
            * self.mackup_folder exists and is a directory (os.path.isdir(self.mackup_folder) is True).
        - If any precondition is violated, the process will have exited via SystemExit.

## Side Effects:
    - May terminate the running Python process by calling utils.error -> sys.exit (SystemExit).
    - Performs only read-only filesystem checks (os.path.isdir); it does not create, modify, or delete any filesystem entries itself.
    - Indirectly relies on check_for_usable_environment which reads os.geteuid() and inspects self._config.path; failures there also call utils.error and terminate the process.

### `mackup.mackup.Mackup.clean_temp_folder` · *method*

## Summary:
Removes the temporary directory created for this Mackup instance from the filesystem, performing destructive cleanup of the temporary workspace while leaving the object's attributes unchanged.

## Description:
Known callers and context:
    - No internal callers exist within the Mackup class; this method is intended to be invoked by external orchestration code or higher-level workflows that manage backup/restore operations.
    - Typical lifecycle stage: final cleanup step after a completed backup or restore operation, or inside an error/recovery path (for example in a finally block) to ensure temporary files do not persist.
    - Creation context: self.temp_folder is initialized in Mackup.__init__ using tempfile.mkdtemp(prefix="mackup_tmp_"), so it normally points to a dedicated temporary directory created when the Mackup instance is constructed.

Why this is a separate method:
    - Encapsulates filesystem teardown in a single discoverable location, simplifying testability and mocking.
    - Keeps cleanup logic separate from business logic so callers can decide whether and when to run it (normal completion vs. error cleanup).

## Args:
    None

## Returns:
    None
    - Successful return indicates the directory tree at the path stored in self.temp_folder has been removed. The method does not provide a status value.

## Raises:
    - Propagates filesystem-level exceptions raised by shutil.rmtree called with self.temp_folder:
        * FileNotFoundError: when the path referenced by self.temp_folder does not exist at call time.
        * PermissionError: when the process does not have the permission required to remove files or directories under self.temp_folder.
        * NotADirectoryError: when the given path exists but is not a directory (or related OS error).
        * OSError: for other OS-level errors during traversal or removal (e.g., I/O errors, filename too long).
    - The method does not catch or translate exceptions; callers that require tolerant behavior should perform existence checks or catch these exceptions.

## State Changes:
    Attributes READ:
        - self.temp_folder (str): read to determine which filesystem tree to remove.
    Attributes WRITTEN:
        - None. The attribute self.temp_folder is not modified by this method and will continue to hold the same string value after the call (even though that path may no longer exist on disk).

## Constraints:
    Preconditions:
        - self.temp_folder should be a non-empty string containing a valid filesystem path that the process expects to own or manage.
        - The process must have sufficient permissions to remove files and directories under self.temp_folder.
        - The caller should avoid calling this method concurrently from multiple threads/processes for the same Mackup instance unless synchronization is provided externally.
    Postconditions:
        - On normal completion (no exception), the filesystem tree rooted at the path stored in self.temp_folder has been removed.
        - The object retains the original value of self.temp_folder (which will typically point to a non-existent path after removal). If callers intend to reuse a temporary directory after cleanup, they must create and assign a new path to self.temp_folder explicitly.

## Side Effects:
    - Destructive I/O: permanently deletes the directory tree at self.temp_folder and all contained files and subdirectories.
    - May impact other processes if the directory is shared; ensure the path is exclusively used for this instance's temporary data.
    - No network or external service calls are made.
    - No modification of other in-memory objects or Mackup attributes beyond the filesystem mutation described above.

### `mackup.mackup.Mackup.create_mackup_home` · *method*

## Summary:
Ensure the configured Mackup storage directory exists on disk: if it is missing, interactively prompt the user to create it; on success the folder exists, otherwise the process exits or an error is raised.

## Description:
Known callers and context:
- check_for_usable_backup_env(): called during preparation for a backup operation to guarantee that the configured storage folder exists before attempting to save configuration data.
- Lifecycle stage: environment validation step executed during startup of backup/backup-related flows; it runs after basic environment checks and before any operations that assume the storage directory exists.

Why this is a separate method:
- Isolates interactive prompting and filesystem-creation logic from broader environment checks so the behavior can be reused, tested, or modified independently.
- Keeps higher-level validation methods concise and focused on sequencing, delegating user interaction and creation details to this method.

## Args:
    None

## Returns:
    None
    - Normal return (None) means the method completed and os.path.isdir(self.mackup_folder) is True (either the directory already existed or was created by this method).
    - If the user declines creation, the method does not return normally; it triggers process termination (SystemExit) via utils.error.
    - If an unexpected filesystem or input error occurs, the corresponding exception propagates (see Raises).

## Raises:
    SystemExit
        - Triggered when the configured mackup folder does not exist and the user explicitly declines to create it. This occurs because utils.error calls sys.exit(...) which raises SystemExit and terminates the process.
    EOFError, KeyboardInterrupt
        - May be raised by utils.confirm because it calls input(...). These propagate out of this method if the user sends EOF (Ctrl-D) or interrupts (Ctrl-C) during the prompt.
    OSError (including subclasses such as PermissionError, FileExistsError)
        - Any filesystem error raised by os.makedirs may propagate. Examples:
            * PermissionError: insufficient permissions to create the directory.
            * FileExistsError: a race condition where the directory is created between the isdir check and os.makedirs (on Python versions where os.makedirs raises for existing paths).
            * OSError if the target path is invalid (e.g., parent is a file) or other low-level FS errors.
        - These errors are not caught within the method and will surface to the caller.

## State Changes:
Attributes READ:
    - self.mackup_folder: read to determine the path to check/create.

Attributes WRITTEN:
    - None on the Python object itself (no attributes of self are reassigned).
    - External state mutated: a directory at self.mackup_folder may be created on the filesystem when the user confirms.

## Constraints:
Preconditions:
    - self.mackup_folder must be a valid path string (set by __init__ from the configuration).
    - Caller must be prepared for interactive behavior and potential process termination (the method prompts the user and may call sys.exit).

Postconditions:
    - If the method returns normally, os.path.isdir(self.mackup_folder) is guaranteed True.
    - If the user declines, the method will not return normally; SystemExit will be raised and the process will terminate.
    - If an exception from input() or os.makedirs occurs, it will propagate to the caller.

## Behavior details and prompt text:
    - If os.path.isdir(self.mackup_folder) is True at the start, the method is a no-op and returns immediately without prompting.
    - If the directory does not exist, the method calls utils.confirm(question) with the question string:
        "Mackup needs a directory to store your configuration files\nDo you want to create it now? <{self.mackup_folder}>"
      utils.confirm will append " <Yes|No> " and read from stdin; if a global FORCE_YES is set in utils, confirm may return True without prompting.
    - On a True response, the method calls os.makedirs(self.mackup_folder) to create the directory (default mkdir semantics; exist_ok is not used).
    - On a False response, the method calls utils.error(...) which prints a colored error message and exits the process (SystemExit).

## Side Effects:
    - Interactive prompt via utils.confirm (reads from stdin).
    - Potential creation of a directory at self.mackup_folder using os.makedirs (filesystem mutation).
    - Possible process termination via utils.error (sys.exit).
    - Possible propagation of input-related or filesystem-related exceptions to the caller.

### `mackup.mackup.Mackup.get_apps_to_backup` · *method*

## Summary:
Compute and return the set of application identifier keys to back up by using the configured include-list when non-empty or discovering available apps otherwise, then removing any configured ignores; if a mutable set is supplied in the configuration, that set may be mutated (items removed).

## Description:
Known callers and call context:
- Invoked during the backup preparation stage to determine which per-application configuration templates will be processed by the backup operation. It is called after Mackup has been instantiated and configuration (self._config) is loaded, and before the code that iterates apps to collect files.
- Typical pipeline: instantiate Mackup -> load config -> call get_apps_to_backup() -> iterate returned set for per-app backup work.

Why this logic is a separate method:
- Encapsulates selection policy (prefer explicit sync list vs. auto-discovery, then apply ignores) so callers don't duplicate the include/exclude logic.
- Keeps backup orchestration code focused on processing apps and makes this selection logic easy to unit-test in isolation.
- Centralizes the dependency on ApplicationsDatabase construction and the interaction with config attributes.

## Args:
(None)

## Returns:
set[str]
- The set of application identifier strings (machine keys derived from .cfg filenames) that should be backed up.
- Construction rules:
    - If self._config.apps_to_sync is truthy (e.g., a non-empty set), that object is used directly as the initial apps_to_backup.
    - If self._config.apps_to_sync is falsy (None, False, an empty set, or empty container), a freshly returned set from ApplicationsDatabase().get_app_names() is used instead.
- Post-filtering:
    - For each name in self._config.apps_to_ignore, the method calls discard(name) on apps_to_backup to remove it.
    - If an ignored name is not present in apps_to_backup, discard is a no-op (no exception).
- Edge cases:
    - If there are no available apps or all are removed by ignores, an empty set is returned.
    - If self._config.apps_to_sync is the initial set and is mutable, the same object is returned after potential mutation (see State Changes).

## Raises:
- Any exception raised during ApplicationsDatabase construction or discovery will propagate:
    - ValueError: propagated from ApplicationsDatabase (e.g., malformed .cfg entries, invalid XDG path).
    - configparser.NoSectionError / configparser.NoOptionError (or equivalent): if required options are missing while parsing .cfg files during ApplicationsDatabase init.
    - KeyError: e.g., missing HOME environment variable used by ApplicationsDatabase.get_config_files().
    - OSError / FileNotFoundError: filesystem access errors during app descriptor discovery.
- AttributeError:
    - If self._config.apps_to_sync is truthy but is not a set-like object implementing discard(name), an AttributeError will occur when discard is attempted. This indicates the config provided an incompatible type (e.g., list or tuple) for apps_to_sync.

NOTE: This method does not catch or translate any of these exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
- self._config.apps_to_sync
- self._config.apps_to_ignore

Attributes WRITTEN:
- No Mackup attributes (no self.<attr>) are reassigned by this method.

Mutations to referenced objects:
- If self._config.apps_to_sync is truthy and is a mutable set object, this method will call discard(...) on that same set object for each ignored name. As a result, the contents of self._config.apps_to_sync may be changed (elements removed). If apps_to_sync is falsy, no mutation of configuration occurs because a fresh set returned by ApplicationsDatabase is used and only that local/returned set is modified.

## Constraints:
Preconditions:
- self._config must exist and expose:
    - apps_to_sync: either falsy (None or empty container) or a set-like mutable container of strings. If truthy and intended to be used in-place, it must implement discard(str).
    - apps_to_ignore: an iterable (possibly empty) of string app keys.
- Environment prerequisites required by ApplicationsDatabase: readable builtin apps directory, $HOME environment variable, and any filesystem permissions needed to read .cfg files.

Postconditions:
- The returned set contains all discovered or configured app keys except those present in self._config.apps_to_ignore.
- If a mutable self._config.apps_to_sync was used, its contents reflect removed ignored names (same object mutated).
- No other Mackup attributes are modified.

## Side Effects:
- Instantiates ApplicationsDatabase(), which performs local filesystem I/O to discover and parse .cfg application descriptors. That I/O can read files and raise the exceptions listed above.
- May mutate the set object referenced by self._config.apps_to_sync if it is used as the initial apps_to_backup and is mutable.
- Allocates and returns a set object if discovery is used; otherwise returns the existing apps_to_sync set object.
- No network calls or external services are invoked by this method itself.

