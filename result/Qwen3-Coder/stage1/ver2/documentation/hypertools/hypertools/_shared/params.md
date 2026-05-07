# `params.py`

## `hypertools._shared.params.default_params` · *function*

## Summary:
Returns a copy of default parameters for a specified model, optionally merged with custom parameter overrides.

## Description:
This function retrieves default hyperparameters for a given model type from a global parameters registry and returns a copy of those parameters. It allows for optional customization by merging additional parameters provided in update_dict. This extraction promotes code reuse and maintains centralized parameter management.

## Args:
    model (str): Identifier for the model type to retrieve default parameters for.
    update_dict (dict, optional): Dictionary containing parameter overrides to merge with defaults. Defaults to None.

## Returns:
    dict or None: A dictionary containing the default parameters for the specified model, updated with any values from update_dict. Returns None if no default parameters exist for the specified model and no update_dict is provided.

## Raises:
    None explicitly raised in the function code.

## Constraints:
    Preconditions:
    - The global variable `parameters` must be defined and contain a dictionary mapping model identifiers to parameter dictionaries.
    - The `model` parameter must be a valid key in the `parameters` dictionary or a string that can be used as a dictionary key.
    
    Postconditions:
    - The returned dictionary is a copy of the default parameters, so modifications to the returned dictionary won't affect the original defaults.
    - If update_dict is provided, the returned dictionary will contain merged key-value pairs from both the defaults and update_dict.
    - If update_dict is provided but no defaults exist for the model, the returned dictionary will be a copy of update_dict.

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
    # Get default parameters for a model
    defaults = default_params('linear_regression')
    
    # Get default parameters and override some values
    custom_defaults = default_params('random_forest', {'n_estimators': 100, 'max_depth': 10})
    
    # Handle case where model has no defaults but update_dict is provided
    custom_only = default_params('unknown_model', {'learning_rate': 0.1})  # Returns {'learning_rate': 0.1}
    
    # Handle case where model has no defaults and no update_dict
    no_defaults = default_params('unknown_model')  # Returns None

