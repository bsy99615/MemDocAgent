# `flavours.py`

## `src.ydata_profiling.report.presentation.flavours.flavours.apply_renderable_mapping` · *function*

## Summary:
Perform an exact-type lookup in a provided mapping and invoke the mapped class's convert_to_class on the supplied Renderable instance, causing an in-place conversion to the flavour-specific implementation. The function returns None.

## Description:
This helper encapsulates the single-step operation used when converting a generic Renderable instance into a flavour-specific renderer:
- It computes the runtime type of the supplied structure (using type(structure)).
- It uses that exact type as a key into the provided mapping to obtain a flavour-specific Renderable class.
- It then calls the mapped class's convert_to_class(structure, flavour) callable to perform the conversion.

Known callers and typical context:
- Presentation factories or report-assembly traversal code that must convert nodes of a pre-built renderable structure to a specific output flavour (for example "html" or "widget") before calling render().
- Typical pipeline stage: invoked during a tree traversal over Renderable nodes immediately prior to rendering each node or before a second pass that expects flavour-specific behavior.
- No direct call-sites were discovered in the provided snapshot; this function is a focused utility meant to be invoked repeatedly by conversion/traversal logic.

Why extracted:
- Centralizes and documents the exact mapping lookup semantics (exact runtime-type keying) and the required call to convert_to_class so callers do not duplicate the lookup/call pattern.
- Keeps conversion semantics consistent and makes it easy to add instrumentation or error handling in a single place if desired.

## Args:
- mapping (Dict[Type[Renderable], Type[Renderable]]):
    - A dictionary mapping concrete runtime classes (the keys) to flavour-specific Renderable classes (the values).
    - Important: keys are matched using type(structure) (exact match). Subclass or isinstance-style matching is not performed by this function.
- structure (Renderable):
    - The instance to convert. The function inspects only type(structure) and passes the instance through to convert_to_class; it does not inspect or mutate content itself.
- flavour (Callable):
    - A callable forwarded unchanged to convert_to_class. The function does not interpret or validate this argument; mapped convert_to_class implementations may use or ignore it.

## Returns:
- None.
- Effect: after successful completion, the instance will typically behave as an instance of the mapped flavour-specific class (for example its methods like render() will follow the flavour implementation) — the exact effect depends on the mapped class's convert_to_class implementation.
- Example of the base behavior: the Renderable base-class implementation of convert_to_class mutates obj.__class__ to the mapped class and ignores the flavour argument; many concrete implementations follow that pattern.

## Raises:
All exceptions from this function propagate to the caller; no exceptions are caught or wrapped.

- KeyError
    - Trigger: mapping does not contain an entry for type(structure). The code performs mapping[type(structure)] with no fallback.
- TypeError
    - Trigger: mapping is not subscriptable (e.g., None or another non-mapping), causing the indexing operation to raise TypeError.
    - Trigger: the attribute convert_to_class exists but is not callable; attempting to call it will raise TypeError.
    - Trigger: convert_to_class implementation attempts an invalid __class__ assignment or other operation that raises TypeError (this is a Python-level error when assigning incompatible C-level layouts between classes).
- AttributeError
    - Trigger: the resolved mapping value is not a class-like object exposing the attribute convert_to_class (i.e., mapping[type(structure)].convert_to_class does not exist).
- Any exception raised inside convert_to_class
    - Trigger: mapped convert_to_class implementation may raise arbitrary exceptions (ValueError, RuntimeError, template loading errors, etc.); those propagate unchanged.

## Constraints:
- Preconditions:
    - mapping must be a mapping whose keys include the exact runtime classes of any structure passed to this function.
    - structure must be an object whose runtime type appears as a key in mapping, or callers must handle the KeyError.
    - convert_to_class implementations must be safe to call on the provided instance (e.g., if they mutate __class__, the source and target classes must be compatible).
- Postconditions:
    - If convert_to_class returns normally, the structure should be converted according to the mapped class's semantics (often by replacing structure.__class__); the function itself does not further mutate structure or return a replacement object.

## Side Effects:
- In-place mutation of the instance is common: convert_to_class often changes structure.__class__ and may mutate other in-memory state.
- No file, network, or stdout I/O is performed here directly. Any I/O or external interactions are the responsibility of convert_to_class.
- No global variables are modified by apply_renderable_mapping itself.

## Control Flow:
flowchart TD
    Start[Start] --> TypeKey[type(structure)]
    TypeKey --> Lookup{mapping[type(structure)] exists?}
    Lookup -- No --> RaiseKeyError[KeyError] --> End
    Lookup -- Yes --> MappedClass[mapped = mapping[type(structure)]]
    MappedClass --> HasAttr{mapped has attribute convert_to_class?}
    HasAttr -- No --> RaiseAttrError[AttributeError] --> End
    HasAttr -- Yes --> IsCallable{convert_to_class callable?}
    IsCallable -- No --> RaiseTypeError[TypeError: not callable] --> End
    IsCallable -- Yes --> CallConvert[Call mapped.convert_to_class(structure, flavour)]
    CallConvert --> Propagate[Propagate any exception from convert_to_class]
    CallConvert --> Success[Return None] --> End

## Examples (usage and error handling in prose):
- Typical guarded usage when you cannot guarantee mapping completeness:
  1) Before converting, validate mapping keys cover the expected types, or at call-time handle missing mappings.
  2) Example handling strategy (described in words): call apply_renderable_mapping inside a try/except block catching KeyError to implement a fallback (skip conversion or apply a default mapping), catch AttributeError/TypeError to detect misconfigured mapping entries, and catch Exception to log and re-raise or abort on unexpected convert_to_class failures.
- Practical notes:
  - If you prefer subclass-aware matching (isinstance-style), perform that logic outside this helper and call convert_to_class on the resolved class explicitly; do not rely on apply_renderable_mapping for subtype matching.
  - Validate mapping values at application startup (e.g., assert all mapping[v].convert_to_class is callable) to fail early rather than at each conversion call.

## `src.ydata_profiling.report.presentation.flavours.flavours.get_html_renderable_mapping` · *function*

## Summary:
Returns a mapping that associates core Renderable types to their HTML-specific Renderable implementations so the HTML flavour renderer can look up the correct class to use for each core component.

## Description:
This function centralizes the pairing between the core presentation Renderable types (from the presentation core) and their HTML-specific implementations (from the HTML flavour). It imports the core Renderable classes and the corresponding HTML implementations and returns a dictionary whose keys are core component types and whose values are the HTML-specific component types.

Known callers:
- No explicit callers were found in the provided source subset. Typically, this mapping is consumed by a flavour/renderer registry or the HTML renderer construction code during report generation when the system resolves which concrete renderable class to instantiate for a given core Renderable type (for example: when the presentation layer chooses the "html" flavour and builds the rendering pipeline).

Why this is a separate function:
- Responsibility boundary: it centralizes and isolates the mapping logic for the HTML flavour so other code can obtain a complete, consistent mapping via a single function call rather than importing or constructing mappings inline. This avoids duplication and makes it easy to test or replace the mapping for the HTML flavour.

## Args:
- None.

## Returns:
- Dict[Type[Renderable], Type[Renderable]]: a dictionary mapping core Renderable classes (keys) to the corresponding HTML-specific Renderable classes (values).
  - Keys: the core types imported from ydata_profiling.report.presentation.core, including (but not limited to) Container, Variable, VariableInfo, Table, HTML, Root, Image, FrequencyTable, FrequencyTableSmall, Alerts, Duplicate, Dropdown, Sample, ToggleButton, Collapse, CorrelationTable.
  - Values: the HTML-specific classes imported from ydata_profiling.report.presentation.flavours.html, for example HTMLContainer, HTMLVariable, HTMLVariableInfo, HTMLTable, HTMLHTML, and so on.
  - Edge cases:
    - If new core types are added to the core module but not added to this mapping, they will not be present in the returned dictionary (caller must handle missing keys).
    - The returned dictionary is a plain Python dict; callers typically perform lookups by core type and instantiate the returned class.

## Raises:
- ImportError or ModuleNotFoundError: if the internal imports (either from the core module or the HTML flavour module) fail, the error will propagate. The function performs imports inside its body, so missing or misconfigured modules will cause an import-related exception at call time.
- No other exceptions are raised by the function body itself.

## Constraints:
- Preconditions:
  - The modules ydata_profiling.report.presentation.core and ydata_profiling.report.presentation.flavours.html must be importable and must expose the classes referenced in the function.
  - The types returned are expected to be subclasses of the Renderable base class; callers may rely on this but the function does not enforce runtime checks.
- Postconditions:
  - The function returns a dict mapping core Renderable types to HTML-specific types. The mapping is deterministic and contains exactly the pairs defined in the function body.
  - No global state is modified.

## Side Effects:
- None in typical operation: the function does not perform I/O, network calls, or mutate external/global state.
- The only observable side effect is the import-time execution when the function is called (module import semantics). If those imports execute module-level code, that may have side-effects (this is typical Python import behavior), but the function itself performs no additional side effects.

## Control Flow:
flowchart TD
    Start --> ImportCore["Import core Renderable types (inside function)"]
    ImportCore --> ImportHTML["Import HTML flavour Renderable types (inside function)"]
    ImportHTML --> BuildMap["Build dict mapping core types -> HTML types"]
    BuildMap --> ReturnMap["Return mapping dict"]
    ReturnMap --> End

## Examples:
- Basic lookup and use (illustrative):
    from ydata_profiling.report.presentation.flavours.flavours import get_html_renderable_mapping

    mapping = get_html_renderable_mapping()
    # To get the HTML class that should render a core Container:
    html_container_cls = mapping.get(Container)
    if html_container_cls is None:
        # handle missing mapping (fallback, error, or default)
        raise KeyError("No HTML renderable registered for Container")
    # instantiate (example; actual constructor args depend on the HTMLContainer implementation)
    html_container = html_container_cls(...)  # pass required constructor arguments

- Defensive usage pattern:
    mapping = get_html_renderable_mapping()
    try:
        html_varinfo_cls = mapping[VariableInfo]
    except KeyError:
        # Fallback to a generic renderer or skip rendering of this component
        html_varinfo_cls = DefaultHTMLVariableInfo
    instance = html_varinfo_cls(...)

## `src.ydata_profiling.report.presentation.flavours.flavours.HTMLReport` · *function*

## Summary:
Converts a pre-built presentation Root node and its immediate runtime type into the HTML flavour by applying the HTML renderable mapping, returning the same Root instance (typically mutated in-place).

## Description:
- Role and intent:
  - This function is a focused conversion entry-point that resolves the HTML-specific renderable class for a given Root node (and, by extension, the node's concrete runtime type) and performs the conversion using the central conversion helper. It does not traverse the tree itself; it converts the supplied Root instance according to an exact-type mapping and returns that instance for further processing or rendering.
- Known callers and typical pipeline stage:
  - No explicit direct callers were discovered in the provided snapshot. In typical usage within the report generation pipeline, this function is invoked when the presentation layer selects the "html" flavour and must convert an already-constructed renderable Root node into the HTML-specific implementations immediately prior to rendering or a second processing pass that expects flavour-specific behavior.
  - Typical trigger condition: the system has constructed a Root renderable tree using core Renderable classes and now needs to make that tree concrete for the HTML output flavour.
- Why this is extracted:
  - Responsibility boundary: it centralizes the simple but important step of (1) obtaining the HTML mapping and (2) applying the exact-type mapping conversion to the supplied Root. Keeping this as a small utility isolates flavour-selection logic, prevents duplication, and allows the conversion call-site to be a single, obvious operation within higher-level orchestration code.

## Args:
    structure (Root):
        - Type: Root (a core Renderable representing the top-level presentation node).
        - Required: yes (no default).
        - Expected value: an instance whose runtime type (type(structure)) is present as a key in the HTML renderable mapping returned by get_html_renderable_mapping.
        - Notes: the function uses the exact runtime type as the lookup key; subclass relationships are not considered by this function. If the mapping lacks an entry for the exact runtime type, a KeyError will be raised.

## Returns:
    Root:
        - The very same Root instance passed in (identity preserved). The instance will typically have been converted in-place to the HTML flavour by calling the mapped class's convert_to_class; conversion semantics depend on that implementation (commonly mutate __class__ and possibly other attributes).
        - Edge cases:
            - If an exception is raised during mapping lookup or conversion, the function does not return; the exception propagates to the caller.
            - There is no alternative return value; successful completion always returns the supplied structure.

## Raises:
    - ImportError / ModuleNotFoundError:
        - Condition: raised by get_html_renderable_mapping if required modules or classes cannot be imported when building the mapping.
    - KeyError:
        - Condition: the mapping does not contain an entry for type(structure). The function uses an exact-type lookup and will raise KeyError if the key is missing.
    - AttributeError:
        - Condition: the mapped value for the type does not provide the required attribute (convert_to_class).
    - TypeError:
        - Condition: the mapping object is not subscriptable, or the resolved convert_to_class attribute is not callable, or convert_to_class performs an invalid operation (for example, an incompatible __class__ assignment).
    - Any exception raised by convert_to_class:
        - Condition: convert_to_class implementations may perform arbitrary work (mutations, template loading, validation) and can raise ValueError, RuntimeError, or other exceptions; these propagate unchanged.

## Constraints:
- Preconditions:
    - The modules used to build the mapping (core presentation types and HTML flavour implementations) must be importable.
    - The supplied structure must be a Root instance whose exact runtime type is a key in the HTML mapping, or the caller must be prepared to handle KeyError.
    - The convert_to_class implementations referenced in the mapping must be safe to call on the provided instance (e.g., compatible class layout if they mutate __class__).
- Postconditions:
    - On normal return, the provided structure has been passed through the mapping's convert_to_class and will exhibit the behaviour of the HTML-specific implementation (per that implementation's semantics).
    - No new object is created by this function itself; it returns the original structure after conversion.

## Side Effects:
- In-place mutation of the provided structure is expected and common: convert_to_class typically mutates the instance (for example by assigning to __class__ and altering attributes).
- The function itself performs no I/O, network calls, or global state mutations. Any I/O or further side effects originate from convert_to_class implementations or from import-time behavior when building the mapping.
- The flavour argument forwarded to convert_to_class is the HTMLReport callable itself; convert_to_class implementations may use or ignore this value.

## Control Flow:
flowchart TD
    Start --> GetMap[get_html_renderable_mapping()]
    GetMap -->|ImportError/ModuleNotFoundError| MapImportError[Raise ImportError/ModuleNotFoundError]
    GetMap --> Apply[apply_renderable_mapping(mapping, structure, flavour=HTMLReport)]
    Apply -->|mapping missing key| KeyError[Raise KeyError] 
    Apply -->|mapped missing convert_to_class| AttrError[Raise AttributeError]
    Apply -->|convert_to_class not callable| TypeErr[Raise TypeError]
    Apply -->|convert_to_class raises| ConvertExc[Propagate exception from convert_to_class]
    Apply --> Success[Return structure]
    MapImportError --> End
    KeyError --> End
    AttrError --> End
    TypeErr --> End
    ConvertExc --> End
    Success --> End

## Examples (usage and error-handling guidance):
- Typical usage pattern (described):
  - A report assembly step has built a Root renderable using core Renderable classes. To prepare that tree for HTML output, call HTMLReport(root). On success, the same root instance will now behave according to the HTML-specific renderable implementations and can be passed to the HTML renderer.
- Defensive calling guidance:
  - If you cannot guarantee the mapping covers all possible runtime types you may pass, call HTMLReport inside a try/except block to handle KeyError (fallback behavior: skip conversion for unsupported node types, apply a default mapping, or abort with a descriptive error).
  - Anticipate and handle ImportError at system initialization if modules required for HTML flavour are optional in some deployments.
  - If convert_to_class implementations are untrusted or may perform complex operations, consider catching broad Exception to log and wrap errors with additional context before re-raising.

## `src.ydata_profiling.report.presentation.flavours.flavours.get_widget_renderable_mapping` · *function*

## Summary:
Return a dictionary mapping core Renderable types to their corresponding "widget" flavour Renderable implementations so the presentation layer can instantiate widget-specific renderable classes for each core semantic component.

## Description:
This utility constructs and returns the mapping used by the "widget" flavour of the presentation layer to translate canonical renderable types (defined in the core presentation API) into their widget-specific implementation classes.

Known callers within the codebase:
- No direct callers are present in this file. In typical usage this function is invoked by presentation factory/registry code that needs to obtain the flavour-specific mapping when rendering a report using the widget flavour (for example, when the system selects which concrete Renderable implementation to instantiate for a given logical component).

Why this is a separate function:
- It centralizes and documents the widget-flavour mapping in one place rather than scattering import/lookup logic across the codebase.
- Separating the mapping into a function makes it trivial to import the mapping lazily (deferring imports until needed), keeps imports local to the function scope to avoid import cycles, and simplifies testing or replacement of the mapping for different flavours.

## Args:
This function takes no arguments.

## Returns:
dict[Type[Renderable], Type[Renderable]]:
- A dictionary where each key is a core presentation Renderable subclass (the canonical type used by the reporting machinery) and the corresponding value is the widget-flavour Renderable subclass that implements that component for the widget frontend.
- The returned mapping contains explicit entries for the following core types (keys) mapped to their widget implementations (values):
  - Container -> WidgetContainer
  - Variable -> WidgetVariable
  - VariableInfo -> WidgetVariableInfo
  - Table -> WidgetTable
  - HTML -> WidgetHTML
  - Root -> WidgetRoot
  - Image -> WidgetImage
  - FrequencyTable -> WidgetFrequencyTable
  - FrequencyTableSmall -> WidgetFrequencyTableSmall
  - Alerts -> WidgetAlerts
  - Duplicate -> WidgetDuplicate
  - Dropdown -> WidgetDropdown
  - Sample -> WidgetSample
  - ToggleButton -> WidgetToggleButton
  - Collapse -> WidgetCollapse
  - CorrelationTable -> WidgetCorrelationTable

Edge-case return values:
- The function always returns the dictionary literal shown above. It does not return None or partial mappings.

## Raises:
- This function does not explicitly raise exceptions in its body.
- Import-time errors (ModuleNotFoundError, ImportError, AttributeError) can occur if the referenced core or widget classes are missing from their modules; these will propagate from the local imports at call time.

## Constraints:
Preconditions:
- The core Renderable classes and widget implementations referenced must be importable at runtime from their respective modules.
- Callers expect keys to be subclasses of the core Renderable type; the mapping is suitable only when those core classes are the canonical types used by the rest of the presentation system.

Postconditions:
- When the function returns successfully, the caller receives a complete mapping from canonical core Renderable classes to widget-specific concrete classes, suitable for use in lookups to select the widget implementation for a given core component.

## Side Effects:
- No I/O is performed (no filesystem, network, or stdout/stderr writes).
- No global state is mutated.
- The only side effect is performing local imports when the function executes; if those imports trigger module-level initialization in the imported modules, those module-level side effects (if any) will occur.

## Control Flow:
flowchart TD
    Start --> Import_Core_and_Widget_Types[Import core and widget classes (local imports)]
    Import_Core_and_Widget_Types --> Build_Mapping[Construct mapping dict literal]
    Build_Mapping --> Return_Mapping[Return the mapping]
    Return_Mapping --> End

## Examples:
Typical usage scenario (described in prose):

1. A presentation factory that renders a report in the "widget" flavour calls this function to obtain the mapping.
2. When the factory needs to render a component for which it has the core Renderable type (for example, Variable), it looks up the corresponding widget implementation in the returned mapping (mapping[Variable]) and instantiates that widget class (passing any required constructor args as expected by that widget implementation).
3. If an import error occurs when retrieving the mapping, the factory should treat it as a configuration or installation error and either fall back to a different flavour (if supported) or surface the error to the user.

Error-handling notes:
- Because missing imports will raise at call time, callers may choose to:
  - Catch ImportError/ModuleNotFoundError/AttributeError around the call and provide a clearer error message to the user.
  - Defer calling this function until they are certain that the widget flavour is in use and its dependencies are available.

## Implementation hints (for reimplementation):
- Keep imports local to the function to avoid import cycles and to defer import-time work until the mapping is needed.
- Return a plain dictionary literal mapping core types to widget classes.
- Ensure all referenced names are the actual classes (not instances or strings).

## `src.ydata_profiling.report.presentation.flavours.flavours.WidgetReport` · *function*

## Summary:
Convert a canonical Root renderable into its "widget" flavour in place and return the same Root instance.

## Description:
- What it does:
  - Obtain the widget-flavour mapping (core Renderable types -> widget Renderable classes).
  - Apply that mapping to the supplied Root instance by delegating to apply_renderable_mapping, which invokes the mapped class's convert_to_class(structure, flavour) to perform an in-place conversion.
  - Return the same Root instance after conversion.

- Known callers and typical context:
  - Presentation factories, report-assembly or traversal code that prepare a report for rendering in the "widget" flavour. Typical pipeline stage: invoked just before rendering or as part of a traversal that converts a pre-built canonical renderable tree into a flavour-specific representation.
  - In practice, code that selects the "widget" presentation flavour will call this to ensure each node uses the widget-specific implementation prior to calling render().

- Why this is a separate function:
  - Encapsulates the small, well-defined step of obtaining the widget mapping and applying it to a root Renderable. Keeps flavour-selection logic centralized (lazy imports, single point of change) and consistent across callers, avoiding duplication of mapping lookup and conversion invocation.

## Args:
    structure (Root): The top-level report Renderable to convert. Must be an instance whose runtime type appears as a key in the widget mapping returned by get_widget_renderable_mapping(). This function mutates the supplied instance in-place (via convert_to_class) and returns it.

Notes on interdependencies:
- The function depends on get_widget_renderable_mapping() to produce a complete mapping and on apply_renderable_mapping(mapping, structure, flavour) to perform the exact-type lookup and to call the mapped convert_to_class.
- The mapping uses exact runtime-type keys (type(structure)) — no isinstance/subclass matching is performed by apply_renderable_mapping.

## Returns:
    Root: The same Root instance passed in, after in-place conversion to the widget flavour. The instance's __class__ and/or nested content may be mutated by convert_to_class; no new object is returned.

Edge-case returns:
- The function always returns the input object on normal completion. If an exception occurs during mapping lookup, import-time resolution, or conversion, the exception propagates and no value is returned.

## Raises:
The function does not catch exceptions; callers must handle them. Possible exceptions include, but are not limited to:
    - ImportError / ModuleNotFoundError / AttributeError:
        - Trigger: get_widget_renderable_mapping performs local imports and they fail (missing modules or attributes).
    - KeyError:
        - Trigger: apply_renderable_mapping indexes the mapping with type(structure) and no entry exists for that exact runtime type.
    - TypeError:
        - Trigger: mapping is not subscriptable; or the resolved mapping entry does not expose a callable convert_to_class; or convert_to_class attempts an invalid __class__ assignment for the instance.
    - AttributeError:
        - Trigger: the mapped object lacks a convert_to_class attribute; or structure lacks expected attributes used by convert_to_class.
    - Any exception raised by the mapped convert_to_class implementation:
        - convert_to_class may raise ValueError, RuntimeError, or other errors; these propagate unchanged.

## Constraints:
- Preconditions:
    - structure must be a Root instance (or at least have the canonical runtime type used as a key in the widget mapping).
    - The runtime type of structure must appear as an exact key in the mapping returned by get_widget_renderable_mapping().
    - The mapped widget class must implement a callable convert_to_class(obj, flavour).
    - convert_to_class implementations must be safe to call on the provided instance (e.g., compatible __class__ assignment if used).

- Postconditions:
    - If the function returns normally, structure has been processed by the flavour-specific convert_to_class for its type; commonly this means structure.__class__ has been changed to the widget implementation and nested parts (e.g., Root.content["body"] and ["footer"]) have been visited via the flavour callable (WidgetReport), resulting in recursive conversion of nested Renderable nodes.

## Side Effects:
- In-memory mutation: convert_to_class commonly mutates structure in-place (for example by assigning structure.__class__ and/or mutating structure.content). Nested Renderable nodes (body, footer, etc.) are typically converted as part of convert_to_class and recursive flavour calls.
- No file, network, or stdout/stderr I/O is performed by WidgetReport itself. Any I/O is the responsibility of convert_to_class implementations or module import-time initializers.
- No global variables are modified by this function.

## Control Flow:
flowchart TD
    Start[Start WidgetReport(structure)] --> GetMap[get_widget_renderable_mapping()]
    GetMap --> Apply[apply_renderable_mapping(mapping, structure, flavour=WidgetReport)]
    Apply --> TypeKey[type(structure)]
    TypeKey --> Lookup{mapping contains type(structure)?}
    Lookup -- No --> RaiseKeyError[KeyError raised -> propagate] --> End
    Lookup -- Yes --> MappedClass[mapped = mapping[type(structure)]]
    MappedClass --> HasConvert{mapped has convert_to_class?}
    HasConvert -- No --> RaiseAttrError[AttributeError -> propagate] --> End
    HasConvert -- Yes --> CallConvert[Call mapped.convert_to_class(structure, WidgetReport)]
    CallConvert --> ConvertEffects[may mutate structure.__class__ and nested content]
    ConvertEffects --> NestedCalls{convert_to_class may call flavour on nested parts}
    NestedCalls -- Yes --> RecursiveApply[WidgetReport invoked for nested items -> repeat]
    NestedCalls -- No --> Continue[continue]
    Continue --> Return[Return structure]
    Return --> End

## Examples:
Typical usage (happy path):
1) Prepare a canonical Root instance (body/footer are Renderable instances):
   - root = Root(name, body, footer, style)
2) Convert to widget flavour and render using widget renderers:
   - widget_root = WidgetReport(root)
   - # widget_root is the same object, now converted to widget implementations; downstream code may call widget_root.render()

Example with error handling (guarding against missing mapping entries and import issues):
- try:
    widget_root = WidgetReport(root)
  except KeyError:
    # Missing mapping for this exact runtime type; fallback or log
    handle_missing_mapping(root)
  except (ImportError, AttributeError) as e:
    # Flavour implementation unavailable or misconfigured
    log_and_fail(e)
  except Exception:
    # Unexpected conversion failure: re-raise or handle as appropriate
    raise

Notes:
- Because mapping lookup is exact by runtime type, if root is an instance of a subclass not present as a key in the mapping, WidgetReport will raise KeyError. If subclass-aware conversion is desired, resolve the appropriate mapped class before calling apply_renderable_mapping or extend the mapping to include the subclass.
- When convert_to_class mutates __class__, ensure the target class layout is compatible to avoid TypeError at assignment time.

