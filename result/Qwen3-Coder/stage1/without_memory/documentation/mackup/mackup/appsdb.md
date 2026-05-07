# `appsdb.py`

## `mackup.appsdb.ApplicationsDatabase` · *class*

*No documentation generated.*

### `mackup.appsdb.ApplicationsDatabase.__init__` · *method*

## Summary:
Initializes the ApplicationsDatabase by reading configuration files and populating application metadata.

## Description:
This method sets up the database by scanning for .cfg configuration files in both standard and custom application directories. It parses each configuration file to extract application names and their associated configuration file paths, storing this information in the self.apps dictionary. The method handles both regular configuration files and XDG configuration files with appropriate validation.

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
    - Configuration files must follow the expected .cfg format with "application" section containing a "name" option
    - Configuration files must not contain absolute paths in configuration_files sections
    - Configuration files must not contain absolute paths in xdg_configuration_files sections
    - $XDG_CONFIG_HOME environment variable must either be unset or point to a location within the user's home directory
    
    Postconditions:
    - self.apps dictionary is populated with application metadata
    - Each application entry contains "name" and "configuration_files" keys
    - All configuration file paths are stored as relative paths

## Side Effects:
    - Reads configuration files from disk
    - Accesses environment variables (HOME, XDG_CONFIG_HOME)
    - May raise ValueError exceptions during processing

### `mackup.appsdb.ApplicationsDatabase.get_config_files` · *method*

*No documentation generated.*

### `mackup.appsdb.ApplicationsDatabase.get_name` · *method*

## Summary:
Retrieves the human-readable name of a specified application from the database.

## Description:
This method provides access to the pretty-printed name of an application stored in the database. It is used internally by other methods like `get_pretty_app_names()` to retrieve application names for display purposes.

## Args:
    name (str): The key used to identify the application in the database

## Returns:
    str: The human-readable name of the specified application

## Raises:
    KeyError: When the specified application name does not exist in the database

## State Changes:
    Attributes READ: self.apps
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The application name must exist as a key in self.apps dictionary
    Postconditions: Returns the string value associated with the "name" key for the specified application

## Side Effects:
    None

### `mackup.appsdb.ApplicationsDatabase.get_files` · *method*

*No documentation generated.*

### `mackup.appsdb.ApplicationsDatabase.get_app_names` · *method*

*No documentation generated.*

### `mackup.appsdb.ApplicationsDatabase.get_pretty_app_names` · *method*

## Summary:
Returns a set of human-readable application names for all registered applications.

## Description:
This method provides access to the pretty (human-readable) names of all applications stored in the database. It transforms the internal application identifiers into their corresponding user-friendly names by leveraging the existing `get_app_names()` and `get_name()` methods.

The method is designed as a separate utility to encapsulate the logic of converting internal application names to their pretty representations, making the code more readable and maintainable by centralizing this transformation logic.

## Args:
    None

## Returns:
    set[str]: A set containing the pretty names of all registered applications.

## Raises:
    KeyError: If any application name returned by `get_app_names()` does not exist in the internal `self.apps` dictionary.

## State Changes:
    Attributes READ: 
    - self.apps (accessed indirectly via get_app_names() and get_name())
    
    Attributes WRITTEN: 
    - None

## Constraints:
    Preconditions:
    - The ApplicationsDatabase instance must be properly initialized with application data
    - All application names returned by `get_app_names()` must exist in `self.apps`
    
    Postconditions:
    - Returns a set of strings representing pretty application names
    - The returned set contains no duplicates (as it's a set)

## Side Effects:
    None

