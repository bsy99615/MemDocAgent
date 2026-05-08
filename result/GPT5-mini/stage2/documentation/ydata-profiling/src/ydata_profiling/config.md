# `config.py`

## `src.ydata_profiling.config._merge_dictionaries` · *function*

## Summary:
Recursively merges keys from a source dictionary into a target dictionary without overwriting existing keys in the target; nested dictionaries are merged depth-first. The target dictionary is mutated in place and returned.

## Description:
Walks the source mapping (first parameter) and merges its contents into the target mapping (second parameter) using these rules:
- If a value in the source is a mapping (dict), the function ensures the corresponding key exists in the target as a mapping (creating an empty mapping if missing) and then recursively merges the nested mapping.
- If a value in the source is not a mapping, the value is copied into the target only if the target does not already contain that key.

Known callers within the codebase:
- No direct call sites were discovered in the scanned files for this analysis. The function is implemented in the configuration module and is intended for internal use when combining layered configuration dictionaries (e.g., filling missing configuration keys from defaults while preserving explicit user-provided values).

Why this logic is a standalone function:
- Centralizes a consistent, non-overwriting deep-merge policy so higher-level configuration code remains focused on I/O and validation.
- Makes it easy to update merge semantics (e.g., handling lists or overwrite policies) in a single place.
- Encapsulates recursive traversal logic to avoid duplication across the codebase.

## Args:
    dict1 (dict): Source dictionary to merge from.
        - Required: mapping-like object; function calls dict1.items().
        - Values may be scalars or nested dict objects; nested dict values trigger recursion.
    dict2 (dict): Target dictionary to merge into.
        - Required: mutable mapping-like object; function uses dict2.setdefault(key, default) and assigns dict2[key] = val.
        - Mutated in place; returned value is the same object.

Interdependencies:
- The function assumes mapping-like behavior for both arguments at all levels of nesting. In particular, whenever dict1 has a dict at some nested key, the corresponding value in dict2 must either be absent or itself be a mapping; otherwise a runtime AttributeError will occur.

## Returns:
    dict: The same object passed as dict2, after being mutated to include keys from dict1 that were absent in dict2.
    - Typical return: dict2 augmented with missing keys from dict1 without overwriting existing dict2 values.
    - Edge cases:
        * If dict1 is empty, dict2 is returned unchanged.
        * If dict2 is empty, the returned mapping reflects dict1's structure (nested dicts copied/created as needed).
        * If dict1 contains a dict for a key and dict2 contains a non-dict for the same key, the function will raise (see Raises).

## Raises:
    AttributeError:
        - Trigger: When the function attempts to call dict2.setdefault(key, {}) on a value that exists in dict2 but is not a mapping (for example, a string or number). In nested merges, this occurs if dict1 has a dict at a nested path but dict2 has a non-dict at the same path.
        - Symptom: "'<type>' object has no attribute 'setdefault'" (or similar), raised at the attempt to call setdefault on a non-mapping.
    TypeError or AttributeError:
        - Trigger: If dict1 does not support .items() or dict2 does not support item assignment, Python will raise a TypeError or AttributeError when those methods/operations are used.
    RecursionError:
        - Trigger: Extremely deep nested dictionaries may exceed Python's recursion limit during recursion.
    Notes:
        - The function performs no explicit input validation; callers should ensure correct types to avoid these runtime exceptions.

## Constraints:
Preconditions:
    - Both dict1 and dict2 (and any nested values expected to be merged) must be mapping-like where dict1 provides dicts: specifically, for any key K where dict1[K] is a dict, either K must not exist in dict2 or dict2[K] must itself be a dict-like object.
    - Caller must accept that dict2 will be mutated in place.
Postconditions:
    - After successful return, dict2 contains all its original keys and additional keys from dict1 that were missing.
    - No key that existed in dict2 is overwritten by dict1.
    - Nested merging has been applied for keys where both dict1 and dict2 contain mappings.

## Side Effects:
    - Mutates dict2 in place.
    - No file, network, or external-service effects.
    - No modification of dict1.

## Control Flow:
flowchart TD
    Start([Start]) --> Loop{For each key,val in dict1.items()}
    Loop --> IsDict{Is val a dict?}
    IsDict -- Yes --> EnsureNode[dict2_node = dict2.setdefault(key, {})]
    EnsureNode --> IsMapping{Is dict2_node mapping-like?}
    IsMapping -- Yes --> Recurse[_merge_dictionaries(val, dict2_node)]
    IsMapping -- No --> RaiseAttr[AttributeError: no setdefault on non-mapping]
    Recurse --> Loop
    IsDict -- No --> Exists{key in dict2?}
    Exists -- Yes --> Skip[Do nothing (preserve dict2)]
    Exists -- No --> Assign[dict2[key] = val]
    Assign --> Loop
    Loop --> End([Return dict2])

## Examples:
- Example 1 (nested merge, preserve existing):
    Input:
        dict1 = {"a": 1, "b": {"x": 10, "y": 20}}
        dict2 = {"b": {"x": 100}, "c": 3}
    Result (returned dict2):
        {"b": {"x": 100, "y": 20}, "c": 3, "a": 1}
    Explanation: Existing values in dict2 (b.x) are preserved; missing nested keys from dict1 (b.y) are added; top-level a is added.

- Example 2 (conflict: non-mapping in target -> error):
    Input:
        dict1 = {"d": {"k": 1}}
        dict2 = {"d": "string"}
    Behavior:
        The call attempts dict2.setdefault("d", {}) but dict2["d"] exists and is a string; since strings do not have setdefault, an AttributeError is raised.
    Handling:
        To avoid the exception, ensure dict2 has a mapping at "d" (e.g., convert or replace the value) before calling, or catch AttributeError and handle the conflict explicitly.

- Example 3 (empty target):
    Input:
        dict1 = {"x": {"y": 2}, "z": 3}
        dict2 = {}
    Result (returned dict2):
        {"x": {"y": 2}, "z": 3}

Usage notes:
    - If callers require overwrite semantics (replace dict2 values with dict1's), or merging into non-mapping target values, this function is not appropriate without modification.
    - To preserve both structures when conflicts exist, callers can:
        * Pre-normalize dict2 so that any key present in dict1 as a mapping is a mapping in dict2 as well, or
        * Call the function on deep copies to avoid in-place mutation, or
        * Wrap the call in try/except to catch AttributeError and implement custom conflict resolution.

## `src.ydata_profiling.config.Dataset` · *class*

## Summary:
A typed container for dataset-level metadata used by the profiling configuration; holds descriptive attributes (description, creator, author, copyright, year, and url).

## Description:
This class models basic textual metadata about a dataset and is intended to be embedded in higher-level configuration objects or passed to reporting/metadata consumers that annotate profiling outputs. Instantiate Dataset when you need a small, validated holder for human-readable dataset metadata (for example, when building or loading an overall profiling configuration). It exists to provide a consistent schema and to leverage pydantic's validation/serialization for configuration persistence and transmission.

Typical instantiation scenarios:
- As the dataset metadata section inside a configuration loader or factory that constructs the profiling configuration.
- Attached to a profiling report object or exported report to supply dataset provenance and description.
- Created in tests or examples to assert serialization behavior or defaults.

Responsibility boundary:
- Stores only textual metadata fields and delegates all validation/coercion to pydantic.v1.BaseModel.
- Does not perform I/O, network requests, or enforce complex constraints such as URL format or numeric year ranges.

## State:
All attributes are public pydantic model fields and are strings after model validation/coercion.

- description: str
  - Default: "" (empty string)
  - Meaning: Human-readable description of the dataset.
  - Constraints: any string allowed; empty string is a valid value.

- creator: str
  - Default: "" (empty string)
  - Meaning: The agent/process that created the dataset.
  - Constraints: any string.

- author: str
  - Default: "" (empty string)
  - Meaning: Primary author or owner of the dataset content.
  - Constraints: any string.

- copyright_holder: str
  - Default: "" (empty string)
  - Meaning: Entity holding the copyright.
  - Constraints: any string.

- copyright_year: str
  - Default: "" (empty string)
  - Meaning: Copyright year or year range as textual data.
  - Constraints: any string (e.g., "2023" or "2020-2023"); no numeric enforcement.

- url: str
  - Default: "" (empty string)
  - Meaning: URL referencing dataset source or documentation.
  - Constraints: any string; URL format is not validated by this model.

Class invariants:
- After instantiation, all declared fields are present and have str types (pydantic ensures coercion where possible).
- There are no enforced relations between fields; any combination of values (including empty strings) is permitted.

## Lifecycle:
Creation:
- Instantiate with zero or more keyword arguments matching field names:
  - No-arg construction yields an instance with all fields as empty strings.
  - Example (conceptual): provide description="..." or author="..." to set those fields.
- During construction, pydantic.v1.BaseModel performs coercion and validation. Values are coerced to str when possible.

Usage:
- Access fields directly as attributes (e.g., instance.description, instance.url).
- Serialize for persistence or transmission using BaseModel helpers such as dict() or json() when embedding into larger configurations or report payloads.
- There is no required call ordering; the instance behaves as a plain data holder.

Destruction / cleanup:
- No explicit cleanup required. This model does not manage external resources and is not a context manager.

## Method Map:
Mermaid graph showing typical interactions:

graph TD
    A[Instantiate Dataset] --> B[pydantic.v1 validation / coercion]
    B --> C[Access attributes directly]
    C --> D[Embed into Report or Config]
    D --> E[Serialize with .dict() or .json()]

(Only instantiation triggers runtime behavior beyond storage: pydantic's validation/coercion.)

## Raises:
- pydantic.v1.ValidationError (the validation error class raised by pydantic during model construction)
  - Trigger: Raised if provided values cannot be coerced to the declared types (here, str) or violate any validation rules applied by pydantic (including any custom validators configured higher in the model hierarchy).
  - Practical note: Most common Python values are coercible to str; this exception is uncommon unless inputs are deliberately non-serializable or pydantic is configured with strict validators.

## Example:
- Default metadata container: construct Dataset() to obtain an instance where every field is the empty string.
- Partial metadata: construct with a subset of fields (e.g., supply description and url) to populate only those values and inherit defaults for the rest.
- Embedding and serialization: include the Dataset instance in a larger configuration object and call the model's serialization helpers (dict() or json()) to persist or transmit the metadata.
- Accessing values: read instance.author or instance.description when rendering report headers or UI labels.

## `src.ydata_profiling.config.NumVars` · *class*

## Summary:
Typed pydantic configuration model that centralizes numeric-variable profiling heuristics (quantiles to compute and numeric-analysis thresholds).

## Description:
NumVars is a lightweight pydantic.v1 BaseModel that groups configuration values used when profiling numeric features. It exists so numeric-related heuristics (which quantiles to compute, what counts as low-cardinality, skewness handling, and a chi-squared threshold) are maintained in one place and can be overridden by consumers.

When to instantiate:
- When constructing the profiler’s global configuration object (a higher-level Config/Settings class typically composes NumVars).
- In tests or user code that override numeric-analysis defaults for a particular profiling run.

Motivation and responsibility boundary:
- Responsibility: hold numeric-analysis tuning parameters (no algorithms or logic).
- It does not perform range validation or enforce inter-field invariants — it delegates type validation to pydantic and expects downstream code to enforce semantic constraints (e.g., quantile values in [0, 1] or non-negative thresholds) if required.

## State:
All fields are public pydantic model fields. Types and defaults are taken directly from the class definition.

- quantiles: List[float]
    - Default: [0.05, 0.25, 0.5, 0.75, 0.95]
    - Meaning: Probability levels for which the profiler should compute quantiles for numeric variables.
    - Expected domain: floats in [0.0, 1.0]; expected to be sorted and unique by downstream consumers.
    - Important note: The default value is a mutable list object defined at the class level. Pydantic.v1 uses the default object as provided — mutating this list in-place (e.g., append/pop) may be observed across different NumVars instances. To avoid shared-state bugs, replace the list rather than mutate it in-place or construct instances with an explicit list.

- skewness_threshold: int
    - Default: 20
    - Meaning: Integer threshold used by numeric-analysis routines to decide when skewness is considered extreme.
    - Expected domain: integer; typically >= 0.

- low_categorical_threshold: int
    - Default: 5
    - Meaning: Maximum number of distinct values at or below which a numeric variable may be considered "low-cardinality categorical".
    - Expected domain: integer >= 0.

- chi_squared_threshold: float
    - Default: 0.999
    - Meaning: Probability threshold (e.g., p-value cutoff or critical probability) used in chi-squared related comparisons.
    - Expected domain: float in [0.0, 1.0].

Class invariants:
- NumVars enforces no cross-field invariants (e.g., quantiles sortedness or range checks). Only type validation is performed by pydantic at instantiation. Any semantic or cross-field constraints must be enforced by callers.

## Lifecycle:
Creation:
- All fields have defaults; create with defaults:
    nv = NumVars()
- Override one or more fields at instantiation:
    nv2 = NumVars(quantiles=[0.1, 0.5, 0.9], low_categorical_threshold=3)
- Because quantiles has a mutable default, prefer providing a fresh list at construction if you intend to mutate it:
    nv_safe = NumVars(quantiles=list([0.05, 0.25, 0.5]))

Validation behavior on creation:
- Pydantic validates and (by default) coerces types on instantiation. For example, an integer in the quantiles list will be coerced to float where possible.

Mutation and updates:
- By default, pydantic.v1 BaseModel instances are mutable (attribute assignment is allowed). Assignment validation (validating values on attribute assignment) is disabled unless BaseModel.Config.validate_assignment is set to True. Since NumVars does not set Config, attribute assignment will not be validated automatically.
- Recommended safe update: use the pydantic .copy(update={...}) method to produce a new validated instance:
    nv3 = nv.copy(update={"quantiles": [0.1, 0.5]})

Destruction:
- No cleanup or resource management required. Instances are regular objects managed by Python GC.

## Method Map:
Minimal interaction flow (Mermaid flowchart).

flowchart TD
    A[Instantiate NumVars()] --> B[Read fields (quantiles, thresholds)]
    B --> C[Profiler numeric-analysis consumes fields]
    B --> D[Update via .copy(update=...) to obtain new validated instance]
    note right of B: In-place mutation of quantiles\nmay affect other instances if not careful

## Raises:
- pydantic.error_wrappers.ValidationError
    - Trigger: when provided values cannot be coerced to the annotated types on instantiation (e.g., quantiles="not-a-list", or an inner element that cannot be converted to float).
- No custom exceptions are raised by NumVars itself. Range or semantic violations (e.g., quantiles outside [0,1]) are not enforced here and thus do not raise by default.

## Example:
Create with defaults:
    nv = NumVars()
    # nv.quantiles == [0.05, 0.25, 0.5, 0.75, 0.95]
    # nv.chi_squared_threshold == 0.999

Override fields safely:
    nv2 = NumVars(quantiles=[0.1, 0.5, 0.9], low_categorical_threshold=3)

Avoid accidental shared mutable default:
    nv_a = NumVars()                      # uses class-level default list object
    nv_b = NumVars()
    # Do NOT mutate in-place if you want instances independent:
    nv_a.quantiles.append(0.99)           # may affect nv_b.quantiles as well
    # Preferred pattern to change quantiles for a new config:
    nv_c = nv_a.copy(update={"quantiles": [0.05, 0.25, 0.5, 0.75, 0.95, 0.99]})

Invalid construction (raises pydantic ValidationError):
    NumVars(quantiles="not-a-list")  # ValidationError: quantiles must be a list of floats

## `src.ydata_profiling.config.TextVars` · *class*

## Summary:
A minimal Pydantic model that declares four boolean configuration flags: length, words, characters, and redact.

## Description:
TextVars is defined as a subclass of pydantic.v1.BaseModel and serves as a typed container for four boolean flags. The class body declares the fields and their defaults; no additional methods or behaviors are defined in the provided source snippet.

Purpose and responsibility:
- Provide a single structured object that contains four named boolean flags with defaults as part of the configuration surface. The class itself only defines the fields and their default values.

## State:
Constructor parameters and corresponding instance attributes (names, types, and defaults exactly as declared)
- length: bool
  - Default: True
  - Notes: Field declared on the class; value is the instance attribute after construction.
- words: bool
  - Default: True
  - Notes: Field declared on the class; value is the instance attribute after construction.
- characters: bool
  - Default: True
  - Notes: Field declared on the class; value is the instance attribute after construction.
- redact: bool
  - Default: False
  - Notes: Field declared on the class; value is the instance attribute after construction.

Class invariants (as visible in source):
- The class defines these four attributes with their defaults. No cross-field invariants or validation logic are declared in this source snippet.

## Lifecycle:
Creation:
- Instantiate directly by calling TextVars() or TextVars(length=<bool>, words=<bool>, characters=<bool>, redact=<bool>).
- The class inherits from pydantic.v1.BaseModel (imported in the file); construction uses Python keyword arguments corresponding to the declared fields.

Usage:
- After instantiation, read attribute values via standard attribute access (e.g., instance.length).
- No custom instance methods are defined in this class in the provided source.

Destruction:
- No cleanup, context-manager protocol, or close semantics are defined in this class.

## Method Map:
graph LR
  A[Call TextVars(...)] --> B[Instance created with attributes: .length .words .characters .redact]
  B --> C[Caller reads attributes as needed]

(There are no custom methods or internal call chains defined in TextVars.)

## Raises:
- The class body does not explicitly raise exceptions. The class inherits from pydantic.v1.BaseModel; any runtime behavior related to BaseModel (such as instantiation-time validation) is provided by Pydantic but is not defined in this source snippet.

## Example:
- Instantiate with defaults:
  tv = TextVars()
  # tv.length == True
  # tv.words == True
  # tv.characters == True
  # tv.redact == False

- Instantiate with overrides:
  tv = TextVars(length=False, redact=True)
  # tv.length == False
  # tv.redact == True

- Access attributes:
  if tv.words:
      # read the flag and branch accordingly
      pass

## `src.ydata_profiling.config.CatVars` · *class*

## Summary:
Typed configuration container for options that govern categorical-variable analysis. Provides explicit, documented defaults for boolean flags, numeric thresholds, and lists used by profiling routines to detect, summarize, and visualize categorical features.

## Description:
CatVars is a lightweight Pydantic BaseModel used as the categorical-section of a larger profiling configuration. Instantiate this model when you need to:
- Configure which categorical diagnostics to run (length, character, word-level summaries).
- Set thresholds controlling cardinality detection, balancing decisions, and histogram sizing.
- Supply stop words for word-level analyses or redact/sample options for examples.

Typical callers:
- A profiling configuration builder that composes multiple section models (numerical, categorical, etc.).
- Categorical-analysis routines or report generators that accept a CatVars instance and read its attributes to decide behavior.

Responsibility boundary:
- CatVars only stores configuration values and relies on callers to enforce semantic constraints (e.g., percentage ranges) and to perform the actual diagnostics or plotting.

## State:
All attributes are public Pydantic model fields. Defaults are defined on the class.

- length: bool = True
  - Include length-based metrics for categorical values (e.g., string length distribution).
  - Values: True or False.

- characters: bool = True
  - Include character-level summaries (e.g., average characters per value).
  - Values: True or False.

- words: bool = True
  - Compute word-level summaries for string categories.
  - Values: True or False.

- cardinality_threshold: int = 50
  - Threshold above which a feature may be considered high-cardinality.
  - Expected: integer >= 0. Class does not enforce non-negativity.

- percentage_cat_threshold: float = 0.5
  - Fraction (expected in [0.0, 1.0]) used to decide whether a variable behaves like a categorical variable.
  - Not enforced by this class.

- imbalance_threshold: float = 0.5
  - Fraction (expected in [0.0, 1.0]) indicating how imbalanced a categorical distribution must be to be flagged.
  - Not enforced by this class.

- n_obs: int = 5
  - Number of example observations to show for a categorical variable.
  - Expected: integer >= 0.

- chi_squared_threshold: float = 0.999
  - Threshold value used by categorical diagnostics that rely on chi-squared-style criteria.
  - Expected typically in [0.0, 1.0], not enforced here.

- coerce_str_to_date: bool = False
  - If True, consumer code may attempt coercion of string values to dates before treating them as categorical.
  - Values: True or False.

- redact: bool = False
  - If True, categorical example values may be masked/redacted in outputs.
  - Values: True or False.

- histogram_largest: int = 50
  - Maximum number of distinct categories to include in histogram visualizations or summaries.
  - Expected: integer >= 0.

- stop_words: List[str] = []
  - Words to ignore when performing word-level analyses.
  - Important: The current class default uses a mutable list literal. That means the same list object is shared between instances created without an explicit stop_words value. If callers mutate stop_words on one instance, other default-constructed instances will observe the mutation. To avoid this shared-state pitfall, prefer constructing instances with an explicit list or change the model definition to use a default factory (e.g., default_factory=list).

Class invariants:
- This class enforces only type constraints through Pydantic (e.g., a field declared int will be validated/coerced to int where possible). No semantic invariants (bounds for percentages or non-negativity) are enforced here — such rules must be applied by caller code or by adding validators to this model.

## Lifecycle:
Creation:
- Instantiate directly with keyword arguments. All fields have defaults so no arguments are strictly required.
  - Example: CatVars(), CatVars(length=False), CatVars(cardinality_threshold=100, stop_words=['a','the']).
- You can also create the model from a mapping (dict) produced by YAML or JSON parsing and pass it to the constructor or to Pydantic parsing helpers.

Usage:
- After instantiation, profiling code reads attributes (e.g., cat_vars.cardinality_threshold) to determine which diagnostics to compute or which charts to render.
- No methods are required to be called on this model; attributes are read-only or writable as normal Python attributes on the model instance (subject to Pydantic behavior).
- Common helper methods provided by Pydantic you will likely use:
  - dict(): get a plain dict of field values.
  - json(): serialize model to JSON string.
  - copy(deep=True): create a shallow/deep copy with optional overrides.

Destruction:
- No cleanup or close actions required. The class holds no external resources and is not a context manager.

## Method Map:
This model defines no custom methods; it relies on Pydantic's BaseModel helpers. Typical interaction flow:

graph LR
  A[Create CatVars instance] --> B[Optional: mutate fields or pass into profiler]
  B --> C[Profiler reads thresholds/flags]
  C --> D[Profiler generates categorical summaries/plots]
  B --> E[Call dict()/json() to serialize config]
  style A fill:#f9f,stroke:#333,stroke-width:1px
  style B fill:#ff9,stroke:#333,stroke-width:1px
  style C fill:#9ff,stroke:#333,stroke-width:1px
  style E fill:#efe,stroke:#333,stroke-width:1px

## Raises:
- Pydantic ValidationError (pydantic.error_wrappers.ValidationError)
  - Trigger: When constructing with values that cannot be coerced to the declared types (for example, a mapping where cardinality_threshold is a complex object rather than an int or a string that cannot be parsed as an int).
  - Note: Pydantic v1 will attempt type coercion in many cases (e.g., "5" -> int 5). ValidationError occurs only when coercion/validation fails.

- No other explicit exceptions are raised by this class definition. Semantic validation (e.g., rejecting negative thresholds) is not implemented; callers should validate further if needed.

## Example:
1) Basic instantiation and read:
  cfg = CatVars()
  # Read a value
  max_categories = cfg.cardinality_threshold

2) Override defaults:
  cfg = CatVars(length=False, cardinality_threshold=100, words=False)

3) Inspect/serialize:
  cfg_dict = cfg.dict()
  cfg_json = cfg.json()

4) Create from YAML (common pattern in configuration workflows):
  # Suppose `yaml_text` is a string read from a YAML file with keys matching CatVars fields.
  parsed = yaml.safe_load(yaml_text)  # returns a dict
  cfg = CatVars(**parsed)

5) Warning about stop_words default:
  # Because stop_words default is a shared list literal, prefer:
  cfg1 = CatVars(stop_words=['and', 'the'])
  cfg2 = CatVars()
  # If code mutates cfg2.stop_words (e.g., cfg2.stop_words.append('a')), cfg1 may remain unaffected,
  # but two default-constructed instances without explicit stop_words share the same list object.
  # To avoid surprises, always pass an explicit list or modify the class to use default_factory=list.

Tips:
- If you need semantic constraints (e.g., ensure 0 <= percentage_cat_threshold <= 1), add Pydantic validators to this model or validate values in higher-level configuration code.
- To avoid the mutable-default stop_words issue in new code, change the field declaration to use a factory: stop_words: List[str] = Field(default_factory=list).

## `src.ydata_profiling.config.BoolVars` · *class*

## Summary:
A small Pydantic model that holds default configuration values and a canonical mapping for interpreting common textual boolean tokens.

## Description:
BoolVars groups three fields used by boolean-detection and boolean-parsing logic:
- n_obs: a count threshold used by callers to decide when to attempt boolean detection,
- imbalance_threshold: a numeric threshold used by callers to decide if a boolean-like variable is imbalanced,
- mappings: a dictionary mapping common lowercase textual tokens to Python booleans.

This model is intended to be instantiated by higher-level components (for example, dataset profilers, parsers, or configuration loaders) that need a consistent source of boolean-related defaults and a token-to-boolean mapping. BoolVars itself stores the values; conversion, normalization, and decision logic remain the responsibility of the callers.

## State:
Fields declared on the class (exact names, types, and defaults as in the source):

- n_obs: int
  - Default: 3
  - Description: Minimum number of observations (count) that callers may use before attempting boolean-detection for a variable.
  - Note: The type is int as declared. Semantically, callers typically use non-negative integers; the class does not perform additional range checks.

- imbalance_threshold: float
  - Default: 0.5
  - Description: A threshold (semantically between 0.0 and 1.0) used by callers to decide when one boolean value dominates (i.e., the variable is imbalanced).
  - Note: The type is float as declared. The class does not enforce a numeric range.

- mappings: Dict[str, bool]
  - Default:
    {
        "t": True,
        "f": False,
        "yes": True,
        "no": False,
        "y": True,
        "n": False,
        "true": True,
        "false": False,
    }
  - Description: Canonical mapping of common lowercase textual boolean tokens to booleans.
  - Note: The mapping is provided as a dict default on the model class. Callers should treat keys as lowercase tokens when performing lookups.

Class invariants (observable from the code):
- After construction, the model exposes the three fields with the types declared in the class definition (Pydantic enforces field presence and type validation at instantiation).
- The declared default values are present when no overrides are provided.

## Lifecycle:
Creation:
- Instantiate directly with the constructor. Examples:
  - BoolVars()  # uses defaults
  - BoolVars(n_obs=5)
  - BoolVars(imbalance_threshold=0.7, mappings={"yes": True, "no": False})
- During instantiation, Pydantic performs field validation; invalid types or incompatible values for the declared fields will cause Pydantic to raise a ValidationError.

Usage:
- Access fields directly on the instance: instance.n_obs, instance.imbalance_threshold, instance.mappings.
- Recommended lookup pattern for textual tokens (caller responsibility):
  1. Normalize the token (e.g., token.strip().lower()).
  2. Use instance.mappings.get(normalized_token) to obtain True, False, or None if unrecognized.
  3. Apply instance.n_obs and instance.imbalance_threshold in higher-level boolean-detection heuristics.

Destruction:
- No cleanup or teardown is required; BoolVars manages no external resources.

## Method Map:
flowchart LR
    A[Construct BoolVars] --> B[Access n_obs]
    A --> C[Access imbalance_threshold]
    A --> D[Access mappings]
    D --> E[Caller normalizes token to lowercase]
    E --> F[Lookup: mappings.get(token_lower)]
    B --> G[Caller checks observation count]
    C --> G
    F --> G
    G --> H[Caller decides boolean handling]

(Note: BoolVars is a data model exposing fields; the diagram shows typical caller interactions with those fields.)

## Raises:
- pydantic.error_wrappers.ValidationError
  - When: Raised by Pydantic at instantiation if provided values cannot be validated or parsed into the declared field types (for example, if mappings is passed as a non-mapping type).

## Example:
Assuming BoolVars has been imported into the current scope:

# Create defaults
bv = BoolVars()

# Normalize a token and look up its boolean interpretation
token = " Yes "
token_normalized = token.strip().lower()       # "yes"
value = bv.mappings.get(token_normalized)      # True for the default mapping, or None if unrecognized

# Use thresholds in caller logic (illustrative)
observed_count = 10
class_proportion = 0.95
if observed_count >= bv.n_obs:
    if max(class_proportion, 1 - class_proportion) >= bv.imbalance_threshold:
        # caller treats variable as imbalanced boolean-like
        pass

Notes and recommendations:
- Normalize textual tokens (strip and lowercase) before consulting mappings.
- If you need a customized mapping, pass an explicit dict to mappings during construction rather than mutating the default in place.
- Catch pydantic.error_wrappers.ValidationError around construction when consuming untrusted configuration inputs.

## `src.ydata_profiling.config.FileVars` · *class*

## Summary:
A compact pydantic-based configuration container for file-related boolean flags. Currently models a single flag `active` that signals whether file-related features are enabled.

## Description:
FileVars is a minimal typed value object implemented as a subclass of pydantic.v1.BaseModel. It is intended to be instantiated whenever a small, validated configuration object for file-related toggles is required — for example, as a field inside a larger configuration/settings model or when constructing runtime options from user input or a parsed configuration file.

Typical instantiation sites:
- Direct creation by calling the model constructor with keyword arguments.
- Construction by higher-level configuration objects in the same package that aggregate multiple flag groups.
- Parsing from external data sources using pydantic parsing helpers (e.g., parse_obj / parse_raw) when deserializing configuration.

Motivation and responsibilities:
- Centralizes file-related boolean flags into a single, typed model to improve discoverability and validation.
- Delegates validation, serialization, and parsing to pydantic.BaseModel.
- Does not perform file I/O, resource management, or business logic; it is exclusively a typed state holder.

## State:
Public attributes (persisted on instances):
- active
  - Type: bool
  - Default: False
  - Valid values: True or False (boolean)
  - Invariant: After model creation, `active` is always present and holds a boolean value as determined by pydantic validation/coercion.

Constructor/initialization notes:
- The constructor accepts `active` as an optional keyword argument. If omitted, the value is False.
- Because FileVars derives from pydantic.BaseModel, incoming values for `active` will be validated and may be coerced by pydantic according to its boolean conversion rules (e.g., Python booleans, some integer or string representations that pydantic recognizes). If a provided value cannot be validated/coerced to boolean, model construction raises a pydantic ValidationError.

Class invariants:
- Instances always expose `active` as a boolean attribute.
- No other attributes are defined by FileVars; any additional fields must be provided via model extension or composition elsewhere.

## Lifecycle:
Creation:
- Instantiate with no arguments to obtain the default state (active = False).
- Instantiate with `active=True` (keyword) to enable the flag at creation time.
- Alternatively, use pydantic parsing helpers such as parse_obj or parse_raw to build an instance from external data (e.g., dictionaries, JSON strings).

Usage:
- Typical usage is read-only access to the `active` flag by consumer code that decides whether to enable file-related behaviors.
- Optionally, use BaseModel utility methods:
  - To serialize: use .dict() to get a Python dict, or .json() for a JSON string.
  - To copy and change: use .copy(update={...}) to produce a modified instance.
  - To parse: use FileVars.parse_obj(data) or FileVars.parse_raw(json_str) when ingesting external representations.

Destruction:
- No explicit cleanup is required. The class does not manage external resources and does not implement context-manager or close semantics.

## Method Map:
A small interaction map showing typical construction, validation, and consumption paths:

mermaid
flowchart LR
    A[Input data (kwargs / dict / json)] --> B[FileVars constructor or parse_*]
    B --> C{pydantic validation/coercion}
    C -->|success| D[Instance with active (bool)]
    C -->|failure| E[ValidationError raised]
    D --> F[Read instance.active]
    D --> G[Serialization via .dict() / .json()]
    D --> H[Copy/modify via .copy(update=...)]

Note: dict/json/parse/copy are provided by pydantic.BaseModel; FileVars does not implement additional methods.

## Raises:
- pydantic.error_wrappers.ValidationError: Raised by the BaseModel constructor or parse_* helpers when the provided input cannot be validated/coerced to the declared types (e.g., when `active` receives a value pydantic cannot interpret as a boolean).

## Example (usage described in prose):
- Default creation: create a FileVars instance without arguments; its `active` attribute will be False.
- Explicit creation: create a FileVars instance supplying the keyword `active=True`; the created instance will have `active == True`.
- Parsing from data: when reading a configuration dictionary or JSON produced externally, use pydantic parsing helpers (e.g., parse_obj for a dict or parse_raw for a JSON string) to construct a validated FileVars instance.
- Serialization: to persist or transmit the flag, call the instance's .dict() to get a serializable mapping or .json() to get a JSON string.
- Error handling: when consuming untrusted input, wrap construction/parsing in try/except for pydantic.ValidationError to handle invalid or malformed values gracefully.

(End of documentation.)

## `src.ydata_profiling.config.PathVars` · *class*

## Summary:
A minimal pydantic configuration model that encapsulates a single boolean flag `active` indicating whether path-related features are enabled.

## Description:
PathVars is a thin, typed container implemented as a pydantic BaseModel with one field: `active`. It exists to centralize and validate a single boolean configuration option so that other parts of the system can accept a consistent, serializable model instead of ad-hoc booleans.

When to instantiate:
- When you need a typed configuration object representing whether path-related behavior should be active.
- As a nested field inside a larger configuration model (e.g., a global settings model) or when loading configuration from external sources (JSON/YAML) and you want pydantic validation.

Motivation:
- Keeps the configuration surface explicit and self-documenting.
- Leverages pydantic for input validation/serialization without adding custom logic.

Known callers/factories:
- None declared in this file. Typical usage is direct construction or embedding in other pydantic models.

## State:
- active
  - Type: bool
  - Default: False
  - Valid values: True or False (or values pydantic can coerce to boolean during model validation)
  - Invariant: The instance's `active` attribute is expected to represent a boolean state; pydantic enforces/coerces types at construction.

Class invariants:
- The only structural guarantee is that the model exposes an `active` attribute whose value is validated by pydantic as a boolean at instantiation.
- There are no multi-field invariants because only one field is defined.

## Lifecycle:
Creation:
- Constructor signature (conceptual): PathVars(active: bool = False)
  - Call with no arguments to obtain the default disabled state: PathVars()
  - Call with PathVars(active=True) to enable
- Model construction triggers pydantic validation/coercion for provided fields.

Usage:
- Read the `.active` attribute to determine whether path-related behavior should run.
- For modifying values:
  - You can assign to `.active` on the instance if the BaseModel configuration permits mutation (pydantic BaseModel default allows mutation). If mutation is disallowed by a project-level BaseModel configuration, use `.copy(update={"active": ...})` to create a modified instance.
- Serialization and interoperability:
  - Use inherited BaseModel utilities such as `dict()` and `json()` to serialize the model for storage, logging, or transmission.
  - The model can be nested inside other pydantic models or used with pydantic parsing helpers when reading configuration from external representations.

Destruction / cleanup:
- No cleanup required. The model does not manage external resources.

## Method Map:
flowchart LR
    Construct[Construct PathVars(active?)] --> Instance[PathVars instance (.active)]
    Instance --> Read[Read .active]
    Instance --> Mutate[Mutate via assignment or copy(update=...)]
    Instance --> Serialize[dict() / json() / copy()]
    Serialize --> Persist[Save or embed in larger config]

(Note: The model itself does not define methods beyond those inherited from pydantic.BaseModel; the diagram shows typical operations.)

## Raises:
- pydantic.ValidationError (raised by the BaseModel machinery) if a provided value for `active` cannot be validated/coerced to a boolean during instantiation.
  - Example triggers: supplying malformed input that pydantic cannot interpret as a boolean for the `active` field.
- No other exceptions are raised by this class definition.

## Example:
- Default instantiation (disabled):
  - instance = PathVars()
  - instance.active  # False

- Enabled instantiation:
  - instance = PathVars(active=True)
  - instance.active  # True

- Serialization:
  - d = instance.dict()   # {'active': True}
  - j = instance.json()   # JSON representation

- Modifying safely (immutable-project-safe pattern):
  - new_instance = instance.copy(update={"active": False})

- Handling invalid input (validation error):
  - try:
        bad = PathVars(active="not-a-boolean")
    except Exception as e:
        # pydantic will raise a ValidationError when input cannot be coerced/validated
        handle_validation_error(e)

## `src.ydata_profiling.config.ImageVars` · *class*

## Summary:
A small pydantic model that groups boolean configuration flags controlling image-related profiling features: whether image processing is active, whether EXIF metadata should be included, and whether image hashing is enabled.

## Description:
ImageVars is a typed configuration container used to represent image-specific feature toggles in the profiling system. It exists so callers can pass a single structured object (instead of several independent booleans) wherever image-related configuration is required.

Typical instantiation scenarios:
- When loading/parsing application configuration (for example, from YAML, dicts, or environment-derived settings) into typed configuration objects.
- When a higher-level settings or profile generator composes configuration blocks for different data types (numerical, categorical, image, etc.) and needs a compact representation for image options.
- During testing to construct deterministic image-related configurations.

Motivation and responsibility:
- Encapsulates image-related flags in a single, validated object.
- Delegates type validation and (where applicable) coercion to the pydantic.v1.BaseModel base class.
- Keeps configuration surface area small and explicit: three booleans that can be read by callers without additional parsing logic.

## State:
- active (bool)
    - Default: False
    - Meaning: Whether image processing / image-feature extraction is enabled.
    - Valid values: True or False.
    - Invariant: Represents a global enable/disable flag for image features; when False, callers should treat other image flags as inert (they may be present but ignored).
- exif (bool)
    - Default: True
    - Meaning: Whether to extract/include EXIF metadata when image processing is active.
    - Valid values: True or False.
    - Invariant: Only relevant when active is True; otherwise callers may ignore this value.
- hash (bool)
    - Default: True
    - Meaning: Whether to compute/store image hashes (e.g., for duplicate detection) when image processing is active.
    - Valid values: True or False.
    - Invariant: Only relevant when active is True.

Notes on validation and runtime representation:
- This class inherits from pydantic.v1.BaseModel. As such:
    - Attribute types are validated at construction; pydantic will attempt to coerce compatible types (for example, 0/1 to booleans in permissive configurations), and will raise pydantic.ValidationError if values cannot be validated/coerced to bool.
    - All three fields have defaults, so an instance can be constructed with zero arguments.
- No additional attributes or computed state are defined on this class.

## Lifecycle:
- Creation:
    - Instantiate directly with any subset of the three boolean fields:
        - Example: ImageVars()  (defaults: active=False, exif=True, hash=True)
        - Example: ImageVars(active=True, exif=False)
    - Construction performs pydantic validation; invalid, non-coercible inputs cause a pydantic.ValidationError.
- Usage:
    - Read-only style usage: callers typically read the boolean flags to decide which image-processing steps to run.
    - There are no instance methods defined on ImageVars; methods available are inherited from pydantic.BaseModel (e.g., .dict(), .json()) and can be used to serialize/inspect configuration.
    - Typical sequence:
        1. Create the ImageVars instance (possibly as part of a larger settings object).
        2. Check .active. If False, skip image-processing stages.
        3. If .active is True, consult .exif and .hash to decide specific processing sub-steps.
- Destruction:
    - No special cleanup is required. Instances are simple data containers and rely on normal Python garbage collection.
    - Not a context manager; no close() or similar method.

## Method Map:
flowchart LR
    A[Construct ImageVars] --> B[Validate fields via pydantic]
    B --> C{Use in profiling pipeline}
    C --> D[Check active flag]
    D -- active=False --> E[Skip image processing]
    D -- active=True --> F[Check exif and hash flags]
    F --> G[Run EXIF extraction if exif=True]
    F --> H[Compute image hash if hash=True]

## Raises:
- pydantic.v1.ValidationError
    - Trigger conditions:
        - Any provided field value cannot be coerced or validated as a boolean by pydantic. For example, providing an object of an incompatible type (and when pydantic cannot coerce it) will lead to this exception during construction.
- Note: Because all fields have defaults, missing fields do not raise errors.

## Example:
- Create a default instance:
    - ImageVars()  -> yields {active: False, exif: True, hash: True}
- Create an enabled configuration that disables EXIF extraction:
    - ImageVars(active=True, exif=False)
- Typical usage pattern in a profiling pipeline (described):
    1. Instantiate or obtain an ImageVars instance from application settings.
    2. If instance.active is False, skip all image-specific work.
    3. If instance.active is True:
        - If instance.exif is True: run EXIF extraction and include metadata in results.
        - If instance.hash is True: compute image hashes for duplicate detection or indexing.
- Serialization / inspection:
    - Use inherited pydantic methods like .dict() or .json() to serialize the configuration for logging, persistence, or comparison.

## `src.ydata_profiling.config.UrlVars` · *class*

## Summary:
A minimal pydantic v1 BaseModel that encapsulates a single boolean configuration flag named `active` with a default of False.

## Description:
UrlVars is a focused configuration value object whose sole responsibility is to represent whether URL-related features or checks are enabled. It is intended to be embedded in higher-level configuration objects or constructed directly where a typed, validated boolean toggle is required.

When to instantiate:
- During configuration composition when the application needs a typed container for the "URLs enabled" flag.
- In tests that require toggling URL-related behavior independently.
- When loading configuration with pydantic-based loaders so the `active` field benefits from pydantic validation and model semantics.

Responsibility boundary:
- Only represents the boolean toggle. It does not implement URL parsing, validation, or any runtime URL logic. Consumers of this model should read its `active` attribute and take appropriate action.

## State:
- active
  - Type: bool
  - Default value: False (as declared on the model)
  - Role: indicates whether URL-related functionality is enabled
  - Valid values: any value that successfully validates as a boolean according to pydantic v1 validation rules (the model itself declares the field type as bool)
- No other fields, private attributes, or computed properties are present in the model.

Class invariants:
- After successful construction, the instance must expose an attribute `active` whose value is a Python bool.
- No inter-field invariants exist because the model contains only one field.

## Lifecycle:
Creation:
- Constructor signature (logical view): UrlVars(active: bool = False)
  - The `active` parameter is optional; omitted values default to False.
  - Construction and validation are performed by pydantic v1's BaseModel machinery (imported as BaseModel in the module).

Usage:
- Typical usage is: construct once during configuration load or composition, then read the instance's `active` attribute where needed in application code.
- There are no methods to call on this model beyond attribute access and the standard pydantic BaseModel utilities available to all such models.

Serialization and mutability:
- As a pydantic v1 BaseModel instance, standard pydantic export/inspection utilities (for example, converting to a dict or JSON via pydantic's provided APIs) are available; consult pydantic v1 documentation for exact method names and options.
- Default mutability and other model behaviors follow pydantic v1 BaseModel defaults unless altered elsewhere in the codebase via model Config.

Destruction:
- No special cleanup or resource management is required.

## Method Map:
flowchart LR
    M[UrlVars (pydantic BaseModel)]
    M --> F[active : bool = False]
    note right of M: No methods defined in the class; interaction is via construction, attribute access, and standard pydantic BaseModel utilities

## Raises:
- pydantic.error_wrappers.ValidationError (pydantic v1 ValidationError) if the provided `active` value does not pass pydantic v1's validation for the `bool` type.
  - This arises from pydantic's validation step during model construction when an invalid value is supplied for `active`.
- The class defines no custom exceptions; any raised exceptions originate from pydantic's BaseModel machinery.

## Example (descriptive; no code):
- Default instance: constructing UrlVars without arguments yields an instance whose `active` attribute is False.
- Enabled instance: constructing UrlVars while providing an explicit boolean True results in an instance whose `active` attribute is True; application code should treat this as the signal to enable URL-related behavior.
- Serialization: the model can be exported to a plain mapping (for example, a dictionary) using pydantic v1 export helpers so that the `active` key and its boolean value are preserved.
- Error handling: if configuration input contains an invalid value for `active`, pydantic v1 will raise a ValidationError at construction time; catch and handle this at the configuration load boundary (for example, by logging and applying a fallback).

## `src.ydata_profiling.config.TimeseriesVars` · *class*

## Summary:
A small Pydantic model that holds typed configuration options for timeseries-specific profiling (toggles and numeric/hyperparameter values).

## Description:
TimeseriesVars groups timeseries-related parameters into a single typed container so callers can pass a structured object into timeseries analysis routines. The class only stores values and types; it does not perform dataset-level checks (for example, verifying that a column named by sortby exists) nor does it implement analysis algorithms.

Typical callers:
- A top-level configuration loader or settings object that composes multiple sub-configuration models.
- Timeseries analysis code that requires a set of parameters (active, lags, thresholds, etc.).

Responsibility boundary:
- Encapsulate default values and types for timeseries settings.
- Not responsible for semantic validation (column existence) or enforcing numeric ranges.

## State:
All attributes are declared on the Pydantic BaseModel with these exact types and defaults (as in the source):

- active: bool
  - Default: False
  - Purpose: toggle to enable or disable timeseries-specific profiling steps.

- sortby: Optional[str]
  - Default: None
  - Purpose: optional column/key name to use to sort records before timeseries computations.

- autocorrelation: float
  - Default: 0.7
  - Purpose: threshold value used by caller code to interpret autocorrelation strength.

- lags: List[int]
  - Default: [1, 7, 12, 24, 30]
  - Purpose: integer lag offsets to inspect when computing lag-based metrics.
  - Note: the model type requires a list of integers; to change lags on an instance, assign a new list (cfg.lags = [1,2,3]).

- significance: float
  - Default: 0.05
  - Purpose: p-value threshold for statistical tests used by caller code.

- pacf_acf_lag: int
  - Default: 100
  - Purpose: maximum lag to evaluate when computing PACF/ACF.

Class invariants:
- Each attribute exists on the model and is subject to Pydantic's type validation at instantiation.
- No cross-field validators or additional logic are defined on this class; any relationships between fields must be enforced by the caller.

## Lifecycle:
Creation:
- Instantiate with TimeseriesVars(...) using keyword arguments for any fields you want to override. Because every field has a default, TimeseriesVars() constructs a valid instance using those defaults.
- Example instantiations:
  - TimeseriesVars()
  - TimeseriesVars(active=True, sortby="timestamp")
  - TimeseriesVars(lags=[1,2,3], autocorrelation=0.6)

Usage:
- Read the attributes directly (cfg.active, cfg.lags, etc.) and pass them into timeseries processing functions.
- Typical order:
  1. Construct TimeseriesVars.
  2. Optionally verify dataset-level semantics (e.g., ensure cfg.sortby exists).
  3. If cfg.active is True, run timeseries analysis using the values stored on the model.
- No special initialization, finalization, or cleanup methods are defined or required.

Destruction / cleanup:
- This class holds no external resources and requires no explicit cleanup.

## Method Map:
This model defines no custom methods. Typical interaction flow:

graph TD
  A[Configuration source] --> B[Instantiate TimeseriesVars]
  B --> C{cfg.active?}
  C -- false --> D[Skip timeseries routines]
  C -- true --> E[Validate dataset semantics]
  E --> F[Run timeseries computations using cfg.lags, cfg.autocorrelation, cfg.significance, cfg.pacf_acf_lag]

## Raises:
- On instantiation, Pydantic validation will run. If provided values do not conform to the declared field types (for example, supplying an int where a list[int] is expected), Pydantic will raise a validation error. The exact exception type and module name are provided by the Pydantic library; callers should catch Pydantic's validation exception if they need to handle invalid input.

- This class does not itself raise errors for semantic issues such as out-of-range numeric values or missing dataset columns.

## Example:
1) Default construction and checking active:
cfg = TimeseriesVars()                # uses defaults; cfg.active is False
cfg2 = TimeseriesVars(active=True, sortby="timestamp")
if cfg2.active:
    # Caller should verify that "timestamp" exists in the dataset before using it to sort
    run_timeseries_analysis(dataframe,
                            sortby=cfg2.sortby,
                            lags=cfg2.lags,
                            autocorrelation=cfg2.autocorrelation,
                            significance=cfg2.significance,
                            pacf_acf_lag=cfg2.pacf_acf_lag)

2) Overriding defaults:
cfg3 = TimeseriesVars(autocorrelation=0.6, lags=[1,2,3], significance=0.01, pacf_acf_lag=50)

3) Invalid instantiation behavior (illustrative):
# Providing a wrong type for a field will trigger Pydantic validation and raise an error
# e.g., TimeseriesVars(lags=5)  -> validation error

## `src.ydata_profiling.config.Univariate` · *class*

## Summary:
Typed Pydantic container that groups all per-datatype "univariate" configuration sections (numeric, text, categorical, image, boolean, path, file, url, timeseries) into a single nested model.

## Description:
Univariate is a small convenience BaseModel that aggregates the nine specialized sub-configuration models used by the profiler for univariate (single-column) analyses:
- num: numeric-variable options (NumVars)
- text: text-specific options (TextVars)
- cat: categorical-variable options (CatVars)
- image: image-related flags (ImageVars)
- bool: boolean-detection options (BoolVars)
- path: path-related flags (PathVars)
- file: file-related flags (FileVars)
- url: URL-related flags (UrlVars)
- timeseries: timeseries-specific options (TimeseriesVars)

When to instantiate:
- As part of constructing a full profiling configuration (the top-level settings model composes Univariate).
- In tests or user code that need grouped univariate defaults or want to override specific per-type defaults.

Why this abstraction exists:
- Collects per-type univariate tuning parameters into one semantically meaningful section for ease of use, validation, and serialization.
- Keeps each specialized group in its own model while exposing a single accessor for all univariate-related options.

Known callers/factories:
- Higher-level configuration objects that compose multiple sections (e.g., global Config/Settings).
- Profiling routines that receive a Univariate instance and read nested attributes to decide which diagnostics to compute.

## State:
Each attribute is a Pydantic model instance described below. The annotation and default shown reflect the class source (defaults are created at class-definition time).

- num: NumVars
  - Default: result of NumVars() (NumVars has defaults: quantiles=[0.05,0.25,0.5,0.75,0.95], skewness_threshold=20, low_categorical_threshold=5, chi_squared_threshold=0.999)
  - Role: numeric-analysis heuristics and thresholds.

- text: TextVars
  - Default: result of TextVars() (defaults: length=True, words=True, characters=True, redact=False)
  - Role: text-specific flags for length/word/character summaries and redaction.

- cat: CatVars
  - Default: result of CatVars() (defaults include cardinality_threshold=50, percentage_cat_threshold=0.5, imbalance_threshold=0.5, n_obs=5, stop_words=[], etc.)
  - Role: categorical-analysis options and thresholds.

- image: ImageVars
  - Default: result of ImageVars() (defaults: active=False, exif=True, hash=True)
  - Role: image feature toggles.

- bool: BoolVars
  - Default: result of BoolVars() (defaults: n_obs=3, imbalance_threshold=0.5, mappings={"t":True,...})
  - Role: boolean-detection thresholds and textual-token mappings.

- path: PathVars
  - Default: result of PathVars() (default: active=False)
  - Role: path-related toggle.

- file: FileVars
  - Default: result of FileVars() (default: active=False)
  - Role: file-related toggle.

- url: UrlVars
  - Default: result of UrlVars() (default: active=False)
  - Role: URL-related toggle.

- timeseries: TimeseriesVars
  - Default: result of TimeseriesVars() (defaults: active=False, sortby=None, autocorrelation=0.7, lags=[1,7,12,24,30], significance=0.05, pacf_acf_lag=100)
  - Role: timeseries options and thresholds.

Important invariant / shared-default note:
- Because the class-level defaults are created by calling each submodel's constructor at class definition time (e.g., NumVars()), the same default submodel instances become the defaults for every Univariate instance constructed without explicit overrides. If those submodel instances contain mutable defaults (for example, lists or dicts such as NumVars.quantiles, CatVars.stop_words, BoolVars.mappings), in-place mutation will be visible across Univariate instances that rely on the class-level default. To obtain instance-isolated nested models, supply fresh submodel instances when constructing Univariate or use Pydantic's copy(deep=True) on a constructed Univariate.

## Lifecycle:
Creation:
- Instantiate via constructor (keyword arguments allowed for any of the nine fields). Examples:
  - default_cfg = Univariate()
  - custom_cfg = Univariate(num=NumVars(quantiles=[0.1,0.5,0.9]), cat=CatVars(cardinality_threshold=100))
- Pydantic validates each provided nested value at construction. You may pass either a submodel instance or a mapping (dict) compatible with the nested model fields (Pydantic will attempt to parse/coerce).

Usage:
- Typical usage is read-only consumption by profiling code:
  - Access nested values like cfg.num.quantiles, cfg.cat.cardinality_threshold, cfg.image.active.
  - Combine thresholds and flags in caller logic to choose diagnostics and visualizations.
- To mutate safely:
  - Prefer creating a new Univariate with explicit nested overrides, or call cfg.copy(deep=True).copy(update={...}) to produce a deep-copied instance with changes, avoiding accidental shared-state through class-level defaults.

Destruction:
- No special cleanup; Univariate holds no external resources.

Recommended sequencing:
1. Construct (supply explicit nested instances if you plan to mutate nested state).
2. Optionally validate dataset-level semantics in caller code (e.g., that timeseries.sortby exists).
3. Read nested attributes to decide profiling steps.
4. When modifying, prefer functional-style replace (copy/update or construct new Univariate) to avoid cross-instance side effects.

## Method Map:
flowchart LR
    A[Construct Univariate(...)] --> B{Are nested args provided?}
    B -- no --> C[Use class-level default submodel instances]
    B -- yes --> D[Pydantic parses/validates provided nested values]
    C --> E[Caller reads nested attrs: .num, .text, .cat, .image, .bool, .path, .file, .url, .timeseries]
    D --> E
    E --> F[Profiler applies nested thresholds & flags to analysis]
    note right of C: Beware: class-level defaults may be shared across instances
    F --> G[When changing config state, prefer .copy(deep=True) or constructing new Univariate]

## Raises:
- pydantic.error_wrappers.ValidationError
  - When: Raised by Pydantic during Univariate instantiation if supplied values for any nested field cannot be validated/coerced into the corresponding nested model (for example, providing a wrong type for a nested list/field).
- No other exceptions are raised by Univariate itself; semantic validation (value ranges, presence of dataset columns, etc.) is performed by caller code or by adding validators to the nested models.

## Example:
1) Default creation and access:
  cfg = Univariate()
  # Inspect numeric quantiles
  q = cfg.num.quantiles
  # Check whether image processing is enabled
  if cfg.image.active:
      # run image-specific diagnostics
      pass

2) Construct with fresh nested instances to avoid shared defaults:
  my_num = NumVars(quantiles=[0.1,0.5,0.9])
  my_cat = CatVars(cardinality_threshold=100, stop_words=["and","the"])
  cfg2 = Univariate(num=my_num, cat=my_cat)
  # Mutating my_cat.stop_words will not affect other Univariate instances that were not constructed with my_cat.

3) Avoid in-place mutation of class-level defaults:
  default_a = Univariate()
  default_b = Univariate()
  # BAD: this will affect both default_a and default_b if the underlying nested list/dict is shared
  default_a.num.quantiles.append(0.99)
  # Prefer:
  cfg_modified = default_a.copy(deep=True)
  cfg_modified.num = cfg_modified.num.copy(update={"quantiles": cfg_modified.num.quantiles + [0.99]})

4) Handling invalid input:
  try:
      # e.g., passing a scalar where a list[int] is required by TimeseriesVars.lags
      bad = Univariate(timeseries={"lags": 5})
  except Exception as e:
      # Pydantic will raise a ValidationError for incompatible nested field types
      handle_validation_error(e)

## `src.ydata_profiling.config.MissingPlot` · *class*

## Summary:
Configuration holder for missing-value visualizations. Encapsulates two plotting options: whether to force labels on missingness plots and which colormap identifier to use.

## Description:
A small pydantic BaseModel intended to carry plotting options for components that render missing-value visualizations (for example, heatmaps or matrix plots that visualize NaNs/missing entries). The class exists solely as a typed configuration object — it does not perform any rendering itself. Typical callers are report-generation code or plotting utilities that want a single object representing missing-plot options.

Motivation and responsibility boundaries:
- Group related plotting options so callers pass a single argument instead of multiple loose parameters.
- Provide sensible defaults (force_labels=True, cmap="RdBu") while delegating rendering-specific validation (e.g., verifying that a colormap string is valid for a plotting backend) to the plotting code that consumes this configuration.
- Rely on pydantic (BaseModel) for basic type validation/coercion at construction time; do not perform or rely on additional validation here.

## State:
Public attributes (available after construction):
- force_labels: bool
  - Type: bool
  - Default: True
  - Meaning: If True, plotting routines should render labels (e.g., row/column or cell labels) on missing-value visualizations where applicable. If False, labels may be omitted to reduce clutter.
  - Validation: pydantic will validate the provided value; it may coerce some inputs (for example numeric 0/1) to booleans according to pydantic rules. If a value cannot be validated/coerced to a bool, pydantic raises a ValidationError during model creation.

- cmap: str
  - Type: str
  - Default: "RdBu"
  - Meaning: Identifier for the colormap to use when rendering missingness visualizations (e.g., a matplotlib colormap name). This class does not validate that the string is a valid colormap; that validation is the responsibility of the plotting backend or caller.
  - Validation: pydantic enforces that the attribute is a string at construction time; non-string inputs will be coerced where possible or raise a ValidationError if incompatible.

Class invariants:
- After successful construction, both attributes exist and have the documented types (bool and str).
- No additional internal/cached state is maintained.
- Mutability: BaseModel (pydantic.v1) instances are mutable by default. Unless the broader project freezes models or enables validate_assignment, callers can reassign attributes post-construction (e.g., config.cmap = "viridis"); such assignments are not validated here unless pydantic's assignment validation is enabled elsewhere.

Edge cases and notes:
- An empty string ("") for cmap is accepted by this model but will likely cause an error only when the plotting backend attempts to resolve the colormap name.
- This class does not verify that cmap corresponds to any backend (matplotlib, seaborn, etc.). Consumers should validate or handle backend errors when applying the colormap.
- The model itself does not define custom validators or constraints beyond type enforcement provided by pydantic.

## Lifecycle:
Creation:
- Instantiate directly using positional or keyword arguments:
  - MissingPlot()
  - MissingPlot(force_labels=False)
  - MissingPlot(cmap="viridis")
  - MissingPlot(force_labels=False, cmap="viridis")
- Construction runs pydantic validation. Incompatible inputs may raise pydantic.v1.error_wrappers.ValidationError.

Usage:
- Common pattern: create one configuration instance and pass it to plotting functions which read config.force_labels and config.cmap to control rendering.
- There is no required call ordering; plotting utilities simply read attributes when preparing plots.

Destruction:
- No special teardown required; the object holds only simple Python values.

## Method Map:
graph LR
  A[Create MissingPlot instance] --> B[Instance with attributes force_labels, cmap]
  B --> C[Plotting utility reads force_labels]
  B --> D[Plotting utility reads cmap]
  C --> E[Renderer configures label visibility]
  D --> E[Renderer configures colormap]
  E --> F[Plot produced / errors forwarded to caller]

## Raises:
- pydantic.v1.error_wrappers.ValidationError
  - Trigger: Raised during instantiation if provided values cannot be validated or coerced to the declared types (bool for force_labels, str for cmap).
  - Example triggers: providing a complex custom object with no coercion path to str for cmap, or an input that pydantic cannot coerce to bool for force_labels.

- No other exceptions are raised by this model itself. Runtime errors related to applying the configuration (for example, an unknown colormap string passed to matplotlib) will originate from the plotting backend or calling code.

## Example:
Construct with defaults:
MissingPlot()

Construct overriding settings:
MissingPlot(force_labels=False)
MissingPlot(cmap="viridis")
MissingPlot(force_labels=False, cmap="viridis")

Handling validation errors (conceptual example):
try:
    cfg = MissingPlot(force_labels="not-a-bool", cmap=object())
except Exception as e:
    # e will be a pydantic ValidationError if inputs cannot be coerced to the required types
    print("Invalid configuration:", e)

Typical usage sequence:
1) Create the MissingPlot configuration once near the start of report generation.
2) Pass the instance to each plotting routine that renders missing-value visualizations.
3) The plotting routine reads cfg.force_labels and cfg.cmap and applies them; the routine is responsible for any additional validation and for translating cfg.cmap into a backend-specific colormap object if necessary.

## `src.ydata_profiling.config.ImageType` · *class*

## Summary:
A small enumeration that defines the allowed image output formats used throughout the configuration: two members, svg and png.

## Description:
This class represents the canonical set of image types supported by the system where image format selections are required (for example, configuration options that control report or chart export formats). Instantiate or reference this enum when you need a type-safe representation of image formats rather than raw strings.

Typical call-sites:
- Configuration parsing and validation where a field must be one of the supported image formats.
- Code that selects an exporter or renderer implementation according to the requested image format.

Motivation and responsibility boundary:
- Encapsulates the finite set of supported image output types in a single, discoverable type.
- Prevents magic strings scattered through the codebase and allows validation and switch/case-style logic based on enum members.
- Does not perform I/O, rendering, or format conversion itself — it merely enumerates allowed values.

## State:
Attributes (members):
- svg
  - Type: enumeration member of ImageType
  - Underlying value (string): "svg"
  - Valid meaning: use Scalable Vector Graphics output format
- png
  - Type: enumeration member of ImageType
  - Underlying value (string): "png"
  - Valid meaning: use PNG raster image output format

Instance-level invariants:
- Each enum member is a singleton; ImageType.svg and ImageType.png are unique, stable objects for the lifetime of the program.
- The set of valid values is exactly {"svg", "png"} — no other string or member is valid for standard operations that accept an ImageType.

Notes on attributes:
- To obtain the underlying string representation of a member, read the member's value attribute (returns "svg" or "png").
- Member names (identifiers) are "svg" and "png"; member values (payload) are the identical strings "svg" and "png".

## Lifecycle:
Creation:
- There is no instantiation via an exposed __init__ signature; the class defines two static members created at class definition time.
- To obtain a member from a string at runtime, use the enum class constructor semantics: pass the underlying value to the enum class (this will return the matching member or raise a ValueError if not found).
- Alternatively, access members directly as attributes on the class (the recommended, explicit approach).

Usage:
- Typical usage patterns:
  - Compare against members using identity/equality checks to select logic: e.g., branch on the requested image type.
  - Read member.value when you need the literal format string for downstream APIs, filenames, or serializers.
  - Use the enum in pydantic/BaseModel validation fields or configuration settings to enforce allowed values.
- Ordering and sequencing: there are no lifecycle methods to call in sequence; the enum is used wherever needed and has no initialization/destruction protocol.

Destruction / cleanup:
- No cleanup or resource management is required. Members are pure Python objects managed by the runtime.

## Method Map:
A simple usage flow showing typical interactions with the ImageType enum.

graph LR
  A[Define or parse format input (string or attribute reference)] --> B{Get ImageType member}
  B -->|Direct attribute| C[ImageType.svg or ImageType.png]
  B -->|From value| D[ImageType(<value>) -> ImageType member or ValueError]
  C --> E[Use .value for string "svg"/"png"]
  D --> E
  E --> F[Pass to renderer/exporter or store in config]

(Note: the diagram represents conceptual flow; actual code uses enum access patterns documented above.)

## Raises:
- ValueError: raised when attempting to construct an ImageType from an invalid value string (e.g., ImageType("jpeg")) — standard Enum constructor behavior.
- KeyError: raised when attempting to access a member via the mapping syntax ImageType["name"] with a non-existent name (e.g., ImageType["jpeg"]).
- AttributeError: attempting to access a non-existent attribute on the ImageType class (e.g., ImageType.jpeg) will raise AttributeError.

These are standard behaviors inherited from Python's Enum implementation.

## Example:
- To refer to the SVG format in code, use the enum member corresponding to the SVG member. When you need the raw string to pass to serializers or file-naming logic, read the member's value which yields "svg".
- To validate a user-supplied string, attempt to convert it to the enum; if conversion succeeds, the value is valid; if it raises ValueError, handle this as invalid input.

Practical guidance:
- Prefer direct attribute access (ImageType.svg / ImageType.png) in code for clarity.
- When storing or serializing configurations, store the underlying string (member.value) so configuration files remain plain strings, and re-construct the enum from that string when parsing.

## `src.ydata_profiling.config.CorrelationPlot` · *class*

## Summary:
A small pydantic model that holds configuration for correlation plots: the colormap identifier and the color used for invalid/missing entries.

## Description:
This class is a lightweight configuration container intended to carry only two settings used when rendering correlation plots or heatmaps: the name/identifier of the colormap and the color to render "bad" (invalid, NaN, or masked) cells. It exists to centralize these two related plotting options into a typed object that can be passed around report-generation or plotting code.

Typical instantiation scenarios:
- Creating a default configuration to be passed into a plotting function.
- Overriding one or both attributes when generating different visual styles.

Motivation and responsibility boundary:
- Responsibility: Hold and validate (via pydantic) simple plotting configuration values.
- Not responsible for: enforcing semantics or formats beyond basic type validation, performing plotting, or translating colormap names to color maps — those are responsibilities of downstream plotting code.

## State:
- cmap (str)
  - Default: "RdBu"
  - Description: A string identifier for a colormap. The class only types this as str; downstream plotting code will interpret the identifier (commonly a Matplotlib colormap name or other plot-backend identifier).
  - Constraints/invariants: No internal format checks are implemented here — any string is accepted by the model itself.
- bad (str)
  - Default: "#000000"
  - Description: A string representing the color to use for invalid/masked cells in a correlation plot. Typically a hex color string (e.g., "#RRGGBB") or any color string accepted by the plotting backend.
  - Constraints/invariants: No internal enforcement of color format occurs in this class.

Class invariants:
- Both attributes exist on all instances and are of type str after pydantic validation/coercion. There are no further relationships or numeric bounds between the attributes enforced by this class.

## Lifecycle:
- Creation:
  - Instantiate directly: CorrelationPlot() to use defaults, or CorrelationPlot(cmap="viridis", bad="#FFFFFF") to override values.
  - Because this class inherits from pydantic.v1.BaseModel, construction performs pydantic validation/coercion of provided values.
- Usage:
  - Access attributes directly (instance.cmap, instance.bad) and pass the instance or its attributes to plotting routines.
  - Instances are immutable only if a pydantic config that enforces immutability is applied elsewhere; by default, fields may be set/updated through pydantic methods (for example, .copy(update=...)) or attribute assignment depending on the model configuration in the surrounding codebase.
- Destruction:
  - No special cleanup is required. The object has no external resources or context-manager behavior.

## Method Map:
graph LR
  A[Instantiate CorrelationPlot] --> B[Pydantic validation/coercion]
  B --> C[Access .cmap]
  B --> D[Access .bad]
  C --> E[Pass to plotting code]
  D --> E

(This class has no custom methods beyond those provided by pydantic.BaseModel; the diagram shows typical flow from instantiation to usage.)

## Raises:
- pydantic.ValidationError
  - Trigger: Provided values that cannot be validated/coerced to the declared field types by pydantic (for example, a complex nested object where a string is required).
  - Note: pydantic v1 may attempt coercion; only irreconcilable type mismatches or explicit validators will cause a ValidationError.

## Example:
- Default instance:
  - Create: CorrelationPlot()
  - Inspect: .cmap returns "RdBu", .bad returns "#000000"
- Custom instance:
  - Create: CorrelationPlot(cmap="viridis", bad="#FFFFFF")
  - Use: Pass instance.cmap and instance.bad into a heatmap-drawing function.
- Updating:
  - Use pydantic features to create a modified copy: instance.copy(update={"cmap": "coolwarm"}) to produce a new CorrelationPlot with the updated colormap.

## `src.ydata_profiling.config.Histogram` · *class*

*No documentation generated.*

## `src.ydata_profiling.config.CatFrequencyPlot` · *class*

## Summary:
Represents configuration options for how categorical value frequencies are plotted. Encapsulates whether to show the plot, the plot style, the maximum number of unique categories to display, and an optional color palette.

## Description:
This class is a small configuration model designed to be instantiated when preparing or rendering categorical frequency visualizations in the profiling/reporting pipeline. Typical callers are configuration loaders, report builders, or plotting utilities that accept a configuration object describing how to render category frequency plots.

Motivation and responsibility:
- Encapsulates plot-specific settings as a typed object instead of scattering raw dicts or function parameters across plotting code.
- Serves as a single source of defaults for categorical frequency visuals and enables downstream code to read consistent settings (show/type/max_unique/colors).
- Does not itself perform plotting; it only carries configuration data used by plotting/rendering components.

Known callers/factories:
- Configuration deserialization code that constructs settings objects from YAML/JSON or programmatic defaults.
- Report generation modules that combine multiple small config objects for different plot types.
- Plotting helper functions that accept an instance of this model to decide whether and how to render category-frequency visuals.

## State:
The class inherits from pydantic.v1.BaseModel; fields below are model attributes validated at instantiation by pydantic.

- show
  - Type: bool
  - Default: True
  - Semantics: If False, the category frequency plot should be considered disabled and not rendered.
  - Invariant: show is always a boolean.

- type
  - Type: str
  - Default: "bar"
  - Semantics: Intended to select the visual representation of frequencies; commonly used values are "bar" or "pie".
  - Constraint: The source code does not enforce an enumeration — any string is accepted by the model, but downstream plotting code should expect one of the intended values ("bar" or "pie").
  - Invariant: type is always a string.

- max_unique
  - Type: int
  - Default: 10
  - Semantics: Maximum number of unique categories to include in the plot (e.g., show top N categories).
  - Constraint: No explicit validation in this model prevents negative or zero values; callers should enforce meaningful ranges (e.g., positive integers) if required.
  - Invariant: max_unique is always an int.

- colors
  - Type: Optional[List[str]]
  - Default: None
  - Semantics: If provided, a list of color values (e.g., hex strings, named colors) to use for plotting categories.
  - Constraint: The model does not validate that strings are valid color specifications or that the list length matches max_unique.
  - Invariant: colors is either None or a list of strings.

Class invariants:
- Each attribute will conform to its declared type after pydantic validation. No cross-field constraints are enforced by this class (e.g., colors length vs max_unique, or type being within a fixed set).

## Lifecycle:
Creation:
- Instantiate directly by calling the constructor with zero or more keyword arguments corresponding to fields:
  - Example: CatFrequencyPlot(), CatFrequencyPlot(show=False), CatFrequencyPlot(type="pie", max_unique=5, colors=["#ff0000", "#00ff00"]).
- Pydantic will validate types at instantiation time and raise a pydantic ValidationError for type mismatches.

Usage:
- Read-only access pattern is typical: pass the instance to plotting code or report builders, and inspect attributes (show, type, max_unique, colors).
- No special sequencing of method calls is required — there are no custom methods on this class beyond BaseModel-provided behavior.
- If callers need additional constraints (e.g., ensure max_unique > 0 or type ∈ {"bar","pie"}), they should validate or normalize values before or after instantiation.

Destruction:
- No special cleanup or close operations are required. Instances are plain data holders managed by Python garbage collection.

## Method Map:
(Note: the class defines no custom methods; this diagram shows the typical flow of actions involving this config object.)

graph LR
    A[Create CatFrequencyPlot] --> B[pydantic validation]
    B --> C[Config object]
    C --> D[Plotting/Rendering code reads fields]
    D --> E[Render or skip plot based on show]
    E --> F[Use type/max_unique/colors to draw]

## Raises:
- pydantic.v1.error_wrappers.ValidationError
  - Trigger: Provided field values do not match the declared types (e.g., show="yes" instead of bool, max_unique="ten" instead of int, colors set to a string rather than List[str]).
- Note: This class does not explicitly raise ValueError, TypeError, or custom exceptions for application-level constraints (such as invalid plot type strings or non-positive max_unique). Those checks, if needed, must be implemented by callers or by extending this model.

## Example:
- Create with defaults:
  - Instantiate: CatFrequencyPlot()
  - Expected state: show=True, type="bar", max_unique=10, colors=None

- Create with explicit settings:
  - Instantiate: CatFrequencyPlot(show=False, type="pie", max_unique=5, colors=["#1f77b4", "#ff7f0e"])
  - Typical use: if instance.show is True then plotting code inspects instance.type to decide rendering logic and uses instance.colors if not None.

- Handling invalid types:
  - Instantiating with wrong types (e.g., CatFrequencyPlot(max_unique="five")) will raise pydantic ValidationError; catch or validate upstream as appropriate.

## `src.ydata_profiling.config.Plot` · *class*

## Summary:
Typed pydantic configuration container that aggregates plotting-related settings used by the profiling/reporting system.

## Description:
Plot is a small pydantic.v1.BaseModel that groups several plot-specific configuration objects and scalar plotting parameters into a single namespace. It is intended to be constructed by configuration-loading code (e.g., YAML/JSON deserialization) or by callers that assemble a report configuration, then passed to plotting and report-generation utilities which read its fields to control rendering behavior.

Typical callers:
- Configuration deserializers that build a complete report configuration.
- Report-generation modules that accept a Plot instance and pass its sub-configs to plotting helpers.
- Plotting utilities and exporters that read individual fields (for example, dpi and image_format) to configure outputs.

Responsibility boundary:
- Plot is strictly a data holder; it performs no rendering or validation beyond pydantic's type checks.
- Semantic validation (for example, ensuring a colormap string exists in the plotting backend, or that histogram parameters fall into acceptable ranges) is the responsibility of downstream plotting code.

## State:
Public attributes available after construction (with defaults from the source):

- missing: MissingPlot
  - Type: MissingPlot (pydantic BaseModel)
  - Default: MissingPlot()
  - Meaning: Controls missing-value visualization options (e.g., whether to force labels, which colormap to use). See MissingPlot documentation for attribute-level details and defaults.
  - Invariant: After construction, this attribute is an instance of MissingPlot.

- image_format: ImageType
  - Type: ImageType (Enum)
  - Default: ImageType.svg
  - Meaning: Preferred image output format used by rendering/exporting code (members: ImageType.svg, ImageType.png).
  - Notes: The field holds an enum member. When parsing user-provided strings from configuration files, convert the string to an ImageType member explicitly (for example, use ImageType(value)) before constructing Plot or ensure the deserializer performs that conversion; attempting to construct Plot with an incompatible value will raise a pydantic ValidationError.

- correlation: CorrelationPlot
  - Type: CorrelationPlot (pydantic BaseModel)
  - Default: CorrelationPlot()
  - Meaning: Holds settings for correlation plots, such as the colormap identifier and color for invalid/masked cells. See CorrelationPlot documentation for details.
  - Invariant: After construction, this attribute is an instance of CorrelationPlot.

- dpi: int
  - Type: int
  - Default: 800
  - Meaning: Raster export resolution (dots per inch) used when exporting PNG images.
  - Constraint: pydantic enforces integer-ness; callers should ensure a positive integer is used if required by downstream exporters.

- histogram: Histogram
  - Type: Histogram (pydantic BaseModel)
  - Default: Histogram()
  - Meaning: Configuration for histogram plotting. The specific fields and defaults of Histogram are not present in the provided snapshot.
  - Guidance for reimplementation: To preserve compatibility, Histogram should be a pydantic.v1.BaseModel subclass and be constructible with no arguments. If you re-create Histogram, consider common histogram parameters used by plotting code (for example: bins: Optional[Union[int, List[int]]] = None, density: bool = False, rug: bool = False), but ensure the final design matches the expectations of the plotting utilities that will consume histogram settings.

- scatter_threshold: int
  - Type: int
  - Default: 1000
  - Meaning: Maximum number of points for which scatter plots should be rendered naively. When the number of points exceeds this threshold, plotting utilities may opt to downsample or skip scatter plots for performance.
  - Constraint: pydantic enforces integer type; treat the value as a non-negative integer in plotting code.

- cat_freq: CatFrequencyPlot
  - Type: CatFrequencyPlot (pydantic BaseModel)
  - Default: CatFrequencyPlot()
  - Meaning: Configuration for categorical frequency plots (controls whether to show the plot, plot style/type, maximum unique categories to display, optional colors, etc.).
  - Important detail (alignment with CatFrequencyPlot): The cat_freq.type field is a string with default "bar" and should be treated as such by downstream code; no enum is enforced by the CatFrequencyPlot model in the provided snapshot. See CatFrequencyPlot documentation for the field-level defaults and semantics.
  - Invariant: After construction, this attribute is an instance of CatFrequencyPlot and its fields conform to the types declared by that model (for example, type is a str, show is a bool, max_unique is an int).

Class invariants:
- After successful pydantic construction, every documented attribute exists and has the declared type.
- Plot does not enforce cross-field constraints (for example, it does not check that dpi is only relevant for PNG or that histogram parameters are within certain ranges). Such semantic checks must be implemented by callers when necessary.
- Model mutability follows pydantic.v1.BaseModel default behavior (instances are mutable unless the broader project applies immutability settings).

## Lifecycle:
Creation:
- Construct via pydantic-style initialization:
  - Example forms: Plot() or Plot(dpi=300, image_format=ImageType.png, missing=MissingPlot(force_labels=False))
- Construction performs pydantic validation; invalid types or values incompatible with the declared field types will cause pydantic.v1.error_wrappers.ValidationError to be raised.

Usage:
- Typical usage pattern is read-only access by plotting functions:
  - Read nested configs (for example, plot_config.missing.cmap, plot_config.correlation.bad) when preparing each plot.
  - Use image_format to select an exporter; use dpi for raster export resolution.
  - Consult scatter_threshold when deciding to downsample or skip scatter plots.
  - Consult cat_freq fields (show, type, max_unique, colors) to decide whether and how to render categorical-frequency visuals.
- There is no required calling sequence; plotting utilities read the relevant fields at the time of rendering.

Destruction / cleanup:
- No special cleanup is required; Plot contains simple Python objects and is managed by the runtime/garbage collector.

## Method Map:
graph LR
  A[Instantiate Plot] --> B[Pydantic validation]
  B --> C[Access missing (MissingPlot)]
  B --> D[Access image_format (ImageType)]
  B --> E[Access correlation (CorrelationPlot)]
  B --> F[Access histogram (Histogram)]
  B --> G[Access dpi (int)]
  B --> H[Access scatter_threshold (int)]
  B --> I[Access cat_freq (CatFrequencyPlot)]
  C --> J[Plotting utility reads missing config]
  D --> K[Choose exporter based on image_format]
  E --> L[Configure correlation heatmap colors]
  F --> M[Configure histogram rendering]
  G --> N[Set raster export DPI]
  H --> O[Decide whether to render or downsample scatter]
  I --> P[Configure categorical frequency plot]

## Raises:
- pydantic.v1.error_wrappers.ValidationError
  - Trigger: Any field value provided to the constructor that cannot be validated/coerced to the declared field type by pydantic (for example, passing a non-integer for dpi or supplying an invalid type for cat_freq).
  - Note: For image_format, attempting to pass an incompatible value that cannot be converted to an ImageType member will result in a ValidationError; prefer converting configuration strings to ImageType members explicitly when parsing configurations.

- Plot itself does not raise runtime errors related to rendering; errors encountered when applying configuration values (for example, unknown colormap names) will originate from downstream plotting libraries.

## Example:
Construct defaults:
Plot()

Construct with overrides (narrative example):
- Provide explicit enum for image format and adjusted DPI, and supply nested sub-configs by constructing their pydantic models first. For example, construct a MissingPlot with force_labels disabled and a CorrelationPlot with a different colormap; then pass these instances into Plot(image_format=ImageType.png, dpi=300, missing=..., correlation=...).

Guidance when Histogram is missing:
- Ensure Histogram is implemented as a pydantic.v1.BaseModel subclass constructible with no arguments so Plot(histogram=Histogram()) remains valid. If you add fields to Histogram, coordinate those field names with the plotting utilities that consume histogram configuration.

Typical usage flow:
1) Load or build sub-configuration objects (MissingPlot, CorrelationPlot, CatFrequencyPlot, Histogram).
2) Construct Plot using the sub-configs and scalar overrides.
3) Pass Plot to plotting/export utilities; they read fields such as correlation.cmap, image_format, dpi, scatter_threshold, and cat_freq.type (a string) to decide rendering behavior.

## `src.ydata_profiling.config.Theme` · *class*

## Summary:
An enumeration of the supported UI/reporting theme identifiers. Provides a single, fixed set of string-valued theme members for configuration and template logic.

## Description:
Theme is a small enum subclass defining the allowed theme identifiers used across configuration and reporting. Use it when you need to validate, normalize, or serialize a theme choice. Typical callers include configuration parsers, report renderers, and asset-selection code that map a validated Theme to concrete CSS/templates.

This class exists to centralize the allowed theme values and prevent arbitrary strings from being passed where a known theme is required. It relies on Python's standard enum.Enum semantics (members are singletons, have .name and .value attributes, and support value- and name-based lookup).

## State:
- Class: Theme (subclass of enum.Enum)
- Members (name -> value):
    - united -> "united"
    - flatly -> "flatly"
    - cosmo  -> "cosmo"
    - simplex -> "simplex"
- Member types:
    - Each member is an instance of Theme. Each member's .value is of type str.
- Valid values:
    - Only the four strings "united", "flatly", "cosmo", "simplex" are valid values for value-based construction.
- Invariants:
    - Member identity is unique and stable: Theme.united is Theme("united") (singleton property).
    - The set of members is fixed at definition time; no dynamic addition of members is supported.

## Lifecycle:
- Creation:
    - You do not call an __init__ to create new members. Obtain members by:
        1. Attribute access: Theme.united
        2. Name lookup: Theme['flatly']  (lookup by member name)
        3. Value lookup / coercion: Theme('cosmo')  (lookup by member value)
- Usage:
    - Validate an input string and obtain a Theme member via Theme(input_string). If successful, use member.value to get the canonical string for serialization or asset selection.
    - Iterate over available themes with: for t in Theme: ...
    - Compare with identity or equality: Theme.united is Theme.united and Theme.united == Theme("united").
- Destruction:
    - No special cleanup required. Enum members are singletons managed by Python runtime.

## Method Map:
graph TD
    Input[Input string or code] --> Lookup{Lookup approach}
    Lookup -->|Attribute| Attr[Theme.united / Theme.flatly / ...]
    Lookup -->|Name| NameLookup[Theme['united']]
    Lookup -->|Value| ValueLookup[Theme('united')]
    Attr --> Use[Read .value or .name]
    NameLookup --> Use
    ValueLookup --> Use
    Use --> Downstream[Serialization / Validation / Asset selection]

## Raises:
- ValueError:
    - When calling Theme(some_value) and some_value is not equal to any member's .value (e.g., Theme("unknown")).
- KeyError:
    - When using name lookup Theme[some_name] and some_name is not one of the defined member names (e.g., Theme["unknown"]).
- Notes:
    - These exception behaviors follow the standard enum.Enum implementation in Python. Callers that coerce user input into Theme should handle ValueError (invalid value) and KeyError (invalid name) as appropriate.

## Example:
- Successful value lookup and use:
    1. input_string = "flatly"
    2. member = Theme(input_string)          # returns Theme.flatly
    3. use_name = member.value                # "flatly" — safe to serialize or pass to templates

- Attribute access:
    1. member = Theme.united
    2. member.name  -> "united"
    3. member.value -> "united"

- Handling invalid input (value lookup):
    1. input_string = "unknown"
    2. try:
           member = Theme(input_string)
       except ValueError:
           # handle invalid theme, e.g., fallback to default or raise configuration error

- Listing available themes:
    1. options = [t.value for t in Theme]    # -> ["united", "flatly", "cosmo", "simplex"]

This documentation gives the complete definition of the Theme enum: the four permitted string values, how to obtain members, the exceptions to expect when coercing input, and common usage patterns. It contains everything necessary to reimplement and use Theme consistently.

## `src.ydata_profiling.config.Style` · *class*

## Summary:
A pydantic model that groups presentation-related configuration: an ordered palette of primary colors, an optional Theme enum member selecting the report theme, a logo identifier string, and a private list of label prefixes. Exposes primary_color as the canonical (first) palette entry.

## Description:
Style is the typed container for visual/style configuration used by reporting and rendering components. Typical callers:
- Configuration parsers and factories that assemble application configuration objects.
- Report builders and template renderers that map a validated Theme to concrete CSS/templates and read color/logo assets.
- Consumers that need a single canonical color (use primary_color) or the ordered palette (primary_colors).

Motivation: centralizes style settings so downstream code depends on a single validated object rather than scattered primitives. The theme field is typed to the Theme enum, so consumers receive a Theme enum member (not an arbitrary string) when a theme is set — consult the Theme enum docs for permitted theme values and how to coerce/validate inputs.

## State:
- primary_colors (List[str])
    - Type: list[str]
    - Default: ["#377eb8", "#e41a1c", "#4daf4a"]
    - Meaning: ordered palette of primary colors where index 0 is the canonical/highest-priority color.
    - Constraints: elements are strings (commonly hex color codes). The class does not enforce a color-string format beyond the string type.
    - Note: the default value is a class-level list; callers who mutate primary_colors on an instance should be aware of typical Python mutable-default semantics.
- primary_color (property) -> str
    - Behavior: a read-only convenience property that returns the first string in the primary_colors list (i.e., primary_colors[0]). This property provides the canonical primary color for the Style instance.
    - Default example: With the class default primary_colors = ["#377eb8", "#e41a1c", "#4daf4a"], primary_color returns "#377eb8".
    - Edge: if primary_colors is empty, accessing primary_color raises IndexError because the implementation performs direct index access without an empty-list guard.
    - Note: the property reflects the current state of primary_colors; mutating primary_colors changes the value returned by primary_color.
- logo (str)
    - Type: str
    - Default: ""
    - Meaning: free-form identifier for a logo asset (file path, URL, inline markup); no format is enforced.
- theme (Optional[Theme])
    - Type: Theme | None
    - Default: None
    - Meaning: when set, this is a Theme enum member (an instance of Theme). Theme members have a .value attribute of type str (see Theme docs for permitted values).
    - Behavior: pydantic will validate/coerce input into a Theme member where possible (e.g., accepting a Theme instance or a value that matches a Theme member); invalid values raise pydantic.ValidationError at construction.
- _labels (List[str])  (private attribute)
    - Type: list[str]
    - Default: ["_"]
    - Meaning: internal helper for label-prefix logic; defined with pydantic.PrivateAttr so it is not part of the public model fields or serialization output.

Class invariants:
- Fields present at construction conform to pydantic validation (type-correct).
- There is no enforced invariant that primary_colors is non-empty; callers must ensure non-empty palettes if they rely on primary_color.

## Lifecycle:
- Creation:
    - Instantiate via the pydantic BaseModel constructor:
        - Example: Style(), Style(primary_colors=[...], logo="...", theme=Theme.united)
    - All fields have defaults; pydantic raises ValidationError for type/coercion failures (e.g., theme value does not match any Theme member).
- Usage:
    - Read primary_color for the canonical top-priority color; mutate primary_colors if a different palette is required (mutations affect primary_color).
    - Access theme as a Theme enum member; use theme.value (a str) when passing the theme to templates or serializing.
    - _labels is private — modify only if you understand internal consumers.
- Destruction:
    - No special cleanup required.

## Method Map:
graph TD
    Instantiate[Style(...) instantiation] --> Pydantic[BaseModel validation/coercion]
    Pydantic --> Instance[Style instance]
    Instance -->|read| PrimaryColor[primary_color -> primary_colors[0]]
    Instance -->|read/write| Palette[primary_colors (list)]
    Instance -->|read| ThemeField[theme (Optional[Theme])]
    ThemeField -->|use .value| Template[Template/CSS selection]
    PrimaryColor --> Renderer[Report / Template / Renderer]

## Raises:
- pydantic.ValidationError
    - Trigger: during instantiation if provided values do not meet the expected types or cannot be coerced (e.g., theme value does not match any Theme member).
- IndexError
    - Trigger: accessing primary_color when primary_colors == [].
- Notes:
    - No other exceptions are raised by the class definition itself. Assignment-time validation behavior depends on pydantic settings (e.g., validate_assignment).

## Example:
1. Default:
   - s = Style()
   - s.primary_color  # -> "#377eb8" (first entry of the default primary_colors)
   - s.theme          # -> None
2. Custom palette and theme:
   - s = Style(primary_colors=["#000000", "#ffffff"], theme=Theme("flatly"), logo="assets/logo.svg")
   - s.primary_color  # -> "#000000"
   - s.theme          # -> Theme.flatly  (enum member)
   - s.theme.value    # -> "flatly"     (string suitable for templates)
3. Guard against empty palette:
   - s = Style(primary_colors=[])
   - accessing s.primary_color raises IndexError; ensure the list contains at least one string before access.

This documentation treats primary_color as the canonical first palette entry (matching the component's behavior and dependent Theme semantics) while also documenting the empty-list edge case and pydantic validation interactions.

### `src.ydata_profiling.config.Style.primary_color` · *method*

## Summary:
A read-only property that returns the canonical primary color for this Style instance — specifically, the first string in the primary_colors list.

## Description:
Known callers:
    - No direct callers were identified in the inspected snapshot. Typical consumers include theming, plotting, or report-rendering code that needs one consistent primary color.

Context and rationale:
    - Implemented as a separate @property to centralize the canonical selection rule (always use the first color). This prevents duplication of indexing logic across consumers and allows changing the selection strategy in one place if needed.

Lifecycle:
    - Can be accessed at any time after a Style instance is created.
    - It does not perform initialization or validation; it simply returns the current first element of primary_colors.

## Args:
    None

## Returns:
    str: The first element of self.primary_colors.
    - Typical values: color strings, commonly hex color codes (for example, "#377eb8").
    - Example: With the class default primary_colors = ["#377eb8", "#e41a1c", "#4daf4a"], primary_color returns "#377eb8".

## Raises:
    IndexError: If self.primary_colors is an empty list (accessing index 0 is invalid). This is the only exception raised by this property itself.

## State Changes:
Attributes READ:
    - self.primary_colors

Attributes WRITTEN:
    - None (no mutation performed)

## Constraints:
Preconditions:
    - self.primary_colors must be a sequence with at least one element before calling this property.
    - Elements are expected to be strings representing colors; the property does not validate format (e.g., hex vs. named colors).

Postconditions:
    - Returns the exact object stored at self.primary_colors[0] without modifying the Style instance.

## Side Effects:
    - None. No I/O, external calls, or modifications to objects outside self are performed by this property.

## `src.ydata_profiling.config.Html` · *class*

## Summary:
Represents HTML- and asset-related configuration for report generation and rendering; a typed container of presentation flags and asset location/prefix settings used by report builders and template renderers.

## Description:
Html is a small pydantic model grouping settings that control how HTML output is produced and where supporting assets are resolved. Typical callers:
- Configuration loaders/parsers that build the application configuration object graph.
- Report builders and template renderers that read these flags to decide whether to inline assets, include a navigation bar, minify output, or resolve assets from local paths or remote prefixes.
- Tests and utilities that need to vary report rendering options in a typed way.

Motivation: centralizes HTML output-related settings behind a single validated object (Html) so downstream code depends on a small, well-typed contract rather than a collection of loose primitives.

Responsibility boundary:
- Html only declares typed fields and defaults. It does not itself implement rendering, asset fetching, minification, or validation of referenced filesystem paths; consumers interpret these fields to implement behavior.

## State:
- style: Style
    - Type: Style (pydantic model)
    - Default: Style()
    - Meaning: visual/style configuration (palette, theme, logo) used by renderers.
    - Notes: the default Style() instance is created at module import time; because it is a mutable object, mutating style on an Html instance that uses the default may affect other instances if the same default object is referenced. To avoid accidental sharing, pass a fresh Style() when constructing multiple independent Html instances.
- navbar_show: bool
    - Type: bool
    - Default: True
    - Meaning: whether a report navigation bar should be shown. Html does not itself render the navbar; consumers read this flag.
- minify_html: bool
    - Type: bool
    - Default: True
    - Meaning: indicates whether consumers should perform HTML minification before emitting the report. The class only signals intent; no minification is performed by Html itself.
- use_local_assets: bool
    - Type: bool
    - Default: True
    - Meaning: when True, consumers may prefer local asset copies over CDN or remote assets. No filesystem or network checks are performed by Html.
- inline: bool
    - Type: bool
    - Default: True
    - Meaning: when True, consumers may inline CSS/JS assets into the HTML output. Html only conveys this preference.
- assets_prefix: Optional[str]
    - Type: Optional[str] (None or str)
    - Default: None
    - Meaning: optional prefix to prepend to asset URLs (for CDN base URL or URL path prefix). Html does not validate that the prefix is a valid URL or path.
- assets_path: Optional[str]
    - Type: Optional[str] (None or str)
    - Default: None
    - Meaning: optional filesystem path or storage key where consumer code may read/write assets. Html does not check existence/permissions.
- full_width: bool
    - Type: bool
    - Default: False
    - Meaning: layout hint indicating whether the rendered report should use a full-width layout. Consumers decide how to map this to templates/CSS.

Class invariants:
- All fields are validated by pydantic at construction time to their declared types (e.g., booleans and optional strings). There are no additional invariants enforced by the class (for example, no requirement that assets_path be set when use_local_assets is True).
- The style field is expected to be a Style instance or a value coercible to Style by pydantic; invalid values will raise pydantic.ValidationError at instantiation.

## Lifecycle:
- Creation:
    - Instantiate via the pydantic BaseModel constructor:
        - Examples: Html(), Html(style=Style(...)), Html(assets_prefix="https://cdn.example.com/", inline=False)
    - All fields have defaults; callers may override any subset of fields.
    - Validation: pydantic performs type-checking/coercion and will raise pydantic.ValidationError for incompatible values.
- Usage:
    - Typical usage pattern: construct Html once (often as part of a larger config), then read its attributes from rendering code:
        - Check inline/use_local_assets to decide asset packaging strategy.
        - Read assets_prefix/assets_path for URL/path resolution.
        - Read style and pass it to template renderers for theme/colors/logo.
        - Use navbar_show and full_width to choose template fragments or CSS classes.
    - No required call ordering is enforced by Html itself.
- Destruction:
    - No cleanup required. Html has no resources to close. When used within larger systems, dispose of any resources opened by consumers (filesystem handles, network connections) separately.

## Method Map:
graph TD
    Instantiate[Instantiate Html(...)] --> Validate[Pydantic validation]
    Validate --> HtmlInstance[Html instance]
    HtmlInstance --> Renderer[TemplateRenderer / ReportBuilder]
    Renderer -->|reads| StyleField[style (Style)]
    Renderer -->|reads| InlineFlag[inline]
    Renderer -->|reads| UseLocal[use_local_assets]
    Renderer -->|reads| AssetsPrefix[assets_prefix]
    Renderer -->|reads| AssetsPath[assets_path]
    Renderer -->|reads| Navbar[navbar_show]
    Renderer -->|reads| Minify[minify_html]
    Renderer -->|reads| Layout[full_width]
    StyleField --> ThemeAndColors[Theme, primary_colors, logo] 

(Notes: Html has no custom methods of its own; the diagram shows typical data flow from an Html instance to consumers.)

## Raises:
- pydantic.ValidationError
    - Trigger: when constructing Html(...) with values that cannot be coerced/validated to the declared field types (e.g., passing a non-bool for navbar_show that pydantic cannot coerce).
- No other exceptions are raised by the class definition itself. Runtime errors due to consumer behavior (e.g., attempting to use assets_path that does not exist) are the responsibility of consumers.

## Example:
1) Default instance:
   - h = Html()
   - h.style        # -> Style instance (the default Style() created at import time)
   - h.inline       # -> True
   - h.assets_path  # -> None

2) Custom configuration for a renderer:
   - h = Html(
         style=Style(primary_colors=["#000","#fff"], logo="assets/logo.svg"),
         inline=False,
         use_local_assets=False,
         assets_prefix="https://cdn.example.com/",
         full_width=True,
     )
   - Renderer behavior (example): the rendering component reads h.inline (False) and h.use_local_assets (False) and therefore emits link/script tags pointing to URLs constructed using h.assets_prefix.

3) Avoiding shared default Style instance:
   - If you need independent Style instances per Html, pass a freshly constructed Style:
     - h1 = Html(style=Style(...))
     - h2 = Html(style=Style(...))

Notes and edge cases:
- Because defaults are simple typed primitives or a Style() instance created at import time, be mindful of mutating complex default objects (style or fields within). To avoid shared mutable defaults, explicitly pass a new Style instance when constructing Html for independent usage.
- Html does not validate filesystem paths or URL formats; consumers must validate assets_path and assets_prefix if correctness is required.

## `src.ydata_profiling.config.Duplicates` · *class*

## Summary:
A lightweight configuration model that holds settings related to "duplicates" reporting: an integer slice size (head) and a display key (key).

## Description:
This class is a minimal pydantic configuration model (inherits from pydantic.v1.BaseModel) intended to encapsulate configuration values concerning duplicate-record reporting or presentation. It should be instantiated anywhere duplicate-reporting display settings are needed (for example, when building a duplicates section in a profiling/reporting pipeline). The class itself only defines storage and type validation for two fields; any interpretation (e.g., that head controls how many duplicate rows to display) is inferred from the field names and defaults, not enforced by the class.

Known callers/factories:
- Any configuration loader or higher-level settings object that aggregates profiling/reporting configuration may instantiate this class (not shown in this file). Because it is a BaseModel, it is compatible with pydantic-driven settings factories or direct instantiation.

Motivation and responsibility boundary:
- Motivation: Provide a simple, typed container for duplicates-related options so that the rest of the codebase can accept a single object rather than separate primitive arguments.
- Responsibility: Hold typed values and perform pydantic validation on construction. It does not implement business logic (e.g., computing duplicates) or enforce semantic constraints beyond type checking.

## State:
- head (int)
    - Type: int
    - Default: 10
    - What it represents: a numeric limit/size to be used by consumers (commonly interpreted as the number of duplicate rows to show). This interpretation is inferred from naming and default; the class does not enforce bounds or semantics.
    - Constraints/invariants: No explicit runtime bounds are enforced by this class. Validation will ensure the value can be coerced to int per pydantic rules.
- key (str)
    - Type: str
    - Default: "# duplicates"
    - What it represents: a display key or label for duplicate-related output. Interpretation is inferred from name/default; not enforced.
    - Constraints/invariants: No explicit constraints beyond pydantic type validation.

Class invariants:
- Instances always have the attributes head and key present (pydantic BaseModel populates defaults if not provided).
- head will be an int (or coercible to int under pydantic validation rules) and key will be a str after successful construction.

## Lifecycle:
- Creation:
    - Instantiate directly using the constructor of the model, e.g. Duplicates() or Duplicates(head=5, key="dupes").
    - Required args: none; both fields have defaults.
    - Because the class inherits from pydantic.v1.BaseModel, construction triggers validation (type checking/coercion) performed by pydantic.
- Usage:
    - Read attributes directly (instance.head, instance.key).
    - The model is immutable or mutable depending on BaseModel configuration elsewhere; this class does not override BaseModel settings — default pydantic behavior applies.
    - No special method ordering is required — it is a plain data holder.
- Destruction:
    - No cleanup responsibilities. No context-manager or close() methods are defined.

## Method Map:
- This model defines no custom methods. Typical flows revolve around construction and attribute access.

Mermaid diagram (method/flowchart):
graph TD
    A[Create Duplicates instance] --> B{pydantic validation}
    B --> C[Valid -> instance with head:int and key:str]
    B --> D[Invalid -> pydantic.ValidationError raised]
    C --> E[Consumers read instance.head / instance.key]

## Raises:
- pydantic.ValidationError (raised by pydantic.v1.BaseModel on instantiation)
    - Trigger conditions: when supplied values cannot be validated/coerced to the declared types (for example, a non-numeric string for head that pydantic cannot coerce to int).
- Note: The class itself contains no explicit raise statements; raised exceptions are those produced by the BaseModel validation process.

## Example:
1) Default construction and access:
    - Instantiate: instance = Duplicates()
    - Access: instance.head  # -> 10
              instance.key   # -> "# duplicates"

2) Custom values:
    - Instantiate: instance = Duplicates(head=5, key="duplicate rows")
    - Access: instance.head  # -> 5
              instance.key   # -> "duplicate rows"

3) Validation failure (illustrative):
    - Attempt: Duplicates(head="not-an-int")
    - Result: pydantic.ValidationError is raised because head cannot be coerced to an int.

Notes:
- This documentation intentionally separates what the class enforces (type presence and validation by pydantic) from typical/assumed semantic uses (how consumers interpret head and key). The latter are plausible usages inferred from names and defaults and are not programmatically enforced by this class.

## `src.ydata_profiling.config.Correlation` · *class*

## Summary:
Represents configuration options for correlation analysis used by the profiler. Encapsulates which correlation to compute (key), whether to calculate correlations, thresholds and heuristics for warning about high correlations, and discretization bins for non-parametric correlation estimates.

## Description:
This class is a thin configuration model (Pydantic BaseModel) intended to be instantiated when configuring correlation-related behavior in the profiling pipeline. Typical scenarios:
- Created as a nested element of a larger profiling configuration object to control how correlations are computed and reported.
- Constructed directly in tests or utilities when running correlation computations in isolation.

Motivation and responsibility boundary:
- Encapsulates only declarative configuration (no computation logic). It centralizes correlation-related parameters so downstream correlation routines can accept a single, validated object rather than many loose arguments.
- It does not perform any correlation computation itself; it only holds parameters and relies on callers to interpret them.

## State:
Attributes (public; declared on the model)
- key (str)
    - Type: str
    - Default: "" (empty string)
    - Semantics: Identifier of the correlation method to use (e.g., "pearson", "spearman", "cramers_v"). The codebase that consumes this config should map this string to the implementation.
    - Constraints: No programmatic constraint in this model; expected to be a short identifier string.
- calculate (bool)
    - Type: bool
    - Default: True
    - Semantics: Whether correlation computation should be performed at all.
    - Constraints: Boolean value; non-bool values will be validated/coerced by Pydantic if possible.
- warn_high_correlations (int)
    - Type: int
    - Default: 10
    - Semantics: Number of top high-correlation pairs to report or to trigger warnings on. Interpretation (e.g., whether this limits reporting or only affects warning text) is up to the consumer.
    - Expected values: non-negative integers make sense semantically; model does not enforce a lower-bound.
- threshold (float)
    - Type: float
    - Default: 0.5
    - Semantics: Floating threshold used to decide what is considered a "high" correlation (e.g., absolute correlation >= threshold is considered high).
    - Expected range: typically between 0.0 and 1.0; not enforced by this model.
- n_bins (int)
    - Type: int
    - Default: 10
    - Semantics: Number of bins to use when discretizing continuous variables for certain correlation estimators (e.g., when estimating mutual information or binned measures).
    - Expected values: positive integers; model does not enforce positivity.

Class invariants:
- There are no programmatic invariants enforced by this class beyond the type checks performed by Pydantic. Any semantic relationships (for example, threshold in [0, 1] and n_bins > 0) are expected to be validated or enforced by the callers if required.

## Lifecycle:
Creation
- Instantiate by calling Correlation(...) with zero or more of the attributes set as keyword arguments.
- Pydantic conveniences available: construction from a dict via Correlation.parse_obj(dict), from a JSON string via parse_raw, and low-level construction via Correlation.construct (bypasses validation).
- All parameters are optional because defaults are provided.

Usage
- Typical usage pattern:
    1. Create the Correlation instance (or obtain it from a larger settings object).
    2. Pass the instance to correlation computation routines, which read its attributes to control behavior.
    3. Optionally call .dict(), .json(), or .copy() (inherited from BaseModel) to serialize or duplicate the configuration.
- There is no required ordering of attribute access; attributes are read-only for most consumers but the model instance itself is mutable by default unless a global Pydantic config makes it immutable.

Destruction / Cleanup
- No special cleanup is required. The class does not hold external resources. Standard Python garbage collection suffices.

## Method Map:
Graph showing typical interactions (inherited BaseModel helpers are available but class defines no custom methods):

flowchart LR
    A[Instantiate Correlation] --> B[Read attributes: key, calculate, threshold, warn_high_correlations, n_bins]
    B --> C[Pass to correlation routine]
    C --> D[Correlation routine reads attributes and computes results]
    A --> E[BaseModel.dict()/json()/copy() used for serialization or duplication]

Note: The class itself defines no custom methods beyond what it inherits from pydantic.v1.BaseModel.

## Raises:
- During instantiation or parsing, pydantic.v1.error_wrappers.ValidationError may be raised if provided values cannot be validated/coerced to the declared types.
    - Examples:
        * Supplying a non-numeric string for threshold that cannot be converted to float may trigger ValidationError.
        * Supplying a list where an int is expected (for warn_high_correlations or n_bins) will trigger ValidationError unless coercion is possible.
- The class itself does not raise custom exceptions.

## Example:
- Create a configuration that disables correlation computation:
    - Instantiate with calculate set to False (other fields may be left as defaults).
- Create a configuration to detect stronger correlations:
    - Instantiate with threshold set to 0.7 and warn_high_correlations set to 5.
- Serialize for storage or CLI printing:
    - Use the model's .dict() or .json() methods (inherited from BaseModel) to obtain a serializable representation.

Implementation notes for reimplementation:
- Implement as a Pydantic BaseModel with the declared fields and defaults:
    - key: str = ""
    - calculate: bool = Field(default=True)
    - warn_high_correlations: int = Field(default=10)
    - threshold: float = Field(default=0.5)
    - n_bins: int = Field(default=10)
- Rely on Pydantic for type validation and (optional) coercion. If stricter enforcement (e.g., range checks for threshold or positivity for n_bins) is required, add validators or tighter Field(...) constraints and document those changes accordingly.

## `src.ydata_profiling.config.Correlations` · *class*

## Summary:
A Pydantic model that groups three per-method Correlation configuration objects (pearson, spearman, auto) into a single, reusable configuration holder for the profiling pipeline.

## Description:
Correlations is a small declarative container whose only responsibility is to expose three named Correlation configuration models so correlation-related routines can accept a single argument. It does not perform any computation.

Typical usage scenarios:
- Nested inside a larger profiling settings model to expose correlation options at a single location.
- Constructed directly in tests or utilities to supply method-specific correlation settings to correlation computation functions.

Responsibility and boundaries:
- Solely stores configuration (three Correlation instances). It relies on upstream or downstream code to interpret and act on these configurations.
- Does not enforce semantic relationships across the three Correlation instances (e.g., consistent thresholds); any such constraints must be enforced by callers.

## State:
Public attributes (declared on the model)
- pearson (Correlation)
    - Type: Correlation
    - Default: Correlation(key="pearson")
    - Purpose: Settings for Pearson correlation calculation.
- spearman (Correlation)
    - Type: Correlation
    - Default: Correlation(key="spearman")
    - Purpose: Settings for Spearman correlation calculation.
- auto (Correlation)
    - Type: Correlation
    - Default: Correlation(key="auto")
    - Purpose: Settings for automatically selected or fallback correlation behavior.

Notes about defaults and validation:
- The default Correlation expressions appear in the class definition; they are evaluated when the class is defined.
- When constructing Correlations, Pydantic will validate each provided field; dictionaries or mappings provided for any of the three fields will be coerced/parsed into Correlation instances when possible.
- Correlations instances (and nested Correlation instances) are mutable by default because they inherit Pydantic BaseModel behavior. If immutability is required, configure the Pydantic model config or avoid mutating nested models.
- To avoid any possibility of unintended shared state when mutating nested models, create fresh Correlation instances for each Correlations instance or use .copy(deep=True) before modifying nested data.

Class invariants:
- Each of pearson, spearman, and auto will be instances of Correlation after validation.
- There are no additional enforced invariants relating the three fields.

## Lifecycle:
Creation:
- Instantiate directly: Correlations() produces an object with default Correlation values.
- Override fields by passing Correlation instances or dict-like values: Correlations(spearman=Correlation(key="spearman", threshold=0.7)) or Correlations(spearman={"key": "spearman", "threshold": 0.7}).
- Alternative constructors (inherited from BaseModel): 
    - Correlations.parse_obj(obj) to create from a mapping
    - Correlations.parse_raw(json_str) to create from a JSON string
    - Correlations.construct(...) for low-level construction that bypasses validation (not recommended for normal use)

Usage:
- Typical order:
    1. Construct Correlations as part of application settings or per-run configuration.
    2. Pass the Correlations instance to routines that compute or report correlations; those routines read pearson, spearman, and/or auto as needed.
    3. Optionally call .dict()/.json() to serialize or .copy(deep=True) to duplicate prior to mutation.
- There is no required invocation order for accessing attributes. Mutations are allowed unless the model is configured otherwise.

Destruction:
- No special cleanup or resource management is required.

## Method Map:
flowchart LR
    A[Instantiate Correlations()] --> B[Access pearson/spearman/auto]
    B --> C[Pass to correlation computation routines]
    C --> D[Routines read Correlation fields and compute results]
    A --> E[Use .dict()/.json() for serialization or .copy(deep=True) to duplicate]

## Raises:
- pydantic.v1.error_wrappers.ValidationError
    - Raised during instantiation or parsing if provided values cannot be validated/coerced into Correlation instances for any of the fields.
    - Examples:
        * Passing a value for pearson that is neither a Correlation nor a coercible mapping.
        * Supplying types that cannot be converted to the expected nested model types.

## Example:
- Create with defaults:
    - cfg = Correlations()
- Override spearman with a dict (which will be parsed into Correlation):
    - cfg = Correlations(spearman={"key": "spearman", "threshold": 0.7})
- Duplicate before mutating nested models to avoid affecting other references:
    - cfg2 = cfg.copy(deep=True)
    - cfg2.pearson.threshold = 0.9
- Serialize to JSON:
    - cfg.json()
Notes:
- If you need independent mutable nested models for each Correlations instance, pass fresh Correlation(...) instances when creating Correlations, or use .copy(deep=True) immediately after construction before performing mutations.

## `src.ydata_profiling.config.Interactions` · *class*

## Summary:
Represents configuration for pairwise interactions settings used by the profiling system — toggles whether interactions are treated as continuous and lists specific column targets to include.

## Description:
This class is a tiny configuration-holder modeled as a Pydantic BaseModel. Instantiate it when you need to convey how interaction computation should behave: whether interaction values are continuous (boolean) and which target columns (by name) to consider for interaction analysis.

Typical callers:
- Configuration loaders or factories that build a larger profiling configuration object.
- Tests and code-paths that require a compact representation of interaction-related flags.

Motivation / Responsibility:
- Encapsulates only the interaction-related options so the larger configuration can compose this object.
- Provides Pydantic-backed validation and type coercion for its fields.

## State:
Attributes (public fields):
- continuous (bool)
  - Type: bool
  - Default: True
  - Valid values: True or False
  - Invariant: Always a boolean value; indicates whether interactions are treated as continuous (True) or categorical/discrete (False).

- targets (List[str])
  - Type: list of strings
  - Default: [] (an empty list)
  - Valid values: list where each element is a string representing a column/feature name.
  - Invariant: All elements, if present, are strings. There is no uniqueness or ordering guarantee enforced by this class.

Important implementation note:
- The class sets targets: List[str] = [] at class definition time. That creates a single mutable default list shared across instances if the instantiation does not override it. To avoid surprising shared-state behavior, callers should pass an explicit list when creating instances (e.g., Interactions(targets=['col_a'])) or the implementer should replace the default with a factory (Field(default_factory=list)).

Class-level invariants:
- continuous must remain a boolean.
- targets must be a sequence of string values.
- No other constraints (such as non-empty list or uniqueness) are enforced here.

## Lifecycle:
Creation:
- Instantiate with zero or both keyword arguments:
  - Interactions()  # uses defaults: continuous=True, targets=[]
  - Interactions(continuous=False)
  - Interactions(targets=['col1','col2'])
- Pydantic BaseModel performs type validation/coercion at creation time.

Usage:
- Typical usage is read-only access to the two fields after construction:
  - Check .continuous to decide the interaction computation mode.
  - Iterate .targets to filter or select target columns for interaction computation.
- There are no methods on this class; it functions purely as a typed data container.

Destruction / cleanup:
- No cleanup required. No context manager or close() method.

## Method Map:
flowchart TD
    A[Create Interactions instance] --> B[Pydantic validation/coercion]
    B --> C[Access attributes: .continuous, .targets]
    C --> D[Consume values in downstream profiling logic]

## Raises:
- pydantic.ValidationError
  - Trigger: Passed values that do not match the declared types (for example, targets is set to an int, or continuous is set to a non-boolean that Pydantic cannot coerce).
  - Note: The exact exception class originates from Pydantic (pydantic.v1 error wrappers). Consumers of this class should catch Pydantic's ValidationError when validating user-provided configuration.

## Example:
- Create with defaults:
  - Interactions()
    - Result: continuous=True, targets=[]
- Create with explicit targets:
  - Interactions(targets=['age', 'income'])
    - Result: continuous=True, targets=['age', 'income']
- Avoid shared default pitfall:
  - a = Interactions()
  - b = Interactions()
  - a.targets.append('x')
  - After this, b.targets may also contain 'x' because the class-level default list is shared. Prefer passing an explicit list when creating instances to avoid this.

## `src.ydata_profiling.config.Samples` · *class*

## Summary:
Typed, validated container for sampling counts (head, tail, random) used to communicate how many rows to include for different sampling strategies.

## Description:
A minimal pydantic BaseModel that groups three integer configuration values describing sampling behavior. Instantiate this model when you need a validated, serializable object to pass sampling counts into components such as profiling, preview, or dataset-inspection utilities. The class only carries numeric parameters; it does not perform sampling itself.

Typical callers
- Configuration loaders that convert raw dict/YAML/JSON settings into typed models.
- Profiling or preview subsystems that accept a Samples instance to decide how many head, tail, and random rows to fetch.

Responsibility boundary
- Validate, store, and serialize three related integer parameters.
- Do not implement dataset access, sampling algorithms, or enforce semantic constraints like non-negativity or total-count limits.

## State:
Public attributes (initialized via constructor or defaults)
- head: int
  - Default: 10
  - Meaning: number of rows to select from the start (head) of a dataset.
  - Constraint: annotated as int. Pydantic will coerce input to int when possible; if coercion fails a ValidationError is raised.
  - Caller note: negative values are allowed by the model definition; callers that require non-negative values must enforce that.

- tail: int
  - Default: 10
  - Meaning: number of rows to select from the end (tail) of a dataset.
  - Same type/constraint notes as head.

- random: int
  - Default: 0
  - Meaning: number of additional random rows to include.
  - Same type/constraint notes as head.

Class invariants
- After successful instantiation, head, tail, and random are integers as validated by pydantic.
- There are no enforced relational invariants between fields (for example, no constraint that head + tail + random <= dataset_size).
- Instances are mutable by default consistent with pydantic.BaseModel unless a global BaseModel config elsewhere overrides mutability.

## Lifecycle:
Creation
- Construct directly by calling the class with keyword arguments; all fields have defaults so no arguments are required.
  - Acceptable forms: create a default instance (no args), or provide any subset of fields as keyword arguments to override defaults.

Validation
- Validation and coercion happen at construction time via pydantic. If a provided value cannot be converted to an integer, instantiation raises pydantic.ValidationError.

Usage
- Read attributes directly (samples.head / samples.tail / samples.random) in sampling code.
- Serialize using BaseModel utility methods (dict(), json()) for persistence, logging, or embedding in larger config objects.
- Because this class holds only data, typical sequencing is: instantiate → read/serialize → discard.

Destruction / cleanup
- No resources to release. No context-manager or close() semantics required.

## Method Map:
graph LR
  A[Call Samples(...) to instantiate] --> B[Pydantic validation/coercion]
  B --> C[Read attributes: head / tail / random]
  C --> D[Optional serialization: dict() / json()]
  
(Note: the class defines no custom methods. Callers rely on attribute access and BaseModel-provided utilities.)

## Raises:
- pydantic.ValidationError
  - Trigger: Any provided value for head, tail, or random that cannot be coerced to int by pydantic (for example, an unparseable string or incompatible complex type). This prevents instantiation and contains field-level error details.
- No other exceptions are raised directly by this class definition.

## Example (concrete usage described in plain text):
- Create default instance:
  - Construct with no arguments to get defaults: head=10, tail=10, random=0. Use the instance directly to drive sampling counts.
- Create customized instance:
  - Construct with chosen values (for example, override head and random while leaving tail default). After construction, read attributes: samples.head, samples.tail, samples.random.
- Serialize for storage or logging:
  - Use the BaseModel helper to convert to a plain dict or JSON string (e.g., call the model's dict() or json() method) before writing to a file or attaching to telemetry.

Usage notes and edge cases
- Enforce non-negativity and dataset-clamping in the caller: the Samples model does not prevent negative values or values larger than the dataset. Downstream code should clamp or validate counts against dataset length to avoid slicing errors or duplicate rows.
- Prefer constructing Samples from configuration parsers that already coerce types (e.g., YAML/JSON loaders) so that pydantic validation remains the final gate for type correctness.

## `src.ydata_profiling.config.Variables` · *class*

## Summary:
Represents a typed container for variable descriptions used by the profiling configuration; a lightweight pydantic model that holds a mapping of variable identifiers to their descriptive metadata.

## Description:
This class encapsulates a mapping of variable names to their descriptions and exists as a small, validated configuration fragment within the profiling configuration system.

Scenarios for instantiation:
- When building or loading profiling configuration that includes human-readable descriptions for dataset variables.
- When code needs a typed object (rather than a plain dict) to store or validate variable descriptions before serializing to YAML/JSON or merging into larger configuration objects.

Motivation and responsibility boundary:
- Provides a distinct, minimal abstraction for storing variable descriptions instead of scattering plain dicts throughout the codebase.
- Responsibility: hold and validate the top-level mapping of variable identifiers to their descriptions. It does not impose a schema on the contents of each description (keys or nested structure) — that responsibility is intentionally left to callers or to downstream validation logic.

## State:
Attributes (public):
- descriptions: dict
  - Type: dict
  - Default: {} (empty dict)
  - Valid values: any mapping object accepted by pydantic for dict; typically a mapping of string variable names to description values (strings or nested structures). The class itself does not restrict key or value types beyond the dict requirement.
  - Invariants: descriptions is always an instance attribute on model instances (pydantic ensures it is present). After initialization, descriptions is a plain Python dict (or a mapping converted by pydantic) accessible for reads and writes.

Class invariants:
- Instances are pydantic BaseModel objects; therefore, attribute values conform to pydantic's validation rules at construction. The invariant is that descriptions holds a dict-compatible value according to pydantic validation for the declared type.

Notes about defaults:
- The default value is a mutable empty dict. Users should be cautious when using the class-level default directly as a shared mutable object; however, pydantic BaseModel initializes instance attributes, so typical usage creates instance-local dicts. Still, avoid relying on mutation of the class-level attribute.

## Lifecycle:
Creation:
- Instantiate by calling the class with an optional descriptions argument.
  - Required args: none (all fields have defaults).
  - Optional: descriptions (a dict-like object).
  - Example instantiation: Variables() or Variables(descriptions={'age': 'Age in years'})

Usage:
- Typical usage is to construct an instance and then:
  - Read or update `.descriptions` directly.
  - Serialize via BaseModel methods such as `.dict()` or `.json()` when integrating with other configuration serialization/deserialization.
- No special sequencing of method calls is required. There are no custom methods defined on this class; it relies on BaseModel behavior.

Destruction / cleanup:
- No special cleanup is required. Instances do not manage external resources and have no context manager or close() methods.

## Method Map:
This class defines no custom methods. The following diagram shows typical interactions using BaseModel-provided operations.

flowchart LR
    A[Instantiate Variables] --> B[Access/modify .descriptions]
    B --> C[Validate via pydantic at construction]
    B --> D[Serialize via .dict()/.json()]
    D --> E[Write to config file / merge into larger config]

(Note: .dict() and .json() are inherited from pydantic.v1.BaseModel)

## Raises:
- ValidationError (from pydantic) is raised during instantiation if the provided `descriptions` argument is not compatible with the declared type (dict).
  - Trigger conditions:
    - Passing a value for descriptions that pydantic cannot coerce to a dict (for example, a non-mapping object that cannot be interpreted as a dict).
- No other exceptions are raised by this class itself; runtime errors can occur if callers mutate descriptions in unexpected ways.

## Example:
- Create with defaults:
  - variables = Variables()
  - variables.descriptions  # -> {}

- Create with initial descriptions:
  - variables = Variables(descriptions={'age': 'Age in years', 'income': 'Annual income in USD'})

- Read a description:
  - desc = variables.descriptions.get('age')

- Serialize to dict for inclusion in a larger configuration:
  - config_fragment = variables.dict()  # {'descriptions': {'age': 'Age in years', ...}}

Notes:
- If you need stricter structure (for example, enforce that each description is a string or an object with specific fields), wrap/replace this class with a more specific pydantic model for the description values or validate descriptions before constructing Variables.

## `src.ydata_profiling.config.IframeAttribute` · *class*

*No documentation generated.*

## `src.ydata_profiling.config.Iframe` · *class*

## Summary:
A pydantic data model that holds iframe configuration: height (CSS size), width (CSS size), and an IframeAttribute value that selects which iframe attribute to use.

## Description:
This class groups three iframe-related settings into a typed container so callers (renderers, report builders, configuration loaders) can pass iframe display options as a single object. It is implemented as a pydantic.v1.BaseModel to get runtime type validation of the declared fields.

When to instantiate:
- When you need a typed configuration object describing iframe dimensions and which iframe attribute to use.
- In configuration construction, settings parsing, or when passing display options to an HTML/template renderer.

Responsibility boundary:
- Responsibility: carry and validate (at the type level) the three fields: height, width, attribute.
- Not responsibility: perform CSS syntax validation, render HTML, or define the IframeAttribute enum members (the enum is defined elsewhere).

## State:
Fields (constructor parameters and instance attributes):

- height: str
  - Default: "800px"
  - Meaning: CSS size string for iframe height (examples: "800px", "100%"). The class enforces that the value is a string via pydantic type validation.

- width: str
  - Default: "100%"
  - Meaning: CSS size string for iframe width (examples: "100%", "800px"). The class enforces that the value is a string via pydantic type validation.

- attribute: IframeAttribute
  - Default: IframeAttribute.srcdoc
  - Meaning: determines which iframe attribute will be used when embedding content (the enum type and its members are defined elsewhere in the codebase).
  - The class enforces that the value is an instance/member of IframeAttribute via pydantic type validation.

Class invariants:
- After successful construction, the three fields have types matching their annotations (str, str, IframeAttribute). No additional invariants or cross-field constraints are defined in this class.

## Lifecycle:
Creation:
- Call the constructor with zero or more keyword arguments:
    - Iframe()                      # all defaults
    - Iframe(height="600px")        # override height
    - Iframe(width="80%", attribute=IframeAttribute.srcdoc)  # override width and attribute
- pydantic performs validation during initialization and will raise a validation error if provided values do not match the annotated types.

Usage:
- Typical usage is read access to .height, .width, and .attribute for rendering or template generation.
- The model does not define custom instance methods; it is a typed data container.

Destruction:
- No cleanup actions are required; instances are normal Python objects with no special teardown.

## Method Map:
Simple data-flow for typical usage:

flowchart LR
    A[Call Iframe(...) to construct] --> B[pydantic BaseModel validation]
    B --> C{Validation OK}
    C --> D[Read .height/.width/.attribute to render iframe]
    B --> E[Validation error raised]

## Raises:
- pydantic.ValidationError
    - Raised during construction if any field value fails pydantic's validation against the annotated type (for example, if height is not a str or attribute is not a valid IframeAttribute member).
    - The exact error details follow pydantic's standard validation error format.

## Example:
Create with defaults:
    iframe = Iframe()
    # iframe.height == "800px"
    # iframe.width == "100%"
    # iframe.attribute == IframeAttribute.srcdoc

Create with custom dimensions (using the visible enum member for attribute):
    iframe = Iframe(height="600px", width="80%", attribute=IframeAttribute.srcdoc)
    # Use iframe.height and iframe.width when generating the <iframe> element
    # Use iframe.attribute to decide which iframe attribute to set when rendering

Notes:
- The full set of valid values for attribute is defined by the IframeAttribute enum elsewhere in the codebase; consult that enum to choose non-default values.
- This model limits validation to type checking performed by pydantic and does not enforce CSS semantics or rendering rules.

## `src.ydata_profiling.config.Notebook` · *class*

## Summary:
A pydantic data model that groups notebook-specific display configuration; it contains a single nested Iframe configuration object used to control iframe rendering for notebook/report views.

## Description:
This class is a minimal pydantic.v1.BaseModel used to encapsulate notebook display settings as part of the broader configuration system. It exists to provide a typed container for a nested Iframe configuration so callers (configuration loaders, report builders, HTML/rendering components, or notebook exporters) can accept or pass a single Notebook object that carries iframe display options.

When to instantiate:
- When constructing or loading the application's configuration that will be used for notebook or embedded-report rendering.
- When handing configuration to components that render reports in Jupyter notebooks or other iframe-capable environments.
- Typically instantiated by a higher-level configuration loader or by code that aggregates settings for different output targets.

Motivation and responsibility boundary:
- Responsibility: hold exactly the notebook-related sub-configuration (currently a single Iframe model) and enforce runtime type validation of that nested object via pydantic.
- Not responsibility: perform rendering, validate CSS semantics, or manage other unrelated configuration keys. Those responsibilities belong to renderers and other configuration models.

## State:
Attributes (public instance attributes produced from the __init__ parameters):

- iframe: Iframe
  - Type: src.ydata_profiling.config.Iframe (pydantic.v1.BaseModel subclass)
  - Default: Iframe() — a new Iframe instance created with its defaults (height="800px", width="100%", attribute=IframeAttribute.srcdoc).
  - Valid values: an instance of Iframe or any mapping/dictionary compatible with Iframe's fields that pydantic can coerce into an Iframe.
  - Invariants:
    - Always present on constructed instances (no None unless explicitly allowed elsewhere).
    - After construction, iframe is guaranteed to be validated by pydantic to match the Iframe model: iframe.height is str, iframe.width is str, iframe.attribute is a valid IframeAttribute member.
    - No additional cross-field invariants are enforced at the Notebook level.

Notes on nested validation:
- Because Notebook inherits from pydantic.v1.BaseModel and declares iframe: Iframe, pydantic will validate and coerce nested input at construction time. Acceptable inputs include:
  - An Iframe instance.
  - A dict/mapping with keys matching Iframe fields (e.g., {"height": "600px"}), which pydantic will use to construct an Iframe.

## Lifecycle:
Creation:
- Instantiate via the class constructor:
    - Notebook()  # uses the default nested Iframe()
    - Notebook(iframe=Iframe(...))  # pass an Iframe instance
    - Notebook(iframe={"height": "600px", "width": "80%"})  # pass a mapping; pydantic will build the nested Iframe
- No other required arguments.

Usage:
- Typical usage is read-only access to notebook.iframe and its fields:
    - Access notebook.iframe.height / notebook.iframe.width / notebook.iframe.attribute for rendering decisions.
- No instance methods are defined on Notebook; it is a typed container only.
- There is no required call ordering; construct it, read fields as needed.

Destruction / cleanup:
- Instances are plain Python objects with no cleanup hooks. No context manager or close() is required.

## Method Map:
Simple flow showing construction and use:

flowchart LR
    A[Instantiate Notebook(...)] --> B[pydantic BaseModel nested validation]
    B --> C{Validation OK}
    C --> D[Use notebook.iframe.* for rendering or templates]
    B --> E[ValidationError raised]

(Note: There are no Notebook instance methods; the flow focuses on construction and typical read-only use.)

## Raises:
- pydantic.ValidationError
  - Trigger conditions:
    - If the provided value for iframe cannot be validated/coerced into the Iframe model (for example, if iframe is provided as an int or another incompatible type).
    - If nested Iframe validation fails (e.g., a non-str value for height/width, or an invalid attribute value that is not a member of IframeAttribute).
  - The exact ValidationError details follow pydantic's standard error structure (field path, error type, and message).

## Example:
Create with defaults:
    notebook = Notebook()
    # notebook.iframe is an Iframe instance with default dimensions and attribute

Create by passing an Iframe instance:
    iframe = Iframe(height="600px", width="80%")
    notebook = Notebook(iframe=iframe)

Create by passing a mapping (pydantic will construct the nested model):
    notebook = Notebook(iframe={"height": "600px", "width": "80%"})
    # Equivalent to Notebook(iframe=Iframe(height="600px", width="80%"))

Handling validation errors:
    try:
        notebook = Notebook(iframe=123)  # invalid type for nested model
    except pydantic.ValidationError as e:
        # Inspect e.errors() for details; handle or surface configuration error

## `src.ydata_profiling.config.Report` · *class*

## Summary:
A lightweight configuration model representing report-level configuration; currently exposes a single integer attribute `precision` with a default value of 8.

## Description:
Report is a minimal pydantic-based configuration model intended to carry report-related configuration values across the codebase. It is intended to be instantiated wherever report configuration is assembled or passed (for example, when creating or rendering reports) and to serve as a single-structured container for report-level settings.

Motivation:
- Encapsulates report formatting/configuration in a small, typed object.
- Keeps configuration values in a single place to pass through APIs that generate or render reports.

Typical scenarios:
- Constructing a Report and passing it to a report-generation routine.
- Loading or merging higher-level configuration into an instance of Report before use.

## State:
Attributes (public):
- precision (int)
  - Type: int
  - Default: 8
  - Description: Represents the integer precision value used for report formatting/representation.
  - Constraints: The class definition does not declare any explicit range or validation constraints beyond the type annotation. Any runtime validation or coercion behavior is provided by the inherited pydantic BaseModel.

Class invariants:
- No additional invariants are declared by this class beyond the presence of the `precision` attribute and its declared type annotation.

## Lifecycle:
Creation:
- Instantiate directly using the class constructor:
  - Required args: none.
  - Optional args: precision (int). If omitted, the instance uses the default value 8.
- Example instantiation: Report() or Report(precision=5)

Usage:
- After instantiation, read the `precision` attribute to guide formatting or numeric display decisions.
- This model is a passive data container; it defines no custom methods. Typical usage is:
  1. Create instance (optionally with precision override).
  2. Pass the instance to consumers (report builders/renderers).
  3. Consumers read `precision` to decide numeric formatting behavior.

Destruction / cleanup:
- The class has no explicit cleanup responsibilities. There is no context-manager protocol or close method implemented here.

## Method Map:
graph TD
    A[Constructor: Report(...)] --> B[Instance created with attribute precision:int]
    B --> C[Consumers read instance.precision]
    C --> D[Formatting / rendering logic uses precision]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#ff9,stroke:#333,stroke-width:1px
    style C fill:#9ff,stroke:#333,stroke-width:1px
    style D fill:#9f9,stroke:#333,stroke-width:1px

## Raises:
- The __init__ (construction) of this model relies on pydantic.v1.BaseModel behavior. If callers provide values that violate the declared types (for example, passing a non-integer for `precision`), the underlying pydantic validation may raise validation errors. The specific exception types and messages are produced by pydantic and are not defined in this class.

## Example:
- Create with default precision:
  Report()
  # instance.precision == 8

- Create with a custom precision:
  Report(precision=3)
  # instance.precision == 3

- Invalid input (behavior depends on pydantic validation; may raise a validation error):
  Report(precision="not-an-int")
  # this will trigger validation behavior from the BaseModel layer

## `src.ydata_profiling.config.Settings` · *class*

*No documentation generated.*

## `src.ydata_profiling.config.Config` · *class*

## Summary:
Represents a minimal configuration holder that exposes a single class-level environment variable prefix, env_prefix, set to "profile_".

## Description:
This class exists solely to centralize a canonical environment-variable prefix value as a class attribute. It has no methods or instance-level state in the provided code; other modules in the codebase may import or reference this class to read the standardized env_prefix value. Instantiate only when an instance object is desirable for API symmetry, but typical usage is to access the prefix directly from the class.

Scenarios where to use:
- When other parts of the system need a single, authoritative prefix for environment variables (e.g., composing environment variable names).
- When code expects a named object that groups configuration-related constants and prefers attribute access (Config.env_prefix) over hard-coded strings.

Motivation and responsibility:
- Encapsulates a single, reusable configuration constant in one place to avoid scattering the literal "profile_" throughout the codebase.
- Responsibility is intentionally narrow: provide the env_prefix value. The class does not parse files, read environment variables, or validate values.

## State:
- env_prefix (class attribute)
    - Type: str
    - Value: "profile_"
    - Mutability: Writable (standard Python class attribute); treating it as a constant is recommended.
    - Valid range/values: any string is allowed by the implementation; the source code sets it to "profile_".
    - Invariant: The class as provided guarantees env_prefix equals "profile_" unless mutated at runtime by other code.

No instance attributes or __init__ parameters are defined in the provided source.

Class invariants:
- The only invariant enforced by the class as written is the presence of the attribute env_prefix; its value is initially "profile_".
- There are no additional invariants or validation enforced by methods in this class.

## Lifecycle:
Creation:
- Instantiation: optional; the default object constructor (Config()) is available (no __init__ defined).
- Required args: none.

Usage:
- Typical usage is to read the prefix directly from the class (Config.env_prefix).
- If an instance is created, reading the attribute from the instance returns the same value unless overwritten on the instance or class (instance-level attribute assignment will shadow the class attribute).

Destruction:
- No special cleanup required. The class has no resources, file handles, or context-manager semantics.

## Method Map:
graph TD
    A[Start] --> B[Reference class attribute]
    B --> C{Access pattern}
    C -->|Class-level| D[Config.env_prefix -> "profile_"]
    C -->|Instance-level| E[instance = Config(); instance.env_prefix -> "profile_"]
    D --> F[Use value in calling code]
    E --> F

## Raises:
- The class definition and attribute access do not raise any exceptions by themselves.
- Potential runtime exceptions could arise only if external code intentionally deletes or overwrites the attribute, or if attribute access occurs in an unusual object model manipulation scenario; none originate from this class's code.

## Example:
- Accessing the canonical prefix from the class:
    - Read directly: Config.env_prefix  # yields the string "profile_"
- Using an instance (functionally identical unless mutated):
    - instance = Config()
    - instance.env_prefix  # yields "profile_"

Notes:
- Because the attribute is a plain class attribute, code that treats env_prefix as immutable should avoid reassigning it at runtime. If mutability is required, manage changes at call sites consciously.

### `src.ydata_profiling.config.Settings.update` · *method*

## Summary:
Returns a new, validated Settings instance created by merging the current settings with a user-supplied updates mapping; missing keys from the updates mapping are filled from the current Settings, and the updates mapping is mutated in-place to include those defaults.

## Description:
- Known callers and contexts:
    - No direct call sites were discovered in the scanned codebase. Conceptually this method is intended for layering configuration: programmatic updates (for example, user-provided dicts produced at runtime or parsed from user input) are merged with the in-memory defaults of a Settings instance so the resulting configuration contains user overrides and all required default values.
    - Typical lifecycle: invoked when applying runtime or user-provided configuration fragments on top of an existing Settings object before using the configuration to generate reports or initialize processing components.

- Why this is a separate method:
    - Encapsulates the two-step process of merging configuration dictionaries (with non-overwriting, recursive semantics) and then re-validating/parsing the merged structure into a Settings object.
    - Keeps callers free of merge and validation details and centralizes the semantics (non-overwriting, deep merge + pydantic validation) in one place.

## Args:
    updates (dict):
        - A mutable mapping representing user-specified configuration overrides.
        - Must support .items() and item assignment (i.e., behave like a standard dict).
        - Nested mapping values are expected for nested configuration sections (e.g., for fields that are themselves models/dicts).
        - No default; this parameter is required.

## Returns:
    Settings:
        - A new Settings instance (the pydantic model) produced by parsing a copy of the current Settings updated with the merged mapping.
        - The returned object is fully validated by pydantic (type conversions and model construction for nested fields apply).
        - Edge cases:
            * If updates is empty, the returned Settings is effectively a validated copy of self (defaults preserved).
            * If validation fails, the method raises (see Raises) and does not return.

## Raises:
    AttributeError:
        - Trigger: Raised by the underlying merge helper when a nested value in the current Settings is a mapping but the corresponding key in updates holds a non-mapping value (e.g., defaults expect a dict at key "x" but updates["x"] is a string). The deep-merge implementation will attempt mapping operations on that value and fail with an AttributeError.
    TypeError or AttributeError:
        - Trigger: If updates does not support .items() or item assignment (i.e., is not a proper dict-like mutable mapping), Python will raise TypeError/AttributeError while performing the merge.
    pydantic.ValidationError:
        - Trigger: Raised by pydantic.parse_obj if the merged mapping cannot be coerced/validated into the Settings model (for example, wrong types or missing required structure after merge).
    RecursionError (rare):
        - Trigger: Extremely deep nested structures may exceed Python recursion limits during the recursive merge.

## State Changes:
- Attributes READ:
    - Reads the full model dictionary produced by self.dict(), which includes these public fields:
        title, dataset, variables, infer_dtypes, show_variable_description, pool_size,
        progress_bar, vars, sort, missing_diagrams, correlation_table, correlations,
        interactions, categorical_maximum_correlation_distinct, memory_deep, plot,
        duplicates, samples, reject_variables, n_obs_unique, n_freq_table_max,
        n_extreme_obs, report, html, notebook
    - (Practically: the method reads the entire serialized representation of self via self.dict()).

- Attributes WRITTEN:
    - None on self: the original Settings instance is not mutated; a new Settings instance is returned.
    - External mutation: the updates argument (the dict passed in) is mutated in-place by the merge helper to include missing keys taken from self.

## Constraints:
- Preconditions:
    - updates must be a mutable, mapping-like object (standard dict or similar) with .items() and item assignment semantics.
    - For any key K where the current Settings has a nested mapping (dict) value, updates[K] should either be absent or itself be a mapping; otherwise the deep merge will raise AttributeError.
    - Caller should be aware that updates will be mutated; pass a copy if that behavior is undesired.

- Postconditions:
    - On successful return:
        * A new Settings instance is returned whose values are the result of taking the keys/values supplied by updates (user overrides) and filling in any missing keys from the current Settings defaults (deep, non-overwriting merge).
        * The returned instance has been validated and parsed by pydantic (nested dicts converted to nested model instances where applicable).
        * The updates mapping now contains the merged structure (i.e., missing keys have been added).

## Side Effects:
- Mutates the updates dict in-place via the recursive merge helper: missing keys are added to updates (preserving any values originally present in updates).
- No I/O, network calls, or other external side effects.
- No mutation of the original Settings instance (self) — a new validated instance is produced and returned.

## Implementation notes for reimplementation:
- Use self.dict() to obtain a plain-structure representation of the current settings (source defaults).
- Perform a deep, non-overwriting recursive merge that inserts keys from the defaults into the updates mapping only where updates lacks those keys (the helper used in this code mutates the updates mapping in place and will raise if it encounters a mapping-vs-non-mapping conflict at any nested path).
- After merging, produce a new Settings object by copying self with the merged mapping applied and then parsing/validating that copy via pydantic (ensures nested model fields are constructed and types validated).
- Ensure the method documents the in-place mutation behavior and potential exceptions so callers can prepare (e.g., pass a copy of updates if mutation is undesired).

### `src.ydata_profiling.config.Settings.from_file` · *method*

## Summary:
Loads configuration from a YAML file on disk and returns a newly constructed Settings instance populated and validated from that file's contents.

## Description:
- Known callers and call context:
    - No direct callers were found in the provided class excerpt. Typically this method is invoked by application startup or configuration-loading code (for example, CLI entrypoints, test setup, or any routine that needs to load a profiling configuration from disk) during the configuration-loading stage of the report-generation pipeline.
- Reason this is a separate method:
    - Encapsulates the I/O (file open + YAML parsing) and model construction so callers can obtain a validated Settings instance in one call.
    - Keeps file parsing logic separate from callers (separation of concerns) and centralizes error behavior and validation through pydantic's parse logic.
    - Facilitates reuse wherever loading Settings from a YAML file is needed (tests, examples, CLI, programmatic usage).

## Args:
    config_file (Union[pathlib.Path, str]):
        Path or string path to the YAML configuration file to read.
        - Allowed values: any filesystem path to a readable text file that contains YAML.
        - Not allowed: non-existent paths (will raise FileNotFoundError), non-text files that cannot be decoded by the platform default encoding (may raise UnicodeDecodeError).

## Returns:
    Settings:
        - A new Settings model instance produced by Settings.parse_obj(data) where `data` is the result of yaml.safe_load on the file contents.
        - If the YAML contents do not provide some model fields, pydantic will apply the model's defaults for those fields.
        - Edge cases:
            - If the YAML file is empty, yaml.safe_load returns None; parse_obj(None) will trigger pydantic validation errors (see Raises).
            - If the YAML contains values with incorrect types or missing required structure, pydantic validation will raise a ValidationError.

## Raises:
    FileNotFoundError:
        - If the given config_file path does not exist when attempting to open it.
    PermissionError:
        - If the process lacks permission to read the file.
    UnicodeDecodeError:
        - If the file cannot be decoded using the platform default encoding when opened (open without explicit encoding).
    yaml.YAMLError (or a subclass):
        - If yaml.safe_load fails to parse the file as valid YAML (syntax errors, etc.).
    pydantic.error_wrappers.ValidationError:
        - If the parsed YAML content cannot be validated/converted into a Settings instance (e.g., top-level value is None, wrong types, missing required structure for fields that do not have defaults).

## State Changes:
- Attributes READ:
    - None on an existing Settings instance — the method is defined as a @staticmethod and does not read or depend on any instance attributes.
- Attributes WRITTEN:
    - None on a pre-existing Settings instance. The method constructs and returns a new Settings object; it does not mutate any existing object or module-level state.

## Constraints:
- Preconditions:
    - config_file must be a path-like object (str or pathlib.Path) pointing to a file that the process can open for reading.
    - The file must contain YAML representing a mapping / dictionary structure compatible with the Settings model (otherwise parse/validation fails).
- Postconditions:
    - On success, returns a Settings instance whose fields reflect the values present in the YAML file; any fields omitted in the YAML are populated from the Settings model defaults and validated by pydantic.
    - No side effects (no global state mutation); only the returned object reflects parsed configuration.

## Side Effects:
- I/O:
    - Reads the specified file from disk (opens with the platform default text encoding).
- External library calls:
    - Calls yaml.safe_load to deserialize YAML content into Python objects.
    - Calls Settings.parse_obj (pydantic) to validate and instantiate the Settings model from the loaded Python data.
- Observable effects outside the return value:
    - None (no writes to disk, no network calls, no mutation of other objects).

## `src.ydata_profiling.config.SparkSettings` · *class*

## Summary:
SparkSettings is a small, declarative configuration container (a Settings subclass) that customizes several nested profiling options for Spark-oriented profiling runs — it provides nested univariate, correlation, interaction, missing-diagram, and sampling defaults tuned for Spark workflows.

## Description:
SparkSettings exists to provide a compact, typed bundle of configuration tweaks that differ from the project's general defaults when profiling Spark datasets. It composes several smaller Pydantic-backed models (Univariate, Correlation, Interactions, Samples) and a few plain-typed flags/collections so callers can pass a single object to profiling code that expects Spark-specific defaults.

When to instantiate:
- When building a profiling configuration specifically for Spark data sources (e.g., a factory or loader that constructs a top-level Config/Settings object for Spark runs).
- In tests or utilities that need the same tuned defaults used for Spark profiling.

Responsibility boundary:
- Purely declarative: SparkSettings holds configuration values and nested models only. It must not implement profiling logic.
- Validation and type-coercion are delegated to the underlying Pydantic/Settings base-class machinery and to the nested models' validators.

Known callers/factories:
- Higher-level configuration loaders/factories that assemble a full profiling Settings/Config object for different backends (CSV, Pandas, Spark).
- Profiling entrypoints that branch behavior based on which Settings subclass is used.

## State:
All fields are public attributes (declared at class definition); their types, default values (as defined in the class body), and important notes are listed below.

- vars: Univariate
  - Type: Univariate (Pydantic submodel)
  - Default: Univariate()  (constructed at class definition time)
  - Mutations at class definition: vars.num.low_categorical_threshold is set to 0 by the class body (overrides Univariate/NumVars default).
  - Semantics: Groups per-datatype univariate settings; here the numeric low_categorical_threshold is tuned to 0 for Spark runs.
  - Important: Because the default Univariate() instance is created once at class-definition time, it may be shared across instances unless callers supply a fresh Univariate instance at construction or the class is implemented with a factory default.

- infer_dtypes: bool
  - Type: bool
  - Default: False
  - Semantics: Whether to attempt inferred datatypes during profiling; False by default for this Spark-targeted configuration.

- correlations: Dict[str, Correlation]
  - Type: mapping from string to Correlation model
  - Default: {
      "spearman": Correlation(key="spearman", calculate=True),
      "pearson": Correlation(key="pearson", calculate=True),
    } (these Correlation instances are constructed at class-definition time)
  - Semantics: Named correlation-method configurations that downstream correlation routines read to decide which correlations to compute and how.
  - Note: Each Correlation instance uses Correlation's own defaults for other fields (threshold, warn_high_correlations, n_bins), as described in the Correlation model.

- correlation_table: bool
  - Type: bool
  - Default: True
  - Semantics: Whether to render/produce a correlation table in reports.

- interactions: Interactions
  - Type: Interactions (Pydantic submodel)
  - Default: Interactions() (constructed at class-definition time)
  - Mutations at class definition: interactions.continuous is set to False by the class body (overrides Interactions default True).
  - Semantics: Controls whether pairwise interactions should be treated as continuous and which targets to include.

- missing_diagrams: Dict[str, bool]
  - Type: mapping from diagram-name to boolean flag
  - Default: {"bar": False, "matrix": False, "dendrogram": False, "heatmap": False}
  - Semantics: Toggles whether specific missing-value visualizations are produced. All are disabled by default for Spark runs here.

- samples: Samples
  - Type: Samples (Pydantic submodel)
  - Default: Samples() (constructed at class-definition time)
  - Mutations at class definition: samples.tail is set to 0 and samples.random is set to 0 by the class body (overrides Samples defaults head=10, tail=10, random=0).
  - Semantics: Number-of-row sampling counts for head/tail/random; here tail is disabled (0) and random is 0 by default to avoid expensive tail/random reads in Spark profiling.

Class invariants and important notes:
- Types and basic coercion are enforced by the underlying Pydantic/Settings machinery at construction time.
- Because many defaults are instantiated at class-definition time (nested Univariate, Correlation instances, Interactions, Samples, and mutable dicts/lists), those default objects may be shared across all SparkSettings instances unless the caller provides fresh instances during construction or the implementer uses Field(default_factory=...) patterns.
- No additional runtime invariants (e.g., head/tail/random non-negativity or correlation threshold range) are enforced by SparkSettings itself — enforce in callers if necessary.

## Lifecycle:
Creation:
- Instantiate via constructor (same semantics as its Settings base class / Pydantic model):
  - SparkSettings()  # uses class-level defaults
  - SparkSettings(vars=Univariate(...), samples=Samples(...))  # pass fresh nested models to avoid shared defaults
  - Alternatively, nested fields may be supplied as dicts acceptable to Pydantic parsing (e.g., SparkSettings(samples={"head":5,"tail":0,"random":0})).

Usage:
- Typical usage is read-only: profiling logic reads flags and nested attributes to decide which computations and visualizations to run.
- If mutation is required, prefer to:
  - Construct with explicit nested instances, or
  - Use instance.copy(deep=True).copy(update={...}) (Pydantic helpers) to obtain a deep-cloned config to avoid mutating class-level defaults shared across instances.

Destruction:
- No special cleanup; SparkSettings holds no external resources.

Recommended sequencing:
1. Construct SparkSettings (prefer supplying fresh nested instances if you will modify nested state).
2. Read fields to configure profiling behavior.
3. If modifications needed, copy(deep=True) and then update.
4. Discard when done; rely on normal GC.

## Method Map:
(The class defines no custom methods; the diagram shows construction and access flow.)

flowchart LR
    A[Define SparkSettings class (class-body runs)] --> B[Class-level nested defaults instantiated: Univariate(), Correlation(...), Interactions(), Samples(), dicts]
    B --> C[Optional class-body tweaks applied: vars.num.low_categorical_threshold=0, interactions.continuous=False, samples.tail=0, samples.random=0]
    C --> D[Instantiate SparkSettings(...) via Pydantic/Settings constructor]
    D --> E[Pydantic validation/coercion of provided values]
    E --> F[Caller reads attributes: .vars, .infer_dtypes, .correlations, .correlation_table, .interactions, .missing_diagrams, .samples]
    F --> G[Profiler uses values to control Spark-specific profiling behavior]
    note right of B: Beware: those class-level instances may be shared across multiple SparkSettings instances

## Raises:
- pydantic.v1.error_wrappers.ValidationError
  - Trigger: Occurs during instantiation if supplied values (for top-level fields or nested fields) cannot be validated/coerced to the declared types (for example, passing a non-dict where a nested model is expected and coercion fails).
- No custom exceptions are raised by SparkSettings itself. Any runtime errors from consumers interpreting configured values are the consumer's responsibility.

## Example:
1) Default instantiation (uses class-level defaults):
  s = SparkSettings()
  # Inspect a tuned default
  # Note: s.vars.num.low_categorical_threshold == 0 (overridden in class body)
  # s.interactions.continuous == False (overridden in class body)
  # s.samples.tail == 0

2) Instantiate with fresh nested instances to avoid shared defaults:
  fresh_vars = Univariate()                     # fresh Univariate instance
  fresh_vars.num.low_categorical_threshold = 0  # same effective setting but instance-local
  fresh_samples = Samples(head=10, tail=0, random=0)
  fresh_interactions = Interactions(continuous=False)
  s2 = SparkSettings(vars=fresh_vars, samples=fresh_samples, interactions=fresh_interactions)

3) Instantiate with inline mapping (Pydantic will parse nested dicts):
  s3 = SparkSettings(samples={"head": 5, "tail": 0, "random": 0}, infer_dtypes=False)

4) Avoid in-place mutation of class-level defaults:
  # BAD: mutating nested defaults created at class-definition time affects all instances
  s_default_a = SparkSettings()
  s_default_b = SparkSettings()
  s_default_a.vars.num.quantiles.append(0.99)  # may also appear in s_default_b.vars.num.quantiles
  # Prefer:
  s_safe = s_default_a.copy(deep=True)
  s_safe.vars = s_safe.vars.copy(update={"num": s_safe.vars.num.copy(update={"quantiles": s_safe.vars.num.quantiles + [0.99]})})

Implementation notes for reimplementation:
- Implement SparkSettings as a Pydantic-based model subclassing the project's Settings base class.
- Define fields with the exact types and defaults shown above.
- If you want to avoid shared mutable defaults, replace class-level instantiation with Field(default_factory=...) for nested models and mutable mappings (recommended change):
  - e.g., vars: Univariate = Field(default_factory=Univariate)
  - and similarly for interactions and samples, and use Field(default_factory=lambda: {...}) for missing_diagrams if you need instance-local dicts.
- Preserve the explicit class-body tweaks (low_categorical_threshold=0, interactions.continuous=False, samples.tail=0) by applying equivalent initialization logic in a validator or by constructing the default nested models with the desired values.

### `src.ydata_profiling.config.Config.get_arg_groups` · *method*

## Summary:
Return the shorthand argument mapping for a named argument group from the class-level arg_groups mapping, possibly filling missing values from Config._shorthands — this may mutate the stored group dictionary in-place.

## Description:
- Known callers:
    - No direct callers were present in the provided code snapshot. This function is a small, focused utility intended to be called by configuration-loading or argument-processing code that needs the shorthand (resolved) form of a named argument group.
- When invoked:
    - Typically used during configuration resolution or initialization when the program needs the shorthand arguments for a specific configuration group (for example, to expand or supply defaults for missing arguments).
- Why this logic is its own method:
    - The method centralizes the logic for retrieving a group's arguments and applying shorthand/default substitutions (via Config.shorthands) so callers do not need to know how shorthand substitution is performed or duplicate that logic. It keeps group lookup and shorthand resolution in one place.

## Args:
    key (str): Name/key of the argument group to retrieve. Must be present as a key in Config.arg_groups (a mapping stored at the class level). No default.

## Returns:
    dict: A dictionary containing the shorthand-resolved arguments for the requested group.
    - The returned dict is the "shorthand_args" result produced by calling Config.shorthands(..., split=False).
    - When split=False, Config.shorthands returns (shorthand_args, {}), so only the first element (dictionary of shorthand arguments) is returned here.
    - Edge cases:
        - If some keys in the group dict have value None and a replacement exists in Config._shorthands, those keys will be populated with the replacement values by Config.shorthands and thus will appear in the returned dict.
        - The returned dict may be the same object as the stored group dict (see Side Effects).

## Raises:
    KeyError: If the provided key is not present in Config.arg_groups (direct indexing: Config.arg_groups[key]).
    TypeError: If Config.arg_groups is not a subscriptable mapping or if the mapped value is not a dict-like object compatible with dict.items() (errors raised are the raw Python exceptions produced by those conditions).

## State Changes:
- Attributes READ:
    - Config.arg_groups (class-level): the mapping from group names to argument dicts is accessed.
    - Config._shorthands (class-level): indirectly read by Config.shorthands to resolve defaults for None values.
- Attributes WRITTEN / Mutated:
    - Config.arg_groups[key] (the dict corresponding to the requested group) may be mutated in-place:
        - Because get_arg_groups fetches the group dict and passes it to Config.shorthands with split=False, and because Config.shorthands assigns shorthand_args = kwargs when split=False, any in-place updates performed by Config.shorthands (for keys with value None that have replacements in Config._shorthands) will modify the original group dict stored in Config.arg_groups.

## Constraints:
- Preconditions:
    - Config.arg_groups must be a mapping (e.g., dict) and contain the requested key.
    - The value at Config.arg_groups[key] must be a dict-like object with .items() that yields (key, value) pairs (so Config.shorthands can iterate and possibly modify it).
    - Config._shorthands should be a mapping used by Config.shorthands when resolving None values (otherwise no defaults are applied).
- Postconditions:
    - The returned dict contains the shorthand-resolved key/value pairs for the requested group.
    - If any keys in the stored group had value None and a replacement existed in Config._shorthands, those keys will have been filled in in the stored group dict as well as in the returned dict.

## Side Effects:
- In-place mutation: Passing the stored group dict into Config.shorthands with split=False causes shorthand resolution to operate on the same dict object; as a result, Config.arg_groups[key] may be modified (populated with replacement/default values).
- No I/O, no network/external service calls.

### `src.ydata_profiling.config.Config.shorthands` · *method*

## Summary:
Resolve keys with None values in a provided kwargs mapping by replacing them with configured shorthand values from Config._shorthands; optionally remove those keys from the original kwargs (split behavior). This updates the kwargs mapping (by deletion or in-place replacement) and returns the shorthand mappings separately when requested.

## Description:
This utility resolves "shorthand" configuration values for keys present in a kwargs dictionary when their current value is None. It consults the class-level mapping Config._shorthands for replacement values.

Known callers and lifecycle:
- No direct callers are present in the provided context. Typical usage: invoked during configuration parsing or options normalization when assembling final configuration values from user-supplied kwargs and default/shorthand mappings (e.g., during profile/config object initialization or when merging CLI/API-supplied options with defaults).
- It's designed as a small reusable helper so shorthand-resolution logic is isolated from higher-level parsing/merging code.

Why this is a separate method:
- Encapsulates the specific policy for treating None values as "use shorthand if available".
- Keeps caller code simpler (caller doesn't need to know about the existence or shape of Config._shorthands).
- Allows sharing the same logic both when callers want shorthand values removed from kwargs (split=True) and when callers want kwargs updated in-place (split=False).

## Args:
    kwargs (dict):
        A mutable mapping of option names to values. The method examines kwargs.items() and may mutate kwargs in-place:
            - If split is True: keys with value None that have a mapping in Config._shorthands are removed from kwargs.
            - If split is False: kwargs is updated in-place for those keys (values replaced with the shorthand values).
        Caller should pass a dict-like object supporting .items(), item assignment, and key deletion.
    split (bool, optional): Defaults to True.
        - If True: return a new dict containing only the resolved shorthand entries, and return the (possibly reduced) original kwargs as the second tuple element.
        - If False: treat the provided kwargs as the shorthand result (the returned first element is the same dict object as kwargs, with in-place value replacements applied) and return an empty dict as the second element.

## Returns:
    Tuple[dict, dict]:
        - First element (shorthand_args):
            * If split is True: a new dict containing only keys that were present in kwargs with value None and that have an entry in Config._shorthands. Each such key maps to Config._shorthands[key].
            * If split is False: the same dict object as the kwargs argument (possibly with values replaced for keys that were None and present in Config._shorthands).
        - Second element:
            * If split is True: the original kwargs dict after removal of keys that were resolved via shorthand (those keys originally had value None and were present in Config._shorthands).
            * If split is False: an empty dict.

Edge-case return notes:
- If no keys match the condition (value is None and key in Config._shorthands), then:
    * If split True: returns ({}, kwargs) where kwargs is unchanged.
    * If split False: returns (kwargs, {}) where kwargs is unchanged.
- The function returns dict objects; when split is False the first returned dict is the exact same object passed as kwargs (identity must be preserved by implementers).

## Raises:
    - No explicit exceptions are raised by the code as written.
    - Potential runtime exceptions:
        * AttributeError: accessing Config._shorthands will raise AttributeError if Config exists but the class attribute _shorthands is not present.
        * Any exception raised by using kwargs (e.g., if kwargs is not a dict-like object and lacks .items(), or if item assignment/deletion is unsupported) will propagate (TypeError/AttributeError).

## State Changes:
    Attributes READ:
        - Config._shorthands (class-level mapping used as source of replacement values)
        - The provided kwargs mapping is read via kwargs.items().
    Attributes WRITTEN:
        - The provided kwargs mapping may be mutated:
            * If split is True: keys that match (value is None and key in Config._shorthands) are deleted from kwargs.
            * If split is False: keys that match are assigned the corresponding values from Config._shorthands (in-place replacement).
        - No class-level attributes on Config are modified by this method.

## Constraints:
    Preconditions:
        - kwargs must be a mutable mapping supporting .items(), key assignment, and key deletion (e.g., a regular dict).
        - Config._shorthands must be a mapping with keys comparable to the keys in kwargs (most commonly str keys). The method checks membership using "key in Config._shorthands".
    Postconditions:
        - For each key K originally in kwargs where kwargs[K] is None and K in Config._shorthands:
            * If split True: K will be absent from the returned second-element kwargs, and shorthand_args[K] == Config._shorthands[K].
            * If split False: the returned first-element dict (the same object as kwargs) will have kwargs[K] == Config._shorthands[K], and the returned second-element is {}.
        - No other keys are added to kwargs or removed except those that match the condition described above.

## Side Effects:
    - In-place mutation of the kwargs argument (either deletions or value replacements) as described above.
    - No I/O, logging, or external service calls.
    - No mutation of Config (class-level) state by this method.

Implementation notes / important details for reimplementation:
    - The method iterates over list(kwargs.items()) — this snapshot iteration allows deletion of keys from kwargs during iteration without raising a runtime error. Implementers must preserve this behavior (i.e., iterate over a static list/tuple of items rather than kwargs.items() live iterator) if they also delete keys during iteration.
    - When split is False, the code intentionally uses shorthand_args = kwargs to return the same object identity; callers may rely on this identity/aliasing behavior.

