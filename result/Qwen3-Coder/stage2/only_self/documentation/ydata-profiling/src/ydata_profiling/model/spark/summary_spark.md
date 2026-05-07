# `summary_spark.py`

## `src.ydata_profiling.model.spark.summary_spark.spark_describe_1d` · *function*

## Summary:
Processes a Spark DataFrame column to generate descriptive statistics and type information for profiling.

## Description:
Handles the one-dimensional descriptive statistics computation for individual columns of Spark DataFrames. This function prepares Spark DataFrame columns by normalizing missing values, determining appropriate data types (either through inference or schema inspection), and then delegates the actual statistical computation to a configured summarizer instance.

The function serves as a specialized adapter in the Spark profiling pipeline, bridging Spark-specific data handling with the generic profiling infrastructure. It's typically invoked during column-wise profiling operations when processing individual DataFrame columns.

## Args:
    config (Settings): Configuration object containing profiling settings, including whether to enable automatic data type inference
    series (DataFrame): A PySpark DataFrame representing a single column of data to be described
    summarizer (BaseSummarizer): An instance of a summarizer that provides the actual statistical computation logic for different data types
    typeset (VisionsTypeset): Type inference system used to determine data types and cast data accordingly

## Returns:
    dict: A dictionary containing the complete descriptive statistics and metadata for the input series, as produced by the summarizer's summarize method

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The series parameter must be a valid PySpark DataFrame with exactly one column
    - The config parameter must be a properly initialized Settings object
    - The summarizer parameter must be a valid BaseSummarizer instance
    - The typeset parameter must be a properly initialized VisionsTypeset instance
    
    Postconditions:
    - The returned dictionary contains the complete descriptive statistics for the input series
    - The series DataFrame has had null values replaced with np.nan before processing

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_describe_1d] --> B[Fill nulls with np.nan]
    B --> C{config.infer_dtypes}
    C -->|True| D[Infer type using typeset.infer_type()]
    C -->|False| E[Determine type from schema]
    D --> F[Cast series to inferred type]
    E --> F
    F --> G[Call summarizer.summarize()]
    G --> H[Return summary dict]
```

## Examples:
```python
# Typical usage in a Spark profiling pipeline
from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import BaseSummarizer
from visions import VisionsTypeset

# Assuming we have a Spark DataFrame column 'age'
result = spark_describe_1d(
    config=Settings(),
    series=spark_df.select('age'),
    summarizer=BaseSummarizer(),
    typeset=VisionsTypeset()
)
```

## `src.ydata_profiling.model.spark.summary_spark.spark_get_series_descriptions` · *function*

## Summary:
Generates descriptive statistics for each column in a Spark DataFrame using parallel processing with ordered result consolidation.

## Description:
Processes each column of a Spark DataFrame concurrently using a thread pool to compute detailed statistical descriptions. This function implements a Spark-specific approach to series description generation by leveraging multiprocessing for performance optimization. It handles the parallel execution of column-wise statistical analysis while ensuring the final result maintains the original column ordering.

## Args:
    config (Settings): Configuration object containing profiling settings and options
    df (DataFrame): PySpark DataFrame containing the data to be described
    summarizer (BaseSummarizer): Summarizer instance used to compute statistical measures
    typeset (VisionsTypeset): Typeset used for type detection and validation
    pbar (tqdm): Progress bar instance for tracking processing progress

## Returns:
    dict: Dictionary mapping column names to their respective descriptive statistics dictionaries. Each entry contains computed statistics and metadata about the corresponding column, with results ordered to match the original DataFrame column sequence.

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - Input DataFrame must have valid column names
    - All parameters must be properly initialized instances of their respective types
    - Progress bar must be a valid tqdm instance
    
    Postconditions:
    - Returns a dictionary with keys matching all DataFrame column names
    - Each value is a dictionary containing column statistics
    - Column order in returned dictionary matches DataFrame column order exactly

## Side Effects:
    - Updates the progress bar status and position during execution
    - Modifies the progress bar's postfix string to indicate current processing column
    - May cause temporary memory spikes due to multiprocessing overhead
    - Creates and manages a ThreadPool with 12 worker threads

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_series_descriptions] --> B[Initialize empty series_description dict]
    B --> C[Create args list with (column_name, df) tuples]
    C --> D[Create ThreadPool with 12 workers]
    D --> E[Process each column in parallel using multiprocess_1d]
    E --> F{Processing complete?}
    F -->|No| G[Update progress bar with column name]
    G --> H[Remove value_counts from description]
    H --> I[Store description in series_description]
    I --> J[Update progress bar]
    J --> F
    F -->|Yes| K[Reorder series_description to match df.columns]
    K --> L[Sort columns according to config.sort]
    L --> M[Return series_description]
```

## Examples:
    # Typical usage in Spark profiling workflow
    from ydata_profiling.config import Settings
    from ydata_profiling.model.summarizer import BaseSummarizer
    from visions import VisionsTypeset
    from tqdm import tqdm
    
    config = Settings()
    df = spark.read.parquet("data.parquet")
    summarizer = BaseSummarizer()
    typeset = VisionsTypeset()
    pbar = tqdm(total=len(df.columns))
    
    descriptions = spark_get_series_descriptions(config, df, summarizer, typeset, pbar)
    print(descriptions["column_name"])

