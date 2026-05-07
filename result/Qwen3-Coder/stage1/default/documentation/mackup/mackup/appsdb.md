# `appsdb.py`

## `mackup.appsdb.ApplicationsDatabase` · *class*

## Summary:
Manages a database of application configurations by parsing .cfg files from standard and custom application directories.

## Description:
The ApplicationsDatabase class serves as a centralized repository for application metadata and their associated configuration file paths. It reads configuration files from two locations: the standard applications directory (defined by APPS_DIR constant) and a user-customizable directory (defined by CUSTOM_APPS_DIR constant). The class processes these .cfg files to extract application names and their associated configuration file paths, supporting both regular and XDG-compliant configuration file specifications.

This class is designed to provide a unified interface for accessing application metadata and their configuration file requirements, making it easier for the mackup tool to manage application-specific backup and restore operations.

## State:
- apps (dict): A dictionary mapping application names (str) to dictionaries containing:
  - name (str): The human-readable name of the application extracted from the "application" section's "name" option
  - configuration_files (set): A set of relative file paths (str) to configuration files for this application
- The apps dictionary is populated during initialization by parsing .cfg files from configured directories

## Lifecycle:
- Creation: Instantiated without arguments; automatically discovers and parses configuration files from standard and custom directories via get_config_files() method
- Usage: Methods are called to retrieve application metadata (names, configuration files) in various formats
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[ApplicationsDatabase.__init__] --> B[get_config_files]
    B --> C[configparser.SafeConfigParser]
    C --> D[config.read(config_file)]
    D --> E[app_name extraction]
    E --> F[app_pretty_name extraction]
    F --> G[configuration_files processing]
    G --> H[Xdg configuration files processing]
    A --> I[ApplicationsDatabase.get_name]
    A --> J[ApplicationsDatabase.get_files]
    A --> K[ApplicationsDatabase.get_app_names]
    A --> L[ApplicationsDatabase.get_pretty_app_names]
```

## Raises:
- ValueError: Raised during initialization when encountering:
  - Unsupported absolute paths in configuration files (both regular and xdg_configuration_files sections)
  - $XDG_CONFIG_HOME environment variable pointing outside the user's home directory

## Example:
```python
# Create the database instance (automatically loads all configs)
db = ApplicationsDatabase()

# Get application names
app_names = db.get_app_names()  # Returns set of raw app names

# Get pretty application names  
pretty_names = db.get_pretty_app_names()  # Returns set of human-readable names

# Get configuration files for a specific app
files = db.get_files("vim")  # Returns set of configuration file paths

# Get the pretty name for an app
name = db.get_name("vim")  # Returns "Vim"
```

### `mackup.appsdb.ApplicationsDatabase.__init__` · *method*

## Summary:
Initializes the ApplicationsDatabase by loading application configuration files and populating internal application metadata.

## Description:
This method constructs the internal database of applications by scanning configuration files in standard and custom application directories. It parses each .cfg file to extract application names and their associated configuration file paths, handling both regular and XDG-compliant configuration files with appropriate validation.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: When encountering absolute paths in configuration files or when $XDG_CONFIG_HOME is not within the user's home directory.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.apps

## Constraints:
    Preconditions:
        - The APPS_DIR and CUSTOM_APPS_DIR constants must be properly defined
        - Configuration files must be readable and properly formatted
        - Environment variable HOME must be set
        - $XDG_CONFIG_HOME (if set) must be within the user's home directory
        
    Postconditions:
        - self.apps is initialized as a dictionary mapping application names to their metadata
        - Each application entry contains 'name' and 'configuration_files' keys
        - All configuration file paths are stored as relative paths (with home directory prefix removed for XDG files)

## Side Effects:
    - Reads configuration files from the filesystem
    - Accesses environment variables (HOME, XDG_CONFIG_HOME)
    - Performs directory listing operations through get_config_files()

### `mackup.appsdb.ApplicationsDatabase.get_config_files` · *method*

## Summary:
Returns a set of absolute file paths to all .cfg configuration files found in the standard and custom applications directories.

## Description:
This function scans two directories for configuration files with the .cfg extension and returns a set containing the absolute paths to these files. It first looks in the custom applications directory (~/Applications) and then in the standard applications directory (relative to the module location). Custom files take precedence over standard files when there are naming conflicts.

## Args:
    None

## Returns:
    set[str]: A set of absolute file paths pointing to .cfg configuration files found in either the standard or custom applications directories.

## Raises:
    None explicitly raised

## State Changes:
    None

## Constraints:
    Preconditions:
        - The APPS_DIR constant must be defined in the constants module
        - The CUSTOM_APPS_DIR constant must be defined in the constants module
        - The process must have appropriate read permissions for both directories
    
    Postconditions:
        - Returns a set of absolute file paths (never None)
        - All returned paths point to existing .cfg files
        - No duplicate paths are returned

## Side Effects:
    - Reads from the filesystem (custom apps directory and standard apps directory)
    - May perform directory listing operations
    - Accesses environment variables (HOME)

### `mackup.appsdb.ApplicationsDatabase.get_name` · *method*

## Summary:
Retrieves the pretty name of a specified application from the database.

## Description:
Returns the human-readable name of an application identified by its internal name. This method provides access to the application's display name stored in the configuration database, which is typically loaded from .cfg files during initialization. The method is part of a set of accessor methods that provide controlled access to application metadata without exposing the internal data structure directly.

Known callers:
- `ApplicationsDatabase.get_pretty_app_names()` - Called during the process of collecting all application display names for presentation purposes
- Direct usage in application logic where the pretty name is needed for user-facing operations

This method exists as a separate function rather than being inlined because it provides a clean abstraction layer over the internal `self.apps` dictionary structure, making the code more readable and maintainable while ensuring consistent access patterns.

## Args:
    name (str): The internal name of the application to retrieve the pretty name for.

## Returns:
    str: The pretty (human-readable) name of the specified application.

## Raises:
    KeyError: When the specified application name does not exist in the database.

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The application name must exist in self.apps dictionary, typically populated during class initialization
    Postconditions: Returns the string value associated with the "name" key for the specified application

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_files` · *method*

## Summary:
Returns the set of configuration file paths associated with a specified application.

## Description:
Retrieves the collection of configuration file paths that belong to the given application. This method provides access to the configuration files defined in the application's configuration file, which are stored in the internal apps dictionary structure.

## Args:
    name (str): The name of the application to retrieve configuration files for.

## Returns:
    set[str]: A set of configuration file path strings associated with the specified application.

## Raises:
    KeyError: When the specified application name does not exist in the database.

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The application name must exist in self.apps dictionary
    Postconditions: Returns a set containing all configuration file paths for the specified application

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_app_names` · *method*

## Summary:
Returns a set of all application names managed by this database instance.

## Description:
Extracts and returns the names of all applications configured in this database. This method provides a clean interface for accessing the collection of available applications without exposing the underlying data structure. It's used internally by other methods like `get_pretty_app_names()` to retrieve all application identifiers before processing them further.

## Args:
    None

## Returns:
    set[str]: A set containing the names of all applications registered in this database instance.

## Raises:
    None

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `self.apps` attribute must be initialized (typically as an empty dict in `__init__`) and populated with application data.
    Postconditions: The returned set contains all application names currently stored in `self.apps`.

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_pretty_app_names` · *method*

## Summary:
Returns a set of human-readable application names from the database.

## Description:
Collects and returns all application pretty names (human-readable display names) from the database. This method provides a convenient way to access all application display names without having to manually iterate through the internal application data structure. It's primarily used for presenting application lists to users or for building UI elements that require human-readable names.

Known callers:
- Direct usage in application logic where a collection of pretty application names is needed for display purposes

This method exists as a separate function rather than being inlined because it encapsulates the logic for transforming internal application identifiers into user-friendly display names, providing a clean abstraction layer that makes the code more readable and maintainable.

## Args:
    None

## Returns:
    set[str]: A set containing the pretty (human-readable) names of all applications registered in this database instance.

## Raises:
    KeyError: When any application name returned by `get_app_names()` does not exist in the internal `self.apps` dictionary.

## State Changes:
    Attributes READ: self.apps
    Method Calls: get_app_names(), get_name()
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The `self.apps` attribute must be properly initialized and populated with application data (typically during class initialization).
    Postconditions: The returned set contains all pretty application names currently stored in `self.apps`.

## Side Effects:
    None

