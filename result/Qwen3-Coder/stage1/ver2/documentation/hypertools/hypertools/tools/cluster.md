# `cluster.py`

## `hypertools.tools.cluster.cluster` · *function*

## Summary:
Performs clustering on input data using various clustering algorithms with flexible configuration options.

## Description:
This function provides a unified interface for applying different clustering algorithms to input data. It supports multiple clustering methods through string identifiers or detailed configuration dictionaries, automatically handles preprocessing, and returns cluster labels for each data point. The function is designed to be flexible and extensible for various clustering needs while maintaining consistent input/output behavior.

## Args:
    x (array-like): Input data to be clustered, typically a list of arrays or matrix
    cluster (str or dict, optional): Clustering algorithm specification. Can be a string name like 'KMeans' or a dictionary with 'model' and 'params' keys. Defaults to 'KMeans'
    n_clusters (int, optional): Number of clusters to form. Used when cluster is a string or when HDBSCAN is not used. Defaults to 3
    ndims (int, optional): Deprecated parameter for dimensionality reduction. Currently ignored with warning. Defaults to None
    format_data (bool, optional): Whether to apply preprocessing formatting to input data. Defaults to True

## Returns:
    list[int]: Cluster labels for each data point in the input dataset. Labels are integers starting from 0.

## Raises:
    ImportError: When HDBSCAN is specified but not installed (hdbscan package missing)

## Constraints:
    Preconditions:
    - Input data `x` should be compatible with numpy array operations
    - If `cluster` is a string, it must correspond to a valid model name in the internal models mapping
    - If `cluster` is a dict, it must contain a 'model' key with a valid model name
    
    Postconditions:
    - Returns a list of integer cluster labels matching the length of input data
    - Input data remains unchanged
    - No side effects on global state

## Side Effects:
    - Issues a deprecation warning when `ndims` parameter is provided
    - Calls the formatter function from _shared.helpers for data preprocessing
    - May raise ImportError if HDBSCAN is requested but not installed

## Control Flow:
```mermaid
flowchart TD
    A[Start cluster function] --> B{cluster == None?}
    B -- Yes --> C[Return x unchanged]
    B -- No --> D{cluster is HDBSCAN?}
    D -- Yes --> E{hdbscan installed?}
    E -- No --> F[ImportError]
    E -- Yes --> G[Continue]
    D -- No --> G
    G --> H{format_data?}
    H -- Yes --> I[Apply formatter with ppca=True]
    H -- No --> J[Skip formatting]
    J --> K{cluster type}
    K --> L{String cluster}
    L --> M[Get model from models dictionary]
    M --> N{Is HDBSCAN?}
    N -- No --> O[Set n_clusters param]
    N -- Yes --> P[Set empty params]
    O --> Q[Create model instance]
    P --> Q
    L --> Q
    K --> R{Dict cluster}
    R --> S[Get model from models dictionary]
    S --> T[Use params from dict]
    T --> U[Create model instance]
    Q --> V[Fit model on np.vstack(x)]
    U --> V
    V --> W[Return model.labels_ as list]
```

## Examples:
```python
# Basic KMeans clustering with default settings
labels = cluster(data)

# Specify number of clusters
labels = cluster(data, n_clusters=5)

# Use different clustering algorithm
labels = cluster(data, cluster='AgglomerativeClustering')

# Use HDBSCAN clustering
labels = cluster(data, cluster='HDBSCAN')

# Use custom parameters via dictionary
custom_cluster = {'model': 'KMeans', 'params': {'n_clusters': 4, 'random_state': 42}}
labels = cluster(data, cluster=custom_cluster)
```

