# `params.py`

## `hypertools._shared.params.default_params` · *function*

## Summary:
Retrieves default parameter configuration for a specified model and optionally merges with custom updates.

## Description:
This function serves as a centralized parameter management utility that fetches predefined default parameters for a given model type and allows for optional customization through update dictionaries. It provides a clean interface for accessing model-specific configurations while supporting flexible parameter overrides. When a model type doesn't have predefined parameters, it gracefully handles the situation by either returning None or creating an empty dictionary based on whether update parameters are provided.

## Args:
    model (str): Identifier for the model type to retrieve default parameters for.
    update_dict (dict, optional): Dictionary containing parameter updates to merge with defaults. Defaults to None.

## Returns:
    dict or None: A dictionary containing merged parameters if the model exists and update_dict is provided, a copy of default parameters if model exists and update_dict is None, an empty dict if model doesn't exist but update_dict is provided, or None if model doesn't exist and update_dict is None.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
    - The `model` argument should be a string that can be used as a key in the `parameters` global variable
    - The `update_dict` should be a dictionary if provided
    
    Postconditions:
    - When model exists: returns a copy of the default parameters or merged parameters
    - When model doesn't exist and update_dict provided: returns a new dictionary with merged parameters (empty if update_dict is empty)
    - When model doesn't exist and update_dict is None: returns None

## Side Effects:
    None - This function is pure and doesn't modify any external state.

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
    G --> I[return params]
    H --> I
    E -- No --> I
    I --> J[Return params]
```

## Examples:
    # Get default parameters for a model
    defaults = default_params("linear_regression")
    # Returns a copy of the default parameters for linear regression
    
    # Get default parameters and update them
    custom_params = default_params("neural_network", {"learning_rate": 0.01, "epochs": 100})
    # Returns merged parameters
    
    # Handle case where model doesn't exist but updates are provided
    params = default_params("nonexistent_model", {"custom_param": "value"})
    # Returns {'custom_param': 'value'}
    
    # No parameters for model and no updates
    result = default_params("unknown_model")
    # Returns None
```

