# `text2mat.py`

## `hypertools.tools.text2mat.text2mat` · *function*

*No documentation generated.*

## `hypertools.tools.text2mat._transform` · *function*

## Summary:
Convert a sequence of grouped inputs into numeric arrays by optionally applying a vectorizer and/or a transformer, then split the transformed results to preserve the original group boundaries.

## Description:
This helper flattens an iterable of groups, applies an optional vectorizer (vmodel) and an optional transformer/topic-model (tmodel) in sequence, and splits the resulting matrix back into a list of group-wise arrays whose group sizes match the input.

Known callers and pipeline stage:
- Used in text-to-matrix conversion pipelines that need to convert grouped documents into numeric representations for visualization or downstream modeling.
- Typical stage: after loading or fitting vectorizer/topic models and before per-group aggregation or plotting.

Why this logic is isolated:
- Centralizes the input-shaping logic required to: compute group boundaries, flatten/stack inputs for model.transform calls, convert sparse results to dense arrays when necessary, and re-split outputs into original groups. This prevents repeated shape-manipulation code across higher-level functions.

## Args:
    vmodel (object or None)
        - If not None, expected to implement transform(iterable) and return a matrix-like result that supports toarray() (e.g., the sparse matrix returned by sklearn CountVectorizer/TfidfVectorizer).
        - When provided, it is applied first to the flattened list of all items across groups: vmodel.transform(np.vstack(x).ravel()).toarray()
        - If None, no vectorizer step is performed.

    tmodel (object or None)
        - If not None, expected to implement transform(...).
        - If tmodel is an instance of sklearn.pipeline.Pipeline, this function will call tmodel.transform on np.vstack(x).ravel() (a 1-D array of flattened items).
        - Otherwise, tmodel.transform is called on the 2-D stacked array np.vstack(x) (document-term matrix or stacked arrays).
        - Typical tmodel types include sklearn.decomposition.LatentDirichletAllocation, sklearn.decomposition.NMF, or other sklearn-style transformers.

    x (iterable of iterables)
        - A sequence (list/tuple) of groups. Each group xi must:
            * support len(xi) (used to compute group boundaries),
            * contain elements that together can be stacked by numpy.vstack (i.e., each element should be an array-like with compatible shapes, or scalar/string if vectorizers expect string inputs).
        - Examples:
            * [['doc1','doc2'], ['doc3']] (groups of raw document strings)
            * [array_rows_group1, array_rows_group2] (groups of numeric rows)

Interdependencies and important notes:
- Order: vmodel, if provided, is always applied before tmodel.
- If vmodel is provided and tmodel is not a Pipeline, the dense array returned by vmodel.toarray() is passed to tmodel.transform.
- If both vmodel is provided and tmodel is a Pipeline, the function will still call the Pipeline branch (passing the ravelled stacked array). This combination may be incorrect for typical Pipelines expecting strings — avoid passing both in incompatible combinations.

## Returns:
    list[array-like]
        - A list with length equal to len(x). Each element is the slice of the transformed output corresponding to the original group.
        - Element types:
            * If transformations produce numpy.ndarray outputs, elements will be numpy.ndarray.
            * If transform returns other array-like objects (e.g., scipy sparse matrices before toarray, or custom array-like results), the returned elements will be array-like of whatever type was produced after any toarray() call (the function explicitly calls toarray() only after vmodel.transform).
        - Special cases:
            * If vmodel and tmodel are both None, the function returns list(x) — a shallow copy of the input groups.
            * If x is empty (len(x) == 0) and either vmodel or tmodel is provided, a ValueError is raised by numpy.vstack when attempting to stack zero arrays. If both models are None, the function returns an empty list.

## Raises:
    - ValueError:
        * From numpy.vstack(...) if x is empty or group elements cannot be stacked (e.g., incompatible shapes).
        * From numpy.vsplit(...) if the array to split is not at least 2-D or if split indices are invalid.
    - AttributeError:
        * If provided models do not implement expected methods (transform, toarray).
    - Any exception raised by the underlying model methods (propagated), including:
        * sklearn.exceptions.NotFittedError if a scikit-learn model is not fitted when transform is called.
        * Other errors from tmodel.transform or vmodel.transform depending on implementations.

## Constraints:
Preconditions:
    - len(xi) must be valid for each group xi in x.
    - Each group must contain at least one element when a model (vmodel or tmodel) will be called (otherwise np.vstack will raise).
    - Elements across groups must be stackable by numpy.vstack (compatible shapes and types), unless only vmodel is None and tmodel Pipeline expects 1-D iterables of raw items.
    - vmodel.transform(...) must return an object with toarray() when vmodel is supplied.

Postconditions:
    - Returned list length equals len(x).
    - The ordering and group boundaries of x are preserved in the returned list.
    - No global variables are modified by this function.

## Side Effects:
    - The function itself performs no I/O or global state changes.
    - It calls methods on provided model objects; any side effects from those methods (logging, internal caching) may occur.

## Control Flow:
flowchart TD
    Start([Start: receive vmodel, tmodel, x])
    Start --> Split[Compute split = np.cumsum([len(xi) for xi in x])[:-1]]
    Split --> CheckV{vmodel is not None?}
    CheckV -- Yes --> VStackV[Call np.vstack(x).ravel() -> vmodel.transform(...).toarray()]
    VStackV --> VSPLITV[Split dense array with np.vsplit(..., split) -> x = pieces]
    CheckV -- No --> SkipV[No vmodel, keep x as provided]
    VSPLITV --> CheckT
    SkipV --> CheckT[Check tmodel is not None?]
    CheckT -- No --> Return[Return list(x)]
    CheckT -- Yes --> IsPipe{tmodel is Pipeline?}
    IsPipe -- Yes --> VStackPipe[Call np.vstack(x).ravel() -> tmodel.transform(...)]
    IsPipe -- No --> VStackT[Call np.vstack(x) -> tmodel.transform(...)]
    VStackPipe --> VSPLITT[Split tmodel output with np.vsplit(..., split) -> x = pieces]
    VStackT --> VSPLITT
    VSPLITT --> Return

## Examples:
1) No models (pass-through)
    - x = [['a','b'], ['c']]
    - _transform(None, None, x) -> [['a','b'], ['c']]

2) Vectorizer only
    - Given fitted CountVectorizer vmodel that accepts strings:
      result = _transform(vmodel, None, [['doc1','doc2'], ['doc3']])
    - Behavior: all docs flattened, vectorized, converted to dense array, and split into two arrays corresponding to the two groups.

3) Topic model (non-Pipeline) after vectorizer
    - Given vmodel and an NMF tmodel that expects numeric matrices:
      result = _transform(vmodel, tmodel, groups)
    - Behavior: vmodel produces dense document-term matrix, NMF.transform is applied to the stacked matrix, and the resulting matrix is split into group-wise arrays.

4) Pipeline tmodel that expects raw strings
    - Given a Pipeline tmodel that includes a vectorizer internally:
      result = _transform(None, pipeline_tmodel, [['a','b'], ['c']])
    - Behavior: the pipeline receives the flattened list of strings (np.vstack(...).ravel()) and its transform output is split.

Error handling example:
    - To catch common issues, validate models before calling or wrap the call:
      try:
          out = _transform(vmodel, tmodel, groups)
      except sklearn.exceptions.NotFittedError:
          # handle model not fitted
      except ValueError:
          # handle empty or non-stackable groups

## `hypertools.tools.text2mat._fit_models` · *function*

## Summary:
Fits the provided vectorizer and/or topic/decomposition model in-place on stacked raw text documents when they are not already fitted; does nothing if an explicit fitted flag indicates models are ready.

## Description:
This helper centralizes the logic to ensure text-processing models are fitted before downstream use. It:
- Checks whether the vectorizer (vmodel) exposes 'vocabulary_' and whether the transformer/topic model (tmodel) exposes 'components_' using scikit-learn's check_is_fitted.
- Calls .fit(...) on models that are not fitted.
- Handles the special case where tmodel is a sklearn.pipeline.Pipeline by fitting it directly on raw documents; otherwise, it fits tmodel on the vectorized output produced by vmodel.transform(...).

Known callers within the provided context:
- No direct callers were found in the supplied snippet. In practice this function is typically invoked by higher-level functions in the text2mat pipeline that prepare and train the components that convert text to matrices or topic representations (e.g., the routine that constructs vectorizers and decomposition models and orchestrates their training).

Responsibility boundary:
- Responsibility: ensure vmodel and tmodel are fitted if required.
- Not responsible for: validating semantic content of x beyond numpy.vstack compatibility; handling exceptions from .fit/.transform beyond letting them propagate.

## Args:
    vmodel (object or None):
        - Expected capabilities: .fit(raw_docs), .transform(raw_docs) and, when fitted, attribute 'vocabulary_'.
        - Typical concrete types: sklearn.feature_extraction.text.CountVectorizer, TfidfVectorizer, or any object that follows scikit-learn's fitted-attribute convention.
        - If None, no vectorizer fitting/transform is performed. If tmodel is not a Pipeline, vmodel must be non-None (see Constraints).

    tmodel (object or None):
        - Expected capabilities: .fit(...) and, when fitted, attribute 'components_'.
        - If tmodel is an instance of sklearn.pipeline.Pipeline, it will be fit on raw documents directly.
        - If tmodel is not a Pipeline, it is assumed to accept vectorized input produced by vmodel.transform(...).
        - Typical concrete types: sklearn.decomposition.LatentDirichletAllocation, sklearn.decomposition.NMF, or a Pipeline wrapping a vectorizer and estimator.

    x (iterable):
        - Iterable of array-like document collections such that numpy.vstack(x).ravel() produces a 1-D sequence of raw documents (strings).
        - Examples: [np.array(["doc1", "doc2"]), np.array(["doc3"])] or a list of lists of strings.
        - The function does not perform deep validation; invalid shapes/types will raise exceptions from numpy or the downstream model code.

    model_is_fit (bool or comparable):
        - If equal to True (using equality ==), the function returns immediately without checking or fitting models.
        - NOTE: the function uses model_is_fit == True rather than a truthiness test. Only values that compare equal to True (e.g., True, 1) will trigger the early return; arbitrary truthy objects (e.g., non-empty lists) will not unless they compare equal to True.

Interdependencies:
    - If tmodel is not a Pipeline and is provided, vmodel must be provided (non-None) because the non-Pipeline fitting branch calls vmodel.transform(...).

## Returns:
    None

    - The function mutates vmodel and/or tmodel in-place by calling their .fit(...) methods if they were not already fitted. After a successful return, models that required fitting should be in a fitted state.

## Raises:
    - NotFittedError:
        - This exception is caught internally when checking fitted status via check_is_fitted; it will not propagate as-is.
    - NameError:
        - If the module does not define the name np (the function calls np.vstack), a NameError will be raised. Ensure the module imports numpy as np (for example: import numpy as np) before calling this function.
    - AttributeError:
        - If tmodel is not a Pipeline but vmodel is None, the code attempts to call vmodel.transform(...) and will raise AttributeError (or a similar error) because vmodel is None.
    - Any exceptions thrown by numpy.vstack, vmodel.fit, vmodel.transform, or tmodel.fit:
        - These can include ValueError, TypeError, or sklearn-specific errors; they are not caught by this function and will propagate to the caller.

## Constraints:
Preconditions:
    - The name np must be defined in the module namespace (i.e., numpy must be imported as np). Otherwise a NameError will occur.
    - x must be such that np.vstack(x).ravel() yields a 1-D sequence of documents acceptable to the vectorizer or tmodel.
    - If tmodel is not a Pipeline, vmodel must be provided and implement .transform(...).
    - model_is_fit should be a boolean-like value; the code uses equality comparison to True (== True).

Postconditions:
    - On normal successful return:
        - Any provided vmodel that was not already fitted has been fitted by calling vmodel.fit(np.vstack(x).ravel()).
        - Any provided tmodel that was not already fitted has been fitted:
            - If tmodel is a Pipeline: tmodel.fit(np.vstack(x).ravel()) was called.
            - Otherwise: tmodel.fit(vmodel.transform(np.vstack(x).ravel())) was called.
        - Models are altered in-place to their fitted state (and should expose related fitted attributes).

## Side Effects:
    - Mutates the provided models via in-place .fit(...) calls.
    - No file, network, or stdout I/O is performed by this function.
    - Relies on numpy (via np) and scikit-learn utilities; errors from those libraries may propagate.

## Control Flow:
flowchart TD
    A[Start] --> B{model_is_fit == True?}
    B -- Yes --> C[Return immediately]
    B -- No --> D{vmodel is not None?}
    D -- Yes --> E[check_is_fitted(vmodel, ['vocabulary_'])]
    E -- Fitted --> G[skip vmodel.fit]
    E -- NotFittedError --> H[vmodel.fit(np.vstack(x).ravel())]
    D -- No --> G
    G --> I{tmodel is not None?}
    I -- No --> J[Return]
    I -- Yes --> K[check_is_fitted(tmodel, ['components_'])]
    K -- Fitted --> J
    K -- NotFittedError --> L{isinstance(tmodel, Pipeline)?}
    L -- Yes --> M[tmodel.fit(np.vstack(x).ravel())]
    L -- No --> N[tmodel.fit(vmodel.transform(np.vstack(x).ravel()))]
    M --> J
    N --> J
    J --> O[End]

## Examples:
1) Typical usage with a CountVectorizer and LDA:
    - Ensure numpy is imported as np in the module:
        import numpy as np
    - Prepare models and documents:
        vmodel = CountVectorizer()
        tmodel = LatentDirichletAllocation(n_components=10)
        x = [np.array(["doc one", "doc two"]), np.array(["doc three"])]
    - Fit models if needed:
        _fit_models(vmodel, tmodel, x, model_is_fit=False)
    - After returning, vmodel and tmodel are fitted.

2) Using a Pipeline that wraps vectorization:
    - import numpy as np
    - vmodel = None
    - tmodel = Pipeline([('vect', CountVectorizer()), ('lda', LatentDirichletAllocation(n_components=5))])
    - x = [np.array(["a", "b"]), np.array(["c"])]
    - _fit_models(vmodel, tmodel, x, model_is_fit=False)
    - The Pipeline will be fitted directly on raw documents.

3) Avoiding common errors:
    - Do not call with vmodel=None and tmodel a non-Pipeline estimator (e.g., LatentDirichletAllocation()) because the function will attempt vmodel.transform(...) and raise AttributeError.
    - Ensure numpy is available under the name np; otherwise a NameError will occur.

Notes:
    - The function relies on scikit-learn conventions that fitted vectorizers expose 'vocabulary_' and that many decomposition/estimator objects expose 'components_' once fitted.
    - Because the function uses model_is_fit == True, callers should pass a boolean True to skip work; passing truthy but not equal-to-True values will not skip fitting.

## `hypertools.tools.text2mat._check_mtype` · *function*

## Summary:
Determine a short textual tag describing the "type" of the argument (one of 'str', 'dict', 'class', 'None', or 'class_instance'), used to classify model/input types for downstream logic.

## Description:
This helper inspects a single value and returns a small string label representing its meta-type. It is typically used when the code must branch behavior depending on whether a parameter is given as a string identifier, a parameter dictionary, a class object, a class instance, or left explicitely as None. No external I/O or side effects occur.

Known callers within the codebase:
- No direct call-sites were discovered in the provided scan for this repository file. Typical callers (in the context of this module, hypertools.tools.text2mat) would be functions that accept a model/configuration parameter and need to normalize handling based on whether the user supplied a model name (string), a dict of parameters, a class object, an instantiated object, or None.

Why this is extracted into a separate function:
- Centralizes and documents the mapping from Python runtime types to a small set of canonical meta-type labels used across the module.
- Keeps branching logic localized so callers can make concise decisions (switch/case-like) based on a single returned tag rather than repeating isinstance/inspect checks.
- Helps unit test the classification behavior independently of the larger processing pipeline.

## Args:
    x (Any): The value to classify. Can be:
        - a string (e.g., a model name or identifier),
        - a dict (configuration / parameters),
        - a class object (e.g., SomeModelClass),
        - an instance of a class (e.g., SomeModelClass()),
        - None.
    No other constraints on x are required by callers; the function will attempt to classify arbitrary objects.

## Returns:
    str or None:
        - 'str'           — if x is an instance of str
        - 'dict'          — if x is an instance of dict
        - 'class'         — if x is a class object (inspect.isclass(x) is True)
        - 'None'          — if x is None (tested via isinstance(x, type(None)))
        - 'class_instance'— if x is an instance of a class (determined by inspect.isclass(type(x)) being True)
        - None            — implicitly returned if none of the above branches return a value (this is unlikely for normal Python objects because type(x) is normally a class and thus inspect.isclass(type(x)) is True). Callers should not rely on receiving None unless they explicitly handle it.

    Notes:
    - The function returns small, canonical string labels intended for programmatic branching; it does not raise for ordinary objects aside from the exceptional path described below.

## Raises:
    TypeError:
        - Raised only if an exception occurs while testing inspect.isclass(type(x)) in the final branch. The exact raised message is:
          'Parameter must of type string, dict, class, or class instance.'
        - This is an exceptional/unexpected path and would occur only if calling type(x) or inspect.isclass(...) themselves raise an exception for the supplied x (very rare).

## Constraints:
    Preconditions:
        - The caller must provide a value for x (can be None). There is no requirement for x to implement any particular interface.
        - The runtime must provide the standard inspect.type/type behavior; this implementation assumes type(x) will return a Python type object for normal objects.

    Postconditions:
        - On successful return, one of the documented string labels will be returned for normal Python objects.
        - If an internal error occurs while determining the class of x, a TypeError is raised with the documented message.
        - No mutation of x or other program state occurs.

## Side Effects:
    - None. No I/O, no mutation of global state, no external service calls.

## Control Flow:
flowchart TD
    Start([start])
    CheckStr{isinstance(x, str)?}
    CheckDict{isinstance(x, dict)?}
    CheckClassObj{inspect.isclass(x)?}
    CheckNone{isinstance(x, type(None))?}
    TryIsClassType[/try: inspect.isclass(type(x))/]
    ReturnStr[/"return 'str'"/]
    ReturnDict[/"return 'dict'"/]
    ReturnClass[/"return 'class'"/]
    ReturnNone[/"return 'None'"/]
    ReturnClassInst[/"return 'class_instance'"/]
    RaiseErr[/raise TypeError('Parameter must of type string, dict, class, or class instance.')/]
    End([end])

    Start --> CheckStr
    CheckStr -- yes --> ReturnStr --> End
    CheckStr -- no --> CheckDict
    CheckDict -- yes --> ReturnDict --> End
    CheckDict -- no --> CheckClassObj
    CheckClassObj -- yes --> ReturnClass --> End
    CheckClassObj -- no --> CheckNone
    CheckNone -- yes --> ReturnNone --> End
    CheckNone -- no --> TryIsClassType
    TryIsClassType -- inspect.isclass(type(x)) is True --> ReturnClassInst --> End
    TryIsClassType -- inspect.isclass(type(x)) is False --> End
    TryIsClassType -- exception --> RaiseErr --> End

## Examples:
    Example 1 — common cases
    - Input: "lda" (a model name string)
      Output: 'str'

    - Input: {'n_components': 10} (a config dict)
      Output: 'dict'

    - Input: SomeModelClass (a class object)
      Output: 'class'

    - Input: SomeModelClass() (an instance of a class)
      Output: 'class_instance'

    - Input: None
      Output: 'None'

    Example 2 — defensive usage pattern in caller
    - Callers that dispatch based on the returned tag should include an explicit fallback to handle the (very unlikely) None return and also be prepared to catch TypeError:
        - tag = _check_mtype(x)
        - if tag == 'str': ...  # treat x as identifier
        - elif tag == 'dict': ...  # treat x as parameters
        - elif tag == 'class': ...  # instantiate or register the class
        - elif tag == 'class_instance': ...  # use instance directly
        - elif tag == 'None': ...  # apply default behavior
        - else: raise ValueError("Unrecognized model type tag: %s" % repr(tag))

