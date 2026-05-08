# `xpathfuncs.py`

## `parsel.xpathfuncs.set_xpathfunc` · *function*

## Summary:
Register or unregister a named XPath extension function in lxml's default (null) FunctionNamespace, making the callable available to (or removing it from) XPath expressions evaluated by lxml.

## Description:
A thin utility that manipulates lxml.etree's default FunctionNamespace mapping:
- When given a callable, it binds that callable to the provided name so XPath expressions can invoke it.
- When given None, it removes the named binding from the namespace.

Known callers within the codebase:
- No direct callers are present in the supplied component context. This function is intended for use by initialization code, parser/plugin setup, or scraping session setup that must register custom XPath helper functions before running XPath queries.

Responsibility boundary:
- Encapsulates the direct interaction with lxml.etree.FunctionNamespace(None) so callers do not perform mapping mutations themselves.
- Does not perform validation of fname or func beyond relying on lxml's behavior.

## Args:
    fname (str):
        - The local name to expose in the default (null) XPath namespace (e.g., 'myfunc').
        - Must be a string; the function does not enforce QName validity or XML namespace rules.
    func (Optional[Callable]):
        - If a callable is provided, it will be registered under fname.
        - If None, the function attempts to remove the existing registration for fname.
        - The callable should be compatible with lxml extension function semantics (typically receiving an XPath context as the first argument, then zero or more arguments). This function does not check callable signature.

Interdependencies:
    - fname and func together determine register vs unregister behavior: func is None -> unregister; otherwise register/overwrite.

## Returns:
    None
    - The function returns None; its observable effect is the mutation of lxml's default FunctionNamespace mapping.

## Raises:
    KeyError:
        - Raised when func is None and there is no existing binding for fname in the default FunctionNamespace. This originates from the del operation on the namespace mapping.
    TypeError (possible; originates from lxml):
        - If func is provided but not a valid callable for lxml's extension-function mechanism, the underlying lxml implementation may raise a TypeError (or another error). This behavior depends on lxml and is not induced directly by this wrapper.

## Constraints:
Preconditions:
    - lxml.etree must be available in the runtime environment and support FunctionNamespace(None).
    - fname must be a string that callers intend to reference from XPath expressions.
    - If registering, func should be a callable compatible with lxml extension functions.

Postconditions:
    - If func is not None: after successful return, the default FunctionNamespace maps fname to func. Any subsequent XPath evaluation that calls the name in the default namespace will invoke func.
    - If func is None: after successful return, no mapping for fname exists in the default FunctionNamespace.
    - Registering (assigning) overwrites any preexisting mapping for fname without warning.

## Side Effects:
    - Mutates global state inside lxml.etree.FunctionNamespace for the default (null) namespace. This mutation is visible to all code that uses the same lxml FunctionNamespace (process-global behavior).
    - No file, network, or stdout/stderr I/O is performed by this function itself.
    - No other Python-global variables are modified by this wrapper.
    - Because it changes global lxml state, concurrent code (other threads or components) that relies on particular namespace bindings may see changed behavior; callers should coordinate registrations/unregistrations if concurrency is a concern.

## Control Flow:
flowchart TD
    Start --> GetNamespace[Get default FunctionNamespace\n(etree.FunctionNamespace(None))]
    GetNamespace --> IsFuncNotNone{func is not None?}
    IsFuncNotNone -- Yes --> Assign[Assign ns_fns[fname] = func\n(overwrite if exists)]
    Assign --> EndAssign[Return None (success)]
    IsFuncNotNone -- No --> Delete[Attempt del ns_fns[fname]]
    Delete --> PresentCheck{fname present?}
    PresentCheck -- Yes --> EndDelete[Return None (success)]
    PresentCheck -- No --> RaiseKeyError[KeyError raised by del]
    RaiseKeyError --> End

## Examples:
- Registering a function (illustrative):
    - Precondition: create or have a callable that matches lxml extension semantics (here shown as my_callable).
    - Invocation: set_xpathfunc('myfunc', my_callable)
    - Effect: XPath expressions evaluated on lxml elements can call myfunc(...) in the default namespace.

- Using the registered function in an XPath evaluation (illustrative):
    - After registration, an lxml element or tree can evaluate an expression like tree.xpath('myfunc(.)') to invoke the registered callable.

- Safe unregister (illustrative pattern to avoid KeyError):
    - try:
          set_xpathfunc('maybe_missing', None)
      except KeyError:
          pass  # function was not registered; safe to ignore

Notes and best practices:
    - Registration overwrites any existing mapping for fname; prefer to register extension functions in a single controlled initialization phase to avoid accidental overwrites.
    - Validate or document callable signature expected by your XPath use-cases; this wrapper does not enforce signature compatibility.
    - Treat namespace registration as global process-level state — coordinate across modules or threads where necessary.

## `parsel.xpathfuncs.setup` · *function*

## Summary:
Register the has-class XPath extension helper in lxml's default (null) FunctionNamespace so XPath expressions can call a has-class(...) helper.

## Description:
This function performs a single responsibility: it binds the module-level has_class callable into lxml's default XPath function namespace under the local name "has-class". Typical callers are initialization or setup code that must make custom XPath helpers available before evaluating XPath expressions (for example, package/module initialization, parser setup, or a scraper session startup step). The logic is separated into this tiny function to centralize the registration step (so other modules can call a single well-named initializer) and to avoid duplicating the registration literal or semantics wherever this helper must be exposed.

Known related components:
- set_xpathfunc: the utility that performs the actual mutation of lxml.etree.FunctionNamespace(None). setup delegates the registration to this function.
- has_class: the callable being registered. Important behaviors of has_class that callers should be aware of:
  - It performs token-based CSS class membership checks (avoiding substring false-positives) by surrounding the normalized attribute string with spaces and testing for " {cls} " containment.
  - It normalizes HTML5 whitespace characters in the class attribute to ASCII spaces before matching (tabs/newlines/multiple spaces are normalized).
  - It validates that at least one class argument is provided and that all provided class arguments are Python str; this validation is performed once per XPath evaluation run and cached by setting context.eval_context["args_checked"] to True to avoid redundant checks across repeated calls during the same evaluation.

Why this is factored out:
- Keeps the registration name ("has-class") in one place so callers do not repeat string literals.
- Encapsulates the dependency on set_xpathfunc so tests or alternative registration strategies can replace or stub this function.
- Makes module initialization explicit and discoverable.

## Args:
This function takes no arguments.

## Returns:
None
- The function returns None; its observable effect is the registration side-effect in lxml's default FunctionNamespace.

## Raises:
- TypeError (possible): If underlying lxml rejects the callable being assigned (e.g., callable is not compatible with lxml extension semantics), lxml may raise a TypeError when binding the function. This originates from lxml and is not raised by this wrapper directly.
- Any exceptions raised by set_xpathfunc are possible (though for the non-None func case, set_xpathfunc typically performs an assignment and does not raise KeyError).

## Constraints:
Preconditions:
- lxml.etree must be importable and support FunctionNamespace(None).
- The module-level has_class callable must be defined and importable in the same module scope.
- The process environment should allow mutating lxml's global FunctionNamespace (consider concurrency implications).

Postconditions:
- After successful return, the default lxml FunctionNamespace maps the local name "has-class" to the has_class callable. Subsequent XPath evaluations that reference the local name "has-class" will invoke has_class.
- Calling setup multiple times simply reassigns the same mapping (idempotent from a functional outcome perspective).

## Side Effects:
- Mutates lxml.etree.FunctionNamespace(None) by assigning ns_fns["has-class"] = has_class. This is global (process-wide) state visible to any code evaluating XPath against lxml trees in the same process.
- No file, network, or stdout/stderr I/O is performed by this function itself.
- No other Python global variables are modified by this function.

## Control Flow:
flowchart TD
    Start --> CallSetXPath["Call set_xpathfunc('has-class', has_class)"]
    CallSetXPath --> SetNamespace["lxml default FunctionNamespace updated\n(ns_fns['has-class'] = has_class)"]
    SetNamespace --> End["Return None"]

## Examples:
1) Typical initialization use:
   - Purpose: make the has-class helper available to subsequent XPath evaluations.
   - Steps:
       - Ensure the environment where lxml is used imports or calls this setup function during initialization.
       - Call setup() early (for example, at module import time or during application startup).
       - After setup, XPath expressions can reference has-class in the default namespace. Example XPath usage conceptually:
           - tree.xpath("//*[has-class('foo')]")
         This evaluates has_class for each candidate node; has_class will normalize HTML5 whitespace in the node's class attribute, perform whole-token matching for 'foo', and return True if present.

2) Error-awareness:
   - If lxml rejects the callable signature for extension functions, a TypeError may propagate from the underlying lxml binding operation. Wrap setup() in a try/except if you expect environments with incompatible lxml versions or restricted extension-function semantics.

Notes:
- Unregistering or replacing the binding must be done via set_xpathfunc with func set to None (not performed by this function).
- Because registration is global, prefer calling setup from a single controlled place to avoid accidental overwrites across modules or threads.

## `parsel.xpathfuncs.has_class` · *function*

## Summary:
Return whether the current XPath context node has all of the specified CSS class names in its class attribute; the match treats class names as whole, space-delimited tokens.

## Description:
This function is intended to be used as an XPath extension helper that checks whether the node currently referenced by an XPath evaluation context contains one or more CSS class names. Typical usage is during XPath evaluation where an extension function is called for each candidate node (for example, when evaluating an expression that filters nodes by class membership).

Known callers within the codebase:
- Used as an XPath helper/extension function when evaluating class membership inside XPath expressions. (No explicit call sites were provided in the immediate context; consumers will typically register this function as an extension function with an lxml XPath evaluator and invoke it from an XPath expression.)

Why this logic is factored into a dedicated function:
- Argument validation and normalization of HTML5 whitespace are centralized here so callers (XPath expressions / extension registration) do not duplicate the same checks.
- It implements a correct token-based class membership check (avoiding false positives from substring matches) and normalizes whitespace per HTML5 rules, responsibilities that belong together and are non-trivial to inline at each call site.
- It caches that arguments were validated in the context.eval_context to avoid redundant validation work across repeated calls during a single XPath evaluation run.

## Args:
    context (Any):
        - Expected shape: an XPath evaluation context object supplying
          - eval_context: a mutable mapping (dict-like) used for storing evaluation-specific state
          - context_node: an element-like object with a .get(attr_name) method that returns the value of an attribute or None
        - In practice this is the context passed by lxml to extension functions during XPath evaluation.
    *classes (str):
        - One or more class name strings to check on the node.
        - Each provided argument must be of type str; otherwise a ValueError is raised.
        - At least one class name must be provided; an empty argument list triggers a ValueError.
        - Class names are treated as literal tokens (no trimming or splitting by the function), so each argument should represent a single CSS class token (no spaces). If a provided class string contains whitespace, it will be looked up literally (and will usually not match).

## Returns:
    bool:
        - True if and only if the node has a "class" attribute and all specified class name tokens are present as whole tokens inside that attribute.
        - False in these cases:
            * The node has no "class" attribute (context.context_node.get("class") returns None).
            * Any requested class token is not present as a whole token in the normalized class attribute.
        - Matching behavior notes:
            * The function inserts a leading and trailing ASCII space around the attribute value and tests for " {cls} " substrings to ensure whole-token matching.
            * Prior to matching, HTML5 whitespace characters in the attribute value are normalized to ASCII spaces (so tabs/newlines/multiple spaces are normalized) using the module's whitespace-normalization helper.
            * Comparison is a plain string containment check (case-sensitive per the implementation).

## Raises:
    ValueError:
        - If no class arguments are supplied: "XPath error: has-class must have at least 1 argument"
        - If any provided class argument is not an instance of str: "XPath error: has-class arguments must be strings"
        - These checks are performed only once per XPath evaluation run and are cached in context.eval_context using the key "args_checked". If the required keys are already present, the checks are skipped.

## Constraints:
    Preconditions:
        - context must provide:
            * eval_context: a mutable mapping (e.g., a dict) that can store arbitrary keys.
            * context_node: an object with .get(attribute_name) method that returns the attribute value or None.
        - callers must pass at least one class name and all class names must be Python str objects.
    Postconditions:
        - No mutation of the DOM/node attributes occurs.
        - context.eval_context["args_checked"] will be set to True after the first successful argument validation call during an XPath evaluation run (side-effect visible to the caller).

## Side Effects:
    - Modifies context.eval_context by setting the key "args_checked" to True the first time argument validation runs; this is used to avoid repeating argument checks across the same evaluation.
    - No I/O, network calls, file operations, or external state (database/cache) writes are performed.
    - Does not modify the node or its attributes.

## Control Flow:
flowchart TD
    Start --> CheckArgsCached{"context.eval_context.get('args_checked')?"}
    CheckArgsCached -- false --> ValidateArgs["If no classes -> raise ValueError\nFor each class: if not isinstance(str) -> raise ValueError\nSet context.eval_context['args_checked'] = True"]
    CheckArgsCached -- true --> SkipValidation[skip validation]
    ValidateArgs --> GetClassAttr["node_cls = context.context_node.get('class')"]
    SkipValidation --> GetClassAttr
    GetClassAttr --> IsNone{"node_cls is None?"}
    IsNone -- true --> ReturnFalse1["return False"]
    IsNone -- false --> Normalize["node_cls = ' ' + node_cls + ' '\nnode_cls = replace_html5_whitespaces(' ', node_cls)"]
    Normalize --> ForEachClassLoop["for cls in classes: if ' ' + cls + ' ' not in node_cls -> return False"]
    ForEachClassLoop --> ReturnTrue["return True"]

## Examples (usage pattern and error handling described):
1) Typical evaluation scenario (described):
   - An XPath evaluator registers this function as an extension function and runs an expression that calls it for multiple candidate nodes. The function will validate its arguments the first time it runs during that evaluation (raising ValueError if the call-site passed no arguments or non-string arguments); subsequent calls reuse the cached validation decision via context.eval_context["args_checked"].

2) Minimal illustrative example (conceptual, not literal registration code):
   - Given a node whose class attribute is "a\tb\nc" (contains HTML5 whitespace characters):
     - The function normalizes whitespace so the value becomes " a b c " before token checks.
     - Calling the helper with classes ('a', 'c') will return True.
     - Calling the helper with classes ('a', 'd') will return False.
   - If the node lacks a class attribute, any call returns False.
   - If called with no class arguments, the function raises ValueError immediately.

Notes and recommendations:
    - Supply single-token class names (no internal whitespace) to the function.
    - Be aware that the function uses simple string containment with surrounding spaces to ensure whole-token matching and that comparison is case-sensitive according to the implementation.

