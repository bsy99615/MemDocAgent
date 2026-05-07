# `summary_pandas.py`

## `src.ydata_profiling.model.pandas.summary_pandas.pandas_describe_1d` · *function*

## Summary:
Determines the Visions data type for a pandas Series (optionally inferring and casting), records that type in the provided typeset, and returns a summarized description produced by the given summarizer.

## Description:
This function is the pandas-specific routine that prepares a single pandas.Series for summary by:
- Normalizing missing values (replacing pandas NA with numpy.nan).
- Resolving the series' Visions type via one of three routes:
  1. Reuse an existing type from a ProfilingTypeSet.type_schema (if available for this series name).
  2. If configuration requests inference, infer a type and cast the series to the inferred type.
  3. Otherwise, detect the type without modifying the series.
- Persisting the resolved type into the provided typeset's type_schema under the series name.
- Delegating the actual computation of descriptive statistics/summary to the provided BaseSummarizer and returning its result.

Known callers in the provided codebase:
- No direct callers were found in the provided sources. Conceptually, this is intended to be used by pandas-based implementations of describe_1d or by a pandas get_series_descriptions orchestration that iterates columns and calls a 1-D describe routine.

Why this is a separate function:
- Responsibility boundary: it centralizes pandas-specific pre-processing and type resolution logic (NA normalization, type inference/detection, typeset bookkeeping) so summarizers only receive a clean, typed series and configuration. This keeps type-resolution/side-effect concerns out of summarizer implementations and avoids code duplication across higher-level orchestration code.

## Args:
    config (Settings):
        Profiling configuration object. Only the attribute infer_dtypes (truthy/falsy) is consulted by this function.
        - If infer_dtypes is truthy, the function will attempt to infer and cast the series to an inferred type via the typeset.
        - The object is otherwise opaque to this function; any missing attributes will raise an AttributeError.
    series (pandas.Series):
        The pandas Series to describe. The function will call series.fillna(np.nan) and may modify the variable bound to series (a new Series object returned from fillna is used).
        - series.name is used as the key in typeset.type_schema; it may be None, in which case None is used as the dictionary key.
    summarizer (BaseSummarizer):
        An object that implements summarize(config, series, dtype=...) -> dict. The function delegates summarization to summarizer.summarize and returns its dict result.
    typeset (VisionsTypeset):
        A Visions typeset instance used to determine and cast the data type of the series.
        - If a ProfilingTypeSet instance is provided and it has a type_schema mapping containing a value for series.name, that stored type is reused.
        - Expected methods (on the provided object): infer_type(series), cast_to_inferred(series), detect_type(series). A ProfilingTypeSet additionally provides the mutable attribute type_schema (dict).

## Returns:
    dict:
        The summary dictionary produced by summarizer.summarize(config, series, dtype=vtype).
        - This represents the descriptive statistics and metadata for the prepared series.
        - The exact structure/keys are determined by the summarizer implementation (BaseSummarizer subclasses) and are not changed by this function.

## Raises:
    AttributeError:
        If the provided config object lacks the attribute infer_dtypes, attribute access will raise AttributeError.
    TypeError / ValueError / Any exception propagated from called methods:
        Any exceptions raised by typeset.infer_type, typeset.cast_to_inferred, typeset.detect_type, or summarizer.summarize will propagate out of this function. Examples:
        - If typeset methods are not implemented on the provided typeset instance, an AttributeError will be raised.
        - If summarizer.summarize internally raises due to unexpected series content, that error propagates unchanged.

## Constraints:
Preconditions:
    - series must be a pandas.Series object (or an object providing fillna and name semantics compatible with pandas.Series).
    - summarizer must provide summarize(config, series, dtype=...) -> dict.
    - typeset must provide detect_type(series); if config.infer_dtypes is True, typeset must also provide infer_type(series) and cast_to_inferred(series).
    - config must have a boolean-ish attribute infer_dtypes.

Postconditions:
    - typeset.type_schema[series.name] is set to the resolved Visions type (vtype). This is a persistent side effect visible to callers that inspect typeset after calling this function.
    - The returned dict is the result of summarizer.summarize called with the same config and the (possibly cast) series and the resolved dtype.

## Side Effects:
    - Mutates typeset.type_schema by writing an entry for key series.name with value equal to the resolved Visions type.
    - Calls methods on the typeset and summarizer objects; any side effects from those methods (casting, logging, metrics collection) will occur.
    - No I/O (files/network) is performed by this function itself.
    - No global variables are mutated by this function.

## Control Flow:
flowchart TD
    Start[Start]
    A[series = series.fillna(np.nan)]
    B{typeset is ProfilingTypeSet\nAND typeset.type_schema\nAND series.name in typeset.type_schema?}
    C[use vtype = typeset.type_schema[series.name]]
    D{config.infer_dtypes is truthy?}
    E[vtype = typeset.infer_type(series)]
    F[series = typeset.cast_to_inferred(series)]
    G[vtype = typeset.detect_type(series)]
    H[typeset.type_schema[series.name] = vtype]
    I[result = summarizer.summarize(config, series, dtype=vtype)]
    End[Return result]
    Start --> A --> B
    B -- yes --> C --> H
    B -- no --> D
    D -- yes --> E --> F --> H
    D -- no --> G --> H
    H --> I --> End

## Examples:
- Typical usage scenario (conceptual):
    1. A profiling orchestrator iterates over DataFrame columns and for each column constructs or reuses:
        - a Settings instance with infer_dtypes configured,
        - a ProfilingTypeSet (or VisionsTypeset) instance,
        - a pandas-specific summarizer (subclass of BaseSummarizer).
    2. For each column series, the orchestrator calls this function to obtain a summary dict.
    3. After calling the function, the orchestrator may inspect typeset.type_schema to see the inferred/detected type used for that column.

- Error handling guidance:
    - If you pass a non-ProfileingTypeSet typeset but still expect type_schema bookkeeping, ensure your typeset implements a mutable type_schema dict; otherwise, expect AttributeError.
    - Wrap the call in try/except if you want to capture and handle errors from type inference/detection or summarization (for example, to continue profiling other columns if one fails).

## `src.ydata_profiling.model.pandas.summary_pandas.pandas_get_series_descriptions` · *function*

## Summary:
Compute and return per-column descriptive summaries for a pandas DataFrame by applying the 1D summarizer to each Series, using either sequential execution or a thread pool determined by configuration, while reporting progress via a tqdm progress bar.

## Description:
This routine iterates every column (Series) in the supplied DataFrame and computes a description for that column by invoking the per-series summarizer (describe_1d). It orchestrates single-threaded or multi-threaded execution based on config.pool_size, collects all results into a dict keyed by column name, reorders results to match the DataFrame's column order when threaded execution is used, then applies sort_column_names according to config.sort before returning.

Known callers and context:
- Called from higher-level profiling pipeline code when producing the per-column metadata stage of a DataFrame profiling run.
- Typical trigger: when the pipeline needs to transform a pandas.DataFrame into a dictionary of per-series metadata for report generation.

Why extracted:
- Separates orchestration (iteration, concurrency, progress reporting, result collation, and ordering) from per-series summarization (describe_1d).
- Centralizes thread-pool management and progress updates so describe_1d remains focused on the 1D summarization logic.

## Args:
    config (Settings)
        - Exact annotation in function signature: Settings
        - Role: runtime configuration. Required attributes:
            * pool_size (int): number of worker threads to use. If <= 0, CPU count is used.
            * sort: sorting preference passed to sort_column_names.
        - Constraints/Notes: pool_size must be an integer. If you need serial execution (no concurrency), set pool_size == 1.

    df (pd.DataFrame)
        - Exact annotation in signature: pd.DataFrame
        - Role: the DataFrame whose columns will be summarized. Iteration is performed via df.items() which yields (column_name, Series).
        - Constraints: If df has no columns, the function returns an empty dict.

    summarizer (BaseSummarizer)
        - Exact annotation: BaseSummarizer
        - Role: object forwarded into describe_1d; may carry state or methods used by the summarization logic.
        - Thread-safety: If config.pool_size > 1, summarizer (and any objects it references) should be safe for concurrent access from multiple threads. If not thread-safe, set pool_size to 1.

    typeset (VisionsTypeset)
        - Exact annotation: VisionsTypeset
        - Role: typeset used by describe_1d for type inference and type-specific summarization.

    pbar (tqdm)
        - Exact annotation: tqdm
        - Role: progress bar updated as each column is processed.
        - Required methods: set_postfix_str(str) and update(int=1). The function calls set_postfix_str(f"Describe variable:{column}") and then pbar.update() once per column.

## Returns:
    dict
        - Mapping: column name (str) -> description (dict).
        - Each description value is whatever describe_1d(config, series, summarizer, typeset) returns for that Series.
        - Ordering:
            * If pool_size == 1: results are produced sequentially in the same order as df.items() iteration; then sort_column_names(...) is applied.
            * If pool_size > 1: results arrive unordered from the thread pool; after collection the function reorders them to match df.columns using a comprehension, then passes the mapping to sort_column_names(...).
        - Edge cases:
            * Empty DataFrame -> returns {}.
            * If describe_1d raises for any Series, the exception propagates and the function does not return a mapping.
            * If a worker fails to produce a result for a column (e.g., an exception swallowed or threads terminated), reordering the results with the comprehension may raise KeyError (see Raises).

## Raises:
    - Any exception raised by describe_1d for an individual Series will propagate out of this function (e.g., ValueError, TypeError).
    - AttributeError: if the provided pbar does not implement set_postfix_str or update.
    - KeyError: in the threaded path (pool_size > 1), after threaded collection the function does:
        {k: series_description[k] for k in df.columns}
      If series_description lacks an entry for a column (because a worker failed to produce it), a KeyError will be raised here.
    - Exceptions from multiprocessing.pool.ThreadPool internals (e.g., if thread creation fails) may propagate.

## Constraints:
Preconditions:
    - config must have integer attribute pool_size and attribute sort compatible with sort_column_names.
    - df must be a valid pandas DataFrame; df.items() must yield (column_name, pandas.Series) pairs.
    - summarizer and typeset must be compatible with describe_1d.

Postconditions:
    - The returned dict contains entries for every column in df.columns (unless an exception was raised).
    - The returned dict has been passed through sort_column_names(series_description, config.sort) before return.

## Side Effects:
    - Progress bar: calls pbar.set_postfix_str(f"Describe variable:{column}") and pbar.update() once per processed column.
    - Concurrency: may create a multiprocessing.pool.ThreadPool(pool_size) (thread-based workers) when pool_size > 1.
    - No file, network, or stdout writes are performed directly by this function (aside from side effects inside describe_1d or summarizer).
    - The input DataFrame df is not mutated by this function.

## Internal helper:
    multiprocess_1d(args: tuple) -> Tuple[str, dict]
        - Implemented as a small inner function that expects args == (column_name, pandas.Series).
        - Behavior: unpacks args and returns (column_name, describe_1d(config, series, summarizer, typeset)).
        - Purpose: makes the target callable for executor.imap_unordered and for sequential calls.

## Control Flow:
flowchart TD
    A[Start] --> B[Read config.pool_size]
    B --> C{pool_size <= 0?}
    C -->|yes| D[pool_size = multiprocessing.cpu_count()]
    C -->|no| E[pool_size = config.pool_size]
    D --> F[Build args = list(df.items())]
    E --> F
    F --> G{pool_size == 1?}
    G -->|yes| H[For each arg in args: call multiprocess_1d(arg)]
    G -->|no| I[Create ThreadPool(pool_size) and executor.imap_unordered(multiprocess_1d, args)]
    H --> J[On each iteration: set_postfix_str, store result in series_description, pbar.update()]
    I --> K[For each (column, description) result from imap_unordered: set_postfix_str, store, pbar.update()]
    J --> L{threaded? -> reorder results to df.columns}
    K --> L
    L --> M[series_description = sort_column_names(series_description, config.sort)]
    M --> N[Return series_description]
    N --> O[End]

## Examples (realistic usage and error handling):
- Typical sequential usage (pool_size == 1):
    * Ensure Settings.pool_size == 1 (for thread-unsafe summarizers).
    * Prepare df (pandas DataFrame), summarizer (BaseSummarizer), typeset (VisionsTypeset), and pbar = tqdm(total=len(df.columns)).
    * Call the function and receive a dict mapping column names to description dicts.
    * Because execution is sequential, exceptions from describe_1d will stop processing immediately.

- Typical threaded usage (pool_size > 1):
    * Ensure summarizer and any shared resources are thread-safe.
    * Set Settings.pool_size to desired thread count (or <= 0 to auto-select CPU count).
    * Provide pbar as above; it will be updated once per completed column.
    * The function collects results unordered from worker threads, reorders to df.columns, then applies sort_column_names.

- Example call pattern (pseudocode-like):
    config.pool_size = 4
    pbar = tqdm(total=len(df.columns))
    try:
        series_desc = pandas_get_series_descriptions(config, df, summarizer, typeset, pbar)
    except Exception as exc:
        # Log the error and decide on fallback behavior
        handle_error(exc)
    finally:
        pbar.close()

Notes and recommendations:
    - If per-column failures should not abort the entire run, consider wrapping describe_1d with a try/except at its call site (or modify multiprocess_1d to capture exceptions and return an error sentinel per column), and then adapt downstream code to handle sentinel values.
    - Use pool_size == 1 when summarizer, typeset, or other resources are not thread-safe.
    - Ensure the provided pbar implements set_postfix_str and update; for non-interactive runs, pass a dummy object implementing these methods as no-ops.

