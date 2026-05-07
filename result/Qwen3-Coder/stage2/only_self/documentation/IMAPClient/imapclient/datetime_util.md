# `datetime_util.py`

## `imapclient.datetime_util.parse_to_datetime` · *function*

## Summary:
Parses an IMAP timestamp byte string into a timezone-aware datetime object, with optional normalization to local system timezone.

## Description:
Converts raw IMAP timestamp bytes into a Python datetime object, handling timezone information appropriately. This function serves as a central utility for parsing datetime data received from IMAP servers, ensuring proper timezone handling and optional normalization to local system time.

The function first normalizes the timestamp format using `_munge()` to handle dotted timezone formats, then parses it using `parsedate_tz()`. It constructs a timezone-aware datetime object and optionally normalizes it to the local system timezone when requested.

This logic is extracted into its own function to centralize datetime parsing and timezone handling, ensuring consistent behavior across the IMAP client when processing timestamps from various server responses.

## Args:
    timestamp (bytes): Raw byte string containing an IMAP timestamp, typically in RFC 2822 format
    normalise (bool): When True (default), converts timezone-aware datetimes to local system timezone before returning. When False, preserves original timezone information

## Returns:
    datetime: A timezone-aware datetime object representing the parsed timestamp. If normalise=True and timezone information exists, the returned datetime will be naive (no timezone) but representing the same moment in local system time.

## Raises:
    ValueError: When the timestamp cannot be parsed by the underlying parsing function, indicating invalid timestamp format

## Constraints:
    Preconditions:
        - Input timestamp must be valid bytes that can be decoded using latin-1 encoding
        - Input timestamp must represent a valid date/time in RFC 2822 format or compatible variant
        
    Postconditions:
        - Output is always a datetime object
        - If timezone information was present in input and normalise=True, output datetime will be naive
        - If timezone information was present in input and normalise=False, output datetime will be timezone-aware

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input timestamp bytes] --> B[_munge() to normalize timezone format]
    B --> C[parsedate_tz() to parse timestamp]
    C --> D{Parse successful?}
    D -- No --> E[Raise ValueError]
    D -- Yes --> F[Extract timezone offset]
    F --> G{Timezone offset exists?}
    G -- No --> H[Create datetime without timezone]
    G -- Yes --> I[Create FixedOffset timezone]
    H --> J[Create datetime with tzinfo=None]
    I --> J
    J --> K{Normalise enabled AND timezone exists?}
    K -- No --> L[Return datetime]
    K -- Yes --> M[datetime_to_native() to normalize to local time]
    M --> L
    L --> N[Return result]
```

## Examples:
    >>> parse_to_datetime(b"Mon, 01 Jan 2024 12:00:00 +0100")
    datetime(2024, 1, 1, 12, 0, 0, tzinfo=FixedOffset(60))
    
    >>> parse_to_datetime(b"Mon, 01 Jan 2024 12:00:00 +0100", normalise=False)
    datetime(2024, 1, 1, 12, 0, 0, tzinfo=FixedOffset(60))
    
    >>> parse_to_datetime(b"Mon, 01 Jan 2024 12:00:00 +0100", normalise=True)
    datetime(2024, 1, 1, 12, 0, 0)  # naive datetime in local timezone
    
    >>> parse_to_datetime(b"Invalid timestamp")
    ValueError: couldn't parse datetime b'Invalid timestamp'

## `imapclient.datetime_util.datetime_to_native` · *function*

## Summary:
Converts a timezone-aware datetime object to a naive datetime in the local system timezone.

## Description:
This function transforms a datetime object with timezone information into a naive datetime (without timezone) using the system's local timezone offset. It's designed to normalize datetime objects to the local system timezone before removing timezone information.

The function is typically called when processing datetime data that needs to be converted to local time for display or further processing without timezone information. This extraction into a separate function ensures consistent timezone conversion behavior across the codebase.

## Args:
    dt (datetime): A timezone-aware datetime object to convert to local system timezone. Must have tzinfo set to a valid timezone.

## Returns:
    datetime: A naive datetime object representing the same moment in time but in the local system timezone. The returned datetime has tzinfo=None.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - Input must be a datetime object with timezone information (tzinfo is not None)
        - Input must be a valid datetime object
    
    Postconditions:
        - Output is always a naive datetime (tzinfo=None)
        - Output represents the same instant in time as input
        - Output is in the local system timezone

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input datetime] --> B{Has timezone info?}
    B -- Yes --> C[Get system timezone offset via FixedOffset.for_system()]
    C --> D[Convert to system timezone using astimezone()]
    D --> E[Remove timezone info with replace(tzinfo=None)]
    E --> F[Return naive datetime]
    B -- No --> F
```

## Examples:
```python
from datetime import datetime, timezone
from imapclient.datetime_util import datetime_to_native

# Convert UTC datetime to local system time
utc_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
local_dt = datetime_to_native(utc_dt)
# Result: naive datetime in local system timezone representing same time

# Convert EST datetime to local system time  
est_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone(-timedelta(hours=5)))
local_dt = datetime_to_native(est_dt)
# Result: naive datetime in local system timezone representing same time

# Works with any timezone-aware datetime
pst_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone(timedelta(hours=-8)))
local_dt = datetime_to_native(pst_dt)
# Result: naive datetime in local system timezone representing same time
```

## `imapclient.datetime_util.datetime_to_INTERNALDATE` · *function*

## Summary:
Converts a Python datetime object to IMAP INTERNALDATE string format with timezone awareness.

## Description:
Transforms a datetime object into the IMAP INTERNALDATE format required by IMAP protocol operations. This function ensures the datetime has proper timezone information by applying the system's local timezone offset when the input datetime lacks timezone information. The resulting string follows the format "DD-MON-YYYY HH:MM:SS +/-HHMM" where MON is the three-letter abbreviated month name.

## Args:
    dt (datetime): A datetime object to convert to INTERNALDATE format. If the datetime lacks timezone information, it will be augmented with the system's local timezone offset.

## Returns:
    str: A string in IMAP INTERNALDATE format, e.g., "01-Jan-2023 12:30:45 +0000". The format consists of day, abbreviated month name, year, time, and timezone offset.

## Raises:
    None explicitly raised by this function. However, underlying strftime formatting may raise ValueError for invalid format strings.

## Constraints:
    Preconditions:
        - Input must be a valid datetime object
        - The datetime object may or may not have timezone information
    Postconditions:
        - Output is always a properly formatted IMAP INTERNALDATE string
        - The returned string includes timezone offset in RFC 2822 format (+HHMM or -HHMM)
        - The month abbreviation is derived from the datetime's month attribute

## Side Effects:
    None.

## Control Flow:
    ```mermaid
    flowchart TD
        A[Start datetime_to_INTERNALDATE] --> B{dt.tzinfo None?}
        B -- Yes --> C[dt.replace(tzinfo=FixedOffset.for_system())]
        B -- No --> D[Use existing timezone info]
        C --> E[Construct format string]
        D --> E
        E --> F[Apply strftime formatting]
        F --> G[Return formatted string]
    ```

## Examples:
    >>> from datetime import datetime
    >>> dt = datetime(2023, 1, 15, 14, 30, 0)
    >>> datetime_to_INTERNALDATE(dt)
    '15-Jan-2023 14:30:00 +0000'
    
    >>> from datetime import datetime, timezone
    >>> dt = datetime(2023, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
    >>> datetime_to_INTERNALDATE(dt)
    '15-Jan-2023 14:30:00 +0000'

## `imapclient.datetime_util._munge` · *function*

## Summary:
Normalizes timestamp strings by converting dotted timezone formats to colon-separated format.

## Description:
Decodes timestamp bytes to latin-1 string and applies timezone normalization by replacing dots with colons in timezone portions. This function specifically targets timestamps that use dotted timezone formats (like "+01.00") and converts them to standard colon-separated format (like "+01:00").

## Args:
    timestamp (bytes): Raw byte string representing a timestamp, typically from IMAP responses

## Returns:
    str: String representation of the timestamp with timezone portions normalized from dotted to colon-separated format when applicable, or the original string if no conversion is needed

## Raises:
    UnicodeDecodeError: When the timestamp bytes cannot be decoded using latin-1 encoding

## Constraints:
    Preconditions:
        - Input must be valid bytes object
        - Bytes must be decodable using latin-1 encoding
    Postconditions:
        - Output is always a string
        - If input contains dotted timezone format, output will have colon-separated timezone

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input bytes timestamp] --> B{Matches _rfc822_dotted_time pattern?}
    B -- Yes --> C[Replace "." with ":" in timezone portion]
    B -- No --> D[Return original string]
    C --> E[Return normalized string]
    D --> E
```

## Examples:
    >>> _munge(b"Mon, 01 Jan 2024 12:00:00 +01.00")
    "Mon, 01 Jan 2024 12:00:00 +01:00"
    
    >>> _munge(b"Tue, 02 Jan 2024 14:30:00 -0500")
    "Tue, 02 Jan 2024 14:30:00 -0500"
```

## `imapclient.datetime_util.format_criteria_date` · *function*

## Summary:
Formats a datetime object into a byte-encoded string representation suitable for IMAP date criteria.

## Description:
Converts a datetime object into a specific string format used by IMAP servers for date-based search criteria. The formatted string follows the pattern "DD-MMM-YYYY" where DD is the day with zero-padding, MMM is the abbreviated month name, and YYYY is the four-digit year. This formatted date is then encoded as ASCII bytes for network transmission.

This function is specifically designed for IMAP protocol date criteria formatting, where dates must be represented in a standardized format for server queries.

## Args:
    dt (datetime): A datetime object containing the date to be formatted. The datetime object must have valid month values (1-12).

## Returns:
    bytes: A byte string representing the formatted date in the format "DD-MMM-YYYY" encoded in ASCII.

## Raises:
    IndexError: If the month value in the datetime object is outside the valid range (1-12) or if _SHORT_MONTHS array does not contain sufficient elements for the month index.

## Constraints:
    Preconditions:
        - The input datetime object must have valid month values (1-12)
        - The datetime object must be a valid datetime instance
        - The _SHORT_MONTHS constant must be properly defined with 12 elements (one for each month)
    
    Postconditions:
        - The returned bytes represent a properly formatted date string matching IMAP criteria format
        - The returned bytes are encoded in ASCII character set

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start format_criteria_date] --> B{Input validation}
    B --> C{Valid datetime object?}
    C -->|No| D[Throw TypeError/ValueError]
    C -->|Yes| E{Valid month (1-12)?}
    E -->|No| F[Throw IndexError]
    E -->|Yes| G[Access _SHORT_MONTHS[month]]
    G --> H[Format as "%02d-%s-%d"]
    H --> I[Encode as ASCII bytes]
    I --> J[Return bytes]
```

## Examples:
```python
from datetime import datetime

# Basic usage
dt = datetime(2023, 12, 25)
result = format_criteria_date(dt)
# Returns: b'25-Dec-2023'

# Another example
dt = datetime(2024, 1, 1)
result = format_criteria_date(dt)
# Returns: b'01-Jan-2024'
```

