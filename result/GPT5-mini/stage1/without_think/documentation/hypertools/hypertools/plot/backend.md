# `backend.py`

## `hypertools.plot.backend.ParrotDict` · *class*

## Summary:
A dict subclass that coerces keys and values to HypertoolsBackend on assignment and lookup, and returns a HypertoolsBackend for missing keys instead of raising KeyError.

## Description:
ParrotDict ensures stored keys and values are normalized backend identifiers by calling HypertoolsBackend(...) whenever items are set or looked up. Instantiate ParrotDict when you want a mapping whose keys and values behave like HypertoolsBackend objects (case-insensitive comparisons, preserved HypertoolsBackend string-method behavior, and helper methods such as as_ipython/as_python available on stored items).

Responsibility boundary:
- Normalizes keys and values to HypertoolsBackend on __setitem__, __getitem__, and membership checks.
- Does not validate that backend names correspond to importable matplotlib backends.
- Does not manage plotting resources or interact with matplotlib beyond storing identifiers.

Known callers/factories:
- Plotting backend management code that maps backend identifiers to backend handlers or configuration and expects HypertoolsBackend behavior for both keys and stored values.

## State:
Attributes:
- Inherited mapping storage from dict. After assignments made via ParrotDict.__setitem__, keys and values stored in that dict will be instances of HypertoolsBackend.

Constructor parameters:
- *args, **kwargs: forwarded directly to dict.__init__ (default: no initial items). Because ParrotDict.__init__ simply calls super().__init__(*args, **kwargs), initial items passed into the constructor may be inserted by dict.__init__ without coercion by ParrotDict.__setitem__; see Lifecycle notes for a safe population pattern.

Class invariants:
- If an entry was inserted through ParrotDict.__setitem__, its key is a HypertoolsBackend instance and its value is a HypertoolsBackend instance.
- Due to HypertoolsBackend's case-insensitive equality and hashing, keys that differ only by case map to a single underlying entry.

## Lifecycle:
Creation:
- Instantiate like a normal dict:
    - d = ParrotDict()
    - d2 = ParrotDict([("TkAgg", "module://...")]) — note: constructor-forwarded initial items may not be coerced to HypertoolsBackend; to guarantee coercion, populate after construction (see below).

Safe population to guarantee coercion:
- Preferred:
    d = ParrotDict()
    for k, v in source.items():
        d[k] = v
  This ensures each insertion goes through ParrotDict.__setitem__ and is coerced.

Usage (typical sequence):
1. Assignment: d[key] = value
   - Coerces key and value to HypertoolsBackend and stores them.
2. Membership: key in d
   - Coerces key to HypertoolsBackend and checks membership (returns bool).
3. Retrieval: v = d[key]
   - Coerces key and returns stored value. If key is absent, the class's __missing__ returns HypertoolsBackend(key) (no KeyError).
4. Iteration, keys(), values(), items(): behave like dict; stored elements will usually be HypertoolsBackend if set via __setitem__.

Destruction:
- No special cleanup required.

## Method Map:
graph LR
    Init[__init__(*args, **kwargs) -> calls dict.__init__] -->|may insert items without coercion| Storage[underlying dict storage]
    Set[__setitem__(key, value)] --> Kcoerce[HypertoolsBackend(key)]
    Set --> Vcoerce[HypertoolsBackend(value)]
    Kcoerce --> Store[super().__setitem__(k_coerced, v_coerced) -> returns None]
    Contains[__contains__(key)] --> Kcoerce2[HypertoolsBackend(key)]
    Kcoerce2 --> KeysCheck[check Kcoerce2 in self.keys() -> bool]
    Get[__getitem__(key)] --> Kcoerce3[HypertoolsBackend(key)]
    Kcoerce3 --> Retrieve[super().__getitem__(k_coerced) or __missing__]
    Missing[__missing__(key)] --> Return[return HypertoolsBackend(key)]

## Methods (behavior, inputs, outputs, edge cases):

- __init__(*args, **kwargs) -> None
    - Behavior: forwards arguments to dict.__init__ exactly as written in the source.
    - Edge: initial items passed via constructor may be inserted by dict.__init__ without passing through ParrotDict.__setitem__; such items will not be coerced by ParrotDict. To ensure coercion, populate with assignments after construction.

- __setitem__(self, key, value) -> None
    - Behavior: coerces both key and value via HypertoolsBackend(key) and HypertoolsBackend(value), then stores them by calling super().__setitem__(key, value).
    - Return: returns whatever dict.__setitem__ returns (in CPython, None).
    - Raises:
        * Any exception raised by HypertoolsBackend(key) or HypertoolsBackend(value) will propagate (e.g., if HypertoolsBackend's constructor raises).
        * If HypertoolsBackend(...) returns an unhashable object (contradicting expected HypertoolsBackend semantics), dict.__setitem__ may raise TypeError.

- __getitem__(self, key)
    - Input: key (any)
    - Behavior: coerces key via HypertoolsBackend(key) and returns super().__getitem__(coerced_key).
      - If the coerced key is present, returns the stored value (typically a HypertoolsBackend if inserted via __setitem__).
      - If the coerced key is absent, dict lookup triggers __missing__(coerced_key) which returns HypertoolsBackend(coerced_key) per this class.
    - Return type: the stored value (commonly HypertoolsBackend) or a HypertoolsBackend instance for a missing key.
    - Raises:
        * Exceptions from HypertoolsBackend(key) conversion.
        * Does not raise KeyError for missing keys due to __missing__ implementation.

- __contains__(self, key) -> bool
    - Behavior: coerces key via HypertoolsBackend(key) and tests membership against self.keys().
    - Return: True if a matching coerced key exists in the mapping; False otherwise.
    - Raises: exceptions from HypertoolsBackend(key) conversion may propagate.

- __missing__(self, key)
    - Behavior: called by dict.__getitem__ when a coerced key is absent. Returns HypertoolsBackend(key) instead of raising KeyError.
    - Important: this method returns the HypertoolsBackend object but does not insert the key into the mapping. The mapping remains unchanged.
    - Return type: HypertoolsBackend
    - Raises: exceptions from HypertoolsBackend(key) conversion.

## Raises:
- NameError/ImportError if HypertoolsBackend is not defined/imported in the module where ParrotDict is used.
- Any exception that HypertoolsBackend(...) may raise will propagate from __setitem__, __getitem__, __contains__, and __missing__.
- No KeyError will be raised by __getitem__ for missing keys because __missing__ returns a value.

## Edge cases and constraints:
- Case-insensitive collisions: setting keys that differ only by case will overwrite the same underlying entry because HypertoolsBackend implements case-insensitive equality/hash.
- Values are coerced: values assigned to the dict are converted to HypertoolsBackend(value) — this may convert non-string objects into string-like HypertoolsBackend instances (because HypertoolsBackend wraps str(value) semantics). If you need to preserve arbitrary Python objects as values, do not use ParrotDict.
- Constructor population caveat: because __init__ forwards to dict.__init__, initial items supplied in the constructor may not be coerced; to guarantee coercion, assign items after construction.
- __missing__ does not mutate the mapping. If you need missing-key behavior that inserts defaults, use a different subclass or wrap assignment logic yourself.

## Example:
- Create and populate ensuring coercion:
    d = ParrotDict()
    d['TkAgg'] = 'module://ipykernel.pylab.backend_inline'
    # Now: stored key is HypertoolsBackend('TkAgg'), stored value is HypertoolsBackend('module://ipykernel.pylab.backend_inline')

- Membership (case-insensitive):
    'tkagg' in d  # -> True (HypertoolsBackend('tkagg') equals stored HypertoolsBackend('TkAgg'))

- Retrieval and missing-key behavior:
    v = d['TKAGG']  # returns the stored HypertoolsBackend value
    missing = d['nonexistent']  # returns HypertoolsBackend('nonexistent') (no KeyError), mapping unchanged

- Overwrite by case-insensitive key:
    d['tkagg'] = 'TkAgg'  # overwrites same entry previously stored under 'TkAgg'

### `hypertools.plot.backend.ParrotDict.__init__` · *method*

## Summary:
Forwards all constructor arguments to the built-in dict initializer, producing a ready ParrotDict instance; any initial items provided via these arguments are inserted into the underlying mapping using dict.__init__ (and therefore may bypass ParrotDict's coercion logic).

## Description:
Known callers and context:
- Called whenever a ParrotDict instance is created by client code that manages plotting backends (e.g., backend mapping factories and plotting-backend configuration code). Typical lifecycle stage: object construction during setup/configuration of backend mappings.
- Frequently used as: d = ParrotDict() or d = ParrotDict(existing_mapping) when creating a mapping intended to store HypertoolsBackend-typed keys/values.

Why this is its own method:
- The method preserves and exposes the standard dict construction semantics by delegating to dict.__init__. This keeps initialization behavior consistent with built-in dicts and avoids duplicating dict construction logic inside ParrotDict. Coercion of keys/values to HypertoolsBackend is intentionally performed in mutation/lookup methods (e.g., __setitem__, __getitem__) rather than during construction so that simple dict-initialization semantics remain intact and predictable.

## Args:
    *args: forwarded to dict.__init__. Typical accepted values:
        - No argument: creates an empty mapping.
        - A mapping object: contents copied into the new dict.
        - An iterable of (key, value) pairs: used to populate the dict.
    **kwargs: forwarded to dict.__init__ as additional key=value initial items.

    Notes:
    - The accepted shapes and behavior are identical to built-in dict.__init__.
    - There are no ParrotDict-specific defaults; all arguments are passed through unchanged.

## Returns:
    None

    - Effect: after return, self is initialized as a dict whose contents equal what dict.__init__ would produce for the given arguments.

## Raises:
    - Any exception raised by dict.__init__ will propagate unchanged. Common examples:
        * TypeError if an invalid number/type of arguments is provided (e.g., a non-iterable passed where an iterable of pairs is required).
        * TypeError if keyword argument names are invalid for dict construction.
    - Note: ParrotDict.__init__ itself does not perform HypertoolsBackend coercion and therefore will not raise HypertoolsBackend-related exceptions during construction; such exceptions may occur later when mutation/lookup methods that perform coercion are invoked.

## State Changes:
Attributes READ:
    - None (the method body does not read any explicit self.<attr> attributes).

Attributes WRITTEN:
    - Underlying mapping storage (inherited dict contents): dict.__init__ may populate self with the provided initial items. These stored entries are created by dict.__init__ and may not have been coerced to HypertoolsBackend (see Constraints and Lifecycle notes).

## Constraints:
Preconditions:
    - The caller must provide only arguments acceptable to dict.__init__ (mapping, iterable of pairs, and/or keyword pairs). No ParrotDict-specific preconditions are required.
    - If the caller expects all stored keys and values to be HypertoolsBackend instances, they must either:
        1) Avoid passing initial items via the constructor and instead populate the mapping after construction using assignment (so __setitem__ coercion runs), or
        2) Explicitly coerce items before passing them to the constructor.

Postconditions:
    - self is a valid dict instance initialized with the same contents that dict.__init__ would produce for the given arguments.
    - There is no guarantee that items inserted as part of construction have been coerced to HypertoolsBackend; items assigned later via __setitem__ will be coerced.

## Side Effects:
    - Mutates the instance (self) by setting its underlying mapping contents according to dict.__init__ behavior.
    - No I/O, logging, or external network/service calls are performed.
    - No direct interaction with HypertoolsBackend occurs during this method; any conversions or interactions with HypertoolsBackend happen later during mutations and lookups.

### `hypertools.plot.backend.ParrotDict.__contains__` · *method*

## Summary:
Performs a membership test by normalizing the provided key to a HypertoolsBackend and checking if that normalized key exists among the dictionary's keys; does not mutate the dictionary.

## Description:
This method implements ParrotDict's membership semantics used by the Python "in" operator and any explicit calls to __contains__. It is invoked whenever client code checks membership (e.g., "if key in parrot_dict:") during configuration parsing, backend lookup, or any control flow that queries whether a backend identifier is present.

Known callers and contexts:
- Implicitly by the Python "in" operator (e.g., if key in parrot_dict:).
- Any code that calls parrot_dict.__contains__(key) directly to decide whether to read, set, or map values (for example, prior to calling __getitem__).
- Typical lifecycle stage: runtime code that needs to determine whether a backend identifier (user-specified or discovered) is already present in the mapping used by plotting backend selection and normalization.

Why this is a separate method:
- Normalizes the input key to a HypertoolsBackend instance before membership testing. Centralizing that normalization here ensures membership checks are consistent with __setitem__, __getitem__, and the rest of ParrotDict which store and compare keys as HypertoolsBackend objects (providing case-insensitive and type-preserving semantics). Keeping this logic in __contains__ avoids repeating normalization logic at every call site.

## Args:
    key (Any): The thing being tested for membership. It may be:
        - a str (recommended), or
        - any object convertible to str() because HypertoolsBackend(key) is called.
    Allowed values: any value accepted by HypertoolsBackend (i.e., anything for which str(value) does not raise).

## Returns:
    bool: True if HypertoolsBackend(key) is equal (per HypertoolsBackend's case-insensitive equality semantics) to one of the items returned by self.keys(); False otherwise.
    Edge cases:
        - If the dictionary currently contains keys as HypertoolsBackend instances (the normal ParrotDict behavior via __setitem__), membership is case-insensitive (e.g., "TkAgg" and "tkagg" compare equal).
        - If keys in the dict are not HypertoolsBackend instances, membership still relies on Python's container membership protocol and the equality/hash behavior of the stored keys.

## Raises:
    Propagates any exception raised during:
        - Construction of HypertoolsBackend(key) — for example, exceptions raised by str(key) if the object's __str__ raises. These exceptions are not caught here.
        - Evaluation of self.keys() or its __contains__ implementation — if the subclass overrides keys() or the underlying keys-view raises, that exception will propagate.
    No additional exceptions are raised explicitly by this method.

## State Changes:
    Attributes READ:
        - The method calls self.keys(), so it reads the mapping's current set of keys (the dict internal state accessible via keys()).
        - It does not read any explicit self.<attribute> fields beyond the dictionary's key view.
    Attributes WRITTEN:
        - None. This method does not modify self or any external object.

## Constraints:
    Preconditions:
        - self is a ParrotDict (subclass of dict) with a functioning keys() method (inherited dict.keys() unless overridden).
        - key must be convertible to a string (i.e., calling str(key) must not raise) since HypertoolsBackend(key) is constructed.
    Postconditions:
        - No mutation of self or of the provided key occurs.
        - The return value accurately reflects whether a value equal to HypertoolsBackend(key) is present among the dictionary keys at the time of the call. Because dict key views are dynamic, subsequent mutations to the dict may change membership.

## Side Effects:
    - No I/O, no external service calls.
    - Allocates a new HypertoolsBackend instance (temporary object) for the duration of the membership test.
    - No persistent mutation of self or other objects occurs.

### `hypertools.plot.backend.ParrotDict.__getitem__` · *method*

## Summary:
Converts the provided key to a HypertoolsBackend identifier and returns the mapping value for that normalized key without mutating the mapping.

## Description:
This method is invoked whenever client code reads an entry from a ParrotDict instance using indexing (e.g., value = parrot_dict[some_key]). Typical callers are backend-resolution code or configuration lookup code that needs to retrieve a plotting backend or a backend-associated value during initialization or plotting setup. It appears during the lookup stage of the backend-selection pipeline: user-supplied keys (possibly with varying case or format) are normalized to the HypertoolsBackend representation before performing the dictionary lookup.

This logic is kept as a method (instead of inlining the conversion at every call site) to centralize and guarantee:
- Consistent normalization of any key used to index the dict (case-insensitive, type-preserving behavior provided by HypertoolsBackend).
- That the dict lookup participates correctly with the class's __missing__ and __setitem__ semantics (both of which operate on HypertoolsBackend-wrapped keys/values).
- Minimal repetition and a single point for any future changes to key-normalization policy.

## Args:
    key (Any): The lookup key. Accepted values are any object accepted by str() because the method constructs HypertoolsBackend(key). In practice callers pass strings or string-like identifiers for plotting backends. No default.

## Returns:
    Any: The value stored in the mapping for the normalized key. Typical return type is HypertoolsBackend when entries were inserted via ParrotDict.__setitem__ (which wraps stored values with HypertoolsBackend), but any object previously stored under that normalized key may be returned. If the normalized key is not present, ParrotDict implements __missing__ and will return HypertoolsBackend(key) instead of raising a KeyError (i.e., missing lookups yield a HypertoolsBackend constructed from the requested key).

## Raises:
    TypeError: If HypertoolsBackend(key) raises TypeError (for example, if conversion to str triggers a TypeError), this will propagate.
    Any exception raised by HypertoolsBackend construction or by the underlying dict machinery (e.g., if __missing__ has been modified to raise) will propagate. Under normal class behavior, a KeyError is not raised for unknown keys because __missing__ returns a HypertoolsBackend instance.

## State Changes:
    Attributes READ:
        - The method reads the mapping contents stored on self (i.e., the dictionary internal storage) to find a value for the normalized key.
        - It constructs a temporary HypertoolsBackend from the supplied key (reads no explicit self.* attributes).
    Attributes WRITTEN:
        - None. This method does not modify self or external objects.

## Constraints:
    Preconditions:
        - self must be a ParrotDict instance (subclass of dict).
        - The caller should expect keys to be normalized via HypertoolsBackend semantics (case-insensitive equality and preserved type for further backend operations).
        - The module-level HypertoolsBackend constructor must be available and functional; if it raises during conversion, that error propagates.
    Postconditions:
        - No mutation to self has occurred.
        - The return value is either:
            * The object stored under HypertoolsBackend(key) in self, or
            * A HypertoolsBackend created from key (if the normalized key was missing and the class's __missing__ method returns that).
        - Subsequent operations that rely on key normalization (for example, comparing keys) will behave consistently because all lookups go through HypertoolsBackend.

## Side Effects:
    - No I/O or external service calls.
    - No mutations of objects outside self.
    - Constructs a new HypertoolsBackend instance from key (which may run code in HypertoolsBackend.__new__ or related hooks); any side effects from that construction (exceptions) will propagate.

### `hypertools.plot.backend.ParrotDict.__missing__` · *method*

## Summary:
Return a HypertoolsBackend representation of a missing key so callers always receive a backend-typed identifier instead of raising KeyError; this does not mutate the mapping.

## Description:
This method is invoked by Python's dict missing-key protocol when a lookup fails (the builtin dict.__getitem__ machinery calls __missing__(key) on the subclass). Known call sites and context:
- ParrotDict.__getitem__: wraps the incoming lookup key with HypertoolsBackend(key) and then calls super().__getitem__(key). Because ParrotDict.__getitem__ performs that wrapping, __missing__ will normally receive a HypertoolsBackend instance as its key argument.
- Direct dict-level missing-key resolution: If other code triggers the dict protocol directly (for example, by calling dict.__getitem__(parrot_dict, raw_key) or by bypassing ParrotDict.__getitem__), __missing__ may receive the original, unwrapped key object.

Why this is a separate method:
- Centralizes conversion to HypertoolsBackend for all missing-key lookups so contain/get/set methods can rely on consistent, type-preserving backend identifiers.
- Avoids duplicating the wrapping logic across lookup sites and leverages Python's mapping protocol to provide a predictable fallback value instead of immediately raising KeyError.

## Args:
    key (object):
        - Typical runtime value: a HypertoolsBackend instance (because ParrotDict.__getitem__ wraps the lookup key first).
        - Other possible values: any object; the value will be forwarded to HypertoolsBackend(key), which effectively performs str(key).
        - Allowed values: any object convertible to str. No additional validation is performed here.

## Returns:
    HypertoolsBackend:
        - A newly constructed HypertoolsBackend instance created as HypertoolsBackend(key).
        - The returned object is not stored into the dictionary; it is returned only to the caller.
        - Edge cases:
            * If construction succeeds, the return is always a HypertoolsBackend.
            * If construction fails (for example, if str(key) raises or HypertoolsBackend.__new__/constructor raises), the exception propagates and no value is returned.

## Raises:
    - Any exception raised by HypertoolsBackend(key), for example:
        * TypeError or other exceptions from HypertoolsBackend.__new__ if the underlying conversion fails.
        * Exceptions raised by key.__str__ if str(key) triggers user code that fails.
    - Note: __missing__ itself does not raise KeyError; rather, it supplies a fallback value. Any exception listed above will propagate to the original caller.

## State Changes:
    Attributes READ:
        - None. The method does not access self.<attr> fields.
    Attributes WRITTEN:
        - None. The mapping object (self) is not modified; no insertion, deletion, or update occurs.

## Constraints:
    Preconditions:
        - HypertoolsBackend must be defined and importable in the module scope.
        - Typical callers expect ParrotDict.__getitem__ to have wrapped the key; if the caller bypasses that logic, the method still behaves by wrapping key but may receive a raw object.
    Postconditions:
        - self remains unchanged.
        - The caller receives a HypertoolsBackend instance corresponding to key (unless an exception was raised).

## Side Effects:
    - Allocates a HypertoolsBackend object (memory allocation).
    - No I/O, no interaction with external services, and no mutation of objects outside the returned HypertoolsBackend.
    - Repeated missing-key lookups for the same key will construct new HypertoolsBackend instances unless the caller stores/caches the returned value.

## Usage notes:
    - Because the returned value is not inserted into the dictionary, callers that want the fallback preserved should explicitly assign it (e.g., parrot_dict[missing_key] = parrot_dict.__missing__(missing_key)).
    - This method aligns with ParrotDict.__contains__ and __setitem__, which also wrap keys/values with HypertoolsBackend to maintain consistent, case-insensitive backend semantics.

### `hypertools.plot.backend.ParrotDict.__setitem__` · *method*

## Summary:
Converts the provided key and value to HypertoolsBackend instances and stores the mapping in the dictionary, replacing any existing entry for that key.

## Description:
Known callers and context:
- Any code that populates or updates a ParrotDict instance with backend identifiers or backend-related values. Typical callsites are module- or configuration-level initializers that build backend name mappings (for example, when constructing BACKEND_MAPPING equivalents) or runtime code that updates mappings of backend names.
- Called during dictionary population or update steps in the lifecycle where backend identifiers must be normalized and stored in a type-preserving form.

Why this logic is a dedicated method:
- Centralizes and enforces the invariant that both keys and values stored in this mapping are HypertoolsBackend instances (a case-insensitive, type-preserving wrapper around str). Putting the conversion in __setitem__ ensures any assignment (e.g., d['TkAgg'] = 'inline') always yields normalized stored types without requiring callers to remember to wrap values manually.

## Args:
    key (Any): The lookup key to store. It will be passed to HypertoolsBackend(key). Typical/expected values are strings naming plotting backends (e.g., "TkAgg" or "module://ipykernel.pylab.backend_inline"), but any object accepted by str() is allowed.
    value (Any): The value to associate with the key. It will be passed to HypertoolsBackend(value). Typical/expected values are backend identifier strings; however, any object accepted by str() is allowed.

## Returns:
    None: This method returns the result of dict.__setitem__, which is always None. Its primary effect is the mutation of self.

## Raises:
    Any exception raised by HypertoolsBackend(key) or HypertoolsBackend(value): for example, if converting the provided object to a string triggers an exception, that exception will propagate.
    TypeError (propagated from dict.__setitem__): in normal use this will not occur because HypertoolsBackend is a str subclass (and therefore hashable), but if an unusual object is returned by HypertoolsBackend that is not usable as a dict key, dict.__setitem__ could raise TypeError. Any exceptions raised by the superclass implementation will propagate unchanged.

## State Changes:
Attributes READ:
    - None of ParrotDict's explicit attributes are read. The method uses the HypertoolsBackend constructor and the dict superclass machinery but does not access custom instance attributes.

Attributes WRITTEN:
    - The mapping contents of self (the underlying dict storage). After the call, self contains an entry mapping HypertoolsBackend(key) -> HypertoolsBackend(value). If an entry for that key already existed (by equality/hash semantics of HypertoolsBackend), it is replaced.

## Constraints:
Preconditions:
    - self is a ParrotDict instance (subclass of dict).
    - HypertoolsBackend must be importable/available and behave as a str-like, hashable wrapper (the module provides this).
    - key and value must be convertible to strings by HypertoolsBackend (i.e., the conversion should not raise if the call is to succeed).

Postconditions:
    - self will contain the entry where both the stored key and stored value are instances of HypertoolsBackend whose underlying string content equals str(key) and str(value), respectively (subject to HypertoolsBackend's normalization semantics).
    - The method returns None.

## Side Effects:
    - Mutates self by inserting or updating a mapping entry.
    - Allocates two HypertoolsBackend objects (one for key, one for value).
    - No I/O operations, no network calls, and no modifications to objects outside of self (it does not modify the original key or value objects passed in; it stores wrapped copies).

## `hypertools.plot.backend.BackendMapping` · *class*

## Summary:
A small utility that normalizes and records correspondences between Python (Matplotlib) backend identifiers and their IPython/inline equivalents, while collecting alias names.

## Description:
BackendMapping constructs three ParrotDict mappings from a provided mapping of python-backend identifiers to ipython-backend identifiers. Each input key or value may be either a single string identifier or an iterable of identifier strings; when an iterable is provided, the first element is treated as the canonical/default identifier and the remaining elements are recorded as equivalent aliases. BackendMapping then records:
- py_to_ipy: canonical Python backend -> canonical IPython backend
- ipy_to_py: canonical IPython backend -> canonical Python backend
- equivalents: alias identifier -> canonical identifier (for any alias encountered on either side)

Typical scenarios:
- Created during plotting backend configuration to canonicalize and translate backend names between Matplotlib and an IPython inline backend.
- Instantiated by code that needs fast lookups from one canonical backend name to the other, and that also needs to resolve alias names to their canonical form.

Motivation:
- Encapsulates the small but repetitive logic of: (a) accepting either single-name or multiple-name declarations, (b) choosing a canonical default per entry, and (c) maintaining forward, reverse and alias lookup structures in a normalized form.
- Uses ParrotDict for storage so lookups and stored values are normalized/coerced to HypertoolsBackend-like identifiers (case-insensitive behavior and no KeyError on lookup).

## State:
Attributes (public):
- py_to_ipy: ParrotDict
  - Maps canonical Python backend identifier -> canonical IPython backend identifier.
  - Keys and values stored will be coerced by ParrotDict to HypertoolsBackend objects on assignment.
  - Invariant: for every pair inserted during initialization, py_to_ipy[py_default] == ipy_default (both stored as ParrotDict-normalized items).

- ipy_to_py: ParrotDict
  - Maps canonical IPython backend identifier -> canonical Python backend identifier (the reverse mapping).
  - Invariant: ipy_to_py[ipy_default] == py_default for each pair inserted during initialization.

- equivalents: ParrotDict
  - Maps each alias identifier encountered (on either side) -> the canonical default identifier for that group.
  - Invariant: for any alias a provided in an iterable for a canonical key c, equivalents[a] == c (stored/coerced by ParrotDict).
  - Note: equivalents does not map canonical keys to themselves; it only stores alias -> canonical entries built from iterable inputs. Canonical names remain accessible as keys in py_to_ipy/ipy_to_py.

Parameter constraints for __init__:
- _dict: a mapping-like object with an .items() method (e.g., dict). Each key and value must be either:
  - a str (single identifier), or
  - an Iterable of identifiers (e.g., list/tuple) whose first element (index 0) is the canonical identifier and subsequent elements are aliases.
- The iterables provided must be non-empty (must have index 0). Passing an empty iterable for a key or value will raise IndexError when accessing [0].

Class invariants:
- After construction, the three ParrotDict attributes reflect a consistent bidirectional mapping between canonical Python and IPython backend names, plus alias -> canonical resolution. Because ParrotDict coerces on assignment, stored items are HypertoolsBackend-like objects (case-insensitive equality/hashing).

## Lifecycle:
Creation:
- Instantiate directly by passing the mapping specification:
    mapping = BackendMapping(spec)
  where spec is a mapping (e.g., dict) whose items follow the constraints above.

Usage:
- Typical usage pattern:
  1. Create the BackendMapping with the desired mapping specification.
  2. Use mapping.py_to_ipy[python_name] to obtain the canonical ipython backend for a given python backend name (returns a ParrotDict/HypertoolsBackend-normalized object).
  3. Use mapping.ipy_to_py[ipy_name] to obtain the canonical python backend.
  4. Use mapping.equivalents[alias] to resolve an alias to its canonical identifier (returns a HypertoolsBackend-like object).
- ParrotDict semantics:
  - Because storage is a ParrotDict, retrieval via these attributes coerces lookups and will not raise KeyError for missing keys — instead a HypertoolsBackend object representing the missing key is returned. (See ParrotDict documentation for details.)

Sequencing:
- No strict method call order is required beyond construction before lookup. The object is read-only after construction (no public mutators provided by BackendMapping itself).

Destruction:
- No special cleanup or resource management is required.

## Method Map:
graph LR
    A[__init__(_dict)] --> B[_store_equivalents(py_key)]
    A --> C[_store_equivalents(ipy_key)]
    B --> D[assign py_to_ipy[py_default] = ipy_default]
    C --> E[assign ipy_to_py[ipy_default] = py_default]
    B --> F[for each py_alias -> equivalents[py_alias] = py_default]
    C --> G[for each ipy_alias -> equivalents[ipy_alias] = ipy_default]

(Note: ParrotDict.__setitem__ is invoked for each assignment above, causing coercion to HypertoolsBackend-like objects.)

## Raises:
- TypeError / AttributeError:
  - If the provided _dict argument does not support .items() (i.e., is not mapping-like), iterating _dict.items() will raise an AttributeError; calling code should pass a mapping.
- IndexError:
  - If any key or value is provided as an empty iterable (e.g., [] or ()), _store_equivalents attempts to access index 0 and will raise IndexError. Callers should ensure iterables have at least one element.
- Any exceptions raised by ParrotDict/HypertoolsBackend coercion:
  - ParrotDict coerces keys and values via HypertoolsBackend during assignment. Any error raised by that coercion (e.g., if HypertoolsBackend's constructor raises for a particular input) will propagate out of BackendMapping.__init__.
- No KeyError is raised by lookups performed on the internal ParrotDicts; missing-key behavior is handled by ParrotDict.__missing__ (which returns a HypertoolsBackend object instead of raising).

## Example:
- Specification using single names (strings):
    spec = {
        "TkAgg": "module://ipykernel.pylab.backend_inline",
        "Qt5Agg": "module://ipykernel.pylab.backend_inline"
    }
    mapping = BackendMapping(spec)
    # mapping.py_to_ipy["TkAgg"] -> canonical ipy backend (ParrotDict/HypertoolsBackend)
    # mapping.ipy_to_py["module://ipykernel.pylab.backend_inline"] -> last assigned canonical python backend for that ipy name

- Specification using aliases (iterables):
    spec = {
        ("TkAgg", "tkagg", "Tk"): ("module://ipykernel.pylab.backend_inline", "inline"),
        ("Qt5Agg", "qt5agg"): "module://ipykernel.pylab.backend_inline"
    }
    mapping = BackendMapping(spec)
    # The canonical python name for the first entry is "TkAgg" (first element)
    # mapping.equivalents["tkagg"] -> "TkAgg"
    # mapping.py_to_ipy["TkAgg"] -> canonical ipy name "module://ipykernel.pylab.backend_inline"
    # mapping.py_to_ipy["tkagg"] -> same value (ParrotDict coercion handles case-insensitivity)

Notes:
- Ensure iterables passed as keys/values are non-empty.
- Because the storage structures are ParrotDicts, lookups and stored items behave like HypertoolsBackend objects: case-insensitive equality and no KeyError on lookup. Use the ParrotDict documentation for further details on lookup semantics and alias handling.

### `hypertools.plot.backend.BackendMapping.__init__` · *method*

## Summary:
Initializes three ParrotDict-based mappings and populates bidirectional canonical mappings between Python (matplotlib) backend identifiers and IPython/inline backend identifiers, normalizing equivalent identifiers into canonical keys.

## Description:
This constructor builds the internal lookup tables used to translate backend identifiers between Python (matplotlib) form and IPython/inline form. It creates three ParrotDict attributes:
- py_to_ipy: maps canonical Python-backend -> canonical IPython-backend
- ipy_to_py: maps canonical IPython-backend -> canonical Python-backend
- equivalents: maps alternative/equivalent identifiers -> canonical identifier

Known callers and lifecycle stage:
- No explicit instantiations were found in the provided code snapshot. Typically this class is instantiated during backend configuration/initialization (e.g., when the plotting subsystem constructs or loads backend mappings) so that later translation/lookups use the normalized canonical keys.
- Callers will normally construct an instance once and then use its mapping attributes to translate backend identifiers during backend selection, backend normalization, or when converting configuration between environments.

Why this logic is its own method:
- The constructor's logic separates normalization and storage responsibilities: _store_equivalents encapsulates the rules for turning a possibly-many-valued identifier into a single canonical key and for recording its equivalents. Keeping this logic in a helper reduces duplication and ensures that both py->ipy and ipy->py population follow identical normalization rules. Using ParrotDict for storage guarantees consistent coercion of keys/values to HypertoolsBackend objects upon assignment.

## Args:
    _dict (mapping-like): A mapping-like object providing .items() that yields (py_key, ipy_key) pairs.
        - py_key and ipy_key may each be:
            * str: an identifier already canonical
            * an indexable sequence (e.g., list or tuple) of strings: the first element is the canonical key; subsequent elements are equivalent identifiers
        - Notes:
            * The code requires key-like iterables to be indexable and sliceable (it uses keylist[0] and keylist[1:]). Iterables that are not indexable (e.g., set, generator) will raise at runtime.
            * _dict must implement .items(); otherwise AttributeError will propagate.

## Returns:
    None

## Raises:
    AttributeError:
        - If _dict does not implement .items(), iterating _dict.items() will raise AttributeError.
    TypeError / IndexError:
        - If a provided py_key or ipy_key is an Iterable but not indexable (e.g., a set or generator), attempting keylist[0] will raise TypeError or IndexError.
    Any exception raised by ParrotDict.__setitem__ or the underlying HypertoolsBackend coercion:
        - On assignment to py_to_ipy, ipy_to_py, or equivalents, ParrotDict coerces keys/values (via HypertoolsBackend(...) per ParrotDict behavior). Exceptions from that coercion (e.g., invalid argument to HypertoolsBackend) will propagate.

## State Changes:
Attributes READ:
    - None of the object's attributes are read prior to initialization; the constructor calls self._store_equivalents but does not depend on pre-existing attribute values.

Attributes WRITTEN:
    - self.py_to_ipy: assigned a fresh ParrotDict instance, then populated with canonical py->ipy mappings (via ParrotDict.__setitem__).
    - self.ipy_to_py: assigned a fresh ParrotDict instance, then populated with canonical ipy->py mappings.
    - self.equivalents: assigned a fresh ParrotDict instance, and updated by _store_equivalents to map each non-canonical equivalent identifier -> canonical identifier.

## Constraints:
Preconditions:
    - _dict must be mapping-like and provide .items() returning (py_key, ipy_key) pairs.
    - Any keylist provided as a multi-equivalent identifier must be indexable (support [0] and [1:]) and its elements should be string-like identifiers.
Postconditions:
    - For each input (py_key, ipy_key) pair:
        * Let py_canonical = _store_equivalents(py_key)
        * Let ipy_canonical = _store_equivalents(ipy_key)
        * self.py_to_ipy[py_canonical] == ipy_canonical (subject to ParrotDict coercion)
        * self.ipy_to_py[ipy_canonical] == py_canonical (subject to ParrotDict coercion)
        * self.equivalents contains mappings from each non-canonical identifier provided in any keylist to its canonical key (also stored via ParrotDict coercion)
    - All stored keys and values are coerced by ParrotDict upon assignment (typically to HypertoolsBackend wrappers), so callers should expect the mapping keys/values to be those coerced types.

## Side Effects:
    - No file I/O, network, or external service calls are performed.
    - Assignments into ParrotDict instances trigger HypertoolsBackend coercion which may perform string normalization and could raise exceptions; this is a side-effect visible as constructor-time exceptions.
    - The constructor populates in-memory mappings used by other components; it does not mutate objects outside self except via the side-effect of raising exceptions during coercion.

### `hypertools.plot.backend.BackendMapping._store_equivalents` · *method*

## Summary:
Return a canonical (default) key for the provided key or list of equivalent keys and record any alternate keys in the instance-level equivalents mapping, thereby mutating the object's equivalence state.

## Description:
This internal helper is called by BackendMapping during initialization to normalize mapping keys provided as either a single key or as an iterable of equivalents. Known callers:
    - BackendMapping.__init__: called for each pair of py_key and ipy_key to compute a default key and register equivalent keys before populating py_to_ipy and ipy_to_py.

Why this is a separate method:
    - Encapsulates the logic to derive a canonical key from one-or-many equivalent keys and to record alternate keys in self.equivalents so that the __init__ logic remains concise and focused on populating the two direction maps. It centralizes equivalence registration for reuse (py and ipy key processing) and isolates input validation/normalization.

## Args:
    keylist (str | Iterable):
        - If a string, treated as a single key (strings are intentionally not treated as iterables here).
        - If a non-string Iterable (e.g., list or tuple), the first element will be used as the canonical/default key and the remaining elements are treated as equivalent keys to be mapped to that default.
        - Required properties when passing a non-string Iterable:
            * Must be non-empty.
            * Must support indexing with [0] (i.e., be a sequence or similar) because the implementation accesses element 0 directly.
            * Its elements should be valid mapping keys (hashable) because they will be used as keys in self.equivalents.

## Returns:
    default_key:
        - When keylist is a non-string iterable: returns keylist[0] (the chosen canonical key).
        - When keylist is a string (or any non-iterable/non-sequence): returns keylist unchanged.
        - No special sentinel values are returned; callers should expect the canonical key or the original key value.

## Raises:
    IndexError:
        - If a non-string Iterable is empty, accessing keylist[0] will raise IndexError.
    TypeError:
        - If keylist is an Iterable that does not support indexing (for example, a generator), attempting keylist[0] will raise TypeError.
        - If an equivalent key is unhashable, assignment into self.equivalents may raise TypeError.
    Note: These exceptions are implicit (not explicitly raised in code) and arise from the operations performed; callers should ensure preconditions to avoid them.

## State Changes:
    Attributes READ:
        - None of the instance attributes are read for their values by this method (it only writes into an attribute).
    Attributes WRITTEN:
        - self.equivalents: for each equivalent key (every element in keylist after the first when keylist is a non-string Iterable), sets self.equivalents[key_equiv] = default_key. This will add or overwrite entries mapping equivalent names to the chosen canonical key.

## Constraints:
    Preconditions:
        - self.equivalents must be a mutable mapping that supports item assignment (e.g., dict-like).
        - If keylist is intended as an iterable of equivalents, it must be a non-empty, indexable sequence (list, tuple, etc.).
        - Strings must be passed when a single string key is intended; passing a string will not iterate its characters.
    Postconditions:
        - The method returns a canonical key (either the original keylist if not an iterable of equivalents, or the first element of keylist if it is).
        - If keylist was a non-string iterable with elements [k0, k1, k2, ...], then for each ki where i >= 1, self.equivalents[ki] == k0 after the call.
        - No other attributes of self are modified.

## Side Effects:
    - Mutates the instance mapping self.equivalents by inserting or updating entries mapping equivalent keys to the canonical key.
    - No I/O, network calls, or global state mutations occur.

## Implementation notes / reimplementation hints:
    - Treat strings specially: check isinstance(keylist, str) first to avoid iterating characters.
    - Determine whether keylist is an Iterable (from typing import Iterable) but ensure index access (access element 0) — in practice accept list/tuple/sequence types.
    - Use the first element as the canonical key and loop over subsequent elements to populate equivalents.
    - Return the canonical key so callers can use it as the normalized mapping key.

## `hypertools.plot.backend.HypertoolsBackend` · *class*

## Summary:
A thin, case-insensitive string subclass representing a plotting backend identifier with helpers to convert between "python" and "ipython" backend name spaces and to preserve the subclassing behavior when standard string methods are called.

## Description:
HypertoolsBackend exists to represent backend names (e.g., "TkAgg", "module://ipykernel.pylab.backend_inline") while:
- Making equality and hashing case-insensitive.
- Preserving the HypertoolsBackend type when common string operations return strings or simple collections of strings (so downstream code can continue to call backend-specific helpers).
- Providing convenience methods to map a backend identifier to its canonical IPython or Python representation via module-level mappings (BACKEND_MAPPING) and to normalize to the appropriate representation for the current runtime (IS_NOTEBOOK).

Typical usage scenarios:
- Created from a user-specified backend string read from config or environment.
- Used by plotting backends code to compare and map backend identifiers in a case-insensitive way.
- Used where code occasionally calls string methods (e.g., lower(), replace(), split()) on backend names but wants to retain the HypertoolsBackend type for further mapping.

Known callers/factories:
- Any code that reads a backend name and wraps it for comparison/normalization before mapping through BACKEND_MAPPING.
- The module-level functions that map between IPython and Python backend names (not included here) will call HypertoolsBackend when returning backend names so that the mapping result preserves this behavior.

Responsibility boundary:
- HypertoolsBackend is only responsible for being a safe, type-preserving identifier for backend names and for looking up conversions via BACKEND_MAPPING and IS_NOTEBOOK. It does not itself manage plotting, import backends, or detect notebook state.

## State:
HypertoolsBackend has no instance attributes beyond the underlying immutable string value (inherited from str). Conceptually its state is the contained string value.

- Underlying string value:
    - name: value (inherited)
    - type: str
    - valid values: any string; intended to be a plotting backend identifier recognizable to BACKEND_MAPPING or to matplotlib. No enforced validation in the class itself.

- External dependencies (must be provided by the module that defines/uses HypertoolsBackend):
    - BACKEND_MAPPING (required for as_ipython and as_python)
        - Expected type: object with these attributes:
            * equivalents: Mapping[str, str] — maps various synonyms (HypertoolsBackend or str) to a canonical key used by the py_to_ipy/ip_y_to_py dictionaries. Keys are comparable to HypertoolsBackend values case-sensitively (the class uses direct dict-subscript with the HypertoolsBackend instance).
            * py_to_ipy: Mapping[str, str] — maps canonical python-backend-key -> ipython-backend-name (string).
            * ipy_to_py: Mapping[str, str] — maps canonical ipython-backend-key -> python-backend-name (string).
        - Semantics: BACKEND_MAPPING.equivalents[self] should return a canonical key (string) for the given backend identifier; that key should be present in both py_to_ipy and ipy_to_py mappings.
        - Example structure (illustrative only):
            equivalents = {
                "tkagg": "tkagg",
                "TkAgg": "tkagg",
                "module://ipykernel.pylab.backend_inline": "inline",
                "inline": "inline",
            }
            py_to_ipy = {"tkagg": "TkAgg", "inline": "module://ipykernel.pylab.backend_inline"}
            ipy_to_py = {"tkagg": "TkAgg", "inline": "TkAgg"}  # actual mapping depends on project
    - IS_NOTEBOOK (required for normalize)
        - Expected type: bool
        - Semantics: True if the current runtime is an interactive IPython notebook environment where IPython-specific backends should be used; False otherwise.

Class invariants:
- The object is a valid Python str instance (immutable).
- Equality and hash semantics are case-insensitive and stable: if a == b then hash(a) == hash(b) (due to casefold-based hashing and equality).
- If a standard str method is invoked that returns a string or a collection of strings, the returned value is of the same "container" type but elements and single strings are wrapped as HypertoolsBackend (so type-preservation invariant holds for these return types).

## Lifecycle:
Creation:
- Instantiate by calling HypertoolsBackend(x) where x is a string (or any object accepted by str(x)). The constructor simply creates a str subclass with the same content; there are no additional init parameters.
- Example: hb = HypertoolsBackend("TkAgg")

Usage:
- Typical methods called on instance:
    - equality comparisons (==, !=) against other strings or HypertoolsBackend instances — comparisons are case-insensitive.
    - any str methods (e.g., lower(), upper(), replace(), split(), strip()). If the underlying str method returns:
        * a str -> the return value is wrapped into HypertoolsBackend.
        * a list, tuple, or set of strings -> every element is converted to HypertoolsBackend and the same container type is returned (e.g., list([...]) or tuple([...])).
        * any other type -> returned unchanged (no wrapping).
    - as_ipython() -> returns a HypertoolsBackend representing the corresponding IPython backend name using BACKEND_MAPPING.
    - as_python() -> returns a HypertoolsBackend representing the corresponding Python/backend name using BACKEND_MAPPING.
    - normalize() -> returns as_ipython() if IS_NOTEBOOK is True, else as_python().

Method sequencing:
- There is no required ordering for string method calls or comparisons.
- as_ipython / as_python / normalize assume that BACKEND_MAPPING and IS_NOTEBOOK are present and properly configured; these methods should be called only after the module-level mapping objects are initialized.

Destruction / cleanup:
- No resources are held; no cleanup required.

## Method Map:
(visual description of how methods depend on each other and on external state)

graph LR
    A[HypertoolsBackend(str)] --> B[__eq__ (case-insensitive)]
    A --> C[__hash__ (casefold hash)]
    A --> D[__getattribute__ -> wraps str methods]
    A --> E[as_ipython()]
    A --> F[as_python()]
    E --> G[BACKEND_MAPPING.equivalents[self] -> key]
    E --> H[BACKEND_MAPPING.py_to_ipy[key]]
    F --> G
    F --> I[BACKEND_MAPPING.ipy_to_py[key]]
    J[normalize()] -->|IS_NOTEBOOK True| E
    J -->|IS_NOTEBOOK False| F

## Detailed behavior (component implementation notes):
- __new__(cls, x):
    - Takes x (any value accepted by str()) and returns a new HypertoolsBackend instance containing str(x).
    - No additional validation.

- __eq__(self, other) -> bool:
    - Compares the casefold()ed underlying string values of self and other (converted to str(other) before casefold), returning True if equal.
    - If other is not string-like, str(other) is still used (matching Python str semantics).

- __hash__(self) -> int:
    - Returns the hash of the casefold()ed underlying string (same key used by __eq__ to keep hash/equality consistent).

- __getattribute__(self, name):
    - If the attribute name exists on the built-in str type (hasattr(str, name) is True), this method returns a bound wrapper for that str method.
    - The wrapper calls the underlying str method (via super()), capturing the return value.
    - Wrapper return handling:
        * If the return value is a str -> wrap in HypertoolsBackend(return_value) and return it.
        * If return value is a list, tuple, or set -> convert each element v into HypertoolsBackend(v) and return a collection of the same type (i.e., list([...]), tuple([...]), or set({...})).
        * Otherwise -> return the original value unchanged.
    - If the attribute is not a member of str, delegate to normal attribute lookup (super().__getattribute__(name)).
    - Note: This implementation only intercepts methods/attributes that exist on str; custom attributes or new methods on subclasses will be fetched normally.

- as_ipython(self) -> HypertoolsBackend:
    - Performs: default_key = BACKEND_MAPPING.equivalents[self]
    - Then returns HypertoolsBackend(BACKEND_MAPPING.py_to_ipy[default_key])
    - Expected behavior:
        * Treats self as a key into BACKEND_MAPPING.equivalents (the mapping must accept string-like keys equal to the HypertoolsBackend instance).
        * If the equivalents lookup or the py_to_ipy lookup fails (KeyError), the method will propagate the KeyError; callers may catch this and wrap as HypertoolsBackendError if desired.

- as_python(self) -> HypertoolsBackend:
    - Performs: default_key = BACKEND_MAPPING.equivalents[self]
    - Then returns HypertoolsBackend(BACKEND_MAPPING.ipy_to_py[default_key])
    - Same lookup/error semantics as as_ipython.

- normalize(self) -> HypertoolsBackend:
    - Returns as_ipython() if IS_NOTEBOOK is truthy; otherwise returns as_python().

## Raises:
- __new__: does not raise beyond exceptions from str() conversion (e.g., if provided object raises during __str__).
- as_ipython / as_python:
    - KeyError: if BACKEND_MAPPING.equivalents does not contain the backend value or if the subsequent mapping (py_to_ipy / ipy_to_py) does not contain the canonical key.
    - TypeError/AttributeError: if BACKEND_MAPPING is not an object with the expected attributes; these errors will propagate.
    - Recommendation: callers may catch KeyError and re-raise HypertoolsBackendError with a clearer message (module imports HypertoolsBackendError from _shared.exceptions).
- normalize:
    - Same as as_ipython/as_python since it delegates to them; may also raise if IS_NOTEBOOK is not defined as a boolean (AttributeError/NameError if not present).

## Edge cases and constraints:
- The code assumes BACKEND_MAPPING.equivalents can accept the HypertoolsBackend instance as a dictionary key; because HypertoolsBackend hashes using casefold(), its hash and equality are case-insensitive, so equivalents should be keyed consistently (prefer canonical lower-case keys) or be tolerant of casefolded keys.
- __getattribute__ wraps return values of str methods only for types str, list, tuple, set. Other iterable types (e.g., generator, deque, numpy arrays) are returned unchanged; if conversion is desired for other iterables, modify the isinstance check accordingly.
- For set returns, element order is undefined after wrapping — callers should not rely on order.
- The class does not validate that the backend names returned by mapping exist in matplotlib or are loadable modules; that validation is responsibility of higher-level code.

## Example:
- Creation:
    hb = HypertoolsBackend("TkAgg")
- Case-insensitive comparison and hashing:
    HypertoolsBackend("TkAgg") == HypertoolsBackend("tkagg")  # True
    hash(HypertoolsBackend("TkAgg")) == hash(HypertoolsBackend("tkagg"))  # True
- Using str methods and preserving type:
    hb2 = hb.replace("Tk", "tk")  # hb2 is HypertoolsBackend("tkagg")
    parts = hb.split("k")  # parts is a list of HypertoolsBackend objects for each split piece
- Mapping via BACKEND_MAPPING (assuming BACKEND_MAPPING defined and configured):
    ipy = hb.as_ipython()  # returns a HypertoolsBackend with the IPython backend name
    py = hb.as_python()    # returns a HypertoolsBackend with the Python backend name
    normalized = hb.normalize()  # resolves based on IS_NOTEBOOK

Notes for reimplementation:
- Reimplement exactly as a subclass of str with __new__ returning super().__new__(cls, x).
- Ensure __eq__ and __hash__ use casefold() for stable, case-insensitive behavior.
- Implement __getattribute__ to detect str methods and wrap return values as described (be careful to bind the wrapper properly so methods remain descriptors).
- Provide clear error messages at the module level for missing or misconfigured BACKEND_MAPPING and IS_NOTEBOOK if desired (e.g., raise HypertoolsBackendError in wrapper functions that call as_ipython/as_python).

### `hypertools.plot.backend.HypertoolsBackend.__new__` · *method*

## Summary:
Creates and returns a new HypertoolsBackend instance (a str subclass) representing the provided input value; effects the object's creation state by producing the immutable string-value instance.

## Description:
This __new__ method is invoked when a HypertoolsBackend is instantiated (e.g., HypertoolsBackend(value)). Typical call sites include:
- HypertoolsBackend(...) calls in this class's helpers such as as_ipython, as_python, and normalize.
- Any other module code that constructs backend identifiers using HypertoolsBackend(...).

Lifecycle/context:
- Executed at object allocation time, before __init__ (if present). It is responsible for creating the underlying immutable string object for the subclass so later instance methods operate on a properly-constructed str-derived object.

Why this method exists:
- Because HypertoolsBackend subclasses the immutable built-in str type, object creation must be performed in __new__ rather than __init__ so the string value is embedded in the instance at creation time. The method delegates to the built-in str.__new__ implementation (via super()) ensuring the returned object is a HypertoolsBackend containing the correct string content.

## Args:
    x (Any): Value to convert into the backend string. Accepted values are the same as those accepted by Python's built-in str constructor (for example: str, bytes with appropriate decoding, numbers, or any object implementable via __str__). There is no default.

## Returns:
    HypertoolsBackend: A newly-created instance of the HypertoolsBackend subclass of str whose content is the string produced by the built-in str.__new__(cls, x) operation (effectively equivalent to str(x) for typical inputs). The returned object is immutable (as a str) and ready for use by other HypertoolsBackend methods.

    Edge cases:
    - When x is already a str or HypertoolsBackend, the returned instance will be a HypertoolsBackend wrapping that same string value (not necessarily the same object identity).
    - If x is a bytes object or other special types, creation follows built-in str semantics (which may require decoding parameters if used differently elsewhere).

## Raises:
    TypeError: If the underlying built-in str.__new__ rejects the provided x (e.g., an invalid argument type in contexts where str.__new__ cannot handle it). This originates from the base implementation; __new__ does not wrap or alter that exception.
    MemoryError: Possible if system memory allocation for the new string object fails (propagated from Python runtime).

## State Changes:
    Attributes READ:
        - None: __new__ does not access instance attributes (the instance does not yet exist). It also does not read class-level attributes.
    Attributes WRITTEN:
        - None on existing objects: __new__ creates and returns a new object but does not mutate any existing self.<attr> fields.

## Constraints:
    Preconditions:
        - cls must be a subclass of str (it is, by declaration). Callers must provide exactly one positional argument as defined here (the code's signature accepts a single argument x).
        - x must be acceptable to the built-in str constructor semantics.

    Postconditions:
        - A HypertoolsBackend instance is returned whose string value equals the result produced by str.__new__(cls, x).
        - No external state is modified and no instance attributes are set by this method (initialization of any additional attributes would occur in __init__, if implemented).

## Side Effects:
    - None visible: no I/O, no logging, no modification of external objects or global state. The only effect is allocation and return of a new HypertoolsBackend (str) object.

### `hypertools.plot.backend.HypertoolsBackend.__eq__` · *method*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Performs a case-insensitive equality comparison between this backend's string value and another object's string representation, returning a boolean without mutating either operand.

## Description:
This method is invoked whenever Python compares a HypertoolsBackend instance with another object using the equality operator (==) or when equality is required by container operations (e.g., list membership checks, set comparisons, or during dictionary key resolution when hash collisions occur). It centralizes case-insensitive comparison semantics for backend identifiers so that backend names are treated equivalently regardless of letter case or Unicode case variants.

The logic is implemented as a dedicated method so that every equality check on the HypertoolsBackend type consistently uses Unicode-aware, casefold-based comparison rather than the default str equality. Keeping it here (on the str subclass) ensures the behavior is automatic across all call sites without duplicating comparison logic.

## Args:
    other (object): Any Python object. The object will be converted to its string representation via str(other) and then compared casefolded. No specific type is required.

## Returns:
    bool: True if str(self).casefold() equals str(other).casefold(); False otherwise.
    - Typical True examples: comparing backend names that differ only in case or Unicode case variants.
    - Edge-case values: non-string operands are coerced by str(); e.g., None compares as 'none' and will match another 'None' case-insensitively.

## Raises:
    None explicitly. The method does not raise under normal circumstances. (Note: if str(other) raises due to a pathological __str__ implementation on other, that exception will propagate.)

## State Changes:
    Attributes READ:
        - the object's intrinsic string value via str(self) (no attribute names on self are modified)
    Attributes WRITTEN:
        - none (method is read-only and does not mutate self or other)

## Constraints:
    Preconditions:
        - self must be a HypertoolsBackend (subclass of str). This method relies on str(self) to obtain the textual backend identifier.
        - No requirements on other; it may be any object but will be coerced via str(other).
    Postconditions:
        - Returns a boolean and leaves both operands unmodified.
        - Comparison semantics are Unicode-aware and case-insensitive due to use of casefold().

## Side Effects:
    - None: no I/O, no external calls, and no mutation of objects outside of reading str(self) and str(other).
    - Any exception originates only from the str() conversion of other (if that conversion itself raises).

### `hypertools.plot.backend.HypertoolsBackend.__getattribute__` · *method*

## Summary:
Intercepts attribute lookups on the str-subclass instance and, for attributes that exist on the built-in str type, returns a bound wrapper that calls the corresponding str implementation on the underlying value and post-processes its return value so that returned strings and collections of strings are converted back into HypertoolsBackend instances. For attributes not present on str, defers to normal attribute lookup.

## Description:
- When Python resolves an attribute access on a HypertoolsBackend instance (for example, when code evaluates instance.upper or instance.split), this __getattribute__ implementation runs.
- If the requested attribute name exists on the built-in str type, this method does not return the raw str attribute. Instead it constructs and returns a bound wrapper which, when invoked, calls the corresponding str attribute/method on the superclass (the underlying string value) and then wraps certain return values:
    - If the str method returns a str, it is returned as a new HypertoolsBackend instance.
    - If the str method returns a sequence/collection of items of type list, tuple, or set, a new collection of the same container type is constructed with each element passed through HypertoolsBackend(...) and returned.
    - All other return values are returned unchanged.
- If the requested attribute name is not defined on str, attribute resolution falls back to the normal superclass behavior by calling super().__getattribute__(name).
- Known callers and contexts:
    - Any user or internal code that accesses str-like methods on HypertoolsBackend instances: e.g., calling methods such as upper(), lower(), split(), join(), replace(), find(), or any other attribute defined on str.
    - This happens at runtime whenever attribute access is performed on a HypertoolsBackend instance — i.e., during normal usage of backend strings, during mapping/normalization operations, or when other HypertoolsBackend methods call str methods on self.
- Why this is implemented as __getattribute__:
    - The behavior must transparently apply to all attribute accesses that correspond to built-in str members across the whole class. Centralizing the logic in __getattribute__ ensures consistent wrapping of return values (preserving the HypertoolsBackend type where appropriate) without needing to override every individual str method.

## Args:
    name (str): The attribute name being accessed. Python's attribute lookup machinery always supplies a str; callers must not rely on passing non-string types.

## Returns:
    object:
        - If name is a member of built-in str:
            - A bound callable (the wrapper) is returned. That callable, when invoked, calls the corresponding str attribute on the superclass and returns:
                - HypertoolsBackend(value) if the underlying str-call returned a str-like value.
                - An instance of the same collection type (list, tuple, or set) containing HypertoolsBackend(element) for each element if the underlying str-call returned a list, tuple, or set.
                - The original value unchanged for any other return types.
            - Note: attribute access itself (i.e., before calling the returned callable) returns the wrapper object; the actual wrapping of return values occurs when that wrapper is invoked.
        - If name is not a member of built-in str:
            - The attribute value resolved by the normal superclass lookup (super().__getattribute__(name)) is returned.

## Raises:
    AttributeError:
        - If name is not present on str and not present on the instance/class, super().__getattribute__(name) will raise AttributeError as in normal attribute lookup.
    Any exception raised by the underlying str attribute call:
        - If the wrapper is invoked, any exceptions thrown by the underlying str implementation (for example TypeError from invalid arguments) propagate through unchanged.
    TypeError:
        - If name exists on str but points to a non-callable descriptor and the returned wrapper is subsequently invoked as a function, a TypeError may be raised at call time by the underlying object.

## State Changes:
- Attributes READ:
    - None of self's instance attributes are read directly by this method (it does not access self.<attr>).
    - It relies on the inheritance relationship (accessing built-in str attributes) but does not read or mutate instance storage.
- Attributes WRITTEN:
    - None. The method does not set or mutate any attributes on self.
    - It does allocate new HypertoolsBackend instances and new collection objects (list/tuple/set) as return values when wrapping is required.

## Constraints:
- Preconditions:
    - self must be an instance of HypertoolsBackend (method is expected to be invoked as an instance attribute lookup).
    - name should be a string (Python attribute lookup supplies a str).
    - The built-in str attribute named by name must exist for the wrapping branch to be taken; this method tests membership via hasattr(str, name).
- Postconditions:
    - This call does not mutate the state of self.
    - If name corresponds to a str attribute and the wrapper is invoked, any str return values are converted to HypertoolsBackend and returned; list/tuple/set return values are converted to the same container type with each element wrapped by HypertoolsBackend.
    - If name does not correspond to a str attribute, attribute lookup behaves exactly as default super().__getattribute__ would.

## Side Effects:
- Allocates new HypertoolsBackend instances when wrapping returned str values.
- Allocates new collection objects (list, tuple, or set) when wrapping returned collections.
- May execute arbitrary code inside the underlying str method being invoked; exceptions and side effects from those str methods propagate.
- No I/O or external service calls are performed by this method itself.

### `hypertools.plot.backend.HypertoolsBackend.__hash__` · *method*

## Summary:
Returns a deterministic integer hash computed from the object's string representation after Unicode-aware, case-insensitive normalization, so that objects whose string forms differ only by case produce the same hash.

## Description:
This method computes the object's hash by:
- Converting the object to its string form via the built-in str(self).
- Normalizing that string with str.casefold() to perform aggressive, Unicode-aware, case-insensitive folding.
- Computing the hash of the normalized string with the built-in string hash implementation (str.__hash__).

Known callers and typical context:
- Standard Python operations that request an object's hash: the built-in hash() function, use as keys in dicts, membership in sets, and other hashed-collection operations.
- Within object lifecycles, this method is invoked when the instance is placed into or looked up in hashed collections or when hash(self) is explicitly called.
- This documentation does not assert any project-specific callers inspected in the repository.

Why this is its own method:
- Encapsulates a clear policy for object hashing (case-insensitive, Unicode-aware) in one place, making the behavior consistent across all hashed uses.
- Uses str.__hash__ explicitly to compute the native string hash (instead of calling hash(normalized_string)) and isolates the normalization and hashing steps so any future changes (e.g., different normalization) are localized.

## Args:
This method takes no explicit parameters beyond self.

## Returns:
int
- The integer hash value produced by str.__hash__ for the normalized string.
- Edge cases:
    - If str(self) produces different values across time (because the instance's state or __str__ output changes), the returned hash will vary accordingly.
    - The return value is the same for any two objects whose str(...) results are identical after casefold() normalization.

## Raises:
- Any exception raised by str(self) or by invoking casefold() on the resulting string will propagate unchanged. Typical examples include:
    - Exceptions thrown from a custom __str__ implementation (any exception type).
    - AttributeError or TypeError if a custom __str__/casefold path misbehaves.
- The method itself performs no explicit try/except handling; it does not suppress or wrap these exceptions.

## State Changes:
Attributes READ:
- None directly (no explicit self.<attr> access in this method).
- Note: calling str(self) may invoke the instance's __str__ implementation, which might read instance attributes; those reads occur inside that invoked code, not directly in this method.

Attributes WRITTEN:
- None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
- str(self) must succeed and return a Python str object (or at least an object with a valid casefold() method); otherwise an exception will be raised and propagated.
- The class should ensure that if it defines __eq__, the equality semantics are compatible with this hashing strategy (i.e., if equality is intended to be case-insensitive, this hash implementation helps maintain the hash/equality contract).

Postconditions:
- Returns an int corresponding to the hash of the casefolded string representation.
- The method leaves the object state unchanged.

## Side Effects:
- None performed by this method itself (no I/O, no global state changes).
- Indirect side effects are possible if the object's __str__ implementation has side effects; those are outside this method's control and will not be suppressed.

### `hypertools.plot.backend.HypertoolsBackend.as_ipython` · *method*

## Summary:
Return a new HypertoolsBackend that is the IPython/Jupyter notebook equivalent of this backend string; the method does not mutate the receiver.

## Description:
- Known callers:
    - HypertoolsBackend.normalize: called when runtime detection determines execution is inside an IPython/Jupyter notebook; normalize delegates to as_ipython() to obtain the notebook-compatible backend identifier.
- Lifecycle/context:
    - Used at runtime when code needs the backend identifier appropriate for IPython inline rendering rather than the Python (non-notebook) backend name.
- Rationale for separate method:
    - Encapsulates the two-step lookup required to convert an instance-specific backend identifier to the canonical key and then to the IPython backend identifier. Keeping this conversion separate avoids duplicating mapping logic and keeps environment-detection (e.g., in normalize) separate from mapping logic.

## Args:
    self (HypertoolsBackend): Backend identifier instance (subclass of str) to convert.
        - Allowed values: any string-like value for which BACKEND_MAPPING.equivalents contains an entry keyed by this instance.
        - No default (implicit receiver).

## Returns:
    HypertoolsBackend
        - A freshly constructed HypertoolsBackend instance wrapping the string value found in BACKEND_MAPPING.py_to_ipy for the canonical/default key.
        - Always returns a HypertoolsBackend (never None) on successful mapping resolution.

## Raises:
    NameError
        - If the global name BACKEND_MAPPING is not defined in the module namespace.
    AttributeError
        - If BACKEND_MAPPING exists but does not expose either of the required mapping attributes: .equivalents or .py_to_ipy.
    KeyError
        - If self is not present as a key in BACKEND_MAPPING.equivalents.
        - Or if the canonical key (default_key) obtained from BACKEND_MAPPING.equivalents[self] is not present in BACKEND_MAPPING.py_to_ipy.
    TypeError
        - If the objects treated as mappings are not subscriptable/mapping-like (e.g., BACKEND_MAPPING.equivalents is not indexable).
        - If the final mapped value passed to the HypertoolsBackend constructor is not a valid string-like object and the constructor raises a TypeError.
    (Any exceptions raised by the HypertoolsBackend constructor or by underlying dict/index operations will propagate; this method does not catch them.)

## State Changes:
- Attributes READ:
    - Reads the global BACKEND_MAPPING object and specifically:
        - BACKEND_MAPPING.equivalents (indexed with self)
        - BACKEND_MAPPING.py_to_ipy (indexed with the canonical/default key)
    - Uses self as a mapping key (this invokes HypertoolsBackend.__hash__ and/or __eq__ for dictionary lookup).
- Attributes WRITTEN:
    - None. The method does not modify self, BACKEND_MAPPING, or any other module/global state.

## Constraints:
- Preconditions:
    - A module-level BACKEND_MAPPING must be defined and must provide mapping-like attributes:
        - .equivalents: mapping from backend identifier (keys compatible with HypertoolsBackend) to a canonical/default key.
        - .py_to_ipy: mapping from canonical/default keys to the IPython-compatible backend identifier strings.
    - self must be a valid key in BACKEND_MAPPING.equivalents.
    - The canonical/default key obtained from equivalents[self] must be present in .py_to_ipy.
- Postconditions:
    - On success, returns a HypertoolsBackend wrapping the IPython backend string corresponding to self.
    - No side effects or mutations are made to the object or global mappings.

## Side Effects:
    - No I/O, logging, or external service calls.
    - Reads global mapping state (BACKEND_MAPPING) but does not mutate it.
    - May raise exceptions originating from global mapping lookups or from the HypertoolsBackend constructor; these exceptions propagate to the caller.

### `hypertools.plot.backend.HypertoolsBackend.as_python` · *method*

## Summary:
Produce a new HypertoolsBackend representing the Python (non‑IPython) matplotlib backend equivalent for this backend identifier; the receiver is not mutated.

## Description:
This method performs a simple two-step lookup using the module-level BACKEND_MAPPING object:
1. Obtain a canonical backend key for the receiver via BACKEND_MAPPING.equivalents[self].
2. Translate that canonical key to the Python/backend name via BACKEND_MAPPING.ipy_to_py[canonical_key] and wrap the result in a HypertoolsBackend which is returned.

Known callers and lifecycle context:
- HypertoolsBackend.normalize: calls this method when the environment is not a Jupyter/IPython notebook (IS_NOTEBOOK is False). In that plotting/configuration stage the code needs a backend identifier suitable for configuring matplotlib in plain Python environments.
- Other code that needs the Python-side variant of a backend identifier may call this before configuring matplotlib.

Why this is its own method:
- Keeps conversion logic symmetric with as_ipython and localized on the HypertoolsBackend type, avoiding repeated mapping lookups throughout the codebase and making testing straightforward.

## Args:
- None.

## Returns:
- HypertoolsBackend: a newly created HypertoolsBackend instance wrapping the Python backend name obtained from the mapping.
  - Because HypertoolsBackend is a str subclass constructed via str.__new__, the stored value is the stringified result of BACKEND_MAPPING.ipy_to_py[canonical_key] (i.e., str(value) semantics at construction time).
  - Typical returned values are string-like backend names (for example, 'tk', 'qt5', 'agg'), wrapped as HypertoolsBackend.

## Raises:
- KeyError: if the lookup BACKEND_MAPPING.equivalents[self] fails because self is not a key in that mapping.
- KeyError: if BACKEND_MAPPING.ipy_to_py[canonical_key] fails because the canonical key is not present there.
- Any exception raised by the mapping objects' __getitem__ implementations will propagate; this method performs no additional exception handling.

## State Changes:
Attributes READ:
- self (used as the lookup key; HypertoolsBackend implements case-insensitive equality and hashing which affects mapping lookup behavior).
- BACKEND_MAPPING.equivalents (consulted to obtain the canonical key).
- BACKEND_MAPPING.ipy_to_py (consulted to obtain the Python backend name).

Attributes WRITTEN:
- None. The method does not modify self, BACKEND_MAPPING, or any other global state.

## Constraints:
Preconditions:
- The module-level BACKEND_MAPPING must be defined and provide both:
  - an attribute .equivalents supporting lookup with the receiver as key, and
  - an attribute .ipy_to_py supporting lookup with the canonical key returned by .equivalents.
- The receiver is expected to be a HypertoolsBackend instance (this method is an instance method on that class).
- Callers that depend on case-insensitive lookup should ensure BACKEND_MAPPING keys are compatible with HypertoolsBackend's casefold-based equality/hash semantics.

Postconditions:
- On successful return, the caller has a HypertoolsBackend whose value equals the string form of BACKEND_MAPPING.ipy_to_py[canonical_key].
- No mutation of the receiver or of BACKEND_MAPPING occurs.

## Side Effects:
- None intrinsic to this method: no I/O, logging, or network activity is performed here.
- Only dictionary-like lookups and a string-construction operation occur; any side effects from custom mapping objects' __getitem__ would propagate but are not introduced by this method itself.

## Usage note:
- Typical usage is indirect via HypertoolsBackend.normalize(), which returns this method's result when running outside a notebook; use this when you need to configure matplotlib with the backend name appropriate for Python environments.

### `hypertools.plot.backend.HypertoolsBackend.normalize` · *method*

## Summary:
Return the backend identifier appropriate for the current execution environment by delegating to the notebook-specific or Python-specific converter; does not mutate the receiver.

## Description:
- Known callers:
    - Plotting and backend-configuration code that needs a backend identifier adapted to the runtime environment (e.g., code that configures matplotlib before rendering).
    - Higher-level convenience functions that normalize user-provided backend names before using them to configure plotting behavior.

- Lifecycle / context:
    - Invoked during plotting/configuration stages when code must choose the correct matplotlib/backend identifier for the current runtime (Jupyter/IPython notebook vs. plain Python process).
    - Executed after a HypertoolsBackend instance has been constructed and a decision is required about which concrete backend string to use.

- Why this is its own method:
    - Encapsulates the simple environment-based dispatch (notebook vs. non-notebook) so that callers need not check the environment themselves.
    - Keeps environment-detection logic separate from the mapping logic implemented by as_ipython() and as_python(), promoting reuse and single-responsibility for each helper.

## Args:
    self (HypertoolsBackend): Instance of the backend identifier (receiver). No other arguments.

## Returns:
    HypertoolsBackend
        - If the module-level flag IS_NOTEBOOK is truthy, returns the result of self.as_ipython().
        - Otherwise, returns the result of self.as_python().
        - The returned value is a new HypertoolsBackend instance wrapping the mapped backend string (never None on successful mapping).

## Raises:
    - Any exception raised by self.as_ipython() or self.as_python() will propagate unchanged.
    - Typical propagated exceptions (depending on which branch runs):
        - NameError: if module-level BACKEND_MAPPING is missing (possible from as_ipython).
        - AttributeError: if BACKEND_MAPPING does not expose required mapping attributes (possible from as_ipython).
        - KeyError: if self is not found in BACKEND_MAPPING.equivalents or if the canonical key is missing in the target mapping (possible from both converters).
        - TypeError: if mapping objects are not subscriptable or the final mapped value is of an invalid type for HypertoolsBackend construction (possible from as_ipython/as_python).
    - No exceptions are created by normalize itself; it only selects the branch and delegates.

## State Changes:
- Attributes READ:
    - IS_NOTEBOOK (module-level flag used to select branch).
    - self (used indirectly by as_ipython()/as_python() for mapping lookup; those methods read BACKEND_MAPPING.*).
    - BACKEND_MAPPING.equivalents and either BACKEND_MAPPING.py_to_ipy or BACKEND_MAPPING.ipy_to_py are read by as_ipython()/as_python() respectively.

- Attributes WRITTEN:
    - None. normalize does not mutate self or any module/global state.

## Constraints:
- Preconditions:
    - The module-level boolean-like flag IS_NOTEBOOK must be defined. Its truthiness determines which conversion method is invoked.
    - The receiver must be a valid HypertoolsBackend instance suitable for use as a lookup key in BACKEND_MAPPING.equivalents (i.e., BACKEND_MAPPING.equivalents must accept the receiver as a key).
    - The module-level BACKEND_MAPPING must provide the mappings required by the chosen converter:
        - If IS_NOTEBOOK is true: BACKEND_MAPPING.equivalents and BACKEND_MAPPING.py_to_ipy must be present and valid.
        - If IS_NOTEBOOK is false: BACKEND_MAPPING.equivalents and BACKEND_MAPPING.ipy_to_py must be present and valid.

- Postconditions:
    - On successful return, a HypertoolsBackend instance is returned whose string value corresponds to the environment-appropriate backend (IPython/Jupyter form if IS_NOTEBOOK truthy, otherwise Python form).
    - No mutation of the receiver or global mapping objects occurs.

## Side Effects:
    - No I/O, logging, or network activity.
    - Calls into as_ipython() or as_python(), which perform mapping lookups; any side effects from custom mapping objects' __getitem__ or HypertoolsBackend constructor may occur and will propagate, but normalize itself does not introduce additional side effects.

## `hypertools.plot.backend._init_backend` · *function*

## Summary:
Initializes and selects an appropriate matplotlib backend for the hypertools plotting subsystem, records the detected environment (notebook vs. non-notebook), and configures module-level helpers and mappings used elsewhere for switching and resetting backends.

## Description:
This function encapsulates detection and selection of a matplotlib backend and populates module-global variables that other plotting utilities consult.

Known callers and typical usage:
- Normally called once during import/initialization of the hypertools.plot.backend module so that plotting code can rely on consistent backend-related globals before creating figures.
- May be called explicitly by initialization or re-configuration routines when the environment changes or tests require reinitialization.

Why this is a separate function:
- Backend detection involves several steps (IPython detection, probing multiple candidate interactive backends, honoring an optional environment override, selecting fallbacks) and must set multiple module-level variables consistently. Extracting the logic prevents duplication and centralizes side effects and error handling.

## Args:
- None.

## Returns:
- None. The function returns no value; it communicates results via module-global variables (see Side Effects and Postconditions).

## Raises:
The function handles some exceptions internally but may raise others:

Handled internally (no propagation out of the try/except block that detects IPython):
- NameError, AssertionError: caught when calling get_ipython() or asserting IPKernelApp presence; triggers the non-notebook (regular) backend selection path.

Handled within backend selection loop:
- ImportError, NameError, ValueError: caught for each mpl.use(candidate_backend) attempt; the loop continues to the next candidate backend.

Handled during notebook branch:
- ImportError from mpl.use('nbAgg') is caught and causes falling back to the inline static backend.

Potentially propagated exceptions (not caught inside this function):
- NameError / UnboundLocalError resulting from a likely bug: when HYPERTOOLS_BACKEND environment variable is present and its lowercase value matches a candidate backend, the code attempts to slice the candidate tuple using an undefined name HYPERTOOLS_BACKEND instead of the local env_backend. That will raise NameError at runtime in the non-notebook path during env var processing. If that or any other uncaught exception occurs before the variable working_backend is set, the finally block still executes and may raise UnboundLocalError (or a different exception) when the code later tries to use working_backend.
- Any exceptions raised by BackendMapping(BACKEND_KEYS) or HypertoolsBackend(working_backend).normalize() will propagate (for example, if BACKEND_KEYS is invalid or HypertoolsBackend refuses the supplied backend string).
- Other unforeseen NameError/AttributeError if required module-level symbols referenced by this function are not defined (see Preconditions).

## Constraints:
Preconditions (what must be true before calling):
- A module-level symbol named mpl must be present and expose get_backend() and use() functions consistent with matplotlib semantics. If the module imported matplotlib under a different name, mpl must be bound to that module before calling.
- The following names must exist in module scope and be valid callables or values referenced by the function: BACKEND_KEYS, BackendMapping, HypertoolsBackend, _switch_backend_regular, _switch_backend_notebook, _reset_backend_notebook, _block_greedy_completer_execution, and get_ipython (get_ipython will usually be provided by IPython when available).
- The process is permitted to read environment variables and emit warnings.

Postconditions (guaranteed after a successful return):
- BACKEND_MAPPING is assigned to BackendMapping(BACKEND_KEYS).
- HYPERTOOLS_BACKEND is set to HypertoolsBackend(working_backend).normalize(), where working_backend is the final backend string chosen by the function.
- IS_NOTEBOOK is True if an IPython kernel was detected and the function followed the notebook branch; otherwise IS_NOTEBOOK is False.
- IPYTHON_INSTANCE is set to the get_ipython() return value if detection succeeded; otherwise it is not set by this function.
- switch_backend and reset_backend are set to environment-appropriate functions:
    - In notebook environment: switch_backend -> _switch_backend_notebook, reset_backend -> _reset_backend_notebook.
    - In regular environment: switch_backend and reset_backend both refer to _switch_backend_regular.
- The original matplotlib backend present at function entry (curr_backend) is restored on exit.

## Side Effects:
- Writes/sets module-global variables: BACKEND_MAPPING, potentially BACKEND_WARNING (only in fallback cases), HYPERTOOLS_BACKEND, IPYTHON_INSTANCE (conditionally), IS_NOTEBOOK, reset_backend, and switch_backend.
- Calls mpl.get_backend() to save the currently active backend and mpl.use(...) repeatedly to probe or set backends; the original backend is restored in a finally block via mpl.use(curr_backend).
- Reads environment variable HYPERTOOLS_BACKEND using getenv("HYPERTOOLS_BACKEND").
- Emits warnings.warn in two cases:
    - When nbAgg is unavailable in a notebook environment, BACKEND_WARNING is set to a message about falling back to inline static plots.
    - When no tested interactive backend works in a regular environment, BACKEND_WARNING is set to a message about falling back to 'Agg'.
    - When an environment-specified backend (HYPERTOOLS_BACKEND) was requested but the final selected working_backend does not match it (case-insensitive), a warnings.warn informs the user that the requested backend could not be used.
- Calls _block_greedy_completer_execution() when not running in an IPython kernel; this may have its own side effects (it is assumed to modify completer behavior).

No file or network I/O is performed by this function itself.

## Important Implementation Note / Known Issue:
- The source code contains a likely bug in the non-notebook environment branch when processing the HYPERTOOLS_BACKEND environment variable. The intent appears to be to move the environment-specified backend to the front of the candidate backends tuple; however, the code slices the tuple using the undefined name HYPERTOOLS_BACKEND instead of the local env_backend. If env_backend is not None and its lowercase value matches a candidate (case-insensitively), this will raise NameError when executing the slice expression, causing the function to abort early. If this occurs before working_backend is defined, the finally block will still execute and may raise UnboundLocalError when attempting to use working_backend. Consumers should be aware that setting HYPERTOOLS_BACKEND in the environment can trigger this bug in the current implementation.

## Control Flow:
flowchart TD
    Start --> SaveCurrBackend[Save current backend via mpl.get_backend()]
    SaveCurrBackend --> TryIPython[Try: IPython detection (get_ipython() + assert 'IPKernelApp' in config)]
    TryIPython -->|success| NotebookBranch[Set IS_NOTEBOOK = True; IPYTHON_INSTANCE set]
    NotebookBranch --> TryNbAgg[Try mpl.use('nbAgg')]
    TryNbAgg -->|success| NbAggOK[working_backend = 'nbAgg']
    TryNbAgg -->|ImportError| NbAggFail[Set BACKEND_WARNING to notebook fallback; working_backend = 'inline']
    NbAggOK --> SetNotebookSwitchers[set switch_backend = _switch_backend_notebook; reset_backend = _reset_backend_notebook]
    NbAggFail --> SetNotebookSwitchers
    TryIPython -->|NameError or AssertionError| RegularBranch[Call _block_greedy_completer_execution(); set IS_NOTEBOOK = False]
    RegularBranch --> BuildBackendsList[Build ordered candidate backends (platform-dependent); prepend env_backend if present]
    BuildBackendsList --> EnvProcessing{env_backend is not None?}
    EnvProcessing -->|yes| EnvHandling[If env_backend matches candidate list (case-insensitive), attempt to reorder candidates]
    EnvHandling -->|bug present| NameErrorBug[Attempt uses undefined HYPERTOOLS_BACKEND - NameError may be raised]
    EnvProcessing --> ForEachBackend{Loop over candidate backends}
    ForEachBackend -->|mpl.use succeeds| BackendSelected[working_backend = candidate; break loop]
    ForEachBackend -->|mpl.use fails (ImportError/NameError/ValueError)| ContinueLoop[try next candidate]
    ForEachBackend -->|no candidates left| FallbackAgg[Set BACKEND_WARNING about falling back; working_backend = 'Agg']
    BackendSelected --> EnvMismatchCheck{If env_backend specified and final backend differs (case-insensitive)}
    EnvMismatchCheck -->|mismatch| WarnUser[warnings.warn that requested env backend could not be used]
    EnvMismatchCheck --> SetRegularSwitchers[set switch_backend = reset_backend = _switch_backend_regular]
    WarnUser --> SetRegularSwitchers
    NbAggOK --> Finally[Proceed to finally]
    SetRegularSwitchers --> Finally
    Finally --> RestoreCurrBackend[mpl.use(curr_backend) to restore original backend]
    RestoreCurrBackend --> SetMappings[BACKEND_MAPPING = BackendMapping(BACKEND_KEYS); HYPERTOOLS_BACKEND = HypertoolsBackend(working_backend).normalize()]
    SetMappings --> End

## Examples:
- Typical initialization flow (descriptive):
    1. Module import triggers _init_backend().
    2. If running inside an IPython notebook kernel, the function attempts mpl.use('nbAgg') and sets switch/reset helpers to notebook variants. If nbAgg is not available, it falls back to 'inline' and sets BACKEND_WARNING explaining the fallback.
    3. If not running in a notebook, the function tries a list of interactive GUI backends (platform-appropriate), optionally honoring the value of the environment variable HYPERTOOLS_BACKEND by attempting it first. If none succeed, it falls back to the non-interactive 'Agg' backend and records a BACKEND_WARNING.
    4. In all cases the originally active matplotlib backend is restored before the function returns.

- How to respond to failures (recommended):
    - After import/initialization, inspect BACKEND_WARNING to detect silent fallbacks and decide whether to raise an error or log.
    - Avoid relying on environment variable HYPERTOOLS_BACKEND until the known bug is fixed; if you must use it, test that the environment value does not trigger the bug (or patch the code to use env_backend consistently).
    - If an exception propagates from BackendMapping(...) or HypertoolsBackend(...).normalize(), ensure that callers catch these at top-level initialization to provide clearer diagnostics.

Notes:
- The function mutates shared module globals and temporarily manipulates matplotlib's global backend setting. It is intended for early, single-time initialization and not for frequent repeated calls in concurrent contexts.

## `hypertools.plot.backend._block_greedy_completer_execution` · *function*

## Summary:
Checks whether IPython's tab-completer is present in a recent portion of the call stack; if detected, removes specific modules from sys.modules and raises a plain Exception to abort the completer's execution.

## Description:
This function inspects a slice of the current Python call stack to detect whether IPython's greedy tab-completer implementation (a file whose path ends with 'IPython/core/completerlib.py') appears among the inspected frames. If such a frame is found, the function attempts to remove the modules 'hypertools.plot', 'hypertools.plot.backend', and 'numpy' from sys.modules (silently ignoring any that are not present) and then raises a bare Exception (no message). If no completer frame is found in the inspected slice, the function returns normally.

Known callers within the provided codebase:
    - No direct callers were discovered in the supplied repository snapshot. The function is defined in hypertools.plot.backend and is intended as a utility to be invoked by modules that need to avoid unwanted import-time side effects caused by IPython's tab-completer.

Why this is a separate function:
    - Encapsulation: centralizes the completer-detection and abort behavior in one place so callers do not duplicate stack-inspection and sys.modules mutation logic.
    - Safety boundary: isolates the dangerous actions (mutating sys.modules and raising an Exception) so callers can deliberately choose whether and how to invoke and handle this behavior.

## Args:
    - None

## Returns:
    - None when no IPython completer frame is found in the inspected stack slice.
    - No return value when the completer is detected because the function raises a plain Exception in that case.

## Raises:
    - Exception: A plain Exception (no message) is raised if the function finds any inspected stack FrameSummary entry whose filename ends with 'IPython/core/completerlib.py'.
        - Exact detection expression: next(entry for entry in stack_trace if entry.filename.endswith(completer_module)) succeeds (does not raise StopIteration).
    - No other exceptions are intentionally propagated by this function in normal operation: the removal of modules uses sys.modules.pop inside a try/except that swallows KeyError for missing keys.

## Constraints:
Preconditions:
    - The standard traceback.extract_stack() is available and returns FrameSummary objects with a filename attribute (true for the standard library traceback).
    - sys.modules behaves like the standard module mapping (supports .pop and KeyError semantics).

Precise stack-slice behavior:
    - The function computes traceback.extract_stack()[-4::-1].
    - This slice starts at the fourth-from-last frame in the full stack (index -4) and then traverses backwards to the oldest frame (step -1). Practically, the three most recent frames (the last three entries of the full extract_stack() result) are excluded from inspection; the search begins at the next older frame and proceeds toward the start of the stack.
    - Effect: only frames older than the most recent three are considered for the presence of IPython's completer file.

Postconditions:
    - If no completer frame is detected: sys.modules is unchanged by this function and the caller continues executing normally.
    - If a completer frame is detected: the keys 'hypertools.plot', 'hypertools.plot.backend', and 'numpy' will have been removed from sys.modules if they were present; execution does not return normally because the function raises Exception.

## Side Effects:
    - Mutates interpreter-global state: pops the module entries for 'hypertools.plot', 'hypertools.plot.backend', and 'numpy' from sys.modules when present. This forces future imports of those names to re-import the modules.
    - Raises a bare Exception (no message), which is intended to abort the completer's execution path. No logging, I/O, network activity, or stdout/stderr output is performed by the function itself.

## Control Flow:
flowchart TD
    A[Call _block_greedy_completer_execution] --> B[Compute stack_trace = traceback.extract_stack()[-4::-1]]
    B --> C{Find entry where entry.filename.endswith('IPython/core/completerlib.py')}
    C -- No --> D[Return None (no changes made)]
    C -- Yes --> E[For each module in ('hypertools.plot','hypertools.plot.backend','numpy') attempt sys.modules.pop(module) and ignore KeyError]
    E --> F[Raise plain Exception (no message)]
    F --> G[Caller does not receive a normal return]

## Examples and recommended caller patterns:
- Typical intent: a module that performs expensive or side-effectful initialization at import time may wish to avoid that initialization when the code is being examined by IPython's tab-completer. Calling this helper gives an explicit, centralized mechanism to detect the completer and abort.

- Recommended handling pattern (prose guidance, not literal code):
    - If invoked at import time, wrap the call in a try/except that catches Exception broadly and then either:
        * skip the expensive initialization and continue importing a lightweight fallback state, or
        * re-raise a more specific exception or log an explanatory message for maintainers, rather than allowing a bare Exception to propagate to end-users.
    - Example (conceptual): A module's initialization could call the helper; if it raises, the module should avoid performing heavy imports or computations and instead register a lazy initializer that runs only during normal execution (not during completion).

Practical notes:
    - Because the function raises a plain Exception with no message when it detects the completer, callers should not treat this as a descriptive error; they should catch Exception and implement clear logging or alternative behavior if desired.
    - The precise stack-slice selection means that only frames older than the three most recent will be inspected; if the environment or IPython version changes how the completer calls occur (for example, additional wrapper frames), detection behavior may change.

## `hypertools.plot.backend._switch_backend_regular` · *function*

## Summary:
Switches Matplotlib's plotting backend to the backend name provided by the backend object; on failure, raises a HypertoolsBackendError with a diagnostic message.

## Description:
This function accepts a backend-like object, obtains the underlying Matplotlib backend name from it, and attempts to set Matplotlib's active backend via matplotlib.pyplot.switch_backend. If any error occurs while switching, the function converts it into a HypertoolsBackendError carrying a helpful message.

Known callers within the provided context:
    - No explicit callers were present in the snippet provided. Typical call sites are higher-level backend-selection utilities or user-facing plotting initialization code that accept a user-specified backend (string or wrapper) and delegate the actual Matplotlib switch to this helper.

Why this is extracted into its own function:
    - Encapsulates the Matplotlib-specific call and its error handling in one place so that higher-level code can focus on backend selection, formatting, or environment-specific adjustments.
    - Centralizes the conversion of diverse backend-related exceptions into a single HypertoolsBackendError type with a clear, user-oriented message.

## Args:
    backend (object): Required. An object implementing an as_python() method that returns the Matplotlib backend name (a string acceptable to matplotlib.pyplot.switch_backend).
        - Expected behavior: backend.as_python() -> str (e.g., "TkAgg", "Qt5Agg", "module://ipykernel.pylab.backend_inline")
        - If backend does not have as_python(), an AttributeError (or similar) will propagate up (this function does not catch attribute-access errors).
        - There are no default values.

## Returns:
    None
    - On success the function returns None after Matplotlib's active backend has been changed.
    - There are no alternative return values; failure is signaled via exception.

## Raises:
    HypertoolsBackendError:
        - Raised whenever any exception occurs during matplotlib.pyplot.switch_backend or while using the backend name returned by backend.as_python().
        - If the original exception is ImportError or ModuleNotFoundError, the HypertoolsBackendError message indicates missing dependencies or platform unavailability for that backend (message includes the backend name).
        - For other exceptions, the HypertoolsBackendError uses a generic message indicating an unexpected error while switching backends (message includes the backend name).
        - The original exception is chained (raised from the original exception), preserving traceback.

    Other exceptions that may propagate (not caught here):
        - AttributeError, TypeError, or any exception raised by backend.as_python() — these will propagate because only exceptions raised from plt.switch_backend are caught and wrapped here.

## Constraints:
    Preconditions:
        - The module-level name plt must reference the matplotlib.pyplot module (or another object providing switch_backend); if not, a NameError will occur before the try/except is reached.
        - The backend argument must provide an as_python() method that returns a string accepted by matplotlib.pyplot.switch_backend.
    Postconditions:
        - If the function returns normally (no exception), Matplotlib's active backend has been set to the returned backend name for the running process.
        - If the function raises HypertoolsBackendError, Matplotlib's backend may be unchanged, partially changed, or in an indeterminate state depending on the underlying failure; callers must treat the backend as potentially unchanged.

## Side Effects:
    - Mutates Matplotlib global state by calling matplotlib.pyplot.switch_backend(backend_name), which changes the active plotting backend for the current Python process.
    - No filesystem, network, or stdout/stderr I/O performed by this function itself, although the backend switch may trigger backend-specific initialization that performs I/O.
    - Raises HypertoolsBackendError on failure (exception chaining preserves original exception and traceback).

## Control Flow:
flowchart TD
    Start --> GetBackendName
    GetBackendName[backend_name = backend.as_python()] --> TrySwitch
    TrySwitch -- success --> End[Return None]
    TrySwitch -- exception e --> IsImportError
    IsImportError{e is ImportError or ModuleNotFoundError}
    IsImportError -- yes --> BuildImportErrMsg[err_msg: Failed to switch... missing dependencies or unavailable on system]
    IsImportError -- no --> BuildGenericErrMsg[err_msg: An unexpected error occurred while trying to switch the plotting backend to {backend}]
    BuildImportErrMsg --> RaiseHypertools
    BuildGenericErrMsg --> RaiseHypertools
    RaiseHypertools --> EndWithException[raise HypertoolsBackendError(err_msg) from e]

## Examples:
Typical usage scenario (described in prose):
    - A higher-level backend selection function receives a user input (either a string or a Backend wrapper). It constructs or receives a backend-like object exposing as_python(), then calls this function to apply the selection. If this function raises HypertoolsBackendError, the caller can present the message to the user or fall back to an alternative backend.

Example (pseudo-code usage; do not assume specific Backend class names exist):
    backend = some_backend_provider(user_choice)   # backend implements as_python() -> "TkAgg"
    try:
        _switch_backend_regular(backend)
    except HypertoolsBackendError as e:
        # Report to user, log the diagnostic message, and optionally select a fallback backend
        handle_backend_error(e)

## `hypertools.plot.backend._switch_backend_notebook` · *function*

## Summary:
Switches the active plotting backend in an IPython / Jupyter notebook environment by running the IPython "matplotlib" line magic for the backend returned by the provided backend object; removes inline-figure flushing callbacks when switching away from the inline backend.

## Description:
This helper executes IPython's "%matplotlib <backend>" magic (via a module-level IPYTHON_INSTANCE) to set the notebook plotting backend to the string produced by backend.as_ipython(). It captures and inspects the magic's stdout to detect two failure cases:
- If the magic raises a KeyError (invalid notebook backend identifier), the function extracts the available backends from the magic's output and raises ValueError indicating the requested backend is not a valid IPython plotting backend.
- If the magic succeeds but prints a GUI-toolkit incompatibility warning that begins with "Warning: Cannot change to a different GUI toolkit", the function falls back to calling _switch_backend_regular(backend) to attempt the Matplotlib-level backend switch; if that fallback fails with HypertoolsBackendError, this function raises a HypertoolsBackendError summarizing both the IPython warning and the fallback failure.

After a successful notebook switch, if the chosen backend string is not 'inline', the function unregisters the inline flush_figures callback from IPYTHON_INSTANCE.events.callbacks['post_execute'] while it is present (this prevents automatic inline flushing behavior from interfering when using non-inline backends).

Known callers within the codebase and typical call sites:
- Higher-level backend-selection utilities or plotting initialization routines that accept a user-specified backend and delegate the notebook-specific switching logic to this function.
- Any code in this module that needs to set the backend in a Jupyter/IPython session rather than via direct Matplotlib API calls.

Why this logic is extracted into its own function:
- Encapsulates IPython-specific behavior (running the "matplotlib" magic, capturing and parsing its stdout, and manipulating IPython event callbacks) separate from Matplotlib-level switching logic.
- Centralizes error classification for notebook contexts: distinguishing an invalid IPython backend (ValueError) from GUI-toolkit incompatibility (which triggers a Matplotlib fallback and may produce HypertoolsBackendError).
- Keeps callers free of low-level stdout capture and callback-unregistration concerns.

## Args:
    backend (object):
        - Required.
        - Expected to implement a method as_ipython() -> str which returns the backend identifier to pass to IPython's "%matplotlib" magic (examples: 'inline', 'qt5', 'tk', 'module://ipykernel.pylab.backend_inline', etc.).
        - No default value.
        - The function does not validate the type beyond calling as_ipython(); any exception raised by as_ipython() (AttributeError, TypeError, etc.) will propagate.

## Returns:
    None
    - On normal completion, the function returns None and the notebook's active plotting backend has been changed (or IPython has been configured to use the requested backend).
    - There are no alternate successful return values.

## Raises:
    ValueError:
        - Raised when IPython's "%matplotlib <backend>" magic raises a KeyError indicating the provided backend identifier is not recognized by IPython.
        - The raised ValueError is chained from the original KeyError and includes a textual list of available backends extracted from the magic's output.
        - Note: the code extracts the last line of the magic's captured output with output_msg.splitlines()[-1]; if output_msg is unexpectedly empty this indexing could raise IndexError (this is an implementation-level edge case that would propagate).

    HypertoolsBackendError:
        - Raised when the IPython magic prints a GUI-toolkit incompatibility warning (output starts with 'Warning: Cannot change to a different GUI toolkit') and the fallback call to _switch_backend_regular(backend) raises HypertoolsBackendError.
        - In this case the function constructs a diagnostic message that includes the IPython warning text and notes that the fallback via Matplotlib failed; the new HypertoolsBackendError is raised and chained from the fallback exception.

    Other exceptions that may propagate:
        - Any exception raised by backend.as_ipython() (e.g., AttributeError if as_ipython does not exist, or exceptions raised by its implementation) will propagate unchanged.
        - NameError if the module-level IPYTHON_INSTANCE is not present.
        - Any other unexpected runtime exceptions (e.g., IndexError when parsing output_msg) will propagate.

## Constraints:
Preconditions:
    - A module-level name IPYTHON_INSTANCE must exist and expose a run_line_magic(name, arg) method and an events attribute with callbacks mapping (IPython API-compatible).
    - The backend argument must provide as_ipython() that returns a string acceptable to IPython's "%matplotlib" magic.
    - The environment is expected to be an IPython/Jupyter kernel; calling this in standard Python without a valid IPYTHON_INSTANCE will raise NameError or attribute errors.

Postconditions:
    - On successful return (no exception), IPython's plotting configuration has been updated to use the backend string returned by backend.as_ipython().
    - If a non-inline backend was selected, the flush_figures function will not remain registered on IPYTHON_INSTANCE.events.callbacks['post_execute'].
    - If a ValueError or HypertoolsBackendError is raised, the caller should assume the plotting backend may be unchanged or in an indeterminate state and should handle or report the error accordingly.

## Side Effects:
    - Executes IPython line magic using IPYTHON_INSTANCE.run_line_magic('matplotlib', backend_string), which writes to stdout; the function captures and suppresses that stdout while inspecting it.
    - May call _switch_backend_regular(backend) (Matplotlib-level switch) as a fallback; that call mutates Matplotlib global state (matplotlib backend) if it succeeds.
    - Mutates IPYTHON_INSTANCE.events.callbacks by unregistering the flush_figures callback while backend != 'inline'.
    - No filesystem, network, or persistent external I/O is performed by this function itself (aside from interactions caused by Matplotlib or backend initialization).
    - Raises ValueError or HypertoolsBackendError to signal failure conditions.

## Control Flow:
flowchart TD
    Start --> GetBackendStr[backend_str = backend.as_ipython()]
    GetBackendStr --> CaptureStdout[redirect stdout to tmp buffer]
    CaptureStdout --> TryMagic[try IPYTHON_INSTANCE.run_line_magic('matplotlib', backend_str)]
    TryMagic -- KeyError e --> MarkExc[exc = e]
    MarkExc --> RunListMagic[IPYTHON_INSTANCE.run_line_magic('matplotlib','-l')]
    TryMagic -- success --> Continue
    Continue --> ReadOutput[output_msg = tmp_stdout.getvalue().strip()]
    ReadOutput --> CloseTmp[tmp_stdout.close()]
    CloseTmp --> IfInvalidExc{exc is not None?}
    IfInvalidExc -- yes --> ExtractBackends[backends_avail = output_msg.splitlines()[-1]]
    ExtractBackends --> RaiseValueError[raise ValueError(... ) from exc]
    IfInvalidExc -- no --> CheckGuiWarning[output_msg startswith 'Warning: Cannot change to a different GUI toolkit'?]
    CheckGuiWarning -- yes --> TryFallback[_switch_backend_regular(backend)]
    TryFallback -- HypertoolsBackendError e --> BuildErrMsg[construct combined diagnostic message]
    BuildErrMsg --> RaiseHypertools[raise HypertoolsBackendError(err_msg) from e]
    TryFallback -- success --> PostProcess
    CheckGuiWarning -- no --> PostProcess
    PostProcess --> IsInline{backend_str != 'inline'?}
    IsInline -- yes --> UnregisterLoop[while flush_figures in callbacks['post_execute'] -> unregister it]
    UnregisterLoop --> End
    IsInline -- no --> End

## Examples:
Typical usage scenario (described in prose):
    - A plotting initialization routine running inside a Jupyter notebook receives a backend wrapper object from user configuration. The wrapper implements as_ipython() to produce the correct IPython backend identifier. The routine calls this function to apply the backend for the notebook session. If this function raises ValueError, the caller reports the invalid backend and may prompt the user to choose from the available backends listed in the exception message. If it raises HypertoolsBackendError, the caller knows that both IPython-level and Matplotlib-level (fallback) attempts failed and may present the combined diagnostic to the user or choose a safe fallback backend.

Error-handling guidance (pseudo-steps, not source code):
    - Call this function inside a try/except that catches ValueError and HypertoolsBackendError.
    - On ValueError: inform the user that the chosen backend is not valid in the IPython environment and display the available backends included in the exception message.
    - On HypertoolsBackendError: provide the full diagnostic message (it contains the IPython warning text and the fallback failure note) and offer to switch to a known-good backend (e.g., 'inline').

## `hypertools.plot.backend._reset_backend_notebook` · *function*

## Summary:
Registers a one-shot IPython notebook callback that will switch the plotting backend on the next cell run by invoking the notebook-level backend-switching logic; prevents duplicate registrations.

## Description:
- Known callers and context:
    - Typically invoked by higher-level backend-selection code or plotting initialization routines that need to apply a user-chosen backend in an interactive Jupyter/IPython notebook environment. Callers request notebook-specific behavior (deferring the actual switch until the next cell execution) and rely on this helper to perform the registration.
- Why this is a separate function:
    - Encapsulates the mechanics of creating a deferred callback, preventing duplicate callback registrations, and capturing the required IPython event manipulation in one place so callers do not need to handle event APIs or duplicate registration checks.

## Args:
    backend (object):
        - Required.
        - Must implement as_ipython() -> Any. The return value of as_ipython() is captured and later passed to _switch_backend_notebook by the deferred callback.
        - No default value.
        - Any exception raised by backend.as_ipython() (AttributeError, TypeError, or other) will propagate to the caller at call time.

## Returns:
    None
    - On successful return the function has either left the IPython events unchanged (if a matching callback was already registered) or has registered a new one-shot callback that will run before the next cell execution.
    - There are no alternate successful return values.

## Raises:
    - The function does not explicitly raise exceptions itself, but the following may propagate:
        - AttributeError/TypeError/Other from backend.as_ipython() if the backend object is missing as_ipython or it fails.
        - NameError if the module-level IPYTHON_INSTANCE name does not exist.
        - KeyError/AttributeError if IPYTHON_INSTANCE.events or its callbacks mapping does not conform to the expected structure (e.g., missing 'pre_run_cell' key).
        - Any exception raised by IPYTHON_INSTANCE.events.register/unregister will propagate.

## Constraints:
- Preconditions:
    - A module-level variable IPYTHON_INSTANCE must exist and expose:
        * events.register(event_name, callback) and events.unregister(event_name, callback) methods, and
        * an events.callbacks mapping where callbacks['pre_run_cell'] is iterable (the implementation inspects it).
    - The backend argument must provide as_ipython() and that call should succeed immediately.
- Postconditions:
    - If no matching '_deferred_reset_cb' callback was already present, IPYTHON_INSTANCE.events.register('pre_run_cell', _deferred_reset_cb) will have been called and the new callback is registered.
    - If a matching callback was already present, the event callbacks are left unchanged.
    - The function itself has no persistent return value; the deferred callback (when triggered) will call _switch_backend_notebook and then unregister itself.

## Side Effects:
- Registers a one-shot callback with IPYTHON_INSTANCE.events under the 'pre_run_cell' event (unless an existing callback with the same name is detected).
- Calls backend.as_ipython() synchronously at registration time; any side effect of that call will occur immediately.
- The deferred callback, when executed on the next cell run, will call _switch_backend_notebook(backend_value) (using the captured return value from as_ipython()) and then unregister itself from IPYTHON_INSTANCE.events.
- No filesystem, network, or stdout I/O is performed directly by this function; however, the deferred logic may trigger side effects of _switch_backend_notebook (which may interact with IPython, Matplotlib, and stdout).

## Control Flow:
flowchart TD
    Start --> ResolveBackend[call backend.as_ipython() -> backend_value]
    ResolveBackend --> CheckRegistered{is a callback named '_deferred_reset_cb' already in IPYTHON_INSTANCE.events.callbacks['pre_run_cell']?}
    CheckRegistered -- Yes --> End[do nothing; return None]
    CheckRegistered -- No --> Register[call IPYTHON_INSTANCE.events.register('pre_run_cell', _deferred_reset_cb)]
    Register --> End

    subgraph DeferredCallbackExecution
        DStart[on next pre_run_cell event] --> CallSwitch[call _switch_backend_notebook(backend_value)]
        CallSwitch --> Unregister[call IPYTHON_INSTANCE.events.unregister('pre_run_cell', _deferred_reset_cb)]
        Unregister --> DEnd[deferred callback removed]
    end

## Implementation notes and edge cases:
- Duplicate detection:
    - The function detects an existing registration by iterating IPYTHON_INSTANCE.events.callbacks['pre_run_cell'] and comparing each func.__name__ to the literal '_deferred_reset_cb'. This:
        * Means duplicate detection depends entirely on function __name__; if a previously registered callable has the same __name__ but different identity, this function will treat it as already registered (avoiding registration even though the exact callable may be different).
        * If callbacks['pre_run_cell'] is missing, not iterable, or contains objects lacking __name__, an exception may be raised.
- Captured argument:
    - The function overwrites the local name backend with backend.as_ipython() and the deferred callback captures that value. Therefore the return value of as_ipython() must be compatible with whatever _switch_backend_notebook expects when the deferred callback runs.
- Exceptions:
    - Any exceptions during backend.as_ipython() will be raised immediately; exceptions during the deferred callback (when the event fires) will propagate through IPython's event handling and are not caught by this function; callers should consider that the actual backend switch occurs later and its errors appear at event execution time.

## Examples:
Typical usage in a notebook-initialization routine (described in prose):
    - A configuration routine receives a backend wrapper object from user settings and calls _reset_backend_notebook(backend_wrapper). If a registration does not already exist, this schedules the actual notebook backend switch to occur just before the next cell executes. The caller may then let normal cell execution trigger the change, or explicitly run a no-op cell to force immediate execution of pre_run_cell handlers.

Error-handling guidance:
    - Because backend.as_ipython() is invoked synchronously, wrap the call site if backend identity errors must be handled immediately.
    - Errors raised during the deferred callback will occur at the time the next cell executes; to observe or handle them you may need to monitor IPython's event system or wrap _switch_backend_notebook directly where appropriate.

## `hypertools.plot.backend._get_runtime_args` · *function*

## Summary:
Resolves a callable's signature against runtime arguments and returns an ordered mapping of parameter names to their bound values, with any missing optional parameters filled from their defaults.

## Description:
This helper extracts the concrete argument values that a callable will receive at runtime by:
1. Obtaining the callable's signature.
2. Binding the provided positional and keyword arguments to that signature.
3. Applying default values for any parameters not explicitly provided.

Known callers within the provided context:
- No explicit callers were provided in the supplied source/context for this repository. Typical callers are internal wrapper or dispatch utilities that need a stable mapping of parameter names to values (for logging, validation, transformation, or re-dispatching) before invoking or inspecting the callable.

Why this logic is extracted:
- Centralizes the signature-binding logic in one place so other code can uniformly obtain a canonical mapping of parameter names to runtime values (including defaults) without duplicating inspect.signature / bind / apply_defaults calls.
- Encapsulates error surface from signature resolution so callers can handle binding/inspection errors in a consistent manner.

## Args:
    func (callable): The target callable whose signature will be inspected. Must be a Python-callable object (function, bound method, functools.partial, callable class instance, etc.)
    *func_args (tuple): Positional arguments that will be bound to the callable's positional parameters.
    **func_kwargs (dict): Keyword arguments that will be bound to the callable's keyword parameters.

Notes on interdependencies:
- The positional and keyword arguments are interpreted together against the callable's signature; supplying both values for the same parameter (e.g., positional and keyword for the same name) will trigger a binding error.
- If the callable defines *args/**kwargs parameters, they will receive any unmatched positional/keyword values per standard Python binding rules and will appear in the returned mapping under the parameter names used in the callable's signature.

## Returns:
collections.OrderedDict (or insertion-ordered mapping): A mapping from parameter name (str) to the bound value for that parameter as it will be seen by the callable at invocation time.
- The mapping includes:
    - All parameters that were provided by func_args and func_kwargs.
    - All parameters that have default values but were not provided — these will be present with their default values (due to apply_defaults()).
    - If the callable includes a var-positional parameter (e.g., *args), the mapping will include that parameter name mapped to a tuple of the bound extra positional values.
    - If the callable includes a var-keyword parameter (e.g., **kwargs), the mapping will include that parameter name mapped to a dict of the extra bound keyword values.

Edge-case returns:
- This function never returns None; on success it always returns a mapping object. It will not partially bind — either binding succeeds and returns the full mapping, or an exception is raised.

## Raises:
- TypeError: If binding fails because the provided func_args/func_kwargs do not satisfy the callable's signature (for example, missing a required positional argument, or multiple values for the same parameter), or if inspect.signature rejects the provided func as not a valid callable in the current runtime.
- ValueError: If the inspection mechanism cannot obtain a signature for the provided callable (for example, certain built-in or C-implemented callables that do not expose a Python-level signature).
- Any exceptions raised are the original exceptions from the inspect module (inspect.signature, BoundArguments.bind, or BoundArguments.apply_defaults) — this function does not wrap them.

## Constraints:
Preconditions:
- func must be a callable that Python's inspect module can analyze.
- func_args and func_kwargs should be the runtime arguments you plan to pass to func; they must be consistent with func's signature or a binding error will be raised.

Postconditions:
- On successful return, the returned mapping contains entries for every parameter name in the signature that is relevant to the provided arguments (including defaults), and values are the concrete objects that would be passed to func if it were invoked with the provided func_args and func_kwargs.

## Side Effects:
- None. The function performs no I/O, does not mutate global state, and does not call the target callable. It only inspects and binds arguments using the inspect module.

## Control Flow:
flowchart TD
    Start([start])
    A[inspect.signature(func)]
    B[BoundArguments.bind(*func_args, **func_kwargs)]
    C[BoundArguments.apply_defaults()]
    D[return BoundArguments.arguments]
    E1[ValueError from inspect.signature]
    E2[TypeError from bind or if func not bindable]
    Start --> A
    A -->|success| B
    A -->|ValueError| E1
    B -->|success| C
    B -->|TypeError| E2
    C --> D

## Examples (descriptive, no code):
1) Successful binding with defaults:
- Given a callable that accepts (a, b=2, c=3) and a runtime call that provides a=1 and c=5, calling this utility with those runtime args will return a mapping: a -> 1, b -> 2 (default filled), c -> 5.

2) Var-positional and var-keyword handling:
- For a callable with signature (x, *args, **kwargs), if runtime positional extras are provided they will be grouped into the mapping under the *args parameter name as a tuple; any extra keywords will be grouped under the **kwargs parameter name as a dict.

3) Error handling:
- If a required positional argument is omitted (e.g., callable requires 'a' but the provided arguments do not set 'a'), the function will raise TypeError originating from BoundArguments.bind; callers should catch TypeError and surface an appropriate error message or re-raise a wrapped exception if desired.

4) Typical integration pattern:
- Use this helper from wrapper code that wants to log or validate the concrete parameter values before calling the underlying function. The wrapper calls this helper with the intended invocation arguments; if binding succeeds it can inspect or mutate the returned mapping, then optionally invoke the callable with those values.

## `hypertools.plot.backend.set_interactive_backend` · *class*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
A context-manager class that temporarily sets the module-level "interactive" plotting backend (HYPERTOOLS_BACKEND) to a requested backend for the duration of a with-block, switching the live matplotlib backend if necessary, and restoring prior state on exit.

## Description:
set_interactive_backend is intended to be used with the with-statement to scope a temporary change to the interactive plotting backend used by the hypertools plotting subsystem.

- When to instantiate:
  - Wrap code that must run using a particular interactive backend (for example, enabling an inline backend when running in a notebook, or switching to a GUI backend for a blocking interactive session).
  - Typical usage: a caller constructs set_interactive_backend(backend) where backend is a string (e.g., "TkAgg" or "module://ipykernel.pylab.backend_inline") or a HypertoolsBackend instance and uses it in a with-block so the backend change is confined to the block.

- Motivation and responsibility boundary:
  - This class encapsulates the two related concerns required for temporarily changing interactive plotting:
    1) update module-level configuration used by hypertools (HYPERTOOLS_BACKEND and BACKEND_WARNING) so other hypertools code sees the requested backend, and
    2) if the actual runtime matplotlib backend differs, call module-level helpers to switch the live backend for the duration of the context and then restore the original live backend on exit.
  - It does not itself implement the low-level backend switching logic; it delegates to switch_backend(...) and reset_backend(...). It also relies on HypertoolsBackend.normalize() semantics to map/normalize backend identifiers.

## State:
Instance attributes (public):
- old_interactive_backend (HypertoolsBackend)
    - The normalized HypertoolsBackend value that was stored in the module-level HYPERTOOLS_BACKEND at construction time.
    - Invariant: set during __init__; used for restoration if the requested new backend differs.
- old_backend_warning (any / optional)
    - Copy of the module-level BACKEND_WARNING value at construction time. Restored on __exit__ if changed.
    - May be None or any other object the module uses to represent a prior warning state.
- new_interactive_backend (HypertoolsBackend)
    - The normalized HypertoolsBackend derived from the `backend` argument passed to __init__.
    - Valid values: any value for which HypertoolsBackend(backend).normalize() returns a HypertoolsBackend; callers should ensure the backend argument is a recognizable backend string or HypertoolsBackend.
- new_is_different (bool)
    - True if new_interactive_backend != old_interactive_backend (case-insensitive comparison via HypertoolsBackend semantics). Indicates whether module-level HYPERTOOLS_BACKEND was updated at construction time.
- backend_switched (bool)
    - Initially False. Set to True inside __enter__ if the live matplotlib backend differs from the requested backend and a live-switch was performed.
- curr_backend (HypertoolsBackend) — set in __enter__
    - The normalized HypertoolsBackend representing the matplotlib runtime backend that was active at context entry (used to restore the live backend on exit).
    - Only present after __enter__ has executed.

Module-level globals that this class reads or modifies (not owned by the class but essential to understand):
- HYPERTOOLS_BACKEND (HypertoolsBackend-like)
    - The module-level configured interactive backend. The class reads and may temporarily overwrite this during __init__ and restore on __exit__.
- BACKEND_WARNING (any)
    - Module-level value used by hypertools to track whether a backend warning has been emitted. set_interactive_backend may set it to None while active and restore the previous value later.
- IN_SET_CONTEXT (bool)
    - Flag toggled True in __enter__ and False in __exit__ to indicate code is currently running inside a set_interactive_backend context. Other code in the module may read this flag to change behavior while inside the context.
- mpl (module-like)
    - The code calls mpl.get_backend() during __enter__ to determine the currently active matplotlib backend. In the surrounding module this is typically an alias for the matplotlib module.

Class invariants:
- After __init__, new_interactive_backend and old_interactive_backend are valid HypertoolsBackend instances.
- If new_is_different is True, HYPERTOOLS_BACKEND has been updated to new_interactive_backend and BACKEND_WARNING set to None until __exit__ restores them.
- If backend_switched is True by __enter__, __exit__ will call reset_backend(curr_backend) to restore the live backend.

## Lifecycle:
Creation (constructor):
- Signature: set_interactive_backend(backend)
  - backend: str or HypertoolsBackend-like object. It will be wrapped by HypertoolsBackend(backend) internally.
  - On construction:
    1) reads and normalizes the current module-level HYPERTOOLS_BACKEND (via HYPERTOOLS_BACKEND.normalize()) and stores that in old_interactive_backend.
    2) saves BACKEND_WARNING into old_backend_warning.
    3) constructs HypertoolsBackend(backend).normalize() and stores it as new_interactive_backend.
    4) compares new_interactive_backend to old_interactive_backend and sets new_is_different accordingly.
    5) if new_is_different is True, assigns HYPERTOOLS_BACKEND = new_interactive_backend and sets BACKEND_WARNING = None so the module's configured backend reflects the requested backend for code that runs before __enter__.
  - Client constraints:
    - backend should be acceptable to HypertoolsBackend(...) and its normalize() method (i.e., BACKEND_MAPPING and IS_NOTEBOOK must be set up so normalize() succeeds). If normalize() fails (KeyError or similar), the exception propagates from the constructor.
    - HYPERTOOLS_BACKEND must be defined in the module when the constructor is called; otherwise NameError will occur.

Usage (context manager protocol):
- __enter__:
  - Sets the module-level IN_SET_CONTEXT = True to signal entry.
  - Queries the currently active matplotlib backend via mpl.get_backend(), wraps it with HypertoolsBackend(...).normalize(), and stores it in curr_backend.
  - If curr_backend != new_interactive_backend (HypertoolsBackend comparison), sets backend_switched = True and calls the module helper switch_backend(new_interactive_backend) to change the live matplotlib backend to the requested backend.
  - After __enter__, code executing inside the with-block will see HYPERTOOLS_BACKEND set (if new_is_different) and the live backend possibly switched.

- __exit__(exc_type, exc_value, traceback):
  - Always sets IN_SET_CONTEXT = False.
  - If new_is_different was True (i.e., constructor changed the module-level configured backend), restores HYPERTOOLS_BACKEND to old_interactive_backend and BACKEND_WARNING to old_backend_warning.
  - If backend_switched is True (i.e., __enter__ performed a live switch), calls reset_backend(curr_backend) to restore the live matplotlib backend to the pre-context value.
  - The method does not suppress exceptions (it returns None implicitly); exceptions raised inside the with-block are propagated after __exit__ runs its restoration logic.

Destruction / cleanup:
- No explicit destructor or context-manager close required beyond relying on __exit__ for restoration. If a context is abandoned without calling __exit__ (e.g., due to process termination), manual restoration will not occur.

## Method Map:
graph LR
    Init[__init__(backend)] -->|reads| OldConfig[HYPERTOOLS_BACKEND.normalize()]
    Init -->|sets| NewConfig[HYPERTOOLS_BACKEND = new_interactive_backend (if different)]
    Enter[__enter__()] -->|set| IN_SET_CONTEXT(True)
    Enter -->|reads| MPLGet[mpl.get_backend() -> curr_backend]
    Enter -->|if different| Switch[switch_backend(new_interactive_backend)]
    Exit[__exit__()] -->|set| IN_SET_CONTEXT(False)
    Exit -->|if new_is_different| RestoreConfig[HYPERTOOLS_BACKEND = old_interactive_backend; BACKEND_WARNING = old_backend_warning]
    Exit -->|if backend_switched| Reset[reset_backend(curr_backend)]

Typical invocation order:
- __init__ (on construction) -> __enter__ (on entering with-block) -> user code -> __exit__ (on leaving with-block)

## Raises:
Exceptions that may propagate from set_interactive_backend methods:

- __init__:
  - KeyError (or HypertoolsBackend-related lookup errors): if HypertoolsBackend(backend).normalize() fails because BACKEND_MAPPING does not recognize `backend` or the mapping is misconfigured. These originate from HypertoolsBackend.normalize() and its internal mapping lookups.
  - NameError/AttributeError: if the module-level HYPERTOOLS_BACKEND or BACKEND_WARNING is not defined or lacks normalize(); these will propagate.
  - Any exception raised during str() conversion of backend when creating HypertoolsBackend(backend) (rare).

- __enter__:
  - NameError: if the alias `mpl` or function mpl.get_backend() is not available in the module.
  - KeyError/lookup errors from HypertoolsBackend(...).normalize() when normalizing the result of mpl.get_backend().
  - Any exception raised by switch_backend(new_interactive_backend) (these depend on the implementation of switch_backend).

- __exit__:
  - Any exception raised by reset_backend(curr_backend) when restoring the live backend.
  - Note: __exit__ performs restoration even if an exception occurred inside the with-block; it does not itself suppress that exception (it does not return True).

## Example:
- Typical usage pattern:
  - Create a context requesting an inline backend while running a block that should render inline (assuming the backend string is recognized by HypertoolsBackend):
    with set_interactive_backend("module://ipykernel.pylab.backend_inline"):
        <run plotting code that expects inline display>

  - If the current runtime used a different live backend, the context will have switched the live matplotlib backend on entering the with-block and will restore the previous live backend upon exit. Module-level HYPERTOOLS_BACKEND and BACKEND_WARNING are also restored to their prior values after the block.

Notes for reimplementation:
- Ensure the constructor uses HYPERTOOLS_BACKEND.normalize() (module-global) and HypertoolsBackend(backend).normalize() for consistent normalization behavior.
- The class deliberately updates HYPERTOOLS_BACKEND at construction time when the requested backend differs — this allows other code that runs before __enter__ (but after construction) to see the requested backend. If this behavior is undesirable, construct the context manager immediately before entering the with-block.
- The class relies on external helper functions switch_backend(target_backend) to perform the live backend switch and reset_backend(original_backend) to restore the live backend. Those helpers should accept HypertoolsBackend (or str) and implement the platform-specific backend switching and restoration logic.

### `hypertools.plot.backend.set_interactive_backend.__init__` · *method*

## Summary:
Initializes the object by recording the current global Hypertools backend and backend-warning state, normalizing the requested backend, computing whether the backend differs, initializing a switch flag, and—if different—updating the module-level backend and clearing any backend warning.

## Description:
This is the __init__ method for the enclosing set_interactive_backend class and is executed when an instance of that class is created. It performs only initialization and global bookkeeping related to a requested interactive backend change:

- Reads the current module-level HYPERTOOLS_BACKEND and BACKEND_WARNING values.
- Constructs and normalizes a HypertoolsBackend from the provided backend argument.
- Compares the normalized new backend to the normalized current backend and records whether they differ.
- Initializes an instance flag backend_switched to False.
- If the normalized backends differ, updates the module-level HYPERTOOLS_BACKEND to the new normalized backend and sets BACKEND_WARNING to None.

No other behavior beyond what is described above occurs in this method. The method does not itself perform any I/O, nor does it explicitly mark the instance as having completed a switch beyond setting backend_switched to False.

## Known callers / Invocation context:
    - The method is called implicitly whenever the enclosing class is instantiated. No additional callers are discoverable from this method alone.

## Why this is an initializer:
    - The logic is grouped in __init__ because it establishes the object's invariant state (old/new backends, whether a change is needed, and an initialized switch flag) immediately at object creation. This centralizes bookkeeping required prior to any further backend-switching actions.

## Args:
    backend (any):
        - Forwarded to HypertoolsBackend(backend) for construction and normalization.
        - Acceptable values: any value supported by HypertoolsBackend's constructor. This method does not validate types beyond delegating to HypertoolsBackend.

## Returns:
    None
    - As a constructor, it does not return a runtime value. On normal completion the instance attributes described below are populated and module-level globals may have been updated.

## Raises:
    - Any exception raised by HypertoolsBackend(backend) or by calling normalize() on HYPERTOOLS_BACKEND or on the HypertoolsBackend instance will propagate unchanged (e.g., validation or implementation-specific errors from HypertoolsBackend).
    - AttributeError (or similar) may propagate if the module-level HYPERTOOLS_BACKEND or BACKEND_WARNING variables are not defined or do not implement the expected interface (for example, if HYPERTOOLS_BACKEND lacks a normalize() method).

## State Changes:
    Attributes READ:
        - Module-level: HYPERTOOLS_BACKEND (via HYPERTOOLS_BACKEND.normalize())
        - Module-level: BACKEND_WARNING (read to save current value)
        - No pre-existing instance attributes are read before being assigned.

    Attributes WRITTEN (instance):
        - self.old_interactive_backend: set to HYPERTOOLS_BACKEND.normalize()
        - self.old_backend_warning: set to the current BACKEND_WARNING
        - self.new_interactive_backend: set to HypertoolsBackend(backend).normalize()
        - self.new_is_different: bool, result of (self.new_interactive_backend != self.old_interactive_backend)
        - self.backend_switched: initialized to False

    Module-level globals modified:
        - HYPERTOOLS_BACKEND: assigned self.new_interactive_backend when self.new_is_different is True
        - BACKEND_WARNING: set to None when HYPERTOOLS_BACKEND is updated

## Constraints:
    Preconditions:
        - The module-level variables HYPERTOOLS_BACKEND and BACKEND_WARNING must exist in the module namespace.
        - HYPERTOOLS_BACKEND must implement a normalize() method that returns a value comparable via !=.
        - The HypertoolsBackend constructor and its normalize() method must be available and behave deterministically for the provided backend argument.

    Postconditions:
        - The instance attributes listed above are initialized.
        - self.new_is_different accurately reflects whether the normalized new backend differs from the normalized current global backend.
        - If self.new_is_different is True, the module-level HYPERTOOLS_BACKEND has been set to the new normalized backend and BACKEND_WARNING has been cleared (set to None).
        - self.backend_switched remains False on exit from this method.

## Side Effects:
    - Mutates module-level state (HYPERTOOLS_BACKEND and BACKEND_WARNING) when the requested backend differs from the current one.
    - No file/network I/O is performed here. However, constructing/normalizing the backend delegates to HypertoolsBackend, which may itself perform arbitrary work (and thus could have side effects) depending on its implementation.

### `hypertools.plot.backend.set_interactive_backend.__enter__` · *method*

## Summary:
On entering the context, mark that a backend-set operation is in-progress, record the current matplotlib backend (normalized through HypertoolsBackend), and if it differs from the requested interactive backend, mark that a backend switch occurred and invoke the switch to the requested interactive backend.

## Description:
This method is the context-manager entry logic for temporarily setting the process's interactive plotting backend. It is invoked automatically when code uses the set_interactive_backend instance with a with statement (for example: with set_interactive_backend('TkAgg'):`...`). Typical callers are user code or library code that must ensure a specific interactive backend is active for the duration of a block that creates interactive plots.

The method exists as __enter__ to:
- Encapsulate and localize the side-effectful operations (setting a global "in-set-context" flag, reading the current backend, and possibly switching backends) that should happen at the precise moment the context is entered.
- Keep enter/exit responsibilities symmetric: __enter__ records and applies the temporary state, while __exit__ restores it. This separation ensures correct restoration on normal exit and on exceptions.

Known call-site lifecycle:
- set_interactive_backend.__init__ prepares the target backend and stores prior values.
- set_interactive_backend.__enter__ (this method) is called at the start of the with-block; it sets the runtime state and may switch the plotting backend.
- set_interactive_backend.__exit__ will be called at the end of the with-block to restore prior backend state and unset the in-context flag.

## Args:
    None (method signature: def __enter__(self))

## Returns:
    None
    - The method has no explicit return statement, so it returns None implicitly.
    - The value returned is what a "with ... as X:" would bind to X (i.e., None here).

## Raises:
    - Any exception raised by HypertoolsBackend(...) or its normalize() call:
        * For example, if HypertoolsBackend.normalize triggers a KeyError because BACKEND_MAPPING is missing or incomplete, that KeyError will propagate.
    - Any exception raised by the mpl.get_backend() call (NameError if the identifier mpl is not defined, or other exceptions coming from matplotlib internals).
    - Any exception raised by switch_backend(self.new_interactive_backend) when called (NameError if switch_backend is not defined in the module scope, or any runtime exception thrown by the backend-switching logic).
    - In short: the method does not catch/translate exceptions; exceptions from called functions propagate to the caller.

## State Changes:
Attributes READ:
    - self.new_interactive_backend : used for comparison to the current backend
    - (implicitly) module globals referenced via calls (the global IN_SET_CONTEXT name is read/written; see WRITTEN)

Attributes WRITTEN:
    - self.curr_backend : set to the normalized current backend obtained from matplotlib (HypertoolsBackend(mpl.get_backend()).normalize())
    - self.backend_switched : may be set to True if the current backend differs from the requested new_interactive_backend
    - global IN_SET_CONTEXT : set to True

## Constraints:
Preconditions:
    - The set_interactive_backend instance must have been initialized so that self.new_interactive_backend exists (this is performed in the class __init__).
    - The module must define or import the names used by the method:
        * mpl (expected to expose get_backend())
        * HypertoolsBackend (class available in the module)
        * switch_backend (callable visible in the module global scope)
      If any of these are missing, NameError will be raised.
    - BACKEND_MAPPING and IS_NOTEBOOK (used by HypertoolsBackend.normalize) should be available and correctly configured if normalization is to succeed without KeyError.

Postconditions:
    - After successful completion:
        * global IN_SET_CONTEXT is True.
        * self.curr_backend holds the normalized representation of the backend that was active at the time __enter__ ran.
        * If the current backend did not equal self.new_interactive_backend, then:
            - self.backend_switched is True
            - switch_backend(self.new_interactive_backend) has been called (and, unless that call raised, the process interactive backend should now be the requested new_interactive_backend).
        * If the current backend already equaled self.new_interactive_backend, self.backend_switched remains False and no backend switch is attempted.

## Side Effects:
    - Calls HypertoolsBackend(mpl.get_backend()).normalize() which:
        * Allocates a HypertoolsBackend wrapper and performs normalization that depends on module-level BACKEND_MAPPING and IS_NOTEBOOK — that normalization may perform lookups that can raise (KeyError, TypeError) if mappings are misconfigured.
    - May call switch_backend(self.new_interactive_backend) which performs global changes to the plotting backend state (matplotlib internals). That call has external side effects beyond the object (it changes the process-wide interactive backend).
    - Mutates module-global IN_SET_CONTEXT (set to True).
    - Mutates attributes on self (curr_backend, backend_switched), which are later used by __exit__ to restore prior state.
    - Does not perform I/O (file, network) directly, but switching backends can trigger platform-specific initialization steps inside matplotlib.

## Edge cases and notes:
    - If mpl.get_backend() returns a backend name that HypertoolsBackend.normalize cannot map (e.g., BACKEND_MAPPING lacks the key), normalize will raise (propagated).
    - If the module-level switch_backend function is not present (NameError) or raises during execution, the context entry will fail and the with-block will not be entered; caller code must handle such exceptions.
    - If self.new_interactive_backend equals the current backend (after normalization), no switch is attempted and backend_switched remains False — __exit__ will therefore avoid resetting the backend unnecessarily.
    - The method intentionally leaves exception handling to the caller so that failures in backend detection or switching are visible to the code that attempted to enter the context.

### `hypertools.plot.backend.set_interactive_backend.__exit__` · *method*

## Summary:
Restores the module-level interactive-backend state and clears the context flag when exiting the set_interactive_backend context; if the backend was switched on enter, attempts to reset it to the previous backend.

## Description:
This method is invoked automatically by Python when a with set_interactive_backend(...) context exits (i.e., it is the context-manager exit handler). Typical callers are any call-sites that use the class in a with-statement, for example:
    with set_interactive_backend('module.backend'):
        ...plotting code...

It is called at the lifecycle stage when temporary backend changes made in __enter__ must be undone — whether the block completed normally or via an exception. The logic is separated into __exit__ (rather than being inlined) to centralize cleanup and symmetry with __enter__, ensuring the global state (HYPERTOOLS_BACKEND, BACKEND_WARNING, IN_SET_CONTEXT) and any actual matplotlib backend are reliably restored after the context.

## Args:
    exc_type (Optional[type[BaseException]]): Exception class raised in the with-block, or None if no exception occurred.
    exc_value (Optional[BaseException]): Exception instance raised in the with-block, or None if no exception occurred.
    traceback (Optional[types.TracebackType]): Traceback object for the exception, or None.

## Returns:
    None
    - The method does not return a truthy value; therefore it does not suppress exceptions from the with-block. If an exception occurred inside the with-block, it will continue propagating after this method returns (unless reset_backend or other called code raises or suppresses it).

## Raises:
    - This method contains no explicit raise statements. However, any exception raised by reset_backend(self.curr_backend) (called when self.backend_switched is True) or by other invoked code will propagate out of __exit__ because exceptions are not caught here.

## State Changes:
Attributes READ:
    - self.new_is_different
    - self.old_interactive_backend
    - self.old_backend_warning
    - self.backend_switched
    - self.curr_backend

Attributes WRITTEN:
    - global IN_SET_CONTEXT is set to False
    - global HYPERTOOLS_BACKEND may be set to self.old_interactive_backend (when self.new_is_different is True)
    - global BACKEND_WARNING may be set to self.old_backend_warning (when self.new_is_different is True)
    - No self.<attr> fields are modified by this method.

## Constraints:
Preconditions:
    - The instance is expected to have been used as a context manager (i.e., __enter__ has been called). In particular:
        * self.curr_backend is expected to exist if self.backend_switched is True (it is set in __enter__).
        * self.old_interactive_backend and self.old_backend_warning were captured in __init__.
    - The module globals IN_SET_CONTEXT, HYPERTOOLS_BACKEND, and BACKEND_WARNING exist in the module scope.

Postconditions:
    - IN_SET_CONTEXT is False after the call.
    - If self.new_is_different was True at exit: HYPERTOOLS_BACKEND is reset to the value saved in self.old_interactive_backend and BACKEND_WARNING is restored to self.old_backend_warning.
    - If self.backend_switched was True at exit: reset_backend(self.curr_backend) is invoked; if it completes successfully, the active matplotlib backend will have been returned to the backend recorded in self.curr_backend.
    - The method itself returns None (does not suppress exceptions).

## Side Effects:
    - Mutates module-level globals: IN_SET_CONTEXT, HYPERTOOLS_BACKEND, and BACKEND_WARNING (conditionally).
    - Calls reset_backend(self.curr_backend) when self.backend_switched is True; any side effects (including I/O or further global mutation) performed by reset_backend occur here and may raise exceptions.
    - No direct I/O (printing, file access) occurs in this method itself.

## `hypertools.plot.backend._null_backend_context` · *function*

## Summary:
Provides a minimal no-op generator that yields once and performs no actions; intended to be wrapped into a context manager when a backend switch/context is not required.

## Description:
This component is a tiny generator-based helper that accepts a single argument (commonly a backend identifier) and immediately yields control, producing no value and causing no side effects. It exists to provide a stable "do nothing" context when higher-level code expects a context manager for backend switching but no switching action is necessary.

Known callers within the codebase:
    - None explicitly identified in the local file-level view. Typical usage pattern in this project is for higher-level backend-selection logic to wrap this generator with contextlib.contextmanager or to substitute it wherever a context manager is required but no work should occur.

Why this logic is extracted into its own function:
    - Encapsulates the no-op semantics in a single place so callers can uniformly obtain a context manager (by wrapping this generator) without branching their usage sites.
    - Keeps backend-selection code simple: callers can always call/enter "a context" even when that context does nothing.
    - Avoids duplicating the "yield-and-do-nothing" behavior where a no-op context is needed.

## Args:
    dummy_backend (Any): A placeholder parameter that accepts any value (usually a backend identifier or object). The parameter is intentionally unused; it exists to provide a compatible signature with other backend context factories.

## Returns:
    generator: A generator object that, when iterated (or used by contextlib.contextmanager to create a context manager), yields exactly once and returns None. If wrapped with contextmanager, entering the context transfers control at the yield point; exiting the context resumes the generator to completion.

    Possible values/edge cases:
    - When called, the function returns a generator object immediately (no side effects).
    - If the generator is iterated, the first next() yields None and subsequent next() will raise StopIteration.
    - If the generator is wrapped by contextlib.contextmanager, it behaves like a context manager that does nothing on enter and does nothing on exit (no exceptions raised or suppressed by default).

## Raises:
    - This function does not raise any exceptions on its own.
    - If used incorrectly (for example, attempting to use the raw generator as a context manager without wrapping), the calling code may encounter type-related errors elsewhere; such errors are not produced by this function.

## Constraints:
    Preconditions:
        - None specific. The argument may be any value; calling the function is always valid.
    Postconditions:
        - No global state is modified.
        - The returned generator object has yielded once (if iterated) or will yield once when driven; wrapping with contextmanager yields a context manager that guarantees no side effects on enter or exit.

## Side Effects:
    - None. The function performs no I/O, does not mutate globals, and does not call external services.

## Control Flow:
flowchart TD
    Start[Start] --> Receive[Receive dummy_backend argument]
    Receive --> CreateGen[Create generator object]
    CreateGen --> YieldPoint[Yield control exactly once]
    YieldPoint --> End[Complete / StopIteration]
    End --> Exit[Return / Context exit]

## Examples:
    Typical pattern to use this helper as a context manager:
    1. Convert the generator into a context manager using a contextmanager factory.
       - The generator itself is not a context manager until wrapped.
    2. Enter the resulting context where caller code expects a backend context.

    Example usage (described without import lines):
        - Wrap the generator with a contextmanager factory to obtain a context manager.
        - Use a with-block to enter the no-op backend context.
        - The body of the with-block executes normally; no backend switching occurs.

    Error handling:
        - There is nothing to catch inside this generator. If the surrounding code needs to manage exceptions that occur inside the with-block, it should do so in the usual way (try/except around the with-block). This helper does not intercept or handle exceptions.

## `hypertools.plot.backend.manage_backend` · *function*

## Summary:
Decorator that wraps a plotting function to (1) snapshot and later restore matplotlib rcParams and (2) conditionally enter a temporary interactive-backend context when the call requests animation or interactive behavior, returning the wrapped function's result unchanged.

## Description:
manage_backend returns a wrapper (plot_wrapper) which, on each call:
1. Copies mpl.rcParams to preserve current rc state.
2. Determines whether to use a no-op backend context or to enter set_interactive_backend based on runtime-bound arguments (animate or interactive) and the resolved mpl_backend.
3. Enters the chosen backend context for the duration of the plotting call (the no-op context is used when no change is required).
4. Emits a warnings.warn(BACKEND_WARNING) if BACKEND_WARNING is non-None.
5. Calls the original plotting function and returns its result.
6. In a finally block, suppresses mpl.MatplotlibDeprecationWarning and updates mpl.rcParams with the saved snapshot.

Known callers / typical triggers:
- Plot functions decorated with @manage_backend. These functions typically accept animate, interactive, and mpl_backend parameters. The wrapper runs on every call and only attempts to set an interactive backend when animate or interactive are truthy in the bound runtime args.

Why this logic is extracted:
- Centralizes rcParams preservation and backend-selection policy so plotting functions remain focused on drawing logic.
- Ensures consistent environment handling for interactive/animated plotting across different runtime environments (e.g., notebooks vs. GUI).

## Args:
- plot_func (callable): The plotting function to wrap. The wrapper binds runtime args using the helper _get_runtime_args to inspect named parameters like animate, interactive, and mpl_backend.

The returned wrapper accepts the same *args and **kwargs as plot_func.

## Returns:
- callable: A wrapper which:
  - Returns whatever plot_func returns when the call succeeds.
  - Propagates exceptions from argument binding, backend normalization, the backend context, or plot_func itself.

## Raises:
The wrapper allows exceptions from its operations to propagate; it does not raise new exception types itself:

- TypeError / ValueError:
  - From _get_runtime_args if provided args/kwargs cannot be bound to plot_func's signature.

- NameError / AttributeError:
  - If required module-level names are missing/misbound: IN_SET_CONTEXT, HYPERTOOLS_BACKEND, BACKEND_WARNING, mpl, set_interactive_backend, _null_backend_context, _get_runtime_args, HypertoolsBackend.

- KeyError or mapping errors:
  - From HypertoolsBackend.normalize() when normalizing mpl.get_backend() or HYPERTOOLS_BACKEND (used when mpl_backend == 'auto') if BACKEND_MAPPING is misconfigured.

- Any exception raised by set_interactive_backend:
  - Construction or __enter__ of the context manager may raise (e.g., errors during live backend switching).

- Any exception raised by plot_func:
  - Propagated unchanged after rcParams restoration.

Notes:
- Emitted warnings via warnings.warn(BACKEND_WARNING) do not raise exceptions by themselves.

## Constraints:
Preconditions:
- The module must provide these names with expected behaviors:
  - _get_runtime_args(callable, *args, **kwargs): binds runtime args to parameter names (including defaults).
  - HypertoolsBackend with normalize() to canonicalize backend identifiers.
  - _null_backend_context: a context-factory usable as with _null_backend_context(tmp_backend).
  - set_interactive_backend: a context-factory accepting a backend id and returning a context manager that may change HYPERTOOLS_BACKEND and the live mpl backend for the with-block.
  - IN_SET_CONTEXT (bool): read to avoid performing backend selection when True.
  - HYPERTOOLS_BACKEND: module-level default backend used when mpl_backend == 'auto'.
  - BACKEND_WARNING: optional message to warn about backend issues.
  - mpl providing:
    - rcParams with .copy() and .update(**dict),
    - get_backend() function,
    - MatplotlibDeprecationWarning class.

Postconditions (what is guaranteed after wrapper returns or raises):
- mpl.rcParams.update(**old_rcParams) is called in the finally block while suppressing mpl.MatplotlibDeprecationWarning. This ensures that keys present in the saved snapshot are set back to their saved values.
- Important: keys that were added to mpl.rcParams during the call but were not present in the saved snapshot will remain present after update; manage_backend does not remove keys that were added while the call ran. In other words, update restores old values but does not revert additions/deletions of keys not present in old_rcParams.
- Any temporary backend changes made inside set_interactive_backend are expected to be undone by that context manager; manage_backend relies on that behavior.

## Side Effects:
- May emit a warning via warnings.warn(BACKEND_WARNING) if BACKEND_WARNING is not None.
- May temporarily mutate module-level backend state and/or switch the live matplotlib backend when entering set_interactive_backend(tmp_backend). These mutations should be reversed by that context manager.
- Restores rcParams by calling mpl.rcParams.update(**old_rcParams). While this resets values for keys in the snapshot, it does not remove keys added during the call.
- Suppresses mpl.MatplotlibDeprecationWarning only during rcParams restoration using warnings.catch_warnings() and warnings.simplefilter('ignore', mpl.MatplotlibDeprecationWarning).

## Control Flow:
flowchart TD
    Start([plot_wrapper called])
    Save[old_rcParams = mpl.rcParams.copy()]
    Defaults[backend_context = _null_backend_context; tmp_backend = None]
    CheckIN{IN_SET_CONTEXT is True?}
    BindArgs[plot_kwargs = _get_runtime_args(plot_func, *args, **kwargs)]
    CheckAnim{plot_kwargs.get('animate') or plot_kwargs.get('interactive')?}
    GetCurr[curr_backend = HypertoolsBackend(mpl.get_backend()).normalize()]
    ReadTmp[tmp_backend = plot_kwargs.get('mpl_backend')]
    Auto{tmp_backend == 'auto' ?}
    UseHYP[tmp_backend = HYPERTOOLS_BACKEND.normalize()]
    NeedSwitch{tmp_backend not in ('disable', curr_backend) ?}
    SetCtx[backend_context = set_interactive_backend]
    Try[try:]
    WithCtx[with backend_context(tmp_backend):]
    WarnCheck{BACKEND_WARNING is not None?}
    Warn[warnings.warn(BACKEND_WARNING)]
    Call[return plot_func(*args, **kwargs)]
    Finally[finally: with warnings.catch_warnings():\n  warnings.simplefilter('ignore', mpl.MatplotlibDeprecationWarning)\n  mpl.rcParams.update(**old_rcParams)]
    End([done])
    Start --> Save --> Defaults --> CheckIN
    CheckIN -- False --> BindArgs --> CheckAnim
    CheckAnim -- True --> GetCurr --> ReadTmp --> Auto
    Auto -- True --> UseHYP --> NeedSwitch
    Auto -- False --> NeedSwitch
    NeedSwitch -- True --> SetCtx --> Try
    NeedSwitch -- False --> Try
    CheckIN -- True --> Try
    Try --> WithCtx --> WarnCheck
    WarnCheck -- True --> Warn --> Call
    WarnCheck -- False --> Call
    Call --> Finally --> End

Notes:
- backend_context is always called as backend_context(tmp_backend) inside the with-statement; _null_backend_context is expected to accept the same signature as set_interactive_backend but perform no actions.

## Edge cases and implementation details:
- tmp_backend initial values:
  - If plot_kwargs lacks 'mpl_backend' tmp_backend will be None and the _null_backend_context will be used; set_interactive_backend is not considered.
  - If plot_kwargs['mpl_backend'] == 'auto', tmp_backend becomes HYPERTOOLS_BACKEND.normalize() (which may raise if HYPERTOOLS_BACKEND is misconfigured).
  - If tmp_backend equals 'disable' (string), no backend context is used (i.e., set_interactive_backend is not selected).
- Equality comparison and matching semantics:
  - curr_backend is obtained as a HypertoolsBackend instance (result of HypertoolsBackend(...).normalize()).
  - HypertoolsBackend implements case-insensitive equality and hashing. Therefore, comparing a plain-string tmp_backend against curr_backend will behave case-insensitively due to HypertoolsBackend's equality semantics. Callers can rely on this case-insensitive comparison, but for determinism prefer using backend identifiers produced by HypertoolsBackend.normalize() or canonical keys from BACKEND_MAPPING.
- IN_SET_CONTEXT:
  - If True, the wrapper skips backend-selection logic entirely (uses the no-op context) to avoid nested or reentrant backend switching.

## Examples (practical usage patterns):
1) Decorating a plotting function:
    - @manage_backend
      def plot(data, animate=False, interactive=False, mpl_backend=None):
          # plotting code...
          pass
    - Calling plot(data, animate=True) will inspect runtime arguments and may enter set_interactive_backend if a backend change is required.

2) Handling a backend normalization error:
    - If HypertoolsBackend.normalize() raises KeyError for an unrecognized backend, callers can catch KeyError and provide a fallback:
      try:
          plot(..., mpl_backend='some-unknown-backend')
      except KeyError:
          # fallback: use a safe backend or inform the user

3) Note on rcParams restoration:
    - Because the wrapper calls mpl.rcParams.update(**old_rcParams) to restore settings, keys added to mpl.rcParams during the call remain present afterwards; to fully revert additions/deletions, callers must explicitly manage rcParams or use a deeper snapshot/restore mechanism.

## Reimplementation hints:
- Do not attempt to replicate argument binding logic; call _get_runtime_args to obtain a mapping of parameter names to values.
- Preserve function metadata using functools.wraps when returning the wrapper.
- Ensure the finally block uses warnings.catch_warnings() and warnings.simplefilter('ignore', mpl.MatplotlibDeprecationWarning) while calling mpl.rcParams.update(**old_rcParams).
- Use _null_backend_context as the default context factory and only switch to set_interactive_backend when animate/interactive are requested and tmp_backend is neither 'disable' nor equal to the current normalized backend.

