# `correlations.py`

## `src.ydata_profiling.report.structure.correlations.get_correlation_items` · *function*

## Summary:
Generates renderable correlation items for display in profiling reports, handling multiple correlation methods and visualization formats.

## Description:
Processes correlation data from a summary object and creates appropriate visual representations (heatmaps and tables) for inclusion in profiling reports. This function extracts correlation matrices from the summary and converts them into renderable components based on configuration settings.

The function handles different correlation methods (Pearson, Spearman, Kendall, Phik, Cramér's V) and supports both single correlation matrices and lists of matrices. It dynamically creates either image-based heatmaps or tabular representations based on the configuration.

This logic is extracted into its own function to separate the concerns of correlation data processing from report generation, allowing for cleaner modularization and easier testing of the correlation rendering logic.

## Args:
    config (Settings): Configuration object containing report settings including plot format and correlation table preferences
    summary (BaseDescription): Summary object containing correlation data from the profiling process with a correlations attribute

## Returns:
    Optional[Renderable]: Container object containing correlation visualizations and tables wrapped in tabs, or None if no correlation data exists

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - config must be a valid Settings object with proper plot and html configuration
    - summary must contain a correlations attribute with valid correlation data
    - summary.correlations must be iterable with valid correlation items
    
    Postconditions:
    - Returns a Container with correlation items if correlations exist
    - Returns None if no correlation items are available
    - All returned renderables are properly configured with appropriate IDs and labels

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_correlation_items] --> B{summary.correlations.items()}
    B --> C[For each key, item in correlations]
    C --> D{item is list?}
    D -->|Yes| E[Create diagrams list]
    E --> F[For each item in list]
    F --> G[Create Image for each item]
    G --> H[Create diagrams grid container]
    H --> I{config.correlation_table?}
    I -->|Yes| J[Create tables list]
    J --> K[For each item in list]
    K --> L[Create CorrelationTable for each item]
    L --> M[Create tables tab container]
    M --> N[Create diagrams-tables tab container]
    N --> O[Add to items]
    I -->|No| P[Add diagrams grid to items]
    D -->|No| Q[Create single diagram Image]
    Q --> R{config.correlation_table?}
    R -->|Yes| S[Create CorrelationTable]
    S --> T[Create diagram-tables tab container]
    T --> U[Add to items]
    R -->|No| V[Add diagram to items]
    O --> W[Create final Container with tabs]
    P --> W
    V --> W
    W --> X{len(items) > 0?}
    X -->|Yes| Y[Return Container]
    X -->|No| Z[Return None]
```

## Examples:
    # Basic usage with correlation data
    config = Settings()
    summary = BaseDescription()
    summary.correlations = {"pearson": correlation_matrix}
    result = get_correlation_items(config, summary)
    
    # Usage with multiple correlation methods
    summary.correlations = {
        "pearson": [matrix1, matrix2], 
        "spearman": correlation_matrix
    }
    result = get_correlation_items(config, summary)

