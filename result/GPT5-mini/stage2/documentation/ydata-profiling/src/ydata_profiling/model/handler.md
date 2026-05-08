# `handler.py`

## `src.ydata_profiling.model.handler.compose` · *function*

## Summary:
Creates a single callable that composes a sequence of callables into a pipeline where each function's output becomes the positional-argument input for the previous function; when an intermediate function returns a boolean (type exactly bool), the previous function is called with the original arguments instead of the boolean result.

## Description:
This helper builds a composed function from an ordered sequence of callables. The composed callable accepts arbitrary positional arguments and executes the functions in the order they are given (the last function in the sequence is invoked first), wiring outputs of each stage into the next stage by unpacking them as positional arguments.

Known callers in this codebase:
- No direct callers were discovered in the provided repository snapshot. If you are integrating this function elsewhere, typical uses are:
  - Building a small pipeline of transformers where each stage returns a tuple (args for the prior stage).
  - Building predicate/transform mixes where a stage can return a boolean to signal "do not forward this stage's result; instead use the original call arguments".

Why this is extracted into its own function:
- It centralizes the non-trivial composition logic (unpacking of results, special-case boolean handling, and identity behavior for an empty sequence) into one reusable utility. This prevents duplication and clarifies the contract for how pipeline stages pass data to each other.

## Args:
    functions (Sequence[Callable]):
        - A sequence (e.g., list or tuple) of callables to compose.
        - Each callable must accept positional arguments (no requirement for keyword-only parameters).
        - Conventions expected by this compose implementation:
            * The last callable in the sequence (executed first) will be called with the original positional arguments passed to the composed callable.
            * If a callable returns a value whose type is exactly bool (type(res) == bool), that boolean is treated as an indicator to NOT pass that boolean as input to the previous function; instead the previous function is invoked with the original positional arguments.
            * If a callable returns any non-bool value, it is expected to be an iterable of values (e.g., tuple, list) which will be unpacked and forwarded as positional arguments to the previous function (i.e., f(*res)).
        - Allowed values:
            * An empty sequence is allowed and results in an identity function: the composed callable returns the tuple of arguments it was called with.
        - No default — functions must be supplied (can be empty sequence).

## Returns:
    Callable: A function that accepts arbitrary positional arguments (*args) and returns whatever the left-most (first in the provided sequence) callable returns when driven through the composition rules described above.
    Possible return behaviors:
        - If functions is empty: returns the identity behavior — the composed callable returns a tuple containing the original positional arguments.
        - If all intermediate returns are non-bool iterables: behaves like nested calls where each stage's iterable output is unpacked into the previous stage.
        - If an intermediate return is type exactly bool: the previous function is called with the original positional arguments; the boolean value itself is not forwarded.

## Raises:
    - TypeError: If an intermediate function returns a non-bool non-iterable (e.g., int), attempting to unpack it with f(*res) will raise a TypeError. This error is not caught internally and will propagate to callers.
    - TypeError or other exceptions from any composed function (argument mismatch, runtime errors) will propagate unchanged — compose does not wrap or translate exceptions.

## Constraints:
    Preconditions:
        - Each callable must be callable with the inputs it will receive according to the composition rules.
        - The typical expectation is that non-bool returns are iterables whose elements are intended as positional arguments for the previous callable.
        - Callers must not rely on isinstance checks for booleans: the implementation uses type(res) == bool; subclasses of bool (rare) will not be treated as bool here.

    Postconditions:
        - After calling the composed callable, one of:
            * The final left-most function's return value is returned to the caller.
            * Or an exception raised by one of the functions propagates outward.
        - No global state is modified by compose itself.

## Side Effects:
    - compose is pure with respect to external state: it returns a new callable but performs no I/O, network calls, file writes, or global mutations.
    - Side effects may occur when the returned callable is invoked if the composed functions perform side effects; compose does not add any additional side effects.

## Control Flow:
flowchart TD
    Start[Start: call composed(*args)]
    -> CallLast[Call last function g = functions[-1] with original args]
    -> CheckRes{type(res) == bool ?}
    ->|true| CallPrevWithOriginal[Call previous function f with original args]
    ->|false| CallPrevWithUnpacked[Call previous function f with unpacked res: f(*res)]
    CallPrevWithOriginal --> CheckIfMore{more functions?}
    CallPrevWithUnpacked --> CheckIfMore
    CheckIfMore -->|yes| Repeat[repeat boolean check/unpack for next previous function]
    CheckIfMore -->|no| End[Return final result]
    Start --> CallLast

Notes:
- The diagram represents the iterative reduce construction: each composed pair enforces the boolean-vs-unpacked branching for passing values backward through the pipeline.

## Examples:
1) Basic unpacking pipeline
    - Given:
        g = lambda x, y: (x + 1, y * 2)
        f = lambda a, b: a * b
    - Compose and call:
        composed = compose([f, g])
        result = composed(2, 3)
    - Execution:
        g(2,3) -> (3, 6) ; f(* (3,6)) -> 18
    - result == 18

2) Boolean short-circuit to original args
    - Given:
        g = lambda x, y: True            # returns a bool indicator
        f = lambda x, y: x - y
    - Compose and call:
        composed = compose([f, g])
        result = composed(5, 2)
    - Execution:
        g(5,2) -> True (type bool) ; because it is exactly bool, call f with original args: f(5,2) -> 3
    - result == 3

3) Empty sequence (identity)
    - composed = compose([])
    - composed(1, 'a') -> returns (1, 'a') as a tuple

4) Error example (non-iterable forwarded)
    - Given:
        g = lambda x: 42   # integer, not iterable and not bool
        f = lambda a, b: a + b
    - Compose and call:
        composed = compose([f, g])
        composed(1) -> raises TypeError when attempting f(*42)
    - Caller should catch TypeError if using functions that may return non-iterables.

## Implementation notes and gotchas:
    - The boolean check uses type(res) == bool (exact-type equality). Using isinstance(res, bool) would treat bool subclasses as booleans; this implementation does not.
    - The implementation assumes that when a stage returns a non-bool, it is safe and intended to be unpacked as positional arguments for the previous stage.
    - If you need keyword-argument forwarding or richer control flow (e.g., passing named outputs forward), extend or replace this helper accordingly.

## `src.ydata_profiling.model.handler.Handler` · *class*

## Summary:
A dispatcher that stores and executes ordered pipelines of callables for Visions types, propagating handlers along the typeset's directed edges so derived types inherit handlers from their ancestors.

## Description:
Handler is constructed with:
- mapping: a dictionary mapping stringified Visions type names to lists of callables (pipelines).
- typeset: a VisionsTypeset whose base_graph describes directed relationships among types.

On creation, Handler completes the mapping by traversing the typeset.base_graph and accumulating handlers: handlers registered for a source type are prepended to handlers of target types along each directed edge. After initialization callers use handle(dtype, *args) to run the composed pipeline for a specific type and obtain the pipeline's result.

Instantiate Handler when you need a single object responsible for:
- Combining per-type handler lists into full pipelines that include ancestor handlers (DAG propagation).
- Dispatching an input (positional args) through the pipeline for a specific type.

Typical callers:
- Any profiling/processing code that needs to apply a sequence of transformations or extractors for a Visions-typed variable.
- Factory code that builds a Handler from a catalog of functions and a VisionsTypeset before bulk processing.

Motivation:
- Separates two concerns: (1) constructing per-type pipelines that respect type inheritance/edges, and (2) invoking those pipelines on demand. The DAG-completion step is extracted to ensure handler propagation is deterministic, testable, and performed exactly once on construction.

## State:
Attributes (public):
- mapping: Dict[str, List[Callable]]
    - Description: Maps stringified Visions type identifiers to ordered lists of callables (pipelines).
    - Expected contents: Each value should be a list (or list-like sequence) of callables. Keys are typically produced by str(type) for Visions types present in typeset.base_graph.
    - Constraints / invariants:
        * For any key k present in typeset.base_graph converted via str(type), mapping must contain mapping[k] at construction time, otherwise _complete_dag will raise KeyError.
        * After initialization, mapping values for a target type begin with handlers from all ancestor/source types according to the topological order of the line graph of the base_graph.
- typeset: VisionsTypeset
    - Description: The Visions typeset whose base_graph defines directed edges between types (used to propagate handlers).
    - Constraints:
        * typeset.base_graph must be a directed acyclic graph (DAG). If not, topological sorting of the line graph will raise networkx.NetworkXUnfeasible.

Class invariants (must hold after __init__ and between public method calls):
- For every directed edge u -> v in typeset.base_graph, mapping[str(v)] starts with the elements of mapping[str(u)] (i.e., ancestor handlers are prepended).
- All mapping values remain sequences of callables (mutating mapping to non-sequences may cause runtime TypeError).

## Lifecycle:
Creation:
- Required arguments: mapping: Dict[str, List[Callable]], typeset: VisionsTypeset.
- Construction steps:
    1. Assign mapping and typeset to attributes.
    2. Invoke _complete_dag() to propagate handlers along the typeset's edges.
- Preconditions for successful construction:
    * mapping contains entries for every involved type key (stringified) used by typeset.base_graph.
    * mapping values are list-like (support + concatenation).
    * typeset.base_graph is a DAG (so topological sorting succeeds).

Usage:
- After construction, call handle(dtype, *args, **kwargs) to execute the pipeline associated with dtype.
- handle looks up mapping.get(dtype, []), composes the list of callables into a single callable using compose, and invokes it with the provided positional arguments.
- Note: keyword arguments passed to handle are accepted by the signature but ignored (not forwarded to pipeline callables).
- Typical ordering:
    1. Construct Handler(mapping, typeset)
    2. For each variable/type encountered, call handler.handle(dtype, *args) to run the pipeline.
- No required ordering among multiple handle() calls; state is not mutated by handle.

Destruction / cleanup:
- Handler owns no external resources and requires no explicit cleanup.
- No context-manager protocol implemented; simply discard when done.

## Method Map:
graph TD
    A[__init__(mapping, typeset)] --> B[_complete_dag()]
    B --> C[mapping mutated to include ancestor handlers]
    C --> D[handle(dtype, *args)]
    D --> E[lookup funcs = mapping.get(dtype, [])]
    E --> F[op = compose(funcs)]
    F --> G[result = op(*args)]
    G --> H[return result]

Notes:
- compose is an external helper that builds a callable pipeline from a list of functions; its semantics (unpacking, boolean short-circuit) affect how pipeline stages pass values to one another.

## Raises:
Exceptions that may be raised during construction or method calls:

__init__ / _complete_dag:
- KeyError:
    - Trigger: mapping does not contain entries for some str(from_type) or str(to_type) that appear in typeset.base_graph.
- networkx.NetworkXUnfeasible (or networkx.exception.NetworkXUnfeasible):
    - Trigger: the line graph of typeset.base_graph is not a DAG (contains cycles); networkx.topological_sort fails.
- TypeError:
    - Trigger: mapping values are not list-like sequences that support concatenation with + (for example, a None or non-sequence), or concatenation results in incompatible types.

handle:
- Any exception raised by compose or by the composed callables will propagate.
    - TypeError: likely triggers include attempting to unpack a non-iterable into positional arguments, or calling a function with incompatible arguments.
    - AttributeError / RuntimeError / ValueError: may arise from pipeline function implementations.
- Note: handle itself will not raise KeyError because it uses mapping.get(dtype, []), but will raise if compose expects callables and mapping contains non-callable elements.

## Example:
- Setup:
    - Prepare mapping where keys are the stringified names of Visions types and values are lists of callables. Each callable should accept positional arguments and return either:
        * an iterable of positional arguments to be passed to the previous function in the pipeline, or
        * a value of type exactly bool to indicate "call previous function with the original arguments" per compose semantics.
    - Provide a VisionsTypeset with a populated base_graph that references the same type identifiers used as mapping keys.

- Typical sequence:
    1. handler = Handler(mapping, typeset)
        - This mutates mapping so that derived types inherit handlers from ancestors.
    2. result = handler.handle("SomeType", value1, value2)
        - This composes the final handler list for "SomeType" and executes the pipeline, returning the pipeline's left-most result.
    3. Use result (often a dict produced by the left-most pipeline function) as needed.

Implementation notes and gotchas:
- mapping keys must match str(type) used by Visions types in typeset.base_graph; mismatches lead to KeyError during DAG completion.
- The DAG propagation performed in _complete_dag is in-place: the original mapping passed to the constructor is mutated.
- handle ignores keyword arguments — pass everything as positional args if pipeline functions expect parameters.
- compose's behavior (boolean short-circuit and iterable unpacking) determines how intermediate function outputs are forwarded; ensure pipeline functions conform to that contract to avoid TypeError at runtime.

### `src.ydata_profiling.model.handler.Handler.__init__` · *method*

## Summary:
Initializes the Handler instance by storing the provided mapping and typeset on the object, then completes the per-type handler pipelines by invoking the DAG-propagation routine which mutates the mapping in-place.

## Description:
Known callers and context:
- Called during normal object construction whenever a Handler is instantiated (e.g., handler = Handler(mapping, typeset)).
- Typical call sites include profiling pipelines or factory code that build a Handler from a catalog of functions and a VisionsTypeset prior to bulk processing.
- Lifecycle stage: construction/initialization. This method is invoked once per Handler instance before any subsequent handle(...) calls.

Why this logic is a separate method:
- The DAG-completion algorithm is a non-trivial graph traversal and mapping accumulation (propagating handlers along the Visions typeset directed edges). Extracting it into _complete_dag keeps __init__ concise and ensures the propagation occurs exactly once at construction. It improves testability and separates concerns: assignment of attributes vs. propagation logic.

## Args:
    mapping (Dict[str, List[Callable]]):
        - A dictionary that maps stringified Visions type identifiers to ordered lists of callables (pipelines).
        - Required. Expected to contain keys for every type referenced by typeset.base_graph (converted via str(type)).
        - Values must be list-like sequences of callables supporting concatenation with + (typical type: List[Callable]).
    typeset (VisionsTypeset):
        - The VisionsTypeset whose base_graph defines directed edges between types; used to propagate handlers along ancestor→descendant relationships.
        - Required. Its base_graph must be a directed acyclic graph (DAG) for successful propagation.
    *args:
        - Accepted but ignored by this implementation; present for compatibility with potential subclasses or factories that forward extra args.
    **kwargs:
        - Accepted but ignored by this implementation; present for compatibility with potential subclasses or factories that forward extra kwargs.

## Returns:
    None
    - The constructor does not return a value. Its observable effects are stored on the created object (attributes and in-place mutation of the provided mapping).

## Raises:
    KeyError:
        - Trigger: self.mapping does not contain an expected key for a type name encountered in typeset.base_graph (str(from_type) or str(to_type)). Raised by the _complete_dag call when it attempts to read or write mapping entries for graph types that are missing.
    networkx.NetworkXUnfeasible (networkx.exception.NetworkXUnfeasible):
        - Trigger: the line graph derived from typeset.base_graph contains a cycle so topological sorting fails. Propagated from networkx.topological_sort invoked inside _complete_dag.
    TypeError:
        - Trigger: mapping values are not list-like sequences supporting concatenation (for example, None or an incompatible type), causing the concatenation operation in _complete_dag (mapping[str(from_type)] + mapping[str(to_type)]) to fail.
    Any exception raised by _complete_dag:
        - The constructor delegates DAG completion to _complete_dag; any exception raised there (including those above) propagates out of __init__.

## State Changes:
Attributes READ:
    - self.mapping (read by _complete_dag after assignment)
    - self.typeset (read by _complete_dag after assignment)
    - self.typeset.base_graph (accessed by _complete_dag during traversal)

Attributes WRITTEN:
    - self.mapping (assigned to reference the provided mapping argument)
    - self.typeset (assigned to reference the provided typeset argument)
    - In-place mutations performed by _complete_dag:
        * Existing mapping entries mapping[str(to_type)] are overwritten (assigned) to be concatenations that prepend ancestors' handler lists. The mapping object passed in is mutated in-place; no deep copy is made.

## Constraints:
Preconditions (what must be true before calling):
    - mapping must be a dict-like object with keys equal to the stringified Visions types referenced by typeset.base_graph.
    - Each mapping value must be a list-like sequence of callables that supports concatenation with +.
    - typeset.base_graph must represent a directed acyclic graph (DAG); otherwise topological sorting over its line graph will fail.

Postconditions (guarantees after return):
    - self.mapping and self.typeset attributes are set to the passed arguments.
    - mapping is mutated so that for every directed edge u -> v in typeset.base_graph, mapping[str(v)] begins with the elements of mapping[str(u)] (handlers from ancestors are prepended). This accumulation follows a topological ordering over the line graph, so handlers from more ancestral nodes appear earlier in each list.
    - No new keys are added to mapping beyond those already present; any missing keys cause exceptions instead of being implicitly created.

## Side Effects:
    - In-place mutation of the mapping argument: the original mapping object provided by the caller is modified. Callers should not rely on an unmodified mapping after constructing a Handler.
    - No file, network, or external I/O is performed.
    - Delegates to networkx APIs (e.g., nx.line_graph and nx.topological_sort) via _complete_dag; their exceptions may propagate.
    - Potentially non-trivial CPU/memory work: list concatenations across edges may be expensive for large graphs or long handler lists.

### `src.ydata_profiling.model.handler.Handler._complete_dag` · *method*

## Summary:
Propagates and accumulates handler functions along the typeset's directed edges so that each target type's mapping is prepended with the handlers of its source (ancestor) types; mutates self.mapping in-place.

## Description:
This method is invoked during the Handler object's initialization to "complete" the directed-acyclic-type graph (DAG) mapping. It iterates over the line graph of self.typeset.base_graph in topological order, treating each node of the line-graph as an ordered edge (from_type, to_type) of the original base_graph. For every such edge it prepends the handlers registered for the source type onto the handlers list for the target type:
    mapping[str(to_type)] = mapping[str(from_type)] + mapping[str(to_type)]

Known callers:
    - Handler.__init__: called once during object construction to ensure mappings include handlers inherited along the DAG before any handling operations (e.g., Handler.handle) are used.

Why this is a separate method:
    - The logic performs a graph traversal and mapping accumulation that is conceptually distinct from initialization and handling; extracting it keeps __init__ concise and makes the propagation behavior testable and reusable.

## Args:
    None

## Returns:
    None
    - The method always returns None and performs its work by mutating self.mapping.

## Raises:
    - KeyError: if mapping lacks an entry for str(from_type) or str(to_type). This occurs when the provided self.mapping does not contain keys for the types present in self.typeset.base_graph.
    - networkx.NetworkXUnfeasible (or networkx.exception.NetworkXUnfeasible): if the line graph produced from self.typeset.base_graph is not a DAG (i.e., contains a cycle). This is raised by networkx.topological_sort.
    - TypeError: if the values in self.mapping under the relevant keys are not list-like objects that support the + operator for concatenation (e.g., None or non-sequence types), the expression mapping[str(from_type)] + mapping[str(to_type)] may raise a TypeError.

## State Changes:
Attributes READ:
    - self.typeset
    - self.typeset.base_graph
    - self.mapping (reads mapping[str(from_type)] and mapping[str(to_type)] for relevant keys)

Attributes WRITTEN:
    - self.mapping[str(to_type)] for each edge (from_type, to_type) encountered; each assigned value is the list concatenation of the source handlers followed by the existing target handlers.

## Constraints:
Preconditions:
    - self.typeset.base_graph must be a directed acyclic graph (DAG) so that a topological ordering exists for the line graph. If this is not true, topological_sort will raise an exception.
    - self.mapping should contain entries (typically lists of callables) for every type name present in self.typeset.base_graph when converted via str(type). If absent, a KeyError will be raised.
    - The values in self.mapping for relevant keys should be list-like sequences (List[Callable]) so that list concatenation semantics apply and produce a new list.

Postconditions:
    - For every directed edge u -> v in self.typeset.base_graph, after execution mapping[str(v)] will begin with the elements of mapping[str(u)] (i.e., handlers from u are prepended to v).
    - Because the iteration follows a topological ordering over the line graph, mappings are propagated along multi-edge paths: mapping[str(v)] will include handlers from all ancestors of v in the base_graph, in an order consistent with the topological traversal (ancestors earlier in topological order appear earlier in the concatenated list).
    - No new keys are added to self.mapping except by overwriting existing mapping[str(to_type)] entries; keys not present will cause an error rather than being implicitly created.

## Side Effects:
    - In-place mutation of self.mapping only; no file, network, or other external I/O.
    - Reliant on networkx APIs: nx.line_graph and nx.topological_sort. Exceptions raised by those calls propagate out.
    - Potentially expensive list concatenations: performance depends on number of edges and cumulative length of handler lists (may have O(E * L) cost where L is typical list length).

### `src.ydata_profiling.model.handler.Handler.handle` · *method*

## Summary:
Dispatches to the pipeline of callables registered for the given data type and returns that pipeline's result, leaving the Handler instance state unchanged.

## Description:
This method looks up a sequence of callables associated with dtype in self.mapping, composes them into a single pipeline callable via compose, and invokes the composed callable with the supplied positional arguments.

Known callers and lifecycle:
- No direct callers were discovered in the provided repository snapshot. Typical usage: invoked during a processing/feature-generation phase where a Handler instance is used to apply the registered pipeline for a specific variable data type. It is called after Handler has been constructed (and its mapping completed by _complete_dag), when a caller needs the result produced by the pipeline for a dtype.
- Typical pipeline stage: Handler is instantiated with a mapping of dtype -> list[Callable]. After initialization and _complete_dag(), callers call handle(dtype, *args) to run that dtype's pipeline.

Why this is a separate method:
- Encapsulates the dispatching behavior (lookup, composition, and invocation) in a single place so callers only need to specify dtype and positional args. Keeps mapping management and call-time behavior decoupled and testable.

## Args:
    dtype (str):
        - The key used to look up the pipeline in self.mapping.
        - Expected to be the stringified name of a Visions type; however any hashable value may be used as a lookup key. If not present, an empty pipeline is used.
    *args (Any):
        - Positional arguments forwarded to the composed pipeline callable.
        - There is no restriction at the Handler level; the arguments must satisfy the first-invoked callable in the composed pipeline (the last function in the stored list) according to compose's contract.
    **kwargs:
        - Accepted but ignored by this implementation. Passing keyword arguments has no effect.

## Returns:
    dict:
        - Declared return type is dict (method annotation). In practice this method returns whatever the left-most callable in the composed pipeline returns.
        - Common/expected case: a dict produced by the pipeline's left-most function.
        - Edge cases:
            * If no functions are registered for dtype (empty sequence), compose returns an identity callable and this method will return a tuple of the original positional arguments.
            * If the pipeline's left-most function returns a non-dict value (e.g., tuple, scalar), that value is returned unchanged.

## Raises:
    - Any exception raised by compose or by one of the composed callables will propagate to the caller. Common examples:
        * TypeError: if a pipeline stage returns a non-bool non-iterable and compose attempts to unpack it for the prior stage, or if a pipeline function is called with incompatible arguments.
        * TypeError / AttributeError: if self.mapping contains non-callable elements where callables are expected.
    - This method does not itself raise KeyError because it uses mapping.get(dtype, []).

## State Changes:
    Attributes READ:
        - self.mapping: used to retrieve the list of callables for dtype.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - Handler instance has been initialized and _complete_dag() has already run (ensured by __init__).
        - dtype should correspond to the intended mapping key; if dtype is not present the method will operate on an empty pipeline.
        - The callables stored in self.mapping[dtype] must conform to the expectations of compose:
            * Each element must be callable.
            * Non-bool return values from intermediate stages must be iterable and intended to be unpacked as positional arguments for the previous stage.
    Postconditions:
        - No mutation of Handler state is performed.
        - The caller receives the raw return value of the pipeline (or the tuple of original positional args if the pipeline is empty).

## Side Effects:
    - The method itself performs no I/O or external service calls.
    - Side effects may occur because the composed callables may perform I/O, mutate external state, or raise exceptions; those effects are caused by the pipeline functions, not by handle.

## Implementation notes and gotchas:
    - kwargs are ignored — callers expecting keyword forwarding will not see their kwargs forwarded to pipeline functions.
    - The method relies on compose semantics: e.g., a pipeline function that returns type exactly bool will trigger compose's boolean-short-circuit behavior (compose will cause the previous function to be called with the ORIGINAL arguments rather than the boolean).
    - If mapping contains an empty list for dtype, the method returns the tuple of positional arguments (identity behavior).
    - Although annotated to return dict, callers should be defensive and validate the return value if a dict is required.

## `src.ydata_profiling.model.handler.get_render_map` · *function*

## Summary:
Returns a mapping from high-level variable type names to their corresponding rendering callables used by the reporting subsystem, allowing callers to look up how to render a variable report by its type.

## Description:
This function centralizes the association between logical variable types (strings) and the rendering functions implemented in the report structure module. It performs a local (lazy) import of the rendering implementations and returns a dictionary that callers can use to find the appropriate renderer for a given variable type.

Known callers within the codebase:
- No direct callers are present in this single-file extract. In the larger profiling/report-generation pipeline, typical callers are components that build or render variable/column reports (for example, report builders or template generators) that need a renderer based on a variable's detected type.

Why this is a separate function:
- Encapsulates the canonical mapping in one place so the mapping can be reused and changed in a single location.
- Performs a lazy import of the report rendering module to avoid import-time side effects and to reduce top-level import cost for modules that do not need rendering.
- Keeps caller code concise: callers only request this mapping and use it; they don't need to know the concrete module or function names.

## Args:
- None

## Returns:
- Dict[str, Callable]: A dictionary that maps string type names to callables (rendering functions).
  - The mapping contains the following keys and associated callable targets (callables are the functions defined in ydata_profiling.report.structure.variables):
    - "Boolean" -> render_boolean
    - "Numeric" -> render_real
    - "Complex" -> render_complex
    - "Text" -> render_text
    - "DateTime" -> render_date
    - "Categorical" -> render_categorical
    - "URL" -> render_url
    - "Path" -> render_path
    - "File" -> render_file
    - "Image" -> render_image
    - "Unsupported" -> render_generic
    - "TimeSeries" -> render_timeseries
  - Each value is a callable object; callers should consult the implementations in ydata_profiling.report.structure.variables for the renderer's expected signature and behavior.

Edge-case return behavior:
- The function always returns a dictionary with the keys listed above. It does not return None or an empty mapping in normal execution.

## Raises:
- This function does not explicitly raise exceptions itself.
- Possible exceptions:
  - ImportError / ModuleNotFoundError if the module ydata_profiling.report.structure.variables cannot be imported at runtime.
  - Any exception raised during the module import (e.g., if that module executes code that raises) will propagate to the caller.

## Constraints:
Preconditions:
- None required by this function beyond a working Python environment.
- For successful lazy import, the package ydata_profiling.report.structure.variables must be importable.

Postconditions:
- After returning, the caller receives a dict[str, Callable] containing the canonical mapping described above.
- The module ydata_profiling.report.structure.variables will have been imported (cached on sys.modules for subsequent imports).

## Side Effects:
- Lazy import: the function executes a local import statement of ydata_profiling.report.structure.variables; that import may run module-level code in that module.
- No file, network, or external state mutations are performed by this function itself.
- No global variables in this module are modified by this function.

## Control Flow:
flowchart TD
    Start --> Import_Module[Lazy import ydata_profiling.report.structure.variables]
    Import_Module --> Build_Map[Construct render_map dict with fixed keys]
    Build_Map --> Return_Map[Return render_map]
    Import_Module -->|import raises| Propagate_Error[Propagate ImportError or other exception]

## Examples (usage pattern described in prose):
- Typical usage pattern:
  1. A report-builder component calls this function to obtain the renderer map at the start of rendering.
  2. The builder looks up a renderer for a variable type string (for example, "Numeric") using dictionary access or .get().
  3. If a renderer callable is found, the builder invokes that callable with the appropriate variable summary/context. If not found, the builder falls back to a default renderer or an "Unsupported" renderer.
- Error handling recommendation:
  - Protect the initial call with exception handling if the import of rendering implementations may fail in the deployment environment. For example: attempt to get the map in a try/except ImportError block and fall back to a minimal set of safe renderers or emit a clear error message.
- Example scenario (described):
  - A report generator detects a column as type "DateTime". It calls this function to get the render_map, retrieves the render_date callable with render_map["DateTime"], and then calls that callable with the column's summary data to produce the report fragment for that column. If the "DateTime" key were unexpectedly absent, the generator should use render_map.get("Unsupported") or otherwise handle the missing renderer gracefully.

