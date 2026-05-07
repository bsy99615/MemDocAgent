# `fixed_offset.py`

## `imapclient.fixed_offset.FixedOffset` · *class*

## Summary:
A timezone information class that represents a fixed timezone offset from UTC, implementing the datetime.tzinfo interface.

## Description:
The FixedOffset class implements the datetime.tzinfo abstract base class to represent a fixed timezone offset that does not change throughout the year. It provides timezone information for datetime objects when a constant offset from UTC is required. This class is particularly useful for handling datetime objects with fixed timezone offsets that don't observe daylight saving time changes.

The class can be instantiated directly with a minute offset or created using the classmethod `for_system()` which automatically detects and uses the system's local timezone offset. It implements all required methods of the datetime.tzinfo interface: utcoffset, tzname, and dst.

## State:
- `__offset`: datetime.timedelta representing the fixed offset from UTC. Valid range is from -1440 minutes (-24 hours) to +1440 minutes (+24 hours).
- `__name`: str formatted timezone name in HHMM or -HHMM format (e.g., "+0530", "-0800"). The format follows standard timezone naming conventions.

## Lifecycle:
- Creation: Instances can be created via `FixedOffset(minutes)` constructor or `FixedOffset.for_system()` classmethod
- Usage: Once created, the instance can be passed to datetime constructors to associate timezone information with datetime objects
- Destruction: No special cleanup required; follows normal Python garbage collection

## Method Map:
```mermaid
graph TD
    A[FixedOffset Constructor] --> B[utcoffset]
    A --> C[tzname]
    A --> D[dst]
    E[for_system] --> A
    B --> F[datetime.timedelta]
    C --> G[str]
    D --> H[Zero timedelta (standard tzinfo)]
```

## Raises:
- No explicit exceptions are raised by the constructor under normal circumstances
- The constructor assumes the minutes parameter is a valid numeric value within acceptable timezone offset ranges (-1440 to +1440 minutes)

## Example:
```python
# Create a fixed offset for UTC+5:30
tz = FixedOffset(330)  # 5.5 hours in minutes

# Create a fixed offset for UTC-8:00 (Pacific Time)
tz = FixedOffset(-480)  # -8 hours in minutes

# Create offset based on system timezone
tz = FixedOffset.for_system()

# Use with datetime
import datetime
dt = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=tz)
```

### `imapclient.fixed_offset.FixedOffset.__init__` · *method*

## Summary:
Initializes a FixedOffset instance with a timezone offset specified in minutes.

## Description:
Constructs a FixedOffset object representing a fixed timezone offset from UTC. This method sets up the internal representation of the offset using a timedelta and generates a standardized name string for the offset.

## Args:
    minutes (float): Timezone offset in minutes from UTC. Positive values indicate eastward offsets, negative values indicate westward offsets.

## Returns:
    None: This method initializes the object's internal state and does not return a value.

## Raises:
    No explicit exceptions are raised by this method.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.__offset: Stores the timezone offset as a datetime.timedelta object
        - self.__name: Stores the formatted timezone name string in HHMM format

## Constraints:
    Preconditions: The minutes parameter should be a valid numeric value representing a timezone offset.
    Postconditions: The object will have its __offset and __name attributes properly initialized.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `imapclient.fixed_offset.FixedOffset.utcoffset` · *method*

## Summary:
Returns the fixed offset from UTC for this timezone instance.

## Description:
This method implements the standard Python timezone interface by returning the fixed offset that was configured during object initialization. It is called by datetime operations to determine the timezone offset for a given datetime.

## Args:
    _ (Optional[datetime.datetime]): A datetime object for which the offset is requested. This parameter is ignored in the fixed offset implementation.

## Returns:
    datetime.timedelta: The fixed offset from UTC, as configured during object initialization.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: self.__offset
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have been properly initialized with a valid timedelta offset.
    Postconditions: The returned timedelta represents a constant offset that does not change over time.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `imapclient.fixed_offset.FixedOffset.tzname` · *method*

## Summary:
Returns the name of this fixed timezone offset as a formatted string.

## Description:
This method implements the standard `tzinfo.tzname()` interface required by Python's datetime module. It returns the pre-computed timezone name string that was constructed during object initialization based on the offset value.

## Args:
    _: Optional[datetime.datetime] - A datetime object (ignored) as required by the tzinfo interface specification.

## Returns:
    str - The formatted timezone name string in the format "+HHMM" or "-HHMM" where HH represents hours and MM represents minutes.

## Raises:
    None - This method does not raise any exceptions.

## State Changes:
    Attributes READ: self.__name
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The FixedOffset object must have been properly initialized with a valid offset value.
    Postconditions: The returned string will always be in the format "+HHMM" or "-HHMM" representing the timezone offset.

## Side Effects:
    None - This method performs no I/O operations or external service calls.

### `imapclient.fixed_offset.FixedOffset.dst` · *method*

## Summary:
Returns the daylight saving time offset for this fixed timezone, which is always zero since fixed offsets don't observe daylight saving time.

## Description:
This method implements the datetime.tzinfo interface by returning the daylight saving time offset. For FixedOffset timezone objects, this is always zero because fixed offset timezones do not observe daylight saving time changes. The method is called internally by Python's datetime handling mechanisms when determining timezone information.

## Args:
    _ (Optional[datetime.datetime]): A datetime object representing the date/time for which DST is being calculated. This parameter is unused in the implementation.

## Returns:
    datetime.timedelta: Always returns a zero timedelta (datetime.timedelta(0)), indicating no daylight saving time offset.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None - this method only reads the implicit ZERO constant
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: None - this method can be called at any time with any datetime argument
    Postconditions: Always returns datetime.timedelta(0)

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only returns a constant value.

### `imapclient.fixed_offset.FixedOffset.for_system` · *method*

## Summary:
Creates a FixedOffset instance representing the system's local timezone offset.

## Description:
This class method determines the appropriate timezone offset for the system's local time zone, taking into account daylight saving time if applicable. It returns a new FixedOffset instance configured with the correct offset in minutes.

The method checks if daylight saving time is currently in effect and uses either the alternate timezone offset (time.altzone) or the standard timezone offset (time.timezone) accordingly. The resulting offset is converted from seconds to minutes and negated to match the expected FixedOffset convention.

This method is designed to create timezone-aware FixedOffset instances that accurately reflect the system's local timezone configuration, making it useful for creating timezone-aware datetime objects that match the local system time.

## Args:
    cls: The FixedOffset class (implicit parameter for classmethod)

## Returns:
    FixedOffset: A new instance representing the system's local timezone offset

## Raises:
    None explicitly raised

## State Changes:
    None - This is a factory method that creates and returns a new instance

## Constraints:
    Preconditions:
    - The system's time zone information must be accessible via the time module
    - The system must have valid timezone configuration
    
    Postconditions:
    - Returns a FixedOffset instance with correct offset for the local timezone
    - The returned instance represents the current system timezone with proper DST handling

## Side Effects:
    None - This method does not perform any I/O operations or mutate external state

