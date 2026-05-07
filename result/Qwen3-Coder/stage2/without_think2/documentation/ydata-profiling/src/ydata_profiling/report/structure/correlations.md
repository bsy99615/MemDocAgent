# `correlations.py`

## `src.ydata_profiling.report.structure.correlations.get_correlation_items` · *function*

## Summary:
Generates a structured presentation of correlation analysis results including heatmaps and tables for different correlation methods.

## Description:
Creates a hierarchical presentation structure containing correlation visualizations and tables for various correlation methods (Pearson, Spearman, Kendall, Phik, Cramér's V, Auto). This function processes correlation data from a BaseDescription object and organizes it into a tabbed interface with optional heatmap and table views. It handles both single correlation matrices and multiple correlation matrices (per variable group) and integrates with the report generation pipeline to produce interactive correlation visualizations.

The function extracts correlation data from the summary object and transforms it into presentation-ready components using the plotting and rendering infrastructure. It's designed to be called during report generation when correlation analysis results need to be displayed in the final output.

## Args:
    config (Settings): Configuration object containing report settings including plot formats, correlation table preferences, and HTML styling options. Must have properly initialized correlation settings and HTML style labels.
    summary (BaseDescription): Data structure containing correlation analysis results and metadata from the profiling process. Must contain a correlations attribute with recognized correlation method keys.

## Returns:
    Optional[Renderable]: A Container object representing the correlation section with tabs for different correlation methods, or None if no correlation data exists. When correlation data is present, returns a Container with sequence_type="tabs" containing correlation visualization components.

## Raises:
    None explicitly raised - All exceptions are propagated from underlying components

## Constraints:
    Preconditions:
    - config must be a valid Settings object with properly initialized correlation settings
    - summary must contain a correlations attribute with valid correlation data
    - summary.correlations must be a dictionary with recognized correlation method keys ("pearson", "spearman", "kendall", "phi_k", "cramers", "auto")
    - config.html.style._labels must be properly initialized for multi-variable correlation displays
    
    Postconditions:
    - Returns a Container with sequence_type="tabs" when correlation data exists
    - Returns None when no correlation data is available
    - All returned Renderable objects are properly initialized with required metadata

## Side Effects:
    None - Pure transformation function with no external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start get_correlation_items] --> B[Initialize items list]
    B --> C[Define key_to_data mapping]
    C --> D[Get image_format from config]
    D --> E[Iterate over summary.correlations.items()]
    E --> F{item is list?}
    F -->|Yes| G[Process list of correlation matrices]
    F -->|No| H[Process single correlation matrix]
    G --> I[Create diagrams list]
    I --> J[Loop through list items]
    J --> K[Create Image for each item]
    K --> L[Build diagrams Grid Container]
    L --> M{config.correlation_table?}
    M -->|Yes| N[Create tables list]
    N --> O[Loop through list items]
    O --> P[Create CorrelationTable for each item]
    P --> Q[Build tables Tab Container]
    Q --> R[Combine diagrams_grid + tables_tab in tabs Container]
    R --> S[Add to items]
    M -->|No| T[Add diagrams_grid to items]
    H --> U[Create single diagram Image]
    U --> V{config.correlation_table?}
    V -->|Yes| W[Create single CorrelationTable]
    W --> X[Combine diagram + table in tabs Container]
    X --> Y[Add to items]
    V -->|No| Z[Add diagram to items]
    E --> AA[Build final Container with items]
    AA --> AB{len(items) > 0?}
    AB -->|Yes| AC[Return Container]
    AB -->|No| AD[Return None]
```

## Examples:
```python
# Basic usage in report generation
from ydata_profiling.config import Settings
from ydata_profiling.model import BaseDescription
from ydata_profiling.report.structure.correlations import get_correlation_items

# Assuming config and summary are properly initialized with correlation data
config = Settings()
summary = BaseDescription(...)  # With correlation data

# Generate correlation presentation components
correlation_section = get_correlation_items(config, summary)

# If correlation data exists, this returns a Container with correlation tabs
if correlation_section is not None:
    # Add to report structure
    report.add(correlation_section)
    
# Example with correlation table enabled
config.correlation_table = True
correlation_section_with_tables = get_correlation_items(config, summary)
# Returns Container with both heatmaps and tables for each correlation method
```

