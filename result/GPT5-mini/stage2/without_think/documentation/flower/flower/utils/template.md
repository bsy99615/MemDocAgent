# `template.py`

## `flower.utils.template.format_time` · *function*

## Summary:
Converts a POSIX timestamp into a timezone-aware formatted timestamp string (YYYY-MM-DD HH:MM:SS.microseconds TZ).

## Description:
This small utility takes a numeric Unix/POSIX timestamp (seconds since the epoch) and a timezone object, constructs a datetime for that instant in the provided timezone, and returns a human-readable formatted string including microseconds and the timezone name.

Known callers within the available codebase:
- No direct callers were found in the scanned repository snapshot. Typical callers in an application using this utility are:
  - Template rendering code that needs to display event times in a particular timezone.
  - Logging or monitoring components that render timestamps for UI or reports.
  - Any code that converts stored numeric timestamps to displayable strings for users.

Why this logic is factored out:
- Keeps formatting/representation logic centralized so multiple templates or UI components can get a consistent string representation of timestamps.
- Separates concerns: callers provide a numeric timestamp and timezone; this function enforces the formatting policy and timezone-aware conversion.

## Args:
    time (int | float):
        POSIX/Unix timestamp: number of seconds since the epoch (1970-01-01T00:00:00 UTC).
        - Allowed values: integers or floats representing seconds. Sub-second precision is supported via float.
        - Behavior on invalid type: passing a non-numeric value will raise a TypeError when passed to datetime.fromtimestamp.
        - Behavior on out-of-range numeric values: may raise ValueError, OSError, or OverflowError depending on platform/implementation.

    tz (datetime.tzinfo):
        A tzinfo-compatible timezone object (for example, a pytz.timezone instance or datetime.timezone/other tzinfo).
        - Must be an object accepted by datetime.fromtimestamp(tz=...).
        - If tz is None or not provided (not applicable here because tz is a required parameter), datetime.fromtimestamp will produce a naive datetime in local time; when tz is provided it will produce an aware datetime in that timezone.
        - The timezone's display name (used for %Z) may be an empty string if the tzinfo implementation does not provide a name.

## Returns:
    str: A formatted timestamp string in the form:
        "YYYY-MM-DD HH:MM:SS.microseconds TZ"
    - microseconds are zero-padded to six digits.
    - TZ is the timezone name as returned by dt.strftime("%Z"); it may be empty if the tzinfo does not define a name.
    - Example returned value: "2021-05-03 14:40:00.123456 UTC"

## Raises:
    TypeError:
        - If `time` is not a numeric type acceptable by datetime.fromtimestamp (e.g., passing a string).
        - If `tz` is an invalid type that datetime.fromtimestamp rejects.

    ValueError / OSError / OverflowError:
        - If `time` is a numeric value outside the platform-supported range for datetime.fromtimestamp.
        - Exact exception type can depend on the Python build and underlying C library/platform.

    Any exception thrown by datetime.fromtimestamp or datetime.strftime will propagate to the caller.

## Constraints:
Preconditions:
    - `time` should be a valid numeric POSIX timestamp (int or float).
    - `tz` should be a tzinfo-compatible object supported by datetime.fromtimestamp.

Postconditions:
    - The function returns a non-null string representing the given instant in the specified timezone.
    - No mutation of inputs or global state occurs.

## Side Effects:
    - None. The function performs no I/O, network calls, global state mutation, or external service interactions.
    - It only constructs datetime objects and returns a formatted string.

## Control Flow:
flowchart TD
    Start([Start]) --> FromTimestamp[Call datetime.fromtimestamp(time, tz=tz)]
    FromTimestamp --> |Success| Strftime[Call dt.strftime("%Y-%m-%d %H:%M:%S.%f %Z")]
    Strftime --> Return([Return formatted string])
    FromTimestamp --> |Raises TypeError/ValueError/OSError/OverflowError| Error([Propagate exception to caller])

## Examples:
- Typical usage (displaying a stored timestamp in UTC):
    from pytz import utc
    s = format_time(1620000000, utc)
    # Example result: "2021-05-03 14:40:00.000000 UTC"

- Handling potential exceptions around out-of-range timestamps:
    try:
        s = format_time(9999999999999999, some_tz)
    except (ValueError, OSError, OverflowError) as e:
        # handle/report invalid timestamp
        s = "invalid timestamp"

- When tz does not provide a name, %Z can be empty:
    # tz that yields no name may produce: "2021-05-03 14:40:00.000000 "

## `flower.utils.template.humanize` · *function*

*No documentation generated.*

