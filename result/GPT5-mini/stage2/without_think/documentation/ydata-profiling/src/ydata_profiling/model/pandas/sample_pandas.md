# `sample_pandas.py`

## `src.ydata_profiling.model.pandas.sample_pandas.pandas_get_sample` · *function*

## Summary:
Generates a list of sample descriptors (Sample objects) extracted from a pandas DataFrame according to the configured head, tail and random sample sizes.

## Description:
This function collects up to three types of row samples from a pandas DataFrame — the first rows, the last rows, and a random sample — based on integer sizes configured in the provided Settings object. It returns a list of Sample datamodel instances, each holding an identifier, the sampled DataFrame slice, and a human-readable name.

Known callers / usage within the codebase:
- ydata_profiling.model.sample.get_sample: Defines the higher-level API for sample extraction; for pandas DataFrame inputs, pandas_get_sample serves as the concrete implementation.
- ydata_profiling.profile_report.ProfileReport.get_sample: Exposes the sample information produced during the profiling pipeline; the profile generation pipeline will call into the model sampling logic (the abstract get_sample) which resolves to this implementation when profiling pandas DataFrames.

Why this logic is extracted:
- Centralizes DataFrame-specific sampling behavior in one small, testable function.
- Keeps the higher-level profiling flow generic (via get_sample) and delegates DataFrame mechanics (head/tail/sample calls and ordering of samples) to this implementation.
- Encapsulates the mapping between configuration (config.samples.*) and the produced Sample objects (ids, names, and data content).

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Expected shape/fields used by this function:
            * config.samples.head: int (number of rows to take from the top)
            * config.samples.tail: int (number of rows to take from the bottom)
            * config.samples.random: int (number of rows to sample randomly)
        - Semantics: values are interpreted as non-negative integers. Values <= 0 are treated as "do not produce that sample".
        - Interdependencies: none between head/tail/random; each is considered independently.

    df (pandas.DataFrame):
        - Type: pandas.DataFrame (or an object that implements len(), head(n), tail(n) and sample(n))
        - Precondition: df should be a pandas.DataFrame. Passing an incompatible object may raise attribute errors at runtime.

## Returns:
    List[Sample]
    - Each Sample is an instance of ydata_profiling.model.sample.Sample with fields:
        * id (str): one of "head", "tail", "random"
        * data: a pandas.DataFrame containing the sampled rows
        * name (str): a human-readable title ("First rows", "Last rows", "Random sample")
        * caption: remains None in this function (not set here)
    - Ordering: Samples are appended in deterministic order: head (if produced), tail (if produced), random (if produced).
    - Edge-case return values:
        * Returns an empty list if len(df) == 0 (no samples produced).
        * Returns an empty list if all configured sizes (head, tail, random) are <= 0.
        * Head/tail sampling with n greater than number of rows returns all rows (pandas.head/tail behavior).
        * Random sampling with n greater than number of rows will not be produced safely — see Raises.

## Raises:
    ValueError:
        - Trigger: When config.samples.random > len(df) and a random sample is requested.
        - Cause: pandas.DataFrame.sample(n=n_random) is called with n greater than the population size while replace=False (the default), which raises:
          "ValueError: Cannot take a larger sample than population when 'replace=False'".
        - Note: The function does not catch this exception; callers that may configure random > len(df) should handle or pre-validate.

    AttributeError / TypeError (implicit):
        - Trigger: If df does not implement head/tail/sample or len, an attribute or type error may be raised when those methods are invoked.
        - Cause: The function assumes a pandas.DataFrame-like object; no explicit type checking is performed.

## Constraints:
    Preconditions:
        - config must have a .samples attribute with integer attributes head, tail and random.
        - df must be a pandas.DataFrame (or compatible object) with methods head(n), tail(n) and sample(n).
        - Caller should ensure config.samples.random <= len(df) if they want to avoid ValueError from pandas.sample.

    Postconditions:
        - The returned list contains 0–3 Sample objects corresponding to the requested sample types.
        - The original DataFrame df is not mutated by this function.
        - The Sample.data values are DataFrame objects created by pandas head/tail/sample operations and reflect the requested rows.

## Side Effects:
    - No I/O (no file, network, or stdout activity).
    - No global state mutation.
    - No in-place modification of the input DataFrame.
    - Relies on pandas library call df.sample which performs the sampling algorithm internally (no external service calls).

## Control Flow:
flowchart TD
    Start --> CheckEmpty
    CheckEmpty{len(df) == 0?}
    CheckEmpty -- Yes --> ReturnEmpty[Return []]
    CheckEmpty -- No --> GetHead
    GetHead --> HeadCond{config.samples.head > 0?}
    HeadCond -- Yes --> AppendHead[Append Sample(id="head", data=df.head(...))]
    HeadCond -- No --> SkipHead
    AppendHead --> GetTail
    SkipHead --> GetTail
    GetTail --> TailCond{config.samples.tail > 0?}
    TailCond -- Yes --> AppendTail[Append Sample(id="tail", data=df.tail(...))]
    TailCond -- No --> SkipTail
    AppendTail --> GetRandom
    SkipTail --> GetRandom
    GetRandom --> RandomCond{config.samples.random > 0?}
    RandomCond -- No --> ReturnSamples[Return samples list]
    RandomCond -- Yes --> AppendRandom[Append Sample(id="random", data=df.sample(...))]
    AppendRandom --> ReturnSamples

## Examples:
1) Typical successful usage:
    - Given: df has 100 rows; config.samples.head = 5, config.samples.tail = 5, config.samples.random = 10
    - Outcome: returns a list of three Sample objects:
        * Sample(id="head", data=df.head(5), name="First rows")
        * Sample(id="tail", data=df.tail(5), name="Last rows")
        * Sample(id="random", data=df.sample(n=10), name="Random sample")

2) Empty DataFrame:
    - Given: df has 0 rows
    - Outcome: returns []

3) Partial configuration:
    - Given: config.samples.head = 3, config.samples.tail = 0, config.samples.random = 0
    - Outcome: returns [Sample(id="head", data=df.head(3), name="First rows")]

4) Error scenario (must be handled by caller):
    - Given: df has 5 rows; config.samples.random = 10
    - Behavior: pandas.DataFrame.sample(n=10) will raise ValueError ("Cannot take a larger sample than population when 'replace=False'") because n_random > len(df). The function does not catch this exception; callers should validate sizes beforehand or catch ValueError.

Notes:
- This function intentionally delegates the actual sampling semantics to pandas.DataFrame.head/tail/sample; callers that need different semantics (e.g., sampling with replacement) should adjust configuration or implement a wrapper before calling this function.

