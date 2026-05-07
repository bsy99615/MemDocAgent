# `compat.py`

## `src.ydata_profiling.utils.compat.pandas_version_info` · *function*

## Summary:
Return the installed pandas version as a tuple of integer components (e.g., "1.2.3" -> (1, 2, 3)), suitable for numeric comparison.

## Description:
This helper reads the pandas version string from the global name pd (pd.__version__), splits it on dots, converts each segment to an int, and returns the components as a tuple of ints.

Known callers within the codebase:
- A repository-wide search was not available during documentation generation, so no exact call sites were discovered. Typical callers are compatibility and feature-gating code paths that need to branch based on the installed pandas version (for example, selecting different code paths when pandas >= 1.2).

Why this is a separate function:
- Centralizes the parsing and normalization of pandas version strings into a consistent, comparable representation. Callers avoid duplicating parsing logic and handle version comparisons using standard tuple ordering.

Important note about imports in this module:
- The module-level imports provided show "import pandas" (no alias), while the function references pd.__version__. If pd is not defined elsewhere in the module (for example, if pandas was not aliased to pd), calling this function will raise NameError. Callers or module maintainers should ensure pd is defined (e.g., import pandas as pd) or change the function to access pandas.__version__.

## Args:
- None.

## Returns:
- Tuple[int, ...]: A tuple of integers representing each dot-separated numeric segment from pd.__version__ in order.
  - Examples:
    - "1.3.4" -> (1, 3, 4)
    - "1.2" -> (1, 2)
    - "0" -> (0,)
  - The function does not normalize or truncate pre-release/build metadata (e.g., "1.2.0rc1" will cause conversion to fail unless sanitized by the caller).

## Raises:
The function performs no explicit exception handling; the following exceptions may be raised by the expressions in the implementation:

- NameError
  - Trigger: The global name pd is not defined in the module scope when evaluating pd.__version__.

- AttributeError
  - Trigger 1: pd exists but does not have a __version__ attribute.
  - Trigger 2: pd.__version__ exists but is an object that does not support .split (for instance, pd.__version__ is None). Accessing or calling .split will raise AttributeError.

- ValueError
  - Trigger: A dot-separated segment of pd.__version__ is not a string representing a valid integer literal (examples: "1.2rc1", "1.2a", "", "1.beta"). The int(...) conversion on such a segment raises ValueError.

- TypeError (possible)
  - Trigger: If pd.__version__.split(".") yields elements that int(...) cannot accept (for example, unusual types that are neither str nor bytes nor numeric), int(...) may raise TypeError. This is less common but possible for non-standard __version__ implementations.

## Constraints:
Preconditions:
- The global name pd must be defined and reference the pandas module (or another object exposing a string-like __version__ attribute).
- pd.__version__ should be a dot-separated string where each segment intended for conversion is a valid integer literal when numeric conversion is required.

Postconditions:
- On successful return, the result is a tuple of ints corresponding to each numeric segment of pd.__version__, and callers can perform lexicographic numeric comparisons (e.g., returned_tuple >= (1, 2, 0)).

## Side Effects:
- None. The function performs no I/O, does not mutate global state, and makes no external service calls. It only reads the value of pd.__version__.

## Control Flow:
flowchart TD
    Start --> Eval_pd__version__["Evaluate pd.__version__"]
    Eval_pd__version__ --> If_pd_missing{"pd defined?"}
    If_pd_missing -- No --> RAISE_NameError[NameError raised]
    If_pd_missing -- Yes --> Access_version["Call .split('.') on pd.__version__"]
    Access_version --> If_no_split{"pd.__version__ supports .split?"}
    If_no_split -- No --> RAISE_AttributeError[AttributeError raised]
    If_no_split -- Yes --> ForEachSeg["For each segment s in split result"]
    ForEachSeg --> TryInt["Try int(s)"]
    TryInt -- Success --> CollectInts["Collect integer"]
    TryInt -- Fail_ValueError --> RAISE_ValueError[ValueError raised]
    TryInt -- Fail_TypeError --> RAISE_TypeError[TypeError raised]
    CollectInts --> ReturnTuple["Return tuple(ints)"]
    ReturnTuple --> End

## Examples:
Example 1 — Basic usage (happy path)
try:
    v = pandas_version_info()
    if v >= (1, 2, 0):
        # Use code path for pandas >= 1.2.0
        pass
    else:
        # Fallback for older pandas
        pass
except (NameError, AttributeError) as exc:
    # Module-level alias/availability problem or missing __version__
    raise RuntimeError("pandas 'pd' alias or __version__ not available") from exc
except ValueError:
    # Version string contains non-integer segments (e.g., "1.2.0rc1")
    # See Example 2 for a safe parsing approach.

Example 2 — Defensive parsing for pre-release suffixes
# If pandas versions may contain pre-release markers like "1.2.0rc1",
# sanitize segments before converting to int:
def safe_pandas_version_info():
    try:
        ver = pd.__version__
    except NameError:
        raise
    if not isinstance(ver, str):
        raise TypeError("pd.__version__ must be a string for safe parsing")
    segments = []
    for seg in ver.split("."):
        # Keep the leading numeric prefix only (stop at first non-digit)
        prefix = ""
        for ch in seg:
            if ch.isdigit():
                prefix += ch
            else:
                break
        if prefix == "":
            # No numeric component present in this segment
            raise ValueError(f"Non-numeric version segment encountered: {seg!r}")
        segments.append(int(prefix))
    return tuple(segments)

# Use the safe parser instead of the fragile helper when versions may include suffixes:
try:
    v = safe_pandas_version_info()
except Exception:
    # handle errors (fallback, logging, etc.)
    raise

Recommendations:
- Ensure the module defines pd (e.g., import pandas as pd) or update the function to read pandas.__version__ directly to avoid NameError.
- For robust version handling (including pre-releases and build metadata), prefer using a dedicated version parser (for example, packaging.version.parse) and compare Version objects rather than manually parsing integer segments.

