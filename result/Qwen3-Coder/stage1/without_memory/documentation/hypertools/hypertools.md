# `hypertools`

## Repository Overview

This repository contains Hypertools, a Python library designed for visualizing and analyzing high-dimensional data. It provides tools for dimensionality reduction, data alignment, clustering, and interactive visualization of complex datasets.

### Tree Structure

```
hypertools/
├── docs/              # Documentation files
└── hypertools/        # Main package directory
    ├── __init__.py    # Package initialization
    ├── _externals/    # External dependency implementations
    │   ├── ppca.py    # Probabilistic PCA implementation
    │   └── srm.py     # Shared Response Model implementations
    ├── _shared/       # Shared utilities and helpers
    │   ├── exceptions.py  # Custom exceptions
    │   └── helpers.py     # Utility functions
    ├── datageometry/  # Data geometry handling and storage
    │   └── __init__.py
    ├── plot/          # Plotting functionality
    │   ├── __init__.py
    │   ├── backend.py # Backend management for plotting
    │   └── plot.py    # Main plotting interface
    └── tools/         # Data processing tools
        ├── __init__.py
        ├── align.py   # Data alignment methods
        ├── analyze.py # Data analysis pipeline
        ├── cluster.py # Clustering functionality
        ├── describe.py # Data description and correlation analysis
        ├── df2mat.py  # DataFrame to matrix conversion
        ├── format_data.py # Data formatting utilities
        ├── load.py    # Data loading functionality
        ├── missing_inds.py # Missing data indices detection
        ├── normalize.py # Data normalization
        ├── procrustes.py # Procrustes analysis
        ├── reduce.py  # Dimensionality reduction
        └── text2mat.py # Text to matrix conversion
```

### Purpose

Hypertools addresses the challenge of visualizing and analyzing high-dimensional data by providing a unified framework that combines:
- Advanced dimensionality reduction techniques
- Data alignment methods for multi-subject or multi-modal data
- Statistical normalization and preprocessing
- Interactive visualization capabilities
- Text data processing and semantic analysis

It is particularly valuable for researchers working with neuroimaging data, text corpora, and other complex datasets where traditional visualization methods fall short.

### Target Users

- Neuroscientists analyzing brain imaging data
- Data scientists working with high-dimensional datasets
- Researchers in computational linguistics and text analysis
- Anyone needing to visualize and understand complex multivariate data

### Position in Ecosystem

Hypertools serves as a high-level analysis and visualization tool that builds upon established scientific computing libraries like NumPy, SciPy, scikit-learn, and Matplotlib. It provides a user-friendly interface for combining these tools into powerful analytical workflows.

### Architecture

The system follows a modular architecture with clearly separated concerns:

1. **Data Processing Layer**: Handles data formatting, normalization, and preprocessing through tools like format_data, normalize, and reduce
2. **Analysis Layer**: Implements core algorithms for dimensionality reduction, alignment, and clustering through modules like align, cluster, and reduce
3. **Visualization Layer**: Provides plotting and interactive visualization capabilities through the plot module
4. **Storage Layer**: Manages DataGeometry objects for persisting analysis results through the datageometry module

### Entry Points

#### Importable API
```python
import hypertools as ht
# Main functions:
ht.plot()           # Primary plotting interface
ht.analyze()        # Analysis pipeline
ht.load()           # Data loading
ht.describe()       # Data description
ht.cluster()        # Clustering
```

#### CLI Commands
No direct CLI commands exposed; uses standard Python imports.

### Core Features

1. **Interactive 2D/3D Visualization** - Plot high-dimensional data in interactive 2D or 3D space using matplotlib
2. **Multi-subject Alignment** - Hyperalignment and SRM for aligning data across subjects through align module
3. **Dimensionality Reduction** - Multiple PCA variants and other reduction techniques through reduce module
4. **Text Analysis** - Convert text data to numerical representations using LDA and vectorizers through text2mat module
5. **Clustering** - Built-in clustering with automatic label assignment through cluster module
6. **Data Persistence** - Save/load DataGeometry objects for reproducible analysis through datageometry module

### Dependencies

- NumPy: Core numerical operations
- SciPy: Scientific computing functions
- scikit-learn: Machine learning algorithms
- Matplotlib: Plotting library
- Seaborn: Statistical data visualization
- Pandas: Data manipulation
- Requests: Network operations for data downloading
- HDBSCAN (optional): Advanced clustering algorithm

### Configuration

Configuration is primarily handled through function parameters rather than config files. Environment variables may influence backend selection for plotting through the backend module.

### Extension Points

1. **Custom Reduction Models**: Implement scikit-learn compatible classes for new dimensionality reduction techniques
2. **Custom Alignment Methods**: Add new alignment algorithms by implementing the required interface
3. **Custom Plotting Backends**: Extend backend management for new visualization environments
4. **New Data Types**: Add support for new data formats through the formatting system

---

## Modules

- [`docs`](docs.md)
- [`docs/tutorials`](docs/tutorials.md)
- [`docs/tutorials/tools`](docs/tutorials/tools.md)
- [`hypertools`](hypertools.md)
- [`hypertools/_externals`](hypertools/_externals.md)
- [`hypertools/_shared`](hypertools/_shared.md)
- [`hypertools/plot`](hypertools/plot.md)
- [`hypertools/tools`](hypertools/tools.md)

