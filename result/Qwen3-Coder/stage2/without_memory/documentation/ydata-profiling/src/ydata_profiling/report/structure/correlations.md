# `correlations.py`

## `src.ydata_profiling.report.structure.correlations.get_correlation_items` · *function*

## Summary:
Generates renderable correlation items from a summary object for visualization in reports.

## Description:
Processes correlation data from a summary object and creates appropriate renderable components (images and/or tables) for displaying correlation matrices. This function handles different correlation methods (Pearson, Spearman, Kendall, Phik, Cramér's V) and formats them according to configuration settings.

## Args:
    config (Settings): Configuration object containing report settings including plot format and correlation table preferences
    summary (BaseDescription): Summary object containing correlation data organized by method type

## Returns:
    Optional[Renderable]: Container of correlation renderable items if correlations exist, otherwise None

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - config must be a valid Settings object with proper plot and html configuration
    - summary must be a valid BaseDescription object containing correlations data
    - summary.correlations must be iterable and contain valid correlation data
    
    Postconditions:
    - Returns a Container with correlation items when correlations exist
    - Returns None when no correlations are present in summary
    - All returned renderables are properly configured with appropriate IDs and labels

## Side Effects:
    None directly observable

## Control Flow:
```mermaid
flowchart TD
    A[Start get_correlation_items] --> B{summary.correlations.items()}
    B --> C{item is list?}
    C -->|Yes| D[Process list of correlation matrices]
    C -->|No| E[Process single correlation matrix]
    D --> F[Create diagrams grid]
    F --> G{config.correlation_table?}
    G -->|Yes| H[Create tables tab]
    G -->|No| I[Add diagrams grid to items]
    H --> J[Create diagrams-tables tab]
    J --> K[Add to items]
    I --> K
    E --> L[Create single diagram]
    L --> M{config.correlation_table?}
    M -->|Yes| N[Create table]
    M -->|No| O[Add diagram to items]
    N --> P[Create diagram-table tabs]
    P --> Q[Add to items]
    O --> Q
    Q --> R[Create final container]
    R --> S{items length > 0?}
    S -->|Yes| T[Return container]
    S -->|No| U[Return None]
```

## Examples:
```python
# Basic usage with correlation data
config = Settings()
summary = BaseDescription()
# ... populate summary with correlation data ...
renderable = get_correlation_items(config, summary)
# Returns Container with correlation visualizations or None
```

