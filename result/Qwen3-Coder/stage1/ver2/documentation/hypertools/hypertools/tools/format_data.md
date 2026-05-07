# `format_data.py`

## `hypertools.tools.format_data.format_data` · *function*

## Summary:
Processes mixed-type data inputs (text, numerical, dataframe, geometric) into standardized numerical matrix representations suitable for visualization and analysis.

## Description:
Converts heterogeneous data inputs into uniform numerical matrices by applying appropriate transformations based on data type. This function handles complex data preprocessing including text vectorization, numerical matrix conversion, missing data imputation with PPCA, and cross-modal data alignment. It serves as a central preprocessing step that standardizes diverse data formats into a common numerical representation that can be used by downstream visualization and analysis tools.

Known callers within the codebase:
- Called by `DataGeometry.transform()` in `hypertools/datageometry.py` during the data processing pipeline
- Triggered when users provide mixed-type data to hypertools functions that require standardized numerical input

This logic is extracted into its own function rather than being inlined because it encapsulates complex data type detection, transformation, and preprocessing logic that needs to be reused across different parts of the library. It provides a clean separation between data input handling and visualization/analysis operations.

## Args:
    x (any): Input data that can be a single item or list of items. Supports various data types including strings, lists of strings, numerical data, pandas DataFrames, and DataGeometry objects.
    vectorizer (str, optional): Text vectorization method to use for text data processing. Defaults to 'CountVectorizer'.
    semantic (str, optional): Semantic modeling method to use for text data processing. Defaults to 'LatentDirichletAllocation'.
    corpus (str, optional): Pre-defined corpus to use for semantic modeling. Defaults to 'wiki'.
    ppca (bool, optional): Whether to apply PPCA for missing data imputation. Defaults to True.
    text_align (str, optional): Alignment method to use when combining text and numerical data. Defaults to 'hyper'.

## Returns:
    list: A list of numpy arrays representing the processed data in standardized numerical format. Each element corresponds to the processed version of the respective input item, maintaining the original structure and ordering.

## Raises:
    None explicitly raised in the function body, though underlying functions may raise exceptions.

## Constraints:
    Preconditions:
    - Input data must be compatible with the `get_type` function for classification
    - Text data must be convertible to numpy arrays
    - Numerical data must be compatible with numpy operations
    - When using alignment, all input datasets must have the same number of samples
    
    Postconditions:
    - All returned arrays are numpy arrays with consistent numerical representation
    - Text data is converted to numerical matrices using specified vectorization and semantic methods
    - Numerical data is converted to proper matrix format
    - Missing values in numerical data are handled via PPCA when applicable
    - Cross-modal data is aligned when both text and numerical data are present with matching sample counts

## Side Effects:
    - Issues warnings via Python warnings module for missing data handling and data alignment
    - May perform I/O operations when loading pre-trained models from corpora
    - Modifies global dictionaries when user-provided models are used (via text2mat)
    - Calls external functions that may have their own side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start format_data] --> B{Input is not list?}
    B -- Yes --> C[Wrap input in list]
    B -- No --> D[Continue]
    C --> D
    D --> E{All elements are strings?}
    E -- Yes --> F[Wrap entire input in list]
    E -- No --> G[Continue]
    F --> G
    G --> H[Get data types for all elements]
    H --> I{Contains text data?}
    I -- Yes --> J[Prepare text processing args]
    J --> K[Collect text data elements]
    K --> L[Convert text data to matrices]
    I -- No --> M[Skip text processing]
    L --> M
    M --> N[Process each element by type]
    N --> O{Element is text?}
    O -- Yes --> P[Use precomputed text matrix]
    O -- No --> Q{Element is DataFrame?}
    Q -- Yes --> R[Convert with df2mat]
    Q -- No --> S{Element is DataGeometry?}
    S -- Yes --> T[Recursively process get_data()]
    S -- No --> U[Use original data]
    P --> V[Add to processed_x]
    R --> V
    T --> V
    U --> V
    V --> W[Ensure all arrays are 2D]
    W --> X[Check for text and numerical data presence]
    X --> Y{ppca enabled AND contains numerical data?}
    Y -- Yes --> Z{Any missing data?}
    Z -- Yes --> AA[Apply PPCA to fill missing data]
    Z -- No --> AB[Skip missing data handling]
    AA --> AC[Update processed_x with filled data]
    AB --> AC
    AC --> AD{Contains both text and numerical data?}
    AD -- Yes --> AE{All arrays have same sample count?}
    AE -- Yes --> AF[Align data using specified method]
    AE -- No --> AG[Skip alignment]
    AF --> AH[Return aligned processed data]
    AG --> AH
    AD -- No --> AH
    AH --> I[Return processed_x]
```

## Examples:
```python
# Basic usage with text data
import hypertools as hp
text_data = ["This is sample text", "Another piece of text"]
processed = hp.format_data(text_data)

# Mixed data types
import pandas as pd
import numpy as np
df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
num_data = np.array([[1, 2], [3, 4], [5, 6]])
mixed_data = [df, num_data, "Some text"]
processed = hp.format_data(mixed_data)

# With custom parameters
processed = hp.format_data(text_data, vectorizer='TfidfVectorizer', semantic='NMF')
```

## `hypertools.tools.format_data.fill_missing` · *function*

## Summary:
Fills missing values in data arrays using Probabilistic Principal Component Analysis (PPCA) and preserves the original data structure.

## Description:
This function applies Probabilistic Principal Component Analysis to impute missing values in datasets while maintaining the original structure of input data arrays. It is particularly useful for handling datasets with missing observations that need dimensionality reduction or further analysis.

The function processes input data by:
1. Stacking all input arrays vertically
2. Applying PPCA to learn the underlying structure and impute missing values
3. Identifying rows with all NaN values and preserving them as NaN in the transformed space
4. Returning results in the same structure as the input

This logic is extracted into a separate function to encapsulate the complex PCA-based missing value imputation process and maintain clean separation between data preprocessing and downstream analysis pipelines.

## Args:
    x (list): A list of numpy arrays or matrices that may contain missing values (represented as np.nan). Each element in the list represents a separate data block that should be processed together but maintained separately in the output.

## Returns:
    list: A list of numpy arrays with missing values filled using PPCA. If the input contains multiple arrays, the output maintains the same number of arrays with the same shapes. If the input contains a single array, returns a list with one element containing the filled array.

## Raises:
    None explicitly raised by this function, though underlying PPCA operations may raise RuntimeError if improperly configured.

## Constraints:
    Preconditions:
    - Input `x` must be a list of numpy arrays/matrices
    - Arrays in the list should be compatible for vertical stacking (same number of columns)
    
    Postconditions:
    - Output arrays will have the same shape as input arrays
    - Missing values in input arrays are replaced with imputed values
    - Rows with all NaN values in input are preserved as all NaN in output

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start fill_missing(x)] --> B[Stack input arrays with np.vstack(x)]
    B --> C[Initialize PPCA model]
    C --> D[Fit PPCA on stacked data]
    D --> E[Transform data with PPCA]
    E --> F[Find indices of rows with all NaN values]
    F --> G{Any all-NaN rows?}
    G -->|Yes| H[Set corresponding positions in PCA result to NaN]
    H --> I[Calculate split points for multiple arrays]
    I --> J{Multiple input arrays?}
    J -->|Yes| K[Split PCA result back into original structure]
    J -->|No| L[Return single PCA result]
    K --> M[Return split results]
    L --> M
    M --> N[End]
```

## Examples:
```python
import numpy as np
from hypertools.tools.format_data import fill_missing

# Example 1: Single array with missing values
data1 = np.array([[1, 2, np.nan], [4, 5, 6], [7, np.nan, 9]])
filled_data1 = fill_missing([data1])
print(filled_data1[0])

# Example 2: Multiple arrays with missing values
data2 = np.array([[1, 2], [3, 4]])
data3 = np.array([[np.nan, 6], [7, 8]])
filled_data2 = fill_missing([data2, data3])
print(filled_data2[0])  # First array with imputed values
print(filled_data2[1])  # Second array with imputed values
```

