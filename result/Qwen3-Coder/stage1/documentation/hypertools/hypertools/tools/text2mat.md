# `text2mat.py`

## `hypertools.tools.text2mat.text2mat` · *function*

## Summary:
Converts text data into numerical matrices using configurable vectorization and semantic modeling techniques.

## Description:
The `text2mat` function transforms textual data into numerical representations suitable for machine learning and data analysis workflows. It supports various text vectorization methods (like CountVectorizer, TfidfVectorizer) and semantic modeling approaches (such as LatentDirichletAllocation, NMF) to create feature matrices from text inputs. The function can utilize pre-trained models from built-in corpora or train new models on provided data.

This logic is extracted into its own function to provide a unified interface for text-to-matrix conversion while handling the complexity of model selection, parameter management, training, and transformation processes. It abstracts away the intricate details of model instantiation, fitting, and transformation, allowing users to focus on their text analysis tasks.

## Args:
    data (list or str): Text data to be converted. Can be a single string or a list of strings/arrays.
    vectorizer (str, dict, class, or None): Text vectorization method to use. Can be a string identifier, dictionary with 'model' and 'params' keys, or a class instance. Defaults to 'CountVectorizer'.
    semantic (str, dict, class, or None): Semantic modeling method to use. Can be a string identifier, dictionary with 'model' and 'params' keys, or a class instance. Defaults to 'LatentDirichletAllocation'.
    corpus (str or None): Built-in corpus name ('wiki', 'nips', 'sotus') to use for pre-trained models or data. Defaults to 'wiki'.

## Returns:
    numpy.ndarray or list: Transformed numerical representation of the input text data. When data is a list of documents, returns a list of arrays where each array corresponds to a document's feature representation. When data is a single string, returns a single array representing that document's features.

## Raises:
    RuntimeError: When vectorizer or semantic model doesn't have the required fit_transform method following scikit-learn API.
    TypeError: When input parameters cannot be classified into supported types by _check_mtype function.

## Constraints:
    Preconditions:
        - Input data should be compatible with numpy array conversion
        - Vectorizer and semantic parameters must be one of: string identifier, dictionary with model/params, class, or class instance
        - If using pre-trained models, corpus must be one of 'wiki', 'nips', 'sotus'
        - All models must follow scikit-learn API conventions with fit_transform methods
        
    Postconditions:
        - Input data is converted to a list format if it's a single string
        - Vectorization and semantic models are properly fitted or loaded
        - Output is a numerical matrix representation of the input text

## Side Effects:
    - File I/O operations when loading pre-trained models or example datasets via the load function
    - Model fitting operations that modify internal states of vectorization and semantic models
    - Potential caching of models or data through the load function's internal mechanisms

## Control Flow:
```mermaid
flowchart TD
    A[Start text2mat] --> B{semantic is None?}
    B -- Yes --> C[Set semantic = 'LatentDirichletAllocation']
    B -- No --> D[Continue]
    D --> E{vectorizer is None?}
    E -- Yes --> F[Set vectorizer = 'CountVectorizer']
    E -- No --> G[Continue]
    G --> H{corpus is not None?}
    H -- Yes --> I{corpus in ('wiki','nips','sotus')?}
    I -- Yes --> J{semantic == 'LatentDirichletAllocation' AND vectorizer == 'CountVectorizer'?}
    J -- Yes --> K[Load pre-trained model with load(corpus + '_model')]
    J -- No --> L[Load corpus data with load(corpus).get_data()]
    I -- No --> M[Convert corpus to numpy array]
    H -- No --> N[Skip corpus processing]
    K --> O[Set model_is_fit = True]
    L --> P[Set corpus = numpy.array(corpus_data)]
    M --> Q[Set corpus = numpy.array([corpus])]
    O --> R[Process vectorizer type with _check_mtype]
    P --> R
    Q --> R
    R --> S{vtype == 'str'?}
    S -- Yes --> T[Get default vectorizer params]
    S -- No --> U{vtype == 'dict'?}
    U -- Yes --> V[Get vectorizer params from dict]
    U -- No --> W{vtype in ('class', 'class_instance')?}
    W -- Yes --> X[Validate vectorizer has fit_transform]
    W -- No --> Y[Error: Invalid vectorizer type]
    X --> Z{vectorizer has fit_transform?}
    Z -- Yes --> AA[Update vectorizer_models with user_model]
    Z -- No --> AB[Error: Missing fit_transform method]
    V --> AC[Set vectorizer = dict model key]
    T --> AD[Set vectorizer = str value]
    AD --> AE[Process semantic type with _check_mtype]
    AE --> AF{ttype == 'str'?}
    AF -- Yes --> AG[Get default semantic params]
    AF -- No --> AH{ttype == 'dict'?}
    AH -- Yes --> AI[Get semantic params from dict]
    AH -- No --> AJ{ttype in ('class', 'class_instance')?}
    AJ -- Yes --> AK[Validate semantic has fit_transform]
    AJ -- No --> AL[Error: Invalid semantic type]
    AK --> AM{semantic has fit_transform?}
    AM -- Yes --> AN[Update texts with user_model]
    AM -- No --> AO[Error: Missing fit_transform method]
    AI --> AP[Set semantic = dict model key]
    AG --> AQ[Set semantic = str value]
    AQ --> AR[Create vectorizer model instance]
    AP --> AR
    AR --> AS{vectorizer is not None?}
    AS -- Yes --> AT[Instantiate vectorizer model]
    AS -- No --> AU[Set vmodel = None]
    AT --> AV[Create semantic model instance]
    AU --> AV
    AV --> AW{semantic is not None?}
    AW -- Yes --> AX[Instantiate semantic model]
    AW -- No --> AY[Set tmodel = None]
    AX --> AZ[Ensure data is list format]
    AY --> AZ
    AZ --> BA{corpus is None?}
    BA -- Yes --> BB[Fit models with data]
    BA -- No --> BC[Fit models with corpus]
    BB --> BD[Transform data with fitted models]
    BC --> BD
    BD --> BE[Return transformation result]
```

## Examples:
    # Basic usage with default parameters
    matrix = text2mat(["This is document one", "This is document two"])
    
    # Using specific vectorizer and semantic models
    matrix = text2mat(
        ["Document one", "Document two"],
        vectorizer="TfidfVectorizer",
        semantic="NMF"
    )
    
    # Using pre-trained wiki model
    matrix = text2mat(["Some text"], corpus="wiki")
    
    # Using custom parameters
    matrix = text2mat(
        ["Document one", "Document two"],
        vectorizer={"model": "CountVectorizer", "params": {"max_features": 1000}},
        semantic={"model": "LatentDirichletAllocation", "params": {"n_components": 5}}
    )
    
    # Using custom class instances
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    
    vectorizer = CountVectorizer(max_features=1000)
    semantic = LatentDirichletAllocation(n_components=5)
    matrix = text2mat(["Document one", "Document two"], vectorizer=vectorizer, semantic=semantic)

## `hypertools.tools.text2mat._transform` · *function*

*No documentation generated.*

## `hypertools.tools.text2mat._fit_models` · *function*

## Summary:
Configures and fits text vectorization and topic modeling components based on their current state and input data.

## Description:
This internal helper function manages the fitting process for text preprocessing and topic modeling components. It ensures that vectorization models (like CountVectorizer or TfidfVectorizer) and topic models (like LatentDirichletAllocation or NMF) are properly fitted only when necessary, avoiding redundant operations on already-fitted models. The function handles both Pipeline-based topic models and direct topic models, applying appropriate fitting strategies for each case. This function is typically called within text processing pipelines to prepare models for subsequent operations.

## Args:
    vmodel (sklearn.base.BaseEstimator or None): Vectorization model (e.g., CountVectorizer, TfidfVectorizer) to be fitted. Can be None if no vectorization is needed.
    tmodel (sklearn.base.BaseEstimator or sklearn.pipeline.Pipeline or None): Topic model (e.g., LatentDirichletAllocation, NMF) to be fitted. Can be None if no topic modeling is needed.
    x (list or array-like): Input text data to be used for fitting the models. Expected to be a nested structure that can be flattened with numpy.vstack(x).ravel().
    model_is_fit (bool): Flag indicating whether models are already fitted. If True, the function returns early without performing any fitting operations.

## Returns:
    None: This function performs in-place fitting operations and returns no value.

## Raises:
    None explicitly raised: The function handles NotFittedError exceptions internally and doesn't raise them outward.

## Constraints:
    Preconditions:
    - Input data x should be compatible with numpy.vstack(x).ravel() operation
    - vmodel and tmodel should be sklearn-compatible estimators or None
    - If vmodel is provided, it should support the vocabulary_ attribute check
    - If tmodel is provided, it should support the components_ attribute check or be a Pipeline
    
    Postconditions:
    - Vectorization model (vmodel) is fitted if not already fitted and vmodel is not None
    - Topic model (tmodel) is fitted if not already fitted and tmodel is not None
    - Both models are in a fitted state after execution (if not None and not already fitted)

## Side Effects:
    - Modifies the internal state of vmodel and tmodel by fitting them with input data
    - May perform I/O operations during the fitting process (as part of sklearn model fitting)
    - No external state mutations or global variable modifications

## Control Flow:
```mermaid
flowchart TD
    A[Start _fit_models] --> B{model_is_fit == True?}
    B -- Yes --> C[Return]
    B -- No --> D[vmodel is not None?]
    D -- Yes --> E[Try check_is_fitted(vmodel, ['vocabulary_'])]
    E --> F{NotFittedError?}
    F -- Yes --> G[vmodel.fit(numpy.vstack(x).ravel())]
    F -- No --> H[Continue]
    D -- No --> I[Skip vmodel fitting]
    I --> J[tmodel is not None?]
    J -- Yes --> K[Try check_is_fitted(tmodel, ['components_'])]
    K --> L{NotFittedError?}
    L -- Yes --> M{isinstance(tmodel, Pipeline)?}
    M -- Yes --> N[tmodel.fit(numpy.vstack(x).ravel())]
    M -- No --> O[tmodel.fit(vmodel.transform(numpy.vstack(x).ravel()))]
    L -- No --> P[Continue]
    J -- No --> Q[Skip tmodel fitting]
    Q --> R[End]
```

## Examples:
    # Example 1: Fitting both models
    vmodel = TfidfVectorizer()
    tmodel = LatentDirichletAllocation(n_components=10)
    data = [["text1", "text2"], ["text3", "text4"]]
    _fit_models(vmodel, tmodel, data, False)
    # Both models are now fitted
    
    # Example 2: Only fitting vectorization model
    vmodel = CountVectorizer()
    tmodel = None
    data = [["text1", "text2"], ["text3", "text4"]]
    _fit_models(vmodel, tmodel, data, False)
    # Only vmodel is fitted
    
    # Example 3: Models already fitted
    vmodel = TfidfVectorizer()
    tmodel = LatentDirichletAllocation(n_components=10)
    # Assuming models are already fitted
    _fit_models(vmodel, tmodel, data, True)
    # Function returns immediately without fitting

## `hypertools.tools.text2mat._check_mtype` · *function*

## Summary:
Determines and returns the string identifier for the type of the input parameter.

## Description:
This utility function performs type checking on input parameters and returns a standardized string representation of their type. It is designed to handle common Python types including strings, dictionaries, class objects, None values, and class instances. The function is typically used internally to validate parameter types and route execution paths based on input type.

The logic is extracted into its own function to provide a centralized, reusable type checking mechanism that can be easily tested and maintained independently from the main processing logic. This promotes code modularity and reduces duplication across different parts of the text processing pipeline.

## Args:
    x: The input parameter whose type needs to be identified. Can be of any type.

## Returns:
    str: A string identifier representing the type of the input parameter. Possible return values include:
        - 'str': Input is a string
        - 'dict': Input is a dictionary
        - 'class': Input is a class object
        - 'None': Input is None
        - 'class_instance': Input is an instance of a class

## Raises:
    TypeError: When the input parameter is not of type string, dict, class, or class instance. This occurs when the input fails the type checking and cannot be classified into any of the supported categories.

## Constraints:
    Preconditions:
        - The input parameter `x` can be of any Python type
    Postconditions:
        - The function always returns one of the predefined string identifiers ('str', 'dict', 'class', 'None', or 'class_instance')
        - The function does not modify the input parameter

## Side Effects:
    None: This function has no side effects and is purely a type identification utility.

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
    J -- Yes --> K[Return 'class_instance']
    J -- No --> L[Raise TypeError]
```

## Examples:
    # Check different types
    type_str = _check_mtype("hello")           # Returns 'str'
    type_dict = _check_mtype({"key": "value"}) # Returns 'dict'
    type_none = _check_mtype(None)             # Returns 'None'
    
    # Check class and class instance
    class MyClass: pass
    type_class = _check_mtype(MyClass)         # Returns 'class'
    type_instance = _check_mtype(MyClass())    # Returns 'class_instance'
    
    # Error case
    try:
        _check_mtype(123)
    except TypeError as e:
        print(e)  # Prints: Parameter must of type string, dict, class, or class instance.
```

