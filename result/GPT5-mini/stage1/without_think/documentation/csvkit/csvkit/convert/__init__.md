# `__init__.py`

## `csvkit.convert.__init__.guess_format` · *function*

## Summary:
Determine a file format hint from a filename by inspecting its final extension (or absence of any extension) and return a canonical short identifier or None when the extension is unrecognized.

## Description:
This function encapsulates the single responsibility of mapping a filename to an inferred format label based solely on the last dot-separated suffix.

Known callers within the provided context:
- None identified in the supplied source. Typically this function is used by higher-level file-conversion utilities or CLI entry points that need a quick, best-effort format inference step before dispatching to a parser/reader.

Reason for extraction:
- Isolates extension-to-format mapping logic so callers can reuse and test the inference behavior independently of file reading or conversion logic. It separates concern of format detection from downstream parsing and keeps the conversion pipeline simpler and more testable.

## Args:
    filename (str):
        - A path or filename string to inspect.
        - Expected to be a string; the function calls the string method rfind.
        - Interpretation details:
            * The function searches for the last period ('.') anywhere in the provided string.
            * If there is no period at all, the filename is treated as having no extension.
            * Leading periods (e.g., ".bashrc") are treated like any other period; the portion after the last period is considered the extension.
            * The extension comparison is case-insensitive.

## Returns:
    str or None:
        - Returns the format identifier string when recognized, otherwise None.
        - Possible return values and when they occur:
            * 'fixed' — returned if the filename contains no period at all (no extension).
            * 'csv', 'dbf', 'fixed', 'xls', 'xlsx' — returned when the lowercased extension exactly matches one of these values; the returned value is the extension itself (e.g., extension 'CSV' -> 'csv').
            * 'json' — returned when the lowercased extension is 'json' or 'js'.
            * None — returned when there is an extension that is not in any of the recognized sets (e.g., 'txt', 'gz', 'tar', 'bashrc').

## Raises:
    - AttributeError (or similar): If filename is not a string-like object (for example, None or an integer), calling filename.rfind will raise an exception. The function does not catch or convert this error; callers should validate input types if untrusted input is possible.
    - The function itself contains no explicit raise statements.

## Constraints:
    Preconditions:
        - filename should be a str. The function assumes the presence of the rfind method.
    Postconditions:
        - The return is either one of the recognized format strings ('fixed', 'csv', 'dbf', 'xls', 'xlsx', 'json') or None.
        - No mutation of inputs or external state occurs.

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and makes no external service calls.

## Control Flow:
flowchart TD
    Start --> FindLastPeriod["Call filename.rfind('.') -> last_period"]
    FindLastPeriod --> NoPeriod{"last_period == -1?"}
    NoPeriod -- Yes --> ReturnFixed["Return 'fixed'"]
    NoPeriod -- No --> ExtractExt["extension = substring after last_period; lowercased"]
    ExtractExt --> InKnownSet{"extension in ('csv','dbf','fixed','xls','xlsx')?"}
    InKnownSet -- Yes --> ReturnExt["Return extension (e.g., 'csv')"]
    InKnownSet -- No --> IsJson{"extension in ('json','js')?"}
    IsJson -- Yes --> ReturnJson["Return 'json'"]
    IsJson -- No --> ReturnNone["Return None"]
    ReturnFixed --> End
    ReturnExt --> End
    ReturnJson --> End
    ReturnNone --> End

## Examples:
- Typical known extension:
  - Filename: report.csv  -> returns 'csv'
  - Filename: data.XLSX  -> returns 'xlsx' (case-insensitive)
- No extension:
  - Filename: fixedwidthfile  -> returns 'fixed' (assumes fixed-width when there is no dot)
- Multi-dot names:
  - Filename: archive.tar.gz  -> returns None (final extension 'gz' is unrecognized)
  - Filename: my.data.csv  -> returns 'csv' (last suffix is 'csv')
- Leading dot (hidden files):
  - Filename: .bashrc  -> returns None (treated like an extension of 'bashrc', which is unrecognized)
- JSON alias:
  - Filename: payload.js  -> returns 'json'
- Error handling:
  - If filename is None or not a string, the function will raise an AttributeError when attempting to call rfind; callers should validate or coerce inputs when necessary.

