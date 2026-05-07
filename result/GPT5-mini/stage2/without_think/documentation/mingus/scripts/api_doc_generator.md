# `api_doc_generator.py`

## `scripts.api_doc_generator._is_class` · *function*

## Summary:
Predicate that returns True when a candidate is a class suitable for documentation/introspection: the candidate must be a subclass of object and must not inherit from any type listed in the module-level _SKIPPED_CLASS_SUPERTYPES.

## Description:
Tiny utility used to filter module members during introspection or API-documentation generation.

Known callers (typical usage):
    - Not discoverable in the supplied fragment. Commonly called by module-level scanner or indexer routines that iterate over a module's members (for example, an inspect.getmembers loop) and apply this predicate to select only classes that should be documented.

Why this is a separate function:
    - Encapsulates the policy for what counts as a documentable class in one place: it enforces (1) the object is a class (subclass of object) and (2) the class does not derive from any excluded supertypes. Centralizing this logic avoids scattered issubclass checks and makes it easy to change the exclusion policy by updating _SKIPPED_CLASS_SUPERTYPES.

## Args:
    cls (type): A class object (a Python type). 
        - The implementation expects a single class object; passing an instance or other non-type will cause a TypeError from issubclass.
        - Do not pass a tuple as the first argument. The second argument to issubclass (the classinfo) is handled via the module-level _SKIPPED_CLASS_SUPERTYPES.

Module-level dependency:
    - _SKIPPED_CLASS_SUPERTYPES (must be defined in the same module): either a single class or a tuple of classes that should be considered "skipped".
    - _SKIPPED_CLASS_SUPERTYPES must be valid as the second argument to Python's issubclass (i.e., a class or a non-empty tuple of classes). An empty tuple is not valid and will cause issubclass to raise TypeError.

## Returns:
    bool — True if and only if:
        1) cls is a subclass of object; and
        2) cls is not a subclass of any class present in _SKIPPED_CLASS_SUPERTYPES.

    Otherwise returns False.

## Raises:
    NameError:
        - If _SKIPPED_CLASS_SUPERTYPES is not defined in the module at call time, a NameError will occur due to the unresolved name.

    TypeError:
        - If cls is not a class object (for example, an instance or arbitrary object), issubclass(cls, ...) raises TypeError.
        - If _SKIPPED_CLASS_SUPERTYPES exists but is not a class or a (non-empty) tuple of classes, issubclass(cls, _SKIPPED_CLASS_SUPERTYPES) will raise TypeError. Notably, an empty tuple is invalid classinfo and causes TypeError.

## Constraints:
Preconditions:
    - The module must define _SKIPPED_CLASS_SUPERTYPES and it must be valid classinfo (a class or a non-empty tuple of classes).
    - Callers should pass an actual class object (a type) as cls.

Postconditions:
    - No global state is mutated.
    - The function returns a boolean when inputs are valid.

## Side Effects:
    - None. The function performs pure computation and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    Start --> CheckSubclassObject{issubclass(cls, object)?}
    CheckSubclassObject -- No --> ReturnFalse1[Result: False]
    CheckSubclassObject -- Yes --> CheckSkipped{issubclass(cls, _SKIPPED_CLASS_SUPERTYPES)?}
    CheckSkipped -- Yes --> ReturnFalse2[Result: False]
    CheckSkipped -- No --> ReturnTrue[Result: True]

## Examples:
    - Normal positive case:
        If the module defines _SKIPPED_CLASS_SUPERTYPES = (FrameworkBase,), and MyClass does not inherit from FrameworkBase, then the predicate yields True for MyClass.

    - Normal negative case:
        If MyHelper subclasses FrameworkBase and FrameworkBase is listed in _SKIPPED_CLASS_SUPERTYPES, the predicate yields False for MyHelper.

    - Built-in classes:
        Built-in types (for example, list or dict) are subclasses of object and will yield True unless their type or one of their supertypes appears in _SKIPPED_CLASS_SUPERTYPES.

    - Common error cases:
        - Passing an instance (for example, an integer or object instance) as cls will cause TypeError.
        - If the module omitted defining _SKIPPED_CLASS_SUPERTYPES or defined it incorrectly (for example, as an empty tuple), invoking this predicate will raise NameError or TypeError respectively.

## `scripts.api_doc_generator._is_method` · *function*

## Summary:
Return True when the object's exact runtime type is one of the types listed in the module-level _METHOD_TYPES collection; otherwise return False.

## Description:
This small predicate encapsulates a single responsibility: testing whether an object's precise runtime type is included in the module-level collection named _METHOD_TYPES.

Known callers:
- No specific callers are present in the provided component context. Typical usage is inside an API/documentation generation pipeline or an object-inspection routine that filters module/class members to detect functions or methods for documentation output.

Why this logic is factored out:
- Encapsulates the membership check against a centralized _METHOD_TYPES collection so callers don't directly depend on the concrete set of types or the membership semantics. This keeps the type-testing policy in one place and makes it easier to change which runtime types count as "methods" without altering callers.

## Args:
    obj (any): The object to test. Any Python object is accepted; the function only uses Python's built-in type() on it.

Notes on arguments:
- There are no constraints on obj itself (it may be None, a bound method, function, builtin, class, instance, etc.). The behavior depends on whether type(obj) is found in _METHOD_TYPES.

## Returns:
    bool: True if type(obj) is a member of the _METHOD_TYPES collection; False otherwise.

All possible outcomes:
- True: the object's exact type matches one of the entries in _METHOD_TYPES.
- False: the object's exact type is not contained in _METHOD_TYPES.

## Raises:
- NameError: If the global name _METHOD_TYPES is not defined in the module at runtime, referencing it will raise a NameError when the function is executed.
- TypeError: If the global _METHOD_TYPES exists but does not support membership testing with the 'in' operator (for example, if _METHOD_TYPES is a non-iterable type object), evaluating "type(obj) in _METHOD_TYPES" may raise a TypeError. Any exception produced by the membership operation will propagate to the caller.

## Constraints:
Preconditions:
- The module must define a global variable named _METHOD_TYPES accessible at call time.
- _METHOD_TYPES should be an iterable (e.g., tuple, list, set, frozenset) of types or type objects so that membership testing with a type value is meaningful.

Postconditions:
- No global state is mutated by this function.
- The function returns a boolean indicating membership; no other side effects occur when preconditions are met.

## Side Effects:
- None intrinsic to the function when preconditions are met. It performs no I/O, does not mutate global variables, and makes no external service calls.
- If _METHOD_TYPES is missing or malformed, the function will raise errors as documented above (these are not intentional side effects but runtime failures).

## Control Flow:
flowchart TD
    Start --> GetType[type(obj)]
    GetType --> CheckMember{type in _METHOD_TYPES?}
    CheckMember -->|Yes| ReturnTrue[return True]
    CheckMember -->|No| ReturnFalse[return False]

## Examples:
Typical (conceptual) usage and behavior descriptions — these are prose examples, not code dumps.

- Typical setup:
    A module defines _METHOD_TYPES as an iterable of runtime types considered "callable methods" for documentation purposes (for example, bound method types and function types). The API documentation generator then calls this predicate for each discovered member to decide whether the member should be treated as a method in generated docs.

- Expected true case:
    If _METHOD_TYPES contains the exact runtime type of a bound method (for example, the method type used by the runtime), calling this predicate on a bound method object yields True and the generator will include that member in the "methods" section.

- Expected false case:
    If _METHOD_TYPES does not include the type of a given object (for example, the object is an integer, class object, or instance), the predicate returns False and the object will not be categorized as a method.

- Error handling:
    If the module forgot to define _METHOD_TYPES, calling this function will raise NameError; callers that rely on this predicate should either ensure _METHOD_TYPES is defined before invoking it or catch exceptions and handle them (for example, by treating missing configuration as "no types match" or by failing fast with a clear error message).

## `scripts.api_doc_generator.Documize` · *class*

*No documentation generated.*

### `scripts.api_doc_generator.Documize.__init__` · *method*

## Summary:
Initializes the Documize instance by delegating module setup to the instance method responsible for configuring the object's module state.

## Description:
This constructor is invoked when a Documize object is instantiated; its role is the construction-time setup of module-related state. It performs no module parsing itself but immediately delegates to self.set_module(module_string), so all module validation, importing, or state initialization is performed by that method.

Known callers and lifecycle stage:
- Called automatically when client code constructs a Documize instance (e.g., Documize('some.module')).
- Typical invocation occurs at object-creation time as the first step in an API documentation generation pipeline where the instance must be bound to a target module.

Rationale for being a separate method:
- The constructor delegates to set_module so that module-selection and validation logic are centralized and reusable (set_module can be called later to change the target module without re-instantiating the object). This keeps __init__ minimal and avoids duplicating module-setup code.

## Args:
    module_string (str): A string identifying the target module (default: ''). Expected to be a module path or name understood by the class's set_module implementation. The constructor does not coerce types; non-string values will be forwarded to set_module and may lead to errors there.

## Returns:
    None: As with all constructors, __init__ does not return a value.

## Raises:
    AttributeError: If the instance does not have a callable set_module attribute (i.e., set_module is missing or not bound), Python will raise AttributeError when attempting the call.
    Any exception raised by self.set_module(module_string): Exceptions produced by set_module (for example, ImportError, ValueError, TypeError, or custom errors) are propagated to the caller.

## State Changes:
Attributes READ:
    - None explicitly read by this method body other than accessing the bound method attribute self.set_module.

Attributes WRITTEN:
    - None directly assigned in __init__. Any changes to the instance state (attributes added, updated, or cleared) are performed by the invoked set_module method.

## Constraints:
Preconditions:
    - self must be a valid Documize instance (i.e., __init__ should be invoked on an instance or during instantiation).
    - module_string should be a string representing the module to bind to; passing other types is allowed syntactically but may cause set_module to raise.

Postconditions:
    - After successful return, the instance's module-related state is configured according to set_module's behavior (exact attributes and invariants depend on set_module's implementation).
    - If set_module raises, the constructor will not complete normally and the instance may be left uninitialized or partially initialized per set_module's side effects.

## Side Effects:
    - Delegates to self.set_module(module_string). Any I/O, imports, filesystem accesses, network calls, or mutations of objects outside self are possible only via set_module and are not performed directly by __init__ itself.

### `scripts.api_doc_generator.Documize._filter_dunder_attributes` · *method*

## Summary:
Return a lazy iterator of attribute names filtered to exclude most Python "dunder" names while preserving a configurable whitelist; does not modify object state.

## Description:
This method is a focused filter used during API documentation generation. Known callers and context:
- process_element_recursively: iterates over attributes of a module/class (typically the result of dir(element_evaled)) and calls this method to obtain the subset of attribute names that should be documented. process_element_recursively is invoked from generate_module_wikidocs and from generate_callable_wikidocs during recursive traversal of a module or class.
Lifecycle stage: invoked during the documentation generation pipeline when Documize enumerates members of a module or class to decide which members to document.

Why this is a separate method:
- Encapsulates the policy for which "dunder" (double-underscore) names are considered meaningful for documentation (e.g., __init__, __repr__) and which should be ignored.
- Keeps the recursion/iteration logic in process_element_recursively concise and makes it easy to override or test the filtering policy independently.
- Produces a lazy generator, avoiding intermediate lists and preserving iteration order from the input iterable.

## Args:
    attrs (iterable[str]): An iterable of attribute names (strings) to filter. Typical callers pass the result of dir(obj), but any iterable of strings is accepted.

## Returns:
    generator[str]: A generator that yields attribute names from the input iterable in the same order they are encountered, but only those that:
        - do not start with '__' (non-dunder names), or
        - are present in self._ALLOWED_DUNDER_METHODS (an explicit whitelist of allowed dunder names).
    If the input iterable is empty, the generator yields nothing.

## Raises:
    AttributeError: If an element of attrs does not implement startswith (i.e., is not string-like), calling attr.startswith('__') may raise AttributeError.
    TypeError: If an element of attrs is unhashable, membership testing (attr in self._ALLOWED_DUNDER_METHODS) may raise TypeError.
    (Note: these exceptions are not explicitly caught by this method; they propagate to the caller.)

## State Changes:
    Attributes READ:
        self._ALLOWED_DUNDER_METHODS — consulted to decide whether a dunder name is allowed.
    Attributes WRITTEN:
        None — this method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - attrs should be an iterable of strings (the method assumes each element supports startswith and is hashable).
        - self._ALLOWED_DUNDER_METHODS must be an iterable container (typically a set) of strings; the class defines it at class level.
    Postconditions:
        - Returns a generator that will yield each attr from attrs for which (not attr.startswith('__')) OR (attr in self._ALLOWED_DUNDER_METHODS) evaluates True.
        - No mutation of attrs or self is performed.

## Side Effects:
    - No I/O performed.
    - No external service calls.
    - No mutation of objects outside self (aside from potential exceptions propagating to caller).
    - The returned generator is lazy; side effects produced by consumers of the generator (if any) occur when the generator is iterated.

### `scripts.api_doc_generator.Documize.process_element_recursively` · *method*

## Summary:
Recursively iterates over the public (and allowed dunder) members of a provided object and dispatches each member to the appropriate documentation generator, updating the object's collected documentation lists on self.

## Description:
- Known callers and lifecycle context:
    - generate_module_wikidocs calls this method to enumerate all members of the top-level module (self.module) when building the module documentation.
    - generate_callable_wikidocs calls this method when it detects a class-like object; in that case it descends into the class to document its members (this method is therefore used both for module-level traversal and for recursive traversal into nested classes).
    - The method also calls itself recursively when generate_callable_wikidocs finds a class and invokes this method for the nested class scope.
    - Typical pipeline stage: invoked during the documentation generation phase (output_wiki -> generate_module_wikidocs) to collect documentation snippets for functions, classes, and attributes.

- Why this is a separate method:
    - It encapsulates the recursive traversal logic and the decision dispatching (callable vs non-callable) so the recursive behavior can be reused from both module-level and class-level entry points without duplicating traversal or filtering logic.
    - Separating traversal from rendering keeps the responsibilities clear: this method focuses on iteration and delegation, while generate_* methods handle formatting and list appending.

## Args:
    element_string (str):
        - Full dotted name string representing the element being traversed (e.g., 'mingus.core', or 'mingus.core.SomeClass').
        - Must be a name that, when used in eval(expression) with attribute accesses appended, resolves in the runtime globals/locals accessible to eval.
    element_evaled (object):
        - The actual Python object (module, class, or instance) whose members will be inspected via dir(element_evaled).
        - Must be compatible with dir() (almost any object is).
    is_class (bool, optional):
        - Flag indicating whether the current element is being treated as a class (defaults to False).
        - When True, downstream generator methods will produce class/method-style directives instead of module/function-style directives.

## Returns:
    None
    - The method does not return a value; it performs side-effecting updates to self (see State Changes).

## Raises:
    - Any exception raised by eval('{0}.{1}'.format(element_string, element)):
        * NameError: if the base name in element_string is not defined in the evaluation context.
        * AttributeError: if the attribute named by element does not exist on the resolved object.
        * Other exceptions that can arise during attribute access (for example, descriptors or properties that raise when accessed) will propagate.
    - Exceptions raised by called helper methods:
        * Any exception raised by self._filter_dunder_attributes, self.generate_non_callable_docs, or self.generate_callable_wikidocs will propagate to the caller.
    - No exceptions are explicitly caught inside this method; callers should expect propagation.

## State Changes:
- Attributes READ:
    - No direct reads of simple self.<attr> fields within this method body, but it calls self._filter_dunder_attributes() (method) which uses self._ALLOWED_DUNDER_METHODS (class attribute).
- Attributes WRITTEN (indirectly via called generators):
    - self.functions: appended-to by generate_function_wikidocs (via generate_callable_wikidocs) when function docs are generated.
    - self.classes: appended-to when class-level documentation blocks are generated.
    - self.attributes: appended-to by generate_non_callable_docs for non-callable attributes at module-level (or to classes list when documenting class attributes).
  Note: those modifications occur inside generate_non_callable_docs / generate_callable_wikidocs / generate_function_wikidocs, which this method invokes.

## Constraints:
- Preconditions:
    - element_string must correspond to a runtime-resolvable root name for eval to succeed (e.g., previously imported module name or otherwise available identifier).
    - element_evaled should represent the same object referenced by element_string (consistency between the string and the object is assumed but not enforced).
    - The caller must ensure the evaluation environment (globals/locals) used by eval includes the names referenced by element_string; the method uses plain eval in the current execution environment.
- Postconditions:
    - After successful completion, every member name yielded by self._filter_dunder_attributes(dir(element_evaled)) will have been passed to either generate_non_callable_docs or generate_callable_wikidocs, and any documentation fragments produced by those generators will have been appended to the appropriate lists on self (functions, classes, attributes).
    - No return value is produced.

## Side Effects:
- Evaluates attribute access using eval on strings constructed from element_string and member name. This performs attribute lookup and can execute descriptor/property code.
- Mutates self by appending documentation strings to self.functions, self.classes, or self.attributes via the invoked generator methods.
- May perform deep recursion into nested classes (via generate_callable_wikidocs calling this method), potentially visiting many objects.
- No file I/O or external network calls are performed in this method itself; side effects are limited to in-memory mutations and any effects triggered by property/descriptor access during eval.

## Behavior notes and edge cases:
- Dunder filtering: member names come from dir(element_evaled) filtered by self._filter_dunder_attributes, so most double-underscore members are skipped unless explicitly allowed in self._ALLOWED_DUNDER_METHODS.
- Callable detection: uses Python's callable() builtin to decide whether to treat a member as callable; some callables (e.g., objects implementing __call__) will be treated as callable, and some descriptors may execute on attribute access.
- The method does not guard against name collisions or malformed element_string entries; incorrect element_string values can lead to NameError or other runtime exceptions from eval.

### `scripts.api_doc_generator.Documize.generate_module_wikidocs` · *method*

## Summary:
Assembles and returns a reStructuredText (RST) module documentation string by resetting internal doc state, optionally including the module docstring, recursively processing module elements to populate internal lists, sorting collections, and concatenating class, attribute, and function fragments into a final RST document.

## Description:
This method is used during the documentation-generation pipeline to produce the final RST text for a single Python module. Typical callers invoke this method when a Documize instance is prepared with:
- self.module_string set to the dotted module name (for headers and module directive)
- self.module set to the actual module object to document
- other internal lists and state that process_element_recursively expects (these are cleared by reset())

Lifecycle stage / pipeline step:
- Called after the Documize instance has been configured for a target module and before the returned RST string is written to disk or aggregated into an index.
- It orchestrates calling reset() -> process_element_recursively(...) and then constructs the textual output.

Why this is a separate method:
- It encapsulates the end-to-end assembly of a module-level RST document (header generation, optional module docstring inclusion, invoking recursive processing, deterministic ordering via sorting, and concatenation of fragments). Separating this logic keeps higher-level orchestration distinct from lower-level element-processing routines and makes it easy to generate a module document in one call.

## Args:
This method takes no direct arguments; it relies on state configured on self:
- self.module_string (str): dotted name used to build the module directive and section header; must be present and non-empty for meaningful output.
- self.module (module-like object): the module whose __doc__ and members will be inspected and processed.

## Returns:
- str: A single reStructuredText-formatted string representing the module documentation. Typical structure:
    - ".. module:: <module_string>" directive
    - A header line of '=' repeated to match the module_string length, the module_string itself, and another header line
    - Optional module-level docstring contents (if present)
    - Concatenated documentation fragments produced by process_element_recursively, followed by any class, attribute, and function fragments stored in self.classes, self.attributes, and self.functions (in that order)
    - A footer separator ('----') and a "Back to Index" doc link
- Edge cases:
    - If self.module.__doc__ is None, that section is omitted.
    - If any of self.classes, self.attributes, or self.functions are empty, their sections simply add nothing to the result.

## Raises:
- AttributeError: If required attributes are missing on self (for example, if self.module_string or self.module do not exist), normal attribute access will raise AttributeError.
- Any exception raised by called methods:
    - Exceptions raised by self.reset() or self.process_element_recursively(...) (such as TypeError, ValueError, or custom exceptions) propagate unchanged.
- No exceptions are explicitly raised by this method itself.

## State Changes:
Attributes READ:
- self.module_string: read to produce the module directive and header.
- self.module: read to access the module __doc__ (if present) and to pass it into process_element_recursively.
- self.classes: iterated to append class fragments to the result (read).
- self.functions: read and sorted; used to append function fragments to the result.
- self.attributes: read and sorted; used to append attribute fragments to the result.
- methods: self.reset() and self.process_element_recursively(...) are invoked (reads and executes those behaviors).

Attributes WRITTEN / MUTATED:
- self.reset(): called at method start; it is expected to modify internal state (clear lists, reset accumulators). The net effect is the module-document generation state is reinitialized.
- self.functions: sorted in-place (mutation). The list may also be populated by process_element_recursively.
- self.attributes: sorted in-place (mutation). The list may also be populated by process_element_recursively.
- self.classes: may be populated or mutated by process_element_recursively (this method itself does not mutate classes directly beyond iterating).
- Any other internal state that self.reset() or self.process_element_recursively modifies (these methods control how lists and fragments are filled).

## Constraints:
Preconditions:
- self.module_string must be a string containing the module name (used to generate header and directive). If empty or missing, the produced header will be based on its length (possibly zero-length) which is likely undesired.
- self.module must be set to a valid module-like object (with __doc__ attribute and members) because the method accesses self.module.__doc__ and passes self.module into process_element_recursively.
- self.reset and self.process_element_recursively methods must be implemented and able to handle the provided self.module_string and self.module values.

Postconditions:
- Returns the assembled RST string as described in Returns.
- self.functions and self.attributes will be sorted (their in-place ordering is deterministic after the call).
- Internal doc-collection lists (self.classes, self.functions, self.attributes, and any others reset/populated by process_element_recursively) will reflect the module's processed contents after the method returns.

## Side Effects:
- No file or network I/O is performed directly by this method (it only returns a string). Writing the returned string to disk or further publishing is the caller's responsibility.
- It mutates the object's internal state via reset() and by sorting/mutating lists (self.functions, self.attributes, possibly self.classes).
- It calls other instance methods which may have their own side effects (e.g., adding to lists, inspecting modules). Any exceptions from those calls propagate outward.

### `scripts.api_doc_generator.Documize.generate_non_callable_docs` · *method*

## Summary:
Generates and appends a reStructuredText fragment describing a non-callable attribute (data/member) for inclusion in the module/class wiki output; updates the object's attribute- or class-doc lists.

## Description:
This method constructs a small reStructuredText documentation block for a non-callable element discovered by reflection and appends it to either self.attributes (for module-level data) or self.classes (for attributes of a class). Typical callers:
- process_element_recursively: invoked when iterating over members discovered via dir() and selecting non-callable values.
- generate_module_wikidocs (indirect): the top-level module doc generator calls process_element_recursively which in turn calls this method.
- output_wiki (indirect): ultimately triggers this as part of generating the full module documentation.

This logic is separated into its own method to keep the reflection/traversal code (process_element_recursively) focused on member discovery and to centralize the formatting/append behavior for non-callable members. That makes it easier to modify formatting rules (for module vs. class attributes) without changing traversal logic.

## Args:
    module_string (str): Dotted module/class path string used by caller (not directly used in output formatting by this method, but provided for context).
    element_string (str): The attribute/member name (e.g., 'VERSION' or 'foo'). Must be a non-empty string (the code indexes element_string[0]).
    evaled (any): The evaluated value of the attribute (the result of evaluating module_string + "." + element_string). Any Python object; its type and repr() are used in the output.
    is_class (bool): If False (default), the produced doc fragment is treated as module-level data and appended to self.attributes. If True, the fragment is treated as a class attribute and appended to self.classes.

## Returns:
    None
    The method returns nothing (implicitly returns None). Its effect is purely to append a formatted string to one of the object's lists when the conditions are satisfied.

## Raises:
    IndexError: If element_string is an empty string (element_string[0] is accessed without a guard).
    Any exception raised by repr(evaled): If the evaluated object's __repr__ implementation raises, this method will propagate that exception.
    Any exception raised by str(type(evaled)): Very unlikely, but if type() or str() raises for a given object, the exception will propagate.
    Note: The method does not explicitly raise on module-level values — it simply skips values whose type is types.ModuleType or whose name starts with '_'.

## State Changes:
Attributes READ:
    self.attributes (to append to it when is_class is False)
    self.classes (to append to it when is_class is True)

Attributes WRITTEN:
    self.attributes (may be modified via append)
    self.classes (may be modified via append)

The method does not read or modify other instance attributes.

## Constraints:
Preconditions:
    - element_string must be a non-empty string (the method indexes element_string[0]).
    - The caller should pass the actual evaluated value in evaled (commonly obtained via evaluation of module_string + "." + element_string).
    - The caller expects that generate_module_wikidocs or reset() has been invoked at some point to initialize instance lists; if not, appending will modify class-level lists (Documize.attributes / Documize.classes) instead of instance-level lists.

Postconditions:
    - If element_string does not start with '_' and evaled is not a ModuleType, then a reStructuredText fragment describing the attribute will have been appended to either self.attributes (is_class False) or self.classes (is_class True).
    - If the above condition is not met, no mutation occurs.
    - No value is returned.

## Side Effects:
    - Mutates internal lists: either self.attributes or self.classes (append).
    - Invokes repr(evaled) and str(type(evaled)) to produce human-readable type and value representations; if those dunder methods have side effects, those will execute.
    - No file, network, or other external I/O is performed.
    - No other objects are mutated by this method (beyond the possible side effects of repr/type on the evaled object itself).

### `scripts.api_doc_generator.Documize.generate_callable_wikidocs` · *method*

## Summary:
Determines whether a discovered member is a method, a class, or a class-like object within the same module namespace and updates the Documize instance's collections (functions/classes) accordingly; may recurse into class members for further documentation generation.

## Description:
This method is called during the module/class member inspection phase of the documentation pipeline. Known callers:
- Documize.process_element_recursively — invoked for each member discovered by dir() over a module or class; this method receives the member name and evaluated object and decides how to document it.
- Indirectly used during Documize.generate_module_wikidocs when process_element_recursively walks a module.

Typical lifecycle stage:
- Called while traversing members of a module or class to categorize and emit reStructuredText directives (function/method or class) and to recurse into class members.

Why this is its own method:
- Encapsulates the decision logic that distinguishes callable methods (documented as functions/methods) from classes and class-like objects that should be recursed into. Keeping this logic separate keeps process_element_recursively simple (it only decides callable vs non-callable) and centralizes the policy for how a callable or class-like member is handled, including appending results to the correct Documize lists and initiating recursion.

## Args:
    module_string (str):
        Dot-separated module path prefix used to qualify nested members (e.g., 'mypkg.mymodule').
        This is used when recursing into nested classes to build the new element_string passed to recursion.
    element_string (str):
        The member name (attribute name) being processed (e.g., 'MyClass' or 'my_function').
        This is the short name used in the generated directive lines and passed to generate_function_wikidocs.
    evaled (any):
        The evaluated object corresponding to module_string + '.' + element_string (e.g., the actual function, method, class, or value).
        The method inspects this object with _is_method(evaled), type(evaled) with _is_class, and by checking evaled.__module__.
    is_class (bool, optional):
        Defaults to False. True when the current inspected container is a class (i.e., the member belongs to a class).
        Influences whether generated function-like docs are formatted as methods (and appended to classes) or functions (and appended to functions).

## Returns:
    None
    - This method does not return a value; its result is observed via mutations to the Documize instance (self.functions and self.classes lists) and by the side effect of possibly recursing into nested members via self.process_element_recursively.

## Raises:
    Propagated errors from helper predicates and methods:
    - NameError or TypeError from _is_method(evaled) or _is_class(type(evaled)) if module-level configuration variables those predicates rely on are missing or malformed.
    - Any exception raised by self.generate_function_wikidocs (for example, inspect.getargspec may raise TypeError on unsupported callables).
    - Any exception raised by self.process_element_recursively (which internally uses eval() to resolve fully-qualified names and may raise NameError, AttributeError, or other runtime errors).
    - AttributeError if evaled lacks expected attributes (the code checks evaled.__module__ with hasattr guard, but other attribute access in downstream calls may fail).
    Notes:
    - The method itself performs no explicit error handling; exceptions propagate to the caller.

## State Changes:
Attributes READ:
    - self.generate_function_wikidocs (method call)
    - self.process_element_recursively (method call)
    - self.functions (read when appending)
    - self.classes (read when appending)
    - evaled.__module__ (read in the third branch)
Attributes WRITTEN:
    - self.functions: may be appended with a function/method docs string when _is_method(evaled) is True and is_class is False.
    - self.classes: may be appended with either a function/method docs string when _is_method(evaled) is True and is_class is True, or with a class directive header string when a class-like object is detected; further recursive calls may append additional items to this list.

## Constraints:
Preconditions:
    - module_string and element_string should correctly identify the evaluated object supplied as evaled (typically the result of evaluating "{module_string}.{element_string}").
    - The module-level helper functions _is_method and _is_class must be defined and behave as expected (see their documentation). If those helpers are missing or misconfigured, this method will raise.
    - The Documize instance must provide generate_function_wikidocs and process_element_recursively methods (present on Documize), and self.functions / self.classes should be list-like.

Postconditions:
    - If evaled is recognized as a method by _is_method:
        * generate_function_wikidocs(element_string, evaled, is_class) is called and its returned text is appended to self.functions (if is_class is False) or to self.classes (if is_class is True).
    - If evaled is recognized as a class by _is_class(type(evaled)) OR evaled.__module__ indicates the object belongs to the same module namespace (starts with module_string):
        * A class directive header string '\n.. class:: {element_string}\n\n' is appended to self.classes.
        * The method then constructs a new qualified module_string by appending '.' + element_string and calls self.process_element_recursively(new_module_string, evaled, True) to document nested members.
    - Otherwise, no changes are made (the method is a no-op in the final else branch).

## Side Effects:
    - Mutates self.functions and/or self.classes by appending documentation strings.
    - May trigger recursion into nested class members (via self.process_element_recursively), which will execute eval() calls to resolve nested attributes; those eval() calls may execute code referenced by attribute access and can raise exceptions.
    - Does not perform I/O itself (no file or network access), but subsequent recursion or helper methods may read __doc__ strings and inspect objects.
    - No return value; effects are achieved via mutations on the Documize instance.

## Implementation notes and important edge cases:
    - The method distinguishes methods vs classes with two separate policies: _is_method operates on the evaled object itself, while _is_class is called with type(evaled). Both predicates can raise if module-level configuration is missing or invalid—callers should be prepared to handle those errors.
    - The third branch (hasattr(evaled, '__module__') and startswith(module_string)) is a fallback that treats some objects (for example, classes defined in the same module) as classes even if type(evaled) fails _is_class. This can include user-defined classes and some class-like descriptors whose runtime type is not captured by _is_class.
    - When recursing, the method builds the qualified name used by process_element_recursively by concatenating a dot and the element_string; callers should pass an appropriate initial module_string (e.g., top-level module path) so subsequent startswith checks are meaningful.
    - The method intentionally ignores non-matching callables/objects (final else: pass). Those members will not produce documentation entries.

### `scripts.api_doc_generator.Documize.generate_function_wikidocs` · *method*

## Summary:
Formats and returns a reStructuredText (Sphinx/wiki-style) documentation snippet for a Python function or method (including its signature and cleaned docstring). Does not mutate the Documize instance; it produces the formatted text that callers append into module/class documentation aggregates.

## Description:
Known callers and lifecycle:
- Documize.generate_callable_wikidocs calls this method when it identifies a callable (function or method) while traversing a module or class.
- Documize.process_element_recursively indirectly triggers this method while iterating members of a module or class during the module documentation generation pipeline.
- The string returned by this method is appended by the caller to Documize.functions (for top-level functions) or Documize.classes (for class methods), so it participates as one formatting step in the full documentation generation flow invoked from Documize.generate_module_wikidocs.

Why this is a separate method:
- The method centralizes the logic for building a standardized signature line (including reasonable handling of default argument values) and for cleaning & formatting the function's docstring (using inspect.cleandoc and minor code-block handling). Separating this from traversal and collection keeps concerns isolated: callers handle discovery and storage, while this method handles textual formatting.

## Args:
    func_string (str):
        Display name for the function or method (typically "module.func" or "Class.method"). Required.
    func (callable):
        The function or method object to document. Must be a Python-level callable accepted by inspect.getargspec. Required.
    is_class (bool, optional):
        If True, formats the directive as a class method ("   .. method") instead of a top-level function (".. function"). Defaults to False.

## Returns:
    str: A reStructuredText snippet containing:
        - A directive line and the function/method signature, e.g.:
            "----\n\n.. function:: module.func(arg1, arg2=default)\n\n"
          or, for methods:
            "\n   .. method:: Class.method(self, ...)\n\n"
        - If the function has a docstring, a cleaned and indented version of that docstring appended after the signature, with the first encountered interactive Python prompt line (a line starting with '>>>') preserved as an indented code example fragment.
        - The method always returns a string (possibly just a short signature with no docstring) and never returns None.

Edge-case returns:
- If inspect.getargspec or other introspection fails (for example when passed a built-in/C-implemented callable not supported by getargspec), the method will not catch that exception and it will propagate to the caller (see Raises).

## Raises:
    Any exception raised by inspect.getargspec(func):
        - For non-Python (built-in/C) callables, inspect.getargspec may raise ValueError or TypeError (implementation-dependent). This method does not catch errors from inspect.getargspec, so those exceptions propagate.
    (Internal formatting errors are guarded in the argument-formatting loop by a try/except which swallows formatting errors for individual arguments and will fall back to emitting the argument name only.)

## State Changes:
    Attributes READ:
        - None (the method does not access or depend on any self.<attr> fields)
    Attributes WRITTEN:
        - None (the method returns a string and does not modify self or external objects)

## Constraints:
    Preconditions:
        - func_string must be a valid string suitable for inclusion in a directive header.
        - func must be a Python-level callable that inspect.getargspec can introspect (i.e., a user-defined function or method). Passing certain builtins/C-extension callables may raise exceptions from inspect.getargspec.
        - The caller is expected to append the returned string to the correct Documize collection (Documize.functions or Documize.classes) — this method does not perform appends itself.

    Postconditions:
        - Returns a syntactically-constructed documentation string representing the function/method signature and, if present, its cleaned docstring formatted for inclusion in the generated module/class documentation.
        - Does not change object state or external state.

## Side Effects:
    - No I/O is performed.
    - No network or external service calls.
    - Reads attributes of the provided func (func.__doc__) and uses the inspect module for introspection.
    - Does not modify the provided func or any external objects.

### `scripts.api_doc_generator.Documize.reset` · *method*

## Summary:
Clears the object's collected documentation buffers by replacing the functions, classes, and attributes collectors with fresh empty lists, resetting the object's in-memory documentation state.

## Description:
- Known callers and lifecycle context:
    - generate_module_wikidocs(): invoked at the start of a module documentation generation run to ensure no leftover items from a previous run persist.
    - set_module(module_string): called whenever the target module is set or changed; ensures the collectors are empty after switching modules.
    - __init__(module_string=''): indirectly invoked during construction because __init__ calls set_module, which calls reset.
  These calls occur during the documentation-generation lifecycle: when a Documize instance is initialized, when a module is selected, and immediately before a module's wiki documentation is produced.

- Why this is a separate method:
    - Centralizes the logic for clearing all collectors in one place so callers (constructor, module setter, generator) do not duplicate list-reset code.
    - Ensures a consistent, single-point behavior for resetting instance state, and makes it explicit and easy to reuse and test.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
- Attributes READ:
    - None (the method does not inspect any existing attributes before assigning)
- Attributes WRITTEN:
    - self.functions: set to a new empty list (list[str])
    - self.classes: set to a new empty list (list[str])
    - self.attributes: set to a new empty list (list[str])

## Constraints:
- Preconditions:
    - self must be a Documize instance (or at least have attributes functions, classes, attributes assignable).
    - No assumptions are made about previous contents of the attributes; they will be replaced unconditionally.
- Postconditions:
    - After return, self.functions, self.classes, and self.attributes reference newly created empty lists.
    - Any prior contents that were stored only in these lists are lost (replaced).
    - The assignment creates instance attributes that shadow any class-level lists with the same names (preventing accidental shared mutable state).

## Side Effects:
- Mutates only the provided object's attributes (self). No I/O, no external service calls, and no mutation of objects outside self.
- Because this assigns new lists to instance attributes, it breaks references to any previously shared list objects (for example, a class-level default list), which prevents subsequent mutations from affecting other instances that might have shared that list.

### `scripts.api_doc_generator.Documize.set_module` · *method*

## Summary:
Set the Documize instance's target by evaluating the provided module expression and clear any previously collected documentation state.

## Description:
Known callers and context:
- Invoked from Documize.__init__ when an initial module_string is supplied during construction.
- Intended to be called by client code to switch which module/object the Documize instance will document prior to calling generate_module_wikidocs or output_wiki.
- Lifecycle stage: module-selection / initialization step of the documentation generation pipeline.

Why this is a separate method:
- It groups two related responsibilities — resolving the target object from a string expression and resetting internal caches/lists — into a single atomic operation. This prevents stale documentation state when the target changes and centralizes the potentially unsafe eval operation for easier review or replacement.

## Args:
    module_string (str): A Python expression represented as a string that will be evaluated to obtain the module or object to document.
        - Behavior for special values:
            - Exactly the empty string (''): treated as a no-op — no changes are made to the instance.
            - Any other string (including whitespace-only strings) is passed to eval and will be evaluated; ensure the expression is valid in the module's evaluation context.
        - Typical usage: a dotted module path such as 'mypackage.mymodule' (assuming that name is resolvable in the evaluation context), or any expression that returns the desired object (for example, 'sys.modules["os"]').

## Returns:
    None
    - The method returns implicitly None and performs state mutation. If module_string == '', the method returns after doing nothing.

## Raises:
    - Propagates any exceptions raised by eval(module_string). Common examples include:
        - SyntaxError: if module_string is not a valid Python expression.
        - NameError: if names used in module_string are not defined in the evaluation context.
        - TypeError: if an inappropriate non-string is passed and causes eval to fail.
        - Any other exception raised during evaluation (these will bubble up to the caller).
    - Note: the method does not catch or wrap eval exceptions; callers must handle or prevent them.

## State Changes:
Attributes READ:
    - self.reset (method attribute): the method is looked up and invoked.
    - The method does not read other self.<attr> values prior to writing them.

Attributes WRITTEN:
    - self.module_string: set to the provided module_string when module_string != ''.
    - self.module: set to the value returned by eval(module_string) when module_string != '' (this can be any Python object, not necessarily a module).
    - self.functions, self.classes, self.attributes: each reset to an empty list via self.reset().

## Constraints:
Preconditions:
    - module_string should be a str. Passing a non-str may cause eval to raise.
    - If module_string != '', it must be a valid Python expression in the evaluation context of this module file (the eval call uses the function's globals/locals).
    - The evaluated expression should resolve to the intended object (module or other) so that subsequent documentation generation behaves as expected.

Postconditions:
    - If module_string == '': no changes to the instance state.
    - If module_string != '' and eval(module_string) completes successfully:
        - self.module_string equals the provided module_string.
        - self.module references the evaluated object (possibly any Python object).
        - Internal documentation lists (self.functions, self.classes, self.attributes) are cleared and ready to be repopulated by generation methods.

## Side Effects:
    - Executes arbitrary code via eval(module_string) in this module's execution context. This can run side-effecting code and is a security risk when module_string is untrusted.
    - No direct file or network I/O performed by this method itself.
    - Mutates the Documize instance's internal state (clears caches), affecting subsequent documentation generation calls.

## Recommendations and Notes:
    - Security: Prefer passing only trusted, fixed strings. If user-provided input must be supported, consider replacing eval with a safer API such as importlib.import_module for simple dotted module names.
    - If you want to set the target using an already-imported module object, consider extending the class with a helper that accepts module objects directly to avoid eval.
    - Remember that whitespace-only strings are not treated as empty; only the exact empty string ('') bypasses evaluation.

### `scripts.api_doc_generator.Documize.output_wiki` · *method*

## Summary:
Delegates to and returns the result of the module-level RST generator, producing the assembled reStructuredText for the configured module and leaving internal collection state in the form produced by the generator.

## Description:
This method is a thin delegator used in the documentation-generation pipeline to obtain the final module-level reStructuredText produced by the Documize instance. It is typically invoked by higher-level code that needs the rendered module documentation string after the Documize instance has been configured (for example, code that sets self.module_string and self.module and then requests the module output). The logic is split out as its own method to provide a stable, explicit public API on Documize for "get me the module wiki text" and to keep callers decoupled from the name of the underlying implementation method (generate_module_wikidocs).

Known callers / lifecycle stage:
- Called after Documize has been configured for a specific target module (via set_module) and when the caller wants the assembled module documentation string for writing to disk or aggregation into an index.
- Typical usage pattern: construct Documize, call set_module(module_name), then call output_wiki() to obtain the RST text.

Why this is a separate method:
- Provides a small, stable public API that encapsulates the full module-document generation step.
- Keeps callers from depending on internal method names or implementation details (delegation centralizes the call).

## Args:
This method takes no arguments.

## Returns:
- str: The reStructuredText-formatted documentation for the module, exactly as returned by self.generate_module_wikidocs().
- Edge cases:
    - If generate_module_wikidocs returns an empty string, that empty string is returned unchanged.
    - If generate_module_wikidocs returns None (unexpected), None is returned unchanged.

## Raises:
- AttributeError: If the instance does not have generate_module_wikidocs as a callable attribute (attempting to access or call it will raise).
- Any exception raised by self.generate_module_wikidocs() propagates unchanged (for example, exceptions raised during module inspection or list operations inside the generator).

## State Changes:
Attributes READ:
- Direct: self.generate_module_wikidocs (the bound method is resolved and called).
- Indirect (read by the delegated method): self.module_string, self.module, self.classes, self.functions, self.attributes (generate_module_wikidocs reads these to assemble output).

Attributes WRITTEN:
- Direct: none — this method does not mutate attributes itself.
- Indirect (mutated by the delegated method): self.reset() is called within generate_module_wikidocs and the delegated execution will clear and repopulate internal lists; specifically, self.functions, self.classes, and self.attributes are reset and then populated and sorted by the delegated method.

## Constraints:
Preconditions:
- self.generate_module_wikidocs must exist and be callable.
- The Documize instance should be configured for a target module (typically via set_module) so that generate_module_wikidocs can operate meaningfully (it expects self.module_string and self.module to be set).

Postconditions:
- The method returns exactly whatever self.generate_module_wikidocs() returned.
- After the call, internal doc-collection lists (self.functions, self.classes, self.attributes) will reflect the state produced by the delegated generator (they will have been reset and then populated/sorted).

## Side Effects:
- No file, network, or external I/O performed directly by this method.
- It invokes generate_module_wikidocs(), which has side effects: it calls reset(), inspects the configured module, and mutates internal lists (self.functions, self.classes, self.attributes). Any side effects of those methods (e.g., exceptions raised during inspection) will occur as part of this call.

## `scripts.api_doc_generator.generate_package_wikidocs` · *function*

## Summary:
Iterates over the public attributes of the evaluated package string and writes wiki-formatted documentation files (one per attribute) into the directory specified by sys.argv[1].

## Description:
This function is a small CLI-oriented utility that:
- Constructs a Documize instance and uses it to produce wiki text for each top-level attribute of a package.
- For each attribute found on the package it sets the Documize module to the attribute's fully-qualified name and calls Documize.output_wiki() to obtain the rendered wiki content, then writes that content to a file under the output directory taken from sys.argv[1].

Known callers within the codebase:
- No callers were found in the scanned repository. This function is written in a style intended to be invoked from a command-line driver (a script which ensures sys.argv[1] is provided).

Typical trigger / pipeline stage:
- Intended to be used at documentation-generation time (build step or ad-hoc CLI run) where the user supplies a destination directory as the first command-line argument and a package path (as a string) as the function argument.

Why this is extracted into a function:
- Packaging the iteration over package attributes, the Documize lifecycle (create → set_module → output), and the per-attribute file output makes the documentation-generation logic reusable and isolated from the particular CLI/driver code that provides sys.argv and calls this function.

Important implementation note (observed bug):
- The code tests callable(element) where element is a string from dir(package). Because element is a string, callable(element) is always False. The effect is that the function will NOT filter out callable attributes as intended — it will attempt to document all non-dunder names. Any reimplementation should call getattr(package, element) and then callable(that_object) to correctly filter callables.

## Args:
    package_string (str):
        - Fully-qualified package expression as a Python expression (for example 'mingus.containers' or 'mypkg.subpkg').
        - This string is evaluated with eval(package_string); therefore it must be a valid Python expression resolvable in the current process namespace.
    file_prefix (str, optional):
        - Prefix for output filenames. Default: 'ref'
        - Example: 'ref' leads to files like 'refMingusContainersNote.wiki'.
    file_suffix (str, optional):
        - Suffix/extension for output filenames. Default: '.wiki'
        - Example: '.wiki', '.md'. Keep the leading dot if you want an extension.

Interdependencies:
- The function uses sys.argv[1] as the output directory path. The caller or the running process must set sys.argv[1] appropriately (usually via the command line) before calling this function.

## Returns:
    None
    - The function does not return a value. It performs side effects (creates/writes files and prints status messages).
    - All success/failure status is communicated by writing to stdout (print) and by creating files under the supplied output directory when writes succeed.

## Raises:
    - The function does not explicitly raise exceptions for IO errors; file opening and writing errors are caught and reported to stdout.
    - Exceptions that may propagate out of the function:
        * Any exception raised by Documize() constructor (if Documize is unavailable or raises during initialization).
        * Any exception raised by eval(package_string) (for example NameError, SyntaxError) — these are not caught and will propagate.
        * Any exception raised while evaluating fullname via eval(fullname) (for example AttributeError or NameError if evaluation fails) — these are not caught before use.
    - File I/O exceptions (open, write) are caught locally and suppressed (the function prints an error message instead of raising).

## Constraints:
Preconditions:
    - package_string must be a valid Python expression referring to an importable/available package object in the running process (otherwise eval will raise).
    - sys.argv must have at least 2 elements and sys.argv[1] should be a writable path if you expect files to be created successfully. The function does not create the destination directory; it only attempts to open files in that directory.
    - Documize class (and its methods set_module and output_wiki) must be importable/available; otherwise construction or method calls will raise.

Postconditions:
    - For each non-dunder attribute name present on the evaluated package (irrespective of whether the attribute is callable, due to the noted bug), the function will attempt to write one file named:
        file_prefix + concatenation of each dotted part of the fully-qualified name with the first letter capitalized + file_suffix
      into the directory path sys.argv[1]; files will exist for attributes that were successfully written, and the function will have printed 'OK' for those files.
    - The function leaves stdout printed logs indicating which files were written and which failed.

## Side Effects:
    - I/O: Opens and writes files to the filesystem under os.path.join(sys.argv[1], wikiname). No explicit file mode for newline or encoding is specified (uses default system encoding).
    - Stdout: Prints progress and error messages using print().
    - Security: Uses eval(package_string) and eval(fullname) which will execute arbitrary code if the strings contain expressions. Do not call this function with untrusted input.
    - No network interactions are performed by this function itself.
    - No global variables are mutated by the function except the possible side effects of Documize.set_module() (implementation-dependent).

## Control Flow:
flowchart TD
    Start --> ConstructDocumize[Create Documize()]
    ConstructDocumize --> EvalPackage[eval(package_string)]
    EvalPackage --> Iterate[for element in dir(package)]
    Iterate -->|element starts with '__'| SkipElement[skip]
    Iterate -->|element is not dunder| BuildFullname[fullname = package_string + '.' + element]
    BuildFullname --> EvalFullname[e = eval(fullname)]
    EvalFullname --> SetModule[d.set_module(fullname)]
    SetModule --> BuildFilename[compose wikiname from file_prefix + parts.capitalize() + file_suffix]
    BuildFilename --> OutputWiki[result = d.output_wiki()]
    OutputWiki --> TryOpen[try: open(os.path.join(sys.argv[1], wikiname), 'w')]
    TryOpen -->|open success| TryWrite[try: f.write(result)]
    TryWrite -->|write success| PrintOK[print('OK')]
    TryWrite -->|write fail| PrintWriteError[print("ERROR. Couldn't write to file.")]
    TryOpen -->|open fail| PrintOpenError[print("ERROR. Couldn't open file for writing.")]
    PrintOK --> ContinueLoop[continue loop]
    PrintWriteError --> ContinueLoop
    PrintOpenError --> ContinueLoop
    SkipElement --> ContinueLoop
    ContinueLoop --> Iterate
    Iterate --> End[End]

Notes:
- The diagram highlights the main decisions and the nested try/except handling for file open/write operations.
- The check to skip callables is incorrectly implemented (callable(element) checks the string name) — thus many elements intended to be skipped may be processed.

## Examples:
Example 1 — typical CLI usage (driver script sets sys.argv[1] to destination directory):
    import sys
    from scripts.api_doc_generator import generate_package_wikidocs

    # CLI would typically set sys.argv; ensure an output dir exists
    sys.argv = ['script_name', './docs']
    generate_package_wikidocs('mingus.containers', file_prefix='ref', file_suffix='.wiki')

    # Expected behaviour:
    # - For each public attribute name on mingus.containers, a file named like
    #   refMingusContainersNote.wiki is attempted under ./docs
    # - Progress printed to stdout, 'OK' printed for successfully written files

Example 2 — defensive wrapper to surface eval errors:
    import sys
    try:
        sys.argv = ['docgen', './docs']
        generate_package_wikidocs('nonexistent.package')  # will raise NameError or similar
    except Exception as exc:
        print('Documentation generation failed:', type(exc).__name__, exc)

Implementation hints for reimplementers:
    - Replace eval(package_string) with a safer import mechanism (for example, importlib.import_module) to avoid executing arbitrary code and to get clearer error semantics.
    - When iterating attributes, use getattr(package, element) and test callable(getattr(...)) to correctly skip callables when intended.
    - Normalize file name generation if different casing/formatting is desired (the current implementation uses str.capitalize() on each dotted part).
    - Explicitly handle encoding when opening files (for example, with open(..., 'w', encoding='utf-8')) for predictable cross-platform behavior.

## `scripts.api_doc_generator.main` · *function*

## Summary:
Prints a short license/header and validates a single command-line output directory argument; on success, drives generation of package reference docs by calling the documentation-generator helper for each top-level mingus package.

## Description:
This function is a tiny command-line entrypoint for producing API documentation for the mingus project. It is intended to be executed from a process started with command-line arguments (sys.argv). Its responsibilities are to:
- Print a fixed version/copyright/warranty header to stdout.
- Validate that the caller supplied exactly one required positional argument: an output directory path (sys.argv[1]).
- If validation passes, call the helper function generate_package_wikidocs for the four top-level mingus subpackages ('mingus.core', 'mingus.midi', 'mingus.containers', 'mingus.extra') to emit reference documentation files into the supplied directory.

Known callers within the codebase:
- None found. main() is implemented as a CLI driver and is expected to be invoked by running the script (e.g., via the Python interpreter or as a module). It is not referenced elsewhere in the repository as a library function.

Typical trigger / pipeline stage:
- Documentation build step or an ad-hoc developer CLI invocation that supplies an output directory to receive generated reStructuredText reference pages.

Why this logic is extracted:
- main() is a thin CLI driver that isolates argument validation and control flow from the actual documentation generation logic implemented in generate_package_wikidocs. Keeping CLI concerns (argument validation, usage printing, early exit) separate from the package-iteration and file-writing logic clarifies responsibilities and makes the generation logic reusable from other callers.

## Args:
This function takes no formal parameters. Instead it relies on the process global sys.argv:
- sys.argv (list[str]): The function expects sys.argv[1] to be present and to be a path to an existing directory that is intended as the output directory for generated docs.
    - Required values:
        * sys.argv must contain at least 2 elements (the script name and the output directory).
        * sys.argv[1] should refer to an existing directory (os.path.isdir will be used to check this).
    - Interdependencies:
        * generate_package_wikidocs (called later) also reads sys.argv[1] to determine the output path for files it writes.

## Returns:
- None.
- The function does not return a value; it performs side effects (printing and calling generate_package_wikidocs which writes files). Success/failure is signalled via stdout messages and, in error cases, by raising SystemExit with exit code 1.

## Raises:
- SystemExit(1): Raised explicitly when the command-line argument requirements are not met:
    * If len(sys.argv) == 1, the function prints a usage line and calls sys.exit(1).
    * If sys.argv[1] exists but is not a directory (os.path.isdir(...) returns False), the function prints an error and calls sys.exit(1).
- Any exception raised by generate_package_wikidocs will propagate out of main (e.g., NameError, IOError, or other runtime exceptions that that helper does not catch).
- Any other unexpected exceptions (for example from os.path.isdir if abnormal inputs are present) will propagate normally.

## Constraints:
Preconditions:
- The process must have sys.argv set such that sys.argv[1] exists and points to an intended output directory.
- The caller must have permissions to read that directory (and generate_package_wikidocs must have permission to write into it).
- The runtime environment must have generate_package_wikidocs defined and importable in the same module (this function calls it directly).

Postconditions:
- If main returns normally (i.e., does not call sys.exit), it will have invoked generate_package_wikidocs four times with package strings:
    * 'mingus.core', 'ref', '.rst'
    * 'mingus.midi', 'ref', '.rst'
    * 'mingus.containers', 'ref', '.rst'
    * 'mingus.extra', 'ref', '.rst'
  The final observable effect depends on generate_package_wikidocs (typically the creation of per-module reference files in the directory sys.argv[1]).
- If argument validation fails, the function will have printed a usage or error message and raised SystemExit(1) before invoking generate_package_wikidocs.

## Side Effects:
- Stdout: Prints a multi-line license/version header at start, plus usage or error messages when validation fails. Example prints:
    * The header beginning with "mingus version 0.5, Copyright (C) 2008-2015, Bart Spaans"
    * On missing argument: "Usage: <script> OUTPUT-DIRECTORY"
    * On invalid directory: "Error: not a valid directory: <supplied-path>"
- Process termination: Calls sys.exit(1) in validation failure cases (raises SystemExit).
- Calls generate_package_wikidocs four times, which writes files into the directory referenced by sys.argv[1] (file creation/writes are side effects performed by that helper).
- No network I/O is performed in main itself.

## Control Flow:
flowchart TD
    Start --> PrintHeader[Print license/version header]
    PrintHeader --> CheckArgs{len(sys.argv) == 1?}
    CheckArgs -->|True| PrintUsage[Print "Usage: <script> OUTPUT-DIRECTORY"]
    PrintUsage --> ExitUsage[sys.exit(1) -> SystemExit raised]
    CheckArgs -->|False| CheckDir{os.path.isdir(sys.argv[1])?}
    CheckDir -->|False| PrintDirError[Print "Error: not a valid directory: <path>"]
    PrintDirError --> ExitDir[sys.exit(1) -> SystemExit raised]
    CheckDir -->|True| CallGen1[generate_package_wikidocs('mingus.core','ref','.rst')]
    CallGen1 --> CallGen2[generate_package_wikidocs('mingus.midi','ref','.rst')]
    CallGen2 --> CallGen3[generate_package_wikidocs('mingus.containers','ref','.rst')]
    CallGen3 --> CallGen4[generate_package_wikidocs('mingus.extra','ref','.rst')]
    CallGen4 --> End[End (return None)]

Notes:
- Any exception raised by generate_package_wikidocs will break the linear sequence and propagate unless handled by an external caller.
- Validation failures cause immediate exit via SystemExit(1).

## Examples:
Example A — typical command-line usage:
- Run from a shell where ./docs exists:
    python scripts/api_doc_generator.py ./docs
  Outcome:
    - The header is printed.
    - If ./docs is an existing directory, the script invokes generate_package_wikidocs for the four mingus packages and returns (the helper writes files under ./docs).
    - If ./docs does not exist or is not a directory, the script prints "Error: not a valid directory: ./docs" and exits with code 1.

Example B — invoked programmatically (useful in test harnesses):
- Ensure the environment mimics a CLI by setting sys.argv first, then call main():
    - Set sys.argv to ['api_doc_generator.py', '/absolute/path/to/docs']
    - Call main()
  Handling errors:
    - Wrap call in try/except SystemExit to capture usage/directory validation failures:
        - If a SystemExit with code 1 is raised, the caller can handle/translate it into a test failure or create the missing directory and retry.
  Notes:
    - generate_package_wikidocs will perform the actual file writes; failures during generation will raise exceptions back to the caller.

Implementation hints for reimplementers:
- main is intentionally minimal — validation and sequencing only. Preserve that separation when reimplementing: do not inline generate_package_wikidocs functionality into main.
- If you want safer, clearer behavior:
    * Replace direct reliance on sys.argv inside library code with explicit parameters (e.g., make a helper that accepts an output_dir argument and call it from a thin main wrapper).
    * Return explicit exit codes or raise well-documented exceptions instead of calling sys.exit from deep in library logic; call sys.exit only from the actual CLI wrapper.

