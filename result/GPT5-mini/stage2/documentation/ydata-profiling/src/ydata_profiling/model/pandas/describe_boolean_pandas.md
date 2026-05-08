# `describe_boolean_pandas.py`

## `src.ydata_profiling.model.pandas.describe_boolean_pandas.pandas_describe_boolean_1d` · *function*

## Summary:
Extracts the most frequent non-NaN value and its count from a precomputed value-counts series, computes a normalized imbalance score for the column, stores these into the provided summary dict, and returns the unchanged config and series along with the mutated summary.

## Description:
This function implements the pandas-specific finalization step for a boolean column's 1D summary in the profiling pipeline. It expects that upstream code has already computed per-value counts excluding NaNs and placed that pandas Series under summary["value_counts_without_nan"]. The function:

- Reads value_counts = summary["value_counts_without_nan"].
- Sets summary["top"] to value_counts.index[0] and summary["freq"] to value_counts.iloc[0].
- Computes summary["imbalance"] by calling column_imbalance_score(value_counts, len(value_counts)).
- Returns (config, series, summary) to preserve the pipeline API.

Known callers and context:
- This function is the pandas-backed handler used when profiling boolean-like Series during the 1D summarization stage. The immediate call sites are not included in the inspected snippet; typically a per-column profiling controller:
  1. Computes value_counts_without_nan = series.dropna().value_counts()
  2. Populates summary with that key
  3. Invokes this boolean-describe function to finalize summary entries
  4. Collects returned (config, series, summary) for downstream formatting and aggregation

Why this is a separate function:
- It isolates boolean-specific post-processing (selecting top/freq, computing imbalance) from value counting and rendering logic, enabling reuse, testing, and consistent handling across series types while preserving a uniform pipeline signature.

## Args:
    config (Settings):
        - Type: Settings
        - Role: Configuration object passed through profiling stages. Not read or modified by this function; returned unchanged.
    series (pd.Series):
        - Type: pandas Series
        - Role: The column being summarized. Not modified; returned unchanged.
    summary (dict):
        - Type: dict
        - Required key:
            - "value_counts_without_nan": pandas.Series where the index are unique values and values are counts (the upstream code must compute and insert this).
        - Role: Input aggregate container that this function mutates in place by adding/updating keys "top", "freq", and "imbalance".

Interdependencies:
- The function delegates imbalance computation to column_imbalance_score(value_counts, n_classes) and passes n_classes = len(value_counts). The caller must ensure value_counts is a pandas Series-like object compatible with .index and .iloc access.

## Returns:
    Tuple[Settings, pd.Series, dict]
        - config: the same Settings object passed in (identity preserved).
        - series: the same pandas Series passed in (identity preserved).
        - summary: the same dict passed in, but mutated to include:
            - "top": value_counts.index[0] — the first index entry from value_counts (interpreted as the most frequent value if upstream ordering is descending).
            - "freq": value_counts.iloc[0] — the corresponding count for that top value.
            - "imbalance": numeric score computed by column_imbalance_score; for n_classes > 1 this returns a normalized entropy-based score in the range [0, 1] (0 = perfectly balanced given entropy-based formula; 1 = maximally imbalanced as determined by the metric), for n_classes == 1 it returns 0.

Edge-case return behavior:
- The function always returns a 3-tuple (config, series, summary) on successful completion. If an exception occurs (see Raises), nothing is guaranteed about the summary content.

## Raises:
    - KeyError:
        - When summary does not contain the "value_counts_without_nan" key (attempting summary["value_counts_without_nan"] triggers this).
    - IndexError:
        - When value_counts exists but is empty (accessing value_counts.index[0] or value_counts.iloc[0] triggers an IndexError).
    - TypeError / AttributeError:
        - If value_counts is not pandas-like (missing .index or .iloc), operations will raise TypeError/AttributeError from pandas or Python internals.
    - Any exception raised by column_imbalance_score:
        - e.g., if that function receives unexpected types; under normal usage with a pandas Series this should not occur.

## Constraints:
Preconditions (must be true before calling):
    - summary contains the key "value_counts_without_nan".
    - summary["value_counts_without_nan"] is a pandas Series-like object produced by upstream counting logic (typically series.dropna().value_counts()).
    - The caller is responsible for ensuring the Series is ordered so that the most frequent value appears first if that semantics is required; this function simply takes the first element.

Postconditions (guarantees after a successful return):
    - summary contains the keys "top", "freq", and "imbalance".
    - The returned config and series are the same objects passed in (no in-function replacement).

Behavioral notes:
    - Tie handling: if multiple values share the same max count, the one that appears first in value_counts (i.e., index[0]) is chosen. Upstream ordering determines which value is considered top in ties.
    - Imbalance semantics: column_imbalance_score uses entropy-based normalization; for two or more classes it returns a float typically in [0, 1]; for a single class it returns 0.

## Side Effects:
    - Mutates the provided summary dict in place (adds/overwrites "top", "freq", "imbalance").
    - No file, network, or global state side effects.
    - Calls column_imbalance_score (a pure computation function with no side effects in normal implementation).

## Control Flow:
flowchart TD
    Start --> ReadVC[value_counts = summary["value_counts_without_nan"]]
    ReadVC --> CheckEmpty{value_counts has >= 1 element?}
    CheckEmpty -- No --> IndexError[/IndexError raised by .index[0] or .iloc[0]/]
    CheckEmpty -- Yes --> SetTopFreq[summary.update({"top": value_counts.index[0], "freq": value_counts.iloc[0]})]
    SetTopFreq --> ComputeImbalance[summary["imbalance"] = column_imbalance_score(value_counts, len(value_counts))]
    ComputeImbalance --> Return[return config, series, summary]

## Examples:
1) Typical profiling pipeline sequence (minimal example steps):
   - Upstream: value_counts = series.dropna().value_counts()
   - Upstream: summary = {"value_counts_without_nan": value_counts, ...}
   - Call: config, series, summary = pandas_describe_boolean_1d(config, series, summary)
   - Result: summary now contains "top" (most frequent non-NaN value), "freq" (its count), and "imbalance" (entropy-based normalized score).

2) Defensive caller pattern to avoid exceptions:
   - If series.dropna().empty:
       - Short-circuit: set summary["top"] = None, summary["freq"] = 0, summary["imbalance"] = 0 (or handle per desired semantics) and skip calling pandas_describe_boolean_1d.
   - Else:
       - Ensure value_counts was computed and placed in summary, then call the function.

Implementation hints for reimplementation:
    - Use the first index and first iloc element of the pandas Series stored under summary["value_counts_without_nan"] for "top" and "freq".
    - Pass the value_counts object and its length to column_imbalance_score to compute the imbalance.
    - Preserve and return the original config and series objects.

