# `time_utils.py`

## `trailscraper.time_utils.parse_human_readable_time` · *function*

## Summary:
Parses a human-readable date/time string and returns a timezone-aware datetime when possible, or None if the string cannot be parsed.

## Description:
This thin utility wraps dateparser.parse with the setting to prefer timezone-aware results. It centralizes parsing behavior so all code that converts human-friendly timestamps into datetime objects gets consistent timezone handling and failure semantics.

Known callers in this repository:
- None found during a static search of the codebase. (If you add a caller, typical usage is in input normalization or timestamp extraction stages.)

Why this function exists:
- Responsibility boundary: encapsulates the single policy "use dateparser.parse and request timezone-aware datetimes" so callers don't have to repeat the settings or handle parsing semantics themselves.
- Extracting this behavior makes it easy to change parsing settings in one place (for example, to enforce a specific timezone or parsing options) without touching all call sites.

## Args:
    time_string (str|object): Input representing a date/time in a human-friendly format (examples: "2 hours ago", "2021-05-01 14:30", "next Tuesday", "April 3rd 2020 5pm").
        - Required: yes.
        - Allowed values: any string or object that dateparser.parse accepts; non-string objects will be passed through to dateparser.parse (they should be convertible to strings or acceptable by dateparser).
        - No default.

## Returns:
    datetime.datetime or None
    - On successful parse: a datetime.datetime instance. The function calls dateparser.parse(..., settings={'RETURN_AS_TIMEZONE_AWARE': True}), so the returned datetime will be timezone-aware (tzinfo set) when dateparser can determine/apply a timezone.
    - If dateparser cannot interpret the input: returns None.
    - Note: exact tzinfo value depends on dateparser's configuration and the parsed text (e.g., an explicit timezone in the string, or dateparser's default/locale/timezone settings).

## Raises:
    - This wrapper does not explicitly raise exceptions.
    - Exceptions thrown by dateparser.parse (for example, TypeError if an unsupported type is passed and dateparser raises) will propagate to the caller.
    - Callers should treat parse failures as returning None rather than relying on an exception.

## Constraints:
    Preconditions:
    - The caller should provide a value that dateparser.parse can handle (typically a str).
    - If callers require a naive (timezone-unaware) datetime, they must convert the returned tz-aware datetime accordingly; this function requests timezone-aware results.

    Postconditions:
    - The function returns either a datetime.datetime (preferably timezone-aware) or None.
    - No global state is modified.

## Side Effects:
    - None within this wrapper itself: no file, network, stdout I/O, global mutation, or external service calls are performed by this function.
    - Any side effects would only come from dateparser.parse if that library performs them (typical usage does not).

## Control Flow:
flowchart TD
    A[Start: call parse_human_readable_time(time_string)] --> B[Invoke dateparser.parse with RETURN_AS_TIMEZONE_AWARE=True]
    B --> C{dateparser.parse succeeds or returns a datetime?}
    C -- Yes --> D[Return datetime (tz-aware when possible)]
    C -- No (returns None) --> E[Return None]
    B --> F{dateparser.parse raises exception}
    F -- Yes --> G[Exception propagates to caller]
    F -- No --> C

## Examples:
Example 1 — Basic usage and handling parse failure:
    from trailscraper.time_utils import parse_human_readable_time

    dt = parse_human_readable_time("2021-05-01 14:30")
    if dt is None:
        # handle parse failure
        raise ValueError("Unable to parse timestamp")
    # dt is a datetime.datetime (likely timezone-aware)
    # proceed with normalized timestamp handling

Example 2 — Handling human-relative input:
    dt = parse_human_readable_time("2 hours ago")
    if dt is None:
        # fall back to a default, or log and ignore
        dt = datetime.datetime.now(tz=datetime.timezone.utc)

Example 3 — Defensive programming for unexpected input types:
    try:
        dt = parse_human_readable_time(maybe_string)
    except Exception as exc:
        # An unexpected exception from dateparser.parse propagated.
        # Log or convert to a controlled error.
        logger.exception("Failed to parse time input", exc_info=exc)
        dt = None

