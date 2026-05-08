# `params.py`

## `hypertools._shared.params.default_params` · *function*

## Summary:
Return a shallow copy of a model's default-parameters mapping (if present) with optional updates applied; if no defaults exist and no updates are provided, return None.

## Description:
This small utility centralizes lookup and merging of a model-specific default-parameters object. It performs three responsibilities:
1. Look up the defaults for the provided model key in a module-global mapping named "parameters".
2. Make a shallow copy of the located defaults to prevent caller-side mutation of global defaults.
3. If an update value is provided (truthy), merge its entries into the copy (or into a new dict if no defaults were found) and return the merged result.

Known callers within the provided context:
- No direct callers are included in the provided file excerpt. In typical usages this function is invoked by higher-level factory, configuration, or plotting code that needs a concrete parameter mapping for a named model and may override specific default settings.

Why this is a separate function:
- Encapsulates consistent lookup/copy/merge semantics so callers remain concise and do not accidentally mutate shared defaults.
- Centralizes truthiness and merge policy (i.e., only merge when update_dict evaluates to truthy) so behavior is uniform across call sites.

## Args:
    model (hashable):
        - Key used to query the module-global "parameters" mapping.
        - Typical values: strings identifying model types (e.g., 'pca', 'tsne'), but any hashable object that is a key in parameters is accepted.
        - If model is unhashable and parameters expects hashable keys, a TypeError may be raised by the membership check.
    update_dict (optional, any truthy or falsy value; default None):
        - If truthy, used as the source to update the returned parameters object.
        - Accepted forms: any object accepted by the mapping.update(...) call on the copied defaults — commonly a mapping (dict-like), an iterable of (key, value) pairs, or keyword-style payloads (when appropriate).
        - Important: The function tests update_dict using Python truthiness (if update_dict:). An empty container (e.g., {}) is falsy and will NOT trigger merging; a non-empty container is truthy and will be merged.
        - The passed update_dict itself is not mutated by this function.

## Returns:
    A shallow-copied mapping-like object with updates applied, or None.
    - If the module-global parameters contains model:
        - The function returns the result of calling copy() on parameters[model], then (if update_dict is truthy) calling update(update_dict) on that copy.
        - Commonly this is a dict; implementers should assume the defaults' value supports copy() and update().
    - If parameters does not contain model:
        - If update_dict is falsy (None or an empty container), the function returns None.
        - If update_dict is truthy, the function returns a new dict populated by applying update_dict (i.e., behaves as params = {}; params.update(update_dict); return params).
    - The returned object is a newly created object distinct from the module-global defaults and distinct from the passed update_dict (no aliasing).

## Raises:
    NameError:
        - If the module-global name "parameters" is not defined in the module, evaluating "model in parameters" will raise NameError.
    TypeError:
        - If "parameters" exists but does not support membership checks, or if model is an unhashable type for the mapping, the membership check ("model in parameters") may raise TypeError.
        - If parameters[model].copy() returns an object whose update(...) method does not accept update_dict's type, or if update_dict is an inappropriate type for update(...), params.update(update_dict) may raise TypeError.
    AttributeError:
        - If parameters[model] does not provide a copy() method, calling copy() will raise AttributeError.
    ValueError:
        - Rare: if update_dict is an iterable but not of (key, value) pairs the mapping update may raise ValueError or TypeError depending on the update implementation.
    Note: The function itself does not intentionally raise custom exceptions; the above exceptions originate from operations on the module-global "parameters" or from the update protocol.

## Constraints:
    Preconditions:
        - The module-global "parameters" should be present and be a mapping-like object whose values are mapping-like with a copy() method and an update(...) method.
        - Callers should pass a model key appropriate for the keys used in parameters (typically hashable).
    Postconditions:
        - If defaults existed for model, the returned object is a shallow copy of those defaults and will reflect any applied updates.
        - If no defaults existed and update_dict was truthy, the returned object will be a plain dict populated with update_dict's entries.
        - If no defaults existed and update_dict was falsy, the function returns None.

## Side Effects:
    - No I/O, logging, or network activity.
    - Reads the module-global variable "parameters" but does not modify it.
    - Does not mutate the passed update_dict.
    - The returned object may be mutated by the caller without affecting module-global defaults.

## Control Flow:
    flowchart TD
        Start([start]) --> CheckParametersDefined{is "parameters" defined?}
        CheckParametersDefined -- no --> NameError([NameError raised during membership check])
        CheckParametersDefined -- yes --> CheckModel{model in parameters?}
        CheckModel -- yes --> CopyDefaults[/params = parameters[model].copy()/]
        CheckModel -- no --> NoDefaults[/params = None/]
        CopyDefaults --> CheckUpdate{is update_dict truthy?}
        NoDefaults --> CheckUpdate
        CheckUpdate -- no --> ReturnParams[/return params/]
        CheckUpdate -- yes & params None --> MakeEmpty[/params = {} (new dict)/]
        CheckUpdate -- yes & params not None --> UseCopy[/params is existing copy/]
        MakeEmpty --> UpdateParams[/params.update(update_dict)/]
        UseCopy --> UpdateParams
        UpdateParams --> ReturnParams
        ReturnParams --> End([end])

## Examples:
    - Defaults exist, no overrides:
        If parameters contains {'pca': {'n_components': 2}}, calling with model='pca' and update_dict=None returns a shallow copy equivalent to {'n_components': 2}.

    - Defaults exist, overrides provided:
        With parameters['pca'] as above, calling with update_dict={'n_components': 3, 'whiten': True} returns {'n_components': 3, 'whiten': True}.

    - No defaults, non-empty updates:
        If parameters has no key 'custom' and update_dict={'alpha': 0.1}, the function returns {'alpha': 0.1} (a new dict).

    - No defaults, empty update:
        If parameters has no key 'unknown' and update_dict is {} (empty dict), the function returns None because update_dict is falsy.

Implementation notes for reimplementation:
    - Use a membership test against a module-global mapping called parameters.
    - Call copy() on the located defaults to obtain a shallow copy; do not mutate the original mapping.
    - Test update_dict for truthiness (if update_dict:) before applying updates.
    - When defaults are missing and update_dict is truthy, initialize params as an empty dict and call update(update_dict) to populate it.
    - Do not assume update_dict is a dict; accept any type supported by mapping.update(...) and handle possible exceptions as described above.

