# `summary_spark.py`

## `src.ydata_profiling.model.spark.summary_spark.spark_describe_1d` · *function*

## Summary:
Accepts a single-column Spark DataFrame and returns a dictionary summary by (optionally) inferring or mapping the column type and delegating the actual summarization to the provided summarizer.

## Description:
spark_describe_1d is a small Spark-specific adapter that prepares a Spark DataFrame column for summarization and then calls the summarizer implementation to compute a one-dimensional summary. It performs three responsibilities:
- Normalizes missing values in the column (replacing nulls with NaN).
- Decides the variable type (vtype) either by delegating to a Visions typeset (when config.infer_dtypes is True) or by mapping the Spark schema type to a high-level vtype string.
- Delegates the summarization to the provided BaseSummarizer instance and returns the summarizer's result.

Known callers:
- Typical callers are Spark-based profiling pipelines that iterate over DataFrame columns and call this function for each column to produce per-column summaries. (No explicit call sites were provided in the available context; treat this function as the per-column summarization step in a Spark profiling pipeline.)

Why this logic is extracted:
- Keeps Spark-specific dtype extraction and null-normalization in one place so summarization logic remains generic and reusable.
- Ensures a single conversion point from Spark schema types to the summarizer's expected dtype representation.
- Allows different summarizers to be used without duplicating Spark handling.

## Args:
    config (Settings):
        - Profiler configuration object.
        - Uses config.infer_dtypes (boolean) to choose whether to run Visions-based inference.
    series (pyspark.sql.DataFrame):
        - A Spark DataFrame that represents a single column (or at least the column to be summarized must be the first column).
        - Must have an accessible schema (series.schema) and at least one column (series.schema[0] used).
        - The function calls series.fillna(np.nan) to replace nulls, so the DataFrame must support fillna.
    summarizer (BaseSummarizer):
        - An instance implementing summarize(config, series, dtype=...) -> dict.
        - The function returns whatever summarizer.summarize returns.
    typeset (VisionsTypeset):
        - A Visions typeset used when config.infer_dtypes is True.
        - Expected to implement infer_type(series) and cast_to_inferred(series).
        - infer_type(series) should return a type descriptor acceptable to the summarizer (commonly a Visions type).
        - cast_to_inferred(series) is expected to return a (possibly converted) Spark DataFrame ready for summarization.

Interdependencies:
    - If config.infer_dtypes is True, typeset.infer_type and typeset.cast_to_inferred are invoked; otherwise a manual mapping of Spark dtype strings to high-level vtypes is used.
    - The value of vtype is passed directly to summarizer.summarize as the dtype argument.

## Returns:
    dict:
        - The summary dictionary returned by summarizer.summarize.
        - If summarizer.summarize returns domain-specific summary keys, they are forwarded unchanged.
        - There are no additional wrapper keys added by spark_describe_1d.

Edge / special return cases:
    - The function always returns the summarizer's return value when it completes successfully. If the summarizer raises, that exception propagates out of this function.

## Raises:
    IndexError:
        - If the provided series has no columns (series.schema is empty), accessing series.schema[0] will raise IndexError.
    KeyError:
        - When config.infer_dtypes is False and the detected Spark dtype string (dtype) is not one of the mapping keys:
          {"float","int","bigint","double","string","ArrayType","boolean","date","timestamp"}.
          Attempting to index the mapping with an unknown key raises KeyError.
    AttributeError:
        - If typeset does not implement infer_type or cast_to_inferred and config.infer_dtypes is True.
        - If summarizer does not implement summarize, an AttributeError may occur when calling summarizer.summarize.
    Any exception raised by summarizer.summarize:
        - Errors from the summarizer (e.g., type errors, data issues) propagate to the caller.

## Constraints:
Preconditions:
    - series must be a Spark DataFrame with at least one column. The column to summarize must be accessible as the first schema field (schema[0]).
    - typeset must provide infer_type(series) and cast_to_inferred(series) when config.infer_dtypes is True.
    - summarizer must implement summarize(config, series, dtype=...) and accept the dtype value produced here.
    - config must be a Settings-like object with a boolean attribute infer_dtypes.

Postconditions:
    - No global state is modified by this function.
    - The returned value is the raw result of summarizer.summarize with dtype set according to either the typeset inference or the Spark-to-vtype mapping.
    - If infer_dtypes was True, the local variable series will be replaced by the typeset.cast_to_inferred result prior to summarization (this does not mutate the caller's DataFrame unless the typeset method mutates in-place).

## Side Effects:
    - Local transformation only: series.fillna(np.nan) is invoked and its result assigned back to the local series variable. For Spark DataFrames this produces a new DataFrame reference rather than in-place mutation.
    - No I/O (files, network) performed by this function itself.
    - No writes to databases, files, or global variables are performed here.
    - External calls:
        - typeset.infer_type(series) and typeset.cast_to_inferred(series) may perform additional work (they are external to this function).
        - summarizer.summarize(config, series, dtype=vtype) is an external call that performs the actual profiling and may have its own side effects or expensive computations.

## Control Flow:
flowchart TD
    A[Start: receive config, series, summarizer, typeset]
    A --> B[series = series.fillna(np.nan)]
    B --> C{config.infer_dtypes?}
    C -->|True| D[vtype = typeset.infer_type(series)]
    D --> E[series = typeset.cast_to_inferred(series)]
    E --> G[call summarizer.summarize(config, series, dtype=vtype)]
    C -->|False| F{series.schema[0].dataType startswith "ArrayType"?}
    F -->|Yes| H[dtype = "ArrayType"]
    F -->|No| I[dtype = series.schema[0].dataType.simpleString()]
    H --> J[map dtype -> vtype via mapping dict]
    I --> J
    J --> G
    G --> K[return summary dict]
    K --> L[End]

## Examples:
- Common successful call (pseudo-code):
    result = spark_describe_1d(config, single_column_spark_df, summarizer, typeset)
    # result is the dict returned by the summarizer for this column

- Example behavior differences:
    - If config.infer_dtypes is True:
        * typeset.infer_type is called to determine vtype.
        * typeset.cast_to_inferred is called to convert the DataFrame prior to summarization.
    - If config.infer_dtypes is False:
        * The function reads the Spark schema for the first column, maps Spark dtype strings to a vtype using the mapping:
          float, int, bigint, double -> "Numeric"
          string, ArrayType -> "Categorical"
          boolean -> "Boolean"
          date, timestamp -> "DateTime"
        * If the Spark dtype string is not present in the mapping, a KeyError is raised.

- Error handling pattern:
    - Callers should guard against IndexError and KeyError if input DataFrame might be empty or contain an unexpected Spark dtype.
    - Any exceptions from summarizer.summarize should be handled by the caller as needed.

## `src.ydata_profiling.model.spark.summary_spark.spark_get_series_descriptions` · *function*

## Summary:
Runs column-wise 1D summarization of a Spark DataFrame in parallel (threaded), collects each column's description (with value counts removed), preserves the original column order, optionally sorts columns according to configuration, and returns a mapping of column name → description dict.

## Description:
- Known callers within the provided codebase:
    - None explicitly found in the provided snippets. Typical caller: a Spark-based profiling pipeline that builds a report for a Spark DataFrame and needs per-column summaries (this function is the Spark-specific implementation that produces the per-column descriptions).
- Typical usage context:
    - Called during the "describe each variable/column" stage of a profiling job for Spark DataFrames, when a Settings object, a summarizer instance, a Visions typeset, and a tqdm progress bar are available.
- Why extracted into its own function:
    - Encapsulates the concurrency and progress-bar integration required to produce per-column descriptions for Spark DataFrames.
    - Keeps the higher-level profiling flow free of threading, pbar, and per-column housekeeping (removing heavy fields like value_counts).
    - Provides a single place to tune parallelism (thread pool size), error handling behavior, and the interaction with sort_column_names.

## Args:
    config (Settings):
        Configuration object (ydata_profiling.config.Settings). Used for options such as sorting behavior (config.sort) and any settings consumed by describe_1d.
    df (pyspark.sql.DataFrame):
        The Spark DataFrame to profile. Must expose .columns (an iterable/list of column names) and support df.select(column) to obtain a single-column DataFrame for describe_1d.
    summarizer (BaseSummarizer):
        An instance (or subclass) of BaseSummarizer responsible for computing the 1D summary for a single column (describe_1d delegates to the summarizer).
    typeset (VisionsTypeset):
        Visions typeset used by describe_1d to determine variable types and typing logic.
    pbar (tqdm):
        A tqdm progress bar object. The function will call pbar.set_postfix_str(...) and pbar.update() once per described column. The caller should initialize pbar (typically with total=len(df.columns)).

Notes on parameter interdependencies:
    - df and typeset/summarizer: describe_1d will be invoked with df.select(column), summarizer and typeset; the summarizer and typeset must be compatible with the structure returned by selecting a single column from the provided Spark DataFrame.
    - config.sort is read by sort_column_names to optionally reorder the returned mapping.

## Returns:
    dict:
        A dictionary mapping each original column name (str) to its description dict (the dict produced by describe_1d with the "value_counts" entry removed).

    Specific behaviors:
        - For each column in df.columns there will be an entry in the returned dict (subject to no exceptions being raised during processing).
        - The values are the description dictionaries returned by describe_1d(config, df.select(column), summarizer, typeset) after removing the "value_counts" key:
            * If describe_1d yields a dictionary D for column c, the returned mapping contains c -> D' where D' == D with the "value_counts" entry popped.
        - Key order:
            * The function first reorders the collected descriptions to match the iteration order of df.columns.
            * After that, sort_column_names is applied with config.sort; if config.sort is "ascending" or "descending" (case-insensitive prefixes 'asc'/'desc'), the resulting mapping will be ordered accordingly; otherwise if config.sort is None, original df.columns order is preserved.

## Raises:
    - Any exception raised by describe_1d will propagate (e.g., runtime errors, type errors). There is no internal try/except around describe_1d; a failing column summary will raise and abort iteration.
    - KeyError:
        - Raised if the description dictionary returned by describe_1d does not contain the "value_counts" key (because the code calls description.pop("value_counts") without a default). This KeyError will propagate to the caller.
    - ValueError:
        - May be raised by sort_column_names if config.sort is present but not a recognized value (sort must be None, start with "asc", or start with "desc"). The exact error message originates from sort_column_names: '"sort" should be "ascending", "descending" or None.'.

## Constraints:
Preconditions:
    - df must be a valid pyspark.sql.DataFrame with a working .columns attribute and support df.select(column).
    - summarizer must be compatible with describe_1d usage (it should implement the summarization pipeline expected by describe_1d).
    - typeset must be a VisionsTypeset usable by describe_1d.
    - pbar must implement set_postfix_str(str) and update() (typical tqdm objects).
    - The environment must allow creation of a ThreadPool with 12 threads (the function uses multiprocessing.pool.ThreadPool(12)).
Postconditions:
    - Returned dict contains an entry for each column name in df.columns, but possibly reordered according to config.sort.
    - Each description dict in the result will not contain the "value_counts" key (it has been removed).
    - The progress bar pbar will have been updated once per column and will have its postfix set to the last processed column name.

## Side Effects:
    - Progress bar mutation: calls pbar.set_postfix_str(...) and pbar.update() repeatedly (one update per column).
    - Thread creation: uses a ThreadPool with a fixed size of 12 threads for concurrent execution; threads will be created and torn down within the function scope.
    - No file I/O, network access, or global state mutations are performed by this function itself.
    - External state mutated indirectly: any side effects performed by describe_1d (if it writes to external resources) will occur and propagate.

## Control Flow:
flowchart TD
    A[Start: call spark_get_series_descriptions] --> B[Build args list: (col_name, df) for each column]
    B --> C[Open ThreadPool(12)]
    C --> D[executor.imap_unordered over args -> worker multiprocess_1d]
    D --> E{Each result (column, description) arrives asynchronously}
    E --> F[Set pbar postfix to "Describe variable:<column>"]
    F --> G[Remove "value_counts" from description (description.pop("value_counts"))]
    G --> H[Insert into series_description[column] = description]
    H --> I[pbar.update()]
    I --> J{All results processed?}
    J -- no --> E
    J -- yes --> K[Reorder series_description to original df.columns order]
    K --> L[Apply sort_column_names(series_description, config.sort)]
    L --> M[Return final mapping]
    M --> Z[End]

## Examples:
- Example (conceptual usage):
    Given:
        - config is a Settings instance (config.sort may be None or "ascending"/"descending").
        - df is a pyspark.sql.DataFrame with columns ["id", "value", "category"].
        - summarizer is an instantiated subclass of BaseSummarizer that describe_1d expects.
        - typeset is a VisionsTypeset appropriate for the dataset.
        - pbar is a tqdm progress bar initialized by the caller (e.g., total=len(df.columns)).
    Expected call and result:
        - Call spark_get_series_descriptions(config, df, summarizer, typeset, pbar).
        - The function will concurrently call describe_1d for each column using df.select(column).
        - For each column it will remove the "value_counts" key from the returned description dict.
        - The returned value is a dict mapping "id" -> desc_id, "value" -> desc_value, "category" -> desc_category, where each desc_* is the description produced by describe_1d (minus "value_counts").
    Error handling recommendation:
        - Wrap the call in try/except where you want to capture exceptions from describe_1d or missing "value_counts":
            * The function does not swallow exceptions; if any column processing raises, the exception will propagate and should be handled by the caller.
            * After catching an exception, the caller may choose to retry, fall back to serial processing, or skip the problematic column and continue (not implemented here).

