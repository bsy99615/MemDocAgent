# `download_history.py`

## `onlinejudge_command.download_history.DownloadHistory` · *class*

*No documentation generated.*

### `onlinejudge_command.download_history.DownloadHistory.__init__` · *method*

## Summary:
Initializes the DownloadHistory instance by storing the path to the download-history JSONL file on the instance.

## Description:
This constructor establishes the persistent file path that the instance will use to read or append download-history records. It is called when a DownloadHistory object is created (i.e., when the class is instantiated) — typically at the start of a workflow that needs to record or query past downloads. No heavy logic is performed here so that path resolution and assignment are centralized and easy to test or override.

Known callers and lifecycle context:
- No specific callers are present in the provided code context. Typical usage is:
  - Higher-level commands or services instantiate DownloadHistory during CLI or program startup before performing download or history operations.
  - The instance is then passed to or used by methods that read/write history records.

Why this is a separate method:
- Keeps object construction trivial and focused (single responsibility): configure the file location once.
- Allows callers to override the default path easily (for testing, debugging, or custom storage locations) without modifying other logic.

## Args:
    path (pathlib.Path): Filesystem path where the download-history is stored.
        - Default: utils.user_cache_dir / 'download-history.jsonl'
        - Expected type: pathlib.Path (callers often pass a Path; the method does not enforce types at runtime)
        - Notes on default: the default expression (utils.user_cache_dir / 'download-history.jsonl') is evaluated at function definition (module import) time, so it depends on the module-level name `utils` resolving correctly and on utils.user_cache_dir being set then.

## Returns:
    None: This initializer does not return a value. It sets instance state (self.path).

## Raises:
    - The method body itself does not explicitly raise exceptions.
    - Possible exceptions that can surface:
        - NameError or AttributeError at import time if the module-level `utils` name or its attribute `user_cache_dir` is missing; this arises from evaluating the default argument expression and is not raised by the assignment in the constructor call.
        - Any exception raised by callers when passing an invalid object as path (e.g., operations that later assume pathlib.Path might fail elsewhere), but this constructor does not validate the value.

## State Changes:
    Attributes READ:
        - None explicitly read by the constructor body.
        - Note: the default value expression may read module-level utils.user_cache_dir at import time (see Args/Constraints).

    Attributes WRITTEN:
        - self.path is assigned to the provided path argument (or the default path).

## Constraints:
    Preconditions:
        - If relying on the default, the module-level name `utils` must be defined and have attribute `user_cache_dir` at import time.
        - Callers should supply a pathlib.Path (or an object compatible with subsequent usage) for predictable behavior.

    Postconditions:
        - After __init__ returns, self.path exists as an attribute referencing the provided value.
        - No file I/O is performed by the constructor; it does not create or validate the file at self.path.

## Side Effects:
    - Mutates the newly-created object by setting self.path.
    - No I/O, logging, or external service calls are performed by this method.

### `onlinejudge_command.download_history.DownloadHistory.add` · *method*

## Summary:
Append a single JSON-formatted history entry (timestamp, directory, url) as a new line to the on-disk history file and then run maintenance to limit the file size; this mutates the filesystem file at self.path but does not change other in-memory attributes.

## Description:
- Known callers and invocation context:
    - The repository scan did not reveal explicit call sites for this method in the provided snapshot. Conceptually, this method is intended to be called by components that perform a problem download or export operation immediately after writing files to disk — i.e., the download pipeline that wants to persist a record of which URL was saved into which directory.
    - Typical lifecycle stage: invoked right after a successful download/save of problem files to record the event into a persistent, append-only history file.

- Why this is a separate method:
    - Appending a history entry and the related filesystem maintenance (ensuring parent directories exist, appending a newline-delimited JSON record, then possibly truncating/halving the file) are distinct concerns from the code that performs downloads. Isolating this logic keeps the download implementation focused on I/O of problem files and centralizes history-format and file-size policy in one place for easier maintenance and testing.

## Args:
    problem (onlinejudge.type.Problem): A Problem object. The method calls problem.get_url() and stores that value under the 'url' key in the written JSON. The object must implement get_url() and that call may raise exceptions if the Problem is in an invalid state.
    directory (pathlib.Path, keyword-only): The directory where the problem was downloaded (recorded by converting to str(directory) in the JSON). It must be a path-like object; the method does not validate that the directory exists beyond converting it to a string.

## Returns:
    None

## Raises:
    - Any exception raised by problem.get_url() will propagate (e.g., if get_url() raises a ValueError or other user-defined error).
    - PermissionError, OSError, FileNotFoundError and other I/O-related exceptions from mkdir(), open(), write(), or other filesystem operations may propagate. Note: parent directories are created with mkdir(parents=True, exist_ok=True), which reduces some FileNotFoundError scenarios, but permission and other I/O errors can still occur.
    - JSON-related errors are unlikely because the method constructs a simple dict of primitive types; however, if problem.get_url() returns a non-serializable object, json.dumps(...) could raise a TypeError.

## State Changes:
Attributes READ:
    - self.path: used to determine the file location, to create the parent directory, to open the file for appending, and passed to self._flush().

Attributes WRITTEN:
    - None of the object's in-memory attributes are reassigned by this method.

Filesystem state written:
    - The file at self.path is opened in append mode and a new line is appended. The appended line is a JSON object with keys 'timestamp', 'directory', and 'url', followed by a newline character.
    - The subsequent call to self._flush() may further modify (truncate/overwrite) the file at self.path depending on file size (see Side Effects and constraints).

## Constraints:
Preconditions:
    - self.path must be a valid pathlib.Path object. The code assumes self.path.parent is creatable/writable when calling mkdir(parents=True, exist_ok=True).
    - problem.get_url() should return a value that is JSON-serializable (commonly a string). If it returns a non-serializable object, json.dumps will fail.
    - directory must be convertible to a string (pathlib.Path is standard).

Postconditions:
    - After successful return, the history file at self.path contains at least one new line appended at its end representing the record:
        {
            "timestamp": <int seconds since epoch>,
            "directory": "<directory as str>",
            "url": "<value returned by problem.get_url()>"
        }
      followed by a newline character.
    - The parent directory of self.path exists (created if necessary).
    - self._flush() has been invoked and may have truncated the file if the configured size threshold is exceeded (the truncation semantics are defined by DownloadHistory._flush()).

## Side Effects:
    - Disk I/O: creates parent directories if missing, opens/creates the history file in append mode, writes one line (the JSON record + newline), and then delegates to self._flush() which may read and rewrite the file to enforce size limits.
    - Logging: emits an info-level log entry via the module logger indicating the append operation and the path (the method calls logger.info('append the downloading history: %s', self.path)).
    - Concurrency: the append + _flush operations are not atomic with respect to other processes; concurrent writers/readers may observe interleaved or lost updates. If concurrent access is possible, callers should serialize access (e.g., via a file lock) before invoking add().
    - No network calls are performed by this method itself. Any network-related effects would come from code that invoked problem.get_url(), if that call triggers network I/O (not expected in normal Problem implementations).

## Implementation details necessary for reimplementation:
    - Create parent directories with self.path.parent.mkdir(parents=True, exist_ok=True) before attempting to open the file.
    - Open the file at self.path in text append mode ('a') and write a single line consisting of json.dumps({...}) + '\n'. The JSON object must include:
        - 'timestamp': int(time.time())  (seconds since the Unix epoch, cast to int)
        - 'directory': str(directory)
        - 'url': problem.get_url()
    - After writing, call self._flush() to allow the class to enforce its on-disk size policy (see DownloadHistory._flush for truncation behavior).
    - Do not swallow exceptions raised during directory creation, file open/write, json.dumps, or the called methods; let them propagate to the caller.

### `onlinejudge_command.download_history.DownloadHistory.remove` · *method*

## Summary:
Remove all JSONL history entries that record downloads for the given directory by rewriting the history file so that only entries whose stored "directory" differs from the provided directory remain. This mutates the on-disk history file but does not change DownloadHistory attributes.

## Description:
This method implements the "delete all history entries for a given directory" step of the download-history lifecycle. It is a standalone operation because it requires reading the entire JSONL history, filtering entries, and rewriting the file — logic that is reused independently of add/get/_flush and that must be centralized to avoid duplication.

Known callers and context:
- There are no callers inside this class. Callers are external components of the download workflow that need to clear recorded download history for a specific local directory (for example, when a directory is removed, reset, or the user requests history clearing).
- Typical usage occurs after download artifacts for a directory are removed or when resetting state for that directory.

Why this is its own method:
- The method encapsulates file-level read/filter/write logic for the JSON Lines history file (JSONL). Centralizing the behavior avoids duplicating file handling and ensures consistent semantics across different code paths that need to clear history for a directory.

## Args:
    directory (pathlib.Path): The directory to remove from the history. Must be a pathlib.Path instance (the method is called using a keyword-only argument).

## Returns:
    None

## Raises:
    - OSError (or subclass, e.g., FileNotFoundError, PermissionError): If opening, reading, or writing the history file fails (file IO errors). Note: the method checks existence first and returns early if self.path does not exist, but IO errors can still occur when opening/reading/writing.
    - json.decoder.JSONDecodeError: If a history line is not valid JSON. This will be raised during filtering and will propagate out of the method (the file has already been opened for writing and therefore is truncated before this decoding happens — see Side Effects/Constraints).
    - KeyError: If a JSON-decoded line does not contain the 'directory' key. This will also propagate and can occur while evaluating the filter.
    - TypeError or ValueError: May be raised during conversion pathlib.Path(json_value) if the JSON value is not a valid path string type.

## State Changes:
Attributes READ:
    - self.path (used to test existence and to open for reading/writing)

Attributes WRITTEN:
    - None of the object's attributes (no self.<attr> fields are assigned). The method does, however, mutate the file at self.path.

## Constraints:
Preconditions:
    - self.path is a pathlib.Path referencing the JSONL history file path (this is set by __init__).
    - directory is provided as a pathlib.Path. The caller is responsible for passing a Path object; the method performs equality comparison against pathlib.Path(json['directory']).
    - The history file is expected to be a JSON Lines file (one JSON object per line) where each object contains a 'directory' string produced by the companion add() method.

Postconditions:
    - If self.path did not exist at call time: the method returns immediately and leaves no filesystem changes.
    - If self.path existed and the method completes successfully: the file at self.path contains only those lines (in original order) whose parsed JSON object's 'directory' value (after pathlib.Path()) is not equal to the provided directory.
    - If an exception from JSON decoding, missing key, or path-conversion occurs while filtering: the file has already been opened with mode 'w' (truncated) and the exception propagates; the file may therefore be left truncated or empty. No rollback or atomic replacement is performed by this method.

Path equality semantics:
    - The comparison uses pathlib.Path(json_value) == directory. This requires the stored string and the provided directory to refer to the same path object under Path's equality semantics. Differences in absolute vs relative paths, symlinks, or string formatting may cause an entry not to match and thus not be removed.

Concurrency and atomicity constraints:
    - The method is not safe against concurrent modification of the history file by other processes/threads. The implementation first reads all lines, then opens the same file in write mode (which truncates it) and writes filtered contents. If concurrent writers/readers exist, results are race-prone.
    - No atomic replace (e.g., write-to-temp-and-rename) is performed; callers that require atomicity must implement an external locking/transaction mechanism.

## Side Effects:
    - File I/O: Reads the entire history file into memory (history_lines) and then rewrites the file at self.path with filtered contents. This can be memory-intensive for very large history files.
    - Truncation risk: The file is opened in write mode before the filtering expression is fully evaluated; if an exception occurs while evaluating filter/join (e.g., JSONDecodeError, KeyError), the file is already truncated and may be lost or left empty.
    - Logging: Emits an info-level log entry indicating the clearing action (logger.info('clear the downloading history for this directory: %s', self.path)).
    - No network or external service calls are made.

### `onlinejudge_command.download_history.DownloadHistory._flush` · *method*

## Summary:
When the history file at self.path reaches or exceeds 1 MiB, truncate it on disk by removing the last floor(N/2) lines (i.e., the most-recent floor(N/2) entries), leaving the earlier lines and reducing file size.

## Description:
Known callers and lifecycle:
- Called by DownloadHistory.add(...) immediately after appending a new history entry. This is invoked as a maintenance step in the append pipeline to enforce a file-size cap so the history file does not grow unbounded.

Why this logic is a separate method:
- Truncation is a distinct maintenance concern separated from append/remove/get operations. Factoring it into its own method isolates the file-size policy and keeps add() focused on appending; it also centralizes logging and truncation behavior.

## Args:
- None.

## Returns:
- None.

## Raises:
- FileNotFoundError: If self.path does not exist when calling self.path.stat() or when opening the file; these errors are not caught by this method.
- PermissionError: If the process lacks permission to read or write self.path.
- OSError and other I/O-related exceptions: Any low-level errors raised by stat() or open() propagate to the caller.
Note: The method does not perform internal exception handling for I/O errors (the caller is expected to handle them if needed).

## State Changes:
Attributes READ:
- self.path (used for stat() and to open the file for reading/writing)

Attributes WRITTEN:
- None of the object's attributes are modified.

Filesystem state written:
- The file at self.path is overwritten. Its new contents are the original file's first M lines where M == len(history_lines) - (len(history_lines) // 2). Concretely, the code writes history_lines[:-half_count] where half_count = len(history_lines) // 2.

## Constraints:
Preconditions:
- self.path must be a valid filesystem path where stat() and open() calls are permitted. Typical caller add() ensures the parent directory exists and has appended at least one line prior to calling _flush().

Size threshold and exact condition:
- The truncation runs only if self.path.stat().st_size >= 1024 * 1024 (i.e., 1,048,576 bytes).

Precise truncation semantics (postconditions):
- If the size check fails (< 1 MiB), the method does nothing and leaves the file unchanged.
- If the size check passes (>= 1 MiB):
    - The file is read fully into memory as a list of text lines via readlines().
    - half_count = len(history_lines) // 2
    - The file is overwritten with history_lines[:-half_count] (the first len(history_lines) - half_count lines).
    - Important precise behavior: in Python, when half_count == 0 (possible if the file contains a single line whose length alone exceeds the threshold), history_lines[:-0] evaluates to an empty list, so the file will be overwritten as empty (all lines removed).
    - An info-level log entry is emitted indicating truncation occurred.

## Side Effects:
- Disk I/O: reads the entire file into memory and then writes a truncated copy back. This can be memory-intensive for files that have very long lines (single-line files).
- Logging: emits an info-level message via the module-level logger indicating the history file was halved (the code calls logger.info('halve history at: %s', self.path)).
- Concurrency considerations: this implementation is not atomic with respect to other writers; concurrent writers or readers may observe intermediate states or lost writes (data races). If concurrent access is possible, the caller should serialize access (e.g., with a file lock) before calling _flush().
- No network calls or external services are used.

## Implementation notes for reimplementation:
- Check the file size with self.path.stat().st_size and compare against the constant 1024 * 1024.
- When truncating:
    - Open the file for reading in text mode (the code uses with open(self.path) as fh:), call fh.readlines() to obtain a list of lines (each ending with newline if originally present).
    - Compute half_count = len(history_lines) // 2.
    - Overwrite the file with open(self.path, 'w') and write ''.join(history_lines[:-half_count]).
    - Preserve the same logging call: logger.info('halve history at: %s', self.path).
- Do not swallow I/O exceptions: let them propagate as in the original implementation.
- Be aware of the semantics of slicing with half_count == 0: list[:-0] is an empty list; the original code therefore clears the file in that case.

### `onlinejudge_command.download_history.DownloadHistory.get` · *method*

## Summary:
Return the list of URLs recorded in the download-history file that reference the specified directory; does not modify the object state.

## Description:
This method reads a newline-delimited JSON history file pointed to by self.path, extracts entries whose "directory" field equals the provided directory, and returns the set of corresponding "url" values as a list. It is typically invoked by higher-level commands or components that need to determine which problem URLs have already been downloaded into a given working directory (for example, to avoid re-downloading or to show download history). The logic is separated into its own method because it cleanly encapsulates reading, parsing, and filtering the persistent history log (I/O + parsing), keeping callers free from file-handling concerns and making error-handling and logging centralized.

Known callers and context:
- Caller: higher-level commands that reconcile or inspect previously downloaded problems (e.g., "download" or "list" command implementations). Called during the stage where the tool decides whether to download a URL again or to show previously downloaded items for a particular directory.
- Lifecycle: invoked at runtime when history is needed; it does not run at object construction.

Why this is a separate method:
- Encapsulates file I/O, parsing, and filtering logic for reuse.
- Centralizes logging and robust handling of corrupted history lines.
- Keeps the calling code focused on decision logic rather than history-file format.

## Args:
    directory (pathlib.Path): A pathlib.Path representing the directory to filter history entries by. This argument is keyword-only (the method signature uses a keyword-only parameter).

## Returns:
    List[str]: A list of URL strings found in the history file whose recorded directory equals the provided directory.
    - If the history file (self.path) does not exist, returns an empty list.
    - Duplicates in the file are removed (the method collects URLs into a set before returning).
    - The order of returned URLs is not guaranteed.

## Raises:
    Any exception raised during open() or parsing that is not explicitly handled by the code may propagate to the caller. Concretely:
    - FileNotFoundError: possible if the file is removed between the exists() check and open().
    - json.JSONDecodeError: NOT raised to caller for corrupted lines — those lines are caught and skipped; however, an unexpected JSON decoding issue outside the per-line try/except could still propagate.
    - KeyError: if a parsed JSON object does not contain the 'directory' or 'url' key, accessing data['directory'] or data['url'] will raise KeyError.
    - TypeError or ValueError: may arise if the JSON values are of unexpected types (for example, data['directory'] is not a string), or when constructing pathlib.Path(data['directory']).
    - Any other I/O or JSON-related exceptions not explicitly caught will propagate.

## State Changes:
Attributes READ:
    - self.path: read to check existence and to open the history file.

Attributes WRITTEN:
    - None. The method does not modify attributes on self.

## Constraints:
Preconditions:
    - self.path should be an attribute on self representing the path to the history file (Path-like). It should be set before calling this method.
    - directory must be a pathlib.Path (or object acceptable to pathlib.Path comparisons); callers should pass a pathlib.Path for correct equality comparisons.

Postconditions:
    - The returned list contains every unique URL string that was recorded in the history file with 'directory' equal to the provided directory at the time of file reading, with corrupted lines ignored.
    - The method does not modify self or the history file.

## Side Effects:
    - Reads from the filesystem (opens and reads self.path).
    - Emits logging events:
        - info: when starting to read and listing found URLs.
        - warning and debug: when a corrupted JSON line is encountered (the JSON decoding exception is caught and logged; the stack trace is logged at debug level).
    - Does not write files or mutate external objects.

