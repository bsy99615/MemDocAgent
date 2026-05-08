# `tracer.py`

## `datasette.tracer.get_task_id` · *function*

## Summary:
Resolve and return a tracing identifier for the current execution context: return a non-None module-level ContextVar value when present, otherwise return the Python id() of the current asyncio.Task, or None if no event loop is available.

## Description:
This function centralizes the logic for obtaining a stable identifier used by tracing/logging code to correlate execution across asynchronous tasks and synchronous contexts.

Behavior:
- First checks the module-level ContextVar named trace_task_id. If trace_task_id.get(None) returns a non-None value, that value is returned unchanged.
- If the ContextVar is unset or contains None, the function attempts to obtain the current asyncio event loop and the currently executing asyncio.Task for that loop; it returns the integer id() of that Task object.
- If asyncio.get_event_loop() raises RuntimeError (no event loop available), the function returns None.

Known callers:
- No direct callers were discovered during the immediate retrieval for this task. Typical callers are tracing, logging, or instrumentation utilities that need a simple task identifier to correlate log lines, metrics, or trace spans.

Why this logic is extracted:
- Avoids duplicating the ContextVar check and asyncio current-task lookup across the codebase.
- Provides a single, well-documented place to change how task identity is resolved in the future.

## Args:
- None. The function takes no parameters.

## Returns:
- Union[int, Any, None]
    - If trace_task_id (module-level ContextVar) contains a non-None value: returns that value exactly (type depends on what the rest of the program stored there — e.g., int, str, or a token object).
    - Else, if an asyncio event loop is available: returns an int equal to id(current_task). This is the Python object identity of the current asyncio.Task and is unique for the lifetime of that Task object within the process.
    - Else (no event loop available): returns None.

Important details and edge cases:
- Only non-None ContextVar values are honored. If trace_task_id is set to None (explicitly or by default), the function will ignore it and fall back to the asyncio Task-based identifier.
- If asyncio.current_task(loop=loop) returns None (for example, code running in the event loop thread but not inside a Task), the function returns id(None) — an int that is constant for the process and therefore does not uniquely identify a Task.
- The int returned from id() should be treated as an in-memory identifier only (it is not stable across process restarts and depends on CPython object identity semantics).

## Raises:
- None. The function catches RuntimeError from asyncio.get_event_loop() and returns None instead of propagating the exception.

## Constraints:
Preconditions:
- None. Safe to call from synchronous or asynchronous contexts.
Postconditions:
- The function will return exactly one of:
    - the non-None trace_task_id ContextVar value,
    - an int (id of the current asyncio.Task or id(None)), or
    - None when there is no running event loop.

## Side Effects:
- None. The function only reads from the module-level ContextVar and asyncio runtime; it does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start((start))
    A[read trace_task_id.get(None)]
    A --> |value is not None| ReturnContext[return that value]
    A --> |value is None| TryLoop[try asyncio.get_event_loop()]
    TryLoop --> |RuntimeError| ReturnNone[return None]
    TryLoop --> |loop obtained| CurrTask[call asyncio.current_task(loop=loop)]
    CurrTask --> |task is not None| ReturnIdTask[return id(task)]
    CurrTask --> |task is None| ReturnIdNone[return id(None)]
    ReturnContext --> End((end))
    ReturnNone --> End
    ReturnIdTask --> End
    ReturnIdNone --> End

## Examples:
1) Typical use inside an async Task (ContextVar not set):
- When running inside an asyncio.Task, the function returns an int identifying that Task for the lifetime of the Task:
    result = get_task_id()
    # result -> int (id of current asyncio.Task)

2) When code sets an explicit trace id in the ContextVar:
- Tracing code may set trace_task_id to a string/token; this explicit value is returned instead of the Task id:
    # trace_task_id.set("trace-42")
    result = get_task_id()
    # result -> "trace-42"

3) Outside any event loop:
- Calling from synchronous code with no asyncio loop yields None:
    result = get_task_id()
    # result -> None

4) Running in an event loop thread but not within a Task:
- current_task may be None; the function returns id(None) (an int constant for the process), which should not be interpreted as a unique Task id:
    result = get_task_id()
    # result -> id(None)  (an int, not a unique Task identifier)

## `datasette.tracer.trace_child_tasks` · *function*

## Summary:
Temporarily sets the module-level tracing ContextVar so child asynchronous tasks created while the context is active inherit the current execution's trace identifier, and restores the previous ContextVar state when the context exits normally.

## Description:
- Known callers / typical usage:
    - Used around code that spawns child asyncio tasks (e.g., calls to asyncio.create_task or similar) so those child tasks inherit a trace identifier based on the current execution context. Typical call site is immediately around task creation in a request handler, background worker, or any code that wants child tasks to be correlated with the parent task for logging/tracing.
    - The module imports contextmanager; this generator function is intended to be used via the contextmanager protocol (i.e., used with `with trace_child_tasks():`) so that the set/reset behavior applies around the with-block.

- Responsibility boundary:
    - This component's sole responsibility is to temporarily bind the module-level ContextVar (trace_task_id) to a value returned by get_task_id() for the duration of a context, then restore the previous token afterwards.
    - It encapsulates the set/reset pattern so callers do not need to manually save and restore ContextVar tokens when creating child tasks.

## Args:
- None.

## Returns:
- When called, this function returns a generator that yields exactly once (no yield value). In typical usage it is wrapped with contextlib.contextmanager (as the module imports) and used as a context manager:
    - Entering the context: trace_task_id is set to get_task_id(), and the with-block executes.
    - Exiting the context normally: the previous ContextVar token is restored with trace_task_id.reset(token).
    - The with-block does not receive any value from the context manager (the yielded value is None).

## Raises:
- The function body itself does not raise explicitly.
- Important behavior regarding exceptions:
    - If an exception is raised inside the with-block, the generator as written does not catch or handle that exception; when the exception is propagated into the generator (via the contextmanager machinery), the reset call placed after the yield will not be executed unless the generator explicitly handles the thrown exception. Therefore, in the current implementation, trace_task_id.reset(token) is not guaranteed to run if the with-block raises — which can leave the ContextVar set to the child token beyond the intended scope.

## Constraints:
- Preconditions:
    - The module-level name trace_task_id must exist and be a ContextVar supporting set() and reset() semantics.
    - get_task_id() must be callable and should return the desired trace identifier to apply to child tasks (it may return None; that value will be used as-is).
    - Caller should use this generator as a context manager (i.e., decorated/wrapped by contextlib.contextmanager or otherwise used to ensure proper enter/exit behavior).

- Postconditions:
    - If the with-block exits normally (no exception escapes), trace_task_id is restored to the token that was active before entering the context.
    - If the with-block raises an exception, reset is not guaranteed to run in this implementation; callers who need guaranteed cleanup in the face of exceptions should wrap usage in an outer try/finally, or the function implementation should be revised to reset inside a finally block.

## Side Effects:
- Mutates module-level ContextVar:
    - Calls trace_task_id.set(get_task_id()) on entry, which changes the ContextVar for the current context (and will be inherited by any child contexts/tasks created from here).
    - Calls trace_task_id.reset(token) on normal exit to restore the previous ContextVar state.
- No I/O, network, stdout, database, or external service calls are performed by this function.

## Control Flow:
flowchart TD
    Start((start))
    A[Call trace_child_tasks()] --> B[token = trace_task_id.set(get_task_id())]
    B --> C[Yield control to caller (enter with-block)]
    C --> |with-block exits normally| D[trace_task_id.reset(token)]
    C --> |with-block raises exception| E[Exception injected into generator]
    E --> |generator catches exception (not implemented)| D
    E --> |generator does NOT catch exception (current implementation)| F[reset not executed -> ContextVar remains set]
    D --> End((end))
    F --> End

## Examples:
1) Normal usage (happy path)
    from contextlib import contextmanager
    # In this module the generator is intended to be used as a contextmanager:
    @contextmanager
    def trace_child_tasks_cm():
        token = trace_task_id.set(get_task_id())
        try:
            yield
        finally:
            trace_task_id.reset(token)

    # Typical usage around task creation:
    with trace_child_tasks_cm():
        asyncio.create_task(child_coroutine())  # child inherits current trace ID

    # After the with-block exits normally, trace_task_id is restored.

2) Important caution — exception during the with-block
    # Using the current implementation (no try/finally inside generator):
    try:
        with trace_child_tasks():    # if used without adjusting implementation
            asyncio.create_task(child_coroutine())
            raise RuntimeError("boom")
    except RuntimeError:
        # Because the generator does not handle the thrown exception, the ContextVar
        # reset may not have been executed. The module-level trace_task_id may still
        # be set to the token introduced in the failed with-block.
        pass

    # Recommendation: either ensure the context manager implementation resets in a finally,
    # or avoid relying on automatic reset if callers may raise exceptions inside the block.

## `datasette.tracer.trace` · *function*

## Summary:
Context manager that measures the elapsed time of a code block and records a trace entry (type, start, end, duration, traceback, plus user-supplied metadata) into the current task's tracer collector when tracing is enabled for the current execution context.

## Description:
This generator-based context manager yields the user-supplied kwargs dict into the with-block, measures the block's start and end times (using time.perf_counter), builds a trace record that includes a traceback snippet and duration in milliseconds, merges in the kwargs, and appends the resulting record to a per-task tracer collector.

Known callers / typical usage:
- Instrumentation and profiling code that wants to record timing and contextual metadata around operations (for example, SQL query execution, HTTP handler sections, long-running computations).
- Typical trigger: used as a with-block around the unit of work to measure. Example: with trace("sql", sql=sql_string): ...
- This function is intended to be used as a context manager (the module imports contextmanager; when reimplementing, decorate this generator with @contextmanager).

Why this logic is extracted:
- Centralizes measurement, traceback capture, and the logic that decides whether tracing is active for the current execution context.
- Keeps callers simple: they only supply a short type string and metadata; the context manager handles start/end timing, traceback capture, and appending to the appropriate per-task collector.

## Args:
    type (str): A short category or kind for the trace entry (e.g., "sql", "http", "render"). Stored as the "type" field in the trace record.
    **kwargs: Arbitrary user metadata to include in the trace. This function yields the kwargs dict into the with-block, so modifications made inside the with-block are reflected in the final recorded trace (the dict is merged into the trace record after the block completes).

Notes on kwargs and reserved keys:
- The function asserts that none of kwargs' keys intersect TRACE_RESERVED_KEYS. TRACE_RESERVED_KEYS is a module-level collection of keys reserved by the tracer (the tracer always produces keys such as "type", "start", "end", "duration_ms", "traceback"). If any reserved key is present in kwargs the function raises an AssertionError (see Raises).
- No parameter defaults beyond the provided kwargs — callers supply whatever metadata they need, but must avoid reserved keys.

## Returns:
    When used as a context manager, the value yielded into the with-block is the kwargs dict passed by the caller. This allows the caller to add or mutate entries that will be recorded in the final trace.
    The context manager itself does not return a value to the caller after exiting; instead it records a trace entry (when tracing is enabled) and returns None from the context manager exit.

Possible yield outcomes:
- Yields the kwargs dict (always; even when tracing is disabled). If tracing is disabled for the current context (no task id or no tracer collector), the context manager is effectively a no-op apart from yielding the kwargs.
- After the block, if tracing is enabled, a trace entry dict is appended to the per-task tracer collector. If tracing is disabled, nothing is appended.

## Raises:
    AssertionError: Raised immediately if kwargs contains any key present in TRACE_RESERVED_KEYS. The assertion message is:
        ".trace() keyword parameters cannot include {TRACE_RESERVED_KEYS}"
    No other exceptions are raised by this function body itself; errors from user code executed inside the with-block will propagate normally (the context manager does not catch exceptions from the block).

## Constraints:
Preconditions:
- TRACE_RESERVED_KEYS must be a module-level iterable (set or similar) of strings representing keys reserved by the tracer. Callers must not pass kwargs with any of these keys.
- tracers must be a module-level mapping keyed by task id (the value returned by get_task_id()) to a per-task collector object that supports an append(trace_info) method (commonly a list). The implementation appends the trace_info dict to tracers[task_id] when tracing is active.
- The function relies on get_task_id() to resolve the current tracing task identifier. get_task_id() may return None (meaning tracing is disabled for the current context), in which case trace becomes a no-op.

Postconditions:
- If tracing was enabled (get_task_id() returned a task id and tracers.get(task_id) returned a collector), then after the with-block completes a dict with at least the following keys will have been appended to the collector:
    - "type": the provided type argument
    - "start": start timestamp (float, seconds from time.perf_counter())
    - "end": end timestamp (float, seconds from time.perf_counter())
    - "duration_ms": elapsed duration in milliseconds (float)
    - "traceback": a small traceback list (produced with traceback.format_list)
  plus all user-supplied/modified kwargs merged into the record.

## Side Effects:
- Mutates the per-task tracer collector by calling tracer.append(trace_info) when tracing is enabled for the current context. This is a global side effect (module-level tracers map).
- Reads module-level values TRACE_RESERVED_KEYS and tracers and calls get_task_id().
- Calls time.perf_counter() and traceback.format_list(...) for timing and traceback capture.
- No file, network I/O, or external service calls are performed by trace itself; it only mutates in-memory tracer collectors.

## Control Flow:
flowchart TD
    Start((start))
    A[assert kwargs keys do not intersect TRACE_RESERVED_KEYS]
    A --> B[get_task_id() -> task_id]
    B --> |task_id is None| C1[yield kwargs to with-block (no-op)]
    C1 --> C1end[exit context, no trace appended]
    B --> |task_id not None| D[tracer = tracers.get(task_id)]
    D --> |tracer is None| C2[yield kwargs to with-block (no-op)]
    C2 --> C2end[exit context, no trace appended]
    D --> |tracer found| E[start = time.perf_counter()]
    E --> F[yield kwargs into with-block]
    F --> G[end = time.perf_counter()]
    G --> H[build trace_info with type,start,end,duration_ms,traceback]
    H --> I[trace_info.update(kwargs)]
    I --> J[tracer.append(trace_info)]
    J --> End((end))

## Examples:
1) Basic usage — record SQL timing and include number of rows after the operation:
    with trace("sql", sql="SELECT id FROM user WHERE active=1") as meta:
        # perform the SQL operation
        rows = execute_sql(...)
        # record extra metadata that will be merged into the saved trace
        meta["row_count"] = len(rows)
    # After the block, a trace dict including "type":"sql", timing, traceback, sql, row_count will be appended to the current task's tracer collector (if tracing enabled).

2) No-op when tracing is disabled:
    # If get_task_id() returns None or tracers has no entry for the current task id,
    # the with-block executes normally but no trace entry is appended.
    with trace("cache", key="user:42") as meta:
        value = cache_get("user:42")
        meta["hit"] = value is not None
    # If tracing is disabled, nothing is appended; meta was still yielded to the with-block.

3) Assertion on reserved keys:
    # If TRACE_RESERVED_KEYS contains "duration_ms", the following raises AssertionError immediately:
    with trace("op", duration_ms=123):
        pass

Implementation notes for reimplementers:
- Implement this function as a generator and decorate it with contextlib.contextmanager to produce a context manager.
- Ensure TRACE_RESERVED_KEYS and tracers are module-level values:
    - TRACE_RESERVED_KEYS: collection of keys reserved by the tracer (must be checked against kwargs).
    - tracers: mapping from task_id to a collector with append() (commonly a dict[int, list[dict]]).
- Use time.perf_counter() for high-resolution timing and traceback.format_list(traceback.extract_stack(limit=6)[:-3]) to capture a short stack trace pointing at the caller site.
- The function yields the same kwargs dict to the caller so that mutations inside the with-block are captured into the final trace record.

## `datasette.tracer.capture_traces` · *function*

## Summary:
Register an opaque tracer object in a module-level per-task mapping for the duration of a yielded region; if no task id can be resolved, do nothing.

## Description:
This generator registers the provided tracer in a module-level mapping keyed by the current task identifier (as returned by get_task_id()) for the time between yielding and the generator resuming/completing. Typical usage wraps this generator with contextlib.contextmanager (or otherwise drives the generator) so the tracer is installed for the lifetime of a with-block.

Known callers:
- No direct callers were discovered in the immediate retrieval. Typical callers are tracing/instrumentation code that want to associate a tracer object with the current execution context (asyncio Task or an explicit ContextVar-based id) for the duration of an operation.

Why this logic is extracted:
- Encapsulates the common pattern of registering/unregistering per-task tracer objects so callers don't need to manipulate the shared mapping directly.
- Keeps the lifecycle management (install-before, remove-after) localized and symmetric, reducing risk of leaks or inconsistent state.

## Args:
    tracer (Any): An opaque tracer object provided by the caller. The function does not inspect or call methods on this object; it merely stores it in the module-level mapping for the task id. Allowed values: any Python object. Interdependencies: the tracer value is associated to the current task id returned by get_task_id(); if get_task_id() returns None, the tracer is not stored.

## Returns:
    generator:
        - This function is a generator that yields exactly once in each code path.
        - Intended semantics when used as a context manager:
            * If get_task_id() returns None: the generator yields once and immediately returns; no tracer is stored.
            * If get_task_id() returns a non-None task_id: the generator stores tracers[task_id] = tracer, yields once (pause point), and upon resumption deletes tracers[task_id] before returning.
        - When wrapped via contextlib.contextmanager, the with-block body executes at the yield point; entering the context registers the tracer (when a task id exists) and exiting the context removes it.

## Raises:
    NameError:
        - If there is no module-level name tracers defined (or it is not accessible in the module namespace), the assignment tracers[task_id] = tracer will raise NameError. This is a likely symptom of a missing module-level mapping and indicates a precondition violation.
    Any exception raised by get_task_id():
        - get_task_id() is called at the start; though the documented implementation of get_task_id does not raise, if an alternate implementation raises, that exception will propagate here.

## Constraints:
    Preconditions:
        - The module-level mutable mapping tracers is expected to exist and be subscriptable (support tracers[key] = value and del tracers[key]).
        - get_task_id() must be importable/available in the module (it is called at the start).
        - Caller must drive the generator (e.g., by wrapping with contextlib.contextmanager or manually advancing) for registration and cleanup to occur.
    Postconditions:
        - If get_task_id() returned a non-None value task_id:
            * During the yielded period, tracers[task_id] == tracer.
            * After the generator resumes and completes, tracers will no longer have an entry for task_id (the function deletes it).
        - If get_task_id() returned None:
            * The tracers mapping is not modified by this function.

## Side Effects:
    - Mutates module-level state: may set tracers[task_id] = tracer and later delete that key.
    - No I/O is performed (no files, network, or stdout writes).
    - No direct calls to tracer methods or other external services are made; the function merely stores the provided object.
    - If tracers mapping operations raise (e.g., if tracers is an object whose __setitem__ or __delitem__ raises), those exceptions propagate to the caller.

## Control Flow:
flowchart TD
    Start((start))
    A[get_task_id() -> task_id]
    A --> |task_id is None| B[yield once and return] --> End((end))
    A --> |task_id is not None| C[set tracers[task_id] = tracer]
    C --> D[yield once (caller code runs here)]
    D --> E[del tracers[task_id]]
    E --> End

## Examples:
1) Typical usage as a context manager (recommended):
    from contextlib import contextmanager
    cm = contextmanager(capture_traces(my_tracer))
    with cm:
        # inside this block, if a task id exists, tracers[task_id] == my_tracer
        do_work()
    # on exiting the with-block, the mapping entry for this task id (if any) is removed

2) Manual generator driving (explicit enter/exit):
    gen = capture_traces(my_tracer)
    try:
        next(gen)   # enters: may register tracer
        do_work()
    finally:
        try:
            next(gen)   # resume to trigger deletion/cleanup
        except StopIteration:
            pass

3) Behavior when no task id is available:
    # get_task_id() returns None
    # Using the contextmanager wrapper will still work; no entry will be written to tracers
    cm = contextmanager(capture_traces(my_tracer))
    with cm:
        do_work()  # tracer not installed because no task id was resolvable

Notes:
- Because the function relies on a module-level mapping named tracers, ensure that mapping is defined (for example as a plain dict) in the same module before this function is used:
    tracers = {}
- The function itself does not validate the tracer object shape; callers are responsible for using a tracer value compatible with other parts of the tracing system that read tracers[task_id].

## `datasette.tracer.AsgiTracer` · *class*

## Summary:
AsgiTracer is an ASGI middleware/app wrapper that, when a request's raw query_string contains the literal token _trace=1, collects in-request trace entries and attempts to inject a summarized trace object into the final HTTP response body (HTML or JSON), while otherwise forwarding all ASGI events unchanged.

## Description:
AsgiTracer should be instantiated with a downstream ASGI application and used as the ASGI-callable the server invokes for each request (for example, app = AsgiTracer(downstream_app)). It implements middleware responsibilities:

- Detect tracing requests by performing a byte-level check for b"_trace=1" among b"&"-separated query_string parts; it does not parse or decode percent-encoding.
- For traced requests, create a per-request traces list and register it via capture_traces(traces) for the duration of the downstream call — but only if capture_traces resolves a task id (see State and Lifecycle). Instrumentation code can append trace entries to that list while the request runs.
- Wrap the provided send callable to accumulate response body bytes (up to max_body_bytes). If final body is captured and is HTML (contains b"</body>") or JSON (content-type indicates JSON and body starts with b"{"), inject trace metadata:
  - HTML: insert an escaped JSON <pre> block before each </body>.
  - JSON: attach a top-level "_trace" key to the parsed object if not present.
- If the body exceeds max_body_bytes while accumulating, forward the collected bytes immediately with "more_body": True and stop attempting injection.

This class focuses on non-invasive, per-request trace collection and opportunistic injection into small HTML/JSON responses; it avoids modifying instance attributes after construction.

## State:
Instance attributes
- app (Callable): The downstream ASGI application stored in __init__. Required; invariant: callable accepting (scope, receive, send) and returning an awaitable.
- max_body_bytes (int, class attribute): Byte limit for response body accumulation. Default: 1024 * 256 (256 KB). Must be positive; reducing it makes injection less likely.

Per-request local state (constructed inside __call__, not persisted on the instance)
- traces (list): A list passed into capture_traces(traces) so instrumentation can append trace entries. AsgiTracer treats entries as opaque except it expects entries (when present) to contain a numeric duration_ms key for sum computation; missing or non-numeric duration_ms will raise during the sum (see Raises).
- accumulated_body (bytes): Concatenated response body bytes collected from "http.response.body" messages. Starts as b"".
- size_limit_exceeded (bool): False initially; set to True when accumulated_body length > max_body_bytes. When True, AsgiTracer stops accumulating and injection.
- response_headers (list[tuple[bytes, bytes]]): Set from the "headers" field of the first "http.response.start" message seen; expected as sequence of (name_bytes, value_bytes). If absent, treated as empty list.

Interaction with capture_traces:
- capture_traces(traces) may register the provided traces object in a module-level mapping keyed by the current task id. This registration occurs only when capture_traces is able to resolve a non-None task id (for example via get_task_id()). If get_task_id() returns None, capture_traces yields without modifying the module-level mapping. If capture_traces did register the mapping entry, it will remove that entry when the context exits (cleanup is conditional on whether it was registered).

## Lifecycle:
Creation:
- Instantiate: tracer = AsgiTracer(app) where app is the downstream ASGI app. __init__ only stores the provided app; it does not validate it.

Per-request usage (sequence):
1. ASGI server calls await tracer(scope, receive, send).
2. __call__ checks scope.get("query_string", b"").split(b"&") for b"_trace=1".
   - If not present: immediately await self.app(scope, receive, send) and return; no tracing or body accumulation is performed.
   - If present: start tracing flow.
3. For tracing requests:
   - Record trace_start = time.perf_counter() and create traces = [].
   - Initialize accumulated_body = b"", size_limit_exceeded = False, response_headers = [].
   - Define async wrapped_send(message) which:
     a) On message["type"] == "http.response.start": set response_headers = message["headers"]; forward message via original send.
     b) If message["type"] != "http.response.body" or size_limit_exceeded is True: forward message unchanged.
     c) On "http.response.body" while accumulating:
        - Append message["body"] to accumulated_body.
        - If len(accumulated_body) > max_body_bytes: send the accumulated buffer with {"type": "http.response.body", "body": accumulated_body, "more_body": True}, set size_limit_exceeded = True, and return.
        - If message.get("more_body") is falsy (final chunk): compute trace_info and attempt injection based on content-type and body content; send the final (possibly modified) body.
4. Use with capture_traces(traces): await self.app(scope, receive, wrapped_send). The capture_traces context manager may register traces in a per-task mapping for the duration of the with-block only if a task id is resolvable; if it registered, it will remove the mapping on exit. If no task id is resolvable, no mapping change occurs.
5. After the with-block exits and the downstream app finishes sending response messages, __call__ returns.

Cleanup:
- No explicit close; per-request registration cleanup is handled by capture_traces when applicable. There are no additional resources retained by the instance between requests.

## Method Map:
flowchart LR
    Init[__init__(app)] --> Instance[AsgiTracer instance]
    Instance --> Call[__call__(scope, receive, send)]
    Call --> QueryCheck{b"_trace=1" in scope.query_string?}
    QueryCheck -- No --> ForwardAll[await app(scope, receive, send)]
    QueryCheck -- Yes --> TracingSetup[setup traces, accumulated_body, response_headers]
    TracingSetup --> Capture[enter capture_traces(traces)]
    Capture --> AwaitDownstream[await app(scope, receive, wrapped_send)]
    AwaitDownstream --> WrappedSend[wrapped_send(message)]
    WrappedSend --> OnStart["http.response.start" -> record headers + forward]
    WrappedSend --> OnBody["http.response.body" -> accumulate or forward]
    OnBody --> SizeCheck{len(accumulated_body) > max_body_bytes?}
    SizeCheck -- Yes --> SendPartial[send accumulated with more_body=True; set size_limit_exceeded]
    SizeCheck -- No --> FinalCheck{message.get("more_body") falsy?}
    FinalCheck -- No --> WaitNext[wait for next chunk]
    FinalCheck -- Yes --> Inject[compute trace_info, inject into HTML/JSON when possible, send final body]
    Inject --> ExitCtx[exit capture_traces -> cleanup if registered]
    ExitCtx --> Return[return from __call__]

## Raises:
- __init__: does not validate the app; if app is not callable, subsequent invocation will raise TypeError when awaited.
- __call__ may let the following exceptions propagate:
  - Any exception raised by the downstream application, the receive callable, or the provided send callable.
  - KeyError: if an ASGI message lacks the "type" key and the code indexes message["type"].
  - UnicodeDecodeError: when decoding header values from bytes to UTF-8 for content-type extraction.
  - json.JSONDecodeError (ValueError): when the body appears to be JSON (starts with b"{") but json.loads fails.
  - KeyError or TypeError when computing sum(t["duration_ms"] for t in traces): if any trace entry lacks the "duration_ms" key, KeyError is raised; if a duration_ms value is non-numeric, TypeError may be raised during summation. These exceptions will propagate.
  - NameError: if capture_traces relies on a module-level mapping that is absent or misnamed, assignment operations inside capture_traces may raise NameError.
Note: AsgiTracer intentionally does not swallow these exceptions; they surface to the ASGI server.

## Example:
- Instantiate middleware:
  tracer = AsgiTracer(downstream_app)
  # Supply tracer as the ASGI app to your server or middleware stack.

- Typical traced request flow:
  1. Client requests /page?_trace=1 (raw query_string includes b"_trace=1").
  2. Server calls await tracer(scope, receive, send).
  3. AsgiTracer sets up traces = [] and enters capture_traces(traces). If capture_traces registers the traces object (task id resolvable), instrumentation code can append dicts containing at least a numeric "duration_ms" key.
  4. Downstream app is awaited with send replaced by wrapped_send; wrapped_send accumulates body chunks (up to max_body_bytes).
  5. On final chunk, AsgiTracer builds trace_info:
     {
       "request_duration_ms": 1000 * (time.perf_counter() - trace_start),
       "sum_trace_duration_ms": sum(t["duration_ms"] for t in traces),
       "num_traces": len(traces),
       "traces": traces
     }
     and injects it into HTML or JSON responses when applicable, then sends the final body.
  6. capture_traces removes the registration when it had previously registered (if any), and __call__ returns.

Implementation hints:
- For content-type detection: find the first header pair where name.lower() == b"content-type" and decode the value as UTF-8; treat missing header as empty string.
- For HTML injection: produce an escaped JSON string of trace_info (use a safe HTML escape) and place it inside a <pre> element immediately before each b"</body>" occurrence; replace operates on bytes with UTF-8 encoding for the injected fragment.
- For JSON injection: only attempt when body starts with b"{". Load, mutate by adding "_trace" if absent, and re-serialize; original whitespace/ordering will be lost.
- Respect the max_body_bytes limit to avoid excessive memory use; when exceeded, forward what has been accumulated with more_body=True and skip injection.

### `datasette.tracer.AsgiTracer.__init__` · *method*

## Summary:
Store the downstream ASGI application on the tracer instance so the tracer can forward requests to it.

## Description:
This initializer runs at object construction time (creation lifecycle). Typical callers:
- Application setup code that wraps a downstream ASGI app, e.g. tracer = AsgiTracer(downstream_app).
- Tests that instantiate AsgiTracer directly to exercise middleware behavior.

It performs a single, focused responsibility: retain a reference to the provided downstream app for later use by the middleware's __call__ method. This logic is its own method because initializing instance attributes is the standard object-construction step; separating it from __call__ keeps construction-time decisions (assignment of the downstream app) distinct from per-request runtime behavior.

## Args:
    app (Callable[[dict, Callable, Callable], Awaitable] | any):
        The downstream ASGI application or callable the tracer will wrap.
        Expected shape: callable accepting three arguments (scope, receive, send) and returning an awaitable (the ASGI convention).
        Allowed values: any object; __init__ does not enforce type checks. Passing a non-callable is permitted here but will likely cause a TypeError when the instance is later invoked as an ASGI app.

## Returns:
    None

## Raises:
    None raised directly by this method.
    Note: __init__ performs no validation. If the provided app is not a callable with the ASGI signature, invoking the tracer (via its __call__) will raise at that later time (for example, a TypeError when attempting to await a non-awaitable or calling a non-callable).

## State Changes:
Attributes READ:
    - None (this method does not read any existing instance attributes).

Attributes WRITTEN:
    - self.app: set to the passed-in app value.

## Constraints:
Preconditions:
    - None strictly required by __init__; the caller should supply the intended downstream app object. For correct runtime behavior the app should conform to the ASGI callable protocol (accept scope, receive, send and return an awaitable).

Postconditions:
    - After return, self.app is bound to the provided value and the AsgiTracer instance is ready to be used as middleware (i.e., can be passed to an ASGI server or awaited via its __call__).

## Side Effects:
    - None: no I/O, no global state mutation, and no external service calls occur. The method only stores the reference on the instance.

### `datasette.tracer.AsgiTracer.__call__` · *method*

## Summary:
Intercepts an ASGI request/response to collect per-request trace data and, when the request contains the trace flag, captures the full response body (up to a size limit) to inject trace information into HTML or JSON responses; does not modify object attributes.

## Description:
This async call method is the ASGI application entrypoint for the AsgiTracer middleware. An ASGI server (for example uvicorn/daphne) or an upstream ASGI middleware will call this coroutine for each incoming request. Typical callers and context:
- ASGI server or middleware invoking the application callable during the request handling lifecycle.
- It runs during the request/response pipeline: it inspects the incoming scope for a tracing query flag, then invokes the wrapped downstream app and intercepts messages sent by that app via a wrapped `send` coroutine.

Why this logic is a separate method:
- It implements the ASGI application protocol for the tracer middleware, needs to be awaited by the server, and must wrap the provided send callable to capture/modify response body chunks. Keeping this as a dedicated async call method cleanly separates middleware behavior from other tracer utilities and allows it to be used directly as an ASGI app.

## Args:
    scope (dict): ASGI connection scope for the incoming request. The method reads scope.get("query_string", b"") (expects bytes) to find the trace flag. Scope must be a mapping-like object per ASGI spec.
    receive (Callable[[], Awaitable[dict]]): Async callable to receive ASGI events from the server. Not inspected by this method beyond passing it to the downstream app.
    send (Callable[[dict], Awaitable[None]]): Async callable to send ASGI events to the server. This method wraps `send` to intercept "http.response.start" and "http.response.body" messages.

## Returns:
    None: This coroutine completes after the downstream application returns and the final response message(s) have been forwarded (possibly modified). It does not produce a return value; its effect is to forward ASGI messages via the supplied `send` callable.

## Raises:
    Any exception raised by the downstream application (self.app), by `receive`, or by `send` will propagate to the caller.
    json.JSONDecodeError (or ValueError): If response content-type looks like JSON and the body starts with "{" but the body is invalid JSON, json.loads will raise; this propagates.
    UnicodeDecodeError: Decoding header values with UTF-8 can raise if header bytes are not valid UTF-8; this can propagate.
    KeyError: If an ASGI message is missing the expected "type" key, the method's indexing message["type"] will raise.
    Note: Extraction of content-type from the recorded response headers handles the case of no content-type gracefully (it catches IndexError and treats content-type as empty string).

## State Changes:
Attributes READ:
    - self.app: the downstream ASGI application to call.
    - self.max_body_bytes: integer size limit used to decide whether to stop accumulating response body chunks.
Attributes WRITTEN:
    - None of the AsgiTracer instance attributes are modified by this method.

Local/mutable state mutated (not object attributes):
    - The local `traces` list is passed into capture_traces(traces); instrumentation code running concurrently may append trace entries to this list while the downstream app runs.
    - The capture_traces context manager will register the `traces` object in a module-level mapping for the current task for the duration of the request, and unregister it on exit (module-level mutation).

## Constraints:
Preconditions:
    - `scope` should implement .get("query_string", b"") and return bytes for the query string; the method searches for the literal byte substring b"_trace=1" among '&'-separated query params.
    - `send` and `receive` must behave according to the ASGI spec (accept and produce mapping-like messages).
    - `self.max_body_bytes` should be a positive integer (class default is 256 KB).
    - The downstream app must send ASGI messages with "type" keys such as "http.response.start" and "http.response.body" and follow ASGI semantics for "more_body".
Postconditions:
    - If the incoming scope does not contain the b"_trace=1" flag in the query string, this method simply forwards all events from the downstream app via the original `send` and returns.
    - If tracing is enabled in the query string:
        * The method will have forwarded the original "http.response.start" message (if any).
        * It will attempt to accumulate the full response body up to `self.max_body_bytes`. If the body exceeds the limit, it sends the accumulated bytes once with "more_body": True and stops attempting to inject trace info.
        * If the method successfully accumulates the final response body chunk (i.e., it sees a body message whose more_body is missing or false), it will inject trace information into HTML responses that contain a </body> tag or attach a "_trace" key to JSON object responses (only when body starts with "{"), then send the final body.
        * Any tracer registration performed by capture_traces(traces) will be unregistered when the with-block exits.

## Side Effects:
    - Calls and awaits `self.app(scope, receive, wrapped_send)`, which runs the downstream ASGI application (may perform arbitrary I/O).
    - Calls and awaits the provided `send` callable to forward ASGI messages; these calls drive network I/O in the ASGI server.
    - Uses the capture_traces context manager with the local `traces` list; capture_traces mutates a module-level mapping to register/unregister the tracer object for the current task (module-level side effect visible to other instrumentation code).
    - May deserialize and reserialize JSON bodies (cpu/memory work) and will call markupsafe.escape and json.dumps to render trace info.
    - If content-type header is missing or not matching JSON/HTML cases, the response body is forwarded unchanged (unless the body is too large, in which case partial body is sent and trace injection is skipped).

## Important implementation notes and edge cases:
    - Detection of tracing request: the method only enables tracing when the raw query string contains the byte token b"_trace=1" among '&'-separated parts; it performs a simple substring check and does not parse URL-escaping.
    - Response header format: `response_headers` is expected to be a sequence of (name_bytes, value_bytes) pairs (ASGI bytes headers). The code decodes header values using UTF-8; if no content-type header is present, content_type defaults to empty string.
    - Body accumulation and size-limiting:
        * The method concatenates successive "http.response.body" message["body"] bytes into a single buffer until the final chunk is seen or the buffer exceeds `self.max_body_bytes`.
        * When the buffer exceeds `self.max_body_bytes`, it immediately sends the buffered data with "more_body": True and sets a flag to stop further accumulation and injection.
    - Determining end-of-body: the method treats the message as final when message.get("more_body") is falsy (None or False). If the downstream app omits the "more_body" key for intermediate chunks, behavior may be incorrect.
    - HTML injection: it replaces occurrences of b"</body>" with the original bytes plus an injected <pre> block containing escaped JSON of trace_info; replacement is a global replace, so multiple </body> occurrences would all receive the injection.
    - JSON injection: only attempted when content-type contains "json" and the body begins with b"{". The code loads, mutates (adds "_trace" if missing), and re-dumps; original ordering and formatting of JSON is not preserved.
    - Exceptions from JSON operations or malformed headers will propagate to the caller; only the absence of content-type header is handled explicitly.

## Trace information structure injected:
When injection occurs the trace information dictionary has the shape:
    {
        "request_duration_ms": float,         # total request time in milliseconds (time.perf_counter())
        "sum_trace_duration_ms": float,       # sum of duration_ms values from collected traces
        "num_traces": int,                    # number of trace entries collected
        "traces": list                        # the traces list captured from capture_traces
    }

This is the same structure embedded into HTML (escaped and wrapped in a <pre>) or added as the "_trace" key on top-level JSON objects.

## Example usage (behavioral, not code snippet):
- When called by an ASGI server for a request with query string _trace=1, this middleware will collect traces produced by instrumentation during the request, and if the response is small enough and is HTML or JSON, it will augment the response body with those traces before sending the final body to the client.

