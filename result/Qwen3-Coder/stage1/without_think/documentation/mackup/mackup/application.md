# `application.py`

## `mackup.application.ApplicationProfile` · *class*

*No documentation generated.*

### `mackup.application.ApplicationProfile.__init__` · *method*

## Summary:
Initializes an ApplicationProfile instance with Mackup configuration, file set, and operational flags.

## Description:
This constructor method sets up the application profile by storing references to the Mackup configuration object, converting the provided file set to a list for internal use, and initializing operational flags. This method serves as the primary initialization point for ApplicationProfile instances, ensuring all required state is properly established before the application profile is used for backup or restore operations.

## Args:
    mackup (Mackup): An instance of the Mackup configuration class that provides storage and environment management capabilities.
    files (set): A set of file paths to be managed by this application profile.
    dry_run (bool): Flag indicating whether operations should be performed in simulation mode without actual changes.
    verbose (bool): Flag indicating whether detailed logging output should be enabled.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    AssertionError: If mackup parameter is not an instance of Mackup class.
    AssertionError: If files parameter is not a set instance.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.mackup: Stores the Mackup configuration instance
    - self.files: Stores the file paths as a list
    - self.dry_run: Stores the dry run flag
    - self.verbose: Stores the verbose flag

## Constraints:
    Preconditions:
    - mackup parameter must be an instance of Mackup class
    - files parameter must be a set instance
    - All file paths in files set should be valid and accessible

    Postconditions:
    - self.mackup attribute contains the provided Mackup instance
    - self.files attribute contains the file paths as a list
    - self.dry_run attribute contains the provided dry run flag
    - self.verbose attribute contains the provided verbose flag

## Side Effects:
    None: This method performs only local attribute assignments and has no external side effects.

### `mackup.application.ApplicationProfile.getFilepaths` · *method*

## Summary:
Returns standardized file paths for an application's configuration file in both the user's home directory and the Mackup backup location.

## Description:
Constructs and returns a tuple containing the full file paths for a given filename in two locations: the user's home directory and the Mackup backup folder. This method centralizes path construction logic used across backup, restore, and uninstall operations for application profiles.

The method is called during the lifecycle of application management operations where files need to be referenced in both their original location (home directory) and backup location (Mackup folder).

## Args:
    filename (str): The name of the configuration file for which to construct paths

## Returns:
    tuple[str, str]: A tuple containing two file paths:
        - First path: Full path to the file in the user's home directory
        - Second path: Full path to the file in the Mackup backup folder

## Raises:
    None explicitly raised

## State Changes:
    - Attributes READ: self.mackup.mackup_folder, os.environ["HOME"]
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: 
        - self.mackup.mackup_folder must be a valid string path
        - os.environ["HOME"] must be defined and accessible
    - Postconditions: 
        - Returns a tuple of two valid file paths constructed using os.path.join
        - Both paths are absolute paths

## Side Effects:
    - None

### `mackup.application.ApplicationProfile.backup` · *method*

## Summary:
Backs up application files from the user's home directory to the Mackup backup location by creating symbolic links.

## Description:
This method iterates through all tracked application files and performs backup operations by copying files to the Mackup backup directory, deleting the original, and creating a symbolic link back to the backup. It handles various file types and conditions including existing backups, file conflicts, and dry-run scenarios.

## Args:
    None - This is a method of the ApplicationProfile class and operates on instance attributes

## Returns:
    None - This method performs side effects but does not return a value

## Raises:
    ValueError: When encountering an unsupported file type in the backup location

## State Changes:
    Attributes READ: self.files, self.verbose, self.dry_run, self.mackup
    Attributes WRITTEN: None - This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
    - The ApplicationProfile instance must be properly initialized with valid mackup, files, dry_run, and verbose attributes
    - Files in self.files must be valid relative paths
    - The Mackup backup folder must be accessible
    
    Postconditions:
    - Files in self.files are either backed up to the Mackup directory or skipped due to existing backups
    - Original files are replaced with symbolic links pointing to the backup location
    - No files remain in the original location after successful backup

## Side Effects:
    - File I/O operations: copies files to backup location, deletes original files, creates symbolic links
    - Console output: prints backup status messages when verbose=True
    - User interaction: prompts for confirmation when replacing existing backups
    - Temporary file creation: uses temporary directories via tempfile module

### `mackup.application.ApplicationProfile.restore` · *method*

## Summary:
Restores application configuration files from backup to their original locations, handling conflicts and platform-specific considerations.

## Description:
Restores application configuration files by creating symbolic links from backed-up files to their original locations in the user's home directory. The method carefully evaluates existing files and handles various scenarios including pre-existing files, broken symbolic links, and platform-specific file restrictions. It provides verbose output and confirmation prompts when appropriate.

This method is called during the application restoration phase of the Mackup workflow, specifically when users want to restore their application configurations from a previously backed-up state.

## Args:
    None explicitly taken (uses instance attributes)

## Returns:
    None

## Raises:
    ValueError: When encountering an unsupported file type during restoration

## State Changes:
    - Attributes READ: self.files, self.verbose, self.dry_run, self.mackup.mackup_folder, os.environ["HOME"]
    - Attributes WRITTEN: None (modifies filesystem through utility functions)

## Constraints:
    - Preconditions:
        - Instance must have valid `self.files` attribute containing filenames to restore
        - Instance must have valid `self.mackup` attribute with `mackup_folder` property
        - User environment must have HOME directory set
    - Postconditions:
        - Files in `self.files` are either restored via symbolic links or skipped based on conditions
        - No changes made to instance state beyond filesystem modifications

## Side Effects:
    - Creates symbolic links in the user's home directory pointing to backup files
    - May delete existing files when user confirms replacement
    - Prints status messages to stdout based on verbosity settings
    - May prompt user for confirmation when replacing existing files
    - Makes filesystem modifications (create/delete symlinks, delete files)

