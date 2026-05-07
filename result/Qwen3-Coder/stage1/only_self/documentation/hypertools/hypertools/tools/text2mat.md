# `text2mat.py`

## `hypertools.tools.text2mat.text2mat` · *function*

*No documentation generated.*

## `hypertools.tools.text2mat._transform` · *function*

## Summary:
Processes segmented text data through vectorization and/or topic modeling transformations while maintaining original segment structure.

## Description:
This internal helper function applies sequential transformations to segmented text data. It first computes cumulative segment lengths to determine split points, then applies vectorization (vmodel) and/or topic modeling (tmodel) transformations to the flattened text data, and finally splits the results back into the original segment structure.

The function is used internally by text processing pipelines in the text2mat module to handle the transformation phase of text analysis workflows. It ensures that segmented text data maintains its structural relationships throughout the transformation process.

## Args:
    vmodel (object, optional): A fitted sklearn vectorization model (e.g., CountVectorizer, TfidfVectorizer) to apply to text data. If None, no vectorization is performed.
    tmodel (object, optional): A fitted sklearn topic modeling model (e.g., LatentDirichletAllocation, NMF) or sklearn Pipeline to apply to text data. If None, no topic modeling is performed.
    x (list of arrays): Input text data segmented into groups, where each element is an array containing text representations for that segment.

## Returns:
    list of arrays: Transformed text representations, where each element corresponds to a segment from the input data and maintains the same structure as the original segments.

## Raises:
    None explicitly raised in the function body, but underlying sklearn model operations may raise exceptions such as NotFittedError if models are not fitted.

## Constraints:
    Preconditions:
    - Input x must be a list of arrays where each array represents a text segment
    - vmodel and tmodel must be fitted sklearn models if provided
    - All models must support the transform() method
    
    Postconditions:
    - Output list has the same length as input x
    - Each transformed element preserves the shape characteristics of its corresponding input segment
    - Original segmentation structure is maintained in the output

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _transform] --> B[Compute split points]
    B --> C{vmodel is not None?}
    C -- Yes --> D[vmodel.transform()]
    C -- No --> E[Skip vmodel transform]
    D --> F[Convert to array with toarray()]
    F --> G[Split with np.vsplit()]
    E --> G
    G --> H{tmodel is not None?}
    H -- Yes --> I{tmodel is Pipeline?}
    I -- Yes --> J[tmodel.transform()]
    I -- No --> K[tmodel.transform()]
    H -- No --> L[Return result]
    J --> M[Split with np.vsplit()]
    K --> M
    M --> L
    L --> N[Return [xi for xi in x]]
```

## Examples:
    # Example 1: Apply vectorization to segmented text
    # Input: x = [[doc1_text], [doc2_text, doc3_text]] 
    #        where doc1_text, doc2_text, doc3_text are text samples
    vectorizer = TfidfVectorizer()
    vectorizer.fit(text_corpus)
    result = _transform(vectorizer, None, [[doc1_text], [doc2_text, doc3_text]])
    # Output: list of arrays with same structure as input segments
    
    # Example 2: Apply topic modeling to segmented text  
    lda = LatentDirichletAllocation(n_components=5)
    lda.fit(vectorized_corpus)
    result = _transform(None, lda, [[doc1_text], [doc2_text, doc3_text]])
    # Output: list of arrays with topic distributions for each segment
    
    # Example 3: Apply both transformations sequentially
    vectorizer = TfidfVectorizer()
    vectorizer.fit(text_corpus)
    lda = LatentDirichletAllocation(n_components=5)
    lda.fit(vectorizer.transform(text_corpus))
    result = _transform(vectorizer, lda, [[doc1_text], [doc2_text, doc3_text]])
    # Output: list of arrays with topic distributions for each segment
```

## `hypertools.tools.text2mat._fit_models` · *function*

## Summary:
Conditionally fits vectorization and topic models based on their current fit status to prevent redundant fitting operations.

## Description:
This helper function manages the fitting process for text preprocessing models by checking if vectorization and topic models are already fitted before performing fitting operations. It prevents redundant computations and supports lazy initialization in text processing pipelines. The function specifically handles scikit-learn compatible models and distinguishes between standard models and Pipeline configurations.

## Args:
    vmodel (sklearn.base.BaseEstimator or None): Vectorization model (e.g., CountVectorizer, TfidfVectorizer) to potentially fit. Can be None if no vectorization is needed. Must support the `vocabulary_` attribute after fitting.
    tmodel (sklearn.base.BaseEstimator or None): Topic model (e.g., LatentDirichletAllocation, NMF) to potentially fit. Can be None if no topic modeling is needed. Must support the `components_` attribute after fitting or be a sklearn Pipeline.
    x (list of array-like): Input text data to fit the models on. Should be a nested structure where each element contains text samples that can be flattened using np.vstack(x).ravel(). Typically a list of lists or array-like objects containing text documents. Each element should be compatible with numpy's vstack operation.
    model_is_fit (bool): Flag indicating whether models are already fitted. If True, function returns early without any fitting operations, allowing for efficient reuse of already-fitted models.

## Returns:
    None: This function does not return any value. It performs in-place fitting of models.

## Raises:
    None explicitly raised: The function handles NotFittedError exceptions internally through sklearn's check_is_fitted mechanism and doesn't propagate them.

## Constraints:
    Preconditions:
    - x should be a nested array-like structure that can be processed by np.vstack(x).ravel()
    - vmodel, if provided, should be a scikit-learn compatible vectorizer that supports the vocabulary_ attribute
    - tmodel, if provided, should be a scikit-learn compatible topic model that supports the components_ attribute or be a sklearn Pipeline
    - All models should be compatible with scikit-learn's check_is_fitted function
    
    Postconditions:
    - If vmodel is not None and not already fitted, it will be fitted on the flattened text data using vmodel.fit()
    - If tmodel is not None and not already fitted, it will be fitted on either:
      * Raw text data (for Pipeline models) using tmodel.fit()
      * Transformed text data (for regular models) using tmodel.fit(vmodel.transform())

## Side Effects:
    - Modifies the state of vmodel and tmodel in-place by fitting them if they are not already fitted
    - Performs in-place operations on the input data through np.vstack(x).ravel() to flatten nested structures
    - May cause memory allocation for intermediate flattened data structures

## Control Flow:
```mermaid
flowchart TD
    A[Start _fit_models] --> B{model_is_fit == True?}
    B -- Yes --> C[Return immediately]
    B -- No --> D[vmodel is not None?]
    D -- Yes --> E[Try check_is_fitted(vmodel)]
    E --> F{NotFittedError?}
    F -- Yes --> G[vmodel.fit(flattened_x)]
    F -- No --> H[Continue to tmodel]
    D -- No --> I[Skip vmodel fitting]
    I --> J[tmodel is not None?]
    J -- Yes --> K[Try check_is_fitted(tmodel)]
    K --> L{NotFittedError?}
    L -- Yes --> M{tmodel is Pipeline?}
    M -- Yes --> N[tmodel.fit(flattened_x)]
    M -- No --> O[tmodel.fit(vmodel.transform(flattened_x))]
    L -- No --> P[End]
    J -- No --> Q[Skip tmodel fitting]
    Q --> P[End]
```

## Examples:
    # Example 1: Fit both models with standard configuration
    vmodel = TfidfVectorizer(max_features=1000)
    tmodel = LatentDirichletAllocation(n_components=5, random_state=42)
    data = [["document1 text", "document2 text"], ["document3 text", "document4 text"]]
    _fit_models(vmodel, tmodel, data, False)
    
    # Example 2: Skip fitting when models are already fitted
    _fit_models(vmodel, tmodel, data, True)
    
    # Example 3: Fit only vectorizer
    vmodel = CountVectorizer()
    _fit_models(vmodel, None, data, False)
    
    # Example 4: Fit only topic model with pipeline
    tmodel = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('lda', LatentDirichletAllocation(n_components=3))
    ])
    _fit_models(None, tmodel, data, False)
```

## `hypertools.tools.text2mat._check_mtype` · *function*

## Summary:
Determines and returns the standardized type identifier for a given input parameter.

## Description:
This utility function examines the type of the input parameter and returns a consistent string identifier representing its type. It is designed to handle various Python data types including strings, dictionaries, classes, None values, and class instances. The function is typically used internally to validate or route input parameters based on their type.

## Args:
    x: The input parameter whose type needs to be identified. Can be of any type.

## Returns:
    str: A string identifier representing the type of the input parameter. Possible return values include:
        - 'str': Input is a string type
        - 'dict': Input is a dictionary type  
        - 'class': Input is a class object
        - 'None': Input is None
        - 'class_instance': Input is an instance of a class

## Raises:
    TypeError: Raised when the input parameter is not of type string, dict, class, or class instance. This occurs when the function cannot determine the type through its standard checks and the fallback inspection fails.

## Constraints:
    Preconditions:
        - The input parameter `x` can be of any Python type
        - No specific validation is performed on the input beyond type checking
    
    Postconditions:
        - The function always returns one of the predefined string identifiers ('str', 'dict', 'class', 'None', 'class_instance')
        - The function does not modify the input parameter

## Side Effects:
    - None: This function performs no I/O operations or external state mutations
    - No external service calls or modifications to global state

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
    
    >>> class MyClass: pass
    >>> _check_mtype(MyClass)
    'class'
    
    >>> _check_mtype(None)
    'None'
    
    >>> obj = MyClass()
    >>> _check_mtype(obj)
    'class_instance'

