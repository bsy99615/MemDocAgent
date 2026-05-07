# `version.py`

## `imapclient.version._imapclient_version_string` · *function*

## Summary:
Format a version tuple (major, minor, micro, releaselevel) into a human-readable semantic version string, appending a hyphen and the release-level when it is not "final".

## Description:
This small utility converts a 4-element version tuple into a textual version identifier suitable for display, logging, packaging, or metadata.

Known callers:
- No direct callers are present in the provided source snapshot. Typical usages in a codebase include producing a package __version__ string, formatting version information for error reporting, or embedding into build artifacts.

Why this is a dedicated function:
- Encapsulates the formatting rule (major.minor.micro plus an optional "-releaselevel") in one place so other parts of the codebase can obtain a consistent string representation of version information without duplicating formatting logic.

## Args:
    vinfo (Tuple[int, int, int, str]):
        A 4-tuple containing:
        - major (int): major version number (expected non-negative).
        - minor (int): minor version number (expected non-negative).
        - micro (int): micro/patch version number (expected non-negative).
        - releaselevel (str): release level marker. The code treats the literal string "final" as the indicator that no release-level suffix should be appended; any other string will be appended after a hyphen.

    Notes:
    - The function expects exactly four elements in the tuple. If the tuple is too short or too long, tuple unpacking will raise an exception.
    - Types are not strictly enforced by runtime checks: if non-integers are provided for the first three elements, the integer formatting operator may raise TypeError or ValueError.

## Returns:
    str: A version string in the form "major.minor.micro" when releaselevel == "final", otherwise "major.minor.micro-releaselevel".

    Examples of results:
    - Input (2, 1, 0, "final") -> "2.1.0"
    - Input (2, 1, 0, "beta")  -> "2.1.0-beta"

    Edge cases:
    - If releaselevel is an empty string (""), the function will append a trailing hyphen: "major.minor.micro-".
    - If releaselevel contains characters such as hyphens or spaces, they are used verbatim in the resulting string.

## Raises:
    ValueError: If vinfo cannot be unpacked into four elements (e.g., tuple length != 4).
    TypeError or ValueError: If the first three elements are not integers (or not acceptable to the "%d" integer formatter). Exact exception type depends on the provided values and Python's formatting behavior.
    Any exceptions raised are propagated to the caller; the function does not catch or wrap runtime errors.

## Constraints:
    Preconditions:
    - vinfo must be an iterable of length 4.
    - The first three elements should be values appropriate for integer formatting (typically int).
    - The fourth element should be a string (or at least a value that compares to the string "final" and can be concatenated to a string).

    Postconditions:
    - The returned value is always a str.
    - If releaselevel == "final", the returned string contains exactly two dots and no hyphen suffix.
    - If releaselevel != "final", the returned string contains exactly two dots and one hyphen followed by the releaselevel value.

## Side Effects:
    - None. The function is pure: it performs no I/O, mutates no global state, and makes no external calls.

## Control Flow:
flowchart TD
    Start["Start: receive vinfo"]
    CheckLen["Unpack vinfo into major,minor,micro,releaselevel"]
    FormatBase["Format base string: \"major.minor.micro\""]
    IsFinal["Is releaselevel == \"final\"?"]
    AppendSuffix["Append '-' + releaselevel"]
    ReturnStr["Return version string"]
    Error["Raise/propagate unpack/format error"]

    Start --> CheckLen
    CheckLen -->|unpack success| FormatBase
    CheckLen -->|unpack fails| Error
    FormatBase --> IsFinal
    IsFinal -->|yes| ReturnStr
    IsFinal -->|no| AppendSuffix
    AppendSuffix --> ReturnStr

## Examples:
1) Normal usage — final release
    Input:
        vinfo = (3, 2, 1, "final")
    Result:
        "3.2.1"

2) Pre-release usage
    Input:
        vinfo = (3, 2, 1, "rc1")
    Result:
        "3.2.1-rc1"

3) Handling incorrect tuple length (error handling)
    Input:
        vinfo = (3, 2, 1)  # only three elements
    Behavior:
        Raises ValueError due to failed unpacking; caller should catch and handle it if tuples may be malformed.

4) Handling non-integer version components
    Input:
        vinfo = ("3", 2, 1, "final")
    Behavior:
        The "%d" formatter will attempt to format the first element; providing a string where an integer is expected will result in a TypeError or ValueError. Caller should validate types before calling if necessary.

