# `tasks.py`

## `flower.api.tasks.BaseTaskHandler` · *class*

*No documentation generated.*

### `flower.api.tasks.BaseTaskHandler.get_task_args` · *method*

## Summary:
Parses the HTTP request body as JSON and extracts positional args, keyword kwargs, and the remaining task options; it validates types for the top-level options object and for args, and returns a 3-tuple without modifying handler attributes.

## Description:
This helper method centralizes JSON parsing and validation for incoming task-invocation payloads. It is called during request handling by endpoints that accept task submission data (e.g., POST handlers on BaseTaskHandler subclasses) to obtain the arguments and options needed to create/apply a task to Celery.

Why separate:
- Keeps parsing and validation logic in one place so all endpoints share identical error responses and semantics.
- Simplifies endpoint handlers by returning a normalized (args, kwargs, options) triple.

Known callers / invocation context:
- Request handlers derived from BaseTaskHandler that implement task creation or dispatch endpoints call get_task_args() early in request processing to parse the client-provided payload.

## Args:
This method takes no explicit parameters; it reads the raw request payload at:
- self.request.body
  - type: bytes or str (as provided by Tornado)
  - semantics:
    - If empty or falsy, the method treats it as if the client provided an empty JSON object (equivalent to {}).
    - Otherwise, the value is passed to tornado.escape.json_decode for JSON decoding.

## Returns:
Tuple (args, kwargs, options)
- args
  - type: list or tuple
  - semantics: positional arguments to pass to the task
  - guarantee: the method enforces that args is a list or tuple; if not, it raises HTTPError(400, 'args must be an array')
  - default: when absent from the JSON, args is []
- kwargs
  - type: any JSON type (most commonly a dict)
  - semantics: the value of the 'kwargs' key in the decoded JSON payload
  - note: kwargs is NOT type-validated by this method — it simply uses options.pop('kwargs', {}) and returns the resulting value; callers should validate that it is a mapping if required
  - default: when absent from the JSON, kwargs is {}
- options
  - type: dict
  - semantics: the decoded JSON object with the 'args' and 'kwargs' keys removed (if they were present)
  - guarantee: the method enforces that the top-level decoded JSON is a dict; options will always be a dict when returned
  - default/edge-case: when the request body is empty, options is an empty dict {}

## Raises:
- tornado.web.HTTPError(400, <message>) raised in these cases:
  - Invalid JSON:
    - Trigger: tornado.escape.json_decode(body) raises ValueError for malformed JSON.
    - Message: the str(e) of the ValueError is used as the HTTPError message.
  - Top-level JSON not an object:
    - Trigger: decoded options is not an instance of dict (e.g., client sent a JSON array or literal).
    - Message: 'invalid options'
  - args not array-like:
    - Trigger: after popping 'args' from options, the value is not an instance of list or tuple.
    - Message: 'args must be an array'

These HTTPError exceptions are intended to produce a 400 Bad Request response to the client.

## State Changes:
Attributes READ:
- self.request.body

Attributes WRITTEN:
- None. The method does not write to any self.<attr> handler attributes.

Local mutation:
- The local variable options (the decoded dict) is mutated by popping 'args' and 'kwargs'; that mutated dict is returned as options.

## Constraints:
Preconditions:
- The handler (self) provides a .request object with a .body attribute containing the raw request payload.
- Caller expects JSON-encoded payloads for task arguments/options.

Postconditions:
- Return value is a triple (args, kwargs, options) where:
  - args is a list or tuple (validated)
  - kwargs is the exact JSON value provided for 'kwargs' (no type guarantees)
  - options is a dict that does not contain keys 'args' or 'kwargs'
- No handler attributes are modified by this method.

## Side Effects:
- Calls tornado.escape.json_decode to parse the request body (CPU/memory only; no external I/O).
- Raises HTTPError(400, ...) on invalid input which will abort request processing and produce a client-facing 400 response.
- Mutates the returned options dict by removing 'args' and 'kwargs'; nested objects inside options remain shared references from the decoded JSON.

### `flower.api.tasks.BaseTaskHandler.backend_configured` · *method*

## Summary:
Return True when the provided Celery result object has a configured backend (i.e., its backend is not the DisabledBackend), otherwise False. This check does not modify object state.

## Description:
This method performs a lightweight availability check to determine whether the result object's backend is configured (not DisabledBackend). It is intended to be used by HTTP handlers or other code paths that must decide whether it is safe to access result attributes such as .result or .traceback (which rely on a configured result backend).

Known callers and lifecycle context:
- No direct callers appear in the shown BaseTaskHandler methods in this file. Typical callers (outside this snippet) are request handlers or helper routines that:
  - Inspect or return a stored task's result or traceback to a client, or
  - Decide whether to query the backend for additional task metadata.
- Lifecycle stage: invoked at request-time when the server is handling client queries about a task's status or result and must first confirm the backend is available.

Why this is a separate method:
- Encapsulates the backend-availability check in a single, reusable location.
- Improves readability and reduces duplication wherever the code needs to guard accesses to result-backed data.
- Centralizes the shape of the check (DisabledBackend detection) so changes to the detection logic affect all callers consistently.

## Args:
    result (celery.result.AsyncResult | celery.contrib.abortable.AbortableAsyncResult | object):
        A result-like object that exposes a .backend attribute. Typically an AsyncResult or AbortableAsyncResult instance returned by the Celery API. The method does not inspect other attributes of the object.

## Returns:
    bool:
        True if result.backend is not an instance of celery.backends.base.DisabledBackend (i.e., a usable backend is configured).
        False if result.backend is an instance of DisabledBackend.
        Note: No other return values are produced.

## Raises:
    AttributeError:
        If the provided result object does not have a .backend attribute, accessing result.backend will raise AttributeError.
    Any other exception raised by evaluating isinstance(result.backend, DisabledBackend) (rare): the method does not catch exceptions.

## State Changes:
    Attributes READ:
        - result.backend (reads the backend attribute on the provided object)
    Attributes WRITTEN:
        - None on self or on the passed-in object; the function is read-only.

## Constraints:
    Preconditions:
        - The caller must provide an object with a .backend attribute (commonly a Celery AsyncResult or AbortableAsyncResult).
        - DisabledBackend must be importable (it is imported at module scope).

    Postconditions:
        - The method returns a boolean indicating presence (True) or absence (False) of a configured backend.
        - The provided result object is unchanged.

## Side Effects:
    - None: the method performs no I/O, no network calls, and performs no mutations of objects outside the read access to result.backend.

### `flower.api.tasks.BaseTaskHandler.write_error` · *method*

## Summary:
Set the HTTP response status code for the current handler without writing a response body or additional error payload.

## Description:
This method centralizes the handler's error-status behavior: it updates the handler's HTTP status to the provided code and returns immediately. It is a minimal override of Tornado-style handlers' error handling and exists so subclasses can override it to emit structured error bodies or perform logging when needed.

Known callers and typical invocation context:
- Tornado's request-handling/error path when an exception or an HTTPError is raised during request processing (the Tornado runtime invokes a handler's error-writing hook).
- Any code in this project's handler methods that chooses to call write_error(status_code) directly to short-circuit request handling with a specific HTTP status.

Why this is a separate method:
- Keeps error-status handling in one place so subclasses can customize error formatting (JSON error object, additional headers, logging) by overriding this method rather than modifying many request handlers.
- Keeps the BaseTaskHandler implementation intentionally minimal while providing an extension point for richer error responses.

## Args:
    status_code (int): HTTP status code to set on the handler (e.g., 400, 404, 500).
    **kwargs: Additional keyword arguments are accepted for compatibility with Tornado's write_error signature but are ignored by this implementation.

## Returns:
    None: The method does not return a value. Its observable effect is the handler's HTTP status being updated.

## Raises:
    No exceptions are raised explicitly by this method itself.
    - If the underlying set_status call rejects the provided status_code (for example, if a non-integer is passed), the underlying Tornado implementation may raise a TypeError or ValueError; those exceptions are not handled here.

## State Changes:
Attributes READ:
    - None (the method does not read any self.<attr> fields in this implementation).

Attributes WRITTEN:
    - The handler's HTTP status is updated via self.set_status(status_code). (This updates the handler's internal response status stored by the underlying RequestHandler; exact attribute name is part of the Tornado base class and not referenced directly here.)

## Constraints:
Preconditions:
    - The caller should provide a valid HTTP status integer. Passing non-integer or otherwise invalid status values may propagate errors from the underlying set_status implementation.

Postconditions:
    - After the call, the handler's HTTP response status will be set to the provided status_code.
    - No response body or headers are added by this method; downstream code is still responsible for writing any response body.

## Side Effects:
    - Mutates the handler's response status via a call to self.set_status(status_code).
    - No I/O (network, file) or external service calls are performed by this method.
    - No changes to objects outside the handler instance other than the handler's response state.

### `flower.api.tasks.BaseTaskHandler.update_response_result` · *method*

## Summary:
Update a response mapping in-place to include the task result (made JSON-safe) and, when the task failed, its traceback.

## Description:
This helper formats the AsyncResult-like object into the response payload returned by HTTP API handlers. It is intended to be called after a task's AsyncResult is retrieved from Celery (or an AbortableAsyncResult/AsyncResult-like object) as part of assembling a JSON response for clients.

Known callers / call site context:
- Invoked by HTTP handler code that composes task inspection or task-detail responses (i.e., endpoints that return the current state/result for a task). The typical lifecycle stage is: handler obtains an AsyncResult for a given task id, then calls this method to merge the task's result and optional traceback into the response dict before serializing it to JSON and returning it to the caller.

Rationale for being a separate method:
- Centralizes the logic for adding task results and failure tracebacks to HTTP responses so all task-related endpoints consistently:
  - apply the same JSON-safety transformation (via safe_result),
  - include traceback only on failure,
  - mutate the response in-place rather than replacing returned objects.
- Keeps handler code concise and avoids repeating the same conditional formatting in multiple places.

## Args:
    response (MutableMapping): A mutable mapping (typically a dict) that will be updated in-place. Must implement the mapping update method (response.update({...})).
    result (AsyncResult or AbortableAsyncResult or any object with .state, .result, .traceback attributes): The task result object returned by Celery backends. Expected attributes:
        - state (str): Task state constant (e.g., states.SUCCESS, states.FAILURE).
        - result: The task return value or exception payload.
        - traceback: A string containing the traceback when the task failed (may be None).

## Returns:
    None
    - The method updates the provided response mapping in-place and does not return a value (implicitly returns None).
    - After the call, response will contain at least the 'result' key; if the task state equals celery.states.FAILURE, response will also contain 'traceback'.

## Raises:
    This method does not raise exceptions itself.
    - It relies on self.safe_result to convert non-JSON-serializable results; safe_result handles TypeError internally and will not propagate it.
    - If the caller passes a response that does not support update(), a TypeError/AttributeError from the mapping operation may occur (this originates from the caller's misuse, not this method's logic).

## State Changes:
    Attributes READ:
        - self.safe_result (method) — called to produce a JSON-safe representation of result.result.
        - (implicitly) module-level constant states.FAILURE to compare result.state.

    Attributes WRITTEN:
        - None on self. The method does not modify any self.<attr> fields.

    External object mutations:
        - response: mutated in-place via response.update(...). After the call it will contain:
            - 'result': value returned by self.safe_result(result.result)
            - 'traceback': result.traceback (present only when result.state == states.FAILURE)

## Constraints:
    Preconditions:
        - response must be a mutable mapping implementing update(mapping) (e.g., dict).
        - result must expose the attributes: state, result, and traceback.
        - The expected state constants come from celery.states (i.e., comparing result.state to states.FAILURE is meaningful).

    Postconditions:
        - response contains a 'result' key whose value is the JSON-safe representation of result.result as produced by self.safe_result.
        - If result.state == states.FAILURE, response additionally contains a 'traceback' key set to result.traceback (which may be None).
        - No attributes on self are modified; no value is returned.

## Side Effects:
    - Mutates the passed-in response mapping in-place (no new mapping is returned).
    - No I/O is performed and no external services are contacted.
    - Relies on self.safe_result to call json.dumps internally; any side effects from safe_result (none in the provided implementation) would apply.

## Implementation notes and edge cases to preserve when reimplementing:
    - Always call self.safe_result(result.result) before inserting into response; do not attempt to re-serialize directly in this method.
    - Only include the 'traceback' field when result.state is exactly celery.states.FAILURE.
    - Do not swallow or transform traceback contents — copy result.traceback as-is.
    - Be tolerant of result.traceback being None; still include the key when state is FAILURE (consistent with the original behavior).

### `flower.api.tasks.BaseTaskHandler.normalize_options` · *method*

## Summary:
Convert scheduling-related option values found in the given options mapping into the Python types expected by downstream task submission code by mutating the mapping in-place (strings -> datetime or numeric types).

## Description:
Normalizes common Celery scheduling fields present in an options dict so subsequent task submission logic can use these fields without further parsing.

Known callers / invocation context:
- Primarily invoked by HTTP request handlers during task submission processing, immediately after parsing request JSON into an options mapping. See BaseTaskHandler.get_task_args which parses the request body into args, kwargs, and options.
- Called during the request handling lifecycle before options are handed off to task submission/broker logic so that scheduling fields are in the correct types for Celery or broker APIs.

Why a separate method:
- Encapsulates and centralizes parsing logic for 'eta', 'countdown', and 'expires' to avoid duplication and ensure consistent usage of self.DATE_FORMAT across handlers.

## Args:
    options (dict): A mutable mapping (typically the parsed JSON object from the request body) that may contain any of these keys:
        - 'eta': expected to be a string formatted according to self.DATE_FORMAT (e.g., '2020-01-01 12:00:00.000000'); after normalization it will be replaced by a datetime.datetime instance.
        - 'countdown': expected to be a numeric value or string representing a number (e.g., 10 or "10.5"); after normalization it will be replaced by a float.
        - 'expires': may be a numeric value (int/float) or numeric string, or a date string formatted according to self.DATE_FORMAT. After normalization it will be replaced by either a float (seconds) if float conversion succeeds, or a datetime.datetime if parsed as a date string.
    Notes:
        - The method mutates options in-place and returns None.
        - The method assumes callers ensure options is a dict; BaseTaskHandler.get_task_args enforces this earlier in the request flow.

## Returns:
    None
    - No return value; effects are visible through the mutated options mapping.

## Raises:
    The method does not catch most conversion exceptions; callers should be prepared to handle exceptions raised by the underlying conversions:
    - datetime.strptime(...) may raise ValueError if the string does not match self.DATE_FORMAT. (This will propagate for 'eta', and will propagate for 'expires' if float conversion raised ValueError and the fallback datetime parsing fails.)
    - float(...) may raise ValueError for non-numeric strings and TypeError for non-convertible types. Behavior by key:
        * 'eta': any exception raised by datetime.strptime (e.g., ValueError) will propagate.
        * 'countdown': any exception raised by float() (ValueError or TypeError) will propagate.
        * 'expires': float(expires) is attempted inside a try/except that catches ValueError only:
            - If float(expires) succeeds, options['expires'] becomes that float.
            - If float(expires) raises ValueError, the code falls back to datetime.strptime(expires, self.DATE_FORMAT); any exception from that call (e.g., ValueError) will propagate.
            - If float(expires) raises TypeError (or other exceptions besides ValueError), that exception is not caught and will propagate.

## State Changes:
    Attributes READ:
        - self.DATE_FORMAT (str): used as the format when calling datetime.strptime for 'eta' and the date-form of 'expires'.
    Attributes WRITTEN:
        - None on self. The method does not change any self.<attr>.
    Mutations to arguments:
        - options (dict) is mutated in-place:
            * 'eta' (if present) becomes a datetime.datetime parsed with self.DATE_FORMAT.
            * 'countdown' (if present) becomes a float.
            * 'expires' (if present) becomes either a float or a datetime.datetime as described above.

## Constraints:
    Preconditions:
        - options must be a dict-like mapping.
        - If present:
            * options['eta'] should be a string matching self.DATE_FORMAT.
            * options['countdown'] should be convertible to float.
            * options['expires'] should be convertible to float or be a string matching self.DATE_FORMAT.
    Postconditions:
        - For each normalized key that existed in options:
            * 'eta' -> datetime.datetime (or exception propagated)
            * 'countdown' -> float (or exception propagated)
            * 'expires' -> float or datetime.datetime (or exception propagated)
        - The method returns None.

## Side Effects:
    - In-place mutation of the provided options mapping; original string values for normalized keys will be lost.
    - No I/O, logging, network calls, or global state modifications are performed.
    - No other objects are mutated.

### `flower.api.tasks.BaseTaskHandler.safe_result` · *method*

## Summary:
Return a JSON-safe value for inclusion in JSON outputs: if the input is JSON-serializable, return it unchanged; otherwise return its string representation.

## Description:
This method verifies whether the provided result can be serialized by the standard json module. It calls json.dumps(result) solely as a liveness/test check; it does not use or return the serialized string. If json.dumps(result) raises TypeError (indicating the object is not JSON-serializable), the method returns repr(result) so callers receive a string instead of an unserializable object.

Callers and context:
- The source snippet does not include explicit call sites. This utility is intended for use where values will be embedded in JSON responses (for example, HTTP API handlers preparing JSON payloads) so that the returned value is safe to pass to json.dumps later.

Why this method is distinct:
- Encapsulates the simple policy "try JSON-serialize, otherwise use repr" in one place for clarity, testability, and to avoid duplicating this fallback logic wherever task results are prepared for JSON output.

## Args:
    result (Any): The value to test/normalize. Can be any Python object.

## Returns:
    Any: Either:
      - the original result object (unchanged) if json.dumps(result) succeeds, ensuring it is JSON-serializable; or
      - a str equal to repr(result) if json.dumps(result) raised TypeError, guaranteeing a JSON-serializable string is returned.

## Raises:
    - Any exception other than TypeError raised by json.dumps(result) will propagate to the caller.
    - Any exception raised during repr(result) (for example, from a custom __repr__ implementation) will propagate to the caller.

## State Changes:
    Attributes READ:
        - None (the method does not access any attributes on self)
    Attributes WRITTEN:
        - None (the method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - None required: callers may pass any Python object as result.
    Postconditions:
        - The returned value is JSON-serializable by json.dumps (either the original value if serializable, or a string).
        - The method does not mutate the input object.

## Side Effects:
    - No I/O or external service calls.
    - The method may invoke result.__repr__ when falling back; that call can execute arbitrary user code and may have side effects or raise exceptions.

## `flower.api.tasks.TaskApply` · *class*

## Summary:
Handles authenticated HTTP POST requests to apply (submit) a Celery task by name; it parses the request payload into task args/options, enqueues the task via apply_async, waits for completion in a thread executor, and returns a JSON response containing task metadata and, when available, the task result/state/traceback.

## Description:
TaskApply is a Tornado request handler endpoint intended to expose a server-side API for submitting Celery tasks by name (URL parameter). It is used when an authenticated client wants to invoke a registered Celery task and receive the immediate result (blocking until the task finishes), or at least the resulting metadata when a backend is configured.

Typical usage scenario:
- A client issues an authenticated HTTP POST to the endpoint backing TaskApply with the task name in the URL and a JSON body containing "args", "kwargs", and other task options (e.g., countdown, eta, expires).
- The handler:
  1. Parses the request body into (args, kwargs, options) using BaseTaskHandler.get_task_args().
  2. Resolves the task by name from the Celery application (self.capp.tasks).
  3. Normalizes scheduling-related options via BaseTaskHandler.normalize_options(options).
  4. Calls task.apply_async(args=args, kwargs=kwargs, **options) to enqueue the task.
  5. Waits for completion by delegating wait_results to IOLoop.run_in_executor (non-blocking for the Tornado main loop).
  6. Writes a JSON response to the client with task-id and, when available, result/state/traceback.

Why this abstraction:
- Separates HTTP request parsing and validation (BaseTaskHandler helpers) from task submission logic.
- Consolidates the synchronous waiting and response population logic in a small, testable class (post + wait_results pair).
- Ensures the Tornado event loop remains responsive by blocking in a thread worker for the synchronous result.get call.

Known callers / instantiation:
- Tornado application route mapping constructs the handler when the endpoint receives a request (Tornado creates handler instances per request). The handler relies on the Tornado decorator @web.authenticated to require authentication.

## State:
TaskApply declares no instance attributes of its own in the class body. It relies on the following external/handler state provided by BaseTaskHandler and the Tornado framework:

- self.capp
  - Type: Celery application (object exposing .tasks mapping)
  - Valid values: any Celery app with a tasks registry mapping strings -> task objects
  - Invariant: self.capp.tasks is a mapping that can be indexed by task name to retrieve a task object; KeyError indicates unknown task.

- self.request
  - Type: Tornado HTTPRequest
  - Usage: BaseTaskHandler.get_task_args reads self.request.body.

- BaseTaskHandler helper methods and attributes used (read-only):
  - get_task_args() -> (args, kwargs, options)
    - args: list or tuple (positional args to pass to the task)
    - kwargs: value provided under "kwargs" in JSON (typically dict)
    - options: dict of remaining options (e.g., 'eta', 'countdown', 'expires'); must be dict
  - normalize_options(options)
    - Mutates options in-place converting string timestamps to datetime, numeric strings to float, etc.; may raise ValueError on invalid conversions.
  - update_response_result(response, result)
    - Mutates response mapping to include JSON-safe 'result' and optionally 'traceback' on FAILURE
  - backend_configured(result) -> bool
    - Returns True when result.backend is configured (not DisabledBackend)

- result returned by task.apply_async(...)
  - Type: celery.result.AsyncResult or similar
  - Expected attributes used:
    - task_id (str): present and used in response
    - get(propagate=False): blocking call used to wait for completion (called inside wait_results)
    - state (str): used optionally to add state to the final response when backend is configured
    - result and traceback: consumed by update_response_result

Class invariants:
- No per-request attribute mutation introduced by TaskApply beyond normal Tornado handler behavior.
- After post completes, a response has been written via self.write(response) for successful requests, or an HTTPError has been raised for invalid/unknown tasks or invalid options.

## Lifecycle:
Creation:
- Instantiated by Tornado when the matching route receives a request. No explicit __init__ parameters for TaskApply; Tornado supplies standard handler constructor args (application, request, etc.). There are no custom constructor constraints.

Usage (normal call sequence for a single HTTP request):
1. Tornado creates handler instance and routes request to TaskApply.post(taskname).
2. post(taskname) is invoked (async):
   - Calls get_task_args() to parse request body.
   - Looks up the task in self.capp.tasks by the provided taskname.
   - Calls normalize_options(options) to convert scheduling fields.
   - Calls task.apply_async(args=args, kwargs=kwargs, **options) to enqueue the job.
   - Builds a minimal response mapping: {'task-id': result.task_id}.
   - Delegates to IOLoop.current().run_in_executor(None, self.wait_results, result, response) to wait for the task to finish without blocking the main event loop.
   - Awaits the executor future (yielding control to the Tornado event loop).
   - Writes the final response mapping (potentially including result/state/traceback) via self.write(response).

3. wait_results(result, response) runs in an executor thread:
   - Calls result.get(propagate=False) to block until completion without propagating task exceptions to the caller.
   - Calls update_response_result(response, result) to add a JSON-safe 'result' and 'traceback' on failure.
   - If backend_configured(result) is True, adds response.update(state=result.state).
   - Returns the updated response mapping back to the awaiting post() method.

Destruction / cleanup:
- No explicit cleanup required by TaskApply.
- Any blocking/waiting occurs in a thread worker; ensure that the Tornado process allows thread workers to finish on shutdown or implement application-level graceful shutdown if necessary.

Sequencing constraints and recommended usage:
- normalize_options must be called before apply_async if options contain scheduling fields that must be Python-native types (datetime/float).
- wait_results is designed to run in a thread executor (not on the event loop) because result.get is blocking.
- Do not call wait_results on the IOLoop thread directly; always dispatch to run_in_executor or similar.

Concurrency considerations:
- Multiple concurrent requests create separate handler instances; shared objects accessed (self.capp, Celery backends) must be thread-safe as apply_async and result.get may be called from executor threads.

## Method Map:
(Flowchart showing method dependencies and typical invocation order)

graph LR
  A[post(taskname) - Tornado async handler] --> B[get_task_args()]
  B --> C[lookup task in self.capp.tasks]
  C --> D[normalize_options(options)]
  D --> E[task.apply_async(...)] 
  E --> F[build response {'task-id': ...}]
  F --> G[run_in_executor(self.wait_results, result, response)]
  G --> H[wait_results(result, response) - runs in thread]
  H --> I[result.get(propagate=False)]
  I --> J[update_response_result(response, result)]
  J --> K[if backend_configured(result) -> response.update(state)]
  K --> L[return response -> awaited by post]
  L --> M[self.write(response) -> HTTP response sent]

## Raises:
Exceptions raised directly by TaskApply.post and their trigger conditions:
- tornado.web.HTTPError(404, "...")
  - Trigger: taskname not found in self.capp.tasks (KeyError on lookup). The message identifies the unknown task: "Unknown task '<taskname>'".
- tornado.web.HTTPError(400, "Invalid option")
  - Trigger: BaseTaskHandler.normalize_options(options) raises ValueError (invalid type/format for scheduling-related options).
- tornado.web.HTTPError(400, <message>)
  - Trigger: BaseTaskHandler.get_task_args() may raise HTTPError(400, ...) for invalid JSON, non-object top-level payload, or invalid args type. Those HTTPErrors propagate from get_task_args into post and will produce corresponding 400 responses.

Other runtime exceptions (not transformed into HTTPError by this code):
- If result or returned objects lack expected attributes (task_id, get, state, backend, result, traceback), AttributeError or other exceptions may occur during wait_results; the code does not catch these. These are considered programming errors or misconfigured backends.
- Exceptions raised within update_response_result or backend_configured will propagate up through the executor and will manifest as a failed Future; post awaiting the future will raise a corresponding exception unless translated by higher-level error handlers.

## Example:
Request (HTTP POST to /api/task/<taskname> with authentication and JSON body):
- JSON request body:
  {
    "args": [42, "foo"],
    "kwargs": {"bar": "baz"},
    "countdown": "5"
  }

Behavior summary:
- get_task_args() -> (args=[42,"foo"], kwargs={"bar":"baz"}, options={"countdown":"5"})
- normalize_options(options) -> options becomes {"countdown": 5.0}
- task.apply_async(args=args, kwargs=kwargs, countdown=5.0) returns result with task_id "abc-123"
- Server waits in a thread until the task completes, then populates the response with result/state/traceback as appropriate.

Possible JSON responses:
- When a backend is configured and the task succeeded:
  {
    "task-id": "abc-123",
    "result": 123,              (JSON-safe representation of return value)
    "state": "SUCCESS"
  }

- When the backend is configured and the task failed:
  {
    "task-id": "abc-123",
    "result": "ValueError('x')",  (JSON-safe representation produced by safe_result)
    "traceback": "Traceback (most recent call last) ...",
    "state": "FAILURE"
  }

- When the result backend is not configured (DisabledBackend):
  {
    "task-id": "abc-123",
    "result": 123
    (no "state" present because backend_configured(result) == False)
  }

Notes:
- The handler enforces authentication via Tornado's @web.authenticated decorator.
- The response always includes 'task-id'; additional fields depend on the backend and task outcome.
- Because wait_results uses result.get(propagate=False), task exceptions are not raised into the thread; instead the result object reflects the failure state and update_response_result will include traceback when appropriate.

### `flower.api.tasks.TaskApply.post` · *method*

## Summary:
Handle an authenticated HTTP POST to enqueue a named Celery task, wait (off the Tornado I/O loop) for its completion via wait_results, and write a JSON-serializable response containing at minimum the Celery task id.

## Description:
This asynchronous Tornado request handler method is executed when an authenticated POST request is routed to TaskApply with a path parameter taskname (the method is decorated with web.authenticated). The method performs these steps in sequence as implemented in the source:

1. Parse invocation parameters by calling self.get_task_args(), assigning the returned values to args, kwargs, and options (code: args, kwargs, options = self.get_task_args()).
2. Log the invocation using logger.debug with taskname, args, and kwargs (code: logger.debug(...)).
3. Look up the task object in the Celery app registry via self.capp.tasks[taskname] (code: task = self.capp.tasks[taskname]). If the key is missing, the KeyError is caught and translated to HTTPError(404, f"Unknown task '{taskname}'") (code: except KeyError ... raise HTTPError(404, ...)).
4. Validate options by calling self.normalize_options(options). If normalize_options raises ValueError, it is caught and translated to HTTPError(400, 'Invalid option') (code: except ValueError ... raise HTTPError(400, ...)).
5. Submit the task with task.apply_async(args=args, kwargs=kwargs, **options) and capture the returned result object (code: result = task.apply_async(...)).
6. Create a response dict with the task id: response = {'task-id': result.task_id} (code: response = {'task-id': result.task_id}).
7. Offload blocking result handling by awaiting IOLoop.current().run_in_executor(None, self.wait_results, result, response). The awaited call invokes self.wait_results(result, response) in a thread and returns its returned response mapping (code: response = await IOLoop.current().run_in_executor(None, self.wait_results, result, response)).
8. Write the final response mapping to the HTTP client using self.write(response) (code: self.write(response)).

Why this is a separate method:
- It implements the POST endpoint for task invocation and contains the request parsing, error mapping to HTTP status codes, task submission, and safe blocking wait via run_in_executor. The blocking work is explicitly moved off the I/O loop.

## Args:
    taskname (str): The Celery task name to invoke. Must be a key in self.capp.tasks; otherwise the method raises HTTPError(404, "Unknown task '<taskname>'").

## Returns:
    None
    - The method does not return a Python value; it sends the HTTP response by calling self.write(response).
    - The response written is a mapping. Immediately after submission it contains:
        * 'task-id' (str): result.task_id
      The mapping returned from wait_results (and written) may include additional keys as provided by wait_results (see wait_results behavior below).

## Raises:
    tornado.web.HTTPError(404)
        - Trigger: self.capp.tasks[taskname] raises KeyError (task not found). Message: "Unknown task '<taskname>'".
    tornado.web.HTTPError(400)
        - Trigger: self.normalize_options(options) raises ValueError. Message: "Invalid option".
    Any exception raised by task.apply_async
        - These are not caught and will propagate.
    Exceptions raised inside wait_results
        - wait_results is executed inside run_in_executor; such exceptions will propagate when awaiting run_in_executor and are not caught by this method.

## wait_results behavior (as implemented in the same class):
    - Calls result.get(propagate=False) (blocking).
    - Calls self.update_response_result(response, result).
    - If self.backend_configured(result) returns True, it calls response.update(state=result.state).
    - Returns the (possibly augmented) response dict.

## State Changes:
Attributes READ:
    - self.capp (accessed to resolve the task via self.capp.tasks[taskname]).
    - Methods called on self (observable from code): get_task_args(), normalize_options(options), wait_results(result, response), update_response_result(response, result), backend_configured(result).
    - Module-level logger via logger.debug (reads provided values; no object state mutation).

Attributes WRITTEN:
    - No self.<attribute> fields are directly assigned in this method.
    - The local response dict is mutated (initial assignment and then potentially mutated by wait_results), and that dict is passed to self.write(response).

## Constraints:
Preconditions:
    - get_task_args() must return an iterable unpackable into three values: args, kwargs, options (as the source performs tuple unpacking).
    - args should be suitable as positional arguments for the task; kwargs should be a mapping suitable for keyword arguments; options should be a mapping acceptable to both normalize_options and Celery's apply_async.
    - self.capp must provide a tasks mapping where self.capp.tasks[taskname] yields an object with apply_async(...) returning a result object that exposes .task_id and .get(...) (e.g., celery.result.AsyncResult or compatible).

Postconditions:
    - On success, self.write(response) has been called with a mapping containing at least {'task-id': <task id>} and possibly augmented fields returned by wait_results.
    - On failure due to unknown task or invalid options, an HTTPError is raised and no successful response is written by this method.

## Side Effects:
    - Calls task.apply_async(...): submits/enqueues the task to the configured Celery broker (I/O external to this process).
    - Calls logger.debug(...): emits a debug log record.
    - Offloads blocking wait to a thread via IOLoop.current().run_in_executor(None, ...).
    - wait_results calls result.get(propagate=False) (blocking and may access the result backend), update_response_result, and may read result.state.
    - Calls self.write(response): sends the HTTP response to the client.

Notes:
    - The method translates exactly two error conditions into HTTPError with specific status/message as shown in the source (KeyError -> 404 "Unknown task '<taskname>'"; ValueError from normalize_options -> 400 "Invalid option"). All other exceptions propagate.
    - If callers require non-blocking (fire-and-forget) behavior, they must avoid awaiting run_in_executor and return immediately after apply_async.

### `flower.api.tasks.TaskApply.wait_results` · *method*

## Summary:
Blocks the current thread until the given Celery result is ready, mutates the provided response mapping with result details, conditionally adds the task state when a result backend is available, and returns the same response mapping.

## Description:
Known callers and lifecycle context:
- Called from TaskApply.post immediately after enqueuing a task with apply_async. TaskApply.post submits this method to a threadpool via IOLoop.current().run_in_executor(...) so the Tornado event loop is not blocked.
- This method represents the synchronous wait-and-collect step in the request lifecycle: wait for the remote task to finish, collect its outcome into the HTTP response payload, and return that payload to the caller.

Why this is a separate method:
- Encapsulates blocking behavior so callers can offload it to an executor (preventing event-loop blockage).
- Groups response-mutation logic (update_response_result) and conditional inclusion of task state (backend_configured) in a single, testable unit.

## Args:
    result (celery.result.AsyncResult | celery.contrib.abortable.AbortableAsyncResult):
        A Celery result object returned by apply_async. Required capabilities:
            - a get(...) method callable as get(propagate=False) that blocks until the task completes,
            - a .state attribute that holds the task state (e.g., 'SUCCESS', 'FAILURE').
        The value is typically the AsyncResult-like object returned by task.apply_async(...).

    response (dict):
        A mutable mapping (normally a dict) which already contains at least the 'task-id' key (set by the caller). This mapping will be mutated in place to include result details.

## Returns:
    dict: The same response mapping instance that was passed in, after mutation. After a successful call the mapping will:
        - preserve existing keys (e.g., 'task-id'),
        - include additional keys/values added by self.update_response_result(response, result),
        - include the 'state' key with value result.state if self.backend_configured(result) returns True.

Edge cases:
- If an exception is raised before any mutation completes, no guarantees are made about the mapping's contents; partial mutation is possible if an error occurs after update_response_result returns.

## Raises:
    Any exception raised by the following will propagate to the caller:
        - result.get(propagate=False): any exception this call raises (timeouts, backend errors, or other runtime exceptions from the result backend).
        - self.update_response_result(response, result): any exception raised by this helper.
        - self.backend_configured(result): any exception raised by this helper.
Note: this method does not catch or transform exceptions; callers are responsible for handling failures.

## State Changes:
Attributes READ:
    - result.get(...) (calls the result's get method)
    - result.state (reads the result.state attribute when backend configured)
    - No direct reads of self.<attr> are present in this method body; helper methods may read handler state.

Attributes WRITTEN:
    - response (the passed-in mapping) is mutated in place by:
        - self.update_response_result(response, result) — augments response with result details.
        - response.update(state=result.state) — conditionally writes/overwrites the 'state' key when a backend is configured.
    - This method does not assign to any self.<attr> directly; helper methods may modify handler state.

## Constraints:
Preconditions:
    - result must be an AsyncResult-like object with working get(propagate=False) and .state.
    - response must be a mutable mapping (dict-like).
    - Because result.get blocks the current thread, callers must invoke wait_results off the Tornado I/O loop (for example via run_in_executor) to avoid blocking the event loop.

Postconditions:
    - On normal completion, response contains result details (via update_response_result) and, if backend_configured(result) is True, response['state'] == result.state.
    - The method returns the same response object passed in.

## Side Effects:
    - Blocks the current thread until the task completes by calling result.get(propagate=False).
    - Mutates the provided response mapping in place.
    - Invokes two helper methods on self: update_response_result(response, result) and backend_configured(result). Those helpers may perform additional I/O, logging, or state inspection/modification (not specified here).
    - No network I/O or HTTP write is performed by this method itself; the HTTP response is written by the caller after this method returns.

## `flower.api.tasks.TaskAsyncApply` · *class*

## Summary:
Schedules the named Celery task asynchronously using arguments and options parsed from the incoming HTTP POST request, then writes a JSON response containing the created task id and (when available) the task state.

## Description:
This Tornado request handler method (POST) is used when a client requests that the server start a background Celery task by name. It is executed for an authenticated HTTP POST routed to this handler with a path parameter taskname.

Typical invocation scenario:
- Tornado creates an instance of the handler for a request and dispatches this post(self, taskname) method when a POST arrives at the configured route (taskname is captured from the URL).
- The method delegates JSON parsing and basic validation to BaseTaskHandler.get_task_args(), normalizes scheduling-related options via BaseTaskHandler.normalize_options(), looks up the task in the Celery application (self.capp.tasks), schedules it with task.apply_async(...), and writes a JSON HTTP response.

Responsibility boundary:
- This method is explicitly responsible for orchestrating request-level operations: parse → validate/normalize → schedule → respond.
- It intentionally delegates parsing, normalization, and backend availability checks to BaseTaskHandler helpers so those concerns remain testable and separate from HTTP plumbing.

Known callers / factories:
- Tornado's routing and request dispatch are the caller/factory; the handler is not directly instantiated by application code but by Tornado for each matching request.

## State:
Attributes read or required by this handler method (must be present on the handler instance):
- self.capp (Celery application-like object)
  - Type: mapping-like Celery app object exposing .tasks (dict-like)
  - Invariants: self.capp.tasks must support lookup by task name string
- self.request (Tornado HTTPRequest)
  - Used indirectly by get_task_args() to read the body
- self.get_task_args (callable)
  - Signature (no args) -> (args, kwargs, options)
  - Contract: returns a 3-tuple where args is list/tuple, kwargs is the kwargs value or {}, options is a dict
- self.normalize_options (callable)
  - Signature: normalize_options(options: dict) -> None
  - Contract: mutates options to convert scheduling option types (eta/countdown/expires) or raises ValueError on invalid values
- self.backend_configured (callable)
  - Signature: backend_configured(result) -> bool
  - Contract: return True when result.backend is usable (not DisabledBackend)
- self.write (callable)
  - Signature: write(obj) -> None
  - Contract: writes a JSON-serializable response to the HTTP client (BaseTaskHandler provided)
- logger (module-level logger)
  - Used for debug logging

Notes on __init__ parameters and defaults:
- The handler class itself has no explicit __init__ shown here — Tornado constructs handlers with the usual (application, request) signature. There are no additional initialization parameters required by this method beyond the standard Tornado handler construction and a configured self.capp attribute.

Class invariants:
- For every request handled by post():
  - self.capp is present and self.capp.tasks supports taskname lookup
  - get_task_args() returns a valid (args, kwargs, options) triple
  - normalize_options(options) will either succeed or raise ValueError (which post converts to HTTP 400)

## Lifecycle:
Creation:
- Instantiated by Tornado per incoming request. No explicit factory method required.

Usage (typical sequence when handling a POST request targeting a task):
1. Authentication enforcement (decorator @web.authenticated): Tornado ensures the request is authenticated before calling post().
2. Call self.get_task_args() to parse request body and extract (args, kwargs, options).
3. Log debug information via logger.debug.
4. Lookup the task with task = self.capp.tasks[taskname].
   - If KeyError: raise HTTPError(404, f"Unknown task '{taskname}'").
5. Call self.normalize_options(options).
   - If ValueError: raise HTTPError(400, "Invalid option").
6. Call result = task.apply_async(args=args, kwargs=kwargs, **options) to enqueue the task.
7. Build response = {'task-id': result.task_id}.
8. If self.backend_configured(result) returns True, add response['state'] = result.state.
9. Call self.write(response) to send the JSON response to the client.

Sequencing requirements:
- get_task_args must be called before any scheduling to obtain arguments and scheduling options.
- normalize_options must be called before passing options to apply_async.
- backend_configured must be checked after obtaining the result and before accessing result.state.

Destruction / cleanup:
- No explicit cleanup or resource release is required by this handler method. Tornado will tear down the handler instance after the request lifecycle completes.

## Method Map:
Mermaid flowchart showing the call order and dependencies when post() executes:

flowchart LR
    A[POST entry (@web.authenticated)] --> B[get_task_args()]
    B --> C[log debug]
    C --> D[lookup task = self.capp.tasks[taskname]]
    D -->|KeyError| E[raise HTTPError 404]
    D --> F[normalize_options(options)]
    F -->|ValueError| G[raise HTTPError 400]
    F --> H[result = task.apply_async(...)]
    H --> I[response = {'task-id': result.task_id}]
    I --> J[if backend_configured(result): response['state'] = result.state]
    J --> K[self.write(response)]

## Raises:
Explicit exceptions converted within this method:
- tornado.web.HTTPError(404, "Unknown task '<taskname>'")
  - Trigger: self.capp.tasks[taskname] raises KeyError
- tornado.web.HTTPError(400, "Invalid option")
  - Trigger: self.normalize_options(options) raises ValueError

Errors propagated (not caught here; will bubble to Tornado/error middleware):
- Any exceptions from self.get_task_args() (e.g., HTTPError(400) for malformed JSON) propagate.
- Any exceptions from task.apply_async(...) propagate (e.g., broker or task-related errors).
- Any exceptions thrown while accessing result.task_id or result.state (rare) will propagate unless backend_configured() prevented the access.

Notes about backend checks:
- The method only adds result.state to the response when backend_configured(result) is True. backend_configured relies on the presence/absence of a configured result backend (DisabledBackend detection).

## Example:
1) Example HTTP request body (JSON) a client might POST to the route:
{
  "args": [1, 2],
  "kwargs": {"verbose": true},
  "countdown": "10"
}
- get_task_args() will return args=[1,2], kwargs={"verbose": true}, options={"countdown": "10"}.
- normalize_options(options) should convert "countdown" to a float (10.0).
- The handler will schedule the task and reply with JSON such as:
  {"task-id": "e3b0c442-..."}  or, if a result backend is present:
  {"task-id": "e3b0c442-...", "state": "PENDING"}

2) Typical high-level pseudo-sequence:
- Client: POST /api/tasks/<taskname> with JSON body as above and authentication credentials.
- Tornado: constructs handler, authenticates, calls TaskAsyncApply.post(taskname).
- Handler: parse → normalize → schedule → write JSON response.

### `flower.api.tasks.TaskAsyncApply.post` · *method*

## Summary:
Schedules the specified Celery task asynchronously using request-provided arguments and options, then writes a JSON HTTP response containing the created task id and (when available) the task state.

## Description:
This is the Tornado HTTP POST handler invoked for authenticated requests that target the TaskAsyncApply route with a task name parameter. It runs during the API request handling stage when a client asks the server to start a background task.

The handler performs three coordinated steps so that HTTP concerns remain separate from argument parsing and option normalization:
1. Extracts call arguments and scheduling options from the incoming request via self.get_task_args().
2. Validates/normalizes those scheduling options via self.normalize_options(options).
3. Looks up the named task on the Celery app (self.capp.tasks[taskname]) and calls task.apply_async(...) to enqueue the job.

These responsibilities are separated into helpers so parsing/validation logic and backend-detection logic can be unit-tested independently of HTTP plumbing.

## Args:
    taskname (str): The task name/key from the URL/route. Must be present in self.capp.tasks; otherwise a 404 HTTPError is raised.

## Returns:
    None
    - The method does not return a Python value. Instead it writes an HTTP JSON response via self.write().
    - Response body (JSON):
        - Always included: "task-id" (str) — the identifier returned by the result object (result.task_id).
        - Conditionally included: "state" (str) — the current task state (result.state), included only if self.backend_configured(result) returns True.

## Raises:
    tornado.web.HTTPError(404)
        - Condition: self.capp.tasks does not contain taskname (KeyError during lookup).
        - Message: "Unknown task '<taskname>'" (constructed with taskname).
    tornado.web.HTTPError(400)
        - Condition: self.normalize_options(options) raises ValueError.
        - Message: "Invalid option"
    Any exception raised by:
        - self.get_task_args(): parsing or argument extraction errors propagate unchanged.
        - task.apply_async(...): errors scheduling the task (broker misconfiguration, invalid options, etc) propagate unchanged.
    Note: Only the two specific exceptions above are caught and converted to HTTPError in this method; other errors will bubble up.

## State Changes:
Attributes READ:
    - self.capp: accessed to read self.capp.tasks for task lookup.
    - self.capp.tasks: mapping-like container used to find the task by name.
    - self.get_task_args (method): called to obtain (args, kwargs, options).
    - self.normalize_options (method): called to validate/normalize options.
    - self.backend_configured (method): called to determine whether to include result.state in the response.
    - self.write (method): used to send the JSON response to the HTTP client.
Attributes WRITTEN:
    - None. The handler does not assign or mutate self.<attr> fields.

## Constraints:
Preconditions:
    - self.capp must be set to a Celery application-like object exposing a tasks mapping (self.capp.tasks[taskname] must be a valid lookup).
    - self.get_task_args() must return a 3-tuple: (args, kwargs, options) where:
        - args: sequence (list or tuple) of positional arguments,
        - kwargs: dict of keyword arguments,
        - options: dict of keyword options meant for task.apply_async and for normalize_options.
    - self.normalize_options must accept the options dict for valid inputs; invalid options should raise ValueError.
    - The caller must be authenticated (the method is decorated with @web.authenticated); Tornado enforces authentication before entering this method.

Postconditions:
    - If no exception is raised:
        - A Celery task has been scheduled by calling task.apply_async(args=args, kwargs=kwargs, **options).
        - An HTTP response has been written containing at least {"task-id": "<id>"}.
        - If backend_configured(result) returns True, the response includes "state": result.state.
    - If a KeyError or ValueError occurred in the recognized places, the request ends with the corresponding HTTPError status and message.

## Side Effects:
    - Logs a debug message via logger.debug indicating the invoked taskname and provided args/kwargs.
    - Calls task.apply_async(...) which enqueues the job on the broker — this is network I/O and schedules asynchronous work.
    - Potentially queries the result backend by accessing result.state when backend_configured(result) is True — this may perform network I/O.
    - Writes JSON to the HTTP response stream via self.write(), producing network I/O.
    - Does not mutate handler instance attributes.

## `flower.api.tasks.TaskSend` · *class*

## Summary:
Handles POST requests to enqueue/dispatch a Celery task by name; parses task arguments from the request, sends the task via the configured Celery application, and returns a minimal JSON response containing the submitted task id and (optionally) the task state when a result backend is available.

## Description:
This Tornado request handler endpoint implements the HTTP POST action for creating/sending a Celery task identified by the URL parameter taskname.

Typical usage scenarios:
- An authenticated HTTP client posts a JSON payload describing positional arguments, keyword arguments, and task sending options (e.g., routing or task-specific options). The server enqueues the task and returns the task id to the client.
- Used in APIs that expose Celery task execution to remote callers (e.g., web UI, REST API).

Known callers / creation:
- Tornado maps this handler.method (post) to a URL pattern that supplies taskname as a path parameter. The method is decorated with @web.authenticated, so Tornado's authentication mechanism must authenticate the request before execution.

Responsibility boundary:
- TaskSend is responsible only for parsing request arguments (delegated to BaseTaskHandler.get_task_args), invoking self.capp.send_task to dispatch the task, and returning a concise response.
- It does not inspect task results beyond optionally reporting the immediate task state if a result backend is configured (via BaseTaskHandler.backend_configured).
- It delegates validation of request JSON structure and error reporting for malformed input to BaseTaskHandler.get_task_args.

## State:
Attributes accessed/read by this component (inferred from code and BaseTaskHandler behavior):
- self.request.body (read indirectly via BaseTaskHandler.get_task_args)
  - Type: bytes or str (as provided by Tornado)
  - Semantics: contains the raw JSON payload describing args/kwargs/options; when empty, get_task_args treats it as {}.
- self.capp
  - Type: Celery application-like object exposing send_task(...) method
  - Required behavior: send_task(taskname, args=list/tuple, kwargs=any, **options) -> result-like object exposing .task_id and .state; typically returns celery.result.AsyncResult or celery.contrib.abortable.AbortableAsyncResult.
  - Constraint: must be set on the handler instance before post is called (provided by the application setup).
- logger (module-level logging object; used for debug logging)
  - Used for informational/debug logging only; absence of logger will raise NameError at runtime, so module must provide logger.

Return / response state:
- The handler writes a response dictionary containing:
  - 'task-id': string (the value of result.task_id)
  - optionally 'state': string (the value of result.state), present only when BaseTaskHandler.backend_configured(result) returns True.

Class invariants / expected assumptions:
- self.capp is a valid Celery app or compatible object when post() executes.
- BaseTaskHandler.get_task_args returns (args, kwargs, options) where args is list/tuple and options is dict (see BaseTaskHandler doc).
- The result object returned by self.capp.send_task exposes .task_id and .state attributes (typical for AsyncResult/AbortableAsyncResult).

## Lifecycle:
Creation:
- Instantiated by Tornado's request handler factory when a matching URL is invoked. No explicit constructor-specific arguments are required here beyond what Tornado RequestHandler normally requires.
- Before calling post, the application must ensure handler instance has attribute .capp referencing a Celery app.

Usage (typical sequence inside a single request):
1. Authentication: Tornado's @web.authenticated runs before post; the request must be authenticated.
2. Parsing: post calls self.get_task_args() (inherited from BaseTaskHandler) which:
   - Reads and decodes JSON from self.request.body,
   - Returns (args, kwargs, options) where args is validated to be a list/tuple and options is a dict.
   - May raise HTTPError(400, ...) on malformed input.
3. Logging: post logs a debug message with the task name and parsed args/kwargs.
4. Dispatch: post calls self.capp.send_task(taskname, args=args, kwargs=kwargs, **options) to enqueue/dispatch the task. This returns a result-like object.
5. Response: Constructs response = {'task-id': result.task_id}. If backend_configured(result) returns True, response['state'] = result.state. Writes the response via self.write(response) and returns to Tornado's request loop.

Destruction / cleanup:
- No explicit cleanup required. The handler relies on Tornado's lifecycle; no context manager, close(), or teardown calls are required by TaskSend itself.

Sequencing rules:
- get_task_args must succeed before send_task is invoked.
- backend_configured(result) is a safe-read check that should be called only after obtaining the result object.

## Method Map:
graph TD
    A[HTTP POST request arrives] --> B[@web.authenticated check]
    B --> C[get_task_args() parses JSON -> (args, kwargs, options)]
    C --> D[logger.debug(...) logs invocation]
    D --> E[self.capp.send_task(taskname, args, kwargs, **options)]
    E --> F[result returned (AsyncResult-like)]
    F --> G[backend_configured(result) ?]
    G -->|True| H[Include result.state in response]
    G -->|False| I[Do not include state]
    H --> J[self.write(response)]
    I --> J[self.write(response)]
    J --> K[HTTP response sent]

## Raises:
Exceptions that can be raised directly or transitively during post():
- tornado.web.HTTPError(400, message)
  - Source: BaseTaskHandler.get_task_args raises this on malformed JSON, non-object top-level JSON, or non-array 'args'. This results in a 400 Bad Request response returned to the client.
- AttributeError / NameError
  - Trigger: If self.capp or logger is not present on the handler instance or if result lacks expected attributes, attribute access may raise AttributeError or NameError. These are uncaught in post().
- Any exception raised by self.capp.send_task(...)
  - Trigger: Invalid task name, broker connectivity issues, or Celery internals may raise exceptions when attempting to send the task. Those exceptions are not caught here and will propagate according to Tornado's error handling configuration.

Notes on backend_configured:
- backend_configured(result) may raise AttributeError if the returned result object does not expose a .backend attribute; BaseTaskHandler.backend_configured documents that behavior.

## Example:
Below is an example HTTP interaction (curl) demonstrating a typical request and response. The handler expects an authenticated request (illustrative Authorization header included).

Request:
curl -X POST "https://example.com/api/tasks/send/myapp.tasks.add" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"args": [2, 3], "kwargs": {}, "queue": "hipri"}'

Possible successful response (JSON):
{"task-id":"c0ffee12-3456-7890-abcd-1234567890ab", "state":"PENDING"}

Notes:
- If the application has no configured result backend, the response will omit the "state" key:
  {"task-id":"c0ffee12-3456-7890-abcd-1234567890ab"}
- If the request body is invalid JSON or violates the expected structure (e.g., args is not an array), the handler will respond with HTTP 400 and an explanatory message produced by BaseTaskHandler.get_task_args.

### `flower.api.tasks.TaskSend.post` · *method*

## Summary:
Enqueues a Celery task using the request-provided arguments and writes a JSON HTTP response containing the enqueued task id and, when available, the task state.

## Description:
This Tornado POST handler parses task invocation parameters from the incoming HTTP request, invokes the Celery application (self.capp) to send the task identified by taskname, and returns immediate JSON feedback to the HTTP client.

Known callers / invocation context:
- Invoked by Tornado's request-dispatching when an authenticated HTTP POST maps to TaskSend.post (the method is decorated with @web.authenticated).
- Runs during the API request handling stage: HTTP request → handler.post → enqueue task → respond.

Why this logic is its own method:
- Implements a single HTTP endpoint workflow (parse request, call Celery, format response). Keeping it here isolates endpoint behavior and leverages Tornado's handler lifecycle (authentication, request context, response writing).

## Args:
    taskname (str):
        - The identifier/name of the Celery task to enqueue (for example a fully-qualified Python path or a registered task name).
        - The method does not validate the task name beyond passing it to self.capp.send_task; callers should provide a valid task identifier for the Celery app in use.

## Returns:
    None
    - The handler does not return a Python value. Instead it writes an HTTP JSON response via self.write().
    - Response shape:
        * Always includes: {'task-id': <task_id_string>}
        * May include: {'state': <state_string>} if self.backend_configured(result) evaluates to True.
    - Example response body:
        {'task-id': 'f3a1b8d4-...','state': 'PENDING'}

## Raises:
    - Propagates exceptions raised by:
        * self.get_task_args() — e.g., request parsing or validation errors.
        * self.capp.send_task(...) — e.g., Celery/broker connection errors, misconfiguration.
        * Accessing result.task_id or result.state — if the Celery API returns an unexpected object.
        * self.write(...) — I/O errors while writing the HTTP response.
    - Any such exception will bubble up to Tornado's error handlers and may result in an HTTP error response if not caught higher in the call stack.

## State Changes:
Attributes READ:
    - self.get_task_args (method): called to obtain a 3-tuple (args, kwargs, options).
    - self.capp (attribute): the Celery application instance used to call send_task.
    - self.backend_configured (method): used to decide whether to include result.state in the response.
    - module-level logger (logger): used for a debug log entry.

Attributes WRITTEN:
    - None of the TaskSend instance attributes are modified by this method.

## Constraints:
Preconditions:
    - Must be called within a Tornado request handler context and after authentication (the method is decorated with @web.authenticated).
    - self.get_task_args() must return a tuple of (args, kwargs, options):
        * args: an iterable (typically list/tuple) of positional arguments for the task.
        * kwargs: a mapping (dict) of keyword arguments for the task.
        * options: a mapping of keyword options forwarded to self.capp.send_task (e.g., routing/queue options).
    - self.capp must be a configured Celery application instance with a working send_task(...) implementation.

Postconditions:
    - A send_task call has been made to the Celery app with the provided taskname, args, kwargs, and options.
    - A JSON response containing at least the enqueued task id has been written to the HTTP response stream; if the backend is configured, the response also contains the task state.

## Side Effects:
    - Sends a message to the Celery broker via self.capp.send_task(...), which enqueues work for workers (network/IPC).
    - Writes an HTTP response to the client using self.write(...).
    - Emits a debug log entry describing the invoked task and supplied arguments.
    - May propagate exceptions originating from argument parsing, Celery/broker interactions, or response writing.

## `flower.api.tasks.TaskResult` · *class*

## Summary:
A Tornado HTTP request handler that returns the current state and, when available or requested, the result of a Celery task identified by its task id.

## Description:
This handler implements the GET endpoint for querying the status and result of a Celery task. It is intended to be mounted into a Tornado application (as a subclass of a framework-specific BaseTaskHandler) and called in response to an authenticated HTTP GET request whose URL contains a task id.

On each GET, the handler:
- Builds a celery.result.AsyncResult from the provided task id.
- Verifies that a result backend is configured using self.backend_configured(result). If the backend is not configured, it responds with HTTP 503 (Service Unavailable) by raising tornado.web.HTTPError(503).
- Returns a JSON-able dict with at least the keys 'task-id' and 'state'.
- Optionally waits up to a caller-specified timeout (seconds) for the task result and augments the response with result details by calling self.update_response_result(response, result).
- If no timeout is given but the task is already ready (result.ready() is True), it augments the response immediately.

Known callers / instantiation:
- Tornado will instantiate and call the handler when the appropriate route is invoked; this class is intended to be used inside the Flower web service or similar Tornado-based APIs.
- The handler is decorated with @web.authenticated, so Tornado's authentication machinery is expected to be configured and will gate access.

Motivation and responsibility boundary:
- This class isolates the HTTP-facing logic required to fetch task state/result from Celery and delegates backend-configuration checks and response formatting to methods provided by its BaseTaskHandler superclass. It does not itself implement backend probing or response formatting beyond the minimal structure it sets.

## State:
This class does not declare its own instance attributes in the provided source. It relies on inherited state and Tornado RequestHandler methods. Relevant implicit state and external objects used during execution:
- result (local variable): celery.result.AsyncResult created per request for the given task id.
- response (local variable): dict that will be sent to the client (JSON-serializable).

Inherited dependency contracts (must be provided by BaseTaskHandler or other mixins):
- backend_configured(result) -> bool
    - Purpose: check whether a Celery result backend is configured/available for the given AsyncResult.
    - TaskResult behavior: If this returns False, TaskResult raises HTTPError(503).
    - Implementer note: a typical implementation checks that result.backend is not DisabledBackend and/or that backend has been properly configured.
- update_response_result(response: dict, result: AsyncResult) -> None
    - Purpose: mutate and enrich the response dict with details from the AsyncResult (e.g., 'result' value, 'traceback', 'date_done' or other metadata).
    - TaskResult behavior: called when the task result has been retrieved or the caller requested to wait; TaskResult does not inspect or rely on the exact keys update_response_result adds — only that it augments the response in-place.

## Lifecycle:
Creation:
- Tornado creates handler instances; there is no public __init__ to call directly in this class.

Usage (typical request flow and sequencing):
1. A GET request arrives bound to this handler with path parameter taskid and optional query param timeout.
2. Tornado enforces authentication (the handler is annotated with @web.authenticated). If unauthenticated, Tornado's auth flow will reject before entering get().
3. The method get(self, taskid) executes:
   - Reads the 'timeout' query parameter via self.get_argument('timeout', None). If provided, attempts to convert it to float.
   - Constructs result = AsyncResult(taskid).
   - Calls self.backend_configured(result). If False => raise HTTPError(503).
   - Prepares response = {'task-id': taskid, 'state': result.state}.
   - If timeout is not None (a numeric float):
       - Calls result.get(timeout=timeout, propagate=False). This blocks up to timeout seconds waiting for the task to finish or raises a timeout exception.
       - After get() returns successfully, calls self.update_response_result(response, result).
   - Else if result.ready() is True:
       - Calls self.update_response_result(response, result).
   - Calls self.write(response) to send the response to the client (Tornado will serialize the dict to JSON if appropriate).
4. The handler does not perform explicit cleanup; Tornado's RequestHandler lifecycle handles instance destruction.

Destruction:
- No special cleanup (no close or context-manager behavior needed).

Important sequencing requirements:
- backend_configured(result) must be called before any attempt to access result data or wait on it.
- update_response_result(response, result) should only be invoked after result.get() has returned (if waiting) or if result.ready() is True.

## Method Map:
graph LR
    A[GET request arrives] --> B[get(self, taskid)]
    B --> C[get 'timeout' query param]
    C --> D[AsyncResult(taskid)]
    D --> E[backend_configured(result)?]
    E -- False --> F[raise HTTPError(503)]
    E -- True --> G[response={'task-id','state'}]
    G --> H{timeout provided?}
    H -- Yes --> I[result.get(timeout=..., propagate=False)]
    I --> J[update_response_result(response, result)]
    H -- No --> K{result.ready()?}
    K -- True --> J
    K -- False --> L[self.write(response)]
    J --> L[self.write(response)]

## Raises:
These exceptions can propagate from the handler as written:
- tornado.web.HTTPError(503)
    - Trigger: self.backend_configured(result) returned False. The handler raises this to indicate the task result backend is not available.
- ValueError
    - Trigger: if the 'timeout' query parameter is present but cannot be converted to float by float(timeout_string). The handler does no try/except around this conversion.
- celery.exceptions.TimeoutError (or the Celery timeout exception type)
    - Trigger: when result.get(timeout=timeout, propagate=False) does not complete within the given timeout. This is raised by Celery's result.get.
- Other exceptions coming from AsyncResult or underlying Celery backends may propagate (e.g., connection errors). The handler does not catch these explicitly.

Implementation notes and constraints:
- The handler relies on Tornado's RequestHandler methods:
    - self.get_argument(name, default) to read query parameters.
    - @web.authenticated to enforce authentication.
    - self.write(response) to send JSON-serializable payloads.
- The handler uses celery.result.AsyncResult(taskid) to access Celery task state and result.
- Because result.get is called with propagate=False, task exceptions (exceptions raised inside the task) will not be re-raised by get(); update_response_result is expected to inspect result (e.g., result.result, result.traceback) to include task failure details if present.

## Example:
Below is a conceptual example of an HTTP request and the handler behavior. (The exact route URL depends on how the Tornado application registers the handler.)

Request:
- GET /api/task/result/01234567-89ab-cdef-0123-456789abcdef?timeout=5
Behavior:
1. Handler reads timeout = "5" -> float -> 5.0
2. Constructs AsyncResult('01234567-89ab-cdef-0123-456789abcdef')
3. If backend not configured -> raise HTTPError(503)
4. Otherwise response initially {'task-id': '01234567-89ab-cdef-0123-456789abcdef', 'state': '<state>'}
5. Calls result.get(timeout=5.0, propagate=False):
   - If the task completes within 5s, update_response_result adds result details (e.g., 'result', 'traceback', 'date_done') to response.
   - If the get call times out, celery.exceptions.TimeoutError is raised (the handler does not catch it).
6. Handler writes response back to the client (Tornado converts dict to JSON).

Developer guidance to reimplement:
- Provide BaseTaskHandler methods backend_configured(result) and update_response_result(response, result) with the documented contracts.
- Ensure the Tornado app wiring provides authentication so @web.authenticated behaves as expected.
- Validate or sanitize the 'timeout' parameter if you prefer returning a 400 Bad Request for invalid numeric input (the current implementation allows ValueError to propagate).

### `flower.api.tasks.TaskResult.get` · *method*

## Summary:
Return the current state (and, if available or requested, the result) for the Celery task identified by taskid and write that information to the HTTP response; may block up to a client-specified timeout while waiting for the result.

## Description:
This is the HTTP GET handler for task status queries. Typical callers:
- HTTP GET requests routed to the TaskResult endpoint (this method is decorated with @web.authenticated, so it is invoked for authenticated clients of the Flower API/UI).
- Polling clients or UI components that want the current state or final result of a Celery task.

It is its own method because it implements the full request lifecycle for a single endpoint: parse query parameters, fetch the AsyncResult, verify backend availability, optionally block for the task result, format the response, and write it to the HTTP response. Centralizing this logic keeps request parsing, backend checks, blocking semantics, and response formatting in one place rather than inlining these steps in multiple callers.

The method performs the following operations in order (each maps to a single statement or small block in the implementation):
1. Read the optional query parameter 'timeout' via self.get_argument('timeout', None) and convert it to float if present.
2. Construct a Celery AsyncResult for the provided taskid.
3. Verify that a result backend is configured by calling self.backend_configured(result); if not configured, raise an HTTP 503.
4. Create a response dict with keys 'task-id' and 'state' (value taken from result.state).
5. If a truthy timeout value was provided (non-zero float), call result.get(timeout=timeout, propagate=False) which may block up to timeout; after that call, or if result.ready() is already True, call self.update_response_result(response, result) to enrich the response with result details (implementation of update_response_result is expected elsewhere).
6. Write the final response object to the HTTP response using self.write(response).

## Args:
    taskid (str): Path parameter identifying the Celery task whose status is requested. Must be a value accepted by celery.result.AsyncResult (typically a UUID string).

Query parameters:
    timeout (optional, str -> float): When present, read from the request arguments and converted to float. If omitted, or provided as the literal string that converts to 0.0, the handler does not block; only when the converted float is truthy (non-zero) does the handler call result.get(...) to block up to that many seconds.

## Returns:
    None — the method writes the response dictionary to the HTTP response (via Tornado's self.write). The response dictionary always contains:
        - 'task-id': the taskid passed in
        - 'state': the current state of the AsyncResult (result.state)
    If the task is ready or the blocking get() completed, update_response_result(response, result) may add additional keys (for example, result value, traceback, meta). Those additional fields are dependent on the implementation of update_response_result.

## Raises:
    tornado.web.HTTPError(503): Raised immediately if self.backend_configured(result) returns False, indicating no result backend is available.
    Any exception raised by AsyncResult.get(...) (for example, celery.exceptions.TimeoutError when a wait times out or backend errors) will propagate out of this method because it is not caught here.
    Any exception raised by self.update_response_result(...) or self.write(...) will also propagate.

## State Changes:
    Attributes READ:
        - No explicit self.<attribute> fields are read or mutated by this method. (It does, however, call these handler methods: self.get_argument, self.backend_configured, self.update_response_result, and self.write.)
    Attributes WRITTEN:
        - This method does not assign to any self.<attribute> fields. It mutates and writes out a local response dict and sends it to the client via self.write.

## Constraints:
    Preconditions:
        - self must be a Tornado RequestHandler (or subclass) exposing get_argument and write methods.
        - The TaskResult handler (or a base class) must implement:
            * backend_configured(result) -> bool
            * update_response_result(response, result) -> None (or equivalent)
          The method assumes these exist and behave as their names imply.
        - taskid must be a value acceptable to AsyncResult (commonly a non-empty string).
        - If the 'timeout' query parameter is provided it must be parseable by float(); otherwise a ValueError will be raised by float conversion.

    Postconditions:
        - The HTTP response buffer has been written with a dictionary that contains at least 'task-id' and 'state'.
        - If timeout was truthy and result.get completed successfully, or result.ready() was True, update_response_result has been invoked to add result details to the response before write().

## Side Effects:
    - Performs I/O with Celery internals: constructs AsyncResult(taskid) and may call result.get(timeout=..., propagate=False). That get() call can:
        * Block the current request handler thread/coroutine for up to the provided timeout.
        * Perform network/backend I/O to the configured result backend.
        * Raise backend-related exceptions (those will propagate).
    - Calls self.write(response) which writes to the outgoing HTTP response (I/O).
    - Calls self.update_response_result(response, result) which may read from the result and mutate the response dict; the exact mutation behavior depends on that helper's implementation.

## `flower.api.tasks.TaskAbort` · *class*

## Summary:
Represents an HTTP handler that receives POST requests to request aborting a Celery task by its task id. It constructs an AbortableAsyncResult for the given id, verifies the backend is available, invokes abort(), and returns a simple JSON confirmation.

## Description:
This Tornado RequestHandler subclass is intended to be mounted as an HTTP endpoint for aborting long-running Celery tasks. Typical scenarios:
- A web UI or API client wants to request that a running task stop early.
- The handler is hit via a POST to a route such as /task/abort/<taskid> (route configuration is external to this class).

Important dependencies and callers:
- The class inherits from BaseTaskHandler (not included here). TaskAbort delegates environment checks to BaseTaskHandler.backend_configured(result) and uses RequestHandler behavior provided by Tornado (for example, self.write and HTTP error handling).
- AbortableAsyncResult is used (from celery.contrib.abortable). TaskAbort only relies on creating an AbortableAsyncResult(taskid) and calling its abort() method — the implementation details of abort() are the responsibility of the celery abortable extension and the worker.
- The method is decorated with @web.authenticated, therefore Tornado's authentication mechanism must be configured; unauthenticated requests will be rejected before post() executes.

Motivation and responsibility boundary:
- This class encapsulates the "abort request over HTTP" behavior (authentication, backend availability check, call to abort, and JSON response). It does not implement task killing logic itself — it only invokes the Celery-provided abort facility and surfaces the result to the HTTP client.

## State:
This class declares no instance-level attributes of its own beyond what is inherited from BaseTaskHandler and Tornado's RequestHandler. Relevant implicit state and constraints:
- Inherited attributes:
    - Methods used at runtime that must exist on the base class: backend_configured(result) — must accept the created result object and return a truthy value when the result backend supports the operation, or falsy otherwise.
    - Tornado's RequestHandler methods used: write(dict) to send JSON-like responses, and the decorated authentication behavior from @web.authenticated.
- Module-level items referenced:
    - logger: a module-level logger is referenced via logger.info; the module must declare/initialize logger (e.g., logging.getLogger(__name__)) for logs to work as expected.
- Valid values:
    - taskid (POST path parameter): a string that identifies a Celery task (format is application-specific; the handler treats it as opaque and passes it to AbortableAsyncResult).

Class invariants:
- For any call to post(taskid):
    - backend_configured(result) must be evaluated before calling result.abort().
    - If backend_configured(result) evaluates to falsy, post must raise HTTPError(503) and must not call result.abort().

## Lifecycle:
Creation:
- No explicit constructor/arguments. Tornado creates an instance per HTTP request according to the application's routing. There is no explicit factory method in this class.

Usage:
1. The HTTP client sends a POST request to the route bound to TaskAbort, including the task id as part of the URL (or otherwise mapped to the handler's argument).
2. Tornado's @web.authenticated enforces authentication before the method executes.
3. post(taskid) is invoked:
    - Logs an "Aborting task 'taskid'" message.
    - Constructs AbortableAsyncResult(taskid).
    - Calls backend_configured(result). If it returns falsy, raises HTTPError(503).
    - Calls result.abort() to request the task be aborted.
    - Sends a JSON response containing message: "Aborted 'taskid'".
4. Any exceptions raised by AbortableAsyncResult creation or by result.abort() are not caught in this method and will propagate to Tornado's error handling (normally returning a 500 if unhandled).

Destruction / cleanup:
- No special cleanup is required by this handler. Tornado manages the handler instance lifecycle per request. There is no context manager or close() method to call.

## Method Map:
Flowchart (Mermaid syntax):

graph TD
    A[POST /route/<taskid> (incoming request)]
    A --> B{@web.authenticated}
    B -->|authenticated| C[post(taskid)]
    B -->|not authenticated| D[deny (Tornado handles)]
    C --> E[logger.info("Aborting task '<taskid>'")]
    C --> F[AbortableAsyncResult(taskid)]
    F --> G[backend_configured(result)?]
    G -->|False| H[raise HTTPError(503) -> client receives 503]
    G -->|True| I[result.abort()]
    I --> J[self.write({"message": "Aborted '<taskid>'"})]
    J --> K[HTTP 200 response returned]

## Raises:
- HTTPError(503):
    - Trigger: backend_configured(result) returned falsy. Indicates the result backend is not configured or does not support the abort operation.
- Implicit / propagated exceptions:
    - Any exceptions raised by AbortableAsyncResult() construction or by result.abort() (for example, runtime errors from Celery client code) are not handled in this method and will propagate to Tornado's global error handling (typically resulting in a 500 response). Users of this handler should be aware that abort-related exceptions are not wrapped here.

## Example:
Assume Tornado routing registers this handler at "/task/abort/(.*)":

- Tornado route (example):
    - (r"/task/abort/(.*)", TaskAbort)

- Example curl call to abort a task:
    - curl -X POST http://<host>:<port>/task/abort/01234567-89ab-cdef-0123-456789abcdef
    - Successful response body (JSON): {"message": "Aborted '01234567-89ab-cdef-0123-456789abcdef'"}
    - If the backend is not configured: HTTP 503 Service Unavailable is returned.

Notes and caveats:
- The actual effect of result.abort() depends on Celery worker support and how the abortable extension is configured; this handler only issues the abort request and reports success immediately after calling abort().
- Authentication and routing configuration are external concerns and must be set up in the Tornado application for the decorator and route mapping to work.
- Ensure module-level logger exists (e.g., logger = logging.getLogger(__name__)) to avoid NameError at runtime.

### `flower.api.tasks.TaskAbort.post` · *method*

## Summary:
Issue an abort request for the Celery task identified by taskid and write a small JSON acknowledgement to the HTTP response; does not modify handler attributes other than the HTTP response state.

## Description:
This method is the Tornado HTTP POST handler used to abort a Celery task. It is decorated with tornado.web.authenticated and is invoked during the request handling lifecycle when an authenticated client issues a POST to the endpoint bound to TaskAbort (the route typically contains a task id path parameter). The method centralizes the request-level behavior for aborting a task so HTTP concerns (authentication, response writing, and HTTP error codes) remain separate from Celery task-control mechanics.

Known callers / context:
- Called by Tornado's request dispatch for POST requests mapped to the TaskAbort handler with a captured taskid.
- Lifecycle: Tornado performs authentication -> TaskAbort.post(taskid) runs -> it validates backend availability -> attempts to abort the task -> writes a response or raises an HTTP error.

Why this logic is separated:
- Keeps HTTP-level behavior (status codes, response format, authentication) together.
- Delegates task-abort semantics to Celery's AbortableAsyncResult, avoiding duplication of backend-specific logic.

## Args:
    taskid (str): Required. The Celery task identifier string (e.g., a UUID-like task id) for the task to abort. Must be acceptable to Celery/AbortableAsyncResult.

## Returns:
    None
    - On success the method writes to the HTTP response using self.write({"message": "Aborted '<taskid>'"}). Tornado handles returning the HTTP response to the client.
    - On failure, an HTTPError is raised (see Raises) and no success message is written.

## Raises:
    tornado.web.HTTPError(503)
        - Raised when self.backend_configured(result) returns a falsey value for the AbortableAsyncResult created for taskid. This indicates the configured result backend is unavailable, disabled, or otherwise not suitable for abort operations; the request cannot be safely served.
    Any exception raised by AbortableAsyncResult(...) or AbortableAsyncResult.abort()
        - Examples include backend connectivity errors or internal Celery/backend exceptions. These exceptions are not caught here and will propagate to Tornado's error handling (which may translate them into 500 responses or log them based on the application's configuration).

## State Changes:
Attributes READ:
    - Calls self.backend_configured(result) (reads handler state or configuration indirectly via that method).
    - Calls self.write(...) (reads/writes the handler's response buffer/state via the RequestHandler API).
    - Uses the global logger to emit an informational log entry.

Attributes WRITTEN:
    - Does not assign or mutate any self.<attribute> fields directly.
    - Mutates the HTTP response state managed by the RequestHandler via self.write(...).

## Constraints:
Preconditions:
    - taskid must be provided and be a string acceptable to Celery's AbortableAsyncResult API.
    - The RequestHandler instance (self) must be fully initialized by Tornado (i.e., running inside a request context).
    - The handler must expose a callable backend_configured(result) method; that method should return truthy only if the configured backend supports the abort operation for the provided result object.

Postconditions:
    - If the method completes without raising:
        - AbortableAsyncResult.abort() has been called for the task; an abort request has been issued to the Celery backend.
        - An acknowledgement {"message": "Aborted '<taskid>'"} has been written to the HTTP response.
    - If backend_configured returns falsey:
        - A tornado.web.HTTPError(503) is raised; no abort attempt is made and no success message is written.

## Side Effects:
    - Emits an INFO-level log via the global logger indicating the abort attempt for the given taskid.
    - Constructs an AbortableAsyncResult(taskid) object (no direct handler mutation).
    - Invokes result.abort(), which affects external system state by requesting task termination in the Celery backend; exact semantics depend on the Celery backend and worker implementation.
    - Writes to the HTTP response stream via self.write(...), affecting the outgoing HTTP response for the current request.

## `flower.api.tasks.GetQueueLengths` · *class*

## Summary:
GetQueueLengths is an HTTP GET handler that returns the lengths/information of active broker queues. It constructs a Broker client for the application's broker URL, requests queue information for the active queue names, and writes the result as JSON under the key "active_queues".

## Description:
This class is a Tornado request handler (subclassing BaseTaskHandler) implementing an authenticated GET endpoint. Typical scenarios:
- Registered as an HTTP route in the Flower web application to let users inspect active queue information.
- Called by the Flower UI or API consumers to obtain current queue metadata for queues that are considered "active" by the handler (via get_active_queue_names()).

Motivation and responsibility boundary:
- Responsibility: translate an HTTP GET request into a call to the configured message-broker's management interface (via the Broker abstraction) and return the broker's queue entries limited to the active queue names.
- This handler does not implement broker-specific logic; it delegates to the Broker implementation resolved by the broker URL scheme. It also does not itself determine which queues are active — it relies on BaseTaskHandler.get_active_queue_names() to provide the list.

Known external interactions / callers:
- Tornado HTTP server instantiates and calls the handler for incoming GET requests.
- The method is decorated with web.authenticated; Tornado will enforce authentication before invoking get().
- It uses self.application and self.capp (Celery application instance) to derive broker connection URI and broker-related configuration.
- It uses utils.broker.Broker (factory) which returns a concrete broker client (e.g., RabbitMQ, Redis, ...).

## State:
This class does not define its own instance attributes in the shown source; it relies on inherited state from BaseTaskHandler / Tornado RequestHandler:
- application (tornado.web.Application) — used read-only.
  - Expected fields accessed: application.transport (str), application.options.broker_api (optional URL-like string).
- capp (Celery application-like object) — expected to be present on self (inherited from BaseTaskHandler).
  - Methods/attributes used:
    - capp.connection().as_uri(include_password=True) -> str (broker URL including credentials)
    - capp.conf.broker_transport_options -> mapping (passed to Broker)
    - capp.conf.broker_use_ssl -> value passed to Broker
- No class-level invariants are introduced by GetQueueLengths itself beyond the expectation that application and capp are available and initialized by the surrounding framework.

Invariants and expectations:
- get() assumes get_active_queue_names() is available on self and returns an iterable of queue names (strings) appropriate to pass into Broker.queues(names).
- Broker.queues(names) is expected to be an async coroutine returning an iterable (commonly a list) of queue information entries. The handler treats its return value as JSON-serializable and writes it directly.

## Lifecycle:
Creation:
- Not instantiated directly by application code; Tornado instantiates the handler for each matching request. No custom __init__ parameters are required by this class.
- Preconditions: the Tornado application must set up the handler so that BaseTaskHandler has initialized attributes like self.capp. The handler method is decorated with web.authenticated, so Tornado's authentication machinery must be configured.

Usage (typical flow for a single request):
1. Tornado verifies the client is authenticated (web.authenticated).
2. Tornado calls GetQueueLengths.get(self, ...) as an async coroutine.
3. get() reads self.application (alias app) to determine whether an HTTP broker management API override exists (app.options.broker_api) when transport is 'amqp'.
4. It constructs a Broker client via Broker(broker_url, http_api=http_api, broker_options=..., broker_use_ssl=...).
   - Broker is a factory that returns a concrete broker client according to the broker URL scheme.
5. It calls await broker.queues(self.get_active_queue_names()) to request the queue information for active queue names.
   - get_active_queue_names() is an inherited method (not shown here) expected to return an iterable of queue names.
6. It writes the response via self.write({'active_queues': queues}).
   - The handler expects the queues value to be JSON-serializable.

Destruction / cleanup:
- No explicit cleanup in this handler. Broker client resources (if any) are managed by the Broker implementation.
- The handler relies on Tornado's per-request lifecycle; no close() or context manager is used here.

## Method Map:
flowchart LR
    A[HTTP GET request (authenticated)] --> B[GetQueueLengths.get()]
    B --> C[Determine http_api (app.options.broker_api if app.transport == 'amqp')]
    B --> D[Construct Broker(...) using capp.connection().as_uri(...), http_api, broker_options, broker_use_ssl]
    D --> E[broker = concrete Broker instance (RabbitMQ/Redis/...)]
    B --> F[await broker.queues(get_active_queue_names())]
    F --> G[self.write({'active_queues': queues})]
    G --> H[HTTP response JSON]

## Raises:
The get() method does not explicitly raise new exception types, but callers should be aware of exceptions that can propagate from the operations it performs:
- NotImplementedError
  - Source: utils.broker.Broker.__new__ raises NotImplementedError when the broker URL scheme is not supported. This can occur during Broker(...) construction if the returned scheme is unknown.
- Exceptions from Broker.queues()
  - Source: broker-specific implementations may raise their own exceptions. For example, RabbitMQ.queues may rethrow an httpclient.HTTPError when the HTTP management API returns a non-200 response (response.rethrow()).
- Network/IO errors related to broker management API calls
  - Source: RabbitMQ.queues catches socket.error and httpclient.HTTPError during the fetch and returns an empty list in that case; however, other broker implementations or different code paths may raise socket.error, httpclient.HTTPError, or other I/O exceptions.
- ValueError during broker client construction
  - Source: some broker classes validate parameters and can raise ValueError (for example, Redis-related classes validate/convert vhost or RedisSsl requires broker_use_ssl). Note: RabbitMQ.validate_http_api raises ValueError but is caught inside RabbitMQ.__init__ in the available implementation; other validations in broker subclasses may raise ValueError.

Behavioral notes about exceptions:
- For RabbitMQ: HTTP fetch failures are logged and RabbitMQ.queues returns an empty list — therefore this handler will send {'active_queues': []} rather than propagate those specific fetch exceptions in that code path.
- If Broker.__new__ raises NotImplementedError (unsupported scheme), that exception will propagate and result in a 500-level error from the handler unless caught elsewhere in the framework.

## Example:
- Typical usage (conceptual — Tornado instantiates the handler and enforces authentication):
1. A client issues an authenticated GET request to the route backed by GetQueueLengths.
2. The handler reads application and capp configuration and constructs a Broker client for the broker URL returned by capp.connection().as_uri(include_password=True).
3. The handler obtains active queue names via get_active_queue_names() and awaits broker.queues(names).
4. The handler responds with JSON: {"active_queues": <list returned by Broker.queues>}.

Notes / Implementation hints for reimplementation:
- Ensure the environment provides:
  - Tornado RequestHandler behaviour (self.application, self.write, web.authenticated decorator).
  - BaseTaskHandler that supplies capp and get_active_queue_names().
- Broker(...) is a factory; when reimplementing, preserve the pattern of resolving a concrete broker client from a broker URI scheme and exposing an async queues(names) method that returns a JSON-serializable iterable of queue entries filtered to the provided names.
- Keep the response format stable: a JSON object with the key "active_queues" whose value is the broker-provided list (or empty list on fetch failures for implementers that follow RabbitMQ behaviour).

### `flower.api.tasks.GetQueueLengths.get` · *method*

## Summary:
Handles an authenticated HTTP GET request by querying the broker for lengths/details of active queues and writing the result as a JSON response under the key "active_queues". This method performs no return value and does not modify handler instance state beyond producing the HTTP response.

## Description:
This asynchronous request handler method is invoked by Tornado when an authenticated client issues a GET request routed to the GetQueueLengths endpoint (the method is decorated with web.authenticated). It executes during the HTTP request handling lifecycle and is responsible for:

- Determining whether an HTTP broker API endpoint should be used (only when the app transport is 'amqp' and app.options.broker_api is set).
- Constructing a Broker instance appropriate for the configured broker URL (the Broker class dispatches to a concrete broker implementation based on the broker URL scheme).
- Calling the broker.queues(names) coroutine with the set of active queue names returned by self.get_active_queue_names().
- Writing the returned queue information as JSON to the HTTP response body as {'active_queues': queues}.

This logic is separated into its own method because it is a single HTTP endpoint handler: it needs to run asynchronously in the Tornado request lifecycle, perform I/O with external services (broker), and serialize the result into an HTTP response. Keeping it as a dedicated handler method preserves the request-handling semantics (authentication, response writing) and isolates the broker-querying behavior from other task-handling utilities.

Known callers and invocation context:
- Tornado's request routing when a GET request is mapped to GetQueueLengths; executed inside Tornado's asynchronous request lifecycle.
- The method is run only for authenticated requests because of the @web.authenticated decorator.

## Args:
None. (Uses instance attributes and helper methods on self for inputs.)

## Returns:
None.
- The method writes a JSON response to the HTTP client. The response body is a mapping with a single key 'active_queues' whose value is whatever the awaited broker.queues(...) coroutine returns (commonly a dict or mapping-like structure describing queue lengths/status).
- No Python value is returned to the caller; the effect is observed via the HTTP response.

## Raises:
- NotImplementedError:
    - May be raised by Broker.__new__ if the broker URL scheme parsed from app.capp.connection().as_uri(...) is not recognized by Broker dispatch. (Broker.__new__ explicitly raises NotImplementedError for unsupported schemes.)
    - May be raised if the broker instance is the base Broker class and its queues method is invoked (Broker.queues raises NotImplementedError in the base class).
- AttributeError:
    - If required attributes are missing on the request handler or application object (for example, if self.capp or self.application is None or lacks the expected attributes), attribute access (self.application, app.capp, app.options) may raise AttributeError.
- Broker-specific or network exceptions:
    - The awaited broker.queues(...) call delegates to a concrete broker implementation (e.g., RabbitMQ, Redis). Network, authentication, or broker-client library errors raised by that implementation will propagate.
- Any exceptions raised by self.write (rare in typical usage) will propagate (e.g., if Tornado internals raise an HTTPError during write).

## State Changes:
Attributes READ:
- self.application
- app.transport (via self.application)
- app.options.broker_api (via self.application)
- self.capp (used to call connection().as_uri(...) and access conf)
- app.capp.connection().as_uri(include_password=True) (used to obtain broker URL string)
- app.capp.conf.broker_transport_options
- app.capp.conf.broker_use_ssl
- self.get_active_queue_names() (method called to produce the queue name list)

Attributes WRITTEN:
- None of the handler's own attributes are modified by this method.
- Side-effect: an HTTP response body is written via self.write({'active_queues': queues}), which mutates the outgoing response stream but not handler attributes.

## Constraints:
Preconditions:
- The request must be authenticated (enforced by @web.authenticated).
- self.get_active_queue_names must be callable and return an iterable of broker queue names (list/tuple/iterable of strings) acceptable to the broker implementation.
- self.capp and self.application must be properly initialized and provide the accessed attributes:
    - self.application.transport
    - self.application.options.broker_api (optional)
    - self.capp.connection().as_uri(include_password=True)
    - self.capp.conf.broker_transport_options
    - self.capp.conf.broker_use_ssl

Postconditions:
- On successful completion, an HTTP response has been sent containing JSON with key 'active_queues' mapped to the broker-provided queue information.
- No handler-instance attributes are altered by the method.

## Side Effects:
- Network I/O: constructs a Broker instance and awaits broker.queues(...), performing I/O to the message broker (or to the broker HTTP API if configured). The concrete I/O depends on the Broker subclass created from the broker URL scheme.
- Writes an HTTP response body via self.write(...).
- Possible HTTP/API calls: when app.transport == 'amqp' and app.options.broker_api is provided, the Broker may use a broker HTTP API (http_api argument) to fetch queue details instead of or in addition to broker client protocol calls.

Implementation notes for re-implementation:
- Ensure the method is asynchronous and awaited from Tornado's I/O loop.
- Preserve authentication decoration (web.authenticated) so unauthenticated requests are rejected before broker access.
- Use include_password=True when calling as_uri(...) only if returning that data is acceptable for the environment; the existing implementation includes passwords in the broker URL used to instantiate the Broker.
- Treat the result of broker.queues(...) as an opaque serializable object; the method merely places it under the 'active_queues' key in the JSON response.

## `flower.api.tasks.ListTasks` · *class*

## Summary:
HTTP GET request handler that enumerates tasks from the application's event store and returns an ordered mapping of task_id → task-metadata dict, with common query-parameter filtering, pagination, and simple worker hostname normalization.

## Description:
ListTasks is a Tornado request handler (subclass of BaseTaskHandler) that implements an authenticated GET endpoint to list tasks known to the Flower application. It parses HTTP query parameters (limit, offset, workername, taskname, state, received_start, received_end, sort_by, search), normalizes them, delegates enumeration to utils.tasks.iter_tasks(app.events, ...), post-processes each returned task via utils.tasks.as_dict, replaces a worker object with its hostname string (if present), and writes the ordered mapping to the HTTP response.

When to instantiate:
- Mounted in the Tornado web.Application route table (for example, at "/tasks") so that incoming requests are routed to this handler. Tornado creates handler instances per request.

Why this abstraction:
- Centralizes request parsing, filtering parameter normalization, and translation of internal task representations into a consistent ordered mapping returned to HTTP clients (UI or API consumers). Task retrieval and conversion logic remain in utils.tasks so ListTasks focuses on HTTP concerns.

Known callers:
- AJAX/UI code that requests the tasks list.
- Any HTTP client requesting the mapped route.

Responsibility boundary:
- Parses and normalizes HTTP query parameters.
- Delegates task enumeration and dict conversion to utils.tasks.iter_tasks and utils.tasks.as_dict.
- Performs only a small normalization of the 'worker' field to return the worker hostname string (if available).
- Does not implement authentication itself — it relies on Tornado's web.authenticated decorator and Tornado's configured authentication behavior.

## State:
Instance attributes:
- None added by ListTasks itself. Relies on inherited RequestHandler attributes and Tornado runtime:
  - self.application: Tornado application instance; must expose an events object at self.application.events, which is forwarded to utils.tasks.iter_tasks.
  - Request-specific context (e.g., arguments) is handled via RequestHandler APIs.

Query parameter handling and invariants:
- limit:
  - Read via get_argument('limit', None) → returns None or string.
  - Then normalized with limit = limit and int(limit).
  - Behavior:
    - If limit is None or an empty string (''), the expression evaluates to that falsy value (None or ''), so int() is not called and the original falsy value is kept.
    - If limit is a non-empty string (e.g., '50'), it is converted to an integer via int('50') → 50.
    - If the provided non-empty value is not a valid integer literal (e.g., 'abc'), int() raises ValueError, which will propagate out of get() unless caught upstream.
  - Invariant: after normalization limit is either an int, None, or an empty string ('') (the latter only if client supplied an empty string).
- offset:
  - Read via get_argument('offset', default=0, type=int).
  - get_argument with type=int attempts to coerce the value to int immediately. After that offset = max(offset, 0) ensures offset is non-negative.
  - Invariant: offset is an int and offset >= 0 (negative values are clamped to 0).
- workername, taskname, state:
  - Read as strings or None. If the literal string 'All' is provided, it is normalized to None to indicate "no filter" for that field.
  - Note: the local variable named type holds the task name filter and shadows Python built-in type. When reimplementing, prefer a different variable name to avoid confusion.
  - Note: the local variable worker is first used to hold the workername filter and is later reassigned inside the loop when popping the 'worker' field from task dicts; this reuse overwrites the outer filter variable in the loop scope.
- received_start, received_end, sort_by, search:
  - Passed through unchanged to utils.tasks.iter_tasks. Their accepted formats are governed by that function (commonly ISO timestamps or None for received_start/received_end).
- Output:
  - An OrderedDict mapping task_id → task_dict (task_dict comes from utils.tasks.as_dict but with the original 'worker' replaced by a hostname string when a worker object is present).

Class-level invariants:
- No per-instance persistent state is introduced by ListTasks across requests.
- For each request, the response is an OrderedDict in the iteration order produced by utils.tasks.iter_tasks (subject to offset, limit, sort_by).

## Lifecycle:
Creation:
- Created by Tornado per HTTP request. No custom constructor arguments required.
- Ensure the Tornado application passed to the handler sets application.events (the event registry used by utils.tasks.iter_tasks).

Usage (typical method sequence):
1. HTTP GET arrives at the bound route.
2. Tornado applies the behavior of the @web.authenticated decorator according to its configuration (for example, it may redirect to the application login_url or raise an HTTPError such as 403). The handler is decorated with @web.authenticated in code; exact runtime behavior follows Tornado's configuration.
3. get():
   - Calls get_argument for each supported query parameter.
   - Normalizes limit, offset, and the 'All' sentinel values.
   - Calls utils.tasks.iter_tasks(app.events, limit=..., offset=..., sort_by=..., type=..., worker=..., state=..., received_start=..., received_end=..., search=...).
   - Iterates results: converts each task object with utils.tasks.as_dict, replaces a worker object with worker.hostname when available, and accumulates (task_id, task_dict).
   - Writes OrderedDict(result) using self.write(...).
4. Tornado serializes the written value for the HTTP response (in Tornado, writing a dict/OrderedDict is typically serialized to JSON by the RequestHandler machinery). The exact serialization behavior is provided by Tornado; ListTasks itself simply calls self.write.

Destruction:
- No explicit cleanup required. Tornado will reclaim the handler instance after the request completes.

## Method Map:
graph LR
    Req[HTTP GET request] --> Auth[@web.authenticated behavior per Tornado config]
    Auth --> Args[get_argument: limit, offset, workername, taskname, state, received_start, received_end, sort_by, search]
    Args --> Norm[normalize: limit=int or falsy, offset=max(offset,0), 'All'->None]
    Norm --> Iter[utils.tasks.iter_tasks(app.events, ...)]
    Iter --> Convert[for each (task_id, task_obj) call utils.tasks.as_dict]
    Convert --> WorkerNorm[pop 'worker' and set worker.hostname if present]
    WorkerNorm --> Collect[collect (task_id, task_dict)]
    Collect --> Write[self.write(OrderedDict(collected_results))]

## Raises:
- Behavior triggered by @web.authenticated depends on Tornado configuration:
  - May result in an HTTPError (e.g., 403) or a redirect to the application's login URL if the request is unauthenticated.
- ValueError: if limit is a non-empty string that cannot be converted to int (int(limit) raises ValueError). This will propagate unless caught by Tornado exception handling.
- Any exception raised by get_argument coercion for offset (if provided value cannot be converted by the type=int callable) — exact behavior depends on Tornado version (may result in a ValueError or an HTTPError).
- Any exception raised by utils.tasks.iter_tasks or utils.tasks.as_dict (e.g., if application.events is missing or malformed) will propagate out of get() and result in Tornado's error handling (likely a 500 response).
- Note: ListTasks does not catch these exceptions itself.

## Example:
Example HTTP request:
- GET /tasks?limit=25&offset=0&workername=worker1&taskname=All&state=STARTED&sort_by=received&search=import

Behavior:
- limit read as '25' → normalized to int 25
- offset coerced to int 0 → normalized to 0
- workername 'worker1' → used as filter
- taskname 'All' → normalized to None (no task-name filter)
- state 'STARTED' → used as filter
- sort_by and search forwarded to utils.tasks.iter_tasks

Example response body (JSON representation of OrderedDict):
{
  "task-id-1": {
    "name": "myapp.tasks.import_data",
    "id": "task-id-1",
    "args": ["s3://bucket/path"],
    "state": "STARTED",
    "received": "2023-06-01T12:34:56.789Z",
    "worker": "worker1.example.com",
    "...": "..."
  },
  "task-id-2": {
    "name": "other.task",
    "id": "task-id-2",
    "args": [],
    "state": "RETRY",
    "received": "2023-06-01T12:30:00.000Z",
    "worker": "worker2.example.com"
  }
}

Notes and implementation hints:
- Respect the exact behavior of limit normalization: empty strings are treated as falsy and will not trigger int() conversion — consider validating limit more strictly if you want to reject empty strings.
- Avoid shadowing built-ins: prefer not to name variables type; use task_name or task_filter instead.
- Be aware that the local variable worker is reused: it initially holds the workername filter and is later overwritten in the loop with the popped worker object from each task dict. Use distinct variable names in reimplementations or tests to avoid confusion.
- The handler relies on utils.tasks.iter_tasks and utils.tasks.as_dict for task enumeration and formatting. In unit tests, stub these to return expected (task_id, task_obj) pairs and dicts (with a 'worker' key that may be an object with a hostname attribute).

### `flower.api.tasks.ListTasks.get` · *method*

## Summary:
Handles an HTTP GET for the tasks list: parses query parameters, fetches matching tasks from the application's events state, transforms each task to a serializable dict (replacing worker objects with hostnames), and writes an OrderedDict mapping task_id -> task dict to the HTTP response.

## Description:
This method is the GET handler for the ListTasks endpoint. It is invoked in response to an incoming HTTP GET request routed to the ListTasks request handler (i.e., during the request/response lifecycle for that URL). Typical callers are the web framework's request dispatcher when a client requests the tasks listing endpoint in the Flower UI or API.

Responsibilities:
- Extract and normalize supported query parameters from the request.
- Call utils.tasks.iter_tasks with the parsed parameters to iterate matching task objects from the application's events.state.
- Convert each task object to a dictionary via utils.tasks.as_dict, replace the worker object with the worker.hostname string (if present), and collect results in insertion order.
- Write the resulting OrderedDict to the HTTP response body.

Why this is a dedicated method:
- Encapsulates HTTP-specific parameter parsing and response serialization (distinct concerns from the lower-level task iteration and conversion utilities in utils.tasks).
- Keeps request handling and transformation logic in one place so routing code remains small and the iteration/conversion logic can be tested independently.

Known callers and invocation stage:
- Called by the Tornado request dispatch system when an HTTP GET arrives at the route backed by ListTasks.
- Executed during the request handling stage of a single HTTP connection (synchronous body of the GET request handler).

## Args:
This method is an instance method of a Tornado RequestHandler subclass and does not accept Python arguments; it reads the following HTTP query parameters from the request instead:

- limit (optional)
    - Type: integer or string representing an integer
    - Default: None (meaning no explicit limit)
    - Behavior: parsed to int(limit) if provided. Non-integer strings will trigger an int(...) conversion error.
- offset (optional)
    - Type: integer
    - Default: 0
    - Behavior: normalized with max(offset, 0) so negative values become 0.
- workername (optional)
    - Type: string
    - Default: None
    - Behavior: if value == 'All', treated as None (no worker filter). Otherwise passed to the iterator to filter by worker hostname.
- taskname (optional)
    - Type: string
    - Default: None
    - Behavior: if value == 'All', treated as None (no task name filter); otherwise used to filter by task name.
- state (optional)
    - Type: string
    - Default: None
    - Behavior: if value == 'All', treated as None (no state filter); otherwise used to filter by task state.
- received_start (optional)
    - Type: string
    - Default: None
    - Expected format: '%Y-%m-%d %H:%M' (e.g., '2023-01-15 13:00')
    - Behavior: used as lower bound (inclusive) for task.received after being converted to epoch seconds by utils.tasks.iter_tasks.
- received_end (optional)
    - Type: string
    - Default: None
    - Expected format: '%Y-%m-%d %H:%M'
    - Behavior: used as upper bound (inclusive) for task.received after conversion.
- sort_by (optional)
    - Type: string
    - Default: None
    - Behavior: forwarded to utils.tasks.iter_tasks which may sort tasks before yielding.
- search (optional)
    - Type: string or structured search payload (depends on utils.tasks.parse_search_terms)
    - Default: None
    - Behavior: forwarded to utils.tasks.iter_tasks for search-term filtering.

Note: All parameters are read from the HTTP request using self.get_argument. Only offset is requested with an explicit default (0) in the handler; other parameters default to None.

## Returns:
- The method does not return a Python value; it writes to the HTTP response via self.write.
- Response body: an OrderedDict mapping task_id -> task_dict where:
    - task_id is the uuid yielded by utils.tasks.iter_tasks
    - task_dict is the result of utils.tasks.as_dict(task) with a worker key post-processed:
        - If the task dict contains a 'worker' object, that object is popped and replaced with the worker.hostname string.
        - If no worker is present, the 'worker' key is omitted.
- Edge cases:
    - If no tasks match the filters, an empty OrderedDict is written.
    - If iter_tasks yields items in a particular order, that order is preserved in the OrderedDict.

## Raises:
- ValueError: raised if the 'limit' query parameter is present but cannot be converted via int(limit).
- AttributeError (or similar): may be raised if self.application or self.application.events is None or does not expose the expected state/tasks_by_timestamp API (this propagates from the call to utils.tasks.iter_tasks).
- Any exceptions raised by:
    - self.get_argument (framework-specific exceptions for argument parsing),
    - utils.tasks.iter_tasks or utils.tasks.as_dict (propagated as-is).
Note: The method itself does not catch exceptions; all errors will propagate to the Tornado error handling mechanism and typically result in an HTTP error response.

## State Changes:
Attributes READ:
- self.application (used to obtain app.events)
- Additionally, the method calls self.get_argument and self.write (methods of self) but does not modify other self.<attr> fields.

Attributes WRITTEN:
- None of self's stored attributes are modified by this method.

## Constraints:
Preconditions (caller must ensure):
- The request context (self) must be a fully-initialized Tornado RequestHandler with access to:
    - self.application where self.application.events is available and exposes the expected in-memory state API used by utils.tasks.iter_tasks.
- Query parameters passed (if any) must be in expected formats:
    - received_start/received_end strings parseable with '%Y-%m-%d %H:%M' as required by the iterator's conversion logic.
    - limit must be parseable by int(...) (if present).
- utils.tasks.iter_tasks must accept the forwarded arguments and yield (uuid, task) pairs where task has an as_dict() method (utils.tasks.as_dict calls task.as_dict()).

Postconditions (guarantees after successful call):
- The HTTP response body contains an OrderedDict mapping matching task UUIDs to task dictionaries with worker hostnames substituted where applicable.
- The number of returned items respects the offset and limit semantics implemented by utils.tasks.iter_tasks.

## Side Effects:
- Writes to the outgoing HTTP response via self.write(OrderedDict(...)).
- Calls into utils.tasks.iter_tasks which reads from the application's events state (no modification expected from the code shown).
- Calls utils.tasks.as_dict which calls task.as_dict() (behavior depends on task object implementation).
- No data on disk, external network, or persistent broker is modified by this method itself; all operations are in-memory and produce an HTTP response.

## `flower.api.tasks.ListTaskTypes` · *class*

## Summary:
HTTP GET request handler that returns the set/list of task types observed by the running application events state.

## Description:
This class is a minimal HTTP endpoint handler (inherits from BaseTaskHandler) whose GET handler reads the task-types known to the application's events state and writes them back to the client in a simple mapping under the key "task-types".

Typical scenario:
- Register ListTaskTypes as a Tornado request handler for a route (for example, "/task-types") in the application's URL routing.
- Tornado instantiates this handler per incoming request and calls its get() method for HTTP GET requests.
- The class is intended to be used in the Flower monitoring service (or similar) where the application exposes an `events.state` component that tracks observed task types.

Motivation and responsibility boundary:
- Responsibility: expose a read-only HTTP endpoint that reports the task types observed by the running event-state subsystem.
- Boundary: this handler does not modify task state, query brokers directly, or perform pagination/filtering; it simply returns whatever `application.events.state.task_types()` yields, packaged in a response map.

Known callers / factories:
- Tornado's HTTP request handling system (Application -> RequestHandler instantiation). No other code in this class constructs instances explicitly.
- The handler is protected by the Tornado `web.authenticated` decorator, so the caller must be an authenticated request (authentication mechanism is provided by the application / BaseTaskHandler).

## State:
- Class-defined attributes:
  - None (ListTaskTypes does not define instance attributes of its own).

- Inherited runtime attributes (assumed from Tornado RequestHandler / BaseTaskHandler):
  - self.application: object
    - Expected interface used by this class:
      - self.application.events: object with attribute `state`.
      - self.application.events.state.task_types(): callable that returns the observed task types.
    - Expected return shape from task_types(): an iterable (commonly a list or set) of task type identifiers (strings). The code accepts whatever is returned and forwards it unchanged inside the response mapping.
  - self.write(response): method used to send the response back to the client. The handler delegates serialization/headers to the inherited implementation.

- Valid ranges / invariants:
  - task-types value: any iterable value returned by state.task_types(). The handler does not validate or transform entries.
  - Class invariant: calling get() must only read from application.events.state and call self.write once with a mapping containing the key "task-types".

## Lifecycle:
- Creation:
  - Do not instantiate directly in application code; register the handler in Tornado application routing. Tornado instantiates one handler object per request with the application and request context set by the framework.
  - No constructor (__init__) parameters are defined here; standard Tornado RequestHandler construction applies.

- Usage (typical sequence):
  1. Incoming HTTP GET request routed to this handler.
  2. Tornado constructs an instance and calls the get() method.
  3. get() (decorated with @web.authenticated) enforces authentication; if authentication passes, it:
     a. Calls self.application.events.state.task_types()
     b. Constructs a response mapping with key 'task-types' mapping to the returned value
     c. Calls self.write(response) to send the response to the client
  4. Tornado completes request processing and releases the handler instance.

- Required sequencing:
  - Authentication must succeed before get() logic executes (enforced by web.authenticated).
  - The application must have attribute events.state with a callable task_types() available at GET invocation time.

- Destruction / cleanup:
  - No cleanup responsibilities. No resources are opened by this handler. Rely on Tornado framework for request lifecycle cleanup.

## Method Map:
flowchart LR
    A[HTTP GET request] --> B[ListTaskTypes.get()]
    B --> C[self.application.events.state.task_types()]
    C --> D[response = {'task-types': seen_task_types}]
    D --> E[self.write(response)]
    E --> F[Tornado sends response back to client]

(Sequence: A → B → C → D → E → F)

## Raises:
- From decorator:
  - tornado.web.HTTPError (typically HTTP 403) if authentication fails when the `web.authenticated` decorator determines the requester is not authenticated. This is raised before get() body executes.

- From attribute access / runtime errors:
  - AttributeError: if `self.application`, `self.application.events`, `self.application.events.state`, or `task_types` do not exist or are not callable, the handler will raise AttributeError or TypeError when attempting to call `task_types()`.
  - Any exception raised by `self.application.events.state.task_types()` (for example, if the state backend raises an error) will propagate and result in an error response unless caught by higher-level middleware.

- From self.write:
  - Errors during response write/serialization (raised by BaseTaskHandler / Tornado internals) will propagate according to the Tornado request handling machinery.

## Example:
1. Register the handler in your Tornado application route table for the desired path (e.g., "/task-types").
2. Ensure the application exposes `application.events.state.task_types()` which returns the observed task types (an iterable of strings).
3. Ensure the authentication setup expected by `web.authenticated` is configured (so authenticated requests are permitted).
4. A successful GET request to the route will result in the handler calling `task_types()` and writing a mapping containing the key "task-types" to the response. If `task_types()` returns an empty list, the response will be {'task-types': []}.

### `flower.api.tasks.ListTaskTypes.get` · *method*

## Summary:
Handles an authenticated HTTP GET request by retrieving the set/list of known task types from the application's event state and writing it to the HTTP response under the key "task-types".

## Description:
This method is an HTTP GET handler invoked by Tornado when a GET request is routed to the ListTaskTypes handler. The handler class is decorated with @web.authenticated, so this method runs only after Tornado's authentication check succeeds. Typical callers: Tornado's request-dispatching machinery during an incoming HTTP GET request for the endpoint served by this handler.

This logic is separated into its own method because Tornado maps HTTP verbs to handler methods (get/post/etc.), and the authentication decorator is applied at the handler method level. Keeping the retrieval-and-write flow in a single concise method follows the RequestHandler pattern and keeps request handling (HTTP layer) distinct from lower-level event-state logic.

## Args:
    None

## Returns:
    None
    - The method does not return a Python value. Instead it writes an HTTP response using self.write(response).
    - The written response is a mapping with a single key "task-types" whose value is the object returned by self.application.events.state.task_types() (commonly a list or iterable of task type identifiers). In edge cases this value may be an empty list or other collection as produced by the state implementation.

## Raises:
    - Any exception raised by evaluating self.application.events.state.task_types() is propagated (e.g., AttributeError if self.application or events or state is missing).
    - Any exception raised by self.write(response) (for example serialization/encoding errors) is propagated to Tornado's request handling stack.

## State Changes:
    Attributes READ:
        - self.application
        - self.application.events
        - self.application.events.state
    Attributes WRITTEN:
        - None on the handler instance (no self.<attr> assignments)

## Constraints:
    Preconditions:
        - The handler must be invoked in an authenticated context (the class/method is decorated with @web.authenticated).
        - self.application must exist and expose an events attribute.
        - self.application.events.state must implement a task_types() method that returns the set/list/iterable of known task types.
    Postconditions:
        - An HTTP response has been scheduled/sent via self.write(...) containing a single top-level key "task-types" mapping to the value returned by task_types().
        - No handler-instance attributes are modified by this method.

## Side Effects:
    - Writes to the HTTP response stream via self.write(response). This is an I/O side effect observable by the HTTP client.
    - No external network/database calls are made directly by this method beyond what the underlying task_types() implementation may perform.
    - No mutations are performed on objects outside of this scope by this method itself.

## `flower.api.tasks.TaskInfo` · *class*

## Summary:
Represents a Tornado HTTP request handler that serves details for a single task id. Its GET handler looks up a task in the application's in-memory events state and writes a serializable mapping of the task to the HTTP response; if the task is not present it raises a 404 HTTPError.

## Description:
This class is a request handler (subclass of BaseTaskHandler) used by the Flower HTTP API to serve information about an individual task. It is intended to be instantiated and managed by Tornado's routing system; when an incoming HTTP GET request matches the route bound to TaskInfo, Tornado calls TaskInfo.get(self, taskid).

Primary responsibilities:
- Authenticate the incoming request (the handler method is decorated with Tornado's @web.authenticated).
- Fetch the task object corresponding to the provided task id from the application's events state via utils.tasks.get_task_by_id.
- If the task is found, produce a serializable mapping by calling task.as_dict(), optionally augment the mapping with the worker hostname, and write the mapping to the HTTP response via self.write(...).
- If the task is not found, raise tornado.web.HTTPError(404) with a descriptive message.

Typical callers / instantiation context:
- Tornado's request-dispatching machinery when a route bound to this handler receives a GET request.
- The handler expects self.application.events to be available and to expose a state.tasks mapping accessible by tasks.get_task_by_id (which simply delegates to events.state.tasks.get(task_id)).

Why this class exists:
- Encapsulates the HTTP-level logic for retrieving and returning a single task resource, keeping request validation, error mapping, and response serialization separated from lower-level event-state utilities.

## State:
Attributes read by the handler (not declared on the class itself but required at runtime):
- self.application.events
  - Type: application-specific events container (Flower's event system object)
  - Required properties: events.state.tasks (a mapping/dict-like where tasks are stored keyed by id)
  - Invariants: events.state.tasks.get(task_id) returns either a task object or a falsy value (e.g., None) if missing

Local variables (within get):
- task
  - Type: task object or None
  - Source: result of utils.tasks.get_task_by_id(self.application.events, taskid)
  - Expected interface when present:
      - as_dict(): returns a mapping (dict-like) that is serializable by Tornado's write
      - .worker attribute: may be None or an object with attribute hostname (a string)
- response
  - Type: mapping/dict
  - Produced by: task.as_dict(), optionally augmented with key 'worker' whose value is task.worker.hostname

Class invariants and constraints:
- The handler assumes that any returned task implements as_dict() and that task.as_dict() returns a serializable mapping. If these expectations are violated, exceptions may be raised and will propagate (not converted by this handler).
- The handler requires that authentication succeed (enforced by the @web.authenticated decorator) before get executes.

## Lifecycle:
Creation:
- Instantiated by Tornado when a matching route is invoked. There are no custom __init__ parameters or factory methods for TaskInfo in this code; rely on Tornado's RequestHandler instantiation.
- Required runtime property: self.application.events must be set by the application (Flower).

Usage / typical method sequence:
1. Tornado dispatches a GET request to the route bound to TaskInfo and calls TaskInfo.get(self, taskid) with taskid extracted from the URL.
2. The handler (already authenticated by @web.authenticated) calls utils.tasks.get_task_by_id(self.application.events, taskid).
3. If no task is returned, the handler raises HTTPError(404) and does not write to the response body.
4. If a task is returned:
   a. Call task.as_dict() to obtain a mapping suitable for serialization.
   b. If task.worker is not None, add response['worker'] = task.worker.hostname.
   c. Call self.write(response) to write the mapping to the HTTP response stream.
5. Tornado completes the response lifecycle (flushes data and finishes the request) per its normal semantics.

Destruction / cleanup:
- The handler does not own any external resources and performs no explicit cleanup. Tornado's normal RequestHandler lifecycle handles resource cleanup and finalization.
- No context manager, close(), or explicit teardown is required in this class.

## Method Map:
flowchart LR
    A[Incoming GET /task/<taskid>] --> B[TaskInfo.get(taskid) @web.authenticated]
    B --> C[utils.tasks.get_task_by_id(self.application.events, taskid)]
    C -->|no task| D[raise HTTPError(404, "Unknown task '<taskid>'")]
    C -->|task found| E[task.as_dict() -> response mapping]
    E --> F{task.worker is not None?}
    F -->|yes| G[response['worker'] = task.worker.hostname]
    F -->|no| H[skip worker injection]
    G --> I[self.write(response)]
    H --> I
    I --> J[Tornado finishes HTTP response]

(Note: the diagram shows the typical control flow and decision points inside the GET handler)

## Raises:
- tornado.web.HTTPError(404, message)
  - Condition: tasks.get_task_by_id(self.application.events, taskid) returns a falsy value (e.g., None).
  - Message: "Unknown task '<taskid>'" (taskid interpolated into the message)

- AttributeError, TypeError, ValueError (possible, propagated)
  - Conditions (not explicitly handled by this handler):
    - task has no as_dict() method -> AttributeError when calling task.as_dict()
    - task.as_dict() returns a non-serializable value or an unexpected type -> serialization or TypeError when Tornado writes the response
    - task.worker exists but lacks .hostname -> AttributeError when accessing task.worker.hostname
  - These exceptions are not caught and will propagate to Tornado's error handling.

## Example:
1) Incoming HTTP GET request:
   - Client issues GET /task/01234567-89ab-cdef-0123-456789abcdef
   - Tornado routes the request to TaskInfo; Tornado enforces authentication before executing get

2) Lookup and response (happy path):
   - TaskInfo.get calls utils.tasks.get_task_by_id(self.application.events, "01234567-89ab-cdef-0123-456789abcdef")
   - The call returns a task object whose as_dict() yields a mapping like {'id': '...', 'name': '...', 'state': 'SUCCESS', ...}
   - If task.worker is not None and has hostname "worker@example.com", the handler adds response['worker'] = "worker@example.com"
   - The handler calls self.write(response). Tornado serializes and sends the mapping to the client as the response body.

3) Not found:
   - If the lookup returns None, TaskInfo.get raises HTTPError(404, "Unknown task '01234567-89ab-cdef-0123-456789abcdef'"), resulting in a 404 response to the client.

Usage notes:
- Ensure the application sets application.events with an events.state.tasks mapping before this handler is used.
- Ensure tasks stored in events.state.tasks expose as_dict() and (optionally) a worker object with hostname to avoid runtime AttributeError.

### `flower.api.tasks.TaskInfo.get` · *method*

## Summary:
Look up a task by id in the application's in-memory events state and write its serialized representation to the HTTP response; if the task is missing a 404 HTTPError is raised.

## Description:
This method is the HTTP GET handler for retrieving a single task's details. It runs inside a Tornado RequestHandler-like instance (TaskInfo) when a client requests a task resource by id. The method performs these steps as an atomic HTTP-handling operation:
- Validate and fetch the task from the application's events state via tasks.get_task_by_id.
- If missing, raise HTTPError(404) to signal "Not Found".
- Otherwise, obtain a serializable representation from task.as_dict(), optionally augment it with the task worker hostname, and write that mapping to the response stream with self.write(response).

Why separate this into its own method:
- It encapsulates HTTP semantics (error mapping, response serialization) and keeps request-level logic separated from lower-level event/state utilities. This simplifies routing (Tornado maps GET requests to this method) and centralizes the behavior expected when a single-task resource is requested.

Known callers / invocation context:
- Tornado's request dispatching when the TaskInfo route is matched (i.e., TaskInfo.get(self, taskid) is invoked for an incoming GET request).
- The handler expects self.application.events to be present and populated by Flower's event processing component.

Minimal example usage (abstracted):
- Incoming HTTP GET /task/<taskid> -> Tornado routes to TaskInfo.get(self, taskid)
- If found, the client receives a mapping derived from task.as_dict(), possibly including a 'worker' string.

## Args:
    taskid (str): Identifier of the task to look up. Typically a Celery task id string, but any key type accepted by the events.state.tasks mapping is allowed. This value is passed directly to tasks.get_task_by_id(self.application.events, taskid).

## Returns:
    None

    Primary effect: writes the task representation to the HTTP response using self.write(response). The written object is the mapping returned by task.as_dict(), possibly augmented with an extra 'worker' key when applicable. The method itself does not return a Python value.

## Raises:
    tornado.web.HTTPError:
        - Raised with status 404 when tasks.get_task_by_id(self.application.events, taskid) returns a falsy value (e.g., None).
        - The error message is "Unknown task '<taskid>'", embedding the requested id.

    AttributeError / TypeError (possible, not explicitly raised by this method):
        - If the returned task object does not implement as_dict(), calling task.as_dict() may raise AttributeError.
        - If task.as_dict() returns a non-mapping or an object incompatible with self.write, a TypeError or other serialization-related error may occur when Tornado attempts to write the response.
        - If task.worker exists but does not have a hostname attribute, accessing task.worker.hostname will raise AttributeError.
        - These are not converted to HTTPError within this method; they propagate and will be handled by Tornado's error handling machinery upstream.

## State Changes:
    Attributes READ:
        - self.application.events: used as the source for tasks.get_task_by_id(...)
        - task (the returned object): read via task.as_dict() and task.worker (if present)
    Attributes WRITTEN:
        - None of the handler's instance attributes are modified by this method.
        - External observable write: the HTTP response body is written via self.write(response) (Tornado RequestHandler output).

## Constraints:
    Preconditions:
        - self.application must expose an 'events' attribute whose state.tasks mapping supports .get(taskid) lookup (this is provided by Flower's event state).
        - The task object returned (when present) should implement as_dict() and should, if worker information is to be included, expose a .worker attribute which may be None or an object with a .hostname string attribute.
    Postconditions:
        - If the task was not found: an HTTPError(404) has been raised and no task mapping was written by this method.
        - If the task was found: self.write(...) has been called with a mapping derived from task.as_dict(), and that mapping includes 'worker': task.worker.hostname when task.worker is not None.

## Side Effects:
    - Sends data to the HTTP response stream via self.write(response). The content is the mapping produced by task.as_dict(), optionally augmented with a 'worker' key.
    - Raises an HTTPError for missing tasks, which results in Tornado producing a 404 response to the caller.
    - No external network, disk, or broker operations are performed by this method itself; it only reads in-memory application state and calls methods on the task object.

