# `application.py`

## `mackup.application.ApplicationProfile` · *class*

## Summary:
Manages backup, restore, and uninstall operations for application configuration files.

## Description:
The ApplicationProfile class encapsulates the operations needed to manage an application's configuration files across three main actions: backup, restore, and uninstall. It operates on a set of files associated with a specific application and uses a Mackup instance to determine storage locations. The class provides methods to backup files to the Mackup storage, restore them back to the user's home directory, and uninstall them by reverting to the original state.

This class serves as a distinct abstraction that separates the concerns of managing individual application profiles from the broader Mackup system, allowing for modular handling of different applications' configuration files.

## State:
- mackup (Mackup): Reference to the Mackup instance that provides storage location information via mackup.mackup_folder
- files (list): List of file paths (relative to home directory) that belong to this application profile
- dry_run (bool): When True, operations are simulated without making actual changes
- verbose (bool): When True, detailed operation information is printed to console

## Lifecycle:
- Creation: Instantiate with a Mackup object, set of file paths, dry_run flag, and verbose flag
- Usage: Call backup(), restore(), or uninstall() methods in sequence as needed
- Destruction: No explicit cleanup required; relies on garbage collection

## Method Map:
```mermaid
graph TD
    A[ApplicationProfile] --> B[backup()]
    A --> C[restore()]
    A --> D[uninstall()]
    B --> E[getFilepaths()]
    C --> E
    D --> E
    E --> F[os.path.join]
```

## Raises:
- AssertionError: Raised in __init__ if mackup is not an instance of Mackup or files is not a set

## Example:
```python
# Create an ApplicationProfile for an application
mackup_instance = Mackup()
app_files = {"./.vimrc", "./.bashrc"}
profile = ApplicationProfile(mackup_instance, app_files, dry_run=False, verbose=True)

# Backup application files
profile.backup()

# Restore application files  
profile.restore()

# Uninstall application (revert to original state)
profile.uninstall()
```

### `mackup.application.ApplicationProfile.__init__` · *method*

## Summary:
Initializes an ApplicationProfile instance with configuration and settings for backup/restore operations.

## Description:
This constructor method sets up the application profile with essential configuration parameters including the Mackup instance, files to process, and operational flags for dry-run and verbose modes. The method validates input types to ensure proper initialization.

## Args:
    mackup (Mackup): Instance of the Mackup class containing configuration and environment settings
    files (set): Set of file paths associated with this application profile
    dry_run (bool): Flag indicating whether to perform a dry run (simulation) instead of actual operations
    verbose (bool): Flag indicating whether to enable verbose logging/output

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    AssertionError: When mackup parameter is not an instance of Mackup class
    AssertionError: When files parameter is not a set type

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.mackup, self.files, self.dry_run, self.verbose

## Constraints:
    Preconditions:
        - mackup parameter must be an instance of Mackup class
        - files parameter must be a set type
    Postconditions:
        - All parameters are stored as instance attributes
        - self.files is converted from set to list for internal processing

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `mackup.application.ApplicationProfile.getFilepaths` · *method*

## Summary:
Returns the absolute file paths for a given filename in the home directory and Mackup backup directory.

## Description:
Constructs and returns a tuple containing the full file paths for a specified filename in both the user's home directory and the Mackup backup directory. This method centralizes path construction logic to avoid duplication across the backup, restore, and uninstall operations.

This method is called during the backup, restore, and uninstall processes to determine where files should be located in the home directory versus where they should be stored in the Mackup backup location.

## Args:
    filename (str): The basename of the file for which to construct paths.

## Returns:
    tuple[str, str]: A tuple containing two string paths:
        - First path: Full path to the file in the user's home directory
        - Second path: Full path to the file in the Mackup backup directory

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: 
        - self.mackup.mackup_folder
    Attributes WRITTEN: 
        - None

## Constraints:
    Preconditions:
        - The `HOME` environment variable must be defined and accessible
        - `self.mackup.mackup_folder` must be a valid directory path
    Postconditions:
        - Returns a tuple of two valid file paths (though not necessarily existing files)
        - Both paths are constructed using os.path.join for proper cross-platform compatibility

## Side Effects:
    None.

### `mackup.application.ApplicationProfile.backup` · *method*

## Summary:
Backs up application files from the user's home directory to the Mackup backup storage, creating symbolic links in the original locations.

## Description:
This method iterates through all tracked application files and backs them up to the Mackup backup folder. It handles various file types (files, directories, symlinks) and manages conflicts by prompting the user for confirmation. The method creates symbolic links in the original locations pointing to the backed-up files, ensuring the original files remain accessible while maintaining backups.

The backup process evaluates each file based on several conditions:
1. If a file exists in the home directory but not in the backup location, it gets backed up
2. If a file exists in both locations and is already properly linked, it's skipped
3. If a file exists in both locations but isn't properly linked, the user is prompted to replace it
4. If a file is a broken symlink, it's skipped with a warning message

## Args:
    None - This is a method of the ApplicationProfile class and operates on instance attributes.

## Returns:
    None - This method performs side effects but does not return a value.

## Raises:
    ValueError: When encountering an unsupported file type during backup operations (specifically when a backup file is neither a file, directory, nor symlink).

## State Changes:
    Attributes READ: self.files, self.verbose, self.dry_run, self.mackup.mackup_folder
    Attributes WRITTEN: None - This method doesn't modify instance attributes directly.

## Constraints:
    Preconditions:
    - The ApplicationProfile instance must be properly initialized with valid mackup, files, dry_run, and verbose attributes
    - All files in self.files must be valid paths relative to the user's home directory
    - The Mackup instance must have a valid mackup_folder attribute
    
    Postconditions:
    - Files in self.files are either backed up to the Mackup folder or skipped due to existing backups
    - Original files are replaced with symbolic links pointing to their backups
    - If dry_run is True, no actual file operations occur but the logic flow is still evaluated

## Side Effects:
    - File I/O operations: copies files to backup location, deletes original files, creates symbolic links
    - Console output: prints backup status messages when verbose is enabled
    - User interaction: prompts for confirmation when replacing existing backup items
    - Potential modification of filesystem: creates/deletes files and directories

### `mackup.application.ApplicationProfile.restore` · *method*

## Summary:
Restores application configuration files from the Mackup backup directory to their original locations in the user's home directory.

## Description:
This method is responsible for restoring application-specific configuration files from the Mackup backup location to their respective positions in the user's home directory. It is typically called during the application restore workflow when a user wants to recover their application settings from a previously backed-up state. The method implements sophisticated logic to handle conflicts with existing files, verifies platform compatibility, and respects dry-run and verbose modes. This separation allows for clear organization of restore logic and enables reuse across different restore scenarios.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: When encountering an unsupported file type during restoration process (when a file is neither a regular file, directory, nor symbolic link)

## State Changes:
    Attributes READ: 
        - self.files: List of filenames to restore
        - self.verbose: Boolean flag for detailed output
        - self.dry_run: Boolean flag to simulate restore without actual changes
        - self.mackup: Reference to the Mackup instance for accessing backup configuration
    Attributes WRITTEN: 
        - None

## Constraints:
    Preconditions:
        - The Mackup backup directory must exist and be accessible
        - The user must have appropriate permissions to modify files in their home directory
        - ApplicationProfile instance must have valid `files` attribute populated with application-specific files
    Postconditions:
        - Files are either restored as symbolic links or left unchanged based on conflict resolution logic
        - No modifications are made to the backup directory
        - User is prompted for confirmation when replacing existing files with backup versions

## Side Effects:
    - Creates symbolic links in the user's home directory pointing to backup files
    - May delete existing files in the home directory when user confirms replacement
    - Prints status messages to stdout based on verbose flag
    - Reads from and writes to the filesystem (creating symlinks, deleting files)
    - May prompt user for interactive confirmation during file replacement decisions

### `mackup.application.ApplicationProfile.uninstall` · *method*

*No documentation generated.*

