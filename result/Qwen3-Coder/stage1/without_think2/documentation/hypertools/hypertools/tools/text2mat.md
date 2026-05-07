# `text2mat.py`

## `hypertools.tools.text2mat.text2mat` · *function*

## Summary:
Converts text data into numerical matrices using configurable vectorization and semantic modeling techniques.

## Description:
The `text2mat` function transforms textual data into numerical representations suitable for machine learning analysis. It supports various combinations of text vectorization methods (like CountVectorizer or TfidfVectorizer) and semantic modeling approaches (such as LatentDirichletAllocation or NMF). The function can utilize pre-trained models from example datasets or build models from scratch based on provided parameters. It handles both single texts and collections of texts, applying appropriate transformations and maintaining data structure integrity.

## Args:
    data (list[str] or str): Input text data to be converted. Can be a single string or a list of strings representing one or more text documents.
    vectorizer (str, dict, class, or None): Text vectorization method to use. Can be a string name, dictionary with 'model' and 'params' keys, or a class instance with fit_transform method. Defaults to 'CountVectorizer'.
    semantic (str, dict, class, or None): Semantic modeling method to use. Can be a string name, dictionary with 'model' and 'params' keys, or a class instance with fit_transform method. Defaults to 'LatentDirichletAllocation'.
    corpus (str or None): Name of pre-defined corpus to use for training models. Supported values are 'wiki', 'nips', 'sotus'. If None, uses the input data directly. Defaults to 'wiki'.

## Returns:
    list[numpy.ndarray]: List of numerical matrices corresponding to the input text data. Each matrix represents the transformed version of a text sequence according to the specified vectorization and semantic models.

## Raises:
    RuntimeError: Raised when a user-provided vectorizer or semantic model doesn't have the required fit_transform method following the scikit-learn API.

## Constraints:
    Preconditions:
        - The `data` parameter must be either a string or a list of strings.
        - If `vectorizer` or `semantic` are provided as class instances, they must have a `fit_transform` method.
        - The `corpus` parameter must be one of 'wiki', 'nips', 'sotus', or None.
        - The `vectorizer` and `semantic` parameters must be valid model identifiers or compatible objects.
    Postconditions:
        - The returned list contains numerical matrices with shapes matching the input text sequences.
        - The function preserves the structure of input data (single text vs. list of texts).

## Side Effects:
    - May perform I/O operations when loading pre-trained models from example datasets.
    - Modifies the state of vectorization and semantic models in-place during fitting operations.
    - May load and cache example datasets if they are not already available.

## Control Flow:
```mermaid
flowchart TD
    A[Start text2mat] --> B{semantic is None?}
    B -- Yes --> C[Set semantic = 'LatentDirichletAllocation']
    B -- No --> D[Continue]
    C --> D
    D --> E{vectorizer is None?}
    E -- Yes --> F[Set vectorizer = 'CountVectorizer']
    E -- No --> G[Continue]
    F --> G
    G --> H{corpus is not None?}
    H -- Yes --> I{corpus in ('wiki', 'nips', 'sotus')?}
    I -- Yes --> J{semantic == 'LatentDirichletAllocation' AND vectorizer == 'CountVectorizer'?}
    J -- Yes --> K[Load pre-trained model]
    J -- No --> L[Load corpus data]
    K --> M[Set model_is_fit = True]
    L --> M
    I -- No --> N[Set corpus = [corpus]]
    N --> M
    H -- No --> O[Set corpus = None]
    O --> M
    M --> P[vtype = _check_mtype(vectorizer)]
    P --> Q{vtype == 'str'?}
    Q -- Yes --> R[Get vectorizer_params from default_params]
    Q -- No --> S{vtype == 'dict'?}
    S -- Yes --> T[Extract vectorizer_params from dict]
    T --> U[Update vectorizer]
    S -- No --> V{vtype in ('class', 'class_instance')?}
    V -- Yes --> W[Validate fit_transform method]
    W --> X[Update vectorizer_models]
    V -- No --> Y[Raise TypeError]
    R --> Z
    U --> Z
    Z --> AA[ttype = _check_mtype(semantic)]
    AA --> AB{ttype == 'str'?}
    AB -- Yes --> AC[Get text_params from default_params]
    AB -- No --> AD{ttype == 'dict'?}
    AD -- Yes --> AE[Extract text_params from dict]
    AE --> AF[Update semantic]
    AD -- No --> AG{ttype in ('class', 'class_instance')?}
    AG -- Yes --> AH[Validate fit_transform method]
    AH --> AI[Update texts]
    AG -- No --> AJ[Raise TypeError]
    AC --> AK
    AF --> AK
    AK --> AL[Build vmodel based on vtype]
    AL --> AM[Build tmodel based on ttype]
    AM --> AN{data is not list?}
    AN -- Yes --> AO[Wrap data in list]
    AO --> AP
    AN -- No --> AP[Continue]
    AP --> AQ{corpus is None?}
    AQ -- Yes --> AR[_fit_models with data]
    AQ -- No --> AS[_fit_models with corpus]
    AR --> AT
    AS --> AT
    AT --> AU[_transform with vmodel, tmodel, data]
    AU --> AV[Return result]
```

## Examples:
    # Basic usage with default parameters
    result = text2mat(["hello world", "foo bar"])
    
    # Using specific vectorizer and semantic models
    result = text2mat(["hello world", "foo bar"], 
                      vectorizer="TfidfVectorizer",
                      semantic="NMF")
    
    # Using pre-trained model from corpus
    result = text2mat(["hello world", "foo bar"], corpus="wiki")
    
    # Using custom model classes
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    vectorizer = CountVectorizer()
    semantic = LatentDirichletAllocation(n_components=5)
    result = text2mat(["hello world", "foo bar"], 
                      vectorizer=vectorizer,
                      semantic=semantic)

## `hypertools.tools.text2mat._transform` · *function*

## Summary:
Transforms text data using vectorization and/or topic modeling models, preserving original data structure.

## Description:
This function applies preprocessing and transformation operations to text data using either a vectorizer model (vmodel) or a topic model (tmodel). It handles the splitting and reconstruction of transformed data to maintain the original structure of input sequences. The function is designed to work with text data that may consist of multiple sequences, ensuring that transformations are applied consistently while preserving sequence boundaries.

## Args:
    vmodel (sklearn.base.BaseEstimator or None): Vectorizer model (e.g., CountVectorizer, TfidfVectorizer) to apply to the text data. If None, no vectorization is performed.
    tmodel (sklearn.base.BaseEstimator, sklearn.pipeline.Pipeline, or None): Topic model (e.g., LatentDirichletAllocation, NMF) or pipeline to apply to the text data. If None, no topic modeling is performed.
    x (list[list[str]]): List of text sequences, where each sequence is a list of strings (words or tokens).

## Returns:
    list[numpy.ndarray]: Transformed text data, where each element corresponds to a sequence from the input x and maintains the shape of the original sequence after transformation.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    - Precondition: Input x must be a list of lists containing strings.
    - Precondition: vmodel and tmodel must be compatible with scikit-learn's transform interface if not None.
    - Postcondition: Output list contains arrays with shapes matching the input sequence lengths.

## Side Effects:
    - None

## Control Flow:
```mermaid
flowchart TD
    A[Start _transform] --> B{vmodel is not None?}
    B -- Yes --> C[vmodel.transform()]
    B -- No --> D[Skip vectorization]
    C --> E[Convert to array]
    E --> F[Split using split indices]
    D --> F
    F --> G{tmodel is not None?}
    G -- Yes --> H[tmodel.transform()]
    G -- No --> I[Return result]
    H --> J[Check if Pipeline]
    J -- Yes --> K[Transform with ravel()]
    J -- No --> L[Transform directly]
    K --> M[Split using split indices]
    L --> M
    M --> I
    I --> N[Return transformed sequences]
```

## Examples:
    # Example 1: Using only vectorizer model
    vmodel = TfidfVectorizer()
    x = [['hello', 'world'], ['foo', 'bar']]
    result = _transform(vmodel, None, x)
    
    # Example 2: Using only topic model
    tmodel = LatentDirichletAllocation(n_components=2)
    x = [['hello', 'world'], ['foo', 'bar']]
    result = _transform(None, tmodel, x)
    
    # Example 3: Using both models
    vmodel = TfidfVectorizer()
    tmodel = LatentDirichletAllocation(n_components=2)
    x = [['hello', 'world'], ['foo', 'bar']]
    result = _transform(vmodel, tmodel, x)
```

## `hypertools.tools.text2mat._fit_models` · *function*

## Summary:
Initializes and fits text vectorization and topic modeling models if they haven't been previously fitted.

## Description:
This function serves as a utility for managing the fitting process of text processing models. It ensures that vectorization and topic modeling components are properly initialized and trained on input text data only when necessary, preventing redundant operations. The function is designed to work with scikit-learn compatible models such as CountVectorizer, TfidfVectorizer, LatentDirichletAllocation, and NMF.

## Args:
    vmodel (CountVectorizer, TfidfVectorizer, or None): The vectorization model to fit. If None, no vectorization is performed.
    tmodel (LatentDirichletAllocation, NMF, Pipeline, or None): The topic modeling model to fit. If None, no topic modeling is performed.
    x (list of arrays or array-like): Input text data to be used for fitting the models. Expected to be a nested structure that can be flattened with np.vstack.
    model_is_fit (bool): Flag indicating whether the models have already been fitted. If True, the function returns early without performing any fitting.

## Returns:
    None: This function does not return any value. It modifies the models in-place if fitting is required.

## Raises:
    None explicitly raised. However, underlying model fitting operations may raise exceptions from scikit-learn or numpy libraries.

## Constraints:
    Preconditions:
        - The input data `x` must be compatible with numpy's vstack operation (arrays must have the same number of columns).
        - The `vmodel` and `tmodel` parameters must be compatible with scikit-learn's expected interface.
        - The `vmodel` must have a `vocabulary_` attribute when checked for fitting status.
        - The `tmodel` must have a `components_` attribute when checked for fitting status.
    Postconditions:
        - If `model_is_fit` is False, the vectorization model (`vmodel`) will be fitted if not already fitted.
        - If `model_is_fit` is False, the topic modeling model (`tmodel`) will be fitted if not already fitted, using either raw text or transformed features from `vmodel`.

## Side Effects:
    - Modifies the state of `vmodel` and `tmodel` in-place by fitting them if necessary.
    - May perform I/O operations during model fitting (though this is typically internal to scikit-learn).

## Control Flow:
```mermaid
flowchart TD
    A[Start _fit_models] --> B{model_is_fit == True?}
    B -- Yes --> C[Return]
    B -- No --> D[vmodel is not None?]
    D -- Yes --> E[check_is_fitted(vmodel)]
    E --> F{NotFittedError?}
    F -- Yes --> G[vmodel.fit()]
    F -- No --> H[tmodel is not None?]
    G --> H
    H -- Yes --> I[check_is_fitted(tmodel)]
    I --> J{NotFittedError?}
    J -- Yes --> K{tmodel is Pipeline?}
    K -- Yes --> L[tmodel.fit()]
    K -- No --> M[tmodel.fit(vmodel.transform())]
    J -- No --> N[End]
    H -- No --> N
    D -- No --> N
```

## Examples:
    # Example 1: Fit both models
    vmodel = TfidfVectorizer()
    tmodel = LatentDirichletAllocation(n_components=5)
    data = [["hello world"], ["foo bar"]]
    _fit_models(vmodel, tmodel, data, False)
    
    # Example 2: Skip fitting if models are already fitted
    _fit_models(vmodel, tmodel, data, True)
    
    # Example 3: Fit only vectorizer
    _fit_models(vmodel, None, data, False)
```

## `hypertools.tools.text2mat._check_mtype` · *function*

## Summary:
Determines the concrete type of a given parameter and returns a standardized string identifier for that type.

## Description:
This utility function analyzes the type of the input parameter and categorizes it into one of several predefined type categories. It is designed to provide consistent type identification for downstream processing logic that needs to handle different input types differently. The function is typically called during preprocessing or validation phases when the exact type of an input parameter needs to be determined.

## Args:
    x: The input parameter whose type needs to be checked. Can be of any type.

## Returns:
    str: A string identifier representing the type of the input parameter. Possible return values include:
        - 'str': Input is a string object
        - 'dict': Input is a dictionary object  
        - 'class': Input is a class object (not an instance)
        - 'None': Input is None
        - 'class_instance': Input is an instance of a class

## Raises:
    TypeError: Raised when the input parameter is not of type string, dict, class, or class instance. This occurs when the input fails all type checks and the fallback inspection also fails.

## Constraints:
    Preconditions:
        - The input parameter x can be of any Python type
        - The function does not modify the input parameter
    
    Postconditions:
        - The function always returns one of the predefined string identifiers
        - The returned string is guaranteed to be one of ['str', 'dict', 'class', 'None', 'class_instance']

## Side Effects:
    - None

## Control Flow:
```mermaid
flowchart TD
    A[Start _check_mtype(x)] --> B{isinstance(x, str)?}
    B -- Yes --> C[Return 'str']
    B -- No --> D{isinstance(x, dict)?}
    D -- Yes --> E[Return 'dict']
    D -- No --> F{inspect.isclass(x)?}
    F -- Yes --> G[Return 'class']
    F -- No --> H{isinstance(x, type(None))?}
    H -- Yes --> I[Return 'None']
    H -- No --> J[Try inspect.isclass(type(x))]
    J -- Success --> K[Return 'class_instance']
    J -- Exception --> L[Raise TypeError]
```

## Examples:
    >>> _check_mtype("hello")
    'str'
    
    >>> _check_mtype({'key': 'value'})
    'dict'
    
    >>> _check_mtype(list)
    'class'
    
    >>> _check_mtype(None)
    'None'
    
    >>> _check_mtype([1, 2, 3])
    'class_instance'
    
    >>> _check_mtype(42)
    TypeError: Parameter must of type string, dict, class, or class instance.
```

