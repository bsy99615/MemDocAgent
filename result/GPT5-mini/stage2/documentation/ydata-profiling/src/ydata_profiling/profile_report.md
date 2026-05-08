# `profile_report.py`

## `src.ydata_profiling.profile_report.ProfileReport` · *class*

*No documentation generated.*

### `src.ydata_profiling.profile_report.ProfileReport.__init__` · *method*

## Summary:
Initializes a ProfileReport instance by selecting and preparing the report configuration, initializing the target dataframe for profiling, storing construction-time metadata (sample, typeset, summarizer, type schema), and optionally triggering report construction when lazy is False.

## Description:
This initializer is executed when a ProfileReport object is created (i.e., during instantiation: ProfileReport(...)). It centralizes the logic for:
- validating input arguments,
- selecting and composing the runtime configuration (from a provided Settings object, a configuration file, or built-in presets),
- applying convenience flag-based configuration groups (explorative, sensitive, dark_mode, orange_mode),
- applying shorthand keyword mappings and any remaining kwargs to the configuration,
- enabling timeseries-related configuration (tsmode and sortby),
- initializing the internal dataframe representation using the finalized configuration,
- storing per-instance metadata fields (sample, typeset, summarizer, type_schema),
- and optionally forcing immediate report generation when lazy is False by accessing self.report.

This logic is kept inside __init__ rather than in external helpers to ensure configuration selection and instance attribute population are performed together, so downstream consumers (properties and methods of ProfileReport) can assume a consistent internal state.

Known callers and typical lifecycle stage:
- Called by client code and library code when a new profiling run is started: ProfileReport(df=..., config=..., minimal=True, ...).
- Occurs at the beginning of the profiling pipeline: construction sets up all state required for later report generation or incremental operations.

## Args:
    df (Optional[Union[pd.DataFrame, sDataFrame]]): The input dataset to profile. May be a pandas DataFrame or a Spark DataFrame (or None). Default: None.
    minimal (bool): When True, selects a minimal built-in configuration (config_minimal.yaml) unless an explicit config_file is provided. Default: False.
    tsmode (bool): Enable time-series mode in the report configuration (sets report_config.vars.timeseries.active). Default: False.
    sortby (Optional[str]): Column name to use for sorting in time-series mode. Applied only if tsmode is True. Default: None.
    sensitive (bool): If True, merges the "sensitive" argument group into the configuration (via Config.get_arg_groups). Default: False.
    explorative (bool): If True, merges the "explorative" argument group into the configuration. Default: False.
    dark_mode (bool): If True, merges the "dark_mode" argument group into the configuration. Default: False.
    orange_mode (bool): If True, merges the "orange_mode" argument group into the configuration. Default: False.
    sample (Optional[dict]): Optional sample specification or metadata to attach to the report instance. This value is stored as self._sample. Default: None.
    config_file (Optional[Union[Path, str]]): Path to a configuration YAML file to load Settings from. If provided (or if minimal is True), Settings().from_file(config_file) is used. Default: None.
    lazy (bool): If False, forces immediate access of self.report (which may trigger report generation). If True (default), creation does not access the report property. Default: True.
    typeset (Optional[VisionsTypeset]): Optional VisionsTypeset to attach to this instance (stored in self._typeset). Default: None.
    summarizer (Optional[BaseSummarizer]): Optional summarizer to attach (stored in self._summarizer). Default: None.
    config (Optional[Settings]): An already-constructed Settings object to use as the base configuration. If provided, this takes precedence over default Settings/SparkSettings selection. Default: None.
    type_schema (Optional[dict]): Optional type schema mapping to be stored in self._type_schema. Default: None.
    **kwargs: Additional configuration keys (flat mapping). Behavior:
        - If kwargs is non-empty, shorthand mappings are extracted via Config.shorthands(kwargs); those shorthands are merged into the base settings.
        - Any remaining kwargs are applied via report_config.update(kwargs).
        - These kwargs must be valid configuration keys accepted by Settings.update(); invalid keys will cause the underlying update call to raise.

## Returns:
    None

## Raises:
    - Any exception raised by the helper methods or configuration functions invoked here may propagate:
        * Exceptions from self.__validate_inputs(...) if the provided arguments are invalid.
        * Exceptions from get_config("config_minimal.yaml") if the minimal config path resolution fails.
        * Exceptions from Settings().from_file(config_file) when reading or parsing the configuration file.
        * Exceptions from Config.shorthands(...) if shorthand processing fails.
        * Exceptions from Settings.update(...) if invalid configuration keys or values are provided.
        * Exceptions from self.__initialize_dataframe(df, report_config) if dataframe initialization fails.
        * If lazy is False, accessing self.report may raise any exceptions produced by the report property/accessor.
    The initializer itself does not explicitly raise new exception types; it forwards errors from these called operations.

## State Changes:
Attributes READ:
    - self.report (only accessed if lazy is False; read access may trigger property logic)
Attributes WRITTEN:
    - self.df: Set to the return value of self.__initialize_dataframe(df, report_config)
    - self.config: Set to the finalized Settings/SparkSettings instance named report_config
    - self._df_hash: Set to None
    - self._sample: Set to the provided sample argument (may be None)
    - self._type_schema: Set to the provided type_schema argument (may be None)
    - self._typeset: Set to the provided typeset argument (may be None)
    - self._summarizer: Set to the provided summarizer argument (may be None)

Additionally, the local report_config object is mutated during construction:
    - report_config is assigned from Settings().from_file(config_file) or from config or from Settings()/SparkSettings()
    - report_config is potentially updated with groups based on explorative/sensitive/dark_mode/orange_mode
    - report_config may be updated with shorthand mappings and with remaining kwargs
    - report_config.vars.timeseries.active is set to the value of tsmode
    - If tsmode is True and sortby is provided, report_config.vars.timeseries.sortby is set.

After these mutations report_config is persisted to self.config.

## Constraints:
Preconditions:
    - The caller should pass either no config_file and accept default Settings selection, or a valid config_file path/string that Settings().from_file can read and parse; otherwise an exception will be raised by Settings().from_file.
    - The df parameter may be None, a pandas DataFrame, or a Spark DataFrame (type annotation). If df is a pandas DataFrame, the code path selects Settings(); otherwise it uses SparkSettings() by default (unless config or config_file is provided).
    - kwargs must contain valid configuration keys/shorthands recognized by Config.shorthands and Settings.update; otherwise Settings.update or shorthand resolution will raise.
    - If tsmode is True and sortby is provided, sortby should be a column name present/valid for the dataframe; otherwise downstream timeseries handling may fail (this initializer only assigns the value into the configuration).

Postconditions:
    - After __init__ returns successfully, the instance will have self.config, self.df, and the listed underscore-prefixed metadata attributes set (self._df_hash == None, self._sample, self._type_schema, self._typeset, self._summarizer).
    - report_config.vars.timeseries.active reflects the provided tsmode argument; report_config.vars.timeseries.sortby reflects sortby when provided and tsmode is True.
    - If lazy was False, self.report was accessed during construction (which may have produced side effects depending on the implementation of the report property).

## Side Effects:
    - May perform I/O when resolving and loading configuration:
        * When minimal is True and no config_file is provided, get_config("config_minimal.yaml") is called to resolve a built-in config path.
        * If config_file is provided (or chosen via minimal), Settings().from_file(config_file) is invoked which typically reads and parses a YAML file.
    - May trigger non-trivial computation or I/O via:
        * self.__initialize_dataframe(df, report_config) — this method is responsible for preparing the dataframe for profiling and may load data, convert types, or sample rows (implementation-specific).
        * If lazy is False: accessing self.report may trigger report generation logic (heavy computation, memory allocation, and possibly I/O) depending on the report property implementation.
    - No global state is modified by this initializer beyond the instance attributes and the possible reading of configuration files; configuration updates are made to local report_config then assigned to self.config.

### `src.ydata_profiling.profile_report.ProfileReport.__validate_inputs` · *method*

## Summary:
Validate constructor arguments for a ProfileReport before profiling begins; enforces mutually exclusive options, non-empty dataframe requirements, and supported mode combinations. Does not mutate object state.

## Description:
This helper performs input validation early in the ProfileReport lifecycle. It is intended to be invoked during ProfileReport initialization (for example, from __init__ or an initialization helper) to fail fast on invalid combinations of arguments before any (potentially expensive) profiling work begins.

Known callers / lifecycle stage:
- Called from the ProfileReport initialization path (constructor or setup routine) prior to computing summaries and generating the report.
- Runs during the preparation/validation stage of the report creation pipeline.

Rationale for separate method:
- Centralizes and documents argument validation logic in one place, keeping the constructor/setup code concise and avoiding duplication if multiple initialization paths exist (e.g., lazy vs. eager creation).

## Args:
    df (Optional[Union[pandas.DataFrame, pyspark.sql.DataFrame]]):
        The input tabular dataset. May be a pandas DataFrame or a Spark DataFrame.
        - Allowed values: a non-empty DataFrame, or None when lazy=True.
        - None is only permitted when lazy is True (see Raises for behavior).
    minimal (bool):
        If True, initialize in "minimal" mode (lighter-weight config).
        - Allowed values: True or False.
    tsmode (bool):
        If True, enable time-series analysis mode.
        - Allowed values: True or False.
        - Note: time-series analysis is not implemented for Spark DataFrames (see Raises).
    config_file (Optional[Union[pathlib.Path, str]]):
        Path to a configuration file to initialize settings from.
        - Allowed values: None or a Path/str pointing to a config file.
        - If provided, cannot be used together with minimal=True.
    lazy (bool):
        If True, allow creating a ProfileReport without immediately providing a DataFrame.
        - Allowed values: True or False.
        - When False, df must be provided and non-empty.

## Returns:
    None

## Raises:
    ValueError:
        - If df is None and lazy is False:
            "Can init a not-lazy ProfileReport with no DataFrame"
        - If config_file is not None and minimal is True:
            "Arguments `config_file` and `minimal` are mutually exclusive."
        - If df is an instance of pandas.DataFrame and df is not None and df.empty is True:
            Raised with the message constructed in the source (note: in the source two adjacent string literals produce the combined message "DataFrame is empty. Pleaseprovide a non-empty DataFrame." due to no space between literals).
        - If df is a Spark DataFrame (or any non-pandas df) and df is not None and df.rdd.isEmpty() returns True:
            Raised with the same "DataFrame is empty. Pleaseprovide a non-empty DataFrame." message (see note above about the literal concatenation).
    NotImplementedError:
        - If df is not a pandas.DataFrame (e.g., a Spark DataFrame or other) and tsmode is True:
            "Time-Series dataset analysis is not yet supported for Spark DataFrames"
        - This branch is reached when df is not a pandas.DataFrame (the code checks isinstance(df, pandas.DataFrame) and uses the else branch for non-pandas types).

## State Changes:
    Attributes READ:
        None (the method is a pure validation routine and does not access self attributes; it only examines the provided function arguments).
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - Caller should pass the same argument values described in Args.
        - If lazy is False, df must be provided and must be non-empty (pandas: df.empty False; Spark: rdd.isEmpty() False).
        - config_file and minimal must not both be set (mutually exclusive).
    Postconditions:
        - If the function returns normally, the input combination is considered valid for subsequent profiling operations:
            * Either df is a non-empty DataFrame, or lazy is True (subject to tsmode caveat below).
            * config_file and minimal are not both set.
            * If tsmode True, df must be a pandas.DataFrame (time-series on Spark DataFrames is rejected earlier).

## Side Effects:
    - For Spark DataFrames, calling df.rdd.isEmpty() will trigger evaluation of the Spark RDD to determine emptiness; this can be an expensive distributed computation and may initiate a Spark job.
    - No file I/O, network calls, nor mutations of objects outside the scope of the provided arguments are performed by this function.

## Notes and subtle behaviors (explicitly derived from source):
    - The code uses isinstance(df, pandas.DataFrame) to decide whether to treat df as a pandas DataFrame. Any non-pandas object (including None) enters the "else" branch.
    - Consequently, if df is None and lazy is True, the initial check allows creation; however, the later isinstance check will treat df as non-pandas and, if tsmode is True, a NotImplementedError will be raised. In other words, passing df=None with lazy=True and tsmode=True will cause a NotImplementedError in the current implementation.
    - The "DataFrame is empty" message in the source is constructed from adjacent string literals ("DataFrame is empty. Please" "provide a non-empty DataFrame.") which concatenates without an intervening space, producing "DataFrame is empty. Pleaseprovide a non-empty DataFrame." This is a source-level formatting detail that appears in the raised ValueError text.

### `src.ydata_profiling.profile_report.ProfileReport.__initialize_dataframe` · *method*

## Summary:
Prepares a DataFrame for time-series analysis by optionally sorting and indexing it according to the report configuration; returns the (possibly transformed) DataFrame without modifying ProfileReport instance state.

## Description:
This static helper is invoked from ProfileReport.__init__ to perform DataFrame-specific initialization when time-series mode is enabled. Known caller:
- ProfileReport.__init__: called as self.df = self.__initialize_dataframe(df, report_config) during object construction, before other attributes (e.g., self.config, self._summarizer) are set.

Purpose of having this logic in a dedicated method:
- Isolates DataFrame pre-processing for time-series analysis (sorting and indexing) from the rest of the constructor.
- Makes the initialization step testable and readable, and avoids inlining DataFrame manipulation logic inside the constructor.

## Args:
    df (Optional[Union[pd.DataFrame, sDataFrame]]):
        The input dataset to initialize. Expected to be either a pandas.DataFrame or a Spark DataFrame (the code branches only handle pandas.DataFrame).
        - None means "no DataFrame provided"; the method will simply return None.
        - If a Spark DataFrame is provided, no pandas-specific operations are applied and the input is returned unchanged.
    report_config (Settings):
        The report configuration object. Required attributes used by this method:
        - report_config.vars.timeseries.active (bool): enables time-series initialization when True.
        - report_config.vars.timeseries.sortby (Optional[str]): optional column name to sort by and set as index.
        The Settings object is expected to provide attribute access to the nested vars.timeseries attributes as shown.

## Returns:
    Optional[Union[pd.DataFrame, sDataFrame]]:
        - If df is None: returns None.
        - If df is not an instance of pandas.DataFrame (e.g., a Spark DataFrame): returns the original df unchanged.
        - If df is a pandas.DataFrame and report_config.vars.timeseries.active is False: returns the original df unchanged.
        - If df is a pandas.DataFrame and report_config.vars.timeseries.active is True:
            - If report_config.vars.timeseries.sortby is truthy (a column name string):
                Returns a new pandas.DataFrame sorted by that column, with that same column set as the index (drop=False so the column remains as a regular column). The returned DataFrame's index.name is set to None.
            - If report_config.vars.timeseries.sortby is falsy (None/empty string):
                Returns a new pandas.DataFrame sorted by its existing index (df.sort_index()).
        The returned DataFrame is the transformed DataFrame; the original object passed in is not guaranteed to be preserved (pandas operations return new objects).

## Raises:
    - KeyError:
        Raised by pandas if report_config.vars.timeseries.sortby is set to a column name that does not exist in df.columns (triggered by df.sort_values or df.set_index).
    - TypeError / ValueError:
        Potentially raised by pandas operations if the sort/index operations cannot be performed due to incompatible dtypes or invalid arguments.
    - No explicit exceptions are raised by this method itself; any exceptions are those thrown by underlying pandas operations.

## State Changes:
    Attributes READ:
        - None on self (method is a staticmethod and does not access self attributes).
        - Reads report_config.vars.timeseries.active
        - Reads report_config.vars.timeseries.sortby
    Attributes WRITTEN:
        - None on self. The method returns a (possibly new) DataFrame; it does not assign or mutate ProfileReport attributes.

## Constraints:
    Preconditions:
        - report_config must be a Settings-like object exposing vars.timeseries.active (bool) and vars.timeseries.sortby (Optional[str]).
        - If df is a pandas.DataFrame and time-series active is True, the code assumes that any sortby value refers to a column present in df.columns.
        - If df is a Spark DataFrame and timeseries is requested, upstream validation (ProfileReport.__validate_inputs) is expected to prevent this combination; this method will not apply pandas-specific logic to Spark DataFrames.
    Postconditions:
        - If a pandas.DataFrame was returned and time-series active was True:
            - If sortby was provided: the returned DataFrame is sorted by that column, that column is also the index (column not dropped), and the index name is None.
            - If sortby was not provided: the returned DataFrame is sorted by its index.
        - If df was None or a non-pandas DataFrame, the returned value equals the original input (no transformation by this method).

## Side Effects:
    - No I/O or external service calls.
    - Does not mutate any state on the ProfileReport instance.
    - The only observable mutation is the returned DataFrame (pandas operations return new DataFrames rather than mutating in-place in this code path). Downstream code that assigns the return value (e.g., self.df = ...) will replace the stored DataFrame with the transformed one.

## Notes / Implementation details to reproduce:
    - Use a static method taking the DataFrame and Settings instance as inputs.
    - Guard the timeseries logic with:
        if df is not None and isinstance(df, pd.DataFrame) and report_config.vars.timeseries.active:
            ...
    - For the 'sortby' branch: call df.sort_values(by=sortby) then df.set_index(sortby, drop=False) and set df.index.name = None.
    - For the no-'sortby' branch: call df.sort_index().
    - Return the (possibly transformed) df at the end.

### `src.ydata_profiling.profile_report.ProfileReport.invalidate_cache` · *method*

## Summary:
Invalidates cached artifacts on the ProfileReport instance by setting one or more internal cache attributes to None so that they will be recomputed on next access.

## Description:
Known callers:
    - No internal callers were found in the surrounding ProfileReport class source. This method is intended as a public API to be invoked by client code or higher-level control flows that need to force cache refresh.
    - Typical call contexts:
        * After mutating or replacing the underlying DataFrame (self.df) externally.
        * After changing configuration (self.config) or other inputs that affect the generated report.
        * When wanting to free memory by removing cached large objects (HTML, widgets, JSON, or report structure).
Lifecycle stage:
    - Invoked between data/config mutation and subsequent rendering or description access; it prepares the object so subsequent property access (description_set, report, html, json, widgets) will recompute fresh values.

Why this is its own method:
    - Centralizes all cache-clearing logic in one place rather than duplicating attribute resets in multiple methods.
    - Provides controlled partial invalidation via the subset parameter (rendering vs report vs full), enabling callers to clear only the necessary caches and avoid unnecessary recomputation.
    - Improves maintainability and ensures consistent behavior and error messaging.

## Args:
    subset (Optional[str]): Which portion of the cache to invalidate.
        - Allowed values: None, "rendering", "report"
        - Default: None
        - Semantics:
            * None: Fully invalidate everything (rendering caches, report structure, and description set).
            * "rendering": Invalidate only rendering caches (widgets, json, html) so that visual/serialized outputs are re-created but the report/description remains cached.
            * "report": Invalidate rendering caches and the report structure, but keep the description_set cached.

## Returns:
    None

## Raises:
    ValueError: Raised when subset is not one of the accepted values.
        - Exact condition: subset is not None and subset not in ["rendering", "report"]
        - Exact message: "'subset' parameter should be None, 'rendering' or 'report'"

## State Changes:
Attributes READ:
    - None of the self.<attr> cache fields are read by this method; it only evaluates the subset argument.
Attributes WRITTEN:
    - self._widgets: set to None when subset is None or subset in ["rendering", "report"]
    - self._json: set to None when subset is None or subset in ["rendering", "report"]
    - self._html: set to None when subset is None or subset in ["rendering", "report"]
    - self._report: set to None when subset is None or subset == "report"
    - self._description_set: set to None when subset is None

    Conditional summary:
        * subset == None  -> _widgets, _json, _html, _report, _description_set all set to None
        * subset == "rendering" -> _widgets, _json, _html set to None (report and description_set left intact)
        * subset == "report" -> _widgets, _json, _html, _report set to None (description_set left intact)

## Constraints:
Preconditions:
    - The instance (self) must be a ProfileReport object; no other preconditions are required.
    - If subset is provided, it must equal "rendering" or "report" (otherwise a ValueError is raised).
Postconditions:
    - After successful return, the specified internal cache attributes are None and will be lazily recomputed on next access to the corresponding properties (widgets, json, html, report, description_set).

## Side Effects:
    - Mutates only in-memory attributes on self; no file I/O, network calls, or other external side effects.
    - No direct calls to other services or modules are performed by this method.
    - Clearing large cached objects may reduce memory usage and cause subsequent operations to perform expensive recomputation.

### `src.ydata_profiling.profile_report.ProfileReport.typeset` · *method*

## Summary:
Lazily create and cache a ProfilingTypeSet (a VisionsTypeset) on the ProfileReport instance and return it, ensuring subsequent accesses reuse the same typeset instance.

## Description:
Provides a single access point that returns the report's VisionsTypeset. The method initializes the typeset only once (lazy initialization / memoization) by constructing a ProfilingTypeSet with the report configuration and the report's type schema when first requested, and returns the cached instance thereafter.

Known callers and context:
- Invoked whenever code requires the VisionsTypeset used for type inference, type checking, or type-aware operations during profiling/report generation. Typical call sites include the data description/summarization pipeline and report rendering steps that need type information.
- It is separated into its own method to centralize the lazy-init and caching logic so that other parts of the ProfileReport can simply request a typeset without duplicating initialization code or needing to know caching details.

## Args:
    None

## Returns:
    Optional[VisionsTypeset]: The cached VisionsTypeset instance stored on self._typeset. If not previously initialized, returns a new ProfilingTypeSet(self.config, self._type_schema) (which is a VisionsTypeset) and caches it on self._typeset before returning. The return is always the same instance on subsequent calls unless external code mutates self._typeset.

## Raises:
    None explicitly. Any exception raised by ProfilingTypeSet(self.config, self._type_schema) (for example, exceptions raised from its constructor due to invalid config or schema) will propagate to the caller.

## State Changes:
Attributes READ:
    - self._typeset (checked to decide whether initialization is needed)
    - self.config (passed to ProfilingTypeSet constructor when creating)
    - self._type_schema (passed to ProfilingTypeSet constructor when creating)

Attributes WRITTEN:
    - self._typeset (set to a new ProfilingTypeSet instance on first initialization)

## Constraints:
Preconditions:
    - self.config and self._type_schema should be in a valid state acceptable to ProfilingTypeSet's constructor. If they are invalid, the constructor may raise.
    - Method expects self._typeset attribute to exist (it checks/reads it); typical class initialization should set or ensure this attribute is present (possibly None).

Postconditions:
    - After a successful call, self._typeset is guaranteed to hold a ProfilingTypeSet instance (a VisionsTypeset), and the method returns that instance.
    - Subsequent calls will return the cached instance without constructing a new ProfilingTypeSet.

## Side Effects:
    - No I/O or external service calls.
    - Side-effect limited to mutating the ProfileReport instance by assigning self._typeset on first initialization.
    - Any side effects produced by ProfilingTypeSet's constructor (if it performs I/O or global state changes) will also occur and propagate; this method does not suppress or handle such side effects.

### `src.ydata_profiling.profile_report.ProfileReport.summarizer` · *method*

## Summary:
Lazily create and return the report's summarizer instance, storing it on the object if it did not exist before.

## Description:
This property accessor ensures a BaseSummarizer is available for the profiling pipeline. It returns an existing summarizer if previously provided or constructed; otherwise it constructs a PandasProfilingSummarizer using the report's current typeset and caches it on the ProfileReport instance.

Known callers and lifecycle stage:
- ProfileReport.description_set: called during description generation when building the dataset summary (the summarizer is passed to describe_df).
- ProfileReport.__init__: external code may pass a summarizer at construction time via the summarizer parameter; that user-provided summarizer is stored on self._summarizer and will be returned unchanged by this property.
- Any other internal pipeline stage that needs a summarizer instance (e.g., custom rendering or reporting steps) will call this property as the canonical accessor.

Why this is its own method:
- Implements lazy initialization to avoid constructing potentially expensive summarizer objects until actually needed.
- Centralizes dependency injection: a summarizer can be provided at construction time (for non-default behavior or testing) but otherwise a default PandasProfilingSummarizer is created.
- Keeps creation logic isolated so other components read a consistent cached instance and do not need to know how to construct a default summarizer.

## Args:
None (property; no arguments).

## Returns:
BaseSummarizer
    - The summarizer instance stored on the ProfileReport.
    - If a summarizer was supplied at initialization (self._summarizer not None), that same instance is returned.
    - Otherwise, a new PandasProfilingSummarizer(self.typeset) is created, assigned to self._summarizer, and returned.

Edge cases:
    - If self._summarizer was set to None explicitly before calling, a new PandasProfilingSummarizer is constructed.
    - The concrete runtime type is typically PandasProfilingSummarizer but is typed as BaseSummarizer.

## Raises:
None directly. No exceptions are raised by the accessor itself.

## State Changes:
Attributes READ:
    - self._summarizer: checked to decide whether to create a new summarizer.
    - self.typeset: accessed when constructing a new PandasProfilingSummarizer (this invokes the typeset property, which may itself create/modify self._typeset).

Attributes WRITTEN:
    - self._summarizer: may be assigned a newly created PandasProfilingSummarizer instance if previously None.

## Constraints:
Preconditions:
    - The ProfileReport instance (self) must be initialized (typical object invariants from __init__ hold). No other explicit preconditions.

Postconditions:
    - After calling, self._summarizer is guaranteed to be non-None (it will contain the returned BaseSummarizer instance).
    - Subsequent calls will return the same cached instance unless self._summarizer is mutated elsewhere (e.g., via direct assignment or invalidate_cache).

## Side Effects:
    - Allocates a PandasProfilingSummarizer object when creating a new summarizer (in-memory object creation).
    - May indirectly cause creation/modification of self._typeset because the typeset property is accessed when constructing the summarizer.
    - No I/O, external service calls, or global state modifications are performed by this accessor.

### `src.ydata_profiling.profile_report.ProfileReport.description_set` · *method*

## Summary:
Lazily compute and cache the full profiling BaseDescription for the report by delegating to the dataset-describing workflow; sets an internal cached description on first access.

## Description:
This property returns the profiling summary (BaseDescription) for the ProfileReport's dataframe. It is a lazy, cached accessor: on first access it calls the centralized profiling orchestration (describe/describe_df) with the report configuration, dataset, summarizer, typeset and optional sampling instructions, stores the result in self._description_set, and returns it. Subsequent accesses return the cached BaseDescription until invalidate_cache clears it.

Known callers and lifecycle stage:
- Accessed internally by other ProfileReport properties and renderers when building the final report:
  - report (property) — builds the report structure using the description
  - _render_html and to_html — use description_set to get title, date and package metadata
  - _render_json and to_json — serialize description_set to JSON
  - _render_widgets / widgets / to_widgets / to_notebook_iframe — may read description_set for table counts and samples
  - get_description, get_sample, get_duplicates, get_rejected_variables — convenience accessors that return data from the description
- It is called during the report-generation stage (presentation/rendering or serialization) when a caller needs the computed profiling results, and is typically invoked lazily (only when an API consumer requests report/html/json/widgets/description).

Why this logic is a separate method/property:
- The profiling orchestration (summarization, correlations, scatter matrices, missing diagrams, sampling, duplicates, alerts, etc.) is a heavyweight, multi-step operation. Extracting the call into this single cached property centralizes the lazy evaluation and caching behavior so callers can request the description without duplicating orchestration or caching logic. It separates concerns: ProfileReport manages lifecycle and caching, while the describe/describe_df function manages the profiling workflow.

## Args:
None (this is a no-argument property that operates on self).

## Returns:
BaseDescription
    - The full profiling description produced by the profiling orchestration. This object contains analysis metadata, table-level statistics, per-variable summaries, correlations, scatter results, missing-diagram outputs, alerts, sample(s) and duplicate information.
    - Edge cases:
        * When the underlying DataFrame has zero rows the returned BaseDescription is still a BaseDescription but may contain empty/zeroed subfields (e.g., correlations may be an empty dict).
        * If an error occurs during profiling (for example, if no DataFrame is present), an exception is propagated instead of returning a description.

## Raises:
Propagates exceptions raised by the underlying profiling routine (describe/describe_df) and its helpers. Notably:
    - ValueError("Can not describe a `lazy` ProfileReport without a DataFrame."): raised when the ProfileReport was constructed lazily without a DataFrame and the caller attempts to compute the description (this is raised by the profiling orchestration).
    - Any exception raised by helper routines used during profiling (summarizer, preprocessors, correlation/scatter/missing-diagram generators, sampling, duplicate detection, alert computation) will propagate upward.

## State Changes:
Attributes READ:
    - self.config
    - self.df
    - self.summarizer
    - self.typeset
    - self._sample

Attributes WRITTEN:
    - self._description_set (set to the BaseDescription result on first successful computation)

## Constraints:
Preconditions:
    - If the ProfileReport was constructed in lazy mode without a DataFrame (self.df is None), calling this property will cause the profiling routine to raise ValueError. Callers should ensure a DataFrame is present or avoid calling the property.
    - self.config must be a valid Settings-like object expected by the profiling routine (provides options such as progress_bar, timeseries settings, and config.json()).
    - self.summarizer and self.typeset must be compatible with the profiling helpers that compute per-variable summaries.

Postconditions:
    - On successful return, self._description_set is a populated BaseDescription reflecting the current state of self.df and self.config.
    - Subsequent accesses return the cached BaseDescription until invalidate_cache clears self._description_set.

## Side Effects:
    - Performs potentially expensive CPU work and memory allocation (per-variable summarization, correlations, scatter matrix construction, sampling, duplicate detection).
    - May emit progress output if self.config.progress_bar is enabled (because the profiling orchestration uses progress bars).
    - The profiling orchestration may internally preprocess the DataFrame; that preprocessing may return a substituted DataFrame for internal use, but the method itself only sets self._description_set and does not reassign self.df in this property.
    - No direct I/O (file, network) is performed by this property itself; however, helpers invoked during profiling may perform non-local operations which will propagate (and are not triggered by this property directly).

### `src.ydata_profiling.profile_report.ProfileReport.df_hash` · *method*

## Summary:
Lazily compute and cache a stable hash string for the report's underlying DataFrame; subsequent calls return the cached value.

## Description:
This property implementation computes an identifier for the current DataFrame by delegating to the shared hash_dataframe utility and stores it on the ProfileReport instance. Known callers and context:
- Accessed whenever external code or user code reads ProfileReport.df_hash (there are no explicit direct internal callers in this file).
- Intended to be used during reporting workflows to identify or compare DataFrame contents (e.g., to detect changes or for caching/compare routines), and thus lives on the ProfileReport object as a cached, lazily-evaluated property.

Reason for being a separate method:
- Centralizes the DataFrame-hashing logic and keeps the property accessor concise.
- Ensures the hash is computed lazily and cached (avoiding repeated expensive computations) and isolates the dependency on the hash_dataframe utility so the hashing strategy can be changed without modifying callers.

## Args:
None.

## Returns:
Optional[str]
- None: returned when self.df is None (no DataFrame available).
- str: when a DataFrame is present, returns the value produced by hash_dataframe(self.df). In the current implementation of hash_dataframe this is a string prefixed with a HASH_PREFIX followed by the SHA-256 hexadecimal digest of the DataFrame content (computed via pandas hashing utilities).

## Raises:
- No exceptions are explicitly raised by this property implementation.
- Any exception raised by the underlying hash_dataframe call (for example, AttributeError/TypeError if the provided self.df is not in a format hash_dataframe accepts) will propagate to the caller.

## State Changes:
Attributes READ:
- self._df_hash
- self.df

Attributes WRITTEN:
- self._df_hash (set to the computed hash string when it was previously None and self.df is not None)

## Constraints:
Preconditions:
- The ProfileReport instance exists.
- If a non-None value is returned, self.df must be in a form accepted by the hash_dataframe utility (typically a pandas.DataFrame or any DataFrame-like object that hash_dataframe can process).

Postconditions:
- If self.df was None prior to call, self._df_hash remains None and the method returns None.
- If self.df was not None and self._df_hash was None prior to call, self._df_hash is set to the result of hash_dataframe(self.df) and that value is returned.
- If self._df_hash was already set, it is unchanged and returned.

## Side Effects:
- Mutates the ProfileReport instance by assigning to self._df_hash when appropriate.
- Does not perform I/O, network access, or modify external objects (other than setting the attribute on self).
- Any low-level exceptions from hash_dataframe may have side effects if hash_dataframe itself performs conversions; this property simply delegates and will propagate such exceptions.

### `src.ydata_profiling.profile_report.ProfileReport.report` · *method*

## Summary:
Lazily construct and return the cached presentation tree (Root) for the profiling report; on first access builds the structure from the current config and description_set and caches it on the instance.

## Description:
- Known callers and context:
    - ProfileReport.__init__: when constructed with lazy=False the initializer forces construction by evaluating this property.
    - ProfileReport._render_html: obtains the report to render the HTML representation.
    - ProfileReport._render_widgets: obtains the report to render widget output.
    - ProfileReport.html (property) / to_html(): triggers HTML rendering which depends on this property.
    - ProfileReport.widgets (property) / to_widgets(): triggers widget rendering which depends on this property.
    - Any external code that needs the presentation tree (e.g., custom renderers or comparison utilities) may access this property to obtain the Root object.
    - Lifecycle stage: typically invoked at render/serialization time (rendering to HTML/widgets) or during eager initialization (lazy=False).
- Rationale:
    - Building the Root presentation tree is potentially expensive; centralizing construction and caching here avoids redundant recomputation and keeps the caching policy consistent. Placing this logic in one property avoids duplicating get_report_structure calls across renderers.

## Args:
    None.

## Returns:
    Root
    - Type: ydata_profiling.report.presentation.core.Root.
    - Behavior: if self._report is None, calls get_report_structure(self.config, self.description_set), assigns the returned value to self._report, and returns it. Otherwise returns the cached self._report.
    - Edge cases: if get_report_structure unexpectedly returns None or a non-Root object, that value is cached and returned (the code does not validate the return type). Normal operation expects a Root instance.

## Raises:
    - This property does not raise its own new exception types.
    - Exceptions raised while computing self.description_set (e.g., data analysis errors, configuration errors) or by get_report_structure will propagate to the caller. Examples include runtime errors from dataframe processing, misconfigured Settings, or third-party library exceptions.
    - No explicit thread-synchronization is performed; concurrent calls from different threads may lead to race conditions (e.g., multiple constructions or partial writes).

## State Changes:
- Attributes READ:
    - self._report: checked to determine whether reconstruction is necessary.
    - self.config: read and passed to get_report_structure.
    - self.description_set: accessed and passed to get_report_structure (accessing this property may itself compute and mutate other lazy attributes).
- Attributes WRITTEN:
    - self._report: set to the value returned by get_report_structure when it was previously None.

## Constraints:
- Preconditions:
    - self.config must be initialized to a valid Settings object (the ProfileReport constructor ensures this in normal usage).
    - If description_set cannot be computed due to an invalid dataframe or configuration, the property access will propagate the underlying error; callers should ensure the ProfileReport was constructed with valid inputs or be prepared to handle such errors.
- Postconditions:
    - After a successful call, self._report holds the constructed Root object (non-None under normal operation), and the same object will be returned on subsequent accesses until invalidate_cache sets self._report back to None.
    - No additional internal caching beyond self._report is modified by this property itself (although accessing description_set may create or update other lazy attributes like self._description_set, self._summarizer, or self._typeset).

## Side Effects:
    - Potentially expensive computation: constructing the report triggers get_report_structure which depends on description_set; computing description_set can perform full DataFrame analysis and create or modify other lazy attributes.
    - Mutates the ProfileReport instance by setting self._report on first construction.
    - No direct I/O, networking, or external system side effects are performed by this property itself; any such effects would originate from functions called during report construction.
    - Not thread-safe: concurrent initial access may lead to multiple constructions or race conditions; callers requiring thread-safety should synchronize externally (e.g., with a lock).
    - Cached report can be cleared by calling ProfileReport.invalidate_cache(subset="report") or invalidate_cache() with subset None.

### `src.ydata_profiling.profile_report.ProfileReport.html` · *method*

## Summary:
Lazily produce and cache the full HTML report for this ProfileReport instance and return it as a string; subsequent calls return the cached HTML without re-rendering.

## Description:
This property is the single-point accessor for the rendered HTML representation of the profile. On first access (when no cached HTML exists) it invokes the internal rendering routine to generate the HTML and stores it on the instance for future calls.

Known callers and usage contexts:
- ProfileReport.to_html(): returns this property's value when the report is requested for export or display.
- ProfileReport.to_file(): requests the HTML via to_html when writing an HTML report to disk.
- External user code or utilities that call profile.html or access the property to embed, save, or display the report.
Lifecycle stage: invoked during the report export/rendering stage — i.e., when the user or a downstream consumer requests the HTML representation. The property is used whenever the report needs to be produced or reused without additional rendering cost.

Rationale for being a separate method/property:
- Encapsulates lazy evaluation + caching of an expensive rendering operation so that the HTML is rendered only once per cache lifecycle.
- Keeps rendering logic separate (in _render_html) so callers don't need to know the rendering details and so the cache management is centralized.

## Args:
This is a property and takes no arguments.

## Returns:
str: The complete HTML document as a Unicode string. On the first call, the value is produced by _render_html(); on subsequent calls the previously cached string (self._html) is returned.
Edge-case returns:
- If _render_html raises an exception, no string is returned and self._html remains None (the exception is propagated).
- There is no case in the property itself where it returns None; it either returns the cached string or the string returned by _render_html.

## Raises:
This property does not raise exceptions itself, but it will propagate any exceptions raised by the internal renderer _render_html. Example sources of propagated errors (originating in _render_html):
- Rendering failures from HTMLReport.render
- Exceptions from html minification if enabled
- Any runtime error raised by objects accessed during rendering (e.g., missing configuration attributes)
All such exceptions are not caught here and will bubble up to the caller.

## State Changes:
Attributes READ:
- self._html: checked to determine whether rendering is required

Attributes WRITTEN:
- self._html: set to the result of self._render_html() when the cache is empty; subsequent calls do not modify it

Other calls:
- Calls self._render_html() when self._html is None. The called method may read or mutate additional attributes (for example self.report, self.config, and self.description_set) and may perform further side effects; those are not mutated by this property directly but may be affected by the rendering routine.

## Constraints:
Preconditions:
- None specific to this property. However, correct rendering depends on the object's configuration and description state; if those are invalid or incomplete, _render_html may raise.

Postconditions:
- After a successful call, self._html is guaranteed to hold a string equal to the returned value.
- After a failed call (exception), self._html remains unchanged (typically None) and the exception is raised to the caller.

## Side Effects:
Direct side effects by this property:
- Mutation of the instance cache attribute self._html.

Indirect side effects (via _render_html, which this property invokes on cache miss):
- Potential CPU work and memory allocation during rendering of the report.
- Display of a progress bar via tqdm while rendering (if enabled in configuration).
- Importing and use of rendering modules (HTMLReport, htmlmin) and their side effects.
- If configuration requests asset creation, _render_html / related flows may cause filesystem or asset-generation side effects (note: the html property itself does not perform file writes; file writes occur elsewhere such as to_file).

Notes:
- Callers that require a fresh render must call invalidate_cache(subset="rendering") (or subset=None) prior to accessing this property to ensure _render_html executes again.

### `src.ydata_profiling.profile_report.ProfileReport.json` · *method*

## Summary:
Return the cached JSON rendering of the report, computing and caching the JSON string on first access.

## Description:
Known callers and contexts:
- ProfileReport.to_json() — provides the public API for exporting the report as JSON; it simply returns this property.
- ProfileReport.to_file(output_file) — when the target file has a .json suffix, this property is used (via to_json) to obtain the JSON to write to disk.
- External code and interactive users — any caller that accesses the .json property to obtain a string representation of the report.

Lifecycle / when invoked:
- Invoked during the "render/export" stage of the report lifecycle when a JSON representation is required (exporting, saving, or programmatic access).
- The property implements lazy evaluation: rendering is deferred until the first access and then the result is cached for subsequent accesses until invalidate_cache is called.

Why this logic is a separate method:
- JSON rendering is relatively expensive (serializing the entire report summary). Separating the lazy-getter from the rendering (_render_json) keeps concerns clear: json() manages caching and retrieval, while _render_json performs the actual rendering/serialization. This makes caching, invalidation, and testing simpler.

## Args:
- None.

## Returns:
- str: A JSON-formatted string containing the serialized summary of the report (pretty-printed with indentation).
  - Typical value: JSON text produced by SerializeReport.format_summary -> encode_it -> redact_summary -> json.dumps.
  - Edge cases:
    - If rendering fails in the underlying _render_json, an exception propagates and no value is returned.
    - After a successful call, an identical str is returned for subsequent calls until cache invalidation.

## Raises:
- No exceptions are raised directly by this property method.
- Any exception raised by the underlying _render_json call (for example exceptions from formatting, encoding, or json.dumps) will propagate to the caller. The json property does not catch or convert those exceptions.

## State Changes:
Attributes READ:
- self._json — checked to determine whether a cached rendering already exists.

Attributes WRITTEN:
- self._json — assigned the output of self._render_json() when the cached value was previously None.

Indirect/Delegated reads (via _render_json):
- self.description_set — used to build the serialized summary.
- self.config — consulted by redact_summary and for progress bar settings.
- Note: these are not directly accessed by this property, but are read by the called _render_json method.

Indirect/Delegated writes:
- None performed by this property. _render_json does not modify this ProfileReport instance beyond returning a string; it only produces the JSON string which is then assigned to self._json.

## Constraints:
Preconditions:
- The ProfileReport object must be properly initialized (its __init__ completed). In practice this means any resources or configuration required by _render_json (e.g., description_set able to be produced) must be obtainable; otherwise _render_json will raise.
- There is no required argument; this is a no-argument property.

Postconditions:
- On successful return, self._json is a non-None str containing the JSON serialization of the report.
- Subsequent accesses to the .json property return the cached string without re-invoking _render_json unless invalidate_cache() clears the rendering cache.

## Side Effects:
- Mutates self._json by caching the rendered JSON string.
- May incur significant CPU and memory usage while computing and holding the serialized report.
- Calls into _render_json which uses progress reporting (tqdm). This can emit progress output depending on the configuration (self.config.progress_bar).
- No file I/O or network calls are performed by this property itself; any I/O would come from callers that consume the returned string (e.g., writing to disk in to_file).

### `src.ydata_profiling.profile_report.ProfileReport.widgets` · *method*

## Summary:
Property that returns a cached widget-based presentation of the report for interactive display; if not present, it renders the widgets via the widget renderer, caches the result on the instance, and returns it.

## Description:
- Nature:
    - Implemented as a property (access without parentheses) that manages a lazy, cached widget rendering.
- Known callers and lifecycle stage:
    - ProfileReport.to_widgets(): accesses this property and displays the returned widget in interactive environments.
    - Interactive usage in notebooks or other UIs where a consumer directly accesses report.widgets to retrieve the interactive representation.
    - Typical lifecycle: used in the "rendering/presentation" stage after the profile description/report is available; accessing this property may trigger computation of description_set and report if they have not yet been built.
- Why this logic is separate:
    - The property handles caching and a small compatibility check, while the heavy rendering work is delegated to _render_widgets(). This separation prevents duplication of rendering logic and centralizes caching invalidation behavior.

## Args:
    None

## Returns:
    Any: The widget object (or widget-like structure) produced by self._render_widgets() (i.e., WidgetReport(copy.deepcopy(report)).render()).
    - If self._widgets was already set, returns that exact cached object.
    - If rendering is required, the returned value is cached in self._widgets and then returned.
    - Concrete type/value depends on the WidgetReport flavour implementation; the method does not validate or coerce the result.
    - Edge-case returns: the underlying renderer may return None or other sentinel values; those are cached and returned unchanged.

## Raises:
    RuntimeError: When the report represents a comparison of multiple reports.
    - Trigger condition: description_set.table["n"] is a list and len(description_set.table["n"]) > 1.
    - Exact message: "Widgets interface not (yet) supported for comparing reports, please use the HTML rendering."
    Propagated exceptions:
    - Any exception raised by accessing self.description_set (e.g., errors computing the description).
    - Any exception raised by self._render_widgets(), such as copy.deepcopy(report) raising TypeError for non-deepcopyable elements, or errors from WidgetReport construction/rendering, or from tqdm.
    - The property does not catch or wrap these exceptions; they propagate to the caller.

## State Changes:
- Attributes READ:
    - self.description_set (may trigger computation of the profile description)
    - self.description_set.table["n"] (checked to detect comparing reports)
    - self._widgets (checked to determine whether rendering is needed)
- Attributes WRITTEN:
    - self._widgets (assigned the result of self._render_widgets() only when it was previously None)

## Constraints:
- Preconditions:
    - self.description_set must exist and expose a mapping-like attribute table containing key "n".
    - description_set.table["n"] is expected to be either:
        - a scalar (commonly an int) representing a single-report count, or
        - a list-like object when multiple reports are present (comparison mode).
      If it is a list with length > 1, the widgets property intentionally aborts with the RuntimeError above because widget rendering for comparisons is not supported.
- Postconditions:
    - On success, self._widgets is set to the rendered widget object and the same object is returned.
    - On failure (exception during rendering or the precondition check), self._widgets remains unchanged (i.e., still None if it was None before).

## Side Effects:
- May trigger expensive computation and increased memory usage:
    - Accessing description_set can compute the full profile description.
    - _render_widgets() typically performs copy.deepcopy(self.report) and runs the WidgetReport renderer, which can increase memory and CPU usage.
- User-visible progress output:
    - Uses tqdm to emit progress UI when self.config.progress_bar is True; this may render a progress bar in console or notebook.
- Caching and invalidation:
    - The returned widget object is cached in self._widgets. To force a re-render, call self.invalidate_cache(subset="rendering") or invalidate_cache() (which resets self._widgets among other caches).
- External side effects:
    - The property itself performs no file, network I/O. Any such effects would be caused by the underlying WidgetReport.render() and are not suppressed here.
- Concurrency:
    - Not thread-safe: concurrent accesses may cause multiple render operations if two threads read self._widgets concurrently when it is None. There is no internal locking.
- Usage example (interactive context):
    - Create a report and access/display the widgets:
      report = ProfileReport(df)
      display(report.widgets)

### `src.ydata_profiling.profile_report.ProfileReport.get_duplicates` · *method*

## Summary:
Return the duplicates DataFrame produced by the profile description, triggering lazy computation of the description set if it has not yet been computed.

## Description:
- Usage context:
    - This is a public accessor on ProfileReport that exposes the duplicates analysis computed by the profiling engine.
    - It does not itself compute duplicates; it returns the value of the duplicates attribute from the object's description set.

- Why this is a separate method:
    - Provides a concise, stable API to retrieve duplicates without requiring callers to access the description_set property directly.
    - Encapsulates the lazy-initialization behavior of the description set so callers do not need to manage initialization.

## Args:
    None

## Returns:
    Optional[pd.DataFrame]:
        - The value of self.description_set.duplicates, typically a pandas DataFrame containing duplicate-row/group information as produced by the profiling describe routine.
        - May be None if the description generator sets duplicates to None (for example, when duplicates are not applicable or no duplicates were found).
        - The exact schema and semantics of the returned DataFrame are defined by the profiling/description implementation (BaseDescription.duplicates) and are not modified by this method.

## Raises:
    - This method does not raise explicit exceptions itself.
    - Any exceptions raised while creating or accessing the description_set (for example, errors from the underlying describe routine) will propagate to the caller.

## State Changes:
- Attributes READ:
    - self._description_set (accessed via the description_set property)
    - indirectly may read self.df during description computation

- Attributes WRITTEN:
    - self._description_set may be assigned (set) as a result of lazy initialization performed by the description_set property

## Constraints:
- Preconditions:
    - The ProfileReport instance must be a valid instance (constructed without fatal errors). No arguments are required.
    - No other preconditions are enforced by this method itself.

- Postconditions:
    - After a successful call, self._description_set will be initialized (set to the computed BaseDescription instance) unless an exception occurred during its computation.
    - The return value will equal the duplicates attribute of the initialized description set (possibly None).

## Side Effects:
    - May trigger potentially expensive, lazy computation by initializing the description set (which constructs/aggregates profile summaries).
    - Does not perform I/O or interact with external services; the only mutation is possibly setting self._description_set.

### `src.ydata_profiling.profile_report.ProfileReport.get_sample` · *method*

## Summary:
Return the profiling "sample" produced by the description set — a direct accessor that exposes the sample payload computed by the profiling pipeline and may cause the description set to be lazily initialized.

## Description:
- Known callers and lifecycle stage:
    - This is a public accessor intended for callers (user code, notebooks, or client code) that need to inspect the representative sample discovered by the profiling process. It is typically invoked after creating a ProfileReport and when the user wants to retrieve the sample for display, debugging, or downstream processing.
    - Internally, other methods in ProfileReport access the full description set directly; get_sample exists as a convenience and stable API for retrieving only the sample portion without requiring callers to depend on the internal description_set structure.

- Why this logic is a separate method:
    - Encapsulates access to the sample so external code does not need to reach into description_set directly.
    - Provides a stable, small-surface API for clients; keeps potential lazy initialization and side effects (heavy compute of description_set) hidden from callers unless they explicitly request the sample.
    - Simplifies backward compatibility: callers expecting a mapping-like sample can call this method even if the underlying description_set internals change.

## Args:
    This method accepts no arguments.

## Returns:
    dict
    - The method returns the raw sample object as stored on the profile's description set.
    - Typical structure (as produced by the profiling pipeline's Sample model or equivalent mapping) is a mapping/dictionary containing at least:
        - "id" (str): sample identifier
        - "data" (any): payload for the sample (e.g., a row / dict / structured payload)
        - "name" (str): human-readable name for the sample
        - "caption" (Optional[str]): optional caption
    - Edge cases:
        - If the profiling pipeline did not produce a sample, the returned value may be an empty dict or another empty/absent sentinel depending on how the description set was constructed.
        - The method returns the value exactly as stored on description_set.sample (it does not call .dict() or otherwise transform Pydantic Sample instances).

## Raises:
    - The method itself performs a direct access and does not raise custom exceptions, but because it accesses the description_set property it can surface exceptions raised during lazy computation of the description set:
        - ValueError: e.g., if the underlying DataFrame was empty and the profiling pipeline or validation layer raises such an error.
        - NotImplementedError: e.g., timeseries-on-Spark limitations surfaced by the pipeline.
        - pydantic.ValidationError: if Sample construction/validation fails while computing the description set.
        - Any other exceptions propagated by the profiling/describe pipeline (describe_df and code it calls).
    - Note: callers who need to handle these should catch exceptions from the profiling pipeline rather than expect get_sample to handle them.

## State Changes:
- Attributes READ:
    - self.description_set (property) — reading this property is how the method obtains the sample.
    - Indirectly reads fields used by description_set computation (e.g., self.df, self._sample) when the property must be initialized.

- Attributes WRITTEN:
    - self._description_set — if the description set has not yet been computed, accessing self.description_set will lazily initialize and assign self._description_set. get_sample therefore may mutate this attribute as a side-effect.
    - get_sample does not modify self._sample, self.df, or other profiling outputs.

## Constraints:
- Preconditions:
    - The ProfileReport instance must be validly constructed. If the object was constructed in a state that makes description_set computation invalid (for example, a missing DataFrame in a non-lazy initialization scenario), accessing the sample may raise pipeline/validation errors.
    - No arguments are required.

- Postconditions:
    - After a successful call, the returned value is the description_set.sample mapping (as stored on the description set).
    - If the description set was not yet computed, calling this method guarantees _description_set is computed and cached on the instance (unless an exception aborts computation).

## Side Effects:
    - May trigger an expensive, synchronous computation: if self._description_set is None, reading self.description_set will run the profiling/describe pipeline, which can be CPU- and memory-intensive and may take significant time for large datasets.
    - No external I/O (file/network) is performed directly by this method, but the describe pipeline invoked by description_set might perform memory allocations and CPU work.
    - Does not mutate caller-provided objects other than caching the computed description set on self._description_set.

## Example usage:
    - After creating a ProfileReport (report = ProfileReport(df)), call report.get_sample() to obtain the sample mapping. The call may be slow on first access due to lazy profiling.

### `src.ydata_profiling.profile_report.ProfileReport.get_description` · *method*

## Summary:
Return the cached profiling summary container for this report, triggering lazy computation if the summary has not yet been produced.

## Description:
This accessor returns the ProfileReport's description container (a BaseDescription) which aggregates all profiling outputs for the dataset associated with this ProfileReport instance.

Known callers / lifecycle:
- Intended as a public API for users or external code to retrieve the full profiling description after creating a ProfileReport.
- Used by external serializers, renderers, or downstream code that consumes profiling results (e.g., custom exporters or tests).
- Within the profiling lifecycle it is typically called after the ProfileReport is instantiated and before rendering or exporting (for example, before calling to_json(), to_html(), or building a custom report). The class itself uses the underlying description_set property in several internal methods (rendering, JSON/HTML export), but there are no internal call-sites in this class that call get_description() directly; it exists to provide a stable public accessor.

Why this is a separate method:
- Provides an explicit, simple public API method to retrieve the profiling description instead of requiring consumers to access the property directly.
- Encapsulates the intent (retrieve the profiling summary) and shields callers from implementation details (lazy population via the description_set property).

## Args:
    None

## Returns:
    BaseDescription
        The BaseDescription instance that contains analysis metadata, table-wide statistics, per-variable summaries, correlations, missingness, alerts, samples, duplicates, and package metadata. This is the same object as the profile_report.description_set property returns (i.e., self._description_set once populated).

        Edge cases:
        - If the internal description cache (self._description_set) is not yet populated, accessing this will trigger the property's lazy computation that produces and stores a BaseDescription; callers always receive a BaseDescription instance once the call returns.

## Raises:
    None explicitly raised by this method.
    (Note: retrieving the description may cause the lazy computation to run; any exceptions thrown by that computation are propagated but are not raised by this method itself.)

## State Changes:
    Attributes READ:
        - self.description_set (property access)
        - transitively (during lazy computation, if triggered): self._description_set, self.config, self.df, self._summarizer, self._typeset, self._sample

    Attributes WRITTEN:
        - self._description_set (only if it was previously None and the lazy computation runs; the method itself does not directly assign this attribute, but accessing description_set may)

## Constraints:
    Preconditions:
        - The ProfileReport instance must be a valid instance (constructed). No arguments are required.
        - If the description_cache is not yet populated, the object should have been initialized sufficiently so that the profiling describe routine (invoked by the description_set property) can run (i.e., required attributes like self.config and self.df should be in a usable state).

    Postconditions:
        - After the call returns, self.description_set will be available and a BaseDescription instance will be returned.
        - If the description had to be computed, self._description_set will be set to the computed BaseDescription.

## Side Effects:
    - May trigger potentially expensive computation (the profiling "describe" routine) if the description has not yet been computed. This computation occurs inside the description_set property and may perform heavy CPU/memory work; it can also take non-trivial time and allocate sizeable in-memory structures.
    - May mutate the object's internal cache by assigning to self._description_set.
    - No direct I/O, external network, or file system operations are performed by this method itself; any such operations would be caused by the lazy computation invoked by the description_set property (and are not performed by get_description directly).

### `src.ydata_profiling.profile_report.ProfileReport.get_rejected_variables` · *method*

## Summary:
Return the set of variable/column identifiers that have been marked as rejected by the profiling pipeline, without modifying the report object.

## Description:
Provides a concise lookup of all columns for which the profiler has emitted alerts with category REJECTED. Typical callers are client code that inspects a generated ProfileReport to determine which variables were excluded from analysis (for example: user code that wants to skip or separately handle rejected variables, or higher-level utilities that compare or filter reports). This method is used during the analysis/report-consumption stage after the ProfileReport.description_set has been computed (the property will be computed lazily if needed).

This logic is extracted into its own method to:
- Encapsulate the filtering logic and keep callers simple (single method call to obtain rejected variables).
- Provide a stable, discoverable API on ProfileReport for programmatic access to rejected variables instead of duplicating the comprehension wherever needed.
- Centralize any future changes to the criteria for "rejected" variables in one location.

## Args:
    None

## Returns:
    set:
        A Python set containing the column identifiers (typically strings) for which an Alert with alert_type == AlertType.REJECTED exists in self.description_set.alerts.
        - If no alerts of type REJECTED exist, returns an empty set.
        - Duplicate alerts for the same column are deduplicated by the set.
        - If an alert has column_name == None (dataset-level rejected alert), None will be included in the returned set.

## Raises:
    TypeError:
        If any alert.column_name is an unhashable object (e.g., a list), attempting to add it to the returned set will raise TypeError.
    AttributeError:
        If self.description_set does not expose an iterable attribute named alerts, an AttributeError will be raised when the method attempts to iterate it.
    (Note: the method does not explicitly raise these exceptions; they arise from the underlying data shape and Python set semantics.)

## State Changes:
    Attributes READ:
        self.description_set
        self.description_set.alerts
        alert.alert_type (read for each alert)
        alert.column_name (read for each alert)

    Attributes WRITTEN:
        None — the method does not modify the ProfileReport instance or its contained objects.

## Constraints:
    Preconditions:
        - The ProfileReport instance must be initialized; if description_set has not yet been computed it will be computed by the property accessor (lazily).
        - Each element of self.description_set.alerts is expected to be an object with attributes alert_type (comparable to AlertType members) and column_name (typically str or None).

    Postconditions:
        - The ProfileReport instance is unchanged after the call.
        - The returned set contains each unique column_name for which an alert with alert_type == AlertType.REJECTED exists at the time of the call.

## Side Effects:
    - No I/O, network, or external service calls are performed.
    - No mutation of objects outside self is performed.
    - Running the method may trigger lazy evaluation of self.description_set if it is not already computed (property access may execute the profiling describe step).

### `src.ydata_profiling.profile_report.ProfileReport.to_file` · *method*

## Summary:
Export the report to disk as HTML or JSON based on the output filename, create any required HTML asset files for offline viewing, write the serialized payload to the filesystem (UTF-8), and optionally trigger a download (Google Colab) or open the file in a browser tab. This call may also cause the report's rendered HTML/JSON to be generated and cached on the instance.

## Description:
Known callers / typical use:
- User code or notebook cells that created a ProfileReport and want to persist the output to disk for sharing or archiving.
- Export steps in analysis pipelines that persist profiling results.
- Interactive notebook workflows where the user wants the file to be automatically downloaded or opened when silent=False.

Lifecycle stage:
- Invoked after creating/initializing a ProfileReport, once the report content (description_set/report) is available or can be generated on demand.
- Separates serialization/persistence logic from rendering: to_file delegates rendering to to_html()/to_json() and focuses on path handling, asset creation, file I/O, progress reporting, and environment-specific post-processing.

Why a separate method:
- Exporting involves multiple concerns: extension handling and normalization, optional creation of HTML asset bundles, writing bytes to disk, progress feedback, and optional interactive environment actions. Centralizing this logic avoids duplication and keeps rendering functions focused on producing strings.

## Args:
    output_file (Union[str, Path])
        - Destination path to write the report. Accepts a str or pathlib.Path.
        - Behavior by suffix:
            * ".json": the method calls to_json() and writes the returned JSON string verbatim.
            * ".html": the method calls to_html() and writes the returned HTML string verbatim.
            * any other suffix (including empty): the method will call to_html(), change the path to use the ".html" suffix (output_file.with_suffix(".html")), and emit a warnings.warn indicating the original extension was not supported and ".html" was assumed.
        - If a non-Path is provided, it is converted via Path(str(output_file)) before use.
    silent (bool, default True)
        - If False, after writing the file the method will first try to trigger files.download(...) in Google Colab and, if that import fails, will open a browser tab using webbrowser.open_new_tab(...). If True, no automatic browser/download action is attempted.

## Returns:
    None
    - On success the method returns None. The side effect is a UTF-8 encoded file at the final path (output_file or output_file.with_suffix(".html")) containing the serialized report.

## Raises:
    - FileNotFoundError:
        * Raised by Path.write_text when the parent directory does not exist (the method does not create missing parent directories).
    - OSError / IOError:
        * Raised if writing the file fails for other I/O reasons (permission denied, disk full, etc.). These originate from output_file.write_text(...).
    - Any exception raised by to_html() or to_json():
        * Rendering or serialization failures (including errors originating from building the report structure, formatting, or optional HTML minification) propagate directly.
    - Any exception raised by create_html_assets(self.config, output_file):
        * If asset creation fails (I/O or other errors), that exception propagates.
    - Note: ModuleNotFoundError when attempting to import google.colab is caught and handled internally (the code falls back to opening the browser). Other exceptions raised by files.download or webbrowser.open_new_tab are not caught and will propagate.

## State Changes:
Attributes READ:
    - self.config (the Settings/Config object)
    - self.config.html.inline (checked to decide whether to create external assets)
    - self.config.html.assets_prefix (read to decide whether a default prefix must be set)
    - self.config.progress_bar (controls whether tqdm is disabled)
    - Indirectly reads self.to_html() or self.to_json() which in turn read:
        * self.report and self.description_set and any attributes those properties require (e.g., self._report, self._description_set, summarizer, typeset, etc.)

Attributes WRITTEN:
    - self.config.html.assets_path is set to str(output_file.parent) when config.html.inline is False.
    - self.config.html.assets_prefix may be set to str(output_file.stem) + "_assets" when config.html.inline is False and assets_prefix is currently None.
    - Indirectly, invoking to_html() or to_json() may populate cached render results:
        * self._html (if HTML rendering occurs) and/or self._json (if JSON rendering occurs) via the property accessors.

## Constraints:
Preconditions:
    - self.config must be present and provide nested html and progress_bar configuration attributes (typical for a properly-initialized ProfileReport).
    - The caller should ensure the parent directory of output_file is writable and exists; Path.write_text does not create missing parent directories.
    - If the caller expects JSON output, they must provide a filename ending with ".json"; otherwise HTML is produced.
    - The environment where silent=False is used should allow launching a browser or support the google.colab.files API for download.

Postconditions:
    - A UTF-8 encoded file exists at the final path: either the original output_file (when ".json" or ".html" was used) or output_file.with_suffix(".html") (if a non-supported suffix was provided).
    - If config.html.inline is False, create_html_assets(self.config, output_file) was invoked and config.html.assets_path (and possibly assets_prefix) were set to values derived from the final output_file.
    - If silent is False, the method attempted to either:
        * call google.colab.files.download(output_file.absolute().as_uri()) if google.colab is importable, or
        * open a new browser tab using webbrowser.open_new_tab(output_file.absolute().as_uri()) as a fallback.
    - The instance may now have cached rendered data in self._html or self._json depending on which rendering path was taken.

## Side Effects:
    - File system writes:
        * Writes a single file with the serialized report via Path.write_text(data, encoding="utf-8").
        * May create additional asset files and directories via create_html_assets when producing non-inline HTML; these are written under output_file.parent and named according to assets_prefix.
    - Configuration mutation:
        * Mutates self.config.html.assets_path and possibly self.config.html.assets_prefix to values derived from output_file.
    - User-visible warning:
        * Emits a warnings.warn when the supplied file extension is not ".html" or ".json" and the method coerces to ".html".
    - Progress feedback:
        * Uses tqdm with total=1 and desc="Export report to file" for a single-step progress indicator; the progress bar is disabled when not self.config.progress_bar.
    - Interactive environment actions (when silent is False):
        * Tries to trigger a download in Google Colab via files.download(output_file.absolute().as_uri()), falling back to webbrowser.open_new_tab(output_file.absolute().as_uri()) if the google.colab import is unavailable.
    - No return value; errors surface via exceptions described above.

### `src.ydata_profiling.profile_report.ProfileReport._render_html` · *method*

## Summary:
Converts the in-memory report structure into a final HTML string using the HTML presentation flavour, updating a short progress indicator. The original report object is not mutated; a deep copy is rendered and returned.

## Description:
This method performs the final presentation step in the report generation pipeline: it takes the prepared report tree (self.report) and passes a deep copy to the HTML presentation renderer (HTMLReport) to produce an HTML document or fragment. It is typically invoked by higher-level export or save functions when the profiling output must be returned as HTML or written to disk/served.

Known callers / lifecycle stage:
- Called during the report export / serialization stage after analysis and summarization are complete.
- Public-facing methods that need HTML output (for example: save/html return helpers) should call this method to obtain the rendered markup.

Why it is separated:
- Rendering involves presentation-specific options (navbar, assets, theme, title/date/version) and a small UX concern (a progress bar) plus an optional post-processing minification step. Encapsulating this logic keeps presentation concerns separate from data analysis and serialization orchestration.

## Args:
None — the method uses instance state (self.*) for all inputs.

## Returns:
str
- The HTML representation produced by HTMLReport.render, possibly post-processed by an HTML minifier.
- Possible returned values:
  - A non-empty HTML document string (typical).
  - An empty string if the HTMLReport.render implementation returns an empty string.
  - A minified HTML string when config.html.minify_html is True; minification is performed with remove_all_empty_space=True and remove_comments=True.

## Raises:
This method does not explicitly raise new exceptions, but the following exceptions can propagate from its operations:

- AttributeError
  - Trigger: self, self.report, self.config, or self.description_set is None or lacks the expected nested attributes (e.g., missing self.config.html or self.description_set.analysis).
- IndexError
  - Trigger: self.config.html.style.primary_colors is an empty sequence; the code accesses primary_colors[0].
- TypeError
  - Trigger: self.config.html.style.primary_colors is not subscriptable (e.g., None or an int) or other nested attributes have the wrong type (e.g., self.config.html.inline is not boolean if downstream code expects a bool).
- KeyError
  - Trigger: "ydata_profiling_version" is missing from self.description_set.package mapping.
- Exception (propagated)
  - Trigger: any exception raised by copy.deepcopy(self.report), by HTMLReport(...) constructor or .render(...), or by the optional HTML minifier. Examples include RecursionError during deepcopy, errors raised by the HTML template rendering engine, or runtime errors in the minifier.

Implementation note:
- The method performs a local import of HTMLReport and (conditionally) re-imports the HTML minifier inside the rendering block. This guards rendering behind local imports and avoids making the top-level module import depend on optional presentation/minification backends. (A top-level import of the minifier may already exist in the file; this method still re-imports it conditionally for clarity and safe fallback.)

## State Changes:
Attributes READ:
- self.report (the report tree, any type expected by HTMLReport)
- self.config (expected types below)
  - self.config.progress_bar (bool)
  - self.config.html.navbar_show (bool)
  - self.config.html.use_local_assets (bool)
  - self.config.html.inline (bool)
  - self.config.html.assets_prefix (str or None)
  - self.config.html.style.primary_colors (Sequence[str] — must contain at least one color)
  - self.config.html.style.logo (str or None)
  - self.config.html.style.theme (str)
  - self.config.html.minify_html (bool)
- self.description_set
  - self.description_set.analysis.title (str)
  - self.description_set.analysis.date_start (datetime-like or str)
  - self.description_set.package (Mapping[str, Any]) — uses key "ydata_profiling_version"

Attributes WRITTEN:
- None. The method does not modify any self.* attribute. It creates a deep copy of self.report before rendering.

## Constraints:
Preconditions:
- self.report must be a data structure compatible with HTMLReport, as HTMLReport(copy.deepcopy(report)) will be called.
- self.config must be present and have the html nested object with the attributes listed under "Attributes READ".
- self.config.html.style.primary_colors must be a sequence (list/tuple) with at least one element.
- self.description_set must provide analysis.title and analysis.date_start, and description_set.package must be a mapping containing the key "ydata_profiling_version".
- The environment must have the HTMLReport presentation flavour available (importable as ydata_profiling.report.presentation.flavours.HTMLReport). If minification is enabled, the htmlmin package should be available (the method does a conditional import and will raise if the minifier is unavailable and called).

Postconditions:
- Returns an HTML string as described in "Returns".
- The instance (self) remains unchanged.
- The progress bar (tqdm) progresses by 1 step; if self.config.progress_bar is False, no progress output is shown.

## Side Effects:
- Displays a short progress indicator via tqdm with label "Render HTML" and total=1 unless disabled by self.config.progress_bar. The progress bar is advanced once (pbar.update()).
- Performs copy.deepcopy(self.report), which increases memory usage transiently and can raise deep-copy related exceptions.
- Locally imports presentation and minification modules; these imports can trigger module initialization side effects.
- No direct file I/O or network I/O is performed by this wrapper method itself. Downstream code (HTMLReport.render or the minifier) may perform additional side effects not introduced here.

## Reimplementation checklist (steps required to reproduce behavior):
1. Read and validate required instance attributes (report, config, description_set) meet preconditions listed above.
2. Optionally import HTMLReport locally: from ydata_profiling.report.presentation.flavours import HTMLReport.
3. Create a deep copy of self.report to avoid mutating the original.
4. Call HTMLReport(deep_copied_report).render(...) passing:
   - nav=self.config.html.navbar_show
   - offline=self.config.html.use_local_assets
   - inline=self.config.html.inline
   - assets_prefix=self.config.html.assets_prefix
   - primary_color=self.config.html.style.primary_colors[0]
   - logo=self.config.html.style.logo
   - theme=self.config.html.style.theme
   - title=self.description_set.analysis.title
   - date=self.description_set.analysis.date_start
   - version=self.description_set.package["ydata_profiling_version"]
5. If self.config.html.minify_html is truthy, import minify (from htmlmin.main import minify) and call minify(html, remove_all_empty_space=True, remove_comments=True).
6. Show/advance a progress bar (tqdm) with total=1, desc="Render HTML", disabled=not self.config.progress_bar; update once before returning.
7. Return the final HTML string.

### `src.ydata_profiling.profile_report.ProfileReport._render_widgets` · *method*

## Summary:
Renders the report as notebook/interactive widgets by delegating to the widget flavour renderer and returns the renderer's output; does not cache or modify the ProfileReport instance state.

## Description:
- What it does and when it runs:
    - Performs the rendering step that converts the internal report structure into a widget-based representation suitable for interactive display (e.g., inside a Jupyter notebook). It runs the WidgetReport rendering pipeline on a deep copy of the computed report structure.
- Known callers and lifecycle stage:
    - ProfileReport.widgets property: invoked when cached widgets are absent (self._widgets is None); the widgets property caches the returned value.
    - ProfileReport.to_widgets(): indirectly calls this through the widgets property when displaying the widgets in a notebook.
    - Typical lifecycle: invoked during the "rendering" stage of producing a report presentation for interactive use (after the report structure is generated via the report property).
- Why this is a separate method:
    - Encapsulates widget-specific rendering logic and progress reporting so the rendering can be invoked from multiple places (property accessor and explicit display methods) without duplicating code. Keeping it separate allows the widgets property to manage caching while this method performs the pure rendering work.

## Args:
    None

## Returns:
    Any: The raw result returned by WidgetReport(copy.deepcopy(report)).render().
    - The exact type/value depends on the widget flavour implementation; this method does not transform the returned value.
    - Edge-case returns: If the underlying flavour returns None or another sentinel, this method will return that same value unchanged.

## Raises:
    - Any exception raised by copy.deepcopy(report), e.g., TypeError when the report contains non-deepcopyable objects.
    - Any exception propagated from WidgetReport(...) construction or its render() call (implementation-specific).
    - Any exception propagated from tqdm context manager (unlikely but possible if stdout behavior is altered).
    - The method itself does not catch exceptions; callers should handle rendering failures.

## State Changes:
- Attributes READ:
    - self.report (property) — accesses and may trigger construction of the report Root structure via self.report
    - self.config.progress_bar — reads to determine whether to show the progress bar
- Attributes WRITTEN:
    - None. This method does not modify any self.<attr> fields (it returns the rendered widgets but does not assign them to self._widgets).

## Constraints:
- Preconditions:
    - self.config must be present and have a boolean attribute progress_bar (the code accesses self.config.progress_bar).
    - self.report must be computeable (the report property must not raise an exception when accessed).
    - The report object must be deepcopyable, or copy.deepcopy(report) will raise.
- Postconditions:
    - No attributes on self are changed by this call.
    - Returns the unmodified output from the widget flavour's render() method.

## Side Effects:
    - Console/notebook output: uses tqdm to emit a short progress indicator (subject to self.config.progress_bar). This may produce terminal or notebook progress UI during execution.
    - Memory: constructs a deep copy of the full report structure (copy.deepcopy(report)), potentially increasing memory usage during rendering.
    - Imports a flavour-specific renderer locally (ydata_profiling.report.presentation.flavours.WidgetReport) — this import may trigger module import side effects if not already loaded.
    - No network or file I/O is performed by this method itself; any such side effects would originate from WidgetReport.render() if implemented to do so.

### `src.ydata_profiling.profile_report.ProfileReport._render_json` · *method*

## Summary:
Render the report's description as a JSON-formatted string by normalizing dataclasses, pandas/numpy objects and applying configured redaction; does not mutate the object state.

## Description:
This method is the JSON serialization step of the profiling/reporting pipeline. It performs three responsibilities in sequence:
1. Obtain the profile description snapshot from self.description_set (a BaseDescription instance or equivalent mapping).
2. Normalize the description into JSON-friendly Python primitives via a local recursive encoder (encode_it) that expands dataclasses, converts pandas and numpy structures to lists/dicts, and stringifies unknown objects.
3. Apply column-level redaction rules (redact_summary) according to self.config, then produce a pretty-printed JSON string using json.dumps(indent=4).

Known callers and invocation context:
- ProfileReport.json property — when a consumer reads report.json, the property caches and returns the result of this method.
- ProfileReport.to_json() — returns the same content via the json property.
- ProfileReport.to_file() — when writing to a file whose suffix is ".json", to_file uses to_json() (thus calling this method) to obtain the JSON to write.
- External code that accesses ProfileReport.json or calls to_json() as part of report export or API responses.

Lifecycle stage:
- Invoked late in the profiling pipeline at export/serialization time, after the summary (description_set) has been computed and before writing or transmitting the result.

Why this is a separate method:
- Keeps JSON-specific normalization, redaction, and progress reporting isolated from report generation and rendering logic (HTML/widgets).
- Allows reuse by multiple callers (property, to_file) and simplifies testing of serialization behavior.

## Args:
- None. (All required inputs are read from self; no parameters are passed into the method.)

## Returns:
- str: A JSON-formatted string (indent=4) representing the normalized and redacted report description.
  - Typical value: a unicode text block containing JSON.
  - Edge cases:
    * If normalization produces objects not supported by json.dumps (e.g., Python set), json.dumps will raise a TypeError instead of returning a string.
    * If format_summary or redact_summary raise exceptions, those propagate (see Raises).

## Raises:
- TypeError: May be raised by json.dumps if the normalized structure still contains non-serializable objects (e.g., Python set). The method does not catch or transform that error.
- Any exception raised by:
    * format_summary(self.description_set) — errors during conversion of BaseDescription or nested values.
    * encode_it — rare exceptions from object methods called during normalization (e.g., .to_dict()).
    * redact_summary(description_dict, self.config) — e.g., KeyError or AttributeError if the summary shape is invalid or redaction helper fails.
  These exceptions are not swallowed and will propagate to the caller.

## Behavior details (encode_it normalization rules):
The method defines a recursive helper encode_it(o: Any) -> Any with the following deterministic rules to convert objects to JSON-friendly primitives:

- If o is a dataclass instance (is_dataclass(o) is True):
    - Replace o by dataclasses.asdict(o) and continue processing the resulting dict.

- If o is a dict:
    - Return a new dict mapping encode_it(k) -> encode_it(v) for every key/value pair. (Keys are processed by encode_it too; callers should be aware that non-string keys can remain non-string until json.dumps handles them.)

- Otherwise (non-dict values):
    - Primitive scalars: if isinstance(o, (bool, int, float, str)) -> return o unchanged.
    - list: return [encode_it(v) for v in o].
    - set: return a Python set constructed as {encode_it(v) for v in o}. (Note: JSON cannot serialize set objects directly; json.dumps will raise TypeError if a set survives.)
    - pandas.DataFrame or pandas.Series: call o.to_dict(orient="records") and return encode_it(...) applied to that result (effectively a list-of-records).
    - numpy.ndarray: call o.tolist() and return encode_it(...) on that list.
    - Sample (ydata_profiling.model.sample.Sample): call o.dict() and return encode_it(...) on that mapping.
    - numpy.generic scalar: call o.item() to obtain a native Python scalar (int/float/str/bool).
    - Any other object: fall back to str(o) and return that string.

Implementation note for reimplementation:
- The encoder is fully recursive: any nested dataclass/dict/list/array structure will be traversed until all values are converted to dict/list/scalar/string or until an unhandled object is stringified.
- Be explicit about the import aliases used by isinstance checks (e.g., pd for pandas, np for numpy) to ensure the same runtime types are recognized.

## State Changes:
Attributes READ:
- self.description_set
- self.config (at least self.config.progress_bar; redact_summary reads additional flags under config.vars.*)
Attributes WRITTEN:
- None. This method does not assign to any self.* attribute. It returns the JSON string; caching is performed by the caller (e.g., ProfileReport.json property).

## Preconditions (constraints before calling):
- self.description_set must be accessible and return a BaseDescription instance or a mapping that format_summary can accept.
- self.config must be a Settings-like object with boolean progress_bar attribute and fields expected by redact_summary (config.vars.cat.redact, config.vars.text.redact, etc.).
- format_summary(self.description_set) must return a mapping (dict-like) suitable for encode_it and redact_summary.

## Postconditions (guarantees after return):
- The method returns a str containing the JSON representation of the profile description after normalization and redaction.
- The object state (self.* fields) is unchanged by this method.

## Side Effects:
- Displays a short progress update using tqdm with description "Render JSON". Whether the progress is shown depends on self.config.progress_bar.
- No file, network, or persistent I/O is performed by this method.
- May call methods on nested objects (e.g., pandas.DataFrame.to_dict(), Sample.dict(), numpy.ndarray.tolist()) which may allocate memory proportional to the size of the description.
- Exceptions from nested conversions or json.dumps propagate to the caller; the method does not catch them.

## Performance and robustness notes:
- The method builds an in-memory Python representation of the entire description and then serializes it to a pretty-printed JSON string (indent=4). For very large datasets/summaries, memory usage may be high.
- The encode_it branch that converts sets returns a Python set; because json.dumps does not accept sets, callers may encounter a TypeError if sets appear. When reimplementing, consider converting sets to lists if preservation of content order/uniqueness is desired and JSON serializability is required.

## Usage examples (textual, no code):
- Typical use: accessing report.json to retrieve a string you can send to an API, write to a .json file, or further process. The JSON string is ready for writing to disk or returning in HTTP responses.
- If you will write the output to a file, prefer ProfileReport.to_file() which handles file extension logic and will call this method internally when appropriate.

### `src.ydata_profiling.profile_report.ProfileReport.to_html` · *method*

## Summary:
Return the report rendered as an HTML string, using the cached rendering when available and triggering lazy HTML generation if not; guarantees the instance's internal HTML cache is populated on success.

## Description:
Known callers and contexts:
- Explicit in-code caller: ProfileReport.to_file uses this method to obtain the HTML to write to disk.
- Public API usage: consumers (interactive users or application code) call this to obtain the report HTML for display, embedding, or further processing.
Lifecycle stage:
- Invoked during the "render/export" stage after a ProfileReport has been instantiated. If the report was constructed with lazy=True, this call may trigger description and report generation.
Reason for being a separate method:
- Provides a stable, user-facing API to retrieve HTML (parallel to to_json/to_widgets).
- Encapsulates caching and lazy-rendering logic implemented in the html property.
- Keeps file-export and display code concise by centralizing HTML retrieval.

## Args:
- None

## Returns:
- str: The rendered HTML document as a Python string.
  - Normal case: a non-empty HTML string produced by the renderer (HTMLReport.render), possibly minified depending on configuration.
  - Edge cases:
    - The returned string may be empty or minimal if the underlying renderer produces such output.
    - The method never returns bytes; encoding (e.g., UTF-8) is applied when callers write the string to disk (to_file uses encoding="utf-8").

## Raises:
- This method does not explicitly raise new exceptions itself.
- It will propagate any exception raised by dependent operations, including but not limited to:
  - Report generation (get_report_structure), description generation (describe_df), and HTML rendering (HTMLReport.render).
  - Optional post-processing steps such as HTML minification.
- Examples of propagated exceptions are implementation-dependent (e.g., ValueError, TypeError, RuntimeError) and originate in the called components; callers should handle exceptions from rendering and report generation.

## State Changes:
Attributes READ:
- self._html (via the html property to determine if rendering is required)
- self.config (read indirectly when generating the report and during rendering)
- self._report (accessed via the report property if rendering is required)
- self._description_set (accessed via the description_set property during report generation)

Attributes WRITTEN:
- self._html (assigned to the rendered HTML string if it was previously None)
- self._report (may be assigned when report property computes and caches the report)
- self._description_set (may be assigned when description_set property computes and caches the description)

## Constraints:
Preconditions:
- The ProfileReport instance must be fully constructed (its __init__ finished).
- If the instance was created lazily (the default), calling this method may perform expensive computations; ensure the environment has sufficient resources.
- There is no additional input validation performed by this method.

Postconditions:
- On successful return, self._html is non-None and equals the returned string.
- Subsequent calls will return the cached HTML (self._html) without re-running rendering unless invalidate_cache() is called to clear the cache.

## Side Effects:
- May trigger expensive CPU/memory work: lazily generates the description and report and renders HTML in memory.
- May display progress output through tqdm depending on self.config.progress_bar.
- May import and use auxiliary libraries during rendering (e.g., HTML renderer, htmlmin for minification) — these operations happen in-process.
- Does not perform filesystem I/O or network I/O by itself; writing to disk is performed by to_file (which calls this method).
- Concurrency: not inherently thread-safe — concurrent calls can race while populating internal caches (self._html, self._report, self._description_set).

### `src.ydata_profiling.profile_report.ProfileReport.to_json` · *method*

## Summary:
Returns the report as a JSON-formatted string, using the object's cached JSON if available and otherwise rendering and caching the JSON representation.

## Description:
- Known callers and lifecycle:
    - ProfileReport.to_file uses this method when writing a report with a .json extension.
    - Interactive users or external code may call this method to obtain the serialized report payload for storage, transmission, or further processing.
    - It is typically invoked after the ProfileReport has been created and (optionally) after the report/description has been computed; the rendering is performed lazily on first call.
- Why this is a separate method:
    - Provides a simple, public API to obtain the JSON representation without exposing internal caching or rendering details.
    - Acts as a convenience wrapper around the json property that preserves lazy evaluation and caching behavior (keeps rendering logic centralized in _render_json and the json property).
    - Maintains a clear symmetry with to_html/to_widgets and supports backward-compatible call sites that expect an explicit to_json() method.

## Args:
    None

## Returns:
    str: A JSON-formatted string (utf-8 text) representing the report summary.
    - The produced JSON is pretty-printed with indentation (indent=4) as created by json.dumps in the rendering pipeline.
    - On the first call, the JSON is rendered from the in-memory description and cached on the instance. Subsequent calls return the cached value until invalidate_cache is used.
    - Edge cases:
        - If the underlying description is empty or minimal, the JSON will reflect that (an empty or minimal summary object).
        - If rendering fails (see Raises), no value is cached and the exception propagates.

## Raises:
    - This method itself does not explicitly raise errors, but it delegates to the json property which may trigger rendering via _render_json.
    - Exceptions that may propagate include:
        - TypeError or other exceptions raised by json.dumps if the final description dict contains non-serializable objects not handled by the encoder.
        - Any exception raised while computing the description (for example, errors from format_summary, redact_summary, or underlying data access). These exceptions are not caught here and will propagate to the caller.

## State Changes:
- Attributes READ:
    - self._json: checked for presence to decide whether to render.
    - self.config: read indirectly by _render_json (for configuration-driven serialization behavior such as progress bar and redaction).
    - self.description_set (via the description_set property): used to build the serializable summary.
- Attributes WRITTEN:
    - self._json: on first render this attribute is set to the produced JSON string (caching).
    - self._description_set: may be created/populated when accessing self.description_set if it was not already computed (this happens inside the property accessor; thus a call may mutate this attribute).

## Constraints:
- Preconditions:
    - The ProfileReport instance must be initialized (i.e., __init__ has completed). If the instance was constructed with lazy=False, description may already be computed; otherwise description will be computed on demand.
    - If the report requires a DataFrame (description_set creation), that DataFrame must be present and valid (non-empty for non-lazy initialization), otherwise earlier validation will have raised during construction.
- Postconditions:
    - After a successful call, self._json contains a JSON-formatted string representing the report and subsequent calls return this cached string until invalidate_cache clears it.
    - No change is made to the underlying DataFrame or to report content by this method; only internal caching fields may be set.

## Side Effects:
    - Console/progress output: rendering uses a progress bar (tqdm) which may emit progress output to stdout/stderr depending on configuration (self.config.progress_bar).
    - No file or network I/O is performed by this method itself; writing to disk is handled by other methods (e.g., to_file).
    - No external services are called. Only in-memory serialization and small helper transformations are performed.

### `src.ydata_profiling.profile_report.ProfileReport.to_notebook_iframe` · *method*

## Summary:
Displays the report inside a Jupyter-style notebook by obtaining an IFrame/HTML object from the notebook widget generator and sending it to IPython.display — does not return a value and does not modify the report's stored state.

## Description:
- Known callers and context:
    - ProfileReport._repr_html_ calls this method to provide the notebook rendering when Jupyter requests the HTML representation of the object.
    - Typical usage is direct invocation by users inside interactive notebook sessions (Jupyter, Colab) to render the profiling report inline.
    - Lifecycle stage: invoked at presentation time, after the ProfileReport has been constructed and (optionally) its report/html/widgets lazily computed.

- Why this is a separate method:
    - Encapsulates the notebook-specific display logic (importing IPython, suppressing warnings, calling the widget-producing helper) so rendering behavior is localized and can be reused by _repr_html_ and by user code.
    - Keeps presentation concerns separate from report generation and serialization logic; avoids inlining notebook imports at class top-level and centralizes warning suppression and display semantics.

## Args:
    None

## Returns:
    None
    - The method returns None; its purpose is side-effectful (displaying output in the notebook).
    - Edge-case behavior: although the method returns None, it calls get_notebook_iframe which produces an IFrame or HTML object that is passed to IPython.display.display and thus rendered in the notebook UI.

## Raises:
    - ImportError / ModuleNotFoundError: If IPython (IPython.core.display) is not importable in the environment, an ImportError (or ModuleNotFoundError) is raised by the local import statement.
    - ValueError: Propagated from get_notebook_iframe when the configuration contains an invalid iframe attribute (get_notebook_iframe raises ValueError if config.notebook.iframe.attribute is neither "src" nor "srcdoc").
    - Any exception raised while constructing the notebook iframe/html (for example, from get_notebook_iframe or its helpers) will propagate; these can include heavy-computation exceptions that arise when reading/serializing the report (e.g., if report rendering fails).

## State Changes:
- Attributes READ:
    - self.config: read directly to determine notebook/iframe behavior and passed into get_notebook_iframe.
    - self (ProfileReport instance): passed to get_notebook_iframe; depending on configuration, that helper may access lazily computed properties such as self.report, self.html, or self.widgets. Therefore, calling this method may trigger computation/reads of:
        - self.report (which may compute description_set and produce the Root report structure)
        - self.html (which may call _render_html and thus compute HTML)
        - self.widgets (which may call _render_widgets)
- Attributes WRITTEN:
    - None. This method does not assign to any self.<attr> fields.

## Constraints:
- Preconditions:
    - The caller should run inside an environment where IPython.display is available (typical in Jupyter/Colab). If not, the local import will fail.
    - self.config must be a valid Settings object with notebook.iframe.attribute set to a supported value (typically IframeAttribute.src or IframeAttribute.srcdoc).
    - The ProfileReport instance should be in a valid state (constructed and not intentionally invalidated) if the notebook rendering is expected to succeed.
- Postconditions:
    - After the call, an IFrame or HTML representation of the report will have been displayed in the notebook output area (assuming no exception).
    - No attributes on self are modified by this method.

## Side Effects:
    - UI output: calls IPython.display.display(...) which renders an IFrame or HTML widget in the notebook output cell.
    - Warning suppression: temporarily suppresses (ignores) warnings for the duration of the display call.
    - May trigger expensive computations: because get_notebook_iframe may access report/html/widgets, calling this method can cause lazy report generation (computing description_set, rendering the report, serializing HTML, etc.) and therefore may consume CPU/memory and take significant time.
    - Exceptions from helper functions (value errors, rendering errors, import errors) propagate to the caller; there is no internal retry or fallback.

### `src.ydata_profiling.profile_report.ProfileReport.to_widgets` · *method*

## Summary:
Displays the report's widget representation in an interactive IPython environment (e.g., Jupyter notebook). May lazily construct and cache the widgets; does not return a value.

## Description:
This method is intended to be called at the interactive presentation stage of the ProfileReport lifecycle — typically by a user in a Jupyter notebook after creating a ProfileReport or by higher-level notebook UI helpers. It centralizes the logic required to (1) detect if code is running on Google Colab and emit a user-facing warning about limited ipywidgets support there, and (2) invoke the IPython display mechanism to render the report's widgets in the frontend.

Known callers / usage contexts:
- End users in interactive sessions: e.g., after report = ProfileReport(df); report.to_widgets()
- Notebook UI code that wants to explicitly render the widget representation for the report
- Not called by the ProfileReport internals in this module (no internal direct callers found)

Why this is a separate method:
- Separates presentation concerns (displaying widgets and handling environment-specific warnings) from widget creation (the widgets property and _render_widgets method). This keeps rendering side-effects in a single place and allows the widgets generation logic to remain pure/lazy and reusable without forcing display behavior.

## Args:
    None

## Returns:
    None
    - The method has no return value. Its observable effect is rendering the widgets in the IPython frontend and possibly populating the object's cache for widgets.

## Raises:
    ModuleNotFoundError
        - Trigger condition: the local import "from IPython.core.display import display" fails because IPython is not installed or not importable in the runtime. The exception is not caught inside the method and will propagate.
    RuntimeError
        - Trigger condition: the widgets property raises a RuntimeError when the report represents a comparison (the property checks if description_set.table["n"] is a list of length > 1). The exact message raised by the widgets property is:
          "Widgets interface not (yet) supported for comparing reports, please use the HTML rendering."
        - This RuntimeError originates from reading self.widgets (the lazy property), not from the to_widgets method itself.

## State Changes:
Attributes READ:
    - self.widgets (accesses the widgets property; this read may cause lazy construction)

Attributes WRITTEN:
    - self._widgets (indirectly written if the widgets property constructs and caches the widget representation when previously None)
    - No other attributes are modified directly by this method.

## Constraints:
Preconditions:
    - The ProfileReport object must be instantiated and its description_set must be valid for widget generation. In particular, the widgets property expects that description_set.table["n"] is not a list with length > 1 (i.e., the report is not a comparison of multiple reports).
    - IPython must be importable in the runtime for display to succeed; otherwise ModuleNotFoundError will be raised.

Postconditions:
    - After successful execution, the profile report's widget representation will have been displayed in the active IPython frontend.
    - If widgets were not previously constructed, self._widgets will be set to the constructed widget object (cached for future reuse).
    - No value is returned.

## Side Effects:
    - Attempts a conditional import of google.colab; if that import succeeds, the method emits a warnings.warn with the following message:
      "Ipywidgets is not yet fully supported on Google Colab (https://github.com/googlecolab/colabtools/issues/60).As an alternative, you can use the HTML report. See the documentation for more information."
      (This import is used only to detect the Colab environment; ModuleNotFoundError for google.colab is caught and ignored.)
    - Emits a Python warning (warnings.warn) when running in Google Colab to advise using the HTML report instead of widgets.
    - Imports and calls IPython.core.display.display and passes the widgets object to it; this triggers frontend rendering of widgets (browser-side UI) in notebook environments.
    - Any exceptions raised by the widget construction (accessing self.widgets) or the display call (e.g., if IPython display is unavailable) will propagate to the caller.

## Implementation notes (for reimplementation):
    - Attempt to import google.colab inside a try/except ModuleNotFoundError block. If the import succeeds, call warnings.warn(...) with the Colab-specific message above. If the import fails, ignore it.
    - Import display from IPython.core.display (do not catch ModuleNotFoundError for this import unless intentionally handling that case).
    - Call display(self.widgets) to render the widget representation; ensure that self.widgets property lazily builds and caches the widget object (writing self._widgets) if necessary.
    - Do not swallow exceptions from importing IPython or from display; allow them to propagate so callers can detect environment problems.

### `src.ydata_profiling.profile_report.ProfileReport._repr_html_` · *method*

## Summary:
Invoke the notebook rendering pathway to display the report as an HTML iframe in Jupyter/IPython frontends; no value is returned.

## Description:
This method is the IPython/Jupyter special display hook invoked by the frontend when a ProfileReport instance is displayed (for example when it is the last expression in a notebook cell or passed to IPython.display.display). It delegates all work to the to_notebook_iframe() method which builds an iframe for the report and calls IPython.display.display to render it.

Known callers and contexts:
- IPython/Jupyter machinery: IPython will call _repr_html_ automatically when an object is to be represented as HTML in notebooks (Jupyter Notebook, JupyterLab, and other frontends that honor _repr_html_).
- Users of the library typically do not call this method directly; it runs when a ProfileReport instance is returned from a cell or handed to display().

Why this is a separate method:
- The _repr_html_ name conforms to IPython's display protocol and must exist on the object for automatic HTML rendering; keeping it as a tiny delegating method keeps the IPython hook distinct from the actual notebook-rendering implementation (to_notebook_iframe). This separation keeps display-specific logic (imports, warnings handling, widget creation) inside to_notebook_iframe and allows other programmatic callers to reuse that logic without going through the IPython protocol method.

## Args:
    None

## Returns:
    None
    - The method always returns None. Its observable effect is producing HTML/iframe output to the active IPython frontend; nothing is returned to the caller.

## Raises:
    None explicitly. However, any exception raised by the delegated call to to_notebook_iframe() will propagate:
    - ModuleNotFoundError / ImportError if required display or widget modules are missing (e.g., IPython not available or the notebook widget helper module cannot be imported).
    - Any runtime error thrown during iframe creation or while calling IPython.display.display may propagate unchanged.

## State Changes:
Attributes READ:
    - self.config (passed into the widget/iframe creation by to_notebook_iframe)
    - (indirect) any attributes accessed by the to_notebook_iframe / get_notebook_iframe call sequence (for example the report structure accessed via self.report)

Attributes WRITTEN:
    - None. _repr_html_ itself does not modify the object's attributes.

## Constraints:
Preconditions:
    - The ProfileReport instance should be properly initialized (self.config and underlying report/description structures should be available or lazily constructible). If the object was created with lazy=False, required structures will already exist; if lazy=True, they may be constructed on demand by the rendering code.

Postconditions:
    - No mutation is guaranteed on the ProfileReport instance.
    - The notebook frontend will receive an HTML representation (iframe) for rendering, assuming no exceptions occur.

## Side Effects:
    - Produces frontend output by invoking IPython.display.display; this is visible in Jupyter Notebook / JupyterLab cells as an embedded HTML iframe of the report.
    - Performs imports at runtime (via to_notebook_iframe), which may raise ImportError/ModuleNotFoundError if IPython or the notebook helper module is unavailable.
    - May trigger lazy generation of report data (e.g., accessing self.report or self.description_set) through the delegated call chain, which can perform computation and use CPU/memory and progress bars.

### `src.ydata_profiling.profile_report.ProfileReport.__repr__` · *method*

## Summary:
Returns an intentionally empty string as the object's machine-readable representation to avoid verbose or heavy output when inspected.

## Description:
Known callers and contexts:
- Python built-in repr(obj) and the interactive interpreter/REPL when an instance is inspected.
- Formatter expressions that request the repr form, e.g., f"{obj!r}".
- Logging or debug tools that call __repr__ to obtain a concise, machine-oriented representation.

Lifecycle stage:
- Invoked whenever a textual representation of the ProfileReport object is requested by Python runtime or user code for debugging/printing in repr-contexts.
- Note that notebook display is handled separately by _repr_html_ and other display helper methods (to_notebook_iframe, to_widgets, to_html), so the plain-text representation is intentionally minimal.

Why this logic is a separate method:
- Separating __repr__ keeps the lightweight machine-readable representation distinct from heavier HTML/widget rendering logic. It prevents accidental expensive rendering (HTML, JSON, widgets) when tools or the interpreter request a simple textual representation.
- Having a dedicated __repr__ allows other display methods to be implemented and evolved independently (for example, _repr_html_ for Jupyter).

## Args:
None.

## Returns:
str
- Value: an empty string ("").
- Edge cases: This method always returns the empty string; there are no alternate return values.

## Raises:
None.
- The implementation does not raise any exceptions.

## State Changes:
Attributes READ:
- None. The implementation does not access any self.<attr> fields.

Attributes WRITTEN:
- None. The implementation does not modify any attributes on self.

## Constraints:
Preconditions:
- None. The method does not require any particular state or initialization of the object.

Postconditions:
- The ProfileReport instance is unchanged.
- The caller receives an empty string as the representation.

## Side Effects:
- None. This method performs no I/O, no external service calls, and does not mutate objects outside of self.

## Notes / Rationale:
- Because ProfileReport may hold large datasets and rendering can be expensive, the class uses specialized display methods for rich output (HTML, widgets) and keeps the plain-text representation deliberately minimal to avoid unintended performance costs when introspecting objects.

### `src.ydata_profiling.profile_report.ProfileReport.compare` · *method*

## Summary:
Call the shared compare routine to compare this ProfileReport with another and return a merged ProfileReport describing differences and combined analyses. This method delegates the work and therefore may cause in-place mutation of the caller and the provided report.

## Description:
- Known callers and usage contexts:
    - Intended for interactive or programmatic use by library users who want to compare two profiling results (for example, comparing two versions of a dataset or profiling output before/after transformations).
    - Typically invoked as part of an analysis pipeline step where two ProfileReport instances have been produced and a combined comparative report is required.
- Why this is a separate method:
    - Acts as a convenience wrapper on top of the library-level orchestration function (ydata_profiling.compare_reports.compare), exposing a simple method on ProfileReport instances.
    - Keeps the ProfileReport API ergonomic (report_a.compare(report_b)) while deferring complex validation, alignment, and merge logic to a centralized compare implementation.

## Args:
    other (ProfileReport):
        - The ProfileReport to compare with this instance.
        - Must be a ProfileReport instance (mixing object types is not allowed; the underlying compare function requires homogeneous input types).
    config (Optional[Settings], default=None):
        - If provided, this Settings object will be passed to the compare routine and used as the merged report's configuration (a copy is used internally by the compare routine).
        - If None (default), this instance's self.config is passed through to the compare routine.

## Returns:
    ProfileReport
    - The ProfileReport produced by ydata_profiling.compare_reports.compare when invoked with [self, other] and the chosen config.
    - Possible return values (delegated semantics):
        * A newly constructed ProfileReport whose _description_set holds the merged comparative BaseDescription.
        * In some edge cases the compare routine may return one of the input ProfileReport instances directly (for example, if after alignment only a single non-empty, overlapping report remains).
    - The method returns whatever the compare() implementation returns; callers should treat the returned value as the canonical merged comparison report.

## Raises:
    TypeError:
        - Propagated from the underlying compare routine when the inputs are not homogeneous (e.g., if `other` is not a ProfileReport or if mixed types are provided).
    ValueError:
        - Propagated when the underlying compare routine encounters invalid inputs (for example, an empty reports list). With normal usage of this method (two ProfileReport instances), this should not occur.
    Any exception from validate_reports or other helpers:
        - The compare routine performs validation and preprocessing; any exceptions raised there (validation errors, configuration reconstruction errors, etc.) are propagated unchanged.

## State Changes:
- Attributes READ:
    - self.config (the method reads this attribute when config is not provided and forwards it to the compare routine)
- Attributes WRITTEN (directly or indirectly via the delegated compare call):
    - self.df: The compare routine may restrict/replace each report.df to the set of aligned columns (it assigns report.df = report.df.loc[:, cols_2_compare]); this mutates the ProfileReport instances passed in.
    - self.config: If a config argument is supplied to the compare routine, each input report.config may be overwritten with a copy of that config (the compare routine preserves some fields such as title and timeseries.active when doing so).
    - self._description_set: The compare routine may set input_report._description_set = None (for example when forcing recomputation via a compute flag) or otherwise mutate description-related state.
    - Note: The method itself is a thin forwarder and performs none of these mutations directly; they occur inside ydata_profiling.compare_reports.compare after this method forwards the arguments.

## Constraints:
- Preconditions:
    - `other` must be a ProfileReport instance (or else the underlying compare function will raise TypeError).
    - If `config` is supplied, it must be a Settings-like object understood by the compare routine.
    - Both ProfileReport instances should be in a valid initialized state (self.config exists and, if relevant, self.df is a pandas DataFrame or a supported Spark DataFrame).
- Postconditions:
    - The returned value is a ProfileReport that represents the merged/comparative description as produced by the compare routine.
    - Input ProfileReport objects (self and other) are not guaranteed to remain unchanged; callers should copy inputs beforehand if they need to preserve them.

## Side Effects:
- Mutations to objects passed in:
    - As described above, calling this method will invoke compare([self, other], ...). That compare routine may mutate the passed ProfileReport objects' df, config, and cached description (_description_set) in-place.
- Global or configuration state:
    - The compare routine may write merged label/style values into the configuration object it uses for constructing the result (this can affect the config object provided or used internally).
- I/O and external calls:
    - This method itself performs no I/O. The underlying compare routine likewise does not perform file/network I/O in normal operation, but it may call helpers that have their own side effects; such behaviors are out of scope for this wrapper and are propagated from the compare implementation.

