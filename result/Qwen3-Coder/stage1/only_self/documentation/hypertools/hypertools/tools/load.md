# `load.py`

## `hypertools.tools.load.load` · *function*

## Summary:
Loads and optionally transforms data from either built-in example datasets or file paths, supporting legacy formats and post-processing operations.

## Description:
The load function provides unified access to both example datasets and user-provided data files. It handles automatic detection of dataset types, supports legacy file formats, and enables post-processing transformations such as dimensionality reduction, alignment, and normalization. This function serves as the primary entry point for loading data in the hypertools library, abstracting away the complexity of different data sources and processing requirements.

The function is designed to be flexible, allowing users to load data directly or apply transformations in a single operation. When transformation parameters are provided, it automatically chains the analysis and plotting steps to return a processed visualization-ready object.

## Args:
    dataset (str): Path to a data file or name of a built-in example dataset. When a path is provided, it supports environment variable expansion and tilde (~) resolution. For example datasets, valid names include 'weights', 'weights_avg', 'weights_sample', 'spiral', 'mushrooms', 'wiki', 'nips', 'sotus', 'wiki_model', 'nips_model', 'sotus_model'.
    reduce (str, optional): Dimensionality reduction technique to apply. Defaults to 'IncrementalPCA' when not specified. Common options include 'PCA', 'IncrementalPCA', 'TSNE', etc.
    ndims (int, optional): Number of dimensions for the reduced data. Required when reduce is specified.
    align (str, optional): Alignment method to apply to the data. Common options include 'Procrustes', 'GlobalAlignment', etc.
    normalize (str, optional): Normalization method to apply. Options include 'across', 'within', 'row', or False.
    legacy (bool): Flag indicating whether to attempt loading as a legacy deepdish format. Defaults to False.

## Returns:
    DataGeometry: A DataGeometry object containing the loaded data. If transformation parameters (reduce, ndims, align, normalize) are provided, returns the result of plot() which is a DataGeometry object containing visualization-ready data. If the dataset ends with '_model', returns the raw DataGeometry object without further processing.

## Raises:
    HypertoolsIOError: When a dataset cannot be found at the specified path, when a file cannot be loaded due to pickle errors, or when legacy format loading fails due to missing dependencies.

## Constraints:
    Preconditions:
    - When providing a file path, the file must exist and be readable
    - When using transformation parameters, the dataset must contain data compatible with the analysis pipeline
    - The dataset parameter must be a valid string identifying either a known example dataset or a file path
    
    Postconditions:
    - Returns a properly initialized DataGeometry object
    - If transformation parameters are used, the returned object contains processed data ready for visualization
    - If dataset is a model variant (ends with '_model'), the raw DataGeometry is returned

## Side Effects:
    - May perform file I/O operations when loading from disk
    - May download example datasets from remote sources if not cached locally
    - May create temporary directories for caching
    - May call external plotting functions that create matplotlib figures and axes

## Control Flow:
```mermaid
flowchart TD
    A[Start load] --> B{dataset in EXAMPLE_DATA?}
    B -- Yes --> C[_load_example_data(dataset)]
    C --> D{dataset ends with _model?}
    D -- Yes --> E[Return geo_data]
    D -- No --> F[Continue to transformations]
    B -- No --> G[Resolve dataset_path]
    G --> H{dataset_path.is_file()?}
    H -- No --> I[Raise HypertoolsIOError]
    I --> J[End]
    H -- Yes --> K{legacy=True?}
    K -- Yes --> L[_load_legacy(dataset_path)]
    K -- No --> M[Try pickle.loads()]
    M --> N{pickle.UnpicklingError?}
    N -- Yes --> O[Raise HypertoolsIOError]
    N -- No --> P{geo_data.data is dict?}
    P -- Yes --> Q[Convert to pd.DataFrame]
    Q --> R[Continue to transformations]
    P -- No --> R
    R --> S{Any transformation parameters?}
    S -- Yes --> T[Import plot]
    T --> U[Set reduce default]
    U --> V[Call analyze()]
    V --> W[Call plot(show=False)]
    W --> X[Return plot result]
    S -- No --> Y[Return geo_data]
```

## Examples:
```python
# Load an example dataset
data_geom = load('spiral')

# Load a file-based dataset with transformations
processed_data = load('my_data.geo', reduce='TSNE', ndims=2)

# Load legacy format dataset
legacy_data = load('old_format.geo', legacy=True)

# Load example dataset with transformations
transformed_example = load('wiki', reduce='PCA', ndims=3, normalize='across')

# Load model variant of example dataset
model_data = load('wiki_model')
```

## `hypertools.tools.load._load_legacy` · *function*

## Summary:
Loads legacy-format datasets saved with deepdish and converts them into a standardized DataGeometry object for use with hypertools analysis and visualization workflows.

## Description:
This internal utility function is responsible for loading datasets that were previously saved in the legacy deepdish format. It handles the specific data type conversions required to ensure compatibility with the modern DataGeometry class structure. The function is called internally when loading legacy datasets and should not be used directly by end users.

The function specifically processes the 'data' field by converting dictionary-based data to pandas DataFrames and numpy array-based data to lists, while ensuring the 'xform_data' field is consistently formatted as a list. This normalization ensures that legacy datasets can be seamlessly integrated into the current hypertools pipeline.

## Args:
    dataset_path (str): Absolute or relative path to the legacy-format dataset file saved with deepdish

## Returns:
    DataGeometry: A DataGeometry object containing the loaded data and associated metadata, properly formatted for use with hypertools analysis and visualization functions

## Raises:
    HypertoolsIOError: When the 'deepdish' module is not installed, preventing loading of legacy-format datasets

## Constraints:
    Preconditions:
    - The dataset_path must point to a valid file containing data saved in legacy deepdish format
    - The file must contain a dictionary structure with 'data' and 'xform_data' keys
    - The 'data' key must contain either a dictionary, numpy array, or list-like structure
    - The 'xform_data' key must contain data that can be converted to a list

    Postconditions:
    - The returned DataGeometry object will have properly formatted data fields
    - The 'data' field will be either a pandas DataFrame or list
    - The 'xform_data' field will be a list

## Side Effects:
    - Reads data from the filesystem at the specified dataset_path
    - Dynamically imports the deepdish module when the function is called

## Control Flow:
```mermaid
flowchart TD
    A[Start _load_legacy] --> B[Try to import deepdish as dd]
    B --> C{Import successful?}
    C -- No --> D[Raise HypertoolsIOError]
    C -- Yes --> E[Load dataset with dd.io.load(dataset_path)]
    E --> F{data field is dict?}
    F -- Yes --> G[Convert data to pd.DataFrame]
    F -- No --> H{data field is ndarray?}
    H -- Yes --> I[Convert data to list]
    H -- No --> J[Keep data as-is]
    G --> K[Set data field]
    I --> K
    J --> K
    K --> L[Convert xform_data to list]
    L --> M[Create DataGeometry(**data_dict)]
    M --> N[Return DataGeometry]
```

## Examples:
```python
# This function is typically called internally by hypertools
# when loading legacy datasets, not directly by users

# Example of expected legacy dataset structure:
# {
#     'data': {'feature1': [1, 2, 3], 'feature2': [4, 5, 6]},  # dict case
#     'xform_data': [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]      # list case
# }
```

## `hypertools.tools.load._load_example_data` · *function*

## Summary:
Loads cached example datasets with automatic download and processing for specific dataset types.

## Description:
This private utility function retrieves example datasets from a local cache directory, automatically downloading them from Google Drive if they don't exist locally. It handles dataset-specific post-processing for certain datasets like 'mushrooms' and provides robust error handling for corrupted cache files.

The function implements a lazy-loading pattern where datasets are downloaded only when first requested and cached locally for subsequent access. It specifically processes the 'mushrooms' dataset by converting its raw data to a pandas DataFrame, ensuring consistent data representation across the library.

## Args:
    dataset (str): Name of the example dataset to load. This corresponds to a key in the EXAMPLE_DATA mapping used by _download_example_data.

## Returns:
    DataGeometry: A DataGeometry object containing the loaded dataset with appropriate data formatting and metadata. For the 'mushrooms' dataset, the data attribute will be a pandas DataFrame.

## Raises:
    HypertoolsIOError: When the cached dataset file cannot be loaded due to corruption or when download fails. Provides guidance to manually delete the cached file and reload.

## Constraints:
    Preconditions:
    - The dataset parameter must be a valid string that exists as a key in the EXAMPLE_DATA global mapping
    - The DATA_DIR must be accessible for file operations
    - The _download_example_data function must be available and properly configured
    - The pandas module must be imported as 'pd'
    
    Postconditions:
    - If successful, returns a DataGeometry object with the dataset loaded
    - If dataset is 'mushrooms', the returned object's data attribute will be a pandas DataFrame
    - The dataset will be cached in the DATA_DIR for future access

## Side Effects:
    - Creates directories in the filesystem if they don't exist (DATA_DIR)
    - Downloads files from Google Drive when datasets are not cached locally
    - Reads binary files from the filesystem for cached datasets
    - May delete partially downloaded files if download fails

## Control Flow:
```mermaid
flowchart TD
    A[Start _load_example_data] --> B[Construct dataset_path from DATA_DIR and dataset]
    B --> C{dataset_path.is_file()?}
    C -- No --> D{DATA_DIR.is_dir()?}
    D -- No --> E[Create DATA_DIR directory]
    E --> F[_download_example_data(dataset_path)]
    C -- Yes --> F
    F --> G[Read dataset file bytes]
    G --> H[Try pickle.loads()]
    H --> I{Exception raised?}
    I -- Yes --> J[Raise HypertoolsIOError]
    I -- No --> K{dataset == 'mushrooms'?}
    K -- Yes --> L[Convert geo_data.data to pd.DataFrame]
    K -- No --> M[Return geo_data]
    L --> M
```

## Examples:
```python
# Load an example dataset
from hypertools.tools.load import _load_example_data

# Load the mushrooms dataset (will be converted to DataFrame)
mushrooms_data = _load_example_data('mushrooms')

# Load another example dataset
iris_data = _load_example_data('iris')
```

## `hypertools.tools.load._download_example_data` · *function*

## Summary:
Downloads example datasets from Google Drive by resolving dataset names to file IDs and streaming content to disk.

## Description:
This private utility function handles the downloading of example datasets from Google Drive. It resolves dataset names to corresponding file IDs using a predefined mapping, makes authenticated requests to Google Drive's download endpoint, and properly handles Google Drive's download confirmation warnings. The function streams content in chunks to efficiently manage memory usage for potentially large files.

## Args:
    dataset_path (Path): A pathlib.Path object pointing to the location where the downloaded dataset should be saved. The filename portion of the path is used as a key to look up the corresponding Google Drive file ID in the EXAMPLE_DATA mapping.

## Returns:
    None: This function does not return any value. It saves the downloaded content directly to the specified file path.

## Raises:
    HypertoolsIOError: Raised when the download fails for any reason, including network errors, invalid file IDs, or failed HTTP requests. The partial file is automatically cleaned up when this exception occurs.

## Constraints:
    Preconditions:
    - The dataset_path must be a valid pathlib.Path object
    - The dataset_path.name must exist as a key in the EXAMPLE_DATA global constant
    - The BASE_URL global constant must be defined and point to Google Drive's download endpoint
    - The EXAMPLE_DATA global constant must be a dictionary mapping dataset names to Google Drive file IDs
    
    Postconditions:
    - If successful, the file at dataset_path will contain the downloaded dataset content
    - If unsuccessful, the file at dataset_path will not exist (partial downloads are cleaned up)

## Side Effects:
    - Makes HTTP requests to Google Drive using the requests library
    - Writes data to the filesystem at the location specified by dataset_path
    - May delete a file if download fails (partial downloads are removed)

## Control Flow:
```mermaid
flowchart TD
    A[Start _download_example_data] --> B{dataset_path.name in EXAMPLE_DATA?}
    B -- No --> C[Raise error]
    B -- Yes --> D[Get file_id from EXAMPLE_DATA]
    D --> E[Create requests.Session()]
    E --> F[Set params with file_id]
    F --> G[Make GET request to BASE_URL]
    G --> H{Response contains download_warning cookie?}
    H -- Yes --> I[Extract confirm token from cookie]
    I --> J[Update params with confirm token]
    J --> K[Make second GET request with confirm token]
    K --> L[Open dataset_path for writing in binary mode]
    L --> M[Iterate through response content chunks]
    M --> N{Chunk is not empty?}
    N -- Yes --> O[Write chunk to file]
    N -- No --> P[Skip empty chunk]
    O --> M
    P --> Q[Close file handle]
    Q --> R[Return success]
    H -- No --> L
    G --> S{Request successful?}
    S -- No --> T[Delete partial file]
    T --> U[Raise HypertoolsIOError]
```

## Examples:
```python
# Typical usage would be within a larger dataset loading function
from pathlib import Path
from hypertools.tools.load import _download_example_data

# Download a dataset to a specific location
dataset_path = Path.home() / "datasets" / "example_dataset.h5"
_download_example_data(dataset_path)
```

