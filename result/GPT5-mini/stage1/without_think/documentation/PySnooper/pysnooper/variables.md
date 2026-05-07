# `variables.py`

## `pysnooper.variables.needs_parentheses` · *function*

## Summary:
Determines whether an expression fragment must be wrapped in parentheses so that an appended attribute access (".x") binds to the entire expression rather than to a sub-expression.

## Description:
This function inserts the provided expression fragment into two syntactic contexts — one unparenthesized ({}.x) and one parenthesized (({}).x) — compiles both contexts to bytecode, and returns whether the resulting bytecode differs. A True result means that the parenthesized and unparenthesized forms compile to different operations, implying parentheses are required to preserve the intended structure when adding attribute access.

Known callers and calling context:
- There are no explicit caller locations hard-coded in this snippet. Typical callers are formatting/pretty-printing utilities that build attribute-access strings from arbitrary expression fragments (for example, when generating a representation like "<expr>.attr" for display or tracing). These callers use this check to decide whether to wrap an expression in parentheses before appending ".attr".

Why this is a separate function:
- The logic encapsulates a small but subtle syntactic test (compile-and-compare bytecode) and isolates exception behavior. Making it a separate function keeps expression-formatting code concise and centralizes the rules for when parentheses are necessary, easing testing and maintenance.

## Args:
    source (str): An expression fragment to test (e.g., "a + b", "obj.method()", "a[0]"). The value will be interpolated into the patterns "{}.x" and "({}).x". Any object whose string representation is a valid expression fragment may be passed, but passing non-string objects relies on their __format__/__str__ behavior.

Notes on interdependencies:
- The function relies on Python's compile behavior; correctness depends on the formatted strings being valid single expressions under eval mode.

## Returns:
    bool: True if the compiled bytecode for "{}.x".format(source) differs from the compiled bytecode for "({}).x".format(source). Semantically:
        - True: Parentheses change how attribute access would be interpreted — parentheses are necessary to ensure the attribute access applies to the whole expression.
        - False: Parentheses do not change the compiled form for the attribute access and therefore are not required for correctness.

Edge-case returns:
- This function always returns a boolean on successful compilation of both forms. It does not return None or other types.

## Raises:
    SyntaxError:
        - If either constructed string is not a valid single expression in eval mode (e.g., source produces multiple statements or an invalid expression), compile will raise SyntaxError which is propagated to the caller.
    Any exception raised by formatting:
        - If formatting the strings using "{}.x".format(source) or "({}).x".format(source) triggers an exception (for example, if source's __format__ raises), that exception will propagate.
    TypeError:
        - If compile is given an unsupported type (unlikely here because formatting produces str), or if callers pass types incompatible with format(), TypeError may propagate.

The function does not catch or translate exceptions; callers should handle these errors if they expect untrusted input.

## Constraints:
Preconditions:
    - The caller should pass a value whose formatted string is intended to be a Python expression fragment.
    - The resulting formatted strings must be suitable for compile(..., mode='eval') — i.e., a single expression, not a block of statements.

Postconditions:
    - If the function returns True, then inserting the raw source into an attribute access position would produce different bytecode than wrapping the source in parentheses first. The caller can rely on this to decide whether to add parentheses.
    - If the function returns False, adding parentheses is unnecessary (for attribute-binding behavior).

## Side Effects:
    - None with respect to I/O or global state. The function only performs string formatting and uses compile to obtain code objects; it does not write files, perform network requests, or mutate global variables.

## Control Flow:
flowchart TD
    Start --> FormatUnparen["Format '{}.x'"]
    Start --> FormatParen["Format '({}).x'"]
    FormatUnparen --> CompileUnparen["compile(..., mode='eval') -> code1"]
    FormatParen --> CompileParen["compile(..., mode='eval') -> code2"]
    CompileUnparen --> GetBytes1["code1.co_code"]
    CompileParen --> GetBytes2["code2.co_code"]
    GetBytes1 --> Compare["Compare co_code bytes"]
    GetBytes2 --> Compare
    Compare --> Equal{"co_code equal?"}
    Equal -- Yes --> ReturnFalse["return False"]
    Equal -- No --> ReturnTrue["return True"]
    FormatUnparen -.-> Exception["format()/compile raises -> propagate"]
    FormatParen -.-> Exception
    CompileUnparen -.-> Exception
    CompileParen -.-> Exception

## Examples:
Typical usage:
- Basic cases:
    - needs_parentheses("a + b") -> True
      Reason: Without parentheses, "a + b.x" parses differently than "(a + b).x".
    - needs_parentheses("obj.attr") -> False
      Reason: "obj.attr.x" vs "(obj.attr).x" compile the same with respect to attribute binding.

- Handling invalid input:
    - If source is "a = 1\nb = 2" (a multi-statement string), both formatted strings will fail compile(..., mode='eval') and the call will raise SyntaxError. Callers should wrap calls in try/except when processing untrusted or arbitrary text:
        - try:
            needs_parentheses(user_input)
          except SyntaxError:
            handle_invalid_expression()

Practical guidance:
- Use this function when programmatically constructing attribute access or indexing forms from arbitrary expression fragments to avoid producing syntactically ambiguous or semantically incorrect output.

## `pysnooper.variables.BaseVariable` · *class*

## Summary:
Represents an abstract, inspectable variable specification: a compiled expression string plus metadata (excluded sub-names) and helpers to evaluate that expression in a Python frame and map the runtime value into one-or-more displayable (name, value) items. BaseVariable is an abstract base class intended to be subclassed to implement concrete item-extraction strategies.

## Description:
- Role:
    - Encapsulates a variable expression (source) that will be evaluated in a given Python frame and then inspected by a subclass to produce one or more (display_name, value) pairs for logging/tracing.
    - Centralizes safe evaluation (with an eval exception guard), normalization of exclude lists, and stable identity/hash behavior used by caches and sets.

- When to instantiate:
    - Do not instantiate BaseVariable directly because it declares an abstract method _items. Create a concrete subclass that implements _items(key, normalize=False) and instantiate that subclass.
    - Typical factories/callers: tracer code that transforms user-specified variable strings into Variable instances, test helpers, and configuration parsers.

- Responsibility and boundaries:
    - Responsibility: maintain compiled code and metadata, evaluate the expression in a frame, and delegate decomposition of the evaluated object to subclasses.
    - Boundary: BaseVariable does not implement traversal or decomposition logic — subclasses implement _items. It does not perform any I/O or logging itself.

## State:
- source (str)
    - Type: str
    - Meaning: Original expression text (e.g., "a", "obj.attr", "my_dict['k']").
    - Constraints: Must be a valid single Python expression for compile(..., mode='eval'); otherwise __init__ will raise SyntaxError/TypeError.

- exclude (tuple)
    - Type: tuple
    - Meaning: Sequence of names (strings) to omit from returned display names.
    - Default: () if not provided.
    - Construction: Normalized via utils.ensure_tuple(exclude) during __init__; generators are consumed and strings are treated as atomic scalars.
    - Invariant: Always a tuple after construction.

- code (code object)
    - Type: compiled-code object (from compile(source, '<variable>', 'eval'))
    - Meaning: Precompiled expression used by items() to eval in a frame.
    - Constraint: Created at construction; compile may raise SyntaxError/TypeError.

- unambiguous_source (str)
    - Type: str
    - Meaning: Either source or the parenthesized form '({})'.format(source) when needs_parentheses(source) returns True; used by subclasses to build canonical display names when normalize=True.

- Class invariant:
    - The fingerprint tuple (type(self), self.source, self.exclude) is the canonical identity used for equality and hashing.

## Public methods and signatures:
- __init__(self, source: str, exclude=())
    - Effect: Stores source, normalizes exclude to a tuple, compiles source into a code object, computes unambiguous_source.
    - Raises: SyntaxError or TypeError from compile(...) for invalid source; exceptions raised by utils.ensure_tuple (e.g., if iterating exclude fails) propagate.

- items(self, frame, normalize: bool = False) -> Iterable[tuple[str, Any]]
    - Effect: Evaluates the precompiled expression in the context of frame.f_globals (or {} if falsy) and frame.f_locals. If evaluation raises any Exception, returns the empty tuple (); otherwise calls and returns self._items(main_value, normalize).
    - Note: Exceptions raised by _items or by iterating a returned lazy iterable propagate to the caller.

- _items(self, key, normalize: bool = False) -> Iterable[tuple[str, Any]]  (abstract)
    - Requirement for subclasses: implement this method to map the evaluated value (key) to zero or more (display_name, value) pairs. display_name must be str.
    - Semantic: Should omit items whose names match any entry in self.exclude. If normalize is True, use canonical naming (e.g., self.unambiguous_source as the root).
    - Edge behavior: Implementations are encouraged to catch expected probing errors (AttributeError, KeyError, IndexError) and skip problematic subitems instead of raising.

- _fingerprint (property) -> tuple[type, Any, Any]
    - Returns the tuple (type(self), self.source, self.exclude). Used by __eq__ and __hash__.

- __hash__(self) -> int
    - Returns hash(self._fingerprint).
    - Raises: TypeError if any element of the fingerprint is unhashable (commonly if an exclude element is unhashable).

- __eq__(self, other) -> bool
    - Exact semantics: returns True iff isinstance(other, BaseVariable) is True and self._fingerprint == other._fingerprint. Otherwise returns False.

## Lifecycle:
- Creation:
    - Required args: source (str)
    - Optional: exclude (iterable or scalar)
    - Steps:
        1. self.source = source
        2. self.exclude = utils.ensure_tuple(exclude)
        3. self.code = compile(source, '<variable>', 'eval')  # may raise SyntaxError/TypeError
        4. self.unambiguous_source = '({})'.format(source) if needs_parentheses(source) else source
    - Note: Because _items is abstract, instantiating BaseVariable directly raises TypeError.

- Usage:
    - Typical order:
        1. Instantiate a concrete subclass that implements _items.
        2. For every traced frame, tracer calls instance.items(frame, normalize=False or True).
        3. Tracer consumes the returned iterable of (display_name, value) pairs and renders/logs them.
    - items(frame, ...) is reentrant and may be called many times for different frames.

- Destruction:
    - No special cleanup required. Instances are ordinary Python objects and are garbage-collected when no longer referenced.

## Method call flow (Mermaid-style flowchart):
flowchart LR
    Init[__init__(source, exclude)] --> NormalizeExclude["exclude = utils.ensure_tuple(exclude)"]
    NormalizeExclude --> CompileCode["code = compile(source, '<variable>', 'eval')"]
    CompileCode --> ComputeUnambiguous["unambiguous_source = parenthesize_if_needed(source)"]
    ComputeUnambiguous --> Ready["Concrete instance ready"]
    Ready --> ItemsCall[items(frame, normalize)]
    ItemsCall --> Eval["eval(self.code, frame.f_globals or {}, frame.f_locals)"]
    Eval -- Exception --> ReturnEmpty["return ()"]
    Eval -- Success --> ToItems["_items(main_value, normalize)"]
    ToItems --> ReturnItems["return iterable of (str, Any)"]
    _fingerprint --> Hash["__hash__ -> hash(_fingerprint)"]
    _fingerprint --> Eq["__eq__ -> isinstance + compare fingerprints"]

## Raises:
- __init__:
    - SyntaxError: if compile(source, '<variable>', 'eval') fails because source is not a valid single expression.
    - TypeError: if compile raises TypeError for an unsupported input type.
    - Any exception raised by utils.ensure_tuple (for example, an iterator that raises during iteration) will also propagate.
    - needs_parentheses uses compile internally; SyntaxError from it will propagate.

- items(frame, normalize=False):
    - None directly: eval exceptions are caught and converted to an empty-tuple return; items will not raise because of eval failures.
    - Exceptions raised by _items or by iterating a lazy returned iterable (AttributeError, KeyError, IndexError, TypeError, or user exceptions) will propagate to the caller.

- __hash__:
    - TypeError if any element in the fingerprint tuple is unhashable (for example, if exclude contains a list).

## Example (stepwise, prose):
1. Implement a concrete subclass:
    - Provide a class MyVariable(BaseVariable) that implements _items(self, key, normalize=False) returning an iterable of (display_name: str, value) pairs. Respect self.exclude and use self.unambiguous_source when normalize=True.

2. Instantiate:
    - Let v = MyVariable("user.profile", exclude=("password",)) — __init__ compiles "user.profile", normalizes exclude to a tuple, and computes unambiguous_source.

3. Use during tracing:
    - For each traced frame, the tracer calls v.items(frame, normalize=False).
    - If evaluating "user.profile" in the frame raises NameError, v.items(...) returns ().
    - If evaluation succeeds and _items returns [("user.profile.name", "Alice"), ("user.profile.email", "a@b")], that list is returned and used by the tracer.

4. Hashing and equality:
    - Two instances compare equal (v1 == v2) only if both are instances of BaseVariable (isinstance check) and have identical fingerprints (same concrete type, same source string, and same exclude tuple).
    - Hashing uses hash((type(instance), source, exclude)), so equal instances have equal hashes (barring unhashable exclude elements).

Implementation notes for subclass authors:
- Treat _items as a pure/probing operation where possible; avoid mutating the inspected object or global state.
- Be defensive: catch AttributeError/KeyError/IndexError when probing nested attributes or indices and either skip the problematic sub-item or return a best-effort set of items.
- If normalize=True is requested, produce stable, canonical display names, using unambiguous_source (parenthesized when required) as the root.

### `pysnooper.variables.BaseVariable.__init__` · *method*

## Summary:
Initializes the variable descriptor by storing the source expression, normalizing the exclusion list into a tuple, compiling the expression for later evaluation, and computing an unambiguous (parenthesized when needed) textual form of the source.

## Description:
This constructor is invoked when a new variable descriptor (a BaseVariable or subclass instance) is created — typically during tracer setup or whenever the tracer parses or constructs variable expressions to monitor. It performs the minimal, deterministic initialization required so subsequent operations (for example, evaluating the expression against a stack frame) can use the precompiled code object and an unambiguous printable source form.

This logic is provided in __init__ rather than being inlined elsewhere because:
- It sets up core immutable state (the compiled code object and canonical source strings) that other instance methods depend on.
- Normalizing the exclude input and compiling the source are initialization concerns best done exactly once at construction time to avoid repeated work and to centralize error handling for invalid expressions.

Known callers and calling context:
- Instantiation points are not listed in this snippet; typical callers are factory functions, parser code, or subclass constructors that create variable descriptors when configuring which expressions to observe during tracing.
- Lifecycle stage: called once when the variable descriptor is created, before any call to items(frame, ...) or other instance methods.

## Args:
    source (str):
        - A Python expression fragment (string) that will later be evaluated using eval against a frame's globals/locals.
        - Must represent a single expression suitable for compile(..., mode='eval').
        - There is no default; callers must pass a value.
    exclude (iterable or single value, optional):
        - Values to mark as excluded for this variable descriptor; semantics of exclusion are determined by subclasses.
        - Any iterable (except that text-like values are treated as scalar) will be converted into a tuple of its elements using utils.ensure_tuple.
        - Defaults to an empty tuple () when omitted.

## Returns:
    None
    - As a constructor, it does not return a value; it initializes instance attributes described below.

## Raises:
    SyntaxError:
        - If compile(source, '<variable>', 'eval') raises SyntaxError because source is not a valid single Python expression.
        - Also possible if needs_parentheses attempts to compile formatted strings and compilation fails; such SyntaxError propagates.
    TypeError:
        - If source is of an unsupported type for compile() (for example, an object that cannot be formatted to a valid source string for the subsequent needs_parentheses check) or if formatting in needs_parentheses raises a TypeError.
    Any exception raised by utils.ensure_tuple:
        - If exclude is an iterable whose iteration raises an exception, that exception propagates (for example, if a custom iterator raises during iteration).
    Notes:
        - These are the direct exceptions visible from the source; callers should handle them if user-provided/untrusted input is possible.

## State Changes:
Attributes READ:
    - None of self's attributes are read before being assigned during initialization.

Attributes WRITTEN:
    - self.source: set to the provided source argument (raw string).
    - self.exclude: set to the tuple returned by utils.ensure_tuple(exclude).
    - self.code: set to the code object returned by compile(source, '<variable>', 'eval').
    - self.unambiguous_source: set to a parenthesized form '({})'.format(source) when needs_parentheses(source) is True, otherwise set equal to source.

## Constraints:
Preconditions:
    - The utils.ensure_tuple function and the needs_parentheses helper must be available in the module namespace.
    - source should be a string (or another object acceptable to compile) that represents a single Python expression suitable for eval mode. If not, compile will raise SyntaxError or TypeError.
    - If exclude is an iterator/generator and the caller needs to reuse it later, the caller must not rely on it after constructing this object because it may be consumed by utils.ensure_tuple.

Postconditions:
    - After successful return:
        * self.source == source (unchanged raw input).
        * self.exclude is a tuple (possibly empty) representing the normalized exclude values.
        * self.code is a compiled code object that can be passed to eval(..., mode='eval') to evaluate the expression in a frame context.
        * self.unambiguous_source is a string guaranteed to produce the same attribute-binding behavior if appended with ".x" (i.e., it will be parenthesized when needed to prevent incorrect attribute binding).
    - No other attributes on self are modified by this constructor.

## Side Effects:
    - Consumes/iterates exclude if it is an iterator/generator (utils.ensure_tuple will iterate it to produce a tuple), potentially exhausting it for the caller.
    - No I/O, no network calls, and no modification of globals or external mutable objects (aside from consuming iterables passed as exclude).
    - Compilation uses filename '<variable>' when creating self.code (useful for tracebacks), but this only affects the created code object's metadata and does not write files.

### `pysnooper.variables.BaseVariable.items` · *method*

## Summary:
Evaluate the variable's compiled expression in the provided frame and return the iterable of (display_name, value) pairs produced by the variable-specific extractor; do not mutate the BaseVariable instance.

## Description:
- Known callers and context:
    - Invoked during the variable-capture stage of a pysnooper trace when the tracer collects values to display for each configured variable. The tracer evaluates each variable expression in the current frame and calls this method to obtain the items to log.
    - The typical lifecycle: BaseVariable is constructed with a source string (compiled into self.code); for each traced frame the tracer calls items(frame, normalize) to get displayable name/value pairs for that variable.
- Why this logic is a separate method:
    - This method centralizes safe evaluation and coarse error-handling around eval, while delegating the object-specific task of mapping the evaluated value into one-or-more (display_name, value) pairs to the subclass-implemented _items method. Separating evaluation from extraction keeps responsibilities clear and enables different traversal strategies per variable kind.

## Args:
    frame (frame object): A Python frame object exposing f_globals and f_locals. These are used as the globals and locals mappings for evaluation.
    normalize (bool, optional): Forwarded to the subclass extractor. If True, callers request canonical/normalized display names (default False).

## Returns:
    Iterable[tuple[str, Any]]:
        - If evaluating the compiled expression raises any Exception, returns the empty tuple () and does not call _items.
        - Otherwise returns the exact value returned by self._items(main_value, normalize). That return value is expected to be an iterable of 2-tuples (display_name, value), where display_name is a str and value is any Python object.
        - If self._items returns a lazy generator/iterator, exceptions raised during iteration will propagate to the caller at iteration time.

## Raises:
    - This method catches and suppresses all exceptions raised by eval and converts them into an empty-tuple result; it does not raise in that case.
    - Any exceptions raised by self._items (or by iterating its returned iterable) are not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.code (the compiled code object produced at construction via compile(source, '<variable>', 'eval'))
        - self._items (method resolution / lookup)
        - frame.f_globals and frame.f_locals (used as mappings supplied to eval)
    Attributes WRITTEN:
        - None. This method does not modify the BaseVariable instance.

## Constraints:
    Preconditions:
        - self.code must be a compiled expression object (constructed in __init__).
        - frame must be a valid frame object with accessible f_globals and f_locals attributes.
    Postconditions:
        - If evaluation raises any Exception, the method returns () and does not call _items.
        - If evaluation succeeds, the method returns exactly what self._items(main_value, normalize) returns.
        - normalize is forwarded unchanged to _items.

## Side Effects:
    - The method executes eval on previously-compiled source in the context (frame.f_globals or {}, frame.f_locals). The "frame.f_globals or {}" fallback means that if frame.f_globals is falsy (e.g., None or an empty mapping), an empty globals mapping is used for evaluation.
    - Because eval executes the expression, it may perform arbitrary side effects (mutations, I/O, imported code execution) depending on the expression contents; those side effects are not controlled by this method.
    - The method calls self._items(main_value, normalize); any side effects performed by _items (mutations, I/O) are the responsibility of the subclass and will propagate.

## Examples (prose):
    - If the BaseVariable was created for source "a.b" and, in the provided frame, evaluating that expression yields an object X, this method will call _items(X, normalize) and return the name/value pairs that the subclass determines (for example, one pair for "a.b" or several pairs for selected attributes of X).
    - If the expression evaluation raises NameError (missing name) or any other exception, items() will return () and the subclass extractor will not be invoked.

### `pysnooper.variables.BaseVariable._items` · *method*

## Summary:
Return an iterable of name/value pairs derived from the evaluated variable value so that the caller can log one or more displayed "items" for this variable. Implementations map the runtime value (the evaluated expression) into zero or more (display_name, value) pairs; they do not mutate the object state.

## Description:
- Known callers and context:
    - BaseVariable.items calls this method after successfully evaluating the variable expression in a frame:
        * It evaluates the expression to produce main_value, and then calls _items(main_value, normalize).
        * This method is invoked during the variable-capture phase of a pysnooper trace when the library is building the set of values to display.
    - Because BaseVariable.items only wraps the evaluation step in a try/except and then directly returns whatever _items produces, any exceptions raised by _items will propagate to the caller. Implementations should therefore handle expected error cases themselves (see Raises below).

- Why this logic is a separate method:
    - Extraction of "items" from a runtime object depends heavily on the variable kind (simple variable, attribute access, mapping, sequence, indexed access, named slices, etc.). Making _items an abstract instance method lets each subclass encapsulate the logic to enumerate one or more displayed items.
    - Keeping this logic separate allows consistent handling of evaluation (in BaseVariable.items) while delegating object-specific traversal and formatting to subclasses.

## Args:
    key (Any): The value produced by evaluating the variable expression (the runtime object to inspect). It may be any Python object (primitive, object, mapping, sequence, etc.).
    normalize (bool): If True, the caller requests that returned display names be put into a canonical/normalized form suitable for deduplication or fingerprinting. Default is False.

## Returns:
    Iterable[tuple[str, Any]]: A sequence (iterator, list, or tuple) of 2-tuples. Each tuple must be:
        - display_name (str): A human-readable identifier for the particular item derived from this variable. Implementations must return strings for all names. Typical forms:
            * For a simple variable: a single name corresponding to the original source or its canonical form (see normalize).
            * For attributes or indexed items: "root.attr" or "root[index]" style names that are unique within this variable's output.
        - value (Any): The object/value to be logged for that display_name (usually the actual Python object or a value derived from it).
    - Empty iterable: If there are no items to report (e.g., value is None or excluded), return an empty iterable (not None).
    - Determinism: The iteration order should be stable and deterministic for the same input value to make logged output predictable.

## Raises:
    NotImplementedError: The base implementation is abstract and should raise NotImplementedError if left unimplemented.
    Other exceptions: Implementations should avoid raising exceptions for ordinary runtime conditions (missing keys, out-of-range indices, uninspectable objects). Because BaseVariable.items does not catch exceptions from _items, any unhandled exception will propagate and may abort logging; therefore implementations should catch and handle expected errors and either skip problematic subitems or return a best-effort set of items.

## State Changes:
    Attributes READ:
        self.source
        self.unambiguous_source
        self.exclude
    Attributes WRITTEN:
        (none) Implementations must not rely on or perform persistent writes to the BaseVariable instance as part of item enumeration. The method is intended to be a pure query against the runtime value and the variable metadata.

## Constraints:
    Preconditions:
        - BaseVariable.items has already evaluated the expression; `key` is the evaluated result (not a source string).
        - The caller expects an iterable of (str, Any); callers may iterate over the result immediately.
    Postconditions:
        - The returned iterable yields only 2-tuples (str, Any).
        - Display names must be strings and should identify the item uniquely relative to the variable's output.
        - If normalize is True, display names should be in a canonical form (for example using self.unambiguous_source as the root rather than self.source, and using consistent bracket/dot notation for sub-items). The precise normalization conventions are left to subclasses, but the names must be stable and comparable across invocations.
        - Items whose display names match any entries in self.exclude (if present) should be omitted by the implementation (or filtered by the caller; implementations are encouraged to respect self.exclude proactively).

## Side Effects:
    - Implementations should avoid:
        * Mutating the inspected object (`key`) or other global state.
        * Performing I/O, logging, or network calls.
        * Creating persistent side effects on self (no writes to instance attributes).
    - Allowed minor actions:
        * Temporary shallow copies or introspection that does not mutate external state.
        * Short-lived allocations used to build names/tuples returned to the caller.

## Implementation guidance and examples:
    - Implementers typically map a variable kind to zero or more items:
        * Simple scalar: return a single [(display_name, key)].
        * Attribute traversal: if the expression is "a.b", return [(f"{root}.b", getattr(key, 'b'))] or similar.
        * Mapping: iterate items() and return [(f"{root}[{repr(k)}]", v) for k, v in key.items()].
        * Sequence: iterate indices up to a configured limit and return [(f"{root}[{i}]", key[i])].
    - Examples (pseudocode, for guidance only):
        * normalize=False -> display_name uses self.source as the root
        * normalize=True  -> display_name uses self.unambiguous_source as the root
    - Error handling:
        * Catch KeyError/IndexError/AttributeError when probing subitems and skip those subitems rather than raising.
        * If an object is too large or expensive to traverse, return a limited or summarized set of items (the caller will display what is returned).

This contract is sufficient to implement subclass _items methods that integrate correctly with BaseVariable.items and the rest of the variable-capture pipeline.

### `pysnooper.variables.BaseVariable._fingerprint` · *method*

## Summary:
Produces a stable, structural fingerprint for this variable object as a 3-tuple containing the object's class, its source attribute, and its exclude attribute.

## Description:
- Known callers and context:
    - No callers are visible in the provided source excerpt. Conceptually, this method is intended to be called whenever a stable, comparable identity for a BaseVariable instance is required (for example: equality checks, membership in sets, use as keys in maps, or cache/registry lookups).
    - Typical lifecycle stage: invoked when code outside the instance needs a compact, deterministic representation of the variable object's identity or configuration.

- Why this is its own method:
    - Centralizes the identity/fingerprint logic in one place so all consumers obtain a consistent tuple representation.
    - Keeps calling code simple (callers need not know which attributes compose the fingerprint) and makes future changes to which attributes form the fingerprint localized to this method.

## Args:
    None.

## Returns:
    tuple[type, Any, Any]
    - A 3-tuple with these elements in order:
        1. type(self): the runtime class object of the instance (e.g., BaseVariable or a subclass).
        2. self.source: the value of the instance's source attribute.
        3. self.exclude: the value of the instance's exclude attribute.
    - Edge cases:
        - The method always returns a 3-tuple; it does not validate or coerce the attribute values.

## Raises:
    None raised explicitly by this method.
    - If accessing self.source or self.exclude raises an AttributeError (because the attributes do not exist), that exception will propagate from the attribute access.

## State Changes:
- Attributes READ:
    - self.source
    - self.exclude
- Attributes WRITTEN:
    - None (this method does not modify the instance state).

## Constraints:
- Preconditions:
    - The instance must have readable attributes named source and exclude. If they are missing, attribute access will raise AttributeError.
- Postconditions:
    - No mutation of self occurs.
    - The returned value is a tuple (type(self), source_value, exclude_value) reflecting the values at the time of the call.

## Side Effects:
    - None. The method performs no I/O, does not call external services, and does not modify objects other than reading attributes on self.

### `pysnooper.variables.BaseVariable.__hash__` · *method*

## Summary:
Compute and return an integer hash derived from the object's fingerprint tuple; does not modify the object's state.

## Description:
Delegates hashing to the object's _fingerprint property, which the class defines as (type(self), self.source, self.exclude). Typical invocation contexts:
- The built-in hash() when called on a BaseVariable instance.
- Automatic hashing operations performed by dict and set when the instance is used as a key or inserted into a set.

This logic is implemented as a dedicated method to centralize hashing behavior and ensure consistency with __eq__, which compares the same _fingerprint.

## Args:
- None

## Returns:
- int: The result of applying Python's built-in hash() to self._fingerprint.

## Raises:
- TypeError: Raised by the built-in hash() if any element of self._fingerprint is unhashable.

## State Changes:
- Attributes READ:
    - self._fingerprint (property) — which accesses:
        - type(self)
        - self.source
        - self.exclude
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - The instance must be initialized so self.source and self.exclude exist (the BaseVariable __init__ establishes these).
    - The elements composing _fingerprint should be hashable to avoid a TypeError.
- Postconditions:
    - The method returns an integer and leaves the object unchanged.
    - If two BaseVariable instances compare equal via __eq__ (i.e., their _fingerprint tuples are equal), they will produce equal hash values.

## Side Effects:
- None (no I/O, no external calls, no mutations of objects outside self)

### `pysnooper.variables.BaseVariable.__eq__` · *method*

## Summary:
Compares this variable to another object for value equality by checking both are BaseVariable instances of the same concrete type and that their identifying fingerprint tuples are equal; does not modify the object.

## Description:
This method implements structural equality for BaseVariable instances by delegating to the _fingerprint property, which uniquely identifies a variable by (type(self), self.source, self.exclude).

Known callers and typical contexts:
- Any Python code that uses == to compare BaseVariable instances (e.g., tests, deduplication logic).
- Implicit callers when BaseVariable instances are used in containers that rely on equality (for example, when comparing keys in dicts or elements in sets).
- Libraries or code that check for semantic equivalence of two variable specifications before caching or memoization.

Why this is a separate method:
- Equality semantics for BaseVariable need to be explicit and consistent with __hash__. Implementing this logic in __eq__ centralizes the comparison rules (type, source, exclude) and ensures Python operators and container behavior behave correctly. Keeping it as a method avoids duplicating fingerprint-comparison logic wherever equality checks are needed.

## Args:
This method takes no explicit arguments beyond the usual self and other.

- other (any): The object to compare against. It may be any Python object; the method will return False for non-BaseVariable objects.

## Returns:
bool
- True if and only if:
    - other is an instance of BaseVariable (including subclasses), and
    - self._fingerprint == other._fingerprint, where _fingerprint is the tuple (type(instance), instance.source, instance.exclude).
- False otherwise (including when other is not a BaseVariable instance).

Edge cases:
- If other is a BaseVariable subclass instance but has a different concrete type than self, the type component of the fingerprint will differ and the result will be False.
- Comparison is reflexive and consistent with __hash__ (i.e., equal fingerprints produce equal hashes).

## Raises:
- No exceptions are explicitly raised by this method.
- If the instance is in an invalid/partially-initialized state (missing attributes used by the _fingerprint property), attribute access inside _fingerprint may raise AttributeError. Under normal use, BaseVariable.__init__ establishes required attributes (source, exclude), so this should not occur.

## State Changes:
Attributes READ:
- self._fingerprint (property). Indirectly reads:
    - type(self)
    - self.source
    - self.exclude
- If other is a BaseVariable instance, other._fingerprint is read (and thus type(other), other.source, other.exclude are read) as part of the tuple comparison.

Attributes WRITTEN:
- None. This method does not modify self or other.

## Constraints:
Preconditions:
- self should be a properly-initialized BaseVariable (its __init__ sets source and exclude). The method assumes self has the attributes accessed by _fingerprint.
- other may be any object; no precondition is required for callers (non-BaseVariable values simply produce False).

Postconditions:
- No mutation of self or other.
- Return value correctly reflects whether both operands share the same concrete type and identical fingerprint tuple.

## Side Effects:
- None. The method performs no I/O, network calls, or external mutations.

## `pysnooper.variables.CommonVariable` · *class*

*No documentation generated.*

### `pysnooper.variables.CommonVariable._items` · *method*

## Summary:
Produce an ordered list of (name, short_repr) pairs describing a value and its inspectable sub-entries for display in trace output; the method does not mutate the object state.

## Description:
- Known callers:
    - No direct callers were discovered in the available repository search results. Conceptually this method is used by tracing or pretty-printing code that flattens a variable into displayable name/value pairs before emitting a trace line.
    - Typical lifecycle stage: invoked when preparing a single trace record or display block for a particular variable; the caller passes the variable as main_value and collects the returned list for rendering.
- Why this is a separate method:
    - Centralizes the logic for creating the initial main-value tuple, iterating safe sub-keys, skipping excluded or failing keys, formatting sub-key names, and converting values to compact one-line strings. This avoids duplicating key-safety, exception-suppression, and consistent representation formatting in multiple places.

## Args:
    main_value (Any):
        The object to inspect. Subclasses interpret sub-keys according to their type-specific _keys/_get_value implementations.
    normalize (bool, default=False):
        If True, the main_value's representation is passed to utils.get_shortish_repr(..., normalize=True). Child-entry representations are produced with the default normalize=False.

## Returns:
    list[tuple[str, str]]:
        Ordered list of (name, short_repr) pairs:
        - The first element is (self.source, utils.get_shortish_repr(main_value, normalize=normalize)).
        - Subsequent elements correspond to keys yielded by self._safe_keys(main_value). For each key not excluded and whose retrieval does not raise, the tuple is (self.unambiguous_source + self._format_key(key), utils.get_shortish_repr(child_value)).
        Edge cases:
        - The list always contains at least the main-value tuple (i.e., it is never empty).
        - Keys for which "key in self.exclude" raises, or for which _get_value raises, are silently skipped.
        - If self._keys yields no keys, only the main-value tuple appears.

## Raises:
    - Exceptions from utils.get_shortish_repr may or may not propagate depending on their origin:
        * Exceptions raised by the chosen repr function when called inside get_shortish_repr are caught by get_shortish_repr; in that case get_shortish_repr substitutes the literal 'REPR FAILED' and returns that string (subject to later normalization/truncation inside get_shortish_repr).
        * Exceptions raised by get_shortish_repr's normalization or truncation steps (for example, from normalize_repr, truncate, or attribute errors when the repr is not a str) will propagate out of this method.
    - Exceptions raised by self._format_key(key) will propagate (this call is outside the try/except used for _get_value).
    - Exceptions raised by utils.get_shortish_repr(child_value) for a child value will propagate only if they originate from normalization/truncation or non-str handling inside get_shortish_repr (see above). get_shortish_repr will not propagate exceptions thrown by the selected repr callable — those are converted to 'REPR FAILED'.
    - Note: exceptions raised during key iteration are largely suppressed because _safe_keys wraps _keys in a try/except; if _keys raises, _safe_keys stops yielding and no exception is raised from that source.

## State Changes:
- Attributes READ:
    - self.source
    - self.unambiguous_source
    - self.exclude
    - self._safe_keys (invoked)
    - self._get_value (invoked)
    - self._format_key (invoked)
- Attributes WRITTEN:
    - None — the method does not modify self or external state.

## Constraints:
- Preconditions:
    - self.source and self.unambiguous_source should be usable in string formatting (they will be formatted into returned name strings).
    - self.exclude must support membership testing via "key in self.exclude".
    - Subclasses should implement _keys, _get_value, and _format_key appropriately; the base _keys returns an empty iterable and the base _get_value/_format_key raise NotImplementedError.
- Postconditions:
    - The returned list contains at least one (name, short_repr) tuple corresponding to the main value.
    - No attributes on self are changed.

## Side Effects:
    - No I/O or network calls are made by this method itself.
    - Calls to utils.get_shortish_repr may invoke user-provided representation functions (via get_repr_function) which can have arbitrary side effects; those side effects will occur here.
    - Calls to self._get_value or self._format_key may have side effects depending on subclass implementations (e.g., property accessors). Any such side effects are not suppressed.

### `pysnooper.variables.CommonVariable._safe_keys` · *method*

## Summary:
Yield keys returned by the subclass _keys iterator while suppressing ordinary exceptions; does not mutate the object's state.

## Description:
Known callers and call context:
- CommonVariable._items(self, main_value, normalize=False): iterates over this method's generator to obtain subordinate keys when building the list of displayable items for a inspected value. This occurs during variable inspection/item generation.
- This method is the safe wrapper used at the point in the inspection pipeline where keys are enumerated and then passed to _get_value and _format_key for display.

Why this is a separate method:
- It centralizes exception handling for key enumeration so subclasses can implement _keys without duplicating try/except logic. _keys is a subclass hook intended for enumerating keys (possibly lazily); _safe_keys isolates the safety policy (suppress exceptions during enumeration) from the actual enumeration implementation.

## Args:
    main_value (object): The value being inspected. The interpretation of main_value is implementation-dependent (e.g., dict, sequence, object instance); subclasses of CommonVariable decide how to enumerate keys from this value.

## Returns:
    iterator:
        A generator/iterator that yields zero or more key objects returned by self._keys(main_value). Typical key types are those that can be used with _get_value(main_value, key) and compared against self.exclude.
    Edge-case return behavior:
        - If self._keys(main_value) raises an Exception or if iterating its return value raises an Exception, _safe_keys suppresses that Exception and the generator ends (behaves as if there are no further keys).
        - If self._keys returns a non-iterable, attempting to iterate it will raise a TypeError; that TypeError is caught and suppressed, resulting in no yielded keys.

## Raises:
    - This wrapper does not raise exceptions derived from Exception; such exceptions are caught and suppressed, causing the generator to terminate quietly.
    - Exceptions that do NOT inherit from Exception (e.g., KeyboardInterrupt, SystemExit, or other BaseException subclasses) are not caught by the except Exception block and will propagate normally.

## State Changes:
Attributes READ:
    - None directly by this implementation. (It does call the instance method self._keys(main_value), which may read attributes inside its implementation.)
Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - No explicit preconditions on self or main_value required by _safe_keys itself. Subclass _keys implementations may require main_value to have a particular shape (e.g., be a mapping or sequence); callers should supply appropriate values for meaningful results.

Postconditions:
    - The returned generator will yield keys produced by self._keys(main_value) until either _keys is exhausted or an Exception is raised inside _keys or during iteration, at which point the generator will stop without raising.
    - No attributes on self are modified by _safe_keys itself.

## Side Effects:
    - This method performs no I/O and has no external side effects by itself.
    - Any side effects come from the subclass implementation of _keys(main_value). Because _safe_keys suppresses Exception, side effects performed by _keys may occur even when errors happen and those errors will be hidden from callers of _safe_keys; subclass implementations should avoid surprising side effects during enumeration.

### `pysnooper.variables.CommonVariable._keys` · *method*

## Summary:
Provide an iterable of sub-keys for a composite/main value so the inspector can enumerate subordinate entries; the default implementation yields no keys (no subordinate entries).

## Description:
Known callers and call context:
- _safe_keys(self, main_value): invokes this method and iterates over its result inside a try/except. Any exception raised by _keys or by attempting to iterate its return value will be caught and suppressed by _safe_keys, causing no keys to be yielded.
- _items(self, main_value, normalize=False): obtains keys via _safe_keys, then for each yielded key checks membership in self.exclude and calls _get_value and _format_key to produce display items.

Lifecycle / pipeline stage:
- This method is called during variable inspection when building a list of displayable items for a variable (i.e., when generating the "items" representation of the inspected object).

Why this logic is its own method:
- _keys is a subclass hook that isolates key enumeration logic from value retrieval (_get_value) and key formatting (_format_key). Separating enumeration into its own method lets subclasses implement efficient/specialized iteration (e.g., yield keys lazily) and keeps exception-handling centralised in _safe_keys.

## Args:
    main_value (object): The value being inspected. The type is implementation-dependent — subclasses decide how to interpret this argument (e.g., dict, sequence, object instance).

## Returns:
    iterable: An iterable of keys (for example, a tuple/list/generator that yields keys). The default implementation returns an empty tuple, indicating "no keys".
    - Practical expectations: keys should be of types comparable to the entries in self.exclude (since callers perform "key in self.exclude") and suitable for use with _get_value(main_value, key).
    - Edge behavior: If _keys returns a non-iterable or raises any exception, _safe_keys will suppress the error and the result will behave as if there are no keys.

## Raises:
    This default implementation does not raise. Subclass implementations may raise exceptions, but such exceptions will be swallowed by _safe_keys during normal inspection; raising is therefore not an effective way to signal errors to the caller.

## State Changes:
Attributes READ:
    - None by the default implementation. (Note: callers will read self.exclude and other attributes, but _keys itself does not access them in the default form.)
Attributes WRITTEN:
    - None

## Constraints:
Preconditions:
    - No specific preconditions are required by the default implementation.
    - If a subclass implementation relies on particular structure of main_value (e.g., expecting a dict), callers should ensure main_value meets that expectation before depending on returned keys.

Postconditions:
    - After the call, no attributes of self are modified by the default implementation.
    - The caller can safely iterate the result via _safe_keys; any exception raised by this method or by iterating its return value will cause no keys to be yielded.

## Side Effects:
    - The default implementation has no I/O or external effects and does not mutate objects outside self.
    - Subclass implementations must avoid performing expensive I/O or mutating main_value unless mutation is explicitly intended, because exceptions from _keys will be suppressed and such side effects may be unexpected during inspection.

## Implementation guidance for subclasses:
    - Prefer yielding keys (generator) for memory efficiency when possible.
    - Ensure keys are directly usable with _get_value(main_value, key) and comparable to elements of self.exclude.
    - Avoid raising exceptions for ordinary control flow. If an exception occurs, it will be silently ignored by the inspection flow.
    - Keep _keys free of side effects where possible to avoid surprising behavior during inspection.

### `pysnooper.variables.CommonVariable._format_key` · *method*

## Summary:
Provide a textual suffix for a single child-key so it can be appended to this variable's unambiguous source; does not modify object state.

## Description:
This abstract helper formats a single key (as produced by this variable's _keys/_safe_keys) into the string fragment that, when concatenated with self.unambiguous_source, yields a human-readable, unambiguous reference to the nested value.

Known callers and lifecycle:
- Called from CommonVariable._items while iterating keys returned by _safe_keys(main_value). In that pipeline stage _format_key is invoked for each discovered child key to build the left-hand "source" column shown in pysnooper output (the fully-qualified name of the inspected value).
- Implementations are also free to be called by other debug/inspection helpers that need the same formatted key semantics.

Why this is a separate method:
- Different container/variable types (mappings, sequences, object attributes, slices, etc.) require different syntactic representations (e.g., "['k']", "[0]", ".attr"). Providing this logic in a single overridable method centralizes the formatting policy for each subclass and keeps _items generic.

## Args:
    key (any):
        A single key value yielded from this variable's _keys(main_value) iterator. Typical concrete types:
        - For mappings: keys of the mapping (str, int, tuple, etc.)
        - For sequences: integer indices or slice objects
        - For attribute-style variables: attribute name as str
        - For nested/compound keys: any object the subclass recognizes
        Implementations must accept the exact keys produced by their own _keys/_safe_keys methods.

## Returns:
    str:
        A string fragment that represents the key when appended to self.unambiguous_source.
        - Must be non-empty.
        - Must include any required syntactic separators (for example ".", "[", "]") so that "{}{}" .format(self.unambiguous_source, returned_string) is a sensible, unambiguous reference to the child value.
        - Examples of acceptable return values (depending on subclass):
            - For attribute "name": ".name"
            - For mapping key "foo": "['foo']"  (quotes and brackets included)
            - For integer index 0: "[0]"
            - For tuple key ('a', 1): "['a',1]" or other unambiguous representation chosen by the implementer

Edge-case return values:
- If the key cannot be sensibly represented, implementations should still return a deterministic string (for example, repr(key) wrapped in brackets) rather than raising, unless the subclass chooses to signal unsupported key types via an explicit exception (see Raises).

## Raises:
    NotImplementedError:
        - The base-class implementation always raises NotImplementedError. Subclasses must override this method.
    TypeError (optional, subclass-specific):
        - Implementations may raise TypeError if given a key of an unsupported type for that variable kind (document this behavior in the subclass).
    ValueError (optional, subclass-specific):
        - Implementations may raise ValueError if the key contains values that cannot be safely converted/escaped; prefer returning a safe representation instead.

## State Changes:
    Attributes READ:
        - self.unambiguous_source (read by the caller when concatenating; implementations may reference other read-only attributes such as configuration flags, e.g., quoting style or max-length settings)
        - any subclass-specific readonly attributes used to influence formatting (implementations should document these)
    Attributes WRITTEN:
        - None. This method should be pure with respect to the object's state (no mutation of self).

## Constraints:
    Preconditions:
        - The provided key must be one that the variable instance's _keys(main_value) would produce for the same inspected value.
        - Caller expects a string return value that is safe to concatenate directly with self.unambiguous_source.

    Postconditions:
        - Returns a deterministic str that, when concatenated to self.unambiguous_source, yields an unambiguous textual reference to the child value.
        - Does not raise (unless the subclass documents and intends to raise for unsupported key types).

## Side Effects:
    - Should have no I/O or network activity.
    - Should not mutate external objects or global state.
    - May call pure helper functions (e.g., repr or a quoting utility) to produce its result.

## Implementation notes and examples for subclass authors:
- Keep the output stable and human-readable; prefer familiar Python indexing/attribute notation.
- Escape or quote keys that could break the chosen syntax (for example, map string keys that contain single quotes should be safely quoted or escaped).
- Examples of minimal implementations:
    - Attribute-style variable: return '.' + key where key is a valid identifier; otherwise return "['" + key.replace("'", "\\'") + "']"
    - Mapping variable: return '[' + repr(key) + ']'
    - Sequence variable: return '[' + str(index) + ']'
- Document any deviations (for example, different quoting styles or omitted separators) in the specific subclass documentation.

### `pysnooper.variables.CommonVariable._get_value` · *method*

## Summary:
Provide the child or member value of a container-like main_value for a given key; this is an abstract accessor that subclasses implement to extract the value associated with key without changing the variable object's own state.

## Description:
- Known callers and call-site context:
    - CommonVariable._items calls this method while building a list of (name, short_repr) pairs for a variable's children. In that lifecycle step pysnooper is collecting child values to include in trace output.
    - The call happens inside a try/except block in _items: exceptions raised while retrieving a child value are caught and simply cause that key to be skipped. This means callers expect implementations to possibly raise standard retrieval exceptions (e.g., KeyError, IndexError, AttributeError) and tolerate them.

- Why this is a separate method:
    - The exact mechanics of retrieving a child value differ by the type of container or variable (for example: mapping key lookup, sequence/index access, attribute access on an object, handling of slices, or custom object protocols). Making this an overridable method isolates that variation into one place so subclasses can supply type-specific logic without duplicating item-iteration or filtering logic contained in _items/_keys/_safe_keys.
    - Separating retrieval allows _items to uniformly format and represent values (using utils.get_shortish_repr) while letting subclasses decide how to obtain those values.

## Args:
    main_value (Any):
        - The container or parent object from which a child/member is to be retrieved.
        - Expected to be the same object passed into the surrounding _items/_keys machinery.
    key (Any):
        - A key/index/attribute descriptor produced by _keys(main_value).
        - Typical kinds: mapping keys (strings, numbers, tuples), integer indices for sequences, slice objects, or attribute names (strings). Implementations should accept whatever key forms _keys yields.

## Returns:
    Any:
        - The value obtained from main_value corresponding to key.
        - May be any Python object. The returned value will be passed to a shortish-representation function by the caller.
        - Edge-case returns: None or sentinel objects are valid return values if that is the natural value for the given key; there is no special wrapping applied by the caller.

## Raises:
    NotImplementedError:
        - The base-class implementation raises NotImplementedError; subclasses must override this method to provide retrieval semantics.

    Other exceptions (KeyError, IndexError, AttributeError, TypeError, ValueError, or arbitrary exceptions):
        - Implementations may raise standard lookup/access exceptions when the key is invalid for the main_value.
        - These are expected to be caught by the caller (CommonVariable._items) and cause the key to be skipped in tracing output. Implementers do not need to pre-catch these unless they want to transform or suppress them.

## State Changes:
- Attributes READ:
    - The base method does not require reading any particular self attributes. Subclass implementations may read configuration or formatting attributes on self (for example, a flag limiting the amount of data to fetch), but this is implementation-specific.
- Attributes WRITTEN:
    - Implementations should not modify the variable object's persistent state. The method is an accessor only; it must not change self.<...> attributes.

## Constraints:
- Preconditions:
    - The key must be one that was (or could be) produced by _keys(main_value) for the same main_value.
    - main_value must be a valid object of the kind that the subclass expects (e.g., mapping, sequence, or object providing attributes). If main_value is of an unexpected type, implementations may raise TypeError or another appropriate exception.
- Postconditions:
    - On successful return, the value returned corresponds to the semantic child/member of main_value for the supplied key.
    - The method does not mutate main_value in the base contract (unless a concrete implementation documents and justifies mutation).

## Side Effects:
- The base contract expects no external I/O or global side effects. However:
    - Accessing attributes or properties on main_value can execute arbitrary user code (property getters, __getitem__, __getattr__, or custom __index__/__getitem__ implementations) and therefore may have side effects external to this method.
    - Implementers should be aware of that risk; because callers suppress retrieval exceptions, side effects that raise exceptions will simply result in the child being skipped.
    - If an implementation intentionally performs costly operations (deep copies, network calls, heavy computation), it should document that behavior and consider caching or limiting detail to avoid degrading tracing performance.

## Implementation guidance for subclasses:
- For mapping-like main_value: implement retrieval by performing a key-based lookup (the natural semantics are to attempt main_value[key] and propagate any KeyError).
- For sequence-like main_value: implement retrieval by integer/index access (support negative indices and slices if _keys yields them).
- For attribute-like access: implement retrieval via attribute lookup (getattr(main_value, key)) and handle AttributeError appropriately.
- If key can represent a composite access path (for example, nested keys or attribute-index tuples), implementers should document the expected key format and resolution order.
- Keep retrieval fast and side-effect-free where possible; rely on _items exception handling for resilience against failures.

## `pysnooper.variables.Attrs` · *class*

## Summary:
Represents a variable-inspection strategy that enumerates and formats an object's attribute names (from __dict__ and __slots__) and retrieves their values for logging/inspection purposes.

## Description:
Attrs is a focused subclass intended to implement attribute-based variable inspection for pysnooper's variable-serialization machinery. It supplies three cooperating helpers:
- _keys(main_value): enumerate attribute names to inspect,
- _format_key(key): format a key segment for display,
- _get_value(main_value, key): read the attribute value from the inspected object.

Typical usage scenario:
- A higher-level routine (for example, CommonVariable._items inside the same module) will create or use an Attrs instance when it needs to inspect an arbitrary Python object for logging. That routine is expected to call _keys to obtain candidate attribute names, then for each key call _format_key to produce a printable key fragment and _get_value to obtain the corresponding value for inclusion in the output.

Motivation and responsibility boundary:
- Attrs encapsulates how to enumerate and read instance-held attributes (both those stored in the instance dictionary and those declared with __slots__) and how to format the attribute name when appended to a parent variable path. It intentionally does not perform higher-level tasks such as deduplication of keys, value formatting, or assembling the final string representation — those responsibilities belong to the calling code (e.g., CommonVariable or other variable-formatting machinery).

## State:
- Attributes defined on Attrs:
    - None. Attrs defines no instance attributes of its own; it is stateless and implements behavior via methods only.
- For __init__ parameters:
    - Attrs does not define its own __init__; instantiation arguments and any invariants are those of its base class (CommonVariable). Consult CommonVariable for constructor parameters and contract.
- Class invariants:
    - Methods are pure with respect to Attrs instance state: none of the provided methods read or mutate self (no access to self.<attr> fields).
    - Methods operate only on the supplied main_value and key arguments and must not rely on any internal state being set on the Attrs instance.

## Lifecycle:
- Creation:
    - Instantiate Attrs using its constructor (inherited from CommonVariable). Because Attrs defines no __init__, there are no additional construction-time parameters or constraints introduced by this class.
- Typical usage sequence:
    1. Caller obtains an Attrs instance (or calls Attrs methods via dynamic dispatch on a variable-handler instance).
    2. Caller calls _keys(main_value) to obtain an iterator of candidate attribute names.
    3. For each key yielded:
        a. Caller calls _format_key(key) to obtain the formatted key segment (prefixed with a dot).
        b. Caller calls _get_value(main_value, key) to retrieve the attribute's current value (or observe that the call raised an exception).
    4. Caller assembles key/value pairs into the final log or representation and handles deduplication, error handling, and presentation.
- Destruction / cleanup:
    - No cleanup responsibilities. Attrs instances hold no resources and do not provide context-manager semantics.

## Method Map:
- The following diagram shows the usual call flow when a variable-inspection routine (for example CommonVariable._items) uses Attrs methods.

Mermaid diagram:
flowchart LR
    A[CommonVariable._items] --> B[Attrs._keys(main_value)]
    B -->|yields keys| C{for each key}
    C --> D[Attrs._format_key(key)]
    C --> E[Attrs._get_value(main_value, key)]
    D --> F[Caller assembles formatted key]
    E --> F[Caller assembles value]
    F --> G[Caller emits/logs key/value pair]

## Component method contracts (detailed)

- _keys(main_value)
    - Summary: Return a lazy iterator that yields attribute names from main_value.__dict__ followed by names from main_value.__slots__ (using empty defaults when either is missing).
    - Inputs:
        - main_value (object): any Python object (None is accepted but will result in an iterator over the provided defaults).
    - Output:
        - An iterator (itertools.chain) that yields zero or more items (commonly strings).
    - Behavior and edge cases:
        - Uses getattr(main_value, '__dict__', ()) and getattr(main_value, '__slots__', ()) as the two underlying iterables. The returned iterator yields the contents of the first iterable, then the second.
        - The iterator is lazy — no iteration occurs until the caller consumes it.
        - If __slots__ is a single string, iterating it yields characters; callers that require slot-name strings should normalize this case.
        - Duplicate names may be yielded (for example, if a slot name also appears in __dict__); callers should deduplicate if needed.
        - If a caller needs to iterate the keys multiple times or needs a stable snapshot, it should materialize the iterator into a list (e.g., list(attrs._keys(obj))) to avoid re-evaluation or differing iteration behavior.
        - If an underlying attribute exists but is not iterable, attempting to consume the iterator will raise TypeError at consumption time.
    - Side effects: none on Attrs state (reading main_value attributes only; attribute access may execute user code).

- _format_key(key)
    - Summary: Return a new string representing the key prefixed with a single period.
    - Inputs:
        - key (str): key segment to format. Should be a Python string in typical usage.
    - Output:
        - str: '.' concatenated with key (for example, key 'name' -> '.name').
    - Behavior and edge cases:
        - If key == '' returns '.'.
        - If key already starts with '.', the result will include multiple leading dots (e.g., key '.x' -> '..x').
        - Passing a non-str will raise TypeError because of string concatenation.
    - Side effects: none; the method does not access or mutate Attrs instance attributes.

- _get_value(main_value, key)
    - Summary: Return getattr(main_value, key) — perform a direct attribute lookup on the inspected object.
    - Inputs:
        - main_value (object): object to inspect.
        - key (str): attribute name to retrieve (typically a string).
    - Output:
        - Any: the raw attribute value returned by getattr.
    - Behavior and edge cases:
        - Standard getattr semantics apply:
            * If the attribute does not exist, AttributeError is raised.
            * If key is not a valid type (non-string where not supported), TypeError may be raised.
            * Accessing a property or descriptor may execute arbitrary user code and raise or perform side effects; such effects propagate through this method unchanged.
        - This method does not read or mutate any attributes on the Attrs instance.
    - Side effects: none introduced by the method itself, but attribute access may invoke user code with side effects.

## Raises:
- Attrs.__init__:
    - Attrs does not declare an __init__; therefore it raises no exceptions itself during construction. Any exceptions raised at construction time originate from the base class CommonVariable.__init__ — consult that class for constructor-specific raises.
- _keys, _format_key, _get_value:
    - These methods raise exceptions that directly reflect underlying operations:
        - _format_key: TypeError if key is not a str (due to string concatenation).
        - _get_value: AttributeError if attribute missing; TypeError if invalid key type; any exception raised by attribute access propagates.
        - _keys: typically safe at call time due to default fallbacks; attempting to iterate the returned iterator may raise TypeError if the underlying __dict__ or __slots__ is not iterable.

## Example (typical usage sequence, described):
- Given an object main_value whose instance dictionary contains {'name': 'alice'} and whose class defines no __slots__:
    - attrs._keys(main_value) returns a chain iterator that yields 'name'.
    - For the yielded key 'name':
        - attrs._format_key('name') returns '.name'.
        - attrs._get_value(main_value, 'name') returns 'alice'.
    - The caller receives the pair ('.name', 'alice') and includes it in the logged representation.

- If main_value has both a __dict__ entry and a slot with the same name, the iterator will yield the name twice; the caller should deduplicate if that is undesired.

Notes:
- Reimplementing Attrs is straightforward: provide the three methods above with the exact semantics described (use itertools.chain and getattr with defaults). Do not add or expect mutable internal state.

### `pysnooper.variables.Attrs._keys` · *method*

## Summary:
Produce an iterator (itertools.chain) that yields attribute names from an object's instance dictionary followed by names declared in its __slots__, without modifying the object.

## Description:
This helper centralizes the logic for enumerating attribute keys on a target object. It constructs and returns an iterator that first yields the keys from main_value.__dict__ (if present) and then yields items from main_value.__slots__ (if present). Typical consumers in this codebase are other Attrs methods that need to list or inspect attribute names before formatting or reading values.

Known callers and invocation context:
- Attrs._format_key — uses the names produced by this method to build a printable key path for each attribute during formatting of an object's attributes.
- Attrs._get_value — iterates these keys to fetch attribute values for logging/inspection.
Lifecycle step: invoked during variable-inspection and pretty-printing steps when the Attrs variable implementation enumerates an object's attributes for output. It is separated into its own method so enumeration logic is consistent and overrideable.

Why this is a separate method:
- Centralizes attribute-key enumeration so callers do not duplicate getattr-and-chain logic.
- Makes behavior (order, defaults, handling of missing attributes) explicit and easy to test or override.
- Keeps format- and value-retrieval code focused on their responsibilities.

## Args:
    main_value (object):
        Any Python object instance to inspect.
        - Expected to be an object that may expose:
            * __dict__: the instance dictionary (typically a mapping of attribute-name -> value)
            * __slots__: an iterable of slot-names (class-defined)
        - None is accepted; getattr will return the provided defaults and the resulting iterator will be empty.

## Returns:
    itertools.chain (iterator):
        - A chain iterator that yields items from two iterables in order:
            1. The result of getattr(main_value, '__dict__', ()) — iterating this yields the dict's keys (commonly strings).
            2. The result of getattr(main_value, '__slots__', ()) — iterating this yields the slot names (commonly strings or an iterable of strings).
        - The returned object is a lazy iterator; no iteration occurs until the caller consumes it.
        - Possible values: zero or more items (normally strings). Duplicates are possible.

## Raises:
    TypeError (when consuming the iterator):
        - The call itself is safe and will not raise for missing attributes because defaults are used.
        - If main_value.__dict__ or main_value.__slots__ exists but is not iterable, attempting to iterate the returned chain will raise TypeError at consumption time.
        - No other exceptions are raised by this function directly.

## State Changes:
    Attributes READ:
        - None on self (the method does not access self.<attr> fields).
        - Reads main_value.__dict__ via getattr and main_value.__slots__ via getattr.
    Attributes WRITTEN:
        - None. The method does not mutate main_value or self.

## Constraints:
    Preconditions:
        - main_value should be an object reference (can be None).
        - Callers should be aware that __slots__ may be defined as a string (which will iterate characters) or any iterable of names.
    Postconditions:
        - The returned iterator, when consumed, yields the sequence of items from __dict__ followed by items from __slots__ in that order.
        - The method does not modify main_value or any external state.

## Edge cases and important behavior notes:
    - Duplicate names: If an attribute name appears both in the instance __dict__ and in __slots__, it will be yielded twice (first from __dict__, then from __slots__). Callers should deduplicate if they require unique names.
    - Ordering: The order of keys from __dict__ follows the underlying mapping iteration order (insertion order for standard dicts on modern Python). The order of __slots__ items is whatever order the class defined or provided.
    - __slots__ as string: If __slots__ is a single string (uncommon but possible), iteration will yield individual characters; callers should normalize this if they expect slot names.
    - Class attributes and descriptors: Attributes defined only on the class (i.e., class attribute or descriptor) will not appear in an instance's __dict__ and will not be produced by this method unless the class also exposes them in __slots__. This method enumerates instance-held names only.
    - Laziness and performance: The returned itertools.chain is lazy and adds negligible overhead; it does not copy the underlying iterables.

## Side Effects:
    - None: no I/O, no external service calls, and no mutation of main_value or other external objects.
    - Requires importing itertools.chain (or equivalent chaining) to produce the returned iterator.

### `pysnooper.variables.Attrs._format_key` · *method*

## Summary:
Return a dotted representation of a key by prefixing it with a single period character, without mutating the object.

## Description:
This small helper produces a string that represents a member/key prefixed by a dot (for example to produce ".name" from "name"). It is intended to be called by routines that build or render hierarchical/dotted variable names for logging or introspection, typically as part of assembling variable-path strings inside the same class or module.

Known callers and lifecycle stage:
- Not determinable from the single-method snippet; in typical usage this is invoked by other methods that format or concatenate attribute/key paths just before they are emitted to a log or output. It is used during key/name formatting stage of any variable-inspection pipeline.

Why this is a separate method:
- Encapsulates the canonical rule for how keys are prefixed so callers remain concise and consistent.
- Keeps formatting behavior in one place to make future changes (for example switching to a different separator) easy to apply.

## Args:
    key (str): The key segment to format. Must be a Python string. No default value.

## Returns:
    str: A new string equal to '.' concatenated with key.
         - If key == '' (empty string) the result is '.'.
         - If key already starts with '.' the result will contain multiple leading periods (e.g., key='.x' -> '..x').

## Raises:
    TypeError: If key is not a str (for example None, bytes, or another non-str object). The TypeError arises from attempting to concatenate the literal '.' (a str) with a non-str using the '+' operator.

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> fields).
    Attributes WRITTEN:
        - None (this method does not modify any self.<attr> fields).

## Constraints:
    Preconditions:
        - The caller must pass a Python str as key. Calling with a non-str will raise TypeError.
    Postconditions:
        - The returned value is a str and begins with a single '.' character followed by the contents of key (which may itself begin with '.' or be empty).
        - The object's state (self) is unchanged.

## Side Effects:
    - None. This method performs no I/O, network calls, or modifications to objects outside self.

### `pysnooper.variables.Attrs._get_value` · *method*

## Summary:
Returns the value of the named attribute from the provided object, performing a direct attribute lookup on main_value without mutating the inspected object or this Attrs instance.

## Description:
Known callers and context:
- pysnooper.variables.CommonVariable._items calls this method while collecting key/value pairs for a variable's representation that will be logged. In the runtime lifecycle, this method is invoked during the variable-inspection phase where pysnooper enumerates attributes (keys) of an object and retrieves their current values to build a human-readable summary.
- By being an overridable instance method, it provides a single place for subclasses to customize how attribute values are retrieved (for example, to handle special containers, proxies, or to apply filtering) instead of inlining attribute access at each call site.

Reason for separation:
- Encapsulates attribute-access semantics so subclasses can override retrieval behavior without duplicating enumeration logic found in CommonVariable._items.
- Keeps a clear separation between "which keys to inspect" (_keys / _safe_keys), "how keys are formatted" (_format_key), and "how attribute values are retrieved" (_get_value).

## Args:
    main_value (object): The object from which an attribute is read. Any Python object is allowed.
    key (str): The name of the attribute to retrieve. Typically a string (e.g., entries obtained from __dict__ or __slots__), but any value acceptable to getattr may be passed.

## Returns:
    Any: The value of main_value.key, i.e., the result of getattr(main_value, key). There is no wrapper or normalization applied; returned value is the raw attribute result.

## Raises:
    AttributeError: If main_value does not have the named attribute and no fallback is provided (this is the standard getattr behavior).
    TypeError: If key is of an invalid type for attribute lookup (for example, not a string) — raised by getattr.
    Any exception raised by the attribute access itself (for example, from a property getter, descriptor, or __getattribute__/__getattr__ implementation) will propagate unchanged.

## State Changes:
Attributes READ:
    - None: this method does not read any attributes from self (no access to self.<attr> is performed).

Attributes WRITTEN:
    - None: this method does not modify any attributes on self.

## Constraints:
Preconditions:
    - main_value must be a valid Python object.
    - key should normally be a string corresponding to an attribute name produced by _keys (e.g., keys from __dict__ or entries declared in __slots__). Passing non-string keys is allowed only if getattr supports them, but doing so may raise TypeError.

Postconditions:
    - On success, returns the attribute value without modifying main_value or self.
    - On failure, an exception from getattr (AttributeError, TypeError, or any exception raised by the attribute access) is propagated to the caller.

## Side Effects:
    - No direct I/O or external service calls are performed by this method itself.
    - Indirect side effects are possible because attribute access may execute arbitrary user code:
        * Accessing a property, descriptor, or user-defined __getattribute__/__getattr__ may run arbitrary code (which can mutate global state, perform I/O, raise exceptions, etc.).
    - The method does not mutate main_value or any other object by itself; any mutation would be the result of code executed inside the attribute's getter.

## `pysnooper.variables.Keys` · *class*

## Summary:
Adapter for inspecting the keys of a mapping-like object in the variable-tracing framework. Provides helpers to enumerate keys, produce a short display label for each key, and fetch a value by key.

## Description:
Keys is a focused, implementation-light subclass of CommonVariable intended for use by a tracing/inspection framework. It encapsulates mapping-specific operations used by a generic inspector:
- enumerate the keys of a mapping-like object,
- render a compact, single-line textual label for each key suitable for trace output, and
- access the mapping's value for a given key.

Typical callers:
- The framework's variable-inspection machinery (the code that inspects values and recursively explores children) will obtain a Keys instance (via CommonVariable factory logic) when it determines a value is mapping-like.

Typical caller pattern (non-prescriptive):
- Call adapter._keys(main_value) to obtain the mapping's keys view (this method returns main_value.keys()).
- Iterate that iterable (optionally take a snapshot with list(...) if you need stability).
- For each key, call adapter._format_key(key) to obtain a short label, and adapter._get_value(main_value, key) to perform a single subscription lookup and obtain the child value.

Motivation and boundaries:
- Keeps mapping-specific logic separate from the generic traversal and pretty-printing code.
- Keys does not snapshot the mapping, enforce ordering, or provide thread-safety; callers should implement those behaviors externally if required.

Note about missing dependency:
- The repository's CommonVariable implementation is not available in the provided context. This documentation therefore does not assume CommonVariable's constructor signature or stored attributes; Keys itself defines no __init__ and introduces no new instance attributes beyond whatever CommonVariable provides.

## State:
- New attributes: None introduced by Keys.
- Inherited state: All instance state is defined by CommonVariable (not included here). Keys does not add fields or override __init__.
- For-call invariants:
    - Methods assume main_value is mapping-like: it implements .keys() and supports indexing main_value[key].
    - _format_key assumes utils.get_shortish_repr returns a text representation as per its contract; formatting wraps that text into a str.

## Lifecycle:
- Creation:
    - Keys is normally instantiated by the framework that manages CommonVariable-derived adapters. Because Keys does not declare its own __init__, construct it the same way other CommonVariable subclasses are constructed in your environment.
- Usage (recommended safe sequence):
    1. keys_iter = adapter._keys(main_value)     # returns main_value.keys()
    2. keys_snapshot = list(keys_iter)            # optional snapshot to avoid concurrent-mutation issues
    3. for key in keys_snapshot:
           label = adapter._format_key(key)
           value = adapter._get_value(main_value, key)  # single subscription lookup main_value[key]
           # inspect or record (label, value)
- Destruction:
    - No special cleanup. Keys has no context-manager protocol or close() method; standard garbage collection applies.

## Method Map (Mermaid flowchart):
flowchart LR
    S[_keys(main_value) -> main_value.keys()] --> ITER{iterate keys view/iterable}
    ITER --> FMT[_format_key(key)]
    ITER --> GET[_get_value(main_value,key) -> main_value[key]]
    FMT --> DISPLAY[display label (str)]
    GET --> CHILD[child value for further inspection]

## Methods and behavioral contracts

- _keys(self, main_value)
    - Purpose: Return the mapping's keys view / iterable to be iterated by the tracer.
    - Signature: (self, main_value)
    - Input:
        - main_value: expected to be mapping-like (implements .keys()).
    - Returns:
        - The direct result of main_value.keys() (e.g., dict_keys or another mapping's keys-view).
    - Errors:
        - AttributeError if main_value has no .keys() attribute.
        - Any exception raised by main_value.keys() will propagate.
    - Notes:
        - The returned object may be a dynamic view that reflects subsequent mutations of the mapping. If callers require a stable snapshot, call list(...) on the returned iterable.

- _format_key(self, key)
    - Purpose: Produce a compact, single-line, human-readable label for a key for inclusion in traces.
    - Signature: (self, key) -> str
    - Behavior:
        - Calls utils.get_shortish_repr(key) to obtain a short, single-line textual representation (see that function's contract).
        - Wraps the result with square brackets and returns the resulting str via '[{}]'.format(...).
    - Returns:
        - str: examples include "['a']" for key 'a' or "[42]" for key 42 (exact text depends on utils.get_shortish_repr).
    - Errors:
        - Any exception raised by utils.get_shortish_repr may propagate according to that function's documented behavior.
        - If utils.get_shortish_repr returns a non-text value that cannot be formatted into a str, a TypeError/ValueError may occur during formatting.

- _get_value(self, main_value, key)
    - Purpose: Return the value associated with key in main_value.
    - Signature: (self, main_value, key)
    - Behavior:
        - Performs a single subscription lookup and returns main_value[key].
    - Input:
        - main_value: mapping-like object supporting __getitem__ with key.
        - key: one of the keys returned by _keys(main_value), or otherwise valid for indexing.
    - Returns:
        - The object stored at main_value[key].
    - Errors:
        - KeyError if key is not present.
        - TypeError if main_value does not support the key's type for indexing.
        - Any exception raised by main_value.__getitem__ will propagate.

## Raises:
- Keys does not introduce new custom exceptions. It propagates exceptions from the underlying mapping and from utils.get_shortish_repr as described per-method above.
- Because Keys defines no __init__, any construction-time exceptions depend entirely on CommonVariable.__init__ (not documented here).

## Example (usage pattern recommended for callers)
- Safe iteration and inspection (pseudocode):
    1. keys_iter = adapter._keys(my_map)
    2. keys_snapshot = list(keys_iter)                # snapshot to avoid concurrent-mutation issues
    3. for key in keys_snapshot:
           label = adapter._format_key(key)          # e.g., "['a']" (no extra spaces)
           try:
               value = adapter._get_value(my_map, key)  # single subscription lookup
           except KeyError:
               value = '<missing>'
           # now record/display (label, value) or recursively inspect value

Notes and guidance:
- For deterministic ordering, use sorted(list(adapter._keys(main_value))) before iterating.
- Keys delegates formatting policy to utils.get_shortish_repr so labels are short and single-line by default; change the central utility if you need different formatting behavior.
- If callers require atomic snapshotting or thread-safety, implement those guarantees outside of Keys (for example, by copying the mapping or locking around iteration).

### `pysnooper.variables.Keys._keys` · *method*

## Summary:
Return the sequence/view of keys from the provided mapping-like object without modifying the Keys instance.

## Description:
This method obtains the keys of a mapping-like value by delegating to that value's keys() method. It is intended to be called during variable inspection/serialization when callers need to enumerate the entries of a mapping. In this class, _keys is used together with sibling methods that format and read individual entries (for example _format_key and _get_value) so callers can iterate keys, present them to the user, and retrieve corresponding values.

Known callers and context:
- Other methods in the same Keys implementation (e.g., higher-level traversal or formatting code) call _keys when enumerating child entries of a mapping-like variable during logging/inspection.
- It is invoked in the lifecycle step where a value is being inspected/expanded into its constituent key/value pairs for output.
This logic is factored into its own method so subclasses can override key enumeration semantics (for example to filter, sort, or transform keys) without changing the code that reads or formats individual values.

## Args:
    main_value (object): A mapping-like object that exposes a keys() method. Typical types are dict or any object implementing the Mapping protocol. No default.

## Returns:
    Iterable: The direct return value of main_value.keys(). Common concrete types include dict_keys for built-in dicts or any iterable/view type provided by the object's implementation. This value may be a dynamic view (it can reflect later mutations to main_value) depending on the mapping implementation.

## Raises:
    AttributeError: If main_value has no attribute named "keys" (i.e., is not mapping-like).
    TypeError or any exception raised by main_value.keys(): If keys exists but is not callable or if the call itself raises.

## State Changes:
    Attributes READ:
        - None (does not access any self.<attr> attributes)
    Attributes WRITTEN:
        - None (does not modify self)

## Constraints:
    Preconditions:
        - main_value must implement a keys() method that can be called without additional arguments.
    Postconditions:
        - The method returns the object produced by calling main_value.keys(); self is unchanged.

## Side Effects:
    - No I/O or external service interaction.
    - May return a live view object that reflects subsequent mutations to main_value (dependent on the mapping implementation), but the method itself performs no mutations.

### `pysnooper.variables.Keys._format_key` · *method*

## Summary:
Produce a short, display-safe string for a mapping key by embedding utils.get_shortish_repr(key) inside square brackets (e.g. "[key_repr]"). The method does not modify the Keys instance.

## Description:
- Known callers and context:
    - This is an internal helper on the Keys class used by the Keys formatting/printing pipeline when rendering mapping keys for human-readable traces, logs, or debug lines. In the Keys class, keys are obtained via _keys(main_value) (which returns main_value.keys()) and individual keys are often converted to their display form via this method before being combined into trace output.
    - Typical lifecycle: called at the moment a single mapping key is being prepared for display (for example, while iterating mapping keys to produce a per-key trace line).
- Reason for being a separate method:
    - Centralizes the visual policy for keys (square-bracket wrapper plus a short, single-line representation) so all key rendering is consistent and overrides can be implemented in subclasses without changing iteration or lookup logic.

## Args:
    key (Any):
        Any Python object representing a mapping key. The value is forwarded to utils.get_shortish_repr to produce the inner text.

## Returns:
    str:
        The formatted key string of the form "[INNER]" where INNER is the result of utils.get_shortish_repr(key).
        - Under normal operation INNER is a single-line str (get_shortish_repr guarantees removal of '\r' and '\n' from typical repr output).
        - Example outputs:
            * If key is the string 'a', typical result: "['a']"
            * If key is the integer 3, result: "[3]"
            * If get_shortish_repr returns its fallback literal due to a repr error, result: "[REPR FAILED]"
        - Implementation note: utils.get_shortish_repr is expected to return a str. If it does, the final result is a str. If it returns a non-str object, Python's formatting machinery will attempt to format that object; any exceptions from that formatting (e.g., TypeError) will propagate.

## Raises:
    - Any exception raised by utils.get_shortish_repr(key) will propagate (examples: TypeError, AttributeError, or other exceptions that may arise from normalization/truncation or user-provided repr callables).
    - Exceptions raised during formatting of the returned inner value into the "[{}]".format(...) expression (for example, if the inner object implements a __format__ that raises or returns an invalid type) will also propagate (commonly a TypeError).

## State Changes:
- Attributes READ:
    - None. This method does not read any self.<attr> fields.
- Attributes WRITTEN:
    - None. This method does not modify self or other passed-in objects.

## Constraints:
- Preconditions:
    - No required state on self. Caller must provide a key value. For predictable, safe behavior, the provided key should be representable by the representation functions used by utils.get_shortish_repr (i.e., typical repr functions that return str).
- Postconditions:
    - Returns a string beginning with '[' and ending with ']' containing whatever text utils.get_shortish_repr produced (subject to its guarantees: typically no CR/newline and optional normalization/truncation).
    - The Keys instance remains unchanged.

## Side Effects:
    - Directly: none (no I/O, no external calls, no mutation).
    - Indirectly: utils.get_shortish_repr may invoke user-supplied condition or representation callables; any side effects or exceptions from those callables will occur and propagate through this method.

### `pysnooper.variables.Keys._get_value` · *method*

## Summary:
Return the item from the provided container using the given key/index, without mutating the object state.

## Description:
This method performs a single subscription lookup: it retrieves and returns main_value[key]. Within the Keys class it complements the key enumeration method and is intended to be used when iterating keys (for example, by calling Keys._keys to obtain keys and then using this method to fetch each corresponding value).

Known callers and context:
    - No direct call sites are present in the provided snippet beyond the Keys class itself. The method is designed to be used in the phase where a container's keys are enumerated and each associated value must be retrieved for inspection or formatting (i.e., the variable-inspection/rendering stage of pysnooper).
    - It is implemented as a separate method to allow subclass customization (overriding lookup behavior) and to keep the key-enumeration (_keys), key-formatting (_format_key), and value-access responsibilities separated.

Why this is a separate method:
    - Encapsulates subscription semantics in one place so subclasses may override how values are retrieved (for example, to provide default values, to handle missing keys specially, or to support non-standard containers).
    - Keeps iteration and access logic decoupled for clearer code organization and testability.

## Args:
    main_value (object): The container from which to retrieve a value. Expected to support the subscription protocol (i.e., implement __getitem__). Typical concrete types are mappings (dict-like) or sequences (list/tuple).
    key (object): The index or key to use for subscription. For mappings this is a hashable key; for sequences this is typically an integer index.

## Returns:
    object: The result of main_value[key]. The exact type and value depend entirely on the container and key supplied. If successful, the return is the container's stored value for that key/index.

## Raises:
    KeyError: If main_value is a mapping and the provided key is not present.
    IndexError: If main_value is a sequence and the provided integer index is out of range.
    TypeError: If main_value does not support subscription (is not subscriptable) or if the key type is invalid for the container's __getitem__ implementation.
    Any exception raised by main_value.__getitem__(key) will propagate unchanged.

## State Changes:
    Attributes READ:
        - None: the method body does not access any self.<attr> fields.
    Attributes WRITTEN:
        - None: the method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - main_value must support subscription via main_value[key]. If this condition is not met, a TypeError (or another exception from __getitem__) will be raised.
        - key must be appropriate for main_value (e.g., an integer for sequences or an appropriate hashable key for mappings).
    Postconditions:
        - On successful return, the caller receives the value obtained by subscription; no attributes on self are changed.
        - On failure, whatever exception __getitem__ raises is propagated to the caller.

## Side Effects:
    - None within the pysnooper state: no I/O, no network calls, and no external mutations are performed by this method itself.
    - Note: If the underlying container's __getitem__ implementation performs side effects, those side effects will occur because this method invokes that implementation.

## `pysnooper.variables.Indices` · *class*

## Summary:
Adapter that represents the integer index positions of a sequence-like object as "keys" for the tracing/inspection framework; supports producing sliced views of those indices.

## Description:
Indices is a Keys subclass that adapts sequence semantics to the Keys adapter interface used by the tracing/inspection framework. While Keys is primarily written with mapping-like objects in mind (providing ._keys(), ._format_key(), and ._get_value() behaviors), Indices repurposes that interface to enumerate integer positions (0..len(main_value)-1) for sequence-like values such as list, tuple, str, or any object supporting len() and integer indexing.

Typical instantiation:
- Created by the framework's CommonVariable factory when a value is identified as sequence-like.
- Can be obtained manually only if your environment's CommonVariable allows direct construction.

Motivation and boundaries:
- Provides a minimal, focused adapter that exposes index positions in the same adapter-pattern used for mapping keys so the generic tracer code can treat sequence elements uniformly with mapping entries.
- It does not snapshot the underlying sequence, provide thread-safety, or guarantee immutability of the sequence; callers must enforce those behaviors externally if required.

## State:
- _slice (slice)
    - Type: slice
    - Default: slice(None) (class-level default; instances may override)
    - Valid values: any Python slice object
    - Invariant: _slice is expected to be a slice instance; adapters rely on applying this slice to the range of indices returned by _keys.
- Inherited state:
    - Any instance state from Keys / CommonVariable is preserved. Indices introduces no additional runtime attributes beyond _slice.
- Class invariants:
    - _slice must be a slice object.
    - Methods assume main_value is sized (len(main_value) is valid) and that integer indices produced by _keys are usable by callers to index main_value.

## Lifecycle:
Creation:
- No explicit __init__ is defined on Indices. Construct via the framework's factory or by standard construction if the CommonVariable base supports it.

Usage (recommended sequence):
1. Optionally obtain a sliced view: sliced_adapter = adapter[begin:end:step]
2. Call indices_iter = adapter._keys(main_value)
   - This returns a range object computed from len(main_value) and sliced by adapter._slice (see _keys below).
3. If a stable snapshot is required, call indices_snapshot = list(indices_iter).
4. Iterate indices_snapshot (or indices_iter) and for each index i:
    - label = adapter._format_key(i)    # inherited behavior e.g. "[0]"
    - value = main_value[i]             # perform single subscription lookup
    - inspect/record value
Notes:
- _keys computes and returns a sliced range object at call time using len(main_value). The returned range is independent of future mutations to main_value (it reflects the length at the moment _keys was invoked).
- To avoid race conditions caused by concurrent mutation of main_value between calling _keys and indexing, callers should snapshot (list(...)) if a consistent view is required.
Destruction:
- No special cleanup. Standard garbage collection applies.

## Method Map:
flowchart LR
    G[__getitem__(slice) ] --> DC[deepcopy(self)]
    DC --> SET[_slice = item on result]
    SET --> RET[return new Indices instance (sliced view)]
    K[_keys(main_value)] --> R[compute range(0, len(main_value))]
    R --> SL[apply self._slice -> range(...) sliced]
    SL --> OUT[return sliced range of integer indices]
    OUT --> ITERATE[caller iterates indices -> uses main_value[index] to fetch elements]

## Methods (behavioral contract)
- _keys(self, main_value)
    - Purpose: Return a sequence (range) of integer indices appropriate for indexing main_value.
    - Signature: (self, main_value)
    - Input:
        - main_value: an object for which len(main_value) is valid and whose elements are addressable by integer indices.
    - Behavior:
        - Computes base_range = range(len(main_value)).
        - Applies the adapter's slice: result = base_range[self._slice].
        - Returns the resulting range object. Example outcomes:
            - With default _slice slice(None), returns range(0, len(main_value)).
            - With slice(1, 5), returns range(1, min(5, len(main_value))) (normalized by range semantics).
    - Output:
        - A range instance representing integer indices.
    - Edge cases and errors:
        - TypeError if len(main_value) fails (main_value not sized).
        - ValueError if the slice is invalid (for example, step == 0) — this error arises from slicing the range and is propagated.
        - The returned indices are integers; using them to index main_value may raise IndexError or other exceptions from main_value.__getitem__.

- __getitem__(self, item)
    - Purpose: Produce a new Indices adapter that applies the provided slice to subsequent _keys() results.
    - Signature: (self, item) -> Indices
    - Input:
        - item: must be a slice instance.
    - Behavior:
        - Uses an assert to require item is an instance of slice (AssertionError if assertion is enabled and item is not a slice).
        - Creates a deep copy of self via deepcopy(self) to avoid sharing mutable adapter state.
        - Sets result._slice = item on the copied adapter and returns the copy.
    - Output:
        - A new Indices instance (deep-copied) whose _slice equals item.
    - Edge cases and errors:
        - AssertionError if item is not a slice and Python assertions are enabled.
        - Note: In optimized runs (python -O), assert statements are removed; passing a non-slice in that case will bypass the assertion and may set _slice to a non-slice value, violating invariants and leading to undefined behavior. Callers should always pass slice objects.
        - deepcopy may raise if adapter state is not deepcopy-able; such exceptions propagate.

## Raises:
- __getitem__:
    - AssertionError if item is not a slice (only when assertions are active).
    - Any exception raised by deepcopy (e.g., TypeError) if the instance is not deepcopy-able.
- _keys:
    - TypeError if len(main_value) fails.
    - ValueError if application of the slice to the range is invalid (e.g., step == 0).
    - IndexError (or other exceptions) may occur when callers use the produced indices to index main_value if the sequence has mutated or the indices are out of bounds.

## Example:
1. Obtain an adapter instance (usually from the framework):
    adapter = Indices()
2. Create a sliced adapter to visit indices 1..9 with step 2:
    sliced = adapter[1:10:2]
3. Compute the indices iterable for a sequence:
    indices_iter = sliced._keys(['a','b','c','d','e','f','g'])
    # indices_iter is a range instance, e.g., range(1,7,2) computed from len==7 and the slice
4. Snapshot and iterate safely:
    indices = list(indices_iter)
    for i in indices:
        label = sliced._format_key(i)   # e.g., "[3]"
        try:
            value = ['a','b','c','d','e','f','g'][i]
        except IndexError:
            value = '<missing>'
        # inspect (label, value)
5. No cleanup required.

Notes and recommendations:
- Because Indices reuses Keys' adapter interface, formatting of labels and element-access semantics are delegated to Keys/CommonVariable conventions (e.g., _format_key and subsequent indexing).
- To avoid deep-copy overhead when slicing adapters, prefer creating lightweight adapters or ensure adapter state is deepcopy-friendly.

### `pysnooper.variables.Indices._keys` · *method*

## Summary:
Produce a range of integer indices 0..len(main_value)-1 and apply the instance's slice selector, returning a sliced range without mutating the Indices object.

## Description:
This method builds the canonical index sequence for a sized container and then applies the Indices instance's configured slice to that sequence. It is the Indices-specific implementation of a Keys-like interface used by higher-level inspection logic to enumerate positions within sequence-like variables.

Known callers and context:
- No direct callers are shown in the provided snippet. Conceptually, this is invoked by variable-inspection code that requests "keys" for a value when that value is a sequence (e.g., lists, tuples, other sized containers).
- Typical lifecycle: an Indices instance is created (the class provides a default slice and supports creating modified instances via Indices.__getitem__), then the inspection framework passes a concrete container as main_value to _keys to obtain its index sequence for reporting or iteration.

Why this is a separate method:
- Encapsulates index-generation logic so different Keys implementations can override it.
- Keeps instance configuration (the slice selector) and index computation separate from other responsibilities (such as creating a sliced Indices instance).

## Args:
    main_value (object): Any object that implements __len__ (i.e., is a sized container). No other container protocol methods are required.

## Returns:
    range: A range object representing integer indices into main_value (0-based) after applying self._slice.
    - For len(main_value) == 0 the returned range is empty.
    - The range reflects the length at call time and does not track subsequent mutations of main_value.
    - The exact returned object is the result of slicing range(len(main_value)) with self._slice, using Python's standard slice semantics.

## Raises:
    TypeError: If main_value does not support len(main_value), calling len(main_value) will raise TypeError which is propagated to the caller.
    TypeError (possible): If self._slice is not a slice object, range(...)[self._slice] may raise TypeError. The Indices class sets a default slice and its __getitem__ enforces slice inputs, so this should not occur for well-formed Indices instances.

## State Changes:
    Attributes READ:
        self._slice
    Attributes WRITTEN:
        None — the method does not modify self or other attributes.

## Constraints:
    Preconditions:
        - self._slice should be a slice object (the Indices class defines _slice = slice(None) by default and __getitem__ enforces slice values).
        - main_value must be sized (implement __len__).

    Postconditions:
        - Returns a range whose iterated integers are valid 0-based indices for main_value at the moment of the call and which reflect the selection described by self._slice.
        - The Indices instance remains unchanged.

## Side Effects:
    - No I/O or external calls.
    - Only operations performed are calling len(main_value) and slicing a freshly created range object; no mutation of main_value or other external objects occurs.

## Examples:
    - Default (no slicing):
        Given main_value with length 4, returns range(0, 4) (iterates 0,1,2,3).
    - With a slice:
        If self._slice corresponds to slice(1, 4, 2), the returned range iterates the indices selected by that slice (e.g., 1, 3).
    - Empty / out-of-range:
        If the slice selects indices outside 0..len(main_value)-1, the returned range will be empty (standard Python slice clipping).
    - Negative indices / negative step:
        Negative slice indices or negative step are handled using Python's standard slicing semantics applied to range(len(main_value)).

### `pysnooper.variables.Indices.__getitem__` · *method*

## Summary:
Return a deep-copied Indices instance configured to represent the provided slice; the original instance is left unchanged.

## Description:
This implements the behavior when an Indices instance is indexed with square-bracket slice notation (e.g., indices[a:b:c]). It is called by Python's indexing machinery at the moment a slice is applied to an Indices object and is used during the setup/selection phase where callers build or refine index specifications.

Why this is a dedicated method:
- Provides a non-mutating, value-like slicing API: callers receive a separate Indices configured for the slice, enabling safe reuse and chaining.
- Centralizes slicing validation (the slice-type assertion) and copy semantics so other code can rely on consistent behavior.

Known caller context:
- Any user or internal code that writes expressions like some_indices[1:5] or some_indices[start:stop:step].
- No internal-only, hidden callers are required — the method is part of the public slicing protocol for the Indices type.

## Args:
    item (slice):
        The slice object provided by the caller. Must be an instance of slice (for example slice(1, 4, 2) or notation like 1:4:2). There is no further validation of slice indices, bounds or step performed here.

## Returns:
    Indices:
        A distinct object (deep copy) of the original Indices with its internal _slice attribute set to the provided slice.

        Details:
        - The returned object's _slice attribute is assigned directly to the provided item; as implemented, returned._slice is item (identity assignment).
        - Mutable sub-objects of self are recursively copied according to Python's copy.deepcopy semantics.
        - If deepcopy succeeds, the method returns the new Indices instance configured for the requested slice.

## Raises:
    AssertionError:
        If item is not an instance of slice. Note: Python assertions may be disabled when the interpreter runs with optimizations enabled (python -O), which would skip this check.

    Any exception raised by the deep-copy operation:
        deepcopy(self) may raise exceptions (for example TypeError or RecursionError) if parts of self cannot be deep-copied or copying recurses too deeply. Those exceptions are not handled here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - The method reads the state of self indirectly via deepcopy(self) during the copy process (this inspects attributes needed to construct the copy).

    Attributes WRITTEN:
        - The original self is not modified.
        - The method sets result._slice = item on the returned (deep-copied) Indices object. No other attributes on self or external objects are mutated.

## Constraints:
    Preconditions:
        - item should be a slice instance.
        - self must be deep-copyable; attributes referenced by self must be compatible with copy.deepcopy to avoid propagation of deepcopy-related exceptions.

    Postconditions:
        - self remains unchanged.
        - The returned object is a deep copy of self and is a different object (returned is not self).
        - returned._slice is exactly the provided item (identity assignment).
        - Any mutable structures inside self are duplicated per deepcopy semantics.

## Side Effects:
    - No I/O or network interactions.
    - Potential memory and CPU overhead from deepcopy.
    - No external objects are mutated by this method (mutations are limited to the returned copy).

## Implementation notes (for reimplementation):
    - Use an assertion or explicit type-check (isinstance(item, slice)) to validate the argument; be aware assertions can be disabled in optimized runs and thus do not substitute for a TypeError if strict enforcement is required.
    - Create a deep copy of self (e.g., copy.deepcopy(self)).
    - Assign the provided slice to the copy's _slice attribute (result._slice = item).
    - Return the copy.

## Examples:
    - indices = Indices()
      sliced = indices[1:10:2]
      # After call: sliced is a deep copy of indices; sliced._slice == slice(1, 10, 2)
      # The original indices object remains unchanged.

## `pysnooper.variables.Exploding` · *class*

## Summary:
A concrete BaseVariable that "explodes" an evaluated value into child (display_name, value) pairs by delegating to a specialized adapter: Keys for mappings, Indices for sequences, and Attrs for other objects.

## Description:
Exploding implements a decomposition strategy for a variable's runtime value: after the variable expression is evaluated by BaseVariable.items, Exploding._items inspects the evaluated object (main_value) and chooses an appropriate adapter to extract sub-items. It is a small delegating adapter whose sole responsibility is to route to the correct adapter and forward the call.

Scenarios for instantiation and callers:
- Instantiate Exploding when you need a BaseVariable subclass that expands or explores the contents of compound values (mappings, sequences, and objects) into multiple (display_name, value) pairs.
- Typical callers: the tracing/inspection framework that constructs Variable instances from user-specified expressions and then calls items(frame, normalize=...) on them. BaseVariable.items evaluates the expression and then calls Exploding._items with the evaluated main_value.
- Adapter factory expectation: the adapter classes Keys, Indices, and Attrs are available and accept (source, exclude) constructor arguments (Exploding instantiates them with those two arguments).

Motivation and responsibility boundary:
- Responsibility: choose the correct adapter based on the runtime type of main_value and return whatever that adapter produces.
- Boundary: Exploding does not itself enumerate keys/indices/attributes or format labels; it delegates all such work to Keys, Indices, or Attrs. It also does not perform evaluation of the variable expression — that is handled by BaseVariable.items.

## State:
Exploding defines no new instance attributes beyond those inherited from BaseVariable / CommonVariable. Relevant inherited state (refer to BaseVariable documentation) that Exploding relies on:
- source (str)
  - The compiled expression's original source text; forwarded to adapter constructors.
  - Constraint: must be a valid single Python expression (compile(...) performed by BaseVariable.__init__).
- exclude (tuple)
  - Tuple of names to omit from returned display names; normalized by BaseVariable.__init__ to a tuple.
  - Forwarded to adapter constructors.
- code, unambiguous_source, and fingerprint properties are inherited from BaseVariable but are not used directly by Exploding beyond being available to delegated adapters if needed.

Class invariants:
- Exploding instances inherit BaseVariable's invariants (e.g., fingerprint composed of (type(self), source, exclude)).
- Exploding guarantees that _items will dispatch to exactly one adapter per invocation (Mapping branch first, then Sequence, then Attrs).

## Lifecycle:
Creation:
- Instantiate Exploding via the same constructor signature as BaseVariable (required: source: str; optional: exclude iterable). BaseVariable.__init__ compiles source and normalizes exclude; because Exploding implements _items, it is instantiable directly.
Usage:
- Typical call flow:
  1. Tracer calls variable.items(frame, normalize=...) on an Exploding instance.
  2. BaseVariable.items evaluates the expression into main_value (or returns () if evaluation fails).
  3. BaseVariable.items calls Exploding._items(main_value, normalize).
  4. Exploding._items inspects main_value and delegates to one adapter:
       - If isinstance(main_value, Mapping) -> instantiate Keys(self.source, self.exclude) and call its _items(main_value, normalize)
       - Else if isinstance(main_value, Sequence) -> instantiate Indices(self.source, self.exclude) and call its _items(main_value, normalize)
       - Else -> instantiate Attrs(self.source, self.exclude) and call its _items(main_value, normalize)
  5. The iterable returned by the chosen adapter's _items is returned to the original caller (the tracer).
- Sequencing constraints: there is no required order of multiple calls; each invocation recomputes adapter instances and delegates anew.
Destruction:
- No special cleanup is required. Exploding instances are ordinary Python objects and are garbage-collected normally. Adapter instances created inside _items are ephemeral and are discarded after the delegated call returns.

## Method Map:
flowchart LR
    Call[_items(main_value, normalize)] --> IsMapping{isinstance(main_value, Mapping)?}
    IsMapping -- yes --> UseKeys[cls = Keys]
    IsMapping -- no --> IsSequence{isinstance(main_value, Sequence)?}
    IsSequence -- yes --> UseIndices[cls = Indices]
    IsSequence -- no --> UseAttrs[cls = Attrs]
    UseKeys --> InstKeys[inst = Keys(self.source, self.exclude)]
    UseIndices --> InstIndices[inst = Indices(self.source, self.exclude)]
    UseAttrs --> InstAttrs[inst = Attrs(self.source, self.exclude)]
    InstKeys --> CallKeys[return inst._items(main_value, normalize)]
    InstIndices --> CallIndices[return inst._items(main_value, normalize)]
    InstAttrs --> CallAttrs[return inst._items(main_value, normalize)]

## Behavior and edge cases:
- Type dispatch order:
  - Mapping test is performed first. If main_value satisfies Mapping, Keys is used even if it also satisfies Sequence.
  - Sequence test is the second branch; typical sequence-like objects (list, tuple, str, bytes, etc.) will match here if they are not Mappings.
  - All other objects fall through to Attrs.
- Common implications:
  - Strings and bytes are Sequence instances and therefore will be handled by Indices (i.e., exploded by index/character).
  - dict and other mapping-like objects are handled by Keys (i.e., exploded by mapping keys).
  - None and simple scalars (ints, floats) do not match Mapping nor Sequence and therefore are handled by Attrs. Attrs methods typically yield nothing for None (since getattr(None, '__dict__', ()) returns ()), so Exploding._items on None commonly returns an empty iterable.
- Adapter constructor contract:
  - Exploding assumes Keys, Indices, and Attrs accept (source, exclude) as positional constructor arguments. If an adapter's constructor signature differs, instantiation may raise TypeError.
- Forwarding of normalize:
  - The normalize boolean argument is forwarded unchanged to the chosen adapter's _items call; adapters are responsible for interpreting and honoring normalize (for example, using unambiguous_source when normalize is True).
- Exceptions propagation:
  - Exploding._items does not catch exceptions raised by adapter instantiation or by the adapter's _items or by iterating the returned iterable; these exceptions propagate to the caller. Typical exceptions include AttributeError, KeyError, IndexError, TypeError, and custom errors raised by adapter logic.
  - Exceptions raised earlier during expression compilation or evaluation are handled by BaseVariable (evaluation exceptions are converted to an empty tuple by BaseVariable.items), so Exploding._items only runs when evaluation succeeded.

## Raises:
- __init__ (inherited from BaseVariable):
  - SyntaxError or TypeError if source cannot be compiled into a single expression.
  - Any exceptions propagated by BaseVariable.__init__ (for example, errors while normalizing exclude).
- _items:
  - TypeError if instantiation of the selected adapter fails due to mismatched constructor signature.
  - Any exception raised by the selected adapter's _items implementation or by iterating the returned iterable (examples: AttributeError, KeyError, IndexError, ValueError, or user-defined exceptions) will propagate.
  - Note: BaseVariable.items will prevent _items from being called when evaluation of the expression raised an exception — in those cases, Exploding._items is not invoked.

## Example (prose):
1. Construction:
   - Create an Exploding variable for expression "user.profile" with an exclude list: instantiate Exploding("user.profile", exclude=("password",)).
   - BaseVariable.__init__ compiles the source and normalizes exclude; no further action is required on creation.

2. Runtime usage:
   - Tracer evaluates "user.profile" in a frame; suppose the result is a mapping (e.g., {'name': 'Alice', 'email': 'a@b'}).
   - BaseVariable.items calls Exploding._items(main_value, normalize=False).
   - Exploding detects the Mapping type and instantiates Keys(self.source, self.exclude); it calls Keys._items(main_value, normalize) and returns whatever Keys yields (for example, ("['name']", 'Alice'), ("['email']", 'a@b')), with any excluded names omitted by the adapter.

3. Edge case:
   - If the evaluated main_value is the string "hello", Exploding treats it as a Sequence and delegates to Indices; the adapter will present per-index items (e.g., "[0]" -> 'h', "[1]" -> 'e', ...).

Implementation note for reimplementers:
- The core logic is a type-dispatching delegation with this minimal shape:
  - if isinstance(main_value, Mapping): adapter_cls = Keys
  - elif isinstance(main_value, Sequence): adapter_cls = Indices
  - else: adapter_cls = Attrs
  - return adapter_cls(self.source, self.exclude)._items(main_value, normalize)
- Ensure you forward normalize and preserve the adapter-instantiation contract (source, exclude). Avoid swallowing exceptions from adapters; let the tracing framework decide how to handle adapter-level errors.

### `pysnooper.variables.Exploding._items` · *method*

## Summary:
Delegate enumeration of a value's child items to a type-specific adapter (mapping, sequence, or attribute adapter) and return that adapter's _items result; does not mutate the Exploding instance.

## Description:
This method is a thin dispatcher used by the variable-inspection/tracing machinery when an object needs to be "exploded" into child items for further inspection. It determines the appropriate adapter class based on the runtime type of main_value:
- If main_value is an instance of Mapping, uses the mapping adapter (Keys).
- Else, if main_value is an instance of Sequence, uses the sequence adapter (Indices).
- Otherwise, uses the attribute adapter (Attrs).

It constructs the chosen adapter by passing self.source and self.exclude to the adapter's constructor and then forwards the call to that adapter's _items method, passing through the main_value and normalize flag.

Known callers and invocation context:
- Higher-level variable-tracing or inspection routines that need to enumerate child items of a value (for example, code that implements recursive traversal/pretty-printing of variables). This method is invoked during the "explode" or "enumerate children" stage of the trace lifecycle where a value is being expanded into labeled child entries.
- The method exists separately (rather than inlined) so the type-dispatch logic and adapter instantiation are centralized in one place and the detailed per-type enumeration behavior is implemented by Keys, Indices, and Attrs. This keeps Exploding._items minimal and defers mapping/sequence/attribute semantics to their respective adapters.

## Args:
    main_value (Any): The value to enumerate children for. Expected to be either:
        - Mapping-like (implements .keys() and __getitem__) — will be handled by Keys,
        - Sequence-like (has __len__ and integer indexing) — will be handled by Indices,
        - or an arbitrary object — handled by Attrs.
    normalize (bool, optional): A boolean flag forwarded verbatim to the adapter's _items method. The meaning and effect of this flag are defined by the adapter implementations; this method does not inspect or alter it. Default: False.

## Returns:
    Any: Exactly the value returned by the invoked adapter's _items(main_value, normalize). The concrete return type and semantics are defined by Keys._items, Indices._items, and Attrs._items; this method only forwards and returns that result.

## Raises:
    - Any exception raised during adapter class selection, instantiation, or by the adapter._items call is propagated unchanged. Examples include, but are not limited to:
        * TypeError if adapter construction or adapter._items expects different input types,
        * Any exception (AttributeError, KeyError, IndexError, ValueError, etc.) raised by code executed within the adapter's _items implementation or by user code invoked while enumerating/accessing children.
    - Note: isinstance checks themselves do not raise; only adapter code or constructor may raise.

## State Changes:
    Attributes READ:
        - self.source
        - self.exclude
    Attributes WRITTEN:
        - None. The method does not assign to any self.<attr> or mutate the Exploding instance.

## Constraints:
    Preconditions:
        - The Exploding instance must have readable attributes source and exclude (their types/meanings are determined by the surrounding framework).
        - main_value should be one of the categories the adapters expect (mapping-like, sequence-like, or arbitrary object) for correct adapter behavior; otherwise the chosen adapter's _items may raise.
    Postconditions:
        - The Exploding instance is unmodified by this call.
        - The method returns whatever the chosen adapter's _items returns (no post-processing is performed here).
        - The normalize flag is passed unchanged to the adapter.

## Side Effects:
    - Side effects depend entirely on the adapter._items implementation and any user code invoked while enumerating or accessing child values (for example, property accessors, __getitem__ implementations, or descriptor code). This method itself performs no I/O and does not perform direct mutations of objects other than what adapter code or attribute/index accessors may do.
    - Instantiating the adapter may execute its constructor (inherited from CommonVariable), which could have side effects depending on that constructor's implementation; those are not introduced by this method itself.

## Implementation notes for reimplementers:
    - Recreate the exact type-dispatch order: test Mapping first, then Sequence, then fallback to Attrs.
    - Use the instance attributes source and exclude when constructing the adapter: cls(self.source, self.exclude).
    - Forward the normalize boolean unchanged: return cls(...)._items(main_value, normalize).
    - Do not attempt to interpret or modify the adapter's return value; leave adapter behavior responsible for enumerating and formatting child items.

