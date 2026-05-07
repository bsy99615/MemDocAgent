# `versions.py`

## `src.ydata_profiling.utils.versions.pandas_version` · *function*

## Summary:
Returns the installed pandas package version as a list of integers representing each dot-separated numeric component (e.g., [1, 4, 2] for "1.4.2").

## Description:
This helper obtains the version string for the installed "pandas" distribution and converts the dot-separated segments into integers. It is typically used where code needs to perform numeric version comparisons (major/minor/patch) rather than string comparisons.

Known callers within the codebase:
- No direct callers were detected in the inspected snapshot of the repository. If present elsewhere, typical callers are compatibility checks or feature-gating logic that branches behavior based on pandas' major/minor version.

Why this logic is extracted:
- Converting a textual distribution version into a list of integers is a distinct responsibility used by multiple consumers (compatibility checks, conditional imports, test assertions). Extracting it prevents duplicated parsing code and centralizes parsing behavior and its error modes.

## Args:
- None

## Returns:
- list[int]: A list of integers representing the numeric components of the installed pandas version (major, minor, patch, ...).
  - Examples:
    - "1.4.2" -> [1, 4, 2]
    - "2.0"   -> [2, 0]
  - Edge-case return values:
    - An empty list is not produced by the function: if a version string exists, at least one component (converted to int) will be returned.
    - If the version string contains more than three components (e.g., "1.4.2.1"), all numeric components will be returned in order.

## Raises:
- importlib.metadata.PackageNotFoundError:
    - Raised by importlib.metadata.version("pandas") if the "pandas" distribution is not installed in the current environment.
- ValueError:
    - Raised when any segment of the version string cannot be converted to an integer (for example, pre-release or local tags like "1.2.3rc1" or "1.2.3+local").
    - The function does not strip or normalize non-numeric qualifiers; such qualifiers will cause int(...) to raise ValueError.

## Constraints:
- Preconditions:
    - The calling environment must have the "pandas" package installed and discoverable by importlib.metadata.version.
    - The distribution version string returned by importlib.metadata.version must consist of dot-separated components that are pure integers for successful parsing.
- Postconditions:
    - On successful return, the function yields a list of ints representing each numeric component from left to right.
    - No mutation to external state or global variables happens as a result of calling this function.

## Side Effects:
- None: the function performs no I/O, does not mutate global state, and does not call external services. It only queries package metadata via importlib.metadata.version.

## Control Flow:
flowchart TD
    A[Start] --> B[Call importlib.metadata.version("pandas")]
    B -->|Package found| C[Split version string on "." into parts]
    B -->|Package not found| D[Raise PackageNotFoundError]
    C --> E[Attempt to convert each part to int]
    E -->|All parts numeric| F[Return list of ints]
    E -->|Any part non-numeric| G[Raise ValueError]

## Examples:
- Typical successful usage (described in prose):
  Call the function to obtain the numeric version for conditional logic. For example, if the returned value begins with [1, 4], you can assume pandas >= 1.4 and enable code paths that depend on that minimum feature set.

- Error handling (described in prose):
  Wrap the call in a try/except to handle environments where pandas may be absent or the installed version uses non-numeric qualifiers:
  - Catch importlib.metadata.PackageNotFoundError to provide a clear error message or fallback behavior when pandas is not installed.
  - Catch ValueError to handle or normalize non-standard version strings (for example, by parsing with a library that understands PEP 440 if you must support pre-release/local tags).

Notes:
- This function performs a strict numeric parse. If your codebase needs to support PEP 440 pre-releases or local version identifiers (rc, a, b, post, dev, +local), consider using packaging.version.parse or pkg_resources.parse_version and adjust comparisons accordingly.

## `src.ydata_profiling.utils.versions.pandas_major_version` · *function*

## Summary:
Returns the installed pandas distribution's major version number as an integer (the first numeric component of the pandas version).

## Description:
This function delegates to the helper that parses the installed pandas distribution version into a list of integers and returns the first element (major version). It is typically used when code needs a quick numeric check of the major pandas version for compatibility gating or conditional logic (for example, enabling features only for pandas >= 2).

Known callers within the codebase:
- No direct callers were detected in the inspected snapshot. Typical callers (where present) are compatibility checks, feature-gating code paths, and conditional imports that only need the major version.

Why this logic is extracted:
- Extracting the retrieval of the major version into a small helper centralizes a common, simple operation: obtaining the most-significant numeric component from the parsed pandas version. This avoids repeated indexing logic across the codebase and keeps version-parsing responsibilities separated (pandas_version does parsing; pandas_major_version provides a convenient, focused accessor).

## Args:
- None

## Returns:
- int: The major version number of the installed pandas distribution.
  - Typical returns:
    - For parsed version [1, 4, 2] -> returns 1
    - For parsed version [2, 0] -> returns 2
  - Edge-case returns:
    - If the underlying parser returned a list with more components, the first component is returned unchanged.
    - The function never returns None; it returns an int if the underlying call succeeds.

## Raises:
- importlib.metadata.PackageNotFoundError:
    - When the pandas distribution is not installed or not discoverable by importlib.metadata.version, the underlying parser raises this exception which propagates out of this function.
- ValueError:
    - If the underlying version-parsing function raises ValueError while converting textual version components to integers (for example, non-numeric qualifiers like "1.2.3rc1"), that ValueError propagates.
- IndexError:
    - If the underlying pandas_version helper were to return an empty list (contrary to its documented behavior), indexing [0] would raise IndexError. This is an implementation contract violation of the helper but is documented here as a possible (though unexpected) side-effect.

## Constraints:
- Preconditions:
    - The environment should have the pandas package installed and discoverable by importlib.metadata.version; otherwise PackageNotFoundError will be raised.
    - The pandas_version helper must return a non-empty list of integers (the function assumes at least one numeric component).
- Postconditions:
    - On successful return, the integer returned equals the first (major) numeric component from the parsed pandas version.
    - No global state is modified by calling this function.

## Side Effects:
- None: the function performs no I/O, does not mutate global state, and does not perform network or filesystem access. It only calls the version-parsing helper which queries package metadata via importlib.metadata.version.

## Control Flow:
flowchart TD
    A[Start] --> B[Call pandas_version()]
    B -->|Raises PackageNotFoundError| C[Propagate PackageNotFoundError]
    B -->|Raises ValueError| D[Propagate ValueError]
    B -->|Returns list parts| E{Is list non-empty?}
    E -->|Yes| F[Return parts[0] as int]
    E -->|No| G[Raise IndexError]

## Examples:
- Typical usage (described in prose):
  Retrieve the major pandas version to select a code path. For example, call the function and then branch on the returned integer (if returned value >= 2, enable pandas-2-specific logic).

- Error handling (described in prose):
  Wrap the call in try/except to handle environments without pandas or with non-numeric version strings:
  - Catch importlib.metadata.PackageNotFoundError to provide fallback behavior or a clear error message when pandas is not installed.
  - Catch ValueError to detect non-numeric or non-standard version strings (you may then choose to parse using a more lenient/PEP-440-aware parser).
  - Optionally catch IndexError as a defensive measure if you cannot guarantee the helper's contract in all runtime environments.

Notes:
- This function intentionally performs a minimal operation and relies on the pandas_version helper for parsing. If your code requires robust PEP 440 handling (pre-releases, post releases, local version identifiers), prefer using packaging.version or pkg_resources.parse_version instead of relying on strict integer conversion.

## `src.ydata_profiling.utils.versions.is_pandas_1` · *function*

## Summary:
Return True when the installed pandas distribution's major version is 1, otherwise return False.

## Description:
Known callers within the codebase:
- No direct callers were detected in the inspected snapshot. Typical callers (where present) are compatibility checks, feature-gating code paths, and conditional logic that needs to enable or disable pandas-1-specific behavior.

Why this logic is extracted:
- This function encapsulates a common boolean compatibility check (is the installed pandas major version equal to 1?) as a self-documenting helper. Extracting the check prevents repeated comparisons against the numeric major-version value, centralizes the compatibility gate, and makes call sites more readable (callers read as "is pandas 1?" rather than "pandas_major_version() == 1").

## Args:
- None

## Returns:
- bool: True if the installed pandas distribution's major version equals 1, otherwise False.
  - True: when pandas_major_version() returns the integer 1.
  - False: when pandas_major_version() returns any integer not equal to 1.
  - Note: The function does not coerce non-integer results itself — it relies on pandas_major_version() to return an int (or raise).

## Raises:
- importlib.metadata.PackageNotFoundError
    - Propagated from the underlying version-parsing helper when the pandas distribution is not installed or not discoverable by importlib.metadata.version.
- ValueError
    - Propagated if the underlying parsing/conversion to integers fails (for example, non-numeric version components).
- IndexError
    - Propagated if the underlying helper unexpectedly returns an empty list; this indicates a contract violation of the helper but can occur if parsing produced no numeric components.

## Constraints:
- Preconditions:
    - The runtime environment should have pandas installed and discoverable by importlib.metadata.version if a boolean result is expected without exceptions.
    - The helper pandas_major_version() must return a non-empty integer (first numeric component). The function assumes that helper's contract.
- Postconditions:
    - On successful return (no exception), the result is a boolean reflecting whether the installed pandas major version equals 1.
    - No global state is modified by this function.

## Side Effects:
- None. The function performs no I/O, network calls, or global state mutations. It only calls the pandas_major_version helper which may inspect package metadata.

## Control Flow:
flowchart TD
    A[Start] --> B[Call pandas_major_version()]
    B -->|Raises PackageNotFoundError| C[Propagate PackageNotFoundError]
    B -->|Raises ValueError| D[Propagate ValueError]
    B -->|Raises IndexError| E[Propagate IndexError]
    B -->|Returns int major| F{major == 1?}
    F -->|Yes| G[Return True]
    F -->|No| H[Return False]

## Examples:
- Typical usage (prose):
  Use this helper to choose between pandas-1-only code paths and newer pandas logic. For example, if a particular API or behavior is different in pandas 1.x, call this function and branch on the returned boolean to keep compatibility code localized.

- Error-handling example (prose):
  In environments where pandas may be missing or have an unusual version string, callers should guard the call:
  - Catch importlib.metadata.PackageNotFoundError to provide a fallback or a clear error message when pandas is not installed.
  - Catch ValueError when version parsing encounters non-numeric components; consider using a more robust PEP 440 parser in that case.
  - Optionally catch IndexError as a defensive measure if the helper's contract cannot be guaranteed.
  Example flow: try to call the function, if PackageNotFoundError occurs fall back to a safe default (e.g., treat as not pandas 1), if ValueError occurs log the unexpected version format and decide on a fallback policy.

