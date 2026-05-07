# `describe_file_pandas.py`

## `src.ydata_profiling.model.pandas.describe_file_pandas.file_summary` · *function*

## Summary:
Retrieve filesystem metadata for each path in the given pandas Series and return a dictionary of pandas Series containing file size and formatted creation/access/modification timestamps.

## Description:
This function maps os.stat over each element of the input pandas Series (typed as pd.Series) to gather filesystem metadata, then extracts file size (st_size) and three timestamp fields (st_ctime, st_atime, st_mtime). Each timestamp is converted to a human-readable string using datetime.fromtimestamp with format "YYYY-MM-DD HH:MM:SS".

Known callers and typical context:
- Intended to be called by higher-level profiling code that processes DataFrame columns identified as containing file paths. It is used when the profiling pipeline needs per-path filesystem metadata for summarization or display.
- The function itself does not perform DataFrame-level aggregation or visualization; it only constructs the raw per-row metadata Series for downstream steps.

Reason for extraction:
- Encapsulates per-path os.stat calls and consistent timestamp formatting in one place so calling code can remain focused on composing summaries, handling missing values, or aggregating metadata. Centralization also makes it easy to change stat behavior (e.g., switch to lstat) or timestamp formatting later.

## Args:
    series (pd.Series):
        Series of path-like values (e.g., str or os.PathLike) where each element is a filesystem path accepted by os.stat.
        - Elements must be values accepted by os.stat; the function does no pre-validation or coercion.
        - The function will iterate over every element; for very large Series, callers should consider pre-filtering or batching.

## Returns:
    dict[str, pd.Series]:
        A dictionary with these keys (each value is a pd.Series aligned to the input Series index):
        - "file_size": pd.Series[int] — st_size from os.stat (file size in bytes).
        - "file_created_time": pd.Series[str] — st_ctime converted via datetime.fromtimestamp and formatted as "YYYY-MM-DD HH:MM:SS".
        - "file_accessed_time": pd.Series[str] — st_atime converted and formatted as above.
        - "file_modified_time": pd.Series[str] — st_mtime converted and formatted as above.

    Additional return notes:
        - For an empty input Series, each returned Series will be empty and preserve the input index.
        - The function preserves the input Series index for all returned Series.

## Raises:
    - Exceptions raised by os.stat for any element will propagate; the function does not catch them. These typically include:
        - FileNotFoundError: if a path does not exist.
        - PermissionError: if the process lacks permission to stat a path.
        - OSError: for other OS-level errors (I/O errors, too many symbolic links, etc.).
        - TypeError: if an element is of an incompatible type (e.g., None) and os.stat cannot accept it.
    Evidence: the implementation maps os.stat directly over series elements (no try/except), so any exception emitted by os.stat will surface to the caller.

## Constraints:
    Preconditions:
        - The caller should supply a pd.Series whose entries are valid path-like values acceptable to os.stat.
        - The process must have filesystem read permission for the given paths.
    Postconditions:
        - On successful completion, returns a dict of four pd.Series containing stat-derived values and timestamp strings formatted with local time using datetime.fromtimestamp("%Y-%m-%d %H:%M:%S").

## Side Effects:
    - Performs read-only filesystem metadata queries (os.stat) for each Series element. No files are opened for reading their contents, and no files or external state are modified.
    - No network I/O, no writes to disk, no logging, and no modification of global variables.

## Control Flow:
flowchart TD
    A[Input: series (pd.Series)] --> B{series empty?}
    B -- Yes --> C[Return dict of four empty pd.Series (preserve index)]
    B -- No --> D[stats = series.map(lambda x: os.stat(x))]
    D --> E{os.stat raises exception for any element?}
    E -- Yes --> F[Exception propagates to caller (FileNotFoundError/PermissionError/OSError/TypeError)]
    E -- No --> G[Build "file_size" = stats.map(lambda x: x.st_size)]
    G --> H[Build timestamps = stats.map(st_ctime/st_atime/st_mtime)]
    H --> I[Convert timestamps: datetime.fromtimestamp(...).strftime("YYYY-MM-DD HH:MM:SS")]
    I --> J[Assemble dict with four pd.Series]
    J --> K[Return dict]

## Examples:
Typical usage pattern (error handling and index preservation emphasized):
- Given a DataFrame df with a column paths containing filesystem paths:
    1. Select the Series: paths = df["paths"]
    2. Optionally drop or validate missing values before calling: paths_valid = paths.dropna()
    3. Call file_summary inside try/except to handle stat-related errors:
        - On success: the returned dict's Series can be assigned back to the DataFrame (they share the same index) or used by profiling code.
        - On FileNotFoundError or PermissionError: handle by logging, skipping affected rows, or notifying the user.
- Notes:
    - Because the function preserves the input index, assignment like df.loc[paths_valid.index, "file_size"] = summary["file_size"] is safe and aligns correctly.
    - For large numbers of paths, consider pre-filtering invalid entries or caching stat results to reduce repeated OS calls.

Implementation and performance hints:
- The implementation uses pandas.Series.map with per-element lambdas; this executes os.stat for each element in Python and is O(n) with OS calls per element — this can be the dominant cost for large Series.
- If symbolic link metadata is required instead of target metadata, replace os.stat with os.lstat upstream.
- Timestamp conversion uses datetime.fromtimestamp (local time). Use datetime.utcfromtimestamp or timezone-aware conversion if UTC or timezone-aware strings are required.

## `src.ydata_profiling.model.pandas.describe_file_pandas.pandas_describe_file_1d` · *function*

## Summary:
Runs file-path-specific profiling on a pandas Series: validates the Series, extracts per-path filesystem metadata, computes a histogram of file sizes, and updates the provided summary dictionary in-place. Returns the unchanged config and series along with the updated summary.

## Description:
This helper is invoked as part of the column-level profiling pipeline when a DataFrame column has been identified as containing file paths. Typical callers are the higher-level "describe" dispatchers that route a Series to a specialized 1-D describer based on inferred variable type (file-like columns). It is separated into its own function to encapsulate:
- validation of the incoming Series (no NaNs and availability of the .str accessor),
- coordination of two focused tasks (per-path filesystem metadata extraction and histogram computation),
- and the in-place update of the profiling summary dictionary so callers remain small and focused on dispatch/aggregation.

The function relies on two collaborators:
- file_summary(series): returns a dict of pd.Series with per-row file metadata (file_size and timestamp strings). This function performs os.stat on each path and may raise filesystem-related exceptions (FileNotFoundError, PermissionError, OSError, TypeError); these exceptions are not caught here and will propagate to the caller.
- histogram_compute(config, finite_values, n_unique, name=...): computes a histogram (via numpy) for the provided values and returns a dict mapping the provided name to the histogram result (a tuple (hist, bin_edges)).

By composing these two helpers here, the function enforces the responsibility boundary: validate inputs → enrich summary with raw metadata → add histogram statistics.

Known callers / context:
- Column-level profiling code that dispatches to a file-type describer during the dataset profiling pipeline (e.g., when the type-detection marks a column as file/path). It is intended to be called during the single-column description stage for file-path columns.

## Args:
    config (Settings):
        Global profiling configuration object. Used to obtain plotting/histogram settings by histogram_compute. Passed through unchanged and also used as an input to histogram computation.
    series (pd.Series):
        pandas Series containing path-like values (strings or os.PathLike).
        - Required: series.hasnans must be False (no NaNs).
        - Required: series must expose the .str accessor (i.e., typical pandas string-like Series).
        - Elements must be acceptable to os.stat (file_summary will call os.stat on each element).
        - The input Series index is preserved by downstream helpers and maintained in returned summary Series.
    summary (dict):
        Mutable dictionary passed in by the caller to accumulate summary statistics. This function updates it in-place with keys produced by file_summary and histogram_compute.

## Returns:
    Tuple[Settings, pd.Series, dict]:
        - config: The same Settings instance passed in (returned unchanged).
        - series: The same pandas Series passed in (returned unchanged).
        - summary: The same dict object passed in, after in-place updates. After successful return the summary will contain at least:
            - Keys produced by file_summary:
                - "file_size": pd.Series[int] aligned to series.index (st_size values in bytes)
                - "file_created_time": pd.Series[str] (formatted "YYYY-MM-DD HH:MM:SS")
                - "file_accessed_time": pd.Series[str]
                - "file_modified_time": pd.Series[str]
            - One key produced by histogram_compute:
                - "histogram_file_size": the histogram result produced by numpy.histogram (a tuple (hist, bin_edges) of numpy.ndarray)
        Note: The function returns the same summary object; callers can continue to use the returned dict or the original reference.

## Raises:
    ValueError:
        - If series.hasnans is True: raised with message "May not contain NaNs".
        - If the series does not expose a .str accessor: raised with message "series should have .str accessor".
    Exceptions propagated from file_summary:
        - FileNotFoundError: if any path in the series does not exist (raised by os.stat).
        - PermissionError: if the process lacks permission to stat a path.
        - OSError: for other OS-level errors from os.stat (I/O errors, too many symbolic links, etc.).
        - TypeError: if an element is of an incompatible type and os.stat cannot accept it.
    Exceptions propagated from histogram_compute/numpy:
        - Errors originating from numpy.histogram or related numpy utilities (e.g., ValueError, TypeError) may propagate if the file_size data is unsuitable for histogram computation.

## Constraints:
    Preconditions:
        - The caller must provide a pandas Series (pd.Series) whose elements are path-like values acceptable to os.stat.
        - The Series must not contain NaNs (series.hasnans must be False).
        - The Series must expose the .str accessor (typical of object-dtype string Series).
        - The process must have permission to call os.stat on the referenced paths.
    Postconditions:
        - On successful completion, the provided summary dict contains the file metadata Series ("file_size", "file_created_time", "file_accessed_time", "file_modified_time") and a histogram under "histogram_file_size".
        - The function returns the same config and series objects unchanged; it mutates the provided summary in-place.

## Side Effects:
    - Performs read-only filesystem metadata queries (os.stat) for each element in the input series via file_summary. These are OS-level stat calls and may be relatively expensive for large Series.
    - Updates the supplied summary dictionary in-place (mutable side-effect). No files are opened for reading their contents.
    - Calls into histogram_compute which performs CPU-bound numeric work (numpy) and may allocate arrays.
    - No network I/O, no external file writes, and no modification of global variables are performed by this function itself.

## Control Flow:
flowchart TD
    A[Start: call pandas_describe_file_1d(config, series, summary)] --> B{series.hasnans?}
    B -- Yes --> C[Raise ValueError "May not contain NaNs"]
    B -- No --> D{hasattr(series, "str")?}
    D -- No --> E[Raise ValueError "series should have .str accessor"]
    D -- Yes --> F[Call file_summary(series)]
    F --> G{file_summary raises?}
    G -- Yes --> H[Filesystem exception (FileNotFoundError/PermissionError/OSError/TypeError) propagates to caller]
    G -- No --> I[summary.update(file_summary_result)]
    I --> J[Compute n_unique = summary["file_size"].nunique()]
    J --> K[Call histogram_compute(config, summary["file_size"], n_unique, name="histogram_file_size")]
    K --> L{histogram_compute raises?}
    L -- Yes --> M[Histogram/numpy exception propagates to caller]
    L -- No --> N[summary.update(histogram_result)]
    N --> O[Return (config, series, summary)]

## Examples:
Typical usage pattern with error handling (descriptive steps):
1. Prepare inputs:
   - config: a Settings object used by histogram_compute.
   - series: pandas Series of file paths (no NaNs, .str accessor available).
   - summary: empty dict or existing summary dict to extend.

2. Call and handle errors:
   - Try to call pandas_describe_file_1d(config, series, summary).
   - Catch ValueError to handle precondition violations (NaNs or missing .str).
   - Catch FileNotFoundError / PermissionError / OSError / TypeError to handle problematic paths returned by os.stat.
   - Catch generic Exception from histogram_compute if the file_size data cannot be histogrammed.

3. After success:
   - Read per-row file metadata from summary["file_size"] and the timestamp Series.
   - Read histogram statistics from summary["histogram_file_size"] (a tuple (hist, bin_edges)) for plotting or further analysis.

Notes:
- For large Series, callers should consider pre-validating or filtering paths (e.g., dropping missing/invalid entries) or batching/stat-caching to avoid many OS calls.
- Because the function mutates the provided summary dict, pass a copy of the summary if the caller must retain the pre-call state.

