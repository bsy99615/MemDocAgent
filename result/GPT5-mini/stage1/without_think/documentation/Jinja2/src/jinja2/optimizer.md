# `optimizer.py`

## `src.jinja2.optimizer.optimize` · *function*

## Summary:
Creates an Optimizer with the provided environment, runs it over the given AST node, and returns the (possibly transformed) AST node; the call is a thin wrapper that delegates the optimization pass to the Optimizer visitor and narrows the static type to nodes.Node.

## Description:
- Known callers within the provided code scan:
    - No direct callsites were discovered in the provided repository snapshot. 
    - Typical callers (outside the snapshot) are components of the template compilation pipeline that run AST transformation passes prior to code generation (for example: a template compiler, a template environment compilation step, or any tool that performs pre-compilation AST optimizations).
- Typical invocation context:
    - Called when a template AST (or a subtree) has been produced and the toolchain wants to perform a constant-folding / compile-time optimization pass using the supplied Environment (which may carry configuration or runtime-like information needed by Const construction).
- Why this is a standalone function:
    - Responsibility boundary: it is a convenience wrapper that builds and runs an Optimizer instance for a single node, keeping caller code concise and avoiding repeated optimizer instantiation logic scattered across the codebase.
    - It enforces a simple, single-call API for performing the optimization pass and communicates the expected input/output types via its signature.

## Args:
    node (nodes.Node):
        - The root AST node (or subtree) to run the optimization pass on.
        - Expected to be an instance of the AST node types used by the template system (nodes.Node or any concrete subclass).
        - Precondition: node should be a valid AST node; the function does not validate node shape beyond relying on the Optimizer.visit path.
    environment (Environment or None):
        - An Environment instance providing context used by the Optimizer and by nodes.Const.from_untrusted, or None if no environment context is required.
        - Although the function's annotation names Environment, the Optimizer accepts an explicit None as a valid value; callers may pass None to indicate "no environment".

## Returns:
    nodes.Node:
        - The returned object is the node returned by optimizer.visit(node), statically narrowed with a typing cast to nodes.Node.
        - Possible concrete outcomes:
            - The original node (if no transformation was performed).
            - A node returned by the optimizer/visitor traversal (this may be the original node, a modified node, or a replacement such as nodes.Const).
            - In particular, constant-folding optimizations performed by Optimizer may replace expression nodes with nodes.Const instances.
        - Note: the cast does not change the runtime value — it only conveys the expected static type.

## Raises:
    - Any exception raised by Optimizer.visit(node) will propagate to the caller. This includes:
        - Exceptions raised by traversal in the base visitor implementation.
        - Exceptions raised by node.as_const or nodes.Const.from_untrusted that are not handled by Optimizer.visit/generic_visit.
    - The optimize wrapper itself does not catch or translate exceptions.
    - (For clarity) nodes.Impossible raised inside node.as_const is handled inside Optimizer.generic_visit and will not propagate out of optimize when it occurs as part of constant-evaluation; however other exceptions from as_const or from Const construction will propagate.

## Constraints:
- Preconditions:
    - The caller must provide a valid AST node compatible with the visitor framework.
    - The environment parameter should be an Environment instance or None (explicit None is acceptable).
    - The runtime must have the Optimizer, nodes, and visitor infrastructure available and registered in imports used by the codebase.
- Postconditions:
    - The returned value is the node resulting from running the Optimizer visitor on the input node; after return, there is no further mutation performed by optimize itself.
    - If Optimizer replaced sub-expressions with constants, those replacements are reflected in the returned node.

## Side Effects:
- No I/O performed by the optimize wrapper itself (no file, network, or stdout activity).
- No global state is modified by this function directly.
- Side effects possible and not shielded by the wrapper:
    - Any side effects produced by Optimizer.visit (or subcomponents it calls) will occur and propagate (for example, if nodes.Const.from_untrusted or other construction routines have side effects, they will run).
    - Exceptions from deeper in the visitor chain propagate to the caller.

## Control Flow:
flowchart TD
  Start((start)) --> Instantiate[Instantiate Optimizer(environment)]
  Instantiate --> CallVisit[Call optimizer.visit(node)]
  CallVisit --> ReturnCast[Return t.cast(nodes.Node, result)]
  CallVisit -->|exception raised| Propagate[Propagate exception to caller]
  ReturnCast --> End((end))
  Propagate --> End

(Interpretation: the function has no branches except the possible propagation of exceptions from optimizer.visit.)

## Examples:
- Typical successful call (no error handling):
    # Assume `ast_root` is a nodes.Node and `env` is an Environment or None
    optimized = optimize(ast_root, env)
    # optimized is the AST after the Optimizer visitor pass; may contain nodes.Const replacements

- With error handling to catch visitor errors:
    try:
        optimized = optimize(ast_root, env)
    except Exception as e:
        # handle or log compilation/optimization errors
        raise

Notes and implementation hints for reimplementers:
- The function's body should:
    1. Instantiate Optimizer with the provided environment.
    2. Call the visitor entry point (Optimizer.visit) with the provided node.
    3. Return the visitor result, optionally narrowing the static type with typing.cast to nodes.Node.
- Avoid swallowing exceptions; let them propagate so caller code can handle compilation-time errors.

## `src.jinja2.optimizer.Optimizer` · *class*

## Summary:
Optimizer is a NodeTransformer subclass that walks AST nodes and attempts to replace expression nodes with constant nodes when the expression can be evaluated at compile time, using an optional Environment for Const construction.

## Description:
Optimizer performs a single-pass constant-folding optimization on AST expression nodes. For each visited node it:
1. Delegates traversal to the parent NodeTransformer via super().generic_visit(...) to allow child nodes to be processed and replaced first.
2. If the node returned from the parent visitor is an instance of nodes.Expr, it attempts to evaluate that expression to a Python value by calling node.as_const(context), where context is args[0] if a positional argument was supplied to generic_visit, otherwise None.
3. If node.as_const returns a value, it replaces the expression with nodes.Const.from_untrusted(value, lineno=node.lineno, environment=self.environment).
4. If node.as_const raises nodes.Impossible, the optimizer leaves the node unchanged.

Intended usage scenarios:
- As an AST transformation pass in a template compilation pipeline to fold compile-time constant expressions into literal constant nodes.
- Can be instantiated and run by compilers or toolchains that perform AST optimizations before code generation.

Motivation / responsibility:
- Purpose: safely convert provably-constant expressions into Const nodes to reduce runtime work and simplify later code generation.
- Boundary: does not attempt to evaluate expressions with runtime dependencies; relies on the node.as_const / nodes.Impossible contract to determine evaluability.

## State:
- environment: "t.Optional[Environment]"
    - Source signature: __init__(self, environment: "t.Optional[Environment]") -> None
    - Stored value: assigned directly to self.environment in __init__.
    - Valid values: an Environment instance or None (no default provided in the signature and callers must pass a value).
    - Invariant: self.environment is used only as the environment argument passed into nodes.Const.from_untrusted; Optimizer itself does not modify environment.

No other instance attributes are set by Optimizer.

Class invariants:
- After construction, self.environment remains available and unchanged by Optimizer methods.
- generic_visit preserves the semantics of NodeTransformer.generic_visit for traversal and only replaces nodes according to the exact logic described here.

## Lifecycle:
Creation:
- Instantiate with: Optimizer(environment)
    - environment must be provided (explicit None is acceptable).
Usage:
- Call optimizer.generic_visit(root_node, *maybe_context) or use the visitor entry point the surrounding framework expects (e.g., optimizer.visit(root_node) if provided by NodeTransformer).
- Typical order: instantiate -> call generic_visit/visit on AST root -> collect returned optimized AST.
- The first positional argument passed to generic_visit (if any) is forwarded as the context to node.as_const.

Destruction:
- No cleanup required. Optimizer does not manage external resources.

## Method Map:
- __init__(self, environment: "t.Optional[Environment]") -> None
- generic_visit(self, node: nodes.Node, *args: t.Any, **kwargs: t.Any) -> nodes.Node

Mermaid diagram:
graph TD
  A[Client] --> B[Optimizer.__init__(environment)]
  B --> C[Optimizer.generic_visit(node, *args, **kwargs)]
  C --> D[super().generic_visit(node, *args, **kwargs)]
  D --> E[returned node]
  E --> F{isinstance(node, nodes.Expr)?}
  F -- no --> G[return node]
  F -- yes --> H[node.as_const(args[0] if args else None)]
  H --> I{returns value or raises nodes.Impossible}
  I -- returns value --> J[nodes.Const.from_untrusted(value, lineno=node.lineno, environment=self.environment)]
  J --> G
  I -- raises nodes.Impossible --> G

(Interpretation: generic_visit delegates to the base visitor, checks for nodes.Expr, tries node.as_const with optional context, on success builds a nodes.Const via from_untrusted preserving lineno and environment; on nodes.Impossible returns the node unchanged.)

## Detailed behavior (step-by-step, matching code):
- Call signature: generic_visit(self, node: nodes.Node, *args: t.Any, **kwargs: t.Any) -> nodes.Node
- Step 1 (line present in source): node = super().generic_visit(node, *args, **kwargs)
  - The returned node may be identical to the input or a replacement produced by the parent visitor.
- Step 2: if isinstance(node, nodes.Expr):
  - This test determines whether the node represents an expression eligible for constant evaluation.
- Step 3: try:
    value = node.as_const(args[0] if args else None)
    return nodes.Const.from_untrusted(value, lineno=node.lineno, environment=self.environment)
  - The call to node.as_const forwards args[0] if there is at least one positional arg; otherwise it forwards None. The optimizer expects node.as_const to either return a Python value or raise nodes.Impossible.
  - On successful return, a nodes.Const is constructed using nodes.Const.from_untrusted with:
    - the computed value,
    - lineno taken from node.lineno,
    - environment equal to self.environment.
  - The created nodes.Const is returned immediately.
- Step 4: except nodes.Impossible: pass
  - If node.as_const raised nodes.Impossible, the exception is caught and execution continues to the final return.
- Step 5: return node
  - If the node was not a nodes.Expr, or as_const raised nodes.Impossible, the (possibly modified by super) node is returned unchanged.

## Inputs and outputs:
- Inputs:
  - __init__: environment argument (string-annotated type "t.Optional[Environment]").
  - generic_visit: node of type nodes.Node and arbitrary positional/keyword arguments forwarded to super and (for args[0]) to node.as_const.
- Outputs:
  - generic_visit returns an instance of nodes.Node. It may be the original node, a replacement returned by super().generic_visit, or a new nodes.Const created by nodes.Const.from_untrusted.

## Raises:
- __init__: does not raise any exceptions in the provided implementation.
- generic_visit:
  - nodes.Impossible: not propagated — it is caught when raised by node.as_const.
  - Any exception raised by super().generic_visit(...) will propagate to the caller.
  - Any exception raised by node.as_const other than nodes.Impossible will propagate to the caller.
  - Any exception raised by nodes.Const.from_untrusted will propagate to the caller.
  - The optimizer does not wrap or transform these exceptions.

## Edge cases and constraints (explicit, code-derived):
- If args is empty, None is passed to node.as_const (args[0] if args else None).
- If node returned from super().generic_visit does not have lineno, nodes.Const.from_untrusted is still called with lineno=node.lineno; if lineno is missing, that will cause the underlying call to fail (this reflects the code's direct use of node.lineno).
- Optimizer performs a single pass: if constant folding of a child expression enables folding of a parent expression only on a subsequent pass, callers must run the optimizer again to achieve the further folding.
- The class relies on the presence of nodes.Expr, nodes.Impossible, and nodes.Const.from_untrusted with the described semantics; reimplementers should provide these contracts.

## Example:
Assume nodes.Expr nodes implement as_const(context) which returns a Python value or raises nodes.Impossible, and nodes.Const.from_untrusted(value, lineno, environment) builds a Const node.

    # instantiate
    optimizer = Optimizer(environment)    # environment may be None

    # call with no context; generic_visit will pass None to as_const
    new_node = optimizer.generic_visit(some_node)

    # call with a context forwarded as args[0] to as_const
    context = {'allow_unsafe': False}
    new_node = optimizer.generic_visit(some_node, context)

Outcome:
- If some_node (after child visits) is a nodes.Expr and node.as_const(context) returns 42, new_node will be nodes.Const.from_untrusted(42, lineno=some_node.lineno, environment=environment).
- If node.as_const(context) raises nodes.Impossible, new_node will be the node returned by super().generic_visit unchanged.

### `src.jinja2.optimizer.Optimizer.__init__` · *method*

## Summary:
Store the provided optional Environment on the new Optimizer instance so instance methods can access runtime configuration.

## Description:
This constructor assigns the passed environment value to an instance attribute for later use by optimizer methods. In this class, generic_visit accesses self.environment when attempting to evaluate expression nodes to constants; therefore the environment is stored on the instance rather than passed through each method.

Known callers:
- No direct callers are present in this file snapshot. This is the class constructor invoked when an Optimizer instance is created.

Why this is a separate method:
- It is the standard initializer for the Optimizer object and centralizes setup of per-instance state (the environment) that other methods rely on.

## Args:
    environment ( "t.Optional[Environment]" ):
        The Environment instance providing runtime/configuration context, or None when no environment is available. The annotation in the source is exactly "t.Optional[Environment]". There is no default value in the signature; callers must supply an argument (which may be None).

## Returns:
    None

## Raises:
    This constructor does not raise any exceptions.

## State Changes:
    Attributes READ:
        - (none)
    Attributes WRITTEN:
        - self.environment: assigned to the provided argument value.

## Constraints:
    Preconditions:
        - No preconditions are enforced by the constructor; any value consistent with the annotation is accepted.
    Postconditions:
        - After return, the instance has an attribute self.environment whose value equals the provided argument.

## Side Effects:
    - No I/O or external service calls.
    - Mutates only the newly created instance by setting self.environment.

### `src.jinja2.optimizer.Optimizer.generic_visit` · *method*

## Summary:
Perform a post-recursive visit of an AST node and, for expression nodes that can be evaluated statically, replace them with a safe Const node constructed from the evaluated value; otherwise return the node produced by the superclass traversal unchanged.

## Description:
This method overrides the NodeTransformer traversal hook to add a constant-folding optimization for expression nodes. It first calls the superclass generic_visit to perform recursive traversal and any transformations that happen there. The node variable is then the value returned by that superclass call. If that returned node is an expression (nodes.Expr), the method attempts to evaluate it to a constant value and, on success, returns a nodes.Const created via nodes.Const.from_untrusted(...). If evaluation is impossible, the method suppresses that specific failure and returns the non-constant node.

Known callers and invocation context:
- Called by the AST traversal mechanism (the NodeTransformer visiting machinery) for each node encountered during an optimization pass over the template AST.
- Typical lifecycle stage: during an optimizer pass invoked after parsing and before template code generation/compilation, to perform constant folding of expression nodes.

Why this logic is a separate method:
- Encapsulates a reusable constant-folding optimization applied uniformly to every expression node encountered during traversal.
- Keeps traversal concerns (delegated to the superclass) separate from optimization behavior, avoiding duplication of constant-evaluation logic across visitors.

## Args:
    self: Optimizer instance.
    node (nodes.Node): The AST node to visit. After the initial call to super().generic_visit, this is the node value returned by the superclass (may be the same object or a transformed node).
    *args (Any): Positional arguments forwarded to super().generic_visit. If present, the first positional argument (args[0]) is forwarded as the evaluation context to node.as_const(...). If no positional args are provided, None is passed to node.as_const(...).
    **kwargs (Any): Keyword arguments forwarded unchanged to super().generic_visit. This method does not inspect keyword arguments.

## Returns:
    nodes.Node:
        - If the node returned by super().generic_visit(...) is an instance of nodes.Expr and can be evaluated statically, returns a nodes.Const created by calling:
            nodes.Const.from_untrusted(value, lineno=node.lineno, environment=self.environment)
          where value is the Python value returned by node.as_const(context), context equals args[0] if provided, else None.
        - Otherwise, returns the node value returned by super().generic_visit(...) without modification.
        - No other sentinel or special return values are used.

## Raises:
    - Exceptions raised by super().generic_visit(...) are propagated unchanged.
    - Any exception other than nodes.Impossible raised by node.as_const(...) or nodes.Const.from_untrusted(...) is propagated unchanged.
    - nodes.Impossible: explicitly caught and suppressed. This exception may be raised by node.as_const(...) when the expression cannot be computed statically, or by nodes.Const.from_untrusted(...) when the conversion is deemed unsafe/untrustworthy; in either case the exception is caught and the method falls back to returning the non-constant node.

## State Changes:
    Attributes READ:
        - self.environment: read and passed as the environment argument to nodes.Const.from_untrusted when creating a replacement Const node.

    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - The Optimizer instance must have an attribute self.environment (Optimizer.__init__ sets this).
        - node must be a nodes.Node-compatible object. If node is or becomes an expression (nodes.Expr), it must implement:
            * as_const(context) -> value or raise nodes.Impossible when static evaluation is impossible.
            * lineno attribute that can be used when creating a replacement Const node.
        - If present, args[0] must be a value acceptable as the evaluation context for node.as_const(...).

    Postconditions:
        - If evaluation to a constant succeeded, the returned node is a nodes.Const whose lineno equals the original node.lineno and whose environment argument equals self.environment.
        - If evaluation failed with nodes.Impossible, the returned node is the value produced by super().generic_visit(...) (no constant replacement).
        - No attributes on self are modified by this call.

## Side Effects:
    - The AST may be mutated by replacing an expression node with a Const node when constant folding succeeds; this method returns the replacement node and the caller is expected to use it in the tree.
    - Calls node.as_const(...) and nodes.Const.from_untrusted(...); any side effects those functions perform (including reading the provided environment or performing internal validations) are external to this method.
    - This method performs no I/O and makes no external network or service calls itself.

