# `application.py`

## `mackup.application.ApplicationProfile` · *class*

*No documentation generated.*

### `mackup.application.ApplicationProfile.__init__` · *method*

## Summary:
Initializes an ApplicationProfile instance by validating inputs and storing a reference to the Mackup manager, a list of files (converted from the provided set), and the run flags; this sets up the object's internal state for subsequent profile operations.

## Description:
- Known callers:
    - No specific callers were present in the provided code snapshot. Typically, ApplicationProfile objects are constructed by higher-level profile-management or command-handling code when preparing to back up, restore, or enumerate application-specific configuration files.
- Lifecycle/context:
    - This constructor is invoked at object creation time to prepare an ApplicationProfile instance before any profile operations (e.g., collection, backup, restore, or listing) are performed.
- Why this method exists:
    - The constructor centralizes the validation and assignment of core attributes (manager reference, files, and flags). Keeping this logic in __init__ ensures all instances start in a consistent, validated state and avoids repeating validation in other methods.

## Args:
    mackup (Mackup): A Mackup manager instance. The constructor asserts that this argument is an instance of the Mackup class imported from mackup.
    files (set): A set containing the files to include in this profile. The constructor asserts that this argument is of type set and converts it to a list for internal storage. Element types are not enforced here by code, but callers should pass a set of file path strings.
    dry_run (bool): Flag indicating whether operations performed using this profile should be a dry run (no destructive changes). The code accepts and stores this value; boolean True/False is expected.
    verbose (bool): Flag indicating whether verbose logging/output should be enabled for operations using this profile. The code accepts and stores this value; boolean True/False is expected.

## Returns:
    None. As a constructor, it does not return a value; it initializes the instance in-place.

## Raises:
    AssertionError: Raised if the first argument is not an instance of Mackup.
    AssertionError: Raised if the second argument is not a set.

## State Changes:
- Attributes READ:
    - None (the constructor does not read any existing self.<attr> attributes).
- Attributes WRITTEN:
    - self.mackup: set to the provided Mackup instance
    - self.files: set to list(files) — a new list created from the provided set; order is unspecified
    - self.dry_run: set to the provided dry_run value
    - self.verbose: set to the provided verbose value

## Constraints:
- Preconditions:
    - The caller must provide a valid Mackup instance for the first parameter.
    - The caller must provide a set for the files parameter.
    - dry_run and verbose are expected to be boolean flags (the code does not enforce this with assertions).
- Postconditions:
    - After return, the instance has the four attributes (mackup, files, dry_run, verbose) assigned.
    - self.files is a list whose elements are the members of the input set; because the input was a set, the resulting list order is not deterministic.

## Side Effects:
    - No I/O, no file system or network activity is performed.
    - No external services are called.
    - No objects outside of self are mutated by this method.

### `mackup.application.ApplicationProfile.getFilepaths` · *method*

## Summary:
Returns the pair of filesystem paths for a given application file: the path inside the user's HOME and the corresponding path inside Mackup's storage folder. This does not modify object state.

## Description:
Known callers and context:
- ApplicationProfile.backup — called while iterating files to construct the source (home) and destination (mackup) paths before backing up a file or folder.
- ApplicationProfile.restore — used when linking or restoring backed-up items to compute the home and backup paths.
- ApplicationProfile.uninstall — used to compute paths when reverting backups back into the home directory.

This logic is extracted into its own method to centralize the home↔mackup path construction (avoids duplicating os.path.join logic in multiple places) and to provide a single place to document and adjust path semantics (for example, relative vs absolute filename handling).

## Args:
    filename (str or os.PathLike): Relative path (recommended) or filename of the item being synchronized.
        - Expected to be the path fragment used in both HOME and Mackup storage (for example, ".config/app/settings.json" or "some/folder").
        - If an absolute path is passed (starts with a path separator), os.path.join semantics apply: the absolute filename will replace the preceding directory component (i.e., the HOME-based path will effectively be the absolute filename).

## Returns:
    tuple[str, str]: A 2-tuple (home_filepath, mackup_filepath)
        - home_filepath: The result of joining os.environ["HOME"] with filename (os.path.join(os.environ["HOME"], filename)).
        - mackup_filepath: The result of joining self.mackup.mackup_folder with filename (os.path.join(self.mackup.mackup_folder, filename)).
        - Both elements are native string paths (as produced by os.path.join). No checks are performed on existence, type, or permissions — callers must perform filesystem checks.

## Raises:
    KeyError: If the environment variable "HOME" is not present in os.environ (accessed via os.environ["HOME"]).
    AttributeError: If self.mackup is missing or does not provide the attribute mackup_folder (unlikely if ApplicationProfile was constructed correctly).
    TypeError: If filename is of a type that os.path.join does not accept (rare; os.path.join accepts str and os.PathLike).

## State Changes:
    Attributes READ:
        - self.mackup (object) — the Mackup instance attached to this profile
        - self.mackup.mackup_folder (str) — the base path for stored backups
        - os.environ["HOME"] — the HOME environment value
    Attributes WRITTEN:
        - None (no attributes on self are modified)

## Constraints:
    Preconditions:
        - ApplicationProfile must have been initialized with a valid Mackup instance that exposes mackup_folder (ApplicationProfile.__init__ asserts this).
        - filename should generally be a relative path (not start with a path separator) to produce expected HOME and mackup-folder-relative paths.
    Postconditions:
        - Returns two path strings computed using os.path.join. No filesystem operations are performed and no state is mutated.

## Side Effects:
    - None: this method performs pure path computations only. It does not touch the filesystem, perform I/O, or call external services.
    - Note: callers commonly perform filesystem operations (os.path.exists, utils.copy, utils.link, etc.) using the returned paths.

### `mackup.application.ApplicationProfile.backup` · *method*

## Summary:
Back up each listed user file or folder by moving its contents into the mackup backup location and replacing the original with a symlink to the backup (no change to the ApplicationProfile object's attributes).

## Description:
This method iterates over the filenames recorded on this ApplicationProfile and, for each entry, computes the absolute home path and the corresponding backup path inside the mackup folder. For an entry that exists in the user's home as a regular file or directory and is not already a symlink pointing to the backup, the method copies the item into the backup location, removes the original in the home directory, and creates a symlink at the original home path pointing to the backup copy.

Known callers / when it's invoked:
- No direct callers are present within this class file. It is intended to be called by the higher-level mackup orchestration (for example a Mackup controller/CLI command) when the user requests an application-level backup operation.
- It is part of the backup/restore/uninstall lifecycle for an ApplicationProfile: backup is the step that moves live files into the centralized backup location and replaces them with links.

Why this is a separate method:
- The method encapsulates the complete backup workflow (existence checks, prompting, filesystem operations, and verbose logging) for a single application profile. Keeping it separate avoids duplicating these checks across the CLI/controller and groups the file-system semantics (copy/delete/link/confirmation) in one place that depends on ApplicationProfile state.

## Args:
This is an instance method; no explicit arguments besides:
    self (mackup.application.ApplicationProfile): holds the following relevant fields:
        - self.files (list[str]): filenames (relative paths) to process (populated from a set in __init__).
        - self.mackup (Mackup): object providing the mackup_folder attribute used to compute backup paths.
        - self.dry_run (bool): if True, no filesystem-modifying operations are performed.
        - self.verbose (bool): if True, prints extended status messages.

## Returns:
    None
    - The method does not return a value. Effects are observable via filesystem changes and printed output.
    - If dry_run is True, the method returns None without making filesystem changes.

## Raises:
    ValueError:
        - If an existing item at the backup path (mackup_filepath) is neither a regular file, directory, nor symlink, a ValueError("Unsupported file: ...") is raised.
    AssertionError:
        - Underlying utils.copy or other utils functions may assert on argument types or existence (e.g., utils.copy asserts src exists). Those assertions may propagate.
    OSError / IOError / other OS-level exceptions:
        - Any filesystem operation (os.path.* checks, os.remove, shutil operations inside utils, os.symlink) may raise OS-level exceptions (permission denied, I/O errors) which propagate to callers.
    Blocking for user input:
        - If a conflicting backup exists, utils.confirm is called which may block waiting for console input (or return immediately if FORCE_YES is set).

## State Changes:
Attributes READ:
    - self.files
    - self.mackup (read to obtain self.mackup.mackup_folder via getFilepaths)
    - self.verbose
    - self.dry_run
    - environment variable HOME (used by getFilepaths to compute home paths)

Attributes WRITTEN:
    - None. The method does not modify any attributes of self (no assignment to self.<attr>).

## Constraints:
Preconditions:
    - The ApplicationProfile instance must have been constructed correctly: self.mackup is a Mackup instance and self.files is present (the class __init__ asserts these).
    - Each filename in self.files is expected to be a relative path under the user's HOME environment variable; getFilepaths uses os.environ["HOME"] without fallback, so HOME must be present in the environment.
    - The process must have the permissions necessary to read the home items and to create/remove files and create directories/symlinks in both the home and mackup folders.

Postconditions (guarantees after a successful, non-dry run call for each processed filename):
    - If the home path was a regular file or directory and not already a symlink pointing to the backup, and either no backup existed or the user confirmed replacement:
        - A copy of the original content exists at the computed mackup_filepath (utils.copy was called).
        - The original home path no longer contains the original content (utils.delete was called on the home path).
        - A symlink exists at the original home path pointing to the backup path (utils.link was called).
    - If dry_run is True, none of the above filesystem modifications are performed.
    - If the user declines replacement when a backup already exists, the backup and home remain unchanged for that item.
    - If the home path did not exist or was a symlink already pointing to the backup, no changes are made.

## Side Effects:
    - Filesystem mutations:
        - May create directories (parent directories of mackup_filepath or of symlink path) when copying/linking.
        - May copy files or directories into the mackup folder (utils.copy).
        - May delete files or directories from either the mackup folder or the home folder (utils.delete).
        - May create symlinks at the original home paths (utils.link).
    - Console I/O:
        - Prints status messages to stdout; messages vary depending on self.verbose.
        - May prompt the user via utils.confirm which reads from stdin (blocks for user response unless a FORCE_YES override is present).
    - External functions called:
        - utils.copy, utils.delete, utils.link, and utils.confirm are invoked and may carry their own side effects (e.g., permission handling, ACL or immutable attribute removal).

### `mackup.application.ApplicationProfile.restore` · *method*

## Summary:
Restore application files from the mackup backup into the user's home by creating symbolic links from each home path to its backup copy, replacing existing items when the user confirms; does not modify the ApplicationProfile object state.

## Description:
This method iterates the profile's file list and, for each entry, computes the corresponding home path and mackup (backup) path. If a backup exists, the item is supported on the current platform, and the home path is not already a symlink pointing to the backup, the method will (unless dry-run is enabled) create a symlink at the home path that points to the backup. If an item already exists at the home path, the method prompts the user (via utils.confirm) to confirm deletion/replacement; when confirmed it deletes the existing home item and then creates the symlink. If the backup is missing, the method prints a "doing nothing" message under verbose mode.

Known callers / invocation context:
- Called during the "restore" phase of the backup/restore lifecycle when the user asks the tool to restore application files from the mackup repository. Typically invoked by a higher-level restore orchestrator (for example, a Mackup.restore method or the CLI command handler) that constructs an ApplicationProfile and calls this method for each application.

Why this is a separate method:
- Encapsulates per-application restore logic and user interaction (confirmations, verbose output) so that a higher-level orchestrator can operate on profiles without duplicating file-level logic. Separating restore behavior into this method keeps file-system decisions and prompts localized to the profile implementation.

## Args:
This is an instance method and takes no explicit arguments besides self. Relevant self attributes used:
    self.mackup (Mackup): used indirectly by getFilepaths to compute backup folder path.
    self.files (list[str]): filenames (relative paths from HOME) to be restored.
    self.dry_run (bool): when True, no filesystem modifications are performed.
    self.verbose (bool): when True, print more detailed, multi-line progress messages.

## Returns:
    None
    - The method does not return a value; its purpose is to perform filesystem side effects (or print messages).

## Raises:
    ValueError
        - Raised if a path exists at the home location but is neither a regular file, directory, nor symlink. Trigger condition: os.path.exists(home_filepath) is True and none of os.path.isfile(home_filepath), os.path.isdir(home_filepath), or os.path.islink(home_filepath) is True. The message is "Unsupported file: {mackup_filepath}".

    (Indirect / dependency exceptions)
        - Underlying utility functions may raise their own exceptions:
            * utils.link asserts that the target exists and may raise AssertionError or propagate OSError from os.symlink or os.makedirs.
            * utils.delete may raise exceptions from os.remove or shutil.rmtree if removal fails.
        - Input/interaction utilities may raise on IO failure (e.g., input() raising EOFError) — the method does not catch these.

## State Changes:
Attributes READ:
    - self.files: iterated to obtain filenames
    - self.mackup (via getFilepaths): used to build mackup_filepath
    - self.verbose: controls printing format and conditional verbose-only messages
    - self.dry_run: when True, file operations are skipped

Attributes WRITTEN:
    - None. The method does not mutate attributes on self.

## Constraints:
Preconditions:
    - os.environ["HOME"] must be set and refer to the user's home directory (getFilepaths uses HOME).
    - self.mackup must have a valid mackup_folder attribute used to build backup paths.
    - self.files should be a list (or iterable) of relative file paths (strings) that represent locations under HOME and under the mackup_folder.
    - utils.can_file_be_synced_on_current_platform must be callable and return a bool for each filename.

Postconditions (guarantees after a non-dry-run call completes):
    - For each filename where:
        * the backup exists (os.path.isfile or os.path.isdir on mackup_filepath),
        * the file is supported on the current platform, and
        * the home path was not already a symlink pointing to the backup,
      then either:
        - if there was no existing home item: a symbolic link will be present at home_filepath pointing to mackup_filepath; or
        - if there was an existing home item and the user confirmed replacement: the existing item was deleted and replaced by a symlink pointing to mackup_filepath.
    - For filenames where the backup does not exist, or the file is unsupported, or the home path already points to the backup, the method performs no modification to the filesystem (but may print a message in verbose mode).
    - If dry_run is True, the method will not perform delete/link operations; only prints occur.

## Side Effects:
    - stdout writes: prints progress or diagnostic messages. If self.verbose is True, prints multi-line descriptions; otherwise prints single-line messages.
    - User interaction via utils.confirm: prompts the user for confirmation to replace existing home items.
    - Filesystem mutations (when dry_run is False and user confirms where required):
        * Calls utils.delete(home_filepath) to remove existing files/directories/links at home paths.
        * Calls utils.link(mackup_filepath, home_filepath) to create symbolic links (this creates parent directories if needed and performs chmod on the target before linking).
    - No network communication is performed by this method itself.

## Behavior notes and edge cases:
    - A backup is considered present if os.path.isfile(mackup_filepath) or os.path.isdir(mackup_filepath) is True.
    - The method treats home items that are symlinks pointing to the mackup file (os.path.islink(home_filepath) and os.path.samefile(mackup_filepath, home_filepath)) as already-restored and skips them.
    - If home_filepath exists but is not a file, directory, or symlink, the method raises ValueError to avoid undefined behavior.
    - If the home path is a symlink whose target does not exist (a broken link), verbose mode prints a special message recommending a fix; no automatic repair is attempted.
    - Platform-specific file support: utils.can_file_be_synced_on_current_platform may exclude certain paths (for example, files under ~/Library on Linux); such entries are skipped.
    - The method relies on utils.link to assert the target exists; ensure the backup file/directory exists before attempting to link.

### `mackup.application.ApplicationProfile.uninstall` · *method*

## Summary:
Reverts each tracked item that has a backup in Mackup storage by removing the existing item in HOME (if present) and copying the stored backup into its place; does not mutate the ApplicationProfile object.

## Description:
Known callers and context:
- There are no direct callers inside this module. This method is intended to be invoked by higher-level uninstall orchestration (for example, the Mackup controller/CLI) when the user requests to revert installed configuration files back to their backed-up versions.
- Typical lifecycle: After a previous backup/restore cycle produced backups in the Mackup storage folder and items exist in the user's HOME, uninstall is called to revert those HOME items to the backed-up state.

Why this is a separate method:
- Encapsulates the uninstall-specific flow: resolving HOME vs backup paths, deciding whether to act based on filesystem existence, printing verbose vs short progress messages, honoring dry-run behavior, and performing the concrete filesystem operations (delete + copy). Keeping this logic separate avoids duplicating these checks and side-effectful operations in other code paths (backup/restore).

## Args:
    None

## Returns:
    None

## Raises:
    KeyError:
        - If the environment variable "HOME" is not present (getFilepaths accesses os.environ["HOME"]).
    AttributeError:
        - If self.mackup is missing or lacks mackup_folder (getFilepaths will fail).
    AssertionError:
        - Possible from utils.copy if its internal assertions fail (e.g., non-string arguments or src missing). In normal operation these assertions should not trigger because uninstall checks existence before calling utils.copy.
    OSError (or subclasses like PermissionError):
        - Any filesystem error raised by utils.delete (os.remove, shutil.rmtree) or by os.makedirs/os file operations invoked by utils.copy.
    Note:
        - These exceptions are not caught inside uninstall and therefore propagate to the caller.

## Behavior (exact, step-by-step):
For each filename in self.files (self.files is a list initialized in __init__):
1. Compute:
    - home_filepath = os.path.join(os.environ["HOME"], filename)
    - mackup_filepath = os.path.join(self.mackup.mackup_folder, filename)
2. Check whether the backup exists:
    - The code treats a backup as present ONLY if os.path.isfile(mackup_filepath) OR os.path.isdir(mackup_filepath) is True.
    - Important: a symbolic link at mackup_filepath that does not report as file/dir via these checks will be treated as "backup does not exist" (the code does not check os.path.islink for the backup path).
3. If the backup exists (per step 2):
    a. If os.path.exists(home_filepath) is True:
        - If self.verbose is True, print the detailed message (exact formatting):
            "Reverting {mackup_filepath}\n  at {home_filepath} ..."
        - Else print the short message:
            "Reverting {filename} ..."
        - If self.dry_run is True:
            - Skip filesystem actions for this filename and continue to the next (messages have already been printed).
        - Otherwise (not a dry run):
            i. Call utils.delete(home_filepath) — removes ACLs/immutable flags (as implemented) and then removes the file, link, or recursively removes a directory.
            ii. Call utils.copy(mackup_filepath, home_filepath) — creates parent directories for the destination and copies files or directories; uses shutil.copy or shutil.copytree depending on src type.
    b. If os.path.exists(home_filepath) is False:
        - Do nothing (no message is printed in this branch).
4. Else (backup does not exist) and if self.verbose is True:
    - Print the message:
        "Doing nothing, {mackup_filepath} does not exist"

## State Changes:
Attributes READ:
    - self.files (iterated)
    - self.mackup (used by getFilepaths to read mackup.mackup_folder)
    - self.verbose (controls printed messages)
    - self.dry_run (controls whether filesystem mutations occur)
Attributes WRITTEN:
    - None (uninstall does not assign to any self attributes)

## Preconditions:
    - ApplicationProfile must have been constructed correctly (self.mackup is a Mackup instance exposing mackup_folder; self.files was provided as a set and stored as a list by __init__).
    - The environment variable "HOME" must exist.
    - Filenames in self.files are strings or os.PathLike values acceptable to os.path.join.

## Postconditions:
    - For each filename where:
        * mackup_filepath is a file or directory (os.path.isfile or os.path.isdir True), AND
        * home_filepath exists (os.path.exists True), AND
        * self.dry_run is False:
      the original item at home_filepath has been removed (utils.delete) and the backup has been copied into home_filepath (utils.copy). After completion, home_filepath should exist and reflect the content of mackup_filepath (unless a filesystem error occurred).
    - For filenames where dry_run is True, or where the backup does not exist, or where the backup exists but home_filepath does not exist, no filesystem mutation occurs for that filename.
    - No attributes of the ApplicationProfile instance are modified.

## Side Effects:
    - Filesystem operations:
        * utils.delete(home_filepath): may remove files, symbolic links, or directories and will perform any helper cleanup (ACL/immutable attribute removal) implemented by utils.delete.
        * utils.copy(mackup_filepath, home_filepath): will create parent directories for the destination and copy the backup file or directory into place; may set permissions (utils.copy calls chmod on dst).
    - Stdout output via print():
        * Detailed message when verbose and both backup and home exist:
            "Reverting {mackup_filepath}\n  at {home_filepath} ..."
        * Short message when not verbose and both backup and home exist:
            "Reverting {filename} ..."
        * When backup does not exist and verbose is True:
            "Doing nothing, {mackup_filepath} does not exist"
    - No network or external service calls; side effects are limited to the local filesystem and stdout.

## Edge cases and important implementation notes:
    - Backup existence check uses os.path.isfile OR os.path.isdir on the mackup path. Consequently:
        * A symbolic link in the backup folder that is not reported as a regular file or directory by these checks will be considered "not present" for uninstall purposes.
    - Home existence is tested with os.path.exists(home_filepath). Broken symlinks at HOME report as non-existent here and therefore will not be reverted.
    - Printing occurs before the dry-run check; when dry_run is True messages indicate intent but no filesystem mutations occur.
    - utils.copy asserts that the source exists and is a file or directory; because uninstall checks the backup path with isfile/isdir before calling utils.copy, utils.copy's runtime ValueError for unsupported file types should not occur under normal conditions.
    - Any filesystem exception (permission denied, I/O errors) raised by utils.delete or utils.copy will propagate to the caller.
    - To preserve compatibility with existing behavior, a reimplementation must:
        * Use the same existence checks (os.path.isfile/os.path.isdir for backups; os.path.exists for home).
        * Preserve the exact printed strings and multi-line formatting for verbose messages.
        * Honor dry_run by skipping delete/copy while still printing progress messages.

