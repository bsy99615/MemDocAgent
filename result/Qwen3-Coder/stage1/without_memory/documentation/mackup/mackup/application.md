# `application.py`

## `mackup.application.ApplicationProfile` · *class*

*No documentation generated.*

### `mackup.application.ApplicationProfile.__init__` · *method*

## Summary:
Initializes an ApplicationProfile instance with configuration and file management settings.

## Description:
Configures an ApplicationProfile object with the necessary components for managing application backups and restores. This constructor sets up the core state needed for file operations including the Mackup environment, target files, and operational flags.

## Args:
    mackup (Mackup): The main Mackup configuration and environment manager instance
    files (set): Set of file paths to be managed by this application profile
    dry_run (bool): When True, performs all operations except actual file modifications
    verbose (bool): When True, provides detailed logging output during operations

## Returns:
    None: This method initializes instance attributes and does not return a value

## Raises:
    AssertionError: If mackup parameter is not an instance of Mackup class
    AssertionError: If files parameter is not a set instance

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.mackup, self.files, self.dry_run, self.verbose

## Constraints:
    Preconditions:
        - mackup must be an instance of the Mackup class
        - files must be a set containing file path strings
    Postconditions:
        - All parameters are stored as instance attributes
        - self.files is converted from set to list for internal processing

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `mackup.application.ApplicationProfile.getFilepaths` · *method*

*No documentation generated.*

### `mackup.application.ApplicationProfile.backup` · *method*

*No documentation generated.*

### `mackup.application.ApplicationProfile.restore` · *method*

*No documentation generated.*

### `mackup.application.ApplicationProfile.uninstall` · *method*

*No documentation generated.*

