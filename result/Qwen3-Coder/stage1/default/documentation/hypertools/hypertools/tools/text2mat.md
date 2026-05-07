# `text2mat.py`

## `hypertools.tools.text2mat.text2mat` · *function*

## Summary:
Converts text data into numerical matrix representations using configurable vectorization and semantic modeling approaches.

## Description:
The text2mat function serves as a unified interface for transforming textual data into numerical matrices suitable for machine learning and data analysis workflows. It supports various combinations of text vectorization techniques (such as CountVectorizer, TfidfVectorizer) and semantic modeling approaches (such as LatentDirichletAllocation, NMF). The function intelligently handles pre-trained models, custom model specifications, and automatic fitting processes to produce ready-to-use matrix representations of text data.

## Args:
    data (list or str): Input text data to be converted. Can be a single string or a list of strings representing documents or text segments.
    vectorizer (str, dict, class, or None): Text vectorization method specification. Can be:
        - String name of a vectorizer (e.g., 'CountVectorizer', 'TfidfVectorizer')
        - Dictionary with 'model' and 'params' keys for custom configuration
        - Class or instance of a sklearn-compatible vectorizer
        - None to skip vectorization
    semantic (str, dict, class, or None): Semantic modeling method specification. Can be:
        - String name of a topic model (e.g., 'LatentDirichletAllocation', 'NMF')
        - Dictionary with 'model' and 'params' keys for custom configuration
        - Class or instance of a sklearn-compatible topic model
        - None to skip semantic modeling
    corpus (str or None): Predefined corpus name for loading pre-trained models. Supported values are 'wiki', 'nips', 'sotus'. If None, uses the provided data directly.

## Returns:
    list of arrays: Transformed text data where each element corresponds to the transformed version of the respective input element. The structure matches the input structure but with applied transformations. Each returned array has dimensions appropriate to the applied transformations.

## Raises:
    RuntimeError: When a user-provided vectorizer or semantic model doesn't have the required fit_transform method following the scikit-learn API.
    TypeError: When input parameters are of invalid types that cannot be processed by the internal type checking mechanism.

## Constraints:
    Preconditions:
        - Input data should be convertible to strings or array-like objects
        - Vectorizer and semantic parameters must be valid model specifications
        - When using pre-trained models (corpus parameter), supported corpus names are limited to 'wiki', 'nips', 'sotus'
        - If custom models are provided, they must follow the scikit-learn API with fit_transform methods
        
    Postconditions:
        - Function always returns a list of arrays with the same length as the input data
        - All returned arrays are properly transformed according to the specified pipeline
        - Models are appropriately fitted or loaded based on the input parameters

## Side Effects:
    - May perform I/O operations when loading pre-trained models from disk
    - Modifies vectorizer and semantic models in-place during the fitting process
    - May trigger loading of example datasets when using predefined corpus names

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
    H -- Yes --> I{corpus in ('wiki','nips','sotus')?}
    I -- Yes --> J{semantic == 'LatentDirichletAllocation' AND vectorizer == 'CountVectorizer'?}
    J -- Yes --> K[Load pre-trained model]
    J -- No --> L[Load corpus data]
    I -- No --> M[Convert corpus to array]
    H -- No --> N[Skip corpus processing]
    K --> O[Set model_is_fit = True]
    L --> P[Set corpus = np.array(corpus_data)]
    M --> P
    N --> P
    O --> P
    P --> Q{_check_mtype(vectorizer)}
    Q --> R{vtype == 'str'?}
    R -- Yes --> S[Get default vectorizer params]
    R -- No --> T{vtype == 'dict'?}
    T -- Yes --> U[Extract vectorizer params from dict]
    T -- No --> V{vtype in ('class', 'class_instance')?}
    V -- Yes --> W[Validate fit_transform method]
    V -- No --> X[Error: Invalid vectorizer type]
    W --> Y[Update vectorizer_models with user_model]
    Y --> Z[Set vectorizer = 'user_model']
    S --> AA
    U --> AA
    AA --> AB{_check_mtype(semantic)}
    AB --> AC{ttype == 'str'?}
    AC -- Yes --> AD[Get default semantic params]
    AC -- No --> AE{ttype == 'dict'?}
    AE -- Yes --> AF[Extract semantic params from dict]
    AE -- No --> AG{ttype in ('class', 'class_instance')?}
    AG -- Yes --> AH[Validate fit_transform method]
    AG -- No --> AI[Error: Invalid semantic type]
    AH --> AJ[Update texts with user_model]
    AJ --> AK[Set semantic = 'user_model']
    AD --> AL
    AF --> AL
    AL --> AM{vectorizer is not None?}
    AM -- Yes --> AN[Create vectorizer model instance]
    AM -- No --> AO[Set vmodel = None]
    AN --> AP
    AO --> AP
    AP --> AQ{semantic is not None?}
    AQ -- Yes --> AR[Create semantic model instance]
    AQ -- No --> AS[Set tmodel = None]
    AR --> AT
    AS --> AT
    AT --> AU{data is not list?}
    AU -- Yes --> AV[Wrap data in list]
    AU -- No --> AW[Continue]
    AV --> AW
    AW --> AX{corpus is None?}
    AX -- Yes --> AY[_fit_models with data]
    AX -- No --> AZ[_fit_models with corpus]
    AY --> BA
    AZ --> BA
    BA --> BB[Return _transform(vmodel, tmodel, data)]
```

## `hypertools.tools.text2mat._transform` · *function*

## Summary:
Transforms text data using vectorization and/or topic modeling models while preserving the original data structure.

## Description:
Applies vectorization and/or topic modeling transformations to text data, maintaining the structural integrity of the input data by splitting results appropriately. This function serves as a utility for processing text data through multiple transformation stages while ensuring that the output maintains the same hierarchical structure as the input.

## Args:
    vmodel (sklearn.base.BaseEstimator or None): Vectorization model (e.g., CountVectorizer, TfidfVectorizer) to apply to the text data. If None, no vectorization is performed. Must support the `.transform()` method.
    tmodel (sklearn.base.BaseEstimator, sklearn.pipeline.Pipeline, or None): Topic modeling model (e.g., LatentDirichletAllocation, NMF) or pipeline to apply to the text data. If None, no topic modeling is performed. Must support the `.transform()` method.
    x (list of arrays): Input text data represented as a list of arrays, where each array corresponds to a document or text segment. Each element should be a numpy array or array-like object.

## Returns:
    list of arrays: Transformed text data where each element corresponds to the transformed version of the respective input element. The structure matches the input structure but with applied transformations. Each returned array has dimensions appropriate to the applied transformations.

## Raises:
    AttributeError: If vmodel or tmodel is provided but lacks the required transform method.
    ValueError: If input x is malformed or incompatible with the transformation process.

## Constraints:
    Preconditions:
    - Input x must be a list of arrays where each array represents a text segment
    - vmodel and tmodel must be compatible with sklearn's transform interface if provided
    - When vmodel is provided, it must be fitted before calling this function
    - When tmodel is provided, it must be fitted before calling this function
    - All elements in x should be compatible with numpy operations (np.vstack, np.vsplit)
    
    Postconditions:
    - Output list contains the same number of elements as input x
    - Each output element has the appropriate dimensionality based on the applied transformations
    - The structure of the data is preserved through the transformations

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _transform] --> B{vmodel is not None?}
    B -- Yes --> C[vmodel.transform()]
    B -- No --> D[Skip vectorization]
    C --> E[np.vstack(x).ravel()]
    E --> F[vmodel.transform().toarray()]
    F --> G[np.vsplit()]
    G --> H[Update x]
    D --> H
    H --> I{tmodel is not None?}
    I -- Yes --> J{tmodel is Pipeline?}
    J -- Yes --> K[tmodel.transform()]
    J -- No --> L[tmodel.transform()]
    K --> M[np.vsplit()]
    L --> M
    M --> N[Update x]
    I -- No --> O[Skip topic modeling]
    O --> N
    N --> P[Return [xi for xi in x]]
```

## Examples:
    # Example 1: Apply only vectorization to text segments
    vectorizer_model.fit(text_corpus)  # Must be fitted first
    transformed_data = _transform(vectorizer_model, None, text_segments)
    
    # Example 2: Apply only topic modeling to text segments  
    lda_model.fit(vectorized_data)  # Must be fitted first
    transformed_data = _transform(None, lda_model, text_segments)
    
    # Example 3: Apply both vectorization and topic modeling
    vectorizer_model.fit(text_corpus)  # Must be fitted first
    lda_model.fit(vectorized_data)  # Must be fitted first
    transformed_data = _transform(vectorizer_model, lda_model, text_segments)
``

## `hypertools.tools.text2mat._fit_models` · *function*

## Summary:
Initializes and fits text vectorization and topic modeling components when needed.

## Description:
This utility function manages the fitting process for text preprocessing and topic modeling components. It checks if models are already fitted and only performs fitting when necessary, preventing redundant operations. The function handles both vectorization models (like CountVectorizer or TfidfVectorizer) and topic models (like LatentDirichletAllocation or NMF), with special handling for sklearn Pipeline objects.

## Args:
    vmodel (sklearn.base.BaseEstimator or None): Vectorization model to fit, such as CountVectorizer or TfidfVectorizer. Can be None if no vectorization is needed.
    tmodel (sklearn.base.BaseEstimator or None): Topic model to fit, such as LatentDirichletAllocation or NMF. Can be None if no topic modeling is needed.
    x (array-like): Text data to fit the models on, typically a list of documents or tokenized texts.
    model_is_fit (bool): Flag indicating whether models are already fitted. If True, the function returns early without performing any fitting.

## Returns:
    None: This function does not return any value. It modifies the models in-place if fitting is required.

## Raises:
    None explicitly raised: The function handles NotFittedError exceptions internally and doesn't propagate them.

## Constraints:
    Preconditions:
    - x should be array-like containing text data
    - vmodel and tmodel should be sklearn-compatible estimators or None
    - model_is_fit should be a boolean value
    
    Postconditions:
    - If vmodel is not None and not already fitted, it will be fitted on the flattened x data
    - If tmodel is not None and not already fitted, it will be fitted either directly or via transformation from vmodel

## Side Effects:
    - Modifies vmodel and tmodel in-place by fitting them on the provided text data
    - May perform I/O operations during model fitting (depending on underlying sklearn implementations)

## Control Flow:
```mermaid
flowchart TD
    A[Start _fit_models] --> B{model_is_fit == True?}
    B -- Yes --> C[Return]
    B -- No --> D[vmodel is not None?]
    D -- Yes --> E[check_is_fitted(vmodel)]
    E --> F{NotFittedError?}
    F -- Yes --> G[vmodel.fit(flattened_x)]
    F -- No --> H[Skip vmodel fitting]
    D -- No --> I[Skip vmodel fitting]
    I --> J[tmodel is not None?]
    J -- Yes --> K[check_is_fitted(tmodel)]
    K --> L{NotFittedError?}
    L -- Yes --> M{tmodel is Pipeline?}
    M -- Yes --> N[tmodel.fit(flattened_x)]
    M -- No --> O[tmodel.fit(vmodel.transform(flattened_x))]
    L -- No --> P[Skip tmodel fitting]
    J -- No --> Q[Skip tmodel fitting]
    G --> R[End]
    H --> R
    N --> R
    O --> R
    P --> R
```

## Examples:
    # Example 1: Fit both models
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    import numpy as np
    
    vectorizer = TfidfVectorizer(max_features=1000)
    lda_model = LatentDirichletAllocation(n_components=5)
    documents = ["this is document one", "this is document two"]
    
    _fit_models(vectorizer, lda_model, documents, False)
    # Both models are now fitted
    
    # Example 2: Skip fitting when models are already fitted
    _fit_models(vectorizer, lda_model, documents, True)
    # No fitting occurs, function returns immediately
    
    # Example 3: Fit only vectorizer
    _fit_models(vectorizer, None, documents, False)
    # Only vectorizer is fitted, topic model is skipped
```

## `hypertools.tools.text2mat._check_mtype` · *function*

## Summary:
Determines and returns the type category of a given input parameter for text processing operations.

## Description:
This utility function performs type checking on input parameters to classify them into specific categories used throughout the text processing pipeline. It is designed to validate input types for various text analysis operations and ensure proper handling based on the parameter type.

## Args:
    x: The input parameter whose type needs to be determined. Can be of any type.

## Returns:
    str: A string identifier representing the type category of the input:
        - 'str': Input is a string type
        - 'dict': Input is a dictionary type  
        - 'class': Input is a class object
        - 'None': Input is NoneType
        - 'class_instance': Input is an instance of a class

## Raises:
    TypeError: When the input parameter is not of type string, dict, class, or class instance.

## Constraints:
    Preconditions:
        - Input parameter x can be of any type
    Postconditions:
        - Function always returns one of the predefined string type identifiers
        - Function raises TypeError for invalid input types

## Side Effects:
    None: This function has no side effects and is purely a type checking utility.

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
```python
# Valid type checks
_check_mtype("hello")           # Returns 'str'
_check_mtype({"key": "value"})  # Returns 'dict'  
_check_mtype(MyClass)           # Returns 'class'
_check_mtype(None)              # Returns 'None'
_check_mtype(MyClass())         # Returns 'class_instance'

# Invalid type raises TypeError
_check_mtype(123)               # Raises TypeError
_check_mtype([1, 2, 3])         # Raises TypeError
```

