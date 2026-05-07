# `describe.py`

## `src.ydata_profiling.model.describe.describe` · *function*

## Summary:
Creates a comprehensive statistical description of a DataFrame by analyzing its structure, variables, correlations, missing values, and other key characteristics.

## Description:
The `describe` function serves as the main entry point for generating a complete statistical profile of a dataset. It orchestrates multiple analysis components including variable type detection, table statistics calculation, correlation analysis, missing value visualization, scatter plots, duplicate detection, and alert generation. This function is designed to be called internally by the profiling system rather than directly by users.

This logic is extracted into its own function to enforce a clear separation of concerns and make the profiling pipeline modular and testable. It encapsulates the complete workflow of data analysis while maintaining proper dependency management and progress tracking.

## Args:
    config (Settings): Configuration object containing analysis parameters and settings
    df (pd.DataFrame): The input DataFrame to be analyzed
    summarizer (BaseSummarizer): Object responsible for summarizing data characteristics
    typeset (VisionsTypeset): Typeset for variable type detection and classification
    sample (Optional[dict]): Custom sample data to use instead of generating a random sample. If None, a random sample is generated

## Returns:
    BaseDescription: A structured object containing all analysis results including table statistics, variable descriptions, correlations, missing value patterns, scatter plots, alerts, and metadata

## Raises:
    ValueError: When the input DataFrame is None, indicating a lazy ProfileReport without data

## Constraints:
    Preconditions:
        - The DataFrame must be valid (checked via check_dataframe)
        - All required configuration parameters must be properly initialized
        - The summarizer and typeset objects must be properly configured
    
    Postconditions:
        - The returned BaseDescription object contains all analysis results
        - Progress bar is properly updated throughout execution
        - All analysis components are executed in the correct order

## Side Effects:
    - Creates progress bar visualization during execution
    - May perform I/O operations when generating samples or visualizations
    - Updates internal progress tracking state
    - Generates and stores various data visualizations (correlations, missing value diagrams, scatter plots)

## Control Flow:
```mermaid
flowchart TD
    A[Start describe()] --> B{df is None?}
    B -- Yes --> C[raise ValueError]
    B -- No --> D[check_dataframe(df)]
    D --> E[preprocess(config, df)]
    E --> F[Initialize progress bar with 5 base tasks]
    F --> G[get_series_descriptions()]
    G --> H[Extract variable types]
    H --> I[Filter supported columns]
    I --> J[get_table_stats()]
    J --> K{table_stats.n != 0?}
    K -- Yes --> L[get_active_correlations()]
    L --> M[calculate_correlation() for each]
    M --> N[Filter non-null correlations]
    K -- No --> O[Skip correlations]
    O --> P[get_scatter_tasks()]
    P --> Q[get_scatter_plot() for each task]
    Q --> R[get_missing_active()]
    R --> S[get_missing_diagram() for each]
    S --> T[Handle custom sample or get_sample()]
    T --> U[get_duplicates()]
    U --> V[get_alerts()]
    V --> W{timeseries.active?}
    W -- Yes --> X[get_time_index_description()]
    X --> Y[Build BaseDescription]
    W -- No --> Z[Build BaseDescription]
    Y --> AA[Return BaseDescription]
    Z --> AA
```

## Examples:
```python
# Typical usage within the profiling system
from ydata_profiling.config import Settings
from ydata_profiling.model.summarizer import BaseSummarizer
from visions import VisionsTypeset
import pandas as pd

config = Settings()
df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
summarizer = BaseSummarizer()
typeset = VisionsTypeset()

description = describe(config, df, summarizer, typeset)
# Returns a BaseDescription object with complete analysis results

# Using custom sample
custom_sample = {'data': df.head(5)}
description = describe(config, df, summarizer, typeset, sample=custom_sample)
```

