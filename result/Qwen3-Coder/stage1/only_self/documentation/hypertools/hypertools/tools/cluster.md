# `cluster.py`

## `hypertools.tools.cluster.cluster` · *function*

## Summary:
Performs clustering on input data using various clustering algorithms with automatic data formatting.

## Description:
This function applies clustering to input data using different clustering algorithms specified by name or configuration. It automatically formats input data using PCA-based preprocessing and supports multiple clustering methods including KMeans, HDBSCAN, and others from scikit-learn. The function handles both string-based algorithm specification and dictionary-based configuration.

## Args:
    x (array-like): Input data to be clustered. Can be various data types including numerical arrays, text data, or mixed data types.
    cluster (str or dict, optional): Clustering algorithm to use. Can be a string name (e.g., 'KMeans', 'HDBSCAN') or a dictionary with 'model' and 'params' keys specifying the clustering algorithm and its parameters. Defaults to 'KMeans'.
    n_clusters (int, optional): Number of clusters to form. Used when cluster is a string and not HDBSCAN. Defaults to 3.
    ndims (int, optional): Deprecated parameter for dimensionality reduction. Currently ignored with warning. Defaults to None.
    format_data (bool, optional): Whether to apply data formatting and preprocessing. Defaults to True.

## Returns:
    list[int]: Cluster labels for each data point in the input. Each label corresponds to the cluster assignment for the respective data point. Returns the original input `x` unchanged if `cluster` is None.

## Raises:
    ImportError: When HDBSCAN is specified but not installed (hdbscan>=0.8.11).

## Constraints:
    Preconditions:
        - Input data `x` must be compatible with the clustering algorithm being used
        - If HDBSCAN is specified, the hdbscan package must be installed
    Postconditions:
        - Returns a list of integer cluster labels with length equal to the number of input data points
        - All cluster labels are integers representing cluster assignments
        - If cluster=None, returns the original input unchanged

## Side Effects:
    - Issues a deprecation warning when `ndims` parameter is provided
    - May issue warnings during data formatting when missing data is encountered
    - Calls external libraries (scikit-learn, hdbscan) for clustering operations

## Control Flow:
```mermaid
flowchart TD
    A[Start cluster()] --> B{cluster == None?}
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
    L --> M{cluster != 'HDBSCAN'?}
    M -- Yes --> N[Set model_params with n_clusters]
    M -- No --> O[Set model_params as empty dict]
    K --> P{Dict cluster}
    P --> Q[Extract model and params from dict]
    Q --> R[Create model instance]
    R --> S[Fit model on np.vstack(x)]
    S --> T[Return list(model.labels_)]
```

## Examples:
    # Basic KMeans clustering
    labels = cluster(data, cluster='KMeans', n_clusters=5)
    
    # Using HDBSCAN clustering
    labels = cluster(data, cluster='HDBSCAN')
    
    # Using custom clustering parameters
    labels = cluster(data, cluster={'model': 'KMeans', 'params': {'n_clusters': 4, 'random_state': 42}})
    
    # With custom number of clusters
    labels = cluster(data, cluster='KMeans', n_clusters=2)
    
    # Skip clustering entirely
    original_data = cluster(data, cluster=None)
```

