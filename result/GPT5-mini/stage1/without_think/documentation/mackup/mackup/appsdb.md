# `appsdb.py`

## `mackup.appsdb.ApplicationsDatabase` · *class*

## Summary:
Represents a read-only in-memory registry of supported applications and their per-application configuration file paths, discovered from bundled and user-provided ".cfg" files.

## Description:
ApplicationsDatabase is instantiated to load and expose metadata about applications supported by this tool. On construction it scans two locations for ".cfg" application definition files (a built-in apps directory and a user "custom apps" directory) and parses each discovered file to record:
- a machine name (derived from the cfg filename, without the ".cfg" suffix),
- a human-friendly name from the "application" section ("name" option),
- a set of configuration file paths declared in the file (from "configuration_files" and "xdg_configuration_files" sections).

Typical callers:
- Any component that needs the list of available apps and their configuration file templates (e.g., code that installs, backs up, or restores application dotfiles).
- Factory/initialization code that needs a snapshot of supported apps for UI or CLI listing.

Motivation and responsibility boundary:
- Centralizes discovery and parsing of per-application .cfg descriptors into a single, read-only structure.
- Does not modify on-disk files; no persistence or mutation API is provided.
- Keeps application metadata normalized (app name keys, pretty display name, normalized relative configuration file paths).

## State:
Attributes (public):
- apps (dict[str, dict]):
    - Mapping keyed by app_name (filename without ".cfg") to a dictionary with:
        - "name" (str): the pretty display name read from the configuration's [application] name option. Expected to be a non-empty string but not enforced by code.
        - "configuration_files" (set[str]): a set of path strings (no leading '/' characters) representing files relative to a base (home or XDG config). Paths added from "xdg_configuration_files" are first joined with XDG_CONFIG_HOME then have the user's home prefix removed (so they remain relative). Invariants:
            - No path in the set begins with a forward slash ("/") — the constructor enforces this by raising on absolute paths.
            - Each value is unique (set semantics).

Constructor (__init__) parameters:
- None. Instantiation immediately triggers a discovery + parse pass. There are no optional parameters or injection hooks.

Class-level / static resources:
- get_config_files() (staticmethod) uses constants.APPS_DIR (relative to the module file) and constants.CUSTOM_APPS_DIR (relative to $HOME) to locate .cfg files. It depends on these constants and the environment variable HOME.

Class invariants:
- After construction, apps contains one entry per successfully-read .cfg file (custom files override same-named built-in files).
- For every app in apps:
    - apps[app]["name"] is present.
    - apps[app]["configuration_files"] is a set (possibly empty).

## Lifecycle:
Creation:
- Instantiate with ApplicationsDatabase() — the constructor performs file discovery and parsing immediately.
- Internally calls ApplicationsDatabase.get_config_files() to compute the set of .cfg file paths to read.

Usage:
- Typical method call order:
    1. Construct the database: db = ApplicationsDatabase()
    2. Query available app keys: db.get_app_names()
    3. For a given app key, get pretty name: db.get_name(app_key)
    4. For a given app key, get configuration templates: db.get_files(app_key)
    5. Optionally, use db.get_pretty_app_names() for a set of display names
- No methods mutate state; methods are read-only accessors. Order of accessor calls does not matter after construction.

Destruction / cleanup:
- No resources are held that require explicit cleanup. There is no close() or context manager API.

## Method Map:
graph LR
    Init([__init__]) --> GetConfigFiles[get_config_files()]
    Init --> ParseCFG[parse each config file with configparser.SafeConfigParser]
    ParseCFG --> AddApp[add apps[app_name] entry with "name" and "configuration_files"]
    AddApp --> ValidatePaths[raise ValueError on absolute paths]
    GetConfigFiles --> CustomDirCheck[check custom apps dir (os.path.isdir)]
    CustomDirCheck --> ReadCustomFiles[listdir(custom_apps_dir)]
    GetConfigFiles --> BuiltinDirRead[listdir(apps_dir)]
    ReadCustomFiles --> AddCustomFiles[add .cfg files from custom dir]
    BuiltinDirRead --> AddBuiltinFiles[add .cfg files from builtin dir, skipping custom names]

(Note: the diagram shows high-level dependencies: __init__ calls get_config_files() then parses each file; get_config_files inspects two directories and builds the set of cfg file paths.)

## Public methods and behaviors:
- __init__():
    - Behavior: Builds self.apps by reading each file returned by get_config_files().
    - For each cfg successfully read:
        - app_name = basename(filename) with trailing ".cfg" removed.
        - Reads "application" section's "name" option; stores as apps[app_name]["name"].
        - Initializes apps[app_name]["configuration_files"] as an empty set.
        - If a "configuration_files" section exists, iterates its option keys (option names) and:
            - If an option key starts with "/", raises ValueError("Unsupported absolute path: {path}").
            - Otherwise adds the option key to configuration_files set.
        - Determines home path via os.path.expanduser("~/") and reads XDG_CONFIG_HOME from environment, fallback to "<home>/.config".
        - If XDG_CONFIG_HOME does not start with the computed home path, raises ValueError explaining it must be inside home.
        - If "xdg_configuration_files" section exists, iterates option keys and:
            - If a key starts with "/", raises ValueError("Unsupported absolute path: ...").
            - Otherwise joins XDG_CONFIG_HOME and the key, then removes the leading home prefix from that joined path, and adds the result to configuration_files set.
    - Notes on parsing:
        - Uses configparser.SafeConfigParser(allow_no_value=True) with optionxform set to str (to preserve option case).
        - Only config.read(config_file) results that indicate success are processed.
        - The code assumes the presence of an [application] section and a "name" option; missing section/option will cause configparser to raise (see "Raises" below).

- get_config_files() -> set[str]:
    - Static discovery of .cfg files. Implementation details:
        - apps_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), APPS_DIR)
        - custom_apps_dir = os.path.join(os.environ["HOME"], CUSTOM_APPS_DIR)
        - If custom_apps_dir exists, add all filenames ending with ".cfg" from it, recording filenames to avoid duplicates.
        - Add .cfg files from apps_dir except those whose filename is present in the custom set (custom overrides built-in).
        - Returns a set of absolute file paths (strings).

- get_name(name: str) -> str:
    - Returns the pretty name stored for the given app key.
    - Raises KeyError if the provided name is not in self.apps.

- get_files(name: str) -> set[str]:
    - Returns the set of configuration file path templates for the given app key.
    - Raises KeyError if the provided name is not in self.apps.

- get_app_names() -> set[str]:
    - Returns a set of the machine app keys (the cfg filenames without ".cfg").

- get_pretty_app_names() -> set[str]:
    - Returns a set of pretty display names corresponding to each app.

## Raises:
Exceptions that may be raised during instantiation or method calls (directly observable from the implementation):
- ValueError:
    - Raised if any configuration_files option begins with "/" (absolute path).
    - Raised if any xdg_configuration_files option begins with "/" (absolute path).
    - Raised if the resolved XDG_CONFIG_HOME does not start with the user's home directory (constructor enforces XDG_CONFIG_HOME within the home directory).
- configparser.NoSectionError or configparser.NoOptionError (or their equivalents depending on the Python version):
    - If a required section or option (for example, the [application] section or its "name" option) is missing while calling config.get("application", "name").
- KeyError:
    - get_config_files() assumes os.environ["HOME"] exists; missing HOME will raise KeyError during discovery.
    - get_name() / get_files() raise KeyError if asked for a non-existent app key.
- OSError / FileNotFoundError:
    - os.listdir(apps_dir) or os.listdir(custom_apps_dir) can raise if the directories do not exist or are unreadable (depending on environment and platform). The code assumes the built-in apps_dir exists and is readable.

Behavioral notes on error conditions:
- If a .cfg file cannot be read (config.read(config_file) returns a falsey value), that file is skipped silently.
- Custom .cfg files (in the CUSTOM_APPS_DIR under $HOME) override same-named built-in .cfg files (the builtin is ignored when filename matches one from the custom directory).

## Example:
Create the database and query available apps and files (typical happy path):

db = ApplicationsDatabase()
all_keys = db.get_app_names()            # set of machine names (filenames without .cfg)
pretty_names = db.get_pretty_app_names() # set of human-visible names
first_key = next(iter(all_keys))
display_name = db.get_name(first_key)    # pretty name for that app
paths = db.get_files(first_key)          # set of relative configuration-file paths

Notes:
- Wrap construction in try/except if you need to handle missing HOME, malformed cfg files, or ValueError conditions described above.
- Methods perform no I/O beyond the initial construction (which reads the .cfg files); subsequent calls are in-memory lookups.

### `mackup.appsdb.ApplicationsDatabase.__init__` · *method*

## Summary:
Initialize the ApplicationsDatabase instance by discovering application configuration files, parsing each configuration, and populating self.apps with per-application metadata (pretty name and a set of configuration file paths). This establishes the object's initial state used by other components.

## Description:
This constructor is invoked when an ApplicationsDatabase object is created (e.g., by calling ApplicationsDatabase() during mackup startup or when code needs the catalog of known applications). Its responsibility is to load and parse application .cfg files (provided by ApplicationsDatabase.get_config_files()), extract the human-readable application name from the "application" section, and collect declared configuration file paths from two optional sections: "configuration_files" and "xdg_configuration_files". The logic lives in __init__ because these actions must run once at object construction time to produce a ready-to-use self.apps mapping; keeping it here centralizes bootstrapping behavior and ensures other methods can rely on populated state.

Known callers and typical lifecycle:
- Any code that instantiates the ApplicationsDatabase class, e.g., at program initialization to build the list of supported applications and their associated configuration files.
- Called once per ApplicationsDatabase instance as part of the object's construction lifecycle.

Why separate logic:
- Bootstrapping must occur exactly once per instance and must populate instance state; embedding this logic inside __init__ ensures correct initialization order and avoids requiring separate initialization calls after construction.

## Args:
    None

## Returns:
    None (returns implicitly None). On successful completion, the instance attribute self.apps is populated as described below.

## Raises:
    ValueError:
        - "Unsupported absolute path: {path}" — raised when an entry listed under "configuration_files" or "xdg_configuration_files" starts with a forward slash (i.e., is an absolute path). The exact message is produced with the offending path substituted.
        - "$XDG_CONFIG_HOME: {xdg_config_home} must be somewhere within your home directory: {home}" — raised when the resolved XDG_CONFIG_HOME environment variable does not begin with the expanded user home directory returned by os.path.expanduser("~/").
    configparser.NoSectionError or configparser.NoOptionError (or their equivalents depending on the configparser implementation):
        - May be raised by config.get("application", "name") if the "application" section or "name" option is missing. These exceptions are propagated and not caught here.

## State Changes:
Attributes READ:
    - None of self.<attr> fields are read before write; however, the constructor reads class-level method ApplicationsDatabase.get_config_files() and environment variables (os.environ) to determine inputs.

Attributes WRITTEN:
    - self.apps (dict): created and populated.
        - For each application discovered, self.apps[app_name] is a dict with:
            - "name" (str): the value returned by config.get("application", "name").
            - "configuration_files" (set[str]): a set of relative path strings describing the app's configuration files.

## Constraints:
Preconditions:
    - ApplicationsDatabase.get_config_files() must return an iterable of configuration file paths (typically files ending with ".cfg"). The code assumes returned items are file paths suitable for config.read().
    - The runtime must have access to the filesystem paths returned by get_config_files() (config.read() attempts to open/read them).
    - The environment may optionally include XDG_CONFIG_HOME; otherwise a default is derived from the expanded home path.

Postconditions (guarantees after a successful call):
    - self.apps is a dict mapping application names (derived from config filename by removing the last len(".cfg") characters) to dicts containing "name" and "configuration_files".
    - For every application entry:
        - "name" is the value from the configuration's "application" -> "name".
        - "configuration_files" is a set containing only relative paths (strings that do not start with "/"). For entries from the "xdg_configuration_files" section, the stored path has had the user's home directory prefix removed (so it typically begins with ".config/..." or another non-absolute string).
    - No file entries that started as absolute paths are accepted; such entries cause exceptions instead of partial population.

## Side Effects:
    - Reads files from disk via config.read(config_file) for each path returned by ApplicationsDatabase.get_config_files().
    - Reads environment variables: os.environ.get("XDG_CONFIG_HOME", default).
    - Calls os.path.expanduser("~/"), os.path.basename, and os.path.join.
    - May raise exceptions that propagate out of __init__ (see Raises).
    - Does not modify global state other than reading environment variables and filesystem contents; all resulting state changes are confined to the new instance's self.apps attribute.

## Implementation details and important notes for reimplementation:
    - Config parser is created with allow_no_value=True and optionxform set to str to preserve option case exactly (no lowercasing).
    - The boolean test if config.read(config_file): proceeds only when the config file was successfully read (config.read returns a non-empty list of read filenames).
    - The app_name key is computed from the basename of the config file by removing exactly the number of characters in the string ".cfg" from the end; the implementation assumes get_config_files() returns filenames that include the ".cfg" suffix.
    - When processing "configuration_files", each item returned by config.options("configuration_files") is treated as a path string and must not be absolute.
    - For "xdg_configuration_files":
        - The XDG_CONFIG_HOME path is taken from the environment or defaulted to "<expanded_home>/.config".
        - xdg_config_home must begin with the expanded home directory path; otherwise a ValueError is raised.
        - Each declared path must not be absolute; it is joined with xdg_config_home and then the expanded home prefix is stripped before being stored, ensuring stored values are relative to the user's home directory.
    - The method intentionally allows configparser to raise its standard exceptions when required sections/options are missing; callers should be prepared to handle these errors.

### `mackup.appsdb.ApplicationsDatabase.get_config_files` · *method*

## Summary:
Return the set of absolute paths to all available application configuration (.cfg) files by scanning the bundled apps directory and an optional per-user custom apps directory; does not modify object state.

## Description:
This function enumerates two locations for application configuration files:
- a packaged apps directory adjacent to the module (derived from the module file location and APPS_DIR), and
- a user-specific custom apps directory inside the user's HOME (derived from the HOME environment variable and CUSTOM_APPS_DIR).

It yields a set of absolute file paths to files whose names end with ".cfg". When a filename exists in both the custom directory and the packaged apps directory, the custom version takes precedence and the packaged file with the same filename is excluded from the result.

Known callers and lifecycle:
- No explicit callers are present in the provided snippet. Conceptually this function is intended to be called by higher-level code that needs to discover available application configuration files (for example: during ApplicationsDatabase initialization, when building a registry of apps, or when listing available app configs for the user). The exact call sites should be searched in the repository for concrete references.

Why this is a separate method:
- The logic encapsulates filesystem enumeration and filename precedence rules; separating it makes discovery behavior reusable and easy to test/mock without inlining filesystem details into unrelated initialization or parsing code.

## Args:
- None

## Returns:
- set[str]: A set of absolute filesystem paths (strings) to files ending with ".cfg" discovered in the two directories.
  - If no matching files are found, returns an empty set.
  - Each element is the result of os.path.join(directory, filename) for the discovered files.
  - Filenames in the custom directory are identified by base filename only (not full path) for precedence checks.

## Raises:
- KeyError: If the HOME environment variable is not present (os.environ["HOME"] is used).
- OSError (including FileNotFoundError on Python 3): If the packaged apps directory (apps_dir) does not exist or cannot be listed (os.listdir(apps_dir) is called unguarded), or if other filesystem access errors occur for the directories being listed.
  - Note: Listing the custom apps directory is guarded by os.path.isdir; therefore missing custom directory will not raise. Errors raised by listing the custom directory are possible only if the directory is present but unreadable.

## State Changes:
- Attributes READ: None (this function does not read or depend on any self.<attr> attributes).
- Attributes WRITTEN: None (this function does not modify any self.<attr> attributes).

## Constraints:
- Preconditions:
  - The HOME environment variable must be defined in os.environ.
  - The bundled apps directory (computed from the module file path and APPS_DIR) should exist and be readable; otherwise os.listdir will raise an OSError/FileNotFoundError.
- Postconditions:
  - The returned set contains every discovered ".cfg" file path from the custom apps directory (if present) and from the packaged apps directory except those whose base filename was already found in the custom directory.
  - No mutation to the object instance or to the filesystem is performed by this function.

## Side Effects:
- Performs filesystem I/O: calls os.path.isdir, os.listdir and os.path.join; reads environment variable HOME.
- No writes to disk, no network I/O.

### `mackup.appsdb.ApplicationsDatabase.get_name` · *method*

## Summary:
Return the user-facing (pretty) name for a loaded application identifier; this is a read-only accessor and does not modify object state.

## Description:
Known callers:
    - ApplicationsDatabase.get_pretty_app_names: uses this accessor to build a set of pretty names.
    - Other external callers may use this accessor, but the only confirmed internal caller in this class is get_pretty_app_names.

Lifecycle/context:
    - This method is intended to be called after ApplicationsDatabase.__init__ has loaded application configuration files into self.apps. It provides a single place to obtain the human-readable name associated with an application identifier.

Why this is a separate method:
    - Encapsulates lookup logic for an application's pretty name so callers do not access self.apps directly. Keeping this as an accessor centralizes future changes (fallback behavior, validation, localization) without modifying call sites.

## Args:
    name (str): The application identifier key (typically the base filename of a .cfg file, without the ".cfg" extension) that was loaded into self.apps. Must match an entry populated by ApplicationsDatabase.__init__.

## Returns:
    str: The value stored at self.apps[name]["name"], typically the human-readable application name as read from the application's configuration file.
    Edge cases:
        - The method returns exactly whatever value is stored at that mapping location; callers should not assume additional invariants beyond it being the configured value.

## Raises:
    KeyError: If name is not a key in self.apps (i.e., the requested application identifier was not loaded) or if the nested mapping for that application does not contain the "name" key.

## State Changes:
    Attributes READ:
        - self.apps
        - self.apps[name] (the nested metadata dict)
    Attributes WRITTEN:
        - None. This method performs no mutations.

## Constraints:
    Preconditions:
        - ApplicationsDatabase.__init__ must have run so that self.apps is populated.
        - The provided name must be an identifier that was loaded into self.apps.
    Postconditions:
        - No state in the ApplicationsDatabase instance is modified.
        - On success, the return value equals self.apps[name]["name"].

## Side Effects:
    - None. The method performs no I/O, makes no external calls, and does not mutate objects outside self.

### `mackup.appsdb.ApplicationsDatabase.get_files` · *method*

## Summary:
Return the internal set of configuration file path entries for the given application key.

## Description:
Accessor method that looks up the application entry in the ApplicationsDatabase internal mapping and returns the value stored under the "configuration_files" key for that application. There are no calls to this method from other methods in this file; it is an explicit, reusable accessor intended to provide a single point of retrieval for the application's configuration file set.

This method is separated from callers so that all code paths that need the configuration file set use a consistent lookup and so the retrieval logic is not duplicated across the codebase.

## Args:
    name (str): The application key (short name derived from the configuration filename when the ApplicationsDatabase was constructed). Required; no default.

## Returns:
    set: The set object stored at self.apps[name]["configuration_files"].
        - Elements are the path fragments recorded during ApplicationsDatabase.__init__ (typically relative paths or XDG-derived paths).
        - May be an empty set if the application defines no configuration files.
        - The returned object is the actual internal set; mutating it will mutate the ApplicationsDatabase internal state.

## Raises:
    KeyError: If `name` is not a key in self.apps, or if the application mapping does not contain the "configuration_files" key. (Under normal construction via ApplicationsDatabase.__init__, the "configuration_files" key is created for each application, so the common trigger is a missing application key.)

## State Changes:
    Attributes READ:
        - self.apps
        - self.apps[name]
        - self.apps[name]["configuration_files"]
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The ApplicationsDatabase instance must have been initialized so that self.apps contains application entries (i.e., __init__ has been executed).
        - `name` must be an application key present in self.apps.
    Postconditions:
        - Returns a reference to the set stored at self.apps[name]["configuration_files"].
        - The method does not modify the ApplicationsDatabase state.

## Side Effects:
    - No I/O or external service calls.
    - Returns a direct reference to an internal mutable set; callers that modify the set will change the database's internal data.
    - Lookup is a constant-time dictionary access (O(1) average).

### `mackup.appsdb.ApplicationsDatabase.get_app_names` · *method*

## Summary:
Return a new set containing all application identifier keys known to this ApplicationsDatabase instance; this does not modify the object's state.

## Description:
Known callers:
- ApplicationsDatabase.get_pretty_app_names (in-class): used to obtain the set of app identifiers before mapping each to its human-readable name.
- External callers (not shown here) may call this method to enumerate available applications or to drive UI/configuration flows.

Typical call context:
- After an ApplicationsDatabase instance has been constructed (its __init__ loads configuration files into self.apps), callers use this method to obtain the collection of application keys for iteration, display, or further lookup.

Rationale for being a separate method:
- Encapsulates the logic for enumerating app identifiers (keys) so callers do not access self.apps directly.
- Returns a fresh set to avoid exposing internal mutable structures and to guarantee callers receive a snapshot of current keys.

## Args:
(None)

## Returns:
set[str]
- A newly allocated set containing each application identifier (string) present as a key in self.apps.
- Possible values: zero or more strings representing the application's internal id (derived from configuration file names).
- Edge cases: returns an empty set if no applications were loaded (self.apps is empty).

## Raises:
- This method does not raise exceptions directly.
- Any exceptions related to constructing or populating self.apps occur elsewhere (e.g., during __init__).

## State Changes:
Attributes READ:
- self.apps

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- The ApplicationsDatabase instance must have been initialized such that self.apps exists (in __init__ self.apps is created as a dict). Each key in self.apps is expected to be a string application identifier.

Postconditions:
- The method returns a set containing exactly the keys present in self.apps at the time of the call.
- The ApplicationsDatabase instance (self) is unchanged by this call.

## Side Effects:
- No I/O, no external service calls, and no mutations of external objects.
- Allocates a new set object proportional to the number of application keys (O(n) memory).
- Time complexity: O(n) where n is the number of keys in self.apps.

## Example:
- Given an instance db where db.apps == {'vim': {...}, 'tmux': {...}}, get_app_names() returns {'vim', 'tmux'}.

### `mackup.appsdb.ApplicationsDatabase.get_pretty_app_names` · *method*

## Summary:
Return a deduplicated set of human-facing application names collected from the database without modifying the object's state.

## Description:
Iterates over the set of application identifiers provided by get_app_names(), maps each identifier to its configured display name via get_name(identifier), and accumulates those display names into a set which is returned.

Known callers / usage context:
    - No internal callers were found in the analyzed repository snapshot.
    - Typical consumers are presentation or CLI/UI code that needs a unique list of application display names for listing, selection menus, or status output.

Why this is a separate method:
    - Encapsulates the common transformation from internal identifiers to user-facing names.
    - Provides a single place to handle deduplication of display names and to hide how names are retrieved from self.apps.
    - Keeps presentation-friendly operations out of lower-level storage accessors.

## Args:
    None.

## Returns:
    set[str]: A set containing the pretty/display names for every application present in self.apps at the time of the call.
    - The set is empty if there are no applications.
    - If multiple application identifiers map to the same display name, only one copy appears in the returned set (deduplication via set semantics).
    - Values are returned exactly as produced by get_name(); the implementation expects strings, but any returned value will be included (subject to set membership requirements).

## Raises:
    KeyError:
        - If get_name(name) raises KeyError because:
            * name is not present as a key in self.apps (this can occur if self.apps is mutated between get_app_names() and get_name()).
            * self.apps[name] exists but does not contain the "name" key.
    TypeError:
        - If a value returned by get_name(name) is an unhashable object (e.g., a list), adding it to the set will raise a TypeError.
    Note:
        - These exceptions are not explicitly raised by this method's own code but are direct consequences of calling get_app_names() and get_name() and of using a set to deduplicate results.

## State Changes:
    Attributes READ:
        - self.apps (indirectly, via get_app_names() and get_name())
        - self.get_app_names() and self.get_name(name) are invoked and therefore read whatever internal state they access.
    Attributes WRITTEN:
        - None. The method does not modify self or any external state.

## Constraints:
    Preconditions:
        - self.get_app_names() must return an iterable of application identifiers (the class implementation returns a set of keys from self.apps).
        - For each identifier yielded, self.get_name(identifier) must be callable and should return the display name (typically a string) for that identifier.
    Postconditions:
        - Returns a new set object containing the display names corresponding to the identifiers returned by get_app_names() at call time.
        - self is left unchanged.

## Side Effects:
    - None: no filesystem, network, or I/O operations are performed by this method itself.
    - Note: external effects can occur if get_name() or get_app_names() are overridden or depend on external state; this method does not introduce side effects beyond invoking those methods.

## Complexity:
    - Time: O(N) where N is the number of application identifiers returned by get_app_names(), dominated by N calls to get_name().
    - Space: O(M) where M is the number of unique display names returned (size of the result set).

## Example (conceptual usage):
    - Callers that want to present a unique list of application display names can call this method and iterate the returned set to render UI elements or print a menu.

