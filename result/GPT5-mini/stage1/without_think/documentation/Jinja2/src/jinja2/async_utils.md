# `async_utils.py`

## `src.jinja2.async_utils.async_variant` · *function*

*No documentation generated.*

## `src.jinja2.async_utils.auto_await` · *function*

## Summary:
Resolves a value that may be awaitable: if the argument is an awaitable, await it and return its resolved result; otherwise return the original value. Values whose concrete type is listed in the module-level _common_primitives set are returned immediately without awaiting.

## Description:
This async utility centralizes the common pattern of accepting either synchronous results or awaitable objects and normalizing them to a single resolved value. It is useful wherever code must handle values produced either synchronously or asynchronously and wants to consume them uniformly using await.

Known callers and typical contexts:
- Expression evaluation within async template rendering (the evaluation pipeline may receive either a value or an awaitable).
- Filter or helper wrappers that accept values returned by user code that may be synchronous or asynchronous.
- Async-aware adapter layers that bridge synchronous APIs into async call sites.
Note: concrete call-sites in the repository were not available in the provided context; the above are typical and realistic use cases rather than an exhaustive list.

Why this is a separate function:
- Avoids duplicating inspect.isawaitable checks throughout the codebase.
- Encapsulates the short-circuit behavior for primitive types that must never be awaited (the exact set is module-defined as _common_primitives).
- Provides a single place to control awaiting semantics and error propagation behavior.

## Args:
    value (Union[Awaitable[V], V]):
        - Input to resolve. Can be an awaitable (for example, coroutine object, Future, or any object implementing __await__) that yields a value of type V, or a plain value of type V.
        - The function first checks whether type(value) is a member of _common_primitives. If so, the value is returned immediately.
        - If the type check does not short-circuit, the function uses inspect.isawaitable to determine whether value should be awaited.
        - V is a generic placeholder representing the eventual resolved value type.

## Returns:
    V
    - If type(value) is exactly one of the types in _common_primitives, the original value is returned unchanged.
    - Else, if inspect.isawaitable(value) is True, the function awaits the awaitable and returns the awaited result.
    - Else, returns the original value unchanged.
    - In short: caller receives a resolved value of type V regardless of whether the input was awaitable or not.

## Raises:
    - Any exception raised by the awaited awaitable is propagated to the caller (the function does not catch or wrap exceptions).
    - The function itself does not raise for normal inputs; exceptions typically originate from the awaited object's execution.

## Constraints:
    Preconditions:
        - Must be invoked from within an async context (for example, inside another async function) because this function uses await.
        - The module must define _common_primitives as an iterable of concrete types. The function performs an exact-type check (type(value) in _common_primitives), so subclasses are not short-circuited unless their concrete type is listed.
    Postconditions:
        - The returned value is resolved: it is the original value for non-awaitable/primitive inputs or the awaited result for awaitable inputs.
        - No module-level state is modified by the function itself.

## Side Effects:
    - The function performs no I/O directly.
    - Awaiting the provided awaitable will execute whatever side effects that awaitable produces (network calls, state mutation, logging, etc.). Those side effects are a property of the awaited object, not this helper.
    - No global variables or caches are modified by this function.

## Control Flow:
flowchart TD
    Start["Start: call auto_await(value)"]
    CheckPrimitive{"type(value) in _common_primitives?"}
    ShortCircuit["Return value (primitive)"]
    CheckAwaitable{"inspect.isawaitable(value)?"}
    AwaitAndReturn["Await value; return awaited result"]
    ReturnValue["Return value (non-awaitable)"]

    Start --> CheckPrimitive
    CheckPrimitive -- Yes --> ShortCircuit
    CheckPrimitive -- No --> CheckAwaitable
    CheckAwaitable -- Yes --> AwaitAndReturn
    CheckAwaitable -- No --> ReturnValue

Notes on precedence:
- The primitive-type check runs before the inspect.isawaitable check. Therefore, if an object’s concrete type is listed in _common_primitives, it is returned without awaiting even if inspect.isawaitable would otherwise report True for that object.

## Examples:
Usage pattern (step-by-step, async context):
1) Acquire a value that may be either synchronous or asynchronous (for example, a function that sometimes returns an int and other times returns a coroutine).
2) Call: resolved = await auto_await(possible_awaitable_or_value)
3) Use resolved as a normal, fully-resolved value without further awaiting.

Error handling (async context):
- If the awaitable raises, that exception propagates to the caller; handle it with normal async exception handling:
    - Attempt to resolve the value using await auto_await(...).
    - If an exception occurs, catch it and handle or re-raise as appropriate.

Edge cases and implementation details to be aware of:
- Exact-type short-circuiting: because the function checks type(value) against the module-level set, instances whose class is a subclass of a listed primitive are not short-circuited unless their concrete class is also listed.
- inspect.isawaitable returns True for native coroutine objects and for objects implementing __await__. Objects that merely look like awaitables but do not implement the awaited protocol will not be awaited.
- The full, authoritative list of short-circuited primitive types is held in the module-level _common_primitives variable; check that symbol in the module to know which types will be immediately returned without awaiting.

## `src.jinja2.async_utils.auto_aiter` · *function*

## Summary:
Returns an asynchronous iterator (an async generator object) that yields every element from the given input, accepting either a synchronous iterable or an asynchronous iterable and normalizing consumption so callers can always use async iteration.

## Description:
This async generator accepts a single value that may implement either the asynchronous-iteration protocol (has __aiter__) or the synchronous-iteration protocol (is iterable). It inspects the input at runtime; if the input exposes __aiter__, it consumes it with async for, otherwise with a regular for loop. The function itself is an async generator function: calling it immediately returns an async generator object which must be consumed with async iteration.

Known callers / typical contexts:
- Template engines or filter implementations that run inside async event loops but must accept user-provided iterables that may be synchronous or asynchronous.
- Any async logic that wants to transparently accept both sync and async producers and iterate them using the same code path (e.g., unified consumer helpers, wrappers around input streams).
(Note: no concrete callers were present in the provided file snapshot; the above are common usage patterns.)

Why this is a separate function:
- It centralizes the runtime branching (sync vs async iteration) and exposes a consistent async-iterator interface. This reduces duplication and prevents scattering the hasattr(__aiter__) check throughout caller code, making client code simpler and protocol-agnostic.

## Args:
    iterable (Union[AsyncIterable[V], Iterable[V]]):
        The value to iterate over. Must either:
        - Implement the asynchronous iteration protocol (provide __aiter__), or
        - Be a synchronous iterable (implement __iter__).
        There is no default. If the object is neither form of iterable, iteration will fail when attempted.

    Type variables:
        V: the element type yielded by the iterable.

    Interdependencies:
        Behavior is determined solely from the runtime presence of the "__aiter__" attribute on the provided object. No other parameters exist.

## Returns:
    AsyncIterator[V]:
        An async generator object (implements AsyncIterator[V] and AsyncIterable[V]) that yields each element from the original iterable in order.

    Important runtime notes:
        - Calling auto_aiter(...) does not begin iteration; it returns an async generator that starts producing items when consumed (e.g., by "async for" or by calling its __anext__ method).
        - If the underlying iterable is synchronous, iteration is executed synchronously inside the async generator (no automatic yielding to the event loop between items).
        - If the underlying iterable is asynchronous, the async path is taken and each awaited element comes from the async iterable.

## Raises:
    Exceptions raised are those produced by Python's iteration machinery or by the underlying iterable:
    - TypeError (typical): If the synchronous path is taken but the object is not actually iterable, the "for" loop will raise TypeError ("'X' object is not iterable").
    - Any exception raised during async iteration: If the object reports __aiter__ but does not implement a valid async iterable protocol, or if its async iteration fails, the async for machinery will raise the appropriate exception (TypeError, AttributeError, RuntimeError, or user exceptions).
    - Any exception raised by code executed during iteration (in the iterable or in consumer code) propagates unchanged through this helper.

    The function does not itself wrap or convert exceptions — it forwards whatever errors occur while obtaining or yielding items.

## Constraints:
    Preconditions:
        - The caller is expected to consume the returned value using async iteration (e.g., "async for item in auto_aiter(...)" or by awaiting __anext__ on the returned async generator).
        - If the input is a long-running synchronous iterable, the caller must be aware that iterating it here will run synchronously and may block the event loop; this helper does not perform any scheduling to avoid blocking.

    Postconditions:
        - All yielded items have been produced in the same order as the underlying iterable.
        - No additional side effects or state are introduced by this helper beyond those caused by iterating the given iterable.

## Side Effects:
    - This function performs no I/O, network calls, or global-state mutation itself.
    - Any side effects are those of the underlying iterable during iteration (e.g., item production may perform I/O or mutate state).
    - For synchronous iterables, iteration happens on the current event loop thread and can block it; the helper does not offload work to threads.

## Control Flow:
flowchart TD
    Start([call auto_aiter(iterable) -> returns async generator])
    Consume{When consumer starts async iteration}
    CheckAiter{hasattr(iterable, "__aiter__")?}
    AsyncLoop[/async for item in iterable\nyield item/]
    SyncLoop[/for item in iterable\nyield item/]
    Exceptions((propagate exceptions from underlying iterable))
    End([iteration complete])

    Start --> Consume
    Consume --> CheckAiter
    CheckAiter -->|yes| AsyncLoop
    CheckAiter -->|no| SyncLoop
    AsyncLoop --> End
    SyncLoop --> End
    AsyncLoop --> Exceptions
    SyncLoop --> Exceptions

## Examples:
Usage scenario: consume a synchronous list from async code
  - Given a normal list like [1, 2, 3], call auto_aiter(list) inside an async function.
  - Consume with async for to receive elements 1, then 2, then 3 in order.
  - Be aware: iterating the list in this helper runs synchronously and may block the event loop if element production is costly.

Example pattern (async consumer with error handling):
  - Acquire async generator: agen = auto_aiter(some_iterable)
  - Use "async for" to iterate:
      async for item in agen:
          try:
              process(item)
          except SpecificError as exc:
              handle(exc)
  - Wrap the async-for in try/except around the loop to catch iteration-time exceptions:
      try:
          async for item in auto_aiter(maybe_iterable):
              use(item)
      except TypeError:
          # handle case where a non-iterable was passed
          handle_bad_input()
      except Exception as e:
          # handle other exceptions raised by the underlying iterable
          handle_other(e)

Example scenario: consume an async generator
  - Given an async generator object (one that defines __aiter__), pass it to auto_aiter; the async path is used and elements are yielded as produced by the original async generator.

Notes and best practices:
  - If you must iterate a long-running synchronous iterable without blocking the event loop, run that iteration in a thread (e.g., loop.run_in_executor) or convert the producer into an async-aware source before passing it to this helper.
  - The runtime decision is based only on hasattr(obj, "__aiter__"); objects that expose that attribute but do not fully conform to the async iteration protocol can still cause errors when consumed.

## `src.jinja2.async_utils.auto_to_list` · *function*

## Summary:
Asynchronously consumes the provided iterable (sync or async) and collects all items into a list, returning that list when iteration completes.

## Description:
Known callers within the codebase:
- No direct call sites were present in the provided snapshot. Typical usage patterns include template filters, template helper utilities, or async-aware adapters that need to obtain a concrete list from a user-supplied iterable while running inside an async event loop.

Context and trigger:
- Called when asynchronous code needs to fully realize an iterable's contents into memory (for example, to perform indexing, repeated passes, length checks, or to supply a concrete sequence to APIs that require a sequence).
- The function is an async coroutine and must be awaited from within an async context or event loop.

Why this is factored out:
- Centralizes the logic of normalizing synchronous and asynchronous iterables into a single operation that produces a concrete Python list. Callers avoid repeating the pattern of converting any iterable into an async-aware form and then collecting items; that responsibility is encapsulated here for clarity and reuse.

## Args:
    value (Union[AsyncIterable[V], Iterable[V]]):
        The source iterable whose items will be collected into a list.
        - May be an asynchronous iterable (implements __aiter__) or a synchronous iterable (implements __iter__).
        - Type variable V denotes the element type.
        - There is no default; the caller must supply a value.
        - Interdependency: behavior (sync vs async consumption) is chosen at runtime by auto_aiter based on whether value has "__aiter__".

## Returns:
    List[V]:
        A concrete Python list containing every item produced by the provided iterable, in the same order they are yielded by the source.
        - If iteration completes normally, the returned list contains all items.
        - For asynchronous iterables, items are awaited and collected.
        - For synchronous iterables, items are read synchronously inside the async coroutine and appended to the result.
        - Edge cases:
            * If the iterable yields no items, an empty list is returned.
            * If the iterable is infinite or extremely large, the coroutine will not complete or may exhaust memory.

## Raises:
    Propagated exceptions from iteration:
        - TypeError: Typical when a non-iterable is passed and the synchronous "for" machinery is used (e.g., "'X' object is not iterable"), or when an object claims to be asynchronous but fails protocol checks while being consumed.
        - Any exception raised by the underlying iterable or during async iteration (AttributeError, RuntimeError, user-defined exceptions, etc.) is propagated unchanged.
        - The function itself does not catch or wrap exceptions thrown during iteration.

## Constraints:
    Preconditions:
        - Must be called (awaited) from within an async context (coroutine or running event loop).
        - Caller should ensure that collecting all items into memory is acceptable; this will allocate memory proportional to the number of items.
        - If passing a long-running synchronous iterable, be aware that iterating it here will execute synchronously on the event loop thread and may block other tasks.

    Postconditions:
        - On successful completion, the returned list contains every item yielded by the source in order.
        - The source iterable will have been fully consumed (unless iteration raised an exception).
        - No additional mutation or global state is introduced by this helper beyond what the underlying iterable does.

## Side Effects:
    - The function itself performs no external I/O or global state mutation.
    - Any side effects are those produced by the underlying iterable when its items are produced (including I/O, side-effecting computations, or state changes).
    - Synchronous iteration of a blocking iterable can block the event loop while items are collected.

## Control Flow:
flowchart TD
    Start([call auto_to_list(value) -> coroutine])
    Await{caller awaits the coroutine?}
    CreateAiter[/call auto_aiter(value) -> async iterator\]
    Collect[/async for item in async_iterator\nappend item to list\]
    Completed([return list])
    Exceptions((propagate exceptions from underlying iteration))

    Start --> Await
    Await --> CreateAiter
    CreateAiter --> Collect
    Collect --> Completed
    Collect --> Exceptions

## Examples:
Typical usage (async consumer collecting a synchronous list):
  - Await the coroutine from within an async function to obtain a concrete list of items produced by the source iterable.
  - Example pattern: obtain the list and then perform synchronous operations that require indexing or multiple passes.

Error-handling pattern:
  - Wrap the await in try/except to handle cases where the provided value is not iterable or where iteration raises an exception.
  - Be cautious with very large or infinite iterables; prefer streaming approaches or explicit limits if consuming everything is unsafe.

Best practices:
  - Do not use this helper if you intend to process items lazily; use async iteration directly instead.
  - If the source is a long-running synchronous generator, consider offloading iteration to a thread or converting it to an async producer before calling this helper to avoid blocking the event loop.

