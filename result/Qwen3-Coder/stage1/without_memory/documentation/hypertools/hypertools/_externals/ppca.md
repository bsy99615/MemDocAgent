# `ppca.py`

## `hypertools._externals.ppca.PPCA` · *class*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.__init__` · *method*

## Summary:
Initializes the PPCA object with null state variables for data storage and computation.

## Description:
This constructor method initializes the PPCA class instance with all internal state variables set to None. These variables will be populated during subsequent calls to the fit() method. The initialization prepares the object for probabilistic principal component analysis operations.

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
    Postconditions: All internal state variables are initialized to None

## Side Effects:
    None

### `hypertools._externals.ppca.PPCA._standardize` · *method*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.fit` · *method*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.transform` · *method*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA._calc_var` · *method*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.save` · *method*

*No documentation generated.*

### `hypertools._externals.ppca.PPCA.load` · *method*

*No documentation generated.*

