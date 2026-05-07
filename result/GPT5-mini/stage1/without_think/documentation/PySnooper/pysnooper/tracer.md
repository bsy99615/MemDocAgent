# `tracer.py`

## `pysnooper.tracer.get_local_reprs` · *function*

## Summary:
Produce an OrderedDict snapshot of a frame's local variables (converted to compact single-line strings) in a stable source-code-derived order and then merge in any additional watched variable items; keys are display names and values are the captured representations or raw watched values.

## Description:
- Known callers and context:
    - Intended for use by tracer logic that captures and formats a frame's state for logging. It is called when preparing a single-line display of locals plus any configured "watch" variables for that frame.
- Responsibility boundary:
    - Build a deterministic ordering for frame locals, convert each local value to a compact single-line textual representation using utils.get_shortish_repr, and then merge in extra (display_name, value) items produced by watch variables. It does not itself perform normalization/truncation logic beyond delegating to utils.get_shortish_repr nor does it evaluate watched-variable expressions (the watch objects do that).
- Why this logic is an extracted function:
    - Centralizes ordering, compactification of local values, and deterministic merging of watched items so tracer code can call a single API to get a display-ready mapping of names -> values.

## Args:
    frame (frame object)
        - A Python frame object. The function reads frame.f_code and frame.f_locals.
    watch (iterable of BaseVariable-like objects, default=())
        - Iterable of variable specification objects; each must implement items(frame, normalize) and return an iterable of (display_name: str, value) tuples.
        - Each watch object's items(...) may return values of any type; this function does not coerce or stringify those values.
    custom_repr (iterable, default=())
        - Forwarded to utils.get_shortish_repr for producing representations of frame local values. Must conform to get_shortish_repr/get_repr_function expectations.
    max_length (int or None, default=None)
        - Forwarded to utils.get_shortish_repr. Truncation occurs only when max_length is truthy.
    normalize (bool, default=False)
        - Forwarded both to utils.get_shortish_repr (for local value representation) and to variable.items(frame, normalize) (for watched variable normalization of names/values when supported).

## Returns:
    collections.OrderedDict[str, Any]
        - Mapping from display name to captured value. For plain frame locals, the values are strings returned by utils.get_shortish_repr(value, custom_repr, max_length, normalize). For items produced by watch variables, the values are exactly the values returned by variable.items(frame, normalize) (they are not passed through get_shortish_repr by this function).
        - Ordering specifics:
            1. All frame locals appear first in the OrderedDict in the order determined by vars_order (see "Ordering details").
            2. After that, for each variable in watch (iterated in the order provided by the watch iterable), the function obtains that variable's items(frame, normalize), sorts those items by display_name (lexicographically), and then calls result.update(sorted_items). The sorted watched items are appended/merged in that sequence.
            3. If a watched item's display_name duplicates an existing key (from locals or a prior watched variable), its value replaces the previous value and the key's position ends up among the watched items (i.e., effectively moved to the point where the update inserted it — typically the end of the OrderedDict after locals).

## Raises:
    - AttributeError (propagates) if frame lacks expected attributes (f_code or f_locals).
    - Any exception raised by utils.get_shortish_repr during local value conversion (e.g., exceptions from normalization or truncation) will propagate.
    - Any exception raised by iterating or invoking variable.items(frame, normalize) for a watched variable will propagate (e.g., TypeError, AttributeError, KeyError raised by the watched variable implementation).
    - TypeError if watch is not iterable.
    - The sorting of locals uses vars_order.index(name); in normal operation vars_order includes all keys from frame.f_locals (because tuple(frame.f_locals.keys()) is appended), so index lookup should succeed; if frame.f_locals changes between building vars_order and sorting (highly unusual), index lookups could theoretically fail and raise ValueError.

## Constraints:
- Preconditions:
    - frame must be a normal Python frame exposing f_code and a mapping f_locals.
    - custom_repr must be acceptable to get_shortish_repr; otherwise utils.get_shortish_repr may raise.
    - Each element in watch must implement items(frame, normalize) and return an iterable of (str, Any) pairs.
- Postconditions:
    - Returns an OrderedDict whose keys are strings (display names) and whose values are either compact repr strings for locals or raw values from watch items.
    - The function does not mutate frame contents; any mutation would originate from called functions (repr functions or variable.items).

## Side Effects:
    - No direct I/O or global state mutation by this function itself.
    - Side effects may occur via:
        * utils.get_shortish_repr, which calls a selected repr function (user-provided callables may have side effects).
        * watched variable .items(...) implementations, which evaluate expressions and may execute arbitrary code.
    - Any exceptions or side effects from callee callables propagate outward.

## Control Flow:
flowchart TD
    Start[Start] --> ReadFrame["Read frame.f_code and frame.f_locals"]
    ReadFrame --> BuildOrder["vars_order = co_varnames + co_cellvars + co_freevars + tuple(f_locals.keys())"]
    BuildOrder --> MapLocals["For each (name,value) in frame.f_locals: call utils.get_shortish_repr(value, custom_repr, max_length, normalize)"]
    MapLocals --> CollectList["Collect (name, repr_str) pairs"]
    CollectList --> SortByOrder["Sort list by vars_order.index(name)"]
    SortByOrder --> MakeOrdered["result = OrderedDict(sorted_list)"]
    MakeOrdered --> ForEachWatch["For each variable in watch (in provided order)"]
    ForEachWatch --> CallItems["  items = variable.items(frame, normalize)"]
    CallItems --> SortItems["  sorted_items = sorted(items)  (lexicographic by display name)"]
    SortItems --> UpdateResult["  result.update(sorted_items)  (overwrites existing keys; updated keys move to insertion position)"]
    UpdateResult --> LoopEnd{"more variables?"}
    LoopEnd -- yes --> ForEachWatch
    LoopEnd -- no --> ReturnResult["return result"]
    ReturnResult --> End[End]

## Examples:
- Basic snapshot:
    - Call: result = get_local_reprs(frame, watch=(), custom_repr=(), max_length=80, normalize=False)
    - Behavior: result contains each local name -> compact single-line repr string, ordered by the function's code-variable order then any extra locals.

- With watched variable that yields extra items:
    - Suppose watch contains a variable v whose items(...) returns [("user.name", "Alice"), ("user.email", "a@b")].
    - The resulting OrderedDict will contain all locals (repr strings) followed by ("user.email" -> "a@b"), ("user.name" -> "Alice") (watched items are sorted lexicographically by name before insertion). If either name conflicted with a local, the watched item's value replaces the local's value and the key appears in the watched-items position.

- Defensive caller pattern:
    - Because get_local_reprs can propagate exceptions from repr normalization/truncation and from watched-variable evaluation, callers that must be robust should wrap the call in try/except and fall back to a simpler capture if an exception occurs (for example, calling get_local_reprs with custom_repr=() and normalize=False or returning an empty OrderedDict).

## `pysnooper.tracer.UnavailableSource` · *class*

## Summary:
A minimal fallback sequence-like object representing an unavailable source; indexing it always yields the Unicode message "SOURCE IS UNAVAILABLE".

## Description:
This class is used as a sentinel/fallback when the original source text (for example, the lines of a file or source block) cannot be loaded or made available to the tracer. Instead of raising errors when client code attempts to access source lines by index, an instance of this class provides a stable, predictable response indicating the source is unavailable.

Typical instantiation scenario:
- Created when a tracer component attempts to load the source for a file but fails (file missing, permission denied, code packaged in a way that prevents access, etc.). Client code that expects a container of source lines can accept this object as a drop-in replacement to avoid additional conditional logic.

Motivation and responsibilities:
- Provide a minimal, safe object that implements the subscription (__getitem__) interface expected of a source-lines container.
- Avoid raising exceptions on access; always return a clear sentinel string to indicate missing source.
- Keep the object stateless and thread-safe.

## State:
- Attributes: This class defines no instance attributes and holds no internal state.
- Type: Instances are plain Python objects (instances of the class).
- Valid values: There are no mutable attributes; the instance is effectively immutable and stateless.
- Invariants:
  - For any instance, calling __getitem__ with any argument must always return the exact Unicode string SOURCE IS UNAVAILABLE.
  - There are no side effects from calling __getitem__.

## Lifecycle:
- Creation:
  - No __init__ parameters are required. Instantiate with the default constructor (no arguments).
  - There are no factory methods in this class; instantiation is direct and trivial.
- Usage:
  - The only exposed capability is subscript access via the indexing protocol. Any code that would normally index a sequence of source lines can index this instance instead.
  - The expected call pattern is: create instance -> perform zero or more index operations -> discard instance. There is no required sequencing between calls; calls may occur in any order and concurrently from multiple threads.
- Destruction / cleanup:
  - No cleanup is necessary. The object holds no resources and requires no explicit close(), context-manager, or destructor logic.

## Method Map:
flowchart TD
    A[Client code] --> B[UnavailableSource instance]
    B --> C[__getitem__(index)]
    C --> D["Returns Unicode string: 'SOURCE IS UNAVAILABLE'"]
    note right of C["__getitem__"]: Accepts any index type (int, negative int, slice, etc.)\nAlways returns same sentinel string

## Methods (behavioral contract):
- __getitem__(self, i)
  - Purpose: Provide an element lookup compatible with sequence-like access.
  - Accepted inputs: Any object passed as an index (commonly int or slice). The method does not inspect or validate the argument.
  - Output: Always returns the Unicode string SOURCE IS UNAVAILABLE (exact sequence of characters, encoded as a Python str in both Python 3 and Python 2 contexts where u'' is supported).
  - Side effects: None.
  - Exceptions: This method does not raise any exceptions; it swallows any index input and returns the sentinel string.

## Thread-safety:
- Because instances are stateless and __getitem__ does not modify or depend on mutable state, the class is safe for concurrent use from multiple threads.

## Raises:
- __init__: does not raise.
- __getitem__: does not raise for any input — it always returns the sentinel string.

## Example (descriptive):
- Create an instance with the default constructor. Use the instance anywhere a sequence of source lines would be used; when the code requests an item by index or a slice, the returned value will be the Unicode string SOURCE IS UNAVAILABLE. Multiple accesses, negative indices, or slice objects all produce the same sentinel value. No cleanup is necessary; simply drop references when finished.

### `pysnooper.tracer.UnavailableSource.__getitem__` · *method*

## Summary:
Returns a constant sentinel string indicating that source text is not available; the call has no effect on the object's state.

## Description:
This method provides a mapping-like access point that always yields a fixed message when source lines are requested but unavailable. It is typically used as a sentinel object where code expects an indexable source (for example, when a tracer or debugger attempts to look up source lines for display) so that callers can index into a source-like object without raising exceptions.

Known callers:
- None found in the provided snippet of pysnooper.tracer. In the broader design, callers are expected to be tracing/logging code paths that obtain source lines by indexing a source object.

Why this is a separate method:
- Encapsulates sentinel behavior behind the indexing operator so callers can treat this object like a real sequence of lines (supporting source[i]) without branching on availability. Keeping the logic here avoids repeated checks at every call site and centralizes the sentinel text.

## Args:
    i (any): Index or slice passed by the caller (int, slice, or any object accepted by Python's __getitem__ protocol). The value is ignored by this implementation.

## Returns:
    str: The unicode string 'SOURCE IS UNAVAILABLE' (literal u'SOURCE IS UNAVAILABLE'). Always returns this exact string for any input.

## Raises:
    None: This method does not raise any exceptions for any input.

## State Changes:
    Attributes READ:
        - None (the method does not read any self.<attr> attributes).
    Attributes WRITTEN:
        - None (the method does not modify any self.<attr> attributes).

## Constraints:
    Preconditions:
        - The caller may assume it holds a reference to an instance of this class; no other preconditions are required.
    Postconditions:
        - The returned value is the constant u'SOURCE IS UNAVAILABLE'.
        - The UnavailableSource instance is unchanged by the call.

## Side Effects:
    - None. No I/O, no external calls, and no mutation of objects outside self.

## `pysnooper.tracer.get_path_and_source_from_frame` · *function*

## Summary:
Resolve a frame's filename and load the corresponding source lines (as a sequence of text lines), returning a tuple of (file_path, source_lines) while caching the result for future lookups.

## Description:
This function accepts a Python frame object and attempts to locate and load the textual source corresponding to that frame. It first consults an in-memory cache keyed by (module_name, file_name); if absent it tries several strategies in order:

- Ask the module loader for source (via loader.get_source(module_name)).
- For IPython "input" pseudo-files, retrieve the cell contents from IPython's history manager.
- For paths that refer to files inside an archived Ansible-style zip path, extract the file from the archive.
- As a fallback, read the file from disk in binary mode.

If none of the strategies produce source lines, an UnavailableSource sentinel instance is returned as the "source" element.

Why this is a separate function:
- The logic for locating and normalizing source from multiple runtime contexts (import loaders, IPython cells, zip archives, plain files) is non-trivial and reused by tracer functionality when mapping frames to human-readable source lines. Extracting it makes the tracer core easier to read, test, and reuse; it isolates caching and source-normalization behavior from the rest of the tracing logic.

Known callers and typical call context:
- Typical usage is internal to a tracer: when a frame is being inspected to generate a trace event, this function is called with that frame to obtain the file path and sequence of source lines for display or annotation.
- The exact callers in this codebase are not available in the provided context; implementers should expect it to be invoked with live frame objects (for example, frames obtained from a trace event handler or inspect.currentframe()).

## Args:
    frame (types.FrameType):
        - A live Python frame object. Expected to provide at least:
            * frame.f_globals (a dict-like mapping of the frame's global variables)
            * frame.f_code.co_filename (a string path used to identify the file)
        - Interdependencies:
            * The function reads frame.f_globals to obtain '__name__' and '__loader__'.
            * If frame.f_globals is falsy, an empty dict is used.

## Returns:
    tuple[str, Sequence[str] or UnavailableSource]:
        - (file_name, source)
        - file_name: The filename string extracted from frame.f_code.co_filename (unchanged).
        - source: One of:
            * A list (or other sequence) of Unicode text lines (str) representing the source, typically created by splitting text by line boundaries.
            * An UnavailableSource instance (sequence-like sentinel) if the source could not be retrieved by any strategy.
        - Notes on variations:
            * When the loader or file read returns binary lines (bytes), the function attempts to detect encoding from a "coding" header in the first two lines and decodes all lines into text using the detected encoding (errors replaced). This yields a sequence of text strings (str).
            * If loader.get_source returns a single string, it is split into lines before returning.

## Raises:
    - NameError:
        * If required module-level globals referenced by the function (for example source_and_path_cache, ipython_filename_pattern, ansible_filename_pattern, UnavailableSource, utils, pycompat) are not defined in the module namespace, calling this function will raise NameError. The function assumes these names exist at module scope.
    - AttributeError / TypeError:
        * If the supplied frame does not provide the attributes the function expects (f_globals, f_code.co_filename), attribute access will raise AttributeError or TypeError.
    - The function intentionally suppresses many lower-level exceptions during source retrieval:
        * loader.get_source: ImportError is caught and ignored.
        * IPython history access, zipfile archive read, and file open/read: exceptions during these retrieval attempts are caught and ignored so that the function can proceed to other strategies. These exceptions are not surfaced by this function.
    - Any other exception raised by external operations that the function does not catch (for example, if module-level cache assignment raises) will propagate.

## Constraints:
    Preconditions:
        - Module-level dependencies must exist:
            * source_and_path_cache: a mutable mapping (supports __getitem__ and __setitem__) used for caching results keyed by (module_name, file_name).
            * ipython_filename_pattern: a compiled regular expression whose .match(file_name) returns None or a match with group(1) giving an entry number for IPython history.
            * ansible_filename_pattern: a compiled regular expression used to detect Ansible zip-style filenames and capture archive path and internal member name.
            * UnavailableSource: a sentinel class (sequence-like) returned when no source is available.
            * utils.file_reading_errors: an exception tuple (or single exception) listing exceptions to ignore when opening files.
            * pycompat.text_type: a callable that converts a bytes line and (encoding, errors) into a text string; used to normalize binary lines to text.
        - The caller must supply a valid frame object (see Args).
    Postconditions:
        - After return, the module-level cache source_and_path_cache will contain an entry mapping the computed cache_key to the returned (file_name, source) tuple.
        - The returned source will be a sequence that is safe to index. If no real source was found, the sequence will be an UnavailableSource instance.

## Side Effects:
    - Mutates module-level cache: writes to source_and_path_cache[ (module_name, file_name) ].
    - Performs I/O:
        * May open files on disk in binary mode (open(file_name, 'rb')).
        * May open and read a zip archive when an ansible-style path is detected.
        * May call IPython.get_ipython() and interact with the IPython history manager to obtain a historical input cell.
    - Imports:
        * The function performs local imports (IPython, zipfile) inside branches; those imports have the usual import side effects (module initialization) the first time they run.
    - No network or external database calls are made by the function itself, but it does interact with IPython runtime state and the filesystem.

## Control Flow:
flowchart TD
    A[Start: receive frame] --> B[globs = frame.f_globals or {}]
    B --> C[module_name = globs.get('__name__')]
    C --> D[file_name = frame.f_code.co_filename]
    D --> E[cache_key = (module_name, file_name)]
    E --> F{Is cache_key in source_and_path_cache?}
    F -- Yes --> G[Return cached (file_name, source)]
    F -- No --> H[loader = globs.get('__loader__')]
    H --> I{loader has get_source?}
    I -- Yes --> J[Call loader.get_source(module_name) (ImportError ignored)]
    J --> K{source is not None?}
    K -- Yes --> L[source = source.splitlines()]
    K -- No --> M[Proceed to filename-based strategies]
    I -- No --> M
    M --> N[ipython_filename_match = ipython_filename_pattern.match(file_name)]
    M --> O[ansible_filename_match = ansible_filename_pattern.match(file_name)]
    N -- Match --> P[Retrieve cell from IPython history (exceptions ignored) -> source = chunk.splitlines()]
    N -- No --> Q{ansible_filename_match?}
    Q -- Yes --> R[Open zip archive and read member (exceptions ignored) -> source = bytes.splitlines()]
    Q -- No --> S[Try open(file_name, 'rb') and read().splitlines() (file errors ignored)]
    S --> T{source truthy?}
    T -- No --> U[source = UnavailableSource()]
    T -- Yes --> V[If source[0] is bytes -> detect encoding in first two lines; decode all lines via pycompat.text_type(...)]
    V --> W[result = (file_name, source)]
    W --> X[source_and_path_cache[cache_key] = result]
    X --> G[Return result]

## Examples (conceptual, end-to-end usage and error handling):
- Typical trace-time usage:
    1. A tracer receives a trace event containing a frame object for the currently executing function.
    2. It calls this function with that frame to obtain (file_path, source_lines).
    3. If source_lines is an UnavailableSource instance, the tracer displays a standardized "SOURCE IS UNAVAILABLE" message when attempting to show source context; otherwise it indexes source_lines by line number to show surrounding lines.

- Error-handling notes for callers:
    * Protect callers against NameError if the module-level environment is not initialized:
        - Before calling, ensure the tracer module has been properly initialized and its module-level dependencies (cache, regex patterns, utils, pycompat) are present.
    * If the caller can receive malformed frames, wrap the call in try/except AttributeError to handle cases where expected frame attributes are missing.

- Reimplementation checklist (what to implement to match behavior):
    * Maintain a module-level cache mapping (module_name, file_name) to (file_name, source).
    * Use loader.get_source(module_name) if available (ignore ImportError).
    * Detect IPython pseudo-filenames and query IPython's history_manager.get_range for the cell text (silently ignore errors when IPython is not available or history access fails).
    * Detect archive-style filenames and open the archive to read the named member (silently ignore errors).
    * Attempt to read the file from disk in binary mode; ignore defined file-reading exceptions.
    * If no source found, return an UnavailableSource sentinel instance for source.
    * If the first element of the source sequence is bytes, inspect the first two lines for an encoding declaration (PEP 263 style), decode using that encoding (fall back to 'utf-8'), and produce text (str) lines; replace undecodable bytes rather than raising.
    * Cache the final (file_name, source) before returning.

## `pysnooper.tracer.get_write_function` · *function*

## Summary:
Returns a callable "write" function that emits text to the configured output target (stderr, a filesystem path, a provided callable, or a writable stream), enforcing the rule that overwrite=True is only valid for file paths.

## Description:
This helper centralizes the logic for converting a user-specified output target into a single-argument text-writing callable.

Typical callers:
- Tracing or logging setup code that needs a uniform write(s) function to emit lines or fragments of trace output without caring about the concrete destination.
- Functions that accept an "output" parameter (None, path, callable, or stream) and want to normalize it to a function they can call repeatedly.

No concrete callers were retrieved during this documentation run; use cases above describe the common contexts in which this function is invoked.

Responsibility boundary:
- Determine the kind of `output` and return a corresponding write(s: str) -> None callable.
- Validate the interaction between `output` and `overwrite` (i.e., only allow overwrite=True when writing to a path).
- Do not perform any file I/O itself except via the returned callable; constructing a FileWriter instance is allowed (it does not touch the filesystem), but get_write_function does not open files.

Why extracted into its own function:
- Keeps destination-dispatch logic in one place (path vs stream vs callable vs default stderr).
- Makes caller code simpler: callers obtain a write function once and then call it repeatedly.
- Encapsulates small compatibility and fallback behaviors (stderr Unicode fallback, FileWriter instantiation).

## Args:
    output (None | pycompat.PathLike | str | callable | utils.WritableStream):
        - Allowed forms:
            * None — produce a write function that writes to sys.stderr with a Unicode-encoding fallback.
            * Path-like (pycompat.PathLike or str) — a filesystem path; returns FileWriter(path, overwrite).write.
            * callable — any callable used directly as the write function.
            * utils.WritableStream — an object with a write(s) method; a wrapper function calling output.write(s) will be returned.
        - Notes:
            * When `output` is a path-like object, it is passed to FileWriter which will convert it with pycompat.text_type. FileWriter.__init__ may raise errors if pycompat.text_type(path) raises.
            * If `output` is a callable, no signature validation is performed; callers should ensure the callable accepts a single text argument.
    overwrite (bool):
        - Determines whether the first successful write to a file path should open the file in 'w' (overwrite) mode instead of 'a' (append).
        - Allowed values: True or False (truthy/falsey accepted).
        - Interdependency: overwrite=True is only valid when `output` is path-like. Passing overwrite=True with a non-path-like output triggers an immediate Exception.

## Returns:
    callable write(s: str) -> None
        - A callable that accepts a single text argument `s` (native text/str) and writes it to the configured destination.
        - Possible concrete returned callables:
            * A function that writes to sys.stderr (when output is None). This function handles UnicodeEncodeError by transforming s via utils.shitcode(s) and retrying the write.
            * The bound method FileWriter(...).write (when output is a path-like). That method performs UTF-8 text writes to the filesystem and may raise I/O exceptions.
            * The original callable provided as `output` (when output is callable). No wrapping is done.
            * A wrapper function that calls output.write(s) (when output is a utils.WritableStream).
        - Edge cases:
            * If the returned callable is the FileWriter.write bound method, calling it may perform filesystem I/O and raise IOError/OSError/PermissionError, etc.
            * If the returned callable is a wrapper around output.write, that underlying write may raise whatever exceptions the stream implementation raises.
            * The returned callable assumes `s` is a text string; passing bytes may raise TypeError in text-mode file writes.

## Raises:
    Exception:
        - Condition: if overwrite is truthy and `output` is not a path-like object (neither pycompat.PathLike nor str).
        - Message (exact): '`overwrite=True` can only be used when writing content to file.'
    AssertionError:
        - Condition: reached when `output` is not None, not path-like, not callable, and failing the runtime assert that it is an instance of utils.WritableStream.
        - This assertion is the code's safeguard; callers may prefer to pass a valid utils.WritableStream to avoid the assertion.
    Indirect exceptions:
        - Constructing FileWriter(output, overwrite) may raise exceptions propagated from pycompat.text_type(output) (e.g., TypeError) during path normalization. These are not raised directly by get_write_function but by FileWriter.__init__.
        - No file I/O happens inside get_write_function itself beyond instantiating FileWriter; I/O exceptions arise when the returned write callable is invoked.

## Constraints:
    Preconditions:
        - The caller must pass valid types for `output` as described above.
        - If overwrite=True, `output` must be a path-like object (pycompat.PathLike or str).
    Postconditions:
        - The function returns a callable that will accept a single text string and attempt to write it to the chosen destination.
        - If a FileWriter instance is returned (bound method), that FileWriter has been constructed and holds the initial overwrite flag until its first successful write.

## Side Effects:
    - get_write_function itself:
        * May instantiate a FileWriter object when `output` is path-like; FileWriter.__init__ performs only path normalization and does not touch the filesystem.
        * No other I/O or global state mutation occurs at call time.
    - The returned callable:
        * May perform I/O (writing to stderr, files, or a user-supplied stream) and may mutate external state (create or modify files, mutate stream buffers).
        * The stderr-branch swallow/handles UnicodeEncodeError by calling utils.shitcode(s) and writing that; this is a secondary write attempt to sys.stderr.

## Control Flow:
flowchart TD
    Start([get_write_function(output, overwrite)]) --> CheckPath{is_path? (pycompat.PathLike or str)}
    CheckPath -->|True| CheckOverwrite{overwrite and not is_path?}
    CheckOverwrite -->|overwrite valid| ReturnFileWriter[return FileWriter(output, overwrite).write]
    CheckPath -->|False| CheckNone{output is None?}
    CheckNone -->|True| ReturnStderr[return write -> sys.stderr.write(s) with UnicodeEncodeError fallback]
    CheckNone -->|False| CheckCallable{callable(output)?}
    CheckCallable -->|True| ReturnCallable[return output]
    CheckCallable -->|False| AssertWritable[assert isinstance(output, utils.WritableStream)]
    AssertWritable --> ReturnStreamWrap[return write -> output.write(s)]
    CheckPath -->|False and overwrite True| Raise[raise Exception about overwrite only for file paths]

## Examples:
- Default (write to stderr with Unicode fallback):
    write = get_write_function(None, overwrite=False)
    # write("a text line\n")  # writes to sys.stderr; if sys.stderr can't encode characters, utils.shitcode(s) is used

- File path (first write may overwrite if requested):
    write = get_write_function("trace.log", overwrite=True)
    # write("first line\n")  # FileWriter.write will open trace.log in 'w' (if successful) and then future writes append

- Custom callable:
    def sink(s): pass  # any callable that accepts a single text arg
    write = get_write_function(sink, overwrite=False)
    # write("text")  # invokes sink("text")

- Writable stream object:
    # stream must implement write(s)
    write = get_write_function(stream, overwrite=False)
    # write("text")  # calls stream.write("text")

- Error case:
    # Raises because overwrite=True with a non-path-like output
    get_write_function(None, overwrite=True)  # raises Exception: '`overwrite=True` can only be used when writing content to file.'

## `pysnooper.tracer.FileWriter` · *class*

## Summary:
A lightweight helper that writes UTF-8 text to a single filesystem path; the first write can optionally overwrite the file, and subsequent writes always append.

## Description:
FileWriter is a focused abstraction for emitting textual output to one file path without holding a persistent file descriptor. It is intended for callers that repeatedly emit small pieces of text (for example: trace/log lines) and prefer each write to open, write, and close the file immediately. Typical callers in tracing/logging code create one FileWriter per output file and call write() each time they need to append or (for the first write) replace the file contents.

Motivation and responsibility:
- Centralize path normalization (using pycompat.text_type).
- Encapsulate the one-time choice: whether the next write should overwrite the file (mode 'w') or append (mode 'a').
- Ensure every write uses UTF-8 text mode and closes the file promptly.
- Do not perform buffering, rotation, synchronization, or maintain an open file handle between writes.

## State:
- path (pycompat.text_type)
    - Type: text type produced by pycompat.text_type (normally str/unicode).
    - Valid values: any value accepted by pycompat.text_type; should be a string representing a filesystem path when used with open().
    - Invariant: represents the target file location; FileWriter does not validate existence or permissions at construction.
- overwrite (bool)
    - Type: bool
    - Initial value: provided by the caller to __init__ (no implicit default inside the class).
    - Valid values: True or False (truthy/falsey values accepted at assignment time).
    - Invariant: indicates whether the next invocation of write() will open the file in 'w' mode. If a write() call completes normally (i.e., the code reaches the final assignment), overwrite will be set to False so subsequent writes append. If an exception occurs before that assignment (for example, during open() or writing), overwrite remains unchanged.

Class invariants:
- path must remain a text string as returned by pycompat.text_type.
- overwrite is meaningful only until the first successful completion of write(); after that it is False.

## Lifecycle:
Creation:
- Instantiate with two arguments: path and overwrite.
  - path: converted via pycompat.text_type(path) and stored as self.path.
  - overwrite: stored as self.overwrite (caller should pass a bool).
- __init__ does not touch the filesystem and does not validate path.

Usage:
- Method: write(s)
  - Input: s — a text string (native str/text). Passing bytes in Python 3 will raise a TypeError when attempting to write to a text-mode file.
  - Behavior:
    - Choose mode = 'w' if self.overwrite is True else mode = 'a'.
    - Open self.path with the chosen mode and encoding='utf-8' using a context manager.
    - Call file.write(s) and close the file when leaving the context manager.
    - After the with-block completes, set self.overwrite = False. If open() or write() raises an exception before this assignment, the overwrite flag is left unchanged.
  - Return: None

Typical sequencing:
1. fw = FileWriter(path, overwrite=True_or_False)
2. fw.write(s1)  # may overwrite if overwrite was True and no exception occurs
3. fw.write(s2)  # appends (because overwrite is set to False after the first successful write)

Destruction / Cleanup:
- No explicit close method: each write() opens and closes the file, so no persistent file descriptor is held.
- No context-manager protocol is implemented; callers do not need to call close() but must handle exceptions from I/O operations.

Threading:
- FileWriter is not synchronized. Concurrent calls from multiple threads may interleave file open/write operations and produce mixed output. If thread-safety is required, callers must provide synchronization.

## Method Map:
flowchart LR
    Create[Create FileWriter(path, overwrite)] --> Write[write(s)]
    Write --> Mode{select 'w' or 'a' based on overwrite}
    Mode --> W[open(path, 'w', encoding='utf-8')]
    Mode --> A[open(path, 'a', encoding='utf-8')]
    W --> WriteToFile[write(s) then close]
    A --> WriteToFile
    WriteToFile --> SetFlag[self.overwrite = False] 
    WriteToFile --> Return[returns None]

## Methods (behavioral details):
- __init__(path, overwrite)
    - Purpose: store the text-converted path and the initial overwrite flag.
    - Parameters:
        - path: any object convertible by pycompat.text_type; the constructor calls pycompat.text_type(path) and stores the result in self.path.
        - overwrite: boolean-like value stored as self.overwrite indicating whether the next write uses 'w' mode.
    - Side effects: no filesystem operations.
    - Errors: exceptions raised by pycompat.text_type (e.g., TypeError) may propagate.

- write(s)
    - Purpose: write the provided text to self.path using UTF-8 encoding.
    - Parameters:
        - s: expected to be a text string (str). Passing bytes in Python 3 will raise TypeError when attempting to write to a text-mode file.
    - Behavior:
        - Determine mode: 'w' if self.overwrite is True else 'a'.
        - Open the file with open(self.path, mode, encoding='utf-8') using a with-statement.
        - Call the file object's write(s) method.
        - When the with-block completes normally, set self.overwrite = False.
        - Return None.
    - Side effects: may create the file if it does not exist; may overwrite or append depending on mode.
    - Thread-safety: none provided.

## Raises:
- __init__:
    - Any exception raised by pycompat.text_type(path) (e.g., TypeError) may propagate to the caller.
- write(s):
    - FileNotFoundError: if the directory components do not exist (depending on OS behavior).
    - PermissionError: insufficient permissions to create or write the file.
    - OSError / IOError: other low-level I/O errors from the OS.
    - TypeError: if s is of an incompatible type (e.g., bytes on Python 3 when the file is opened in text mode).
Notes:
- FileWriter does not catch these exceptions; they propagate to callers. Because self.overwrite is set to False only after the with-block completes, an exception during open() or write() will leave self.overwrite unchanged.

## Example:
Simple usage (conceptual snippet):
fw = FileWriter("trace.log", overwrite=True)
fw.write("=== TRACE START ===\n")   # opens in 'w' and writes; sets overwrite=False if successful
fw.write("first event\n")          # opens in 'a' and appends
# No explicit close needed; each write opens and closes the file.

## Implementation notes for re-implementation:
- Use pycompat.text_type(path) to preserve repository compatibility semantics for path conversion.
- Always open the file with encoding='utf-8' in text mode ('w' or 'a') and use a context manager to ensure the file is closed.
- After a successful write (i.e., after leaving the with-block normally), set self.overwrite = False so the initial overwrite flag only affects the first successful write.
- Do not add implicit synchronization or persistent file handles unless higher-level code requires it; the class intentionally opens and closes on each write.

### `pysnooper.tracer.FileWriter.__init__` · *method*

## Summary:
Initializes the FileWriter instance by storing the target file path (as text) and the initial overwrite behavior flag, establishing the object's minimal writable state.

## Description:
This constructor prepares a FileWriter that will later be used to append or overwrite text into a file when write(...) is called. It performs two simple actions: (1) coerces the provided path to a text string using pycompat.text_type and assigns it to self.path, and (2) stores the provided overwrite flag on self.overwrite.

Known callers and lifecycle context:
- Instances are created by code that configures where trace/log output should be sent (for example, higher-level tracer setup code). Creation typically occurs during tracer initialization or when a new output destination is configured.
- The object is lightweight and intended to be created and held until its write method is invoked; the __init__ performs no I/O and therefore is safe to call at configuration time.

Why this is a separate method:
- Encapsulates the minimal, deterministic setup of FileWriter state so the write(...) method can rely on well-typed attributes (a text path and an overwrite flag) with no additional validation or coercion on each write.
- Keeps initialization logic trivial and isolated from I/O concerns.

## Args:
    path (Any): The file path or path-like object to which the FileWriter will write.
        - The value is converted via pycompat.text_type(path) and stored as self.path.
        - Accepts strings or objects with a sensible text conversion. If conversion fails, the exception from pycompat.text_type (e.g., TypeError) will propagate.
    overwrite (bool): Flag indicating whether the first write should overwrite the file (True -> mode 'w') or append (False -> mode 'a').
        - Any truthy value will be treated as True by the write logic; non-boolean values are accepted but should be avoided for clarity.

## Returns:
    None

## Raises:
    Propagates exceptions raised by pycompat.text_type(path) when the path cannot be converted to text (e.g., TypeError). No other exceptions are explicitly raised by this method.

## State Changes:
    Attributes READ:
        - None (the initializer does not read any existing self.<attr> attributes)
    Attributes WRITTEN:
        - self.path: set to pycompat.text_type(path)
        - self.overwrite: set to the provided overwrite value

## Constraints:
    Preconditions:
        - The caller should provide a path value that pycompat.text_type can convert to a text string.
        - overwrite should represent the desired behavior for the first subsequent write call; passing a boolean is recommended.

    Postconditions:
        - After return, self.path is a text string representation of the provided path.
        - After return, self.overwrite equals the provided overwrite value (truthiness determines behavior in write()).
        - No file I/O has occurred during initialization.

## Side Effects:
    - No I/O or external service calls are performed.
    - No global state is modified.
    - Subsequent calls to the instance's write(...) method will perform file I/O and will mutate self.overwrite (write(...) sets self.overwrite to False after performing the write).

### `pysnooper.tracer.FileWriter.write` · *method*

## Summary:
Writes the given text to the file at the writer's path, using overwrite semantics on first write, and then clears the overwrite flag on the instance.

## Description:
This method opens the file referenced by the writer's path and writes the provided string to it. It chooses write mode 'w' (truncate/create) if the instance's overwrite flag is True, otherwise it appends using 'a'. After performing the write, it sets the instance's overwrite attribute to False so subsequent calls append by default.

Known callers:
    - No explicit callers were provided in the supplied snippet. In the typical pysnooper design, a FileWriter instance is used by the tracing infrastructure to persist trace output; the tracing code calls this method whenever it needs to emit one or more lines to the trace file.

Why this logic is its own method:
    - Centralizes file-opening and write-mode logic (overwrite vs append) in a single place.
    - Ensures consistent encoding (utf-8) and a single point where the overwrite flag is reset after the first write.
    - Keeps higher-level tracing code free of I/O details and state mutation (overwrite reset).

## Args:
    s (str):
        The text to write to the file. Must be a text (unicode) string or an object coercible to text. The method writes s as-is; no newline is added automatically.

## Returns:
    None.
    - The method does not return a value. Its effect is the file I/O performed and the mutation of self.overwrite to False.

## Raises:
    - Any exception raised by opening or writing to the file will propagate to the caller. This includes, but is not limited to:
        * FileNotFoundError: if the path points to a directory that does not exist and the environment disallows creating it.
        * PermissionError: if the process lacks permission to open or write the file.
        * OSError / IOError: other I/O related errors (disk full, file system errors).
    - The method itself does not catch or wrap these exceptions.

## State Changes:
    Attributes READ:
        - self.path: the filesystem path (string) used to open the file.
        - self.overwrite: boolean flag used to decide whether to open in 'w' or 'a' mode for this call.

    Attributes WRITTEN:
        - self.overwrite: set to False unconditionally after the write operation completes (even when appending).

## Constraints:
    Preconditions:
        - self.path must be a valid path-like text string (the class stores it as text in initialization).
        - self.overwrite should be a boolean (True to truncate on next write, False to append).
        - The caller should expect that exceptions from filesystem operations may be raised; callers that need robustness must catch these exceptions.

    Postconditions:
        - The file at self.path will contain the new content written (truncated if overwrite was True, otherwise appended).
        - self.overwrite will be False on the instance after the method returns (unless an exception propagated before the assignment).
        - The file descriptor is closed when the context manager exits.

## Side Effects:
    - Performs filesystem I/O: opens a file at self.path using encoding='utf-8' and writes the provided string.
    - If overwrite was True, open is performed with mode 'w', which truncates or creates the file; otherwise mode 'a' is used to append.
    - No synchronization or locking is performed: concurrent invocations (from other threads or processes) can interleave and may cause race conditions or data loss.
    - Any exceptions from open/write are propagated to the caller; no internal recovery or retry is attempted.

## `pysnooper.tracer.Tracer` · *class*

*No documentation generated.*

### `pysnooper.tracer.Tracer.__init__` · *method*

## Summary:
Set up a Tracer instance by normalizing the output writer, converting watched variable specifications into BaseVariable instances, and initializing all runtime containers and presentation flags required for tracing.

## Description:
This method runs when a Tracer object is instantiated (for example when the pysnooper.snoop decorator or a caller constructs Tracer(...)). It centralizes input normalization and initial state allocation so subsequent tracer logic can assume a consistent internal shape.

Known callers and lifecycle stage:
- Direct construction: Tracer(...) during configuration/setup.
- Higher-level factories/decorators (such as pysnooper.snoop) that create a Tracer as part of preparing to instrument a function or code block. In those flows __init__ executes during tracer creation, before any tracing begins.

Why this is an initializer method:
- It performs multiple orthogonal normalization and validation tasks (output -> write callable, normalization of watch/watch_explode entries, platform-aware color enabling) and allocates shared runtime containers (start_times, frame mappings, thread-local storage). Centralizing these responsibilities in __init__ avoids duplicating setup logic elsewhere and ensures other methods can rely on the instance invariants established here.

## Args:
    output (None | path-like | callable | writable-stream), default=None
        Destination for emitted trace text. get_write_function is called with (output, overwrite) and returns a single-argument callable self._write.
        - None: default; results in a writer that writes to sys.stderr (with a Unicode-encoding fallback).
        - Path-like (str / Path): results in a FileWriter-backed write method (may perform file I/O when invoked).
        - Callable: used directly as the write function (no wrapping).
        - Writable stream object: an object implementing write(s); get_write_function will wrap it into a callable that calls output.write(s).
        Note: get_write_function enforces that overwrite=True is only allowed with path-like outputs and will raise otherwise.

    watch (iterable | single item), default=()
        Variables to monitor in regular (non-exploding) mode. Normalization performed:
        - utils.ensure_tuple is used to convert the argument into a tuple: if the argument is an Iterable (but not a string) it is converted to tuple(x); otherwise (x,) is returned.
        - Each element v of the resulting tuple is converted to:
            * v if isinstance(v, BaseVariable)
            * CommonVariable(v) otherwise
        - The normalized list from watch becomes the initial portion of self.watch.

    watch_explode (iterable | single item), default=()
        Variables to monitor in "exploding" mode. Normalization is analogous to watch:
        - First ensure_tuple is applied.
        - Each element v is converted to:
            * v if isinstance(v, BaseVariable)
            * Exploding(v) otherwise
        - The normalized list from watch_explode is concatenated after the normalized watch list to form self.watch.

    depth (int), default=1
        Integer stored on self.depth. The initializer asserts that depth >= 1; an AssertionError is raised if depth is less than 1.

    prefix (str), default=''
        String stored on self.prefix and later used as a per-line prefix for output.

    overwrite (bool), default=False
        Forwarded to get_write_function which controls file open mode behavior when output is path-like. get_write_function validates its use and may raise Exception if used with a non-path-like output.

    thread_info (bool), default=False
        Flag stored on self.thread_info. When True, tracer will include thread-related information in output (other tracing methods consult this flag). thread_info_padding is initialized to 0.

    custom_repr (iterable), default=()
        Custom representation configuration stored on self.custom_repr after a normalization rule:
        - If len(custom_repr) == 2 and NOT all(isinstance(x, pycompat.collections_abc.Iterable) for x in custom_repr), then custom_repr is replaced with a single-element tuple containing the original pair: (custom_repr,).
          In other words, when a 2-tuple is supplied whose elements are not both Iterables, the pair is treated as a single custom-repr entry and wrapped into a tuple.
        - Otherwise custom_repr is stored unchanged.

    max_variable_length (int), default=100
        Integer stored on self.max_variable_length; used by variable-formatting code elsewhere to cap representation length.

    normalize (bool), default=False
        Stored flag (self.normalize) used by other tracer code to determine normalization behavior.

    relative_time (bool), default=False
        Stored flag (self.relative_time) that affects how timestamps are computed by other methods.

    color (bool), default=True
        Preferred color output flag. The actual self.color is computed as: color and sys.platform in ('linux','linux2','cygwin','darwin').
        If True, several ANSI color/style string attributes are set to escape codes; otherwise those attributes are set to empty strings.

## Returns:
    None
    - Standard object initializer: configures the instance in-place and returns None.

## Raises:
    AssertionError
        - Condition: depth < 1 triggers assert self.depth >= 1.

    Exception (from get_write_function)
        - Condition: overwrite=True with a non-path-like output. get_write_function raises an Exception with the message: '`overwrite=True` can only be used when writing content to file.'
        - This initializer does not catch that exception; it propagates to the caller.

    Propagated exceptions from subcomponents
        - Construction of CommonVariable or Exploding for watch entries may raise exceptions depending on their constructors.
        - get_write_function may raise other exceptions indirectly (e.g., path normalization errors when constructing FileWriter). Those propagate out of __init__.

## State Changes:
Attributes READ:
    - None of self.<attr> fields are read prior to assignment in this method.

Attributes WRITTEN (assigned or created):
    - self._write: callable returned by get_write_function(output, overwrite).
    - self.watch: list[BaseVariable] created by concatenating normalized watch and watch_explode entries (CommonVariable/Exploding wrappers applied where appropriate).
    - self.frame_to_local_reprs: dict, initialized {}.
    - self.start_times: dict, initialized {}.
    - self.depth: int (value of depth argument).
    - self.prefix: str (value of prefix argument).
    - self.thread_info: bool (value of thread_info argument).
    - self.thread_info_padding: int, initialized to 0.
    - self.target_codes: set, initialized to set().
    - self.target_frames: set, initialized to set().
    - self.thread_local: threading.local() instance (new per Tracer).
    - self.custom_repr: normalized custom_repr as described above.
    - self.last_source_path: None.
    - self.max_variable_length: int (value of max_variable_length).
    - self.normalize: bool (value of normalize).
    - self.relative_time: bool (value of relative_time).
    - self.color: bool (computed as color and platform check).
    - ANSI/style string attributes:
        * When self.color is True:
            - self._FOREGROUND_BLUE = '\x1b[34m'
            - self._FOREGROUND_CYAN = '\x1b[36m'
            - self._FOREGROUND_GREEN = '\x1b[32m'
            - self._FOREGROUND_MAGENTA = '\x1b[35m'
            - self._FOREGROUND_RED = '\x1b[31m'
            - self._FOREGROUND_RESET = '\x1b[39m'
            - self._FOREGROUND_YELLOW = '\x1b[33m'
            - self._STYLE_BRIGHT = '\x1b[1m'
            - self._STYLE_DIM = '\x1b[2m'
            - self._STYLE_NORMAL = '\x1b[22m'
            - self._STYLE_RESET_ALL = '\x1b[0m'
        * When self.color is False: the above attributes are set to '' (empty string).

## Constraints:
Preconditions:
    - depth must be an integer >= 1.
    - If overwrite is True, output must be path-like (enforced by get_write_function).
    - Items supplied in watch and watch_explode must be acceptable inputs for CommonVariable/Exploding constructors or already be BaseVariable instances.

Postconditions:
    - After return, the Tracer instance has:
        * a ready-to-call writer at self._write (subject to behavior of get_write_function and potential I/O when invoked),
        * a normalized list self.watch of BaseVariable instances,
        * allocated containers and thread-local storage for runtime tracing,
        * color/style attributes set consistently with the platform and color flag.

## Side Effects:
    - Calls get_write_function(output, overwrite): may instantiate helper objects (e.g., FileWriter) and may raise if arguments are invalid. get_write_function itself does not perform file I/O at call time, but the returned callable may perform I/O when later invoked.
    - Allocates threading.local() and several empty containers (dicts/sets) on the instance.
    - No I/O occurs during __init__ itself (no writes), but subsequent calls to self._write may write to stderr, files, or user-provided streams.

### `pysnooper.tracer.Tracer.__call__` · *method*

## Summary:
Delegates a callable invocation used as a decorator: if tracing is globally disabled returns the original object unchanged; otherwise dispatches to the appropriate wrapper for classes or functions, updating no Tracer attributes itself.

## Description:
This method implements the Tracer instance's callable behavior so Tracer objects can be used as decorators. Typical callers and invocation contexts:
- Applied at definition time via decorator syntax or programmatic decoration (for example, when a developer writes @some_tracer on a function or class). The decorator machinery (interpreter/module initialization) calls this method once with the target object.
- Any external helper that treats a Tracer instance as a callable (e.g., factory code that applies a tracer to many callables) will call this method.

This logic is separated into its own method so that a Tracer instance can be directly used as a decorator (making Tracer objects first-class decorator factories) and so the simple dispatch and global-disable check are centralized rather than duplicated inside _wrap_class/_wrap_function or at decorator call sites.

## Args:
    function_or_class (object): The object being decorated. Typically either:
        - a class object (inspect.isclass returns True), or
        - a function or other callable (inspect.isclass returns False).
    There is no explicit type enforcement — any object is accepted; non-class objects are forwarded to _wrap_function.

## Returns:
    object: One of the following:
        - If the module-level DISABLED flag is truthy, returns the original function_or_class unchanged.
        - If inspect.isclass(function_or_class) is True, returns the value returned by self._wrap_class(function_or_class).
        - Otherwise, returns the value returned by self._wrap_function(function_or_class).
    Edge cases:
        - If _wrap_class or _wrap_function returns None or raises, that value/exception propagates unchanged from this method.
        - The method does not wrap non-class objects specially; they are forwarded to _wrap_function even if not callable.

## Raises:
    Any exception raised by self._wrap_class or self._wrap_function will propagate out of this method unchanged.
    This method itself does not raise new exceptions under normal conditions.

## State Changes:
Attributes READ:
    - DISABLED (module-level name): the boolean flag consulted to short-circuit wrapping.
    - self._wrap_class (bound method): consulted when the target is a class.
    - self._wrap_function (bound method): consulted when the target is not a class.

Attributes WRITTEN:
    - None. This method does not mutate any self.<attr> fields directly.

## Constraints:
Preconditions:
    - The Tracer instance must have callable attributes self._wrap_class and self._wrap_function; otherwise an AttributeError will occur when called.
    - The intended use is as a decorator at definition time; calling with arbitrary objects is allowed but semantics depend on the implementations of _wrap_*.

Postconditions:
    - If DISABLED was truthy at call time, self is unchanged and the original object is returned.
    - If DISABLED was falsy and _wrap_class/_wrap_function complete successfully, the returned value is whatever those methods return (commonly a wrapper or the original object).

## Side Effects:
    - No direct I/O or global state mutation occurs in this method itself.
    - Delegated methods (self._wrap_class or self._wrap_function) may perform side effects (install wrappers, modify attributes on the target, register hooks, write to files, etc.); those side effects are not created by this method but will occur when they are invoked.
    - If DISABLED is truthy, no delegation occurs and none of those side effects happen.

### `pysnooper.tracer.Tracer._wrap_class` · *method*

## Summary:
Wraps all plain instance methods defined on a class with this Tracer's function wrapper and returns the same class object; the class is mutated in-place and the tracer's internal state is updated indirectly by the per-function wrapper creation.

## Description:
Known callers and context:
    - Tracer.__call__ invokes this method when a Tracer instance is used as a decorator on a class (decoration time, immediately after the class body is executed).
    - It is intended to be used at class-definition time to instrument instance methods so that calls into those methods are traced by this Tracer instance.

Why this is a separate method:
    - Iterating a class's attributes and wrapping each function is a distinct concern from wrapping a single function; extracting it keeps Tracer.__call__ small and makes the class-wrapping logic reusable and testable.
    - The method centralizes the logic for deciding which class attributes should be wrapped and performs the in-place mutation on the class.

## Args:
    cls (type): The class object whose methods should be wrapped. Must be a class (a type object) that exposes a __dict__ mapping of attributes as typical Python classes do.

## Returns:
    type: The (same) class object passed in, after mutation. For every attribute in the class __dict__ that meets the criteria below, the attribute value is replaced with the wrapper returned by self._wrap_function(attr). If no attributes matched, the same class object is returned unchanged except for the identity-preserving return.

## Raises:
    NotImplementedError: If a class attribute is a function that represents an async generator function (pycompat.isasyncgenfunction(attr) is True) then self._wrap_function(attr) raises NotImplementedError; this exception will propagate out of _wrap_class.
    AttributeError / TypeError: If the provided cls is not a class-like object with a __dict__ mapping, attempting to iterate cls.__dict__.items() may raise AttributeError or TypeError. The method assumes cls is a proper class type.

## Behavior and Edge Cases:
    - Only attributes where inspect.isfunction(attr) is True are candidates to be wrapped. This includes normal instance methods defined with def inside the class body.
    - Attributes that are descriptors such as staticmethod or classmethod are not plain function objects in the class __dict__ (they are staticmethod/classmethod objects) and therefore are not wrapped by this method. To instrument staticmethod or classmethod, callers must unwrap the descriptor and rewrap appropriately (not performed here).
    - Coroutine functions (async def) are skipped by the early pycompat.iscoroutinefunction(attr) check and are not wrapped here. This avoids attempting to produce a synchronous wrapper around an async function.
    - If a plain function attribute is an async generator function, _wrap_function will raise NotImplementedError; this propagates to callers of _wrap_class.
    - The method mutates the class in-place: setattr(cls, attr_name, wrapped) replaces the attribute with the wrapper returned by self._wrap_function(attr).
    - Wrapping preserves function metadata via functools.wraps inside _wrap_function (so name, docstring, module, and attributes propagated by wraps are retained on the wrapper).

## State Changes:
    Attributes READ:
        - self._wrap_function (method lookup/read)
    Attributes WRITTEN:
        - None directly on self within this method. However, as a side-effect of calling self._wrap_function(attr) for each matched function, that helper may mutate Tracer state (for example, _wrap_function adds function.__code__ to self.target_codes). Those indirect writes to self.target_codes occur during the execution of _wrap_function.
    External object mutations:
        - cls: one or more attributes in the class object are replaced in-place with the wrapper functions returned by self._wrap_function.

## Constraints:
    Preconditions:
        - cls must be a class (a type object) exposing a __dict__ that yields (name, value) pairs.
        - The method expects that ordinary instance methods are stored as plain function objects in cls.__dict__ (the usual case for methods defined with def).
    Postconditions:
        - For each attribute name/value pair in the original cls.__dict__ where:
            * pycompat.iscoroutinefunction(value) is False, and
            * inspect.isfunction(value) is True,
          the class attribute is replaced with the result of self._wrap_function(value).
        - The method returns the same cls object passed in.
        - Tracer state may now include additional entries (for example in self.target_codes) as a result of invoking self._wrap_function for each wrapped function.

## Side Effects:
    - Mutates the provided class object by replacing qualifying attributes with wrapper callables (in-place modification of cls).
    - Indirectly mutates the Tracer instance via calls to self._wrap_function (e.g., adding wrapped function code objects to self.target_codes).
    - No I/O or global system calls are performed by this method itself.

### `pysnooper.tracer.Tracer._wrap_function` · *method*

## Summary:
Registers the function's code object for tracing and returns a wrapper that runs the function under this Tracer's tracing context; for generator functions it returns a wrapper that preserves generator send/throw semantics while running each generator step inside the Tracer context.

## Description:
This method is used whenever the Tracer is applied as a decorator to a function or when individual class methods are wrapped by Tracer._wrap_class. Typical callers and call sites:
- Tracer.__call__(function_or_class) — invoked when a Tracer instance is used as a decorator; if the passed object is a function this method is called.
- Tracer._wrap_class(cls) — invokes this method for each function attribute on a class to create wrapped methods.
- Any usage of Tracer as a decorator: @Tracer(...) decorating a function or class will indirectly call this method.

This logic is separated into its own method because:
- It centralizes the logic for registering a function's code object with the tracer and for selecting the correct wrapper strategy (regular function vs generator).
- It is reused for both single-function decoration and for wrapping many methods on a class.
- It isolates the generator-handling logic (which must preserve send/throw behavior) from the higher-level decorator flow.

## Args:
    function (callable): A Python function object (expected to be a regular function or generator function). Must have a __code__ attribute. Bound methods are acceptable (their underlying function object also has __code__).

## Returns:
    function: A wrapper callable with the same call signature as `function` (metadata such as __name__ and __doc__ are preserved via functools.wraps):
      - If `function` is a generator function (inspect.isgeneratorfunction(function) is True), returns `generator_wrapper`, a function that when called returns a generator whose each step (each send/throw into the underlying generator) is executed under the Tracer context manager (with self). The returned generator preserves:
          - yield behavior (yields the same values as the original generator),
          - send(value) semantics (values sent by the caller are forwarded into the underlying generator),
          - throw(exc) semantics (exceptions thrown by the caller are forwarded to the underlying generator via gen.throw),
          - StopIteration is propagated as completion.
      - Otherwise returns `simple_wrapper`, a function that executes the wrapped function inside `with self:` and returns the underlying function's return value.

    Edge-case returns:
      - The returned generator function (generator_wrapper) returns None when the underlying generator raises StopIteration (normal termination).
      - The wrappers do not transform return values or exceptions beyond running the code under the Tracer context.

## Raises:
    NotImplementedError:
      - Raised if pycompat.iscoroutinefunction(function) is True (the code explicitly refuses to wrap native coroutine functions).
      - Raised if pycompat.isasyncgenfunction(function) is True (the code explicitly refuses to wrap async-generator functions).
    Notes:
      - No other exceptions are raised by this method itself, but exceptions raised when the returned wrapper is invoked will propagate from the underlying function/generator as usual.

## Behavior and Implementation Details:
- The first action is to register the function's code object:
    - self.target_codes.add(function.__code__)
  This ensures the Tracer's trace() method recognizes frames executing this function and will instrument them.

- simple_wrapper:
    - Decorated with functools.wraps(function) so wrapper preserves the wrapped function's metadata (__name__, __doc__, __module__, and update_wrapper behavior).
    - When invoked, it executes:
        with self:
            return function(*args, **kwargs)
      thereby installing tracing (via Tracer.__enter__/__exit__ which manipulate sys.settrace, start times, and other state) for the entire call of `function`.

- generator_wrapper:
    - Also decorated with functools.wraps(function).
    - When called, it instantiates the underlying generator: gen = function(*args, **kwargs)
    - It uses a small loop to drive the generator so that each invocation of the generator's .send or .throw into the underlying generator happens inside the Tracer context:
        - Initialize method = gen.send and incoming = None.
        - Loop:
            - Enter `with self:` and call outgoing = method(incoming).
                - If the underlying generator raises StopIteration during that call, generator_wrapper returns (ends the generator).
            - Yield outgoing to caller: the code performs (yield outgoing) to receive the next `incoming` value.
            - If a value is sent by the caller, the wrapper sets method, incoming = gen.send, (yielded_value)
            - If the caller throws an exception into the wrapper, the wrapper switches to method, incoming = gen.throw, exc_object
    - This preserves:
        - First iteration semantics (send(None) to prime the generator),
        - send(value) behavior,
        - throw(exception) behavior forwarded to the underlying generator,
        - proper termination on StopIteration.

- Async constructs:
    - The implementation purposely refuses to handle coroutine functions and async generators (NotImplementedError), because managing async event-loop scheduling and awaitables would require a different approach.

## State Changes:
- Attributes READ:
    - None explicitly read for decision purposes except implicit attribute access to self when creating wrappers and for registration (the method does not inspect other self attributes).
- Attributes WRITTEN:
    - self.target_codes: the function's __code__ object is added to this set.

## Constraints:
- Preconditions:
    - `function` must be a Python function object with a __code__ attribute.
    - The Tracer instance (`self`) must be properly initialized (target_codes must be a mutable set).
    - Wrapping coroutine functions or async generator functions is not supported — callers must expect NotImplementedError for those inputs.
- Postconditions:
    - After the call, self.target_codes contains function.__code__.
    - The returned callable will run the original function under the Tracer context (so invocation will activate tracing for frames whose code object is in self.target_codes).
    - For generator functions, the returned wrapper will preserve generator protocol semantics (send/throw/StopIteration).

## Side Effects:
- Immediate:
    - Mutation of Tracer state: function.__code__ is added to self.target_codes.
- When returned wrapper is invoked:
    - The wrapper uses Tracer.__enter__ and Tracer.__exit__ (via `with self:`), which have broader side effects:
        - they manipulate the Python tracing facilities (sys.settrace and frame.f_trace),
        - they may write to the Tracer output (self._write) and update Tracer.start_times, self.frame_to_local_reprs, self.target_frames, and thread-local stacks,
        - they may cause I/O (writing formatted trace lines).
    - The wrappers themselves do not perform external I/O directly, but the context manager they use does.

## Implementation notes for reimplementation:
- Use functools.wraps to preserve metadata but note that wraps does not rewrite the Python function signature. For strict signature preservation one must use advanced tooling (not necessary here).
- To implement generator_wrapper correctly, ensure that:
    - The wrapper yields exactly the same yielded values as the underlying generator.
    - Values and exceptions sent or thrown from the caller are forwarded to gen.send and gen.throw respectively.
    - Each invocation of gen.send/gen.throw occurs while inside the Tracer context manager (with self: block) to ensure trace() is active for code executed inside the generator step.
    - The initial call should use gen.send(None) behavior (the code initializes incoming=None and calls method(incoming) with method=gen.send).
- Ensure the same NotImplementedError behavior for coroutine and async generator functions to match original contract.

### `pysnooper.tracer.Tracer.write` · *method*

## Summary:
Writes a single log line to the Tracer's configured output by prepending the instance prefix and appending a trailing newline. Does not mutate Tracer internal state (aside from performing external output).

## Description:
This method centralizes line formatting and output for all internal logging in Tracer. It is the single point where textual log lines produced throughout Tracer are formatted and handed off to the writable destination.

Known callers and contexts:
- Tracer.trace(): called repeatedly to emit event lines (source path, timestamped events, variable changes, return values, exceptions). Called during tracing lifecycle whenever Tracer decides to emit a log line.
- Tracer.__exit__(): called to emit the "Elapsed time" summary when the traced context ends.
- Other internal call sites within Tracer that need to output a single line use this method for consistent formatting (prefix handling and newline termination).

Why this is a separate method:
- Keeps formatting (prefix + newline) consistent across all Tracer outputs.
- Delegates actual writing to the configured write function (self._write), which may be a file write, stream write, or custom callable obtained from get_write_function(output, overwrite) in __init__.
- Centralizing output logic reduces duplication, making it easy to change prefixing/termination behavior in one place and to ensure all trace output goes through the same I/O abstraction.

## Args:
    s (str or any object with a string representation): The content to write. The value will be converted to a string via Python format substitution into the template "{self.prefix}{s}\n". Passing non-string objects is allowed; they will be formatted using their __format__/__str__ behavior.

## Returns:
    None: The method performs side-effectful output and returns None implicitly.

## Raises:
    Any exception raised by the Python string formatting operation:
        - For example, AttributeError or TypeError can occur if formatting references fail.
    Any exception raised by the underlying write callable (self._write):
        - For example, IOError/OSError when writing to files or streams, or arbitrary exceptions from a custom callable.
    Notes:
        - The method does not catch or translate exceptions; they propagate to the caller unchanged.

## State Changes:
    Attributes READ:
        - self.prefix: used to prepend every output line.
        - self._write: the callable invoked to perform the actual write.
    Attributes WRITTEN:
        - None: this method does not modify Tracer attributes.

## Constraints:
    Preconditions:
        - The Tracer instance must have been initialized so that self._write exists and is callable (set up in Tracer.__init__ by get_write_function).
        - s must be a value acceptable to Python string formatting; arbitrary objects are permitted but may raise during formatting.
    Postconditions:
        - The configured write callable (self._write) is invoked once with a single string argument equal to the concatenation of self.prefix, the provided s formatted as text, and a trailing newline character.
        - No Tracer attributes are changed by this method.

## Side Effects:
    - Performs external I/O by calling the configured write callable (self._write). The exact side effects depend on that callable (writing to stdout, a file, a buffer, or any custom destination).
    - Always appends a newline to the emitted content; if the supplied s already contains newlines, an additional newline will still be appended.

### `pysnooper.tracer.Tracer.__enter__` · *method*

## Summary:
Installs this Tracer's tracing function for the current thread and calling frame when entering a context, recording the calling frame's start time and saving the previous trace function on a per-thread stack. If the global DISABLED flag is set, performs no action.

## Description:
- When called by the context manager protocol (i.e., when a Tracer instance is used in a with statement), this method sets up tracing so the Tracer will observe events in the code inside the with-block.
- Typical caller: the Python interpreter invokes this method as part of executing "with tracer_instance:" before entering the with-block body.
- Lifecycle stage: initialization of runtime tracing for the active thread and the immediate calling frame; this is the setup step for the Tracer's context-managed tracing session.
- Rationale for being a dedicated method: entering a tracing context requires multiple coordinated operations (registering a per-frame trace function, saving/restoring previous trace functions, recording a timestamp, and mutating thread-local state). Keeping these steps together ensures consistent setup and simplifies the context-manager interface.

## Args:
    None

## Returns:
    None
    - The method returns implicitly. If the global DISABLED flag is true, it returns immediately without performing any setup; otherwise it completes the tracing setup and returns None.

## Raises:
    - This method does not explicitly raise any exceptions in its body. Runtime exceptions may occur if attributes it accesses are missing or invalid (for example, if inspect.currentframe() returns None and subsequent operations assume a frame object), but such exceptions are not raised intentionally by this method.

## State Changes:
Attributes READ:
    - self._is_internal_frame (method is called with calling_frame as argument)
    - self.thread_local (accessed to reach thread_local.__dict__)
    - self.start_times (read to assign into)
    - self.trace (used as the trace function to install)
    - self.target_frames (checked/used when adding calling_frame)

Attributes WRITTEN:
    - self.target_frames: calling_frame is added (self.target_frames.add(calling_frame))
    - self.thread_local.__dict__: the key 'original_trace_functions' is created if missing and its list is mutated (stack.append(sys.gettrace()))
    - self.start_times: an entry mapping the calling_frame to datetime_module.datetime.now() is assigned

## Other mutated state / external effects (side effects):
    - thread_global.__dict__: ensures the key 'depth' exists by calling setdefault('depth', -1).
    - calling_frame.f_trace: for non-internal calling frames, sets calling_frame.f_trace = self.trace (mutates the frame object external to self).
    - sys module trace function: pushes the currently-installed trace function onto the per-thread stack and then calls sys.settrace(self.trace) to install this Tracer's trace function as the global trace function for the current thread.
    - The per-thread list under thread_local.__dict__['original_trace_functions'] is mutated by appending the previously-active trace function (sys.gettrace()).
    - self.start_times is updated with the current timestamp obtained via datetime_module.datetime.now().

## Constraints:
Preconditions:
    - The global DISABLED flag must be False for the method to perform tracing setup; if DISABLED is True the method returns immediately and performs no changes.
    - The instance is expected to expose the attributes used here: _is_internal_frame (callable), thread_local (object with a __dict__ mapping), start_times (mutable mapping), trace (callable), and target_frames (set-like with an add method). The method calls and assignments assume these attributes exist and have the required semantics.

Postconditions:
    - After a successful (non-disabled) call:
        - thread_global.__dict__ contains the key 'depth' (existing value preserved if present; otherwise set to -1).
        - If the calling frame is not considered internal by self._is_internal_frame, that frame's f_trace is set to self.trace and that frame is present in self.target_frames.
        - The current thread's per-thread stack under thread_local.__dict__['original_trace_functions'] has been appended with the previously-installed trace function (the value returned by sys.gettrace()).
        - self.start_times contains an entry for the calling frame with a timestamp equal to the value returned by datetime_module.datetime.now() at the time of the call.
        - sys.gettrace() (for the current thread) after this method completes will return self.trace (because sys.settrace(self.trace) was called).

## Side Effects:
    - Installs a new trace function for the current thread (sys.settrace(self.trace)).
    - Mutates an external frame object's f_trace attribute (calling_frame.f_trace).
    - Mutates a per-thread stack of original trace functions stored in thread_local.__dict__.
    - Records a timestamp in self.start_times for the calling frame.
    - May cause other tracing-related behavior in the interpreter (e.g., enabling line/event callbacks) because the global trace function has changed.

### `pysnooper.tracer.Tracer.__exit__` · *method*

## Summary:
Restore the previous per-thread trace function, clean up per-frame tracing state for the calling frame, compute and emit the elapsed time for the traced block, and return without suppressing exceptions (unless tracing is disabled).

## Description:
This method is invoked by the Python context-manager protocol when a Tracer instance used in a with statement completes the with-block (i.e., as part of the __exit__ step). Common callers in this repository include:
- The Python interpreter when executing "with tracer:" blocks.
- The wrappers created in Tracer._wrap_function (simple_wrapper and generator_wrapper), which use "with self:" to trace function or generator execution.

The logic is separated into its own __exit__ method because exiting a tracing context requires multiple coordinated operations (restoring the prior trace function, cleaning per-frame state, computing elapsed time, and writing output). Keeping those steps in a dedicated method centralizes cleanup semantics and pairs naturally with __enter__.

## Args:
    exc_type (type | None):
        Exception class if an exception was raised in the with-block; otherwise None. This method ignores the value and does not attempt to suppress exceptions.

    exc_value (Exception | None):
        The exception instance raised inside the with-block, or None.

    exc_traceback (traceback | None):
        The traceback object associated with exc_value, or None.

## Returns:
    None
    - The method does not return True to suppress exceptions; any exception raised inside the with-block will propagate after this method completes (unless an exception is raised within __exit__ itself).

## Raises:
    Any exception raised by underlying operations. Notable conditions:
    - IndexError:
        - If the per-thread stack of original trace functions (self.thread_local.original_trace_functions) is empty, stack.pop() will raise IndexError.
    - KeyError:
        - If the calling frame is not present as a key in self.start_times, start_times.pop(calling_frame) will raise KeyError.
    - AttributeError / TypeError:
        - If inspect.currentframe() returns None, accessing f_back may raise AttributeError; or if thread_local/original_trace_functions are not set up as expected, attribute access may fail.
    - Exceptions raised by datetime_module.datetime.now or pycompat.timedelta_format are also possible but unlikely.
    Note: If the global DISABLED flag is True, the method returns immediately and raises nothing.

## State Changes:
Attributes READ:
    - self.thread_local.original_trace_functions: accessed to obtain the list of previously-installed trace functions for current thread.
    - self.target_frames: consulted and modified (see WRITTEN).
    - self.frame_to_local_reprs: accessed when popping the stored local-repr mapping for the calling frame.
    - self._FOREGROUND_YELLOW, self._STYLE_DIM, self._STYLE_NORMAL, self._STYLE_RESET_ALL: read to assemble the formatted elapsed-time message.
    - self.start_times: accessed to remove and obtain the start time for the calling frame.
    - self.write (callable): invoked to emit text output.
    - thread_global.depth: read to compute indentation for the elapsed-time line.
    - inspect.currentframe(): used to locate the calling frame for cleanup.

Attributes WRITTEN / Mutated:
    - self.thread_local.original_trace_functions: mutated by popping the last saved trace function (stack.pop()).
    - self.target_frames: mutated by discarding the calling frame (self.target_frames.discard(calling_frame)).
    - self.frame_to_local_reprs: mutated by removing any entry for the calling frame (pop).
    - self.start_times: mutated by popping the entry for the calling frame (start_times.pop(calling_frame)).
    - The global interpreter trace function is changed by sys.settrace(...) (external mutation, not a self attribute).

## Constraints:
Preconditions:
    - The global DISABLED flag must be False for the method to perform cleanup; if DISABLED is True the method returns immediately and performs no actions.
    - __enter__ should have been called earlier in the same context so that:
        * self.thread_local.original_trace_functions exists and contains at least one saved trace function to restore,
        * self.start_times contains an entry keyed by the calling frame (so start_time can be popped).
    - The Tracer instance must have the style attributes (_FOREGROUND_YELLOW, _STYLE_DIM, _STYLE_NORMAL, _STYLE_RESET_ALL) initialized (this is done in __init__).

Postconditions (guarantees after successful non-error completion):
    - The previously-installed trace function for the current thread has been restored via sys.settrace.
    - The calling frame has been removed from self.target_frames.
    - Any local-representation mapping for the calling frame has been removed from self.frame_to_local_reprs.
    - The start time recorded for the calling frame has been removed from self.start_times.
    - A single formatted "Elapsed time" line has been emitted via self.write containing:
        * indentation computed from thread_global.depth + 1,
        * the elapsed time formatted by pycompat.timedelta_format,
        * ANSI/style strings taken from the instance attributes (or empty strings when color is disabled).
    - The method does not suppress exceptions raised inside the with-block (it returns None).

## Side Effects:
    - Mutates interpreter-level tracing by calling sys.settrace(restored_trace), restoring the trace function previously saved in thread-local storage.
    - Performs a write operation through self.write, which in turn calls the underlying writer self._write; this may perform I/O (writing to stderr, a file, or a user-provided stream).
    - Calls datetime_module.datetime.now() to compute the elapsed duration (reads system clock).
    - Calls pycompat.timedelta_format(duration) to obtain a human-readable elapsed-time string.
    - Reads thread_global.depth (module-level global) to compute indentation. This method does not change thread_global.depth itself.
    - Mutates the list object stored at self.thread_local.original_trace_functions by popping its last element.
    - If any of the external calls (sys.settrace, inspect.currentframe, datetime_module, pycompat, or self.write) raise, those exceptions propagate to the caller.

## Implementation notes / cautions:
    - The method intentionally ignores exc_type, exc_value, and exc_traceback: its job is cleanup and reporting, not exception handling. Do not attempt to return True to silence exceptions unless intentionally changing behavior.
    - To avoid IndexError and KeyError, ensure __enter__ reliably sets up self.thread_local.original_trace_functions and self.start_times for the calling frame; callers should prefer using the context-manager protocol (with tracer:) rather than invoking __enter__/__exit__ directly.
    - The method computes indent using (thread_global.depth + 1) to align the elapsed-time line with the frame-entering indentation convention used by trace(). This relies on thread_global.depth being correctly maintained by trace() during the traced execution.

### `pysnooper.tracer.Tracer._is_internal_frame` · *method*

## Summary:
Return True if the provided frame's code filename is exactly equal to the filename where Tracer.__enter__ is defined; otherwise return False. This predicate does not mutate the Tracer instance.

## Description:
This helper performs a direct equality comparison between the runtime frame's code filename and the filename of Tracer.__enter__.__code__.co_filename. The implementation is a single expression that uses the frame's f_code.co_filename and the Tracer class's __enter__ function code object filename.

Known callers and call context:
- No callers are visible in the provided source snippet. In typical tracer implementations such a predicate is used by frame-filtering or dispatch logic, but that usage is not shown here.

Why this logic is a separate method:
- The comparison is a single, well-scoped predicate that is convenient to name and reuse; extracting it makes the intent explicit and isolates the filename-based check.

## Args:
    frame (types.FrameType or any object exposing `f_code.co_filename`):
        A Python frame object (or a duck-typed object) whose `.f_code.co_filename` attribute will be read. Must not be None.

## Returns:
    bool:
        True when frame.f_code.co_filename == Tracer.__enter__.__code__.co_filename; False otherwise.

## Raises:
    AttributeError:
        If `frame` is None or does not have an `.f_code` attribute, or if `.f_code` lacks a `.co_filename` attribute, attribute access will raise AttributeError.

## State Changes:
    Attributes READ:
        - Class-level code object information via Tracer.__enter__.__code__.co_filename is accessed.
        - No instance attributes on self (self.<attr>) are read by this method.
    Attributes WRITTEN:
        - None. The method does not modify self or any other state.

## Constraints:
    Preconditions:
        - `frame` must be a frame-like object with an accessible `f_code.co_filename` attribute.
        - The Tracer class must have an attribute `__enter__` that is a function (or function-like object) with a `__code__` object exposing `co_filename` (as is true for normal Python functions).
    Postconditions:
        - No mutation of the Tracer instance or external objects.
        - The method returns a boolean result reflecting the filename equality.

## Side Effects:
    - None. The method performs no I/O and does not call or mutate external services or objects outside of reading the two filename attributes involved in the comparison.

### `pysnooper.tracer.Tracer.set_thread_info_padding` · *method*

## Summary:
Adjusts the Tracer's stored thread-info column width to accommodate the given thread_info string and returns a right-padded version of that string so thread information aligns across log lines.

## Description:
- Known callers:
    - Tracer.trace — invoked each time a tracing event is being formatted when thread_info is enabled. In that context the method is called after constructing a short thread descriptor (typically "{ident}-{name} ") and immediately before writing the tracing line.
- Lifecycle/context:
    - This method is used during the formatting stage of a tracing event. Each time an event is formatted, the current thread string is passed here so the Tracer can maintain a running maximum width and return a padded string for aligned output.
- Why a separate method:
    - Encapsulates the logic that maintains and updates the shared padding state (self.thread_info_padding) and produces a padded string. This keeps trace formatting code concise and centralizes behavior for computing/remembering the maximum thread-info width across many calls.

## Args:
    thread_info (str):
        - The thread description string to be aligned (e.g., "12345-MainThread ").
        - Must be a string-like object supporting len(...) and the str.ljust(width) operation.
        - No default; caller must supply the string.

## Returns:
    str:
        - A right-padded version of thread_info whose length equals the updated self.thread_info_padding.
        - If thread_info is shorter than the current maximum width, the returned string contains trailing spaces to reach that width.
        - If thread_info is already as long as (or longer than) the previous maximum, the internal padding is increased and the returned string length equals the new maximum.
        - Edge-case: if thread_info is the empty string and the current padding is 0, returns the empty string.

## Raises:
    TypeError:
        - If thread_info does not support len(...) or does not implement ljust(width), a TypeError (or AttributeError from the underlying operations) will be raised.
        - If self.thread_info_padding is of an incompatible type such that max(...) cannot compare it with the integer length, a TypeError may be raised.
    (The method itself does not explicitly raise exceptions; these are the exceptions produced by built-in operations when preconditions are violated.)

## State Changes:
- Attributes READ:
    - self.thread_info_padding (reads current stored padding value)
- Attributes WRITTEN:
    - self.thread_info_padding (updated to max(previous_value, len(thread_info)))

## Constraints:
- Preconditions:
    - The object must have an integer-like self.thread_info_padding attribute (Tracer.__init__ sets it to 0).
    - thread_info should be a str (or str-like) so len(thread_info) yields an integer and thread_info.ljust(width) is defined.
    - Typical callers construct thread_info as a formatted string (e.g., "{ident}-{name} ") — callers should preserve that string format and include any trailing separator (space) if desired.
- Postconditions:
    - self.thread_info_padding >= previous self.thread_info_padding
    - self.thread_info_padding >= len(thread_info)
    - The returned string has length exactly equal to self.thread_info_padding and equals thread_info right-padded with spaces as necessary.

## Side Effects:
    - Mutates only the Tracer instance attribute self.thread_info_padding.
    - No I/O, no global state modifications, and no external service calls.
    - Does not change the passed-in thread_info object (strings are immutable); returns a new padded string.

## Implementation notes / limitations:
    - Width is based on Python string length (number of codepoints). Terminal column width differences for multi-codepoint graphemes or wide characters (e.g., East Asian width) are not accounted for — padding may not perfectly align visually in all terminals.
    - The method relies on callers to supply a thread_info string; it does not itself query threading.current_thread().

### `pysnooper.tracer.Tracer.trace` · *method*

*No documentation generated.*

