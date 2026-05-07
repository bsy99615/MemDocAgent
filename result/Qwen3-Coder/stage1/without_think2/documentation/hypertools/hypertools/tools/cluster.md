# `cluster.py`

## `hypertools.tools.cluster.cluster` · *function*

## Summary:
Performs clustering on input data using various scikit-learn and HDBSCAN clustering algorithms.

## Description:
The cluster function provides a unified interface for applying different clustering algorithms to input data. It supports multiple clustering methods including KMeans, HDBSCAN, AgglomerativeClustering, and others through a flexible string-based or dictionary-based configuration approach. The function handles data formatting automatically and returns cluster labels for each data point.

## Args:
    x (array-like): Input data to be clustered. Can be a list of arrays, a single array, or other supported data types.
    cluster (str or dict, optional): Clustering algorithm to use. Can be a string name like 'KMeans' or a dictionary with 'model' and 'params' keys. Defaults to 'KMeans'.
    n_clusters (int, optional): Number of clusters to form. Used by most clustering algorithms except HDBSCAN. Defaults to 3.
    ndims (int, optional): Deprecated parameter for dimensionality reduction. Ignored in current implementation. Defaults to None.
    format_data (bool, optional): Whether to apply automatic data formatting before clustering. Defaults to True.

## Returns:
    list[int]: Cluster labels for each data point in the input dataset. Each label corresponds to the cluster assignment for the respective data point.

## Raises:
    ImportError: When HDBSCAN is requested but the hdbscan package is not installed.

## Constraints:
    Preconditions:
        - Input data x must be compatible with numpy array conversion
        - If cluster is set to 'HDBSCAN', the hdbscan package must be installed
        - When using dictionary-based cluster specification, the 'model' key must reference a valid clustering algorithm
        
    Postconditions:
        - Function always returns a list of integer cluster labels
        - Input data is properly formatted before clustering when format_data=True
        - The returned labels correspond to the input data points in order

## Side Effects:
    - Issues a warning when ndims parameter is provided (deprecated)
    - May issue warnings during data formatting when missing values are encountered
    - Calls external clustering libraries (scikit-learn, hdbscan)

## Control Flow:
```mermaid
flowchart TD
    A[cluster(x, cluster, n_clusters, ndims, format_data)] --> B{cluster == None?}
    B -- Yes --> C[Return x]
    B -- No --> D{cluster is HDBSCAN?}
    D -- Yes --> E{hdbscan installed?}
    E -- No --> F[ImportError]
    E -- Yes --> G[Continue]
    D -- No --> G
    G --> H{ndims != None?}
    H -- Yes --> I[Warning: ndims deprecated]
    H -- No --> J[Continue]
    J --> K{format_data?}
    K -- Yes --> L[formatter(x, ppca=True)]
    K -- No --> M[x unchanged]
    M --> N{cluster is str?}
    N -- Yes --> O{cluster == 'HDBSCAN'?}
    O -- Yes --> P[model_params = {}]
    O -- No --> Q[model_params = {'n_clusters': n_clusters}]
    N -- No --> R{cluster is dict?}
    R -- Yes --> S{cluster['model'] is str?}
    S -- Yes --> T[model = models[cluster['model']]]
    S -- No --> U[Error]
    T --> V[model_params = cluster['params']]
    U --> W[Error]
    P --> X[model = model(**model_params)]
    Q --> X
    V --> X
    X --> Y[model.fit(np.vstack(x))]
    Y --> Z[Return list(model.labels_)]
```

## Examples:
    >>> # Basic KMeans clustering
    >>> data = [[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]]
    >>> labels = cluster(data, cluster='KMeans', n_clusters=2)
    >>> print(labels)
    [0, 0, 0, 1, 1, 1]
    
    >>> # Using HDBSCAN clustering
    >>> labels = cluster(data, cluster='HDBSCAN')
    >>> print(labels)
    [-1, -1, -1, 0, 0, 0]
    
    >>> # Using dictionary-based configuration
    >>> config = {'model': 'AgglomerativeClustering', 'params': {'n_clusters': 2}}
    >>> labels = cluster(data, cluster=config)
    >>> print(labels)
    [0, 0, 0, 1, 1, 1]

