# `datageometry.py`

## `hypertools.datageometry.DataGeometry` · *class*

*No documentation generated.*

### `hypertools.datageometry.DataGeometry.__init__` · *method*

## Summary:
Initializes a DataGeometry object with visualization and data processing parameters.

## Description:
The DataGeometry constructor sets up the object's state with various visualization and data transformation parameters. It handles special processing for list-type data by converting text elements and determines the data type for internal consistency.

## Args:
    fig (any, optional): Figure object for plotting. Defaults to None.
    ax (any, optional): Axes object for plotting. Defaults to None.
    line_ani (any, optional): Line animation object. Defaults to None.
    data (any, optional): Raw data to be stored. Defaults to None.
    xform_data (any, optional): Transformed data. Defaults to None.
    reduce (any, optional): Reduction configuration. Defaults to None.
    align (any, optional): Alignment configuration. Defaults to None.
    normalize (any, optional): Normalization configuration. Defaults to None.
    semantic (any, optional): Semantic processing configuration. Defaults to None.
    vectorizer (any, optional): Vectorization configuration. Defaults to None.
    corpus (any, optional): Text corpus for semantic processing. Defaults to None.
    kwargs (dict, optional): Additional keyword arguments. Defaults to None.
    version (str, optional): Version string. Defaults to __version__.
    dtype (any, optional): Explicit data type specification. Defaults to None.

## Returns:
    None: This method initializes the object's state and returns nothing.

## Raises:
    TypeError: When data of unsupported type is passed to get_dtype function.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.fig
    - self.ax  
    - self.line_ani
    - self.data
    - self.dtype
    - self.xform_data
    - self.reduce
    - self.align
    - self.normalize
    - self.semantic
    - self.vectorizer
    - self.corpus
    - self.kwargs
    - self.version

## Constraints:
    Preconditions:
    - data parameter can be None, list, numpy array, pandas DataFrame, string, or bytes
    - All other parameters are optional and can be None
    - If data is a list, it will be processed through convert_text function
    
    Postconditions:
    - All provided parameters are set as instance attributes
    - If data is a list, it is converted using convert_text function
    - self.dtype is set based on the data type using get_dtype function

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `hypertools.datageometry.DataGeometry.get_data` · *method*

*No documentation generated.*

### `hypertools.datageometry.DataGeometry.get_formatted_data` · *method*

## Summary:
Returns the data formatted into a standardized numerical representation suitable for analysis and visualization.

## Description:
This method provides access to the formatted version of the underlying data stored in the DataGeometry object. The formatting process converts various data types (text, numerical arrays, DataFrames) into a consistent numerical matrix format that can be used for downstream processing such as dimensionality reduction, alignment, and visualization. This method serves as a clean interface to access the processed data without modifying the original data stored in `self.data`.

## Args:
    None

## Returns:
    list: A list of numpy arrays representing the formatted data. Each array corresponds to a data sample or feature set, depending on the input data type. The exact structure depends on the input data types and the formatting logic in the `format_data` function.

## Raises:
    None explicitly raised, though the underlying `format_data` function may raise exceptions if the data is malformed or unsupported.

## State Changes:
    Attributes READ: self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The DataGeometry object must have been initialized with valid data.
    Postconditions: The returned data maintains the same number of samples as the original data, but in a standardized numerical format.

## Side Effects:
    None

### `hypertools.datageometry.DataGeometry.transform` · *method*

## Summary:
Transforms input data through a complete preprocessing pipeline and returns the aligned, reduced representation.

## Description:
This method applies a complete data transformation pipeline to input data, consisting of formatting, normalization, dimensionality reduction, and alignment operations. When no data is provided (data=None), it returns the previously computed transformed data stored in `self.xform_data`. When data is provided, it processes the data through the full pipeline and returns the final aligned result. This method serves as the primary interface for applying the configured transformation workflow to new datasets or retrieving cached transformations.

## Args:
    data (Any, optional): Input data to transform. Can be of various types including lists, strings, arrays, or DataGeometry objects. If None, returns cached transformed data from `self.xform_data`.

## Returns:
    Any: Transformed data after processing through the full pipeline. When data is None, returns `self.xform_data`. When data is provided, returns the result of the alignment operation from the complete transformation pipeline.

## Raises:
    None explicitly raised in the method body.

## State Changes:
    Attributes READ: 
        - self.xform_data (when data is None)
        - self.semantic
        - self.vectorizer
        - self.corpus
        - self.normalize
        - self.reduce
        - self.align
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - When data is provided, `self.reduce` must be a dictionary containing a 'params' key with an 'n_components' field
        - All required configuration attributes (semantic, vectorizer, corpus, normalize, reduce, align) must be properly initialized in the DataGeometry instance
        - The data parameter must be compatible with the format_data function's expectations
    
    Postconditions:
        - If data is None, returns `self.xform_data` unchanged
        - If data is provided, returns the result of the alignment operation from the complete transformation pipeline

## Side Effects:
    - Calls external functions from tools.format_data, tools.normalize, tools.reduce, and tools.align
    - May issue warnings during data processing (e.g., missing data warnings, alignment warnings)
    - Uses numpy operations and potentially modifies data arrays during processing

### `hypertools.datageometry.DataGeometry.plot` · *method*

*No documentation generated.*

### `hypertools.datageometry.DataGeometry.save` · *method*

## Summary:
Saves the DataGeometry object to a file in pickle format with .geo extension, temporarily clearing visualization attributes to ensure proper serialization.

## Description:
This method serializes the entire DataGeometry object to disk using Python's pickle module. It handles the special case of matplotlib figure objects that cannot be pickled by temporarily setting visualization-related attributes to None during serialization. The saved file will have a .geo extension, automatically appended if not present.

## Args:
    fname (str): Path to the output file. If the filename doesn't end with '.geo', it will be automatically appended.
    compression (None): Deprecated parameter. Has no effect on serialization behavior and will be removed in future versions.

## Returns:
    None: This method does not return any value.

## Raises:
    FutureWarning: When the deprecated compression parameter is provided.
    IOError: If the file cannot be written due to permission issues or invalid path.

## State Changes:
    Attributes READ: self.fig, self.ax, self.line_ani, self.data
    Attributes WRITTEN: self.fig, self.ax, self.line_ani, self.data (temporarily modified during serialization)

## Constraints:
    Preconditions: The DataGeometry object must be in a valid state with appropriate data and configuration.
    Postconditions: The object remains unchanged after the method call, with all attributes restored to their original values.

## Side Effects:
    I/O operation: Writes serialized object to disk at the specified file path.
    Warning: Issues a FutureWarning if the deprecated compression parameter is provided.

