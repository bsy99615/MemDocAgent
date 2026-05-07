# `correlation_table.py`

## `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.__init__` · *method*

## Summary:
Initializes a correlation table presentation component with a correlation matrix and associated metadata.

## Description:
This method constructs a CorrelationTable instance by setting up the underlying presentation structure with a correlation matrix and optional configuration parameters. It serves as the constructor for correlation table visualizations in the reporting system, establishing the data structure needed for rendering correlation information.

## Args:
    name (str): Unique identifier for this correlation table component
    correlation_matrix (pd.DataFrame): DataFrame containing correlation coefficients between variables
    **kwargs: Additional keyword arguments passed to the parent ItemRenderer constructor

## Returns:
    None: This method initializes the object state and does not return a value

## Raises:
    None explicitly raised: The method delegates to parent constructors which may raise exceptions based on invalid arguments

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.item_type: Set to "correlation_table"
    - self.content: Dictionary containing the correlation_matrix and potentially name, anchor_id, and classes from kwargs

## Constraints:
    Preconditions:
    - name must be a string
    - correlation_matrix must be a pandas DataFrame
    - All kwargs must be valid arguments for the parent Renderable class
    
    Postconditions:
    - self.item_type is set to "correlation_table"
    - self.content contains the correlation_matrix under the key "correlation_matrix"
    - If name is provided, it's stored in self.content["name"]
    - If anchor_id or classes are provided in kwargs, they're stored in self.content

## Side Effects:
    None: This method performs no I/O operations or external service calls

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.__repr__` · *method*

## Summary:
Returns a string representation of the CorrelationTable object.

## Description:
This method provides a standard string representation for CorrelationTable instances, returning the literal string "CorrelationTable". It is called when the built-in repr() function is used on a CorrelationTable object or when the object is displayed in interactive environments.

## Args:
    None

## Returns:
    str: The literal string "CorrelationTable"

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: None

## Side Effects:
    None

### `src.ydata_profiling.report.presentation.core.correlation_table.CorrelationTable.render` · *method*

## Summary:
Abstract method that renders a correlation matrix table into a presentation-ready format.

## Description:
This method serves as an abstract interface for rendering correlation matrix data into various presentation formats. The method must be implemented by subclasses to provide concrete rendering logic for correlation tables. It is part of the presentation layer that transforms data structures into visual representations suitable for reports or dashboards.

## Args:
    None

## Returns:
    Any: The rendered representation of the correlation matrix, typically HTML, JSON, or another presentation format.

## Raises:
    NotImplementedError: This method is not implemented in the base class and must be overridden by subclasses.

## State Changes:
    Attributes READ: 
    - self.content: Accesses the stored correlation_matrix data
    - self.item_type: Accesses the item type identifier
    - self.name: Accesses the correlation table name
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The CorrelationTable instance must be properly initialized with a valid correlation_matrix
    - The correlation_matrix should be a pandas DataFrame containing correlation coefficients
    
    Postconditions:
    - Subclasses must return a valid presentation format representation of the correlation matrix
    - The returned value should be compatible with the presentation framework's rendering pipeline

## Side Effects:
    None

