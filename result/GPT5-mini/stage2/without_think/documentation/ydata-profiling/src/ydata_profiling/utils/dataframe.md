# `dataframe.py`

## `src.ydata_profiling.utils.dataframe.warn_read` · *function*

## Summary:
Invokes warnings.warn with the expression f as the message argument; because the function body is exactly warnings.warn(f) and does not reference the extension parameter, calling it will raise NameError unless a name 'f' is defined in accessible scope.

## Description:
- Exact behavior in source: The function evaluates the expression f and passes the resulting value to warnings.warn. The parameter extension (type-annotated str) is present in the signature but is not used in the function body.
- Caller discovery: A repository-wide search for callers was not available in the provided context; no callers are confirmed.
- Notes on intent: The source contains no docstring or comments explaining intent. Any statement about why the function was added or what message it should emit is speculative and not asserted here.

## Args:
    extension (str)
        - The function signature requires a single parameter named extension annotated as str.
        - Constraint: The implementation does not use this parameter; there is no validation of its value in the function.

## Returns:
    None
        - The function has no return statement; if it completes normally it returns None.
        - If a NameError occurs while evaluating the argument expression f, the function does not return and the exception propagates.

## Raises:
    NameError
        - Trigger condition: evaluating the argument expression f before calling warnings.warn. If the name f is not defined in local, enclosing, global, or builtins scope, Python raises NameError with message: "name 'f' is not defined".
    (No other exceptions are raised by the function itself. warnings.warn may raise only in unusual circumstances unrelated to this function's code path.)

## Constraints:
- Preconditions:
    - A caller must supply a value for the extension parameter (signature enforces it), but the function will ignore that value.
    - To avoid NameError, some binding named f must exist in accessible scope at call time — this is an accidental requirement caused by the current implementation.
- Postconditions:
    - If f is defined and evaluation succeeds, a warning is emitted via warnings.warn and the function returns None.
    - If f is undefined, a NameError is raised and no warning is emitted.

## Side Effects:
- Primary side effect: emits a Python warning via the warnings module (warnings.warn) if argument evaluation succeeds. The message passed to warnings.warn is the value of the expression f (which may be any object; warnings.warn will accept strings or Warning instances).
- No I/O (file, network), no global state mutations, and no external service calls are performed by this function as implemented.

## Control Flow:
flowchart TD
    Start[call warn_read(extension)] --> Eval[Evaluate expression: f]
    Eval --> IsDefined{Is name 'f' defined?}
    IsDefined -- No --> Raise[NameError: "name 'f' is not defined"] --> EndEx[exception propagated]
    IsDefined -- Yes --> CallWarn[Call warnings.warn(resolved value of f)]
    CallWarn --> Emit[warnings module emits a warning]
    Emit --> EndOK[Function returns None]

## Examples:
- Example showing the current failing behavior (no 'f' defined):
    try:
        warn_read("csv")
    except NameError as e:
        # Typical exception message:
        # NameError: name 'f' is not defined
        print("Raised:", type(e).__name__, str(e))

- Example showing behavior if a name 'f' happens to exist:
    f = "Legacy or accidental message"
    warn_read("csv")  # emits a warning with message "Legacy or accidental message"

- Recommended correction (illustrative suggestion for maintainers; not present in source):
    # Replace warnings.warn(f) with a constructed message that uses extension:
    message = f"Reading files with extension '{extension}' may be unsupported or experimental"
    warnings.warn(message)

- Example after the recommended correction:
    warn_read("xlsx")
    # Emits a warning: "Reading files with extension 'xlsx' may be unsupported or experimental"

## `src.ydata_profiling.utils.dataframe.is_supported_compression` · *function*

## Summary:
Return whether a given file extension string corresponds to a supported compression format (bz2, gz, xz, zip). The check is case-insensitive and performs a direct membership test on the lowercased extension.

## Description:
This function centralizes the logic for deciding whether a file suffix represents a compression format that the system can handle. Typical usage is to validate the suffix extracted from a filename or a Path object (for example, when choosing how to open or read a file). No callers were discovered in the available repository scan; when present, callers are usually code paths that branch on compressed versus uncompressed input handling.

This logic is extracted into its own function to:
- Keep the membership list of supported compression types in one place for easy maintenance.
- Provide a single, well-documented semantic check used by multiple file-processing components.
- Avoid repetition of case-insensitive matching logic across the codebase.

## Args:
    file_extension (str):
        - The file suffix to check, expected as a string such as ".gz" or ".zip".
        - The comparison is exact after lowercasing; the string must include the leading dot to match (e.g., ".gz" not "gz").
        - Typical values that return True: ".bz2", ".gz", ".xz", ".zip" (any capitalization: ".GZ", ".Zip" etc. are accepted).
        - Interdependencies: none. The function assumes the caller provides a suffix-like string (commonly produced by Path.suffix or manual parsing).

## Returns:
    bool:
        - True if the lowercased file_extension is one of: ".bz2", ".gz", ".xz", ".zip".
        - False otherwise (including when the extension is empty, lacks a leading dot, contains extra whitespace, or is a different suffix).
        - No other return values are possible.

## Raises:
    AttributeError:
        - If the provided file_extension does not support the lower() method (for example, None or an integer), calling file_extension.lower() will raise an AttributeError.
        - The function does not explicitly validate types; callers should ensure file_extension is a string-like object.

## Constraints:
    Preconditions:
        - Caller should pass a string or an object that implements a lower() method returning a comparable string.
        - If using Path.suffix, expect the leading dot to be present (Path.suffix returns '' when there is no suffix).
    Postconditions:
        - The function returns a boolean value and does not modify the input.
        - No side effects or global state changes occur.

## Side Effects:
    - None. The function performs pure computation and does not perform I/O, mutate external state, or call external services.

## Control Flow:
flowchart TD
    A[Start: receive file_extension] --> B{Has lower() method?}
    B -- No --> C[AttributeError propagates to caller]
    B -- Yes --> D[file_extension_lower = file_extension.lower()]
    D --> E{file_extension_lower in supported_list?}
    E -- Yes --> F[Return True]
    E -- No --> G[Return False]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style F fill:#bfb,stroke:#333,stroke-width:1px
    style G fill:#fbb,stroke:#333,stroke-width:1px
    style C fill:#ffdead,stroke:#333,stroke-width:1px

## Examples:
- Common successful case:
    Suppose the caller extracts a suffix ".gz" from a filename. After lowercasing the suffix, the function will return True because ".gz" is in the supported set.

- Case-insensitivity:
    An input ".GZ" (uppercase) will be lowercased and yield True.

- False cases:
    - An empty string '' or a suffix without a leading dot like 'gz' will return False.
    - A suffix with surrounding whitespace such as ' .gz' will return False (the function does not strip whitespace).
    - A non-string value such as None will cause an AttributeError when attempting to call lower().

- Typical integration pattern:
    1) Extract a suffix (for example, via a path object's suffix property or custom parser).
    2) Pass the suffix into this function.
    3) Branch on the boolean result to choose a compressed-file handler or a plain-file handler.

## `src.ydata_profiling.utils.dataframe.remove_suffix` · *function*

## Summary:
Return the input string with a trailing substring removed only when that substring is non-empty and exactly matches the end of the input; otherwise return the input unchanged.

## Description:
A compact utility that centralizes the pattern "remove a suffix if present" and avoids repeated conditional slicing logic at call sites.

Known callers within the provided context:
- No direct callers were found in the supplied file excerpt. Typical usages elsewhere in the codebase include:
  - stripping file extensions from filenames,
  - normalizing column names by removing known suffix tokens,
  - removing processing-specific suffixes (e.g., ".bak", "_copy") after earlier transformations.

Why this is a separate function:
- Encapsulates a small but commonly-repeated conditional pattern, improving readability and reducing duplication.
- Prevents errors that arise from naive slicing (for example, slicing with -0) by treating empty/falsy suffixes as "no-op".
- Provides a single place to document corner cases and expected input types.

## Args:
    text (str):
        The base text value from which a trailing suffix may be removed.
        - Required: should be a Python str (or an object that implements str-like .endswith and supports slicing).
    suffix (str):
        The suffix substring to remove if present.
        - Expected type: str.
        - Allowed values: any non-empty string. Empty string or other falsy values (e.g., '', None, False) are treated as "no suffix" and cause the function to return the original text unchanged.
        - Important interdependency: The function only computes len(suffix) when it actually removes the suffix (i.e., when suffix is truthy and text.endswith(suffix) returns True). Passing non-string or complex types for suffix changes behavior (see Constraints and Raises).

## Returns:
    str:
        - If suffix is truthy and text.endswith(suffix) is True: a new string equal to text with the last len(suffix) characters removed.
        - Otherwise: the original text (unchanged).
    Edge cases:
        - If suffix equals the entire text, returns an empty string.
        - If suffix is longer than text (and therefore cannot match), returns the original text unchanged.
        - If suffix is falsy (e.g., '' or None), returns the original text unchanged.

## Raises:
    AttributeError:
        - If the provided text object does not implement .endswith (for example, passing an integer for text), attempting to call text.endswith(...) will raise AttributeError.
    TypeError:
        - If suffix is provided with a type incompatible with str.endswith for the given text (for example, passing bytes when text is str), text.endswith(suffix) will raise TypeError.
        - If suffix is a tuple of candidate suffixes (a value accepted by str.endswith), the function will call len(suffix) to compute the slice length. This does not raise immediately but is likely a logic error (see Constraints). If len(suffix) cannot be computed, a TypeError will be raised.
    Note:
        - This function does not intentionally raise custom exceptions; the above are exceptions that can be raised by the underlying string operations.

## Constraints:
    Preconditions:
        - text should be a str (or an object with .endswith and slicing behavior compatible with the operation).
        - suffix should be a str. Passing a tuple of strings (which str.endswith accepts) leads to incorrect removals because the function uses len(suffix) (the tuple length) when slicing; do not pass tuples unless you intend that behavior.
    Postconditions:
        - The returned value is a str.
        - If the function removed a suffix, the returned string will not end with the provided suffix (when suffix is a single string).
        - The input string remains unmodified (strings are immutable).

    Gotchas:
        - Tuple suffixes: str.endswith accepts a tuple of suffixes (e.g., ('a', 'b')), and the function will test membership correctly. However, if a tuple match succeeds the code uses len(suffix) (the number of tuple elements) when slicing — not the length of the matched string — which will produce incorrect removal lengths. Example:
            * text = "filename.txt", suffix = (".txt", ".md")
              - text.endswith(suffix) -> True
              - len(suffix) == 2 -> slicing removes 2 characters, producing "filename.t" (incorrect)
          Therefore, callers should pass a single string suffix when they expect removal of a matched suffix.
        - Type mismatches between text and suffix (str vs bytes) will raise TypeError from .endswith.

## Side Effects:
    - None. No I/O, no external state mutation, and no network or service calls.

## Control Flow:
flowchart TD
    Start --> IsSuffixTruthy{Is suffix truthy?}
    IsSuffixTruthy -- No --> ReturnOriginal[Return original text]
    IsSuffixTruthy -- Yes --> HasEndsWith{text.endswith(suffix) ?}
    HasEndsWith -- No --> ReturnOriginal
    HasEndsWith -- Yes --> ComputeLen[Compute n = len(suffix)]
    ComputeLen --> Slice[Return text[: -n]]
    Slice --> End
    ReturnOriginal --> End

## Examples:
    - Typical removal:
        Input: text = "report_2021.csv", suffix = ".csv"
        Output: "report_2021"
    - Suffix not present:
        Input: text = "data_backup", suffix = ".csv"
        Output: "data_backup" (unchanged)
    - Empty suffix:
        Input: text = "note.txt", suffix = ""
        Output: "note.txt" (suffix falsy; no change)
    - Suffix equals full text:
        Input: text = "archive", suffix = "archive"
        Output: "" (empty string)
    - Suffix longer than text:
        Input: text = "x", suffix = "longsuffix"
        Output: "x" (unchanged)
    - Tuple suffix gotcha (do not do this if you expect removal of the matched string):
        Input: text = "file.txt", suffix = (".txt", ".md")
        Behavior:
            - text.endswith(suffix) -> True
            - len(suffix) -> 2
            - Returned value -> "file.t" (incorrect removal of 2 characters rather than 4)
        Recommendation: pass a single string suffix or perform tuple matching outside this function and pass the actual matching string.
    - Defensive calling pattern:
        Try:
            candidate = ".csv"
            if isinstance(text, str) and isinstance(candidate, str):
                cleaned = remove_suffix(text, candidate)
            else:
                cleaned = text
        Except TypeError as e:
            handle_error(e)

## `src.ydata_profiling.utils.dataframe.uncompressed_extension` · *function*

## Summary:
Return the effective (uncompressed) file extension for a Path, resolving common compressed file wrappers (e.g., ".gz", ".zip") to the extension of the underlying file when present.

## Description:
This function determines whether a file's suffix represents a supported compression format and, if so, returns the suffix of the underlying (uncompressed) filename; otherwise it returns the file's suffix itself. Typical callers are file-reading or file-dispatching code that needs to decide how to parse the file contents (for example, to choose between CSV, JSON, or other format readers) and must treat compressed files like "data.csv.gz" as CSVs rather than gz files.

Known callers within the codebase:
- No direct callers were found in the supplied repository scan. Typical usages (where this function belongs conceptually) include:
  - Pre-processing logic that selects a parser/reader based on the file's true data format (e.g., pick CSV handler when uncompressed extension is ".csv").
  - Helper utilities that normalize reported file types for logging or reporting.

Why this is a separate function:
- Encapsulates the common pattern "if compressed, find and return the inner extension" so callers don't repeat composition of Path, lowercasing, compression checks, and suffix removal.
- Ensures consistent case-folding and handling of multi-part filenames (e.g., "archive.tar.gz" -> ".tar") across the codebase.
- Keeps the supported-compression list and the suffix-stripping behavior isolated for easier maintenance and testing.

## Args:
    file_name (pathlib.Path):
        A pathlib.Path object representing the filename or path to inspect.
        - Expected: a Path-like object whose .suffix property yields a string (possibly empty).
        - The function relies on reading file_name.suffix and calling .lower() on that suffix, and on calling str(file_name).lower() for suffix removal in the compressed case.

## Returns:
    str:
        - If the file's last suffix (lowercased) is a supported compression suffix (supported set: ".bz2", ".gz", ".xz", ".zip"), returns the suffix of the filename after removing that compression suffix (the "inner" suffix). The returned inner suffix includes the leading dot (e.g., ".csv", ".tar") or is the empty string '' when there is no inner suffix.
        - If the file's last suffix is not a supported compression suffix, returns that last suffix (lowercased) as-is (including the leading dot, or '' if there is no suffix).
        - Examples of possible outputs: ".csv", ".tar", ".json", "".

## Raises:
    AttributeError:
        - If file_name.suffix does not return a string-like object with a lower() method, calling .lower() will raise AttributeError. This can happen if file_name is not a pathlib.Path or a Path-like object with the standard .suffix behavior.
    TypeError:
        - If the underlying helper remove_suffix or is_supported_compression encounter type mismatches (for example, if they receive a non-string where a string is expected), a TypeError may propagate.
    Note:
        - The function itself does not perform explicit type checks; callers must pass a pathlib.Path or an object compatible with Path.suffix and str(file_name).

## Constraints:
    Preconditions:
        - file_name must be a pathlib.Path (or Path-like) whose .suffix attribute returns a string (possibly '').
        - The file name string representation (str(file_name)) must be convertible to and treatable as a string (so calling .lower() is valid).
    Postconditions:
        - The returned value is a Python str representing a filename suffix (with leading dot) or the empty string.
        - The returned suffix is lowercased (because the function lowercases the suffix and the filename when computing the inner suffix).
        - No mutation of the input object occurs.

## Side Effects:
    - None. The function performs pure computation only (no file/IO/network operations, no global state mutation).

## Control Flow:
flowchart TD
    Start --> GetSuffix[Get suffix = file_name.suffix.lower()]
    GetSuffix --> CheckCompression{is_supported_compression(suffix)?}
    CheckCompression -- No --> ReturnSuffix[Return suffix (lowercased)]
    CheckCompression -- Yes --> LowerName[base = str(file_name).lower()]
    LowerName --> RemoveComp[trimmed = remove_suffix(base, suffix)]
    RemoveComp --> InnerSuffix[inner = Path(trimmed).suffix]
    InnerSuffix --> ReturnInner[Return inner (may be '' or like ".csv")]
    ReturnSuffix --> End
    ReturnInner --> End

## Examples:
    - Compressed file wrapping a known extension:
        Input: Path("data/report.csv.gz")
        Behavior:
            suffix = ".gz" -> supported
            base = "data/report.csv.gz".lower() -> "data/report.csv.gz"
            trimmed = remove_suffix(base, ".gz") -> "data/report.csv"
            inner = Path("data/report.csv").suffix -> ".csv"
        Return: ".csv"

    - Multi-part archive (common tar+gz pattern):
        Input: Path("archive.backup.tar.gz")
        Return: ".tar"

    - Compressed file with no inner extension:
        Input: Path("README.gz")
        Behavior:
            trimmed -> "readme"
            inner = Path("readme").suffix -> ""
        Return: ""

    - Uncompressed file:
        Input: Path("image.PNG")
        Behavior:
            suffix = ".png" (lowercased)
            is_supported_compression(".png") -> False
        Return: ".png"

    - No suffix:
        Input: Path("LICENSE")
        Return: ""

    - Error handling example:
        Try:
            p = Path_like_object  # must present .suffix and be convertible to str
            ext = uncompressed_extension(p)
        Except AttributeError:
            # file_name did not have a string-like suffix or .lower() failed
            handle_invalid_input()

Implementation note for re-creation:
    - Compute extension = file_name.suffix.lower()
    - If the extension is a supported compression (use the same supported set used by is_supported_compression), remove that suffix from the lowercased string form of the path (use a remove_suffix helper that removes the trailing substring only when it exactly matches), then take Path(trimmed).suffix and return it.
    - Otherwise, return extension directly.

## `src.ydata_profiling.utils.dataframe.read_pandas` · *function*

## Summary:
Read a filesystem path into a pandas DataFrame by detecting the file's effective (uncompressed) extension and dispatching to the appropriate pandas read_* function.

## Description:
This function centralizes format detection and dispatch for common tabular and serialized file formats. It resolves compressed wrappers (via uncompressed_extension) so files like "data.csv.gz" are treated as CSVs, then calls the corresponding pandas reader.

Known callers within the codebase:
- No direct callers were discovered in the supplied repository scan. Typical callers include:
  - Data ingestion or profiling pipelines that accept a path and need a DataFrame for analysis.
  - CLI utilities or higher-level helpers that normalize disparate file inputs into a DataFrame for downstream processing.

Why this is a separate function:
- Avoids duplicating format-dispatch logic across the codebase.
- Ensures consistent handling of compressed filenames and of unsupported/unknown extensions.
- Centralizes warning behavior for unexpected extensions and the mapping between extensions and pandas readers.

## Args:
    file_name (pathlib.Path):
        Path-like object pointing to the file to read.
        - Required.
        - Preconditions: file_name must provide a .suffix attribute (string-like) and be convertible to str; uncompressed_extension uses these properties.
        - Not supported: file-like objects (streams); only filesystem path objects are accepted.

Notes about imports and aliasing:
- The implementation calls pandas reader functions through a pd alias (e.g., pd.read_csv). The file-level imports provided in the repository snapshot show "import pandas" (not "import pandas as pd"). If pandas is not actually bound to the name pd in the runtime module scope, calls in this function will raise NameError. This is an implementation inconsistency to be fixed in the codebase (either import pandas as pd or change calls to use the 'pandas' name).

## Returns:
    pandas.DataFrame
        - The DataFrame returned by the pandas reader chosen for the file type.
        - Behavior mirrors the chosen pandas reader: empty files -> empty DataFrame (may raise pandas.errors.EmptyDataError), parsed data -> DataFrame with columns/types inferred by pandas.
        - No alternate sentinel values are returned; parsing or I/O problems raise exceptions.

## Raises:
    ValueError:
        - Raised explicitly when the effective extension is ".tar".
        - Exact message:
          "tar compression is not supported directly by pandas, please use the 'tarfile' module"

    NameError:
        - May be raised indirectly due to two separate implementation issues:
            1) warn_read(extension) currently evaluates a free name f and therefore raises NameError ("name 'f' is not defined") unless a name f is present in scope. This NameError will propagate out of read_pandas when warn_read is invoked for unknown extensions.
            2) If pandas is not bound to pd (see "Notes about imports and aliasing"), the first use of pd.read_* will raise NameError.
        - Callers should be prepared to handle NameError until the underlying implementation bugs are corrected.

    AttributeError:
        - May be raised by uncompressed_extension(file_name) when file_name does not provide a string-like .suffix (e.g., an incompatible object is passed). This AttributeError will propagate.

    TypeError:
        - May be raised by uncompressed_extension or by downstream code if unexpected non-string values are encountered in suffix handling. It will propagate.

    Exceptions from pandas readers and I/O:
        - FileNotFoundError, OSError, pandas.errors.EmptyDataError, ValueError, and other exceptions raised by pandas file readers are not caught and will propagate to the caller.

## Constraints:
Preconditions:
- file_name must be a Path-like object with expected .suffix semantics and str(file_name) valid.
- pandas must be available in the runtime environment, and the module must expose the alias expected by the implementation (pd), otherwise NameError will occur.

Postconditions:
- On success, returns a pandas.DataFrame parsed from the file.
- No modification to the file on disk; no changes to global state within this function.

## Side Effects:
- Performs file I/O by calling pandas reader functions (opens and reads the file).
- Calls warn_read(extension) for unknown non-CSV extensions; intended to emit a warning but may raise NameError because of warn_read's implementation bug.
- No network calls, no writes to databases, and no global state mutations are performed by read_pandas itself.

## Control Flow:
flowchart TD
    Start --> GetExt[extension = uncompressed_extension(file_name)]
    GetExt --> IsJSON{extension == ".json"}
    IsJSON -- Yes --> ReadJSON[pd.read_json(str(file_name))]
    IsJSON -- No --> IsJSONL{extension == ".jsonl"}
    IsJSONL -- Yes --> ReadJSONL[pd.read_json(str(file_name), lines=True)]
    IsJSONL -- No --> IsDTA{extension == ".dta"}
    IsDTA -- Yes --> ReadDTA[pd.read_stata(str(file_name))]
    IsDTA -- No --> IsTSV{extension == ".tsv"}
    IsTSV -- Yes --> ReadTSV[pd.read_csv(str(file_name), sep="\t")]
    IsTSV -- No --> IsXLS{extension in [".xls", ".xlsx"]}
    IsXLS -- Yes --> ReadXLS[pd.read_excel(str(file_name))]
    IsXLS -- No --> IsHDF{extension in [".hdf", ".h5"]}
    IsHDF -- Yes --> ReadHDF[pd.read_hdf(str(file_name))]
    IsHDF -- No --> IsSAS{extension in [".sas7bdat", ".xpt"]}
    IsSAS -- Yes --> ReadSAS[pd.read_sas(str(file_name))]
    IsSAS -- No --> IsParquet{extension == ".parquet"}
    IsParquet -- Yes --> ReadParquet[pd.read_parquet(str(file_name))]
    IsParquet -- No --> IsPickle{extension in [".pkl", ".pickle"]}
    IsPickle -- Yes --> ReadPickle[pd.read_pickle(str(file_name))]
    IsPickle -- No --> IsTar{extension == ".tar"}
    IsTar -- Yes --> RaiseTar[raise ValueError(...)]
    IsTar -- No --> WarnCheck{extension != ".csv"}
    WarnCheck -- Yes --> CallWarn[warn_read(extension)] --> ReadCSV[pd.read_csv(str(file_name))]
    WarnCheck -- No --> ReadCSV
    ReadJSON --> ReturnDF[return df]
    ReadJSONL --> ReturnDF
    ReadDTA --> ReturnDF
    ReadTSV --> ReturnDF
    ReadXLS --> ReturnDF
    ReadHDF --> ReturnDF
    ReadSAS --> ReturnDF
    ReadParquet --> ReturnDF
    ReadPickle --> ReturnDF
    ReadCSV --> ReturnDF

## Examples:
- Basic usage:
    from pathlib import Path
    try:
        df = read_pandas(Path("data/measurements.csv.gz"))
        # df is a pandas.DataFrame with parsed contents
    except FileNotFoundError:
        # file missing: handle or propagate
        raise

- Handling explicit .tar rejection:
    try:
        df = read_pandas(Path("archive/data.tar"))
    except ValueError as e:
        # Message: "tar compression is not supported directly by pandas, please use the 'tarfile' module"
        # Recommended: extract or open the tar with the tarfile module and read inner files explicitly
        raise

- Defensive example for warn_read and pandas alias issues:
    # Because warn_read currently may raise NameError, and because the module uses
    # pd.* readers but the module import may be 'import pandas' (no pd alias),
    # callers that must be robust can guard NameError and fallback manually:
    from pathlib import Path
    import pandas as real_pd

    try:
        df = read_pandas(Path("data/unknown.xyz"))
    except NameError:
        # Attempt fallback: try reading as CSV using a guaranteed pandas alias
        df = real_pd.read_csv(str(Path("data/unknown.xyz")))

## `src.ydata_profiling.utils.dataframe.rename_index` · *function*

## Summary:
Renames any column named "index" to "df_index" and, if the DataFrame's index has a name "index", renames that index name to "df_index"; returns the same DataFrame (mutated in place).

## Description:
This small utility ensures that a DataFrame does not expose the ambiguous reserved name "index" as either a column label or an index name by consistently renaming it to "df_index". This is useful when preparing DataFrames for further processing or serialization where the name "index" would collide with an actual index or reserved field.

Known callers within the repository:
- No callers were discovered during the analysis step (repository-wide search failed). Typical call sites are data preprocessing or profiling pipelines where the code must avoid ambiguous "index" identifiers before downstream consumption (e.g., when converting to JSON/CSV, merging, or hashing). When present, callers will usually pass a pandas DataFrame that may have been constructed or transformed earlier in the pipeline.

Why this function is extracted:
- Encapsulates a single responsibility: normalize the reserved identifier "index" across both columns and index names.
- Keeps calling code concise and avoids repeating the same renaming logic in multiple places.
- Ensures consistent behavior for both single-level and multi-level (MultiIndex) index name renaming.

## Args:
    df (pandas.DataFrame): The target DataFrame to normalize. This argument is required.
        - Expected type: pandas.DataFrame (or an object with a DataFrame-like API implementing .rename and .index.names)
        - No default value.
        - Interdependencies: The function operates in-place on the provided DataFrame; callers should not assume a copy is returned unless they explicitly provide one.

## Returns:
    pandas.DataFrame: The same DataFrame object passed in, after in-place modifications.
        - If the DataFrame had a column labeled "index", that column label will be replaced with "df_index".
        - If the DataFrame's index has one or more names and any name equals the string "index", those names are replaced with "df_index". This applies to single-level and multi-level indexes (index.names is iterated).
        - If neither a column named "index" nor an index name "index" exists, the DataFrame is returned unchanged (still the same object).

## Raises:
    - No exceptions are explicitly raised by this function.
    - Possible exceptions raised by underlying pandas operations:
        * AttributeError or TypeError may occur if the supplied df does not implement the expected DataFrame API (e.g., no .rename or no .index attribute). These originate from pandas internals and are not explicitly handled here.

## Constraints:
Preconditions:
    - Caller must pass a pandas.DataFrame or an object that implements the DataFrame-like interface used (rename method and index.names attribute).
    - Column labels and index names are expected to be strings or objects comparable to the string "index" using equality.

Postconditions:
    - The returned object is the same object as the input df (mutated in-place).
    - All column labels equal to the string "index" are renamed to "df_index".
    - All index names equal to the string "index" are replaced with "df_index" while preserving other index names and their order.
    - No file I/O, network calls, or external state mutations beyond the in-memory DataFrame modification are performed.

## Side Effects:
    - Mutates the passed DataFrame in place:
        * Calls DataFrame.rename(..., inplace=True) to change column names.
        * Assigns to df.index.names to update index names.
    - No external I/O (files, network) or global state modification occurs.

## Control Flow:
flowchart TD
    Start --> RenameColumns
    RenameColumns[Call df.rename(columns={'index':'df_index'}, inplace=True)]
    RenameColumns --> CheckIndexNames
    CheckIndexNames{Is 'index' in df.index.names?}
    CheckIndexNames -- Yes --> ReplaceIndexNames[Set df.index.names = [x if x != 'index' else 'df_index' for x in df.index.names]]
    CheckIndexNames -- No --> SkipReplace[No index-name change]
    ReplaceIndexNames --> ReturnDF
    SkipReplace --> ReturnDF
    ReturnDF[Return df (same object)] --> End

## Examples:
Example 1 — single-level index and a column named "index":
    # Given a DataFrame with a column named "index" and an index named "index"
    # (pseudocode / plain-text):
    df:
        index  val
    idx0   a    1
    idx1   b    2
    df.index.name = "index"

    After calling rename_index(df):
    - The column labeled "index" is now "df_index".
    - The index name "index" is now "df_index".
    - The function returns the same df object (mutated in place).

Example 2 — DataFrame with MultiIndex names:
    - If df.index.names == ['level_0', 'index', 'level_2']
    - After the call, index.names == ['level_0', 'df_index', 'level_2'].

Example 3 — no "index" present:
    - If neither a column label nor an index name equals "index", df is returned unchanged (object identity preserved).

Usage notes:
    - If callers need to keep the original DataFrame unchanged, create a copy before calling (e.g., df.copy()). This function intentionally performs in-place edits.
    - This function performs string-equality checks; non-string index names equal to the string "index" are unlikely, but equality semantics are preserved as implemented.

## `src.ydata_profiling.utils.dataframe.expand_mixed` · *function*

## Summary:
Expands DataFrame columns whose non-missing entries are single-level iterable or mapping containers (lists, tuples, dicts by default) into new prefixed columns; recursion is applied to newly created expanded blocks until no further eligible columns remain.

## Description:
This function scans each column in the provided pandas DataFrame and identifies columns whose non-null entries are of an exact type present in `types` (default: list, dict, tuple) and whose contained elements are not themselves of any type in `types`. For each such column:

1. The non-null values are converted to a pandas DataFrame using .dropna().tolist().
2. New column names are created by prefixing the original column name with an underscore.
3. The function calls itself recursively on the expanded DataFrame to further flatten nested structures.
4. The original column is dropped in-place from the input DataFrame.
5. The expanded block is concatenated to the original DataFrame along axis=1.

Known callers:
- Not referenced elsewhere in this file. Intended to be used before profiling, type inference, or other steps that expect scalar column values.

Responsibility:
- Encapsulates detection and flattening of simple container-valued columns so upstream analysis code can operate on scalar columns without duplicating expansion logic.

## Args:
    df (pd.DataFrame):
        Input DataFrame. Must be a pandas DataFrame. The function will mutate `df` by dropping any original columns that are expanded.
    types (Any, optional):
        Iterable of Python type objects used for detection (default: [list, dict, tuple]).
        - Detection uses exact type equality: type(x) in types (not isinstance). Subclasses or custom sequence types will not match unless added explicitly.
        - The nested check examines elements y produced by iterating x (for dict, iteration yields keys). Therefore, nested checks inspect dict keys, not dict values.

## Returns:
    pd.DataFrame:
        The DataFrame after expansion and concatenation. Notes:
        - The input DataFrame `df` is mutated for columns that are expanded (dropped in-place).
        - New columns are created with names prefixed by "originalColumnName_".
        - Rows that were null for an expanded column will have NaN in the expanded columns only if the expanded block's rows align with those original row indices (see Index / alignment caveat below).
        - If truly no column matches the expansion criterion, the original DataFrame object (possibly unchanged) is returned.

Index / alignment caveat (important):
    - The expanded DataFrame is constructed from df[column].dropna().tolist(), which converts the non-null cell values into a plain Python list and therefore produces a new DataFrame with a fresh RangeIndex (0..m-1). The original row labels (index) of the non-null entries are not preserved in this step.
    - When concatenating the expanded block with the original DataFrame using pd.concat([df, expanded], axis=1), pandas aligns on index labels. Because the expanded block has lost the original row labels, its rows will be aligned to index labels 0..m-1 — which may not correspond to the original rows that produced those values.
    - Practical consequence: unless the original DataFrame already has a RangeIndex that matches the order and labels of the non-null rows (for example, fresh 0..n-1 index and no row filtering), values in the expanded columns may be assigned to incorrect rows after concatenation.
    - Recommended mitigations:
        * If preserving the mapping between original rows and expanded values is required, create the expanded DataFrame with the original non-null index, e.g.:
            expanded = pandas.DataFrame(df[col].dropna().tolist(), index=df[col].dropna().index)
          Then the subsequent concat will align expanded rows to the correct original rows.
        * Alternatively, reset the DataFrame index before calling expand_mixed if appropriate:
            df = df.reset_index(drop=True)
          but be cautious as this changes the original row labels.

## Raises:
    - The function itself does not explicitly raise exceptions. Underlying pandas operations (DataFrame construction, concatenation) may raise exceptions (ValueError, TypeError, MemoryError) which will propagate.

## Constraints:
Preconditions:
    - `df` is a valid pandas DataFrame.
    - If provided, `types` is an iterable of type objects.

Postconditions:
    - Every column for which each non-null value x satisfies type(x) in types and none of the elements y in x satisfy type(y) in types will be removed from `df` and replaced by expanded prefixed columns — except where the empty-column caveat applies (see below).
    - The DataFrame's index labels remain the same (no rows are added/removed), but the mapping of expanded values to original rows is only preserved if the expanded block retains original indices (see Index / alignment caveat).

Special cases:
    - Empty / all-NA columns: df[col].dropna() produces an empty Series; calling .all() on an empty Series returns True in pandas. Therefore, a column that contains only NA values will be considered "expandable" by the current logic: the function will create an empty expanded DataFrame and then drop the original column, resulting in the original column being removed with no replacement columns added. If you need to preserve all-NA columns, filter them out prior to calling expand_mixed.

## Side Effects:
    - Mutates the input DataFrame by dropping expanded columns in-place.
    - No file, network, or external I/O.
    - No changes to global state beyond the passed-in DataFrame mutation.

## Control Flow:
flowchart TD
    Start --> ForEachColumn
    ForEachColumn --> ComputeFlag[Compute non_nested_enumeration = df[col].dropna().map(lambda x: type(x) in types and not any(type(y) in types for y in x))]
    ComputeFlag -->|dropna() yields empty| EmptySeries[.all() == True -> column considered expandable (empty expanded DataFrame)]
    ComputeFlag -->|All True| BuildExpanded[expanded = DataFrame(df[col].dropna().tolist())]
    BuildExpanded --> Prefix[expanded = expanded.add_prefix(col + "_")]
    Prefix --> Recurse[expanded = expand_mixed(expanded)]
    Recurse --> DropOriginal[df.drop(columns=[col], inplace=True)]
    DropOriginal --> Concat[df = pd.concat([df, expanded], axis=1)]
    Concat --> NextColumn
    ComputeFlag -->|Not All True| NextColumn
    NextColumn --> IfMoreColumns{More columns?}
    IfMoreColumns -->|Yes| ForEachColumn
    IfMoreColumns -->|No| ReturnDf[Return df]

## Examples:
- Correct mapping example (preserve row alignment):
    If preserving row alignment is important, construct the expanded block with the original non-null index:
      series_non_null = df["col"].dropna()
      expanded = pandas.DataFrame(series_non_null.tolist(), index=series_non_null.index)
      expanded = expanded.add_prefix("col_")
    Then concatenation will place expanded values into the correct rows.

- Typical usage:
    df = pandas.DataFrame({"id": [1,2,3], "tags": [["a","b"], ["c"], None]})
    Calling expand_mixed(df) will:
      - Drop "tags" and add columns like "tags_0" and "tags_1".
      - Rows with None in "tags" will have NaN in the new columns only if the expansion preserves index alignment; otherwise, see Index / alignment caveat.

- All-NA column:
    df = pandas.DataFrame({"id": [1,2,3], "maybe": [None, None, None]})
    expand_mixed(df) will drop the "maybe" column (no replacement columns will be added). To avoid this, pre-filter or test for df["maybe"].notna().any() before calling expand_mixed.

Error handling guidance:
    - Wrap calls in try/except to catch pandas exceptions when working with irregular or very large data.

## `src.ydata_profiling.utils.dataframe.hash_dataframe` · *function*

## Summary:
Produces a deterministic SHA-256 fingerprint string for a pandas DataFrame by hashing pandas' per-object hashes, concatenating them into a canonical UTF-8 byte sequence, computing the digest, and returning the hex string prefixed with a module-level HASH_PREFIX.

## Description:
This function implements a single, centralized policy for converting a pandas DataFrame into a compact, reproducible identifier:
1. It calls pandas.core.util.hashing.hash_pandas_object(df) to obtain pandas' per-element/row hash values.
2. It converts those hash values to strings (.astype(str)) and joins them using newline characters ("\n") to form a deterministic text representation.
3. It encodes that text as UTF-8 bytes and computes the SHA-256 digest.
4. It returns the digest as a 64-character lowercase hexadecimal string prefixed by a module-level constant HASH_PREFIX.

Known callers (supplied context):
- No call sites were available in the provided context. To discover callers in the repository, search for the symbol "hash_dataframe(".

Why this is a separate function:
- Hashing a DataFrame for identity/versioning is a distinct concern (deterministic serialization → digest → prefixing). Centralizing it prevents duplicated, inconsistent hashing logic and makes it easy to update algorithmic policies (digest algorithm, joiner, prefix) in one place.

## Args:
    df (pd.DataFrame):
        - Type: pandas DataFrame (annotation uses pd.DataFrame).
        - Requirement: The object must be compatible with pandas.core.util.hashing.hash_pandas_object.
        - Note: The module where this function is defined is expected to have the symbol pd bound to the pandas module (e.g., import pandas as pd). If pd is not defined at import time and annotations are evaluated, a NameError may occur when the module is imported.

## Returns:
    str: The fingerprint string composed of HASH_PREFIX followed by the 64-character lowercase SHA-256 hexadecimal digest of the UTF-8 encoded joined per-object hash strings.
    - Format: "<HASH_PREFIX><64-hex-chars>"
    - Length: If HASH_PREFIX is defined, len(returned_string) == len(HASH_PREFIX) + 64.
    - Empty DataFrame behavior: hash_pandas_object yields an empty sequence; joining yields the empty string ""; SHA-256(b"") is the well-known digest:
      e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      So, if HASH_PREFIX == "dfhash:", the function returns:
      "dfhash:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

## Raises:
    NameError:
        - Condition: If the module-level constant HASH_PREFIX is not defined in the module's runtime scope when the function executes, a NameError will be raised when formatting the return value (f"{HASH_PREFIX}{digest}").
        - Also possible at module import time if the annotation pd.DataFrame is evaluated but pd is not defined in the module.
    Any exception from pandas.core.util.hashing.hash_pandas_object:
        - Condition: If pandas encounters an input it cannot hash, or an internal error occurs, that exception (e.g., TypeError, ValueError) will propagate to the caller.
    (Note: hashlib.sha256 on bytes will not raise under normal, documented conditions for valid bytes input.)

## Constraints:
Preconditions:
    - The pandas hashing routine (pandas.core.util.hashing.hash_pandas_object) must be available and accept the provided df.
    - The module must define HASH_PREFIX before this function is called (or the caller must be prepared to catch NameError).
    - The symbol pd referenced in the annotation should resolve to the pandas module in the module namespace (common pattern: import pandas as pd).
Postconditions:
    - The input DataFrame is not mutated.
    - The returned fingerprint is deterministic for identical DataFrame content and structure, provided pandas' hashing behavior and the module-level policies remain unchanged.

## Side Effects:
    - None: The function performs no file I/O, network I/O, or global state mutation.
    - It reads the DataFrame and module-level constants only.

## Performance and resource notes:
    - Memory: The function materializes a joined string containing one stringified hash per value/row returned by hash_pandas_object. For very large DataFrames this string may be large; callers should be aware of memory consumption.
    - Time: The cost is dominated by pandas' hashing routine and the SHA-256 computation; for extremely large DataFrames, consider hashing a canonical serialized form in a streaming fashion if memory is a constraint.

## Control Flow:
flowchart TD
    A[Start: call hash_dataframe(df)] --> B[Call hash_pandas_object(df)]
    B --> C{hash_pandas_object returns sequence/Series or raises?}
    C -->|Raises| D[Exception propagates to caller]
    C -->|Returns (including empty sequence)| E[Convert values to strings (.astype(str))]
    E --> F[Join strings with "\n" to produce single text]
    F --> G[Encode text as UTF-8 bytes]
    G --> H[Compute hashlib.sha256 digest]
    H --> I[Convert digest to 64-char lowercase hex]
    I --> J{Is HASH_PREFIX defined in module scope?}
    J -->|Yes| K[Return HASH_PREFIX + digest]
    J -->|No| L[NameError at formatting time -> exception propagates]
    K --> M[End]
    L --> M

## Examples:
Example 1 — Typical successful usage (module must define HASH_PREFIX and pd alias):
    # In the module defining hash_dataframe:
    # import pandas as pd
    # HASH_PREFIX = "dfhash:"
    import pandas as pd
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    fingerprint = hash_dataframe(df)
    # fingerprint -> "dfhash:" + 64-char hex digest

Example 2 — Concrete empty-DataFrame fingerprint:
    # HASH_PREFIX = "dfhash:"
    import pandas as pd
    empty = pd.DataFrame()
    fingerprint = hash_dataframe(empty)
    assert fingerprint == "dfhash:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

Example 3 — Recovering if HASH_PREFIX is missing:
    import pandas as pd
    from pandas.core.util.hashing import hash_pandas_object
    import hashlib
    df = pd.DataFrame({"a": [1]})
    try:
        fingerprint = hash_dataframe(df)
    except NameError:
        # Recreate the digest logic and apply a fallback prefix
        values = "\n".join(hash_pandas_object(df).values.astype(str))
        digest = hashlib.sha256(values.encode("utf-8")).hexdigest()
        fingerprint = f"fallback:{digest}"

Notes and caveats:
    - The fingerprint depends on pandas' hash_pandas_object behavior: changes in pandas version, hashing internals, DataFrame column order, index, or dtype representations will change the fingerprint for the same logical data. For reproducibility across environments, normalize column order and dtypes and ensure consistent pandas versions.
    - Prefer using this centralized function rather than reimplementing hashing logic to avoid accidental divergence in fingerprint format.

## `src.ydata_profiling.utils.dataframe.slugify` · *function*

*No documentation generated.*

## `src.ydata_profiling.utils.dataframe.sort_column_names` · *function*

## Summary:
Return a new mapping with the same items but with keys ordered according to the requested sort direction (case-insensitive ascending or descending). If no sort direction is provided, the original mapping is returned unchanged.

## Description:
This small utility centralizes the logic for optionally ordering a mapping of column names (or other string keys) by key name in a case-insensitive manner.

Known callers within the provided code context:
- No direct callers were identified in the provided repository snapshot for this task. Typical callers (not explicitly present here) are report generators or metadata-assembly routines that prepare column-level dictionaries for deterministic presentation or comparison.

Why this logic is factored out:
- It isolates the decision and implementation of string-key ordering (including the case-insensitive comparison rule) so callers do not need to duplicate sorting logic or remember the allowed sort value semantics. It enforces a clear contract for accepted sort values and provides a single place to change ordering behavior (e.g., the normalization strategy) if needed.

## Args:
    dct (dict):
        A mapping (expected to be a dict or dict-like object with an items() method) whose iteration order may be adjusted and then returned as a new dict. Keys are expected to be strings (or objects providing a casefold() method) because the sort uses key.casefold() to perform a case-insensitive sort.
    sort (Optional[str]):
        One of:
          - None: do not change order; return the input mapping as-is.
          - A string starting with "asc" (case-insensitive), e.g. "asc", "ascending": sort keys in case-insensitive ascending order.
          - A string starting with "desc" (case-insensitive), e.g. "desc", "descending": sort keys in case-insensitive descending order.
        Any other non-None value will cause a ValueError.

Notes on parameter interdependencies:
- The function treats None specially; if sort is None no validation of the string content occurs and the input mapping is returned unchanged.
- The function performs case-insensitive checks using Python string lower()/startswith() semantics on the provided sort argument.

## Returns:
    dict:
        A new dict containing the same key-value pairs as the input mapping but with insertion order adjusted according to the requested sorting:
          - If sort is None: returns the original mapping object unchanged (the original object is returned by reference).
          - If sort requests ascending/descending: returns a newly created dict built from sorted(dct.items()) so the returned dict has items in the requested order (Python 3.7+ maintains insertion order).
        Edge cases:
          - If the input mapping has non-string keys (or keys without casefold), attempting to sort will raise an attribute-related error (see Raises).

## Raises:
    ValueError:
        Raised when sort is not None and does not start with "asc" or "desc" (case-insensitive). Exact trigger: after lowering the sort string, neither sort.startswith("asc") nor sort.startswith("desc") is true.
    AttributeError (or similar):
        If the mapping contains keys that do not support the casefold() method (for example, integer keys), the lambda used as the sort key will attempt to call casefold() on such a key and that call will raise AttributeError. This is not explicitly caught by the function.
    TypeError:
        If the provided dct is not a mapping-like object that supports items() or is otherwise non-iterable in the expected way, Python's sorted() or dict() calls may raise TypeError.

## Constraints:
Preconditions:
- Caller should pass a mapping (preferably an actual dict) whose keys are strings or otherwise implement a Unicode casefold() method.
- If sort is not None, it must be a string-like object; the function uses .lower() and .startswith() on it.

Postconditions:
- If sort is None: the original object passed as dct is returned unchanged.
- If sort requests ordering: a new dict is returned whose iteration order (insertion order) reflects the requested case-insensitive ordering of keys.
- The returned dict contains exactly the same key-value pairs as the input mapping (no items are added or removed).

## Side Effects:
- The function performs no I/O, network calls, or global-state mutation.
- It does not modify the input mapping when sorting is requested; instead it creates and returns a new dict. (If sort is None it returns the original mapping object by reference.)
- No external services or caches are touched.

## Control Flow:
flowchart TD
    Start --> CheckSortIsNone
    CheckSortIsNone{sort is None?}
    CheckSortIsNone -- Yes --> ReturnOriginal[Return original mapping]
    CheckSortIsNone -- No --> LowerCaseSort[sort = sort.lower()]
    LowerCaseSort --> IsAsc{sort.startswith("asc")?}
    IsAsc -- Yes --> SortAsc[Sort items by key.casefold() ascending]
    SortAsc --> ReturnSortedAsc[Return new dict(sorted ascending)]
    IsAsc -- No --> IsDesc{sort.startswith("desc")?}
    IsDesc -- Yes --> SortDesc[Sort items by key.casefold() descending]
    SortDesc --> ReturnSortedDesc[Return new dict(sorted descending)]
    IsDesc -- No --> RaiseErr[Raise ValueError('"sort" should be "ascending", "descending" or None.')]
    RaiseErr --> End
    ReturnOriginal --> End
    ReturnSortedAsc --> End
    ReturnSortedDesc --> End

## Examples:
- Typical usage (conceptual representation):
  Input mapping: {'b': 1, 'A': 2, 'c': 3}

  - No sorting requested:
    Call: sort = None
    Result: returns the original mapping object unchanged (iteration order preserved as input).

  - Ascending (case-insensitive):
    Call: sort = "ascending"
    Result: returned dict iteration order: 'A' (2), 'b' (1), 'c' (3)

  - Descending (case-insensitive):
    Call: sort = "desc"
    Result: returned dict iteration order: 'c' (3), 'b' (1), 'A' (2)

- Error cases:
  - Invalid sort string:
    If sort = "random", the function raises ValueError because the lowered value does not start with "asc" or "desc".
  - Non-string keys:
    If mapping contains a key 1 (integer), the function will attempt to call casefold() on that key during sorting and will raise an AttributeError (or a similar attribute-related exception). To avoid this, ensure keys are strings before calling this function.

