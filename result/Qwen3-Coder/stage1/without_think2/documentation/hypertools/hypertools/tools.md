# `hypertools.tools`

## Tree:
tools/
├── align.py
├── analyze.py
├── cluster.py
├── describe.py
├── df2mat.py
├── format_data.py
├── load.py
├── missing_inds.py
├── normalize.py
├── procrustes.py
├── reduce.py
└── text2mat.py

## Role:
Provides a collection of utility functions for preprocessing, transforming, and analyzing neuroimaging and textual data in a standardized manner.

## Description:
The tools module serves as a foundational component of the hypertools library, offering a suite of data processing utilities that enable consistent and efficient handling of diverse data types including neuroimaging, textual, and numerical data. It provides functions for data alignment, normalization, dimensionality reduction, clustering, and format conversion that are essential for reproducible scientific analysis.

This module is organized around shared concepts of data preprocessing and transformation rather than specific analytical tasks. It acts as a bridge between raw data ingestion and higher-level analysis functions, ensuring that data is consistently formatted and appropriately processed before being fed into visualization or machine learning pipelines.

Primary consumers of this module include:
- The main `hypertools` analysis functions that orchestrate multi-step processing workflows
- Visualization components that require standardized numerical representations
- Data loading utilities that need to preprocess datasets before analysis
- Higher-level APIs that expose simplified interfaces for common data processing tasks

## Components:
- align (function): Performs hyperalignment or SRM-based alignment of multi-subject neuroimaging data
- analyze (function): Applies a sequence of data processing transformations (normalization, dimensionality reduction, and alignment)
- cluster (function): Performs clustering on input data using various scikit-learn and HDBSCAN clustering algorithms
- describe (function): Analyzes the relationship between high-dimensional data and its dimensionality-reduced representations by computing correlations
- describe.get_cdist (function): Computes the pairwise Euclidean distances between all rows in the input array
- describe.get_corr (function): Computes the Pearson correlation coefficient between flattened reduced and all-dimensions data arrays
- df2mat (function): Converts a pandas DataFrame with mixed data types into a numerical matrix suitable for plotting
- format_data (function): Formats mixed-type data (text, numerical, and geometric) into a standardized numerical representation
- load._download_example_data (function): Downloads example datasets from a remote server to a local file path
- load._load_example_data (function): Loads example datasets from local cache or downloads them from a remote server if not available
- load._load_legacy (function): Loads legacy-format dataset files saved with deepdish and converts them into DataGeometry objects
- load.load (function): Loads and optionally processes dataset files or example datasets for analysis and visualization
- missing_inds (function): Identifies indices of missing (NaN) values in array-like data structures
- normalize (function): Normalizes input data using z-score standardization across specified dimensions
- procrustes (function): Performs Procrustes analysis to find the optimal linear transformation between two datasets
- reduce (function): Reduces the dimensionality of input data using various scikit-learn and custom dimensionality reduction techniques
- reduce.reduce_list (function): Applies dimensionality reduction to a list of data arrays while preserving their individual structures
- text2mat._check_mtype (function): Determines the concrete type of a given parameter and returns a standardized string identifier for that type
- text2mat._fit_models (function): Initializes and fits text vectorization and topic modeling models if they haven't been previously fitted
- text2mat._transform (function): Transforms text data using vectorization and/or topic modeling models, preserving original data structure
- text2mat.text2mat (function): Converts text data into numerical matrices using configurable vectorization and semantic modeling techniques

## Public API:
- align(data, align='hyper', normalize=None, ndims=None, method=None, format_data=True): Performs hyperalignment or SRM-based alignment of multi-subject neuroimaging data
- analyze(data, normalize=None, reduce=None, ndims=None, align=None, internal=False): Applies a sequence of data processing transformations (normalization, dimensionality reduction, and alignment)
- cluster(x, cluster='KMeans', n_clusters=3, ndims=None, format_data=True): Performs clustering on input data using various scikit-learn and HDBSCAN clustering algorithms
- describe(x, reduce='IncrementalPCA', max_dims=None, show=True, format_data=True): Analyzes the relationship between high-dimensional data and its dimensionality-reduced representations by computing correlations across varying numbers of components
- describe.get_cdist(x): Computes the pairwise Euclidean distances between all rows in the input array
- describe.get_corr(reduced, alldims): Computes the Pearson correlation coefficient between flattened reduced and all-dimensions data arrays
- df2mat(data, return_labels=False): Converts a pandas DataFrame with mixed data types into a numerical matrix suitable for plotting
- format_data(x, vectorizer='CountVectorizer', semantic='LatentDirichletAllocation', corpus='wiki', ppca=True, text_align='hyper'): Formats mixed-type data (text, numerical, and geometric) into a standardized numerical representation
- load._download_example_data(dataset_path): Downloads example datasets from a remote server to a local file path
- load._load_example_data(dataset): Loads example datasets from local cache or downloads them from a remote server if not available
- load._load_legacy(dataset_path): Loads legacy-format dataset files saved with deepdish and converts them into DataGeometry objects
- load.load(dataset, reduce=None, ndims=None, align=None, normalize=None, legacy=False): Loads and optionally processes dataset files or example datasets for analysis and visualization
- missing_inds(x, format_data=True): Identifies indices of missing (NaN) values in array-like data structures
- normalize(x, normalize='across', internal=False, format_data=True): Normalizes input data using z-score standardization across specified dimensions
- procrustes(source, target, scaling=True, reflection=True, reduction=False, oblique=False, oblique_rcond=-1, format_data=True): Performs Procrustes analysis to find the optimal linear transformation between two datasets
- reduce(x, reduce='IncrementalPCA', ndims=None, normalize=None, align=None, model=None, model_params=None, internal=False, format_data=True): Reduces the dimensionality of input data using various scikit-learn and custom dimensionality reduction techniques
- reduce.reduce_list(x, model): Applies dimensionality reduction to a list of data arrays while preserving their individual structures
- text2mat._check_mtype(x): Determines the concrete type of a given parameter and returns a standardized string identifier for that type
- text2mat._fit_models(vmodel, tmodel, x, model_is_fit): Initializes and fits text vectorization and topic modeling models if they haven't been previously fitted
- text2mat._transform(vmodel, tmodel, x): Transforms text data using vectorization and/or topic modeling models, preserving original data structure
- text2mat.text2mat(data, vectorizer='CountVectorizer', semantic='LatentDirichletAllocation', corpus='wiki'): Converts text data into numerical matrices using configurable vectorization and semantic modeling techniques

## Dependencies:
- Internal imports:
  - `hypertools.tools.align`
  - `hypertools.tools.analyze`
  - `hypertools.tools.cluster`
  - `hypertools.tools.describe`
  - `hypertools.tools.df2mat`
  - `hypertools.tools.format_data`
  - `hypertools.tools.load`
  - `hypertools.tools.missing_inds`
  - `hypertools.tools.normalize`
  - `hypertools.tools.procrustes`
  - `hypertools.tools.reduce`
  - `hypertools.tools.text2mat`
- External imports:
  - `numpy` (for numerical operations)
  - `pandas` (for DataFrame handling)
  - `scipy` (for statistical functions)
  - `sklearn` (for machine learning algorithms)
  - `matplotlib` (for visualization)
  - `seaborn` (for statistical visualization)
  - `requests` (for HTTP requests)
  - `hdbscan` (for HDBSCAN clustering)
  - `umap` (for UMAP dimensionality reduction)
  - `joblib` (for parallel processing)
  - `pickle` (for serialization)
  - `inspect` (for introspection)
  - `os` (for file system operations)
  - `warnings` (for warnings)
  - `pathlib` (for path manipulation)
  - `collections` (for data structures)
  - `typing` (for type hints)

## Constraints:
- All functions expect input data to be compatible with numpy array operations
- Functions that process multiple datasets require consistent dimensional properties across inputs
- Some functions have deprecated parameters that will be removed in future versions
- Thread safety is not guaranteed for functions that modify global state or cache files
- Certain functions require specific external packages (e.g., hdbscan for HDBSCAN clustering)
- Functions that perform data alignment or reduction assume sufficient sample sizes for stable computation

---

## Files

- [`align.py`](tools/align.md)
- [`analyze.py`](tools/analyze.md)
- [`cluster.py`](tools/cluster.md)
- [`describe.py`](tools/describe.md)
- [`df2mat.py`](tools/df2mat.md)
- [`format_data.py`](tools/format_data.md)
- [`load.py`](tools/load.md)
- [`missing_inds.py`](tools/missing_inds.md)
- [`normalize.py`](tools/normalize.md)
- [`procrustes.py`](tools/procrustes.md)
- [`reduce.py`](tools/reduce.md)
- [`text2mat.py`](tools/text2mat.md)

