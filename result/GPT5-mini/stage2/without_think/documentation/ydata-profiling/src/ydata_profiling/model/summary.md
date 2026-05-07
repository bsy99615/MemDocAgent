# `summary.py`

## `src.ydata_profiling.model.summary.describe_1d` · *function*

## Summary:
Coordinate per-column profiling by obtaining a Visions dtype for a single 1D series, invoking the configured summarizer pipeline for that dtype, normalizing the pipeline payload, and returning a summary dictionary. Note: the current source is a stub that raises NotImplementedError; the following specifies the intended contract and an implementation recipe.

## Description:
This function is the per-series orchestration point in a profiling workflow. Its intended responsibilities are:
1. Determine or accept a Visions dtype for the input series using the provided VisionsTypeset.
2. Invoke summarizer.summarize(config, series, dtype) to execute the Handler pipeline associated with that dtype.
3. Validate and normalize the pipeline's returned payload into a consistent summary dict that callers can aggregate.

Known, verifiable behavior (from existing code + BaseSummarizer contract):
- The shipped implementation raises NotImplementedError().
- BaseSummarizer.summarize(config, series, dtype) delegates to the Handler pipeline associated with str(dtype) and returns the pipeline's summary payload (the third element of the pipeline's returned tuple). BaseSummarizer will propagate exceptions raised by the pipeline or by Handler.handle and can raise standard unpacking errors if the pipeline result does not match the expected shape.

Why this is a separate function:
- Centralizes dtype inference, summarizer invocation, error handling, and consistent normalization of pipeline outputs.
- Facilitates unit testing of per-column behavior and keeps the dataset-level orchestration simple.

## Args:
    config (Settings)
        Configuration/settings forwarded unchanged to the summarizer and pipeline; treated opaquely by this function.
    series (Any)
        The 1D data to summarize (typically pandas.Series, numpy 1D array, or list-like). The implementation should handle empty sequences and be able to compute length and missing-value counts in a manner compatible with the chosen series type.
    summarizer (BaseSummarizer)
        Handler-backed summarizer adapter. Per BaseSummarizer's documented contract, call summarizer.summarize(config, series, dtype) and expect the pipeline's summary dictionary as the result under normal operation.
    typeset (VisionsTypeset)
        Visions typeset used to obtain the dtype for the series. The exact call to obtain the dtype depends on the typeset API available in the runtime and therefore is not hard-coded here; the important requirement is that the result be usable by summarizer.summarize (BaseSummarizer.summarize uses str(dtype) internally to select the pipeline).

Interdependencies:
- The dtype value returned/used must be compatible with the summarizer: str(dtype) should match a key in the Handler mapping constructed for the summarizer, or an ancestor type must exist in the mapping so the Handler pipeline can be found.

## Returns:
    dict
    A dictionary representing the one-dimensional summary returned by the pipeline. Guidance on contents:
      - On a successful pipeline run: the pipeline-defined keys (type identifier, counts, dtype-specific statistics).
      - Implementers are advised to ensure at least a minimal, consistent set of keys is present for downstream consumers (commonly "type", "n", "n_missing"), either because the pipeline provides them or by adding them during normalization.
      - On empty or unsupported series: either return a minimal summary dict describing the situation (recommended to keep profiling robust) or raise an error — this is a policy choice for the project and should be consistent across callers.

Edge-case behavior (options):
  - Empty series: return a dict with n == 0 and n_missing computed appropriately.
  - Unsupported/infer-failure: either return {"type": "Unsupported", "n": len(series), "n_missing": <count>} or raise ValueError; the implementation should document which policy it follows.

## Raises:
    NotImplementedError
        The current stub raises NotImplementedError unconditionally.
    Any exception raised by typeset dtype inference
        (e.g., if the chosen typeset API raises for malformed input).
    Any exception raised by summarizer.summarize or the underlying Handler pipeline
        These include (but are not limited to) TypeError, ValueError, RuntimeError, or unpacking errors if the pipeline returns a value that cannot be processed by BaseSummarizer.summarize.

Recommended handling:
- Allow pipeline exceptions to propagate to the caller or catch and wrap them with context (e.g., column name) depending on higher-level orchestrator expectations.

## Constraints:
Preconditions (expected for correct operation):
  - summarizer is a BaseSummarizer whose Handler mapping contains pipelines for the expected dtype keys (or their ancestors).
  - typeset is a usable VisionsTypeset capable of providing a dtype for the input series in the runtime environment.
  - series is 1-dimensional.

Postconditions:
  - On success, returns a dict representing the pipeline summary. The function itself does not mutate summarizer.mapping or typeset internals; any mutations are side effects of the pipeline callables.

## Side Effects:
  - The function itself should not perform I/O or mutate global state.
  - Pipeline callables executed by summarizer.summarize may perform I/O or mutate external state; those side effects are outside the scope of describe_1d.

## Control Flow:
flowchart TD
    Start[Start: describe_1d called] --> ObtainDtype[Obtain dtype via typeset API available at runtime]
    ObtainDtype -->|dtype obtained| InvokeSummarizer[Invoke summarizer.summarize(config, series, dtype)]
    ObtainDtype -->|dtype unobtainable| HandleInferenceFail{Policy: return minimal dict or raise}
    InvokeSummarizer -->|raises| PropagateOrWrap[Propagate or wrap exception]
    InvokeSummarizer -->|returns| ValidateReturn{Is return a dict?}
    ValidateReturn -->|yes| Normalize[Normalize/ensure basic keys ("type","n","n_missing") as needed]
    ValidateReturn -->|no| RaiseTypeError[Raise TypeError("summarizer returned non-dict")]
    Normalize --> Return[Return summary dict]
    HandleInferenceFail --> Return

Decision guidance:
- Prefer returning a minimal dict on inference failure to allow profiling to continue across columns, unless the surrounding system expects an inference failure to be fatal.
- Use str(dtype) as the stable, serializable identifier for the inferred dtype when adding a "type" field.

## Implementation recipe (explicit, no hard-coded typeset API names):
1. Optionally assert summarizer is a BaseSummarizer to provide early clarity to implementers.
2. Acquire a dtype for the series using the VisionsTypeset API available at runtime (the exact method name is environment-dependent). The returned object should be usable with BaseSummarizer.summarize (BaseSummarizer uses str(dtype) to look up pipelines).
3. If dtype cannot be obtained:
   - Option A (recommended): construct and return a minimal summary dict (see Returns).
   - Option B: raise ValueError to abort profiling for this series.
4. Call summary = summarizer.summarize(config, series, dtype).
   - Note: BaseSummarizer.summarize will invoke the Handler pipeline for str(dtype) and extract the pipeline's third-element payload as the returned summary. It may raise unpacking errors if the pipeline returns a non-conforming shape.
5. Validate the returned summary:
   - If not a dict, raise TypeError("summarizer.summarize returned non-dict").
6. Normalize:
   - If "type" not present, set it to str(dtype).
   - If "n" not present, set it to the length of the series (computed in a manner compatible with the series type).
   - If "n_missing" not present, compute missing count consistent with the series representation (e.g., pandas isnull semantics) and set it.
7. Return the normalized dict.

## Examples (pseudocode-level; adapt to the local typeset API):
- Typical caller flow:
    - For each column in a dataset:
        - summary = describe_1d(config, series, summarizer, typeset)
        - collect summary into dataset report

- Error-resilient strategy:
    - try:
        summary = describe_1d(config, series, summarizer, typeset)
      except Exception as exc:
        # log or record the failure and continue profiling other columns
        handle_failure_for_column(exc)

## Current file behavior:
    The implemented function in this file is a stub that raises NotImplementedError(). The above documentation defines the expected contract and provides guidance to implement a production-ready version that interoperates with BaseSummarizer and a VisionsTypeset instance.

## `src.ydata_profiling.model.summary.get_series_descriptions` · *function*

## Summary:
Produce per-column summary dictionaries for every series in a table-like object by using the provided Visions typeset to determine each series' type and the provided summarizer to compute the summary. Returns a dict mapping column identifiers to the summary dict produced by the summarizer pipeline.

## Description:
This function is intended to be the worker that converts an entire dataset (DataFrame-like object) into a mapping of column -> summary dict. It belongs in the profiling pipeline after schema/type inference and before aggregation or report rendering: the orchestrator should call this function to compute all column-level summaries.

Known callers / call-site context:
- Profiling orchestration code that needs per-column summaries for a report. No concrete callers were present in the provided snapshot; implementors should expect this function to be invoked once per profiling run with the full dataset, a configured summarizer, a Visions typeset, and an optional progress bar.
- Typical trigger: after the typeset and summarizer are constructed and the dataset is ready for per-column analysis.

Why this is a separate function:
- Separates iteration, per-column error handling, and progress reporting from the summarizer implementation which focuses on a single series.
- Improves reusability and testability: allows testing of iteration and resilience independently of summarizer pipeline implementations.

Note about current implementation status:
- In the provided source, get_series_descriptions currently raises NotImplementedError unconditionally. The remainder of this document specifies the intended contract and a recommended implementation approach that a developer can implement to replace the NotImplementedError.

## Args:
    config (Settings)
        - Type: Settings (configuration object).
        - Role: forwarded into summarizer.summarize for each series; may influence what statistics are computed.
        - Precondition: must conform to what summarizer and registered pipeline functions expect.

    df (Any)
        - Type: Table-like object (commonly a pandas.DataFrame).
        - Requirements:
            * Iterable over column identifiers (e.g., has .columns or supports iter(df) yielding keys).
            * Indexable by column identifier to obtain a single-column sequence/Series (e.g., df[col]).
        - Behavior for special values:
            * If df is None or has zero columns, the function should return {}.

    summarizer (BaseSummarizer)
        - Type: BaseSummarizer instance (per-memory contract, its summarize(config, series, dtype) returns the pipeline's summary dict).
        - Precondition: configured such that summarizer.summarize returns a dict representing the per-series summary.

    typeset (VisionsTypeset)
        - Type: VisionsTypeset instance.
        - Role: used to determine the Visions type of each series prior to calling the summarizer.
        - Note: Visions has multiple public APIs across versions; the function must call whichever typeset API exists in the runtime (e.g., an "infer" or "detect" style method). If the available typeset in the environment exposes no direct series-typing API, the implementor should convert or adapt the typeset usage (for example, by deriving a type from pandas dtype or accepting a precomputed dtype mapping).

    pbar (tqdm)
        - Type: tqdm progress-bar or a compatible object with an update(n: int) method.
        - Role: optional progress reporting. If provided, the function should call pbar.update(1) (or an equivalent) once per column processed.
        - Note: whether to close or finalize pbar is left to the caller; the function should not unilaterally close a caller-owned progress bar unless explicitly agreed by the calling convention.

Interdependencies:
- The dtype value produced from the typeset must be acceptable to summarizer.summarize. In practice, summarizer.summarize will call str(dtype) internally; therefore, typeset-produced dtype should be a Visions type object or otherwise compatible.

## Returns:
    dict
        - Mapping from column identifier to the summary dict returned by the summarizer.
        - If all columns succeed:
            * One entry per column, e.g. {"col_a": { ... summary ... }, "col_b": { ... }, ...}
        - If df has no columns:
            * Returns an empty dict {}.
        - Error / partial results policy (recommended behavior):
            * If summarization for a column raises an exception, the function should capture the exception, record an error payload for that column, and continue processing remaining columns. This is a recommended resilience strategy; implementors may choose to re-raise instead if strict semantics are required.
            * Recommended error payload shape (convention — not enforced by code):
                {
                    "<column>": {
                        "__error__": True,
                        "exception": "<ExceptionClassName>",
                        "message": "<str(exception)>"
                    }
                }
            * The function may also include additional debugging info (e.g., stacktrace) if desired.

## Raises:
    NotImplementedError
        - Condition: in the provided source snapshot the function raises NotImplementedError unconditionally.
    Other exceptions (implementation-dependent)
        - If implemented, the function may propagate exceptions originating from:
            * typeset usage (if type inference fails in a way that the implementation does not catch).
            * summarizer.summarize (e.g., pipeline unpacking errors, type errors).
            * df indexing/iteration (e.g., KeyError).
        - Recommended design: catch per-column exceptions and include them as error payloads in results rather than allowing one column failure to abort the entire run.

## Constraints:
    Preconditions:
        - summarizer must implement summarize(config, series, dtype) and return a dict (per BaseSummarizer contract).
        - df must provide iterable column identifiers and indexable columns.
    Postconditions:
        - Returns a mapping with one key per column attempted. Columns that failed to be summarized will have error payloads if the recommended error-capturing behavior is implemented.
        - The progress bar, if provided, will have been advanced by the number of processed columns; the function will not implicitly close or reset the pbar unless the calling convention expects it.

## Side Effects:
    - Calls pbar.update(1) (or equivalent) per column when pbar is provided.
    - No file or network I/O by this function itself.
    - No mutation of module-level globals.
    - Note: the summarizer pipeline callables may have side effects (user-provided); these are outside the responsibility of this function.

## Control Flow:
flowchart TD
    A[Start] --> B{df is None or has no columns?}
    B -- Yes --> C[Return {}]
    B -- No --> D[Obtain ordered list of columns]
    D --> E[For each column in columns]
    E --> F[series = df[column]]
    F --> G[Determine dtype using typeset (adapter to available API)]
    G --> H[Try: summary = summarizer.summarize(config, series, dtype)]
    H --> I{Succeeded?}
    I -- Yes --> J[results[column] = summary]
    I -- No --> K[results[column] = error payload (recommended)]
    J --> L[If pbar: pbar.update(1)]
    K --> L
    L --> M[Next column]
    M --> N[All columns processed -> return results]

## Examples (recommended usage):
    from tqdm import tqdm
    # df: pandas.DataFrame, summarizer: BaseSummarizer, typeset: VisionsTypeset, config: Settings
    pbar = tqdm(total=len(df.columns))
    results = get_series_descriptions(config, df, summarizer, typeset, pbar)
    # Note: whether to pbar.close() is the caller's responsibility

Example error result (convention):
    {
        "age": {"count": 100, "mean": 35.2, ...},
        "zipcode": {
            "__error__": True,
            "exception": "ValueError",
            "message": "Type inference failed for series 'zipcode'"
        }
    }

## Implementation guidance (concrete steps an implementor can follow):
1. Defensive checks:
    - If df is None: return {}.
    - If summarizer is None: raise ValueError("summarizer is required") or decide preferred behavior.
2. Columns iteration:
    - Prefer df.columns when available to preserve column order (pandas DataFrame).
    - Otherwise use list(iter(df)) to obtain keys.
3. Per-column processing loop:
    a. series = df[col]
    b. Derive dtype via a small adapter that calls the appropriate method on typeset available at runtime. If no direct API exists, fall back to a conservative dtype derived from series' pandas dtype or other metadata.
    c. Call summarizer.summarize(config, series, dtype) and expect a dict result per BaseSummarizer contract.
    d. On success: results[col] = summary.
    e. On exception: capture exception info and store an error payload under results[col] (recommended); do not let the exception stop the overall loop.
    f. If pbar is not None: call pbar.update(1).
4. Return the results dict.

## Rationale:
- The function centralizes iteration and resilience; keeping summarizer logic separate makes pipeline functions focused and pluggable.
- The recommended per-column error-capturing strategy allows generating partial reports even when individual columns fail.

