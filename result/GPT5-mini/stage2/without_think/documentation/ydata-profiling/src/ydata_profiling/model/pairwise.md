# `pairwise.py`

## `src.ydata_profiling.model.pairwise.get_scatter_tasks` · *function*

## Summary:
Generate the list of (target, variable) pairs that should be plotted as pairwise scatter plots when continuous interactions are enabled.

## Description:
This function examines the profiling configuration to decide whether continuous interactions (pairwise scatter plots) are enabled and, if so, constructs the Cartesian product of configured targets and the set of continuous variables to produce plotting tasks.

Known callers within the codebase:
- No direct call sites were provided in the scanned source. Conceptually, this function is intended to be used by the visualization/plotting stage of the profiling pipeline (for example, the scatter-plot generation logic such as scatter_pairwise or a task scheduler that prepares plot jobs) when preparing which pairs of variables to plot.

Typical trigger/context:
- Called during the "interactions" / visualization phase of a profile run after variable types (continuous vs. categorical) have been determined and a list of continuous variables is available.
- The function is used when the configuration flag enabling continuous interactions is true; otherwise it returns no tasks.

Reason for extraction:
- Encapsulates the small but specific logic of deciding whether to produce scatter-plot tasks and how to combine configured targets with discovered continuous variables.
- Keeps plotting/task-scheduling code simpler and isolates configuration handling and pair-generation rules in a single testable function.

## Args:
    config (Settings):
        - Instance of the ydata_profiling Settings object that contains an `interactions` sub-configuration.
        - The function only reads:
            * config.interactions.continuous (bool): whether to create continuous interaction plots.
            * config.interactions.targets (sequence): a sequence (e.g., list) of "target" variable identifiers. May be empty.
        - Preconditions: config must be a valid Settings object (or at least have the `interactions` attribute with the described fields).
    continuous_variables (list):
        - A list (or other sequence) of continuous variable identifiers discovered earlier in the profiling pipeline (typically column names or column indices).
        - Expected element types: strings or other hashable identifiers used by the plotting code. Empty list is allowed.

Interdependencies:
- If config.interactions.targets is an empty sequence, targets are taken from continuous_variables (so targets defaults to continuous_variables).
- If config.interactions.continuous is False, continuous_variables is ignored and the function returns immediately with an empty list.

## Returns:
    List[Tuple[Any, Any]]:
        - A list of 2-tuples (target, variable). Each tuple describes one scatter-plot task where:
            * first element (x) is a target from config.interactions.targets or, if that list is empty, an element from continuous_variables.
            * second element (y) is an element from continuous_variables.
        - Ordering: the result is produced by the comprehension [(x, y) for y in continuous_variables for x in targets]. This means all pairs for the first continuous variable appear first (with targets iterated in their order), then all pairs for the second continuous variable, and so on.
        - Edge cases:
            * If config.interactions.continuous is False: returns an empty list [].
            * If continuous_variables is empty: returns an empty list [] (no y values to pair).
            * If targets and continuous_variables are both empty: returns [].
            * If targets contains elements equal to elements in continuous_variables, self-pairs (x == y) may appear.

## Raises:
    - The function does not explicitly raise any exceptions.
    - Possible runtime exceptions if the provided config is malformed (for example, missing `.interactions` or missing attributes on `.interactions`) — these would be standard AttributeError or TypeError raised by Python when attempting attribute access or calling len() on an unsupported type. The function does not catch these.

## Constraints:
Preconditions:
    - config should expose an `.interactions` attribute with `.continuous` (bool) and `.targets` (sequence) attributes.
    - continuous_variables should be an iterable sequence of variable identifiers (commonly list[str]).

Postconditions:
    - Returns a list (possibly empty) of (target, variable) tuples as described under Returns.
    - If config.interactions.continuous is True, the returned list length equals len(targets) * len(continuous_variables) where targets is either config.interactions.targets (if non-empty) or continuous_variables (if targets was empty).

## Side Effects:
    - None. The function is pure: it does not perform I/O, mutate global state, or call external services. It only reads from the provided inputs and returns a new list.

## Control Flow:
flowchart TD
    Start([Start])
    A{config.interactions.continuous?}
    B[Return []]
    C[targets = config.interactions.targets]
    D{len(targets) == 0?}
    E[targets = continuous_variables]
    F[tasks = [(x, y) for y in continuous_variables for x in targets]]
    G[Return tasks]
    Start --> A
    A -- No --> B
    A -- Yes --> C
    C --> D
    D -- Yes --> E
    D -- No --> F
    E --> F
    F --> G

## Examples:
1) When continuous interactions are disabled:
    config.interactions.continuous = False
    continuous_variables = ["age", "income"]
    -> returns []

2) When targets are specified:
    config.interactions.continuous = True
    config.interactions.targets = ["gender"]
    continuous_variables = ["age", "income"]
    -> returns [("gender", "age"), ("gender", "income")]

3) When no explicit targets are configured (targets empty):
    config.interactions.continuous = True
    config.interactions.targets = []
    continuous_variables = ["age", "income"]
    -> targets defaults to continuous_variables and returns:
       [("age", "age"), ("income", "age"), ("age", "income"), ("income", "income")]
    Note: ordering follows the comprehension (all pairs for the first continuous variable, then the second, etc.). Adjust expected ordering accordingly when consuming tasks.

## `src.ydata_profiling.model.pairwise.get_scatter_plot` · *function*

*No documentation generated.*

