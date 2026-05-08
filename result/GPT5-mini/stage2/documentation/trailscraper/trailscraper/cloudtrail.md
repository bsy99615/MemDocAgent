# `cloudtrail.py`

## `trailscraper.cloudtrail.Record` · *class*

## Summary:
Represents a single CloudTrail event and provides conversion helpers to produce an IAM Statement that approximates the permission (Action objects and Resource ARNs) implied by the event.

## Description:
Record models a minimal CloudTrail event: event_source, event_name, associated resource ARNs, optional assumed role ARN, event timestamp, and the raw event payload. Typical callers create a Record for each parsed CloudTrail JSON event (e.g., in log-parsing code or an event iterator) and call to_statement() to obtain a trailscraper.iam.Statement that approximates the IAM permission used.

Responsibility boundary:
- Record holds event metadata and maps that metadata to IAM constructs (Action and Statement) using internal mapping rules.
- Record does not validate ARNs, normalize timestamps, or fetch additional context; it only transforms stored attributes into a trailscraper.iam.Statement when requested.

## State:
Attributes initialized by __init__:

- event_source (str)
  - Example: "s3.amazonaws.com", "apigateway.amazonaws.com".
  - No validation is performed; callers should supply the CloudTrail event's eventSource string.

- event_name (str)
  - Example: "PutObject", "GetCallerIdentity".
  - The raw API/operation name from CloudTrail; used to derive an IAM action-name string.

- resource_arns (list[str])
  - Default: ["*"] if the caller passes None.
  - Used directly when building Statement Resource; to_statement() will sort this list for the resulting Statement.
  - Must be an iterable of hashable strings for Record hashing to work.

- assumed_role_arn (str | None)
  - Default: None.
  - Stored for callers to inspect; not used directly by to_statement().

- event_time (datetime.datetime | None)
  - Default: None.
  - Stored and participates in equality/hash semantics. No automatic timezone normalization is performed.

- raw_source (Any)
  - Default: None.
  - The original raw event payload (e.g., parsed JSON dict). Kept for callers that need details beyond the fields Record stores.

Class invariants:
- resource_arns is never None after construction (it becomes the passed value or ["*"]).
- Equality and hashing depend on event_source, event_name, event_time, resource_arns, and assumed_role_arn.

## Lifecycle:
Creation:
- Call:
  Record(event_source: str, event_name: str, resource_arns: Optional[List[str]] = None, assumed_role_arn: Optional[str] = None, event_time: Optional[datetime.datetime] = None, raw_source: Optional[Any] = None)
- resource_arns defaults to ["*"] if None.

Usage:
- Typical flow:
  1. Construct Record from parsed CloudTrail event.
  2. Inspect fields as needed.
  3. Call to_statement() to get a trailscraper.iam.Statement (or None for specific ignored events).
  4. Aggregate resulting Statements into a policy builder.

- Details of to_statement():
  - If the event is sts.amazonaws.com:GetCallerIdentity, to_statement() returns None (ignored).
  - If event_source is apigateway.amazonaws.com, to_statement() delegates to _to_api_gateway_statement(), which uses operation_definition("apigateway", event_name) to determine HTTP method and request URI and builds an API Gateway ARN pattern for the Statement Resource.
  - Otherwise, to_statement():
    1. Calls _source_to_iam_prefix() to derive an IAM service prefix (string). This maps some AWS event_source strings to a different IAM prefix (e.g., monitoring.amazonaws.com -> "cloudwatch"); otherwise it takes the portion before the first '.'.
    2. Calls _event_name_to_iam_action() which returns an IAM-style action-name string. This method applies service-specific special-case mappings (numerous s3 mappings exist) and a sequence of regex-based normalizations (e.g., strip version suffixes or map DeleteBucketCors -> PutBucketCORS).
    3. Constructs an Action by calling Action(prefix, action_name). The resulting Action object (not a plain string) is placed inside the Statement Action list.
    4. Note: Action objects are expected to expose json_repr() (or equivalent) that returns a stable string representation (commonly "prefix:action"). That canonicalization is the responsibility of the Action class, not Record.
    5. Constructs and returns a Statement(Effect="Allow", Action=[the Action instance], Resource=[sorted resource_arns]).

Destruction:
- No cleanup required. Record is a plain data object.

## Method Map:
Mermaid flowchart showing method dependencies and typical invocation order:

graph LR
  A[Record.__init__] --> B[Record.to_statement]
  B --> C{special-case?}
  C -->|sts:GetCallerIdentity| D[return None]
  C -->|apigateway.amazonaws.com| E[_to_api_gateway_statement]
  E --> F[operation_definition("apigateway", event_name)]
  F --> G[derive http_method, requestUri]
  G --> H[build Statement(Action=Action("apigateway", http_method), Resource=API_ARN_pattern)]
  C -->|other services| I[_source_to_iam_prefix]
  C -->|other services| J[_event_name_to_iam_action]
  I --> K[prefix (str)]
  J --> L[action_name (str)]
  K & L --> M[Action(prefix, action_name)]
  M --> N[Action.json_repr -> "prefix:action"]
  M --> O[Statement(Effect="Allow", Action=[Action], Resource=sorted(resource_arns))]

Notes:
- _event_name_to_iam_action returns a normalized action-name string only; the Action class is responsible for the canonical representation.
- _to_api_gateway_statement constructs an Action for API Gateway using the HTTP method as the action name.

## Raises:
- __init__:
  - Performs no explicit validation and thus does not raise intentionally. However:
    - If resource_arns is a non-iterable or contains unhashable items, later operations (hashing via __hash__ or sorted() in to_statement()) may raise TypeError.
- to_statement / _to_api_gateway_statement:
  - operation_definition("apigateway", event_name) may raise exceptions if the operation is unknown or the definitions are missing; such errors will propagate.
  - The Action and Statement constructors (from trailscraper.iam) may raise if they validate inputs; those exceptions propagate.

## Example:
Basic S3 event conversion:

rec = Record("s3.amazonaws.com", "PutObject", resource_arns=["arn:aws:s3:::my-bucket/*"], event_time=datetime.datetime.utcnow())
stmt = rec.to_statement()
# stmt is a trailscraper.iam.Statement with Effect="Allow", Action list containing an Action object whose json_repr() returns "s3:PutObject", and Resource ["arn:aws:s3:::my-bucket/*"]

API Gateway example:

rec_api = Record("apigateway.amazonaws.com", "GetRestApi", resource_arns=["*"])
stmt_api = rec_api.to_statement()
# _to_api_gateway_statement() queries operation_definition("apigateway","GetRestApi") to get the http method and requestUri,
# builds an API Gateway ARN pattern, and returns a Statement with Action [Action("apigateway", http_method)].
# Each Action object exposes json_repr() returning a stable "apigateway:http_method" string.

Guidance:
- Always check for None from to_statement() before using the returned value.
- Normalize event_time and validate resource_arns prior to constructing Record if deterministic hashing or strict ARN validity is required.

### `trailscraper.cloudtrail.Record.__init__` · *method*

## Summary:
Initializes a Record instance to represent a single CloudTrail event by storing event metadata (source, name, timestamp, resource ARNs, assumed role) and the original raw payload; sets the object's fields used by later conversion helpers (e.g., to_statement()).

## Description:
Known callers and lifecycle stage:
- Constructed by log-parsing code or an event iterator for each parsed CloudTrail JSON event.
- Typical usage: create Record(...) during event parsing, then call Record.to_statement() to convert the stored metadata into a trailscraper.iam.Statement.
- Called early in the Record lifecycle (creation stage) and expected to be cheap and side-effect free.

Why this is a separate method:
- Separates simple data capture from later transformation logic (to_statement and other helpers). Keeping construction minimal avoids coupling parsing/validation with conversion rules and makes Records lightweight, immutable-in-practice data holders after construction.

## Args:
    event_source (str):
        - The CloudTrail eventSource string (e.g., "s3.amazonaws.com", "apigateway.amazonaws.com").
        - No validation is performed; callers should pass the eventSource from the CloudTrail event.
    event_name (str):
        - The CloudTrail eventName (e.g., "PutObject", "GetCallerIdentity").
        - No validation is performed; used later to derive an IAM action name.
    resource_arns (Optional[Iterable[str]], optional):
        - Iterable of resource ARN strings associated with the event (e.g., ["arn:aws:s3:::my-bucket/*"]).
        - If the provided value is falsy (None, empty list, empty string, etc.), the constructor sets self.resource_arns to ["*"].
        - No type enforcement is performed here; the iterable should contain hashable strings for later sorting/hashing to succeed.
        - Default: None (which becomes ["*"]).
    assumed_role_arn (Optional[str], optional):
        - ARN of an assumed role present in the event, if any. Stored as-is.
        - Default: None.
    event_time (Optional[datetime.datetime], optional):
        - Timestamp of the event. Stored as-is (no timezone normalization).
        - Default: None.
    raw_source (Optional[Any], optional):
        - The original raw event payload (commonly a parsed JSON dict). Stored for callers that need details beyond the top-level fields.
        - Default: None.

## Returns:
    None
    - The constructor always returns None (standard __init__ behavior). No value is returned to the caller.

## Raises:
    - The __init__ method itself performs no explicit validation and therefore does not intentionally raise exceptions.
    - Note: Passing a non-iterable for resource_arns will not raise during assignment here, but later operations that assume resource_arns is iterable (e.g., sorted(self.resource_arns) in to_statement(), or hashing) may raise TypeError. If resource_arns contains unhashable members, hashing or set operations elsewhere may raise TypeError.

## State Changes:
    Attributes READ:
        - None of self.<attr> fields are read by this method (it only assigns attributes).
    Attributes WRITTEN:
        - self.event_source: set to the provided event_source value.
        - self.event_name: set to the provided event_name value.
        - self.raw_source: set to the provided raw_source value.
        - self.event_time: set to the provided event_time value.
        - self.resource_arns: set to resource_arns if it is truthy; otherwise set to ["*"].
        - self.assumed_role_arn: set to the provided assumed_role_arn value.

## Constraints:
    Preconditions:
        - The method imposes no runtime type checks. For correct downstream behavior:
            * event_source and event_name should be strings representing the CloudTrail fields.
            * resource_arns, if provided, should be an iterable of hashable strings (e.g., list[str]) to allow sorting and hashing later.
    Postconditions:
        - After return:
            * self.event_source == event_source
            * self.event_name == event_name
            * self.raw_source == raw_source
            * self.event_time == event_time
            * self.assumed_role_arn == assumed_role_arn
            * self.resource_arns is never None; it equals the original resource_arns if that value was truthy, otherwise equals ["*"].

## Side Effects:
    - No I/O, no logging, and no network or external service calls.
    - Does not mutate objects outside of self (it assigns references provided via parameters).
    - Because raw_source is stored by reference, if the caller subsequently mutates that object, the Record.raw_source will observe those mutations.

### `trailscraper.cloudtrail.Record.__repr__` · *method*

## Summary:
Returns a developer-facing string snapshot of the Record composed from four attributes (event_source, event_name, event_time, resource_arns) without modifying the object.

## Description:
This dunder method is the object's canonical textual representation used by Python's repr() built-in and by any tooling that requests an object's representation (debuggers, interactive shells, container reprs, logging when repr() is used). It centralizes a concise, human-oriented view of a Record for inspection and diagnostics.

The method exists as __repr__ so that the representation is produced automatically wherever Python requests an object's representation; keeping the formatting here prevents duplication and ensures consistency across the codebase.

## Args:
None.

## Returns:
str: A single-line string built by an f-string concatenation. The exact format produced by this implementation is:
    Record(event_source={event_source} event_name={event_name} event_time={event_time} resource_arns={resource_arns})
where each brace expression is replaced by the corresponding attribute's formatted value (Python calls the attribute's __format__ with an empty format spec, which falls back to __str__ if appropriate).

Notes and edge cases:
- The method does not truncate or escape attribute contents; if an attribute's string contains newlines or very large content, those characters appear verbatim in the returned string.
- The method makes no guarantee that the representation is unambiguous or that eval(repr(obj)) will reconstruct the object.

## Raises:
- AttributeError: If the instance lacks any of the attributes accessed (event_source, event_name, event_time, resource_arns), attribute access during f-string evaluation will raise AttributeError which propagates out of this method.
- Any exception raised while formatting an attribute (for example, if an attribute's __format__ or __str__ raises) will propagate.

## State Changes:
Attributes READ:
- self.event_source
- self.event_name
- self.event_time
- self.resource_arns

Attributes WRITTEN:
- None. The method performs no assignments and does not mutate self.

## Constraints:
Preconditions:
- The Record instance must have accessible attributes named event_source, event_name, event_time, and resource_arns.
- Attribute accessors (properties) should not raise side-effect exceptions unless callers intend to handle them.

Postconditions:
- The Record instance remains unchanged after the call.
- The returned string reflects the attribute values at the time of the call.

## Side Effects:
- This method itself performs no I/O, network calls, or external mutations.
- Any observable side effects can only originate from attribute accessors or their formatting methods invoked during evaluation (those side effects are not caused by this method's implementation).

### `trailscraper.cloudtrail.Record.__eq__` · *method*

## Summary:
Compares this Record to another object for value equality by checking that both are Record instances and that the event_source, event_name, event_time, resource_arns, and assumed_role_arn attributes are pairwise equal; returns True if all match, otherwise False.

## Description:
Known callers:
    - Record.__ne__: delegates inequality to this method (returns the negation).
    - Any external code that uses the '==' operator to compare Record instances (e.g., for assertions, deduplication, filtering, or membership checks).

Context:
    - Invoked whenever two Record objects are compared with the equality operator (==). Typical lifecycle usage is during event-processing pipelines or tests when distinct CloudTrail event Records must be compared or deduplicated.

Rationale for being a separate method:
    - Centralizes the definition of Record equality so that __ne__, the equality operator, and any external comparisons use a single, consistent implementation.
    - Keeps equality logic decoupled from hashing and representation logic while ensuring compatibility with __hash__ (both use the same attribute set).

## Args:
    other (any): The object being compared to this Record. No specific type is required; the method will defensively check type.

## Returns:
    bool: 
        - True if and only if:
            * other is an instance of the same class as self, and
            * self.event_source == other.event_source, and
            * self.event_name == other.event_name, and
            * self.event_time == other.event_time, and
            * self.resource_arns == other.resource_arns, and
            * self.assumed_role_arn == other.assumed_role_arn.
        - False in all other cases (including when other is a different type).

Edge-case return notes:
    - If both records have event_time set to None, they compare equal for that field.
    - resource_arns comparison is a list equality check: it is order-sensitive and requires identical list contents and order to be considered equal.

## Raises:
    None: The method performs only attribute comparisons and an isinstance check; it does not raise exceptions itself.

## State Changes:
    Attributes READ:
        - self.event_source
        - self.event_name
        - self.event_time
        - self.resource_arns
        - self.assumed_role_arn
    Attributes WRITTEN:
        - None (this method does not modify self or other).

## Constraints:
    Preconditions:
        - The Record instance's comparison attributes (event_source, event_name, event_time, resource_arns, assumed_role_arn) exist (they are set in the constructor). No further invariants are required before calling.
    Postconditions:
        - No mutation of self or other occurs.
        - The return value correctly reflects equality based on the five listed attributes.
        - Equality semantics are consistent with __hash__: when two Record instances are equal per this method, they will produce the same hash because __hash__ hashes the same attributes (with resource_arns converted to a tuple).

## Side Effects:
    - None: the method has no I/O, does not call external services, and does not mutate objects other than reading attributes on self and other.

### `trailscraper.cloudtrail.Record.__hash__` · *method*

## Summary:
Compute and return an integer hash derived from the Record's key identifying fields (event source, event name, event time, resource ARNs, and assumed role ARN) so the Record can be used in hashed collections without changing object state.

## Description:
This method produces a deterministic hash value computed from a 5-tuple of instance attributes:
(event_source, event_name, event_time, tuple(resource_arns), assumed_role_arn).

Known callers and invocation context:
- The method is invoked implicitly by the Python runtime when:
  - hash(record) is called,
  - a Record instance is inserted into a set,
  - a Record instance is used as a dictionary key,
  - any other hashed-collection operation that requires an object's hash.
- Typical pipeline usage: Records created during CloudTrail processing are often deduplicated or grouped using sets or dicts; __hash__ is used during those deduplication/indexing steps.
- There are no explicit direct calls to __hash__ within this module; usage is via Python's hashing machinery.

Why this logic is a separate method:
- Python requires a __hash__ method that is consistent with __eq__; isolating the hashing logic ensures that equality and hashing remain aligned and centralizes the tuple-construction and attribute ordering.

## Args:
- None (other than self).

## Returns:
- int: A Python integer hash for the tuple:
  (self.event_source, self.event_name, self.event_time, tuple(self.resource_arns), self.assumed_role_arn).
- Notes:
  - The returned integer is computed by Python's built-in hash algorithm and may vary across interpreter versions and processes (hash randomization for strings may change values between runs).
  - If an element in the tuple is unhashable, the method will not return a value; instead a TypeError is raised.

## Raises:
- TypeError:
  - If any element of the tuple is unhashable.
  - Common triggers:
    - An element of self.resource_arns is itself a mutable/unhashable object (e.g., a list or dict).
    - self.resource_arns is None (tuple(None) raises TypeError).
    - Any other attribute used in the tuple is assigned an unhashable object.

## State Changes:
Attributes READ:
- self.event_source
- self.event_name
- self.event_time
- self.resource_arns
- self.assumed_role_arn

Attributes WRITTEN:
- None. The method does not modify the Record instance.

## Constraints:
Preconditions:
- The Record instance should have the attributes initialized (Record.__init__ sets defaults):
  - event_source: expected to be a string (initialized from constructor argument).
  - event_name: expected to be a string.
  - event_time: typically a datetime.datetime or None.
  - resource_arns: typically a list (Record.__init__ uses ["*"] if None) — before calling __hash__, this must be an iterable of hashable items (commonly strings).
  - assumed_role_arn: string or None.
- Avoid mutating the attributes involved in hashing while the object is stored in a hashed collection.

Postconditions:
- Returns an int and leaves the Record instance unchanged.
- If two Record instances are equal according to Record.__eq__ (their five identifying attributes compare equal), they will produce equal hash values.

## Side Effects:
- None: no I/O, logging, external service calls, or mutations of objects outside self occur.

## Warnings and best practices:
- Do not mutate any of the attributes used in the hash (particularly elements of resource_arns) after the Record has been placed into a set or used as a dict key. Changing those attributes will not update previously computed hash placements and can lead to lost lookups or corrupted set/dict invariants.
- Ensure resource_arns is an iterable of hashable items before calling hash(); if it is None or contains unhashable elements, __hash__ will raise TypeError.

## Small usage note (plain-text example):
- Typical hash use: inserting a Record into a set or using it as a dict key triggers this method implicitly.
- Mutation hazard: if record.resource_arns is later changed from a list of strings to a list containing a list, future hashing will raise TypeError and previously stored hashed positions may be invalidated.

### `trailscraper.cloudtrail.Record.__ne__` · *method*

## Summary:
Returns True when the provided object is not value-equal to this Record (negates the equality comparison) and does not modify the Record's state.

## Description:
Known callers:
    - Any code that uses the '!=' operator to compare two objects; typical call sites include event-processing pipelines, tests, set/deduplication checks, or any conditional that checks inequality between Records.
    - Indirectly used wherever Python invokes rich comparison for inequality.

Context:
    - Invoked at comparison time when two objects are compared with '!='. In typical lifecycle usage this happens during filtering, deduplication, assertions in tests, or conditional checks while processing CloudTrail event Records.

Why this is a separate method:
    - Provides explicit inequality semantics by delegating to the canonical equality implementation (__eq__) and returning its logical negation. This centralizes equality logic in one place (__eq__) while ensuring Python's inequality operator behaves consistently.
    - Keeps the inequality implementation minimal and ensures consistent behavior with __eq__ and __hash__.

## Args:
    other (any): The object to compare against this Record. Any type is allowed; the method will rely on the semantics of __eq__ to determine equality and then negate it.

## Returns:
    bool:
        - True if this Record is not equal to other according to the Record.__eq__ logic.
        - False if Record.__eq__(other) returns True (i.e., the objects are value-equal).
        - Edge cases:
            * If other is not an instance of Record (or the same class), Record.__eq__ returns False; therefore __ne__ will return True for non-Record objects.
            * If __eq__ returns a truthy/falsey value (per Python's boolean coercion), __ne__ returns the logical negation of that value.

## Raises:
    None: The implementation performs no operations that raise exceptions on its own; it simply delegates to __eq__ and negates the result. Any exception would originate from __eq__ if __eq__ were to raise (but __eq__ in this class does not raise).

## State Changes:
    Attributes READ:
        - self.event_source (read transitively when __eq__ is invoked)
        - self.event_name (read transitively when __eq__ is invoked)
        - self.event_time (read transitively when __eq__ is invoked)
        - self.resource_arns (read transitively when __eq__ is invoked)
        - self.assumed_role_arn (read transitively when __eq__ is invoked)
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Record instance should be properly initialized (the attributes listed above exist). No other preconditions are required.
    Postconditions:
        - The method does not mutate self or other.
        - The return value is the boolean negation of what Record.__eq__(other) would return, preserving consistency between equality, inequality, and hashing behavior in the class.

## Side Effects:
    - None: no I/O, no external service calls, and no mutation of objects outside self. The method's only effect is to compute and return a boolean value.

### `trailscraper.cloudtrail.Record._source_to_iam_prefix` · *method*

## Summary:
Return the IAM service prefix corresponding to this record's event_source (affects how Actions are constructed for IAM Statements).

## Description:
Known callers:
- Record.to_statement — invoked when converting a CloudTrail Record into an IAM Statement during policy extraction/policy-generation from CloudTrail events.

Context / lifecycle:
- This method is called as part of the step that translates a parsed CloudTrail event (Record) into an IAM Statement (i.e., when building Action(service_prefix, action_name) instances).
- It isolates the mapping logic from event parsing and statement construction so that special-case mappings and the default extraction rule are centralized and easy to modify.

Rationale for being a separate method:
- Several services require explicit, non-trivial mappings from the CloudTrail event_source (full AWS service domain) to the IAM service prefix used in action ARNs. Keeping the mapping here avoids duplicating the special-case table and makes the to_statement method concise and easier to test.

## Args:
None.

## Returns:
str
- The IAM service prefix to use when constructing an Action for this Record.
- Typical possible return values include:
  - Special-case mappings (exact matches): 'cloudwatch', 'appstream', 'lex', 'mechanicalturk', 'dynamodb', 'tag'
  - Default extracted prefix: the substring of self.event_source before the first '.' (for example, 's3' from 's3.amazonaws.com', 'ec2' from 'ec2.amazonaws.com').
- Edge-case returns:
  - If self.event_source is an empty string, the method returns an empty string.
  - If self.event_source contains no '.', the entire string is returned.

## Raises:
- AttributeError: If self.event_source is None or otherwise does not have a .split method (e.g., not a str). This arises because the implementation calls self.event_source.split('.') directly.
- No other exceptions are raised by this method itself.

## State Changes:
Attributes READ:
- self.event_source

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- Preferably, self.event_source should be a non-empty str holding the CloudTrail event source domain (e.g., 's3.amazonaws.com', 'monitoring.amazonaws.com'). The Record.__init__ sets event_source, but callers should ensure it is a valid string before invoking this method.

Postconditions:
- The method returns a deterministic str derived solely from the current value of self.event_source and does not modify any object state.

## Side Effects:
- None. The method does not perform I/O, network calls, or mutate objects outside of reading self.event_source.

### `trailscraper.cloudtrail.Record._event_name_to_iam_action` · *method*

## Summary:
Convert the CloudTrail event_name into a canonical IAM action string (service-aware mapping plus deterministic regex normalization). This is a pure computation that returns the derived action name; it does not modify any Record attributes.

## Description:
This method computes the IAM-style action corresponding to the CloudTrail event recorded in the Record instance. It is invoked by Record.to_statement() when constructing an IAM Statement from a CloudTrail record to determine the Action part of the Statement.

Why this logic is isolated:
- There are many service-specific special-case mappings (notably for S3 and KMS) that are clearer and easier to maintain in one place.
- A deterministic sequence of normalizing regex substitutions must be applied in order; keeping them together prevents subtle ordering bugs.
- Downstream code expects a single canonical string representing the required permission.

Known callers and lifecycle:
- Record.to_statement(): used when converting a Record into an IAM Statement (the method supplies the Action argument to Statement).
- Typical pipeline stage: mapping parsed CloudTrail events into IAM Actions/Statements during audit, policy-generation, or analysis steps.

## Args:
    None (method uses attributes on self)

    Implicit inputs (required on self):
    - self.event_name (str): raw event name from CloudTrail (e.g., "CompleteMultipartUpload", "HeadObject", "ReEncrypt"). Must be a string for successful processing.
    - self.event_source (str): AWS event source identifier (e.g., "s3.amazonaws.com", "kms.amazonaws.com"). Used to look up service-specific special-case mappings. If missing, service-specific mappings are not applied.

## Returns:
    str: the mapped and normalized IAM action name.
    - If a service-specific mapping exists for the tuple (self.event_source, self.event_name), the mapped string is returned verbatim (examples below).
    - Otherwise, the method returns the result of applying three regex substitutions (in order) to self.event_name.
    - If no mapping or substitution alters the input, the original self.event_name (as a str) is returned.
    - Examples of possible return values:
        - "PutObject" (e.g., s3: CompleteMultipartUpload -> PutObject)
        - "GetObject" (e.g., s3: HeadObject -> GetObject)
        - "ListAllMyBuckets" (s3: ListBuckets)
        - "PutBucketCORS" (result of DeleteBucketCors -> PutBucketCORS substitution)
        - "ReEncrypt*" (kms: ReEncrypt -> ReEncrypt*)

## Service-specific special-case mappings (exact table used)
- For event_source == "s3.amazonaws.com", the following event_name -> mapped action pairs are used:
    - CompleteMultipartUpload -> PutObject
    - CopyObject -> PutObject
    - CreateMultipartUpload -> PutObject
    - DeleteBucketAnalyticsConfiguration -> PutAnalyticsConfiguration
    - DeleteBucketEncryption -> PutEncryptionConfiguration
    - DeleteBucketInventoryConfiguration -> PutInventoryConfiguration
    - DeleteBucketLifecycle -> PutLifecycleConfiguration
    - DeleteBucketMetricsConfiguration -> PutMetricsConfiguration
    - DeleteBucketReplication -> DeleteReplicationConfiguration
    - DeleteBucketTagging -> PutBucketTagging
    - DeleteObjects -> DeleteObject
    - GetBucketAccelerateConfiguration -> GetAccelerateConfiguration
    - GetBucketAnalyticsConfiguration -> GetAnalyticsConfiguration
    - GetBucketEncryption -> GetEncryptionConfiguration
    - GetBucketInventoryConfiguration -> GetInventoryConfiguration
    - GetBucketLifecycle -> GetLifecycleConfiguration
    - GetBucketLifecycleConfiguration -> GetLifecycleConfiguration
    - GetBucketMetricsConfiguration -> GetMetricsConfiguration
    - GetBucketNotificationConfiguration -> GetBucketNotification
    - GetBucketReplication -> GetReplicationConfiguration
    - HeadBucket -> ListBucket
    - HeadObject -> GetObject
    - ListBucketAnalyticsConfigurations -> GetAnalyticsConfiguration
    - ListBucketInventoryConfigurations -> GetInventoryConfiguration
    - ListBucketMetricsConfigurations -> GetMetricsConfiguration
    - ListBuckets -> ListAllMyBuckets
    - ListMultipartUploads -> ListBucketMultipartUploads
    - ListObjectVersions -> ListBucketVersions
    - ListObjects -> ListBucket
    - ListObjectsV2 -> ListBucket
    - ListParts -> ListMultipartUploadParts
    - PutBucketAccelerateConfiguration -> PutAccelerateConfiguration
    - PutBucketAnalyticsConfiguration -> PutAnalyticsConfiguration
    - PutBucketEncryption -> PutEncryptionConfiguration
    - PutBucketInventoryConfiguration -> PutInventoryConfiguration
    - PutBucketLifecycle -> PutLifecycleConfiguration
    - PutBucketLifecycleConfiguration -> PutLifecycleConfiguration
    - PutBucketMetricsConfiguration -> PutMetricsConfiguration
    - PutBucketNotificationConfiguration -> PutBucketNotification
    - PutBucketReplication -> DeleteReplicationConfiguration
    - UploadPart -> PutObject
    - UploadPartCopy -> PutObject

- For event_source == "kms.amazonaws.com":
    - ReEncrypt -> ReEncrypt*  (approximation; comment in source notes this is not precise)

If self.event_source is not present in the special-case table, no service-specific mapping is applied.

## Ordered regex normalization steps (exact sequence)
After applying any special-case mapping lookup (above), the method applies the following substitutions to the current value (this is done in order; each step receives the result of the previous step):

1. Replace the exact substring "DeleteBucketCors" with "PutBucketCORS".
   - Pattern: r"DeleteBucketCors"
   - Replacement: "PutBucketCORS"

2. Remove trailing version/number suffixes from names that match letters followed by digits, 'v', or underscores:
   - Pattern: r"([a-zA-Z]+)[0-9v_]+$"
   - Replacement: r"\1"
   - Example: "Action20150331" -> "Action"

3. Replace suffix "Cors" with uppercase "CORS":
   - Pattern: r"Cors$"
   - Replacement: "CORS"
   - This runs after the version-stripping substitution, so "PutBucketCors" -> "PutBucketCORS".

These substitutions are applied using a left-to-right functional pipeline: start with the (possibly mapped) event name, then apply substitution 1, then 2, then 3, returning the final string.

## Raises:
    - AttributeError: If self.event_name or self.event_source attributes do not exist on the Record instance (attribute access fails).
    - TypeError: If self.event_name (or the intermediate value) is not a string (for example, None or another type). The regex substitution functions call Pattern.sub on the value, which will raise TypeError if the subject is not a str/bytes-like object.
    - re.error: If any of the regex patterns provided in the code were invalid, the regex engine could raise re.error during compilation. With the current hard-coded patterns this is not expected.

## State Changes:
    Attributes READ:
        - self.event_name
        - self.event_source
    Attributes WRITTEN:
        - None (method does not modify self or external state)

## Constraints:
    Preconditions:
        - self.event_name must be present and ideally be a non-empty str for meaningful output.
        - self.event_source should be present as a str if service-specific mappings are to be applied.
    Postconditions:
        - The return value is a str containing the service-mapped and normalized IAM action name.
        - The Record instance remains unchanged.

## Side Effects:
    - None. The method performs in-memory computation only and does not perform I/O, network calls, or mutate external objects.

## Implementation notes (for reimplementation)
- Use the exact special_cases mapping table above.
- Implement the normalization as a pipeline: map -> apply regex substitution 1 -> apply substitution 2 -> apply substitution 3.
- Ensure proper defensive behavior: callers should ensure self.event_name is a str; if not, be prepared to handle TypeError or check types before calling.

### `trailscraper.cloudtrail.Record._to_api_gateway_statement` · *method*

## Summary:
Convert this CloudTrail record into a single IAM Statement that grants the API Gateway HTTP method captured by the record against the corresponding API Gateway resource ARN; does not mutate the record.

## Description:
This method looks up the API Gateway operation model for this record's event name, extracts the HTTP method and request URI, normalizes path-parameter placeholders into wildcards, and returns a Statement describing an Allow for that method on the constructed API Gateway ARN.

Known callers and invocation context:
- No direct callers were discovered statically in the repository. Conceptually this method is intended to be called by the record-to-policy conversion step of the policy-inference pipeline (i.e., any code that converts trailscraper.cloudtrail.Record instances into trailscraper.iam.Statement objects to build or infer IAM policies). It is executed during the stage where a single CloudTrail record is translated into one or more IAM statements describing required permissions.

Why this logic is encapsulated:
- The mapping from CloudTrail event -> API Gateway operation -> IAM Action + Resource ARN is API-Gateway-specific and requires use of boto service definitions. Encapsulating it keeps service-specific ARN/Action construction localized, makes testing easier, and avoids duplicating the operation_definition lookup and request-URI normalization logic elsewhere.

## Args:
This is an instance method and takes only self.
- self.event_name (str, required): Name of the API Gateway operation (the CloudTrail eventName) used to lookup the operation model via operation_definition("apigateway", event_name). Must be a non-empty string that exists as a key in the botocore service definition for apigateway.

## Returns:
- trailscraper.iam.Statement
    - Effect: "Allow"
    - Action: a list containing a single trailscraper.iam.Action constructed as Action("apigateway", http_method) where http_method is taken from op_def['http']['method'].
    - Resource: a single-item list containing the ARN string formatted as:
      arn:aws:apigateway:{region}::{resource_path}
      - region is currently the literal "*" (the code comments indicate region should be derived from requestParameters in the future).
      - resource_path is derived from the operation model's requestUri (op_def['http']['requestUri']) with path-parameter placeholders replaced by "*" (see edge-case notes).
    - Normal behavior: returns the Statement described above.
    - There is no case where this method returns None; on error it raises/propagates exceptions.

## Raises:
This method does not catch exceptions from its callees; callers must handle or propagate them. Possible exceptions include:
- KeyError
    - Condition: operation_definition returned a mapping that does not contain the expected 'http' key or 'requestUri'/'method' keys, or operation_definition itself raised KeyError when the requested operationname is missing.
- IndexError / pkg_resources.* exceptions / OSError / FileNotFoundError / json.JSONDecodeError
    - Condition: propagated from operation_definition(servicename, operationname) when the botocore service definition file cannot be found, opened, or parsed.
- Any exception raised by the Action or Statement constructors (rare; these constructors do not validate inputs strongly in this codebase but will surface TypeError if passed inappropriate types).
- re.error is extremely unlikely because the pattern is a fixed, valid regex; it would only occur if the regex literal in the source were changed to an invalid expression.

## State Changes:
- Attributes READ:
    - self.event_name
- Attributes WRITTEN:
    - None (the Record instance is not mutated)

## Constraints:
Preconditions:
- self.event_name must be a valid, non-empty string corresponding to an API Gateway operation name present in the botocore service definition for "apigateway".
- The parsed operation model for the event must contain an 'http' mapping with string keys 'method' and 'requestUri'. If these are absent the method raises KeyError.

Postconditions:
- If the call returns normally:
    - A trailscraper.iam.Statement instance is returned with Effect "Allow", a single Action entry for the API Gateway HTTP method, and a single Resource entry with the constructed ARN string.
    - The Record object (self) remains unchanged.

## Side Effects:
- Indirect filesystem I/O via operation_definition("apigateway", self.event_name): this call opens and reads a botocore service-definition JSON file. Any I/O or JSON parsing errors from operation_definition will propagate out of this method.
- No network I/O, no writes, and no mutations to objects outside self (the method only constructs and returns new Action and Statement instances).

## Implementation details and edge cases (important for correct reimplementation):
- operation_definition("apigateway", event_name) is used to obtain the operation model dictionary. This helper performs filesystem reads and may raise IndexError, OSError, FileNotFoundError, json.JSONDecodeError, or KeyError if the operation is missing.
- Expected operation model shape:
    - op_def['http']['method'] -> string representing the HTTP method (e.g., "GET", "POST").
    - op_def['http']['requestUri'] -> string representing the API Gateway request URI, potentially containing path-parameter placeholders like /users/{userId}/items.
- Path-parameter normalization:
    - The implementation replaces placeholders that match the regex r"{[a-zA-Z_]+}" with "*" (a single star). This pattern matches braces containing only ASCII letters and underscores; placeholders containing digits, hyphens, or other characters will not match and therefore will remain unchanged in the resource_path.
    - Example: "/v1/users/{userId}/items" -> "/v1/users/*/items"
- ARN format produced:
    - The resource string uses the API Gateway ARN pattern used by this codebase: arn:aws:apigateway:{region}::{resource_path}
    - region is currently "*", producing arn:aws:apigateway:*::{resource_path}. The caller may expect a more specific region extraction in future changes.
- Action object:
    - The Action instance is constructed with prefix "apigateway" and action equal to the http_method value from the operation model. The Action class stores these two strings without validation; callers that rely on canonical string forms should call Action.json_repr() if needed.
- If deterministic ordering or merging of statements is required by callers, be aware that this method returns a single-statement result; callers may need to merge it with other statements using Statement.merge() if combining is necessary.

## Example (conceptual):
- Given a record with event_name "GetResource" whose operation_definition yields:
    op_def['http']['method'] == "GET"
    op_def['http']['requestUri'] == "/restapis/{restapi_id}/resources/{resource_id}/methods"
  The returned Statement will be equivalent to:
    Effect: "Allow"
    Action: [ Action("apigateway", "GET") ]
    Resource: [ "arn:aws:apigateway:*::/restapis/*/resources/*/methods" ]

### `trailscraper.cloudtrail.Record.to_statement` · *method*

## Summary:
Convert this Record into an IAM Statement object representing the permission implied by the CloudTrail event, or return None for the identity-check GetCallerIdentity event; the call does not modify the Record.

## Description:
This method maps a parsed CloudTrail Record into a trailscraper.iam.Statement describing the Effect, Action(s), and Resource(s) that correspond to the event.

Known/typical callers and context:
- Policy-building or analysis code that aggregates Statements from parsed CloudTrail events to produce an IAM policy or to reason about required permissions.
- Pipeline stage immediately after a Record is parsed/deserialized from CloudTrail where events are converted to Statement objects for merging/deduplication.

Why this is a separate method:
- The conversion contains concise but distinct decision logic and special cases (e.g., sts:GetCallerIdentity suppression and API Gateway mapping) that are conceptually a single responsibility. Isolating this mapping makes tests, special-case maintenance, and policy-merging logic simpler and avoids inlining these rules at call sites.

## Args:
- None (method is invoked as an instance method: self is a trailscraper.cloudtrail.Record)

## Returns:
- type: trailscraper.iam.Statement or None
- Possible return values and conditions:
    - None: returned when the event is the identity-check sts:GetCallerIdentity (event_source == "sts.amazonaws.com" and event_name == "GetCallerIdentity"). This event conveys identity information and is intentionally not represented as an Allow statement.
    - Statement: returned in two paths:
        1. API Gateway special-case: if event_source == "apigateway.amazonaws.com", returns the Statement produced by self._to_api_gateway_statement(). That Statement contains Effect="Allow", Action set to an Action for API Gateway (method), and Resource set to a generated ARN pattern (region is wildcarded in the current implementation).
        2. Default path: returns Statement(Effect="Allow", Action=[Action(prefix, action_name)], Resource=sorted(self.resource_arns))
            - prefix comes from self._source_to_iam_prefix()
            - action_name comes from self._event_name_to_iam_action()
            - resource list is created by sorting the existing self.resource_arns into a new list (sorted lexicographically)

- Edge cases:
    - If resource_arns contains non-comparable types, sorted(...) may raise TypeError which will propagate.
    - If helpers invoked (e.g., operation_definition called inside the API Gateway helper) raise exceptions, those exceptions will propagate to the caller.

## Raises:
- The method does not explicitly raise exceptions itself.
- Exceptions may propagate from helpers or constructors invoked:
    - TypeError from sorted(self.resource_arns) if elements are not mutually comparable.
    - Any exception raised by self._to_api_gateway_statement(), self._source_to_iam_prefix(), self._event_name_to_iam_action(), Action(), or Statement() (for example KeyError from operation_definition used by the API Gateway helper) will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.event_source
    - self.event_name
    - self.resource_arns
    - (indirectly read by helpers) any attributes accessed by:
        - self._source_to_iam_prefix() (reads self.event_source)
        - self._event_name_to_iam_action() (reads self.event_name)
        - self._to_api_gateway_statement() (reads self.event_name and uses operation_definition("apigateway", self.event_name))
- Attributes WRITTEN:
    - None — this method does not mutate self or other external objects.

## Constraints:
- Preconditions:
    - self.event_source must be a string (methods like .split('.') and equality comparisons assume string).
    - self.event_name must be a string (helpers apply regex and string transformations).
    - self.resource_arns should be an iterable of strings (sorting and use as ARN strings assume string elements). Note: Record.__init__ defaults resource_arns to ["*"] if not provided.
- Postconditions:
    - If return is None, the Record is unchanged and the caller should interpret that the event should not produce an Allow statement.
    - If return is a Statement, the returned Statement has:
        - Effect == "Allow"
        - Action == list with a single trailscraper.iam.Action instance (API Gateway path produces Action with API method)
        - Resource == list of strings (default path: sorted copy of self.resource_arns; API Gateway path: single generated ARN string)

## Side Effects:
- No I/O is performed by this method directly.
- The method constructs and returns new objects (Action and Statement) but does not mutate external state.
- Any side effects originate from helper calls (for example operation_definition inside the API Gateway helper) and will surface as propagated exceptions if those helpers perform I/O or raise.

## `trailscraper.cloudtrail.LogFile` · *class*

## Summary:
Represents a single CloudTrail log file on disk (typically a .json.gz file) and provides helpers to inspect its filename-derived timestamp, validate filename format, load and parse contained event records, and check whether the file contains events within a given timeframe.

## Description:
Instantiate this class when you have a path to a CloudTrail delivery file (the gzipped JSON files delivered by CloudTrail to S3 or copied locally). Typical usages:
- During a directory or S3 listing, create one LogFile per file path and filter files by has_valid_filename() before processing.
- Call records() to load the gzip JSON payload and convert the "Records" array into parsed Record objects (via parse_records).
- Use timestamp() or contains_events_for_timeframe() to include/exclude files when scanning by date/time windows.

This class encapsulates file-path-oriented logic (filename parsing) and local file loading. It intentionally separates filename/timestamp extraction from the record-parsing step (the latter is delegated to parse_records), so callers can cheaply inspect filenames without opening files.

Known callers/factories:
- Higher-level log discovery and processing code that enumerates CloudTrail log files and then needs to load/parse them.
- Pipelines that call parse_records(records) for downstream Record/Statement extraction.

## State:
- _path (str)
    - Description: Filesystem path to the gzipped CloudTrail log file.
    - Expected shape: Path to a gzip-compressed JSON file, commonly with a filename matching the CloudTrail naming convention (examples: ACCOUNTID_CloudTrail_region_YYYYMMDDTHHMMSSZ_RANDOM.json.gz).
    - Constraints: Not validated at construction time; can be any string. Methods that parse or open the file may raise exceptions if _path does not refer to an existing or readable gzip JSON file.
- Class invariants:
    - _path is treated as an opaque string identifying the file location. No methods modify _path.
    - Methods may assume a conventional CloudTrail filename layout only when called; callers should check has_valid_filename() before relying on timestamp() correctness.

## Lifecycle:
- Creation:
    - Instantiate by calling LogFile(path).
    - Required argument:
        - path (str): local filesystem path to a .json.gz file. No automatic type enforcement is performed.
    - __init__ does not open files or validate the path.
- Typical usage order (recommended):
    1. Create LogFile(path).
    2. Optionally call has_valid_filename() to skip non-conforming filenames cheaply.
    3. Optionally call timestamp() to obtain the file's timestamp (derived from the filename).
    4. Call records() to open, decompress, parse JSON, and convert the contained "Records" array into typed Record objects.
    5. Use contains_events_for_timeframe(from_date, to_date) if selecting files by window; this calls timestamp() internally.
- Destruction / cleanup:
    - No special cleanup is required. records() uses context-managed gzip.open, so file handles are closed automatically.
    - There is no close(), context-manager, or persistent resources owned by LogFile beyond the path string.

## Method Map:
flowchart TD
    A[LogFile(path)] --> B{has_valid_filename()}
    B -->|True| C[timestamp() —> datetime (UTC, minute precision)]
    B -->|False| D[timestamp() may raise on malformed filename]
    C --> E[contains_events_for_timeframe(from, to)]
    F[records()] --> G[open gzip file] --> H[json.load -> obj] --> I[obj["Records"]] --> J[parse_records(records) -> list[Record]]
    G -. IO/OSError caught .-> K[returns empty list]
    H -. JSONDecodeError propagates .-> L[exception]
    J -. parse_records exceptions may propagate .-> L

## Methods / Behavior (summary)
- filename() -> str
    - Returns the basename of _path (os.path.split semantics).
- has_valid_filename() -> match|None
    - Uses a precompiled regex to match CloudTrail-style filenames.
    - Returns the regex match object (truthy) when the filename matches the expected pattern, otherwise returns None (falsy). Callers should wrap with bool(...) if a boolean is required.
    - Pattern details: expects something like "<digits>_CloudTrail_<region-or-account>_<timestamp-part>_<rand>.json.gz".
- timestamp() -> datetime.datetime (tz-aware, pytz.UTC)
    - Extracts the timestamp token from the filename (the 4th underscore-separated segment, index 3) and parses year, month, day, hour and minute.
    - Construction: year = dstr[:4], month = dstr[4:6], day = dstr[6:8], hour = dstr[9:11], minute = dstr[11:13]. Returns a datetime with tzinfo=pytz.utc.
    - Notes: This implementation ignores seconds and any timezone suffix inside the token. It expects the timestamp token to contain a 'T' or similar character at index 8 that is skipped when reading hour/minute (for example: "20190101T120000Z"); the code uses fixed slicing, so format deviations will cause parsing errors.
- records() -> list[Record]
    - Opens the file at _path with gzip.open(..., 'rt'), loads JSON with json.load, extracts json_data['Records'], and returns parse_records(records) (see parse_records documentation: returns list[Record]).
    - Error handling:
        - IOError or OSError while opening/reading the gzip file are caught; a warning is logged and an empty list is returned.
        - JSONDecodeError from json.load is not caught here and will propagate to the caller.
        - parse_records may raise exceptions (see parse_records docs); those exceptions are not caught and will propagate.
- contains_events_for_timeframe(from_date, to_date) -> bool
    - Returns True if timestamp() is within [from_date, to_date + 1 hour].
    - Uses timestamp() (tz-aware UTC) and a one-hour inclusive extension on the to_date side.

## Raises:
The class methods can raise exceptions under the following conditions; callers should handle these as appropriate.

- __init__(path)
    - No explicit exceptions are raised by the constructor itself.
    - If the caller passes a non-string path, subsequent method calls that treat _path as a path (e.g., os.path.split, gzip.open) may raise TypeError or ValueError when used.

- filename()
    - Does not raise by itself beyond what os.path.split would raise on non-conforming types (e.g., TypeError if _path is not a str/bytes).

- has_valid_filename()
    - No exceptions; returns None when not matching.

- timestamp()
    - IndexError: if filename().split('_') has fewer than 4 segments (accessing index 3 fails).
    - ValueError: if the substring slices cannot be converted to int (non-digit characters in expected numeric positions).
    - Any exceptions above will propagate to the caller.
    - Recommendation: call has_valid_filename() before calling timestamp() when file naming is uncertain.

- records()
    - Catches IOError and OSError (e.g., file not found, permission denied, gzip errors at open) — logs a warning and returns an empty list instead of raising.
    - json.JSONDecodeError (a subclass of ValueError): if file contents are not valid JSON, this will propagate (not caught).
    - KeyError: if the top-level JSON object lacks the 'Records' key, a KeyError will propagate.
    - Exceptions raised by parse_records (e.g., ValueError for malformed timestamps within records or other parsing errors) will propagate — parse_records documents these propagation behaviors.

- contains_events_for_timeframe(from_date, to_date)
    - Propagates exceptions from timestamp() as described above.
    - TypeErrors may occur if from_date/to_date are not comparable to the timestamp (i.e., not datetime-like). Callers must supply datetime.datetime instances (preferably timezone-aware or compatible with the returned UTC datetime).

## Edge cases and notes:
- Filename dependence: timestamp() uses fixed string-slice offsets. If Amazon changes the filename timestamp format, parsing will fail. Use has_valid_filename() to mitigate this risk.
- Minute precision: seconds in the filename's timestamp token are ignored by timestamp(); the returned datetime only encodes to the minute level.
- Timezone handling: timestamp() returns a datetime with tzinfo=pytz.utc. When comparing to caller-supplied datetimes, prefer timezone-aware datetimes or normalize to UTC to avoid ambiguity and TypeError when comparing naive vs aware datetimes.
- records() swallowing IO errors: I/O-related failures return an empty list (and log a warning). This design favors resilience during bulk processing but callers who need to treat missing/unreadable files as errors should detect and handle empty results accordingly.
- parse_records interactions: parse_records will return list[Record] for well-formed Records arrays and may raise errors that propagate — callers should wrap records() in try/except when input may contain malformed events they wish to ignore or handle specially.

## Example:
Create a LogFile and process events defensively.

1) Inspect filename and timestamp
    lf = LogFile("/path/to/123456789012_CloudTrail_us-east-1_20190101T120000Z_abcd.json.gz")
    if not lf.has_valid_filename():
        skip this file
    ts = lf.timestamp()  # datetime.datetime(2019, 1, 1, 12, 0, tzinfo=pytz.UTC)

2) Load and parse records (handle parsing exceptions)
    try:
        recs = lf.records()  # returns list[Record] from parse_records
    except json.JSONDecodeError:
        handle_invalid_json()
    except Exception as e:
        handle_parse_error(e)

3) Timeframe filtering
    from_dt = datetime.datetime(2019, 1, 1, 0, 0, tzinfo=pytz.utc)
    to_dt = datetime.datetime(2019, 1, 1, 23, 59, tzinfo=pytz.utc)
    if lf.contains_events_for_timeframe(from_dt, to_dt):
        process lf.records()

## Implementation notes for reimplementation:
- filename() should be implemented with os.path.split(self._path)[-1].
- has_valid_filename() should compile and use the existing regex: r"[0-9]+_CloudTrail_[a-z0-9-]+_[0-9TZ]+_[a-zA-Z0-9]+\.json\.gz" and return the match object (not coerced to bool) to preserve original behavior.
- timestamp() must split filename by '_' and parse the 4th segment (index 3). Use fixed slicing as above to obtain year, month, day, hour and minute, convert to ints, assemble a datetime and attach pytz.utc tzinfo.
- records() must open the gzip file with gzip.open(self._path, 'rt'), json.load the file object, extract json_data['Records'], and return parse_records(records). Catch IOError and OSError, log a warning and return [] on those I/O issues. Do not catch JSONDecodeError or parse_records exceptions (allow propagation).
- contains_events_for_timeframe(from_date, to_date) should call timestamp() and check whether from_date <= timestamp <= to_date + datetime.timedelta(hours=1).

### `trailscraper.cloudtrail.LogFile.__init__` · *method*

## Summary:
Stores the provided filesystem path on the new LogFile instance as an opaque identifier for a CloudTrail gzipped JSON file (sets the object's _path attribute).

## Description:
- Known callers and contexts:
    - Directory- or S3-listing stages that enumerate CloudTrail delivery files and instantiate one LogFile per discovered path.
    - Higher-level log discovery and processing pipelines that prepare LogFile objects before calling methods such as has_valid_filename(), timestamp(), records(), or contains_events_for_timeframe().
    - Any factory or code that needs a lightweight, filename-focused wrapper around a file path prior to performing I/O or parsing.

- Lifecycle stage:
    - Invoked at object creation time to initialize a LogFile before any filename inspection or file access. Typical use: create LogFile(path) during discovery, then call filename()/has_valid_filename()/timestamp() or records().

- Why this is a separate method:
    - Keeps construction cheap and side-effect free so callers can inspect filenames or filter files without opening or validating the file contents.
    - Separates the responsibility of storing the file identifier from heavier actions (decompressing, JSON parsing, record conversion), improving testability and enabling lazy I/O.

## Args:
    path (str): Filesystem path (string) identifying the target CloudTrail file (commonly a ".json.gz" file path).
        - Allowed values: Any object can be passed technically, but typical and expected usage is a string path.
        - Constraints: The constructor does not validate the format or existence of the path. If callers require path validation, they must perform it separately before or after construction.

## Returns:
    None: As with all Python __init__ methods, the constructor does not return a value; it initializes the instance in-place.

## Raises:
    - None explicitly: The constructor contains a simple assignment and does not raise exceptions in normal usage.
    - Note: Passing highly unusual objects (e.g., objects that raise on attribute assignment) could raise in unusual environments, but standard use with a string does not raise here. Subsequent method calls that treat _path as a file path may raise TypeError, OSError, FileNotFoundError, JSONDecodeError, etc., when those methods attempt I/O or parsing.

## State Changes:
- Attributes READ:
    - None (the constructor does not access any existing self attributes)

- Attributes WRITTEN:
    - self._path — set to the provided path argument (stored verbatim, no transformation, no validation)

## Constraints:
- Preconditions:
    - None strictly required by this method. For correct downstream behavior, callers should ensure:
        - path is a string representing a filesystem path (recommended).
        - If downstream methods will be called, the path should point to a readable gzip-compressed JSON file matching CloudTrail naming conventions (optional but typical).

- Postconditions:
    - After return, self._path exists on the instance and equals the passed-in path argument (identity/equals depending on type).
    - The instance is ready for filename-only operations (e.g., os.path.split(self._path) or regex matches) and for later I/O operations invoked by other methods.

## Side Effects:
    - None external: does not perform I/O, logging, or external service calls.
    - No mutation of objects outside self (only self._path is assigned).

### `trailscraper.cloudtrail.LogFile.timestamp` · *method*

## Summary:
Extract the timestamp token from the file's basename, parse year/month/day/hour/minute from fixed character positions, and return a timezone-aware datetime in UTC; the method does not modify the object's state.

## Description:
This method performs the following steps:
1. Calls self.filename() to obtain the file basename.
2. Splits the basename on underscores and selects the fourth segment (index 3) as the timestamp token.
3. Parses fixed-position slices of that token into integers for year, month, day, hour and minute, constructs a datetime from those fields, and returns it with tzinfo set to pytz.utc.

Known callers and usage context:
    - LogFile.contains_events_for_timeframe(from_date, to_date): uses this method to decide whether a log file's timestamp places it inside a requested time window.
    - File-selection, sorting, or filtering routines that operate on sets of LogFile objects and need a normalized datetime derived from the filename rather than filesystem metadata.

Why this is a separate method:
    - Encapsulates brittle, index-based parsing rules for CloudTrail-style filenames so other code can reuse a single, testable implementation rather than duplicating slice logic. Centralization reduces subtle bugs arising from inconsistent parsing.

## Args:
    None

## Returns:
    datetime.datetime
        - A timezone-aware datetime (tzinfo=pytz.utc) representing the parsed year, month, day, hour and minute from the filename.
        - Seconds and microseconds are zero.
        - Example:
            - Basename: "123_CloudTrail_acct_20200101T1230_ABCDEF.json.gz"
            - Timestamp token: "20200101T1230"
            - Returned value: datetime.datetime(2020, 1, 1, 12, 30, tzinfo=pytz.utc)

## Raises:
    IndexError
        - Trigger: filename().split('_') returns fewer than four segments so accessing index 3 fails.
        - This indicates a malformed basename that does not follow the expected underscore-separated layout.

    ValueError
        - Trigger: any of the fixed slices cannot be converted to an integer (for example, empty strings when the token is too short or non-digit characters present) or when datetime(...) rejects the numeric values (e.g., month == 0 or an out-of-range day).
        - Note: If the timestamp token is shorter than the expected length, Python slicing yields shorter strings (not an IndexError); int('') or int of a non-digit-containing slice raises ValueError.

    Any exception raised by self.filename()
        - Any exception propagated from filename() (for example, if self._path is missing) will bubble up unchanged.

## Implementation details (exact slicing and mapping):
    - The method executes the equivalent of:
        dstr = self.filename().split('_')[3]
        year   = int(dstr[0:4])
        month  = int(dstr[4:6])
        day    = int(dstr[6:8])
        hour   = int(dstr[9:11])
        minute = int(dstr[11:13])
        return datetime.datetime(year, month, day, hour, minute).replace(tzinfo=pytz.utc)
    - Requirements for the token:
        - The code expects the token to contain digits at positions:
            0..3 = year (4 chars)
            4..5 = month (2 chars)
            6..7 = day (2 chars)
            8     = delimiter (commonly 'T') — skipped by the slices
            9..10= hour (2 chars)
            11..12= minute (2 chars)
        - The minimal length for the token to satisfy the slices is 13 characters (indices 0 through 12). If shorter, slices return shorter strings and integer conversion will fail (ValueError).
        - Any characters after index 12 (for example a trailing 'Z') are ignored by these slices.

## State Changes:
    Attributes READ:
        - self._path (indirectly) via self.filename()
        - Any attributes accessed by filename()

    Attributes WRITTEN:
        - None (the method is pure with respect to object state)

## Constraints:
    Preconditions:
        - self.filename() must return a basename with at least four underscore-separated segments and the fourth segment must contain a timestamp token matching the compact layout described above.
        - It is recommended (but not required) to call LogFile.has_valid_filename() first; its regex validates the overall CloudTrail filename pattern and reduces the chance of ValueError/IndexError.

    Postconditions:
        - On success, returns a datetime.datetime with tzinfo=pytz.utc corresponding to the parsed timestamp; self remains unchanged.
        - On failure, an IndexError or ValueError is raised (or filename()'s exception propagates); no object mutation occurs.

## Side Effects:
    - No I/O, no network access.
    - No mutation of external objects or files.
    - Only CPU-bound string processing and datetime construction; exceptions propagate to the caller.

### `trailscraper.cloudtrail.LogFile.filename` · *method*

## Summary:
Return the final path component (basename) extracted from the object's stored path value without mutating the object.

## Description:
Extracts and returns the filename portion of the LogFile instance's internal _path using the platform-aware path split behavior provided by the runtime.

Known callers within this module:
- timestamp() — calls this method to obtain the filename and parse the timestamp embedded in it.
- has_valid_filename() — calls this method to validate the filename against the CloudTrail filename pattern.
- contains_events_for_timeframe() — indirectly invokes this method via timestamp() when checking whether the file's timestamp lies within a timeframe.

Lifecycle context: used during pre-processing and validation steps to derive metadata (filename and timestamp) before the file content is inspected or processed. Implemented as a separate method because the basename extraction is reused by multiple other methods and centralizing it simplifies maintenance and testing.

## Args:
This method takes no arguments.

## Returns:
str or bytes: The basename (final path component) of self._path.
- The concrete return type matches the input type accepted by os.path.split:
  - If self._path is a str or a PathLike that resolves to str, a str is returned (the typical case).
  - If self._path is bytes or a PathLike that resolves to bytes, bytes is returned.
- Example typical value: "123456789012_CloudTrail_us-east-1_20210101T0000Z_abcdef.json.gz"
- Edge-case returns:
  - '' (empty string) when self._path is an empty string or when it ends with a path separator (e.g., '/some/dir/').
  - b'' (empty bytes) when self._path is empty bytes or ends with a separator in bytes form.

## Raises:
This method does not explicitly raise exceptions itself, but may propagate exceptions from the underlying os.path.split or path conversion:
- TypeError: if self._path is None or another unsupported type (e.g., a custom object without a __fspath__ and not str/bytes), a TypeError will be raised by the path handling functions.
- Any other exceptions raised by os.path.split or os.fspath (in unusual environments) will propagate to the caller.

## State Changes:
Attributes READ:
- self._path

Attributes WRITTEN:
- None

## Constraints:
Preconditions:
- self._path must be set before calling; for predictable behavior it should be either a str, bytes, or an object implementing the PathLike protocol (i.e., providing __fspath__).

Postconditions:
- The method returns the basename of self._path and leaves the LogFile instance unchanged.

## Side Effects:
- None. The method performs no I/O or network activity and does not mutate external objects.

## Implementation notes (for reimplementation):
- Use the system path utilities to obtain the final path component (in Python: os.path.split(self._path)[-1]) so platform-specific path separators are respected.
- Do not attempt to open or validate the file's existence; this method is purely for path-to-filename extraction.

### `trailscraper.cloudtrail.LogFile.has_valid_filename` · *method*

## Summary:
Checks whether the LogFile's filename matches the expected CloudTrail delivery filename pattern and returns the regex match (does not modify the object).

## Description:
This method validates the textual filename (derived from self._path) against a compiled regular expression that encodes the typical CloudTrail S3-delivered log filename format:
[digits]_CloudTrail_[a-z0-9-]+_[0-9TZ]+_[a-zA-Z0-9]+.json.gz

Known callers:
- No direct callers were found in the provided memory snapshot. Typical usage is by upstream file-enumeration, filtering, or ingestion logic that iterates over candidate LogFile instances and keeps only files whose names match the CloudTrail delivery pattern before attempting to parse or timestamp them (for example, before calling records() or timestamp()).

Why this is a separate method:
- Encapsulates the filename validation logic behind a single, testable method so callers do not need to duplicate the regex.
- Keeps parsing/IO methods focused on reading content; validation is a cheap, independent check done prior to I/O.

## Args:
    None

## Returns:
    re.Match or None
    - If the filename begins with a sequence that satisfies the regex, a re.Match object is returned (truthy).
    - If the filename does not match the pattern, None is returned (falsy).
    - Typical consumer pattern: bool(logfile.has_valid_filename()) to obtain a boolean validity result.
    - Note: the code uses re.match (which anchors at the start) but the regex is not explicitly anchored at the end with $, so valid-looking prefixes followed by additional trailing characters after ".json.gz" will still produce a match.

## Raises:
    - No exceptions are raised explicitly by this method.
    - Any exception raised by filename() (for example, TypeError if self._path is not a string-like object, or other unexpected errors from os.path.split) will propagate through has_valid_filename.

## State Changes:
    Attributes READ:
        - self._path (indirectly, via self.filename())
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self._path must be present and be a path-like string so that filename() can return a string filename.
    Postconditions:
        - The method does not mutate the LogFile instance.
        - The return value is either a re.Match object (indicating a pattern match) or None (no match).

## Side Effects:
    - None: this method performs no I/O, does not call external services, and does not modify objects other than reading self._path via filename().

## Example:
    - Given a filename "123456789012_CloudTrail_us-east-1_20160101T0000Z_ABCDEFGHIJKL.json.gz",
      has_valid_filename() will return a re.Match object (truthy).
    - Given "not-a-cloudtrail-file.txt", has_valid_filename() will return None (falsy).

### `trailscraper.cloudtrail.LogFile.records` · *method*

## Summary:
Load and parse the CloudTrail event records stored in this log file path, returning the list of successfully parsed Record objects (no change to the LogFile instance).

## Description:
- Known callers and call context:
    - Higher-level CloudTrail log-processing code that iterates over LogFile instances to read events from on-disk CloudTrail delivery files (for example: a pipeline step that enumerates files, constructs LogFile(path) objects, and then calls records() to obtain typed Record objects for downstream analysis).
    - Typical lifecycle stage: "discover compressed CloudTrail JSON files -> instantiate LogFile(path) -> call records() to read and parse events -> pass returned list[Record] to statement-extraction/aggregation components."

- Why this is a dedicated method:
    - Encapsulates file I/O, decompression, JSON decoding, extraction of the top-level 'Records' array, and delegation to parse_records in one place. Keeping this logic in the LogFile class centralizes file-format-specific handling (including error handling for unreadable files) instead of scattering gzip/json handling across call sites.

## Args:
    None

## Returns:
    list[Record]
    - On successful read and parse: returns the list produced by parse_records(json_data['Records']), i.e., a list of successfully parsed Record instances in the same relative order as their input entries.
    - On file I/O errors (e.g., unreadable file, missing file, permission error): returns an empty list.
    - Note: If the JSON payload is syntactically invalid or missing the 'Records' key, or if parse_records raises, those exceptions are propagated (see Raises).

## Raises:
    - json.JSONDecodeError (subclass of ValueError):
        * Raised when the file contents are not valid JSON; json.load will raise this and it is not caught by this method.
    - KeyError:
        * Raised when the top-level parsed JSON does not contain the 'Records' key (access json_data['Records']).
    - Any exception raised by parse_records:
        * parse_records may raise TypeError, ValueError, AttributeError, or other exceptions when individual records are malformed; such exceptions propagate out of this method.
    - The following are NOT raised (they are handled internally by this method):
        * IOError / OSError (including FileNotFoundError): these are caught; the method logs a warning and returns an empty list.

## State Changes:
- Attributes READ:
    - self._path (str): the filesystem path to the gzip-compressed CloudTrail JSON file is read to open the file.
- Attributes WRITTEN:
    - None. The method does not modify any attributes of self.

## Constraints:
- Preconditions:
    - self._path must be set to a filesystem path pointing to a gzip-compressed file containing a top-level JSON object with a 'Records' key whose value is an iterable of record objects (typical CloudTrail payload).
    - Caller should be prepared to handle exceptions outlined in Raises when input data or record parsing is malformed.
- Postconditions:
    - If the file is successfully opened, contains valid JSON, and parse_records returns normally, the method returns the parse_records result and leaves self unchanged.
    - If opening the file raises an IOError/OSError (permission issue, missing file, unreadable), the method logs a warning and returns an empty list; self remains unchanged.

## Side Effects:
- I/O:
    - Opens and reads from the filesystem at self._path using gzip.open(..., 'rt') and passes the file handle to json.load.
- Logging:
    - Emits a debug log at method start: "Loading %s" with self._path.
    - If an IOError/OSError occurs while opening/reading the file, logs a warning: "Could not load %s: %s" with (self._path, error) and returns [].
- External calls:
    - Delegates per-record parsing to parse_records(json_data['Records']), which may itself perform logging. No network or persistent external side effects are performed by this method.

### `trailscraper.cloudtrail.LogFile.contains_events_for_timeframe` · *method*

## Summary:
Determines whether this LogFile's timestamp falls within the inclusive interval [from_date, to_date + 1 hour]. The method only inspects the object's filename-derived timestamp and does not modify the object's state.

## Description:
This method checks whether the timestamp parsed from the LogFile's filename lies between two given datetimes: greater than or equal to from_date, and less than or equal to to_date extended by one hour. The one-hour extension on to_date ensures files whose timestamps fall up to one hour after the requested end time are considered (useful for hourly-rolled CloudTrail files that may contain events falling shortly after the nominal period end).

Known callers and lifecycle context:
- There are no explicit callers inside this class definition. Typical usage is in higher-level filtering logic that enumerates LogFile instances (for example, scanning S3 or a local directory) and filters them to the time window of interest before loading or parsing records via LogFile.records().
- It is intended to be used as a cheap pre-check to avoid opening and parsing files whose timestamps are outside the requested timeframe.

Why this is a separate method:
- The check encapsulates the domain-specific rule (inclusive lower bound and an inclusive upper bound extended by one hour) and centralizes filename timestamp interpretation usage so callers do not need to parse filenames or duplicate the +1 hour logic elsewhere.

## Args:
    from_date (datetime.datetime): Lower bound (inclusive). Must be comparable to the LogFile timestamp (see Preconditions). Typically timezone-aware (UTC) to match timestamp().
    to_date (datetime.datetime): Upper bound (the method will compare against to_date + 1 hour). Must be comparable to the LogFile timestamp (see Preconditions). Typically timezone-aware (UTC).

## Returns:
    bool: True if from_date <= self.timestamp() <= to_date + datetime.timedelta(hours=1); otherwise False.
    - Edge cases:
        - If from_date > to_date, the method will still perform the comparison and will usually return False unless the timestamp lies in the small interval between from_date and to_date+1h.
        - No special sentinel values are returned; boolean only.

## Raises:
    - IndexError: Propagated when self.timestamp() attempts to extract the expected filename segment but the filename does not contain enough '_'-separated parts (e.g., filename().split('_')[3] fails).
    - ValueError: Propagated when timestamp parsing fails converting filename substrings to integers.
    - TypeError: Can occur when comparing timezone-aware and timezone-naive datetimes (Python raises TypeError for such comparisons). Because self.timestamp() returns a timezone-aware datetime (tzinfo=pytz.utc), from_date and to_date should usually also be timezone-aware to avoid this error.

## State Changes:
    Attributes READ:
        - self._path (indirectly): accessed via self.filename(), which uses os.path.split(self._path)[-1].
        - Any transient values computed by self.filename() and self.timestamp(), including the parsed filename string.
    Attributes WRITTEN:
        - None — this method does not mutate any attributes on self.

## Constraints:
    Preconditions:
        - self.filename() must follow the naming convention expected by timestamp() so that timestamp() can parse the date portion. If the filename is malformed, timestamp() will raise IndexError/ValueError.
        - from_date and to_date must be datetimes comparable with the value returned by self.timestamp(). Because timestamp() returns a tz-aware datetime with tzinfo=pytz.utc, callers should pass tz-aware datetimes (preferably in UTC).
    Postconditions:
        - No mutation of the LogFile object.
        - The method returns a boolean indicating whether the filename-parsed timestamp falls within the inclusive interval [from_date, to_date + 1 hour].

## Side Effects:
    - None: the method performs no I/O, no file access, and does not call external services. It only reads the object's path/filename and performs in-memory datetime comparisons.

## `trailscraper.cloudtrail._resource_arns` · *function*

## Summary:
Return a list of ARN values extracted from the 'resources' array of a single CloudTrail event record.

## Description:
This small helper inspects a parsed CloudTrail JSON record (a mapping/dict-like object), looks up the optional 'resources' field, and collects the value of the 'ARN' key from each resource entry that contains that key. It is intended for use during event parsing/normalization when callers need the resource ARNs referenced by an event for analysis, policy mapping, or logging.

Known callers and call context:
- No direct callers were visible in the provided file excerpt. Typical callers are functions that parse or normalize CloudTrail events and need to:
  - extract resource identifiers to build IAM Statements or Actions,
  - filter events by affected resources,
  - enrich events with resource metadata.
- Typical trigger: called after a CloudTrail log event has been parsed into a dict and the caller wants a simple list of resource ARNs present in that event.

Why this logic is a separate function:
- Encapsulates the single responsibility of extracting ARNs from the record so higher-level code stays focused on orchestration.
- Centralizes any future changes to extraction rules (case normalization, validation, deduplication) in one place.

## Args:
    json_record (Mapping[str, Any]):
        A mapping-like object representing a parsed CloudTrail event record.
        - The function uses json_record.get('resources', []), so json_record must implement .get.
        - Expected (but not enforced) shape when present:
            resources: iterable of mapping-like objects (e.g., dict) where each mapping may contain an 'ARN' key.

## Returns:
    list:
        A list of values taken verbatim from resource['ARN'] for each resource entry where the 'ARN' key is present.
        - If the record lacks a 'resources' key, returns an empty list [].
        - If the record has "resources": [] (empty list), returns [].
        - If the record has "resources": None (explicitly set to None), the function will attempt to iterate None and raise TypeError (see Raises).
        - The function does not coerce or validate ARN strings; returned values may be None or non-string if present in the record.
        - Order of elements matches the order of entries in the 'resources' iterable; duplicates are preserved.

## Raises:
    AttributeError:
        If json_record is None or does not implement .get, attempting json_record.get(...) will raise AttributeError.

    TypeError:
        - If the value of json_record.get('resources', []) is not iterable (for example, None or an integer), attempting to iterate it in the list comprehension will raise TypeError.
        - If a resource entry contains the substring/key check ('ARN' in resource) returning True (e.g., resource is a string containing the substring 'ARN'), but the entry does not support indexing by key (so resource['ARN'] is invalid), Python will raise TypeError when attempting resource['ARN'].

Notes:
    - The function never raises KeyError for missing 'ARN' keys because it checks "'ARN' in resource" before indexing resource['ARN'].
    - The function does not perform any validation or normalization of ARN values.

## Constraints:
Preconditions:
    - Caller should pass a mapping-like json_record (e.g., dict). If callers cannot guarantee this, they should validate or guard before calling.

Postconditions:
    - The input json_record is not mutated.
    - A list (possibly empty) is returned that contains every resource['ARN'] value from resources entries where 'ARN' is a key.

## Side Effects:
    - None. The function performs no I/O and does not mutate inputs or global state.

## Control Flow:
flowchart TD
    A[Start: receive json_record] --> B{json_record has .get?}
    B -- No --> C[AttributeError when calling .get]
    B -- Yes --> D[resources = json_record.get('resources', [])]
    D --> E{resources is iterable?}
    E -- No --> F[TypeError during iteration]
    E -- Yes --> G[Iterate over each resource in resources]
    G --> H{'ARN' in resource?}
    H -- No --> I[Skip this resource]
    H -- Yes --> J[Append resource['ARN'] to result list]
    J --> G
    G --> K[Return list of collected ARNs]

## Examples:
1) Typical usage
    Input:
        {
            "eventTime": "2023-01-01T12:00:00Z",
            "resources": [
                {"ARN": "arn:aws:s3:::example-bucket"},
                {"ARN": "arn:aws:iam::123456789012:role/ExampleRole"},
                {"Type": "AWS::S3::Bucket", "ARN": "arn:aws:s3:::another-bucket"}
            ]
        }
    Output:
        ["arn:aws:s3:::example-bucket",
         "arn:aws:iam::123456789012:role/ExampleRole",
         "arn:aws:s3:::another-bucket"]

2) No resources key present
    Input:
        {"eventName": "CreateUser", "userIdentity": {...}}
    Output:
        []

3) resources explicitly None (error case)
    Input:
        {"resources": None}
    Behavior:
        TypeError raised when attempting to iterate None.

4) Defensive calling pattern
    If json_record may be malformed, validate before calling:
        if not isinstance(json_record, dict):
            handle_error(...)
        arns = _resource_arns(json_record)

## `trailscraper.cloudtrail._assumed_role_arn` · *function*

## Summary:
Return the ARN of the IAM role that was assumed in a CloudTrail event record, or None when the record is present but does not represent an assumed-role session.

## Description:
This small helper fetches the assumed-role ARN from a single CloudTrail event record (a dict parsed from JSON). It performs a direct indexing of the top-level 'userIdentity' and, when that mapping has a 'type' equal to the literal 'AssumedRole' and contains 'sessionContext', returns the value found at sessionContext -> sessionIssuer -> arn.

Known callers within the codebase:
    - No direct callers were discovered in a repository-wide scan. The function is a private helper inside trailscraper.cloudtrail and is intended for use by higher-level record-processing functions in that module when extracting the identity that initiated an event.

Why this logic is extracted:
    - Responsibility boundary: centralizes the specific extraction semantics and conditional checks for identifying an assumed-role ARN in CloudTrail userIdentity objects. Callers can rely on this single location to obtain the ARN or None and handle malformed records consistently.

## Args:
    json_record (dict): A mapping representing a parsed CloudTrail event record. The function expects to index json_record['userIdentity'] directly; it does not defensively check for the top-level key before indexing.

    Interdependencies:
    - If json_record['userIdentity']['type'] == 'AssumedRole', the function expects json_record['userIdentity'] to also contain 'sessionContext' and that nested mapping to contain 'sessionIssuer' with an 'arn' key. Missing nested keys result in exceptions (see Raises).

## Returns:
    str or None:
    - str: The ARN string located at json_record['userIdentity']['sessionContext']['sessionIssuer']['arn'] when all of the following are true:
        * json_record is subscriptable and contains 'userIdentity';
        * user_identity contains a 'type' key whose value is the literal 'AssumedRole';
        * user_identity contains the 'sessionContext' key.
      Note that even when 'sessionContext' exists, a missing 'sessionIssuer' or missing 'arn' within it will raise KeyError instead of returning None.
    - None: returned when user_identity exists and either:
        * 'type' is not present or does not equal 'AssumedRole', or
        * 'sessionContext' is not present in user_identity.
    - The function never mutates the input.

## Raises:
    KeyError:
        - If the top-level 'userIdentity' key is missing from json_record (accessing json_record['userIdentity'] raises KeyError).
        - If 'type' check passes ('AssumedRole') but the nested path sessionContext -> sessionIssuer -> 'arn' lacks keys (accessing ['sessionIssuer'] or ['arn'] will raise KeyError).
    TypeError:
        - If json_record is not subscriptable (e.g., None or a non-mapping), attempting json_record['userIdentity'] will raise TypeError.
    Note: The function does not catch these exceptions; callers must handle them if records may be malformed.

## Constraints:
    Preconditions:
        - Caller should provide a mapping-like json_record. If the caller cannot guarantee the presence of 'userIdentity' or the nested arn for assumed-role sessions, the caller must guard with try/except.
    Postconditions:
        - If a non-None value is returned, it is the assumed-role ARN string extracted from the record.
        - No side effects or mutations are performed on the input.

## Side Effects:
    - None. The function performs only in-memory reads; there is no I/O, logging, network access, or mutation of external state.

## Control Flow:
flowchart TD
    Start[Start: json_record provided] --> GetUserIdentity[Attempt json_record['userIdentity']]
    GetUserIdentity -->|KeyError if missing or json_record not subscriptable| RaiseKeyError[KeyError raised -> caller must handle]
    GetUserIdentity --> UserIdentityAssigned[user_identity assigned]
    UserIdentityAssigned --> CheckType{'type' in user_identity and equals 'AssumedRole'?}
    CheckType -- No --> ReturnNone1[Return None]
    CheckType -- Yes --> CheckSessionContext{'sessionContext' in user_identity?}
    CheckSessionContext -- No --> ReturnNone2[Return None]
    CheckSessionContext -- Yes --> ReturnArn[Return user_identity['sessionContext']['sessionIssuer']['arn']]
    ReturnArn -->|May raise KeyError if sessionIssuer or 'arn' missing| RaiseNestedKeyError[KeyError raised -> caller must handle]
    ReturnNone1 --> End[End]
    ReturnNone2 --> End
    RaiseKeyError --> End
    RaiseNestedKeyError --> End

## Examples:

Example 1 — typical assumed-role record:
    record = {
        "userIdentity": {
            "type": "AssumedRole",
            "sessionContext": {
                "sessionIssuer": {
                    "arn": "arn:aws:iam::123456789012:role/RoleName"
                }
            }
        }
    }
    # Returns: "arn:aws:iam::123456789012:role/RoleName"

Example 2 — record that is present but not an assumed-role session:
    record = {"userIdentity": {"type": "Root", "arn": "arn:aws:iam::123456789012:root"}}
    # Returns: None

Example 3 — malformed record where top-level key is missing (caller must handle exception):
    record = {}
    try:
        arn = _assumed_role_arn(record)
    except (KeyError, TypeError):
        arn = None  # safe fallback for malformed records

Example 4 — malformed assumed-role-like record missing nested arn (will raise KeyError):
    record = {
        "userIdentity": {
            "type": "AssumedRole",
            "sessionContext": {
                # 'sessionIssuer' key missing or present without 'arn'
            }
        }
    }
    # Calling the function will raise KeyError when trying to access ['sessionIssuer'] or ['arn'].

## `trailscraper.cloudtrail._parse_record` · *function*

## Summary:
Parse a single CloudTrail JSON event mapping into a Record object containing event source, event name, UTC event timestamp, extracted resource ARNs, the assumed-role ARN (if any), and the original raw payload; returns None and logs a warning when required top-level keys are missing.

## Description:
- Known callers and call context:
    - Higher-level CloudTrail log-parsing code in this module (e.g., event iterators or file parsers) that iterate parsed JSON event records and convert each into a typed Record for downstream processing (such as converting to an IAM Statement). Typical pipeline stage: "parse raw JSON event -> call _parse_record(json_record) -> if Record returned, process further; otherwise skip/record error".
- Why this logic is a separate function:
    - Encapsulates the mapping from a raw CloudTrail JSON record into the Record data structure (including timestamp parsing and delegating extraction of resource ARNs and assumed-role ARN). This separates low-level field extraction and error handling from higher-level orchestration (iteration, filtering, policy-building) and centralizes the behavior for consistent parsing and logging.

## Args:
    json_record (Mapping[str, Any]):
        A mapping-like object (typically a dict parsed from CloudTrail JSON) representing a single CloudTrail event record.
        Required top-level keys used by this function:
            - 'eventSource' (str): service identifier (e.g., "s3.amazonaws.com")
            - 'eventName' (str): API/operation name (e.g., "PutObject")
            - 'eventTime' (str): timestamp in the exact format "%Y-%m-%dT%H:%M:%SZ" (UTC with trailing 'Z')
        Interdependencies:
            - The function accesses nested helpers:
                * _resource_arns(json_record) to produce resource_arns (see its doc for its input expectations).
                * _assumed_role_arn(json_record) to obtain an assumed-role ARN (see its doc for its input expectations).
            - If those helpers raise exceptions (other than KeyError), those exceptions propagate unless they are KeyError (see Raises and Behavior).

## Returns:
    Record or None
    - Record: A newly constructed Record with these fields populated:
        * event_source: value from json_record['eventSource']
        * event_name: value from json_record['eventName']
        * event_time: datetime.datetime parsed from json_record['eventTime'] using format "%Y-%m-%dT%H:%M:%SZ" and converted to an aware UTC datetime via .replace(tzinfo=pytz.utc)
        * resource_arns: result of _resource_arns(json_record) (list of ARNs or [])
        * assumed_role_arn: result of _assumed_role_arn(json_record) (string or None)
        * raw_source: the original json_record object
    - None: returned when any KeyError is raised during the construction (missing required top-level keys or a KeyError raised within a called helper). In that case, a warning is logged and None is returned to indicate the record could not be parsed.

## Raises:
    - The function catches KeyError and handles it by logging a warning and returning None. Therefore KeyError will not propagate to callers.
    - Exceptions that may propagate to the caller (not caught):
        * ValueError: if json_record['eventTime'] exists but does not match the expected format "%Y-%m-%dT%H:%M:%SZ", datetime.strptime raises ValueError and it propagates.
        * TypeError / AttributeError: if _resource_arns(json_record) raises TypeError or AttributeError (for example because json_record lacks .get or resources is None), those exceptions propagate.
        * Any other exception raised by Record constructor or by helper functions that is not KeyError will propagate (e.g., custom validation in Record, unexpected types).
    - Practical summary:
        * Missing required top-level keys yields a logged warning and None (KeyError handled).
        * Malformed timestamp or malformed nested structures that raise non-KeyError exceptions will surface to the caller.

## Constraints:
    Preconditions:
        - json_record must be subscriptable (support __getitem__) and normally contain 'eventSource', 'eventName', and 'eventTime'. If these are absent, the function will log and return None (KeyError).
        - eventTime must be a string exactly matching "%Y-%m-%dT%H:%M:%SZ" if timestamp parsing is expected to succeed.
        - Caller should be prepared to handle None (parse failure) and to catch non-KeyError exceptions for malformed nested data or timestamp format errors.
    Postconditions:
        - On successful return, the returned Record contains an aware UTC datetime in event_time and raw_source is the original json_record; resource_arns and assumed_role_arn reflect what the helper functions extracted.
        - On a KeyError during parsing, the function logs a warning and returns None without raising.

## Side Effects:
    - Logging: when a KeyError occurs anywhere during construction, a warning is emitted via logging.warning with the JSON record and the error message.
    - No I/O, network access, global state mutation, or external service calls are performed by this function itself. Helper functions called may raise exceptions but are documented separately for their side effects (they perform no I/O either).

## Control Flow:
flowchart TD
    A[Start: receive json_record] --> TryBlock[Attempt to build Record]
    TryBlock --> ParseEventSource[eventSource = json_record['eventSource']]
    TryBlock --> ParseEventName[eventName = json_record['eventName']]
    TryBlock --> ParseEventTime[eventTime = datetime.strptime(json_record['eventTime'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)]
    TryBlock --> ExtractResources[resource_arns = _resource_arns(json_record)]
    TryBlock --> ExtractAssumedRole[assumed_role_arn = _assumed_role_arn(json_record)]
    TryBlock --> ConstructRecord[Create Record(...)]
    ConstructRecord --> ReturnRecord[Return Record instance]
    TryBlock -->|KeyError anywhere| HandleKeyError[logging.warning("Could not parse ..., ...")]
    HandleKeyError --> ReturnNone[Return None]
    ParseEventTime -->|ValueError if format mismatch| PropagateValueError[ValueError propagates]
    ExtractResources -->|TypeError/AttributeError| PropagateTypeError[TypeError/AttributeError propagates]
    ExtractAssumedRole -->|KeyError from nested missing keys| HandleKeyError

## Examples:
1) Typical successful parse (conceptual input/output):
    Input record:
        {
            "eventSource": "s3.amazonaws.com",
            "eventName": "PutObject",
            "eventTime": "2023-01-01T12:00:00Z",
            "resources": [{"ARN": "arn:aws:s3:::example-bucket/obj"}],
            "userIdentity": { ... } 
        }
    Outcome:
        - Returns a Record with event_source="s3.amazonaws.com", event_name="PutObject",
          event_time set to a timezone-aware UTC datetime for 2023-01-01T12:00:00+00:00,
          resource_arns ["arn:aws:s3:::example-bucket/obj"], assumed_role_arn per helper result, raw_source equal to the input dict.

2) Missing required top-level key:
    Input record missing 'eventTime' or 'eventName':
        {"eventSource": "s3.amazonaws.com"}
    Outcome:
        - A warning is logged: "Could not parse <record>: 'eventTime'" (example)
        - Function returns None (no exception raised).

3) Malformed timestamp:
    Input record with eventTime = "2023-01-01 12:00:00" (wrong format)
    Outcome:
        - datetime.strptime raises ValueError and that exception propagates to the caller (function does not catch ValueError).

4) Nested helper raises KeyError:
    If _assumed_role_arn(json_record) raises KeyError because nested sessionIssuer['arn'] is missing, that KeyError is caught by this function; a warning is logged and None is returned.

Guidance for callers:
    - After calling _parse_record, always check for None before using the returned value.
    - Wrap calls in try/except to handle ValueError and TypeError if input data may be malformed beyond missing keys.

## `trailscraper.cloudtrail.parse_records` · *function*

## Summary:
Convert an iterable of raw CloudTrail JSON event records into a list of successfully parsed Record objects by delegating each item to the single-record parser and discarding any records that failed to parse.

## Description:
- Known callers and call context:
    - Higher-level CloudTrail log-processing code that extracts the "Records" array from CloudTrail payloads (for example, functions that read CloudTrail log files, S3-stored logs, or delivery payloads) and then need to convert that array of JSON objects into typed Record instances for downstream policy or analysis steps.
    - Typical pipeline stage: "read raw CloudTrail JSON -> extract list of event records -> call parse_records(list_of_records) -> receive list[Record] for further processing (statement extraction, aggregation, storage)."

- Why this logic is extracted into its own function:
    - Encapsulates the iteration and filtering semantics (call per-record parser and drop failed parses) so callers do not need to duplicate the loop, None filtering, or the handling policy for partially malformed batches. This keeps calling code concise and enforces a consistent contract: callers receive only successfully parsed Record objects (no None values).

## Args:
    json_records (iterable[Mapping[str, Any]]):
        An iterable (typically a list) of JSON-like mapping objects representing individual CloudTrail event records (each item is usually a dict parsed from JSON).
        - Each element is passed unchanged to the internal _parse_record function.
        - If json_records is not iterable, a TypeError will be raised by Python before any parsing occurs.

## Returns:
    list[Record]
    - A list containing the Record instances returned by _parse_record for each input element that successfully parsed.
    - The ordering of returned Record objects preserves the order of their successful inputs (stable, input-order relative).
    - If no input records parse successfully, an empty list is returned.
    - None values produced by _parse_record are removed; callers are guaranteed that the returned list contains no None entries.

## Raises:
    - TypeError: if json_records is not iterable (e.g., None) or if iteration over json_records fails; this originates from Python iteration semantics rather than being raised explicitly by this function.
    - Any exception raised by _parse_record that is not handled inside _parse_record will propagate. Notable possible propagated exceptions include:
        * ValueError: if a nested timestamp inside a record is malformed and _parse_record's timestamp parsing raises ValueError.
        * TypeError / AttributeError: if a nested structure is malformed and _parse_record (or helpers it calls) raises these.
    - parse_records does not catch exceptions raised by _parse_record; it only filters out None results returned by _parse_record.

## Constraints:
- Preconditions:
    - json_records must be an iterable of mapping-like objects suitable for _parse_record (each element should normally contain the keys _parse_record expects: 'eventSource', 'eventName', 'eventTime', etc.).
    - Callers should be prepared to handle exceptions propagated from _parse_record (e.g., ValueError for malformed timestamps).
- Postconditions:
    - Returns a list of Record instances with no None entries.
    - The original input iterable is not modified by this function (items are read but not mutated by parse_records itself).

## Side Effects:
- Indirect logging: _parse_record may emit logging warnings for records that fail due to missing required keys; those warnings will occur during parse_records execution because it delegates to _parse_record. parse_records itself performs no logging, I/O, network calls, or global-state mutations.
- No file, network, or persistent-state operations are performed directly by this function.

## Control Flow:
flowchart TD
    A[Start: receive json_records iterable] --> B{Can iterate?}
    B -- yes --> C[For each record in json_records: call _parse_record(record)]
    C --> D{_parse_record returned value}
    D -- Record instance --> E[Append to results list]
    D -- None --> F[Skip / do not append]
    C --> G[Continue next record until end]
    B -- no --> H[TypeError from iteration propagates]
    G --> I[Return results list (possibly empty)]

## Examples:
1) Typical usage (conceptual):
    - Input: a list of CloudTrail event dicts extracted from a log payload.
    - Behavior: parse_records calls _parse_record for each dict, discards any None results, and returns a list of valid Record objects in the same relative order as their input entries.
    - Result: use the returned list for statement extraction, aggregation, or storage; no caller-side filtering of None is required.

2) Handling malformed batches:
    - If some events are missing required keys, _parse_record will log a warning for each such event and return None for them; parse_records returns a list containing only the successfully parsed events.
    - If any record contains a malformed timestamp (causing ValueError inside _parse_record), that ValueError will propagate from parse_records and should be caught by the caller if the caller needs to continue processing other batches.

3) Empty input or no successful parses:
    - Input: an empty list or a list where every record fails to parse.
    - Output: an empty list is returned.

Notes and recommendations:
    - Wrap calls to parse_records in try/except when input data may contain malformed values that should not abort the whole processing pipeline.
    - Because parse_records preserves order and removes only failed parses, it is suitable for pipelines that rely on temporal or sequence ordering of events.

## `trailscraper.cloudtrail._by_timeframe` · *function*

## Summary:
Returns a predicate function that selects records whose event_time is either missing (None) or falls inclusively within the given start and end datetimes.

## Description:
This helper constructs a boolean predicate intended for filtering collections of event/record objects by their event_time attribute. The returned predicate evaluates to True when the record has no event_time (None) or when event_time is between the provided from_date and to_date inclusive.

Known context within this module:
- The module imports toolz.curried.filter and pipe; the predicate produced here is intended to be used with filter-like APIs (for example, toolz.filter, built-in filter, or comprehension-based filtering) when processing CloudTrail-style records.

Why this logic is extracted:
- Encapsulates the inclusive timeframe test (and the deliberate acceptance of records with missing event_time) in a small, reusable predicate.
- Keeps filtering logic declarative and composable (suitable for passing to higher-order filter functions) rather than inlining repeated comparisons throughout the codebase.

## Args:
    from_date (datetime.datetime): Inclusive start of the timeframe. Should be comparable to record.event_time.
    to_date (datetime.datetime): Inclusive end of the timeframe. Should be comparable to record.event_time.

Notes on types and interdependencies:
- Both from_date and to_date must be objects comparable with record.event_time using <= and >= (typically datetime.datetime instances).
- It is strongly recommended that all datetimes be either all timezone-aware or all timezone-naive to avoid TypeError when comparing; mixing aware and naive datetimes will raise an exception at runtime.
- No implicit validation is performed: if from_date > to_date, the predicate will only accept records with event_time is None (unless a record.event_time somehow falls between those values, which is impossible if they are datetimes).

## Returns:
    callable(record) -> bool

The returned function takes a single argument (record) and returns:
- True if record.event_time is None.
- True if from_date <= record.event_time <= to_date.
- False otherwise.

Edge-case return behaviour:
- If record.event_time has a type that is not comparable with from_date/to_date, the predicate will raise TypeError.
- If record lacks an event_time attribute, an AttributeError will be raised by the predicate.

## Raises:
This function itself does not raise exceptions when creating the predicate, but invoking the returned predicate may raise:
    AttributeError: If the provided record has no attribute named event_time.
    TypeError: If record.event_time cannot be compared to from_date/to_date (e.g., mixing timezone-aware and naive datetimes, or incompatible types).
These exceptions are produced by the underlying comparison operations and are not caught by the predicate.

## Constraints:
Preconditions (caller must ensure):
- from_date and to_date must be comparable to the event_time attribute values (preferably datetime.datetime instances).
- Prefer consistent timezone-awareness for all datetimes used in comparisons.

Postconditions (guarantees after return):
- The function returns a stateless predicate suitable for repeated use in filtering operations.
- The predicate implements the inclusive range test plus allowance for missing event_time as described in Returns.

## Side Effects:
- None. The function and the returned predicate perform no I/O and do not mutate external state.

## Control Flow:
flowchart TD
    A[Start: call _by_timeframe(from_date,to_date)] --> B[Return predicate function]
    B --> C[Invoke predicate(record)]
    C --> D{record.event_time is None?}
    D -- Yes --> E[Return True]
    D -- No --> F{from_date <= record.event_time <= to_date?}
    F -- Yes --> E
    F -- No --> G[Return False]
    C --> H[If record lacks event_time attribute -> AttributeError (propagates)]
    C --> I[If comparison invalid -> TypeError (propagates)]

## Examples:
Usage pattern (described in prose):
- Construct a predicate for a one-week interval and use it with a filter operation over a list of event records:
  1. Decide the timeframe boundaries as datetime.datetime values (keep timezone consistency).
  2. Call this helper to obtain the predicate.
  3. Use the predicate with a filtering API (for example, toolz.curried.filter, built-in filter, or a list comprehension) to retain records whose event_time is None or falls inside the timeframe.
  4. Handle exceptions if records may be missing the event_time attribute or if datetimes may be incompatible.

Error handling guidance:
- If input records may lack an event_time attribute and you prefer to treat such records as excluded rather than included, wrap or replace the predicate with a safe wrapper that checks for hasattr(record, "event_time") and returns False when absent.
- To avoid TypeError due to timezone mixing, normalize datetimes (e.g., convert to UTC timezone-aware datetimes) before creating the predicate.

Typical developer note:
- The predicate intentionally treats missing event_time (None) as a match. If this policy should differ in a particular pipeline, filter the None cases explicitly before or after applying this predicate.

## `trailscraper.cloudtrail._by_role_arns` · *function*

*No documentation generated.*

## `trailscraper.cloudtrail.filter_records` · *function*

## Summary:
Filters an iterable of CloudTrail-style records by an inclusive timeframe and optional role-ARN membership, returning a list of records that pass both predicates; logs a warning if the input contained records but all were filtered out.

## Description:
This function composes two predicates to reduce an input sequence of records:
- a timeframe predicate produced by _by_timeframe(from_date, to_date) (see its component documentation), and
- a role-ARN predicate produced by _by_role_arns(arns_to_filter_for) (module-level helper; behavior expected: accept or reject records based on whether the record represents activity by one of the supplied ARNs).

It uses a functional pipeline (toolz.pipe-style) to apply the two filters in sequence and materializes the result as a list.

Known callers:
- No direct callers were discovered in the provided code snapshot. Typical usage is inside pipelines that process CloudTrail event batches (for example, when narrowing events to a timeframe and a set of IAM role principals prior to permission analysis).

Why this is extracted:
- Centralizes the dual-filtering pattern so callers can request the common combination "timeframe + role-ARN" without duplicating predicate composition.
- Keeps higher-level pipeline code declarative and small by encapsulating filter composition, list materialization, and the "log when everything was filtered" policy.

## Args:
    records (iterable): An iterable of record objects or dict-like records representing CloudTrail events.
        - Each record is expected to be compatible with the predicates produced by _by_timeframe and _by_role_arns (for example, to have an event_time attribute or key and the fields examined by the role-ARN predicate).
        - The function will iterate the iterable once; if it is a generator it will be consumed.
    arns_to_filter_for (iterable[str] | None): Optional collection of IAM role ARNs to retain.
        - None (default) indicates no ARN-based restriction; the role-ARN predicate implementation is expected to accept all records in this case (i.e., act as a no-op).
        - If provided, each element should be a string ARN; predicate semantics (exact match, prefix match, etc.) depend on _by_role_arns implementation.
    from_date (datetime.datetime): Inclusive lower bound for event_time. Default: datetime.datetime(1970, 1, 1, tzinfo=pytz.utc).
        - Must be comparable with record.event_time values (matching timezone-awareness).
    to_date (datetime.datetime): Inclusive upper bound for event_time.
        - Default: value computed by datetime.datetime.now(tz=pytz.utc) at function definition time (i.e., the module import time). This default is fixed when the module is imported — callers should pass an explicit to_date for an up-to-date upper bound.

Notes on parameter interdependencies:
- Both date parameters must be comparable with record.event_time (mixing timezone-aware and naive datetimes will raise TypeError).
- The predicates expect the same interpretation of missing or None event_time as implemented by _by_timeframe (see that helper's doc: it treats record.event_time == None as a match).

## Returns:
    list: A list of input records that passed both the timeframe and role-ARN predicates.
    - If input records is empty or falsy, returns an empty list.
    - If no records remain after filtering but input records was non-empty, returns [] and a warning is emitted via logging.warning with the module constant ALL_RECORDS_FILTERED as the message.

Edge-case return values:
- The function always returns a list (never an iterator), possibly empty.
- No special sentinel values are returned.

## Raises:
This function does not explicitly raise custom exceptions, but exceptions from its dependencies or predicate evaluation will propagate:
    - NameError: If the module-level symbol filterz, _by_role_arns, or ALL_RECORDS_FILTERED is undefined at runtime (the function references these symbols).
    - TypeError: May be raised during datetime comparisons inside the timeframe predicate (e.g., mixing timezone-aware and naive datetimes) or by incompatible types in record fields.
    - AttributeError / KeyError: If predicates assume attributes/keys that are missing from a record, those exceptions will propagate unless predicates handle them.
    - Any other exception raised by the predicates or by iterating records will propagate to the caller.

## Constraints:
Preconditions:
    - The caller must provide records that are consumable by the timeframe and role-ARN predicates (see _by_timeframe doc for event_time expectations).
    - Prefer timezone-consistent datetime inputs (all-aware or all-naive).
    - If the caller expects up-to-the-moment to_date behavior, pass to_date explicitly (the default to_date is evaluated at module import time).

Postconditions:
    - All returned records satisfy both predicates.
    - The input iterable will be consumed (if it was an iterator/generator).
    - No external state is changed by this function beyond logging.

## Side Effects:
    - Emits a log warning via logging.warning(ALL_RECORDS_FILTERED) when the input contained at least one record but none matched after filtering.
    - No I/O, network calls, file writes, or global state mutations are performed by this function itself.
    - Exceptions originating in helper predicates may cause additional side effects if those helpers perform I/O.

## Control Flow:
flowchart TD
    A[Start: call filter_records(records,...)] --> B{records truthy?}
    B -- No --> C[Return [] immediately]
    B -- Yes --> D[Construct timeframe predicate: _by_timeframe(from_date,to_date)]
    D --> E[Construct role predicate: _by_role_arns(arns_to_filter_for)]
    E --> F[Apply pipe(records, filterz(timeframe_pred), filterz(role_pred)) and materialize list]
    F --> G{result non-empty?}
    G -- Yes --> H[Return result (list of records)]
    G -- No --> I[logging.warning(ALL_RECORDS_FILTERED)]
    I --> H

## Examples:
Example — typical filtering pipeline (pseudocode):
    # Given an iterable of CloudTrail-like event records whose event_time values are datetime objects:
    filtered = filter_records(records, arns_to_filter_for=['arn:aws:iam::123456789012:role/MyRole'],
                              from_date=start_dt, to_date=end_dt)
    # filtered is a list of records where event_time is between start_dt and end_dt (inclusive)
    # and (depending on _by_role_arns) the record indicates activity by one of the requested ARNs.
    if not filtered and records:
        # The function already logged ALL_RECORDS_FILTERED; handle the empty result if needed.
        handle_empty_case()

Error handling guidance:
    - If records may contain items missing required fields, either:
        * normalize records before calling (add missing fields or filter them), or
        * ensure the helper predicates are defensive (catch AttributeError/KeyError) so that filter_records does not raise.
    - To avoid stale default to_date, compute now at call time and pass it explicitly:
        safe_filtered = filter_records(records, from_date=earlier, to_date=datetime.datetime.now(tz=pytz.utc))

