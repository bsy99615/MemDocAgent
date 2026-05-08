# `local_directory_record_source.py`

## `trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource` · *class*

## Summary:
Loads CloudTrail-derived Record objects from a local filesystem directory by discovering log files, filtering out invalid filenames, and aggregating records from files whose timestamps overlap a requested timeframe.

## Description:
LocalDirectoryRecordSource is a thin directory-backed record source used when CloudTrail delivery files are stored on the local filesystem. Instantiate this class when you need to scan a directory tree for CloudTrail-style .json.gz files, filter files by filename-derived timestamps, and aggregate event records from matching files.

Typical scenarios:
- Batch ingestion pipelines that need to collect records between two datetimes from a directory of CloudTrail delivery files.
- One-off analysis where log files have been copied to a local folder and records must be read and parsed by the existing LogFile/parse_records pipeline.

This class intentionally delegates file-level parsing and timestamp logic to trailscraper.cloudtrail.LogFile; LocalDirectoryRecordSource is responsible only for directory traversal, filename-based filtering (via LogFile.has_valid_filename() used internally), and flattening of per-file record lists into a single list for callers.

Known callers:
- Any higher-level orchestration code or ingestion pipeline that wants a simple API to "load records between from_date and to_date from a local directory".

Responsibility boundary:
- Does not open or parse file contents itself; it creates LogFile instances and calls their methods (contains_events_for_timeframe, records).
- Does not persist state beyond the configured directory path.
- Does not swallow parsing exceptions from LogFile.records(); such errors propagate up to callers.

## State:
- _log_dir (str)
    - Description: Root filesystem directory path to search for log files.
    - Expected values: Valid filesystem path string (absolute or relative).
    - Constraints: Not validated at construction time; if the path does not exist or is unreadable, directory traversal (os.walk) will raise and that exception will propagate when methods that iterate files are called.
- Class invariants:
    - _log_dir is immutable after construction (no methods modify it).
    - Methods assume LogFile implements filename parsing and record-loading behaviors described in trailscraper.cloudtrail.LogFile; callers should understand that LogFile may raise parsing or I/O exceptions which LocalDirectoryRecordSource does not catch in most cases.
    - _valid_log_files() yields only LogFile instances for which LogFile.has_valid_filename() returned truthy; invalid filenames are skipped and a warning is logged.

## Lifecycle:
- Creation:
    - Instantiate with LocalDirectoryRecordSource(log_dir).
    - Required argument:
        - log_dir (str): path to the directory root containing CloudTrail delivery files.
- Usage (typical method sequence):
    1. Call load_from_dir(from_date, to_date) to collect all Record objects whose source file timestamp overlaps [from_date, to_date].
       - This internally iterates files via _valid_log_files(), uses each LogFile.contains_events_for_timeframe(from_date, to_date) to decide inclusion, and extends a result list with LogFile.records() results.
    2. Optionally call last_event_timestamp_in_dir() to obtain the timestamp of the most recent event found in the directory.
       - This method finds the latest LogFile by filename-derived timestamp, loads its records, then finds the record with the largest event_time and returns that event_time.
- Sequencing constraints:
    - No special ordering of public method calls is required, but both public methods depend on the presence of readable files under log_dir and correct LogFile behavior.
- Destruction / cleanup:
    - No explicit cleanup is required. There are no open persistent file handles kept by this class. Any open/close semantics are handled by LogFile.records().

## Methods (behavior summary - for reimplementation)
- _valid_log_files() -> iterable[LogFile]
    - Traverses the filesystem tree rooted at self._log_dir using os.walk.
    - For each file path discovered, constructs a LogFile(path).
    - Calls LogFile.has_valid_filename() and:
        - yields the LogFile instance if filename is valid (truthy match).
        - otherwise logs a warning "Invalid filename: <basename>" and excludes the file.
    - Returns a lazy iterable/iterator of LogFile instances (the implementation uses toolz.pipe/mapcat/map/filter semantics).
    - Exceptions that may propagate:
        - FileNotFoundError / OSError if os.walk cannot access the root path.
        - Any exception raised by LogFile.__init__ or LogFile.has_valid_filename() (though LogFile.has_valid_filename() is expected not to raise).
- load_from_dir(from_date, to_date) -> list[Record]
    - Parameters:
        - from_date (datetime.datetime): start of timeframe (inclusive). Prefer timezone-aware UTC datetimes to avoid comparison errors.
        - to_date (datetime.datetime): end of timeframe (inclusive). Prefer timezone-aware UTC datetimes.
    - Behavior:
        - Iterates LogFile instances from _valid_log_files().
        - For each LogFile, calls contains_events_for_timeframe(from_date, to_date).
        - If True, calls LogFile.records() and extends the result list with the returned list of Record objects.
        - Returns a flat list containing all Record objects collected from matching files (in directory traversal order).
    - Edge cases:
        - If no files match, returns an empty list.
        - If LogFile.records() raises (e.g., JSONDecodeError, parse errors), that exception propagates to the caller.
        - If from_date/to_date are not comparable to the LogFile timestamp (e.g., naive vs aware datetime mismatch), a TypeError may propagate from LogFile.contains_events_for_timeframe().
- last_event_timestamp_in_dir() -> datetime.datetime
    - Behavior:
        - Sorts LogFile instances from _valid_log_files() by LogFile.timestamp and selects the last (most recent) file.
        - Loads records from that LogFile and sorts them by record.event_time, selects the last (most recent) record, and returns record.event_time.
    - Edge cases and exceptions:
        - If there are no valid files under log_dir, the underlying "last" operation will raise (propagated exception from the toolz last/iteration).
        - If the chosen LogFile has no records, selecting the last record will raise similarly.
        - Any exceptions from LogFile.timestamp() or LogFile.records() (IndexError, ValueError, JSONDecodeError, parse errors) are propagated.
        - Caller should be prepared to catch exceptions indicating no data found or malformed filenames/records.

## Method Map:
flowchart TD
    A[LocalDirectoryRecordSource(log_dir)] --> B[_valid_log_files()]
    B --> |yields paths| C[LogFile(path) instances]
    C --> |filter| D[LogFile.has_valid_filename() -> warn & skip invalid]
    E[load_from_dir(from_date,to_date)] --> B
    E --> |for each file| F[LogFile.contains_events_for_timeframe(from_date,to_date)]
    F --> |True| G[LogFile.records() -> list[Record] -> extend results]
    H[last_event_timestamp_in_dir()] --> B
    H --> |sorted by| I[LogFile.timestamp()]
    I --> |last file| J[LogFile.records() -> sort by record.event_time -> last -> return event_time]

## Raises:
- __init__(log_dir)
    - The constructor itself does not explicitly raise. However, passing a non-string or inappropriate type may cause subsequent method calls to raise TypeError when os.walk is invoked.
- _valid_log_files()
    - FileNotFoundError, OSError: if the underlying os.walk cannot access or find the configured directory root.
    - Any exception thrown by LogFile construction or its methods (propagated).
- load_from_dir(from_date, to_date)
    - Propagates exceptions from:
        - _valid_log_files() (FileNotFoundError/OSError)
        - LogFile.contains_events_for_timeframe(from_date, to_date) (IndexError/ValueError from timestamp parsing, TypeError for datetime comparisons)
        - LogFile.records() (IOError/OSError when opening a file may be caught by LogFile and return [], but JSONDecodeError or parse-related exceptions from parse_records will propagate)
- last_event_timestamp_in_dir()
    - Raises/propagates exceptions when directory contains no valid log files or no records (the "last" call will raise from the iterator/sequence operations).
    - Also propagates exceptions from LogFile.timestamp(), LogFile.records(), and record parsing (IndexError, ValueError, JSONDecodeError, etc.)

## Example:
1) Basic usage - collect records in a timeframe
    from datetime import datetime, timezone
    src = LocalDirectoryRecordSource("/var/log/cloudtrail")
    from_dt = datetime(2021, 6, 1, 0, 0, tzinfo=timezone.utc)
    to_dt   = datetime(2021, 6, 1, 23, 59, tzinfo=timezone.utc)
    try:
        records = src.load_from_dir(from_dt, to_dt)
        # process records (list of Record objects returned by LogFile.records())
    except FileNotFoundError:
        # handle missing directory
    except Exception as e:
        # handle parsing or I/O errors propagated from LogFile

2) Get most recent event timestamp (defensive)
    try:
        last_ts = src.last_event_timestamp_in_dir()
    except Exception:
        # no valid files or records, or parsing error; handle accordingly

Notes:
- For predictable behavior, ensure callers supply timezone-aware datetimes (UTC) for from_date and to_date; LogFile.timestamp() returns a UTC datetime and comparisons between naive and aware datetimes will raise TypeError.
- This class is intentionally small and delegates filename parsing and record loading to LogFile; consult trailscraper.cloudtrail.LogFile docs for the exact semantics of filename validation, timestamp parsing, and record parsing.

### `trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource.__init__` · *method*

## Summary:
Stores the provided directory path on the instance so the record-source can later traverse that filesystem root.

## Description:
This is the class constructor invoked when creating a LocalDirectoryRecordSource instance (e.g., LocalDirectoryRecordSource("/path/to/logs")). Typical callers are higher-level orchestration or ingestion code that instantiate the source during pipeline setup or when performing an on-demand scan of a local directory for CloudTrail-derived log files. The constructor is executed at the object-creation stage of the lifecycle.

This logic exists in the constructor because the class must retain the configured directory root as instance state for use by other methods (such as _valid_log_files, load_from_dir, and last_event_timestamp_in_dir). There is no additional initialization work required here — responsibility for file parsing, validation, and I/O is delegated to LogFile and the instance methods that traverse the directory.

## Args:
    log_dir (str):
        Root filesystem directory path to search for CloudTrail delivery files.
        - Expected type: str (absolute or relative path).
        - Valid values: any string representing a filesystem path. The constructor does not validate existence or readability.
        - Default: required positional argument (no default).

## Returns:
    None

## Raises:
    None explicitly.
    - The constructor performs a simple assignment and does not raise exceptions itself.
    - Note: if callers pass a non-path object (e.g., None or a non-string), later methods that call os.walk or otherwise treat _log_dir as a filesystem path may raise TypeError, FileNotFoundError, or OSError when those methods are invoked.

## State Changes:
    Attributes READ:
        - None

    Attributes WRITTEN:
        - self._log_dir: set to the provided log_dir argument

## Constraints:
    Preconditions:
        - No runtime checks are performed here. Callers are expected to supply a string-like filesystem path.
        - For predictable behavior of other methods, supplying a readable directory path (and preferably a string) is recommended.

    Postconditions:
        - After construction, self._log_dir is equal to the provided log_dir value.
        - The instance holds no other persistent resources (no open file descriptors, no network calls).

## Side Effects:
    - No I/O is performed.
    - No external services are contacted.
    - The only mutation is the assignment of the given value to the instance attribute self._log_dir.

### `trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource._valid_log_files` · *method*

## Summary:
Returns a lazy iterable of LogFile objects for every file path under the configured directory that appears to be a CloudTrail log file; invalid filenames are skipped and a warning is logged for each.

## Description:
Known callers:
- LocalDirectoryRecordSource.load_from_dir — iterates the returned sequence to select files whose events fall within a given timeframe and then loads records from each.
- LocalDirectoryRecordSource.last_event_timestamp_in_dir — consumes the returned sequence to find the most-recent file by timestamp.

Lifecycle/context:
- This method is invoked during directory-scanning phases of the pipeline where the system must discover candidate CloudTrail log files on local disk before opening them.
- It is intentionally separated into its own method to encapsulate the file-discovery + filename-validation steps (so callers get a single reusable iterable of already-wrapped LogFile objects), to keep scanning logic testable and to avoid duplicating path->LogFile conversion and filename-warn behavior across call sites.

## Args:
- None

## Returns:
- Iterable[LogFile]
    - A lazy iterable (iterator/generator-like) that yields trailscraper.cloudtrail.LogFile instances.
    - Each yielded LogFile was constructed from a full filesystem path discovered under self._log_dir.
    - Only LogFile instances for which LogFile.has_valid_filename() is truthy are yielded; files with invalid filenames are excluded.
    - The iterable is lazy: filesystem traversal (os.walk), path joining, LogFile construction, and filename validation occur as the iterable is consumed, not at the moment _valid_log_files() is called.
    - Edge-case returns:
        - If the directory tree contains no files (or os.walk yields no entries), the returned iterable yields no elements.
        - If every discovered filename is invalid, the iterable yields no elements (but warnings are logged for each invalid filename).

## Raises:
- None directly from this method in normal operation.
    - Indirect exceptions are possible only if a component used during iteration raises (for example, if a customized LogFile constructor raised); with the provided LogFile implementation, construction does not perform I/O and therefore will not raise for ordinary path strings.
    - Any exceptions that occur while consuming the returned iterable (e.g., from downstream operations on LogFile objects) will propagate to the consumer at iteration time.

## State Changes:
- Attributes READ:
    - self._log_dir — used as the root path argument to os.walk.
- Attributes WRITTEN:
    - None — this method does not modify self or external mutable state.

## Constraints:
- Preconditions:
    - self._log_dir must be set to a filesystem path (string). Preferably this is an existing directory path; if it does not exist, os.walk will simply produce no results and the returned iterable will be empty.
    - Callers must be prepared to treat the result as an iterable that may be empty.
- Postconditions:
    - Iterating the returned value will yield zero or more LogFile objects whose LogFile.has_valid_filename() returned truthy at the time of iteration.
    - For each encountered file with an invalid filename, a logging.warning was emitted with the basename of the file.

## Side Effects:
- I/O:
    - Uses os.walk(self._log_dir) to list directories and files under the given root — this performs filesystem directory reads when the iterable is consumed.
- Logging:
    - Calls logging.warning("Invalid filename: %s", log_file.filename()) for every discovered file whose LogFile.has_valid_filename() is falsy.
- Object construction:
    - Constructs LogFile(path) objects during iteration. With the documented LogFile implementation, construction is cheap and does not open files.
- No network calls, no file content reads, and no persistent mutations of objects outside self occur in this method.

## Implementation notes (behavioral recipe):
- For each triple produced by os.walk(self._log_dir) (root, dirs, files):
    - Convert the list of filenames into full paths using os.path.join(root, filename).
    - Wrap each path with LogFile(path) to get a LogFile instance.
    - Call LogFile.has_valid_filename() and:
        - If truthy, yield the LogFile instance.
        - Otherwise, emit logging.warning("Invalid filename: %s", log_file.filename()) and skip yielding that LogFile.
- Ensure the pipeline is lazy so that filesystem traversal and validation happen on consumption rather than at call time.

### `trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource.load_from_dir` · *method*

## Summary:
Collects and returns all parsed Record objects from log files discovered in the source directory whose filename-derived timestamps fall within the supplied date range; the method does not mutate the LocalDirectoryRecordSource instance.

## Description:
- Known callers / invocation context:
    - Typical callers are higher-level ingestion or processing pipelines that need to load CloudTrail events from a local directory for a given timeframe (for example: "load all events between from_date and to_date for downstream parsing/analysis").
    - This method is invoked during the discovery/collection stage of a pipeline that enumerates log files, selects those relevant to the requested window, and aggregates their parsed events.
- Why this is its own method:
    - The logic encapsulates directory traversal, per-file selection by filename-derived timestamp, and aggregation of parsed records into a single result list. Extracting this as a dedicated method keeps higher-level pipelines simple and centralizes the time-window selection and file-reading behavior.

## Args:
    from_date (datetime.datetime):
        - Lower bound (inclusive) of the timeframe used to decide whether to include a file.
        - Should be comparable to filename-derived timestamps (preferably timezone-aware UTC datetimes). If not comparable, Python may raise TypeError during comparisons.
    to_date (datetime.datetime):
        - Upper bound of the timeframe. The method includes files whose filename-derived timestamp is <= to_date + 1 hour (the +1 hour policy comes from LogFile.contains_events_for_timeframe).
        - Should be comparable to filename-derived timestamps (preferably timezone-aware UTC datetimes).

## Returns:
    list[Record]:
        - A flat list containing the concatenation (in discovery order) of the lists returned by logfile.records() for each LogFile whose contains_events_for_timeframe(from_date, to_date) returned True.
        - Possible values:
            - Non-empty list[Record] when at least one selected file contained parsed records.
            - Empty list when no files matched the timeframe, when matched files contained zero records, or when there are no readable files (note: LogFile.records() returns [] on I/O errors).
        - Note: The method does not further filter records by event timestamps — selection is based on the filename-derived timestamp only, so individual returned records may lie outside the from_date/to_date window.

## Raises:
    - Any exception propagated by LogFile.contains_events_for_timeframe(from_date, to_date), including:
        - IndexError or ValueError from LogFile.timestamp() if a filename is malformed.
        - TypeError when comparing timezone-naive and timezone-aware datetimes (if caller supplies incompatible date objects).
    - Any exception propagated by LogFile.records(), including (but not limited to):
        - json.JSONDecodeError if a selected file contains invalid JSON.
        - KeyError if the JSON does not include the top-level 'Records' key.
        - Exceptions raised by parse_records() when individual records are malformed (these propagate).
    - Notes on non-propagated conditions:
        - IOError / OSError encountered when opening/reading a file are handled inside LogFile.records(): such errors are logged and that file contributes an empty list (no exception surfaces from records() for these I/O errors).

## State Changes:
- Attributes READ:
    - self._log_dir (indirectly) — accessed by self._valid_log_files(), which traverses the directory tree to discover file paths.
    - Any transient values computed by self._valid_log_files() and by each LogFile instance (e.g., filename parsing).
- Attributes WRITTEN:
    - None — this method does not assign to or mutate attributes on self.

## Constraints:
- Preconditions:
    - self must have been constructed with a valid _log_dir attribute (a filesystem path string). If the directory does not exist, os.walk yields no files and the method returns an empty list.
    - from_date and to_date should be datetime objects comparable with LogFile.timestamp() (LogFile.timestamp() returns a tz-aware UTC datetime; prefer supplying tz-aware UTC datetimes to avoid TypeError).
    - Callers should be prepared to handle exceptions that propagate from LogFile.timestamp()/records() (see Raises).
- Postconditions:
    - The returned list contains the concatenated parsed Record objects from every LogFile in the directory that passed the filename-timestamp window test implemented by contains_events_for_timeframe.
    - The LocalDirectoryRecordSource instance remains unchanged.

## Side Effects:
    - File I/O: Calls to LogFile.records() open and read gzip-compressed JSON files from disk; this performs actual filesystem reads.
    - Logging:
        - _valid_log_files() may emit warnings for invalid filenames (when has_valid_filename() is False).
        - LogFile.records() may log a warning and return [] when I/O errors occur while opening/reading a file.
    - Exceptions from JSON decoding or record parsing (json.JSONDecodeError, parse_records exceptions) may be raised and propagate out of this method.
    - No network calls or external service interactions are performed by this method directly; all side effects are local (filesystem and logging).

### `trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource.last_event_timestamp_in_dir` · *method*

*No documentation generated.*

