# `time_utils.py`

## `trailscraper.time_utils.parse_human_readable_time` · *function*

## Summary:
Converts human-readable time strings into timezone-aware datetime objects.

## Description:
Parses natural language time expressions (like "today at 3 PM" or "next Monday") into timezone-aware datetime objects using the dateparser library. This function serves as a standardized interface for time parsing throughout the application, ensuring consistent timezone handling by enforcing the RETURN_AS_TIMEZONE_AWARE setting.

## Args:
    time_string (str): A human-readable time expression that dateparser can interpret, such as "yesterday", "tomorrow 2:30 PM", or "2023-12-25".

## Returns:
    datetime: A timezone-aware datetime object representing the parsed time. The timezone information is preserved from the input when available, or defaults to UTC.

## Raises:
    Exception: When the input time_string cannot be parsed by dateparser. The specific exception type depends on dateparser's behavior.

## Constraints:
    Preconditions:
    - The input time_string must be a valid string that dateparser can parse
    - The string should represent a recognizable time expression
    
    Postconditions:
    - The returned datetime object will have timezone information attached
    - The datetime object will be timezone-aware (not naive)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input time_string] --> B{dateparser.parse(settings={'RETURN_AS_TIMEZONE_AWARE': True})}
    B --> C[Return timezone-aware datetime]
```

## Examples:
    >>> parse_human_readable_time("today at 3 PM")
    datetime.datetime(2023, 10, 15, 15, 0, tzinfo=<UTC>)
    
    >>> parse_human_readable_time("next Monday")
    datetime.datetime(2023, 10, 23, 0, 0, tzinfo=<UTC>)
```

