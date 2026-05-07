# `template.py`

## `flower.utils.template.format_time` · *function*

## Summary:
Formats a Unix timestamp with timezone information into a human-readable datetime string.

## Description:
Converts a Unix timestamp to a formatted datetime string with timezone information. This function extracts the logic for timestamp formatting into a reusable utility, allowing consistent datetime display throughout the application while maintaining timezone awareness.

## Args:
    time (float): Unix timestamp representing seconds since epoch.
    tz (pytz.BaseTzInfo): Timezone information to apply to the timestamp.

## Returns:
    str: Formatted datetime string in the format "%Y-%m-%d %H:%M:%S.%f %Z" which includes year, month, day, hour, minute, second, microsecond, and timezone name.

## Raises:
    ValueError: When the timestamp is invalid or cannot be converted to a datetime object in the specified timezone.

## Constraints:
    Preconditions:
        - The time parameter must be a valid numeric timestamp
        - The tz parameter must be a valid timezone object from pytz
    Postconditions:
        - Returns a string representation of the datetime in the specified timezone
        - The returned string always includes microseconds and timezone information

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[format_time(time, tz)] --> B{Valid timestamp?}
    B -->|Yes| C[datetime.fromtimestamp(time, tz)]
    C --> D[dt.strftime("%Y-%m-%d %H:%M:%S.%f %Z")]
    D --> E[Return formatted string]
    B -->|No| F[Raise ValueError]
```

## Examples:
    # Basic usage with UTC timezone
    result = format_time(1609459200, utc)
    # Returns: "2021-01-01 00:00:00.000000 UTC"
    
    # Usage with specific timezone
    eastern = timezone('US/Eastern')
    result = format_time(1609459200, eastern)
    # Returns: "2021-01-01 00:00:00.000000 EST"

## `flower.utils.template.humanize` · *function*

## Summary
Formats objects into human-readable strings with various transformations based on type and formatting options.

## Description
This utility function transforms raw data into user-friendly string representations. It handles multiple data types and formatting styles including time formatting with timezone support, natural time differences, string capitalization, and list joining. The function is designed to be used in templates where clean, readable output is needed.

## Args
- obj (Any): The object to be formatted. Can be None, time values, strings, or lists.
- type (str, optional): Formatting type specifier. Supports 'time' and 'natural-time' prefixes for time-related formatting.
- length (int, optional): Maximum length for the resulting string. Strings exceeding this length will be truncated with ' ...'.

## Returns
- str: A human-readable formatted string representation of the input object.

## Raises
- None explicitly raised in the function body.

## Constraints
- Preconditions: 
  - obj should be compatible with the operations performed (None, numeric timestamps, strings, lists)
  - When type starts with 'time' or 'natural-time', obj should be convertible to float timestamp
- Postconditions:
  - Returns a string representation of the input object
  - String length will not exceed the specified length parameter plus 4 characters for ellipsis

## Side Effects
- None

## Control Flow
```mermaid
flowchart TD
    A[Start humanize] --> B{obj is None?}
    B -- Yes --> C[obj = '']
    B -- No --> D{type and starts with 'time'?}
    D -- Yes --> E[tz = type[len('time'):] or current_app.timezone]
    E --> F[obj = format_time(float(obj), tz)]
    D -- No --> G{type and starts with 'natural-time'?}
    G -- Yes --> H[tz = type[len('natural-time'):] or current_app.timezone]
    H --> I[delta = datetime.now(tz) - datetime.fromtimestamp(float(obj), tz)]
    I --> J{delta < 1 day?}
    J -- Yes --> K[obj = naturaltime(delta)]
    J -- No --> L[obj = format_time(float(obj), tz)]
    G -- No --> M{isinstance(obj, str) and not UUID?}
    M -- Yes --> N[obj = replace('-', ' ').replace('_', ' ')]
    N --> O[obj = uppercase KEYWORDS_UP matches]
    O --> P{obj and obj not in KEYWORDS_DOWN?}
    P -- Yes --> Q[obj = capitalize first letter]
    M -- No --> R{isinstance(obj, list)?}
    R -- Yes --> S{all elements are int/float/str?}
    S -- Yes --> T[obj = join with ', ']
    R -- No --> U[Continue to length check]
    U --> V{length is not None and len(obj) > length?}
    V -- Yes --> W[obj = truncate with ' ...']
    V -- No --> X[Return obj]
```

## Examples
```python
# Basic string formatting
humanize("hello_world")  # Returns "Hello World"

# Time formatting with timezone
humanize(1609459200, type="time-EST")  # Returns formatted time string

# Natural time formatting
humanize(1609459200, type="natural-time")  # Returns "2 days ago" or similar

# List formatting
humanize([1, 2, 3])  # Returns "1, 2, 3"

# Length truncation
humanize("very_long_string", length=10)  # Returns "very_lo ..."
```

