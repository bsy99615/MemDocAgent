# `appsdb.py`

## `mackup.appsdb.ApplicationsDatabase` · *class*

## Summary:
Manages a database of application configurations by parsing .cfg files from built-in and custom directories.

## Description:
The ApplicationsDatabase class serves as a centralized repository for application configuration metadata. It scans both built-in application definitions (in APPS_DIR) and user-defined custom applications (in CUSTOM_APPS_DIR) to build an in-memory database of applications and their associated configuration files. This abstraction allows other parts of the system to query application information without dealing directly with file I/O operations.

This class is designed to be instantiated once during application startup and provides methods to query application metadata such as names and configuration file paths.

## State:
- apps: dict mapping application names to dictionaries containing:
  - "name": str, the human-readable application name
  - "configuration_files": set of str, relative paths to configuration files
- The apps dictionary is populated during initialization from .cfg files

## Lifecycle:
- Creation: Instantiate without arguments; automatically scans and loads configuration files
- Usage: Call getter methods like get_name(), get_files(), get_app_names(), get_pretty_app_names()
- Destruction: No explicit cleanup required; uses standard Python garbage collection

## Method Map:
```mermaid
graph TD
    A[ApplicationsDatabase.__init__] --> B[get_config_files]
    B --> C[os.listdir]
    C --> D[configparser.SafeConfigParser]
    D --> E[config.read]
    E --> F[config.get("application", "name")]
    F --> G[config.has_section("configuration_files")]
    G --> H[config.options("configuration_files")]
    H --> I[Path validation]
    I --> J[config.has_section("xdg_configuration_files")]
    J --> K[config.options("xdg_configuration_files")]
    K --> L[Path processing]
    L --> M[apps dictionary population]
```

## Raises:
- ValueError: When encountering absolute paths in configuration files or invalid $XDG_CONFIG_HOME environment variable values
- FileNotFoundError: When configuration files cannot be read (though this is handled gracefully by configparser)

## Example:
```python
# Create database instance
db = ApplicationsDatabase()

# Get application names
app_names = db.get_app_names()

# Get configuration files for a specific app
files = db.get_files("vim")

# Get pretty application name
pretty_name = db.get_name("vim")
```

### `mackup.appsdb.ApplicationsDatabase.__init__` · *method*

## Summary:
Initializes the ApplicationsDatabase by parsing configuration files and building an in-memory database of applications and their configuration file paths.

## Description:
This constructor method scans configuration files from both standard and custom application directories, parses them using configparser, and builds an internal dictionary mapping application names to their metadata and configuration file paths. The method handles both regular configuration files and XDG-compliant configuration files with appropriate validation checks.

The initialization process occurs during object creation and sets up the `self.apps` attribute with structured data about available applications. This method is designed to be called automatically during instantiation and should not be called manually afterward.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: When encountering absolute paths in configuration files or invalid $XDG_CONFIG_HOME environment variable values
    FileNotFoundError: When configuration files cannot be read (handled gracefully by configparser)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.apps: dict mapping application names to dictionaries containing:
      - "name": str, the human-readable application name
      - "configuration_files": set of str, relative paths to configuration files

## Constraints:
    Preconditions:
    - The APPS_DIR and CUSTOM_APPS_DIR constants must point to valid directories
    - Configuration files must follow the expected .cfg format with proper sections
    - Environment variables like $XDG_CONFIG_HOME must be properly set if used
    
    Postconditions:
    - self.apps contains all applications found in configuration directories
    - All configuration file paths are stored as relative paths
    - Application names are stored in their canonical form (without .cfg extension)

## Side Effects:
    - Reads from the filesystem to access configuration files
    - Performs I/O operations to parse configuration files
    - May raise ValueError for invalid configuration file contents

### `mackup.appsdb.ApplicationsDatabase.get_config_files` · *method*

## Summary:
Collects all configuration files (.cfg) from standard and custom application directories, prioritizing custom configurations.

## Description:
This function scans two directories for configuration files ending with '.cfg' extension. It first looks in the custom applications directory (typically ~/.config/mackup/custom_apps) and then in the standard applications directory (typically ./apps). Custom files take precedence over standard ones, so if a file exists in both locations with the same name, only the custom version is included in the result.

## Args:
    None

## Returns:
    set[str]: A set of absolute file paths to all .cfg configuration files found in both directories, with custom files taking priority.

## Raises:
    None explicitly raised

## State Changes:
    None

## Constraints:
    Preconditions:
    - The module must be properly imported
    - The APPS_DIR constant must point to a valid directory relative to the module location
    - The CUSTOM_APPS_DIR constant must point to a valid directory relative to the user's home directory
    
    Postconditions:
    - Returns a set of absolute file paths to .cfg files
    - Custom files are prioritized over standard files with identical names
    - All returned paths are absolute paths

## Side Effects:
    - Reads from the filesystem to check directory existence and list directory contents
    - May perform I/O operations to access file system directories

### `mackup.appsdb.ApplicationsDatabase.get_name` · *method*

## Summary:
Retrieves the human-readable name of an application from the database.

## Description:
Provides access to the pretty-printed name of a registered application. This method serves as a clean interface for accessing application metadata stored in the database, encapsulating the internal dictionary structure and making the code more readable and maintainable.

The method is typically called during application enumeration, user interface display, or when building lists of available applications. It's commonly used by `get_pretty_app_names()` to retrieve human-readable names for all registered applications.

## Args:
    name (str): The internal application name (key) used to look up the application record in the database.

## Returns:
    str: The human-readable name of the specified application as stored in the configuration files.

## Raises:
    KeyError: When the specified application name does not exist in the database.

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The ApplicationsDatabase instance must be properly initialized with configuration files loaded into self.apps, and the specified application name must exist in the database.
    Postconditions: The method returns the string value associated with the "name" key for the specified application.

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_files` · *method*

*No documentation generated.*

### `mackup.appsdb.ApplicationsDatabase.get_app_names` · *method*

## Summary:
Returns a set of all application names registered in the database.

## Description:
This method provides access to the collection of application names that have been loaded from configuration files. It's designed to be a clean interface for retrieving all available applications without exposing the internal dictionary structure. The method is used primarily to enumerate all supported applications in the system.

## Args:
    None

## Returns:
    set[str]: A set containing the names of all applications registered in the database. Each name corresponds to a key in the internal self.apps dictionary.

## Raises:
    None

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The ApplicationsDatabase instance must be properly initialized with configuration files loaded into self.apps.
    Postconditions: The returned set contains all application names currently stored in the database.

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_pretty_app_names` · *method*

## Summary:
Returns a set of human-readable application names from the database.

## Description:
This method retrieves all application names from the database and transforms them into their corresponding human-readable (pretty) names. It serves as a convenience method to provide access to the formatted application names without requiring direct access to the internal application data structure.

## Args:
    None

## Returns:
    set[str]: A set containing the pretty (human-readable) names of all applications in the database.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The ApplicationsDatabase instance must be properly initialized with application data.
    Postconditions: Returns a set of strings representing pretty application names, with no duplicates.

## Side Effects:
    None

