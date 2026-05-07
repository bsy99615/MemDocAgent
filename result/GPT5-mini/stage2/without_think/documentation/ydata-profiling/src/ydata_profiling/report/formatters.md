# `formatters.py`

## `src.ydata_profiling.report.formatters.list_args` · *function*

## Summary:
Wraps a single-value callable so it can be invoked with either a single value or a built-in Python list of values; when given a list it applies the callable to each element and returns a list of results, otherwise it forwards the single value and returns the callable's result.

## Description:
This decorator returns a wrapper that inspects the wrapper's first positional argument. If that argument is an instance of Python's built-in list, the wrapper calls the original callable once per list element (with the same trailing positional and keyword arguments) and returns a list of the results. If the first argument is not a built-in list, the wrapper calls the original callable once with the provided arguments and returns that single result.

Known callers within this module:
- No callers are defined in src/ydata_profiling/report/formatters.py for this decorator. The decorator is intended to be applied to functions that operate on a single element (for example, single-value formatter functions) so those functions can accept either a scalar or a list without changing their implementation.

Why this logic is a separate function:
- It centralizes the dispatch for scalar-vs-list inputs so individual single-value callables remain focused on element processing.
- It enforces a clear boundary: the decorator handles collection-level iteration; the wrapped callable handles single-element logic.

## Args:
- func (Callable) — The callable to be wrapped. Expected to accept at least one positional argument (the element to process) and optionally additional positional and keyword arguments. No assumptions are made about func's return type.

Wrapper call signature produced by the decorator:
- arg (Any) — The first positional argument passed to the wrapper; used to determine dispatch mode.
- *args (Any) — Additional positional arguments forwarded unchanged to func.
- **kwargs (Any) — Keyword arguments forwarded unchanged to func.

Interdependencies:
- The decorator assumes func expects a single element as its first argument. If func is written to accept an entire collection as its first argument, applying this decorator will break that contract.

## Returns:
- Callable: the wrapper function.

Behavior of the returned wrapper when invoked:
- If arg is an instance of built-in list: returns list[Any] — a list containing func(element, *args, **kwargs) for each element in arg, in the same order. If arg is an empty list, the wrapper returns an empty list.
- If arg is not an instance of built-in list: returns Any — the single result of func(arg, *args, **kwargs).

Notes on return values:
- The element-wise returned list will contain the exact values produced by func for each element (including None or exceptions propagated during element processing).
- The wrapper does not attempt to flatten nested lists — if elements are lists and func returns lists, those lists appear as-is in the result list.

## Raises:
- The decorator itself raises no exceptions.
- Any exception raised by func (e.g., TypeError, ValueError) when invoked either for a scalar arg or for an element in a list will propagate out of the wrapper unchanged.

## Constraints:
Preconditions:
- func should be callable and designed to operate on a single element as its first parameter.
- To trigger element-wise processing, callers must pass a built-in Python list instance as the wrapper's first positional argument. Other iterable/sequence types (tuple, set, numpy.ndarray, pandas.Series, generator, etc.) are not treated as lists and will be forwarded to func as a single argument.

Postconditions:
- After the wrapper returns, the caller receives either:
  - the exact return value from func when invoked with a scalar first argument, or
  - a list of values produced by func for each element when invoked with a list first argument.
- The original func object and its behavior remain unchanged.

## Side Effects:
- The decorator performs no I/O and does not mutate global state.
- Any side effects are those performed by func and will occur once per element when a list is provided (and once for scalar inputs).

## Control Flow:
flowchart TD
    Start([Invoke wrapper]) --> IsList{is arg instance of built-in list?}
    IsList -- Yes --> Iterate[For each element in list]
    Iterate --> CallFunc[Call func(element, *args, **kwargs)]
    CallFunc --> Append[Append result to output list]
    Append --> Iterate
    Iterate --> ReturnList([Return output list])
    IsList -- No --> CallOnce[Call func(arg, *args, **kwargs)]
    CallOnce --> ReturnSingle([Return single result])

## Examples:
- Scalar input example (conceptual):
  If func(value) returns a formatted string for a numeric value, calling the wrapper with a single number returns that formatted string exactly as func would produce.

- List input example (conceptual):
  With the same func, calling the wrapper with a Python list of numbers returns a list of formatted strings, one per input element in the same order. If the input list is empty, an empty list is returned.

- Error propagation example (conceptual):
  If func raises a ValueError for a particular input element, invoking the wrapper with a list that includes that element will raise the same ValueError during processing of that element; the decorator does not catch or aggregate errors.

## `src.ydata_profiling.report.formatters.fmt_color` · *function*

## Summary:
Wraps the given text in an HTML <span> element with an inline CSS color style, returning the resulting HTML string.

## Description:
This small utility creates an HTML fragment that applies the provided CSS color to the supplied text by embedding both values directly into a <span> element's style attribute. In the provided source context there are no direct callers shown; typically this function is used by higher-level HTML/templating helpers within a reporting or rendering pipeline to colorize small pieces of text for display in generated reports or dashboards.

Responsibility boundary:
- Single responsibility: formatting a text string as a colored HTML span.
- Does not perform input validation, escaping, or sanitization; those responsibilities remain with the caller.

Why this is a separate function:
- Centralizes the HTML snippet construction so callers do not duplicate formatting markup.
- Makes intent explicit (apply color to text) and allows a single place to add escaping/validation in the future if desired.

## Args:
    text (str): The textual content to place inside the span. Can contain any characters; note that it is inserted verbatim into the output.
    color (str): A CSS color value to assign to the span via the inline style. Typical values: CSS color name ('red'), hex color ('#ff0000'), rgb/rgba function ('rgb(255,0,0)').

Interdependencies:
- Both parameters are used directly to build the HTML string. There is no normalization or validation performed between them.

## Returns:
    str: A string containing an HTML span element with the inline color styling, for example:
         '<span style="color:red">Hello</span>'.

All possible return shapes:
- Always returns a str following the pattern '<span style="color:{color}">{text}</span>'.
- There is no alternate return value for invalid inputs (no exceptions are raised by the function itself).

## Raises:
    This function does not raise any exceptions explicitly. If non-string types are passed and the runtime environment enforces strict typing, Python will implicitly convert via f-string formatting (e.g., ints will be converted to their string representation). No validation errors are raised inside the function.

## Constraints:
Preconditions:
- Prefer passing str for both arguments. While non-str values will be stringified, callers should ensure inputs are suitable for HTML insertion.
- If inputs originate from untrusted sources (user input, external files, network), callers must sanitize or escape them before calling this function to avoid XSS or malformed HTML.

Postconditions:
- Returns a valid HTML fragment (string) that places the original text inside a span whose inline style sets the CSS color to the provided color value.
- The function guarantees no mutation of external state.

## Side Effects:
- None. The function performs no I/O, no network access, and does not mutate global variables or perform any external service calls.

Security note:
- The function inserts both text and color directly into the output without escaping or validation. If either argument contains malicious content (for example, text containing HTML/JS or color containing quotes and CSS injection), it may lead to XSS when the returned string is embedded into an HTML page. Callers responsible for rendering untrusted inputs must escape or validate values prior to calling this function.

## Control Flow:
flowchart TD
    Start([Start]) --> Build["Construct string: '<span style=\"color:{color}\">{text}</span>'"]
    Build --> Return([Return resulting HTML string])
    Return --> End([End])

## Examples:
- Basic usage:
    result = fmt_color('Hello', 'blue')
    # result -> '<span style="color:blue">Hello</span>'

- Using a hex color:
    result = fmt_color('Error', '#ff0000')
    # result -> '<span style="color:#ff0000">Error</span>'

- Important: avoid passing unsanitized user input directly:
    unsafe_text = '<img src=x onerror=alert(1)>'
    # Do NOT call fmt_color(unsafe_text, 'red') without escaping; instead escape or sanitize first.

## `src.ydata_profiling.report.formatters.fmt_class` · *function*

## Summary:
Returns an HTML span element string that wraps the provided content and assigns the given CSS class to it.

## Description:
A tiny formatting utility that produces a span element with a class attribute and the provided inner content. The function performs no escaping or validation: both arguments are interpolated verbatim into the returned HTML fragment.

Known callers within the provided context:
- No explicit call sites were supplied in the provided source. Typical callers are report-rendering or templating code that needs a consistent way to add a CSS class to small pieces of content before including them in an HTML report.

Why this logic is extracted into its own function:
- Consolidates a common HTML fragment pattern so callers get a uniform span structure across the codebase.
- Separates markup composition from concerns like escaping, sanitization, or style-name validation so those responsibilities can be implemented and unit-tested independently by callers.

## Args:
    text (str):
        The inner content to place between the opening and closing span tags. Any value passed will be coerced to a string via Python formatting rules:
        - If a str is provided, it is used as-is.
        - If None is provided, it becomes the string "None".
        - Numeric values and other objects use their __format__/__str__ implementation.
        Because coercion is used, callers must escape or sanitize user-provided content prior to calling this function if raw text should not be interpreted as HTML.
    cls (str):
        The CSS class attribute value to set on the span element. This value is inserted verbatim into the double-quoted class attribute. It must be a string or convertible to string; however, it must not contain unescaped double-quote characters (") or sequences that would break an HTML attribute. The function does not validate or escape the class name.

Interdependencies:
- Both parameters are concatenated into a single HTML fragment without validation; safety and correctness depend entirely on the caller performing required escaping/sanitization.

## Returns:
    str:
        A single-line HTML fragment of the form:
        '<span class="{cls}">{text}</span>'
        Possible return behaviors and edge cases:
        - If cls contains a double quote, the returned fragment will include that quote and may produce invalid or broken HTML.
        - If text contains HTML, that HTML will be included verbatim (which can lead to XSS when text is untrusted).
        - If non-string objects are supplied, they are converted to strings (None -> "None").

## Raises:
    This function does not raise exceptions itself. Because of Python's formatting coercion, passing non-string values will not raise here; they will be converted to strings. Exceptions may still occur upstream if callers attempt further operations on the returned string, or if __format__/__str__ implementations on supplied objects raise.

## Constraints:
Preconditions:
- Prefer callers pass already-escaped/sanitized text when the content originates from untrusted sources.
- Ensure class names do not contain characters that will break HTML attributes (notably double quotes).

Postconditions:
- Returns a deterministic HTML fragment string that contains the provided class and content.
- No mutation of inputs or external state occurs.

## Side Effects:
- None internal: no file or network I/O, no global state mutation.
- Security side effect to be aware of: returning unescaped user-controlled content may enable XSS vulnerabilities when the result is embedded in a web page. This is a risk arising from how the return value is used, not from the function performing I/O.

## Control Flow:
flowchart TD
    Start --> Interpolate
    Interpolate --> ReturnResult[Return "<span class=\"{cls}\">{text}</span>"]

## Examples:
Note: examples show caller-side escaping when appropriate.

Example — handling untrusted text safely:
    from markupsafe import escape
    user_input = '<script>alert(1)</script>'
    safe_text = escape(user_input)                 # caller performs escaping
    html = fmt_class(safe_text, 'user-content')
    # html -> '<span class="user-content">&lt;script&gt;alert(1)&lt;/script&gt;</span>'

Example — passing None or numbers (coerced to strings):
    html_none = fmt_class(None, 'meta')            # None becomes "None"
    # html_none -> '<span class="meta">None</span>'
    html_num = fmt_class(42, 'count')              # number becomes "42"
    # html_num -> '<span class="count">42</span>'

Example — when raw HTML is intentionally supplied (trusted content):
    raw_html = '<strong>Note</strong>'             # trusted HTML fragment
    html = fmt_class(raw_html, 'highlight')
    # html -> '<span class="highlight"><strong>Note</strong></span>'

Example — problematic class name (avoid quotes):
    bad_cls = 'bad"class'
    html = fmt_class('text', bad_cls)
    # html -> '<span class="bad"class">text</span>'   # invalid HTML; caller must avoid such names

Best practices:
- Escape text with markupsafe.escape (or equivalent) before calling when text can contain user input.
- Validate or sanitize cls to a whitelist of allowed characters (letters, digits, hyphen, underscore) if cls originates from user input.

## `src.ydata_profiling.report.formatters.fmt_bytesize` · *function*

## Summary:
Convert a numeric quantity into a concise human-readable binary-size string (uses 1024-based prefixes) with one decimal place, e.g., "1.5 KiB" or "1.0 MiB".

## Description:
This function iteratively scales a numeric value by factors of 1024 and selects the first binary prefix for which the absolute value is less than 1024. It returns a formatted string containing the numeric value with one decimal place, a single space, and the concatenation of the chosen binary prefix and the provided suffix (for example, "GiB").

Known callers in the supplied observation:
- No direct callers were discovered in the provided graph. In typical reporting/formatting contexts this helper is used when rendering file sizes, memory usage, or other byte-like quantities for display in reports or templates.

Why this is a separate function:
- Centralizes the binary-size formatting logic so reporting and templating components can reuse a consistent representation (binary 1024-based prefixes and fixed one-decimal formatting) without duplicating scaling and formatting rules.

## Args:
    num (float):
        Numeric quantity to format.
        - Expected types: float or int (types that support abs(), true division by a float, and formatting with format-specifier '.1f').
        - Not supported as-is: decimal.Decimal or other numeric-like types that cannot be divided in-place by a Python float (see Constraints for details).
        - Notes on special float values:
            * float('inf') and -float('inf'): will be propagated and formatted as "inf" or "-inf" with the highest unit (Yi + suffix).
            * float('nan'): comparisons with 1024 always fail; the function will fall through the loop and return "nan Yi<suffix>".
    suffix (str, optional):
        Trailing label appended after the binary prefix (default "B").
        - Typical usage: "B" to produce outputs like "KiB", "MiB".
        - The function concatenates the prefix and suffix directly (e.g., prefix "Ki" + suffix "iB" -> "KiiB").

## Returns:
    str: A formatted string of the form "<value> <prefix><suffix>" where:
    - "<value>" is the numeric quantity rounded/formatted to one decimal place.
    - There is always one space between the numeric value and the composed unit (prefix+suffix).
    - Possible unit prefixes returned: "", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", or the final fallback "Yi".
    - Example outputs: "512.0 B", "1.5 KiB", "1.0 MiB", "nan YiB", "inf YiB".

## Raises:
    - TypeError: If `num` does not support abs(num) or division by a float (e.g., passing a decimal.Decimal will raise TypeError when dividing by 1024.0).
    - TypeError or ValueError: If `num` cannot be formatted with the float format-specifier used ("{num:3.1f}" / "{num:.1f}"), formatting may raise these exceptions.
    - The function itself does not explicitly raise custom exceptions; any raised exceptions originate from Python's numeric operations or formatting.

## Constraints:
Preconditions:
    - `num` must be a numeric type compatible with:
        * abs(num)
        * division by a float literal (num /= 1024.0)
        * float-format formatting ('.1f').
    - If using decimal.Decimal, convert to float before calling (e.g., float(my_decimal)) or adapt the implementation to use Decimal(1024) and Decimal arithmetic.

Postconditions:
    - Returns a non-empty string with one decimal place, a single space, and a concatenated unit (prefix+suffix).
    - The function does not modify external state or perform I/O.

## Side Effects:
    - None. Pure computation and string formatting only.

## Control Flow:
flowchart TD
    Start([Start]) --> ForEachUnit{For each unit in ["","Ki","Mi","Gi","Ti","Pi","Ei","Zi"]}
    ForEachUnit --> Check{abs(num) < 1024.0 ?}
    Check -- Yes --> ReturnFmt1["Return f\"{num:3.1f} {unit}{suffix}\""]
    Check -- No --> Divide["num /= 1024.0"]
    Divide --> ContinueLoop{More units left?}
    ContinueLoop -- Yes --> ForEachUnit
    ContinueLoop -- No --> FinalReturn["Return f\"{num:.1f} Yi{suffix}\""]
    ReturnFmt1 --> End([End])
    FinalReturn --> End

## Examples:
Example 1 - Typical byte sizes
    fmt_bytesize(512)         -> "512.0 B"
    fmt_bytesize(1023)        -> "1023.0 B"
    fmt_bytesize(1024)        -> "1.0 KiB"
    fmt_bytesize(1536)        -> "1.5 KiB"
    fmt_bytesize(1048576)     -> "1.0 MiB"

Example 2 - Negative values
    fmt_bytesize(-1536)       -> "-1.5 KiB"

Example 3 - Custom suffix (illustrates direct concatenation)
    fmt_bytesize(2048, suffix="iB") -> "2.0 KiiB"
    Note: To obtain the common "KiB" output, use the default suffix="B".

Example 4 - Special float values
    fmt_bytesize(float('inf')) -> "inf YiB"
    fmt_bytesize(float('nan')) -> "nan YiB"

Implementation details worth noting:
    - The first successful return uses the format specifier "{num:3.1f}" (a minimum field width of 3 with one decimal), while the final fallback uses "{num:.1f}" (no minimum width). This affects padding for small numeric values but not numeric precision.
    - The function uses IEC-style binary prefixes (Ki, Mi, Gi, ...), i.e., powers of 1024.

## `src.ydata_profiling.report.formatters.fmt_percent` · *function*

## Summary:
Convert a fractional numeric value into a one-decimal-place percentage string, optionally using human-friendly shorthand for extremely small positive values ("< 0.1%") and values extremely close to 1 but still less than 1 ("> 99.9%").

## Description:
This small, pure formatting helper turns a numeric fraction (commonly in the 0.0–1.0 range) into a consistent percentage string for inclusion in reports, alerts, or UI displays. The function is intentionally presentation-focused: it performs no normalization or validation beyond using Python numeric operations.

Known callers within the codebase and typical context:
- No direct callers are present in the provided source snapshot for this file. A function of this name/shape is also present in other modules (for example, src.ydata_profiling.model.alerts.fmt_percent) and is intended to be used by reporting or alert-generation code that needs consistent percentage text.
- Typical invocation point: when preparing textual output for a report or an alert where a fraction must be shown to a user in percent form.

Why this is a separate function:
- Encapsulates formatting choices (one decimal place, minimum field width, and two textual shorthands) so display logic remains consistent and maintainable across the codebase.
- Keeps consumers free of formatting details and centralizes any future display-rule changes.

## Args:
    value (float):
        - A numeric value to format. Typical semantic range is 0.0 to 1.0 (0%–100%), but any numeric value is accepted and simply multiplied by 100 and formatted.
        - Must support Python numeric operations used in the function: round(value, 3), comparison operators, and multiplication.
    edge_cases (bool, default True):
        - If True, the function applies two textual shorthand outputs:
            * If round(value, 3) == 0 and value > 0, returns "< 0.1%".
            * If round(value, 3) == 1 and value < 1, returns "> 99.9%".
        - If False, those shorthand checks are skipped and the numeric formatting is always returned.

Interdependencies:
- The shorthand checks depend both on rounding to three decimals and on strict inequality checks (value > 0 or value < 1). Both conditions must hold for a shorthand to be returned.

## Returns:
    str: A percentage representation of the input.

    Exact possible outcomes (directly derivable from the implementation):
    - "< 0.1%": returned when edge_cases is True AND round(value, 3) == 0 AND value > 0 (tiny positive values that round to 0.000 at 3 decimals).
    - "> 99.9%": returned when edge_cases is True AND round(value, 3) == 1 AND value < 1 (values that round to 1.000 at 3 decimals but are strictly less than 1).
    - Otherwise: returns the numeric formatting f"{value*100:2.1f}%", i.e., the numeric value multiplied by 100, formatted with one decimal place and a minimum field width of 2.

    Representative exact outputs:
    - value == 0 -> "0.0%"
    - value == 1 -> "100.0%"
    - value = 0.1234 -> "12.3%"
    - value = 1.234 -> "123.4%"

## Raises:
    - No custom exceptions are raised by the function.
    - Standard exceptions may propagate from Python numeric operations if the input is inappropriate:
        * TypeError: if the provided value does not support rounding, comparison, or multiplication (e.g., passing a non-numeric object).
        * Other built-in exceptions may surface from the underlying numeric operations depending on the type of value provided.
    - The function does not perform explicit NaN/inf checks; any such behavior follows Python's numeric and formatting semantics.

## Constraints:
Preconditions:
    - Caller should provide a numeric type (float, int, numpy/pandas numeric scalar). The function assumes no normalization; callers must supply values in their intended semantic range (e.g., 0..1 for fractions).

Postconditions:
    - The function returns a string.
    - If edge_cases True and a shorthand condition is met, the return is one of the two shorthand strings; otherwise it is a numeric percentage string formatted to one decimal place.

## Side Effects:
    - None. The function is pure: it performs no I/O and mutates no external state.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckEdge{edge_cases == True?}
    CheckEdge -->|No| FormatNumeric[Compute value*100 and format with "2.1f" -> Return]
    CheckEdge -->|Yes| CheckTiny[round(value,3) == 0 AND value > 0?]
    CheckTiny -->|Yes| ReturnTiny[Return "< 0.1%"]
    CheckTiny -->|No| CheckNearOne[round(value,3) == 1 AND value < 1?]
    CheckNearOne -->|Yes| ReturnNearOne[Return "> 99.9%"]
    CheckNearOne -->|No| FormatNumeric

## Examples:
- Typical cases:
    - fmt_percent(0.1234) -> "12.3%"
    - fmt_percent(0.0004) -> "< 0.1%"  (edge_cases True; tiny positive)
    - fmt_percent(0.9997) -> "> 99.9%" (edge_cases True; very close to 1 but < 1)
    - fmt_percent(0.0) -> "0.0%"
    - fmt_percent(1.0) -> "100.0%"
    - fmt_percent(1.234) -> "123.4%"  (works for values > 1)

- Disabling shorthand behavior:
    - fmt_percent(0.0004, edge_cases=False) -> "0.0%"

- Negative and special numeric values (behavior follows code's numeric operations):
    - fmt_percent(-0.01) -> "-1.0%"
    - fmt_percent(-0.0004) -> "-0.0%" (small negative numbers do not trigger the "< 0.1%" shorthand because value > 0 is required)
    - fmt_percent(float('nan')) -> "nan%"  (formatting behavior follows Python's float formatting)
    - fmt_percent(float('inf')) -> "inf%"  (similarly follows Python's formatting rules)

- Defensive usage pattern:
    - Example:
        try:
            s = fmt_percent(maybe_numeric_value)
        except TypeError:
            # Handle/log invalid input; function expects a numeric input
            s = "n/a"

## `src.ydata_profiling.report.formatters.fmt_timespan` · *function*

*No documentation generated.*

## `src.ydata_profiling.report.formatters.fmt_timespan_timedelta` · *function*

## Summary:
Convert a value representing a time span into a human-readable string: if given a pandas Timedelta, normalize it to seconds (including positive micro- and nanosecond parts) and delegate to the generic timespan formatter; otherwise format the value as a numeric string via the numeric formatter.

## Description:
Known callers within the codebase:
- No direct call sites were provided in this analysis. Typical callers are report rendering code, column/variable summary formatters, or HTML templates that need to display duration or elapsed-time values produced by dataframes or profiling computations.

Typical trigger/context:
- Called when rendering or serializing values that may be pandas Timedelta objects (e.g., durations computed from datetime diffs) and when a human-readable timespan string is desired for reports or UI.

Why this logic is a separate function:
- Responsibility is to detect Timedelta-like values and convert them into a normalized number of seconds (including any positive microsecond and nanosecond parts) before delegating to a timespan formatter. It centralizes Timedelta-specific handling (detection and normalization) so the more general timespan formatting implementation (fmt_timespan) and numeric formatting (fmt_numeric) can remain focused on presentation. This keeps type-dispatch and small normalization logic out of higher-level rendering code.

## Args:
    delta (Any):
        The value to format. Expected either a pandas Timedelta-like object (the code checks isinstance(delta, pd.Timedelta)) or any other numeric-like value that fmt_numeric can handle. No static type is enforced here.
    detailed (bool, default=False):
        Passed through to fmt_timespan when delta is a pandas Timedelta. Controls whether the timespan formatter emits a detailed representation. Ignored for non-Timedelta inputs.
    max_units (int, default=3):
        Passed through to fmt_timespan when delta is a pandas Timedelta. Limits the number of time units to show (e.g., days, hours, minutes). Ignored for non-Timedelta inputs.
    precision (int, default=10):
        Used only when delta is not recognized as a pandas Timedelta: forwarded to fmt_numeric to control significant-digit formatting. Ignored for Timedelta inputs.

Interdependencies:
- detailed and max_units only affect the branch where delta is a pandas Timedelta.
- precision only affects the non-Timedelta branch (fmt_numeric call).

## Returns:
    str:
        - If delta is detected as a pandas Timedelta: returns the string result of calling fmt_timespan(num_seconds, detailed, max_units), where num_seconds is computed from delta.total_seconds() and augmented by any positive microsecond and nanosecond parts of the Timedelta.
        - If delta is not a pandas Timedelta: returns the string result of calling fmt_numeric(delta, precision).
    Possible return shapes:
        - Any string value produced by fmt_timespan for numeric seconds (typical human-friendly duration like "1 day, 2 hours" or similar depending on fmt_timespan).
        - Any string value produced by fmt_numeric (compact numeric string; may include HTML fragments for scientific notation per fmt_numeric behavior).
    Notes on edge returns:
        - The function does not itself return None or non-string types; underlying formatters determine the exact string content and may produce special values like "nan" or "inf" as strings if those arise.

## Raises:
    - This function raises no exceptions explicitly.
    - Exceptions from underlying calls may propagate:
        * If pandas (pd) is not available or pd.Timedelta is undefined, a NameError/AttributeError could occur at runtime before the isinstance check resolves.
        * If delta is a pandas Timedelta, exceptions from delta.total_seconds(), or from accessing delta.microseconds or delta.nanoseconds, will propagate.
        * If fmt_timespan or fmt_numeric are missing or raise, those exceptions propagate unchanged (e.g., TypeError, ValueError).
    In short: any errors raised by pd.Timedelta attributes access, fmt_timespan, or fmt_numeric will propagate to the caller.

## Constraints:
Preconditions:
    - The module must expose fmt_timespan and fmt_numeric in the same runtime scope; otherwise the delegations will fail.
    - The symbol pd used in isinstance(delta, pd.Timedelta) must refer to the pandas module (common convention: "import pandas as pd") so that the isinstance check works correctly.
    - Callers should expect a string result and should not pass objects for which fmt_numeric or fmt_timespan cannot produce a string.

Postconditions:
    - The returned value is a str (result of fmt_timespan or fmt_numeric).
    - No global state is modified by this function.

## Side Effects:
    - None intrinsic to this function. No I/O, no network calls, no writes to external state.
    - It delegates to other formatters that are also expected to be pure/string-producing utilities.

## Control Flow:
flowchart TD
    Start([Start]) --> IsTimedelta{"isinstance(delta, pd.Timedelta)?"}
    IsTimedelta -- Yes --> ComputeSeconds["num_seconds = delta.total_seconds()"]
    ComputeSeconds --> AddMicro{"delta.microseconds > 0 ?"}
    AddMicro -- Yes --> AddMicroOp["num_seconds += delta.microseconds * 1e-6"]
    AddMicro -- No --> SkipMicro["no change"]
    AddMicroOp --> CheckNano
    SkipMicro --> CheckNano
    CheckNano{"delta.nanoseconds > 0 ?"} --> AddNanoOp["num_seconds += delta.nanoseconds * 1e-9"]
    CheckNano -- No --> SkipNano["no change"]
    AddNanoOp --> CallFmtTimespan["return fmt_timespan(num_seconds, detailed, max_units)"]
    SkipNano --> CallFmtTimespan
    IsTimedelta -- No --> CallFmtNumeric["return fmt_numeric(delta, precision)"]
    CallFmtTimespan --> End([End])
    CallFmtNumeric --> End

## Examples:
- Timedelta path (typical):
    - Input: a pandas Timedelta representing 1 day, 2 seconds and 300 microseconds.
    - Behavior: total_seconds() produces the base seconds; because microseconds > 0 the function adds 300 * 1e-6 to num_seconds; nanoseconds will be added only if > 0. The resulting float seconds value is passed to fmt_timespan with the given detailed and max_units settings and the returned human-readable duration string is returned to the caller.

- Non-timedelta (numeric) path:
    - Input: a plain numeric value or object that fmt_numeric accepts (e.g., float 12345.0).
    - Behavior: The function forwards (delta, precision) to fmt_numeric and returns whatever compact numeric string fmt_numeric produces (for example a formatted decimal or HTML-friendly scientific notation).

- Error handling example:
    - If fmt_timespan raises ValueError for an out-of-range seconds value, that ValueError will propagate to the caller. Callers should wrap calls in try/except if they need to handle such formatting errors explicitly.

## `src.ydata_profiling.report.formatters.fmt_numeric` · *function*

## Summary:
Formats a numeric value into a concise, human-readable string using general-format significant digits and converts scientific notation into an HTML-friendly form (using " × 10<sup>...</sup>" for exponents).

## Description:
Known callers within the codebase:
- No specific caller functions were provided for this run. Typical callers are report rendering code or HTML templates that need to display numeric summary values (e.g., statistics, aggregated metrics) in a readable form in generated reports.

Why this function exists:
- Formatting numeric values consistently for human-readable HTML reports requires special handling of scientific notation. This function centralizes that logic so callers can obtain a compact string suitable for insertion into HTML output and avoids duplicating exponent-to-HTML conversion throughout the reporting pipeline.

Responsibility boundary:
- Convert a numeric value to a string with a given significant-digit precision using Python's general format ("g"), then transform any scientific notation parts ("e+" or "e-") into an HTML exponent fragment. It does not perform HTML escaping, localization, or rounding policy beyond the "g" format behavior.

## Args:
    value (float):
        The numeric value to format. Semantically accepts Python numeric types (e.g., float, int, decimal.Decimal, numpy numeric types) that are compatible with Python's format specification. Values that are not compatible will raise formatting-related exceptions.
    precision (int, default=10):
        Number of significant digits used by the general-format specifier ("g"). Should be a non-negative integer (typical usage: positive integers). Negative precision or non-integer types will cause the underlying formatting call to raise an exception.

Interdependencies:
- The precision controls how Python's "{:.{precision}g}" formats the magnitude and whether the result uses scientific notation at all. The post-processing logic only runs when the formatted string contains "e+" or "e-".

## Returns:
    str:
        A string representation of the input numeric value:
        - If the formatted string does not contain scientific notation, the original formatted text produced by "{:.{precision}g}" is returned unchanged.
        - If scientific notation is present (substrings "e+" or "e-"), the exponent is rewritten into an HTML fragment using a multiplication sign and superscript tag:
            Example transformation: "1.23e+04" -> "1.23 × 10<sup>4</sup>"
            Example transformation: "1.23e-04" -> "1.23 × 10<sup>-4</sup>"
        - Leading zeros in exponent text are removed (e.g., "<sup>04</sup>" becomes "<sup>4</sup>").
        - The return value is an HTML fragment (contains "<sup>...</sup>" for exponents); it is not auto-escaped and should be treated appropriately by template renderers.

All possible return shapes:
- Plain formatted string without HTML (for non-scientific results, NaN, inf, etc.)
- Formatted string containing HTML superscript exponent when the "g" formatted value used exponential notation

## Raises:
    ValueError:
        If the format specification or provided precision is invalid for Python's format machinery (e.g., negative precision in some Python versions or otherwise invalid format string).
    TypeError:
        If the provided value is not compatible with the format specifier (for example, passing an incompatible object that does not support numeric formatting).
    Any exceptions raised by the underlying formatting operation (via str.format) may propagate.

## Constraints:
Preconditions:
- Caller should pass a numeric value (or an object that supports formatting with the "g" specifier).
- precision should be an integer (preferably >= 0). The function does not validate the type beyond relying on Python formatting.

Postconditions:
- The returned value is a str.
- If the input formatted value used scientific notation, the returned string contains an HTML superscript exponent fragment (" × 10<sup>...</sup>") with no leading zero in the exponent, and includes the correct minus sign for negative exponents.

## Side Effects:
- None. The function performs pure string operations and does not perform I/O, modify global state, or call external services.
- Note: The function produces HTML (sup tags) but does not escape values; embedding the result into web pages should be handled by the caller (escape or mark as safe as appropriate).

## Control Flow:
flowchart TD
    Start([Start]) --> Format["Format using '{:.{precision}g}'"]
    Format --> CheckExp{"Contains 'e+' or 'e-'?"}
    CheckExp -- No --> ReturnPlain["Return formatted string"]
    CheckExp -- Yes --> ForLoop["For each v in ['e+','e-']"]
    ForLoop --> CheckV{"v present in formatted string?"}
    CheckV -- No --> NextV["Continue to next v"]
    CheckV -- Yes --> SignAssign["Set sign = '-' if v == 'e-' else ''"]
    SignAssign --> ReplaceExp["Replace v with ' × 10<sup>' and append '</sup>'"]
    ReplaceExp --> StripLeadingZero["Replace '<sup>0' with '<sup>'"]
    StripLeadingZero --> InsertSign["Insert sign into '<sup>' as '<sup>{sign}'"]
    InsertSign --> ReturnHtml["Return modified HTML-formatted string"]
    NextV --> CheckV
    ReturnPlain --> End([End])
    ReturnHtml --> End

## Examples:
- Positive exponent example:
    Input: value = 12345.0, precision = 3
    "{:.3g}" => "1.23e+04"
    Output: "1.23 × 10<sup>4</sup>"

- Negative exponent example:
    Input: value = 0.000012345, precision = 3
    "{:.3g}" => "1.23e-05"
    Output: "1.23 × 10<sup>-5</sup>"

- Non-scientific (no exponent):
    Input: value = 123.456, precision = 6
    "{:.6g}" => "123.456"
    Output: "123.456"

- Special float values:
    Input: value = float("nan"), precision = 5
    Output: "nan"  (no exponent rewriting)
    Input: value = float("inf"), precision = 5
    Output: "inf"  (no exponent rewriting)

Usage note:
- Because the function returns an HTML fragment when scientific notation is present, callers embedding the result into HTML templates should ensure appropriate escaping or marking-as-safe behavior depending on the template engine.

## `src.ydata_profiling.report.formatters.fmt_number` · *function*

## Summary:
Formats an integer-like value into a locale-aware string using Python's "n" numeric format specifier.

## Description:
This small utility returns a string representation of an integer-like value using Python's format specification "n", which produces a locale-aware presentation (e.g., grouping and decimal separators follow the active locale). It centralizes numeric formatting for report generation so callers across the reporting pipeline present integers consistently.

Known callers within the provided codebase snapshot:
- None found in the provided snapshot. (In the full project this is typically used by report rendering/formatting utilities that build human-readable tables and summaries.)

Why this is a separate function:
- Encapsulates the exact formatting choice ("n") in one place so changes (for example to use grouping, a different specifier, or additional pre-processing) can be made centrally without touching many call sites.
- Improves readability where formatting is used repeatedly in templates and report builders.

## Args:
    value (int):
        The integer-like value to format.
        - Expected type: int (annotation). The implementation uses Python's format machinery, so any object supporting numeric formatting with the "n" specifier (e.g., int, float, numpy integer types) will work.
        - Allowed range/value: any integer representable by Python (arbitrary precision). If a non-numeric or incompatible object is passed, formatting will raise an error.

## Returns:
    str:
        A string containing the formatted representation of the input value according to Python's "n" format specification.
        - Examples of possible return values:
            * 12345 -> "12345" (or locale-specific grouping like "12,345" if locale enables grouping)
            * -10 -> "-10"
            * Large integers remain fully represented (no truncation)
        - There is no None return; the function always returns a string on successful formatting.

## Raises:
    TypeError:
        Raised by Python's format machinery if the passed `value` does not support numeric formatting with the "n" specifier (for example, passing None or an arbitrary object).
    ValueError:
        Unlikely in this implementation because the format specifier is fixed; would only occur if Python's formatting machinery raises it for a given value.

## Constraints:
    Preconditions:
        - Caller should supply an integer-like value (int or numeric type that implements formatting).
        - No assumptions are made about the current locale; the output may vary depending on the active locale settings.

    Postconditions:
        - Returns a str representing the input value formatted with the "n" specifier.
        - The function does not mutate input objects.

## Side Effects:
    - None: the function performs pure formatting and does not perform I/O, modify globals, or call external services.
    - Note: The appearance of the returned string can be affected by the process-wide locale settings, which are external state. The function itself does not change locale.

## Control Flow:
flowchart TD
    Start --> FormatAttempt[Attempt f"{value:n}"]
    FormatAttempt -->|Success| ReturnStr[Return formatted string]
    FormatAttempt -->|TypeError/ValueError| RaiseErr[Propagate formatting exception]

## Examples:
Example — basic usage
    value = 12345
    s = fmt_number(value)
    # s -> "12345" (or "12,345" if a locale with grouping is active)

Example — negative and large values
    fmt_number(-42)        # -> "-42"
    fmt_number(10**12)     # -> "1000000000000" (or locale-grouped equivalent)

Example — handling non-numeric inputs
    try:
        fmt_number(None)
    except TypeError:
        # handle the error: log, coerce, or substitute a default
        s = "N/A"

Example — using with numpy integer types
    import numpy as np
    fmt_number(np.int64(1000))  # typically -> "1000"

## `src.ydata_profiling.report.formatters.fmt_array` · *function*

## Summary:
Return a concise string representation of a NumPy array by temporarily applying a short-printing NumPy configuration.

## Description:
Converts the provided NumPy array (or any object with a meaningful str()) to a string while temporarily adjusting NumPy's print options so that large arrays are condensed. The function uses a context manager to set numpy.printoptions(threshold=3, edgeitems=threshold_param) for the duration of the conversion; after the with-block exits, NumPy's global print options are restored.

Known callers within the provided snapshot:
- No direct callers were discovered in the supplied code snapshot. Typical callers are reporting or formatting utilities that need a stable, human-friendly, truncated string for arrays when producing text or HTML reports, logs, or debugging output.

Why this is a separate function:
- Centralizes the pattern "temporarily set print options → stringify array → restore options" so callers don't need to manage NumPy's global print configuration.
- Ensures consistent short-format array representations across the reporting/formatting pipeline.

## Args:
    value (np.ndarray):
        The object to stringify. Intended to be a numpy.ndarray but any object is accepted; the function simply calls str(value) inside the configured NumPy printoptions context.
    threshold (Any, optional): default: np.nan
        The value passed to numpy.printoptions as the edgeitems argument while the function runs.
        - The function sets numpy.printoptions(threshold=3, edgeitems=threshold).
        - If an integer n is provided, up to n items from each edge of each dimension will be shown for large arrays (per NumPy's edgeitems semantics).
        - If left as the default (np.nan), the literal np.nan value is passed as edgeitems; whether this is accepted depends on the NumPy implementation/version.

Note on naming/behavior:
- Although the parameter is named threshold, the code maps this parameter to the numpy.printoptions edgeitems keyword; the printoptions threshold argument is hard-coded to 3 inside the function.

## Returns:
    str: The textual representation produced by str(value) while NumPy print options are temporarily set as described.
    - For numpy.ndarray inputs, this typically yields a truncated representation (showing a few leading and trailing elements) according to NumPy's formatting rules with threshold=3 and the supplied edgeitems value.
    - For non-array inputs, returns str(value) under the same temporarily-applied print options (which may have no effect if the object's __str__ does not use NumPy formatting).
    - If str(value) returns an empty string, that empty string is returned.

## Raises:
    - The function does not explicitly raise exceptions. Any exception raised by numpy.printoptions(...) or by str(value) will propagate to the caller unchanged.
    - Because the function passes the provided threshold parameter directly to numpy.printoptions(edgeitems=...), an incompatible value may cause numpy.printoptions to raise; the exact exception types depend on the NumPy implementation and are not asserted here.

## Constraints:
Preconditions:
    - NumPy must be importable as the symbol used in the runtime environment (the function uses np.printoptions and expects np to be bound to the NumPy module).
    - Prefer passing an integer-like value for threshold when deterministic edge-items truncation is required.

Postconditions:
    - NumPy global print options are restored to their prior values when the function returns (the change is confined to the context manager).
    - The caller receives the string produced by str(value) executed under the temporary print options.

## Side Effects:
    - Temporarily modifies NumPy's global print options inside the with-block; these options are reverted after the block exits.
    - No file, network, stdout/stderr I/O, or persistent external state modifications are performed by this function.

## Control Flow:
flowchart TD
    Start --> Enter_with_block
    Enter_with_block --> Set_np_printoptions["Call np.printoptions(threshold=3, edgeitems=threshold)"]
    Set_np_printoptions --> Stringify["return_value = str(value)"]
    Stringify --> Exit_with_block
    Exit_with_block --> Return["return return_value"]
    Return --> End

## Examples:
Example 1 — Typical use for large 1-D array
    import numpy as np
    arr = np.arange(100)
    # Show only 2 items at each edge while formatting the string
    s = fmt_array(arr, threshold=2)
    # s might look like: "[ 0  1 ... 98 99]" (exact formatting depends on NumPy version)

Example 2 — Non-array object
    obj = {"a": list(range(10))}
    # Even though obj is not a numpy.ndarray, str(obj) is returned (np.printoptions has no effect here)
    s = fmt_array(obj, threshold=1)
    # s == str(obj)

Example 3 — Defensive usage
    import numpy as np
    arr = np.arange(10)
    try:
        # Provide an integer threshold for predictable behavior
        s = fmt_array(arr, threshold=3)
    except Exception as e:
        # If NumPy rejects the edgeitems value or str(value) raises, handle the propagated exception
        handle_error(e)

## `src.ydata_profiling.report.formatters.fmt` · *function*

## Summary:
Dispatches a value to a numeric formatter when it is a built-in int or float; otherwise returns an HTML-escaped string representation suitable for inclusion in HTML output.

## Description:
Known callers within the codebase:
- Report rendering code and HTML templates that need a compact, safe-to-insert textual representation of a value for display in generated reports.
- Any higher-level formatting utilities that prepare cell/summary values for HTML reports.

Typical trigger/context:
- Called when rendering individual values into report HTML fragments (for example, when producing table cells, summary statistics, or tooltip text). The caller wants: (a) human-friendly scientific-notation formatting for plain Python numeric types, and (b) HTML-escaped text for all other values to avoid injection/markup issues.

Why this logic is extracted into its own function:
- Enforces a single, consistent dispatch policy between numeric formatting (via fmt_numeric) and HTML-escaping for non-numeric values. Keeping this routing in one function prevents duplicating the numeric-vs-non-numeric decision across templates and rendering code and centralizes the escape semantics.

Responsibility boundary:
- Decide whether a value is a built-in numeric (exact type float or int) and delegate to fmt_numeric for such values.
- For every other type, produce an HTML-escaped string via markupsafe.escape and return it as a plain Python str.
- Does not attempt to coerce or convert non-built-in numeric types (e.g., numpy scalars, decimal.Decimal) into built-in numeric types before formatting; it also does not perform localization.

## Args:
    value (Any):
        - Any Python object.
        - If value is exactly of type float or exactly of type int (type(value) is float or int), it will be passed to fmt_numeric for numeric-specific formatting.
        - All other types (including bool, decimal.Decimal, numpy scalar types, pandas types, None, str, dict, list, etc.) are handled by markupsafe.escape and returned as a string.
        - Note: bool is not treated as numeric here because its type is bool (not int) and the code checks type equality.

## Returns:
    str:
        - If value is a built-in float or int: returns whatever fmt_numeric(value) returns (a str). Typically this is a concise human-readable number; for sufficiently large/small magnitudes fmt_numeric rewrites scientific notation into an HTML fragment using " × 10<sup>...</sup>".
        - Otherwise: returns str(escape(value)) — an HTML-escaped string representation of the value (no automatic numeric exponent conversion).
        - The function always returns a Python str object.

Edge-case returns:
    - For numpy scalar numbers, decimal.Decimal, pandas numeric types: these are not recognized as built-in float/int by the type check and therefore return the escaped string form (not the specialized numeric formatting).
    - For None: returns "None" (escaped string form).
    - For values where fmt_numeric raises (when value is a built-in float/int but formatting fails), that exception will propagate.

## Raises:
    - No exceptions are explicitly raised by this function itself.
    - Exceptions from fmt_numeric will propagate when value is a built-in float or int (e.g., TypeError/ValueError raised by the numeric formatter).
    - Exceptions from markupsafe.escape are unlikely for normal usages but would propagate if encountered (e.g., if the escape implementation receives an object that raises on string conversion).

## Constraints:
Preconditions:
    - None strictly enforced. Callers should be prepared that only exact built-in float and int are treated as numeric.
    - If callers expect other numeric-like types (numpy, decimal) to be numerically formatted, they must convert/coerce them to built-in float/int before calling fmt.

Postconditions:
    - The returned value is a str.
    - Built-in float/int inputs were processed by fmt_numeric and thus follow fmt_numeric's postconditions (e.g., HTML exponent formatting when applicable).
    - Non-built-in types are HTML-escaped and safe for insertion into HTML when used as-is.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state.
    - It relies on markupsafe.escape to produce HTML-escaped text but does not mark strings as safe for template engines — callers should decide how to embed the returned string into templates.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckType{"type(value) in [float, int]?"}
    CheckType -- Yes --> CallNum[/"Call fmt_numeric(value)"/]
    CallNum --> ReturnNum["Return fmt_numeric result (str)"]
    CheckType -- No --> Escape["Call markupsafe.escape(value)"]
    Escape --> ToStr["Call str(...) on the escaped value"]
    ToStr --> ReturnEsc["Return escaped string"]
    ReturnNum --> End([End])
    ReturnEsc --> End

## Examples:
- Numeric (built-in float) — delegated to numeric formatter:
    Example: value = 1.2345e9
    Behavior: fmt delegates to fmt_numeric(1.2345e9). With fmt_numeric's default precision this will typically produce an HTML-friendly scientific format such as "1.2345 × 10<sup>9</sup>".

- Integer (built-in int) — delegated to numeric formatter:
    Example: value = 12345
    Behavior: fmt calls fmt_numeric(12345) and returns that string (often "12345" or a compact representation determined by fmt_numeric).

- numpy scalar — not treated as built-in numeric (important edge case):
    Example: value = numpy.float64(1.2345e9)
    Behavior: type is not exactly float, so fmt returns str(escape(value)) — the escape/string form of the numpy scalar — rather than going through fmt_numeric. If callers want numeric formatting for numpy types they should pass float(value) or otherwise convert before calling fmt.

- decimal.Decimal — not treated as built-in numeric:
    Example: value = decimal.Decimal("1.23E+04")
    Behavior: returned value is the HTML-escaped string form of the Decimal, not fmt_numeric output. Convert to float or int first if numeric formatting is required.

- Non-numeric / potential HTML:
    Example: value = "<script>alert('x')</script>"
    Behavior: fmt returns a safely escaped string such as "&lt;script&gt;alert(&#39;x&#39;)&lt;/script&gt;" (exact escaping per markupsafe.escape), preventing HTML injection when inserted into pages.

- Bool:
    Example: value = True
    Behavior: Because type(True) is bool (not int), fmt will escape and return "True" as text (not pass it to fmt_numeric). If numeric treatment for bool is desired, convert explicitly (e.g., int(True)).

Error handling example:
    If a built-in float is passed and fmt_numeric raises a ValueError due to an unexpected formatting issue, the caller can catch it:
    try:
        out = fmt(1.0e1000)  # hypothetically could trigger formatting error in extreme cases
    except (ValueError, TypeError) as e:
        # handle or fallback to a safe escaped representation
        out = str(escape(1.0e1000))

## `src.ydata_profiling.report.formatters.fmt_monotonic` · *function*

## Summary:
Translate an integer code in the range -2..2 into a canonical, human-readable monotonicity label.

## Description:
This small utility maps a discrete monotonicity indicator to one of five fixed strings for use in reports or displays.

Known callers within the provided context:
- No direct callers were discovered in the provided context.

Why this logic is extracted:
- Encapsulates the mapping between integer codes and display labels in a single location so the exact strings and error behavior are consistent across the codebase.

## Args:
    value (int):
        - The monotonicity code. The function signature is annotated with int.
        - Allowed runtime-matching values: -2, -1, 0, 1, 2.
        - Implementation note: the code uses equality comparisons (==) to select the branch. Therefore, at runtime any object that compares equal to one of the allowed integers will follow the corresponding branch (for example, 1.0 == 1 evaluates True). Despite that, callers should prefer passing plain ints to match the annotation.

## Returns:
    str:
        - One of these exact strings (matching the branches in source order):
            - "Strictly increasing"
            - "Increasing"
            - "Not monotonic"
            - "Decreasing"
            - "Strictly decreasing"
        - The returned value is a canonical label intended for presentation.

## Raises:
    ValueError:
        - Raised when the input does not equal any of -2, -1, 0, 1, or 2.
        - Exact message produced by the function: "Value should be integer ranging from -2 to 2."

## Constraints:
    Preconditions:
        - The caller should supply a value that equals one of the integers -2 through 2. The function signature indicates an int, but runtime equality comparison determines acceptance.
    Postconditions:
        - If the function returns normally, the result is exactly one of the five canonical label strings above.
        - If the input does not match any allowed code, a ValueError is raised and no label is returned.

## Side Effects:
    - None: the function performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    Start([Start: receive value])
    Start --> Check2{value == 2?}
    Check2 -- Yes --> StrictlyIncreasing["Return: \"Strictly increasing\""]
    Check2 -- No --> Check1{value == 1?}
    Check1 -- Yes --> Increasing["Return: \"Increasing\""]
    Check1 -- No --> Check0{value == 0?}
    Check0 -- Yes --> NotMonotonic["Return: \"Not monotonic\""]
    Check0 -- No --> CheckNeg1{value == -1?}
    CheckNeg1 -- Yes --> Decreasing["Return: \"Decreasing\""]
    CheckNeg1 -- No --> CheckNeg2{value == -2?}
    CheckNeg2 -- Yes --> StrictlyDecreasing["Return: \"Strictly decreasing\""]
    CheckNeg2 -- No --> Error["Raise ValueError(\"Value should be integer ranging from -2 to 2.\")"]
    StrictlyIncreasing --> End([End])
    Increasing --> End
    NotMonotonic --> End
    Decreasing --> End
    StrictlyDecreasing --> End
    Error --> End

## Examples:
    # Valid inputs (exact matches)
    >>> fmt_monotonic(2)
    'Strictly increasing'
    >>> fmt_monotonic(0)
    'Not monotonic'
    >>> fmt_monotonic(-1)
    'Decreasing'

    # Invalid input triggers the documented ValueError
    >>> try:
    ...     fmt_monotonic(3)
    ... except ValueError as e:
    ...     print(str(e))
    Value should be integer ranging from -2 to 2.

    # Runtime behavior with non-int that compares equal to an allowed integer
    >>> fmt_monotonic(1.0)
    'Increasing'
    >>> import numpy as np
    >>> fmt_monotonic(np.int64(1))
    'Increasing'

## `src.ydata_profiling.report.formatters.help` · *function*

## Summary:
Returns a small HTML badge (a question-mark styled span), optionally wrapped in a link when a URL is provided, intended to be used as an inline "help" or documentation hint in generated HTML reports.

## Description:
This helper constructs a compact HTML fragment representing a help badge. When a URL is supplied the badge is clickable (an anchor wrapping the badge); otherwise a non-clickable badge is returned.

Known callers within the provided context:
- No direct call sites were present in the scanned source for this task. In the larger project this function is typically called by report/template rendering code that assembles section headers, metric labels, or field descriptions in HTML reports to attach help links or tooltips.

Why this logic is extracted into its own function:
- Centralizes the HTML structure and styling for help badges so the same appearance and linking behavior is used consistently across the report. Keeps template/formatter code concise by encapsulating the badge markup generation.

## Args:
    title (str): Text used for the title attribute on the returned element(s). Appears as a tooltip in browsers and is also set on both the anchor (if present) and the inner span. Must be provided; the function signature expects a string.
    url (Optional[str], default=None): If provided and not None, the returned HTML wraps the badge in an <a> element whose href is this value. If None, returns only the badge span.

Notes on interdependencies:
- The function does not perform escaping; title and url are interpolated directly. Callers are responsible for sanitizing or escaping values if untrusted input may be passed.

## Returns:
    str: An HTML fragment as a string. Two possible shapes:
        - If url is not None:
            '<a title="{title}" href="{url}"><span class="badge pull-right" style="color:#fff;background-color:#337ab7;" title="{title}">?</span></a>'
        - If url is None:
            '<span class="badge pull-right" style="color:#fff;background-color:#337ab7;" title="{title}">?</span>'
    The returned string is ready to be embedded inside larger HTML produced by the report generator.

Edge-case return values:
- If title is an empty string, the title attributes will be empty but the HTML will still be returned.
- If non-string values are passed (despite the annotation), Python will convert them to strings via f-string formatting (e.g., None becomes "None") — the function does not validate types at runtime.

## Raises:
    - This function does not raise any exceptions itself in normal operation.
    - Exceptions can occur indirectly if e.g. the f-string formatting triggers an unexpected error from a custom object's __format__ implementation, but there is no explicit raise in the function.

## Constraints:
Preconditions:
    - title should be a value suitable for inclusion in an HTML attribute (preferably a plain string). If the input originates from an untrusted source, it must be escaped or sanitized by the caller to avoid XSS.
    - If url is provided, it should be a valid URL string; the function does not validate URL format.

Postconditions:
    - The function returns a non-empty string containing the HTML fragment described above.
    - No global state is changed.

## Side Effects:
    - None. The function performs pure string construction and does not perform I/O, network calls, global mutations, or logging.

## Control Flow:
flowchart TD
    Start --> CheckURL
    CheckURL{url is not None?}
    CheckURL -->|Yes| ReturnAnchorWithSpan
    CheckURL -->|No| ReturnSpanOnly
    ReturnAnchorWithSpan --> End
    ReturnSpanOnly --> End

## Examples:
- Basic (non-clickable badge):
    help("More information about this metric")
    Possible return:
    <span class="badge pull-right" style="color:#fff;background-color:#337ab7;" title="More information about this metric">?</span>

- Clickable badge (link to documentation):
    help("Open docs", "https://example.com/docs/metric")
    Possible return:
    <a title="Open docs" href="https://example.com/docs/metric"><span class="badge pull-right" style="color:#fff;background-color:#337ab7;" title="Open docs">?</span></a>

- Security note / untrusted input:
    If title is derived from user input such as '<script>alert(1)</script>', that string will be inserted verbatim into the title attribute. To avoid XSS, callers should escape or sanitize title and url before calling this function (for example, using an HTML-escaping utility).

## `src.ydata_profiling.report.formatters.fmt_badge` · *function*

## Summary:
Convert numeric counts written in parentheses inside a string into HTML badge spans, replacing every occurrence of "(<digits>)" with <span class="badge">digits</span>.

## Description:
This small utility transforms textual count markers like "Errors (3)" into an HTML-friendly form "Errors <span class=\"badge\">3</span>" by replacing all occurrences of a left parenthesis, one or more digits, and a right parenthesis with a <span class="badge">...</span> containing the digits.

Known callers within the provided repository slice:
- No direct callers were identified in the provided code observation. Typical usage in reporting or HTML-rendering pipelines is to post-process label strings that include counts in parentheses so the counts render visually as badges in generated HTML reports.

Why this logic is extracted into its own function:
- Responsibility boundary: isolates the formatting rule (pattern and HTML wrapper) from higher-level rendering code. This keeps the regex-based transformation in one place so templating/reporting code can apply it consistently to label strings without duplicating the pattern or HTML markup.

## Args:
    value (str): Input text that may contain zero or more occurrences of a parenthesized integer, e.g., "Label (12)". Must be a str (or a string-like object acceptable to re.sub). There is no special handling of None or non-string types in the implementation.

## Returns:
    str: A new string where every substring matching the regular expression \((\d+)\) has been replaced by <span class="badge">N</span> where N is the captured digits.
    - If there are no matches, the original string is returned unchanged.
    - Multiple matches are all replaced (global substitution).
    - Only contiguous decimal digits inside parentheses are matched; other parenthesized content (e.g., "(n/a)", "(1a)", or "(-1)") will not be replaced.

## Raises:
    - No explicit exceptions are raised by the function itself.
    - Underlying library behavior: re.sub will raise a TypeError if the provided value is None or if an incompatible non-string-like object is passed.

## Constraints:
Preconditions:
    - The caller should pass a string (str). The function assumes text input and does not perform HTML escaping.
    - The pattern only recognizes sequences of ASCII digits (0-9) inside a single pair of parentheses.

Postconditions:
    - The returned value is a str.
    - Any numeric sequences inside parentheses present in the input are replaced with equivalent <span class="badge">...</span> fragments; other content is preserved verbatim.

## Side Effects:
    - None. The function performs a pure transformation; it does not perform I/O, mutate global state, or call external services.
    - Note: The function does not HTML-escape the rest of the input. If the input may contain untrusted HTML, the caller must escape it before or after calling this function depending on the desired output encoding/templating approach.

## Control Flow:
flowchart TD
    Start --> CallReSub[Call re.sub with pattern \\((\\d+)\\) and replacement <span class="badge">\\1</span>]
    CallReSub --> CheckMatches{Matches found?}
    CheckMatches -- Yes --> ReturnReplaced[Return string with replacements]
    CheckMatches -- No --> ReturnOriginal[Return original string unchanged]
    ReturnReplaced --> End
    ReturnOriginal --> End

## Examples:
- Input: "Errors (4)"  
  Output: "Errors <span class=\"badge\">4</span>"

- Input: "Warnings (2) and Errors (10)"  
  Output: "Warnings <span class=\"badge\">2</span> and Errors <span class=\"badge\">10</span>"

- Input: "(123) Start"  
  Output: "<span class=\"badge\">123</span> Start"

- Input: "Counts (n/a) and (-1)"  
  Output: "Counts (n/a) and (-1)"  (no change because the contents are not exclusively digits)

- Input: "No counts here"  
  Output: "No counts here"  (returned unchanged)

Usage notes:
- If labels may include user-provided HTML or special characters, perform HTML-escaping at the appropriate point in the rendering pipeline; this function itself does not escape the input.

