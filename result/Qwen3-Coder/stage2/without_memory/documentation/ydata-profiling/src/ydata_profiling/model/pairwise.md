# `pairwise.py`

## `src.ydata_profiling.model.pairwise.get_scatter_tasks` · *function*

## Summary:
Generates a list of variable pair tuples for continuous scatter plot analysis based on configuration settings.

## Description:
Creates task pairs for pairwise scatter plots by combining target variables with continuous variables. This function is used to determine which variable combinations should be analyzed for scatter plots in the profiling report. The function respects configuration settings to control whether continuous interactions are computed and which variables serve as targets for analysis.

## Args:
    config (Settings): Configuration object containing interaction settings including continuous flag and target variables
    continuous_variables (list): List of continuous variables to be used in scatter plot analysis

## Returns:
    List[Tuple[Any, Any]]: List of (x, y) tuples representing variable pairs for scatter plot analysis. Returns empty list if continuous interactions are disabled in configuration.

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
        - config must be a valid Settings object with interactions attribute
        - continuous_variables must be a list-like object
    Postconditions:
        - Returns a list of tuples where each tuple contains two elements
        - If config.interactions.continuous is False, returns empty list regardless of inputs
        - If config.interactions.targets is empty, uses continuous_variables as targets

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_scatter_tasks] --> B{config.interactions.continuous}
    B -- False --> C[Return empty list]
    B -- True --> D[Get targets from config]
    D --> E{len(targets) == 0}
    E -- True --> F[targets = continuous_variables]
    E -- False --> G[Use targets from config]
    F --> H[Generate pairs]
    G --> H
    H --> I[Return tasks list]
```

## Examples:
    # Basic usage with targets configured
    config = Settings()
    config.interactions.continuous = True
    config.interactions.targets = ['var1', 'var2']
    continuous_vars = ['var3', 'var4', 'var5']
    tasks = get_scatter_tasks(config, continuous_vars)
    # Returns [('var1', 'var3'), ('var1', 'var4'), ('var1', 'var5'), ('var2', 'var3'), ('var2', 'var4'), ('var2', 'var5')]

    # Usage with no targets configured (defaults to continuous variables)
    config = Settings()
    config.interactions.continuous = True
    config.interactions.targets = []
    continuous_vars = ['var1', 'var2']
    tasks = get_scatter_tasks(config, continuous_vars)
    # Returns [('var1', 'var1'), ('var1', 'var2'), ('var2', 'var1'), ('var2', 'var2')]
```

## `src.ydata_profiling.model.pairwise.get_scatter_plot` · *function*

## Summary:
Generates a scatter plot for pairwise variable comparisons when both variables are continuous.

## Description:
This function creates scatter plots for pairs of continuous variables in a dataset. It serves as a helper function to generate visualizations for correlation analysis between numeric variables. The function filters out missing values and delegates the actual plotting to the scatter_pairwise utility function.

## Args:
    config (Settings): Configuration object containing visualization settings and preferences
    df (pd.DataFrame): The input DataFrame containing the data to visualize
    x (Any): The first variable/column name for the scatter plot
    y (Any): The second variable/column name for the scatter plot
    continuous_variables (list): List of variable names that are considered continuous/numeric

## Returns:
    str: HTML representation of the scatter plot when both variables are continuous, empty string otherwise

## Raises:
    None explicitly raised - however, underlying scatter_pairwise function may raise exceptions related to plotting

## Constraints:
    Preconditions:
    - config must be a valid Settings object
    - df must be a valid pandas DataFrame
    - continuous_variables must be a list of variable names
    - x and y must be valid column names in the DataFrame
    
    Postconditions:
    - Returns HTML string representation of scatter plot or empty string
    - Original DataFrame is not modified
    - No side effects on global state

## Side Effects:
    None directly - but the underlying scatter_pairwise function may generate matplotlib figures and potentially write to disk if configured to do so

## Control Flow:
```mermaid
flowchart TD
    A[Start get_scatter_plot] --> B{x in continuous_variables?}
    B -- Yes --> C{y == x?}
    C -- Yes --> D[df_temp = df[[x]].dropna()]
    C -- No --> E[df_temp = df[[x,y]].dropna()]
    D --> F[scatter_pairwise(config, df_temp[x], df_temp[y], x, y)]
    E --> F
    F --> G[Return HTML plot]
    B -- No --> H[Return empty string]
    H --> G
```

## Examples:
    # Basic usage with continuous variables
    result = get_scatter_plot(config, df, 'age', 'income', ['age', 'income', 'score'])
    
    # Usage with identical variables (diagonal)
    result = get_scatter_plot(config, df, 'age', 'age', ['age', 'income', 'score'])
    
    # Usage with non-continuous variable (returns empty string)
    result = get_scatter_plot(config, df, 'category', 'income', ['age', 'income', 'score'])
```

