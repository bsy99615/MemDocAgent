# `summary_spark.py`

## `src.ydata_profiling.model.spark.summary_spark.spark_describe_1d` · *function*

## Summary:
Processes a Spark DataFrame series for statistical profiling by inferring or mapping data types and delegating to a summarizer.

## Description:
This function serves as the Spark-specific implementation for describing 1D data series during data profiling. It prepares the Spark DataFrame by handling missing values and determining appropriate data types before passing control to a summarizer to generate descriptive statistics.

The function is designed to be called as part of the Spark data profiling pipeline, typically when processing individual columns of a Spark DataFrame for statistical summary generation.

## Args:
    config (Settings): Configuration object containing profiling settings
    series (DataFrame): Spark DataFrame representing a single column/series to profile
    summarizer (BaseSummarizer): Summarizer instance responsible for generating the actual statistics
    typeset (VisionsTypeset): Type inference system for determining data types

## Returns:
    dict: Statistical summary of the series including various descriptive metrics and type information

## Raises:
    None explicitly raised in the function body

## Constraints:
    Preconditions:
    - The series parameter must be a valid PySpark DataFrame with a single column
    - config must be a properly initialized Settings object
    - summarizer must be a valid BaseSummarizer instance
    - typeset must be a properly initialized VisionsTypeset instance
    
    Postconditions:
    - The returned dictionary contains complete statistical profiling information
    - The series DataFrame is processed to handle null values appropriately

## Side Effects:
    None explicitly stated in the function body

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_describe_1d] --> B[Fill NaN values with np.nan]
    B --> C{config.infer_dtypes}
    C -- True --> D[Infer type using typeset]
    C -- False --> E[Determine dtype from schema]
    D --> F[Cast to inferred type]
    E --> F
    F --> G[Map dtype to Visions type]
    G --> H[Call summarizer.summarize()]
    H --> I[Return summary dict]
```

## Examples:
```python
# Typical usage in Spark profiling pipeline
from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import BaseSummarizer
from visions import VisionsTypeset

config = Settings()
summarizer = BaseSummarizer()
typeset = VisionsTypeset()
result = spark_describe_1d(config, spark_df_column, summarizer, typeset)
```

## `src.ydata_profiling.model.spark.summary_spark.spark_get_series_descriptions` · *function*

## Summary:
Processes Spark DataFrame columns in parallel to generate descriptive statistics for each column using multiprocessing.

## Description:
This function takes a Spark DataFrame and generates descriptive statistics for each column using parallel processing with a thread pool. It processes each column independently by calling the underlying `describe_1d` function and aggregates the results into a dictionary. The function removes the "value_counts" field from each column's description to reduce memory usage and optimize performance. This function is specifically designed for Spark environments to enable efficient column-wise analysis.

## Args:
    config (Settings): Configuration settings for the profiling process
    df (DataFrame): Input Spark DataFrame to be described
    summarizer (BaseSummarizer): Summarizer instance for generating statistics
    typeset (VisionsTypeset): Typeset for type detection and validation
    pbar (tqdm): Progress bar for tracking processing progress

## Returns:
    dict: Dictionary mapping column names to their descriptive statistics (with "value_counts" removed), with columns ordered according to configuration settings

## Raises:
    None explicitly raised - relies on underlying functions for exception handling

## Constraints:
    Preconditions:
    - Input DataFrame must be a valid Spark DataFrame
    - All parameters must be properly initialized and not None
    - Config should contain valid settings for profiling
    - Progress bar should be properly initialized
    
    Postconditions:
    - Returns a dictionary with one entry per DataFrame column
    - Column order in returned dictionary matches DataFrame column order
    - Each column description has "value_counts" field removed
    - Progress bar is updated appropriately during execution

## Side Effects:
    - Updates the progress bar with processing status
    - Processes DataFrame columns in parallel using ThreadPool with 12 workers
    - May consume significant memory due to multiprocessing overhead
    - Modifies the progress bar's postfix string during execution
    - Removes "value_counts" from each column's description dictionary

## Control Flow:
```mermaid
flowchart TD
    A[Start spark_get_series_descriptions] --> B[Initialize empty series_description dict]
    B --> C[Create args list with (column_name, df) tuples]
    C --> D[Create ThreadPool with 12 workers]
    D --> E[Process columns in parallel using multiprocess_1d]
    E --> F{Processing complete?}
    F -->|No| G[Update progress bar with column name]
    G --> H[Remove value_counts from description]
    H --> I[Store description in series_description]
    I --> J[Continue processing]
    F -->|Yes| K[Reorder series_description to match df.columns]
    K --> L[Sort columns according to config.sort]
    L --> M[Return series_description]
```

## Examples:
    # Typical usage in Spark profiling workflow
    from pyspark.sql import SparkSession
    from ydata_profiling.config import Settings
    from ydata_profiling.model.summarizer import BaseSummarizer
    from visions import VisionsTypeset
    from tqdm import tqdm
    
    spark = SparkSession.builder.appName("Profile").getOrCreate()
    df = spark.read.parquet("data.parquet")
    
    config = Settings()
    summarizer = BaseSummarizer()
    typeset = VisionsTypeset()
    pbar = tqdm(total=len(df.columns))
    
    descriptions = spark_get_series_descriptions(config, df, summarizer, typeset, pbar)

