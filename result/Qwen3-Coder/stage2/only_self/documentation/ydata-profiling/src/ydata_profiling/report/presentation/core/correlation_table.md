# `correlation_table.py`

## `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.__init__` · *method*

## Summary:
Initializes a correlation table presentation component with a correlation matrix and associated metadata.

## Description:
Constructs a CorrelationTable object that represents a correlation matrix visualization in the report presentation layer. This method sets up the internal structure required for rendering correlation tables in reports, storing the correlation matrix data along with metadata like name and other presentation attributes.

## Args:
    name (str): The name identifier for this correlation table component
    correlation_matrix (pd.DataFrame): A pandas DataFrame containing the correlation coefficients to be displayed
    **kwargs: Additional keyword arguments for presentation configuration (anchor_id, classes, etc.)

## Returns:
    None: This method initializes the object state and does not return a value

## Raises:
    None explicitly raised: The method delegates to parent constructors which may raise exceptions if invalid arguments are passed

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "correlation_table"
    - self.content: Dictionary containing the correlation_matrix and potentially name, anchor_id, and classes

## Constraints:
    Preconditions:
    - correlation_matrix must be a valid pandas DataFrame
    - name must be a string
    - All kwargs must be valid arguments for the parent Renderable class
    
    Postconditions:
    - The object is properly initialized with item_type set to "correlation_table"
    - The correlation_matrix is stored in the content dictionary under the key "correlation_matrix"
    - The name parameter is stored in the content dictionary if provided

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.__repr__` · *method*

## Summary:
Returns a string representation of the CorrelationTable object indicating its class type.

## Description:
Implements the Python special method `__repr__` to provide a standardized string representation of CorrelationTable instances. This method is called by Python's built-in `repr()` function and is used for debugging and logging purposes to clearly identify CorrelationTable objects.

## Args:
    None

## Returns:
    str: Always returns the literal string "CorrelationTable" to identify the object type.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned string is always exactly "CorrelationTable"

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.render` · *method*

## Summary:
Renders the correlation matrix into a presentation-ready format for display in profiling reports.

## Description:
This method is intended to convert the stored correlation matrix into a visual representation suitable for inclusion in profiling report presentations. As an abstract method inherited from ItemRenderer, it must be implemented by subclasses to provide the actual rendering logic. The method accesses the correlation_matrix stored in the instance's content dictionary to generate the appropriate output format.

## Args:
    None

## Returns:
    Any: The rendered representation of the correlation matrix, typically HTML, JSON, or another presentation format suitable for report generation.

## Raises:
    NotImplementedError: When called directly on the abstract CorrelationTable class without a concrete implementation.

## State Changes:
    Attributes READ: 
    - self.content: Accesses the correlation_matrix stored in the content dictionary
    - self.item_type: Accesses the item type identifier

## Constraints:
    Preconditions:
    - The CorrelationTable instance must have been properly initialized with a valid correlation_matrix
    - The correlation_matrix should be a pandas DataFrame containing correlation coefficients
    
    Postconditions:
    - The returned value should be in a format compatible with the reporting framework's presentation layer
    - The method should not modify the instance's state

## Side Effects:
    None: This method is expected to be pure and not cause any external I/O or state mutations beyond returning the rendered result.

