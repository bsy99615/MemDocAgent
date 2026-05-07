# `ppca.py`

## `hypertools._externals.ppca.PPCA` · *class*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.__init__` · *method*

## Summary:
Initializes a PPCA object with null state attributes for subsequent data processing.

## Description:
This constructor method initializes the internal state of a PPCA (Probabilistic Principal Component Analysis) object by setting key instance attributes to None. These attributes are populated during the model fitting process via the `fit` method. The initialization ensures the object starts with a clean state before any data processing occurs.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.raw: Set to None
    - self.data: Set to None  
    - self.C: Set to None
    - self.means: Set to None
    - self.stds: Set to None

## Constraints:
    Preconditions: None
    Postconditions: All instance attributes are initialized to None

## Side Effects:
    None

### `hypertools._externals.ppca.PPCA._standardize` · *method*

## Summary:
Standardizes input data using pre-computed mean and standard deviation values.

## Description:
This method applies z-score normalization to input data using previously computed mean and standard deviation statistics. It is typically called during the model fitting process to normalize training data before dimensionality reduction operations.

## Args:
    X (array-like): Input data to be standardized, with shape (n_samples, n_features)

## Returns:
    array-like: Standardized data with the same shape as input X, where each feature has zero mean and unit variance

## Raises:
    RuntimeError: When the model has not been fitted yet (i.e., self.means or self.stds are None)

## State Changes:
    Attributes READ: self.means, self.stds
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The model must be fitted first (self.means and self.stds must be set)
    - Input X must be compatible with the dimensions of self.means and self.stds
    
    Postconditions:
    - Returns standardized data with zero mean and unit variance per feature
    - Input X is not modified

## Side Effects:
    None

### `hypertools._externals.ppca.PPCA.fit` · *method*

## Summary:
Fits a probabilistic principal component analysis model to data with support for missing values and infinite observations through iterative optimization.

## Description:
Performs probabilistic principal component analysis (PPCA) fitting using an iterative expectation-maximization algorithm. This method processes input data by replacing infinite values with maximum finite values, filtering out features with insufficient observations, standardizing the data, and then applying alternating optimization between latent variables and model parameters until convergence. The method initializes component matrices when needed and updates model parameters to maximize the likelihood of the observed data under the PPCA model.

This method serves as the core fitting routine for the PPCA implementation, separating data preprocessing from the optimization algorithm for cleaner code organization.

## Args:
    data (array-like): Input data matrix of shape (n_samples, n_features) where some entries may be NaN or infinite.
    d (int, optional): Number of principal components to compute. If None, defaults to number of features.
    tol (float, optional): Convergence tolerance for the optimization algorithm. Defaults to 1e-4.
    min_obs (int, optional): Minimum number of valid observations required per feature. Defaults to 10.
    verbose (bool, optional): If True, prints convergence diagnostics during iterations. Defaults to False.

## Returns:
    None: This method modifies instance attributes in-place and does not return a value.

## Raises:
    None explicitly raised: The method handles numerical issues internally but does not raise explicit exceptions.

## State Changes:
    Attributes READ: 
        - self.C: Current component matrix (if exists)
        - self.raw: Raw data attribute (if exists)
    Attributes WRITTEN:
        - self.raw: Stores the input data after processing infinite value replacement
        - self.means: Stores mean values per feature computed from valid observations
        - self.stds: Stores standard deviation values per feature computed from valid observations
        - self.C: Stores the fitted component matrix after orthogonalization and eigenvector sorting
        - self.data: Stores processed standardized data with missing values imputed
        - self.eig_vals: Stores eigenvalues of the fitted components in descending order

## Constraints:
    Preconditions:
        - Input data should be numeric with potential NaN or infinite values
        - Data dimensions should be compatible with the PPCA algorithm
    Postconditions:
        - Instance attributes self.C, self.data, self.means, self.stds, and self.eig_vals are set
        - The component matrix C is orthogonalized using scipy.linalg.orth
        - Eigenvalues are sorted in descending order

## Side Effects:
    None: This method operates purely on instance state and does not perform I/O operations or external service calls.

### `hypertools._externals.ppca.PPCA.transform` · *method*

## Summary:
Projects input data onto the principal component space learned during model fitting.

## Description:
Transforms input data by projecting it onto the principal component subspace using the fitted component matrix. This method is typically called after fitting the PPCA model to reduce the dimensionality of new data or to apply the same transformation to the training data. When no data is provided, it transforms the training data that was used during fitting.

## Args:
    data (array-like, optional): New data to transform. If None, transforms the training data used during fitting. Defaults to None.

## Returns:
    array-like: Transformed data with reduced dimensionality. Shape is (n_samples, n_components) where n_components is determined during fitting.

## Raises:
    RuntimeError: When the model has not been fitted yet (self.C is None).

## State Changes:
    Attributes READ: self.C, self.data
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The PPCA model must be fitted before calling this method (self.C must not be None)
        - Input data dimensions must be compatible with the fitted component matrix
    Postconditions:
        - Returns transformed data with the same number of samples but fewer features

## Side Effects:
    None: This method operates purely on input arguments and instance state without external I/O or side effects.

### `hypertools._externals.ppca.PPCA._calc_var` · *method*

## Summary:
Calculates the cumulative variance explained by the principal components from eigenvalues.

## Description:
This method computes the proportion of total variance explained by each successive eigenvalue in descending order. It's called automatically during the fitting process to track how much variance is captured by the principal components. The method is separated from the main fitting logic to maintain clean code organization and enable reuse for variance calculations.

## Args:
    None

## Returns:
    None

## Raises:
    RuntimeError: When the data model has not been fitted yet (self.data is None)

## State Changes:
    Attributes READ: self.data, self.eig_vals
    Attributes WRITTEN: self.var_exp

## Constraints:
    Preconditions: 
    - self.data must not be None (data must be fitted first)
    - self.eig_vals must exist (eigenvalues must be computed)
    
    Postconditions:
    - self.var_exp is set to a numpy array containing cumulative variance ratios

## Side Effects:
    None

### `hypertools._externals.ppca.PPCA.save` · *method*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.load` · *method*

## Summary:
Loads a pre-computed principal component matrix from a numpy file and assigns it to the object's internal state.

## Description:
This method reads a numpy array file containing pre-computed principal component coefficients and stores it in the object's `C` attribute. It is typically used to restore a previously fitted PPCA model from disk storage. The method validates that the specified file exists before attempting to load it.

## Args:
    fpath (str): Absolute or relative path to the numpy file containing the principal component matrix.

## Returns:
    None: This method does not return any value.

## Raises:
    AssertionError: When the specified file path does not correspond to an existing file.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.C

## Constraints:
    Preconditions: The file at `fpath` must exist and contain a valid numpy array that can be loaded with `np.load()`.
    Postconditions: The `self.C` attribute will be updated to contain the loaded numpy array.

## Side Effects:
    I/O operation: Reads from the filesystem to load the numpy file.

