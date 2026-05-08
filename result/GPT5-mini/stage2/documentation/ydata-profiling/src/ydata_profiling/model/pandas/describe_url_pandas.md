# `describe_url_pandas.py`

## `src.ydata_profiling.model.pandas.describe_url_pandas.url_summary` · *function*

## Summary:
Produces counts of each URL component (scheme, network location, path, query, fragment) across a pandas Series of parsed URL objects and returns them in a dictionary.

## Description:
This function accepts a pandas Series whose elements expose URL component attributes (scheme, netloc, path, query, fragment) and computes value-counts for each component across the Series. Typical usage is after parsing raw URL strings into urllib.parse.SplitResult-like objects (for example using urlsplit) so that each element has the required attributes.

Known callers within the provided code snapshot:
- No direct callers were found in the scanned files. The module defines describe_url_1d (currently unimplemented) which is the logical higher-level consumer for URL summarization; url_summary is intended to be used by describe_url_1d or other profiling routines that summarize URL columns.

Reason for extraction:
- Separates the pure counting of URL components from higher-level summarization logic. This isolates a deterministic aggregation task (component-wise value_counts) so callers can pre-process inputs (parsing, cleaning) and handle richer metadata or configuration external to this function.

## Args:
    series (pandas.Series): A pandas Series whose elements are parsed URL objects exposing the attributes:
        - scheme (str)
        - netloc (str)
        - path (str)
        - query (str)
        - fragment (str)
    Notes:
        - The function expects the series elements to be objects similar to urllib.parse.SplitResult (i.e., the result of urlsplit) or any object providing the five attributes above.
        - Elements must be non-null and have the listed attributes; otherwise, attribute access will raise an exception.
        - The function does not accept raw URL strings; callers must parse them first (e.g., series.map(urlsplit)).

## Returns:
    dict: A dictionary with the following keys and pandas.Series values (each value is the result of pandas.Series.value_counts()):
        - "scheme_counts": counts of the scheme component (index: scheme strings; values: counts)
        - "netloc_counts": counts of the netloc (network location / host:port)
        - "path_counts": counts of the path component
        - "query_counts": counts of the query string component
        - "fragment_counts": counts of the fragment component
    Edge cases:
        - If the input series is empty, each returned pandas.Series will be empty.
        - Duplicate/missing components are handled naturally by value_counts (missing component values are treated as distinct keys if present; absent entries yield no key).
        - If some elements have empty strings for a component, those empty strings will be counted as a key in the corresponding counts Series.

## Raises:
    AttributeError: If any element in series does not have the required attribute(s) (e.g., an element is None, a float NaN, or a raw string). For example, accessing x.scheme on an element that lacks that attribute will raise an AttributeError.
    TypeError: If the provided `series` is not a pandas.Series (attempting to call series.map or series.value_counts will raise a TypeError or an AttributeError depending on the object).
    Note: The function does not perform explicit type-checking; these exceptions are raised by the underlying attribute access and pandas method calls.

## Constraints:
Preconditions:
    - The caller must pass a pandas.Series instance.
    - Each element of the series must be a parsed-URL object (e.g., urllib.parse.SplitResult) or an equivalent object exposing scheme, netloc, path, query, and fragment attributes.
    - Preferably ensure missing values are handled before calling (e.g., dropna()).

Postconditions:
    - Returns a dict with the five keys listed above, each mapping to a pandas.Series of counts (possibly empty).
    - The input series is not mutated.

## Side Effects:
    - None. The function performs pure in-memory computation using pandas operations and does not perform any I/O, global state mutation, or external service calls.

## Control Flow:
flowchart TD
    A[Start: receive pandas.Series] --> B{Elements have attributes?}
    B -- No --> E[AttributeError raised by attribute access]
    B -- Yes --> C[Compute scheme_counts: series.map(lambda x: x.scheme).value_counts()]
    C --> D[Compute netloc_counts: series.map(lambda x: x.netloc).value_counts()]
    D --> F[Compute path_counts: series.map(lambda x: x.path).value_counts()]
    F --> G[Compute query_counts: series.map(lambda x: x.query).value_counts()]
    G --> H[Compute fragment_counts: series.map(lambda x: x.fragment).value_counts()]
    H --> I[Package counts into dict and return]
    E --> I

## Examples (usage described as steps):
1. Start with a pandas Series of raw URL strings extracted from your data column.
2. Parse these strings into parsed-URL objects so each element has .scheme, .netloc, .path, .query, and .fragment attributes. Example step (conceptual): parsed_series = raw_series.map(urlsplit)
3. Optionally drop or handle missing values beforehand: parsed_series = parsed_series.dropna()
4. Call the function with the parsed series: result = url_summary(parsed_series)
5. Inspect counts per component:
   - result["scheme_counts"] gives a pandas.Series mapping scheme strings (e.g., "http", "https") to their frequencies.
   - result["netloc_counts"] gives frequencies for hosts/hosts:ports.
6. Error handling: wrap the call in try/except to catch AttributeError if the input series contains elements that are None or not parsed URL objects; or ensure pre-processing (parsing + dropna) avoids these errors.

## Implementation notes for re-implementation:
- Use pandas.Series.map with a lambda that accesses the appropriate attribute on each element, then call pandas.Series.value_counts() to aggregate frequencies.
- Keep the function side-effect free: do not modify the input series in place.
- Maintain the exact dict keys ("scheme_counts", "netloc_counts", "path_counts", "query_counts", "fragment_counts") so downstream consumers expect a consistent schema.

## `src.ydata_profiling.model.pandas.describe_url_pandas.pandas_describe_url_1d` · *function*

## Summary:
Parses a pandas Series of URL strings into urllib.parse.SplitResult objects, aggregates URL-component counts into the provided summary dict, and returns the updated config, parsed series, and summary.

## Description:
- Known callers and context:
    - Intended as a pandas-specific helper for higher-level URL summarization routines (the module-level describe_url_1d is the logical consumer). No direct callers were found in the scanned snapshot; this function is designed to be invoked when profiling a column of URL strings during the "describe 1D" pipeline stage.
    - Typical trigger: called when a column's data type has been identified as URL-like and the profiling pipeline needs component-wise statistics (scheme, netloc, path, query, fragment).

- Responsibility and reason for extraction:
    - Encapsulates pandas-centric preprocessing (validation and parsing of string values using urlsplit) and the link to url_summary which computes component counts.
    - Keeps parsing and pandas-specific checks separate from the pure aggregation logic (url_summary), improving testability and reusability.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: profiling configuration object passed through the pipeline; this function does not modify it.
    series (pandas.Series):
        - Type: pandas.Series of raw URL-like values (typically Python str for each element).
        - Requirement: must be a pandas.Series instance, must have the pandas string accessor (.str), and must not contain NaN values (series.hasnans must be False).
        - Notes: elements should be string-like values acceptable to urllib.parse.urlsplit; otherwise urlsplit will raise an error when applied.
    summary (dict):
        - Type: dict
        - Role: a mutable mapping used to accumulate summary information across profiling steps. This function will update this dict in-place with URL component counts.

## Returns:
    Tuple[Settings, pandas.Series, dict]
    - The function returns a 3-tuple of:
        1. config: the same Settings object passed in (unchanged).
        2. series: a new pandas.Series whose elements are the results of urllib.parse.urlsplit applied to each input element (i.e., SplitResult-like objects exposing .scheme, .netloc, .path, .query, .fragment).
        3. summary: the same dict object passed in, updated in-place with the results of url_summary(parsed_series). The update uses dict.update(...), so existing keys in summary may be overwritten if url_summary returns identical keys.

    - Possible return variations / edge cases:
        - If the input series is empty (len == 0), the returned parsed series will also be empty and url_summary will return empty counts; summary will be updated with empty count Series for each component.
        - The function never returns None; it always returns a 3-tuple on successful completion.

## Raises:
    ValueError:
        - If series.hasnans is True:
            - Raised with exact message "May not contain NaNs"
            - Condition in code: first if-check.
        - If the passed series object lacks a pandas string accessor:
            - Raised with exact message "series should have .str accessor"
            - Condition in code: second if-check using hasattr(series, "str")
    Exceptions propagated from downstream operations:
        - Any exception raised by urllib.parse.urlsplit when called on an element (e.g., TypeError if an element is not string-like) will propagate.
        - Any exception raised by url_summary (for example AttributeError if parsed elements lack expected attributes) will propagate.

## Constraints:
- Preconditions:
    - Caller must pass a pandas.Series instance as the series parameter.
    - series.hasnans must be False (no NaN or missing values present).
    - series must support .str accessor (i.e., be string-like at the Series level).
    - Elements should be valid inputs for urllib.parse.urlsplit (typically str).
    - summary must be a mutable mapping (dict) passed by reference.

- Postconditions:
    - The returned series is a pandas.Series of urllib.parse.SplitResult-like objects (result of urlsplit).
    - The summary dict will contain (or be updated with) the URL component counts produced by url_summary; keys from url_summary will be merged into the provided summary dict.
    - The original Series object passed as argument is not mutated in place; a new Series (the return value) contains the parsed results.
    - The config object is returned unchanged.

## Side Effects:
- Mutates the provided summary dict in-place via summary.update(...).
- No I/O is performed (no file, network, or stdout/stderr operations).
- No global state mutation, no external service calls.

## Control Flow:
flowchart TD
    Start[Start] --> CheckNaN{series.hasnans?}
    CheckNaN -- True --> RaiseNaN[Raise ValueError("May not contain NaNs")]
    CheckNaN -- False --> CheckStr{hasattr(series,"str")?}
    CheckStr -- False --> RaiseStr[Raise ValueError("series should have .str accessor")]
    CheckStr -- True --> ApplySplit[series = series.apply(urlsplit)]
    ApplySplit --> UrlSummary[call url_summary(parsed_series)]
    UrlSummary --> UpdateSummary[summary.update(url_summary_result)]
    UpdateSummary --> Return[return config, parsed_series, summary]

## Examples:
- Happy path:
    - Given:
        - config = Settings()
        - raw_series = pandas.Series(["https://example.com/path?a=1#f", "http://host.test/"])
        - summary = {}
    - Call:
        - config, parsed_series, summary = pandas_describe_url_1d(config, raw_series, summary)
    - Effect:
        - parsed_series[0] is a SplitResult for "https://example.com/path?a=1#f"
        - summary will be updated with keys produced by url_summary (e.g., "scheme_counts", "netloc_counts", ...), each mapped to a pandas.Series of counts.

- Handling NaNs (error example):
    - Given:
        - raw_series = pandas.Series(["http://a", None])
        - raw_series.hasnans == True
        - summary = {}
    - Call:
        - pandas_describe_url_1d(config, raw_series, summary)
    - Outcome:
        - Raises ValueError("May not contain NaNs")

- Defensive usage with try/except:
    - Wrap the call to catch both explicit input validation errors and propagated parsing errors:
        - try:
            config, parsed_series, summary = pandas_describe_url_1d(config, raw_series, summary)
          except ValueError as e:
            handle_validation_error(e)
          except Exception as e:
            handle_parsing_or_summary_error(e)

Notes:
- This function is a thin, pandas-oriented preprocessing wrapper: it performs strict input validation (no NaNs, requires .str), parses each string with urllib.parse.urlsplit, delegates aggregation to url_summary, and updates the provided summary mapping in-place.

