# `template.py`

## `flower.utils.template.format_time` · *function*

## Summary:
Formats a Unix timestamp into a human-readable datetime string with timezone information.

## Description:
Converts a Unix timestamp to a formatted datetime string using the specified timezone. This function extracts the logic for timestamp formatting to provide a consistent representation of time values throughout the application, ensuring uniform display of timestamps across different modules.

## Args:
    time (float): Unix timestamp representing seconds since epoch.
    tz (datetime.tzinfo): Timezone information to apply to the timestamp.

## Returns:
    str: Formatted datetime string in the format "%Y-%m-%d %H:%M:%S.%f %Z" where:
         - %Y-%m-%d represents year-month-day
         - %H:%M:%S represents hour:minute:second
         - %f represents microseconds
         - %Z represents timezone name

## Raises:
    ValueError: Raised by datetime.fromtimestamp() when the timestamp is invalid (e.g., out of range).

## Constraints:
    Preconditions:
        - The `time` argument must be a valid numeric Unix timestamp.
        - The `tz` argument must be a valid timezone object from the pytz library or datetime.timezone.
    Postconditions:
        - The returned string will always follow the format "%Y-%m-%d %H:%M:%S.%f %Z".
        - The timezone information in the result will match the provided timezone.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[format_time(time, tz)] --> B{Convert timestamp to datetime}
    B --> C{Format datetime to string}
    C --> D[Return formatted string]
```

## Examples:
    >>> format_time(1609459200, utc)
    '2021-01-01 00:00:00.000000 UTC'
    
    >>> format_time(1609459200, timezone('US/Eastern'))
    '2020-12-31 19:00:00.000000 EST'
    
    >>> format_time(1609459200.123456, utc)
    '2021-01-01 00:00:00.123456 UTC'

## `flower.utils.template.humanize` · *function*

## Summary:
Transforms various data types into human-readable formats with optional truncation.

## Description:
The humanize function processes different input types (None, time values, natural time deltas, strings, lists) and converts them into more readable formats. It handles timezone-aware timestamp conversion, natural time formatting for recent timestamps, string capitalization, and list-to-comma-separated-string conversion. This extraction allows consistent presentation formatting across the application while keeping the core logic centralized.

## Args:
    obj (Any): Input object to be humanized, can be None, timestamp, string, or list.
    type (str, optional): Type hint for special processing. Supports 'time' and 'natural-time' prefixes with timezone specification.
    length (int, optional): Maximum length for the resulting string. If exceeded, truncates with ' ...' suffix.

## Returns:
    str: Human-readable representation of the input object, potentially truncated based on length parameter.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
        - When type starts with 'time' or 'natural-time', obj must be convertible to float.
        - When obj is a list, all elements must be int, float, or str.
        - When type specifies a timezone, it must be a valid pytz timezone identifier.
    Postconditions:
        - Returns a string representation regardless of input type.
        - String truncation respects the length limit when specified.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[humanize(obj, type, length)] --> B{obj is None?}
    B -->|Yes| C[obj = '']
    B -->|No| D{type and starts with 'time'?}
    D -->|Yes| E[tz = type[len('time'):]...]
    E --> F[obj = format_time(float(obj), tz)]
    D -->|No| G{type and starts with 'natural-time'?}
    G -->|Yes| H[tz = type[len('natural-time'):]...]
    H --> I[delta = datetime.now(tz) - datetime.fromtimestamp(float(obj), tz)]
    I --> J{delta < timedelta(days=1)?}
    J -->|Yes| K[obj = naturaltime(delta)]
    J -->|No| L[obj = format_time(float(obj), tz)]
    G -->|No| M{isinstance(obj, str) and not UUID?}
    M -->|Yes| N[obj = replace('-', ' ').replace('_', ' ')]
    N --> O[obj = re.sub(KEYWORDS_UP, lambda m: m.group(0).upper(), obj)]
    O --> P{obj and obj not in KEYWORDS_DOWN?}
    P -->|Yes| Q[obj = obj[0].upper() + obj[1:]]
    M -->|No| R{isinstance(obj, list)?}
    R -->|Yes| S{all elements int/float/str?}
    S -->|Yes| T[obj = ', '.join(map(str, obj))]
    R -->|No| U[Continue to length check]
    U --> V{length is not None and len(obj) > length?}
    V -->|Yes| W[obj = obj[:length-4] + ' ...']
    V -->|No| X[Return obj]
```

## Examples:
    >>> humanize(None)
    ''
    
    >>> humanize(1609459200, type='time-US/Eastern')
    '2021-01-01 00:00:00.000000 EST'
    
    >>> humanize(1609459200, type='natural-time')
    '2 days ago'
    
    >>> humanize('hello-world_test')
    'Hello World Test'
    
    >>> humanize([1, 2, 3])
    '1, 2, 3'
    
    >>> humanize('long_string_example', length=10)
    'long_stri ...'

