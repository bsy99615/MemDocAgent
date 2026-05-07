# `expectations_report.py`

## `src.ydata_profiling.expectations_report.ExpectationHandler` · *class*

## Summary:
A specialized handler that maps data types to expectation algorithms for data profiling and validation.

## Description:
The ExpectationHandler class is responsible for creating type-specific mappings of expectation algorithms that can be used to validate data properties during profiling. It extends the base Handler class to provide type-aware expectation handling for data validation purposes. This class is typically instantiated by the profiling system when generating expectations reports for datasets, particularly when validating data characteristics against predefined expectations.

## State:
- mapping: dict[str, list[Callable]] - Maps data type names to lists of expectation algorithm functions
- typeset: VisionsTypeset - The typeset object that defines the data type hierarchy and relationships

## Lifecycle:
- Creation: Instantiate with a VisionsTypeset object; the mapping is automatically constructed during initialization
- Usage: The handler's `handle` method is typically called with a data type string to retrieve appropriate expectation algorithms
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[ExpectationHandler.__init__] --> B[Handler.__init__]
    B --> C[mapping construction]
    C --> D[super().__init__]
    D --> E[Handler._complete_dag()]
    E --> F[Handler.handle() method available]
```

## Raises:
- TypeError: If typeset parameter is not of type VisionsTypeset
- ValueError: If the mapping construction fails due to invalid configuration

## Example:
```python
from visions import VisionsTypeset
from ydata_profiling.expectations_report import ExpectationHandler

# Create a typeset (typically done by the profiling system)
typeset = VisionsTypeset()

# Initialize the expectation handler
handler = ExpectationHandler(typeset)

# The handler can now be used to retrieve expectation algorithms for different data types
# via the inherited handle() method
```

### `src.ydata_profiling.expectations_report.ExpectationHandler.__init__` · *method*

## Summary:
Initializes an ExpectationHandler with type-specific expectation algorithm mappings and configures the handler for data type processing.

## Description:
Configures the expectation handler by establishing a mapping between data types and their corresponding expectation algorithms, then initializes the parent Handler class with this configuration. This method sets up the handler to process data expectations based on the detected data types from the Visions typeset.

## Args:
    typeset (VisionsTypeset): The typeset object containing data type information and relationships
    *args: Additional positional arguments passed to the parent Handler constructor
    **kwargs: Additional keyword arguments passed to the parent Handler constructor

## Returns:
    None: This method initializes the object and does not return a value

## Raises:
    None explicitly raised: The method delegates to the parent Handler constructor which may raise exceptions based on invalid arguments

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.mapping: Set to the type-specific expectation algorithm mapping
    - self.typeset: Set to the provided typeset parameter

## Constraints:
    Preconditions:
    - typeset must be a valid VisionsTypeset instance
    - The typeset should contain the expected data type definitions referenced in the mapping
    
    Postconditions:
    - self.mapping contains the complete mapping of data types to expectation algorithms
    - self.typeset is properly assigned to the provided typeset instance

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal state.

## `src.ydata_profiling.expectations_report.ExpectationsReport` · *class*

## Summary
A class that converts statistical profiling reports into Great Expectations expectation suites for automated data validation.

## Description
The ExpectationsReport class serves as a bridge between ydata-profiling's statistical analysis capabilities and Great Expectations' data validation framework. It takes a profiling report (which includes statistical summaries and data type information) and automatically generates appropriate data validation expectations that can be used to ensure data quality over time.

This class is typically instantiated by the profiling system when users want to convert their data analysis results into executable validation rules. It leverages the profiling report's variable summaries and type information to create meaningful expectations that can be run against future data to detect anomalies or violations of data quality standards.

The class depends on the presence of a `get_description()` method which should return a `BaseDescription` object containing variable summaries and statistical information. This method is typically implemented by parent classes such as `ProfileReport`.

## State
- config: Settings - Configuration object containing profiling settings and metadata
- df: Optional[pd.DataFrame] = None - The dataset that was profiled, used for generating expectations
- typeset: Optional[VisionsTypeset] - Data type hierarchy for type-specific expectation mapping (currently returns None in the base implementation)

## Lifecycle
- Creation: Instantiate with a configuration object and optionally a DataFrame
- Usage: Call `to_expectation_suite()` method to generate Great Expectations expectation suite
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map
```mermaid
graph TD
    A[ExpectationsReport.to_expectation_suite] --> B[Import Great Expectations]
    B --> C[Slugify config.title if suite_name is None]
    C --> D[Create ExpectationHandler if none provided]
    D --> E[Create DataContext if none provided]
    E --> F[Create expectation suite]
    F --> G[Create PandasDataset from df]
    G --> H[Get description from get_description()]
    H --> I[Process each variable with handler]
    I --> J[Get updated expectation suite]
    J --> K{run_validation?}
    K -->|Yes| L[Recreate PandasDataset with suite]
    L --> M[Run validation operator]
    M --> N[Get validation result identifier]
    K -->|No| O[Skip validation]
    O --> P[Save suite if save_suite or build_data_docs]
    P --> Q[Build docs if build_data_docs]
    Q --> R[Open docs if build_data_docs]
    R --> S[Return expectation suite]
```

## Raises
- ImportError: When Great Expectations is not installed in the environment
- TypeError: If typeset parameter is not of type VisionsTypeset (when ExpectationHandler is created)
- ValueError: If the mapping construction fails due to invalid configuration (when ExpectationHandler is created)

## Example
```python
from ydata_profiling import ProfileReport
from ydata_profiling.config import Settings

# Create a profiling report
df = pd.read_csv("data.csv")
config = Settings(title="My Data Profile")
profile = ProfileReport(df, config=config)

# Convert to Great Expectations suite
suite = profile.expectations_report.to_expectation_suite(
    suite_name="my_data_suite",
    save_suite=True,
    run_validation=True,
    build_data_docs=True
)
```

### `src.ydata_profiling.expectations_report.ExpectationsReport.typeset` · *method*

## Summary:
Returns the VisionsTypeset object defining the data type hierarchy for expectation validation, or None if not yet computed.

## Description:
This property provides access to the VisionsTypeset instance that represents the data type hierarchy for the dataset being profiled. The typeset is used by the ExpectationHandler to map data types to appropriate expectation algorithms during the generation of data validation expectations. 

In the current implementation, this property returns None, indicating that the typeset computation is not yet implemented. It should return a properly configured VisionsTypeset based on the dataset and configuration when implemented.

Known callers:
- `to_expectation_suite()` method: Called during expectation suite generation to initialize ExpectationHandler with the appropriate typeset for type-specific expectation mapping.

## Args:
    None

## Returns:
    Optional[VisionsTypeset]: A VisionsTypeset object representing the data type hierarchy for the dataset, or None if not yet computed or available.

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The ExpectationsReport instance must be properly initialized with configuration and data.
    Postconditions: When implemented correctly, the returned VisionsTypeset object should be suitable for use with ExpectationHandler.

## Side Effects:
    None

### `src.ydata_profiling.expectations_report.ExpectationsReport.to_expectation_suite` · *method*

## Summary:
Converts the profiling report into a Great Expectations expectation suite with optional validation and documentation generation.

## Description:
This method transforms the statistical profile of a dataset into a Great Expectations expectation suite. It leverages the profiling report's variable summaries and type information to automatically generate appropriate data validation expectations. The method can optionally execute validation, save the expectation suite to disk, and generate data documentation.

The method follows these steps:
1. Creates or uses a Great Expectations DataContext
2. Generates an expectation suite with the specified name
3. Processes each variable in the profiling report using an expectation handler
4. Optionally runs validation against the dataset
5. Saves the suite and builds documentation if requested

## Args:
    suite_name (Optional[str]): Name for the expectation suite. Defaults to a slugified version of the report title.
    data_context (Optional[Any]): Great Expectations DataContext instance. Creates a default DataContext if not provided.
    save_suite (bool): Whether to save the expectation suite to disk. Defaults to True.
    run_validation (bool): Whether to run validation against the dataset. Defaults to True.
    build_data_docs (bool): Whether to build and open data documentation. Defaults to True.
    handler (Optional[Handler]): Custom expectation handler. Creates a default ExpectationHandler if not provided.

## Returns:
    Any: The final Great Expectations expectation suite object containing all generated expectations.

## Raises:
    ImportError: When Great Expectations is not installed in the environment.

## State Changes:
    Attributes READ: self.config, self.typeset, self.df, self.get_description()
    Attributes WRITTEN: None (modifies external objects through Great Expectations API)

## Constraints:
    Preconditions: 
    - The profiling report must have been generated (self.df must be set)
    - Great Expectations must be installed in the environment
    - self.config.title must be accessible for suite naming
    
    Postconditions:
    - An expectation suite is created with expectations derived from the profiling report
    - If save_suite=True, the suite is persisted to the DataContext
    - If build_data_docs=True, data documentation is generated and opened

## Side Effects:
    - Creates and potentially modifies Great Expectations DataContext
    - Saves expectation suite files to disk if save_suite=True
    - Builds and opens HTML documentation if build_data_docs=True
    - May trigger network requests when building documentation

