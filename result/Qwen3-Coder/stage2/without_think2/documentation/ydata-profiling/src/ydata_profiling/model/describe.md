# `describe.py`

## `src.ydata_profiling.model.describe.describe` · *function*

## Summary:
Generates a comprehensive statistical description of a DataFrame by analyzing its structure, content, and relationships.

## Description:
The `describe` function orchestrates the complete profiling analysis of a dataset by coordinating multiple specialized analysis components. It serves as the main entry point for generating detailed statistical summaries, variable descriptions, correlation matrices, missing value patterns, and quality alerts for a given DataFrame.

Known callers within the codebase:
- Called by the main profiling pipeline during report generation workflows
- Triggered when users request a complete dataset analysis through the ProfileReport interface
- Invoked during automated data quality assessment routines

This logic is extracted into its own function rather than being inlined because it provides a centralized coordination point for the entire profiling process. This modular approach enables clean separation of concerns between the orchestration layer and individual analysis components, making the system more maintainable, testable, and extensible while ensuring consistent execution flow and data aggregation.

## Args:
    config (Settings): Configuration object containing profiling settings and preferences
    df (pd.DataFrame): Input DataFrame to be analyzed and described
    summarizer (BaseSummarizer): Component responsible for generating summary statistics for each variable
    typeset (VisionsTypeset): Type detection system for identifying variable data types
    sample (Optional[dict]): Custom sample data to use instead of generating a random sample, defaults to None

## Returns:
    BaseDescription: A structured object containing all analysis results including table statistics, variable descriptions, correlations, missing value patterns, alerts, and sample data

## Raises:
    ValueError: Raised when the input DataFrame is None, indicating a lazy ProfileReport without data

## Constraints:
    Preconditions:
        - config must be a valid Settings object with properly initialized configuration
        - df must be a valid pandas DataFrame or compatible structure
        - summarizer must be a valid BaseSummarizer instance
        - typeset must be a valid VisionsTypeset instance
    Postconditions:
        - Returns a complete BaseDescription object with all analysis components populated
        - Input parameters remain unmodified
        - Progress bar is properly managed throughout execution

## Side Effects:
    - Creates progress bar visualization during execution
    - Generates and stores various statistical analyses in memory
    - May create temporary data structures for intermediate calculations
    - Updates progress bar status messages during execution

## Control Flow:
```mermaid
flowchart TD
    A[describe called] --> B{df is None?}
    B -- Yes --> C[raise ValueError]
    B -- No --> D[check_dataframe(df)]
    D --> E[preprocess(config, df)]
    E --> F[Initialize progress bar]
    F --> G[get_series_descriptions]
    G --> H[Extract variable types]
    H --> I[Get table statistics]
    I --> J{table_stats['n'] != 0?}
    J -- Yes --> K[Get active correlations]
    J -- No --> L[Skip correlations]
    K --> M[Calculate correlations]
    M --> N[Filter valid correlations]
    N --> O[Get scatter tasks]
    O --> P[Generate scatter plots]
    P --> Q[Get missing diagrams]
    Q --> R[Generate missing diagrams]
    R --> S[Get sample data]
    S --> T[Detect duplicates]
    T --> U[Get alerts]
    U --> V{timeseries active?}
    V -- Yes --> W[Get time index description]
    W --> X[Build BaseDescription]
    V -- No --> X
    X --> Y[Return BaseDescription]
```

## Examples:
    # Basic usage in profiling workflow
    from ydata_profiling.config import Settings
    from ydata_profiling.model import BaseDescription
    import pandas as pd
    
    config = Settings()
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    
    # Assuming summarizer and typeset are properly initialized
    description = describe(config, df, summarizer, typeset)
    # Returns a complete BaseDescription object with all analysis results
    
    # Usage with custom sample
    custom_sample = {"data": df.head(5)}
    description = describe(config, df, summarizer, typeset, sample=custom_sample)
    # Uses custom sample instead of generating a random one
    
    # Error handling example
    try:
        description = describe(config, None, summarizer, typeset)
    except ValueError as e:
        print(f"Error: {e}")
        # Handle the case where DataFrame is None

