# `pairwise.py`

## `src.ydata_profiling.model.pairwise.get_scatter_tasks` · *function*

## Summary:
Generates a list of variable pairs for scatter plot analysis based on configuration settings and continuous variable lists.

## Description:
This function creates a collection of (x, y) variable pairs that define which continuous variables should be plotted against each other in scatter plots. It respects the interaction configuration settings to determine whether to compute continuous variable interactions and which variables should serve as targets for analysis.

The function is designed to be called during the profiling process to prepare the tasks needed for generating scatter plot visualizations between continuous variables. It handles two key configuration options: whether to compute continuous interactions at all, and which variables should be treated as targets for analysis.

## Args:
    config (Settings): Configuration object containing interaction settings including continuous flag and target variables
    continuous_variables (list): List of variable names that are continuous in nature

## Returns:
    List[Tuple[Any, Any]]: A list of (x, y) tuples representing variable pairs for scatter plot generation. Each tuple contains two variable names where x is the target variable and y is the continuous variable being plotted against.

## Raises:
    None explicitly raised by this function

## Constraints:
    Preconditions:
    - config must be a valid Settings object with properly initialized interactions configuration
    - continuous_variables must be a list of variable names (strings or other hashable types)
    
    Postconditions:
    - Returns an empty list if config.interactions.continuous is False
    - Returns a list of tuples where each tuple contains elements from continuous_variables
    - If no targets are specified, all continuous variables become both targets and variables

## Side Effects:
    None

## Control Flow:
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

## Examples:
```python
# Example 1: Continuous interactions enabled with no specific targets
config = Settings(interactions=Interactions(continuous=True, targets=[]))
continuous_vars = ['age', 'income', 'score']
tasks = get_scatter_tasks(config, continuous_vars)
# Result: [('age', 'age'), ('income', 'age'), ('score', 'age'), 
#          ('age', 'income'), ('income', 'income'), ('score', 'income'),
#          ('age', 'score'), ('income', 'score'), ('score', 'score')]

# Example 2: Continuous interactions disabled
config = Settings(interactions=Interactions(continuous=False, targets=[]))
continuous_vars = ['age', 'income', 'score']
tasks = get_scatter_tasks(config, continuous_vars)
# Result: []

# Example 3: With specific target variables
config = Settings(interactions=Interactions(continuous=True, targets=['target']))
continuous_vars = ['age', 'income', 'score']
tasks = get_scatter_tasks(config, continuous_vars)
# Result: [('target', 'age'), ('target', 'income'), ('target', 'score')]
```

## `src.ydata_profiling.model.pairwise.get_scatter_plot` · *function*

## Summary:
Generates a scatter plot for pairwise continuous variable analysis or returns an empty string for non-continuous variables.

## Description:
Creates a scatter plot visualization for two continuous variables using the scatter_pairwise function. This function acts as a filter and preparer, ensuring that only continuous variables are processed for scatter plot generation. When the x variable is not in the continuous variables list, it returns an empty string, indicating no plot should be generated.

## Args:
    config (Settings): Configuration settings for the visualization
    df (pd.DataFrame): The input DataFrame containing the data
    x (Any): The first variable/column name for the scatter plot
    y (Any): The second variable/column name for the scatter plot
    continuous_variables (list): List of variable names that are considered continuous

## Returns:
    str: HTML representation of the scatter plot if both variables are continuous, otherwise an empty string

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - config must be a valid Settings object
    - df must be a valid pandas DataFrame
    - continuous_variables must be a list of variable names
    - x and y must be valid column names in the DataFrame
    
    Postconditions:
    - Returns either a valid HTML string representing a scatter plot or empty string
    - Does not modify the input DataFrame or configuration

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start get_scatter_plot] --> B{x in continuous_variables?}
    B -- Yes --> C{y == x?}
    C -- Yes --> D[Create df_temp = df[[x]].dropna()]
    C -- No --> E[Create df_temp = df[[x, y]].dropna()]
    D --> F[Call scatter_pairwise]
    E --> F
    F --> G[Return result]
    B -- No --> H[Return ""]
```

## Examples:
    # Basic usage with continuous variables
    result = get_scatter_plot(config, df, 'age', 'income', ['age', 'income', 'score'])
    
    # Usage with same variable (diagonal)
    result = get_scatter_plot(config, df, 'age', 'age', ['age', 'income', 'score'])
    
    # Usage with non-continuous variable
    result = get_scatter_plot(config, df, 'category', 'income', ['age', 'income', 'score'])
    # Returns empty string

