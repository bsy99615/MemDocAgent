# `template.py`

## `flower.utils.template.format_time` · *function*

## Summary:
Formats a Unix timestamp into a human-readable datetime string with timezone information.

## Description:
Converts a Unix timestamp to a formatted datetime string including microseconds and timezone name. This utility function extracts the time formatting logic to provide consistent datetime display across the application, particularly in templates where timestamps need to be rendered in user-friendly formats.

## Args:
    time (float): Unix timestamp to convert to datetime
    tz (pytz.BaseTzInfo): Timezone object for converting the timestamp

## Returns:
    str: Formatted datetime string in format "%Y-%m-%d %H:%M:%S.%f %Z" where:
         - %Y is the 4-digit year
         - %m is the month (01-12)
         - %d is the day (01-31)
         - %H is the hour (00-23)
         - %M is the minute (00-59)
         - %S is the second (00-59)
         - %f is the microsecond (000000-999999)
         - %Z is the timezone name

## Raises:
    ValueError: If the timestamp is invalid or out of range for the system
    TypeError: If the timestamp is not numeric or timezone is not a valid timezone object
    OSError: If the timestamp represents a date that cannot be represented in the system

## Constraints:
    Preconditions:
    - The `time` parameter must be a valid numeric Unix timestamp
    - The `tz` parameter must be a valid pytz timezone object
    
    Postconditions:
    - Returns a string representation of the datetime with microsecond precision
    - The returned string includes timezone information

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[format_time called] --> B{time parameter valid?}
    B -->|Yes| C[datetime.fromtimestamp(time, tz=tz)]
    C --> D[dt.strftime("%Y-%m-%d %H:%M:%S.%f %Z")]
    D --> E[Return formatted string]
    B -->|No| F[Exception from datetime.fromtimestamp]
```

## Examples:
    # Basic usage with UTC timezone
    result = format_time(1609459200, utc)
    # Returns: "2021-01-01 00:00:00.000000 UTC"
    
    # Usage with a specific timezone
    eastern = timezone('US/Eastern')
    result = format_time(1609459200, eastern)
    # Returns: "2021-01-01 00:00:00.000000 EST"
    
    # Edge case with microseconds
    result = format_time(1609459200.123456, utc)
    # Returns: "2021-01-01 00:00:00.123456 UTC"

## `flower.utils.template.humanize` · *function*

## Summary
Formats and transforms input objects into human-readable strings with optional type-specific processing and length limiting.

## Description
The humanize function processes various data types to convert them into more readable string representations. It supports time formatting with timezone awareness, natural time descriptions, string capitalization, list joining, and text truncation. This utility extracts common formatting logic to provide consistent presentation of data across the application.

## Args
- obj (Any): The object to be humanized. Can be None, time values, strings, or lists. When None, becomes empty string.
- type (str, optional): Type hint for special processing. Supports 'time' and 'natural-time' prefixes with timezone specification. 
- length (int, optional): Maximum length for the resulting string. If exceeded, truncates with ' ...' suffix.

## Returns
- str: A human-readable string representation of the input object, processed according to the specified type and length constraints.

## Raises
- None explicitly raised in the function body.

## Constraints
- Preconditions: The obj parameter should be compatible with the operations performed (e.g., numeric values for time processing).
- Postconditions: The returned value is always a string, with length not exceeding the specified limit if provided.

## Side Effects
- No direct I/O operations or external state mutations.
- Uses timezone information from Celery app configuration when available.

## Control Flow
```mermaid
flowchart TD
    A[Start humanize] --> B{obj is None?}
    B -- Yes --> C[obj = '']
    B -- No --> D{type starts with 'time'?}
    D -- Yes --> E[tz = type suffix]
    E --> F[tz = timezone(tz) or current_app.timezone or utc]
    F --> G[obj = format_time(float(obj), tz)]
    D -- No --> H{type starts with 'natural-time'?}
    H -- Yes --> I[tz = type suffix]
    I --> J[tz = timezone(tz) or current_app.timezone or utc]
    J --> K[delta = now - fromtimestamp(obj, tz)]
    K --> L{delta < 1 day?}
    L -- Yes --> M[obj = naturaltime(delta)]
    L -- No --> N[obj = format_time(float(obj), tz)]
    H -- No --> O{isinstance(obj, str) AND not UUID_REGEX match?}
    O -- Yes --> P[obj = replace('-', ' ') and replace('_', ' ')]
    P --> Q[obj = capitalize keywords from KEYWORDS_UP]
    Q --> R{obj not in KEYWORDS_DOWN?}
    R -- Yes --> S[obj = capitalize first letter]
    O -- No --> T{isinstance(obj, list)?}
    T -- Yes --> U{all elements are int/float/str?}
    U -- Yes --> V[obj = join with ', ']
    T -- No --> W[Continue to length check]
    W --> X{length is not None AND len > length?}
    X -- Yes --> Y[obj = truncate with ' ...']
    X -- No --> Z[Return obj]
```

## Examples
```python
# Basic string humanization
humanize("hello-world")  # Returns "Hello World" (assuming standard keyword handling)

# Time formatting with timezone
humanize(1609459200, type="time-EST")  # Returns formatted time in EST timezone

# Natural time formatting
humanize(1609459200, type="natural-time")  # Returns "2 days ago" or formatted time

# List formatting
humanize([1, 2, 3])  # Returns "1, 2, 3"

# Length limiting
humanize("very long text", length=10)  # Returns "very lo ..."
```

