# `cluster.py`

## `hypertools.tools.cluster.cluster` · *function*

## Summary:
Applies clustering to input data using various clustering algorithms with optional preprocessing.

## Description:
This function performs clustering on input data using different algorithms specified by the cluster parameter. It supports multiple clustering methods including KMeans, HDBSCAN, and others from scikit-learn. The function can optionally format the input data before clustering and handles special cases like returning the original data when cluster is None.

## Args:
    x (array-like): Input data to be clustered
    cluster (str or dict, optional): Clustering algorithm to use. Can be a string name of algorithm or a dictionary with 'model' and 'params' keys. Defaults to 'KMeans'.
    n_clusters (int, optional): Number of clusters for algorithms that require it. Defaults to 3.
    ndims (int, optional): Deprecated parameter for dimensionality reduction. Defaults to None.
    format_data (bool, optional): Whether to format input data before clustering. Defaults to True.

## Returns:
    list: Cluster labels for each data point in the input. Each label is an integer representing the cluster assignment. Returns the original input data unchanged if cluster is None.

## Raises:
    ImportError: When HDBSCAN is requested but not installed

## Constraints:
    Preconditions:
    - Input data x should be compatible with the chosen clustering algorithm
    - If cluster is a dictionary, it must contain a 'model' key with a valid algorithm name
    - If cluster is a string, it must be a valid key in the models dictionary
    
    Postconditions:
    - Returns a list of integer cluster labels corresponding to each input data point
    - If cluster is None, returns the original input data unchanged

## Side Effects:
    - Issues a warning when ndims parameter is used (deprecated)
    - May raise ImportError if HDBSCAN is requested but not available

## Control Flow:
```mermaid
flowchart TD
    A[Start cluster function] --> B{cluster == None?}
    B -- Yes --> C[Return x]
    B -- No --> D{cluster is HDBSCAN?}
    D -- Yes --> E{hdbscan installed?}
    E -- No --> F[ImportError]
    E -- Yes --> G[Continue]
    D -- No --> G
    G --> H{format_data?}
    H -- Yes --> I[Apply formatter]
    H -- No --> J[Skip formatting]
    J --> K{cluster type}
    K --> L{cluster is str?}
    L -- Yes --> M[Get model from models dict]
    L -- No --> N[Get model from cluster['model']]
    M --> O{cluster == 'HDBSCAN'?}
    O -- No --> P[Set n_clusters param]
    O -- Yes --> Q[Set empty params]
    N --> R[Set params from cluster dict]
    P --> S[Create model instance]
    Q --> S
    R --> S
    S --> T[Fit model on data]
    T --> U[Return labels as list]
```

## Examples:
    # Basic usage with default KMeans
    labels = cluster(data)
    
    # Using HDBSCAN
    labels = cluster(data, cluster='HDBSCAN')
    
    # Using custom parameters
    labels = cluster(data, cluster={'model': 'KMeans', 'params': {'n_clusters': 5}})
    
    # With custom number of clusters
    labels = cluster(data, cluster='KMeans', n_clusters=5)
    
    # Skip data formatting
    labels = cluster(data, format_data=False)
    
    # Return original data when cluster is None
    original_data = cluster(data, cluster=None)
```

