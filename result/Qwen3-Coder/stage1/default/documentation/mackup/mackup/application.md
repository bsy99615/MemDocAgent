# `application.py`

## `mackup.application.ApplicationProfile` · *class*

## Summary:
Manages file operations for application configuration files in the Mackup system.

## Description:
The ApplicationProfile class coordinates backup, restore, and uninstall operations for a set of application configuration files. It maintains references to the Mackup storage system and manages file operations between user home directories and backup storage.

## State:
- mackup (Mackup): Reference to the main Mackup instance containing configuration and storage paths
- files (list): List of file paths (relative to home directory) that belong to this application profile
- dry_run (bool): Flag indicating whether operations should be simulated without making actual changes
- verbose (bool): Flag indicating whether detailed operation information should be printed

## Lifecycle:
- Creation: Instantiate with a Mackup object, set of file paths, and boolean flags for dry_run and verbose modes
- Usage: Call backup(), restore(), or uninstall() methods to perform file operations
- Destruction: No explicit cleanup required

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
- AssertionError: When mackup parameter is not an instance of Mackup class
- AssertionError: When files parameter is not a set
- ValueError: When encountering unsupported file types during backup operations

## Example:
```python
# Create an application profile for managing vim configuration
mackup_instance = Mackup()
vim_files = {"vimrc", ".vimrc"}
profile = ApplicationProfile(mackup_instance, vim_files, dry_run=False, verbose=True)

# Perform backup operation
profile.backup()

# Perform restore operation  
profile.restore()

# Perform uninstall operation
profile.uninstall()
```

### `mackup.application.ApplicationProfile.__init__` · *method*

## Summary:
Initializes an ApplicationProfile instance with configuration and operational parameters for managing application files.

## Description:
Configures the ApplicationProfile object with references to the Mackup storage system and sets up operational flags for backup, restore, and uninstall operations. This method validates input parameters and establishes the foundation for subsequent file management operations by storing essential configuration data.

## Args:
    mackup (Mackup): Instance of the Mackup class containing storage configuration and paths
    files (set): Set of file paths (relative to home directory) belonging to this application profile
    dry_run (bool): Flag indicating whether operations should be simulated without making actual changes
    verbose (bool): Flag indicating whether detailed operation information should be printed

## Returns:
    None

## Raises:
    AssertionError: When mackup parameter is not an instance of Mackup class
    AssertionError: When files parameter is not a set

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.mackup: Stores reference to the Mackup instance
    - self.files: Converts set of file paths to list and stores them
    - self.dry_run: Stores the dry run flag
    - self.verbose: Stores the verbose flag

## Constraints:
    Preconditions:
    - mackup parameter must be a valid Mackup instance
    - files parameter must be a set of valid file path strings
    - All file paths in files must be relative to the user's home directory
    
    Postconditions:
    - Instance attributes are properly initialized with validated input values
    - self.files is converted from set to list for consistent iteration behavior
    - All validation assertions pass successfully

## Side Effects:
    None

### `mackup.application.ApplicationProfile.getFilepaths` · *method*

## Summary:
Returns absolute file paths for a given filename in both the user's home directory and the Mackup backup directory.

## Description:
This method constructs and returns a tuple containing two absolute file paths for a specified filename: one pointing to the location in the user's home directory and another pointing to the corresponding location within the Mackup backup directory. This allows applications to easily access both the original and backup versions of configuration files.

The method is used during the backup and restore processes to determine where files should be located in both the user's environment and the backup storage area.

## Args:
    filename (str): The name of the file (including extension) for which to construct paths.

## Returns:
    tuple[str, str]: A tuple containing two string paths:
        - First path: Full path to the file in the user's home directory
        - Second path: Full path to the file in the Mackup backup directory

## Raises:
    KeyError: If the HOME environment variable is not set.
    AttributeError: If self.mackup or self.mackup.mackup_folder does not exist.

## State Changes:
    Attributes READ: 
        - self.mackup.mackup_folder
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The HOME environment variable must be set
        - self.mackup must be an object with a mackup_folder attribute
        - filename should be a string-like object that can be joined with paths
        
    Postconditions:
        - Both returned paths are absolute file paths
        - The second path is within the Mackup backup directory
        - The first path is within the user's home directory

## Side Effects:
    None

### `mackup.application.ApplicationProfile.backup` · *method*

## Summary:
Backs up application configuration files from the user's home directory to the Mackup backup storage, creating symbolic links in the original locations.

## Description:
This method iterates through all tracked files for an application profile and backs them up to the Mackup storage directory. It handles both new files and existing backups, prompting for confirmation when replacing existing backup files. The method creates symbolic links in the original locations pointing to the backed-up files, ensuring that the application continues to work normally while maintaining backups.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: When encountering an unsupported file type in the backup directory during replacement operations.

## State Changes:
    Attributes READ: 
    - self.files: List of filenames to process
    - self.verbose: Boolean flag for verbose output
    - self.dry_run: Boolean flag for dry-run mode
    - self.mackup: Object containing backup storage information
    - self.mackup.mackup_folder: Path to the Mackup backup directory
    
    Attributes WRITTEN: 
    - None (this method does not modify any instance attributes directly)

## Constraints:
    Preconditions:
    - The ApplicationProfile instance must be properly initialized with required attributes
    - The Mackup storage directory must be accessible
    - Files in self.files must be valid paths relative to the user's home directory
    
    Postconditions:
    - All files in self.files are either backed up to the Mackup storage or skipped due to existing backups
    - Original files are replaced with symbolic links pointing to their backups
    - Backup files are created in the Mackup storage directory

## Side Effects:
    - Creates directories in the Mackup backup storage if they don't exist
    - Modifies filesystem by copying files to backup storage
    - Modifies filesystem by deleting original files and creating symbolic links
    - May prompt user for confirmation when replacing existing backups
    - Prints status messages to stdout based on verbose setting

### `mackup.application.ApplicationProfile.restore` · *method*

## Summary:
Restores application configuration files from backup to their original locations in the user's home directory.

## Description:
This method iterates through all tracked application files and restores them from the Mackup backup directory to their respective locations in the user's home directory. It handles various scenarios including replacing existing files, creating symbolic links, and providing user confirmation when conflicts occur. The method respects platform-specific file syncing restrictions and dry-run modes.

## Args:
    None - This is a method of the ApplicationProfile class and operates on instance attributes

## Returns:
    None - This method performs file operations and does not return a value

## Raises:
    ValueError - When encountering an unsupported file type during restoration process

## State Changes:
    Attributes READ: self.files, self.dry_run, self.verbose
    Attributes WRITTEN: None - This method doesn't modify instance attributes directly

## Constraints:
    Preconditions: 
    - The ApplicationProfile instance must be properly initialized with valid mackup, files, dry_run, and verbose attributes
    - Backup files must exist in the Mackup backup directory
    - The user must have appropriate permissions to create symbolic links and modify files in the home directory
    
    Postconditions:
    - Files in the home directory will be replaced with symbolic links pointing to backup files when restoration conditions are met
    - User will be prompted for confirmation when replacing existing files
    - No changes will be made if dry_run is enabled

## Side Effects:
    - Creates symbolic links in the user's home directory pointing to backup files
    - May delete existing files in the home directory when user confirms replacement
    - Prints status messages to stdout based on verbose flag
    - Prompts user for confirmation via stdin when replacing existing files

### `mackup.application.ApplicationProfile.uninstall` · *method*

## Summary:
Reverts application configuration files from backup by copying them back to their original locations.

## Description:
This method restores application configuration files from the Mackup backup directory back to their original locations in the user's home directory. It iterates through all tracked files and performs restoration only when both the backup file and original file exist. The operation effectively undoes a previous backup by replacing the original files with their backed-up versions.

The method is typically called during the application uninstallation process to clean up and restore user configuration files to their original state.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
        - self.files
        - self.verbose
        - self.dry_run
    Attributes WRITTEN: 
        - None

## Constraints:
    Preconditions:
        - The ApplicationProfile instance must be properly initialized with valid mackup folder and files
        - The backup files must exist in the Mackup backup directory
        - The original files must exist in the user's home directory (when not in dry-run mode)
        
    Postconditions:
        - Original files are replaced with backup versions when both exist
        - No changes occur when in dry-run mode
        - Files are only restored when both backup and original exist

## Side Effects:
    - File I/O operations: Deletes original files and copies backup files to original locations
    - Prints status messages to stdout when verbose mode is enabled

