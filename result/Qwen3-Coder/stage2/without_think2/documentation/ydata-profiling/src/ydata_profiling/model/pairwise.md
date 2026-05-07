# `pairwise.py`

## `src.ydata_profiling.model.pairwise.get_scatter_tasks` · *function*

## Summary:
Generates a list of variable pairs for scatter plot analysis based on configuration settings and continuous variables.

## Description:
This function determines which variable pairs should be analyzed for scatter plots by examining the interaction configuration settings. It serves as a factory function that creates the task list for pairwise continuous variable scatter plot generation.

The function is called during the profiling pipeline when scatter plot analysis is enabled, specifically when continuous variable interactions are configured to be computed.

## Args:
    config (Settings): Configuration object containing interaction settings including continuous flag and target variables
    continuous_variables (list): List of continuous variables to consider for scatter plot analysis

## Returns:
    List[Tuple[Any, Any]]: A list of tuples representing variable pairs (x, y) for scatter plot generation. Returns an empty list if continuous interactions are disabled.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - config must be a valid Settings object with interactions attribute
        - continuous_variables must be a list-like object
    Postconditions:
        - Returns a list of tuples where each tuple contains two elements
        - If config.interactions.continuous is False, returns empty list regardless of inputs
        - If config.interactions.targets is empty, uses all continuous_variables as targets

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_scatter_tasks] --> B{config.interactions.continuous}
    B -- False --> C[Return empty list]
    B -- True --> D[Get targets from config]
    D --> E{len(targets) == 0}
    E -- True --> F[Set targets = continuous_variables]
    E -- False --> G[Use targets as-is]
    F --> H[Generate task pairs]
    G --> H
    H --> I[Return task list]
```

## Examples:
    Example 1: Continuous interactions disabled
    ```python
    config = Settings()
    config.interactions.continuous = False
    result = get_scatter_tasks(config, ['a', 'b', 'c'])
    # Returns: []
    ```

    Example 2: With targets specified
    ```python
    config = Settings()
    config.interactions.continuous = True
    config.interactions.targets = ['target1', 'target2']
    result = get_scatter_tasks(config, ['var1', 'var2'])
    # Returns: [('target1', 'var1'), ('target2', 'var1'), ('target1', 'var2'), ('target2', 'var2')]
    ```

    Example 3: No targets specified (uses all variables)
    ```python
    config = Settings()
    config.interactions.continuous = True
    config.interactions.targets = []
    result = get_scatter_tasks(config, ['var1', 'var2'])
    # Returns: [('var1', 'var1'), ('var2', 'var1'), ('var1', 'var2'), ('var2', 'var2')]
    ```

## `src.ydata_profiling.model.pairwise.get_scatter_plot` · *function*

## Summary:
Generates a scatter plot for pairwise continuous variable analysis in data profiling, returning HTML representation of the plot.

## Description:
Creates scatter plots for continuous variable pairs to visualize relationships between variables. This function serves as a wrapper that prepares data and delegates plotting to the scatter_pairwise function. It's part of the pairwise analysis functionality used in automated data profiling reports.

The function is extracted to separate data preparation logic from visualization logic, making the code more modular and testable. It handles filtering of continuous variables and manages data cleaning by removing NaN values before plotting.

## Args:
    config (Settings): Configuration object containing plotting settings and HTML formatting options
    df (pd.DataFrame): Input dataframe containing the data to analyze
    x (Any): Variable name for x-axis (can be any type)
    y (Any): Variable name for y-axis (can be any type)
    continuous_variables (list): List of variable names that are considered continuous

## Returns:
    str: HTML string representation of the scatter plot image when both x and y are continuous variables, or empty string when x is not in continuous_variables

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - config must be a valid Settings object
    - df must be a pandas DataFrame
    - continuous_variables must be a list of variable names
    - x and y must be valid column names in df
    
    Postconditions:
    - Returns either a valid HTML string with plot data or empty string
    - Original DataFrame is not modified
    - Plot is properly formatted according to config settings

## Side Effects:
    - Creates matplotlib plots internally
    - May generate temporary files when config.html.inline is False
    - Closes matplotlib figures after plotting

## Control Flow:
```mermaid
flowchart TD
    A[Start get_scatter_plot] --> B{x in continuous_variables?}
    B -- Yes --> C{y == x?}
    C -- Yes --> D[df_temp = df[[x]].dropna()]
    C -- No --> E[df_temp = df[[x,y]].dropna()]
    D --> F[scatter_pairwise call]
    E --> F
    F --> G[Return plot result]
    B -- No --> H[Return empty string]
    H --> G
```

## Examples:
    # Basic usage with continuous variables
    result = get_scatter_plot(config, df, 'age', 'income', ['age', 'income', 'score'])
    # Returns HTML string with scatter plot showing relationship between age and income
    
    # Usage with identical variables (diagonal)
    result = get_scatter_plot(config, df, 'age', 'age', ['age', 'income', 'score'])
    # Returns HTML string with scatter plot for single variable (diagonal)
    
    # Usage with non-continuous variable (returns empty string)
    result = get_scatter_plot(config, df, 'category', 'income', ['age', 'income', 'score'])
    # Returns empty string since 'category' is not in continuous_variables
    
    # Edge case: No matching continuous variables
    result = get_scatter_plot(config, df, 'category1', 'category2', ['age', 'income'])
    # Returns empty string since neither category1 nor category2 are continuous
```

