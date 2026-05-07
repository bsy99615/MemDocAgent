# `pairwise.py`

## `src.ydata_profiling.model.pairwise.get_scatter_tasks` · *function*

## Summary
Generates a list of variable pairs for scatter plot analysis based on configuration settings and continuous variables.

## Description
Creates a collection of (x, y) variable pairs for pairwise scatter plot generation. This function determines which continuous variable interactions should be computed based on the configuration settings and returns the appropriate task pairs for processing.

The function is extracted into its own component to separate the logic of determining which scatter plot tasks to generate from the actual plotting implementation, allowing for cleaner code organization and easier testing of the task generation logic.

## Args
- config (Settings): Configuration object containing interaction settings including continuous flag and target variables
- continuous_variables (list): List of variable names identified as continuous for analysis

## Returns
- List[Tuple[Any, Any]]: List of (x, y) tuples representing variable pairs for scatter plot generation. Returns empty list when continuous interactions are disabled.

## Raises
- None explicitly raised by this function

## Constraints
- Preconditions: 
  - config must be a valid Settings object with proper interactions configuration
  - continuous_variables must be a list of variable names
- Postconditions:
  - Returns either an empty list or a list of valid (x, y) variable pair tuples
  - All returned tuples contain elements that exist in continuous_variables or targets list

## Side Effects
- None

## Control Flow
```mermaid
flowchart TD
    A[Start get_scatter_tasks] --> B{config.interactions.continuous}
    B -- False --> C[Return empty list]
    B -- True --> D[Get config.interactions.targets]
    D --> E{len(targets) == 0}
    E -- True --> F[targets = continuous_variables]
    E -- False --> G[Use targets as-is]
    F --> H[Generate tasks with nested loops]
    G --> H
    H --> I[Return tasks list]
```

## Examples
```python
# Basic usage with continuous interactions enabled
config = Settings(interactions=Interactions(continuous=True))
continuous_vars = ['age', 'income', 'score']
tasks = get_scatter_tasks(config, continuous_vars)
# Returns [('age', 'age'), ('income', 'age'), ('score', 'age'), 
#          ('age', 'income'), ('income', 'income'), ('score', 'income'),
#          ('age', 'score'), ('income', 'score'), ('score', 'score')]

# With specific targets configured
config = Settings(interactions=Interactions(continuous=True, targets=['income']))
continuous_vars = ['age', 'income', 'score']
tasks = get_scatter_tasks(config, continuous_vars)
# Returns [('income', 'age'), ('income', 'income'), ('income', 'score')]
```

## `src.ydata_profiling.model.pairwise.get_scatter_plot` · *function*

## Summary:
Generates a scatter plot for pairwise variable analysis when both variables are continuous.

## Description:
This function creates a scatter plot visualization for two continuous variables by filtering out missing values and delegating the actual plotting to the scatter_pairwise function. It serves as a preprocessing step that ensures only valid continuous variable pairs are visualized. The function acts as a gatekeeper, ensuring that only continuous variables are processed for scatter plots, preventing errors when dealing with categorical or mixed-type data.

## Args:
    config (Settings): Configuration settings for the visualization
    df (pd.DataFrame): The input DataFrame containing the data
    x (Any): The first variable/column name to plot on x-axis
    y (Any): The second variable/column name to plot on y-axis
    continuous_variables (list): List of variable names that are considered continuous

## Returns:
    str: HTML representation of the scatter plot if both variables are continuous, empty string otherwise

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - config must be a valid Settings object
    - df must be a valid pandas DataFrame (imported as pd)
    - continuous_variables must be a list of variable names
    - x and y must be valid column names in the DataFrame
    
    Postconditions:
    - Returns HTML string representation of scatter plot when both variables are continuous
    - Returns empty string when either variable is not in continuous_variables list

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_scatter_plot] --> B{x in continuous_variables?}
    B -- Yes --> C{y == x?}
    C -- Yes --> D[Create df_temp = df[[x]].dropna()]
    C -- No --> E[Create df_temp = df[[x,y]].dropna()]
    D --> F[Call scatter_pairwise]
    E --> F
    F --> G[Return result]
    B -- No --> H[Return ""]
```

## Examples:
    # Basic usage with continuous variables
    result = get_scatter_plot(config, df, 'age', 'income', ['age', 'income', 'score'])
    
    # Usage with identical variables (should work)
    result = get_scatter_plot(config, df, 'age', 'age', ['age', 'income'])
    
    # Usage with non-continuous variable (returns empty string)
    result = get_scatter_plot(config, df, 'category', 'income', ['age', 'income'])

