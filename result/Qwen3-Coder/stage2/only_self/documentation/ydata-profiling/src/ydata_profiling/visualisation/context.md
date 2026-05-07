# `context.py`

## `src.ydata_profiling.visualisation.context.manage_matplotlib_context` · *function*

## Summary:
Context manager that applies custom matplotlib styling and ensures proper cleanup of matplotlib configuration.

## Description:
A context manager that temporarily modifies matplotlib's rcParams to apply a consistent visual style for data visualization. It registers matplotlib converters, applies custom styling parameters, sets seaborn style, and ensures proper restoration of original settings upon exit. This function encapsulates the complexity of matplotlib configuration management to ensure consistent visual appearance across different plotting operations.

## Args:
    None

## Returns:
    Generator that yields control to the wrapped code block, allowing execution of matplotlib plotting operations with the custom styling applied.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Matplotlib and seaborn must be available in the environment
    - The function should be used as a context manager (with 'with' statement)
    
    Postconditions:
    - All matplotlib configuration changes are reverted upon exiting the context
    - Original matplotlib rcParams are restored exactly as they were before entering the context
    - Matplotlib converters are properly deregistered

## Side Effects:
    - Modifies global matplotlib rcParams during execution
    - Registers and deregisters matplotlib converters
    - Sets seaborn style to "white"
    - May affect subsequent matplotlib plotting operations due to global state changes

## Control Flow:
```mermaid
flowchart TD
    A[Start manage_matplotlib_context] --> B[Save original rcParams]
    B --> C[Define custom rcParams]
    C --> D[Register matplotlib converters]
    D --> E[Update rcParams with custom values]
    E --> F[Set seaborn style to "white"]
    F --> G[Yield control to caller]
    G --> H[On exit (finally block)]
    H --> I[Deregister matplotlib converters]
    I --> J[Restore original rcParams]
    J --> K[End]
```

## Examples:
```python
# Basic usage as context manager
with manage_matplotlib_context():
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.savefig('output.png')

# Usage with multiple plots
with manage_matplotlib_context():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot([1, 2, 3], [1, 4, 9])
    ax2.plot([1, 2, 3], [1, 8, 27])
    plt.tight_layout()
```

