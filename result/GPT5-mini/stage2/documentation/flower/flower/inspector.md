# `inspector.py`

## `flower.inspector.Inspector` · *class*

block.

Action: WRITE
<DOCUMENTATION>
## Summary:
Represents a lightweight inspector that issues Celery control inspect commands (stats, queues, registered tasks, scheduled tasks, active tasks, reserved tasks, revoked tasks, and configuration) against one or all workers and collects their responses into an in-memory workers table.

## Description:
Use this class when you need to poll Celery worker state from an event loop and aggregate the received responses per worker. Typical callers instantiate Inspector with an event loop (that supports run_in_executor and add_callback) and a Celery app (or a control-like object) and then call inspect() to concurrently request multiple inspect endpoints. The class encapsulates:
- issuing multiple inspect commands concurrently (one per method in methods)
- converting remote inspect results into local updates
- storing the latest response per worker and method, along with a timestamp

Motivation: The Inspector isolates the logic of interacting with the Celery control.inspect API from the rest of the application and adapts asynchronous event-loop execution (run_in_executor / add_callback) to update a simple shared in-memory structure. This separation keeps polling and response-processing concerns centralized.

Known callers/factory patterns:
- Any code that needs periodic or on-demand snapshots of worker state can create an Inspector, call inspect() to schedule requests, and read the inspector.workers mapping for results.
- The class does not provide its own scheduling; external schedulers or callers (e.g., a periodic callback) should call inspect() as required.

Responsibility boundary:
- Does: schedule inspect calls, process responses, store latest per-worker state.
- Does not: implement persistent storage, manage worker lifecycles, or provide a high-level API for querying aggregated metrics (reading of the workers mapping must be done by callers).

## State:
- methods (class attribute): tuple[str]
  - Value: ('stats', 'active_queues', 'registered', 'scheduled', 'active', 'reserved', 'revoked', 'conf')
  - Invariant: order is stable and defines which inspect operations will be issued by inspect().

- io_loop (instance attribute): object
  - Required interface:
    - run_in_executor(executor, func) -> future-like object: used to schedule _inspect(method, workername) concurrently; the returned objects are collected and returned by inspect().
    - add_callback(callback): used to schedule _on_update callbacks back on the loop when inspect responses arrive.
  - Constraints: Must accept None as the executor argument (common in Python's asyncio/tornado interfaces). If these methods are missing or behave differently, Inspector operations will fail.

- capp (instance attribute): object
  - Expected interface:
    - capp.control.inspect(timeout=..., destination=...) -> inspect_controller
      - inspect_controller must support callables for each method named in methods (e.g., inspect_controller.stats(), inspect_controller.active(safe=True), etc.).
  - Behavior: Inspect controller methods must return either:
    - a mapping {worker_name: response} where response can be any JSON-serializable structure representing that method's data, or
    - None to indicate failure, or
    - a mapping that includes an 'error' key to signal failure for the whole call.

- timeout (instance attribute): int | float
  - Interpretation: seconds to pass to capp.control.inspect when creating the inspect controller.
  - Constraints: Must be a non-negative numeric value. Negative values may be passed through to the underlying API and will behave according to that API.

- workers (instance attribute): collections.defaultdict(dict)
  - Shape: mapping worker_name (str) -> info dict
  - info dict contents:
    - keys: method name strings (from methods) mapped to the most recent response object returned by that method for this worker
    - 'timestamp': float Unix epoch seconds added/updated whenever any method response is recorded for the worker
  - Invariants:
    - Every info dict will have a 'timestamp' key after at least one successful _on_update call for that worker.
    - Responses are never pruned by Inspector (callers must manage lifetime/cleanup if necessary).

- logger (module-level expected usage)
  - The class invokes logger.debug and logger.warning. The module should define a module-level logger (for example, logging.getLogger(__name__)). If no logger is defined in the module namespace, NameError will occur at runtime. Inspector does not create or configure the logger itself.

## Lifecycle:
Creation:
- Instantiate with Inspector(io_loop, capp, timeout)
  - io_loop: event loop-like object with run_in_executor and add_callback
  - capp: Celery app-like object exposing control.inspect
  - timeout: numeric seconds for inspection calls
- After construction, Inspector.workers is an empty defaultdict(dict) and ready to accept updates.

Usage:
- Call inspect(workername=None) to schedule a set of inspect operations for all methods declared in methods. If workername is provided (string), only that worker will be targeted.
- inspect() returns a list of future-like objects (exact future type depends on io_loop.run_in_executor). Callers can wait on or attach callbacks to these futures if they need to observe completion of each method's execution.
- When each inspect method completes, Inspector schedules _on_update on the io_loop via add_callback; _on_update updates the workers mapping and timestamp.
- Typical ordering: instantiate -> call inspect(...) optionally repeatedly -> read or export Inspector.workers to observe latest per-worker responses.

Sequencing / ordering rules:
- There is no required order of method invocations; inspect() will concurrently issue all methods every time it is called.
- Callers must not assume that updates arrive or apply in any particular order; each method updates only its own key in the worker info dict.

Destruction / cleanup:
- Inspector does not provide explicit cleanup, close(), or context-manager behavior.
- There are no asynchronous cancellation or shutdown hooks; if the surrounding application wishes to stop inflight inspect calls, it must use the returned futures and the io_loop facilities to cancel them (if supported).
- The workers mapping persists for the lifetime of the Inspector instance.

## Method Map:
Flowchart of primary method interactions and typical invocation order:

graph TD
    A[Caller] -->|calls inspect(workername?)| B[Inspector.inspect]
    B --> C[io_loop.run_in_executor for each method]
    C --> D[_inspect(method, workername) executed in executor]
    D -->|on successful response| E[io_loop.add_callback(partial(_on_update))]
    E --> F[_on_update(workername, method, response)]
    F --> G[update workers[workername][method] and workers[workername]['timestamp']]

(Note: the above is a textual mermaid-compatible flow where B issues concurrent tasks (C) that run _inspect (D), then schedule _on_update (E) which mutates the shared workers map (F->G).)

## Method details (behavioral summary):
- inspect(workername=None) -> list[future-like]
  - Schedules one executor task per method in methods by delegating to io_loop.run_in_executor(None, partial(self._inspect, method, workername)).
  - Returns a list of the futures returned by run_in_executor in the same order as methods.
  - Does not block; scheduling errors raised by run_in_executor are propagated to the caller.

- _inspect(method, workername) -> None
  - Internal synchronous function executed in an executor thread/process.
  - Builds destination = [workername] when workername is provided (string), otherwise destination = None to target all workers.
  - Calls self.capp.control.inspect(timeout=self.timeout, destination=destination) to obtain an inspect controller.
  - Invokes the method on the controller:
    - For method == 'active': calls inspect.active(safe=True)
    - For other methods: calls inspect.<method>() with no args
  - Logs debug information including elapsed time.
  - If the controller call returns None or a mapping that contains the key 'error', logs a warning and returns without scheduling updates.
  - Otherwise, iterates result.items(); for each (worker, response) pair where response is not None, schedules self._on_update(worker, method, response) to run on the io_loop using add_callback.
  - Exceptions:
    - Underlying exceptions from capp.control.inspect or from invoking the controller method may propagate if not caught by the underlying control.inspect implementation. Inspector does not explicitly catch exceptions here; callers should be prepared to handle exceptions raised from the returned futures.

- _on_update(workername, method, response) -> None
  - Internal callback intended to run on the event loop thread.
  - Ensures an info dict exists for the worker in self.workers (defaultdict behavior).
  - Sets info[method] = response and info['timestamp'] = time.time().
  - Quick, non-blocking update; should not raise under normal conditions (unless response cannot be stored in a dict or time.time() fails, which are unlikely).

## Raises:
- __init__(io_loop, capp, timeout)
  - Does not explicitly raise, but potential runtime errors:
    - If io_loop or capp is None or of an unexpected shape, errors will be raised later when methods are used.
- inspect(workername=None)
  - Errors can propagate from io_loop.run_in_executor if the io_loop implementation validates arguments synchronously (e.g., TypeError when run_in_executor is missing).
- _inspect(method, workername)
  - May raise AttributeError if the inspect controller returned by capp.control.inspect lacks an attribute matching method.
  - May propagate any exception raised by capp.control.inspect or by the controller method invocation.
- _on_update(...) does not raise under normal circumstances; if it does, exceptions will propagate to the event loop's callback handling mechanism.

## Edge cases and notes:
- If inspect controller methods return None or a mapping containing the key 'error', Inspector will log a warning and ignore that method's results for this call.
- Responses equal to None for a particular worker are ignored (no update recorded for that worker/method).
- There is no built-in rate limiting, debouncing, or deduplication. Repeated calls to inspect() will schedule new concurrent tasks regardless of previous in-flight tasks.
- The class expects a module-level logger object named logger to be present (used via logger.debug and logger.warning). If the module does not define logger, a NameError will occur. It is recommended to define at module import time: logger = logging.getLogger(__name__).

## Example:
- Creation:
    inspector = Inspector(io_loop, capp, timeout=5.0)
- Schedule an inspection for all workers:
    futures = inspector.inspect()           # returns list of futures (one per method)
- Optionally wait or attach callbacks to futures depending on the io_loop implementation.
- Read aggregated results:
    snapshot = inspector.workers           # dict: worker_name -> {'stats': ..., 'active': ..., 'timestamp': 162...}
- Target a single worker:
    inspector.inspect(workername='worker1@example.com')
- No explicit cleanup required; to stop using the object, drop references to it and let GC reclaim it.

### `flower.inspector.Inspector.__init__` · *method*

## Summary:
Initializes an Inspector instance by storing the provided event-loop, Celery-app-like object, and timeout, and creating an empty workers mapping (collections.defaultdict(dict)) on the instance.

## Description:
This constructor establishes the minimal state an Inspector needs to operate: a reference to an event loop-like object (io_loop), a Celery-app-like control object (capp), a numeric timeout, and an initially-empty workers mapping to hold per-worker inspection results.

Known callers and lifecycle stage:
- Exact call sites are not provided in the available source. Typical callers are higher-level components that create an Inspector prior to invoking its operational methods (for example, components that will schedule inspect operations or poll worker state).
- Lifecycle stage: called once at object creation time. After __init__ returns, the Inspector instance should be ready for any subsequent instance methods that rely on these attributes.

Why this is a dedicated method:
- Centralizes object state setup and ensures the workers mapping is created with the intended default factory (dict). Keeping initialization logic in __init__ makes the instance predictable and ensures downstream methods can assume these attributes exist.

## Args:
    io_loop (object):
        An event-loop-like object stored on self.io_loop.
        Expected capabilities (caller must ensure these exist):
            - run_in_executor(...) and/or add_callback(...) are commonly expected by code that performs async scheduling or posts callbacks to the loop.
        Allowed values: any object. If the object lacks required methods, errors will manifest later when those methods are used.
    capp (object):
        A Celery-app-like or control-like object stored on self.capp.
        Expected usage by other Inspector methods: the object will be used to call control.inspect(...). The constructor does not validate the object.
    timeout (int | float):
        Numeric value (seconds) stored on self.timeout and intended for use when making inspect/control calls.
        Allowed values: any numeric value; non-negative values are typical. __init__ does not enforce range checks.

## Returns:
    None
    - As a constructor, it does not return a meaningful value; it returns the new Inspector instance as per normal object construction semantics.

## Raises:
    - The __init__ method does not explicitly raise any exceptions.
    - Possible runtime errors only if:
        - The module-level name collections is missing or shadowed (not the case given imports).
        - Provided arguments are of types that later cause exceptions in other methods; those errors will occur when those methods are invoked, not during __init__.

## State Changes:
Attributes READ:
    - None. The constructor does not read any pre-existing instance attributes.

Attributes WRITTEN:
    - self.io_loop: set to the io_loop argument.
    - self.capp: set to the capp argument.
    - self.timeout: set to the timeout argument.
    - self.workers: set to collections.defaultdict(dict), an initially-empty mapping that creates a new dict for missing keys.

## Constraints:
Preconditions:
    - Callers should provide a valid io_loop and capp appropriate for the Inspector's later use. __init__ does not validate these objects.
    - timeout should be a numeric type appropriate for downstream calls that expect seconds.

Postconditions:
    - After __init__ completes:
        - self.io_loop, self.capp, and self.timeout are available and contain the provided values.
        - self.workers is a collections.defaultdict whose default factory is dict, so accessing self.workers[worker_name] will create and return an empty dict if that key did not previously exist.

## Side Effects:
    - No I/O is performed.
    - No external services are contacted.
    - The only observable mutation is the creation and population of the new Inspector object's attributes.
    - No global state is modified by this constructor.

### `flower.inspector.Inspector.inspect` · *method*

## Summary:
Schedules a background task for each configured inspect operation by submitting partial(self._inspect, method, workername) to the I/O loop's executor and returns the list of returned future-like objects. The call itself does not synchronously mutate Inspector state; scheduled tasks and their callbacks will update self.workers later.

## Description:
Known callers and lifecycle:
    - Intended to be invoked by external code that needs to initiate a round of Celery inspections (e.g., a periodic poller or an on-demand administration action). There are no callers within this module.
    - Invocation typically marks the beginning of an inspection cycle: it schedules all per-method inspect tasks and returns immediately so the caller remains non-blocking.

Why this is its own method:
    - Centralizes the logic for scheduling multiple inspector tasks (one per inspect method), keeping executor submission details in one place and separating orchestration from the blocking inspect logic implemented in _inspect. This enables running blocking I/O off the main loop and lets _inspect focus on the I/O and callback scheduling.

## Args:
    workername (str | None): Optional worker identifier to target.
        - If a string, each scheduled _inspect will run with that workername (targeting a single worker).
        - If None (default), scheduled _inspect calls target all workers.

## Returns:
    list[future-like]:
        - A list with one element per entry in self.methods. Each element is whatever self.io_loop.run_in_executor returns when called as shown in the implementation (i.e., a future-like object representing the scheduled execution of partial(self._inspect, method, workername)).
        - Each returned future will complete when the corresponding _inspect task finishes; results of _inspect are None, so futures typically resolve to None unless an exception occurs.
        - Edge cases:
            * If self.methods is empty, an empty list is returned.
            * If self.io_loop.run_in_executor raises an exception synchronously for any method, that exception propagates immediately and no list is returned.

## Raises:
    - AttributeError: if self.io_loop, self.methods, or self._inspect are missing.
    - TypeError: if self.methods is not iterable.
    - Any exception raised synchronously by self.io_loop.run_in_executor will propagate to the caller.
    - Exceptions raised during asynchronous execution of the scheduled tasks do not raise here; they surface through the returned futures.

## State Changes:
Attributes READ:
    - self.methods: iterated to determine which inspect calls to schedule.
    - self.io_loop: invoked to run tasks in an executor (run_in_executor called).
    - self._inspect: referenced via functools.partial to create the task callable.
Attributes WRITTEN:
    - None synchronously. This method does not modify self.workers or other attributes directly.
    - Indirect writes: scheduled _inspect tasks will schedule callbacks (self.io_loop.add_callback) that call self._on_update and mutate self.workers when those callbacks execute.

## Constraints:
Preconditions:
    - self.methods must be an iterable of method-name strings (the class defines a default tuple of supported names).
    - self.io_loop must implement run_in_executor(executor, func, *args) and accept None as the executor argument (None delegates to a default executor).
    - self._inspect must be a callable accepting (method: str, workername: Optional[str]).
    - workername, if provided, must be a string acceptable to _inspect and the underlying Celery inspect API.

Postconditions:
    - For each element in self.methods, a task has been submitted via self.io_loop.run_in_executor(None, partial(self._inspect, method, workername)) and the list of returned futures is returned to the caller.
    - No synchronous changes to self.workers or other Inspector state are made by this method.

## Side Effects:
    - Scheduling: submits N tasks (N == len(self.methods)) to the I/O loop's executor using run_in_executor with executor argument set to None and the callable set to partial(self._inspect, method, workername).
    - The scheduled tasks will perform network I/O and logging inside _inspect and will schedule callbacks to mutate Inspector state; those side effects occur asynchronously and are not caused directly by this method.
    - This method itself performs no blocking I/O and writes no external resources synchronously.

### `flower.inspector.Inspector._on_update` · *method*

## Summary:
Update the per-worker inspection record by storing the response for a given inspection method and stamping the record with the current time.

## Description:
This method is invoked when an inspection result for a particular worker and method is ready and should be merged into the Inspector's in-memory state.
Known callers and call flow:
- Inspector.inspect() schedules inspector._inspect(...) to run in a thread executor.
- Inspector._inspect(...) performs the remote/control inspect call and, for each worker result, schedules this method to run in the IO loop thread via self.io_loop.add_callback(partial(self._on_update, worker, method, response)).
Lifecycle/context:
- Called during the periodic or on-demand inspection lifecycle to record the latest reported state from workers.
Why this is a separate method:
- _on_update is a small callback intended to run in the IO loop (single-threaded) for safe, quick mutation of shared state. Separating it keeps the network/inspect logic (_inspect) decoupled from the state update and ensures updates occur on the IO loop thread.

## Args:
    workername (str): The worker identifier (typically a hostname or worker name) used as the key in self.workers.
    method (str): The name of the inspect method whose response is being recorded. Callers normally pass one of Inspector.methods (e.g., 'stats', 'active', 'scheduled', ...), but the method is not validated here.
    response (Any): The inspection response value returned by the control.inspect <method>. Usually a serializable mapping or list describing the worker's state; can be any Python object.

## Returns:
    None: This method performs in-place mutation of self.workers and does not return a value.

## Raises:
    No exceptions are explicitly raised by this implementation.
    - It will not raise KeyError when accessing self.workers[workername] when self.workers is the default defaultdict(dict) initialized in Inspector.__init__ (this creates a new dict for unknown keys).
    - If self.workers has been replaced by a mapping type that raises on missing keys, a KeyError may occur when the key is absent. Similarly, if attributes used here are missing or incompatible types, attribute or type-related exceptions could propagate.

## State Changes:
Attributes READ:
    - self.workers

Attributes WRITTEN:
    - self.workers (mutated by writing into self.workers[workername]; the nested dict returned/created is assigned new keys)
    - In particular, for the per-worker dict 'info' (self.workers[workername]):
        - info[method] is set to response
        - info['timestamp'] is set to the current time (float from time.time())

## Constraints:
Preconditions:
    - self.workers must exist and be a mapping that supports self.workers[workername] for reading/creating the per-worker dict. The implementation expects the common initialization: self.workers = collections.defaultdict(dict).
    - workername should be a hashable key (typically a non-empty string). _inspect schedules only non-None responses, so callers normally provide a non-None response.
    - This method is intended to run on the IO loop thread (it is scheduled there by _inspect). Calling it concurrently from multiple threads without synchronization may cause race conditions.

Postconditions:
    - After the call, self.workers[workername][method] == response.
    - After the call, self.workers[workername]['timestamp'] is set to a float timestamp representing the time.time() at the moment of update.
    - Existing values for other methods in the same per-worker dict are preserved unless the same method key is overwritten.

## Side Effects:
    - Mutates in-memory state self.workers (no external I/O).
    - No network calls or blocking operations are performed.
    - No logging is performed by this method itself (logging is done in _inspect).
    - Because it mutates shared state, it should run on the IO loop thread to avoid race conditions; scheduling is typically done via self.io_loop.add_callback.

### `flower.inspector.Inspector._inspect` · *method*

## Summary:
Performs a single Celery control inspect call for the given inspect-method and (optionally) a specific worker, measures its duration, and schedules result handling callbacks on the object I/O loop. Does not directly modify Inspector state; instead it enqueues callbacks that will update self.workers.

## Description:
This method is invoked from Inspector.inspect by scheduling it on a background executor:
- Known caller: Inspector.inspect, which calls io_loop.run_in_executor(None, partial(self._inspect, method, workername)) for each method in Inspector.methods.
- Invocation context: executed in a worker thread (executor) so it can perform blocking I/O (the Celery control.inspect call) without blocking the main I/O loop.
- Responsibility: isolate the blocking Celery control.inspect interaction and transform its results into callbacks that are executed back on the I/O loop. This separation keeps blocking operations out of the main thread and centralizes error handling and scheduling of the update callback.
- Why a separate method: The Celery inspect call is blocking and may take time; placing it in its own function makes it easy to run in an executor and to encapsulate the logic for calling the inspect API, measuring duration, interpreting common failure shapes (None or {'error': ...}), and scheduling the update callback.

## Args:
    method (str):
        - One of the inspect operation names expected by the Celery inspect API and by this Inspector instance.
        - Allowed values (as used by Inspector.methods): 'stats', 'active_queues', 'registered', 'scheduled', 'active', 'reserved', 'revoked', 'conf'.
        - Behavior: for method == 'active' the underlying inspect method is called with safe=True; for other methods it is called with no extra keyword args.
    workername (str | None):
        - If a string, the call is targeted to a single worker; the method sets destination = [workername].
        - If None, the call is sent with destination=None (which requests all workers).

## Returns:
    None
    - The method does not return any meaningful value. It returns implicitly None in all cases.
    - Edge behavior: on failure (result is None or result contains an 'error' key) the method returns early after logging a warning.

## Raises:
    - AttributeError: if the inspect controller object returned by self.capp.control.inspect(...) does not have the requested method attribute (getattr(inspect, method) will raise).
    - Any exception raised by the Celery control.inspect(...) call or by the invoked inspect method will propagate out of this function (there is no try/except that swallows exceptions).
    - Note: the method explicitly treats the common "failure shapes" (result is None or 'error' in result) as non-exceptional failure cases and returns; other unexpected exceptions are not caught here and will propagate to the executor.

## State Changes:
    Attributes READ:
        - self.capp (used to obtain capp.control.inspect(...))
        - self.timeout (used as the timeout argument to capp.control.inspect)
        - self.io_loop (used to schedule callbacks back onto the main loop via add_callback)
        - self._on_update (referenced when creating the partial callback scheduled on the I/O loop)
    Attributes WRITTEN:
        - None directly. This method does not mutate any self.<attr> fields synchronously.
        - Indirect / scheduled writes: when results are present, this method schedules partial(self._on_update, worker, method, response) on self.io_loop; when those callbacks execute they mutate self.workers (via _on_update).

## Constraints:
    Preconditions:
        - self.capp must be an object exposing .control.inspect(timeout=..., destination=...) that returns an object with methods matching the allowed inspect method names.
        - self.timeout must be a numeric timeout acceptable to the underlying capp.control.inspect API.
        - self.io_loop must support add_callback(callable) (and the caller must have used io_loop.run_in_executor to call _inspect).
        - method must be a string and preferably one of Inspector.methods; otherwise AttributeError or unexpected behavior may occur.
        - workername, if provided, must be a string acceptable as a destination identifier to the underlying inspect API.
    Postconditions:
        - If the underlying inspect call returns a mapping of worker -> response (and response is not None), for each such worker a callback will have been scheduled on self.io_loop that will call self._on_update(worker, method, response).
        - If the inspect result is None or contains an 'error' key, no callbacks are scheduled and the method returns after logging a warning.
        - No synchronous mutation to self.workers or other attributes happens inside this method; any state updates are deferred to callbacks executed on the I/O loop.

## Side Effects:
    - Network / I/O: calls into the Celery control API via self.capp.control.inspect(...), which may perform network operations and block until a response or timeout.
    - Logging: emits debug logs when sending the command and reporting elapsed time, and a warning log if the inspect result indicates failure.
    - Scheduling: calls self.io_loop.add_callback(...) to schedule a callback that will call self._on_update and thereby update Inspector state (self.workers). The scheduling of these callbacks is the primary means this method produces observable state changes.
    - Threading boundary: this method is intended to run in a background executor thread; the scheduled callbacks ensure subsequent state updates happen in the I/O loop's thread/context.

## Implementation notes / behavior details useful for reimplementation:
    - The duration measurement is performed with time.time(): record start before invoking the inspect method and log time.time() - start afterwards.
    - For the 'active' inspect method, call with safe=True (getattr(inspect, 'active')(safe=True)); for other methods call without kwargs.
    - Treat result == None or result containing an 'error' key as failure: log a warning and return without scheduling callbacks.
    - Iterate over result.items(): for each (worker, response) where response is not None, schedule partial(self._on_update, worker, method, response) via self.io_loop.add_callback.

