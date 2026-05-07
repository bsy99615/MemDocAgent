# `text2mat.py`

## `hypertools.tools.text2mat.text2mat` · *function*

## Summary:
Converts text data into numerical matrix representations using configurable vectorization and semantic modeling techniques.

## Description:
Transforms raw text data into numerical matrices suitable for machine learning applications by applying text vectorization followed by semantic modeling. The function supports various combinations of vectorizers (like CountVectorizer, TfidfVectorizer) and semantic models (like LatentDirichletAllocation, NMF) with built-in support for pre-trained models from corpora like Wikipedia, NIPS, and State of the Union speeches. This function encapsulates the entire text-to-matrix pipeline, including model selection, fitting, and transformation.

## Args:
    data (str or list): Input text data to be converted. Can be a single string or a list of strings/documents. 
    vectorizer (str, dict, class, or None): Text vectorization method to use. Can be a string identifier (e.g., 'CountVectorizer'), dictionary with 'model' and 'params' keys, or a class instance with fit_transform method. If None, defaults to 'CountVectorizer'. 
    semantic (str, dict, class, or None): Semantic modeling method to use. Can be a string identifier (e.g., 'LatentDirichletAllocation'), dictionary with 'model' and 'params' keys, or a class instance with fit_transform method. If None, defaults to 'LatentDirichletAllocation'.
    corpus (str or None): Pre-defined corpus to use for model loading. Supported values are 'wiki', 'nips', 'sotus'. If None, uses provided data for training. Defaults to 'wiki'.

## Returns:
    list: Transformed text data represented as numerical matrices, preserving the original chunk structure of the input data. Each element in the returned list corresponds to the transformed version of the respective input chunk.

## Raises:
    RuntimeError: When user-provided vectorizer or semantic model doesn't have a fit_transform method following scikit-learn API conventions.

## Constraints:
    Preconditions:
        - Input data must be compatible with numpy array conversion
        - Vectorizer and semantic models must follow scikit-learn API specifications
        - If corpus is specified, it must be one of 'wiki', 'nips', or 'sotus'
        - Data should be in a format suitable for text processing (strings or lists of strings)
        - Global dictionaries `vectorizer_models` and `texts` must be initialized with appropriate model mappings
    
    Postconditions:
        - Output maintains the same number of chunks as input data
        - All returned matrices are numerically representable
        - Models are properly fitted before transformation
        - Global dictionaries `vectorizer_models` and `texts` may be updated with user-provided models

## Side Effects:
    - May perform I/O operations when loading pre-trained models from corpora
    - Modifies global dictionaries `vectorizer_models` and `texts` when user-provided models are used
    - Fits vectorization and semantic models in-place during processing
    - Uses global variables `vectorizer_models` and `texts` for model instantiation

## Control Flow:
```mermaid
flowchart TD
    A[Start text2mat] --> B{semantic is None?}
    B -->|Yes| C[Set semantic = 'LatentDirichletAllocation']
    B -->|No| D[Continue]
    C --> D
    D --> E{vectorizer is None?}
    E -->|Yes| F[Set vectorizer = 'CountVectorizer']
    E -->|No| G[Continue]
    F --> G
    G --> H{corpus is not None?}
    H -->|Yes| I{corpus in ('wiki','nips','sotus')?}
    I -->|Yes| J{semantic == 'LatentDirichletAllocation' AND vectorizer == 'CountVectorizer'?}
    J -->|Yes| K[Load pre-trained model from corpus]
    J -->|No| L[Load corpus data]
    I -->|No| M[Convert corpus to array]
    H -->|No| N[Skip corpus processing]
    K --> O[Set model_is_fit = True]
    L --> P[Set corpus = np.array(corpus_data)]
    M --> Q[Set corpus = np.array([corpus])]
    O --> R
    P --> R
    Q --> R
    R --> S{_check_mtype(vectorizer)}
    S --> T{vtype == 'str'}
    T -->|Yes| U[Get default vectorizer params]
    T -->|No| V[Process vectorizer dict/class]
    U --> W
    V --> W
    W --> X{_check_mtype(semantic)}
    X --> Y{ttype == 'str'}
    Y -->|Yes| Z[Get default semantic params]
    Y -->|No| AA[Process semantic dict/class]
    Z --> AB
    AA --> AB
    AB --> AC{vectorizer is not None?}
    AC -->|Yes| AD[Create vectorizer model instance from vectorizer_models]
    AC -->|No| AE[Set vmodel = None]
    AD --> AF
    AE --> AF
    AF --> AG{semantic is not None?}
    AG -->|Yes| AH[Create semantic model instance from texts]
    AG -->|No| AI[Set tmodel = None]
    AH --> AJ
    AI --> AJ
    AJ --> AK{data is not list?}
    AK -->|Yes| AL[Wrap data in list]
    AK -->|No| AM[Continue]
    AL --> AN
    AM --> AN
    AN --> AO{corpus is None?}
    AO -->|Yes| AP[Fit models with data]
    AO -->|No| AQ[Fit models with corpus]
    AP --> AR
    AQ --> AR
    AR --> AS[Transform data with fitted models]
    AS --> AT[Return transformed data]
```

## `hypertools.tools.text2mat._transform` · *function*

## Summary:
Applies vectorization and topic modeling transformations to text data chunks while preserving their structural organization.

## Description:
Processes text data through vectorization and/or topic modeling models, maintaining the original chunk structure. This utility function handles the complexity of applying scikit-learn models to text data that has been pre-splitted into logical units, ensuring proper transformation and reconstruction of the data structure.

The function is typically called internally by text processing pipelines when applying transformations to text data that has been pre-split into logical units (such as documents or sentences). It enables the application of both feature extraction (vectorization) and topic modeling transformations while preserving the hierarchical structure of the input data chunks.

## Args:
    vmodel (sklearn.base.BaseEstimator or None): Vectorization model (e.g., CountVectorizer, TfidfVectorizer) to apply. If None, no vectorization is performed.
    tmodel (sklearn.base.BaseEstimator or sklearn.pipeline.Pipeline or None): Topic modeling or transformation model to apply. If None, no topic modeling is performed.
    x (list): List of text data chunks, where each chunk can be a string or list of strings.

## Returns:
    list: Transformed data chunks, where each chunk corresponds to the transformed version of the original input chunks. The structure preserves the original chunking pattern.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
        - Input x must be a list of text chunks
        - If vmodel is provided, it must be a fitted sklearn estimator with a transform method
        - If tmodel is provided, it must be a fitted sklearn estimator or Pipeline with a transform method
    Postconditions:
        - Output maintains the same number of chunks as input
        - Each output chunk is the result of applying appropriate transformations

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _transform] --> B{vmodel is not None?}
    B -->|Yes| C[Calculate split points from chunk lengths]
    C --> D[Flatten all chunks with np.vstack(x).ravel()]
    D --> E[Apply vmodel.transform()]
    E --> F[Convert to array with toarray()]
    F --> G[Split result using split points]
    G --> H{tmodel is not None?}
    H -->|Yes| I[Check if tmodel is Pipeline]
    I -->|Yes| J[Apply tmodel.transform() with ravel()]
    I -->|No| K[Apply tmodel.transform()]
    K --> L[Split result using split points]
    H -->|No| M[Return x]
    B -->|No| N{tmodel is not None?}
    N -->|Yes| O[Calculate split points from chunk lengths]
    O --> P[Flatten all chunks with np.vstack(x).ravel()]
    P --> Q[Check if tmodel is Pipeline]
    Q -->|Yes| R[Apply tmodel.transform() with ravel()]
    Q -->|No| S[Apply tmodel.transform()]
    S --> T[Split result using split points]
    T --> U[Return x]
    N -->|No| V[Return x]
```

## Examples:
```python
# Apply vectorization to text data
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
transformed_data = _transform(vectorizer, None, [["doc1 sentence1", "doc1 sentence2"], ["doc2 sentence1"]])

# Apply topic modeling to text data  
from sklearn.decomposition import LatentDirichletAllocation
lda_model = LatentDirichletAllocation(n_components=5)
transformed_data = _transform(None, lda_model, [["doc1 sentence1", "doc1 sentence2"], ["doc2 sentence1"]])

# Apply both vectorization and topic modeling
transformed_data = _transform(vectorizer, lda_model, [["doc1 sentence1", "doc1 sentence2"], ["doc2 sentence1"]])
```

## `hypertools.tools.text2mat._fit_models` · *function*

## Summary:
Configures and fits text vectorization and topic modeling components for text-to-matrix transformations.

## Description:
This internal utility function manages the fitting process for text preprocessing and topic modeling components. It ensures that vectorizers and topic models are properly initialized and fitted only when necessary, avoiding redundant operations. The function handles both standard scikit-learn estimators and pipeline objects, making it flexible for various text processing workflows.

## Args:
    vmodel (object or None): Text vectorizer model (e.g., CountVectorizer, TfidfVectorizer) to be fitted. Can be None if no vectorization is needed.
    tmodel (object or None): Topic model (e.g., LatentDirichletAllocation, NMF) to be fitted. Can be None if no topic modeling is needed.
    x (array-like): Input text data to be used for fitting the models. Expected to be a nested array structure that can be flattened with np.vstack.
    model_is_fit (bool): Flag indicating whether models are already fitted. If True, the function returns immediately without performing any fitting operations.

## Returns:
    None: This function performs in-place fitting operations and does not return any values.

## Raises:
    None explicitly raised: The function handles NotFittedError internally through try/except blocks.

## Constraints:
    Preconditions:
        - Input data `x` should be compatible with numpy's vstack operation
        - Vectorizer model (`vmodel`) should support a `fit` method and have a `vocabulary_` attribute when checked
        - Topic model (`tmodel`) should support a `fit` method and have a `components_` attribute when checked
        - If `tmodel` is a Pipeline, it should support a `fit` method that accepts text data directly
    
    Postconditions:
        - If models are not already fitted, they will be fitted with the provided text data
        - The function ensures that vectorizer is fitted before topic model when both are provided

## Side Effects:
    - Modifies the internal state of `vmodel` and `tmodel` by fitting them with input data
    - May perform I/O operations during the fitting process of sklearn models
    - No external state mutations or global variable modifications

## Control Flow:
```mermaid
flowchart TD
    A[Start _fit_models] --> B{model_is_fit == True?}
    B -- Yes --> C[Return]
    B -- No --> D[vmodel is not None?]
    D -- Yes --> E[Try check_is_fitted(vmodel, ['vocabulary_'])]
    E --> F{NotFittedError?}
    F -- Yes --> G[vmodel.fit(np.vstack(x).ravel())]
    F -- No --> H[Continue]
    D -- No --> I[Skip vectorizer fitting]
    I --> J[tmodel is not None?]
    J -- Yes --> K[Try check_is_fitted(tmodel, ['components_'])]
    K --> L{NotFittedError?}
    L -- Yes --> M{isinstance(tmodel, Pipeline)?}
    M -- Yes --> N[tmodel.fit(np.vstack(x).ravel())]
    M -- No --> O[tmodel.fit(vmodel.transform(np.vstack(x).ravel()))]
    L -- No --> P[Continue]
    Q[End]
    G --> H
    N --> P
    O --> P
    H --> P
```

## Examples:
    # Example 1: Fit both models
    vmodel = TfidfVectorizer()
    tmodel = LatentDirichletAllocation(n_components=10)
    text_data = [["hello world"], ["foo bar"]]
    _fit_models(vmodel, tmodel, text_data, False)
    
    # Example 2: Skip fitting when models are already fitted
    _fit_models(vmodel, tmodel, text_data, True)
    
    # Example 3: Fit only vectorizer
    _fit_models(vmodel, None, text_data, False)
    
    # Example 4: Fit with Pipeline topic model
    tmodel = Pipeline([('nmf', NMF(n_components=5))])
    _fit_models(vmodel, tmodel, text_data, False)

## `hypertools.tools.text2mat._check_mtype` · *function*

## Summary:
Determines and returns the standardized type identifier for a given parameter.

## Description:
This utility function examines the type of the input parameter and returns a consistent string identifier representing its type. It is designed to categorize parameters into predefined type classes for use in type-aware processing pipelines.

## Args:
    x (any): The parameter whose type needs to be identified.

## Returns:
    str: A string identifier representing the type of the input parameter. Possible return values include:
        - 'str': Input is a string type
        - 'dict': Input is a dictionary type  
        - 'class': Input is a class object
        - 'None': Input is NoneType
        - 'class_instance': Input is an instance of a class

## Raises:
    TypeError: Raised when the input parameter is not of type string, dict, class, or class instance.

## Constraints:
    Preconditions:
        - The input parameter x can be of any type
    Postconditions:
        - Always returns one of the predefined string identifiers ('str', 'dict', 'class', 'None', 'class_instance')

## Side Effects:
    - No I/O operations
    - No external state mutations
    - No external service calls

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
    # Check string type
    result = _check_mtype("hello")
    # Returns: 'str'
    
    # Check dictionary type  
    result = _check_mtype({"key": "value"})
    # Returns: 'dict'
    
    # Check None type
    result = _check_mtype(None)
    # Returns: 'None'
    
    # Check class type
    result = _check_mtype(list)
    # Returns: 'class'
    
    # Check class instance
    result = _check_mtype([1, 2, 3])
    # Returns: 'class_instance'
```

