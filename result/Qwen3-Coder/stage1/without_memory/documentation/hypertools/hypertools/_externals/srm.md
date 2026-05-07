# `srm.py`

## `hypertools._externals.srm._init_w_transforms` · *function*

*No documentation generated.*

## `hypertools._externals.srm.SRM` · *class*

*No documentation generated.*

### `hypertools._externals.srm.SRM.__init__` · *method*

## Summary:
Initializes the Shared Response Model with configurable hyperparameters for probabilistic modeling.

## Description:
Configures the probabilistic Shared Response Model (SRM) with specified training parameters. This method is called during object instantiation to set up the model's hyperparameters that control the iterative fitting process and random seed initialization.

## Args:
    n_iter (int): Number of iterations for the Expectation-Maximization algorithm. Defaults to 10.
    features (int): Number of shared response features to extract. Defaults to 50.
    rand_seed (int): Random seed for reproducible results. Defaults to 0.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None: This method does not raise exceptions directly.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.n_iter, self.features, self.rand_seed

## Constraints:
    Preconditions: None
    Postconditions: Instance attributes self.n_iter, self.features, and self.rand_seed are set to the provided values.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `hypertools._externals.srm.SRM.fit` · *method*

*No documentation generated.*

### `hypertools._externals.srm.SRM.transform` · *method*

*No documentation generated.*

### `hypertools._externals.srm.SRM._init_structures` · *method*

*No documentation generated.*

### `hypertools._externals.srm.SRM._likelihood` · *method*

*No documentation generated.*

### `hypertools._externals.srm.SRM._srm` · *method*

*No documentation generated.*

## `hypertools._externals.srm.DetSRM` · *class*

*No documentation generated.*

### `hypertools._externals.srm.DetSRM.__init__` · *method*

## Summary:
Initializes the Deterministic Shared Response Model with configurable hyperparameters for iterative optimization.

## Description:
Configures the SRM algorithm parameters including the number of iterations, feature dimensions, and random seed for reproducible results. This method establishes the foundational configuration needed for the model's training process.

## Args:
    n_iter (int): Number of iterations for the SRM optimization algorithm. Defaults to 10.
    features (int): Number of features (dimensions) in the shared response space. Defaults to 50.
    rand_seed (int): Random seed for initializing weight matrices. Defaults to 0.

## Returns:
    None: This method initializes instance attributes and does not return a value.

## Raises:
    None: This method does not raise exceptions directly.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.n_iter, self.features, self.rand_seed

## Constraints:
    Preconditions: None
    Postconditions: Instance attributes self.n_iter, self.features, and self.rand_seed are set to the provided values.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `hypertools._externals.srm.DetSRM.fit` · *method*

*No documentation generated.*

### `hypertools._externals.srm.DetSRM.transform` · *method*

*No documentation generated.*

### `hypertools._externals.srm.DetSRM._objective_function` · *method*

*No documentation generated.*

### `hypertools._externals.srm.DetSRM._compute_shared_response` · *method*

*No documentation generated.*

### `hypertools._externals.srm.DetSRM._srm` · *method*

## Summary:
Performs iterative optimization to compute subject-specific transforms and shared response for a Deterministic Shared Response Model.

## Description:
Implements the core algorithm for Deterministic Shared Response Model (SRM) that finds shared neural responses across multiple subjects while learning subject-specific transformation matrices. This method iteratively optimizes the transforms (w) and shared response (s) by alternating between updating subject-specific components and recomputing the shared response.

## Args:
    data (list[np.ndarray]): List of subject data matrices, where each matrix has shape (voxels, time_points) representing neuroimaging data for a subject.

## Returns:
    tuple[list[np.ndarray], np.ndarray]: Tuple containing:
        - w (list[np.ndarray]): List of subject-specific transformation matrices, each with shape (voxels, features)
        - shared_response (np.ndarray): Shared response matrix with shape (features, time_points)

## Raises:
    None explicitly raised, but may raise exceptions from underlying operations like:
    - ValueError: If data validation fails in parent methods
    - np.linalg.LinAlgError: If SVD computation fails

## State Changes:
    - Attributes READ: self.n_iter, self.features, self.rand_seed
    - Attributes WRITTEN: None (this is a private method that doesn't modify instance state)

## Constraints:
    - Preconditions:
        - Input data must be a list of numpy arrays
        - Each subject's data matrix must have the same number of time points
        - Data matrices should have sufficient voxels for the requested number of features
        - Random seed should be set appropriately for reproducibility
    - Postconditions:
        - Returns orthogonal transformation matrices for each subject
        - Returns a shared response that captures common neural patterns across subjects

## Side Effects:
    - Sets random seed using self.rand_seed for reproducible results
    - Logs iteration progress and objective function values when logger level is INFO
    - Uses numpy linear algebra operations (SVD, matrix multiplication)

