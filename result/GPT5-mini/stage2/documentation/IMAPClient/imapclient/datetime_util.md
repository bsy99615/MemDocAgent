# `datetime_util.py`

## `imapclient.datetime_util.parse_to_datetime` · *function*

## Summary:
Parse a server-provided timestamp (bytes) into a Python datetime, interpreting any numeric timezone offset and optionally converting the result to a system-local naive datetime.

## Description:
This function accepts a raw timestamp as bytes, performs light normalization and parsing, then constructs a datetime from the parsed components. Typical usage is immediately after receiving a timestamp value from an IMAP server (for example an INTERNALDATE response) to convert the server-supplied timestamp into a datetime object suitable for application logic.

Known callers within the provided snapshot:
- No explicit call sites are present in the provided repository excerpt. In typical IMAP client code this function is called after reading a timestamp byte sequence from the server and before storing or comparing message timestamps.

Why this is a separate function:
- Parsing a bytes-encoded timestamp requires multiple steps (byte decoding + normalization, parsing to a time tuple, attaching a timezone when provided, and optional normalization to the system local time). Centralizing these steps ensures consistent handling of dotted time separators, timezone offsets, and the choice to return an aware or naive datetime across the codebase.

## Args:
    timestamp (bytes)
        - Description: Raw timestamp bytes as returned by the server (e.g., b'21-Feb-2021 09:05:03 +0000' or b'21-Feb-2021 09.05.03 +0000').
        - Required type: bytes. The implementation calls the helper _munge which decodes the input via latin-1; passing a non-bytes value will raise an AttributeError when _munge attempts to decode.
        - Content: The function does not validate semantic correctness beyond relying on parsedate_tz; malformed timestamp strings will typically lead to a parse failure (ValueError).

    normalise (bool, optional) = True
        - Description: If True and the parsed timestamp included a timezone offset, convert the resulting aware datetime to the system-local timezone and return a tz-naive datetime representing the same instant (uses datetime_to_native). If False, return the datetime with the timezone attached (FixedOffset) when a timezone is present.
        - Interdependency: normalise only has effect when the parsed timestamp contains a timezone offset (i.e., parsedate_tz supplies a tz offset). If no tz offset is present, the returned datetime is naive regardless of normalise.

## Returns:
    datetime.datetime
        - If parsed timestamp contains a timezone offset and normalise is False: returns an aware datetime with tzinfo set to a FixedOffset constructed from the parsed offset (offset passed as tz_offset_seconds / 60).
        - If parsed timestamp contains a timezone offset and normalise is True: returns a tz-naive datetime produced by converting the aware datetime to the system local timezone and dropping tzinfo (via datetime_to_native). The returned naive datetime represents the same instant as the original timestamp.
        - If parsed timestamp contains no timezone offset: returns a naive datetime constructed from the parsed year, month, day, hour, minute, second values.
        - In all cases the calendar fields (year..second) are taken from the first six elements of parsedate_tz(...) and used to construct the datetime.

## Raises:
    ValueError
        - Condition: parsedate_tz(_munge(timestamp)) returned None (i.e., the timestamp string could not be parsed). The function raises ValueError("couldn't parse datetime %r" % timestamp) in this case.

    AttributeError (propagated)
        - Condition: If timestamp is not a bytes object, _munge will attempt to call .decode("latin-1") and that will raise AttributeError. This exception is not caught in this function.

    TypeError, ValueError, or other exceptions (propagated)
        - Condition: If the parsed time_tuple does not have at least six elements, datetime(*time_tuple[:6], ...) may raise TypeError due to missing required positional arguments. Also FixedOffset(...) or datetime_to_native(...) may raise and those exceptions are propagated to the caller.
        - Note: parsedate_tz from email.utils normally returns a time tuple with at least 9 elements or None; the above errors are defensive notes for malformed return values or unexpected behavior from helper calls.

## Constraints:
Preconditions:
    - timestamp must be a bytes object (the function relies on _munge which decodes bytes).
    - The module-level helper _munge and the imported parsedate_tz and FixedOffset must be available at runtime.

Postconditions:
    - The function returns a datetime instance representing the instant described by timestamp (aware with FixedOffset if normalise is False and a tz offset was present; naive after conversion if normalise is True and a tz offset was present; naive if the original timestamp contained no tz offset).
    - If parsed successfully, the returned datetime's year..second fields reflect the parsed values from the timestamp.

## Side Effects:
    - None observable: the function performs no I/O, does not mutate global state, and does not perform network or file operations.
    - It does call FixedOffset(...) (to create a tzinfo) and may call datetime_to_native(...) which consults system timezone information (FixedOffset.for_system()) when normalising; no persistent side effects are produced by these calls.

## Control Flow:
flowchart TD
    Start[Start: parse_to_datetime(timestamp, normalise)]
    Start --> Munge[Call _munge(timestamp) -> decoded string]
    Munge --> Parse[Call parsedate_tz(decoded)]
    Parse --> CheckParse{time_tuple is None?}
    CheckParse -- yes --> RaiseV[Raise ValueError("couldn't parse datetime %r" % timestamp)]
    CheckParse -- no --> GetTZ[tz_offset_seconds = time_tuple[-1]]
    GetTZ --> TZNone{tz_offset_seconds is None?}
    TZNone -- yes --> TZSetNone[tz = None]
    TZNone -- no --> MakeFixed[tz = FixedOffset(tz_offset_seconds / 60)]
    TZSetNone --> MakeDT
    MakeFixed --> MakeDT
    MakeDT[dt = datetime(*time_tuple[:6], tzinfo=tz)] --> NormCond{normalise and tz?}
    NormCond -- yes --> ToNative[dt = datetime_to_native(dt)]
    NormCond -- no --> SkipNorm
    ToNative --> Return[return dt]
    SkipNorm --> Return

## Examples:
1) Timestamp with explicit UTC offset, normalise=True (default)
    - Input: b'21-Feb-2021 09:05:03 +0000' (or b'21-Feb-2021 09.05.03 +0000' which is normalized by _munge)
    - Behavior:
        * _munge decodes and normalizes dotted times if present.
        * parsedate_tz parses the date/time and returns a time tuple including a tz offset (0 seconds for +0000).
        * FixedOffset(0 / 60) is attached as tzinfo to the constructed datetime.
        * Because normalise is True and a tz was present, datetime_to_native converts that aware datetime to the system local timezone and returns a tz-naive datetime representing the same instant.
    - Outcome (illustrative): returns a tz-naive datetime in local time representing the same absolute instant as "2021-02-21 09:05:03+00:00". The exact wall-clock values depend on the system timezone.

2) Timestamp with explicit offset, normalise=False
    - Input: b'21-Feb-2021 09:05:03 +0200' and normalise=False
    - Outcome: returns an aware datetime with tzinfo set to FixedOffset(120.0) (120.0 = 7200 seconds / 60). The datetime represents 2021-02-21T09:05:03 with that FixedOffset tzinfo attached.

3) Timestamp without timezone information
    - Input: b'21-Feb-2021 09:05:03' (no tz)
    - Outcome: parsedate_tz returns a tuple with tz_offset_seconds set to None; the function returns a naive datetime built from the parsed year..second values.

4) Parse failure
    - Input: b'not a date'
    - Outcome: parsedate_tz returns None and the function raises ValueError("couldn't parse datetime %r" % timestamp). Caller should catch ValueError to handle unparseable timestamps.

Notes:
    - Because _munge decodes bytes using latin-1, any byte sequence is accepted and will not raise UnicodeDecodeError, but may fail parsing.
    - The conversion performed when normalise=True depends on system timezone; test outcomes will differ across environments.

## `imapclient.datetime_util.datetime_to_native` · *function*

## Summary:
Return a naive datetime representing the same instant expressed in the system local timezone.

## Description:
This function converts the provided datetime to the system-local offset (obtained from FixedOffset.for_system()) and then removes the timezone information, producing a tz-naive datetime.

Known callers in the provided snapshot:
    - None found in the supplied repository excerpt.

Why this logic is extracted:
    - Centralizes the two-step transformation (convert to system offset, then drop tzinfo) so callers do not need to repeat timezone conversion details or instantiate FixedOffset themselves.

## Args:
    dt (datetime.datetime): The datetime to convert. The implementation calls dt.astimezone(...) and dt.replace(...), so dt must be an object that implements those methods (normally a standard datetime.datetime instance).

## Returns:
    datetime.datetime: A new datetime object with tzinfo set to None whose calendar fields correspond to the original instant represented in the system-local timezone (i.e., result == dt.astimezone(FixedOffset.for_system()).replace(tzinfo=None)).

## Raises:
    - Propagated exceptions from the invoked datetime methods:
        * AttributeError: if dt has no astimezone or replace attribute.
        * TypeError: if dt.astimezone(...) or dt.replace(...) is called with inappropriate types.
        * ValueError: if datetime.astimezone() raises it for the given dt (behavior depends on the datetime object's state and Python runtime).
    The function does not catch or wrap these exceptions; they surface to the caller.

## Constraints:
    Preconditions:
        - dt must be a datetime-like object implementing astimezone(tz) and replace(tzinfo=...).
        - No other preconditions are enforced by this function.
    Postconditions:
        - Returned datetime.tzinfo is None.
        - The returned object represents the same absolute instant as dt but expressed in the system-local timezone.

## Side Effects:
    - None. The function constructs and returns a new datetime; it does not perform I/O or mutate external state.
    - The only external observation is that FixedOffset.for_system() reads system timezone/DST information to build the offset (no persistent state change).

## Control Flow:
flowchart TD
    Start --> GetSystemOffset[Call FixedOffset.for_system()]
    GetSystemOffset --> Convert[Call dt.astimezone(system_offset)]
    Convert --> StripTZ[Call .replace(tzinfo=None)]
    StripTZ --> Return[Return naive datetime]
    Convert -.-> PropagateErr[Propagate exceptions from astimezone/replace]
    PropagateErr --> End
    Return --> End
    End((End))

## Examples:
Example (illustrative):
    - Given an aware UTC datetime:
        dt_utc = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
    - Calling the function:
        native = datetime_to_native(dt_utc)
    - Result:
        - native is tz-naive (native.tzinfo is None).
        - native represents the same instant as dt_utc but expressed in the system local timezone:
          native == dt_utc.astimezone(FixedOffset.for_system()).replace(tzinfo=None)

Notes:
    - The function intentionally leaves exception handling to callers; if callers need to accept non-datetime inputs or guarantee behavior for naive dt values, they should validate or normalize dt before calling.

## `imapclient.datetime_util.datetime_to_INTERNALDATE` · *function*

## Summary:
Format a datetime into an IMAP INTERNALDATE string (day-short-month-year hour:minute:second timezone), attaching the system local timezone when the input is naive.

## Description:
This function returns a string formatted for IMAP INTERNALDATE usage by:
- Ensuring the datetime has a timezone: if dt.tzinfo is None (naive datetime), it attaches a FixedOffset returned by FixedOffset.for_system() before formatting.
- Constructing a strftime format that embeds a short month name looked up from the module-level _SHORT_MONTHS mapping/list via _SHORT_MONTHS[dt.month] and includes the numeric timezone offset token %z.
- Calling dt.strftime(fmt) to produce the final string.

Known callers:
- No direct callers were discovered in the provided snapshot of the codebase. In typical IMAP client implementations, functions like this are called when building the INTERNALDATE argument for APPEND, APPEND-related utilities, or when serializing message dates for upload to the server.

Why this is a separate function:
- IMAP INTERNALDATE has a strict textual format and requires consistent treatment of naive datetimes (system-local tz) and month-name canonicalization. Centralizing this logic avoids duplication and ensures all callers produce the same canonical formatting.

## Args:
    dt (datetime.datetime): The date/time to format.
        - Must provide attributes/methods used: tzinfo, replace(), month (int 1..12), and strftime(format).
        - If dt.tzinfo is None, the function calls FixedOffset.for_system() and replaces tzinfo via dt.replace(...).
        - If dt.tzinfo is present but its utcoffset() returns None, strftime("%z") may produce an empty string; the function does not detect or correct that.

## Returns:
    str: A formatted IMAP INTERNALDATE string:
         "%d-<short-month>-<YYYY> %H:%M:%S %z"
    - <short-month> is obtained as _SHORT_MONTHS[dt.month].
    - %z is the numeric timezone offset derived from dt.tzinfo (formatted ±HHMM). If dt.tzinfo.utcoffset(datetime) returns None, %z will be an empty string.
    - Examples (actual timezone parts depend on _SHORT_MONTHS contents and system/local tz):
        - For an aware datetime in UTC: "02-Jan-2020 14:04:05 +0000"
        - For a naive datetime on a machine with +0100 local offset: "02-Jan-2020 15:04:05 +0100"

## Raises:
    - AttributeError or TypeError: If dt does not implement the expected attributes/methods (tzinfo, replace, month, strftime).
    - KeyError or IndexError: If _SHORT_MONTHS does not contain an entry for key/index dt.month (e.g., dt.month outside 1..12 or _SHORT_MONTHS missing proper keys/indices).
    - Any exception raised by FixedOffset.for_system() will propagate when dt is naive.
    - Note: dt.strftime(fmt) may raise ValueError on some platforms for unsupported format combinations; such exceptions will also propagate.

## Constraints:
Preconditions:
    - dt.month must be a valid lookup into _SHORT_MONTHS. Recommended forms for _SHORT_MONTHS:
        - A mapping/dict with integer keys 1..12 mapping to strings, e.g. {1: 'Jan', 2: 'Feb', ...}
        - Or a sequence (list/tuple) where indexing with dt.month is valid. If a sequence is used, a common pattern is to make it 1-based with a placeholder at index 0: ['', 'Jan', 'Feb', ..., 'Dec'].
    - dt should be a datetime.datetime instance (or a compatible duck-typed object).

Postconditions:
    - The returned value is a str formatted as described above.
    - The input dt is not mutated; when tzinfo is attached the function uses dt.replace(...) to produce a new datetime instance internally.

## Side Effects:
    - No external I/O, network, or persistent state changes.
    - When dt is naive, FixedOffset.for_system() is invoked; that call inspects system timezone information (time.timezone / time.altzone and time.localtime().tm_isdst) and returns a FixedOffset tzinfo instance representing the local offset. This reads system time data but has no other side effects.

## Control Flow:
flowchart TD
    Start --> IsTzPresent
    IsTzPresent{dt.tzinfo is not None?}
    IsTzPresent -- Yes --> BuildFormat
    IsTzPresent -- No --> AttachSystemTZ
    AttachSystemTZ --> BuildFormat
    BuildFormat --> Strftime
    Strftime --> Return
    Return --> End

    Start[Start]
    IsTzPresent{dt.tzinfo is not None?}
    AttachSystemTZ[dt = dt.replace(tzinfo=FixedOffset.for_system())]
    BuildFormat[fmt = "%d-" + _SHORT_MONTHS[dt.month] + "-%Y %H:%M:%S %z"]
    Strftime[output = dt.strftime(fmt)]
    Return[return output]
    End[End]

## Examples:
- Example 1 — naive datetime:
    - Given: dt = datetime(2020, 1, 2, 15, 4, 5)  (tzinfo is None)
    - Behavior: function calls FixedOffset.for_system(), attaches that tzinfo via dt.replace(...), looks up _SHORT_MONTHS[1] (e.g., "Jan"), and returns a string like:
        02-Jan-2020 15:04:05 +0100
      (exact timezone text depends on the system local offset and _SHORT_MONTHS content)

- Example 2 — aware datetime with tzinfo that provides an offset:
    - Given: dt = datetime(2020, 1, 2, 14, 4, 5, tzinfo=timezone.utc)
    - Behavior: tzinfo is preserved; the result might be:
        02-Jan-2020 14:04:05 +0000

- Example 3 — aware datetime whose tzinfo.utcoffset() returns None:
    - Given a tzinfo implementation where utcoffset() returns None, %z will be empty and the returned string may look like:
        02-Jan-2020 14:04:05 
      (the trailing timezone is empty). The function does not normalize or fill such missing offsets.

Notes and recommendations:
    - Ensure _SHORT_MONTHS contains canonical short-month names for months 1..12. A safe implementation is a 13-entry sequence with a dummy at index 0, or a dict keyed 1..12.
    - If you need guaranteed non-empty timezone output even when an explicit tzinfo yields None for utcoffset, normalize dt before calling this function (attach a tzinfo or convert to a tz-aware datetime).

## `imapclient.datetime_util._munge` · *function*

## Summary:
Decode a timestamp given as bytes to a latin-1 string and normalize dotted time separators by replacing all '.' characters with ':' so the result is suitable for RFC-822 style parsers.

## Description:
This small helper converts a raw bytes timestamp into a string and normalizes dotted time separators that some servers emit (e.g., "12.34.56" -> "12:34:56"). It exists to prepare byte-valued timestamp fields for string-based parsers (for example, email.utils.parsedate_tz), which require string input and expect colon-separated hours/minutes/seconds.

Known callers within the codebase:
- No explicit callers are present in the provided snapshot of the file. In typical usage within IMAP client code, this function is invoked immediately after receiving a timestamp value from the server (e.g., an INTERNALDATE response) and before handing the normalized string to a timestamp parser such as email.utils.parsedate_tz.

Why this logic is extracted:
- Decoding bytes and normalizing dotted separators are distinct, repeatable preprocessing steps. Centralizing them reduces duplication and ensures consistent behavior before parsing timestamps in multiple places.

## Args:
    timestamp (bytes): The raw timestamp bytes received from the server.
        - Required type: bytes. The function calls timestamp.decode("latin-1"); passing any other type will raise an AttributeError at runtime.
        - There is no additional validation of content; empty bytes (b'') are accepted and decoded to an empty string.

## Returns:
    str: The decoded timestamp string encoded via latin-1 with all '.' characters replaced by ':' when a dotted-time pattern is detected.
    - The function always returns a Python str.
    - Behavior details:
        * The input bytes are decoded using the latin-1 codec (ISO-8859-1). This mapping is one-to-one for byte values 0–255, so decoding will not raise UnicodeDecodeError.
        * If the decoded string matches the module-level regular expression _rfc822_dotted_time (i.e., the string appears to have an RFC-822 timestamp that uses dots as time separators), the function returns s.replace(".", ":"). This is a global replacement of every '.' character in the decoded string.
        * If the regex does not match, the original decoded string is returned unchanged.

## Raises:
    - AttributeError: If timestamp is not a bytes object (e.g., passing a str or None) because the code calls decode on the input.
    - NameError: If the module-level name _rfc822_dotted_time is not defined at runtime.
    - No UnicodeDecodeError will be raised because latin-1 decoding handles all byte values.

## Constraints:
Preconditions:
- The caller must pass a bytes object.
- The module-level compiled regular expression _rfc822_dotted_time must be defined and behave like a standard re.Pattern with a match(s) method.

Postconditions:
- The return value is a str.
- If _rfc822_dotted_time.match(decoded) returned True, then the returned string contains no '.' characters (all were replaced by ':'); otherwise the returned string equals the decoded input.

## Side Effects:
- None. The function performs no I/O, does not mutate global state, and makes no external calls beyond a regex match and string replace.

## Control Flow:
flowchart TD
    A[Start: timestamp (bytes)] --> B[Decode with latin-1 -> s]
    B --> C{_rfc822_dotted_time.match(s)?}
    C -- true --> D[return s.replace(".", ":")  (global replacement)]
    C -- false --> E[return s]
    D --> F[End]
    E --> F[End]

## Examples:
1) Normalizing a dotted-time bytes value:
    Input: b'21-Feb-2021 09.05.03 +0000'
    Call: _munge(b'21-Feb-2021 09.05.03 +0000')
    Output: '21-Feb-2021 09:05:03 +0000'

2) Already-normalized bytes:
    Input: b'21-Feb-2021 09:05:03 +0000'
    Call: _munge(b'21-Feb-2021 09:05:03 +0000')
    Output: '21-Feb-2021 09:05:03 +0000'

3) Edge cases and error handling:
    - Empty input:
        Input: b''
        Output: ''  (empty string)
    - Wrong type:
        If the caller mistakenly provides a str:
            try:
                _munge('21-Feb-2021 09.05.03 +0000')  # wrong type
            except AttributeError:
                handle_error()
        The function raises AttributeError because str in Python 3 has no decode method.
    - Missing regex:
        If _rfc822_dotted_time is not defined, calling this function raises NameError.

Notes:
- The implementation intentionally performs a global replacement of '.' characters only after confirming the decoded string matches _rfc822_dotted_time; it does not attempt to localize replacements to a substring of the result. If callers need more targeted normalization, perform additional validation before or after calling this helper.

## `imapclient.datetime_util.format_criteria_date` · *function*

## Summary:
Return an ASCII-encoded bytes object representing a date in the IMAP SEARCH criteria format DD-Mon-YYYY (for example, b'05-Aug-2021') from a datetime-like object.

## Description:
This helper produces a single IMAP-compatible date token by:
- Reading the day, month, and year attributes from the provided object,
- Looking up a short month name from the module-level _SHORT_MONTHS sequence using dt.month as the index,
- Formatting the string "DD-Mon-YYYY" with a zero-padded two-digit day, a short month name, and the year, and
- Encoding the result to ASCII bytes.

Known callers and usage context:
- No direct callers were identified in the provided snippet. In practice this function is used by higher-level code that constructs IMAP SEARCH criteria (for example, building ON/SINCE/BEFORE clauses) where date tokens must be encoded as ASCII bytes.

Why this function exists separately:
- It centralizes the exact formatting and ASCII encoding for IMAP date tokens so callers need not duplicate formatting logic and can rely on a consistent representation.

## Args:
    dt (datetime.datetime or duck-typed object)
        - Required attributes: dt.day, dt.month, dt.year.
        - The function only reads these attributes; it does not require dt to be an actual datetime instance at runtime.
        - The caller is responsible for ensuring dt.month is a valid index for the module-level _SHORT_MONTHS sequence (see Preconditions).

## Returns:
    bytes
        - ASCII-encoded bytes of the formatted date string "DD-Mon-YYYY".
        - Day is zero-padded to two digits. Month is taken from _SHORT_MONTHS[dt.month] without modification. Year is formatted as decimal digits.
        - Examples:
            - datetime(2021, 8, 5) -> b'05-Aug-2021'
            - datetime(1999, 12, 1) -> b'01-Dec-1999'

## Raises:
    AttributeError
        - If dt lacks any of the attributes day, month, or year.
        - Trigger: attempting to access dt.day, dt.month, or dt.year.
    IndexError
        - If dt.month cannot be used to index into the module-level _SHORT_MONTHS sequence.
        - Trigger: evaluating _SHORT_MONTHS[dt.month] when dt.month is out of bounds.
    TypeError
        - If dt.day, dt.month, or dt.year are present but incompatible with the numeric formatting specifiers used ("%02d" and "%d"). For example, completely non-numeric objects may provoke a TypeError during formatting.
    UnicodeEncodeError
        - If the month name retrieved from _SHORT_MONTHS contains characters that cannot be encoded to ASCII when calling out.encode("ascii").

## Constraints:
Preconditions:
    - dt must expose .day, .month, .year attributes suitable for formatting.
    - The module-level symbol _SHORT_MONTHS must be an indexable sequence such that _SHORT_MONTHS[dt.month] is valid for the provided dt.month. The code does not enforce whether dt.month is 1-based, 0-based, or otherwise — callers must ensure consistency between dt.month values and how _SHORT_MONTHS is arranged in the module.
    - No timezone or normalization is applied. If callers need to convert between timezones or normalize dates, they must do so before calling this function.

Postconditions:
    - Returns a bytes object encoded in ASCII in the format DD-Mon-YYYY, where DD is zero-padded to two digits.
    - No external state is modified.

## Side Effects:
    - None. This function performs no I/O and does not mutate global state. It only reads dt attributes and the module-level _SHORT_MONTHS sequence.

## Control Flow:
flowchart TD
    Start --> ReadAttrs[Read dt.day, dt.month, dt.year]
    ReadAttrs --> Lookup[month_name = _SHORT_MONTHS[dt.month]]
    Lookup --> Format[Create string out = "%02d-%s-%d" % (day, month_name, year)]
    Format --> Encode[bytes_out = out.encode("ascii")]
    Encode --> Return[Return bytes_out]
    ReadAttrs -->|missing attribute| AttrErr[AttributeError raised]
    Lookup -->|index error| IndexErr[IndexError raised]
    Format -->|bad types| TypeErr[TypeError raised]
    Encode -->|non-ascii| UnicodeErr[UnicodeEncodeError raised]

## Examples:
Example — constructing an IMAP ON search criterion:
    from datetime import datetime
    # Caller ensures dt.month is compatible with _SHORT_MONTHS
    dt = datetime(2021, 8, 5)
    # format_criteria_date returns bytes suitable for inclusion in a command
    date_token = format_criteria_date(dt)            # b'05-Aug-2021'
    imap_search = b'ON ' + date_token                # b'ON 05-Aug-2021'
    # Send imap_search as part of an IMAP SEARCH command payload.

Example — defensive caller checking indexability:
    dt = datetime(2021, 8, 5)
    try:
        # verify dt.month indexes _SHORT_MONTHS before calling (pattern depends on how _SHORT_MONTHS is defined)
        _ = _SHORT_MONTHS[dt.month]
    except Exception as e:
        # handle invalid month mapping (e is typically IndexError or TypeError)
        raise
    bdate = format_criteria_date(dt)

