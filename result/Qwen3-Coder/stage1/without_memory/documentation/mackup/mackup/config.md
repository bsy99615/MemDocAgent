# `config.py`

## `mackup.config.Config` · *class*

*No documentation generated.*

### `mackup.config.Config.__init__` · *method*

## Summary:
Initializes a configuration object by parsing settings from a configuration file and setting up internal state variables.

## Description:
The `__init__` method sets up a Config instance by reading configuration data from a file and parsing various configuration options. It performs validation and setup of storage engine, backup path, directory, and application selection settings. This method orchestrates the configuration parsing process by calling several private helper methods to populate the object's internal state.

This method is called during object instantiation to prepare the configuration for use throughout the application lifecycle. It serves as the central initialization point that ensures all configuration parameters are properly parsed and validated before the object is ready for use.

## Args:
    filename (str, optional): Path to the configuration file. If None, uses the default configuration file path. Defaults to None.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    ConfigError: Raised when an unknown storage engine is specified or when the required 'path' option is missing while using the 'file_system' engine.
    SystemExit: Raised when deprecated configuration sections are detected (via error() function).

## State Changes:
    Attributes READ: 
    - self._parser (accessed via helper methods)
    
    Attributes WRITTEN:
    - self._parser: Set by _setup_parser() method
    - self._engine: Set by _parse_engine() method  
    - self._path: Set by _parse_path() method
    - self._directory: Set by _parse_directory() method
    - self._apps_to_ignore: Set by _parse_apps_to_ignore() method
    - self._apps_to_sync: Set by _parse_apps_to_sync() method

## Constraints:
    Preconditions:
    - filename must be either a string or None
    - Configuration file must exist and be readable if specified
    - Configuration file must not contain deprecated sections
    
    Postconditions:
    - All internal configuration attributes are initialized
    - The object is ready for use with valid configuration data
    - Invalid configurations will cause early termination with appropriate errors

## Side Effects:
    - Reads configuration file from disk
    - May print error messages to stderr if deprecated configuration sections are detected
    - May terminate the program with SystemExit if deprecated configuration is detected

### `mackup.config.Config.engine` · *method*

## Summary:
Returns the storage engine type as a string, representing the backup destination service.

## Description:
Provides access to the configured storage engine type. This property is read-only and returns a string identifier indicating which cloud storage service or filesystem location should be used for backups. The engine type determines how Mackup locates and interacts with the backup storage directory.

## Args:
    None

## Returns:
    str: The storage engine type, one of:
        - 'dropbox' for Dropbox storage
        - 'google_drive' for Google Drive storage  
        - 'copy' for Copy.com storage
        - 'icloud' for Apple iCloud storage
        - 'file_system' for local filesystem storage

## Raises:
    None

## State Changes:
    Attributes READ: self._engine
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Config object must be properly initialized with a valid configuration file or defaults.
    Postconditions: The returned string is guaranteed to be one of the predefined engine constants.

## Side Effects:
    None

### `mackup.config.Config.path` · *method*

## Summary:
Returns the absolute path to the backup storage location based on the configured storage engine.

## Description:
This property provides access to the root directory path where Mackup stores application configurations. It is computed during object initialization based on the storage engine configuration and returns a string representation of the internal `_path` attribute. The path is determined by the storage engine type (Dropbox, Google Drive, Copy, iCloud, or filesystem) and corresponds to the appropriate cloud storage folder or user-specified filesystem path.

## Args:
    None

## Returns:
    str: The absolute path to the backup storage location as a string.

## Raises:
    None

## State Changes:
    Attributes READ: self._path
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Config object must be properly initialized with a valid configuration.
    Postconditions: The returned value is always a string representing a valid filesystem path.

## Side Effects:
    None

### `mackup.config.Config.directory` · *method*

## Summary:
Returns the configured backup directory path as a string.

## Description:
Provides access to the backup directory configuration, which is parsed from the configuration file during object initialization. This property allows retrieving the directory where Mackup stores application configurations.

## Args:
    None

## Returns:
    str: The absolute path to the backup directory, or the default backup path if not configured.

## Raises:
    ConfigError: When the configuration specifies CUSTOM_APPS_DIR as the directory, which is not allowed.

## State Changes:
    Attributes READ: self._directory
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Config object must be properly initialized with a valid configuration.
    Postconditions: The returned value is always a string representing a valid directory path.

## Side Effects:
    None

### `mackup.config.Config.fullpath` · *method*

*No documentation generated.*

### `mackup.config.Config.apps_to_ignore` · *method*

*No documentation generated.*

### `mackup.config.Config.apps_to_sync` · *method*

## Summary:
Returns a set of application names configured to be synchronized by Mackup.

## Description:
Provides read-only access to the collection of applications that are configured to be backed up and synchronized. This method serves as a property interface to the internal `_apps_to_sync` attribute, ensuring that callers receive a fresh set copy rather than a reference to the internal mutable set.

## Args:
    None

## Returns:
    set[str]: A set containing the names of applications configured for synchronization. Returns an empty set if no applications are explicitly configured.

## Raises:
    None

## State Changes:
    Attributes READ: self._apps_to_sync
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The Config instance must be properly initialized with valid configuration data.
    Postconditions: The returned set is a copy of the internal data, preventing external modification of the internal state.

## Side Effects:
    None

### `mackup.config.Config._setup_parser` · *method*

*No documentation generated.*

### `mackup.config.Config._warn_on_old_config` · *method*

*No documentation generated.*

### `mackup.config.Config._parse_engine` · *method*

*No documentation generated.*

### `mackup.config.Config._parse_path` · *method*

*No documentation generated.*

### `mackup.config.Config._parse_directory` · *method*

*No documentation generated.*

### `mackup.config.Config._parse_apps_to_ignore` · *method*

*No documentation generated.*

### `mackup.config.Config._parse_apps_to_sync` · *method*

*No documentation generated.*

## `mackup.config.ConfigError` · *class*

*No documentation generated.*

