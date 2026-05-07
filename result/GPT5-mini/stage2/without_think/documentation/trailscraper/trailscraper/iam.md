# `iam.py`

## `trailscraper.iam.BaseElement` · *class*

## Summary:
BaseElement is a minimal abstract base for domain elements that expose a deterministic JSON-style representation (json_repr) used for equality, hashing, and textual representation.

## Description:
BaseElement exists to centralize a single canonical representation hook (json_repr) that subclasses implement. This representation is used by the base class implementations of equality, inequality, hashing, and repr so that subclasses gain consistent value-based semantics without re-implementing those methods.

When to instantiate:
- You do not instantiate BaseElement directly. Subclasses must override json_repr and are instantiated instead.
- Typical callers/factories: any factory or deserialization code that produces domain element instances (for example, parsers that convert external JSON/records into model objects) should instantiate subclasses of BaseElement.

Motivation and responsibility boundary:
- Responsibility: provide reusable, consistent implementations of __eq__, __ne__, __hash__, and __repr__ that depend entirely on a single, canonical representation returned by json_repr.
- Boundary: BaseElement does NOT define storage, validation, or construction parameters — those are the responsibility of subclasses. BaseElement enforces only the contract around json_repr and how it will be used.

## State:
This class has no instance attributes declared by itself. State expectations are expressed as requirements on the value returned by json_repr implemented by subclasses.

For json_repr() return value:
- Expected type: any value that:
  - is deterministic (same logical object state → same returned value),
  - is suitable for equality comparisons (the returned value's equality semantics are relied upon),
  - and ideally is JSON-serializable (primitives, lists/tuples, dict-like structures) because the method name implies JSON-like structure.
- Hashability constraint: Because BaseElement.__hash__ calls hash(self.json_repr()), the returned value must be hashable (for example: str, int, float, tuple, frozenset, or other immutable objects). If json_repr returns an unhashable container (e.g., dict or list), calling hash(...) will raise TypeError. Either ensure json_repr returns a hashable representation or override __hash__ in the subclass.
- Stability constraint: If instances are used in hashed collections (set, dict keys), json_repr must be stable (unchanged) for the lifetime of the object while it is in those collections. Violating this breaks the invariants of hashing containers.

Class invariants:
- For any two instances a and b of the same class (or subclass of that class; see equality caveat below): a == b iff a.json_repr() == b.json_repr().
- __repr__ returns a string form of json_repr(): repr(a) == str(a.json_repr()).

## Lifecycle:
Creation:
- Instantiate subclasses that override json_repr. BaseElement itself has no __init__ signature to follow.

Usage (typical method order and expectations):
1. Create a subclass instance that implements json_repr.
2. Use equality comparisons (==) between instances of related classes to check value equivalence.
3. Use instances as keys in dicts or elements of sets only if json_repr returns a stable, hashable value.
4. Use repr() to obtain a string representation based on json_repr.

Destruction/Cleanup:
- BaseElement provides no special cleanup. There is no context-manager protocol or close() hook defined here. Resource cleanup, if any, must be implemented by subclasses.

## Method Map:
Mermaid diagram showing relationships and typical invocation paths:

graph LR
    json_repr[json_repr()] --> eq[__eq__(other)]
    json_repr --> hash[__hash__()]
    json_repr --> repr[__repr__()]
    eq --> ne[__ne__(other)]
    note[Note: json_repr must be deterministic and preferably hashable] --> json_repr

(Interpretation: __eq__, __hash__, and __repr__ delegate to json_repr; __ne__ delegates to __eq__.)

## Methods (behavioral detail):
- json_repr(self)
  - Purpose: Return the canonical representation of this element that defines value identity.
  - Parameters: none
  - Returns: any Python object representing the element's value. Recommended to be JSON-serializable and hashable.
  - Behavior: Abstract in BaseElement — subclasses MUST override. If not overridden, calling json_repr() raises NotImplementedError.
  - Edge cases / constraints:
    - Must be deterministic across calls for the same logical state.
    - If the returned object is mutable or unhashable, be aware of consequences on hashing and container membership.
    - Prefer immutable containers (tuple, frozenset) or primitive types for safe hashing.

- __eq__(self, other)
  - Purpose: Value-based equality comparing canonical representations.
  - Behavior:
    - If other is an instance of self.__class__ (i.e., the same class or a subclass of self's class), returns self.json_repr() == other.json_repr().
    - Otherwise returns False.
  - Important caveat:
    - This implementation can produce asymmetric equality in cross-class comparisons. Example:
      - If A is a base class and B a subclass of A, then A_instance == B_instance may be True (isinstance(B_instance, A) is True), but B_instance == A_instance will be False if B.__class__ is not a superclass of A. This violates the usual symmetry expectation of equality; design subclasses accordingly if cross-class comparisons are expected.

- __ne__(self, other)
  - Purpose: Inequality.
  - Behavior: Returns the logical negation of __eq__.

- __hash__(self)
  - Purpose: Allow instances to be used in hashed collections based on their canonical representation.
  - Behavior: Returns hash(self.json_repr()).
  - Edge cases:
    - If json_repr returns an unhashable object (e.g., dict or list), calling __hash__ will raise TypeError. To avoid this, ensure json_repr returns a hashable representation or override __hash__ in the subclass.
    - Hash must be stable for the lifetime of the object while it is present in any hashed container.

- __repr__(self)
  - Purpose: Human-readable textual representation.
  - Behavior: Returns str(self.json_repr()).

## Raises:
- json_repr (called on BaseElement) raises NotImplementedError in the base implementation. Subclasses must override json_repr; otherwise methods that rely on it will propagate NotImplementedError (direct call) or raise other errors (for example, hash/eq calling json_repr may propagate NotImplementedError).
- __hash__ may raise TypeError if json_repr() returns an unhashable value.

## Example (usage pattern, described):
- Define a subclass that implements json_repr to return an immutable, JSON-serializable value (for example, a tuple of primitive fields, or a stringified canonical JSON).
- Instantiate two objects of the same subclass. Comparing them with == will compare their json_repr values.
- If json_repr returns a hashable and stable value, you can add instances to a set or use them as dict keys. If the representation is mutable or unhashable, either avoid using hashed containers or override __hash__.
- When implementing subclasses that might be compared with instances of related classes, be aware of the asymmetric equality behavior; if symmetry is required, implement equality using an explicit type check (type(self) is type(other)) or otherwise coordinate equality semantics across the class hierarchy.

### `trailscraper.iam.BaseElement.json_repr` · *method*

## Summary:
Provide a canonical, JSON-style representation of this element suitable for equality, hashing, and textual representation; the base implementation is abstract and must be overridden by subclasses.

## Description:
This method is intended to be implemented by subclasses to return a representation of the element that captures its identity and value in a form suitable for equality checks, hashing, and stringification.

Known callers and contexts:
- BaseElement.__eq__: compares the json_repr() return value of two instances to determine equality (used during object comparisons and tests).
- BaseElement.__hash__: hashes the json_repr() return value to produce a stable hash for use in sets and dict keys.
- BaseElement.__repr__: converts the json_repr() return value to a string for debugging and logging.

Lifecycle stage / pipeline step:
- Invoked whenever instances are compared, used as dictionary keys or set members, or printed/logged. This typically occurs during runtime operations that compare elements, insert them into collections, or serialize/inspect them.

Why this is a separate method:
- Centralizes the element's canonical external representation so equality, hashing, and textual representation behave consistently without duplicating logic across those methods. Subclasses implement this once to guarantee consistent behavior across comparisons, hashing, and repr.

## Args:
    None

## Returns:
    Any
    - The returned value represents the element's canonical representation.
    - Practical requirements for compatibility with the rest of BaseElement:
        * Must be equality-comparable (values that support ==).
        * Must be string-convertible via str(...) because __repr__ uses str(json_repr()).
        * To be safely used with BaseElement.__hash__, it should be hashable (e.g., int, str, tuple, frozenset). If an unhashable type is returned (e.g., dict, list), calling __hash__ will raise a TypeError.
    - Implementations may choose a primitive (str/int/float), a tuple of primitives, or another immutable structure that faithfully encodes the element's identity.

## Raises:
    NotImplementedError
    - The base implementation always raises this to indicate that subclasses must provide a concrete implementation.
    - Trigger condition: calling BaseElement.json_repr() on the base class (or on a subclass that did not override the method).

## State Changes:
    Attributes READ:
        - None in the base implementation. (Note: subclass implementations will typically read one or more self.<attr> attributes to build the representation; document those attributes in the subclass's json_repr documentation.)
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The caller should expect this method to be implemented by concrete subclasses. Calling the base implementation directly will raise NotImplementedError.
        - To avoid breaking BaseElement.__hash__, the subclass's return value should be hashable if instances are expected to be used as keys in dicts or elements in sets.

    Postconditions:
        - A successful call returns a value that encodes the element's identity/value without mutating self.
        - Given two instances a and b of the same concrete subclass, if a.json_repr() == b.json_repr() then a == b (because BaseElement.__eq__ delegates to json_repr()).
        - If json_repr() returns hashable, hash(a) == hash(b) whenever a.json_repr() == b.json_repr().

## Side Effects:
    - The base method has no side effects.
    - Subclass implementations should avoid performing I/O or mutating global state; json_repr is expected to be a pure/accessor-like operation used for identity, hashing, and display.

### `trailscraper.iam.BaseElement.__eq__` · *method*

## Summary:
Compares this element to another by checking both are instances of the same class (or compatible subclass) and that their JSON representations (from json_repr) are equal; does not modify the object's state.

## Description:
- Known callers and context:
    - Internal: __ne__ uses the equality operator (not self == other) and therefore invokes this method when Python evaluates "self == other" inside __ne__.
    - No additional direct external callers were discovered in the inspected class definition. In normal use this method is invoked whenever code uses the "==" operator to compare two BaseElement-derived instances (for example: equality checks, membership tests, assertions in tests, or de-duplication logic).
    - The class also provides __hash__ (based on json_repr) and __repr__ (stringified json_repr); equality is intentionally implemented to align with __hash__ so that objects with equal json_repr compare equal and have the same hash.
- Rationale for being a separate method:
    - Centralizes the equality semantics for all subclasses by delegating structural equality to json_repr, ensuring a consistent definition of equality across the class hierarchy and avoiding duplicated comparison code in many places.
    - Keeps operator behavior (==) concise and ensures the semantic relationship between equality, hashing, and string representation is maintained.

## Args:
    other (object): Any object. The method only returns True if other is an instance of self.__class__ (i.e., isinstance(other, self.__class__)) and the two json_repr() outputs compare equal.

## Returns:
    bool: 
        - True if isinstance(other, self.__class__) is True and self.json_repr() == other.json_repr().
        - False otherwise (including whenever other is a different, non-compatible type).

## Raises:
    - Any exception raised by self.json_repr() or other.json_repr() will propagate out of __eq__ (for example NotImplementedError if the subclass has not implemented json_repr). __eq__ itself does not catch or raise additional exceptions.

## State Changes:
    Attributes READ:
        - None explicitly by this method. It calls self.json_repr() and other.json_repr(), which in turn may read instance attributes defined by subclasses.
    Attributes WRITTEN:
        - None. __eq__ does not modify self or other.

## Constraints:
    Preconditions:
        - The instance (self) and other must be in a valid state for json_repr() to run (i.e., json_repr must be callable and should not raise unintentionally).
        - For a comparison to return True, other must be an instance of self.__class__ (isinstance check) and both json_repr() outputs must be comparable for equality.
    Postconditions:
        - No mutation performed on self or other.
        - The return value is a boolean describing structural equality based on json_repr.
    Important notes:
        - Because the method uses isinstance(other, self.__class__), equality can be sensitive to the class hierarchy: comparisons between instances of related but different classes (e.g., a class and one of its subclasses) can produce asymmetric results depending on which side is compared first. Developers should be aware of this if symmetry across hierarchies is required.
        - To satisfy the equality/hash contract, subclasses should ensure json_repr() is stable and deterministic (objects that are equal according to __eq__ should yield equal hashes via __hash__).

## Side Effects:
    - __eq__ performs no I/O and makes no external service calls itself.
    - Any side effects are those of json_repr(); if a subclass's json_repr performs I/O, network calls, or mutates state, those side effects will occur when __eq__ invokes it.

### `trailscraper.iam.BaseElement.__ne__` · *method*

## Summary:
Returns the logical negation of equality with another object (i.e., True when the two objects are not equal). Does not modify the object's state.

## Description:
This method is invoked when Python's inequality operator (!=) is used between instances of this class (or when code calls __ne__ explicitly). No repository-specific call sites were found in the provided code snapshot; it is therefore relied upon anywhere inequality semantics for BaseElement-derived objects are required (for example: filtering, deduplication, conditional checks).

The method exists as a distinct override so that inequality semantics are consistent with the class's equality implementation (__eq__). By delegating to __eq__ and returning its boolean negation, subclasses only need to implement json_repr (and thereby __eq__) to get consistent != behavior without duplicating comparison logic.

## Args:
    other (object): Any object to compare against. There is no type restriction in this method itself; equality is determined by the class's __eq__ implementation which checks instance type and compares json_repr() values.

## Returns:
    bool: True if the current object and other are not equal; False otherwise.
    - If other is not an instance of the same concrete class, __eq__ returns False and so __ne__ returns True.
    - Edge cases:
        * If __eq__ (or any method it calls, e.g., json_repr) raises an exception, that exception will propagate and __ne__ will not return a boolean.

## Raises:
    Propagated exceptions raised by __eq__ or underlying calls:
    - NotImplementedError: If json_repr is not implemented by a subclass and __eq__ attempts to call it.
    - Any other exception raised by json_repr or __eq__ (TypeError, AttributeError, etc.) will propagate unchanged.

## State Changes:
    Attributes READ:
        - None directly accessed here, but this method calls self.__eq__(other), which in turn calls self.json_repr() and other.json_repr(); those methods may read internal attributes of both objects.
    Attributes WRITTEN:
        - None. This method does not mutate self or other.

## Constraints:
    Preconditions:
        - self and other should be fully-initialized instances (or any objects) such that calling __eq__ and json_repr (if invoked) is valid.
        - Subclasses are expected to implement json_repr; otherwise __eq__ may raise NotImplementedError.
    Postconditions:
        - No mutation occurs on self or other.
        - The method returns a boolean if no exception is raised; otherwise it raises the same exception __eq__/json_repr raised.

## Side Effects:
    - No I/O or external service calls.
    - No mutations of objects outside self and other.
    - The only runtime effect is calling __eq__ (which may lead to arbitrary read-only operations performed by json_repr).

### `trailscraper.iam.BaseElement.__hash__` · *method*

## Summary:
Returns the integer hash of the element's canonical JSON representation, enabling instances to be used in hashed collections (dict keys, set members) while remaining consistent with the class's equality semantics.

## Description:
This method delegates to the object's json_repr() to obtain a canonical representation of the element and returns Python's built-in hash() of that representation.

Known callers and typical invocation contexts:
- The Python runtime when an instance is used as a key in a dict or inserted into a set.
- Explicit calls to the built-in hash() function on an instance.
- Any library or code path that caches, indexes, or deduplicates elements by their hash value.

Lifecycle stage / pipeline step:
- Invoked at equality / membership-check phases: when adding or looking up instances in hashed collections (e.g., during building of indexes, sets, or mapping keys).
- Not intended to be called during mutation of the object's identity fields — it should be used after the object is in a stable/immutable state with respect to its identity.

Why this logic is its own method:
- Centralizes the hashing strategy to mirror __eq__ which uses json_repr() for equality. Keeping hashing logic simple and delegated to json_repr() ensures consistent identity semantics across equality and hashing without duplicating representation logic in multiple places.
- Allows subclasses to control identity by implementing json_repr() once; __hash__ remains generic and correct for all such subclasses.

## Args:
None

## Returns:
int
- The integer result of calling Python's built-in hash() on the value returned by self.json_repr().
- Edge cases:
  - If json_repr() returns an already-hashed/int value, hash() will be applied to that value producing an int as usual.
  - Hash collisions are possible (two distinct representations may yield equal hash values); callers must not rely on hashes for uniqueness beyond the normal guarantees of Python's hash function.

## Raises:
- NotImplementedError: If the subclass has not implemented json_repr(), the call to self.json_repr() will raise this error (as BaseElement.json_repr raises NotImplementedError).
- TypeError: If json_repr() returns an unhashable value (e.g., a dict, list, or other unhashable container), Python's built-in hash() will raise TypeError.
- Any exception raised by json_repr() will propagate through __hash__ unchanged.

## State Changes:
Attributes READ:
- None directly by __hash__ itself.
- Indirectly, __hash__ invokes self.json_repr(), which may read one or more self.<attr> attributes. Therefore, any attributes used by json_repr() are read during hashing.

Attributes WRITTEN:
- None. __hash__ does not modify self or any external state.

## Constraints:
Preconditions:
- json_repr() must be implemented by subclasses and must return a value that:
  - Is hashable (i.e., hash(value) does not raise TypeError).
  - Is stable/immutable for the lifetime of the object while it is used in hashed collections (its value must not change while the object is used as a key in a dict or as a member of a set).
  - Is logically consistent with __eq__: two objects that compare equal via __eq__ must produce equal json_repr() values so that their hashes match.
- Prefer producing a string or tuple (immutable, hashable) from json_repr() rather than mutable containers like dicts or lists.

Postconditions:
- Returns an integer hash value derived from the current json_repr() of the instance.
- Does not modify the instance or any external objects.

## Side Effects:
- None intrinsic to __hash__ beyond calling self.json_repr(). No I/O, no external service calls.
- Any side effects would come from the implementation of json_repr() (if it performs I/O or mutates state) — such side effects would be observed when __hash__ is invoked.

### `trailscraper.iam.BaseElement.__repr__` · *method*

## Summary:
Return a human-readable string representation of the object by converting the object produced by json_repr() to a string; does not modify the object's state.

## Description:
This method delegates the actual structural representation to self.json_repr() and returns its string conversion. It is typically invoked implicitly by the Python runtime (for example via the built-in repr() and when an object is printed or logged if no custom __str__ is defined), and may be used by developers during debugging and logging to inspect object contents.

Known callers and contexts:
- No explicit internal callers exist in this module; runtime-level callers include:
  - repr(instance) which directly calls __repr__.
  - str(instance) and print(instance) in contexts where __str__ is not overridden (the runtime will use __repr__ to produce the string).
- Developers or logging/debugging code that obtain textual representations of objects.

Why this is a standalone method:
- Keeps textual formatting centralized so every subclass can provide a JSON-like structure via json_repr() and inherit a consistent string representation.
- Separates concerns: json_repr() defines the serializable structure; __repr__ controls how that structure is presented as text.

## Args:
    None

## Returns:
    str: The string result of calling str(self.json_repr()).
    - If json_repr() returns a dict/list/primitive, the returned value is the stringified form of that object (exact formatting depends on the object's __str__ implementation).
    - If json_repr() already returns a string, the returned value will be that string (possibly unchanged).
    - Edge cases: if json_repr() returns an object whose __str__ raises an exception, that exception will propagate.

## Raises:
    Any exception raised by self.json_repr() will propagate unchanged.
    - NotImplementedError: raised when the class (or a subclass) has not implemented json_repr(); since BaseElement.json_repr() raises NotImplementedError, calling __repr__ on an instance that uses the base implementation will raise NotImplementedError.
    - Any other exception raised by json_repr() or by the returned object's __str__ will also be propagated.

## State Changes:
Attributes READ:
    - Calls the method self.json_repr(); the method may read attributes of self to build the returned structure.

Attributes WRITTEN:
    - None. __repr__ itself does not modify any attributes on self.

## Constraints:
Preconditions:
    - The instance must provide a working json_repr() implementation (i.e., a subclass must override json_repr to return a serializable or printable structure) if the caller expects a successful string representation.

Postconditions:
    - Returns str(self.json_repr()) without mutating the instance.
    - If json_repr() completes normally, no attributes on self are changed by __repr__.

## Side Effects:
    - None directly. __repr__ performs no I/O and does not call external services.
    - Note: any side effects performed inside json_repr() (if a subclass implements it with side effects) will occur when __repr__ invokes json_repr(); those are not caused by __repr__ itself but will be observed by callers.

## `trailscraper.iam.Action` · *class*

## Summary:
Represents a single IAM action (service prefix and action name) as a value object with a canonical JSON-style string representation ("prefix:action") used for equality, hashing, and matching against the repository of known IAM actions.

## Description:
Action is a lightweight value-class that encapsulates the two parts of an IAM permission identifier: the service/namespace prefix (the substring before ":") and the action name (the substring after ":"). It supplies:
- json_repr(): the canonical string form "prefix:action" used by the BaseElement superclass to implement equality, hashing, and repr.
- _base_action(): a normalized action name with common base prefixes removed and trailing plural 's' stripped to produce a simple stem used for generating related action candidates.
- matching_actions(allowed_prefixes): generate candidate Actions by combining allowed prefixes with the normalized base action (and its plural) and return only those candidates that are known/recognized for this Action's prefix (delegates verification to known_iam_actions).

Typical callers and instantiation scenarios:
- Parsers/deserializers converting textual IAM action identifiers into objects.
- Policy validation, auto-completion, or normalization routines that need to enumerate or match related actions.
- Tests and tooling that manipulate or compare lists of actions.

Motivation and responsibility boundary:
- Purpose: provide a stable, value-based representation of IAM action strings and helpers to derive related/alternate action forms.
- Boundary: Action does not perform file I/O or manage the repository of known actions itself — it delegates that lookup to known_iam_actions. It also does not validate inputs on construction beyond storing them.

## State:
Attributes (instance-level):
- prefix (str)
    - Description: IAM service/namespace portion before ":" (for example "s3", "ec2").
    - Expected type: str. Required by json_repr which joins prefix and action with ':'; non-str values will cause TypeError when json_repr() is called.
    - Constraints: should be a stable, immutable string for reliable hashing and comparison.
- action (str)
    - Description: action name portion (for example "GetObject", "ListBuckets").
    - Expected type: str. Non-str values will cause TypeError when json_repr() is called.
    - Constraints: should be stable and immutable while the object is used in hashed collections.

Derived/stateful results:
- json_repr() (str): canonical representation "prefix:action" (string).
- _base_action() (str): normalized stem derived from .action by removing any regex prefixes contained in BASE_ACTION_PREFIXES (applied via re.sub) and removing a trailing "s" if present.

Class invariants:
- json_repr() returns a deterministic, hashable string; because BaseElement implements __hash__ as hash(self.json_repr()), Action instances are hashable only if prefix and action are strings (or otherwise produce a string via json_repr).
- Equality and hashing are value-based and identical to equality/hashing of the json_repr string: two Action instances compare equal iff their json_repr() strings are equal.
- The attributes prefix and action must remain stable while an instance is used as a dict key or set member.

## Lifecycle:
Creation:
- Constructor signature: Action(prefix, action)
    - Required positional args: prefix (str), action (str).
    - No validation is performed; the constructor simply stores the provided values to self.prefix and self.action.
    - If callers pass non-string values, errors will occur later when json_repr or BaseElement hashing/comparisons are used.

Usage (typical sequence):
1. Instantiate: a = Action("s3", "GetObject")
2. Inspect canonical form: a.json_repr() -> "s3:GetObject"
3. Compare or hash: use ==, !=, hash(a), set/dict operations (valid only if json_repr returns a stable hashable value)
4. Derive related candidates: a.matching_actions(allowed_prefixes=None) — will:
    - compute stem = a._base_action()
    - construct candidate Action objects by concatenating each prefix in allowed_prefixes (defaults to BASE_ACTION_PREFIXES) with stem and stem + "s"
    - return only those candidates that are present in known_iam_actions(a.prefix) and are not the original action instance

Destruction:
- No special cleanup required. There is no context-manager protocol or close() method.

Sequencing constraints:
- No method requires a strict call order beyond constructing an instance before invoking its methods.
- Methods that rely on external data (matching_actions) may raise exceptions originating from known_iam_actions (file I/O and parsing errors) — callers should be prepared to handle those.

## Method Map:
graph LR
    init[__init__(prefix, action)] --> setstate[set attributes: prefix, action]
    setstate --> json[json_repr() -> "prefix:action"]
    setstate --> base[_base_action() -> normalized stem]
    base --> match[matching_actions(allowed_prefixes)]
    match --> known[call known_iam_actions(self.prefix)]
    json --> base
    note[Note: equality/hash/repr are provided by BaseElement and depend on json_repr()] --> json

## Behavior details and edge cases:
- json_repr():
    - Returns ':'.join([self.prefix, self.action]) — always a string if both attributes are strings.
    - If either attribute is not a str, Python's str.join will raise TypeError. Callers should pass strings.
- _base_action():
    - Iteratively applies re.sub(prefix, "", without_prefix) for each prefix pattern in the global BASE_ACTION_PREFIXES list (treats those entries as regex patterns). This removes occurrences matched by the regexes from the action name.
    - After removing prefixes, removes a single trailing "s" if present (re.sub(r"s$", "", ...)).
    - Returns the resulting string which may be empty or unchanged if no patterns match.
    - Edge cases: if BASE_ACTION_PREFIXES entries are not valid regex strings, re.sub may raise re.error (rare if constants are correct).
- matching_actions(allowed_prefixes):
    - If allowed_prefixes is falsy (None, empty), the method uses the global BASE_ACTION_PREFIXES as the list of prefixes to attempt.
    - It generates two candidate forms per allowed prefix:
        1) allowed_prefix + base_action
        2) allowed_prefix + base_action + "s"
      Each candidate is constructed as an Action instance using the same prefix as self.prefix (i.e., Action(prefix=self.prefix, action=...)).
    - It filters candidates by membership in known_iam_actions(self.prefix) — known_iam_actions returns a list of Action objects for the provided prefix; membership uses Action equality (json_repr), so the candidate must have an identical json_repr to one returned by known_iam_actions(self.prefix).
    - The method excludes the original Action instance from the returned list.
    - Exceptions that can surface:
        - Any exception raised by known_iam_actions (FileNotFoundError, OSError, UnicodeDecodeError, AttributeError, IndexError, TypeError) will propagate.
        - If BASE_ACTION_PREFIXES is missing or malformed, matching_actions may behave incorrectly or raise.

## Raises:
- __init__:
    - Does not explicitly raise. However, improper types (non-str) will cause TypeError later when json_repr() or hashing operations are invoked.
- json_repr:
    - TypeError if prefix or action are not strings (because str.join requires str items).
- _base_action:
    - re.error if an item in BASE_ACTION_PREFIXES contains an invalid regular expression.
- matching_actions:
    - Propagates exceptions raised by known_iam_actions (see known_iam_actions documentation): FileNotFoundError, OSError, UnicodeDecodeError, AttributeError, IndexError, TypeError, etc.
    - If allowed_prefixes contains non-iterable or unexpected types, the list/generation may raise TypeError.

## Example:
- Typical usage:
    1) Creation and canonical form:
        a = Action("s3", "GetObject")
        a.json_repr()  # -> "s3:GetObject"
    2) Compare and hash:
        b = Action("s3", "GetObject")
        a == b  # True (value-based equality via json_repr)
        {a, b}  # set will contain one element (hash based on json_repr)
    3) Generate related known actions (may raise if repository file missing):
        # allowed_prefixes omitted -> defaults to BASE_ACTION_PREFIXES
        related = a.matching_actions(None)
        # related is a list of Action instances that are present in known_iam_actions("s3")
    4) Notes:
        - Prefer passing strings for prefix and action.
        - If matching_actions is used, be prepared to catch file/parse errors from known_iam_actions.

### `trailscraper.iam.Action.__init__` · *method*

## Summary:
Initializes an Action value object by storing the provided IAM service prefix and action name on the instance, establishing the object's minimal state used by equality, hashing, and other helpers.

## Description:
Known callers and invocation context:
- Parsers or deserializers that convert textual IAM identifiers into objects (e.g., parsing "s3:GetObject").
- Policy validation, normalization, auto-completion routines that create Action instances before calling helpers like json_repr(), _base_action(), or matching_actions().
- Tests and tooling that construct Action objects for comparisons, set membership, or candidate generation.

Lifecycle stage:
- Called at object creation time; this is the primary setup step for an Action instance and must precede any use of instance methods or hashing.

Why this is a separate method:
- Keeps construction trivial and explicit for a lightweight value object; separates state assignment from other behaviors (normalization, matching, and serialization) which live in other methods. This aligns with the class's role as a stable value holder without performing validation or side effects during construction.

## Args:
    prefix (str): Required. The IAM service/namespace portion that appears before ':' (example: "s3", "ec2").
        - Allowed values: any string. Recommended to be a stable, immutable identifier for reliable hashing and comparisons.
        - Default: none (positional required).
    action (str): Required. The action name portion that appears after ':' (example: "GetObject", "ListBuckets").
        - Allowed values: any string. Recommended to be a stable, immutable action name.
        - Default: none (positional required).

## Returns:
    None
    - The constructor returns None (standard Python __init__ behavior). The effect is observable via the mutated instance attributes.

## Raises:
    - None explicitly raised by this method.
    - Indirect/Deferred errors:
        * If non-string values are supplied, this constructor will not raise immediately, but later calls to methods that expect strings (e.g., json_repr(), hashing via BaseElement, or regex operations in _base_action()) may raise TypeError, AttributeError, or other exceptions.

## State Changes:
Attributes READ:
    - None (the method does not read any pre-existing attributes on self).

Attributes WRITTEN:
    - self.action: set to the provided action argument.
    - self.prefix: set to the provided prefix argument.

## Constraints:
Preconditions:
    - The caller should provide two positional arguments: prefix and action.
    - For reliable downstream behavior (json_repr, hashing, normalization), both arguments should be strings. If callers pass non-string values, behavior is undefined until methods expecting strings are invoked.

Postconditions:
    - After return, self.prefix references the provided prefix value and self.action references the provided action value.
    - The instance is usable with other Action methods (subject to the types/values provided).
    - No validation guarantees are made (e.g., format "prefix:action" is not enforced here).

## Side Effects:
    - None. The constructor performs no I/O, does not call external services, and does not mutate objects outside the Action instance.
    - No logging, file, or network activity occurs as part of initialization.

### `trailscraper.iam.Action.json_repr` · *method*

## Summary:
Returns the IAM-style string representation of this Action by joining the prefix and action parts with a colon (produces "prefix:action"). This provides the canonical string used when serializing actions into IAM policy structures.

## Description:
Known callers:
    - No direct call sites for Action.json_repr were found in the scanned codebase. The method is intended to be used by serialization routines that convert IAM element objects into primitive Python types (strings/dicts) when building a PolicyDocument for JSON output — for example, when a higher-level serializer collects action values to include under an IAM Statement or PolicyDocument.

Lifecycle / pipeline stage:
    - Invoked during policy serialization or any conversion step that needs the canonical textual form of an Action object (the stage that produces data ready for json.dumps or for comparison against known IAM action strings).

Why this is a separate method:
    - Encapsulates the canonical textual representation of an Action in one place so callers (serializers, comparators, tests) need not reimplement the "prefix:action" concatenation. It also provides a BaseElement-defined interface (BaseElement.json_repr) so different IAM element types can present a uniform serialization API.

## Args:
    None.

## Returns:
    str: A string formed by concatenating self.prefix and self.action with a single colon separator, equivalent to ':'.join([self.prefix, self.action]).
    Examples:
        - If self.prefix == "s3" and self.action == "GetObject", returns "s3:GetObject".
        - If self.prefix == "" and self.action == "List", returns ":List".
    Edge cases:
        - If either attribute contains additional colons, those remain unchanged (e.g., prefix "a:b" and action "C" -> "a:b:C").
        - If either attribute is an empty string, the returned string will contain an empty portion on that side of the colon.

## Raises:
    TypeError: If either self.prefix or self.action is not a str (since ':'.join expects string elements), a TypeError will be raised at runtime.
    Notes:
        - The method does not explicitly validate types or values; callers should ensure attributes are strings when necessary.

## State Changes:
Attributes READ:
    - self.prefix
    - self.action

Attributes WRITTEN:
    - None (this method does not modify object state)

## Constraints:
Preconditions:
    - The instance must have attributes prefix and action accessible (as assigned by Action.__init__).
    - Preferably both attributes should be str for meaningful output; otherwise a TypeError occurs.

Postconditions:
    - No state on self is modified.
    - The method returns a string joining prefix and action with a single colon if both attributes are str.

## Side Effects:
    - None. The method performs no I/O, external service calls, or mutations of objects outside self.

### `trailscraper.iam.Action._base_action` · *method*

## Summary:
Return the canonical, singular "base" verb for this Action by removing any configured action-prefix patterns and a trailing plural "s", without mutating the object.

## Description:
Known callers:
- Action.matching_actions: called when constructing potential matching Action objects to derive the canonical verb before re-applying allowed prefixes and optional pluralization. This method is invoked during the permissions/action matching phase where the code enumerates related IAM actions for comparison.

Why this is a separate method:
- The logic for removing configured prefixes and singularizing the action is reused by matching_actions and may be needed wherever a normalized action-form is required. Centralizing this behavior avoids duplication and keeps the prefix/ plural-stripping rules in one place so they can be updated consistently.

Behavior summary:
- Iterates through the module-level BASE_ACTION_PREFIXES sequence and applies a regex substitution for each prefix pattern against self.action, removing all matches of that prefix pattern.
- After removing configured prefixes, removes a single trailing lowercase "s" if present (using a regex that matches an 's' at the end of the string).
- Returns the resulting string (the base action). The Action instance is not modified.

## Args:
- self: Instance of Action (method uses self.action; no external args).

## Returns:
- str: The normalized base action (singular form) derived from self.action after removing any substrings that match any pattern in BASE_ACTION_PREFIXES and then removing a trailing 's' if present.
- Possible edge-case return values:
    - An empty string if self.action consists entirely of removed prefix patterns and optionally the trailing 's'.
    - The original string (possibly unchanged) if no prefixes matched and it did not end with 's'.

## Raises:
- TypeError: If self.action is not a string-like object acceptable to re.sub (for example, None or a non-string type), re.sub will raise a TypeError when attempting to process it.
- re.error: If any regex pattern in BASE_ACTION_PREFIXES is an invalid regular expression, re.sub may raise re.error when that pattern is used.
- Note: These exceptions originate from the underlying re.sub calls; the method does not explicitly catch them.

## State Changes:
- Attributes READ:
    - self.action
- Attributes WRITTEN:
    - None (the method does not modify any attributes on self)

## Constraints:
- Preconditions:
    - self.action must be a string (or at least a type accepted by re.sub as the input text).
    - BASE_ACTION_PREFIXES must be an iterable of regex patterns/strings; each element should be a valid regex pattern to avoid re.error.
- Postconditions:
    - The returned value is a str representing the action with all occurrences of the configured prefix patterns removed and with any single trailing 's' removed.
    - self.action and other object state remain unchanged.

## Side Effects:
- No I/O or external service calls.
- Calls into the Python standard library re.sub for regex-based substitutions.
- Depends on the module-level name BASE_ACTION_PREFIXES; changing that global will change the normalization behavior.

## Implementation notes / important details to preserve when reimplementing:
- Use regex substitution (re.sub) for each pattern in BASE_ACTION_PREFIXES to allow flexible prefix patterns (anchors, optional pieces, separators).
- Do not restrict prefix removal to the start of the string unless the patterns themselves include anchors; the current implementation removes every match of each pattern.
- Plural handling is minimal: only removes a single lowercase "s" at the end of the processed string (pattern r"s$"). It does not handle irregular plurals or multi-letter plural suffixes.

### `trailscraper.iam.Action.matching_actions` · *method*

## Summary:
Return a list of known Action objects (same prefix) that correspond to alternate allowed-prefix variants of this Action's base operation, excluding the Action itself.

## Description:
- Known callers:
    - No direct callers were found in the provided repository snapshot.
    - Typical callers and contexts: policy validation or normalization pipelines, autocompletion/UIs that suggest equivalent IAM actions across different service prefixes, and test utilities that need to enumerate canonical actions related to a given Action.
    - Lifecycle stage: invoked when you have an Action instance and need to find other, canonical Action objects (from repository-maintained canonical data) that represent the same base operation but with different action-prefix variants (for example, singular vs plural forms or different namespace prefixes allowed by configuration).

- Why this is a separate method:
    - Encapsulates the matching/mapping logic (compute a base action, generate candidate actions across allowed prefixes and singular/plural forms, filter by canonical known actions and exclude self) so callers need not reimplement file-reading, parsing, or comparison semantics.
    - Keeps the responsibility of producing canonical alternatives local to the Action type and leverages the central known_iam_actions source of truth for validation.

## Args:
    allowed_prefixes (iterable[str] or None):
        - Description: An iterable of string action-prefixes (each typically a prefix string used to build an action name) to consider when generating candidate actions.
        - Behavior:
            * If falsy (None, empty list, empty tuple, etc.), the method uses the global BASE_ACTION_PREFIXES as the list of prefixes to try.
            * Each element must be a string suitable for concatenation with the base action (the code performs action_prefix + base_action). If an element is not a string, a TypeError will be raised at runtime.
        - Examples of valid values: None, ["iam:", "s3:"], BASE_ACTION_PREFIXES.

## Returns:
    list[Action]:
        - A list of Action instances drawn from known_iam_actions(self.prefix) that match the generated candidates.
        - Each returned Action:
            * Has .prefix equal to self.prefix (because known_iam_actions is queried with self.prefix and returns Actions with that prefix).
            * Has an .action value equal to action_prefix + base_action OR action_prefix + base_action + "s" for some action_prefix in allowed_prefixes (or in BASE_ACTION_PREFIXES when allowed_prefixes is falsy).
        - Ordering: The ordering of returned items is unspecified (depends on known_iam_actions and underlying grouping); callers should not rely on a stable order.
        - Edge cases:
            * If no generated candidate matches the canonical set, an empty list is returned.
            * The method always excludes self from the returned list even if self appears among the canonical known actions.

## Raises:
    - Propagated exceptions from known_iam_actions(self.prefix):
        * FileNotFoundError, OSError, UnicodeDecodeError (file I/O/decoding from underlying all_known_iam_permissions).
        * AttributeError, IndexError (possible parsing errors in _parse_action invoked internally).
        * TypeError (if grouping/lookup expects different types).
    - TypeError raised by this method's own list comprehensions if:
        * allowed_prefixes is truthy but not iterable (for action_prefix in allowed_prefixes will raise TypeError).
        * an action_prefix element is not a string (concatenation action_prefix + base_action() raises TypeError).
    - Any exception raised by self._base_action() will propagate (for example, if self.action is malformed for the pattern removals done in _base_action).

## State Changes:
- Attributes READ:
    - self.prefix (used to construct candidate Action objects and passed to known_iam_actions)
    - self.action (read indirectly by calling self._base_action())
- Attributes WRITTEN:
    - None. The method does not modify this Action instance or any other in-place state.

## Constraints:
- Preconditions:
    - self.prefix must be a string acceptable to known_iam_actions (the function expects a string prefix and will return [] if the prefix is unknown).
    - self.action must be a string formatted such that self._base_action() can derive the base operation (Action._base_action strips known BASE_ACTION_PREFIXES and a trailing "s").
    - allowed_prefixes, if provided and truthy, must be an iterable of strings.
    - The global BASE_ACTION_PREFIXES must be defined (used when allowed_prefixes is falsy).
- Postconditions:
    - No mutation to the Action instance or external state (other than any file reads performed by known_iam_actions).
    - The return value is a list (possibly empty) of Action objects drawn from the canonical known_iam_actions for this Action's prefix; none of the returned Actions is the original self.

## Side Effects:
- Indirect read-only file I/O: calls known_iam_actions(self.prefix), which in turn reads the repository canonical action list (all_known_iam_permissions) and parses it. This can trigger file I/O and its associated errors.
- No network I/O, no logging, and no writes to disk or external resources are performed by this method itself.
- Creates short-lived Action objects (potential_matches) but does not persist them beyond the returned list.

## Implementation notes (reimplementation guidance):
- Steps to reimplement:
    1. Compute base_action by calling the Action._base_action() helper on self (it should remove any known prefixes and a trailing 's').
    2. Determine the prefixes to try:
        - If allowed_prefixes is falsy, use BASE_ACTION_PREFIXES (global constant).
        - Otherwise use the provided iterable.
    3. Generate candidate Action objects:
        - For each action_prefix in prefixes: create Action(prefix=self.prefix, action=action_prefix + base_action)
        - Additionally create candidates with a trailing "s": action_prefix + base_action + "s"
    4. Query the canonical set: call known_iam_actions(self.prefix) to obtain the list of canonical Action objects for this prefix.
    5. Filter candidates:
        - Keep candidates that are present in the canonical list (membership uses Action equality semantics).
        - Exclude any candidate equal to self.
    6. Return the filtered list.
- Equality semantics:
    - The membership test (potential_match in known_iam_actions(self.prefix)) depends on Action equality semantics (Action.__eq__). Ensure Action equality compares the same fields used in known_iam_actions parsing (typically .prefix and .action).
- String handling:
    - Because known_iam_actions may return Actions produced from raw file lines, be aware of possible trailing CR characters or empty lines in the canonical source; equality and comparisons should account for the exact string values produced by the parsing pipeline.

## `trailscraper.iam.Statement` · *class*

## Summary:
Represents a single IAM policy statement grouping an Effect (e.g., "Allow"/"Deny"), a list of Action objects, and a list of Resource identifiers; provides JSON serialization, merging of statements with identical effects, and ordering behavior.

## Description:
This class models one statement from an IAM-style policy document. Instantiate when you need a structured, comparable representation of a statement containing:
- Effect: a string describing whether actions are allowed or denied (commonly "Allow" or "Deny").
- Action: a list of action objects (each must expose a json_repr() method returning a stable string representation).
- Resource: a list of resource identifiers (strings, typically ARNs).

Typical instantiation scenarios:
- Converting parsed policy inputs into normalized statements for sorting, deduplication, or merging.
- Producing a JSON-compatible representation for policy output or comparison.
- Combining multiple statements with identical Effect into a single statement via merge().

Known callers/factories:
- Any higher-level policy builder or parser that constructs policies by assembling Statement instances.
- De-duplication/normalization routines that sort, merge, and compare statements.

Motivation and responsibility boundary:
- Statement encapsulates the minimal data and operations needed for statement-level equality, ordering, merging, and JSON serialization. It intentionally does not validate Action or Resource contents beyond the minimal interface/constraints required for its operations (see State and Raises sections). Validation of domain semantics (e.g., correct ARN format) is left to callers.

## State:
Attributes (public by design):

- Action
  - Type: list of elements; each element must implement a method json_repr() -> str.
  - Valid values: a finite sequence of objects that are hashable (so they can be placed in a Python set) and comparable for equality.
  - Invariant: Action is a list (sequence) and when compared or merged the elements' equality and hash semantics are relied upon.

- Effect
  - Type: str
  - Valid values: any string; callers normally use "Allow" or "Deny".
  - Invariant: Effect is immutable in the sense that operations that combine statements require identical Effect values.

- Resource
  - Type: list[str]
  - Valid values: sequence of strings (e.g., ARNs). Elements must be hashable (strings are) and comparable.
  - Invariant: Resource is a list (sequence) of string identifiers.

Class invariants:
- For any Statement instance s: s.json_repr() returns a dict with three keys: 'Action', 'Effect', 'Resource', matching the current attributes.
- merge(other) assumes self.Effect == other.Effect and produces a new Statement with deduplicated, sorted Action and Resource lists.
- Ordering and equality behavior assume Action elements are comparable for equality and that json_repr() returns deterministic strings.

Notes on mutability:
- Attributes are assigned directly in __init__; callers should treat Statement instances as simple data containers. Methods merge and json_repr do not mutate self; merge returns a new Statement.

## Lifecycle:
Creation:
- Instantiate by calling Statement(Action=<list>, Effect=<str>, Resource=<list>).
  - Example conceptual call: Statement(Action=[action1, action2], Effect='Allow', Resource=['arn:...'])
  - All three parameters are required; there are no defaults.

Usage:
- Typical sequence:
  1. Create Statement instances from parsed or constructed action/resource data.
  2. Use json_repr() to obtain a JSON-serializable dict view of the statement.
  3. Use merge(other) to combine two statements with identical Effect into a single statement that contains unique Actions and Resources.
  4. Use the ordering defined by __lt__ (Python's <) to sort lists of Statement instances deterministically.

- Method ordering/requirements:
  - merge(other) requires other to be a Statement and have the same Effect.
  - __lt__ (less-than) may be used whenever deterministic ordering of statements is required; it uses Effect, Action list summary, then concatenated Resources to compare.

Destruction / cleanup:
- No explicit cleanup required. Statement instances hold only Python built-in data references; no context manager or close() is necessary.

## Method Map:
flowchart LR
    A[__init__(Action, Effect, Resource)] --> B[json_repr()]
    A --> C[merge(other)]
    C --> D[create deduped Action list (uses action.json_repr() for sort key)]
    C --> E[create deduped Resource list]
    A --> F[__lt__(other)]
    F --> G[compare Effect]
    F --> H[compare Action via __action_list_strings()]
    H --> I[__action_list_strings() uses action.json_repr()]
    F --> J[compare concatenated Resources]

(Explanation: instantiation leads to three primary operations — serialization (json_repr), merging (merge), and ordering ( __lt__ which may call __action_list_strings). merge constructs sorted, deduplicated lists; __lt__ performs a three-stage comparison.)

## Methods (behavioral summary)
- __init__(Action, Effect, Resource)
  - Stores the provided arguments on the instance without additional validation.
  - Caller responsibility: supply Action as list-like, Effect as string, Resource as list of strings.

- json_repr()
  - Returns a dict with keys 'Action', 'Effect', 'Resource' whose values are the instance attributes. Intended to be JSON-serializable when Action and Resource are themselves JSON-serializable (Action elements should be objects where their json_repr() consumer output is used elsewhere; in this implementation Action attribute remains a list of objects).

- merge(other)
  - Combines two statements that have the same Effect into a new Statement.
  - Behavior:
    - If self.Effect != other.Effect -> raises ValueError (see Raises).
    - Builds the union of self.Action and other.Action:
      - Concatenates the two lists, converts to a set to deduplicate, then sorts the unique actions using key= lambda action: action.json_repr().
      - The resulting actions are placed in a list in deterministic order.
      - Requirements: Action elements must be hashable and expose json_repr() -> str.
    - Builds the union of self.Resource and other.Resource:
      - Concatenates, deduplicates via set, and sorts lexicographically; result is a list.
      - Requirements: Resource elements must be hashable (strings suffice).
    - Returns a new Statement(Effect=<same as inputs>, Action=<sorted unique list>, Resource=<sorted unique list>).
  - Does not mutate either operand.

- __action_list_strings()
  - Internal helper returning a single string obtained by joining the json_repr() strings of each Action element with a hyphen ("-").
  - Used to produce a stable comparison key for Action lists.

- __lt__(other)
  - Defines less-than ordering used by sorting algorithms.
  - Comparison steps (in order):
    1. Compare Effect strings lexicographically; if different, effect strings determine ordering.
    2. If Effects equal but Action lists differ (list equality check), compare the __action_list_strings() outputs lexicographically.
    3. If both Effect and Action are equal, compare concatenated Resource strings (join of Resource list elements) lexicographically.

## Raises:
- merge(other)
  - Raises ValueError if other.Effect is not equal to self.Effect with message "Trying to combine two statements with differing effects: {self.Effect} {other.Effect}".
- __init__
  - Does not explicitly raise exceptions, but callers may encounter TypeError or AttributeError later if they pass Action elements lacking json_repr() or non-hashable/unexpected types, since merge() and sorting assume these interfaces.

Edge-case notes:
- If Action elements are not hashable (i.e., their __hash__ is None), the set(...) operation in merge() will raise a TypeError. To avoid this, ensure Action elements have stable hashing (default object identity hashing is acceptable) or use immutable/value-like action objects.
- If Action.json_repr() returns non-deterministic values across calls, sorting and equality comparisons may behave inconsistently; json_repr() should be deterministic.
- If Resource contains non-string elements, sorting behavior depends on Python's comparison rules and may raise TypeError in mixed-type lists on Python 3; prefer strings.

## Example:
- Preconditions: You have action-like objects that implement json_repr() -> str (for example, an object representing "s3:GetObject" whose json_repr returns "s3:GetObject").

- Steps (conceptual):
  1. Create two statements with the same Effect but different actions/resources:
     - s1: Action = [actionA], Effect = "Allow", Resource = ["arn:aws:s3:::bucket1/*"]
     - s2: Action = [actionB], Effect = "Allow", Resource = ["arn:aws:s3:::bucket2/*"]
  2. Merge them:
     - merged = s1.merge(s2)
     - Result: merged.Action is a sorted list of unique actions [actionA, actionB] (sorted by action.json_repr()), merged.Resource is a sorted list of unique resources.
  3. Serialize for output:
     - payload = merged.json_repr()  # {'Action': [...], 'Effect': 'Allow', 'Resource': [...]}
  4. Sort a collection of Statement instances:
     - statements_sorted = sorted(list_of_statements)  # relies on __lt__ ordering

(There is no resource cleanup required.)

### `trailscraper.iam.Statement.__init__` · *method*

## Summary:
Initializes a Statement instance by storing the provided Action, Effect, and Resource values on the object.

## Description:
This is the initializer (constructor) for a Statement-like object. When a caller instantiates the class, this method runs once to assign the three core fields that represent an access-control statement. It exists as a separate method (the class constructor) to clearly encapsulate object construction and to make later code that builds, serializes, or inspects statement objects rely on a stable set of attributes.

Known callers and context:
- Invoked implicitly whenever the Statement class is instantiated (e.g., Statement(Action, Effect, Resource)). There are no callers visible inside this method; callers are any code paths that create Statement objects as part of building IAM-like statements or policies.
- Typical lifecycle stage: object construction / model population before the Statement is used for policy composition, validation, serialization, or evaluation.

Why this logic is separate:
- Assignment of core attributes belongs in the constructor to ensure newly created instances always contain the three required fields. Placing this logic in __init__ centralizes instance initialization, keeps instantiation atomic, and avoids duplicating attribute initialization elsewhere.

## Args:
    Action: Any
        The value provided for the statement's actions. The constructor stores it as self.Action without validation. Callers typically supply a string, list, or other structure representing permitted actions, but the method accepts any value.
    Effect: Any
        The value provided for the statement's effect (for example, 'Allow' or 'Deny' in common IAM models). The constructor stores it as self.Effect without validation.
    Resource: Any
        The value provided for the statement's resource(s). The constructor stores it as self.Resource without validation.

## Returns:
    None
        As a constructor, it does not return a value; it initializes the instance in-place.

## Raises:
    None
        This method does not raise any exceptions itself. It performs straightforward attribute assignments and will only raise if Python raises (e.g., out-of-memory), which is not specific to this method.

## State Changes:
Attributes READ:
    - None

Attributes WRITTEN:
    - self.Action: assigned the provided Action argument
    - self.Effect: assigned the provided Effect argument
    - self.Resource: assigned the provided Resource argument

## Constraints:
Preconditions:
    - There are no enforced preconditions within this method. Callers should ensure the provided values are appropriate for downstream consumers (for example, using strings like 'Allow'/'Deny' for Effect or string/list forms for Action/Resource) because no validation occurs here.

Postconditions:
    - After this call, the instance will have three attributes set: Action, Effect, and Resource, each holding exactly the value passed in.

## Side Effects:
    - The method mutates only the instance (self) by creating or overwriting the three attributes listed above.
    - There are no I/O actions, external service calls, or mutations to objects outside of self performed by this method.

### `trailscraper.iam.Statement.json_repr` · *method*

## Summary:
Returns a plain Python dictionary view of the Statement containing the Action, Effect, and Resource fields; does not modify the Statement instance.

## Description:
This method produces a canonical mapping of the Statement object's three public fields into a dictionary with keys 'Action', 'Effect', and 'Resource'. It is intended to be used whenever the Statement needs to be converted into a JSON-serializable representation or included in policy documents. No callers are shown in the provided snippet; typical call sites include serialization routines or code that aggregates multiple Statement objects into a larger policy structure.

This logic is placed in its own method to centralize and standardize the mapping from object attributes to the dictionary keys, avoiding duplication of the mapping logic across the codebase and making it easier to change the exported shape in one place.

## Args:
    None

## Returns:
    dict
        A new dictionary with exactly three keys:
        - 'Action': value taken directly from self.Action
        - 'Effect': value taken directly from self.Effect
        - 'Resource': value taken directly from self.Resource

        The values are returned verbatim (their types are whatever the corresponding attributes hold). The method does not enforce or convert types; callers that require JSON serialization should ensure values are JSON-serializable.

## Raises:
    AttributeError
        If any of self.Action, self.Effect, or self.Resource does not exist on the object, Python will raise AttributeError when attempting to access the missing attribute.

## State Changes:
    Attributes READ:
        - self.Action
        - self.Effect
        - self.Resource

    Attributes WRITTEN:
        - None (the method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - The Statement instance must have the attributes Action, Effect, and Resource accessible (they can be instance attributes or provided via properties).
        - If the caller intends to JSON-serialize the returned dictionary, the attribute values should be JSON-serializable (this method does not perform serialization).

    Postconditions:
        - Returns a dict mapping the three keys to the current values of the corresponding attributes.
        - The Statement instance remains unchanged.

## Side Effects:
    - None. The method performs no I/O, makes no external calls, and does not mutate objects outside of returning a new dictionary.

### `trailscraper.iam.Statement.merge` · *method*

## Summary:
Combine two compatible statement objects into a new statement containing the union of their actions and resources while preserving the original effect; does not mutate either operand.

## Description:
Known callers and contexts:
- Policy normalization or simplification routines that coalesce multiple statements with the same effect into a single consolidated statement.
- Any code that deduplicates or aggregates statements produced by parsers or builders (e.g., after parsing policy fragments or when merging policies).
- Test utilities that combine statement fixtures.

Lifecycle stage:
- Invoked during a consolidation/normalization step after individual Statement objects have been parsed or constructed and before final serialization or comparison.

Why this is a separate method:
- Merging statements is a distinct, reusable operation with explicit precondition (matching Effect) and non-trivial behavior (union, deduplication, deterministic ordering). Keeping it as a separate method promotes clarity, avoids code duplication wherever statements need combining, and ensures the same deterministic merge semantics are applied everywhere.

## Args:
    other (Statement): Another Statement instance to merge with self.
        - Required.
        - Expected properties on the argument:
            * other.Effect: comparable to self.Effect (typically a string such as "Allow" or "Deny").
            * other.Action: a sequence (e.g., list) of Action instances; each Action must provide json_repr() for ordering and equality.
            * other.Resource: a sequence (e.g., list) of resource strings.

Notes on types:
- self and other are both instances of Statement (the caller is expected to call this as self.merge(other)).
- Action values are value-objects whose equality and hashing are determined by their json_repr() string.

## Returns:
    Statement: A newly-constructed Statement instance with:
        - Effect: the shared Effect from self and other (exactly self.Effect).
        - Action: a list of unique Action objects formed from the concatenation of self.Action and other.Action, deduplicated using Python set semantics, and deterministically sorted by each Action.json_repr() value.
        - Resource: a list of unique resource items formed from concatenation of self.Resource and other.Resource, deduplicated using Python set semantics, and sorted using Python's default ordering for the resource items (commonly lexicographic for strings).

Edge-case returns:
- If both inputs have empty Action or Resource lists, the returned Statement will contain empty lists for those fields.
- The method always returns a new Statement object; it never returns None.

## Raises:
    ValueError: if self.Effect != other.Effect. The message contains both effect values (e.g., "Trying to combine two statements with differing effects: Allow Deny").
Potential runtime exceptions (not explicitly raised by the method but possible if inputs violate expected types):
    AttributeError: if Action items do not implement json_repr().
    TypeError: if self.Action or other.Action are not concatenable sequences, or if resource items are not comparable/sortable (e.g., non-homogeneous types that sorted() cannot compare).
    Any exception raised by Statement constructor if it validates/handles its inputs differently in other contexts (not present in the shown ctor).

## State Changes:
Attributes READ:
    - self.Effect
    - self.Action
    - self.Resource
    - other.Effect
    - other.Action
    - other.Resource

Attributes WRITTEN:
    - None on self or other. The method constructs and returns a new Statement; it does not mutate either operand.

## Constraints:
Preconditions:
    - other must be a Statement-like object with attributes Effect, Action, Resource.
    - self.Effect and other.Effect must be equal (same value and type) otherwise ValueError is raised.
    - Elements of self.Action and other.Action must be Action-like objects exposing json_repr() and supporting equality/hash semantics consistent with json_repr().
    - Elements of self.Resource and other.Resource must be values that can be hashed (for deduplication via set) and sorted (for deterministic ordering). In typical usage, resource items are strings.

Postconditions:
    - The returned Statement.Effect equals self.Effect (and other.Effect).
    - Returned Action list equals the set-union of the input Action sequences, with deterministic ordering by action.json_repr().
    - Returned Resource list equals the set-union of the input Resource sequences, with deterministic ordering by the default sorted() behavior for those items.
    - self and other remain unchanged.

## Side Effects:
    - None: there is no I/O, no network calls, and no mutation of objects outside the method's local scope.
    - The only observable effect is construction and return of a new Statement object.

### `trailscraper.iam.Statement.__action_list_strings` · *method*

## Summary:
Return a single hyphen-separated string formed by joining the canonical JSON-style representations of every item in the statement's Action list; does not modify the object.

## Description:
This private helper produces a deterministic string representation of the Statement's Action collection by calling json_repr() on each element and joining the results with "-" as the separator.

Known callers and call sites:
- Statement.__lt__: used when ordering/comparing Statement instances (e.g., during sorting) to compare two Action lists deterministically.
- Typical lifecycle: invoked during comparison/sorting operations on Statement objects (ordering phase of algorithms that sort or deduplicate statements).

Rationale for a dedicated method:
- The join-and-map logic is used specifically for ordering comparisons and is isolated to provide a single, testable implementation point (avoids duplicating the list-to-string conversion logic in multiple comparison locations and ensures consistent ordering semantics).

## Args:
None.

## Returns:
str
- A single string consisting of the json_repr() output of each element in self.Action concatenated with "-" between entries.
- If self.Action is an empty iterable, returns an empty string "".
- The return value is deterministic for a given ordering of self.Action.

## Raises:
- AttributeError: if any item in self.Action does not have a callable json_repr attribute (e.g., an element is a plain str or other object without json_repr).
- TypeError: if self.Action is not iterable, or if one or more json_repr() calls return non-str objects (join requires all elements to be str), or if items are bytes while others are str.
- Any exception raised by an element's json_repr() implementation will propagate unchanged (for example, if json_repr itself raises ValueError).

## State Changes:
Attributes READ:
- self.Action

Attributes WRITTEN:
- None (no mutation of self or of items is performed by this method).

## Constraints:
Preconditions:
- self.Action must be an iterable of objects that implement a callable json_repr() method which returns a Python str.
- The order of elements in self.Action is significant; the produced string reflects that order.

Postconditions:
- self remains unchanged.
- The method returns a str as described above (or raises as documented).

## Side Effects:
- No I/O, no external service calls.
- Does not mutate objects outside self (it merely calls json_repr() on each item).
- Note: because the method concatenates with "-", if an element's json_repr() contains "-" itself, the combined string may not be safely reversible by simple splitting; consumers relying on splitting should not assume unique separability.

## Implementation notes and edge cases:
- Because the method is defined with double leading underscores, it is name-mangled and intended to be private to the Statement class.
- Common failure modes:
    - If self.Action is None or another non-iterable, the method will raise TypeError when attempting iteration or when join receives an invalid argument.
    - If some json_repr() return types are not str (e.g., bytes or non-string objects), the join will raise TypeError.
    - If any json_repr() raises an exception, that exception will propagate to the caller.
- Empty-action behavior is explicit: an empty iterable yields the empty string, which is a valid return value used by comparison logic (see __lt__).

### `trailscraper.iam.Statement.__lt__` · *method*

## Summary:
Determines a lexicographic ordering between two Statement objects for sorting purposes; performs no mutation.

## Description:
Implements a three-tier comparison used by Python ordering machinery (e.g., sorted(), list.sort(), and any direct use of '<'):

1. Compare Effect values directly using the '<' operator.
2. If Effects are equal but Action lists differ, compare the string produced by the private helper __action_list_strings() on each Statement.
   - __action_list_strings() implementation: "-".join([a.json_repr() for a in self.Action])
   - This means each Action element's json_repr() value (as produced at runtime) is concatenated with "-" between elements, and those resulting strings are compared with '<'.
3. If Effects and Action lists are equal, compare Resources by concatenating all elements of Resource into a single string using "".join(self.Resource) and comparing those strings with '<'.

Known callers and contexts:
- Implicitly used by Python's sorting and comparison operations when Statement instances are placed in sortable collections.
- Used anywhere the codebase needs a deterministic, repeatable ordering of Statement objects (for canonicalization, deterministic serialization, or deduplication).
- No explicit named callers are present in the Statement class file; the method exists to enable idiomatic use of comparisons and sorting.

Why this method exists separately:
- Centralizes the canonical ordering logic so all code that sorts Statements relies on the same rules.
- Avoids duplicating multi-field comparison logic at each callsite and keeps the behavior testable in one place.

## Args:
    other (Statement): The Statement to compare against. Must provide the same public attributes (Effect, Action, Resource).

## Returns:
    bool: True if self is considered less than other according to the ordering rules described above; otherwise False.

Edge-case return behavior:
    - Always returns a boolean. There are no special sentinel values.
    - The result depends on the runtime types and values of Effect, the string values produced by action.json_repr(), and the elements of Resource.

## Raises:
    AttributeError:
        - If other is missing Effect, Action, or Resource attributes.
        - If an Action element lacks a json_repr() attribute when __action_list_strings() is called.
    TypeError:
        - If Effect values are of types that do not support '<' against each other (e.g., incompatible types).
        - If json_repr() returns non-string values such that "-".join(...) fails.
        - If any element of Resource is not a string, causing "".join(self.Resource) to raise TypeError.
        - If the final comparison operands are of incompatible types for '<'.
    Note: These exceptions originate from the built-in operations used in the comparison (attribute access, method calls, string joins, and '<' operator); the method does not explicitly raise custom exceptions.

## State Changes:
Attributes READ:
    - self.Effect
    - self.Action
    - self.Resource
    - other.Effect
    - other.Action (indirectly, via equality check and __action_list_strings)
    - other.Resource
Attributes WRITTEN:
    - None (method is pure read-only with respect to Statement state)

## Constraints:
Preconditions:
    - other should be a Statement-like object with attributes Effect, Action, and Resource.
    - Effect values must be mutually comparable with '<' (commonly strings).
    - Each element in Action must implement json_repr() and the returned values should be strings (required by "-".join).
    - Elements of Resource must be strings (required by "".join).

Postconditions:
    - Neither self nor other are modified.
    - A boolean value is returned that reflects the lexicographic ordering defined above.

## Behavioral notes and pitfalls:
    - Action list equality (self.Action != other.Action) uses Python's list equality semantics; whether Action elements compare equal depends on those objects' equality implementations. If lists are equal, __action_list_strings() will not be called.
    - The Resource comparison relies on element order and string content; different orderings of Resource elements produce different results even if they contain the same set of values.
    - Determinism of ordering therefore depends on consistent types and stable representations from action.json_repr() and Resource element ordering.
    - No I/O or external service calls are made. The only external call is to each action element's json_repr() method.

## `trailscraper.iam.PolicyDocument` · *class*

## Summary:
Represents an AWS-style IAM policy document containing a Version string and a Statement payload and provides JSON serialization using the IAMJSONEncoder.

## Description:
PolicyDocument is a lightweight value object that holds the two standard fields of an IAM policy document:
- Version: a string that identifies the policy language version (defaults to "2012-10-17").
- Statement: the policy statements (a single statement or collection of statements) in a structure suitable for JSON serialization.

When to instantiate:
- Create PolicyDocument when you need an in-memory representation of an IAM policy to be serialized to JSON (for example, when producing CloudFormation templates, SDK calls, or configuration files).
- Typical callers/factories: policy builders, CloudFormation resource serializers, unit tests that assert policy JSON output.

Responsibility and boundaries:
- Responsibility: hold the canonical policy fields and expose a deterministic JSON-style representation (json_repr) and a convenience method (to_json) for producing pretty-printed JSON using the project’s IAMJSONEncoder.
- Boundary: PolicyDocument intentionally does not validate the structure or semantics of Statement (for example, it does not enforce required keys like "Effect" or "Action"); validation, if required, must be performed by callers prior to construction or by separate validators.

## State:
- Version (str)
  - Type: str
  - Default: "2012-10-17"
  - Constraints: no runtime validation is performed — caller should pass a string compatible with AWS policy version identifiers.
  - Invariant: self.Version is the exact string used as the 'Version' value in json_repr().

- Statement (any JSON-serializable structure or objects supporting json_repr)
  - Type: dict | list | tuple | BaseElement instance | list/dict containing such elements
  - Valid values: Any value that json.dumps(..., cls=IAMJSONEncoder) can serialize:
    - Primitive Python types (str, int, float, bool, None)
    - dict/list/tuple structures composed of primitives
    - Instances of classes implementing json_repr() (these will be encoded by IAMJSONEncoder)
  - Constraints: PolicyDocument does not normalize a single-statement dict into a list or vice-versa. The Statement attribute is stored exactly as supplied and appears unchanged in json_repr().
  - Invariant: self.Statement is the value emitted verbatim under the 'Statement' key in json_repr().

Class invariants:
- json_repr() always returns a dict with exactly two top-level keys: 'Version' and 'Statement', mapped to the instance's Version and Statement attributes respectively.
- Because json_repr() returns a plain dict (an unhashable type), attempting to use PolicyDocument instances in hashed collections (e.g., calling hash() on an instance, using as a dict key, adding to a set) will raise TypeError unless the subclass or caller overrides hashing behavior. This arises from the BaseElement contract: subclasses must ensure json_repr returns a hashable value or must override __hash__.

## Lifecycle:
Creation:
- Constructor signature:
  - PolicyDocument(Statement, Version="2012-10-17")
    - Statement: required. Provide the policy statements (dict, list, or compatible objects).
    - Version: optional. Provide a version string if you need a value other than the default.
- No factory helpers are required by the class itself; callers typically call the constructor directly.

Usage:
- Typical sequence:
  1. Construct: pd = PolicyDocument(Statement=my_statement)
  2. Retrieve the JSON-style representation: pd.json_repr() → {'Version': pd.Version, 'Statement': pd.Statement}
  3. Serialize to JSON text for persistence or API consumption: pd.to_json() (pretty-printed, sorted keys)
- Ordering and sequencing: There is no required method-call order, but to_json() delegates to json.dumps(...) which will attempt to serialize pd.json_repr() and may recursively call IAMJSONEncoder.default for nested non-serializable objects that implement json_repr().

Destruction / cleanup:
- No explicit cleanup or context-manager support. Instances hold only in-memory data and have no external resources to release.

## Method Map:
flowchart LR
    A[__init__(Statement, Version)] --> B[json_repr()]
    B --> C[to_json()]
    C --> D[json.dumps(obj=json_repr(), cls=IAMJSONEncoder, indent=4, sort_keys=True)]
    D --> E{Encoder needs to serialize nested custom objects?}
    E -- yes --> F[IAMJSONEncoder.default calls nested_object.json_repr() -> returns serializable form]
    E -- no --> G[Standard JSON encoding completes]
    note[Important: json_repr() returns a dict (unhashable) — using hash() on instances will raise TypeError] --> B

## Methods (behavioral summary)
- __init__(self, Statement, Version="2012-10-17")
  - Purpose: initialize a PolicyDocument with the given Statement and Version.
  - Inputs:
    - Statement: required; stored verbatim on the instance.
    - Version: optional; defaults to "2012-10-17".
  - Behavior: stores parameters on self.Version and self.Statement without validation or transformation.

- json_repr(self)
  - Purpose: return the canonical JSON-style representation used by serializers and by BaseElement semantics.
  - Returns: dict with keys:
    - 'Version' -> str (self.Version)
    - 'Statement' -> the raw Statement value (self.Statement)
  - Notes: the returned dict is suitable for json.dumps but is unhashable.

- to_json(self)
  - Purpose: produce a pretty-printed JSON string of the policy document.
  - Behavior:
    - Calls json.dumps(self.json_repr(), cls=IAMJSONEncoder, indent=4, sort_keys=True)
    - Uses IAMJSONEncoder to allow nested objects that implement json_repr() to be encoded.
  - Output: str containing formatted JSON.

## Raises:
- __init__:
  - No explicit exceptions are raised by the constructor. It will accept any Python value for Statement and Version and simply store them.
- json_repr:
  - Does not raise under normal operation (it constructs and returns a dict).
- to_json:
  - May raise json.JSONEncodeError / TypeError (depending on Python version) if any value inside the representation is not JSON-serializable and cannot be handled by IAMJSONEncoder.
  - If a nested object implements json_repr but that method raises, the exception will propagate out of to_json.
- Hashing-related errors:
  - Because json_repr returns a dict (unhashable), calling hash(pd) or using an instance in a hashed collection will raise TypeError unless a subclass overrides __hash__ or the caller converts to a hashable representation.

## Example:
# Typical creation with a list of statement dicts
stmt = [
    {
        "Effect": "Allow",
        "Action": ["s3:GetObject"],
        "Resource": ["arn:aws:s3:::example-bucket/*"]
    }
]
pd = PolicyDocument(Statement=stmt)                     # Version defaults to "2012-10-17"
print(pd.json_repr())                                   # {'Version': '2012-10-17', 'Statement': [...]} 
json_text = pd.to_json()                                # Pretty-printed JSON string ready for output or API calls

# Statement may include objects that implement json_repr(); IAMJSONEncoder will delegate to them
# If a nested element is not serializable and lacks json_repr, pd.to_json() will raise TypeError

# Beware: Using pd as a dict key or inserting into a set will raise TypeError because json_repr() returns a dict (unhashable):
# hash(pd)  --> TypeError: unhashable type: 'dict'

### `trailscraper.iam.PolicyDocument.__init__` · *method*

## Summary:
Initializes a PolicyDocument instance by storing the provided policy Statement and Version on the object, affecting the object's persistent state.

## Description:
This constructor sets up the minimal internal state required for a policy document object. It stores the Version and Statement values on the newly created instance and performs no validation or mutation of the input values.

Known callers and invocation context:
- No specific callers are identified within this code snippet. Typically, this constructor is invoked wherever the application creates or reconstructs IAM-style policy documents — for example, when parsing a JSON/YAML policy, constructing a policy programmatically before serialization, or wrapping an existing policy structure for further processing.
- Lifecycle stage: object construction / initialization; this method is invoked when a new PolicyDocument instance is created as part of policy-building, modification, or serialization workflows.

Why this is a separate method:
- Encapsulates state initialization for PolicyDocument instances in one place, making object construction explicit and discoverable.
- Keeps any future initialization logic (validation, defaults, normalization) centralized rather than duplicated at call sites.

## Args:
    Statement (any):
        The policy statement data to store on the instance. The constructor does not enforce a type or structure.
        Typical expected values (convention only, not enforced): a dict representing a single IAM Statement or a list of dicts representing multiple statements following AWS IAM policy structure.
    Version (str, optional): Defaults to "2012-10-17".
        The policy version identifier to store on the instance. No validation is performed on the string.

## Returns:
    None
    The constructor returns no value (standard __init__ behavior). After the call, self.Version and self.Statement are set on the instance.

## Raises:
    None
    This method does not raise exceptions under any implemented code path. It performs plain attribute assignment and does not validate input.

## State Changes:
    Attributes READ:
        None (this method does not read any pre-existing instance attributes).
    Attributes WRITTEN:
        self.Version  -- assigned the provided Version value
        self.Statement -- assigned the provided Statement value

## Constraints:
    Preconditions:
        - No preconditions are enforced by the method. Callers should provide meaningful values for Statement and Version if their code relies on specific structure or content.
    Postconditions:
        - After return, the instance will have attributes Version and Statement set to the provided values (or the default Version if none was supplied).

## Side Effects:
    - No I/O, no network calls, and no mutation of external objects are performed by this method.
    - Only side effect is setting attributes on the constructed instance itself.

### `trailscraper.iam.PolicyDocument.json_repr` · *method*

## Summary:
Return a shallow Python dict representation of the policy document ready for JSON serialization, exposing the Version and Statement values stored on the object.

## Description:
Known callers:
    - PolicyDocument.to_json: used during final JSON serialization (to_json calls the JSON serializer on this dict).
    - Tests, custom encoders, or utilities that need the canonical dict form of the policy document may call this method directly.

Context / lifecycle:
    - This method is invoked during the serialization stage for an IAM policy document. It separates the concern of producing the structural representation (mapping attribute names to keys) from converting that representation to a JSON string.

Why a separate method:
    - Keeps representation logic reusable and testable without performing string encoding.
    - Allows custom JSON encoders or composition of policy documents to operate on the dict form.

## Args:
    None (instance method).
    Implicit:
        - self (PolicyDocument): instance initialized by PolicyDocument.__init__(Statement, Version="2012-10-17").

## Returns:
    dict: A shallow mapping with exactly two keys:
        - 'Version' (str): the Version value held on the instance. Default value set in __init__ is "2012-10-17".
        - 'Statement' (any): the Statement value held on the instance. Typically a JSON-serializable dict or list of dicts representing IAM statements.
    Example return value:
        {'Version': '2012-10-17', 'Statement': [{'Effect': 'Allow', 'Action': 's3:GetObject', 'Resource': '*'}]}

Notes:
    - The method does not perform validation or type coercion; it returns the raw attribute values exactly as stored.
    - The returned mapping is shallow: its 'Statement' entry is the same object reference as self.Statement.

## Raises:
    - AttributeError: if self.Version or self.Statement attributes are missing on the instance (for example, if the instance was not constructed via PolicyDocument.__init__ or attributes were deleted).
    - No other exceptions are raised by this method itself. Errors due to non-JSON-serializable Statement contents will occur later when callers attempt JSON serialization.

## State Changes:
    Attributes READ:
        - self.Version
        - self.Statement
    Attributes WRITTEN:
        - None (the method does not modify the instance)

## Constraints:
    Preconditions:
        - The instance should have been initialized so that self.Version and self.Statement are present. __init__ sets Version (default "2012-10-17") and Statement.
        - For successful downstream JSON encoding, callers should ensure self.Statement is JSON-serializable (this is a caller responsibility; not enforced here).

    Postconditions:
        - The method returns a dict with keys exactly 'Version' and 'Statement'.
        - The PolicyDocument instance remains unchanged.
        - The 'Statement' value in the returned dict is the same object reference as self.Statement (mutating nested structures in the returned dict will affect the instance's state).

## Side Effects:
    - No I/O, network, or external service calls.
    - No deep copies: returning the same nested object references can lead to external mutation of the instance if callers modify nested contents of the returned dict.

### `trailscraper.iam.PolicyDocument.to_json` · *method*

## Summary:
Returns a JSON-formatted string representation of the PolicyDocument object by delegating to its json_repr() and encoding the result with the IAMJSONEncoder; does not modify the object.

## Description:
This method converts the PolicyDocument into a human-readable JSON string suitable for storage, transmission, or display. It calls the object's json_repr() to obtain a JSON-serializable structure (a dict with keys "Version" and "Statement" for this class) and then serializes that structure using json.dumps with IAMJSONEncoder, an indent of 4 spaces, and sorted keys.

Known callers and invocation context:
- No direct callers were found in the available repository memory. Typical call sites include any code that needs the PolicyDocument as JSON (for example, code that writes a policy to disk, includes it in an HTTP request to an API, or returns it in a higher-level serialization routine).
- Typical lifecycle stage: final serialization step when producing the external representation of a PolicyDocument.

Reason this is a separate method:
- Encapsulates the canonical JSON serialization parameters (indentation, key ordering, and the use of IAMJSONEncoder) in one place so callers do not need to replicate those details.
- Keeps presentation concerns (how the object is encoded as a JSON string) separate from the pure data representation returned by json_repr().

## Args:
- None

## Returns:
- str: A JSON string.
  - The string is produced by json.dumps(..., cls=IAMJSONEncoder, indent=4, sort_keys=True).
  - The JSON will be pretty-printed with 4-space indentation and object keys sorted alphabetically.
  - On Python 3 this is a unicode str; on Python 2 (if supported) it will be a native str type produced by json.dumps.

## Raises:
- Any exception raised by self.json_repr() will propagate unchanged.
  - Example: AttributeError, ValueError, or a user-defined exception originating from json_repr() implementation.
- TypeError from json.dumps/IAMJSONEncoder when the structure returned by json_repr() (or nested elements thereof) cannot be serialized and no json_repr() is available for non-serializable nested objects.
  - The exact message typically follows json library conventions, e.g., "Object of type X is not JSON serializable".
- json.JSONEncode-related exceptions may propagate if invalid encoder parameters are somehow introduced (not in this method as implemented).

## State Changes:
- Attributes READ:
  - self.Version (accessed indirectly via json_repr())
  - self.Statement (accessed indirectly via json_repr())
  - Any other attributes that json_repr() reads (none in the provided json_repr for this class).
- Attributes WRITTEN:
  - None. This method does not mutate self or external objects.

## Constraints:
- Preconditions:
  - self.json_repr() must be callable without arguments.
  - The object returned by self.json_repr() should be JSON-serializable (primitive types, lists, dicts, or nested structures that are serializable or provide json_repr()).
  - If nested non-serializable objects are present in the json_repr() return value, those objects must either be natively serializable or implement json_repr() themselves so IAMJSONEncoder can encode them.
- Postconditions:
  - On successful return, the method yields a JSON string representing the structure returned from json_repr(), formatted with 4-space indentation and with keys sorted.
  - The PolicyDocument instance remains unchanged.

## Side Effects:
- No I/O is performed.
- No network calls or external service interactions are performed.
- The only external interactions are:
  - Calling self.json_repr(), which may have side effects if that method is implemented to mutate state (the provided json_repr implementation does not mutate state).
  - Using json.dumps with IAMJSONEncoder which may call json_repr() on nested objects; any side effects from those json_repr() calls will propagate.

## `trailscraper.iam.IAMJSONEncoder` · *class*

## Summary:
A JSON encoder subclass that delegates serialization of custom objects to their own json_repr() method when present; otherwise falls back to the standard json.JSONEncoder behavior.

## Description:
Use IAMJSONEncoder whenever you need json.dumps/json.dump (or JSONEncoder.encode) to support serializing application-specific objects that implement a json_repr() method. When the JSON encoder encounters an object it cannot serialize directly, IAMJSONEncoder checks for a json_repr attribute and, if present, calls that method and uses its return value as the serializable representation.

Typical callers:
- json.dumps(obj, cls=IAMJSONEncoder)
- json.dump(obj, fp, cls=IAMJSONEncoder)
- IAMJSONEncoder().encode(obj)

Motivation and responsibility:
- Keeps serialization logic local to model objects by allowing them to expose a json_repr() method that returns a JSON-serializable representation (primitive, dict, list, or nested structures).
- Centralizes the policy for "ask the object how to represent itself" without modifying json.JSONEncoder core logic.
- It does not attempt to inspect object internals or mutate objects; it only delegates to json_repr if present.

## State:
- No instance attributes are defined by IAMJSONEncoder itself.
- Invariants:
  - IAMJSONEncoder instances behave exactly like json.JSONEncoder instances, except for the custom delegation in default().
  - The encoder does not store or mutate object state; it is stateless with respect to encoding operations.

For callers:
- __init__ is inherited from json.JSONEncoder; any parameters accepted by json.JSONEncoder.__init__ (such as skipkeys, ensure_ascii, check_circular, allow_nan, indent, separators, default, sort_keys, etc.) may be passed through when instantiating IAMJSONEncoder.

## Lifecycle:
Creation:
- Instantiate using the same constructor signature as json.JSONEncoder, e.g. IAMJSONEncoder() or IAMJSONEncoder(indent=2).
- Alternatively, pass the class as the cls argument to json.dump/json.dumps: json.dumps(obj, cls=IAMJSONEncoder).

Usage:
- Typical usage is to call json.dumps(obj, cls=IAMJSONEncoder) or json.dump(obj, fp, cls=IAMJSONEncoder).
- During encoding, whenever the underlying JSON machinery encounters an object it cannot serialize, JSONEncoder will call IAMJSONEncoder.default(o).
- IAMJSONEncoder.default(o) will:
  1. If o has a callable attribute named json_repr (i.e., hasattr(o, 'json_repr') is True), call o.json_repr() with no arguments and return its result.
  2. Otherwise, delegate to json.JSONEncoder.default(self, o) which raises TypeError for unsupported objects.

Sequencing:
- No special sequencing is required by callers; the JSON encoding process invokes default() as needed.
- If json_repr() returns another object that itself requires custom encoding, the JSON encoder will re-enter encoding on that returned object (and IAMJSONEncoder will be invoked again if it's not natively serializable).

Destruction:
- No special cleanup is required. The object does not manage external resources and is not a context manager.

## Method Map:
flowchart LR
    A[Start encoding] --> B{Encoder encounters non-serializable object o}
    B -- no --> C[Encode normally]
    B -- yes --> D[Call IAMJSONEncoder.default(o)]
    D --> E{hasattr(o, 'json_repr')?}
    E -- yes --> F[o.json_repr() called -> return repr]
    F --> G[Encoder attempts to serialize repr]
    G --> H{repr fully serializable?}
    H -- yes --> I[Encoding continues/succeeds]
    H -- no --> B
    E -- no --> J[Call json.JSONEncoder.default(self, o)]
    J --> K[Typically raises TypeError]

## Methods (behavioral details)
default(self, o)
- Purpose:
  - Provide a fallback mechanism used by json.JSONEncoder when it cannot natively serialize object o.
  - If o implements json_repr, use that to obtain a serializable representation.

- Inputs:
  - o (any): The object that the JSON encoder could not serialize natively.

- Behavior:
  - If hasattr(o, 'json_repr') is True, call o.json_repr() with no arguments and return the value.
    - The returned value should be a JSON-serializable Python type (str, int, float, bool, None, list, dict), or a structure composed of those types.
    - If the returned value contains other non-serializable objects, the JSON encoder will attempt to encode them and may call default() again for nested objects.
  - If o does not have json_repr, call json.JSONEncoder.default(self, o) to preserve the standard fallback behavior (which normally raises TypeError: Object of type X is not JSON serializable).

- Outputs:
  - A JSON-serializable representation of o (as returned by json_repr), or a delegate to the base class which will typically raise TypeError.

- Edge cases and constraints:
  - json_repr must be callable without arguments; IAMJSONEncoder calls it with zero parameters.
  - If json_repr exists but raises an exception, that exception will propagate out of the encoding operation.
  - If json_repr returns another complex object that is not serializable, the encoder will attempt to encode it and may raise TypeError unless that object also supplies json_repr.
  - IAMJSONEncoder does not coerce or validate the return type of json_repr; responsibility for producing a serializable representation lies with the object’s json_repr implementation.
  - IAMJSONEncoder does not catch exceptions from json_repr.

## Raises:
- __init__:
  - Inherits behavior from json.JSONEncoder.__init__; may raise TypeError if invalid constructor arguments are supplied.
- default:
  - If the object lacks json_repr and is not natively serializable, json.JSONEncoder.default(self, o) will typically raise TypeError: Object of type <typename> is not JSON serializable.
  - Any exception raised by o.json_repr() will propagate (e.g., AttributeError, ValueError, custom exceptions).

## Example:
# Example: define a custom class that exposes json_repr
class User:
    def __init__(self, user_id, name, metadata):
        self.user_id = user_id
        self.name = name
        self.metadata = metadata
    def json_repr(self):
        # produce a JSON-serializable dict representation
        return {
            "id": self.user_id,
            "name": self.name,
            "metadata": self.metadata,
        }

# Serialize using IAMJSONEncoder via json.dumps
u = User(1, "alice", {"role": "admin"})
json_string = json.dumps(u, cls=IAMJSONEncoder)

# Alternatively, instantiate the encoder and encode directly
encoder = IAMJSONEncoder(indent=2)
json_text = encoder.encode(u)

Notes:
- Ensure your objects' json_repr methods return only JSON-serializable structures or types, or arrange for nested objects to also implement json_repr.
- IAMJSONEncoder keeps a minimal surface area — it only overrides default() and otherwise respects json.JSONEncoder's contract and configuration.

### `trailscraper.iam.IAMJSONEncoder.default` · *method*

## Summary:
Encodes non-standard objects for JSON by delegating to an object's json_repr() method when present; otherwise falls back to the base JSONEncoder.default behavior.

## Description:
This method is the override of a JSONEncoder subclass's default handler. When the JSON encoding machinery encounters an object it does not know how to serialize, it calls this method to obtain a JSON-serializable representation.

Known callers and context:
- json.dumps(..., cls=IAMJSONEncoder) and json.JSONEncoder.encode()/iterencode() — the standard json library calls this method as part of encoding objects it cannot serialize by built-in rules.
- Any code that directly uses an instance of IAMJSONEncoder to convert complex objects into JSON (e.g., custom logging, API response serialization).

Why this is a separate method:
- It centralizes the logic that allows arbitrary objects to opt into JSON serialization by implementing a json_repr() method. Keeping this logic in the encoder's default method keeps encoding-time decision-making localized and compatible with the json library's extension point (JSONEncoder.default), instead of requiring callers to pre-convert objects everywhere.

## Args:
    self (IAMJSONEncoder): Instance of the JSONEncoder subclass.
    o (Any): The object to encode. May be any Python object. No type restriction is enforced here.

## Returns:
    Any: If the object has a callable json_repr attribute, returns the result of o.json_repr(). Otherwise, returns the value produced by delegating to json.JSONEncoder.default(self, o).
    - Typical returned types: dict, list, str, int, float, bool, None or another JSON-serializable structure.
    - If o.json_repr() returns a non-JSON-serializable value, the JSON encoding process will later fail (or the base encoder may be invoked again for that returned value).

## Raises:
    Any exception raised by o.json_repr(): If o has a json_repr attribute but calling it raises (e.g., TypeError, ValueError, RuntimeError), that exception propagates out of this method.
    TypeError: If the object lacks a usable json_repr and json.JSONEncoder.default(self, o) raises TypeError indicating the object is not JSON serializable, this TypeError is propagated.

## State Changes:
    Attributes READ:
        - None. This method does not read or depend on any stored attributes of self in its implementation.
    Attributes WRITTEN:
        - None. The method does not modify self or any of its attributes.

## Constraints:
    Preconditions:
        - self should be an instance of a JSONEncoder subclass (the method assumes it is being called by the json encoding machinery).
        - If o defines json_repr, that attribute should be callable and should return a JSON-serializable structure; otherwise callers should be prepared to handle propagated exceptions.
    Postconditions:
        - On success, a JSON-serializable representation (or at least a value acceptable to the json encoder or its base.default) is returned.
        - On failure, an exception originating from o.json_repr() or json.JSONEncoder.default(self, o) is raised and propagated to the caller.

## Side Effects:
    - May call o.json_repr(), which can have arbitrary side effects depending on the implementation of that method (I/O, mutation of o or other objects, logging, etc.). This method itself performs no I/O and does not mutate external state directly.

## `trailscraper.iam._parse_action` · *function*

## Summary:
Parses a colon-delimited IAM action string into its two components and returns an Action object whose prefix and action attributes are set from the first and second segments.

## Description:
Known callers within the codebase:
    - No direct callers were found in the provided repository snapshot. This function is intended to be used wherever IAM-style action strings (formatted as "prefix:action") must be converted into Action objects (for example, when normalizing or comparing permission/action tokens).

Typical trigger/context:
    - Called during IAM action parsing or normalization pipelines when a textual permission token needs to be converted into a structured Action instance for further processing (matching, JSON representation, comparisons).

Why this logic is extracted:
    - Keeps string-parsing concerns isolated from higher-level logic (construction and handling of Action instances). It enforces a single responsibility: convert a colon-delimited string into a two-field Action, so callers need not repeat split-and-construct logic or duplicate error behavior.

## Args:
    action (str): A colon-separated IAM action string in the format "prefix:action".
        - Required format: must contain at least one colon separating prefix and action.
        - Typical values:
            * prefix: service or namespace identifier (e.g., "s3", "ec2")
            * action: operation name (e.g., "ListBuckets", "DescribeInstances")
        - Interdependencies:
            * The function reads the text before the first colon as the prefix and the text between the first and second colon as the action (if multiple colons are present). Additional segments after the second colon are ignored by this function.

## Returns:
    Action: An Action instance constructed with prefix set to the substring before the first colon and action set to the substring immediately after the first colon.
    - Examples of possible return values:
        * Input "s3:ListBuckets" -> Action(prefix='s3', action='ListBuckets')
        * Input "service:subaction:extra" -> Action(prefix='service', action='subaction')
    - Edge-case returns:
        * There is no special "safe" or sentinel return for malformed input; instead the function will allow Python exceptions to propagate (see Raises).

## Raises:
    AttributeError:
        - If the provided action does not support the split method (e.g., action is None or an integer), calling action.split(":") raises AttributeError (or more generally, the attempt to call split on the object fails).
    IndexError:
        - If action.split(":") returns fewer than two segments (i.e., the input contains no colon), accessing parts[1] raises IndexError. This occurs for inputs like "s3ListBuckets" or an empty string.

## Constraints:
Preconditions:
    - Caller should pass a string-like value with at least one ":" character separating prefix and action to avoid exceptions.
Postconditions:
    - On successful return, the returned object is an Action with:
        * prefix equal to the substring before the first ":" in the input
        * action equal to the substring after the first ":" and before the second ":" (if present)
    - No global state is modified.

## Side Effects:
    - None. The function performs only pure in-memory string operations and constructs a new Action object; it does not perform I/O, network calls, or mutate external state.

## Control Flow:
flowchart TD
    Start --> Split[action.split(":")]
    Split -->|len(parts) >= 2| Construct[Construct Action(parts[0], parts[1])]
    Split -->|len(parts) < 2| ErrorR[IndexError raised when accessing parts[1]]
    Construct --> Return[Return Action object]
    ErrorR --> Raise[Propagation of IndexError]
    Start -->|action has no split method| AttrErr[AttributeError raised]

## Examples:
Successful parsing:
    - Input: "s3:ListBuckets"
      Outcome: returns Action(prefix='s3', action='ListBuckets')

Multiple colons (only the first two segments are used):
    - Input: "service:subaction:extra"
      Outcome: returns Action(prefix='service', action='subaction')

Error handling example (calling code should handle exceptions if input may be malformed):
    - If input may be missing a colon or not be a string, wrap the call:
      Try to call _parse_action and catch AttributeError and IndexError to handle malformed inputs (e.g., log and skip, or raise a more specific validation error upstream).

Notes for implementers:
    - Reimplementation must replicate the exact behavior: split on ":" without limiting splits, then construct Action(parts[0], parts[1]). Do not attempt to auto-correct or normalize inputs; this function intentionally allows exceptions to propagate so callers can decide how to validate or recover.
    - If you wish to accept colon-containing action names (where action itself may include ":"), adapt callers instead of changing this function; the current contract takes the second segment as the action.

## `trailscraper.iam._parse_statement` · *function*

## Summary:
Converts a raw IAM-style statement dictionary into a Statement object by parsing each textual Action token into Action objects and preserving the Effect and Resource fields.

## Description:
Known callers within the codebase and typical context:
- Typically invoked by a higher-level policy parsing or normalization routine that iterates over the "Statement" entries of an IAM-style policy document, converting each raw dict into a structured Statement instance.
- Relies on the helper _parse_action to convert textual action tokens (e.g., "s3:ListBucket") into Action objects.
- No specific direct callers were found in the provided snapshot; treat this function as the statement-level factory used during policy deserialization.

Why this logic is extracted into its own function:
- Separates the concerns of (a) converting raw dicts representing statements into the Statement data model and (b) parsing individual action strings. This enforces a clear boundary: statement-level assembly (this function) vs action-level parsing (_parse_action). It keeps the caller code concise and centralizes error propagation for malformed statements.

## Args:
    statement (dict):
        - Expected shape: a mapping with the following required keys:
            * 'Action' : iterable of textual action tokens (commonly a list of strings such as ["s3:ListBucket", "s3:GetObject"])
            * 'Effect' : string describing the effect, typically "Allow" or "Deny"
            * 'Resource': iterable/list of resource identifiers (strings, e.g., ARNs)
        - Type contract:
            * statement must support __getitem__ access with the above keys (i.e., behave like a dict).
            * statement['Action'] must be iterable (typically list). Each element will be passed to _parse_action and therefore should be a string-like object with split(":").
            * statement['Effect'] should be a string (no runtime validation performed).
            * statement['Resource'] should be an iterable of strings (no runtime validation performed).
        - Interdependencies:
            * The function does not validate internal consistency between Effect/Action/Resource; it only constructs a Statement from the provided values.

## Returns:
    Statement:
        - A Statement instance constructed with:
            * Action: list of Action objects returned by calling _parse_action on each element of statement['Action'] (order preserved from the input iterable).
            * Effect: the raw value statement['Effect'] (no normalization performed).
            * Resource: the raw value statement['Resource'] (assigned directly).
        - Possible return scenarios:
            * Normal: returns a Statement with parsed Action objects.
            * This function never returns None or sentinel values; it either returns a Statement or allows exceptions to propagate for malformed input.

## Raises:
    KeyError:
        - If any required key ('Action', 'Effect', or 'Resource') is missing from the input mapping, attempting to access statement['...'] raises KeyError.

    TypeError:
        - If statement['Action'] is not iterable (e.g., None or a non-iterable), the list comprehension will raise a TypeError during iteration.
        - If statement is not subscriptable (e.g., None or an object without __getitem__), accessing statement['Action'] will raise TypeError.

    AttributeError / IndexError (propagated from _parse_action):
        - Each action token is passed to _parse_action which may raise:
            * AttributeError if the token does not support split(":") (e.g., token is None or integer-like without split).
            * IndexError if the token contains no ":" and _parse_action tries to access the second segment.
        - These exceptions propagate unchanged from _parse_action.

    Any other exception:
        - Exceptions raised by Statement.__init__ (e.g., if Statement assumes specific types for its arguments elsewhere) will propagate.

## Constraints:
Preconditions:
    - Caller should pass a mapping-like object containing keys 'Action', 'Effect', and 'Resource'.
    - Elements in statement['Action'] should be string-like values that contain at least one ":" if callers expect successful parsing (to avoid IndexError).
    - No side-effecting or mutable contract is required; inputs are consumed but not mutated by this function.

Postconditions:
    - On success, returns a Statement instance whose:
        * Action attribute is a list of Action objects produced by _parse_action for each input action token (in input order).
        * Effect attribute equals statement['Effect'].
        * Resource attribute equals statement['Resource'] (same reference is passed through).
    - No global state is modified.

## Side Effects:
    - None intrinsic: the function performs pure in-memory operations (list comprehension and object construction).
    - No I/O, no network calls, no stdout/stderr writes, and no mutation of global variables.
    - Side effects may occur indirectly if _parse_action or Statement construction has side effects (by contract, they do not).

## Control Flow:
flowchart TD
    Start --> Access[Access statement['Action'], statement['Effect'], statement['Resource']]
    Access -->|missing key| KeyError[KeyError raised]
    Access --> Iterate[List comprehension over statement['Action']]
    Iterate --> CallParse[_parse_action(action) for each action]
    CallParse -->|_parse_action raises AttributeError/IndexError| PropagateErr[Exception propagates]
    CallParse --> Collect[Collect Action objects into list]
    Collect --> Construct[Construct Statement(Action=list, Effect=..., Resource=...)]
    Construct --> Return[Return Statement instance]
    PropagateErr --> EndErr[Caller sees propagated error]

## Examples:
Successful example:
    raw_stmt = {
        "Action": ["s3:ListBucket", "s3:GetObject"],
        "Effect": "Allow",
        "Resource": ["arn:aws:s3:::example-bucket/*"]
    }
    try:
        stmt_obj = _parse_statement(raw_stmt)
        # stmt_obj is a Statement with:
        #   - Action: [Action(prefix='s3', action='ListBucket'), Action(prefix='s3', action='GetObject')]
        #   - Effect: "Allow"
        #   - Resource: ["arn:aws:s3:::example-bucket/*"]
    except Exception as e:
        # handle malformed input or downstream errors
        raise

Example showing defensive handling for malformed inputs:
    raw_stmt = {"Action": ["invalidaction"], "Effect": "Allow", "Resource": []}
    try:
        stmt_obj = _parse_statement(raw_stmt)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        # Input was malformed (missing key, non-iterable Action, or invalid action token)
        # Take appropriate recovery action: log, skip this statement, or re-raise with context.
        handle_malformed_statement(raw_stmt, exc)

## `trailscraper.iam._parse_statements` · *function*

## Summary:
Converts an iterable of raw IAM-style statement dictionaries into a list of Statement objects by delegating each element to the statement-level parser.

## Description:
- Known callers and context:
    * Typically invoked by a higher-level policy parsing or deserialization routine that has parsed a JSON policy document and is now converting its "Statement" array into structured objects.
    * The function expects json_data to be the list/iterable value of the "Statement" field from an IAM-style policy document (i.e., a sequence of mapping-like statement objects).
    * No specific direct callers were found in the provided snapshot; treat this function as the collection-level factory that maps raw statement dicts into Statement instances.

- Why this logic is extracted:
    * Separates collection-level iteration from per-statement parsing. This keeps the calling code simple (one call to parse all statements) and centralizes error propagation and input shape expectation for the entire statements array.
    * Delegates the responsibility for parsing an individual statement to _parse_statement so that per-statement validation/parsing logic is isolated.

## Args:
    json_data (iterable):
        - An iterable (commonly a list) of statement-like mappings/dictionaries.
        - Expected element shape: each element should be a mapping with required keys 'Action', 'Effect', and 'Resource' (see _parse_statement for per-element contract).
        - Interdependencies:
            * The function does not inspect or normalize elements beyond forwarding each to _parse_statement. Each element must satisfy _parse_statement's preconditions for successful parsing.

## Returns:
    list:
        - A list of Statement objects produced by calling _parse_statement on each element of json_data, preserving input order.
        - Edge-case return values:
            * If json_data is empty (e.g., []), returns an empty list [].
            * The function never returns None; it either returns the list of parsed Statement objects or an exception is raised.

## Raises:
    TypeError:
        - If json_data is not iterable (e.g., None or a non-iterable), attempting to iterate over it will raise TypeError.
        - If an element in json_data is not subscriptable (and thus _parse_statement attempts to index it), that will raise TypeError (propagated).

    Any exception raised by _parse_statement (propagated):
        - KeyError: if a required key ('Action', 'Effect', or 'Resource') is missing in any element.
        - TypeError: if an element's 'Action' value is not iterable.
        - AttributeError / IndexError: if an action token does not have the expected string form and _parse_action (called by _parse_statement) fails.
        - Any other exception raised by Statement construction or _parse_statement will propagate unchanged.

## Constraints:
- Preconditions:
    * json_data must be an iterable containing elements acceptable to _parse_statement (mapping-like elements with 'Action', 'Effect', 'Resource').
    * Callers that require per-element fault tolerance should not rely on this function to swallow exceptions; this function will propagate exceptions from individual element parsing.

- Postconditions:
    * On successful return, every element of the returned list is a Statement instance corresponding (in order) to the input elements.
    * No global state is mutated by this function; inputs are consumed but not modified.

## Side Effects:
- Intrinsic side effects: none. The function performs purely in-memory object construction.
- Indirect side effects: any side effects caused by _parse_statement, _parse_action, or Statement.__init__ (if present) will occur and propagate; this function itself does not perform I/O, network calls, or logging.

## Control Flow:
flowchart TD
    Start --> CheckIterability[Attempt to iterate over json_data]
    CheckIterability -->|not iterable| TypeError_Raised[TypeError raised by iterator]
    CheckIterability -->|iterable| ForEach[For each element in json_data]
    ForEach --> CallParse[_parse_statement(element)]
    CallParse -->|_parse_statement raises| PropagateErr[Exception propagates to caller]
    CallParse --> Collect[Collect returned Statement into list]
    ForEach -->|all elements processed| ReturnList[Return list of Statement objects]
    PropagateErr --> EndErr[Caller receives exception]

## Examples:
Successful bulk-parse:
    raw_policy_statements = [
        {"Action": ["s3:ListBucket", "s3:GetObject"], "Effect": "Allow", "Resource": ["arn:aws:s3:::example/*"]},
        {"Action": ["ec2:DescribeInstances"], "Effect": "Allow", "Resource": ["*"]}
    ]
    # Typical usage: parse all statements at once
    statements = _parse_statements(raw_policy_statements)
    # statements is a list of Statement objects corresponding to the two input dicts

Handling malformed statement entries (per-element defensive strategy):
    raw_policy_statements = [valid_stmt, malformed_stmt, another_valid_stmt]
    parsed = []
    for elem in raw_policy_statements:
        try:
            # use _parse_statement directly to allow per-item error handling
            parsed.append(_parse_statement(elem))
        except (KeyError, TypeError, AttributeError, IndexError) as exc:
            # Decide how to handle malformed entries: log, skip, wrap error, or re-raise
            handle_malformed(elem, exc)
    # If caller needs atomic behavior (all-or-nothing), call _parse_statements and let it propagate the first error encountered.

Notes:
- For callers that need partial success (skip bad statements), iterate explicitly and catch per-item exceptions instead of relying on this bulk helper.
- For deterministic behavior in presence of invalid input, validate json_data and its elements before calling this function or use explicit per-element try/except as shown above.

## `trailscraper.iam.parse_policy_document` · *function*

## Summary:
Parse a JSON-formatted IAM policy (provided as a string or file-like object) and return an in-memory PolicyDocument whose Statement list is produced by the project's statement parser.

## Description:
- Known callers and contexts:
    - Higher-level policy deserialization routines that receive policy JSON from files, templates, or HTTP payloads and need a structured PolicyDocument instance.
    - Policy builders, CloudFormation resource serializers, CLI tools, or unit tests that accept a JSON policy text or a file containing policy JSON.
    - Typical trigger: when the system has policy JSON text or an open file/stream and needs a PolicyDocument object for further processing, serialization, or validation.

- Responsibility boundary:
    - This function is responsible only for turning JSON text/streams into the project's PolicyDocument object and delegating the conversion of the "Statement" array to _parse_statements.
    - It centralizes detection of whether the input is a raw string or a file-like object and isolates JSON parsing and minimal top-level key extraction from downstream statement-parsing logic.
    - It does not perform deep validation of statement contents; that responsibility belongs to _parse_statements and the Statement-level parser.

## Args:
    stream (str | file-like object):
        - If a text string (any type matching six.string_types), it is interpreted as the complete JSON document and parsed via json.loads.
        - Otherwise the value is passed to json.load and must be a file-like object implementing read() that returns a text string (not bytes) containing JSON.
        - The JSON must be an object/dict containing at least the keys 'Statement' and 'Version'.
        - Interdependencies:
            - If stream is not a string, it must be readable (i.e., implement read()). The function will consume the stream (read to end).

## Returns:
    PolicyDocument
        - A PolicyDocument constructed with:
            * Statement = the result of calling _parse_statements(json_dict['Statement'])
            * Version = json_dict['Version']
        - Possible shapes:
            - On success returns a PolicyDocument instance whose .Statement holds the parsed Statement objects (list) and .Version is the exact string from the JSON.
        - Edge-case return behavior:
            - The function never returns None; it either returns a PolicyDocument or raises an exception if parsing fails.

## Raises:
    json.JSONDecodeError (or ValueError on older Python versions)
        - If the input string/stream does not contain valid JSON.
    KeyError
        - If the top-level JSON object lacks the 'Statement' or 'Version' keys (access via json_dict['Statement'] or json_dict['Version']).
    TypeError / AttributeError
        - If a non-string argument is provided that is not a proper file-like object (json.load will raise), or if _parse_statements encounters non-iterable / malformed items and raises TypeError/AttributeError.
    Any exception raised by _parse_statements
        - Exceptions raised while parsing individual statement elements (e.g., KeyError for missing action/effect fields, TypeError for invalid types) propagate unchanged.

## Constraints:
- Preconditions:
    - Caller must supply either:
        - A text string containing valid JSON representing an AWS-style policy object, or
        - A file-like object opened in text mode whose read() returns a JSON string.
    - The JSON must contain the 'Statement' and 'Version' top-level keys.
    - Elements inside the 'Statement' value must satisfy _parse_statements/_parse_statement expectations.
- Postconditions:
    - On successful return, the result is a PolicyDocument whose .Version equals the JSON 'Version' value and whose .Statement is the parsed representation returned by _parse_statements.
    - The input stream (if file-like) will have been consumed (read pointer at end).

## Side Effects:
- The function reads from the provided stream (consumes the content).
- No network, file writes, stdout/stderr output, or global state mutations are performed by this function itself.
- Any side effects raised by _parse_statements or Statement constructors are possible and will propagate.

## Control Flow:
flowchart TD
    Start --> IsString{isinstance(stream, six.string_types)?}
    IsString -- yes --> LoadsString[json.loads(stream) -> json_dict]
    IsString -- no --> LoadsStream[json.load(stream) -> json_dict]
    LoadsString --> Extract[Extract json_dict['Statement'] and json_dict['Version']]
    LoadsStream --> Extract
    Extract --> ParseStatements[_parse_statements(json_dict['Statement'])]
    ParseStatements --> Construct[PolicyDocument(parsed_statements, Version=json_dict['Version'])]
    Construct --> Return[return PolicyDocument]
    LoadsString -->|invalid JSON| JSONErr[raise json.JSONDecodeError/ValueError]
    LoadsStream -->|io/read error| IOErrorErr[raise TypeError/ValueError/etc from json.load]
    ParseStatements -->|parsing error| ParseErr[propagate exception from _parse_statements]
    Extract -->|missing key| KeyErr[raise KeyError]

## Examples:
1) Parse from a JSON string (happy path)
    json_text = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:GetObject","Resource":"arn:aws:s3:::example/*"}]}'
    try:
        pd = parse_policy_document(json_text)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        handle_parse_error(exc)
    else:
        # pd is a PolicyDocument with parsed statements and the given Version
        use_policy_document(pd)

2) Parse from a file-like object
    with open('policy.json', 'r', encoding='utf-8') as f:
        try:
            pd = parse_policy_document(f)
        except Exception as exc:
            # handle malformed JSON, missing top-level keys, or statement parsing errors
            log_and_fail(exc)
        else:
            deploy_policy(pd)

3) Defensive per-statement handling (when you want partial success)
    # _parse_statements will stop on the first exception and propagate it.
    # To get partial results, parse the top-level JSON manually and iterate:
    json_dict = json.load(open('policy.json'))
    raw_statements = json_dict['Statement']
    parsed = []
    for raw in raw_statements:
        try:
            parsed.append(_parse_statement(raw))   # call statement-level parser directly
        except Exception as exc:
            handle_bad_statement(raw, exc)
    pd = PolicyDocument(Statement=parsed, Version=json_dict.get('Version', '2012-10-17'))

## `trailscraper.iam.all_known_iam_permissions` · *function*

## Summary:
Returns the set of known IAM action strings by reading the repository-maintained "known-iam-actions.txt" file located next to the iam.py module.

## Description:
This function centralizes the logic to load the canonical list of IAM permission/action identifiers from a plain text file shipped with the package. It opens the file known-iam-actions.txt (located in the same directory as this module), reads every line, strips only the trailing newline character from each line, and returns all unique entries as a Python set.

Known callers within the codebase:
- No direct callers were identified in the repository scan provided. Typical call sites (not present in the scan) would include validation routines, policy-generation code, or tests that need the authoritative list of IAM actions.

Why this is extracted into a dedicated function:
- Encapsulates file-location logic (module-relative path) and the exact normalization rule (rstrip('\n')) in one place, avoiding duplication across the codebase.
- Provides a single point to change file-handling behavior (e.g., caching, normalization) later without altering callers.
- Makes unit testing straightforward by isolating file I/O to one function.

## Args:
- None.

## Returns:
- set[str]: A set of strings, each string is one line from known-iam-actions.txt with the trailing newline character removed.
  - Duplicate lines in the file are de-duplicated by the set.
  - Blank lines in the file produce an empty-string entry ('') in the returned set (because a blank line yields '\n' from readlines(), and rstrip('\n') -> '').
  - Trailing carriage return characters (e.g., '\r' from Windows CRLF files) are NOT removed by the current code and will remain in the returned strings (e.g., 's3:GetObject\r') because only '\n' is stripped.
  - If the file is empty, the function returns an empty set.

## Raises:
- FileNotFoundError: If known-iam-actions.txt does not exist at the expected path (os.path.join(os.path.dirname(__file__), 'known-iam-actions.txt')).
- OSError: For other filesystem-level errors when opening or reading the file (permission errors, I/O errors).
- UnicodeDecodeError: If the file's bytes cannot be decoded using the explicit encoding "UTF-8" provided to open().

All exceptions from open() or readlines() are propagated to the caller (there is no internal exception handling).

## Constraints:
Preconditions:
- The caller should expect the file to exist at package-install time next to the iam.py module.
- The function assumes UTF-8 encoding for the file contents.

Postconditions:
- After a successful return, the caller is guaranteed to have an in-memory set containing each unique line from the file with trailing newline characters removed.
- No global state is modified by the function.

## Side Effects:
- Performs read-only file I/O on the package file known-iam-actions.txt.
- No network I/O.
- No writes to disk, no mutation of global variables, no cache updates.

## Control Flow:
flowchart TD
    A[Start] --> B[Open file at module-dir/known-iam-actions.txt with encoding UTF-8]
    B -->|open() fails| E[Raise FileNotFoundError / OSError / UnicodeDecodeError]
    B --> C[Read all lines (readlines())]
    C --> D[For each line: line.rstrip('\n')]
    D --> F[Aggregate results into a set (deduplicate)]
    F --> G[Return set]
    E --> H[Propagate exception to caller]

## Examples (usage and error handling described in prose):
- Typical usage:
  1. A policy validator calls this function at startup to obtain the canonical list of allowed IAM actions and then checks each action used in a policy against this set.
  2. A unit test calls this function to assert that a generated policy contains only actions present in the canonical list.

- Handling missing file:
  - When embedding this in a CLI or service, wrap the call in a try/except block that catches FileNotFoundError and logs a clear error message indicating the package is incomplete or corrupted, then exits or falls back to a safe default.

- Normalization note for callers:
  - Because the function only strips trailing '\n', callers that need to compare actions in a robust way (ignoring surrounding whitespace and CR characters) should further normalize returned strings (for example, applying .strip() and removing '\r') before comparisons.

## `trailscraper.iam.known_iam_actions` · *function*

## Summary:
Return the list of Action objects known for a given IAM service/namespace prefix by loading the repository's canonical action strings, parsing them into Action objects, grouping them by prefix, and returning the group for the requested prefix.

## Description:
- Known callers:
  - No direct callers were found in the provided repository snapshot. Typical uses include policy validation, autocompletion, UI suggestions, normalization routines, and tests that need all recognized actions for a particular IAM service (for example, obtaining all "s3" actions).
  - Typical trigger: invoked when a caller needs to validate, enumerate, or match IAM actions for a single prefix (the portion before ":" in an IAM action string).

- Why this logic is a separate function:
  - Centralizes the pipeline: load canonical action strings (via all_known_iam_permissions), parse each string to an Action object (via _parse_action), group parsed Action objects by their prefix, and return the subset for a requested prefix.
  - Keeps file I/O, parsing, and grouping concerns out of callers and provides a single place to change normalization or caching policies.

## Args:
    prefix (str)
        - Description: The IAM service/namespace prefix to look up (the substring before ":" in IAM action strings, e.g., "s3", "ec2").
        - Type: str is expected and typical. Passing an unhashable object (e.g., list) may raise a TypeError depending on the grouping implementation; callers should pass a string.
        - Behavior: If the provided prefix does not exist in the canonical data, the function returns an empty list.

## Returns:
    list[Action]
        - A list of Action instances whose .prefix attribute equals the supplied prefix.
        - How the result is obtained (observable pipeline):
            1. Call all_known_iam_permissions(), which returns a set of strings (repository-maintained "known-iam-actions.txt" lines, each with trailing '\n' removed).
            2. Each string from that set is transformed with _parse_action into an Action instance.
            3. The resulting Action objects are grouped by their .prefix attribute (the code calls a grouping helper and then .get on the result).
            4. The function returns the list associated with the requested prefix, or [] if the prefix key is absent.
        - Important details and edge cases:
            - all_known_iam_permissions returns a set of strings, so duplicate lines in the file are deduplicated before parsing.
            - Because the source is a set and grouping does not guarantee ordering, the ordering of the returned list is unspecified — do not rely on stable ordering.
            - all_known_iam_permissions strips only trailing newline characters ('\n'):
                * Blank lines in the file become the empty string '' and will be included in the set and subsequently parsed (which may raise on parsing).
                * Carriage return characters ('\r') from CRLF files are not removed and may remain in strings (e.g., 's3:GetObject\r'), which can cause parsing/lookup differences unless callers normalize further.
            - The returned Action objects are exactly what _parse_action produces; no extra normalization or filtering is performed here.

## Raises:
    - Exceptions from all_known_iam_permissions(), for example:
        * FileNotFoundError if the known-iam-actions.txt file is missing.
        * OSError for other filesystem errors.
        * UnicodeDecodeError if the file cannot be decoded as UTF-8.
    - Exceptions from _parse_action(), for example:
        * AttributeError if a returned item is not string-like and lacks split().
        * IndexError if an item lacks the ":" separator expected by _parse_action (e.g., an empty string).
    - Exceptions related to grouping/mapping helpers:
        * AttributeError if the grouping result does not support .get and the code attempts to call knowledge.get(prefix, []).
    - TypeError:
        * If prefix is unhashable and the grouping implementation uses dict-like semantics internally, a TypeError may be raised when using it as a key.
    - All exceptions propagate to the caller; this function does not catch or wrap them.

## Constraints:
- Preconditions:
    - The package must include and be able to read the canonical file used by all_known_iam_permissions.
    - all_known_iam_permissions must return an iterable of strings; in the current implementation it returns a set[str].
    - _parse_action must accept each string from that iterable and return an Action instance.
- Postconditions:
    - On success, the function returns a list (possibly empty) of Action objects with .prefix equal to the requested prefix.
    - No global state is modified; no files are written and no network calls are performed by this function itself.

## Side Effects:
- Indirect read-only file I/O: calling this function triggers all_known_iam_permissions(), which reads known-iam-actions.txt.
- No stdout/stderr writes, no network I/O, no database writes, no persistent caching. Exceptions from helper functions are propagated.

## Control Flow:
flowchart TD
    Start --> Load[Call all_known_iam_permissions() -> set[str]]
    Load -->|open/read/decode error| PropagateLoadErr[Propagate FileNotFoundError/OSError/UnicodeDecodeError]
    Load --> MapParse[Apply _parse_action to each string]
    MapParse -->|_parse_action raises (AttributeError/IndexError)| PropagateParseErr[Propagate parsing exception]
    MapParse --> Group[Group parsed Action objects by .prefix (expect mapping with .get)]
    Group -->|grouping result lacks .get| PropagateGroupErr[Propagate AttributeError]
    Group --> Lookup[knowledge.get(prefix, [])]
    Lookup -->|found| ReturnList[Return list of Action objects]
    Lookup -->|not found| ReturnEmpty[Return []]
    ReturnList --> End
    ReturnEmpty --> End

## Examples:
- Example (happy path):
    - Suppose known-iam-actions.txt contains:
        s3:ListBuckets
        s3:GetObject
        ec2:DescribeInstances
      Then:
        actions = known_iam_actions("s3")
        # actions is a list of Action objects representing "s3:ListBuckets" and "s3:GetObject"
        # For an Action a in actions, a.json_repr() would return "s3:ListBuckets" or "s3:GetObject"

- Handling missing file:
    try:
        s3_actions = known_iam_actions("s3")
    except FileNotFoundError:
        # known-iam-actions.txt missing; handle or surface error
        s3_actions = []

- Handling malformed lines in canonical data:
    # Because blank lines become '' and trailing '\r' may remain, _parse_action may raise.
    try:
        actions = known_iam_actions("s3")
    except (AttributeError, IndexError) as e:
        # Log or raise a clearer error; the function intentionally lets parsing errors propagate
        raise

- Notes for callers and implementers:
    - If callers require robust normalization, perform additional normalization (strip whitespace, remove '\r') on action strings before parsing or after receiving Action objects.
    - Reimplementers should preserve these observable semantics: all_known_iam_permissions returns a set[str] (with only '\n' stripped), _parse_action splits on ":" and may raise on malformed inputs, and the grouping step yields a mapping from prefix to list of Actions which is queried with .get(prefix, []).

