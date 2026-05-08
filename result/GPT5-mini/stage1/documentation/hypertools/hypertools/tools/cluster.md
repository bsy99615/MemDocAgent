# `cluster.py`

## `hypertools.tools.cluster.cluster` · *function*

## Summary:
Clusters stacked observations with a chosen clustering model (by name or specification) and returns a Python list of cluster labels for each stacked row.

## Description:
This function prepares input observations (optionally via a formatter), selects and constructs a clustering model from a mapping of supported models, fits the model to the vertically stacked data, and returns the model's labels as a list.

Known callers within the codebase:
    - None were provided in the supplied context. Typical use is within a data processing or visualization pipeline immediately before downstream steps that require cluster membership (for example, color-coding points in a plot).

Responsibility boundary:
    - Encapsulates data-formatting (if requested), model selection/instantiation, model fitting on the stacked data, and extraction of labels.
    - Delegates actual clustering behavior to external model classes (e.g., scikit-learn estimators or HDBSCAN).

## Args:
    x (sequence of array-like):
        Sequence (e.g., list or tuple) of array-like objects representing observations. The function stacks them with numpy.vstack (via np.vstack in the implementation). Each element must have the same number of columns/features so that np.vstack(x) produces a 2-D array shaped (n_rows, n_features).
        Notes:
            - If elements have mismatched column counts, numpy.vstack will raise a ValueError.
            - If x is already a single 2-D array inside a sequence (e.g., [arr]), it will be stacked into arr unchanged.

    cluster (str or dict or None, default 'KMeans'):
        - None: clustering is skipped and the original x is returned unchanged.
        - str: a lookup key into a global models mapping (e.g., 'KMeans', 'HDBSCAN'). When a string is provided, the function will set model_params automatically:
            * If cluster == 'HDBSCAN': model_params = {} (no n_clusters param supplied)
            * Otherwise: model_params = {'n_clusters': n_clusters}
        - dict: expected shape {'model': <str>, 'params': <dict>}
            * 'model' must be a string key present in models
            * 'params' must be a dict of keyword args passed directly to the model constructor
        Edge cases:
            - If the dict is missing keys or 'model' is not a string, the function may raise KeyError or later raise UnboundLocalError because local variables model/model_params would not be set.

    n_clusters (int, default 3):
        Applied only when cluster is a string and the chosen model is not 'HDBSCAN'. Ignored when cluster is a dict (because dict.params are used instead).

    ndims (any, default None):
        Deprecated. If not None, a warnings.warn is emitted and the value is ignored. No dimensionality reduction is performed by this function.

    format_data (bool, default True):
        If True, the function calls a global formatter callable with ppca=True to transform x before stacking. If False, x is used as provided.

## Returns:
    list or original x:
        - If cluster is None: returns x unchanged (the original sequence passed in).
        - Otherwise: returns list(model.labels_) — a Python list of labels with one entry per row in np.vstack(x).
        - For models that indicate noise with a special label (e.g., HDBSCAN uses -1), those special labels are returned unchanged.
        - If model.fit does not produce labels_ or the length of labels_ does not match the stacked rows, the returned list may be inconsistent; callers should rely on model implementations to guarantee label length matches input rows.

## Raises:
    ImportError:
        - Raised with exact message 'HDBSCAN is not installed. Please install hdbscan>=0.8.11' when:
            * cluster == 'HDBSCAN' (string) OR cluster is a dict with cluster['model'] == 'HDBSCAN'
            AND the global boolean flag _has_hdbscan is False (or not truthy).
    KeyError:
        - If cluster is a string not present in the global models mapping, accessing models[cluster] will raise KeyError.
        - If cluster is a dict missing keys 'model' or 'params', accessing cluster['model'] or cluster['params'] will raise KeyError.
    UnboundLocalError:
        - If cluster is a dict but cluster['model'] is not a string (the code checks isinstance(cluster['model'], str) and only then sets model/model_params), the later reference to model will raise UnboundLocalError because model was never assigned.
    NameError:
        - The implementation calls np.vstack(...) (alias name np). If the module-level alias np is not defined (for example only 'import numpy' is present instead of 'import numpy as np'), a NameError will be raised at runtime.
        - If the global formatter or models symbols are not defined in the module, NameError will occur when they are referenced.
    ValueError / TypeError (from underlying libraries):
        - model.fit(...) or numpy.vstack(...) may raise ValueError/TypeError for invalid shapes or parameters; these exceptions propagate from the underlying libraries.

## Constraints:
    Preconditions:
        - A global mapping named models must exist and map string names to clustering classes (callables that accept **kwargs and return instances exposing fit(...) and labels_).
        - A callable formatter must exist in the module scope when format_data is True; it must accept (x, ppca=True) and return a sequence compatible with np.vstack.
        - A global boolean _has_hdbscan must exist and accurately reflect HDBSCAN availability if 'HDBSCAN' is requested.
        - The name np must be defined in module scope as an alias that provides vstack (commonly numpy aliased to np). If not, NameError occurs.
        - The model classes used must set a labels_ attribute after fit(...) (this is standard for scikit-learn-like clusterers and HDBSCAN).

    Postconditions:
        - If cluster is None: the function returns the original x unchanged.
        - Otherwise: a model instance has been instantiated and its fit() has been invoked on the stacked input; the result returned is list(model.labels_), matching the number of stacked rows assuming the model behaves correctly.

## Side Effects:
    - Emits a warnings.warn if ndims is not None.
    - May raise ImportError if HDBSCAN is requested and _has_hdbscan is False.
    - Calls external model.fit(...) which can consume CPU/memory and run arbitrary clustering code; no file, network I/O, database, or global state is modified by this function itself.
    - Depends on module-level globals (models, formatter, _has_hdbscan, np); missing or incorrect globals lead to NameError or other exceptions.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckNone{cluster is None?}
    CheckNone -- Yes --> ReturnX[Return original x]
    CheckNone -- No --> CheckHDB{cluster == 'HDBSCAN' or dict with model 'HDBSCAN'?}
    CheckHDB -- Yes --> HasHDB{_has_hdbscan True?}
    HasHDB -- No --> RaiseImp[Raise ImportError: HDBSCAN not installed]
    HasHDB -- Yes --> Continue[Proceed]
    CheckHDB -- No --> Continue
    Continue --> CheckNdims{ndims is not None?}
    CheckNdims -- Yes --> WarnNdims[Emit warnings.warn about deprecation]
    CheckNdims -- No --> SkipWarn
    WarnNdims --> CheckFormat
    SkipWarn --> CheckFormat
    CheckFormat{format_data True?} -- Yes --> CallFormatter[Call formatter(x, ppca=True) -> x_formatted]
    CheckFormat -- No --> UseX[Use provided x]
    CallFormatter --> SelectModel
    UseX --> SelectModel
    SelectModel{cluster is str or dict?}
    SelectModel -- str --> LookupModel[model = models[cluster]; set model_params depending on 'HDBSCAN' vs others]
    SelectModel -- dict --> DictModel{isinstance(cluster['model'], str)?}
    DictModel -- True --> LookupDictModel[model = models[cluster['model']]; model_params = cluster['params']]
    DictModel -- False --> UnsetModel[model left unset -> later UnboundLocalError]
    LookupModel --> Instantiate[model = model(**model_params)]
    LookupDictModel --> Instantiate
    UnsetModel --> Instantiate
    Instantiate --> Fit[model.fit(np.vstack(x))]
    Fit --> ReturnLabels[Return list(model.labels_)]

## Examples (usage patterns, not runnable code blocks):
Example A — Standard named model (conceptual):
    1. Ensure module globals exist: models contains 'KMeans' mapped to a clustering class, formatter exists, np is defined.
    2. Call function with cluster='KMeans' and default n_clusters=3.
    3. The function optionally formats x via formatter, stacks rows, instantiates KMeans(n_clusters=3), fits, and returns a list of integer labels.

Example B — Custom model params via dict:
    1. Provide cluster={'model': 'AgglomerativeClustering', 'params': {'n_clusters': 4, 'linkage': 'ward'}}.
    2. The function looks up 'AgglomerativeClustering' in models, instantiates it with the provided params, fits on stacked data, and returns labels.
    3. Note: the top-level n_clusters argument is ignored in this mode.

Example C — Error scenarios to handle:
    - If you pass cluster={'model': None, 'params': {...}} the function will not set model (it only sets model when cluster['model'] is a str) and later will raise UnboundLocalError. Validate cluster dict before calling.
    - If you request 'HDBSCAN' but _has_hdbscan is False, catch ImportError with the exact message 'HDBSCAN is not installed. Please install hdbscan>=0.8.11'.
    - If np is not defined as an alias for numpy in the module, the call to np.vstack will raise NameError; ensure the module defines np or change to use numpy.vstack.

Implementation notes for reimplementers:
    - Ensure to import numpy as np (or adjust code to use the same name used here) to avoid NameError.
    - Validate the cluster dict shape before use to avoid UnboundLocalError: require 'model' to be str and 'params' to be dict.
    - Provide a models mapping where each value is a class with a constructor accepting kwargs and an instance method fit(X) that results in an attribute labels_ containing one label per row in X.
    - When constructing the model from a string, pass {'n_clusters': n_clusters} for non-HDBSCAN models; for HDBSCAN pass no n_clusters unless specified in dict params.

