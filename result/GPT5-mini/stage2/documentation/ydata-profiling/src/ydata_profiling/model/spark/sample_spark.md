# `sample_spark.py`

## `src.ydata_profiling.model.spark.sample_spark.spark_get_sample` · *function*

## Summary:
Produce a small list of Sample records extracted from a PySpark DataFrame according to the configured sampling parameters; currently only a "head" sample is implemented and collected to a pandas.DataFrame.

## Description:
This function collects representative samples from a Spark DataFrame for inclusion in profiling reports. It is implemented specifically for PySpark DataFrame inputs and returns a list of lightweight Sample Pydantic models.

Known callers (in the provided code snapshot):
- No direct callers of this specific function were found in the provided repository snapshot. Conceptually it is intended to be invoked by higher-level profiling/reporting code when the input dataset is a PySpark DataFrame (i.e., the profiling pipeline should dispatch to this Spark-specific sampler when appropriate).

Why this is extracted into its own function:
- Sampling behavior for Spark requires different mechanics (e.g., using DataFrame.limit and toPandas to move a small slice to the driver) compared with in-process pandas sampling. Extracting Spark-specific logic keeps sampling responsibilities separated from generic sampling logic and from presentation/rendering code; it centralizes driver-collection mechanics and the construction of Sample objects.

## Args:
    config (Settings):
        - Type: ydata_profiling.config.Settings
        - Role: Configuration container. The function reads the following fields (it assumes they exist on config.samples):
            * config.samples.head (int): number of head rows to collect (n_head).
            * config.samples.tail (int): number of tail rows requested (n_tail); present but not implemented.
            * config.samples.random (int): number of random rows requested (n_random); present but not implemented.
        - Constraints: The code expects config and config.samples to have the above attributes; missing attributes will raise an AttributeError at runtime. The function does not validate that these values are integers.

    df (pyspark.sql.dataframe.DataFrame):
        - Type: pyspark.sql.dataframe.DataFrame
        - Role: The input dataset to sample from.
        - Constraints: Must be a valid PySpark DataFrame object with head, limit, and toPandas methods. Passing None or a non-DataFrame object will result in an exception from the attempted attribute access or method calls.

## Returns:
    List[Sample]:
        - A list of ydata_profiling.model.sample.Sample instances.
        - Possible outcomes:
            * Empty list []:
                - If the DataFrame is empty (determined by len(df.head(1)) == 0), the function returns immediately with an empty list.
                - If sampling counts are zero (e.g., config.samples.head == 0 and no other implemented samples), the returned list may be empty.
            * Single-element list containing the "head" sample:
                - If config.samples.head > 0 and the DataFrame is non-empty, one Sample is appended:
                    - Sample.id == "head"
                    - Sample.name == "First rows"
                    - Sample.data == result of df.limit(n_head).toPandas(), i.e., a pandas.DataFrame containing the first n_head rows (or fewer if the DataFrame has fewer rows).
            * The function does not currently append "tail" or "random" samples; when those counts are > 0 it only emits warnings and does not add corresponding Sample entries.
        - Notes: Sample.data is created by collecting the limited Spark DataFrame to the driver via toPandas(), therefore it is a pandas.DataFrame suitable for serialization and downstream rendering.

## Raises:
    - The function itself does not explicitly raise exceptions in its body.
    - Runtime exceptions can propagate from underlying operations:
        * AttributeError: if config, config.samples, or df lack required attributes/methods.
        * Exceptions raised by PySpark methods (e.g., calling df.head(1), df.limit(...), or toPandas()) such as execution/analysis errors, or driver memory errors when collecting to pandas. These are not caught and will propagate to the caller.

## Constraints:
    Preconditions:
        - config must have a .samples attribute exposing integer attributes head, tail, and random (the code accesses config.samples.head, etc.).
        - df must be a valid PySpark DataFrame and non-null.
        - The environment must allow collecting small partitions to the driver (toPandas will attempt to transfer data to driver memory).

    Postconditions:
        - The returned list contains zero or one Sample for the implemented behaviors:
            * If n_head > 0 and df is non-empty: the returned list contains a Sample with id "head" whose data is a pandas.DataFrame of up to n_head rows.
            * No "tail" or "random" Sample objects are included by this implementation (only warnings are emitted when requested).

## Side Effects:
    - Emits warnings via the warnings.warn standard library when config.samples.tail > 0 or config.samples.random > 0 to notify callers that these sampling modes are not implemented for Spark.
    - Calls df.limit(n_head).toPandas() when requesting a head sample. This collects data from the cluster to the driver process (network I/O and memory allocation on the driver). Large n_head may cause significant driver memory usage.
    - No file, external network, or global-state writes are performed by this function beyond the collection-to-driver effect described above.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckEmpty{len(df.head(1)) == 0?}
    CheckEmpty -- Yes --> ReturnEmpty([return []])
    CheckEmpty -- No --> ReadHead[n_head = config.samples.head]
    ReadHead --> HeadGT0{n_head > 0?}
    HeadGT0 -- Yes --> AddHead[append Sample(id="head", data=df.limit(n_head).toPandas(), name="First rows")]
    HeadGT0 -- No --> SkipHead[skip]
    AddHead --> ReadTail[n_tail = config.samples.tail]
    SkipHead --> ReadTail
    ReadTail --> TailGT0{n_tail > 0?}
    TailGT0 -- Yes --> WarnTail[warnings.warn("tail sample not implemented for spark...")]
    TailGT0 -- No --> SkipTail[skip]
    WarnTail --> ReadRandom[n_random = config.samples.random]
    SkipTail --> ReadRandom
    ReadRandom --> RandomGT0{n_random > 0?}
    RandomGT0 -- Yes --> WarnRandom[warnings.warn("random sample not implemented for spark...")]
    RandomGT0 -- No --> SkipRandom[skip]
    WarnRandom --> ReturnSamples([return samples])
    SkipRandom --> ReturnSamples

## Examples:
Example — basic usage in profiling pipeline (illustrative):

- Typical call context:
    - A profiling dispatcher detects the input is a PySpark DataFrame and calls spark_get_sample(config, df) to collect small, serializable sample payloads for reporting.

- Minimal usage example (pseudo-usage; adapt to concrete Settings type in your codebase):
    from types import SimpleNamespace
    # Construct a lightweight config-like object with the expected shape:
    cfg = SimpleNamespace(samples=SimpleNamespace(head=5, tail=0, random=0))
    # df is a pyspark.sql.DataFrame obtained from SparkSession.read or similar
    samples = spark_get_sample(cfg, df)
    # samples is a list of Sample objects; if df is non-empty and head>0, samples[0].data is a pandas.DataFrame

- Edge case — empty DataFrame:
    # If df has no rows: spark_get_sample(cfg, df) -> [] (empty list), no warnings emitted.

Notes:
- Because toPandas() is used to convert the head slice, this function should only be used with small head sizes relative to available driver memory. If you need full-featured sampling (tail/random/per-column), implement those branches or use a reimplementation that performs distributed-safe sampling and returns appropriately shaped Sample objects.

