# `cache.py`

## `src.ydata_profiling.utils.cache.cache_file` · *function*

## Summary:
Download a file from a remote URL into the project's data directory and return the local path, skipping the download if the file is already present.

## Description:
This function centralizes the logic for caching downloaded files under the project's data directory. It:
- Resolves the data directory via get_data_path() and ensures the directory exists.
- Constructs a local file path using the provided file_name.
- If the target file does not already exist, it downloads the content from the given URL and writes it to the local file path.
- Returns the Path to the local file (whether newly downloaded or previously present).

Known callers:
- No explicit callers are provided in the supplied context. Typical callers are modules that need to fetch and cache remote assets (example: sample datasets, pretrained models, auxiliary resources) during initialization or setup phases.

Why this logic is extracted:
- Responsibility boundary: encapsulates idempotent download-and-cache semantics so callers can rely on a single place to ensure a local copy exists.
- Reuse: avoids duplicating download, directory-creation, and file-write code across the codebase.
- Error propagation: centralizes error behavior for networking and filesystem failures so callers can implement consistent retry / error handling.

## Args:
    file_name (str): File name (relative) to use inside the project's data directory (e.g., "dataset.csv" or "models/resnet.pt"). This is appended to the directory returned by get_data_path().
    url (str): URL (e.g., "http://..." or "https://...") to fetch the file content from when the local file is absent.

Interdependencies:
    - file_name is interpreted relative to the Path returned by get_data_path(). The function does not validate that file_name is a simple name vs. a path (subdirectory components are permitted and will be appended to the data directory).
    - The function relies on get_data_path() to point to an existing or creatable directory under the project root.

## Returns:
    pathlib.Path: The path to the cached file inside the project's data directory. If the file already existed, that path is returned without attempting a download. If the file had to be downloaded and writing succeeded, the new file path is returned.

Edge-case return behavior:
    - The function always returns the file Path when it completes successfully.
    - If an exception occurs during download or write, the exception is propagated and no Path is returned.

## Raises:
    - urllib.error.URLError or urllib.error.HTTPError: If request.urlopen fails to connect or receives an HTTP error response while attempting to download the URL.
    - OSError (including PermissionError, FileNotFoundError): If writing the file bytes to disk fails (e.g., due to permission issues, disk full, invalid path components).
    - Any other exceptions raised by get_data_path() or Path.mkdir() are propagated (for example if get_data_path() itself raises).

Exact trigger conditions visible in the implementation:
    - request.urlopen(url) will raise networking-related exceptions if URL is unreachable or returns an error.
    - file_path.write_bytes(...) will raise standard filesystem-related OSError-derived exceptions if the write fails.
    - No explicit exception handling is present in the function; callers must catch and handle exceptions as needed.

## Constraints:
Preconditions:
    - The environment must have network access to reach the provided URL when a download is required.
    - The process must have permissions to create the project's data directory and write files into it.
    - get_data_path() should return a valid Path where a "data" directory can be created.

Postconditions (on successful return):
    - The directory returned by get_data_path() exists (mkdir was called with exist_ok=True).
    - The returned Path points to an existing file containing the bytes downloaded from the provided URL (or the pre-existing file if the function skipped the download).
    - The function does not validate file integrity (no checksums) or handle partial downloads; if a partial file already exists, it is treated as "present" and the function will not attempt to re-download.

## Side Effects:
    - Filesystem: may create the data directory (via Path.mkdir(exist_ok=True)) and will write a file under it using file_path.write_bytes(...).
    - Network I/O: may perform an HTTP(S) request through urllib.request.urlopen to fetch the file content.
    - No global variables are modified by this function.
    - No automatic extraction, decompression, or checksum verification is performed (zipfile is imported in the module file but not used by this function).

## Control Flow:
flowchart TD
    Start --> GetDataPath[get_data_path()]
    GetDataPath --> Mkdir[data_path.mkdir(exist_ok=True)]
    Mkdir --> BuildPath[file_path = data_path / file_name]
    BuildPath --> ExistsCheck{file_path.exists()}
    ExistsCheck -- Yes --> ReturnExisting[return file_path]
    ExistsCheck -- No --> Download[response = request.urlopen(url)]
    Download --> Write[file_path.write_bytes(response.read())]
    Write --> ReturnNew[return file_path]
    Download -->|network error| PropagateError[raise URLError/HTTPError]
    Write -->|write error| PropagateError2[raise OSError/PermissionError]

## Examples:
Example 1 — Basic usage in a setup phase:
    try:
        path = cache_file("iris.csv", "https://example.com/datasets/iris.csv")
        # Use the file at `path` for downstream processing
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        # Handle network issues (retry, fallback, or surface error)
        raise
    except OSError as e:
        # Handle filesystem issues (permission, disk space)
        raise

Example 2 — Using a cached file if present (idempotent):
    # Calling this repeatedly is safe: it will only download once as long as
    # the file exists in the data directory.
    cached = cache_file("models/resnet50.pt", "https://example.com/models/resnet50.pt")
    # Proceed to load cached

Notes and recommendations for callers:
    - If your use case needs integrity checks, atomic writes, or resumable downloads, implement those safeguards around or before calling this function (for example, download to a temporary file and rename on success).
    - For large files, consider streaming the response instead of reading all bytes at once to reduce memory usage; this implementation reads the entire response in memory via response.read() before writing.
    - If concurrent processes may call cache_file with the same file_name, callers should coordinate (e.g., file locking) to avoid race conditions where multiple processes attempt downloads/writes simultaneously.

## `src.ydata_profiling.utils.cache.cache_zipped_file` · *function*

## Summary:
Downloads a ZIP archive from a URL, extracts a single member (by basename) into the library data directory (creating that directory if it exists or is creatable), and returns a Path object that represents where the caller expects the file to be cached. If the file already exists at the expected path, the function does nothing and returns immediately.

## Description:
This utility centralizes the pattern of ensuring a particular resource file (packaged inside a remote ZIP archive) is available on disk for later processing. It performs: ensure data directory exists, skip work if file already present, download the ZIP, extract exactly one archive member, remove the temporary archive, and return the expected Path.

Typical callers and trigger conditions:
- Data-loading or initialization code that depends on a shipped asset (for example, a CSV, JSON, or model weight file) provided inside a ZIP on a remote server.
- Callers invoke this when they need to guarantee the file is locally available before parsing or training.

Why this logic is isolated:
- It separates network and filesystem concerns from higher-level logic, prevents duplication, and ensures a consistent cache location and cleanup policy across the codebase.

Important implementation detail (behavioral caveat):
- The function extracts zip member using the basename of the requested file name (file_path.name). If the caller supplies file_name that contains path components (for example, "subdir/data.csv"), the function will extract only "data.csv" directly into the data directory, but it still returns data_dir / "subdir/data.csv". This means the returned Path may not point to the actual extracted file when file_name contains directory components. Callers should pass only the archive member name (no path components) to avoid this mismatch.

## Args:
    file_name (str): The archive member name to extract (should be the basename, e.g., "data.csv"). If file_name contains directory separators (e.g., "subdir/data.csv"), extraction will use only the final segment (basename), but the function will still compute and return data_dir / file_name — see the caveat above.
    url (str): HTTP(S) URL pointing to a ZIP archive that contains the desired file_name.

Interdependencies:
- The function relies on get_data_path() to locate the data directory. The returned path is used to compute the destination and temporary file paths.

## Returns:
    pathlib.Path: The computed destination path (get_data_path() / file_name). This is the path the caller should expect the file to be at after a successful call.

Return edge cases:
- If file_name contains path components, the actual extracted file will be data_dir / basename(file_name) while the function still returns data_dir / file_name. This discrepancy can cause the returned Path not to exist even after successful extraction — treat this behavior as a precondition: pass a basename-only file_name.
- If the file already exists at the computed destination when the function is called, it returns immediately with that Path and performs no network I/O.

## Raises:
The function does not swallow exceptions; callers will observe the underlying exceptions raised by the operations below:
    - urllib.error.URLError or urllib.error.HTTPError: Raised by request.urlopen(url) on network failures or non-successful HTTP responses.
    - zipfile.BadZipFile: Raised if the downloaded bytes are not a valid ZIP archive.
    - KeyError (or zipfile-related error): Raised if the expected member is not found in the archive when extracting (zipfile.ZipFile.extract will fail for missing members).
    - OSError (including PermissionError, FileNotFoundError): Raised by filesystem operations such as writing the temporary file, creating the directory (mkdir), or unlinking files.
    - Any exceptions from get_data_path() if that function raises.

## Constraints:
Preconditions:
    - url must point to a reachable ZIP archive.
    - file_name should be the archive member name (basename only). Avoid supplying path components to file_name unless you intentionally accept the behavior described above.
    - The process must have permission to create and write files inside the path returned by get_data_path().
    - The parent directories of the path returned by get_data_path() must already exist or be creatable by the process; mkdir is called without parents=True, so missing intermediate parents may cause an OSError.

Postconditions (on successful return):
    - A file with the same basename as file_name exists in the directory returned by get_data_path() (i.e., data_dir / basename(file_name)).
    - The temporary ZIP file named "tmp.zip" that was created for the download has been removed.
    - The returned Path equals data_dir / file_name (note the caveat about dirname components above).

## Side Effects:
    - Network: performs an HTTP(S) request to download the ZIP via urllib.request.urlopen.
    - Filesystem:
        - Calls mkdir(exist_ok=True) on the data directory (will create the final directory if its parent exists).
        - Writes a temporary file named "tmp.zip" into the data directory containing the downloaded archive bytes.
        - Extracts an archive member (the basename of file_name) into the data directory; this may overwrite an existing file with the same name.
        - Removes the temporary "tmp.zip" upon successful extraction.
    - No global variables, external databases, or network services (other than the provided URL) are modified beyond the described I/O.

Failure side effects:
    - If an exception is raised before tmp.zip is unlinked (for example, during download or extraction), the temporary file may remain on disk. Callers that must avoid leftover temporary files should handle exceptions and delete get_data_path() / "tmp.zip" as needed.

## Control Flow:
flowchart TD
    A[Start] --> B[get_data_path()]
    B --> C[mkdir(data_path, exist_ok=True)]
    C --> D[file_path = data_path / file_name]
    D --> E{file_path.exists()?}
    E -- Yes --> F[Return file_path]
    E -- No --> G[response = request.urlopen(url)]
    G --> H[tmp_path = data_path/"tmp.zip"]
    H --> I[tmp_path.write_bytes(response.read())]
    I --> J[with zipfile.ZipFile(tmp_path) as zip_file]
    J --> K[zip_file.extract(file_path.name, data_path)]
    K --> L[tmp_path.unlink()]
    L --> F[Return file_path]
    J --> M[Exception during open/extract -> propagate]
    G --> N[Network error -> propagate]
    C --> O[mkdir error if parent missing -> propagate]

## Examples (usage pattern and error handling):
- Typical (happy-path) usage:
    - Call with a basename and the URL of the ZIP:
        - file_path = cache_zipped_file("example.csv", "https://example.com/archive.zip")
        - After return, example.csv will be present in the library data directory.
- Defensive usage showing cleanup of the temporary ZIP on error (pseudocode):
    try:
        path = cache_zipped_file("example.csv", "https://example.com/archive.zip")
    except Exception as exc:
        # If a failure left a temporary file, remove it to prevent stale state.
        tmp = get_data_path() / "tmp.zip"
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            # Ignore cleanup failures; re-raise original exception
            pass
        raise

Recommendations:
    - Always pass only the member basename for file_name to avoid the returned-path vs extracted-file mismatch.
    - If callers require atomicity and stronger guarantees (temporary cleanup on any failure), consider wrapping this call with retry/cleanup logic or extend the function to always unlink tmp.zip in a finally block.

