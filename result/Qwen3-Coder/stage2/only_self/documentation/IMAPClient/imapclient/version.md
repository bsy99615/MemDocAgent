# `version.py`

## `imapclient.version._imapclient_version_string` · *function*

## Summary:
Formats a version tuple into a human-readable version string.

## Description:
Converts a version tuple containing major, minor, micro version numbers and release level into a standardized string format. This function is used to create readable version identifiers for the IMAPClient library.

## Args:
    vinfo (Tuple[int, int, int, str]): A tuple containing four elements:
        - major (int): Major version number
        - minor (int): Minor version number  
        - micro (int): Micro version number
        - releaselevel (str): Release level identifier (e.g., "final", "alpha", "beta")

## Returns:
    str: A formatted version string in the format "major.minor.micro" or "major.minor.micro-releaselevel" if releaselevel is not "final"

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - vinfo must be a tuple of exactly 4 elements
        - First three elements must be integers representing version numbers
        - Fourth element must be a string representing the release level
    Postconditions:
        - Returns a properly formatted version string
        - String follows semantic versioning conventions

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B[vinfo = (major, minor, micro, releaselevel)]
    B --> C[v = "%d.%d.%d" % (major, minor, micro)]
    C --> D{releaselevel != "final"?}
    D -->|Yes| E[v += "-" + releaselevel]
    E --> F[Return v]
    D -->|No| F
```

## Examples:
    >>> _imapclient_version_string((1, 2, 3, "final"))
    '1.2.3'
    >>> _imapclient_version_string((1, 2, 3, "beta"))
    '1.2.3-beta'
```

