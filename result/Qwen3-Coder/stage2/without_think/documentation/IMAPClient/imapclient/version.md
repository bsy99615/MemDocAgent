# `version.py`

## `imapclient.version._imapclient_version_string` · *function*

## Summary:
Formats a version tuple into a semantic version string representation.

## Description:
Converts a version tuple containing major, minor, and micro version numbers along with a release level into a standardized version string format. This function is used internally by the IMAPClient library to generate human-readable version identifiers.

## Args:
    vinfo (Tuple[int, int, int, str]): A tuple containing four elements:
        - major (int): Major version number
        - minor (int): Minor version number  
        - micro (int): Micro version number
        - releaselevel (str): Release level identifier (e.g., "final", "alpha", "beta")

## Returns:
    str: A formatted version string in the format "X.Y.Z" for final releases or "X.Y.Z-releaselevel" for pre-release versions.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - The input tuple must contain exactly 4 elements
        - All numeric elements (major, minor, micro) must be non-negative integers
        - The releaselevel must be a string
    
    Postconditions:
        - Returns a properly formatted semantic version string
        - The returned string follows standard versioning conventions

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B[vinfo = (major,minor,micro,releaselevel)]
    B --> C[v = "%d.%d.%d" % (major,minor,micro)]
    C --> D{releaselevel != "final"?}
    D -->|Yes| E[v += "-" + releaselevel]
    E --> F[Return v]
    D -->|No| F
```

## Examples:
    >>> _imapclient_version_string((1, 2, 3, "final"))
    '1.2.3'
    
    >>> _imapclient_version_string((1, 2, 3, "alpha"))
    '1.2.3-alpha'
    
    >>> _imapclient_version_string((2, 0, 1, "beta"))
    '2.0.1-beta'
```

