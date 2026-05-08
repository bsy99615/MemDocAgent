# `expectations_report.py`

## `src.ydata_profiling.expectations_report.ExpectationHandler` · *class*

## Summary:
Handles the application of expectation algorithms based on data types using a type mapping system.

## Description:
The ExpectationHandler class serves as a specialized handler that maps data types to appropriate expectation algorithms for data validation. It inherits from the base Handler class and provides a type-specific mapping that enables the execution of domain-appropriate expectations for different data categories such as numeric, categorical, datetime, and others.

This class is designed to be instantiated by the profiling system when generating expectations reports, allowing for type-aware validation of data characteristics according to the appropriate expectation algorithms for each data type. The handler uses a mapping system that associates data types with collections of expectation algorithms, enabling flexible and extensible data validation.

## State:
- mapping: Dictionary mapping data type names to lists of expectation algorithm callables
- typeset: VisionsTypeset instance containing type hierarchy information
- The mapping is initialized with specific expectation algorithms for different data types:
  - "Unsupported": generic_expectations
  - "Text", "Categorical", "Boolean": categorical_expectations  
  - "Numeric": numeric_expectations
  - "URL": url_expectations
  - "File": file_expectations
  - "Path": path_expectations
  - "DateTime": datetime_expectations
  - "Image": image_expectations

## Lifecycle:
- Creation: Instantiate with a VisionsTypeset object; the mapping is automatically constructed during initialization via the parent Handler.__init__
- Usage: Call the inherited handle() method with a data type string to retrieve and execute applicable expectation algorithms
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[ExpectationHandler.__init__] --> B[Handler.__init__]
    B --> C[Handler._complete_dag]
    A --> D[Mapping configured]
    D --> E[handle() method available]
```

## Raises:
- No explicit exceptions are raised by __init__ beyond those potentially raised by the parent Handler class initialization
- The constructor may raise exceptions from the parent Handler class if invalid arguments are passed

## Example:
```python
# Create the handler with a typeset
handler = ExpectationHandler(typeset)

# Apply expectations for a specific data type
result = handler.handle("Numeric", data_column)
```

### `src.ydata_profiling.expectations_report.ExpectationHandler.__init__` · *method*

## Summary:
Initializes an ExpectationHandler instance with type-specific expectation algorithm mappings.

## Description:
Configures the handler with a mapping of data types to their corresponding expectation algorithms, enabling type-aware expectation generation for data profiling. This method establishes the relationship between data type categories and the appropriate expectation functions that should be applied to validate those data types.

## Args:
    typeset (VisionsTypeset): The typeset object defining the data type hierarchy and relationships.
    *args: Additional positional arguments passed to the parent Handler constructor.
    **kwargs: Additional keyword arguments passed to the parent Handler constructor.

## Returns:
    None: This method initializes the instance and does not return a value.

## Raises:
    None explicitly raised by this method, though parent class may raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.mapping: Set to the type-specific expectation algorithm mapping
    - self.typeset: Set to the provided typeset parameter

## Constraints:
    Preconditions:
    - The typeset parameter must be a valid VisionsTypeset instance
    - All expectation algorithm references in the mapping must be valid callable objects
    
    Postconditions:
    - The instance will have a properly initialized mapping attribute
    - The instance will have a properly initialized typeset attribute
    - The _complete_dag method will have been called to finalize the mapping

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal state.

## `src.ydata_profiling.expectations_report.ExpectationsReport` · *class*

## Summary
A class that converts statistical profiling reports into Great Expectations expectation suites for data validation.

## Description
The ExpectationsReport class serves as a bridge between ydata-profiling's statistical analysis capabilities and Great Expectations' data validation framework. It transforms the descriptive statistics and data characteristics gathered during profiling into structured expectation suites that can be used to validate data quality and consistency over time.

This class is typically instantiated by the profiling system when users want to export their data analysis results into a format suitable for automated data validation workflows. It leverages the profiling summary data to generate appropriate expectations based on data types and statistical properties.

The class requires a configuration object and optional DataFrame to function properly. The configuration's title is used to name the expectation suite when no explicit suite name is provided.

## State
- config: Settings instance containing configuration parameters including title for suite naming
- df: Optional pandas DataFrame containing the data being profiled (default: None)
- typeset: Property that should return VisionsTypeset for data type detection (currently returns None)

## Lifecycle
- Creation: Instantiate with a Settings configuration object and optional DataFrame
- Usage: Call to_expectation_suite() method to generate Great Expectations suite
- Destruction: No special cleanup required; relies on Python garbage collection

## Method Map
```mermaid
graph TD
    A[ExpectationsReport.to_expectation_suite] --> B[Import Great Expectations]
    B --> C[Create suite name from config.title using slugify]
    C --> D[Initialize ExpectationHandler with typeset]
    D --> E[Create DataContext if none provided]
    E --> F[Create expectation suite]
    F --> G[Create PandasDataset]
    G --> H[Get description from profiling data via get_description()]
    H --> I[Process each variable with handler]
    I --> J[Get updated expectation suite]
    J --> K{run_validation}
    K -->|Yes| L[Recreate dataset with suite]
    L --> M[Run validation operator]
    M --> N[Save suite if requested]
    N --> O{build_data_docs}
    O -->|Yes| P[Build data docs]
    P --> Q[Open data docs]
    K -->|No| R[Skip validation]
    R --> S[Save suite if requested]
    S --> T[Return expectation suite]
    Q --> T
```

## Raises
- ImportError: When Great Expectations is not installed in the environment
- Various exceptions from Great Expectations APIs during suite creation, validation, or documentation building

## Example
```python
# Create an ExpectationsReport instance
report = ExpectationsReport(config=settings, df=dataframe)

# Convert to Great Expectations suite
suite = report.to_expectation_suite(
    suite_name="my_data_suite",
    save_suite=True,
    run_validation=True,
    build_data_docs=True
)

# The returned suite can be used for ongoing data validation
```

### `src.ydata_profiling.expectations_report.ExpectationsReport.typeset` · *method*

## Summary:
Returns the Visions typeset representing the detected data types in the profiling report's dataframe, or None if not yet implemented.

## Description:
This property is designed to return a VisionsTypeset instance that encapsulates the data type information for all columns in the dataframe being profiled. The typeset is used by the expectation generation system to determine appropriate Great Expectations for different data types. In the current implementation, this property returns None and requires proper implementation to compute the actual typeset from the underlying dataframe. This property is accessed by the `to_expectation_suite` method to initialize the expectation handler.

## Args:
    None

## Returns:
    Optional[VisionsTypeset]: A VisionsTypeset instance containing type information for all columns, or None if not yet implemented or if no dataframe is available.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.df
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The class should have a valid dataframe assigned to self.df
    - The Visions library must be available in the environment
    
    Postconditions:
    - Should return a valid VisionsTypeset instance when properly implemented
    - Returns None when self.df is None or empty, or when not yet implemented

## Side Effects:
    None

### `src.ydata_profiling.expectations_report.ExpectationsReport.to_expectation_suite` · *method*

## Summary:
Converts the profiling report into a Great Expectations expectation suite with optional validation and documentation generation.

## Description:
Transforms the statistical summary and data characteristics from the profiling report into a structured Great Expectations expectation suite. This method orchestrates the creation of expectations based on data types and variable characteristics, optionally running validations and generating documentation. It serves as the main interface for exporting profiling insights into the Great Expectations framework for data validation.

## Args:
    suite_name (Optional[str]): Name for the expectation suite. Defaults to slugified title from config.
    data_context (Optional[Any]): Great Expectations data context instance. Creates default if None.
    save_suite (bool): Whether to save the expectation suite to disk. Defaults to True.
    run_validation (bool): Whether to run validation on the dataset. Defaults to True.
    build_data_docs (bool): Whether to build and open data documentation. Defaults to True.
    handler (Optional[Handler]): Custom expectation handler. Creates default ExpectationHandler if None.

## Returns:
    Any: The final expectation suite object from Great Expectations.

## Raises:
    ImportError: When Great Expectations is not installed in the environment.

## State Changes:
    Attributes READ: self.config, self.typeset, self.df, self.get_description()
    Attributes WRITTEN: None - modifies external systems (Great Expectations context)

## Constraints:
    Preconditions: 
    - Great Expectations must be installed
    - self.df must contain valid pandas DataFrame
    - self.config.title must be convertible to string
    - self.typeset must be a valid VisionsTypeset instance
    
    Postconditions:
    - Returns a valid Great Expectations expectation suite object
    - If save_suite=True, suite is persisted to data context storage
    - If build_data_docs=True, documentation is generated and opened

## Side Effects:
    - Creates and modifies Great Expectations data context and expectation suites
    - May save files to disk if save_suite=True
    - May launch browser windows if build_data_docs=True
    - Calls external Great Expectations APIs for validation and documentation building

