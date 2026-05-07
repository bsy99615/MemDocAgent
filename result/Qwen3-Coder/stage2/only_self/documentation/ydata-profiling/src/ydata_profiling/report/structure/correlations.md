# `correlations.py`

## `src.ydata_profiling.report.structure.correlations.get_correlation_items` · *function*

## Summary:
Generates renderable correlation items for a data profiling report, including heatmaps and tables for various correlation methods.

## Description:
Processes correlation data from a BaseDescription summary and creates visual representations (heatmaps) and tabular displays for different correlation methods. This function extracts correlation matrices from the summary and converts them into renderable components suitable for inclusion in HTML reports. It handles both single correlation matrices and lists of correlation matrices (for different variable groups) and supports conditional display of both heatmap and table views based on configuration settings.

The function is extracted into its own component to separate the logic of transforming correlation data into presentation-ready renderables from the higher-level report generation process. This allows for cleaner separation of concerns and makes the correlation display logic reusable and testable independently.

## Args:
    config (Settings): Configuration object containing report settings including plot formats, correlation method selections, and display preferences
    summary (BaseDescription): Data profiling summary containing correlation matrices and metadata

## Returns:
    Optional[Renderable]: A Container renderable object containing correlation heatmaps and tables organized in tabs, or None if no correlation data is available

## Raises:
    None explicitly raised - All exceptions would come from underlying dependencies like plot.correlation_matrix or rendering functions

## Constraints:
    Preconditions:
    - config must be a valid Settings object with properly initialized plot and html configuration
    - summary must be a BaseDescription object with a populated correlations attribute
    - summary.correlations must contain valid correlation data (either single matrices or lists of matrices)
    
    Postconditions:
    - Returns a Container with correlation items if summary contains correlation data
    - Returns None if summary contains no correlation data
    - All returned renderables are properly configured with appropriate metadata and styling

## Side Effects:
    None directly observable - The function only processes data and creates renderable objects without modifying external state

## Control Flow:
```mermaid
flowchart TD
    A[Start get_correlation_items] --> B[Initialize items list]
    B --> C[Iterate through summary.correlations.items()]
    C --> D{Is item a list?}
    D -->|Yes| E[Process list of correlation matrices]
    D -->|No| F[Process single correlation matrix]
    E --> G[Create diagrams for each matrix]
    G --> H[Create diagrams grid container]
    H --> I{config.correlation_table enabled?}
    I -->|Yes| J[Create tables for each matrix]
    J --> K[Create tables tab container]
    K --> L[Create diagrams-tables tab container]
    L --> M[Add to items list]
    I -->|No| N[Add diagrams grid to items list]
    F --> O[Create single diagram]
    O --> P{config.correlation_table enabled?}
    P -->|Yes| Q[Create single table]
    Q --> R[Create diagram-table tab container]
    R --> S[Add to items list]
    P -->|No| T[Add diagram to items list]
    M --> U[Create final correlation container]
    S --> U
    T --> U
    U --> V{Items list not empty?}
    V -->|Yes| W[Return correlation container]
    V -->|No| X[Return None]
```

## Examples:
```python
# Basic usage with correlation data
from ydata_profiling.config import Settings
from ydata_profiling.model import BaseDescription

# Assuming we have a populated summary with correlation data
config = Settings()
summary = BaseDescription()

# Generate correlation items for report
correlation_renderable = get_correlation_items(config, summary)

# Check if correlation data was available
if correlation_renderable is not None:
    # Add to report content
    report_content.append(correlation_renderable)
else:
    # Handle case where no correlations were calculated
    print("No correlation data available")
```

