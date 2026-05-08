# `load.py`

## `hypertools.tools.load.load` · *function*

*No documentation generated.*

## `hypertools.tools.load._load_legacy` · *function*

## Summary:
Read a legacy-format dataset file using deepdish, normalize the 'data' and 'xform_data' fields to expected in-memory types, and return a DataGeometry constructed from the resulting dictionary.

## Description:
This helper centralizes compatibility logic for datasets saved in an older on-disk (legacy) format. It dynamically imports the deepdish loader, uses dd.io.load to read the file into a dictionary, performs a small set of type-normalizing transformations on two fields, and then forwards the final mapping into DataGeometry(**data_dict).

Known callers within the provided repository snapshot:
    - No direct call-sites were found in the provided snapshot. This function is intended to be invoked by the package's dataset-loading pipeline when a file is detected to be in the legacy format.

Why this function is extracted:
    - Isolates legacy-format handling and the conditional dependency on deepdish so the main loader code does not need to manage import errors or format-specific conversions.
    - Encapsulates the minimal set of transformations required to adapt legacy payloads to the shape expected by DataGeometry, making the compatibility logic easier to test and evolve.

## Args:
    dataset_path (str or os.PathLike)
        Path to the legacy-format dataset file. The value is passed directly to deepdish.io.load.
        - Required: yes
        - Accepted forms: string path or Path-like object pointing to a file accessible by the runtime process.

## Returns:
    datageometry.DataGeometry
        An instance created by calling DataGeometry(**data_dict) where data_dict is the dictionary returned by dd.io.load after the in-place transformations described below.

        Notes on return behavior:
        - On success, always returns a DataGeometry instance.
        - No explicit None return or sentinel values are produced by this function; failure scenarios raise exceptions (see Raises).

## Behavior and transformations (exact logic from source):
    1. Attempt to import deepdish as the local alias dd. If import fails, raise HypertoolsIOError (see Raises).
    2. Call dd.io.load(dataset_path) and assign the result to data_dict. This code expects data_dict to be a mapping (supporting data_dict['data'] and data_dict['xform_data']).
    3. Inspect data_dict['data']:
        - If isinstance(data_dict['data'], dict): replace it with pd.DataFrame(data_dict['data'])
        - Else if isinstance(data_dict['data'], np.ndarray): replace it with list(data_dict['data'])
        - Otherwise leave data_dict['data'] unchanged.
      Note: The source uses pd and np (the pandas and numpy aliases) for these checks and transformations.
    4. Replace data_dict['xform_data'] with list(data_dict['xform_data']) (always converted to a list).
    5. Return DataGeometry(**data_dict)

## Raises:
    HypertoolsIOError
        - Trigger: deepdish cannot be imported (ImportError). The function raises HypertoolsIOError with a message instructing to install 'deepdish'. The original ImportError is chained.

    KeyError
        - Possible triggers:
            * data_dict does not contain the 'data' key when the function attempts to access data_dict['data'].
            * data_dict does not contain the 'xform_data' key when the function attempts to access data_dict['xform_data'].
        - These KeyErrors originate from direct dictionary indexing in the source.

    Any exception raised by dd.io.load(dataset_path)
        - Examples include file-related errors (e.g., file not found, permission errors) or deepdish-specific parsing errors. These propagate unchanged.

    TypeError or other exceptions from DataGeometry(**data_dict)
        - If the final data_dict lacks required constructor arguments or contains incompatible types/extra unexpected keys, DataGeometry's constructor may raise TypeError or custom validation errors. These propagate unchanged.

    TypeError or AttributeError (other)
        - If dd.io.load returns a non-mapping (e.g., None or list), attempting data_dict['data'] will raise TypeError or other exceptions. These propagate.

## Constraints:
    Preconditions:
        - Caller must provide a filesystem path accessible to the process.
        - The file at dataset_path must be in the legacy format that deepdish can parse into a mapping containing at least 'data' and 'xform_data' keys (otherwise KeyError or other exceptions will be raised).
        - The pandas and numpy aliases referenced in the function (pd and np) must resolve to pandas and numpy modules respectively in the runtime environment.

    Postconditions (guarantees on successful return):
        - data_dict['data'] will be one of:
            * pandas.DataFrame if the original was a dict
            * list if the original was a numpy.ndarray
            * unchanged for other original types
        - data_dict['xform_data'] will be a list instance (list(xform_data))
        - The function returns a DataGeometry instance constructed with the transformed data_dict

## Side Effects:
    - Performs dynamic import of deepdish (module import).
    - Performs file I/O by calling deepdish.io.load(dataset_path) (reads the file content from disk).
    - Does not modify global variables in this module.
    - No network I/O or external service calls are performed by the function itself.

## Control Flow:
flowchart TD
    Start --> ImportTry["import deepdish as dd"]
    ImportTry -->|ImportError| RaiseHTIOErr["Raise HypertoolsIOError: install 'deepdish'"]
    ImportTry -->|Success| Load["data_dict = dd.io.load(dataset_path)"]
    Load --> CheckDataKey{"'data' key present?"}
    CheckDataKey -->|no| NextXform["Convert xform_data -> list(...)"]
    CheckDataKey -->|yes| IsDict{"isinstance(data_dict['data'], dict)?"}
    IsDict -->|yes| ToDataFrame["data_dict['data'] = pd.DataFrame(...)"]
    IsDict -->|no| IsNDArray{"isinstance(data_dict['data'], np.ndarray)?"}
    IsNDArray -->|yes| ToList["data_dict['data'] = list(...)"]
    IsNDArray -->|no| Keep["leave data_dict['data'] unchanged"]
    ToDataFrame --> NextXform
    ToList --> NextXform
    Keep --> NextXform
    NextXform --> ConvertXform["data_dict['xform_data'] = list(data_dict['xform_data'])"]
    ConvertXform --> Construct["return DataGeometry(**data_dict)"]
    Construct --> End

## Examples:
    - Basic usage (conceptual):
        try:
            geom = _load_legacy("/path/to/legacy_dataset.h5")
        except HypertoolsIOError as e:
            # deepdish not installed; inform user how to install
            handle_missing_dependency(e)
        except KeyError as e:
            # file missing expected keys (likely not a legacy dataset or corrupted)
            handle_bad_format(e)
        except Exception as e:
            # catch-all for file I/O / parsing / constructor errors
            handle_general_failure(e)
        else:
            # geom is a DataGeometry instance ready for downstream use
            use_geometry(geom)

    - Notes on realistic failure modes:
        * If the file is not present or unreadable, dd.io.load will typically raise a file I/O error (propagated).
        * If deepdish is not installed in the environment, HypertoolsIOError is raised immediately before any file I/O.
        * If the stored payload does not include the expected mapping keys ('data' and 'xform_data'), KeyError will be raised when those keys are accessed.

## `hypertools.tools.load._load_example_data` · *function*

## Summary:
Loads a named example dataset from the local example-cache directory, downloading it first if necessary, and returns a DataGeometry object representing the dataset. For the 'mushrooms' dataset the returned object's .data attribute is converted to a pandas.DataFrame.

## Description:
This internal helper resolves the on-disk path for a requested example dataset (joining the module-level DATA_DIR with the dataset name). If the dataset file does not exist locally, it ensures DATA_DIR exists and delegates the download to the module-level _download_example_data(dataset_path), which is responsible for fetching and writing the file.

Known callers:
- Not deterministically discovered in the code snapshots available. Typical callers are higher-level dataset loader functions such as a module-level "load example dataset" or "ensure example presence" function which accepts a dataset name and needs a ready-to-use DataGeometry object. In such pipelines, this function is invoked when the caller needs to obtain a concrete DataGeometry instance for a named example.

Why this logic is extracted:
- Separates path-resolution, cache-check, and post-processing from the network/file-download responsibilities. This function focuses on ensuring a dataset file is present and on converting the raw cached bytes into an in-memory DataGeometry object, while _download_example_data encapsulates network and streaming I/O, retry, and cleanup behavior.

## Args:
    dataset (str):
        The dataset identifier (file name/key). Expected to match an example dataset file name used in the module cache directory and the key used by the example-download mapping used by _download_example_data. Typical values include example dataset names like 'mushrooms' (which receives special post-processing). Must be a valid filename component (no path separators expected).

## Returns:
    datageometry.DataGeometry:
        A DataGeometry instance reconstructed from the pickled bytes stored at DATA_DIR / dataset. On success this object is returned directly. If the dataset equals 'mushrooms', the returned object's .data attribute is converted into a pandas.DataFrame (replacing whatever raw structure was stored) before returning.

    Edge-case return values:
        - If loading succeeds, a DataGeometry instance is always returned.
        - There is no explicit None-return path in normal execution; failures raise exceptions.

## Raises:
    HypertoolsIOError:
        Raised when unpickling or reading the cached dataset bytes fails. Triggered when any exception is thrown during dataset_path.read_bytes() or pickle.loads(...). The raised HypertoolsIOError message is:
            "Failed to load '<dataset>' data. Try deleting cached file at<dataset_path> and reloading."
        The original exception is chained as the __cause__.

    Propagated exceptions from dependencies:
        - Any exception raised by _download_example_data (for example HypertoolsIOError, KeyError for unknown dataset name, or network/IO errors converted by that helper) will propagate to the caller.
        - If the module-level DATA_DIR variable is missing or not a Path-like object, builtin exceptions such as NameError or AttributeError/TypeError may occur before the explicit HypertoolsIOError is raised.

## Constraints:
    Preconditions:
        - The module-level DATA_DIR must be a pathlib.Path (or Path-like) representing the directory used to cache example files.
        - The caller must provide a valid dataset name (string). If that dataset is unknown to the download helper, downloading will fail.
        - The process must have permission to create DATA_DIR and to write files inside it (when the dataset is not cached locally).
        - Network access may be required indirectly if the dataset is not cached (because _download_example_data will attempt to download).

    Postconditions:
        - On success: DATA_DIR / dataset exists (either pre-existing or newly downloaded) and the returned object is a deserialized DataGeometry representing the dataset. For 'mushrooms' the .data attribute is a pandas.DataFrame.
        - On failure: an exception is raised; partially cached files (if any) are expected to be handled by the download helper, and no partially-deserialized DataGeometry is returned.

## Side Effects:
    Filesystem:
        - May create the directory DATA_DIR (via DATA_DIR.mkdir()) if it does not exist.
        - May cause a new file to be written at DATA_DIR / dataset by calling _download_example_data when the cached file is missing.

    Network:
        - Indirect network activity can occur because _download_example_data performs HTTP requests to fetch missing datasets.

    Memory:
        - Allocates memory for the unpickled DataGeometry object when reading the file into memory.

    No other global state is modified by this function itself.

## Control Flow:
flowchart TD
    Start[Start] --> ResolvePath[dataset_path = DATA_DIR.joinpath(dataset)]
    ResolvePath --> CheckExists{dataset_path.is_file()?}
    CheckExists -- Yes --> LoadPickle[try: bytes = dataset_path.read_bytes(); geo_data = pickle.loads(bytes)]
    CheckExists -- No --> EnsureDir{DATA_DIR.is_dir()?}
    EnsureDir -- No --> MakeDir[DATA_DIR.mkdir()]
    EnsureDir -- Yes --> CallDownload[_download_example_data(dataset_path)]
    CallDownload --> LoadPickle
    LoadPickle -->|pickle.loads raised| RaiseLoadError[raise HypertoolsIOError(...)]
    LoadPickle -->|success| PostProcess{dataset == 'mushrooms'?}
    PostProcess -- Yes --> ConvertDF[geo_data.data = pandas.DataFrame(geo_data.data)]
    PostProcess -- No --> ReturnGeo[return geo_data]
    ConvertDF --> ReturnGeo

## Examples:
    Typical usage pattern (caller-level pseudocode):
        try:
            geom = _load_example_data('mushrooms')
            # geom is a DataGeometry instance; geom.data is a pandas.DataFrame for 'mushrooms'
            # proceed to analyze or plot:
            # analyze(geom) or plot(geom)
        except HypertoolsIOError as e:
            # Loading failed (corrupt cache, unpickling error). Suggest remedy to user:
            print("Failed to load example dataset. Try deleting the cached file and retrying.")
            raise

    Notes:
        - If the requested dataset is not present in the cache, this function will attempt to download it automatically by calling _download_example_data; callers should expect download-related errors (HypertoolsIOError, KeyError) to propagate.
        - For automated workflows, callers that wish to distinguish "absent dataset" from "corrupt cache" should attempt to check (DATA_DIR / dataset).is_file() and handle KeyError from the download helper before calling this function.

## `hypertools.tools.load._download_example_data` · *function*

## Summary:
Downloads an example dataset identified by dataset_path.name from a remote BASE_URL into the given filesystem path, streaming the response to disk and converting any low-level failures into a HypertoolsIOError.

## Description:
This helper performs the network download and file-writing responsibilities required to fetch example datasets whose identifiers are stored in the module-level EXAMPLE_DATA mapping. Typical call context: a higher-level "load example dataset" function resolves a target local path (Path) and delegates the download to this helper when the dataset file is not present locally. This separation isolates:
- network and streaming I/O logic,
- the cookie-based confirmation retry behavior required by some servers,
- cleanup of partially-written files on failure,
so the higher-level loader can focus on path resolution, decompression/format handling, and post-processing.

Known callers within the codebase:
- Not determined at documentation generation time. In practice, this function is intended to be called by functions that need to ensure a named example dataset exists locally (e.g., a module-level load_example or ensure_example function). The exact call sites were not available for retrieval.

Why extracted:
- Encapsulates transient network and file-write concerns, including retry-on-confirm-cookie behavior and deterministic cleanup of partial downloads, so callers can be simpler and handle only higher-level dataset readiness.

## Args:
    dataset_path (pathlib.Path or path-like object with .name, .open, .unlink):
        Path where the downloaded file will be written. The function reads dataset_path.name to look up the remote file identifier in EXAMPLE_DATA and opens the path in binary write mode. The provided object must support:
          - .name (str): dataset identifier key
          - .open(mode) -> file-like object writable in binary mode
          - .unlink(missing_ok=True) to remove the file on failure (or an equivalent method)

    Implicit module-level dependencies (must be present and valid):
        EXAMPLE_DATA (dict-like): mapping from dataset name (dataset_path.name) to a remote file identifier used as the value for the 'id' request parameter.
        BASE_URL (str): base URL used for HTTP GET requests to download the file.
    Interdependencies:
        dataset_path.name must be a key in EXAMPLE_DATA; otherwise a KeyError will be raised before any network activity.

## Returns:
    None

    Behavior: on success the function completes after fully writing the remote response stream to dataset_path and returns None implicitly. No explicit success value is returned.
    Edge cases:
      - If an exception occurs during HTTP request, iteration, or file I/O, the function attempts to remove the partially-written file (dataset_path.unlink(missing_ok=True)) and raises a HypertoolsIOError instead of propagating the original exception.

## Raises:
    KeyError:
        If dataset_path.name is not present in the EXAMPLE_DATA mapping (lookup of EXAMPLE_DATA[dataset_path.name]).

    HypertoolsIOError:
        Raised when any exception occurs during the download or file-write process. The original exception is chained as the __cause__ of the HypertoolsIOError. The error message is:
            "Failed to download '<dataset_path.name>' dataset"
        (The function also attempts to delete the target file before raising.)

    Other possible exceptions (not converted):
        If dataset_path lacks required attributes or methods (e.g., .open or .unlink) the function may raise AttributeError or TypeError before or during execution.

## Constraints:
    Preconditions:
      - EXAMPLE_DATA must be defined and contain dataset_path.name as a valid key.
      - BASE_URL must be defined and reachable.
      - Caller must provide a path location where the process has permission to write.
      - Network access is available to contact BASE_URL.

    Postconditions:
      - On success: dataset_path exists on disk and contains the downloaded bytes exactly as delivered by the server's response body.
      - On failure: an attempt is made to remove dataset_path (missing_ok=True); a HypertoolsIOError is raised and the original exception is attached as the cause.

## Side Effects:
    I/O:
      - Network: one or two HTTP GET requests to BASE_URL using requests.Session with params {'id': file_id} and stream=True. If a cookie whose key starts with 'download_warning' is present in the first response, a second request is made with params['confirm'] set to that cookie value.
      - Filesystem: opens dataset_path for binary writing and writes chunks of the response. On exception, calls dataset_path.unlink(missing_ok=True) to remove partial files.

    External state mutations:
      - No global variables are modified by this function.
      - Uses requests.Session which holds ephemeral cookies scoped to the function; no persistent session stored externally.

    External services:
      - Any remote HTTP server serving files at BASE_URL.

## Control Flow:
flowchart TD
    Start[Start] --> Lookup{dataset_path.name in EXAMPLE_DATA}
    Lookup -- Missing --> RaiseKeyError[KeyError raised]
    Lookup -- Found --> GetFileID[file_id = EXAMPLE_DATA[name]]
    GetFileID --> CreateSession[session = requests.Session()]
    CreateSession --> PrepareParams[params = {'id': file_id}]
    PrepareParams --> TryRequest[try: response = session.get(BASE_URL, params=params, stream=True)]
    TryRequest --> CheckCookies[for key,value in response.cookies.items()]
    CheckCookies -->|key startswith 'download_warning'| SetConfirm[params['confirm'] = value]
    SetConfirm --> RetryRequest[response = session.get(BASE_URL, params=params, stream=True)]
    CheckCookies -->|no such cookie| SkipRetry[proceed to write]
    RetryRequest --> WriteFile
    SkipRetry --> WriteFile[open dataset_path and write response.iter_content(chunk_size=32768) if chunk]
    WriteFile --> Success[Return None]
    TryRequest -->|exception| Cleanup[dataset_path.unlink(missing_ok=True)]
    Cleanup --> RaiseHypertoolsIOError[raise HypertoolsIOError(...)]
    RaiseHypertoolsIOError --> End[End]

## Examples:
    Example usage pattern (illustrative, not actual code block):
      - Prepare a target path:
          p = Path.home() / ".hypertools" / "examples" / "example_dataset.mat"
      - Ensure parent directory exists, then call the helper and handle failures:
          try:
              _download_example_data(p)
              # Next: load or post-process the downloaded file
          except HypertoolsIOError as e:
              # Log and surface a user-friendly error
              raise RuntimeError(f"Could not obtain example dataset at {p}") from e

    Notes on typical error handling:
      - If EXAMPLE_DATA lacks the dataset name, callers should catch KeyError before calling, or wrap calls and report "unknown example dataset".
      - If network issues occur, callers will receive HypertoolsIOError. The exception's __cause__ field contains the original exception (e.g., requests.exceptions.RequestException, OSError).

