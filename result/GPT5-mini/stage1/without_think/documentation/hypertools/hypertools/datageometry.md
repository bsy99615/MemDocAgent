# `datageometry.py`

## `hypertools.datageometry.DataGeometry` · *class*

*No documentation generated.*

### `hypertools.datageometry.DataGeometry.__init__` · *method*

## Summary:
Initializes a DataGeometry instance by storing plotting-related handles and data-related parameters on the object and computing the inferred data dtype; after this call the instance holds all incoming configuration needed by later transformation and plotting steps.

## Description:
This constructor is called when a new DataGeometry object is created to hold the plotting/analysis state for a dataset. Typical use occurs at the start of the plotting or data-processing pipeline when creating an instance that will be passed through transformation steps (reduce, align, normalize) and ultimately to plotting routines.

This logic is separated into its own method because it centralizes and documents the object's initial state setup: assigning user-provided handles (figure, axis, animation), normalizing/text-converting raw input data when it is a list, and computing the canonical dtype for the stored data. Keeping initialization logic in one place simplifies later code that expects the DataGeometry instance to provide a consistent set of attributes.

## Args:
    fig (object, optional):
        A plotting Figure object or equivalent handle. Default: None.
    ax (object, optional):
        A plotting Axes object or equivalent handle. Default: None.
    line_ani (object, optional):
        An optional animation/line animation handle used by plotting code. Default: None.
    data (any, optional):
        The raw data to be stored. Can be None, a pandas.DataFrame, numpy array, list, or other structure accepted by the library.
        If a list is provided, each element is passed through the convert_text helper before being stored.
        Default: None.
    xform_data (any, optional):
        A placeholder for transformed/processed data (set but not modified by this method). Default: None.
    reduce (any, optional):
        A reducer specification or result to be stored for later use by tools.reduce. Default: None.
    align (any, optional):
        An alignment specification or result for later use by tools.align. Default: None.
    normalize (any, optional):
        A normalization specification or result for later use by tools.normalize. Default: None.
    semantic (any, optional):
        Semantic-processing related metadata or flag (library-specific). Default: None.
    vectorizer (any, optional):
        A vectorizer object (e.g., for text embedding) used by semantic steps. Default: None.
    corpus (any, optional):
        A corpus or collection used by semantic/vectorizer steps. Default: None.
    kwargs (dict, optional):
        A dictionary of additional keyword arguments or configuration passed through to downstream tools/plotting. Default: None.
    version (str, optional):
        Version string recorded on the instance; defaults to the package-level __version__ imported from config. Default: __version__.
    dtype (any, optional):
        Declared dtype (user-supplied) — NOTE: the current implementation accepts this parameter but does not use it; dtype is inferred from the stored data via get_dtype(data). Default: None.

## Returns:
    None
    - As a constructor, it does not return a value. The observable result is the set of attributes assigned on self.

## Raises:
    - This method does not explicitly raise exceptions itself.
    - Exceptions raised by helper functions propagate:
        * convert_text may raise exceptions if elements of a provided list are not convertible (propagated).
        * get_dtype may raise exceptions depending on the implementation and invalid data (propagated).
    - Any exceptions originating from user-supplied objects assigned to attributes (unlikely at assignment time) will propagate as usual.

## State Changes:
    Attributes READ:
        - None of self's attributes are read prior to assignment in this implementation.
    Attributes WRITTEN:
        - self.fig: set to the provided fig
        - self.ax: set to the provided ax
        - self.line_ani: set to the provided line_ani
        - self.data: set to the provided data (after convert_text mapping if data is a list)
        - self.dtype: set to result of get_dtype(data)
        - self.xform_data: set to the provided xform_data
        - self.reduce: set to the provided reduce
        - self.align: set to the provided align
        - self.normalize: set to the provided normalize
        - self.semantic: set to the provided semantic
        - self.vectorizer: set to the provided vectorizer
        - self.corpus: set to the provided corpus
        - self.kwargs: set to the provided kwargs
        - self.version: set to the provided version (defaults to package __version__)

## Constraints:
    Preconditions:
        - No required preconditions on self; this method is the initializer.
        - Provided handles (fig, ax, vectorizer, etc.) should be valid objects as expected by downstream code; otherwise downstream errors may occur.
    Postconditions:
        - self.data will equal the original data argument except that if the original data argument was a list, each element has been replaced by convert_text(element).
        - self.dtype will equal the return value of get_dtype(data) called after any convert_text mapping.
        - All listed attributes in "Attributes WRITTEN" are set on the instance after return.
        - The dtype parameter passed to the constructor is ignored by the current implementation (documented behavior to avoid confusion).

## Side Effects:
    - Calls convert_text on each element if data is a list; convert_text may mutate or convert elements and may raise exceptions.
    - Calls get_dtype(data) to infer and store the data type; get_dtype's behavior or side effects (if any) will occur.
    - No file I/O, network calls, or other external I/O are performed directly by this method.
    - No mutation of external objects is performed by assignments except for any side effects arising from convert_text or get_dtype.

### `hypertools.datageometry.DataGeometry.get_data` · *method*

## Summary:
Return a shallow copy of the stored data container so callers can inspect or operate on the data without directly mutating the DataGeometry instance's internal reference.

## Description:
This accessor returns a shallow copy of the DataGeometry.data attribute using Python's copy.copy. It is intended for external callers (client code or other modules) that need a snapshot of the current data while preserving the DataGeometry object's internal reference. There are no internal callers within the DataGeometry class itself.

Why this is a separate method:
- Centralizes the policy for exposing internal data (explicit shallow-copy semantics) in one place.
- Avoids duplicating copy.copy(self.data) throughout client code and documents the intended behavior.

Known callers / lifecycle:
- Not called by other methods inside DataGeometry.
- Typical use: after constructing or updating a DataGeometry instance, client code calls this method to obtain a copy for analysis, transformation, or plotting without altering the instance's self.data.

## Args:
    None

## Returns:
    object: A shallow copy of self.data (the same container type as stored).
    - If self.data is None, returns None.
    - Typical container types: list, dict, pandas.DataFrame, or other user-defined containers.
    - Shallow copy semantics:
        - The returned top-level container/object is a new object (new reference).
        - Nested mutable objects (elements, values, underlying data buffers) are shared between the original and the returned copy. Mutating those nested objects may affect both.
        - For pandas.DataFrame, the returned object will be a new DataFrame object that shares the same underlying data buffers (i.e., not a deep copy of the data).

Example usage:
- Calling get_data() on a DataGeometry instance returns a separate top-level container:
  - If the caller reassigns the returned value (e.g., sets variable = returned_value), the DataGeometry.data attribute is unaffected.
  - If the caller mutates nested elements (e.g., modifies a list inside the returned list or modifies entries in a returned DataFrame's underlying data), those changes may also be visible in the original self.data because the copy is shallow.

## Raises:
    Any exception raised by copy.copy(self.data) is propagated to the caller.
    - This includes exceptions from a custom __copy__ implementation on the stored object or failures during the shallow copy operation.

## State Changes:
    Attributes READ:
        - self.data
    Attributes WRITTEN:
        - None (the method does not modify any DataGeometry attributes)

## Constraints:
    Preconditions:
        - The DataGeometry instance must be initialized; self.data may be any Python object including None.
        - No other invariants are required.

    Postconditions:
        - The DataGeometry instance is unchanged by this call.
        - The caller receives a new top-level object that is a shallow copy of the stored data.

## Side Effects:
    - No I/O, logging, or external service calls.
    - The method itself does not mutate external objects, but because the copy is shallow, subsequent mutations performed by the caller on nested objects contained within the returned value may affect the original nested objects referenced by self.data.

### `hypertools.datageometry.DataGeometry.get_formatted_data` · *method*

## Summary:
Returns a formatted representation of this DataGeometry object's data as a list of 2-D numeric arrays suitable for downstream processing (e.g., alignment, normalization, reduction). This call does not mutate the DataGeometry instance; it produces and returns a new formatted data structure derived from self.data.

## Description:
Known callers and lifecycle stage:
    - No direct callers were identified in the provided source for this repository excerpt. Conceptually, this method is intended to be invoked at stages of the data-processing pipeline that require a standardized numeric representation of data, for example immediately before alignment, normalization, dimensionality reduction, or plotting routines.
    - Typical pipeline usage: consumer code that needs to convert heterogeneous user-provided data (lists, arrays, text, pandas DataFrames, nested DataGeometry objects) into a canonical list of 2-D numeric arrays will call this method to obtain formatted inputs for further processing.

Why this method exists (separation of concerns):
    - This method is a thin wrapper around the shared formatting utility tools.format_data. Keeping the wrapper on DataGeometry centralizes how callers obtain a formatted representation from the object's internal state (self.data) and encapsulates the dependency on tools.format_data behind the DataGeometry API. It prevents callers from having to import or call the lower-level helper directly and keeps formatting logic conceptually part of the DataGeometry interface.

## Args:
    None

## Returns:
    list[numpy.ndarray]
        A list of arrays where each element is a numeric array with at least two dimensions:
        - Each returned array is shaped (n_samples, n_features).
        - Any 1-D arrays present in input are reshaped to (n_samples, 1) by the formatter.
        - The list length corresponds to the number of processed data "blocks" produced from self.data (text blocks may be expanded into matrix representations; nested DataGeometry instances may be expanded into multiple list entries).
        - Edge cases:
            - If self.data is a single item, format_data treats it as a one-element list and will return a list with one array (or more if nested geo/data expands).
            - If numeric arrays contain missing values, format_data may trigger PPCA-based handling and still return numeric arrays (possibly after imputation); warnings may be emitted.

## Raises:
    - This method does not explicitly raise exceptions in its body.
    - Exceptions raised by tools.format_data or any of its callees (for example, errors from text2mat, df2mat, alignment or numpy operations) will propagate to the caller. Typical causes that may raise include:
        - AttributeError or TypeError if self.data is missing or of an unsupported type for the downstream formatters.
        - ValueError from lower-level converters if input shapes or contents are invalid.
    - Warnings: format_data emits warnings (warnings.warn) in certain situations (e.g., missing data handled via PPCA, automatic alignment) — these are warnings, not exceptions.

## State Changes:
    Attributes READ:
        - self.data
    Attributes WRITTEN:
        - None (the method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - self must have a public attribute data (self.data) set before calling.
        - self.data should be a type acceptable to tools.format_data: either a single datum or a list/sequence of data items. Supported input kinds (as interpreted by format_data's type-dispatch) include textual inputs (strings / list of strings / arrays of strings), numeric arrays or lists, pandas DataFrame, and nested DataGeometry-like objects that expose get_data().
    Postconditions:
        - The DataGeometry object remains unchanged (no mutation of self attributes).
        - The method returns a list whose elements are 2-D numeric arrays ready for downstream numeric processing (alignment, normalization, plotting).

## Side Effects:
    - Emits warnings via the warnings module in cases detected by tools.format_data (for example, when missing numeric data is handled with PPCA or when automatic alignment is performed). These warnings are global and visible to the application.
    - May indirectly call other modules (tools.text2mat, tools.df2mat, tools.align, etc.), which perform their own computation; no I/O (file, network) is performed directly by this method itself.

### `hypertools.datageometry.DataGeometry.transform` · *method*

## Summary:
Return a transformed representation of the given data by running the full pipeline (format -> normalize -> reduce -> align); if called with no argument, return the object's cached transformed data (self.xform_data) without modifying the object.

## Description:
- Purpose and typical usage:
    - This method centralizes the multi-stage data preprocessing pipeline: it formats raw inputs into numeric matrices (and converts text inputs), applies normalization, performs dimensionality reduction, then aligns multiple datasets into a common coordinate space. It is intended to produce data ready for plotting or downstream analysis.
- Known callers / invocation context:
    - Public API of the DataGeometry object. Callers include plotting or analysis workflows that need a transformed representation for either the object's stored data (call with no args) or for ad-hoc input data provided at call time (call with data=...).
- Why this is a separate method:
    - The sequence and configuration of formatting, normalization, reduction, and alignment is non-trivial and reused across the codebase; centralizing it ensures consistent ordering, configuration usage (self.semantic, self.vectorizer, self.corpus, self.normalize, self.reduce, self.align), and single-point maintenance for warnings and errors emitted by helper tools.

## Args:
    data (optional):
        - None (default): return the cached transformed representation stored in self.xform_data.
        - Otherwise: a dataset or an iterable of datasets accepted by format_data. Accepted input types include:
            * numpy arrays (1D or 2D)
            * Python lists or arrays of numeric values
            * pandas.DataFrame
            * lists/arrays of strings (text documents)
            * DataGeometry objects (their .get_data() is processed)
        - When non-None, the argument is forwarded to format_data(..., ppca=True) with semantic=self.semantic, vectorizer=self.vectorizer, corpus=self.corpus.

## Returns:
    - If data is None:
        * Exactly self.xform_data (whatever was stored previously). This method does not modify or recompute it.
    - If data is provided:
        * The object returned by the final alignment step. Possible concrete cases:
            1. Multiple input datasets (or format_data produces a list of length > 1):
                - The method returns a list of 2D numpy.ndarray objects: [arr1, arr2, ...], each arr having shape (n_samples_i, n_components) where n_components is determined by the reduction configuration (if reduction is applied).
            2. Single input dataset where reduction produces a single reduced array:
                - The method returns a single 2D numpy.ndarray of shape (n_samples, n_components).
            3. If reduction is a no-op (self.reduce is None), the method returns the normalized (and possibly aligned) structure produced by format_data/normalize; this is usually a list (even for a single original input, format_data returns a list), but downstream helpers may return a single array in some branches.
        * In short: callers should be prepared to accept either a list of ndarrays or a single ndarray depending on how many datasets are processed and how the reduce/align helpers behave.

## Raises:
    - AssertionError: if self.normalize has an invalid value; normalize(...) asserts that normalize is one of ['across','within','row', False, None].
    - ValueError: if the reduction configuration (self.reduce) is malformed or not supported by the reduction backend; reduce(...) raises ValueError for invalid model names or missing params.
    - TypeError or KeyError: this method accesses self.reduce['params']['n_components'] directly. If self.reduce is None or not a mapping that contains 'params' and 'n_components', attempting to read this value will raise TypeError or KeyError before the reduce function is invoked.
    - Any exception raised by format_data, normalize, reduce, or align is propagated to the caller; this method performs no try/except around those calls.
    - Warnings (not exceptions) are emitted by helper functions under degenerate conditions (e.g., missing data with PPCA, reduction warnings when ndims greater than rows, deprecation notices).

## State Changes:
- Attributes READ:
    - self.semantic
    - self.vectorizer
    - self.corpus
    - self.normalize
    - self.reduce
    - self.align
    - self.xform_data (only when data is None)
- Attributes WRITTEN:
    - None. The method performs no assignment to self.<attr>; the DataGeometry object's state remains unchanged.

## Constraints:
- Preconditions:
    - If you intend reduction to run without error, ensure self.reduce is a dict-like object with the structure {'model': <model>, 'params': {'n_components': <int>, ...}} so that self.reduce['params']['n_components'] is a valid value. The transform implementation directly indexes this path.
    - The provided data must be compatible with format_data. format_data will coerce single inputs into a list, handle text and dataframe types, and may raise for unsupported types.
    - If normalization is enabled (self.normalize not in [False, None]), its value must be one of ['across','within','row'].
- Postconditions:
    - The DataGeometry instance is unchanged (no side-effect state mutations).
    - The return value is the fully processed output according to the instance configuration (formatting options, normalization, reduction dims, and alignment mode).
    - If data is None, returned value equals pre-call self.xform_data.

## Side Effects:
- No file I/O, network, or external service calls.
- Emits runtime warnings from the helper functions in certain edge conditions (missing values, shape mismatches, deprecations).
- Imports helper functions (align, normalize, reduce) dynamically inside the method body; this is a benign side effect using normal Python import caching.
- Does not mutate input arguments or any attributes on self.

## Usage guidance and example patterns:
- To retrieve the previously computed transform (no recomputation), call with no args:
    - result = obj.transform()
- To compute a new transform for some data and ensure reduction uses 3 components:
    - obj.reduce = {'model': 'IncrementalPCA', 'params': {'n_components': 3}}
    - transformed = obj.transform(data=my_data)
- Caller robustness:
    - Be prepared to accept either a list of arrays or a single array from this method. If your downstream code requires a list, wrap single-array outputs as [result] when isinstance(result, np.ndarray).
    - If you observe an exception indexing self.reduce['params']['n_components'], verify obj.reduce is a dict with the expected keys; alternatively, change the code to populate self.reduce accordingly before calling transform.

### `hypertools.datageometry.DataGeometry.plot` · *method*

## Summary:
Delegates rendering of the stored or provided dataset to the central plotting routine, composing instance-level defaults and any per-call overrides; does not mutate the DataGeometry instance.

## Description:
This method is the public entry point for producing a visualization from a DataGeometry instance. It selects which data and transformation pipeline to pass to the plotting implementation, merges this instance's stored plotting defaults with any overrides supplied by the caller, and delegates the actual plotting work to the plot.plot.plot function (imported locally as the plotter).

Known callers and invocation context:
- There are no internal callers inside DataGeometry; this is intended to be used by client code (scripts, notebooks, or higher-level hypertools APIs) when a user asks to render data associated with a DataGeometry object or to render an external dataset using the same plotting defaults.
- Typical lifecycle: after constructing a DataGeometry object (which carries data, transformation metadata, and plotting defaults), call plot() to produce or update a visualization. The method is separated from constructor/transform logic because it only composes arguments and delegates plotting; the heavy plotting logic lives in the external plotter.

Why this is a separate method:
- Keeps a thin, testable interface that composes instance defaults with call-time overrides.
- Encapsulates the decision logic for whether to reuse a precomputed transformation (self.xform_data) or force re-computation in the plotter when pipeline parameters are overridden.
- Delegates rendering to the specialized plot.plot.plot implementation to avoid duplicating plotting code inside DataGeometry.

## Args:
    data (optional, any): If provided, this object is passed directly to the plotter and no stored transform (self.xform_data) is used. If omitted (None), the method will use a shallow copy of self.data and may use a shallow copy of self.xform_data as the transform argument unless pipeline-related overrides are provided via kwargs.
    **kwargs: Arbitrary keyword arguments forwarded to the delegated plotter. If any of the following keys are present in kwargs: 'reduce', 'align', 'normalize', 'semantic', 'vectorizer', 'corpus', then the method will explicitly clear the transform (set transform=None) so the plotter will recompute transforms according to the supplied overrides.

Allowed/expected shapes and types:
- data: any object accepted by the delegated plotter (commonly preformatted numeric arrays, lists, or other structures understood by hypertools' formatters).
- kwargs: standard Python keyword arguments; typical keys are plotting and pipeline configuration options.

## Returns:
    Any: The exact return value is whatever the delegated plot.plot.plot function returns when called as plotter(d, **new_kwargs). This method does not post-process or wrap that return value.

Edge-case return values:
- If plotter raises, the exception propagates directly; there is no catch here.

## Raises:
    AttributeError: If self.kwargs is None (or not a dict-like object providing an update method), the call new_kwargs.update(update_kwargs) will raise 'NoneType' object has no attribute 'update'. In practice, self.kwargs is expected to be a dict-like mapping; callers or constructors should ensure that.
    Any exception raised by the delegated plotter (plot.plot.plot) will propagate unchanged.

## State Changes:
Attributes READ:
    - self.data
    - self.xform_data
    - self.kwargs
    - self.reduce
    - self.align
    - self.normalize
    - self.semantic
    - self.vectorizer
    - self.corpus

Attributes WRITTEN:
    - None. This method does not modify any self.<attr> fields. All copies are shallow copies and local variables; the object state is preserved.

## Constraints:
Preconditions:
    - If data is None, self.data should be set to a value acceptable to the plotting pipeline (not strictly enforced by this method).
    - self.kwargs must be a dict-like object (supports copy.copy(self.kwargs) and .update()) to avoid an AttributeError.
    - The instance pipeline attributes (self.reduce, self.align, self.normalize, self.semantic, self.vectorizer, self.corpus) can be None or structured as expected by the plotter; their exact required shape is determined by the delegated plotting and transform code.

Postconditions:
    - No changes are made to the DataGeometry instance.
    - The delegated plotter has been invoked with:
        - d set to a shallow copy of self.data when data is None (unless data argument provided),
        - transform set to a shallow copy of self.xform_data when data is None and the caller did not override pipeline-related kwargs; otherwise transform is None,
        - all instance-level pipeline attributes (self.reduce, self.align, self.normalize, self.semantic, self.vectorizer, self.corpus) supplied as keyword args unless overwritten by explicit kwargs,
        - any explicit kwargs provided by the caller override instance defaults.

## Side Effects:
    - No file I/O or network operations are performed by this method itself.
    - The method performs shallow copies (via copy.copy) of self.data and self.xform_data when appropriate; this avoids mutating the stored references but does not deep-copy nested objects.
    - The plotter called at the end may produce side effects (e.g., create figures, open windows, save files) depending on its implementation; those side effects are not handled or suppressed here and will occur as defined by the delegated plot function.

### `hypertools.datageometry.DataGeometry.save` · *method*

## Summary:
Saves the DataGeometry instance to disk as a pickled .geo file, temporarily removing non-serializable plotting state and converting pandas DataFrame data to a simple dict form; the in-memory object is restored to its original state before the method returns.

## Description:
This method serializes the DataGeometry object to a file using Python's pickle module. It is intended to be used when a user or calling code needs to persist a prepared/processed DataGeometry for later loading (for example, after building or visualizing trajectories). Typical call sites include user-driven "save" actions in a workflow after data preparation, alignment, reduction, or plotting steps.

Why this is a separate method:
- Plotting attributes (figure, axes, animation objects) are frequently not picklable or are heavy/GUI-bound, so the method centralizes the safe serialization logic: remove those attributes, convert the data to a pickle-friendly representation, write the object, and then restore the original in-memory state.
- Encapsulating this logic in one method avoids duplicating the careful try/finally restoration pattern wherever the object must be saved.

## Args:
    fname (str):
        - File path or base name to write the serialized object to.
        - If the string does not end with the extension ".geo", the extension will be appended automatically.
    compression (optional, any):
        - Accepted but ignored. If a non-None value is passed, the method emits a FutureWarning stating that the argument has no effect and will be removed in a future version.
        - Default: None

## Returns:
    None
    - The method does not return a value. Its effect is to create (or overwrite) a file at the given path containing the pickled object.

## Raises:
    - Any I/O exceptions raised by opening the file are propagated (e.g., OSError, IOError).
    - Any pickle errors (for example, pickle.PicklingError or TypeError) raised by pickle.dump are propagated.
    - Note: the method itself does not catch these exceptions; it uses a try/finally to guarantee restoration of in-memory state even when an exception occurs.

## Behavior and Edge Cases:
    - If compression is not None, a FutureWarning is emitted (via warnings.warn) but no compression is applied.
    - If fname does not end with ".geo", the method appends ".geo" (so "file" becomes "file.geo").
    - Before serialization:
        - The method reads and saves the current values of self.fig, self.ax, self.line_ani, and self.data into local temporaries.
        - If self.data is a pandas DataFrame, it is converted to a dictionary-of-lists using to_dict('list'); otherwise the data value is used as-is for serialization.
        - The method then sets self.fig, self.ax, and self.line_ani to None and sets self.data to the prepared data_out_fmt. This modified object is what gets pickled.
    - The object written to disk therefore contains:
        - fig = None, ax = None, line_ani = None
        - data = data_out_fmt (DataFrame converted to dict-of-lists if applicable)
    - Restoration:
        - In a finally block the method restores the original values of self.fig, self.ax, self.line_ani, and self.data so the in-memory object is unchanged after the method returns (successful or not).
    - The try/finally ensures restoration even if pickle.dump or file open fails.

## State Changes:
    Attributes READ:
        - self.fig
        - self.ax
        - self.line_ani
        - self.data
    Attributes WRITTEN (temporarily during serialization, then restored):
        - self.fig (set to None)
        - self.ax (set to None)
        - self.line_ani (set to None)
        - self.data (replaced with a pickle-friendly representation for the duration of the dump)

## Preconditions:
    - The caller should supply a valid filesystem path or filename string for fname. The process must have write permission to the target directory.
    - The DataGeometry instance should contain data that is either directly picklable or convertible to a picklable form by the DataFrame-to-dict conversion. If data contains non-picklable objects, pickle.dump may raise.
    - No special precondition is required for self.fig/self.ax/self.line_ani because they will be nulled for serialization; however, if other attributes refer to GUI or external resources, those may still affect pickling.

## Postconditions:
    - On successful completion, a file named fname (with ".geo" extension) exists and contains a pickled snapshot of the DataGeometry object where plotting attributes are None and DataFrame data has been converted to a dictionary-of-lists.
    - The in-memory DataGeometry object is restored to its exact pre-call state (original fig, ax, line_ani, data), regardless of whether serialization succeeded or raised an exception.

## Side Effects:
    - Writes a binary file to disk via open(..., 'wb') and pickle.dump(self, f).
    - Emits a FutureWarning via warnings.warn when compression is not None.
    - No network calls or external services are used.
    - The method mutates the object attributes temporarily but restores them before returning; external references to the same object may observe the temporary state if they access attributes concurrently during the dump (concurrency is not synchronized).

## Implementation notes (for reimplementation):
    - Use a try/finally pattern to guarantee restoration of attributes even when serialization raises.
    - Convert pandas DataFrame to a serializable structure using to_dict('list') to preserve column-wise data as lists.
    - Use pickle.dump(self, f) to write the object; open the file in binary write mode.
    - Ensure the file name ends with ".geo" by appending the extension if missing.
    - Emit a FutureWarning when compression is passed and ignored.

