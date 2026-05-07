# `config.py`

## `mackup.config.Config` · *class*

## Summary:
Represents the application's runtime configuration read from a user config file; encapsulates parsing, validation and convenient accessors for storage engine, storage path, backup directory, and application lists to ignore or explicitly sync.

## Description:
Instantiating this class loads and validates the mackup configuration file from the current user's home directory and exposes a small, read-only configuration surface used by the rest of the program.

Typical callers:
- Command-line entry points or higher-level configuration loaders create a Config() instance early in program startup to determine where backups are stored and which applications to process.
- No factory is required; simply construct with an optional filename to override the default config filename.

Why this abstraction exists:
- Centralizes all config-file parsing logic, defaulting and validation for storage engines and related settings.
- Provides a stable, easy-to-use API (properties) for other modules to obtain storage engine name, resolved storage path, backup directory name, and sets of application names to ignore or sync.

Responsibility boundary:
- Responsible only for reading/parsing and basic validation of the config file. It delegates platform-specific discovery of provider folders (Dropbox/Google Drive/Copy/iCloud) to utility functions.
- Not responsible for performing I/O to backup files, network operations, or persisting configuration changes.

## State:
Instance attributes (private/internal):
- _parser (configparser.SafeConfigParser)
  - Type: configparser.SafeConfigParser
  - Invariant: initialized and has read the target config file from $HOME/filename (filename defaults to MACKUP_CONFIG_FILE).
  - Note: parser may be empty if file not present; code checks for sections/options rather than assuming presence.

- _engine (str)
  - Type: str
  - Valid values: must be one of ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_COPY, ENGINE_ICLOUD, ENGINE_FS (these are constants imported from constants).
  - Invariant: always a string belonging to the allowed set; otherwise construction raises ConfigError.

- _path (str)
  - Type: str
  - Meaning: absolute path to the root folder used to store/read backups for the selected engine.
  - Invariant: must be a valid string returned by either:
      - the get_*_folder_location() utilities for provider engines (Dropbox, Google Drive, Copy, iCloud), or
      - for ENGINE_FS the path formed by joining $HOME and the 'path' option from the storage section in the config file.
  - Note: When the provider discovery utilities cannot determine their folder location they call error(), which exits the process (see Raises).

- _directory (str)
  - Type: str
  - Meaning: name of the subdirectory inside the storage path where mackup stores backups.
  - Default: MACKUP_BACKUP_PATH (imported constant) if 'directory' option is not present.
  - Constraint: cannot be equal to CUSTOM_APPS_DIR; if it is, initialization raises ConfigError.

- _apps_to_ignore (set[str])
  - Type: set of option names (strings)
  - Meaning: names of applications listed under the applications_to_ignore section of the config file; empty set if section absent.

- _apps_to_sync (set[str])
  - Type: set of option names (strings)
  - Meaning: names of applications listed under the applications_to_sync section of the config file; empty set if section absent.

Public read-only properties:
- engine -> str : returns the normalized engine name (string).
- path -> str : returns resolved storage root path string.
- directory -> str : returns storage subdirectory name string.
- fullpath -> str : returns os.path.join(path, directory) as string.
- apps_to_ignore -> set[str] : returns a set copy of _apps_to_ignore.
- apps_to_sync -> set[str] : returns a set copy of _apps_to_sync.

Class invariants:
- engine is always one of the allowed engine constants.
- directory is never equal to CUSTOM_APPS_DIR.
- apps_to_ignore and apps_to_sync are disjoint only if the config enforces it externally; Config makes no automatic resolution — it simply reads sections.

## Lifecycle:
Creation:
- Signature: Config(filename: Optional[str] = None)
  - filename: optional config filename (relative to $HOME); must be a str or None (an AssertionError will be raised otherwise).
  - If filename is falsy (None or empty), MACKUP_CONFIG_FILE is used as the filename.
- Construction performs these steps (in order):
  1. _setup_parser(filename) — constructs a configparser.SafeConfigParser with allow_no_value=True and inline_comment_prefixes=(";", "#") and calls parser.read(os.path.join(os.environ["HOME"], filename)).
     - This will attempt to read the file at $HOME/filename; parser.read is silent if file missing.
     - Accessing os.environ["HOME"] may raise KeyError if HOME not set in the environment.
  2. _warn_on_old_config() — checks for legacy sections ("Allowed Applications", "Ignored Applications"). If found, it calls error(...) which prints a message and exits the process (sys.exit). This is a hard exit, not an exception.
  3. _parse_engine() — reads storage.engine option if present, otherwise defaults to ENGINE_DROPBOX. Validates the engine against the allowed constants; raises ConfigError if unknown.
  4. _parse_path() — resolves the storage path according to engine:
     - For ENGINE_DROPBOX,ENGINE_GDRIVE,ENGINE_COPY,ENGINE_ICLOUD: delegates to respective get_*_folder_location() helper functions. Those helpers call error(...) and exit if the provider folder cannot be discovered.
     - For ENGINE_FS: reads 'storage.path' from config and joins it with $HOME; if missing, raises ConfigError.
  5. _parse_directory() — reads 'storage.directory' or defaults to MACKUP_BACKUP_PATH. Raises ConfigError if directory equals CUSTOM_APPS_DIR.
  6. _parse_apps_to_ignore() and _parse_apps_to_sync() — read the optional sections "applications_to_ignore" and "applications_to_sync" returning sets of option names (empty sets if sections absent).

Usage:
- After construction, consumers call the public properties (engine, path, directory, fullpath, apps_to_ignore, apps_to_sync).
- There is no mutation API; treat instances as immutable snapshots of the config at construction time.

Destruction:
- No explicit cleanup or resource release required. The class does not open persistent handles or register a context manager.

## Method Map:
flowchart LR
    Init[__init__(filename=None)]
    Init --> Setup[_setup_parser(filename)]
    Setup --> Warn[_warn_on_old_config()]
    Warn --> ParseEngine[_parse_engine()]
    ParseEngine --> ParsePath[_parse_path()]
    ParsePath --> ParseDir[_parse_directory()]
    ParseDir --> ParseIgnore[_parse_apps_to_ignore()]
    ParseDir --> ParseSync[_parse_apps_to_sync()]
    ParseIgnore --> Ready[instance ready — properties available]
    ParseSync --> Ready

Notes:
- Utility functions (get_dropbox_folder_location, get_google_drive_folder_location, get_copy_folder_location, get_icloud_folder_location) are invoked by _parse_path depending on engine; these can call error(...) and terminate the process.

## Raises:
Exceptions and exit behaviors that may occur during construction:
- AssertionError
  - Trigger: filename passed to __init__ is not a str and not None.
- KeyError
  - Trigger: os.environ["HOME"] access when HOME is not present in environment (happens in _setup_parser and for ENGINE_FS path handling).
- ConfigError (custom)
  - Trigger 1: _parse_engine raises ConfigError when the configured engine value (from storage.engine) is not one of the allowed ENGINE_* constants.
  - Trigger 2: _parse_path raises ConfigError when engine == ENGINE_FS and the storage.path option is missing in the config.
  - Trigger 3: _parse_directory raises ConfigError when storage.directory option is set to CUSTOM_APPS_DIR (disallowed directory name).
- SystemExit via utils.error(...)
  - Trigger: _warn_on_old_config calls error(...) when legacy sections are present in the config file. Also triggered indirectly if any provider helper (get_dropbox_folder_location, get_google_drive_folder_location, get_copy_folder_location, get_icloud_folder_location) cannot discover the provider folder — those functions call error(...) which calls sys.exit with a formatted message.
- Note: configparser itself may raise standard exceptions on malformed config constructs in extreme cases, but this implementation guards access using has_option/has_section and otherwise uses parser.get; any configparser-specific exceptions are not explicitly handled.

## Example:
- Basic instantiation (use within a script):
    from mackup.config import Config, ConfigError
    try:
        cfg = Config()  # uses default MACKUP_CONFIG_FILE in $HOME
    except AssertionError:
        # handle programmer error: wrong type used to construct Config
        raise
    except KeyError:
        # environment missing HOME
        handle_missing_home()
    except ConfigError as e:
        print("Invalid configuration:", e)
        exit(1)
    # Accessing properties:
    engine = cfg.engine        # e.g. "dropbox"
    storage_root = cfg.path    # resolved absolute path to provider root
    backup_dir = cfg.directory # backup directory name inside storage_root
    full_backup_path = cfg.fullpath  # os.path.join(storage_root, backup_dir)
    to_ignore = cfg.apps_to_ignore   # set of app names to ignore
    to_sync = cfg.apps_to_sync       # set of app names to sync

- Typical usage pattern:
    cfg = Config()
    if "some_app" in cfg.apps_to_ignore:
        skip()
    else:
        perform_backup(os.path.join(cfg.fullpath, "some_app"))

### `mackup.config.Config.__init__` · *method*

## Summary:
Initialize the Config instance by loading and validating the configuration file, then populate internal fields for parser, storage engine, resolved storage path, storage directory name, and application sets to ignore or sync.

## Description:
- Known callers and invocation context:
    - Command-line entry points and top-level configuration loaders instantiate Config early in program startup to determine backup storage settings and which applications to process.
    - Typical usage: cfg = Config() (uses default MACKUP_CONFIG_FILE in $HOME) or cfg = Config(filename) to override the filename.
    - This method runs during object construction and performs all parsing/validation steps so callers receive a ready-to-use, read-only snapshot of configuration state.

- Why this logic is its own method:
    - As an initializer, it sequences a small number of focused parsing/validation helpers (_setup_parser, _warn_on_old_config, _parse_engine, _parse_path, _parse_directory, _parse_apps_to_ignore, _parse_apps_to_sync) to build a consistent Config instance. Extracting sequencing into __init__ keeps parsing logic modular (each helper has a single responsibility) and centralizes lifecycle logic for constructing a validated configuration object.

## Args:
    filename (str | None): Optional configuration filename (relative to the user's HOME directory).
        - Allowed values: any Python str or None.
        - Default behavior: If None (or another falsey filename is passed by higher-level code), the module-level constant MACKUP_CONFIG_FILE is used by _setup_parser to determine the file to read.
        - Type check: The method asserts that filename is either a str or None; passing other types triggers AssertionError.

## Returns:
    None — constructs and initializes the instance in-place. After successful return the instance fields documented below are populated and can be accessed via the class' public properties.

## Raises:
    AssertionError
        - Condition: filename argument is not a str and not None (triggered by the initial assert in __init__).

    KeyError
        - Condition: os.environ["HOME"] is accessed by _setup_parser or by path resolution for ENGINE_FS while HOME is not defined.

    ConfigError (custom)
        - Conditions arising from called helpers:
            * _parse_engine raises ConfigError when the configured storage engine value is not one of the supported ENGINE_* constants.
            * _parse_path raises ConfigError when engine == ENGINE_FS but the "storage.path" option is missing in the configuration.
            * _parse_directory raises ConfigError when the configured storage.directory equals the reserved CUSTOM_APPS_DIR.
        - These are raised by the parsing helpers invoked during initialization.

    SystemExit (via utils.error or equivalent behavior)
        - Conditions:
            * _warn_on_old_config detects legacy config sections and calls utils.error(...) which, by project convention, produces a user-facing message and exits the process.
            * Provider-discovery helpers invoked by _parse_path (get_dropbox_folder_location, get_google_drive_folder_location, get_copy_folder_location, get_icloud_folder_location) may call utils.error(...) when they cannot discover the provider folder, causing process termination.
        - Note: the exact mechanism may be sys.exit invoked by utils.error; callers should treat this as an unrecoverable configuration error.

    Other exceptions
        - Any exceptions thrown by configparser or by provider helper functions (I/O errors, parser errors) will propagate; these are not handled inside __init__.

## State Changes:
- Attributes READ:
    - self._parser — read by _warn_on_old_config, _parse_engine, _parse_path, _parse_directory, _parse_apps_to_ignore and _parse_apps_to_sync to query sections and options.
    - self._engine — after it is assigned, subsequent helpers (e.g., _parse_path) read the engine value via the internal attribute or its property.

- Attributes WRITTEN (assigned by this initializer):
    - self._parser: assigned to the return value of self._setup_parser(filename)
    - self._engine: assigned to the validated engine string returned by self._parse_engine()
    - self._path: assigned to the engine-resolved storage path string returned by self._parse_path()
    - self._directory: assigned to the storage directory name returned by self._parse_directory()
    - self._apps_to_ignore: assigned to the set returned by self._parse_apps_to_ignore()
    - self._apps_to_sync: assigned to the set returned by self._parse_apps_to_sync()

## Constraints:
- Preconditions:
    - filename must be a str or None (enforced by assertion).
    - The HOME environment variable should be defined when using default/relative file paths or when resolving file-system engine paths.
    - _setup_parser must return a parser-like object implementing has_section/has_option/get/options so subsequent helpers operate correctly. In practice __init__ calls _setup_parser itself before other helpers.
- Postconditions:
    - On successful completion (no exceptions or process exit), the Config instance satisfies these invariants:
        * self._parser is a configparser-like object that has attempted to read the resolved config file.
        * self._engine is a str equal to one of the supported engine constants (ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_COPY, ENGINE_ICLOUD, ENGINE_FS).
        * self._path is a str representing the resolved storage root appropriate to the chosen engine (provider helpers or os.path.join(os.environ["HOME"], configured_path) for ENGINE_FS).
        * self._directory is a str (defaults to MACKUP_BACKUP_PATH) and is never equal to CUSTOM_APPS_DIR.
        * self._apps_to_ignore and self._apps_to_sync are sets of strings (possibly empty) reflecting the respective config sections.
    - Instance is ready for read-only access via the class' public properties (engine, path, directory, fullpath, apps_to_ignore, apps_to_sync).

## Side Effects:
- I/O and environment access:
    - Calls _setup_parser which attempts to read the resolved configuration file from the filesystem (parser.read(...)); missing file is tolerated silently by parser.read.
    - Reads the HOME environment variable via os.environ["HOME"] inside _setup_parser and potentially inside _parse_path when ENGINE_FS is used.
- External calls:
    - May invoke utils.error(...) (directly via _warn_on_old_config or indirectly via provider helpers) which produces a user-facing error message and typically terminates the process.
    - May call provider-discovery helper functions (get_dropbox_folder_location, get_google_drive_folder_location, get_copy_folder_location, get_icloud_folder_location) which may perform filesystem or OS-specific discovery and may also call utils.error(...) on failure.
- No mutation of external persistent state is performed by __init__ itself beyond the side effects of the called helpers; the method does not write files or perform network requests directly.

### `mackup.config.Config.engine` · *method*

## Summary:
Returns the storage engine identifier for this Config as a normalized string (read-only), reflecting the engine selected from the config file or the default.

## Description:
Known callers and context:
- Called internally by Config._parse_path during object initialization to choose the storage path based on the selected engine. (Config.__init__ sets self._engine first by calling _parse_engine, then _parse_path reads this property.)
- Intended for use by other code that needs to inspect which storage engine the configuration selected (for example, modules that branch behavior based on the engine).

Why this is a separate property:
- Exposes a stable, read-only view of the validated engine value that was parsed and normalized by _parse_engine.
- Keeps external access simple and consistent (always returns a string) while the parsing and validation logic remain encapsulated in _parse_engine.
- Using a property enforces that the value is accessed as an attribute rather than requiring callers to know about internal field names.

## Args:
    None (this is a no-argument read-only property).

## Returns:
    str: The engine identifier as a string.
    Possible returned values (string constants imported from constants):
        - ENGINE_DROPBOX
        - ENGINE_GDRIVE
        - ENGINE_COPY
        - ENGINE_ICLOUD
        - ENGINE_FS
    Notes:
        - The value originates from Config._parse_engine, which reads the 'storage' -> 'engine' option from the configuration file or falls back to ENGINE_DROPBOX, then validates it against the allowed list above.
        - The returned string is the result of str(self._engine), which ensures the returned type is str even if the underlying value were another string-like type.

## Raises:
    The property itself does not explicitly raise exceptions in its implementation.
    However, callers may observe:
        - AttributeError if the Config instance was not properly initialized (i.e., self._engine does not exist). In normal use this will not happen because __init__ sets self._engine via _parse_engine.
    All validation and explicit ConfigError raising for unknown engines is performed in _parse_engine (raised when parsing/initializing _engine).

## State Changes:
    Attributes READ:
        - self._engine
    Attributes WRITTEN:
        - None (this property does not modify the object state)

## Constraints:
    Preconditions:
        - The Config instance should have completed initialization (or otherwise ensured) so that self._engine exists and holds the parsed engine identifier (a string). In standard usage this is satisfied by Config.__init__ calling _parse_engine.
    Postconditions:
        - The call returns a string equal to str(self._engine).
        - No mutation to the Config instance or external state is performed.

## Side Effects:
    - None. The property only reads an internal attribute and returns its string representation; it performs no I/O, no external service calls, and does not modify objects outside of self.

### `mackup.config.Config.path` · *method*

## Summary:
Return a normalized string representation of the configured storage root path (the internal _path) without modifying the Config object.

## Description:
Known callers and context:
- Config.fullpath: calls this property to assemble the final storage location (fullpath = os.path.join(self.path, self.directory)).
- General consumers: any code that needs the configured storage root for file operations (backup, restore, sync) should read this property after Config initialization.

Lifecycle note:
- The internal attribute self._path is set during Config.__init__ by calling _parse_path(). That parsing step performs engine-specific resolution and may raise ConfigError if configuration is invalid. This property simply exposes the result of that parsing as a str.

Why this logic is a separate property:
- Provides a consistent, read-only accessor that always returns a str, hiding how _path was computed.
- Keeps callers simple and prevents repeated conversions at call sites.

## Args:
None — this is a parameterless read-only property.

## Returns:
str — the storage root path as a Python string.
- Typical value: a filesystem path (e.g., '/Users/alice/Dropbox/Mackup') produced by _parse_path().
- Edge cases: if the Config instance was not initialized and _path is missing, the property will not return a value (see Raises).

Example usage:
- Read only: config = Config(); base = config.path

## Raises:
- AttributeError: if self._path does not exist (e.g., __init__ did not complete, or the attribute was removed).
- Any exception raised by the conversion str(self._path) (rare for normal path values).

Important: this accessor does not itself raise ConfigError; configuration validation and ConfigError raising occur in _parse_path during initialization.

## State Changes:
Attributes READ:
- self._path

Attributes WRITTEN:
- None (no mutation performed).

## Constraints:
Preconditions:
- Config.__init__ must have run successfully so that self._path exists and holds the parsed path value (set by _parse_path()).
- self._path should be a value that can be converted to str.

Postconditions:
- No changes to the Config instance state.
- Caller receives a str that represents the current storage root path.

## Side Effects:
- None. This property does not perform I/O, external calls, or mutate objects outside the Config instance.

### `mackup.config.Config.directory` · *method*

## Summary:
Return the configured storage directory as a string (read-only accessor for the parsed directory value stored on the Config instance).

## Description:
- Known callers and context:
    - Config.fullpath directly accesses this property to build an absolute path (fullpath is implemented as os.path.join(self.path, self.directory)).
    - The property is intended for use after a Config instance has been constructed (__init__ completes), when callers need the directory component of the backup location.
- Why this is a separate property:
    - Provides a stable, read-only accessor that guarantees callers receive a string and hides the internal attribute _directory.
    - Keeps callers from relying on the internal attribute name and centralizes the type coercion (str(...)).

## Args:
    None

## Returns:
    str: The storage directory name. This is exactly str(self._directory), where self._directory is populated during initialization by _parse_directory().
    - Possible return sources:
        - If the configuration file contains the option "storage" -> "directory", its value (parser.get(...)) is used.
        - Otherwise, the default constant MACKUP_BACKUP_PATH is used.
    - The returned value is a string; no additional normalization or path joining is performed by this property.

## Raises:
    AttributeError: If the Config instance does not have the internal attribute _directory (for example, if __init__ was not executed), accessing this property will raise AttributeError.
    Note: validation errors related to the directory value (for example, the parser raising ConfigError when configured directory equals CUSTOM_APPS_DIR) are raised during object initialization in _parse_directory(), not by this property.

## State Changes:
- Attributes READ:
    - self._directory
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - __init__ must have been executed so that self._directory exists (it is set by self._parse_directory() in the constructor).
- Postconditions:
    - The Config instance is unchanged by this call.
    - The caller receives a str equal to str(self._directory).

## Side Effects:
    - None. This accessor performs no I/O, no external calls, and does not mutate self or any external objects.

## Implementation notes (for reimplementation):
    - Implement as a read-only property that returns str(self._directory).
    - Ensure _parse_directory is responsible for parsing/validating the config option and for supplying a default (MACKUP_BACKUP_PATH).

### `mackup.config.Config.fullpath` · *method*

## Summary:
Return the filesystem path that results from joining the configured storage base path and the configured storage directory, as a str; does not modify the Config object.

## Description:
Known callers:
    - No direct callers are defined inside the Config class shown. Externally, this property is intended for any code that needs the resolved location of the backup/sync storage directory (for example: backup, restore, sync, or listing operations). Those callers are part of the runtime logic that performs filesystem operations using configuration values.

Lifecycle / context:
    - fullpath is a read-only computed property that is safe to call after a Config instance has been constructed (after Config.__init__ completes).
    - The parsing helpers invoked during __init__ populate the underlying values (self._path and self._directory) used here.
    - This logic is factored into its own property to centralize path construction and ensure consistent join semantics across the codebase.

Why this method exists separately:
    - Encapsulates os.path.join(self.path, self.directory) in a single place so callers do not duplicate join logic or need to know internal attribute names.
    - Provides a single point to add normalization or validation in the future (e.g., converting to absolute, resolving symlinks) without touching all callers.

## Args:
    - None. The property reads instance state only.

## Returns:
    - str: The result of os.path.join(self.path, self.directory) coerced to str.
    - Important notes on possible return values:
        * If self.directory is an absolute path (e.g., starts with "/" on POSIX), os.path.join will ignore self.path and return self.directory (joined result equals the absolute directory).
        * If self.directory is an empty string, the returned value is equivalent to self.path.
        * If self.path or self.directory are relative paths, the returned string will be a relative path (no automatic conversion to an absolute path or expansion of ~ is performed here).
        * The method does not normalize the path (no os.path.abspath, no os.path.normpath, and no environment expansion).

## Raises:
    - This property itself does not raise exceptions.
    - However, callers should be aware that Config.__init__ (and the parsing helpers it calls) may raise ConfigError when configuration is invalid (for example, missing required 'path' when using the file-system engine, or using the reserved CUSTOM_APPS_DIR as the storage directory). Those errors occur during construction; fullpath assumes the instance was successfully created.

## State Changes:
    Attributes READ:
        - self.path (property) — which reads and returns str(self._path)
        - self.directory (property) — which reads and returns str(self._directory)
    Attributes WRITTEN:
        - None. No attributes of self (or external objects) are modified.

## Constraints:
    Preconditions:
        - The Config instance must be fully initialized so that self._path and self._directory exist (i.e., Config.__init__ completed without raising).
        - self.path and self.directory should be valid string values (the class enforces str conversion in the corresponding properties).

    Postconditions:
        - The Config instance remains unchanged.
        - The return value is a string representing the joined path and follows the semantics of os.path.join for the supplied components (including the absolute-directory override rule).

## Side Effects:
    - None. The property performs no I/O, does not read from or write to the filesystem, and makes no external service calls. It is purely a read-only, in-memory computation.

### `mackup.config.Config.apps_to_ignore` · *method*

## Summary:
Returns a snapshot copy of the Config object's internal collection of application identifiers that should be ignored, so callers can inspect or iterate over ignored apps without mutating the internal state.

## Description:
This property accessor provides read-only access to the set of application names/options that were parsed from the configuration file (the "applications_to_ignore" section). It is typically invoked during decision-making steps where the program needs to determine whether an application should be skipped (for example, when enumerating installed apps to back up or sync). No callers are defined in the provided excerpt of this module; consumers outside this class are expected to call this property to obtain the current ignore-list.

The logic is implemented as a distinct property rather than inlined so callers always receive an independent copy (snapshot) of the internal set, preventing accidental external mutation of Config's internal state.

## Args:
None.

## Returns:
set[str]
    - A new set containing the same string elements as self._apps_to_ignore.
    - Typical values: an empty set (when no "applications_to_ignore" section is present) or a set of application identifier strings (option names from the config parser).
    - Edge-case return values:
        * Always returns a set object when the call succeeds.
        * If self._apps_to_ignore is empty, an empty set() is returned.

## Raises:
AttributeError
    - If the Config instance has not been fully initialized and the attribute self._apps_to_ignore does not exist.
TypeError
    - If self._apps_to_ignore is present but contains unhashable items or is otherwise not an iterable compatible with the built-in set() constructor, constructing the returned set will raise TypeError.

## State Changes:
Attributes READ:
    - self._apps_to_ignore

Attributes WRITTEN:
    - None (the method does not mutate the object)

## Constraints:
Preconditions:
    - The Config instance should have been initialized (its __init__ sets self._apps_to_ignore by calling _parse_apps_to_ignore).
    - self._apps_to_ignore should be an iterable of hashable items (typically strings).

Postconditions:
    - The Config object's internal attribute self._apps_to_ignore remains unchanged.
    - The caller receives a separate set object containing the same elements; mutating the returned set will not affect Config._apps_to_ignore.

## Side Effects:
    - None. This accessor performs no I/O, does not call external services, and does not mutate objects other than returning a new set.

### `mackup.config.Config.apps_to_sync` · *method*

## Summary:
Returns a defensive copy of the configuration's set of application identifiers selected for syncing, leaving the object's internal state unchanged.

## Description:
- Known callers and context:
    - No direct callers for this property were found in the scanned repository snapshot. It is provided as a public read-only accessor for code that needs the configured set of applications to sync (for example: sync routines, CLI commands, or higher-level orchestration that decides which application settings to back up).
    - Typical lifecycle stage: called after a Config instance is constructed and parsed (Config.__init__ sets up internal state). Consumers call this property when they need an immutable snapshot of which apps should be synchronized.

- Rationale for being a separate method/property:
    - Encapsulates access to the internal _apps_to_sync set and enforces returning a copy to prevent callers from mutating internal state.
    - Keeps symmetry with other configuration accessors (e.g., apps_to_ignore) and centralizes behavior in one place for clarity and future maintenance.

## Args:
    None

## Returns:
    set[str]: A new set containing the application identifiers (strings) present in the Config instance's internal _apps_to_sync collection.
    - If no applications are configured, returns an empty set.
    - The returned set is a shallow copy: mutating it does not affect self._apps_to_sync.

## Raises:
    - None explicitly raised by the method.
    - Runtime note: If the Config instance was not initialized correctly (i.e., self._apps_to_sync attribute missing), attribute access will raise AttributeError when this property is accessed.

## State Changes:
    Attributes READ:
        - self._apps_to_sync
    Attributes WRITTEN:
        - None (this method does not modify any attributes)

## Constraints:
    Preconditions:
        - The Config instance must have the attribute _apps_to_sync (typically populated by Config.__init__ via _parse_apps_to_sync()).
        - Elements stored in self._apps_to_sync are expected to be strings (application identifiers).

    Postconditions:
        - self._apps_to_sync remains unchanged.
        - The caller receives a new set object containing the same elements as self._apps_to_sync.

## Side Effects:
    - None. This method performs no I/O and does not call external services. It does not mutate objects outside of its local return value.

### `mackup.config.Config._setup_parser` · *method*

## Summary:
Constructs and returns a configparser.SafeConfigParser configured with project-specific parsing options and initialized by reading a configuration file; does not modify the Config instance.

## Description:
Creates a SafeConfigParser with allow_no_value=True and inline comment prefixes (";", "#"), then calls its read(...) method with a path computed from the HOME environment variable and the provided filename (or a module default when filename is falsey). No callers are present in the provided snippet.

This method centralizes the parser construction and the file-reading call so callers can obtain a consistently configured parser via a single call.

## Args:
    filename (str or None): Name or path to the configuration file.
        - The source asserts the type using: assert isinstance(filename, str) or filename is None.
        - If filename is None or another falsey value, the module-level constant MACKUP_CONFIG_FILE is used instead.
        - The code resolves the file argument by passing os.path.join(os.path.join(os.environ["HOME"], filename_used)) to parser.read, where filename_used is filename or the default constant.

## Returns:
    configparser.SafeConfigParser: The parser instance configured with allow_no_value=True and inline_comment_prefixes=(";", "#") after parser.read(...) has been invoked with the resolved path. The method returns the parser object; it does not return the list returned by parser.read(...).

## Raises:
    AssertionError:
        - If filename is neither a str nor None (from the initial assert).
    KeyError:
        - If the HOME environment variable is not present when accessed via os.environ["HOME"].
    Any exception raised by configparser.SafeConfigParser(...) construction or by parser.read(...) will propagate; the method contains no try/except to handle such exceptions.

## State Changes:
    Attributes READ:
        - No self.<attr> attributes are read.
        - Reads the process environment via os.environ["HOME"].
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - filename must be a str or None (enforced by assert).
        - The HOME environment variable must be available if the default or a relative filename is used.
    Postconditions:
        - Returns a SafeConfigParser instance configured as specified and that has had .read(resolved_path) called.
        - The Config instance (self) remains unmodified.

## Side Effects:
    - Calls parser.read(resolved_path), which attempts to read the resolved filesystem path.
    - Reads the HOME environment variable.

### `mackup.config.Config._warn_on_old_config` · *method*

## Summary:
Checks the loaded configuration for deprecated/legacy sections and triggers an abort via the shared error handler if any are present, leaving the Config object state unchanged.

## Description:
This internal helper scans the parser attached to the Config instance for two legacy section names ("Allowed Applications" and "Ignored Applications"). If any are found it calls the repository-wide error(...) helper with a multi-line message that references the project configuration filename and instructs the user to migrate their configuration.

Known callers and invocation context:
- Intended to be executed immediately after a configuration file has been parsed or loaded into self._parser (for example, during configuration parsing/validation steps). It is a validation gate to prevent running with an outdated file format.
- It is an internal method (prefixed with an underscore) and should be invoked by Config initialization or configuration-loading routines rather than by external code.

Why this is a separate method:
- The check is a focused validation step that does not modify object state; extracting it makes the configuration parsing code clearer and centralizes the legacy-detection message/behavior so it can be reused in multiple load paths and updated in one place.

## Args:
None.

## Returns:
None (implicitly returns None). There are no meaningful return values — the method either completes with no effect if no legacy sections exist or it calls the error(...) handler when it detects legacy sections.

## Raises:
This function does not itself raise exceptions in its implementation. However, it calls utils.error(...). The exact behavior (e.g., logging, raising an exception, or calling sys.exit) depends on that helper's implementation. Callers should assume that utils.error may terminate the process or raise an exception; consult the utils.error definition for precise behavior.

## State Changes:
Attributes READ:
- self._parser — only used to call has_section(section_name) to detect legacy sections.

Attributes WRITTEN:
- None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
- self._parser must be an object implementing has_section(section_name) (e.g., instances of ConfigParser.ConfigParser or configparser.ConfigParser). If self._parser is missing or does not provide has_section, an AttributeError or similar will be raised by Python before any legacy detection occurs.

Postconditions:
- If no legacy sections are present, the method completes normally and the Config instance is unchanged.
- If a legacy section is present, the method invokes utils.error(...) with a formatted message referring to MACKUP_CONFIG_FILE; beyond that, no additional postcondition is guaranteed by this method itself (the error handler's behavior determines whether control returns or the process terminates).

## Side Effects:
- Calls the external function error(...) imported from utils with a multi-line user-facing message. That call is the only side effect and may produce output (e.g., write to stderr, log) or terminate the process depending on the error helper's implementation.
- Reads the module-level constant MACKUP_CONFIG_FILE to include the config filename in the message.

### `mackup.config.Config._parse_engine` · *method*

## Summary:
Parses and validates the storage "engine" value from the configuration parser and returns it as a normalized Python str; does not mutate the Config object.

## Description:
Reads the "engine" option from the "storage" section of the configuration (via self._parser). If the option is missing, the method uses ENGINE_DROPBOX as the default. It validates that the resulting value is a string and that it matches one of the supported engine identifiers; otherwise it raises a ConfigError.

Known callers and call context:
- Intended to be invoked during the configuration-parsing stage of this Config object (for example, by an initializer or a top-level parse/load method in the same class or module) when the code needs the storage engine value.
- The exact calling sites are not included in the provided snippet; callers should expect this method to be used while assembling the runtime configuration.

Reason this logic is a dedicated method:
- Isolates the retrieval, defaulting, type-checking, and validation of the storage engine into a single place so callers can obtain a validated engine string without duplicating checks elsewhere.

## Args:
- None

## Returns:
- str: A normalized Python str representing the storage engine. The returned value is guaranteed (on successful return) to be equal to one of the supported engine constants imported in the module (ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_COPY, ENGINE_ICLOUD, ENGINE_FS). If the option is missing in the parser, ENGINE_DROPBOX is returned.

Edge-case returns:
- The method always returns a str on success. It will not return None or other types.

## Raises:
- ConfigError: Raised if the parsed (or defaulted) engine string is not one of the supported engine identifiers. The exception message is exactly "Unknown storage engine: {engine}" where {engine} is the invalid value.
- AssertionError: Raised if the computed engine is not a Python str due to the assert isinstance(engine, str) in the implementation. This can occur only if the upstream parser or constants supply a non-str value and assertions are enabled.

## State Changes:
Attributes READ:
- self._parser.has_option("storage", "engine")
- self._parser.get("storage", "engine")

Attributes WRITTEN:
- None — this method does not modify any attributes on self.

## Constraints:
Preconditions:
- self._parser must be an object implementing has_option(section, option) -> bool and get(section, option) -> value.
- The constants ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_COPY, ENGINE_ICLOUD, ENGINE_FS must be present in the module scope (they are imported at file level).

Postconditions:
- On successful return, the method yields a str equal to one of the supported engine constants.
- The Config object's state is unchanged by this call.

## Side Effects:
- No I/O is performed.
- No network, filesystem, or external service calls are made.
- No mutation of objects outside self is performed.

## Implementation notes for reimplementation:
- Query the parser for the "storage" -> "engine" option; if present, coerce its value to a str before validation.
- Use ENGINE_DROPBOX as the fallback default when the option is absent.
- Validate membership against the set {ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_COPY, ENGINE_ICLOUD, ENGINE_FS}.
- Raise ConfigError with the exact message shown if validation fails; otherwise return the engine as a str.

### `mackup.config.Config._parse_path` · *method*

## Summary:
Resolve and return the storage location path for the configured storage engine as a string; the method does not modify the Config instance (the caller typically assigns the result to self._path during initialization).

## Description:
This internal helper inspects the effective storage engine (self.engine) and performs engine-specific discovery to compute the filesystem location used for backups. It centralizes logic for multiple providers (Dropbox, Google Drive, Copy, iCloud) and a manual file-system mode, keeping Config.__init__ concise and making path-resolution behavior testable in isolation.

Known callers and lifecycle stage:
- Config.__init__: invoked during Config construction immediately after parsing the configuration file and the storage engine. Typical call site in the class is: self._path = self._parse_path()
- No public/other-callers are expected; the method is internal (prefixed with an underscore).

Why this logic is separated:
- Each supported engine requires distinct discovery steps (provider-specific DB/files or a config option for file-system mode). Encapsulating this logic prevents duplication, simplifies testing, and isolates provider-specific failures.

## Args:
- None (instance method; only receives self)

## Returns:
- type: str
- Description: The resolved storage path for the configured engine.
    - For ENGINE_DROPBOX: returns the value produced by get_dropbox_folder_location(), converted to str.
    - For ENGINE_GDRIVE: returns the value produced by get_google_drive_folder_location(), converted to str.
    - For ENGINE_COPY: returns the value produced by get_copy_folder_location(), converted to str.
    - For ENGINE_ICLOUD: returns the value produced by get_icloud_folder_location(), converted to str.
    - For ENGINE_FS: returns os.path.join(os.environ["HOME"], cfg_path) where cfg_path is the "path" option from the "storage" section of the parsed config.
- Edge-case return values:
    - If a provider helper returns a non-string path-like object, the method coerces it to str before returning.
    - If execution reaches the end without setting path (e.g., due to an unexpected engine not handled here), Python will raise UnboundLocalError when attempting to return path.

## Raises:
- ConfigError:
    - Trigger: self.engine == ENGINE_FS and self._parser.has_option("storage", "path") is False.
    - Exact message produced by the implementation:
        "The required 'path' can't be found while the 'file_system' engine is used."
- KeyError:
    - Trigger: Accessing os.environ["HOME"] when the HOME environment variable is not defined.
- Propagated errors / side effects from helper functions:
    - get_dropbox_folder_location(), get_google_drive_folder_location(), get_copy_folder_location(), and get_icloud_folder_location may themselves raise IO/DB-related exceptions or call utils.error(...) to signal unrecoverable provider-discovery failures; such behavior will propagate to the caller of _parse_path.

## State Changes:
- Attributes READ:
    - self.engine (property reading self._engine) — selects the resolution branch.
    - self._parser — used in the ENGINE_FS branch to check and retrieve the "storage" -> "path" option via has_option and get.
- Attributes WRITTEN:
    - None. The method does not mutate any attributes on self.

## Constraints:
- Preconditions:
    - self._parser must be a configparser-like object that implements has_option(section, option) and get(section, option). In normal usage this is established by _setup_parser() before _parse_path() is called.
    - self.engine should be one of the supported constants: ENGINE_DROPBOX, ENGINE_GDRIVE, ENGINE_COPY, ENGINE_ICLOUD, or ENGINE_FS. In the class flow, _parse_engine() validates this; calling _parse_path() with an unsupported engine will result in an error (e.g., UnboundLocalError).
    - For ENGINE_FS: the "storage" section must include a "path" option and the HOME environment variable must be present.
- Postconditions:
    - On successful completion the method returns a str representing the storage path appropriate to the configured engine.
    - No attributes on the Config instance are changed by this call.

## Side Effects:
- Reads the HOME environment variable when resolving a file-system path (os.environ["HOME"]).
- Invokes provider-specific helper functions which may read files, query databases, or perform filesystem checks; these helpers may also call utils.error(...), which in the project's conventions indicates an unrecoverable configuration discovery error (its exact behavior is defined elsewhere). Any exceptions or side effects from those helpers propagate out of this method.

## Implementation notes (for reimplementation):
- Use the engine constants to select the correct helper or the FS branch.
- For the file system engine:
    - Check self._parser.has_option("storage", "path"); if false raise ConfigError with the exact message above.
    - If present, retrieve cfg_path = self._parser.get("storage", "path") and compute path = os.path.join(os.environ["HOME"], cfg_path).
- Always return str(path) to ensure callers receive a string regardless of helper return types.
- Do not perform existence checks here; provider helpers handle discovery validation and error signaling.

### `mackup.config.Config._parse_directory` · *method*

## Summary:
Return the configured storage directory name (as a string) to be stored on the Config object, defaulting to MACKUP_BACKUP_PATH when no option is provided and rejecting the reserved CUSTOM_APPS_DIR.

## Description:
Known callers and lifecycle stage:
- Called from mackup.config.Config.__init__ while building a Config instance. In the current initialization sequence it is invoked after the parser is set up and after engine/path parsing, and its return value is assigned to self._directory.
- No other callers are present in the module; this method is intended to encapsulate parsing and validation of the "storage:directory" configuration option during configuration load.

Rationale for being a distinct method:
- Encapsulates a single responsibility: retrieving the directory value from the config and enforcing a specific validation rule (disallowing the reserved CUSTOM_APPS_DIR).
- Keeps __init__ linear and readable and allows reuse or targeted testing of directory-specific parsing/validation.

## Args:
- None.

## Returns:
- type: str
- Description: The directory name to use for storage.
  - If the config file contains a "storage" section with a "directory" option, returns that option's value converted to str.
  - If the "storage:directory" option is not present, returns the module-level constant MACKUP_BACKUP_PATH converted to str.
- Edge cases:
  - The returned string is exactly the option value read from the parser (no normalization is performed).
  - The method never returns the reserved CUSTOM_APPS_DIR; if that value appears in the config it raises ConfigError instead of returning it.

## Raises:
- ConfigError: raised when the configuration explicitly sets the "storage:directory" option to the reserved value CUSTOM_APPS_DIR. The message explains that CUSTOM_APPS_DIR cannot be used as a storage directory.
  - Exact trigger: self._parser.has_option("storage", "directory") is True and self._parser.get("storage", "directory") == CUSTOM_APPS_DIR.
- Note (precondition-related): the method assumes self._parser exists and behaves like a configparser (providing has_option and get). If self._parser is missing or not a compliant parser object, attribute access errors may occur (these are not raised intentionally by this method).

## State Changes:
- Attributes READ:
  - self._parser: used to check for and read the "storage:directory" option.
- Attributes WRITTEN:
  - None. This method does not assign to any self.<attr>. The caller (Config.__init__) assigns the returned value to self._directory.

## Constraints:
- Preconditions:
  - self._parser must be set to a configparser-like object (supporting has_option(section, option) and get(section, option)) prior to calling.
  - Module-level constants CUSTOM_APPS_DIR and MACKUP_BACKUP_PATH must be defined and importable in the module scope.
- Postconditions:
  - The method returns a str suitable for assignment to self._directory.
  - If the configuration attempted to use the reserved directory name (CUSTOM_APPS_DIR), the method raises ConfigError and does not return.

## Side Effects:
- None: the method performs no I/O, makes no external service calls, and does not mutate any objects outside its local scope. It only reads from self._parser and module-level constants.

### `mackup.config.Config._parse_apps_to_ignore` · *method*

## Summary:
Return the set of application identifiers listed under the "applications_to_ignore" section of the loaded configuration and leave object state unchanged.

## Description:
This method examines the parsed configuration (self._parser) for a section named "applications_to_ignore". If that section exists, it collects the option names declared in that section and returns them as a set. It does not read option values — only option names are returned.

Known callers:
    - Config.__init__: called during Config construction to initialize the instance attribute self._apps_to_ignore.
    - No other internal callers in this class. The public property Config.apps_to_ignore exposes the stored set (copy) populated from this method's return value during initialization.

Lifecycle/context:
    - Invoked during Config initialization after the configuration parser is created and warnings about old config formats are handled. This keeps configuration parsing responsibilities modular and symmetric with the companion _parse_apps_to_sync method.

Why a separate method:
    - Keeps parsing logic for ignored apps isolated and testable.
    - Mirrors the structure used for parsing apps to sync, improving readability and maintainability.
    - Avoids inlining parsing steps directly inside __init__.

## Args:
    None

## Returns:
    set[str]: A set containing the option names from the "applications_to_ignore" section.
    - If the section does not exist, an empty set is returned.
    - If the section exists but contains no options, an empty set is returned.
    - Option names are returned as provided by the configuration parser instance; with the parser created in _setup_parser (configparser.SafeConfigParser with default option handling), option names are typically normalized by the parser (e.g., lowercased by default).

## Raises:
    - No exceptions are explicitly raised by this method.
    - If self._parser is not present or does not implement has_section/options, an AttributeError or similar will be raised by the underlying call; callers should ensure the parser is initialized (Config.__init__ does this before calling the method).

## State Changes:
    Attributes READ:
        - self._parser (used to query for the section and options)
    Attributes WRITTEN:
        - None (the method does not modify any attributes on self)
    Note: __init__ assigns the returned set to self._apps_to_ignore immediately after calling this method.

## Constraints:
    Preconditions:
        - self._parser must be initialized and implement has_section(section_name) and options(section_name).
        - The configuration file, if present, should use a section named "applications_to_ignore" to declare ignored apps.
    Postconditions:
        - Returns a set of option names representing ignored applications.
        - Does not modify the Config object's attributes or any external state.

## Side Effects:
    - None. The method performs no I/O and makes no external service calls. It only queries the in-memory parser and returns a new set derived from it.

### `mackup.config.Config._parse_apps_to_sync` · *method*

## Summary:
Return the set of application identifiers listed under the "applications_to_sync" section of the configuration parser and leave the object's state unchanged.

## Description:
This method queries the already-initialized configuration parser (self._parser) for a section named "applications_to_sync" and collects the option names defined in that section into a set. It is invoked during Config object initialization to populate the instance's apps-to-sync list (see Config.__init__), and kept as a separate method to mirror the parsing responsibilities of other _parse_* helpers, to keep __init__ concise, and to make parsing behavior easily testable in isolation.

Known callers and lifecycle context:
- Config.__init__: called while building a new Config instance to compute self._apps_to_sync.
- Indirectly read later via the property Config.apps_to_sync which returns a copy of the stored set.
Because it's invoked during initialization, it runs after self._parser has been created by _setup_parser.

Why this logic is its own method:
- Encapsulates the specific parsing logic for applications-to-sync.
- Follows the same design pattern as other _parse_* methods (e.g., _parse_apps_to_ignore), improving readability and testability.
- Isolates error handling and transformation of parser output from higher-level initialization code.

## Args:
This method takes no arguments.

## Returns:
set[str] - a set containing the option names (strings) present under the "applications_to_sync" section of the configuration file.
- If the "applications_to_sync" section is absent, an empty set is returned.
- Duplicate option names in the config become a single entry in the returned set.
- Order is not preserved (sets are unordered).

## Raises:
- This method does not explicitly raise exceptions. However, any exception thrown by the underlying parser when calling self._parser.options(section) (for example, parser-specific exceptions) will propagate to the caller. Under normal conditions, because the method checks has_section(section) before calling options(section), such exceptions should not occur.

## State Changes:
Attributes READ:
- self._parser: used to check for section existence and to retrieve option names.

Attributes WRITTEN:
- None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
- self._parser must be initialized and implement has_section(section: str) -> bool and options(section: str) -> Iterable[str].
- Typically called after _setup_parser has been run (as is done in Config.__init__).

Postconditions:
- The Config instance remains unchanged.
- The return value is a deduplicated set of option names from the "applications_to_sync" section (or an empty set if the section is missing).

## Side Effects:
- No I/O is performed by this method.
- No external services are contacted.
- No mutation of objects outside self occurs.

## `mackup.config.ConfigError` · *class*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
A dedicated exception type defined in the mackup.config module that represents configuration-related error conditions; it subclasses the built-in Exception without adding behavior.

## Description:
ConfigError is declared in mackup/config.py as a named exception type for signaling problems related to configuration. It provides a specific, catchable type so code can distinguish configuration errors from other exceptions. The class definition contains no methods or attributes beyond those inherited from Exception.

Purpose and boundaries:
- Purpose: provide a distinct exception class for configuration problems so callers can raise and catch a semantically meaningful type.
- Boundary: it does not implement validation logic, message formatting helpers, or any additional data fields — those responsibilities remain with the code that raises this exception.

## State:
No custom instance or class attributes are defined. Inherited state and their expected usage:
- args (tuple): standard Exception attribute containing positional arguments passed at construction. Typical usage is args[0] containing a human-readable message.
    - Type: tuple
    - Typical content: (message: str,)
- __str__ / __repr__: use Exception's implementations which format based on args.

Class invariants:
- Instances behave identically to instances of Exception; there are no extra invariants or constraints introduced by this class.

## Lifecycle:
Creation:
- Instantiate with positional arguments accepted by Exception, e.g., ConfigError("message").
Usage:
- Raise with: raise ConfigError("descriptive message")
- Catch with: except ConfigError as e:
- No special order of method calls is required beyond the standard raise/catch flow.
Destruction:
- No cleanup, context manager protocol, or explicit close required. Instances are regular objects eligible for garbage collection.

## Method Map:
flowchart LR
    A[Detect configuration problem] --> B[raise ConfigError("message")]
    B --> C[Exception machinery constructs instance]
    C --> D[Exception propagates up the stack]
    D --> E[except ConfigError as e: handle error]

(Note: ConfigError defines no methods; the diagram shows the typical raise->propagate->catch flow using built-in Exception behavior.)

## Raises:
- Instantiating or raising ConfigError follows built-in Exception semantics and does not itself raise custom exceptions.

## Example:
- Raising:
    raise ConfigError("Missing required 'backup' entry in configuration")

- Catching:
    try:
        load_config(path)
    except ConfigError as e:
        print("Configuration error:", str(e))
        # handle or re-raise

