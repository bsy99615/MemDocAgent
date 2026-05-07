# `compare_reports.py`

## `src.ydata_profiling.compare_reports._should_wrap` · *function*

## Summary:
Decides whether two values should be considered equal for wrapping/presentation by applying type-aware equality checks and returning the equality result (typically a boolean).

## Description:
Performs a small, conservative equality policy used by report comparison logic: it short-circuits for certain container types, uses pandas-specific equality for DataFrame/Series, and otherwise falls back to Python's equality operator.

Known callers:
- No explicit callers were discoverable in the provided context. Typical usage is inside report-diff or compare-report code paths where the system must decide whether two corresponding values from different profiling reports are "the same" and therefore need not be wrapped or highlighted.

Why this is a separate function:
- Centralizes the nuanced equality policy (special-casing of list/dict, pandas objects, and exception handling) so the higher-level comparison code does not repeat fragile equality logic.
- Makes it easier to test and change equality semantics in one place without touching the larger comparison flow.

## Args:
    v1 (Any): First value to compare. Common runtime types include scalars, pandas.DataFrame, pandas.Series, list, dict, numpy.ndarray, or custom objects.
    v2 (Any): Second value to compare; typically the corresponding value from another report or snapshot.

Interdependencies and notes:
- The function only inspects the type of v1 for the list/dict short-circuit (if v1 is a list or dict the function returns False immediately, regardless of v2's type).
- The module must bind pandas to the name pd (e.g., import pandas as pd) because the implementation uses pd.DataFrame and pd.Series in isinstance checks.

## Returns:
    bool or Any: The equality result. The function intends to return a boolean indicating equality, and in the common cases it does:
    - Returns False immediately if v1 is an instance of list or dict.
    - If both v1 and v2 are pandas.DataFrame, returns the boolean from v1.equals(v2).
    - If both v1 and v2 are pandas.Series, returns the boolean from v1.equals(v2).
    - Otherwise, returns the direct result of v1 == v2.

Important detail:
- The fallback v1 == v2 may return non-boolean objects (for example, numpy.ndarray of booleans). In those cases this function returns that non-bool value unchanged. Callers that assume a strict Python bool should coerce the result (for example with bool(...) or .all() / .any() for array-like results) or handle array-like comparisons explicitly.

All possible return scenarios:
- True/False (most common)
- A numpy.ndarray of booleans (or similar array-like) when v1 == v2 yields an array-like result
- Any other object returned by a custom __eq__ implementation

## Raises:
    - ValueError: Not raised to callers—if v1 == v2 raises ValueError, the function catches it and returns False.
    - Any other exception (e.g., TypeError, AttributeError, NameError) raised by the equality operation or by the isinstance checks is not caught and will propagate:
        * TypeError: may be raised by some __eq__ implementations or by comparing incompatible types.
        * NameError: will be raised if the module does not define pd (missing pandas alias).
        * Other exceptions defined by custom __eq__ implementations.

## Constraints:
Preconditions:
- The module namespace must make pandas available as pd (e.g., import pandas as pd) to avoid NameError on isinstance checks for DataFrame/Series.
- Callers that require a strict boolean result must handle or convert non-boolean equality results themselves.

Postconditions:
- The function returns immediately with a value representing equality according to the described rules and does not mutate v1 or v2.
- No file, network, or global state is changed.

## Side Effects:
- The function itself has no intended side effects.
- If v1 == v2 invokes user-defined equality logic, any side effects in that operator will occur (those are outside this function's control).

## Control Flow:
flowchart TD
    Start --> IsListDict{isinstance(v1, (list, dict))}
    IsListDict -- Yes --> ReturnFalse1[return False]
    IsListDict -- No --> IsBothDF{isinstance(v1, pd.DataFrame) and isinstance(v2, pd.DataFrame)}
    IsBothDF -- Yes --> DFEquals[v1.equals(v2)]
    DFEquals --> ReturnDF[return result (bool)]
    IsBothDF -- No --> IsBothSeries{isinstance(v1, pd.Series) and isinstance(v2, pd.Series)}
    IsBothSeries -- Yes --> SEquals[v1.equals(v2)]
    SEquals --> ReturnS[return result (bool)]
    IsBothSeries -- No --> TryEq[try: return v1 == v2]
    TryEq --> EqSuccess[comparison returned value]
    EqSuccess --> ReturnEq[return that value (may be non-bool)]
    TryEq --> EqValueError[ValueError raised]
    EqValueError --> ReturnFalse2[return False]

## Examples (realistic scenarios and guidance):
- Lists/Dicts:
  - Scenario: v1 = [1, 2, 3], v2 = [1, 2, 3] -> Result: False (function short-circuits on v1 being a list; it does not perform structural comparison).
  - Guidance: If structural equality for sequences/mappings is required, callers should perform their own comparison (for example, v1 == v2 or deep equality utilities) instead of relying on this function.

- pandas objects:
  - Scenario: v1 and v2 are pandas.DataFrame with identical content -> Result: True if v1.equals(v2) is True.
  - Scenario: v1 and v2 are pandas.Series with identical content -> Result: True if v1.equals(v2) is True.

- Scalars and typical objects:
  - Scenario: v1 = 5, v2 = 5 -> Result: True (fallback to v1 == v2).
  - Scenario: v1 = "a", v2 = "b" -> Result: False.

- numpy arrays:
  - Scenario: v1 and v2 are numpy arrays with identical contents. The expression v1 == v2 yields a numpy ndarray of booleans; this function returns that ndarray (not a single bool). Callers that use the return value in boolean contexts (e.g., if result:) will encounter a ValueError from numpy about ambiguous truth value. Guidance: callers should convert the ndarray result to a single boolean using .all() or .any() before using it as a truth value.

- Exceptions in __eq__:
  - Scenario: v1.__eq__(v2) raises ValueError -> Result: False (caught and mapped to False).
  - Scenario: v1.__eq__(v2) raises TypeError -> Result: TypeError propagates to the caller; callers should catch such exceptions if needed.

## `src.ydata_profiling.compare_reports._update_merge_dict` · *function*

## Summary:
Merges two mapping-like objects into a new dictionary containing the union of keys; for keys present in both inputs it either wraps the two values into a two-element list or delegates to the mixed-merge policy to produce a merged value.

## Description:
This function produces a shallow union of two dictionaries while applying a special merge policy for keys present in both inputs. For each key that appears in both d1 and d2:
- If the equality policy _should_wrap(d1[k], d2[k]) indicates the values should be wrapped, the resulting value for that key is the two-element list [d1[k], d2[k]].
- Otherwise, the two values are combined by calling _update_merge_mixed(d1[k], d2[k]) which either recursively deep-merges dictionaries or applies the sequence-merge policy for non-dicts.

Known callers:
- _update_merge_mixed (when both operands are dictionaries, it delegates to this function to merge them).
- Typical usage: invoked as part of the compare/merge pipeline in the compare_reports module when two profile-report fragments or nested description dictionaries need to be merged.

Why this is a separate function:
- Encapsulates the dictionary-specific merging pattern (union of keys with special handling of overlapping keys), keeping the logic concise and reusable by recursive callers. It separates the concerns of: enumerating keys, wrapping vs. merging overlapping values, and constructing the resulting dict without mutating the inputs.

## Args:
    d1 (Any):
        - Expected to be a mapping-like object (typically a dict) with hashable keys and support for iteration over keys and subscription (d1[k]).
        - If a non-iterable or non-mapping is passed, a TypeError or similar exception will occur.
    d2 (Any):
        - Same expectations as d1.

Notes on interdependencies:
- The function relies on two helpers in the same module:
    - _should_wrap(value1, value2): decides whether overlapping values should be wrapped into [value1, value2].
    - _update_merge_mixed(value1, value2): merges or combines two non-wrappable values (may call _update_merge_dict again for nested dicts).
- The function's correct behavior depends on those helpers' documented semantics.

## Returns:
    dict:
        - A new dictionary representing the merged result.
        - Keys present only in d1 appear with their original value from d1 unless a key also exists in d2 (in which case the merged logic applies).
        - Keys present only in d2 appear with their original value from d2.
        - Keys present in both appear with value:
            * [d1[k], d2[k]] if _should_wrap(d1[k], d2[k]) is truthy,
            * otherwise the value returned by _update_merge_mixed(d1[k], d2[k]) (which may be a dict, list, or tuple depending on the helper's rules).
        - The function always returns a dict when it completes normally.

## Raises:
    - TypeError:
        - If d1 or d2 are not iterable/mapping-like (so {*d1} or {*d2} fails) or do not support subscription by key.
    - Any exception raised by:
        - _should_wrap(d1[k], d2[k]) (e.g., if that function raises due to underlying equality logic),
        - _update_merge_mixed(d1[k], d2[k]) (e.g., due to unexpected types inside nested structures).
    - These exceptions propagate to the caller; the function does not catch them.

## Constraints:
Preconditions:
    - Both d1 and d2 should be mapping-like objects (dicts or similar) with iterable keys and support for subscription using those keys.
    - Keys in d1 and d2 must be hashable (as required by Python dict semantics).
    - Callers expecting boolean semantics from _should_wrap must ensure that helper returns a truthy/falsey value per its contract.

Postconditions:
    - The returned dictionary contains the union of keys from d1 and d2.
    - Input objects d1 and d2 are not modified by this function; a new dict is returned.
    - Overlapping keys are resolved according to the wrap-vs-merge policy described above.

## Side Effects:
    - None intrinsic to this function: no I/O, no global state modification, and no in-place mutation of d1 or d2.
    - Side effects may occur indirectly if helper functions or user-defined __eq__ implementations invoked by _should_wrap produce side effects; those are outside this function's control.

## Control Flow:
flowchart TD
    Start --> ValidateInputs{Are d1 and d2 mapping-like?}
    ValidateInputs -- No --> Error[TypeError or iteration/subscription error]
    ValidateInputs -- Yes --> BuildBase[Create base dict: copy of d1 then d2]
    BuildBase --> ComputeOverlap{For each k in intersection of keys}
    ComputeOverlap --> ForKey{Process single overlapping key k}
    ForKey --> ShouldWrap[_should_wrap(d1[k], d2[k])]
    ShouldWrap -- True --> SetWrapped[use value [d1[k], d2[k]] for k]
    ShouldWrap -- False --> CallMixed[_update_merge_mixed(d1[k], d2[k])]
    CallMixed --> SetMixed[use result for k]
    SetWrapped --> NextKey[continue for remaining overlapping keys]
    SetMixed --> NextKey
    NextKey --> Done[Unpack merged overlapping-key dict into base and return]
    Done --> End

## Examples:
1) Simple non-overlapping keys
    - Input:
        d1 = {"a": 1}
        d2 = {"b": 2}
    - Result:
        {"a": 1, "b": 2}

2) Overlapping key where values should be wrapped
    - Given _should_wrap(1, 2) returns True
    - Input:
        d1 = {"x": 1}
        d2 = {"x": 2}
    - Result:
        {"x": [1, 2]}

3) Overlapping key delegated to mixed merge (nested dict merge)
    - Suppose _should_wrap returns False and _update_merge_mixed merges dicts recursively.
    - Input:
        d1 = {"x": {"y": 1}}
        d2 = {"x": {"z": 2}}
    - Result (after recursive merging):
        {"x": {"y": 1, "z": 2}}

4) Nested mixture: sequence and dict
    - If values for an overlapping key are non-dict and not wrappable, the merged value will be whatever _update_merge_mixed produces (e.g., a list or tuple).
    - Input:
        d1 = {"k": [1]}
        d2 = {"k": ["a"]}
    - Possible Result (depending on _should_wrap and _update_merge_mixed rules):
        {"k": ([1], ["a"])}  or {"k": [[1], ["a"]]}  (see _update_merge_seq / _update_merge_mixed for precise sequence policy)

Usage guidance:
- Ensure d1 and d2 are dict-like. This function is intended to be used as a deterministic, non-mutating dictionary merge step inside the report-compare pipeline; for other merging policies (e.g., full structural deep-merge that flattens lists or concatenates sequences differently) call or implement the appropriate helper.

## `src.ydata_profiling.compare_reports._update_merge_seq` · *function*

## Summary:
Normalizes and combines two "sequence-like" values into either a tuple or a flattened list according to a small set of rules, preserving list wrappers in one branch and flattening in others.

## Description:
This helper determines how two values representing update sequences (or single items) should be merged and returns either:
- a tuple containing both original lists (when both inputs are lists),
- a tuple formed by appending the second value as a single element to the elements of the first tuple (when the first input is a tuple and the second is a list),
- or a flattened list that contains the elements of inputs (if any input is a list its elements are flattened into the result; otherwise inputs are wrapped as single elements).

Known callers:
- No direct callers were discovered in the provided context. This function is intended for use inside the compare_reports module (or similar merging logic) to centralize the small but non-trivial decision logic for how two "update sequences" should be combined.

Why this is a separate function:
- The branching logic encodes a specific and non-obvious merging policy (preserve two-list pair as a tuple vs. flatten otherwise). Extracting it to a small, well-documented function avoids repeating this policy at every merge site and makes the behavior easier to test and reason about.

## Args:
    d1 (Any):
        - Primary value to merge. Typical values: list, tuple, or any scalar/object.
        - The function checks specifically for list and tuple types; other types are treated as single items and will be wrapped in a list when producing a flattened list result.
    d2 (Any):
        - Secondary value to merge. Typical values: list, tuple, or any scalar/object.
        - The function checks specifically for list type for certain branches; other types are treated as single items and will be wrapped in a list when producing a flattened list result.

Interdependencies:
    - Behavior depends only on the runtime types of d1 and d2 (isinstance checks for list and tuple). There are no other parameter interdependencies.

## Returns:
    Union[list, tuple]:
    - If both d1 and d2 are lists:
        Returns a 2-tuple: (d1, d2). Both lists are returned unchanged and not flattened or concatenated.
    - Elif d1 is a tuple and d2 is a list:
        Returns a tuple created by unpacking the elements of d1 and adding d2 as one final element. In other words, the result is a tuple whose first N elements are the elements of d1 and whose last element is the list object d2 itself (not its elements).
    - Else (all other type combinations):
        Returns a list whose elements are:
            - the elements of d1 if d1 is a list, otherwise the single element d1,
            - followed by the elements of d2 if d2 is a list, otherwise the single element d2.
        This branch flattens lists into their elements and wraps non-list values as single-element entries.

Edge-case return behaviors:
    - If d1 and/or d2 are None, they will be wrapped like any other non-list/tuple value (None becomes a list element or tuple element depending on branch).
    - If d1 is a tuple and d2 is not a list, the code does not match the second branch and falls through to the else branch; the tuple will be wrapped as a single element (so the resulting list will contain the tuple as one element, not its contents).
    - No branch returns None.

## Raises:
    - The function does not explicitly raise exceptions.
    - Potential runtime exceptions only arise from misuse of Python language features outside the guarded branches (none in current code). Given the explicit isinstance checks and the operations used (tuple/list construction and sequence unpacking of an object already verified as a tuple), normal usage will not raise. If the Python runtime is inconsistent (e.g., a custom object that breaks tuple unpacking despite isinstance(obj, tuple)) a TypeError could occur, but this is not expected for normal built-in list/tuple/scalar inputs.

## Constraints:
Preconditions:
    - No preconditions enforced by the function beyond valid Python objects for d1 and d2. The function relies only on runtime type checks (isinstance for list and tuple).
Postconditions:
    - The return value is either a tuple or a list as described in Returns.
    - Original input objects are not mutated by this function; lists and tuples are returned directly or referenced (no copies are made).

## Side Effects:
    - None. The function performs no I/O, does not mutate its inputs, and does not touch global state or external services.

## Control Flow:
flowchart TD
    Start --> CheckBothLists
    CheckBothLists{isinstance(d1, list) and isinstance(d2, list)}
    CheckBothLists -->|yes| ReturnTupleOfLists[Return (d1, d2) (tuple of two lists)]
    CheckBothLists -->|no| CheckTupleList
    CheckTupleList{isinstance(d1, tuple) and isinstance(d2, list)}
    CheckTupleList -->|yes| ReturnTupleUnpack[Return (*d1, d2) (tuple: elements of d1, then d2 as one element)]
    CheckTupleList -->|no| ReturnFlattenedList[Return flattened list: elements(d1 if list else [d1]) + elements(d2 if list else [d2])]
    ReturnFlattenedList --> End
    ReturnTupleUnpack --> End
    ReturnTupleOfLists --> End

## Examples:
- Example A: both inputs are lists
    - Input: d1 = [1, 2], d2 = ["a", "b"]
    - Output: a tuple containing the two lists: ([1, 2], ["a", "b"])
    - Rationale: when both are lists, the function preserves them as two sequence objects inside a tuple.

- Example B: first is tuple, second is list
    - Input: d1 = (1, 2), d2 = ["a", "b"]
    - Output: a tuple where the first elements are the tuple items and the last element is the list object: (1, 2, ["a", "b"])
    - Rationale: the function unpacks the tuple elements and appends the list as a single element.

- Example C: mixed or scalar inputs (flattening branch)
    - Input: d1 = [1, 2], d2 = "x"
    - Output: a list with flattened elements and scalar wrapped: [1, 2, "x"]
    - Input: d1 = 1, d2 = 2
    - Output: [1, 2]
    - Input: d1 = (1, 2), d2 = (3, 4)
    - Output: [(1, 2), (3, 4)]  (each tuple is wrapped as a single element because neither is a list)

- Example D: None-handling
    - Input: d1 = None, d2 = [1]
    - Output: [None, 1]  (None wrapped, list flattened)

Usage note:
- Choose this function when you need a small deterministic policy to combine two update/sequence-like values and want the specific preservation vs. flattening semantics described above.

## `src.ydata_profiling.compare_reports._update_merge_mixed` · *function*

## Summary:
Choose the correct merge strategy for two values: perform a deep dict-merge when both inputs are dictionaries; otherwise combine them using the sequence-merge policy (producing a list or tuple).

## Description:
This dispatcher centralizes the decision of whether two values should be merged as dictionaries or combined via the sequence/list/tuple policy.

Known callers within the codebase:
- src.ydata_profiling.compare_reports._update_merge_dict — used recursively when merging overlapping keys in dictionaries (see that function for the merging context and examples).

Typical calling context:
- Merging two fragments of a profile report or nested description where some values are nested dicts (which should be merged structurally) and others are sequence-like values (which should be combined with a small set of preservation vs. flattening rules). Callers rely on deterministic, recursive behavior: dicts are merged key-by-key, and non-dict values follow the sequence policy.

Why this is a separate function:
- The binary decision (both-dicts vs non-dicts) is the critical branching point used recursively. Extracting it reduces duplication and isolates the responsibility of choosing and delegating to the specialized merge strategies:
  - src.ydata_profiling.compare_reports._update_merge_dict (dict deep-merge)
  - src.ydata_profiling.compare_reports._update_merge_seq (list/tuple/scalar merge policy)

## Args:
    d1 (Any):
        - Left/primary value. Common types: dict, list, tuple, scalar, or None.
    d2 (Any):
        - Right/secondary value. Same common types as d1.
    Notes:
        - The function performs only an isinstance(d1, dict) and isinstance(d2, dict) check; behavior depends only on those runtime checks.

## Returns:
    Union[dict, list, tuple]
    - If both d1 and d2 are dict instances:
        - Returns the dict produced by _update_merge_dict(d1, d2). That result contains keys from both inputs and merges overlapping keys recursively using this dispatcher for nested values.
    - Otherwise:
        - Returns the result of _update_merge_seq(d1, d2). That helper returns either a tuple or a list according to its documented rules (e.g., two lists -> tuple of lists; otherwise lists are flattened into an output list, etc.).
    - Edge cases:
        - This dispatcher itself never returns None; the exact shape (dict/list/tuple) is determined by the delegated helper.
        - Passing None as a non-dict value is treated like any other scalar by the sequence-merge policy.

## Raises:
    - Under normal usage, this dispatcher does not raise exceptions.
    - Both delegated helpers are documented to use only runtime type checks and do not intentionally raise exceptions; therefore no exceptions are expected from typical, well-formed inputs.
    - As with any Python code, unexpected runtime errors (e.g., pathological custom object implementations that break basic sequence semantics) could raise built-in exceptions (TypeError, AttributeError), but such errors are not part of the documented behavior.

## Constraints:
    Preconditions:
        - No further validation is performed: callers should ensure inputs are the intended objects if they need stricter guarantees.
    Postconditions:
        - If both inputs were dict instances, the return value is a dict (deep-merge semantics handled by _update_merge_dict).
        - Otherwise, the return value is a list or tuple as defined by _update_merge_seq.
        - The dispatcher does not perform in-place mutation; helper documentation indicates inputs are not mutated.

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and does not mutate its inputs directly. Any side-effect behavior would originate from code outside this dispatcher (none expected here).

## Control Flow:
flowchart TD
    Start --> AreBothDicts{isinstance(d1, dict) and isinstance(d2, dict)}
    AreBothDicts -->|yes| CallDict[_update_merge_dict(d1, d2)]
    CallDict --> ReturnDict[return dict result]
    AreBothDicts -->|no| CallSeq[_update_merge_seq(d1, d2)]
    CallSeq --> ReturnSeq[return list or tuple result]
    ReturnDict --> End
    ReturnSeq --> End

## Examples:
- Both inputs are dicts (simple merge):
    - Input: d1 = {"a": 1}, d2 = {"b": 2}
    - Call: _update_merge_mixed(d1, d2)
    - Result: {"a": 1, "b": 2}  (handled by _update_merge_dict)

- Nested dicts with overlapping keys (recursive merge):
    - Input: d1 = {"x": {"y": [1]}}, d2 = {"x": {"y": [2]}}
    - Call: _update_merge_mixed(d1, d2)
    - Result: Determined by _update_merge_dict which will call this dispatcher recursively to merge the nested "y" values; see _update_merge_dict and _update_merge_seq for the exact nested merging outcome.

- Non-dict inputs (delegates to sequence policy):
    - Input: d1 = [1, 2], d2 = ["a", "b"]
    - Call: _update_merge_mixed(d1, d2)
    - Result: ([1, 2], ["a", "b"])  (two lists are preserved as a tuple by _update_merge_seq)

- Scalars (flattening branch of sequence policy):
    - Input: d1 = 1, d2 = 2
    - Call: _update_merge_mixed(d1, d2)
    - Result: [1, 2]  (flattened list as returned by _update_merge_seq)

See also:
- src.ydata_profiling.compare_reports._update_merge_dict
- src.ydata_profiling.compare_reports._update_merge_seq

## `src.ydata_profiling.compare_reports._update_merge` · *function*

## Summary:
Return a merged dictionary result for two profile-description mappings: if the first mapping is None, return the second as-is; otherwise validate both are dicts and delegate to the dictionary-merge helper to produce a merged dict.

## Description:
This helper enforces the top-level behavior and validation for merging two mapping-like description fragments (typically ProfileReport.description_set entries) before delegating the actual dictionary-merge logic to the specialized helper.

Known callers and typical context:
- Used by other merge utilities in the same compare_reports module (the compare/merge pipeline) that combine fragments of ProfileReport.description_set or nested description dictionaries.
- Indirectly involved in recursive merge flows: _update_merge_dict and _update_merge_mixed call each other and call this function at appropriate levels.
- Typical trigger: when two report fragments (possibly subtrees of a profile description) need to be combined into a single description mapping during comparison/merge of ProfileReport objects.

Why this logic is a separate function:
- Separates top-level validation and the simple None-as-empty-operand policy from the more detailed dictionary-merge semantics (implemented in _update_merge_dict). This keeps callers concise and centralizes the entry-point behavior (None handling and type checking).

## Args:
    d1 (Optional[dict]):
        - The "left" mapping to be merged. If None, this function returns d2 immediately (no type validation of d2 is performed).
        - Expected to be a dict when not None.
    d2 (dict):
        - The "right" mapping to be merged into d1.
        - Annotated as dict; used as-is when d1 is None; otherwise validated to be a dict.

Notes on interdependencies:
- When both d1 and d2 are dicts, this function delegates to _update_merge_dict(d1, d2) which produces a new merged dict (see that helper's documentation for exact merging rules).
- The behavior of the merge result (for overlapping keys) depends on _should_wrap and _update_merge_mixed, which are used by _update_merge_dict.

## Returns:
    dict:
        - If d1 is None: returns d2 exactly as provided (no copy, no validation).
        - If d1 is not None and both arguments are dicts: returns the result returned by _update_merge_dict(d1, d2). That helper returns a new dict representing the union of keys with special handling for overlapping keys.
        - There is no other return type on normal completion; the function's annotated and actual successful return types are dict.

Edge-case returns:
    - If d1 is None and d2 is not a dict (contradicting the annotation), this function will still return that non-dict value unchanged (this is an observed behavior of the implementation).

## Raises:
    TypeError:
        - Raised when d1 is not None and either d1 or d2 is not a dict.
        - Exact exception message:
            "Both arguments need to be of type dictionary (ProfileReport.description_set)"
    Propagated exceptions:
        - Any exception raised by _update_merge_dict (or any helper it calls) will propagate to the caller.

## Constraints:
Preconditions:
    - Callers should pass d1 as None or a dict; d2 should be a dict to match the annotated contract.
    - If d1 is None, be aware that d2 is returned as-is (so callers expecting a new dict copy must copy d2 before calling).

Postconditions:
    - If d1 is None: the returned object is exactly the same object as the provided d2.
    - If d1 and d2 are dicts: the returned value is a dict produced by _update_merge_dict and inputs are not mutated by this function itself (see _update_merge_dict for mutation guarantees).
    - If this function raises TypeError, no merge has occurred.

## Side Effects:
    - None directly. The function performs no I/O and does not mutate global state.
    - Note: if d1 is None and d2 is a mutable object, returning it as-is means subsequent mutations to the returned object will affect the original object referenced by the caller.
    - Any side effects produced by helper functions called later (when both args are dicts) are possible but not caused by this wrapper.

## Control Flow:
flowchart TD
    Start --> IsD1None{d1 is None?}
    IsD1None -- Yes --> ReturnD2[return d2 (no validation)]
    IsD1None -- No --> TypeCheck{are d1 and d2 both dict?}
    TypeCheck -- No --> Raise[raise TypeError with message "Both arguments need to be of type dictionary (ProfileReport.description_set)"]
    TypeCheck -- Yes --> Delegate[return _update_merge_dict(d1, d2)]
    Delegate --> End

## Examples:
1) Simple merge (both dicts)
    - Inputs:
        d1 = {"a": 1}
        d2 = {"b": 2}
    - Behavior:
        d1 is not None and both are dicts -> delegates to _update_merge_dict and returns merged dict (e.g., {"a": 1, "b": 2}).

2) First operand is None
    - Inputs:
        d1 = None
        d2 = {"a": 1}
    - Behavior:
        Immediately returns d2 exactly (no copy). Caller receives the same object {"a": 1}.

3) Type error when both present but not dicts
    - Inputs:
        d1 = ["not", "a", "dict"]
        d2 = {"a": 1}
    - Behavior:
        d1 is not None, d1 is not a dict -> raises TypeError with message:
        "Both arguments need to be of type dictionary (ProfileReport.description_set)"

4) Subtle edge-case: d1 is None but d2 is not a dict
    - Inputs:
        d1 = None
        d2 = ["list-not-dict"]
    - Behavior:
        Because of the early return, the function returns d2 (the list) unchanged; no TypeError is raised even though d2 violates the annotated type.

Usage guidance:
- Prefer to ensure d2 is a dict even when d1 may be None (to conform to the function's contract).
- If you need a defensive copy when d1 is None, call copy(d2) prior to calling this function or copy the result.
- For details on how overlapping keys are merged when both args are dicts, consult the documentation for _update_merge_dict and its helpers (_should_wrap, _update_merge_mixed).

## `src.ydata_profiling.compare_reports._placeholders` · *function*

## Summary:
Normalize multiple BaseDescription objects in-place so each has the same scatter row/column keys (filling missing cells with empty strings) and the same table["types"] keys (filling missing counts with 0).

## Description:
Known callers within the provided context:
- No explicit call sites for this private helper were provided in the supplied files. It is intended for use by report comparison, alignment, or merging routines that operate on multiple BaseDescription-like objects (e.g., functions that compare ProfileReport outputs or aggregate statistics across reports).

Typical trigger/context:
- Call when multiple BaseDescription objects must be compared or combined and downstream code requires that every report exposes identical scatter keys and identical type-key sets so it can iterate across keys without per-report existence checks.

Why extracted:
- Centralizes the normalization logic for scatter matrices and type-count mappings, avoiding duplicated placeholder-filling logic across comparison/merge code paths. The function enforces a single policy for default values (empty string for scatter cells and 0 for missing type counts) and performs modifications in-place to avoid extra memory copies.

## Args:
    reports (List[BaseDescription]):
        - A list of objects expected to have the following attributes (the function does not validate types beyond attribute access and dictionary operations):
            * scatter: a mapping-like object whose keys are labels and whose values are mapping-like objects that map labels to cell values (the function will use membership checks and item assignment: report.scatter[k1], report.scatter[k1][k2] = ...).
            * table: a mapping-like object that must contain the key "types".
            * table["types"]: a mapping-like object mapping type_key -> integer counts.
        - Allowed values:
            * reports may be empty (the function will do nothing and return).
        - Interdependencies:
            * The union of scatter keys and the union of table["types"] keys are computed from the entire reports list and then applied to every report.

## Returns:
    None
    - The function mutates the provided BaseDescription objects in-place.
    - Guarantees on return:
        * For each report and for each label k1 in the computed union of scatter keys, report.scatter will contain a key k1 mapping to a mapping-like object (if missing, an empty dict is assigned).
        * For every pair (k1, k2) in that union, report.scatter[k1][k2] will exist; if it did not exist before, it will be set to the empty string "".
        * For each report and each type_key in the computed union of table["types"] keys, report.table["types"][type_key] will exist; if it did not exist before, it will be set to integer 0.

## Raises:
    The function performs direct attribute access and mappings operations; the following exceptions can be raised by the implementation as written:
    - KeyError:
        * When computing type_keys: if any report.table does not contain the key "types", the comprehension r.table["types"] will raise KeyError.
    - AttributeError:
        * If a report object lacks the scatter or table attributes entirely, accessing r.scatter or r.table will raise AttributeError.
    - TypeError:
        * If report.scatter is not a mapping-like object (so membership iteration or assignment fails), or if report.scatter[k1] is not a mapping-like object (so report.scatter[k1][k2] assignment fails), a TypeError may be raised.
    - Any exception raised while indexing or assigning into the report objects will propagate; the function does not catch or translate exceptions.

## Constraints:
Preconditions (caller responsibility):
    - Each item in reports should be a BaseDescription-like object with:
        * report.scatter supporting iteration over keys, membership tests, indexing and assignment of mapping values (e.g., a dict[str, dict[str, Any]]).
        * report.table supporting indexing and containing the key "types".
        * report.table["types"] supporting iteration over keys, membership tests, and item assignment (e.g., a dict[str, int]).
    - If these preconditions are not met, callers should either pre-normalize the objects or catch the exceptions listed above.

Postconditions (guaranteed by this function):
    - All reports share the same set of scatter keys (the union collected at the start).
    - For every combination of those keys, report.scatter contains nested entries so report.scatter[k1][k2] is present (new entries set to "").
    - All reports' table["types"] mappings contain the same set of keys (missing keys set to 0).

Performance characteristics:
    - Let R = number of reports, K = number of unique scatter keys (size of the computed union).
    - Time complexity: O(R * K^2) due to nested loops over keys for each report.
    - Space complexity: O(K + T) extra where T is number of unique type keys (for the small sets used during union computation); the function mutates inputs in-place and does not create deep copies.

## Side Effects:
    - Mutates the provided BaseDescription objects in-place (adds keys/entries to report.scatter and report.table["types"]).
    - No file, network, or stdout I/O.
    - No other external/global state is modified.

## Control Flow:
flowchart TD
    Start[Start: receive reports list] --> Compute[Compute keys = union of all r.scatter keys; type_keys = union of all r.table["types"] keys]
    Compute --> ReportsLoop[For each report in reports]
    ReportsLoop --> RowLoop[For each k1 in keys]
    RowLoop --> ColLoop[For each k2 in keys]
    ColLoop --> CheckRow{k1 in report.scatter?}
    CheckRow -- No --> AssignRow[report.scatter[k1] = {}]
    CheckRow -- Yes --> SkipRow[do nothing]
    AssignRow --> CheckCell
    SkipRow --> CheckCell
    CheckCell{k2 in report.scatter[k1]?}
    CheckCell -- No --> AssignCell[report.scatter[k1][k2] = ""]
    CheckCell -- Yes --> SkipCell[do nothing]
    AssignCell --> ContinueCell
    SkipCell --> ContinueCell
    ContinueCell --> NextCol
    NextCol --> AfterCols[Finished all k2 for this k1]
    AfterCols --> NextRow
    NextRow --> AfterRows[Finished all k1 for this report]
    AfterRows --> TypeLoop[For each type_key in type_keys]
    TypeLoop --> CheckType{type_key in report.table["types"]?}
    CheckType -- No --> AssignType[report.table["types"][type_key] = 0]
    CheckType -- Yes --> SkipType[do nothing]
    AssignType --> NextType
    SkipType --> NextType
    NextType --> DoneReport
    DoneReport --> NextReport
    NextReport --> End[All reports processed -> End]

## Examples:
Example — aligning two simple in-memory report objects:
    # Setup (conceptual, not executable here):
    report_a.scatter == {"a": {"a": "x"}}
    report_a.table == {"types": {"int": 2}}
    report_b.scatter == {"b": {"b": "y"}}
    report_b.table == {"types": {"float": 1}}

    After calling _placeholders([report_a, report_b]):
    - Both report_a.scatter and report_b.scatter will have rows and columns "a" and "b".
    - Newly created cells (those absent before the call) will contain the empty string "".
    - report_a.table["types"]["float"] will be set to 0 and report_b.table["types"]["int"] will be set to 0.

Defensive usage pattern:
    - If reports may not have table["types"], pre-initialize or guard the call:
        * for r in reports:
            if not hasattr(r, "table") or "types" not in getattr(r, "table", {}):
                r.table = r.table if hasattr(r, "table") else {}
                r.table["types"] = {}
        * then call _placeholders(reports)
    - Alternatively, wrap the call in try/except to handle KeyError/AttributeError from malformed inputs.

## `src.ydata_profiling.compare_reports._update_titles` · *function*

## Summary:
Replace default report titles in-place by converting any title exactly equal to "Pandas Profiling Report" to "Dataset X" where X is a single uppercase character derived from the report's zero-based index (A, B, C, ...).

## Description:
This function scans the supplied list of ProfileReport objects and updates their .config.title attribute when it exactly matches the library default string "Pandas Profiling Report". The replacement title for the report at index i is computed as "Dataset " + chr(65 + i) (so index 0 -> "Dataset A", index 1 -> "Dataset B", etc.). The mutation happens in-place; no new report objects or lists are returned.

Known callers and context:
- In the provided code snapshot there are no explicit call sites found for this helper. Its intended use is within higher-level comparison or aggregation logic that prepares multiple ProfileReport instances for side-by-side presentation or export, so that reports that kept the default title become distinguishable.
- Typical trigger: call this immediately prior to rendering, exporting, or merging several ProfileReport objects when you want default titles made unique and human-friendly.

Why this is a separate function:
- Encapsulates a single, well-scoped transformation (default-title normalization).
- Avoids duplicating title-renaming logic across different comparison/export routines.
- Facilitates unit testing for this specific normalization behavior.

## Args:
    reports (List[ProfileReport]):
        - Required. A list (typed as List[ProfileReport]) of ProfileReport instances.
        - Each element is expected to expose a .config attribute with a .title property (typically a string).
        - The resulting title depends on the element's position in this list: index 0 maps to 'A', index 1 to 'B', etc.

## Returns:
    None
    - The function does not return a value. It mutates the .config.title of matching ProfileReport objects in-place.

## Raises:
    - The function does not raise custom exceptions.
    - Possible runtime exceptions stemming from invalid inputs:
        * AttributeError: if an element in reports lacks .config or .config.title.
        * TypeError: if reports is not iterable (e.g., None) or if an element's .config is present but .title access raises a TypeError.
    - These exceptions are not intentionally raised by the function but will surface if callers provide incompatible objects.

## Constraints:
Preconditions:
    - `reports` must be an iterable (preferably a list) of objects where each object exposes `.config.title`.
    - The function compares `.config.title` using equality to the string "Pandas Profiling Report"; only exact matches are changed.
Postconditions:
    - For every report at index i whose original `.config.title` was exactly "Pandas Profiling Report", its `.config.title` will equal f"Dataset {chr(65 + i)}".
    - Reports whose titles did not match the exact default string remain unchanged.
    - Operation is performed in-place; object identity of reports and their .config remains the same.

## Side Effects:
    - In-memory mutation: updates .config.title for matching reports.
    - No file, network, stdout/stderr, database, or other external side effects.

## Edge cases and notes:
    - Non-string titles: if .config.title is not equal to the exact string "Pandas Profiling Report" (including being None or another type), it will be left unchanged.
    - Large lists: chr(65 + i) yields single ASCII characters. For i >= 26 this produces characters beyond 'Z' (e.g., index 26 -> '['). If you must support more than 26 reports, provide custom titles beforehand or apply a different naming scheme (for example, numeric suffixes or multi-letter sequences).
    - The function performs no validation nor normalization beyond the exact equality check to the literal default string.

## Control Flow:
flowchart TD
    Start --> ForEach[Enumerate reports: for idx, report in enumerate(reports)]
    ForEach --> Check{report.config.title == "Pandas Profiling Report"?}
    Check -- Yes --> Assign[report.config.title = "Dataset " + chr(65 + idx)]
    Check -- No --> Continue[Do nothing]
    Assign --> Next[Index increment / next report]
    Continue --> Next
    Next --> ForEach
    ForEach --> End[Return None]

## Examples:
- Usage scenario (described as steps):
    1. Collect or construct a list of ProfileReport objects to be compared or displayed together.
    2. Ensure any manually assigned titles are already set on report.config.title for reports you want to keep unchanged.
    3. Call this helper with the list of reports.
    4. After the call, every report that previously had the exact title "Pandas Profiling Report" will have been renamed to "Dataset A", "Dataset B", etc., based on its position in the list.
    5. Proceed to render, export, or merge the reports; titles are now distinct and human-readable.

- Error-handling guidance:
    - If you may receive inputs that are not ProfileReport instances, validate or filter the list first:
        * For each element, confirm hasattr(element, "config") and hasattr(element.config, "title") before calling.
    - If you expect to produce more than 26 dataset labels, replace or extend the naming logic before calling to avoid non-alphabet characters.

## `src.ydata_profiling.compare_reports._compare_title` · *function*

## Summary:
Return a user-facing title for a comparison report: if all provided titles are identical return that title; otherwise return an HTML-formatted phrase listing the compared titles.

## Description:
This helper produces the header/title shown when multiple profile reports are compared. It centralizes the presentation rule so callers building comparison reports do not need to duplicate string-assembly logic.

Known callers within the provided snapshot:
    - No direct callers were discovered in the provided code snapshot. In practice this function is intended to be used by functions in the compare_reports module that assemble comparison report metadata and headers.

Why this logic is extracted:
    - Keeps presentation formatting separate from comparison logic. This makes the formatting easy to change or test independently (for example, adjusting punctuation or HTML tags) without touching the comparison algorithms.

## Args:
    titles (List[str]):
        - A non-empty list (or sequence) of strings representing report display names.
        - Required: len(titles) >= 1.
        - Element constraints: every element must be a str. The implementation uses equality checks and string joining; non-str elements will violate these assumptions and may cause runtime errors.
        - Order matters: the last element is treated as the final item in the human-readable "A, B and C" construction.

## Returns:
    str:
        - If every element in titles compares equal to titles[0] (all-equal), returns that string exactly (no HTML).
        - Otherwise, returns an HTML-formatted phrase:
          "<em>Comparing</em> {item1, item2, ..., itemN-1} <em>and</em> {itemN}"
          where {item1...itemN-1} is the comma-separated concatenation of all items except the last, and {itemN} is the last item.
        - Guarantee: the function always returns a Python str when preconditions are met.

## Raises:
    IndexError:
        - If titles is an empty sequence, the function accesses titles[0] and raises IndexError.

## Constraints:
    Preconditions:
        - titles is a sequence supporting indexing and slicing (e.g., list, tuple).
        - titles contains at least one element.
        - All elements are strings.

    Postconditions:
        - The returned value is a string suitable for placing into an HTML report header (it may contain <em> tags).
        - The input sequence is not mutated.

## Side Effects:
    - None. Pure function: no I/O, no network calls, and no global state modification.

## Control Flow:
flowchart TD
    A[Start: receive titles (sequence)] --> B{Is titles empty?}
    B -- Yes --> C[IndexError raised (titles[0] access)]
    B -- No --> D{Do all titles equal titles[0]?}
    D -- Yes --> E[Return titles[0] (plain string)]
    D -- No --> F[Build prefix = ", ".join(titles[:-1])]
    F --> G[Return "<em>Comparing</em> {prefix} <em>and</em> {titles[-1]}"]
    E --> H[End]
    G --> H[End]
    C --> H[End]

## Examples:
    - All titles identical:
        Input: ["Monthly report", "Monthly report", "Monthly report"]
        Output: "Monthly report"
        Rationale: all-equal branch returns the canonical title without HTML.

    - Distinct titles (three items):
        Input: ["Report A", "Report B", "Report C"]
        Output: "<em>Comparing</em> Report A, Report B <em>and</em> Report C"
        Rationale: lists first N-1 items separated by commas, appends the last after "and".

    - Two distinct titles:
        Input: ["Left", "Right"]
        Output: "<em>Comparing</em> Left <em>and</em> Right"
        Rationale: prefix becomes the first item only, formatting still applies.

    - Single-element list:
        Input: ["Solo"]
        Output: "Solo"
        Rationale: treated as all-equal; returns the single title.

    - Empty list:
        Input: []
        Outcome: IndexError is raised by accessing titles[0]; callers should validate non-emptiness before calling.

Notes:
    - The function hard-codes English literals ("Comparing" and "and") and minimal HTML (<em> tags). If consumers require plain-text or localized output, they should post-process the returned string.
    - Avoid passing non-string elements since the join operation assumes string elements.

## `src.ydata_profiling.compare_reports._compare_profile_report_preprocess` · *function*

## Summary:
Prepare multiple ProfileReport objects for side-by-side comparison by extracting their titles (labels), aligning visual/style settings (primary colors and typeset) where appropriate, and returning a list of report labels together with their BaseDescription objects.

## Description:
This function accepts a list of ProfileReport instances and an optional Settings object, performs in-place adjustments on each ProfileReport to make their visual presentation and typesetting compatible for comparison, and then retrieves each report's description (BaseDescription). It sets each returned description's title to the corresponding report title.

Known callers within the provided codebase:
- No direct callers are present in the provided snippet. Typically this helper is invoked by higher-level "compare reports" orchestration code (functions that compute diffs or generate comparison HTML) that take multiple ProfileReport objects and produce a comparative view.

Why this logic is extracted:
- This function encapsulates the preprocessing responsibilities required before comparing reports: harmonizing style (primary colors), forcing a shared typeset, extracting descriptions, and labeling them. Extracting these steps into a helper keeps higher-level comparison code focused on computing differences and rendering comparisons rather than dealing with per-report configuration mutations and title propagation.

## Args:
    reports (List[ProfileReport]):
        - A non-empty list of ProfileReport instances to be compared.
        - Required attributes accessed on each ProfileReport:
            * report.config.title (str)
            * report.config.html.style.primary_colors (list-like)
            * report.get_description() -> BaseDescription
            * report.typeset (used as a source for subsequent reports' _typeset)
        - The list is mutated in-place (see Side Effects).

    config (Optional[Settings], default=None):
        - If provided, must have config.html.style.primary_colors accessible.
        - If omitted (None), the function uses per-report config values to adjust colors.

    Interdependencies:
        - The function requires at least one report in reports because it reads reports[0] in multiple places.
        - Behavior of colors depends on the length of primary_colors either on reports[0] (when config is None) or on the provided config.

## Returns:
    Tuple[List[str], List[BaseDescription]]:
        - labels: list of strings, one per report, containing report.config.title in the same order as the input reports.
        - descriptions: list of BaseDescription objects returned by report.get_description() for each report in the same order.
            * For each returned description, the function sets description.analysis.title = corresponding label (mutates description objects).
        - Edge cases:
            * If reports is empty, the function does not handle it and will raise an IndexError (see Raises).
            * The function always returns labels and descriptions in matching order.

## Raises:
    IndexError:
        - Triggered if reports is an empty list (the function accesses reports[0] and iterates reports[1:]).

    AttributeError (or similar):
        - May be raised if a ProfileReport instance does not have the expected attributes (e.g., config, config.html.style.primary_colors, get_description, typeset).
        - May be raised if the provided config is not a Settings-like object with html.style.primary_colors.

## Constraints:
    Preconditions:
        - reports must contain at least one ProfileReport.
        - Each ProfileReport must expose config and get_description() as described above.
        - If config is provided, it must expose html.style.primary_colors.

    Postconditions:
        - The input reports list is unchanged in ordering.
        - report.config.html.style.primary_colors may be changed on each report (see Side Effects).
        - All reports from index 1 onward have their _typeset attribute set to reports[0].typeset.
        - Returned descriptions have their description.analysis.title set to the corresponding report title.

## Side Effects:
    - Mutates each ProfileReport in reports:
        * May replace report.config.html.style.primary_colors for each report.
            - If config is None and the first report's primary_colors length is > 1:
                The function replaces each report.config.html.style.primary_colors with a single-element list containing the color at the report's index from that report's original primary_colors list.
            - If config is provided and config.html.style.primary_colors length is > 1:
                The function sets each report.config.html.style.primary_colors to config.html.style.primary_colors (the entire list) — i.e., all reports receive the same primary_colors list from the provided config.
        * Sets report._typeset = reports[0].typeset for every report after the first (reports[1:]).
    - Mutates returned description objects by setting description.analysis.title to the report label.
    - No I/O (file, network, stdout) is performed.
    - No global state, database, or external cache modifications happen beyond the passed-in report objects and the returned descriptions.

## Control Flow:
flowchart TD
    A[Start: receive reports, optional config] --> B{reports is empty?}
    B -- Yes --> C[Raise IndexError (access reports[0])] 
    B -- No --> D[Build labels = [report.config.title for report in reports]]
    D --> E{config is None?}
    E -- Yes --> F{len(reports[0].config.html.style.primary_colors) > 1?}
    E -- No --> G{len(config.html.style.primary_colors) > 1?}
    F -- Yes --> H[For each idx,report: set report.config.html.style.primary_colors = [original_colors[idx]]]
    F -- No --> I[Do not change per-report primary_colors]
    G -- Yes --> J[For each idx,report: set report.config.html.style.primary_colors = config.html.style.primary_colors]
    G -- No --> K[Do not change primary_colors from config]
    H --> L[Set report._typeset for reports[1:] to reports[0].typeset]
    J --> L
    I --> L
    K --> L
    L --> M[descriptions = [report.get_description() for report in reports]]
    M --> N[For each label,description: set description.analysis.title = label]
    N --> O[Return labels, descriptions]
    C --> O

## Examples:
Example 1 — Typical happy path
    - Given two ProfileReport instances report_a and report_b with valid config.title and get_description:
        labels, descriptions = _compare_profile_report_preprocess([report_a, report_b])
      After the call:
        * labels == [report_a.config.title, report_b.config.title]
        * descriptions is a list of two BaseDescription objects whose analysis.title values equal those labels.
        * report_b._typeset == report_a.typeset

Example 2 — Handling missing reports (error handling)
    try:
        labels, descriptions = _compare_profile_report_preprocess([])
    except IndexError:
        # The function requires at least one ProfileReport; handle as appropriate
        handle_empty_reports_case()

Notes:
    - This helper intentionally mutates the passed ProfileReport objects' visual settings and typeset to ensure consistent rendering during comparison. Callers that must preserve original per-report settings should pass deep copies of ProfileReport instances (or their config objects) before calling this function.

## `src.ydata_profiling.compare_reports._compare_dataset_description_preprocess` · *function*

## Summary:
Extracts the title strings from a list of dataset description objects and returns the titles together with the original reports list.

## Description:
This private helper (indicated by the leading underscore) is an internal utility intended for use inside the compare_reports module to prepare label text for display or for mapping results back to the original dataset descriptions. It traverses the provided reports and collects the value found at report.analysis.title into a labels list while returning the original reports list unchanged.

Known callers:
- Intended for internal use by dataset-comparison routines within the compare_reports module. A repository-wide scan did not reveal direct external callers; it is a small preprocessing step typically invoked immediately before comparison, alignment, or visualization code that requires both a list of display labels and the original report objects.

Why this is extracted:
- Keeps comparison code focused on alignment/diffing logic by centralizing label extraction.
- Encapsulates the mapping from a BaseDescription to its display label so changes to how titles are obtained need to be made in only one place.
- Simplifies testing of label extraction behavior independently from comparison routines.

## Args:
    reports (List[BaseDescription]):
        - A list (possibly empty) of dataset description objects that are expected to expose an attribute path report.analysis.title.
        - Type: list-like container of BaseDescription instances or objects with the same shape.
        - Allowed values: any list. An empty list is valid and will produce an empty labels list.
        - Interdependencies: None between elements; each element is handled independently.
        - Expectation: Each report.analysis.title is expected to be a string (str). If elements produce non-string values, those values are returned as-is (see Returns and Raises).

## Returns:
    Tuple[List[str], List[BaseDescription]]:
        - labels: list[str] — a list containing the title value taken from report.analysis.title for each corresponding report.
            * The function returns the title values exactly as read. The function's type annotation signals List[str]; callers should ensure titles are strings. If a title is not a string (e.g., None or another type), that value will appear in the labels list unchanged and may therefore violate the hinted type.
            * If reports is empty, labels is an empty list.
        - reports: List[BaseDescription] — the exact same list object passed in, returned unmodified (same order and same element identities).
        - Alignment guarantee: len(labels) == len(reports) and labels[i] corresponds to reports[i].

## Raises:
    - The function does not explicitly raise custom exceptions.
    - Implicit exceptions that may propagate:
        * AttributeError: If an element in reports lacks an analysis attribute, or if analysis lacks a title attribute, attribute access will raise AttributeError.
        * Any exception raised by evaluating report.analysis.title (for example, property accessors that raise).
    - Recommendation: If input data may be malformed, callers should validate reports or handle exceptions (e.g., try/except AttributeError) before or around this helper.

## Constraints:
    Preconditions:
        - Caller should pass a list-like object whose elements provide report.analysis.title.
        - If strict typing is required, ensure each report.analysis.title is a str before calling.

    Postconditions:
        - The returned labels list has the same length and order as the input reports list.
        - The returned reports value is the same list object (identity preserved) that was passed in; no deep or shallow copy is made by this function.
        - No mutation of report objects is performed by this function.

## Side Effects:
    - None: no I/O, no network calls, no global state mutation.
    - The function only reads attributes and returns data. It does not copy or modify the report objects or the input list.

## Control Flow:
flowchart TD
    Start --> IsEmpty{"reports empty?"}
    IsEmpty -- Yes --> ReturnEmpty["return ([], reports) // labels empty"]
    IsEmpty -- No --> ForEach["iterate reports: read report.analysis.title"]
    ForEach --> Append["append title value to labels"]
    Append --> DoneIteration["after all reports processed"]
    DoneIteration --> Return["return (labels, reports)"]
    Return --> End

## Examples:
- Successful case (described):
    - Input: reports is a list of three BaseDescription-like objects where their analysis.title values are "A", "B", "C".
    - Output: (["A", "B", "C"], reports) — labels list aligns with the original reports list.

- Empty input:
    - Input: reports = []
    - Output: ([], []) — both labels and reports are empty lists.

- Non-string title values:
    - If a report has analysis.title == None or analysis.title == 123, the returned labels list will contain None or 123 at the corresponding index. Because the function does not coerce values to strings, callers that require strings should validate or convert titles beforehand.

- Error handling (described):
    - If a report lacks an analysis attribute, calling this helper will raise AttributeError. Example strategy for robust callers: wrap the call in try/except AttributeError to detect malformed inputs and handle them (e.g., skip, supply a default label, or surface a clearer error).

## `src.ydata_profiling.compare_reports.validate_reports` · *function*

## Summary:
Validate that a pair (or list) of profiling reports and their configurations are compatible for comparison; raises clear errors for invalid inputs and emits warnings for non-fatal but noteworthy situations.

## Description:
Performs pre-comparison checks to ensure inputs are suitable for side-by-side comparison. Concretely it:
- Requires at least two report objects and warns if more than two are supplied.
- Verifies that all config objects uniformly indicate either timeseries or tabular reports (no mixing).
- When ProfileReport instances are supplied, ensures every report has an initialized DataFrame (.df is not None).
- Compares feature sets (column names or variable keys) and warns when they differ.

Known callers and context:
- Comparison routines and utilities that combine, diff, or render two profiling results call this function at the start of their pipeline to reject incompatible inputs early.
- Typically invoked immediately after constructing ProfileReport or BaseDescription objects and after preparing their corresponding configuration objects.

Why this logic is extracted:
- Centralizes validation rules used by multiple comparison implementations so the core comparison logic can assume validated inputs and consistent error/warning messages.

## Args:
    reports (Union[List[ProfileReport], List[BaseDescription]]):
        List of report-like objects to be compared.
        - The runtime type of elements is expected to be homogeneous across the list.
        - If elements are ProfileReport instances, each should have a non-None .df attribute (a pandas-like DataFrame).
        - If elements are BaseDescription-like, each should expose a .variables mapping (with .keys()).
        - Minimum length: 2.

    configs (List[dict]):
        Sequence of configuration-like objects. Although annotated List[dict], the code accesses c.vars.timeseries.active on each element; therefore each config should be an object (for example, a Settings instance) exposing vars.timeseries.active as a boolean. The function does not verify len(configs) == len(reports); however, configs should align with reports in practice.

Notes on interdependencies:
- The function uses the first report's runtime type to decide how to inspect all entries; passing mixed-type reports (e.g., some ProfileReport and some BaseDescription) is unsupported and may cause attribute errors.

## Returns:
    None

A successful return (no exception) means the basic compatibility checks passed. Non-fatal issues are reported with warnings but do not prevent return.

## Raises:
    ValueError("At least two reports are required for this comparison")
        When len(reports) < 2.

    ValueError("Comparison between timeseries and tabular reports is not supported.")
        When configs indicate mixed report types: some configs have vars.timeseries.active == True and others False. The condition checked is all(report_types) != any(report_types).

    ValueError("Reports where not initialized with a DataFrame.")
        When the reports are ProfileReport instances (determined by isinstance(reports[0], ProfileReport)) and at least one report has r.df is None.

    AttributeError
        May be raised if reports or configs do not expose the attributes the function expects:
        - If reports contain mixed runtime types so that an accessed attribute (.df or .variables) is missing on some elements.
        - If a config object does not expose the vars.timeseries.active chain.
        This is not explicitly raised by the function but can occur due to attribute access on unexpected types.

## Constraints:
Preconditions:
    - reports must be a sequence with at least two elements.
    - All elements in reports should be of the same runtime type (either all ProfileReport or all BaseDescription-like).
    - configs must be a sequence of objects with vars.timeseries.active booleans. For sensible validation, configs should correspond to reports (one config per report).

Postconditions:
    - If the function returns normally:
        * The configs (as inspected) consistently indicate either timeseries or non-timeseries reports.
        * If ProfileReport instances were provided, each has a non-None .df.
        * The caller may have been alerted via warnings about >2 reports and/or differing feature sets.

## Side Effects:
    - Emits warnings via the warnings module for:
        * Providing more than two reports.
        * Reports describing different feature sets.
    - No file, network, or stdout I/O.
    - No mutation of global state, databases, or external services.

## Control Flow:
flowchart TD
    Start([Start validate_reports])
    A{len(reports) < 2?}
    B[Raise ValueError: At least two reports required]
    C{len(reports) > 2?}
    D[Warn: Comparison of more than two reports not supported]
    E[report_types = [c.vars.timeseries.active for c in configs]]
    F{all(report_types) != any(report_types)?}
    G[Raise ValueError: timeseries vs tabular mixed]
    H{isinstance(reports[0], ProfileReport)?}
    I[is_df_available = [r.df is not None for r in reports]]
    J{not all(is_df_available)?}
    K[Raise ValueError: Reports where not initialized with a DataFrame]
    L[features = sets of columns or variable keys from reports]
    M{not all(features equal)?}
    N[Warn: Datasets have a different set of columns]
    End([Return None])

    Start --> A
    A -- True --> B
    A -- False --> C
    C -- True --> D --> E
    C -- False --> E
    E --> F
    F -- True --> G
    F -- False --> H
    H -- True --> I
    I --> J
    J -- True --> K
    J -- False --> L
    H -- False --> L
    L --> M
    M -- True --> N --> End
    M -- False --> End

## Examples (realistic usage patterns and error handling):
- Valid comparison (both ProfileReport):
    Two ProfileReport objects are fully initialized with DataFrames (r.df is a pandas DataFrame) and two corresponding config objects both have vars.timeseries.active == False. Calling validate_reports(reports, configs) returns None and comparison can proceed.

- Timeseries mismatch (error case):
    If configs evaluate to [True, False] for vars.timeseries.active, validate_reports raises ValueError("Comparison between timeseries and tabular reports is not supported.") to prevent combining incompatible report types.

- Missing DataFrame (error case):
    If reports are ProfileReport instances but any r.df is None, validate_reports raises ValueError("Reports where not initialized with a DataFrame.") indicating initialization is incomplete.

- Mixed report runtime types (potential AttributeError):
    If reports = [ProfileReport(...), BaseDescription(...)] and the first element is ProfileReport, validate_reports will attempt to access .df on every element; the BaseDescription element may not have .df and Python will raise AttributeError. To avoid this, ensure reports are homogeneous before calling.

Notes:
- Although the function's signature annotates configs as List[dict], the implementation expects objects with an attribute chain vars.timeseries.active; pass Settings-like objects or equivalent, not plain dicts.
- The function does not check len(configs) == len(reports); callers should ensure configurations align with their reports.

## `src.ydata_profiling.compare_reports._apply_config` · *function*

## Summary:
Prune or clear sections of a BaseDescription in-place according to a Settings instance, and return the same (mutated) BaseDescription.

## Description:
This function applies Settings-driven visibility rules to a BaseDescription by removing or replacing parts that the configuration disables. It transforms the following attributes on the provided description: missing, correlations, sample, duplicates, and scatter. The function performs in-place mutations and returns the same description instance.

Notes on exact behavior:
- The function directly indexes config.missing_diagrams with keys from description.missing; missing keys will raise KeyError.
- Correlation filtering uses config.correlations.get(k, Correlation(calculate=False).calculate) and tests the returned value for truthiness. The explicit default used in the code is Correlation(calculate=False).calculate (the .calculate attribute of a Correlation instance created with calculate=False).

## Args:
    description (BaseDescription)
        - A mutable description object representing profiling results for a variable.
        - Required attributes (must be present and of compatible types):
            * missing: dict-like; iterated via description.missing.items()
            * correlations: dict-like; iterated via description.correlations.items()
            * sample: list-like; will be replaced with [] in some cases
            * duplicates: any type; may be set to None
            * scatter: dict-like; may be set to {}
        - The object is modified in-place and the same instance is returned.

    config (Settings)
        - Configuration object controlling retention of sections. Required members and expectations:
            * missing_diagrams: mapping supporting __getitem__ with keys matching description.missing keys; values are boolean-like (True to keep).
            * correlations: mapping supporting get(key, default). Values may be booleans or objects; the returned value's truthiness decides retention. The default used by the function is Correlation(calculate=False).calculate (False).
            * samples: object with numeric attributes head, tail, random. These are compared against 0.
            * duplicates: object with numeric attribute head. Compared against 0.
            * interactions: object with boolean attribute continuous.
        - Interdependencies:
            * Keys in description.missing must be present in config.missing_diagrams to avoid KeyError.
            * Numeric sample and duplicates attributes must be comparable to zero.

## Returns:
    BaseDescription
        - The same description instance passed in, after in-place modification.
        - Resulting transformations:
            * description.missing becomes a dict containing only entries where config.missing_diagrams[k] is truthy.
            * description.correlations becomes a dict containing only entries where bool(config.correlations.get(k, Correlation(calculate=False).calculate)) is True.
            * description.sample remains unchanged if any of config.samples.head, config.samples.tail, config.samples.random > 0; otherwise it is set to [].
            * description.duplicates remains unchanged if config.duplicates.head > 0; otherwise it is set to None.
            * description.scatter remains unchanged if config.interactions.continuous is truthy; otherwise it is set to {}.

## Raises:
    KeyError
        - If a key k from description.missing is not present in config.missing_diagrams, since the code uses config.missing_diagrams[k].

    AttributeError
        - If expected attributes are missing on description or config (e.g., description.missing, config.samples.head, config.interactions.continuous).

    TypeError (or other comparison-related exceptions)
        - If numeric comparisons (s > 0 or config.duplicates.head > 0) are attempted on values that do not support comparison with 0 (e.g., None or incompatible types).

## Constraints:
Preconditions:
    - description must expose the attributes listed above and those attributes must be of the expected container/primitive types.
    - config must expose missing_diagrams, correlations, samples, duplicates, and interactions with the attribute shapes and semantics described.
    - All keys in description.missing should exist in config.missing_diagrams to avoid KeyError.

Postconditions:
    - After return, description has been pruned according to config:
        * No missing entries whose corresponding config.missing_diagrams[k] is falsy remain.
        * No correlation entries whose config.correlations.get(k, Correlation(calculate=False).calculate) is falsy remain.
        * description.sample is [] exactly when all of config.samples.head, config.samples.tail, config.samples.random are <= 0.
        * description.duplicates is None exactly when config.duplicates.head <= 0.
        * description.scatter is {} exactly when bool(config.interactions.continuous) is False.

## Side Effects:
    - Mutates the passed BaseDescription instance in memory (no copy is produced).
    - No I/O (files, network) and no global state mutation.

## Control Flow:
flowchart TD
    Start[Start: receive description, config] --> FilterMissing[Filter description.missing by config.missing_diagrams[k]]
    FilterMissing --> FilterCorrelations[Filter description.correlations by config.correlations.get(k, Correlation(calculate=False).calculate)]
    FilterCorrelations --> CollectSamples[Collect samples = [config.samples.head, config.samples.tail, config.samples.random]]
    CollectSamples --> AnyPos{Any sample > 0?}
    AnyPos -->|Yes| KeepSample[Keep description.sample as-is]
    AnyPos -->|No| ClearSample[Set description.sample = []]
    KeepSample --> DupCheck
    ClearSample --> DupCheck
    DupCheck{config.duplicates.head > 0?} -->|Yes| KeepDup[Keep description.duplicates]
    DupCheck -->|No| ClearDup[Set description.duplicates = None]
    KeepDup --> InteractionCheck
    ClearDup --> InteractionCheck
    InteractionCheck{bool(config.interactions.continuous)?} -->|True| KeepScatter[Keep description.scatter]
    InteractionCheck -->|False| ClearScatter[Set description.scatter = {}]
    KeepScatter --> Return[Return description]
    ClearScatter --> Return

## Examples:
(Conceptual transformations — these are descriptions of input→output state changes; constructing real BaseDescription and Settings objects is required in real code.)

1) Keep/Drop missing entries:
    - Input: description.missing = {'x': m1, 'y': m2}
      config.missing_diagrams = {'x': True, 'y': False}
    - Output: description.missing -> {'x': m1}

2) Correlation retention with explicit default:
    - The function uses config.correlations.get('pearson', Correlation(calculate=False).calculate).
      Since Correlation(calculate=False).calculate is False, an absent key defaults to False (dropped).
    - If config.correlations['pearson'] is True, the 'pearson' entry is kept.

3) Sample/duplicates/scatter behavior:
    - If config.samples.head = config.samples.tail = config.samples.random = 0 then description.sample -> [].
    - If config.duplicates.head = 0 (or negative) then description.duplicates -> None.
    - If config.interactions.continuous is falsy then description.scatter -> {}.

4) Defensive usage recommendation:
    - Validate that all keys in description.missing exist in config.missing_diagrams, and that config.samples.* and config.duplicates.head are numeric, before calling this function to avoid KeyError / TypeError.

## `src.ydata_profiling.compare_reports._is_alert_present` · *function*

## Summary:
Checks whether an alert with the same column name and alert type exists in a list of alerts and returns True if at least one match is found; otherwise returns False.

## Description:
This small predicate is intended for use when comparing or merging alert collections (for example, when comparing two profile reports and deciding whether an alert from one report is already present in another). It encapsulates the matching rule: two alerts are considered the same when both their column_name and alert_type attributes are equal.

Known callers within the codebase:
- No direct callers were discovered by the inspection step provided. Conceptually, this function is used inside report comparison logic (compare_reports module) to determine whether an Alert from one list should be considered duplicate/present in another list before adding or reporting it.

Why this is extracted:
- The equality/matching policy (column_name + alert_type) is a single, well-defined responsibility and is used in multiple places during report comparison. Extracting it:
  - Centralizes the matching rule so it can be changed in one place.
  - Improves readability of higher-level comparison code.
  - Makes unit-testing the matching behavior straightforward.

## Args:
    alert (Alert):
        - Type: ydata_profiling.model.alerts.Alert (or any object exposing attributes `column_name` and `alert_type`)
        - Required. The alert to search for in alert_list.
        - Interdependencies: both alert.column_name and alert.alert_type are read and compared; their values may be None and will be compared using normal equality semantics.
    alert_list (list):
        - Type: iterable/list of Alert-like objects (each must expose `column_name` and `alert_type` attributes)
        - Required. The collection to search.
        - Allowed values: any iterable. Empty iterable is allowed and results in False.
        - Interdependencies: elements are expected to be objects (not primitive dicts unless attribute access is supported) with attributes used in comparisons.

## Returns:
    bool:
        - True if at least one element `a` in alert_list satisfies:
            a.column_name == alert.column_name AND a.alert_type == alert.alert_type
        - False if no such element exists (including when alert_list is empty).
        - Edge cases:
            * If multiple matching elements exist, still returns True.
            * If alert.column_name or alert.alert_type is None, comparison uses normal None equality semantics.
            * If alert_list contains elements with matching attribute values but of different types, Python's equality rules apply.

## Raises:
    AttributeError:
        - If `alert` or an element `a` in `alert_list` does not have attribute `column_name` or `alert_type`, attempting to access those attributes will raise AttributeError.
    TypeError:
        - If `alert_list` is not an iterable, calling the membership/iteration will raise TypeError.
    Note: The function performs no explicit exception handling; errors from attribute access or iteration propagate to the caller.

## Constraints:
    Preconditions:
        - `alert` must be a non-None object exposing attributes `column_name` and `alert_type`.
        - `alert_list` must be an iterable of objects exposing `column_name` and `alert_type`.
    Postconditions:
        - No mutation of `alert` or `alert_list` occurs.
        - The function returns a boolean and does not have side effects.
        - The original order and contents of alert_list remain unchanged.

## Side Effects:
    - None. The function does not perform I/O, network calls, global state mutations, or modify the provided inputs.

## Control Flow:
flowchart TD
    Start[Start] --> CheckIterable{Is alert_list iterable?}
    CheckIterable -- No --> TypeError["Raise TypeError on iteration"]
    CheckIterable -- Yes --> Iterate[Iterate over elements a in alert_list]
    Iterate --> HasAttrA{Does element a have column_name and alert_type?}
    HasAttrA -- No --> AttributeError["Attribute access raises AttributeError"]
    HasAttrA -- Yes --> Compare{a.column_name == alert.column_name\nAND a.alert_type == alert.alert_type?}
    Compare -- Yes --> MatchFound[Return True]
    Compare -- No --> Continue[Continue iteration]
    Continue --> Iterate
    Iterate --> Exhausted{All elements checked?}
    Exhausted -- Yes --> NoMatch[Return False]

## Examples:
- Typical usage scenario: during a comparison of two profile reports, for each alert from report A, call this predicate with that alert and the list of alerts from report B to decide whether the alert from A is already reported in B. If the function returns True, skip adding or reporting the duplicate; if False, consider it a newly observed alert.

- Edge case examples (described in words):
    * If alert_list is empty, the function yields False (nothing to match).
    * If alert has column_name equal to "age" and alert_type equal to "missing_values", and alert_list contains at least one alert object with column_name "age" and alert_type "missing_values", the function yields True.
    * If an element in alert_list is a plain dict (no attribute access), calling this function will raise AttributeError when the code attempts to access a.column_name.

Implementation notes (for reimplementation):
- Use a short, efficient membership test: iterate over alert_list and for each element `a`, check the two attribute-equality conditions; return True immediately on the first match, otherwise return False after iteration.
- Complexity: O(n) time where n is len(alert_list), O(1) extra memory.

## `src.ydata_profiling.compare_reports._create_placehoder_alerts` · *function*

## Summary:
Produce aligned alert lists for multiple reports by inserting placeholder copies (marked empty) for alerts that appear in some reports but are missing in others, returning a tuple of per-report alert lists with placeholders ensuring every alert from any report appears (as real or placeholder) in every report's list.

## Description:
This function is used during comparison/merging of alerts across multiple profile reports. Typical callers are higher-level routines in the compare_reports module that need to produce a combined view of alerts from several ProfileReport objects so that alerts can be displayed or compared side-by-side across reports.

Why this is a separate function:
- It encapsulates the single responsibility of aligning alert collections across reports by inserting placeholder alerts where necessary.
- Centralizing the placeholder-creation logic keeps comparison code concise and makes the matching, copying, and placeholder-marking semantics easy to test and modify independently.

Known callers / invocation context:
- compare_reports workflows that build side-by-side comparisons of alerts from two or more reports (e.g., when generating a diff or unified display of alerts across ProfileReport instances).
- It is typically invoked after each report's alerts have been collected into per-report lists (one list per report) and before any presentation or aggregation step that assumes each per-report list contains the union of all alerts (either as real alerts or placeholders).

## Args:
    report_alerts (tuple of iterables of Alert-like objects):
        - Type: tuple
        - Each element must be an iterable (commonly a list) containing Alert objects (instances of ydata_profiling.model.alerts.Alert) or objects exposing the same attributes used for comparison.
        - Allowed values: any length tuple (including zero-length). Any inner iterable may be empty.
        - Interdependencies: elements of the inner iterables are expected to be alert-like objects that can be shallow-copied and passed to the helper predicate _is_alert_present for membership testing. If the elements do not expose expected attributes, errors will propagate from those operations.

## Returns:
    tuple of list[Alert]:
        - The function returns a tuple whose length equals len(report_alerts). Each element is a list of Alert objects corresponding to that report.
        - For each input report index i:
            * All original Alert objects from report_alerts[i] are included (in the order they are iterated) in the returned list at position i.
            * For every alert present in any other report j (j != i) that is not considered present in report i according to _is_alert_present, a placeholder Alert is appended to the returned list for index i. Each placeholder is a shallow copy of the originating alert with its _is_empty attribute set to True.
        - Edge cases:
            * If report_alerts is empty, returns an empty tuple.
            * If some reports have no alerts (empty iterables), they will receive placeholder copies for alerts found in other reports.
            * If multiple alerts in other reports require placeholders to be inserted, placeholders are appended in the order those source alerts are encountered during the nested iteration.
        - Notes on object identity:
            * Original alerts are inserted as the same object references from the input iterables (no copy is made for alerts that already exist in a report).
            * Placeholders are shallow copies: object identity differs from the original alert, but mutable nested attributes (e.g., a dict in Alert.values) are shared by the shallow copy.

## Raises:
    - The function does not raise application-specific errors itself but allows exceptions from underlying operations to propagate:
        * TypeError if report_alerts is not iterable, or if an inner element is not iterable.
        * AttributeError or other exceptions raised by _is_alert_present when an alert-like object lacks expected attributes (column_name, alert_type).
        * Errors raised by copy.copy (e.g., if the alert object is not copyable) will propagate.
    - No explicit try/except blocks are present; callers should validate inputs or handle these exceptions if necessary.

## Constraints:
    Preconditions:
        - report_alerts must be a tuple where each element is an iterable of alert-like objects.
        - Alert-like objects must be shallow-copyable via copy.copy and must be compatible with _is_alert_present (i.e., expose column_name and alert_type attributes).
    Postconditions:
        - The returned tuple has the same number of entries as the input tuple.
        - For every alert object present in any input inner iterable, every returned inner list contains an alert object (either the original or a placeholder shallow copy) that will be considered matching by _is_alert_present for that alert's column_name and alert_type.
        - Original input iterables and their contained Alert objects are not modified by this function (placeholders are new objects; existing alerts are referenced but not mutated by this function).

## Side Effects:
    - In-memory allocations: constructs new Python lists and shallow-copied Alert objects for placeholders.
    - Mutations: sets the attribute _is_empty = True on each placeholder copy (this mutates the new placeholder object only).
    - No external I/O, network calls, file or database writes, global state modifications, or printing occur.

## Control Flow:
flowchart TD
    Start[Start] --> Init[Initialize fixed as list of empty lists, one per input report]
    Init --> OuterLoop[For each idx, alerts in enumerate(report_alerts)]
    OuterLoop --> ForEachAlert[For each alert in alerts]
    ForEachAlert --> AppendOriginal[Append alert to fixed[idx]]
    AppendOriginal --> InnerLoop[For each i, fix in enumerate(fixed)]
    InnerLoop --> IsSameIndex{Is i == idx?}
    IsSameIndex -- Yes --> SkipIndex[Continue to next i]
    IsSameIndex -- No --> CheckPresent{_is_alert_present(alert, report_alerts[i])?}
    CheckPresent -- True --> NoPlaceholder[Do not add placeholder]
    CheckPresent -- False --> MakeCopy[empty_alert = shallow copy(alert); set empty_alert._is_empty = True; append to fix]
    NoPlaceholder --> InnerLoop
    MakeCopy --> InnerLoop
    InnerLoop --> ForEachAlert
    ForEachAlert --> OuterLoop
    OuterLoop --> ReturnTuple[Return tuple(fixed)]
    ReturnTuple --> End[End]

## Examples:
1) Two-report alignment (conceptual example):
    - Inputs:
        * report_alerts[0] contains Alert A (column "age", type MISSING) and Alert B (column "income", type OUTLIER)
        * report_alerts[1] contains Alert A only
    - Behavior:
        * For report 0: original Alerts A and B are appended to fixed[0]; when iterating, no placeholders are needed for report 0 because it already contains A and B.
        * For report 1: when processing Alert B from report 0, _is_alert_present detects B is absent in report 1, so a shallow copy of B is created, its _is_empty flag set True, and it is appended to fixed[1].
    - Result:
        * Returned tuple has two lists:
            - Index 0: [A, B] (original objects)
            - Index 1: [A, B_placeholder] (A is original from report 1; B_placeholder is a shallow copy of B with _is_empty True)

2) Empty and multiple reports:
    - If report_alerts is ([], [C, D]):
        * Return: ([C_placeholder, D_placeholder], [C, D]) where placeholders are shallow copies with _is_empty True.
    - If report_alerts is empty tuple:
        * Return empty tuple.

Usage note:
- After calling this function, downstream code can iterate the returned per-report lists in parallel to present alerts side-by-side; checking the _is_empty attribute identifies placeholder entries that represent "missing" alerts for that report.

## `src.ydata_profiling.compare_reports.compare` · *function*

## Summary:
Compare multiple profiling reports or dataset descriptions and produce a single merged ProfileReport describing differences and combined analyses.

## Description:
- Known callers:
    - No internal callers are enumerated in this file. Typical usage is by library users or by higher-level utilities that need to compare multiple ProfileReport instances or summaries (BaseDescription objects) produced by the profiling pipeline.
- Purpose and responsibility:
    - Orchestrates comparison of multiple objects of the same type (either all ProfileReport or all BaseDescription).
    - Aligns features/variables across reports, applies/merges configuration(s), delegates preprocessing to specialized comparison helpers, merges the resulting descriptions, and returns a new ProfileReport with the combined BaseDescription set.
    - Extracted into its own function to encapsulate: validation of input homogeneity, feature alignment, configuration propagation, and the merge workflow — keeping higher-level code free from these orchestration details.

## Args:
    reports (Union[List[ProfileReport], List[BaseDescription]]):
        - A non-empty list containing either only ProfileReport objects or only BaseDescription objects (mixing types raises an error).
        - Each ProfileReport is expected to have an attribute df (a pandas DataFrame) and config.
        - Each BaseDescription is expected to implement the package/config structure used to reconstruct Settings (the function reads r.package["ydata_profiling_config"]).
        - Interdependencies: All items must be of the same runtime type. The function assumes the first element's schema/features form the base alignment.
    config (Optional[Settings], default=None):
        - If provided, used as the merged report's configuration (a copy is taken).
        - When provided and the inputs are ProfileReport objects, each report's config is replaced with a copy of this config, but the original report title and timeseries.active flag are preserved on each report.
    compute (bool, default=False):
        - Only applicable when config is provided and reports are ProfileReport: when True, the function clears each report's cached description (report._description_set = None) to force recomputation in later stages.
        - No effect for BaseDescription inputs.

## Returns:
    ProfileReport
    - A new ProfileReport instance whose _description_set is a BaseDescription representing the merged/compared description of the provided reports.
    - Possible edge-case returns:
        * If the input list contains only one report after aligning columns (ProfileReport branch) the function returns that remaining ProfileReport instance directly (no new merged report).
        * If the inputs are BaseDescription objects and no subsequent report shares any variables with the first description, the function constructs and returns a ProfileReport whose _description_set is the first BaseDescription (no merge).
    - Normal flow: combines all preprocessed descriptions into a dictionary, post-processes title/alerts/time_index_analysis, converts back to a BaseDescription and wraps into a new ProfileReport.

## Raises:
    ValueError:
        - Raised when the provided reports list is empty.
    TypeError:
        - Raised when the provided reports list contains multiple runtime types (e.g., mixing ProfileReport and BaseDescription).
        - The same TypeError is raised if the list is not homogeneously typed at the preprocessing decision point.
    Any exception raised by validate_reports:
        - The function calls validate_reports(reports=..., configs=...). Any exceptions produced by validate_reports (validation failures) propagate up unchanged.

## Constraints:
- Preconditions:
    - reports must be a non-empty list.
    - All items in reports must be of the same runtime type (all ProfileReport or all BaseDescription).
    - Each ProfileReport must expose df (pandas.DataFrame) and config attributes; each BaseDescription must expose variables and package["ydata_profiling_config"] for reconstructing Settings.
- Postconditions:
    - The returned object is a ProfileReport with _description_set set to a BaseDescription instance describing the merged comparison results.
    - If config was provided, the returned ProfileReport.config is a copy of that config with computed labels set (config is not the original passed object but a copy).
    - Input report objects MAY be mutated (see Side Effects) — callers should copy inputs if immutability is required.

## Side Effects:
- Mutations to objects passed in:
    - For ProfileReport inputs:
        * The function restricts each report.df to columns that exist in the base features (reports[0].df.columns) by assigning report.df = report.df.loc[:, cols_2_compare]; therefore the DataFrame object referenced by each ProfileReport is replaced with a sub-DataFrame view — this mutates the report objects passed in.
        * If a config argument is provided, each report.config is overwritten with a copy of the provided config (but the original title and timeseries.active flag are preserved).
        * If compute=True and config is provided, each report._description_set is set to None to force recomputation.
    - For BaseDescription inputs:
        * No in-place DataFrame mutation occurs, but no guarantees about immutability of BaseDescription objects held by callers (function reads and uses their attributes).
- I/O and external calls:
    - The function does not perform file or network I/O directly. It calls helper functions (validate_reports, preprocessing helpers, merging helpers) which may have their own side effects; those side effects are not performed by this function itself except by propagation.
- Global state:
    - The function writes merged label values into _config.html.style._labels before creating the final ProfileReport (this modifies the _config object used for the returned report).

## Control Flow:
flowchart TD
    Start --> CheckEmpty
    CheckEmpty{reports empty?}
    CheckEmpty -- Yes --> RaiseValueError
    CheckEmpty -- No --> CheckHomogeneousTypes
    CheckHomogeneousTypes{all same type?}
    CheckHomogeneousTypes -- No --> RaiseTypeError
    CheckHomogeneousTypes -- Yes --> BuildConfigs
    BuildConfigs --> validate_reports
    validate_reports --> IsProfileReport
    IsProfileReport{inputs are ProfileReport?}
    IsProfileReport -- Yes --> AlignProfileDataFrames
    AlignProfileDataFrames --> DropEmptyReports
    DropEmptyReports{only one report left?}
    DropEmptyReports -- Yes --> ReturnSingleReport
    DropEmptyReports -- No --> DetermineConfig
    IsProfileReport -- No --> BaseDescriptionBranch
    BaseDescriptionBranch --> DetermineOverlap
    DetermineOverlap{no overlap with first?}
    DetermineOverlap -- Yes --> ReturnProfileWithFirstDescription
    DetermineOverlap -- No --> DetermineConfig
    DetermineConfig --> ApplyConfigToReportsIfProvided
    ApplyConfigToReportsIfProvided --> PreprocessByType
    PreprocessByType --> SetLabelsInConfig
    SetLabelsInConfig --> CreatePlaceholders
    CreatePlaceholders --> ApplyConfigToDescriptions
    ApplyConfigToDescriptions --> MergeDescriptionsLoop
    MergeDescriptionsLoop --> PostProcessTitleAlertsTimeIndex
    PostProcessTitleAlertsTimeIndex --> BuildProfileReportFromDescription
    BuildProfileReportFromDescription --> ReturnMergedProfileReport
    RaiseValueError --> End
    RaiseTypeError --> End
    ReturnSingleReport --> End
    ReturnProfileWithFirstDescription --> End
    ReturnMergedProfileReport --> End

## Examples:
- Typical compare of two ProfileReport objects:
    report = compare([profile_report_a, profile_report_b])
    # returns either:
    #  - the single ProfileReport if only one non-empty overlapping set of columns remained
    #  - or a new ProfileReport whose _description_set is the merged BaseDescription

- Forcing recomputation of descriptions when supplying a new config:
    merged = compare([profile_a, profile_b], config=new_settings, compute=True)
    # Each input profile's cached description is cleared so later computations reflect the new config.

- Comparing serialized descriptions (BaseDescription objects):
    merged = compare([desc_a, desc_b])
    # If desc_b shares no variables with desc_a (after checking the first vs others), the function will return a ProfileReport wrapping desc_a.

Notes:
- This function is an orchestration wrapper. Many details (how descriptions are preprocessed, how merging occurs, how placeholders are expanded, and how alerts/time index analysis are computed) are delegated to helper functions called inside; to modify merging behavior you must change those helpers.
- Because the function mutates ProfileReport instances passed in (df and config), call with copies of reports when you need to preserve original objects.

