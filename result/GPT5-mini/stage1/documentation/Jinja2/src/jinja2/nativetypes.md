# `nativetypes.py`

## `src.jinja2.nativetypes.native_concat` · *function*

## Summary:
Attempt to join an iterable of values into a single string and parse it as a Python literal; returns the parsed native value when possible, otherwise returns the raw concatenated string, a single non-string item unchanged, or None for an empty input.

## Description:
This function accepts an iterable of values and produces a native Python value when the concatenated text represents a valid Python literal. It is typically used where template-engine logic needs to combine multiple value fragments and, if possible, interpret the result as a Python literal (numbers, tuples, lists, dicts, booleans, None, strings, etc.). 

Known callers within the provided context:
- None were provided in the input snapshot. (No direct call sites are available in the supplied files.) 

Why this is a separate function:
- The function centralizes the specific behavior of (1) efficient handling of iterables and generators, (2) a single-item fast-path that preserves non-string objects, (3) concatenation to a single string when necessary, and (4) a best-effort conversion from the concatenated string into a native Python object using AST literal parsing. Extracting this logic avoids duplicating generator handling, single-item edge-case logic, and the safe literal parsing everywhere it is needed.

## Args:
    values (typing.Iterable[typing.Any]):
        An iterable producing zero or more items. Items may be of any type.
        - If the iterable is empty, the function returns None.
        - If the iterable yields exactly one item and that item is not a str, that item is returned unchanged.
        - If the iterable yields one or more items and at least one is a str (or multiple items exist), all items are converted to str and concatenated in iteration order before attempting to parse.

    Notes on interdependencies:
        - If values is a generator (i.e., an instance of types.GeneratorType), the function consumes the first two items to determine behavior and, if more items exist, re-chains the consumed head back to the remaining generator so that no items are lost in concatenation.

## Returns:
    typing.Optional[typing.Any]
    The result depends on the input:
    - None: if the input iterable yields no items.
    - The single non-string object: if the iterable yields exactly one item that is not an instance of str.
    - A parsed Python object: if the concatenated string (the string form of each item joined in order) successfully parses to a Python literal using AST parsing and literal evaluation. Examples of parsed results: int, float, tuple, list, dict, bool, None, or str (when the concatenated content is a quoted string literal).
    - The raw concatenated string: if parsing fails (literal_eval raises ValueError, SyntaxError, or MemoryError), then the plain concatenated string is returned.

    All possible return types are therefore: None, any non-str single item, or any Python object that can be produced by ast.literal_eval from the concatenated text, or plain str.

## Raises:
    This function catches and suppresses exceptions raised by the literal parsing stage:
    - Does NOT propagate ValueError, SyntaxError, or MemoryError raised during parsing; these are intercepted and cause the function to return the raw concatenated string instead.
    - The function itself does not explicitly raise any exceptions in the provided implementation. Errors raised before parsing (for example, errors from iterating a broken iterator) will propagate normally.

## Constraints:
    Preconditions:
        - The argument must be an iterable. Passing a non-iterable will raise a TypeError when the function attempts to iterate.
        - If a generator is passed, it should be ok to partially consume the generator (the function consumes up to two items to inspect them, and if more items exist the function reconstructs iteration so all items are used).
    Postconditions:
        - The input iterable will be fully consumed by the function (either directly or via re-chaining); callers should not expect to reuse the iterator afterwards.
        - The return value will be one of: None, a single original non-string item, a Python literal parsed from the concatenated string, or the raw concatenated string.

## Side Effects:
    - No I/O is performed (no file, network, or stdout/stderr writes).
    - No global state or external resources are modified.
    - The input iterable is consumed (which is a mutation of iterator state). Passing a generator will exhaust it.

## Control Flow:
flowchart TD
    Start([Start]) --> Head[Collect first two items via islice(values, 2)]
    Head --> |no items| ReturnNone[Return None]
    Head --> |one item| SingleCheck{Is item a str?}
    SingleCheck --> |not str| ReturnItem[Return the single non-str item]
    SingleCheck --> |is str| ConcatPath[Prepare raw = item]
    Head --> |>=2 items| GenCheck{Is original values a GeneratorType?}
    GenCheck --> |yes| Rechain[values = chain(head, values)]
    GenCheck --> |no| SkipRechain[Do not rechain]
    Rechain --> BuildRaw[raw = "".join(str(v) for v in values)]
    SkipRechain --> BuildRaw
    BuildRaw --> TryParse[Try: parsed = literal_eval(parse(raw, mode="eval"))]
    TryParse --> |success| ReturnParsed[Return parsed]
    TryParse --> |ValueError/SyntaxError/MemoryError| ReturnRaw[Return raw]

## Examples:
- Empty iterable:
    Input: an empty list iterator => returns None

- Single non-string:
    Input: iter([42]) => returns integer 42 (the original object, not converted to string)

- Concatenation and successful parse:
    Input: iter(["1", "2"]) => concatenated raw "12" => parsed by literal_eval => int 12 is returned

- Concatenation and parse failure:
    Input: iter(["a", "b"]) => concatenated raw "ab" => parsing raises SyntaxError => returns "ab"

- Generator handling:
    Input: a generator that yields "1", "0", " + 2" => function re-chains the first two items back to remaining generator, concatenates all items to "10 + 2", tries to parse; if parsing fails it's returned as raw.

- Error handling:
    The function never propagates ValueError, SyntaxError, or MemoryError from the parsing stage; those result in the raw concatenated string being returned so callers can continue to operate with the textual result.

## `src.jinja2.nativetypes.NativeCodeGenerator` · *class*

## Summary:
NativeCodeGenerator is a focused CodeGenerator subclass that helps emit native-Python representations for constant child nodes and writes minimal surrounding source text for non-constant children during template code generation.

## Description:
NativeCodeGenerator provides helper methods used by a template CodeGenerator pipeline to either inline child nodes as Python-native constants or to emit simple pre/post text fragments around non-constant children.

Typical scenarios and callers:
- Invoked by higher-level code generation logic that traverses template AST nodes and delegates per-child emission concerns to these helpers.
- Callers supply:
  - node: an AST child (nodes.Expr) whose value may be constant,
  - frame: a Frame whose eval_ctx is used for constant evaluation,
  - finalize: a CodeGenerator._FinalizeInfo-like object that supplies per-child emission metadata (see State).

Motivation and responsibility:
- Keep constant folding logic centralized and small: try to convert children to native constants when possible (to embed them directly), otherwise provide a simple pair of pre/post hooks for emitting surrounding source.
- This class does not itself traverse ASTs nor emit full expression code — it only implements the small, well-scoped helpers called by the surrounding CodeGenerator logic.

## State:
- Instance attributes:
  - NativeCodeGenerator declares no new instance attributes. It relies on attributes and methods inherited from CodeGenerator, notably:
    - write(text: str) -> None: appends text to the current output buffer. All methods that write rely on this method being present.
- External-context values used by methods:
  - frame (Frame): used for constant evaluation via frame.eval_ctx. Methods expect frame to have an attribute eval_ctx that node.as_const can accept.
  - finalize (CodeGenerator._FinalizeInfo): expected shape and constraints:
    - src: Optional[str] — may be None or a string (possibly empty). If src is not None, _output_child_pre will write finalize.src and _output_child_post will write a literal ")" after the child emission. The code checks only for None, so an empty string is allowed and produces no visible prelude.
    - const: Callable[[t.Any], t.Any] — a callable used to convert a raw evaluated constant into the finalize-specific representation for non-TemplateData nodes. The method _output_child_to_const calls finalize.const(const) and returns its result. The precise semantics of this callable are defined by the caller/CodeGenerator pipeline.
- Class invariants:
  - Methods assume write(text: str) exists and appends to the output buffer.
  - node.as_const(frame.eval_ctx) should return a Python literal value when the node is const-evaluable; otherwise, callers must handle nodes.Impossible or other exceptions raised by node.as_const.
  - has_safe_repr(const) must be consulted before inlining a constant; if it returns False, nodes.Impossible is raised by _output_child_to_const.

## Lifecycle:
- Creation:
  - Constructed using the CodeGenerator base class constructor. NativeCodeGenerator does not add or require constructor arguments.
  - No additional initialization is performed by this subclass.

- Usage / method sequencing:
  - Typical pattern for emitting a child:
    1. Attempt to inline: call _output_child_to_const(node, frame, finalize).
       - If it returns a value (not raising), use that value as the inlined/native representation for the child.
       - If nodes.Impossible is raised (constant cannot be safely represented), fall back to the non-constant emission path.
    2. Non-constant fallback: call _output_child_pre(node, frame, finalize), then emit the child's expression using the surrounding generator logic, then call _output_child_post(node, frame, finalize).
  - There is no required destruction or cleanup specific to NativeCodeGenerator beyond what CodeGenerator provides.

## Methods (signatures must match source):
- staticmethod _default_finalize(value: t.Any) -> t.Any
  - Summary: Identity function used as a minimal finalize handler.
  - Args:
    - value (t.Any): any Python value.
  - Returns:
    - t.Any: the same value passed in (no transformation).
  - Side effects: none.

- _output_const_repr(self, group: t.Iterable[t.Any]) -> str
  - Summary: Produce a Python literal representation for a group of values joined as strings.
  - Behavior: returns repr("".join([str(v) for v in group])) exactly as implemented.
  - Args:
    - group (t.Iterable[t.Any]): iterable of values to be stringified and concatenated.
  - Returns:
    - str: the repr() of the joined string.
  - Side effects: none.

- _output_child_to_const(
    self, node: nodes.Expr, frame: Frame, finalize: CodeGenerator._FinalizeInfo
  ) -> t.Any
  - Summary: Attempt to evaluate node to a constant and return a finalize-appropriate representation.
  - Behavior:
    - Calls node.as_const(frame.eval_ctx) to obtain a constant value.
    - If has_safe_repr(const) is False, raises nodes.Impossible().
    - If node is an instance of nodes.TemplateData, returns the raw const (no finalize.const call).
    - Otherwise, returns finalize.const(const).
  - Args:
    - node (nodes.Expr): the child AST node being queried for const-ness.
    - frame (Frame): evaluation frame; used for frame.eval_ctx in node.as_const().
    - finalize (CodeGenerator._FinalizeInfo): carries at least src and const as described in State.
  - Returns:
    - t.Any: either the raw constant (for TemplateData) or the result of finalize.const(const) for other constants.
  - Raises:
    - nodes.Impossible: when the constant value exists but has_safe_repr(const) returns False, indicating the value cannot be safely inlined.
    - Any exception raised by node.as_const(...) or finalize.const(...) will propagate to the caller.

- _output_child_pre(
    self, node: nodes.Expr, frame: Frame, finalize: CodeGenerator._FinalizeInfo
  ) -> None
  - Summary: Emit the leading source fragment for a non-constant child if finalize.src is provided.
  - Behavior:
    - If finalize.src is not None, calls self.write(finalize.src).
    - Otherwise does nothing.
  - Args:
    - node (nodes.Expr): child node (unused by this method but provided for API symmetry).
    - frame (Frame): frame (unused by this method but provided for API symmetry).
    - finalize (CodeGenerator._FinalizeInfo): uses finalize.src.
  - Returns:
    - None
  - Raises:
    - Propagates exceptions from self.write if write fails.

- _output_child_post(
    self, node: nodes.Expr, frame: Frame, finalize: CodeGenerator._FinalizeInfo
  ) -> None
  - Summary: Emit the trailing source fragment for a non-constant child if finalize.src is provided.
  - Behavior:
    - If finalize.src is not None, calls self.write(")").
    - Otherwise does nothing.
  - Args:
    - node (nodes.Expr): child node (unused here).
    - frame (Frame): frame (unused here).
    - finalize (CodeGenerator._FinalizeInfo): uses finalize.src presence as a flag.
  - Returns:
    - None
  - Raises:
    - Propagates exceptions from self.write if write fails.

## Method Map:
flowchart LR
    A[_default_finalize(value: t.Any)] --> B[_output_const_repr(group: t.Iterable[t.Any])]
    B --> C[_output_child_to_const(node: nodes.Expr, frame: Frame, finalize)]
    C -->|calls node.as_const(frame.eval_ctx)| D[got const]
    D -->|if not has_safe_repr(const)| E[nodes.Impossible raised]
    D -->|if has_safe_repr and node is TemplateData| F[return const]
    D -->|if has_safe_repr and node not TemplateData| G[return finalize.const(const)]
    C --> H[_output_child_pre(node, frame, finalize)]
    H -->|if finalize.src is not None| I[self.write(finalize.src)]
    I --> J[emit child expression (external)]
    J --> K[_output_child_post(node, frame, finalize)]
    K -->|if finalize.src is not None| L[self.write(")")]

Note: "emit child expression (external)" denotes the emission performed by other CodeGenerator logic between pre and post.

## Raises:
- __init__:
  - NativeCodeGenerator defines no __init__; any exceptions during construction would come from CodeGenerator.__init__.
- Methods:
  - nodes.Impossible is raised by _output_child_to_const when has_safe_repr(const) is False.
  - node.as_const(...) and finalize.const(...) may raise exceptions that are propagated to callers.
  - self.write(...) may raise exceptions (e.g., I/O or buffer errors) which will propagate.

## Example (pseudocode usage pattern):
- Setup:
  - generator: a NativeCodeGenerator instance (constructed via CodeGenerator API)
  - frame: Frame with frame.eval_ctx
  - finalize: object with attributes:
      - src: Optional[str]
      - const: Callable[[t.Any], t.Any]

- Try to inline:
  - Call _output_child_to_const(node, frame, finalize)
  - If it returns a value V, use V as the child's inlined/native representation.
  - If it raises nodes.Impossible, fall back:
      - Call _output_child_pre(node, frame, finalize)
      - Emit the node's expression by invoking other generator methods
      - Call _output_child_post(node, frame, finalize)

Notes:
- The class is intentionally minimal and designed to be used only as part of the larger CodeGenerator pipeline that handles traversal and full expression emission.
- Implementers recreating this class must ensure the CodeGenerator base supplies write(), and that frame and finalize match the shapes and semantics described above.

### `src.jinja2.nativetypes.NativeCodeGenerator._default_finalize` · *method*

## Summary:
A stateless identity finalize function defined as a static method that returns the given value unchanged; used where a finalize callable is required but no transformation should occur.

## Description:
Known callers and context:
- There are no direct callers of this method by name within this file. It is defined as a static method on NativeCodeGenerator so it can be supplied wherever the generator pipeline expects a finalize callable.
- Typical lifecycle usage: in code generation phases that accept a finalize function to convert or represent evaluated values, this method can be used when no conversion or formatting is needed (i.e., to leave values as-is).

Why this is a separate method:
- Encapsulating the identity behavior in a named static method makes the "no-op" finalize behavior explicit and easily passed around to callers that accept finalize callables, avoiding ad-hoc special-casing at call sites.

## Args:
    value (t.Any): Any Python object or value. Accepts None and mutable objects.

## Returns:
    t.Any: The exact same object passed in; identity is preserved for mutable objects (no copy is performed).

## Raises:
    None: The function body performs no checks and does not raise any exceptions itself.

## State Changes:
Attributes READ:
    - None (does not read self or any object state)

Attributes WRITTEN:
    - None (does not modify self or external attributes)

## Constraints:
Preconditions:
    - None enforced by the function. Callers are free to pass any value.

Postconditions:
    - The returned value is identical to the input (same reference for mutable objects).
    - No side effects or state mutations are introduced by this method.

## Side Effects:
    - None. No I/O, no external calls, and no mutation of external state beyond returning the provided reference.

### `src.jinja2.nativetypes.NativeCodeGenerator._output_const_repr` · *method*

## Summary:
Return the Python source representation (repr) of the concatenation of the given iterable's elements converted to strings. This produces a single string suitable for embedding as a Python string literal in emitted native code.

## Description:
This method takes an iterable of values, converts each element to its string form, concatenates them, and returns the repr(...) of the resulting string. It is a small utility used during native code emission to produce a safe Python literal representation of grouped constant pieces.

Known callers and context:
- No direct call sites were present in the provided class snippet. Conceptually, this method is intended to be called by native code generation routines when multiple constant pieces (for example, adjacent TemplateData nodes or finalized constants) need to be represented as a single Python string literal in generated source.
- Lifecycle stage: used during the "emit native Python source" stage of template compilation, when constant string parts are collected and must be written into generated code as valid Python string literals.

Why this is a separate method:
- Centralizes the logic for producing a Python literal representation of a grouped set of values, ensuring consistent quoting/escaping via repr.
- Keeps higher-level code generation routines focused on control flow and assembly rather than on the mechanics of converting grouped constants to a source-safe literal.
- Improves reuse and testability by isolating a single responsibility.

## Args:
    group (typing.Iterable[typing.Any]):
        An iterable of values whose string forms should be concatenated. Elements may be of any type; each element will be converted using str(element) before concatenation.
        - Allowed values: any iterable (list, tuple, generator, etc.) whose iteration does not raise unexpected exceptions.
        - Empty iterable is allowed.

## Returns:
    str:
        The return value is the result of repr(concatenated_string), i.e. a Python source representation of the concatenated string. Example results include "''", "'abc'", or '"line\nbreak"' depending on the content.
        - Edge cases:
            * If group is empty, returns repr("") which is "''".
            * If elements include characters that require escaping, that is handled by repr (escape sequences and quotes are represented according to Python's repr rules).

## Raises:
    TypeError:
        If the provided group is not actually iterable, Python will raise a TypeError when attempting to iterate; this method does not catch it.
    Any exception raised by an element's __str__:
        If calling str(v) for any element v raises an exception, that exception will propagate.
    Any exception raised during iteration:
        If the iterable raises while iterating (for example, a generator that raises), that exception will propagate.

## State Changes:
    Attributes READ:
        - None (this implementation does not access any self.<attr> fields)
    Attributes WRITTEN:
        - None (this method does not modify self or external state)

## Constraints:
    Preconditions:
        - group must be an iterable (supporting iteration).
        - Iteration and conversion to str must not raise unexpected exceptions for normal operation.
    Postconditions:
        - No mutation of self or input objects is performed by this method.
        - The returned string is a valid Python literal representation (as produced by repr) of the concatenation of str() applied to each element in the iteration order.

## Side Effects:
    - None intrinsic to this method: no I/O, no external service calls, and no mutations of objects outside self (beyond any side effects that may occur during iteration or str() conversion of elements, which are not caused by this method itself).

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_to_const` · *method*

## Summary:
Convert a child expression node into a code-generation-safe constant representation, returning the raw constant for template text nodes and delegating non-text constants to the finalize helper; raises nodes.Impossible if the node is not a safe, representable constant.

## Description:
This helper is used during native-code generation to turn a child expression (nodes.Expr) into a constant value or a finalized constant representation suitable for embedding into generated code. Typical callers are code-generation helpers that need to inline or emit the value of a child node when that child is a compile-time constant. It is separated into its own method to centralize:
- the logic for calling node.as_const with the current evaluation context,
- the safety check using has_safe_repr, and
- the special-case handling of raw template data versus other constant types that require finalization.

Lifecycle stage: invoked during the code generation / finalization phase when walking the template AST to produce native output (i.e., when a child node may be emitted directly as a constant).

Why this method exists separately:
- Encapsulates the constant-extraction + safety-check + finalization steps in one place so all call sites get consistent behavior.
- Keeps code-generation visitor code concise by hiding the constant handling details.
- Ensures the TemplateData special-case (return raw constant) is applied uniformly.

## Args:
    self: instance of NativeCodeGenerator (method bound to this class).
    node (nodes.Expr): The AST expression node to convert. Must implement as_const(eval_ctx) which returns a Python value for constant expressions or raise nodes.Impossible if the expression is not statically evaluable.
    frame (Frame): Current code generation frame. This method uses frame.eval_ctx as the evaluation context passed to node.as_const.
    finalize (CodeGenerator._FinalizeInfo): Finalization helper that exposes a const(value) method used to obtain a code-generation representation for non-template-data constants.

## Returns:
    Any:
    - If node is a nodes.TemplateData instance, returns the raw Python constant value returned by node.as_const(frame.eval_ctx) (typically a string).
    - Otherwise returns the result of finalize.const(const), i.e., the finalized representation for the constant appropriate for the surrounding code generator.
    - There is no further transformation performed by this method: it either returns the raw const for TemplateData or whatever finalize.const returns for other constants.

## Raises:
    nodes.Impossible:
    - If node.as_const(frame.eval_ctx) itself raises nodes.Impossible (i.e., the expression is not a compile-time constant), that exception propagates.
    - If node.as_const(...) returns a value but has_safe_repr(const) returns False, this method raises nodes.Impossible to indicate the value cannot be safely represented in generated source.

## State Changes:
    Attributes READ:
    - None of self's attributes are directly read by this method.
    - The method does use frame.eval_ctx (accessed by calling node.as_const(frame.eval_ctx)).

    Attributes WRITTEN:
    - None. This method does not modify attributes on self or frame itself.

## Constraints:
    Preconditions:
    - node must be an expression node that implements as_const(eval_ctx) and, for TemplateData, should return a Python value representing template text.
    - frame must provide an eval_ctx attribute appropriate for passing into node.as_const.
    - finalize must implement a const(value) method that accepts the Python constant and returns a codegen finalization object/value.

    Postconditions:
    - If the method returns without raising, the returned value is guaranteed to be either:
        * the raw Python constant returned by node.as_const(...) when node is TemplateData, or
        * the value produced by finalize.const(...) for other constant types.
    - If the method raises nodes.Impossible, the caller can assume the node is not usable as a safe compile-time constant (either because it isn't a compile-time constant or because it has no safe source-code representation).

## Side Effects:
    - The method itself performs no I/O.
    - finalize.const(const) may have side effects (e.g., registering the constant in a constants pool or returning a reference/token that depends on finalize's internal state). Any such side effects are caused by finalize.const and are not performed directly by this method.

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_pre` · *method*

## Summary:
Writes the source fragment provided by the finalize info to the generator via self.write when that fragment is present, leaving generator state unchanged otherwise.

## Description:
This method is invoked by the native code generation pipeline when emitting a child expression's prelude (the piece of source that must come before the child's own emitted code). It is implemented as a small, separate helper so the logic for emitting a finalize-provided source fragment is centralized and can be reused or paired with a corresponding post-emission helper (see _output_child_post which writes a trailing ")" when applicable).

Known callers and context:
- Called from code-generation logic responsible for emitting child expression nodes as part of producing native template code. The exact call sites are not present in this snippet; within this module it is grouped with _output_child_post and _output_child_to_const and intended to be used as the "pre" emission step for a child node.

Why this is a separate method:
- The method encapsulates the single responsibility of emitting a finalize-provided source fragment (if any). Separating it avoids duplicating the conditional write around child-emission code and pairs cleanly with the corresponding post method.

## Args:
    node (nodes.Expr): The child expression AST node being emitted. This implementation does not inspect or modify the node but accepts it to conform to the child-emission helper interface.
    frame (Frame): The current compilation Frame provided by the code generator. Not used by this method but supplied for interface compatibility with other child-emission helpers.
    finalize (CodeGenerator._FinalizeInfo): A finalize-info object created by the code generator that may contain:
        - src: Optional[str] — a source fragment to be emitted before the child. If src is None, nothing is emitted by this method.
        - (other finalize helpers/members may exist in the finalize object; this method only accesses finalize.src)

## Returns:
    None

## Raises:
    AttributeError: If the provided finalize object does not have a 'src' attribute, an AttributeError will be raised when this method attempts to access finalize.src.
    Any exception raised by self.write(finalize.src) will propagate to the caller. This method does not catch or convert exceptions from self.write.

## State Changes:
Attributes READ:
    - self.write (method attribute is looked up and invoked)
    - finalize.src (reads the attribute value)

Attributes WRITTEN:
    - None of the object's attributes are assigned to by this method.

Note: Although no self.<attr> fields are directly assigned, calling self.write may mutate internal generator output state; see Side Effects.

## Constraints:
Preconditions:
    - finalize must be an object exposing a 'src' attribute (which may be None or a string).
    - self must implement a write method that accepts the type stored in finalize.src (typically a str).

Postconditions:
    - If finalize.src is not None, self.write(finalize.src) has been invoked exactly once.
    - If finalize.src is None, no call to self.write is made by this method.

## Side Effects:
    - Invokes self.write(finalize.src) when finalize.src is not None. The concrete effect of that call depends on the implementation of self.write (for example, appending to the generated output buffer or stream); this method does not itself perform I/O.

### `src.jinja2.nativetypes.NativeCodeGenerator._output_child_post` · *method*

## Summary:
Conditionally emit a single closing parenthesis to the generator output by calling the generator's write method when the provided finalize descriptor contains a non-None source snippet.

## Description:
This is a minimal post-emission helper on NativeCodeGenerator intended to be run after emitting a child expression. Its sole purpose is to close a wrapper started by the corresponding pre-emission helper in the same class (_output_child_pre) when a finalizer source snippet is present.

Concrete behavior:
- The method checks whether finalize.src is not None. If that condition holds, it calls self.write with a single character: a closing parenthesis.
- If finalize.src is None, the method performs no action.

Why separate:
- The method isolates the post-emission (closing) step from pre-emission logic; the class also defines _output_child_pre which writes the opening snippet when finalize.src is present. Keeping pre/post separate preserves symmetry and simplifies the calling code that surrounds child emission.

Known relationships:
- Companion to NativeCodeGenerator._output_child_pre (same class). No other callers are referenced in this method.

## Args:
    self: NativeCodeGenerator instance.
    node (nodes.Expr): The child expression node passed by the caller. This method does not read or use this parameter.
    frame (Frame): The current compilation frame. This method does not read or use this parameter.
    finalize (CodeGenerator._FinalizeInfo): An object carrying finalizer information. This method only reads its attribute src (tested against None).

## Returns:
    None

## Raises:
    This method does not explicitly raise exceptions. Indirect exceptions may propagate from self.write if that callable raises.

## State Changes:
Attributes READ:
    - finalize.src: inspected for None to decide whether to emit output.
    - self.write: the callable is looked up and invoked when the condition is met.

Attributes WRITTEN:
    - The method does not assign to any self.<attr> attributes.
    - Invoking self.write is expected to mutate the code generator's output buffer/stream (the specific buffer attribute is not referenced here).

## Constraints:
Preconditions:
    - finalize must have an attribute named src (it may be None or a string-like value).
    - The caller should ensure that, if finalize.src is not None, emitting a closing parenthesis is syntactically appropriate for the already-emitted surrounding text.

Postconditions:
    - If finalize.src is not None, self.write has been called exactly once with the string ")".
    - If finalize.src is None, no calls are made and the generator state is unchanged by this method.

## Side Effects:
    - Calls self.write(")"), which mutates the generator's external output buffer or stream (implementation-dependent).
    - No file, network, or other external I/O is performed by this method itself.

## `src.jinja2.nativetypes.NativeEnvironment` · *class*

## Summary:
A minimal Environment subclass configured for "native" template generation: it selects a native-focused code generator and a concatenation routine that attempts to produce Python-native values from concatenated fragments.

## Description:
NativeEnvironment exists to provide a ready-to-use Environment specialization whose template compilation and concatenation behavior are tuned for producing native Python values when possible.

When to instantiate:
- Use this class when you need an Environment that emits or works with native-Python representations of template expressions and that applies a best-effort conversion from concatenated textual fragments into Python literals.
- Typical high-level callers are the application bootstrap or factory code that constructs an Environment for template compilation and rendering. The instance is used anywhere a normal Environment would be used (creating templates from strings/files, compiling templates, rendering).

Motivation and responsibility boundary:
- Instead of duplicating configuration at call sites, NativeEnvironment centralizes two environment-level customizations:
  1. code_generator_class — the specific CodeGenerator subclass responsible for emitting "native" code fragments (see NativeCodeGenerator).
  2. concat — a callable used to join multiple child fragments and, when possible, parse the joined text into a Python literal (see native_concat).
- NativeEnvironment does not implement compilation or rendering logic itself; it relies entirely on the base Environment implementation for those behaviors. Its responsibility is only to supply the environment-specific code generator and concat policy.

References:
- NativeCodeGenerator documentation (src.jinja2.nativetypes.NativeCodeGenerator) — describes the semantics expected of code_generator_class.
- native_concat documentation (src.jinja2.nativetypes.native_concat) — describes the concat callable's exact behavior and return guarantees.

## State:
Attributes (class-level; inherited instance behavior follows from Environment):

- code_generator_class: type
  - Description: The CodeGenerator subclass the Environment should instantiate/use when generating code for templates.
  - Concrete value in this class: NativeCodeGenerator (a CodeGenerator subclass tailored for native/Python-friendly emission).
  - Required properties:
    - Must be a subclass of the CodeGenerator base used by the template compilation pipeline.
    - Instances of this class are expected to implement write(text: str) and the small helper API described in the NativeCodeGenerator doc.

- concat: callable (stored as a staticmethod)
  - Description: A callable used by template code-generation/rendering to join multiple value fragments and, when possible, produce a native Python object.
  - Concrete value in this class: native_concat wrapped as a staticmethod.
  - Expected signature and behavior:
    - Accepts an iterable of values (typing.Iterable[typing.Any]).
    - Returns typing.Optional[typing.Any]: one of None, the single original non-str object (if the iterable had exactly one non-str item), a Python object parsed from the concatenated string using ast.literal_eval (when parsing succeeds), or the raw concatenated string if parsing fails.
    - Invariants provided by native_concat that callers can rely on:
      - Empty iterable => returns None.
      - Single non-str item => returns that item unchanged.
      - Iterable with one or more strings (or multiple items) => concatenates string representations and attempts to parse into a Python literal; on parse errors returns the raw concatenated string.
      - If the input is a generator, native_concat safely inspects up to two items and re-chains them so that no items are lost.

Instance state:
- NativeEnvironment does not declare additional instance attributes and inherits all runtime state and initialization behavior from Environment. Any instance attributes created by Environment.__init__ are unaffected by this subclass.

Class invariants:
- code_generator_class must remain a CodeGenerator-like class throughout the lifetime of the process (changing it at runtime is allowed but callers should ensure the replacement satisfies CodeGenerator semantics).
- concat must remain a callable with the documented contract (see native_concat). Users may replace it with a different callable but must preserve the input/output contract if other code assumes native-like parsing.

## Lifecycle:
Creation:
- Instantiation uses Environment.__init__ (NativeEnvironment provides no custom __init__). Callers must supply the same parameters Environment.__init__ expects (this class does not change that signature).
- No additional construction-time validation is performed by NativeEnvironment itself.

Usage:
- Typical sequence:
  1. Create an instance via the standard Environment constructor (i.e., call the Environment constructor via NativeEnvironment(...)).
  2. Use the environment to load or compile templates (e.g., from strings or loaders). During compilation, the environment or compilation pipeline will instantiate or reference code_generator_class (NativeCodeGenerator) to produce native-friendly code fragments.
  3. When template code or rendering needs to join multiple fragments and possibly coerce them to native Python values, the pipeline will call env.concat(iterable_of_fragments) (which is native_concat by default).
- There is no special method ordering or required calls unique to NativeEnvironment beyond the normal Environment usage patterns.

Destruction / cleanup:
- No cleanup, context-manager, or close() behavior is defined by NativeEnvironment itself. Cleanup responsibilities (if any) are those of the Environment base class and any resources the caller attaches to the instance (loaders, file handles, etc.).

## Method Map:
flowchart LR
    EnvClass[NativeEnvironment (subclass of Environment)]
    EnvClass -->|provides| CG[code_generator_class = NativeCodeGenerator]
    EnvClass -->|provides| CON[c o n c a t = staticmethod(native_concat)]
    CG --> NC[See NativeCodeGenerator (helpers for native emission)]
    CON --> NCAT[See native_concat (join/parse semantics)]

(Interpretation: NativeEnvironment configures Environment to use NativeCodeGenerator when generating code and native_concat when concatenating fragments. See the referenced component docs for the implementation details those attributes supply.)

## Raises:
- __init__:
  - NativeEnvironment defines no constructor of its own; any exceptions raised during creation are those raised by Environment.__init__ or by the call sites that pass invalid arguments to Environment.
  - No new exceptions are introduced by this subclass.

- Runtime usage:
  - Calls to env.concat(...) will raise whatever exceptions native_concat may raise when iterating its input (for example, if iterating the provided iterable raises). native_concat itself suppresses parsing exceptions (ValueError, SyntaxError, MemoryError) and returns the raw concatenated string in those cases.
  - Anything that depends on the behavior of code_generator_class may propagate exceptions from NativeCodeGenerator or the wider compilation pipeline.

## Example (descriptive):
- Creation:
  - Obtain a NativeEnvironment instance by calling the Environment constructor via NativeEnvironment with the same parameters you would use for a normal Environment (loader, autoescape settings, etc.). NativeEnvironment does not change the call signature.

- Typical usage flow (textual, no code shown here):
  1. Construct env = NativeEnvironment(...) using the same args you would pass to Environment.
  2. Use env to create or load a template (the Environment base responsibilities).
  3. When the template is compiled, the compilation pipeline will use env.code_generator_class (NativeCodeGenerator) to guide native-friendly emission of constant children and simple surrounding source for non-constant children.
  4. When multiple template fragments must be combined into a single value, the pipeline calls env.concat(iterable_of_fragments). By default, this is native_concat, which tries to return a native Python value when the joined text represents a Python literal, or the raw concatenated string when parsing fails.

Notes for implementers:
- Recreating NativeEnvironment requires only two assignments on a subclass of Environment:
  1. Set the class attribute code_generator_class to the desired CodeGenerator subclass (here NativeCodeGenerator).
  2. Set the class attribute concat to a callable with the documented contract, stored as a staticmethod if you wish it to be available at the class level (here staticmethod(native_concat)).
- Do not add constructor logic unless you consciously want to change Environment.__init__ behavior; this subclass intentionally leaves initialization to the base class.

## `src.jinja2.nativetypes.NativeTemplate` · *class*

*No documentation generated.*

### `src.jinja2.nativetypes.NativeTemplate.render` · *method*

## Summary:
Synchronously produce a native Python rendering result from the template using the provided context data; returns the exact value produced by the environment's concat policy and does not modify the template object.

## Description:
- Known callers and lifecycle stage:
  - Called by application code that needs a synchronous rendering result from a compiled template (the synchronous counterpart to render_async). Typical call sites are service request handlers, scripts, or any code that previously used Template.render to obtain template output as a Python value.
  - Invoked after the template has been compiled and attached to an Environment instance; the method relies on environment configuration (environment_class.concat and environment.handle_exception).

- Why this method exists separately:
  - It groups three logically-related steps that must be performed together and in a specific order:
    1. Build a plain mapping from the caller arguments.
    2. Turn that mapping into a rendering context using self.new_context.
    3. Invoke the compiled template root function and pass its output through the environment concat policy to produce a native Python value.
  - Centralizing these steps ensures consistent error handling (delegation to environment.handle_exception) and keeps synchronous rendering behavior separate from the asynchronous variant.

## Args:
    *args: typing.Any
        - Forwarded to the built-in dict(...) call used to create the initial mapping passed to new_context.
        - Acceptable shapes mirror dict(...) semantics:
            * No positional args — only kwargs are used.
            * One positional arg — a mapping or iterable of (key, value) pairs acceptable to dict.
        - Errors from invalid usages of dict (for example, passing more than one positional argument) propagate as the same exceptions dict would raise (typically TypeError).
    **kwargs: typing.Any
        - Keyword arguments merged into the mapping passed to dict(...).

Notes:
    - The code performs ctx = self.new_context(dict(*args, **kwargs)). Any exception raised by dict(...) or by self.new_context(...) occurs before entering the try/except and therefore propagates to the caller.

## Returns:
    typing.Any
        - Exactly the value returned by calling self.environment_class.concat(...) on the value produced by self.root_render_func(ctx).
        - Possible concrete outcomes depend on the environment_class.concat implementation (for example NativeEnvironment.concat / native_concat):
            * None for an empty fragment sequence if concat defines that result.
            * A native Python object parsed from the concatenated text (e.g., number, list, dict) when concat attempts and succeeds at literal parsing.
            * A single non-string object passed through unchanged when the rendered fragments consist of exactly one non-string item.
            * A raw concatenated string when parsing fails or concat chooses to return text.
        - If an exception occurs during the root_render_func call or during the concat call, the method returns the value returned by self.environment.handle_exception() (exceptions in new_context are not handled here; see Raises).

## Raises:
    - Exceptions from dict(*args, **kwargs) or from self.new_context(...) are propagated (these happen before the try block).
    - The try block catches all Exception subclasses raised while invoking self.root_render_func(ctx) or while calling environment_class.concat(...). In that case, the method calls and returns self.environment.handle_exception().
    - Exceptions that are not subclasses of Exception (for example KeyboardInterrupt, SystemExit) are not caught by the except Exception clause and therefore propagate.
    - If self.environment.handle_exception() itself raises, that exception propagates to the caller.
    - If environment_class.concat is not callable or root_render_func returns an unexpected type that causes concat to raise, those exceptions are caught and handled via environment.handle_exception().

## State Changes:
- Attributes READ:
    - self.new_context — used to convert the plain mapping into whatever context object the template system expects.
    - self.root_render_func — invoked with the created context; this is the compiled template entrypoint.
    - self.environment_class — accessed to obtain the concat callable (self.environment_class.concat).
    - self.environment — used to call handle_exception() on caught errors.
- Attributes WRITTEN:
    - None. This method does not assign to or mutate attributes on self.

## Constraints:
- Preconditions:
    - The Template instance must be initialized and compiled so that self.root_render_func is callable and self.new_context is available.
    - new_context must accept a dict and return a context acceptable to root_render_func.
    - environment_class.concat must accept the return value of root_render_func(ctx) (typically an iterable or sequence of fragments) and conform to the concat contract expected by the environment (see NativeEnvironment.concat/native_concat for details).
- Postconditions:
    - On normal execution, no template instance attributes are changed and the return value equals environment_class.concat(root_render_func(ctx)).
    - On exceptions arising inside root_render_func or concat, the method returns the result of self.environment.handle_exception() (unless that handler raises).

## Side Effects:
    - Executing self.root_render_func(ctx) runs the compiled template code; any side effects contained in that compiled code (I/O, logging, mutation of external objects) will occur.
    - environment_class.concat(...) may iterate over the fragments returned by root_render_func; if fragments are generators, they may be partially or fully consumed by concat (native_concat inspects up to two items when determining behavior).
    - On caught exceptions, calling self.environment.handle_exception() may perform logging or other side effects depending on the environment implementation.
    - The method itself performs no direct I/O or external service calls; all side effects stem from invoked callbacks or compiled template code.

### `src.jinja2.nativetypes.NativeTemplate.render_async` · *method*

## Summary:
Performs asynchronous rendering of the template with the provided context and returns the environment-specific concatenation/parsed result; verifies the environment is configured for async execution and does not modify the template object state.

## Description:
This is the async counterpart to the synchronous render path. It is invoked by callers that need an awaitable rendering operation (for example, application code handling a request inside an async framework that calls await template.render_async(...)). Typical calling contexts:
- Consumer code that explicitly wants async template rendering (e.g., await template.render_async(...)).
- Higher-level rendering utilities that choose the async path when the Environment is configured for async execution.

Lifecycle stage:
- Called at template render time after a Template object has been constructed and possibly compiled. It is the final step that executes the compiled template code and combines yielded fragments into the final returned value.

Why this logic is a separate method:
- Async rendering requires explicit environment checks and the use of asynchronous iteration semantics (async for) over the template's root render function. Keeping the logic separate avoids mixing async and sync iteration, and isolates the environment readiness check and the async-comprehension-based collection needed to feed the environment's concat routine.

## Args:
    *args (typing.Any): Positional arguments forwarded to dict(...) to produce the template context mapping. Accepted forms follow the semantics of the built-in dict constructor (e.g., a single mapping, an iterable of (key, value) pairs, or no args).
    **kwargs (typing.Any): Keyword arguments that, together with *args, are passed to dict(...) to produce the template context mapping.

Note: The method builds the context with ctx = self.new_context(dict(*args, **kwargs)), so argument validation/error behavior matches that of dict(...) and of self.new_context(...).

## Returns:
    typing.Any: The value returned by self.environment_class.concat(...) when called on the sequence of values produced by the template's async root render function.
    Possible return shapes (depend on the environment.concat implementation; see NativeEnvironment/native_concat for the default semantics):
    - None when the concat callable determines the fragments yield an empty result.
    - A single non-str object if the sequence contains exactly one non-string item and concat preserves it.
    - A Python object parsed from the concatenated textual fragments (for example, via ast.literal_eval) when parsing succeeds.
    - A concatenated string when parsing fails or concat chooses not to coerce to a native object.
    - If an exception occurs during rendering/concatenation, the return value is the result of self.environment.handle_exception().

## Raises:
    RuntimeError: Raised immediately if self.environment.is_async is false. Exact message:
        "The environment was not created with async mode enabled."
    Any exception raised by self.environment.handle_exception() (if that method itself raises) will propagate.
    Other exceptions thrown inside the try block (from new_context, root_render_func, or environment_class.concat) are caught and handled by environment.handle_exception(); they are not raised directly by render_async.

## State Changes:
    Attributes READ:
      - self.environment (reads .is_async and calls self.environment.handle_exception())
      - self.environment_class (used to access .concat on the class)
      - self.new_context (method is called to create ctx)
      - self.root_render_func (method is invoked with ctx and iterated asynchronously)
    Attributes WRITTEN:
      - None. This method does not modify any self.* attributes.

## Constraints:
    Preconditions:
      - self.environment must be present and have a boolean attribute is_async. That attribute must be True before calling this method.
      - The Template instance must provide new_context(mapping) which returns a valid context object for the compiled template code.
      - The Template instance must provide root_render_func(ctx) which must be an asynchronous iterable (async generator or async iterator) yielding fragments accepted by environment_class.concat.
      - environment_class.concat must accept an asynchronous sequence of fragments (the method collects the fragments into a list via an async-comprehension before calling concat).

    Postconditions:
      - The Template object (self) remains unchanged.
      - The returned value satisfies the contract of environment_class.concat for the sequence of fragments produced by root_render_func.
      - Any exceptions raised during rendering are converted into a return value by self.environment.handle_exception(), unless handle_exception itself raises.

## Side Effects:
    - Executes the compiled template code via self.root_render_func(ctx). That execution may invoke user-defined filters, tests, or functions, and therefore may perform arbitrary side effects (I/O, state mutation, async network/database calls) depending on template content.
    - Calls self.environment_class.concat(...) which may attempt to parse/join fragments (default NativeEnvironment.concat/native_concat may call ast.literal_eval). Parsing/concatenation may raise internal exceptions during iteration which are caught and handled as described above.
    - Calls self.environment.handle_exception() when any exception escapes the try block; handle_exception may perform logging, wrap/translate exceptions, or raise.

