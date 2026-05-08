# `describe.py`

## `src.ydata_profiling.model.describe.describe` · *function*

## Summary:
Produces a full profiling description of a pandas DataFrame by running the summarization, table-level statistics, correlations, scatter plots, missing-data diagrams, sampling, duplicate detection and alerts, and returns a BaseDescription capturing those results.

## Description:
This function orchestrates the end-to-end profiling steps for a dataset (DataFrame) and packages results into a BaseDescription object. It performs validation and preprocessing of the DataFrame, computes per-series descriptions, derives table-level statistics, computes enabled correlations, builds a scatter-matrix for numeric/time-series variables, generates missing-value diagrams, takes a sample, detects duplicates, collects alerts, optionally analyzes a timeseries index, and records package/reproduction metadata.

Known callers within the codebase:
- This file does not include call sites. Typical callers are higher-level report-generation code paths (for example, a ProfileReport builder or other top-level API) which trigger profiling after assembling a Settings object, a summarizer instance and a VisionsTypeset. There are no explicit call sites in this module.

Why this logic is extracted into its own function:
- Responsibility boundary: describe centralizes the entire profiling workflow (validation → preprocessing → per-variable summary → table-level analyses → aggregation into a description object). Extracting this orchestration isolates side-effecting steps (progress bar updates, calls to many helper modules) from presentation or report-generation layers so tests and callers can request a ready-to-use BaseDescription without embedding orchestration logic into UI/report code.

## Args:
    config (Settings):
        Configuration controlling which analyses run, progress-bar behavior, timeseries options, and other profiling options. Must implement .progress_bar (boolean), .vars.timeseries.active (boolean), .title (string), and .json() (string) as used in this function.
    df (pd.DataFrame):
        The pandas DataFrame to profile. Must not be None. Will be validated by check_dataframe and may be replaced by the preprocessed DataFrame returned by preprocess(config, df).
    summarizer (BaseSummarizer):
        Summarizer instance used by get_series_descriptions to produce per-series summaries. Must conform to the BaseSummarizer interface expected by get_series_descriptions.
    typeset (VisionsTypeset):
        Visions typeset used by get_series_descriptions to infer/validate variable types.
    sample (Optional[dict], default=None):
        Optional custom sampling descriptor. If None the function uses get_sample(config, df) to obtain sample(s). If provided, it is passed to get_custom_sample to build the sample(s) included in the output.

Interdependencies:
- config controls multiple downstream branches (e.g., which correlations are active, whether timeseries index analysis runs, and whether progress display is enabled).
- If sample is provided, get_custom_sample is used; otherwise get_sample is used.

## Returns:
    BaseDescription
        A populated BaseDescription object containing these fields (constructed and returned at the end):
        - analysis: BaseAnalysis(config.title, date_start, date_end) — start/end timestamps for profiling and the report title.
        - time_index_analysis: TimeIndexAnalysis or None — present only when timeseries analysis is active and get_time_index_description returned a value.
        - table: table_stats — table-level statistics computed by get_table_stats (a mapping/dict including at least "n" for number of rows).
        - variables: series_description — mapping from column name to per-series description as produced by get_series_descriptions.
        - scatter: scatter_matrix — nested mapping {x: {y: scatter_result}} for pairs returned by get_scatter_tasks; values may be None when no plot was produced.
        - correlations: dict — mapping correlation_name -> correlation result for enabled correlations; entries with None are filtered out.
        - missing: dict — mapping of missing-diagram name -> diagram result (None-filtered).
        - alerts: alerts structure returned by get_alerts for the computed table/variables/correlations.
        - package: dict with metadata:
            - ydata_profiling_version: value of __version__
            - ydata_profiling_config: JSON string of config via config.json()
        - sample: samples — sample(s) produced by get_sample or get_custom_sample.
        - duplicates: duplication statistics/data returned by get_duplicates.

Edge-case return values:
- correlations will be an empty dict if table_stats["n"] == 0 (no rows).
- time_index_analysis will be None unless both config.vars.timeseries.active is truthy and get_time_index_description returns a non-empty description.

## Raises:
    ValueError:
        If df is None, the function raises ValueError("Can not describe a `lazy` ProfileReport without a DataFrame.") and performs no further work.

Other exceptions:
- This function calls many helpers (get_series_descriptions, get_table_stats, calculate_correlation, get_scatter_plot, get_missing_diagram, get_sample/get_custom_sample, get_duplicates, get_alerts, get_time_index_description). Any exceptions raised by those helpers will propagate unless caught upstream; this function does not catch or wrap those exceptions.

## Constraints:
Preconditions:
- df must be provided (not None).
- config must provide attributes and behavior expected by downstream helpers (progress_bar, vars.timeseries.active, json(), title, and options used by get_active_correlations and other helpers).
- summarizer and typeset must be compatible with get_series_descriptions.

Postconditions:
- The returned BaseDescription will contain consistent snapshots of the analyses carried out during the function run: per-variable descriptions, computed table statistics, computed correlations (when applicable), scatter results (for produced tasks), missing-diagram outputs, sample(s), duplicates and alerts, and package metadata.
- The DataFrame passed in may be replaced by a preprocessed DataFrame internally (preprocess(config, df)) but the original external reference is not mutated by this function unless preprocess or other helpers mutate it (this function does not explicitly reassign the caller's reference).

## Side Effects:
- Progress output: If config.progress_bar is truthy, a tqdm progress bar is used and will emit progress updates to stdout/console. The progress() helper is used to integrate pbar with internal functions.
- No files, databases, or network calls are directly performed by this function itself; any I/O or network access would occur inside helper functions (not wrapped here).
- The function records package metadata by calling config.json() (serializing the config to JSON) and reading the local __version__ value.
- No global variables are mutated by this function (it builds local structures and returns a BaseDescription).

## Control Flow:
flowchart TD
    Start --> ValidateDF{df is None?}
    ValidateDF -- Yes --> RaiseValueError[Raise ValueError]
    ValidateDF -- No --> CheckDF[check_dataframe(df)]
    CheckDF --> Preprocess[preprocess(config, df)]
    Preprocess --> GetSeries[call get_series_descriptions]
    GetSeries --> DeriveVars[derive variables, supported and interval columns]
    DeriveVars --> GetTable[get_table_stats]
    GetTable --> HasRows{table_stats["n"] != 0?}
    HasRows -- Yes --> GetCorrNames[get_active_correlations(config)]
    GetCorrNames --> CalcCorrs[for each correlation_name: calculate_correlation]
    CalcCorrs --> FilterNone[filter out None correlations]
    HasRows -- No --> SkipCorrs[correlations = {}]
    SkipCorrs --> ScatterTasks[get_scatter_tasks for interval columns]
    ScatterTasks --> BuildScatter[loop scatter_tasks -> get_scatter_plot]
    BuildScatter --> MissingMap[get_missing_active(config, table_stats)]
    MissingMap --> GetMissing[for each missing_map item: get_missing_diagram]
    GetMissing --> SampleChoice{sample is None?}
    SampleChoice -- Yes --> GetSample[get_sample(config, df)]
    SampleChoice -- No --> CustomSample[get_custom_sample(sample)]
    SampleChoice --> DupsAndMetrics[get_duplicates -> returns metrics, duplicates]
    DupsAndMetrics --> UpdateTable[table_stats.update(metrics)]
    UpdateTable --> GetAlerts[get_alerts(table_stats, series_description, correlations)]
    GetAlerts --> TimeIndexCheck{config.vars.timeseries.active?}
    TimeIndexCheck -- Yes --> GetTimeIndex[get_time_index_description(config, df, table_stats)]
    TimeIndexCheck -- No --> SkipTimeIndex
    GetTimeIndex --> BuildPackage[prepare package metadata]
    SkipTimeIndex --> BuildPackage
    BuildPackage --> CreateAnalysis[BaseAnalysis(title, date_start, date_end)]
    CreateAnalysis --> BuildDescription[BaseDescription(...)]
    BuildDescription --> Return[return BaseDescription]
    Return --> End

## Examples:
Basic usage (happy path):

    from ydata_profiling.config import Settings
    from ydata_profiling.model.summarizer import BaseSummarizer
    from visions import VisionsTypeset
    import pandas as pd

    config = Settings()            # configured with desired options
    df = pd.DataFrame(...)         # DataFrame to profile (must not be None)
    summarizer = MySummarizer()   # subclass/implementation of BaseSummarizer
    typeset = VisionsTypeset()     # configured visions typeset

    try:
        description = describe(config, df, summarizer, typeset)
        # description is a BaseDescription with fields described above.
    except ValueError as exc:
        # This happens when df is None
        raise

Handling the case of a custom sample:

    custom_sample = {"type": "random", "n": 100}
    description = describe(config, df, summarizer, typeset, sample=custom_sample)

