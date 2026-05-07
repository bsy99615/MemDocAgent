# `version.py`

## `imapclient.version._imapclient_version_string` · *function*

## Summary:
Formats a version tuple into a human-readable string representation.

## Description:
Converts a version tuple containing major, minor, micro version numbers and release level into a standard semantic versioning string format. This function is used internally by the IMAPClient library to generate version strings for display or logging purposes.

## Args:
    vinfo (Tuple[int, int, int, str]): A tuple containing four elements:
        - major (int): Major version number
        - minor (int): Minor version number  
        - micro (int): Micro version number
        - releaselevel (str): Release level identifier (e.g., 'final', 'alpha', 'beta')

## Returns:
    str: A formatted version string in the format "X.Y.Z" for final releases or "X.Y.Z-releaselevel" for pre-release versions.

## Raises:
    None explicitly raised, but may raise TypeError if vinfo does not contain exactly 4 elements or if elements are not of expected types.

## Constraints:
    Preconditions:
        - vinfo must be a tuple of exactly 4 elements
        - The first three elements must be integers representing version numbers
        - The fourth element must be a string representing the release level
    Postconditions:
        - Returns a properly formatted semantic version string
        - Final releases omit the release level suffix
        - Pre-release versions include the release level as a suffix

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B[vinfo unpacked into major,minor,micro,releaselevel]
    B --> C{releaselevel == "final"?}
    C -->|Yes| D[Return "%d.%d.%d" format]
    C -->|No| E[Return "%d.%d.%d" + "-" + releaselevel]
```

## Examples:
    >>> _imapclient_version_string((1, 2, 3, "final"))
    '1.2.3'
    >>> _imapclient_version_string((1, 2, 3, "alpha"))
    '1.2.3-alpha'
```

