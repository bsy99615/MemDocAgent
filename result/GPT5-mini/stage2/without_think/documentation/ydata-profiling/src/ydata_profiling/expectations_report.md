# `expectations_report.py`

## `src.ydata_profiling.expectations_report.ExpectationHandler` · *class*

## Summary:
Initializes and configures a mapping from Visions type names to Great Expectations expectation-generator callables, and delegates type-specific expectation generation to the Handler base class.

## Description:
ExpectationHandler is a small adapter class that constructs the initial association between high-level Visions types (e.g., "Text", "Numeric", "DateTime") and a curated list of expectation-generating functions (from ydata_profiling.model.expectation_algorithms). It then delegates the remainder of the behavior to the generic Handler base class which finalizes type propagation using the Visions typeset DAG.

Typical scenarios:
- Instantiate once with a VisionsTypeset that describes the dataset's type hierarchy when producing Great Expectations expectation suites as part of a profiling run.
- Called by reporting or profiling code that needs to produce expectations for a column given its Visions-derived dtype, summary statistics, and a Great Expectations batch/validator object.

Responsibility boundary:
- This class only supplies the initial mapping of types to expectation functions and ensures that mapping and typeset are passed to Handler to build the DAG-completed mapping.
- It does not itself run the expectation-generating functions; those are executed by Handler.handle (inherited) after DAG completion.

## State:
Attributes inherited from Handler (documented here as they are established by ExpectationHandler):
- mapping: Dict[str, List[Callable]]
  - Description: maps Visions type name (string) to a list of callable expectation generator functions.
  - Valid keys (explicitly initialized by ExpectationHandler): "Unsupported", "Text", "Categorical", "Boolean", "Numeric", "URL", "File", "Path", "DateTime", "Image".
  - Initial values: each key maps to a single-element list referencing a corresponding function in expectation_algorithms, e.g. "Numeric" -> [expectation_algorithms.numeric_expectations].
  - Invariant: after Handler._complete_dag runs, mapping[str(child_type)] will contain a list equal to mapping[str(parent_type)] + mapping[str(child_type)] for edges parent->child in the Visions type DAG. In other words, mapping entries get extended so that child types inherit parent expectation generators (parent functions appear earlier in the list).
- typeset: VisionsTypeset
  - Description: the Visions typeset object that provides the type hierarchy (base_graph) used to propagate expectation generators along the graph.
  - Invariant: typeset.base_graph must be a graph acceptable to networkx line_graph and topological_sort (i.e., a directed acyclic graph over type nodes). The Handler._complete_dag assumes that iterating topological_sort over the line graph yields (from_type, to_type) pairs whose string forms are valid keys into mapping.

Notes on expectation-generator callables:
- Each callable referenced in mapping is expected to have a signature similar to:
  (name: str, summary: dict, batch: Any, *args) -> Tuple[str, dict, Any]
  - They usually call methods on the provided Great Expectations batch/validator and return the (name, summary, batch) triple for chaining.
- ExpectationHandler does not validate the signatures of the callables; it relies on the expectation_algorithms module to supply correctly-shaped functions.

## Lifecycle:
Creation:
- Required: a VisionsTypeset instance describing the type DAG.
- How to instantiate: ExpectationHandler(typeset)
  - __init__ builds the default mapping (see State) and calls the Handler constructor which in turn completes the DAG (propagating parent functions to children).

Usage:
- Typical sequence:
  1. Instantiate ExpectationHandler with a VisionsTypeset.
  2. For each column to profile, determine the Visions dtype string (the key used by mapping).
  3. Call the inherited handle(dtype, *args, **kwargs) method to run the composed expectation functions for that dtype. Commonly the args passed are (column_name: str, summary: dict, batch/validator: Any).
  4. The result returned by handle is the result of the composed pipeline (typically a tuple (name, summary, batch) after the sequence of expectation functions has been applied).
- Required ordering: instantiate before calling handle. There is no other required ordering between different handle calls; mapping is precomputed at construction time.

Destruction:
- No explicit cleanup is required from ExpectationHandler. It holds only in-memory structures (mapping and typeset). It does not open files or network connections and does not implement context manager or close methods.

## Method Map:
- The class defines only __init__ (it inherits behavior from Handler). Typical call-flow (method dependency graph):

graph LR
    EH__init__["ExpectationHandler.__init__"] --> Handler__init__["Handler.__init__"]
    Handler__init__ --> _complete_dag["Handler._complete_dag"]
    _complete_dag --> mapping["mapping mutated (parent funcs prepended to child keys)"]
    User["User code (profiling/report)"] --> Handler_handle["Handler.handle(dtype, *args)"]
    Handler_handle --> compose["compose(funcs)"]
    compose --> op["op(...) (composed expectation functions)"]
    op --> expectation_funcs["expectation_algorithms.* functions"]
    expectation_funcs --> batch_methods["Great Expectations validator methods called (side effects)"]

Notes:
- The expectation functions are invoked in the order they appear in mapping[dtype] after DAG completion; parent-type functions are placed before child-specific functions.

## Raises:
Possible exceptions that can surface when instantiating or using ExpectationHandler:
- TypeError
  - Condition: If the provided typeset is not a VisionsTypeset (or lacks the expected attributes such as base_graph). The constructor does not perform explicit type checks, so attribute access on an incompatible object will raise TypeError or AttributeError.
- KeyError
  - Condition: Handler._complete_dag performs lookups mapping[str(from_type)] and mapping[str(to_type)]. If the Visions typeset graph contains nodes (or edges / types) whose string names are not keys in the initial mapping created by ExpectationHandler, a KeyError will be raised during DAG completion. This means the initial mapping must cover all base type names that appear in typeset.base_graph (or the graph must only contain edges connecting the covered types).
- Any exception raised by the expectation generator functions or the Great Expectations batch/validator when those functions are later executed via handle; these will propagate from the call-site and are not caught by ExpectationHandler.

## Example:
- High-level (pseudocode usage; names reflect expected types):
  1. Prepare a VisionsTypeset (e.g., provided when profiling a pandas DataFrame).
  2. Create an ExpectationHandler:
     handler = ExpectationHandler(typeset)
  3. For a column named "age" whose Visions dtype is "Numeric", with a precomputed summary dict and a Great Expectations validator/batch (validator):
     result = handler.handle("Numeric", "age", summary, validator)
  4. The expectation generator functions in mapping["Numeric"] will be composed and run in sequence, each typically calling validator.expect_* methods. The result returned is the output of the composed functions (commonly the tuple (name, summary, batch/validator)).

Implementation notes for re-implementing:
- Build the mapping exactly as shown in the State section (strings to single-item lists referencing the expectation_algorithms functions).
- Pass mapping and the provided typeset to the Handler base class constructor (or replicate Handler.__init__ behavior: store mapping and typeset, then call the DAG completion routine).
- Ensure DAG completion concatenates parent lists onto child lists in the order given by a topological traversal of the line graph of typeset.base_graph, matching Handler._complete_dag semantics.
- Do not alter the expected callable signature of expectation_algorithms functions; Handler.handle composes them and expects each to return an updated (name, summary, batch) to allow chaining.

### `src.ydata_profiling.expectations_report.ExpectationHandler.__init__` · *method*

## Summary:
Initializes the ExpectationHandler by creating a Visions-type → expectations-algorithms mapping and delegating initialization to the Handler base class, thereby configuring the handler's internal behavior for generating expectations.

## Description:
This constructor constructs a mapping between Visions type names (e.g., "Text", "Numeric", "DateTime") and lists of expectation-algorithm providers taken from the expectation_algorithms module. After creating that mapping it calls the parent Handler.__init__ with the mapping and the provided typeset, forwarding any additional positional and keyword arguments.

Known callers and lifecycle:
- Called when an ExpectationHandler instance is created as part of the profiling/reporting pipeline, typically during the setup phase where expectations are prepared for columns based on their Visions types. This occurs prior to iterating over columns to generate expectations.
- It is invoked at object construction time (i.e., when code needs a configured handler that maps Visions types to expectation generators).

Why this is a separate method:
- Encapsulates the mapping construction and parent-delegation in one place to keep subclass-specific configuration separated from generic Handler initialization logic contained in the base class.
- Keeping this logic in __init__ prevents duplication and centralizes the mapping definition for easier maintenance and testing.

## Args:
    typeset (VisionsTypeset):
        - The Visions typeset describing how data types were inferred for columns.
        - Must be an instance compatible with visions. It is used to interpret column types and to allow the Handler to map types to expectations.
    *args: 
        - Additional positional arguments forwarded to Handler.__init__. No constraints are enforced here; validity depends on the Handler initializer.
    **kwargs:
        - Additional keyword arguments forwarded to Handler.__init__. No constraints are enforced here; validity depends on the Handler initializer.

## Returns:
    None
    - As a constructor, it does not return a value. On successful completion, the ExpectationHandler instance is constructed and ready for use (with internal state configured by the Handler base class).

## Raises:
    - Propagates any exception raised by Handler.__init__ or by invalid arguments passed through *args/**kwargs.
      For example, if Handler.__init__ enforces types/structure and raises TypeError or ValueError, those exceptions will bubble up from this constructor.
    - No new exceptions are raised directly within this method by its own code.

## State Changes:
    Attributes READ:
        - None directly read from self by this method.
    Attributes WRITTEN:
        - None directly assigned on self by this method.
        - Indirect / delegated: this constructor calls Handler.__init__(mapping, typeset, *args, **kwargs). The Handler implementation is responsible for initializing instance state (for example, storing the provided mapping and typeset on the instance). The exact attributes written depend on Handler.__init__.

## Constraints:
    Preconditions:
        - typeset should be a VisionsTypeset or a compatible object expected by the Handler base class.
        - Any positional/keyword arguments must satisfy the preconditions of Handler.__init__.
    Postconditions:
        - If no exception is raised, the returned object (self) is a fully-initialized ExpectationHandler, with its behavior configured according to the mapping defined in this constructor and any additional initialization performed by Handler.__init__.

## Side Effects:
    - No I/O operations, network calls, or filesystem interactions occur in this method.
    - The only side effect is the initialization of instance state via the call to the parent Handler.__init__, which may register or store the mapping and typeset on the instance.
    - The method references modules (expectation_algorithms) to build the mapping (this only constructs references to provider objects; it does not execute their heavy logic).

## `src.ydata_profiling.expectations_report.ExpectationsReport` · *class*

## Summary:
Represents an adapter that converts a profiling report (dataframe + description) into a Great Expectations expectation suite, optionally running validation and building documentation.

## Description:
ExpectationsReport is an abstraction that knows how to take the profiling state produced by the ydata-profiling pipeline (a pandas DataFrame `df`, a `config` containing a `title`, and a description produced by get_description()) and convert it into a Great Expectations expectation suite. It encapsulates orchestration logic: creating or reusing a Great Expectations DataContext, creating an expectation suite, populating expectations per-variable using a Handler, optionally validating the data against the generated suite, saving the suite, and optionally building + opening the GE data docs.

Typical instantiation scenarios:
- A higher-level profiling Report generator creates an instance (or subclass) of ExpectationsReport, assigns `config` (Settings), sets `df` to the profiled DataFrame, and either relies on the default `typeset` property (None) or overrides it to return a VisionsTypeset instance.
- Callers call to_expectation_suite(...) to produce and persist an expectation suite and (optionally) validate and publish docs.

Motivation and responsibility:
- Keeps the responsibility of converting profiling output into expectations centralized and decoupled from the rest of the profiling code.
- Delegates per-variable expectation creation logic to a Handler (or custom handler implementing the same interface), making expectation generation algorithm pluggable.

## State:
Public attributes and expected types:
- config (Settings)
  - Type: ydata_profiling.config.Settings
  - Required: yes (must have attribute `title` used for suite naming when suite_name not provided)
  - Constraint: config.title must be a non-empty string when suite_name is omitted
  - Invariant: remains constant for the lifetime of the instance unless caller mutates it.

- df (Optional[pandas.DataFrame])
  - Type: pandas.DataFrame or None
  - Default: None
  - Constraint: to_expectation_suite requires df to be a valid pandas.DataFrame; if df is None a TypeError or equivalent will be raised by the Great Expectations PandasDataset constructor.
  - Invariant: df should represent the dataset being profiled and not be mutated externally in ways that invalidate the previously generated expectation suite.

- typeset (property) -> Optional[VisionsTypeset]
  - Type: visions.VisionsTypeset or None
  - Default implementation returns None
  - Intention: subclasses can override this property to provide a VisionsTypeset which may be required by the default ExpectationHandler (or other handlers) to determine types/expectations.

Implied (not stored here but required to exist):
- get_description() method (callable on self)
  - Expected to return a BaseDescription instance (from ydata_profiling.model)
  - BaseDescription.variables must be a mapping: variable_name -> variable_summary dict
  - variable_summary must contain at least a "type" key; its other keys are passed to the Handler for decision-making.

Handler interface requirements (expected by to_expectation_suite):
- A Handler-like object with a method:
  - handle(type_name: str, variable_name: str, variable_summary: dict, batch: Any) -> None
- The handler will be invoked for each variable in the description to add expectations to the Great Expectations batch/dataset.

Class invariants:
- After to_expectation_suite completes successfully, a valid expectation suite representing `df` should be returned (as provided by Great Expectations).
- get_description() must return a BaseDescription whose variables correspond to columns present in df.

## Lifecycle:
Creation:
- There is no explicit __init__ in this component; instantiate by creating an object and ensuring the following attributes exist:
  - set instance.config to a Settings object (with non-empty title if you plan to rely on default suite name)
  - set instance.df to a pandas.DataFrame containing the data to generate expectations for
  - optionally override typeset property by subclassing or monkey-patching to provide a VisionsTypeset

Usage (typical sequence):
1. Prepare instance with config and df set.
2. (Optional) If custom handling is required, provide a `handler` implementing the Handler.handle(...) method, or allow the default handler to be constructed (ExpectationHandler expected to accept a typeset argument).
3. Call to_expectation_suite(...). Parameters and their effects:
   - suite_name: Optional[str] — explicit GE expectation suite name (if omitted the slugified config.title is used).
   - data_context: Optional[Any] — a Great Expectations DataContext object; if omitted, a new ge.data_context.DataContext() is created (requires GE installed and configured).
   - save_suite: bool (default True) — if True, calls data_context.save_expectation_suite(suite).
   - run_validation: bool (default True) — if True, re-creates a batch for validation and runs data_context.run_validation_operator("action_list_operator", assets_to_validate=[batch]), capturing the validation result identifier for opening docs.
   - build_data_docs: bool (default True) — if True, runs data_context.build_data_docs() and data_context.open_data_docs(validation_result_identifier).
   - handler: Optional[Handler] — custom handler instance to populate expectations; when None the code constructs ExpectationHandler(self.typeset).

Sequencing constraints:
- get_description() must be available and produce a description before handler.handle calls.
- If run_validation is True, validation uses the created suite and the dataset df; DataContext configuration (expectations store, validation operators) must include an operator named "action_list_operator" for run_validation to succeed.

Destruction / Cleanup:
- No special cleanup is required by this class.
- However, side effects to external systems occur: expectation suite saved to Great Expectations stores and data docs may be built and opened.
- If the DataContext opens web docs, the calling environment may spawn or require browser interaction; callers may need to manage DataContext lifecycle externally.

## Method Map:
Flowchart (Mermaid) showing the call flow of to_expectation_suite:

graph LR
  A[to_expectation_suite(...)] --> B{Import great_expectations}
  B -->|missing| E[Raise ImportError]
  B -->|ok| C[determine suite_name (slugify config.title if None)]
  C --> D{handler provided?}
  D -->|yes| F[use handler]
  D -->|no| G[handler = ExpectationHandler(typeset)]
  G --> H{data_context provided?}
  H -->|no| I[data_context = ge.data_context.DataContext()]
  H -->|yes| I2[use provided data_context]
  I --> J[data_context.create_expectation_suite(...)]
  J --> K[batch = ge.dataset.PandasDataset(df, expectation_suite=suite)]
  K --> L[summary = self.get_description()]
  L --> M[for each variable in summary.variables: handler.handle(..., batch)]
  M --> N[suite = batch.get_expectation_suite()]
  N --> O{run_validation?}
  O -->|yes| P[create new batch; data_context.run_validation_operator(...)]
  P --> Q[validation_result_identifier = results.list_validation_result_identifiers()[0]]
  O -->|no| R[validation_result_identifier = None]
  N --> S{save_suite or build_data_docs?}
  S -->|True| T[data_context.save_expectation_suite(suite)]
  S -->|False| U[skip save]
  S --> V{build_data_docs?}
  V -->|True| W[data_context.build_data_docs(); data_context.open_data_docs(validation_result_identifier)]
  V -->|False| X[skip docs]
  W --> Y[return batch.get_expectation_suite()]

(Note: the above Mermaid graph nodes correspond to the logical steps executed by to_expectation_suite.)

## Raises:
- ImportError
  - Trigger: Great Expectations is not installed; the method explicitly raises ImportError with message "Please install great expectations before using the expectation functionality".
- AttributeError / KeyError
  - Trigger: If self.config has no attribute `title` and suite_name is omitted, slugify(self.config.title) will raise AttributeError.
  - Trigger: If get_description() does not return a BaseDescription-like object with `.variables` mapping, iterating or indexing it will raise AttributeError/KeyError.
- TypeError / ValueError (indirect)
  - Trigger: If self.df is None or not a pandas.DataFrame, constructing ge.dataset.PandasDataset(self.df, ...) will raise a TypeError or ValueError coming from Great Expectations or pandas.
- IndexError
  - Trigger: When run_validation is True but the results list returned by run_validation_operator has no identifiers, indexing [0] will raise IndexError.
- Exceptions raised by Great Expectations/DataContext APIs
  - Trigger: data_context.create_expectation_suite, run_validation_operator, save_expectation_suite, build_data_docs, or open_data_docs may raise GE-specific exceptions if the DataContext is misconfigured (e.g., missing stores, missing "action_list_operator", or permission errors).
- Any exceptions raised by handler.handle(...) (these are passed through).

## Example:
Step-by-step example usage (no code shown to avoid embedding source):
1. Prepare a Settings instance and set its title attribute to "My Dataset Profile".
2. Prepare a pandas.DataFrame containing the data to profile and assign it to the instance.df attribute.
3. Ensure the instance implements get_description() returning a BaseDescription where `variables` maps column names to summaries (each summary includes at least a "type" key).
4. Optionally override the typeset property to return a VisionsTypeset if the default handler requires it.
5. Call to_expectation_suite() with optional parameters:
   - Omit `suite_name` to generate a suite name from the slugified config.title.
   - Provide a Great Expectations DataContext if you want control over where suites/docs are stored.
   - Set save_suite, run_validation, and build_data_docs flags according to whether you want to persist or validate/evaluate the suite.
6. Observe side effects:
   - The expectation suite will be created/overwritten in the specified DataContext.
   - If run_validation=True, validation will be executed via the configured "action_list_operator".
   - If build_data_docs=True, GE data docs will be built and opened (using the validation result identifier when available).
7. The method returns the final expectation suite (as produced by Great Expectations' batch.get_expectation_suite()).

Implementation notes for re-creation:
- Ensure to import great_expectations inside to_expectation_suite and raise an informative ImportError if unavailable.
- Use slugify(self.config.title) when suite_name is not provided.
- Create or accept a ge.data_context.DataContext object; call create_expectation_suite(suite_name, overwrite_existing=True).
- Use ge.dataset.PandasDataset(self.df, expectation_suite=suite) to create a batch for populating expectations.
- Rely on get_description() to obtain per-variable summaries and iterate through summary.variables to let the handler add expectations to the batch.
- After populating expectations, call batch.get_expectation_suite() and optionally run validation and save/build docs as described above.

### `src.ydata_profiling.expectations_report.ExpectationsReport.typeset` · *method*

## Summary:
Returns the VisionsTypeset used by this report for mapping column/variable types, or None if no typeset is provided. This method does not modify the object's state.

## Description:
Known callers:
- ExpectationsReport.to_expectation_suite — invoked when converting a profiling report into a Great Expectations expectation suite; the returned value is passed to the ExpectationHandler constructor inside that pipeline step.

Context / lifecycle stage:
- This property is read during the "export to expectations" stage of the profiling report lifecycle (specifically inside to_expectation_suite) to obtain any Visions type-system configuration required by expectation-generation code.

Purpose:
- Encapsulates the source of a VisionsTypeset so the type mapping can be customized or overridden in subclasses without changing the expectation-generation logic. Keeping it as a separate property separates configuration (which Visions typeset to use) from the algorithm that generates expectations.

## Args:
- None

## Returns:
- Optional[VisionsTypeset]
    - If a VisionsTypeset instance is available, it should be returned here so callers (e.g., ExpectationHandler) can use it to interpret variable types.
    - Current implementation returns None to indicate no explicit typeset is provided.
    - Edge cases: returning None is valid (current behavior); callers must handle the None case (behavior depends on the caller implementation).

## Raises:
- None — this property does not raise exceptions in its current implementation.

## State Changes:
- Attributes READ:
    - None (the current implementation does not access any self.<attr> fields)
- Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
- None enforced by this property. Callers expecting a non-None VisionsTypeset must ensure an appropriate override provides one.

Postconditions:
- After calling, the caller receives either None or a VisionsTypeset. The object's attributes remain unchanged.

## Side Effects:
- None. This property performs no I/O, does not call external services, and does not mutate any objects outside self.

### `src.ydata_profiling.expectations_report.ExpectationsReport.to_expectation_suite` · *method*

## Summary:
Export the profiling report into a Great Expectations ExpectationSuite stored in the provided or a newly-created DataContext, optionally run validation and build/open data docs. The method does not modify the ExpectationsReport object's attributes.

## Description:
This method integrates a profiling report with Great Expectations (GE) by:
1. Lazily importing GE (raises ImportError if GE is absent).
2. Determining an expectation suite name (uses slugify(self.config.title) when suite_name is None).
3. Creating or using a GE DataContext.
4. Creating an expectation suite in that DataContext with overwrite_existing=True.
5. Building a GE PandasDataset batch from self.df attached to that suite.
6. Obtaining the profiling summary from self.get_description() and invoking handler.handle for each column to add expectations to the batch.
7. Retrieving the expectation suite from the batch, optionally recreating the batch and running a validation operator, saving the suite (when requested), and optionally building/opening data docs.

Known callers / lifecycle:
- Used after profiling a DataFrame to export generated expectations for later validation, monitoring, or sharing.
- Typical lifecycle: invoked post-profile to produce a GE suite, optionally validate the dataset, and publish data docs.

Why this is a separate method:
- It coordinates multiple side-effecting operations with an external library (imports, DataContext initialization, suite creation/saving, validation operator execution, and docs publishing). Separating it keeps GE integration isolated and configurable.

## Args:
    suite_name (Optional[str] = None):
        Name for the GE expectation suite. If None, slugify(self.config.title) is used.
    data_context (Optional[Any] = None):
        Existing Great Expectations DataContext to use. If falsy, the method instantiates ge.data_context.DataContext().
    save_suite (bool = True):
        If True, triggers data_context.save_expectation_suite(suite). Note: the suite is also saved when build_data_docs is True even if save_suite is False.
    run_validation (bool = True):
        If True, the method recreates a PandasDataset batch bound to the suite and runs the "action_list_operator" via data_context.run_validation_operator(...).
    build_data_docs (bool = True):
        If True, after saving the suite (see above), the method calls data_context.build_data_docs() and data_context.open_data_docs(validation_result_identifier). If validation was not run, the identifier passed to open_data_docs will be None.
    handler (Optional[Handler] = None):
        Handler instance used to convert a column's profiling summary into GE expectations. If None, a default ExpectationHandler(self.typeset) is created.
        Required handler.handle signature and calling convention:
            handler.handle(dtype, column_name, variable_summary, batch)
        The method calls handler.handle(variable_summary["type"], name, variable_summary, batch) for each column.

## Returns:
    Any
        The expectation suite obtained from the final batch.get_expectation_suite() call. Concretely, this is the GE ExpectationSuite representation (commonly great_expectations.core.expectation_suite.ExpectationSuite or a dict-like equivalent). Notes:
        - The returned suite reflects expectations added by handler.handle prior to the final get_expectation_suite() call.
        - If run_validation is True, the method recreates the batch prior to validation and returns the suite from that final batch; otherwise it returns the suite from the batch used to add expectations.

## Raises:
    ImportError
        If great_expectations is not installed: raises ImportError with message
        "Please install great expectations before using the expectation functionality".
    AttributeError / KeyError / TypeError / ValueError / Exception
        Errors propagated from downstream operations, including:
        - Accessing self.config.title (AttributeError) if config/title are missing when suite_name is None.
        - ge.dataset.PandasDataset(self.df, ...) raising if self.df is None or incompatible (TypeError/ValueError).
        - Constructing ExpectationHandler(self.typeset) raising TypeError/KeyError if self.typeset is None or incompatible with the initial mapping/DAG completion.
        - Missing expected keys in profiling summaries (e.g., variable_summary["type"]) causing KeyError.
        - Exceptions from handler.handle or GE API calls (create_expectation_suite, save_expectation_suite, run_validation_operator, build_data_docs, open_data_docs), which are not caught and will propagate.

## State Changes:
Attributes READ:
    self.config (self.config.title used when suite_name is None)
    self.typeset (used to construct ExpectationHandler when handler is None)
    self.df (used to create ge.dataset.PandasDataset(self.df, expectation_suite=suite))
    self.get_description() (invoked to produce the BaseDescription; its .variables mapping is iterated)

Attributes WRITTEN:
    None — the ExpectationsReport instance is not mutated by this method.

## Constraints:
Preconditions:
    - great_expectations must be installed.
    - self.df must be a pandas.DataFrame or otherwise compatible with ge.dataset.PandasDataset.
    - If handler is None, self.typeset must be a VisionsTypeset whose base_graph node names are present in ExpectationHandler's initial mapping.
    - self.get_description() must return a BaseDescription-like object with a .variables mapping where each variable_summary contains a "type" key.

Postconditions:
    - An expectation suite named suite_name exists in the DataContext (created with overwrite_existing=True).
    - The returned value is the expectation suite attached to the last batch created in the method.
    - If save_suite is True or build_data_docs is True, data_context.save_expectation_suite(suite) is called.
    - If run_validation is True, a validation run was executed via the "action_list_operator", producing a validation_result_identifier used by open_data_docs if docs are built.
    - If build_data_docs is True, data docs were built and an attempt to open them was made.

## Side Effects:
    - Imports great_expectations (module import).
    - If data_context is falsy, instantiates ge.data_context.DataContext(), which may read GE config from disk.
    - Constructs and mutates GE batch/validator state via ge.dataset.PandasDataset(self.df, expectation_suite=suite) and handler.handle(...). Handler typically calls GE expect_* methods which add expectations to the suite.
    - Calls GE APIs that perform I/O and external effects:
        * data_context.create_expectation_suite(..., overwrite_existing=True)
        * data_context.save_expectation_suite(...)
        * data_context.run_validation_operator(..., assets_to_validate=[batch])
        * data_context.build_data_docs()
        * data_context.open_data_docs(validation_result_identifier)
    - Recreates the GE batch prior to running validation, so the batch returned at the end may be the validation-bound batch.
    - Any side effects from handler.handle or expectation-generator functions (e.g., additional I/O) will occur.

