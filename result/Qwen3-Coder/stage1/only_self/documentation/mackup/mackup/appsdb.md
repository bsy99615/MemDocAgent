# `appsdb.py`

## `mackup.appsdb.ApplicationsDatabase` · *class*

## Summary:
Manages a database of application configurations by parsing .cfg files from built-in and custom directories.

## Description:
The ApplicationsDatabase class serves as a centralized registry for application configuration metadata. It scans both built-in application configuration files (in APPS_DIR) and user-defined custom configuration files (in CUSTOM_APPS_DIR) to build an in-memory database of applications and their associated configuration file paths. This allows other parts of the mackup system to query application information without having to repeatedly parse configuration files.

This class is designed as a singleton-like abstraction that encapsulates the complexity of configuration file discovery, parsing, and validation. It provides methods to retrieve application names, configuration file lists, and pretty application names.

## State:
- `apps` (dict): Dictionary mapping application names to dictionaries containing:
  - `name` (str): The human-readable name of the application
  - `configuration_files` (set): Set of relative paths to configuration files for this application
- `__init__` parameters: None required
- Class invariants: All stored configuration file paths are relative (no absolute paths allowed), and all XDG configuration paths are properly normalized to be relative to the home directory

## Lifecycle:
- Creation: Instantiate with `ApplicationsDatabase()` - automatically scans and loads all available configuration files
- Usage: Call getter methods like `get_name()`, `get_files()`, `get_app_names()`, and `get_pretty_app_names()`
- Destruction: No explicit cleanup required - uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[ApplicationsDatabase.__init__] --> B[get_config_files]
    B --> C[configparser.SafeConfigParser]
    C --> D[config.read]
    D --> E[config.get("application", "name")]
    E --> F[apps[name]["name"] = app_pretty_name]
    F --> G[apps[name]["configuration_files"] = set()]
    G --> H[config.has_section("configuration_files")]
    H --> I[config.options("configuration_files")]
    I --> J[Path validation and addition]
    J --> K[config.has_section("xdg_configuration_files")]
    K --> L[config.options("xdg_configuration_files")]
    L --> M[Path normalization and addition]
    A --> N[get_name]
    A --> O[get_files]
    A --> P[get_app_names]
    A --> Q[get_pretty_app_names]
```

## Raises:
- `ValueError`: When encountering absolute paths in configuration files or when $XDG_CONFIG_HOME is not within the user's home directory
- `configparser.Error`: When configuration files are malformed (inherited from configparser)

## Example:
```python
# Create the database instance
db = ApplicationsDatabase()

# Get all application names
app_names = db.get_app_names()
print(f"Found {len(app_names)} applications")

# Get configuration files for a specific application
files = db.get_files("vim")
print(f"Vim configuration files: {files}")

# Get pretty application name
pretty_name = db.get_name("vim")
print(f"Pretty name: {pretty_name}")
```

### `mackup.appsdb.ApplicationsDatabase.__init__` · *method*

## Summary:
Initializes the ApplicationsDatabase by loading application configuration files and parsing their metadata into the internal apps dictionary.

## Description:
This method constructs the application database by scanning configuration files in both default and custom application directories. It reads each .cfg file, extracts application metadata such as name and configuration file paths, and stores this information in the internal `self.apps` dictionary. The method handles both standard configuration files and XDG-compliant configuration files with proper validation of paths and environment variables.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: When encountering absolute paths in configuration files or when $XDG_CONFIG_HOME is set to a location outside the user's home directory.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.apps: Populated with application data from configuration files, where each entry contains:
      * "name": The pretty name of the application
      * "configuration_files": A set of configuration file paths associated with the application

## Constraints:
    Preconditions:
    - The ApplicationsDatabase.get_config_files() method must return valid file paths
    - Configuration files must follow the expected .cfg format with proper sections
    - Environment variables must be properly set for path resolution
    
    Postconditions:
    - self.apps is initialized as a dictionary mapping application names to their metadata
    - All configuration file paths are stored as relative paths (with home directory prefix removed for XDG paths)
    - Invalid configuration entries are rejected with appropriate error messages

## Side Effects:
    - Reads configuration files from the filesystem
    - Accesses environment variables (HOME, XDG_CONFIG_HOME)
    - Performs filesystem operations to resolve paths
    - May raise ValueError for malformed configuration files or invalid paths

### `mackup.appsdb.ApplicationsDatabase.get_config_files` · *method*

## Summary:
Retrieves all configuration files (.cfg) from both default and custom application directories, with custom files taking precedence.

## Description:
This function scans two directories for configuration files ending with '.cfg' extension. It first looks in the custom applications directory (typically ~/.config/mackup/custom-apps/) and then in the default applications directory (typically ./apps/). Custom files are prioritized and will override default files with the same basename. This function is designed to be used as a method of the ApplicationsDatabase class, though it is currently implemented as a standalone function.

## Args:
    None

## Returns:
    set[str]: A set of absolute file paths to all .cfg configuration files found in both directories, with custom files taking precedence.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None (this is a standalone function, not a method)
    Attributes WRITTEN: None (this is a standalone function, not a method)

## Constraints:
    Preconditions: 
    - The APPS_DIR constant must be defined and point to a valid directory relative to the module location
    - The CUSTOM_APPS_DIR constant must be defined and point to a valid directory relative to the user's home directory
    - The process must have appropriate read permissions for both directories
    
    Postconditions:
    - Returns a set containing absolute paths to all .cfg files found
    - Custom files are prioritized over default files with identical basenames
    - Empty set is returned if neither directory contains .cfg files

## Side Effects:
    - Reads from the filesystem (both custom and default application directories)
    - May perform directory listing operations
    - Uses environment variable HOME to resolve custom directory path

### `mackup.appsdb.ApplicationsDatabase.get_name` · *method*

## Summary:
Retrieves the pretty name of an application from the database by application identifier.

## Description:
This method provides access to the human-readable name of applications stored in the database. It serves as a lookup mechanism to retrieve application names using their internal identifiers. The method is part of the ApplicationsDatabase class which manages application configuration data.

## Args:
    name (str): The internal identifier/name of the application to look up

## Returns:
    str: The pretty/normalized name of the application

## Raises:
    KeyError: When the specified application name does not exist in the database

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The application identifier must exist in self.apps dictionary
    Postconditions: Returns the string value associated with the "name" key for the given application

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_files` · *method*

## Summary:
Returns the set of configuration file paths associated with a specified application.

## Description:
Retrieves the collection of configuration file paths that belong to the specified application. This method provides access to the configuration files defined in the application's configuration file, which are loaded during the initialization of the ApplicationsDatabase instance.

## Args:
    name (str): The name of the application to retrieve configuration files for.

## Returns:
    set[str]: A set containing the relative paths to configuration files for the specified application.

## Raises:
    KeyError: When the specified application name does not exist in the database.

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The application name must exist in self.apps dictionary
    - The application must have been properly initialized with configuration files
    
    Postconditions:
    - Returns a set of configuration file paths (never None)
    - The returned set is a copy of the internal data structure

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_app_names` · *method*

*No documentation generated.*

### `mackup.appsdb.ApplicationsDatabase.get_pretty_app_names` · *method*

## Summary:
Returns a set of human-readable application names by mapping internal application identifiers to their pretty names.

## Description:
This method retrieves all application names from the database and transforms them into their human-readable form. It serves as a utility for obtaining display-friendly names for all registered applications. The method iterates through all application identifiers returned by `get_app_names()` and maps each to its pretty name using `get_name()`.

## Args:
    None

## Returns:
    set[str]: A set containing the pretty names of all applications registered in the database

## Raises:
    KeyError: When an application identifier exists in the database but its pretty name cannot be retrieved (should not occur under normal circumstances)

## State Changes:
    Attributes READ: self.apps, self.get_app_names(), self.get_name()
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The ApplicationsDatabase instance must be properly initialized with application data
    Postconditions: Returns a set of strings representing human-readable application names

## Side Effects:
    None

