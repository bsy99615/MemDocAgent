# `datageometry.py`

## `hypertools.datageometry.DataGeometry` · *class*

## Summary:
DataGeometry is a container class that manages data transformations, visualizations, and associated metadata for high-dimensional data analysis and plotting.

## Description:
The DataGeometry class serves as a central data structure for the hypertools library, encapsulating both raw data and transformed data along with all relevant configuration parameters needed for visualization and analysis. It provides methods for data transformation, plotting, and persistence while maintaining the state of visualization components like matplotlib figures and axes.

This class acts as a stateful wrapper around data processing pipelines, allowing users to chain transformations and visualizations while preserving intermediate results and configuration. It's designed to work with the broader hypertools ecosystem for analyzing and visualizing complex datasets, particularly those involving text data and high-dimensional representations.

## State:
- fig: matplotlib figure object or None - The matplotlib figure associated with the visualization
- ax: matplotlib axes object or None - The matplotlib axes associated with the visualization  
- line_ani: animation object or None - Animation handler for animated plots
- data: array-like or list - Raw input data, potentially converted to standardized format using convert_text for list inputs
- dtype: str - Data type identifier (list, arr, df, str, geo) determined by get_dtype function
- xform_data: array-like or None - Transformed data ready for visualization
- reduce: dict or None - Configuration for dimensionality reduction, typically containing 'model' and 'params' keys
- align: dict or None - Configuration for data alignment, typically containing 'model' and 'params' keys
- normalize: str or None - Normalization method specification ('across', 'within', 'row', False, None)
- semantic: str or None - Semantic modeling approach for text data (e.g., 'LatentDirichletAllocation')
- vectorizer: str or None - Text vectorization method (e.g., 'CountVectorizer')
- corpus: str or None - Corpus used for semantic modeling (e.g., 'wiki')
- kwargs: dict or None - Additional plotting parameters passed to the plotting backend
- version: str - Version of the hypertools library used

## Lifecycle:
Creation: Instantiate with optional parameters including data, transformation configurations, and plotting components. Data undergoes preprocessing including text conversion via convert_text for list inputs and dtype determination via get_dtype.

Usage: Typically used in a workflow where data is first transformed using the transform() method, then visualized using the plot() method. The get_data() method provides access to the raw data (copy), while get_formatted_data() returns the data in a format suitable for further processing. The transform() method can operate on either internal data or external data provided as an argument.

Destruction: The save() method allows persistent storage of the entire DataGeometry object, including its state and configuration. The class implements proper cleanup during save operations to ensure serialization compatibility by temporarily setting figure/axes objects to None during pickling.

## Method Map:
```mermaid
flowchart TD
    A[DataGeometry.__init__] --> B[get_dtype(data)]
    A --> C[convert_text(data) if data is list]
    B --> D[Set self.dtype]
    C --> D
    
    E[DataGeometry.transform] --> F{data is None?}
    F -- Yes --> G[Return self.xform_data]
    F -- No --> H[format_data()]
    H --> I[normalize()]
    I --> J[reduce()]
    J --> K[align()]
    K --> L[Return aligned data]
    
    M[DataGeometry.plot] --> N{data is None?}
    N -- Yes --> O[Use self.data and self.xform_data]
    N -- No --> P[Use external data]
    O --> Q[Prepare kwargs with defaults]
    P --> Q
    Q --> R[plot()]
    R --> S[Return new DataGeometry]
    
    T[DataGeometry.save] --> U[pickle.dump()]
    U --> V[Temporarily set fig/ax/line_ani to None]
    V --> W[Serialize self]
    W --> X[Restore fig/ax/line_ani]
```

## Raises:
- TypeError: Raised by get_dtype() when input data type is not supported
- ValueError: Raised by various transformation functions when invalid parameters are provided
- NotImplementedError: Not explicitly raised but could occur from underlying tools

## Example:
```python
# Create a DataGeometry object with sample data
data = ["This is sample text", "Another piece of text"]
geom = DataGeometry(data=data)

# Transform the data (operates on internal data)
transformed = geom.transform()

# Transform with external data
external_data = ["New text data", "More text"]
transformed_external = geom.transform(data=external_data)

# Plot the data
plot_geom = geom.plot()

# Save the object
geom.save('my_data.geo')
```

### `hypertools.datageometry.DataGeometry.__init__` · *method*

## Summary:
Initializes a DataGeometry object with configuration parameters and preprocesses input data.

## Description:
The DataGeometry constructor creates a new instance with the specified configuration parameters. It handles special preprocessing for list-type data by converting text entries using the convert_text helper function, and determines the data type using get_dtype. This method serves as the entry point for creating DataGeometry objects that encapsulate data along with transformation and visualization configurations.

## Args:
    fig (matplotlib.figure.Figure or None, optional): Matplotlib figure object for visualization. Defaults to None.
    ax (matplotlib.axes.Axes or None, optional): Matplotlib axes object for visualization. Defaults to None.
    line_ani (object or None, optional): Animation handler for animated plots. Defaults to None.
    data (array-like or list, optional): Raw input data. If a list, text entries are converted using convert_text. Defaults to None.
    xform_data (array-like or None, optional): Pre-transformed data ready for visualization. Defaults to None.
    reduce (dict or None, optional): Configuration for dimensionality reduction. Defaults to None.
    align (dict or None, optional): Configuration for data alignment. Defaults to None.
    normalize (str or None, optional): Normalization method specification. Defaults to None.
    semantic (str or None, optional): Semantic modeling approach for text data. Defaults to None.
    vectorizer (str or None, optional): Text vectorization method. Defaults to None.
    corpus (str or None, optional): Corpus used for semantic modeling. Defaults to None.
    kwargs (dict or None, optional): Additional plotting parameters. Defaults to None.
    version (str, optional): Version of the hypertools library. Defaults to __version__.
    dtype (str or None, optional): Data type identifier. If provided, skips automatic type detection. Defaults to None.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    TypeError: Raised by get_dtype() when input data type is not supported.
    TypeError: Raised by convert_text() when input data type is not supported.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self.fig: Set to the provided fig parameter
        - self.ax: Set to the provided ax parameter  
        - self.line_ani: Set to the provided line_ani parameter
        - self.data: Set to the provided data parameter, with text conversion applied if data is a list
        - self.dtype: Set to the result of get_dtype(data)
        - self.xform_data: Set to the provided xform_data parameter
        - self.reduce: Set to the provided reduce parameter
        - self.align: Set to the provided align parameter
        - self.normalize: Set to the provided normalize parameter
        - self.semantic: Set to the provided semantic parameter
        - self.vectorizer: Set to the provided vectorizer parameter
        - self.corpus: Set to the provided corpus parameter
        - self.kwargs: Set to the provided kwargs parameter
        - self.version: Set to the provided version parameter

## Constraints:
    Preconditions:
        - All parameters must be of appropriate types for their intended use
        - If data is provided as a list, all elements should be compatible with convert_text function
        - If dtype is provided, it must be one of the supported type identifiers ('list', 'arr', 'df', 'str', 'geo')

    Postconditions:
        - All provided parameters are stored as instance attributes
        - If data is a list, it is processed through convert_text before storage
        - self.dtype is set to the appropriate data type identifier

## Side Effects:
    None: This method performs no I/O operations or external state mutations. It only sets instance attributes.

### `hypertools.datageometry.DataGeometry.get_formatted_data` · *method*

## Summary:
Returns formatted data ready for downstream processing by applying standard formatting transformations to the stored data.

## Description:
This method provides access to the formatted version of the data stored in the DataGeometry object. It serves as a clean interface to retrieve pre-processed data that has been normalized and transformed into a consistent format suitable for analysis and visualization. The method is typically called during data transformation pipelines or when preparing data for plotting operations.

## Args:
    None

## Returns:
    list: A list of formatted data arrays that have been processed through the standard format_data pipeline. The exact structure depends on the input data type but generally contains numerical arrays ready for machine learning or visualization operations.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The DataGeometry object must have been initialized with valid data in self.data
    Postconditions: Returns a list of formatted data arrays that are ready for downstream processing

## Side Effects:
    None

### `hypertools.datageometry.DataGeometry.transform` · *method*

## Summary:
Transforms input data through a standardized pipeline of formatting, normalization, dimensionality reduction, and alignment, or returns previously transformed data.

## Description:
This method applies a complete data transformation pipeline to input data, or returns cached transformed data if no new data is provided. The pipeline consists of formatting raw data into numerical representations, normalizing the data, reducing dimensionality, and finally aligning the data across different datasets. This method serves as the primary interface for applying the full preprocessing and transformation workflow to new data.

When no data is provided (data=None), this method returns the cached transformed data stored in self.xform_data. When data is provided, it processes the data through the full pipeline: format_data → normalize → reduce → align.

## Args:
    data (list, optional): Input data to transform. If None, returns cached transformed data (self.xform_data). Defaults to None.

## Returns:
    list: Transformed data after formatting, normalization, dimensionality reduction, and alignment. When data is None, returns self.xform_data. When data is provided, returns the aligned result of the transformation pipeline.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.xform_data, self.semantic, self.vectorizer, self.corpus, self.normalize, self.reduce, self.align
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - When data is provided, self.reduce must contain a 'params' dictionary with 'n_components' key
    - All required attributes (semantic, vectorizer, corpus, normalize, reduce, align) must be properly initialized in the DataGeometry instance
    - Input data must be compatible with the format_data function
    Postconditions:
    - When data is None, returns self.xform_data unchanged
    - When data is provided, returns the result of the full transformation pipeline

## Side Effects:
    None

### `hypertools.datageometry.DataGeometry.plot` · *method*

## Summary:
Plots data using stored configuration parameters and optional external data, returning a new DataGeometry object with plotting results.

## Description:
This method provides plotting functionality for DataGeometry objects. It can either plot the internal data stored in the object or accept external data to visualize. The method prepares appropriate parameters by combining class-level configuration with any override parameters provided via kwargs, then delegates to the underlying plotting function.

## Args:
    data (array-like, optional): External data to plot. If None, uses internal self.data. Defaults to None.
    **kwargs: Additional plotting parameters that override class-level settings. Common parameters include reduce, align, normalize, semantic, vectorizer, and corpus.

## Returns:
    DataGeometry: A new DataGeometry object containing the plotting results, including figure, axes, and transformed data.

## Raises:
    None explicitly raised by this method. Exceptions may be raised by the delegated plot function.

## State Changes:
    Attributes READ: self.data, self.xform_data, self.kwargs, self.reduce, self.align, self.normalize, self.semantic, self.vectorizer, self.corpus
    Attributes WRITTEN: None (this method doesn't modify instance state)

## Constraints:
    Preconditions: 
    - The object must be properly initialized with required attributes
    - If data is provided, it must be compatible with the underlying plotting functions
    - The plot function must be able to process the data and parameters
    
    Postconditions:
    - Returns a new DataGeometry object with plotting results
    - Original object state remains unchanged

## Side Effects:
    - Calls external plotting functions which may perform I/O operations
    - May create matplotlib figures and axes
    - May save files if save_path is specified in kwargs

### `hypertools.datageometry.DataGeometry.save` · *method*

## Summary:
Saves the DataGeometry object to a file in pickle format with .geo extension, temporarily clearing visualization attributes during serialization.

## Description:
This method serializes the entire DataGeometry object to a file using Python's pickle module. It handles the special case of pandas DataFrame data by converting it to a dictionary format before saving. The method temporarily sets visualization-related attributes (fig, ax, line_ani) to None during serialization to avoid issues with pickling matplotlib objects, then restores them afterward.

## Args:
    fname (str): Path to the output file. If no .geo extension is provided, it will be added automatically.
    compression (None): Deprecated parameter. Has no effect on serialization behavior and will be removed in future versions.

## Returns:
    None: This method does not return any value.

## Raises:
    None explicitly raised: The method does not raise any exceptions directly, though file I/O operations may raise IOError or OSError if the file cannot be written.

## State Changes:
    Attributes READ: self.fig, self.ax, self.line_ani, self.data
    Attributes WRITTEN: self.fig, self.ax, self.line_ani, self.data (temporarily modified during serialization)

## Constraints:
    Preconditions: The DataGeometry object must be properly initialized with valid data and attributes.
    Postconditions: The object remains unchanged after the method call except for temporary attribute modifications during serialization.

## Side Effects:
    I/O: Writes binary data to the specified file path using pickle serialization.
    Temporary attribute modification: Sets fig, ax, line_ani to None and data to dictionary format during serialization process.

