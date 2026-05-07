# `cluster.py`

## `hypertools.tools.cluster.cluster` · *function*

## Summary:
Performs clustering on input data using various clustering algorithms with flexible configuration options.

## Description:
This function provides a unified interface for applying different clustering algorithms to input data. It supports string-based specification of clustering methods (like 'KMeans', 'HDBSCAN') or dictionary-based configuration for more detailed control. The function handles preprocessing of data and manages special cases like HDBSCAN installation requirements.

## Args:
    x (array-like): Input data to be clustered, typically a list of arrays or matrix
    cluster (str or dict, optional): Clustering algorithm to use. Can be a string name ('KMeans', 'HDBSCAN', etc.) or a dictionary with 'model' and 'params' keys. Defaults to 'KMeans'.
    n_clusters (int, optional): Number of clusters to form. Used when cluster is a string and not HDBSCAN. Defaults to 3.
    ndims (int, optional): Deprecated parameter for dimensionality reduction. Defaults to None.
    format_data (bool, optional): Whether to preprocess input data using formatter function. Defaults to True.

## Returns:
    list[int]: Cluster labels for each data point in the input, represented as integers

## Raises:
    ImportError: When HDBSCAN is requested but not installed (hdbscan package missing)

## Constraints:
    Preconditions:
        - Input data `x` should be compatible with numpy array operations
        - If cluster is a string, it must be a valid key in the models dictionary
        - If cluster is a dict, it must contain a 'model' key with a valid model name
    Postconditions:
        - Returns a list of integer cluster labels matching the length of input data
        - Input data remains unchanged

## Side Effects:
    - Issues a warning when ndims parameter is used (deprecated)
    - May raise ImportError if HDBSCAN is requested but not installed
    - Calls formatter function for data preprocessing if format_data=True

## Control Flow:
```mermaid
flowchart TD
    A[Start cluster function] --> B{cluster == None?}
    B -- Yes --> C[Return x unchanged]
    B -- No --> D{cluster is HDBSCAN?}
    D -- Yes --> E{HDBSCAN installed?}
    E -- No --> F[ImportError]
    E -- Yes --> G[Continue]
    D -- No --> G
    G --> H{format_data?}
    H -- Yes --> I[Apply formatter]
    H -- No --> J[Skip formatting]
    J --> K{cluster type}
    K --> L{String cluster}
    L --> M[Get model from models dict]
    M --> N{Is HDBSCAN?}
    N -- No --> O[Set n_clusters param]
    N -- Yes --> P[Set empty params]
    O --> Q[Create model instance]
    P --> Q
    L --> Q
    K --> R{Dict cluster}
    R --> S[Get model from models dict]
    S --> T[Use params from dict]
    T --> U[Create model instance]
    Q --> V[Fit model on data]
    U --> V
    V --> W[Return cluster labels]
```

## Examples:
    # Basic KMeans clustering
    labels = cluster(data, cluster='KMeans', n_clusters=4)
    
    # Using HDBSCAN clustering
    labels = cluster(data, cluster='HDBSCAN')
    
    # Custom clustering with parameters
    custom_cluster = {'model': 'KMeans', 'params': {'n_clusters': 5, 'random_state': 42}}
    labels = cluster(data, cluster=custom_cluster)
    
    # Skip data formatting
    labels = cluster(data, format_data=False)

