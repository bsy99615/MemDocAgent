# `mackup.py`

## `mackup.mackup.Mackup` · *class*

*No documentation generated.*

### `mackup.mackup.Mackup.__init__` · *method*

## Summary:
Initializes the Mackup object by setting up configuration, backup folder path, and temporary directory.

## Description:
The `__init__` method serves as the constructor for the Mackup class, establishing the core state needed for the application to operate. It creates a configuration object to determine storage settings, sets up the main backup folder path, and creates a temporary directory for intermediate operations during backup/restore processes.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._config: Assigned a new config.Config() instance
    - self.mackup_folder: Assigned from self._config.fullpath
    - self.temp_folder: Assigned from tempfile.mkdtemp(prefix="mackup_tmp_")

## Constraints:
    Preconditions: None
    Postconditions: 
    - self._config is initialized with a valid Config instance
    - self.mackup_folder points to the configured storage location
    - self.temp_folder contains a valid temporary directory path

## Side Effects:
    - Creates a temporary directory on the filesystem
    - May trigger configuration parsing and validation logic from Config.__init__

### `mackup.mackup.Mackup.check_for_usable_environment` · *method*

*No documentation generated.*

### `mackup.mackup.Mackup.check_for_usable_backup_env` · *method*

*No documentation generated.*

### `mackup.mackup.Mackup.check_for_usable_restore_env` · *method*

*No documentation generated.*

### `mackup.mackup.Mackup.clean_temp_folder` · *method*

## Summary:
Removes the temporary folder used by Mackup for storing temporary files during operations.

## Description:
This method deletes the temporary directory that Mackup creates for staging files during backup or restore operations. It's typically called at the end of a Mackup operation to clean up temporary resources. The method is designed to remove the entire directory tree recursively.

## Args:
    None

## Returns:
    None

## Raises:
    FileNotFoundError: If the temporary folder does not exist when this method is called.
    PermissionError: If the process lacks permissions to delete the temporary folder.
    OSError: If there's a general operating system error during deletion (such as the directory being locked).

## State Changes:
    Attributes READ: self.temp_folder
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.temp_folder attribute must be set to a valid directory path.
    Postconditions: The directory referenced by self.temp_folder is completely removed from the filesystem, or an exception is raised if it cannot be removed.

## Side Effects:
    I/O: Deletes files and directories from the filesystem.

### `mackup.mackup.Mackup.create_mackup_home` · *method*

*No documentation generated.*

### `mackup.mackup.Mackup.get_apps_to_backup` · *method*

*No documentation generated.*

