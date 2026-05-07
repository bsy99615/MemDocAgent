# `params.py`

## `hypertools._shared.params.default_params` · *function*

## Summary:
Returns a copy of default hyperparameters for a specified model, optionally updated with custom parameters.

## Description:
This function retrieves the default parameter set for a given model type from a global parameters registry and allows for selective updates with custom parameters. It serves as a centralized mechanism for managing model-specific default configurations while supporting runtime customization.

## Args:
    model (str): Identifier for the model type to retrieve defaults for. Must correspond to a key in the global `parameters` dictionary.
    update_dict (dict, optional): Dictionary containing parameter overrides to apply to the default parameters. Defaults to None.

## Returns:
    dict or None: A dictionary containing the default parameters for the specified model, updated with values from `update_dict` if provided. Returns None if the model is not found in the parameters registry.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
        - The global variable `parameters` must be defined and contain a mapping from model names to parameter dictionaries.
        - The `model` argument must be a string that exists as a key in the `parameters` dictionary, or the function will return None.
    Postconditions:
        - The returned dictionary is a copy of the default parameters, ensuring that modifications to the result don't affect the original defaults.
        - If `update_dict` is provided, the returned dictionary contains merged key-value pairs from both the defaults and the update dictionary.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start default_params] --> B{model in parameters?}
    B -- Yes --> C[params = parameters[model].copy()]
    B -- No --> D[params = None]
    C --> E{update_dict provided?}
    D --> E
    E -- Yes --> F{params is None?}
    F -- Yes --> G[params = {}]
    F -- No --> H[params.update(update_dict)]
    G --> H
    H --> I[Return params]
    E -- No --> I
    I --> J[End]
```

## Examples:
    # Retrieve default parameters for a model
    defaults = default_params("linear_regression")
    
    # Retrieve and update parameters
    custom_defaults = default_params("logistic_regression", {"max_iter": 1000, "tol": 1e-4})
    
    # Handle unknown model gracefully
    unknown_params = default_params("unknown_model")  # Returns None

