# `template.py`

## `flower.utils.template.format_time` · *function*

## Summary:
Formats a Unix timestamp with timezone information into a human-readable datetime string.

## Description:
Converts a Unix timestamp to a formatted datetime string including year, month, day, hour, minute, second, microsecond, and timezone name. This utility function extracts the timezone-aware datetime formatting logic to ensure consistent timestamp presentation throughout the application.

## Args:
    time (float): Unix timestamp representing seconds since epoch
    tz (datetime.tzinfo): Timezone information to apply to the timestamp

## Returns:
    str: Formatted datetime string in the format "%Y-%m-%d %H:%M:%S.%f %Z"
         where:
         - %Y is the 4-digit year
         - %m is the 2-digit month
         - %d is the 2-digit day
         - %H is the 24-hour format hour
         - %M is the 2-digit minute
         - %S is the 2-digit second
         - %f is the 6-digit microsecond
         - %Z is the timezone name

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - time must be a valid numeric Unix timestamp
        - tz must be a valid timezone object (datetime.tzinfo instance)
    Postconditions:
        - Returns a string representation of the datetime with timezone information
        - The returned string follows the format "%Y-%m-%d %H:%M:%S.%f %Z"

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[format_time(time, tz)] --> B{Convert timestamp to datetime}
    B --> C{Format datetime to string}
    C --> D[Return formatted string]
```

## Examples:
    >>> from datetime import datetime, timezone
    >>> from pytz import utc
    >>> format_time(1609459200.0, utc)
    '2021-01-01 00:00:00.000000 UTC'
    
    >>> from pytz import timezone as tz
    >>> eastern = tz('US/Eastern')
    >>> format_time(1609459200.0, eastern)
    '2021-01-01 00:00:00.000000 EST'

## `flower.utils.template.humanize` · *function*

## Summary:
Transforms raw data objects into human-readable string representations with optional type-specific formatting and truncation.

## Description:
A versatile utility function that converts various data types into user-friendly string formats. It handles null values, time formatting with timezone support, natural time descriptions, string capitalization, and list serialization. This function centralizes formatting logic to ensure consistent presentation of data across templates and UI components.

## Args:
    obj (Any): The object to be humanized, supporting multiple types including None, numeric timestamps, strings, and lists
    type (str, optional): Type hint for special formatting behavior:
        - 'time[-timezone]': Format timestamp with timezone-aware datetime formatting
        - 'natural-time[-timezone]': Show time difference as natural language (e.g., "2 hours ago")
    length (int, optional): Maximum string length before truncating with ellipsis

## Returns:
    str: Human-readable representation of the input object, potentially truncated based on length parameter

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - When type starts with 'time' or 'natural-time', obj must be convertible to float timestamp
        - When obj is a string, it should not match UUID pattern (UUID_REGEX)
        - When obj is a list, all elements must be int, float, or str types
    Postconditions:
        - Returns a string representation of the input object
        - String length never exceeds specified length parameter when provided

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[humanize(obj, type, length)] --> B{obj is None?}
    B -->|Yes| C[obj = '']
    B -->|No| D{type and starts with 'time'?}
    D -->|Yes| E[tz = type[len('time'):] or current_app.timezone or utc]
    E --> F[obj = format_time(float(obj), tz)]
    D -->|No| G{type and starts with 'natural-time'?}
    G -->|Yes| H[tz = type[len('natural-time'):] or current_app.timezone or utc]
    H --> I[delta = now - datetime.fromtimestamp(float(obj), tz)]
    I --> J{delta < 1 day?}
    J -->|Yes| K[obj = naturaltime(delta)]
    J -->|No| L[obj = format_time(float(obj), tz)]
    G -->|No| M{isinstance(obj, str) and not UUID?}
    M -->|Yes| N[obj = replace('-', ' ').replace('_', ' ')]
    N --> O[obj = uppercase keywords]
    O --> P{obj not in KEYWORDS_DOWN?}
    P -->|Yes| Q[obj = capitalize first letter]
    M -->|No| R{isinstance(obj, list)?}
    R -->|Yes| S{all elements are int/float/str?}
    S -->|Yes| T[obj = join with ', ']
    P -->|No| U[Continue unchanged]
    R -->|No| V[Continue unchanged]
    V --> W{length specified and obj too long?}
    W -->|Yes| X[obj = truncate + ' ...']
    W -->|No| Y[Return obj]
```

## Examples:
    >>> humanize(None)
    ''
    
    >>> humanize(1609459200.0, type='time-UTC')
    '2021-01-01 00:00:00.000000 UTC'
    
    >>> humanize(1609459200.0, type='natural-time-UTC')
    '2 hours ago'  # (if current time is 2 hours later)
    
    >>> humanize('hello-world_test')
    'Hello World Test'
    
    >>> humanize(['a', 'b', 'c'])
    'a, b, c'
    
    >>> humanize('long_string_example', length=10)
    'long_stri...'

